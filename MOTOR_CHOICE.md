# P2-BLDC-Motor-Control - Configuring the driver for your motor

We just had the occasion to add support for a new BLDC Motor.  This page helps us reminds us of steps needed to properly select a motor in our project code.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Motors Supported

The motors currently supported by this driver:

| Category | Value | Description |
| --- | --- | --- |
| `MOTR_6_5_INCH` | **-- 6.5" Motor-in-Wheel --** | the Parallax Hoverboard-like motors
| Hall Tics per Revolution | 90 ticks | 
| Degrees per hall tick | 4 degrees
| Ticks per hall-cycle | 6 ticks | FWD (CW): 1-3-2-6-4-5</br>REV (CCW): 1-5-4-6-2-3
| Hall-cycles per Revolution | 15 hall-cycles |
| Degrees per Hall-cycle | 24 degrees |
| |
| `MOTR_DOCO_4KRPM` | **-- docoEng.com 4k RPM 24v motor --** | the new Parallax small motor
| Hall Tics per Revolution | 24 ticks | 
| Degrees per hall tick | 15 degrees
| Ticks per hall-cycle | 6 ticks | FWD (CW): 1-5-4-6-2-3</br>REV (CCW): 1-3-2-6-4-5
| Hall-cycles per Revolution | 4 hall-cycles |
| Degrees per Hall-cycle | 90 degrees |

## Select a motor

- Select an Enum constant value from the list of values
  - If you have the **6.5" In-wheel motor** then use the `MOTR_6_5_INCH` enum value
  - If, instead, you have the **DocoEng.com 4000 RPM, 24V smaller motor** use the `MOTR_DOCO_4KRPM` enum value
- In your project open the file **isp\_bldc\_motor\_userconfig.spin2** and set `MOTOR_TYPE = {motorEnumValue}` to the value you selected

The next time you compile the driver will now handle your new motor correctly.

That's all there is to selecting your motor for use with this driver.

Enjoy!


## Motor Reference: Attainable RPM at Power

When characterizing the motors for this driver we search for the maximum attainable RPM at each power level and we set this as the limit for the motor
at a given voltage. This way the driver can take a "Set power to 100%" request and "I'm driving the motor with a 12V supply" and can scale the request correctly for the power system. 

This "limiting" of the reqeust at a given power level allows us to drive the motor at the highest RPM possible without the motor faulting.  (That is without the driver being unable to keep the motor at the requested RPM value.)

**NOTE:** While there is a range of max rpm requests that all come up with the same achievable RPM at given power level we choose the lowest value (*the value which gives the same RPM but at the lowest possible current draw that can achieve the RPM value.*)

**NOTE2:** these limits are all based on "no load" conditions. Which means under load the motor can fault. We are planning on adding a fall back so we can drive the motor as best we can while still handling a given load.

| Motor Power (+V) | RPM | Max hall-tics / sec |
| --- | --- | --- |
| `MOTR_DOCO_4KRPM` | **-- docoEng.com 4k RPM 24v motor --**</br>&nbsp;&nbsp;(+ is Fwd/CW, - is Rev/CCW ) |
| `PWR_6V` 6.0V | *tba*
| `PWR_7p4V` 7.4V | *tba*
| `PWR_11p1V` 11.1V | +1640/-1640 | 656
| `PWR_12V` 12.0V | +1660/-1660 | 664
| `PWR_14p8V` 14.8V | +2500/-2500 | 1000
| `PWR_18p5V` 18.5V | +2860/-2860 | 1144
| `PWR_22p2V` 12.2V | +2860/-2860 | 1144
| `PWR_24V` 24.0V | *tba*
| |
| `MOTR_6_5_INCH` | **-- 6.5" Motor-in-Wheel --** 
| `PWR_6V` 6.0V | *tba*
| `PWR_7p4V` 7.4V | *tba*
| `PWR_11p1V` 11.1V | +165.3/-165.3 | 248
| `PWR_12V` 12.0V | +181.3/-181.3 | 272
| `PWR_14p8V` 14.8V | +224.0/-224.0 | 336
| `PWR_18p5V` 18.5V | +272.0/-272.0 | 408
| `PWR_22p2V` 12.2V | +320.0/-320.0 | 480
| `PWR_24V` 24.0V | *tba*

---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Disclaimer and Legal

> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Copyright © 2022 Iron Sheep Productions, LLC. All rights reserved.

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765
