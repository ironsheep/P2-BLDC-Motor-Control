# The 6.5″ hub motor — a technical manual

**What it is, how the 64010 board drives it, and where it wants to run.**

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

This manual describes the Parallax hoverboard-style 6.5-inch motor-in-wheel (`MOTR_6_5_INCH`)
as we have actually measured it, and how to get good behaviour out of it with the Parallax
64010 Universal Motor Driver board.

It is written for someone who wants to understand this motor — not a motor designer, but not a
beginner either. Section 3 assumes you know what PWM is. Nothing else assumes much.

If you are bringing up a *different* motor, read this as the worked example for
[ADDING_MOTOR.md](ADDING_MOTOR.md): every property it asks you to measure is measured here, and
the methods are explained in [TECHNIQUES.md](TECHNIQUES.md).

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

### 1.2 Where each number comes from

Every table says how its numbers were obtained:

| Basis | Means |
|---|---|
| **measured** | measured on our hardware — two units of this motor on a Rev B board, wheels lifted unless stated — with its error where we have one |
| **calculated** | worked out from measured values or from the driver's constants; the arithmetic is shown |
| **vendor** | taken from a datasheet or a Parallax manual, not checked on our hardware |
| **driver** | a constant or behaviour of the driver in `src/isp_bldc_motor.spin2` |

A number without an error bar is a number claiming more precision than it has. Where we have
a spread or a standard error, it is printed.

### 1.3 Motor, driver, instrument — the three things this manual keeps apart

A lot of what one observes on a bench is a property of the *system*, not of the motor. This
manual attributes every quantity, because getting that wrong is how a "motor specification"
becomes misleading:

| Quantity | Belongs to |
|---|---|
| Pole count, hall geometry, the hall zero **Z**, winding resistance | the **motor** — durable, transfers with any driver |
| The lead **L**, the servo setpoint, the offsets, the fault limit, how it stops and holds | the **driver** — our choices, not the motor's properties |
| Whether L's speed dependence is the motor's electrical time constant or our commutation lag | **not separated** — §9 |
| Current readings in mV, the abort thresholds | the **instrument** |

### 1.4 What is not settled

Open questions are marked ⬚ where they arise and collected in §9. Strike every one of them and
§§2–8 remain a complete description of the motor and how to drive it.

---

## 2 · The motor

### 2.1 Construction and geometry

| Property | Value | Basis |
|---|---|---|
| Type | 3-phase BLDC hub motor; the stator is the axle, the rotor is the wheel | vendor |
| Magnets (poles) | **30** | measured, §2.2 |
| Pole pairs / electrical cycles per wheel revolution | **15** | measured, §2.2 |
| Position sensing | 3 hall sensors, 120° apart electrically | vendor |
| Hall states per electrical cycle | **6** | measured |
| Hall ticks (transitions) per wheel revolution | **90** | measured, §2.2 |
| Mechanical degrees per hall tick | **4°** | calculated (360 / 90) |
| Wheel outside diameter | 6.5 in = 165.1 mm | vendor (nameplate) |
| Wheel circumference | 518.6 mm | calculated (π × 165.1) |
| Travel per hall tick | **5.76 mm** | calculated (518.6 / 90) |
| Hall state sequence | positive power (ticks rising): 1-5-4-6-2-3 · negative power (ticks falling): 1-3-2-6-4-5 | driver (`deltas65`), and measured |
| Winding resistance, phase to phase | **≈ 0.48 Ω** (every pair 0.41–0.55 Ω) | measured, §2.4 |

There is **no shaft**. The motor *is* the wheel, so there is nowhere to mount a shaft encoder
— which is why every position fact below had to be obtained from the halls or by hand.

### 2.2 How the 90 ticks were counted

With the motor unpowered, a wheel was turned **three full revolutions by hand** and the hall
transitions counted:

```
T0-12,begin,told_direction,CW_FROM_HUB,revolutions,3,wheel,RIGHT_P16
T0-12,end,transitions,270,illegal,0,pos,-270,final_hall_code,6
```

270 ÷ 3 = **exactly 90 ticks per revolution**, hence 15 electrical cycles and 30 magnets. The
starting and final hall codes match (as they must after a whole number of cycles) and no illegal
hall state occurred.

Note what this measurement does *not* use: no library constant appears anywhere in it. A human
supplied the ground truth and a counter counted edges. Checks that *look* like confirmations
but are circular — the mm-per-tick arithmetic, a speed sweep, comparing the driver's RPM with a
program's RPM — all divide by the same 90 they would be confirming.

### 2.3 Hall sensor health, as observed

Across every run on both units: no missed transitions and no illegal hall states. The driver's
start check has read legal halls at every start; the only exception was a deliberately unplugged
hall connector, and it was caught every time.

The halls are the one sensor in this system that has never given us a bad reading.

### 2.4 The windings

The driver measures the resistance itself, at start, when a program asks it to. It drives each phase
pair in turn (U→V, V→W, W→U) at 5 % duty and waits until the halls have been still for 30 ms, because a
turning rotor's back-EMF would bias the reading. It then reads the DC-link current on the shunt:
R = d² × V × rSense ÷ net mV.

| | LEFT | RIGHT | Basis |
|---|---|---|---|
| Every pair, on the measured pack voltage (20.72 V) | 454–552 mΩ | 406–515 mΩ | measured |
| Mean over two starts | **501 mΩ** | **467 mΩ** | measured |
| The two units | 7 % apart | | measured |

The supply voltage matters here: computed with the *nominal* 18.5 V instead of the measured 20.72 V,
the same readings come out 12 % low — exactly the ratio 18.5 / 20.72. The negative case is exact: with
one lead withheld in firmware, the two pairs through that lead read "not visible" and the third still
measures, in 10 of 10 starts.

**How good the number is.** Each reading is only 14–19 mV on the shunt, and one millivolt moves R by
about 6 %, so a single pair is good to about **±6 %**. Take **≈ 0.48 Ω** as right to within about 7 % on
both units. It is phase to phase through the driver's own bridge, FETs and leads included. It is not a
meter reading of the bare winding.

**The inductance is not measured.** It is only bounded: the graded short (§6.5) brakes less than its
duty share at low percentages, which says the winding's L/R time constant is not much shorter than a
few milliseconds.

**The six sectors are unequal by about ±1° electrical**: LEFT ±0.9°, with sector `101` about 61°
and `001` about 59°; RIGHT ±0.55°. That comes from sensor placement, and on this motor 1° of
placement is 15° electrical. ±1° is noise to a 60° sector commutator. It would set the error
floor for any sub-sector interpolation.

---

## 3 · How the 64010 board drives it

### 3.1 The power stage

| | Value | Basis |
|---|---|---|
| Bridge | four half-bridges (U, V, W, X); three used for a BLDC motor | vendor |
| MOSFETs | Micro Commercial MCAC85N06Y-TP, 60 V, 85 A package-limited (54 A at 100 °C case) | vendor |
| Gate driver | Rev A: MIC4604 · Rev B: TI UCC27211D | vendor |
| Current sense | low-side shunt in the common MOSFET-ground return — **total bridge current** | vendor |
| Sense scale | Rev A **5 mV/A** (5 mΩ, no amplifier) · Rev B **150 mV/A** (3 mΩ × INA180B2 gain 50) | vendor |
| Phase sense | three **phase-voltage** channels (U, V, W), read every frame beside the current | driver; measured in use |
| Bus-voltage sense | **none on the board** (see the optional [pack sensor](VOLTAGE-SENSOR.md)) | vendor |
| Minimum dead-time | **250 ns, both revisions** — set by MOSFET response, not by driver speed | vendor |

**Every measurement in this manual was taken on two units of this motor on a Rev B board.**

Rev B has 30× the sense resolution of Rev A. At 10 A, Rev A presents 50 mV to a 3.3 V ADC and Rev B
presents 1.5 V. Rev B is the better instrument by a wide margin, and that is why measurements are
taken there. §8.1 says what can and cannot be measured on Rev A.

⚠ **The shunt sits between the FETs' common ground and system ground, so it sees only current that
returns through the supply.** When the drive shorts the phases (all low sides on), the braking current
circulates phase to phase through the low-side FETs and never crosses the shunt. The board therefore
cannot measure a phase short's current, and the current limit cannot limit it. In practice the shunt
reads 4–5 mV through a hard short from speed.

### 3.2 The control loop, in one pass

The driver does **not** compute where to put the field from the rotor's position. It drives the
field forward on its own clock and *corrects* it from the halls. That distinction explains most
of this manual.

Each PWM frame the driver:

1. reads the current-sense and phase ADCs;
2. advances the commanded field angle `angle_` by `drv_incr` — the speed command;
3. computes the three phase outputs as `duty × sin(angle_ + 0° / 120° / 240°)` with the P2's
   CORDIC (`QROTATE`);
4. reads the halls, looks up the sector's angle, adds the direction's offset, and forms
   `err_ = angle_ − (hall_angle + offset)` — how far the field leads the rotor estimate;
5. sets `duty` as a **feedforward** from the field's speed plus an integral **trim** that holds
   `|err_|` at the setpoint (below).

Separately, once a millisecond, the front cog re-derives the offset pair from the speed, using the
lead table in §5.2. [DRIVER-THEORY-OF-OPERATIONS.md](DRIVER-THEORY-OF-OPERATIONS.md) describes the
whole driver.

| Constant | Value | Basis |
|---|---|---|
| PWM / ADC frame rate | 44,000 Hz → **22.7 µs per frame** | driver (`PWM_RATE_IN_HZ`) |
| Drive passes (speed updates) | one per 23 frames → **1,913 passes/s** | driver |
| Field angle resolution | 32-bit fraction of an electrical cycle | driver |
| Rotor angle resolution | **6 positions per electrical cycle** (one per hall sector) | driver |
| Error representation | 8-bit signed, **256 counts per electrical cycle** (1 count = 1.4°) | driver |
| Duty servo setpoint | `SERVO_SETPOINT` **48 counts = 67.5°** | driver |
| Duty feedforward | the magnitude of `drv_incr` × `duty_max` ÷ `ff_ceiling`, where `ff_ceiling` is the motor's back-EMF line (duty 167–174 per 10⁶ of increment at 18.5 V) | driver; the line measured |
| Duty trim | each frame adds (the magnitude of `err_` − 48) × (duty ÷ 16) to an accumulator, applied shifted right 14: symmetric, untruncated, and with a gain that scales with duty | driver |
| What the servo actually holds | a **point**: mean `err` **47–48 counts** at every speed step tried, both motors, both directions | measured |
| Duty floor / ceiling at 270 MHz | `duty_min` **1,600** · `duty_max` **27,648**, the largest amplitude the PWM carries without clipping after the drive re-centres the three levels each frame | calculated; measured clip-free |
| Dead gap applied | 260 ns (meets the 250 ns minimum) | driver |
| Lag: the ramp eases its acceleration off | `LAG_SOFT` 80 counts = **112.5°** | driver |
| Ramp shape | jerk-limited: acceleration eases in and out over **250 ms**; built-in limits **1,000 mm/s²** up and **1,470 mm/s²** down, both provisional until measured under load | driver |
| Lag: the field stops advancing | `LAG_HOLD` 100 counts = **140.6°** | driver |
| Lag: fault | 125 counts = **175.8°** | driver |

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

1. ⚠ **A correction applied to both knobs is applied twice.** The textbook says drive at ±90°
   electrical, and the setpoint is below that; the offset's lead makes up the difference. Moving
   the setpoint as well would count the same correction twice, and given how steep the current
   basin is (§5.3: 12.7× over 30°), that is not marginal.
2. **The two knobs behave differently in time.** The offset is instant; the setpoint is reached
   through the servo, which is regulated.

**So the drive carries the lead in the offset and keeps the setpoint fixed.** The offset is the
knob that can follow speed at once, and the lead has to follow speed (§5.2). At every speed the
lead table sits inside the measured region of least current, so no other split of the same total
placement can lower the steady current further.

### 3.4 What the driver does *not* do

| The textbook principle | What we do |
|---|---|
| Place power at ±90° electrical from the rotor | The duty servo holds **67.5°**, and the offset adds a lead that varies with speed |
| Resolve electrical angle to 12 bits (4,096 positions) | **6 positions** — one hall sector, 60° wide |
| Compute electrical angle from a fine mechanical angle | The motor has no shaft and no fine sensor |

The textbook method (`electrical = mechanical_12bit × pole_pairs MOD 4096`) is correct — and it
starts from a 12-bit *mechanical* angle this motor cannot provide. The gap is architectural, not a
tuning difference: that method assumes an absolute position sensor, and this motor carries three hall
sensors. Closing it here would mean interpolating within a sector from edge timing and speed, or
estimating angle from the phase voltages the driver already samples.

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

| Motor | Speed | Z | Basis |
|---|---|---|---|
| LEFT | 49 ticks/s | **−3.8° ± 0.3** | measured |
| RIGHT | 49 ticks/s | **−4.0° ± 0.3** | measured |
| LEFT | 98 ticks/s | **−3.85°** | measured |
| RIGHT | 98 ticks/s | **−3.45°** | measured |

**Measured a second way, cold.** With the bridge coasting and each wheel turned by hand, the three
phase terminals carry the motor's own back-EMF, whose zero crossings are fixed to the magnets. Placing
them against the hall edges (8 legs per motor, both directions, two hand speeds, two runs):

| Motor | Z, cold | Slow vs brisk | Basis |
|---|---|---|---|
| LEFT | **−3.31°** | −3.34 / −3.29 | measured |
| RIGHT | **−3.25°** | −3.22 / −3.28 | measured |

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
   speed, while the lead L moved 12.2° across the same doubling. That is the method's own
   negative case, and it passed.
5. **A second method, sharing nothing with the first, agrees within 0.35°.** The cold back-EMF
   measurement uses no drive, no current and no offset sweep, and its own negative case holds too:
   slow and brisk legs agree within 0.12°. Its frame is itself tested by the data — the three
   phases fall 120° apart in the one order the drive's phase convention predicts.

### 4.4 The honest limit

The offset sweep covers about **126° of the 360° electrical cycle** — roughly 35 %, bounded
outward by an over-current abort and inward by the motor faulting. Inside that window there is
exactly one minimum per direction, deep and reproducible.

**So the adopted alignment is established as a true local minimum, not proven to be the global
one.** Theory bounds it (torque per amp goes roughly as the sine of the lead, so one maximum per
cycle per direction is expected, and the solution 180° away is the reverse-torque one, excluded
because the wheel tracked its commanded direction at every speed). That is an argument, not a
measurement (§9).

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
  lag, the offset in use, or the servo, and it works the same on either board revision (§8.1).

**It is also there on a wheel coasting from speed after a fault.** The phase channels carry a back-EMF
wave of 281–1,006 mV peak to peak, crossing at the hall rate, on both units, from 40 to 120 × 10⁶. A shorted bridge ties the
phases together and the signal is gone. That is one reason a coast is the kinder response when the
halls are lost (§6.5).

⬚ The same signal exists while the motor is being driven, but the phase pins then also carry the
drive's PWM. Whether it can still be read there is not yet measured (§9). That is the question that
decides whether this can become a live position source for the drive, not just a way to measure the
motor.

### 4.7 What differs from one unit to the next

Measured on two units by the method in §4.6:

| Property | LEFT | RIGHT | Unit-specific? |
|---|---|---|---|
| Hall zero Z | −3.31° | −3.25° | **No** — within measurement scatter; one constant serves both |
| Sector widths (§2.4) | ±0.9° about 60° | ±0.55° | **Yes**, each unit has its own fixed pattern, and it is small |
| Hall lag, each direction | ±1.05° | ±0.8 to ±1.2° | No — the same size on both |

**Hall lag** is the halls switching slightly late in the direction of travel. Forward readings of
Z sit about 2° more negative than reverse ones. The difference is the same at 43 and 117 edges/s,
so it is an angle rather than a time delay: it behaves like the sensors' switching hysteresis.
Averaging the two directions cancels it, which is why Z is always quoted as the mean.

**In wheel terms these are tiny.** On a 15-pole-pair motor, 1° electrical is 1/15° of wheel
rotation. So Z's −3.3° electrical is about 0.22° of wheel, and the difference between the two
units is about 0.004°. The sensors are placed consistently from unit to unit. Two units are not a
population, though (§9).

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

The lead of least net current at four speeds, one octave apart:

| Speed (increment) | ticks/s | Lowest-current lead, both motors and directions | Flat region | Table |
|---|---|---|---|---|
| 18.4 × 10⁶ | 49 | 13–23° | 13–23° within ~6 mV | **20.5°** |
| 36.75 × 10⁶ | 98 | −2 to 8° | −2 to 8° within ~15 % | **5°** |
| 73.5 × 10⁶ | 196 | 3–8° | 3 and 8° within 1–3 % | **8°** |
| 147 × 10⁶ | 393 | 8° | 13° costs 2× | **8°** |

Measured over two runs, counting only steps at which the wheel held its commanded rate. Every
table value sits inside its flat region. Between points the drive interpolates linearly; outside
the table it holds the end value and never extrapolates.

**L falls by about 15° from 49 to 98 ticks/s, then holds at 3–8° up to full speed.** These values
hold for this driver's duty servo: a servo that settles at a different point moves the whole curve.
That is what a drive parameter does, and it is why L is not quoted as a property of the motor.

⚠ **The textbook current-lag model gives the wrong sign here.** The standard argument is that
current lags applied voltage more at higher electrical frequency, so the *voltage* lead needed
to place the *current* at 90° should **grow** with speed. On both servos we measure the reverse, or
at best a flat line. Do not design from that model on this motor. Why the real behaviour goes the
other way is not established (§9).

**The practical consequence:** Z is safe in a compile-time constant. L is not, and no fixed number
serves the whole range: the table draws 24–78 % less current than a flat 18° from 40 to 140 × 10⁶
(107–374 ticks/s), because 18° over-leads everywhere above the slowest table speed.

### 5.3 The basin is steep

Measured current against swept offset, LEFT motor, negative increment, net mV:

| swept° | 63 | 53 | **43** | 33 | 28 | 23 | 18 | **13** | 8 | 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| net mV | abort | 392.8 | **167.1** | 67.2 | 40.5 | 23.7 | 14.6 | **13.1** | 15.1 | fault |

**167.1 → 13.1 mV over 30° — a 12.7× change.**

A basin that deep is consistent with off-optimum current being dominated by **circulating current
that produces no torque**, rather than by a modest loss of torque per amp — which is also the most
natural reading of the 15–26× difference in §7.3.

**What it means for you: alignment on this motor is worth a lot, and being 30° out costs an
order of magnitude in current, not a few percent.**

---

## 6 · The operating envelope

### 6.1 Speeds

The speed command is an angle increment applied 1,913 times a second. `power` 100 commands the
ceiling increment and `power` 1 the floor.

| | Value | Basis |
|---|---|---|
| Drive passes per second | 1,913 | calculated |
| Ceiling increment at 18.5 V | **165,000,000** | measured, and held through the public API |
| → electrical frequency | **73.5 Hz** | calculated |
| → hall ticks per second | **441** | calculated |
| → wheel speed | **294 RPM** | calculated |
| → rim speed | **2.54 m/s** (5.7 mph) | calculated |
| Floor increment | **100,000** → 0.27 ticks/s, ~0.2 RPM | measured: every speed down to it rotated steadily at exactly its commanded rate; it was the lowest tried, so the true floor is lower |
| Ceiling at the other supply voltages | 165 × 10⁶ scaled by voltage, rounded down | calculated; measurements at other voltages follow that line to within 2.5 % |

**How the ceiling is chosen.** It is the fastest measured speed that keeps an unloaded duty
reserve: at 165 × 10⁶ duty runs at 92–93 % of its ceiling, on both motors and in both directions.
It is not the speed at which the wheel stops following, which is far higher (§6.3). How much of that
reserve survives a load is not yet measured (§9).

Every speed figure here is wheels-up.

### 6.2 The two walls

Moving the lead away from its optimum at a fixed commanded speed, the motor stops running well
for **two different reasons**, and they are not the same wall:

| Wall | Side | What happens |
|---|---|---|
| **Current wall** | too much lead | Current explodes, and the run aborts on the current cap. |
| **Torque wall** | too little lead | The motor cannot make enough torque. The rotor falls behind the field: it slows, or the field outruns it and it faults. |

At 90° from optimum, torque is zero at any speed. The reachable arc is the band between the two
walls, and **it narrows as speed rises**.

**On this driver the optimum is inside the reachable arc at every speed.** The lead was stepped
from 33° down to −7° in 5° steps at all four speeds of §5.2. All 16 minima were bracketed, and no
step faulted. The torque wall appears as slowing, not as a fault: at 49 ticks/s, −2° held only 51 %
of the commanded rate and −7° never settled.

### 6.3 The duty ceiling

Above a certain speed the drive runs out of voltage: duty reaches its ceiling and can rise no
further. That knee is a **voltage / back-EMF limit**, not a commutation defect.

**Where the knee sits.** With the clip-free duty ceiling (27,648, §3.2), duty first caps between 175
and 185 × 10⁶ on all four wheel-directions.

**Above the knee the wheel still follows, by field weakening.** With duty pinned, the only way to
advance the rotor further is more lead. `err` grows from 48 to 65 counts, about 24° more field
advance, and the wheel keeps its commanded rate up to 245 × 10⁶, the highest command tried. It pays
in current: 2.3–2.6 A at 245 × 10⁶ unloaded, against 0.3–0.4 A at the knee.

⚠ **Field-weakened running can slip.** One motor, driven forward, lost synchronism between 235 and
245 × 10⁶ on three consecutive runs, with a current peak of about 23–25 A and no fault. The other three
wheel-directions held 245 × 10⁶. That is why the ceiling (§6.1) sits below the knee, with reserve,
rather than at the speed where following ends.

**Alignment moves the knee as well.** The lead table unpinned 147 and 155 × 10⁶, which a flat 18° lead
had held at the ceiling. So alignment buys headroom as well as current.

### 6.4 Starting from rest — the transient

**A start from rest is quiet.** The current rises smoothly to the settled value, and duty does
not swing on the way:

| Start to 98 ticks/s, both motors, both directions | Largest duty drop while accelerating | Peak current ÷ settled |
|---|---|---|
| | **0.01–0.03** | **1.15–1.53** |

**Why the servo stays quiet.** The rotor's torque rises with lag only weakly near its operating angle,
and more weakly the lower the duty. An integral loop around a rotor that is only slightly stiff is stable
only below a gain that scales with that stiffness; a fixed gain high enough for the top of the range
hunts at low speed. So the servo gets the duty a speed needs in advance (the feedforward) and a trim
whose gain scales with duty (§3.2), and the loop stays stable across the range.

**At the lowest speeds.** At the two slowest speeds tested, 10 and 20 × 10⁶ (27 and 53 ticks/s), duty
swings by 178–399 counts, and `err` peaks at 76–86 counts around its mean of 48. It is a small residual,
not a surge.

**Faster ramps.** Starts at two and four times the default acceleration also follow cleanly, without the
drive once having to hold the field back for the rotor to catch up. Their
current peak grows with the acceleration, as it must (1.26–1.34 × settled at the default rate, 1.51–1.83
at twice it and 1.57–2.13 at four times), and in absolute terms it stays at about 0.2 A. Slowing down
produces no surge at either rate tried: the current only falls.

⬚ These start figures were measured at a constant acceleration. The driver's ramp eases its acceleration
in and out (§7.5); that ramp is measured for its shape and its stops, not yet for start current. Every
trace here was taken wheels-up; how a start behaves under load is in §9.

### 6.5 Stopping, faulting and holding

**The two ways to let go of a turning wheel differ by two orders of magnitude.** A coast (all six FETs
off) lets the wheel roll on its own drag. A short (all low sides on) brakes it against its own
back-EMF. Here is one unit from a forced fault at speed, wheels up:

| From | ≈ rim speed | Coast: ticks / ms to rest | Short: ticks / ms to rest |
|---|---|---|---|
| 40 × 10⁶ | 0.6 m/s | 14–16 / 312 | 0–1 / 5 |
| 80 × 10⁶ | 1.2 m/s | 54 / 536 | 1–2 / 9 |
| 120 × 10⁶ | 1.9 m/s | 115–116 / 703 | 1–3 / 11–89 |

Measured over three runs, reproducing within 3 ticks; the other unit gave the same comparison. One tick
is 5.76 mm, so the 120 × 10⁶ coast is about 0.67 m of tyre.

⚠ **Read these as the wheel's own behaviour, not a robot's.** Wheels up, a coast is resisted only by the
motor's drag, and a short stops only the wheel's own inertia. On the floor the platform's mass is behind
the wheel. A short from speed then becomes a braking torque at the contact patch, and the platform tips
if its centre of gravity is high. A coast becomes a roll, and on an incline a runaway. The
short-circuit current behind that torque is about **35–42 A** from the ceiling speed: 17–20 V of back-EMF
into ≈ 0.48 Ω. That figure is calculated from the measured resistance; it cannot be measured on this
board, because the shunt cannot see it (§3.1).

**The graded short sits between the two.** The driver can short the phases for a set percentage of each
10 ms period (`BRAKE_PCT`). One unit, 80 × 10⁶, fault to rest:

| Brake % | coast | 10 | 25 | 50 | 100 |
|---|---|---|---|---|---|
| ms to rest | 518 | 282 | 84 | 16 | 10 |
| ticks to rest | 52 | 22 | 7 | 2 | 1 |

Measured, reproduced within 3 ticks, and the same on the other unit. It is strictly monotone, and **not
linear**. Taken as braking added over the coast's drag, 10 %, 25 % and 50 % add about 0.8×, 5× and 30×
that drag, where a linear brake would give 1 : 2.5 : 5. Each short slice ends before the winding current
has fully built (§2.4). The driver's default is 10 %. It is the gentlest step measured, and it still stops
in about half the coast's time with about 28× less deceleration than the full short.

**A controlled stop is possible after a lost-control fault.** With the halls still legal, the driver can
re-seed its field from the halls and ramp down at the configured deceleration, and a second fault during
that ramp falls back to the graded short (or to a coast in float mode). On the jerk-limited ramp, a stop
from 81.7 × 10⁶ took **1,106 ms and ran 122 ticks**, against the driver's own prediction of 120. Every stop
on this ramp costs about 250 ms and v × 125 ms of travel more than a constant-rate ramp would, the price
of easing the deceleration in and out (§7.5).

This is `FR_GRADED`, the driver's default fault response. `FR_SHIPPED`, which coasts or shorts at once by
stop mode, stays selectable. On a two-wheel platform, a fault on one wheel stops
the other.

**At rest, the stop states are distinct at the wheel.** A hand spin of a stopped wheel gives:

- coast: 12–14 ticks through the measuring band;
- e-stop short: 0;
- fault-coast: 13–14;
- fault-short: 1–3;
- a stopped cog, the free reference: 13–14.

**The hold** (`holdAtStop(TRUE)`) is a load-following hold, not a static short. While the wheel is pushed
off its rest position, duty rises from its floor to a ceiling of 10 % of `duty_max`. It gets there in
the configured 250 ms (measured 249–250), and it never falls back within that rest. At the ceiling one
unit draws about **0.26–0.27 A** of DC-link current. A firm hand push makes it give way (a slip). After its
limit time at the ceiling it hands off to the phase short. That was measured wheels up, by hand, and it
sizes nothing for a slope (§9).

**A wheel commanded but not turning** is caught by the blocked-rotor stop about 1 s in, in the user's
stop mode. The second is counted from the moment the wheel stops ticking with the field pressed against it, so a
wheel that keeps rocking against a yielding obstacle restarts the count with every tick (below).

**On the floor** (a 7.7 kg two-wheel platform, two units, Rev B boards):

- **Distance stops land with the platform's mass behind them**: spins in place and 1 m straight runs came to rest
  within 3 hall ticks of their limits, at every speed tried.
- **A fault on one wheel stops the other with it**: 2 s after a forced fault the partner wheel was at 0 % of its
  speed, both ramped down together, and the platform's heading changed by under 2°.
- **After a fault and its recovery the next drive draws normal current**: 0.72–0.95 times its current before the
  fault.
- **Against a solid obstacle the blocked-rotor stop latched** after the wheel had stood still for 1.0–1.1 s, refused
  drives until cleared, and left the phases shorted in brake mode. **Against a yielding obstacle** the platform
  rocks and pushes repeatedly: one run pushed for about 6 s without latching, another ended in a fault response
  (a controlled stop of both wheels) after about 4 s. Either way the push is current-limited.
- **Under a steady one-sided load** the two wheels slowed together (49 % and 47 % of their command, the line kept
  within 3 %), and the held wheel kept turning without a fault.
- **A stop from speed:** from about 2.3 m/s at a deceleration of 2,087 mm/s² the platform stopped in 1.2 s and
  1.38 m, as the ramp predicts (1.23 s, 1.41 m). At full speed (about 2.45 m/s on the floor) the duty reached
  96 % of its ceiling, and the pack sagged about 0.3 V (1.5 %) at the 3.5 A peaks.

### 6.6 What the driver can prove about the motor at start

At start the driver checks the motor and refuses to start (`ERR_START_CHECK_FAILED`, after 3 retries)
when a check fails. Wheels up, both units:

| Check | Healthy reading | What a failure looked like | Basis |
|---|---|---|---|
| Current-sense rest zero | LEFT 6.4–9.4 mV, RIGHT −0.3–3.1 mV; the accepted band is −17…+36 mV, calculated from the INA180's and the P2 ADC's figures (the comment at `REST_ZERO_MIN_MV` in `src/isp_bldc_motor.spin2`) | — | readings measured over 60+ starts; band calculated |
| Each lead drives its phase (probe) | driven phase 777–823 mV, undriven phases follow at ≥ 95 % | a withheld lead ≤ 31 mV; a bridge not driving, 11–27 mV on all three | measured |
| Halls present and legal | legal at every start | connector unplugged: `%111`, caught 10 of 10 | measured |
| Winding resistance (opt-in) | §2.4 | the withheld lead's two pairs go dark, 10 of 10 | measured |
| Wiring walk, one electrical cycle each way (opt-in, moves the wheel) | legs of 7 ticks out and back, 13–21 mV peak | swapped hall pair (made in firmware): fails 3 of 3 | measured |

⚠ **A miswired walk with no guard drew a ~26 A peak** (3,858 mV). The walk now ends a leg at 150 mV net
(about 1 A), and a miswired walk peaks right at that trip. 20 of 20 healthy walks pass, including a
healthy wheel beside a miswired partner.

**A start check cannot see what happens later in a run.** It proves the motor and the bridge were healthy
when the program started, nothing more.

---

## 7 · Current and power

### 7.1 What is measured and what is not

| | Status |
|---|---|
| Total bridge current (DC link) | **measured**, calibrated, 150 mV/A on Rev B |
| Per-phase voltages | **measured** |
| Winding resistance | **measured** by the driver at start, ±6 % per reading (§2.4) |
| Bus voltage | ⛔ **not measured by the board** — assumed from the configured `DRIVE_VOLTAGE`, unless the optional [pack sensor](VOLTAGE-SENSOR.md) is fitted (`getPackVoltage()`) |
| A phase short's current | ⛔ **not visible** — it never crosses the shunt (§3.1) |
| Motor or board temperature | ⛔ not measured |
| Regenerative current | ⛔ **not visible** — the shunt is low-side, so regeneration drives the sense node below ground, and Rev B's amplifier (INA180) is a one-direction part with no reference pin |

⚠ **Every power figure in this manual is a current measurement against an assumed voltage.** Without a
pack sensor, nothing in the system feeds back battery voltage, and a sagging pack looks identical to a
healthy one.

### 7.2 Protection limits

| Limit | Value | Basis |
|---|---|---|
| Peak, loop folds back | **40 A** | 0.75 × the MOSFET's package-limited 54 A at 100 °C case |
| What the fold-back compares | the sense reading less the rest zero taken at start, never below 0, and only while the bridge is driven | driver |
| Continuous, derated to | **27 A** | junction ≤ 125 °C at 50 °C ambient, 55 °C/W |
| Peak restored below | 80 % of continuous | driver |
| Averaging window | ~1 s | driver |
| Fault (field outruns rotor) | 175.8° electrical | driver |
| Blocked-rotor detection | ~1 s at the lag limit with no hall tick; stops in the user's stop mode | driver; measured firing at about 1 s |

These protect the board, not the motor, and they are not user settings. None of them can limit the
current of a phase short, which the shunt cannot see (§3.1). A short is limited only by the winding
resistance, or by the graded short's duty (§6.5).

### 7.3 Current in normal running

**What alignment is worth.** Net current (mV) at the same commanded speed, both motors, aligned (offsets
14 / 338) and driven 25° off optimum, each with a fixed offset pair:

| Motor | Speed (increment) | **aligned** (neg / pos) | the same motor driven 25° off optimum | cost of that misalignment |
|---|---|---|---|---|
| LEFT | 40 × 10⁶ (107 ticks/s) | **130 / 129** | 1991 / 977 | 15.3× / 7.6× |
| LEFT | 60 × 10⁶ (160 ticks/s) | **230 / 242** | 5422 / 2636 | 23.6× / 10.9× |
| LEFT | 80 × 10⁶ (214 ticks/s) | **417 / 424** | 10879 / 5461 | 26.1× / 12.9× |
| RIGHT | 80 × 10⁶ (214 ticks/s) | **425 / 469** | 11016 / 5875 | 25.9× / 12.5× |

In amps at 100 × 10⁶ (267 ticks/s): **0.46 A** LEFT and **0.49 A** RIGHT aligned, against 7.40 A and 7.75 A
at 25° off. The right-hand columns are the §5.3 basin measured on the running machine rather than on a sweep.

Three independent observables agree on this and they do not share a signal path: the current sense
channel, the duty servo's own demand (which fell from 83.7 % to 53.9 % and is not read through the sense
channel at all), and the fact that the commanded rate was met in both cases to within 1 %. **The machine
turns the same wheel at the same speed for a fraction of the current.**

**Letting the lead follow speed goes further.** With the lead table (§5.2), net current is a further
**22–74 % below** the aligned fixed pair from 40 to 140 × 10⁶, and the saving grows with speed:
22–27 % at 40 × 10⁶, 70–74 % at 120 × 10⁶. Duty falls 5–13 % with it, and speed tracks within 0.04–0.47 %.

**Direction symmetry.** The LEFT motor's two directions draw the same current to within 1–4 % at every
speed from 40 to 140 × 10⁶. The RIGHT motor keeps a small residual: its negative direction draws 2–8 %
less than its positive one (for example 264 against 286 mV × 10 at 100 × 10⁶). It is a few percent of a
current that is already an order of magnitude smaller than misaligned.

### 7.4 What off-optimum current costs

From §5.3: 30° off optimum multiplies current by 12.7×. Most of that is not doing work — it is
circulating current producing no torque, and it comes out as heat in the MOSFETs and the
windings.

**This is the single largest lever on how hot the board runs and how long the battery lasts.**

### 7.5 Transitions

Changing speed draws current above the settled value while the wheel accelerates. Beyond that, the
excess at a speed change is small: at worst **10 mV left and 12 mV right** over the settled current,
across every speed change measured (below). Misalignment makes it much larger, which is one more reason
to use the lead table.

**The ramp is jerk-limited.** One trajectory generator runs every drive pass the motor is not at rest.
Its acceleration moves toward its limit by at most one jerk step a pass, rising from 0 to the limit over
250 ms and ramping back out to land exactly on the target speed. A reversal passes through zero without
a restart, and the rotor-lag gate eases the acceleration off rather than freezing it. The built-in
limits are 1,000 mm/s² up and 1,470 mm/s² down, both provisional and open to retuning once they are
measured under load; `setAcceleration()` and `setDeceleration()` change them.

What that costs is calculated from the driver's own per-pass arithmetic: a stop from speed v at
deceleration a takes about v ÷ a + 0.25 s and runs about v² ÷ 2a + v × 0.125 s, so every stop is about
250 ms longer and v × 125 ms further than a constant-rate ramp.

**Measured wheels up**, sampled pass by pass: a start from rest, a slow-down, an arrival and every stop
moved the acceleration by at most one jerk step a pass (71 up, 104 down) and never past its limit, and
settled on the target; a reversal from +40 × 10⁶ to −40 × 10⁶ passed through zero without the driver
reporting STOPPED; stop limits armed at cruise and mid-ramp came to rest within 2 ticks and 3 ms of their
limits, and the same stop plans repeated to within a millisecond on a second day.

⬚ **Not yet known:** the feel of a start, a speed change and a stop on the floor, the current each draws
under load, and whether the built-in rates suit a loaded platform (§9).

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
   between 49 and 98 ticks/s (§5.2). A fixed pair is a one-speed tune.
5. **Stay below the duty knee** where you care about efficiency or about current readings meaning
   anything. `power` 100 keeps about 7 % unloaded duty reserve. Above the knee the wheel follows
   only by field weakening, draws amps unloaded, and can slip with a 23–25 A peak (§6.3).
6. **Every speed figure is wheels-up.** On the floor, driving a 7.7 kg platform at full stick, the duty reached 96 %
   of its ceiling (§6.5); the reserve left under a heavier load is not yet measured.

**Starting and stopping**

7. **A start from rest is quiet on this drive.** Its current peaks at about 1.2–1.5× the settled
   value (§6.4). A faster ramp draws more because it accelerates harder, not because it surges.
8. **Size the supply for acceleration and for speed changes**, not for a start surge (§6.4, §7.5).
9. **Choose the stop mode for your platform, not for the wheel.** A short from speed stops the wheel
   in a tick or two. Behind a tall platform, that is a 35–42 A braking pulse nothing on the board can
   limit, and a tip-over risk. A coast rolls, and on a slope runs away. The graded short and the
   re-synced ramp (`FR_GRADED`) sit between them (§6.5).
10. **The hold resists a push; it is not yet shown to hold a slope** (§6.5).
11. **Let the start checks run.** They catch an unplugged hall connector, a dead lead and a bridge that
    will not drive, before the wheel is commanded (§6.6). The wiring walk moves the wheel about 4 cm,
    so run it wheels up or with room to move.

**Two-wheel platforms**

12. **The two motors face opposite directions**, so one wheel's forward is the other's reverse.
    That makes direction symmetry a two-wheel concern, not a nicety. Aligned, the two directions
    cost the same current to within a few percent (§7.3), so driving in a straight line loads both
    wheels almost equally. An alignment that is symmetric about zero rather than about Z costs one
    wheel of every pair roughly double the current for the same speed.

**Measurement**

13. **Use Rev B boards for anything where current matters.** 150 mV/A against 5 mV/A is a 30×
    resolution difference (§3.1).
14. **Do not infer bus voltage from anything on the board.** It is not measured (§7.1). Fit the
    optional [pack sensor](VOLTAGE-SENSOR.md) if the voltage matters to you.

### 8.1 If your board is a Rev A

The two quantities that matter most are not equally available on Rev A, and the difference is the
current channel:

- **Z — the hall zero — needs no current and no drive.** It is measured with the bridge coasting and
  the wheel turned by hand (§4.6). Nothing in that method reads the current-sense channel, so Rev A's
  30×-coarser sense does not degrade it, and nothing can fault or run away because nothing is driven.
  One check first: the driver scales the three phase channels identically on both boards, but whether
  the two *boards* present phase voltage at the same scale is not something the vendor documentation
  addresses. Confirm it before trusting a Rev A phase reading.
- **L — the lead — needs the motor driven and a current minimum located.** Rev A presents current to
  the ADC at 5 mV/A against Rev B's 150 mV/A. At good alignment the whole signal is a few hundred
  millivolts on Rev B, so the same measurement on Rev A sits in the bottom two percent of the range.
  Expect much wider error bars.
- **Winding resistance will not come from the driver on Rev A.** At 5 mV/A a 0.1 A probe current is
  half a millivolt, so the winding check deliberately drives nothing on a Rev A board. Use a meter
  across each lead pair of the unpowered motor.
- **The start check's rest-zero band** for Rev A (−17…+17 mV) is calculated from component data and
  has not yet been checked against a Rev A board.

⭐ Notice the pattern: **the quantity that belongs to the motor can be measured on any board; the
quantity that belongs to the driver depends on which board it is.** That is §1.3's attribution showing
up as a practical fact.

---

## 9 · What we do not know yet

Each question says why it matters and what would settle it.

| Question | Why it matters | What would settle it |
|---|---|---|
| **Whether the lead table holds speed under a heavy load.** Spinning a 7.7 kg platform in place (both tyres scrubbing, the heaviest load it meets), the lead table's timing ran at 57–94 % of its commanded speed with the drive using well under its duty range, where two fixed timings held 100 % at about twice the current. On straight runs at low speed it held. | The lead table's unloaded saving (§5) is not a win if it costs speed under load. | Being investigated in the driver. |
| **How a start behaves under load at higher speeds.** Measured only at low and medium speed on the floor. | A start's current spike is what a heavy robot feels. | A longer loaded run at speed. |
| **Whether the hold keeps a platform from creeping on an incline.** Not yet measured on a slope. | It decides the hold's ceiling for a robot that parks on one. | A run on an incline. |
| **Why L falls with speed.** Is the speed dependence a property of the motor (its electrical time constant) or of the commutation scheme (loop lag)? The textbook predicts the opposite sign (§5.2). | It decides whether a speed law can be written down or must be measured per motor. | The motor's time constant does not care about the drive-pass rate and loop lag does, so the lead measurement repeated on a build with a different pass rate would tell them apart. |
| **Is the alignment the global optimum?** About 35 % of the electrical cycle has been swept (§4.4); one minimum per direction lies inside it. | Theory says there is only one, but that is an argument. | A full-cycle sweep, by a method that does not drive the motor into the current wall to get there. |
| **Unit-to-unit variation.** Two units measured; Z agrees within 0.06° and resistance within 7 %. | Two is not a population. | More units — Z can be measured on any board (§8.1). |
| **Winding inductance, and so L/R.** Only bounded (§2.4). | It sets how finely a graded short can be sliced, and how a current pulse rises. | An LCR meter across two leads, or a fast read of the current's rise during a drive pulse. |
| **Can back-EMF be read while the motor is driven?** It reads cleanly while coasting (§4.6). While driving, every ADC reading averages a whole PWM frame. | It decides whether back-EMF can become a position source when the halls are lost. | Releasing the bridge for a few frames at a few speeds and capturing the phase pins. |
| **Bus voltage.** The board cannot measure it (§7.1). Our rig has the optional pack sensor fitted, calibrated against a meter at one voltage (within 7 mV at 20.74 V); the winding measurement (§2.4) uses it. | The power figures in §7 still rest on the nominal voltage, and the calibration has one point. | A check at a second pack voltage. |
| **A phase short's current.** About 35–42 A from the ceiling speed, calculated (§6.5). | It is the braking torque behind a hard stop. | Not measurable on this board: the shunt cannot see it (§3.1). |

---

## 10 · About the measurements

Every measurement here was taken on two units of this motor, on a Rev B 64010 board, with the P2 at
270 MHz, during the 6.0 driver work in September 2026: with the wheels lifted, except the floor results in §6.5
and §9, which were taken with the two units driving a 7.7 kg two-wheel platform. The measurements were made
with the driver's own sense channels, read through the programs in `src/test_*.spin2`;
[TECHNIQUES.md](TECHNIQUES.md) explains the methods. The analyses behind each number are kept in this
repository's `DOCs/analyses/` folder.

---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Disclaimer and Legal

> _Parallax, Propeller Spin, and the Parallax and Propeller Hat logos_ are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
