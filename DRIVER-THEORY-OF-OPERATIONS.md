# P2-BLDC-Motor-Control — Driver Theory of Operations

How the BLDC driver actually works: the cog topology, the Spin2↔PASM2 contract, the
commutation and PWM loop, and the invariants that must hold for any of it to be correct.

This is a *developer reference*. For the public method tables see
[DRIVE-OBJECTS.md](DRIVE-OBJECTS.md); for wiring your own project up see
[DEVELOP.md](DEVELOP.md); for adding a motor see [ADDING_MOTOR.md](ADDING_MOTOR.md). How the
6.5″ motor itself behaves under this driver — its hall zero, the lead it wants, its speed and
current envelope — is in
[the 6.5″ motor technical manual](DOCs/MOTOR-6.5IN-TECHNICAL-MANUAL.md).

It describes `src/isp_bldc_motor.spin2` and `src/isp_steering_2wheel.spin2` as of v6.0.0.

---

## 1. The shape of the thing

The drive subsystem is **not** a call-and-return motor API. It is a set of cogs that run
continuously, plus blocks of shared hub memory. Motion changes because a driver cog notices a
changed value on its next pass.

What a public method does depends on its kind:

- **Command methods** validate their arguments on the caller's cog, post a request to the
  **front cog**, and wait — bounded, 20 ms — for its answer. They return that answer as a
  status (`NO_ERROR` or an `ERR_*` code) and record it for `getError()`.
- **Status methods** read the shared values directly and return at once.

### Cog topology

```
                    ┌─────────────────────────────────────────┐
   user app cog ───▶│ isp_steering_2wheel  (optional layer)   │   ← Spin2 objects
                    └───────────┬─────────────────┬───────────┘     (no cog of their own)
                    ┌───────────▼──────┐ ┌────────▼─────────┐
                    │ isp_bldc_motor   │ │ isp_bldc_motor   │
                    │ (left instance)  │ │ (right instance) │
                    └───────────┬──────┘ └────────┬─────────┘
              ╔═════════════════▼═══╗ ╔═══════════▼═════════╗
              ║ PASM2 driver cog    ║ ║ PASM2 driver cog    ║   ← 1 cog per motor
              ║ 44 kHz frame loop   ║ ║ 44 kHz frame loop   ║
              ║ 1,913 Hz drive pass ║ ║ 1,913 Hz drive pass ║
              ╚═════════════════════╝ ╚═════════════════════╝
              ╔═══════════════════════════════════════════════╗
              ║ front cog (Spin2) — 1 kHz                     ║   ← 1 cog, serving every
              ║ requests · tracking · limits · protection     ║     motor it owns
              ╚═══════════════════════════════════════════════╝
```

| Configuration | Cogs | Who starts what |
|---|---|---|
| Single motor, `isp_bldc_motor` direct | **2** | `start()` launches the driver and the motor's own front cog |
| Two motors, `isp_steering_2wheel` | **3** | `start()` launches both drivers with `startOwned()` (no front cog of their own) and one steering front cog that serves both |

`startSenseCog()` starts nothing. It returns the front cog's id and exists so 5.x programs
still compile.

### The front cog owns the drive

The front cog is the **only writer** of every driver command (`targetIncre`), of `e_stop`, of
the stop limits and of the tracking, and the only caller of `cogatn` once running. Every other
cog reaches the drive by posting a request. That single-writer rule is what lets two cogs of
the user's application command the same motor without racing.

**Request slots.** Each motor instance (and the steering object) holds one request slot per
P2 cog, indexed by `COGID()`. A caller withdraws its slot, writes the request and its
arguments, then publishes a fresh sequence number *last*. The front cog copies the slot,
checks the sequence did not change under it, applies the request, writes the status, then
writes the answered sequence *last*. Every long has exactly one writer. Each pass the front
cog takes emergency stops first, then stops, then everything else in slot order, and allows
at most one request that must wait on the driver per pass.

**Errors.** Each instance also holds one error slot per cog. The first error a cog incurs is
kept until that cog calls `getError()`; later errors do not replace it.

---

## 2. The Spin2 ↔ PASM2 contract

This is the most fragile part of the codebase and the part most likely to be broken by an
innocent-looking edit.

The PASM2 driver does not call Spin2 and Spin2 does not call PASM2. They communicate
**only** through hub memory, addressed by the driver as raw offsets from a single pointer.
**Declaration order in the `VAR` blocks is the ABI.**

### The pointer walk

`coginit(NEWCOG, @driver, @pinbase)` hands the cog `@pinbase` in `ptra`. The driver reads the
base pin and the parameter-block pointer, and steps past `targetAngle` and `targetIncre`, so
`ptra` then points at the status block:

| Region | Address | Direction | Longs |
|---|---|---|---|
| `targetAngle` | `ptra[-2]` | Spin2 → driver (test only) | 1 |
| `targetIncre` | `ptra[-1]` | front cog ↔ driver (command and sync handshake) | 1 |
| Status block, `drive_u` … `drv_stop_fp` | `ptra[0..23]` | driver → Spin2, every frame | `DRVR_STATUS_LONGS_COUNT` = 24 |
| `fault` | `ptra[24]` | driver → Spin2, on fault only | 1 |
| Parameter block, `offset_fwd` … `sense_zero` | `params_ptr_` | Spin2 → driver, every frame | `DRVR_PARAMS_LONGS_COUNT` = 27 |

The launch quartet's own length is `DRVR_LAUNCH_LONGS_COUNT` = 4. The counts are as of
DRIVER_REV 39; the constants in `isp_bldc_motor.spin2` are the authority, not this page.

### The invariants

**Invariant 1 — the launch quartet is ordered and adjacent.** `pinbase`, `params_ptr`,
`targetAngle`, `targetIncre` are four contiguous longs, in that order, immediately before the
status block.

**Invariant 2 — the status block is 24 contiguous longs, and `fault` is the next one.**

| Index | Long | Meaning |
|---|---|---|
| 0–2 | `drive_u`, `drive_v`, `drive_w` | the three phase levels written this frame |
| 3–6 | `sense_u_mV`, `sense_v_mV`, `sense_w_mV`, `sense_i_mV` | the three phase voltages and the DC-link current reading, mV |
| 7 | `hall` | the hall code |
| 8 | `pos` | the signed hall-tick position (§4) |
| 9 | `duty` | the applied duty |
| 10 | `err` | the commanded angle less the rotor's, 256ths of a cycle |
| 11 | `loop_ticks` | the frame loop's duration, clock ticks |
| 12 | `loop_ctcks` | the drive pass's duration, clock ticks |
| 13 | `drv_state` | the `DCS_*` state |
| 14 | `hall_missed` | hall changes with no countable step, since driver start |
| 15 | `hall_illegal` | entries into `%000` (low word) and `%111` (high word), since driver start |
| 16 | `drv_incr_now` | the field's angle increment per drive pass |
| 17 | `lag_held` | passes on which the lag limiter withheld the field's advance (unbounded) |
| 18 | `duty_capped` | passes on which the duty demand exceeded the cap (unbounded) |
| 19 | `fault_resyncs` | faults answered by a re-sync and a controlled stop (unbounded) |
| 20 | `foldback_frames` | frames the current fold-back lowered the duty (unbounded) |
| 21 | `drv_accel_now` | the ramp generator's acceleration: the signed change of `drv_incr_now` per pass |
| 22 | `drv_stop_passes` | the driver's stop plan: drive passes to rest for a stop written now (DRIVER_REV 39) |
| 23 | `drv_stop_fp` | the driver's stop plan: the field's travel to rest, 1/256 hall tick (DRIVER_REV 39) |
| 24 | `fault` | ← immediately after the run; written TRUE on every fault |

The driver writes them in one burst (`setq #DRVR_STATUS_LONGS_COUNT-1` / `wrlong drive_u_,
ptra`) and reports a fault by writing `ptra[DRVR_STATUS_LONGS_COUNT]`. Since `drv_accel_now`
is no longer the run's last long, a reader of the raw run (a bench harness) finds the three
appended longs by the index constants `DRVR_STATUS_ACCEL_NOW_IDX` (21),
`DRVR_STATUS_STOP_PASSES_IDX` (22) and `DRVR_STATUS_STOP_FP_IDX` (23), not by counting.

**Invariant 3 — the parameter block is 27 contiguous longs.**

| # | Long | Meaning |
|---|---|---|
| 0 | `offset_fwd` | commutation offset applied to negative increments |
| 1 | `offset_rev` | commutation offset applied to positive increments |
| 2 | `duty_min` | the duty floor |
| 3 | `duty_max` | the duty ceiling |
| 4 | `servo_shift` | the trim accumulator's shift |
| 5 | `ff_ceiling` | the motor's back-EMF line the feedforward scales by (not a speed ceiling) |
| 6 | `dead_gap` | the dead gap between a half-bridge's two sides |
| 7 | `accel_dn` | the slow-down acceleration limit (was `ramp_down`) |
| 8 | `cfg_ctcks` | the drive pass's 500 µs deadline, clock ticks |
| 9 | `stop_mode` | `SM_FLOAT` or `SM_BRAKE` |
| 10 | `e_stop` | `ES_OFF`, or the kind of emergency stop latched |
| 11 | `accel_up` | the speed-up acceleration limit (was `ramp_max`) |
| 12 | `jerk_up` | the speed-up jerk (was `ramp_min`) |
| 13 | `jerk_dn` | the slow-down jerk (was `ramp_inc`) |
| 14 | `i_limit_k` | the current-limit threshold factor |
| 15 | `duty_floor` | the duty floor for the phase-current estimate |
| 16 | `hold_duty` | the duty applied at rest |
| 17 | `hold_short` | TRUE once a braked hold at rest has handed off to the phase short |
| 18 | `fault_mode` | `FR_SHIPPED` or `FR_GRADED`, the response to a position fault |
| 19 | `brake_on` | the braking bridge's shorted frames per brake period |
| 20 | `probe_phase` | the phase the start-time continuity probe drives at rest |
| 21 | `force_seq` | test use: advanced to force one fault |
| 22 | `fault_clr` | advanced by the front cog to clear `DCS_FAULTED` |
| 23 | `probe_sink` | test use: the phase whose low side the probe holds on |
| 24 | `probe_y` | test use: the probed phase's high-side duty |
| 25 | `drv_release` | TRUE asks the driver to release the bridge and park; only `stop()` writes it |
| 26 | `sense_zero` | the DC-link rest offset the fold-back nets out, mV — the last long |

Read every frame by `setq #DRVR_PARAMS_LONGS_COUNT-1` / `rdlong params_ptr_+1, params_ptr_`.
`frame_cnt` sits after the block and is deliberately outside it.

**Append only.** A new long goes at the end of its run — after `drv_stop_fp` (so `fault` moves
up one) or after `sense_zero`. Reordering, inserting or removing a long anywhere else silently
corrupts the driver.

**Three places must agree** for each block, and change together: the Spin2 `VAR` order, the
PASM `res` register block (`offset_fwd_` … `sense_zero_`, `drive_u_` … `stop_fp_`), and the
count constant (with, for the status run, its index constants). **`start()` checks the layout
before it launches anything** (`isAbiLayoutValid()`): the launch quartet must end where
`drive_u` begins, `fault` must sit `DRVR_STATUS_LONGS_COUNT` longs after `drive_u`,
`drv_accel_now`, `drv_stop_passes` and `drv_stop_fp` must sit at their `DRVR_STATUS_*_IDX`
indexes with `drv_stop_fp` the run's last long, `sense_zero` must be the parameter run's
`DRVR_PARAMS_LONGS_COUNT`-th long, and every Spin2-only array — the error slots, the request
slots, the front cog's stack, the rpm window, its in-flight request — must lie outside the runs. A mismatch refuses the start with `ERR_ABI_MISMATCH`. The check sees
offsets and sizes, not meaning: two longs swapped inside a run still pass it.

### `targetIncre` — a signed field with a stolen bit

`targetIncre` carries two things: bit 31 is a **sync** flag, and bits 30..0 are the signed
increment. The driver restores the sign with `SIGNX #30`. When the sync flag is set, the driver
keeps its previous target until it sees ATN, then clears the flag and writes the value back as
its acknowledgement. The steering layer uses that to start both wheels in the same drive pass.

**Invariant 4 — the increment must satisfy |value| < 2³⁰ (1,073,741,823).** A magnitude
that reaches bit 30 is read back as negative, and the motor runs the wrong way. The largest
value in the current tables is 545,000,000 (DocoEng, 11.1 V); the largest 6.5″ value is
214,000,000 at 24 V.

### One-shot DAT initialization

`sync_required`, the per-motor tables (§4) and the two LUT code pointers (`lutCodePtr`, the
start image; `planCodePtr`, the run image) live in the driver's
`DAT` image, written by `init()` **before** `coginit`. The cog receives its own copy at load
time; writing them afterwards has no effect on a running driver.

---

## 3. Startup sequence

```
start(basePin, voltage, detectMode)                   (steering: startOwned() per wheel)
  ├─ validate pin group, voltage, detect mode         → ERR_BAD_* on failure
  ├─ isAbiLayoutValid()                               → ERR_ABI_MISMATCH
  ├─ bHallDeltaTablesValid(): every motor's steps     → ERR_BAD_MOTOR_TABLE
  ├─ stop any driver and front cog this instance already runs
  ├─ claim the pin group                              → ERR_PIN_GROUP_IN_USE
  ├─ init(...)
  │    ├─ derive tick constants from CLKFREQ
  │    ├─ getBoardType()                              ← detect the board revision
  │    ├─ select the per-motor tables and offsets     ← copied (the deltas packed) into the driver image
  │    ├─ compute frame_cnt, dead_gap, duty_min/max
  │    └─ confgurePowerLimits(voltage)                ← the power → increment table
  ├─ refuse an undetected board under BRD_AUTO_DET    → ERR_BOARD_NOT_DETECTED
  ├─ coginit(NEWCOG, @driver, @pinbase)               → ERR_NO_FREE_COG
  ├─ start the front cog, wait for its first pass     → ERR_NO_RESPONSE
  └─ capture the current-sense rest zero (~1 s)       ← nothing has driven the motor yet
```

Inside the driver cog: load the start sequence into LUT RAM and run it there, configure the
six PWM smart pins (low sides inverted), calibrate the four ADC channels against GIO and VIO,
compute per-channel scaling with the CORDIC, then — if `sync_required` — `waitatn` until
released. The start sequence's last act is `loadOverlay`, which loads the LUT run image over
the now-spent start image (§4) and enters the drive loop.

**Two wheels start in lockstep.** The steering object starts both drivers parked, reverses
the right wheel (`forwardIsReverse()`, since the motors face opposite ways), and releases
both with one `cogatn(cogmask)` from the caller's cog — before its front cog exists, so no
second caller of `cogatn` can exist yet. It then samples both wheels' rest zero together and
starts its front cog.

**Board revision detection** charges a capacitor on `pinbase+4`, floats the pin, and counts
how many of 500 reads still read high:

| Sum | Meaning |
|---|---|
| `0` | Rev A (a 1 kΩ pulldown holds it low) |
| ~40–180 | Rev B (the capacitor discharging) |
| `>250` | no board attached |

The detected revision sets the current-sense scale (Rev A 5 mV/A, Rev B 150 mV/A) and with it
the current limit. That is why `start()` refuses a board it cannot detect: without the
revision there is no current limit. `BRD_REV_A` / `BRD_REV_B` force one.

---

## 4. The driver cog

The driver runs two nested loops.

- **The frame loop** runs once per PWM frame, **44 kHz (22.7 µs)**: read the ADCs, compute
  and write the three phase levels, read the halls, compute the error, check for a fault,
  apply the current limit, and servo the duty. It writes the 24-long status block every frame.
  On the nine frames after each drive pass it also works out the stop plan, a third of a plan
  a frame, in the slack after that frame's status write (below).
- **The drive pass** runs every **23 frames, about 1,913 times a second (522.7 µs)**: take
  the command, advance the ramp, and advance the commanded angle. `cfg_ctcks` is a 500 µs
  deadline, but it is tested only at frame boundaries, so the pass runs on the 23rd frame.
  Every per-pass rate — the increments, the ramps — is per 522.7 µs.

### The drive pass

```
1. e_stop set?              → short the bridge, clear the running state, state := DCS_ESTOP, exit
2. read targetIncre         → sync handshake, sign restore
3. target is 0?             → start the ramp down (or, if stopped, re-apply the stop mode)
4. target changed?          → taken in EVERY state; a faulted motor is cleared first
5. jerkStep: move the acceleration toward its limit by at most one jerk step, then
   drv_incr by the acceleration, landing exactly on the target; if the field is
   ahead of the rotor by LAG_SOFT (112.5°) the way the acceleration pushes, the
   acceleration eases toward 0 by one jerk step instead
6. advance angle_ by drv_incr, unless the rotor trails by LAG_HOLD (140.6°):
   then the field is held, lag_held counts it, and drv_incr decays toward the
   rate the rotor achieves (1/64 per held pass)
7. compute the duty feedforward for this pass's speed
```

**The ramp is jerk-limited** (DRIVER_REV 38, PL-160). One trajectory generator, `jerkStep` (in
the LUT), runs every pass the motor is not at rest, whatever the state, and takes every command
as it stands; the states are now only what it reports. Four parameter longs drive it:
`accel_up` and `accel_dn`, the acceleration limits (change of `drv_incr` per pass), and
`jerk_up` and `jerk_dn`, each its limit spread over `RAMP_TAU_MS` (250 ms). The acceleration
rises by at most a jerk a pass to its limit, and ramps back out to land exactly on the target;
a limit lowered mid-ramp is unwound at the larger jerk. A reversal passes through zero in one
continuous ramp: only a start from `DCS_STOPPED` seeds the field from the halls. The
generator's present acceleration is the status long `drv_accel_now`. Built-in limits:
1,000 mm/s² up and 1,470 mm/s² down (33,958 and 49,918 on the 6.5″ wheel), provisional.
`setAcceleration()` and `setDeceleration()` set the limits from mm/s²; `setRampingValues()`
sets them raw, and its `minRamp` and `incRamp` have no effect.

Steps 5 and 6 are why the driver seldom faults any more: the field never gets far enough
ahead of the rotor to trip the 175.8° fault test unless the rotor is truly lost.

### The stop plan

**The driver plans its own stop** (DRIVER_REV 39, PL-161), so no front cog computes one.
After each drive pass, `planStage` runs the jerk-limited stop's closed form in integers
(`planA` … `planC`: 64-bit sums, `QSQRT` roots, no float), a third of a plan a frame over the
next nine frames so that it fits at 160 MHz. It plans from the pass's own increment and
acceleration, and from both ends of the accelerations the next pass could reach under any
command, so the plan holds whether the stop is taken by the next pass or, if that pass has
already read its command, by the one after. The largest passes-to-rest and the largest travel
of the three are published as `drv_stop_passes` and `drv_stop_fp`, by the status write of the
tenth frame after the pass (about 230 µs).

### Cog and LUT memory

Registers live in cog RAM, because instruction operands reach only cog RAM; code may live in
the LUT, which runs at cog speed. The `fit` comments in the source, read from the compiler at
DRIVER_REV 45, give the budget:

| Memory | Holds | Used |
|---|---|---|
| Cog RAM | the frame loop, the drive pass, the routines both phases share (`wait4adc`, `checkstop`, `initAngleFmHall`, `countIllegal`), `planFp` and `planCorner`, the constants and tables, and every register | **441 of 496** |
| LUT, start image | `lutCodeStart` $200 … `lutCodeEnd` $290: the start sequence and `driveinit` | 144 (hidden under the run image) |
| LUT, run image | `runCodeStart` $200 … `runCodeEnd` $3C9: `gettgtincr`, `passEnd`/`feedForward`, `holdDecay`, `jerkStep`, the bridge routines, `driverRelease`, `xStar`, `run`, `planStage` and the planner's core (`planA` … `rampOut`) | **457 of 512** |

The LUT holds **two images at the same addresses, one after the other** (DRIVER_REV 42). The
entry code block-loads the start image from `lutCodePtr` and runs it. Its last act is
`loadOverlay`, in cog RAM, which block-loads the run image from `planCodePtr` over it and
enters the drive loop. The two are partitioned by call graph: the start image calls only cog
RAM and its own `driveinit`, and nothing in cog RAM or the run image calls into the start
image, so no run-image address is reached before the load and no start-image address after
it. `countIllegal`, which both phases call, lives in cog RAM for that reason. So LUT use is the
larger of the two images, and the start image costs none. The load happens once, after the ATN
release: both wheels load the same 457 longs, so their lockstep is unchanged. Until
DRIVER_REV 41 the LUT held 507 resident longs, and only the planner's 126-long core was an
overlay over the spent start sequence.

DRIVER_REV 41 also made 21 cog longs do double duty. The entry code, `loadOverlay`, eight
start-only constants, `adc_modes` and `calibPeriod` are dead once the start sequence has run,
and each is also the home of a register only the drive loop uses (`pl_v` … `sp_F`, `jrk_e`
… `jrk_lim`).

DRIVER_REV 43 took 15 more cog longs out of the frame loop and the drive pass, each by an exact
instruction-level identity: the phase levels' minimum and maximum by `FLES`/`FGES`, the centre
bias and the dead gap folded into the one offset each level is moved by, the fold-back compare
as `sense_i > t + sense_zero` (no `fold_net` register), `NEGC` for the signed lag, `TJZ` for the
e-stop and duty-ceiling tests, and `ADDCT1` on `ctrlSrtTix` itself (no `ctrlEndTix`). The pins,
the hub writes and every live register are unchanged.

DRIVER_REV 44 took 20 more. The driver's `deltas` table is 8 longs of nibbles, not 64 bytes:
nibble `new` of long `old`, read by `ALTGN`/`GETNIB`. Each nibble carries the transition's
step (bits 1:0, −1/0/+1) and its integrity event: bit 2 a missed transition, bit 3 an entry
into `%000` or `%111`. Both events are fixed by the pair and its step, so `init()` works them
out once (`packHallDeltas()`), from the motor's byte table (`deltas65`, `deltas4k`, still the
authoring format) with any test hall swap applied. The frame then needs 8 instructions where
it had 20. A step outside −1..+1 cannot be packed, so every start checks every motor's byte
table first and refuses a bad one with `ERR_BAD_MOTOR_TABLE` (`bHallDeltaTablesValid()`).

DRIVER_REV 45 took 8 cog longs and 19 run-image longs out of the stop planner. `planStage`
runs one parameterised part A, B or C for all three plans (the stop taken at the next pass, and
the two ends of the take pass) and one fold. It adds the take pass only when the plan has one.
`plan_stage` keeps its values 1 to 9, so each stage runs on the same frame as before and the
published pair is unchanged. `run`, `planSat`, `planFp` and `planCorner` lost redundant
instructions, and `DECOD`/`BMASK` replace `##` constants.

### The frame loop — commutation

The three hall lines are read in **one instruction**, so all three bits come from the same
instant. The 3-bit code and the previous one, `(old << 3) | new`, select one 4-bit entry of
the driver's `deltas` table: nibble `new` of long `old` (`ALTGN`/`GETNIB`). Bits 1:0 are the
position step for that transition, −1, 0 or +1. This is what makes `pos` a signed,
direction-aware tick counter. Bit 2 marks a missed transition, a change between two legal
codes with no step (`hall_missed`). Bit 3 marks an entry into `%000` or `%111`, which is
counted by kind (`hall_illegal`, low and high words). A change out of `%000` or `%111` counts
nothing, since it was counted on entry. Both marks depend only on the transition and its step,
so `init()` sets them once (`packHallDeltas()`) and the frame only tests them. The per-motor
byte tables below are the source `init()` packs from; since DRIVER_REV 44 the driver no longer
holds them as bytes.

The hall code also indexes `hall_angles` for the rotor's angle within the hall cycle; bit 3 of
the index selects the forward or reverse half. Per-motor tables are chosen in `init()`:

| Motor | Hall ticks/rev | Degrees/tick | Angle table | Delta table |
|---|---|---|---|---|
| 6.5″ hub (`MOTR_6_5_INCH`) | 90 | 4° | `hltbAngles` | `deltas65` |
| DocoEng 4 kRPM (`MOTR_DOCO_4KRPM`) | 24 | 15° | `hltbAngl4k` | `deltas4k` |

The error is `err_ = angle_ − (hall_angle + offset)`, in 256ths of an electrical cycle, with
`offset_fwd` applied to negative increments and `offset_rev` to positive ones. **For the 6.5″
motor the front cog rewrites the offset pair as speed changes**: a hall zero of −4° plus or
minus a lead taken from a four-point table against the increment (§5). The DocoEng motor keeps
one fixed pair.

### The frame loop — duty

The applied duty is a **feedforward** from the field's speed plus an integral **trim**:

- **Feedforward**: `|drv_incr| × duty_max ÷ ff_ceiling`, where `ff_ceiling` is the motor's
  back-EMF line (for the 6.5″ motor, measured at 18.5 V and scaled by voltage). It gives the
  duty a speed needs before the error has to ask for it.
- **Trim**: each frame adds `(|err_| − SERVO_SETPOINT) × (duty >> 4)` to an accumulator,
  applied shifted right by `servo_shift`. The setpoint is 48 counts (67.5°). It is symmetric
  and untruncated, so it holds a point; its gain scales with duty, so it follows the rotor's
  stiffness and does not hunt at low speed.
- **Limits**: duty is clamped to `duty_min`..`duty_max`, with an extra ceiling during a ramp
  down that scales with speed, lifted whenever the rotor trails by `LAG_SOFT`. Every clamp
  re-derives the accumulator from what was applied, so the trim never winds up.

**The setpoint is never the knob for the lead.** The offset and the setpoint add; the lead is
carried by the offset.

### The frame loop — current limit

Each frame the bridge is driven, the DC-link current reading less `sense_zero` (the rest zero
`start()` measured), never below 0, is compared with a threshold scaled from the phase
limit by the modulation depth (`duty × i_limit_k >> 16`, with duty floored at
`duty_floor`). At or above it, duty folds back about 1.6 % that frame and the trim is
skipped. `i_limit_k` holds the 40 A peak limit, or the 27 A continuous limit while the front
cog has derated it (§5).

### PWM, the phase levels and the dead gap

Triangle PWM at **44 kHz** (`PWM_RATE_IN_HZ`), one ADC sample per frame. The three phase
levels are `duty × sin(angle_ + 0°/120°/240°)` from the CORDIC, then **re-centred** on the
midpoint of their largest and smallest value, which lets the amplitude reach `(F − dead_gap) ÷
√3`. `duty_max` is derived from exactly that bound, less a 4-count guard, so the PWM cannot
clip: 27,648 at 270 MHz.

`dead_gap` is the delay between switching off one side of a half-bridge and switching on the
other. **It is 260 ns on both board revisions.** Both Parallax manuals specify a 250 ns
minimum even though Rev B's gate drivers are about twice as fast as Rev A's, because the limit
is set by the MOSFETs' response, not the drivers'. The value is 260 rather than 250 because
the integer conversion truncates: a literal 250 gives 248 ns at 270 MHz.

### The bridge states

| State | What the six FETs do | When |
|---|---|---|
| `BR_DRIVE` | PWM | running; and at rest with `holdAtStop(true)` (held at `duty_min`) |
| `BR_COAST` | all off | at rest with `holdAtStop(false)`; on a fault with `holdAtStop(false)` |
| `BR_SHORT` | low sides on | emergency stop, always; on a fault with `holdAtStop(true)` |

### Fault handling

A fault is declared when the rotor lags the commanded angle by 125/256 of a cycle (175.8°) —
commutation has lost the rotor. The bridge takes the stop mode's fault state (above),
`DCS_FAULTED` is latched, and `fault` is written. The fault test is skipped while the bridge
is not driven, so turning an idle wheel by hand cannot fault it. A new command clears the
fault.

---

## 5. The front cog

One pass per millisecond, on an absolute `getct()` schedule; a late pass is counted and the
schedule re-anchored, never replayed.

```
0. confirm a stop written in an earlier pass, or write it again
1. take, apply and answer the posted requests (e-stops, then stops, then the rest); one
   that depends on the driver (a synchronized take, an e-stop release, a fault clear) is
   held in flight and answered on the pass that sees the driver act, within 4 drive
   passes (DRIVER_REV 37) -- no front pass waits on a driver
2. tracking: latch a new fault's cause; accumulate hall ticks since the last pass
   every 8th pass (125 Hz): advance the 1-second rpm window, update the following
   reading, and re-derive the lead (6.5″ only)
3. limits: a time or distance limit fires early by the stopping time or distance the
   driver has published (drv_stop_passes / drv_stop_fp), so the motor comes to rest at
   the limit
4. the command timeout, when on
5. protection: the phase-current average and the derate; the blocked-motor test
```

**Stopping time and distance** are the driver's own stop plan (§4), read from the status run:
the front cog computes nothing and only reads and compares. `frontStopTicks()` is
`drv_stop_fp` in whole hall ticks; `frontStopMs()` is `drv_stop_passes` at 522.7 µs a pass,
rounded up. The plan counts from the published pass's own time, and the run is read after
that, so its age can only make a limit's stop early, never late. The plan is the jerk-limited
stop's phases (unwinding any acceleration still speeding up, the rise, the plateau at
`accel_dn`, the ramp-out) in closed form, exact against the driver's own per-pass arithmetic —
the form the Spin2 `stopPlan()` computed at DRIVER_REV 38 (it is gone). From 196 ticks/s on
the 6.5″ motor that form gave about 100 hall ticks, DERIVED and not yet measured; the
constant-rate ramp before DRIVER_REV 38 gave 75, the figure the bench measured. Only one limit
is live at a time: a time limit is checked first, and a distance limit only while no time
limit is armed.

**The following reading** divides the rpm window's measured rate by the commanded rate. The
driver acts on it internally; no public method reports it.

**Protection:**

- **Derate.** The front cog estimates the phase current from the DC-link reading and the
  modulation depth, averages it over about a second, and switches `i_limit_k` to the 27 A
  continuous limit when the average exceeds it, back to 40 A once it falls below 80 % of 27 A.
- **Blocked motor.** A motor commanded to move whose rotor is held `LAG_SOFT` or more from the
  field with no hall transition for 1,000 passes (about a second) is secured, and a protective stop
  (`ERR_PLATFORM_BLOCKED`) latches until `clearProtectiveStop()`.

**The steering front cog** runs the same pass for both wheels, plus one thing of its own:
**path-preserving speed limiting.** When either wheel reads short of its command, both wheels'
commands are scaled by the slower wheel's achieved fraction — at once going down, slowly coming
back up — so the platform keeps its path and loses speed.

---

## 6. The two-wheel layer

`isp_steering_2wheel` owns two `isp_bldc_motor` instances and adds coordination:

- **Mirrored mounting.** `rtWheel.forwardIsReverse()` is called at start, so a positive power
  means "forward" for both wheels despite them facing opposite ways.
- **Lock-step start** and **lock-step commands**: drive commands are written to both wheels
  with the sync bit set and released with one `cogatn`, so both take them in the same drive
  pass.
- **Steering mix.** `driveDirection()` slows the wheel on the side of the turn in proportion to
  `|direction|`, stopping it at 100. It never reverses a wheel, so it cannot pivot in place;
  use `driveAtPower(+n, −n)` for that.
- **Distance moves.** `driveForDistance(left, right)` runs each wheel at a power in proportion
  to its distance, so both finish at about the same time, and arms each wheel's own limit.
- **One protective stop for both.** A cause on either wheel secures both.

---

## 7. Behaviors that will surprise you

| Behavior | Why |
|---|---|
| `start()` blocks for about a second | It samples the current sense at rest so `getCurrent()` reads zero at rest. |
| A command method can take up to 20 ms | It waits, bounded, for the front cog's answer. `ERR_NO_RESPONSE` means the answer did not come in time and the outcome is unknown. |
| Setting a time and a distance limit together honours only the time | The distance limit waits until no time limit is armed (§5). |
| `setMaxSpeed()` never refuses | It caps what you command. A motor that cannot reach its command holds the fastest speed it can sustain. |
| Reverse power on a `MOTR_DOCO_4KRPM` uses *negative* increments as "forward" | The DocoEng motor's increment convention is inverted relative to the 6.5″ motor. |
| Distance methods need a non-zero wheel diameter | With `WHEEL_DIA_IN_INCH = 0.0` they return `ERR_NO_WHEEL_DIA`. Single-motor bench setups usually have it at 0. |
| `power` 100 is not the fastest the motor can turn | It is the fastest speed that keeps a duty reserve. Above it the motor follows only by field weakening, at a steep cost in current, and can slip. |

---

## 8. Adding a motor — what the driver must be told

Summarised from [ADDING_MOTOR.md](ADDING_MOTOR.md), from the driver's point of view. The
driver cannot detect any of this at runtime, so all of it is compiled in:

1. **Hall geometry** — ticks per revolution and degrees per tick (`hallTicInfoForMotor`).
2. **Hall order** — the forward/reverse sequence, encoded in the `hltb*` angle table.
3. **Transition deltas** — the `deltas*` table, indexed `(old << 3) | new`.
4. **Commutation offsets** — the fwd/rev electrical offsets that minimise current
   (`offsetsForMotor`); for the 6.5″ motor, a hall zero and a lead table against speed.
5. **Per-voltage increment ceilings** (`confgurePowerLimits`), subject to Invariant 4, and the
   motor's back-EMF line for the feedforward.
6. **A motor identifier** — added to the `MOTR_*` enum in `isp_bldc_motor_userconfig.spin2`,
   which defines it; `isp_bldc_motor.spin2` re-exports it, and the steering object re-exports
   the motor object's names.
