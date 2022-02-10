
# P2-BLDC-Motor-Control
Single and Two-motor driver objects P2 Spin2/Pasm2 for our 6.5" Hub Motors with Universal Motor Driver Board

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

**-- This is a work in progress!! --**

As I'm researching I'm studying both LEGO Mindstorms motor control since this is for 9-14 year olds to program and I'm studying BlocklyProp the Parallax Offering.  I'm intending to develop either side by side interchangable control methods or some sort of blend of the different methods. Let's see how it turns out! For now I'm recording initial thoughts here and it will all gradually be whittled down to the target interface specs for the steering and motor objects.

My thinking so far is that the motor control system is a live system. We as programmers simply adjust the control values and can read the current state/historical status values from the system.  This form of thinking allows us to place code that monitors the motors and other sensors and influences the drive system or with very little effort a simple multi-variable controller like our Futaba RC controller.

## Object: isp_steering.spin2

The steering object makes it easy to make your robot drive forward, backward, turn, or stop. You can adjust the steering to make your robot go straight, drive in arcs, or make tight turns.

The steering object is for robot vehicles that have two Large Motors, with one motor driving the left side of the vehicle and the other the right side. 

#### Provide steering direction and power-for-both-wheels 

The steering object controls both motors at the same time, to drive your vehicle in the direction that you choose.

| LEGO Drive Interface |
| --- |
| PUB driveBothDuration(power, direction, bBrakeAtEnd, duration)
| PUB driveBothDegrees(power, direction, bBrakeAtEnd, degrees)
| PUB driveBothRotations(power, direction, bBrakeAtEnd, rotations)

#### Alternatively: Provide power for each wheel

The steering object also provides an alternative form of control where you can make the two motors go at different speeds or in different directions to make your robot turn.

| LEGO Drive Interface |
| --- |
| PUB driveEachDuration(leftPower, rightPower, bBrakeAtEnd, duration)
| PUB driveEachDegrees(leftPower, rightPower, bBrakeAtEnd, degrees)
| PUB driveEachRotations(leftPower, rightPower, bBrakeAtEnd, rotations)


## Object: ispBldc_motor.spin2

The BLDC motor object controls a single BLDC Motor. You can turn a motor on or off, control its power level, or turn the motor on for a specified amount of time or rotation.

### LEGO Control/Status form

| LEGO Motor-likeInterface | Notes |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB moveDuration(power, bBrakeAtEnd, seconds) </PRE>| Turns the motor on for the number of {seconds}, then turns it off (or holds) based on {bBrakeAtEnd}. Control the speed and direction of the motor using the {power}. 
| <PRE>PUB moveDegrees(power, bBrakeAtEnd, degrees)</PRE>| Turns the motor on for the number of degrees of rotation in {degrees}, then turns it off (or holds) based on {bBrakeAtEnd}.  Control the speed and direction of the motor using the {power}. </br>360 degrees of rotation results in one full turn of the motor.
| <PRE>PUB moveRotations(power, bBrakeAtEnd, rotations) </PRE>| Turns the motor on for the number of {rotations}, then turns it off (or holds) based on {bBrakeAtEnd}. Control the speed and direction of the motor using the {power}.</br>1 rotation (or 360 degrees)  results in one full turn of the motor.
| PUB disable() | Turns off active motor control 
|  **>--- CONFIG**
| PUB resetTracking()| Resets the position tracking values returned by getDegrees()/getRotations()
|  **>--- STATUS**
| PUB getDegrees() | Returns accumulated degrees since last reset
| PUB getRotations() | Returns decimal number degrees/360 as count of rotations since last reset
| PUB getPower() | Returns the current motor power level if the motor is running (1-100), or 0 if the motor is stopped
| PUB getStatus() | Returns: moving to position, holding position or off

**NOTE1** {power} is [(-100) - 100] where neg is drive backwards, pos is forward, 0 is hold

**NOTE2** {bBrakeAtEnd} is T/F where T means stop the motor by holding at the ending position and F means just turn off motor control (effectively coast)

### BlocklyProp Feedback 360° control form

The BLDC motor object provides an alternative form of control which works as if you are controlling a Feedback 360° Servo. Control for these servos offers Velocity Control and Angular Control subsystems.

| Fb360 Servo-like Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| PUB setSpeed(degrPerSec) | Where +/- degrees/Sec rotation rate (capped by limitSpeed())
| PUB gotoAngle(degrees) | Where +/- degrees (relative to home as last set)
| PUB moveAngle(degrees) | Where +/- degrees (relative to curr position)
| PUB disable() | Turns off active motor control
|  **>--- CONFIG**
| PUB limitAccel(value) | Where value (°/s2) [600 - 7200] determines how quickly the servo will transition to a new speed setting, in units of degrees per second squared
| PUB limitSpeed(value) | Where value (°/s2) [1 - 1080] determines the maximum rotation speed in units of degrees per second, independent of direction
| <PRE>PUB adjustVelocityControl(kP,kL,kD,I)</PRE> | (Speed) Defaults: kP=500,kI=0,kD=0 and I=0
| <PRE>PUB adjustAngularControl(kP,kL,kD,I)</PRE> | (Position) Defaults: kP=12000,kI=600,kD=6000 and I=1000
| PUB resetTracking() | Reset motor position tracking
| PUB setHome() | Tells motor that current position should be thought of as home
| **>--- STATUS**
| PUB getTurnCount() | Returns +/- count of revolutions since last reset
| PUB getPosition() | [0-359] Return the current postion of the motor where 0 is home position as last set
| PUB getStatus() | Returns: moving to position, holding position or off
| PUB getSpeed() | Returns +/- degrees/Sec rotation rate, 0 if stopped


### BlocklyProp CR Servo control form

The BLDC motor object provides an alternative form of control which works as if you are controlling a Continuous Rotation (CR) Servo.

| CR Servo-like Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| PUB setSpeed(speed) | Where speed is [(-200) - 200], neg values backward, pos forward, 0 is stop
| PUB setRamp(ramp) | Where ramp [0 - 100] is amount of change ea. 20ms cycle
| PUB disable() | Turns off active motor control
| **>--- STATUS**
| PUB getSpeed() | Returns speed [(-200) - 200], neg values backward, pos forward, 0 stopped
| PUB getRamp() | Returns ramp [0 - 100] the requested amount of change ea. 20ms cycle
| PUB getStatus() | Returns: moving, holding position or off


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
