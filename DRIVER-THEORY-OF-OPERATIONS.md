# P2-BLDC-Motor-Control — Driver Theory of Operations

How the BLDC driver actually works: the cog topology, the Spin2↔PASM2 contract, the
commutation and PWM loop, and the invariants that must hold for any of it to be correct.

This is a *developer reference*. For the public method tables see
[DRIVE-OBJECTS.md](DRIVE-OBJECTS.md); for wiring your own project up see
[DEVELOP.md](DEVELOP.md); for adding a motor see [ADDING_MOTOR.md](ADDING_MOTOR.md).

**Status of this document:** written 2026-09-09 from a full read of the driver source.
It describes the code **as it is**, including places where behavior differs from what the
public documentation claims. Where that happens it is marked ⚠ and cross-referenced to
`DOCs/analyses/DRIVER-AUDIT-2026-09-09.md`.

---

## 1. The shape of the thing

The drive subsystem is **not** a call-and-wait API. It is a set of cogs that run
continuously, plus a block of shared memory. Public methods almost never *do* anything —
they write a control variable and return. Motion changes because a driver cog notices a
changed value on its next pass, typically within 500 µs.

Understanding that one fact explains most of the design: why there are no completion
callbacks, why `stopAfterDistance()` returns immediately, why status is polled, and why
almost every "setter" is a single assignment.

### Cog topology

```
                    ┌─────────────────────────────────────────┐
   user app cog ───▶│ isp_steering_2wheel  (optional layer)   │
                    └───────────┬─────────────────┬───────────┘
                                │                 │
                    ┌───────────▼──────┐ ┌────────▼─────────┐
                    │ isp_bldc_motor   │ │ isp_bldc_motor   │   ← Spin2 objects
                    │ (left instance)  │ │ (right instance) │     (no cog of their own)
                    └───────────┬──────┘ └────────┬─────────┘
                                │                 │
              ╔═════════════════▼═══╗ ╔═══════════▼═════════╗
              ║ PASM2 driver cog    ║ ║ PASM2 driver cog    ║   ← 1 cog each, 2 kHz
              ║ commutation + PWM   ║ ║ commutation + PWM   ║
              ╚═════════════════════╝ ╚═════════════════════╝
              ╔═══════════════════════════════════════════════╗
              ║ taskPostionSense  (Spin2)  — 8 Hz             ║   ← 1 cog total
              ╚═══════════════════════════════════════════════╝
```

Cog count: **one PASM2 driver cog per motor**, plus **one position-sense cog**. A
two-wheel platform therefore burns 3 cogs and leaves 5 for the application. A
single-motor setup uses 2.

The sense cog is started differently depending on the layer you use:

| Configuration | Sense cog started by |
|---|---|
| Single motor, `isp_bldc_motor` direct | you call `startSenseCog()` yourself |
| Two motors, `isp_steering_2wheel` | automatically inside `start()` |

The Spin2 objects themselves do **not** run in their own cog — their methods execute in
whichever cog called them. This matters: a method that blocks (and two of them do) blocks
*your* cog. See §7.

---

## 2. The Spin2 ↔ PASM2 contract

This is the most fragile part of the codebase and the part most likely to be broken by an
innocent-looking edit.

The PASM2 driver does not call Spin2 and Spin2 does not call PASM2. They communicate
**only** through a block of hub memory, addressed by the driver as raw offsets from a
single pointer. **Declaration order in the `VAR` blocks is the ABI.**

### The pointer walk

`coginit(NEWCOG, @driver, @pinbase)` hands the cog `@pinbase` in `ptra`. The driver's
prologue then walks it:

```pasm2
rdlong  tmpX, ptra++                    ' [0] base pin
rdlong  params_ptr_, ptra++             ' [1] pointer to the parameter block
add     ptra, #2*4                      ' skip [2] targetAngle and [3] targetIncre
                                        ' ptra now points at the STATUS block
```

After that walk, three regions are addressable:

| Region | Address | Direction | Longs |
|---|---|---|---|
| `targetAngle` | `ptra[-2]` | Spin2 → driver (test only) | 1 |
| `targetIncre` | `ptra[-1]` | Spin2 ↔ driver (handshake) | 1 |
| Status block | `ptra[0..13]` | driver → Spin2, every loop | 14 |
| `fault` | `ptra[14]` | driver → Spin2, on fault only | 1 |
| Parameter block | `params_ptr_` | Spin2 → driver, every loop | 14 |

### The three invariants

**Invariant 1 — the launch quartet is ordered and adjacent.**
`pinbase`, `params_ptr`, `targetAngle`, `targetIncre` must be the first four longs of the
`VAR` block, in that order. The prologue reads two and skips two by fixed offset.

**Invariant 2 — the status block is 14 contiguous longs, and `fault` is the 15th.**

```
drive_u, drive_v, drive_w,                          (3)
sense_u_mV, sense_v_mV, sense_w_mV, sense_i_mV,     (4)
hall, pos,                                          (2)
duty, err,                                          (2)
loop_ticks, loop_ctcks,                             (2)
drv_state                                           (1)  = 14
fault                                                    ← must be immediately after
```

The driver writes them in one burst — `setq #DRVR_STATUS_LONGS_COUNT-1` then
`wrlong drive_u_, ptra` — and reports a fault by writing `ptra[DRVR_STATUS_LONGS_COUNT]`,
i.e. index 14. The PASM side mirrors the same 14 names as contiguous `res 1` registers.
**Three places must agree**: the Spin2 `VAR` order, the PASM `res` order, and the count
constant.

**Invariant 3 — the parameter block is 14 contiguous longs.**

```
offset_fwd, offset_rev, duty_min, duty_max, duty_up, duty_dn, dead_gap,
ramp_down, cfg_ctcks, stop_mode, e_stop, ramp_max, ramp_min, ramp_inc     = 14
```

Read every loop by `setq #DRVR_PARAMS_LONGS_COUNT-1` / `rdlong params_ptr_+1, params_ptr_`.
`frame_cnt` sits *after* the block and is deliberately outside it.

> Insert, remove, or reorder a long inside any of these runs and the driver silently reads
> the wrong values. There is no check, no assertion, and no symptom other than a motor
> behaving strangely. If you change one, change the matching count constant and the PASM
> `res` block in the same edit.

### `targetIncre` — a 31-bit signed field with a stolen bit

The single most surprising piece of the contract. `targetIncre` carries **two** things:

```
 bit 31        bits 30..0
┌────────┬───────────────────────────┐
│  sync  │  signed increment (31-bit)│
└────────┴───────────────────────────┘
```

Spin2 side (`setTargetAccel`):

```spin2
nTgtIncr ZEROX= 30          ' clear bit 31 — this DESTROYS the sign bit
nTgtIncr |= (sync << 31)    ' bit 31 now means "wait for ATN before accepting"
targetIncre := nTgtIncr
```

PASM side (`.gettgtincr`):

```pasm2
rdlong  tgt_incr, ptra[-1]
testb   tgt_incr, #31           wc      ' sync requested?
if_c    pollatn                 wz      ' Z := ATN flag state (1 = received)
if_c_and_nz mov tgt_incr, sv_tgt_incr   ' not yet — keep the previous target
if_c_and_z  bitl tgt_incr, #31          ' got it — strip the sync bit
if_c_and_z  wrlong tgt_incr, ptra[-1]   ' ...and acknowledge by writing it back
_ret_   signx tgt_incr, #30             ' restore the sign from bit 30
```

**⚠ Invariant 4 — the increment must satisfy |value| < 2³⁰ (1 073 741 823).** Because the
sign is recovered by `SIGNX #30`, a magnitude that reaches bit 30 is read as a negative
number: the motor silently runs the wrong direction. The largest value in the current
tables is 545 000 000 — roughly 2× headroom. Nothing checks this and nothing else says it.
A new motor or a higher supply voltage is exactly the change that would breach it.

The write-back at `ptra[-1]` is also the **sync acknowledgement**: `SyncStatus()` spins
until bit 31 clears, which is how the steering layer knows both motors have accepted the
same command.

### One-shot DAT initialization

`sync_required` lives in the **`DAT`** block, not `VAR`. Spin2 writes it in `startEx()`
*before* `coginit`, and the cog receives its own copy at load time. Writing it afterwards
has no effect on the running cog. This works, but it is the only variable in the design
that behaves this way.

---

## 3. Startup sequence

```
startEx(basePin, voltage, detectMode, sync)
  ├─ sync_required := sync              ← must precede coginit (§2)
  ├─ init(...)
  │    ├─ derive tick constants from CLKFREQ
  │    ├─ getBoardType()                ← charges a cap on pinbase+4, samples 500×
  │    ├─ select per-motor tables       ← copied into the driver image BEFORE launch
  │    ├─ compute frame_cnt, dead_gap, pwm_limit, duty_min/max
  │    └─ confgurePowerLimits(voltage)  ← fills the increment tables
  ├─ params_ptr := @offset_fwd
  ├─ setTargetAccel(0, false)           ← explicitly "do not move at startup"
  └─ coginit(NEWCOG, @driver, @pinbase)
```

Inside the cog: read the pointers, configure six PWM smart pins (low side inverted, high
side not), calibrate the four ADC channels against GIO and VIO reference levels, compute
per-channel scaling with the CORDIC, then — if `sync_required` — `waitatn` until released.

**Board revision detection** is done by charging a 0.1 µF capacitor on `pinbase+4`,
floating the pin, and counting how many of 500 reads still read high:

| Sum | Meaning |
|---|---|
| `0` | Rev A (1 kΩ pulldown holds it low) |
| ~40–180 | Rev B (capacitor discharging) |
| `>250` | no board attached |

⚠ The revision result is then compared against **two different enum families** in the same
method, and one comparison can never be true. See audit findings A1–A3.

---

## 4. The 2 kHz drive loop

One iteration every 500 µs (`cfg_ctcks`), per motor:

```
1. e_stop set?          → drive off, state := DCS_ESTOP, exit
2. read targetIncre     → .gettgtincr (sync handshake + sign restore)
3. target == 0?         → stop path; honour stop_mode (brake vs float)
4. target changed?      → accept ONLY if state is STOPPED, AT_SPEED, or FAULTED;
                          otherwise discard the request and keep doing what we were doing
5. ramp drv_incr toward tgt_incr
6. angle_ += drv_incr   → the commanded electrical angle advances
7. read hall sensors    → look up the actual angle for this hall state
8. err_ = actual − commanded
9. |err_| ≥ 125/256 turn (~176°)?  → FAULT: drive off, latch DCS_FAULTED, signal hub
10. modulate duty by err_ (duty_up when lagging, duty_dn when leading), clamp to
    duty_min..duty_max
11. write the 14-long status block to hub
```

Step 4 is worth dwelling on: **a new drive command is silently discarded while the motor
is mid-ramp.** Only `DCS_STOPPED`, `DCS_AT_SPEED` and `DCS_FAULTED` accept new targets.
Command a speed change during spin-up and it is dropped — the caller is not told.

### Commutation

The rotor position comes from three hall sensors. Their 3-bit pattern indexes
`hall_angles`, a 16-entry table giving the angle within the hall cycle. Bit 3 of the index
selects the forward or reverse half of the table, so the same table serves both
directions. Per-motor tables are chosen in `init()` and copied into the driver image
*before* the cog starts:

| Motor | Hall ticks/rev | Degrees/tick | Angle table | Delta table |
|---|---|---|---|---|
| 6.5″ hub (`MOTR_6_5_INCH`) | 90 | 4° | `hltbAngles` | `deltas65` |
| DocoEng 4 kRPM (`MOTR_DOCO_4KRPM`) | 24 | 15° | `hltbAngl4k` | `deltas4k` |

`deltas*` is indexed by `(previous_hall << 3) | new_hall` and yields −1, 0 or +1 — the
position increment for that transition. This is what makes `pos` a signed, direction-aware
tick counter rather than a pulse count.

### PWM and the dead gap

Triangle PWM at **44 kHz** (`PWM_RATE_IN_HZ`); one ADC sample per PWM frame, phase-locked
by enabling the ADC and PWM pins in the same instruction. `dead_gap` is the enforced delay
between switching the high and low side of a phase — driving both at once shoots through
the half-bridge.

| Board | MOSFET driver | Vendor minimum | Code *intends* | Code *actually applies* |
|---|---|---|---|---|
| Rev A | MIC4604 (39 ns prop, ~20 ns rise/fall) | **250 ns** | 260 ns | 260 ns ✅ |
| Rev B | UCC27211D (~20 ns prop, 7.2/5.5 ns) | **250 ns** | 52 ns ⚠ **out of spec** | 260 ns ✅ |

**There is no per-revision deadtime requirement.** Both Parallax manuals specify the same
250 ns minimum even though Rev B's drivers are roughly twice as fast as Rev A's — because
the limit is set by **MOSFET response time, not driver switching speed**. Below it, both
FETs are partially on and the channel draws momentary overcurrent.

The enum defect at `isp_bldc_motor.spin2:198` (audit finding **A1**) means the Rev B
branch never executes, so every board gets 260 ns — **which is the correct value for both
boards.** The accident lands on the right answer.

**So the fix is to delete the conditional**, not repair it: one `gapInNs := 260` for both
revisions. Repairing the comparison alone would take every Rev B board ~5× below spec. Keep
260 rather than 250 — the integer divide truncates, and a literal 250 gives 248.1 ns at
270 MHz. The gap costs ~1.1 % of duty range either way. See **A1** and **PL-9**.

The gap directly limits usable duty: `pwm_limit = frame_cnt/2 − dead_gap/2`, so any
change to it also moves `pwm_limit` and `duty_min`.

### Ramping

`drv_incr` chases `tgt_incr` rather than jumping. Ramp-up starts at `ramp_min` (1 500) and
adds `ramp_inc` (22) every 500 µs until it reaches `ramp_max` (200 000); ramp-down is a
fixed `ramp_down` (50 000). A direction reversal goes through `DCS_SLOW_TO_CHG` — decelerate
through zero, then accelerate the other way.

### Fault handling

A fault is declared when the rotor lags the commanded angle by ~176°, which means
commutation has lost sync — the motor is being asked for more torque than it can deliver.
The driver's response is absolute: **PWM off, `DCS_FAULTED` latched, `fault` signalled.**

There is no retry, no torque back-off, no re-sync attempt. Recovery happens only when a
*new* drive command arrives (`.resetFault`). This is the behavior README describes as
"motor can fault at higher load conditions… we need to add a fallback algorithm so the
motor doesn't 'give up' under load."

⚠ Combined with the status defect below, a faulted motor stops dead while the API still
reports it as moving. See audit findings Z and AF.

---

## 5. The 8 Hz position-sense loop

A Spin2 cog, one iteration every 125 ms:

1. If the driver is `DCS_FAULTED` / `DCS_ESTOP`, reset the accumulators.
2. Compute ticks since the last pass, add to `posTrkHallTicks`, push into an 8-entry
   ring buffer (8 samples × 125 ms = a 1-second moving window).
3. Enforce `stopAfterTime` / `stopAfterDistance` — this is where those actually take
   effect; the setters only record a target.
4. Auto-clear an emergency stop after ~2 passes.
5. Derive RPM, counts/sec, mm/s, km/h, mph for the HDMI debug display.

**Time and distance are checked with `if`/`elseif`, so setting both means only the time
limit is honoured** — the distance target stays armed and will fire on a later move.

⚠ The moving-window sum is broken: it adds a variable that is only ever zero, so every
derived rate (RPM, mm/s, km/h, mph) reads zero-or-negative. Distance and rotation counts
are *not* affected — they use a different variable. See audit finding W.

---

## 6. The two-wheel layer

`isp_steering_2wheel` owns two `isp_bldc_motor` instances and adds coordination:

- **Mirrored mounting.** `rtWheel.forwardIsReverse()` is called once at start, so a
  positive power means "forward" for both wheels despite them facing opposite ways.
- **Lock-step start.** Both motors are started with `sync = true`, so each parks in
  `waitatn`; a single `cogatn(cogmask)` releases them together.
- **Lock-step commands.** `driveAtPower()` writes both targets with the sync bit set,
  issues one `cogatn`, then calls `SyncStatus()` on each wheel to confirm both accepted
  the same command in the same 500 µs window.
- **Steering mix.** `calcPowerForDirection()` keeps the outside wheel at full power and
  reduces the inside wheel proportionally to `|direction|`. It never reverses a wheel, so
  `driveDirection()` cannot pivot in place; use `driveAtPower(+n, −n)` for that.

⚠ Which wheel is "inside" is inconsistent between the code, its own comment, and the
README. See audit finding AC.

---

## 7. Behaviors that will surprise you

Collected because each one has cost someone time.

| Behavior | Why |
|---|---|
| `resetTracking()` blocks for 200 ms | It sleeps instead of handshaking with the sense cog. Via the steering layer it is called for both wheels — ~400 ms. |
| `stopAfterDistance()` and friends `abort` on bad input | Parameter validation uses `abort`, not error returns. Uncaught, it unwinds your call stack — and if the motor was already running, it keeps running. |
| A speed change during spin-up is ignored | Drive-loop step 4. Silently. |
| Setting both a time and a distance limit honours only time | §5, `if`/`elseif`. |
| `start()` returns cog-id **+1**, and **0** on failure | Not −1, despite the doc comment. |
| Reverse power on a `MOTR_DOCO_4KRPM` uses *negative* increments as "forward" | The DocoEng motor's increment convention is inverted relative to the 6.5″ motor. |
| Distance methods need a non-zero wheel diameter | With `WHEEL_DIA_IN_INCH = 0.0` they abort. Single-motor bench setups usually have it at 0. |

---

## 8. Adding a motor — what the driver must be told

Summarised from [ADDING_MOTOR.md](ADDING_MOTOR.md), from the driver's point of view. The
driver cannot detect any of this at runtime, so all of it is compiled in:

1. **Hall geometry** — ticks per revolution and degrees per tick (`hallTicInfoForMotor`).
2. **Hall order** — the forward/reverse sequence, encoded in the `hltb*` angle table.
3. **Transition deltas** — the `deltas*` table, indexed `(old << 3) | new`.
4. **Commutation offsets** — the fwd/rev electrical offsets that minimise current at a
   given speed (`offsetsForMotor`).
5. **Per-voltage increment ceilings** — the empirically characterised maximum increment
   for each supported supply voltage (`confgurePowerLimits`), subject to Invariant 4.
6. **A motor identifier** — added to the enum in **both** `isp_bldc_motor.spin2` and
   `isp_bldc_motor_userconfig.spin2`; they are two hand-maintained copies of one list.

---

## 9. Cross-reference

Findings marked ⚠ above are detailed, with evidence and severity, in
**`DOCs/analyses/DRIVER-AUDIT-2026-09-09.md`**:

| Marker | Finding |
|---|---|
| §3 board revision | A1, A2, A3 — board-revision enum family mismatch |
| §4 dead gap | A1 — wrong-enum comparison; **revised 2026-09-10, the naive fix is a hardware hazard** (PL-9) |
| §4 fault | Z — hard latch with no fallback |
| §5 rate window | W — all speed/RPM telemetry reads zero-or-negative |
| §6 steering mix | AC — direction inverted relative to its own comment |
| §7 / status | M, AF — a faulted motor reports as moving, end to end |
