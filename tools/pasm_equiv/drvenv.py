"""The world one driver cog sees: hub RAM, its 14 pins, the attention flag and the CT1 event.

Everything the cog reads is a function of the scenario, the frame index (the count of ADC samples the cog has
observed) and the read's ordinal -- never of the clock -- plus, for the closed loop, observables the comparison
itself checks (the field angle the frame fed to QROTATE, the hub status run, the pin writes). So two images that
behave identically see identical inputs, whatever their clock counts.

Frames: the five ADC pins (base+0..4) raise IN once per count period after their DIR rises; a TESTP that sees a
new period is a frame boundary. The driver's frame loop tests pin_adc_cur_i in wait4adc.
"""
import ast
import random
import sys
import zlib

import initmodel
from p2cog import M32, Parked, Unmodelled, EmuError, s32

OBJ_BASE = 0x0_1000
LAUNCH = 0x4_0000
PARAMS = 0x4_0400
HUB_BYTES = 0x8_0000
SECTOR = 0x1_0000_0000 // 6
SHORT_PASS = 20                    # a pass shorter than this many frames is an adversarial CT1 schedule
LAG_RATE = 0.1                     # the most the rotor model's lag moves per frame, 1/256 turn electrical
_WORLD = ('rotor', 'hall', 'load', 'lag', 'lagnow', 'over', 'adcx', 'stuck')   # physics actions, before the reads


class Layout:
    """Where the model puts the launch block, the status run, fault and the parameter run. Only their order and
    adjacency is ABI (the driver reaches them through PTRA and params_ptr), so any placement is faithful."""

    def __init__(self, img):
        con = img.con
        self.n_status = con['DRVR_STATUS_LONGS_COUNT']
        self.n_params = con['DRVR_PARAMS_LONGS_COUNT']
        if self.n_params != len(initmodel.PARAM_NAMES):
            raise EmuError('DRVR_PARAMS_LONGS_COUNT is %d; initmodel.PARAM_NAMES has %d'
                           % (self.n_params, len(initmodel.PARAM_NAMES)))
        self.launch = LAUNCH
        self.target_incre = LAUNCH + 12
        self.status = LAUNCH + 16
        self.fault = self.status + 4 * self.n_status
        self.params = PARAMS
        self.frame_cnt = PARAMS + 4 * self.n_params
        v = img.var
        base = v['DRIVE_U']
        self.sidx = {}
        for name, off in v.items():
            k = (off - base) // 4
            if 0 <= k < self.n_status and (off - base) % 4 == 0:
                self.sidx[name] = k
        for i, n in enumerate(initmodel.PARAM_NAMES):
            if v.get(n) != v['OFFSET_FWD'] + 4 * i:
                raise EmuError('the parameter run in the listing is not initmodel.PARAM_NAMES (at %s)' % n)
        for need in ('DUTY', 'DRV_STATE', 'FAULT_RESYNCS', 'LOOP_TICKS', 'LOOP_CTCKS', 'DRV_INCR_NOW'):
            if need not in self.sidx:
                raise EmuError('status long %s not found in the listing VAR table' % need)
        # the status longs that carry clock counts (a CT difference): timing, compared as timing only
        self.timing_status = {self.status + 4 * self.sidx['LOOP_TICKS'], self.status + 4 * self.sidx['LOOP_CTCKS']}
        if (v['FAULT'] - base) // 4 != self.n_status:
            raise EmuError('fault is not immediately after the status run')


class Pin:
    __slots__ = ('dir', 'out', 'mode', 'x', 'y', 'last_ack')

    def __init__(self):
        self.dir = 0
        self.out = 0
        self.mode = 0
        self.x = 0
        self.y = 0
        self.last_ack = -1


_NO_TAGS = frozenset()


class FrameLog:
    """One frame's outputs. While the frame runs they are lists; at its end `freeze()` keeps a compressed exact
    rendering (`blob`) for the comparison, plus the few facts the stimulus reads back (field, driven)."""
    __slots__ = ('hub', 'pins', 'qin', 'events', 'busy', 'overrun', 'tags', 'stage', 'field', 'ic', 'blob',
                 'driven')

    def __init__(self):
        self.hub = []
        self.pins = []
        self.qin = []
        self.events = []
        self.busy = None
        self.overrun = False
        self.tags = set()
        self.stage = None
        self.field = None
        self.ic = None                     # when tracing: {'hub': [icount...], 'pins': [...], ...}
        self.blob = None
        self.driven = False

    def freeze(self, mask, drive_pin, keep=False):
        hub = [(a, 0 if a in mask else v) for a, v in self.hub]    # clock counts are timing, not behaviour
        self.blob = zlib.compress(repr((hub, self.pins, self.qin, self.events)).encode(), 1)
        self.driven = any(n == 'wypin' and drive_pin in p and v for n, p, v in self.pins)
        self.tags = frozenset(self.tags) if self.tags else _NO_TAGS
        if not keep:
            self.hub = self.pins = self.qin = self.events = None
        return self

    def lists(self):
        hub, pins, qin, events = ast.literal_eval(zlib.decompress(self.blob).decode())
        return hub, pins, qin, events


class Env:
    def __init__(self, img, scen, layout, base_con):
        self.img = img
        self.scen = scen
        self.cfg = scen.cfg
        self.lay = layout
        self.con = base_con
        self.hub = None                    # built by _load_image()
        self.pins = [Pin() for _ in range(64)]
        self.frame = 0
        self.log = FrameLog()
        self.logs = []                     # finished frames
        self.boundary_pending = False
        self.read_ord = 0
        self.mid_writes = {}
        self.cog = None
        self.pass_ct0 = None
        self.ct1_armed = None              # frame index of the last ADDCT1
        self.ct1_n = None
        self.ct1_target = None
        self.pass_count = 0
        self.start_atn = bool(self.cfg.sync)
        # ADC timing (all five ADC pins are enabled together)
        self.adc_en = None
        self.adc_period = None
        self.adc_seen = 0
        self.t_boundary = 0
        self.waiting = False
        self.spin = (None, 0, 0)
        self.trace_ic = False
        self._load_image()
        self._init_world()

    # ------------------------------------------------------------------ image + init()
    def _load_image(self):
        img = self.img
        obj = img.obj
        # place the object so the driver's DAT longs are long-aligned in the model's long-addressed hub (the
        #  driver region's longs share one residue mod 4; a real hub reads unaligned longs the same)
        self.obj_base = OBJ_BASE + ((-img.driver_hub) % 4)
        raw = bytearray(HUB_BYTES)
        raw[self.obj_base:self.obj_base + len(obj)] = obj
        self.hub = memoryview(raw).cast('I').tolist() if sys.byteorder == 'little' else \
            [int.from_bytes(raw[k:k + 4], 'little') for k in range(0, HUB_BYTES, 4)]
        self.obj_end = self.obj_base + len(obj)
        cfg = self.cfg
        p, d = initmodel.params(cfg, self.con)
        self.params0 = p
        self.derived = d
        ptrs, unknown = initmodel.dat_writes_checked(img)
        if unknown:
            raise EmuError('%s: init()/launchDriver() write driver DAT symbol(s) %s that initmodel.py does not '
                           'model -- extend initmodel.py for this work package' % (img.label, ', '.join(unknown)))

        ob = self.obj_base

        def put(sym, val):
            h = img.sym_hub(sym)
            if h is None:
                raise EmuError('%s: no DAT symbol %s' % (img.label, sym))
            if (ob + h) & 3:
                raise EmuError('%s: DAT long %s is not aligned with the driver image' % (img.label, sym))
            self.hub[(ob + h) >> 2] = val & M32

        put('ADC_FRAM', d['adc_fram'])
        put('FRAM', d['fram'])
        put('BIAS', d['bias'])
        put('SYNC_REQUIRED', 1 if cfg.sync else 0)
        for ptr, label in ptrs.items():
            put(ptr, ob + img.sym_hub(label))
        deltas, angles = initmodel.hall_tables(img, cfg)
        dh = ob + img.sym_hub('DELTAS')
        for k in range(64):
            a = dh + k
            w = self.hub[a >> 2]
            sh = 8 * (a & 3)
            w = (w & ~(0xFF << sh)) | ((deltas[k] & 0xFF) << sh)
            self.hub[a >> 2] = w & M32
        ah = ob + img.sym_hub('HALL_ANGLES')
        for k in range(16):
            self.hub[(ah >> 2) + k] = angles[k]
        # the rotor model reads the motor's TRUE tables (a hall swap is a wiring fault the driver must not know)
        _, self.true_angles = initmodel.unswapped_tables(img, cfg)
        # adc modes, for recognising what an ADC pin is set to
        am = img.sym_hub('ADC_MODES')
        self.adc_modes = [img.long_at(am + 4 * k) for k in range(3)]

    def _init_world(self):
        L = self.lay
        h = self.hub
        h[L.launch >> 2] = self.cfg.base
        h[(L.launch >> 2) + 1] = L.params
        h[(L.launch >> 2) + 2] = M32                     # targetAngle := $FFFFFFFF
        h[(L.launch >> 2) + 3] = 0                        # setTargetAccel(0, false)
        for k in range(L.n_status + 1):
            h[(L.status >> 2) + k] = 0
        self.param_index = {n: i for i, n in enumerate(initmodel.PARAM_NAMES)}
        for n, v in self.params0.items():
            h[(L.params >> 2) + self.param_index[n]] = v & M32
        h[L.frame_cnt >> 2] = self.derived['frame_cnt']
        # stimulus state
        sc = self.scen
        self.rng0 = random.Random(sc.seed * 7919 + 17)
        self.theta = self.rng0.randrange(1 << 32)
        self.omega = 0
        self.rotor_mode = 'follow'
        self.hand_speed = 0
        self.lag = self.lag_target = sc.lag0
        self.load = sc.load0
        self.overcurrent = 0
        self.over_factor = 1.0
        self.stuck = None
        self.last_field = None
        self.prev_field = None
        self.field_dir = 0
        self.hall = self._code_for(self.theta, 0)
        self.hall_override = None
        base = self.cfg.base
        self.adc_pins = list(range(base, base + 5))
        self.hall_pins = [base + 5, base + 6, base + 7]
        self.gio_frac = [self.rng0.uniform(0.08, 0.12) for _ in range(5)]
        self.vio_frac = [self.rng0.uniform(0.86, 0.92) for _ in range(5)]
        self.sense_mv = [0, 0, 0, 0, 0]
        self.adc_extreme = {}
        self.front_fault_seen = None
        self.last_resyncs = 0

    # ------------------------------------------------------------------ rotor / halls
    def _view(self, code, dirc, angles=None):
        angles = angles or self.true_angles
        L = self.lay
        off = self.hub[(L.params >> 2) + (0 if dirc else 1)]
        return (angles[(8 if dirc else 0) + code] + off) & M32

    def _code_for(self, theta, dirc):
        for code in (1, 2, 3, 4, 5, 6):
            if ((theta - self._view(code, dirc)) & M32) < SECTOR:
                return code
        return 1

    def _update_rotor(self, k, rng):
        F = self.logs[-1].field if self.logs else None
        if F is not None:
            if self.last_field is not None:
                dF = s32(F - self.last_field)
                if dF > 0:
                    self.field_dir = 1
                elif dF < 0:
                    self.field_dir = -1
            self.prev_field, self.last_field = self.last_field, F
        driven = self.logs[-1].driven if self.logs else False
        old = self.theta
        mode = self.rotor_mode
        if mode == 'stall':
            pass
        elif mode == 'hand':
            self.theta = (self.theta + self.hand_speed) & M32
        elif mode == 'follow' and driven and F is not None:
            step = self.lag_target - self.lag              # the lag changes gradually, as a load does
            self.lag += max(-LAG_RATE, min(LAG_RATE, step))
            lag = int(self.lag * (1 << 24)) + rng.randint(-(1 << 22), 1 << 22)
            self.theta = (F - self.field_dir * lag) & M32
        else:
            self.theta = (self.theta + self.omega) & M32
            self.omega = int(self.omega * 0.995)
        if mode != 'stall':
            self.omega = s32(self.theta - old) if (mode == 'follow' and driven) else self.omega
        dirc = 1 if self.field_dir < 0 else 0
        code = self._code_for(self.theta, dirc)
        if self.stuck is not None:
            bit, val, until = self.stuck
            if k <= until:
                code = (code & ~(1 << bit)) | (val << bit)
            else:
                self.stuck = None
        if self.hall_override is not None:
            code = self.hall_override
            self.hall_override = None
        self.hall = code & 7

    # ------------------------------------------------------------------ ADC stimulus
    def _status(self, name):
        return self.hub[(self.lay.status >> 2) + self.lay.sidx[name]]

    def _update_sense(self, k, rng):
        L = self.lay
        P = L.params >> 2
        duty = self._status('DUTY')
        driven = self.logs[-1].driven if self.logs else False
        rest = 4 + rng.randint(0, 8)
        if driven:
            i_mv = rest + int(duty * self.load / 4096.0) + rng.randint(-2, 2)
        else:
            i_mv = rest
        if self.overcurrent > 0:
            self.overcurrent -= 1
            ilk = self.hub[P + self.param_index['I_LIMIT_K']] & 0xFFFF
            dfl = self.hub[P + self.param_index['DUTY_FLOOR']]
            t = (max(s32(duty), s32(dfl)) & 0xFFFF) * ilk >> 16
            i_mv = int(t * self.over_factor) + self.hub[P + self.param_index['SENSE_ZERO']] + rng.randint(0, 3)
        self.sense_mv = [rng.randint(0, 3000), rng.randint(0, 3000), rng.randint(0, 3000), 0, max(0, i_mv)]

    def _adc_count(self, idx, period, mode):
        g = int(round(self.gio_frac[idx] * period))
        v = int(round(self.vio_frac[idx] * period))
        if mode == 0:
            return g
        if mode == 1:
            return v
        ext = self.adc_extreme.get(idx)
        if ext == 'lo':
            return 0
        if ext == 'hi':
            return period
        return max(0, min(period, g + (self.sense_mv[idx] * (v - g)) // 3300))

    # ------------------------------------------------------------------ frame boundary
    def begin_frame(self, k):
        """Called by the runner at boundary k: stimulus for frame k, then frame k's scheduled writes."""
        rng = random.Random((self.scen.seed * 1_000_003 + k * 7_919) & 0xFFFF_FFFF_FFFF)
        self.read_ord = 0
        self.mid_writes = {}
        if self.ct1_n is not None and self.ct1_n < SHORT_PASS:
            self.log.tags.add('ct1short')          # an adversarial pass schedule: out of the frame budget
        acts = self.scen.actions.get(k, ())
        for a in acts:
            if a[0] in _WORLD:
                self._apply(a, k)
        self._update_rotor(k, rng)
        self._update_sense(k, rng)
        for a in acts:
            if a[0] not in _WORLD:
                ordn = a[1] if a[0] == 'mid' else 0
                if ordn:
                    self.mid_writes.setdefault(ordn, []).append(a[2])
                else:
                    self._apply(a[2] if a[0] == 'mid' else a, k)
        self._front(k)

    def _front(self, k):
        """The scenario's front-cog reflexes, from the hub status only."""
        sc = self.scen
        if not sc.front:
            return
        st = self._status('DRV_STATE')
        dcs_faulted = self.con['DCS_FAULTED']
        if st == dcs_faulted:
            if self.front_fault_seen is None:
                self.front_fault_seen = k
            elif k - self.front_fault_seen == sc.front_clear_after:
                self._apply(('cmd', 0, 0), k)
                self._apply(('pinc', 'FAULT_CLR'), k)
        else:
            self.front_fault_seen = None
        rs = self._status('FAULT_RESYNCS')
        if rs != self.last_resyncs:
            self.last_resyncs = rs
            self._apply(('cmd', 0, 0), k)

    def _apply(self, a, k):
        kind = a[0]
        L = self.lay
        P = L.params >> 2
        if kind == 'cmd':
            v = (a[1] & 0x7FFF_FFFF) | ((1 << 31) if a[2] else 0)
            self.hub[L.target_incre >> 2] = v
        elif kind == 'cmdv':                       # a target equal to the field's present speed (+ an offset)
            v = s32(self._status('DRV_INCR_NOW')) + a[1]
            self.hub[L.target_incre >> 2] = v & 0x7FFF_FFFF
        elif kind == 'param':
            self.hub[P + self.param_index[a[1]]] = a[2] & M32
        elif kind == 'pinc':
            i = P + self.param_index[a[1]]
            self.hub[i] = (self.hub[i] + 1) & M32
        elif kind == 'atn':
            self.cog.atn = 1
        elif kind == 'rotor':
            self.rotor_mode = a[1]
            if a[1] == 'hand':
                self.hand_speed = a[2]
            if a[1] == 'free' and len(a) > 2:
                self.omega = a[2]
        elif kind == 'lag':
            self.lag_target = a[1]
        elif kind == 'lagnow':
            self.lag = self.lag_target = a[1]
        elif kind == 'load':
            self.load = a[1]
        elif kind == 'over':
            self.overcurrent = a[1]
            self.over_factor = a[2]
        elif kind == 'hall':
            self.hall_override = a[1]
        elif kind == 'stuck':
            self.stuck = (a[1], a[2], k + a[3])
        elif kind == 'adcx':
            if a[2] is None:
                self.adc_extreme.pop(a[1], None)
            else:
                self.adc_extreme[a[1]] = a[2]
        else:
            raise EmuError('unknown scenario action %r' % (a,))

    # ------------------------------------------------------------------ cog hooks: hub
    def hub_read_block(self, cog, addr, n):
        self.read_ord += 1
        w = self.mid_writes.pop(self.read_ord, None)
        if w:
            for a in w:
                self._apply(a, self.frame)
        i = addr >> 2
        if i + n > len(self.hub):
            raise EmuError('hub read beyond the modelled hub at $%05X' % addr)
        return self.hub[i:i + n]

    def hub_write_block(self, cog, addr, vals):
        i = addr >> 2
        if i + len(vals) > len(self.hub):
            raise EmuError('hub write beyond the modelled hub at $%05X' % addr)
        if addr < self.obj_end and addr + 4 * len(vals) > self.obj_base:
            raise EmuError('the cog wrote into the object image at hub $%05X' % addr)
        lg = self.log.hub
        for k, v in enumerate(vals):
            self.hub[i + k] = v
            lg.append((addr + 4 * k, v))
        if self.trace_ic:
            self._mark('hub', len(vals))

    def _mark(self, kind, n=1):
        ic = self.log.ic
        if ic is None:
            ic = self.log.ic = {'hub': [], 'pins': [], 'qin': [], 'events': []}
        ic[kind].extend([self.cog.icount] * n)

    # ------------------------------------------------------------------ cog hooks: pins
    def _adc_edges(self, t):
        if self.adc_en is None or not self.adc_period:
            return 0
        if t < self.adc_en:
            return 0
        return (t - self.adc_en) // self.adc_period

    def _adc_in(self, pin, t):
        n = self._adc_edges(t)
        if n < 1:
            return 0
        last_edge = self.adc_en + n * self.adc_period
        return 1 if last_edge > self.pins[pin].last_ack else 0

    def testp(self, cog, pin):
        t = cog.ct
        if pin in self.adc_pins:
            b = self._adc_in(pin, t)
            n = self._adc_edges(t)
            if b and n > self.adc_seen:
                if not self.waiting and self.frame > 0:
                    self.log.overrun = True
                    self.log.busy = t - self.t_boundary
                self.adc_seen = n
                self.boundary_pending = True
                self.t_boundary = t
                self.waiting = False
            elif not b:
                if not self.waiting:
                    self.waiting = True
                    self.log.busy = t - self.t_boundary
                # a pure spin (this TESTP again after at most two other instructions): skip whole loop turns up
                #  to the next ADC period, keeping the poll phase exact -- clocks only, nothing else changes
                if self.spin[0] == cog.last_pc and cog.icount - self.spin[2] <= 3 and self.adc_en is not None:
                    L = t - self.spin[1]
                    if L > 0:
                        te = self.adc_en + (self._adc_edges(t) + 1) * self.adc_period
                        k = (te - t) // L
                        if k > 1:
                            cog.ct += (k - 1) * L
                self.spin = (cog.last_pc, cog.ct, cog.icount)
            return b
        if pin in self.hall_pins:
            return (self.hall >> self.hall_pins.index(pin)) & 1
        raise Unmodelled('TESTP on pin %d (not an ADC or hall pin of this group)' % pin)

    def read_in_port(self, cog, port):
        t = cog.ct
        v = 0
        for idx, p in enumerate(self.hall_pins):
            if (p >> 5) == port and (self.hall >> idx) & 1:
                v |= 1 << (p & 31)
        for p in self.adc_pins:
            if (p >> 5) == port and self._adc_in(p, t):
                v |= 1 << (p & 31)
        return v

    def write_port_reg(self, cog, a, v):
        self.log.pins.append(('reg%03X' % a, (), v))
        if self.trace_ic:
            self._mark('pins')

    def pin_op(self, cog, name, pins, value):
        t = cog.ct
        self.log.pins.append((name, tuple(pins), value))
        if self.trace_ic:
            self._mark('pins')
        orig = 0
        adc_dir_change = None
        for i, p in enumerate(pins):
            pn = self.pins[p]
            if i == 0:
                orig = pn.dir if name.startswith('dir') else pn.out
            if name == 'wrpin':
                pn.mode = value
                pn.last_ack = t
            elif name == 'wxpin':
                pn.x = value
                pn.last_ack = t
            elif name == 'wypin':
                pn.y = value
                pn.last_ack = t
            elif name == 'akpin':
                pn.last_ack = t
            else:
                grp, lvl = name[:-1], 1 if name[-1] == 'h' else 0
                if grp == 'dir':
                    if p in self.adc_pins and pn.dir != lvl:
                        adc_dir_change = lvl
                    pn.dir = lvl
                elif grp == 'out':
                    pn.out = lvl
                elif grp == 'drv':
                    if p in self.adc_pins and pn.dir != 1:
                        adc_dir_change = 1
                    pn.out, pn.dir = lvl, 1
                elif grp == 'flt':
                    if p in self.adc_pins and pn.dir != 0:
                        adc_dir_change = 0
                    pn.out, pn.dir = lvl, 0
        if adc_dir_change is not None:
            if adc_dir_change:
                cur = self.pins[self.adc_pins[4]]
                self.adc_en = t
                self.adc_period = cur.x
                self.adc_seen = 0
                for p in self.adc_pins:
                    self.pins[p].last_ack = t
            else:
                self.adc_en = None
        elif name == 'wxpin' and any(p in self.adc_pins for p in pins) and self.adc_en is not None:
            self.adc_period = value
            self.adc_en = t
            self.adc_seen = 0
        return orig

    def rdpin(self, cog, pin, ack):
        if pin not in self.adc_pins:
            raise Unmodelled('RDPIN/RQPIN on pin %d (only the ADC pins are modelled)' % pin)
        pn = self.pins[pin]
        idx = pin - self.cfg.base
        mode = self.adc_modes.index(pn.mode) if pn.mode in self.adc_modes else None
        if mode is None:
            raise Unmodelled('RDPIN on ADC pin %d in an unrecognised mode $%08X' % (pin, pn.mode))
        period = self.adc_period or pn.x
        v = self._adc_count(idx, period, mode)
        if ack:
            pn.last_ack = cog.ct
        return v & M32, 0

    # ------------------------------------------------------------------ cog hooks: CORDIC, ATN, CT1
    def cordic_input(self, cog, kind, a, b, q):
        if kind in ('qrotate', 'qvector'):
            self.log.qin.append((kind, a, b, q))
            if self.trace_ic:
                self._mark('qin')
            if kind == 'qrotate' and self.log.field is None:
                self.log.field = b

    def cogatn(self, cog, mask):
        self.log.events.append(('cogatn', mask))
        if self.trace_ic:
            self._mark('events')

    def atn_poll(self, cog):
        f = cog.atn
        cog.atn = 0
        return f

    def atn_wait(self, cog):
        if cog.atn:
            cog.atn = 0
            return cog.ct
        if self.start_atn:
            self.start_atn = False
            self.log.events.append(('start_atn',))
            if self.trace_ic:
                self._mark('events')
            return cog.ct + self.scen.start_atn_delay
        raise Parked('WAITATN with no attention scheduled')

    def ct1_set(self, cog, target):
        self.ct1_armed = self.frame
        self.ct1_n = self.scen.pass_frames(self.pass_count)
        self.pass_count += 1
        self.ct1_target = target
        off = None if self.pass_ct0 is None else (target - self.pass_ct0) & M32
        self.log.events.append(('addct1', off))
        if self.trace_ic:
            self._mark('events')

    def ct1_poll(self, cog):
        if self.ct1_armed is None:
            raise EmuError('JNCT1 before any ADDCT1 (the CT1 event is scheduled from ADDCT1)')
        return (self.frame - self.ct1_armed) >= self.ct1_n

    def ct1_wait(self, cog):
        return cog.ct + s32((self.ct1_target - cog.ct) & M32) if self.ct1_target is not None else cog.ct
