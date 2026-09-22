# Limits reset — moving the limits the old drive set, on purpose

**Asked by Stephen, 2026-09-22:** *"look for values that were limits that were put in place before we had the new
drive technology. Now that we have the new drive technology, I want you to think about where those limits move
to, and let's move them purposefully"* — and then: *"Identify which limits are in consideration, and then how
you'd run experiments to move them to identify where to move them to, and then let's plan for that."*

**The starting evidence:** Visit 8b ([evaluation](../analyses/bench/2026-09-22/VISIT-8B-EVALUATION.md)), on
DRIVER_REV 4, wheels up. Cruise current is 22–74 % below the old driver's, duty is 5–13 % lower at every speed,
and the top rungs no longer saturate.

---

## 1. The limits in consideration

Each row names the limit, where it lives, what set it, and whether the new drive gives a reason to move it.

| # | Limit | Where | Set by | Move? |
|---|---|---|---|---|
| **L1** | **Speed ceiling per voltage** (18.5 V: 147 × 10⁶, "until fault at 277 RPM") | `confgurePowerLimits()` `maxFwdIncreAtPwr` | the old drive's fault edge | **Yes.** At 165 × 10⁶ both wheels follow at 100.1–100.2 % with no lag holds (Visit 8b §3.5). The true edge is above that, and it has never been commanded. |
| **L2** | **Duty ceiling**, `duty_max = (pwm_limit << 4) / 2` (24,264 at 270 MHz) | `init()`; the source records 5/8 and 3/4 as "BAD" | trials on the old drive | **Yes, by construction first.** The drive re-centres the three phase levels each frame (`sub drive_x, (min+max)/2`), so the largest excursion is cos 30° = 0.866 of the amplitude. **~14 % of voltage headroom is unused** (15.5 %, less the dead-gap's share). DERIVED from the PWM arithmetic; unmeasured. |
| **L3** | **Acceleration ramp** (`ramp_min` 1,500, `ramp_inc` 22, `ramp_max` 200,000; `ramp_down` 50,000) and **`ACCEL_MAX_MM_S2`** 10,000 | `init()`, `setAcceleration()` | 2022 notes: *"at 18.5v 50_000 seems to fault a lot on gravel"* — old-drive faults | **Measure.** The start surge that made fast ramps fault is gone (A-1 0.01–0.02), so a faster ramp may now be clean. |
| **L4** | **Default max speed**, `maxSpeed` / `maxSpeed4dist` = 75 % | `init()`, `setMaxSpeed*()` | undocumented; likely the old top-end fault margin | **Decide after L1.** It is a user-facing default (Stephen's decision). |
| **L5** | **Low-speed floor**, `minFwdIncreAtPwr` 544,628 (*"anything below yields NO rotation"*) | `confgurePowerLimits()` | the old drive | **Measure.** The new servo holds a point at low speed; rotation below the floor is untested. |
| **L6** | **Duty floor**, `duty_min` 1,600 | `init()` | Chip's original (was 200 << 4) | **Measure only.** The low-speed current it costs is small (~10 mV net at 1 × 10⁶). |

**In consideration, and staying where they are:**

| Limit | Why it does not move |
|---|---|
| Current limits `I_PEAK_A` 40 / `I_CONT_A` 27 | set by the MOSFETs, not the drive |
| `LAG_SOFT` 80, `LAG_HOLD` 100, fault test 125 | bound by the hall sawtooth (PL-105); moving them needs a sub-sector angle, deferred with back-EMF («#3602») |
| The fold-back and protective-stop mechanisms | protection, not performance |

---

## 2. The experiments — how each limit's new value is found

All wheels up except E5. Each experiment is a tier of the one bench script, and each prints its verdicts.

### E0 · Desk, before any run: give the feedforward its own constant (PL-107)

`ff_ceiling` is `maxFwdIncreAtPwr` today, so **raising L1 would silently weaken the feedforward.** Give the
feedforward its own per-motor, per-voltage constant, equal to today's value (147 × 10⁶ at 18.5 V), so L1 can
move without moving it. No behaviour changes. The gates certify it, and the next ladder re-confirms A-5
unchanged.

### E1 · Find the unloaded top speed (L1)

- **Load:** extend `dual-a`'s probe rungs above 165 × 10⁶ in 10 × 10⁶ steps (175, 185, …) until the wheel stops
  following. Both motors, both directions, on the existing ladder machinery and its guards (10 A abort, fault
  recovery, stop after consecutive faults).
- **Reads per rung:** following (`rate / pred`), duty capped fraction (`win_cap`), lag holds (`win_lag`), `err`,
  net current.
- **The top speed** is the highest rung with following ≥ 98 % and zero lag holds. **The edge** is the first rung
  that holds or faults. Both are printed.
- **Can fail:** yes, it reports the edge wherever it is; a top below 147 × 10⁶ would be a regression.

### E2 · Use the duty headroom (L2), then repeat E1

- **Desk first:** compute the largest amplitude for which every phase's high- and low-side PWM value stays
  inside `0 .. frame`, **including the dead-gap offsets**. Make that `duty_max`, and name the invariant it
  guarantees: the PWM never clips.
- **Build:** a `-D` variant (`DUTY_MAX_SVM`), so the same visit can compare the two.
- **Instrument:** the status block already carries `drive_u/v/w`. The harness reads their per-window maxima
  and judges **no value outside `0 .. frame`**. That is a cell that fails on clipping, the failure "5/8 BAD"
  most likely was.
- **Then:** E1 again on the variant. The predicted gain is ~14 % in top speed, and the current at every lower
  rung should be unchanged (the ladder's A-5 comparison).

### E3 · Faster acceleration (L3)

- **Load:** START traces (the A-1/A-2 machinery) at `ramp_inc` 22 (today), 44 and 88, and a speed-DOWN pair at
  `ramp_down` 50,000 and 100,000, both motors and directions.
- **Judged per setting:** duty drop ≤ 0.10, peak ratio ≤ 1.8, following during the ramp (no lag holds), time
  to AT_SPEED.
- **The new value** is the fastest ramp that passes all four **wheels up**. Its loaded margin is E5's.

### E4 · Below the low-speed floor (L5, L6)

- **Load:** extend LOWSPD below 544,628 (e.g. 400,000, 250,000, 100,000). Record whether each rotates and
  follows, and its gap statistics. The same rungs are also run with `duty_min` halved as a variant.
- **The new floor** is the lowest increment that rotates steadily.

### E5 · Loaded confirmation — the floor run («#3591», at «#3576»)

Wheels-up numbers set a ceiling. **Only a loaded run sets the margin under it.** The published top speed and
acceleration are E1–E3's values reduced by what the floor run shows under load. This is the only experiment
that needs the PLOT panel work («#3585») unbenched.

---

## 3. The plan

| Step | What | Gate | Task |
|---|---|---|---|
| 1 | **E0**: split the feedforward constant from the ceiling | build-check, check_style | new |
| 2 | **Build E1–E4**: probe rungs above 165 × 10⁶, the `DUTY_MAX_SVM` variant and its clip cell, the ramp settings, and the low-speed rungs; plus the Visit 9 run sheet | build-check, check_style; each new cell shown able to fail | new |
| 3 | **Visit 9** (wheels up): `dual-a` (E1, E3, E4), then `dual-a-svm` (E2) | the run sheet | new |
| 4 | **Move the limits** from Visit 9's report: the L1 ceiling table (18.5 V measured, other voltages scaled by voltage and marked DERIVED), L2 `duty_max` if E2 passes, L3 ramps, L5 floor. The speed-ceiling table in `MOTOR_CHOICE.md` follows. | build-check; a confirming `dual-a` | new; feeds «#3515» |
| 5 | **E5** under load | the floor-run sheet | «#3591» / «#3576» |

**The one decision that is Stephen's** (raised on its own, not here): raising L1 changes what `power` 100 means,
because power maps linearly onto the ceiling (C-7). A robot commanded at 60 today would go faster after the
update. Either power keeps its meaning and the extra range is reached another way, or the scale changes and
the release note says so.
