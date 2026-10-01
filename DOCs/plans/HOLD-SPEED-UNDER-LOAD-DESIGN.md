# Hold speed under load — design (PL-167, «#3640», phase 1 of 2)

**Status:** DESIGN, approved (§7). No driver code is changed by this document. **Release: 6.1.0** (R21: 6.0.0 ships
first with PL-167 as a Known Issue).
**Phase 2, desk steps (2026-10-01):** the H-a refit (§3.6) and D-4's condition (§7 Q1) are recorded. H-a did not
reproduce the slow/medium depth and revealed no second mechanism; D-4's condition failed, so `LAG_HOLD` stays 100.
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

**Status: DESIGN, for Stephen's ruling (P5). No driver code.** Plan §1.1. Not to be confused with *R18.4 D-5*, the
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
