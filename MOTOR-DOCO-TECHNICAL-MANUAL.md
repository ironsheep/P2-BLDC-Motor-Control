# The DocoEng 4,000 rpm motor — a technical manual

**What it is, how the 64010 board drives it, and where it wants to run.**

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

This manual describes the DocoEng 24 V, 4,000 rpm BLDC motor (`MOTR_DOCO_4KRPM`) as we have
actually measured it, and how to get good behaviour out of it with the Parallax 64010 Universal
Motor Driver board.

It is the companion of the [6.5″ hub motor's manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md) and is built
section for section on it, so §5 here can be read beside §5 there. Where the two motors behave
alike, this manual says so briefly and points across; where they differ, it says how.

Its wiring is on [DOCOENG_MOTOR.md](DOCOENG_MOTOR.md). The methods behind the numbers are
explained in [TECHNIQUES.md](TECHNIQUES.md).

---

## 1 · How to read this manual

### 1.1 The one idea to carry through

> **One electrical cycle is 90° of shaft.**

The motor has 8 magnets — 4 pole pairs — so the electrical machine goes round 4 times for every
turn of the shaft. The three hall sensors divide each electrical cycle into six sectors of 60° on
average, so:

| | electrical | mechanical (shaft) |
|---|---|---|
| one hall sector (one "tick") | 60° on average | **15°** on average |
| one electrical cycle (6 ticks) | 360° | **90°** |
| one shaft revolution (24 ticks) | 1,440° (4 cycles) | 360° |

Against the 6.5″ motor's 15 pole pairs, this motor is far less sensitive to where a hall sensor
sits: 1° of placement is 4° electrical here, not 15°. What it has instead is **speed**. It turns
up to 4,000 rpm and beyond, so the drive's field moves tens of electrical degrees between two of
its updates, and timing that is right at walking pace is not right at the top (§5.4).

Our test shaft carries a 360-line encoder, 1,440 counts a turn, so **one encoder count is one
electrical degree.** Most angles below were measured with it.

### 1.2 Where each number comes from

| Basis | Means |
|---|---|
| **measured** | measured on our hardware — two units of this motor on a **Rev A** board, the shaft free with only the encoder on it — with its error where we have one |
| **calculated** | worked out from measured values or from the driver's constants; the arithmetic is shown |
| **vendor** | taken from the maker's data sheet ([DOCOMotor.pdf](DOCs/DOCOMotor.pdf)) or a Parallax manual, not checked on our hardware |
| **driver** | a constant or behaviour of the driver in `src/isp_bldc_motor.spin2` |

### 1.3 Motor, driver, instrument, rig — what this manual keeps apart

| Quantity | Belongs to |
|---|---|
| Pole count, hall geometry, the sector widths, the hall zero **Z**, the back-EMF constant | the **motor** — durable, transfers with any driver |
| The lead **L**, the offsets, the speed limits, how it stops and holds | the **driver** — our choices, not the motor's properties |
| Current readings in mV, what can and cannot be resolved | the **instrument** — on this motor, a Rev A board (§7.1) |
| Vibration and shaking at some speeds | the **rig** — the motor and encoder sit unanchored on a rubber mat (§6.7) |

### 1.4 What is not settled

Open questions are marked ⬚ where they arise and collected in §9.

---

## 2 · The motor

### 2.1 Construction and geometry

| Property | Value | Basis |
|---|---|---|
| Type | 3-phase BLDC, 5 mm shaft out of both ends | vendor |
| Magnets (poles) | **8** | measured, §2.2 |
| Pole pairs / electrical cycles per revolution | **4** | measured, §2.2 |
| Position sensing | 3 hall sensors | vendor |
| Hall states per electrical cycle | **6** | measured |
| Hall ticks per revolution | **24** | measured, §2.2 |
| Shaft degrees per hall tick | **15° on average**; the sectors are unequal (§2.4) | calculated, measured |
| Hall state sequence | positive increment (ticks rising): 1-5-4-6-2-3 · negative increment (ticks falling): 1-3-2-6-4-5 | driver (`deltas4k`), and measured both ways |
| Direction | the maker's clockwise, viewed from the output shaft (the end with the raised boss), counts the halls **up**. The library's forward power drives a **negative** increment, so forward turns the shaft counter-clockwise viewed from the output shaft | measured |
| Nominal voltage | 24 V | vendor |
| Back-EMF constant Ke | **3.53 V per 1,000 rpm** | vendor; the drive's own duty line agrees (§3.2) |
| Torque constant | 0.034 N·m/A | vendor |
| No-load speed / current | 6,800 rpm ±10 % at 24 V / 0.4 A max | vendor |
| Rated speed / torque / power | 4,000 rpm ±10 % / 0.0625 N·m (about 1.84 A) / 26 W | vendor |
| Winding resistance, phase to phase | **1.8 Ω** | vendor — not measured on our hardware (§2.4) |

### 2.2 How the 24 ticks were counted

With the motor unpowered, the shaft was turned by hand about three turns and the hall edges counted
against the encoder: **74 ticks over 4,445 counts = 3.087 turns, 23.97 ticks a turn.** No library
constant enters the count. The halls and the encoder agreed on the direction of every step.

Driven, the hall map closes exactly: every burst of 48 ticks covers 2,880 encoder counts (±1),
two turns, on both units, both directions, at both speeds tried.

### 2.3 Hall sensor health, as observed

Across every driven hall map on both units: **no illegal hall state and no out-of-order edge**,
2,304 edges judged on the first unit and 384 on the second. The driver's start check has read
legal halls at every start.

### 2.4 The windings and the sectors

**The winding resistance and inductance are not measured.** The driver's own resistance check
needs a current reading the Rev A board cannot resolve at a safe probe current, so it drives
nothing on Rev A (§7.1). Take the maker's 1.8 Ω phase to phase. The inductance is not measured; the lead model puts it at about
1.06 mH a phase (§5.4).

**The six sectors are not equal, and that matters more here than on the 6.5″.** Each code's width
in electrical degrees, driven both ways at 24 and 96 ticks/s:

| Hall code | First unit (12 runs, 7.4–24 V) | Second unit | Difference |
|---|---|---|---|
| 1 | 55.8–56.9 (mean 56.3) | 59.1 | +2.8 |
| 2 | 59.8–60.6 (60.0) | 58.8 | −1.2 |
| 3 | 64.3–65.3 (64.8) | 63.4 | −1.4 |
| 4 | 67.0–67.8 (67.3) | 65.9 | −1.4 |
| 5 | 57.1–58.0 (57.6) | 56.4 | −1.2 |
| 6 | 53.6–54.2 (53.9) | 56.6 | +2.7 |

All measured. Each unit repeats its own pattern to about 1° at every voltage and speed, so this is
geometry, not noise. **Codes 3 and 4 are the wide pair on both units.** Codes 1 and 6 are narrow on
the first unit and near 60° on the second.

Those codes come in opposite pairs in the rotation (1 and 6, 2 and 5, 3 and 4), and the difference
between the units sits in one pair. That is the signature of one hall sensor placed slightly
differently.

Inside a code there is a second, smaller pattern: the 24 sectors of one turn range 52–68°, and
each repeats exactly turn after turn (four turns, no misfit). That one is where each magnet sits on
the rotor.

A driver that assumes 60° sectors places the field up to **6° off** inside a sector on this motor.
Against the ±1° of the 6.5″, that is why the Doco's sector widths are worth a table (§3.2).

**Hall hysteresis** (the halls switching a little late in the direction of travel): 3.0–3.4° on the
first unit, 2.6–2.8° on the second, at every speed (measured). The zero does not move with speed
(≤ 0.3° between 24 and 96 ticks/s).

---

## 3 · How the 64010 board drives it

### 3.1 The power stage

The board is the one in the [6.5″ manual §3.1](MOTOR-6.5IN-TECHNICAL-MANUAL.md#31-the-power-stage):
four half-bridges, a low-side shunt reading total bridge current, three phase-voltage channels, no
bus-voltage sense, a 250 ns minimum dead time.

**Every measurement in this manual was taken on a Rev A board**, the reverse of the 6.5″ manual. Rev A
reads current at **5 mV/A** against Rev B's 150 mV/A. On this board a single frame's reading scatters
by 0.50–0.64 mV standard deviation (about 0.1 A) while driven, 4.8 mV peak to peak (measured, two
supplies), so at the Doco's light-load currents — a few hundred milliamps — the current is only a few
counts above the noise. §7.1 says what that costs.

### 3.2 The control loop, in one pass

The loop is the 6.5″ manual's [§3.2](MOTOR-6.5IN-TECHNICAL-MANUAL.md#32-the-control-loop-in-one-pass):
the driver turns the field forward on its own clock and corrects it from the halls, with a duty
feedforward and an integral trim that holds the field-to-rotor error at its setpoint. What is
particular to this motor:

| | Value | Basis |
|---|---|---|
| Field advance per drive pass at 2,400 rpm | **30° electrical** (1,913 passes/s) | calculated |
| at 4,343 rpm, the fastest measured | **54.5°** a pass; under one hall tick a pass | calculated |
| How the field moves inside a pass | a frame at a time: frame k of 23 drives the field at angle + (k − 11) × step ÷ 23, so it turns smoothly and its mean over the pass is the commanded angle | driver |
| Duty feedforward line | **688 × 10⁶ increment at 18.5 V** for full duty, scaled by the supply (37.2 × 10⁶ a volt) | measured; the maker's Ke predicts 37.2 × 10⁶ a volt |
| Rotor angle within a sector | the sector's table angle, **equal 60° sectors** today (§2.4) | driver |
| Commutation offsets | **one fixed pair per supply voltage**, each direction its own (§5.1) | driver |

The frame-by-frame field is what lets this motor run smoothly above about 2,400 rpm. A field that jumped
a whole step once a pass would swing the error by half a step either way, which at these speeds reaches
the servo's fast-response threshold on every pass, and the drive spends duty no load asked for.

### 3.3 The two knobs that place the field

As on the 6.5″ ([§3.3](MOTOR-6.5IN-TECHNICAL-MANUAL.md#33-the-two-knobs-that-place-the-field--and-they-add)):
the commutation offset and the servo's setpoint add. The lead is carried in the offset; the setpoint
stays fixed.

---

## 4 · Position and geometry: the hall zero **Z**

### 4.1 What Z is

Z is where the hall pattern's zero sits against true electrical zero — a property of sensor placement,
the same in both directions ([6.5″ §4.1](MOTOR-6.5IN-TECHNICAL-MANUAL.md#41-what-z-is)).

### 4.2 The measured values

Z is the midpoint of the two directions' current minima at the same speed:

| Supply | Speed | Z | Basis |
|---|---|---|---|
| 7.4 V | half speed | **−0.3°** | measured |
| 14.8 V | half speed | **−4.4°** | measured |
| 22.2 V | half speed | **−2.8°** | measured |

**Take Z ≈ −2.5° for this motor, known to a few degrees.** The pair the driver ships at each voltage
(§5.1) has its midpoint at −2 to −4.5°.

⬚ The cold method that measured the 6.5″'s Z to a tenth of a degree (the motor's own back-EMF with the
bridge off, [6.5″ §4.6](MOTOR-6.5IN-TECHNICAL-MANUAL.md#46-how-the-motors-own-voltage-locates-the-magnets))
did not resolve on this motor: its legs disagreed by up to 36°. Why is not established (§9). The second
unit's Z could not be read either: its current minima did not resolve (§4.7).

### 4.4 The honest limit

On this motor at light load the current curve is shallow (§5.3) and Rev A reads it coarsely (§7.1), so
only some speeds and voltages gave a resolved minimum in each direction. Z rests on three rows that did.

### 4.7 What differs from one unit to the next

Two units, measured on the same board at 14.8 V:

| Property | First unit | Second unit | Unit-specific? |
|---|---|---|---|
| Sector widths (§2.4) | 53.6–67.8° | 56.4–65.9° | **Partly** — the same wide pair, one pair differs by up to 2.8° |
| Hall hysteresis | 3.0–3.4° | 2.6–2.8° | Close |
| Hall order, direction, ticks a turn | — | the same | No |
| Duty at the same speed | — | within ~5 % | No — the same motor constant |
| Current at the same speed | 220–280 mA at a quarter speed | **450–840 mA** | **Yes** — 2–3× the drag (a stiffer bearing, or a unit not yet run in) |
| Runs on the shipped offsets | yes | yes, losing hold only 15–20° away either side | No |

Two units are not a population (§9).

(§§4.3, 4.5 and 4.6 of the 6.5″ manual have no counterpart here: this motor's Z has no independent second
method yet, and no hand-detent or cold back-EMF study was completed on it.)

---

## 5 · Field placement: the lead **L**

### 5.1 What L is, and the pair this motor ships

L is where the field is put against the rotor — a drive parameter, combined with Z into the offset
pair ([6.5″ §5.1](MOTOR-6.5IN-TECHNICAL-MANUAL.md#51-what-l-is)). On this motor a larger reverse offset,
or a smaller forward one, puts the field further ahead: here L **is** the real lead (on the 6.5″ it is
written the other way round). Each direction carries its own measured value, the current minimum at half
speed:

| Supply | 7.4 V | 11.1 V | 12.0 V | 14.8 V | 18.5 V | 22.2 V | 24.0 V |
|---|---|---|---|---|---|---|---|
| Forward (negative increments) | 305° | 299° | 300° | 298° | 302° | 299° | 300° |
| Reverse (positive increments) | 55° | 54° | 54° | 53° | 54° | 56° | 52° |

Measured where a half-speed minimum resolved; the others take the mean of those (and 12.0 V is not
tested). In signed terms the pair is about −60° / +54°: **L ≈ 57°**, against the 6.5″'s offsets of about
−12° to −24°. Most of that difference is bookkeeping: this motor's hall-angle table is defined 60° apart
from the 6.5″'s, so the same real field placement reads about 60° higher here. The rest is each motor's own
hall placement.

### 5.2 L depends on speed

| Speed | Supply | Where the current is least, from the shipped pair | Basis |
|---|---|---|---|
| a quarter and half speed | 7.4–24 V | within about 2° (the pair *is* this point) | measured |
| 1,120 rpm | 11.1 V | 7° toward less lead forward, 9° toward more lead reverse; the current is a few counts above the noise here, so read both as ±5° | measured, weakly (§7.1) |
| the top, 1,650–2,800 rpm | 11.1–24 V | 5–15° toward **more** lead, still falling at the edge of the sweep at 18.5 and 22.2 V | measured |

And the duty — the voltage the drive must apply — is least at **more lead still**: about 18–20° beyond
the current minimum at a quarter and half speed, and beyond 10° more lead at every top step measured:

| Supply | Speed | 10° more lead than shipped saves this much duty | Basis |
|---|---|---|---|
| 7.4 V | 1,650–2,212 rpm (its top) | 9–14 % | measured |
| 24 V | 2,800 rpm | nothing forward; reverse needs 5 % *more* | measured |
| 24 V | 2,940–4,343 rpm | 3–26 % forward, 2–8 % reverse | measured |

**The Doco therefore wants more lead high up** — as the 6.5″ does: its table's L falls with speed, which
on that motor is the real lead rising (6.5″ §5.2). Today the Doco ships one fixed pair per voltage; the
6.5″ ships a lead table against speed. §5.4 gives the curves a table for this motor is drawn from.

### 5.3 The basin is shallow

Unloaded, this motor's current hardly moves across a ±20° sweep. The second unit at 14.8 V, half
speed, reverse, around its shipped 53°:

| offset° | 33 | 38 | 43 | 48 | **53** | 58 | 63 | 68 | 73 |
|---|---|---|---|---|---|---|---|---|---|
| DC current, mA | 1,116 | 902 | 862 | 882 | **684–904** | 734 | 674 | 798 | 908 |
| duty | 12,999 | 11,708 | 10,728 | 9,995 | **9,423** | 8,967 | 8,625 | 8,367 | 8,160 |

The current is flat to within the board's resolution; the duty falls steadily toward more lead. **What
it means for you:** on this motor at light load, timing shows up in the voltage the drive needs — its
headroom — more than in its current. That is the reverse of the 6.5″, whose current basin is 12.7×
deep over 30°.

### 5.4 The lead curves

What a lead sweep measures — a current bowl and a duty bowl at each speed, whose bottoms trace the
**efficiency** and **headroom** curves — and the four things a model of the windings predicts about them,
are set out in the driver's [theory of operations](DRIVER-THEORY-OF-OPERATIONS.md#the-lead-curves--where-the-offset-should-sit).
This section says how this motor measures up; the [6.5″ manual §5.4](MOTOR-6.5IN-TECHNICAL-MANUAL.md#54-the-lead-curves)
does the same for that one.
"Lead" here is the field's real lead over the rotor: 360° less the forward offset, or the reverse offset.

| | On this motor |
|---|---|
| 1 · one bowl shape | **holds**, to 0.1–0.3 % on every sweep below about 2,500 rpm |
| 2 · bottom = zero + atan(ω × inductance ÷ R) | **holds**: **53.5° + atan(ω × 1.17 ms)** fits 19 speeds at every supply from 7.4 to 24 V within 0.9°. At about 650 rpm the bottom is 70–71° on 11.1, 14.8, 18.5 and 24 V alike. With the maker's 1.8 Ω, the time constant gives a winding inductance of about **1.06 mH a phase** (calculated) |
| 3 · the curves coincide at low speed and part | **holds**: the zero, 53.5°, is where the current is least at low speed (50–54°); the gap is 16–21° at 560–650 rpm and 37° at 1,821 |
| 4 · the hold wall just past the duty bottom | **holds**: every hold wall measured lies 1–5° past its sweep's duty bottom, on both units |

The curves, as measured and calculated (the mean of the two directions; forward reads 5° more and reverse
5° less on the first unit, 2.7° on the second):

| rpm | 600 | 1,300 | 1,800 | 2,500 | 2,800 | 4,000 |
|---|---|---|---|---|---|---|
| Efficiency curve (± 4°, Rev A) | 51° | 57° | 61° | 66° | 68° | — |
| Headroom curve, the hold wall | 70° | 86° | 95° | 102° | 107° (calculated) | 117° (calculated) |
| The shipped fixed pair | 57° | 57° | 57° | 57° | 57° | 57° |

At the top the shipped pair sits 50–60° short of the headroom curve and about 10° short of the efficiency
curve, which is why the top speed costs duty (§6.3). Above 2,800 rpm the efficiency curve is not cleanly
measured: there the servo's working point shifts at 24 V (§6.3).

### 5.5 Unit-to-unit

The second unit could not be put through the same minimum test as the first: its current was flat
within the board's resolution at every speed (§5.3). On the shipped pair it ran cleanly at a quarter,
half and full speed both ways, and lost hold only 15° (forward) and 20° (reverse) away from the pair,
as the first unit does. **The shipped pair serves both units.**

---

## 6 · The operating envelope

### 6.1 Speeds

The speed command is an angle increment applied 1,913 times a second: 100 × 10⁶ is **668 rpm** on this
motor (calculated). `power` 100 commands the ceiling and `power` 1 the floor.

| Supply | Floor (shipped) | Ceiling (shipped) | Basis |
|---|---|---|---|
| 7.4 V | 4.00 ticks/s, **10 rpm** | 247 × 10⁶, **1,650 rpm** | driver, from measurement |
| 11.1 V | 10 rpm | 370.5 × 10⁶, **2,475 rpm** | driver, from measurement |
| 12.0 V | 10 rpm | 400.5 × 10⁶, **2,675 rpm** | driver, calculated (not tested) |
| 14.8–24 V | 0.60 ticks/s, **1.5 rpm** | 419 × 10⁶, **2,799 rpm** | driver, from measurement |

**How the ceiling is chosen.** As on the 6.5″: the fastest speed that keeps 7.5 % of the duty unused,
unloaded, read on the needier direction, and scaled by the supply — capped at 2,799 rpm, the fastest
speed every supply had then been certified at.

**What the motor actually holds** (first unit, the speed held steadily for 5 s in each direction):

| Supply | Slowest steady | Fastest held, forward | Fastest held, reverse | What ended it | Basis |
|---|---|---|---|---|---|
| 7.4 V | **3.00 ticks/s, 7.5 rpm** both ways (2.00 stutters) | **1,931 rpm** | **2,212 rpm** | the duty ceiling | measured |
| 24 V | **0.10 ticks/s, 0.25 rpm** both ways, the slowest tried | **4,343 rpm** | **≥ 3,782 rpm** | forward the duty ceiling; reverse the test program's own error, not the motor | measured |

So **both ends of the shipped range sit well inside what the motor holds**, most of all at 24 V. The
ceilings are set by the duty the drive needs at the top, and §5.2 says more lead lowers it. They will
be raised when the lead does (§9).

**Why low supply cannot crawl as slowly.** Every slowest step runs at the duty floor, 5.8 % of full
duty: 0.43 V at 7.4 V, 1.39 V at 24 V (calculated). Below about 3 ticks/s at 7.4 V that is not enough
to pull the rotor smoothly past each magnet, and the shaft stutters. The slowest steady speed at 7.4 V
moved between 1 and 4 ticks/s from one session to the next, which is why the floor there is 4.

Every speed figure here is unloaded.

### 6.2 The two walls

| Wall | Side | What happens |
|---|---|---|
| **Hold wall** | too much lead, at low speed | The rotor cannot keep up with a field placed that far ahead. It hunts, then slows: 15–20° beyond the shipped pair at a quarter speed and at 560 rpm, on both units; 25° in reverse at 1,120 rpm |
| **Duty cost** | too little lead | The voltage needed rises steadily (§5.3) and the current with it: at 1,120 rpm forward, 30° short of the pair needed 61 % more duty |

The shipped pair sits 15–25° from the hold wall at low speed, on both units. **The hold wall is the
bottom of the duty bowl** (§5.4): past it, a rotor that falls back gains lead and needs more voltage, not
less, so it falls further. Every hold wall measured lies 1–5° past its sweep's duty bottom, and the
bottom moves to more lead as speed rises, so the wall recedes with speed.

### 6.3 The duty ceiling

**Every top speed measured ended at the duty ceiling, not at a limit of the motor.** Up to about
2,500 rpm the drive's duty follows the motor's back-EMF line within a few percent. Above it, it needs
more:

| Speed | Supply | Duty over the back-EMF line | Basis |
|---|---|---|---|
| 2,475 rpm | 11.1 V | +5 % | measured |
| 2,799 rpm | 22.2 and 24 V | **+55 to +67 %** | measured |
| 2,799 rpm | 14.8 V | 99.6 % of full duty — no reserve | measured |

Two things make that excess:

- **Timing, the larger part.** At these speeds the windings' reactance is larger than their resistance, so
  the voltage a load needs grows faster than the back-EMF, and the fixed pair sits 50–60° short of the duty
  bowl's bottom (§5.4). 10° more lead lowers the duty at the top by up to 26 %, measured, as the model
  predicts.
- **The servo's working point shifting, at 24 V.** Above 2,800 rpm at 24 V the field-to-rotor error peaks
  at 86–104 counts on every step, past the 80 at which the servo's fast response engages. That response
  only ever adds duty, so the error's mean settles at 40–45 counts instead of 48: the field sits 4–11°
  less far ahead than the pair asks, and the duty rises and falls with speed rather than climbing smoothly
  (19.4 × 10³ at 3,220 rpm, 25.3 × 10³ at 3,497, 22.0 × 10³ at 4,063). At 7.4 V's tops the error holds 48.

Up to 11.1 V's top (2,475 rpm) the drive runs in one steady state: the error holds its setpoint (mean
47.8–48.3 counts against 48), and the duty within a 5 s window varies by a few hundred counts.

**Direction.** The forward direction (negative increments) needs more duty than reverse at the same
speed: +1 to +4 % at 11.1 V, +3 to +15 % at 7.4 V, rising with speed; at 7.4 V's top forward ran out
of duty at 1,931 rpm and reverse at 2,212.

### 6.4 Starting from rest

Starts from rest followed their command at 999–1,000 ‰ at every supply, and the built-in speed-up
arrived within its band (−46 to +10 ‰ of the planned time). The start current was not separately
measured on this motor.

### 6.5 Stopping and holding

**Stops by distance** came to rest within their band at every supply from 14.8 V up, and in the
forward direction at every supply. **In reverse at 7.4 and 11.1 V, a stop from the top speed rests 4–6
ticks short** of its target (a quarter turn at 7.4 V). The cause is measured: as the shaft slows at low
supply, the drive repeatedly pauses its field to let the rotor catch up (81–164 paused passes in
reverse against 11–51 forward), and each pause is distance the stop does not make up. The rotor does not
stall: it stops 5–20 ms after the field. ⬚ The fix is in progress (§9).

**Stops by time** rested within ±100 ms at every supply, with one exception: one slow forward crawl stop
at 18.5 V came to rest 120 ms after its field stopped.

**The hold** (`holdAtStop(TRUE)`) behaves as on the 6.5″: at 11.1 V its duty rose to its ceiling in
249–250 ms, and a push made it give way after 2 ticks.

**Under load by hand** at a 4 A and a 2 A current limit, the limit held the motor with no fault. The
shaft could not be stopped by hand: at 4 A it makes 136 mN·m, about 20–45 N at the fingertips on a 5 mm
shaft. ⬚ How the blocked-rotor stop behaves on this motor is not yet measured (§9).

**Stopping from 4,000 rpm returns energy to the supply.** A bench supply cannot take it back; ours rode
through every stop from the top.

Coast-versus-short figures like the 6.5″'s were not measured on this motor.

### 6.6 What the driver can prove about the motor at start

The start checks of the [6.5″ §6.6](MOTOR-6.5IN-TECHNICAL-MANUAL.md#66-what-the-driver-can-prove-about-the-motor-at-start)
run on this motor and pass: legal halls, a healthy current-sense rest zero (1.5–4.2 mV on Rev A, band
−17 … +17 mV), each lead driving its phase, and the opt-in wiring walk (4 ticks each way, band 3–11).
A start with the phase leads not connected was refused with all three phase checks failed and the halls
passing, as designed; the same start passed once they were connected.

### 6.7 Smoothness and vibration

The test program times every hall edge against the encoder, so it can see the shaft's speed wobble
inside a turn (first unit, measured):

| | 7.4 V, 1,650–2,212 rpm | 24 V, 2,800–4,343 rpm |
|---|---|---|
| Speed ripple from sector to sector | 0.2–1.5 % | 0–0.3 % |
| Speed ripple once per turn | 0.9–2 % forward (reverse not read) | **up to 13 %** near 3,000 rpm forward and 10 % near 3,360 reverse, falling to under 1 % above 4,000 rpm |
| Current ripple by hall code | under one sense count | under one sense count |

**The sectors do not shake the shaft.** The once-per-turn wobble that peaks near 3,000 rpm and fades above
4,000 rpm is a resonance of the test rig: the motor and the encoder (about the motor's own diameter)
sit unanchored on a rubber mat, and at some speeds the pair shakes, shifts and slowly turns on the mat.
⬚ How much of it is the motor's own is to be measured on a clamped rig (§9). The current sense on a Rev
A board cannot see the vibration at all.

---

## 7 · Current and power

### 7.1 What is measured and what is not

| | Status |
|---|---|
| Total bridge current (DC link) | **measured**, Rev A 5 mV/A: one frame scatters about 0.1 A, so below about 1 A the reading is a handful of counts |
| Per-phase voltages | **measured** |
| Winding resistance | ⛔ **not measured by the driver on Rev A** (§2.4) |
| Bus voltage | ⛔ not measured: our figures use the supply's setting |
| Regeneration, a phase short's current | ⛔ not visible, as on the 6.5″ ([§7.1](MOTOR-6.5IN-TECHNICAL-MANUAL.md#71-what-is-measured-and-what-is-not)) |

**What Rev A costs this motor's measurements.** The timing minimum is found where the current is least
(§5.2). This motor draws 0.2–0.9 A unloaded, and a ±20° sweep moves that by about the board's noise, so
many minima did not resolve: the second unit's at every speed, the first's at a quarter speed and at the
top. The duty, which the driver knows exactly, resolves every time — but its minimum sits at the hold
wall's edge, not at the efficient lead (§5.3).

### 7.2 Protection limits

The limits are the 6.5″'s ([§7.2](MOTOR-6.5IN-TECHNICAL-MANUAL.md#72-protection-limits)): 40 A peak, 27 A
continuous, the field held at 90° while the limit acts. **On Rev A the fold-back reads a filtered
current**, smoothed over 16 frames (0.36 ms), against a floor of 3 mV, and a single frame more than
14 mV over the limit folds at once. Measured on this motor's board: a hand load at 4 A and 2 A limits was
held with no fault; at 4 A the limit folded 201 frames and held the field 271 passes.

### 7.3 Current in normal running

| Condition | DC-link current | Basis |
|---|---|---|
| a quarter and half speed, 14.8 V, first unit | 220–290 mA | measured |
| the same, second unit | 450–840 mA | measured |
| 7.4 V top, 1,650–2,212 rpm | 180–500 mA (forward the higher) | measured |
| 24 V, 2,800–4,343 rpm | 0.65–1.4 A | measured |

The forward direction draws more than reverse at the same speed at low supply: at 7.4 V's top, about
twice (384–500 against 182–264 mA).

---

## 8 · Driving it well

**Alignment**

1. **Use the shipped pair for your supply** (§5.1). It is the measured current minimum at half speed, and
   it sits 15–25° from the hold wall on both units measured (§5.5, §6.2).
2. **Expect the timing to show in headroom, not in current.** At light load this motor's current hardly
   moves with timing; its duty does (§5.3).
3. **Carry the lead in the offset; never move the servo setpoint** (6.5″ §3.3).

**Speed**

4. **The shipped speed range is conservative.** The motor held 0.25 to 4,343 rpm at 24 V and 7.5 to
   1,931–2,212 rpm at 7.4 V (§6.1). The ceilings will rise when the lead follows speed.
5. **The top speed costs duty.** Above about 2,500 rpm the drive needs more voltage than the back-EMF
   explains (§6.3). At 14.8 V the shipped top runs at 99.6 % of full duty, with no reserve for a load.
6. **At 7.4–12 V the slowest steady speed is about 10 rpm** (§6.1); from 14.8 V up it is far lower.

**Stopping**

7. **A reverse stop by distance from top speed at 7.4–11.1 V rests a few ticks short** (§6.5). Stop by
   time, or approach the target more slowly, where a tick matters.
8. **Size the supply for regeneration** when stopping from 4,000 rpm (§6.5).

**Measurement**

9. **Use a Rev B board for anything where current matters.** On Rev A this motor's light-load current is
   a few counts above the noise (§7.1).
10. **Anchor the motor** before trusting a vibration reading (§6.7).

### 8.1 If your board is a Rev B

Everything in this manual was measured on Rev A. The driver's Rev B values for this motor — its offsets,
ceilings and floors — date from 2023 and **have not been re-checked** with this driver. Expect the
current readings to resolve far better (150 mV/A) and the timing minima with them; the motor's own
properties in §2 do not depend on the board.

---

## 9 · What we do not know yet

| Question | Why it matters | What would settle it |
|---|---|---|
| **The efficiency curve above 2,800 rpm** (§5.4). The model draws the headroom curve there; the current minimum is not cleanly measured. | It sets the lead at the very top. | The speed range repeated on a lead that follows speed. |
| **How much the servo's shifted working point at 24 V costs** (§6.3). The error's mean sits 4–11° below its setpoint at the 24 V tops. | It is the other part of the top's excess duty. | A top-speed run once the lead follows speed, which recovers about as much lead as the shift takes. |
| **Z by a cold method.** The back-EMF method did not resolve on this motor (§4.2). | Z is known only to a few degrees. | The cold method's legs examined for why they disagree. |
| **The inductance and the resistance** on our hardware (§2.4). The model gives about 1.06 mH a phase, from the maker's resistance (§5.4). | It checks the model. | A meter and an LCR meter across the leads. |
| **The sector table.** A table of each code's measured width would place the field up to 6° better (§2.4). | It is in progress, from the two units' mean. | The proof run after it is built. |
| **The reverse stop's few-tick shortfall at low supply** (§6.5). | Distance stops in reverse at 7.4–11.1 V. | The fix in progress, then the stops run again. |
| **Vibration on a clamped rig** (§6.7). | Separates the motor's own shaking from the rig's. | The speed range repeated with the motor clamped. |
| **The blocked-rotor stop, and a load the hand can hold.** A bare 5 mm shaft cannot be held (§6.5). | It is how the drive answers a jam. | The hand-load runs with a grip about 25 mm in radius on the shaft. |
| **Unit-to-unit variation.** Two units: the same constant and pattern, one sensor pair and the drag differ (§4.7). | Two is not a population. | More units. |
| **Rev B.** Not run with this driver (§8.1). | Its table values are untested. | The qualification on a Rev B board. |

---

## 10 · About the measurements

Every measurement here was taken on two units of this motor (the second only for its hall map and
timing), on a Rev A 64010 board, with the P2 at 270 MHz, during the driver work of October 2026: the
shaft free with a 360-line encoder on its far end and nothing else on it, on a bench supply set to each
voltage named, the motor and encoder resting unanchored on a rubber mat. The measurements were made with
the driver's own sense channels and the encoder, read through `src/test_bench_single.spin2` and the
motor-adoption tool `src/util_adopt_motor.spin2`; [TECHNIQUES.md](TECHNIQUES.md) explains the methods.
The analyses behind each number are kept in this repository's `DOCs/analyses/` folder.

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
