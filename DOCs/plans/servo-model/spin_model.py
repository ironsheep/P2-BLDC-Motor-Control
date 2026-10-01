"""Desk model for PL-167 (DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md): the DRIVER_REV 46 drive under a floor load.

Physics: DOCs/plans/servo-model/sim_servo.py's voltage-mode dq motor, extended with winding inductance
(dynamic dq currents) and a per-wheel reflected platform inertia and Coulomb load.
Driver: the DRIVER_REV 46 arithmetic, ported from src/isp_bldc_motor.spin2:
  per frame  (.servoTrim / .dutyLimits, :7986-8014): acc += (|e|-48) * (duty>>4); duty = (acc SAR 14) + duty_ff;
             clamp [duty_min, duty_max]; re-derive acc when a clamp acted; fault at |e| >= 125 (:7930)
  per pass   (drvMotor, every 23 frames): lag_s from err_ (:7642); jerkStep with its LAG_SOFT gate (:8757-8851,
             xStar :9002); .justIncr's LAG_HOLD gate (:7734) and holdDecay (:8716); feedForward (:8706)
  per 1 ms   the front cog's lead schedule (frontApplyLead :6459, leadTenthsForIncrement :5025)
The offsets enter as the angle at which the voltage sits on the q axis (e90). DERIVED from the err_ formula
(:7919-7927) and the pair definition (offset_fwd = Z + L for negative increments, offset_rev = Z - L for positive,
:4967): lag_s = (true field lead) + L_eff, L_eff = L - 4 - Z (positive), L + 4 + Z (negative), with the motor's
true hall zero -4 deg (manual 4.2). So e90 = E90_AT_L18 + (L_eff - 18) * 256/360, E90_AT_L18 = 56, the value
sim_servo.py fitted against the 14/338 (L = 18) bench ladder (DRIVE-INTEGRATION-DESIGN.md 5.2).

usage (run from any directory; spin2_model.py imports this file from beside it):
  python3 spin_model.py legs   [key=value ...]   -- the ten floor spin legs (2026-09-30 floor2 2.1), one wheel
  python3 spin_model.py checks [key=value ...]   -- wheels-up negatives: the bench readings the model must also meet
  python3 spin_model.py sweep  [key=value ...]   -- the legs across the parameter bracket (J, Lh, e90, Tc)
  python3 spin_model.py trace  seed=<leg> [...]  -- one leg's 2 ms trace (seed carries the leg number)
  python3 spin_model.py wall   [key=value ...]   -- H-a: the wheels-up torque wall over an (e90_L18, Lh) grid
"""
import math, sys

FRAME = 1 / 44000.0
PASS = 23
SECTOR = 256 / 6.0
TWO32 = 2 ** 32

P = dict(
    Vbus=20.4,            # floor pack at the start check (RC-TEL pack_mv 20_311; RC-BANNER session)
    Vcfg=18.5,            # configured DRIVE_VOLTAGE: ff_ceiling's nominal (init() :4479)
    pp=15, R=0.24,        # phase R: half the measured 0.48 ohm phase to phase (manual 2.4)
    Lh=0.50e-3,           # phase inductance, H: NOT measured; bracketed 0.37-0.74 mH by the wheels-up torque wall
    J=0.030,              # kg m^2 per wheel: wheel (0.006, sim_servo) + its share of the 7.7 kg platform
    Tc=0.45,              # N m Coulomb load per wheel (scrub); FITTED to the legacy leg's duty (see 'legs')
    Bv=0.018,             # N m per mech rad/s (sim_servo)
    duty_max=27_648, duty_min=1_600, duty_ff_line=24_256,   # 270 MHz (manual 3.2; init() :4425-4428)
    ff_incr=147_000_000,
    e90_L18=56.0,
    setpoint=48, preshift=4, acc_shift=14,
    lag_soft=80, lag_hold=100, fault=125,
    accel_up=33_958, jerk_up=71, accel_dn=49_918, jerk_dn=104,   # built-in ramp (DRIVER_REV 46 comments :7141)
    hold_decay_shift=6, incr_floor=1_500,
    wrap=1,               # 1 = err_ wraps as the driver's does: (angle_ - table) SAR 24 of a 32-bit angle, -128..127
                          #  (:7926-7930; the fault test reads the wrapped value). 0 = unwrapped, as the design's
                          #  first runs (2026-10-01, phase 1) had it; it differs only once |err| passes 128
    fine=0,               # wall mode: 1 = the fine grid
    seed=1,
    # --- the proposed drive (design mode) ---
    design=0,             # 1 = D-A + D-B + D-C
    lead_load_k=0.0,      # D-A: counts of lag_s target removed per count of trim (not used: see the design doc)
)

LEAD_INCR = (18_375_000, 36_750_000, 73_500_000, 147_000_000)
LEAD_TENTHS = (205, 50, 80, 80)


def lead_tenths(abs_incr):
    if abs_incr <= LEAD_INCR[0]:
        return LEAD_TENTHS[0]
    for i in range(1, 4):
        if abs_incr <= LEAD_INCR[i]:
            lo, hi = LEAD_TENTHS[i - 1], LEAD_TENTHS[i]
            span = LEAD_INCR[i] - LEAD_INCR[i - 1]
            step = abs(hi - lo) * (abs_incr - LEAD_INCR[i - 1]) // span
            return lo + step if hi >= lo else lo - step
    return LEAD_TENTHS[3]


def l_eff(L, Z, sign):
    return (L - 4 - Z) if sign > 0 else (L + 4 + Z)


def ke_from_ladder(p):
    """ke so the wheels-up rung 20e6 at L = 18 (e90 56, mean e 48) needs duty 170 per 1e6 at 18.5 V (the line)."""
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
        iq = (R * (Va * math.sin(delta) - ke * we) - X * Va * math.cos(delta)) / Z2
        need = (0.20 + 0.018 * wm) / kt          # sim_servo's wheels-up loss
        if iq > need:
            lo = ke
        else:
            hi = ke
    return (lo + hi) / 2


def isqrt(n):
    return math.isqrt(max(0, n))


def xstar(E, J):
    t = (2 * E) // J
    m = isqrt(t)
    if t < m * (m + 1):
        m -= 1
    h = m * (m + 1) // 2
    return (E + J * h) // (m + 1)


class Drive:
    """The DRIVER_REV 46 per-pass state: v = drv_incr, a = accel_now, the reported state."""
    def __init__(s, p):
        s.p = p; s.v = 0; s.a = 0; s.state = 'STOPPED'; s.held = 0

    def jerk_step(s, tgt, err):
        p = s.p
        e = tgt - s.v
        if e != 0:
            sref = e
        else:
            Jx = max(p['jerk_up'], p['jerk_dn'])
            if not (Jx < abs(s.a)):
                s.a = 0; s.state = 'AT_SPEED'
                return tgt == 0
            sref = -s.a
        s_neg = sref < 0
        E = abs(e)
        alpha = -s.a if s_neg else s.a
        shed = ((s.v < 0) != s_neg) and s.v != 0
        J, A = (p['jerk_dn'], p['accel_dn']) if shed else (p['jerk_up'], p['accel_up'])
        J = max(J, 1)
        xs = xstar(E, J)
        Jx = max(p['jerk_up'], p['jerk_dn'])
        if alpha < 0:
            U = min(alpha + Jx, 0)
        elif A < alpha:
            U = max(alpha - Jx, A)
        else:
            U = min(alpha + J, A)
        je = -err if s_neg else err
        if alpha < 0:
            je = -je
        if je >= p['lag_soft'] and alpha >= 0:
            U = max(alpha - J, 0)
        alpha2 = min(U, max(alpha - J, xs))
        s.a = -alpha2 if s_neg else alpha2
        v0 = s.v
        s.v += s.a
        if tgt == 0:
            if s.v == 0 or ((s.v < 0) != (v0 < 0)):
                s.v = 0; s.a = 0; s.state = 'STOPPED'
                return True
            s.state = 'SPIN_DN'
            return False
        if s.v == tgt:
            s.state = 'AT_SPEED'
        elif ((s.v < 0) != (tgt < 0)) and s.v != 0:
            s.state = 'SLOW_TO_CHG'
        else:
            s.state = 'SPIN_UP' if abs(s.v) < abs(tgt) else 'SPIN_DN'
        return False

    def hold_decay(s):
        if s.state == 'AT_SPEED':
            s.state = 'SPIN_UP'
        if s.state == 'SPIN_UP' and abs(s.v) >= s.p['incr_floor']:
            s.v -= s.v >> s.p['hold_decay_shift']     # SAR: Python >> floors, as SAR does


def run_leg(p, target, seconds, pair, win=None, sample_ms=2.0, trace=None):
    """One wheel, one leg from rest. pair: ('SCHED', None) or ('FIXED', L) with Z; returns window statistics."""
    kind, Lfix, Z = pair
    sign = 1 if target > 0 else -1
    ke = ke_from_ladder(p); kt = 1.5 * p['pp'] * ke
    R, Lh = p['R'], p['Lh']
    drv = Drive(p)
    thf = 0.0; thr = 0.0; w = 0.0          # counts, counts, counts/s (signed)
    idd = 0.0; iq = 0.0
    duty = p['duty_min']; acc = duty << p['acc_shift']; duty_ff = 0
    e_meas = 0
    L = lead_tenths(0) / 10 if kind == 'SCHED' else Lfix
    e90 = p['e90_L18'] + (l_eff(L, Z, sign) - 18) * 256 / 360
    started = False
    n = int(seconds / FRAME)
    every = int(sample_ms / 1000 / FRAME)
    t_arrive = None
    samples = []
    faulted = False
    hall_ticks = 0; last_sector = 0
    for f in range(n):
        t = f * FRAME
        # ---- front cog, once per ms: the lead schedule
        if kind == 'SCHED' and f % 44 == 0:
            L = lead_tenths(abs(drv.v)) / 10
            e90 = p['e90_L18'] + (l_eff(L, Z, sign) - 18) * 256 / 360
        # ---- drive pass
        if f % PASS == 0 and not faulted:
            lag_s = -e_meas if drv.v < 0 else e_meas
            if not started:
                started = True
                thf = (math.floor(thr / SECTOR) + 0.5) * SECTOR      # seeded from the halls: err 0
                drv.state = 'SPIN_UP'
            at_rest = drv.jerk_step(target, e_meas)
            if not at_rest:
                if lag_s < p['lag_hold']:
                    thf += drv.v / TWO32 * 256
                else:
                    drv.held += 1
                    drv.hold_decay()
            # feedForward: |v| * duty_max / ff_ceiling, ff_ceiling = 147e6 (18.5 V config) * duty_max / dutyAtFfLine
            duty_ff = min(abs(drv.v) * p['duty_ff_line'] // p['ff_incr'], p['duty_max'])
            if drv.state == 'AT_SPEED' and t_arrive is None:
                t_arrive = t
        # ---- physics (rotor frame; e > 0: rotor trails the field in + direction)
        e_true = (thf - thr) * sign
        delta = math.radians(90 + (e_true - e90) * 360 / 256) * sign
        Va = p['Vbus'] * duty / (16 * 3068)
        we = w * 2 * math.pi / 256
        Vd = Va * math.cos(delta); Vq = Va * math.sin(delta)
        didt = (Vd - R * idd + we * Lh * iq) / Lh
        diqt = (Vq - R * iq - we * Lh * idd - ke * we) / Lh
        idd += didt * FRAME; iq += diqt * FRAME
        T = kt * iq
        wm = we / p['pp']
        if abs(wm) < 1e-3 and abs(T) <= p['Tc']:
            wm = 0.0
        else:
            fr = p['Tc'] * (1 if (wm > 0 or (wm == 0 and T > 0)) else -1) + p['Bv'] * wm
            wm += (T - fr) / p['J'] * FRAME
        w = wm * p['pp'] * 256 / (2 * math.pi)
        thr += w * FRAME
        sector = math.floor(thr / SECTOR)
        if sector != last_sector:
            hall_ticks += abs(sector - last_sector); last_sector = sector
        est = (sector + 0.5) * SECTOR
        e_meas = math.floor(thf - est)
        if p['wrap']:
            e_meas = ((e_meas + 128) % 256) - 128
        if abs(e_meas) >= p['fault']:
            faulted = True
        # ---- the trim, every frame
        x = abs(e_meas) - p['setpoint']
        acc += x * (duty >> p['preshift'])
        want = (acc >> p['acc_shift']) + duty_ff
        d2 = max(p['duty_min'], min(p['duty_max'], want))
        if d2 != want:
            acc = (d2 - duty_ff) << p['acc_shift']
        duty = d2
        if f % every == 0:
            pin = 1.5 * (Vd * idd + Vq * iq)
            samples.append((t, duty, e_meas * sign, max(pin, 0.0) / p['Vbus'], thr * sign / SECTOR, drv.v, drv.held, drv.state))
            if trace is not None:
                trace.append(samples[-1])
    if win is None:
        return samples, faulted
    t0 = (t_arrive if t_arrive is not None else 0.6) + 0.25
    ws = [s for s in samples if t0 <= s[0] < t0 + win]
    if len(ws) < 3:
        return dict(ok=False, faulted=faulted)
    ds = [s[1] for s in ws]; es = [s[2] for s in ws]; am = [s[3] for s in ws]
    ticks = ws[-1][4] - ws[0][4]
    rate = ticks / (ws[-1][0] - ws[0][0])
    pred = abs(target) / TWO32 * (44000 / PASS) * 6
    held_in = ws[-1][6] - ws[0][6]
    dmean = sum(ds) / len(ds)
    return dict(ok=True, faulted=faulted, fol=100 * rate / pred, rate=rate, pred=pred,
                duty=dmean, duty_pk=max(ds), swing=max(ds) - dmean,
                err=sum(es) / len(es), err_pk=max(es), amps=sum(am) / len(am), held=held_in,
                e90=e90, L=L)


SLOW, MED, BRISK = 10_093_936, 20_087_872, 36_744_432
LEGS = [  # (leg, pair label, target, (kind, L, Z), window s, logged LEFT/RIGHT (fol, err_pk, swing))
    (1, 'sched SLOW +', SLOW, ('SCHED', None, -4), 2.0, '84/88 %, 100/100, 1199/1647'),
    (2, 'sched SLOW -', -SLOW, ('SCHED', None, -4), 2.0, '57/80 %, 113/100, 1080/1133'),
    (3, 'sched MED +', MED, ('SCHED', None, -4), 1.0, '90/94 %, 100/100, 1460/910'),
    (4, 'sched MED -', -MED, ('SCHED', None, -4), 1.0, '88/94 %, 100/84, 1368/1195'),
    (5, 'legacy MED +', MED, ('FIXED', 43, 0), 1.0, '100/100 %, 72/72, 95/121'),
    (6, 'legacy MED -', -MED, ('FIXED', 43, 0), 1.0, '100/100 %, 72/72, 238/175'),
    (7, 'sched BRISK +', BRISK, ('SCHED', None, -4), 0.3, '84/88 %, 97/91, 1044/803'),
    (9, 'fixed BRISK +', BRISK, ('FIXED', 18, -4), 0.3, '101/100 %, 80/92, 834/1474'),
    (10, 'fixed BRISK -', -BRISK, ('FIXED', 18, -4), 0.3, '100/100 %, 89/94, 965/1250'),
]
LEG_SECONDS = {SLOW: 6.0, MED: 3.5, BRISK: 2.2}


def parse(argv):
    p = dict(P)
    for a in argv:
        k, v = a.split('=')
        p[k] = type(P[k])(float(v)) if not isinstance(P[k], str) else v
    return p


def fmt(r):
    if not r.get('ok'):
        return 'no window' + (' FAULT' if r.get('faulted') else '')
    return (f"fol {r['fol']:5.1f} %  err {r['err']:5.1f} pk {r['err_pk']:4}  duty {r['duty']:6.0f} pk {r['duty_pk']:6} "
            f"swing {r['swing']:5.0f}  A {r['amps']:5.2f}  held {r['held']:4}  (L {r['L']:4.1f}, e90 {r['e90']:4.1f})"
            + ('  FAULT' if r['faulted'] else ''))


def legs(p, quiet=False):
    out = {}
    for leg, label, tgt, pair, win, logged in LEGS:
        r = run_leg(p, tgt, LEG_SECONDS[abs(tgt)], pair, win=win)
        out[leg] = r
        if not quiet:
            print(f"leg {leg:2} {label:14} {fmt(r)}   | logged {logged}")
    return out


def verdict(out):
    """The falsification bar: schedule legs show the signature, legacy/fixed do not."""
    bad = []
    for leg in (1, 2, 3, 4, 7):
        r = out[leg]
        if not r.get('ok') or not (r['fol'] < 97 and r['err_pk'] >= 100 and r['swing'] > 400 and r['held'] > 0):
            bad.append(f"sched leg {leg} lacks the signature")
    for leg in (5, 6, 9, 10):
        r = out[leg]
        if not r.get('ok') or not (r['fol'] >= 98 and r['err_pk'] < 100 and r['held'] == 0):
            bad.append(f"leg {leg} shows the signature")
    return bad


if __name__ == '__main__':
    mode = sys.argv[1]
    p = parse(sys.argv[2:])
    print(f"ke {ke_from_ladder(p):.5f} V s/rad  kt {1.5 * p['pp'] * ke_from_ladder(p):.3f} N m/A  "
          f"J {p['J']}  Tc {p['Tc']}  Lh {p['Lh'] * 1e3:.2f} mH  e90@L18 {p['e90_L18']}")
    if mode == 'legs':
        out = legs(p)
        bad = verdict(out)
        print('VERDICT:', 'REPRODUCED (schedule signature present; legacy/fixed absent)' if not bad else '; '.join(bad))
    elif mode == 'checks':
        wu = dict(p); wu.update(J=0.006, Tc=0.20, Vbus=18.5)
        print('-- wheels up (J 0.006, Tc 0.20, 18.5 V): manual 6.4 measured swing 178-399, err_pk 76-86 at 10/20e6')
        for tgt in (SLOW, MED, BRISK):
            r = run_leg(wu, tgt, 3.0, ('SCHED', None, -4), win=1.0)
            print(f"  sched {tgt/1e6:5.1f}e6  {fmt(r)}")
        print('-- wheels up, the torque wall (manual 6.2: at 49 ticks/s L -2 held 51 %, L -7 never settled; '
              'the quarter flat -2..8)')
        for L in (20.5, 8, 3, -2, -7):
            r = run_leg(wu, 18_375_000, 3.0, ('FIXED', L, -4), win=1.0)
            print(f"  eighth L {L:5.1f}  {fmt(r)}")
        for L in (8, 3, -2):
            r = run_leg(wu, 36_750_000, 3.0, ('FIXED', L, -4), win=1.0)
            print(f"  quarter L {L:5.1f}  {fmt(r)}")
    elif mode == 'sweep':
        n_ok = 0; n = 0
        for J in (0.020, 0.030, 0.045):
            for Lh in (0.37e-3, 0.50e-3, 0.74e-3):
                for e90 in (52.0, 56.0, 60.0):
                    for Tc in (0.30, 0.45, 0.60):
                        q = dict(p); q.update(J=J, Lh=Lh, e90_L18=e90, Tc=Tc)
                        out = legs(q, quiet=True)
                        bad = verdict(out)
                        n += 1; n_ok += (not bad)
                        s = ' '.join(f"{k}:{out[k]['fol']:.0f}/{out[k]['err_pk']}/{out[k]['swing']:.0f}"
                                     if out[k].get('ok') else f"{k}:--" for k in sorted(out))
                        print(f"J {J:.3f} Lh {Lh*1e3:.2f} e90 {e90:.0f} Tc {Tc:.2f} | {'OK ' if not bad else 'NO '} | {s}")
        print(f"REPRODUCED in {n_ok} of {n} parameter sets")
    elif mode == 'wall':
        # H-a (design doc 3.6): refit e90 and the winding inductance jointly to the wheels-up torque wall.
        # MEASURED targets (manual 6.2; VISIT-8B-EVALUATION.md 3.6, wheels up, steps within 2 % counted as held):
        #   eighth (18.375e6): L 3 -> 91 %, L -2 -> 51 %, L -7 never steady; L 8 and up held (minima 13-23)
        #   quarter (36.75e6): L -2, 3, 8 held (a minimum at -2 on one wheel-direction; flat -2..8)
        # score = squared misses of the two eighth numbers + squared shortfalls under 98 % where held was measured
        #         + squared excess over 40 % at the eighth's L -7 (never steady: well under the -2 step's 51 %)
        wu = dict(p); wu.update(J=0.006, Tc=0.20, Vbus=18.5)
        print('e90  Lh mH | eighth L 8 / 3 / -2 / -7 (held at -2, -7) | quarter L 8 / 3 / -2 / -7 | score')
        rows = []
        if p['fine']:    # fine=1: the valley the coarse grid finds
            e90s = (51.0, 52.0, 53.0, 54.0, 55.0)
            Lhs = tuple(x * 1e-5 for x in range(45, 110, 5))
        else:
            e90s = (40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0)
            Lhs = (0.20e-3, 0.30e-3, 0.37e-3, 0.50e-3, 0.62e-3, 0.74e-3, 0.90e-3)
        for e90 in e90s:
            for Lh in Lhs:
                q = dict(wu); q.update(e90_L18=e90, Lh=Lh)
                e8 = {L: run_leg(q, 18_375_000, 3.0, ('FIXED', L, -4), win=1.0) for L in (8, 3, -2, -7)}
                e4 = {L: run_leg(q, 36_750_000, 3.0, ('FIXED', L, -4), win=1.0) for L in (8, 3, -2, -7)}
                f8 = {L: (r['fol'] if r.get('ok') else 0.0) for L, r in e8.items()}
                f4 = {L: (r['fol'] if r.get('ok') else 0.0) for L, r in e4.items()}
                score = (f8[3] - 91) ** 2 + (f8[-2] - 51) ** 2 + max(0.0, 98 - f8[8]) ** 2 \
                    + sum(max(0.0, 98 - f4[L]) ** 2 for L in (8, 3, -2)) + max(0.0, f8[-7] - 40) ** 2
                h8 = [e8[L].get('held', 0) if e8[L].get('ok') else -1 for L in (-2, -7)]
                flt = any(r.get('faulted') for r in list(e8.values()) + list(e4.values()))
                rows.append((score, e90, Lh))
                print(f"{e90:4.0f} {Lh*1e3:5.2f} | {f8[8]:5.1f} {f8[3]:5.1f} {f8[-2]:5.1f} {f8[-7]:5.1f} ({h8[0]:4} {h8[1]:4}) | "
                      f"{f4[8]:5.1f} {f4[3]:5.1f} {f4[-2]:5.1f} {f4[-7]:5.1f} | {score:8.0f}" + ('  FAULT' if flt else ''),
                      flush=True)
        rows.sort()
        print('best five (score, e90_L18, Lh mH):', [(round(s), e, round(L * 1e3, 2)) for s, e, L in rows[:5]])
    elif mode == 'ladder':
        # wheels up, the fixed 14/338 pair (L 18): steady duty per 1e6 and err at the ladder's rungs. MEASURED
        #  (DRIVE-INTEGRATION-DESIGN.md 5.1, the pass 2 ladder): 167-174 duty per 1e6 at rungs 3-7, mean |e| 48 at
        #  40-120e6. The ladder was run at the old duty clip (24,264) with the old servo: duty per 1e6 and the duty
        #  reserve at 120e6 are the comparable readings, err_pk is not
        wu = dict(p); wu.update(J=0.006, Tc=0.20, Vbus=18.5, duty_max=24_264)
        print('-- wheels up, L 18, duty clip 24,264, 18.5 V')
        for inc in (10e6, 20e6, 40e6, 60e6, 80e6, 100e6, 120e6):
            r = run_leg(wu, int(inc), 3.0, ('FIXED', 18, -4), win=1.0)
            print(f"  {inc/1e6:5.0f}e6  duty per 1e6 {r['duty'] / (inc / 1e6):6.1f}  {fmt(r)}" if r.get('ok') else
                  f"  {inc/1e6:5.0f}e6  {fmt(r)}")
    elif mode == 'start':
        # wheels up, the schedule, a start from rest to the quarter (36.75e6) on the built-in ramp: START's two
        #  acceptance metrics as start_metrics.py computes them. MEASURED on today's servo (manual 6.4; Visit 8 / 8b):
        #  largest duty drop 0.01-0.03, start current peak over settled 1.15-1.53
        wu = dict(p); wu.update(J=0.006, Tc=0.20, Vbus=18.5)
        s, _ = run_leg(wu, 36_750_000, 2.0, ('SCHED', None, -4))
        leave = 0
        for n_, r in enumerate(s):
            if r[1] <= wu['duty_min']:
                leave = n_ + 1
        end = next((n_ for n_, r in enumerate(s) if r[7] == 'AT_SPEED'), len(s))
        run_max, drop = 0, 0.0
        for r in s[leave:end]:
            run_max = max(run_max, r[1])
            if run_max:
                drop = max(drop, (run_max - r[1]) / run_max)
        tail = [r[3] for r in s if r[0] >= s[-1][0] - 0.06]
        print(f"start to 36.75e6: duty drop {drop:.3f}  current peak / settled {max(r[3] for r in s) / (sum(tail) / len(tail)):.2f}"
              f"  arrival {s[end][0] * 1000 if end < len(s) else float('nan'):.0f} ms  held {s[-1][6]}")
    elif mode == 'trace':
        tr = []
        leg = int(p['seed'])           # trace mode: seed=<leg number>

        L = [x for x in LEGS if x[0] == leg][0]
        run_leg(p, L[2], LEG_SECONDS[abs(L[2])], L[3], trace=tr)
        for s in tr[::5]:
            print(f"t {s[0]*1000:6.0f} duty {s[1]:6} e {s[2]:5} A {s[3]:5.2f} ticks {s[4]:7.1f} v {s[5]/1e6:6.2f}e6 held {s[6]:4} {s[7]}")
