# P2-BLDC-Motor-Control - Via Serial from RPi, Arduino, or...

Serial control of our Single and Two-motor driver objects P2 Spin2/Pasm2 for our 6.5" Hub Motors with Universal Motor Driver Board

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## The Project

Instead of using the FlySky for remote control this document describe how to use a 2-wire serial interface to control your P2 hardware on your robot platform.

The code for this project implements an active serial receiver running on the P2 and a top-level application which listens for drive/status commands arriving via serial and then forwards the requests to the 2-wheel steering system.

## Current status

Latest Changes:

```
04 May 2022 v1.0.0
- Initial Public Release
```

## Table of Contents

On this Page:

- TBA

Additional pages:

- [README](README.md) - The top level file for this repository
- [Steering and Motor control](DRIVE-OBJECTS.md) - The object public interfaces
- [Start your drive project using these objects](DEVELOP.md) - Walks thru configuration and setup of your own project using these objects
- [Drawings](DRAWINGS.md) - Files (.dwg) that you can use to order your own platform inexpensively
- [To-scale drawings](DOCs/bot-layout.pdf) of possible rectangular and round robotic drive platforms for Edge Mini Break and JonnyMac P2 Development boards


## Wiring our Serial Connection

The **P2-BLDC-Motor-Control-Demo.py** script is built to use the main serial I/O channel at the RPi GPIO Interface.  These are GPIO pins 14 & 15 (header pins 8 & 10).

**NOTE:** FYI a good reference is: [pinout diagram for RPi GPIO Pins](https://pinout.xyz/)

**RPi Wiring for Daemon use:**

| RPi Hdr Pin# | RPi GPIO Name| RPi Purpose | P2 Purpose | P2 Pin # |
| --- | --- | --- | --- | --- |
| 6 | GND | Signal ground| Signal ground | GND near Tx/Rx Pins|
| 8 | GPIO 14 | Uart Tx | Serial Rx (from RPi) | 57
| 10 | GPIO 15 | Uart Rx | Serial Tx (to RPi) | 56

Pick two pins on your P2 dev board to be used for RPi serial communications. The top-level file provided by this project defines these two pins as 56, 57. This was due to the two motor control boards occupying most of the remaining pins on the Mini Edge Breakout board. Feel free to choose different pins. Just remember to adjust the constants in your code to use your pin choices.

### ...

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
