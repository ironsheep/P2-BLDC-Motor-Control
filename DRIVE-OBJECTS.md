
# P2-BLDC-Motor-Control - Drive Objects

Single and Two-motor driver objects P2 Spin2/Pasm2 for our 6.5" Hub Motors with Universal Motor Driver Board

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

There are two objects in our motor control system. There is a lower-level object (**isp\_bldc_motor.spin2**) that controls a single motor and there's an upper-level object (**isp\_steering_2wheel.spin2**) which coordinates a pair of motors as a drive subsystem.

If you are working with a dual motor device then you'll be coding to the interface of this upper-level object as you develop your drive algorithms.  If you were to work with say a three-wheeled device then you may want to create a steering object that can better coordinate all three motors at the same time. (*And, if you do please consider contributing it to this project so it can be available to us all!*)

On this page:

- [Objects and cogs](#objects-and-cogs) - how many cogs the drive uses, and how your calls reach it
- [The 2-Wheel Steering Object](#object-isp_steering_2wheelspin2) - public interface
- [The Motor Object](#object-isp_bldc_motorspin2) - public interface
- [Errors](#errors) - what every method returns, and how to find out why a call was refused
- [Protection and limits](#protection-and-limits) - what the drive does on its own to protect the motor, the board and your path
- [How far the motor travels while stopping](#how-far-the-motor-travels-while-stopping)

## Objects and cogs

**The drive uses a fixed number of cogs:**

| You use | Cogs the drive uses | What they are |
| --- | --- | --- |
| `isp_bldc_motor.spin2` (one motor) | **2** | the motor's driver cog, and one front cog |
| `isp_steering_2wheel.spin2` (two motors) | **3** | one driver cog per motor, and one front cog that serves both |

`start()` launches all of them. Nothing else needs starting.

**The driver cog** commutates the motor and generates its PWM. **The front cog** runs once a millisecond: it tracks wheel position, enforces the stop limits (`stopAfterDistance()` and the rest), applies the protections described below, and is the only thing that ever commands the driver.

Conceptually, the drive system is always running. Your calls do not drive the motor directly: a command method checks its arguments on your cog, hands the request to the front cog, and waits, briefly and with a bound, for the front cog to accept it. It then returns a status, which you may check or ignore (see [Errors](#errors)). Status methods read the drive's current values directly and return at once.

The objects themselves do not run in a cog of their own: their methods run in whichever cog calls them.

## Object: isp\_steering_2wheel.spin2

This steering object makes it easy to make your robot drive forward, backward, turn, or stop. You can adjust the steering to make your robot go straight, drive in arcs, or make tight turns. This steering object is for robot vehicles that have two motors, with one motor driving the left side of the vehicle and the other the right side.

### Provide steering-direction and power-for-both-wheels

The steering object controls both motors at the same time, to drive your vehicle in the direction that you choose. Steering-direction is used to re-interpet the power value that is actually sent to each wheel.

### Alternatively: Provide power for each wheel seperately

The steering object also provides an alternative form of control where you can make the two motors go at different speeds or in different directions to make your robot turn in more precise ways.

### Turning Concepts

When you think of turning your robot vehicle you think of turning about some point relative to the robot position (e.g., spin about its center point, spin about one of the wheels, or even make some large arcing turn.) All of these turns can be thought of within a singular concept. If you draw a radial line from the center point of your robot vehicle out thru the center point of the slowest wheel, continuing out beyond your robot... all possible turns that your robot vehicle can make have their center-point somewhere on this line!  By adjusting the power of each wheel and the direction of each wheel you are specifying where the center-point of your turn will be on this line.  Fun, right?

- If you drive one wheel backward and one wheel forward but at the same velocity this spins the robot vehicle about its center-point, one end of our line.

- Ignoring friction issues for this discussion, if you stop one wheel and power the other your robot vehicle is now spinning about the center-point of the stopped wheel, another point on our line.

- Now instead of stopping the wheel just drive it at a slower speed than the other but in the opposite direction. Now our center-point of the spin has moved yet again but this time it moved from over the slower wheel to instead between the slower wheel and the center point of the robot vehicle.

- Lastly, let's instead drive this slow wheel in the same direction as the faster wheel but keep the speed slower. This time the robot vehicle is now moving in a large arc as the center-point of our turn has now moved on our line beyond the exterior of our robot, out past the slower wheel.

### The 2-Wheel Steering Object PUBLIC Interface

The object **isp\_steering_2wheel.spin2** provides the following methods. Every method listed as returning `eError` returns `NO_ERROR` (0) or a negative `ERR_*` code; see [Errors](#errors).

| Steering Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveDirection(power, direction) : eError</PRE> | Control the speed and direction of your robot using the {power} and {direction} inputs.</br>Turns both motors on at {power, [(-100) to 100]} but adjusted by {direction, [(-100) to 100]}. A positive {direction} turns right and a negative one left, by slowing the wheel on that side; at 100 that wheel stops.</br> AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| <PRE>PUB driveForDistance(leftDistance, rightDistance, distanceUnits) : eError</PRE> | Drive both wheels forward until each has travelled its own distance: equal distances drive straight, unequal ones turn toward the shorter side.</br>Each wheel runs at a power in proportion to its distance, the longer one at setMaxSpeedForDistance() (never above setMaxSpeed()), so both finish at about the same time, and each comes to rest at its own distance (within about two hall ticks). {\*distance} is in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI].</BR> AFFECTED BY:  setAcceleration(), setMaxSpeedForDistance(), setMaxSpeed(), holdAtStop()
| PUB driveAtPower(leftPower, rightPower) : eError | Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br>Turns left motor on at {leftPower} and right on at {rightPower}. Where {\*Power} are in the range [(-100) to 100].</br>AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits) : eError | Stops both motors so they are at rest when either motor reaches {rotationCount} of {rotationUnits} [DRU\_HALL\_TICKS, DRU\_DEGREES or DRU\_ROTATIONS].</BR>The stop begins early, by the distance each wheel needs to slow down, so the platform comes to rest at the limit (within about two hall ticks), not past it.</BR>USE WITH:  driveDirection(), driveAtPower()
| PUB stopAfterDistance(distance, distanceUnits) : eError | Stops both motors so they are at rest when either motor reaches {distance} specified in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI].</BR>The stop begins early, as for stopAfterRotation().</br>USE WITH:  driveDirection(), driveAtPower()
| PUB stopAfterTime(time, timeUnits) : eError | Stops both motors so they are at rest when {time} specified in {timeUnits} [DTU\_MILLISEC or DTU\_SEC] has elapsed (within a few milliseconds).</br>USE WITH:  driveDirection(), driveAtPower()
| PUB stopMotors() : eError | Stops both motors, killing any motion that was still in progress. The stop follows the drive's ramp down.</BR> AFFECTED BY: holdAtStop()
| PUB emergencyCutoff() : eError | EMERGENCY-Stop - Immediately stop both motors, killing any motion that was still in progress. The emergency stop latches: drives are refused with ERR\_EMERGENCY\_STOPPED until clearEmergency(). **By design this is a hard stop**: both wheels short their phases at once, giving up the gentle deceleration every other stop uses. From speed that can draw tens of amps per wheel and stop the platform abruptly, which can tip a tall robot. Use stopMotors() when a controlled stop will do.
| PUB clearEmergency() : eError | Clear the emergency stop, allowing the motors to be driven again. Both motors stay stopped until commanded.
| PUB clearProtectiveStop() : eError | Acknowledge a protective stop (see [Protection and limits](#protection-and-limits)). Both motors stay stopped and may be driven again.
|  **>--- CONFIG**
| PUB start(leftBasePin, rightBasePin, driveVoltage, leftDetectMode, rightDetectMode) : ok | Start both motors' drivers and the front cog that serves them (3 cogs), for the boards at {leftBasePin} and {rightBasePin} [PINS\_\*], at {driveVoltage} [PWR\_\*], each board detected per its {\*DetectMode} [BRD\_AUTO\_DET, BRD\_REV\_A or BRD\_REV\_B].</br>Returns the front cog's id, or -1 when either motor or the front cog failed to start; getError() then names the cause and the wheel. A wheel whose board is not detected is refused (ERR\_BOARD\_NOT\_DETECTED) unless its detect mode forces BRD\_REV\_A or BRD\_REV\_B. Blocks for about 1 s on success while it calibrates both current sensors.
| PUB stop() : eError | Stop the front cog and both drive cogs, and release the motor pins
| PUB setAcceleration(rate) : eError | Set how fast both wheels speed up: every speed-up from now on ramps at a constant {rate} in mm/s² at the wheel rim, [ACCEL\_MIN\_MM\_S2 to ACCEL\_MAX\_MM\_S2] (1 to 10,000). Slowing down and stopping keep their own fixed rate, so stopping distances do not change. Until this is called the drive uses a gentle built-in ramp (see the motor object).
| PUB setMaxSpeed(speed) : eError | Limit top-speed to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*. It caps what you command; under load a motor may run slower than a capped command, and then holds the fastest speed it can sustain.
| PUB setMaxSpeedForDistance(speed) : eError | Limit top-speed of driveForDistance() operations to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setCommandTimeout(nMs) : eError | A link-loss guard, off by default. While it is on, a platform driven by driveDirection() or driveAtPower() must be sent a drive command (repeating the same one is enough) at least every {nMs} [CMD\_TIMEOUT\_MIN\_MS to CMD\_TIMEOUT\_MAX\_MS] (10 to 60,000 ms). When one does not arrive in time both motors stop, as stopMotors() stops them, and getError() reports ERR\_COMMAND\_TIMEOUT once on every cog that calls it. driveForDistance() is a bounded move and is not watched. CMD\_TIMEOUT\_OFF (0) turns it off; start() turns it off.
| PUB calibrate() : eError | **NOT WORKING, YET** <BR>*(we may need this?)*
| PUB holdAtStop(bEnable) : eError | Once at rest, actively hold position (bEnable=true) or coast (bEnable=false). Every stop from speed follows the drive's ramp down either way; this only chooses what happens at rest. Coast turns all the bridge transistors off. The hold keeps each wheel where it stopped and uses only the effort the load needs: the further a slope or a push moves the wheel, the harder it holds, up to a ceiling. If the load moves a wheel past the hold, or the hold stays at its ceiling too long, that wheel's motor phases are shorted instead. The short gives a drag that grows with speed but cannot hold a wheel still. getHoldStatus() reports which.
| PUB resetTracking() : eError | Resets the position tracking values returned by getDistance() and getRotationCount(): the current position becomes home.
|  **>--- STATUS**
| PUB getError() : eError, eLeftError, eRightError | Return and clear this cog's first recorded errors: the steering object's own, then each wheel's. NO\_ERROR where there is none. See [Errors](#errors).
| PUB getDistance(distanceUnits) : leftDistanceInUnits, rightDistanceInUnits | Returns the distance in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI] travelled by each motor since last reset
| PUB getRotationCount(rotationUnits) : leftRotationCount, rightRotationCount | Returns accumulated {\*RotationCount} in {rotationUnits} [DRU\_HALL\_TICKS, DRU\_DEGREES or DRU\_ROTATIONS], since last reset, for each of the motors.
| PUB getPower() : leftPower, rightPower | Returns the last commanded power value for each of the motors, [-100 to 100] (zero once the motor is stopped). This is what you commanded, not what the motor achieved.
| PUB getCurrent() : nLtAmps, nLtWatts, nRtAmps, nRtWatts | Returns each motor's current, in units of 0.1 mA (amps × 10,000), and its power draw in mW, calculated against the configured drive voltage.
| PUB getDriveVoltage() : eVoltage, nMilliVolts | Returns the PWR\_\* value both motors were started for, and its nominal voltage in mV (e.g. 18,500 for PWR\_18p5V). This is the configured value, not a measurement.
| PUB getStatus() : eLeftStatus, eRightStatus | Returns status of motor drive state for each motor: enumerated constant: DS\_MOVING, DS\_HOLDING, DS\_OFF, DS\_FAULTED, DS\_ESTOP, or DS\_Unknown
| PUB getFaultCause() : eLeftCause, eRightCause | Returns why each wheel's most recent fault since start() happened: FC\_LAG (the rotor could not follow the field: an overload, a stall, or a wrong commutation offset), FC\_HALL (a hall sensor read an illegal code: dead, unpowered or disconnected), or FC\_NONE. It stays readable after the fault itself clears.
| PUB getHealth() : nLeftChecked, nLeftFailed, nRightChecked, nRightFailed | Returns what start() checked on each wheel with the platform at rest, and which checks failed, as HLT\_\* bits. HLT\_HALLS covers the hall sensors, HLT\_SENSE\_ZERO the current sense, and HLT\_PHASE\_U, HLT\_PHASE\_V and HLT\_PHASE\_W each motor lead (connected and drivable). An open lead fails its own bit, and a missing motor fails all three. Nothing moves during these checks, and a wheel that fails one still starts: what to do about it is your program's choice. HLT\_WIRING is added once checkWiring() has run.
| PUB getPackVoltage() : ePackStatus, nMilliVolts | Returns the battery pack's voltage in mV from the optional pack voltage sensor (VOLTAGE-SENSOR.md), averaged over about 64 ms. The status is PACK\_PRESENT, PACK\_ABSENT (the sensor is fitted but reads no pack: unplugged, or a broken lead), or PACK\_NOT\_FITTED. The voltage is 0 unless PACK\_PRESENT.
| PUB checkWiring() : eError | **Moves the robot.** Turns the platform a few degrees in place and back, each wheel one electrical cycle each way (about 3.5 cm at the tyre). This proves each wheel's hall and phase wiring: a swapped hall pair, swapped phase leads, a dead hall line or a wheel that does not turn all fail it. The verdict is recorded as that wheel's HLT\_WIRING. A wheel whose leg draws more current than a healthy walk ever does (miswiring stalls it against the field) is stopped at once by shorting its phases, and fails. It blocks about half a second, leaves both wheels at rest per holdAtStop(), and resets the position tracking. It returns NO\_ERROR once the walk has run, pass or fail (read the verdict from getHealth()), or the error that kept it from running.
| PUB getHoldStatus() : eLeftState, nLeftDisplacement, eRightState, nRightDisplacement | Returns what each wheel's hold at rest is doing (holdAtStop(true)): HS\_HOLDING while holding, HS\_SLIPPED (the load moved the wheel past the hold) or HS\_LIMITED (it held at its ceiling too long) once that wheel has switched to the phase short, or HS\_OFF when not holding. Each displacement is how far, in hall ticks, the load has moved that wheel from where it stopped. A switched wheel stays shorted until the next command.
| PUB getProtectiveStop() : eLeftCode, eRightCode | Returns each wheel's latched protective-stop cause (ERR\_PLATFORM\_BLOCKED), or NO\_ERROR when none, without clearing it. A cause on either wheel stops both.
| PUB getHallIntegrityCounts() : nLtMissed, nLtIllegal, nRtMissed, nRtIllegal | Returns, per motor since start, the times a hall transition was skipped and the times the hall sensors read an illegal code (%000 or %111)
| PUB getHallIllegalCodes() : nLtAllLow, nLtAllHigh, nRtAllLow, nRtAllHigh | Returns each motor's illegal hall codes split by kind: all three lines low (%000, a sensor without power) and all three high (%111, a line stuck or floating high)
| PUB getMaxSpeed() : maxSpeed | Returns the last specified {maxSpeed}
| PUB getMaxSpeedForDistance() : maxSpeed4dist | Returns the last specified {maxSpeedForDistance}
| PUB isReady() : bState | Return T/F where T means both motors' driver cogs are running
| PUB isStopped() : bState | Return T/F where T means both motors are stopped
| PUB isStarting() : bState | Return T/F where T means either motor is spinning up
| PUB isTurning() : bState | Return T/F where T means either motor is commanded to move and is not stopped, faulted or emergency-stopped. A motor that stalls is stopped by the protective stop within about a second.
| PUB isFaulted() : bState | Return T/F where T means either motor has faulted (the fault clears only when a stop or a power is commanded)
| PUB isEmergency() : bState | Return T/F where T means either motor is emergency-stopped
|  **>--- VALIDATION**
| PUB validBasePinForChoice(userBasePin) : legalBasePin | Returns {userBasePin} when it is a legal PINS\_\* group, else INVALID\_PIN\_BASE
| PUB validVoltageForChoice(userVoltage) : legalVoltage | Returns {userVoltage} when the configured motor supports it, else INVALID\_VOLTAGE
| PUB validMotorForChoice(userMotor) : legalMotor | Returns {userMotor} when it names a supported motor, else INVALID\_MOTOR
| PUB validDetectModeForChoice(userDetMode) : legalMode | Returns {userDetMode} when it is a BRD\_\* value, else INVALID\_DET\_MODE

**NOTE1** {power} whenever used is [(-100) - 100] where neg. values drive backwards, pos. values forward, 0 is hold/stop. Power is a commanded speed: 100 is the motor's top speed at your drive voltage (see [MOTOR_CHOICE.md](MOTOR_CHOICE.md)). Unloaded the motor meets it across the range; the upper part of the range has less torque in reserve, so under load a motor may fall short.

**NOTE2** {direction} whenever used is [(-100) - 100] A value of 0 (zero) will make your robot vehicle drive straight. A positive number (greater than zero) will make the robot turn to the right, and a negative number will make the robot turn to the left. The farther the steering value is from zero, the tighter the turn will be.

**NOTE3** A HALL TICK is 4° for our 6.5" Dia. Motors.

**NOTE4** {e\*MotorBasePin} is one of: PINS\_P0\_P15, PINS\_P8\_P23, PINS\_P16\_P31, PINS\_P32\_P47 or PINS\_P40\_P55

**NOTE5** {eMotorVoltage} is one of: PWR\_6p0V, PWR\_7p4V, PWR\_11p1V, PWR\_12p0V, PWR\_14p8V, PWR\_18p5V, PWR\_22p2V or PWR\_24p0V. The DocoEng motor does not support PWR\_6p0V. See [MOTOR_CHOICE.md](MOTOR_CHOICE.md) for what each gives you.

## Object: isp\_bldc_motor.spin2

The BLDC motor object controls a single BLDC Motor. You can turn a motor on or off, control its power level, or turn the motor on for a specified amount of time or rotation.

### The Motor Object PUBLIC Interface

The object **isp\_bldc_motor.spin2** provides the following methods. Every method listed as returning `eError` returns `NO_ERROR` (0) or a negative `ERR_*` code; see [Errors](#errors).

| Single-motor Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveForDistance(distance, distanceUnits) : eError</PRE> | Turn the motor on, and bring it to rest after it travels {distance} in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI].</BR> AFFECTED BY:  setAcceleration(), setMaxSpeedForDistance(), holdAtStop()
| PUB driveAtPower(power) : eError | Control the speed and direction of this motor using the {power, [(-100) to 100]} input.</br>Turns the motor on at {power}. A faulted motor is cleared first, automatically.</br>AFFECTED BY:  setAcceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits) : eError | Stops the motor so it is at rest at {rotationCount} of {rotationUnits} [DRU\_HALL\_TICKS, DRU\_DEGREES or DRU\_ROTATIONS] (within about two hall ticks). The stop begins early, by the distance the motor needs to slow down.</BR>USE WITH:  driveAtPower()
| PUB stopAfterDistance(distance, distanceUnits) : eError | Stops the motor so it is at rest at {distance} specified in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI]. The stop begins early, as for stopAfterRotation().</br>USE WITH:  driveAtPower()
| PUB stopAfterTime(time, timeUnits) : eError | Stops the motor so it is at rest when {time} specified in {timeUnits} [DTU\_MILLISEC or DTU\_SEC] has elapsed (within a few milliseconds).</br>USE WITH:  driveAtPower()
| PUB stopMotor() : eError | Stops the motor, killing any motion that was still in progress. The stop follows the drive's ramp down.</BR> AFFECTED BY: holdAtStop()
| PUB emergencyCutoff() : eError | EMERGENCY-Stop - Immediately stop the motor, killing any motion that was still in progress. It brakes by shorting the motor phases, whatever holdAtStop() selects, and latches: drives are refused with ERR\_EMERGENCY\_STOPPED until clearEmergency(). **By design this is a hard stop**, giving up the gentle deceleration every other stop uses. From speed the short can draw tens of amps and stop the wheel abruptly, which can tip a tall robot. Use stopMotor() when a controlled stop will do.
| PUB clearEmergency() : eError | Clear the emergency stop. The motor stays stopped and may be driven again.
| PUB clearProtectiveStop() : eError | Acknowledge a protective stop (see [Protection and limits](#protection-and-limits)). The motor stays stopped and may be driven again.
|  **>--- CONFIG**
| PUB start(eMotorBasePin, eMotorVoltage, eDetectionMode) : ok | Start this motor's driver and its front cog (2 cogs), for the board at {eMotorBasePin} [PINS\_\*], at {eMotorVoltage} [PWR\_\*], with the board detected per {eDetectionMode} [BRD\_AUTO\_DET, BRD\_REV\_A or BRD\_REV\_B].</br>Returns the driver's cog id, or -1 when it failed to start; getError() then holds the cause. A pin group where no board is detected is refused (ERR\_BOARD\_NOT\_DETECTED) unless you force BRD\_REV\_A or BRD\_REV\_B. Blocks for about 1 s on success while it calibrates the current sensor.
| PUB stop() : eError | Stop both cogs and release the pins assigned to this motor
| PUB setAcceleration(rate) : eError | Set how fast the motor speeds up: every speed-up from now on ramps at a constant {rate} in mm/s² at the wheel rim, [ACCEL\_MIN\_MM\_S2 to ACCEL\_MAX\_MM\_S2] (1 to 10,000). Until this is called the motor uses a gentle built-in ramp that starts near 44 mm/s² and grows by about 1,240 mm/s² every second (6.5" wheel). Slowing down and stopping keep their own fixed rate, so stopping distances do not change. The motor can still accelerate more slowly than asked: the drive never lets the field run further ahead of the rotor than the motor can follow.
| PUB setMaxSpeed(speed) : eError | Limit top-speed to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*. It caps what you command; under load the motor may run slower than a capped command, and then holds the fastest speed it can sustain.
| PUB setMaxSpeedForDistance(speed) : eError | Limit top-speed of driveForDistance() operations to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setCommandTimeout(nMs) : eError | A link-loss guard, off by default. While it is on, a motor driven by driveAtPower() must be sent a drive command (repeating the same power is enough) at least every {nMs} [CMD\_TIMEOUT\_MIN\_MS to CMD\_TIMEOUT\_MAX\_MS] (10 to 60,000 ms). When one does not arrive in time the motor stops, as stopMotor() stops it, and getError() reports ERR\_COMMAND\_TIMEOUT once on every cog that calls it. driveForDistance() is not watched. CMD\_TIMEOUT\_OFF (0) turns it off; start() turns it off.
| PUB calibrate() : eError | **NOT WORKING, YET** <BR>*(we may need this?)*
| PUB holdAtStop(bEnable) : eError | Once at rest, actively hold position (bEnable=true) or coast (bEnable=false). Every stop from speed follows the drive's ramp down either way. Coast turns all the bridge transistors off. The hold keeps the wheel where it stopped and uses only the effort the load needs, up to a ceiling. If the load moves the wheel past the hold, or the hold stays at its ceiling too long, the motor phases are shorted instead, and getHoldStatus() says which. After a fault the motor coasts (false) or brakes (true), since a faulted drive cannot hold a position.
| PUB resetTracking() : eError | Resets the position tracking values returned by getDistance() and getRotationCount()
| PUB forwardIsReverse() : eError | Reverse this motor's sense of forward, for a motor mounted facing the other way (the steering object does this for the right wheel)
|  **>--- STATUS**
| PUB getError() : eError | Return and clear this cog's first recorded error, NO\_ERROR when there is none. See [Errors](#errors).
| PUB getDistance(distanceUnits) : distanceInUnits | Returns the distance in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI] travelled by this motor since last reset
| PUB getRotationCount(rotationUnits) : rotationCount | Returns accumulated {rotationCount} in {rotationUnits} [DRU\_HALL\_TICKS, DRU\_DEGREES or DRU\_ROTATIONS], since last reset, for this motor.
| PUB getPower() : nPower | Returns the last commanded power [-100 to 100] (zero once the motor is stopped). This is what you commanded, not what the motor achieved.
| PUB getCurrent() : fAmps, fWatts | Returns the motor's current, in units of 0.1 mA (amps × 10,000), and its power draw in mW, calculated against the configured drive voltage
| PUB getDriveVoltage() : eVoltage, nMilliVolts | Returns the PWR\_\* value this motor was started for, and its nominal voltage in mV. This is the configured value, not a measurement.
| PUB getStatus() : eStatus | Returns status of motor drive state for this motor: enumerated constant: DS\_MOVING, DS\_HOLDING, DS\_OFF, DS\_FAULTED, DS\_ESTOP, or DS\_Unknown
| PUB getFaultCause() : eCause | Returns why the most recent fault since start() happened: FC\_LAG, FC\_HALL or FC\_NONE (see the steering object's getFaultCause()). It stays readable after the fault itself clears.
| PUB getHealth() : nChecked, nFailed | Returns what start() checked with the motor at rest, and which checks failed: HLT\_\* bits (see the steering object's getHealth()).
| PUB getPackVoltage() : ePackStatus, nMilliVolts | Returns the battery pack's voltage in mV from the optional pack voltage sensor: PACK\_PRESENT, PACK\_ABSENT or PACK\_NOT\_FITTED (see the steering object's getPackVoltage()).
| PUB checkWiring() : eError | **Moves the wheel** one electrical cycle forward and back to prove its hall and phase wiring, and records the verdict as HLT\_WIRING (see the steering object's checkWiring()).
| PUB getHoldStatus() : eHoldState, nDisplacement | Returns what the hold at rest is doing (holdAtStop(true)): HS\_HOLDING, HS\_SLIPPED, HS\_LIMITED or HS\_OFF, and how far the load has moved the wheel from where it stopped, in hall ticks (see the steering object's getHoldStatus()).
| PUB isFaultSignal() : bState | Return T/F where T means the motor has faulted since start() or since clearFaultSignal(); unlike isFaulted() it stays set after the fault clears
| PUB clearFaultSignal() : eError | Reset the record read by isFaultSignal()
| PUB getProtectiveStop() : eProtectiveCode | Returns the latched protective-stop cause (ERR\_PLATFORM\_BLOCKED), or NO\_ERROR when none, without clearing it
| PUB getHallIntegrityCounts() : nMissedTransitions, nIllegalCodes | Returns the times since start a hall transition was skipped, and the times the hall sensors read an illegal code (%000 or %111)
| PUB getHallIllegalCodes() : nAllLowCodes, nAllHighCodes | Returns the illegal hall codes split by kind: %000 (a sensor without power) and %111 (a line stuck or floating high)
| PUB getMaxSpeed() : maxSpeed | Returns the last specified {maxSpeed}
| PUB getMaxSpeedForDistance() : maxSpeed4dist | Returns the last specified {maxSpeedForDistance}
| PUB getRawHallTicks() : rawTickCount | Return the raw driver-maintained tick count<BR>See: getDistance() for ticks accumulated since last reset
| PUB getBoardType() : eBoardRev | Returns REV\_A or REV\_B for the board at this pin group, else REV\_Unknown
| PUB isReady() : bState | Return T/F where T means the motor's driver cog is running
| PUB isStopped() : bState |  Return T/F where T means the motor is stopped
| PUB isStarting() : bState | Return T/F where T means the motor is spinning up
| PUB isTurning() : bState | Return T/F where T means the motor is commanded to move and is not stopped, faulted or emergency-stopped. A motor that stalls is stopped by the protective stop within about a second.
| PUB isEmergency() : bState | Return T/F where T means the motor is emergency-stopped
| PUB isFaulted() : bState | Return T/F where T means the motor has faulted (the fault clears only when a stop or a power is commanded)
|  **>--- VALIDATION**
| PUB validBasePinForChoice(userBasePin) : legalBasePin | as the steering object's
| PUB validVoltageForChoice(userVoltage) : legalVoltage | as the steering object's
| PUB validMotorForChoice(userMotor) : legalMotor | as the steering object's
| PUB validDetectModeForChoice(userDetMode) : legalMode | as the steering object's
| PUB startSenseCog() : ok | Kept so 5.x programs still compile: it starts nothing, and returns the front cog's id that start() already launched (or -1 when the motor is not started)

The NOTES under the steering object's table apply here too.

## Errors

**Every command method returns a status**: `NO_ERROR` (0) when it did what it was asked, or one of the negative `ERR_*` codes below. You may check it or ignore it. A refused call changes nothing unless its description says otherwise.

**The first error is also kept for you.** Each command records its code, per calling cog, so you can issue several commands and ask once whether any of them failed: `getError()` returns the first code recorded on your cog since you last asked, and clears it. The steering object's `getError()` returns three results, its own first error, then the left wheel's and the right wheel's, so you can tell which wheel refused.

**`start()` returns a cog id, or -1.** On -1 the cause is in `getError()`.

**Status methods that cannot measure** return a documented neutral value, usually 0, and record the reason for `getError()`: for example `getDistance()` with `WHEEL_DIA_IN_INCH` set to 0 returns 0 and records `ERR_NO_WHEEL_DIA`.

Every code is below -1,000, so none can be mistaken for a cog id, a power, a distance or any other value these objects return. The steering object re-exports every one, so you can name them as `wheels.ERR_*`.

| Code | Value | Means |
| --- | --- | --- |
| NO\_ERROR | 0 | the call did what it was asked |
| ERR\_BAD\_PIN\_GROUP | -1001 | start(): the base pin is not a legal PINS\_\* group |
| ERR\_PIN\_GROUP\_IN\_USE | -1002 | start(): another motor already holds that pin group |
| ERR\_BAD\_VOLTAGE | -1003 | start(): the configured motor does not support that voltage |
| ERR\_BAD\_DETECT\_MODE | -1004 | start(): the detection mode is not a BRD\_\* value |
| ERR\_NO\_FREE\_COG | -1005 | start(): no cog was free |
| ERR\_ABI\_MISMATCH | -1006 | start(): the driver's internal layout is inconsistent; nothing was launched |
| ERR\_NOT\_STARTED | -1007 | the motor has not been started |
| ERR\_NO\_SENSE\_TASK | -1008 | no longer raised; kept so 5.x programs still compile |
| ERR\_BAD\_UNITS | -1009 | a units value outside its DDU\_\*, DRU\_\* or DTU\_\* list |
| ERR\_BAD\_COUNT | -1010 | a distance, rotation, time, rate or timeout outside its range (for example, less than 1) |
| ERR\_NO\_WHEEL\_DIA | -1011 | a distance request when `WHEEL_DIA_IN_INCH` is 0 |
| ERR\_LIMIT\_UNRESOLVABLE | -1012 | a stop limit shorter than one hall tick |
| ERR\_SYNC\_TIMEOUT | -1013 | a synchronized start the driver did not take in time; the motors are stopped |
| ERR\_BUSY | -1014 | test use only |
| ERR\_FAULT\_NOT\_CLEARED | -1015 | test use only |
| ERR\_EMERGENCY\_STOPPED | -1016 | a drive refused while emergency-stopped; call clearEmergency() |
| ERR\_NO\_RESPONSE | -1017 | the drive did not answer within its bound |
| ERR\_BOARD\_NOT\_DETECTED | -1018 | start(): no board was detected at the pin group and no revision was forced; getCurrent(): no current scale |
| ERR\_COMMAND\_TIMEOUT | -1019 | setCommandTimeout() is on and no drive command arrived in time: the motors were stopped |
| ERR\_PROTECTIVE\_STOP | -2000 | a protective stop is latched for a cause other than the named ones |
| ERR\_PLATFORM\_BLOCKED | -2001 | a protective stop is latched: a motor commanded to move did not turn for about a second |

## Protection and limits

The drive does these on its own. None of them needs a call to turn it on.

- **Current limiting.** The drive estimates each motor's phase current and folds back its output above **40 A**, and derates to **27 A** when the average stays high. These protect the driver board's transistors, not the motor, and they are not user settings.
- **A ramp the motor can follow.** Speeding up never lets the field run further ahead of the rotor than the motor can follow: if the rotor falls behind, the ramp waits for it. So a heavy load or a steep `setAcceleration()` slows the acceleration instead of faulting the motor.
- **Holding what it can sustain.** When a motor cannot reach its commanded speed, under load say, it holds the fastest speed it can sustain rather than winding the field ahead of the rotor.
- **Path-preserving speed limiting** (two wheels). When one wheel cannot keep up, one side loaded say, the steering object slows both wheels together, so the platform keeps the path you commanded instead of curving off it.
- **The protective stop.** A motor that is commanded to move but does not turn for about a second, its rotor held far behind the field with no hall transition, is stopped at once in the state you chose with `holdAtStop()`, and so is its partner on a two-wheel platform. With `holdAtStop(FALSE)` the wheel coasts; with `holdAtStop(TRUE)` its phases are shorted, since a blocked wheel cannot be held. (An emergency stop always shorts the phases.) It latches: every drive is refused with `ERR_PLATFORM_BLOCKED` until you call `clearProtectiveStop()`. `clearEmergency()` does not release it. Check `getProtectiveStop()` to see whether it has fired.
- **Faults.** If the rotor cannot follow the field at all, the drive faults. The motor then coasts or brakes as `holdAtStop()` selects, `getStatus()` reports `DS_FAULTED`, and `getFaultCause()` says why. The fault clears when you command a stop or a new power. On a two-wheel platform, a fault on one wheel also stops the other along its ramp down, as `stopMotors()` would, so the platform stops instead of pivoting about the faulted wheel.
- **The emergency stop** brakes the motor by shorting its phases and latches until `clearEmergency()`.

## How far the motor travels while stopping

A stop is not instant. The motor ramps down, and it keeps moving while it does. `stopAfterDistance()`, `stopAfterRotation()` and `stopAfterTime()` account for this themselves, by starting the stop early. You need this figure only when you stop the motor with `stopMotor()` or `stopMotors()` and must know how far it will go.

**The ramp down is a fixed deceleration**, so the distance grows with the **square** of the speed you stop from. For the 6.5" motor, measured on our hardware with the wheels off the ground:

| Stopping from | Hall ticks to come to rest | Approximate travel |
| --- | --- | --- |
| 196 ticks/s (about 131 RPM) | **75 ticks** (74–77 over repeated runs, both motors) | **≈ 432 mm** (17 in) |

To estimate another speed, scale by the square of the speed: stopping from twice the speed takes about four times the distance. From the top speed at 18.5 V (about 441 ticks/s, `power` 100) that is roughly 380 ticks, about 2.2 m.

- **Treat these figures as the most travel to expect, not a prediction.** With the platform on the floor, carrying weight, friction helps it stop and it comes to rest sooner.
- **The speed a given `power` produces depends on your drive voltage** (see [MOTOR_CHOICE.md](MOTOR_CHOICE.md)), so the same call stops in a shorter distance at a lower voltage. If you change `DRIVE_VOLTAGE`, re-check any clearance this was sizing.
- **`holdAtStop()` does not change it.** It only selects what happens once the motor is at rest.
- **`setRampingValues()` changes it**: its ramp-down step sets the deceleration.

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


