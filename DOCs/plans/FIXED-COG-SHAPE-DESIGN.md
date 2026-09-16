# Fixed cog shape — phase-1 design («#3513», with «#3512» C-3)

Status: **shape agreed by Stephen 2026-09-15; the product shapes are his ruling below. Nothing is
implemented.** Two items are flagged for him in §7, neither blocking.

> **AMENDED 2026-09-16 by Stephen's rulings. Where the body below disagrees, this block governs.**
> - **In this sprint (6.0.0): the front cog (§3) for today's two forms.** Those are `isp_bldc_motor`
>   standalone and `isp_steering_2wheel`. STEPHEN chose the cog shape for this sprint, *"I would like A"*.
> - **After 6.0.0, with the Doco effort:** the roster owner and N-motor API (§4), `demo_n_motor` (§7), the
>   `nmotor` config blocks and the gate's block classifier. STEPHEN: *"yes, after 6.0.0"*.
>   - The front cog is still built so a roster plugs in later without rework.
>   - The §6 roster rows are not certified in this sprint.
> - **§1's "Driving shape: 6.5″ hub only" is corrected.** STEPHEN's words were that the N-motor shape never uses
>   6.5″ motors. A dual Doco config block exists and is certified, so the driving shape stays open to both motor
>   types.
> - **§3.2 and §8, "S-4 unchanged", are superseded.** The e-stop latches until `clearEmergency()`, with no
>   auto-clear (API rule, STEPHEN 2026-09-16).
> - **§8, "PL-47 out of scope", is superseded.** The error contract lands first. Requests posted to the front
>   cog carry their status back to the caller, and the protective-stop detector runs in the front cog.
>   (`ABORT-ERROR-CONTRACT-DESIGN.md`, amended 2026-09-16.)
> - **§3.3, "refused and reported on `DBGCH_ERROR` until PL-47 lands":** a drive refused while e-stopped
>   returns an `ERR_*` status.

## 0. The decisions on record

**STEPHEN 2026-09-15**, on ownership, verbatim: *"the sense cog is the owner, cog for the motors, this extends
to the dual stering form too stearing control and sense are one cog. so the front cog forwards the inteface to
the motors. Agreed."*

**STEPHEN 2026-09-15**, on the product shapes, verbatim: *"I think there are two basic different shapes here:
1. A driving system that would be the dual motor with steering. 2. N motors. The way we get over 3 is we have
multiple P2s communicating over serial to get to 6 or 9. A single P2 is going to control 1 to 3 motors, but
they will never be the 6.5-inch shape motors. The 6.5-inch shape is for rubber wheels for driving. They'll
never run a CNC. The Docom motors are the ones that drive CNCs. … Demo single motor should actually be demo 1
or more motor."*

**STEPHEN 2026-09-15**, on the demo set, verbatim: *"how about we add the demo_n_motor to the set not replace
the single motor demo. reason users of the repo get to see all three forms implemented"*. So the repo ships
**three** demos: one motor, 1-to-3 motors, and the two-wheel driving platform.

**STEPHEN 2026-09-11:** *"What I want is a motor subsystem that is a fixed number of cogs, that is highly
reliable, and that is the minimum number of cogs we can do a motor system in."* The library never runs on the
user's application cog.

Options B (raise the sense-loop rate, change nothing else) and C (front cog split into Spin2 tasks) are **not
taken**: B leaves every two-writer hazard in §2.2 in place; C needs Spin2 v47 and a task table sharing cog
registers `$100..$11F` with inline PASM, for a loop that already fits one pass (§3.2).

## 1. The two shapes

| | **Driving shape** | **N-motor shape** |
|---|---|---|
| Object | `isp_steering_2wheel` | the roster owner (§4) |
| Motors | exactly 2, **6.5″ hub only** | **1 to 3, Doco only** |
| Motor role | rubber wheels, driving a platform | CNC and positioning axes |
| Coordination | steering: power + direction, turn geometry | per-axis commands, plus roster-wide stop and e-stop |
| Demo | `demo_dual_motor` | `demo_n_motor` (new). `demo_single_motor` stays, as the simplest form |
| Cogs | 3 | **N + 1**: 2, 3 or 4 |
| Beyond it | — | **more P2s over serial**, not more motors per P2 |

Two consequences fall straight out of this and make the design smaller:

- **Each shape is one motor type by construction.** All instances of an object share one compiled image and
  one DAT, and `init()` copies the motor-type tables into that shared driver image (PL-18,
  `p2kbSpin2ObjectImageDedup`). A mixed-type roster would corrupt it. Since 6.5″ never appears in the N-motor
  shape and Doco never drives the platform, no roster is ever mixed. The constraint costs nothing.
- **Scaling past 3 is a system concern, not an object concern.** Multiple P2s over the existing serial path
  (`isp_steering_serial` / `isp_host_serial` / `isp_queue_serial`). Nothing in the front cog changes for it.

### 1.1 What caps a single P2 at 3 (DERIVED from the code and the enums)

| Cap | Value | Why |
|---|---|---|
| **Pin groups** | **3** | Legal bases are `PINS_P0_P15`, `PINS_P8_P23`, `PINS_P16_P31`, `PINS_P32_P47`, `PINS_P40_P55`, and adjacent pairs overlap — `claimPinBase()` refuses them. The only non-overlapping triples are {P0_P15, P16_P31, P32_P47} and {P0_P15, P16_P31, P40_P55}. There is no `PINS_P48_P63`. |
| **Cogs** | 6 | N drivers + 1 front + the application, out of 8. Never reached: pins bind first. |

So Stephen's "1 to 3 motors per P2" is exactly what the hardware and the pin-base enum already allow. Three
is the ceiling, and the design does not need to reach past it.

## 2. What the source does today (DERIVED, read 2026-09-15 at `65bda4b`)

### 2.1 Cog cost

| Configuration | Cogs | Which |
|---|---|---|
| Two wheels | **3** | two driver cogs + the steering object's `taskPostionSense()` cog |
| One motor | **1 or 2** | one driver cog, + that object's sense cog **only if** the caller calls `startSenseCog()` |

`DRIVE-OBJECTS.md` still says "two cogs" — stale for two wheels. A single-motor caller who never calls
`startSenseCog()` silently gets no distance or time stops.

### 2.2 The defect the ownership ruling fixes

Two writers, no owner:

| Shared value | Caller's cog writes | Sense cog writes |
|---|---|---|
| `targetIncre` (drive command, bit 31 = sync) | `driveAtPower*()`, `stopMotor()`, `emergencyCutoff()` | distance and time stops |
| `e_stop` | `emergencyCutoff()`, `clearEmergency()` | the e-stop auto-clear (S-4) |
| `motorStopHallTicks`, `motorStopMSecs` | `stopAfter*()` | cleared when a limit fires |
| `posTrkHallTicks`, the hall window | `resetTracking()` | `+=` every pass |

DERIVED consequences, none yet observed: a stop landing between the two sync writes and `cogatn` strands an
ATN and releases the *next* synchronized command early; `resetTracking()` loses counts; `SyncStatus()` can
hang the application while a driver is in `DCS_ESTOP` (PL-49 F-6); stop limits are checked at 8 Hz, so a stop
is up to 125 ms late before it is commanded — about 294 mm at top speed (C-3).

### 2.3 The steering object already forwards the motor API — by per-side names

Verified by reading the file in full: the whole product API is forwarded in aggregate form (control, config,
status), the motor enums are re-exported as `CON` aliases, and about twenty `testLeft*` / `testRight*` pairs
cover the TEST-USE surface. Only `getRawHallTicks()` and `getBoardType()` are product-API gaps, reachable
through TEST-USE.

**The gap is the shape, not the coverage.** The side is baked into each method name, so N motors would need N
names. The roster API (§4) is the fix, and it is what gives the N-motor shape its interface.

## 3. The front cog

### 3.1 Ownership

- The front cog is the **only** writer of `targetIncre`, `e_stop`, the stop limits and the tracking state, and
  the only caller of `cogatn` and the sync wait.
- Public methods validate on the caller's cog, **post** a request, and wait, bounded, for the front cog to
  take it. Getters read status longs directly; a read needs no owner.
- **One request slot per calling cog** (`LONG reqCmd[8]`, indexed by `COGID()`), sequence written last. No
  lock, so none can leak (PL-41). Requests from one cog apply in order.
- **Bound** `REQ_ACK_TIMEOUT_MS` = 20 (twenty front passes). The front cog has no unbounded step, so it is
  never reached while the front cog runs. If the front cog is not running, the request is dropped and the
  method returns at once — today's behaviour when the driver is not running.

### 3.2 The loop

One Spin2 method on its own cog, paced on an absolute `getct()` schedule:

| Every pass (1 ms, `FRONT_LOOP_HZ` = 1000) | Every 125th pass (8 Hz, unchanged) |
|---|---|
| take and apply posted requests | `updateWindowAccumulators()` per motor, so rpm keeps its 1 s window |
| check every owned motor's time and distance limits; command the stops that fire | |
| the e-stop auto-clear, timed in passes (S-4 behaviour unchanged) | |

- **C-3 built in:** a stop is commanded within one front pass (1 ms) and taken within one drive pass (522.7 µs,
  PL-50): the bound falls from 125 ms to about 1.5 ms, under one tick at top speed.
- **Not fixed by it:** the ramp-down distance (C-4: 74–76 ticks from half speed; PL-58). Afterwards the
  overshoot should equal the C-4 ramp distance plus at most one tick; more is a finding.
- **Cost:** today's body is about 9 µs for two motors; the slot scan adds a few long reads. 1 ms leaves ample
  slack for three motors, and late passes are counted, not accumulated.

### 3.3 Synchronized drive, e-stop, shutdown

- **Synchronized drive:** the front cog writes every owned motor's command with the sync bit, issues one
  `cogatn` over the roster mask, and waits for the bits to clear, bounded to 20 drive passes.
- **While any owned driver is in `DCS_ESTOP`, a drive command is refused and never written.** The driver
  ignores requests while e-stopped, so a written command would sit stale and then drive on `clearEmergency()`.
  Refusing removes F-6's hang and that surprise together. Reported on `DBGCH_ERROR` until PL-47 lands.
- **Lockstep start unchanged:** every driver starts with `sync: true` and is released by one `cogatn(cogmask)`
  on the caller's cog, before the front cog exists — no second writer can exist yet. The driving shape still
  applies `forwardIsReverse()` to the right wheel.
- **Cooperative shutdown (PL-41):** `stop()` posts EXIT; the front cog finishes its pass and acknowledges;
  then the cogs stop. Without an acknowledgement inside the bound it stops anyway and says so.

## 4. The roster

The front cog services **a roster of motors**. One implementation serves both shapes.

- **Per-motor object** (`isp_bldc_motor`): one motor, its driver cog, its state, and one internal service
  routine the owner calls once per pass. It owns no cog beyond its driver when an owner manages it.
- **Owner** declares the roster and runs the one front cog:
  ```
  OBJ
      motor[MOTOR_COUNT] : "isp_bldc_motor"      ' p2kbSpin2KwOBJ: name[N] : "file"
  ```
- **The N-motor API is indexed:** `driveAtPower(motorIdx, power)`, `getStatus(motorIdx)`,
  `stopAfterDistance(motorIdx, …)`, plus roster-wide `stopAll()`, `emergencyCutoff()` and one synchronized
  drive across the roster.
- **The driving shape keeps every name it has today.** `isp_steering_2wheel` is the 2-motor specialization:
  left/right pairs, `driveDirection()`, the turn geometry, the right-wheel reversal. No user of it sees a
  change.
- **`isp_bldc_motor` used standalone** stays valid: it keeps a small loop of its own that calls the same
  per-motor service routine. The per-motor work exists once; only the loop shell is duplicated, a few lines.
  (It cannot include the owner — that would be circular.)

## 5. Invariants this construction guarantees

1. Every driver control long has exactly one writer: the front cog.
2. No library wait is unbounded.
3. No lock is allocated, so none can leak.
4. A stop is commanded within one front pass of its limit.
5. The cog cost is fixed at `start()`: **N + 1**.
6. The PASM driver and its shared-memory ABI are untouched; the request slots are new VAR, outside the
   PASM-addressed runs.
7. No roster mixes motor types (§1).

## 6. Certification at the next visit (each prints PASS / FAIL / NOMEAS)

| Mechanism | Test |
|---|---|
| Fixed cog count | free cogs before and after `start()`: N + 1 used, all returned by `stop()` |
| Lockstep | every driver leaves `DCS_STOPPED` within one drive pass of the others, at start and on each synchronized drive |
| Stop latency (C-3) | `stopAfterDistance()` at half speed: ticks from limit crossing to `DCS_SPIN_DN` ≤ 1; overshoot ≤ the C-4 ramp distance + 1 |
| No hang while e-stopped (F-6) | `emergencyCutoff()`, then a drive returns within 50 ms; nothing moves after `clearEmergency()` |
| Ordered stop during a drive | a time limit firing during a drive issued from another cog: every motor ends in the same state |
| Cooperative shutdown | `stop()` acknowledged; no truncated debug line in the log |
| Tracking reset | `resetTracking()` at speed, then `getDistance()` counts only motion after the reset |

The N-motor shape is certified on the bench at roster 1 and roster 2 (the rig has two boards). Roster 3 is
compile-certified and left to the first 3-motor rig.

## 7. The demo set, and what it costs the gate

**Three demos, additive (STEPHEN 2026-09-15).** Each shows one form, and nothing existing is renamed:

| Demo | Object it shows | Cogs |
|---|---|---|
| `demo_single_motor` (unchanged) | `isp_bldc_motor` standalone — the simplest form | 2 |
| `demo_n_motor` (**new**) | the roster owner, 1 to 3 Doco motors | N + 1 |
| `demo_dual_motor` (unchanged) | `isp_steering_2wheel`, the driving platform | 3 |

Consequences, all mechanical:

- **`tools/build-check.sh` certifies release demos by name** (`RELEASE_TOPS="demo_single_motor
  demo_dual_motor"`). The new demo joins that list, so the gate certifies three.
- **The gate's block classifier has to learn the new shape.** It reads each config block and labels it
  `single` (`ONLY_MOTOR_BASE`) or `dual` (`LEFT_MOTOR_BASE`); anything else is `other` and is **skipped**. An
  N-motor block would therefore never be activated, `demo_n_motor` would compile under no config, and rule 2
  ("every top compiles under at least one config") would fail the gate. The classifier gains an `nmotor` kind.
- **The gate prints a file count**, and this adds files to `src/`. That figure and every `DOCs/analyses/`
  reference to it move together («#3515» item 8).
- **The README demo table and `DEVELOP.md`** gain the third form rather than editing the first.

**Open for Stephen, not blocking:** the user-config block for the N-motor shape. Today a block declares
`ONLY_MOTOR_BASE`, or `LEFT_MOTOR_BASE` + `RIGHT_MOTOR_BASE`. The N-motor shape needs a count plus a base and
board type per motor. Proposed: `MOTOR_COUNT` with `MOTOR_1_BASE` … `MOTOR_3_BASE` and `MOTOR_1_BOARD_TYPE` …,
added as new example blocks so the existing six are untouched and every current user's config still compiles.
`WHEEL_DIA_IN_INCH` stays meaningful only where wheels turn. Proposed name for the owner object:
`isp_bldc_motor_group.spin2`.

## 8. Out of scope

The PASM driver, its ramps and fault logic; PL-47's error contract; S-4's e-stop auto-clear; PL-66; a single
PASM cog driving two motors; a new pin-base enum value; the multi-P2 serial protocol for 6 or 9 motors.

## 9. Documentation consequences (phase 2)

- **README §DEMOs table** — five rows today (`demo_single_motor`, `demo_dual_motor`, `demo_dual_motor_hdmi`,
  `demo_dual_motor_rc`, `demo_dual_motor_rc_hdmi`); it gains a sixth for `demo_n_motor`.
- **The "two objects / two cogs" paragraph, in three places.** README:181-185 says *"There are two objects in
  our motor control system"* and *"The drive subsystem currently uses two cogs, one for each motor and a third
  cog for active tracking"*; `DRIVE-OBJECTS.md`:10-14 and `DRIVE-OBJECTS-SERIAL.md`:10 carry the same block
  (it is one of PL-7's duplicated-prose pairs). All copies become three objects and **N + 1** cogs, and PL-7's
  rule applies: one canonical copy, links from the others.
- **README:183 is superseded.** It tells a reader wanting three motors to *"create your own better-suited
  steering object"*. That is exactly what the roster owner now provides.
- **`images/objects-cogs.png`** (README's System Diagram) shows today's cog structure and goes stale. It is a
  generated image, so regenerating it is Stephen's, like `isp_bldc_motor.txt`; otherwise it is recorded as
  knowingly stale.
- `DRIVE-OBJECTS.md`: the roster API table for the new owner object.
- `DEVELOP.md`: all three forms; the single-motor example no longer needs `startSenseCog()`.
- README 6.0.0 block: the fixed cog count, stops within about 1 ms of their limit, and a drive while
  e-stopped no longer hanging.
- `tools/build-check.sh`: `RELEASE_TOPS` gains the new demo, and the block classifier gains the `nmotor` kind.
