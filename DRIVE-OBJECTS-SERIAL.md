
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

**An ERROR reply comes in one of these forms.** In each case the command was not run.

- **The line could not be read as a command.** These are checked first, in this order:
  - `ERROR Unrecognized String`: the line held no command name (it was empty, or only spaces).
  - `ERROR Command NOT found`: the first word is not one of the commands below.
  - `ERROR Missing/Extra parameter(s)`: the command was sent with the wrong number of values.
  - `ERROR Parameter {n} ({text}) is not a decimal integer`: value {n}, counting from 1, is not a number (see [Values sent as numbers](#values-sent-as-numbers)). For example `drivepwr 20 fast` is refused `ERROR Parameter 2 (fast) is not a decimal integer`.
- **The value you sent was out of range.** The message names the value and its range. For example `drivepwr 120 0` is refused `ERROR LT-Power (120) out of range [-100, 100]`.
- **The drive refused the command.** The message names the command, the drive's error and its code. For example `ERROR drivepwr failed: ERR_EMERGENCY_STOPPED (-1016)`. The codes are listed in [Drive Objects: Errors](DRIVE-OBJECTS.md#errors).

An `OK` means the drive accepted the command. The non-OK responses help detect problems early in the development of your control routines. Once your drive code is working you should see them only for out-of-range values, an emergency stop, or a protective stop.

### How fast the P2 answers

When no command is waiting, the serial top-level checks for a new one every 1 ms. A command is picked up about 1 ms after its line's LF arrives. Then it takes as long as the command itself:

- A getter answers at once.
- A command the drive applies waits for the drive's answer, which is bounded.
- `checkwiring` takes about 1.3 s: two legs of about 0.65 s each. It takes at most about 4 s, if a leg does not come to rest.
- `setstartchecks 0` takes a full start.

At 624,000 baud each character takes 16 µs on the wire, so sending a command and its reply adds well under 1 ms. (Before 6.0 an idle P2 slept for up to 1 s between checks, so every command could wait that long.)

The P2 sends nothing unasked. The only line it sends on its own is its `ident:` line at start. Every other line is a reply to a command. Each reply is exactly one line, ending with a single LF. (Before 6.0, `OK` and `ERROR` replies ended with the two characters `\n` and no LF, and a getter's reply was followed by a stray `\n`.)

### How your host learns of a command timeout

When `settimeout` is on and no drive command arrives in time, both motors stop. The P2 does not send a message to say so. Your host finds out by asking:

- `getstopreason` reads `stopreason 46 46`: 46 is SR\_LINK\_LOST for each wheel.
- `geterror` reads `err -1019 ...`: its first value is ERR\_COMMAND\_TIMEOUT. It is reported once, and reading it clears it.

Send `geterror` before any command that might be refused. A refused command reads and clears the recorded errors to build its own `ERROR` reply, and that would take the -1019 with it.

### Values sent as numbers

Every value you send is a decimal integer: the digits 0-9, with an optional leading minus (`-5`), between -2,147,483,647 and 2,147,483,647. Where a command takes true or false you may also send the words `true` and `false` (in any case). A `+` sign, a decimal point, hex (`0x20`) or any other character is refused with `ERROR Parameter {n} ({text}) is not a decimal integer`. Values are separated by spaces or tabs. A line ends with LF, and a CR before the LF is ignored.

Units and status travel as the numbers of their enums:

| Kind | Values |
| --- | --- |
| {d-u} distance units | 1 DDU\_MM, 2 DDU\_CM, 3 DDU\_IN, 4 DDU\_FT, 5 DDU\_M, 6 DDU\_KM, 7 DDU\_MI |
| {r-u} rotation units | 1 DRU\_HALL\_TICKS, 2 DRU\_DEGREES, 3 DRU\_ROTATIONS |
| {t-u} time units | 1 DTU\_MILLISEC, 2 DTU\_SEC |
| status (`stat` reply) | 10 DS\_Unknown, 11 DS\_MOVING, 12 DS\_HOLDING, 13 DS\_OFF, 14 DS\_FAULTED, 15 DS\_ESTOP |
| hold {true \| false} | -1 true (hold), 0 false (coast) |
| setstartchecks {true \| false} | -1 true (refuse a start whose checks fail), 0 false (start anyway) |
| stop reason (`stopreason` reply) | 40 SR\_NONE, 41 SR\_COMMANDED, 42 SR\_AT\_LIMIT, 43 SR\_FAULT\_CONTROLLED, 44 SR\_FAULT\_LOST, 45 SR\_BLOCKED, 46 SR\_LINK\_LOST, 47 SR\_EMERGENCY, 48 SR\_PARTNER |
| event kind (`event` reply, `getevtotal {kind}`) | 60 EV\_NONE, 61 EV\_LOST, 62 EV\_STOP, 63 EV\_FAULT\_RESYNC, 64 EV\_FAULT, 65 EV\_HOLD\_SLIP, 66 EV\_HOLD\_LIMIT, 67 EV\_CURRENT\_LIMIT, 68 EV\_PATH\_LIMIT, 69 EV\_HALL\_MISSED, 70 EV\_HALL\_ILLEGAL, 71 EV\_WALK\_GUARD, 72 EV\_LATE\_PASS, 73 EV\_PACK, 74 EV\_CHECK\_RETRY, 75 EV\_FOLDBACK |
| event wheel (`event` reply) | 50 EVW\_LEFT, 51 EVW\_RIGHT, 52 EVW\_PLATFORM (the platform's own: EV\_LATE\_PASS, EV\_PACK); 0 with EV\_NONE |
| fault response {mode} | 0 FR\_SHIPPED, 1 FR\_GRADED |
| health bits (`health` reply) | 1 HLT\_HALLS, 2 HLT\_SENSE\_ZERO, 4 HLT\_PHASE\_U, 8 HLT\_PHASE\_V, 16 HLT\_PHASE\_W, 32 HLT\_WIRING, 64 HLT\_PACK -- each number is the sum of its bits |
| pack sensor status (`packvolt` reply) | 0 PACK\_NOT\_FITTED, 1 PACK\_ABSENT, 2 PACK\_PRESENT |
| fault cause (`faultcause` reply) | 0 FC\_NONE, 1 FC\_LAG, 2 FC\_HALL |
| hold state (`holdstatus` reply) | 0 HS\_OFF, 1 HS\_HOLDING, 2 HS\_SLIPPED, 3 HS\_LIMITED |

The stop reasons, event kinds and event wheels start at 40, 60 and 50, so none of them can be read as a status, a board revision or an error code. The pack status, fault cause and hold state start at 0: read them only from their own replies. New values are only ever appended.

**If the motors do not start because a start check failed**, the serial top-level still answers the host, but only three commands:

- `gethealth` says which check failed, on which wheel.
- `geterror` reads `ERR_START_CHECK_FAILED (-1020)` for the platform and for each failing wheel.
- `setstartchecks 0` starts the motors anyway.

Every other command is answered `ERROR {cmd} failed: ERR_NOT_STARTED (-1007)`. A start that failed for any other reason opens no host link. One such reason is `ERR_BAD_MOTOR_TABLE (-1022)`: a motor's hall delta table in the firmware holds a step other than -1, 0 or +1, so no motor starts until the table is corrected (see [Adding a Motor](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/ADDING_MOTOR.md#driver-startup-hall-order)).

### The 2-Wheel Steering Object PUBLIC Interface

| Steering Interface | Description |
| --- | --- |
|  **>--- CONTROL**
| <PRE>PUB driveDirection(power, direction)</PRE><BR><PRE>SER drivedir {pwr} {dir}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Control the speed and direction of your robot using the {power} and {direction} inputs.</br>Turns both motors on at {power, [(-100) to 100]} but adjusted by {direction, [(-100) to 100]}.</br> AFFECTED BY:  setAcceleration(), setDeceleration(), setMaxSpeed(), holdAtStop()
| <PRE>PUB driveForDistance(leftDistance, rightDistance, distanceUnits)</PRE><BR><PRE>SER drivedist {ltdist} {rtdist} {d-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Drive both wheels forward until each has travelled its own distance: equal distances drive straight, unequal ones turn toward the shorter side. Each wheel comes to rest at its own distance.</BR> AFFECTED BY:  setAcceleration(), setDeceleration(), setMaxSpeedForDistance(), setMaxSpeed(), holdAtStop()
| PUB driveAtPower(leftPower, rightPower)<BR><PRE>SER drivepwr {ltpwr} {rtpwr}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Control the speed and direction of your robot using the {leftPower} and {rightPower} inputs.</br>Turns left motor on at {leftPower} and right on at {rightPower}. Where {\*Power} are in the range [(-100) to 100].</br>AFFECTED BY:  setAcceleration(), setDeceleration(), setMaxSpeed(), holdAtStop()
| PUB stopAfterRotation(rotationCount, rotationUnits)<BR><PRE>SER stopaftrot {count} {r-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors so they are at rest when either motor reaches {rotationCount} of {rotationUnits}.</BR>USE WITH:  driveDirection(), driveAtPower()
| PUB stopAfterDistance(distance, distanceUnits)<BR><PRE>SER stopaftdist {dist} {d-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors so they are at rest when either motor reaches {distance} in {distanceUnits}.</br>USE WITH:  driveDirection(), driveAtPower()
| PUB stopAfterTime(time, timeUnits)<BR><PRE>SER stopafttime {time} {t-u}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Stops both motors so they are at rest when {time} in {timeUnits} has elapsed.</br>USE WITH:  driveDirection(), driveAtPower()
| PUB stopMotors()<BR><PRE>SER stopmotors<br>SER Returns: OK</PRE> | Stops both motors, killing any motion that was still in progress</BR> AFFECTED BY: setDeceleration(), holdAtStop()
| PUB emergencyCutoff()<BR><PRE>SER emercutoff<br>SER Returns: OK</PRE> | EMERGENCY-Stop - Immediately stop both motors, killing any motion that was still in progress. Drives are refused until `emerclear`.
| PUB clearEmergency()<BR><PRE>SER emerclear<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Clear the emergency stop, allowing the motors to be controlled again
| PUB clearProtectiveStop()<BR><PRE>SER protclear<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Acknowledge a protective stop: a motor commanded to move that did not turn for about a second stops both motors, and every drive is refused with `ERR_PLATFORM_BLOCKED (-2001)` until this. `emerclear` does not release it, and `protclear` does not release an `emercutoff`. With no protective stop latched it replies `OK` and changes nothing: a running drive keeps running.
| PUB checkWiring()<BR><PRE>SER checkwiring<br>SER Returns: OK \| ERROR {errormsg}</PRE> | **Moves the robot:** it turns the platform a few degrees in place and back, one electrical cycle each way per wheel, to prove each wheel's hall and phase wiring. Send it only when the robot may turn a little. It takes about 1.3 s, and both wheels end at rest as `hold` chooses. A wheel whose leg draws 1 A or more (on either board revision; a healthy leg draws about a tenth of that) is stopped at once by shorting its phases, and fails. The walk's travel adds to `getdist` and `getrot`; it does not reset them. `OK` means the check ran, whatever its verdict. The verdict is each wheel's HLT\_WIRING bit (32) in `gethealth`: checked, and failed or not. `ERROR checkwiring failed: ERR_NO_RESPONSE (-1017)` means the built-in ramp the walk runs on could not be confirmed in force: neither wheel moved and no verdict was recorded.
|  **>--- CONFIG**
| PUB start(leftBasePin, rightBasePin, driveVoltage, leftDetectMode, rightDetectMode)<BR><PRE>SER N/A</PRE> | Called by the serial top-level from your user configuration
| PUB stop() <BR><PRE>SER N/A</PRE>| Stop cogs and release pins assigned to motor drivers
| PUB setStartChecks(bRefuse)<BR><PRE>SER setstartchecks {true \| false}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Choose whether a start whose checks fail is refused. The serial top-level starts the motors at power-up, before your host is connected, so this is answered only **after its start checks refused the platform**. `setstartchecks 0` starts the motors anyway, and replies `OK` once they run: from then on every command is answered, and `gethealth` still says what failed. Nothing moves during the start, which takes about 1 s plus up to about 4 s for each wheel whose check still fails. If the start fails for another reason, the reply is `ERROR setstartchecks failed: {ERR_NAME} ({code})`. `setstartchecks -1` keeps the refusal. While the motors run the reply is `ERROR StartChecks apply only to a start its checks refused: the motors are running`.
| PUB setAcceleration(rate)<BR><PRE>SER setaccel {rate}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Set how fast both wheels speed up, in mm/s² at the wheel rim [1 to 10,000]; 1,000 until set. Every ramp eases its acceleration in and out over 250 ms, so no start, speed change, reversal or stop begins or ends with a jolt. Slowing down and stopping are set apart, by `setdecel`. Kept until the P2 is reset.
| PUB setDeceleration(rate)<BR><PRE>SER setdecel {rate}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Set how fast both wheels slow down and stop, in mm/s² at the wheel rim [250 to 10,000]; 1,470 until set. Every stop ramps down at it (`stopmotors`, the `settimeout` stop, a controlled fault stop), eased in and out over 250 ms, so it sets the stopping distance: about speed² ÷ (2 × rate) + speed × 0.125 s, where half the rate doubles the first part and the easing's part does not change (derived, not yet measured; see [How far the motor travels while stopping](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DRIVE-OBJECTS.md#how-far-the-motor-travels-while-stopping)). `stopaftdist`, `stopaftrot`, `stopafttime` and `drivedist` still come to rest at their limit. `emercutoff` does not ramp. Kept until the P2 is reset. A value out of range is refused with `ERROR Decel Rate ({rate}) out of range [250, 10000] mm/s^2` and changes nothing.
| PUB setMaxSpeed(speed)<BR><PRE>SER setspeed {speed}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Limit top-speed to {speed} where {speed} is  [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setMaxSpeedForDistance(speed)<BR><PRE>SER setspeedfordist {speed}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | Limit top-speed of driveForDistance() operations to {speed} where {speed} is [1 to 100] - *DEFAULT is 75 and applies to both forward and reverse*
| PUB setCommandTimeout(nMs)<BR><PRE>SER settimeout {ms}<br>SER Returns: OK \| ERROR {errormsg}</PRE> | A link-loss guard, off by default. While it is on, a driven platform must be sent a drive command at least every {ms} [10 to 60,000], whatever started it (`drivedir`, `drivepwr` or `drivedist`, with or without a stop limit armed); when one does not arrive in time both motors stop. Re-sending `drivedist` starts its distance again. `settimeout 0` turns it off. It is the host's choice: the serial top-level never turns it on by itself.
| PUB calibrate() <BR><PRE>SER N/A</PRE> | **NOT WORKING, YET** <BR>*(we may need this?)*
| PUB holdAtStop(bEnable)<BR><PRE>SER hold {true \| false}<br>SER Returns: OK \| ERROR {errormsg}</PRE>| Once at rest, actively hold position (true) or coast (false)
| PUB setFaultResponse(eMode, brakePct)<BR><PRE>SER setfaultresp {mode} {pct}<br>SER Returns: OK \| ERROR {errormsg}</PRE>| What both wheels do on a position fault (a wheel could not follow its field). {mode} 0 (FR\_SHIPPED): at once, coast (`hold false`) or short the phases (`hold true`). {mode} 1 (FR\_GRADED): with the hall sensors reading, re-sync and stop under control; otherwise coast (`hold false`), or brake with the phases shorted for {pct} [0 to 100] % of the time (`hold true`). The other wheel is stopped too. Restored to the default at start.
| PUB getFaultResponse() : eMode, brakePct<BR><PRE>SER getfaultresp<br>SER Returns: faultresp {mode} {pct}</PRE>| Returns the fault response in effect, as `setfaultresp` set it
| PUB setHoldLimits(ceilingPct, riseMs, limitMs)<BR><PRE>SER setholdlimits {pct} {rise} {limit}<br>SER Returns: OK \| ERROR {errormsg}</PRE>| Limits of the hold at rest (`hold true`): its effort ceiling {pct} [1 to 100] % of full duty, the {rise} [1 to 10,000] ms to reach it while a wheel is pushed off its stop position, and the {limit} [1 to 600,000] ms at the ceiling before it hands off to shorting the phases. The defaults were sized with the wheels unloaded. Restored to the defaults at start.
| PUB getHoldLimits() : ceilingPct, riseMs, limitMs<BR><PRE>SER getholdlimits<br>SER Returns: holdlimits {pct} {rise} {limit}</PRE>| Returns the hold limits in effect, as `setholdlimits` set them
| PUB resetTracking()<BR><PRE>SER resettracking<br>SER Returns: OK \| ERROR {errormsg}</PRE>| Resets the position tracking values returned by getDistance() and getRotationCount()
|  **>--- STATUS**
| PUB getDistance(distanceUnits) : leftDistanceInUnits, rightDistanceInUnits<BR><PRE>SER getdist {d-u}<br>SER Returns: dist {ltDistInUnits} {rtDistInUnits} \| ERROR {errormsg}</PRE> | Returns the distance in {distanceUnits} travelled by each motor since last reset
| PUB getRotationCount(rotationUnits) : leftRotationCount, rightRotationCount <BR><PRE>SER getrot {r-u}<br>SER Returns: rot {ltRotCountInUnits} {rtRotCountInUnits} \| ERROR {errormsg}</PRE>| Returns accumulated rotation in {rotationUnits}, since last reset, for each of the motors.
| PUB getPower() : leftPower, rightPower <BR><PRE>SER getpwr<br>SER Returns: pwr {ltPwr} {rtPwr}</PRE>| Returns the last commanded power value for each of the motors (zero once the motor is stopped)
| PUB getStatus() : eLeftStatus, eRightStatus<BR><PRE>SER getstatus<br>SER Returns: stat {ltStatus} {rtStatus}</PRE> | Returns each motor's drive status as a number (see the table above). **DS\_FAULTED (14)**: the motor has faulted, and clears when a stop or a new power is commanded. **DS\_ESTOP (15)**: the motor is emergency-stopped until `emerclear`, or protectively stopped until `protclear`.
| PUB getProtectiveStop() : eLeftCode, eRightCode <BR><PRE>SER getprot<br>SER Returns: prot {ltCode} {rtCode}</PRE>| Returns each wheel's latched protective-stop code (-2001 for `ERR_PLATFORM_BLOCKED`), or 0 when none
| PUB getStopReason() : eLeftReason, eRightReason <BR><PRE>SER getstopreason<br>SER Returns: stopreason {ltReason} {rtReason}</PRE>| Returns why each wheel's last drive ended, as a stop-reason number (40-48, see the table above): the first stop after the last drive command it accepted. 40 (SR\_NONE) while a drive is still open. 48 (SR\_PARTNER) means the other wheel's fault or block stopped this one: read the other wheel's reason. Not an error code.
| PUB getEvent() : eKind, nMs, eWheel, nValue <BR><PRE>SER getevent<br>SER Returns: event {kind} {ms} {wheel} {value}</PRE>| Returns the oldest event not yet read over this link, one per request: something the drive handled on its own (a stop and its reason, a fault, a current limit, hall-sensor trouble, ...). {kind} is 60 (EV\_NONE), with {ms}, {wheel} and {value} 0, when there is none. {ms} is the P2's millisecond count when it happened (compare only differences). {kind} 61 (EV\_LOST) comes first when events were lost because they were not read in time; its {value} is how many. The meaning of {value} depends on {kind}: for 62 (EV\_STOP) it is the stop reason.
| PUB getEventTotal(eKind) : nLeft, nRight, nPlatform <BR><PRE>SER getevtotal {kind}<br>SER Returns: evtotal {lt} {rt} {plat} \| ERROR {errormsg}</PRE>| Returns how many events of {kind} [62 to 75] each wheel, and the platform itself, has had since start, read or not, lost or not
| PUB getHealth() : nLeftChecked, nLeftFailed, nLeftRecovered, nRightChecked, nRightFailed, nRightRecovered <BR><PRE>SER gethealth<br>SER Returns: health {ltChk} {ltFail} {ltRecov} {rtChk} {rtFail} {rtRecov}</PRE>| Returns, for each wheel as health bits (see the table above), the checks start ran, the ones that failed, and the ones that failed at first and passed when retried. Answered even when the motors did not start.
| PUB getError() : eError, eLeftError, eRightError <BR><PRE>SER geterror<br>SER Returns: err {code} {ltCode} {rtCode}</PRE>| Returns, and clears, the first error codes recorded for this link since it last asked: the platform's own, the left wheel's and the right wheel's, 0 when none. Answered even when the motors did not start. (A command the drive refuses reads and clears them for its own `ERROR` reply.)
| PUB getDriveVoltage() : eVoltage, nMilliVolts <BR><PRE>SER getvoltage<br>SER Returns: volt {pwrEnum} {milliVolts}</PRE>| Returns the configured drive voltage, as its PWR\_\* number and its nominal value in mV. This is the configured value, not a measurement.
| PUB getPackVoltage() : ePackStatus, nMilliVolts <BR><PRE>SER getpackvolt<br>SER Returns: packvolt {status} {milliVolts}</PRE>| Returns the pack voltage measured by the optional pack voltage sensor ([VOLTAGE-SENSOR.md](VOLTAGE-SENSOR.md)), averaged over about 64 ms: read once a millisecond, folded into the average every 8 ms, following a change with a time constant of about 60 ms. {status} is 2 (PACK\_PRESENT), 1 (PACK\_ABSENT: the sensor is fitted but reads no pack) or 0 (PACK\_NOT\_FITTED). {milliVolts} is 0 unless the status is PACK\_PRESENT.
| PUB getCurrent() : nLtAmps, nLtWatts, nRtAmps, nRtWatts <BR><PRE>SER getcurrent<br>SER Returns: current {ltCurrent} {ltMilliWatts} {rtCurrent} {rtMilliWatts}</PRE>| Returns each motor's latest current, in units of 0.1 mA (so 12,500 is 1.25 A), and its power draw in mW. Both are net of the rest zero taken at start, so a motor at rest reads about 0 on average. One reading carries the sense's noise, and resolves one millivolt of sense: about 7 mA (a {ltCurrent} step of about 67) on a Rev B board, 0.2 A (2,000) on a Rev A board.
| PUB getFaultCause() : eLeftCause, eRightCause <BR><PRE>SER getfaultcause<br>SER Returns: faultcause {ltCause} {rtCause}</PRE>| Returns why each wheel's most recent fault since start happened: 1 (FC\_LAG) means the rotor could not follow the field, 2 (FC\_HALL) means a hall sensor read %000 or %111, and 0 (FC\_NONE) means it has not faulted. The cause stays readable after the fault clears; only a later fault replaces it.
| PUB getHoldStatus() : eLeftState, nLeftDisplacement, eRightState, nRightDisplacement <BR><PRE>SER getholdstatus<br>SER Returns: holdstatus {ltState} {ltTicks} {rtState} {rtTicks}</PRE>| Returns what each wheel's hold at rest (`hold true`) is doing: 1 (HS\_HOLDING), 2 (HS\_SLIPPED) or 3 (HS\_LIMITED), when the hold has handed off to shorting the phases, or 0 (HS\_OFF) when not holding. Each state is followed by the hall ticks the load has moved that wheel from where it stopped, signed, and 0 when not holding.
| PUB getHallIntegrityCounts() : nLtMissed, nLtIllegal, nRtMissed, nRtIllegal <BR><PRE>SER gethallcounts<br>SER Returns: hallcounts {ltMissed} {ltIllegal} {rtMissed} {rtIllegal}</PRE>| Returns, for each motor since start, the times its hall code changed without a countable single step (missed), and the times its hall sensors entered an illegal code, %000 or %111 (a dead or disconnected sensor)
| PUB getHallIllegalCodes() : nLtAllLow, nLtAllHigh, nRtAllLow, nRtAllHigh <BR><PRE>SER gethallillegal<br>SER Returns: hallillegal {ltAllLow} {ltAllHigh} {rtAllLow} {rtAllHigh}</PRE>| Returns each motor's illegal hall codes since start, split by kind. %000 (all low) is a sensor without power or a line pulled low; %111 (all high) is a line stuck or floating high. Each count stops at 65,535.
| PUB getMaxSpeed() : maxSpeed <BR><PRE>SER getmaxspd<br>SER Returns: speedmax {maxSpeed}</PRE>| Returns the last specified {maxSpeed}
| PUB getMaxSpeedForDistance() : maxSpeed4dist <BR><PRE>SER getmaxspdfordist<br>SER Returns: speeddistmax {maxSpeed}</PRE>| Returns the last specified {maxSpeedForDistance}
| PUB getAcceleration() : nRate <BR><PRE>SER getaccel<br>SER Returns: accel {rate}</PRE>| Returns the speed-up rate `setaccel` set, in mm/s²; the built-in rate, 1,000, until one is set.
| PUB getDeceleration() : nRate <BR><PRE>SER getdecel<br>SER Returns: decel {rate}</PRE>| Returns the slow-down and stop rate `setdecel` set, in mm/s²; the built-in rate, 1,470, until one is set.

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


