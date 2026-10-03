"""What init() and launchDriver() leave in hub RAM before coginit(NEWCOG, @driver, @pinbase).

Two kinds of writes:
  * the launch block and the 27-long parameter run (VAR, the ABI), built with init()'s formulas for a
    motor / board / voltage / clock configuration;
  * the driver's own DAT image, patched before the copy: adc_fram, fram, bias, sync_required, the hall tables
    (deltas, hall_angles, permuted by testSetHallSwap()'s swap) and every `<ptr> := @<label>` pointer init()
    assigns (lutCodePtr, planCodePtr today; relCodePtr or runCodeStart after C8/C2, found by reading init()).

The delta table is written in whichever layout the image has: 64 bytes, or (WP4/C4, DRIVER_REV 44) the 8
packed longs pack_deltas() derives from the baseline's per-frame rules, built from the same swapped byte table.

GUARD: `dat_writes_checked()` reads init(), swapHallTables(), launchDriver(), packHallDeltas() and
deltaTableForMotor() of each image and refuses to run if they touch a driver DAT symbol this model does not know
how to fill. A work package that changes what init() puts in the image must extend this file, or the run stops
and says so.
"""
import re

M32 = 0xFFFF_FFFF

# the DAT symbols this model fills (upper case, as in the listing)
KNOWN_DAT_WRITES = {'ADC_FRAM', 'FRAM', 'BIAS', 'SYNC_REQUIRED', 'DELTAS', 'HALL_ANGLES', 'DRIVER'}

PARAM_NAMES = ['OFFSET_FWD', 'OFFSET_REV', 'DUTY_MIN', 'DUTY_MAX', 'SERVO_SHIFT', 'FF_CEILING', 'DEAD_GAP',
               'ACCEL_DN', 'CFG_CTCKS', 'STOP_MODE', 'E_STOP', 'ACCEL_UP', 'JERK_UP', 'JERK_DN', 'I_LIMIT_K',
               'DUTY_FLOOR', 'HOLD_DUTY', 'HOLD_SHORT', 'FAULT_MODE', 'BRAKE_ON', 'PROBE_PHASE', 'FORCE_SEQ',
               'FAULT_CLR', 'PROBE_SINK', 'PROBE_Y', 'DRV_RELEASE', 'SENSE_ZERO']

NOMINAL_MV = {1: 6_000, 2: 7_400, 3: 11_100, 4: 12_000, 5: 14_800, 6: 18_500, 7: 22_200, 8: 24_000, 9: 25_900}

# DocoEng 4k rows (confgurePowerLimits(), offsetsForMotor()), PWR_7p4V .. PWR_24p0V
DOCO_MAX_B = [385_000_000, 287_500_000, 485_000_000, 388_000_000, 449_500_000, 420_000_000, 460_000_000]
DOCO_MAX_A = [282_000_000, 545_000_000, 335_000_000, 376_000_000, 398_000_000, 470_000_000, 391_000_000]
DOCO_OFS_B = [33, 33, 39, 40, 36, 37, 45]
DOCO_OFS_A = [52, 53, 53, 53, 54, 54, 53]


def frac(a, b):
    return ((a & M32) << 32) // b & M32


def muldiv64(a, b, c):
    return (a * b) // c


def hall_bits_swapped(code, a, b):
    out = code & ~((1 << a) | (1 << b)) & 7
    out |= ((code >> a) & 1) << b
    out |= ((code >> b) & 1) << a
    return out


def spin_body(src, header_re):
    """The text of one Spin2 method, from its PUB/PRI line to the next top-level block."""
    m = re.search(header_re, src, re.MULTILINE)
    if not m:
        return ''
    rest = src[m.end():]
    e = re.search(r'^(PUB|PRI|DAT|VAR|CON|OBJ)\b', rest, re.MULTILINE)
    return rest[:e.start()] if e else rest


def _strip_comments(text):
    out = []
    for line in text.split('\n'):
        out.append(line.split("'")[0])
    return '\n'.join(out)


def pointer_inits(img):
    """{PTR_SYMBOL: TARGET_LABEL} for every `x := @label` in init() whose x is a driver DAT long."""
    body = _strip_comments(spin_body(img.source, r'^PRI init\('))
    found = {}
    for lhs, rhs in re.findall(r'^\s*(\w+)\s*:=\s*@(\w+)\s*$', body, re.MULTILINE):
        L, R = lhs.upper(), rhs.upper()
        if img.sym_cog(L) is not None and img.sym_hub(R) is not None:
            found[L] = R
    return found


def dat_writes_checked(img):
    """Every driver DAT symbol init(), swapHallTables(), launchDriver(), packHallDeltas() and deltaTableForMotor()
    name must be one this model fills. (A method the source lacks contributes nothing.)"""
    ptrs = pointer_inits(img)
    known = KNOWN_DAT_WRITES | set(ptrs)
    driver_syms = {n for n, a in img.cog_sym.items() if '.' not in n}
    lut_labels = {n for n, (cog, hub, typ) in img.dat.items() if cog is not None and cog >= 0x200 and '.' not in n}
    unknown = set()
    for hdr in (r'^PRI init\(', r'^PRI swapHallTables\(', r'^PRI launchDriver\(', r'^PRI packHallDeltas\(',
                r'^PRI deltaTableForMotor\('):
        body = _strip_comments(spin_body(img.source, hdr))
        for ident in set(re.findall(r'[A-Za-z_]\w*', body)):
            u = ident.upper()
            if u in driver_syms and u not in known:
                unknown.add(u)
            if u in lut_labels and u not in set(ptrs.values()):
                # a LUT label named in Spin2 must be an @target of a pointer we fill
                unknown.add(u)
    return ptrs, sorted(unknown)


class Config:
    """One start configuration."""

    def __init__(self, clk_hz=160_000_000, motor='6.5', board='B', voltage=6, base=16, sync=0, swap=0,
                 stop_mode='float'):
        self.clk_hz = CLOCK_OVERRIDE or clk_hz
        self.motor = motor          # '6.5' or '4k'
        self.board = board          # 'A' or 'B'
        self.voltage = voltage      # PWR_* enum, 1..9
        self.base = base            # pin group base: 0, 8, 16, 32, 40
        self.sync = sync            # sync_required (startOwned(): parked until ATN)
        self.swap = swap            # HSW_* : 0 none, 1 halls 0/1, 2 halls 1/2, 3 halls 0/2
        self.stop_mode = stop_mode

    def as_dict(self):
        return dict(self.__dict__)


CLOCK_OVERRIDE = None          # --clock: when set, every Config runs at this clock (Hz)
GAP_NS = 260                   # init()'s gapInNs: both Parallax manuals' 250 ns minimum, plus margin


def derived(cfg, con):
    """init()'s clock-derived values at DRIVER_REV 50 (task 3670): the frame is CLKFREQ / PWM_RATE rounded to the
    nearest even clock count, the pass deadline is K frames less half a frame, the dead gap is rounded UP from the
    64-bit product, the duty floor is a fixed fraction of the frame, and the pass's time is K frames at CLKFREQ,
    rounded up."""
    clk, pwm = cfg.clk_hz, con['PWM_RATE_IN_HZ']
    k = con.get('DRIVE_PASS_FRAMES', 23)
    ticks1us = clk // 1_000_000
    ticks1ms = clk // 1_000
    frame_cnt = ((clk + pwm) // (2 * pwm)) * 2
    dead_gap = -(-(clk * GAP_NS) // 1_000_000_000)
    ctcks = k * frame_cnt - frame_cnt // 2
    drive_pass_us = -(-(k * frame_cnt * 1_000_000) // clk)
    pwm_limit = (frame_cnt // 2) - (dead_gap // 2)
    duty_min = max((frame_cnt * con.get('DUTY_MIN_FRAME_NUM', 100)) // con.get('DUTY_MIN_FRAME_DEN', 6136) << 4,
                   (dead_gap // 2) << 4)
    bias = ((frame_cnt // 2) - dead_gap) // 2
    duty_max = muldiv64((frame_cnt // 2) - dead_gap - con['SVM_GUARD_COUNTS'], con['SVM_INV_ROOT3_PPM'],
                        con['PPM']) << 4
    return dict(ticks1us=ticks1us, ticks1ms=ticks1ms, ctcks=ctcks, frame_cnt=frame_cnt, drive_pass_us=drive_pass_us,
                dead_gap=dead_gap, pwm_limit=pwm_limit, duty_min=duty_min, bias=bias, duty_max=duty_max,
                duty_at_ff=(pwm_limit << 4) // 2, adc_fram=frame_cnt, fram=((frame_cnt // 2) << 16) + 1)


def derived_rev49(cfg, con):
    """The same values as DRIVER_REV 49's init() made them (the formulas task 3670 replaced): the baseline for the
    before / after table. ctcks is its ticks500us; drive_pass_us was the constant DRIVE_PASS_US (523)."""
    ticks1us = cfg.clk_hz // 1_000_000
    ticks1ms = cfg.clk_hz // 1_000
    ticks500us = (ticks1ms * 500) // 1000
    frame_cnt = (ticks1us * (1_000_000_000 // con['PWM_RATE_IN_HZ'])) // 1000
    dead_gap = (ticks1us * GAP_NS) // 1000
    pwm_limit = (frame_cnt // 2) - (dead_gap // 2)
    duty_min = max(100 << 4, (dead_gap // 2) << 4)
    bias = ((frame_cnt // 2) - dead_gap) // 2
    duty_max = muldiv64((frame_cnt // 2) - dead_gap - con['SVM_GUARD_COUNTS'], con['SVM_INV_ROOT3_PPM'],
                        con['PPM']) << 4
    return dict(ticks1us=ticks1us, ticks1ms=ticks1ms, ctcks=ticks500us, frame_cnt=frame_cnt, drive_pass_us=523,
                dead_gap=dead_gap, pwm_limit=pwm_limit, duty_min=duty_min, bias=bias, duty_max=duty_max,
                duty_at_ff=(pwm_limit << 4) // 2, adc_fram=frame_cnt, fram=((frame_cnt // 2) << 16) + 1)


def before_after(clk_hz, con):
    """[(name, before, after)] for every init-derived value that differs between DRIVER_REV 49 and 50 at clk_hz, in
    the units named, plus ff_ceiling's scale (duty_max / duty_at_ff) that follows duty_max."""
    cfg = Config(clk_hz=clk_hz)
    cfg.clk_hz = clk_hz                 # not the --clock override: the caller names the clock
    a, b = derived_rev49(cfg, con), derived(cfg, con)
    units = {'frame_cnt': 'clocks', 'adc_fram': 'clocks', 'fram': 'PWM X: half frame << 16 + 1',
             'dead_gap': 'clocks', 'ctcks': 'clocks (cfg_ctcks)', 'drive_pass_us': 'us', 'duty_min': '1/16 count',
             'duty_max': '1/16 count', 'bias': 'counts', 'pwm_limit': 'counts', 'duty_at_ff': '1/16 count'}
    rows = []
    for k in ('frame_cnt', 'adc_fram', 'fram', 'dead_gap', 'ctcks', 'drive_pass_us', 'duty_min', 'duty_max', 'bias',
              'pwm_limit', 'duty_at_ff'):
        rows.append((k, units[k], a[k], b[k]))
    return rows


def jerk_for_accel(a, con):
    return max(1, (muldiv64(a, 2 * con['RAMP_JERK_NUM'], con['RAMP_JERK_DEN']) + 1) >> 1)


def ramps_for(up, dn, con):
    up = min(max(1, up), con['ACCEL_STEP_CAP'])
    dn = min(max(1, dn), con['ACCEL_STEP_CAP'])
    return jerk_for_accel(up, con), up, jerk_for_accel(dn, con), dn


def offsets(cfg):
    if cfg.motor == '4k':
        idx = min(max(cfg.voltage - 2, 0), 6)             # lookdown(PWR_7p4V..PWR_24p0V), 1-based -> 0-based
        o = (DOCO_OFS_B if cfg.board == 'B' else DOCO_OFS_A)[idx]
        fwd, rev = o, 360 - o
    else:
        fwd, rev = (-4 + 18) % 360, (-4 - 18) % 360       # HUB_HALL_ZERO_DEGR +/- HUB_LEAD_DEGR
    return frac(fwd * 10, 3600), frac(rev * 10, 3600)


def params(cfg, con):
    d = derived(cfg, con)
    fwd, rev = offsets(cfg)
    ju, au, jd, ad = ramps_for(con['RAMP_ACCEL_BUILTIN_STEP'], con['RAMP_DECEL_BUILTIN_STEP'], con)
    if cfg.motor == '4k':
        idx = min(max(cfg.voltage - 2, 0), 6)
        ff = abs((DOCO_MAX_B if cfg.board == 'B' else DOCO_MAX_A)[idx])
    else:
        ff = muldiv64(con['HUB_FF_INCR_AT_NOMINAL'], NOMINAL_MV[cfg.voltage], con['HUB_FF_NOMINAL_MV'])
    ff = max(1, muldiv64(ff, d['duty_max'], d['duty_at_ff']))
    rsense = con['F_REV_A_RSENSE'] if cfg.board == 'A' else con['F_REV_B_RSENSE']
    nk = min(max(1, muldiv64(3 * con['I_PEAK_A'] * rsense, 0x1_0000, 16 * d['frame_cnt'])), 0xFFFF)
    floor_est = muldiv64(d['frame_cnt'], 4 * con['DUTY_FLOOR_PCT'], 100)
    nfloor = min(max(floor_est, ((con['FOLD_MIN_MV'] << 16) + nk - 1) // nk), 0xFFFF)
    p = {
        'OFFSET_FWD': fwd, 'OFFSET_REV': rev, 'DUTY_MIN': d['duty_min'], 'DUTY_MAX': d['duty_max'],
        'SERVO_SHIFT': con['SERVO_ACC_SHIFT'], 'FF_CEILING': ff, 'DEAD_GAP': d['dead_gap'], 'ACCEL_DN': ad,
        'CFG_CTCKS': d['ctcks'], 'STOP_MODE': con['SM_BRAKE'] if cfg.stop_mode == 'brake' else con['SM_FLOAT'],
        'E_STOP': 0, 'ACCEL_UP': au, 'JERK_UP': ju,
        'JERK_DN': jd, 'I_LIMIT_K': nk, 'DUTY_FLOOR': nfloor, 'HOLD_DUTY': d['duty_min'], 'HOLD_SHORT': 0,
        'FAULT_MODE': con['FR_GRADED'], 'BRAKE_ON': muldiv64(con['BRAKE_PERIOD_FRAMES'], con['BRAKE_PCT_DEFAULT'], 100),
        'PROBE_PHASE': 0, 'FORCE_SEQ': 0, 'FAULT_CLR': 0, 'PROBE_SINK': 0, 'PROBE_Y': 0, 'DRV_RELEASE': 0,
        'SENSE_ZERO': 0,
    }
    return p, d


def hall_tables(img, cfg):
    """The 64 delta bytes and 16 hall-angle longs init() copies into the image (with the test swap applied)."""
    if cfg.motor == '4k':
        dsrc, asrc = img.sym_hub('DELTAS4K'), img.sym_hub('HLTBANGL4K')
    else:
        dsrc, asrc = img.sym_hub('DELTAS65'), img.sym_hub('HLTBANGLES')
    deltas = list(img.obj[dsrc:dsrc + 64])
    angles = [img.long_at(asrc + 4 * k) for k in range(16)]
    if cfg.swap:
        a, b = {1: (0, 1), 2: (1, 2)}.get(cfg.swap, (0, 2))
        na = list(angles)
        nd = list(deltas)
        for old in range(8):
            na[old] = angles[hall_bits_swapped(old, a, b)]
            na[8 + old] = angles[8 + hall_bits_swapped(old, a, b)]
            for new in range(8):
                nd[(old << 3) | new] = deltas[(hall_bits_swapped(old, a, b) << 3) | hall_bits_swapped(new, a, b)]
        angles, deltas = na, nd
    return deltas, angles


NIB_MISSED = 0b0100
NIB_ILLEGAL = 0b1000
ILLEGAL_CODES = (0b000, 0b111)


def baseline_hall_decision(byte_table, old, new):
    """What the BASELINE frame (mem-reduce-start, .ctlMotor) does with one (old, new) hall pair, as
    (step, missed, illegal): the amount added to pos_, 1 if hall_missed_ is incremented, 1 if countIllegal is
    called (with tmpY = new, so the count goes into new's own word). See pack_deltas() for the derivation."""
    b = byte_table[(old << 3) | new] & 0xFF
    step = b - 0x100 if b & 0x80 else b               # altgb/getbyte, signx #7
    if old == new or step != 0:                       # test ...#%111 wz / if_z jmp;  cmp tmpY,#0 wz / if_nz jmp
        return step, 0, 0
    if new in ILLEGAL_CODES:                          # countIllegal: Z set (counted) for new == %000 or %111
        return step, 0, 1
    if old in ILLEGAL_CODES:                          # cmp old,#%000 wz / if_nz cmp old,#%111 wz
        return step, 0, 0
    return step, 1, 0                                 # if_nz add hall_missed_, #1


def pack_deltas(byte_table):
    """The 8 longs a packed-`deltas` driver (DRIVER_REV 44, WP4/C4) must find in its image for the 64-byte
    delta table `byte_table` (indexed (old << 3) | new, already hall-swapped) that the baseline image is given.

    Derived from the BASELINE PASM only (mem-reduce-start, .ctlMotor, after `and hall_, #%111_111`, so
    hall_ = old << 3 | new with old, new in 0..7):

        altgb   hall_, #deltas      \\  tmpY := signx(byte[hall_], 7) = the step s
        getbyte tmpY                 |
        signx   tmpY, #7             |
        add     pos_, tmpY          /   pos_ += s, on every pair
        mov tmpX, hall_ / shr tmpX,#3 / xor tmpX, hall_ / test tmpX, #%111 wz
        if_z jmp #.hallCounted          old == new: nothing counted
        cmp tmpY, #0 wz / if_nz jmp     s != 0: nothing counted
        mov tmpY, hall_ / and tmpY,#%111 / call #countIllegal
                                        countIllegal(new): new == %000 or %111 -> counted in new's word, Z=1;
                                        otherwise it returns at once with Z=0 and counts nothing
        if_z jmp #.hallCounted          counted illegal: never also missed
        mov tmpY, hall_ / shr tmpY,#3 / cmp tmpY,#%000 wz / if_nz cmp tmpY,#%111 wz
        if_nz add hall_missed_, #1      old legal: a missed transition; old %000/%111: nothing

    Every decision is a function of (old, new, s) and of nothing else in the cog, so it is a static function of
    the pair, and a nibble per pair can carry all of it:

        step    = s                                             (every pair)
        illegal = old != new and s == 0 and new in {%000, %111}
        missed  = old != new and s == 0 and new not in {%000, %111} and old not in {%000, %111}

    Nibble `new` of long `old`: bits 1:0 = s & 3 (the candidate reads the step back as signx(n & 3, 1)),
    bit 2 = missed, bit 3 = illegal. illegal and missed are exclusive. The step is exact only for s in -2..+1
    (bits 1:0 sign-extended); any other byte cannot be carried, and this raises rather than guess. The counted
    illegal code is `new` itself, which the candidate keeps in tmpY for countIllegal, so the nibble need not
    say which word."""
    out = [0] * 8
    for old in range(8):
        for new in range(8):
            step, missed, illegal = baseline_hall_decision(byte_table, old, new)
            if not -2 <= step <= 1:
                raise ValueError('delta byte (old %d, new %d) = %d: a packed nibble carries only -2..+1'
                                 % (old, new, step))
            nib = (step & 3) | (NIB_MISSED if missed else 0) | (NIB_ILLEGAL if illegal else 0)
            out[old] |= nib << (4 * new)
    return out


def deltas_packed(img):
    """True when the image's `deltas` is the packed 8-long table (WP4/C4): hall_angles follows it 32 bytes on,
    not 64 as with the byte table."""
    d, a = img.sym_hub('DELTAS'), img.sym_hub('HALL_ANGLES')
    if d is None or a is None:
        raise ValueError('%s: no DELTAS / HALL_ANGLES symbol' % img.label)
    if a - d not in (32, 64):
        raise ValueError('%s: HALL_ANGLES - DELTAS is %d bytes, neither the byte table (64) nor the packed '
                         'table (32)' % (img.label, a - d))
    return a - d == 32


def unswapped_tables(img, cfg):
    """The motor's true tables (what the halls physically mean), for the rotor model."""
    c2 = Config(**{**cfg.as_dict(), 'swap': 0})
    return hall_tables(img, c2)
