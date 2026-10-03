# The 6.5″ motor manual — where each section's numbers come from

The user-facing manual, [`MOTOR-6.5IN-TECHNICAL-MANUAL.md`](../../MOTOR-6.5IN-TECHNICAL-MANUAL.md) in the
repo root, says only whether a number was measured on our hardware, calculated, or taken from vendor data.
This file carries the citations behind it, so the manual can stay readable for someone who knows nothing of
our bench work (doctrine overlay P8: *the traceability is not lost, it is relocated*).

**When a bench pass changes a number in the manual, add its source here in the same change.**

The version of the manual with every citation inline, as it stood before the user rewrite, is
`DOCs/MOTOR-6.5IN-TECHNICAL-MANUAL.md` at commit `8b9ea3f` (2026-09-28).

Paths are under `DOCs/analyses/bench/` unless stated.

| Manual section | Source |
|---|---|
| §2.1 hall sequence | `deltas65` in `src/isp_bldc_motor.spin2`; +50 power raised `pos` (PL-39) |
| §2.2 30 poles / 90 ticks | `2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §2, `debug_260915-142347.log` (T0-12, 270 transitions over 3 revolutions) |
| §2.3 hall health | `2026-09-21/VISIT-7B-EVALUATION.md` F10; `VISIT-10-PASS2-EVALUATION.md` §3.2; `VISIT-10-PASS4-EVALUATION.md` §2 |
| §2.4 winding resistance | `2026-09-26/pass7/VISIT-10-PASS7-EVALUATION.md` §3 (calibrated pack V); `VISIT-10-PASS4-EVALUATION.md` §5 (nominal V, 12 % low) |
| §2.4 inductance bound | `VISIT-10-DUALFAULT-T0-EVALUATION.md` §3 |
| §2.4 sector widths | `2026-09-22/VISIT-7C-PASS2-EVALUATION.md` §3.5 |
| §3.1 board facts | `DOCs/analyses/BOARD-REVISION-FACTS.md` |
| §3.1 shunt blind to a phase short | vendor placement; `VISIT-10-PASS2-EVALUATION.md` §3.3; PL-118 |
| §3.2 servo holds a point | `VISIT-8-EVALUATION.md` §3.2 |
| §3.2 clip-free duty ceiling | `VISIT-9-EVALUATION.md` §2.3 |
| §3.4 designer's principles | `DOCs/analyses/BLDC-COMMUTATION-PRINCIPLES.md` |
| §4.2 Z by current minima | `2026-09-22/VISIT-7C-EVALUATION.md` §6 |
| §4.2 Z cold, by back-EMF | `2026-09-22/VISIT-7C-PASS2-EVALUATION.md` §3.3 |
| §4.6 back-EMF while coasting from speed | `VISIT-10-PASS2-EVALUATION.md` §3.3; `VISIT-10-PASS5-EVALUATION.md` §2 (COASTEMF) |
| §4.7 unit-to-unit, hall lag | `2026-09-22/VISIT-7C-PASS2-EVALUATION.md` |
| §5.2 lead table | `VISIT-8-EVALUATION.md` §3.5; `VISIT-8B-EVALUATION.md` §3.6 |
| §5.3 the basin | offset sweep, LEFT, negative increment: `2026-09-14/SCAN-RUN-7-EVALUATION.md`, `2026-09-14/VISIT-1-RESULTS.md` (also quoted in `VISIT-7B-EVALUATION.md`) |
| §6.1 ceiling 165 × 10⁶ | `VISIT-9-EVALUATION.md` §6a; `VISIT-9B-EVALUATION.md` §3 |
| §6.1 floor 100,000 | `VISIT-9-EVALUATION.md` §4 |
| §6.2 the two walls | `VISIT-8-EVALUATION.md` §3.5; `VISIT-8B-EVALUATION.md` §3.6 |
| §6.3 duty knee, field weakening | `VISIT-9-EVALUATION.md` §2, §2.1–2.2 |
| §6.3 RIGHT forward slip | `VISIT-9B-EVALUATION.md` §2 |
| §6.3 alignment moves the knee | `VISIT-8B-EVALUATION.md` §3.5 |
| §6.4 quiet start | `VISIT-8-EVALUATION.md` §3.1; `VISIT-8B-EVALUATION.md` §3.2 |
| §6.4 faster ramps | `VISIT-9-EVALUATION.md` §3 |
| §6.5 coast vs short | `VISIT-10-PASS2-EVALUATION.md` §3.3; `VISIT-10-DUALFAULT-T0-EVALUATION.md` §3; `VISIT-10-PASS4-EVALUATION.md` §3; RIGHT at pass 5 |
| §6.5 graded short | `VISIT-10-DUALFAULT-T0-EVALUATION.md` §3; pass 4; RIGHT at pass 5 |
| §6.5 re-synced stop after a fault | `VISIT-10-PASS2-EVALUATION.md` §3.3; `VISIT-10-PASS5-EVALUATION.md` §2 |
| §6.5 stop on the jerk-limited ramp | `2026-09-27/rc/VISIT-10-RC-EVALUATION.md` (T0-25 plan leg 0: 2,117 passes, 1,106 ms, 122 ticks vs 120) |
| §6.5 stop states at rest | `VISIT-10-PASS3-T0-DUALSTART-EVALUATION.md` §3; `VISIT-10-DUALFAULT-T0-EVALUATION.md` §5 |
| §6.5 hold | `VISIT-10-PASS3-T0-DUALSTART-EVALUATION.md`; `VISIT-10-DUALFAULT-T0-EVALUATION.md` |
| §6.5 blocked-rotor stop | `VISIT-10-DUALFAULT-T0-EVALUATION.md` §4 |
| §6.5 on the floor: distance stops within 3 ticks | `2026-09-30/floor/FLOOR-VISIT-EVALUATION.md` §6 (SPINSTOP 10 of 10); `2026-09-30/floor2/FLOOR-RERUN-EVALUATION.md` §2.1 (210–214 of 211), §2.2 (`l_trav,173`) |
| §6.5 on the floor: partner stop, heading under 2° | `floor2/FLOOR-RERUN-EVALUATION.md` §2.2 (SPINPLAT 0 %; fence heading −8.5° → −10.2°) |
| §6.5 on the floor: current after a fault 0.72–0.95× | `floor2/FLOOR-RERUN-EVALUATION.md` §2.2 (POSTFLT 95 / 72) |
| §6.5 on the floor: blocked-rotor latch 1.0–1.1 s; the rocking obstacle (6 s, no latch) and the fault after ~4 s | `floor/FLOOR-VISIT-EVALUATION.md` §3 (short trial `l_stand,1_143`; coast trial FC_LAG at ~4.3 s); `floor2/FLOOR-RERUN-EVALUATION.md` §4 (brake `r_stand,1_097`; coast NO_LATCH after ~6 s) |
| §6.5 on the floor: one-sided load 49 % / 47 %, line within 3 % | `floor2/FLOOR-RERUN-EVALUATION.md` §3 (LDPATH `mis_pm,30`, `l_pct,49,r_pct,47`, LDHOLD 276 ms) |
| §6.5 on the floor: stop from 2.3 m/s; duty 96 % at full speed; pack sag | `floor2/FLOOR-RERUN-EVALUATION.md` §5 (FlySky RC-TEL: 1.2 s / 1.38 m at 2,087; duty 26,476 of 27,648; pack 20,397 → 20,085 mV) |
| §7.5 ramps on the floor: felt smooth, no clicking or unusual sound | `floor/FLOOR-VISIT-EVALUATION.md` header (Stephen's report of the FlySky run, 2026-09-30); `floor2/FLOOR-RERUN-EVALUATION.md` §5 |
| (superseded by the 6.1.0 rows below) the 6.0.0 reading of the lead table under load, 57–94 % of command; the manual no longer states it | `floor2/FLOOR-RERUN-EVALUATION.md` §2.1 (the ten spin legs' `fol_pct`, `path_pm`, `err_pk`) |
| §3.2 duty trim (shift 16, `SERVO_ACC_SHIFT`), fast slope past `LAG_SOFT`, `LAG_LIM` | `src/isp_bldc_motor.spin2` constants; `DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md` §4 (D-1, D-2), §4.9 (D-5) |
| §6.1 the figures labelled 18.5 V were taken on a pack of about 20.5–20.7 V; 102–104 % of the duty ceiling at 18.5 V | pack: `2026-09-26/pass7/VISIT-10-PASS7-EVALUATION.md` §3 (20.72 V), `2026-10-02/VISIT-6.1.0-EVALUATION.md` (`floor-rc` pack 20,588 mV), `2026-10-02b/VISIT-6.1.0B-EVALUATION.md` (20.2 V); 102–104 % is derived: 92–93 % (`VISIT-9-EVALUATION.md` §6a) × 20.5–20.7 ÷ 18.5 |
| §6.3 smooth to 245 × 10⁶, mean `err` 49 → 61, about 0.5 → 3.6 A of pack current (the 6.0.0 slip at 235–245 is no longer stated) | `2026-10-02c/VISIT-6.1.0C-EVALUATION.md` §1, §2 (LEFT reverse: `BM-RUNG2` / `BM-RUNGHL`, `i_max` 74 → 536 sense mV; TOPSPD 245 on all four wheel-directions; `win_lag,0` on every rung) |
| §6.4 lowest speeds: swing about 30–100, `err` peaks 70–77 | `2026-10-02/VISIT-6.1.0-EVALUATION.md` §2.2 (swing 31–99, `err_pk` 70–75); `2026-10-02b/VISIT-6.1.0B-EVALUATION.md` §2.1 (one window 77) |
| §6.5 on the floor, 6.1.0: spins 100–107 %, ramp legs within 1 % | `2026-10-02/VISIT-6.1.0-EVALUATION.md` §3.1 (SPINRATE, RAMPARR); repeated in `2026-10-02b/…B-EVALUATION.md` §3.1 and `2026-10-02c/…C-EVALUATION.md` §3.2 |
| §6.5 on the floor, 6.1.0: a hand's load, left 31 % / right 70 % | `2026-10-02c/VISIT-6.1.0C-EVALUATION.md` §3.3 (`BM-LOADW l_pct,31,r_pct,70,path_min,733`; LDFLT PASS). A hand cannot slow it at 4 A: `2026-10-02/…-EVALUATION.md` §3.3 |
| §6.5 on the floor, 6.1.0: after a fault 0.79 / 1.41 | `2026-10-02/VISIT-6.1.0-EVALUATION.md` §3.1 (POSTFLT PASS, 1.41 / 0.79) |
| §6.5 and §7.2 blocked-rotor stop, 6.1.0: latched about 1.0 s after the wheel stopped, coast and brake, 2 A test limit, no fault; not measured against a yielding object | `2026-10-02c/VISIT-6.1.0C-EVALUATION.md` §3.1 (stand 1,017 / 1,028 ms, count 997 / 1,003; BLKFLT, BLKCOAST, BLKSHORT, PROTCLR PASS); `2026-10-02b/…B-EVALUATION.md` §3.2 |
| §7.2 the hold at the current limit, largest lag 107 after one tick pushed back; the release cap; field ends an over-command at 9–20 % | `2026-10-02c/VISIT-6.1.0C-EVALUATION.md` §3.1 (`l_emax` 107), §2 (`BM-FOLLOW kind,OVER permille` 88–199; OVRSTEP PASS); design §4.11, §4.12 |
| §7.5 slow-down excess 24 / 30 mV, speed-ups under 10 mV | `2026-10-02b/VISIT-6.1.0B-EVALUATION.md` §2.1 (TRKICK-A 24 / 30 mV); `2026-10-02/…-EVALUATION.md` §2.2 (speed-ups `tr_i_over` ≤ 9) |
| §6.5 on the floor, 6.1.0: one spin stop of twenty within 4 hall ticks | `2026-10-02c/VISIT-6.1.0C-EVALUATION.md` §3.2 (SPINSTOP FAIL 1: leg 3 RIGHT `r_trk` 216 against 212, tolerance 3); PL-192 |
| §7.5 a speed raised while a wheel is still slowing dips about 0.3 s | `2026-10-02b/VISIT-6.1.0B-EVALUATION.md` §3.4 (LEFT field 6.8 × 10⁶, 12 % of target, about 300 ms) |
| §9 full power on an 18.5 V pack not run; blocked stop against a yielding object not measured | `2026-10-02c/VISIT-6.1.0C-EVALUATION.md` §7, §8; `2026-10-02/…-EVALUATION.md` §7 |
| §6.6 start checks | `VISIT-10-PASS2-EVALUATION.md` §3.1–3.2; `VISIT-10-PASS3-T0-DUALSTART-EVALUATION.md` §2; `VISIT-10-PASS4-EVALUATION.md` §5–6; `VISIT-10-PASS5-EVALUATION.md` §5; rest-zero band: comment at `REST_ZERO_MIN_MV` |
| §6.6 walk guard, 26 A unguarded | `VISIT-10-PASS2-EVALUATION.md`; `VISIT-10-PASS3-RERUN-EVALUATION.md`; fix certified pass 6 |
| §7.2 protection limits | `src/isp_bldc_motor.spin2` constants; `BOARD-REVISION-FACTS.md` |
| §7.3 alignment A/B | `VISIT-7B-EVALUATION.md` §3 |
| §7.3 lead table saving, symmetry | `VISIT-8B-EVALUATION.md` §3.3; `VISIT-9-EVALUATION.md` §2.3 |
| §7.5 kicks | `VISIT-7B-EVALUATION.md`; `VISIT-8B-EVALUATION.md` §3.7; pass 7 R21-DUAL-TRKICK-T |
| §7.5 jerk-limited ramp | `2026-09-27/rc/VISIT-10-RC-EVALUATION.md`; `2026-09-28/blockA/BLOCK-A-EVALUATION.md` |
| §9 pack sensor | `VOLTAGE-SENSOR.md`; «#3611» |
| §9 back-EMF while driven | «#3602» (after 6.0.0) |
| (removed from the user manual) the RIGHT unit's intermittent loss of drive | PL-120; `VISIT-10-PASS1…PASS7` evaluations — evidence points at the right board, not the motor |
