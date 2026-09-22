# The 6.5″ hub motor — a technical manual

**What it is, how the 64010 board drives it, and where it wants to run.**

This manual describes the Parallax hoverboard-style 6.5-inch motor-in-wheel (`MOTR_6_5_INCH`)
as we have actually measured it, and how to get good behaviour out of it with the Parallax
64010 Universal Motor Driver board.

It is written for someone who wants to understand this motor — not a motor designer, but not a
beginner either. Section 3 assumes you know what PWM is. Nothing else assumes much.

---

## 1 · How to read this manual

### 1.1 The one idea to carry through

> **One electrical cycle is 24° of wheel.**

The motor has 30 magnets — 15 pole pairs — so the electrical machine goes round 15 times for
every one turn of the wheel. Almost everything in this manual is an *electrical* angle, and
electrical angles are small in wheel terms. The three hall sensors divide each electrical
cycle into six 60° sectors, so:

| | electrical | mechanical (wheel) |
|---|---|---|
| one hall sector (one "tick") | 60° | **4°** |
| one electrical cycle (6 ticks) | 360° | **24°** |
| one wheel revolution | 5,400° (15 cycles) | 360° |

That ratio is why a 1° error in where a hall sensor sits becomes a **15° electrical** error,
and why this motor is unusually sensitive to commutation alignment. It is also why angles
quoted here to a tenth of a degree are not absurd: a tenth of an electrical degree is
0.0067° of wheel, and we measure it by timing, not by looking.

### 1.2 Every number carries a label and a source

| Label | Means |
|---|---|
| **MEASURED** | read off the bench, from a named log or evaluation, with its error where we have one |
| **DERIVED** | computed from measured values or from source constants; the arithmetic is shown or cited |
| **ASSUMED** | taken from a datasheet, a vendor manual, or a constant nobody has verified on our hardware |

A number without an error bar is a number claiming more precision than it has. Where we have
a standard error, it is printed.

### 1.3 Motor, driver, instrument — the three things this manual keeps apart

A lot of what one observes on a bench is a property of the *system*, not of the motor. This
manual attributes every quantity, because getting that wrong is how a "motor specification"
becomes misleading:

| Quantity | Belongs to |
|---|---|
| Pole count, hall geometry, the hall zero **Z** | the **motor** — durable, transfers with any driver |
| The lead **L**, the servo setpoint, the offsets, the fault ceiling | the **driver** — our choices, not the motor's properties |
| Direction-to-direction current asymmetry | was **ours**, and is gone (§7.3) |
| Whether L's speed dependence is the motor's electrical time constant or our commutation lag | **not separated** — §9, hole H-2 |
| Current readings in mV, the abort thresholds, the ladder rungs | the **instrument** |

### 1.4 What is not settled

Open questions are marked ⬚ where they arise and collected in §9. They are annotations on
this manual, not its subject: strike every one of them and §§2–8 remain a complete description
of the motor and how to drive it.

---

## 2 · The motor

### 2.1 Construction and geometry

| Property | Value | Label |
|---|---|---|
| Type | 3-phase BLDC hub motor; the stator is the axle, the rotor is the wheel | ASSUMED (vendor) |
| Magnets (poles) | **30** | MEASURED, §2.2 |
| Pole pairs / electrical cycles per wheel revolution | **15** | MEASURED, §2.2 |
| Position sensing | 3 hall sensors, 120° apart electrically | ASSUMED (vendor) |
| Hall states per electrical cycle | **6** | MEASURED |
| Hall ticks (transitions) per wheel revolution | **90** | MEASURED, §2.2 |
| Mechanical degrees per hall tick | **4°** | DERIVED (360 / 90) |
| Wheel outside diameter | 6.5 in = 165.1 mm | ASSUMED (nameplate) |
| Wheel circumference | 518.6 mm | DERIVED (π × 165.1) |
| Travel per hall tick | **5.76 mm** | DERIVED (518.6 / 90) |
| Hall state sequence | forward (CW): 1-3-2-6-4-5 · reverse (CCW): 1-5-4-6-2-3 | ASSUMED (library table) |

There is **no shaft**. The motor *is* the wheel, so there is nowhere to mount a shaft encoder
— which is why every position fact below had to be obtained from the halls or by hand, and why
the bench's 360 P/R optical encoder (which we do own) cannot be used on this motor.

### 2.2 Why we believe 30 poles and 90 ticks

This is worth stating because a competing figure exists. The board designer's recollection was
that hoverboard wheels are *"like 23 electrical revolutions per mechanical revolution"* —
hedged in his own words. If that were right, every distance and rotation reading in the library
would be wrong by 53%.

**It is not right for this motor, and the check was direct.** With the motor unpowered, the
right wheel was turned **three full revolutions by hand** and the hall transitions counted:

```
T0-12,begin,told_direction,CW_FROM_HUB,revolutions,3,wheel,RIGHT_P16
T0-12,end,transitions,270,illegal,0,pos,-270,final_hall_code,6
```

270 ÷ 3 = **exactly 90 ticks per revolution**, hence 15 electrical cycles. 23 cycles would have
required 414 transitions. The starting and final hall codes match (as they must after a whole
number of cycles) and no illegal hall state occurred. **MEASURED** —
`DOCs/analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §2, log `debug_260915-142347.log`.

Note what this measurement does *not* use: no library constant appears anywhere in it. A human
supplied the ground truth and a counter counted edges. Checks that *look* like confirmations
but are circular — the mm-per-tick arithmetic, the speed ladder, the driver-versus-harness RPM
comparison — all divide by the same 90 they would be confirming.

### 2.3 Hall sensor health, as observed

Across every dual-motor run to date: `missed` 0, `illegal` 0, hardware skips 0, summed over all
ladder records on both motors. **MEASURED** —
`DOCs/analyses/bench/2026-09-21/VISIT-7B-EVALUATION.md` F10.

The halls are the one sensor in this system that has never given us a bad reading.

**The six sectors are unequal by about ±1° electrical**: LEFT ±0.9°, with sector `101` about 61°
and `001` about 59° on every leg; RIGHT ±0.55°. That comes from sensor placement, and on this motor
1° of placement is 15° electrical. ±1° is noise to a 60° sector commutator. It would set the error
floor for any sub-sector interpolation. MEASURED —
`DOCs/analyses/bench/2026-09-22/VISIT-7C-PASS2-EVALUATION.md` §3.5.

---

## 3 · How the 64010 board drives it

### 3.1 The power stage

| | Value | Label |
|---|---|---|
| Bridge | four half-bridges (U, V, W, X); three used for a BLDC motor | ASSUMED (vendor) |
| MOSFETs | Micro Commercial MCAC85N06Y-TP, 60 V, 85 A package-limited (54 A at 100 °C case) | ASSUMED (datasheet) |
| Gate driver | Rev A: MIC4604 · Rev B: TI UCC27211D | ASSUMED (vendor) |
| Current sense | low-side shunt in the common MOSFET-ground return — **total bridge current** | ASSUMED (vendor) |
| Sense scale | Rev A **5 mV/A** (5 mΩ, no amplifier) · Rev B **150 mV/A** (3 mΩ × INA180B2 gain 50) | ASSUMED (vendor) |
| Minimum dead-time | **250 ns, both revisions** — set by MOSFET response, not by driver speed | ASSUMED (vendor) |

**Every measurement in this manual was taken on the two units of the Rev B platform.** Two more
units of this motor exist on a Rev A platform; what they can and cannot add, and when, is §9.1.

Rev B has 30× the sense resolution of Rev A. At 10 A, Rev A presents 50 mV to a 3.3 V ADC and Rev B presents 1.5 V. Rev B is the better
instrument by a wide margin, and that is why measurements are taken there.

Full vendor text and part numbers: `DOCs/analyses/BOARD-REVISION-FACTS.md`.

### 3.2 The control loop, in one pass

The driver does **not** compute where to put the field from the rotor's position. It drives the
field forward on its own clock and *corrects* it from the halls. That distinction explains most
of this manual.

Each PWM frame the driver:

1. reads the current-sense and phase ADCs;
2. advances the commanded field angle `angle_` by `drv_incr` — the speed command;
3. computes the three phase outputs as `duty × sin(angle_ + 0° / 120° / 240°)` — `QROTATE` with
   no `SETQ`, read back with `GETQY` (p2kb `p2kbPasm2Qrotate`); the source comment says *cos*, and
   the instruction says otherwise;
4. reads the halls, looks up the sector's angle, adds the direction's offset, and forms
   `err_ = angle_ − (hall_angle + offset)` — how far the field leads the rotor estimate;
5. servos `duty` up or down to hold `|err_|` in its band (below).

| Constant | Value | Label |
|---|---|---|
| PWM / ADC frame rate | 44,000 Hz → **22.7 µs per frame** | DERIVED from `PWM_RATE_IN_HZ` |
| Drive passes (speed updates) | one per 23 frames → **1,913 passes/s** | DERIVED, `DRIVE_PASS_FRAMES = 23` |
| Field angle resolution | 32-bit fraction of an electrical cycle | source |
| Rotor angle resolution | **6 positions per electrical cycle** (one per hall sector) | source |
| Error representation | 8-bit signed, **256 counts per electrical cycle** (1 count = 1.4°) | source |
| Duty servo setpoint | `SERVO_SETPOINT` = `256/6` → **42 counts = 59°** (the immediate truncates) | source |
| Duty servo gains | **18 above** the setpoint, **4 below**, each shifted right 8 | source (`duty_up`, `duty_dn`) |
| What the servo actually holds | a **band**, 42–56 counts (**59–79°**): the shift truncates, so nothing moves until the excess reaches 15 counts; below 42 duty always falls | DERIVED from the two rows above; MEASURED: duty first rose at 57–59 on eight START traces |
| Duty floor / ceiling at 270 MHz | `duty_min` **1,600** · `duty_max` **24,264** | DERIVED from frame and dead-gap |
| Dead gap applied | 260 ns (compliant with the 250 ns minimum) | source |
| Lag: ramp waits | `LAG_SOFT` 80 counts = **112.5°** | source |
| Lag: field stops advancing | `LAG_HOLD` 100 counts = **140.6°** | source |
| Lag: fault | 125 counts = **175.8°** | source |

### 3.3 The two knobs that place the field — and they add

This is the single most important thing to understand about driving this motor, and the easiest
thing to get wrong.

**Where the field sits relative to the rotor in steady state is set by two separate numbers that
add together:**

- the **commutation offset**, added to the hall angle before the error is formed. It is
  feedforward: it takes effect instantly and does not depend on the servo.
- the **duty servo setpoint**, currently 60°. The servo drives `duty` until `|err_|` settles
  there, so the rotor ends up trailing the field by the setpoint.

Total steady-state field placement is the **sum**. Two consequences follow, and both are live:

1. ⚠ **A correction applied to both knobs is applied twice.** The board designer's principle
   says drive at ±90° electrical; our servo holds 60°. Separately, sweeping the offsets moved
   the lead from 43° to 18° — a −25° correction. Those are the **same correction reached
   independently**, agreeing within 5°, and doing both would mis-place the field by about 55°.
   Given how steep the current basin is (§7.4: 12.7× over 30°), that is not marginal.
2. **The two knobs behave differently in time.** Feedforward is instant; the servo is
   regulated and takes hundreds of passes to get there. §6.4 is the consequence.

⬚ Which knob should carry the lead is not decided — §9, hole H-1.

### 3.4 What the driver does *not* do

| The board designer's principle | What we do |
|---|---|
| Place power at ±90° electrical from the rotor | The duty servo holds **60°** |
| Resolve electrical angle to 12 bits (4,096 positions) | **6 positions** — one hall sector, 60° wide |
| Compute electrical angle from a fine mechanical angle | The motor has no shaft and no fine sensor |

*(The designer's notes are quoted in full, with their provenance, in
`DOCs/analyses/BLDC-COMMUTATION-PRINCIPLES.md` — that document is canonical for them; this
section states only the consequence for this motor.)*

The designer's method (`electrical = mechanical_12bit × pole_pairs MOD 4096`) is textbook and
correct — and it starts from a 12-bit *mechanical* angle this motor cannot provide. The gap is
architectural, not a tuning difference: their machine carries an absolute position sensor and
ours carries three hall sensors. Closing it here would mean interpolating within a sector from
edge timing and speed, or estimating angle from the phase voltages the driver already samples.

---

## 4 · Position and geometry: the hall zero **Z**

### 4.1 What Z is

The halls tell you which 60° sector the rotor is in. They do not tell you where that sector
boundary sits relative to true electrical zero. **Z is that offset** — a fixed property of how
the sensors were placed in this motor. It is geometry: it cannot change with speed, load or
direction, and it transfers to any driver.

### 4.2 The measured values

Z is obtained as the **midpoint of the two per-direction current minima**. If each direction
wants the field leading by the same amount, the two minima sit symmetric about Z, and their
midpoint is Z with the lead cancelled out.

| Motor | Rung | Z | Label |
|---|---|---|---|
| LEFT | eighth | **−3.8° ± 0.3** | MEASURED |
| RIGHT | eighth | **−4.0° ± 0.3** | MEASURED |
| LEFT | quarter | **−3.85°** | MEASURED |
| RIGHT | quarter | **−3.45°** | MEASURED |

*(`DOCs/analyses/bench/2026-09-22/VISIT-7C-EVALUATION.md` §6.)*

**Measured a second way, cold.** With the bridge coasting and each wheel turned by hand, the three
phase terminals carry the motor's own back-EMF, whose zero crossings are fixed to the magnets. Placing
them against the hall edges (8 legs per motor, both directions, two hand speeds, two runs):

| Motor | Z, cold | Slow vs brisk | Label |
|---|---|---|---|
| LEFT | **−3.31°** | −3.34 / −3.29 | MEASURED |
| RIGHT | **−3.25°** | −3.22 / −3.28 | MEASURED |

*(`DOCs/analyses/bench/2026-09-22/VISIT-7C-PASS2-EVALUATION.md` §3.3.)*

**Take Z = −4° electrical for this motor**, on both units — right to within 0.7° by both methods,
which is inside the constant's own 1° resolution.

### 4.3 Why we trust it

Five independent confirmations, and they do not share a signal path:

1. **The symmetry prediction held.** The two per-direction minima are symmetric about a common
   midpoint on both motors, and the two midpoints agree within 0.5°. An aliased or spurious
   minimum would not land symmetrically about a common Z.
2. **Two physically separate motors and boards agree** — within 0.55°.
3. **It reproduces across independent runs** and across two speeds, within stated error.
4. **Z is speed-invariant, as geometry must be**: it moved 0.2–0.55° across a doubling of
   speed, while the lead L moved 12.2° across the same doubling. That is the instrument's own
   negative case, and it passed.
5. **A second method, sharing nothing with the first, agrees within 0.35°.** The cold back-EMF
   measurement uses no drive, no current and no offset sweep, and its own negative case holds too:
   slow and brisk legs agree within 0.12°. Its hall-frame derivation is itself tested by the data —
   the three phases fall 120° apart in the one order the drive's phase convention predicts.

### 4.4 The honest limit

The offset sweep covers about **126° of the 360° electrical cycle** — roughly 35%, bounded
outward by an over-current abort and inward by the motor faulting. Inside that window there is
exactly one minimum per direction, deep and reproducible.

**So the adopted alignment is established as a true local minimum, not proven to be the global
one.** Theory bounds it (torque per amp goes roughly as the sine of the lead, so one maximum per
cycle per direction is expected, and the solution 180° away is the reverse-torque one, excluded
because the wheel tracked its commanded direction at rate/predicted ≈ 1.000 at every rung). That
is an argument, not a measurement. See §9, hole H-4.

### 4.5 A caution for anyone turning the wheel by hand

Turning an unpowered 6.5″ hub wheel, you can plainly feel periodic detent — magnetic cogging
between the magnets and the stator teeth. **That is not commutation.** It is a property of the
iron, it exists with the drive switched off, and it must not be read as evidence about offsets.
Likewise, any low-current region you find while rotating the wheel repeats **15 times per
revolution, once every 24°** — those are not fifteen candidate alignments, they are one
alignment seen fifteen times. The offset is a single electrical angle applied identically inside
every one of the 15 cycles; "which one around the circumference" is not something the parameter
can express.

### 4.6 How the motor's own voltage locates the magnets

The halls report which 60° sector the rotor is in. They cannot report where the magnets actually
are. The motor itself can.

Turn the wheel with the bridge switched off, and every magnet sweeping past a winding induces a
voltage in it. Each of the three phase terminals then carries a sine wave **generated by the motor
alone**; the drive plays no part in it. Speed changes only the wave's size and how fast it
repeats. **Where its zero crossings and peaks fall is fixed by where the magnets sit relative to
that winding.** So each crossing marks the rotor's true electrical angle.

Timestamp the hall edges and those crossings on one clock, and the hall edges can be placed
against the magnets directly. That placement is Z. Three details make the reading sound:

- **The frame is checked, not assumed.** The three phases' peaks must fall 120° apart, in the
  order the drive's phase convention predicts. They do, to within 0.7°.
- **Peaks, not crossings.** The sense channels clip the negative half-wave, which shifts each
  crossing. The midpoint between a phase's rising and falling crossings is immune to that shift.
- **No drive, no current.** Nothing is powered, so the reading cannot be disturbed by current
  lag, the offset in use, or the servo, and it works the same on either board revision (subject
  to §9.1's phase-scale check).

The same signal exists while the motor is being driven, but the phase pins then also carry the
drive's PWM. Whether it can still be read there is not yet measured. That is the question that
decides whether this can become a live position source for the drive, not just a way to measure
the motor.

### 4.7 What differs from one unit to the next

Measured on the two units of the Rev B platform, by the method in §4.6:

| Property | LEFT | RIGHT | Unit-specific? |
|---|---|---|---|
| Hall zero Z | −3.31° | −3.25° | **No** — within measurement scatter; one constant serves both |
| Sector widths (§2.3) | ±0.9° about 60° | ±0.55° | **Yes**, each unit has its own fixed pattern, and it is small |
| Hall lag, each direction | ±1.05° | ±0.8 to ±1.2° | No — the same size on both |

**Hall lag** is the halls switching slightly late in the direction of travel. Forward readings of
Z sit about 2° more negative than reverse ones. The difference is the same at 43 and 117 edges/s,
so it is an angle rather than a time delay: it behaves like the sensors' switching hysteresis.
Averaging the two directions cancels it, which is why Z is always quoted as the mean.

**In wheel terms these are tiny.** On a 15-pole-pair motor, 1° electrical is 1/15° of wheel
rotation. So Z's −3.3° electrical is about 0.22° of wheel, and the difference between the two
units is about 0.004°. The sensors are placed consistently from unit to unit.

Two units are not a population. The Rev A pair can be measured the same way (§9.1), which would
make it four.

---

## 5 · Field placement: the lead **L**

### 5.1 What L is

Z says where the halls sit. **L says how far ahead of the rotor to put the field.** It is a
drive parameter, not a motor property. The two combine into the shipped offset pair:

```
offset_fwd = Z + L      applied to NEGATIVE increments
offset_rev = Z − L      applied to POSITIVE increments
```

With Z = −4 and L = 18, that is the shipped **14 / 338**.

### 5.2 L depends strongly on speed — and not the way theory predicts

| Rung | Commanded rate | LEFT | RIGHT | Label |
|---|---|---|---|---|
| **eighth** | 49 ticks/s | **27.8°** | **28.3°** | MEASURED |
| **quarter** | 98 ticks/s | **15.85°** | **15.55°** | MEASURED |

*(`VISIT-7C-EVALUATION.md` §6; reproduces an earlier independent run's 28.05 ± 0.05 and
15.88 ± 0.03 to within stated error.)*

**L falls by about 12.2° for every doubling of speed**, reproducing run-to-run to 0.1° on both
motors. This is a confirmed result, not a provisional one.

⚠ **The textbook current-lag model gives the wrong sign here.** The standard argument is that
current lags applied voltage more at higher electrical frequency, so the *voltage* lead needed
to place the *current* at 90° should **grow** with speed. We measure the reverse, strongly and
reproducibly. Do not design from that model on this motor. Why the real behaviour goes the
other way is not established — §9, hole H-2.

**The practical consequence today:** the shipped 14 / 338 pair is a *quarter-speed* tune. It is
right to about 1° at the quarter rung, and 11–14° away from what the motor wants at an eighth.
Z is safe in a compile-time constant. **The speed-varying part of L is not**, and no fixed
number can serve the whole range.

### 5.3 The basin is steep

Measured current against swept offset, LEFT motor, negative increment, net mV:

| swept° | 63 | 53 | **43** | 33 | 28 | 23 | 18 | **13** | 8 | 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| net mV | abort | 392.8 | **167.1** | 67.2 | 40.5 | 23.7 | 14.6 | **13.1** | 15.1 | fault |

**167.1 → 13.1 mV over 30° — a 12.7× change.** MEASURED.

This contradicts the standing prediction that the minimum would be broad (*"±15° from the
optimum costs only a few percent"*), and it contradicts it in our favour. A basin that deep is
consistent with off-optimum current being dominated by **circulating current that produces no
torque**, rather than by a modest loss of torque per amp — which is also the most natural
reading of the 15–26× current collapse in §7.3.

**What it means for you: alignment on this motor is worth a lot, and being 30° out costs an
order of magnitude in current, not a few percent.**

---

## 6 · The operating envelope

### 6.1 Speeds

The speed command is an angle increment applied 1,913 times a second. At 18.5 V the library's
ceiling increment is 147,000,000.

| | Value | Label |
|---|---|---|
| Drive passes per second | 1,913 | DERIVED |
| Ceiling increment at 18.5 V | 147,000,000 | source |
| → electrical frequency | **65.5 Hz** | DERIVED |
| → hall ticks per second | **393** | DERIVED |
| → wheel speed | **262 RPM** | DERIVED |
| → rim speed | **2.26 m/s** (5.1 mph) | DERIVED |
| Minimum increment that produces rotation | 544,628 → **~1 RPM** | source |

⚠ **The published table in `MOTOR_CHOICE.md` says 272 RPM / 408 ticks/s at 18.5 V.** Those
figures assume a 2,000 passes/s drive rate; the real rate is 1,913, and the measured ladder came
in at 0.946–0.965 of the 2,000 model. **Treat the published speed figures as about 4% high.**
They are ceilings for the fault limiter, not achieved speeds, and correcting them is release
work.

Bench work uses fractions of the ceiling increment as "rungs" — the eighth (49 ticks/s) and the
quarter (98 ticks/s) rungs appear throughout this manual.

### 6.2 The two walls

Sweeping the offset at a fixed commanded speed, the motor stops running for **two different
reasons**, and they are not the same wall:

| Wall | Where | What happens |
|---|---|---|
| **Current wall** | swept ±63° | Too much lead. Current explodes; the run aborts on the current cap. |
| **Torque wall** | swept +7° to −11° at the quarter rung | Too little lead. The motor cannot make enough torque; the field outruns the rotor and it faults. |

At 90° from optimum, torque is zero at any speed. The reachable arc is the band between the two
walls, and **it narrows as speed rises**:

| Rung | Reachable arc | Bounded by | Label |
|---|---|---|---|
| eighth | 40–50° | rise / current | MEASURED |
| quarter | ~±63 to +7 / −11 | current / torque | MEASURED |
| **half** | **20°** (23…43 and −43…−23) | **torque at BOTH ends** | MEASURED |

⬚ At the half rung the arc is 20° wide, torque-bounded at both ends, and extrapolating L
(27.9 → 15.7 → ~3.5) puts the optimum near swept 3–4° — **outside the reachable window
entirely**. That is a fact about the motor, measured with working guards, no fits pinned and
zero faults. It is the reason L at the half rung has never been obtained. See §9, hole H-5.

### 6.3 The duty ceiling

Above a certain speed the duty servo runs out of voltage: it asks for 100% and the rotor still
cannot keep up, so current falls away rather than rising. That knee is a **voltage / back-EMF
limit**, not a commutation defect.

**Where the knee sits depends on alignment.** At the shipped alignment duty first pins at rung
8; driven 25° off optimum the same motor pins at rung 6, two rungs lower. That is what a
voltage-limit model predicts when the current needed per unit torque falls, and an independent
frame counter agrees (6.8× fewer capped frames). MEASURED.

So alignment buys headroom as well as current. It does not remove the ceiling — above it, at
any alignment, the drive is saturated and current readings mean less than they appear to.

### 6.4 Starting from rest — the transient

**Every spin-up from rest produces a current surge that you can feel.** What the traces show, on
four starts per run across both motors and both directions, in two runs:

1. **The first ~0.45 s is quiet, and the rotor is moving through it.** Early in the ramp the field
   advances slowly enough for minimum duty (1,600 counts) to drag the rotor with it: `pos` walks
   several ticks while duty sits at its floor and `|err|` stays small. Duty has no reason to rise
   until the ramp outruns what minimum duty can hold.
2. **The surge is the duty servo HUNTING as the ramp accelerates.** From there `err` and duty swing
   together on a ~150 ms cycle — `err` −35 to −84, duty 3,600 to 6,200 — and each swing's high
   point is a current peak (57–100 counts, wheels up).

| Start (QTR, both directions) | Duty leaves its floor for good | Peak current | at |
|---|---|---|---|
| LEFT, two starts | ~0.49 s | 72–100 | 0.74–0.90 s |
| RIGHT, two starts | ~0.49 s | 57–82 | 0.73–0.91 s |

MEASURED — `DOCs/analyses/bench/2026-09-22/VISIT-7C-PASS2-EVALUATION.md` §4.3, and the same shape in
the earlier run's four traces.

**What it is not.** It is not the servo waiting out a deadband at the start. Starting the field
80° ahead of the rotor — where the servo first raises duty — was built and measured: duty rose at
once, the rotor snapped about a tick past the field, duty fell back to its floor for as long as
before, and the peaks did not change.

**Why it hunts — a model's answer, not yet a bench one.** The servo is integral-only. The rotor's
torque rises with lag only weakly near its operating angle, and more weakly the lower the duty. An
integral loop around a rotor that stiff only slightly is stable only below a gain that scales with
that stiffness. At low speed the servo's gain is above it, so the loop oscillates, and every start
passes through that region.
- **Evidence you can check without the model:** the same hunting appears at *constant* low speed with
  no ramp at all (duty peaks 40–60 % above its mean at 10 and 20 × 10⁶), and disappears from 40 × 10⁶
  up.
- **A desk model of the drive**, fitted on one parameter, reproduces both that pattern and the start's
  swings. It also shows that the 21° band and the uneven up/down gain (§3.2) are **not needed** to
  produce it.
- **The cure it points to:** give the servo the duty a speed needs in advance, and a gain that scales
  with duty. The next bench visit judges that change. The design is
  `DOCs/plans/DRIVE-INTEGRATION-DESIGN.md` §5.

Practical consequences:

- **It is structural.** Every start runs the same ramp and the same servo, so it happens every
  time, regardless of where the rotor stopped.
- **It is not immediate.** The surge arrives three-quarters of a second in, as the wheel
  accelerates — not at the command.
- **Alignment does nothing for it.** The startup peak is 90–120 counts at every offset pair
  measured. What alignment changes is the *steady* current around it: at 25° off optimum the
  motor draws ~109 counts continuously, so a surge to ~110 is not an event; at the shipped
  alignment the steady current is ~32, and the same surge is a **2.6–4.1× excursion you can
  feel through the frame.** Driving this motor well makes the start transient audible and
  palpable — not because the surge grew, but because everything around it got quiet.

⬚ Magnitude under load is not established — every trace above was taken wheels-up. §9, hole H-6.

---

## 7 · Current and power

### 7.1 What is measured and what is not

| | Status |
|---|---|
| Total bridge current | **MEASURED**, calibrated, 150 mV/A on Rev B |
| Per-phase voltages | **MEASURED**, carried separately since fmt 11 |
| Bus voltage | ⛔ **NOT MEASURED — assumed from the configured `DRIVE_VOLTAGE`** |
| Motor or board temperature | ⛔ not measured |
| Regenerative current | ⛔ undetermined — the shunt is low-side, so regen drives the sense node below ground; whether the Rev B amplifier sees it has not been established |

⚠ **Every power figure in this manual is a current measurement against an assumed voltage.**
There is no battery-voltage feedback anywhere in the system. A sagging pack looks identical to a
healthy one.

### 7.2 Protection limits

| Limit | Value | Basis |
|---|---|---|
| Peak, loop folds back | **40 A** | 0.75 × the MOSFET's package-limited 54 A at 100 °C case |
| Continuous, derated to | **27 A** | junction ≤ 125 °C at 50 °C ambient, 55 °C/W |
| Peak restored below | 80% of continuous | design |
| Averaging window | ~1 s | design |
| Fault (field outruns rotor) | 175.8° electrical | source |
| Blocked-rotor detection | ~1 s at the lag limit with no hall tick | source |

These protect the board, not the motor, and they are not user settings.

### 7.3 Current in normal running

At the shipped alignment, netted current at the same commanded speed, both motors:

| Motor | Rung | **at the shipped alignment** (neg / pos) | the same motor driven 25° off optimum | cost of that misalignment |
|---|---|---|---|---|
| LEFT | 3 | **130 / 129** | 1991 / 977 | 15.3× / 7.6× |
| LEFT | 4 | **230 / 242** | 5422 / 2636 | 23.6× / 10.9× |
| LEFT | 5 | **417 / 424** | 10879 / 5461 | 26.1× / 12.9× |
| RIGHT | 5 | **425 / 469** | 11016 / 5875 | 25.9× / 12.5× |

In calibrated amps at rung 6: **0.46 A** LEFT and **0.49 A** RIGHT at the shipped alignment,
against 7.40 A and 7.75 A at 25° off. MEASURED — `VISIT-7B-EVALUATION.md` §3. The right-hand
columns are the §5.3 basin measured on the running machine rather than on a sweep.

**Direction symmetry.** At the shipped alignment the reverse-over-forward current ratio is
**0.91–1.01** across rungs 2–5 on both motors. Forward and reverse now cost the same.

Three independent observables agree on this and they do not share a signal path: the current
sense channel, the duty servo's own demand (which fell from 83.7% to 53.9% at rung 5 and is not
read through the sense channel at all), and the fact that the commanded rate was met in both
cases to within 1%. **The machine turns the same wheel at the same speed for a fraction of the
current.**

⚠ A small residual asymmetry remains on the RIGHT motor (0.88–0.93 at rungs 4–7) and has
changed sign — the alignment slightly overshoots there. It is a few percent of a current that is
already 20× smaller. ⬚ §9, hole H-3.

### 7.4 What off-optimum current costs

From §5.3: 30° off optimum multiplies current by 12.7×. Most of that is not doing work — it is
circulating current producing no torque, and it comes out as heat in the MOSFETs and the
windings.

**This is the single largest lever on how hot the board runs and how long the battery lasts.**

### 7.5 Transitions

Changing speed produces a current kick above the settled value. At the shipped alignment the
worst kick fell from 1,247 to 204 counts and the mean positive kick from 261 to 50 — about 6×.
MEASURED. Kicks peak where duty saturates.

---

## 8 · Driving it well

Everything here follows from §§4–7 and cites the section it comes from.

**Alignment**

1. **Use Z = −4°, L = 18° (offsets 14 / 338).** Confirmed on two motors and two boards, by four
   independent routes (§4.3), and worth 15–26× in steady-state current (§7.3).
2. **Do not apply both the offset correction and a servo-setpoint change.** They add, and doing
   both mis-places the field by ~55° into a basin that is 12.7× steep over 30° (§3.3).
3. **Alignment is the highest-value thing you can get right on this motor** (§7.4). If the board
   runs hot or a direction costs more than the other, suspect alignment first.

**Speed**

4. **The shipped alignment is a quarter-speed tune.** It is close to optimal around 98 ticks/s
   (≈65 RPM) and progressively wrong as you go slower — 11–14° off at half that speed (§5.2).
5. **Stay off the duty ceiling** where you care about efficiency or about current readings
   meaning anything. Above the knee the drive is saturated (§6.3).
6. **Treat `MOTOR_CHOICE.md`'s speed figures as ~4% high** and as fault ceilings, not achieved
   speeds (§6.1).

**Starting and stopping**

7. **Expect a current surge at every start from rest**, ~2.6–4.1× the settled current, landing a
   few hundred milliseconds in (§6.4). If your mechanism cannot take it, ramp in from a low
   commanded speed rather than starting at target.
8. **Budget for it in power supply sizing** — it is the drive's worst relative excursion, and it
   is unaffected by alignment.

**Two-wheel platforms**

9. **The two motors face opposite directions**, so one wheel's forward is the other's reverse.
   That makes direction symmetry a two-wheel concern, not a nicety: at the shipped alignment
   the two directions cost the same current (§7.3), so driving in a straight line loads both
   wheels equally. An alignment that is symmetric about zero rather than about Z costs one
   wheel of every pair roughly double the current for the same speed.

**Measurement**

10. **Use Rev B boards for anything where current matters.** 150 mV/A against 5 mV/A is a 30×
    resolution difference (§3.1).
11. **Do not infer bus voltage from anything.** It is not measured (§7.1).

---

## 9 · What we do not know yet

Each hole names why it matters and what would settle it. States: **OPEN** ·
**CLOSED-UNANSWERABLE** · **FILLED**.

| # | Hole | State |
|---|---|---|
| **H-1** | **Which knob should carry the lead** — feedforward offset or servo setpoint. They add (§3.3), so the split is a real choice, and it matters because feedforward is instant while the servo is regulated, and because only a speed-dependent knob can track a speed-dependent optimum. | **OPEN** |
| | *What would settle it:* an A/B of two builds differing only in the servo setpoint (60° against 90°), each run at its own compensating lead so total field placement is held constant and the comparison isolates the split rather than re-testing placement. Run at the quarter rung, where the total is measured. | |
| **H-2** | **Why L falls with speed** — is the speed dependence a property of the motor (electrical time constant) or of our commutation scheme (loop lag)? The textbook model predicts the opposite sign (§5.2). This decides whether a speed law can be written down or must be measured per motor. | **OPEN** |
| | *What would settle it:* a third speed point, plus a test that separates the two — the motor's time constant does not care about our pass rate, and our loop lag does. | |
| **H-3** | **Are the six hall sectors equal?** No: they are unequal by about ±1° (§2.3). That is too small to matter to a 60° commutator, and it does **not** explain the residual RIGHT-motor asymmetry (§7.3), because RIGHT has the smaller spread. | **FILLED** |
| **H-4** | **Is the adopted alignment the global optimum?** About 35% of the electrical cycle has been swept (§4.4); one minimum per direction lies inside it. Theory says there should be only one, but that is an argument. | **OPEN** |
| | *What would settle it:* a full-cycle sweep, which needs a method that does not drive the motor into the current wall to get there. | |
| **H-5** | **The optimum at the half rung.** Five attempts, five distinct causes. The most recent is informative rather than a failure: the reachable arc there is 20° wide, torque-bounded at both ends, and the extrapolated optimum sits outside it (§6.2). | **OPEN**, and a candidate for **CLOSED-UNANSWERABLE** |
| | *What would settle it:* a sweep that can report *"the optimum is outside the reachable window"* as a result rather than failing to bracket. If that is the answer, this hole closes as unanswerable on this rig at this voltage, and that is a real finding about the motor. | |
| **H-6** | **The start surge under load.** Its shape is measured and its mechanism modelled (§6.4). Its magnitude under load is not: every trace was wheels-up. | **OPEN** |
| | *What would settle it:* the tethered, loaded floor run. | |
| **H-7** | **Can the board see regeneration?** The shunt is low-side, so regen drives the sense node below ground. Rev A almost certainly cannot see it; Rev B depends on the INA180B2 variant and its reference pin. | **OPEN** |
| | *What would settle it:* the INA180B2 datasheet, or a bidirectional external sensor. | |
| **H-8** | **Bus voltage.** Never measured (§7.1); every power figure rests on the configured nominal. | **OPEN** |
| | *What would settle it:* a divider and an ADC channel — a hardware addition, currently out of scope. | |
| **H-9** | **Per-direction speed ceilings.** The published ceilings are single numbers applied to both directions, and no per-direction ceiling has ever been measured. With the direction asymmetry now removed, they should converge — which is itself a prediction nobody has tested. | **OPEN** |
| | *What would settle it:* a speed ladder run to the fault edge in both directions at the shipped alignment. | |
| **H-10** | **Whether the drive knows it is following.** The driver carries a measured-rate-versus-commanded reading with no ceiling, which is what a droop would show up in — but the reading is not yet trustworthy end to end. | **OPEN** |
| | *What would settle it:* a scan run re-judging the reading against a corrected denominator. | |
| **H-11** | **Unit-to-unit variation.** Every measurement in this manual comes from the **two** units on the Rev B platform. Z agrees within 0.55° between them — encouraging, and not a population. **Four units of this motor exist**: two on the Rev B platform and two on a Rev A platform. | **OPEN** |
| | *What would settle it:* the other two units. They divide into two measurements with very different prerequisites — see §9.1. | |

### 9.1 · What the Rev A pair can contribute, and when

The second pair is a real chance to turn single-platform numbers into a population of four, but
the two quantities are not equally available, and the difference is the current channel.

**Z — the hall zero — needs no current and no drive.** It is measured with the bridge
**coasting**: the motor is never powered, the wheel is turned by hand, and the hall zero comes
from the phase voltages the motor generates itself. Nothing in that method reads the
current-sense channel, so Rev A's 30×-coarser sense (§3.1) does not degrade it, and nothing can
fault, abort on current, or run away because nothing is ever driven. **This measurement does not
wait on the driver work at all.**

⬚ One thing to check before assuming it ports: our code scales the three phase channels from
the P2's own GIO/VIO calibration, with no board-revision term anywhere in that path — only the
*current* channel carries a per-revision constant. That says our **software** treats the phase
channels identically on both boards. Whether the two **boards** present phase voltage at the
same scale is not addressed by the vendor comparison in `BOARD-REVISION-FACTS.md`, which covers
the current sense and the gate driver and is silent on phase sensing. Confirm it before trusting
a Rev A phase reading, or the first Rev A leg is measuring the board.

**L — the lead — needs the motor driven, and that is the part that waits.** Two reasons, both
real:

1. **Safety.** Rev B exists because Rev A boards were damaged in service, and the protection Rev
   A lacks is a current limit. The driver work adds exactly that (§7.2). Driving a Rev A board
   hard before it lands is spending a board to learn something the Rev B pair already told us.
2. **Resolution.** L is found by locating a *current minimum*, and Rev A presents current to the
   ADC at 5 mV/A against Rev B's 150 mV/A. At the shipped alignment the whole signal is a few
   hundred millivolts on Rev B, so the same measurement on Rev A sits in the bottom two percent
   of the range. Expect materially wider error bars, and say so rather than comparing a Rev A L
   to a Rev B L as though the two had equal weight.

**So the sequence is: Z on the Rev A pair is available early and cheaply and would take the
population from two to four on the one quantity that is pure motor geometry. L on the Rev A pair
waits for the current limit, and arrives with a worse error bar than anything in §5.2.**

⭐ That split is worth noticing on its own: **the quantity that belongs to the motor is the one
that can be measured on any board, and the quantity that belongs to our driver is the one that
depends on which board it is.** That is §1.3's attribution showing up as a scheduling fact.

---

## 10 · Sources

| Source | What it supplies |
|---|---|
| `DOCs/analyses/bench/2026-09-22/VISIT-7C-EVALUATION.md` | Z and L at two rungs both motors; the start-transient traces; the half-rung arc |
| `DOCs/analyses/bench/2026-09-22/VISIT-7C-PASS2-EVALUATION.md` | Z measured cold from back-EMF; hall-sector widths; hall lag; the start transient's shape; back-EMF as a position source |
| `DOCs/analyses/bench/2026-09-21/VISIT-7B-EVALUATION.md` | the alignment A/B; current collapse; direction symmetry; the duty knee; the start surge in context |
| `DOCs/analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` | the hand-rotation pole count |
| `DOCs/analyses/BOARD-REVISION-FACTS.md` | vendor hardware facts, sense scaling, dead-time, MOSFET ratings |
| `DOCs/analyses/BLDC-COMMUTATION-PRINCIPLES.md` | the board designer's principles, and the two-motor comparison |
| `src/isp_bldc_motor.spin2` | every driver constant quoted in §3 |
| `MOTOR_CHOICE.md` | the published speed/voltage table (see §6.1's caveat) |

Bench logs referenced by name live beside their evaluations under `DOCs/analyses/bench/`.

---

## 11 · Revision history

| Date | Change |
|---|---|
| 2026-09-22 | First issue. Sections 2–8 describe current understanding; section 9 opens eleven holes, and §9.1 states what the second pair of units can add. |
| 2026-09-22 | §4 gains the cold back-EMF measurement of Z. §6.4 rewritten: the start surge is the duty servo hunting as the ramp accelerates, not a wait at the setpoint — the earlier account did not survive a seed that removed the wait. §3.2 corrected against the code: the phase function is sine, `err_`'s sign, and the servo's band. H-6 reworded to match. |
| 2026-09-22 | §2.3 states the measured sector widths, and H-3 is FILLED. The earlier update left both still saying the sectors had never been measured. |
| 2026-09-22 | §4.6 (how back-EMF locates the magnets) and §4.7 (what differs from unit to unit, including hall lag) added, drawn from the board designer's questions. |
| 2026-09-22 | §6.4's open question is answered by a desk model: the hunting is a gain-against-stiffness limit cycle, shown at constant low speed as well as at starts. The band and the gain asymmetry are no longer suspects. The bench certification is pending. |
