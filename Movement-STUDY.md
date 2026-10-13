# P2-BLDC-Motor-Control - Movement API Study

How LEGO Mindstorms and Parallax BlocklyProp shaped the public interface of our steering and motor objects (2022 design study).

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Table of Contents

On this Page:

- [Steering Control/Status APIs](#steering-controlstatus-apis) - the two-wheel steering interfaces studied (LEGO and BlocklyProp)
- [Motor Control/Status APIs](#motor-controlstatus-apis) - the single-motor and servo interfaces studied

Additional pages:

- [Main Page](README.md) - Return to the top of this repo
- [Drive Objects](DRIVE-OBJECTS.md) - the interface the steering and motor objects actually have
- [Start Your Own Drive Project](DEVELOP.md) - add the objects to your own project

---

This page is a design study from 2022, kept as background. The interface it led to is described in [Drive Objects](DRIVE-OBJECTS.md); the tables below record what was studied, not what was built, and the open questions are the ones the study raised at the time.

While researching I studied both LEGO Mindstorms motor control, since this is for 9-14 year olds to program, and BlocklyProp, the Parallax offering. I intended to develop either side by side interchangeable control methods or some sort of blend of the different methods. For now I'm recording initial thoughts here and it will all gradually be whittled down to the target interface specs for the steering and motor objects.

My thinking so far is that the motor control system is a live system. We as programmers simply adjust the control values and can read the current state/historical status values from the system. This form of thinking allows us to use code that monitors the motors and other sensors and sends values to the drive system -OR- with very little effort use serial receiver code which listens to a multi-variable controller like our Futaba RC controller and forwards value changes to the drive system.

## Steering Control/Status APIs

The steering API makes it easy to make your robot drive forward, backward, turn, or stop. You can adjust the steering to make your robot go straight, drive in arcs, or make tight turns. The steering object is for robot vehicles that have two motors, with one motor driving the left side of the vehicle and the other the right side.

### Provide steering-direction and power-for-both-wheels

The steering API controls both motors at the same time, to drive your vehicle in the direction that you choose. Steering-direction is used to reinterpret the power value that is actually sent to each wheel.

### Alternatively: Provide power for each wheel

The steering API also provides an alternative form of control where you can make the two motors go at different speeds or in different directions to make your robot turn.

### LEGO Drive Control/Status

| LEGO Drive-like Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveBothDuration(power, direction, bBrakeAtEnd, seconds)</PRE> | Turns both motors on for the number of {seconds}, then turns them off (or holds) based on {bBrakeAtEnd}. Control the speed and direction of your robot using the {power} and {direction} inputs.
| <PRE>PUB driveBothDegrees(power, direction, bBrakeAtEnd, degrees)</PRE> | Turns both motors on, waits until one of them has turned for the number of degrees of rotation {degrees}, then turns both motors off (or holds) based on {bBrakeAtEnd}. Control the speed and direction of your robot using the {power} and {direction} inputs.</br> This can be used to make your robot travel a specific distance or turn a specific amount.</br> 360 degrees of rotation corresponds to one full turn of a motor. 
| <PRE>PUB driveBothRotations(power, direction, bBrakeAtEnd, rotations)</PRE> | Turns both motors on, waits until one of them has turned for the number of {rotations}, then turns both motors off (or holds) based on {bBrakeAtEnd}. Control the speed and direction of your robot using the {power} and {direction} inputs.</br>This can be used to make your robot travel a specific distance or turn a specific amount.
| <PRE>PUB driveEachDuration(leftPower, rightPower, bBrakeAtEnd, seconds)</PRE> | Turns both motors on for the number of {seconds}, then turns them off (or holds) based on {bBrakeAtEnd}. Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.
| <PRE>PUB driveEachDegrees(leftPower, rightPower, bBrakeAtEnd, degrees)</PRE> | Turns both motors on, waits until one of them has turned for the number of degrees of rotation {degrees}, and then turns both motors off (or holds) based on {bBrakeAtEnd}. Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br> This can be used to make your robot travel a specific distance or turn a specific amount.</br> 360 degrees of rotation corresponds to one full turn of a motor.
| <PRE>PUB driveEachRotations(leftPower, rightPower, bBrakeAtEnd, rotations)</PRE> | Turns both motors on, waits until one of them has turned for the number of {rotations}, then turns both motors off (or holds) based on {bBrakeAtEnd}.  Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br> This can be used to make your robot travel a specific distance or turn a specific amount.
| PUB stop() | stops both motors, killing any motion that was still in progress
|  **>--- CONFIG**
| PUB resetTracking()| Resets the position tracking values returned by getDegrees()/getRotations()
|  **>--- STATUS**
| PUB getDegrees() | Returns accumulated degrees since last reset for each of the motors
| PUB getRotations() | Returns decimal number degrees/360 as count of rotations since last reset for each of the motors
| PUB getStatus() | Returns: moving to position, holding position or off

**NOTE1:** *{power} is [(-100) - 100] where negative values drive backwards, positive values forward, 0 is hold*

**NOTE2:** *{direction} is [(-100) - 100]. A value of 0 (zero) will make your robot drive straight. A positive number (greater than zero) will make the robot turn to the right, and a negative number will make the robot turn to the left. The farther the steering value is from zero, the tighter the turn will be.*

**NOTE3:** *{bBrakeAtEnd} is T/F where T means the motor is stopped and is held in position and F means motor power turned off and the motor is allowed to coast*

### BlocklyProp Drive Control/Status

| BlocklyProp-like Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB setDriveDistance(ltDistance, rtDistance, units)</PRE> | where {\*distance} is in {units} [ticks, in., or mm]
| PUB setDriveSpeed(ltSpeed, rtSpeed) | where {\*speed} is [(-128) - 128] and zero stops the motor 
| PUB stop() | stops both motors
|  **>--- CONFIG**
| PUB setAcceleration(rate) | where {rate} is [100 - 2000] ticks/s squared (default is 400 ticks/s squared)
| PUB setMaxSpeed(speed) | where {speed} is [0 - 128] ticks/s (default is 128 ticks/s)
| PUB setMaxSpeedForDistance(speed) | where {speed} is [0 - 128] ticks/s (default is listed as 600 ticks/s; see the question below)
| PUB calibrate() | open question: do we need this?
| PUB resetDistance()| Resets the distance tracking values
|  **>--- STATUS**
| PUB getDistance(units) | Returns the distance in {units} [ticks, in., or mm] traveled by each motor since last reset

**NOTE:** *"ticks" in BlocklyProp are single encoder ticks, which are 3.25 mm long and are used as (ticks|in|mm) distance values.*

**NOTE:** *A suggestion the study raised: ticks do not apply to our BLDC motor, so use a unit of measure that makes sense.*

**NOTE:** *A question the study raised: the listed default of 600 ticks/s for setMaxSpeedForDistance(speed) is outside the [0 - 128] range, so it cannot be set. Are the BlocklyProp docs incorrect?*

### BlocklyProp Robot Control Reference

The reference material studied and from which the above information was extracted is found at: [Robot API docs](https://learn.parallax.com/support/reference/propeller-blocklyprop-block-reference/robot)

## Motor Control/Status APIs

With the Motor Control API you can turn a motor on or off, control its power level, or turn the motor on for a specified amount of time or rotation and retrieve its status.

### LEGO Motor Control/Status API

LEGO Mindstorms provides control over large, medium and small motors using the following API:

| LEGO Motor-like Interface | Notes |
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

**NOTE1:** *{power} is [(-100) - 100] where negative is drive backwards, positive is forward, 0 is hold*

**NOTE2:** *{bBrakeAtEnd} is T/F where T means the motor is stopped and is held in position and F means motor power turned off and the motor is allowed to coast*

### BlocklyProp: Feedback 360° control API

BlocklyProp provides control of a Feedback 360° Servo. Control for these servos offers Velocity Control and Angular Control subsystems.

| Fb360 Servo-like Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| PUB setSpeed(degrPerSec) | Where +/- degrees/Sec rotation rate (capped by limitSpeed())
| PUB gotoAngle(degrees) | Where +/- degrees (relative to home as last set)
| PUB moveAngle(degrees) | Where +/- degrees (relative to current position)
| PUB disable() | Turns off active motor control
|  **>--- CONFIG**
| PUB limitAccel(value) | Where value (°/s^2) [600 - 7200] determines how quickly the servo will transition to a new speed setting, in units of degrees per second squared
| PUB limitSpeed(value) | Where value (°/s) [1 - 1080] determines the maximum rotation speed in units of degrees per second, independent of direction
| <PRE>PUB adjustVelocityControl(kP,kL,kD,I)</PRE> | (Speed) Defaults: kP=500,kI=0,kD=0 and I=0
| <PRE>PUB adjustAngularControl(kP,kL,kD,I)</PRE> | (Position) Defaults: kP=12000,kI=600,kD=6000 and I=1000
| PUB resetTracking() | Reset motor position tracking
| PUB setHome() | Tells motor that current position should be thought of as home
| **>--- STATUS**
| PUB getTurnCount() | Returns +/- count of revolutions since last reset
| PUB getPosition() | [0-359] Return the current position of the motor where 0 is home position as last set
| PUB getStatus() | Returns: moving to position, holding position or off
| PUB getSpeed() | Returns +/- degrees/Sec rotation rate, 0 if stopped

### BlocklyProp: CR Servo control API

BlocklyProp also provides control for a Continuous Rotation (CR) Servo.

| CR Servo-like Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| PUB setSpeed(speed) | Where speed is [(-200) - 200], negative values backward, positive forward, 0 is stop
| PUB setRamp(ramp) | Where ramp [0 - 100] is amount of change each 20ms cycle
| PUB disable() | Turns off active motor control
| **>--- STATUS**
| PUB getSpeed() | Returns speed [(-200) - 200], negative values backward, positive forward, 0 stopped
| PUB getRamp() | Returns ramp [0 - 100] the requested amount of change each 20ms cycle
| PUB getStatus() | Returns: moving, holding position or off

### BlocklyProp Servo Reference

The reference material studied and from which the above information was extracted is found at: [Feedback 360° and CR Servo API docs](https://learn.parallax.com/support/reference/propeller-blocklyprop-block-reference/servo)

---

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## How to Contribute

This is a project supporting our P2 Development Community. Please feel free to contribute to this project. You can contribute in the following ways:

- File **Feature Requests** or **Issues** (describing things you are seeing while using our code) at the [Project Issue Tracking Page](https://github.com/ironsheep/P2-BLDC-Motor-Control/issues)
- Fork this repo and then add your code to it. Finally, create a Pull Request to contribute your code back to this repository for inclusion with the projects code. See [CONTRIBUTING](CONTRIBUTING.md)

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
