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
- [Checking for errors](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#checking-for-errors)

Additional pages:

- [Main Page](https://github.com/ironsheep/P2-BLDC-Motor-Control) - Return to the top of this repos
- [Drawings](DRAWINGS.md) - Files (.dwg) that you can use to order your own platform inexpensively
- [To-scale drawings](DOCs/bot-layout.pdf) of possible rectangular and round robotic drive platforms for Edge Mini Break and JonnyMac P2 Development boards

---

## Download the latest release demo-archive-set.zip file

Go to the project [Releases page](https://github.com/ironsheep/P2-BLDC-Motor-Control/releases) expand the **Assets** heading to see the demo-archive-set.zip file link. Click on it to download the .zip file. Unpack it and move the files into your project. 

The objects provided by this project read a user configuration to determine how to configure themselves.  You'll first adjust this file to describe your setup.  Then you'll include the motor/steering objects you need into your top-level file.

Lastly you'll start the objects and then add your drive code and any sensor code you wish to use.

**Budget your cogs.** The drive uses **2 cogs** for a single motor and **3 cogs** for a two-wheel platform, leaving 6 or 5 for your application. See [Objects and cogs](DRIVE-OBJECTS.md#objects-and-cogs).

### Adjust config file to your desired configuration

Edit the user configuration file, **isp\_bldc\_motor\_userconfig.spin2**, and adjust the settings to describe the configuration you will be using.

Here's the Author's two-wheel setup:

```
' -------------------------------------------------------------------
' AUTHORs  TEST configuration (dual Motor)
' -------------------------------------------------------------------
{
    ' using 6.5" hub motors
    MOTOR_TYPE = MOTR_6_5_INCH

    ' using Mini Edge Breakout
    LEFT_MOTOR_BASE = PINS_P0_P15
    RIGHT_MOTOR_BASE = PINS_P16_P31

    ' using a 5s battery
    DRIVE_VOLTAGE = PWR_18p5V

    WHEEL_DIA_IN_INCH = 6.5   ' 6.5 inches (floating point constant)

    ' let the driver recognize each board's revision
    LEFT_BOARD_TYPE = BRD_AUTO_DET
    RIGHT_BOARD_TYPE = BRD_AUTO_DET
'}
```

You will need to configure one of:

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

Use `BRD_AUTO_DET` unless you have a reason not to. With it, `start()` refuses a pin group where it cannot detect a board, because without the board's revision the driver has no current limit for it. `BRD_REV_A` or `BRD_REV_B` forces a revision; forcing one that does not match your hardware will cause the driver to not work.

Here's the Author's single motor setup:

```
' -------------------------------------------------------------------
' AUTHORs  TEST configuration (docEng single Motor)
' -------------------------------------------------------------------
{
    ' using smaller docoEng.com motor
    MOTOR_TYPE = MOTR_DOCO_4KRPM

    ' using JonnyMac breakout board
    ONLY_MOTOR_BASE = PINS_P16_P31

    DRIVE_VOLTAGE = PWR_12p0V

    ' no wheel attached to this motor
    WHEEL_DIA_IN_INCH = 0.0   ' 0 inches (floating point constant)

    ONLY_BOARD_TYPE = BRD_AUTO_DET
'}
```

**NOTE:** *The constants you can use for {pinBaseConstant}, {motorTypeConstant}, {voltageConstant} and {detectModeConstant} are provided at the top of the file for you. Which voltages each motor supports is in [MOTOR_CHOICE.md](MOTOR_CHOICE.md).*

Save your changes and you are ready to start adding the driver to your code.

## Include Project Objects in your top-object-file

You now need to select objects based on if you are a one-wheel or two-wheel confuration.

### Using Two Motor Objects

- isp\_bldc\_motor_userconfig.spin2 - your configuration (motor connections, power, wheel size)
- isp\_steering_2wheel.spin2 - the steering object which include the motor objects

You simply include them with something like:

```script
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


