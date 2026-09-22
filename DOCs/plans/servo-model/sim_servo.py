"""Desk model of the 6.5in hub motor under the shipped PASM driver's field clock + duty servo.

Frame-accurate (44 kHz) for the servo, pass-accurate (every 23 frames) for the ramp, with the hall
angle held per sector exactly as the driver holds it. Electrical: R-only dq model (voltage mode).
Mechanical: one inertia, coulomb + viscous loss. Positive direction only; e > 0 = rotor trails.

Units: angles in driver err_ counts (256 per electrical cycle); duty in driver duty_ counts.

usage: python3 sim_servo.py <scenario> [key=value ...]
  scenarios: start       -- the QTR start, 36.75e6, printed every 2 ms like BM-TS
             ladder      -- steady rungs, prints mean/peak duty and e per rung

The evidence base for DOCs/plans/DRIVE-INTEGRATION-DESIGN.md section 5 («#3589», 2026-09-22).
Everything it says is DERIVED; the bench certifies. Reproduce the design's tables with:
  python3 sim_servo.py ladder                         -- §5.2, the shipped servo against the ladder
  python3 sim_servo.py ladder mode=frac ki=0.05       -- §5.2, band and asymmetry removed, still hunts
  python3 sensitivity.py                              -- §5.3, every variant, shipped against D-1 + D-2
  python3 start_metrics.py log <bench log>            -- §5.5 A-1/A-2 on real START traces
  python3 start_metrics.py model mode=ffpi kff=165.0 ki=0.03125 ksched=1
Fitted: e90 only (default below). Estimated, not fitted: J and R -- sensitivity.py varies them.
"""
import math, sys

P = dict(
    Vbus=18.5, pp=15, R=0.25, J=0.006,
    Tc=0.20, Bv=0.018,             # coulomb N*m, viscous N*m per mech rad/s
    duty_max=24264, duty_min=1600,
    e90=56.0,                       # FITTED: e_true (counts) at which the voltage sits at 90 deg (Id = 0)
    sp=42, up=18, dn=4, shift=8,    # the shipped servo
    lag_soft=80, lag_hold=100,
    ramp_min=1500, ramp_inc=22, ramp_max=200_000,
    mode='shipped',                 # shipped | frac | fftrim | ffpi (ffpi with ksched=1 is D-1 + D-2)
    kff=170.0,                      # feedforward duty per 1e6 incr
    kp=0.0, ki=0.0,                 # ffpi gains: duty per count, duty per count per frame
    interp=0,                       # 1 = servo sees the interpolated rotor angle, not the held hall angle
    ksched=0,                       # 1 = integral gain scales with duty
)
FRAME = 1 / 44000.0
PASS = 23
SECTOR = 256 / 6.0
# back-EMF constant from the ladder: steady duty ~170 per 1e6 incr, taken as pure back-EMF at 90 deg
ELEC_HZ_PER_E6 = 1e6 / 2**32 * 44000 / PASS            # electrical Hz per 1e6 incr


def ke_of(p):
    # the ladder's steady duty (170 per 1e6 at mean e 48) is back-EMF / sin(delta at e = 48)
    v_per_hz = (170.0 / p['duty_max'] * p['Vbus'] / 2) / ELEC_HZ_PER_E6
    d48 = math.radians(90.0 + (48 - p['e90']) * 360 / 256)
    return v_per_hz / (2 * math.pi) * math.sin(d48)     # peak phase V per electrical rad/s


def run(p, target, seconds, sample_ms=2.0, start_state=None, trace=None):
    ke = ke_of(p)
    kt = 1.5 * p['pp'] * ke
    thf = 0.0                        # field angle, counts (angle_)
    thr = -0.0                       # rotor electrical angle, counts
    w = 0.0                          # rotor electrical speed, counts/s
    duty = float(p['duty_min'])
    acc = 0.0                        # ffpi integrator
    drv = 0.0                        # drv_incr, in 2**32 units
    ramp = p['ramp_min']
    state = 'UP'
    last_edge_t, sect_period, last_sector = 0.0, None, 0
    t = 0.0
    n_frames = int(seconds / FRAME)
    every = int(sample_ms / 1000 / FRAME)
    out = []
    e_meas = 0
    for f in range(n_frames):
        # ---- drive pass
        if f % PASS == 0:
            lag = e_meas
            if state == 'UP':
                if drv >= target:
                    state = 'AT'
                elif lag < p['lag_soft']:
                    step = min(ramp, target - drv)
                    drv += step
                    ramp = min(ramp + p['ramp_inc'], p['ramp_max'])
            if lag < p['lag_hold']:
                thf += drv / 2**32 * 256
        # ---- rotor estimate as the driver sees it
        sector = math.floor(thr / SECTOR)
        if sector != last_sector:
            if sect_period is None and last_edge_t == 0.0:
                sect_period = None
            else:
                sect_period = t - last_edge_t
            last_edge_t = t
            last_sector = sector
        hall_angle = sector * SECTOR + SECTOR / 2
        if p['interp'] and sect_period:
            frac = min((t - last_edge_t) / sect_period, 1.0)
            est = sector * SECTOR + frac * SECTOR
        else:
            est = hall_angle
        e_true = thf - thr
        e_meas = int(round(thf - est))
        # ---- physics
        delta = math.radians(90.0 + (e_true - p['e90']) * 360 / 256)
        Va = duty / p['duty_max'] * p['Vbus'] / 2
        we = w * 2 * math.pi / 256
        iq = (Va * math.sin(delta) - ke * we) / p['R']
        idd = Va * math.cos(delta) / p['R']
        T = kt * iq
        wm = we / p['pp']
        loss = p['Bv'] * wm + (p['Tc'] if wm > 1e-3 else (min(p['Tc'], abs(T)) * (1 if T > 0 else -1) if abs(T) < p['Tc'] else p['Tc']))
        if wm <= 1e-3 and abs(T) <= p['Tc']:
            alpha = 0.0
            w = max(w, 0.0)
        else:
            alpha = (T - loss) / p['J']
        wm += alpha * FRAME
        w = wm * p['pp'] * 256 / (2 * math.pi)
        thr += w * FRAME
        # ---- servo
        if p['mode'] == 'shipped':
            x = abs(e_meas) - p['sp']
            g = p['up'] if x >= 0 else p['dn']
            duty += (x * g) >> p['shift']
        elif p['mode'] == 'frac':
            # the same integral servo with the band and the asymmetry removed: symmetric gain ki,
            # fractional accumulation (no truncation), about the same setpoint the shipped one holds
            duty += p['ki'] * (e_meas - p['e90'] + 8)
        elif p['mode'] == 'fftrim':
            # feedforward from the field's speed; the SHIPPED servo, unchanged, as the trim
            x = abs(e_meas) - p['sp']
            g = p['up'] if x >= 0 else p['dn']
            acc += (x * g) >> p['shift']
            ff = p['kff'] * abs(drv) / 1e6
            duty = ff + acc
        else:
            # ffpi: feedforward + PI trim about the mean the shipped servo holds (48)
            ff = p['kff'] * abs(drv) / 1e6
            err = e_meas - 48
            # ksched: integral gain proportional to duty (the stiffness the rotor has), ki at duty 8192
            kgain = p['ki'] * (duty / 8192.0 if p['ksched'] else 1.0)
            acc += kgain * err
            duty = ff + p['kp'] * err + acc
        clamped = max(p['duty_min'], min(p['duty_max'], duty))
        if p['mode'] in ('fftrim', 'ffpi') and clamped != duty:
            acc += clamped - duty                  # anti-windup: the trim never holds what the clamp refused
        duty = clamped
        # DC-link current, a proxy: power / Vbus, in sense mV (150 mV/A)
        if f % every == 0:
            ph = math.hypot(iq, idd)
            idc = 1.5 * Va * (iq * math.sin(delta) + idd * math.cos(delta)) / p['Vbus']
            out.append((t, f // every, int(thr // SECTOR), e_meas, int(duty), idc * 150 / 10, drv, ph))
        t += FRAME
    return out


def parse(argv):
    p = dict(P)
    for a in argv:
        k, v = a.split('=')
        p[k] = type(P[k])(v) if not isinstance(P[k], str) else v
    return p


if __name__ == '__main__':
    scen = sys.argv[1]
    p = parse(sys.argv[2:])
    if scen == 'start':
        rows = run(p, 36_750_000, 1.3)
        for (t, k, pos, e, d, i, drv, ph) in rows:
            if k % 5 == 0 or k > 230 and k % 2 == 0:
                print(f"{k:4} pos {pos:4} i {i:6.1f} d {d:6} e {e:5}  drv {drv/1e6:6.2f}e6")
    elif scen == 'ladder':
        for inc in (5e6, 10e6, 20e6, 40e6, 60e6, 80e6, 100e6, 120e6):
            rows = run(p, inc, 4.0)
            tail = rows[len(rows) // 2:]
            d = [r[4] for r in tail]; e = [r[3] for r in tail]; i = [r[5] for r in tail]
            print(f"{inc/1e6:6.0f}e6  duty mean {sum(d)/len(d):7.0f} pk {max(d):6}  e mean {sum(e)/len(e):5.1f} pk {max(e):4}"
                  f"  i mean {sum(i)/len(i):6.1f} pk {max(i):6.1f}")
