
# Punch-list archive — 2026-10-01

Items swept out of [`DOCs/PUNCH-LIST.md`](../../PUNCH-LIST.md) at the 6.0.0 sprint closeout
(2026-10-01; see [`2026-10-01-BENCH-READINESS-CLOSEOUT.md`](2026-10-01-BENCH-READINESS-CLOSEOUT.md)
and [`2026-10-01-WINDOW-FREE-BENCH-CLOSEOUT.md`](2026-10-01-WINDOW-FREE-BENCH-CLOSEOUT.md)).
Each entry is copied verbatim, and under it an **Archived** line says what closed it.
Confirmed-done entries swept: PL-7, PL-14, PL-16, PL-51, PL-52, PL-54, PL-93, PL-95, PL-106, PL-144, PL-145, PL-146, PL-149, PL-150, PL-161, PL-162.

**This file is never re-edited.** If an archived item must be reopened, it returns to the active
punch list as a *new* item that references this archive.

**"What is outstanding?" is answered from the active punch list only** — never re-derived from
this file.

---

### PL-7 — Six blocks of prose are maintained in two or more documents

> ✅ **DONE 2026-09-27** (Stephen: *"we fix them!"*): the last three blocks resolved — the tagline now lives only in
> README.md (the four other headers already name the project); the FlySky pin paragraph and the RPi video line each
> have one copy, with a link from AUTHORS-Platform.md. `tools/doc-audit.sh` reports no duplicates (its demo count no
> longer counts the `demo_drive_names` helper object as a demo).

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (duplicated documentation prose)

Found by `tools/doc-audit.sh` on its first run. Each pair will diverge; the only question
is when. The fix is **one canonical copy and links from the others**, never "edit both and
keep them aligned" — that arrangement is what produces the drift.

| Duplicated block | Copies |
| --- | --- |
| Project tagline ("Single and Two-motor driver objects…") | `README.md:3`, `CONTRIBUTING.md:3`, `DRAWINGS.md:3`, `DRIVE-OBJECTS.md:4`, `Movement-STUDY.md:3` |
| "There are two objects in our motor control system…" | `DRIVE-OBJECTS.md:10`, `DRIVE-OBJECTS-SERIAL.md:10` |
| "This steering object makes it easy to…" | `DRIVE-OBJECTS.md:17`, `DRIVE-OBJECTS-SERIAL.md:18` |
| "The object isp_steering_2wheel.spin2 provides…" | `DRIVE-OBJECTS.md:42`, `DRIVE-OBJECTS-SERIAL.md:46` |
| FlySky wiring paragraph | `README.md:231`, `AUTHORS-Platform.md:63` |
| "Video of author running the system…" | `SERIAL-CONTROL.md:55`, `AUTHORS-Platform.md:10` |


### PL-14 -- `eMotorVoltage` is a documented public parameter that does nothing

> ✅ **DONE — CERTIFIED 2026-09-27, RC pass** (`debug_260927-140745.log`): R20-T0-API-PERSIST PASS; a start at
> PWR_14p8V read back `5` / `14_800` mV, the restart `6` / `18_500`.

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: no cell; certify by code reading or a t0 cell.
> **2026-09-27:** cell built — t0 SRC_REV 24 (f9c1d81), R20-T0-API-PERSIST starts at a second supported voltage
> (14.8 V on the bench) and reads it back through `getDriveVoltage()`, then restarts at DRIVE_VOLTAGE. The pre-fix
> library would read 18.5 V. Certifies at pass 8 (`t0-api`).

**Found 2026-09-10 while building the Tier 0 harness («#3474»). Not in the
24 findings of `DRIVER-AUDIT-2026-09-09.md` -- this is a new one.**

`start()`, `startEx()` and `testSetup()` all take `eMotorVoltage` and all
document it:

```
'' @param eMotorVoltage - The voltage ENUM (PWR_*) for this motor
```

It is never read. The parameter appears **only** in method signatures and in
those doc comments; no method body references it. `init()` passes the
compile-time constant instead:

```
isp_bldc_motor.spin2:259:    confgurePowerLimits(user.DRIVE_VOLTAGE)
```

So `start(pins, PWR_18p5V, mode)` and `start(pins, PWR_25p9V, mode)` behave
identically, and the drive voltage is whatever `isp_bldc_motor_userconfig.spin2`
was compiled with. A user following the published interface can select a
voltage, observe no change, and have no way to tell why -- the API accepts the
argument and the documentation promises it means something.

**Likely history:** voltage selection moved to the user-config file (the
documented mechanism -- users edit section 2) and the parameter was left in
place rather than removed.

**Two possible fixes, and it is an API decision, not a defect fix:** honour the
parameter (a behaviour change for every existing caller, and it would then
disagree with the compile-time power tables), or delete it from all three
signatures and the docs (a breaking signature change for every caller). Either
way `DRIVE-OBJECTS.md` and the generated `isp_bldc_motor.txt` move with it.

**Consequence for the bench suite, already absorbed:** T0-4 (finding O,
voltage legality) cannot sweep voltages through `testSetup()` in a single
build -- only the active config's voltage is ever exercised. Confirming O for
a second voltage needs a rebuild with `DRIVE_VOLTAGE` changed. The harness
documents this inline.

Write this back into `DRIVER-AUDIT-2026-09-09.md` as a new finding when
«#3481» runs.

**FIXED IN SOURCE (aged-state sweep 2026-09-17, found reading `init()` for «#3568»):** `init()` now honours the
caller's `eMotorVoltage` rather than re-reading `user.DRIVE_VOLTAGE` (`src/isp_bldc_motor.spin2`, the block
commented *"PL-14: honour the caller's eMotorVoltage parameter"*, just before `confgurePowerLimits()`), which makes
the parameter and `validVoltageForChoice()` meaningful and lets two motors run at different voltages. This entry
had gone on saying "an API decision"; the decision was taken the parameter-honouring way. No isolating cell exists:
every shipped caller passes the configured voltage, so the change is behaviour-neutral for them.

### PL-16 -- `util_char_motor.spin2` drive helpers: comment says 10 s, constant is 5 s

> ✅ **DONE 2026-09-27:** both comments now name `DRIVE_AT_SPEED_SECS` instead of a number.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (characterisation utility comment)

**Found 2026-09-11 while building `src/test_bench_char.spin2` («#3497»).**

`src/util_char_motor.spin2:455` and `:476` (lines updated 2026-09-26; first filed as `:379` and `:392`):

```
wheel.stopAfterTime(DRIVE_AT_SPEED_SECS, wheel.DTU_SEC)      ' set to hold at speed for 10 Sec
```

`DRIVE_AT_SPEED_SECS = 5` at `:57`. The comment says ten seconds on both lines; the
constant has been five. A reader trusting the comment mis-times every
characterisation run made with this tool, and the error is invisible because a
five-second drive still looks like a drive.

**This nearly propagated.** «#3497»'s task body said to reuse
`driveForwardAtSpeed()` / `driveReverseAtSpeed()` for operator-held meter reads.
An operator hold is indefinite; either helper would have stopped the motor five
seconds in, collapsing the meter reading toward zero **while the panel kept
displaying a correct-looking hold**, and the operator would have written down a
number taken from a stopped motor. `test_bench_char.spin2` therefore commands
motion with `testDriveAtMotorIncrement()` and no stop timer at all.

**Fix:** correct both comments to match the constant, or name the constant in the
comment rather than restating its value -- a comment that repeats a number is a
second place for that number to be wrong.


### PL-51 -- the steering object's `getMaxSpeedForDistance()` returns the max speed, not the max speed for distance

> ✅ **DONE — CERTIFIED 2026-09-27, RC pass** (`debug_260927-140745.log`): R20-T0-API-STEER PASS, 0 bad of 51 calls,
> the distance-speed set/read-back rows included.

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: no cell.
> **2026-09-27:** cell built — t0 SRC_REV 24 (f9c1d81), R20-T0-API-STEER sets the steering distance speed across its
> range and reads each back. The pre-fix getter returned `getMaxSpeed()` (75). Certifies at pass 8 (`t0-api`).

**Found 2026-09-14** by «#3508» phase 2(b1), and confirmed by the arbiter reading source. DERIVED, not
observed on hardware.

- `src/isp_steering_2wheel.spin2:558-564`: the method's doc says *"Returns the last specified
  {maxSpeedForDistance}"*, but its body returns `rtWheel.getMaxSpeed()`. The commented-out line above it
  makes the same call on the left wheel.
- It sits directly below `getMaxSpeed()` (`:550-556`), whose body is identical, so this reads as a
  copy-paste defect.
- **Who is affected:** any caller that reads back the speed limit it set for distance moves. That
  includes a host driving the serial protocol, if it exposes this getter.
- **Not affected:** `driveForDistance()` itself, which reads the wheels directly (`:252`).

- **The correct getter exists:** `PUB getMaxSpeedForDistance() : nSpeed4dist` at
  `src/isp_bldc_motor.spin2:773-777`, returning `maxSpeed4dist`. The steering object's own
  `driveForDistance()` calls it on both wheels (`:252-253`).
- **The documentation describes the intended behaviour, which the code does not deliver:**
  `DRIVE-OBJECTS.md:71` (steering) and `:117` (motor).
- **Bench consequence:** «#3508»'s harness does not read this getter. It sets the distance speed
  itself and prints the value it set (`plans/MOTION-HARNESS-DESIGN.md` §12.8).

**Fix direction:** `nSpeed4dist := rtWheel.getMaxSpeedForDistance()`, a one-line change. Also check
whether the serial object exposes this getter.

**Fixed in tree 2026-09-16 («#3556»).** `getMaxSpeedForDistance()` (`src/isp_steering_2wheel.spin2` ~:1383-1390; line updated 2026-09-26, first filed as `:769-775`)
now calls `rtWheel.getMaxSpeedForDistance()`, matching `driveForDistance()`'s own call. The serial
object was not checked for the same getter -- out of this task's scope.

### PL-52 -- `getPower()` keeps reporting the last power after the motor is stopped, against its own doc

> ✅ **DONE — CERTIFIED 2026-09-27, RC pass** (`debug_260927-140529.log`): R20-T0-SR-COMMANDED PASS with
> `T0-25,power,run,15,want,15,stopped,0`.

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: no cell.
> **2026-09-27:** cell built — t0 SRC_REV 24 (f9c1d81), T0-25's commanded-stop leg reads `getPower()` while driving
> (want 15) and after `stopMotor()` returns (want 0), in R20-T0-SR-COMMANDED (record `T0-25,power`). The pre-fix
> library read 15 after the stop. Certifies at pass 8 (`t0-stopreason`).

**Found 2026-09-14** by «#3508» phase 2(b3), and confirmed by the arbiter reading source. DERIVED, not
observed on hardware.

- **The doc:** `src/isp_bldc_motor.spin2:744-748` says `getPower()` returns the last specified power
  *"(will be zero if the motor is stopped)"*. `DRIVE-OBJECTS.md:68` says the same for the steering
  object.
- **The code returns `motorPower` unchanged.** The stop paths never write it:
  - `stopMotor()` (`:664-669`) and `emergencyCutoff()` (`:671-677`) only call
    `setTargetAccel(0, false)`;
  - `setTargetAccel()` (`:1434-1440`) writes `targetIncre`, not `motorPower`;
  - the sense task's distance and time stops use the same `setTargetAccel(0)` path.
- **Who is affected:** any caller that reads `getPower()` to decide whether the motor is still
  commanded. After a stop or a completed distance move, it still sees the old power.
- **Not yet checked:** every writer of `motorPower` was not searched. A writer elsewhere, such as
  `driveAtPower(0)`, could make some stop paths read zero.
- **Bench consequence:** «#3508»'s BM-OUT `l_pwr`/`r_pwr` and BM-FLOOR print `getPower()` as the last
  specified power, which is what it returns. No harness change is needed
  (`plans/MOTION-HARNESS-DESIGN.md` §12.9).

**Fix direction:** first find every writer of `motorPower`. Then either clear it on every stop path, or
correct the doc to "last specified power", whichever the API intends.

**Fixed in tree 2026-09-16 («#3556»).** *(Aged-state sweep 2026-09-17: no cell isolates `getPower()`
after a stop; Visit 5's t0 certifies the error contract it rides on, not this getter. It stays
certified by construction only.)* The rule: `getPower()`
reads 0 whenever the front cog has left the motor commanded to stop. The line numbers above predate
the front cog («#3513»).
- **Writers:** `motorPower` is written by `frontDrive()` (a commanded power) and by the stop paths:
  `frontZeroPower()`, `frontEStop(TRUE)`, `frontSecure()` and `stop()`.
- **Stops that zero it, in both objects:**
  - `REQ_STOP`
  - the distance/rotation/time limits
  - the e-stop
  - a synced command the driver did not take (`ERR_SYNC_TIMEOUT`)
- **While FAULTED** it keeps the last commanded power: nothing commanded a stop.
- **Exception:** `REQ_TEST_INCREMENT` writes a raw increment, not a power, and leaves it unchanged; its
  doc says so.


### PL-54 -- `src/test_dual_motor.spin2` names itself `demo_dual_motor.spin2`, and most of its body can never run

> ✅ **DONE 2026-09-27:** the bare holding `repeat` is removed, so the steps after the distance-and-turn loop run and the
> program ends with `wheels.stop()` and `* DONE`, as its body was written to (the header was fixed 2026-09-26).

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (test program, Stephen's call)

**Found 2026-09-14** by «#3508» (`plans/MOTION-HARNESS-DESIGN.md` §7.3), and confirmed by reading the
source in phase 2. DERIVED, not observed on hardware.

- **The wrong name:** `src/test_dual_motor.spin2:3` reads `File....... demo_dual_motor.spin2`, the name of
  the certified release demo, not this file's.
- **The unreachable code:** `:77` prints `* TEST complete, holding`, then `:78` is a bare `repeat` with no
  body and no exit. Nothing after it in the valid-configuration branch can run: the 1 ft distance drive,
  the two `driveDirection()` holds, the left and right wheel holds (`:80-106`) and `wheels.stop()`
  (`:109`). `debug("* DONE")` (`:113`) is reached only on the invalid-configuration path.
- **The class:** a program whose visible intent (its header, its later steps) differs from what
  executes, so a reader, or an agent trusting either, is misled. It is not a bench binary (no records,
  watchdog or sign-off), so no visit depends on it.
- **Fix direction:** correct the header's file name. Then either delete the unreachable steps or remove the
  holding `repeat` so they run, whichever this test is meant to do. That is Stephen's call: it is his test
  program.

**2026-09-26:** the header is fixed (`src/test_dual_motor.spin2:3` now reads `test_dual_motor.spin2`); only the
unreachable body remains (the bare `repeat` at `:86`, then `:87-117` including `wheels.stop()`).

### PL-93 -- after a real fault and a successful recovery, the next drive-up draws 3-4x current and aborts

> **6.0 status (2026-09-30, the rerun):** ✅ CERTIFIED on the floor — after the forced LEFT fault and its recovery the
> drive drew 0.95x (LEFT) and 0.72x (RIGHT) its current before (R21-DUAL-POSTFLT-P PASS, bound 1.5;
> `DOCs/analyses/bench/2026-09-30/floor2/FLOOR-RERUN-EVALUATION.md` §2.2).

**Found 2026-09-19 at Visit 6a.** A new defect class, and it was unreachable until this visit: the
fault provocation had never actually faulted before (PL-86), so nothing downstream of a real fault had
ever run.

**MEASURED (`debug_260919-173537.log`, `dual-c` POSTFLT, all twelve traces):** the first trace on each
wheel faults properly (`st,FAULTED, flt,TRUE, e,-101`) and coasts to rest -- LEFT tid 9 `rest_k 278`,
RIGHT tid 15 `rest_k 257`. **Every trace after it aborts**: tid 10-14 and 16-20, on
`reason,ABS_CURRENT`, `value,3_435` (LEFT) and `3_771` (RIGHT) mV against `ABS_ABORT_MV 1_500`
(10 A at 150 mV/A). Half-speed running current is about **900 mV** (Visit 3,
`debug_260916-123957.log` tid 11). The aborted traces carry **no samples at all** -- the abort fires
during the next trial's drive-up, before the instrument arms -- and that includes the e-stop traces,
which write no offsets. The offsets were correctly restored each time (`BM-OFFREST … ok,TRUE`), and the
harness's recovery reports success (`BM-RECOVER … step,RESET, cleared,TRUE, ms,31, st,STOPPED,
flt,FALSE`).

**MEASURED, why it is new:** at Visit 3 the same segment ran **all twenty traces to `end,REST` with
zero aborts**.

**Not settled by these logs:** whether this belongs to the driver's post-fault state or to the
harness's recovery sequence. **It is user-visible either way** -- fault, recover, drive again is an
ordinary thing for an application to do -- so it is chased before the release, and the discriminating
read is the driver's own state after `.resetFault` against what the harness commands next.

**Cost this visit:** it is the reason every cell downstream of the first fault is NOMEAS, including
`R17-DUAL-FLTSTOP-C`.

### ⛔ THE MECHANISM, read from the samples 2026-09-20 -- and it is a DRIVER defect, not a harness one

**MEASURED** (`debug_260919-173537.log`, tid 16, RIGHT wheel, eight consecutive samples k 64-71):

| | reading |
|---|---|
| `i` | **3_742 -> 3_772 mV**, i.e. about **25 A** at the harness's own 150 mV/A calibration |
| `d` | **23_891 -> 24_264**, and 24_264 **is `duty_max`** -- the servo wound to the ceiling and stayed |
| `e` | **pinned at -101**, just under the driver's `\|err\| >= 125` fault test, and right at `LAG_HOLD` (100) |
| `st` | **AT_SPEED** throughout |

**DERIVED, and every step is visible in the numbers above:** the lag limiter holds the field so `err`
sits at its hold threshold and **never reaches the fault test**; the duty servo, seeing an error it
cannot clear, **winds `duty_` to `duty_max`**; S-2's current fold-back computes its threshold as
`max(duty_, duty_floor_) * i_limit_k_ >> 16`, so **at `duty_max` that threshold is at its most
permissive** and no fold-back occurred (duty rose into the ceiling rather than backing off); the
protective stop did not fire either. The driver therefore sat at **maximum duty drawing ~25 A while
reporting AT_SPEED**, and the only thing that stopped it was the harness's external 10 A abort.

⛔ **A USER HAS NO SUCH ABORT.** This is the same shape as a stalled or blocked wheel -- "commanded rate
cannot be reached" -- so it is reachable outside a provoked fault. It is filed here because a fault
exposed it, but **the condition is general and it is the most consequential thing Visit 6a found.**

**Fix direction (driver, and it subsumes PL-86 and PL-46's instrument problem):** a **droop detector** --
compare commanded tick rate against measured tick rate, and when they diverge for N consecutive frames
act on it (fault, or the protective stop that already exists). One mechanism then serves three needs:
the driver gets the protection it is missing, the commutation scan gets the stop condition the limiter
took away (PL-46), and the fault provocation gets a reachable edge (PL-86). The current-limit threshold
scaling with duty should be re-read at the same time: it is most permissive exactly when duty is
highest, which is backwards for this failure.

**2026-09-26:** R18.4 was built and measured unloaded at Visits 8, 8b, 9 and 9b; what remains is the loaded floor run.


### PL-95 -- the drive does not integrate hall and current: above mid-range it runs saturated, field parked, and calls it AT_SPEED

> **6.0 status (2026-09-30):** ✅ CERTIFIED — the kick at the RC pass; on the floor, R21-DUAL-HELDATSPD-P 0 bad over
> every OBSTACLE drive and the GRAB window (443 + 547 + 254 samples; FLOOR-VISIT-EVALUATION.md §3-§4).

> ## THE INSTRUMENT HALF IS LANDED 2026-09-20 («#3580» R18.1); THE DRIVE IS UNCHANGED
>
> Everything this entry says about the drive still stands -- **no control-path statement has been
> touched**, deliberately, so Visit 7 characterises today's drive and not a half-changed one. What has
> changed is what the drive **publishes** and what the harness **asks of it**:
>
> - The driver counts the passes on which each limit ACTED -- `lag_held` (the limiter withheld the field
>   advance) and `duty_capped` (the duty demand exceeded the cap), read through `testGetDriveHealth()`.
>   A count has no ceiling, which is the whole point: `err` is held near `LAG_HOLD` and bounded by its
>   own +-127, and `duty` pins at `duty_max`, so both stop reporting exactly where this entry's
>   behaviour lives. `err` and `duty` stay beside them, unchanged, for continuity with Visits 5 and 6a.
> - The harness differences both across the **transition** and across the **steady window** of every
>   measured rung, as the new `BM-RUNGHL` record. **No cell judges them** -- the acceptance numbers are
>   R18.3's to choose before R18.4 builds against them (doctrine D2).
> - **The command space this entry says is unmeasured is now reachable.** The ladder walk gains a
>   descent and six delta cells -- a small and a large change of speed at low, at the knee and at the
>   ceiling, each taken up and down -- and `LIVE` emits a transition record at last. The "speed DOWN,
>   any" row of the table below stops being empty at Visit 7.
> - The kick's cell is re-judged on current rather than on the clamped error: see PL-87.
>
> **Still owed: the drive change itself (R18.4), and Visit 7 to characterise against.**

**Found 2026-09-20, re-reading Visit 6a's ladder as a RAMP rather than as a set of rungs.** STEPHEN
2026-09-20: *"you are too focused on the braking when the ramps and proper integration of hall and
current into motor drive is much more important"*. He is right, and the data he already had says so
louder than anything in the stop-state work.

**MEASURED, `debug_260919-173751.log`, LEFT reverse ladder, twelve rungs:**

| rung | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| commanded incre (x10^6) | 5 | 10 | 20 | 40 | 60 | 80 | **100** | 120 | 140 | 147 | 155 | 165 |
| `duty_pk` | 2_066 | 2_792 | 4_686 | 9_460 | 14_955 | 21_081 | **24_264** | 24_264 | 24_264 | 24_264 | 24_264 | 24_264 |
| steady current | 13 | 17 | 48 | 213 | 571 | 1_146 | **1_162** | 524 | 140 | 78 | 48 | 65 |
| `err_pk` | 98 | 76 | 73 | 75 | 75 | 75 | 78 | 85 | 95 | 97 | **102** | **105** |

**Three things happen at once at rung 7, and they are the whole finding:**

1. **`duty_pk` reaches `duty_max` (24_264) and STAYS THERE for the top half of the range.** From rung 7
   up the driver has no authority left -- it is commanding full duty and cannot command more.
2. **The steady current PEAKS and then FALLS** -- 1_162 at rung 7 down to 48 at rung 11 -- while the
   commanded speed keeps rising. Current falling as commanded speed rises, at saturated duty, is the
   signature of a drive that has stopped delivering torque.
3. **`err_pk` climbs from 75 toward 105**, i.e. toward `LAG_HOLD` (100). The field is running further
   and further ahead of the rotor, and the limiter parks it there.

⛔ **And the driver reports AT_SPEED throughout.** Rungs 8-12 are a motor that is not tracking its
command, at full duty, with the field parked at a large angular error -- reported as healthy.

⭐ **THIS IS THE SAME STATE AS PL-93**, which was reached through a provoked fault: `duty_max`, `err`
pinned near the limiter hold, `AT_SPEED`, current set by the load rather than by control. **PL-93 is not
an edge case -- it is the normal top half of this driver's speed range**, and a loaded wheel in that
state is what drew 25 A.

⭐ **And it explains the kick (PL-87).** The transition current peaks at **rung 7**, exactly where duty
saturates: every ramp step throws the field further ahead before the rotor can follow, and the step that
lands in saturation is the worst. Stephen feels one at each increment because each increment does it.

**What is actually missing, stated as the design gap rather than as symptoms:**

- **The halls are used coarsely and the field is advanced open-loop between them.** The rotor's position
  is known six times per electrical cycle; between those edges the driver advances `angle_` at the
  commanded rate and hopes. When the command exceeds what the rotor can do, nothing closes that loop --
  the limiter only clamps the reported error.
- **Current is not feedback.** It is read for the S-2 fold-back threshold and for telemetry, and
  nowhere does it inform commutation. Yet the table above shows current is the only observable that
  tracks what the drive is actually doing -- error is clamped, duty saturates, and current is neither.
- **The ramp commands a rate, not an achievable acceleration.** `ramp_inc` advances the commanded
  increment by a fixed step per drive pass regardless of whether the rotor is following, so every step
  is an open-loop lunge and the error absorbs the difference.

### ⭐ THE OBSERVABLES THEMSELVES MUST BE RESPECIFIED -- a measure that tops out is not a measure

**STEPHEN 2026-09-20:** *"if we have measures that are topping out we need to respecify them so they do
not - as they are not useful once topped out"*. That is the general statement of why every instrument
built on this driver has been blind, and it applies to the driver's own control as much as to the bench.

| Observable | How it tops out | What it should be instead -- unbounded where it matters |
|---|---|---|
| `err` (position error) | **Twice over.** The lag limiter holds it near `LAG_HOLD` (100), and the stored field is bounded by its own +-127 representation -- the tree already notes a driver with no limiter simply prints 127. | **The limiting actually applied** -- the field advance the limiter withheld this pass. When the drive is keeping up it is zero; when it cannot, it grows without bound. That is the same information `err` was supposed to carry, in a form that does not stop. |
| `duty` | Saturates at `duty_max` (24_264) and pins there for the whole top half of the range. | **Duty DEMAND before the cap**, or the **deficit** (demand less cap). Once duty pins, the deficit is what says how far past capability the command is; duty itself says only "still pinned". |
| `tr_over` (the kick cell) | Derived from `err`, so it inherits both ceilings -- which is why it read 0 of 22 while the transition current rose seventy-five fold. | Transition **current**, already recorded as `tr_i_pk`. Not clamped. |
| `AT_SPEED` | A boolean meaning "my own increment reached its target" -- true by construction even when the motor never got there. | **Measured rate against commanded rate**, a ratio that keeps informing on both sides of the limit. |

⭐ **This is not only a telemetry fix. The respecified quantities are exactly what the drive needs as
feedback**: "how much am I withholding" and "how much duty did I want beyond what I have" are the two
numbers that say the command is unachievable, and a drive that has them does not need a separate droop
detector bolted on -- it can hold at the achievable rate by construction. The instrument and the control
want the same respecification, which is a sign it is the right one.

**Cog space is a constraint to respect, not a gate** (STEPHEN 2026-09-20: *"you are fretting too much
about cog space, the lut addition just doubled it. we have room we just have to be mindful"*).

**Fix direction (this is the 6.0.0 driver work, and everything else is downstream of it):** close the
loop the halls and the current are already giving us -- correct the field against hall edges rather than
free-running between them, bound the ramp by measured acceleration rather than a fixed increment step,
and use current as the signal for commutation quality rather than only as a fold-back trigger. **A
droop detector, which this list previously proposed, is a guard around this defect and not a fix for
it** (doctrine D1: fix the system, not the display).

### What the user can actually command -- the space the drive has to be good across

**STEPHEN 2026-09-20:** *"if we also weigh-in what a user can command we are going to have to handle
small delta speed-up/slow-down requests as well as large, near max throttle... our drive mech. has to
handle this well"*. That is the acceptance space, and measuring against it exposes two gaps.

⛔ **CORRECTION to an earlier reading of mine: the kick does NOT scale with the size of the speed
change.** MEASURED, the SAME 20x10^6 step taken at six places in the range:

| step | 20->40 | 40->60 | 60->80 | **80->100** | 100->120 | 120->140 |
|---|---|---|---|---|---|---|
| transition current | 234 | 583 | 1_197 | **1_439** | 1_264 | 599 |

**Identical command, six-fold difference in what the motor does** -- peaking at the step that lands on
the saturation knee (rung 7). So the same user action, a modest throttle bump, behaves completely
differently depending on where in the range it is made. **Where the change happens dominates; how big it
is does not.** That is a property of the drive, not of the request, and it is exactly what "handle this
well" has to mean.

⛔ **AND EVERY TRANSITION WE HAVE EVER MEASURED IS A SPEED-UP.** MEASURED across the whole load: **44
speed-up steps recorded, ZERO speed-down steps.** The ladder only climbs, and the LIVE segment
(QTR -> HALF -> TOP) climbs too and emits no transition record at all. **A user slowing from 80% to 60%
is completely uncharacterised** -- and slowing is the direction where the field must fall BACK through
the rotor, which is the opposite sign of error and a different failure if it is wrong.

**The space, and what we hold for each cell:**

| | small delta | medium delta | large delta | near-max |
|---|---|---|---|---|
| **speed UP, low in range** | not measured | MEASURED (rungs 3-5) | not measured | n/a |
| **speed UP, at the knee** | not measured | **MEASURED, and it is the worst case** | not measured | n/a |
| **speed UP, high in range** | not measured | MEASURED (rungs 9-12, already saturated) | not measured | MEASURED, saturated |
| **speed DOWN, any** | **NOTHING** | **NOTHING** | **NOTHING** | **NOTHING** |

**So the acceptance test for the corrected drive is a ladder that also descends, that includes a small
delta and a large one at each of low / knee / high, and that records a transition for every step
including the LIVE-style ones.** The instrument change is small -- `BM-RUNGTR` already carries the right
fields and simply is not emitted for every segment -- and it must land with the drive fix, not after it,
or the fix is verified only on the quarter of the space we happen to have.

**Verification is already paid for on the part we do cover:** the ladder prints `duty_pk`, steady
current, `err_pk` and the transition current per rung, so the table above IS the acceptance test. A corrected drive flattens the
transition current, keeps duty off its ceiling until genuinely at the ceiling, and does not report
AT_SPEED while the field is parked.

### PL-106 -- the blocked-motor protective stop cannot be provoked on a lifted rig, so no driver change to it is certified

> **6.0 status (2026-09-30):** ✅ CERTIFIED on the floor — floor-obstacle-short latched SR_BLOCKED after the LEFT stood
> 1,143 ms (band 988-1,168), the RIGHT SR_PARTNER (R21-DUAL-BLKSTOP-P PASS; FLOOR-VISIT-EVALUATION.md §3); and again on the
> rerun's BRAKE trial (`r_stand,1_097`, SR_BLOCKED + SR_PARTNER). Against a rocking obstacle the latch can take seconds
> (the rerun's coast trial pushed about 6 s; the first visit's took a graceful lag fault at about 4 s, lag peaks within 5
> counts of the fault line): **accepted as it is for 6.0** (Stephen 2026-10-01, R18: *"i think the current obstacle
> behavior is find for this release"*). Listed in v6.0.0's Known Issues (Stephen 2026-10-01, *"yes A"*).

**Found 2026-09-22 at Visit 8** ([evaluation](analyses/bench/2026-09-22/VISIT-8-EVALUATION.md) §3.4, F-3).
`R16-DUAL-BLOCKED-D` has read NOMEAS (`why,NOT_BLOCKED`) in **every** part-D log on record: 2026-09-17 twice,
2026-09-19, and Visit 8. At the 1 A limit the step sets, a lifted wheel keeps turning, so the front cog never
sees a motor commanded to move and standing still. The cell cannot fail on this rig. The Visit 8 run sheet
wrongly claimed it would certify DRIVER_REV 3's fix: the overload hold's decay now stops at `ramp_min_`, so a
stall keeps the lag the protective stop needs. **That fix is correct by reading and unmeasured.**

**What it would take:** a stall built by construction. For example, a test-only driver command that holds the
field still (an increment of 0 with the bridge driven), or a limit low enough to stop a lifted wheel, found
by stepping it down until the hall ticks stop. Either must be shown able to reach `NOT_BLOCKED`'s negative
case before the cell is trusted. **The floor run («#3591»)** is the other place a real stall can happen.

⚠ **2026-09-22 23:40 -- the stop DID fire on a lifted rig, possibly for the wrong reason (PL-116).** T0-24's
two powered rows each latched `ERR_PLATFORM_BLOCKED` at power 50, straight after the e-stop row's
`clearEmergency()`. Until PL-116 separates "the drive did not resume" from "the test false-fired", this does not
certify the blocked test.

**A construction found, 2026-09-23 (Visit 9b, [evaluation](analyses/bench/2026-09-23/VISIT-9B-EVALUATION.md) §5, G-3).**
`dual-limits-top`'s over-command step lowers the limits to 1 A and commands 245 × 10⁶. On three wheel-directions
the wheel fell to **2–4 % of command** (`h_pct` 2–4, the field walked down to 6–19 × 10⁶), with no fault. The
fold-back limits estimated *phase* current, which rises as duty falls, so once it bites it keeps biting. That is
the nearest a lifted rig has come to "commanded and standing still". The BLOCKED step's 1 A limit at power 50 never
crosses, because a lifted wheel there draws about 0.14 A. The same limit under an over-command does cross. Whether it
reaches a true stall, and so the protective stop, is untried.

**2026-09-24:** the protective stop fired about 1 s in on the dead right bridge (VISIT-10-DUALFAULT-T0-EVALUATION.md §4), before DRIVER_REV 20 made it honour the stop mode (PL-132); a blocked wheel has still never been measured.


### PL-144 -- the path limiter hunts: a wheel that cannot sustain its command cycles the platform between 8 % and 100 %

> **6.0 status (2026-09-30, the rerun):** ✅ CERTIFIED — R21-DUAL-LDHUNT-P PASS, 0 limiter transitions inside the hold's
> window with the limiter engaged (`flips,0,engages_pre,2,engaged,TRUE`; FLOOR-RERUN-EVALUATION.md §3). The first visit's
> record follows.
>
> **First visit (2026-09-30):** floor R21-DUAL-LDHUNT-P **FAIL, 3 engages of 1**: two in the free start-up
> (LEFT 713 ‰ released after 0.57 s, RIGHT 771 ‰ after 0.71 s), then one held through the hold to the stop; no cycling under
> the hold. The cell counted the whole lifetime, a scope written for wheels-up starts that never engage (harness H3:
> it now counts the limiter's transitions inside the judged window, PASS 0 with the limiter engaged -- the pre-fix
> cycling gives >= 3 in 2.5 s; the start-up engages still printed). Rerun floor-grab.

**Found 2026-09-26** at Visit 10 pass 6 ([evaluation](analyses/bench/2026-09-26/VISIT-10-PASS6-EVALUATION.md) §5).
- **MEASURED** (`dual-d`, BLOCK step at a 1 A limit, the left weaker than the right): five cycles in 4 s.
  - `PATH_LIMIT,wheel,LEFT` engages at 82, 95, 81, 80 and 85 ‰ (ms 64_946, 65_730, 66_450, 67_162, 67_954);
  - each is followed by a full release to 1_000 about 430 ms later;
  - the next engage comes about 300-350 ms after that, a period of 720-790 ms.
- **The design says otherwise:** DRIVE-INTEGRATION-DESIGN.md §3 requires the limiter to release *"without hunting
  between the two"*.
- **Cause, read in `frontLimitPath()`.** A slot counted as clean when no field was held. But the fields ramp toward
  each released scale at their acceleration, so the scale reached full about 0.4 s before the weak wheel's field did.
  At full the wheel fell behind again, and the limiter re-engaged from full.
- On a floor, that is a platform surging between a crawl and full command every ~0.75 s whenever one wheel is
  overloaded.

**Disposition: ⛔ FIX, built** (DRIVER_REV 30, `isp_steering_2wheel.spin2`). A slot counts as clean only when both
fields have reached the present scale, within one release step. So the release never outruns the fields, and a wheel
that cannot sustain its command falls back from near its limit, not from full. No PASM change.
- **Cell:** R20-DUAL-PATH-HUNT (`test_bench_dual` SRC_REV 52): the BLOCK step's most EV_PATH_LIMIT pairs in one log.
  PASS at exactly 1. Its negative is pass 6's log: 5 on the pre-fix driver.
- **Not established:** how the fixed limiter settles on a floor. A wheel behind by less than one release step can still
  drift slowly, deepening without an event; the floor run shows it.
- **By design, stated:** a field that stops short of the scale without being held (its ramp waiting at LAG_SOFT) now
  keeps the scale where it is until the fields catch up or a new command arrives. The path is kept, just slower.

**2026-09-27, Visit 10 pass 7:** the log shows ONE engage in the BLOCK step (`PATH_LIMIT,wheel,LEFT,...,value,91`)
and its release, where pass 6 showed five cycles. But R20-DUAL-PATH-HUNT read NOMEAS on its precondition, so the cell
has not judged it; the log is evidence only. The precondition is being fixed (harness SRC_REV 56). Certifies at pass 8.

### PL-145 -- R16-DUAL-TIMESTOP's 20 ms slack sits inside the step's own measured spread

> ✅ **DONE — CERTIFIED 2026-09-27, RC pass** (`debug_260927-141141.log`): TIMESTOP-D and WTIMSTOP-D PASS;
> `BM-TIMESTOP,...,fire_ms,-1_108,zero_ms,-1` (steering) and `zero_ms,-2` (single), bound −6..+6 ms.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench cell slack, watch)

**Found 2026-09-26** at Visit 10 pass 6 (evaluation §5).
- **MEASURED:** the single-wheel form failed, `BM-DSTEP,...,TIMESTOP,motor,LEFT,seg,LIMIT,measured,329,...,hi,320`,
  which is rest confirmed 29 ms after the deadline.
- Every TIMESTOP on file reads 254-329 ms (7 runs, both forms). That is -46 to +29 ms against the deadline, once the
  300 ms rest-confirmation dwell is taken off. One earlier run also failed, at 321 (STEERSEG).
- **DERIVED:** the stop is timed so the FIELD reaches zero at the deadline (`bFrontLimitsDue()`, `frontStopMs()`). Rest
  is then confirmed by the last hall tick. At the end of a ramp a tick is tens of ms long, so where the last tick falls
  scatters the reading by about that much.
- **The verdict stands (D2).** The 20 ms slack is tighter than the reading's own resolution at the end of a ramp, so
  the cell can fail a correct stop.

**Disposition: Watch.** The fix is a bound derived from the last tick's duration at the ramp's end, stated before a
run. It is never the worst reading seen. What would make it actionable: a TIMESTOP later than about 60 ms past its
deadline, which the tick scatter cannot explain.

**2026-09-27, Visit 10 pass 7:** ACTIONABLE. The steering TIMESTOP read `measured,386` against 320: rest confirmed
86 ms past the deadline, beyond this entry's 60 ms line. The single-wheel form (WTIMSTOP) read 314. The root cause is
being traced at the desk alongside the front-cog overrun (PL-161); late passes and the DRIVER_REV 33 limit bookkeeping
are the candidates.

**2026-09-27, desk root cause: the INSTRUMENT.** Neither candidate: the time-stop path is unchanged since DRIVER_REV
29, and each pass re-reads `getms()`, so late passes can delay the stop by about 1 ms each, not 86. **DERIVED:** the
driver brings the FIELD to zero at the deadline; the bridge then coasts, and the rotor, which the ramp-down lets lead
the field by up to LAG_SOFT (~1.9 hall ticks), still crosses hall edges and restarts the cell's 300 ms rest dwell.
The cell times coast, which friction sets, not the stop, which the driver sets. **Disposition: ⛔ FIX the cell,
built** (`test_bench_dual` SRC_REV 57, FMT 36): TIMESTOP-D and WTIMSTOP-D now judge when every driver of the form
first reads DCS_STOPPED (polled 1 ms), criterion FIELD_ZERO_BY_LIM, bound −4..+7 ms of the deadline, each term derived
from library constants in the CON block. Negative: a stop fired at the deadline instead of a ramp-down before it
reads about +646 ms. New record `BM-TIMESTOP` (`zero_ms` judged; `rest_ms` the old reading, unjudged; `late_pass`).
Not covered by the bound, so it would FAIL as a real late stop: ramp-down passes held while the rotor leads by
LAG_SOFT. Certifies at pass 8.

### PL-146 -- part D's event drains read a stalled wheel's log before its fold-back released

> ✅ **DONE — CERTIFIED 2026-09-27, RC pass** (`debug_260927-141141.log`): R20-DUAL-EV-FOLDBACK PASS and FOLDBACK-D
> L/R PASS. Consequence recorded under PL-150: with the offset no longer counted, the unloaded left wheel keeps up at
> 1 A, so pass 7's HOLDSET/NOTFOL left PASS were this defect's artifact.

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: pass 7 EV-FOLDBACK 0 bad.

**Found 2026-09-26** at Visit 10 pass 6 (evaluation §5).
- **MEASURED:** R20-DUAL-EV-FOLDBACK FAIL, 1 bad. The BLOCK drain holds `FOLDBACK,wheel,LEFT,...,value,0` (engage, ms
  64_326) and no left release. The right's pair is complete: engage 64_334, release 69_310 with 4_295 frames.
- **DERIVED:** the drain waited EV_SETTLE_MS (1_032 ms) after the step's rest wait, which confirms rest by *position*.
  The left was stalled at 1 A, so it read at rest while its field was still ramping down under the fold-back. Its
  release, queued after a second of quiet, fell after the drain at about ms 69_790.
- **Not a driver defect:** the driver logged the engage, and would log the release after its quiet second, as
  designed.

**Disposition: ⛔ FIX, built** (`test_bench_dual` SRC_REV 52). Each part D drain first waits, bounded by D_REST_MS,
for both drivers to read DCS_STOPPED; the settle counts from there. Certifies at pass 7 (EV-FOLDBACK 0 bad).

**2026-09-27, Visit 10 pass 7:** RE-CAUSED. The drain-timing fix did not cure it: R20-DUAL-EV-FOLDBACK FAIL again,
1 bad, the left's engage (65_351) with no release.
- **VERIFIED in source:** the PASM fold-back compares the RAW `sense_i_` (the left board rests at ~8 mV) against
  `max(duty_, duty_floor_) * i_limit_k_ >> 16`, and it runs on an undriven bridge (`isp_bldc_motor.spin2`
  ~:7273-7280; the fault test's `tjnz bridge, #.noFault` falls into it). At the harness's 1 A limit the threshold at
  the duty floor is a few mV, so the left counts a fold-back on every frame at rest and never releases.
- **FIX built** (DRIVER_REV 36, f9c1d81): `tjnz bridge, #.servoTrim` at the head of `.noFault` — an undriven
  bridge skips the compare, the duty cut and the count; `.dutyLimits` still applies `duty_min_` as before. Cog RAM
  495 of 496. A wheel held at rest (SM_BRAKE) is driven, so its fold-back still acts; netting the rest offset out
  would need a new parameter long (an ABI change) and is not done. Certifies at pass 8 (EV-FOLDBACK 0 bad).

**2026-09-27, built (DRIVER_REV 37), the driven-at-rest residual.**
- **VERIFIED in source:** after DRIVER_REV 36 the compare still took the RAW `sense_i_` on a DRIVEN bridge, and a
  wheel held at rest (SM_BRAKE, `checkstop` sets `BR_DRIVE`) is driven: the left's ~8 mV offset against a ~11 mV
  threshold (DERIVED: 3 x 1 A x 150 x 10 / 400 at the duty floor, Rev B) counts on noise.
- **Built:** a new parameter long `sense_zero`, APPENDED after `drv_release` (DRVR_PARAMS_LONGS_COUNT 26 -> 27,
  `isAbiLayoutValid()` and `bOutsideDriverRuns()` now end the run at `sense_zero`). The Spin2 side hands it
  `restZeroSenseMv` (same units as `sense_i_`, mV), never negative, and 0 when the rest zero is out of its band
  (`applySenseZero()`, from `restZeroBegin()`/`restZeroFinish()`; `init()` writes 0). `.noFault` compares
  `max(sense_i_ - sense_zero_, 0)` (new register `fold_net`); `sense_i_` itself stays raw, as it is reported.
- **Cog RAM, from the compiler** (`pnut-ts -l`, FOLDBACK_CNT_'s VALUE): 495 -> 487 of 496. The fold-back cost 5 longs
  (two registers, three instructions); `countIllegal` (13 longs, unchanged) moved to the LUT block to pay for it: LUT
  280 -> 293 of 512 (LUTCODEEND $318 -> $325).
- **Negative** (the reading that shows it did not work): R20-DUAL-EV-FOLDBACK still FAIL with a left engage and no
  release, or `foldback_frames` still advancing on a wheel held at rest at the 1 A limit. The over-netting negative:
  a stall at 1 A with no EV_FOLDBACK engage. Certifies at pass 8.

### PL-149 -- no shipped demo has run on hardware against the 6.0 API

> ✅ **DONE — CERTIFIED 2026-09-27, RC pass** (`debug_260927-143043.log`, `debug_260927-143212.log`): both release
> demos ran end to end on DRIVER_REV 46 — start checks clean, `* wiring: ok` / `LEFT ok, RIGHT ok`, every
> `* stopped:` SR_AT_LIMIT, `demo-dual` `* DONE`.

> **6.0 status (2026-09-26 audit):** RELEASE — the demos are what users copy; compile-only today.

**Found 2026-09-26** by the release audit.
- `demo_single_motor` and `demo_dual_motor` (the release demos) were rewritten for the 6.0 API («#3624», 1fa665d), as
  were the RC and HDMI demos. They now cover start checks, stop reasons, the event log and the fault response.
- The compile gate certifies them plain and with `-d` (PL-142). **No bench log shows any of them run on the 6.0
  driver;** the last hardware run of a demo is Visit 1, v5.x.

**Disposition: ⛔ release work.** One wheels-up run of each release demo through `tools/bench-run.sh` (a tier each,
unattended), read like any other log. The RC demo also needs the RC transmitter, so it is Stephen's call whether it
joins.


### PL-150 -- the floor run has no cells for two load-dependent 6.0 claims

> **6.0 status (2026-09-30, the rerun):** ✅ CERTIFIED — both slow together under a light one-sided hold
> (R21-DUAL-LDPATH-P `mis_pm,30`, bound 100; `l_pct,49,r_pct,47`, 33 / 32 ticks) and the held wheel holds without a fault
> (LDHOLD 276 ms; the first visit 284 ms). FLOOR-RERUN-EVALUATION.md §3.

**Found 2026-09-26** by the release audit. The floor run's sheet (`VISIT-6B-FLOOR-RUNSHEET.md`, «#3576») carries
SPINSTOP, SPINSTRT, SPINPEAK, SPINSYM, SPINCTL, SPINLEAD, SPINPLAT and the CREEP cells. It carries nothing for:
- **the path limiter under load** ("when one wheel cannot keep up, both slow together"): certified only wheels-up, at a
  lowered current limit (pass 7, PL-144);
- **the overload hold** ("holds the fastest speed it can sustain instead of faulting"): shown only wheels-up under a
  lowered limit (Visit 9b G-3).

The protective stop on a blocked wheel is PL-106, and the 27 A derate cannot be reached on this rig. The README now
states the derate as a design limit.

**Disposition (was ⛔ release work, now discharged):** the loaded path cell and the overload cell were built into the
floor run (`floor-grab`: LDPATH, LDHUNT, LDHOLD) and certified on 2026-09-30, as the status banner above records.

**2026-09-27, RC pass (evaluation F4): the hold is floor-only, and pass 7's wheels-up evidence for it is withdrawn.**
Pass 7's R18-DUAL-HOLDSET-D and -NOTFOL-D LEFT PASS came from the 1 A step stalling a left wheel that the PL-146
defect throttled on its rest offset (`first_short_ms,601`). With PL-146 fixed, neither unloaded wheel holds at 1 A
(`first_short_ms,NA`, both NOMEAS). The floor run's LDHOLD, HELDATSPD and LDPATH are therefore the only evidence the
hold and the path limiter will have; PL-144 certifies there too.


### PL-161 -- the steering front cog overruns its 1 ms slot

> ✅ **DONE — CERTIFIED 2026-09-27, RC pass:** FRONTST-D ×2, FRONTST-EV ×2 (≤ 950 µs) and R22-T0-FRAMESLACK PASS.
> Worst pass: `dual-start` lifetimes 389–553 µs, `late,0` (pass 7: 533–1,058); STEERSEG 517 µs (pass 7: 1,015,
> `late,3`); least PWM loop 4,382 clocks against 699 of frame work.

> **6.0 status (2026-09-26 audit):** RELEASE — found at Visit 10 pass 7; the front cog is what services every command.

**Found 2026-09-26** at Visit 10 pass 7 ([evaluation](analyses/bench/2026-09-26/pass7/VISIT-10-PASS7-EVALUATION.md) §3, §4).
- **MEASURED:** STEERSEG `max_us,1_015,late,3` (R16-DUAL-FRONTST-D FAIL). A wiring-walk end-pass took 1,058 µs
  (pass 6: 874 / 921). About +140 µs was added to the worst pass.
- **Candidates (UNDETERMINED which):** the pack sampler, which runs every pass (rdpin plus two `muldiv64`), active for
  the first time now the sensor is fitted; and the per-pass odometer and limit-base work added at DRIVER_REV 33.

**Disposition: ⛔ FIX by construction** (DRIVER_REV 36): the pack is sampled at slot cadence with its conversion off
the per-pass path, and the per-pass additions are reviewed. Separating the candidates on the bench is not needed.
Certifies at pass 8 (FRONTST late 0, max under 950 µs).

**2026-09-27, built (DRIVER_REV 36, f9c1d81).** The desk review found a third cause larger than either candidate:
- **DERIVED:** the worst pass is a request pass that busy-waits for a synchronized driver take, up to one drive pass
  (523 µs), on top of its own work. Pass 7's dual-start lifetimes of one binary read 533-1,058 µs, a spread of one
  drive pass, so the +140 µs between passes cannot be pinned on added work.
- **Built:** the pack pin is summed inline and folded once per slot (PACK_PHASE 2), kept in raw counts, converted
  when read. The steering state report (~45% of a pass's calls, printing nothing in the bench build) runs only when
  its debug channels compile, once per slot. A request that would wait is not taken on the slot-work phases 0 and 4;
  it is taken on the next pass (the acknowledgement bound, 17.5 ms, stays under the 20 ms timeout). The odometer and
  limit additions measured negligible.
- **If pass 8 still shows a ~520 µs spread across dual-start lifetimes,** that spread is the wait itself, and the
  remaining fix is answering synchronized requests on a later pass instead of waiting in it.

**2026-09-27, built (DRIVER_REV 37), that remaining fix, by construction, in both front cogs.**
- **VERIFIED in source:** three in-pass busy-waits were reachable from each front cog's request service: the
  synchronized take (steering `frontWaitForDrivers(WAIT_SYNC_TAKEN)`, single `bFrontWaitForDriver()`), the e-stop
  release (`WAIT_ESTOP_LEFT`) and the PL-66 fault clear (`frontClearFault()`, `WAIT_FAULT_LEFT`), each bounded at 4 drive
  passes (2.09 ms), two in one pass for a drive of a FAULTED wheel. The single-motor front cog had the same pattern.
- **Built:** all three are gone. A request whose drivers must act is held IN FLIGHT (`pendStage`: PST_FAULT_LEFT,
  PST_SYNC_TAKEN, PST_ESTOP_LEFT), polled once at the head of each pass, and answered on the pass that sees the
  condition, or `bFrontWaitExpired()` (the same 4-drive-pass bound, condition read first, as before). One in flight at
  a time; while it is, nothing else is taken (as nothing was during an in-pass wait); the phase bar of DRIVER_REV 36 is
  removed. Statuses are the busy-waits' (ERR_SYNC_TIMEOUT, ERR_NO_RESPONSE per wheel, the zeroes, audit M). Lockstep
  is unchanged: both commands written, then ONE `cogatn()` of both drivers' bits, in the same pass as before.
- **Worst pass, in operations:** no loop reachable from `frontLoop()` now exits on a driver's state; the request
  service is bounded by its slots and classes (8-slot scan, at most 4 x 8 `frontTakeSlot()` copies, at most one apply
  per open slot, at most one poll of 2-3 getter calls and one `getct()` compare). The in-flight write pass adds one
  drive write per wheel, one `cogatn()` and the records, straight-line. So a pass's length no longer contains a term
  set by a driver (was up to 523 µs live, 2 x 2.09 ms bounded); what remains is the fixed work pass 7 read as the
  low end of the lifetimes (533 µs), plus DRIVER_REV 36's savings.
- **Acknowledgement bound (DERIVED):** a live driver acts within one drive pass, under the 0.9 ms least pass interval,
  so a request in flight is answered on the next pass (one pass later than before). With every bound gone: 15 ms
  steering (4 ahead x 3 passes + 3), 18 ms single (5 x 3 + 3), under 20. A two-stage request (drive of a FAULTED wheel)
  with both bounds gone adds 3 passes each (the old in-pass pair added 2 x 2.09 ms): not under 20 ms if every cog posts
  one at once, as it was not before.
- **Negative** (the reading that shows it did not work): R16-DUAL-FRONTST still late or max at or over 950 µs, or the
  dual-start lifetimes' max still one drive pass (~520 µs) above their min. And for the change itself: any
  ERR_SYNC_TIMEOUT or ERR_NO_RESPONSE on a live driver, or a ~1 drive-pass lag between the wheels' starts (lockstep).
  Certifies at pass 8.

**2026-09-27, built (DRIVER_REV 39), the stop prediction moved out of the front cogs, by construction.** Not yet run
on hardware.
- **Found at the desk (DERIVED, not measured):** DRIVER_REV 38's `stopPlan()` (PL-160) ran on every front pass while
  a limit was armed, once per query. The steering front cog made up to **4** runs a pass. A platform time limit asks
  both wheels (`frontStopMs()`), and the distance is asked on every pass the time is not due. So a platform time limit
  plus a platform distance limit (`REQ_LIMIT_TIME` and `REQ_LIMIT_TICKS` arm independently) makes 2 + 2 runs. So does
  a platform time limit plus a `driveForDistance()`, whose `REQ_DRIVE_DISTANCE` keeps the time limit. A platform
  distance and wheel distances are never armed together (each request disarms the other). The single-motor front cog
  made at most 1 (time *or* distance). One run on its worst path costs 15 calls, 12 `muldiv64`, ~12 float operations
  (one `FSQRT`) and 2 `SQRT`.
- **Built (option D, the owner's ruling): the DRIVER plans its own stop; the front cogs only read it.**
  - After each drive pass, `planStage` runs in the slack of the next **nine** PWM frames, after each frame's status
    write, one third of one plan per frame (`planA` the corner or unwind, `planB` the rise, `planC` the plateau and
    ramp-out; the state stays in the `pl_` registers). Stages 1-3 plan the stop from the pass's own (v, a) (m = 1).
    Stages 4-6 and 7-9 plan it after a **take pass** at each end of that pass's reachable accelerations, a' = a - Jx
    and a' = a + Jx (v' = v + a'), plus the take pass itself (m = 2). Stage 9 publishes the largest passes and travel
    as `drv_stop_passes` / `drv_stop_fp`, seen at the tenth frame's status write, **≤ ~232 µs after the pass**.
  - **The take pass under ANY command (closes last round's open gap by construction):** whatever the next pass reads
    -- the command this pass took, a new command written after this pass read its own, a synchronized command
    released since, a stop -- and whatever its lag gate does, `jerkStep` gives a' in [a - Jx, a + Jx],
    Jx = max(jerk_up, jerk_dn). On every branch alpha' ≥ min(U, alpha - J) ≥ alpha - Jx and alpha' ≤ U ≤ alpha + Jx; at
    a target |a| ≤ Jx gives 0; a stop reaching rest only shortens. The plan after the take pass is longest at an end of
    that range. So the two ends bound every command without the front knowing which one the pass reads: no 25th
    status long, no bookkeeping of command times, and no wait in the front cog are needed.
  - The planner (`planA`/`planB`/`planC`) is the PL-160 closed form in integers. Its sums are exact 64-bit (6 x SUM = 3[(n-1)V + (n+1)v_end] +
    d(n^3-n)/2 per run). The corner and rise roots are `QSQRT` floors, with no float and no correction loop. x*(E) is
    moved out of `jerkStep` unchanged (`xStar`) and shared.
  - `frontStopMs()`, `frontStopTicks()`, `bFrontStopMsReaches()` and `bFrontStopTicksReaches()` read the two longs.
    The Spin2 `stopPlan()`, its helpers, and the interim kept-plan / cheap-bound machinery are deleted.
  - **Front-cog stop-prediction cost: 1 hub read and 1 compare per limit query, for both front cogs.**
  - **Read-to-write ordering (both front cogs):** every stop limit writes its stop before any output or bookkeeping.
    `bFrontLimitsDue()` and the steering's `bFrontPlatformLimitsDue()` no longer print. `frontReportLimit()` /
    `frontReportPlatformLimit()` print after the writes, and a platform stop writes both wheels' zeros first
    (`frontWriteStop()`), then each `frontZeroPower()`.
    - The worst read-to-write span is the platform distance limit's left wheel: ≤ 5 method calls, 8 returns and ~15
      simple statements. There is no loop, wait or `debug()`.
    - ESTIMATE: ≤ 500 clocks per call/return pair and ≤ 100 per statement gives ~4,750 clocks, ~30 µs at 160 MHz.
      The proof needs **< ~268 µs** (the next-but-one pass cannot read its command before T_k + 1,000 µs, since each
      pass waits its 500 µs CT1 deadline; publication takes ≤ ~232 µs). That is ~9x margin, by construction of the
      ordering, whatever the debug mask.
- **ABI:** status run 22 -> **24** longs, `fault` after them: `DRVR_STATUS_LONGS_COUNT` 24, plus named indexes
  `DRVR_STATUS_ACCEL_NOW_IDX` 21, `DRVR_STATUS_STOP_PASSES_IDX` 22 and `DRVR_STATUS_STOP_FP_IDX` 23;
  `isAbiLayoutValid()` checks all three. **`drv_accel_now` is no longer the run's last long.** test_bench_t0's
  `T0R_ST_ACCEL = motor.DRVR_STATUS_LONGS_COUNT - 1` now indexes `drv_stop_fp`, and must become
  `motor.DRVR_STATUS_ACCEL_NOW_IDX`. test_bench_dual's `ABI_STATUS_LONGS` follows the count. Harness owner's to change.
- **Memory (read from the compiler listing):**
  - cog RAM 492/496 (was 403): 20 registers, `loadOverlay`, `planFp` and `planCorner`.
  - LUT 507/512 (was 402): `xStar`, `run` and `planStage`.
  - The planner's core (`planA`/`planB`/`planC`, `planSat`, `rampOut`) is a **LUT overlay**: it is block-loaded over
    the spent start sequence ($200-$280) as the start sequence ends. It uses 126 of those 129 longs
    (`fit gettgtincr`).
- **Clocks.** The lowest clock: nothing in the driver bounds clkfreq (frame_cnt = clkfreq / 44 kHz, the 500 µs CT1
  deadline and the dead gap all scale with it; only a comment names 200/270/300 MHz), so **160 MHz**, as instructed.
  Worst-case model: 2 clocks per instruction, 4 per taken branch/call/return, CORDIC issue up to 9 and result 55
  later (p2kb), every operation waited for.
  - Frame work is ≤ 699 clocks (`frame_clocks.py`, every branch counted as taken). A stage's worst, from the
    interpreter (`desk_driverplan2.py` E), per stage 1-9: 1,296 / 1,052 / 1,726 / 1,324 / 1,052 / 1,740 / 1,328 /
    1,052 / 1,750.

    | Clock | Frame | Slack after frame work | Worst stage | Share of slack |
    | --- | --- | --- | --- | --- |
    | 160 MHz | 3,636 | 2,937 | 1,750 | 60% |
    | 200 MHz | 4,545 | 3,846 | 1,750 | 46% |
    | 270 MHz | 6,136 | 5,437 | 1,750 | 32% |

  - The drive pass's own frame carries no stage: ≤ 699 + 1,184 = 1,883 of 3,636 clocks at 160 MHz (an upper bound;
    pre-existing work plus ~10 clocks).
  - **No floor on clkfreq is needed by this planner above 160 MHz.** Outside PL-161's scope, but found:
    - the front cog's Spin2 pass (533 µs measured at 270 MHz) scales with the clock, to ~900 µs at 160 MHz;
    - PL-50's "22 truncated frames fall short of 500 µs" does not hold at a clock that is an exact multiple of 44 kHz
      (176 or 264 MHz), where the pass can run on the 22nd frame.
- **The status run's age, and never-late (DERIVED; desk-checked):**
  - A plan published for pass k counts passes from pass k's own time T_k. It is read at t ≥ T_k, so counting from
    now can only over-state the stop. That makes it early, never late, and no age correction is needed.
  - A stop the front writes after reading it is taken by pass k+1 (m = 1) or, if that pass has already read its
    command, by pass k+2 (m = 2: the take pass first, under any command). The plan is the largest of those.
  - m ≤ 2 holds when the read→write span is under 1,000 µs - 500 µs - ~232 µs ≈ **268 µs** (above). By the ordering
    rule it is a few calls, whatever the debug mask.
  - Remaining stated exclusion: the lag gate holding a pass DURING the stop (as for PL-160's plan and the harness's
    TIMESTOP bound). The take pass's lag gate is covered by the range. An alpha above A (a lowered deceleration
    mid-stop) is taken as A, as PL-160's plan did, and over-predicts only.
  - At rest the plan is no longer 0: with the built-in rates, 3 passes (`frontStopMs()` 2 ms), 0 ticks, since the
    take pass might yet start a drive.
- **Desk check (`desk_driverplan2.py`, outside the tree, seed 5, 3,000 samples):** the PASM is executed from its
  source lines by the instruction-level interpreter (392 instructions).
  - **B, planA+B+C vs the pass-by-pass stop:** 2,977 stops. Passes: 0 under, 87 over (all alpha > A). Travel: 0 under.
  - **C, the published pair vs its definition** (max of the m = 1 walk and 1 + the walk from each end, with |v'|):
    2,983; 0 under.
  - **G, the take-pass range:** 3,000 states x 4 random commands (a stop, the same, a reversal, any speed) with a
    random lag gate: a' outside [a - Jx, a + Jx] **0**. An a' drawn inside the range beating both ends: **0 of
    36,000**. The ends' maximality is sampled, not proved.
  - **D, never late:** a timeline with passes 500-523 µs apart, a read anywhere the pair is visible, a stop written
    within 268 µs, and **a new command written at any time after pass k read its own** (the take pass then runs
    whatever the hub held at its read, with a random lag gate): 3,000 reads, **0 late**. Cruising at the built-in
    rates (1-2 s stops), the prediction is ahead of the rest by at most 3.5 ms. That comes from the take pass
    (+1 pass beyond DRIVER_REV 38's), the age (≤ ~0.75 ms), ms rounding, and 523 vs 522.7 µs.
    **R16-DUAL-TIMESTOP's EARLY bound (4 ms) does not count the age term.** It is tight against this; the harness
    owner should re-derive it.
- **Desk-only intermediate steps this replaced, recorded because the owner ruled on them:** a kept plan with a
  cheap-bound gate (its bound had 0 violations in 60,000), and a proposed one-plan-per-pass alternation. The
  alternation was shown to fire late: the stop grows 2-6 ms per drive pass at built-in rates, up to ~40 ms per pass
  across the setter range, and 132-159 ms at a reversal's crossing.
- **Negative** (what shows it did not work): R16-DUAL-FRONTST late or max at or over 950 µs; a distance or time
  limit coming to rest outside its cell's tolerance; a PWM frame overrun or ADC sample loss in the nine frames after
  a drive pass (loop_dtcks), at the bench clock or at 160 MHz; any change in the start checks (the overlay loads
  after them). Certifies at pass 8.
- **Arbiter's ruling (2026-09-27):** the any-command bound is accepted in place of a 25th status long. It is
  never late by construction, puts no wait back into the front pass (DRIVER_REV 37's rule), and costs up to one
  pass of early firing.
- **Found by the same work, recorded (DERIVED):**
  - **The front cog's Spin2 pass scales with the system clock.** 533 µs measured at 270 MHz would be about 900 µs
    at 160 MHz, against the 950 µs budget. The driver states no minimum clock, and every demo runs at 270 MHz,
    so the release documents 270 MHz as the tested clock and says that below about 250 MHz the front cog's
    1 ms pass has not been shown to keep its slot.
  - **PL-50's 23-frame drive pass can be 22 frames** at clocks that are exact multiples of 44 kHz (176 and
    264 MHz). Not at 270; ancillary to 6.0.

### PL-162 -- two pack cells are judged with a wrong instrument

> ✅ **CLOSED 2026-09-27** by Stephen's ruling (no more unplug testing; pass 7's detection stands): *"we need to stop unplugging the sensor - it's wearing on the hardware - we know it works why keep testing it?"*

> **Was:** RELEASE (instrument) — found at Visit 10 pass 7.

**Found 2026-09-26** at Visit 10 pass 7 ([evaluation](analyses/bench/2026-09-26/pass7/VISIT-10-PASS7-EVALUATION.md) §3, §4).
- **R20-PACK-ABSENT FAIL 1 of 2 (VERIFIED in the harness):** the cycle reference and the calibration mark are taken
  from the last pre-ABSENT sample of a decaying average (`pkRefMv := pkHistMv[0]`, and `pkMarkMv`). Pass 7's reference
  read 20,505 against a steady 20,688; the replug read 20,684.
- **R19-DUAL-PACK-X FAIL 10/10 (VERIFIED):** the criterion hard-codes "no sensor fitted", and the sensor is now fitted.
- The calibration (1012) is unaffected: its mark matched the steady mean within 3 mV.

**Disposition: ⛔ FIX** (harness SRC_REV 56): the reference and the mark come from the steady reading, and PACK-X is
judged against the configuration.

**2026-09-27, RC pass:** R19-DUAL-PACK-X PASS (0 bad of 10) — that half is certified. R20-PACK-ABSENT and PACK-EV's
unplug half FAILED on `OPERATOR_TIMEOUT`: no unplug seen in 60 s (`o_seen,FALSE`), so the steady-reference fix was never
exercised. Whether the Powerpole was unplugged decides it (asked of Stephen): not unplugged → re-run `dual-pack`;
unplugged → the driver's absent detection is investigated at the desk first (DRIVER_REV 36 changed the pack sampling).

**2026-09-27, STEPHEN RULED: no more unplug testing** — *"we need to stop unplugging the sensor - it's wearing on the
hardware - we know it works why keep testing it?"* The absent detection's evidence stands on pass 7, where both unplugs
were detected (the FAIL there was the harness's reference, fixed at SRC_REV 56); DRIVER_REV 36 changed the sampling
cadence, not the absent test, and the RC pass's steady readings certify the sampling path at DRIVER_REV 46. PL-162 is
**CLOSED** on that evidence and this ruling; `dual-pack`'s unplug cycles are not run again.
