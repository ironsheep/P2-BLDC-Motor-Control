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
         )

PATH_RELEASE_SLOTS, PATH_RELEASE_STEP, PATH_BEHIND = 4, 20, 100
SHORT_SLOTS = 4


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

    def permille(w):
        return min(abs(w.drv.v) * 1000 // abs(w.cmd), 1000) if w.cmd else 1000


def run(p, target, seconds, pairs, win, sample_ms=2.0, trace=None, t0_override=None):
    ke = ke_from_ladder(p); kt = 1.5 * p['pp'] * ke
    W = [Wheel(p, p['RL'], *pairs, target), Wheel(p, p['RR'], *pairs, -target if p['straight'] else target)]
    rr = p['r'] ** 2
    a = p['Jw'] + p['m'] * rr / 4 + p['Iz'] * rr / p['track'] ** 2
    b = p['m'] * rr / 4 - p['Iz'] * rr / p['track'] ** 2
    det = a * a - b * b
    scale = 1000; clean = 0; engages = 0; scale_min = 1000
    n = int(seconds / FRAME)
    every = int(sample_ms / 1000 / FRAME)
    slot = int(p['slot_ms'] * 44)
    samples = []
    rnd = 12345 + 7919 * (int(p['seed']) - 1)          # seed=1 (the default) is the sequence every earlier run used
    noise = [0.0, 0.0]
    # the obstacle and the protective stop (obst=1)
    if p['obst']:
        for i, w in enumerate(W):
            w.anchor = p['ob_x'] + (p['ob_dx'] if i == 1 else 0.0)
            w.contact_t = None; w.last_tick_t = 0.0; w.blk_pos = 0; w.blk_n = 0; w.F = 0.0
            w.err_pk = 0; w.ticks_fwd = 0; w.ticks_back = 0; w.tick_sector = 0; w.blk_best = 0
            w.blk_cap = 0                 # D-5 (blk_lim): the limiter counts as the previous front pass read them
        blk = dict(latch_t=None, wheel=None, stand=None, fault_t=None, fault_wheel=None)
    for f in range(n):
        t = f * FRAME
        # ---- the front cog's protective stop, once per 1 ms front pass (bFrontProtect() :2898-2904)
        if p['obst'] and f % 44 == 0:
            for i, w in enumerate(W):
                pos = math.floor(w.thr / SECTOR)
                lim_f = w.capped != w.blk_cap        # D-5 (blk_lim): a limiter acted since the previous front pass
                w.blk_cap = w.capped
                if w.tgt != 0 and (abs(w.e) >= p['lag_soft'] or (p['blk_lim'] and lim_f)) and pos == w.blk_pos \
                        and w.drv.state in ('SPIN_UP', 'AT_SPEED', 'SPIN_DN'):
                    w.blk_n += 1
                else:
                    w.blk_n = 0
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
                    w.e90 = p['e90_L18'] + (l_eff(w.L, w.Z, w.sign) - 18) * 256 / 360
                if w.drv.held != w.last_held:
                    w.hold_slots_ago = 0
                elif w.hold_slots_ago < SHORT_SLOTS:
                    w.hold_slots_ago += 1
                w.last_held = w.drv.held
            sh = [w.hold_slots_ago < SHORT_SLOTS for w in W]
            pm = [w.permille() for w in W]
            behind = [sh[0] and (pm[1] - pm[0] > PATH_BEHIND), sh[1] and (pm[0] - pm[1] > PATH_BEHIND)]
            if behind[0] or behind[1]:
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
                at_rest = w.drv.jerk_step(w.tgt, w.e)
                if not at_rest:
                    # D-5 (d5): while a limiter has the duty, in the states holdDecay walks, the hold is lag_lim
                    dir_ = -1 if w.drv.v < 0 else 1
                    if w.lim_sector is not None and (math.floor(w.thr / SECTOR) - w.lim_sector) * dir_ > 0:
                        w.lim_sector = None       # C4: the rotor ticked forward past the armed sector
                    lim_hold = p['d5'] and (w.capped != w.capped_seen or w.lim_sector is not None) \
                        and w.drv.state in ('SPIN_UP', 'AT_SPEED')
                    hold_at = p['lag_lim'] if lim_hold else p['lag_hold']
                    if lag_s < hold_at:
                        w.thf += w.drv.v / TWO32 * 256
                    else:
                        if lim_hold and p['d5_back'] and lag_s > p['lag_lim']:
                            # the set-back: angle_ -= sign(drv_incr) * (lag_s - lag_lim) << 24, so err reads lag_lim
                            back = lag_s - p['lag_lim']
                            if p['d5_step'] > 0:
                                back = min(back, p['d5_step'])
                            w.thf -= back * dir_
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
                w.ff = min(abs(w.drv.v) * p['duty_ff_line'] // p['ff_incr'], p['duty_max'])
                if w.drv.state == 'AT_SPEED' and w.t_arrive is None:
                    w.t_arrive = t
            sgn = w.sign
            e_true = (w.thf - w.thr) * sgn
            delta = math.radians(90 + (e_true - w.e90) * 360 / 256) * sgn
            Va = p['Vbus'] * w.duty / (16 * 3068)
            we = w.wm * p['pp']
            Vd = Va * math.cos(delta); Vq = Va * math.sin(delta)
            Lh = p['Lh']; R = w.R
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
            w.e = math.floor(w.thf - (sector + 0.5) * SECTOR)
            if p['wrap']:
                w.e = ((w.e + 128) % 256) - 128        # err_ is a wrapped 8-bit angle (:7926-7930)
            if abs(w.e) >= p['fault']:
                w.faulted = True
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
            if math.hypot(w.idd, w.iq) > p['i_limit']:
                w.duty -= w.duty >> 6
                w.duty = max(w.duty, p['duty_min'])
                w.acc = (w.duty - w.ff - w.pterm) << p['acc_shift']
                w.capped += 1                      # D-C: the limit acted (foldback_cnt advanced)
                continue
            # ---- the trim (DRIVER_REV 46), plus the proposed proportional term
            x = abs(w.e) - p['setpoint']
            w.acc += x * (w.duty >> p['preshift'])
            if p['dB']:
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
            d2 = max(p['duty_min'], min(p['duty_max'], want))
            if d2 != want:
                w.acc = (d2 - w.ff - pterm) << p['acc_shift']
                if d2 < want:
                    w.capped += 1
            w.duty = d2
        if p['obst'] and any(w.faulted for w in W):
            k_ = [w.faulted for w in W].index(True)
            blk.update(fault_t=t, fault_wheel=('L', 'R')[k_])
            break
        if f % every == 0:
            samples.append((t, [(w.duty, w.e * w.sign, max(w.pin, 0) / p['Vbus'], w.thr * w.sign / SECTOR,
                                 w.drv.v, w.drv.held, w.drv.state, math.hypot(w.idd, w.iq), w.capped) for w in W], scale))
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
                              setbacks=w.setbacks)
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
    lat = []; stands = []; nolatch = 0; faults = 0; back = 0; best = 0
    for j in range(int(q['ob_n'])):
        qj = dict(q); qj['ob_x'] = q['ob_x'] + sector_m * j / q['ob_n']
        b = run(qj, SLOW, q['ob_t'], ('SCHED', None, -4), 0.5)['block']
        cs = [x['contact'] for x in b['wheels'] if x['contact'] is not None]
        c0 = min(cs) if cs else None
        back += sum(x['back'] for x in b['wheels'])
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
    lat.sort(); stands.sort()
    s = f"latched {len(lat)} of {int(q['ob_n'])}, no latch {nolatch}, fault {faults}; contact-to-latch ms "
    s += (f"min {1000 * lat[0]:.0f} median {1000 * lat[len(lat) // 2]:.0f} max {1000 * lat[-1]:.0f}; "
          f"stand ms {1000 * stands[0]:.0f}-{1000 * stands[-1]:.0f}" if lat else 'none')
    s += f"; back ticks {back}" + (f"; longest count without latch {best}" if nolatch else '')
    return 'SUMMARY: ' + s


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
             if p['d5'] else '') + (f"  blk_lim {p['blk_lim']}" if p['blk_lim'] else ''))
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
