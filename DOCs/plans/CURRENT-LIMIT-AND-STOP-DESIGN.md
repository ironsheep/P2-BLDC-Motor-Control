# Current limiting and stopping from speed — one design

«#3557», phase 1 of 2. Plan §R16.5 (Sprint Revision 2026-09-16). This document changes no source; «#3558»
builds exactly what it approves.

**Scope, STEPHEN 2026-09-16:** *"yes A - i want intelligent behavior to limit current vs. aborting where this is
the right thing to do for the dirving system"*. That covers S-2 (the current limit), C-5 (the lag-limited ramp),
the PL-55 stop and the protective stop. On the protective stop, STEPHEN 2026-09-16: *"yes your A"*.

Units used throughout (DERIVED from `isp_bldc_motor.spin2`):
- **`err_`** is `angle_ - rotor angle`, shifted right by 24 bits. So 256 units make one hall cycle
  (360° electrical), and 1 unit is 1.41°.
- **The driver's increment** is `drv_incr`. At the 6.5″ ceiling of 172,000,000 it advances `angle_`
  by 10.25 units per drive pass. At 75 % (110,250,000) it advances 6.57 units.
- **A drive pass** is 522.7 µs (PL-50). A control frame is 22.7 µs.

---

## 1 · The stop-current mechanism

**The duty servo regulates load angle, never current.**
- Each control frame, `duty_` moves by `(|err_| − 42) × duty_up or duty_dn >> 8`
  (`isp_bldc_motor.spin2:3740-3753`), with `duty_up := 18` and `duty_dn := 4` (`:506-507`).
- Duty can fall only while the lag is below 42 units (59°), and then at 4/256 per frame.

**What happens during a stop.** `.rampDn` lowers the field's speed by `ramp_down` (50,000) every pass, and
keeps the bridge driven until zero (`:3507-3538`). MEASURED on the unloaded half-speed stop
(`src/logs/_OLD/debug_260915-135838.log:97-199`, LEFT NEG):
- `e` keeps the motoring sign, −22 to −70, through SPIN_DN, exactly as at AT_SPEED (`:80-96`). The rotor
  still lags the field in the direction of motion. The motor is **pushing**, not braking.
- `d` falls only from 18,777 to 16,646 in about 100 ms.
- `i` rises from 931 to 1,130 mV over the same span.

**The mechanism (DERIVED).**
- Back-EMF falls with speed, but the servo holds duty almost constant, because the lag angle it regulates
  has not changed.
- The voltage across the winding therefore grows, and the current grows with it.
- The unloaded wheel would coast to rest faster than the ramp: `stop()` coasts at 370–510 ticks/s² against
  the ramp's 254 (VISIT-2-RESULTS.md §4). So the driver is spending current to hold the wheel *back*
  to the ramp.
- From 75 %, the same 20–50 % rise crosses the harness's 10 A abort (VISIT-3-RESULTS.md §2.1).

**The candidate this rules out:** field angle during the ramp. There is no sign change in `e`, so the rotor
never leads the field on this rig.

**What it cannot rule out:** braking lead on a loaded platform. Robot mass would make the rotor lead during
a stop. The design below handles both directions.

## 2 · The spin-up fault signature

MEASURED (VISIT-2-RESULTS.md §6): at `ramp_inc` 500, 2,000 and 10,000 the motor faults 96–186 ms after the
start. It does so after 1–2 ticks of motion, at 123–219 mV, with `dsat` FALSE, and `e` saturates at 127.

**DERIVED:** the field outruns the rotor before the duty servo has climbed from `duty_min`. Duty is not
saturated; it is *slow*. So C-5's trigger as the study wrote it (`|err_| > lag_soft AND duty_ >= duty_max_`)
would never fire on these faults. The trigger has to be the lag alone.

## 3 · The design — four mechanisms, one invariant each

### 3.1 Signed lag, computed once per drive pass

At the top of `drvMotor`:

`lag_s := err_`, negated when `drv_incr` is negative.

- `lag_s > 0`: the field is ahead of the rotor in the direction of motion (motoring).
- `lag_s < 0`: the rotor is ahead of the field (braking).

This is one new cog register and about 4 instructions.

### 3.2 Lag-limited field (C-5, redesigned from the measured signature)

Two compile-time PASM constants, not params. They are properties of the commutation, not of the user's
setup.

| Constant | Units | Angle | Role |
|---|---|---|---|
| (servo set point, existing) | 42 | 59° | where `duty_` settles |
| `LAG_SOFT` | 80 | 112.5° | the ramp stops chasing the rotor |
| `LAG_HOLD` | 100 | 140.6° | the field stops advancing |
| (fault, existing) | 125 | 175.8° | a genuine mechanical event only |

**Rules, applied each drive pass:**
1. **Field hold.** If `lag_s > LAG_HOLD`, skip `angle_ += drv_incr` this pass (at `.justIncr`). The field
   waits for the rotor. The duty servo keeps climbing, because the lag is still above 42.
2. **Ramp-up hold.** If `lag_s > LAG_SOFT`, `.rampUp` does not add to `drv_incr` this pass.
3. **Ramp-down hold.** If `lag_s < −LAG_SOFT`, `.rampDn` and `.slow2Chg` do not subtract from `drv_incr`
   this pass. The field does not decelerate faster than the rotor can be braked.

**Invariant:** `|err_|` cannot exceed `LAG_HOLD` plus one pass's increment (100 + 10.25 < 125) through the
field's own motion. The 176° fault is reachable only when the rotor is driven backwards by more than 25
units within one 523 µs pass: a jam, a lost hall, or an external back-drive.

**Consequences:**
- A load the motor cannot follow becomes **speed droop**: the field advances only as fast as the rotor.
- `ramp_inc` stops being a fault generator (README's oldest known issue).
- `drv_state` still reaches AT_SPEED once `drv_incr` reaches its target, even while the field is being held.
  No new DCS state is added: that would be an ABI enum change. Visit 4 observes droop by speed, not by state.

**The AT_SPEED ripple check:** the unloaded trace swings −22 to −70 (`135838:80-96`). The largest excursion
is 10 units under `LAG_SOFT`. On a loaded platform the servo set point stays at 42, so the ripple rides on the
same centre.

### 3.3 The stop: remove the cause (PL-55)

**Feed-forward duty ceiling during a ramp-down.** It is set on entry to SPIN_DN or SLOW_TO_CHG:
- `duty0 := duty_` and `incr0 := |drv_incr|`.

Then, each pass while ramping down:

`duty_cap_ := duty0 × |drv_incr| / incr0`, floored at `duty_min_`.

In every other state, and whenever `lag_s > LAG_SOFT` (the motor really needs the torque),
`duty_cap_ := duty_max_`.

The control loop's `fles duty_, duty_max_` becomes `fles duty_, duty_cap_`. That is the same instruction
count.

**Invariant:** during a stop, drive voltage falls in proportion to field speed, and so to back-EMF. The winding
voltage, and so the current, falls along the ramp instead of rising.

The arithmetic is 32×32 over 32, so it uses the CORDIC multiply and divide, once per pass. PASM2 semantics
for that are looked up in p2kb at «#3558». No new params are needed.

**New deceleration.**
- **Unloaded:** unchanged at 254 ticks/s². The ramp is still the law, and the cap lifts at `LAG_SOFT` if the
  rotor falls behind. «#3559» computes early stops from 254, as today.
- **Loaded (rotor leads):** rule 3 holds the ramp. The stop is then as fast as braking current within the
  limit (§3.4) allows. So a heavy platform stops **later** than the ramp predicts, never with a fault and
  never above the limit. «#3559»'s band applies within the limit, and its doc says so.

### 3.4 Current protection from the MOSFET ratings (S-2)

**What is being protected.** Both revisions use the same MOSFET, the Micro Commercial MCAC85N06Y, so the
limits are the same for Rev A and Rev B. Only the conversion to millivolts at the sense pin differs. The
datasheet values are recorded in `BOARD-REVISION-FACTS.md` §1.4. STEPHEN 2026-09-16: *"revB exists because
we could damage rev A boards"*.

**The quantity that matters is phase current, and the board measures DC-link current.** A MOSFET carries its
phase's current. The shunt carries the bridge's total return current. The two are related through the
modulation depth.
- **Modulation** (DERIVED, `init()`): phase amplitude is `(duty_ >> 4) / (frame_cnt / 2)` of the bus, so
  m = `duty_ / (4 × frame_cnt)`. That is about 1.0 at `duty_max`, since `duty_max ≈ 4 × frame_cnt`.
- **Current** (DERIVED, sinusoidal three-phase power balance):
  `I_dc = 0.75 × m × I_phase_peak × cos φ`, so **`I_phase_peak ≥ I_dc / (0.75 × m)`**.
- The estimate is a **lower bound**, because cos φ ≤ 1. At low modulation the same DC-link current means a
  much larger phase current. So a fixed DC-link limit does not protect the MOSFETs during a start or a stall.
  The limit must scale with `duty_`.

**The limits (DERIVED from the datasheet).** Assumptions, all chosen to be conservative, and each one named:
- ambient 50 °C, in an enclosed robot
- junction held at or below 125 °C (the part is rated to 150 °C)
- R<sub>θJA</sub> 55 °C/W (the datasheet's 1 in² 2 oz copper figure; the board's own copper area is not known)
- R<sub>DS(on)</sub> 3 mΩ, the maximum at V<sub>GS</sub> 10 V, × 1.9 for 125 °C, giving 5.7 mΩ. The gate drive is
  10 V on Rev A and 12 V on Rev B (facts file §1.4, §2).
- each MOSFET in a leg carrying half of its phase's conduction
- a 22.2 V bus

| Limit | Value, phase peak | Derivation |
|---|---|---|
| **Continuous (thermal)** | **27 A** | Allowed dissipation is (125 − 50) / 55 = 1.36 W per MOSFET. Conduction loss is 0.25 × I² × 5.7 mΩ. Switching loss is 0.5 × 22.2 V × (0.64 × I) × (6.7 + 26.9 ns) × 44 kHz. The sum reaches 1.36 W at I ≈ 27.5 A; rounded down. |
| **Peak (fold-back)** | **40 A** | 0.75 × the package-limited 54 A continuous rating at T<sub>C</sub> 100 °C. I<sub>DM</sub> 390 A is far above it; the package limit governs. |

**What this rig already does, as lower bounds** (DERIVED from the recorded DC-link currents and duties):
- unloaded half speed, 6.2 A at m = 0.77: at least 10.8 A peak
- a stop from 75 %, up to 11 A at about m = 0.7: at least 21 A, briefly
- a ramp-22 start peak of 7.2 A at an unrecorded m: at least 9.6 A even at m = 1

Unloaded running sits under both limits. Brief stop peaks sit under the peak limit, and §3.3 removes them.
So on this rig the limits should engage only under genuine overload, a stall, or a test stimulus.

**Layer 1: peak fold-back, in the PASM control loop, every 22.7 µs.**
- **Test:** is `sense_i_ × 16 × frame_cnt` ≥ `3 × I_PEAK × rSense × max(duty_, duty_floor)`? This is the
  lower-bound estimate rearranged so the loop never divides. Spin2 precomputes the constant factors at
  start into one param, `i_limit_k`.
- **`duty_floor`** is m = 0.1. Below it, true phase current is physically small (it is bounded by
  m × V<sub>bus</sub> / R). The floor also stops sense noise at `duty_min` from reading as a large phase
  current. On Rev A, ±3 mV of noise at m = 0.1 is under 8 A.
- **On exceed:** `duty_ -= duty_ >> 6`, about 1.6 % per frame, a time constant of about 1.4 ms. The servo add
  is skipped for that frame.
- The multiply fits within the 16×16 range if `duty_` is scaled first; the exact PASM2 multiply semantics are
  looked up in p2kb at «#3558». About 8 instructions.

**Layer 2: thermal derate, in the front cog, every 1 ms pass.**
- **Estimate:** the same phase-peak lower bound, from hub `sense_i_mV` (net of the rest zero) and `duty`,
  smoothed with a 1 s time constant. There is no transient thermal impedance curve in the datasheet, so a
  short window is the conservative choice.
- **Derate:** when the smoothed value reaches the 27 A continuous limit, the front cog rewrites `i_limit_k`
  for 27 A. It restores 40 A once the value falls below 22 A.
- **Result:** a sustained overload folds back to a thermally safe level and slows the motor. Nothing aborts.

**Invariants:**
- The instantaneous lower-bound phase current cannot stay above 40 A.
- The one-second average cannot stay above 27 A.
- Both hold in every state, motoring or plugging.

**Not covered, and stated as such:**
- **Voltage.** V<sub>DS</sub> is 60 V against a bus of at most 24 V (a 2.5× margin), and the body diodes clamp
  each phase to the bus. Bus pumping during regeneration depends on the battery, and no layer here can
  limit it.
- **Rev A's gate-driver spikes.** §1.4 of the facts file infers that Rev A's damage more likely came from negative
  switching spikes at its MIC4604 driver. Lower current at switch-off reduces that spike energy, but it does
  not replace the protection Rev B added.

**Interlock with §3.2:**
- Lower duty lets the lag grow, so the field hold engages, and the result is droop, not a fault.
- A stalled rotor ends at the limit with the field held, which is what §3.5 detects.

**Details:**
- **Units:** `sense_i_` is millivolts at the pin since «#3503». `i_limit_` is millivolts too, computed in Spin2
  at start: `limit amps × rSenseForBoard`, which is 5 mV/A on Rev A and 150 mV/A on Rev B (BOARD-REVISION-FACTS
  §2.2). An undetected board gets no limit from the scale; see §3.6.
- **Rev A resolution:** 10 A is 50 mV at the pin, a small fraction of the ADC range. The limit works, but
  coarsely. Rev A platforms do not drive on this rig (conventions, *Rig facts*), so it is NOMEAS.
- **Regeneration:** BOARD-REVISION-FACTS §2.8 leaves open whether reverse current is visible. It is very likely
  invisible on Rev A, and unknown on Rev B. **The design does not depend on it:**
  - §3.3 removes the unloaded stop's positive current.
  - §3.2 rule 3 bounds braking by lag, not by current.
  - Pure regeneration is therefore not limited by this mechanism, and the design says so rather than claiming it.
- **The rest zero (PL-45)** is 7–8 mV on Rev B, about 0.05 A. That is negligible against a limit, so the PASM
  compares the raw reading.

### 3.5 Blocked-platform detector and protective stop

**Where:** the front cog («#3513»), once per 1 ms pass, per motor. In the steering form it covers either wheel.

**Criterion, per motor:**
- a nonzero command (`targetIncre` without the sync bit),
- and `drv_state` is SPIN_UP, AT_SPEED or SPIN_DN,
- and `|err| >= LAG_SOFT`: the field is being held for the rotor,
- and the hall position has not changed,
- all continuously for `BLOCKED_MS`.

**`BLOCKED_MS` = 1,000.** MEASURED: an unloaded start at `ramp_inc` 22 sits about 200 ms without motion
(VISIT-2-RESULTS.md §6). 1 s is 5×, which leaves room for a loaded start. A legitimate drive whose rotor turns
resets the timer on every tick.

**Action.** This is the error-contract design §3.7 as amended 2026-09-16; nothing aborts anywhere:
1. The detecting front cog secures **both** motors first (`frontSecure(TRUE)` per wheel in steering), and
   zeroes `getPower()` (PL-52).
2. It latches `ERR_PLATFORM_BLOCKED` (−2_001) in the object's protective latch. The range −2_000..−2_099 is
   reserved for protective causes; any other value latches `ERR_PROTECTIVE_STOP` (−2_000).
3. While latched, every drive request is refused on the front cog with the protective code, like the e-stop
   refusal.
4. `getError()` returns the protective code first, without clearing it.
5. `getProtectiveStop()` reads the cause without clearing. `clearProtectiveStop()` goes through the front cog
   as a request: zero command, release the latch, and the motors stay stopped until commanded.
6. Both objects get all three calls; steering mirrors the constants (CLAUDE.md).

**Invariant:** a blocked platform cannot sit at the current limit indefinitely, and nothing but an explicit
acknowledgement releases it.

### 3.6 Undetected board

With `rSenseForBoard` unset there is no scale, so neither limit can be converted to millivolts. `i_limit_k` is
then set so the test can never be met, which means no fold-back and no derate (PL-73). The start is **not** refused: a board that fails
detection still drives today, and refusing it would be a contract change this task does not own. It is filed
as a finding.

## 4 · The ABI and the cog

- **Params block:** two new longs, placed after `ramp_inc` (hub VAR) and after `ramp_inc_` (PASM DAT):
  - `i_limit_k`: the peak limit's precomputed factor, rewritten by the front cog's derate.
  - `duty_floor`: m = 0.1, which is `0.4 × frame_cnt`.

  `DRVR_PARAMS_LONGS_COUNT` goes from 14 to 16, in lockstep (CLAUDE.md). `frame_cnt` follows them and is not in
  the copied run. The extended ABI guard from «#3554» must pass.
- **Limits as constants:** `I_PEAK_A = 40` and `I_CONT_A = 27` live in the motor object's CON block, with this
  document cited. They come from the board's MOSFET, not from the user's setup, so they are not in the user
  config.
- **Status block:** unchanged. `err`, `duty`, `sense_i_mV` and `pos` already give the detector and the bench
  everything they need.
- **New cog registers:** `lag_s`, `duty_cap_`, `duty0`, `incr0`. Four longs.
- **New instructions:** about 4 for §3.1, 8 for §3.2, 12 for §3.3 and 8 for §3.4, roughly 32 in all. The
  loop's `fit` directive fails the compile if cog RAM is exceeded, so «#3558»'s gate enforces the budget. If
  the budget does not hold, the §3.3 arithmetic moves to the LUT-resident block, as «#3535» did for
  `gettgtincr`.
- **Test hook:** `testSetCurrentLimits(peakAmps, contAmps)`, TEST USE, goes through the front cog. It lets
  Visit 4 set limits an unloaded wheel cannot turn under. That provokes fold-back, derate, droop and the blocked
  detector on a wheels-lifted rig.

## 5 · Visit 4 cells (for «#3560»)

Every cell is wheels-lifted, and each states the unfixed value it fails on.

| Cell | Stimulus | PASS when | Unfixed value |
|---|---|---|---|
| STOPCUR | FAULTB stop from 110.25M, all four combinations | the stop completes, and the peak current during SPIN_DN is ≤ the running current before it | 4 of 4 trip the 10 A abort; +20–50 % rise |
| STOPDECEL | half-speed `stopMotor()`, both motors | ticks to rest 74–77 (254 ticks/s² unchanged) | same (a no-regression cell; the negative limb is covered by STOPCUR) |
| RAMPDROOP | FAULTB trials `ramp_inc` 500 / 2,000 / 10,000 | no DCS_FAULTED; the wheel reaches speed | DCS_FAULTED in 96–186 ms |
| NOFOLD | the shipped limits; unloaded ladder rungs and a ramp-22 start | no fold-back or derate engages; speeds match Visit 2's ladder | a no-regression cell; the negative limb is FOLDBACK |
| FOLDBACK | `testSetCurrentLimits` peak low, drive 50 % | the logged lower-bound phase estimate (from `i` and `d`) holds at the limit; no fault | the estimate is unbounded (no limit exists) |
| DERATE | peak high, continuous low, drive 50 % for 3 s | the limit drops to the continuous value about 1 s in, and restores after the drive stops | no derate exists |
| BLOCKED | the peak limit set below what turns the wheel | protective stop latches within `BLOCKED_MS` + 1 pass; a drive returns `ERR_PLATFORM_BLOCKED`; `clearProtectiveStop()` releases; the motors stay stopped | no detector: the drive sits at the limit indefinitely |
| LAGBOUND | every trace above | `|e|` never exceeds 110 outside a fault | `e` saturates at 127 |

**Braking lead** (§3.2 rule 3) needs a loaded platform, so it is NOMEAS by the wheels-lifted ruling.

## 6 · Resolved with Stephen

- **The limit is the MOSFET's, not a round default.** STEPHEN 2026-09-16: *"we know which mosfets are on REv A/B
  boards. what would they need as protection"*. He then supplied both manuals' MOSFET sections and the
  MCAC85N06Y datasheet, and each board's gate supply: 10 V on Rev A, 12 V on Rev B. §3.4 derives both limits
  from them.
- **Regeneration visibility** is not asked: the design does not depend on it (§3.4).
- **Not known, taken conservatively rather than asked:** the board's copper area under each MOSFET.
  R<sub>θJA</sub> is taken as the datasheet's 1 in² figure. More copper would raise the continuous limit; less
  would lower it, and this is the one assumption that could be optimistic.
