"""Desk check of the DUTY_MAX_SVM bound (task 3604, LIMITS-RESET-PLAN.md E2).

Emulates the driver's per-frame level computation (isp_bldc_motor.spin2, the three QROTATEs, the
(min+max) sar 1 centring, + bias, + dead_gap on the low side) over every angle, at each bench clock,
with the CORDIC's Y perturbed by -1/0/+1, and reports the worst headroom to each rail for the legacy
and the SVM constants. Headroom < 0 means the PWM clips.
"""
import math, itertools

def consts(clk, svm):
    ticks1us = clk // 1_000_000
    frame_cnt = (ticks1us * (1_000_000_000 // 44_000)) // 1_000
    F = frame_cnt // 2
    dg = (ticks1us * 260) // 1_000
    pwm_limit = F - dg // 2
    if svm:
        bias = (F - dg) // 2
        amp = ((F - dg - 4) * 577_350) // 1_000_000
    else:
        bias = frame_cnt // 4
        amp = ((pwm_limit << 4) // 2) >> 4
    return F, dg, bias, amp

def worst(clk, svm, steps=36_000):
    F, dg, bias, amp = consts(clk, svm)
    lo_room, hi_room = 10**9, 10**9
    for k in range(steps):
        th = 2 * math.pi * k / steps
        base = [amp * math.sin(th + n * 2 * math.pi / 3) for n in range(3)]
        for e in itertools.product((-1, 0, 1), repeat=3):
            v = [int(math.floor(b + 0.5)) + d for b, d in zip(base, e)]
            c = (min(v) + max(v)) >> 1
            hs = [x - c + bias for x in v]
            lo_room = min(lo_room, min(hs))                  # high side Y >= 0
            hi_room = min(hi_room, F - (max(hs) + dg))       # low side Y = hs + dg <= F
    return F, dg, bias, amp, lo_room, hi_room

for clk in (200_000_000, 270_000_000, 300_000_000):
    for svm in (False, True):
        F, dg, bias, amp, lo, hi = worst(clk, svm)
        print(f"clk {clk//1_000_000:3} MHz {'SVM   ' if svm else 'legacy'} F {F} dg {dg} bias {bias} "
              f"amp {amp} duty_max {amp << 4}  room to 0: {lo}  room to F: {hi}  "
              f"{'OK' if min(lo, hi) >= 0 else 'CLIPS'}")
