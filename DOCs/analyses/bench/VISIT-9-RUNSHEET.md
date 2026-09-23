# Visit 9 — run sheet (the limits reset: top speed, duty headroom, ramps, the low-speed floor)

**Task:** «#3605» runs it; «#3604» built it. **Plan:** [`LIMITS-RESET-PLAN.md`](../../plans/LIMITS-RESET-PLAN.md)
§2 E1–E4. **Why this visit:** Visit 8b ([evaluation](2026-09-22/VISIT-8B-EVALUATION.md) §3.5) freed the top of the
range. Every limit below was set by the old drive, and none has been measured on the new one. Each reading here
feeds one constant that «#3605» moves.

---

## Check the banner before reading anything else

| Load | Every `BM-BANNER` / `BM-BUILD` / record must read |
|---|---|
| both | `src_rev,32` · `fmt,18` · `drv_rev,6` · part `LIM` · `BM-CLIPTEST ... judge_ok,TRUE` |
| `dual-limits` | every `BM-CLIP` reads `duty_max,24_264`; segments `LIMTOP`, `LIMRAMP`, `LIMLOW` |
| `dual-limits-svm` | every `BM-CLIP` reads `duty_max,27_648`; segment `LIMTOP` only |

A `duty_max` that does not match its tier means `-D DUTY_MAX_SVM` did not reach the motor object: stop and report.

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Measurement** of four limits the old drive set: the unloaded top speed (E1), the top on the raised duty ceiling (E2), the fastest clean ramps (E3), the lowest speed that turns steadily (E4). Plus **one certification**: the raised ceiling never clips the PWM (`R18-DUAL-PWMCLIP-M`). |
| **Hardware risk** | **The wheels run faster than on any visit before.** Each wheel climbs past 147 × 10⁶ in 10 × 10⁶ steps until it stops keeping up. The command is capped at 245 × 10⁶, about 440 rpm, and the old drive faulted near 277 rpm. At the edge a wheel may **fault on purpose**; it is recovered in-run, and two faults in a row end that climb. On the SVM build the PWM amplitude is 14 % larger. By the desk bound it stays 1–2 counts inside both rails at every angle, and the dead-gap is unchanged. The ramps at 2× and 4× today's are the ones that faulted on gravel in 2022; wheels up they meet no load. The 10 A abort and the fold-back limiter apply throughout. **Wheels up, no hands near the rig. Panic: physical battery disconnect.** |
| **Who can observe** | Nobody needs to. **Two observations are worth having if you are near.** During the climb, does a wheel sound rough, or change its note, at the highest speeds? During the last few minutes of `dual-limits`, do the slowest speeds turn smoothly or visibly step? Observations, not verdicts. |
| **Runs that carry state** | None. Ramps and `duty_min` are restored and read back inside the run (`BM-RAMPREST`, `BM-LOWDUTY`). `DUTY_MAX_SVM` is compiled in, not written to the board. |
| **Run length** | **About 23 minutes (ESTIMATED from `BM-PLAN`):** `dual-limits` about 17 (LIMTOP ~6, LIMRAMP ~5, LIMLOW ~6), `dual-limits-svm` about 6. |
| **Repeatability** | Both repeatable and idempotent. |
| **Variant matrix** | One source, two builds of `test_bench_dual.spin2` part LIMITS: default and `-D DUTY_MAX_SVM`. Same rig as Visit 8b: Rev B, the paired 6.5in hubs, 18.5 V, 270 MHz. Two logs. |

**New information, and what is carried.** Every load is new. No rung above 165 × 10⁶, no `ramp_inc` above 22 on
this drive, no `ramp_down` above 50,000 and no speed below 1 × 10⁶ has ever been run. LIMTOP's base rungs re-run
the ladder's twelve speeds on purpose. They are E2's comparison: the same speeds on both builds, one run apart.

---

## The commands

```bash
tools/bench-run.sh dual-limits       # 1: E1 top speed, E3 ramps, E4 floor, on today's duty ceiling
tools/bench-run.sh dual-limits-svm   # 2: E2 -- the top-speed climb again on the raised duty ceiling
```

Order matters only for reading: run 1 is the baseline run 2 is compared with.

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). Cells print their own verdict. The rest are judged in the
report from the named records.

| Id | Judged by | Criterion | Fails if | Negative case |
|---|---|---|---|---|
| **E1 top** | `BM-TOPSPD`, per motor × sign, run 1 | report `top`, `unsat` and `edge` / `edge_why` | — (a measurement) | — |
| **`R18-DUAL-TOPSPD-M`** | cell, per motor | the worse sign's `top` ≥ 147 × 10⁶ | the new drive tops out below today's published ceiling | **A regression guard, not a certification.** No drive on file fails it: the shipped and the R18.4 drive both follow to 165 × 10⁶ (`debug_260922-122752.log`, `-161317.log`). Its limb is the arithmetic in `limTopSign()`, not a run. |
| **E2 gain** | `BM-TOPSPD`, run 2 against run 1 | `unsat` rises on both motors. Predicted: by up to the 14 % the duty ceiling rose, since `unsat` is where duty first caps | the extra amplitude does not reach the motor | run 1 is the control: the same climb on the old ceiling |
| **E2 no side effect** | `BM-RUNG2` net current, LIMTOP rungs 3–8, run 2 against run 1 | within ±10 % or ±5 mV (the larger) at every rung | the bias move or the feedforward's rescale changed the drive below the ceiling | a feedforward that moved with `duty_max` (PL-107's trap) would raise duty and current by ~14 % at every rung |
| **`R18-DUAL-PWMCLIP-M`** | cell, per motor, both runs | least room to a rail over every LIMTOP rung ≥ 0 counts | any stored PWM level outside `0 .. F` (dead-gap included) | **The judge:** `BM-CLIPTEST`, on synthetic levels one count past each rail, must read negative (`judge_ok`). Without it the cell prints NOMEAS. **The sampling:** at full duty the desk room is 1–2 counts on the SVM build and ~150 on the default. Run 2 must read within ~20 counts of its desk figure. A reading far above it means the instrument is not reaching the peaks, and the PASS certifies nothing. |
| **E3 starts** | `start_metrics.py` on the LIMRAMP START traces; `BM-RAMP` | per `ramp_inc`: drop ≤ 0.10, peak ratio ≤ 1.8, `followed,TRUE`; report `ramp_ms` | a faster ramp brings back the surge, or outruns the rotor | `ramp_inc` 22 is the control, already measured at Visit 8b (drop 0.01–0.02, ratio 1.24–1.33) |
| **E3 speed-downs** | the SLOWER traces; `BM-RAMP` | per `ramp_down`: peak current ÷ the settled quarter's mean ≤ 1.8, `followed,TRUE`; report `ramp_ms` | the faster fall draws a surge, or lags | `ramp_down` 50,000 is the control |
| **E3 new value** | the two above | the fastest setting passing all of its criteria on both motors and signs | — | — |
| **E4 rotates** | `BM-LOW` `edges`, `BM-RUNG` `ticks` | at least half the expected edges in the window (expected: 11, 8, 5, 2 at 544,628 / 400,000 / 250,000 / 100,000) | the rung does not turn | today's floor, 544,628, is the control; its source says "anything below yields NO rotation" |
| **E4 steady** | `BM-LOW` `gap_max` | ≤ 2× the expected gap (687, 935, 1,497, 3,743 ms) | the rotor steps, catching at each commutation | the same rung with `duty_min` halved: if the steps come from the duty floor, halving it changes them |
| **E4 new floor** | the two above | the lowest increment that rotates steadily, with `duty_min` as built; the halved run says whether `duty_min` is the reason | — | — |
| `R14-DUAL-TRACES-M` | cell, run 1 | no LIMRAMP trace lost samples | a trace lost its head or dropped samples | the same cell's existing negative cases in parts A–C. **NOMEAS on run 2 by design**: that build takes no trace |
| `R18-DUAL-NOSTALL-M`, `-DBGMASK-M` | cells, both runs | as every part | as every part | as every part |

**What this visit cannot measure, named:** any margin under load. Every number here is a ceiling; the published
top speed and acceleration are these reduced by what the floor run (E5, «#3591» / «#3576») shows.
