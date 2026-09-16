# Abort and Error Contract -- Design (task «#3538», phase 1)

**Date:** 2026-09-14
**Status:** DESIGN FOR REVIEW. No source was changed in this phase.

> **AMENDED 2026-09-16 by Stephen's rulings. Where the body below disagrees, this block governs.**
> - **§5 Q1: yes.** Command methods return a status (0, or a negative `ERR_*`), and callers may ignore it.
>   STEPHEN: *"We can actually change the contract to say an error code is returned. The success and error code
>   is returned, and that will not affect any users today until they decide to use it."*
> - **Getters and conditions found after the call returns** use a documented neutral value plus `getError()`.
>   STEPHEN: *"yes, option 1"*.
> - **§5 Q3 and §3.7: no abort anywhere.** While a protective stop is latched, energising calls refuse and
>   return its code; they do not abort. STEPHEN: *"yes your A"*.
>   - Names as proposed: `clearProtectiveStop()`, `getProtectiveStop()`, `ERR_PLATFORM_BLOCKED`.
>   - `getError()` returns an active protective code first and does not clear it.
>   - `abortIfProtectiveStop()` becomes a refuse-and-return check, and I2's "one abort per file" becomes "no
>     abort".
> - **§3.7's detector is in this sprint**, designed with the current-limit work (S-2, C-5). STEPHEN: *"i want
>   intelligent behavior to limit current vs. aborting where this is the right thing to do for the dirving
>   system"*.
> - **Sense tasks:**
>   - The e-stop auto-clear (S-4) is deleted, not gated: the e-stop latches until `clearEmergency()`.
>   - The sense loop is the front cog of `FIXED-COG-SHAPE-DESIGN.md`, at 1 ms, not 8 Hz.
> - **Protective stop as a whole:** motors secured where detected, refuse-and-return, acknowledgement by
>   `clearProtectiveStop()`.
**Governs:** PL-47 (`DOCs/PUNCH-LIST.md:1475-1528`). Feeds «#3539» (bench-harness trap removal).

**Provenance tags** follow the project convention (`DOCs/analyses/PL-44-ROOT-CAUSE-STUDY.md:20-21`):
- **MEASURED** means a log line.
- **DERIVED** means a reading of source or of the P2 knowledge base, or inference from one. Where a
  DERIVED claim rests on an inference rather than a direct reading, it says "(inference)".
- **UNVERIFIED** marks a P2/Spin2 fact the knowledge base does not state.

Line references abbreviate as follows:
- `lib` = `src/isp_bldc_motor.spin2`
- `steer` = `src/isp_steering_2wheel.spin2`
- `serial` = `src/isp_steering_serial.spin2`
- `t0` / `char` / `scan` = `src/test_bench_*.spin2`

**Owner's rules, verbatim (STEPHEN 2026-09-14; PL-47):**
- *"an abort can return a value, we should never return a zero from an abort as it wouldn't be
  recognizable as a bare abort returns zero"*
- *"if the rhs method that was aborted returnes a value when not aborted we can't let abort values be
  in the set of method returned values"*
- *"a bare abort returns 0 so a method that also returns zero won't see the abort case"*
- *"traps are an exeptional return path - not normal use (we likelly abort to protect hardware from
  being damaged - or actuators harming their environmnet"*
- *"if we are diving at high rate of speed and all of a sudden both motors start showing hi current
  this probably means the platorm is now blocked by something... continuing to drive the motors in
  this case would likely cause harm  this might be good cause for abortive behavior"*
- *"for methods that can't signal an error why don't we have an error variable (do we need this per
  calling cog) that carries the error or no-error which we then check in our tests"*
- *"never see the bench as an esy way out to avoid doing real engineering. design for "correct by
  construction" to reduce side-effects"*

**Spin2 facts this design rests on:**
- A bare `ABORT` "returns 0 to the trapping caller". `ABORT expression` returns that value. A trap
  returns the method's normal value when no abort occurs. Uncaught, "the program terminates". An
  abort unwinds "the call stack" of the executing code. DERIVED, `p2kbSpin2Abort`.
- A method with no declared result returns 0. DERIVED, `p2kbSpin2MethodDefinition` (`default_return`).
- `COGID()` "always returns 0-7, never -1" and does not change during the cog's lifetime. DERIVED,
  `p2kbSpin2Cogid`.
- An abort cannot cross from one cog to another, because each cog runs on its own stack. DERIVED
  (inference) from the unwind semantics above and `p2kbSpin2MethodDefinition` `stack_usage`.
- What "the program terminates" does in a cog other than cog 0 is **UNVERIFIED**. The design never
  depends on it: see I3 and I6.
- Whether VAR longs are laid out strictly in declaration order is **UNVERIFIED**: `p2kbSpin2KwVAR` says
  only "aligned to natural boundaries". The design does not depend on it either, because the extended
  ABI guard (§3.8) refuses to launch the driver if the layout is ever wrong.

---

## 1 · Inventory

### 1.1 Every `abort` in the library

**Scope read in full:**
- `lib` (2999 lines)
- `steer` (1266 lines)
- `src/isp_dist_utils.spin2` (143 lines, no `abort`)
- `src/isp_bldc_motor_userconfig.spin2` (244 lines, constants only, no `abort`)
- `src/isp_bldc_motor_userconfig_bench.spin2` (100 lines, constants only, no `abort`)

These are every object `lib` and `steer` include (`lib:59-66`, `steer:86-95`).

**Result:** 22 `abort` sites, 15 in `lib` and 7 in `steer`. **Every one is bare (value 0). None has a
protective purpose.** DERIVED.

"Normal returns" in the table is the set a trapping caller can receive when no abort happens. It is
given at the method, and at the public method the abort escapes through when that differs.

| # | Site | Method | Value | Normal returns of the method (and of the public method it escapes through) | Abort in that set? | Trigger | User input reaches it? | Protective purpose? |
|---|---|---|---|---|---|---|---|---|
| A1 | `lib:259` | `validatePinBase()` (PRI) | bare 0 | {-1, 0, 8, 16, 32, 40} (`lib:255-260`, enum `lib:23`). Escapes through `validBasePinForChoice()` (same set, `lib:989`), through `start()`/`startEx()` {-1..7} (`lib:86`, `:112`, `:121`), and through `testSetup()` {0} | **Yes**: 0 = `PINS_P0_P15`, cog id 0, and testSetup's default 0 | Requested 16-pin group overlaps a group another instance has claimed (`lib:223-248`) | Yes: base argument of `start`/`startEx`/`testSetup`/`validBasePinForChoice` | **No.** The claim is refused before any pin is touched (`lib:257` precedes `:272-278`), so refusing already prevents two drivers on shared pins. Unwinding adds nothing. Ordinary error. |
| A2 | `lib:580` | `stopAfterRotation()` | bare 0 | {0}: no declared result | **Yes** | `nRotationCount < 1` | Yes | No. Ordinary error. |
| A3 | `lib:595` | `stopAfterRotation()` | bare 0 | {0} | **Yes** | Rotation units not `DRU_*` | Yes | No. Also **erases an armed limit before aborting** (`lib:583`): see F-4. |
| A4 | `lib:606` | `stopAfterDistance()` | bare 0 | {0} | **Yes** | `nDistance < 1` | Yes | No. |
| A5 | `lib:610` | `stopAfterDistance()` | bare 0 | {0} | **Yes** | `user.WHEEL_DIA_IN_INCH == 0.0` | Yes, by configuration | No. Configuration error. |
| A6 | `lib:632` | `stopAfterDistance()` | bare 0 | {0} | **Yes** | Distance units not MM/CM/IN/FT/M | Yes | No. |
| A7 | `lib:643` | `stopAfterTime()` | bare 0 | {0} | **Yes** | `nTime < 1` | Yes | No. |
| A8 | `lib:650` | `stopAfterTime()` | bare 0 | {0} | **Yes** | Time units not `DTU_*` | Yes | No. |
| A9 | `lib:726` | `getDistance()` | bare 0 | Non-negative integers including 0. `posTrkHallTicks` only ever adds absolute deltas (`lib:1751`, `:1760`, `:1871`). 0 is also returned silently when wheel diameter is 0 (`lib:700-702`) | **Yes** | Units not `DDU_*` | Yes | No. A query. |
| A10 | `lib:744` | `getRotationCount()` | bare 0 | Non-negative integers including 0 (same accumulator). The `-1` preset at `lib:732` is unreachable | **Yes** | Units not `DRU_*` | Yes | No. A query. |
| A11 | `lib:1275` | `incrementForPower()` (PRI) | bare 0 | Signed increments including 0 (a stop, `lib:1285`). Escapes through `driveAtPowerEx`/`driveAtPower`/`driveForDistance` {0}, and through `steer` `driveAtPower`/`driveDirection`/`driveForDistance` {0} | **Yes** | Motion commanded while `eUserSelectedVolts == VALUE_NOT_SET`: never started, or the last `init()` aborted in `confgurePowerLimits()` after `lib:380` | Yes, by call order | No. With no driver cog nothing is energised. The case where a cog is running (`testSetup()` re-init of a running motor with a bad voltage, `lib:170` → `:1376`) is protected by refusing the command, not by unwinding. Ordinary error. |
| A12 | `lib:1376` | `confgurePowerLimits()` (PRI) | bare 0 | {0}. Escapes through `init()` → `start`/`startEx` {-1..7} and `testSetup` {0} | **Yes**: 0 = cog id 0 | `eMotorVoltage` not legal for `user.MOTOR_TYPE` (`lib:1373-1376`; argument honoured since PL-14, `lib:394-399`) | Yes | No. Also **leaks the pin claim** taken at `lib:272`: see F-2. |
| A13 | `lib:1408` | `confgurePowerLimits()` (PRI) | bare 0 | {0}, escaping as A12 | **Yes** | Doco voltage absent from the table. **Unreachable**: validator range `PWR_7p4V..PWR_24p0V` (`lib:998`) is enum values 2..8 (`lib:29`), exactly the table's seven entries (`lib:1385`) | No | No. A "SHOULD NEVER get here" guard over two copies of one list. |
| A14 | `lib:1422` | `confgurePowerLimits()` (PRI) | bare 0 | {0}, escaping as A12 | **Yes** | 6.5″ voltage absent from the table. **Reachable with `PWR_25p9V`**: the validator accepts 1..9 (`lib:1001`); the table ends at `PWR_24p0V` = 8 (`lib:1411`). Audit finding O | Yes | No. Two lists that disagree. |
| A15 | `lib:1455` | `motorVoltage()` (PRI) | bare 0 | Floats 6.0..25.9 (non-zero bit patterns, `lib:1452`). Escapes as A12 | At its own level no; through `start` **yes** | Voltage outside `PWR_6p0V..PWR_25p9V`. **Unreachable**: its only call (`lib:1427`) passes a value already found in the table | No | No. |
| B1 | `steer:276` | `stopAfterRotation()` | bare 0 | {0} | **Yes** | `nRotationCount < 1` | **Yes, over serial**: `isPostiveValue()` accepts 0 (`serial:463-466`), so `stopaftrot 0 …` reaches it (`serial:272-279`). See F-7 | No. |
| B2 | `steer:293` | `stopAfterRotation()` | bare 0 | {0} | **Yes** | Units not `DRU_*` | Yes | No. **Erases an armed limit first** (`steer:281`): F-4. |
| B3 | `steer:308` | `stopAfterDistance()` | bare 0 | {0}. Also escapes through `driveForDistance()` {0} (`steer:247`) | **Yes** | `nDistance < 1` | Yes, over serial (`serial:289-296`) | No. |
| B4 | `steer:314` | `stopAfterDistance()` | bare 0 | {0} | **Yes** | `tickInMM_x100 == 0`: wheel diameter 0, **or `start()` never ran** (it is set only at `steer:142-149`). The message at `:313` names only the first | Yes | No. |
| B5 | `steer:346` | `stopAfterDistance()` | bare 0 | {0} | **Yes** | Units not MM/CM/IN/FT/M | Yes | No. **Resets tracking first** (`steer:316`): F-4. |
| B6 | `steer:360` | `stopAfterTime()` | bare 0 | {0} | **Yes** | `nTime < 1` | Yes, over serial (`serial:306-313`) | No. |
| B7 | `steer:367` | `stopAfterTime()` | bare 0 | {0} | **Yes** | Units not `DTU_*` | Yes | No. |

**Every abort's value lies in its method's normal return set.** In 20 of the 22, and in all three
unreachable ones once they escape through `start()`, the value is the method's own default 0 or a
legal value (DERIVED from the table). This is exactly the ambiguity behind the owner's rules, and the
reason `t0` needed completion-flag wrappers (`t0:177-203`).

**Aborts that escape through `steer` from a wheel:** `steer:start()` calls both `startEx()`s
(`steer:119`, `:121`). If `rtWheel.startEx()` aborts (A1, A12, A14), `ltWheel` has already started a
driver cog parked on `waitatn`. The abort unwinds past the failed-start cleanup at `steer:124-133`,
so that cog and its pins stay held with no handle. That is audit AD's stranded motor, re-created on
the abort path. DERIVED (inference). Recorded as F-13.

### 1.2 Failures reported only as debug text, or not at all

"Queryable" means the caller can learn of the failure from a return value or state without reading
the debug stream.

| Site | What fails | What the caller gets today |
|---|---|---|
| `lib:113` `startEx()` | driver `coginit` failed | -1 (queryable), but no cause |
| `lib:367` `init()` ABI guard | status block mis-laid | **Nothing, and the driver is launched anyway** (`lib:109`) |
| `lib:421` `startSenseCog()` | sense cog failed | -1 but no cause. `demo_single_motor.spin2:72` ignores it, so every `stopAfter*` limit is silently unenforced (F-5b) |
| `lib:494`, `:504`, `:563` | out-of-range speed or power clamped | a warning line; the call succeeds at the clamped value (see open question Q4) |
| `lib:534` `moveShaftToAngle()` (TEST-USE) | request dropped, driver busy | nothing |
| `lib:827` `boardIdString()` | impossible `eDetectedBoard` | `"????"` |
| `lib:895` `getBoardType()` | pin base not set | `REV_Unknown`, the same value as "no board". Reached inside `init()` for an illegal base enum, and `start()` then continues (F-3) |
| `lib:1155` `testResetFault()` (TEST-USE) | fault did not clear within 2 s | nothing |
| `lib:1350-1369` `getInternalDetectMode()` | illegal detection mode | **silent**: mapped to `BRD_AUTO_DET` (F-8) |
| `lib:255-260` `validatePinBase()` | illegal base enum | **silent** `VALUE_NOT_SET`, and `init()`/`start()` continue (F-3) |
| `lib:700-702` `getDistance()` | wheel diameter unknown | **silent** 0 |
| `lib:589`, `:618-629` limits | request rounds to 0 ticks | **silent**: 0 means "no limit" to the sense task (`lib:1795`), so no limit is armed (F-5) |
| `lib:1444-1448` `SyncStatus()` | a wheel never takes the synced command | **hang, no return** (audit Q; F-6) |
| `steer:133`, `:167` `start()` | a motor or the sense cog failed | -1 but no cause and no wheel |
| `steer:447` `convertDistance()` | wheel diameter 0 / not started | debug line and 0 |
| `steer:431-445` `convertDistance()` | bad units | **silent** 0 (no `other` arm) |
| `steer:459-471` `convertRotationCount()` | bad units | **silent** -1, undocumented, where the motor object aborts on the same input (A10) |
| `steer:287`, `:330-343` limits | request rounds to 0 ticks | **silent**, as F-5 (`steer:978`) |
| `steer:152-153` `start()` | a `stopAfter*` set before `start()` | **silently erased** (F-5c) |

### 1.3 Public methods with no free values in their normal return range

These cannot carry an in-band error, so under this contract they signal only through the error
variable. None of them has a protective purpose, so none may abort. DERIVED.

- **`lib`:**
  - `getRawHallTicks()`: signed `pos`, full range (`lib:804`).
  - `getCurrent()`: signed `fAmps`/`fWatts` (`lib:766-767`).
  - `getRampingValues()`: whatever was set, unvalidated (`lib:479-486`).
  - `testGetTelemetry()`: signed duty/err/sense (`lib:1181-1188`).
  - `testGetResults()` (`lib:1125-1128`).
  - `getposTrkHallTicks()` (`lib:1821`).
  - `getDebugData()`: pointers.
- **`steer`:**
  - `getCurrent()`, `testGetRawHallTicks()` and `testLeft/RightGetTelemetry()`: mirrors of the above.
  - `getDistance()`/`getRotationCount()`: two data results, where 0 is legal.

**Values are free but the methods are data getters.** `getDistance()`/`getRotationCount()` never
return a negative value in `lib`, but the design still does not overload data returns with codes: the
knowledge base lists that as the `mixing_error_codes_and_data` anti-pattern (`p2kbSpin2Abort`). The
rest carry enums or booleans: `getPower()` [-100..100], `getStatus()`, `getDriverState()`,
`getBoardType()`, the `is*()` predicates and `valid*ForChoice()`.

### 1.4 Defects found while taking the inventory

All are DERIVED from source and not observed on hardware. Each is removed by the construction in §3;
they are listed so they are not re-derived, and each warrants a punch-list entry.

| ID | Defect | Evidence |
|---|---|---|
| **F-1** | **`valid*ForChoice` claims pins, and `start()` then `pinclear`s P0..P15 on a fresh instance.** `validBasePinForChoice()` calls `validatePinBase()`, which takes the AE claim keyed by `@pinbase` (`lib:985-990`, `:250-260`). `startEx()` sees `holdsPinBaseClaim()` and calls `stop()` (`lib:103-104`). A fresh instance's `pinbase` VAR is 0, not `VALUE_NOT_SET` (VAR is zeroed, `lib:1980`), so `stop()` passes its guard and runs `pinclear(0 addpins 7)` and `pinclear(8 addpins 7)` (`lib:149-155`). Its own comment assumes the claim is taken only by `init()`. **Shipped demos that validate first are exposed:** `demo_single_motor.spin2` starts HDMI on `PINS_P8_P15` (`:33`, `:55-57`), then validates (`:61`) and starts (`:68`). `demo_dual_motor_hdmi.spin2` and `demo_dual_motor_rc_hdmi.spin2` start HDMI on `PINS_P0_P7` (`:29`/`:36`), then validate through `steer`, which validates both bases on `ltWheel` (`steer:576-580`), then start. `PINCLEAR` zeroes the pin's smart-pin mode (PL-35 note, `p2kbSpin2Pinclear`). Whether the HDMI output is then lost depends on how `p2videodrv` uses those pins, which was not read: **UNVERIFIED on hardware**. | `lib:103-104`, `:149-155`, `:250-260`, `:985-990`; demos as cited |
| **F-2** | **A start that fails on its voltage keeps its pin claim with no cog.** `init()` claims at `lib:272`, then aborts at `lib:1376`/`:1422` from `lib:399`. The abort skips PL-36's release at `lib:118`. | `lib:272`, `:399`, `:1376`, `:1422`, `:109-118` |
| **F-3** | **`start()` with a non-legal base enum launches a driver cog anyway.** `validatePinBase()` returns `VALUE_NOT_SET` without aborting when the enum is not in the legal list (`lib:255-260`), `init()` stores it (`lib:272`), and `startEx()` calls `coginit` unconditionally (`lib:109`). The driver derives every pin from `pinbase = $FFFF_FFFF` (`lib:2812-2822`); which physical pins that addresses is UNVERIFIED, but none of them is claimed. Reachable by `start(99, …)`. The demos pre-validate and are not exposed. | `lib:109`, `:255-260`, `:272`, `:2812-2822` |
| **F-4** | **A rejected stop-limit call has already changed state.** `stopAfterRotation()` zeroes `motorStopHallTicks` before validating units (`lib:583` vs `:595`; `steer:281` vs `:293`), erasing a limit already armed. `steer:stopAfterDistance()` calls `resetTracking()` before validating units (`steer:316` vs `:346`). | as cited |
| **F-5** | **Stop limits that silently arm nothing.** (a) A distance or rotation that rounds to 0 ticks: for example `stopAfterRotation(3, DRU_DEGREES)` on the 6.5″ motor gives `3 / 4 = 0` (`lib:589`), and 0 means "no limit" (`lib:1795`, `steer:978`). (b) A single-motor limit with no sense cog running is never evaluated (the only evaluator is `lib:1790-1799`). (c) A steering limit set before `start()` is erased by `steer:152-153`. | as cited |
| **F-6** | **`SyncStatus()` can hang the application cog.** It busy-waits on the sync bit with no bound (`lib:1448`). The driver clears it only in `gettgtincr` (`lib:2973-2979`), which the e-stop path skips (`lib:2141-2148`). So `steer:driveAtPower()` hangs while a wheel is e-stopped, not started, or stopped. Today S-4's 250 ms auto-clear releases the e-stop case by accident. | as cited |
| **F-7** | **A host command can end the serial top level with the motors still driving.** `stopaftrot 0 …`, `stopaftdist 0 …` and `stopafttime 0 …` pass `isPostiveValue()` (0 is accepted, `serial:463-466`) and reach B1/B3/B6. Nothing traps, so the abort ends `main()` while the drivers hold the last command (study S-8). `sendOK()` has already been sent (`serial:278`, `:295`, `:312`). | as cited |
| **F-8** | **An illegal detection mode is silently replaced by `BRD_AUTO_DET`.** | `lib:1352`, `:1364-1369` |
| **F-9** | **The ABI guard only prints.** A mismatch still launches the driver (`lib:366-367`, `:109`). Separately, `CLAUDE.md`'s "14 longs … drive_u through drv_state" is stale: the status run is 16 longs, `drive_u..hall_illegal`, with `fault` after it (`lib:1963`, `:2002-2011`). | as cited |
| **F-13** | **A wheel abort inside `steer:start()` strands the other wheel** (§1.1, last paragraph). | `steer:119-133` |

---

## 2 · Invariants

Each is guaranteed by how the code is built, not by a test that might catch its violation. Where a
mechanical gate is proposed, it checks the *construction* (a lint over source text), not behaviour.

### I1 -- No failure is silent

**Every error condition either returns a distinct value or records an `ERR_*` code the caller can read.**

**Construction:**
1. **One recording path.** Every failure goes through `PRI recordError(eCode) : eCode` (§3.3), which
   writes the caller's slot and hands back the same code. A failing public method's exit is
   `return recordError(ERR_…)`. Record and return are one expression, so the two cannot diverge.
2. **Validate, then acquire, then commit.** Every public method checks all its inputs and
   preconditions before it touches state, pins or cogs (§3.5). A rejected call therefore has nothing
   to undo and cannot leave a half-changed object. This removes F-2, F-3 and F-4 by construction.
3. **Failing phases are placed before `init()`.** After validation, the pin claim and `coginit` are
   the only steps that can fail, so `init()` itself becomes infallible. No partial `init()` can exist.
4. **One source for each validated list.** The voltage validator and the power table read one lookup
   (§3.6), so "validated but not in the table" (A13, A14, A15, audit O) cannot be written.
5. **Every row of §1.2 is converted** (§3.4). The only exception is clamping, which is a documented
   saturation rather than a failure (Q4).
6. **Gate (lint, proposed for `tools/check_style.sh`):**
   - a `debug()` whose text begins `"!"` must share its block with a `recordError(` call;
   - no `abort` token appears outside the helper in I2.

### I2 -- No abort is bare, and no abort value is a normal return of its method

**Construction:**
1. **`abort` appears exactly once per library file**, inside `PRI abortIfProtectiveStop()` (§3.3). It
   reads the latch once into a local, aborts only when that local is non-zero, and aborts with that
   local. So the value is non-zero by the `if`, and cannot change between the test and the abort.
2. **The latch holds only protective codes.** It is written by `protectiveStop()` alone, which forces
   its argument into the protective range `-2_000..-2_099` (§3.7).
3. **Only energising methods call the helper**, and their normal return set is `{NO_ERROR} ∪
   ordinary codes`, which lie in `-1_001..-1_099` (§3.2). The two ranges are disjoint, so no abort
   value can equal a normal return.
4. **The helper is reached from no method whose normal returns could include a protective code.**
   `start`/`startEx`/`startSenseCog` keep {-1..7}; their codes, had they any, would lie outside -1..7
   by the same range argument. They do not abort.

### I3 -- An abort happens only on a protective path

**Construction:**
- The latch is set only by `protectiveStop()` (§3.7), and it **secures the motors before it latches**
  (e-stop and zero command first).
- The abort is raised only by energising calls, after the hardware is already safe.
- **No ordinary error aborts:** all 22 existing sites are converted (§3.4), and I2's single-`abort`
  lint keeps it so.
- **An uncaught protective abort ends the caller only after the motors are secured.** So the outcome
  of the UNVERIFIED "program terminates" is safe whatever it turns out to be.

### I4 -- Error state is per calling cog and cannot be clobbered by another cog's success

**Construction:**
1. **Single writer per slot.** `recordError()` writes only `lastError[COGID()]`; `getError()` reads and
   clears only `lastError[COGID()]`. No other code touches the array, so each slot's only writer is
   the cog whose index it is. No lock is needed.
2. **Success never writes.** `recordError()` ignores `NO_ERROR`, and only `getError()` zeroes a slot.
   So no cog's success, including the same cog's later success, can erase a recorded error.
3. **Sticky first.** A slot is written only when it holds `NO_ERROR`, so the first cause survives until
   it is collected.
4. **Library-owned cogs cannot leak a slot to a reused cog id.**
   - The sense tasks call only non-recording methods (§3.7), so their slots are never written.
   - Each sense task also clears its own slot at entry.
   - `stop()` clears the slot of any cog it stops.
   - The driver cog runs no Spin2, so it never writes.
5. **Application cogs, documented:** a cog should call `getError()` once at its own start to drain a
   slot a previous holder of its id left. This is the one residual that construction cannot close,
   because nothing tells the library that an application cog was restarted.
6. **The protective latch is instance-wide by intent.** It is a platform condition, not a call result,
   and is cleared only by an explicit `clearProtectiveStop()`, never by any call's success.

### I5 -- The error record cannot disturb the PASM ABI or the fault latch

**Construction:**
1. **Placement.** `lastError[8]` and `protectiveCode` go in a new VAR block placed textually after
   every ABI-bearing block (after `lib:2071-2073`, before `DAT { Motor DRIVER }` at `lib:2075`). No
   run is split or shifted, whatever the compiler's alignment rules (UNVERIFIED ordering, see header).
2. **Symbolic addressing only.** The new longs are named only by Spin2 symbols. The driver receives
   exactly two addresses, `@pinbase` (`lib:109`) and `@offset_fwd` (`lib:106`). It walks them by fixed
   offset (`lib:2812`, `:2824-2825`, `:2521-2522`, `:2543`, `:2556-2557`), never to the new block.
3. **Extended guard that refuses to launch.** The ABI guard is extended to all three runs, and to the
   new block's position, and it *refuses to launch* on any mismatch (§3.8). A layout that violated I5
   could not start a driver.
4. **The fault latch stays separate.** `fault` (`lib:2011`) is written by the driver (`lib:2543`) and
   cleared only by `clearFaultSignal()`/`testResetFault()`. No error helper reads or writes it, and no
   `ERR_*` code is derived from it. One value, one meaning.
5. **No new ABI write.** `protectiveStop()` writes `e_stop` and `targetIncre`, which
   `emergencyCutoff()`/`setTargetAccel()` already write (`lib:677-678`, `:1440`). That adds no new
   write *kind* to the ABI.

### I6 -- The securing path is unconditional

This one follows from I3 and is stated because the protective design depends on it.

**Construction:** `stop()`, `stopMotor()`, `stopMotors()`, `emergencyCutoff()` and `protectiveStop()`
never record, never abort and have no precondition. A cog can always secure the motors, even an
unstarted instance or one under a protective latch.

---

## 3 · Design

### 3.1 Vocabulary

| Term | Meaning |
|---|---|
| **Ordinary error** | a call could not do what it was asked; nothing is at risk. It is returned and/or recorded, and never aborts |
| **Protective condition** | continuing to drive risks the hardware or the surroundings (a blocked platform). The motors are secured where it is detected, a latch is set, and energising calls abort |
| **Energising method** | a call that commands torque. **`lib`:** `driveAtPower`, `driveAtPowerEx`, `driveForDistance`, `testDriveAtMotorIncrement`, `moveShaftToAngle`. **`steer`:** `driveDirection`, `driveAtPower`, `driveForDistance`, `testLeftDriveAtMotorIncrement`, `testRightDriveAtMotorIncrement` |
| **Securing method** | I6's list |

### 3.2 The `ERR_*` code set

All are declared in `lib` `CON { Public Interface Constants }` and mirrored in `steer` as
`ERR_X = ltWheel.ERR_X` (the pattern of `steer:13-84`, as `CLAUDE.md` requires).

**Why these numbers (DERIVED):**
- Every ordinary code is at most -1_001 and every protective code is at most -2_000, so all are
  disjoint from every existing public value domain:
  - `PINS_*` 0..40; `PWR_*` 0..9; `REV_*` 20..22; `BRD_*` 30..32;
  - `DDU/DRU/DTU_*` 0..7; `DS_*` 10..13; `DCS_*` 0..7; `SM_*` 0..2;
  - cog ids 0..7; the -1 sentinels; booleans 0/-1;
  - power and direction [-100..100].
- So no printed code can be mistaken for a legal value.

| Name | Value | Kind | Raised by (after conversion) |
|---|---|---|---|
| `NO_ERROR` | 0 | none | |
| `ERR_BAD_PIN_GROUP` | -1_001 | ordinary | `start`/`startEx`/`testSetup`: base not a legal `PINS_*` (was F-3) |
| `ERR_PIN_GROUP_IN_USE` | -1_002 | ordinary | the same: group overlaps another instance's claim (was A1) |
| `ERR_BAD_VOLTAGE` | -1_003 | ordinary | the same: voltage not in this motor's power table (was A12, A14) |
| `ERR_BAD_DETECT_MODE` | -1_004 | ordinary | the same: mode not `BRD_*` (was F-8) |
| `ERR_NO_FREE_COG` | -1_005 | ordinary | `startEx` (`lib:110`), `startSenseCog` (`lib:418`), `steer:start` sense cog (`steer:162`) |
| `ERR_ABI_MISMATCH` | -1_006 | ordinary | `startEx`/`testSetup` guard (was F-9) |
| `ERR_NOT_STARTED` | -1_007 | ordinary | an energising method or a `steer` stop limit on an instance with no running driver (was A11, part of B4, F-5c) |
| `ERR_NO_SENSE_TASK` | -1_008 | ordinary | `lib` `stopAfter*` with no sense cog to enforce the limit (F-5b) |
| `ERR_BAD_UNITS` | -1_009 | ordinary | A3, A6, A8, A9, A10, B2, B5, B7; `steer` convert* |
| `ERR_BAD_COUNT` | -1_010 | ordinary | value < 1: A2, A4, A7, B1, B3, B6 |
| `ERR_NO_WHEEL_DIA` | -1_011 | ordinary | A5, B4; `getDistance()` with diameter 0 |
| `ERR_LIMIT_UNRESOLVABLE` | -1_012 | ordinary | the request rounds to 0 ticks (F-5a) |
| `ERR_SYNC_TIMEOUT` | -1_013 | ordinary | `SyncStatus()` bound expired (F-6) |
| `ERR_BUSY` | -1_014 | ordinary | `moveShaftToAngle()` (TEST-USE, `lib:534`) |
| `ERR_FAULT_NOT_CLEARED` | -1_015 | ordinary | `testResetFault()` (TEST-USE, `lib:1155`) |
| `ERR_PROTECTIVE_STOP` | -2_000 | **protective** | `protectiveStop()` called with an out-of-range cause |
| `ERR_PLATFORM_BLOCKED` | -2_001 | **protective** | the blocked-platform detector (§3.7) |
| (reserved) | -2_002..-2_099 | protective | for the current-limit work (S-2/C-5) to name its own causes |
| `ERR_PROTECTIVE_FIRST` / `ERR_PROTECTIVE_LAST` | -2_000 / -2_099 | range bounds | used by `protectiveStop()` and by callers classifying a code |

`INVALID_*` (-1) and `VALUE_NOT_SET` (-1) are unchanged. They remain the documented results of
`valid*ForChoice()`. Codes are not reused for them.

### 3.3 Per-cog error storage and the two helpers

**`lib`: a new VAR block after `lib:2073`** (I5):

```spin2
VAR { error contract -- Spin2 only, never addressed by the PASM driver }
    LONG    lastError[8]        ' per calling cog, indexed by COGID(); sticky first error; 0 = NO_ERROR
    LONG    protectiveCode      ' instance-wide protective latch; 0 = none, else -2_000..-2_099
```

**`steer`:** `LONG lastError[8]` in a VAR block after `steer:911`. It has no protective latch of its
own: the wheels hold them. No ABI exists in `steer`.

```spin2
PRI recordError(eCode) : eSame
' the ONLY writer of lastError[]; records the first error for the calling cog, returns eCode unchanged
    if (eCode <> NO_ERROR) and (lastError[COGID()] == NO_ERROR)
        lastError[COGID()] := eCode
    eSame := eCode

PRI abortIfProtectiveStop() | eCode
' the ONLY `abort` in the file (I2); called first by every energising method
    eCode := protectiveCode                 ' read once: the value tested is the value aborted with
    if eCode <> NO_ERROR
        recordError(eCode)                  ' PL-47 rule 4: record before abort, same code
        abort eCode
```

**Read-and-clear, and precedence:**

```spin2
PUB getError() : eError
'' Return and clear this cog's first recorded error, NO_ERROR when none.
'' While a protective stop is latched its code is returned first and is NOT cleared by this call.
    eError := protectiveCode
    if eError == NO_ERROR
        eError := lastError[COGID()]
        lastError[COGID()] := NO_ERROR
```

**Decisions:**
- **Sticky first:** yes. The first cause is the causal one, and later codes are usually consequences.
- **Read-and-clear:** yes. The only consumer of a slot is its own cog, so read-and-clear cannot steal
  another cog's error (I4).
- **Non-clearing peek:** not provided. It would add a second way to consume a slot and nothing that
  read-and-clear plus a local copy cannot do. `getProtectiveStop()` is the non-clearing query for the
  one condition that must persist (§3.7).
- **Protective precedence in `getError()`:** so that a test or application that checks only
  `getError()` after each call cannot read a protective stop away (Q3).

### 3.4 How each abort and silent failure is converted

**Rule:** every existing abort becomes an ordinary error. None is kept as an abort, because none is
protective (§1.1).

| Was | Becomes |
|---|---|
| A1 `validatePinBase` overlap | `startEx`/`testSetup`: the claim is taken after validation, before `init()`. Refusal gives `return recordError(ERR_PIN_GROUP_IN_USE)`, and `start` returns -1. `validBasePinForChoice()` becomes a **pure check**: legal enum or `INVALID_PIN_BASE`, no claim (removes F-1; Q5) |
| F-3 illegal base | the same validation step: `ERR_BAD_PIN_GROUP`, -1, no cog launched |
| A12, A14 voltage; A13, A15 | one power-table lookup (§3.6). An illegal voltage is `ERR_BAD_VOLTAGE` at validation, before any claim (removes F-2). The unreachable branches cease to exist |
| F-8 detection mode | `ERR_BAD_DETECT_MODE` at validation; no silent substitution |
| F-9 ABI guard | `ERR_ABI_MISMATCH` at validation; no cog launched (§3.8) |
| `lib:110` coginit fail | `recordError(ERR_NO_FREE_COG)`, then the existing PL-36 `stop()`, then -1 |
| A2-A8 `stopAfter*` | gain a result `: eError` (Q1). Validate everything, including "sense task running" (`ERR_NO_SENSE_TASK`) and "resolves to at least one tick" (`ERR_LIMIT_UNRESOLVABLE`), then commit. The pre-clear at `lib:583` moves after validation (F-4) |
| B1-B7 `steer` `stopAfter*` | the same, plus "started" (`ERR_NOT_STARTED`), which splits B4. `resetTracking()` at `steer:316` moves after validation (F-4) |
| A9, A10 getters | `recordError(ERR_BAD_UNITS)` and return 0; wheel diameter 0 gives `ERR_NO_WHEEL_DIA` and 0. The data return is not overloaded (§1.3) |
| `steer` `convertDistance`/`convertRotationCount` | the same codes into `steer`'s slot; return 0, not a silent -1 |
| A11 `incrementForPower` | the abort is deleted. `driveAtPowerEx()` checks `motorCog <> 0` first and returns `ERR_NOT_STARTED`. With `init()` infallible (I1 item 3), `motorCog <> 0` implies `init()` completed, which implies `eUserSelectedVolts` is set (`lib:1426`). So the PRI can no longer be reached unconfigured (inference) |
| F-6 `SyncStatus` | `PUB SyncStatus() : eError`, bounded by `SYNC_TIMEOUT_MS = 50` (DERIVED: the driver polls ATN once per 500 µs pass, `lib:344`, `:2973-2979`, so 100 passes). On expiry: `ERR_SYNC_TIMEOUT` |
| `steer:driveAtPower` | two-phase: (1) `abortIfProtectiveStop()` over both wheels, then `senseCog <> 0` (else `ERR_NOT_STARTED`), then (2) command both. On either wheel's `ERR_SYNC_TIMEOUT` it calls `stopMotors()` (the platform must not pivot on one wheel, audit M) and returns the code |
| F-13 `steer:start` | inherits `startEx` returning -1 instead of aborting, so the existing cleanup at `steer:124-133` always runs; the failed wheel's code is readable per §3.5 |
| F-7 serial | no library abort remains to end `main()`; the serial migration is in §4 |
| `lib:534`, `lib:1155` TEST-USE | `: eError` with `ERR_BUSY` / `ERR_FAULT_NOT_CLEARED` |
| `clearEmergency()` under a protective latch | refuses and returns the latch code, **without aborting** (it energises nothing) |

### 3.5 Order inside `startEx()` (validate, acquire, commit)

1. **Validate, with no side effects:**
   - base enum legal (`ERR_BAD_PIN_GROUP`);
   - voltage in this motor's table (`ERR_BAD_VOLTAGE`);
   - detection mode (`ERR_BAD_DETECT_MODE`);
   - ABI guard (`ERR_ABI_MISMATCH`).

   Any failure returns -1 and **leaves a running motor running, unchanged.** A rejected call changes
   nothing.
2. **Free this instance's previous driver, sense cog and claim** (`stop()`, as PL-24 ruled). This now
   happens only for validated arguments.
3. **Acquire the pin claim** (`ERR_PIN_GROUP_IN_USE`, -1). No pin has been touched yet.
4. **`init()`.** It cannot fail any more.
5. **`coginit`** (`ERR_NO_FREE_COG`, then PL-36 `stop()`, then -1).

`testSetup()` runs steps 1-4 and returns `: eError`. The ruling-B contract of `start`/`startEx` is
kept: {0..7} on success, -1 on failure, with the cause in `getError()`.

**`steer` reports which wheel failed.** `getError() : eError, eLeftError, eRightError` (Q2):

```spin2
PUB getError() : eError, eLeftError, eRightError
'' Return and clear this cog's errors: the steering object's own first error, and each wheel's
    eLeftError := ltWheel.getError()
    eRightError := rtWheel.getError()
    eError := lastError[COGID()]
    lastError[COGID()] := NO_ERROR
    ' precedence: a protective code from either wheel, then steer's own, then left, then right
```

**Why the wheel slots are drained lazily here:**
- `ltWheel`/`rtWheel` are private to `steer`, so the application can reach their slots only through
  this call.
- A wheel slot is sticky-first and written only by this cog.
- So no wheel error is lost, and no per-method draining code is needed (inference).

### 3.6 One power-table lookup (removes A13, A14, A15)

`PRI powerTableIndex(eVoltage) : index` holds the one `lookdown` list per motor type (today's
`lib:1385` and `lib:1411`). Three places use it:
- `validVoltageForChoice()` is legal iff `index <> 0`.
- `confgurePowerLimits()` indexes the ceilings with the same `index`.
- `motorVoltage()` is called only with a validated enum.

The two lists can no longer disagree, so the "SHOULD NEVER get here" branches are deleted, not
converted.

**User-visible:** 6.5″ with `PWR_25p9V` now fails validation instead of passing it and then aborting
in `start()` (audit O). That is a release-note item.

### 3.7 The protective-abort path: blocked platform

**Where it is detected.** In the sense-task cog: `lib` `taskPostionSense()` (`lib:1764-1815`) for a
single motor, and `steer` `taskPostionSense()` (`steer:947-999`) for two. The log shows that cog, not
the application's, calling into the wheel instances: `Cog4 - STATE ltMot: dcsSPIN_UP` while `Cog0` is
the application (MEASURED, `DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:402-411`).

**Which cog secures the motors.** The detecting sense cog, at once, before anything else:

```spin2
PUB protectiveStop(eProtectiveCode)
'' SECURING: float the drive now and latch a protective stop until clearProtectiveStop()
    e_stop := TRUE                                        ' 1. secure: the driver floats the drive (lib:2141-2148)
    setTargetAccel(0, false)                              ' 2. discard any command, clear any sync bit
    if (eProtectiveCode > ERR_PROTECTIVE_FIRST) or (eProtectiveCode < ERR_PROTECTIVE_LAST)
        eProtectiveCode := ERR_PROTECTIVE_STOP            ' the latch holds only protective codes (I2)
    if protectiveCode == NO_ERROR
        protectiveCode := eProtectiveCode                 ' 3. signal last; first cause sticks
```

**In `steer`:**
- `steer:protectiveStop()` calls both wheels' `protectiveStop()`. A cause on either wheel secures both:
  a two-wheel platform driving one wheel pivots (audit M's failure scenario; inference).
- The steering sense task's detector calls `steer:protectiveStop(ERR_PLATFORM_BLOCKED)`.

**How the application's cog learns of it.** Three ways:
1. **Its next energising call aborts** with the code (`abortIfProtectiveStop()` first, in `lib` and,
   over both wheels, in `steer`), caught by its one top-level trap. The code is also recorded in its
   slot.
2. **`getError()` returns the code** with precedence, and does not clear the latch.
3. **`getProtectiveStop() : eCode`** gives a side-effect-free read. `steer` returns
   `eLeftCode, eRightCode`.

**Acknowledgement.**

```spin2
PUB clearProtectiveStop() : eError
'' Acknowledge a protective stop: the motor stays stopped and may be commanded again
    setTargetAccel(0, false)                              ' a command written while latched must not resume motion
    protectiveCode := NO_ERROR
    e_stop := FALSE
```

The command is zeroed first. So a `driveAtPower()` that passed its latch check just before the latch
was set, and wrote while the drive was floated, cannot come back to life when the e-stop is released
(inference from `lib:2141-2152`: the driver ignores `targetIncre` while `e_stop` is set and reads it
on the next pass after).

**Required gating in the same change:** both sense tasks' e-stop auto-clear (`lib:1804-1807`,
`steer:989-992`; study S-4) must not clear while a latch is set. Otherwise the library itself would
release a protective stop in 250 ms. This design only gates it on the latch; S-4's own redesign stays
out of scope.

**Invariants on this path:**
- The sense tasks call no energising method, so they never reach the abort helper and cannot abort
  themselves (I3).
- They call no recording method, so their slots stay clean (I4).
- `getProtectiveStop()` and `protectiveStop()` are the only new calls in them.

**Coordinated with, not designed here: the current-limit work (S-2/C-5).** The design fixes only the
interface the detector plugs into:
- `PRI blockedCondition() : eProtectiveCode`, returning `NO_ERROR` or a code in `-2_001..-2_099`;
- evaluated each 8 Hz sense pass;
- in `steer`, over both wheels.

**Out of scope, and why:**

| Out of scope | Reason / owner |
|---|---|
| The criterion itself (current threshold, "at speed", persistence) | S-2/C-5 |
| The PASM-level current fold-back and lag-limited ramp | study §I.11 Tier 0, C-5. They act in microseconds inside the driver; this path is the supervisory stop at 125 ms granularity |
| The sense zero offset | PL-45 |
| Post-fault stop mode | S-9a |
| The fault taxonomy bitfield | study Tier 1; would change the meaning of `fault`, which this contract keeps separate |
| Status-enum widening | audit M/AF |
| The 3-second fault-latch erasure | S-5 |
| A `getfaults` serial command | S-6 |
| The command watchdog | S-8 |

**Precondition, documented:** supervisory protection exists only while a sense task runs:
`startSenseCog()` for one motor, and always for `steer` after `start()`.

### 3.8 Extended ABI guard (I5)

This runs in `startEx()`/`testSetup()` step 1 and refuses with `ERR_ABI_MISMATCH`. The layout facts
are DERIVED from `lib:1978-2073` and the PASM walk cited in I5.

- `(@drive_u - @pinbase) == 4 * 4`: the launch block is pinbase, params_ptr, targetAngle, targetIncre.
- `(@fault - @drive_u) == DRVR_STATUS_LONGS_COUNT * 4`: today's check (`lib:366`).
- `(@ramp_inc - @offset_fwd) == (DRVR_PARAMS_LONGS_COUNT - 1) * 4`
- `@lastError` and `@protectiveCode` each lie outside both `@pinbase..@fault` and
  `@offset_fwd..@ramp_inc`.

### 3.9 Public API additions and documentation

**`isp_bldc_motor.spin2`, mirrored where marked (M):**

| Addition / change | `@returns` text |
|---|---|
| CON `NO_ERROR`, all `ERR_*`, `ERR_PROTECTIVE_FIRST/LAST` (M) | |
| `PUB getError() : eError` (M: `steer` returns 3) | `eError - this cog's first error since the last call (NO_ERROR when none), cleared by this call; an active protective stop's code is returned first and is not cleared` |
| `PUB getProtectiveStop() : eProtectiveCode` (M: 2 results) | `eProtectiveCode - the active protective stop's cause, NO_ERROR when none; no side effects` |
| `PUB protectiveStop(eProtectiveCode)` (M) | none; `@param eProtectiveCode - ERR_PLATFORM_BLOCKED or another -2_0xx cause; any other value latches ERR_PROTECTIVE_STOP` |
| `PUB clearProtectiveStop() : eError` (M) | `eError - NO_ERROR` |
| `: eError` added to `stopAfterRotation`, `stopAfterDistance`, `stopAfterTime`, `driveForDistance`, `driveAtPower`, `driveAtPowerEx`, `clearEmergency`, `SyncStatus`, and TEST-USE `testSetup`, `testDriveAtMotorIncrement`, `moveShaftToAngle`, `testResetFault` (M for the `steer` equivalents, including `driveDirection`) | `eError - NO_ERROR, or the ERR_* code also recorded for getError()`, plus, on energising methods, `ABORTS with a -2_0xx code while a protective stop is latched` |
| `start`/`startEx`/`startSenseCog`/`steer:start` | unchanged `@returns`, plus `the cause of a -1 is in getError()` |
| `getDistance`/`getRotationCount` (both objects) | add `returns 0 and records ERR_BAD_UNITS / ERR_NO_WHEEL_DIA on a bad request` |
| `validBasePinForChoice` | `legalBasePin or INVALID_PIN_BASE; no side effects (overlap is reported by start())` |

**`DRIVE-OBJECTS.md` changes:**
1. A new section, **"Errors and protective stops"**, placed before both interface tables. It covers:
   - the code table;
   - the per-cog `getError()` rule;
   - "drain at cog start";
   - the protective latch lifecycle;
   - the recommended shape: normal calls, check `getError()`, and one top-level `\` trap that
     secures and reports.
2. **Table rows:**
   - add the five new methods to **STATUS/CONTROL** in both tables;
   - add `: eError` to the changed signatures;
   - delete every "Will ABORT" note (source `lib:574`, `:600`, `:637`, `steer:270`, `:302`, `:354`)
     and replace it with the error code.
3. **Existing errors, fixed in the same pass:**
   - `start(...)` rows lack the detection-mode parameters (`DRIVE-OBJECTS.md:57`, `:104`) and state no
     return;
   - NOTE4/NOTE5 list stale enums (`:79-81`, `:130-132`).
4. **Also to change:** `DRIVE-OBJECTS-SERIAL.md` and `SERIAL-CONTROL.md` if they describe error replies
   (not read in this phase).

---

## 4 · Migration

**Source compatibility (DERIVED):**
- No public method is removed or renamed, and no parameter changes.
- Adding a result to a method its callers use as a statement leaves those calls valid. In-tree
  evidence: `demo_dual_motor.spin2:53` already calls `wheels.start(...)`, which has a result, as a
  statement, and that demo is release-certified by `tools/build-check.sh`. Knowledge-base support for
  discarding a result is **UNVERIFIED**.
- **So no caller needs an edit to compile. What changes is behaviour at the sites below.**

**Behaviour changes a caller can see** (release notes, «#3515»):
1. Bad arguments no longer abort. The call returns or records an `ERR_*` code, and a stop-limit call
   that fails leaves the prior limit untouched.
2. `validBasePinForChoice()` no longer claims pins or detects overlap; `start()` reports overlap.
3. 6.5″ + `PWR_25p9V` is rejected at validation.
4. An illegal detection mode is rejected, not replaced by auto-detect.
5. Motion on an unstarted instance does nothing and returns `ERR_NOT_STARTED`.
6. Limits that round to 0 ticks, or have no sense task to enforce them, are rejected.
7. `steer:driveAtPower()` returns `ERR_SYNC_TIMEOUT` instead of hanging, with both wheels stopped.
8. Energising calls abort with a -2_0xx code while a protective stop is latched.
9. `steer:getRotationCount()` with bad units returns 0 and a code, where it returned -1.

**Demos and the serial top level** (deliverables, changed in phase 2 to show the contract):

| File | Call sites | Change |
|---|---|---|
| `demo_single_motor.spin2` | `:61-64` validate; `:68` `start` (return ignored); `:72` `startSenseCog` (ignored); `:89`, `:95` `stopAfterTime`; `:90`, `:94` `driveAtPower` | check `start`/`startSenseCog` and `getError()`; one top-level trap around the drive sequence that calls `wheel.stop()`. `:94-95` drives before arming its limit; reorder to limit-then-drive. F-1 no longer applies once validation is pure |
| `demo_dual_motor.spin2` | `:42-47`; `:53` `start` (ignored); `:63` `driveForDistance`; `:67`, `:72`, `:79`, `:85` `drive*`; `:68`, `:73`, `:80`, `:86` `stopAfterTime` | the same pattern; `getError()` shows which wheel |
| `demo_dual_motor_hdmi.spin2` | `:57-62`; `:68`; `:95` `driveAtPower`; `:96` `stopAfterTime` (the others at `:81-92` and `:100-106` are in block comments) | the same; F-1 exposure (HDMI on P0..P7) removed by the pure validator |
| `demo_dual_motor_rc.spin2` | `:55-60`; `:66`; `:235` `setAcceleration`; `:243`, `:249`, `:271` `driveDirection`; `:270`, `:274`, `:277` `getRotationCount`; `:273` `stopAfterRotation` | the RC loop gains a trap that secures on a protective abort and waits for SwD. `doOneRotation()` checks the limit's result before relying on it |
| `demo_dual_motor_rc_hdmi.spin2` | `:77-82`; `:91`; `:282`; `:290`, `:296`, `:318`; `:317`, `:321`, `:324`; `:320` | as `demo_dual_motor_rc` |
| `isp_steering_serial.spin2` | `:141-146`; `:152` `start` (ignored); `:222`, `:244`, `:262` drive; `:279`, `:296`, `:313` `stopAfter*`; `:402`, `:417` getters | **call first, then reply**: `sendOK()` on `NO_ERROR`, else `sendError()` with the code's name (F-7). `isPostiveValue()` becomes "≥ 1" for counts. A top-level trap around `processCommand()` sends the protective code to the host and keeps the loop alive. Check `start()` before `hostIF.startx` |

**Bench binaries: sites only; the changes are «#3539».** «#3539» also owns the full inventory of every
`test_bench_*` / `util_*` / `test_*` file. Only `t0` was read end to end here; `char` and `scan` were
read at the sites PL-44's study cites; `test_bench_detect.spin2`, `test_bench_spin.spin2` and the other
`test_*`/`util_*` tops were not read.

| File | Sites |
|---|---|
| `t0` | **Per-test traps in `main()`:** `:240`, `:257-263`, `:268-269`, `:273-275`, `:279-281`, `:289-290`, `:295`. **Value-capturing traps:** `:324`, `:349`, `:436`, `:478`, `:481`, `:484`, `:487`, `:515-516`, `:527`, `:813`, `:1017`, `:1131`. **Statement traps:** `:820`, `:827`. **Completion-flag wrappers:** `startTrapped` `:1036-1057`, `setupTrapped` `:1059-1082`, `stopDistanceTrapped` `:1084-1108`, VAR `:177-210`. **Guards accepting a stuck 0:** `:621`, `:685`, `:942`. **Header comments that describe the abort contract:** `:58-83`, `:1000-1006`, `:160`. **Tests whose verdict relied on an abort happening:** T0-6 `:464-488`, T0-7 `:490-528` (overlap now returns `ERR_PIN_GROUP_IN_USE` from `testSetup`), T0-3 `:355-415` |
| `char` | top-level `\runSession()` `:893`, printed only on abort `:2556`; `steerStartTrapped` `:1949-1969` (trap `:1957`), called at `:1883`, `:1899`; `steerDriveTrapped` `:1971-1984` (trap `:1981`, abort misreport `:1982`), called at `:1909`; `brakeStartTrapped` `:2240-2265` (trap `:2249`), called at `:1941`, `:1944`, `:2209`; masked PL-36 check `:1887-1893`; guard `:2212-2213` |
| `scan` | top-level `\runScan()` `:1186`, value used only on abort `:1187-1188` |
| `test_bench_detect.spin2` | a trapped `start()` capture exists (`start_ret 0`, `DOCs/analyses/bench/2026-09-12/DETECT-A-EVALUATION.md` §6); site not located in this phase |

---

## 5 · Open questions for the owner

Only public API names and shape. Everything else above follows from the rules or the code.

**Arbiter review (2026-09-14): three of the five retired, two go to the owner.** The project rule is
that a defect with only one correct remedy gets fixed, not parked as the owner's choice (overlay P3).
- **Q2 is retired: three results.** The two-result form loses one wheel's code whenever the wheels
  fail differently, which breaks I1. Only one form is correct.
- **Q4 is retired: saturation stays.** Clamping to [-100..100] is existing documented behaviour
  (`CLAUDE.md` Conventions), so keeping it changes nothing, and a sticky clamp code would mask the
  real error behind it. Phase 2 documents it in `DRIVE-OBJECTS.md`.
- **Q5 is retired: the validator becomes a pure check.** The method's own doc says it only validates,
  and taking a claim inside it causes F-1, now filed as PL-48.
- **Q1 and Q3 go to the owner:** they choose public signatures and names, where more than one answer
  is correct.

The original five, kept for the record:

1. **Add a result to methods that return nothing today?** The affected methods are `stopAfter*`,
   `drive*`, `clearEmergency`, `SyncStatus` and the TEST-USE setters, which would each gain
   `: eError` alongside the per-cog variable.
   **Recommend yes:**
   - their result set is empty today, so the code cannot collide with anything;
   - the call site learns of the failure without a second call;
   - existing statement calls still compile.
   **The alternative:** the variable only, which keeps every signature but makes every caller issue a
   second `getError()` call.
2. **Steering error shape:** `getError() : eError, eLeftError, eRightError`, or
   `getError() : eError, eWheel` (a `WHEEL_NONE/LEFT/RIGHT/BOTH` enum).
   **Recommend three results:** the two-result form loses the second wheel's code when the wheels fail
   differently, which breaks I1.
3. **Protective API names and `getError()` precedence.** The proposed names are `protectiveStop()`,
   `clearProtectiveStop()` and `getProtectiveStop()`, with `getError()` returning an active
   protective code first and not clearing it.
   **Recommend these names and that precedence:** a protective stop must not be readable away by a
   test loop that checks only `getError()`. The acknowledgement is the one deliberate act that
   releases it.
4. **Clamping of out-of-range power, direction and speed** (`lib:492-494`, `:502-504`, `:561-563`):
   keep it as documented saturation (no code), or record an ordinary `ERR_VALUE_CLAMPED`?
   **Recommend saturation, documented in `DRIVE-OBJECTS.md`:** a clamp recorded as a sticky first
   error would mask the real error that follows it. The RC and serial front ends already bound their
   inputs (`serial:211-218`).
5. **Make `validBasePinForChoice()` a pure check**, so overlap is reported only by `start()`
   (`ERR_PIN_GROUP_IN_USE`)?
   **Recommend yes:**
   - a validator that takes a claim is F-1's cause;
   - through `steer` it already validates both bases on one instance, so the second call releases the
     first claim (`lib:221`), and it cannot detect a left/right overlap anyway (`steer:576-580`).

---

## 6 · What phase 2 will change

| File | Change |
|---|---|
| `src/isp_bldc_motor.spin2` | `ERR_*` CON; the new VAR block after `:2073`; `recordError`/`abortIfProtectiveStop`/`getError`/`getProtectiveStop`/`protectiveStop`/`clearProtectiveStop`; `startEx`/`testSetup` validate-acquire-commit with the extended ABI guard; `powerTableIndex` shared by `validVoltageForChoice`/`confgurePowerLimits`/`motorVoltage`; pure `validBasePinForChoice`; every conversion in §3.4; bounded `SyncStatus`; the sense task gains the `blockedCondition()` hook (returning `NO_ERROR` until S-2/C-5 supplies it), the latch-gated e-stop auto-clear, and slot clearing at entry; `stop()` clears stopped cogs' slots; no `abort` outside the helper. The PASM `DAT` is **not** touched |
| `src/isp_steering_2wheel.spin2` | `ERR_*` CON aliases; `lastError[8]`; three-result `getError`; protective pass-throughs over both wheels; two-phase energising methods; conversions B1-B7 and convert*; the sense-task hook and gating |
| `src/isp_steering_serial.spin2` | call-then-reply with error names; count validation at least 1; top-level trap around `processCommand()` |
| `src/demo_single_motor.spin2`, `src/demo_dual_motor.spin2`, `src/demo_dual_motor_hdmi.spin2`, `src/demo_dual_motor_rc.spin2`, `src/demo_dual_motor_rc_hdmi.spin2` | adopt the contract: check returns/`getError()`, one top-level trap that secures; reorder limit-before-drive (`demo_single_motor.spin2:94-95`) |
| `DRIVE-OBJECTS.md` | §3.9 |
| `DRIVE-OBJECTS-SERIAL.md`, `SERIAL-CONTROL.md` | error replies, if described there (to check) |
| `README.md` | "Latest Changes": §4's behaviour changes; "Known Issues" unchanged |
| `ADDING_MOTOR.md` | check whether its power-table step must name the single `powerTableIndex` list (not read in this phase) |
| `isp_bldc_motor.txt` | regenerate (tracked interface report) |
| `CLAUDE.md` | the ABI paragraph: status run is 16 longs `drive_u..hall_illegal` (F-9); one paragraph on the error contract and the single-`abort` rule |
| `tools/check_style.sh` | the two construction lints in I1/I2 |
| `DOCs/PUNCH-LIST.md` | PL-47 updated to this design. Filed in phase 1: F-1 as PL-48, and the others (F-2 to F-9, F-13) as PL-49. Phase 2 marks them fixed |
| `test_bench_*.spin2` | **not phase 2**: «#3539», per §4 |

Gates for phase 2:
- `tools/build-check.sh` (both release demos certified);
- `tools/check_style.sh` with the new lints.

The run-time proofs owed to a bench visit are for «#3539» to declare as sign-off cells, not for this
design to assume:
- a protective abort observed at the application's trap after the sense cog secured;
- `getError()` per cog under two calling cogs;
- `ERR_PIN_GROUP_IN_USE` from `start()`.
