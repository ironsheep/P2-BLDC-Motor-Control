# P2-BLDC-Motor-Control - Configuring the driver for your motor

Select your motor and drive voltage in our Parallax Propeller 2 (P2) project code, and see each supported motor's top speed.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Table of Contents

On this Page:

- [Motors Supported](#motors-supported) - the two motors the driver knows, with their geometry
- [Select a motor, Select wheel size](#select-a-motor-select-wheel-size) - the two constants to set
- [Motor Reference: Top speed at each drive voltage](#motor-reference-top-speed-at-each-drive-voltage) - the speed table and its notes
- [Motor Reference: Commutation](#motor-reference-commutation) - hall zero and lead for each motor
- [How to Contribute](#how-to-contribute) - help improve this project

Additional pages:

- [Main Page](README.md) - Return to the top of this repo
- [Connecting the DocoEng Motor](DOCOENG_MOTOR.md) - which wire goes where
- [Adding support for a new motor](ADDING_MOTOR.md) - characterize a motor the driver does not know yet
- [Drive Objects](DRIVE-OBJECTS.md) - the public interface of the motor objects

## Motors Supported

The motors currently supported by this driver:

| Category | Value | Description |
| --- | --- | --- |
| `MOTR_6_5_INCH` | **6.5" Motor-in-Wheel** | the Parallax Hoverboard-like motor |
| Hall ticks per revolution | 90 ticks | |
| Degrees per hall tick | 4 degrees | |
| Ticks per hall-cycle | 6 ticks | positive power (ticks rising): 1-5-4-6-2-3<br>negative power (ticks falling): 1-3-2-6-4-5 |
| Hall-cycles per revolution | 15 hall-cycles | |
| Degrees per hall-cycle | 24 degrees | |
| Magnets | 30 poles | |
| `MOTR_DOCO_4KRPM` | **DocoEng 4k RPM 24V motor** | the Parallax small motor |
| Hall ticks per revolution | 24 ticks | |
| Degrees per hall tick | 15 degrees | |
| Ticks per hall-cycle | 6 ticks | positive power (ticks rising): 1-5-4-6-2-3<br>negative power (ticks falling): 1-3-2-6-4-5 |
| Hall-cycles per revolution | 4 hall-cycles | |
| Degrees per hall-cycle | 90 degrees | |
| Magnets | 8 poles | |

## Select a motor, Select wheel size

- Select an enum constant value from the list of values
  - If you have the **6.5" In-wheel motor** then use the `MOTR_6_5_INCH` enum value
  - If, instead, you have the **DocoEng 4000 RPM, 24V smaller motor** use the `MOTR_DOCO_4KRPM` enum value
- In your project open the file **isp_bldc_motor_userconfig.spin2** and set `MOTOR_TYPE = {motorEnumValue}` to the value you selected
- Also in this same file, the DocoEng motor does not have a wheel attached. Until you add a wheel or gear to it you will need to set `WHEEL_DIA_IN_INCH = 0.0`. This will disable all distance based status as well as distance based methods (since they are meaningless without an attached gear or wheel diameter).

The next time you compile, the driver will handle your motor correctly.

That's all there is to selecting your motor for use with this driver.

## Motor Reference: Top speed at each drive voltage

`power` 100 is the motor's top speed at your drive voltage, and `power` 1 is its slowest. The driver scales every `power` you command between the two, so "100" means the same thing, full speed, whatever battery you use. The table gives that top speed, the same in both directions.

**How the top speed is chosen.** The drive keeps some voltage in reserve at full speed, so it can still correct the motor when something pushes back. Top speed is the fastest speed that keeps that reserve, not the fastest the motor can be made to spin. Unloaded, the motor meets every `power` across the range. Under load it has less in hand near the top. The drive answers a load with torque, up to its current limit, and a motor held at that limit runs slower than commanded rather than faulting.

All figures are **unloaded**: wheels off the ground, no payload.

| Motor Power (+V) | Top speed, RPM | Hall ticks / sec | Rim speed | Verified on our hardware |
| --- | --- | --- | --- | --- |
| **`MOTR_6_5_INCH`: 6.5" Motor-in-Wheel** | | | | |
| `PWR_6p0V` 6.0V | 95 | 143 | 0.82 m/s | |
| `PWR_7p4V` 7.4V | 118 | 176 | 1.02 m/s | |
| `PWR_11p1V` 11.1V | 176 | 265 | 1.52 m/s | |
| `PWR_12p0V` 12.0V | 191 | 286 | 1.65 m/s | |
| `PWR_14p8V` 14.8V | 235 | 353 | 2.03 m/s | |
| `PWR_18p5V` 18.5V | 294 | 441 | 2.54 m/s | yes |
| `PWR_22p2V` 22.2V | 353 | 529 | 3.05 m/s | |
| `PWR_24p0V` 24.0V | 381 | 572 | 3.30 m/s | |
| **`MOTR_DOCO_4KRPM`: DocoEng 4k RPM 24V motor** | | | | |
| `PWR_6p0V` 6.0V | (*not supported*) | | | |
| `PWR_7p4V` 7.4V | 2,018 | 807 | | yes (Rev A) |
| `PWR_11p1V` 11.1V | 3,030 | 1,212 | | yes (Rev A) |
| `PWR_12p0V` 12.0V | 3,274 | 1,310 | | |
| `PWR_14p8V` 14.8V | 4,039 | 1,616 | | yes (Rev A) |
| `PWR_18p5V` 18.5V | 5,051 | 2,020 | | yes (Rev A) |
| `PWR_22p2V` 22.2V | 6,060 | 2,424 | | yes (Rev A) |
| `PWR_24p0V` 24.0V | 6,551 | 2,620 | | yes (Rev A) |
| `PWR_25p9V` 25.9V | (*not supported: the motor is rated for 24V*) | | | |

**NOTE1:** *Verified on our hardware means we ran that row on our own motors with this release of the driver and it did what the table says. We ran the 18.5V row on a pack of about 20.5-20.7 V; on a pack at the nominal 18.5 V full power needs about 102-104 % of the drive's duty ceiling, and the motor keeps up by letting its lag grow (calculated, not run). The other 6.5" rows are the 18.5V measurement scaled by voltage, which is how the motor behaves, but we have not run them. The DocoEng rows are its top speeds on a Rev A driver board: we ran each marked row, speeding up to it, holding it, slowing to a stop and reversing through zero, on our own motor; the 12.0V row lies between two rows we ran. If you rely on an unchecked row, check it on your own platform.*

**NOTE2:** *The slowest speed, `power` 1, is a crawl: on the 6.5" motor it is well under 1 RPM at any voltage.*

**NOTE3:** *The DocoEng motor is sold as a 4,000 RPM motor at 24V; unloaded, on a Rev A board, it runs faster than that, as the table shows. On a Rev B board the DocoEng motor keeps lower top speeds, which we have not re-checked with this release: about 1,920 to 3,240 RPM depending on the voltage. Its [technical manual](MOTOR-DOCO-TECHNICAL-MANUAL.md) has the measurements.*

**How far the motor travels while stopping** grows with the square of the speed you stop from; see [Drive Objects](DRIVE-OBJECTS.md#how-far-the-motor-travels-while-stopping).

## Motor Reference: Commutation

The driver needs to know where each motor's hall sensors sit relative to its magnets, and how far ahead of the rotor to place the field. Both are built in for the supported motors; there is nothing to set.

| Motor | Hall zero | Lead |
| --- | --- | --- |
| `MOTR_6_5_INCH` | −4° electrical, the same on every unit we have measured | follows speed: about 20° electrical at a crawl, falling to 5–8° from a quarter of top speed upward |
| `MOTR_DOCO_4KRPM` | one offset, the same each way, chosen by supply voltage and board revision from its characterization | (included in the offset) |

Getting these right matters: on the 6.5" motor, placing the field 25° away from the best position draws 15 to 25 times the current for the same speed. How to find them for a new motor is in [ADDING_MOTOR.md](ADDING_MOTOR.md).

Enjoy!

*Stephen*

---

## How to Contribute

This is a project supporting our P2 Development Community. Please feel free to contribute to this project. You can contribute in the following ways:

- File **Feature Requests** or **Issues** (describing things you are seeing while using our code) at the [Project Issue Tracking Page](https://github.com/ironsheep/P2-BLDC-Motor-Control/issues)
- Fork this repo and then add your code to it. Finally, create a Pull Request to contribute your code back to this repository for inclusion with the projects code. See [CONTRIBUTING](CONTRIBUTING.md)

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

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
