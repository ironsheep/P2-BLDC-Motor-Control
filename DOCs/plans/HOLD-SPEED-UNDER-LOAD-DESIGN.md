# Hold speed under load — design (PL-167, «#3640», phase 1 of 2)

**Status:** DESIGN, approved (§7). No driver code is changed by this document. **Release: 6.1.0** (R21: 6.0.0 ships
first with PL-167 as a Known Issue).
**Phase 2, desk steps (2026-10-01):** the H-a refit (§3.6) and D-4's condition (§7 Q1) are recorded. H-a did not
reproduce the slow/medium depth and revealed no second mechanism; D-4's condition failed, so `LAG_HOLD` stays 100.
**D-5 RULED (STEPHEN 2026-10-02, "ok let's go with A"):** build D-1..D-3 **plus D-5** (§4.9): the limit hold at 64
with its one-pass set-back, and the blocked count on limiter activity. The build is «#3655»; the coast trial's
expectation becomes "latches" («#3656» item 1).
**Driver:** `src/isp_bldc_motor.spin2` at DRIVER_REV 46 (`:6796`; PASM image unchanged since 45, `:7011-7020`).
**Evidence:** `DOCs/analyses/bench/2026-09-30/floor2/` (`debug_260930-181811.log` floor-auto, `…-182135.log`
obstacle, `…-182653.log` FlySky) and `FLOOR-RERUN-EVALUATION.md` §2.1, §2.3, §5.
**Desk model:** `DOCs/plans/servo-model/spin_model.py` (one wheel) and `spin2_model.py` (two wheels), built on
`sim_servo.py` beside them, and `logscan.py` for the logs (§3.3, §9). Moved into the repository in phase 2 (Q2).
**Doctrine:** P10 (design the cause out; no re-measuring), P5 (benefit priced before anything is built), P13 (cog/LUT
headroom counted), P14 (degrade gracefully).

---

## 0. Summary for Stephen

- **What happens.** Spinning in place on the shipped lead schedule, each wheel's duty servo falls into a slow limit
  cycle: about 0.25-0.3 s per swing, duty 4,450 ↔ 8,500, lag 0 ↔ 100. Each peak reaches `LAG_HOLD`, so the field is
  held and the hold decay cuts the field's speed by 1/64. The ramp's lag gate then stops it climbing back, and the
  steering object pulls the other wheel down to match. The speed is given up with 7-20 % of the duty in use and no
  current limit anywhere near.
- **Why (the cause).** The trim is integral-only on the lag. It is stable only while the rotor's stiffness at its
  operating angle can carry the trim's gain against the inertia behind the wheel. The schedule puts the field where it
  draws least current with the wheels up, which is close to the motor's torque peak, so that stiffness is small. On the
  bench the wheel's own inertia (~0.006 kg m²) tolerates that. A 7.7 kg platform puts about 5× that inertia behind
  each wheel, and the loop goes unstable. The legacy pair sits 39-47° from the torque peak and stays calm. The fixed
  pair sits 23° away and swings, but stays under the hold. The schedule sits 10-19° away and reaches the hold.
- **Proven?** For the BRISK pair contrast, yes. The desk model, built from the driver's own arithmetic, reproduces
  the schedule leg's signature and not the fixed pair's, with only the offsets changed. It also loses the signature
  on every leg when only the trim's gain is quartered. For the slow and medium legs it reproduces the oscillation and
  its absence on the legacy pair, but **not the depth of the speed loss** (modelled 94-100 % against the logged
  57-94 %). That part is not proven (§3.6). The phase 2 refit to the torque wall (H-a) did not prove it either, and it
  makes the BRISK contrast depend on the parameters (§3.6).
- **The design (D-1..D-3, plus D-4 for Stephen).**
  - **D-1:** a calm trim gain sized for the platform, `SERVO_ACC_SHIFT` 14 → 16 (a constant).
  - **D-2:** a fast trim slope only while the lag is past `LAG_SOFT`, so a real load gets torque at once.
  - **D-3:** the hold decay acts only when a limiter has the duty, so the field gives way only at the limit.
  - **D-4 (candidate):** lower `LAG_HOLD` 100 → 86, so that at the limit the held field sits near the torque peak
    instead of past it (PL-105). **Phase 2: its condition failed. `LAG_HOLD` stays 100, option (c) (§7 Q1).**
  - The placement (the lead schedule) is untouched, so **the unloaded current is unchanged by construction**.
- **Benefit (modelled).**
  - Every spin leg at 99.6-100 % of command, against 57-94 % logged, with no hold and no path limiting.
  - At equal speed the schedule draws 2.5-4.4× less current than legacy.
  - A one-sided straight-line load of 2-4 N·m (25-48 N at the tyre) is held at 99 %+, against 8-62 % today.
  - The 3,000 mm/s² speed-up arrives on time.
  - Unloaded current is identical.
- **Cost:** cog +2 longs (55 → 53 free), LUT +14 (55 → 41 free), about +22 clocks per frame. No ABI change.
- **Questions (§7):** D-4 and the protective stop (Q1); keeping the desk model in the repository (Q2); proceeding
  with the slow/medium depth unproven (Q3); how the drive "says so" (Q4).

---

## 1. The signature, and what it is not

### 1.1 The logged lines

Identical commands for every pair at a given speed; only the offsets differ (`BM-SPINLEG`, log lines 53-60):

```
:53  BM-SPINLEG,...,leg,3,pair,2,offs,SCHED,speed,MEDIUM,dir,RIGHT,l_pwr,13,incre,20_087_872,pred_x10,536,...
:55  BM-SPINLEG,...,leg,5,pair,3,offs,LEGACY,speed,MEDIUM,dir,RIGHT,l_pwr,13,incre,20_087_872,pred_x10,536,...
```

The schedule leg at the medium speed, then the legacy leg at the same command:

```
:126 BM-SPINW,...,leg,3,motor,LEFT,...,amps,1_406,duty,3_622,duty_pk,5_082,err,57,err_pk,100,rate_x10,479,fol_pct,90,
     fol_pm,633,short,TRUE,off_neg,17,off_pos,336
:158 BM-SPINW,...,leg,5,motor,LEFT,...,amps,1_787,duty,4_181,duty_pk,4_276,err,48,err_pk,72,rate_x10,538,fol_pct,100,
     fol_pm,1_000,short,FALSE,off_neg,43,off_pos,317
```

And at BRISK, the schedule leg against the fixed pair:

```
:497 BM-SPINW,...,leg,7,motor,LEFT,...,duty,5_379,duty_pk,6_423,err,47,err_pk,97,rate_x10,794,fol_pct,84,...,off_neg,5,off_pos,347
:923 BM-SPINW,...,leg,9,motor,LEFT,...,duty,6_477,duty_pk,7_311,err,47,err_pk,80,rate_x10,993,fol_pct,101,...,off_neg,14,off_pos,338
```

The path limiter engages on every schedule leg and never on the others. Leg 3, for example (`:128-132`):
`PATH_LIMIT LEFT 895, 1_000, 880, 1_000, 897`.

The one traced schedule spin, leg 7, RIGHT (`BM-TS`, 2 ms samples, `python3 …/logscan.py trace`) is a limit cycle:

```
k 345 d 7_356 e 66 | k 400 d 6_620 e 11 | k 463 d 6_645 e 100 | k 495 d 8_404 e 41 | k 545 d 5_865 e 6 | k 600 d 6_231 e 101
running samples 157: duty min 4451 max 8495 mean 6232; err min -8 max 101 mean 33.6
```

Duty peaks come every ~140 samples (~280 ms); `err` swings between near 0 and the hold.

The FlySky 200 mm/s² speed-up shows the same cycle on a **straight** drive (`…-182653.log`, 18:28:57-59,
`python3 …/logscan.py rc`): `L err 96 duty 2_888 short 0 | … err 8 duty 3_671 | … err 95 duty 3_774 short 1`, a
roughly 300 ms period, `short` set at each peak.

### 1.2 The ten legs

Duty swing is `duty_pk − duty` from the `BM-SPINW` lines.

| Leg | Pair | path_pm | LEFT fol / err_pk / swing | RIGHT fol / err_pk / swing |
|---|---|---|---|---|
| 1 | schedule SLOW + | 810 | 84 % / 100 / 1,199 | 88 % / 100 / 1,647 |
| 2 | schedule SLOW − | 629 | 57 % / 113 / 1,080 | 80 % / 100 / 1,133 |
| 3 | schedule MED + | 633 | 90 % / 100 / 1,460 | 94 % / 100 / 910 |
| 4 | schedule MED − | 756 | 88 % / 100 / 1,368 | 94 % / 84 / 1,195 |
| 5 | legacy MED + | 1,000 | 100 % / 72 / 95 | 100 % / 72 / 121 |
| 6 | legacy MED − | 1,000 | 100 % / 72 / 238 | 100 % / 72 / 175 |
| 7 | schedule BRISK + | 861 | 84 % / 97 / 1,044 | 88 % / 91 / 803 |
| 9 | fixed BRISK + | 1,000 | 101 % / 80 / 834 | 100 % / 92 / 1,474 |
| 10 | fixed BRISK − | 1,000 | 100 % / 89 / 965 | 100 % / 94 / 1,250 |

⚠ **A correction to the dispatch's premise.** The fixed pair's swing is **834-1,474**, not "≤ ~250"; only the
legacy pair is that calm. The fixed pair hunts too (A-3 would fail it), but stays under the hold. **The discriminating
observable is reaching `LAG_HOLD`** (holds, decay, path limiting), not the swing. §3 uses that.

### 1.3 What it is not

- **Not the harness.**
  - Every reading is the driver's own status (duty, `err`, the hold count behind `short`) or the steering object's
    event. The same harness, session, battery and command increments ran the legacy and fixed legs clean,
    interleaved with the failing ones (legs 5-6 between 4 and 7).
  - The offsets were written and read back for every leg (`BM-OFFREST`, SPINOFF PASS).
- **Not the path limiter as cause.**
  - It engages only for a wheel that is SHORT (its lag limiter held within the last 4 slots) and BEHIND (steering
    `:2764-2765`), so every engagement comes after a hold.
  - It never engaged on legacy or fixed (`path_pm 1_000`).
  - The single-wheel model, which has no limiter at all, still holds and loses speed at BRISK (fol 89.5 %, 9 held
    passes; `spin_model.py legs`).
  - Its role is to import one wheel's loss into the other: a consequence, and an amplifier.
- **Not the current limit.**
  - Duty 2,000-5,379 of 27,648 and 0.050-0.236 A DC on the failing legs.
  - **No `FOLDBACK` or `CURRENT_LIMIT` event anywhere in the floor-auto session** (grep count 0).
  - The fixed BRISK legs ran higher duty (6,477-6,870) and current (to 0.424 A) than any failing leg, and held 100 %.
- **Not the supply.**
  - The pack read 20,311-20,397 mV at the RC session's start and sagged about 1.5 % at its 3.25-3.49 A peaks.
  - The spins draw under 0.5 A.
  - The same pack ran the passing legs between the failing ones.
- **Not the lead table "being wrong" unloaded.** Wheels up it is the measured least-current lead (manual §5.2), and
  the model runs it calm wheels up (§3.3). The table is right for what it was measured for. It leaves the loop no
  margin once inertia is added.

---

## 2. The mechanism as built (DRIVER_REV 46)

### 2.1 Every PWM frame (44 kHz), `.ctlMotor`

1. The halls are read and the error is formed against the sector's table angle plus the direction's offset:
   `err_ = (angle_ − (hall_angles[] + offset)) SAR 24`, 256 counts per electrical cycle (`:7915-7927`). The table
   angle is held for the whole sector, so `err_` carries a ±21-count sawtooth on the true lag.
2. Fault if `|err_| ≥ 125` (`:7929-7935`).
3. Fold-back if the DC-link reading is over the limit: `duty_ −= duty_ >> 6`, `foldback_cnt_++`, and the trim is
   skipped (`:7948-7981`).
4. **The trim:** `servo_acc += (|err_| − 48) × (duty_ >> 4)`; `duty_ = (servo_acc SAR servo_shift_) + duty_ff`
   (`:7986-7993`). `servo_shift_` is the params-run long `servo_shift` (`:7352`), loaded from `SERVO_ACC_SHIFT = 14`
   by `init()` (`:4429`, `:7039`).
5. Clamps `[duty_min_, duty_cap_]`; `duty_capped_++` when the ceiling is enforced; the one anti-windup re-derives
   `servo_acc` from the applied duty (`:7996-8014`).

### 2.2 Every drive pass (every 23 frames, 1,913/s), `drvMotor`

1. `lag_s := ±err_`, signed in the direction of motion (`:7642-7643`).
2. The command is taken (`gettgtincr`, `:7674`, `:8690-8699`).
3. **`jerkStep`** (`:7714` → `:8757-8851`) steps the acceleration toward its limit by one jerk per pass. **The lag gate**
   (`:8796-8807`): while the field leads the rotor by `LAG_SOFT` (80) or more in the direction the acceleration
   pushes, the acceleration eases toward 0 instead of rising.
4. **`.justIncr`** (`:7734-7738`): if `lag_s < LAG_HOLD` (100) the field advances `angle_ += drv_incr`. Otherwise it
   is **held**: `lag_held_++`, and **`holdDecay`** (`:8716-8725`) turns AT_SPEED into SPIN_UP and, in SPIN_UP above
   `DRV_INCR_FLOOR`, takes `drv_incr −= drv_incr SAR 6` (1/64; a 33 ms time constant).
5. `passEnd` → **`feedForward`** (`:8701-8714`): `duty_ff = |drv_incr| × duty_max / ff_ceiling`, which `init()`
   scales so that duty_ff = |drv_incr| × 24,256 / 147×10⁶ at the 18.5 V configuration (`:4478-4485`).
6. The PL-55 ceiling during a ramp-down (`:7746-7764`). It does not bind here: a held SPIN_UP is not SPIN_DN.

### 2.3 Every front slot (8 ms)

- **The lead:** `frontApplyLead()` writes the pair `Z ± L` with `Z = −4°` and `L` from `leadTenthsForIncrement(|drv_incr_now|)`
  (`:6440`, `:6459-6477`; table `:5016-5023`: 20.5° at 18.375×10⁶ and below, 5° at 36.75×10⁶, 8° above).
  **It is keyed on the field's speed**, so a decayed field reads more lead. At BRISK the read-back pairs were 5/347
  and 6/346 (L ≈ 9-10°) instead of the expected 1/351 (L 5°). That load dependence is in the right direction, and too
  small.
- **The shortfall:** `holdSlotsAgo` (`:6441-6445`); `shortfallNow()` reads `|drv_incr_now| / |command|` (`:6448-6457`).
  That fraction is exact only because the decay walks the field down to the rotor.
- **The steering path limiter** (`isp_steering_2wheel.spin2:2726-2800`): a SHORT wheel more than 100 ‰ behind its
  partner scales both commands to its fraction at once (`frontScaleCommand`, motor `:2812-2831`). The scale releases
  by 20 ‰ per slot only after 4 clean slots (`:2455-2456`, `:2787-2800`).

### 2.4 The offsets, in the frame the physics needs

From the error's formula (`:7919-7927`) and the pair's definition (`offset_fwd = Z + L` for negative increments,
`offset_rev = Z − L` for positive, `:4966-4972`), with the motor's true hall zero of −4° (manual §4.2), **DERIVED**:

```
lag_s  =  (true field lead over the rotor)  +  L_eff        L_eff = L − 4 − Z  (positive),  L + 4 + Z  (negative)
```

**At the same `err_`, each degree of L is a degree less of voltage angle from the magnets.** Smaller L moves the field
toward the torque peak. Two independent readings agree with that sign:

- **The basin** (manual §5.3, LEFT, negative increment, the swept `offset_fwd = Z + L`): current rises toward large
  offsets (abort at 63°), and the drive **faults at 3°**. Small L is the torque-wall side.
- **The walls** (manual §6.2): "too little lead" is the torque wall. At 49 ticks/s, L −2° held only 51 % and −7°
  never settled.

So the shipped schedule's slow and medium L (19-20.5°), and especially its BRISK L (5-10°), place the field nearer the
torque peak than the fixed pair's 18° or the legacy pair's 43°. That is exactly why they draw less current.

---

## 3. The root cause

### 3.1 Statement

**The duty trim is an integral loop on the lag, closed through the rotor's torque-against-lag stiffness. At the
schedule's placement that stiffness is small, because the least-current placement is the one nearest the torque peak.
The platform's inertia (about 5× the wheel's own) then demands more stiffness margin than the placement leaves, for
the trim's gain.** The loop limit-cycles at about 3-4 Hz. Each peak that reaches `LAG_HOLD` holds the field, and each
held pass takes 1/64 off the field's speed (`holdDecay`). The lag gate stops the ramp back while the cycle keeps
reaching 80. The steering limiter imports the slower wheel's fraction into its partner. The speed is given up with
torque to spare, because nothing in that chain asks whether the duty could rise.

The PL-167 candidates, answered:

- **"The servo's authority and stability under load with this timing":** stability, yes. Authority, no: duty and
  current are far below their limits.
- **"The order in which the lag limiter and the servo act":** it matters once the loop oscillates. The hold converts a
  transient peak into a permanent loss of field speed before the trim has asked for more torque. D-3 fixes that order.
- **"The lead's load dependence":** the schedule follows the field's speed, so a decayed field gets slightly more
  margin. Too little, and only after the speed is already lost.

### 3.2 Why the margin, the inertia and the gain decide it (DERIVED)

The same model `DRIVE-INTEGRATION-DESIGN.md` §5.2 used for the start surge, `J s³ + D s² + K_δ s + K_V g = 0`, is
stable only when `D·K_δ > J·K_V·g`. Extend its R-only motor with the winding's inductance, with `δ` the voltage's angle
from the magnets and the torque peak at `90° + φ`, `φ = atan(ωL/R)`. Then:

```
K_δ ∝ V sin m,   K_V ∝ cos m,   m = (90° + φ) − δ  (the margin to the torque peak);   the trim's g = g0·V (duty-scaled)
stable  ⇔  tan m  >  J · g0 / D
```

Four consequences:

1. The margin needed grows with the inertia J and with the trim's gain g0.
2. Wheels up to the floor is J × ~5, so the needed `tan m` is ~5× larger.
3. Quartering g0 (D-1) brings it back to ~1.25× the bench value.
4. To first order it depends on neither the load nor the speed. That is why the bench never showed it and the floor
   does, and why only the placement separates the pairs.

The margins at the servo's point (`err_` 48), from the model's parameters (`spin_model.py`'s printed e90; φ for
0.5 mH, 0.24 Ω):

| Leg | L_eff | δ at err 48 | torque peak (90° + φ) | margin m | Logged |
|---|---|---|---|---|---|
| schedule SLOW | 20.5° | 76.2° | 93.4° | **17.2°** | holds |
| schedule MED | 19.1° | 77.6° | 96.7° | **19.1°** | holds |
| schedule BRISK | 5-10° | 86.8-91.7° | 102.1° | **10.4-15.3°** | holds |
| fixed BRISK | 18° | 78.8° | 102.1° | **23.3°** | swings, no hold |
| legacy MED + / − | 39° / 47° | 57.8° / 49.8° | 96.7° | **38.9° / 46.9°** | calm |

### 3.3 The desk model

`spin_model.py` (one wheel) and `spin2_model.py` (two wheels) are in `DOCs/plans/servo-model/`, beside the
`sim_servo.py` they extend (its motor, its fitted e90 = 56 at L = 18, its friction). `logscan.py` there reads the
floor2 logs.

**One correction in phase 2.** The driver's `err_` is an 8-bit angle: `(angle_ − table) SAR 24` of a 32-bit
difference, so it wraps at ±128, and the fault test reads the wrapped value (`:7926-7930`). The phase 1 runs did not
wrap it. The models now do (`wrap=1`, the default; `wrap=0` reproduces phase 1). Nothing changes while `|err_|` stays
under 128: `legs`, `design`, `step` (today and D-1..D-3) and `release` (D-1..D-3, with and without
`lag_hold=86`) re-ran digit for digit. One phase 1 claim changes: D-3 without D-2 at
4 N·m is a slowdown to 76.3 % with 526 held passes, not a lag fault (`step acc_shift=16 dC=1`; §4.2, R5). A rotor
pushed back past the held field now reads a wrapped error, as it does on the floor (the obstacle trace's `e 115` to
`e −98`, `logscan.py obst`).

- **Driver arithmetic, ported line by line:** the frame trim, clamps and anti-windup (`:7986-8014`); the pass's
  `lag_s`, `jerkStep` with `xStar` and the lag gate, `.justIncr`'s hold and `holdDecay`, `feedForward`; the front cog's
  lead schedule every 8 ms; the steering `frontLimitPath()` / `frontScaleCommand()`. Fold-back is modelled on phase
  current at 27 A.
- **Physics:**
  - dq currents with the winding's inductance, voltage mode.
  - Two motors coupled through the platform's mass matrix (7.7 kg, track 387 mm from `BM-SPINBUILD`, r = 82.55 mm,
    yaw inertia Iz); spin and straight drives are its two modes.
  - Per-motor resistance from the manual §2.4 means (LEFT 501, RIGHT 467 mΩ phase to phase).
- **Offsets enter only as e90**, via §2.4's `L_eff`.

**Parameters and their standing:**

| Parameter | Value | Standing |
|---|---|---|
| e90 at L = 18 | 56 counts | FITTED earlier (sim_servo, bracket 52-60) |
| Winding L | 0.5 mH | NOT MEASURED. Bracketed 0.37-0.74 mH by the wheels-up torque wall: at the quarter, L −2° still holds; at the eighth it does not (manual §6.2) |
| Yaw inertia Iz | 0.26 kg m² (J per wheel 0.030 spin, 0.032 straight) | NOT MEASURED. Estimated from the build (0.22-0.35) |
| Coulomb scrub Tc | 0.45 N·m per wheel | FITTED to one number: the legacy leg 5 duty, model 4,175 against logged 4,181 / 4,051 |
| **Refit (phase 2, H-a):** e90 at L = 18, winding L | **52 counts, 0.85 mH** | FITTED jointly to the torque wall (§3.6). The wall pins a valley, not a point: (53, 0.65 mH) and (54, 0.55 mH) fit nearly as well. The phase 1 bracket for the winding L (0.37-0.74 mH) came from the model's softer wall and is superseded |

**Checks the model must also pass**, wheels up (`spin_model.py checks`):

- The schedule runs calm at 10, 20 and 37×10⁶: swing 36-59, err_pk 69-70. The bench is noisier (178-399, manual §6.4);
  the model has no cogging.
- The torque wall at the eighth: L −2° gives 75 % (measured 51 %), L −7° gives 45 % with 488 holds (measured "never
  settled").
- At the quarter, L −2°..8° hold (measured flat).

On the floor it predicts the duties it was not fitted to: schedule MED 3,483-3,695 (logged 3,487-3,742), SLOW
2,154-2,335 (logged 2,000-2,287). The BRISK trace's period and range match: model ~240 ms, duty 5,000-9,000; logged
~280 ms, 4,450-8,500 (`spin_model.py trace seed=7`).

### 3.4 The falsification test

**The rule:** the cause is proven only if the model reproduces the schedule legs' signature and not the legacy/fixed
legs', with only the offsets changed.

| Contrast (same model, only offsets differ) | Schedule legs, model | Legacy / fixed legs, model | Verdict |
|---|---|---|---|
| **BRISK, leg 7 against 9/10** (`spin2_model.py legs`) | fol 92.1 / 89.7 %, err_pk 101, swing 1,958 / 1,799, holds 2 / 10, **path limiter engaged 880 ‰** (logged 861) | fol 98.0-101.7 %, err_pk 78-81, swing 411-537, no hold, path 1,000 | **REPRODUCED** at the central parameters. Holds for every Iz from 0.18 to 0.35 (`jscan`); fixed first holds at Iz 0.42. **At the phase 2 refit it does not hold up** (§3.6) |
| **SLOW / MED, legs 1-4 against 5/6**, central parameters | swing 451-1,060, err_pk 82-97, no hold, fol 98.8-100.3 % | swing 69-103, err_pk 69 | **PARTIAL.** Oscillation and contrast reproduced; holds and speed loss not |
| SLOW / MED at the bracket's edge (`legs e90_L18=53 Tnoise=0.4 Iz=0.30`) | holds on all four, err_pk 99-100, swing 1,193-1,616, path limiter on legs 1-2 (894, 813), **fol 94.4-98.9 %** | clean: err_pk 71-74, swing 136-193; fixed err_pk 93-97, swing 1,333-1,707 (logged 80-94 / 834-1,474) | **PARTIAL.** Signature present, depth short (logged 57-94 %) |
| **The gain alone:** `SERVO_ACC_SHIFT` 14 → 16, nothing else (`design acc_shift=16`) | every schedule leg clean: err_pk 69-70, swing 57-184, fol 99.6-99.8 % | unchanged, clean | **The mechanism is load-bearing:** removing the gain excess removes the signature on every leg |

**So the cause is PROVEN for the BRISK contrast and for the mechanism.** The model reproduces the schedule-against-fixed
signature with only the offsets changed, and loses it when only the trim gain changes. **It is NOT proven as the whole
explanation of the slow/medium speed loss:** the model reaches the hold there only at the bracket's edge, and loses
1-6 % where the floor lost 6-43 %.

### 3.5 The second limit: where the held field sits (PL-105)

A trace of a 4 N·m one-sided step applied 0.45 s after arrival, under D-1..D-3 (`rtrace acc_shift=16 dB=1
boost_shift=10 dC=1`):

1. The lag reaches 100 at 1,050 ms.
2. The trim takes duty from 5,398 to 16,482 in 20 ms, and the phase current reaches the limit.
3. **The rotor stalls there with 27 A flowing.**

At `LAG_HOLD` the field sits 25-85° past the torque peak, depending on where in its sector the rotor stopped
(`err_` = H means a true lag of H ± 21). So the current at the limit makes only about half the torque it could:
PL-105, from the earlier fit. This is the remaining obstacle to "torque up to the current limit". It is what D-4
addresses.

### 3.6 What is not proven, and the experiment that would settle each

| Hypothesis for the missing slow/medium depth | Discriminating experiment (desk first) |
|---|---|
| H-a: the real margin at low speed is smaller than modelled (e90 and winding L fitted on other data). The model's eighth-speed torque wall is softer than measured: 75 % against 51 % at L −2°. | Refit e90 and winding L jointly to the manual §6.2 wall (51 % at −2°, unsettled at −7°) and the ladder, then rerun `spin2_model.py legs`. Proven if the refit reproduces fol 57-94 % while legacy/fixed stay clean. |
| H-b: the floor's scrub torque fluctuates more, or more slowly, than ±40 % at 8 ms. | Sweep `Tnoise` amplitude and correlation time. The first visit's spins (`floor/`) are comparison legs only and carry no trace. |
| H-c: platform yaw dynamics or caster scrub beyond the mass matrix couple the wheels. | Compare the model's left/right phase against a **traced** slow schedule spin; none exists (only legs 7/8 were traced). |
| H-d: the harness's window rule (250 ms after AT_SPEED) catches the cycle at its worst. | Apply the harness's exact window and AT_SPEED rule in the model. |

**H-a outcome (phase 2, 2026-10-01): NOT PROVEN, and no second mechanism.** The refit fits the wall and the model's
other checks. It reproduces the size of the slow/medium oscillation, but not the depth of the speed loss.

**The refit** (`spin_model.py wall`, then `wall fine=1`; MODELLED against MEASURED targets, wheels up):

| Reading | MEASURED (manual §6.2; `VISIT-8B-EVALUATION.md` §3.6) | Central (e90 56, 0.50 mH) | **Refit (e90 52, 0.85 mH)** |
|---|---|---|---|
| Eighth, L 3° | 91 % | 101.4 % | **90.7 %** |
| Eighth, L −2° | 51 % | 75.2 % | **48.1 %** |
| Eighth, L −7° | never steady | 44.7 %, 488 held passes | **26.8 %, 396 held passes** |
| Eighth, L 8° | held | 100.3 % | 100.6 % |
| Quarter, L 8° / 3° / −2° | held (flat) | 100.0 / 100.0 / 99.9 % | 100.0 / 100.0 / 99.8 % |
| Wall score (squared misses) | — | 714 | **9** |

The wall pins a valley rather than a point: (53, 0.65 mH) scores 21 and (54, 0.55 mH) 49.

**The other checks, at the refit (MODELLED):**
- **Ladder** (`ladder`; wheels up, L 18, the old duty clip). 169.3 / 165.9 / 167.7 / 171.2 / 175.7 duty per 10⁶ at 20-100×10⁶,
  against MEASURED 167-174. Mean err 48.0-48.1. Central: 165.6-174.4.
- **START** (`start`). Duty drop 0.010, against MEASURED 0.01-0.03. Current peak over settled 1.05, against MEASURED 1.15-1.53
  (the model's current is a proxy). Central: 0.039 / 1.23.
- **Wheels-up schedule** (`checks`). Calm: swing 34-84, err_pk 69-70, as at central.
- **The R-only `sim_servo.py`**, the old servo the START fit was made on (`sim_servo.py ladder e90=52.0`). At 20×10⁶:
  duty 4,196, peak 6,059, err_pk 90 (MEASURED 3,850, 5,300-5,580, 87-89). Its 120×10⁶ rung pins at the clip, where
  the bench held mean err 48. e90 52 sits at the edge of that fit's bracket (52-60). That model has no winding
  inductance to offset it, so this reading is weak.
- **Floor duties** (`spin2_model.py legs e90_L18=52 Lh=0.00085`). Legacy leg 5: 4,152 / 4,125 against logged 4,181 /
  4,051 (Tc not refitted). Schedule MED 3,688-3,913 and SLOW 2,276-2,436: about 5 % above the logged ranges' tops
  (3,742 and 2,287).

**Today's drive on the refit** (`spin2_model.py legs e90_L18=52 Lh=0.00085`, MODELLED):

| Legs | Logged (MEASURED) | Refit |
|---|---|---|
| Schedule SLOW / MED (1-4) | fol 57-94 %, err_pk 84-113, swing 910-1,647, path 629-810 | **fol 97.9-101.8 %**, err_pk 88-100, swing 916-1,497. Holds on leg 1 (11 / 4) and leg 2 (4 / 0); the path limiter engaged on leg 1 only (866 ‰) |
| Schedule BRISK (7) | fol 84 / 88 %, err_pk 97 / 91, path 861 | fol 100.7 / 104.2 %, err_pk 97 / 99, holds 1 / 0, no path limiting in the window |
| Legacy (5, 6) | fol 100 %, err_pk 72, swing 95-238 | fol 99.9-100 %, err_pk 69-70, swing 78-116: clean |
| Fixed (9, 10) | fol 100-101 %, err_pk 80-94, swing 834-1,474 | fol 97.4-101.2 %, err_pk 84-89, swing 749-1,030, no hold |

**Along the valley:**
- At (53, 0.65 mH): SLOW/MED fol 98.4-100.3 %; BRISK 96.5 / 96.7 % with holds 2 / 6 and no path limiting.
- At (54, 0.55 mH): SLOW/MED 98.6-99.7 %; BRISK 97.8 / 94.2 % with holds 0 / 13 and the path limiter at 894 ‰.
- With ±40 % scrub on the refit (`Tnoise=0.4`): both SLOW legs hold, and the path limiter engages at 852-895 ‰. Fol is
  still 97.4-98.7 %.
- `jscan` on the refit:
  - SLOW leg 1 carries the full signature from Iz 0.30, and leg 2 from 0.35.
  - BRISK carries it only at Iz 0.22.
  - The fixed pair is no longer clean from Iz 0.30.

**What it means:**
1. **H-a is not proven.** The refit gets the oscillation's size right: swing and err_pk now sit inside the logged ranges
   on more legs than at central, and holds appear at SLOW. The speed given up stays at 0-2 %, against 6-43 % logged. A
   smaller low-speed margin is part of the picture. It is not the depth.
2. **The BRISK contrast of §3.4 depends on the parameters.** At the better-fitted wall it weakens (at 53 and 54) or
   vanishes (at 52). The mechanism test that survives at every parameter set is the gain test. `design acc_shift=16`
   on the refit cleans every leg: fol 99.6-100 %, err_pk 67-70.
3. **No second mechanism is revealed.** The design (`design acc_shift=16 dB=1 boost_shift=10 dC=1`) cleans every leg at
   all three valley points: fol 99.6-100.0 %, err_pk 67-70, swing 20-157, no hold, no path limiting. On the refit,
   `lag_hold=86` gives the identical result.
4. **What carries the depth is still unidentified.** H-b, H-c and H-d are untested. The model also lacks cogging,
   non-uniform hall sectors and the PL-55 ceiling. SPINRATE (§6) is the floor's catch for it.

None of these changes the design. The only mechanism the model shows is the gain-against-margin one, and removing it
cleans every leg at every parameter set tried (§5), the phase 2 refit included. The certification cells (§6) would
catch a second mechanism.

---

## 4. The design

### 4.1 The invariant

**Speed is held by torque, up to the current limit; the field gives way only at the limit, and the drive says so.**

In the driver's terms:

- **(I-1)** In steady running under any load the drive can carry, the field is never held. The lag stays under the
  hold because the loop is stable and a real load gets torque at once.
- **(I-2)** `drv_incr` falls below the command (the field gives way) only on a pass where a limiter held the duty since
  the previous pass: the fold-back (`foldback_cnt_` advanced) or the duty ceiling (`duty_capped_` advanced).
- **(I-3)** Every give-way therefore coincides with a limiter count and, through the shortfall, with the steering
  object's path limiting. `EV_FOLDBACK` and `EV_PATH_LIMIT` in the event log mean "a wheel at its limit".

### 4.2 The changes

**D-1 · A calm trim gain, sized for the platform.**
- `SERVO_ACC_SHIFT` 14 → **16**, a quarter of today's gain. It is a value in the params run (`servo_shift`, `:7352`),
  re-read every frame, so **no PASM changes and no ABI moves**.
- In the model the stability margin then holds from Iz 0.18 to 0.42 (J 0.022-0.044 per wheel), with e90 down to 53
  and ±40 % scrub (§5).
- The value is provisional. Phase 2 settles 15 or 16 on the refit model (Q3) and the wheels-up regression.

**D-2 · A fast slope past `LAG_SOFT`, so a real load gets torque at once.** Each frame, after the trim's own add (`:7990`):

```
                testb   drv_incr, #31               wc
                negc    lag_s, err_                     ' the frame's lag, signed as the pass forms it (:7642-7643)
                cmps    lag_s, #LAG_SOFT            wc
    if_nc       sub     lag_s, #LAG_SOFT
    if_nc       muls    lag_s, tmpX                     ' tmpX = duty_ >> 4, already formed (:7988)
    if_nc       shl     lag_s, #SERVO_BOOST_SHL         ' 6: 64x the calm gain at SERVO_ACC_SHIFT 16
    if_nc       add     servo_acc, lag_s
```

- Below 80 it does nothing, and the calm loop is undisturbed. Steady `err_pk` is 67-76 in the model at every
  parameter set.
- Above 80 the duty grows exponentially, by a factor e every ~370 / (lag − 80) ms: 19 ms at the hold. From a running
  duty of 3,500 it reaches the current limit's duty in about 30-40 ms.
- `lag_s` is reused as scratch: every pass recomputes it at entry (`:7643`) before any read, and the pass's reads come
  before the frame code. No new register is needed.
- MULS takes 16 × 16 signed (`p2kbPasm2Muls`): (lag − 80) ≤ 47 and `duty_ >> 4` ≤ 1,728.

**D-3 · The field gives way only at the limit.**
- `holdDecay` (`:8716`) still turns AT_SPEED into SPIN_UP, but walks `drv_incr` down only when
  `duty_capped_ + foldback_cnt_` has changed since the previous pass.
- `passEnd` snapshots that sum each pass, into one new cog register `lim_seen`.
- A hold below the limit is then a pause of the field, a few tens of milliseconds while D-2 lifts the duty. It is not a
  permanent loss of speed, and the shortfall the steering object reads stays at the command.
- **D-3 never ships without D-2.** Without the fast slope, a long hold below the limit leaves the partner unscaled. In
  the model (gain/4 + D-3, no boost) the platform's pivot then drags the held wheel back at 4 N·m: 76.3 % with 526
  held passes (`step acc_shift=16 dC=1`), against 99.6 % with D-2. Phase 1 read this as a lag fault (err 143). That
  was the unwrapped error; the driver's wrapped `err_` reads −113 there and does not fault (§3.3).

**D-4 · CANDIDATE (Q1): `LAG_HOLD` 100 → 86, so that the field held at the limit sits near the torque peak.**
- D-1 makes calm running peak at 67-76 (sawtooth top), which leaves room for a hold at 86. Today's servo peaked at
  71-89, which is why PL-105 could not move the hold.
- With D-4 the 4 N·m early-step case holds 99.9 % instead of stalling (§5).
- **It narrows the blocked-rotor test's margin.** `bFrontProtect()` counts `|err| ≥ LAG_SOFT` with no tick (`:2899`).
  A stalled wheel then stands at ~86 instead of ~100, so a rocking stand dips under 80 more often and restarts the
  count. The obstacle behaviour accepted for 6.0 (R18) could get worse. That is Stephen's call, not this document's.
- **Phase 2: NOT TAKEN.** Its desk condition failed (§7 Q1). A wheel held at 86 that the load pushes back one hall
  sector reads 86 + 42.7 = 128.7, which wraps to −127 and trips the fault test at 125. On a rocking obstacle that
  replaced the protective stop with a lag fault in most of the modelled contacts.

### 4.3 Why each is correct by construction

- **D-1:** `tan m > J·g0/D` (§3.2). Lowering g0 lowers the margin the loop needs, whatever the placement. It moves no
  placement, so it cannot change the unloaded current.
- **D-2:** it acts only where the motor is already past its operating point (lag ≥ 80, δ ≥ ~124°). It therefore cannot
  enter the small-signal loop D-1 stabilises. Its only job is to reach torque before the lag reaches the hold.
- **D-3:** the give-way is gated on the two counters that are, by definition, "the duty could not rise". I-2 holds by
  construction, not by tuning.
- **D-4:** it moves the field held at the limit toward the torque peak. It only changes behaviour once the lag is past
  86, which calm running does not reach after D-1.

### 4.4 What it costs (P13)

Headroom, read from the source's `fit` comments: **cog 441 of 496 used, 55 free** (`:8406`, DRIVER_REV 45, PASM
unchanged at 46 per `:7020`); **LUT run image 457 of 512, 55 free** (`:9313`).

| Part | Cog longs | LUT longs | Time |
|---|---|---|---|
| D-1 constant | 0 | 0 | 0 |
| D-2, in the LUT run image via one `CALL` from `.servoTrim` (recommended) | +1 | +8 (7 + `RET`) | ~22 clocks per frame (CALL 4, `p2kbPasm2Call`; RET; 7 × 2) |
| D-2, cog-resident instead | +7 | 0 | 14 clocks per frame |
| D-3 (`lim_seen`; `holdDecay` +4, `passEnd` +2) | +1 register | +6 | +4 instructions on held passes, +2 per pass |
| D-4 constant (an immediate) | 0 | 0 | 0 |
| **Total, recommended** | **+2 (53 free)** | **+14 (41 free)** | **~+22 clocks per frame** of 6,136 at 270 MHz |

These are estimates from the sketch, not counts. Phase 2 counts from the compiler and runs `tools/pasm_equiv`'s
frame-budget report, which fails any window over 75 % of the 160 MHz frame (2,727 clocks).

**Accumulator range at shift 16:** `(duty − ff) << 16` ≤ 27,648 × 65,536 = 1.81×10⁹ < 2³¹ (84 % of range). D-2's
largest add is 47 × 1,728 × 64 = 5.2×10⁶ per frame, and the anti-windup re-derives every clamped frame. Phase 2 adds
pasm_equiv scenarios at `duty_max` to prove it.

### 4.5 ABI impact

**None.** No VAR long is added, removed or moved. `servo_shift` keeps its place in the params run and only its value
changes. `DRVR_PARAMS_LONGS_COUNT` (27) and `DRVR_STATUS_LONGS_COUNT` (24) are unchanged, and so is
`isAbiLayoutValid()`. The counters D-3 reads (`duty_capped_`, `foldback_cnt_`) are already in the status run. A new
public "torque-limited" signal (Q4) would be an API addition mirrored in `isp_steering_2wheel`. It is not proposed.

### 4.6 Risks

| # | Risk | Where it stands |
|---|---|---|
| R1 | The calm loop's margin is modelled, not measured: Iz and winding L are unmeasured | Clean across Iz 0.18-0.42, e90 53-60, winding L 0.37-0.74 mH, ±40 % scrub (`jscan`, corners) |
| R2 | Calm-running peaks reach 80 and trigger D-2 in running | Model 67-76 (a few hundred boost frames per leg only at the adverse corner, harmless there). The bench measured 76-86 at 10/20×10⁶ **under today's gain** (manual §6.4). A-3's err_pk ≤ 76 is the guard |
| R3 | A load step's current overshoots into the fold-back; D-3 reads that as "at the limit" | The modelled 4 N·m early step does this. With the hold past the peak it stalls (40 % after release, against 84 % today). D-4 would remove it (99.9 %), but **D-4 is not taken (§7 Q1), so this modelled regression in one case stands** (PL-105) |
| R4 | Obstacle behaviour (R18) | D-1..D-3: same logic, same fold-back limit, reached sooner. The obstacle stands already reach it today (14 `FOLDBACK` events in `…-182135.log`). Modelled at `LAG_HOLD` 100 (`block`, §7 Q1): latch times as today's, a solid object 987-1,102 ms after contact against today's 1,004-1,620 |
| R5 | Fault interaction | Fault test unchanged (125). On the load steps, no fault with D-2 present. D-3 alone slowed to 76 % at 4 N·m (§4.2): **they ship together**. On an obstacle a lag fault stays possible, as today: 1-2 of 16 modelled contacts at central parameters, today and D-1..D-3 alike; 4 of 16 on the rocking obstacle at the refit, against today's 1 |
| R6 | Unloaded behaviour | Current identical wheels up (0.04 / 0.09 / 0.13 A at 10 / 20 / 37×10⁶). Low-speed duty swing 56-61 → 148-154, under A-3's 400 |
| R7 | Rev A (5 mV/A) resolves the fold-back coarser (PL-163, archived; its open residual is PL-170), so D-3's "at the limit" may come later | Not modelled. Rev A is not certified by this design |
| R8 | The grab cells' premise | A hand load below the current limit (~11 N·m per wheel at 27 A, ~135 N at the tyre) no longer slows the wheels, so LDPATH / LDHUNT see no path limiting: a PL-168-type premise correction before the next run |
| R9 | A second slow/medium mechanism (§3.6) survives | The certification cells catch it: SPINRATE on every leg |

### 4.7 Alternatives considered and rejected

| Alternative | Why not |
|---|---|
| A proportional term on the lag sampled at each hall edge (sawtooth-free) | Modelled. It clears the holds, but leaves its own oscillation (swing to 914; to 3,176 at twice the gain), and fails BRISK at the adverse corner (`design dA=1`, `design dA=1 dC=1 kp_shift=2`). Its once-per-tick sampling adds the lag it is meant to remove |
| The gain alone (D-1 without D-2 / D-3) | Clean spins, but a 1 N·m one-sided load drops the platform to 21 % (`step acc_shift=16`): the slower trim reaches the hold, and the decay and the limiter do the rest |
| Load-dependent lead (more L under load) | Buys margin by spending circulating current exactly when the motor is working, and moves the placement the unloaded saving rests on. D-1 gets the margin without either |
| Lifting the decay without a fast slope (D-3 alone) | 76 % with 526 held passes at 4 N·m in the model, against 99.6 % with D-2 (§4.2; phase 1 read it as a lag fault) |
| A sub-sector angle (hall-time interpolation or back-EMF) to place the hold at the peak | The real fix for PL-105, and out of scope. D-4 gets most of it with a constant |

### 4.8 How a user would notice

- Spins, turns and pushes run at the commanded speed. The wheels draw more current while a load is on, because that
  is the torque.
- The platform slows only when a wheel is at its current limit. Then the event log shows `EV_FOLDBACK`, and on a
  two-wheel platform `EV_PATH_LIMIT`, and both wheels slow together as today.
- Speed-ups arrive when the ramp says.
- Nothing changes unloaded: same current, same speed, same ramps.

### 4.9 D-5 — where the held field sits while a limiter has the duty («#3645», PL-167, PL-105)

**Status: DESIGN, RULED IN (STEPHEN 2026-10-02: "ok let's go with A" -- D-1..D-3 + D-5). Built by «#3655».** Plan §1.1. Not to be confused with *R18.4 D-5*, the
source's label for `holdDecay` (`:7738`, `:8716`); the build should name this one "PL-167 D-5".

#### 4.9.1 What it answers

Under D-1..D-3 one modelled case regresses (§3.5, R3). A 4 N·m load on the LEFT wheel from 1.0 s to 2.0 s, on a straight
drive at power 13, leaves the platform at **40.4 / 41.0 %** of command over the 1.5 s after release, against today's
**83.9 / 82.9 %** (`release`). The chain (`rtrace acc_shift=16 dB=1 boost_shift=10 dC=1`):

1. D-2 lifts the duty to the 27 A limit in ~60 ms. The field is held at `LAG_HOLD` 100.
2. At a stall the voltage has no back-EMF to work against, so the current is in phase with it. The torque peak is
   then where the voltage sits on the q axis: `err` ≈ e90, 56-57 counts at the schedule's MEDIUM placement (§3.3).
   A field held at `err` 100 leads the rotor by 79-121 counts, 22-64 past that peak. **On that side of the peak a
   rotor that slips back loses torque**, down to none at 64 counts (90°) past. So the wheel stalls with 27 A flowing.
3. D-3 correctly lets the field give way at the limit. At a stall the limit never releases, so `holdDecay` walks
   `drv_incr` to the floor, and the path limiter scales both wheels to 66 ‰.

The lever is where the held field sits once a limiter has the duty. A fixed lower hold failed (D-4, §7 Q1). The
blocked stop must still latch a wheel stopped at its limit (`bFrontProtect()`, `:2864-2904`).

#### 4.9.2 The mechanism

**D-5a, driver: the limit hold.** On a running pass in SPIN_UP or AT_SPEED where a limiter acted since the previous
pass (D-3's own fact: `duty_capped_ + foldback_cnt_` differs from `lim_seen`):
- the field advances only while `lag_s < LAG_LIM`, **64**, instead of `LAG_HOLD`;
- a field already past `LAG_LIM` is **set back to it in that pass**:
  `angle_ −= sign(drv_incr) × (lag_s − LAG_LIM) << 24`, and `prior_angle` moves with it;
- the held pass counts `lag_held_` and calls `holdDecay` as today (D-3 gates the decay on the same fact).

Every other pass keeps today's `LAG_HOLD` 100. SPIN_DN and SLOW_TO_CHG are excluded: `holdDecay` does not walk them,
and the PL-55 ceiling, the one limiter of SPIN_DN, would otherwise pin the lag under its own lift at `LAG_SOFT`.

**D-5b, front cog: the blocked count.** `bFrontProtect()` counts a pass when a drive is commanded, the state is driving
and there is no hall tick, and **either** `|err| ≥ LAG_SOFT` (today) **or a limiter acted since its previous pass**
(`duty_capped + foldback_frames` changed; both are already in the status run).

The sketch below replaces `.justIncr`'s `cmps lag_s, #LAG_HOLD wc` (`:7734`) with `call #holdGate`, LUT-resident. It is
a design sketch: the build counts and checks it.

```
holdGate        mov     tmpX, duty_capped_              ' D-3's fact: did a limiter act since the previous pass?
                add     tmpX, foldback_cnt_
                cmp     tmpX, lim_seen              wz  ' NZ: limited. Z survives to the return on every path
    if_nz       cmp     drv_state_, #DCS_SPIN_DN    wc  ' C: SPIN_UP or AT_SPEED (:6693; .justIncr is reached only
    if_nz_and_c jmp     #.limHold                       '  running, so no state below SPIN_UP -- the build confirms)
    _ret_       cmps    lag_s, #LAG_HOLD            wc  ' today's gate: C = the field advances
.limHold        cmps    lag_s, #LAG_LIM             wc  ' the limit hold: C = the field advances
    if_c        ret                                     ' RET without WC/WZ keeps C (p2kbPasm2Ret)
                mov     tmpX, lag_s                     ' the set-back in angle_ units, (lag_s - LAG_LIM) << 24 <= 63 << 24
                sub     tmpX, #LAG_LIM
                shl     tmpX, #24
                testb   drv_incr, #31               wc  ' signed as the pass forms lag_s (:7642-7643); writes C only
    if_c        neg     tmpX
                sub     angle_, tmpX                    ' err_ reads LAG_LIM on the next frame
                sub     prior_angle, tmpX               ' I-7: CMPM sees no move, so fwdrev keeps its side (:7915-7916)
    _ret_       cmps    lag_s, #LAG_LIM             wc  ' NC again: held. lag_held_ and holdDecay follow at .justIncr
```

**Why `prior_angle` moves too (DERIVED).** `.ctlMotor` reads the direction from the field's last move:
`cmpm angle_, prior_angle wcz` / `if_nz wrc fwdrev` (`:7915-7916`). CMPM's C is the sign of `angle_ − prior_angle`
(`p2kbPasm2Cmpm`). A bare set-back would flip `fwdrev` for a forward drive. The error would then be read against the
other offset (`:7924-7925`), which is 2L away (up to 29 counts), and it would stay flipped while the field is held.
The model has no `fwdrev`, so it models only the corrected form.

#### 4.9.3 The invariants

- **(I-4)** While a limiter has the duty in SPIN_UP or AT_SPEED, the field is held no more than `LAG_LIM` ahead of the
  rotor's sector: after such a pass, `err_` reads at most 64. By construction: the set-back writes it.
- **(I-5)** The drive parks a field against a still rotor at only two places: `LAG_HOLD` 100 with no limiter, and
  `LAG_LIM` 64 at a limiter. Both lie outside the wrap-fault lattice (§4.9.4).
- **(I-6)** The blocked stop counts every pass on which the drive pins a still wheel: past `LAG_SOFT`, or at a
  limiter.
- **(I-7)** The set-back moves the field, never the direction `err_` is read in.
- **I-1..I-3 stand.** D-5 acts only on limited passes. Steady running below the limit is untouched: every `design`
  leg is identical digit for digit. The give-way stays D-3's.

#### 4.9.4 Why it cannot enter the 82.3-88.3 window (DERIVED)

- **The lattice.** A parked field reading L reads L + 42.67k (wrapped) after k backward hall ticks. It faults when that
  lands in [125, 131] mod 256 (`|err_| ≥ 125` on the wrapped 8-bit value, `:7926-7930`).
  - So L is unsafe when L mod 42.67 lies within 3 counts of the lattice points {0, 42.7, 85.3}.
  - Those are the windows −3..3, 39.7..45.7 and 82.3..88.3. The last is §7 Q1's.
- **64 sits in the middle of the safe band.** 64 = 1.5 sectors is residue 21.3, 18.3 counts from both edges.
  - Its backward ticks read 106.7, −106.7, −64, −21.3, 21.3 and 64, none within 18 counts of ±125.
  - 100 is residue 14.7, 11.7 counts from an edge. 21.3 and 106.7 are equally central but sit before the peak and
    further past it.
- **While limited, a back tick is answered at once.** The next pass (≤ 0.52 ms) sets the field back to 64, so a
  limited parked field is only ever read one tick back (106.7).
- **Set back, never walked.** A field above 64 when the limiter acts reaches 64 in one pass, so it never dwells in the
  window while limited. Candidate C3, which walks, reads 88 and 84 on its way down.
- **The margin covers what moves the reading.**
  - A lead-schedule write moves `err_` by the change in L. The schedule spans 5-20.5°, which is at most 11 counts.
  - Real hall sectors are not exactly 42.67 counts.
  - Both are inside 18.3. The model cannot show the lead effect: its `err` does not include the offset (§2.4).
- **What D-5 does not remove.** The field still transits 82.3-88.3 at its own speed against a rotor that has just
  stopped, before any limiter acts. Today's drive and D-1..D-3 carry this too. It is the one fault per obstacle cell
  below: the faulting wheel had been held 1-2 passes and set back at most once.

#### 4.9.5 What the blocked stop counts

- **Today's test never counts it.** Under D-5 a wheel stopped at its limit reads `|err|` 64, below `LAG_SOFT`.
  - Model, D-5a without D-5b, solid object: **0 of 16 latch.** 15 run 7.8 s unlatched and 1 faults.
  - Constraint 2 fails exactly as predicted. This is D-5b's negative.
- **D-5b counts on the limiter, not on `err`.** A still wheel at its limit folds back on every 1 ms front pass.
  - With D-5b, solid object: 15 of 16 latch.
  - Every latch in the grid comes 1,000-1,055 ms after the wheel's last tick, inside the harness band of 988-1,168
    (`test_bench_dual.spin2:15961-15962`).
- **The two cheaper counts fail (DERIVED).**
  - Lowering the threshold to `LAG_LIM` needs no new long. But the parked field reads exactly 64, a margin of 0, and a
    lead write can lower `err_` by up to 11 counts and stop the count.
  - Counting `lag_held` fails the same way: below 64 the field is not held. At the decayed floor (1,500 per pass,
    about 0.17 counts/s) it takes about 6 s per count to creep back.
- **BLKSTOP's bounds stay valid.** The latch still needs `BLOCKED_PASSES` after the last tick (the lower bound). D-5b
  can only start the count sooner (the upper bound). Its premise text (`test_bench_dual.spin2:15925`) names today's
  test, and the build amends it.
- **BLKLIMIT stays meaningful.** At 64 the count runs only while the limiter acts.
- **A premise change for the floor (as R8).**
  - On the rocking (yielding) object the model now **latches 15-16 of 16**. D-1..D-3 rocked 5-7 of 16 for 7.7 s.
  - The torque at the limit stalls the wheel against the spring. The blocked count alone, without the hold, gives
    9 latched / 6 rocked / 1 fault.
  - The coast trial's expectation ("rocks without latching", R18) becomes "latches". The floor premises are corrected
    before the next run.

#### 4.9.6 Candidates considered

| Candidate | Release, 4 N·m, L / R | Other | Verdict |
|---|---|---|---|
| **C1:** limit hold at 64, set back in one pass, + D-5b | **99.9 / 100.0 %** | grid in §4.9.7 | **Chosen** |
| C2: lower hold while limited, no set-back | 40.4 / 41.0 % | — | No effect: a stalled rotor never brings the lag down to the lower hold |
| C3: set back 4 counts per pass | 95.2 / 95.0 %, path limiter to 762 ‰ | rocking 16 / 0 / 0 | Rejected on I-5: walks 100 → 96 → 92 → 88 → 84, through the window, while limited |
| C4: C1, sticky until a forward tick | 100.0 / 100.0 % | faults 1/0/1/1/1 against C1's 1/1/0/1/1 (solid, rocking 1,000, rocking 3,000 at central; solid, rocking at refit) | Rejected: a register and a hall compare more, no modelled gain |
| C5: a fixed `LAG_HOLD` 64 | — | every spin leg held 17-499 passes in the window, 82.2-96.8 % | Rejected: fails I-1. The limiter gate is load-bearing |
| C1 + D-4 (`LAG_HOLD` 86) | — | rocking 13 / 0 / 3 | Not taken: more faults |

#### 4.9.7 The measure of benefit (for Stephen; P5)

The model's central parameters unless marked; refit e90_L18=52 Lh=0.00085; adverse e90_L18=53 Tnoise=0.4 Iz=0.42.
"Today" is quoted from §5 / §7 Q1 unless re-run. The D-1..D-3 column was re-run for every row below. Commands are in
§9.

| What a user sees | Today | D-1..D-3 | **D-1..D-3 + D-5** | Standing |
|---|---|---|---|---|
| 4 N·m on 1.0-2.0 s, then released: speed over the next 1.5 s, L / R | 83.9 / 82.9 % | 40.4 / 41.0 %: stalls at 27 A, path 66 ‰ | **99.9 / 100.0 %**, no path limiting, 3 set-backs | MODELLED |
| The same at the refit / at adverse | — | 74.0 / 74.2 % / 64.9 / 65.0 % | **99.9 / 100.0 % / 100.0 / 100.0 %** | MODELLED |
| Spin legs (all ten), central / refit / adverse | 57-94 % (MEASURED) | 99.6-100 %, no hold, no path limiting | **Identical, digit for digit**: clean at all three sets | MODELLED |
| Duty swing / err_pk while spinning | 803-1,647 / 84-113 (MEASURED) | 15-184 / 67-70; adverse 53-544 / 67-76 | Identical | MODELLED |
| Current, schedule against legacy at equal speed | — | 2.5-4.4× less | Identical | MODELLED (ratio) |
| Unloaded current | — | 0.04 / 0.09 / 0.13 A | Identical | DERIVED (acts only at a limiter) + MODELLED |
| One-sided load at power 13, L / R | 1 N·m 98.6 / 99.3; 2: 61.8 / 61.5; 4: 7.8 / 12.1 % | 1: 99.0 / 100; 2: 99.4 / 100; 4: 99.6 / 100 % at 12.4 A | 1: 99.0 / 100; **2: 99.2 / 100 (−0.2)**; 4: 99.6 / 100 % at 12.1 A | MODELLED |
| Where the field gives way | at 0.05-0.14 A (MEASURED) | 8 N·m (97 N): 25.2 / 25.7 %, 27 A, 1,050 limit frames | **8 N·m: 99.9 / 100 %**, 21.2 A mean, 22.7 A peak, no limit frame in the window. The give-way load is now above 8 N·m | MODELLED; where above 8 N·m UNKNOWN (not searched) |
| Ramp at 3,000 mm/s², arrival / prediction | 696 / 320 ms (MEASURED) | 322 / 321 ms | Identical | MODELLED |
| Ramp at 200 mm/s², FlySky; SPINSYM | as §5 | UNKNOWN | UNKNOWN (unchanged) | UNKNOWN |

**The one row that moves the wrong way.** A 2 N·m load drops from 99.4 to 99.2 % (`step`), and in `release` from 99.8
to 99.7 %. That is 0.16 of a hall tick over the 1.5 s window. It comes from one set-back on the load's current
transient (LEFT phase mean 8.32 → 8.69 A). It is reported, not hidden: the plan's "no row may get worse" is not met to
the letter.

**The obstacle grid** (`block`, 16 contacts per cell, the session's 2 A limit). Each cell reads latched / rocked 7.7 s /
lag fault, then the contact-to-latch median and range in ms:

| Obstacle | Parameters | Today | D-1..D-3 | **D-1..D-3 + D-5** |
|---|---|---|---|---|
| Solid, 50,000 N/m | central | 15 / 0 / 1; 1,023 (1,004-1,620) | 14 / 0 / 2; 1,005 (987-1,102) (re-run) | **15 / 0 / 1; 1,011 (1,011-1,075)** |
| Solid, 50,000 N/m | refit | — | 14 / 1 / 1; 1,030 (1,021-1,139) | **15 / 0 / 1; 1,011 (1,010-2,030)** |
| Rocking, 1,000 N/m | central | 10 / 5 / 1; 1,072 (1,055-1,157) | 8 / 7 / 1; 1,062 (1,045-1,124) (re-run) | **15 / 0 / 1; 1,092 (1,080-1,923)** |
| Rocking, 1,000 N/m | refit | 9 / 6 / 1; 1,093 (1,081-3,563) | 6 / 6 / 4; 1,082 (1,075-1,450) | **15 / 0 / 1; 1,104 (1,083-2,003)** |
| Rocking, 3,000 N/m | central | — | 10 / 5 / 1; 1,025 (1,010-1,975) | **16 / 0 / 0; 1,047 (1,042-2,647)** |
| Negative: D-5a without D-5b, solid | central | — | — | 0 / 15 / 1: never latches |

- **Every cell is no worse than D-1..D-3.** More latched, fewer rocked, and faults equal or fewer (1 / 1 / 1 / 1 / 0
  against 2 / 1 / 1 / 4 / 1).
- The longer latches (to 2.6 s after contact) come on contacts that rocked through several ticks first. The stand after
  the last tick stays 1,000-1,055 ms.

**The cost (P13; estimated from the sketch: the build counts from the compiler).** Starting from §4.4: cog 53 free and
LUT 41 free after D-1..D-3.

| Part | Cog longs | LUT longs | Time | ABI |
|---|---|---|---|---|
| D-5a `holdGate`: one CALL replaces one CMPS | 0 | +16 | ~+16 clocks per drive pass; ~+38 on a limited, set-back pass; 0 per frame | none |
| `LAG_LIM` (an immediate) | 0 | 0 | 0 | none |
| D-3's limiter test, shared through Z | 0 | up to −3 | — | — |
| D-5b (Spin2, front cog) | — | — | one compare and one assignment per 1 ms front pass | +1 Spin2-only VAR long per motor (`blockedLimSeen`, beside `blockedPos` `:7427`, after every PASM-addressed run) |
| **With D-1..D-3** | **+2 (53 free)** | **+27-30 (25-28 free)** | ~22 per frame (D-2) + 16-38 per pass | **no params or status long**; `DRVR_*_LONGS_COUNT` unchanged |

Clock basis: CALL and RET take 4 clocks in cog/LUT (`p2kbPasm2Call`, `p2kbPasm2Ret`), and ALU instructions take 2
(`p2kbPasm2Testb`, `p2kbPasm2Cmpm`). `_RET_`'s cost is taken as RET's: UNVERIFIED. The pass's extra clocks land in that
frame's window, which `tools/pasm_equiv`'s frame-budget report measures in the build.

#### 4.9.8 The falsifier

**The claim:** the modelled benefit comes from where the held field sits relative to the torque peak. Each rival below
makes a prediction the model can test.

- **R-a: any set-back breaks the stall chain (the decay, the path limiter), wherever it lands.**
  - It predicts the benefit at every `LAG_LIM` below 100.
  - The sweep (`release ... d5=1 lag_lim=N`) gives 99.9 / 100.0 % at 21, 43, 53, 64 and 75; 88.6 / 88.7 % at 90;
    57.7 / 57.6 % at 97; 40.4 / 41.0 % at 100.
  - At 90 and 97 the field is set back 56 and 53 times and still loses. **Excluded.**
- **R-b: the benefit is leaving D-2's boost band (lag ≥ `LAG_SOFT`), not the torque angle.**
  - It predicts that a hold at 75 with the boost acting at it loses, and a hold at 90 with the boost lifted above it
    wins.
  - Hold 75 with `lag_soft=70` gives 99.9 / 100.0 %; the control (D-1..D-3 with `lag_soft=70`) gives 49.7 / 49.7 %.
  - Hold 90 with `lag_soft=95` gives 93.0 / 93.2 %; the control gives 37.7 / 35.0 %.
  - The boost accounts for at most ~4.5 points at 90. **Excluded as the carrier.**
- **R-c: the blocked count, not the hold, changes the obstacle outcome.**
  - The blocked count alone gives 9 / 6 / 1 on the rocking object, against D-1..D-3's 8 / 7 / 1. **Excluded.**
- **The positive test: move the peak instead of the hold.**
  - `e90_L18=70` puts the peak 14 counts nearer the hold. D-1..D-3 alone then gives 99.1 / 99.0 %.
- **Standing (D2).**
  - Inside the model the rivals are excluded. On the motor the peak's position rests on e90 and the winding inductance,
    which are FITTED (§3.3), not measured. So the hardware verdict is **"consistent with"**.
  - The benefit holds for any `LAG_LIM` from 21 to 75 and at both fits, so it does not depend on the peak sitting
    exactly where fitted.
  - No bench run is proposed. The §6 cells, with their load premises corrected in the build (R8), are where it is
    checked.

#### 4.9.9 Model changes (`DOCs/plans/servo-model/spin2_model.py`)

New parameters. Each defaults to today's behaviour, and `release` and `release acc_shift=16 dB=1 boost_shift=10 dC=1`
print 83.9 / 82.9 and 40.4 / 41.0 % before and after.
- `d5`: the limit hold.
- `lag_lim`: its lag, 64.
- `d5_back=0`: candidate C2. `d5_step=N`: C3. `d5_sticky=1`: C4.
- `blk_lim`: D-5b's count. It acts only in `block` mode.

Runs print `set-backs [L, R]` when there are any.

#### 4.9.10 Not checked

- The default 27 A limit on an obstacle: every `block` run uses the session's 2 A.
- The PL-55 ceiling, and the driver's phase-current estimate (the model folds back on the true current).
- Non-uniform hall sectors, and a lead write moving `err_` (the model's `err` has no offset). Both are DERIVED inside
  64's margin only.
- `fwdrev`, which the model lacks. I-7 is DERIVED from the source.
- The state precondition at `.justIncr` (never below SPIN_UP), which the build confirms in `jerkStep`.
- Rev A's coarser fold-back (R7).
- Where above 8 N·m the field now gives way.

#### 4.9.11 As built (DRIVER_REV 47, «#3655», 2026-10-02)

Three differences from the sketch above, each a correction found in the build:
- **The set-back is signed by `err_`, not by `drv_incr`.** A limited pass whose `jerkStep` takes the speed through
  zero changes `drv_incr`'s sign on that pass; the sketch's sign then moved the field 21 counts away from the rotor
  (pasm_equiv mutant m3, scenario `d5_reversal_crossing`). `lag_s` ≥ 64 is formed with `err_`'s sign, so that is the
  sign of the lag being taken back.
- **`lim_seen` is re-taken at any pass whose state was not SPIN_UP or AT_SPEED**, at the top of `gettgtincr`. Invariant:
  at `holdGate` the change in `duty_capped_ + foldback_cnt_` counts only frames run in SPIN_UP or AT_SPEED. Without it
  the PL-55 ceiling's clamps during a slow-down read as "a limiter acted" on the next speed-up's first pass, and D-3
  decayed the field once (mutant m1, scenario `d3_spin_dn_then_up`).
- **D-5b's limiter half counts only in SPIN_UP or AT_SPEED**, the states the limit hold acts in. In SPIN_DN the field
  is still held at `LAG_HOLD`, so `|err|` counts a stall there, and a ceiling clamping a slow-down is not a blocked
  wheel. The harness's mirror (`test_bench_dual` `blockWatch()`) follows the same rule.

Costs from the listing: cog 443 used / 53 free; LUT run image 486 / 26 free; +20 clocks per trim frame (D-2), +28 per
pass unlimited, +48 on a set-back pass; worst window 2,221 clocks, 61.1 % of the 160 MHz frame (budget 75 %).

### 4.10 — after the 6.1.0 visit: the blocked count, the transient faults («#3662», PL-179, PL-180)

**Status: DESIGN, phase 1 of 2 (cause and shape). No driver code is changed by this section.** It answers the 6.1.0
visit's F-1, F-2 and F-3 (`DOCs/analyses/bench/2026-10-02/VISIT-6.1.0-EVALUATION.md` §3.2, §3.4, §2.2, §4a, §8) and the
PL-181 watch question (§4.10.10). One part is a new driver behaviour (C4, §4.10.6), so it goes to Stephen with its
benefit before anything is built (P5).

Command shorthand for this section (`S=DOCs/plans/servo-model`, every run `python3 $S/spin2_model.py <mode> ...`):
- `CAL` = `pasm=1 v_dt=0.18 i_noise=3`, the model corrected to the PASM and calibrated to the stall (§4.10.2);
- `R46` = no drive flags (DRIVER_REV 46's drive); `R47` = `acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1` (as built);
- `FIX` = `R47 cap_lift=48 d5_sticky=1 blk_fix=1` (the recommended set: S-1, C4, F-a).

#### 4.10.1 Summary for Stephen

- **F-1, the blocked stop that did not latch. Cause: SETTLED.** At the 2 A test limit the current fold-back does not
  act on every pass. It acts in single frames, about 100-180 times a second on the bench (every 15-27 ms in the
  model). The blocked count's limiter half restarts on every 1 ms pass without one, so it never reaches 1,000 in a
  row. The driver's own counter shows it: in the ~9.5 s stall LEFT folded on 1,677 frames and RIGHT on 914
  (`EV_FOLDBACK` release values, `debug_261002-103634.log` seq 22-23). At most 18 % and 10 % of the front passes could
  have counted. §4.9.5's model latched because it folded on every frame
  (its fold read the true phase current, and that was over 2 A even at `duty_min`). The driver's fold reads the DC link
  against a threshold floored at duty 2,454 (§4.10.2).
- **F-2a, the lag fault at obstacle contact. Cause: consistent with, modelled.** Between two folds the field is not
  limited, so it walks back up from 64 towards `LAG_HOLD`. That walk crosses |err| 82..88, where one hall tick against
  the field reads 125 or more: the fault lattice of §4.9.4, which D-5 meant the field to avoid. The bench's COAST stand
  read RIGHT `o_e` −81 to −87 and LEFT `e` 82-84. In the model, a rocking obstacle gives **7 lag faults in 16 contacts
  under DRIVER_REV 47, against 1 under DRIVER_REV 46**.
- **F-2b, the FlySky reversal fault. Cause: NOT established. The model does not reproduce it.**
  - D-5 plays no part: a slow-down is SPIN_DN or SLOW_TO_CHG, where the limit hold does not act, and the model's
    numbers are identical with it on and off.
  - The evaluation's hypothesis that D-2 and D-5 act against each other in a reversal is refuted.
  - The modelled exposure is lower in REV 47 than in REV 46.
  - The fault's last step is the same lattice (r_err 77 then 125, with `r_pos` 146 → 145).
  - No driver change is designed for it. The next drive's hard reversal is its reading.
- **F-3, the slow-down current kick. Cause: consistent with, modelled.** On a slow-down the PL-55 ceiling holds the
  duty under what the wheel needs, so the lag climbs to `LAG_SOFT`. There the ceiling lifts and D-2's boost starts at
  the same moment, from a clamped duty. D-2 alone takes the modelled 80 → 20 kick from +52 to +99 mV. D-5 changes no
  digit.
- **The fix: three separable parts.**
  - **F-a, front cog (Spin2).** The blocked count's limiter half becomes *sticky*: once a limiter has acted with no
    hall tick since, every pass counts until the next tick. One limiter action is enough, whatever the pattern.
  - **C4, driver (PASM, a new behaviour).** Once the limit hold has set the field back, it stays the hold until the
    rotor ticks forward. The field then never walks back into the fault window while the wheel is at its limit.
  - **S-1, driver (one immediate).** The PL-55 ceiling lifts at `SERVO_SETPOINT` (48) instead of `LAG_SOFT` (80).
- **Benefit (MODELLED, CAL; details in §4.10.8).**
  - Blocked on a solid object: a protective stop 1,000-1,050 ms after the last tick on 15 of 16 contacts, where
    DRIVER_REV 47 never stops.
  - Rocking obstacle: lag faults 7 → 0 of 16, and 15 of 16 latched.
  - The 80 → 20 kick: +115 / +105 → +52 / +52 mV.
  - Every §5 row: identical, or better by 0.1 point.
- **Cost (ESTIMATE): no ABI change.** F-a: +1 Spin2-only VAR long per motor. C4: about +12 LUT longs (26 → ~14 free),
  +3 cog longs (53 → 50) and +8-16 clocks per drive pass. S-1: nothing.
- **RULED (STEPHEN 2026-10-02, *"yes, a"*): build all three** (F-a, C4, S-1).
- **Recommendation: all three.**
  - F-a is the ⛔ fix.
  - C4 is needed with it. F-a alone still faults on 4 of 16 rocking contacts before its latch, and C4 alone never latches.
  - S-1 costs nothing and clears F-3.

#### 4.10.2 The model, corrected to the PASM

Every correction below is off by default (`pasm=0`), so every earlier command reproduces its numbers. The arbiter's
must-not-change input, `block acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1`, printed the same 15 lines before
the edit and after it. `legs` and `release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1` were also diffed against a
copy of the original file, with no difference.

| `pasm=1` | The PASM (authority) | What the model did |
|---|---|---|
| (a) **the fold-back**: a frame folds when the whole-mV net DC-link reading is above `(max(duty, duty_floor) × k) >> 16`. k = 3 × amps × 150 mV/A × 65,536 / (16 × 6,136) = 600 at 2 A, and the floor is 2,454 (m = 0.1) | `:8000-8033`, `currentLimitK()` `:6304-6321`, `setFoldLimit()` `:6323-6344` | folded on `hypot(id, iq) > i_limit`. Its stalled wheel drew 2.66 A at `duty_min`, so it folded on every frame. That is the `limited 53,886-56,311` of the must-not-change run |
| (b) **the PL-55 ceiling**: in SPIN_DN / SLOW_TO_CHG, `duty_cap = duty0 × |drv_incr| / incr0` unless the pass's `lag_s` ≥ `LAG_SOFT`. `duty0` and `incr0` are taken on the pass the state first turns down | `:7798-7817`, `:8985-8991` | no ceiling (§4.9.10 "not checked") |
| (c) `lim_seen` re-taken when the previous pass's state was neither SPIN_UP nor AT_SPEED | `gettgtincr` `:8763-8766` | no re-take (the build's mutant m1) |
| (d) the blocked count's limiter half only in SPIN_UP / AT_SPEED | `bFrontProtect()` `:2907` | also in SPIN_DN |
| (e) the set-back signed by `err_` | `holdGate` `:8842` | signed by `drv_incr` |
| (f) `fwdrev` follows the field's last move | `.ctlMotor` `:7967-7968` | fixed per run. The model's two directions' e90 are mirror fits, so at a flip its reading moves 128 − 2·e90 ≈ 12 counts where the driver's moves 2L (29 at L = 20.5°). **A model limit**, met only when a reversal crosses zero |

Also under `pasm=1`: a wheel at rest is modelled as a coasting, unfaultable bridge (`:7983`). And the 82..88 window
is counted in the driver's integer reading. `SAR 24` floors, so on the negative side a real lag of 81.4 already reads
−82 and faults on a tick. **§4.9.4's 82.3-88.3 band is the positive side only; in integer readings it is |err| 82..88
on both sides** (DERIVED; the model's fault context below shows −82 → −125).

**Two physical parameters, FITTED.**
- **`v_dt` = 0.18 V.** This is the bridge's dead-time voltage, opposing the phase current; ke is refitted with it, so
  the 20×10⁶ ladder point keeps 170 per 10⁶.
  - It is fitted to one bench reading: the 2 A stall's duty of 2,054-2,378 (COAST trace `d`, `k` 700-2,975). The
    model gives 1,939-2,166 (`block ob_n=16 ob_k=50000 R47 CAL diag=1`).
  - A reading it was not fitted to agrees. The wheels-up ladder needs 475 duty counts above proportional (80×10⁶
    12,453, 20×10⁶ 3,469; `debug_261002-100025.log` seq 16_712, 16_717), which is 0.18 V at 18.5 V.
- **`i_noise` = 3 mV.** The DC-link reading's jitter, matching the stand's raw `i` of 22-29.

**The calibration against the COAST trial.**

| COAST trial, 2 A | MEASURED | MODELLED, CAL (`block ob_n=16 ob_k=50000 [R46/R47] CAL diag=1`) |
|---|---|---|
| DRIVER_REV 46: the stop | stand 1,183 / 1,092 ms (2026-09-30 seq 362) | 15 of 16 latched, stand 1,000-1,051 ms (the model runs ~100 ms short, as in §7 Q1) |
| DRIVER_REV 47: the stop | none in 9.2 s (seq 327) | **0 of 16 latched**, 15 rocked unlatched for 7.8 s, 1 lag fault at contact |
| REV 47: |err| over the stand | LEFT 64-84; RIGHT up to 87 | 64..83 (one contact 22..108) |
| REV 47: duty over the stand | 2,054-2,378 (LEFT) | 1,939-2,166 |
| REV 47: fold frames per second | 176 LEFT, 96 RIGHT | 61-77 |

The model folds less often than the bench, so it under-states how often the limiter half could count: the bench's 18 %
is the stronger evidence.

#### 4.10.3 F-1: why the blocked count never reached 1,000

**The mechanism (MODELLED, CAL; `diag` lines of `block ob_n=16 ob_k=50000 R47 CAL diag=1`):**
1. On a limited pass D-5 sets the field back to 64, and the trim, at |err| − 48 = 16, lifts the duty by about 1/65,536 of
   itself per frame.
2. A fold takes 1/64 of the duty. The trim needs ~1,000 frames (23 ms) to win it back, so the next fold waits.
3. Between folds no limiter acts, so the hold is `LAG_HOLD` and the field advances again. `jerkStep`'s lag gate is open
   below `LAG_SOFT`, so the generator even re-accelerates it. The lag climbs from 64 to 80-84, where D-2's boost lifts
   the duty to the next fold.
4. Result per stand: **a limiter on 6.1-7.2 % of the front passes, never on more than 2 in a row, with gaps of 16-27
   passes**, and |err| ≥ `LAG_SOFT` on 1-7 % of passes. The count's longest run was 108 passes in all 16 contacts.

**The separating reading (SETTLED).** §4.9.5's premise ("a limiter acts there on every pass") predicts a fold-back
count rising at least once per front pass: ~9,500 over the 9.5 s stall. The driver's counter rose 1,677 (LEFT) and
914 (RIGHT) in total. In the model, the same flags with only the fold's criterion switched (`pasm=0` → `pasm=1`, no
`v_dt`) take the stall from 53,886-56,311 limited frames in ~1.2 s (all 6 contacts latched) to 1,382-2,123 in 7.8 s
(none of 3 latched; a limiter on 6.0 % of passes, longest run 1). With CAL it is ~560 in 7.8 s.

**Why the |err| half does not cover the gaps.** The lag reaches 80 only at the top of each walk: its stand range is
64..83 in the model and 64-84 on the bench. It cannot count a pass at 64-79.

#### 4.10.4 F-2: the two lag faults

**(a) At obstacle contact (BRAKE trial, RIGHT): the field walks through the window between folds. Consistent with,
MODELLED.**
- **The bench.**
  - In the COAST stand the RIGHT reading sat at −81..−87 several times: `o_e` −87 (`k` 675), −83 (750), −81 (1,525).
    LEFT read 82-84 (`k` 1,450, 1,575, 1,600, 1,800). That is inside the band where a tick against the field faults.
  - The COAST rotor did not rock. In the BRAKE trial it did: RIGHT `o_e` −71 at `k` 705, re-synced by `k` 721, and
    faulted at −125 (`k` 775).
- **The model, one rocking contact** (`block ob_n=1 ob_x=0.152521 ob_k=1000 R47 CAL diag=1`, its printed fault
  context).
  - RIGHT, in SPIN_UP: its 120th set-back takes the reading to −64, and with no limiter after it the reading walks
    −64 → −82 over 16 ms at duty ~1,950-2,010.
  - The spring pushes the rotor one sector back: −125. Lag fault.
- **The model, the grid** (16 contacts each; latched / rocked unlatched / lag fault):

| Obstacle | R46 | R47 | R47 + F-a | R47 + C4 | R47 + F-a + C4 (= FIX less S-1) | FIX |
|---|---|---|---|---|---|---|
| Solid, 50,000 N/m | 15 / 0 / 1 | 0 / 15 / 1 | 15 / 0 / 1 | 0 / 15 / 1 | 15 / 0 / 1 | 15 / 0 / 1 |
| Rocking, 1,000 N/m | 11 / 4 / 1 | **0 / 9 / 7** | 10 / 2 / 4 | 0 / 14 / 2 | **15 / 1 / 0** | **15 / 1 / 0** |
| Rocking, 3,000 N/m | 10 / 5 / 1 | 0 / 13 / 3 | 13 / 1 / 2 | — | 15 / 1 / 0 | 15 / 1 / 0 |
| Rocking 1,000: time |err| read 82..88, all contacts; ticks against the field taken from it (a fault, or a miss by under a count at the reading's floor) | 4,312 ms; 1 | 1,187 ms; 11 | 644 ms; 8 | 22 ms; 2 | 1 ms; 0 | 1 ms; 0 |

- **DRIVER_REV 46 spends more time in the window but takes fewer ticks from it.** Its field parks at 100, outside the
  window, and crosses the window only while walking up after a *forward* tick. D-5's field drifts up while the spring
  is pressing the rotor *back*. The ticks that fault are the backward ones. This explanation is consistent with the
  numbers, not proven by them.
- **The one solid-object fault** is the same in every column, R46 included. It is the contact transit §4.9.4 already
  carries: AT_SPEED, the field walks 62 → 84 before any limiter acts, then one rebound tick takes it to 126 (the
  `FIX diag=1` fault context). Nothing here changes it.

**(b) The FlySky reversal (RIGHT, 31,942 / 32,134 ms): NOT reproduced; cause not established.**
- **What the bench shows** (`debug_261002-104014.log` RC-TEL, field order in its `RC-FIELDS` line).
  - From 31,550 ms RIGHT is in SLOW_TO_CHG (`r_dcs` 5), then SPIN_DN (4).
  - Its rotor runs at about half its field's speed: `r_tps` 50 against ~103 tps of field.
  - `r_err` sits at 90-101 for ~300 ms, at duty up to 10,623 and up to 4.07 A.
  - After the re-sync (`r_err` 13) the field walks up again: 59, 93, 62, 77, then **125 at 32,150 ms, with `r_pos`
    146 → 145, a tick against the field**. A fault from 77 needs the reading to have reached 82..88 first (DERIVED;
    that sample is not in the 40 ms record).
- **What the model shows** (`reversal [R46 / ... / FIX] CAL`): 15 slow-downs or reversals from −175 tps per run (the
  logged stick sequence, a full reversal, a stop), at the knobs' rates (accel 1,000-2,900, decel 1,000-2,600). No run
  takes a tick against the field, so none faults. The exposure:

| Drive (`reversal <flags> CAL`) | lag faults | |err| in 82..88, all 15, both wheels | held passes | lag_pk | Iph peak |
|---|---|---|---|---|---|
| R46 | 0 / 15 | 3,541 ms | 1,307 | 103 | 21.6 A |
| D-1 alone (`acc_shift=16`) | 0 / 15 | 1,102 ms | 142 | 102 | 16.3 A |
| D-1 + D-2 | 0 / 15 | 887 ms | 30 | 100 | 23.0 A |
| R47 | 0 / 15 | 897 ms | 36 | 101 | 28.7 A |
| R47 without D-2 (`dB=0`) | 0 / 15 | 1,090 ms | 316 | 102 | 18.5 A |
| R47 without D-5 (`d5=0`) | 0 / 15 | 897 ms (identical to R47) | 36 | 101 | 28.7 A |
| R47 + S-1, and FIX | 0 / 15 | 626 ms | 37 | 101 | 28.7 A |

- **D-5 changes no digit**, as it cannot: the limit hold acts only in SPIN_UP / AT_SPEED (`holdGate` `:8834`), and a
  slow-down is SPIN_DN / SLOW_TO_CHG. So "D-2 and D-5 act against each other on a reversal" (evaluation §4a) is
  refuted.
- **The modelled exposure falls from DRIVER_REV 46 to 47**, so the model gives no reason to attribute the fault to
  D-1..D-5.
- **The model does not make the bench's excursion.** For the logged sequence, R47's RIGHT peaks at lag 96 and 0.47 A
  of DC link; the bench sat at 100 with up to 4.07 A. The bench platform slowed far faster than the model's straight
  drive. That load is outside the model: candidates are a caster swivelling at the direction change, or yaw. Its
  measurement is the next visit's hard reversal (evaluation §5 item 4).
- C4 does not apply here (SPIN_DN). S-1 lowers the window time by 30 %.

#### 4.10.5 F-3: the slow-down kick

**Readings** (`stepdn <flags> CAL`, wheels up). Columns: 80 → 20×10⁶ lag_pk, held passes, ceiling frames, boost
frames; that step's DC-link peak over the destination's steady, L / R; the same for 40 → 20.

| Drive | 80 → 20: lag / held / cap / boost | 80 → 20 kick | 40 → 20 kick |
|---|---|---|---|
| MEASURED, DRIVER_REV 47 (dual-a seq 16_718-16_719, 17_291) | 101 / 26 / 367 / — | +79 / +89 mV | +25 mV, cap 139 |
| MEASURED, 2026-09-22 ladder (driver 4) | 84-92 / — / — / — | 0-19 mV | — |
| R46 | 100-101 / 22, 16 / 2,978 / 0 | +50 / +50 mV | +42 / +35 |
| D-1 alone | 101 / 36, 29 / 935 / 0 | +52 / +52 | +21 / +22 |
| D-1 + D-2 | 101 / 13, 10 / 952 / 3,477 | **+99 / +94** | +52 / +44 |
| R47 | 101 / 13, 10 / 952 / 3,518 | **+115 / +105** | +52 / +44 |
| R47 without D-2 | 101 / 42, 34 / 935 / 0 | +52 / +52 | +22 / +23 |
| R47 without D-5 | identical to R47 | +115 / +105 | +52 / +44 |
| R47, boost only in SPIN_UP / AT_SPEED (`boost_run=1`, run without `i_noise`, which acts only on a fold) | 101 / 21, 19 / 935 / 734 | +140 / +134 | +63 / +53 |
| **R47 + S-1** (`cap_lift=48`) | 95 / 0 / 66 / 2,150 | **+52 / +52** | +30 / +27 |
| R47, no ceiling at all (`cap_lift=-200`) | 75 / 0 / 0 / 0 | +52 / +52 | +11 / +10 |

The up-step (20 → 80) reads +5 mV in every row (bench +3).

- **The cause (consistent with, MODELLED).**
  1. The ceiling's line, `duty0 × v / v0`, has no room for the part of the duty that does not scale with speed: the
     dead-time voltage and friction, 475 counts on this ladder.
  2. So on the way down it clamps the duty under the need (952 frames), and the rotor falls behind until the lag
     reaches `LAG_SOFT`.
  3. At that pass the ceiling lifts and D-2's boost starts, on a duty the clamp has held low and with the lag already
     at 80-101. The boost drives the current up: the kick.
- **The separating readings.**
  - Switching D-2 alone moves the kick 52 ↔ 99-115 mV.
  - Switching D-5 moves nothing.
  - Lifting the ceiling at 48, or removing it, returns the kick to D-1's level whether D-2 is on or not.
  - On the bench, only the steps that cap (`tr_cap` 367 and 139) kick; the up-steps neither cap nor kick.
- **Where the model stands against the bench.** Its absolute kick runs 30-50 mV high: R46 gives +50 against the old
  ladder's 0-19, and R47 +105-115 against 79-89. The increment D-2 adds (+47-63 mV) matches the bench's (+60-89).
- **PL-55's own case**, a stop from 147×10⁶ (`stepdn`'s last row), phase-current peak: R46 2.33-2.34 A, R47 2.32-2.36,
  S-1 2.34-2.38, no ceiling 2.50-2.56. The model never draws PL-55's >10 A (that was the pre-R18.4 servo), so it cannot
  price the ceiling's protection. It can only show that S-1 keeps the ceiling in force where it binds today.

#### 4.10.6 The fix

**F-a · the blocked count counts from the first limiter action after the last tick (front cog, `bFrontProtect()`).**
- **Mechanism.**
  - A per-motor flag, `bLimSinceTick`, is set on a front pass with no hall tick on which a limiter acted:
    `duty_capped + foldback_frames` changed, in SPIN_UP / AT_SPEED.
  - It is cleared by a hall tick, a zero command, or a state other than SPIN_UP / AT_SPEED.
  - The count's limiter half reads the flag instead of this pass's change. The `|err| ≥ LAG_SOFT` half is unchanged
    (a SPIN_DN stall at `LAG_HOLD`).
- **Invariant (I-8), by construction.**
  - A commanded wheel in SPIN_UP / AT_SPEED that a limiter has acted on since its last hall tick is counted on every
    front pass until it ticks.
  - So it latches exactly `BLOCKED_PASSES` passes after the first such limiter action, **for any pattern of the
    limiter's later actions, including none**. The stand (last tick to latch) is therefore at least 1,000 ms, and at
    most 1,000 ms plus the time to the first limiter action.
- **What it cannot latch falsely (DERIVED).** A count needs 1,000 ms with no tick. A wheel that is free to turn ticks
  once its field has moved one sector further than the rotor. Only two kinds of field move less than a sector per
  second (`|drv_incr|` < 42.67 × 2³² / 256 / 1,913 ≈ 374,000 per pass, 0.23 % of full power):
  - one D-3 has decayed at a limiter, which is a wheel at its limit that does not move: blocked by definition;
  - one the steering object has scaled to `DRV_INCR_FLOOR`, which needs a short partner. Such a partner carries the
    flag only if a limiter acted on it too, since its own last tick.
- **Sketch** (the build counts and checks it; local `bRun` added):

```
    nowPos := pos
    nowLimSum := duty_capped + foldback_frames
    bRun := (drv_state == DCS_SPIN_UP) or (drv_state == DCS_AT_SPEED)
    if (nowPos <> blockedPos) or ((targetIncre & !SYNC_BIT) == 0) or (bRun == FALSE)
        bLimSinceTick := FALSE                          ' a tick, no drive, or not running: clear (I-8)
    elseif nowLimSum <> blockedLimiterSum
        bLimSinceTick := TRUE                           ' a limiter acted with no tick since: every pass counts until one
    if ((targetIncre & !SYNC_BIT) <> 0) and ((abs(err) >= LAG_SOFT) or bLimSinceTick) and (nowPos == blockedPos) and ((drv_state == DCS_SPIN_UP) or (drv_state == DCS_AT_SPEED) or (drv_state == DCS_SPIN_DN))
        blockedPasses++
```

- **Where it lands.**
  - `bLimSinceTick` is one Spin2-only VAR long beside `blockedLimiterSum` (`:7471`), after every PASM-addressed run:
    **no ABI change**.
  - It is cleared with `blockedPasses` at `:2928`, `:2935` and `:4525-4527`.
  - The `''` doc at `:2870-2872` and the comment at `:2899-2904` change.
- **The harness's mirror** (`src/test_bench_dual.spin2`, read-only here; phase 2 changes it with the driver, or
  BLKSTOP's count bounds fail a correct latch):
  - a VAR `blkLimTick[INST_MOTORS]` beside `blkLimPrev` (`:17013`), cleared at `:20954-20956` and `:21039-21046`;
  - in `blockWatch()`, the tick branch (`:21061-21065`) clears it;
  - `bLimited` (`:21059`) sets it while running, and a state other than SPIN_UP / AT_SPEED clears it;
  - the count test (`:21066`) reads `bLimited or blkLimTick[slotIdx]`;
  - the texts naming the rule: `:736`, `:21004-21014`, `:16282-16286`, `:16318-16323`.
  - `BLK_COUNT_LO_MS` / `BLK_COUNT_HI_MS` stand: the count still lands `BLOCKED_PASSES` after its own start.
- **Cost:** +1 VAR long per motor. On each 1 ms front pass, one comparison chain and one assignment more (ESTIMATE;
  the build reads the front loop's late-pass count).

**C4 · the limit hold stays armed until the rotor ticks forward (driver, `holdGate`). A new driver behaviour (P5).**
- **Mechanism.**
  - On the pass the limit hold sets the field back, `holdGate` arms: `lim_pos := pos_`.
  - While armed, every running pass takes the limit hold: the field advances only below `LAG_LIM`, and is set back to
    it when past, limiter or not.
  - It disarms when the rotor has ticked forward past `lim_pos` in the field's direction, or the state leaves
    SPIN_UP / AT_SPEED.
  - D-3's decay still needs a limiter on the pass: Z is unchanged, so an armed pass without one does not give way.
- **Invariant (I-9).** From a wheel's first set-back until it ticks forward, its field stays at most `LAG_LIM` ahead of
  the rotor's sector. A parked field read k ticks back reads 64 + 42.7k (wrapped), never 82..88, so **no tick against
  the field can fault while the wheel is at its limit**. This is I-5 kept between folds, which D-5 assumed and the
  intermittent fold broke. It does not cover the contact transit before the first set-back (§4.10.4 (a)).
- **Sketch** (replaces `holdGate`'s head, `:8831-8836`; the set-back `:8837-8850` is unchanged except the two arming
  lines; flags as the as-built comments read them: CMP, CMPS and TESTB with WC write C only, NEG and TJZ write no flag
  — `p2kbPasm2Cmps`, `p2kbPasm2Neg`, `p2kbPasm2Tjz`):

```
holdGate        mov     tmpX, duty_capped_
                add     tmpX, foldback_cnt_
                cmp     tmpX, lim_seen              wz  ' Z: no limiter acted since the previous pass. Z survives to RET
                cmp     drv_state_, #DCS_SPIN_DN    wc  ' C: SPIN_UP or AT_SPEED
    if_nc       mov     lim_arm, #0                     ' PL-179 C4: any other state disarms
    if_nc       jmp     #.today
                tjz     lim_arm, #.noArm                ' armed: has the rotor ticked forward past the armed sector?
                mov     tmpX, pos_
                sub     tmpX, lim_pos
                testb   drv_incr, #31               wc
    if_c        neg     tmpX                            '  ticks forward, in the field's direction
                cmps    tmpX, #1                    wc  ' NC: one or more forward
    if_nc       mov     lim_arm, #0                     '  the load gave way: disarm
.noArm  if_z    tjz     lim_arm, #.today                ' no limiter now and not armed: today's LAG_HOLD gate
.limHold        cmps    lag_s, #LAG_LIM             wc  ' (unchanged from here: the set-back)
    if_c        ret
                ...                                     ' :8839-8849 as built
                mov     lim_pos, pos_                   ' C4: armed at this sector
                mov     lim_arm, #1
    _ret_       modc    _clr                        wc
.today  _ret_   cmps    lag_s, #LAG_HOLD            wc
```

- `driveFromRest` (LUT, `:9046`) and `.clearRun` (cog, `:8100`, the e-stop and fault-reset path) also zero `lim_arm`,
  so no drive starts armed. Any pass outside SPIN_UP / AT_SPEED disarms as well.
- **Cost (ESTIMATE).**
  - LUT: +12 longs (`holdGate` 16 → 27, `driveFromRest` +1), so the run image goes 486 → ~498 of 512.
  - Cog: +2 registers (`lim_pos`, `lim_arm`) and +1 instruction in `.clearRun`, 53 → 50 free.
  - Time: +8 clocks per unarmed running pass and +16 per armed one (2 per ALU instruction; TJZ 2, or 4 taken). That
    is under 1 % of the 2,727-clock window; the build reads `tools/pasm_equiv`'s budget.
- **ABI:** none.
- **Why §4.9.6 rejected C4, and why that no longer holds.** It was rejected as "a register and a hall compare more, no
  modelled gain". That model folded on every frame, so its field never had a gap to walk through. Under the driver's
  own fold the gain is 7 → 0 rocking faults (with F-a), or 7 → 2 alone.

**S-1 · the PL-55 ceiling lifts once the rotor trails its running point (driver, one immediate).**
- **Mechanism.** At `:7804` `cmps lag_s, #LAG_SOFT wc` becomes `cmps lag_s, #SERVO_SETPOINT wc`.
- **Invariant (I-10).** The ramp-down ceiling binds only while the rotor is at or ahead of the servo's own point
  (lag_s < 48). That is the case PL-55 exists for: a rotor overrunning a slowing field. A slow-down whose load needs
  more motoring than steady running gets the trim at once. The lag no longer has to reach `LAG_SOFT`, D-2's threshold,
  to lift the ceiling, so the boost no longer starts on a clamped duty.
- **Cost:** none (an immediate). ABI: none.

#### 4.10.7 Candidates considered

| Candidate | Modelled (CAL) | Verdict |
|---|---|---|
| **F-b:** the count's limiter half alive while a limiter acted in the last 50 front passes (`blk_fix=2 blk_win=50`) | solid 15 / 0 / 1; rocking 1,000: 10 / 2 / 4; rocking 3,000: 13 / 1 / 2. The same as F-a | Viable, not recommended. It is correct only while the limiter's gap stays under the window. The model's gaps are 16-28 passes, the bench's are unmeasured, and the DC-link noise makes them unbounded in principle. F-a needs no bound |
| Count the held passes (`lag_held`) | — | Rejected, DERIVED. Without C4 a hold happens only on a limited pass, so it has the same gaps. With C4 a lead write that lowers `err_` under 64 still opens gaps (§4.9.5) |
| A lower `LAG_LIM` or `BLOCKED_PASSES` | — | Not licensed (evaluation §4a) |
| F-a alone, no C4 | rocking 1,000: 10 / 2 / 4 | Latches, but 4 of 16 contacts fault first |
| C4 alone, no F-a | solid 0 / 15 / 1; rocking 0 / 14 / 2 | Never latches: F-1 stands |
| S-2: D-2's boost only in SPIN_UP / AT_SPEED | 80 → 20 kick +140 / +134 mV | Rejected: worse. The boost then fires on the arrival pass, with the lag still high |
| Remove the PL-55 ceiling | 80 → 20 +52 mV; 40 → 20 +11 mV (S-1: +30); stop from 147×10⁶ 2.50-2.56 A against 2.32-2.38 | Not recommended. A little better on the small step, but the ceiling's own failure (>10 A stops) is outside the model, so removing it cannot be priced |

#### 4.10.8 The measure of benefit (for Stephen; P5)

MODELLED unless marked: the two-wheel model at its central parameters under CAL. Each cell is from the commands in
§4.10.12. The model's absolute currents run high (§5), so currents are compared within a row.

| What a user sees | DRIVER_REV 46 | DRIVER_REV 47 (as built) | **REV 47 + F-a + C4 + S-1** | Standing |
|---|---|---|---|---|
| Wheel against a wall at 2 A, COAST: does the platform stop itself? | yes: bench 1,092-1,183 ms after the last tick; model 1,000-1,051 ms | **no**: bench ran 9.2 s to the harness's timeout; model 0 of 16 | **yes**: 15 of 16, 1,000-1,050 ms after the last tick, 1,009-1,169 ms after contact | MEASURED (46, 47); MODELLED (fix) |
| The same against a yielding object (1,000 N/m): stopped / pushed on / lag fault, of 16 | 11 / 4 / 1 | **0 / 9 / 7** | **15 / 1 / 0**, 1,080-1,738 ms after contact | MODELLED |
| The same (3,000 N/m) | 10 / 5 / 1 | 0 / 13 / 3 | 15 / 1 / 0 | MODELLED |
| A lag fault at the moment of contact (solid object) | 1 of 16 | 1 of 16 | 1 of 16 (the contact transit: unchanged) | MODELLED; bench BRAKE: 0 (46) and 1 (47) of 1 |
| Wheels up, a sharp slow-down (80 → 20×10⁶): current kick over steady | +50 mV (model); 0-19 mV (bench, driver 4) | +115 / +105 mV (model); **79 / 89 mV (bench)** | **+52 / +52 mV** (≈ 0.35 A of DC link) | MODELLED; MEASURED where marked |
| Wheels up, 40 → 20×10⁶ kick | +42 / +35 mV | +52 / +44 mV (bench 25) | +30 / +27 mV | MODELLED |
| A stop from 89 % power: phase-current peak | 2.33-2.34 A | 2.32-2.36 A | 2.34-2.38 A (+1 %) | MODELLED; PL-55's >10 A case not reproducible: UNKNOWN |
| FlySky slow-downs and reversals: lag faults per 15 | 0 | 0 (bench: 1 in the drive) | 0 | MODELLED; the bench fault is not reproduced: **UNKNOWN** whether any variant changes it |
| The same: time the lag reads in the fault window (both wheels, 15 transients) | 3,541 ms | 897 ms | 626 ms | MODELLED |
| Spin legs (all nine): speed, err_pk, swing | — | 99.6-100.5 %, 68-76, 39-295 | **identical, digit for digit** | MODELLED (`design R47 CAL` against `design FIX CAL`) |
| One-sided load at power 13: 1 / 2 / 4 / 8 N·m, LEFT | — | 99.1 / 99.2 / 99.3 / 99.8 % | 99.1 / 99.2 / **99.4** / 99.8 % | MODELLED (`step`) |
| 4 N·m on 1.0-2.0 s, then released: speed after, L / R | — | 99.9 / 100.0 % | 99.9 / 100.0 % (identical but the set-back count) | MODELLED (`release`) |
| Ramps at 200 / 1,000 / 3,000 mm/s²: arrival against prediction | — | 1,800 / 1,800, 560 / 559, 322 / 321 ms | identical | MODELLED (`ramp`) |
| Wheels up, unloaded: duty, current | — | 10 / 20 / 37×10⁶: 0.04 / 0.07 / 0.13 A | identical | MODELLED (`wheelsup`) |

**No row gets worse.** The 4 N·m step is 0.1 point better. Every other §5 row under CAL is identical.

#### 4.10.9 Certification: each cell can fail

| Cell | Criterion | Its negative (this visit fails it) |
|---|---|---|
| **BLKSTOP / BLKLIMIT** (floor-obstacle, COAST and BRAKE trials) | latched; stand in BLK_STAND_LO (988) and up; the mirrored count (F-a's rule) 988-1,012 ms | COAST: `stop_by,TIMEOUT` after 9.2 s (`BM-BLOCK` seq 327) |
| **BLKWIN** (new; I-9) | after a stalled wheel's first limiter action, and while it has no hall tick, no `BM-TS` sample reads |e| or |o_e| in 82..88 | COAST trace: `o_e` −87 (`k` 675), −83 (750); `e` 82-84 (`k` 1,450-1,800) |
| **BLKFLT** (new) | the BRAKE trial latches with no `EV_FAULT` and no `RESYNC` | BRAKE: `EV_FAULT` RIGHT (seq 338), `RESYNC` (seq 336) |
| **TRKICK-A** (dual-a, as defined) | every transition's `tr_i_over` ≤ 50 mV | 79 / 89 mV on the four 80 → 20 steps (seq 16_718, 16_909, 17_100, 17_291) |
| **SPINRATE / RAMPARR** (floor-auto) | as defined; the regression guard for C4 and S-1, which touch the drive path | — (they passed on DRIVER_REV 47; a drop is the regression) |

The FlySky reversal has no cell: its cause is not established. The next drive's hard reversal, with the moment of any
fault asked for (evaluation §5 item 4), is a reading, not a certification.

#### 4.10.10 PL-181: does D-2 firing in calm running matter?

**It costs no speed. It does cost swing and current where the peaks cross 80 (MODELLED).**
- **Central parameters** (`design R47 CAL` against `design acc_shift=16 dC=1 d5=1 CAL`): err_pk 68-76, so the boost
  barely enters running.
  - Speed is identical (99.6-100.5 %).
  - The schedule legs are identical except MED −, where swing goes 136 → 221.
  - The legacy legs carry more swing (MED − 45 → 295) and current (0.60 → 0.76, model units).
- **The adverse corner** (`e90_L18=53 Tnoise=0.4 Iz=0.42`, the same pair): the slow legs' peaks reach the bench's
  79-90 (80-91 here).
  - With D-2 on, speed stays 98.7-100.8 % (off: 98.6-100 %), and the slow legs' err_pk sits a few counts lower
    (80-87 against 85-91).
  - The duty swing rises on the medium and brisk legs: schedule MED − 507 → 1,400 (2.8×), legacy MED − 110 → 883
    (8×), fixed BRISK − 195 → 402. The mean current rises with it (schedule MED − 0.16 → 0.27, legacy MED −
    0.52 → 0.84, model units).
  - The bench's schedule swings (95-539) lie inside the model's range with the boost on (74-1,400). The model does not
    say which leg of the bench it would match.
- **So:**
  - SPINHUNT's `err_pk` ≤ 76 fails on a boost that is harmless to speed.
  - The cost the floor would feel is a little current and duty ripple on medium spins, not lost speed.
  - Nothing in this section changes it. S-1 and C4 leave calm running identical.

#### 4.10.11 Not checked, and the model's limits

- **The rocking that faults.** The model makes it only from the spring obstacle. It makes none in a straight drive's
  slow-down, which is why F-2b is not reproduced.
- **The fold rate.** The model folds at 61-77 per second against the bench's 96-176. `i_noise` is uniform and
  per-frame; the board's noise spectrum is not modelled.
- **`v_dt`** is FITTED to the stall duty and checked against the ladder's offset only. It is applied only under CAL;
  the §5 numbers above it are without it.
- **The direction flip (f)** reads 12 counts where the driver reads 29 (§4.10.2). The only runs that flip are the full
  reversals, and their window time is a lower bound.
- **Not modelled:** the default 27 A limit on an obstacle; Rev A (5 mV/A); non-uniform hall sectors; a lead write
  moving `err_`.
- **The PASM sketches** are not assembled: the costs are ESTIMATE. The Spin2 sketch's front-pass time is not measured.
- The harness mirror's new rule is specified (§4.10.6), not written.

#### 4.10.12 Reproduce

```
S=DOCs/plans/servo-model; R47="acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1"; CAL="pasm=1 v_dt=0.18 i_noise=3"
python3 $S/spin2_model.py block acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1         # must-not-change: as before
python3 $S/spin2_model.py block ob_n=3 ob_k=50000 $R47 pasm=1 diag=1                          # F-1: fold criterion alone (v_dt 0)
python3 $S/spin2_model.py block ob_n=16 ob_k=50000 $CAL diag=1                               # R46 calibration
python3 $S/spin2_model.py block ob_n=16 ob_k=50000 $R47 $CAL diag=1                          # F-1 reproduced
python3 $S/spin2_model.py block ob_n=1 ob_x=0.152521 ob_k=1000 $R47 $CAL diag=1              # F-2a fault context
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 $R47 $CAL diag=1                           # and ob_k=3000; and with no flags (R46)
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 $R47 $CAL blk_fix=1 diag=1                 # F-a
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 $R47 $CAL blk_fix=2 blk_win=50             # F-b
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 $R47 $CAL d5_sticky=1 diag=1               # C4 alone
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 $R47 $CAL cap_lift=48 d5_sticky=1 blk_fix=1 diag=1   # FIX; ob_k=50000, 3000
python3 $S/spin2_model.py stepdn $R47 $CAL                                                   # F-3; drop dB=1 / d5=1; acc_shift=16 alone; no flags
python3 $S/spin2_model.py stepdn $R47 $CAL cap_lift=48                                       # S-1; cap_lift=-200 (no ceiling)
python3 $S/spin2_model.py stepdn acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 pasm=1 v_dt=0.18 boost_run=1   # S-2
python3 $S/spin2_model.py reversal $R47 $CAL                                                 # F-2b; and each variant of the table
python3 $S/spin2_model.py step|release|ramp|wheelsup|design $R47 $CAL                        # 4.10.8, against + cap_lift=48 d5_sticky=1 blk_fix=1
python3 $S/spin2_model.py design acc_shift=16 dC=1 d5=1 $CAL                                 # PL-181 (D-2 off); + e90_L18=53 Tnoise=0.4 Iz=0.42
```

### 4.11 — rough running above 175 ×10⁶ (PL-187)

**Status: DESIGN, Part A of «#3668» (the desk study). No driver code is changed by this section.** It answers PL-187
(HOLD-SPEED plan §1.7). In the 6.1.0 visit's `dual-limits` run, wheels up, Stephen heard the wheels at their highest
speeds sound gravelly, labour and vibrate hard, and suspected the drive was out of sync with the rotor's position. The
fix proposed here (T-1, §4.11.7) is a new driver behaviour, so it goes to Stephen with its benefit before anything is
built (P5).

- **Evidence:** `DOCs/analyses/bench/2026-10-02/debug_261002-101625.log` (DRIVER_REV 47), its LIMTOP segment (seq
  53-491). Cited by seq as `:seq` in this section; source lines are cited as `:line`.
- **Driver:** `src/isp_bldc_motor.spin2` at DRIVER_REV 48. Line numbers below are REV 48's. On this path REV 48 differs
  from the logged REV 47 only in `holdGate`'s C4 head (`:8879-8891`).
- **Harness:** `src/test_bench_dual.spin2`, read only.

Command shorthand (`S=DOCs/plans/servo-model`; every run is `python3 $S/spin2_model.py topspd ...` unless named):
- `CAL` and `R47` as in §4.10.
- `R48` = `R47 cap_lift=48 d5_sticky=1 blk_fix=1` (§4.10's FIX, as built).
- `R46` = no drive flags.
- `T1` = `R48 d5_fold_only=1`.
- `V20` = `top_v=21.3`, the model supply that reproduces this run's duty (§4.11.4), i.e. the session's pack at about
  20.5 V.
- `V18` = `top_v=19.2`, the same scaled to an 18.5 V pack (× 18.5 / 20.5).

#### 4.11.1 Summary for Stephen

- **What you heard is the drive's own reaction to running out of voltage. The motor is not losing its place.**
  - Above about 175 ×10⁶ (wheels up, on this pack) the motor needs more voltage than the battery gives, and the duty
    (the share of the battery's voltage the drive applies) reaches its ceiling.
  - From then on the drive treats that ceiling as a limit, exactly as it treats the current limit. It does the two
    things 6.1.0 added for a wheel stopped against an obstacle:
    - it stops the field (the rotating magnetic pull) running more than 90° ahead of the rotor, and pulls it back when
      it is further;
    - each time it does, it takes 1/64 off the field's speed.
- **At speed that is the wrong move.**
  - A motor at its voltage ceiling needs the field *further* ahead than 90° to keep its speed. The earlier driver ran
    this way, smoothly, up to 245 ×10⁶ at Visit 9.
  - So, about 20 times a second, the drive holds the field back for one step (15.5° of the electrical cycle at
    185 ×10⁶), sometimes pulls it back further, and slows it.
  - Each of those is a jolt of current: in the model, peaks of 11-16 A where steady running draws under 2 A. That is
    the gravel and the vibration.
  - The field's speed never settles. That is why the 185 rung timed out on all four wheel-directions.
- **What it is not.**
  - Not the PWM clipping its waveform. The drive caps the duty before it makes the waveform, and the waveform stayed 3
    counts inside its limits.
  - Not the hall sensors losing track. The driver's own hall checks counted no missed and no illegal transitions. The
    log's "skips" are the test instrument, which samples 500 times a second and cannot resolve 494 hall ticks a second
    (as at Visit 9).
  - Not the timing (the lead) being wrong at that speed. The same lead runs 175 ×10⁶ clean. In the model, changing the
    lead only moves the speed at which the ceiling is reached, and the roughness moves with the ceiling.
  - Not the motor slipping past its peak torque. The model shows that regime only far higher (205-245 ×10⁶) or under a
    heavy load.
- **It reaches full power, on two counts.**
  - On an 18.5 V pack, full power (165 ×10⁶) needs 102-104 % of the duty ceiling (worked out from this run's duty). The
    model runs it rough, at 96.5 % of the commanded speed.
  - On the floor it already happens on a full charge. In the FlySky drive the right wheel reached 96-99.6 % of the
    ceiling in full-power pivots. The drive was holding its field on 11 of 13 samples, and the field ran 4-8 % slow
    (measured).
- **The fix (T-1): the hold acts on the current limit only, not on the voltage ceiling.**
  - One rule changes in the driver. When only the voltage ceiling clamped the duty, the field keeps the allowance it had
    before 6.1.0: up to 140° ahead before it is held.
  - The 6.1.0 rule that the field gives way only at a limit stays.
  - The blocked-wheel stop is unchanged by construction: a stalled wheel reaches its current limit, not the voltage
    ceiling.
- **Benefit (modelled; currents compared within a row, as the model's absolute currents run high):**
  - 185 ×10⁶ wheels up settles in 0.4 s at 100 %. Its current ripple is 50 times smaller (0.05 A against 2.4-3.2 A).
  - Full power on an 18.5 V pack runs at 100 % and calm, instead of 96.5 % and rough.
  - Full power on a charged pack carries 4 N·m on one wheel (about 48 N at the tyre) at 100 %. Today's drive runs rough
    from 1 N·m (12 N).
  - Nothing else moves. The obstacle stops, the load steps, the spins and the slow-downs are identical digit for digit.
- **Cost (estimated): no change to the shared-memory layout.** One cog register (50 → 49 free), about 5 LUT longs
  (13 → 8 free), about 10 clocks per drive pass.
- **Decision for you (§4.11.9):** build T-1 into the 6.1.0 load. Recommendation: yes.
- **RULED (STEPHEN 2026-10-03, *"yes a"*): build T-1** — only the current fold-back triggers the limit hold; the duty
  ceiling alone no longer does.

#### 4.11.2 What the driver does at the duty ceiling, pass by pass

At 185 ×10⁶ the rung runs in SPIN_UP or AT_SPEED. The PL-55 ceiling binds only in SPIN_DN and SLOW_TO_CHG
(`:7831-7834`), so on a rung `duty_cap_` is `duty_max_`, 27,648.

**Every frame (44 kHz, `.ctlMotor`):**
1. **The feedforward is already at the ceiling.** `feedForward` (`:8823-8831`) gives |drv_incr| × duty_max /
   ff_ceiling, at most duty_max.
   - `ff_ceiling` is 167,501,483 in this build (`BM-ABIP1`, `:18`). So from 167.5 ×10⁶ up, the feedforward alone is
     27,648, and only the trim's negative part keeps the duty under it.
   - At 175 the trim held −342 to −623 counts (duty 27,025-27,306; `:141`, `:250`, `:359`, `:468`) and no frame
     clamped (`BM-RUNGHL` `win_cap,0`; `:143`, `:252`, `:361`, `:470`). DERIVED.
2. **At 185 the trim asks for more than the ceiling.**
   - `.dutyLimits` clamps and counts `duty_capped_` (`:8085-8086`).
   - The anti-windup re-derives `servo_acc` from the clamped duty (`:8094-8100`): here 0, the ceiling less the
     feedforward.
   - From then on every frame with `|err_|` above 48 asks for more than the ceiling and is counted. The frames below
     48 pull the duty under it. So `duty_capped_` advances within almost every pass's 23 frames.
3. **The waveform touches its limits and never crosses them.**
   - `duty_ >> 4` feeds three QROTATEs (`:7915-7926`), then the min/max centring (`:7930-7954`).
   - At 27,648 the centred levels span 2 × 0.866 × 1,728 = 2,993 of the 2,998 counts the frame leaves after its 70-count
     dead gap.
   - `BM-CLIP` reads `lvl_min,3,lvl_max,2_995,room,3` on all four 185 rungs (`:152`, `:261`, `:370`, `:479`), and room
     20-36 at 175. DERIVED and MEASURED: **no clipped sine**.

**Every drive pass (1,913/s, `drvMotor`):**

4. `lag_s := ±err_` (`:7715-7716`). `jerkStep` (`:7787` → `:8960-9054`) steps toward the command. Its lag gate
   (`:8999-9010`) does not act below 80.
5. **`holdGate` (`:7807` → `:8876-8908`) sees a limiter.**
   - `duty_capped_ + foldback_cnt_` differs from `lim_seen` (`:8876-8878`): Z = 0.
   - In SPIN_UP or AT_SPEED it takes `.limHold` (`:8890-8891`): the field may advance only while `lag_s < LAG_LIM`, 64
     (`:8893`).
   - Past 64, the field is set back to 64 (`:8895-8903`), the hold arms (C4, `:8906-8907`), and C = 0.
6. **Held.** In `.justIncr` (`:7812-7815`) the field does not take this pass's increment.
   - At 185 ×10⁶ that drops 11 counts, 15.5° electrical, of field phase. `lag_held_` counts the pass.
   - `holdDecay` (`:8847-8855`) turns AT_SPEED into SPIN_UP and, with Z = 0, takes `drv_incr −= drv_incr SAR 6`:
     2.9 ×10⁶ off the field's speed.
7. **C4** (`:8883-8889`) keeps the limit hold on every running pass until the rotor ticks forward past `lim_pos`. At 494
   ticks/s that is the next sector, under 2 ms. It changes little here: REV 47 and REV 48 model alike (§4.11.4).
8. **The climb back.** `passEnd` (`:8821-8822`) re-snapshots `lim_seen`. The next passes' `jerkStep`, now in SPIN_UP,
   re-accelerates toward 185 ×10⁶ at `jerk_up` 71 per pass. Winning back one decay from a standing acceleration takes
   about 150 ms (√(2 × 2.9 ×10⁶ / 71) = 286 passes).
9. **Why it recurs in most sectors (DERIVED; no model parameter).**
   - Between hall edges `err_` is a staircase: +11 counts a pass at 185 ×10⁶, −42.7 at each edge, about 3.9 passes a
     sector.
   - With its mean at the servo point (48) or above, the top step reads 64 or more. The bench's 175 rungs read `err_pk`
     73-74 (`BM-RUNG2`; `:141`, `:250`, `:359`, `:468`), so the staircase passes 64 in every sector.
   - Below the ceiling that step meets `LAG_HOLD` 100 (`:8892`) and nothing happens. Once a frame has clamped, it meets
     `LAG_LIM` 64.
   - **So once the duty caps, the limit hold acts in most sectors, whatever the motor's parameters.**
10. **The lead does not move.** `frontApplyLead()` keys the lead on `|drv_incr_now|` (`:6493`), and the table is flat at
    8° above 73.5 ×10⁶ (`:5038-5045`; held flat past its end, `:5060`). Neither the decay nor the climb writes a new pair.

The driver's own history names step 6's effect. Skipping one increment at a ramp's arrival "dropped a whole drv_incr of
field phase at every arrival (12.3 deg electrical at 147e6) and rang the load angle at ~18 Hz: the current kick at every
speed change" (`:7788-7793`, PL-78 / PL-87 / PL-95). At the ceiling, REV 47 and REV 48 drop that increment 18-24 times
a second (MODELLED, §4.11.4).

#### 4.11.3 The log, fact by fact

The rivals:
- (a) voltage saturation: (a1) the clipped sine, (a2) the duty at its ceiling;
- (b) the lag past the torque peak once the duty can rise no further (`LAG_HOLD`, PL-105);
- (c) the lead or commutation timing wrong at that speed;
- (d) the one §4.11.2 adds: the drive's limit response (D-3's give-way and D-5's limit hold) engaged by the voltage
  ceiling.

| # | Log fact | What it supports or refutes | Standing | The separating reading |
|---|---|---|---|---|
| 1 | 165 and 175 clean on all four wheel-directions: OK, follow 99-100 %, `err_pk` 71-74, no hold, no clamp (`:133-146`, `:242-255`, `:351-364`, `:460-473`) | Against (c): the same 8° lead runs 175 clean. Consistent with (d): no limiter, so no hold | MEASURED | — |
| 2 | 175 duty 27,025-27,306, room 20-36, `win_cap` 0; `BM-TOPSPD` `unsat,175_000_000` (`:163`, `:272`, `:381`, `:490`) | The ceiling lies between 175 and 185 on all four: (a2) is the trigger | MEASURED | — |
| 3 | 185 `STEADY_TIMEOUT` on all four: no AT_SPEED in 6 s (`LADDER_STEADY_MS`, `test_bench_dual.spin2:1845`; `:147`, `:256`, `:365`, `:474`) | **Supports (d)**: `holdDecay` turns AT_SPEED into SPIN_UP on each held pass, and the field never reaches the command (model REV 47 / 48: no AT_SPEED in 6 s; REV 46 and T-1: AT_SPEED in 392 ms). Against (a) alone: the old driver followed 185 by field weakening (fact 8). Not (b) under REV 47: a pass the ceiling clamped holds at 64 (`:8893`), so the lag cannot sit at 100 there | MEASURED; MODELLED | The trace (§4.11.10): `lag_held` rising while `duty_capped` rises and `foldback_frames` does not, with `err` never at 100 |
| 4 | `BM-CLIP` `room,3` on all four at 185 | (a1) **REFUTED**: room ≥ 0 is no clip (`clipRoom()`, `test_bench_dual.spin2:10399-10408`; the judge passed its own negative case, `BM-CLIPTEST` `:54`), and the duty is clamped before the waveform by construction. (a2) **SETTLED**: levels at the rails means duty 27,648 | SETTLED | — |
| 5 | `hw_skip` 2-6 at 185 (`:151`, `:260`, `:369`, `:478`); `missed_d,0,illegal_d,0` | Supports no rival. It is the harness instrument's 500 Hz hall poll (`instReadHall()` `:24012-24016`, one poll per sample `:23979-23980`) meeting 494 ticks/s. At Visit 9, `hw + hw_skip` matched the driver's ticks within 2 (`VISIT-9-EVALUATION.md` §2.1). The driver decodes the halls every frame and missed none. **Not evidence of lost synchronism** | SETTLED | — |
| 6 | No lag fault in LIMTOP (`BM-SEG` `:491`, faults 0) | Consistent with (d): a hold at 64 keeps the reading far from 125. Against (b) as a slip at 185 | MEASURED | — |
| 7 | The over-command (245 ×10⁶) falls to 12.6-13.1 % (`BM-FOLLOW OVER`, `:159`, `:268`, `:377`, `:486`) | Says nothing about 185. The 1 A limit is set only inside `overCommandStep()` (`test_bench_dual.spin2:10540`, restored `:10545`; read back 40 / 27 A, `BM-OCLIM` `:160`, `:269`, `:378`, `:487`). The rungs ran at the 40 A peak, so this is the fold-back, not the ceiling. It **validates the model**: REV 47 gives field 12.6-12.7 % and rotor 3.7 % (harness `h_pct` 5). The Visit 9 driver did the same (6-19 ×10⁶, `VISIT-6.1.0-EVALUATION.md` §2.3) | SETTLED; MODELLED | — |
| 8 | Visit 9, same rig, older driver (`2026-09-23/debug_260922-193000.log`): 185 followed at 100 % drawing 0.32-0.41 A; 245 followed on 3 of 4 by field weakening (`err` 48 → 65); one slip at 235 with a ~25 A peak | (a2) alone does not make the motor rough or lose the rung; the drive's response does. The 235 slip is the (b) regime | MEASURED | — |
| 9 | Stephen: gravel, labouring, vibration, "out of sync" | (d) predicts an irregular ~20/s train of field steps back against a turning rotor, with current peaks 6-8× the steady current (MODELLED). (b) predicts a slip with one large peak (fact 8) | CONSISTENT-WITH (d) | The trace's `drv_incr_now` steps and hold rate |
| 10 | Floor, FlySky, REV 47, pack 20,208-20,255 mV (`debug_261002-104014.log` RC-TEL seq 3,811-3,823): full-power pivot (LEFT at power 0), RIGHT `r_duty` 26,492-27,535 (96-99.6 % of the ceiling), SPIN_UP throughout, field 152.2-158.2 ×10⁶ of 165 (92.2-95.9 %), `r_short` 1 on 11 of 13 samples, `r_err` 21-65 | (d)'s signature in use: holds at the ceiling with `err` never above 65. Against (b): no `err` near 100 | MEASURED | — |

**Verdicts.**
- (a1) the clipped sine: **REFUTED** (SETTLED).
- (a2) the duty at its ceiling: **SETTLED as the trigger**; refuted as the carrier (MEASURED at Visit 9, MODELLED).
- (b) past the torque peak: **UNKNOWN on the bench at 185**, since the rung opened no window. Excluded under REV 47 by
  construction while the ceiling clamps (`:8893`). In the model it appears only at 205-245 ×10⁶ or under 6 N·m (T-1).
- (c) the lead: **REFUTED as the carrier**. MEASURED: 175 runs clean at the same lead. MODELLED: Table C below.
- (d) the limit response at the ceiling: **CONSISTENT-WITH every fact, and MODELLED as the carrier** (§4.11.4, §4.11.6).

#### 4.11.4 The model, 165-245 ×10⁶ wheels up

**The new mode.** `topspd` (§4.11.13) climbs as LIMTOP does: wheels up, each rung commanded 10 ×10⁶ above the last,
read over the last 1 s of the 6 s after the step. "Reaches" is the harness's 6 s steady bound. It runs with no steering
path limiter (`path=0`), because LIMTOP drives one motor object at a time. The fold-back is at the rig's 40 A peak
(`BM-ABIP2` `i_limit_k,12_015`).

**Calibration.** The model's own 18.5 V does not reproduce this run's duty. Its back-EMF constant comes from the ladder's
"170 per 10⁶ at 18.5 V", which was measured on the same pack under that nominal label (§4.11.11 S-a). At `top_v=21.3`
it does:

| Reading | MEASURED | MODELLED, `R47 CAL V20` |
|---|---|---|
| 165 ×10⁶ duty | 25,460-25,721 | 25,558-25,594 |
| 175 ×10⁶ duty | 27,025-27,306 | 27,136-27,169 |
| 165 / 175 `err_pk` | 71-74 | 74 |
| 185 ×10⁶ | `STEADY_TIMEOUT` on all four | no AT_SPEED within 6 s, both wheels |
| 245 ×10⁶ at 1 A: field / rotor | 12.6-13.1 % / `h_pct` 5 | 12.6-12.7 % / 3.7 % |

So V20 (21.3) stands for this run's pack, about 20.5 V, and V18 (19.2) for an 18.5 V pack. The raw supplies tell the
same story with the knee about 10 ×10⁶ lower (`topspd R48 CAL top_hi=205`):
- REV 48 is rough from 165 at 18.5 V and from 175 at 20.5 V.
- T-1 is steady to 185 at both, with one wheel rippling from 195.

**Table A: the climb at V20** (`R47`, `R48`, `R46`, `T1`, each `CAL V20 top_over=1`; LEFT and RIGHT together):

| Rung ×10⁶ | DRIVER_REV 47 / 48 (as built) | REV 46 (no PL-167) | REV 48 + T-1 |
|---|---|---|---|
| 165, 175 | AT_SPEED in 392 ms, 100 %, current sd 0.06-0.07 A, peak 1.9-2.1 A | identical | identical |
| **185** | **never steady**: rotor 93.4-95.1 %, field 94.9-96.2 %; 18-24 held passes/s, 12-19 set-backs/s; phase current sd 2.4-3.2 A, peak 11.6-15.7 A; torque sd 1.7-2.3 N·m; speed sd 15-20 rpm (at 330 rpm) | AT_SPEED in 392 ms, 100 %, lag 50.2-50.3 (peak 76), no hold; sd 0.05 A, peak 1.9 A; torque sd 0.007 N·m | identical to REV 46 |
| 195 | rotor 88.5-89.3 %, sd 2.8 A | 100 %; LEFT calm (sd 0.11 A); RIGHT ripples (sd 2.7-2.8 A, lag peak 83-84) | as REV 46 |
| 205-245 | the field gives way: rotor 84 → 71 %, field 86 → 72 % (≈ 175 ×10⁶); sd 2.8-3.2 A, peak 13.8-15.6 A throughout | 97.7-99.9 %; lag 55 → 66 (Visit 9 MEASURED 48 → 65); from 205-215 lag peaks 108-114, 4-10 holds/s at `LAG_HOLD`, sd 7.9-8.8 A, peaks 30-39 A | as REV 46, within a few % |
| 245 at 1 A | REV 47: field 12.6-12.7 %, rotor 3.7 % (MEASURED 12.6-13.1 %). REV 48: field 64.8 %, rotor 3.4-3.5 % (S-b) | field 5.9-6.0 % (the Visit 9 driver: 2.4-7.8 %) | as REV 48 |

**Table B: what carries it** (185 ×10⁶, V20; same model, only flags differ):

| Drive | Steady? | Rotor | Held / set-backs per s | Phase current sd / peak |
|---|---|---|---|---|
| `R47` | no | 93.8-95.1 % | 18-20 / 12-13 | 2.4-3.0 / 11.6-13.7 A |
| D-1..D-3 without D-5 (`acc_shift=16 dB=1 boost_shift=10 dC=1 blk_lim=1 CAL`) | yes, 392 ms | 100 % | 0 / 0 | 0.05 / 1.9 A |
| `R47 d5_back=0`: the limit hold, no set-back | no | 95.1-95.5 % | 19-20 / 0 | 1.9-2.2 / 10.0-11.6 A |
| `R47 hold_decay_shift=30`: no decay | AT_SPEED 97-98 % of the time | 96.7-96.8 % | 43-44 / 41-42 | 2.0 / 10.2-11.1 A |
| `T1` | yes, 392 ms | 100 % | 0 / 0 | 0.05 / 1.9 A |

What Table B shows:
- **The limit hold on a pass the ceiling clamped is necessary and sufficient for the roughness.** Without it, or armed
  only by the fold-back, 185 runs clean.
- The set-back adds to it, but the hold alone already jolts.
- The decay turns the jolts into the lost speed and the never-steady state. With no decay the rotor still runs 3 %
  slow: 43 held passes a second drop 43 field steps that are never made up.

**Table C: rival (c), the lead** (`R48 CAL V20 top_lo=175 top_hi=185 top_L=3`, `=13`, `=18`; 8° is the schedule):

| Fixed lead | 175 ×10⁶ | 185 ×10⁶ |
|---|---|---|
| 3° | clean, duty 25,428-25,556 | below the ceiling (26,717-26,931): LEFT clean; RIGHT ripples without a clamp (sd 2.2 A, lag peak 77, the low-lead side) |
| 8° (the schedule) | clean | rough (Table A) |
| 13° | rough: 91.5-92.8 %, sd 2.6-3.0 A | rough: 86.9-87.5 % |
| 18° | rough: 85.6-86.1 % | rough: 80.5-81.3 % |

The lead moves where the duty first caps (manual §6.3, "alignment moves the knee"). In every column the first capped rung
is the rough one. **The roughness follows the ceiling, not the lead.**

**Parameters: central only.** The phase 2 refit (e90 52, 0.85 mH) hunts at 145-175 ×10⁶ wheels up even under REV 46
with the supply far above its need (`R46 CAL e90_L18=52 Lh=0.00085 top_v=26.0 top_lo=145 top_hi=175`: lag peaks 107-109,
current sd 5.4-6.0 A, 83-95 %). The bench runs these rungs calm (`err_pk` 71-74). So the refit is falsified at top speed,
and the central parameters are the ones that reproduce the bench at 165, 175 and 185 (§4.11.11 S-c).

#### 4.11.5 Does full power on an 18.5 V pack enter the region?

**Yes. It is DERIVED from this run's duty and MODELLED, and on the floor it is MEASURED at a full charge.**
- **DERIVED from this run's duty.** The duty a speed needs is the voltage the motor needs divided by the pack's voltage,
  and the motor's need does not depend on the pack.
  - At 165 ×10⁶ this run needed 25,460-25,721 (`:134`, `:243`, `:352`, `:461`).
  - The run prints no pack reading: `BM-BUILD`'s `pack_mV,18_500` (`:4`) is the configured value.
  - The same pack read 20,521 mV 19 minutes later (`debug_261002-103332.log` `BM-FLLEG` seq 797) and 20,508-20,588 mV
    at 10:40 (RC-TEL). The rig's sensor read 20.72 V at Visit 10 pass 7.
  - At 20.5-20.7 V, 165 ×10⁶ on 18.5 V needs 25,460-25,721 × (20.5-20.7) / 18.5 = 28,212-28,780: **102-104 % of the
    ceiling.**
  - With this run's 165 → 175 slope (156.5-158.5 per 10⁶, × (20.5-20.7) / 18.5), **an 18.5 V pack reaches the ceiling at
    158-162 ×10⁶: power 96-98.**
- **MODELLED (V18).**
  - REV 48: 145 and 155 are clean. 165 is rough: 96.5 % of command, never steady, 16 holds/s, current sd 1.6 A, peaks
    7.5-8.3 A, torque sd 1.06 N·m.
  - T-1: 165, 175 and 185 run steady at 100 % (lag 50 / 53 / 55, current sd 0.02-0.17 A).
- **MEASURED on the floor at 20.2 V.** The FlySky drive's full-power pivots put the RIGHT wheel at 96-99.6 % of the
  ceiling, with the hold acting (§4.11.3 fact 10).
- **So the reserve the power table rests on holds only for a charged pack, wheels up.** That reserve is 165 ×10⁶ at
  92-93 % of the ceiling (manual §6.1).

#### 4.11.6 The cause

**Established at the desk to §4.9.8's standard.** The mechanism is SETTLED in the driver's logic, MODELLED as the
carrier, and CONSISTENT-WITH every log fact.
- **Statement.**
  - At the duty ceiling, D-3 and D-5 (DRIVER_REV 47) treat the voltage limit as a limiter.
  - D-5's limit hold then caps the lag at 64. That is the stall's torque placement (§4.9.1), and it sits 18-24 counts
    short of where the voltage-limited torque peaks at speed.
  - The cap catches the top step of the lag's staircase in most sectors. Each held pass drops 15.5° of field phase, and
    some step the field back as well; D-3 then takes 1/64 off the field's speed.
  - The field can neither settle nor follow, and the current jolts 18-24 times a second.
- **Why the peak is out of reach (DERIVED, §3.2's model).**
  - With the voltage's magnitude fixed, the torque peaks where the voltage leads the back-EMF by 90° + φ, with
    φ = atan(ωL/R).
  - At 185 ×10⁶, ω = 518 rad/s. With 0.5 mH and 0.25 Ω, φ = 46° = 33 counts, so on the schedule's 8° (e90 ≈ 49) the
    peak reads `err` ≈ 82. At 0.85 mH, φ = 60° and the peak is at about 88.
  - A hold at 64 sits before that peak, and `LAG_HOLD` 100 sits after it.
  - At a stall there is no back-EMF, φ plays no part, and the peak is at e90 (56-57 at MEDIUM, §4.9.1). That is the case
    D-5 was designed for.
- **The separating evidence (MODELLED, same model, only the flags differ).**
  - D-5 off: 185 clean.
  - D-5 armed only by the fold-back (T-1): clean.
  - D-5 as built (REV 47 and 48): the bench's `STEADY_TIMEOUT`, with 50× the current ripple.
  - REV 46 reproduces Visit 9's following to 245 (lag 66 against 65 MEASURED).
- **Hardware standing: consistent with.** The trigger is a fact of the source: §4.11.2 step 9 needs only the logged
  `err_pk`. That this train of holds is what Stephen heard rests on the model, and on the floor's MEASURED holds at the
  ceiling. The trace (§4.11.10) can refute it. Per P10 it is not a precondition for building the fix.

#### 4.11.7 The fix: T-1, the limit hold on the current limit only

**Mechanism.**
- In `holdGate`, the limit hold (and C4's arming) is entered when the **fold-back** acted since the previous pass, or
  while the hold is armed. A pass on which only the duty ceiling clamped does not enter it.
- D-3's fact, Z ("a limiter acted"), is unchanged and still feeds `holdDecay`.
- So a pass where only the ceiling clamped takes today's `LAG_HOLD` gate. If its lag reaches 100 there, the field is held
  and D-3 gives way, as REV 46 did. I-2 stands.

**Sketch.** The build counts and checks it. It needs one cog register, `fold_seen`. TJNZ and TJZ write no flag
(`p2kbPasm2Tjnz`, `p2kbPasm2Tjz`), and SUB without WC/WZ writes none (`p2kbPasm2Sub`), so Z reaches `holdDecay` unchanged.

```
' passEnd (:8821-8822), after lim_seen:
                mov     fold_seen, foldback_cnt_        ' T-1: the fold count as this pass leaves it (no flag)
' gettgtincr's re-take (:8804-8805), beside lim_seen: a drive starts from STOPPED, so this also seeds it
    if_nz       mov     fold_seen, foldback_cnt_
' holdGate: .noArm (:8890) becomes
.noArm          mov     tmpX, foldback_cnt_             ' T-1: did the FOLD-BACK act since the previous pass?
                sub     tmpX, fold_seen                 '  mod 2^32; no flag written, so Z (any limiter) survives
                tjnz    tmpX, #.limHold                 ' yes: the limit hold, as today
                tjz     lim_arm, #.today                ' no, and not armed: today's LAG_HOLD gate (was IF_Z TJZ)
                jmp     #.limHold                       ' :8891 unchanged: armed, the limit hold
```

**Invariant (I-11).** In SPIN_UP / AT_SPEED the limit hold (`LAG_LIM`, its set-back and C4's arming) acts only on a pass
where the current fold-back acted since the previous pass, or while a hold such a pass armed is still armed. A pass on
which only the duty ceiling clamped keeps `LAG_HOLD`. D-3's give-way still reads both limiters, so I-2 stands.

**Why it is correct by construction.**
- **The hold's placement (64) is right where the current limit binds: at a stall** (§4.9.1).
  - For the 6.5″ motor at 18.5-20.5 V, a stalled wheel meets the fold-back first. The ceiling's phase voltage,
    0.563 × 18.5 = 10.4 V, over 0.24-0.25 Ω would drive 42-43 A, above the 40 A peak limit. DERIVED.
  - The obstacle grids are identical with T-1 (§4.11.9).
- **In SPIN_UP / AT_SPEED the ceiling clamps only when back-EMF has used the voltage** (`duty_cap_` is `duty_max_` there,
  `:7831-7834`). There the torque peak sits at e90 + φ, past 64 (§4.11.6). So the ceiling must never arm a hold placed for
  a stall.
- **It changes nothing where the ceiling does not clamp.** `legs`, `design R48 CAL`, `release`, `stepdn` and `block`
  re-ran identical with and without it (§4.11.13).
- **Boundary (UNKNOWN).** In a configuration whose ceiling binds before its current limit at a stall (a lower supply, or
  a higher-resistance motor), T-1 gives that stall REV 46's `LAG_HOLD` instead of D-5's 64.
  - Not modelled. The 12 V single-motor (DocoEng) build is the one to check.
  - T-1b (§4.11.8) keeps D-5 for that case.

**Cost (ESTIMATE from the sketch).**
- **Cog:** +1 register (`fold_seen`), 50 → 49 free (`:8503`).
- **LUT:** +5 longs (`holdGate` +3, `passEnd` +1, `gettgtincr` +1), 13 → 8 free (`:9517`).
- **Time:** about +6 clocks per running pass in `holdGate` (+2 when the TJNZ is taken), +2 in `passEnd` and +2 in
  `gettgtincr`; 0 per frame.
- **ABI:** none. No params or status long; `foldback_frames` is already in the status run.
- **Text:** the comments at `:7082-7087`, `:7807-7811` and `:8858-8875` change. DRIVER_REV 49.

#### 4.11.8 Candidates considered

| Candidate | Modelled | Verdict |
|---|---|---|
| **T-1:** the limit hold armed only by the fold-back | 185 clean at V20; 165-185 clean at V18; 4 N·m at full power at 100 %; obstacle, load, spins and slow-downs identical | **Recommended** |
| T-1b: T-1, but the ceiling still arms the hold while the field is slow (\|drv_incr\| under a set speed, e.g. ff_ceiling / 4) | not run; identical to T-1 on every rung here (all above 145 ×10⁶) | Viable if Stephen wants D-5 kept for a stall that meets the ceiling first (§4.11.7 boundary); +2-3 LUT longs |
| T-0: drop the ceiling from D-3's give-way too | not run | Rejected, DERIVED. At `LAG_HOLD` with no decay, the field pauses on every held pass at speed: §4.11.2 step 6 again. And I-2 loses its voltage half: a load the voltage cannot carry would never give way |
| A separate hold at the ceiling near the voltage-limited peak (about 80-88) | not run | Rejected: 82-88 is the fault lattice's window (§4.9.4, §4.10.2) |
| Lower the top of the lead table (3°) | L 3° moves the knee above 185 at V20 (Table C) | Not a fix: the response at the ceiling is unchanged, and 3° is not measured above 73.5 ×10⁶ (manual §5.2: 8° at 147, and 13° costs 2×). A lever on headroom only |
| Keep users below the knee: a power-100 ceiling that follows the measured pack | — | Not a fix: a loaded wheel at full power reaches the ceiling on a full pack (§4.11.3 fact 10). It also needs the optional pack sensor |

#### 4.11.9 The measure of benefit (for Stephen; P5)

MODELLED unless marked: central parameters under `CAL`; V20 is the session's pack (about 20.5 V), V18 an 18.5 V pack. The
model's absolute currents run high (§5; here 3.3-4× the bench's DC current at 175, 1.27 A against 0.32-0.38 A). So
currents are compared within a row.

| What a user sees | DRIVER_REV 47 / 48 (as built) | **REV 48 + T-1** | Standing |
|---|---|---|---|
| Wheels up at 185 ×10⁶, charged pack: does it settle? | no. Bench: `STEADY_TIMEOUT`, 4 of 4. Model: never; rotor 93-95 % | yes, in 0.4 s, 100 % | MEASURED (REV 47); MODELLED |
| The same: phase-current ripple (sd / peak), torque ripple, speed ripple at 330 rpm | 2.4-3.2 A / 11.6-15.7 A; 1.7-2.3 N·m; 15-20 rpm | 0.05 A / 1.9 A; 0.007 N·m; 0 | MODELLED |
| Full power (165 ×10⁶) on an 18.5 V pack, unloaded | 96.5 % of speed, never steady; sd 1.6 A, peaks 7.5-8.3 A; torque sd 1.06 N·m | 100 %, steady; sd 0.02-0.03 A | DERIVED (needs 102-104 % of the ceiling) + MODELLED |
| Full power, charged pack: the largest load on one wheel carried at 100 %, calm | 0.5 N·m (about 6 N at the tyre). Rough from 1 N·m (98.8 %, peaks 10.5 A); 90.8 % at 2 N·m | **4 N·m (about 48 N)** at 100 %. Gives way at 6 N·m (93.6 %, at `LAG_HOLD`, torque sd 0.28 N·m) | MODELLED |
| The same on an 18.5 V pack | none: rough unloaded | 2 N·m at 100 %; 96.0 % at 4 N·m | MODELLED |
| On the floor, full-power pivots at 20.2 V | duty at the ceiling, the field held (11 of 13 samples), 4-8 % slow | UNKNOWN on the floor (the wheels-up rows above) | MEASURED (REV 47) / UNKNOWN |
| Above 195 ×10⁶ wheels up (beyond any user command) | the field gives way to about 175 ×10⁶, rough | follows (97-100 %). From 205 the model holds at `LAG_HOLD` with large ripple, as REV 46 does; Visit 9 measured smooth following to 245 on 3 of 4 | UNKNOWN (the model over-states) |
| Unloaded DC current, 175 → 185 ×10⁶ | 185 never steady | +9 % (field weakening). Visit 9 measured 0.32-0.41 A at 185 against 0.32-0.38 A at 175 | MODELLED / MEASURED |
| Blocked on a rocking obstacle (1,000 N/m): stopped / pushed on / lag fault, of 16 | 15 / 1 / 0, 1,080-1,738 ms after contact | identical, digit for digit | MODELLED |
| Load and release, spins, slow-downs, the stop from 147 ×10⁶ | §4.10.8 | identical, digit for digit | MODELLED |
| The 1 A over-command (the harness's negative case): field / rotor | REV 47: 12.6-12.7 % / 3.7 % (MEASURED 12.6-13.1 %). REV 48: 64.8 % / 3.4 % | as REV 48 | MODELLED (S-b) |

**No row gets worse.** Every row the ceiling never reaches is identical.

**RULING NEEDED (P5): build T-1 into the 6.1.0 load?**
- **Recommendation: yes.**
- It removes the roughness at the voltage ceiling that a user meets at full power on a part-charged pack, or under load.
- It costs one register and about five LUT longs.
- It changes no behaviour below the ceiling.
- If Stephen wants D-5 kept for a hypothetical low-voltage stall, the variant is T-1b.

#### 4.11.10 What the dual-limits trace must record (Part B)

**Fields per 2 ms sample:**
- the driver's `pos`, not the instrument's `hw`, which aliases at 494 ticks/s;
- duty, signed `err`, `drv_state` and `drv_incr_now`;
- the cumulative counters `lag_held`, `duty_capped` and `foldback_frames` (all in the status run: `BM-ABIS2`, `BM-ABIS3`);
- the DC-link reading.

**Once per trace:** the pack's mV (the rig's sensor is fitted: Visit 10 pass 7), the offsets in force, and `duty_max`.

**Windows:**
- the 185 rung, from its step to the 6 s timeout: about 3,000 samples, inside the 4,096-sample ring;
- the last 1 s of the 175 rung, as the control;
- the over-command's hold and window.

**Does Part B's 2 ms BM-STRACE suffice? Yes, for the verdict.**
- The counters are cumulative, so the holds, clamps and folds in each 2 ms are exact.
- The decay's 1/64 steps and the climbs back (about 150 ms) are resolved in `drv_incr_now`.
- `err` is sampled every 2.00 ms against a 2.02 ms sector at 185 ×10⁶, so single samples alias. But the samples beat
  through the whole staircase about every 200 ms, so over the window `err`'s range is complete.
- It does not resolve each current jolt (about 1-2 ms wide; a 2 ms DC-link snapshot under-reads the peaks). The verdict
  does not need the jolt's shape.

**The readings at the 185 rung that separate the rivals:**

| Reading | (d) the limit response | (b) past the peak | (a2) saturation alone | (c) the lead |
|---|---|---|---|---|
| `lag_held` rate while `duty_capped` rises and `foldback_frames` does not | 18-24/s (model) | > 0, with `err` ≥ 100 at the holds | 0 | 0 |
| `err` range | peaks 84-88, none ≥ 100 | samples ≥ 100 | mean 50-53, peaks ≤ about 80 | — |
| `drv_incr_now` | steps down by 1/64, climbs back; mean 95-96 % | decays at `LAG_HOLD` | 100 % | 100 % |
| `drv_state` | never AT_SPEED for long | — | AT_SPEED | — |
| The 175 control | no hold, no clamp | the same | the same | rough at 175 too |

- **The falsifier for (d):** holds absent at 185 while the rung is still rough or times out. Then the carrier is physical,
  (a) or (c), and T-1 does not apply.
- **Certification after T-1:** the same trace shows `lag_held` 0, AT_SPEED within the 6 s bound, and `duty_capped`
  rising.
  - This run's REV 48 build is the cell's negative.
  - Proposed cell: on the 185 and 195 rungs, no `lag_held` while `duty_capped` advances and `foldback_frames` does not,
    and AT_SPEED reached.
- **The over-command under REV 48 (MODELLED):** rotor 3.4-3.5 %, `drv_incr_now` about 65 % (permille about 648), holds
  about 1,780/s, folds about 78 frames/s. `BM-FOLLOW OVER` would then read `h_pct` 3-5 against a permille of about 650,
  where REV 47 read 126-131 (S-b).

#### 4.11.11 Side findings (recorded, not acted on)

- **S-a. The "18.5 V" top speed was measured on a pack at about 20.7 V.**
  - The rig's pack read 20.72 V (meter 20.74 V) at Visit 10 pass 7 (`VISIT-10-PASS7-EVALUATION.md`), and Visit 9's runsheet
    calls the same rig "18.5 V".
  - The duty at 165 ×10⁶ is the same at Visit 9 (25,334-25,582) and in this run (25,460-25,721). Both therefore ran on the
    pack.
  - So the manual's "ceiling increment at 18.5 V: 165 ×10⁶, measured" (§6.1) and the feedforward line "measured at
    18.5 V" (`:4495`) belong to about 20.5-20.7 V. On a true 18.5 V pack, full power reaches the ceiling (§4.11.5).
  - It touches the power table, the manual and DRIVE-OBJECTS. A punch-list candidate for Stephen.
- **S-b. REV 48's C4 decouples `drv_incr` from the field during a held crawl (MODELLED).**
  - At the 1 A over-command, REV 48 keeps the field held on about 1,780 passes a second, but decays it only on fold
    passes (about 78/s).
  - Meanwhile `jerkStep` (`:7787`), which runs before `holdGate`, keeps raising `drv_incr` toward the command
    (`:9011-9019`).
  - Result: the field crawls with the rotor at 3.4 %, while `drv_incr_now` reads 64.8 % (REV 47 read 12.6 %).
  - Two readers take `drv_incr_now` as the field's speed: the steering object's shortfall (`shortfallNow()`,
    `:6470-6479`; §2.3: "exact only because the decay walks the field down to the rotor"), and the harness's FOLLOW /
    FOLFALL.
  - The fold-back case, so outside T-1's scope. A punch-list candidate. Part B should expect it.
- **S-c. The refit parameters are falsified at top speed (MODELLED against MEASURED).** They hunt at 145-175 ×10⁶ wheels
  up, where the bench runs calm. Any later use of the refit at speed should cite this.

#### 4.11.12 Not checked, and the model's limits

- **Above 195 ×10⁶.** The model holds at `LAG_HOLD` with large ripple in every drive, which Visit 9's bench did not show
  on 3 of 4. UNKNOWN there. No user command reaches it: power 100 is 165 ×10⁶.
- **Parameters.** Only the central parameters reproduce the bench at speed. The bracket between them and the refit is
  not run.
- **Not modelled:**
  - cogging;
  - unequal hall sectors, which change which pass meets 64 (DERIVED only as "most sectors");
  - Rev A;
  - the current jolt's shape, which needs sub-pass sampling;
  - the sound itself: current and torque ripple are its proxies.
- **Not run:**
  - the floor at full power with T-1 (the platform's straight drive at 165 ×10⁶);
  - T-1's boundary case (a stall that meets the ceiling first; the 12 V DocoEng build) and T-1b.
- **The PASM sketch is not assembled.** Its costs are ESTIMATE.

#### 4.11.13 Reproduce

```
S=DOCs/plans/servo-model; CAL="pasm=1 v_dt=0.18 i_noise=3"; R47="acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1"
R48="$R47 cap_lift=48 d5_sticky=1 blk_fix=1"; T1="$R48 d5_fold_only=1"
python3 $S/spin2_model.py topspd $R47 $CAL top_v=21.3 top_lo=155 top_hi=195             # calibration (V20); REV 47 at the edge
python3 $S/spin2_model.py topspd $R47 $CAL top_v=21.3 top_lo=205 top_over=1             # REV 47 above it; the 1 A over-command
python3 $S/spin2_model.py topspd $R48 $CAL top_v=21.3 top_over=1                        # Table A, REV 48
python3 $S/spin2_model.py topspd $CAL top_v=21.3 top_over=1                             # Table A, REV 46
python3 $S/spin2_model.py topspd $T1 $CAL top_v=21.3 top_over=1                         # Table A, T-1
python3 $S/spin2_model.py topspd acc_shift=16 dB=1 boost_shift=10 dC=1 blk_lim=1 $CAL top_v=21.3 top_lo=185 top_hi=195  # Table B: no D-5
python3 $S/spin2_model.py topspd $R47 $CAL d5_back=0 top_v=21.3 top_lo=185 top_hi=185                                  # Table B: no set-back
python3 $S/spin2_model.py topspd $R47 $CAL hold_decay_shift=30 top_v=21.3 top_lo=185 top_hi=185                        # Table B: no decay
python3 $S/spin2_model.py topspd $R48 $CAL top_v=21.3 top_lo=175 top_hi=185 top_L=3                                    # Table C; top_L=13, 18
python3 $S/spin2_model.py topspd $R48 $CAL top_v=19.2 top_lo=145 top_hi=185             # an 18.5 V pack (V18); and $T1
python3 $S/spin2_model.py topspd $R48 $CAL top_v=21.3 top_lo=165 top_hi=165 step_T=1.0  # reserve: REV 48 step_T=0.5, 1, 2; $T1 1, 2, 4, 6; V18 $T1 2, 4
python3 $S/spin2_model.py topspd $R48 $CAL top_hi=205                                   # the raw supplies, 18.5 and 20.5 V; and $T1
python3 $S/spin2_model.py topspd $CAL e90_L18=52 Lh=0.00085 top_v=26.0 top_lo=145 top_hi=175  # S-c: the refit hunts at speed
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 $R48 $CAL                             # T-1 changes nothing: each of these
python3 $S/spin2_model.py release $R48 $CAL                                             #  four, with and without
python3 $S/spin2_model.py design $R48 $CAL                                              #  d5_fold_only=1, printed
python3 $S/spin2_model.py stepdn $R48 $CAL                                              #  identically
python3 $S/spin2_model.py legs                                                          # must-not-change: identical on the original copy and the edited file
```

**Model changes (`spin2_model.py`, additive; every new parameter defaults to the old behaviour):**
- the `topspd` mode and `top_rung()`;
- new parameters: `d5_fold_only` (T-1), `path` (default 1, the steering path limiter as before), `top_v`, `top_L`,
  `top_lo`, `top_hi`, `top_over`;
- the trace sample gains five appended fields (set-backs, ceiling frames, fold frames, iq, rotor speed). Every earlier
  reader reads by index, so none sees them.

**The identity checks:**
- `legs` (no flags) and `stepdn $R48 $CAL` printed identically on a copy of the original file and on the edited one.
- `block ob_n=16 ob_k=1000 $R48 $CAL` reproduces §4.10.8's 15 / 1 / 0, 1,080-1,738 ms.
- `release $R48 $CAL` reproduces §4.10.8's 99.9 / 100.0 %.

### 4.12 — the limit hold's three gaps (PL-189), with T-1

**Status: DESIGN, Part C of «#3668». No driver code is changed by this section.**
- **What it answers.** The second 6.1.0 visit's G-2, G-3 and G-4 (`DOCs/analyses/bench/2026-10-02b/VISIT-6.1.0B-EVALUATION.md`
  §3.2, §3.3, §2.2, §4a), designed together with T-1, which is ruled (§4.11.7).
- **Why it goes to Stephen first.** Each correction is a new driver behaviour, so it goes to him with its benefit before
  anything is built (P5).

- **Evidence**, all DRIVER_REV 48, cited by seq or by trace `k`:
  - `debug_261002-143413.log` (floor-obstacle);
  - `debug_261002-143538.log` (floor-grab);
  - `debug_261002-142002.log` (dual-limits);
  - the comparison `2026-10-02/debug_261002-101625.log` (DRIVER_REV 47).
- **Driver:** `src/isp_bldc_motor.spin2` at DRIVER_REV 48 (`7fc6a77`):
  - `holdGate` `:8858-8908`, `.justIncr` `:7806-7817`, `holdDecay` `:8833-8856`;
  - `gettgtincr` `:8794-8814`, `passEnd` `:8816-8822`;
  - `driveFromRest` `:9104-9110`, `.clearRun` `:8131-8136`;
  - `bFrontProtect()` `:2864-2922`.
- **Harness:** `src/test_bench_dual.spin2` `blockWatch()` `:21276-21368`, read only.

Command shorthand (`S=DOCs/plans/servo-model`; every run is `python3 $S/spin2_model.py <mode> ...`):
- `CAL`, `R47`, `R48` and `T1` as in §4.11.
- `B` = `$T1 c4_state=1`, the baseline of this section: REV 48 + T-1, with the as-built disarm in any state but SPIN_UP /
  AT_SPEED, which the model lacked (§4.12.3).
- `FIX` = `$B u_arm=1 u_span=2 u_cap=1 u_cap_sec=4`: T-1 + U-1 + U-2 + U-5, the recommended set.
- `HOLD` = `grab_B=5 grab_v=0.45 grab_a=0.8 grab_f=5 grab_rnd=2 grab_n=16`: a hand that holds steadily, as the run sheet
  asks.
- `RAND` = `grab_B=5 grab_v=0.15 grab_a=1.0 grab_f=5 grab_rnd=1 grab_n=16`: a rougher hand that also pushes the wheel on.

#### 4.12.1 Summary for Stephen

**What went wrong.** All three gaps are in the hold 6.1.0 added for a wheel at its current limit. That hold keeps the
rotating field (the magnetic pull that drags the rotor round) no more than 90° of the electrical cycle ahead of the
rotor. Then a wheel pushed back one step cannot trip the "lost its place" fault.
1. **It switched on one step late.**
   - It armed when it first pulled the field back, not when the current limit first acted.
   - In between, the field drifted into the band where a single push back faults the motor.
   - The obstacle test caught it once per trial (readings 85 and 83).
2. **It switched off too early.**
   - Every forward step of the wheel turned it off.
   - So a wheel your hand slowed but did not stop was unprotected for part of every step, and your grab faulted it.
3. **While on, it let the field's speed run away from the wheel's.**
   - In the 1 A over-command test the field kept going at about half speed while the wheel crawled at 4 %.
   - When the full current limit came back, the drive pushed that field speed into an almost stopped wheel.
   - Result: about 10 A from the battery, the test's own safety abort, and a right-hand board that went quiet.

**The fix: three small changes, built with T-1.**
- **Arm at the first current-limit action**, not at the first pull-back.
- **Stay armed until the wheel has turned one whole step forward with no current-limit action**, not at every forward
  step.
- **When the hold switches off, cap the field's speed** at four steps divided by the time since the limit last acted.
  - That is never slower than the wheel itself and at most four times its recent speed.
  - So the field restarts from about the wheel's own speed, not from wherever it had run away to.

**Benefit (modelled, 16 trials per row):**
- **At an obstacle:** the drift into the fault band at contact is gone. The test's window hits go 6 → 0, and a solid
  obstacle now stops the platform 16 times out of 16 (was 15, and 1 fault).
- **A hand holding a wheel steadily:** faults 1 → 0 of 16, and the time in the fault band 468 → 386 ms. A rougher hand:
  6 → 4 of 16.
- **The end of a long current limit:** the battery-current peak falls 34 A → 3 A in the model, which is below the 4.5 A
  of the driver the first 6.1.0 visit ran cleanly.
- **Everything else is identical, digit for digit, or 0.1 point better:** spins, ramps, slow-downs, reversals, top speed
  and the load tests. Two things move the wrong way:
  - one load test loses 0.1 point (2 N·m released: 99.8 → 99.7 %);
  - on 3 of 16 solid-obstacle contacts the protective stop comes about 270 ms later (up to 1.36 s after contact).

**What it does not fix: the line on a grab.**
- When one wheel is held at its limit, the steering does not slow the other wheel to keep the platform's line. The held
  wheel's field speed still reads near full.
- The change that would fix it, letting the field's speed fall while the wheel is held, made the grab and obstacle faults
  worse in the model. It is not proposed.
- The grab's line check (LDPATH) will therefore fail. It is recorded, not hidden.

**Cost.** No change to the shared-memory layout.
- About 6 of the 13 free LUT longs (7 left) and about 16 of the 50 free cog longs.
- About 0-4 clocks per drive pass, and about 95 on the rare pass where the hold switches off.

**Decision for you (§4.12.9): build T-1 with these three changes for the third visit.** Recommendation: yes.

#### 4.12.2 The three gaps, reproduced, and their causes

**G-2: the hold arms at the first set-back, not the first limiter action.**
- **The mechanism (DERIVED, `:8876-8908`).**
  - The arming lines (`:8906-8907`) are inside the set-back. That runs only on a limited pass with `lag_s` ≥ 64.
  - A first fold with `lag_s` < 64 takes `.limHold` and returns without setting back, so the hold does not arm.
  - The following passes see no limiter and take `.today` (`LAG_HOLD` 100). The field walks up through 82..88 until the
    next fold sets it back and arms.
- **The bench.**
  - `BM-BLKWIN` seq 386 (COAST): `r_hit,1,r_emax,85`.
  - `BM-BLKWIN` seq 760 (BRAKE): `r_hit,1,r_emax,83`, and `l_emax,106`. That is one back tick from an armed 64:
    64 + 42.7 = 106.7, outside the window.
- **The model** (`block ob_n=16 ob_k=50000 $B $CAL blkwin=1`):
  - At the harness's own 5 ms poll: 6 hits on 3 of 16 contacts, emax 92.
  - At every frame: |err| 82..88 for 39.5 ms on 7 contacts, **every one with the hold not armed**.
- **The separating reading.** The hits fall only in the unarmed interval between a wheel's first limiter action and its
  first set-back.
- **Under `FIX`:** 0 poll hits. At frame level, 0.8 ms on 3 contacts.
  - That residue is the gap between the fold's frame and the drive pass that arms, at most 22 frames (0.5 ms).
  - The field does not move between passes, so it is the contact transit's own reading (§4.9.4). The 5 ms poll cannot
    see it.

**G-3: the hold disarms at the first forward tick.**
- **The mechanism (DERIVED, `:8883-8889`).**
  - Disarm at the first tick past `lim_pos`, the sector of the last set-back. Then `.today` applies until the next fold.
  - After a forward tick the reading is 64 − 42.7 ≈ 21. The field walks up past 64 into 82..88 before the next fold.
  - A back tick there reads 125 or more.
- **The bench** (`debug_261002-143538.log`, `BM-TS` tid 1; LEFT `e`, `st`, `pos`):
  - **After each forward tick** (`k` 1,093, 1,139, 1,168, 1,208): 22-25.
  - **Unarmed between folds:** 72-83 in AT_SPEED (`k` 1,200: 72; `k` 1,245: 73; `k` 1,375: 83).
  - **The fault:** at `k` 1,923 `e` 81 in AT_SPEED at `pos` 108, then at `k` 1,924 `pos` 107 (a back tick) with `flt`
    TRUE. That is the re-sync (`EV_FAULT_RESYNC` seq 16, 19,234 ms), and the fault follows (seq 19, 19,360 ms).
- **The model** (`grab $B $CAL HOLD diag=1`, and `RAND`). The hand is a damper to a moving hand. `HOLD` slows LEFT to
  9-21 % (bench: 19 %).
  - `HOLD`: 1 lag fault in 16; `RAND`: 6.
  - Every fault has "hold not armed" with 100-450 fold frames before it.
  - The fault contexts replay the bench's sequence: 64, a forward tick to 21-25, a walk to 82-88, a back tick, then
    125-127.
- **The separating reading.** Every `B` fault is in the unarmed walk after a forward tick. Under `FIX`, `HOLD` faults 0
  of 16.

**G-4: while armed, the field's speed runs away from the rotor's.**
- **The mechanism (DERIVED; §4.11.11 S-b).**
  - While armed, every pass ends set back at 64, so `jerkStep`'s `LAG_SOFT` gate (`:8999-9010`) never sees 80. The
    generator keeps accelerating `drv_incr` toward the command.
  - D-3 decays it only on fold passes. So `drv_incr` stays at 47-75 % of 245×10⁶ while the rotor crawls at 3-4 %.
  - When the limits return (40 A) and full power (165×10⁶) is commanded, the command is below `drv_incr`, so the state is
    SPIN_DN. As built (`:8881`), that disarms.
  - The field then leaves at `drv_incr`. The lag reaches `LAG_HOLD` within a few passes, and D-2's boost lifts the duty
    into the 40 A fold.
- **The bench.**
  - `BM-FOLLOW` OVER `drv_incr` −116.5 / 113.9 / −128.1×10⁶, permille 475 / 464 / 522 (seq 159, 269, 378). DRIVER_REV
    47 read −31×10⁶ (12.6-13.1 %).
  - `BM-ABORT` seq 161, `ABS_CURRENT` 1,445 mV, 65 ms after `BM-OCLIM` seq 160 by the host's timestamps.
  - `BM-POWER` seq 162: `drv_incr` −120.7×10⁶, 0 ticks, `ABORTED`.
  - LEFT forward completed (seq 271, follow 99 %). RIGHT fell silent after seq 379.
- **The model** (`overend`; LEFT / RIGHT). T-1 changes nothing here: this is the fold, not the ceiling.

| Drive | Field over the last 1 s at 1 A, rotor (% of 245×10⁶) | DC-link peak after the restore | Over 10 A |
|---|---|---|---|
| `R47 $CAL` | 12.6-12.7 % (§4.11.4; bench 12.6-13.1 %), 3.6-3.7 % | 4.69 / 4.50 A | 0 ms |
| `B` | 73.1 / 74.0 %, 3.0 % | **34.0 / 33.9 A** | 320 / 374 ms |

- **The separating reading: the field's speed at the release.**
  - REV 47's 13 % gives no surge, and `B`'s 74 % does.
  - Holding the hold through SPIN_DN without a cap (U-4, `u_dn=1`) still surges (33.8 / 31.3 A). So the carrier is a
    release at a runaway field speed, not the state change.
- **The model's currents run high** (§4.11.9: 3.3-4× the bench's at speed). Compare within the table: B's surge is 7×
  REV 47's.

#### 4.12.3 Model changes (`spin2_model.py`, additive)

New modes:
- **`grab`** (floor-grab).
  - A straight drive at power 7 under the 2 A limit. From 1.0 s, a hand on the LEFT tyre: a damper (`grab_B`, N m s/rad)
    to a hand moving at `grab_v` of the commanded speed.
  - The hand's speed changes by up to `grab_a` of it every 1 / `grab_f` s: a sine, or (`grab_rnd` 1) random −1..1, or
    (2) random −1..0.
  - Prints each wheel's rate, the LEFT field's speed, the |err| 82..88 time, ticks against the field from it, the
    longest tick gap (LDHOLD's reading), and each fault: armed or not, lag or lead.
- **`overend`** (dual-limits).
  - Wheels up at `top_v` (21.3), from 175×10⁶: 245×10⁶ at 1 A for `ov_hold` (4) s, then 40 A and 165×10⁶ together. That
    is `overCommandStep()` then `limPowerCheck()`.
  - Prints the field's and rotor's speeds before the restore, then the DC-link peak, the time over 10 A, AT_SPEED and
    the full-power rate.

New switches, all off by default:
- **`u_arm`, `u_span`, `u_cap`, `u_cap_sec`**: U-1, U-2, U-5 (§4.12.4).
- **`u_give`, `u_jgate`, `u_dn`**: the rejected U-3, U-3b, U-4 (§4.12.5). `u_dn` also moves the blocked count's limiter
  half into SPIN_DN and onto the fold-back only.
- **`c4_state`**: the as-built disarm in any state but SPIN_UP / AT_SPEED (`:8881`), which the model lacked.
  - It matters on the floor. The steering object's scaling puts a held wheel into SPIN_DN, where the hold disarms.
  - `RAND` faults 3 of 16 without it and 6 with it. `HOLD` faults 0 without it and 1 with it.
  - The obstacle and every §5 row are identical, or within 0.2 ms of window time.
  - It is part of `B` and `FIX`.
- **`blkwin`**: the BLKWIN mirror in `block` mode, at every frame and at the harness's 5 ms poll. It also prints the
  window time split by armed and unarmed.
- **`lim_prog`** (an argument to `run()`): a limit change mid-run.

**The hands are harsher than the bench.**
- REV 46 passed its bench grab (2026-09-30 floor2, §3), but the model faults it 4 of 16 under `HOLD` and 14 of 16 under
  `RAND`.
- So grab faults are compared within a row, and the window time (|err| 82..88, the exposure) is the steadier reading.
- `HOLD` is the hand the run sheet asks for ("hold steadily"). `RAND` is a bound.

**Identity checks** (the commands in §4.12.11):
- `legs`, `block ob_n=16 ob_k=1000 $R48 $CAL` and `topspd $T1 $CAL top_v=21.3 top_over=1` printed the same lines before
  the edit and after it.
- `block` reproduces §4.10.8's 15 / 1 / 0, 1,080-1,738 ms, 87 back ticks.
- `topspd` reproduces §4.11.4's 245 at 1 A: field 64.8 %, rotor 3.4-3.5 %.

#### 4.12.4 The corrections

**U-1 · arm at the first fold-back (closes G-2).**
- **Mechanism.** On any pass in SPIN_UP / AT_SPEED where the fold-back acted since the previous pass (T-1's limiter):
  `lim_arm := 1` and `lim_pos := pos_`, whatever `lag_s` reads. If `lag_s` ≥ 64 the pass also sets back, as today.
- Every later fold re-arms at its own sector. The set-back no longer arms.

**U-2 · disarm only after a whole sector forward with no fold-back (closes G-3).**
- **Mechanism.** The disarm test becomes `pos_ − lim_pos ≥ LIM_SPAN` (2) in the field's direction, instead of ≥ 1.
- `lim_pos` is the sector of the most recent fold. So the hold disarms only once the rotor has crossed one whole sector
  forward without a fold-back.
- A wheel crawling at its limit folds within every sector, so it stays armed. That holds on the bench, where the gaps
  between folds were 6-10 ms against 60-120 ms per tick. It holds in the model too (23 ms against more than 100 ms).
- Any state but SPIN_UP / AT_SPEED still disarms, as built.

**U-5 · at the release, cap the field's speed (closes G-4).**
- **Mechanism.** When the hold disarms, by U-2 or by the state test:
  `|drv_incr| := min(|drv_incr|, 4 sectors / n)`, where n is the drive passes since the last fold.
- If the cap acts, `accel_now := 0`: the generator restarts its ramp from the capped speed toward the command.
- A sector is 2³²/6 of `angle_`, so the numerator is 2,863,311,531, and n is forced to at least 2.
- **The cap never binds a running wheel** (§4.12.6): the design, step, ramp and stepdn rows are identical.

**Invariants, by construction.**
- **(I-9′, U-1 + U-2)** The hold's reach.
  - It runs from the pass after a wheel's first fold-back action in SPIN_UP / AT_SPEED until the rotor has crossed a whole
    sector forward with no fold-back action, or the state leaves.
  - Throughout, the field is at most `LAG_LIM` ahead of the rotor's sector at the end of every drive pass.
  - So one back tick reads at most 64 + 42.7 = 106.7 < 125, and the next pass sets it back.
  - A fault would need two back ticks within one pass (0.52 ms). That is over 3,800 sectors a second, eight times the
    top speed's 494.
  - So **no tick against the field can fault while the wheel is limited.** It does not cover the contact transit before
    the first fold-back (§4.9.4).
- **(I-12, U-5)** Where the field restarts.
  - The rotor moved less than 2 sectors in those n passes (it had not reached `lim_pos` + 2 before the release). So the
    cap is at least twice its mean speed since the fold.
  - That is at least its present speed for any rotor whose present speed is at most twice its mean, such as uniform
    acceleration from rest. **The field never restarts behind such a rotor.**
  - On a U-2 release the rotor moved more than 1 sector, so the cap is at most 4× its mean speed. **The field restarts
    within 4× of the rotor's own speed**, not from a speed the hold had hidden.
- **I-2, I-11 (T-1) and D-3 stand.** `holdDecay` and its Z are as built.
- **I-1 stands.** Calm running never folds, so it never arms; every `design` leg is identical.

**The PASM sketch.** The build counts and checks it.
- **Flags:**
  - CMP / CMPS / TESTB with WC write C only (`p2kbPasm2Cmps`, `p2kbPasm2Testb`).
  - SUB, MOV, ADD and NEG without WC/WZ write none (`p2kbPasm2Sub`).
  - TJZ / TJNZ write none (`p2kbPasm2Tjz`, `p2kbPasm2Tjnz`).
  - QDIV writes none, and its result is ready 55 clocks after issue (`p2kbPasm2Qdiv`).
  - GETQX writes none without WC/WZ (`p2kbPasm2Getqx`).
  - FLES / FGES / FGE write none without WC/WZ (`p2kbPasm2Fles`, `p2kbPasm2Fges`, `p2kbPasm2Fge`).
- **So Z** (D-3's fact for `holdDecay`) is written once, by the head's `CMP WZ`, and by nothing after it on any path.

```
' passEnd (:8821-8822), after lim_seen:                              (T-1, §4.11.7)
                mov     fold_seen, foldback_cnt_
' gettgtincr's re-take (:8804-8805), beside lim_seen:
    if_nz       mov     fold_seen, foldback_cnt_

holdGate        mov     tmpX, duty_capped_              ' D-3's fact, as built
                add     tmpX, foldback_cnt_
                cmp     tmpX, lim_seen              wz  ' Z: no limiter acted. Written here only
                cmp     drv_state_, #DCS_SPIN_DN    wc  ' C: SPIN_UP or AT_SPEED
    if_nc       jmp     #.offState                      ' any other state: release (if armed), today's gate
                mov     tmpX, foldback_cnt_             ' T-1: did the FOLD-BACK act since the previous pass?
                sub     tmpX, fold_seen
                tjnz    tmpX, #.fold                    ' U-1: yes -- arm (or re-arm) here, whatever lag_s reads
                tjz     lim_arm, #.today                ' no fold, not armed: LAG_HOLD (T-1: a ceiling clamp alone)
                add     lim_n, #1                       ' U-5: passes since the arming fold
                mov     tmpX, pos_                      ' U-2: sectors forward since that fold
                sub     tmpX, lim_pos
                testb   drv_incr, #31               wc
    if_c        neg     tmpX
                cmps    tmpX, #LIM_SPAN             wc  ' LIM_SPAN = 2. C: a whole sector not yet crossed
    if_c        jmp     #.limHold                       '  still armed
.offState       tjz     lim_arm, #.today                ' (from the line above lim_arm is set: falls through)
                jmp     #holdRelease                    ' U-2's release with U-5's cap (cog RAM); returns from there
.today  _ret_   cmps    lag_s, #LAG_HOLD            wc
.fold           mov     lim_pos, pos_                   ' U-1: armed at the fold's sector
                mov     lim_n, #0
                mov     lim_arm, #1
.limHold        cmps    lag_s, #LAG_LIM             wc  ' as built (:8893-8905), less the two arming lines (:8906-8907)
    if_c        ret
                mov     tmpX, lag_s
                sub     tmpX, #LAG_LIM
                shl     tmpX, #24
                testb   err_, #31                   wc
    if_c        neg     tmpX
                sub     angle_, tmpX
                sub     prior_angle, tmpX
    _ret_       modc    _clr                        wc

' cog RAM (the LUT cannot take it, below)
holdRelease     mov     lim_arm, #0                     ' U-2: released
                fge     lim_n, #2                       ' n >= 2: the quotient stays under 2^31 (a positive signed cap)
                qdiv    ##LIM_CAP_K, lim_n              ' U-5: 4 sectors, 4 x 2^32 / 6 = 2_863_311_531, / n passes
                getqx   tmpX                            '  the cap (waits out the CORDIC's 55 clocks)
                testb   drv_incr, #31               wc  ' C: the field runs backward
    if_c        neg     tmpX                            ' the cap, signed as the field
                mov     tmpY, drv_incr
    if_nc       fles    drv_incr, tmpX                  ' forward: drv_incr := min(drv_incr, cap)
    if_c        fges    drv_incr, tmpX                  ' backward: drv_incr := max(drv_incr, -cap)
                sub     tmpY, drv_incr                  ' 0 when the cap did not act
                tjz     tmpY, #.rel
                mov     accel_now_, #0                  ' capped: the generator's ramp restarts from here
.rel    _ret_   cmps    lag_s, #LAG_HOLD            wc  ' then today's gate
```

- **What stays as it is.**
  - `driveFromRest` and `.clearRun` still zero `lim_arm`. `lim_n` needs no clearing: it is set at every arming and forced
    to at least 2 at use.
  - `lim_n` wraps only after 2³² passes (26 days) armed with no fold and no release.
- **UNVERIFIED, for the build:**
  - that `tmpY` is dead across `holdGate` (`holdDecay` and `passEnd` write it before reading);
  - the assembler's acceptance of `##` on QDIV's D (`p2kbPasm2Qdiv` documents `{#}D`; its example uses `##` with MOV).

**Cost (ESTIMATE from the sketch; the build counts from the listing).**

| Part | LUT longs | Cog longs | Time |
|---|---|---|---|
| `holdGate` (28 → 32) | +4 | — | about 0-4 clocks per running pass; +6 on a fold pass |
| T-1's `fold_seen` snapshots (`passEnd`, `gettgtincr`) | +2 | +1 register | 2 clocks per pass each |
| `holdRelease` | — | +14 | about 95 clocks on a release pass (QDIV 55 + 9 to issue + 14 instructions) |
| `lim_n` | — | +1 register | — |
| **Total** | **+6: 13 → 7 free** | **+16: 50 → 34 free** | worst window 2,221 + 95 ≈ 2,316 clocks, about 64 % of the frame (budget 75 %) |

- **Why `holdRelease` is in cog RAM.** The whole of U-5 in the LUT would need about 19 longs, which is 6 more than are
  free. A release is rare, and the CALL / JMP across the boundary is already the driver's pattern (`drvMotor`).
- **ABI: none.** No params or status long is added. DRIVER_REV 49.
- **Text to change:**
  - the comments at `:7048-7070`, `:7082-7087`, `:7807-7811`, `:8384-8387` and `:8858-8875`;
  - the `fit` notes at `:8503` and `:8516`.

#### 4.12.5 Candidates considered

All runs below are `$CAL`, 16 trials per cell. "Grab" cells read `HOLD` / `RAND`: faults of 16, then the |err| 82..88
time.

| Candidate | Modelled | Verdict |
|---|---|---|
| **U-1 + U-2 + U-5 (4 sectors)** = `FIX` | §4.12.6 | **Recommended** |
| U-1 + U-2, no cap | G-2 / G-3 as `FIX` (grab 0 / 318 ms; 2 / 862 ms). G-4: 33.8 / 31.3 A, over 10 A for 20-62 ms | Not enough: the release still carries the runaway speed |
| U-3: an armed pass that holds also gives way (`holdDecay` on every armed held pass; the evaluation's candidate) | G-4 closed: 0.45 / 0.87 A. With `FIX`, grab `HOLD` 0 → 2 faults and 386 → 952 ms; `RAND` 4 → 11; solid obstacle 16 / 0 / 0 → 15 / 0 / 1; rocking median latch 1,131 → 1,679 ms (max 2,396) | **Rejected.** See the note below the table |
| U-3b: while armed, `jerkStep`'s lag gate reads `LAG_SOFT` (no acceleration behind the set-back) | field 36-37 %, G-4 32.5 / 20.6 A | Rejected: not enough. D-3 decays only on fold passes, about 50 a second |
| U-4: the hold acts and stays armed in SPIN_DN (and the blocked count's limiter half follows it there, on the fold only) | G-4 with no cap: 33.8 / 31.3 A; with the cap: identical to the cap alone. With U-3 it was part of the 13-of-16 `RAND` row | Not needed: the release, not the state, carries G-4 |
| U-5 at 2 sectors (the bound itself) | G-4 0.42 / 0.56 A; but the 8 N·m step falls 99.8 → 98.2 % (path limiter engaged at 865 ‰) and 2 N·m −0.1 | Rejected: a cap equal to the rotor's mean speed can sit below a rotor still accelerating |
| U-5 at 3 sectors | G-4 2.04 / 2.09 A; step rows identical | Viable. 4 is chosen for I-12's lower bound (at least the present speed of a rotor accelerating uniformly from rest) |
| Disarm after N passes with no fold (a time window, as F-b) | not run | Rejected, DERIVED: the gap between folds is set by noise and is unbounded in principle, the reason F-b was not taken (§4.10.7) |

**Why U-3 is rejected.** The decaying field engages the steering path limiter: RIGHT slows to 19-29 %, so the line is
kept better. But the scaling unloads the held wheel, which then drops out of the hold more often. And a hand that pushes
the wheel on overtakes the decayed field. That is lead faults, the way REV 46 behaves: `RAND` 14 of 16.

#### 4.12.6 The measure of benefit (for Stephen; P5)

MODELLED unless marked: central parameters under `CAL`, 16 trials per cell. The model's currents run high (§4.11.9), so
currents are compared within a row.

| What a user sees | DRIVER_REV 48 + T-1 (`B`) | **+ U-1, U-2, U-5 (`FIX`)** | Standing |
|---|---|---|---|
| Driving into a solid obstacle (2 A): stopped by itself / pushed on / lag fault | 15 / 0 / 1; stopped 1,009-1,169 ms after contact | **16 / 0 / 0**; 1,009-1,359 ms (3 contacts about 270 ms later; the stop after the last tick is 1,002-1,282 ms) | MODELLED; bench REV 48: both trials stopped, 1,002 / 1,022 ms |
| The same: the field read in the fault band after the current limit acted (BLKWIN, 5 ms poll) | 6 hits on 3 contacts, up to 92 | **0** | MODELLED; bench REV 48: 1 hit per trial (85, 83) |
| A yielding obstacle (1,000 N/m) | 15 / 1 / 0; 1,080-1,738 ms | 15 / 1 / 0; 1,080-1,773 ms | MODELLED |
| A yielding obstacle (3,000 N/m) | 15 / 1 / 0; 1,031-1,325 ms (without `c4_state`) | 15 / 1 / 0; 1,032-1,323 ms | MODELLED |
| A hand holding a wheel steadily at the 2 A limit: lag faults of 16; time in the fault band | 1; 468 ms | **0; 386 ms** | MODELLED; bench REV 48: 1 fault in 1 grab |
| A rougher hand: lag faults of 16; time in the band | 6; 895 ms | **4; 791 ms** (one is at the grab's onset, before any limit acted) | MODELLED |
| The grabbed wheel's longest pause between ticks (LDHOLD) | up to 1,142 ms | up to 1,127 ms | MODELLED (the hand decides it) |
| The other wheel during the grab (does the platform keep its line?) | 91-100 % while the held one runs 9-21 % | 79-98 % | MODELLED: **neither keeps the line** (S-b) |
| End of a long current limit (1 A over-command, then full power): battery-current peak; time over 10 A | **34.0 / 33.9 A; 320 / 374 ms** | **2.96 / 2.56 A; 0 ms** (REV 47: 4.69 / 4.50 A) | MODELLED; bench REV 48: ~9.6 A abort, REV 47: clean |
| The same: the field's speed during the over-command (FOLLOW reads it) | 73-74 % of 245×10⁶, rotor 3.0 % | 42-45 %, rotor 4.4-4.5 % (`topspd`: 55-58 %, against 64.8 %) | MODELLED (S-b stands) |
| The same: full power reached after the restore | in 0.7-1.0 s (after the surge) | in 2.5 s (REV 47: 2.2 s) | MODELLED |
| Top speed, wheels up, 165-245×10⁶ at both supplies (T-1's rows) | §4.11.4 | **identical, every rung** | MODELLED |
| Spin legs (all nine): speed, err_pk, swing | 99.6-100.5 %, 68-76, 39-295 | identical, digit for digit | MODELLED |
| One-sided load, power 13: 1 / 2 / 4 / 8 N·m | 99.1 / 99.2 / 99.4 / 99.8 % (RIGHT 100 / 100 / 100 / 99.9) | identical; 8 N·m **99.9** / 99.9 | MODELLED |
| 1 / 2 / 4 N·m on 1.0-2.0 s, released: speed after | 99.7 / 99.8 / 99.9 % | 99.7 / **99.7** / 99.9 % | MODELLED |
| Ramps 200 / 1,000 / 3,000 mm/s² | 1,800 / 1,800, 560 / 559, 322 / 321 ms | identical | MODELLED |
| Wheels up, unloaded, and the slow-down kicks (80 → 20, 40 → 20, the stop from 147×10⁶) | +52 / +52 mV, +30 / +27 mV, 2.34 / 2.38 A | identical | MODELLED |
| FlySky slow-downs and reversals: lag faults of 15; band time | 0; 626 ms | identical | MODELLED |

**Rows that move the wrong way.**
- **2 N·m released:** 99.8 → 99.7 %, a tenth of a point, about 0.16 of a hall tick over the 1.5 s window. U-1 and U-2
  alone show the same.
- **The solid obstacle's slowest stop:** 1,169 → 1,359 ms after contact, on 3 of 16 contacts.
  - These contacts rebound one tick. The armed hold keeps the field at 64, where the trim lifts the duty more slowly than
    D-2's boost did at 80+. So the first fold after the last tick comes about 270 ms later.
  - The count after it is unchanged (F-a: exactly 1,000 passes). BLKSTOP's bounds hold: stand ≥ 988 ms, count
    988-1,012 ms.
- Every other row is identical, or better.

#### 4.12.7 Recorded, not acted on

- **S-b stands (§4.11.11).** While armed, `drv_incr` is not the field's speed. Two readers take it as the field's speed:
  - the steering object's shortfall (`shortfallNow()`), so the path limiter does not engage for a wheel held at its
    limit;
  - the harness's FOLLOW / FOLFALL.
- **Its fix is the rejected U-3**, or a measured rotor speed for those readers. A punch-list candidate, with LDPATH's
  premise (§4.12.8).
- **The model's REV 48 rows before this section lacked the as-built state disarm.** On the floor that understates the
  grab's exposure (`RAND` 3 → 6 faults with it). The obstacle and §5 rows are unaffected.

#### 4.12.8 Certification: each cell can fail on the second visit's logs

| Cell | Criterion | Its negative (the second visit, unless marked) | Premise |
|---|---|---|---|
| **BLKWIN** (floor-obstacle; I-9′) | as SRC_REV 77: no poll reads \|e\| or \|o_e\| 82..88 from the pass after a wheel's first limiter action until its next tick | `BM-BLKWIN` seq 386 `r_hit,1,r_emax,85`; seq 760 `r_hit,1,r_emax,83` | **Should change** (not required for this run): the flag should read `foldback_frames` alone, as T-1 arms on it. With `duty_capped` in the flag, a stall that met the duty ceiling first would open a window no hold guards (T-1's boundary, §4.11.7). No obstacle trial reaches the ceiling |
| **BLKSTOP / BLKLIMIT** | as defined, with the mirror fixed (G-1, SRC_REV 80) | `l_count,0,r_count,0` (seq 383, 757); first visit COAST `TIMEOUT` | Unchanged. `FIX` stand 1,000-1,282 ms, count 1,000 passes |
| **BLKFLT** | the trials latch with no `EV_FAULT` / `EV_FAULT_RESYNC` | first visit BRAKE (seq 338). It passed on the second visit, so it guards against regression; it does not certify U-1..U-5 | Unchanged |
| **LDFLT** (new, floor-grab; I-9′) | no `EV_FAULT` and no `EV_FAULT_RESYNC` from the grab's start to the leg's end, the gripped wheel slowed but moving (`BM-LOADW` `l_pct` 5-60, else NOMEAS) | `EV_FAULT_RESYNC` seq 16, `EV_FAULT` seq 19 | New |
| **OVRSTEP** (new, dual-limits; I-12) | after each over-command, the full-power step completes: `BM-POWER` why `NONE`, no `BM-ABORT` | `BM-ABORT` seq 161 `ABS_CURRENT`, `BM-POWER` seq 162 `ABORTED`; RIGHT never reached it (NOMEAS there) | New |
| **TOPSPD** (T-1; §4.11.10) | 185 and 195 rungs: AT_SPEED within 6 s; no `lag_held` while `duty_capped` advances and `foldback_frames` does not | rids 14 / 35 / 56 `STEADY_TIMEOUT` | As proposed in §4.11.10; its trace half needs SRC_REV 79 |
| LDHOLD (gripped wheel's tick gap ≤ 1,000 ms) | as defined | 99,999 ms (the fault) | **Must change, or it can fail a correct drive.** A steady hold near a stop gives 1,127-1,142 ms in the model under both drives. Judge it only when `l_pct` ≥ 15, or drop it |
| LDPATH (line mismatch ≤ 100 ‰) | as defined | 666 ‰ | **Will fail under `FIX`** (S-b): re-premise to NOMEAS while a wheel is held at its limit, or carry as a known failure |
| FOLLOW / FOLFALL (the over-command's field) | as defined | NOMEAS (the run stopped) | **Will fail** (S-b: field 42-58 %); same disposition as LDPATH |
| Regression guards: `dual-a` (SRVKEEP, LAGBND, TRKICK-A), `floor-auto` (SPINRATE, RAMPARR, SPINHOLD) | as defined | — (they passed; a drop is the regression) | Unchanged |

#### 4.12.9 Recommendation

**RULED (STEPHEN 2026-10-03, *"yes A"*): build U-1, U-2 and U-5 with T-1** (DRIVER_REV 49).

**RULING NEEDED (P5): build T-1 + U-1 + U-2 + U-5 (DRIVER_REV 49) for the third visit?**
- **Recommendation: yes.**
- **Why:**
  - Each closes one gap by construction (I-9′, I-12), and each gap is reproduced in the model with the bench's own
    readings.
  - Nothing else moves: one row loses 0.1 point, and one obstacle row is slower on 3 of 16 contacts.
  - The cost is about 6 LUT and 16 cog longs, with no ABI change.
- **What not to build:** U-3, the evaluation's third candidate. It closes G-4 but brings back REV 46's grab and obstacle
  exposure (§4.12.5).
- **Before the run sheet** (the arbiter's, not this design's): the harness changes in §4.12.8.
  - BLKWIN's flag on the fold-back;
  - the new LDFLT and OVRSTEP;
  - LDHOLD's and LDPATH's premises.

#### 4.12.10 Not checked, and the model's limits

- **The hand.**
  - No modelled hand reproduces the bench's grab exactly. Both are harsher than the bench (REV 46 faults 4 of 16 under
    `HOLD`), so fault counts are compared within a row. The band time is the steadier reading.
  - The grab's fault at the onset, before any limit acts, is the contact transit (§4.9.4). Nothing here changes it.
- **Not modelled:**
  - the default 27 A limit on an obstacle or grab;
  - Rev A;
  - unequal hall sectors (U-2 counts sectors);
  - a lead write moving `err_` (I-9′'s margin is 18 counts, §4.9.4);
  - the right board's silence (whether it reset is UNKNOWN; U-5 removes the modelled surge).
- **U-5's lower bound (I-12)** covers a rotor whose present speed is at most twice its mean since the fold. A sharper
  acceleration can restart the field behind the rotor. It is DERIVED as harmless, because the generator ramps up and
  the gap is a fraction of a sector, but it is not modelled beyond the step and release rows.
- **T-1's boundary** (a stall that meets the duty ceiling first, the 12 V DocoEng build) is still not run (§4.11.7).
- **The PASM sketch is not assembled.** Its costs are ESTIMATE.

#### 4.12.11 Reproduce

```
S=DOCs/plans/servo-model; CAL="pasm=1 v_dt=0.18 i_noise=3"; R47="acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1"
R48="$R47 cap_lift=48 d5_sticky=1 blk_fix=1"; T1="$R48 d5_fold_only=1"; B="$T1 c4_state=1"
FIX="$B u_arm=1 u_span=2 u_cap=1 u_cap_sec=4"
HOLD="grab_B=5 grab_v=0.45 grab_a=0.8 grab_f=5 grab_rnd=2 grab_n=16"
RAND="grab_B=5 grab_v=0.15 grab_a=1.0 grab_f=5 grab_rnd=1 grab_n=16"
python3 $S/spin2_model.py block ob_n=16 ob_k=50000 $B $CAL blkwin=1      # G-2 reproduced; and $FIX; ob_k=1000, 3000 ($T1 at 3000)
python3 $S/spin2_model.py grab $B $CAL $HOLD diag=1                      # G-3 reproduced; and $RAND; and $FIX
python3 $S/spin2_model.py grab $CAL $HOLD                                # the hands against REV 46; and $R47; and $RAND
python3 $S/spin2_model.py overend $R47 $CAL                              # G-4: REV 47; $B; $FIX
python3 $S/spin2_model.py overend $B $CAL u_arm=1 u_span=2 u_dn=1        # U-4 without the cap; u_cap=1 u_cap_sec=2 / 3 / 4
python3 $S/spin2_model.py overend $T1 $CAL u_give=1                      # U-3; and $B $CAL u_arm=1 u_span=2 u_jgate=1 (U-3b)
python3 $S/spin2_model.py grab $FIX $CAL $HOLD u_give=1                  # U-3 with FIX; $RAND; block ob_k=1000 / 50000
python3 $S/spin2_model.py step $FIX $CAL                                 # and u_cap_sec=2, 3; and $B
python3 $S/spin2_model.py release|design|ramp|wheelsup|stepdn|reversal $FIX $CAL   # 4.12.6; each against $B
python3 $S/spin2_model.py topspd $FIX $CAL top_v=21.3 top_over=1          # and top_v=19.2 top_lo=145 top_hi=185 against $T1
python3 $S/spin2_model.py legs                                           # identity: as before the edit
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 $R48 $CAL               # identity: 4.10.8's 15 / 1 / 0, 1,080-1,738 ms
python3 $S/spin2_model.py topspd $T1 $CAL top_v=21.3 top_over=1           # identity: 4.11.4, 245 at 1 A field 64.8 %
```

`$T1`, `$B` and `$FIX` do not include `$CAL`: pass it with each, as shown.

---

## 5. The measure of benefit (for Stephen's decision; P5)

All numbers are from the two-wheel model at its central parameters unless marked. **The model's absolute currents run
1.2-2.6× the logged ones** (legacy leg 5: model 0.41 A, logged 0.158-0.179 A; schedule legs 3-4: model 0.17-0.23 A,
logged 0.087-0.141 A), so **only current ratios are claimed**.

| What a user sees | Today | With D-1..D-3 (+D-4) | Confidence |
|---|---|---|---|
| Spin in place, speed held (all ten legs) | **57-94 %** on the schedule legs (MEASURED) | **99.6-100 %** on every leg, no hold, no path limiting (`design acc_shift=16 dB=1 boost_shift=10 dC=1`) | MODELLED. The model under-predicts today's slow/medium loss (§3.6) |
| Duty swing / err_pk while spinning | 803-1,647 / 84-113 (MEASURED) | 15-184 / 67-70 (central); 53-544 / 67-76 at the adverse corner | MODELLED |
| Current, spinning at the medium command, schedule against legacy **at equal speed** | Not comparable: SPINCTL's 1.89× / 2.40× compares 88-94 % against 100 % (MEASURED) | Schedule 0.16-0.17 A against legacy 0.41-0.70 A (model units): **2.5-4.4× less** | MODELLED (ratio) |
| Unloaded current (the schedule's 8-25× saving) | MEASURED (manual §7.3) | **Unchanged by construction**: placement untouched. Model wheels up 0.04 / 0.09 / 0.13 A before and after | DERIVED + MODELLED |
| One-sided load on a straight drive at power 13, applied in steady running, LEFT / RIGHT speed | 1 N·m: 98.6 / 99.3 %. **2 N·m (24 N at the tyre): 61.8 / 61.5 % with 7.4 A phase, no limit.** 4 N·m: 7.8 / 12.1 % | 1 N·m: 99.0 / 100 %. 2 N·m: 99.4 / 100 %. **4 N·m (48 N): 99.6 / 100 % at 12.4 A.** (+D-4, not taken: 99.7 / 99.6 / 99.3 %, partner 100 %) | MODELLED (`step`; D-1..D-3 re-run in phase 2, unchanged) |
| Where the field gives way | Wherever the cycle reaches the hold: at 0.05-0.14 A (MEASURED) | 8 N·m (97 N): 25 % at the 27 A limit, 1,050 limit frames in the window. (+D-4, not taken: 83 %, phase 21.5 A, peak 24.3 A) | MODELLED |
| A 4 N·m load 0.45 s after arrival, then released: speed after release | 83.9 / 82.9 % | **D-1..D-3: 40.4 / 41.0 % (stalls at the limit, §3.5).** +D-4 would give 99.9 / 100 %, but D-4 is not taken (§7 Q1): **40.4 / 41.0 % stands** | MODELLED (`release`; re-run in phase 2 with the wrapped error, unchanged) |
| Ramp leg at 3,000 mm/s², arrival / prediction | 696 / 320 ms (MEASURED); model 612 / 321 with the path limiter engaged | 322 / 321 ms, no hold | MODELLED |
| Ramp leg at 200 mm/s² and the FlySky gentle speed-up | 2,846 / 1,790 ms; half the set rate (MEASURED) | **Unknown.** The model does not reproduce today's failure here (arrives on time today) | UNKNOWN |
| SPINSYM RIGHT 1.36 | MEASURED, at unequal speeds | Re-judged at equal speed | UNKNOWN |
| Obstacle, blocked stop | MEASURED: latches 1.0-1.1 s on a solid object; rocks without latching on a yielding one (accepted, R18) | D-1..D-3 at `LAG_HOLD` 100: solid object latched 14 of 16, 987-1,102 ms after contact; rocking one 8 latched, 7 rocked 7.7 s, 1 fault (today: 10 / 5 / 1). D-4 at 86 would turn 9-10 of 16 rocking contacts into lag faults, so it is not taken (§7 Q1) | MODELLED (`block`); BLKLIMIT and the latch-time comparison guard it on the floor |

---

## 6. Certification

**Before the floor (wheels up):**
- The Visit 8 cells A-1, A-2, A-3, A-5 (rungs 3-8 duty and net current within ±5 %: the unloaded saving kept), A-6
  and A-7 on the new image.
- `tools/build-check.sh`.
- `tools/pasm_equiv` equivalence outside the changed routines, plus the frame budget.

**On the floor.** Each new cell has a negative that can fail it: the 2026-09-30 floor2 logs, today's binary, fail every
new cell.

| Cell | Criterion | The negative (today's floor2 data fails it) |
|---|---|---|
| **SPINRATE** (new) | every spin leg, every pair, both wheels: fol ≥ 97 % | schedule legs 57-94 % |
| **SPINHOLD** (new; I-1) | no held pass (`lag_held` unchanged) and no `EV_PATH_LIMIT` in any spin leg | every schedule leg engaged the path limiter 2-18 times |
| **LIMGIVE** (new; I-2) | over the whole session, every slot in which `drv_incr_now` falls below 98 % of the command while held has `foldback_cnt` or `duty_capped` advanced within its last 4 slots | floor-auto: path limiting (hence decays) on 6 legs with **no** `FOLDBACK` / `CURRENT_LIMIT` event in the session |
| **RAMPARR** (new, from the ramp legs' existing readings) | arrival within 10 % of the prediction on all four ramp legs, no `EV_PATH_LIMIT` | legs 1 and 3: 2,846 / 1,790 and 696 / 320 ms |
| **SPINCTL** (re-premised) | legacy over schedule mean current at medium ≥ 1.25, **judged only when both legs read fol ≥ 97 %**, else NOMEAS | floor2 leg pairs 3/5 and 4/6: schedule under 97 %, so NOMEAS, not the false PASS |
| **BLKLIMIT** (new; obstacle) | on the solid-object trial, `EV_FOLDBACK` engages before the protective stop latches, and the latch lands in today's 988-1,168 ms band | — (today passes it: 14 `FOLDBACK` events; its negative is a stand latched without the limit) |

**Kept unchanged:** SPINHUNT (A-3: swing ≤ 400, err_pk ≤ 76; the model predicts 15-544 / 67-76), SPINERR (A-4),
SPINFOL (A-8 agreement), SPINSYM (now at equal speed), SPINLEAD (after PL-168's window fix), SPINSTOP, SPINOFF, LAGBND,
POSTFLT, SPINPLAT, BLKSTOP, PROTCLR, BLKSHORT.

**Re-premised before the run (R8):** LDPATH / LDHUNT / LDHOLD need a load past the current limit, or they read NOMEAS.

**If D-4 is taken** (it is not: §7 Q1)**:** the coast and brake trials' latch times are compared against today's on the same obstacle. The
harness's `BLK_STAND_HI_MS` (derived from the lag at the hold, PL-168) is re-derived for a hold at 86.

---

## 7. Open questions for Stephen

Asked one at a time. Q2 and Q4 were design-internal and are decided by the reviewer (P3); Q1 and Q3 went to Stephen.

**Q1 — D-4: lower `LAG_HOLD` to ~86?**
- Without it, a heavy load that arrives right after a speed change can stall at the current limit, because the held
  field sits past the torque peak. That is one modelled case (40 % after release, against today's 84 %).
- With it, that case holds 99.9 %. But a stalled wheel stands 6 counts above the blocked test's 80 instead of 20, so a
  rocking obstacle may take longer to latch.
- Options:
  - **(a)** take D-4 at 86, with a phase 2 desk check of the blocked count on a rocking stand and BLKLIMIT and the
    latch-time comparison as floor guards. This finishes "torque up to the limit"; it risks R18's accepted obstacle
    behaviour.
  - **(b)** take D-4 at ~90. That leaves a 10-count margin, has not been modelled, and is a compromise on both sides.
  - **(c)** leave `LAG_HOLD` at 100 for 6.0. PL-105 stays, and with it the one modelled regression.
- **Recommendation: (a), conditional.** If the desk check shows the rocking latch lengthening, fall back to (c) before
  anything is built.

> **DECIDED 2026-10-01 (Stephen): (a), conditional.** Kept here in full so that anyone reopening it starts from the
> same ground.
>
> - **What we were solving.** At `LAG_HOLD` 100 the field held at the current limit sits 25-85° past the torque peak
>   (§3.5, PL-105), so the current there makes about half the torque it could. Under D-1..D-3 that leaves one modelled
>   regression: a 4 N·m load arriving 0.45 s after a speed change stalls the wheel at 27 A, and after release it runs
>   40 % of command against today's 84 %. With `LAG_HOLD` 86 the same case runs 99.9 % (re-run by the reviewer:
>   `release ... lag_hold=86`, LEFT 99.9 %, no fault).
> - **What it trades.** `bFrontProtect()` counts `|err| ≥ LAG_SOFT` (80) with no tick. A stalled wheel standing at
>   ~86 instead of ~100 has a 6-count margin instead of 20, so a wheel rocking against a yielding obstacle dips under
>   80 more often and restarts the count. The obstacle behaviour accepted for 6.0 (R18) could latch later.
> - **The choices.** (a) 86, behind a desk check; (b) ~90, a 10-count margin, unmodelled, halfway on both sides; (c)
>   keep 100 for 6.0 and carry PL-105 and the regression. (a) was taken because the desk check decides (a) against
>   (c) before anything is built, so R18 is never risked on the floor.
> - **The condition (phase 2, before any build).** Model a rocking stand against a yielding obstacle at 86 and at 100.
>   If the time to latch lengthens at 86, fall back to (c) and record it here.
> - **Floor guards.** BLKLIMIT (fold-back engages before the protective stop latches, latch in today's 988-1,168 ms
>   band) and the coast/brake latch-time comparison against the 2026-09-30 obstacle session (§6).
> - **Reopen if:** the desk check fails; BLKLIMIT or the latch-time comparison fails on the floor; calm running
>   peaks reach 86 (A-3's err_pk ≤ 76 is the guard, R2); or a sub-sector angle (§4.7) is taken up, which places the
>   hold at the peak properly and makes the constant moot.
>
> **CONDITION OUTCOME (phase 2 desk check, 2026-10-01): FAIL. Fall back to (c): `LAG_HOLD` stays 100 for the fix's release (6.1.0, R21).**
>
> - **How it was modelled.**
>   - `spin2_model.py block` runs a straight drive at power 7 (SLOW) under the obstacle session's 2 A limit
>     (`BM-BLKBUILD limit_a,2`) into a one-sided spring at each tyre.
>   - `bFrontProtect()` is ported line for line (`:2898-2904`). It counts each 1 ms front pass with `|err| ≥ LAG_SOFT`,
>     no hall tick, a non-zero command and a driving state, and latches at `BLOCKED_PASSES` 1,000 (`:7245`).
>   - Each case runs 16 contacts, spread over one hall sector.
>   - The solid object is 50,000 N/m. The rocking object is 1,000 N/m (and 3,000 N/m): the stiffnesses at which
>     `blockcal` shows today's drive giving both of the session's outcomes. The stiffness is chosen, not measured.
> - **Today's drive against the session (the calibration, MODELLED against MEASURED).**
>   - **Solid object:** 15 of 16 latched, 1,000-1,048 ms after the last tick. MEASURED: the band is 988-1,168 ms and the
>     BRAKE trial latched at 1,097 ms.
>   - **Rocking object, 10 of 16 latched:** 1,055-1,157 ms after contact, 1,022-1,034 ms after the last tick.
>   - **Rocking object, 5 of 16 rocked for the whole 7.7 s without latching:** ±14-22 hall ticks back and forth, err_pk
>     114-122, no fault. MEASURED (the COAST trial): about 6 s of rocking, err peaks 114-120, no fault.
>   - **Rocking object, 1 of 16 took a lag fault**, as the first visit's FC_LAG did.
>   - So one modelled obstacle gives both trials' outcomes, as the session's one obstacle did.
>   - **Where the model differs:** its lag returns to 80 within 0-48 ms of a tick (stands 1,000-1,048 ms). The session
>     took about 97 ms on the latched RIGHT and about 640 ms on its partner (`logscan.py obst`; BM-TS samples are
>     4 ms). So the model's stands run 49-97 ms short of the BRAKE trial's 1,097 ms.
> - **The comparison (MODELLED).** Each cell is latched / rocked 7.7 s without a latch / lag fault, then the
>   contact-to-latch median and range in ms:
>
>   | Obstacle | Parameters | Today (100) | D-1..D-3 at 100 | D-1..D-3 at 86 |
>   |---|---|---|---|---|
>   | Solid, 50,000 N/m | central | 15 / 0 / 1; 1,023 (1,004-1,620) | 14 / 0 / 2; 1,005 (987-1,102) | 12 / 0 / 4; 1,019 (1,006-1,030) |
>   | Solid, 50,000 N/m | refit (§3.6) | — | 14 / 1 / 1; 1,030 (1,021-1,139) | 15 / 0 / 1; 1,028 (1,016-1,092) |
>   | Rocking, 1,000 N/m | central | 10 / 5 / 1; 1,072 (1,055-1,157) | 8 / 7 / 1; 1,062 (1,045-1,124) | 7 / 0 / **9**; 1,083 (1,075-1,100) |
>   | Rocking, 1,000 N/m | refit | 9 / 6 / 1; 1,093 (1,081-3,563) | 6 / 6 / 4; 1,082 (1,075-1,450) | 6 / 0 / **10**; 1,086 (1,076-1,098) |
>   | Rocking, 3,000 N/m | central | — | 10 / 5 / 1; 1,025 (1,010-1,975) | 6 / 0 / **10**; 1,043 (1,037-1,047) |
>
> - **Verdict.**
>   - **Taken literally, the latch lengthens at 86, but only marginally.** Against 100 the medians move +14 to +21 ms
>     at the central parameters and −2 / +4 ms at the refit, all inside the solid-object band.
>   - **The decisive change: at 86 a rocking stand ends in a lag fault, not a latch.** 9-10 of 16 contacts fault at
>     86, against 1-4 at 100, and none rocks on. The protective stop that BLKSTOP, BLKLIMIT and the latch-time
>     comparison expect is replaced, not delayed. That is the R18 risk the condition exists to keep off the floor, so
>     the condition fails on either reading.
>   - **Why it faults (DERIVED, not only modelled).** Take a field held at 86-88 that the load pushes back one hall
>     sector (42.7 counts). The lag then reads 128.7-130.7. The 8-bit `err_` wraps that to −127..−125, which trips the
>     fault test (`|err_| ≥ 125`, `:7929-7930`). Any backward tick from a lag of 82.3-88.3 faults this way. At 100 the
>     same tick reads −113 and does not fault.
> - **What stands as a result.** PL-105, and the one modelled regression of §3.5 (40.4 / 41.0 % after a 4 N·m early
>   load is released, R3), are carried into 6.0.
> - **Not checked.**
>   - The default 27 A limit: every run used the session's 2 A.
>   - Non-uniform hall sectors: the model's are 42.7 counts each, and real ones move the 82.3-88.3 window per sector.
>   - The PL-55 duty ceiling in SPIN_DN, and the driver's phase-current estimate (the model folds back on the true phase
>     current).
>   - A wheel-by-wheel contact geometry: both tyres meet the spring.
>   - The obstacle's stiffness, which is unmeasured.
>   - Option (b): one informational run only, not part of this decision. `LAG_HOLD` 90 on the 1,000 N/m rocking
>     object gave 11 / 3 / 2, median 1,086 ms (1,066-4,142). Its held lag sits 1.7 counts above the fault window.

**Q2 — keep the desk model in the repository?**
- The design's numbers come from `spin_model.py` / `spin2_model.py`, which sit in this session's scratch directory.
  This task was not allowed to add them.
- Options:
  - **(a)** phase 2 adds them beside `sim_servo.py` in `DOCs/plans/servo-model/`. Anyone can then re-run every number
    here (P10).
  - **(b)** leave them as scratch: the numbers become unreproducible.
- **Recommendation: (a).**

> **DECIDED 2026-10-01 (reviewer, a design-internal choice, P3): (a).** The numbers are only as good as their
> reproducibility (P10). Phase 2 adds `spin_model.py`, `spin2_model.py` and `logscan.py` beside `sim_servo.py`.
> The alternative, (b), was rejected because every figure in §3-§5 would become unrecheckable.
> **Done 2026-10-01 (phase 2):** all three are in `DOCs/plans/servo-model/`, and §9 runs them from there.

**Q3 — proceed with the slow/medium depth unproven?**
- Options:
  - **(a)** go to phase 2. Its first step is the desk refit H-a (§3.6), which is cheap and desk-only. The design does
    not change if the refit succeeds, and SPINRATE catches a residual.
  - **(b)** hold the design until the model reproduces 57-94 %.
- **Recommendation: (a).** The only mechanism found is removed by construction, and (b) delays a release item for a
  refinement that changes no line of the design.

> **DECIDED 2026-10-01 (Stephen): (a).** Phase 2 starts with the desk refit H-a (§3.6). **If the refit reveals a
> second mechanism the design does not remove, phase 2 stops and it goes back to Stephen before anything is built.**
> (b) was rejected because it delays a release item for a refinement that changes no line of the design, and may not
> converge while Iz and the winding inductance are unmeasured. SPINRATE (§6) is the floor's catch for a residual.

**Q4 — how the drive "says so".**
- Options:
  - **(a)** the existing events, with their meaning documented: after D-3 a give-way coincides with `EV_FOLDBACK` (or
    the duty ceiling) and, on two wheels, `EV_PATH_LIMIT`.
  - **(b)** a new public "torque-limited" signal, an event kind or a getter, mirrored in `isp_steering_2wheel` (the
    other half of PL-102).
- **Recommendation: (a) for 6.0.** No API growth, and PL-102 keeps the public getter.

> **DECIDED 2026-10-01 (reviewer, a design-internal choice, P3): (a).** D-3 makes every give-way coincide with a
> limiter count by construction (I-2), so the existing events already mean "a wheel at its limit"; phase 2 documents
> that meaning. (b), a public torque-limited signal, was not rejected on merit: it stays with PL-102 and would need an
> API addition mirrored in `isp_steering_2wheel`, which is release scope and Stephen's.

---

## 8. Side findings (recorded, not acted on)

- **The manual's §5.2 sign warning.** Under §2.4's frame, L's measured fall with speed means the voltage's angle from
  the magnets *grows* with speed. That is the textbook's sign. The manual says "do not design from that model on this
  motor". Its owner should re-read that paragraph against §2.4 (DERIVED here, unmeasured).
- **SPINCTL's PASS** compared unequal speeds (N6). The re-premised cell (§6) cannot pass that way again.
- **The obstacle session already reaches the fold-back** (14 events), which is why BLKLIMIT has a working baseline.

---

## 9. Reproduce

`S=DOCs/plans/servo-model` (from the repository root; the scripts run from any directory). Every run uses the wrapped
`err_` (§3.3); add `wrap=0` to reproduce a phase 1 number exactly.

```
python3 $S/logscan.py trace                     # leg 7's BM-TS limit cycle (1.1)
python3 $S/logscan.py rc                        # the FlySky 200 mm/s^2 speed-up (1.1)
python3 $S/logscan.py obst                      # the obstacle session's stand traces, ticks and |err| 80 crossings (7 Q1)
python3 $S/spin_model.py checks                 # wheels-up negatives (3.3)
python3 $S/spin_model.py legs                   # one wheel, the ten legs (1.3, 3.4)
python3 $S/spin_model.py legs J=0.045
python3 $S/spin_model.py trace seed=7           # the modelled BRISK cycle (3.3)
python3 $S/spin2_model.py legs                  # two wheels + the path limiter (3.4)
python3 $S/spin2_model.py jscan                 # inertia scan, today's drive (3.4)
python3 $S/spin2_model.py legs e90_L18=53 Tnoise=0.4 Iz=0.30
python3 $S/spin2_model.py design acc_shift=16   # the gain alone (3.4, 4.7)
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 dC=1                          # the design (5)
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 dC=1 e90_L18=53 Tnoise=0.4 Iz=0.42
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 e90_L18=60 Lh=0.00037 Iz=0.18
python3 $S/spin2_model.py jscan acc_shift=16 dB=1 boost_shift=10
python3 $S/spin2_model.py step                  # load steps, today (5)
python3 $S/spin2_model.py step acc_shift=16
python3 $S/spin2_model.py step acc_shift=16 dC=1
python3 $S/spin2_model.py step acc_shift=16 dB=1 boost_shift=10 dC=1
python3 $S/spin2_model.py step acc_shift=16 dB=1 boost_shift=10 dC=1 lag_hold=86
python3 $S/spin2_model.py release               # load release (5)
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 lag_hold=86
python3 $S/spin2_model.py rtrace acc_shift=16 dB=1 boost_shift=10 dC=1    # the stall at the limit (3.5)
python3 $S/spin2_model.py ramp                  # ramp legs (5)
python3 $S/spin2_model.py ramp acc_shift=16 dB=1 boost_shift=10 dC=1
python3 $S/spin2_model.py wheelsup
python3 $S/spin2_model.py wheelsup acc_shift=16 dB=1 boost_shift=10 dC=1
python3 $S/spin2_model.py design dA=1           # rejected: edge-sampled P term (4.7)
python3 $S/spin2_model.py design dA=1 dC=1 kp_shift=2
# phase 2: H-a, the refit (3.3, 3.6)
python3 $S/spin_model.py wall                   # the torque wall over (e90_L18, Lh); then the fine grid
python3 $S/spin_model.py wall fine=1
python3 $S/spin_model.py checks e90_L18=52 Lh=0.00085
python3 $S/spin_model.py ladder e90_L18=52 Lh=0.00085
python3 $S/spin_model.py start e90_L18=52 Lh=0.00085
python3 $S/sim_servo.py ladder e90=52.0
python3 $S/spin2_model.py legs e90_L18=52 Lh=0.00085
python3 $S/spin2_model.py legs e90_L18=53 Lh=0.00065
python3 $S/spin2_model.py legs e90_L18=54 Lh=0.00055
python3 $S/spin2_model.py legs e90_L18=52 Lh=0.00085 Tnoise=0.4
python3 $S/spin2_model.py jscan e90_L18=52 Lh=0.00085
python3 $S/spin2_model.py design acc_shift=16 e90_L18=52 Lh=0.00085
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 dC=1 e90_L18=52 Lh=0.00085   # also =53/0.00065, =54/0.00055
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 dC=1 lag_hold=86 e90_L18=52 Lh=0.00085
python3 $S/spin2_model.py step acc_shift=16 dC=1                 # D-3 without D-2: 76 % (wrap=0: the phase 1 'fault')
# phase 2: D-4's condition (7 Q1); add e90_L18=52 Lh=0.00085 for the refit rows
python3 $S/spin2_model.py blockcal ob_n=8                         # the obstacle's calibration grid, today's drive
python3 $S/spin2_model.py block ob_n=16 ob_k=50000                # solid, today
python3 $S/spin2_model.py block ob_n=16 ob_k=1000                 # rocking, today
python3 $S/spin2_model.py block ob_n=16 ob_k=50000 acc_shift=16 dB=1 boost_shift=10 dC=1
python3 $S/spin2_model.py block ob_n=16 ob_k=50000 acc_shift=16 dB=1 boost_shift=10 dC=1 lag_hold=86
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 acc_shift=16 dB=1 boost_shift=10 dC=1
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 acc_shift=16 dB=1 boost_shift=10 dC=1 lag_hold=86
python3 $S/spin2_model.py block ob_n=16 ob_k=3000 acc_shift=16 dB=1 boost_shift=10 dC=1
python3 $S/spin2_model.py block ob_n=16 ob_k=3000 acc_shift=16 dB=1 boost_shift=10 dC=1 lag_hold=86
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 acc_shift=16 dB=1 boost_shift=10 dC=1 lag_hold=90   # informational
# «#3645» D-5 (4.9). The design = the D-1..D-3 flags + d5=1 (and blk_lim=1, which acts only in block mode). Every new
#  parameter defaults off: `release` and `release acc_shift=16 dB=1 boost_shift=10 dC=1` still print 83.9 / 82.9, 40.4 / 41.0
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1                 # the release case
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 e90_L18=52 Lh=0.00085    # refit; drop d5=1 for D-1..D-3
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 e90_L18=53 Tnoise=0.4 Iz=0.42   # adverse; likewise
python3 $S/spin2_model.py rtrace acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1                           # no stall at the limit
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1                           # diff against the run without
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 e90_L18=52 Lh=0.00085     #  d5=1: identical but the
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 e90_L18=53 Tnoise=0.4 Iz=0.42   #  header line
python3 $S/spin2_model.py jscan acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1
python3 $S/spin2_model.py step acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1                             # and without d5=1
python3 $S/spin2_model.py ramp acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1                             # diff: identical
python3 $S/spin2_model.py wheelsup acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1                         # diff: identical
python3 $S/spin2_model.py block ob_n=16 ob_k=50000 acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1   # solid; + e90_L18=52 Lh=0.00085
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1    # rocking; + the refit
python3 $S/spin2_model.py block ob_n=16 ob_k=3000 acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1
python3 $S/spin2_model.py block ob_n=16 ob_k=50000 acc_shift=16 dB=1 boost_shift=10 dC=1             # D-1..D-3, re-run: as 7 Q1
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 acc_shift=16 dB=1 boost_shift=10 dC=1              # D-1..D-3, re-run: as 7 Q1
python3 $S/spin2_model.py block ob_n=16 ob_k=50000 acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1        # D-5b's negative: 0 latch
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 acc_shift=16 dB=1 boost_shift=10 dC=1 blk_lim=1    # R-c: the blocked count alone
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1 lag_hold=86   # + D-4
# D-5's candidates (4.9.6)
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 d5_back=0               # C2
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 d5_step=4               # C3
python3 $S/spin2_model.py block ob_n=16 ob_k=1000 acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 blk_lim=1 d5_step=4
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 d5_sticky=1             # C4; also step, and the
                                                                                                      #  five block cells, + d5_sticky=1
python3 $S/spin2_model.py design acc_shift=16 dB=1 boost_shift=10 dC=1 lag_hold=64                   # C5
# D-5's falsifier (4.9.8)
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 lag_lim=21              # R-a: also 43, 53, 75, 90, 97
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 lag_lim=75 lag_soft=70  # R-b; control: drop d5=1 lag_lim=75
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 d5=1 lag_lim=90 lag_soft=95  # R-b; control: drop d5=1 lag_lim=90
python3 $S/spin2_model.py release acc_shift=16 dB=1 boost_shift=10 dC=1 e90_L18=70                   # the peak moved instead of the hold
```

Run times depend on the machine; independent runs can go in parallel.
