# P2-BLDC-Motor-Control - Configuring the driver for your motor

We just had the occasion to add support for a new BLDC Motor.  This page helps us reminds us of steps needed to properly select a motor in our project code.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Motors Supported

The motors currently supported by this driver:


| Category | Value | Description |
| --- | --- | --- |
| **-- 6.5" Wheel --** || the Parallax Hoverboard-like motors
| Hall Tics per Revolution | 90 ticks | 
| Degrees per hall tick | 4 degrees
| Ticks per hall-cycle | 6 ticks | FWD 110 -> 100 -> 101 -> 010 -> 100 -> 101</br>-or-</br>001 -> 101 -> 100 -> 110 -> 010 -> 011</br>etc.
| Hall-cycles per Revolution | 15 hall-cycles |
| degrees per Hall-cycle | 24 degrees |
|
 **-- docoEng.com 4k RPM 24v motor --** || the new Parallax small motor
| Hall Tics per Revolution | 24 ticks | 
| Degrees per hall tick | 15 degrees
| Ticks per hall-cycle | 6 ticks | 001 -> 011 -> 010 -> 110 -> 100 -> 101</br>-or-</br>001 -> 101 -> 100 -> 110 -> 010 -> 011</br>etc.
| Hall-cycles per Revolution | 4 hall-cycles |
| degrees per Hall-cycle | 90 degrees |
|



## Select a motor

- determine geometry of motor

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
