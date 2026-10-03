# P2-BLDC-Motor-Control - Developing a P2 Application interacting with the new motor objects

Add a BLDC drive control subsystem to your own project!

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Table of Contents

On this Page:

*Follow these steps to add motor control to your project:*

- [Download the latest release .zip file](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#download-the-latest-release-demo-archive-setzip-file) - get project files
- [Adjust config file to your desired configuration](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#adjust-config-file-to-your-desired-configuration) 
- [Include project objects in your top-object-file](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#include-project-objects-in-your-top-object-file)
- [Make calls to steering or motor object to drive your platform](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#and-youre-off--add-your-own-motor-control-code) 
- [Driving a distance, and waiting for it to finish](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#driving-a-distance-and-waiting-for-it-to-finish) - and backing up
- [Tuning the ramp for your robot's mass](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#tuning-the-ramp-for-your-robots-mass) - acceleration, deceleration and stopping distance
- [Checking for errors](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#checking-for-errors)

Additional pages:

- [Main Page](https://github.com/ironsheep/P2-BLDC-Motor-Control) - Return to the top of this repos
- [Drawings](DRAWINGS.md) - Files (.dwg) that you can use to order your own platform inexpensively
- [To-scale drawings](DOCs/bot-layout.pdf) of possible rectangular and round robotic drive platforms for Edge Mini Break and JonnyMac P2 Development boards

---

## Download the latest release archive-set .zip file

Go to the project [Releases page](https://github.com/ironsheep/P2-BLDC-Motor-Control/releases) and expand the **Assets** heading. Each release carries three archive sets: **demo-1mot-archive-set.zip** (a single motor), **demo-2mot-archive-set.zip** (a two-wheel platform) and **serial-control-archive-set.zip** (driving a platform from a Raspberry Pi or Arduino). Download the one for your platform, unpack it and move the files into your project.

The objects provided by this project read a user configuration to determine how to configure themselves.  You'll first adjust this file to describe your setup.  Then you'll include the motor/steering objects you need into your top-level file.

Lastly you'll start the objects and then add your drive code and any sensor code you wish to use.

**Budget your cogs.** The drive uses **2 cogs** for a single motor and **3 cogs** for a two-wheel platform, leaving 6 or 5 for your application. See [Objects and cogs](DRIVE-OBJECTS.md#objects-and-cogs).

### Adjust config file to your desired configuration

Edit the user configuration file, **isp\_bldc\_motor\_userconfig.spin2**, and adjust the settings to describe the configuration you will be using.

The file holds **two configurations**, and your top-level program chooses one of them with a few lines at the very top of its file (see [Include Project Objects](#include-project-objects-in-your-top-object-file) below):

- `CFG_SINGLE_MOTOR` — one motor, driven by `isp_bldc_motor` directly
- `CFG_DUAL_MOTOR` — a two-wheel platform, driven by `isp_steering_2wheel`

Edit the configuration your program selects. As shipped, the two-wheel configuration is:

```
    MOTOR_TYPE = MOTR_6_5_INCH

    LEFT_MOTOR_BASE = PINS_P16_P31
    RIGHT_MOTOR_BASE = PINS_P32_P47

    DRIVE_VOLTAGE = PWR_18p5V

    WHEEL_DIA_IN_INCH = 6.5   ' 6.5 inches (floating point constant)

    LEFT_BOARD_TYPE = BRD_AUTO_DET
    RIGHT_BOARD_TYPE = BRD_AUTO_DET
```

In a configuration you set:

- `ONLY_MOTOR_BASE` =  &nbsp; {pinBaseConstant}  &nbsp;  -OR-
- `LEFT_MOTOR_BASE` = &nbsp; {pinBaseConstant} and `RIGHT_MOTOR_BASE` = {pinBaseConstant}

and then set your motor type:

- `MOTOR_TYPE ` =  &nbsp; {motorTypeConstant}

and then set:

- `DRIVE_VOLTAGE` =  &nbsp; {voltageConstant}

as well as:

- `WHEEL_DIA_IN_INCH` = &nbsp; {wheelDiameterInInches}  (floating point value; 0.0 when no wheel is attached)

and the board detection, one of:

- `ONLY_BOARD_TYPE` = &nbsp; {detectModeConstant}  &nbsp;  -OR-
- `LEFT_BOARD_TYPE` = &nbsp; {detectModeConstant} and `RIGHT_BOARD_TYPE` = {detectModeConstant}

A motor board uses its base pin and the 15 pins above it, so the two motors of a two-wheel platform need pin groups that do not overlap (for example `PINS_P16_P31` and `PINS_P32_P47`, or `PINS_P0_P15` and `PINS_P16_P31`). The configuration checks this when you compile. A base that is not one of the `PINS_*` groups, or two groups that share pins, stops the compile with an error like:

```
isp_bldc_motor_userconfig.spin2:190:error:Divide by zero (m145)
```

The line it names is a `CHECK_` line below your settings, and the comment on that line says what to change. `start()` refuses such a group at run time too, for a program built another way.

Use `BRD_AUTO_DET` unless you have a reason not to. With it, `start()` refuses a pin group where it cannot detect a board, because without the board's revision the driver has no current limit for it. `BRD_REV_A` or `BRD_REV_B` forces a revision; forcing one that does not match your hardware will cause the driver to not work.

As shipped, the single-motor configuration is:

```
    MOTOR_TYPE = MOTR_DOCO_4KRPM

    ONLY_MOTOR_BASE = PINS_P16_P31

    DRIVE_VOLTAGE = PWR_12p0V

    WHEEL_DIA_IN_INCH = 0.0   ' no wheel attached (floating point constant)

    ONLY_BOARD_TYPE = BRD_AUTO_DET
```

**NOTE:** *The constants you can use for {pinBaseConstant}, {motorTypeConstant}, {voltageConstant} and {detectModeConstant} are provided at the top of the file for you, and more example settings are below the two configurations. Which voltages each motor supports is in [MOTOR_CHOICE.md](MOTOR_CHOICE.md).*

Save your changes and you are ready to start adding the driver to your code.

## Include Project Objects in your top-object-file

You now need to select objects based on if you are a one-wheel or two-wheel confuration.

**First, select your configuration.** Put these lines at the very top of your top-level file, before anything else. They choose which of the two configurations in `isp_bldc_motor_userconfig.spin2` is compiled. With PNut-TS, a program without them does not compile, and the error names these lines.

```script
' a two-wheel program:
#DEFINE CFG_DUAL_MOTOR
#IFDEF __PNUT_TS__
#PRAGMA EXPORTDEF CFG_DUAL_MOTOR
#ENDIF

' -- OR -- a single-motor program:
#DEFINE CFG_SINGLE_MOTOR
#IFDEF __PNUT_TS__
#PRAGMA EXPORTDEF CFG_SINGLE_MOTOR
#ENDIF
```

`#PRAGMA EXPORTDEF` is what carries your program's choice into the configuration file. It is a PNut-TS feature, so it sits inside `#IFDEF __PNUT_TS__`, a symbol only PNut-TS defines; that keeps the same file buildable with PNut.

### Building with PNut

PNut has `#DEFINE` and `#IFDEF`, but a `#DEFINE` reaches only the file it is in, and PNut has no `#PRAGMA EXPORTDEF` to carry it further. So with PNut, the configuration file cannot see your program's choice, and you make the choice there instead. Do **one** of these:

- **Edit the configuration file.** Near the top of `isp_bldc_motor_userconfig.spin2`, find these lines, and remove the leading `'` from the **one** that matches your program:

    ```script
    #IFNDEF __PNUT_TS__
    '#DEFINE CFG_SINGLE_MOTOR
    '#DEFINE CFG_DUAL_MOTOR
    #ENDIF
    ```

    PNut-TS skips these lines, so they can never contradict a program built with PNut-TS. The catch: with PNut, every program you build from that folder gets the same configuration, so keep single-motor and two-wheel programs in separate folders.

- **Or define the symbol on PNut's command line**, and leave the files unchanged: `-D CFG_SINGLE_MOTOR` or `-D CFG_DUAL_MOTOR`.

If you do neither, PNut stops with an error about an undefined symbol such as `MOTOR_TYPE`: that is the configuration file with no configuration selected.

*The PNut path follows the P2 Knowledge Base's documented behaviour of PNut's preprocessor; we build and test with PNut-TS.*

### Using Two Motor Objects

- isp\_bldc\_motor_userconfig.spin2 - your configuration (motor connections, power, wheel size)
- isp\_steering_2wheel.spin2 - the steering object which include the motor objects

You simply include them with something like:

```script
#DEFINE CFG_DUAL_MOTOR
#IFDEF __PNUT_TS__
#PRAGMA EXPORTDEF CFG_DUAL_MOTOR
#ENDIF

OBJ { Objects Used by this Object }

    user    :    "isp_bldc_motor_userconfig"     ' project motor, power configuration
    wheels  :    "isp_steering_2wheel"           ' steering and motor drivers and tracking
```

#### Start the Two-motor Objects

Starting the wheels object in Spin2 is also pretty simple:

```script

PUB main() | frontCog, eError, eLeftError, eRightError

    ' start our motor drivers (left and right) and the front cog that serves them: 3 cogs
    frontCog := wheels.start(user.LEFT_MOTOR_BASE, user.RIGHT_MOTOR_BASE, user.DRIVE_VOLTAGE, user.LEFT_BOARD_TYPE, user.RIGHT_BOARD_TYPE)
    if frontCog < 0
        ' start() refused: getError() says why, and which wheel
        eError, eLeftError, eRightError := wheels.getError()
        debug("motors did not start: ", sdec_long(eError), sdec_long(eLeftError), sdec_long(eRightError))
        return

    ' just don't draw current at stop
    wheels.holdAtStop(false)

  ... and do your app stuff from here on ...
  
   wheels.stop()   ' if you wish to shutdown COGs and release motor pins
   
```

### Using A Single Motor Object

- isp\_bldc\_motor_userconfig.spin2 - your configuration (motor connections, power, wheel size)
- isp\_bldc_motor.spin2 - the motor object

You simply include them with something like:

```script
#DEFINE CFG_SINGLE_MOTOR
#IFDEF __PNUT_TS__
#PRAGMA EXPORTDEF CFG_SINGLE_MOTOR
#ENDIF

OBJ { Objects Used by this Object }

    user    :    "isp_bldc_motor_userconfig"     ' project motor, power configuration
    wheel   :    "isp_bldc_motor"                ' motor driver
```

#### Start the Single-motor Object

Starting the motor object in Spin2 is also pretty simple. `start()` launches everything the motor needs, the driver and its front cog: 2 cogs.

```script

PUB main() | motorCog

    ' start our single motor driver and its front cog
    motorCog := wheel.start(user.ONLY_MOTOR_BASE, user.DRIVE_VOLTAGE, user.ONLY_BOARD_TYPE)
    if motorCog < 0
        ' start() refused: getError() says why
        debug("motor did not start: ", sdec_long(wheel.getError()))
        return

    ' just don't draw current at stop
    wheel.holdAtStop(false)

  ... and do your app stuff from here on ...
  
    wheel.stop()   ' if you wish to shutdown COGs and release motor pins
   
```

`start()` checks the pin group, voltage and detection mode itself, and refuses with the reason in `getError()`. The `valid*ForChoice()` methods are there if you want to check a value before you start.

### And you're off!  Add your own motor control code

You are now at the `... and do your app stuff from here on ...` section of this page.
From here on, just use any of the Public Methods found in the [Steering and Motor control](DRIVE-OBJECTS.md) interface description.  

**Remember:** if you are two wheeled you are calling methods of the [**isp\_steering_2wheel.spin2**](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DRIVE-OBJECTS.md#the-2-wheel-steering-object-public-interface) object `wheels.*` and if you are a single wheel then you are calling methods of the [**isp\_bldc_motor.spin2**](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DRIVE-OBJECTS.md#the-motor-object-public-interface) object `wheel.*`.

**Your settings are kept.** `setMaxSpeed()`, `setMaxSpeedForDistance()`, `holdAtStop()`, `setAcceleration()`, `setDeceleration()` and (motor object) `setForwardIsReverse()` may be called before `start()`, and are kept across `stop()` and `start()`. The protective settings, `setFaultResponse()`, `setHoldLimits()` and `setCommandTimeout()`, need a running motor, and every `start()` restores their defaults, so set them after each `start()`. See [Settings start() keeps](DRIVE-OBJECTS.md#settings-start-keeps).

### Driving a distance, and waiting for it to finish

`driveForDistance()` drives forward and brings the wheels to rest at the distance, counted from the call. To wait for it, poll `isMoveDone()` **with a bound**, then ask `getStopReason()` why it ended:

```script
    eError := wheels.driveForDistance(24, 24, wheels.DDU_IN)
    if eError == wheels.NO_ERROR
        startMs := getms()
        repeat until wheels.isMoveDone() or (getms() - startMs >= 10_000)
            waitms(10)
        if wheels.isMoveDone() == false
            wheels.stopMotors()                         ' not over in time: end it yourself
        eLeftReason, eRightReason := wheels.getStopReason()   ' SR_AT_LIMIT when the distance was reached
```

`isMoveDone()` is TRUE once the wheels are at rest with nothing commanded, and at once on a fault, an emergency stop or a protective stop, so the wait cannot hang on one of those. (`isStopped()` alone never becomes TRUE on a fault or an emergency stop.)

**Backing up a distance.** `driveForDistance()` is forward only. To back up, drive in reverse and arm a distance limit:

```script
    wheels.driveAtPower(-40, -40)                       ' drive in reverse...
    wheels.stopAfterDistance(24, wheels.DDU_IN)         ' ...and bring the platform to rest 24 in from here
```

These are **two calls, not one atomic move**: the platform is already reversing when the limit is armed, and a limit counts from the moment it is armed. Make the calls the other way round (`stopAfterDistance()` first, at rest, then `driveAtPower(-40, -40)`) and the limit counts from before the platform moves. See [Backing up a distance](DRIVE-OBJECTS.md#backing-up-a-distance).

**The odometer is total travel.** `getDistance()` and `getRotationCount()` count every tick each wheel turns, forward and back, since the last `resetTracking()` or `start()`; nothing else resets them. Each distance or rotation limit counts only its own travel, from when it was armed.

### Tuning the ramp for your robot's mass

The built-in ramp suits a light platform: it speeds up at 1,000 mm/s² (about 0.1 g) and slows and stops at 1,470 mm/s² (roughly 0.15 g). Every ramp is jerk-limited: its acceleration eases in from zero over 250 ms (`RAMP_TAU_MS`) and back out as the new speed arrives, so no start, speed change, reversal or stop begins or ends with a jolt, and a reversal passes through zero in one continuous ramp. The easing is fixed; the rates are yours. A speed raised while a wheel is still slowing dips briefly (about 0.3 s) before it climbs, because the ramp unwinds the slow-down first. A heavier or taller robot usually wants gentler rates, and you set the two ends apart, in mm/s² at the wheel rim: `setAcceleration(rate)` for speeding up and `setDeceleration(rate)` for slowing down and every stop. Both may be set before `start()` and are kept across it, and `getAcceleration()` and `getDeceleration()` read them back.

```script
    wheels.setAcceleration(600)                         ' ease a heavy robot into motion
    wheels.setDeceleration(900)                         ' and stop it more gently than the built-in 1,470
```

Lower the rates when the wheels slip on starts or stops (above about half of *g*, 5,000 mm/s², most tyres let go), or when a tall robot pitches or tips as it stops. A rate the motor cannot deliver for your robot's mass is not a fault: the ramp eases its acceleration off until the rotor catches up, so the robot just speeds up or stops less sharply than asked. Remember what the deceleration costs: **the stopping distance is about speed² ÷ (2 × rate) + speed × 0.125 s**. The first part is the steady deceleration, and halving the rate doubles it; the second is the 250 ms easing, and the rate does not change it (1 m/s at 900 mm/s² takes about 0.56 + 0.13 ≈ 0.68 m, and about 1.36 s). These figures are derived from the driver's arithmetic and not yet measured on a robot. `stopAfterDistance()`, `stopAfterRotation()`, `stopAfterTime()` and `driveForDistance()` allow for it themselves and still stop at their limit; a plain `stopMotors()` does not, so leave the room. `emergencyCutoff()` ignores the rate: it is always a hard stop. See [How far the motor travels while stopping](DRIVE-OBJECTS.md#how-far-the-motor-travels-while-stopping).

### Checking for errors

Every command method returns `NO_ERROR` (0) or a negative `ERR_*` code, and you may ignore it. When you do want to know, there are two ways:

**Check each call** where the answer changes what you do next:

```script
    eError := wheels.driveForDistance(24, 24, wheels.DDU_IN)
    if eError <> wheels.NO_ERROR
        debug("driveForDistance refused: ", sdec_long(eError))
```

**Or check once, after a group of calls.** Each command also records its error for the calling cog, and `getError()` returns the first one since you last asked, then clears it:

```script
    wheels.setMaxSpeed(50)
    wheels.setAcceleration(500)
    wheels.driveAtPower(40, 40)
    eError, eLeftError, eRightError := wheels.getError()
    if eError <> wheels.NO_ERROR or eLeftError <> wheels.NO_ERROR or eRightError <> wheels.NO_ERROR
        debug("a command was refused: ", sdec_long(eError), sdec_long(eLeftError), sdec_long(eRightError))
```

The codes, and what each means, are listed in [Drive Objects: Errors](DRIVE-OBJECTS.md#errors). Two latched states refuse every drive until you clear them: an emergency stop (`clearEmergency()`) and a protective stop (`clearProtectiveStop()`).

Have Fun!



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

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg


