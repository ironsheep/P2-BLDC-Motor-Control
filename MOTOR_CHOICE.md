# P2-BLDC-Motor-Control - Configuring the driver for your motor

We just had the occasion to add support for a new BLDC Motor.  This page reminds us of steps needed to properly select a motor in our project code.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Motors Supported

The motors currently supported by this driver:

| Category | Value | Description |
| --- | --- | --- |
| `MOTR_6_5_INCH` | **-- 6.5" Motor-in-Wheel --** | the Parallax Hoverboard-like motor
| Hall Tics per Revolution | 90 ticks | 
| Degrees per hall tick | 4 degrees
| Ticks per hall-cycle | 6 ticks | FWD (CW): 1-3-2-6-4-5</br>REV (CCW): 1-5-4-6-2-3
| Hall-cycles per Revolution | 15 hall-cycles |
| Degrees per Hall-cycle | 24 degrees |
| Magnets	| 30 poles |
| |
| `MOTR_DOCO_4KRPM` | **-- docoEng.com 4k RPM 24v motor --** | the new Parallax small motor
| Hall Tics per Revolution | 24 ticks | 
| Degrees per hall tick | 15 degrees
| Ticks per hall-cycle | 6 ticks | FWD (CW): 1-5-4-6-2-3</br>REV (CCW): 1-3-2-6-4-5
| Hall-cycles per Revolution | 4 hall-cycles |
| Degrees per Hall-cycle | 90 degrees |
| Magnets	| 8 poles |

## Select a motor, Select wheel size

- Select an Enum constant value from the list of values
  - If you have the **6.5" In-wheel motor** then use the `MOTR_6_5_INCH` enum value
  - If, instead, you have the **DocoEng.com 4000 RPM, 24V smaller motor** use the `MOTR_DOCO_4KRPM` enum value
- In your project open the file **isp\_bldc\_motor\_userconfig.spin2** and set `MOTOR_TYPE = {motorEnumValue}` to the value you selected
- Also in this same file, the DocoEng motor does not have a wheel attached. Until you add a wheel or gear to it you will need to set `WHEEL_DIA_IN_INCH = 0.0`. This will disable all distance based status as well as distance based methods (Since they are meaningless without an attached gear or wheel diameter.

The next time you compile the driver will now handle your new motor correctly.

That's all there is to selecting your motor for use with this driver.

Enjoy!


## Motor Reference: Top speed at each drive voltage

`power` 100 is the motor's top speed at your drive voltage, and `power` 1 is its slowest. The driver scales every `power` you command between the two, so "100" means the same thing, full speed, whatever battery you use. The table gives that top speed, the same in both directions.

**How the top speed is chosen.** The drive keeps some voltage in reserve at full speed, so it can still correct the motor when something pushes back. Top speed is the fastest speed that keeps that reserve, not the fastest the motor can be made to spin. Unloaded, the motor meets every `power` across the range. Under load it has less in hand near the top, and a heavily loaded motor may run slower than commanded; it then holds the fastest speed it can sustain.

All figures are **unloaded**: wheels off the ground, no payload.

| Motor Power (+V) | Top speed, RPM | Hall ticks / sec | Rim speed | Verified on our hardware |
| --- | --- | --- | --- | --- |
| `MOTR_6_5_INCH` | **-- 6.5" Motor-in-Wheel --** | | | |
| `PWR_6p0V` 6.0V | 95 | 143 | 0.82 m/s | |
| `PWR_7p4V` 7.4V | 118 | 176 | 1.02 m/s | |
| `PWR_11p1V` 11.1V | 176 | 265 | 1.52 m/s | |
| `PWR_12p0V` 12.0V | 191 | 286 | 1.65 m/s | |
| `PWR_14p8V` 14.8V | 235 | 353 | 2.03 m/s | |
| `PWR_18p5V` 18.5V | 294 | 441 | 2.54 m/s | ✓ |
| `PWR_22p2V` 22.2V | 353 | 529 | 3.05 m/s | |
| `PWR_24p0V` 24.0V | 381 | 572 | 3.30 m/s | |
| | | | | |
| `MOTR_DOCO_4KRPM` | **-- docoEng.com 4k RPM 24v motor --** | | | |
| `PWR_6p0V`   6.0V | (*not supported*) | | | |
| `PWR_7p4V`   7.4V | 1885 | 754 | | |
| `PWR_11p1V` 11.1V | 3645 | 1458 | | |
| `PWR_12p0V` 12.0V | 2242 | 897 | | |
| `PWR_14p8V` 14.8V | 2517 | 1007 | | |
| `PWR_18p5V` 18.5V | 2662 | 1065 | | |
| `PWR_22p2V` 22.2V | 3145 | 1258 | | |
| `PWR_24p0V` 24.0V | 2615 | 1046 | | |
| `PWR_25p9V` 25.9V | (*not supported: the motor is rated for 24V*) | | | |

**NOTE**(1): *Verified on our hardware* means we ran that row on our own motors with this release of the driver and it did what the table says. The other 6.5" rows are the 18.5V measurement scaled by voltage, which is how the motor behaves, but we have not run them. The DocoEng rows come from characterizing that motor with an earlier release of the driver and have not been re-checked with this one. If you rely on an unchecked row, check it on your own platform.

**NOTE**(2): *The slowest speed, `power` 1, is a crawl: on the 6.5" motor it is well under 1 RPM at any voltage.*

**NOTE**(3): *The DocoEng motor is supposed to achieve 4,000 RPM, we've managed to get this motor up to 3,645 RPM pretty reliably but only at certain drive voltages.  Just "why this is" will take time time understand...*

**How far the motor travels while stopping** grows with the square of the speed you stop from; see [Drive Objects](DRIVE-OBJECTS.md#how-far-the-motor-travels-while-stopping).

## Motor Reference: Commutation

The driver needs to know where each motor's hall sensors sit relative to its magnets, and how far ahead of the rotor to place the field. Both are built in for the supported motors; there is nothing to set.

| Motor | Hall zero | Lead |
| --- | --- | --- |
| `MOTR_6_5_INCH` | −4° electrical, the same on every unit we have measured | follows speed: about 20° electrical at a crawl, falling to 5–8° from a quarter of top speed upward |
| `MOTR_DOCO_4KRPM` | one offset, the same each way, chosen by supply voltage and board revision from its characterization | (included in the offset) |

Getting these right matters: on the 6.5" motor, placing the field 25° away from the best position draws 15 to 25 times the current for the same speed. How to find them for a new motor is in [ADDING_MOTOR.md](ADDING_MOTOR.md).

---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Disclaimer and Legal

> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg


