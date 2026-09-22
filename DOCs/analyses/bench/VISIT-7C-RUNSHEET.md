# Visit 7c — run sheet, pass 2 (two loads; the first needs your hands on the wheels)

**Plan section:** R18.2f ([`../../plans/BENCH-READINESS-SPRINT-PLAN.md`](../../plans/BENCH-READINESS-SPRINT-PLAN.md)).
**Task:** «#3594».

**Pass 1 — done.** 2026-09-21/22, `scan-droop` + `scan` + `dual-a`. Judged in
[`2026-09-22/VISIT-7C-EVALUATION.md`](2026-09-22/VISIT-7C-EVALUATION.md): the start-transient
mechanism is answered (the servo's 60° deadband, 4 of 4 traces).

---

## Check the banner before reading anything else

| Load | Banner must read |
|---|---|
| `dual-align` | `BM-BANNER` `src_rev 25`, `fmt 13`, part `ALIGN` |
| `dual-a` | `BM-BANNER` `src_rev 25`, `fmt 13`, part `A`; **`BM-BUILD` `servo_engage,57`** |

⛔ `src_rev` below 24 means the hysteresis and the band test are **not** in the image: the ALIGN run
repeats the 2026-09-21 shakedown and measures nothing. ⛔ **No `servo_engage` field** means the
driver's start seed is not in the image, and load 2 certifies nothing. Stop and rebuild either way.

---

## The visit, declared

Seven attributes, per *Shared vocabulary — the bench visit* (`~/.claude/skills-docs/SKILLS-AUTHORING.md`).

| | |
|---|---|
| **Purpose** | **Two jobs.** It **certifies** two things built since pass 1: the rebuilt ALIGN crossing detector and clip test (PL-99, PL-100), and the **driver's start seed** («#3600»: a start places the field where the duty servo engages, so there is no pinned wait and catch-up). It **measures**, cold and at zero current, two things no driven run can: the hall zero `Z` over the whole circle, and **whether the six hall sectors are equal** (manual hole H-3). It is also the first real reading of back-EMF on this rig. |
| **Hardware risk** | **Load 1: none from the drive — no motor is ever driven.** Both drivers start with the bridge set to coast (all six FETs off), and only a driven bridge can fault. MEASURED at the shakedown: worst current in the tier **15 mV** against a 150 mV band. **Load 2:** the same kind of risk as every prior `dual-a` — wheels up, nothing on the platform, no hands near it. What is new is only how a start begins: the field starts 80° ahead of the rotor at minimum duty instead of 0°, so expect a **firmer, earlier** start. The 10 A abort and the fold-back limiter are unchanged and still apply. Panic throughout: physical battery disconnect. |
| **Who can observe** | **Load 1: you turn each wheel by hand.** Load 2: nobody — hands clear, unattended. Every verdict is printed. |
| **Runs that carry state** | **None.** Nothing is written to the driver at run time; nothing needs restoring. |
| **Run length** | **About 15 minutes.** Load 1: ~3 minutes of turning (MEASURED at the shakedown: 8 legs, 64 s first edge to last; the pauses are yours). Load 2: ~12 minutes (MEASURED 2026-09-20: part A ran 693 s). |
| **Repeatability** | Both repeatable and idempotent. A leg turned the wrong way is **not** a mistake: legs are labelled by the direction they measure. |
| **Variant matrix** | Two builds of one source, `test_bench_dual.spin2`: part ALIGN and part A, both on the new driver. One rig (Rev B, paired 6.5 in hub, 18.5 V, 270 MHz). Two logs. |

---

## The command

```bash
tools/bench-run.sh dual-align     # load 1 -- ATTENDED, your hands, ~3 min of turning
tools/bench-run.sh dual-a         # load 2 -- unattended, hands clear, ~12 min
```

**What your hands do in load 1.** Eight legs: left wheel then right, each forward and reverse, each slow then
brisk. Before each leg the screen prints one line in plain words: which wheel, which way, how fast.
**Wait for that line with the wheel still.** The tier reads the resting level first and re-takes it
if the wheel is moving. Turn about 3 turns; the leg ends by itself and the output resumes.

- **Slow** is an easy steady turn. **Brisk** is as quick as you can turn smoothly. Your own pace is
  right: the rate you actually turned at is measured and printed.
- **Get up to pace promptly.** The first part of a leg, while the hand is barely moving, is where the
  signal is weakest.

---

## What it decides

| Question | Feeds |
|---|---|
| **`Z` cold**, per wheel, per direction, per speed | «#3589»; confirms or retires the driven −3.6 ± 0.4° |
| **Are the six hall sectors equal?** (H-3) | «#3589»; the RIGHT motor's residual asymmetry; any future sub-sector interpolation |
| **Back-EMF's usable range** — at what hand speed crossings become countable | «#3589»'s sensor table, the row «#3596» leaves OPEN |
| **Does the start seed remove the pinned wait?** (load 2, the START trace) | certifies «#3600» |

---

## Before the run: the cells, and that each can fail

The five `R18-DUAL-ALIGN-*` cells, unchanged in meaning except **CLIP**:

| Cell | Crit | Passes when | Fails if |
|---|---|---|---|
| `-ND` | `PEAK_I_AT_REST` | worst \|sense\| ≤ 150 mV | the bridge drove. Data on file fails it: a braked hold reads 700–940 mV |
| `-CLIP` | **`BAND_NOT_RAILED`** (was `PHASE_NOT_RAILED`) | no phase's **crossing band** (resting level ± hysteresis) touches a rail | a band sits at or below 20 mV. **Desk-checked 2026-09-22:** a phase resting at 18 mV is refused |
| `-COVER` | `LEAST_CROSSINGS` | every kept leg ≥ 20 crossings | a leg's signal never left the band |
| `-RES` | `LEAST_PER_SECTOR` | every kept sector ≥ 4 samples | a leg turned too fast to place a crossing |
| `-MTRX` | `ALL_FOUR_MEASURED` | all four wheel × direction combinations returned a clean leg | any one did not; three of four is **not** three-quarters of a `Z` |

**Why `-CLIP` changed (PL-100).** The shakedown failed all eight legs because brisk turns flattened
the **negative peaks** (15.7 % of readings) — which cannot move a crossing, since the crossing is read
at the resting level ~55 mV, well inside range. Peak railing is now printed per leg as **`rail_pm`**
(per thousand readings) and judges nothing. **Expect** `rail_pm` in the low hundreds on brisk legs.

### The report-level falsifiers — stated before the run

- **PL-99 took, or it did not.** A physical leg carries **270 crossings** (3 turns × 15 electrical
  cycles × 3 phases × 2). **The shakedown counted ~1,487**, 5.5× that, and overflowed. Each leg's
  `cross` must now sit **near 270**, with **`dropped,0`**. ⛔ `cross` far above 270, or any
  `dropped` > 0, means the hysteresis did not take. `cross` far **below** 270 on a *brisk* leg
  means the band is too wide for the signal. Either is a finding about the instrument, and no `Z` is
  read from that leg.
- **`hyst_*_mV` in `BM-AGUIDE`** is the band each phase used. It is sized from that phase's own
  resting noise plus 4 mV. **Expect** single or low double digits; **`band_railed,0`**.
- **`Z` must not depend on speed** — Z is geometry. The instrument's own negative case: **slow and
  brisk legs disagreeing on `Z`** by more than their spread **falsifies the instrument, not the
  motor**. Forward and reverse *are* expected to differ (hall hysteresis and filter delay are late in
  the direction of travel); their **mean** is the `Z`.
- **Agreement with the driven value** — `Z` = **−3.6 ± 0.4°** from four scan self-locations. A cold
  `Z` inside about ±2° of it confirms both; outside that, the report states which of the two it
  believes and why, and neither is quietly preferred.
- **H-3 can come out either way, and both are results.** Equal sectors: each hall code's crossings
  sit at the same place within their sector, within their spread. Unequal: a stable per-sector offset,
  the same on both directions and both speeds.

**Desk evidence for the new detector** (a scratch model of `alignCross()`, 2026-09-22: 3 mV noise,
the real 0.52 ms channel): on a slow leg the old detector counted **1,248** crossings against 89 real;
the new one counts **89**, on both slow and brisk legs. Its timing bias on the slow leg is 0.28°. The
remaining ~2.5° late at brisk is the 0.52 ms sample spacing — it predates this change and cancels in the
forward/reverse mean by design.

### Load 2 — the START trace, against the driver's new start seed («#3600»)

**What changed.** At every start from rest the driver used to place the field exactly on the rotor
estimate (`err_` = 0). The duty servo only raises duty once `|err_|` reaches **57** units: its setpoint
is 42, and its truncating gain (18, shifted right 8) adds nothing until the excess reaches 15. So duty
sat pinned at minimum while the field ran away from a stationary rotor, then caught up hard. Pass 1
measured exactly that, 4 of 4: **pinned at 1,600 until k=232 (464 ms), first moving at `|err|`
57–59, `err` reading −1 from k=2.** The field now starts **57 units (80°) ahead** of the rotor in the
direction of travel.

**Prediction, fixed before the run** — the same four traces (QTR cells, both motors, both directions):

| Reading | Pass 1 (seed 0) | Pass 2 must show |
|---|---|---|
| `\|err\|` from k=2 | ~1 | **~57** (the seed) |
| duty's first change | k=232 (464 ms) | **within the first few samples** — tens of ms at most |
| from-rest peak current | 64–100, peaking **after** the pinned wait (i=87 at k=369) | **lower**, and early |

⛔ **Falsifier:** `|err|` near 0 at k=2 (the seed is not in the image — check `servo_engage` first), or
duty still pinned for hundreds of ms, or peak current **unchanged or higher**. Any one of them means the
seed does not do what the construction claims, and the fix is not certified.

**And nothing else in part A may get worse.** The seed touches only starts from rest — the lines run
by a speed change, a stop and a hold are unchanged. So every part-A cell that passed at its last run
must pass again. A new failure anywhere in part A is a finding against this change, not noise.

---

## What this pass does NOT decide

- **The start surge UNDER LOAD.** Wheels are up. This pass shows whether the pinned wait is gone; the
  size of what is left under load is the tethered floor run's.
- **The servo setpoint A/B is retired, not deferred.** The driver applies the field at the commanded
  angle and the servo integrates duty until `|err|` equals its setpoint, so at steady state the
  setpoint and the lead combine **by construction** (`isp_bldc_motor.spin2:4456-4463`, `:4580`). A 90°
  build at a lead 31° higher *is* the 60° build. A bench run would measure an equation.
- **`L` at a half** (H-5) — unchanged by this pass.
