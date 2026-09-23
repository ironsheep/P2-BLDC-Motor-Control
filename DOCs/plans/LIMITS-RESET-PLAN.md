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
| **L2** | **Duty ceiling**, `duty_max = (pwm_limit << 4) / 2` (24,264 at 270 MHz) | `init()`; the source records 5/8 and 3/4 as "BAD" | trials on the old drive | **Yes, by construction first.** The drive re-centres the three phase levels each frame (`sub drive_x, (min+max)/2`), so the largest excursion is cos 30° = 0.866 of the amplitude. **14.0 % more amplitude fits** once the PWM bias is centred on its switching window (§2 E2: 1,728 against 1,516 counts at 270 MHz). DERIVED from the PWM arithmetic; unmeasured. |
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

All of E1–E4 are one new part of the motion harness, `LIMITS` (`tools/bench-run.sh dual-limits`; E2 is
`dual-limits-svm`). It carries only the new loads. Re-running `dual-a` around them would re-measure an
unchanged drive for 25 minutes.

### E1 · Find the unloaded top speed (L1)

- **Load:** segment `LIMTOP`. The ladder's twelve speeds (5 … 165 × 10⁶), then probe rungs in 10 × 10⁶ steps
  (175 … 245 × 10⁶) until the wheel stops following. Both motors, both directions, on the existing ladder
  machinery and its guards (10 A abort, fault recovery, stop after consecutive faults).
- **Reads per rung:** following (`rate / pred`), duty capped fraction (`win_cap`), lag holds (`win_lag`), `err`,
  net current, and the PWM levels (`BM-CLIP`, E2).
- **The top speed** is the highest rung with following ≥ 98 % (widened by the rung's own tick quantisation) and
  zero lag holds. **The edge** is the first rung that is not like that: it holds, faults, falls short or measures
  no window. The climb stops at the first such rung at or above 147 × 10⁶. `BM-TOPSPD` prints both.
- ⚠ **Following alone does not find a usable top, so `BM-TOPSPD` prints a second one.** MEASURED: on the shipped
  drive *and* the R18.4 drive, every ladder rung up to 165 × 10⁶ followed at 99.8–100.3 % with zero lag holds,
  while duty sat at its cap from 147 × 10⁶ up (`debug_260922-122752.log`, `-161317.log`). A wheel that follows with
  duty pinned has nothing in reserve for a load. So `unsat` is the highest clean rung that never capped duty.
  Which of the two the published ceiling moves to is step 4's call, with E5 beside it.
- **Can fail:** yes, it reports the edge wherever it is; a top below 147 × 10⁶ would be a regression
  (`R18-DUAL-TOPSPD-M`). That cell is a regression guard: no drive on file fails it.

### E2 · Use the duty headroom (L2), then repeat E1

- **Desk first — done.** `P_PWM_TRIANGLE` holds Y in `0 .. F`, F = `frame_cnt / 2` (p2kb
  `p2kbArchSmartPin01000PwmTriangle`). The high side's Y is `level + bias`, the low side's is that plus
  `dead_gap`. Re-centring puts each level within √3/2 of the amplitude either side of `bias`. The old `bias`
  (F / 2) wastes `dead_gap` of room on the low rail, so the construction centres it on the switching window,
  `bias = (F − dead_gap) / 2`. The amplitude that then fills both rails is `(F − dead_gap) / √3`, less a 4-count
  guard for the CORDIC's rounding and the floored centring. **The invariant: every high-side Y ≥ 0 and every
  low-side Y ≤ F, so the PWM never clips.** `DOCs/plans/servo-model/svm_bound.py` checks it over every angle with
  the CORDIC's Y perturbed ±1 at each bench clock:

  | Clock | F | dead-gap | legacy amplitude, room to the rails | SVM amplitude (`duty_max`), room |
  |---|---|---|---|---|
  | 200 MHz | 2,272 | 52 | 1,123 · 162 / 110 | **1,279** (20,464) · 1 / 1 |
  | 270 MHz | 3,068 | 70 | 1,516 · 220 / 150 | **1,728** (27,648) · 2 / 1 |
  | 300 MHz | 3,409 | 78 | 1,685 · 244 / 166 | **1,920** (30,720) · 1 / 2 |

  The same arithmetic explains the two trials the source marks "BAD". Under the old bias the low side had 1,464
  counts before it clipped, and 5/8 peaks at 1,641 while 3/4 peaks at 1,970. Both clipped.
- **Build — done, then adopted:** `-D DUTY_MAX_SVM` (DRIVER_REV 6), certified at Visit 9 (PWM room 2 against the
  desk's 1–2; `unsat` +12.9 %; rungs 3–8 unchanged) and made the drive's only construction at DRIVER_REV 7. The
  feedforward's slope does **not** move with `duty_max`:
  `ff_ceiling` scales by `duty_max` over the duty the back-EMF line was measured against. That is exactly 1:1 on
  the default build (PL-107's trap, one level down).
- **Instrument — done:** the instrument cog folds the least and greatest `drive_u/v/w` over every capture's
  stored samples (`testGetDriveLevels()`), and `BM-CLIP` prints the least room to either rail per rung.
  `R18-DUAL-PWMCLIP-M` fails on any negative room. Its judge proves its own negative case first on synthetic
  levels (`BM-CLIPTEST`). The sampling misses the exact peak, so an observed room can only read *more* than the
  true one. What shows the instrument reaches the peaks is the SVM build reading within a few counts of the
  desk's 1–2 at full duty.
- **Then:** E1 again on the variant. The predicted gain is ~14 % in top speed, and the current at every lower
  rung should be unchanged (the ladder's A-5 comparison).

### E3 · Faster acceleration (L3)

- **Load:** segment `LIMRAMP`. START traces (the A-1/A-2 machinery) from rest to the quarter at `ramp_inc` 22
  (today), 44 and 88. Then a speed-DOWN pair, from 147 × 10⁶ to the quarter, at `ramp_down` 50,000 and 100,000
  (new trace cause `SLOWER`). Both motors and directions; the defaults are restored and read back after
  (`BM-RAMPREST`).
- **Judged per setting:** duty drop ≤ 0.10, peak ratio ≤ 1.8, following during the ramp (no lag holds), time
  to AT_SPEED. `BM-RAMP` prints the last two per trace (`lag_holds`, `ramp_ms`, `followed`). Drop and ratio come
  from the trace through `start_metrics.py`, the code that judged A-1/A-2 at Visit 8. Duty drop does not apply
  to a speed-down: duty is meant to fall.
- **The new value** is the fastest ramp that passes all four **wheels up**. Its loaded margin is E5's.

### E4 · Below the low-speed floor (L5, L6)

- **Load:** segment `LIMLOW`. 544,628 (today's floor), 400,000, 250,000 and 100,000, descending. Record whether
  each rotates and follows, and its gap statistics (`BM-LOW`). The same rungs run again with `duty_min` halved,
  set live through `testSetDutyMin()`, read back and restored (`BM-LOWDUTY`).
- **The window is 7.5 s, and that is a hard limit.** `windowStats()` times the window by a `getct()`
  difference, which wraps past 2³¹ ticks (7.9 s at 270 MHz). Samples are stored one in three, so the ring holds
  the transition and the window. Expected hall edges per window: 11, 8, 5 and 2. That says whether each rung
  rotates and how evenly. It does not measure the lowest rungs' rate finely.
- **The new floor** is the lowest increment that rotates steadily.

### E5 · Loaded confirmation — the floor run («#3591», at «#3576»)

Wheels-up numbers set a ceiling. **Only a loaded run sets the margin under it.** The published top speed and
acceleration are E1–E3's values reduced by what the floor run shows under load. This is the only experiment
that needs the PLOT panel work («#3585») unbenched.

---

## 3. The plan

| Step | What | Gate | Task |
|---|---|---|---|
| 1 | **E0**: split the feedforward constant from the ceiling | build-check, check_style | «#3603», done |
| 2 | **Build E1–E4**: probe rungs above 165 × 10⁶, the `DUTY_MAX_SVM` variant and its clip cell, the ramp settings, and the low-speed rungs; plus the Visit 9 run sheet ([`VISIT-9-RUNSHEET.md`](../analyses/bench/VISIT-9-RUNSHEET.md)) | build-check, check_style; each new cell shown able to fail | «#3604», done |
| 3 | **Visit 9** (wheels up): `dual-limits` (E1, E3, E4), then `dual-limits-svm` (E2) — **run 2026-09-22, both complete** ([evaluation](../analyses/bench/2026-09-23/VISIT-9-EVALUATION.md)) | the run sheet | «#3605», done |
| 4 | **Move the limits** from Visit 9's report. **Moved (DRIVER_REV 7):** L2 the clip-free `duty_max` is the drive; L1 147 → 165 × 10⁶ at 18.5 V on the rule *keep today's ~7 % unloaded duty reserve*, the other voltages scaled and DERIVED; L5 544,628 → 100,000. **Not moved:** L3 (A-2 cannot rank ramps, PL-109; the stop ramp waits for E5); L6 (PL-110). The speed-ceiling table in `MOTOR_CHOICE.md` follows. | build-check; the confirming **`dual-limits-top`**, which carries the power check (`R18-DUAL-POWERMAP-M`); `dual-a`'s raw ladder cannot see a power table | «#3605»; feeds «#3515» |
| 5 | **E5** under load | the floor-run sheet | «#3591» / «#3576» |

**What `power` means when L1 moves — settled by the API, not a decision.** `power` 100 is top speed (C-7:
power maps linearly onto the ceiling), so when the ceiling rises, 100 rises with it. STEPHEN, 2026-09-22:
*"100 means top speed, if we moved it, 100 meaning moves."* The release note states the effect: an app runs
faster at the same `power`, by the ratio Visit 9 measures («#3515»).
