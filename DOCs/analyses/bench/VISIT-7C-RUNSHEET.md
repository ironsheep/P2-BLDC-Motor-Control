# Visit 7c — run sheet, pass 2 (one load, ATTENDED: your hands turn the wheels)

**Plan section:** R18.2f ([`../../plans/BENCH-READINESS-SPRINT-PLAN.md`](../../plans/BENCH-READINESS-SPRINT-PLAN.md)).
**Task:** «#3594».

**Pass 1 — done.** 2026-09-21/22, `scan-droop` + `scan` + `dual-a`. Judged in
[`2026-09-22/VISIT-7C-EVALUATION.md`](2026-09-22/VISIT-7C-EVALUATION.md): the start-transient
mechanism is answered (the servo's 60° deadband, 4 of 4 traces).

---

## Check the banner before reading anything else

| Load | Banner must read |
|---|---|
| `dual-align` | `src_rev 24`, `fmt 12`, part `ALIGN` |

⛔ `src_rev 23` means the hysteresis and the band test are **not** in the image. The run then repeats
the 2026-09-21 shakedown and measures nothing. Stop and rebuild.

---

## The visit, declared

Seven attributes, per *Shared vocabulary — the bench visit* (`~/.claude/skills-docs/SKILLS-AUTHORING.md`).

| | |
|---|---|
| **Purpose** | **Two jobs.** It **certifies** the rebuilt crossing detector (PL-99) and clip test (PL-100). It **measures**, cold and at zero current, two things no driven run can: the hall zero `Z` over the whole circle, and **whether the six hall sectors are equal** (manual hole H-3). It is also the first real reading of back-EMF on this rig. |
| **Hardware risk** | **None from the drive — no motor is ever driven.** Both drivers start with the bridge set to coast (all six FETs off), and only a driven bridge can fault. MEASURED at the shakedown: worst current in the whole tier **15 mV** against a 150 mV band. Wheels up. Panic throughout: physical battery disconnect. |
| **Who can observe** | **You turn each wheel by hand.** Nothing else is asked of you: every verdict is printed. |
| **Runs that carry state** | **None.** Nothing is written to the driver; nothing needs restoring. |
| **Run length** | **About 3 minutes of turning.** MEASURED at the shakedown: 8 legs, 64 s from the first edge of the first leg to the last. The pauses between legs are yours. |
| **Repeatability** | Repeatable and idempotent. A leg turned the wrong way is **not** a mistake: legs are labelled by the direction they measure. |
| **Variant matrix** | One build: `test_bench_dual.spin2` part ALIGN. One rig (Rev B, paired 6.5 in hub, 18.5 V, 270 MHz). One log. |

---

## The command

```bash
tools/bench-run.sh dual-align
```

**What your hands do.** Eight legs: left wheel then right, each forward and reverse, each slow then
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

---

## What this pass does NOT decide

- **The start-surge fix.** The mechanism is answered; the fix (start the servo at its setpoint rather
  than at zero error) is a driver change and rides a later pass with the START trace that certifies it.
- **The servo setpoint A/B is retired, not deferred.** The driver applies the field at the commanded
  angle and the servo integrates duty until `|err|` equals its setpoint, so at steady state the
  setpoint and the lead combine **by construction** (`isp_bldc_motor.spin2:4456-4463`, `:4580`). A 90°
  build at a lead 31° higher *is* the 60° build. A bench run would measure an equation.
- **`L` at a half** (H-5) — unchanged by this pass.
