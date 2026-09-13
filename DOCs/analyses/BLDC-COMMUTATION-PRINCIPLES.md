# BLDC commutation — principles from the board designer

**Provenance:** the Universal Motor Driver board designer, relayed verbatim by Stephen,
2026-09-12. Recorded as a **supplied technique** — the authority for *how this hardware is
meant to be driven* (doctrine overlay P7, second row). What P2 silicon or Spin2 defines stays
with `p2kb-mcp`; what the driver code actually does stays with the source.

---

## The notes, verbatim

> *"The key to driving bldc Motors is giving power at plus or minus 90° of current position,
> position being electrical angle, which is always a fraction of mechanical angle."*

> *"Knowing the electrical angle is vital. Which resolves 0 to 360° 12 bits. With wrap
> around, of course. That gives us 4,096 positions, from which we can determine what plus and
> minus 90° of electrical angle would be."*

## What they state, as principles

1. **Drive at ±90° electrical from the rotor's present electrical position.** +90° for one
   direction, −90° for the other. This is the torque-producing quadrature relationship: power
   applied at any other angle produces less torque per amp.
2. **Electrical angle, not mechanical.** Electrical angle is a fraction of mechanical angle —
   one mechanical revolution spans several electrical cycles, one per pole pair.
3. **Resolve electrical angle to 12 bits** — 4,096 positions per electrical cycle, with
   wrap-around, so ±90° is ±1,024 positions.

## What the driver does today

Read from `src/isp_bldc_motor.spin2` at `4e82b08` (DERIVED from source; line numbers drift,
locate by the quoted instruction).

| Aspect | The driver | Against the principles |
|---|---|---|
| **Where the field is placed** | The drive angle `angle_` is **commanded**: it advances by `drv_incr` every control pass (`add angle_, drv_incr`), and the three phase levels are `duty × cos(angle_ + 0/120/240°)` via `qrotate`. | The field is not computed from the rotor's position; it is driven ahead and **corrected**. |
| **How rotor position enters** | Only as feedback: `err_ = hall_angle + offset − angle_`, reduced to 8 bits (`sar err_, #24`, 256 counts per 360°). Duty is servoed so `|err_|` sits at **`256/6` = 60°** (`sub tmpY, #256/6` → `duty_up`/`duty_dn`). A lag of ~176° faults. | The held relationship is **60°**, not the designer's **90°**, measured against a hall estimate rather than the true rotor angle. |
| **Rotor angle resolution** | Three halls, **6 positions per electrical cycle** (60° sectors). The hall-angle table gives each sector's angle, with a second copy shifted by one sector (−60°) for the other direction of travel. | **6 positions, not 4,096.** Within a sector the rotor could be anywhere across 60°. |
| **Command resolution** | `angle_` and the offsets are full 32-bit fractions of a turn. | Finer than 12 bits on the command side. |
| **What the offsets carry** | One offset per direction: negative increments use `offset_fwd` (43°), positive use `offset_rev` (317° = −43°). | Each offset mixes **two things**: where the hall pattern's zero sits relative to true electrical angle (the same for both directions) and how far the field should lead (a sign per direction). |

## How the principles apply

1. **They explain the Bench Pass 1 asymmetry** (DERIVED). If each direction wants the field at
   ±90° from the rotor, then an offset pair symmetric about 0° (43 / −43) is right only if the
   hall pattern's zero *is* at 0°. If it sits at some other angle Z, one direction leads by
   more than it needs and the other by less — less torque per amp in one direction, hence more
   current at the same speed. That is exactly the measured signature: a negative increment draws
   1.76–1.97× the current of a positive one, on both motors
   ([evaluation](bench/2026-09-12/CHAR-RUN-EVALUATION.md) finding 1).
2. **They give the offset scan falsifiable predictions** (DERIVED, «#3520»):
   - **The two per-direction minima should be symmetric about the hall zero** — their midpoint
     estimates Z.
   - **At its own minimum, each direction should draw about the same current.** Stephen's goal
     — forward and reverse load near-identical — is what the principle predicts is reachable.
     A residual imbalance at the minima falsifies the simple model and points somewhere else:
     unequal hall sectors, sensor placement, or the one-sector shift between the two tables.
   - **The minimum is broad.** Torque per amp falls roughly as the sine of the lead angle, so
     ±15° from the optimum costs only a few percent. Fit the curve; do not trust the single
     lowest noisy sample.
   - **The optimum may move with speed.** Current lags the applied voltage more at higher
     electrical frequency, so the voltage lead that places the *current* at 90° grows with
     speed. The ½-speed confirmation must compare minima, not just default against found.
3. **They name what the driver would need to follow them directly** (DERIVED; a change to what
   the driver *is*, so Stephen's scope call — PL-26):
   - Separate the two meanings the offsets carry: one hall-alignment constant, and a lead angle
     applied +/− per direction.
   - Hold the field at 90° rather than the 60° the duty servo targets today.
   - Resolve rotor angle better than 60°: interpolate within a sector from the time since the
     last hall edge and the current speed, or estimate it from the phase voltages the driver
     already samples every cycle (`sense_u/v/w`).

## The two motors are not the same problem

Facts from `src/isp_bldc_motor.spin2` (`hallTicInfoForMotor()`, `offsetsForMotor()`,
`confgurePowerLimits()` and their characterisation comments) and `util_char_motor.spin2`'s
motor notes:

| | 6.5″ hub | Doco 4k RPM |
|---|---|---|
| Hall ticks per revolution | 90 (4° per tick) | 24 (15° per tick) |
| Pole pairs | 15 (30 poles) | 4 (8 poles) |
| Electrical cycles per mechanical revolution | 15 | 4 |
| Top recorded speed in the source comments | 408 ticks/s at 18.5 V = **68 Hz electrical** | 1,458 ticks/s at 11.1 V = **243 Hz electrical** |
| Control-loop passes per hall sector at that speed | ~108 | ~30 |
| Electrical degrees per 22.8 µs control pass at that speed | ~0.6° | ~2° |
| 12 bits of electrical angle, per mechanical revolution | 61,440 | 16,384 |
| Commutation offsets | one pair (43/317), same for both board revisions | a table per voltage, **different per board revision** (Rev B 33–45, Rev A 52–54) |
| Speed ceilings | per voltage, same for both boards | per voltage, **different per board revision** |

All DERIVED from those numbers:

1. **The hub is the more alignment-sensitive motor.** A sensor placement error of one
   mechanical degree is 15° electrical on the hub and 4° on the Doco. The same small
   misplacement moves the hub's hall zero almost four times as far. That fits a large
   measured asymmetry on the hub.
2. **The Doco is the more speed-sensitive motor.** It runs at roughly 3.6× the electrical
   frequency, so current lags the applied voltage much more, and the voltage lead needed to put
   *current* at 90° changes more across its speed range. A fixed offset is a closer
   approximation on the hub than on the Doco. The Doco's per-voltage offset table already
   behaves like a crude speed-dependent advance: the Rev B column rises from 33° at 7.4 V to
   45° at 24 V.
3. **Timing resolution matters more on the Doco.** At top speed a hall edge can be seen up to
   ~2° electrical late on the Doco against ~0.6° on the hub, and interpolating within a sector
   has ~30 control passes to work with rather than ~108.
4. **The hub's sectors are the least uniform.** Thirty magnets and three sensors around a large
   rotor make unequal sector widths more likely. Interpolating within a sector assumes equal
   sectors, so on the hub it may need a per-sector correction.
5. **The offset scan's answer does not transfer.** Pole count, hall geometry, the direction
   tables (the Doco's "forward" table is the hub's "reverse" table) and the board-dependent
   columns all differ. The Doco needs its own scan on its own rig, which is deferred past the
   next release (decision 2026-09-11).

## Top speed — the phase error costs it

In this driver the top speed is a **fault ceiling**, not a plateau. The source comments
record each ceiling as *"anything above yields RPM … (until fault at …)"*. The fault fires
when the commanded angle outruns the rotor by ~176°. The rotor keeps up only while the motor
can produce enough torque from the voltage headroom left above its back-EMF, and that headroom
shrinks as speed rises.

So **anything that wastes torque per amp at speed lowers the ceiling** (DERIVED):

- **The hall-zero misalignment** costs one direction more than the other. Prediction: on the
  hub, the negative-increment direction — the one drawing ~1.9× the current — faults at a
  lower speed than the positive one. The ceilings in the source are single numbers applied to
  both directions, and no per-direction ceiling has ever been measured.
- **A fixed lead while current lag grows with speed** puts the current further from 90°
  exactly where headroom is scarcest. That matters more on the Doco.
- **The 60° servo relationship** rather than 90°.
- Beyond placing current at 90°, **advancing the lead further at high speed weakens the
  effective back-EMF and can raise top speed** above the voltage-limited point. That is general
  motor-control practice, not measured on this hardware; recorded as an option, not a claim.

**How to measure it:** per-direction speed ceilings on the hub, before and after the scanned
offsets are applied — the C-1 speed ladder in Bench Pass 3, run in both directions.
