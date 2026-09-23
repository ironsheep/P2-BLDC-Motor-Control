# P2-BLDC-Motor-Control - Adding a battery voltage sensor

> **DRAFT, 2026-09-23.** These are the values and construction notes for a sensor that has not been built
> yet. The driver does not read it yet either: that support is being added and this page will say when it
> lands. Build it now if you like; until then it only reads on a meter.

This page shows how to build a small voltage sensor, so the P2 can read your robot's battery pack voltage on
one pin. The motor driver boards cannot do this themselves: their four sense channels measure phase
**current**, not voltage. The sensor is four resistors and a capacitor, with an optional fifth part.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## What it does

A resistor divider scales the pack voltage down into the P2 pin's 0-3.3 V range, and a capacitor filters out
the motors' switching noise. It is sized for a **5S lithium pack** (18.5 V nominal, 21.0 V fully charged),
the pack this project is developed on and the one most hoverboard-motor platforms use. The same sensor also
reads 4S, 3S and 2S packs; see [Other pack sizes](#other-pack-sizes).

## Schematic

```
  PACK +  (Anderson Powerpole)
    │
    ├──[ 4.7 nF C0G 100 V ]──── PACK −      (optional: only at the pack end, only if the lead is long)
    │
  [ 68.1k 1% ]      ◄── inline, right at the Powerpole
    │
    │  yellow wire  (the long run)
    │
    ▼  ─────────────────────── the small board, at the P2 end ───────────────────────
  TAP ──┬──[ 10.0k 1% ]──┬── GND
        │                │
        ├──[ 100 nF ]────┘
        │
      [ 1.0k ]
        │
        ├──[ 1 MΩ ]────────── GND
        │
     yellow ──► female header ──► P2 ADC pin
     black  ──► female header ──► P2 GND pin (the same header group as the ADC pin)

  Every GND on the small board (R2, C1 and R4) joins at one point, and that point IS the black wire.
  The black wire is the sensor's only ground. C2's "PACK −" is at the pack end and is not on the board.
```

## Parts

All four resistors are ordinary **1/4 W, 1% metal-film** through-hole parts. The power they dissipate is
tiny, so 1/4 W is roughly 50 times more than needed. Their ~250 V working rating also covers the motor bus's
voltage spikes.

| Part | Value | Rating | Where | Why |
|---|---|---|---|---|
| R1 | **68.1 kΩ** 1% | 1/4 W metal film | inline, at the Powerpole | top of the divider. It has the pack across it (18.3 V at full charge, about 5 mW). At the pack end it also limits the current in everything downstream to under 0.3 mA |
| R2 | **10.0 kΩ** 1% | 1/4 W metal film | small board | bottom of the divider. **Use the same type and series as R1** so the two drift together with temperature |
| C1 | **100 nF** | 16 V or higher, X7R ceramic | small board, tap to GND | removes the 44 kHz PWM switching noise (about a 180 Hz corner). 1 µF also works (about 18 Hz) |
| R3 | **1.0 kΩ** | 1/4 W, 1% or 5% | small board, tap to pin | protects the P2 pin: if R2 ever opens, the pin's input current stays under 0.3 mA |
| R4 | **1 MΩ** | 1/4 W, 5% is fine | small board, pin to GND | makes an **unplugged sensor read about 0 V**. Without it, a disconnected pin floats near mid-rail and reads as a believable ~12.8 V |
| C2 *(optional)* | **4.7 nF** | **100 V** C0G/NP0 (50 V minimum) | pack end, + to − | catches spikes on a long lead before they reach R1. C0G because it does not lose capacitance under DC bias |

Wire: one **yellow** (sense) and one **black** (ground), 22-26 AWG stranded. You also need 2.54 mm female
header housings and contacts for the P2 end, one Anderson Powerpole contact and housing for the pack end,
and heat-shrink tubing.

## The numbers (5S)

Divider ratio: 10.0k ÷ (68.1k + 10.0k) = **0.1280**. **Pack voltage = pin voltage × 7.81.**

| Pack state | Pack voltage | Voltage at the P2 pin |
|---|---|---|
| Fully charged (4.20 V/cell) | 21.0 V | 2.69 V |
| Nominal (3.70 V/cell) | 18.5 V | 2.37 V |
| Nearly empty (3.20 V/cell) | 16.0 V | 2.05 V |
| Cutoff (3.00 V/cell) | 15.0 V | 1.92 V |
| The pin's full scale | 25.8 V | 3.30 V |

A fully charged pack sits at about 81% of the pin's range, leaving 4.8 V of headroom for a charger's
overshoot or the bus rising while the motors brake.

## Construction

1. **Pack end: R1 inline at the Powerpole.**
   - Solder R1 directly to the Powerpole contact, or to a very short heavy pigtail crimped into it, and put
     the Powerpole on the pack's **+** distribution.
   - ⚠ The smallest Powerpole contacts are made for 12-16 AWG wire, so a bare resistor lead or thin signal
     wire will not crimp securely. Either solder R1's lead to a short 16 AWG pigtail and crimp the pigtail,
     or fold the lead and fill the barrel with solder.
   - Keep R1 **right at the connector**. Everything after it then carries under 0.3 mA, so a chafed wire
     further down cannot short the pack.
   - Heat-shrink over R1's body and both joints.
   - If you fit C2, it goes here too, from **+** to **−**, before R1.
2. **The long run: the yellow wire only.** Run it from R1 to the small board. Route it along the existing
   power wiring and **away from the motor phase leads**, which switch hard and radiate noise.
   - Do **not** run a second ground wire back to the pack. The sensor's ground reference is the P2's own
     ground (step 4), and a separate ground run to the pack would make a loop carrying motor return current.
   - If you want to twist the yellow with a black wire for noise, connect that black at the **P2 end only**
     and leave its pack end unconnected.
3. **The small board.** Solder R2, C1, R3 and R4 to a small piece of perfboard, laid out as the schematic
   shows. Keep the tap node (the joint of R1's wire, R2, C1 and R3) short: that node is where noise gets in.
   **Join the ground ends of R2, C1 and R4 at one point, and solder the black lead to that point.** It is
   the board's only ground and the sensor's only ground connection.
4. **P2 end: two short leads with female headers.** From the board, a **yellow** lead (after R3) goes to the
   chosen ADC pin, and a **black** lead goes to a **GND pin on the same header group**. Use single-pin
   housings if the two pins are not adjacent. Keep these leads short.
5. **Strain relief** at both ends, and heat-shrink or sleeve the small board. On a robot, vibration breaks
   unsupported solder joints long before anything electrical fails.

## Choosing the P2 pin

- Keep clear of the motor boards' pin groups (**P16-P31** and **P32-P47** on this project's platform) and of
  **P56-P63** (on a P2 Edge: the LEDs, the boot flash and the serial/debug pins).
- Pick a pin that is, if possible, **alone in its group of four** (P0-P3, P4-P7, ...). The ADC measures
  against its own group's supply rails, so a quiet group gives a cleaner reading.

## Test before plugging into the P2

With the sensor connected to the pack and **not** plugged into the P2, measure with a meter between the
yellow and black header contacts:

- It should read **pack voltage ÷ 7.81**, which is 2.69 V on a full 5S pack, and **never more than 3.3 V**.
  If it reads higher, a resistor is wrong or open: **do not plug it into the P2.**
- With the Powerpole disconnected, the reading should fall to about 0 V (R4 pulling it down).

## Calibration

The P2's ADC pins have a small fixed offset (up to about 9 mV measured, about 70 mV at the pack), and the
resistors are 1% parts. One calibration covers the resistor tolerances and the loading of R4 and the pin.

1. In `isp_bldc_motor_userconfig.spin2`, set `PACK_SENSOR_FITTED = TRUE` and `PACK_SENSE_PIN` to your pin.
2. Run your program and read `getPackVoltage()`. At the same moment, read the pack with a meter.
3. Set `PACK_SENSE_CAL_PERMILLE` to 1000 × meter ÷ `getPackVoltage()`. For example, if the meter reads 18.62 V
   and the driver reads 18.50 V, set 1006.

An unplugged or broken sensor reads as `PACK_ABSENT`, never as a voltage, and `getHealth()` reports it as
`HLT_PACK`.

## Other pack sizes

**The same sensor reads every pack from 2S to 5S**; only the numbers change. Pack voltage is always the pin
voltage × 7.81.

| Pack | Fully charged | Pin at full charge |
|---|---|---|
| 5S | 21.0 V | 2.69 V |
| 4S | 16.8 V | 2.15 V |
| 3S | 12.6 V | 1.61 V |
| 2S | 8.4 V | 1.08 V |

A smaller pack uses less of the pin's range, but each millivolt at the pin is still 7.8 mV at the pack,
which is far finer than a battery gauge needs.

**To use the full range for a smaller pack instead,** keep R2 at 10.0k and change only R1:

| Pack | R1 | Pin at full charge |
|---|---|---|
| 4S | 52.3 kΩ | 2.70 V |
| 3S | 36.5 kΩ | 2.71 V |
| 2S | 21.0 kΩ | 2.71 V |

The rule: **R1 = 10.0k × (full-charge voltage ÷ 2.69 − 1)**, rounded to the nearest 1% value. The
multiplier then becomes (R1 + 10.0k) ÷ 10.0k.

## Things to know

- **It draws about 0.27 mA from the pack all the time it is connected**, roughly 2.4 Ah a year. That is
  negligible while running, but unplug the Powerpole if the robot will be stored for months.
- **The reading drifts slightly with temperature**, by up to about 0.4% over a 40 °C swing with typical
  100 ppm/°C resistors. Matching R1 and R2 (same type and series) keeps the drift closer to zero.

---

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
