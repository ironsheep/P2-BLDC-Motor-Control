# Front cog: implementation plan (R16.3, phase 1)

**Date:** 2026-09-16
**Status:** APPROVED WITH AMENDMENTS (arbiter review, 2026-09-16). No source file was changed in this phase.

> **ARBITER REVIEW, 2026-09-16. Where the body below disagrees, this block governs.**
>
> **A1 · `startEx()`'s `sync` keeps one meaning (doctrine D7: one value, one meaning).** The body makes
> `sync = TRUE` mean both "the driver waits for a release" and "this instance is owned and starts no front cog, so its
> commands refuse". That silently changes a documented public parameter into an ownership switch.
> - **Owned start is its own method:** `PUB startOwned(eMotorBasePin, eMotorVoltage, eDetectionMode) : ok`, marked
>   INTERNAL USE (for an owner such as `isp_steering_2wheel`, the precedent of `hallTicInfoForMotor()`). It runs
>   `setupForStart()`, launches the driver parked for its owner's ATN, starts no front cog, and returns the driver's
>   cog id or -1. `steer:start()` calls it for both wheels. The lockstep is unchanged: one `cogatn(cogmask)` on the
>   caller before the steering front cog exists.
> - **`startEx(..., sync)` always starts the front cog.** `sync = TRUE` still means the driver starts parked, and the
>   front cog's entry releases it with one `cogatn` to its own driver. The front cog stays the only caller of
>   `cogatn` for a standalone motor. `start()` is `startEx(..., FALSE)`, as today.
> - This departs from the task body's wording "startEx(..., sync: true)" for the lockstep call. The mechanism the body
>   requires (both drivers parked, one ATN before the front cog exists) is kept exactly. Only the method that parks
>   them changes, so that `sync` keeps its one meaning.
> - Section 7.3's check for "`startEx(..., TRUE)` on a standalone motor" is dropped, because that call keeps working.
>
> **A2 · The two new codes are decided, not asked.** `ERR_EMERGENCY_STOPPED = -1_016` and `ERR_NO_RESPONSE = -1_017`,
> as proposed, mirrored in `steer`, and added to the serial `errorName()` table. The contract's names were ruled by
> Stephen only where two shapes were each correct (ABORT design §5, Q1/Q3). The `ERR_*` names of §3.2 were set by the
> design without a question, and these follow that precedent. Section 8 is therefore closed.
>
> **Section 9 facts, checked against p2kb-mcp by the arbiter:**
> - **F1 VERIFIED** (`p2kbSpin2Cogatn`): the attention flag is cleared when polled or waited, and signals merge
>   without queueing.
> - **F3 VERIFIED as written** (`p2kbSpin2Waitct`): `WAITCT` "blocks execution until system counter matches Tick".
>   So the mandatory late test (3.4) stands.
> - **F5 VERIFIED in part** (`p2kbSpin2Cogspin`): -1 on failure. Stack need per frame is not stated, so 128 longs and
>   the high-water observation (3.7) stand.
> - **F2, F4, F6-F15:** not stated by p2kb in the entries read. The plan already avoids depending on F6 (it parks) and
>   F9 (the guard refuses). The rest are the assumptions the shipped library already rests on for shared VAR between
>   cogs, and they stay marked as assumptions.
>
> **The 3.4 "~16 s stall" finding is recorded, not asserted.** It follows from F3 as derived. But «#3556»'s recorded
> unfixed value, an e-stop auto-clear at ~125 ms, could not occur under a 16 s stall, and a recorded measurement
> outranks a derivation (doctrine overlay P8). Filed as PL-72 with that contradiction stated. The front cog removes
> the construct either way.
>
> Everything else is approved as written.
**Governs:** `src/isp_bldc_motor.spin2` (used standalone) and `src/isp_steering_2wheel.spin2`. No roster owner, N-motor
API, `demo_n_motor`, `nmotor` config block or gate classifier change.
**Built on:**
- `FIXED-COG-SHAPE-DESIGN.md` with its 2026-09-16 amendment block, which governs;
- `ABORT-ERROR-CONTRACT-DESIGN.md` with its 2026-09-16 amendment, and invariants I1-I6;
- the committed error contract (a128782, 4e07f89). It was read in the tree, not taken from the designs.

**Provenance tags:** DERIVED means read from source or inferred from it, and "(inference)" marks an inference.
UNVERIFIED means a P2/Spin2 fact the plan depends on that was not checked against p2kb in this phase (no p2kb access).
Every such fact is listed in section 9.

**Line references:** `lib` = `src/isp_bldc_motor.spin2` and `steer` = `src/isp_steering_2wheel.spin2`, both at 4e07f89.

---

## 0. Decisions in one screen

1. **Ownership.** The existing `senseCog` becomes the front cog, in both objects, keeping its name. Stephen's
   words make it *"the sense cog is the owner"*. The front cog is the only writer of `targetIncre`, `e_stop`,
   `motorStopHallTicks`, `motorStopMSecs`, `posTrkHallTicks` and the tracking window. It is also the only caller of
   `cogatn` and of the sync wait, with two exceptions, both named in section 7.1: pre-launch initialisation, and
   the lockstep `cogatn` sent before the front cog exists.
2. **Request protocol.** Each calling cog has one slot, indexed by `COGID()`. The caller withdraws, writes the
   arguments, then publishes by writing a fresh sequence number last. The front cog copies the request and re-reads
   the sequence before applying it, then writes the status and then the acknowledgement. No lock is used.
3. **Statuses travel as data.** The front cog never calls `recordError()`: it writes a status long, and the calling
   cog records and returns it unchanged. A wheel's code reaches the wheel's own slot for the calling cog through a new
   INTERNAL-USE `recordCallerError()` on the motor object.
4. **Loop.** 1 ms on an absolute `getct()` schedule. Each pass applies requests, updates tracking, then checks limits,
   so a limit stop is written in the same pass it is seen. A pass that overruns is counted and re-anchored, and is
   never caught up.
5. **Synchronized drive, in the pass.** The front cog writes each selected motor's command with the sync bit, sends
   one `cogatn`, and waits in the pass, bounded to 4 drive passes (~2.1 ms), with at most one such wait per pass.
   This departs from the design's 20 passes; section 3.6 gives the reason.
6. **E-stop latches.** Nothing clears it except a `clearEmergency()` request. A drive is refused with the new
   `ERR_EMERGENCY_STOPPED` while `e_stop` is set or any selected driver reads `DCS_ESTOP`.
7. **Cog cost.** `start()` gives a single motor a driver cog plus a front cog (2). `isp_steering_2wheel` has two
   owned drivers plus one front cog (3). `startEx(..., sync: TRUE)` means *owned*: the driver is parked for its
   owner's ATN, and the instance starts no front cog of its own.
8. **`startSenseCog()` is kept.** It starts nothing, and returns the front cog id that `start()` launched, or -1 with
   `ERR_NOT_STARTED`. The API rule decides this (section 4.2).
9. **Shutdown is cooperative.** `stop()` posts EXIT. The front cog answers every other open request, acknowledges
   EXIT, and parks with no output. Only then does the caller `cogstop` it and the drivers. The wait is bounded.
10. **PASM untouched.** No line of the PASM `DAT` and no declaration in the PASM-addressed VAR runs changes. The new
    slots are a new VAR block after `lastError`. The extended ABI guard gains a check for each new or resized array.

---

## 1. The request/ack protocol

### 1.1 Slot layout

This is a new VAR block in each object. In `lib` it goes after `VAR { error record }` (`lib:2402-2405`), before
`DAT { Motor DRIVER }`. In `steer` it goes after `VAR { error record }` (`steer:994-995`).

```spin2
CON { front cog requests }
    SEQ_IDLE        = 0             ' reqSeq value meaning "no request outstanding"
    OWNED_MOTOR_MAX = 1             ' lib: 1; steer: 2 (left = index 0, right = index 1); a roster: 3

VAR { front cog request slots -- Spin2 only, never addressed by the PASM driver }
    LONG    reqCmd[COG_SLOT_COUNT]          ' caller-written: REQ_* code
    LONG    reqMask[COG_SLOT_COUNT]         ' caller-written: owned-motor selector, bit i = motor i
    LONG    reqArg1[COG_SLOT_COUNT]         ' caller-written: arguments, meaning per REQ_* (section 2.3)
    LONG    reqArg2[COG_SLOT_COUNT]
    LONG    reqArg3[COG_SLOT_COUNT]
    LONG    reqNextSeq[COG_SLOT_COUNT]      ' caller-written: this cog's own counter, never SEQ_IDLE
    LONG    reqSeq[COG_SLOT_COUNT]          ' caller-written LAST: SEQ_IDLE, or the published sequence
    LONG    ackStatus[COG_SLOT_COUNT]       ' front-written FIRST: NO_ERROR or ERR_* for the platform/object
    LONG    ackMotorStatus[COG_SLOT_COUNT * OWNED_MOTOR_MAX] ' front-written: per owned motor (steer only)
    LONG    ackSeq[COG_SLOT_COUNT]          ' front-written LAST: the sequence it answered
    LONG    frontPasses                     ' front-written heartbeat (zeroed by start before launch)
    LONG    frontLatePasses                 ' front-written: passes that overran their slot
    LONG    frontMaxPassTicks               ' front-written: longest pass body, in ticks
```

`lib` has one motor, so `ackStatus` carries its whole result and `ackMotorStatus` is omitted there. `steer` declares
`ackMotorStatus[COG_SLOT_COUNT * 2]`. In `steer`, `COG_SLOT_COUNT` is referenced as `ltWheel.COG_SLOT_COUNT`
(guide §2.4).

### 1.2 Single writer of every long (why no lock is needed)

| Long | Only writer | Readers |
|---|---|---|
| `reqCmd/reqMask/reqArg1-3/reqNextSeq/reqSeq [c]` | the cog whose `COGID()` is `c`, inside the post helper | front cog |
| `ackStatus[c]`, `ackMotorStatus[c*M+i]`, `ackSeq[c]` | the front cog | cog `c`, inside the post helper |
| `frontPasses`, `frontLatePasses`, `frontMaxPassTicks` | the front cog. `start()` zeroes them before the launch, when no front cog exists | `start()`'s handshake, TEST-USE getter |

Two facts together remove any need for a lock. First, every long has exactly one writer. Second, every
multi-long exchange is made safe by the write order in 1.3 and 1.4, without any mutual exclusion. None is allocated,
so none can leak (PL-41). This rests on one fact: a hub long read by one cog never shows a torn write from another
(UNVERIFIED, section 9 fact F10).

### 1.3 Caller side: `PRI postRequest(eCmd, motorMask, arg1, arg2, arg3) : eStatus`

Order of operations, on the calling cog:

1. **Withdraw:** `reqSeq[c] := SEQ_IDLE`. After this, the front cog can no longer apply any earlier request from this
   slot (see 1.4 step 3).
2. **Write the request:** `reqCmd[c]`, `reqMask[c]`, `reqArg1..3[c]`.
3. **Pick a fresh sequence:** `reqNextSeq[c] += 1`, skipping `SEQ_IDLE` on wrap. The sequence is monotonic, so it can
   never equal a stale `ackSeq[c]`.
4. **Publish, last:** `reqSeq[c] := reqNextSeq[c]`.
5. **Wait, bounded:** poll `ackSeq[c] == mySeq`, `waitms(1)` between polls, until `REQ_ACK_TIMEOUT_MS` (= 20, as the
   design sets it; section 3.6 derives it) has passed on a `getct()` deadline.
   - **Acknowledged:** `eStatus := ackStatus[c]`, then the per-motor statuses. `ackStatus` was written before
     `ackSeq`, so the value read belongs to this sequence.
   - **Timed out:** withdraw (`reqSeq[c] := SEQ_IDLE`). Then `eStatus := ERR_NOT_STARTED` if `senseCog == 0` by now
     (the front cog was stopped while this cog waited), otherwise `ERR_NO_RESPONSE`. Section 3.6 makes the second
     case unreachable while a front cog runs. It is documented as "outcome unknown", because the front cog may have
     taken the request in the instant before the withdraw.

**Precondition, checked before posting:** `senseCog == 0` gives `ERR_NOT_STARTED` at once, with no post and no wait.
This is the design's "if the front cog is not running, the request is dropped and the method returns at once".

`postRequest` never calls `recordError()`. The public method records, so the one-expression rule
`eError := recordError(eStatus)` (I1 item 1) stays at the public exit. Securing methods do not record (I6).

### 1.4 Front side: taking and answering a slot

This runs once per pass, for `c` from 0 to `COG_SLOT_COUNT - 1`:

1. `seqTaken := reqSeq[c]`. If it is `SEQ_IDLE` or equals `ackSeq[c]`, the slot is empty.
2. Copy `reqCmd/reqMask/reqArg1..3[c]` into locals.
3. **Re-read `reqSeq[c]`.** If it no longer equals `seqTaken`, the caller withdrew while the copy was being made, so
   the copy is discarded and nothing is answered. Why this is sufficient (DERIVED): the caller writes arguments only
   after its withdraw.
   - If the re-read ran before the withdraw, every copy ran before the withdraw, so the copy is one whole request.
   - If the re-read ran after the withdraw, the check fails.
   - The sequence never returns to `seqTaken` (1.3 step 3), so an ABA match is impossible.
4. Apply the copy (section 2.3), giving `eStatus` and, in `steer`, per-motor statuses.
5. **Answer:** write `ackMotorStatus[...]`, then `ackStatus[c] := eStatus`, then `ackSeq[c] := seqTaken`.

**Order within a pass:** a first sweep over the eight slots records which are open, then they are applied by class.
- **(A) securing:** `REQ_ESTOP`, then `REQ_STOP`;
- **(B) everything else**, in slot order;
- **(C) `REQ_EXIT`** last.

So an e-stop and a drive posted in the same pass always resolve with the e-stop first, and the drive is refused
(DERIVED from the class order). Requests from one cog still apply in order, because a cog has one slot and waits for
its answer.

### 1.5 Sequence handling and what a timeout means

- One outstanding request per cog. The cog is blocked in `postRequest` until the request is answered or has timed
  out and been withdrawn.
- **Residual, documented:** two Spin2 tasks on one cog share a `COGID()`, so they share a slot. Concurrent library
  calls from two tasks on one cog are not supported. The error slots have the same limit today (I4). This depends on
  fact F8.
- A request answered after its caller timed out writes `ackSeq`/`ackStatus` for a sequence nobody waits on. The next
  post from that cog waits for its own, higher, sequence and ignores the stale answer.

---

## 2. Every public method

### 2.1 Categories

| Category | Meaning |
|---|---|
| **READ** | reads hub longs directly on the caller's cog; no post, no wait |
| **CONFIG** | writes a configuration long directly on the caller's cog, as today. These are not in the owned set: the driver or the front cog only *reads* them. No read-modify-write exists on them (DERIVED), so last-writer-wins between application cogs is today's semantics and is kept |
| **V+POST** | validates on the caller (codes recorded there), then posts; the front cog's status is recorded and returned by the caller |
| **POST** | no caller-side validation beyond "started" |
| **SECURE** | never records, never refuses, always returns `NO_ERROR` (I6): see 2.2 |
| **LIFE** | lifecycle (section 4) |
| **FRONT** | INTERNAL USE: called only from a front cog's call graph (the object's own, or its owner's) |

### 2.2 How securing stays unconditional

`stopMotor()`/`stopMotors()`/`emergencyCutoff()`:
1. **`senseCog <> 0`:** post `REQ_STOP` / `REQ_ESTOP` and wait, bounded. The class-A order in 1.4 applies them first
   in the next pass.
2. **`senseCog == 0`** (no front cog: not started; the window inside `start()` between the driver's `coginit` and the
   front cog's launch; or after `stop()`): call `PRI secureWithoutFront(bEStop)`. It writes `e_stop := TRUE` (e-stop
   only) and then `setTargetAccel(0, false)` directly. No front cog exists, so no second writer exists. The front cog
   writes neither long at its entry (4.1), so a secure made inside the start window is not undone by the launch.
3. **Posted but not answered in time:** call `secureWithoutFront()` too, and print `DBGCH_ERROR`. By 3.6 this means
   the front cog is not executing. It is the one path where the direct writer and a live front cog could coexist, and
   it is reachable only if the front cog has broken its own bound. Section 7.1 names it as a sanctioned writer site.

`stop()` is securing in the same sense: it always stops every cog and returns `NO_ERROR` (4.3).

### 2.3 Request codes (internal `CON`, both objects)

| `REQ_*` | Args | Front action (in `lib`: this motor; in `steer`: the motors in `reqMask`) | Status produced |
|---|---|---|---|
| `REQ_ESTOP` | - | `frontEStop(TRUE)`: `e_stop := TRUE`, then write command 0, no sync | `NO_ERROR` |
| `REQ_STOP` | - | write command 0, no sync | `NO_ERROR` |
| `REQ_CLEAR_ESTOP` | - | write command 0; `e_stop := FALSE`; wait bounded (3.6) until each selected driver has left `DCS_ESTOP` | `NO_ERROR` (a driver still in `DCS_ESTOP` after the bound: `ERR_NO_RESPONSE` for that motor) |
| `REQ_DRIVE` | arg1 power (lib) / left power (steer); arg2 right power (steer); arg3 bSync | refuse if e-stopped (3.5), else compute each increment from its power on the front cog (`incrementForPower`, `maxSpeed`, reversal) and write; `motorPower := saturated power`; if bSync: one `cogatn`, bounded wait; on timeout write 0 to every selected motor | `NO_ERROR`, `ERR_EMERGENCY_STOPPED` (per e-stopped motor), `ERR_SYNC_TIMEOUT` (per motor that did not take it) |
| `REQ_DRIVE_DISTANCE` | arg1 stop ticks; arg2/arg3 powers | refuse if e-stopped (limit **not** armed); else arm the tick limit (and reset tracking in `steer`), then as `REQ_DRIVE` | as `REQ_DRIVE`. Atomic: arm-and-drive or neither (I1 item 2) |
| `REQ_LIMIT_TICKS` | arg1 ticks; arg2 bResetTracking (steer's distance limit) | optionally reset tracking; `motorStopHallTicks := arg1` | `NO_ERROR` |
| `REQ_LIMIT_TIME` | arg1 absolute `getms()` deadline (computed on the caller) | `motorStopMSecs := arg1` | `NO_ERROR` |
| `REQ_RESET_TRACKING` | - | `lib`: `posTrkHallTicks := 0`, per-pass base := `pos`; `steer`: each wheel's full window reset (today's `resetWindowAccumulators()` without its `waitms`) | `NO_ERROR` |
| `REQ_RESET_MAX` | mask | today's `bResetSenseData` action: window, HDMI maxima and tracking reset (kept as it is, TEST-USE) | `NO_ERROR` |
| `REQ_TEST_INCREMENT` | arg1 raw increment; mask one motor | refuse if e-stopped; else write raw increment, no sync | `NO_ERROR` / `ERR_EMERGENCY_STOPPED` |
| `REQ_EXIT` | - | section 4.3 | `NO_ERROR` |

### 2.4 `isp_bldc_motor.spin2`

| Method | Category | Where its `eError` comes from, and how it reaches the caller |
|---|---|---|
| `null` | - | - |
| `start`, `startEx`, `testSetup`, `stop`, `startSenseCog` | LIFE | section 4 |
| `testSetMotorId`, `setAcceleration`, `setRampingValues`, `setMaxSpeed`, `setMaxSpeedForDistance`, `calibrate`, `holdAtStop`, `forwardIsReverse` | CONFIG | caller, `NO_ERROR` as today. (`setRampingValues` writes four params-run longs non-atomically, as today; R16.6 owns the params block) |
| `resetTracking` | POST | caller: `ERR_NOT_STARTED`; else the front's `NO_ERROR`. **The `waitms(200)` is deleted**: the call returns when the reset has been applied |
| `moveShaftToAngle` | CONFIG (TEST-USE) | writes `targetAngle`, a launch-block long whose PASM reader is commented out (`lib:2512-2523`). It is not in the owned set and is unchanged |
| `driveForDistance` | V+POST | caller validates as `stopAfterDistance` (codes recorded there); posts `REQ_DRIVE_DISTANCE` with `maxSpeed4dist`; front status recorded by caller |
| `driveAtPower`, `driveAtPowerEx` | V+POST | caller: `ERR_NOT_STARTED` if `senseCog == 0`; the front cog gives `NO_ERROR` / `ERR_EMERGENCY_STOPPED` / `ERR_SYNC_TIMEOUT` (only with sync); caller `eError := recordError(ackStatus)`. The debug warning for an out-of-range power stays on the caller |
| `stopAfterRotation`, `stopAfterDistance`, `stopAfterTime` | V+POST | caller: `ERR_BAD_UNITS`, `ERR_BAD_COUNT`, `ERR_NO_WHEEL_DIA`, `ERR_LIMIT_UNRESOLVABLE`, and now `ERR_NOT_STARTED` in place of `ERR_NO_SENSE_TASK` (4.2). All validated before the post, so a rejected call arms nothing (F-4) |
| `stopMotor`, `emergencyCutoff` | SECURE | `NO_ERROR` always (2.2) |
| `clearEmergency` | POST | caller `ERR_NOT_STARTED` / front `NO_ERROR` / `ERR_NO_RESPONSE` |
| `getError` | READ | own slot, read-and-clear, unchanged |
| `getDistance`, `getRotationCount`, `getPower`, `getCurrent`, `getMaxSpeed`, `getMaxSpeedForDistance`, `getStatus`, `getDriverState`, `getRawHallTicks`, `getHallIntegrityCounts`, `boardIdString`, `getBoardType`, `is*`, `valid*`, `hallTicInfoForMotor`, `wheelGeometry` | READ | unchanged (getters record their own codes on the caller, as today) |
| `isFaultSignal` / `clearFaultSignal` | READ / CONFIG | `fault` is written by the PASM driver and cleared here, as today. Not in the owned set |
| `SyncStatus` | READ | kept public, read-only and bounded at `SYNC_TIMEOUT_MS`. The library no longer calls it |
| `getposTrkHallTicks` | READ | unchanged |
| `getDebugData` | READ | writes only this instance's HDMI pointer tables on the caller, as today |
| `testSetLimit`, `testSetFwdRevOffsets`, `testSetFwdRevIndep`, `testSetMotorReversed` | CONFIG | unchanged |
| `testGetFwdRevIndep`, `testGetResults`, `testGetTelemetry`, `testGetDriveConstants`, `testGetStopHallTicks`, `testGetRpm`, `testGetMotorCog` | READ | unchanged; `testGetRpm`'s doc names the front cog and the 1 s window |
| `testDriveAtMotorIncrement` | V+POST | caller `ERR_NOT_STARTED`; front `NO_ERROR` / `ERR_EMERGENCY_STOPPED` |
| `testResetFault` | POST + caller wait | posts `REQ_STOP`, then (caller) `clearFaultSignal()` and the existing bounded `isStopped()` wait; `ERR_FAULT_NOT_CLEARED` recorded on the caller |
| `testResetMaxValues` | POST | `REQ_RESET_MAX`; the `waitms(200)` is deleted |
| **new** `testGetFrontStats() : nPasses, nLatePasses, nMaxPassTicks` | READ (TEST-USE) | Visit 4's late-pass and budget cells |
| `resetWindowAccumulators`, `updateWindowAccumulators` | **become PRI** | today these are PUB INTERNAL USE and write `posTrkHallTicks`. As PRI they have only front-graph callers (7.1). Phase 2 compiles every top to find outside callers (8.3) |
| **new** `recordCallerError(eCode) : eSameCode` | INTERNAL USE | `recordError(eCode)` on the calling cog, for an owner that has received a motor's status (2.6) |
| **new** `front*` routines | FRONT | section 6.1; called by this object's front loop and by an owner's |

### 2.5 `isp_steering_2wheel.spin2`

| Method | Category | `eError` source and path |
|---|---|---|
| `start`, `stop` | LIFE | section 4 |
| `setAcceleration`, `setMaxSpeed`, `setMaxSpeedForDistance`, `calibrate`, `holdAtStop` | CONFIG | unchanged: `firstError()` over the wheels' direct setters, on the caller |
| `resetTracking` | POST (mask 3) | caller `ERR_NOT_STARTED` recorded in steer's slot; front `NO_ERROR`. **The two 200 ms waits are gone** |
| `driveDirection` | V+POST | `calcPowerForDirection()` on the caller, then as `driveAtPower`. `rqstPower`/`rqstDirection` are HDMI echoes, still written by the caller |
| `driveAtPower` | POST (mask 3, sync) | caller: `ERR_NOT_STARTED` into steer's slot. Front: per wheel `ackMotorStatus` = `NO_ERROR` / `ERR_EMERGENCY_STOPPED` / `ERR_SYNC_TIMEOUT` (both wheels written 0 on any timeout, audit M). Caller records each wheel's code with `ltWheel.recordCallerError(eLeft)`, `rtWheel.recordCallerError(eRight)` and returns `firstError(eLeft, eRight)`. So `getError()` gives `eLeftError`/`eRightError` exactly as today |
| `driveForDistance` | V+POST | caller validates the shorter distance (as `stopAfterDistance`, into steer's slot), reads `getMaxSpeedForDistance` on both wheels, posts `REQ_DRIVE_DISTANCE`; statuses as `driveAtPower` |
| `stopAfterRotation`, `stopAfterDistance`, `stopAfterTime` | V+POST | caller codes as today (steer's slot, including `ERR_NOT_STARTED`); front `NO_ERROR`. `stopAfterDistance` posts `REQ_LIMIT_TICKS` with bResetTracking = TRUE, so reset-and-arm is one front action |
| `stopMotors`, `emergencyCutoff` | SECURE | 2.2, over both wheels. With `senseCog == 0` the direct path calls each wheel's `secureWithoutFront()` through a FRONT-marked PUB (`frontSecure(bEStop)`) |
| `clearEmergency` | POST (mask 3) | caller `ERR_NOT_STARTED` / front `NO_ERROR` / per-wheel `ERR_NO_RESPONSE` recorded into that wheel's slot |
| `getError` | READ | unchanged three-result form |
| `getDistance`, `getRotationCount`, `getPower`, `getCurrent`, `getHallIntegrityCounts`, `getStatus`, `getMaxSpeed`, `getMaxSpeedForDistance`, `getLeft/RightDebugData`, `valid*`, `is*`, `showDriveStates` | READ | unchanged |
| `testGetDriverState`, `testGetBoardTypes`, `testGetFaultStatus`, `testGetRawHallTicks`, `testLeft/RightGetTelemetry`, `testLeft/RightGetResults`, `testLeft/RightGetRpm`, `testLeft/RightGetFwdRevIndep`, `testLeft/RightGetRampingValues` | READ | unchanged |
| `testLeft/RightSetFwdRevOffsets`, `...SetFwdRevIndep`, `...SetLimit`, `...SetMotorReversed` | CONFIG | unchanged |
| `testLeft/RightDriveAtMotorIncrement` | V+POST (mask 1 / 2) | front per-wheel status recorded into that wheel's slot on the caller |
| `testLeft/RightResetFault` | POST + caller wait | posts `REQ_STOP` for that wheel; then on the caller `wheel.clearFaultSignal()` and the bounded `isStopped()` wait; `ERR_FAULT_NOT_CLEARED` via `wheel.recordCallerError()` |
| `testLeft/RightResetMaxValues` | POST (mask 1 / 2) | front `NO_ERROR` |
| **new** `testGetFrontStats()` | READ (TEST-USE) | as in `lib` |

### 2.6 Why every status reaches its caller unchanged (DERIVED)

- The front cog produces a status as a value and writes it to `ackStatus`/`ackMotorStatus`. It calls no recording
  method, so a library-owned cog writes no error slot (I4 item 4, and the task's invariant).
- The waiting caller reads the value after `ackSeq` matches, and records it with its own `recordError()` (or the
  wheel's `recordCallerError()`, which calls the wheel's `recordError()` on the same calling cog). It returns the
  value that `recordError` hands back, which is the same value by construction (`lib:1736-1746`).
- Sticky-first and read-and-clear are unchanged, because `recordError` is still the only writer of `lastError[]`.

---

## 3. The front loop

### 3.1 Constants

| Constant | Value | Basis |
|---|---|---|
| `FRONT_LOOP_HZ` | 1000 | task body |
| `HALL_WINDOW_SIZE` | 125 | window span = 125 slots x 8 passes = 1 s. Keeps today's ~128 Hz update cadence of the rpm moving sum, and today's 1 s span |
| `WINDOW_PASSES` | `FRONT_LOOP_HZ / HALL_WINDOW_SIZE` = 8 | integer by choice of 125 |
| `DRIVE_PASS_US` | 523 | DERIVED and certified: 522.7 us per drive pass (PL-50) |
| `FRONT_SYNC_WAIT_PASSES` | 4 | section 3.6 |
| `REQ_ACK_TIMEOUT_MS` | 20 | design value; section 3.6 shows the bound holds |
| `FRONT_START_TIMEOUT_MS` | 100 | start handshake (4.1); covers cog launch latency (UNVERIFIED F5) |
| `LATE_MARGIN_US` | 100 | guard before `waitct` (3.4; UNVERIFIED F3) |
| `STACK_SIZE_LONGS` | 128 in both objects | today 48 / 64 ("exceed at 48", `steer:1075`); the call depth grows by about one frame (front -> wheel.frontDrive -> incrementForPower -> map). Stack need per frame is UNVERIFIED (F5), so the size is doubled and made observable (3.7) |

`SENSE_LOOP_HZ`, `ESTOP_HOLD_PASSES` and `ticksSenseLp` are deleted, and the auto-clear goes with them.

### 3.2 One pass (single motor, `lib` `PRI frontLoop()`)

```
entry:  geometry := hallTicInfoForMotor() (compile-time, PL-70); per-pass base := pos; window reset
        (no waitms); posTrkHallTicks := 0; nextDue := getct() + ticksPerPass
repeat
    passStart := getct(); frontPasses++
    1. requests:   sweep 8 slots; apply class A, then B, then C (1.4). EXIT -> park (4.3)
    2. tracking:   frontTrack(passCount): if drv_state is DCS_FAULTED or DCS_ESTOP, zero tracking and window
                   (today's behaviour, now with no 200 ms wait); else posTrkHallTicks += |pos - base|,
                   base := pos; every WINDOW_PASSES-th pass: window slot update + updateHdmiData()
    3. limits:     if frontLimitsDue(getms()) then write command 0 (same pass). Precedence as today:
                   time checked first, distance only when no time limit is armed (lib:2108-2117)
    4. accounting: body := getct() - passStart; frontMaxPassTicks max= body
                   late test and absolute wait (3.4)
```

`steer` `PRI frontLoop()` is the same shell over both wheels:
- step 2 calls `ltWheel.frontTrack()` and `rtWheel.frontTrack()`;
- step 3 checks steer's own platform limits (either wheel's `getposTrkHallTicks()` past `motorStopHallTicks`, or time)
  and stops both wheels;
- `showDriveStatesOnChange()` runs after step 3, as today.

The per-pass tracking accumulation is new. Today `posTrkHallTicks` advanced only when the window did, every 7.8 ms,
so a distance limit could be seen up to one window step late. At 1 ms, the limit sees at most 1 ms of stale counts.
This is DERIVED, and it is what makes C-3's "within about one tick" reachable.

### 3.3 Stop within one pass

A limit crossing appears in `pos` on the driver's status copy. The next pass sees it at step 2, and step 3 writes the
zero command in the same pass. The driver takes it on its next drive pass. Bound: <= 1 ms + 522.7 us, about 1.5 ms.
At top speed that is under one tick (design §3.2, DERIVED). Deceleration distance (C-4, PL-58) is unchanged and is
R16.7's.

### 3.4 Absolute schedule and late passes

- `nextDue` advances by `ticksPerPass = CLKFREQ / FRONT_LOOP_HZ` each pass, and is never re-derived from
  `passStart`, so a normal pass does not drift.
- **Late test before every wait:** the pass is late if `nextDue - getct()` (as a signed tick difference) is below
  `LATE_MARGIN_US` in ticks. A late pass increments `frontLatePasses`, skips `waitct`, and re-anchors:
  `nextDue := getct() + ticksPerPass`. Missed slots are not replayed.
- **Why the test is mandatory (UNVERIFIED F3):** if `WAITCT` with a target already past waits for the counter to wrap,
  a late pass that reaches `waitct` stalls for about 2^32 ticks, 15.9 s at 270 MHz.
- **DERIVED finding for the arbiter, independent of this task:** today's sense tasks call `resetWindowAccumulators()`
  on every pass while a driver is `DCS_FAULTED` or `DCS_ESTOP`, and that calls `resetTracking()`, which does
  `waitms(200)` (`lib:2095-2096`, `lib:2063`, `lib:615`; `steer:1168-1172`). A 7.8 ms pass therefore runs 200-400 ms
  and then reaches `waitct()` with a target already past (`lib:2139`, `steer:1217`). If F3 holds, the unfixed sense
  task stalls about 16 s each pass while faulted or e-stopped. That would stretch S-4's "1/8 s" auto-clear and every
  limit check in that state. It should be filed on the punch list. The front cog removes it by construction: there
  is no wait in the loop body, and the late test runs before every `waitct`.

### 3.5 E-stop latch and drive refusal

- No auto-clear exists anywhere. `e_stop` is written only by `frontEStop()` (TRUE, from `REQ_ESTOP`), by
  `REQ_CLEAR_ESTOP` (FALSE), and by the pre-launch `init()` and the direct securing path (section 7.1).
- **Refusal predicate, per selected motor:** `(e_stop <> FALSE) or (drv_state == DCS_ESTOP)`. The first term is the
  front cog's own latch, which closes the one-drive-pass window between setting `e_stop` and the driver reporting
  `DCS_ESTOP`. The second term follows the task wording.
- **When the predicate holds:** that motor's status is `ERR_EMERGENCY_STOPPED` and **no motor in the request is
  written**. The whole request is refused, so a platform never drives one wheel. The design's stale-command surprise
  cannot arise, because nothing is written while latched.
- **`REQ_CLEAR_ESTOP`** writes command 0 first, so nothing moves after the clear, even by construction. It then
  releases `e_stop`, and answers only once every selected driver has left `DCS_ESTOP`, bounded (3.6). So a drive
  posted right after `clearEmergency()` returns is not refused for the one pass the driver needs to leave the state.
- **Time to refusal:** a refusal waits for nothing, so it is answered within 4.1 ms (3.6). The Visit 4 bound is
  50 ms.

### 3.6 Per-pass budget and the acknowledgement bound

| Work in a pass | Cost | Basis |
|---|---|---|
| Slot sweep, nothing open (8 x two long reads and a compare) | a few us | UNVERIFIED (F13: Spin2 per-operation cost is not in hand); instrumented by `frontMaxPassTicks` |
| Tracking per motor (state read, `pos` read, abs, add) | part of today's body | today's body "about 1_880 ticks ... little over 9 uS @200MHz" (`lib:2137`, `steer:1215`). The comment gives no measurement record, so treat it as UNVERIFIED |
| Window update + `updateHdmiData()` (every 8th pass; float math) | part of the same ~9 us | same |
| Limit check | a few operations | inference |
| **Idle pass total** | tens of us against a 1_000 us slot | DERIVED from the rows above, subject to F13 |
| Synchronized drive wait | <= 522.7 us for a live driver | DERIVED: `gettgtincr` polls ATN once per drive pass (`lib:3313-3320`), passes are 522.7 us (PL-50) |
| Sync / clear-e-stop bound per request | 4 drive passes, about 2.1 ms | 4x margin over the live-driver case |
| `debug()` output from the front cog | not budgeted | channel-masked by the user config; when enabled, each line blocks for its transmission (UNVERIFIED F12). Visible as late passes |

**Rule: at most one bounded wait per pass.** Only `REQ_DRIVE`/`REQ_DRIVE_DISTANCE` with sync and `REQ_CLEAR_ESTOP`
wait. When one of them has waited in a pass, any further waiting request stays open to the next pass. Non-waiting
requests (securing, limits, resets, EXIT) are applied in the same pass regardless.

**The acknowledgement bound, with that rule** (DERIVED). There are at most 6 application cogs with a single motor
(8 - driver - front) and 5 with two wheels. So at most 6 waiting requests are ahead of any request.

The worst case for a waiting request is 6 passes of (1 ms + one 2.1 ms wait): **18.6 ms < `REQ_ACK_TIMEOUT_MS` = 20**,
for any mix of callers. A non-waiting request is answered in the pass after it is posted, even behind one wait:
<= 1 + 2.1 + 1 = **4.1 ms**. That covers securing requests and e-stop refusals, and it is the figure the
"no hang while e-stopped" cell sees.

**Why the sync wait is 4 drive passes, not the design's 20.** With 20 drive passes (10.45 ms) the same arithmetic
gives 6 x 11.45 = 68.7 ms, which breaks the design's own `REQ_ACK_TIMEOUT_MS = 20`. A live driver takes a sync command
within one drive pass (`gettgtincr` polls ATN every pass, and is reached in every state except e-stop, which is
refused before any write). So 4 passes is a 4x margin, and an expiry means a driver that is not running. That case is
already an error: the front cog writes command 0 to every selected motor and returns `ERR_SYNC_TIMEOUT`.

### 3.7 Stack observability

At launch, `start()` fills the front stack with a sentinel pattern. `testGetFrontStats()` also returns the high-water
mark by scanning for the first non-sentinel long, which is a read on the caller. An overflow therefore shows as a
number in a Visit 4 cell, not as corrupted VARs. The stack arrays are included in the ABI guard (section 5).

---

## 4. Lifecycle

### 4.1 Start

**Single motor, `startEx(base, volts, detect, sync)`:**
1. `setupForStart()`, unchanged: validate, then `stop()` of the previous instance (now including its EXIT), claim,
   and `init()`.
2. Before any launch (no cog of this instance exists): `sync_required := sync`, `params_ptr`,
   `setTargetAccel(0, false)`, `frontPasses := frontLatePasses := frontMaxPassTicks := 0`, and fill the stack sentinel.
3. `motorCog := coginit(NEWCOG, @driver, @pinbase)`. On failure: `recordError(ERR_NO_FREE_COG)`, `stop()`, return -1
   (today's path, `lib:152-161`).
4. **`sync == FALSE` (standalone):** `senseCog := cogspin(NEWCOG, frontLoop(), @taskStack)`.
   - Launch failure: `recordError(ERR_NO_FREE_COG)` on the caller, `stop()` (driver and pins released), return -1.
   - Launched: wait up to `FRONT_START_TIMEOUT_MS` for `frontPasses <> 0`. On expiry: `recordError(ERR_NO_RESPONSE)`,
     `stop()`, return -1.
   - Otherwise return the driver's cog id, as today.
   - **Cog cost 2.**
5. **`sync == TRUE` (owned):** no front cog. The driver waits on ATN from its owner. Commands on this instance return
   `ERR_NOT_STARTED`, because only the owner's front cog services it. **Cog cost 1**, and the owner adds 1.

**Why `sync` is the owned switch** (API rule, DERIVED): the parameter's only in-tree purpose is the steering object's
lockstep (`steer:152`, `:154`). A synced driver needs someone else's `cogatn`, which is exactly an owner. The task
fixes `startEx(..., sync: true)` as the lockstep call. A bench top that calls `startEx(..., TRUE)` on a standalone
motor and then commands it would change behaviour, so phase 2 checks for one (8.3).

**Two wheels, `steer:start()`:**
1. Stop a running front cog first (EXIT, 4.3).
2. `ltWheel.startEx(..., TRUE)`, `rtWheel.startEx(..., TRUE)`. The F-13 cleanup is unchanged.
3. `rtWheel.forwardIsReverse()`; `cogmask`; `waitms(100)`; **`cogatn(cogmask)` on the caller before any front cog
   exists** (unchanged, `steer:168-172`).
4. Pre-launch initialisation of `tickInMM_x100`, `motorStopHallTicks := 0`, `motorStopMSecs := 0` and the rest, the
   heartbeat counters, and the stack sentinel.
5. `senseCog := cogspin(NEWCOG, frontLoop(), @taskStack)`, then the handshake as in the single-motor step 4. On failure
   both wheels stop, `recordError(ERR_NO_FREE_COG or ERR_NO_RESPONSE)` goes into steer's slot on the caller, and -1 is
   returned. Otherwise the front cog id is returned (today's contract: the sense cog id). **Cog cost 3.**

The front cog's entry writes none of `targetIncre`, `e_stop` or the limits. It adopts them, so a securing write made
inside the start window survives (2.2).

### 4.2 `startSenseCog()`: kept, as a query that starts nothing

**The API rule:** *"the actions requested through the API should be what we'd expect the actions to do in a clean
way."*
- **Removing it** breaks `demo_single_motor.spin2:74` and every caller written to 5.x docs. The error contract's
  migration rule is also "no public method is removed" (ABORT design §4).
- **Starting a second cog** would break the fixed cog count.
- **What the name promises**, a running sense task with its id returned, is already true after `start()`.

**Decision:** `startSenseCog() : ok` returns `senseCog - 1` when the front cog runs. Otherwise it returns -1 and
records `ERR_NOT_STARTED`, because a front cog cannot exist without a started driver.
- Doc: *"Return the id of the sense (front) cog that start() launched; starts nothing. -1 when the motor is not
  started, with the cause in getError()."*
- **Visible change:** `testSetup()` followed by `startSenseCog()` used to launch a sense task with no driver. It now
  returns -1. Phase 2 checks the bench tops for that pattern (8.3).
- `ERR_NO_SENSE_TASK` stays declared (and mirrored) so no caller's source breaks. It is no longer raised, and this is
  documented.

### 4.3 Cooperative shutdown (PL-41's pattern)

`lib:stop()` and `steer:stop()`:
1. If `senseCog <> 0`, post `REQ_EXIT` and wait up to `REQ_ACK_TIMEOUT_MS`. In the front cog, class C:
   - it answers every other open slot: securing requests `NO_ERROR` (the cogs are about to stop), everything else
     `ERR_NOT_STARTED`;
   - it acknowledges EXIT;
   - it **parks**: `repeat` with `waitms()`, and no `debug()`.

   Its last `debug()` has finished before the acknowledgement, because the cog is sequential. So the `cogstop` that
   follows cannot cut a line (PL-41, Stephen 2026-09-14). The front cog parks rather than returning so that its cog
   id cannot be released and reused before the caller's `cogstop` (fact F6; the plan does not depend on what a return
   does).
2. On acknowledgement timeout: `debug[DBGCH_ERROR]` from the caller ("front cog did not acknowledge EXIT; stopping
   anyway"), and continue. `stop()` still returns `NO_ERROR` (I6): the cogs are stopped, and only the clean-line
   guarantee was lost.
3. `cogstop(senseCog - 1)`, `senseCog := 0`. Then the existing driver stop, `drv_state := DCS_Unknown`, `pinclear`,
   and claim release (`lib:172-205`). `steer` then calls `ltWheel.stop()` and `rtWheel.stop()`, which are owned and
   stop drivers only.

**Residual, unchanged from today:** two cogs calling `stop()` on one instance at the same moment can both `cogstop`
the same ids. The front cog answers both EXITs. Concurrent `stop()` of one instance is not supported, as today.

### 4.4 Failure paths and where each cause is recorded

| Failure | Returned | Recorded on |
|---|---|---|
| any `setupForStart()` validation / claim | -1 | caller (`recordError`, unchanged) |
| driver `coginit` | -1 | caller, `ERR_NO_FREE_COG` |
| front `cogspin` | -1 | caller, `ERR_NO_FREE_COG` (in `steer`: steer's slot) |
| front handshake timeout | -1 | caller, `ERR_NO_RESPONSE` |
| a wheel's `startEx` inside `steer:start` | -1 | the wheel's slot for the caller cog (unchanged), read through `getError()`'s left/right results |

The front cog records nothing on any path.

---

## 5. VAR runs: what is added, and proof the ABI is untouched

**Unchanged, character for character** (checked in phase 2 by `git diff`):
- `VAR { * Data Structure for PASM Driver * }` (`lib:2305-2338`: `motorCog`, `senseCog`, `maxDrvTics`, `minDrvTics`,
  the launch run `pinbase..targetIncre`, the status run `drive_u..hall_illegal`, `fault`);
- `VAR { Motor Parameters }` (`lib:2370-2392`: `offset_fwd..ramp_inc`, `frame_cnt`);
- the whole PASM `DAT` from `lib:2407` to the end of `lutCodeEnd`;
- `VAR { * Data for Motor Position Tracking * }` and `VAR { * HDMI Data ... * }`, which sit between the two runs
  (`lib:2340-2368`).

**Changed, outside every run:**

| Block | Change | Position relative to the runs |
|---|---|---|
| `lib` `VAR { * sense buffer and stack arrays * }` (`lib:1954-1965`) | `taskStack[STACK_SIZE_LONGS]` gets its constant raised to 128; `hallCountsWindow[SENSE_LOOP_HZ]` becomes `[HALL_WINDOW_SIZE]` (125); `bResetSenseData` deleted | textually before `pinbase` |
| `lib` new `VAR { front cog request slots }` | section 1.1, plus the per-pass base `trackBasePos` | textually after `lastError` (`lib:2405`), before `DAT { Motor DRIVER }` |
| `steer` `VAR { time values & arrays }` (`steer:1088-1096`) | `taskStack` resized by constant; `ticksSenseLp` becomes `ticksPerPass` | no ABI in `steer` |
| `steer` new `VAR { front cog request slots }` | section 1.1 | after `steer:995` |

**Extended ABI guard** (`abiLayoutIsValid()`, `lib:1748-1763`). The three run checks stay as they are. For **each**
of `lastError`, every request array, the three front counters, `taskStack`, `hallCountsWindow` and `trackBasePos`,
the guard adds "lies wholly outside `@pinbase..@fault` and wholly outside `@offset_fwd..@ramp_inc`". The check is one
new PRI, `outsideDriverRuns(pFirst, pLast) : bOutside`, used once per array. The stack is the most important entry:
it is the only new memory written at 1 kHz. Should the compiler ever lay a declaration inside a run (declaration
order is UNVERIFIED, F9), `startEx()` refuses with `ERR_ABI_MISMATCH` and launches no cog.

---

## 6. How a roster plugs in later («#3562»), without rework

### 6.1 The per-motor service surface (the seam)

These are PUB INTERNAL-USE routines on `isp_bldc_motor`, marked `' FRONT COG ONLY` in their doc. They are the entire
contract between a motor and whoever owns it:

| Routine | Does |
|---|---|
| `frontDrive(power, bSync) : eStatus` | refusal check; increment from power; write; `motorPower` |
| `frontWriteIncrement(nIncre, bSync)` | raw write (TEST-USE path and stops) |
| `frontEStop(bEStop)` / `frontIsEStopped() : bEStopped` | latch control and the refusal predicate |
| `frontTakenSync() : bTaken` | reads the sync bit (the owner's bounded wait loops over its motors) |
| `frontDriverCogBit() : cogBit` | `1 << (motorCog - 1)`, or 0 when no driver is running (never `1 << -1`, D1) |
| `frontTrack(passCount)` | tracking, fault/e-stop zeroing, window cadence |
| `frontSetLimits(nTicks, nMsDeadline)` / `frontLimitsDue(nowMs) : bFired` | per-motor limits |
| `frontResetTracking(bWholeWindow)` / `frontResetMax()` | resets |
| `frontSecure(bEStop)` | the direct securing path, guarded by the owner's own "no front cog" test |
| `recordCallerError(eCode) : eSameCode` | a status delivered to the caller's slot |

The standalone `lib:frontLoop()` calls exactly these, by name within its own object. `steer:frontLoop()` calls them
on `ltWheel`/`rtWheel`. A roster owner's `frontLoop()`
calls them on `motor[idx]`. The per-motor work exists once. Only the loop shell and the slot protocol are repeated,
as the design accepts (§4).

### 6.2 Protocol fields that already carry a roster

- **`reqMask`** is a bitmask of owned motors. Steer uses bits 0 and 1; a roster uses bits 0..2. "All motors" is
  `(1 << count) - 1`.
- **`ackMotorStatus[c * OWNED_MOTOR_MAX + i]`** carries per-motor statuses. A roster sets `OWNED_MOTOR_MAX = 3` and
  its caller records each motor's code with `motor[i].recordCallerError()`, exactly as steer does for two.
- **The synchronized drive** is written over a mask: OR `frontDriverCogBit()` over the selected motors, one `cogatn`,
  one bounded wait over the mask. The two-wheel case is that loop with two entries.
- **The refusal predicate and the securing classes** are per motor inside a mask loop, so roster-wide `stopAll()` and
  `emergencyCutoff()` are `REQ_STOP` and `REQ_ESTOP` with the all-motors mask.
- **The cog cost stays N + 1,** because an owned motor never starts a front cog (4.1, `sync = TRUE`).

### 6.3 What is deliberately not built

The roster object, its indexed API, its config block, `demo_n_motor` and the gate's `nmotor` classifier. None of the
seams above needs changing to add them (inference, from the table in 6.1 being index-free).

---

## 7. Verify plan

### 7.1 Single-writer source-search property

Phase 2 is accepted only if a text search over `src/isp_bldc_motor.spin2` and `src/isp_steering_2wheel.spin2` shows
all of the following:
- every assignment to `targetIncre`, `e_stop`, `motorStopHallTicks`, `motorStopMSecs` and `posTrkHallTicks` (`:=`,
  `+=`, `~`);
- every `cogatn(`;
- every call of the PRIs/PUBs that contain those writes.

Each of those sites must lie in one of these **sanctioned sites**:

| Site | Why a second writer cannot exist there |
|---|---|
| the front cog's call graph: `frontLoop()` -> apply/track/limit PRIs -> `front*` routines -> `setTargetAccel()`; in `steer`, `frontLoop()` -> `ltWheel/rtWheel.front*` | it is the owner |
| pre-launch initialisation: `init()` (`targetAngle`, `e_stop := FALSE`), `startEx()` before `coginit`/`cogspin`, `steer:start()` before `cogspin` | no cog of the instance exists yet |
| `steer:start()` lockstep `cogatn(cogmask)` | before the front cog exists (task body) |
| `secureWithoutFront()` / `frontSecure()`, reached only when `senseCog == 0` or after an unanswered securing post | no front cog, or a front cog that has broken its bound (2.2) |
| the PASM driver's `wrlong tgt_incr, ptra[-1]` clearing the sync bit (`lib:3319`) | the ABI, unchanged and outside Spin2 |

Anything else fails the property. The search also confirms that `resetWindowAccumulators`/`updateWindowAccumulators`
are PRI, and that no `recordError(` or `recordCallerError(` call is reachable from either `frontLoop()`.

### 7.2 Gates

- `tools/build-check.sh`: green, every top certified, both release demos certified.
- `tools/check_style.sh`: exit 0.
- `git diff 4e07f89 -- src/isp_bldc_motor.spin2` shows no hunk inside the PASM `DAT`, `VAR { * Data Structure for PASM
  Driver * }` or `VAR { Motor Parameters }` (section 5).
- `central:spin2-authoring-guide` at strength gate for the changed methods: single exit (§5.2), doc structure (§4.3),
  named constants (§5.7).
- **Recorded departure from the guide, T3:** guide §5.8 requires a hardware lock and WAITATN/COGATN signalling for a
  worker cog. This design uses per-cog slots with no lock, and polled acknowledgement, as Stephen's governing design
  requires. ATN is reserved for the drivers' sync, where it is part of the unchanged ABI.

### 7.3 Phase-2 checks (compile gate plus reading, no bench)

- Tops calling `resetWindowAccumulators`, `updateWindowAccumulators`, `startSenseCog` after `testSetup`, or
  `startEx(..., TRUE)` on a standalone motor. The compile gate finds the first two; the last two are found by reading
  the `test_*`, `util_*` and `demo_*` tops that include `isp_bldc_motor` directly.
- `CLAUDE.md` "Cog model" paragraph updated: the sense cog is the front cog, started by `start()`; single = 2 cogs,
  two wheels = 3.
- `isp_bldc_motor.txt` regeneration is Stephen's; it is recorded as stale.

### 7.4 Visit 4 cells (harness «#3560»), today's two forms

Each cell prints PASS / FAIL / NOMEAS, with the value the unfixed tree gives.

| Cell | Test | PASS | Unfixed value (4e07f89) |
|---|---|---|---|
| Cog count | free cogs before/after `start()`, and after `stop()` | single: 2 used after `start()` alone; two wheels: 3; all returned | single: **1** after `start()` alone (2 only if `startSenseCog()` is called); two wheels 3; all returned |
| Lockstep | driver-state samples at start and on each synchronized drive | every driver leaves `DCS_STOPPED` within one drive pass of the other | lockstep also holds unfixed (same ATN mechanism, issued from the caller). This cell guards against regression and does not discriminate |
| Stop latency (C-3) | `stopAfterDistance()` at half speed: ticks from limit crossing to `DCS_SPIN_DN`; overshoot | <= 1 tick; overshoot <= C-4 ramp distance + 1 | ~2 ticks at 128 Hz (task body). Up to one extra 7.8 ms window step of stale `posTrkHallTicks` (3.2) |
| No hang while e-stopped (F-6) | `emergencyCutoff()`, then a drive; time and status; then `clearEmergency()` and watch `pos` | returns `ERR_EMERGENCY_STOPPED` within 50 ms; `pos` unchanged after the clear | two wheels: `ERR_SYNC_TIMEOUT` after >50 ms (`SYNC_TIMEOUT_MS`, strict `>`), so FAIL on the status and on the time. Single motor: `NO_ERROR`, and the motor drives once the auto-clear releases the e-stop, so FAIL |
| Ordered stop during a drive | cog B arms a time limit; cog A drives repeatedly; the limit fires during a drive | every motor ends `DCS_STOPPED` with command 0 | usually PASS: the unfixed race window is a few us. This cell guards against regression and is not a discriminator, which is stated in its label |
| Cooperative shutdown | a front-cog debug channel enabled in the harness build; `stop()` right after a state change | EXIT acknowledged; no truncated line in the log | a truncated line is possible, not certain (PL-41). Non-deterministic unfixed |
| Tracking reset at speed | at speed: `resetTracking()`; time the call; `getDistance()` after N ms against N ms of `pos` motion | call <= 20 ms; distance counts only post-reset motion (within 1 tick) | call >= 200 ms (single) / >= 400 ms (two wheels), so FAIL on time. Post-reset counts can include a pre-reset window step when the sense task's `+=` races the zero |
| Front loop health (new) | `testGetFrontStats()` over a full drive sequence at the release debug mask | `frontLatePasses == 0`; max pass < 1_000 us; stack high-water < `STACK_SIZE_LONGS` | NOMEAS (getter does not exist) |

---

## 8. Open questions

Only one remains that the tree, the designs and the authorities cannot settle:

1. **Names and values of two new public error codes**, mirrored in `steer`. The error contract gives signatures and
   names to Stephen where more than one answer is correct (ABORT design §5). A code is needed in both cases, because
   I1 forbids reusing a code with another meaning:
   - `ERR_EMERGENCY_STOPPED = -1_016`: a drive refused while e-stopped (F-6; task body).
   - `ERR_NO_RESPONSE = -1_017`: the front cog did not answer within its bound, either at start or for a request.

   Recommendation: these names. They read as the condition, and they sit next in the ordinary range.

---

## 9. P2 facts to verify (all UNVERIFIED in this phase; no p2kb access)

| # | Fact the plan assumes | Where it matters |
|---|---|---|
| F1 | `COGATN(mask)` latches an attention request on each target cog, and the request persists until that cog `POLLATN`s or `WAITATN`s. `POLLATN` consumes it | the sync drive; the stranded-ATN reasoning in 3.6; the lockstep start |
| F2 | an ATN sent before the driver reaches `WAITATN` is not lost | the lockstep start (unchanged; `waitms(100)` precedes it today) |
| F3 | `WAITCT(target)` with `target` already in the past waits until the 32-bit counter next equals `target` (about 2^32 ticks) | the mandatory late test (3.4) and the DERIVED ~16 s stall finding |
| F4 | `GETCT()` is a free-running 32-bit counter, and signed differences across a wrap are correct in Spin2 integer arithmetic | schedule, late test, bounded waits |
| F5 | `COGSPIN(NEWCOG, method(), @stack)` returns the cog id or a negative value on failure. Stack need per call frame and per `debug()` statement. Latency from `COGSPIN` to the first executed statement | `STACK_SIZE_LONGS = 128`; `FRONT_START_TIMEOUT_MS = 100` |
| F6 | what happens when a `COGSPIN`'d method returns (cog stops, and its id becomes free) | the choice to park instead of return (4.3) |
| F7 | `COGSTOP` of a cog mid-`debug()` frees lock 15 and truncates only that line | settled by Stephen 2026-09-14 (PL-41); listed for completeness |
| F8 | `COGID()` is 0-7 and constant for a cog's life; Spin2 v47 tasks on one cog share it | per-cog slots (1.5) |
| F9 | VAR declarations are laid out in declaration order | protected, not assumed: the ABI guard refuses a wrong layout (5) |
| F10 | a hub LONG read by one cog never observes a partially written LONG from another | the no-lock protocol (1.2-1.4) |
| F11 | `GETMS()` is monotonic and wraps at 2^32 ms | time limits (unchanged semantics) |
| F12 | a `debug()` statement blocks its cog for the duration of its transmission; channels excluded by `DEBUG_MASK` compile to nothing | the budget row for debug output |
| F13 | the cost of a simple Spin2 statement (long read, compare, add) at 200-300 MHz | the idle-pass budget (3.6); instrumented by `frontMaxPassTicks` either way |
| F14 | a call `ltWheel.frontX()` made on the steering front cog runs on that cog, using `ltWheel`'s VAR instance | the owned-motor model (6.1) |
| F15 | `COGSTOP` on a driver cog leaves its smart-pin modes configured until `PINCLEAR` | unchanged `stop()` order (driver stopped, then pins cleared) |
