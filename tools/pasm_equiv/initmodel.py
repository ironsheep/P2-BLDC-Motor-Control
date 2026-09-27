"""What init() and launchDriver() leave in hub RAM before coginit(NEWCOG, @driver, @pinbase).

Two kinds of writes:
  * the launch block and the 27-long parameter run (VAR, the ABI), built with init()'s formulas for a
    motor / board / voltage / clock configuration;
  * the driver's own DAT image, patched before the copy: adc_fram, fram, bias, sync_required, the hall tables
    (deltas, hall_angles, permuted by testSetHallSwap()'s swap) and every `<ptr> := @<label>` pointer init()
    assigns (lutCodePtr, planCodePtr today; relCodePtr or runCodeStart after C8/C2, found by reading init()).

GUARD: `dat_writes_checked()` reads init(), swapHallTables() and launchDriver() of each image and refuses to run
if they touch a driver DAT symbol this model does not know how to fill. A work package that changes what
init() puts in the image (C4's packed deltas) must extend this file, or the run stops and says so.
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
    """Every driver DAT symbol init(), swapHallTables() and launchDriver() name must be one this model fills."""
    ptrs = pointer_inits(img)
    known = KNOWN_DAT_WRITES | set(ptrs)
    driver_syms = {n for n, a in img.cog_sym.items() if '.' not in n}
    lut_labels = {n for n, (cog, hub, typ) in img.dat.items() if cog is not None and cog >= 0x200 and '.' not in n}
    unknown = set()
    for hdr in (r'^PRI init\(', r'^PRI swapHallTables\(', r'^PRI launchDriver\('):
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
        self.clk_hz = clk_hz
        self.motor = motor          # '6.5' or '4k'
        self.board = board          # 'A' or 'B'
        self.voltage = voltage      # PWR_* enum, 1..9
        self.base = base            # pin group base: 0, 8, 16, 32, 40
        self.sync = sync            # sync_required (startOwned(): parked until ATN)
        self.swap = swap            # HSW_* : 0 none, 1 halls 0/1, 2 halls 1/2, 3 halls 0/2
        self.stop_mode = stop_mode

    def as_dict(self):
        return dict(self.__dict__)


def derived(cfg, con):
    """init()'s clock-derived values."""
    ticks1us = cfg.clk_hz // 1_000_000
    ticks1ms = cfg.clk_hz // 1_000
    ticks500us = (ticks1ms * 500) // 1000
    frame_cnt = (ticks1us * (1_000_000_000 // con['PWM_RATE_IN_HZ'])) // 1000
    dead_gap = (ticks1us * 260) // 1000
    pwm_limit = (frame_cnt // 2) - (dead_gap // 2)
    duty_min = max(100 << 4, (dead_gap // 2) << 4)
    bias = ((frame_cnt // 2) - dead_gap) // 2
    duty_max = muldiv64((frame_cnt // 2) - dead_gap - con['SVM_GUARD_COUNTS'], con['SVM_INV_ROOT3_PPM'],
                        con['PPM']) << 4
    return dict(ticks1us=ticks1us, ticks1ms=ticks1ms, ticks500us=ticks500us, frame_cnt=frame_cnt,
                dead_gap=dead_gap, pwm_limit=pwm_limit, duty_min=duty_min, bias=bias, duty_max=duty_max,
                duty_at_ff=(pwm_limit << 4) // 2, adc_fram=frame_cnt, fram=((frame_cnt // 2) << 16) + 1)


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
        'CFG_CTCKS': d['ticks500us'], 'STOP_MODE': con['SM_BRAKE'] if cfg.stop_mode == 'brake' else con['SM_FLOAT'],
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


def unswapped_tables(img, cfg):
    """The motor's true tables (what the halls physically mean), for the rotor model."""
    c2 = Config(**{**cfg.as_dict(), 'swap': 0})
    return hall_tables(img, c2)
