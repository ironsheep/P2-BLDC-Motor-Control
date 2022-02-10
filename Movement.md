
# P2-BLDC-Motor-Control
Single and Two-motor driver objects P2 Spin2/Pasm2 for our 6.5" Hub Motors with Universal Motor Driver Board

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

**-- This is a work in progress!! --**

## Object: isp_steering.spin2

The steering object makes it easy to make your robot drive forward, backward, turn, or stop. You can adjust the steering to make your robot go straight, drive in arcs, or make tight turns.

The steering object is for robot vehicles that have two Large Motors, with one motor driving the left side of the vehicle and the other the right side. 

#### Provide steering direction and power-for-both-wheels 

The steering object controls both motors at the same time, to drive your vehicle in the direction that you choose.

| Drive Interface |
| --- |
| PUB drive\_both_duration(power, direction, bBrakeAtEnd, duration)
| PUB drive\_both_degrees(power, direction, bBrakeAtEnd, degrees)
| PUB drive\_both_rotations(power, direction, bBrakeAtEnd, rotations)

#### Alternatively: Provide power for each wheel

The steering object also provides an alternative form of control where you can make the two motors go at different speeds or in different directions to make your robot turn.

| Drive Interface |
| --- |
| PUB drive\_each\_duration(leftPower, rightPower, bBrakeAtEnd, duration)
| PUB drive\_each\_degrees(leftPower, rightPower, bBrakeAtEnd, degrees)
| PUB drive\_each\_rotations(leftPower, rightPower, bBrakeAtEnd, rotations)


## Object: isp\_bldc_motor.spin2

The BLDC motor object controls a single BLDC Motor. You can turn a motor on or off, control its power level, or turn the motor on for a specified amount of time or rotation.

| Drive Interface |
| --- |
| PUB move_duration(power, bBrakeAtEnd, duration)
| PUB move_degrees(power, bBrakeAtEnd, degrees)
| PUB move_rotations(power, bBrakeAtEnd, rotations)

The BLDC motor object provides an alternative form of control which works as if you are controlling a Feedback 360° Servo.

| Fb360 Servo-like Interface | Description |
| --- | --- |
| PUB configureAccel() 
| PUB configureMaxSpeed() 
| PUB configureVelocityControlSpeed(kP, kL, kD, I)
| PUB configureVelocityControlPosition(kP, kL, kD, I)
| PUB resetTurnCount() | use to reset to zero 
| PUB getTurnCount(count) | returns +/- revolutions since last reset
| PUB setHome() | tells motor that current position should be thought of as home
| PUB setSpeed(degrPerSec) +/- degrees/second rotation rate
| PUB setAngle(degrees) | +/- degrees - go to (relative to home)
| PUB moveAngle(degrees) | +/- degrees (relative to curr position)
| PUB setPosition(degrees) | [0-359] rotate to position (code uses shortest amount of movement)
| PUB getPosition() | [0-359] return the current postion of the motor
| PUB initialize() | reset motor position tracking

| CR Servo-like Interface | Description |
| --- | --- |
| TBA...

### ...

---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Disclaimer and Legal

> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor
>
> This project is a community project not for commercial use.
>
> This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by *Parallax Inc., dba Parallax Semiconductor* or any of its affiliates or subsidiaries.

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
