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
| Status block, `drive_u` … `duty_capped` | `ptra[0..18]` | driver → Spin2, every frame | `DRVR_STATUS_LONGS_COUNT` = 19 |
| `fault` | `ptra[19]` | driver → Spin2, on fault only | 1 |
| Parameter block, `offset_fwd` … `duty_floor` | `params_ptr_` | Spin2 → driver, every frame | `DRVR_PARAMS_LONGS_COUNT` = 16 |

### The invariants

**Invariant 1 — the launch quartet is ordered and adjacent.** `pinbase`, `params_ptr`,
`targetAngle`, `targetIncre` are four contiguous longs, in that order, immediately before the
status block.

**Invariant 2 — the status block is 19 contiguous longs, and `fault` is the next one.**

```
drive_u, drive_v, drive_w,                          (3)
sense_u_mV, sense_v_mV, sense_w_mV, sense_i_mV,     (4)
hall, pos,                                          (2)
duty, err,                                          (2)
loop_ticks, loop_ctcks,                             (2)
drv_state,                                          (1)
hall_missed, hall_illegal,                          (2)
drv_incr_now,                                       (1)
lag_held, duty_capped                               (2)   = 19
fault                                                     ← immediately after
```

The driver writes them in one burst (`setq #DRVR_STATUS_LONGS_COUNT-1` / `wrlong drive_u_,
ptra`) and reports a fault by writing `ptra[DRVR_STATUS_LONGS_COUNT]`.

**Invariant 3 — the parameter block is 16 contiguous longs.**

```
offset_fwd, offset_rev, duty_min, duty_max, servo_shift, ff_ceiling, dead_gap,
ramp_down, cfg_ctcks, stop_mode, e_stop, ramp_max, ramp_min, ramp_inc,
i_limit_k, duty_floor                                                         = 16
```

Read every frame by `setq #DRVR_PARAMS_LONGS_COUNT-1` / `rdlong params_ptr_+1, params_ptr_`.
`frame_cnt` sits after the block and is deliberately outside it.

**Three places must agree** for each block: the Spin2 `VAR` order, the PASM `res` order, and
the count constant. **`start()` checks the layout before it launches anything**
(`isAbiLayoutValid()`): the three runs must have the offsets the driver walks, and every
Spin2-only array — the error slots, the request slots, the front cog's stack, the rpm window —
must lie outside them. A mismatch refuses the start with `ERR_ABI_MISMATCH`. The check sees
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

`sync_required`, the per-motor tables (§4) and the LUT code pointer live in the driver's
`DAT` image, written by `init()` **before** `coginit`. The cog receives its own copy at load
time; writing them afterwards has no effect on a running driver.

---

## 3. Startup sequence

```
start(basePin, voltage, detectMode)                   (steering: startOwned() per wheel)
  ├─ validate pin group, voltage, detect mode         → ERR_BAD_* on failure
  ├─ isAbiLayoutValid()                               → ERR_ABI_MISMATCH
  ├─ stop any driver and front cog this instance already runs
  ├─ claim the pin group                              → ERR_PIN_GROUP_IN_USE
  ├─ init(...)
  │    ├─ derive tick constants from CLKFREQ
  │    ├─ getBoardType()                              ← detect the board revision
  │    ├─ select the per-motor tables and offsets     ← copied into the driver image
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
released.

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
  apply the current limit, and servo the duty. It writes the 19-long status block every frame.
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
5. ramp drv_incr toward the target, unless the rotor trails (or, slowing, leads)
   the field by LAG_SOFT (112.5°): then the ramp waits for the rotor this pass
6. advance angle_ by drv_incr, unless the rotor trails by LAG_HOLD (140.6°):
   then the field is held, lag_held counts it, and drv_incr decays toward the
   rate the rotor achieves (1/64 per held pass)
7. compute the duty feedforward for this pass's speed
```

A speed change starts its ramp from `ramp_min` again, as a start from rest does. A direction
reversal goes through `DCS_SLOW_TO_CHG`: ramp down through zero, then up the other way.
Default ramps: `ramp_min` 1,500, `ramp_inc` 22 per pass, `ramp_max` 200,000; ramp down is a
fixed `ramp_down` 50,000 per pass. `setAcceleration()` replaces the ramp up with a constant
rate converted from mm/s².

Steps 5 and 6 are why the driver seldom faults any more: the field never gets far enough
ahead of the rotor to trip the 175.8° fault test unless the rotor is truly lost.

### The frame loop — commutation

The three hall lines are read in **one instruction**, so all three bits come from the same
instant. The 3-bit code, combined with the previous one as `(old << 3) | new`, indexes a
`deltas` table giving −1, 0 or +1 — the position step for that transition. This is what makes
`pos` a signed, direction-aware tick counter. A change with no legal step counts as a
missed transition (`hall_missed`), and an entry into `%000` or `%111` is counted by kind
(`hall_illegal`, low and high words).

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

Each frame the DC-link current reading is compared with a threshold scaled from the phase
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
1. take, apply and answer the posted requests (e-stops, then stops, then the rest)
2. tracking: latch a new fault's cause; accumulate hall ticks since the last pass
   every 8th pass (125 Hz): advance the 1-second rpm window, update the following
   reading, and re-derive the lead (6.5″ only)
3. limits: a time or distance limit fires early by the stopping time or distance at
   the current speed, so the motor comes to rest at the limit
4. the command timeout, when on
5. protection: the phase-current average and the derate; the blocked-motor test
```

**Stopping distance** is computed from the ramp: a stop from increment `i` takes
`i ÷ ramp_down + 1` passes and covers `i × passes ÷ 2` of angle, which is 75 hall ticks from
196 ticks/s on the 6.5″ motor — the figure the bench measured. Only one limit is live at a
time: a time limit is checked first, and a distance limit only while no time limit is armed.

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
