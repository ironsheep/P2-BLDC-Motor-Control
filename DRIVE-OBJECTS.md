
# P2-BLDC-Motor-Control - Drive Objects

Single and Two-motor driver objects P2 Spin2/Pasm2 for our 6.5" Hub Motors with Universal Motor Driver Board

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

There are two objects in our motor control system. There is a lower-level object (**isp\_bldc_motor.spin2**) that controls a single motor and there's an upper-level object (**isp\_steering_2wheel.spin2**) which coordinates a pair of motors as a drive subsystem.

If you are working with a dual motor device then you'll be coding to the interface of this upper-level object as you develop your drive algorithms.  If you were to work with say a three-wheeled device then you may want to create a steering object that can better coordinate all three motors at the same time. (*And, if you do please consider contributing it to this project so it can be available to us all!*)

The drive subsystem currently uses two cogs, one for each motor.  Conceptually, the drive system is always running. It is influenced by updating control variable values. When the values change the drive subsystem responds accordingly. The public methods of both the steering object and the motor object simply write to these control variables and/or read from associated status variables returning their current value or an interpretation thereof.
## Object: isp\_steering_2wheel.spin2

This steering object makes it easy to make your robot drive forward, backward, turn, or stop. You can adjust the steering to make your robot go straight, drive in arcs, or make tight turns. This steering object is for robot vehicles that have two motors, with one motor driving the left side of the vehicle and the other the right side. 

### Provide steering-direction and power-for-both-wheels 

The steering object controls both motors at the same time, to drive your vehicle in the direction that you choose. Steering-direction is used to re-interpet the power value that is actually sent to each wheel.

### Alternatively: Provide power for each wheel seperately

The steering object also provides an alternative form of control where you can make the two motors go at different speeds or in different directions to make your robot turn in more precise ways.

### Turning Concepts

When you think of turning your robot vehicle you think of turning about some point relative to the robot position (e.g., spin about its center point, spin about one of the wheels, or even make some large arcing turn.) All of these turns can be thought of within a singular concept. If you draw a radial line from the center point of your robot vehicle out thru the center point of the slowest wheel, continuing out beyond your robot... all possible turns that your robot vehicle can make have their center-point somewhere on this line!  By adjusting the power of each wheel and the direction of each wheel you are specifying where the center-point of your turn will be on this line.  Fun, right?

- If you drive one wheel backward and one wheel forward but at the same velocity this spins the robot vehicle about its center-point, one end of our line.

- Ignoring friction issues for this discussion, if you stop one wheel and power the other your robot vehicle is now spinning about the center-point of the stopped wheel, another point on our line.

- Now instead of stopping the wheel just drive it at a slower speed than the other but in the opposite direction. Now our center-point of the spin has moved yet again but this time it moved from over the slower wheel to instead between the slower wheel and the center point of the robot vehicle.

- Lastly, let's instead drive this slow wheel in the same direction as the faster wheel but keep the speed slower. This time the robot vehicle is now moving in a large arc as the center-point of our turn has now moved on our line beyond the exterior of our robot, out past the slower wheel.


### The 2-Wheel Steering Object PUBLIC Interface

The object **isp\_steering_2wheel.spin2** provides the following methods:

| Steering Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveDirection(power, direction)</PRE> | Control the speed and direction of your robot using the {power} and {direction} inputs.</br>Turns both motors on at {power, [(-100) to 100]} but adjusted by {direction, [(-100) to 100]}.</br> AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| <PRE>PUB driveForDistance(leftDistance, rightDistance, distanceUnits)</PRE> | Control the forward direction or rate of turn of your robot using the {leftDistance} and {rightDistance} inputs.</br>Turn both motors on then turns them off again when either reaches the specified {leftDistance} or {rightDistance}, where {\*distance} is in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M].</BR> AFFECTED BY:  setAcceleration(), setMaxSpeedForDistance(), holdAtStop()
| PUB driveAtPower(leftPower, rightPower) | Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br>Turns left motor on at {leftPower} and right on at {rightPower}. Where {\*Power} are in the range [(-100) to 100].</br>AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits) | Stops both motors, after either of the motors reaches {rotationCount} of {rotationUnits} [DRU\_DEGREES, DRU\_ROTATIONS, or DRU\_HALL_TICKS].</BR>USE WITH:  driveDirection(), drive()
| PUB stopAfterDistance(distance, distanceUnits) | Stops both motors, after either of the motors reaches {distance} specified in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M].</br>USE WITH:  driveDirection(), drive()
| PUB stopAfterTime(time, timeUnits) | Stops both motors, after {time} specified in {timeUnits} [DTU\_IN\_MILLISEC or DTU\_IN\_SEC] has elapsed.</br>USE WITH:  driveDirection(), drive()
| PUB stopMotors() | Stops both motors, killing any motion that was still in progress</BR> AFFECTED BY:holdAtStop()
| PUB emergencyCutoff() | EMERGENCY-Stop - Immediately stop both motors, killing any motion that was still in progress
| PUB clearEmergency() | clear the emergency stop status allowing motors to be controlled again
|  **>--- CONFIG**
| PUB start(eLeftMotorBasePin, eRightMotorBasePin, eMotorVoltage) | Specify motor control board connect location for each of the left and right motor control boards
| PUB stop() | Stop cogs and release pins assigned to motor drivers
| PUB setAcceleration(rate) | **NOT WORKING, YET** <BR>Limit Acceleration to {rate} where {rate} is [??? - ???] mm/s squared (default is ??? mm/s squared)
| PUB setMaxSpeed(speed) | Limit top-speed to {speed} where {speed} is  [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setMaxSpeedForDistance(speed) | Limit top-speed of driveDistance() operations to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB calibrate() | **NOT WORKING, YET** <BR>*(we may need this?)*
| PUB holdAtStop(bEnable)| Informs the motor subsystem to actively hold postiion (bEnable=true) or coast (bEnable=false) at end of motion 
| PUB resetTracking()| Resets the position tracking values returned by getDistance() and getRotations()
|  **>--- STATUS**
| PUB getDistance(distanceUnits) : leftDistanceInUnits, rightDistanceInUnits | Returns the distance in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M] travelled by each motor since last reset
| PUB getRotationCount(rotationUnits) : leftRotationCount, rightRotationCount | Returns accumulated {*RotationCount} in {rotationUnits} [DRU\_DEGREES, DRU\_ROTATIONS, or DRU\_HALL_TICKS], since last reset, for each of the motors.  
| PUB getPower() : leftPower, rightPower | Returns the last specified power value for each of the motors (will be zero if the motor is stopped).
| PUB getStatus() : eLeftStatus, eRightStatus | Returns status of motor drive state for each motor: enumerated constant: DS\_MOVING, DS\_HOLDING, DS\_OFF, or DS_Unknown
| PUB getMaxSpeed() : maxSpeed | Returns the last specified {maxSpeed}
| PUB getMaxSpeedForDistance() : maxSpeed4dist | Returns the last specified {maxSpeedForDistance}

**NOTE1** {power} whenever used is [(-100) - 100] where neg. values drive backwards, pos. values forward, 0 is hold/stop

**NOTE2** {direction} whenever used is [(-100) - 100] A value of 0 (zero) will make your robot vehicle drive straight. A positive number (greater than zero) will make the robot turn to the right, and a negative number will make the robot turn to the left. The farther the steering value is from zero, the tighter the turn will be.

**NOTE3** A HALL TICK is 4° for our 6.5" Dia. Motors.

**NOTE4** {e\*MotorBasePin} is one of: PINS\_P0\_P15, PINS\_P16\_P31, or PINS\_P32\_P47

**NOTE5** {eMotorVoltage} is one of: PWR\_7p4V, PWR\_11p1V, PWR\_12V, PWR\_14p8V, PWR\_18p5V, or PWR\_22p2V

## Object: isp\_bldc_motor.spin2

The BLDC motor object controls a single BLDC Motor. You can turn a motor on or off, control its power level, or turn the motor on for a specified amount of time or rotation.


### The Motor Object PUBLIC Interface

The object **isp\_bldc_motor.spin2** provides the following methods:

| Single-motor Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveForDistance(distance, distanceUnits)</PRE> | Control the forward direction of this motor using the {distance} and {distanceUnits} inputs.</br>Turn the motor on then turn it off again after it reaches the specified {distance} in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M].</BR> AFFECTED BY:  setAcceleration(), setMaxSpeedForDistance(), holdAtStop()
| PUB driveAtPower(power) | Control the speed and direction of this motor using the {power, [(-100) to 100]} input.</br>Turns the motor on at {power}.</br>AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits) | Stops the motor after it reaches {rotationCount} of {rotationUnits} [DRU\_DEGREES, DRU\_ROTATIONS, or DRU\_HALL_TICKS].</BR>USE WITH:  driveDirection(), drive()
| PUB stopAfterDistance(distance, distanceUnits) | Stops the motor after it reaches {distance} specified in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M].</br>USE WITH:  driveDirection(), drive()
| PUB stopAfterTime(time, timeUnits) | Stops the motor, after {time} specified in {timeUnits} [DTU\_IN\_MILLISEC or DTU\_IN\_SEC] has elapsed.</br>USE WITH:  driveDirection(), drive()
| PUB stopMotor() | Stops the motor, killing any motion that was still in progress</BR> AFFECTED BY:holdAtStop()
| PUB emergencyCutoff() | EMERGENCY-Stop - Immediately stop motor, killing any motion that was still in progress (floats the drive pins)
| PUB clearEmergency() | clear EMERGENCY-Stop - allow the motors to be controlled again 
|  **>--- CONFIG**
| PUB start(eMotorBasePin, eMotorVoltage) | Specify motor control board connect location for this motor
| PUB stop() | stop cog and release pins assigned to this motor
| PUB setAcceleration(rate) | **NOT WORKING, YET** <BR>Limit Acceleration to {rate} where {rate} is [??? - ???] mm/s squared (default is ??? mm/s squared)
| PUB setMaxSpeed(speed) | Limit top-speed to {speed} where {speed} is  [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setMaxSpeedForDistance(speed) | Limit top-speed of driveDistance() operations to {speed} where {speed} is  [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB calibrate() | **NOT WORKING, YET** <BR>*(we may need this?)*
| PUB holdAtStop(bEnable)| Informs the motor control cog to actively hold postiion (bEnable=true) or coast (bEnable=false) at end of motion 
| PUB resetTracking()| Resets the position tracking values returned by getDistance() and getRotations()
|  **>--- STATUS**
| PUB getDistance(distanceUnits) : distanceInUnits | Returns the distance in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M] travelled by this motor since last reset
| PUB getRotationCount(rotationUnits) : rotationCount | Returns accumulated {rotationCount} in {rotationUnits} [DRU\_DEGREES, DRU\_ROTATIONS, or DRU\_HALL_TICKS], since last reset, for this motor.
| PUB getStatus() : eStatus | Returns status of motor drive state for this motor: enumerated constant: DS\_MOVING, DS\_HOLDING, DS\_OFF, or DS_Unknown
| PUB getMaxSpeed() : maxSpeed | Returns the last specified {maxSpeed}
| PUB getMaxSpeedForDistance() : maxSpeed4dist | Returns the last specified {maxSpeedForDistance}
| PUB getRawHallTicks() : rawTickCount | Return the raw driver-maintained tick count<BR>See: getDistance() for ticks accumulated since last reset
| PUB isReady() : bState | Return T/F where T means the motor COG is running
| PUB isStopped() : bState |  Return T/F where T means the motor is stopped
| PUB isStarting() : bState | Return T/F where T means the motor is spinning up
| PUB isEmergency() : bState | Return T/F where T means the motor is emergency-stopped

**NOTE1** {power} whenever used is [(-100) - 100] where neg. values drive backwards, pos. values forward, 0 is hold/stop

**NOTE2** {direction} whenever used is [(-100) - 100] A value of 0 (zero) will make your robot vehicle drive straight. A positive number (greater than zero) will make the robot turn to the right, and a negative number will make the robot turn to the left. The farther the steering value is from zero, the tighter the turn will be.

**NOTE3** A HALL TICK is 4° for our 6.5" Dia. Motors.

**NOTE4** {eMotorBasePin} is one of: PINS\_P0\_P15, PINS\_P16\_P31, or PINS\_P32\_P47

**NOTE5** {eMotorVoltage} is one of: PWR\_7p4V, PWR\_11p1V, PWR\_12V, PWR\_14p8V, PWR\_18p5V, or PWR\_22p2V

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

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg


