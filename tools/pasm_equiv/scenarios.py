"""Scenarios: a start configuration, a pass schedule, and a timeline of actions keyed by frame.

Actions (applied at the frame's boundary, or before the frame's r-th hub read with ('mid', r, action)):
  ('cmd', incr, sync)          targetIncre := incr (31-bit signed) with bit 31 = sync
  ('cmdv', offset)             targetIncre := the status run's drv_incr_now + offset (a target equal to v)
  ('param', NAME, value)       one long of the 27-long parameter run
  ('pinc', NAME)               advance a front-written counter (FORCE_SEQ, FAULT_CLR)
  ('atn',)                     another cog strobes this cog's attention
  ('rotor', mode[, arg])       the rotor model: 'follow', 'stall', 'free'[, speed], 'hand', speed
  ('lag', units)               the following lag, 1/256 turn electrical
  ('load', k)                  the DC-link current per duty count (x 4096)
  ('over', frames, factor)     a DC-link reading `factor` x the fold threshold for `frames` frames
  ('hall', code)               the hall code for one frame (0/7 illegal, or a skip/bounce)
  ('stuck', bit, value, frames) a hall line stuck
  ('adcx', pin_index, 'lo'|'hi'|None)  an ADC pin read at a rail
"""
import math
import random
import zlib

import initmodel

CLOCKS = [160_000_000, 200_000_000, 270_000_000, 300_000_000, 176_000_000, 264_000_000]
BASES = [0, 8, 16, 32, 40]
VOLTS_65 = [1, 2, 3, 4, 5, 6, 7, 8]
VOLTS_4K = [2, 3, 4, 5, 6, 7, 8]
SHORT_PASS = 20                    # a pass shorter than this many frames is an adversarial CT1 schedule


class Scenario:
    def __init__(self, name, seed, cfg, n_frames):
        self.name = name
        self.seed = seed
        self.cfg = cfg
        self.n_frames = n_frames
        self.actions = {}
        self.lag0 = 24
        self.load0 = 1.0
        self.front = True
        self.front_clear_after = 40
        self.start_atn_delay = 5_000
        self.ct0 = 0x1000_0000
        self.sched = []                # explicit pass lengths, in order
        self.race = False              # frame_cnt divides cfg_ctcks: a pass may land on either frame
        self.rng = random.Random(seed * 31 + 5)
        self.budget = True             # frames count toward the frame-budget check

    def add(self, frame, *action):
        self.actions.setdefault(frame, []).append(tuple(action))

    def mid(self, frame, ordinal, *action):
        self.actions.setdefault(frame, []).append(('mid', ordinal, tuple(action)))

    def pass_frames(self, i):
        if i < len(self.sched):
            return self.sched[i]
        return self.default_pass(i)

    def default_pass(self, i):
        con = self._con
        d = initmodel.derived(self.cfg, con)
        cfgc, fr = d['ticks500us'], d['frame_cnt']
        n = -(-cfgc // fr)
        if cfgc % fr == 0:
            return n + (random.Random(self.seed * 977 + i).random() < 0.5)
        return n


def _speed(rng, lo=1e4, hi=3e8):
    return int(math.exp(rng.uniform(math.log(lo), math.log(hi)))) * rng.choice((1, -1))


def _ramp(rng, con, extreme=False):
    if extreme:
        a = rng.choice((1, 2, 7, 1000, 1_000_000))
    else:
        a = int(math.exp(rng.uniform(math.log(2e3), math.log(1e6))))
    j = initmodel.jerk_for_accel(a, con)
    return j, a


def _fold(con, cfg, amps):
    d = initmodel.derived(cfg, con)
    rs = con['F_REV_A_RSENSE'] if cfg.board == 'A' else con['F_REV_B_RSENSE']
    nk = min(max(1, initmodel.muldiv64(3 * amps * rs, 0x1_0000, 16 * d['frame_cnt'])), 0xFFFF)
    fe = initmodel.muldiv64(d['frame_cnt'], 4 * con['DUTY_FLOOR_PCT'], 100)
    nf = min(max(fe, ((con['FOLD_MIN_MV'] << 16) + nk - 1) // nk), 0xFFFF)
    return nk, nf


def _set_ramps(s, f, j_up, a_up, j_dn, a_dn, torn=False):
    order = [('JERK_UP', j_up), ('ACCEL_UP', a_up), ('JERK_DN', j_dn), ('ACCEL_DN', a_dn)]
    if torn:
        s.add(f, 'param', *order[0])
        s.add(f, 'param', *order[1])
        s.add(f + 1, 'param', *order[2])      # the driver's block read sees a torn pair for one frame
        s.add(f + 1, 'param', *order[3])
    else:
        for n, v in order:
            s.add(f, 'param', n, v)


# ======================================================================== random scenarios
def random_scenario(seed, con, frames=None):
    rng = random.Random(seed)
    motor = rng.choice(('6.5', '6.5', '4k'))
    cfg = initmodel.Config(
        clk_hz=rng.choice(CLOCKS), motor=motor, board=rng.choice('AB'),
        voltage=rng.choice(VOLTS_65 if motor == '6.5' else VOLTS_4K), base=rng.choice(BASES),
        sync=1 if rng.random() < 0.25 else 0, swap=rng.choice((1, 2, 3)) if rng.random() < 0.06 else 0,
        stop_mode=rng.choice(('float', 'brake')))
    n = frames or rng.randint(1_500, 3_500)
    s = Scenario('rand-%d' % seed, seed, cfg, n)
    s._con = con
    s.lag0 = rng.randint(4, 40)
    s.load0 = rng.uniform(0.2, 3.0)
    s.front = rng.random() < 0.8
    s.front_clear_after = rng.randint(5, 120)
    s.ct0 = rng.choice((0, 0x1000_0000, 0xFFFF_0000, rng.randrange(1 << 32)))
    s.start_atn_delay = rng.randint(1, 50_000)
    p0, d = initmodel.params(cfg, con)
    # the pass schedule: nominal, with occasional adversarial stretches
    sched = []
    for i in range(n // 10 + 10):
        if rng.random() < 0.02:
            sched.append(rng.choice((1, 2, 3, 5, 12, 22, 23, 24, 30)))
        else:
            sched.append(s.default_pass(i))
    s.sched = sched
    ju, au, jd, ad = p0['JERK_UP'], p0['ACCEL_UP'], p0['JERK_DN'], p0['ACCEL_DN']
    if rng.random() < 0.7:
        ju, au = _ramp(rng, con, rng.random() < 0.1)
        jd, ad = _ramp(rng, con, rng.random() < 0.1)
        if rng.random() < 0.3:                 # a jerk well above A / tau: short ramps, quick arrivals
            ju = min(2091, ju * rng.randint(2, 40))
            jd = min(2091, jd * rng.randint(2, 40))
        _set_ramps(s, 1, ju, au, jd, ad)
    f = rng.randint(8, 60)                      # the first command lands after start
    rest_speed = [0]
    while f < n - 30:
        r = rng.random()
        if r < 0.30:                            # a drive
            v = _speed(rng, 1e3, 3e8) if rng.random() < 0.8 else rng.choice((2 ** 30 - 1, -(2 ** 30 - 1), 1, -1))
            sync = 1 if rng.random() < 0.12 else 0
            if rng.random() < 0.15:
                s.mid(f, rng.randint(1, 3), 'cmd', v, sync)
            else:
                s.add(f, 'cmd', v, sync)
            if sync and rng.random() < 0.85:
                s.add(f + rng.randint(0, 80), 'atn')
            rest_speed[0] = v
        elif r < 0.45:                          # a stop
            s.add(f, 'cmd', 0, 1 if rng.random() < 0.05 else 0)
        elif r < 0.50:                          # a short walk-like move: drive a few passes, then stop
            v = _speed(rng, 1e4, 2e6)
            s.add(f, 'cmd', v, 0)
            s.add(f + 23 * rng.randint(1, 6) + rng.randint(0, 22), 'cmd', 0, 0)
        elif r < 0.56:                          # ramps changed, often mid-plan
            nju, nau = _ramp(rng, con, rng.random() < 0.15)
            njd, nad = _ramp(rng, con, rng.random() < 0.15)
            _set_ramps(s, f, nju, nau, njd, nad, torn=rng.random() < 0.2)
        elif r < 0.60:                          # an e-stop, cleared later
            s.add(f, 'param', 'E_STOP', rng.choice((1, 2)))
            s.add(f + rng.randint(1, 400), 'param', 'E_STOP', 0)
        elif r < 0.64:                          # the rotor held (a stall), then released
            s.add(f, 'rotor', 'stall')
            s.add(f + rng.randint(20, 600), 'rotor', 'follow')
        elif r < 0.66:                          # a forced fault (testForceFault())
            s.add(f, 'pinc', 'FORCE_SEQ')
        elif r < 0.69:                          # hall trouble
            k = rng.random()
            if k < 0.4:
                s.add(f, 'hall', rng.choice((0, 7)))
            elif k < 0.7:
                s.add(f, 'hall', rng.randint(1, 6))
            else:
                s.add(f, 'stuck', rng.randint(0, 2), rng.randint(0, 1), rng.randint(1, 200))
        elif r < 0.72:                          # fault response / stop mode / brake
            s.add(f, 'param', 'FAULT_MODE', rng.choice((0, 1)))
            s.add(f, 'param', 'BRAKE_ON', rng.randint(0, 440))
            if rng.random() < 0.5:
                s.add(f, 'param', 'STOP_MODE', rng.choice((con['SM_FLOAT'], con['SM_BRAKE'])))
        elif r < 0.75:                          # the hold at rest
            s.add(f, 'param', 'HOLD_DUTY', rng.randint(p0['DUTY_MIN'], max(p0['DUTY_MIN'], p0['DUTY_MAX'] // 4)))
            s.add(f, 'param', 'HOLD_SHORT', rng.choice((0, 1)))
        elif r < 0.78:                          # current limit / rest zero
            nk, nf = _fold(con, cfg, rng.randint(1, 40))
            s.add(f, 'param', 'I_LIMIT_K', nk)
            s.add(f, 'param', 'DUTY_FLOOR', nf)
            s.add(f, 'param', 'SENSE_ZERO', rng.randint(0, 60))
        elif r < 0.82:                          # an over-current stretch (fold-back)
            s.add(f, 'over', rng.randint(1, 120), rng.uniform(0.8, 4.0))
        elif r < 0.84:                          # load changes
            s.add(f, 'load', rng.uniform(0.0, 6.0))
            s.add(f, 'lag', rng.randint(0, 70))
        elif r < 0.86:                          # the commutation pair rewritten (the lead schedule)
            s.add(f, 'param', 'OFFSET_FWD', initmodel.frac(rng.randint(0, 3599), 3600))
            s.add(f, 'param', 'OFFSET_REV', initmodel.frac(rng.randint(0, 3599), 3600))
        elif r < 0.88:                          # the continuity probe / winding check (at rest)
            s.add(f, 'cmd', 0, 0)
            g = f + rng.randint(60, 200)
            s.add(g, 'param', 'PROBE_PHASE', rng.randint(1, 3))
            s.add(g, 'param', 'PROBE_SINK', rng.choice((0, 0, 1, 2, 3)))
            s.add(g, 'param', 'PROBE_Y', rng.choice((0, rng.randint(1, p0['DUTY_MAX'] >> 4))))
            s.add(g + rng.randint(10, 200), 'param', 'PROBE_PHASE', 0)
        elif r < 0.90:                          # a hand turn while coasting
            s.add(f, 'rotor', 'hand', rng.randint(-30_000_000, 30_000_000))
            s.add(f + rng.randint(10, 300), 'rotor', 'follow')
        elif r < 0.92:                          # an ADC rail
            pi = rng.choice((0, 1, 2, 4))
            s.add(f, 'adcx', pi, rng.choice(('lo', 'hi')))
            s.add(f + rng.randint(1, 30), 'adcx', pi, None)
        elif r < 0.93:                          # a fault clear without a fault
            s.add(f, 'pinc', 'FAULT_CLR')
        elif r < 0.94:                          # an unsolicited attention
            s.add(f, 'atn')
        elif r < 0.97:                          # a new target equal to the present speed, mid-ramp
            s.add(f, 'cmdv', rng.choice((0, 0, 1, -1)))
        else:
            pass
        f += rng.randint(5, 400)
    if rng.random() < 0.3:                      # the release, stop()'s last request
        s.add(rng.randint(n // 2, n - 40), 'param', 'DRV_RELEASE', 1)
    s.budget = True
    return s


# ======================================================================== the named edge suite
def named_scenarios(con):
    out = []

    def mk(name, n, **kw):
        cfg = initmodel.Config(**{k: v for k, v in kw.items() if k in initmodel.Config().__dict__})
        s = Scenario(name, zlib.crc32(name.encode()) % 100_000 + 7, cfg, n)
        s._con = con
        return s

    p0, _ = initmodel.params(initmodel.Config(), con)
    V = 3_000_000

    s = mk('start_float_idle', 400)
    out.append(s)

    s = mk('start_brake_idle', 400, stop_mode='brake')
    out.append(s)

    s = mk('start_sync_atn', 400, sync=1)
    s.start_atn_delay = 12_345
    s.add(80, 'cmd', 200_000, 1)
    s.add(200, 'atn')
    out.append(s)

    for clk in (160_000_000, 200_000_000, 270_000_000, 300_000_000, 176_000_000):
        for motor in ('6.5', '4k'):
            s = mk('drive_stop_%s_%d' % (motor, clk // 1_000_000), 2_600, clk_hz=clk, motor=motor,
                   voltage=6 if motor == '6.5' else 5)
            _set_ramps(s, 1, 900, 60_000, 1_500, 90_000)
            s.add(30, 'cmd', V, 0)
            s.add(1_300, 'cmd', 0, 0)
            out.append(s)

    s = mk('reverse_drive_stop', 2_600, base=40)
    _set_ramps(s, 1, 900, 60_000, 1_500, 90_000)
    s.add(30, 'cmd', -V, 0)
    s.add(1_300, 'cmd', 0, 0)
    out.append(s)

    s = mk('reversal', 3_000)
    _set_ramps(s, 1, 1_000, 60_000, 1_500, 90_000)
    s.add(30, 'cmd', V, 0)
    s.add(900, 'cmd', -V, 0)
    s.add(2_000, 'cmd', 0, 0)
    out.append(s)

    s = mk('plan_corner', 2_000)                   # a stop read just before a reversal's crossing
    _set_ramps(s, 1, 2_000, 200_000, 400, 30_000)
    s.add(30, 'cmd', V, 0)
    s.add(500, 'cmd', -V, 0)
    for k in range(560, 760, 23):
        s.add(k, 'cmd', 0 if (k // 23) % 3 == 0 else -V, 0)
    s.add(900, 'cmd', 0, 0)
    out.append(s)

    s = mk('walk_legs', 3_000)
    for i, f in enumerate(range(30, 2_800, 260)):
        s.add(f, 'cmd', (1 if i % 2 else -1) * 400_000, 0)
        s.add(f + 23 * 3, 'cmd', 0, 0)
    out.append(s)

    s = mk('speed_changes', 3_000)
    _set_ramps(s, 1, 2_000, 100_000, 2_000, 100_000)
    for i, f in enumerate(range(30, 2_900, 180)):
        s.add(f, 'cmd', [V, V // 3, 2 * V, V, -V // 2, V // 10][i % 6], 0)
    out.append(s)

    for kind in (1, 2):
        for stop in ('float', 'brake'):
            s = mk('estop_%d_%s' % (kind, stop), 2_600, stop_mode=stop)
            _set_ramps(s, 1, 1_500, 60_000, 1_500, 90_000)
            s.add(10, 'param', 'E_STOP', kind)          # at rest
            s.add(60, 'param', 'E_STOP', 0)
            s.add(100, 'cmd', V, 0)
            s.add(160, 'param', 'E_STOP', kind)         # spinning up
            s.add(260, 'param', 'E_STOP', 0)
            s.add(280, 'cmd', V, 0)
            s.add(1_100, 'param', 'E_STOP', kind)       # at speed
            s.add(1_200, 'param', 'E_STOP', 0)
            s.add(1_210, 'cmd', V, 0)
            s.add(1_900, 'cmd', 0, 0)
            s.add(1_990, 'param', 'E_STOP', kind)       # spinning down
            s.add(2_200, 'param', 'E_STOP', 0)
            out.append(s)

    for fm in (0, 1):
        for stop in ('float', 'brake'):
            s = mk('fault_mode%d_%s' % (fm, stop), 4_200, stop_mode=stop)
            s.add(2, 'param', 'FAULT_MODE', fm)
            _set_ramps(s, 1, 2_091, 1_000_000, 2_091, 1_000_000)
            s.add(30, 'cmd', 1_000_000, 0)
            s.add(400, 'pinc', 'FORCE_SEQ')               # a forced fault on a driven frame
            s.add(430, 'pinc', 'FORCE_SEQ')               # and a second one, on the re-synced stop (graded)
            s.add(1_600, 'cmd', 1_000_000, 0)
            s.add(2_000, 'hall', 7)                       # an illegal code on a driven frame
            s.add(2_600, 'cmd', 1_000_000, 0)
            s.add(3_000, 'hall', 0)                       # %000 on a driven frame, faulting: the halls cannot
            s.add(3_000, 'pinc', 'FORCE_SEQ')             #  re-seed the field, so even FR_GRADED blunts
            s.add(3_600, 'cmd', 1_000_000, 0)
            s.add(3_900, 'lag', 118)                      # a real position fault from the lag
            s.front_clear_after = 60
            out.append(s)

    s = mk('lag_hold', 7_000)                         # the rotor trailing: LAG_SOFT's gate, LAG_HOLD, holdDecay
    _set_ramps(s, 1, 2_091, 1_000_000, 2_091, 1_000_000)
    s.add(20, 'cmd', 10_000_000, 0)                    # err spans lag .. lag + 42.7 (the hall quantisation), so
    s.add(600, 'lag', 62)                             #  the field must sweep a sector for the err to sweep too
    s.add(1_400, 'lag', 20)
    s.add(3_600, 'lag', 82)                           # at speed: LAG_HOLD holds the field; holdDecay
    s.add(4_800, 'lag', 20)
    s.add(5_200, 'cmd', -10_000_000, 0)
    s.add(5_600, 'lag', 80)
    s.add(6_300, 'lagnow', 10)
    s.add(6_400, 'cmd', 0, 0)
    out.append(s)

    s = mk('stall_at_speed', 9_000)                   # the rotor held at speed until the lag faults
    _set_ramps(s, 1, 2_091, 1_000_000, 2_091, 1_000_000)
    s.add(20, 'cmd', 60_000_000, 0)
    s.add(5_500, 'rotor', 'stall')
    s.add(7_000, 'rotor', 'follow')
    s.add(7_100, 'cmd', 0, 0)
    out.append(s)

    s = mk('fault_second_on_resync', 2_600)
    s.add(2, 'param', 'FAULT_MODE', 1)
    _set_ramps(s, 1, 1_500, 60_000, 1_500, 90_000)
    s.add(30, 'cmd', V, 0)
    s.add(700, 'pinc', 'FORCE_SEQ')
    s.add(760, 'pinc', 'FORCE_SEQ')
    s.add(1_400, 'cmd', V, 0)
    s.add(1_450, 'pinc', 'FAULT_CLR')
    out.append(s)

    s = mk('fault_latched_no_front', 1_500)
    s.front = False
    s.add(2, 'param', 'FAULT_MODE', 0)
    s.add(30, 'cmd', V, 0)
    s.add(400, 'pinc', 'FORCE_SEQ')
    s.add(900, 'cmd', 0, 0)
    s.add(930, 'pinc', 'FAULT_CLR')
    out.append(s)

    for ph in (1, 2, 3):
        s = mk('probe_%d' % ph, 700, stop_mode='brake')
        s.add(20, 'param', 'PROBE_PHASE', ph)
        s.add(200, 'param', 'PROBE_SINK', (ph % 3) + 1)
        s.add(260, 'param', 'PROBE_Y', 700)
        s.add(400, 'param', 'PROBE_Y', 0)
        s.add(420, 'param', 'PROBE_SINK', 0)
        s.add(500, 'param', 'PROBE_PHASE', 0)
        out.append(s)

    s = mk('hold_short', 1_500, stop_mode='brake')
    s.add(20, 'param', 'HOLD_DUTY', p0['DUTY_MIN'] * 3)
    s.add(200, 'rotor', 'hand', 5_000_000)
    s.add(260, 'rotor', 'follow')
    s.add(400, 'param', 'HOLD_SHORT', 1)
    s.add(700, 'param', 'HOLD_SHORT', 0)
    s.add(800, 'param', 'STOP_MODE', con['SM_FLOAT'])
    s.add(900, 'param', 'STOP_MODE', con['SM_BRAKE'])
    s.add(1_000, 'cmd', 300_000, 0)
    s.add(1_200, 'cmd', 0, 0)
    out.append(s)

    for when, nm in ((200, 'rest'), (700, 'running'), (0, 'faulted'), (1, 'estop')):
        s = mk('release_%s' % nm, 1_600)
        s.add(30, 'cmd', V // 3, 0)
        if nm == 'rest':
            s.add(40, 'cmd', 0, 0)
            s.add(when, 'param', 'DRV_RELEASE', 1)
        elif nm == 'running':
            s.add(when, 'param', 'DRV_RELEASE', 1)
        elif nm == 'faulted':
            s.front = False
            s.add(2, 'param', 'FAULT_MODE', 0)
            s.add(400, 'pinc', 'FORCE_SEQ')
            s.add(700, 'param', 'DRV_RELEASE', 1)
        else:
            s.add(500, 'param', 'E_STOP', 1)
            s.add(700, 'param', 'DRV_RELEASE', 1)
        out.append(s)

    s = mk('hall_illegal_entries', 1_200)
    s.add(20, 'rotor', 'hand', 90_000_000)
    for f in range(30, 1_100, 3):
        s.add(f, 'hall', 0 if (f // 3) % 2 else 7)
    out.append(s)

    s = mk('hall_illegal_saturate', 132_000)          # %000 entered 65_535+ times: the count saturates at $FFFF
    for f in range(20, 131_990, 2):
        s.add(f, 'hall', 0)
    out.append(s)

    s = mk('hall_missed_bounce_stuck', 2_000)
    s.add(30, 'cmd', V, 0)
    for f in range(300, 1_600, 37):
        s.add(f, 'hall', (f % 6) + 1)
    s.add(1_650, 'stuck', 1, 0, 150)
    out.append(s)

    s = mk('plan_passes_max', 1_600)                 # A = J = 1: a plan of more than PLAN_PASSES_MAX passes
    _set_ramps(s, 1, 1, 1, 1, 1)
    s.add(20, 'cmd', 2_000_000, 0)
    s.add(40, 'param', 'JERK_UP', 2_000)
    s.add(40, 'param', 'ACCEL_UP', 1_000_000)
    s.add(700, 'param', 'JERK_UP', 1)
    s.add(700, 'param', 'ACCEL_UP', 1)
    s.add(900, 'cmd', 0, 0)
    out.append(s)

    s = mk('plan_unwind_max', 2_000)                  # an acceleration away from rest, the jerk then lowered
    _set_ramps(s, 1, 2_091, 1_000_000, 2_091, 1_000_000)
    s.add(20, 'cmd', 2 ** 30 - 1, 0)
    s.add(600, 'cmd', -(2 ** 30 - 1), 0)
    s.add(640, 'param', 'JERK_UP', 1)
    s.add(640, 'param', 'JERK_DN', 1)
    s.add(700, 'cmd', 0, 0)
    out.append(s)

    s = mk('ramp_extremes', 2_400)
    _set_ramps(s, 1, 1, 1, 1, 1)
    s.add(10, 'cmd', 50, 0)
    s.add(400, 'cmd', 0, 0)
    _set_ramps(s, 600, 2_091, 1_000_000, 2_091, 1_000_000)
    s.add(610, 'cmd', 2 ** 30 - 1, 0)
    s.add(1_100, 'cmd', -(2 ** 30 - 1), 0)
    s.add(1_700, 'cmd', 0, 0)
    out.append(s)

    s = mk('params_midplan', 2_400)
    _set_ramps(s, 1, 1_200, 60_000, 1_200, 90_000)
    s.add(30, 'cmd', V, 0)
    for f in range(200, 2_300, 41):                   # every offset within the nine planner frames
        j, a = (f % 7 + 1) * 250, (f % 5 + 1) * 40_000
        s.add(f, 'param', 'JERK_DN', j)
        s.add(f, 'param', 'ACCEL_DN', a)
        if f % 3 == 0:
            s.add(f, 'param', 'JERK_UP', j // 2 + 1)
        if f % 400 < 41:
            s.add(f, 'cmd', 0 if f % 800 < 400 else V, 0)
    out.append(s)

    s = mk('foldback', 1_800, board='A')
    s.add(30, 'cmd', V, 0)
    for f in range(200, 1_700, 150):
        s.add(f, 'over', 60, 1.5 + (f % 4))
        s.add(f + 70, 'param', 'SENSE_ZERO', (f // 150) * 5)
    nk, nf = _fold(con, initmodel.Config(board='A'), 2)
    s.add(900, 'param', 'I_LIMIT_K', nk)
    s.add(900, 'param', 'DUTY_FLOOR', nf)
    out.append(s)

    s = mk('ct1_short', 900)
    s.sched = [1] * 30 + [2] * 20 + [3] * 20
    s.add(20, 'cmd', 500_000, 0)
    s.add(300, 'cmd', 0, 0)
    s.budget = False
    out.append(s)

    s = mk('ct1_22_23', 2_000, clk_hz=176_000_000)
    s.sched = [22, 23] * 60
    s.add(20, 'cmd', V, 0)
    s.add(1_000, 'cmd', 0, 0)
    out.append(s)

    s = mk('sync_commands', 2_000)
    s.add(20, 'cmd', V, 1)                            # waits for its ATN
    s.add(120, 'atn')
    s.add(600, 'cmd', -V, 1)                          # never released: a plain command replaces it
    s.add(900, 'cmd', V // 2, 0)
    s.add(1_200, 'atn')                               # an ATN latched with no sync pending
    s.add(1_500, 'cmd', 0, 1)
    s.add(1_530, 'atn')
    out.append(s)

    s = mk('offsets_change', 2_000)
    s.add(20, 'cmd', V, 0)
    for f in range(100, 1_900, 97):
        s.add(f, 'param', 'OFFSET_FWD', initmodel.frac((f * 37) % 3600, 3600))
        s.add(f, 'param', 'OFFSET_REV', initmodel.frac((f * 53) % 3600, 3600))
    out.append(s)

    for sw in (1, 2, 3):
        s = mk('hallswap_%d' % sw, 1_200, swap=sw)
        s.add(20, 'cmd', 300_000, 0)
        s.add(700, 'cmd', 0, 0)
        out.append(s)

    s = mk('target_equals_v', 1_600)                  # |a| > Jx at the target: pushed against, not ended
    _set_ramps(s, 1, 50, 1_000_000, 50, 1_000_000)
    s.add(20, 'cmd', 2 ** 30 - 1, 0)
    for f in (400, 700, 1_000):
        s.add(f, 'cmdv', 0)
        s.add(f + 150, 'cmd', (2 ** 30 - 1) if f != 700 else -(2 ** 30 - 1), 0)
    s.add(1_300, 'cmd', 0, 0)
    out.append(s)

    s = mk('mid_frame_writes', 1_500)
    s.mid(20, 1, 'cmd', V, 0)
    for f in range(100, 1_400, 23):
        s.mid(f, 1 + (f % 3), 'param', 'JERK_DN', 300 + f)
    s.mid(1_000, 2, 'cmd', 0, 0)
    out.append(s)

    return out
