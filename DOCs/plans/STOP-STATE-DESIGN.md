# Stop-state design — every stop path delivers the user's `holdAtStop()` selection

**Task:** «#3568», plan §R17.1 (`BENCH-READINESS-SPRINT-PLAN.md`, *Sprint Revision — 2026-09-17 (night)*).
**Phase:** 2 of 2 — **implemented 2026-09-17** as designed, with the §3 mapping as recommended (Stephen raised no
objection; the two judgement rows are one-line changes in `.faultBridge` and the e-stop entry if he wants either
flipped). Added during implementation: the bridge comes up COASTING at driver start (§3's invariant also covers
the frame before the control loop's first write). Run-time proof is owed to the bench (§5).
**Findings it closes:** PL-89, PL-56, S-9a (`DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md` §I.9).

**STEPHEN 2026-09-17:** *"isn't there a set*() which specifies motor stop condition? so user would select it
for their application"*. The user's selection is the contract; this design makes the driver keep it.

---

## 1 · The promises

| Member | What its documentation promises (`src/isp_bldc_motor.spin2`) |
|---|---|
| `holdAtStop(bEnable)` (`:704-714`) | *"actively hold position (bEnable=true) or coast (bEnable=false) once AT REST"*; sets `stop_mode := SM_BRAKE` or `SM_FLOAT` |
| `stopMotor()` (`:911-925`) | *"the stop itself always follows the driver's ramp; holdAtStop() only selects hold vs. coast once AT REST"* |
| `emergencyCutoff()` (`:927-941`) | *"Immediately stop motor, killing any motion that was still in progress"*; latches until `clearEmergency()` |
| a fault | **no documented promise** about the bridge at all |
| `stop()` | releases the pins (`pinclear`) and ends the driver cog: a true float, and not in scope |

---

## 2 · What the driver does today — established, not inferred

Four facts, each from an authority:

1. **The drive-off write.** When `driveoff` is 1 the control loop runs `wypin #0, drive_pins` on all six PWM pins
   (`src/isp_bldc_motor.spin2`, the `.ctlMotor` loop, `testb driveoff, #0 wc` / `if_c wypin #0, drive_pins`).
2. **What `Y = 0` produces.** p2kb `p2kbArchSmartPin01000PwmTriangle`: *"Output high when counter ≤ duty
   value"*; the counter runs from the frame period down to **1**; *"Y=0 produces constant low output"*;
   *"Y=frame period value produces constant high"*.
3. **The low side is inverted.** The low-side pins carry `pwmn` = `P_INVERT_OUTPUT | P_BITDAC | P_PWM_TRIANGLE |
   P_OE`; the high side carries `pwmt`, not inverted. So `Y = 0` leaves each **high-side pin LOW** and each
   **low-side pin HIGH**.
4. **A HIGH on a low-side input turns that FET ON.** Settled from normal drive in PL-56: each low side is written
   the high side's duty plus `dead_gap` on an inverted output, which is complementary drive with dead time only
   under that polarity; the other polarity would short every phase every PWM period, which hours of running have
   never shown. The board's added logic buffer acts on the **high** side only (*"the high side MOSFET can only be
   turned on when the low side MOSFET is turned off"*, `BOARD-REVISION-FACTS.md` §1.4).

**Therefore `driveoff = 1` holds all three low-side FETs ON: the phases are shorted together, a dynamic brake.**

Where that state is used today:

| Path | Code | Bridge today |
|---|---|---|
| At rest, `holdAtStop(FALSE)` (`SM_FLOAT`) | `checkstop`: FLOAT → `driveoff := 1` | **short** — documented as coast |
| At rest, `holdAtStop(TRUE)` (`SM_BRAKE`) | `checkstop`: BRAKE → `driveoff := 0`, `duty_ := duty_min`, angle from the halls | powered position hold — as documented |
| Fault | `.driveoff` on the fault test, whatever `stop_mode` is | **short** |
| E-stop | `.driveoff`, commented *"regardless of stop mode"* | **short** — matches *"immediately stop"* |

**Corroborating measurements:** `emergencyCutoff()` stops a half-speed wheel within one tick where `stop()` coasts
38-48 ticks (Visit 2, PL-56); the char tier's quiescent hold under the default `SM_FLOAT` shows the duty servo
wound to `duty_max` with near-zero current, so FLOAT at rest is the `driveoff` path
(`bench/2026-09-17/debug_260917-125254.log:91-93`).

### ⛔ The one conflict, and it is a hardware fact — so it goes to Stephen as a confirm question (overlay P8)

The chain above says **FLOAT at rest brakes**. The record says **"Stephen's prior bench testing shows freewheel/float
works"** (the 2026-09-09 safety study) and *"we came into this work with float working as desired"* (STEPHEN
2026-09-15). **The design does not depend on which is right** — it builds coast explicitly (§3) — but the release
note does: either coast was broken and is now fixed, or nothing changes for users. See §7.

---

## 3 · The design — three bridge states, each built explicitly

**Invariant:** *the bridge is always in exactly one named state, and each state is produced by writing each pin a
value whose meaning does not depend on that pin's inversion.* One value, one meaning (D7): `driveoff` today means
"PWM off" in its comment and "low sides on" in its effect.

| State | High-side pins | Low-side pins (inverted) | FETs | Meaning |
|---|---|---|---|---|
| **DRIVE** | commanded duty | commanded duty + `dead_gap` | switching | the motor is driven (and, at rest in `SM_BRAKE`, held at `duty_min`) |
| **COAST** | `Y = 0` → constant LOW | `Y = frame` → raw constant HIGH → pin LOW | **all six OFF** | freewheel |
| **SHORT** | `Y = 0` → constant LOW | `Y = 0` → raw LOW → pin HIGH | **three low sides ON** | dynamic brake (today's `driveoff = 1`) |

- `driveoff` is replaced by a `bridge_` register holding one of `BR_DRIVE`, `BR_COAST`, `BR_SHORT`, named in the
  `DAT` block beside the pin constants.
- The frame value for COAST comes from the frame period already configured into `fram` at start; it is computed
  once at start into its own register, not re-derived per pass.

### Which state each path takes

| Path | `SM_FLOAT` (coast selected) | `SM_BRAKE` (hold selected) | Why |
|---|---|---|---|
| Stop, once at rest | **COAST** *(today: SHORT)* | DRIVE, held at `duty_min` *(unchanged)* | the documented promise |
| Fault | **COAST** *(today: SHORT)* | **SHORT** *(today: SHORT)* | a faulted driver cannot hold position — it has lost the rotor — so "hold" is delivered by the passive brake, and "coast" is delivered as coast |
| E-stop (latched until cleared) | **SHORT** | **SHORT** | *"Immediately stop motor"*: the shortest stop the hardware has (1 tick measured), and no powered motor function while an emergency is latched |
| `stop()` | pins released | pins released | unchanged, out of scope |

⚠ **Two rows are judgement calls that stay reviewable** (overlay P3: a choice between two clean readings is his):
- **E-stop ignores the selection.** The alternative is "e-stop delivers the selection too", so a coast user's e-stop
  coasts. I recommend SHORT because *immediately* is the one word the e-stop's doc promises, and a coasting
  platform after an emergency is the case the e-stop exists to prevent.
- **A fault under `SM_BRAKE` shorts rather than holds.** A powered hold needs the rotor angle, which is what a fault
  says the driver no longer has.

### The duty servo while the bridge is not DRIVE

Today the servo keeps running with the bridge off and winds `duty_` to `duty_max` (char hold 0), so telemetry
reports a duty that is not applied. **Change:** while `bridge_` is not DRIVE, `duty_` is held at `duty_min` and the
servo is skipped, which is what `.checkstopfloaton` already assumes when it resets `duty_` on leaving float.

### Comments corrected in the same change (STEPHEN: *"always fix code/comment sync issues"*)

- `' make sure pwm is off and all drive pins low'` — describes the register value, not the pins; replaced by the
  state it produces.
- `driveoff`'s declaration comment *"pwm enabled (0) or disabled (1)"*, and every `.driveoff` / `checkstop*` comment.
- `fault`'s status-block comment *"(pins are floated when this happens)"* — they are not; it becomes the actual state.
- `stopMotor()` and `holdAtStop()` doc-comments gain the fault and e-stop rows in one sentence each.

---

## 4 · What does not change

- **The Spin2↔PASM2 ABI.** `stop_mode` and `e_stop` are already in the 16-long params run; the bridge state is an
  internal PASM register. Both VAR runs stay byte-identical (verified by content diff).
- **Stopping from speed.** Every stop still follows the ramp (PL-58); the state applies once at rest, on a fault, or
  on an e-stop.
- **The e-stop's measured behaviour** (SHORT, 1 tick) and the powered hold under `SM_BRAKE`.
- **Cog RAM:** the change is a handful of instructions and two registers against the `fit 496` budget; the
  headroom is read from the compiler's listing at implementation, not assumed.

---

## 5 · Certification (phase 2, and the visit)

- **Stephen's hand test** (attended, a `t0-hand`-shaped cell announcing each state and waiting on a key; the hall
  counter logs how far the wheel turned in each). Predictions, so it can fail:
  1. `holdAtStop(TRUE)` + `stopMotor()` → held at a fixed angle: steady, cogging resistance.
  2. `holdAtStop(FALSE)` + `stopMotor()` → **spins freely and coasts** (the fix; today the chain above predicts it
     resists harder the faster it is turned).
  3. `emergencyCutoff()` → resists harder the faster it is turned (SHORT).
  4. A provoked fault under `SM_FLOAT` → spins freely; under `SM_BRAKE` → resists with speed (needs R17.5's
     provocation).
- **An unattended stop-mode trace** in the dual harness: after a FLOAT stop at rest, the bridge-state telemetry
  (or, if none is published, the sense current and hall counter under a gentle nudge) confirms COAST; the e-stop's
  1-tick stop is re-confirmed.

### Built 2026-09-19 («#3578») as `t0-stopmode` — `src/test_bench_t0.spin2` T0-24, `-D T0_STOPMODE`

Six rows on the right wheel, each building one bridge state and then measuring what it does to a hand:
the powered hold, COAST at rest, the e-stop, a provoked fault under each stop mode, and `stop()` last as
the free yardstick. The panel (`tools/gen_t0stop_assets.py`) names the action **before** each row runs, and
**no cell reads a key**: Stephen's key press sequences the row and marks the moment he lets go, nothing more.

**What each cell judges is the time the wheel takes to fall to HALF the rate it had at the release**, counted
by the harness's own hall poll. How *far* it carries on scales with however hard he pushed; a shorted winding
brakes with a torque proportional to speed, so the halving time is a property of the bridge state and not of
his arm. Limits `SF_FREE_HALF_MS` 150 / `SF_BRAKE_HALF_MS` 60 are DERIVED from PL-56's Visit 2 reading (§2's
one tick against 38–48), with a 90 ms dead band between them. The distance is printed beside it.

Cells: `R17-T0-HOLDPWR` (turning the hold records a fault — which only a driven bridge can do),
`R17-T0-RESTCOAST`, `R17-T0-RESTSHORT`, `R17-T0-STOPGAP`, `R17-T0-FLTCOAST`, `R17-T0-FLTSHORT`,
`R17-T0-FLTGAP`, `R17-T0-FREEREF`. The fault rows use R17.5's computed provocation at the same power the
dual harness provokes at, so their readings and `R17-DUAL-FLTSTOP-C`'s compare.

---

## 6 · Release note (for «#3515»)

*"`holdAtStop(FALSE)` now truly lets the motor coast at rest, and a fault now follows your `holdAtStop()` choice
(coast, or brake if you chose hold). An emergency stop always brakes."* — the first clause is worded against §7's
answer.

---

## 7 · The conflict is settled by the test, not by a question

> **SETTLED 2026-09-19 BY CONSTRUCTION, not by a second binary («#3578»).** `BR_SHORT` is written as
> `wypin #0, drive_pins` on all six pins — the identical instruction the old `driveoff = 1` path ran for
> FLOAT at rest. So the **e-stop row of the hand test measures, on the fixed binary, the very state the old
> build put a floated wheel into**, and the release note is worded from that row. The paragraph below, which
> asked for a run of the unfixed binary or a reading from the Visit 5 quiescent hold, is superseded: neither
> is needed, and no bench time is spent on one.

The source chain in §2 says today's FLOAT at rest shorts the windings; the pre-sprint record says float works.
**The hand test in §5 decides it** — STEPHEN 2026-09-17: *"what can i confirm without being at hardware... that's
what our test is for..."*. The design does not depend on the answer (COAST is built explicitly); the release note
in §6 is worded after the test: *coast was broken and is fixed* if the unfixed build resists, *no change for users*
if it spins free. To make that possible, the hand test runs its FLOAT row on the current binary as well as the
fixed one, or the old behaviour is read from the Visit 5 char quiescent hold plus a nudge.
