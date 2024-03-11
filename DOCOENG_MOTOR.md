# P2-BLDC-Motor-Control - Connecting the new motor

This page details which wires on the motor go to where on our control board.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Specs of the new Motor

The new Motor we've added:

| Category | Value | Description |
| --- | --- | --- |
| **-- docoEng.com 4k RPM 24v motor --** || the new Parallax small motor
| Hall Tics per Revolution | 24 ticks | 
| Degrees per hall tick | 15 degrees
| Ticks per hall-cycle | 6 ticks | FWD (CW): 1-5-4-6-2-3</br>REV (CCW): 1-3-2-6-4-5
| Hall-cycles per Revolution | 4 hall-cycles |
| Degrees per Hall-cycle | 90 degrees |
| Magnets	| 8 poles |

## Cabling of new Motor

We're adding the DocoEng.com BLDC motor - 4,000 RPM, 24V to the driver. The motor [specifications are here](./DOCs/DOCOMotor.pdf). These are the connections I used. I ended up cutting off the end of some female connector wires and soldering them to the motor wires to make a connector. While most of use would simply solder on connectors, I was on a road trip and this is what I had access to. ;-) 

| Wire Color | Purpose | Adapter Wire Color | board Connector |
| --- | --- | --- | --- |
| **Hall Sensor Wires** | | *- 26 AWG wires (thinner) -*
| Red | +5V Hall Pwr | adapt Red | Hall IN: +v
| Yellow | Hall U | adapt Yellow | Hall IN: U
| Green | Hall V | adapt Green  | Hall IN: V
| Blue | Hall W | adapt Orange  | Hall IN: W
| Black | Ground | adapt Brown  | Hall IN: +v
| **Motor Drive Wires** | | *- 20 AWG wires -*
| Yellow | Phase U | -no adapter- | Motor out U
| Green | Phase V | -no adapter- | Motor out V
| Blue | Phase W | -no adapter- | Motor out W

**FIGURE 1**: *This is the cabling per the table above.*

![coffee](images/new-motor-connect.jpg)

**FIGURE 2**: *The new motor hooked up.*

![coffee](images/motor-hooked-up.jpg)

*NOTE: the electrical tape "flag" so i can tell relative position of shaft during movement.

Once this cabling of your new motor is completed, you are ready to [configure your driver](MOTOR_CHOICE.md) then run the code.

Enjoy!
-Stephen

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


