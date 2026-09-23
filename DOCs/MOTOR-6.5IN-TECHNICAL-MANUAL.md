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
| Direction-to-direction current asymmetry | was **ours**, and is gone but for a few percent on one unit (§7.3) |
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
5. sets `duty` as a **feedforward** from the field's speed plus an integral **trim** that holds
   `|err_|` at the setpoint (below).

Separately, once a millisecond, the front cog re-derives the offset pair from the speed, using the
lead table in §5.2.

| Constant | Value | Label |
|---|---|---|
| PWM / ADC frame rate | 44,000 Hz → **22.7 µs per frame** | DERIVED from `PWM_RATE_IN_HZ` |
| Drive passes (speed updates) | one per 23 frames → **1,913 passes/s** | DERIVED, `DRIVE_PASS_FRAMES = 23` |
| Field angle resolution | 32-bit fraction of an electrical cycle | source |
| Rotor angle resolution | **6 positions per electrical cycle** (one per hall sector) | source |
| Error representation | 8-bit signed, **256 counts per electrical cycle** (1 count = 1.4°) | source |
| Duty servo setpoint | `SERVO_SETPOINT` **48 counts = 67.5°** | source |
| Duty feedforward | the magnitude of `drv_incr` × `duty_max` ÷ `ff_ceiling`, where `ff_ceiling` is the motor's back-EMF line (duty 167–174 per 10⁶ of increment at 18.5 V), kept apart from the speed ceiling | source; the line MEASURED |
| Duty trim | each frame adds (the magnitude of `err_` − 48) × (duty ÷ 16) to an accumulator, applied shifted right 14: symmetric, untruncated, and with a gain that scales with duty | source |
| What the servo actually holds | a **point**: mean `err` **47–48 counts** at every rung from 1 to 8, both motors, both directions | MEASURED — `VISIT-8-EVALUATION.md` §3.2 |
| Duty floor / ceiling at 270 MHz | `duty_min` **1,600** · `duty_max` **27,648**, the largest amplitude the PWM carries without clipping after the drive re-centres the three levels each frame | DERIVED from frame and dead-gap; MEASURED clip-free, least room left 2 counts against the desk's 1–2 — `VISIT-9-EVALUATION.md` §2.3 |
| Dead gap applied | 260 ns (compliant with the 250 ns minimum) | source |
| Lag: ramp waits | `LAG_SOFT` 80 counts = **112.5°** | source |
| Lag: field stops advancing | `LAG_HOLD` 100 counts = **140.6°** | source |
| Lag: fault | 125 counts = **175.8°** | source |

### 3.3 The two knobs that place the field — and they add

This is the single most important thing to understand about driving this motor, and the easiest
thing to get wrong.

**Where the field sits relative to the rotor in steady state is set by two separate numbers that
add together:**

- the **commutation offset**, added to the hall angle before the error is formed. It takes
  effect instantly and does not depend on the servo.
- the **duty servo setpoint**, 67.5°. The trim moves `duty` until `|err_|` settles there, so
  the rotor ends up trailing the field by the setpoint.

Total steady-state field placement is the **sum**. Two consequences follow:

1. ⚠ **A correction applied to both knobs is applied twice.** The board designer's principle
   says drive at ±90° electrical, and the setpoint is below that; the offset's lead makes up the
   difference. Moving the setpoint as well would count the same correction twice, and given how
   steep the current basin is (§7.4: 12.7× over 30°), that is not marginal.
2. **The two knobs behave differently in time.** The offset is instant; the setpoint is reached
   through the servo, which is regulated.

**So the drive carries the lead in the offset and keeps the setpoint fixed.** The offset is the
knob that can follow speed at once, and the lead has to follow speed (§5.2). At every speed the
lead table sits inside the measured region of least current, so no other split of the same total
placement can lower the steady current further.

### 3.4 What the driver does *not* do

| The board designer's principle | What we do |
|---|---|
| Place power at ±90° electrical from the rotor | The duty servo holds **67.5°**, and the offset adds a lead that varies with speed |
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
drive parameter, not a motor property. The two combine into the offset pair:

```
offset_fwd = Z + L      applied to NEGATIVE increments
offset_rev = Z − L      applied to POSITIVE increments
```

Z is a constant (−4°). L comes from the table in §5.2, by speed, so the front cog re-derives the
pair as the speed changes. The fixed pair **14 / 338** (L = 18°) is written only at start-up,
before the front cog runs.

### 5.2 L depends strongly on speed — and not the way theory predicts

The lead of least net current at four speeds, one octave apart, under the current servo:

| Rung | Increment | Lowest-current lead, both motors and directions | Flat region | Table |
|---|---|---|---|---|
| **eighth** | 18.4 × 10⁶ (49 ticks/s) | 13–23° | 13–23° within ~6 mV | **20.5°** |
| **quarter** | 36.75 × 10⁶ (98 ticks/s) | −2 to 8° | −2 to 8° within ~15 % | **5°** |
| **half** | 73.5 × 10⁶ (196 ticks/s) | 3–8° | 3 and 8° within 1–3 % | **8°** |
| **full** | 147 × 10⁶ (393 ticks/s) | 8° | 13° costs 2× | **8°** |

MEASURED, from two runs, counting only steps at which the wheel held its commanded rate —
`DOCs/analyses/bench/2026-09-22/VISIT-8-EVALUATION.md` §3.5 and `VISIT-8B-EVALUATION.md` §3.6. Every
table value sits inside its flat region. Between points the drive interpolates linearly; outside
the table it holds the end value and never extrapolates.

**L falls by about 15° from the eighth to the quarter, then holds at 3–8° up to full speed.**
The earlier servo, which held a band rather than a point, measured 27.8 / 28.3° at the eighth and
15.85 / 15.55° at the quarter, falling 12.2° per doubling. The servo change moved the whole curve.
That is what a drive parameter does, and it is why L is not quoted as a property of the motor.

⚠ **The textbook current-lag model gives the wrong sign here.** The standard argument is that
current lags applied voltage more at higher electrical frequency, so the *voltage* lead needed
to place the *current* at 90° should **grow** with speed. On both servos we measure the reverse, or
at best a flat line. Do not design from that model on this motor. Why the real behaviour goes the
other way is not established — §9, hole H-2.

**The practical consequence:** Z is safe in a compile-time constant. L is not, and no fixed number
serves the whole range: on the same drive, the table draws 24–78 % less current than a flat 18° at
rungs 3–8, because 18° over-leads everywhere above the eighth. The table's benefit against the
earlier drive is in §7.3.

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

The speed command is an angle increment applied 1,913 times a second. `power` 100 commands the
ceiling increment and `power` 1 the floor.

| | Value | Label |
|---|---|---|
| Drive passes per second | 1,913 | DERIVED |
| Ceiling increment at 18.5 V | **165,000,000** | MEASURED — `VISIT-9-EVALUATION.md` §6a; held through the public API, `VISIT-9B-EVALUATION.md` §3 |
| → electrical frequency | **73.5 Hz** | DERIVED |
| → hall ticks per second | **441** | DERIVED |
| → wheel speed | **294 RPM** | DERIVED |
| → rim speed | **2.54 m/s** (5.7 mph) | DERIVED |
| Floor increment | **100,000** → 0.27 ticks/s, ~0.2 RPM | MEASURED: every rung down to it rotated steadily at exactly its commanded rate; the lowest tried, so the true floor is lower — `VISIT-9-EVALUATION.md` §4 |
| Ceiling at the other supply voltages | 165 × 10⁶ scaled by voltage, rounded down | DERIVED: the earlier measured rows followed that line to within 2.5 % |

**How the ceiling is chosen.** It is the fastest measured speed that keeps the unloaded duty
reserve the drive has always shipped with: at 165 × 10⁶ duty runs at 92–93 % of its ceiling, on
both motors and in both directions. It is not the speed at which the wheel stops following, which
is far higher (§6.3). How much of that reserve survives a load is not yet measured (§9).

Every speed figure here is wheels-up. Bench work uses fixed increments as "rungs"; the eighth
(18.4 × 10⁶, 49 ticks/s) and the quarter (36.75 × 10⁶, 98 ticks/s) appear throughout this manual.

### 6.2 The two walls

Moving the lead away from its optimum at a fixed commanded speed, the motor stops running well
for **two different reasons**, and they are not the same wall:

| Wall | Side | What happens |
|---|---|---|
| **Current wall** | too much lead | Current explodes, and the run aborts on the current cap. |
| **Torque wall** | too little lead | The motor cannot make enough torque. The rotor falls behind the field: it slows, or the field outruns it and it faults. |

At 90° from optimum, torque is zero at any speed. The reachable arc is the band between the two
walls, and **it narrows as speed rises**. Under the earlier servo the half-rung arc was only 20°
wide and excluded that servo's optimum.

**Under the current drive the optimum is inside the reachable arc at every rung.** The lead was
stepped from 33° down to −7° in 5° steps at all four rungs. All 16 minima were bracketed, and no
step faulted. The torque wall appears as slowing, not as a fault: at the eighth, −2° held only 51 %
of the commanded rate and −7° never settled.
MEASURED — `VISIT-8-EVALUATION.md` §3.5, `VISIT-8B-EVALUATION.md` §3.6.

### 6.3 The duty ceiling

Above a certain speed the drive runs out of voltage: duty reaches its ceiling and can rise no
further. That knee is a **voltage / back-EMF limit**, not a commutation defect.

**Where the knee sits.** With the clip-free duty ceiling (27,648 counts, §3.2), duty first caps
between 175 and 185 × 10⁶ on all four wheel-directions. The old ceiling of 24,264 capped it between
155 and 165 × 10⁶. The raise moved the knee up 13 % and changed nothing below it: net current at
rungs 3–8 agrees within ±10 % or ±5 mV, and duty within 0.5 %. MEASURED — `VISIT-9-EVALUATION.md`
§2.

**Above the knee the wheel still follows, by field weakening.** With duty pinned, the only way to
advance the rotor further is more lead. `err` grows from 48 to 65 counts, about 24° more field
advance, and the wheel keeps its commanded rate up to 245 × 10⁶, the highest command tried. It pays
in current. On the clip-free ceiling it draws 2.3–2.6 A at 245 × 10⁶ unloaded, against 0.3–0.4 A
at the knee. The old ceiling needed 3.8–4.2 A for the same speed. MEASURED — `VISIT-9-EVALUATION.md`
§2.1–2.2.

⚠ **Field-weakened running can slip.** The RIGHT motor, driven forward, lost synchronism between
235 and 245 × 10⁶ on three consecutive runs, with a current peak of about 23–25 A and no fault. The
other three wheel-directions held 245 × 10⁶. That is why the ceiling (§6.1) sits below the knee,
with reserve, rather than at the speed where following ends. MEASURED — `VISIT-9B-EVALUATION.md` §2.

**Alignment moves the knee as well.** Filling the lead table unpinned 147 and 155 × 10⁶, which the
flat 18° lead had held at the ceiling (`VISIT-8B-EVALUATION.md` §3.5). So alignment buys headroom
as well as current.

### 6.4 Starting from rest — the transient

**A start from rest is quiet.** The current rises smoothly to the settled value, and duty does
not swing on the way:

| Start to the quarter, both motors, both directions | Largest duty drop while accelerating | Peak current ÷ settled |
|---|---|---|
| This drive | **0.01–0.03** | **1.15–1.53** |
| The earlier drive | 0.34–0.53 | 1.94–3.04 |

MEASURED over two runs — `VISIT-8-EVALUATION.md` §3.1, `VISIT-8B-EVALUATION.md` §3.2.

**Why the earlier drive surged.** Its servo was integral-only, with a fixed gain. The rotor's
torque rises with lag only weakly near its operating angle, and more weakly the lower the duty.
An integral loop around a rotor that is only slightly stiff is stable only below a gain that
scales with that stiffness. At low speed the old gain was above that limit, so the loop hunted on a
~150 ms cycle, and every start passed through that region. It hunted at *constant* low speed too.
The current drive gives the servo the duty a speed needs in advance (the feedforward) and a trim
whose gain scales with duty (§3.2). That removed the surge, as a desk model of the drive had
predicted, with both start figures landing inside the model's predicted ranges.

**What remains at the lowest speeds.** At rungs 1–2 (10 and 20 × 10⁶) duty still swings, 178–399 counts
against 800–1,650 before, and `err` still peaks at 76–86 counts around its mean of 48. It is a
small residual, not a surge.

**Faster ramps.** Starts at two and four times the default acceleration also follow cleanly, with
zero lag-limiter holds. Their current peak grows with the acceleration, as it must (1.26–1.34 ×
settled at the default rate, 1.51–1.83 at twice it and 1.57–2.13 at four times), and in absolute
terms it stays at about 0.2 A. Slowing down produces no surge at either rate tried: the current
only falls. MEASURED — `VISIT-9-EVALUATION.md` §3.

Every trace here was taken wheels-up. How a start behaves under load is §9, hole H-6.

---

## 7 · Current and power

### 7.1 What is measured and what is not

| | Status |
|---|---|
| Total bridge current | **MEASURED**, calibrated, 150 mV/A on Rev B |
| Per-phase voltages | **MEASURED**, carried separately since fmt 11 |
| Bus voltage | ⛔ **NOT MEASURED — assumed from the configured `DRIVE_VOLTAGE`** |
| Motor or board temperature | ⛔ not measured |
| Regenerative current | ⛔ **not visible** — the shunt is low-side, so regen drives the sense node below ground, and Rev B's amplifier is a one-direction part with no reference pin (§9, H-7) |

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

**What alignment is worth.** Netted current at the same commanded speed on the earlier drive, both
motors, aligned (offsets 14 / 338) and driven 25° off optimum:

| Motor | Rung | **aligned** (neg / pos) | the same motor driven 25° off optimum | cost of that misalignment |
|---|---|---|---|---|
| LEFT | 3 | **130 / 129** | 1991 / 977 | 15.3× / 7.6× |
| LEFT | 4 | **230 / 242** | 5422 / 2636 | 23.6× / 10.9× |
| LEFT | 5 | **417 / 424** | 10879 / 5461 | 26.1× / 12.9× |
| RIGHT | 5 | **425 / 469** | 11016 / 5875 | 25.9× / 12.5× |

In calibrated amps at rung 6: **0.46 A** LEFT and **0.49 A** RIGHT aligned, against 7.40 A and
7.75 A at 25° off. MEASURED — `VISIT-7B-EVALUATION.md` §3. The right-hand columns are the §5.3
basin measured on the running machine rather than on a sweep.

Three independent observables agree on this and they do not share a signal path: the current
sense channel, the duty servo's own demand (which fell from 83.7% to 53.9% at rung 5 and is not
read through the sense channel at all), and the fact that the commanded rate was met in both
cases to within 1%. **The machine turns the same wheel at the same speed for a fraction of the
current.**

**The current drive goes further.** With the lead following speed (§5.2), net current at rungs
3–8 is a further **22–74 % below** the aligned earlier drive, and the saving grows with speed:
22–27 % at rung 3, 70–74 % at rung 7. Duty falls 5–13 % with it, and speed tracks within
0.04–0.47 % at rungs 4–8. MEASURED — `VISIT-8B-EVALUATION.md` §3.3.

**Direction symmetry.** On the current drive the LEFT motor's two directions draw the same current
to within 1–4 % at every rung from 40 to 140 × 10⁶. The RIGHT motor keeps a small residual: its
negative direction draws 2–8 % less than its positive one (for example 264 against 286 mV × 10 at
100 × 10⁶), the same size as on the earlier drive. It is a few percent of a current that is already
an order of magnitude smaller than misaligned. MEASURED — `VISIT-9-EVALUATION.md` §2.3.

### 7.4 What off-optimum current costs

From §5.3: 30° off optimum multiplies current by 12.7×. Most of that is not doing work — it is
circulating current producing no torque, and it comes out as heat in the MOSFETs and the
windings.

**This is the single largest lever on how hot the board runs and how long the battery lasts.**

### 7.5 Transitions

Changing speed produces a current kick above the settled value, which you can feel as a small
jolt. Each drive change has made it smaller. Aligning the earlier drive cut the worst kick from
1,247 to 204 counts (`VISIT-7B-EVALUATION.md`). With the lead table in place, the mean peak current at a
speed change is 79–84, against 116–125 with a flat 18° lead, and the worst is 253–270. MEASURED —
`VISIT-8B-EVALUATION.md` §3.7.

The largest kicks come where duty is pinned, above the knee (§6.3): there the drive has no voltage
left to absorb a change. Below the knee the kick is smaller but still present in both directions.

---

## 8 · Driving it well

Everything here follows from §§4–7 and cites the section it comes from.

**Alignment**

1. **Use Z = −4° and a lead that follows speed.** Z is confirmed on two motors and two boards, by
   five independent routes (§4.3). The lead comes from the table in §5.2. Aligned, the motor draws
   15–26× less current than 25° off (§7.3), and letting the lead follow speed saves a further
   22–74 %.
2. **Carry the lead in the offset; never move the servo setpoint to chase it.** The two add, and
   changing both mis-places the field in a basin that is 12.7× steep over 30° (§3.3).
3. **Alignment is the highest-value thing you can get right on this motor** (§7.4). If the board
   runs hot or a direction costs more than the other, suspect alignment first.

**Speed**

4. **No fixed offset pair suits the whole speed range.** The lowest-current lead falls about 15°
   between the eighth and the quarter rung (§5.2). A fixed pair is a one-speed tune.
5. **Stay below the duty knee** where you care about efficiency or about current readings meaning
   anything. `power` 100 keeps about 7 % unloaded duty reserve. Above the knee the wheel follows
   only by field weakening, draws amps unloaded, and can slip with a 23–25 A peak (§6.3).
6. **Every speed figure is wheels-up.** The reserve left under load is not yet measured (§6.1).

**Starting and stopping**

7. **A start from rest is quiet on this drive.** Its current peaks at about 1.2–1.5× the settled
   value (§6.4). A faster ramp draws more because it accelerates harder, not because it surges.
8. **Size the supply for acceleration and for speed changes**, not for a start surge (§6.4, §7.5).

**Two-wheel platforms**

9. **The two motors face opposite directions**, so one wheel's forward is the other's reverse.
   That makes direction symmetry a two-wheel concern, not a nicety. Aligned, the two directions
   cost the same current to within a few percent (§7.3), so driving in a straight line loads both
   wheels almost equally. An alignment that is symmetric about zero rather than about Z costs one
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
| **H-1** | **Which knob should carry the lead.** The offset carries it, following speed, and the servo setpoint stays fixed at 67.5° (§3.3). At every speed the lead table sits inside the measured region of least current, so no other split of the same total placement can lower the steady current (§5.2). The servo that holds the fixed setpoint also removed the start surge (§6.4). | **FILLED** |
| **H-2** | **Why L falls with speed** — is the speed dependence a property of the motor (electrical time constant) or of our commutation scheme (loop lag)? Four speed points now exist: L falls about 15° from the eighth to the quarter, then holds at 3–8° to full speed (§5.2). The textbook model predicts the opposite sign. This decides whether a speed law can be written down or must be measured per motor. | **OPEN** |
| | *What would settle it:* a test that separates the two. The motor's time constant does not care about our drive-pass rate, and our loop lag does, so the lead run repeated on a build with a different pass rate would tell them apart. No such run has been planned. | |
| **H-3** | **Are the six hall sectors equal?** No: they are unequal by about ±1° (§2.3). That is too small to matter to a 60° commutator, and it does **not** explain the residual RIGHT-motor asymmetry (§7.3), because RIGHT has the smaller spread. | **FILLED** |
| **H-4** | **Is the adopted alignment the global optimum?** About 35% of the electrical cycle has been swept (§4.4); one minimum per direction lies inside it. Theory says there should be only one, but that is an argument. | **OPEN** |
| | *What would settle it:* a full-cycle sweep, which needs a method that does not drive the motor into the current wall to get there. The offset sweep cannot do it, since the walls are what bound it. | |
| **H-5** | **The optimum at the half rung.** **3–8°**, flat to within 1–3 % across that range on both motors, with the table at 8° (§5.2). The current drive's reachable arc contains it (§6.2). | **FILLED** |
| **H-6** | **Behaviour under load.** Every number in this manual was taken wheels-up. Not yet measured: how a start behaves under load (§6.4), how much of the ceiling's 7 % duty reserve a load leaves (§6.1), and whether the lead table's saving holds under load (§5.2). | **OPEN** |
| | *What would settle it:* the tethered, loaded floor run. It is planned, and it waits on the attended display panel it needs. | |
| **H-7** | **Can the board see regeneration?** No. The shunt is low-side, so regeneration drives the sense node below ground. Rev B's INA180 is the one-direction member of its family, with no reference pin (the vendor names the INA181 as the version that measures both directions), so a reversed current reads as zero. Rev A feeds the node to the ADC with no offset and almost certainly cannot see it either. ASSUMED (vendor, TI's INA180 product page); not measured. | **FILLED** |
| **H-8** | **Bus voltage.** Never measured (§7.1); every power figure rests on the configured nominal. The board has no voltage channel, and the external front end that would add one is outside the current work. | **CLOSED-UNANSWERABLE** on this rig |
| **H-9** | **Per-direction speed ceilings.** The same in both directions. Duty first caps between 175 and 185 × 10⁶ on all four wheel-directions, and the ceiling is chosen below that (§6.3). The one difference is above the knee: RIGHT forward loses its field-weakened synchronism between 235 and 245 × 10⁶, and the other three hold 245 × 10⁶. No fault edge was reached, because 245 × 10⁶ was the highest command tried. | **FILLED** |
| **H-10** | **Whether the drive knows it is following.** Yes. The driver's own reading of measured rate against commanded rate agrees with an independent hall count with a gap of 0 points over 75 rungs, and also when the wheel falls short to 2–4 % of its command. The falling case was shown on three of the four wheel-directions; RIGHT forward's step did not run. MEASURED — `VISIT-9B-EVALUATION.md` §3. | **FILLED** |
| **H-11** | **Unit-to-unit variation.** Every measurement in this manual comes from the **two** units on the Rev B platform. Measured cold, Z agrees within 0.06° between them — encouraging, and not a population. **Four units of this motor exist**: two on the Rev B platform and two on a Rev A platform. | **OPEN** |
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

**L — the lead — needs the motor driven, and that is the part that costs more.** Two reasons,
both real:

1. **Safety.** Rev B exists because Rev A boards were damaged in service, and the protection Rev
   A lacked is a current limit. The driver now has one (§7.2), so a driven Rev A leg is possible.
   It is still a risk to a board that is hard to replace, and it would re-measure a drive parameter
   the Rev B pair has already given, so it is worth running only for a question the Rev B pair
   cannot answer.
2. **Resolution.** L is found by locating a *current minimum*, and Rev A presents current to the
   ADC at 5 mV/A against Rev B's 150 mV/A. At the shipped alignment the whole signal is a few
   hundred millivolts on Rev B, so the same measurement on Rev A sits in the bottom two percent
   of the range. Expect materially wider error bars, and say so rather than comparing a Rev A L
   to a Rev B L as though the two had equal weight.

**So the sequence is: Z on the Rev A pair is cheap and would take the population from two to four
on the one quantity that is pure motor geometry. L on the Rev A pair is possible now that the
current limit exists, but it risks the board and arrives with a worse error bar than anything in
§5.2.**

⭐ That split is worth noticing on its own: **the quantity that belongs to the motor is the one
that can be measured on any board, and the quantity that belongs to our driver is the one that
depends on which board it is.** That is §1.3's attribution showing up as a scheduling fact.

---

## 10 · Sources

| Source | What it supplies |
|---|---|
| `DOCs/analyses/bench/2026-09-23/VISIT-9B-EVALUATION.md` | the ceiling and floor held through the public API; the driver's following reading, holding and falling; RIGHT forward's slip |
| `DOCs/analyses/bench/2026-09-23/VISIT-9-EVALUATION.md` | the speed ceiling, the floor, the clip-free duty ceiling, field weakening above the knee, ramps, direction symmetry on the current drive |
| `DOCs/analyses/bench/2026-09-22/VISIT-8B-EVALUATION.md` | the lead table confirmed; cruise current against the earlier drive; the top of the range freed; speed-change kicks |
| `DOCs/analyses/bench/2026-09-22/VISIT-8-EVALUATION.md` | the start surge gone; the servo holding a point; the lead against speed under the current servo |
| `DOCs/analyses/bench/2026-09-22/VISIT-7C-EVALUATION.md` | Z and L at two rungs both motors under the earlier servo |
| `DOCs/analyses/bench/2026-09-22/VISIT-7C-PASS2-EVALUATION.md` | Z measured cold from back-EMF; hall-sector widths; hall lag; the start transient's shape; back-EMF as a position source |
| `DOCs/analyses/bench/2026-09-21/VISIT-7B-EVALUATION.md` | the alignment A/B; current collapse; direction symmetry; the duty knee; the start surge in context |
| `DOCs/analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` | the hand-rotation pole count |
| `DOCs/analyses/BOARD-REVISION-FACTS.md` | vendor hardware facts, sense scaling, dead-time, MOSFET ratings |
| `DOCs/analyses/BLDC-COMMUTATION-PRINCIPLES.md` | the board designer's principles, and the two-motor comparison |
| `src/isp_bldc_motor.spin2` | every driver constant quoted in §3, the lead table, the ceiling and floor |
| TI, INA180 product page (`ti.com/product/INA180`) | the amplifier is the one-direction member of its family |

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
| 2026-09-23 | Brought to the current drive: the feedforward-and-trim servo holding 67.5° (§3.2–3.4), the lead table that follows speed (§5), the 165 × 10⁶ ceiling, the 100,000 floor, the clip-free duty ceiling and field weakening above the knee (§6.1–6.3), the quiet start (§6.4), and cruise current, direction symmetry and speed-change kicks (§7.3, §7.5). §8 rewritten to match. Section 9: H-1, H-5, H-7, H-9 and H-10 FILLED; H-8 CLOSED-UNANSWERABLE; H-6 widened to cover everything under load; H-2 gains the new speed points. §9.1: the current limit has landed. |
