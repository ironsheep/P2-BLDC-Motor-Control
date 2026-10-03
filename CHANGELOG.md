# Changelog

Changes to the P2-BLDC-Motor-Control objects, newest first. Each release's entry is also its
GitHub release page.

## v6.1.0 (2026-10-03)

The drive holds its commanded speed under load, giving way only at its current limit.

### Improvements

- Under load the drive answers with torque up to its current limit and keeps its commanded speed: spins in
  place no longer run slow, and speed changes arrive at the set rate
- A wheel held at its current limit cannot lag-fault when pushed back, and resumes without a current surge
  when the limit releases
- Past full power a wheel keeps up smoothly at the voltage ceiling instead of running rough
- Two wheels: `EV_FOLDBACK` marks a wheel at its current limit, and `EV_PATH_LIMIT` both wheels slowed
  together because one is at its limit
- The FlySky demos hold a stopped wheel, so a full left or right turn pivots about it instead of spinning
- The FlySky demos send a knob's rate only when the knob moves, and always at either end
- Overlapping or unknown motor pin groups are refused at compile time, with a message naming the problem
- [DRIVER_BOARDS.md](DRIVER_BOARDS.md) describes the Rev A and Rev B boards and when to be careful with each
- Each release archive carries `LICENSE` and `CHANGELOG.md`

### Known Issues

- The drive does not use the pack sensor's voltage yet: `getCurrent()`'s watts and the speed table assume
  the configured `DRIVE_VOLTAGE`
- `getCurrent()` does not show regenerative current
- Braking by shorted phases (`emergencyCutoff()`, `holdAtStop(true)`) is not current-limited; ramp down
  before stopping where you can, as `stopMotor()` and the stop limits do
- `setHoldLimits()`'s defaults were sized with the wheels unloaded
- `calibrate()` is not implemented
- The drive is supported at a 270 MHz system clock (`_clkfreq = 270_000_000`, as in every demo); below about
  250 MHz its timing is unproven
- The DocoEng 4,000 RPM motor is not validated for v6.1.0; v6.1.0 is validated on the 6.5″ hub motor with
  Rev B boards
- The serial control path (`isp_steering_serial.spin2`, the Python host demo) is not validated on hardware
  for v6.1.0

## v6.0.0 (2026-10-01)

A reworked drive: lower current, a quiet start, built-in protection, and every command reporting its result.

### New Features

- `setFaultResponse()` chooses what a motor does on losing control: re-sync from the halls and ramp down
  (`FR_GRADED`, the default) or stop at once (`FR_SHIPPED`)
- Current limiting protects the board: output folds back above 40 A and derates to 27 A under sustained load
- Protective stop: a commanded motor that cannot turn for about a second stops until
  `clearProtectiveStop()` (`ERR_PLATFORM_BLOCKED`, `getProtectiveStop()`)
- `start()` checks the hall sensors, the current sense and each motor lead with nothing moving, retries a
  failing check, and `getHealth()` reports the result
- `checkWiring()`: an opt-in check that moves each wheel a few centimetres to prove its hall and phase wiring
- `setCommandTimeout(ms)`: an opt-in link-loss guard that stops the motors when drive commands stop arriving
- `getStopReason()` says why the last drive ended: your command, its limit, a fault, a blocked wheel, a lost
  link, an e-stop, or the other wheel
- `getEvent()` and `getEventTotal()` log what the drive handled on its own (stops, faults, current limiting,
  hall trouble), for every cog, counting any lost
- `holdAtStop(true)` holds a stopped wheel with the effort its load needs, up to a ceiling, then shorts the
  phases (`getHoldStatus()`, `setHoldLimits()`)
- `getPackVoltage()` reads the battery pack from an optional voltage sensor
  ([VOLTAGE-SENSOR.md](VOLTAGE-SENSOR.md))
- `getFaultCause()`, `getHallIntegrityCounts()` and `getHallIllegalCodes()` report why a motor faulted and
  the health of its hall sensors
- `setDeceleration(rate)` sets the slow-down and stop rate (250 to 10,000 mm/s²); `getAcceleration()` and
  `getDeceleration()` read the ramp, the built-in rates until set
- Ramp rates set before `start()` are kept across it
- `getDriveVoltage()` returns the configured drive voltage
- Distance commands accept `DDU_KM` and `DDU_MI`
- Two wheels: `isFaulted()` and `isEmergency()` report a faulted or e-stopped platform
- `isp_flysky_rx` `hasSignal()` reports whether the transmitter is heard; the FlySky demos stop the platform when
  it is lost
- Serial: new commands `settimeout`, `getvoltage`, `protclear`, `getprot`, `getpackvolt`, `getcurrent`,
  `getfaultcause`, `getholdstatus`, `gethallcounts`, `gethallillegal`, `checkwiring`, `setstartchecks`,
  `setdecel`, `getaccel` and `getdecel`; `protclear` releases a protective stop, which `emerclear` does not

### Improvements

- 6.5″ motor: commutation uses the motor's measured hall position and a lead that follows speed, placing the
  field for the least running current
- Forward and reverse draw the same current, to within 8 %
- Starting from rest is smooth: the current surge at spin-up is gone
- Every ramp is jerk-limited: acceleration eases in and out over 250 ms, and a reversal passes through zero
  in one continuous ramp
- A motor that cannot reach its command runs slower instead of faulting
- `stopAfterDistance()`, `stopAfterRotation()` and `stopAfterTime()` bring the motor to rest at the limit
- Two wheels: when one wheel cannot keep up, both slow together, so the platform keeps its path
- Two wheels: when one wheel faults, the other ramps to a stop instead of pivoting the platform
- `getCurrent()` reads zero at rest; `start()` takes about 1 s to calibrate it
- The drive uses a fixed 2 cogs for one motor and 3 for two; `startSenseCog()` starts nothing and is kept
  so 5.x programs compile
- `getError()` returns the calling cog's first error; the steering object's returns its own, the left
  wheel's and the right wheel's
- The three hall sensors are read at one instant, so a switching transient cannot form a false hall code
- Distance readings and distance stops use the wheel's circumference to a tenth of a millimetre
- `isp_3wire_joystick` and `isp_4button_af1332` print no debug line per press; the joystick's `stop()` releases
  its analog pins
- The PWM dead-time is 260 ns on both board revisions, meeting the 250 ns minimum both board manuals specify
- Serial: commands are handled about 1 ms after arrival; a refused command replies
  `ERROR {cmd} failed: {ERR_NAME} ({code})`, and a non-decimal parameter is refused
- Serial: the Python demo sends hold as -1 / 0, and has a wrapper for every command
- The FlySky demos set deceleration from the VrB knob (1,000 to 3,000 mm/s²) beside acceleration on VrA

### Bug Fixes

- `getStatus()` reports `DS_FAULTED` and `DS_ESTOP` (serial `getstatus`: 14 and 15); a faulted or e-stopped
  motor no longer reports that it is moving
- `driveForDistance(left, right)` drives each wheel its own distance, so unequal distances turn
- `holdAtStop(false)` coasts with all bridge transistors off; a fault coasts or brakes as `holdAtStop()`
  selects; `emergencyCutoff()` brakes and latches until `clearEmergency()`
- After `clearEmergency()`, the next drive ramps up from rest; it faulted at once
- Two wheels: `getDistance()` reports the distance travelled; it reported ten times it
- `stopAfterDistance()` with `DDU_M` stops at the full distance, on both objects; it stopped at a tenth
- `isReady()` and `isStopped()` answer `FALSE` after `stop()`, and a `start()` that fails releases its pin group
- `isp_queue_serial` `stop()` stops its own receive cog; it stopped the cog numbered one lower
- `isp_flysky_rx` `readSwitch()` and `readSw3Way()` read a channel that is not a 3-position switch as OFF; it
  read as ON
- The FlySky demos no longer have a "1 rotation" switch, which read a switch the transmitter lacks and could
  turn a wheel while the sticks were disabled

### Breaking Changes

- **BREAKING**: a top-level program selects its configuration in `isp_bldc_motor_userconfig.spin2` with
  `#DEFINE CFG_SINGLE_MOTOR` (or `CFG_DUAL_MOTOR`) and a guarded `#PRAGMA EXPORTDEF` at its top; without
  them PNut-TS stops with an error naming the lines. PNut users select it in the config file instead
  ([DEVELOP.md](DEVELOP.md)).
- **BREAKING**: `driveDirection()` turns right for a positive `{direction}` and left for a negative one, as
  documented; it turned the other way. Programs that negated `{direction}` to compensate must remove the
  negation. The FlySky demos no longer invert the joystick.
- **BREAKING**: `start()` returns the started cog's id (0 to 7), or -1 when it fails; it returned the id + 1,
  or 0. This holds for the motor, steering, joystick, 4-button and HDMI debug objects. Code that tests the
  result for 0 must test for -1.
- **BREAKING**: support-object renames: `isp_flysky_rx` `swIsOn()`, `swIsOff()` and `swIsMiddle()` are now
  `isSwitchOn()`, `isSwitchOff()` and `isSwitchMiddle()`; `isp_queue_serial` `haveCommand()` and
  `haveRxString()` are now `hasCommand()` and `hasRxString()`. Programs calling them rename the calls; the
  motor and steering methods are unchanged.
- **BREAKING**: command methods return `NO_ERROR` or a negative `ERR_*` code instead of aborting on bad
  arguments. Calls that ignore the result need no change; code relying on an abort to stop a cog must check
  the result.
- **BREAKING**: `power` values run about 12 % faster on the 6.5″ motor: `power` 100 at 18.5 V is now 294 RPM.
  Code tuned to a particular speed may need its power lowered.
- **BREAKING**: `start()` refuses a pin group where no board is detected (`ERR_BOARD_NOT_DETECTED`) unless
  `BRD_REV_A` or `BRD_REV_B` is forced. Platforms whose boards are detected need no change.
- **BREAKING**: `start()` refuses a motor that still fails a start check after retrying it
  (`ERR_START_CHECK_FAILED`). Call `setStartChecks(false)` before `start()` to start it anyway.
- **BREAKING**: `setAcceleration(rate)` and serial `setaccel` take mm/s² at the wheel rim (1 to 10,000); they
  previously passed `{rate}` to the driver as its ramp step. Code that passed a ramp step should pass the
  rate that step gave. Built-in rates: 1,000 mm/s² up, 1,470 mm/s² down.
- **BREAKING**: `setRampingValues()` and `getRampingValues()` are removed from the single-motor object (the
  steering object never had them). Use `setAcceleration()` and `setDeceleration()`, in mm/s², on either
  object or over serial (`setaccel`, `setdecel`).
- **BREAKING**: every stop takes about 0.25 s longer and runs about speed × 0.125 s further than the same
  deceleration without easing: from 1.13 m/s, about 0.57 m instead of 0.43 m (calculated). The stop limits and
  `driveForDistance()` allow for it; a plain `stopMotor()` / `stopMotors()` does not, so leave the room.

### Known Issues

- Under load, spins in place can run up to 43 % slow and speed changes arrive late; both wheels slow together,
  keeping the path
- Against an obstacle that gives way, a blocked wheel can keep pushing for several seconds before the protective
  stop latches; the push is current-limited
- The drive does not use the pack sensor's voltage yet: `getCurrent()`'s watts and the speed table assume
  the configured `DRIVE_VOLTAGE`
- `getCurrent()` does not show regenerative current
- Braking by shorted phases (`emergencyCutoff()`, `holdAtStop(true)`) is not current-limited; ramp down
  before stopping where you can, as `stopMotor()` and the stop limits do
- Speeds are characterized unloaded; under load the motor has less torque in reserve near top speed
- `setHoldLimits()`'s defaults were sized with the wheels unloaded
- `calibrate()` is not implemented
- The drive is supported at a 270 MHz system clock (`_clkfreq = 270_000_000`, as in every demo); below about
  250 MHz its timing is unproven
- The DocoEng 4,000 RPM motor is not validated for v6.0.0; v6.0.0 is validated on the 6.5″ hub motor
- The serial control path (`isp_steering_serial.spin2`, the Python host demo) is not validated on hardware
  for v6.0.0

## v5.0.2 (2025-02-21)

Consecutive distance drives, and two more board connection points.

### New Features

- Two more motor-board connection points: `PINS_P8_P23` and `PINS_P40_P55`

### Bug Fixes

- Consecutive `driveForDistance()` calls each drive their distance (#23)

### Known Issues

- Drive status reporting is not working in the base objects, so it is also reported badly over the serial
  interface
- A motor can fault under higher load conditions

## v5.0.1 (2025-02-13)

A fix for distance drives on two wheels.

### Bug Fixes

- `driveForDistance()` in the two-wheel steering object drives the requested distance
- License information is updated throughout the documentation

## v5.0.0 (2023-09-16)

Synchronized motor starts, dynamic ramping, and correct current and power.

### New Features

- Multiple motors can be started in sync with each other
- The FlySky receiver pin is configurable, in both FlySky demos

### Improvements

- Ramping is dynamic: the ramp climbs from `ramp_min` to `ramp_max` instead of running at a fixed rate
- The board revision is detected before it is used
- PWM enable and disable are reworked

### Bug Fixes

- `getCurrent()` reports the correct current and power
- DocoEng 4,000 RPM motor: direction and fault handling
- DocoEng 4,000 RPM motor: wheel-diameter handling, and the position-sense task
- The `DCS_SLOW_TO_CHG` state, stop-mode handling, `duty_min`, and the initial angle taken from the halls

### Credits

- Pull requests from TimM — thank you Tim.

## v4.2.0 (2023-08-15)

Motor object update and documentation corrections.

### Improvements

- Motor object update, and corrections throughout the documentation

## v4.1.0 (2023-08-14)

A steering-object fix.

### Bug Fixes

- `validDetectModeForChoice()` in the two-wheel steering object calls the correct underlying method

### Known Issues

- Calculation of current and power is not yet correct

## v4.0.0 (2023-04-14)

Automatic board-revision detection, full Rev B support, and fault detection.

### New Features

- Automatic detection of the board revision (Rev A / Rev B); every demo and test uses it
- Rev B board support for both motors
- Fault detection, shown on HDMI and cleared after 3 seconds
- HDMI display of steering
- Support for the larger Edge Breakout board (#64029) running two motors with HDMI
- New demo: two motors with FlySky control and HDMI debug output

### Improvements

- The DocoEng motor is re-characterized, with the best Rev B offsets applied
- Position tracking in the driver serves two-wheel steering; HDMI display field overruns are fixed
- New platform layout drawings, and FlySky wiring documentation

### Known Issues

- Calculation of current and power is not yet correct
- `validDetectModeForChoice()` in `isp_steering_2wheel.spin2` calls the wrong underlying method

## v3.0.0 (2022-08-16)

A PWM fix for better top-end drive, and the DocoEng motor re-characterized.

### Improvements

- The DocoEng motor is re-characterized at every supported voltage, with its speed limits revised
- Finer resolution in the single-motor position sense
- Documentation updated for the new motor

### Bug Fixes

- PWM generation is corrected, giving better top-end drive

### Known Issues

- Drive status reporting is not working in the base objects, so it is also reported badly over the serial
  interface
- A motor can fault at higher load conditions

## v2.1.0 (2022-07-07)

Support for a second motor: the DocoEng 24 V, 4,000 RPM BLDC motor.

### New Features

- `MOTR_DOCO_4KRPM`: the smaller DocoEng.com 24 V, 4,000 RPM motor, at the same supply voltages as the 6.5″
  hub motor ([DOCOENG_MOTOR.md](DOCOENG_MOTOR.md))

## v2.0.0 (2022-05-04)

Serial control: drive a platform from a Raspberry Pi or Arduino.

### New Features

- `isp_steering_serial.spin2`: a top-level object that drives the two-wheel steering object over serial,
  with a Raspberry Pi host example ([SERIAL-CONTROL.md](SERIAL-CONTROL.md))

### Bug Fixes

- Position tracking and reporting in `isp_steering_2wheel.spin2`

### Known Issues

- Drive status reporting is not working in the base objects, so it is also reported badly over the serial
  interface
- A motor can fault at higher load conditions

## v1.1.0 (2022-04-27)

Emergency stop, and a gentler spin-up.

### New Features

- Emergency stop methods in `isp_bldc_motor.spin2` and `isp_steering_2wheel.spin2`
- FlySky switch SwD is mapped to emergency stop

### Improvements

- The spin-up ramp starts slower, then speeds up: better traction on loose surfaces, with a faster climb
- FlySky control mapping documented in the README

### Known Issues

- Position tracking is not working in `isp_steering_2wheel.spin2`
- Drive status reporting is not working in the base objects (motor and steering)

## v1.0.1 (2022-04-02)

**Initial release.** Spin2/PASM2 objects that drive BLDC hub motors through the Parallax 64010 Universal
Motor Driver board from a Propeller 2: a single-motor object built on Chip Gracey's BLDC driver, a
two-wheel steering object for mobile platforms, and demos including FlySky remote control.
