
# P2-BLDC-Motor-Control - Drive Objects

Single and Two-motor driver objects P2 Spin2/Pasm2 for our 6.5" Hub Motors with Universal Motor Driver Board

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

There are two objects in our motor control system. There is a lower-level object (**isp\_bldc_motor.spin2**) that controls a single motor and there's an upper-level object (**isp\_steering_2wheel.spin2**) which coordinates a pair of motors as a drive subsystem.

If you are working with a dual motor device then you'll be coding to the interface of this upper-level object as you develop your drive algorithms.  If you were to work with say a three-wheeled device then you may want to create a steering object that can better coordinate all three motors at the same time. (*And, if you do please consider contributing it to this project so it can be available to us all!*)

The drive subsystem currently uses two cogs, one for each motor.  Conceptually, the drive system is always running. It is influenced by updating control variable values. When the values change the drive subsystem responds accordingly. The public methods of both the steering object and the motor object simply write to these control variables and/or read from associated status variables returning their current value or an interpretation thereof.
## Object: isp\_steering_2wheel.spin2

This steering object makes it easy to make your robot drive forward, backward, turn, or stop. You can adjust the steering to make your robot go straight, drive in arcs, or make tight turns. This steering object is for robot vehicles that have two motors, with one motor driving the left side of the vehicle and the other the right side. 

#### Provide steering-direction and power-for-both-wheels 

The steering object controls both motors at the same time, to drive your vehicle in the direction that you choose. Steering-direction is used to re-interpet the power value that is actually sent to each wheel.

#### Alternatively: Provide power for each wheel seperately

The steering object also provides an alternative form of control where you can make the two motors go at different speeds or in different directions to make your robot turn in more precise ways.

#### Turning Concepts

When you think of turning your robot vehicle you think of turning about some point relative to the robot position (e.g., spin about its center point, spin about one of the wheels, or even make some large arcing turn.) All of these turns can be thought of within a singular concept. If you draw a radial line from the center point of your robot vehicle out thru the center point of the slowest wheel, continuing out beyond your robot... all possible turns that your robot vehicle can make have their center-point somewhere on this line!  By adjusting the power of each wheel and the direction of each wheel you are specifying where the center-point of your turn will be on this line.  Fun, right?

- If you drive one wheel backward and one wheel forward but at the same velocity this spins the robot vehicle about its center-point, one end of our line.

- Ignoring friction issues for this discussion, if you stop one wheel and power the other your robot vehicle is now spinning about the center-point of the stopped wheel, another point on our line.

- Now instead of stopping the wheel just drive it at a slower speed than the other but in the opposite direction. Now our center-point of the spin has moved yet again but this time it moved from over the slower wheel to instead between the slower wheel and the center point of the robot vehicle.

- Lastly, let's instead drive this slow wheel in the same direction as the faster wheel but keep the speed slower. This time the robot vehicle is now moving in a large arc as the center-point of our turn has now moved on our line beyond the exterior of our robot, out past the slower wheel.


#### The Object PUBLIC Interface

The object **isp\_steering_2wheel.spin2** provides the following methods:

| Steering Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveDirection(power, direction)</PRE> | Control the speed and direction of your robot using the {power} and {direction} inputs.</br>Turns both motors on at {power, [(-100) to 100]} but adjusted by {direction, [(-100) to 100]}.</br> AFFECTED BY:  setAcceleration(), setMaxSpeed()
| <PRE>PUB driveForDistance(ltDistance, rtDistance, units)</PRE> | Turn both motors on then turn them off again when either reaches the specified distance {ltDistance} or {rtDistance}, where {*distance} is in {units} [DDU\_IN or DDU\_MM].</BR> Control the forward direction or rate of turn.</br>AFFECTED BY:  setAcceleration(), setMaxSpeedForDistance()
| PUB driveAtPower(leftPower, rightPower) | Turns left motor on at {leftPower} and right at {rightPower}.</br>  Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br>AFFECTED BY:  setAcceleration(), setMaxSpeed()
| PUB stopAfterRotations(rotations) | stops both motors, after either of the motors reaches {rotations}.</br>USE WITH:  driveDirection(), drive()
| PUB stopAfterDistance(distance, units) | stops both motors, after either of the motors reaches {distance} specified in {units} [DDU\_IN or DDU\_MM].</br>USE WITH:  driveDirection(), drive()
| PUB stop() | stops both motors, killing any motion that was still in progress
|  **>--- CONFIG**
| PUB setAcceleration(rate) | Limit Acceleration to {rate} where {rate} is [??? - ???] mm/s squared (default is ??? mm/s squared)
| PUB setMaxSpeed(speed) | Limit top-speed to {speed} where {speed} is [??? - ???] mm/s (default is ??? mm/s)
| PUB setMaxSpeedForDistance(speed) | Limit top-speed of driveDistance() operations to {speed} where {speed} is [??? - ???] mm/s (default is ??? mm/s)
| PUB calibrate() | (we may need this?)
| PUB holdAtStop(bEnable)| Informs the motor subsystem to actively hold postiion (bEnable=true) or coast (bEnable=false) at end of motion 
| PUB resetTracking()| Resets the position tracking values returned by getDegrees()/getRotations()
|  **>--- STATUS**
| PUB getDistance(units) : distanceInUnits | Returns the distance in {units} [DDU\_IN or DDU\_MM] travelled by each motor since last reset
| PUB getDegrees() : ltDegrees, rtDegrees | Returns accumulated degrees, since last reset, for each of the motors
| PUB getRotations() : ltRotations, rtRotations | Returns accumulated rotations, since last reset, for each of the motors
| PUB getStatus() : eStatus | Returns: enumerated constant: DS\_MOVING, DS\_HOLDING or DS\_OFF

**NOTE1** {power} is [(-100) - 100] where neg. values drive backwards, pos. values forward, 0 is hold/stop

**NOTE2** {direction} is [(-100) - 100] A value of 0 (zero) will make your robot vehicle drive straight. A positive number (greater than zero) will make the robot turn to the right, and a negative number will make the robot turn to the left. The farther the steering value is from zero, the tighter the turn will be.


## Object: isp\_bldc_motor.spin2

The BLDC motor object controls a single BLDC Motor. You can turn a motor on or off, control its power level, or turn the motor on for a specified amount of time or rotation.

### LEGO Control/Status form

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

**NOTE1** {power} is [(-100) - 100] where neg is drive backwards, pos is forward, 0 is hold

**NOTE2** {bBrakeAtEnd} is T/F where T means the motor is stopped and is held in position and F means motor power turned off and the motor is allowed to coast

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
