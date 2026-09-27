
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
- [Settings start() keeps](#settings-start-keeps) - which settings you may make before start(), and which start() restores
- [Backing up a distance](#backing-up-a-distance) - driveForDistance() is forward only
- [Errors](#errors) - what every method returns, and how to find out why a call was refused
- [Stop reasons and events](#stop-reasons-and-events) - why a motor stopped, and what the drive handled on its own
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
| <PRE>PUB driveDirection(power, direction) : eError</PRE> | Control the speed and direction of your robot using the {power} and {direction} inputs.</br>Turns both motors on at {power, [(-100) to 100]} but adjusted by {direction, [(-100) to 100]}. A positive {direction} turns right and a negative one left, by slowing the wheel on that side; at 100 that wheel stops.</br> AFFECTED BY:  setAcceleration(), setDeceleration(), setMaxSpeed(), holdAtStop()
| <PRE>PUB driveForDistance(leftDistance, rightDistance, distanceUnits) : eError</PRE> | Drive both wheels forward until each has travelled its own distance: equal distances drive straight, unequal ones turn toward the shorter side.</br>Each wheel runs at a power in proportion to its distance, the longer one at setMaxSpeedForDistance() (never above setMaxSpeed()), so both finish at about the same time, and each comes to rest at its own distance (within about two hall ticks). {\*distance} is in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI].</br>Each distance counts from this call, whatever the odometers read, so two calls in a row each travel their own distance. **Forward only**: to back up, see [Backing up a distance](#backing-up-a-distance).</BR> AFFECTED BY:  setAcceleration(), setDeceleration(), setMaxSpeedForDistance(), setMaxSpeed(), holdAtStop()
| PUB driveAtPower(leftPower, rightPower) : eError | Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br>Turns left motor on at {leftPower} and right on at {rightPower}. Where {\*Power} are in the range [(-100) to 100].</br>AFFECTED BY:  setAcceleration(), setDeceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits) : eError | Stops both motors so they are at rest when either motor reaches {rotationCount} of {rotationUnits} [DRU\_HALL\_TICKS, DRU\_DEGREES or DRU\_ROTATIONS], counted from this call, turning either way.</BR>The stop begins early, by the distance each wheel needs to slow down, so the platform comes to rest at the limit (within about two hall ticks), not past it. DRU\_DEGREES rounds to the nearest hall tick (4° on the 6.5" motor: 90° is 23 ticks, 92°); a rotation that rounds to 0 ticks is refused with ERR\_LIMIT\_UNRESOLVABLE.</BR>USE WITH:  driveDirection(), driveAtPower()
| PUB stopAfterDistance(distance, distanceUnits) : eError | Stops both motors so they are at rest when either motor reaches {distance} specified in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI], counted from this call, forward or back. The odometers are not reset.</BR>The stop begins early, as for stopAfterRotation(). With driveAtPower(-power, -power) it backs the platform up a distance (see [Backing up a distance](#backing-up-a-distance)).</br>USE WITH:  driveDirection(), driveAtPower()
| PUB stopAfterTime(time, timeUnits) : eError | Stops both motors so they are at rest when {time} specified in {timeUnits} [DTU\_MILLISEC or DTU\_SEC] has elapsed (within a few milliseconds).</br>USE WITH:  driveDirection(), driveAtPower()
| PUB stopMotors() : eError | Stops both motors, killing any motion that was still in progress. The stop follows the drive's ramp down, at setDeceleration()'s rate.</BR> AFFECTED BY: setDeceleration(), holdAtStop()
| PUB emergencyCutoff() : eError | EMERGENCY-Stop - Immediately stop both motors, killing any motion that was still in progress. The emergency stop latches: drives are refused with ERR\_EMERGENCY\_STOPPED until clearEmergency(). **By design this is a hard stop**: both wheels short their phases at once, giving up the gentle deceleration every other stop uses. From speed that can draw tens of amps per wheel and stop the platform abruptly, which can tip a tall robot. Use stopMotors() when a controlled stop will do.
| PUB clearEmergency() : eError | Clear the emergency stop, allowing the motors to be driven again. Both motors stay stopped until commanded.
| PUB clearProtectiveStop() : eError | Acknowledge a protective stop (see [Protection and limits](#protection-and-limits)). Both motors stay stopped and may be driven again.
|  **>--- CONFIG**
| PUB start(leftBasePin, rightBasePin, driveVoltage, leftDetectMode, rightDetectMode) : ok | Start both motors' drivers and the front cog that serves them (3 cogs), for the boards at {leftBasePin} and {rightBasePin} [PINS\_\*], at {driveVoltage} [PWR\_\*], each board detected per its {\*DetectMode} [BRD\_AUTO\_DET, BRD\_REV\_A or BRD\_REV\_B].</br>Returns the front cog's id, or -1 when either motor or the front cog failed to start, or a start check refused it; getError() then names the cause and the wheel. A wheel whose board is not detected is refused (ERR\_BOARD\_NOT\_DETECTED) unless its detect mode forces BRD\_REV\_A or BRD\_REV\_B. Blocks for about 1 s on success while it calibrates both current sensors.</br>With nothing moving, it checks each wheel's hall sensors, current sense and motor leads (see getHealth()). A check that fails is retried, up to 3 times; if one still fails on either wheel the platform is not started: start() returns -1 and getError() reports ERR\_START\_CHECK\_FAILED, for the platform and for each failing wheel. getHealth() still says which check failed. The retries add time only when a check fails, up to about 4 s per failing wheel. setStartChecks(false) starts the platform anyway.
| PUB stop() : eError | Stop the front cog and both drive cogs, and release the motor pins
| PUB setAcceleration(rate) : eError | Set how fast both wheels speed up: every speed-up from now on reaches a steady {rate} in mm/s² at the wheel rim, [ACCEL\_MIN\_MM\_S2 to ACCEL\_MAX\_MM\_S2] (1 to 10,000). Every ramp eases its acceleration in and out over RAMP\_TAU\_MS (250 ms), so no start, speed change or stop begins or ends with a step of torque. Slowing down and stopping are set apart, by setDeceleration(), so this does not change stopping distances. Until this is called the built-in rate applies, ACCEL\_BUILTIN\_MM\_S2 (1,000 mm/s²). **Kept**: it may be set before start() and is kept across stop() and start(). A value out of range is refused with ERR\_BAD\_COUNT and changes nothing. See [Tuning the ramp](DEVELOP.md#tuning-the-ramp-for-your-robots-mass).
| PUB setDeceleration(rate) : eError | Set how fast both wheels slow down and stop: every slow-down and stop from now on reaches a steady {rate} in mm/s² at the wheel rim, [DECEL\_MIN\_MM\_S2 to DECEL\_MAX\_MM\_S2] (250 to 10,000), eased in and out as setAcceleration()'s is. Until this is called the built-in rate applies, DECEL\_BUILTIN\_MM\_S2 (1,470 mm/s²). **It sets the stopping distance** (see [How far the motor travels while stopping](#how-far-the-motor-travels-while-stopping)): stopMotors(), the command timeout's stop and a controlled fault stop all ramp down at it, and stopAfterDistance(), stopAfterRotation(), stopAfterTime() and driveForDistance() still bring the wheels to rest at their limit, since they start the stop early by whatever distance this rate needs. Its floor is higher than setAcceleration()'s for that reason: every stop must stay a stop. emergencyCutoff() does not ramp and is not affected. A wheel can still slow more gently than asked: the ramp down eases its deceleration off whenever the rotor runs too far ahead of the field. **Kept**, as setAcceleration(). A value out of range is refused with ERR\_BAD\_COUNT and changes nothing.
| PUB setMaxSpeed(speed) : eError | Limit top-speed to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 (MAX\_SPEED\_DEFAULT) and applies to both forward and reverse*. A value outside the range is saturated to it, never refused. It caps what you command; under load a motor may run slower than a capped command, and then holds the fastest speed it can sustain. **Kept**: it may be set before start() and is kept across stop() and start() (see [Settings start() keeps](#settings-start-keeps)).
| PUB setMaxSpeedForDistance(speed) : eError | Limit top-speed of driveForDistance() operations to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*. Saturated, not refused, and **kept**, as setMaxSpeed().
| PUB setCommandTimeout(nMs) : eError | A link-loss guard, off by default. While it is on, a driven platform must be sent a drive command at least every {nMs} [CMD\_TIMEOUT\_MIN\_MS to CMD\_TIMEOUT\_MAX\_MS] (10 to 60,000 ms), whatever started it: driveDirection(), driveAtPower() or driveForDistance(), with or without a stopAfter\*() limit armed. When one does not arrive in time both motors stop, as stopMotors() stops them, and getError() reports ERR\_COMMAND\_TIMEOUT once on every cog that calls it. Re-sending the same driveDirection() or driveAtPower() keeps an armed stopAfter\*() limit; re-sending driveForDistance() starts its distance again. CMD\_TIMEOUT\_OFF (0) turns it off. **Restored by start()**: every start() turns it off, and it needs a started platform (ERR\_NOT\_STARTED before start()), so set it after every start(). A value out of range is refused with ERR\_BAD\_COUNT.
| PUB calibrate() : eError | **NOT IMPLEMENTED**: it does nothing, and returns ERR\_NOT\_IMPLEMENTED (also recorded for getError()). It is kept so programs that call it still compile; no calibration is needed.
| PUB holdAtStop(bEnable) : eError | Once at rest, actively hold position (bEnable=true) or coast (bEnable=false, the default). Every stop from speed follows the drive's ramp down either way; this only chooses what happens at rest. Coast turns all the bridge transistors off. The hold keeps each wheel where it stopped and uses only the effort the load needs: the further a slope or a push moves the wheel, the harder it holds, up to a ceiling. If the load moves a wheel past the hold, or the hold stays at its ceiling too long, that wheel's motor phases are shorted instead. The short gives a drag that grows with speed but cannot hold a wheel still. getHoldStatus() reports which. setHoldLimits() sets the ceiling and the time limit. **Kept**: it may be set before start(), and start() applies it once its checks (which run with the motors coasting) are done.
| PUB setHoldLimits(ceilingPct, riseMs, limitMs) : eError | Set the limits of both wheels' hold at rest (holdAtStop(true)): the hold's effort rises to {ceilingPct} [1 to 100] % of the drive's full output over {riseMs} [1 to HOLD\_RISE\_MS\_MAX] (10,000) ms while a wheel stays displaced, and after {limitMs} [1 to HOLD\_LIMIT\_MS\_MAX] (600,000) ms at that ceiling the wheel switches to the phase short (getHoldStatus() reports HS\_LIMITED). The defaults, 10 %, 250 ms and 10,000 ms, were sized with the wheels unloaded; a loaded robot may need others. Both wheels always carry the same limits. **Restored by start()**: every start() restores the defaults, and it needs a started platform (ERR\_NOT\_STARTED before start()). A value out of range is refused with ERR\_BAD\_COUNT.
| PUB setFaultResponse(eMode, brakePct) : eError | Choose what a wheel does on a position fault, when its rotor cannot follow the field (an overload or a stall). FR\_SHIPPED coasts (holdAtStop(false)) or shorts the phases (holdAtStop(true)) at once. FR\_GRADED, the default, while the wheel's hall sensors read, re-syncs the field from them and stops along the ramp down (getStopReason() reports SR\_FAULT\_CONTROLLED); if the hall sensors are lost, or it faults again on that stop, it coasts (holdAtStop(false)) or brakes with the phases shorted for {brakePct} [0 to 100] % of the time (holdAtStop(true)), which scales the average braking to that share of a full short (the peak current is still a full short's). Either way the other wheel is stopped along its ramp. Both wheels always carry the same response. **Restored by start()**: every start() restores the default, FR\_GRADED, {brakePct} 10, and it needs a started platform (ERR\_NOT\_STARTED before start()). A value out of range is refused with ERR\_BAD\_COUNT.
| PUB setStartChecks(bRefuse) : eError | Choose whether start() refuses to start the platform when a start check still fails on either wheel after its retries (bRefuse=true, the default) or starts it anyway (bRefuse=false). Call it **before** start(). The retries run either way, and getHealth() reports the result either way. checkWiring() and the pack voltage sensor never refuse a start. The choice is kept across stop() and start() until you change it.
| PUB resetTracking() : eError | Resets both wheels' odometers: the distances getDistance() and the rotations getRotationCount() report start again from 0. Nothing else resets them. An armed distance or rotation limit is not moved: each counts from the moment it was armed.
|  **>--- STATUS**
| PUB getError() : eError, eLeftError, eRightError | Return and clear this cog's first recorded errors: the steering object's own, then each wheel's. NO\_ERROR where there is none. See [Errors](#errors).
| PUB getStopReason() : eLeftReason, eRightReason | Returns why each wheel's last drive ended, as an SR\_\* value: the first stop after the last drive command that wheel accepted. It stays readable until that wheel's next accepted drive command. SR\_NONE while a drive is under way. SR\_PARTNER means the other wheel's fault or block stopped this one: read the other wheel's reason. It is not an error code. See [Stop reasons and events](#stop-reasons-and-events).
| PUB getEvent() : eKind, nMs, eWheel, nValue | Returns this cog's oldest unread event: something the platform handled on its own, as an EV\_\* kind, the getms() time it happened, whose it was (EVW\_LEFT, EVW\_RIGHT, or EVW\_PLATFORM for the platform's own), and a value whose meaning depends on the kind. EV\_NONE (with the rest 0) when this cog has read them all. Every cog that calls it reads every event for itself, both wheels' merged oldest first; a cog that falls too far behind is told first, with EV\_LOST. See [Stop reasons and events](#stop-reasons-and-events).
| PUB getEventTotal(eKind) : nLeft, nRight, nPlatform | Returns how many events of {eKind} [EV\_STOP to EV\_FOLDBACK] each wheel, and the platform itself (EV\_LATE\_PASS and EV\_PACK only), has logged since start(), whether read or not, lost or not. Any other {eKind} returns 0s and records ERR\_BAD\_COUNT.
| PUB getDistance(distanceUnits) : leftDistanceInUnits, rightDistanceInUnits | Returns each wheel's odometer: the distance in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI] it has travelled since the last resetTracking() or start(). It is **total travel**, never negative: forward and back both add to it. Nothing but resetTracking() and start() resets it (not a drive, a limit, a fault, an emergency stop or checkWiring()). Resolution: whole hall ticks (about 5.76 mm on the 6.5" wheel), rounded to the nearest whole unit, so DDU\_M reads 0 until half a metre.
| PUB getRotationCount(rotationUnits) : leftRotationCount, rightRotationCount | Returns each wheel's odometer as a rotation in {rotationUnits} [DRU\_HALL\_TICKS, DRU\_DEGREES or DRU\_ROTATIONS], total travel either way since the last resetTracking() or start(). Resolution: DRU\_HALL\_TICKS counts each tick; DRU\_DEGREES steps by the motor's degrees per tick (4° on the 6.5" motor, 15° DocoEng); DRU\_ROTATIONS counts **whole** rotations completed, truncated (89 ticks of a 90-tick rotation read 0).
| PUB getPower() : leftPower, rightPower | Returns the last commanded power value for each of the motors, [-100 to 100] (zero once the motor is stopped). This is what you commanded, not what the motor achieved.
| PUB getCurrent() : nLtAmps, nLtWatts, nRtAmps, nRtWatts | Returns each motor's current and power draw, **all four integers**: the current in tenths of a milliamp (12,345 reads 1.2345 A) and the power in mW, calculated against the configured drive voltage. Each current is net of the rest reading start() takes with the motors floated, so a motor at rest reads about 0 A on average. One reading carries the sense's noise, and resolves one millivolt of sense: about 7 mA on a Rev B board, 0.2 A on a Rev A board.
| PUB getDriveVoltage() : eVoltage, nMilliVolts | Returns the PWR\_\* value both motors were started for, and its nominal voltage in mV (e.g. 18,500 for PWR\_18p5V). This is the configured value, not a measurement.
| PUB getStatus() : eLeftStatus, eRightStatus | Returns status of motor drive state for each motor: enumerated constant: DS\_MOVING, DS\_HOLDING, DS\_OFF, DS\_FAULTED, DS\_ESTOP, or DS\_Unknown. DS\_HOLDING reads only while that wheel's hold at rest is holding; a hold that has switched to the phase short reads DS\_OFF, stopped and not holding (getHoldStatus() says why). DS\_ESTOP covers the protective stop too.
| PUB getFaultCause() : eLeftCause, eRightCause | Returns why each wheel's most recent fault since start() happened: FC\_LAG (the rotor could not follow the field: an overload, a stall, or a wrong commutation offset), FC\_HALL (a hall sensor read an illegal code: dead, unpowered or disconnected), or FC\_NONE. It stays readable after the fault itself clears.
| PUB getHealth() : nLeftChecked, nLeftFailed, nLeftRecovered, nRightChecked, nRightFailed, nRightRecovered | Returns what start() checked on each wheel with the platform at rest, which checks failed, and which failed at first and then passed on a retry, as HLT\_\* bits. HLT\_HALLS covers the hall sensors, HLT\_SENSE\_ZERO the current sense, and HLT\_PHASE\_U, HLT\_PHASE\_V and HLT\_PHASE\_W each motor lead (connected and drivable). An open lead fails its own bit, and a missing motor fails all three. Nothing moves during these checks. A check that still fails after its retries refuses the start (see start() and setStartChecks()); the results stay readable after the refusal. A recovered check is not in the failed bits. HLT\_WIRING is added once checkWiring() has run, and the left wheel's HLT\_PACK when the pack voltage sensor is fitted.
| PUB getPackVoltage() : ePackStatus, nMilliVolts | Returns the battery pack's voltage in mV from the optional pack voltage sensor (VOLTAGE-SENSOR.md), averaged over about 64 ms: the pin is read once a millisecond and folded into the average every 8 ms, so a change in the pack shows with a time constant of about 60 ms. The status is PACK\_PRESENT, PACK\_ABSENT (the sensor is fitted but reads no pack: unplugged, or a broken lead), or PACK\_NOT\_FITTED. The voltage is 0 unless PACK\_PRESENT.
| PUB checkWiring() : eError | **Moves the robot.** Turns the platform a few degrees in place and back, each wheel one electrical cycle each way (about 3.5 cm at the tyre). This proves each wheel's hall and phase wiring: a swapped hall pair, swapped phase leads, a dead hall line or a wheel that does not turn all fail it. The verdict is recorded as that wheel's HLT\_WIRING. A wheel whose leg draws more current than a healthy walk ever does (miswiring stalls it against the field) is stopped at once by shorting its phases, and fails: the limit is 1 A of motor current on either board revision, about ten times what a healthy leg draws. It blocks about 1.3 seconds and leaves both wheels at rest per holdAtStop(). The walk always runs on the built-in ramp (ACCEL\_BUILTIN\_MM\_S2, DECEL\_BUILTIN\_MM\_S2), whatever setAcceleration() or setDeceleration() chose, and restores your rates when it ends. The walk's travel adds to the odometers; it does not reset them. It returns NO\_ERROR once the walk has run, pass or fail (read the verdict from getHealth()), or the error that kept it from running, such as ERR\_NOT\_STARTED or ERR\_EMERGENCY\_STOPPED. It returns ERR\_NO\_RESPONSE when the built-in ramp could not be confirmed in force on both wheels: then neither wheel moves, and your rates are restored. After any error no HLT\_WIRING verdict is recorded.
| PUB getHoldStatus() : eLeftState, nLeftDisplacement, eRightState, nRightDisplacement | Returns what each wheel's hold at rest is doing (holdAtStop(true)): HS\_HOLDING while holding, HS\_SLIPPED (the load moved the wheel past the hold) or HS\_LIMITED (it held at its ceiling too long) once that wheel has switched to the phase short, or HS\_OFF when not holding. Each displacement is how far, in hall ticks, the load has moved that wheel from where it stopped. A switched wheel stays shorted until the next command.
| PUB getHoldLimits() : ceilingPct, riseMs, limitMs | Returns the limits of the hold at rest in effect, as setHoldLimits() set them (the defaults after start())
| PUB getFaultResponse() : eMode, brakePct | Returns the fault response in effect, FR\_SHIPPED or FR\_GRADED and its {brakePct}, as setFaultResponse() set it (the default after start())
| PUB isHoldAtStop() : bEnable | Returns whether both wheels hold at rest (true) or coast (false, the default), as holdAtStop() set it. It reads the same before start().
| PUB isForwardReversed() : bLeftReversed, bRightReversed | Returns each wheel's reversal: start() reverses the right wheel's sense of forward, since the two motors face opposite ways, so it reads false, true once started.
| PUB getCommandTimeout() : nMs | Returns the command timeout in effect, in ms, as setCommandTimeout() set it; CMD\_TIMEOUT\_OFF (0) when off, before start() and after every start() until set.
| PUB getProtectiveStop() : eLeftCode, eRightCode | Returns each wheel's latched protective-stop cause (ERR\_PLATFORM\_BLOCKED), or NO\_ERROR when none, without clearing it. A cause on either wheel stops both.
| PUB getHallIntegrityCounts() : nLtMissed, nLtIllegal, nRtMissed, nRtIllegal | Returns, per motor since start, the times a hall transition was skipped and the times the hall sensors read an illegal code (%000 or %111)
| PUB getHallIllegalCodes() : nLtAllLow, nLtAllHigh, nRtAllLow, nRtAllHigh | Returns each motor's illegal hall codes split by kind: all three lines low (%000, a sensor without power) and all three high (%111, a line stuck or floating high)
| PUB getMaxSpeed() : maxSpeed | Returns the last specified {maxSpeed}; 75 until one is set, before start() as after
| PUB getMaxSpeedForDistance() : maxSpeed4dist | Returns the last specified {maxSpeedForDistance}; 75 until one is set, before start() as after
| PUB getAcceleration() : nRate | Returns the rate both wheels speed up at, in mm/s² at the rim, as setAcceleration() set it; the built-in rate, ACCEL\_BUILTIN\_MM\_S2 (1,000), until one is set. (Before driver revision 38 this read 0 until one was set: the old built-in ramp had no single rate.) 0 only when no wheel diameter is configured. It reads the same before start().
| PUB getDeceleration() : nRate | Returns the rate both wheels slow down and stop at, in mm/s² at the rim, as setDeceleration() set it; the built-in rate, DECEL\_BUILTIN\_MM\_S2 (1,470), until one is set. It reads the same before start().
| PUB isReady() : bState | Return T/F where T means both motors' driver cogs are running
| PUB isStopped() : bState | Return T/F where T means both motors are stopped (at rest; not TRUE while faulted or emergency-stopped: to wait for a drive to end, use isMoveDone())
| PUB isMoveDone() : bDone | Return T/F where T means neither wheel is moving under a command: the last drive is over, however it ended. TRUE once both wheels are at rest with no drive commanded (a limit, a stop, a timeout or a zero power ended it), and at once while a wheel is faulted, emergency-stopped or protectively stopped. FALSE from the moment a drive command is accepted. **Wait on this, with a bound, for a limited drive to finish**, then read getStopReason() to see why it ended; a drive with no limit never ends by itself. TRUE when not started.
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
| <PRE>PUB driveForDistance(distance, distanceUnits) : eError</PRE> | Turn the motor on, and bring it to rest after it travels {distance} in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI], counted from this call, whatever the odometer reads: two calls in a row each travel their own distance. **Forward only**: to back up, see [Backing up a distance](#backing-up-a-distance).</BR> AFFECTED BY:  setAcceleration(), setDeceleration(), setMaxSpeedForDistance(), holdAtStop()
| PUB driveAtPower(power) : eError | Control the speed and direction of this motor using the {power, [(-100) to 100]} input.</br>Turns the motor on at {power}. A faulted motor is cleared first, automatically.</br>AFFECTED BY:  setAcceleration(), setDeceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits) : eError | Stops the motor so it is at rest at {rotationCount} of {rotationUnits} [DRU\_HALL\_TICKS, DRU\_DEGREES or DRU\_ROTATIONS] (within about two hall ticks), counted from this call, turning either way. The stop begins early, by the distance the motor needs to slow down. DRU\_DEGREES rounds to the nearest hall tick, as for the steering object's stopAfterRotation().</BR>USE WITH:  driveAtPower()
| PUB stopAfterDistance(distance, distanceUnits) : eError | Stops the motor so it is at rest at {distance} specified in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI], counted from this call, forward or back. The stop begins early, as for stopAfterRotation(). With driveAtPower(-power) it backs the motor up a distance (see [Backing up a distance](#backing-up-a-distance)).</br>USE WITH:  driveAtPower()
| PUB stopAfterTime(time, timeUnits) : eError | Stops the motor so it is at rest when {time} specified in {timeUnits} [DTU\_MILLISEC or DTU\_SEC] has elapsed (within a few milliseconds).</br>USE WITH:  driveAtPower()
| PUB stopMotor() : eError | Stops the motor, killing any motion that was still in progress. The stop follows the drive's ramp down, at setDeceleration()'s rate.</BR> AFFECTED BY: setDeceleration(), holdAtStop()
| PUB emergencyCutoff() : eError | EMERGENCY-Stop - Immediately stop the motor, killing any motion that was still in progress. It brakes by shorting the motor phases, whatever holdAtStop() selects, and latches: drives are refused with ERR\_EMERGENCY\_STOPPED until clearEmergency(). **By design this is a hard stop**, giving up the gentle deceleration every other stop uses. From speed the short can draw tens of amps and stop the wheel abruptly, which can tip a tall robot. Use stopMotor() when a controlled stop will do.
| PUB clearEmergency() : eError | Clear the emergency stop. The motor stays stopped and may be driven again.
| PUB clearProtectiveStop() : eError | Acknowledge a protective stop (see [Protection and limits](#protection-and-limits)). The motor stays stopped and may be driven again.
|  **>--- CONFIG**
| PUB start(eMotorBasePin, eMotorVoltage, eDetectionMode) : ok | Start this motor's driver and its front cog (2 cogs), for the board at {eMotorBasePin} [PINS\_\*], at {eMotorVoltage} [PWR\_\*], with the board detected per {eDetectionMode} [BRD\_AUTO\_DET, BRD\_REV\_A or BRD\_REV\_B].</br>Returns the driver's cog id, or -1 when it failed to start or a start check refused it; getError() then holds the cause. A pin group where no board is detected is refused (ERR\_BOARD\_NOT\_DETECTED) unless you force BRD\_REV\_A or BRD\_REV\_B. Blocks for about 1 s on success while it calibrates the current sensor.</br>With nothing moving, it checks the hall sensors, the current sense and the motor leads (see getHealth()). A check that fails is retried, up to 3 times; if one still fails the motor is not started: start() returns -1 and getError() reports ERR\_START\_CHECK\_FAILED. getHealth() still says which check failed. The retries add time only when a check fails, up to about 4 s. setStartChecks(false) starts the motor anyway.
| PUB stop() : eError | Stop both cogs and release the pins assigned to this motor
| PUB setAcceleration(rate) : eError | Set how fast the motor speeds up: every speed-up from now on reaches a steady {rate} in mm/s² at the wheel rim, [ACCEL\_MIN\_MM\_S2 to ACCEL\_MAX\_MM\_S2] (1 to 10,000). Every ramp eases its acceleration in from 0 over RAMP\_TAU\_MS (250 ms) and back out as the target speed arrives, so it never begins or ends with a step of torque; a reversal passes through zero in one continuous ramp. Until this is called the built-in rate applies, ACCEL\_BUILTIN\_MM\_S2 (1,000 mm/s²). Slowing down and stopping are set apart, by setDeceleration(), so this does not change stopping distances. The motor can still accelerate more slowly than asked: the drive never lets the field run further ahead of the rotor than the motor can follow. **Kept** across stop() and start(), and may be set before start(). A value out of range is refused with ERR\_BAD\_COUNT and changes nothing.
| PUB setDeceleration(rate) : eError | Set how fast the motor slows down and stops: every slow-down and stop from now on reaches a steady {rate} in mm/s² at the wheel rim, [DECEL\_MIN\_MM\_S2 to DECEL\_MAX\_MM\_S2] (250 to 10,000), eased in and out as setAcceleration()'s is. Until this is called the built-in rate applies, DECEL\_BUILTIN\_MM\_S2 (1,470 mm/s²). It sets the stopping distance, and the limits follow it, as for the steering object's setDeceleration(). **Kept** across stop() and start(), and may be set before start(). A value out of range is refused with ERR\_BAD\_COUNT and changes nothing.
| PUB setMaxSpeed(speed) : eError | Limit top-speed to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 (MAX\_SPEED\_DEFAULT) and applies to both forward and reverse*. A value outside the range is saturated to it, never refused. It caps what you command; under load the motor may run slower than a capped command, and then holds the fastest speed it can sustain. **Kept** across stop() and start(), and may be set before start() (see [Settings start() keeps](#settings-start-keeps)).
| PUB setMaxSpeedForDistance(speed) : eError | Limit top-speed of driveForDistance() operations to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*. Saturated, not refused, and **kept**, as setMaxSpeed().
| PUB setCommandTimeout(nMs) : eError | A link-loss guard, off by default. While it is on, a driven motor must be sent a drive command at least every {nMs} [CMD\_TIMEOUT\_MIN\_MS to CMD\_TIMEOUT\_MAX\_MS] (10 to 60,000 ms), whatever started it: driveAtPower() or driveForDistance(), with or without a stopAfter\*() limit armed. When one does not arrive in time the motor stops, as stopMotor() stops it, and getError() reports ERR\_COMMAND\_TIMEOUT once on every cog that calls it. Re-sending the same driveAtPower() keeps an armed stopAfter\*() limit; re-sending driveForDistance() starts its distance again. CMD\_TIMEOUT\_OFF (0) turns it off. **Restored by start()**: every start() turns it off, and it needs a running motor (ERR\_NOT\_STARTED before start()).
| PUB calibrate() : eError | **NOT IMPLEMENTED**: it does nothing, and returns ERR\_NOT\_IMPLEMENTED (also recorded for getError()). It is kept so programs that call it still compile; no calibration is needed.
| PUB holdAtStop(bEnable) : eError | Once at rest, actively hold position (bEnable=true) or coast (bEnable=false, the default). Every stop from speed follows the drive's ramp down either way. Coast turns all the bridge transistors off. The hold keeps the wheel where it stopped and uses only the effort the load needs, up to a ceiling. If the load moves the wheel past the hold, or the hold stays at its ceiling too long, the motor phases are shorted instead, and getHoldStatus() says which. setHoldLimits() sets the ceiling and the time limit. After a fault the motor coasts (false) or brakes (true), since a faulted drive cannot hold a position (see setFaultResponse()). **Kept**: it may be set before start(), and start() applies it once its checks (which run with the motor coasting) are done.
| PUB setHoldLimits(ceilingPct, riseMs, limitMs) : eError | Set the limits of the hold at rest (holdAtStop(true)): {ceilingPct} [1 to 100], {riseMs} [1 to HOLD\_RISE\_MS\_MAX] and {limitMs} [1 to HOLD\_LIMIT\_MS\_MAX], as for the steering object's setHoldLimits(). The defaults, 10 %, 250 ms and 10,000 ms, were sized with the wheel unloaded; a loaded robot may need others. **Restored by start()**: every start() restores the defaults, and it needs a running motor (ERR\_NOT\_STARTED before start()). A value out of range is refused with ERR\_BAD\_COUNT.
| PUB setFaultResponse(eMode, brakePct) : eError | Choose what the motor does on a position fault: FR\_GRADED (the default) or FR\_SHIPPED, with {brakePct} [0 to 100], as for the steering object's setFaultResponse(). **Restored by start()**: every start() restores the default, FR\_GRADED, {brakePct} 10, and it needs a running motor (ERR\_NOT\_STARTED before start()). A value out of range is refused with ERR\_BAD\_COUNT.
| PUB setStartChecks(bRefuse) : eError | Choose whether start() refuses to start a motor whose start check still fails after its retries (bRefuse=true, the default) or starts it anyway (bRefuse=false). Call it **before** start(). The choice is kept across stop() and start() until you change it.
| PUB resetTracking() : eError | Resets the odometer: the distance getDistance() and the rotation getRotationCount() report start again from 0. Nothing else resets it. An armed distance or rotation limit is not moved: each counts from the moment it was armed.
| PUB forwardIsReverse() : eError | Reverse this motor's sense of forward, for a motor mounted facing the other way (the steering object does this for the right wheel). The same as setForwardIsReverse(true); setForwardIsReverse(false) undoes it.
| PUB setForwardIsReverse(bEnable) : eError | Reverse this motor's sense of forward (bEnable=true) or restore it (false, the default). A positive power then turns the motor the other way; getPower() still reads what you commanded. It applies to the next drive command. **Kept** across stop() and start(), and may be set before start().
|  **>--- STATUS**
| PUB getError() : eError | Return and clear this cog's first recorded error, NO\_ERROR when there is none. See [Errors](#errors).
| PUB getStopReason() : eReason | Returns why the motor's last drive ended, as an SR\_\* value: the first stop after the last drive command it accepted, readable until the next one. SR\_NONE while a drive is under way. It is not an error code. See [Stop reasons and events](#stop-reasons-and-events).
| PUB getEvent() : eKind, nMs, nValue | Returns this cog's oldest unread event: an EV\_\* kind, the getms() time it happened, and a value whose meaning depends on the kind; EV\_NONE (with the rest 0) when this cog has read them all. As for the steering object's getEvent(), without the wheel. See [Stop reasons and events](#stop-reasons-and-events).
| PUB getEventTotal(eKind) : nCount | Returns how many events of {eKind} [EV\_STOP to EV\_FOLDBACK] the motor has logged since start(), whether read or not, lost or not. Any other {eKind} returns 0 and records ERR\_BAD\_COUNT.
| PUB getDistance(distanceUnits) : distanceInUnits | Returns the odometer: the distance in {distanceUnits} [DDU\_MM, DDU\_CM, DDU\_IN, DDU\_FT, DDU\_M, DDU\_KM or DDU\_MI] this motor has travelled since the last resetTracking() or start(), total travel forward and back, never negative, rounded to the nearest whole unit (as the steering object's getDistance())
| PUB getRotationCount(rotationUnits) : rotationCount | Returns the odometer as a rotation in {rotationUnits} [DRU\_HALL\_TICKS, DRU\_DEGREES or DRU\_ROTATIONS] since the last resetTracking() or start(); DRU\_ROTATIONS counts whole rotations, truncated (as the steering object's getRotationCount())
| PUB getPower() : nPower | Returns the last commanded power [-100 to 100] (zero once the motor is stopped). This is what you commanded, not what the motor achieved.
| PUB getCurrent() : fAmps, fWatts | Returns the motor's current and power draw. **Both are integers, not floats, despite their names**: the current in tenths of a milliamp (12,345 reads 1.2345 A) and the power in mW, calculated against the configured drive voltage. The current is net of the rest reading start() takes with the motor floated, so the motor at rest reads about 0 A on average (see the steering object's getCurrent())
| PUB getDriveVoltage() : eVoltage, nMilliVolts | Returns the PWR\_\* value this motor was started for, and its nominal voltage in mV. This is the configured value, not a measurement.
| PUB getStatus() : eStatus | Returns status of motor drive state for this motor: enumerated constant: DS\_MOVING, DS\_HOLDING, DS\_OFF, DS\_FAULTED, DS\_ESTOP, or DS\_Unknown. DS\_HOLDING reads only while the hold at rest is holding; a hold that has switched to the phase short reads DS\_OFF (getHoldStatus() says why)
| PUB getFaultCause() : eCause | Returns why the most recent fault since start() happened: FC\_LAG, FC\_HALL or FC\_NONE (see the steering object's getFaultCause()). It stays readable after the fault itself clears.
| PUB getHealth() : nChecked, nFailed, nRecovered | Returns what start() checked with the motor at rest, which checks failed, and which failed at first and then passed on a retry: HLT\_\* bits (see the steering object's getHealth()). The results stay readable after start() refuses the motor.
| PUB getPackVoltage() : ePackStatus, nMilliVolts | Returns the battery pack's voltage in mV from the optional pack voltage sensor: PACK\_PRESENT, PACK\_ABSENT or PACK\_NOT\_FITTED (see the steering object's getPackVoltage()).
| PUB checkWiring() : eError | **Moves the wheel** one electrical cycle forward and back to prove its hall and phase wiring, and records the verdict as HLT\_WIRING (see the steering object's checkWiring()). The walk always runs on the built-in ramp (ACCEL\_BUILTIN\_MM\_S2, DECEL\_BUILTIN\_MM\_S2), whatever setAcceleration() or setDeceleration() chose, and restores your rates when it ends. The walk's travel adds to the odometer; it does not reset it. It returns NO\_ERROR once the walk has run, pass or fail, ERR\_NOT\_STARTED, or ERR\_NO\_RESPONSE when the built-in ramp could not be confirmed in force: then the wheel does not move and no HLT\_WIRING verdict is recorded.
| PUB getHoldStatus() : eHoldState, nDisplacement | Returns what the hold at rest is doing (holdAtStop(true)): HS\_HOLDING, HS\_SLIPPED, HS\_LIMITED or HS\_OFF, and how far the load has moved the wheel from where it stopped, in hall ticks (see the steering object's getHoldStatus()).
| PUB getHoldLimits() : ceilingPct, riseMs, limitMs | Returns the limits of the hold at rest in effect, as setHoldLimits() set them (the defaults after start())
| PUB getFaultResponse() : eMode, brakePct | Returns the fault response in effect, as setFaultResponse() set it (the default after start())
| PUB isHoldAtStop() : bEnable | Returns whether the motor holds at rest (true) or coasts (false, the default), as holdAtStop() set it. It reads the same before start().
| PUB isForwardReversed() : bEnable | Returns whether this motor's sense of forward is reversed, as setForwardIsReverse() or forwardIsReverse() set it. It reads the same before start().
| PUB getCommandTimeout() : nMs | Returns the command timeout in effect, in ms, as setCommandTimeout() set it; CMD\_TIMEOUT\_OFF (0) when off, before start() and after every start() until set.
| PUB isFaultSignal() : bState | Return T/F where T means the motor has faulted since start() or since clearFaultSignal(); unlike isFaulted() it stays set after the fault clears
| PUB clearFaultSignal() : eError | Reset the record read by isFaultSignal()
| PUB getProtectiveStop() : eProtectiveCode | Returns the latched protective-stop cause (ERR\_PLATFORM\_BLOCKED), or NO\_ERROR when none, without clearing it
| PUB getHallIntegrityCounts() : nMissedTransitions, nIllegalCodes | Returns the times since start a hall transition was skipped, and the times the hall sensors read an illegal code (%000 or %111)
| PUB getHallIllegalCodes() : nAllLowCodes, nAllHighCodes | Returns the illegal hall codes split by kind: %000 (a sensor without power) and %111 (a line stuck or floating high)
| PUB getMaxSpeed() : maxSpeed | Returns the last specified {maxSpeed}; 75 until one is set, before start() as after
| PUB getMaxSpeedForDistance() : maxSpeed4dist | Returns the last specified {maxSpeedForDistance}; 75 until one is set, before start() as after
| PUB getAcceleration() : nRate | Returns the rate the motor speeds up at, in mm/s² at the rim: the rate setAcceleration() was given, the built-in rate, ACCEL\_BUILTIN\_MM\_S2 (1,000), until then. Every ramp has a single steady rate since driver revision 38, so this no longer reads 0 for the built-in ramp. 0 only when no wheel diameter is configured. It reads the same before start().
| PUB getDeceleration() : nRate | Returns the rate the motor slows down and stops at, in mm/s² at the rim: the rate setDeceleration() was given, the built-in rate, DECEL\_BUILTIN\_MM\_S2 (1,470), until then. It reads the same before start().
| PUB getRawHallTicks() : rawTickCount | Return the raw driver-maintained tick count, signed: it counts up one way and down the other<BR>See: getRotationCount() for the odometer, the total travel since the last resetTracking()
| PUB getBoardType() : eBoardRev | Returns REV\_A or REV\_B for the board at this pin group, else REV\_Unknown
| PUB isReady() : bState | Return T/F where T means the motor's driver cog is running
| PUB isStopped() : bState |  Return T/F where T means the motor is stopped (at rest; not TRUE while faulted or emergency-stopped: to wait for a drive to end, use isMoveDone())
| PUB isMoveDone() : bDone | Return T/F where T means the motor is not moving under a command: the last drive is over, however it ended (as the steering object's isMoveDone()). Wait on it with a bound, then read getStopReason().
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

## Settings start() keeps

Some settings are your program's choices, and start() keeps them. Others protect the motor and the board, and every start() puts them back to their defaults. The rule is the same on both objects.

| Kept: set any time, before start() too; kept across stop() and start() | Read back with |
| --- | --- |
| setMaxSpeed() | getMaxSpeed() |
| setMaxSpeedForDistance() | getMaxSpeedForDistance() |
| holdAtStop() | isHoldAtStop() |
| setForwardIsReverse(), forwardIsReverse() (motor object) | isForwardReversed() |
| setStartChecks() | (read by start() itself) |
| setAcceleration() | getAcceleration() |
| setDeceleration() | getDeceleration() |

| Restored by every start(): set them after start() | Read back with |
| --- | --- |
| setFaultResponse() | getFaultResponse() |
| setHoldLimits() | getHoldLimits() |
| setCommandTimeout() | getCommandTimeout() |

The ramp is two settings: setAcceleration() sets the speed-up part and setDeceleration() the slow-down part, the same calls on the steering and motor objects. Until either is called its built-in rate applies.

The restored settings need a running motor: called before start() they are refused with `ERR_NOT_STARTED`. `start()` checks the motor with it coasting whatever holdAtStop() chose, and applies the hold only once those checks are done.

## Backing up a distance

`driveForDistance()` drives forward only. To back up a distance, use two calls: a reverse power, and a distance limit.

```spin2
    wheel.driveAtPower(-40)                        ' drive in reverse...
    wheel.stopAfterDistance(30, wheel.DDU_CM)      ' ...and bring the motor to rest 30 cm from here
```

On the steering object the same two calls are `wheels.driveAtPower(-40, -40)` and `wheels.stopAfterDistance(30, wheels.DDU_CM)`.

- **They are two calls, not one atomic move.** Each is its own command, and the motor is already reversing when the limit is armed. A distance limit counts from the moment it is armed, so the few milliseconds of travel between the two calls are not counted. If that matters, make the calls the other way round, as the demos arm every limit: `stopAfterDistance()` first, at rest, then `driveAtPower(-40)`; the limit then counts from before the motor moves.
- **A distance limit counts travel either way**, so it stops a reversing motor just as it stops one going forward.
- **The odometer is not reset.** `getDistance()` keeps counting total travel, forward and back; backing up 30 cm adds 30 cm to it.

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
| ERR\_START\_CHECK\_FAILED | -1020 | start(): a start check still failed after its retries, so the motor was not started; getHealth() says which |
| ERR\_NOT\_IMPLEMENTED | -1021 | the method is kept so programs compile, but does nothing: calibrate() |
| ERR\_BAD\_MOTOR\_TABLE | -1022 | start(): a motor's hall delta table holds a step other than -1, 0 or +1 (see ADDING\_MOTOR.md); nothing was launched |
| ERR\_PROTECTIVE\_STOP | -2000 | a protective stop is latched for a cause other than the named ones |
| ERR\_PLATFORM\_BLOCKED | -2001 | a protective stop is latched: a motor commanded to move did not turn for about a second |

## Stop reasons and events

`getError()` tells you about your own calls. Two more status methods tell you what the drive did on its own.

**`getStopReason()` says why the last drive ended.** A drive begins when the motor accepts a non-zero power or a `driveForDistance()`; a refused command begins nothing. The first stop after that is the reason, and it stays readable until the motor accepts its next drive command. A later stop of the motor at rest does not replace it (a fault there still appears in the event log). The one exception: a controlled fault stop that faults again before it comes to rest turns `SR_FAULT_CONTROLLED` into `SR_FAULT_LOST`. A stop reason is not an error code, and `getStatus()` is unchanged by it.

| Reason | Means |
| --- | --- |
| SR\_NONE | a drive is under way, or none has ended since start() |
| SR\_COMMANDED | your program ended it: a stop, a zero power, or a call that replaced it |
| SR\_AT\_LIMIT | its distance, rotation or time limit was reached |
| SR\_FAULT\_CONTROLLED | a position fault, answered by re-syncing from the hall sensors and stopping along the ramp down (setFaultResponse(FR\_GRADED) only) |
| SR\_FAULT\_LOST | a position fault that lost control: the motor coasted or braked as the fault response selects |
| SR\_BLOCKED | the protective stop: the motor was commanded to move and did not turn |
| SR\_LINK\_LOST | setCommandTimeout(): no drive command arrived in time |
| SR\_EMERGENCY | emergencyCutoff() |
| SR\_PARTNER | steering object only: the other wheel's fault or block stopped this one; read that wheel's reason |

**One limit.** If the front cog ever fails to answer a stop in time, your cog stops the motor itself and no reason is recorded, so a drive that was under way reads SR\_NONE.

**`getEvent()` returns what the drive handled on its own**, one event per call, oldest first: its kind, the `getms()` time it happened, and a value whose meaning depends on the kind. The steering object also returns whose it was: EVW\_LEFT, EVW\_RIGHT, or EVW\_PLATFORM for the platform's own (EV\_LATE\_PASS and EV\_PACK). When your cog has read everything, it returns EV\_NONE.

- **Every cog reads every event for itself.** One cog reading an event does not take it from another.
- **The log keeps the last EV\_QUEUE\_DEPTH (16) unread events for each cog** (per wheel, on the steering object). A cog that falls further behind loses its oldest, and its next call returns EV\_LOST, whose value is how many were lost, before anything else. A lost event never reads as EV\_NONE.
- **`getEventTotal()` counts each kind since start()**, read or not, lost or not.
- **start() empties the log.**

| Event | Means | Value |
| --- | --- | --- |
| EV\_NONE | nothing unread | 0 |
| EV\_LOST | this cog fell behind and lost events; it always comes first | how many were lost |
| EV\_STOP | a drive ended | the SR\_\* recorded, as getStopReason() then reads |
| EV\_FAULT\_RESYNC | a position fault answered by a re-sync and a controlled stop | FC\_LAG |
| EV\_FAULT | a position fault latched (DS\_FAULTED) | FC\_LAG or FC\_HALL |
| EV\_HOLD\_SLIP | the hold at rest switched to the phase short: the load moved the wheel past it | the displacement, hall ticks |
| EV\_HOLD\_LIMIT | the hold at rest switched to the phase short: it held at its ceiling too long | the drive duty it held |
| EV\_CURRENT\_LIMIT | the sustained-load current derate engaged or released | the current limit now in force, amps |
| EV\_FOLDBACK | the peak current fold-back engaged, and again once it has been quiet for a second | 0 on engaging; then how many PWM frames it limited |
| EV\_PATH\_LIMIT | steering object only: both wheels were slowed to keep the path, or fully released | the speed scale, per mille (1000 on release) |
| EV\_HALL\_MISSED | hall transitions were missed; at most one a second | how many since the last |
| EV\_HALL\_ILLEGAL | the hall sensors read an illegal code (%000 or %111); at most one a second | how many since the last |
| EV\_WALK\_GUARD | checkWiring() ended a wheel's leg for drawing too much current | the reading that tripped it, mV |
| EV\_LATE\_PASS | a front-cog pass ended within 100 µs of its 1 ms slot's end (or past it); at most one a second | how many since the last |
| EV\_PACK | the pack voltage sensor's status changed; at most one a second | the new PACK\_\* status |
| EV\_CHECK\_RETRY | a start check failed, then passed on a retry | the recovered HLT\_\* bits, plus the attempts used × 256 |

## Protection and limits

The drive does these on its own. None of them needs a call to turn it on.

- **Current limiting.** The drive estimates each motor's phase current, net of the rest reading `start()` takes, and while it is driving the motor folds back its output above **40 A**, and derates to **27 A** when the average stays high. These protect the driver board's transistors, not the motor, and they are not user settings. Each is logged when it acts: the fold-back as EV\_FOLDBACK, the derate as EV\_CURRENT\_LIMIT (see [Stop reasons and events](#stop-reasons-and-events)).
- **A ramp the motor can follow.** Speeding up never lets the field run further ahead of the rotor than the motor can follow: if the rotor falls behind, the ramp's acceleration eases off to zero (at the same jerk as every ramp, never a sudden step) until it catches up. So a heavy load or a steep `setAcceleration()` slows the acceleration instead of faulting the motor. Slowing down likewise eases its deceleration off whenever the rotor runs too far ahead of the field, so a steep `setDeceleration()` on a heavy robot stops less sharply than asked.
- **Holding what it can sustain.** When a motor cannot reach its commanded speed, under load say, it holds the fastest speed it can sustain rather than winding the field ahead of the rotor.
- **Path-preserving speed limiting** (two wheels). When one wheel cannot keep up, one side loaded say, the steering object slows both wheels together, so the platform keeps the path you commanded instead of curving off it.
- **The protective stop.** A motor that is commanded to move but does not turn for about a second, its rotor held far behind the field with no hall transition, is stopped at once in the state you chose with `holdAtStop()`, and so is its partner on a two-wheel platform. With `holdAtStop(FALSE)` the wheel coasts; with `holdAtStop(TRUE)` its phases are shorted, since a blocked wheel cannot be held. (An emergency stop always shorts the phases.) It latches: every drive is refused with `ERR_PLATFORM_BLOCKED` until you call `clearProtectiveStop()`. `clearEmergency()` does not release it. Check `getProtectiveStop()` to see whether it has fired. `getStopReason()` reports SR\_BLOCKED for the blocked wheel and, on a two-wheel platform, SR\_PARTNER for the other.
- **Faults.** If the rotor cannot follow the field at all, the drive faults. By default (`setFaultResponse(FR_GRADED)`, at 10 %) a motor whose hall sensors still read re-syncs from them and stops along its ramp down, and `getStopReason()` reports SR\_FAULT\_CONTROLLED. If its halls are lost, or it faults again on that stop, it coasts or takes the graded short (the phases shorted for 10 % of each brake period) as `holdAtStop()` selects, and `getStopReason()` reports SR\_FAULT\_LOST. With `setFaultResponse(FR_SHIPPED)` the motor instead coasts or brakes with the full short at once. Either way `getStatus()` reports `DS_FAULTED` and `getFaultCause()` says why. The fault clears when you command a stop or a new power. On a two-wheel platform, a fault on one wheel also stops the other along its ramp down, as `stopMotors()` would, so the platform stops instead of pivoting about the faulted wheel; that wheel reports SR\_PARTNER.
- **The start checks.** `start()` checks each motor's hall sensors, current sense and leads with nothing moving, retries a check that fails, and refuses to start a motor that still fails one (`ERR_START_CHECK_FAILED`). `setStartChecks(FALSE)` starts it anyway; `getHealth()` reports the result either way.
- **The emergency stop** brakes the motor by shorting its phases and latches until `clearEmergency()`.

## How far the motor travels while stopping

A stop is not instant. The motor ramps down, and it keeps moving while it does. `stopAfterDistance()`, `stopAfterRotation()` and `stopAfterTime()` account for this themselves, by starting the stop early. You need this figure only when you stop the motor with `stopMotor()` or `stopMotors()` and must know how far it will go.

**The ramp down reaches a steady deceleration**, the rate `setDeceleration()` sets (`getDeceleration()` reads it back), after easing in over RAMP\_TAU\_MS (250 ms), and eases out again as the wheel comes to rest. So the distance grows with the **square** of the speed you stop from, plus a term for the easing: travel ≈ speed² ÷ (2 × rate) + speed × 0.125 s, and the stop takes about speed ÷ rate + 0.25 s. Until you call `setDeceleration()` the rate is the built-in one, DECEL\_BUILTIN\_MM\_S2, 1,470 mm/s². For the 6.5" motor, wheels off the ground:

| Stopping from | Hall ticks to come to rest | Approximate travel |
| --- | --- | --- |
| 196 ticks/s (about 131 RPM) | **≈ 100 ticks** (derived for driver revision 38; not yet measured) | **≈ 575 mm** (23 in) |
| the same, before driver revision 38 (no easing) | **75 ticks** measured (74–77 over repeated runs, both motors) | ≈ 432 mm (17 in) |

To estimate another speed, use the formula: 196 ticks/s is about 1.13 m/s, and 1.13² ÷ (2 × 1.47) + 1.13 × 0.125 ≈ 0.57 m. From the top speed at 18.5 V (about 441 ticks/s, `power` 100, about 2.54 m/s) that is roughly 2.5 m, about 436 ticks.

- **Treat these figures as the most travel to expect, not a prediction.** With the platform on the floor, carrying weight, friction helps it stop and it comes to rest sooner.
- **The speed a given `power` produces depends on your drive voltage** (see [MOTOR_CHOICE.md](MOTOR_CHOICE.md)), so the same call stops in a shorter distance at a lower voltage. If you change `DRIVE_VOLTAGE`, re-check any clearance this was sizing.
- **`holdAtStop()` does not change it.** It only selects what happens once the motor is at rest.
- **`setDeceleration()` changes it**: the speed² term in inverse proportion to the rate (half the rate, twice that part of the distance); the easing term does not change with the rate. The limits (`stopAfterDistance()`, `stopAfterRotation()`, `stopAfterTime()`, `driveForDistance()`) follow the new rate on their own and still come to rest at the limit: they predict the driver's own stop, easing included, from its present speed and acceleration.
- **A wheel may stop less sharply than the rate asks.** The ramp down eases off whenever the rotor runs too far ahead of the field, so a high rate on a heavy robot stops in more distance than the formula gives.

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


