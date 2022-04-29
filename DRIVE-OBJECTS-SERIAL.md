
# P2-BLDC-Motor-Control - Serial Interface of Steering Object

Serial interface for our steering object - P2 Spin2/Pasm2 for our 6.5" Hub Motors with Universal Motor Driver Boards

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

There are two objects in our motor control system. There is a lower-level object (**isp\_bldc_motor.spin2**) that controls a single motor and there's an upper-level object (**isp\_steering_2wheel.spin2**) which coordinates a pair of motors as a drive subsystem.

This document describes the serial interface of the steering object which controls a dual motor robot platform.

The drive subsystem currently uses two cogs, one for each motor. A third cog privides motor position sense.  Conceptually, the drive system is always running. It is influenced by updating control variable values. When the values change the drive subsystem responds accordingly. The public methods of the steering object simply writes to these control variables and/or read from associated status variables of the sensor cog returning their current value or an interpretation thereof.

## Object: isp\_steering_2wheel.spin2

This steering object makes it easy to make your robot drive forward, backward, turn, or stop. You can adjust the steering to make your robot go straight, drive in arcs, or make tight turns. This steering object is for robot vehicles that have two motors, with one motor driving the left side of the vehicle and the other the right side. 


### The 2-Wheel Steering Object PUBLIC Interface

With each public method of this object we've added the serial command and response values. in this example:

```
SER drivedir {pwr} {dir}
SER Returns: OK | ERROR {errormsg}
```

... we see the first line represents the command to be sent from the connected device (RPi, Arduino, etc.) to the P2 via serial.  On the second line we see "Returns:" meaning that the P2 upon receiving the command will return the specified response.

Generally speaking when driving a robot using these serial commands one expects to see:

```
commandA
ok
commandB
ok
commandC
ok
```

... the non OK responses are there to help us detect problems early in the development of our control routines. We don't expect to be getting non-OK responses once we've developed our drive code. The exception to this would be if our drive code generates values which would be out of the range of legal values for a given command.


The object **isp\_steering_2wheel.spin2** provides the following methods:

| Steering Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveDirection(power, direction)</PRE><BR><PRE>SER drivedir {pwr} {dir}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Control the speed and direction of your robot using the {power} and {direction} inputs.</br>Turns both motors on at {power, [(-100) to 100]} but adjusted by {direction, [(-100) to 100]}.</br> AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| <PRE>PUB driveForDistance(leftDistance, rightDistance, distanceUnits)</PRE><BR><PRE>SER drivedist {ltdist} {rtdist} {d-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Control the forward direction or rate of turn of your robot using the {leftDistance} and {rightDistance} inputs.</br>Turn both motors on then turns them off again when either reaches the specified {leftDistance} or {rightDistance}, where {\*distance} is in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M].</BR> AFFECTED BY:  setAcceleration(), setMaxSpeedForDistance(), holdAtStop()
| PUB driveAtPower(leftPower, rightPower)<BR><PRE>SER drivepwr {ltpwr} {rtpwr}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br>Turns left motor on at {leftPower} and right on at {rightPower}. Where {\*Power} are in the range [(-100) to 100].</br>AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits)<BR><PRE>SER stopaftrot {count} {r-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors, after either of the motors reaches {rotationCount} of {rotationUnits} [DRU\_DEGREES, DRU\_ROTATIONS, or DRU\_HALL_TICKS].</BR>USE WITH:  driveDirection(), drive()
| PUB stopAfterDistance(distance, distanceUnits)<BR><PRE>SER stopaftdist {dist} {d-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors, after either of the motors reaches {distance} specified in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M].</br>USE WITH:  driveDirection(), drive()
| PUB stopAfterTime(time, timeUnits)<BR><PRE>SER stopafttime {time} {t-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors, after {time} specified in {timeUnits} [DTU\_IN\_MILLISEC or DTU\_IN\_SEC] has elapsed.</br>USE WITH:  driveDirection(), drive()
| PUB stopMotors()<BR><PRE>SER stopmotors<br>SER Returns: OK</PRE> | Stops both motors, killing any motion that was still in progress</BR> AFFECTED BY:holdAtStop()
| PUB emergencyCutoff()<BR><PRE>SER emercutoff<br>SER Returns: OK</PRE> | EMERGENCY-Stop - Immediately stop both motors, killing any motion that was still in progress
| PUB clearEmergency()<BR><PRE>SER emerclear<br>SER Returns: OK</PRE> | clear the emergency stop status allowing motors to be controlled again
|  **>--- CONFIG**
| PUB start(eLeftMotorBasePin, eRightMotorBasePin, eMotorVoltage)<BR><PRE>SER N/A</PRE> | Specify motor control board connect location for each of the left and right motor control boards
| PUB stop() <BR><PRE>SER N/A</PRE>| Stop cogs and release pins assigned to motor drivers
| PUB setAcceleration(rate)<BR><PRE>SER setaccel {rate}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | **NOT WORKING, YET** <BR>Limit Acceleration to {rate} where {rate} is [??? - ???] mm/s squared (default is ??? mm/s squared)
| PUB setMaxSpeed(speed)<BR><PRE>SER setspeed {speed}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Limit top-speed to {speed} where {speed} is  [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setMaxSpeedForDistance(speed)<BR><PRE>SER setspeedfordist {speed}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Limit top-speed of driveDistance() operations to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB calibrate() <BR><PRE>SER N/A</PRE> | **NOT WORKING, YET** <BR>*(we may need this?)*
| PUB holdAtStop(bEnable)<BR><PRE>SER hold {true \| false}<br>SER Returns: OK \| ERROR {errormsg}</PRE>| Informs the motor subsystem to actively hold postiion (bEnable=true) or coast (bEnable=false) at end of motion 
| PUB resetTracking()<BR><PRE>SER resettracking<br>SER Returns: OK</PRE>| Resets the position tracking values returned by getDistance() and getRotations()
|  **>--- STATUS**
| PUB getDistance(distanceUnits) : leftDistanceInUnits, rightDistanceInUnits<BR><PRE>SER getdist {d-u}<br>SER Returns: dist {ltDistInUnits} {rtDistInUnits} \| ERROR {errormsg}</PRE> | Returns the distance in {distanceUnits} [DDU\_IN, DDU\_CM, DDU\_FT or DDU\_M] travelled by each motor since last reset
| PUB getRotationCount(rotationUnits) : leftRotationCount, rightRotationCount <BR><PRE>SER getrot {r-u}<br>SER Returns: rot {ltRotCountInUnits} {rtRotCountInUnits} \| ERROR {errormsg}</PRE>| Returns accumulated {*RotationCount} in {rotationUnits} [DRU\_DEGREES, DRU\_ROTATIONS, or DRU\_HALL_TICKS], since last reset, for each of the motors.  
| PUB getPower() : leftPower, rightPower <BR><PRE>SER getpwr<br>SER Returns: pwr {ltPwr} {rtPwr}</PRE>| Returns the last specified power value for each of the motors (will be zero if the motor is stopped).
| PUB getStatus() : eLeftStatus, eRightStatus<BR><PRE>SER getstatus<br>SER Returns: stat {ltStatus} {rtStatus}</PRE> | Returns status of motor drive state for each motor: enumerated constant: DS\_MOVING, DS\_HOLDING, DS\_OFF, or DS_Unknown
| PUB getMaxSpeed() : maxSpeed <BR><PRE>SER getmaxspd<br>SER Returns: speedmax {maxSpeed}</PRE>| Returns the last specified {maxSpeed}
| PUB getMaxSpeedForDistance() : maxSpeed4dist <BR><PRE>SER getmaxspdfordist<br>SER Returns: speeddistmax {maxSpeed}</PRE>| Returns the last specified {maxSpeedForDistance}

**NOTE1** {power} whenever used is [(-100) - 100] where neg. values drive backwards, pos. values forward, 0 is hold/stop

**NOTE2** {direction} whenever used is [(-100) - 100] A value of 0 (zero) will make your robot vehicle drive straight. A positive number (greater than zero) will make the robot turn to the right, and a negative number will make the robot turn to the left. The farther the steering value is from zero, the tighter the turn will be.

**NOTE3** A HALL TICK is 4° for our 6.5" Dia. Motors.

**NOTE4** {e\*MotorBasePin} is one of: PINS\_P0\_P15, PINS\_P16\_P31, or PINS\_P32\_P47

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

Copyright © 2022 Iron Sheep Productions, LLC. All rights reserved.

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[marketplace-version]: https://vsmarketplacebadge.apphb.com/version-short/ironsheepproductionsllc.spin2.svg

[marketplace-installs]: https://vsmarketplacebadge.apphb.com/installs-short/ironsheepproductionsllc.spin2.svg

[marketplace-rating]: https://vsmarketplacebadge.apphb.com/rating-short/ironsheepproductionsllc.spin2.svg

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765
