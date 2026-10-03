"""Two-wheel desk model for PL-167 (DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md): both motors, the platform, the
steering path limiter, and (block mode) an obstacle with the front cog's protective stop.

Imports the DRIVER_REV 46 port (Drive, xstar, lead table, ke) from spin_model.py. Adds:
  - two motors coupled through the platform's mass matrix (motor coordinates; the right motor is mounted reversed,
    so a spin in place is both motors turning the same motor-level way, as BM-SPINW's m_sign shows):
      M = [[a, -b], [-b, a]],  a = Jw + m r^2/4 + Iz r^2/track^2,  b = m r^2/4 - Iz r^2/track^2
    spin (common motor mode) sees a - b = Jw + 2 Iz r^2/track^2; straight (differential motor mode) a + b = Jw + m r^2/2
  - per-motor phase resistance from the manual 2.4 means (LEFT 501, RIGHT 467 mOhm phase to phase)
  - the front cog every 8 ms slot: frontApplyLead (:6440), holdSlotsAgo / shortfallNow (:6441-6457), and the steering
    object's frontLimitPath (isp_steering_2wheel.spin2 :2726-2800) with frontScaleCommand (:2812-2831)

usage (run from any directory; spin_model.py must sit beside this file):
  python3 spin2_model.py legs     [key=value ...]   -- the floor legs, both wheels, with the path limiter
  python3 spin2_model.py jscan    [key=value ...]   -- the inertia at which each pair first reaches the hold
  python3 spin2_model.py design   [key=value ...]   -- the floor legs under the proposed drive
  python3 spin2_model.py step | release | rtrace | ramp | wheelsup [key=value ...]   -- see the design doc section 9
  python3 spin2_model.py block    [key=value ...]   -- a straight drive into an obstacle; the protective stop's latch
  python3 spin2_model.py blockcal [key=value ...]   -- the obstacle's calibration grid (stiffness x slide force)

D-5 (design doc 4.9), off by default so every earlier command reproduces its numbers: d5=1 the limit hold (lag_lim,
the candidates' d5_back / d5_step / d5_sticky), blk_lim=1 the blocked count that also counts a front pass on which a
limiter acted. The design's runs add `d5=1 blk_lim=1` to the D-1..D-3 flags.

«#3662» (design doc 4.10), off by default so every earlier command reproduces its numbers:
  pasm=1     the DRIVER_REV 47 arithmetic the model lacked (4.10.2): (a) the fold-back on the DC-link reading against a
             threshold scaled by max(duty, duty_floor); (b) the PL-55 duty ceiling in SPIN_DN / SLOW_TO_CHG; (c) lim_seen
             re-taken after a pass in another state; (d) the blocked count's limiter half only in SPIN_UP / AT_SPEED;
             (e) the D-5 set-back signed by err_; (f) the field's direction (fwdrev) follows its last move
  v_dt=V     the bridge's dead-time voltage, opposing the phase current (FITTED, 4.10.2; ke is refitted with it)
  blk_fix=1  candidate F-a, the blocked count's limiter half sticky from a limiter until the next hall tick;
  blk_fix=2  candidate F-b, a limiter within the last blk_win front passes
  diag=1     block mode: each wheel's limiter pattern over its stand (the separating reading for F-1)
  python3 spin2_model.py stepdn   [key=value ...]   -- wheels up, the ladder's speed steps (F-3)
  python3 spin2_model.py reversal [key=value ...]   -- the floor, straight, a slow-down / reversal from -175 tps (F-2)

«#3668» (design doc 4.11), off by default so every earlier command reproduces its numbers:
  python3 spin2_model.py topspd   [key=value ...]   -- wheels up, LIMTOP's climb past the duty ceiling (165-245 x 10^6)
  d5_fold_only=1  candidate T-1: D-5's limit hold (and C4's arming) acts on a pass the fold-back acted, not on one where
                  only the duty ceiling clamped; D-3's decay still reads both limiters
  top_v=V (one model supply; 0 = 18.5 and 20.5), top_L=L (a fixed lead; -99 = the schedule), top_lo / top_hi (rungs,
  x 10^6), top_over=1 (also the over-command, 245 x 10^6 at a 1 A limit from 175)
"""
import math, sys
from spin_model import P, Drive, lead_tenths, l_eff, ke_from_ladder, FRAME, PASS, SECTOR, TWO32, SLOW, MED, BRISK

Q = dict(P)
Q.update(m=7.7, r=0.08255, track=0.387, Jw=0.006, Iz=0.26,     # Iz: NOT measured (0.22-0.35 from the build); see doc
         RL=0.2505, RR=0.2335, w0=0.05, Tnoise=0.0, slot_ms=8,
         # the proposed drive (design mode), each switchable
         dA=0, dC=0,
         kp_shift=3,              # D-A: P = (lag_edge - 48) * (duty >> 4) SAR kp_shift  (3: duty/128 per count)
         dB=0, boost_shift=12,    # D-B: above LAG_SOFT the trim also adds (lag - LAG_SOFT) * (duty >> 4) SAR boost_shift
         i_limit=27.0,            # A phase: the fold-back, modelled on phase current (the derated continuous limit)
         straight=0,              # 1 = a straight drive (motors opposite at motor level)
         step_t=0.0, step_T=0.0,  # a one-sided load step on the LEFT wheel: time, N m
         step_off=99.0,           # and its release time
         # the obstacle (block mode; design doc 7 Q1's condition): a one-sided spring at each tyre, met after ob_x m of
         #  tyre travel (the RIGHT ob_dx later), that slides forward when its force passes ob_slip (a yielding object)
         obst=0, ob_x=0.15, ob_dx=0.0, ob_k=50_000.0, ob_c=50.0, ob_slip=1e9,
         blocked_passes=1000,     # BLOCKED_PASSES (:7245): front passes (1 ms) at |err| >= LAG_SOFT with no hall tick
         ob_n=6, ob_t=9.0,        # block mode: realizations (contact points spread over one hall sector), seconds each
         # D-5 (design doc 4.9), the limit hold. Off by default: every earlier command reproduces its numbers
         d5=0,                    # 1 = on a pass in SPIN_UP / AT_SPEED where a limiter acted since the previous pass (the
                                  #  D-3 fact: fold-back or duty cap), the field's hold is lag_lim instead of lag_hold, and a
                                  #  field past it is set back to it on that pass (err then reads lag_lim)
         lag_lim=64,              # D-5's held lag: 1.5 hall sectors, the point furthest from the wrap-fault lattice (4.9.3)
         d5_back=1,               # 0 = candidate C2: the lower hold while limited, without the set-back
         d5_step=0,               # > 0 = candidate C3: the set-back moves at most d5_step counts per pass (0: all at once)
         d5_sticky=0,             # 1 = candidate C4: once the limit hold has set the field back, it stays the hold (and
                                  #  sets back again, limiter or not) until the rotor ticks forward past that sector
         blk_lim=0,               # 1 = D-5's blocked count: bFrontProtect also counts a front pass on which a limiter acted
                                  #  (duty_capped + foldback advanced since its previous pass), with no hall tick
         # «#3662» (design doc 4.10). Off by default: every earlier command reproduces its numbers
         pasm=0,                  # 1 = the as-built arithmetic (see the module doc): fold on the DC-link reading
                                  #  (:8000-8033, currentLimitK :6304, setFoldLimit :6323), the PL-55 ceiling (:7798-7817,
                                  #  capture :8985-8991), the lim_seen re-take (:8763-8766), bFrontProtect's state rule
                                  #  (:2907), the set-back's sign (:8842), fwdrev (:7967-7968)
         frame_cnt=6136,          # clocks per PWM frame at 270 MHz (init() :4394)
         duty_floor=2454,         # dutyFloorEst, m = 0.1 (init() :4511); setFoldLimit() raises it for a small limit
         r_sense=150,             # Rev B, mV per A of DC link (the obstacle and ladder runs are Rev B)
         v_dt=0.0,                # V, the bridge's dead-time voltage, opposing the phase current. 0 = none (as before)
         blk_fix=0,               # the blocked-count candidates (4.10.4): 1 = F-a, sticky; 2 = F-b, a window
         blk_win=50,              # F-b: front passes a limiter keeps the count alive
         diag=0,                  # block mode: 1 = print each wheel's limiter pattern over its stand
         i_noise=0.0,             # pasm=1: the DC-link reading's noise, uniform +- i_noise mV per frame (0 = none)
         rv_acc=0, rv_dec=0,      # reversal mode: one (acceleration, deceleration) pair, mm/s^2; 0 = the FlySky grid
         cap_lift=0,              # candidate S-1 (4.10.6): 0 = the PL-55 ceiling lifts at LAG_SOFT (as built); N = it
                                  #  lifts once the pass's lag_s reaches N (SERVO_SETPOINT 48: the rotor trails its point)
         boost_run=0,             # candidate S-2 (4.10.6): 1 = D-2's boost only in SPIN_UP / AT_SPEED
         # «#3668» (design doc 4.11). Off by default: every earlier command reproduces its numbers
         d5_fold_only=0,          # 1 = candidate T-1: the limit hold (and C4's arming) acts on a pass the fold-back acted,
                                  #  not on one where only the duty ceiling clamped; D-3's decay still reads both
         top_v=0.0,               # topspd mode: one model supply, V (0 = 18.5 and 20.5)
         top_L=-99.0,             # topspd mode: a fixed lead L, deg (-99 = the schedule)
         top_lo=165, top_hi=245,  # topspd mode: the rungs, x 10^6, LIMTOP's 10 x 10^6 apart
         top_over=0,              # topspd mode: 1 = also the over-command, 245 x 10^6 at a 1 A limit from 175
         path=1,                  # 0 = no steering path limiter: each wheel is its own motor object (topspd sets it;
                                  #  LIMTOP drives one motor object at a time, with no steering object)
         )

PATH_RELEASE_SLOTS, PATH_RELEASE_STEP, PATH_BEHIND = 4, 20, 100
SHORT_SLOTS = 4
FOLD_MIN_MV = 4                  # :7287
RUNNING = ('SPIN_UP', 'AT_SPEED')
RAMPING_DOWN = ('SPIN_DN', 'SLOW_TO_CHG')


def ke_fit(p):
    """ke as spin_model.ke_from_ladder fits it (rung 20e6 at L 18 needs duty 170 per 1e6 at 18.5 V), with the bridge's
    dead-time voltage v_dt opposing the current (a fixed point of the steady dq equations). v_dt = 0: that function."""
    if not p['v_dt']:
        return ke_from_ladder(p)
    incr = 20e6
    we = incr / TWO32 * (44000 / PASS) * 2 * math.pi
    delta = math.radians(90 + (48 - p['e90_L18']) * 360 / 256)
    Va = 18.5 * (170 * incr / 1e6) / (16 * 3068)
    X = we * p['Lh']; R = p['R']; Z2 = R * R + X * X
    wm = we / p['pp']
    lo, hi = 1e-4, 1.0
    for _ in range(80):
        ke = (lo + hi) / 2
        kt = 1.5 * p['pp'] * ke
        idd, iq = 0.0, 0.0
        for _ in range(40):
            im = max(math.hypot(idd, iq), 0.05)
            Vd = Va * math.cos(delta) - p['v_dt'] * idd / im
            Vq = Va * math.sin(delta) - p['v_dt'] * iq / im
            idd = (R * Vd + X * (Vq - ke * we)) / Z2
            iq = (R * (Vq - ke * we) - X * Vd) / Z2
        need = (0.20 + 0.018 * wm) / kt
        if iq > need:
            lo = ke
        else:
            hi = ke
    return (lo + hi) / 2


def fold_threshold(p):
    """(k, floor): the driver's fold factor and duty floor for p['i_limit'] amps (currentLimitK() :6321, setFoldLimit()
    :6338). The fold acts on a frame whose whole-mV net DC-link reading is above (max(duty, floor) * k) >> 16 (:8000-8033)."""
    amps = int(p['i_limit'])
    k = max(1, min(0xFFFF, (3 * amps * p['r_sense'] * 0x10000) // (16 * p['frame_cnt'])))
    floor = min(max(p['duty_floor'], ((FOLD_MIN_MV << 16) + k - 1) // k), 0xFFFF)
    return k, floor


class Wheel:
    def __init__(w, p, R, kind, Lfix, Z, target):
        w.p = p; w.R = R; w.kind = kind; w.Lfix = Lfix; w.Z = Z
        w.cmd = target; w.tgt = target; w.sign = 1 if target > 0 else -1
        w.drv = Drive(p)
        w.thf = 0.0; w.thr = 0.0; w.wm = 0.0; w.idd = 0.0; w.iq = 0.0
        w.duty = p['duty_min']; w.acc = w.duty << p['acc_shift']; w.ff = 0
        w.e = 0; w.started = False
        w.L = lead_tenths(0) / 10 if kind == 'SCHED' else Lfix
        w.e90 = p['e90_L18'] + (l_eff(w.L, Z, w.sign) - 18) * 256 / 360
        w.hold_slots_ago = SHORT_SLOTS; w.last_held = 0
        w.t_arrive = None; w.faulted = False
        w.pin = 0.0
        w.lag_edge = 48; w.last_sector = 0; w.pterm = 0
        w.capped_seen = 0; w.capped = 0; w.boosts = 0
        w.setbacks = 0                    # D-5: passes the limit hold set the field back
        w.lim_sector = None               # D-5 C4 (d5_sticky): the sector the limit hold armed in, None when clear
        # «#3662» (pasm=1): the PL-55 ceiling's capture and value, fwdrev, and the counters the new modes read
        w.duty0 = 0; w.incr0 = 0; w.duty_cap = p['duty_max']
        w.pdir = w.sign                   # the direction the error is read in and the physics' frame (fwdrev)
        w.folds = 0                       # fold-back frames (the model's w.capped counts both limiters)
        w.cap_frames = 0                  # frames the duty ceiling clamped (duty_capped)
        w.lim_tick = False                # F-a: a limiter acted since the last hall tick
        w.lim_ago = 1 << 30               # F-b: front passes since a limiter acted
        w.flips = 0
        w.hold_win = 0                    # held passes with the lag reading 82..88 (I-5's window, integer reading)
        w.win_frames = 0                  # frames the driven lag reads in that band: a backward tick there faults
        w.ring = []                       # diag=1: the last frames' (t, err, sector, field speed, state, duty, note)
        w.back_in_win = 0                 # backward hall ticks taken while the lag read in that band
        w.folds_seen = 0                  # «#3668» T-1 (d5_fold_only): the fold count as the previous pass left it

    def permille(w):
        return min(abs(w.drv.v) * 1000 // abs(w.cmd), 1000) if w.cmd else 1000


def run(p, target, seconds, pairs, win, sample_ms=2.0, trace=None, t0_override=None, prog=None, mon=None):
    """prog: optional [(t s, target), ...] commands taken in time order (the straight drive's sign rule applies);
    mon: optional dict the run fills with the transient readings the stepdn / reversal modes print."""
    ke = ke_fit(p); kt = 1.5 * p['pp'] * ke
    W = [Wheel(p, p['RL'], *pairs, target), Wheel(p, p['RR'], *pairs, -target if p['straight'] else target)]
    fk, ffloor = fold_threshold(p)
    prog = list(prog) if prog else []
    rr = p['r'] ** 2
    a = p['Jw'] + p['m'] * rr / 4 + p['Iz'] * rr / p['track'] ** 2
    b = p['m'] * rr / 4 - p['Iz'] * rr / p['track'] ** 2
    det = a * a - b * b
    scale = 1000; clean = 0; engages = 0; scale_min = 1000
    n = int(seconds / FRAME)
    every = int(sample_ms / 1000 / FRAME)
    slot = int(p['slot_ms'] * 44)
    samples = []
    if mon is not None:
        mon['w'] = [dict(lag_pk=-999, idc_pk=0.0, iph_pk=0.0, duty_pk=0, soft=0, c0=None, c1=None, post=[], pre=[])
                    for _ in W]
        mon['fault'] = None
        mon.setdefault('post', (99.0, 99.0)); mon.setdefault('pre', (99.0, 99.0))
    rnd = 12345 + 7919 * (int(p['seed']) - 1)          # seed=1 (the default) is the sequence every earlier run used
    rnd_i = 777 + 7919 * int(p['seed'])                 # «#3662»: the sense noise's own sequence (i_noise)
    noise = [0.0, 0.0]
    # the obstacle and the protective stop (obst=1)
    if p['obst']:
        for i, w in enumerate(W):
            w.anchor = p['ob_x'] + (p['ob_dx'] if i == 1 else 0.0)
            w.contact_t = None; w.last_tick_t = 0.0; w.blk_pos = 0; w.blk_n = 0; w.F = 0.0
            w.err_pk = 0; w.ticks_fwd = 0; w.ticks_back = 0; w.tick_sector = 0; w.blk_best = 0
            w.blk_cap = 0                 # D-5 (blk_lim): the limiter counts as the previous front pass read them
            # «#3662» diag: the stand's front passes (no tick since the last), those a limiter acted on, the longest
            #  run of limited passes and the longest gap between them, the |err| range, the fold frames
            w.dg = dict(n=0, lim=0, run=0, run_pk=0, gap=0, gap_pk=0, e_lo=999, e_hi=-999, soft=0, folds0=None)
        blk = dict(latch_t=None, wheel=None, stand=None, fault_t=None, fault_wheel=None)
    for f in range(n):
        t = f * FRAME
        # ---- «#3662»: a programmed command (stepdn, reversal), taken as the front cog writes one
        while prog and t >= prog[0][0]:
            _, tg = prog.pop(0)
            for i, w in enumerate(W):
                c = -tg if (p['straight'] and i == 1) else tg
                w.cmd = c; w.tgt = c
                if c:
                    w.sign = 1 if c > 0 else -1
        # ---- the front cog's protective stop, once per 1 ms front pass (bFrontProtect() :2898-2904)
        if p['obst'] and f % 44 == 0:
            for i, w in enumerate(W):
                pos = math.floor(w.thr / SECTOR)
                lim_f = w.capped != w.blk_cap        # D-5 (blk_lim): a limiter acted since the previous front pass
                w.blk_cap = w.capped
                st = w.drv.state
                if p['pasm'] and st not in RUNNING:
                    lim_f = False                    # (d) the limiter half counts only in SPIN_UP / AT_SPEED (:2907)
                lim_c = lim_f
                if p['blk_fix'] == 1:
                    # F-a: once a limiter has acted with no tick since, every pass counts until the next tick
                    if pos != w.blk_pos or w.tgt == 0 or st not in RUNNING:
                        w.lim_tick = False
                    elif lim_f:
                        w.lim_tick = True
                    lim_c = w.lim_tick
                elif p['blk_fix'] == 2:
                    # F-b: a limiter within the last blk_win front passes
                    w.lim_ago = 0 if lim_f else w.lim_ago + 1
                    lim_c = w.lim_ago < p['blk_win'] and st in RUNNING
                if w.tgt != 0 and (abs(w.e) >= p['lag_soft'] or ((p['blk_lim'] or p['blk_fix']) and lim_c)) \
                        and pos == w.blk_pos and w.drv.state in ('SPIN_UP', 'AT_SPEED', 'SPIN_DN'):
                    w.blk_n += 1
                else:
                    w.blk_n = 0
                if p['diag'] and w.contact_t is not None and pos == w.blk_pos and t >= w.contact_t + 0.3:
                    d = w.dg
                    if d['folds0'] is None:
                        d['folds0'] = (w.folds, t)
                    d['n'] += 1; d['lim'] += lim_f; d['soft'] += abs(w.e) >= p['lag_soft']
                    d['run'] = d['run'] + 1 if lim_f else 0
                    d['gap'] = 0 if lim_f else d['gap'] + 1
                    d['run_pk'] = max(d['run_pk'], d['run']); d['gap_pk'] = max(d['gap_pk'], d['gap'])
                    d['e_lo'] = min(d['e_lo'], abs(w.e)); d['e_hi'] = max(d['e_hi'], abs(w.e))
                    d['d_lo'] = min(d.get('d_lo', 1 << 20), w.duty); d['d_hi'] = max(d.get('d_hi', 0), w.duty)
                    d['t1'] = t; d['folds1'] = w.folds
                elif p['diag'] and pos != w.blk_pos:
                    w.dg['run'] = 0; w.dg['gap'] = 0         # a tick: the stand restarts
                w.blk_pos = pos
                w.blk_best = max(w.blk_best, w.blk_n)
                if w.blk_n >= p['blocked_passes'] and blk['latch_t'] is None:
                    blk.update(latch_t=t, wheel=('L', 'R')[i], stand=t - w.last_tick_t)
            if blk['latch_t'] is not None:
                break
        # ---- front cogs, once per slot
        if f % slot == 0 and f > 0:
            for w in W:
                if w.kind == 'SCHED':
                    w.L = lead_tenths(abs(w.drv.v)) / 10
                    w.e90 = p['e90_L18'] + (l_eff(w.L, w.Z, w.pdir if p['pasm'] else w.sign) - 18) * 256 / 360
                if w.drv.held != w.last_held:
                    w.hold_slots_ago = 0
                elif w.hold_slots_ago < SHORT_SLOTS:
                    w.hold_slots_ago += 1
                w.last_held = w.drv.held
            sh = [w.hold_slots_ago < SHORT_SLOTS for w in W]
            pm = [w.permille() for w in W]
            behind = [sh[0] and (pm[1] - pm[0] > PATH_BEHIND), sh[1] and (pm[0] - pm[1] > PATH_BEHIND)]
            if p['path'] and (behind[0] or behind[1]):     # «#3668»: path=0, no steering object (topspd)
                clean = 0
                want = pm[0] if behind[0] else pm[1]
                if want < scale:
                    if scale == 1000:
                        engages += 1
                    scale = want
                    for w in W:
                        w.tgt = w.sign * max(abs(w.cmd) * scale // 1000, min(p['incr_floor'], abs(w.cmd)))
            elif sh[0] or sh[1]:
                clean = 0
            elif scale < 1000:
                if pm[0] + PATH_RELEASE_STEP >= scale and pm[1] + PATH_RELEASE_STEP >= scale:
                    clean += 1
                else:
                    clean = 0
                if clean >= PATH_RELEASE_SLOTS:
                    scale = min(scale + PATH_RELEASE_STEP, 1000)
                    for w in W:
                        w.tgt = w.sign * max(abs(w.cmd) * scale // 1000, min(p['incr_floor'], abs(w.cmd)))
            if p['Tnoise'] > 0:
                for i in (0, 1):
                    rnd = (rnd * 1103515245 + 12345) & 0x7FFFFFFF
                    noise[i] = 0.7 * noise[i] + 0.3 * ((rnd / 0x7FFFFFFF) * 2 - 1)
        # ---- each driver: its drive pass, then the frame
        T = [0.0, 0.0]
        for i, w in enumerate(W):
            if f % PASS == 0 and not w.faulted:
                lag_s = -w.e if w.drv.v < 0 else w.e
                if not w.started:
                    w.started = True
                    w.thf = (math.floor(w.thr / SECTOR) + 0.5) * SECTOR
                    w.drv.state = 'SPIN_UP'
                prev = w.drv.state
                if p['pasm'] and prev not in RUNNING:
                    w.capped_seen = w.capped          # (c) gettgtincr's re-take: frames in another state are no limit
                    w.folds_seen = w.folds
                at_rest = w.drv.jerk_step(w.tgt, w.e)
                if p['pasm'] and not at_rest and w.drv.state in RAMPING_DOWN and prev not in RAMPING_DOWN:
                    w.duty0 = w.duty; w.incr0 = abs(w.drv.v)    # (b) jerkStep's .report: where the ramp-down starts
                if not at_rest:
                    # D-5 (d5): while a limiter has the duty, in the states holdDecay walks, the hold is lag_lim
                    dir_ = -1 if w.drv.v < 0 else 1
                    if w.lim_sector is not None and (math.floor(w.thr / SECTOR) - w.lim_sector) * dir_ > 0:
                        w.lim_sector = None       # C4: the rotor ticked forward past the armed sector
                    # «#3668» T-1 (d5_fold_only): only the fold-back arms the limit hold; else either limiter (as built)
                    lim_now = (w.folds != w.folds_seen) if p['d5_fold_only'] else (w.capped != w.capped_seen)
                    lim_hold = p['d5'] and (lim_now or w.lim_sector is not None) \
                        and w.drv.state in ('SPIN_UP', 'AT_SPEED')
                    hold_at = p['lag_lim'] if lim_hold else p['lag_hold']
                    if lag_s < hold_at:
                        if p['pasm'] and w.drv.v != 0 and (1 if w.drv.v > 0 else -1) != w.pdir:
                            # (f) fwdrev turns with the field's move (:7967-7968): the error is read against the
                            #  other direction's offset. The model keeps the voltage's angle on the rotor continuous
                            #  (its two directions' e90 are mirror fits), so its reading moves by 128 - 2 e90 counts
                            #  where the driver's moves by 2L (4.10.9)
                            nd = -w.pdir
                            e90n = p['e90_L18'] + (l_eff(w.L, w.Z, nd) - 18) * 256 / 360
                            w.thf -= w.pdir * (w.e90 + e90n - 128)
                            w.pdir = nd; w.e90 = e90n; w.flips += 1
                        w.thf += w.drv.v / TWO32 * 256
                    else:
                        if p['pasm'] and 82 <= lag_s <= 88:
                            w.hold_win += 1
                        if lim_hold and p['d5_back'] and lag_s > p['lag_lim']:
                            # the set-back: angle_ -= sign(drv_incr) * (lag_s - lag_lim) << 24, so err reads lag_lim
                            back = lag_s - p['lag_lim']
                            if p['d5_step'] > 0:
                                back = min(back, p['d5_step'])
                            w.thf -= back * (dir_ if not p['pasm'] else (1 if w.e >= 0 else -1))   # (e) :8842
                            w.setbacks += 1
                            if p['d5_sticky']:
                                w.lim_sector = math.floor(w.thr / SECTOR)
                        w.drv.held += 1
                        if not p['dC']:
                            w.drv.hold_decay()
                        else:
                            # D-C: a held pass walks the field down only when the duty could not rise in the last
                            #  pass (a limiter clamped it: duty_capped advanced; the model has no fold-back below the
                            #  cap); else the field waits at the hold and the trim answers
                            if w.capped != w.capped_seen:
                                w.drv.hold_decay()
                            elif w.drv.state == 'AT_SPEED':
                                w.drv.state = 'SPIN_UP'
                    w.capped_seen = w.capped
                    w.folds_seen = w.folds
                if p['pasm']:
                    w.capped_seen = w.capped          # passEnd's snapshot, every pass
                    w.folds_seen = w.folds
                    # (b) the PL-55 ceiling for this pass's frames: duty0 x |drv_incr| / incr0 while ramping down,
                    #  lifted when the pass's lag_s >= LAG_SOFT (:7798-7817)
                    w.duty_cap = p['duty_max']
                    if w.drv.state in RAMPING_DOWN and lag_s < (p['cap_lift'] or p['lag_soft']) and w.incr0:
                        w.duty_cap = max(p['duty_min'], min(p['duty_max'], w.duty0 * abs(w.drv.v) // w.incr0))
                w.ff = min(abs(w.drv.v) * p['duty_ff_line'] // p['ff_incr'], p['duty_max'])
                if w.drv.state == 'AT_SPEED' and w.t_arrive is None:
                    w.t_arrive = t
            sgn = w.pdir if p['pasm'] else w.sign
            e_true = (w.thf - w.thr) * sgn
            delta = math.radians(90 + (e_true - w.e90) * 360 / 256) * sgn
            Va = p['Vbus'] * w.duty / (16 * 3068)
            we = w.wm * p['pp']
            Vd = Va * math.cos(delta); Vq = Va * math.sin(delta)
            if p['v_dt']:
                # «#3662»: the dead-time voltage, against the phase current (linear below 50 mA)
                im = max(math.hypot(w.idd, w.iq), 0.05)
                Vd -= p['v_dt'] * w.idd / im; Vq -= p['v_dt'] * w.iq / im
            Lh = p['Lh']; R = w.R
            if p['pasm'] and w.drv.state == 'STOPPED':
                w.idd = w.iq = w.pin = 0.0             # «#3662»: at rest the bridge takes the stop mode; modelled as a coast
            else:
                w.idd += (Vd - R * w.idd + we * Lh * w.iq) / Lh * FRAME
                w.iq += (Vq - R * w.iq - we * Lh * w.idd - ke * we) / Lh * FRAME
                w.pin = 1.5 * (Vd * w.idd + Vq * w.iq)
            fr = p['Tc'] * (1 + p['Tnoise'] * noise[i]) * math.tanh(w.wm / p['w0']) + p['Bv'] * w.wm
            if i == 0 and p['step_T'] > 0 and p['step_t'] <= t < p['step_off']:
                fr += p['step_T'] * math.tanh(w.wm / p['w0'])
            T[i] = kt * w.iq - fr
            if p['obst']:
                # the obstacle at this tyre: x the tyre's forward travel, m; F >= 0 pushes back
                x = w.thr * w.sign / 256 / p['pp'] * 2 * math.pi * p['r']
                pen = x - w.anchor
                F = 0.0
                if pen > 0:
                    if p['ob_k'] * pen > p['ob_slip']:
                        w.anchor = x - p['ob_slip'] / p['ob_k']           # the object slides: it yields
                        pen = x - w.anchor
                    F = max(0.0, p['ob_k'] * pen + p['ob_c'] * w.wm * w.sign * p['r'])
                    if w.contact_t is None:
                        w.contact_t = t
                w.F = F
                T[i] -= w.sign * F * p['r']
        aL = (a * T[0] + b * T[1]) / det
        aR = (b * T[0] + a * T[1]) / det
        for i, w in enumerate(W):
            w.wm += (aL if i == 0 else aR) * FRAME
            w.thr += w.wm * p['pp'] * 256 / (2 * math.pi) * FRAME
            sector = math.floor(w.thr / SECTOR)
            e_old = w.e
            w.e = math.floor(w.thf - (sector + 0.5) * SECTOR)
            if p['wrap']:
                w.e = ((w.e + 128) % 256) - 128        # err_ is a wrapped 8-bit angle (:7926-7930)
            if abs(w.e) >= p['fault'] and not (p['pasm'] and w.drv.state == 'STOPPED'):
                w.faulted = True                       # (an undriven bridge takes no fault, :7983)
            if p['diag'] and (not w.ring or w.ring[-1][1] != w.e or w.ring[-1][2] != sector):
                w.ring.append((round(t, 5), w.e, sector, w.drv.v, w.drv.state, w.duty, w.setbacks, w.drv.held))
                del w.ring[:-24]
            # I-5's window in the driver's integer reading (err_ = ... SAR 24 floors, :7979): a tick away from the field
            #  takes |err| from 82..88 to 125..131, wrapped: a lag fault. Either sign of err (the floor makes the
            #  negative side 81.33..87.33 real counts, the positive 82.33..88.33)
            if p['pasm'] and w.drv.state != 'STOPPED' and 82 <= abs(w.e) <= 88:
                w.win_frames += 1
            if p['pasm'] and sector != w.last_sector:
                if 82 <= abs(e_old) <= 88 and (w.last_sector - sector) * (1 if e_old > 0 else -1) > 0:
                    w.back_in_win += 1                 # a tick away from the field from inside the window
            if sector != w.last_sector:
                # D-A: the lag at the edge, exact: the rotor is on the sector boundary, half a sector from the table
                #  angle the frame's err_ is formed from (sawtooth-free, one sample per hall tick)
                lag_now = -w.e if w.drv.v < 0 else w.e
                w.lag_edge = lag_now + 21
                if p['obst']:
                    w.last_tick_t = t
                    if w.contact_t is not None:
                        if (sector - w.last_sector) * w.sign > 0:
                            w.ticks_fwd += 1
                        else:
                            w.ticks_back += 1
                w.last_sector = sector
            if p['obst'] and w.contact_t is not None:
                w.err_pk = max(w.err_pk, abs(w.e))
            # ---- the fold-back (S-2): over the limit, duty -= duty >> 6 and the trim is skipped this frame
            if p['pasm']:
                # (a) the driver's test: the whole-mV net DC-link reading above (max(duty, floor) x k) >> 16 (:8000-8033)
                rd = max(w.pin, 0.0) / p['Vbus'] * p['r_sense']
                if p['i_noise']:
                    rnd_i = (rnd_i * 1103515245 + 12345) & 0x7FFFFFFF
                    rd += ((rnd_i / 0x7FFFFFFF) * 2 - 1) * p['i_noise']
                over = math.floor(rd) > ((max(w.duty, ffloor) * fk) >> 16)
            else:
                over = math.hypot(w.idd, w.iq) > p['i_limit']
            if over:
                w.duty -= w.duty >> 6
                if p['pasm'] and w.duty > w.duty_cap:
                    w.duty = w.duty_cap; w.capped += 1; w.cap_frames += 1   # .dutyLimits after a fold too
                w.duty = max(w.duty, p['duty_min'])
                w.acc = (w.duty - w.ff - w.pterm) << p['acc_shift']
                w.capped += 1                      # D-C: the limit acted (foldback_cnt advanced)
                w.folds += 1
                continue
            # ---- the trim (DRIVER_REV 46), plus the proposed proportional term
            x = abs(w.e) - p['setpoint']
            w.acc += x * (w.duty >> p['preshift'])
            if p['dB'] and (not p['boost_run'] or w.drv.state in RUNNING):
                lag_f = -w.e if w.drv.v < 0 else w.e
                if lag_f >= p['lag_soft']:
                    w.boosts += 1
                    # the boost, in accumulator units: (lag - LAG_SOFT) * (duty >> 4) << (acc_shift - boost_shift)
                    w.acc += ((lag_f - p['lag_soft']) * (w.duty >> p['preshift'])) << (p['acc_shift'] - p['boost_shift'])
            pterm = 0
            if p['dA']:
                pterm = ((w.lag_edge - p['setpoint']) * (w.duty >> p['preshift'])) >> p['kp_shift']
            w.pterm = pterm
            want = (w.acc >> p['acc_shift']) + w.ff + pterm
            d2 = max(p['duty_min'], min(w.duty_cap if p['pasm'] else p['duty_max'], want))
            if d2 != want:
                w.acc = (d2 - w.ff - pterm) << p['acc_shift']
                if d2 < want:
                    w.capped += 1
                    w.cap_frames += 1
            if p['pasm'] and w.drv.state == 'STOPPED':
                d2 = p['duty_min']; w.acc = (d2 - w.ff - pterm) << p['acc_shift']    # .endAtZero, then undriven
            w.duty = d2
        if p['obst'] and any(w.faulted for w in W):
            k_ = [w.faulted for w in W].index(True)
            blk.update(fault_t=t, fault_wheel=('L', 'R')[k_])
            if p['diag']:
                print(f"    diag fault context {'LR'[k_]} (t, err, sector, drv_incr, state, duty, set-backs, held):")
                for r_ in W[k_].ring:
                    print(f"      {r_}")
            break
        if mon is not None:
            for i, w in enumerate(W):
                m = mon['w'][i]
                if mon['t_from'] <= t < mon['t_to']:
                    if m['c0'] is None:
                        m['c0'] = (w.drv.held, w.cap_frames, w.folds, w.boosts, w.back_in_win, w.hold_win,
                                   w.win_frames)
                    lag = -w.e if w.drv.v < 0 else w.e
                    m['lag_pk'] = max(m['lag_pk'], lag)
                    m['idc_pk'] = max(m['idc_pk'], max(w.pin, 0.0) / p['Vbus'])
                    m['iph_pk'] = max(m['iph_pk'], math.hypot(w.idd, w.iq))
                    m['duty_pk'] = max(m['duty_pk'], w.duty)
                    m['soft'] += lag >= p['lag_soft']
                    m['c1'] = (w.drv.held, w.cap_frames, w.folds, w.boosts, w.back_in_win, w.hold_win,
                               w.win_frames)
                if mon['post'][0] <= t < mon['post'][1]:
                    m['post'].append(max(w.pin, 0.0) / p['Vbus'])
                if mon['pre'][0] <= t < mon['pre'][1]:
                    m['pre'].append(max(w.pin, 0.0) / p['Vbus'])
            if mon['fault'] is None and any(w.faulted for w in W):
                k_ = [w.faulted for w in W].index(True)
                mon['fault'] = (t, 'LR'[k_], W[k_].drv.state)
                break
        if f % every == 0:
            samples.append((t, [(w.duty, w.e * w.sign, max(w.pin, 0) / p['Vbus'], w.thr * w.sign / SECTOR,
                                 w.drv.v, w.drv.held, w.drv.state, math.hypot(w.idd, w.iq), w.capped,
                                 # «#3668»: appended, so every reader above (by index) is unchanged
                                 w.setbacks, w.cap_frames, w.folds, w.iq, w.wm) for w in W], scale))
            if trace is not None:
                trace.append(samples[-1])
    ta = [w.t_arrive for w in W if w.t_arrive is not None]
    t0 = (max(ta) if len(ta) == 2 else 0.6) + 0.25
    if t0_override is not None:
        t0 = t0_override
    ws = [s for s in samples if t0 <= s[0] < t0 + win]
    res = dict(engages=engages, faulted=[w.faulted for w in W], boosts=[w.boosts for w in W],
               setbacks=[w.setbacks for w in W])
    if p['obst']:
        blk['t_end'] = t
        blk['wheels'] = [dict(contact=w.contact_t, last_tick=w.last_tick_t, fwd=w.ticks_fwd, back=w.ticks_back,
                              err_pk=w.err_pk, held=w.drv.held, limited=w.capped, blk_best=w.blk_best, F=w.F,
                              setbacks=w.setbacks, dg=w.dg, folds=w.folds, back_in_win=w.back_in_win,
                              hold_win=w.hold_win, win_frames=w.win_frames)
                         for w in W]
        res['block'] = blk
        return res
    if len(ws) < 3:
        res['ok'] = False
        return res
    res['ok'] = True
    pred = abs(target) / TWO32 * (44000 / PASS) * 6
    res['path_min'] = min(s[2] for s in ws)
    res['path_mean'] = sum(s[2] for s in ws) / len(ws)
    for i, name in enumerate(('L', 'R')):
        ds = [s[1][i][0] for s in ws]; es = [s[1][i][1] for s in ws]; am = [s[1][i][2] for s in ws]
        ticks = ws[-1][1][i][3] - ws[0][1][i][3]
        rate = ticks / (ws[-1][0] - ws[0][0])
        dm = sum(ds) / len(ds)
        ph = [s[1][i][7] for s in ws]
        res[name] = dict(fol=100 * rate / pred, duty=dm, swing=max(ds) - dm, err=sum(es) / len(es),
                         err_pk=max(es), amps=sum(am) / len(am), held=ws[-1][1][i][5] - ws[0][1][i][5],
                         iph=sum(ph) / len(ph), iph_pk=max(ph), folds=ws[-1][1][i][8] - ws[0][1][i][8],
                         held_all=samples[-1][1][i][5])
    return res


LEGS = [
    (1, 'sched SLOW +', SLOW, ('SCHED', None, -4), 2.0, 'L 84 % 100 1199 | R 88 % 100 1647 | path 810'),
    (2, 'sched SLOW -', -SLOW, ('SCHED', None, -4), 2.0, 'L 57 % 113 1080 | R 80 % 100 1133 | path 629'),
    (3, 'sched MED +', MED, ('SCHED', None, -4), 1.0, 'L 90 % 100 1460 | R 94 % 100 910 | path 633'),
    (4, 'sched MED -', -MED, ('SCHED', None, -4), 1.0, 'L 88 % 100 1368 | R 94 % 84 1195 | path 756'),
    (5, 'legacy MED +', MED, ('FIXED', 43, 0), 1.0, 'L 100 % 72 95 | R 100 % 72 121 | path 1000'),
    (6, 'legacy MED -', -MED, ('FIXED', 43, 0), 1.0, 'L 100 % 72 238 | R 100 % 72 175 | path 1000'),
    (7, 'sched BRISK +', BRISK, ('SCHED', None, -4), 0.3, 'L 84 % 97 1044 | R 88 % 91 803 | path 861'),
    (9, 'fixed BRISK +', BRISK, ('FIXED', 18, -4), 0.3, 'L 101 % 80 834 | R 100 % 92 1474 | path 1000'),
    (10, 'fixed BRISK -', -BRISK, ('FIXED', 18, -4), 0.3, 'L 100 % 89 965 | R 100 % 94 1250 | path 1000'),
]
LEG_SECONDS = {SLOW: 6.0, MED: 3.5, BRISK: 2.2}


def fmt(r):
    if not r['ok']:
        return 'no window'
    s = ''
    for k in ('L', 'R'):
        x = r[k]
        s += f"{k} {x['fol']:5.1f} % {x['err_pk']:4} {x['swing']:5.0f} (d {x['duty']:5.0f} A {x['amps']:4.2f} h {x['held']:3}) | "
    return (s + f"path {r['path_min']:4} (mean {r['path_mean']:4.0f}, eng {r['engages']})"
            + (f" boost frames {r['boosts']}" if any(r['boosts']) else '')
            + (f" set-backs {r['setbacks']}" if any(r['setbacks']) else '') + (' FAULT' if any(r['faulted']) else ''))


def legs(p, quiet=False, which=None):
    out = {}
    for leg, label, tgt, pair, win, logged in LEGS:
        if which and leg not in which:
            continue
        r = run(p, tgt, LEG_SECONDS[abs(tgt)], pair, win)
        out[leg] = r
        if not quiet:
            print(f"leg {leg:2} {label:14} {fmt(r)}")
            print(f"   {'':14} logged {logged}")
    return out


def signature(r):
    """schedule signature: a wheel held in the window, the path limiter engaged, a wheel under 97 %, swing > 400"""
    if not r['ok']:
        return False
    held = r['L']['held'] + r['R']['held'] > 0
    low = min(r['L']['fol'], r['R']['fol']) < 97
    sw = max(r['L']['swing'], r['R']['swing']) > 400
    return held and low and sw and (r['path_min'] < 1000 or r['engages'] > 0)


def clean(r):
    return r['ok'] and r['L']['held'] + r['R']['held'] == 0 and r['path_min'] == 1000 and r['engages'] == 0 \
        and min(r['L']['fol'], r['R']['fol']) >= 97 and max(r['L']['err_pk'], r['R']['err_pk']) < 100


def block_params(p):
    q = dict(p); q.update(straight=1, obst=1)
    if 'i_limit=' not in ' '.join(sys.argv[2:]):
        q['i_limit'] = 2.0                  # the obstacle session's limit (BM-BLKBUILD limit_a 2)
    return q


def block_set(q, verbose=False):
    """ob_n realizations, contact points spread over one hall sector; returns the summary line"""
    sector_m = 2 * math.pi * q['r'] / 90
    lat = []; stands = []; nolatch = 0; faults = 0; back = 0; best = 0; win_ms = 0.0; win_ticks = 0
    for j in range(int(q['ob_n'])):
        qj = dict(q); qj['ob_x'] = q['ob_x'] + sector_m * j / q['ob_n']
        b = run(qj, SLOW, q['ob_t'], ('SCHED', None, -4), 0.5)['block']
        cs = [x['contact'] for x in b['wheels'] if x['contact'] is not None]
        c0 = min(cs) if cs else None
        back += sum(x['back'] for x in b['wheels'])
        win_ms += sum(x['win_frames'] for x in b['wheels']) / 44
        win_ticks += sum(x['back_in_win'] for x in b['wheels'])
        if b['latch_t'] is not None:
            lat.append(b['latch_t'] - c0); stands.append(b['stand'])
            out = (f"LATCH {b['wheel']} at {b['latch_t']:.3f} s: {1000 * (b['latch_t'] - c0):6.0f} ms after contact, "
                   f"stand {1000 * b['stand']:5.0f} ms after its last tick")
        elif b['fault_t'] is not None:
            faults += 1
            out = f"FAULT {b['fault_wheel']} at {b['fault_t']:.3f} s ({1000 * (b['fault_t'] - c0):.0f} ms after contact)"
        else:
            nolatch += 1
            best = max(best, max(x['blk_best'] for x in b['wheels']))
            out = f"no latch by {b['t_end']:.2f} s ({1000 * (b['t_end'] - c0) if c0 is not None else float('nan'):.0f} ms of contact)"
        if verbose:
            print(f"  ob_x {qj['ob_x']*1000:6.1f} mm: {out}")
            print('  ' + ' ' * 14 + ' | '.join(
                f"{n_} contact {x['contact'] if x['contact'] is None else round(x['contact'], 3)} ticks +{x['fwd']}/-{x['back']} "
                f"err_pk {x['err_pk']} held {x['held']} limited {x['limited']} longest count {x['blk_best']} F {x['F']:.1f} N"
                + (f" set-backs {x['setbacks']}" if x['setbacks'] else '')
                for n_, x in zip('LR', b['wheels'])), flush=True)
            if q['diag']:
                for n_, x in zip('LR', b['wheels']):
                    d = x['dg']
                    if not d['n']:
                        continue
                    secs = d['t1'] - d['folds0'][1]
                    fps = (d['folds1'] - d['folds0'][0]) / secs if secs > 0 else float('nan')
                    print(f"    diag {n_}: stand {d['n']} front passes; a limiter acted on {d['lim']} "
                          f"({100 * d['lim'] / d['n']:.1f} %), |err| >= LAG_SOFT on {d['soft']}; longest limited run "
                          f"{d['run_pk']}, longest gap {d['gap_pk']}; |err| {d['e_lo']}..{d['e_hi']}; duty "
                          f"{d['d_lo']}..{d['d_hi']}; fold frames "
                          f"{fps:.0f}/s; |err| in 82..88 for {x['win_frames'] / 44:.1f} ms (held there "
                          f"{x['hold_win']}), back ticks from it {x['back_in_win']}",
                          flush=True)
    lat.sort(); stands.sort()
    s = f"latched {len(lat)} of {int(q['ob_n'])}, no latch {nolatch}, fault {faults}; contact-to-latch ms "
    s += (f"min {1000 * lat[0]:.0f} median {1000 * lat[len(lat) // 2]:.0f} max {1000 * lat[-1]:.0f}; "
          f"stand ms {1000 * stands[0]:.0f}-{1000 * stands[-1]:.0f}" if lat else 'none')
    s += f"; back ticks {back}" + (f"; longest count without latch {best}" if nolatch else '')
    if q['diag']:
        s += f"; |err| in 82..88 for {win_ms:.0f} ms over all contacts, ticks from it {win_ticks}"
    return 'SUMMARY: ' + s


def mon_line(mon):
    """«#3662»: one transient's readings per wheel (run(mon=...)): the lag's peak in the direction of motion, held passes
    (and the time |err| read 82..88), ticks away from the field from that band, ceiling-clamped and fold frames, boost frames, the
    peaks, and the DC-link current's peak over the destination's steady mean (A, and mV at the Rev B 150 mV/A)"""
    out = []
    for n_, m in zip('LR', mon['w']):
        if m['c0'] is None or m['c1'] is None:
            out.append(f"{n_} --")
            continue
        c = [b_ - a_ for a_, b_ in zip(m['c0'], m['c1'])]
        post = sum(m['post']) / len(m['post']) if m['post'] else float('nan')
        kick = m['idc_pk'] - post
        out.append(f"{n_} lag_pk {m['lag_pk']:4} held {c[0]:3} in-82-88 {c[6] / 44:5.1f} ms back-from-it {c[4]} cap {c[1]:4} "
                   f"fold {c[2]:4} boost {c[3]:5}; duty_pk {m['duty_pk']:5} Iph_pk {m['iph_pk']:5.2f} A DC_pk {m['idc_pk']:.3f} A"
                   + (f" over steady {kick:+.3f} A ({kick * 150:+.0f} mV)" if m['post'] else ''))
    f_ = mon['fault']
    return '\n      '.join(out) + (f"\n      FAULT {f_[1]} at {f_[0]:.3f} s in {f_[2]}" if f_ else '')


def top_rung(q, tgt, prev, pair, kt):
    """«#3668» topspd: one LIMTOP rung, wheels up. prev is commanded from rest on the built-in ramp, then tgt 0.5 s
    after the generator alone would arrive at prev (the harness climbs 10 x 10^6 a rung). Per wheel: the first sample
    reporting AT_SPEED after the step (s; None when none within 6 s, the harness's LADDER_STEADY_MS, whose miss is
    STEADY_TIMEOUT), and over the last 1 s of those 6 s: the rotor's rate and the field's speed (drv_incr) as % of
    the command, the share of 0.5 ms samples reporting AT_SPEED, duty, the lag's mean and peak, held passes, set-backs,
    duty-ceiling frames and fold frames per second, and the noise proxies: the phase current's mean, standard deviation
    and peak, the torque ripple kt x std(iq) and the rotor's speed ripple std(rpm)."""
    d = Drive(q); d.state = 'SPIN_UP'; k = 0
    while d.state != 'AT_SPEED' and k < 40000:
        d.jerk_step(prev, 0); k += 1
    ts = k * PASS / 44000.0 + 0.5
    tr = []
    res = run(q, prev, ts + 6.0, pair, 1.0, sample_ms=0.5, trace=tr, t0_override=ts + 5.0, prog=[(ts, tgt)])
    pred = abs(tgt) / TWO32 * (44000 / PASS) * 6
    win = [s for s in tr if ts + 5.0 <= s[0] < ts + 6.0]
    dt = win[-1][0] - win[0][0]
    n = len(win)

    def sd(xs):
        m = sum(xs) / len(xs)
        return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5

    out = []
    for i in (0, 1):
        col = [[s[1][i][j] for s in win] for j in range(14)]
        a, b = win[0][1][i], win[-1][1][i]
        # the step is taken on the next pass, which leaves AT_SPEED: reach counts from the first sample after that
        left = next((k_ for k_, s in enumerate(tr) if s[0] >= ts and s[1][i][6] != 'AT_SPEED'), len(tr))
        out.append(dict(
            reach=next((s[0] - ts for s in tr[left:] if s[1][i][6] == 'AT_SPEED'), None),
            fol=100 * (b[3] - a[3]) / dt / pred, field=100 * sum(col[4]) / n / tgt, field_min=100 * min(col[4]) / tgt,
            atspd=100 * sum(1 for x in col[6] if x == 'AT_SPEED') / n, duty=sum(col[0]) / n,
            e=sum(col[1]) / n, e_pk=max(col[1]), held=(b[5] - a[5]) / dt, setb=(b[9] - a[9]) / dt,
            cap=(b[10] - a[10]) / dt, folds=(b[11] - a[11]) / dt, iph=sum(col[7]) / n, iph_sd=sd(col[7]),
            iph_pk=max(col[7]), tq_sd=kt * sd(col[12]), rpm_sd=sd(col[13]) * 60 / (2 * math.pi), idc=sum(col[2]) / n))
    return out, res['faulted']


def parse(argv):
    p = dict(Q)
    for a_ in argv:
        k, v = a_.split('=')
        p[k] = type(Q[k])(float(v))
    return p


if __name__ == '__main__':
    mode = sys.argv[1]
    p = parse(sys.argv[2:])
    rr = p['r'] ** 2
    print(f"Iz {p['Iz']} -> J spin {p['Jw'] + 2 * p['Iz'] * rr / p['track']**2:.4f}, straight {p['Jw'] + p['m'] * rr / 2:.4f}; "
          f"Tc {p['Tc']} Lh {p['Lh']*1e3:.2f} mH e90@L18 {p['e90_L18']} Tnoise {p['Tnoise']}"
          + (f"  DESIGN dA {p['dA']} (kp_shift {p['kp_shift']}) dB {p['dB']} (boost_shift {p['boost_shift']}) "
             f"dC {p['dC']} acc_shift {p['acc_shift']}")
          + (f"  D-5 d5 {p['d5']} lag_lim {p['lag_lim']} d5_back {p['d5_back']} d5_step {p['d5_step']} "
             f"d5_sticky {p['d5_sticky']}"
             if p['d5'] else '') + (f"  blk_lim {p['blk_lim']}" if p['blk_lim'] else '')
          + (f"  PASM pasm {p['pasm']} v_dt {p['v_dt']} i_noise {p['i_noise']} (fold k {fold_threshold(p)[0]} "
             f"floor {fold_threshold(p)[1]} at i_limit {p['i_limit']})" if p['pasm'] or p['v_dt'] else '')
          + (f"  cap_lift {p['cap_lift']}" if p['cap_lift'] else '') + (f"  boost_run {p['boost_run']}" if p['boost_run'] else '')
          + (f"  blk_fix {p['blk_fix']}" + (f" blk_win {p['blk_win']}" if p['blk_fix'] == 2 else '') if p['blk_fix'] else ''))
    if mode in ('legs', 'design'):
        out = legs(p)
        bad = [k for k in (1, 2, 3, 4, 7) if not signature(out[k])] if mode == 'legs' else []
        bad2 = [k for k in (5, 6, 9, 10) if not clean(out[k])] if mode == 'legs' else []
        if mode == 'legs':
            print('VERDICT:', 'REPRODUCED' if not bad and not bad2 else
                  f"schedule legs without the signature {bad}; legacy/fixed legs not clean {bad2}")
        else:
            print('DESIGN: legs clean (no hold, no path limit, >= 97 %):',
                  [k for k in out if clean(out[k])], ' not clean:', [k for k in out if not clean(out[k])])
    elif mode == 'step':
        # a straight drive at MED (power 13, ~308 mm/s), then a one-sided load on the LEFT wheel (a grab)
        print('-- straight MED, LEFT load step at 1.5 s; window 1.9-3.4 s')
        for T_ in (0.0, 1.0, 2.0, 4.0, 8.0):
            q = dict(p); q.update(straight=1, step_t=1.5, step_T=T_)
            r = run(q, MED, 3.5, ('SCHED', None, -4), 1.5, t0_override=1.9)
            print(f"  load {T_:4.1f} N m  {fmt(r)}")
            if r['ok']:
                x = r['L']
                print(f"  {'':12}LEFT phase A mean {x['iph']:5.2f} pk {x['iph_pk']:5.2f}; limit/cap frames in window "
                      f"{x['folds']}; held passes whole run {x['held_all']}; fault {r['faulted']}")
    elif mode == 'ramp':
        # the floor's ramp legs (2026-09-30 floor2 2.3): straight, power 13 (MED) from rest, the set acceleration
        print('-- straight MED from rest; logged arrival: 200 -> 2_846 ms (pred 1_790); 1_000 -> 565 (558); 3_000 -> 696 (320)')
        for acc_mm in (200, 1000, 3000):
            q = dict(p); q.update(straight=1)
            q['accel_up'] = acc_mm * 33_958 // 1000
            q['jerk_up'] = max(1, q['accel_up'] // 478)
            # the generator alone (no rotor): the predicted arrival
            d = Drive(q); d.state = 'SPIN_UP'; k = 0
            while d.state != 'AT_SPEED' and k < 20000:
                d.jerk_step(MED, 0); k += 1
            pred_ms = k * PASS / 44.0
            tr = []
            r = run(q, MED, max(4.0, pred_ms / 1000 * 2.5), ('SCHED', None, -4), 0.5, trace=tr)
            arr = None
            for s in tr:
                if all(x[6] == 'AT_SPEED' for x in s[1]):
                    arr = s[0]; break
            held = tr[-1][1][0][5] + tr[-1][1][1][5]
            pmin = min(s[2] for s in tr)
            pk = [max(s[1][i][0] for s in tr) for i in (0, 1)]
            print(f"  {acc_mm:5} mm/s^2: pred {pred_ms:6.0f} ms  arrived {('%6.0f' % (arr * 1000)) if arr else '  none'} ms  "
                  f"held {held:4}  path min {pmin:4}  duty pk {pk[0]}/{pk[1]}")
    elif mode == 'release':
        # a straight drive at MED, a LEFT load on at 1.0 s and released at 2.0 s; window 2.0-3.5 s (the release)
        print('-- straight MED, LEFT load on 1.0 s, off 2.0 s; window over the release, 2.0-3.5 s')
        for T_ in (1.0, 2.0, 4.0):
            q = dict(p); q.update(straight=1, step_t=1.0, step_T=T_, step_off=2.0)
            tr = []
            r = run(q, MED, 3.5, ('SCHED', None, -4), 1.5, t0_override=2.0, trace=tr)
            post = [s for s in tr if s[0] >= 2.0]
            e_min = min(s[1][0][1] for s in post); e_max = max(s[1][0][1] for s in post)
            d_pk = max(s[1][0][0] for s in post)
            print(f"  load {T_:4.1f} N m released: {fmt(r)}")
            print(f"  {'':12}LEFT after release: err min {e_min} max {e_max}, duty pk {d_pk}; fault {r['faulted']}")
    elif mode == 'rtrace':
        # trace the LEFT/RIGHT wheels through a 4 N m load at step_t (default 1.0 s) .. step_off (2.0 s)
        q = dict(p); q.update(straight=1, step_T=p['step_T'] or 4.0)
        if q['step_t'] == 0.0:
            q['step_t'] = 1.0
        if q['step_off'] == 99.0:
            q['step_off'] = 2.0
        tr = []
        run(q, MED, 3.0, ('SCHED', None, -4), 0.5, trace=tr)
        for s in tr[::5]:
            if 0.8 <= s[0] <= 2.6:
                L_, R_ = s[1]
                print(f"t {s[0]*1000:5.0f} | L duty {L_[0]:6} e {L_[1]:5} Iph {L_[7]:5.1f} v {L_[4]/1e6:6.2f}e6 held {L_[5]:4} lim {L_[8]:5} {L_[6]:9}"
                      f" | R e {R_[1]:5} v {R_[4]/1e6:6.2f}e6 | path {s[2]}")
    elif mode == 'block':
        # design doc 7 Q1's condition: a straight drive at power 7 (SLOW) into an obstacle under the obstacle session's
        #  2 A limit (BM-BLKBUILD limit_a 2), the protective stop ported from bFrontProtect(). Each realization meets
        #  the obstacle at a different point of a hall sector (ob_x stepped across one sector of tyre travel, 5.76 mm).
        #  MEASURED (2026-09-30 floor2 obstacle session): solid-object stand 988-1,168 ms band, BRAKE trial latched
        #  1,097 ms after its last tick; COAST trial rocked ~6 s in a 66-76-tick band without latching
        q = block_params(p)
        print(f"-- block: SLOW straight, i_limit {q['i_limit']} A, lag_hold {q['lag_hold']}"
              + (f" (D-5 lag_lim {q['lag_lim']})" if q['d5'] else '') + f", ob_k {q['ob_k']:.0f} N/m, "
              f"ob_slip {q['ob_slip']:.0f} N, ob_c {q['ob_c']} N s/m, ob_dx {q['ob_dx']*1000:.1f} mm, {q['ob_t']} s each")
        print(block_set(q, verbose=True))
    elif mode == 'blockcal':
        # the obstacle's calibration grid: stiffness x the force at which it slides, for the drive given
        q = block_params(p)
        print(f"-- blockcal: lag_hold {q['lag_hold']}, i_limit {q['i_limit']} A, {int(q['ob_n'])} contact points x {q['ob_t']} s")
        for k_ in (300.0, 1000.0, 3000.0, 10000.0, 50000.0):
            for s_ in (1e9, 20.0, 10.0):
                qk = dict(q); qk.update(ob_k=k_, ob_slip=s_)
                print(f"ob_k {k_:6.0f} ob_slip {s_:10.0f} | {block_set(qk)}", flush=True)
    elif mode == 'stepdn':
        # «#3662» F-3: wheels up (as wheelsup), the schedule, the ladder's steps at the built-in ramps (accel 1,000,
        #  decel 1,470 mm/s^2); the step at 2.5 s, its transition read over 2.5-4.0 s, the destination's steady 4.0-4.5 s
        q = dict(p); q.update(m=0.0, Iz=0.0, Tc=0.20, Vbus=18.5)
        print('-- stepdn: wheels up, schedule, built-in ramps; MEASURED (dual-a seq 16_708-16_719, 17_291): 80->20 tr_err_pk '
              '101, tr_i_over 79 / 89 mV, tr_lag 26, tr_cap 367; 40->20 91, 25 mV, 0, 139; 20->80 71, 3 mV, 0, 0')
        for a_, b_, ts, te in ((80_000_000, 20_000_000, 2.5, 4.0), (40_000_000, 20_000_000, 2.5, 4.0),
                               (20_000_000, 80_000_000, 2.5, 4.0), (147_000_000, 0, 3.5, 5.6)):
            # the last: PL-55's own case, a stop from 89 % of full power (Visit 2: over 10 A before the ceiling); its
            #  'over steady' is the peak, the wheel being at rest after
            mon = dict(t_from=ts, t_to=te, post=(te, te + 0.5))
            run(q, -a_, te + 0.5, ('SCHED', None, -4), 0.5, prog=[(ts, -b_)], mon=mon)
            print(f"  {a_ // 1_000_000:3} -> {b_ // 1_000_000:3}e6: {mon_line(mon)}", flush=True)
    elif mode == 'reversal':
        # «#3662» F-2: the floor, a straight drive at -175 tps (power 42: 68,391,000 per pass, RC-TEL l_ci_k), then at
        #  2.5 s one of three commands: 'logged' -- the FlySky's at 31,110-31,870 ms (power 56, 98, 18, 0 at 0, 280, 520,
        #  760 ms); 'reverse' -- to +175 tps; 'stop'. Ramps at the FlySky knobs' rates (setAcceleration /
        #  setDeceleration: 33.958 steps per mm/s^2, jerk over RAMP_TAU_MS = 478 passes)
        V175 = 68_391_000
        seqs = (('logged', [(0.0, 91_711_000), (0.28, 161_668_000), (0.52, 28_416_000), (0.76, 0)], 2.5),
                ('reverse', [(0.0, V175)], 3.5), ('stop', [(0.0, 0)], 2.0))
        rates = [(p['rv_acc'], p['rv_dec'])] if p['rv_acc'] else [(1497, 1048), (1000, 1000), (2900, 1000),
                                                                   (1000, 2600), (2900, 2600)]
        print('-- reversal: floor, straight, from -175 tps; MEASURED (floor-rc, 31,110-32,134 ms, acc 1,497 / dec 1,048): '
              'RIGHT re-synced in SPIN_DN at r_err 100, then FAULTED at 125')
        n_f = 0; n_t = 0; tot = dict(win=0.0, held=0, boost=0, cap=0, iph=0.0, lag=-999)
        for acc_mm, dec_mm in rates:
            q = dict(p); q.update(straight=1)
            q['accel_up'] = acc_mm * 33_958 // 1000; q['jerk_up'] = max(1, q['accel_up'] // 478)
            q['accel_dn'] = dec_mm * 33_958 // 1000; q['jerk_dn'] = max(1, q['accel_dn'] // 478)
            for name, sq, dur in seqs:
                T0 = 2.5
                mon = dict(t_from=T0, t_to=T0 + dur)
                run(q, -V175, T0 + dur, ('SCHED', None, -4), 0.5, prog=[(T0 + a_, b_) for a_, b_ in sq], mon=mon)
                n_t += 1; n_f += mon['fault'] is not None
                for m in mon['w']:
                    if m['c0'] is not None and m['c1'] is not None:
                        c = [b_ - a_ for a_, b_ in zip(m['c0'], m['c1'])]
                        tot['win'] += c[6] / 44; tot['held'] += c[0]; tot['boost'] += c[3]; tot['cap'] += c[1]
                        tot['iph'] = max(tot['iph'], m['iph_pk']); tot['lag'] = max(tot['lag'], m['lag_pk'])
                print(f"  acc {acc_mm:4} dec {dec_mm:4} {name:7}: {mon_line(mon)}", flush=True)
        print(f"SUMMARY: lag faults in {n_f} of {n_t} transients; over all, both wheels: |err| in 82..88 for "
              f"{tot['win']:.0f} ms, held {tot['held']}, ceiling-clamped {tot['cap']}, boost {tot['boost']} frames; "
              f"lag_pk {tot['lag']}, Iph_pk {tot['iph']:.1f} A")
    elif mode == 'topspd':
        # «#3668» (design doc 4.11): wheels up (as wheelsup, but the supply is the mode's), LIMTOP's climb past the duty
        #  ceiling, the schedule's lead unless top_L. The fold-back at the rig's 40 A peak (BM-ABIP2 i_limit_k 12,015;
        #  BM-OCLIM peak_a 40) unless i_limit is given. Positive direction; both wheels (LEFT 501, RIGHT 467 mOhm)
        q = dict(p); q.update(m=0.0, Iz=0.0, Tc=0.20, path=0)
        if 'i_limit=' not in ' '.join(sys.argv[2:]):
            q['i_limit'] = 40.0
        pair = ('SCHED', None, -4) if q['top_L'] == -99.0 else ('FIXED', q['top_L'], -4)
        print('-- topspd: wheels up, each rung from the one 10e6 below; MEASURED (debug_261002-101625.log, DRIVER_REV 47, '
              'pack ~20.5 V): 165 / 175 clean, duty 25,460-25,721 / 27,025-27,306, err_pk 71-74; 185 STEADY_TIMEOUT on '
              'all four; 245 at 1 A: field 12.6-13.1 % (BM-FOLLOW OVER). Columns: reach = first AT_SPEED after the step; '
              'over the last 1 s of 6 s: rotor rate and field speed % of command, AT_SPEED share, per-second counts')
        for V in ((q['top_v'],) if q['top_v'] else (18.5, 20.5)):
            qv = dict(q); qv['Vbus'] = V
            kt = 1.5 * qv['pp'] * ke_fit(qv)
            print(f"  Vbus {V} V, fold at {qv['i_limit']} A peak, lead "
                  f"{'the schedule' if pair[0] == 'SCHED' else pair[1]}, kt {kt:.3f} N m/A")
            rows = [(r_ * 1_000_000, (r_ - 10) * 1_000_000, qv)
                    for r_ in range(int(q['top_lo']), int(q['top_hi']) + 1, 10)]
            if q['top_over']:
                qo = dict(qv); qo['i_limit'] = 1.0
                rows.append((245_000_000, 175_000_000, qo))
            for tgt, prev, qq in rows:
                ws, flt = top_rung(qq, tgt, prev, pair, kt)
                tag = f"{tgt // 1_000_000:3}e6" + (f" at {qq['i_limit']:.0f} A" if qq['i_limit'] != qv['i_limit'] else '')
                for n_, x, f_ in zip('LR', ws, flt):
                    rch = f"{1000 * x['reach']:5.0f} ms" if x['reach'] is not None else ' none   '
                    print(f"    {tag} {n_} reach {rch} | fol {x['fol']:5.1f} % field {x['field']:5.1f} % (min "
                          f"{x['field_min']:5.1f}) AT_SPEED {x['atspd']:3.0f} % duty {x['duty']:6.0f} lag {x['e']:4.1f} pk "
                          f"{x['e_pk']:4} | held {x['held']:4.0f} set-backs {x['setb']:4.0f} cap {x['cap']:6.0f} fold "
                          f"{x['folds']:4.0f} /s | Iph {x['iph']:5.2f} sd {x['iph_sd']:5.2f} pk {x['iph_pk']:5.2f} A "
                          f"torque sd {x['tq_sd']:5.3f} N m rpm sd {x['rpm_sd']:5.2f} Idc {x['idc']:4.2f} A"
                          + (' FAULT' if f_ else ''), flush=True)
    elif mode == 'wheelsup':
        q = dict(p); q.update(m=0.0, Iz=0.0, Tc=0.20, Vbus=18.5)
        print('-- wheels up (no platform, J 0.006, Tc 0.20, 18.5 V), schedule; manual 6.4: swing 178-399, err_pk 76-86 at 10/20e6')
        for tgt in (SLOW, MED, BRISK):
            r = run(q, tgt, 3.0, ('SCHED', None, -4), 1.0)
            print(f"  {tgt/1e6:5.1f}e6  {fmt(r)}")
    elif mode == 'jscan':
        for Iz in (0.18, 0.22, 0.26, 0.30, 0.35, 0.42):
            q = dict(p); q['Iz'] = Iz
            out = legs(q, quiet=True)
            line = ' '.join(f"{k}:{'S' if signature(out[k]) else ('c' if clean(out[k]) else '?')}" for k in sorted(out))
            Js = q['Jw'] + 2 * Iz * rr / q['track'] ** 2
            print(f"Iz {Iz:.2f} (J spin {Js:.4f}) | {line}")
        print("S = the schedule signature (held, path limiter, < 97 %, swing > 400); c = clean (no hold, no limiter, "
              ">= 97 %, err_pk < 100); ? = neither")
