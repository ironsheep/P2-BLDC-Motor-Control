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

«#3668» part C (design doc 4.12, PL-189), off by default so every earlier command reproduces its numbers:
  python3 spin2_model.py grab    [key=value ...]   -- floor-grab: a hand on the LEFT tyre at the 2 A limit (G-3)
  python3 spin2_model.py overend [key=value ...]   -- wheels up: the 1 A over-command, then the limits back and full power (G-4)
  u_arm=1    U-1: the limit hold arms at every fold-back (T-1's limiter), at that pass's sector; the set-back no longer arms
  u_span=N   U-2 at 2: the hold disarms once the rotor is N sectors forward of the last fold's sector (1 = as built)
  u_cap=1    U-5: at a disarm, the field's speed is capped at u_cap_sec (4) sectors over the passes since the last fold
  c4_state=1 the as-built disarm in any state but SPIN_UP / AT_SPEED (holdGate :8881), which the model lacked
  u_give=1, u_jgate=1, u_dn=1   rejected candidates U-3, U-3b, U-4 (design doc 4.12.5)
  blkwin=1   block mode: the BLKWIN mirror (test_bench_dual blockWatch()), at every frame and at the harness's 5 ms poll
  grab_B / grab_v / grab_a / grab_f / grab_rnd   the hand: a damper to a hand moving at grab_v of the command, rocking
             by grab_a of it, every 1 / grab_f s (grab_rnd=1 random -1..1, 2 random -1..0: a hand that only holds back)

«#3678» the DocoEng 4k RPM motor (DOCs/analyses/DOCO-DESK-MODEL-2026-10-03.md), off by default so every earlier command
reproduces its numbers. doco=1 swaps the 6.5in plant for the Doco's (DOCO below: the sheet's numbers, the brackets for
what the sheet does not give, Rev A's 5 mV/A sense, one motor, no platform) AND sets the drive as built at DRIVER_REV
49-52 (the design doc 4.12.11's $FIX $CAL), so a doco* mode runs 6.1.0's servo with no further flags. Any key=value
after doco=1 overrides the preset (Jw, Lh, Tc, Bv, e90 through lead, ...). Every doco* mode takes:
  dv=V       one supply (one of the seven Rev A rows); 0 = the mode's own set
  lead=L     the voltage's lead over q at the servo's point, deg (e90 = 48 - L x 256/360); -99 = the mode's default
  ke_set=K   (any motor) the back-EMF constant, phase peak V per electrical rad/s; 0 = fitted from the 6.5in ladder
  python3 spin2_model.py docoss   doco=1 [...]   -- DERIVED steady state + per-pass arithmetic per Rev A row: hall
                                                    rate per front pass, field step per drive pass, the duty each
                                                    speed needs at a fixed lead, the best lead, the reserve ceiling
  python3 spin2_model.py doco     doco=1 [...]   -- the 6.1.0 servo on a ladder to each row's ceiling, unloaded
  python3 spin2_model.py docoramp doco=1 [...]   -- the wheel-less built-in ramp: rates, times, stops; ramp_x=N runs
                                                    a start at N x the built-in steps
  python3 spin2_model.py docostep doco=1 [...]   -- a load step at top speed: the LAG_HOLD-to-fault margin
  python3 spin2_model.py docohand doco=1 [...]   -- a hand stall at low speed: current, the blocked stop's latch;
                                                    i_limit=A is testSetCurrentLimits(A, A)
  python3 spin2_model.py docohold doco=1 [...]   -- DERIVED: the hold at rest (SM_BRAKE) at the hold defaults
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
         # «#3668» part C (design doc 4.12, PL-189). Off by default: every earlier command reproduces its numbers
         u_arm=0,                 # U-1: the limit hold arms on every running pass the limiter that enters it acted (T-1: the
                                  #  fold-back), and lim_pos becomes that pass's sector; the set-back no longer arms
         u_span=1,                # U-2 at 2: disarm once the rotor is u_span sectors forward of lim_pos (1 = as built, :8888)
         u_give=0,                # U-3: an armed pass that holds the field gives way (holdDecay), limiter this pass or not
         u_jgate=0,               # U-3b (candidate): while armed, jerkStep's lag gate reads the lag as at least LAG_SOFT
         c4_state=0,              # the as-built disarm in any state but SPIN_UP / AT_SPEED (holdGate :8881); the model lacked it
         u_dn=0,                  # U-4 (candidate): the limit hold also acts, and stays armed, in SPIN_DN (c4_state then
                                  #  disarms only in SLOW_TO_CHG and at rest)
         u_cap=0,                 # U-5 (candidate): when the hold disarms (either rule), the field's speed is capped at
                                  #  2 sectors / the passes since the last fold armed it -- an upper bound of the rotor's
                                  #  mean speed since then, the rotor having moved less than 2 sectors -- and the
                                  #  generator's acceleration restarts from 0
         u_cap_sec=2,             # U-5: the sectors in that cap (2 = the bound itself; 4 = twice it, a margin)
         blkwin=0,                # block mode: 1 = mirror BLKWIN (test_bench_dual blockWatch(), SRC_REV 77) and print it
         grab_T=0.0, grab_r=0.0,  # grab mode: the hand on the LEFT tyre, a Coulomb drag grab_T and a rocking torque of
         grab_f=3.0, grab_t=1.0,  #  amplitude grab_r at grab_f Hz (N m, Hz), from grab_t s; grab_n realizations (the rock's
         grab_n=8, grab_s=6.0,    #  phase spread over one cycle), grab_s s each
         grab_ph=0.0,             # grab mode: the rock's phase, rad (the mode sets it per realization)
         grab_B=0.0,              # grab mode: the hand as a damper (N m s/rad) to a hand that moves at grab_v of the
         grab_v=0.2, grab_a=0.0,  #  commanded wheel speed, rocking by grab_a of it at grab_f Hz (backward when grab_a > grab_v)
         grab_rnd=0,              # grab mode: 1 = the hand's rock is random, a new uniform -1..1 every 1 / grab_f s (a hand
                                  #  is not periodic), its sequence seeded by the realization; 2 = the same over -1..0 (a
                                  #  hand that only holds back, never drives the wheel faster than grab_v)
         ov_hold=4.0,             # overend mode: s at the 1 A over-command before the limits return (OVERCMD_HOLD_MS + WINDOW_MS)
         )

PATH_RELEASE_SLOTS, PATH_RELEASE_STEP, PATH_BEHIND = 4, 20, 100
SHORT_SLOTS = 4
FOLD_MIN_MV = 4                  # :7287
RUNNING = ('SPIN_UP', 'AT_SPEED')
RAMPING_DOWN = ('SPIN_DN', 'SLOW_TO_CHG')

# «#3678»: the keys the Doco modes add, each off (0) or unused by every earlier mode
Q.update(doco=0, ke_set=0.0, dv=0.0, lead=-99.0, ramp_x=1.0,
         hand_k=0.5, hand_c=0.002, hand_pwr=10,  # docohand: the hand as a rotational spring, N m/rad, N m s/rad; the power
         step_load=0.0,                          # docostep: one load, N m (0 = the mode's set)
         rung_e6=0,                              # doco: one rung, x 10^6 increment (0 = 25/50/75/100 % of the row)
         sag_t=0.0, sag_rate=0.0)                # run(): the supply falls at sag_rate V/s from sag_t s (0 = none)
DOCO_ROWS = (7.4, 11.1, 12.0, 14.8, 18.5, 22.2, 24.0)
# confgurePowerLimits(), the Rev A rows (src/isp_bldc_motor.spin2, maxRevIncreAtPwr's lookup, the else branch)
DOCO_CEIL_REVA = dict(zip(DOCO_ROWS, (282_000_000, 545_000_000, 335_000_000, 376_000_000, 398_000_000, 470_000_000,
                                      391_000_000)))
DOCO_KE_LL = 3.53 / (1000 * 2 * math.pi / 60)   # DOCs/DOCOMotor.pdf: 3.53 V/kRPM, read as line-to-line PEAK (its no-load
                                                 #  6,800 rpm at 24 V is 24.0 V of it; Kt 0.034 = Ke in SI, the DC form)
DOCO_RATED_NM = 0.0625                           # the sheet's rated torque
DOCO_SECTOR_RAD = 2 * math.pi / 24               # one hall tick of shaft: 15 deg
DOCO = dict(
    pp=4, RL=0.9, RR=0.9,                        # sheet: 8 poles; 1.8 ohm phase to phase, so 0.9 per phase
    ke_set=DOCO_KE_LL / math.sqrt(3) / 4,        # phase peak V per electrical rad/s; kt = 1.5 pp ke = 0.0292 N m per A peak
    Jw=4.0e-6,                                   # kg m^2: NOT on the sheet. Bracket 2e-6 .. 8e-6 (a 20-22 mm x 25-35 mm rotor,
                                                 #  0.5 m r^2, plus the encoder and its coupling); fitted from D1's coast-down
    Tc=0.003, Bv=1.0e-5,                         # N m, N m s/rad: NOT on the sheet beyond the no-load 0.4 A max (<= 0.0136 N m
                                                 #  at 6,800 rpm). Bracket (0.002, 5e-6) .. (0.006, 1.05e-5)
    w0=0.5,                                      # rad/s: the Coulomb term's smoothing (stable at the frame step with this J)
    Lh=1.0e-3,                                   # H per phase: NOT on the sheet. Bracket 0.5 .. 1.5 mH
    e90_L18=48.0,                                # with the FIXED (18, -4) pair this IS e90: 48 puts the voltage on q at the setpoint
    m=0.0, Iz=0.0, path=0,                       # one motor: no platform, no steering object (both model wheels are the Doco)
    r_sense=5,                                   # Rev A, 5 mV per A (the Doco bench)
    i_limit=40.0,                                # I_PEAK_A, the default fold-back (the derate's 27 A average never engages)
    duty_ff_line=24_264,                         # init(): dutyAtFfLine at 270 MHz; ff_incr is set per row (doco_at())
    # the drive as built, DRIVER_REV 49-52: HOLD-SPEED-UNDER-LOAD-DESIGN.md 4.12.11's $FIX $CAL
    acc_shift=16, dB=1, boost_shift=10, dC=1, d5=1, blk_lim=1, cap_lift=48, d5_sticky=1, blk_fix=1, d5_fold_only=1,
    c4_state=1, u_arm=1, u_span=2, u_cap=1, u_cap_sec=4, pasm=1, v_dt=0.18, i_noise=3.0)


def ke_fit(p):
    """ke as spin_model.ke_from_ladder fits it (rung 20e6 at L 18 needs duty 170 per 1e6 at 18.5 V), with the bridge's
    dead-time voltage v_dt opposing the current (a fixed point of the steady dq equations). v_dt = 0: that function.
    «#3678»: ke_set > 0 is the motor's own constant (the Doco's from its sheet), and no fit is made."""
    if p['ke_set']:
        return p['ke_set']
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
        # «#3668» part C (4.12): BLKWIN's mirror at frame resolution and at the harness's 5 ms poll, and the grab's ticks
        w.wf = dict(flag=False, cap=0, sec=None, back_f=-99, n=0, hit=0, park=0, emax=0, unarmed=0,
                    hflag=False, hcap=0, hsec=None, hn=0, hhit=0, hemax=0)
        w.g_last = None; w.g_gap = 0.0; w.g_back = 0; w.g_fwd = 0; w.g_dir = 0
        w.lim_n = 0; w.caps = 0           # U-5: passes since the arming fold; disarms that capped the field's speed

    def permille(w):
        return min(abs(w.drv.v) * 1000 // abs(w.cmd), 1000) if w.cmd else 1000


def run(p, target, seconds, pairs, win, sample_ms=2.0, trace=None, t0_override=None, prog=None, mon=None,
        lim_prog=None):
    """prog: optional [(t s, target), ...] commands taken in time order (the straight drive's sign rule applies);
    mon: optional dict the run fills with the transient readings the stepdn / reversal modes print;
    lim_prog: optional [(t s, amps), ...] current limits taken in time order («#3668» overend: the limits restored)."""
    ke = ke_fit(p); kt = 1.5 * p['pp'] * ke
    W = [Wheel(p, p['RL'], *pairs, target), Wheel(p, p['RR'], *pairs, -target if p['straight'] else target)]
    fk, ffloor = fold_threshold(p)
    ilim = p['i_limit']
    lim_prog = list(lim_prog) if lim_prog else []
    grab_on = p['grab_T'] > 0 or p['grab_B'] > 0          # «#3668» grab mode's hand
    g_k = -1; g_u = 0.0; rnd_g = 4242 + int(p['grab_ph'] * 1000)   # its random rock (grab_rnd)
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
            w.blk_fold = 0                # «#3668» U-4: the fold count as the previous front pass read it
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
        while lim_prog and t >= lim_prog[0][0]:
            _, ilim = lim_prog.pop(0)                  # «#3668»: setFoldLimit() from the front cog, both wheels
            fk, ffloor = fold_threshold(dict(p, i_limit=ilim))
        # ---- the front cog's protective stop, once per 1 ms front pass (bFrontProtect() :2898-2904)
        if p['obst'] and f % 44 == 0:
            for i, w in enumerate(W):
                pos = math.floor(w.thr / SECTOR)
                lim_f = w.capped != w.blk_cap        # D-5 (blk_lim): a limiter acted since the previous front pass
                w.blk_cap = w.capped
                st = w.drv.state
                blk_states = RUNNING
                if p['u_dn']:
                    # U-4's front half: the limiter half reads the fold-back only (as T-1 arms the hold), and counts
                    #  in SPIN_DN too, where the hold now acts
                    lim_f = w.folds != w.blk_fold
                    w.blk_fold = w.folds
                    blk_states = RUNNING + ('SPIN_DN',)
                if p['pasm'] and st not in blk_states:
                    lim_f = False                    # (d) the limiter half counts only in SPIN_UP / AT_SPEED (:2907)
                lim_c = lim_f
                if p['blk_fix'] == 1:
                    # F-a: once a limiter has acted with no tick since, every pass counts until the next tick
                    if pos != w.blk_pos or w.tgt == 0 or st not in blk_states:
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
                e_gate = w.e
                if p['u_jgate'] and w.lim_sector is not None:
                    # U-3b: armed (as the previous pass left it), the generator's lag gate reads LAG_SOFT at least
                    e_gate = (1 if w.drv.v >= 0 else -1) * max(abs(w.e), p['lag_soft'])
                at_rest = w.drv.jerk_step(w.tgt, e_gate)
                if p['pasm'] and not at_rest and w.drv.state in RAMPING_DOWN and prev not in RAMPING_DOWN:
                    w.duty0 = w.duty; w.incr0 = abs(w.drv.v)    # (b) jerkStep's .report: where the ramp-down starts
                if not at_rest:
                    # D-5 (d5): while a limiter has the duty, in the states holdDecay walks, the hold is lag_lim
                    dir_ = -1 if w.drv.v < 0 else 1
                    sec_now = math.floor(w.thr / SECTOR)
                    hold_states = RUNNING + (('SPIN_DN',) if p['u_dn'] else ())
                    # «#3668» T-1 (d5_fold_only): only the fold-back arms the limit hold; else either limiter (as built)
                    lim_now = (w.folds != w.folds_seen) if p['d5_fold_only'] else (w.capped != w.capped_seen)
                    if p['u_arm'] and p['d5'] and lim_now and w.drv.state in hold_states:
                        w.lim_sector = sec_now    # U-1: armed by the limiter itself, at the sector it acted in (a fold
                        w.lim_n = 0               #  pass never disarms: the sketch arms before any disarm test)
                    else:
                        was_armed = w.lim_sector is not None
                        if p['c4_state'] and w.drv.state not in hold_states:
                            w.lim_sector = None   # as built (:8881): any other state disarms
                        if w.lim_sector is not None and (sec_now - w.lim_sector) * dir_ >= p['u_span']:
                            w.lim_sector = None   # C4: the rotor ticked forward past the armed sector (U-2: u_span of them)
                        if was_armed:
                            w.lim_n += 1          # U-5: passes since the fold that last armed (or re-armed) the hold
                            if p['u_cap'] and w.lim_sector is None:
                                cap = p['u_cap_sec'] * 715_827_883 // max(w.lim_n, 1)   # sectors (2^32 / 6) per lim_n passes
                                if abs(w.drv.v) > cap:
                                    w.drv.v = cap if w.drv.v > 0 else -cap
                                    w.drv.a = 0
                                    w.caps += 1
                    lim_hold = p['d5'] and (lim_now or w.lim_sector is not None) \
                        and w.drv.state in hold_states
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
                            if p['d5_sticky'] and not p['u_arm']:
                                w.lim_sector = math.floor(w.thr / SECTOR)
                        w.drv.held += 1
                        if not p['dC']:
                            w.drv.hold_decay()
                        else:
                            # D-C: a held pass walks the field down only when the duty could not rise in the last
                            #  pass (a limiter clamped it: duty_capped advanced; the model has no fold-back below the
                            #  cap); else the field waits at the hold and the trim answers
                            if w.capped != w.capped_seen or (p['u_give'] and lim_hold and w.lim_sector is not None):
                                w.drv.hold_decay()        # U-3: an armed pass that holds also gives way
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
            if p['sag_rate']:
                # «#3678» docosag: the supply falls at sag_rate V/s from sag_t (the bridge's voltage only; the fold's
                #  reading keeps the nominal Vbus, which no default-limit Doco run reaches)
                Va = (p['Vbus'] - max(0.0, t - p['sag_t']) * p['sag_rate']) * w.duty / (16 * 3068)
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
            if i == 0 and grab_on and t >= p['grab_t']:
                # «#3668» grab: a hand on the LEFT tyre (positive resists the drive): a drag and a rocking push, and/or
                #  a damper to a hand moving at grab_v of the commanded speed, rocking by grab_a of it
                ph_ = 2 * math.pi * p['grab_f'] * (t - p['grab_t']) + p['grab_ph']
                rock = math.sin(ph_)
                if p['grab_rnd']:
                    k_ = int((t - p['grab_t']) * p['grab_f'])
                    if k_ != g_k:
                        g_k = k_
                        rnd_g = (rnd_g * 1103515245 + 12345) & 0x7FFFFFFF
                        g_u = (rnd_g / 0x7FFFFFFF) * 2 - 1 if p['grab_rnd'] == 1 else -(rnd_g / 0x7FFFFFFF)
                    rock = g_u
                fr += p['grab_T'] * math.tanh(w.wm / p['w0']) + w.sign * p['grab_r'] * rock
                if p['grab_B']:
                    w_cmd = abs(w.cmd) / TWO32 * (44000 / PASS) * 2 * math.pi / p['pp']
                    fr += p['grab_B'] * (w.wm - w.sign * w_cmd * (p['grab_v'] + p['grab_a'] * rock))
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
            if p['blkwin'] and p['obst']:
                # «#3668» BLKWIN (blockWatch(), test_bench_dual.spin2 :21336-21368): a flag set by a limiter action
                #  (duty_capped + foldback_frames moved) with no tick since, cleared by a tick or a state other than
                #  SPIN_UP / AT_SPEED; |err| read while it was set at the previous read and still is. Here at every
                #  frame (n, hit, emax), and at the harness's own 5 ms poll (hn, hhit, hemax). park: a hit with no
                #  backward tick in the last drive pass; unarmed: a hit with the limit hold not armed
                d = w.wf
                run_ = w.tgt != 0 and w.drv.state in RUNNING
                if d['sec'] is None:
                    d['sec'] = sector; d['cap'] = w.capped; d['hsec'] = sector; d['hcap'] = w.capped
                tick = sector != d['sec']
                if tick and (sector - d['sec']) * w.sign < 0:
                    d['back_f'] = f
                was = d['flag']
                if tick or not run_:
                    d['flag'] = False
                elif w.capped != d['cap']:
                    d['flag'] = True
                d['cap'] = w.capped; d['sec'] = sector
                if was and d['flag']:
                    ae = abs(w.e)
                    d['n'] += 1; d['emax'] = max(d['emax'], ae)
                    if 82 <= ae <= 88:
                        d['hit'] += 1
                        d['park'] += (f - d['back_f']) > PASS
                        d['unarmed'] += w.lim_sector is None
                if f % 220 == 0:
                    hwas = d['hflag']
                    if sector != d['hsec'] or not run_:
                        d['hflag'] = False
                    elif w.capped != d['hcap']:
                        d['hflag'] = True
                    d['hcap'] = w.capped; d['hsec'] = sector
                    if hwas and d['hflag']:
                        d['hn'] += 1; d['hemax'] = max(d['hemax'], abs(w.e))
                        d['hhit'] += 82 <= abs(w.e) <= 88
            if grab_on and t >= p['grab_t'] and sector != w.last_sector:
                if w.g_last is not None:
                    w.g_gap = max(w.g_gap, t - w.g_last)
                w.g_last = t
                if (sector - w.last_sector) * w.sign > 0:
                    w.g_fwd += 1; w.g_dir = 1
                else:
                    w.g_back += 1; w.g_dir = -1
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
                over = math.hypot(w.idd, w.iq) > ilim
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
    res['g'] = [dict(gap=max(w.g_gap, (t - w.g_last) if w.g_last is not None else 0.0), fwd=w.g_fwd, back=w.g_back,
                     setbacks=w.setbacks, t_end=t, armed=w.lim_sector is not None, folds=w.folds, e=w.e, last_dir=w.g_dir,
                     ring=list(w.ring)) for w in W]      # «#3668» grab: appended; no earlier reader sees it
    if p['obst']:
        blk['t_end'] = t
        blk['wheels'] = [dict(contact=w.contact_t, last_tick=w.last_tick_t, fwd=w.ticks_fwd, back=w.ticks_back,
                              err_pk=w.err_pk, held=w.drv.held, limited=w.capped, blk_best=w.blk_best, F=w.F,
                              setbacks=w.setbacks, dg=w.dg, folds=w.folds, back_in_win=w.back_in_win,
                              hold_win=w.hold_win, win_frames=w.win_frames, wf=w.wf)
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
    bw = dict(n=0, hit=0, park=0, unarmed=0, emax=0, hn=0, hhit=0, hemax=0, trials_hit=0, trials_hhit=0)
    for j in range(int(q['ob_n'])):
        qj = dict(q); qj['ob_x'] = q['ob_x'] + sector_m * j / q['ob_n']
        b = run(qj, SLOW, q['ob_t'], ('SCHED', None, -4), 0.5)['block']
        cs = [x['contact'] for x in b['wheels'] if x['contact'] is not None]
        c0 = min(cs) if cs else None
        if q['blkwin']:
            for k_ in ('n', 'hit', 'park', 'unarmed', 'hn', 'hhit'):
                bw[k_] += sum(x['wf'][k_] for x in b['wheels'])
            bw['emax'] = max([bw['emax']] + [x['wf']['emax'] for x in b['wheels']])
            bw['hemax'] = max([bw['hemax']] + [x['wf']['hemax'] for x in b['wheels']])
            bw['trials_hit'] += any(x['wf']['hit'] for x in b['wheels'])
            bw['trials_hhit'] += any(x['wf']['hhit'] for x in b['wheels'])
            if verbose:
                print('    blkwin ' + ' | '.join(
                    f"{n_} window {x['wf']['n'] / 44:6.0f} ms, |err| 82..88 {x['wf']['hit'] / 44:5.1f} ms (parked "
                    f"{x['wf']['park'] / 44:5.1f}, unarmed {x['wf']['unarmed'] / 44:5.1f}) emax {x['wf']['emax']:3}; "
                    f"5 ms poll {x['wf']['hn']} reads, {x['wf']['hhit']} hits, emax {x['wf']['hemax']}"
                    for n_, x in zip('LR', b['wheels'])), flush=True)
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
    if q['blkwin']:
        s += (f"\nBLKWIN: window {bw['n'] / 44:.0f} ms over all contacts; |err| 82..88 for {bw['hit'] / 44:.1f} ms "
              f"(parked {bw['park'] / 44:.1f}, unarmed {bw['unarmed'] / 44:.1f}) on {bw['trials_hit']} of "
              f"{int(q['ob_n'])} contacts, emax {bw['emax']}; at the 5 ms poll {bw['hhit']} hits in {bw['hn']} reads on "
              f"{bw['trials_hhit']} contacts, emax {bw['hemax']}")
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


def doco_at(p, V, lead):
    """«#3678»: the Doco at one Rev A row: the supply, the feedforward's scale (init(): ff_ceiling := the row's ceiling,
    so the feedforward reaches dutyAtFfLine there), the dead-time voltage scaled with the supply (CAL's 0.18 V at
    18.5 V), and the voltage's lead over q at the servo's point (e90 = 48 - lead x 256/360)"""
    q = dict(p)
    q['Vbus'] = V
    q['ff_incr'] = DOCO_CEIL_REVA[V]
    q['v_dt'] = p['v_dt'] * V / 18.5
    q['e90_L18'] = 48.0 - lead * 256 / 360
    return q


def doco_rows(p):
    return (p['dv'],) if p['dv'] else DOCO_ROWS


def doco_ramp(q, x):
    """the built-in ramp's steps (the 6.5in wheel's, which a wheel-less Doco falls back to) times x, jerk over TAU"""
    q = dict(q)
    q['accel_up'] = int(33_958 * x); q['jerk_up'] = max(1, round(q['accel_up'] / 478.3))
    q['accel_dn'] = int(49_918 * x); q['jerk_dn'] = max(1, round(q['accel_dn'] / 478.3))
    return q


def rpm_of(incr):
    """shaft rpm of the Doco at a field increment: one hall cycle is 2^32, 4 cycles a revolution"""
    return incr / TWO32 * (44000 / PASS) * 60 / 4


def doco_need(q, incr, lead):
    """«#3678», DERIVED from the model's own plant at steady state (run()'s dq equations with d/dt = 0, no sector
    sawtooth, no dead-time voltage): the 6.1.0 trim holds the mean |err| at SERVO_SETPOINT (48), so at a fixed offset
    the voltage sits `lead` deg ahead of q and only the duty is free. Unloaded (friction only). Returns (duty, phase A
    peak, d-axis A) or None where no duty holds that speed at that lead."""
    ke = ke_fit(q); kt = 1.5 * q['pp'] * ke
    we = incr / TWO32 * (44000 / PASS) * 2 * math.pi
    wm = we / q['pp']
    iq = (q['Tc'] + q['Bv'] * wm) / kt
    R = q['RL']; X = we * q['Lh']; Z2 = R * R + X * X
    d = math.radians(90 + lead)
    den = R * math.sin(d) - X * math.cos(d)
    if den <= 0:
        return None
    Va = (iq * Z2 + R * ke * we) / den
    idd = (R * Va * math.cos(d) + X * (Va * math.sin(d) - ke * we)) / Z2
    return Va * 16 * 3068 / q['Vbus'], math.hypot(idd, iq), idd


def doco_best_lead(q, incr):
    """the lead (deg, 1-deg grid -30..85) of least phase current whose duty fits duty_max; (lead, duty, amps) or None"""
    best = None
    for L in range(-30, 86):
        r = doco_need(q, incr, L)
        if r and r[0] <= q['duty_max'] and (best is None or r[1] < best[2]):
            best = (L, r[0], r[1])
    return best


def doco_top(q, lead, reserve=0.925):
    """the fastest increment (5e6 grid) whose steady duty stays at or under reserve x duty_max (the 6.5in ceiling rule:
    165e6 ran at 92-93 % of its duty cap); lead None = the best lead at every speed (a lead schedule)"""
    top = 0
    for k in range(1, 215):
        incr = k * 5_000_000
        if lead is None:
            b = doco_best_lead(q, incr)
            ok = b is not None and b[1] <= reserve * q['duty_max']
        else:
            r = doco_need(q, incr, lead)
            ok = r is not None and r[0] <= reserve * q['duty_max']
        if not ok:
            break
        top = incr
    return top


def doco_arrival(q, tgt):
    """the generator alone from rest to tgt: (passes, field travel in angle units)"""
    d = Drive(q); d.state = 'SPIN_UP'; k = 0; trav = 0
    while d.state != 'AT_SPEED' and k < 400_000:
        d.jerk_step(tgt, 0); trav += d.v; k += 1
    return k, trav


def doco_stop(q, v0):
    """the generator alone from v0 at rest acceleration to 0: (passes, field travel in angle units)"""
    d = Drive(q); d.state = 'AT_SPEED'; d.v = v0; d.a = 0; k = 0; trav = 0
    while k < 400_000:
        k += 1
        if d.jerk_step(0, 0):
            break
        trav += d.v
    return k, trav


def doco_rung(q, tgt, settle=1.5, win=1.0, prog=None):
    """one rung from rest on q's ramp; the window is the last `win` s of arrival + settle. Returns (run, mon, arrival s)"""
    k, _ = doco_arrival(q, tgt)
    ta = k * PASS / 44000.0
    t0 = ta + settle - win
    mon = dict(t_from=t0, t_to=t0 + win)
    r = run(q, tgt, ta + settle, ('FIXED', 18, -4), win, t0_override=t0, mon=mon, prog=prog)
    return r, mon, ta


def mon_counts(m, win):
    c = [b_ - a_ for a_, b_ in zip(m['c0'], m['c1'])] if m['c0'] and m['c1'] else [0] * 7
    return dict(held=c[0] / win, cap=c[1] / win, fold=c[2] / win, boost=c[3] / win)


def parse(argv):
    p = dict(Q)
    if 'doco=1' in argv:
        p.update(DOCO)                  # «#3678»: the preset first, so a key=value after it overrides it
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
          + (f"  blk_fix {p['blk_fix']}" + (f" blk_win {p['blk_win']}" if p['blk_fix'] == 2 else '') if p['blk_fix'] else '')
          + (f"  T-1 d5_fold_only 1" if p['d5_fold_only'] and mode in ('grab', 'overend') else '')
          + (f"  U u_arm {p['u_arm']} u_span {p['u_span']} u_give {p['u_give']} u_jgate {p['u_jgate']} u_dn {p['u_dn']} "
             f"u_cap {p['u_cap']} ({p['u_cap_sec']} sectors) c4_state {p['c4_state']}" if p['u_arm'] or p['u_span'] != 1 or p['u_give']
             or p['u_jgate'] or p['c4_state'] or p['u_dn'] or p['u_cap'] else ''))
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
    elif mode == 'grab':
        # «#3668» G-3 (design doc 4.12): floor-grab. A straight drive at power 7 (SLOW) under the session's 2 A limit
        #  (BM-LDBUILD limit_a 2); from grab_t a hand on the LEFT tyre: a drag grab_T and a rocking push of amplitude
        #  grab_r at grab_f Hz, its phase spread over grab_n realizations. Read from grab_t + 0.5 s to the end (or the
        #  fault): each wheel's rotor rate as % of the command, LEFT's field speed, |err| 82..88 time, ticks against the
        #  field from it, the longest LEFT tick gap (LDHOLD's reading), set-backs, held passes, fold frames
        q = dict(p); q.update(straight=1)
        if 'i_limit=' not in ' '.join(sys.argv[2:]):
            q['i_limit'] = 2.0
        print(f"-- grab: SLOW straight, i_limit {q['i_limit']} A, LEFT hand from {q['grab_t']} s: drag {q['grab_T']} N m, "
              f"push {q['grab_r']} N m; damper {q['grab_B']} N m s/rad to a hand at {q['grab_v']} of command rocking "
              f"{q['grab_a']} of it; at {q['grab_f']} Hz, {int(q['grab_n'])} x {q['grab_s']} s. MEASURED (2026-10-02b "
              f"floor-grab, DRIVER_REV 48): LEFT 19 %, RIGHT 57 % (BM-LOADW); LEFT re-synced then faulted (seq 16, 19)")
        pred = SLOW / TWO32 * (44000 / PASS) * 6
        nf = 0; pcts = [[], []]; fpct = []; win_ms = 0.0; bk = 0; gap = 0.0; kinds = dict(lag=0, lead=0)
        for j in range(int(q['grab_n'])):
            qj = dict(q); qj['grab_ph'] = 2 * math.pi * j / q['grab_n']
            tr = []
            mon = dict(t_from=q['grab_t'] + 0.5, t_to=q['grab_s'])
            r = run(qj, SLOW, q['grab_s'], ('SCHED', None, -4), 0.5, trace=tr, mon=mon)
            ws = [s for s in tr if s[0] >= q['grab_t'] + 0.5]
            out = []
            for i in (0, 1):
                if len(ws) > 2:
                    dt = ws[-1][0] - ws[0][0]
                    pc = 100 * (ws[-1][1][i][3] - ws[0][1][i][3]) / dt / pred
                else:
                    pc = float('nan')
                pcts[i].append(pc)
                m = mon['w'][i]
                c = [b_ - a_ for a_, b_ in zip(m['c0'], m['c1'])] if m['c0'] and m['c1'] else [0] * 7
                g = r['g'][i]
                out.append(f"{'LR'[i]} {pc:5.1f} % held {c[0]:5} fold {c[2]:5} |err| 82..88 {c[6] / 44:6.1f} ms, "
                           f"back from it {c[4]}, ticks +{g['fwd']}/-{g['back']} gap {1000 * g['gap']:5.0f} ms "
                           f"set-backs {g['setbacks']}")
                if i == 0:
                    win_ms += c[6] / 44; bk += c[4]; gap = max(gap, g['gap'])
                    fpct.append(100 * sum(abs(s[1][0][4]) for s in ws) / len(ws) / SLOW if ws else float('nan'))
            f_ = mon['fault']
            nf += f_ is not None
            gf = r['g']['LR'.index(f_[1])] if f_ else None
            kind = ''
            if f_:
                # the faulting tick's direction (the reading wraps, so its sign cannot say): a tick back is a lag
                #  fault (the field too far ahead), a tick forward a lead fault (the rotor past its field)
                kind = 'lag' if gf['last_dir'] < 0 else 'lead'
                kinds[kind] += 1
            print(f"  phase {j}/{int(q['grab_n'])}: " + ' | '.join(out) + f" | LEFT field {fpct[-1]:5.1f} %"
                  + (f"  FAULT {f_[1]} at {f_[0]:.3f} s in {f_[2]}, hold {'ARMED' if gf['armed'] else 'not armed'}, "
                     f"{gf['folds']} fold frames before it {kind}" if f_ else ''), flush=True)
            if f_ and q['diag']:
                print('    diag fault context (t, err, sector, drv_incr, state, duty, set-backs, held):')
                for r_ in gf['ring']:
                    print(f"      {r_}")
        pcts = [[x for x in pc if x == x] or [float('nan')] for pc in pcts]   # a run that faulted early has no rate
        fpct = [x for x in fpct if x == x] or [float('nan')]
        print(f"SUMMARY: lag faults {nf} of {int(q['grab_n'])} (rotor behind the field {kinds['lag']}, ahead of it "
              f"{kinds['lead']}); LEFT {min(pcts[0]):.1f}-{max(pcts[0]):.1f} %, RIGHT "
              f"{min(pcts[1]):.1f}-{max(pcts[1]):.1f} % of command; LEFT field {min(fpct):.1f}-{max(fpct):.1f} %; LEFT "
              f"|err| 82..88 {win_ms:.0f} ms over all, back ticks from it {bk}; longest LEFT tick gap {1000 * gap:.0f} ms")
    elif mode == 'overend':
        # «#3668» G-4 (design doc 4.12): wheels up as topspd, the dual-limits over-command and the step after it. From
        #  175e6 at the 40 A peak, 245e6 at 1 A for ov_hold s (OVERCMD_HOLD_MS + WINDOW_MS), then the limits back to
        #  40 A and full power (165e6) together (overCommandStep() then limPowerCheck()). MEASURED (2026-10-02b
        #  dual-limits, DRIVER_REV 48, pack ~20.2 V): OVER drv_incr 47-52 % (BM-FOLLOW -116 / 114 / -128e6), then LEFT
        #  reverse ABS_CURRENT abort at 1,445 mV (~9.6 A DC link), RIGHT silent, LEFT forward completed. DRIVER_REV 47
        #  (2026-10-02): OVER 12.6-13.1 %, both power steps clean
        q = dict(p); q.update(m=0.0, Iz=0.0, Tc=0.20, path=0)
        q['Vbus'] = q['top_v'] or 21.3
        i_hi = q['i_limit'] if 'i_limit=' in ' '.join(sys.argv[2:]) else 40.0
        q['i_limit'] = i_hi
        pair = ('SCHED', None, -4)
        d = Drive(q); d.state = 'SPIN_UP'; k = 0
        while d.state != 'AT_SPEED' and k < 40000:
            d.jerk_step(175_000_000, 0); k += 1
        ts = k * PASS / 44000.0 + 0.5
        t_r = ts + q['ov_hold']
        tr = []
        mon = dict(t_from=t_r, t_to=t_r + 1.0)
        run(q, 175_000_000, t_r + 4.0, pair, 0.5, sample_ms=0.25, trace=tr, mon=mon,
            prog=[(ts, 245_000_000), (t_r, 165_000_000)], lim_prog=[(ts, 1.0), (t_r, i_hi)])
        pred245 = 245_000_000 / TWO32 * (44000 / PASS) * 6
        pred165 = 165_000_000 / TWO32 * (44000 / PASS) * 6
        print(f"-- overend: wheels up, Vbus {q['Vbus']} V; 175e6 -> 245e6 at 1 A for {q['ov_hold']} s, then {i_hi} A and "
              f"165e6 at {t_r:.3f} s. MEASURED (2026-10-02b, REV 48): OVER field 47-52 %, then ~9.6 A DC (abort); REV 47 "
              f"field 12.6-13.1 %, clean")
        for i in (0, 1):
            pre = [s for s in tr if t_r - 1.0 <= s[0] < t_r]
            post = [s for s in tr if t_r <= s[0] < t_r + 1.0]
            last = [s for s in tr if t_r + 3.0 <= s[0] < t_r + 4.0]
            rot = 100 * (pre[-1][1][i][3] - pre[0][1][i][3]) / (pre[-1][0] - pre[0][0]) / pred245
            fld = 100 * sum(s[1][i][4] for s in pre) / len(pre) / 245_000_000      # the field's mean over that 1 s
            over10 = sum(1 for s in post if s[1][i][2] > 10.0) * 0.25
            reach = next((s[0] - t_r for s in tr if s[0] >= t_r + 0.002 and s[1][i][6] == 'AT_SPEED'), None)
            fol = (100 * (last[-1][1][i][3] - last[0][1][i][3]) / (last[-1][0] - last[0][0]) / pred165
                   if len(last) > 2 else float('nan'))
            m = mon['w'][i]
            print(f"  {'LR'[i]} over its last 1 s at 1 A: field {fld:5.1f} % rotor {rot:4.1f} % of 245e6 (field "
                  f"{100 * pre[-1][1][i][4] / 245_000_000:5.1f} % at the restore), duty {pre[-1][1][i][0]:5} | "
                  f"after: DC peak {m['idc_pk']:5.2f} A ({150 * m['idc_pk']:5.0f} mV at 150 mV/A), over 10 A for "
                  f"{over10:5.1f} ms, phase peak {m['iph_pk']:5.1f} A, duty peak {m['duty_pk']:5}, lag peak {m['lag_pk']:4} | "
                  f"AT_SPEED {('%5.0f ms' % (1000 * reach)) if reach is not None else ' none  '} | full power "
                  f"{fol:5.1f} % over its 3-4 s window", flush=True)
        if mon['fault']:
            print(f"  FAULT {mon['fault'][1]} at {mon['fault'][0]:.3f} s in {mon['fault'][2]}")
    elif mode == 'docoss':
        # «#3678» part 1 and 2's arithmetic, DERIVED: per Rev A row, the hall rate against the 1 ms front pass and the
        #  8 ms window slot, the field's step per drive pass against the LAG_HOLD -> fault margin (125 - 100 = 25 counts),
        #  the steady |err| sawtooth's peak against LAG_SOFT, then the model plant's steady state (doco_need()) per Lh
        print('-- docoss: per Rev A row (DERIVED). saw = 48 + (field step + one sector, 42.7) / 2, the steady |err| peak '
              'the trim leaves when it holds the mean at 48. "fills" = rpm at which the back-EMF alone needs duty_max. '
              'Reserve ceilings search to 1.07e9 = 7149 rpm, the last 5e6 step under the increment\'s 2^30 encoding limit '
              '(7174 rpm; setTargetAccel ZEROX 30); '
              '"best lead" = least phase current, unloaded (it minimises current, not duty)')
        args = ' '.join(sys.argv[2:])
        for V in doco_rows(p):
            c = DOCO_CEIL_REVA[V]
            q = doco_at(p, V, 0.0)
            tps = c / TWO32 * (44000 / PASS) * 6
            a = c / 2 ** 24
            saw = 48 + (a + 256 / 6) / 2
            fills = 0.9757 * V / 3.53 * 1000
            print(f"{V:4} V ceiling {c / 1e6:4.0f}e6 = {rpm_of(c):4.0f} rpm, {tps:4.0f} ticks/s: {tps / 1000:4.2f} ticks per "
                  f"front pass, {tps * 0.008:4.1f} per window slot, {tps / (44000 / PASS):4.2f} per drive pass; field step "
                  f"{a:4.1f} counts ({'under' if a < 25 else 'OVER'} the 25 margin); saw {saw:4.1f} "
                  f"({'under' if saw < 80 else 'OVER'} LAG_SOFT); fills {fills:4.0f} rpm", flush=True)
            for Lh in ((p['Lh'],) if 'Lh=' in args else (0.5e-3, 1.0e-3, 1.5e-3)):
                qL = dict(q); qL['Lh'] = Lh
                leads = (0, 15, 30, 45, 60)
                tops = [doco_top(qL, L) for L in leads]
                sched = doco_top(qL, None)
                bl = [doco_best_lead(qL, int(c * f_)) for f_ in (0.25, 0.5, 1.0)]
                need = [doco_need(qL, c, L) for L in leads]
                print(f"   Lh {Lh * 1e3:3.1f} mH | reserve ceiling rpm at lead 0/15/30/45/60: "
                      + '/'.join(f"{rpm_of(t_):4.0f}" for t_ in tops) + f", best lead each speed {rpm_of(sched):4.0f} | "
                      "best lead (A) at 25/50/100 % of the row: "
                      + '/'.join(f"{b[0]:2d} ({b[2]:4.2f})" if b else '--' for b in bl)
                      + " | duty % at the row's ceiling, lead 0/15/30/45/60: "
                      + '/'.join(f"{100 * n[0] / q['duty_max']:3.0f}" if n else '--' for n in need), flush=True)
    elif mode == 'doco':
        # «#3678» part 1: the 6.1.0 servo on a ladder to each row's ceiling, unloaded. lead -99: per row, the best
        #  (least-current) lead at the row's ceiling -- an offset tuned at top speed, as the 2023 rows were
        q0 = doco_ramp(p, p['ramp_x'])
        print(f"-- doco: the 6.1.0 servo, unloaded, from rest on {p['ramp_x']} x the built-in ramp; J {p['Jw']:.1e} kg m^2, "
              f"Lh {p['Lh'] * 1e3:.1f} mH, Tc {p['Tc']} N m, Bv {p['Bv']:.1e}; window the last 1 s of arrival + 1.5 s. "
              f"soft = ms per s the frame |err| reads >= LAG_SOFT; per-second counts; Iph phase A peak; Idc the DC link")
        for V in doco_rows(p):
            q = doco_at(q0, V, 0.0)
            if p['lead'] == -99.0:
                b = doco_best_lead(q, DOCO_CEIL_REVA[V])
                lead = float(b[0]) if b else 0.0
            else:
                lead = p['lead']
            q = doco_at(q0, V, lead)
            print(f"  {V:4} V, lead {lead:3.0f} deg (e90 {q['e90_L18']:5.1f})", flush=True)
            fracs = (p['rung_e6'] * 1e6 / DOCO_CEIL_REVA[V],) if p['rung_e6'] else (0.25, 0.5, 0.75, 1.0)
            for f_ in fracs:
                tgt = int(DOCO_CEIL_REVA[V] * f_)
                r, mon, ta = doco_rung(q, tgt)
                m = mon['w'][0]; c = mon_counts(m, 1.0)
                if r.get('ok') and not any(r['faulted']):
                    x = r['L']
                    print(f"    {int(f_ * 100):3} % {rpm_of(tgt):4.0f} rpm: fol {x['fol']:5.1f} % duty "
                          f"{100 * x['duty'] / q['duty_max']:3.0f} % swing {x['swing']:5.0f} | lag {x['err']:4.1f} pk "
                          f"{m['lag_pk']:3} soft {m['soft'] / 44:5.1f} | held {c['held']:4.0f} cap {c['cap']:5.0f} fold "
                          f"{c['fold']:4.0f} boost {c['boost']:5.0f} | Iph {x['iph']:4.2f} pk {m['iph_pk']:4.2f} Idc "
                          f"{x['amps']:4.2f}", flush=True)
                else:
                    f2 = mon['fault']
                    print(f"    {int(f_ * 100):3} % {rpm_of(tgt):4.0f} rpm: "
                          + (f"FAULT at {f2[0]:.3f} s ({f2[0] - ta:+.3f} s from the generator's arrival) in {f2[2]}"
                             if f2 else 'no window'), flush=True)
    elif mode == 'docomap':
        # «#3678» part 1's bracket: the 6.1.0 servo at each row's 25 % and top rung (11.1 V: 75 %, the top is past its
        #  back-EMF) over the offset's lead x Lh x J, from rest at ramp_x (4 unless given: the steady state, not the
        #  ramp, is judged). clean = no fault, no held pass, lag pk < LAG_HOLD and duty swing < 400 (the 6.5in hunting
        #  signature's bounds, spin2_model.signature()); rough = only the swing is >= 400 (the field never held); hunt =
        #  lag pk >= LAG_HOLD or a held pass; FAULT = the 125 test tripped. TALLY counts each class per rung kind
        rx = p['ramp_x'] if 'ramp_x=' in ' '.join(sys.argv[2:]) else 4.0
        args = ' '.join(sys.argv[2:])
        Lhs = (p['Lh'],) if 'Lh=' in args else (0.5e-3, 1.0e-3, 1.5e-3)
        Js = (p['Jw'],) if 'Jw=' in args else (2.0e-6, 8.0e-6)
        leads = (p['lead'],) if p['lead'] != -99.0 else (0.0, 10.0, 20.0, 30.0)
        print(f"-- docomap: ramp x {rx}; cell = class(lag pk, swing, held/s); leads {leads}")
        tally = {kind: dict(clean=0, rough=0, hunt=0, FAULT=0) for kind in ('25 %', 'top')}
        for V in doco_rows(p):
            for f_ in (0.25, 0.75 if V == 11.1 else 1.0):
                kind = '25 %' if f_ == 0.25 else 'top'
                tgt = int(DOCO_CEIL_REVA[V] * f_)
                for Lh in Lhs:
                    for J in Js:
                        cells = []
                        for L in leads:
                            q = doco_at(doco_ramp(p, rx), V, L); q['Lh'] = Lh; q['Jw'] = J
                            r, mon, ta = doco_rung(q, tgt)
                            m = mon['w'][0]; c = mon_counts(m, 1.0)
                            if mon['fault'] or not r.get('ok'):
                                k_ = 'FAULT'; cells.append(f"L{L:2.0f} FAULT")
                            else:
                                x = r['L']
                                if c['held'] > 0 or m['lag_pk'] >= 100:
                                    k_ = 'hunt'
                                else:
                                    k_ = 'clean' if x['swing'] < 400 else 'rough'
                                cells.append(f"L{L:2.0f} {k_:5}({m['lag_pk']:3},{x['swing']:5.0f},{c['held']:3.0f})")
                            tally[kind][k_] += 1
                        print(f"  {V:4} V {rpm_of(tgt):4.0f} rpm Lh {Lh * 1e3:3.1f} J {J:.0e}: " + ' | '.join(cells), flush=True)
        print('TALLY:', tally)
    elif mode == 'docoramp':
        # «#3678» part 3: the wheel-less built-in ramp. The generator alone (rates, arrival, stop), then the model's
        #  start from rest to the row's ceiling at 1 x and at candidate multiples of the built-in steps
        g = (44000 / PASS) ** 2 * 6 / TWO32                      # ticks/s^2 per unit of ramp step
        up, dn = 33_958 * g, 49_918 * g
        print(f"-- docoramp: built-in up {up:5.1f} ticks/s^2 = {up / 90 * 60:5.1f} rpm/s on the 6.5in, {up / 24 * 60:5.1f} "
              f"rpm/s on the Doco ({90 / 24:.2f} x); down {dn:5.1f} ticks/s^2 = {dn / 90 * 60:5.1f} / {dn / 24 * 60:5.1f} rpm/s")
        q1 = doco_ramp(p, p['ramp_x'])
        for V in doco_rows(p):
            c = DOCO_CEIL_REVA[V]
            k, _ = doco_arrival(q1, c)
            ks, trav = doco_stop(q1, c)
            wm = rpm_of(c) * 2 * math.pi / 60
            fr = p['Tc'] + p['Bv'] * wm
            a_dn = dn * p['ramp_x'] * 2 * math.pi / 24          # shaft rad/s^2 at ramp_x x the built-in deceleration
            print(f"  {V:4} V x {p['ramp_x']:3.1f} to {rpm_of(c):4.0f} rpm: arrives {k * PASS / 44000:5.2f} s; stop {ks * PASS / 44000:5.2f} s, "
                  f"{trav / TWO32 * 6 / 24:6.1f} rev; braking torque the ramp asks J x a {p['Jw'] * a_dn * 1e3:6.3f} mN m "
                  f"against friction {fr * 1e3:5.2f} mN m at the top: {'motoring all the way (no regeneration)' if p['Jw'] * a_dn < p['Tc'] else 'REGENERATES'}",
                  flush=True)
        xs = (p['ramp_x'],) if p['ramp_x'] != 1.0 else (1.0, 2.5, 10.0)
        for V in ((p['dv'],) if p['dv'] else (12.0, 24.0)):
            for x_ in xs:
                q = doco_ramp(doco_at(p, V, 0.0), x_)
                b = doco_best_lead(q, DOCO_CEIL_REVA[V])
                q = doco_at(doco_ramp(p, x_), V, float(b[0]) if b else 0.0)
                c = DOCO_CEIL_REVA[V]
                k, _ = doco_arrival(q, c)
                ta = k * PASS / 44000
                mon = dict(t_from=0.0, t_to=ta + 0.3)
                tr = []
                r = run(q, c, ta + 0.8, ('FIXED', 18, -4), 0.5, t0_override=ta + 0.3, mon=mon, trace=tr)
                m = mon['w'][0]; cc = mon_counts(m, ta + 0.3)
                a_dn = 49_918 * x_ * g * 2 * math.pi / 24
                print(f"  {V:4} V start x {x_:4.1f} ({up * x_ / 24 * 60:6.0f} rpm/s): generator arrives {ta:5.2f} s | over the "
                      f"ramp: lag pk {m['lag_pk']:3} soft {m['soft'] / 44:6.1f} ms, held {cc['held'] * (ta + 0.3):4.0f} "
                      f"boost {cc['boost'] * (ta + 0.3):6.0f} frames, Iph pk {m['iph_pk']:5.2f} A | after: "
                      + (f"fol {r['L']['fol']:5.1f} %" if r.get('ok') else 'no window')
                      + (f" FAULT at {mon['fault'][0]:.3f} s" if mon['fault'] else '')
                      + f" | its stop: J x a {p['Jw'] * a_dn * 1e3:5.3f} mN m vs Tc {p['Tc'] * 1e3:4.1f}", flush=True)
    elif mode == 'docostep':
        # «#3678» part 2's driver-side consequence: at top speed a load step makes the rotor fall behind; the field is held
        #  at LAG_HOLD (100) and, released, steps a whole drive pass's advance. Over 25 counts a step from just under 100
        #  passes the 125 fault test. Each row at its ceiling, and (rows over 419.4e6) at 400e6 for comparison
        rows = doco_rows(p) if p['dv'] else (11.1, 22.2, 18.5)
        loads = (p['step_load'],) if p['step_load'] else (0.02, 0.04, 0.0625, 0.1)
        print('-- docostep: steady at the speed, then a load step held 1 s (N m; the sheet rates 0.0625). LAG_HOLD 100, '
              'fault 125: a field step over 25 counts can cross it')
        for V in rows:
            q = doco_at(p, V, 0.0)
            c = DOCO_CEIL_REVA[V]
            for tgt in ((c, 400_000_000) if c > 419_430_400 else (c,)):
                b = doco_best_lead(q, tgt)
                qv = doco_at(p, V, float(b[0]) if b else 0.0)
                k, _ = doco_arrival(qv, tgt)
                ts = k * PASS / 44000 + 0.5
                for T_ in loads:
                    q2 = dict(qv); q2.update(step_t=ts, step_T=T_)
                    mon = dict(t_from=ts, t_to=ts + 1.0)
                    r = run(q2, tgt, ts + 1.0, ('FIXED', 18, -4), 0.5, t0_override=ts + 0.5, mon=mon)
                    m = mon['w'][0]; cc = mon_counts(m, 1.0)
                    f2 = mon['fault']
                    print(f"  {V:4} V {tgt / 1e6:4.0f}e6 ({tgt / 2 ** 24:4.1f} counts/pass, lead {b[0] if b else 0:2}) load "
                          f"{T_:6.4f}: lag pk {m['lag_pk']:3} held {cc['held']:5.0f}/s cap {cc['cap']:5.0f}/s | "
                          + (f"FAULT {1000 * (f2[0] - ts):6.1f} ms after the step, in {f2[2]}" if f2 else
                             (f"no fault, last 0.5 s fol {r['L']['fol']:5.1f} %, Iph {r['L']['iph']:4.2f} A" if r.get('ok')
                              else 'no window')), flush=True)
    elif mode == 'docosag':
        # «#3678» part 2's driver-side margin on the unloaded bench: at a row's top, the supply is dialled down at
        #  sag_rate V/s (1 unless given) from 0.5 s after the generator arrives, until the drive loses the speed. A field
        #  step under 25 counts should let the field be held and decay (the speed falls, no fault); over 25 a release
        #  from just under LAG_HOLD lands past 125 (a fault). Reported: the supply when the first held pass comes, when
        #  the field speed first falls 2 % under the command, and when (if) the fault test trips
        rate = p['sag_rate'] or 1.0
        rows = doco_rows(p) if p['dv'] else (22.2, 18.5, 24.0, 12.0)
        print(f"-- docosag: unloaded, each row's top, the supply falling {rate} V/s from arrival + 0.5 s")
        for V in rows:
            c = DOCO_CEIL_REVA[V]
            for tgt in ((c, 400_000_000) if c > 419_430_400 else (c,)):
                b = doco_best_lead(doco_at(p, V, 0.0), tgt)
                q = doco_at(p, V, float(b[0]) if b else 0.0)
                k, _ = doco_arrival(q, tgt)
                ts = k * PASS / 44000 + 0.5
                q['sag_t'] = ts; q['sag_rate'] = rate
                dur = min(V - 3.0, 14.0) / rate
                tr = []
                mon = dict(t_from=ts, t_to=ts + dur)
                run(q, tgt, ts + dur, ('FIXED', 18, -4), 0.5, sample_ms=1.0, trace=tr, t0_override=ts, mon=mon)
                held_t = next((s[0] for s in tr if s[0] >= ts and s[1][0][5] > 0), None)
                slow_t = next((s[0] for s in tr if s[0] >= ts and abs(s[1][0][4]) < 0.98 * tgt), None)
                f2 = mon['fault']

                def vat(t_):
                    return V - (t_ - ts) * rate
                print(f"  {V:4} V {tgt / 1e6:4.0f}e6 ({tgt / 2 ** 24:4.1f} counts/pass, {rpm_of(tgt):4.0f} rpm, lead "
                      f"{b[0] if b else 0:2}): first held pass at "
                      + (f"{vat(held_t):5.2f} V" if held_t else ' none ') + "; field 2 % under command at "
                      + (f"{vat(slow_t):5.2f} V" if slow_t else ' none ') + "; "
                      + (f"FAULT at {vat(f2[0]):5.2f} V in {f2[2]}" if f2 else f"no fault down to {vat(ts + dur):5.2f} V"),
                      flush=True)
    elif mode == 'docohand':
        # «#3678» part 1's hand load: a hand closes on the shaft at low speed (a rotational spring hand_k N m/rad with
        #  damping hand_c, reached 0.5 s after the generator arrives; ob_n contact points over one 15-deg hall sector)
        #  and holds. The front cog's blocked stop is ported (bFrontProtect() with F-a). i_limit is the fold-back's peak
        #  (testSetCurrentLimits(A, A)); 40 is the default
        rows = doco_rows(p) if p['dv'] else (12.0, 24.0)
        args = ' '.join(sys.argv[2:])
        lims = (p['i_limit'],) if 'i_limit=' in args else (40.0, 4.0, 2.0)
        n = int(p['ob_n'])
        print(f"-- docohand: power {p['hand_pwr']}, hand {p['hand_k']} N m/rad damping {p['hand_c']}, {n} contact points; "
              f"MEASURED on the 6.5in (2026-09-30 obstacle): BLKSTOP band 988-1,168 ms")
        for V in rows:
            c = DOCO_CEIL_REVA[V]
            tgt = 544_628 + (c - 544_628) * (p['hand_pwr'] - 1) // 99        # incrementForPower()'s map, reverse floor
            b = doco_best_lead(doco_at(p, V, 0.0), c)
            for lim in lims:
                q = doco_at(p, V, float(b[0]) if b else 0.0)
                q['i_limit'] = lim
                k, trav = doco_arrival(q, tgt)
                ta = k * PASS / 44000
                x0 = (trav + tgt * int(0.5 * 44000 / PASS)) / TWO32 * 2 * math.pi / q['pp']
                lat = []; flt = 0; nol = 0; ipk = 0.0; idc = []; fold = 0; setb = 0; Fm = 0.0; dpk = 0
                for j in range(n):
                    qj = dict(q); qj.update(obst=1, r=1.0, ob_x=x0 + DOCO_SECTOR_RAD * j / n, ob_dx=0.0, ob_k=p['hand_k'],
                                            ob_c=p['hand_c'], ob_slip=1e9)
                    mon = dict(t_from=ta + 0.3, t_to=ta + 4.0, post=(ta + 0.9, ta + 1.3))
                    res = run(qj, tgt, ta + 4.0, ('FIXED', 18, -4), 0.5, mon=mon)
                    bl = res['block']; w0_ = bl['wheels'][0]; m = mon['w'][0]
                    ipk = max(ipk, m['iph_pk']); dpk = max(dpk, m['duty_pk'])
                    if m['post']:
                        idc.append(sum(m['post']) / len(m['post']))
                    fold += w0_['folds']; setb += w0_['setbacks']; Fm = max(Fm, w0_['F'])
                    if bl['latch_t'] is not None and w0_['contact'] is not None:
                        lat.append(bl['latch_t'] - w0_['contact'])
                    elif bl['fault_t'] is not None:
                        flt += 1
                    else:
                        nol += 1
                lat.sort()
                print(f"  {V:4} V power {p['hand_pwr']} ({rpm_of(tgt):4.0f} rpm), limit {lim:4.1f} A: latched {len(lat)} of {n}"
                      + (f" at {1000 * lat[0]:5.0f}-{1000 * lat[-1]:5.0f} ms after contact" if lat else '')
                      + f", faults {flt}, no latch {nol} | hand torque pk {Fm * 1e3:5.1f} mN m | Iph pk {ipk:5.2f} A, "
                      f"duty pk {100 * dpk / q['duty_max']:3.0f} %, DC link in the stand {min(idc) if idc else 0:5.2f}-"
                      f"{max(idc) if idc else 0:5.2f} A ({5 * (max(idc) if idc else 0):4.1f} mV at 5 mV/A) | fold frames "
                      f"{fold}, set-backs {setb}", flush=True)
    elif mode == 'docohold':
        # «#3678» the hold at rest (frontHold(), SM_BRAKE), DERIVED: at rest the field stays at the stop angle; while
        #  the halls read the rotor displaced (one tick or more) the duty rises from duty_min to HOLD_CEILING_PCT of
        #  duty_max over HOLD_RISE_MS; HOLD_SLIP_TICKS (2) displaced hands off to the phase short. Stalled, so no
        #  back-EMF: I = Va / R per phase, torque kt I sin(displacement, electrical)
        print('-- docohold (DERIVED): torque at 60 deg electrical (one tick, the first displacement the halls see) and its '
              'peak at 90 deg; the slip at 120 deg (2 ticks)')
        kt = 1.5 * p['pp'] * ke_fit(p)
        q65 = dict(Q); kt65 = 1.5 * q65['pp'] * ke_fit(q65)
        for name, kt_, R, Vs, tick_deg, rated in (('Doco', kt, p['RL'], doco_rows(p), 15.0, DOCO_RATED_NM),
                                                 ('6.5in', kt65, P['R'], (18.5,), 4.0, None)):
            for V in Vs:
                out = []
                for duty, lab in ((1600, 'duty_min'), (int(0.10 * 27_648), 'ceiling 10 %')):
                    Va = V * duty / (16 * 3068)
                    I = Va / R
                    out.append(f"{lab}: {I:5.2f} A, {kt_ * I * math.sin(math.radians(60)) * 1e3:6.1f} / {kt_ * I * 1e3:6.1f} "
                               f"mN m" + (f" ({100 * kt_ * I / rated:3.0f} % of rated)" if rated else '')
                               + f", copper {1.5 * I * I * R:5.2f} W")
                print(f"  {name:5} {V:4} V (kt {kt_:.4f} N m/A; slip at {2 * tick_deg:4.0f} deg of shaft): " + ' | '.join(out))
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
