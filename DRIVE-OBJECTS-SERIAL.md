
# P2-BLDC-Motor-Control - Serial Interface of Steering Object

Serial interface for our steering object - P2 Spin2/Pasm2 for our 6.5" Hub Motors with Universal Motor Driver Boards

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

This document describes the serial interface of the steering object (**isp\_steering_2wheel.spin2**), which controls a dual motor robot platform. The serial top-level object, **isp\_steering\_serial.spin2**, receives these commands from your host (RPi, Arduino, etc.) and calls the steering object for you.

How the drive objects fit together, and how many cogs they use, is described once in [Drive Objects: Objects and cogs](DRIVE-OBJECTS.md#objects-and-cogs). The serial top-level adds its own serial receiver on top of that.

## Object: isp\_steering_2wheel.spin2

What the steering object does, and how its turning works, is described in [Drive Objects: the 2-Wheel Steering Object](DRIVE-OBJECTS.md#object-isp_steering_2wheelspin2). This page gives its serial form.

### Commands and replies

Each command is one line of text. With each public method below we've added its serial command and the reply. In this example:

```
SER drivedir {pwr} {dir}
SER Returns: OK | ERROR {errormsg}
```

... the first line is the command sent from the connected device to the P2, and the second is what the P2 sends back.

Generally speaking when driving a robot using these serial commands one expects to see:

```
commandA
OK
commandB
OK
```

**An ERROR reply comes in one of two forms:**

- **The value you sent was out of range**, so the command was never tried. The message names the value and its range, for example `ERROR Power (120) out of range [-100, 100]`.
- **The drive refused the command.** The message names the command, the drive's error and its code, for example `ERROR drivepwr failed: ERR_EMERGENCY_STOPPED (-1016)`. The codes are listed in [Drive Objects: Errors](DRIVE-OBJECTS.md#errors).

An `OK` means the drive accepted the command. The non-OK responses help detect problems early in the development of your control routines; once your drive code is working you should see them only for out-of-range values, an emergency stop, or a protective stop.

### Values sent as numbers

Units and status travel as the numbers of their enums:

| Kind | Values |
| --- | --- |
| {d-u} distance units | 1 DDU\_MM, 2 DDU\_CM, 3 DDU\_IN, 4 DDU\_FT, 5 DDU\_M, 6 DDU\_KM, 7 DDU\_MI |
| {r-u} rotation units | 1 DRU\_HALL\_TICKS, 2 DRU\_DEGREES, 3 DRU\_ROTATIONS |
| {t-u} time units | 1 DTU\_MILLISEC, 2 DTU\_SEC |
| status (`stat` reply) | 10 DS\_Unknown, 11 DS\_MOVING, 12 DS\_HOLDING, 13 DS\_OFF, 14 DS\_FAULTED, 15 DS\_ESTOP |
| hold {true \| false} | -1 true (hold), 0 false (coast) |

### The 2-Wheel Steering Object PUBLIC Interface

| Steering Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveDirection(power, direction)</PRE><BR><PRE>SER drivedir {pwr} {dir}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Control the speed and direction of your robot using the {power} and {direction} inputs.</br>Turns both motors on at {power, [(-100) to 100]} but adjusted by {direction, [(-100) to 100]}.</br> AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| <PRE>PUB driveForDistance(leftDistance, rightDistance, distanceUnits)</PRE><BR><PRE>SER drivedist {ltdist} {rtdist} {d-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Drive both wheels forward until each has travelled its own distance: equal distances drive straight, unequal ones turn toward the shorter side. Each wheel comes to rest at its own distance.</BR> AFFECTED BY:  setAcceleration(), setMaxSpeedForDistance(), setMaxSpeed(), holdAtStop()
| PUB driveAtPower(leftPower, rightPower)<BR><PRE>SER drivepwr {ltpwr} {rtpwr}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br>Turns left motor on at {leftPower} and right on at {rightPower}. Where {\*Power} are in the range [(-100) to 100].</br>AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits)<BR><PRE>SER stopaftrot {count} {r-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors so they are at rest when either motor reaches {rotationCount} of {rotationUnits}.</BR>USE WITH:  driveDirection(), driveAtPower()
| PUB stopAfterDistance(distance, distanceUnits)<BR><PRE>SER stopaftdist {dist} {d-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors so they are at rest when either motor reaches {distance} in {distanceUnits}.</br>USE WITH:  driveDirection(), driveAtPower()
| PUB stopAfterTime(time, timeUnits)<BR><PRE>SER stopafttime {time} {t-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors so they are at rest when {time} in {timeUnits} has elapsed.</br>USE WITH:  driveDirection(), driveAtPower()
| PUB stopMotors()<BR><PRE>SER stopmotors<br>SER Returns: OK</PRE> | Stops both motors, killing any motion that was still in progress</BR> AFFECTED BY: holdAtStop()
| PUB emergencyCutoff()<BR><PRE>SER emercutoff<br>SER Returns: OK</PRE> | EMERGENCY-Stop - Immediately stop both motors, killing any motion that was still in progress. Drives are refused until `emerclear`.
| PUB clearEmergency()<BR><PRE>SER emerclear<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Clear the emergency stop, allowing the motors to be controlled again
|  **>--- CONFIG**
| PUB start(leftBasePin, rightBasePin, driveVoltage, leftDetectMode, rightDetectMode)<BR><PRE>SER N/A</PRE> | Called by the serial top-level from your user configuration
| PUB stop() <BR><PRE>SER N/A</PRE>| Stop cogs and release pins assigned to motor drivers
| PUB setAcceleration(rate)<BR><PRE>SER setaccel {rate}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Set how fast both wheels speed up, in mm/s² at the wheel rim [1 to 10,000]. Slowing down and stopping keep their own fixed rate.
| PUB setMaxSpeed(speed)<BR><PRE>SER setspeed {speed}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Limit top-speed to {speed} where {speed} is  [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setMaxSpeedForDistance(speed)<BR><PRE>SER setspeedfordist {speed}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Limit top-speed of driveForDistance() operations to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setCommandTimeout(nMs)<BR><PRE>SER settimeout {ms}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | A link-loss guard, off by default. While it is on, a platform driven by `drivedir` or `drivepwr` must be sent a drive command at least every {ms} [10 to 60,000]; when one does not arrive in time both motors stop. `settimeout 0` turns it off. It is the host's choice: the serial top-level never turns it on by itself.
| PUB calibrate() <BR><PRE>SER N/A</PRE> | **NOT WORKING, YET** <BR>*(we may need this?)*
| PUB holdAtStop(bEnable)<BR><PRE>SER hold {true \| false}<br>SER Returns: OK \| ERROR {errormsg}</PRE>| Once at rest, actively hold position (true) or coast (false)
| PUB resetTracking()<BR><PRE>SER resettracking<br>SER Returns: OK \| ERROR {errormsg}</PRE>| Resets the position tracking values returned by getDistance() and getRotationCount()
|  **>--- STATUS**
| PUB getDistance(distanceUnits) : leftDistanceInUnits, rightDistanceInUnits<BR><PRE>SER getdist {d-u}<br>SER Returns: dist {ltDistInUnits} {rtDistInUnits} \| ERROR {errormsg}</PRE> | Returns the distance in {distanceUnits} travelled by each motor since last reset
| PUB getRotationCount(rotationUnits) : leftRotationCount, rightRotationCount <BR><PRE>SER getrot {r-u}<br>SER Returns: rot {ltRotCountInUnits} {rtRotCountInUnits} \| ERROR {errormsg}</PRE>| Returns accumulated rotation in {rotationUnits}, since last reset, for each of the motors.
| PUB getPower() : leftPower, rightPower <BR><PRE>SER getpwr<br>SER Returns: pwr {ltPwr} {rtPwr}</PRE>| Returns the last commanded power value for each of the motors (zero once the motor is stopped)
| PUB getStatus() : eLeftStatus, eRightStatus<BR><PRE>SER getstatus<br>SER Returns: stat {ltStatus} {rtStatus}</PRE> | Returns each motor's drive status as a number (see the table above). **DS\_FAULTED (14)**: the motor has faulted, and clears when a stop or a new power is commanded. **DS\_ESTOP (15)**: the motor is emergency-stopped until `emerclear`.
| PUB getDriveVoltage() : eVoltage, nMilliVolts <BR><PRE>SER getvoltage<br>SER Returns: volt {pwrEnum} {milliVolts}</PRE>| Returns the configured drive voltage, as its PWR\_\* number and its nominal value in mV. This is the configured value, not a measurement.
| PUB getMaxSpeed() : maxSpeed <BR><PRE>SER getmaxspd<br>SER Returns: speedmax {maxSpeed}</PRE>| Returns the last specified {maxSpeed}
| PUB getMaxSpeedForDistance() : maxSpeed4dist <BR><PRE>SER getmaxspdfordist<br>SER Returns: speeddistmax {maxSpeed}</PRE>| Returns the last specified {maxSpeedForDistance}

**NOTE1** {power} whenever used is [(-100) - 100] where neg. values drive backwards, pos. values forward, 0 is hold/stop

**NOTE2** {direction} whenever used is [(-100) - 100] A value of 0 (zero) will make your robot vehicle drive straight. A positive number (greater than zero) will make the robot turn to the right, and a negative number will make the robot turn to the left. The farther the steering value is from zero, the tighter the turn will be.

**NOTE3** A HALL TICK is 4° for our 6.5" Dia. Motors.

The pin groups and drive voltage are set in your user configuration, not over serial: see [DEVELOP.md](DEVELOP.md).

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


