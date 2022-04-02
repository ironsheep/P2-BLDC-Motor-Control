# P2-BLDC-Motor-Control - Developing a P2 Application interacting with the new motor objects

Add a BLDC drive control subsystem to your own project!

![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

## Table of Contents

On this Page:

- [Add Steering and Config Objects to your P2 Project](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#add-steering-and-config-objects-to-your-p2-project) 
- [Make calls to steering or motor object to drive platform](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DEVELOP.md#and-youre-off--add-your-own-motor-control-code) 

Additional pages:

- [Main Page](https://github.com/ironsheep/P2-BLDC-Motor-Control) - Return to the top of this repos
- [Drawings](DRAWINGS.md) - Files (.dwg) that you can use to order your own platform inexpensively
- [To-scale drawings](DOCs/bot-layout.pdf) of possible rectangular and round robotic drive platforms for Edge Mini Break and JonnyMac P2 Development boards

---

## Add Steering and Config Objects to your P2 Project

The objects provided by this project read a user configuration to determine how to cinfiugure themselves.  You'll first adjust this file to describe your setup.  Then you'll include the motor/steering objects you need into your top-level file.

Lastly you'll start the objects and then add your drive code and any sensor code you wish to use.

### Adjust config file to your desired configuration

Edit the user configuration file and adjust the settings to describe the configuration you will be using.

Here's the Author's two-wheel setup:

```
' -------------------------------------------------------------------
' AUTHORs  TEST configuration (dual Motor)
' -------------------------------------------------------------------
{
    ' using Mini Edge Breakout
    LEFT_MOTOR_BASE = PINS_P0_P15
    RIGHT_MOTOR_BASE = PINS_P16_P31

    DRIVE_VOLTAGE = PWR_12V

    MOTOR_DIA_IN_INCH = 6.5   ' 6.5 inches (floating point constant)
    
'}
```

You will need to configure one of:

- `ONLY_MOTOR_BASE` =  &nbsp; {pinBaseConstant}  &nbsp;  -OR-
- `LEFT_MOTOR_BASE` = &nbsp; {pinBaseConstant} and `RIGHT_MOTOR_BASE` = {pinBase}

and then set:

- `DRIVE_VOLTAGE` =  &nbsp; {voltageConstant}

as well as:

- `MOTOR_DIA_IN_INCH` = &nbsp; {wheelDiameterInInches}  (loating point value)

**NOTE:** *The constants you can use for {pinBaseConstant} and {voltageConstant} are provided in the file for you.*

Save your changes and you are ready to start adding the driver to your code.

### Include Project Objects

Yuu now need to select objects based on if you are a one-wheel or two-wheel confuration.

#### Using Two Motor Objects

- isp\_bldc\_motor_userconfig.spin2 - your configuration (motor connections, power, wheel size
- isp\_steering_2wheel.spin2 - the steering object which include the motor objects

You simply include them with something like:

```script
OBJ { Objects Used by this Object }

    user    :    "isp_bldc_motor_userconfig"     ' project motor, power configuration
    wheels  :    "isp_steering_2wheel"           ' steering and motor drivers and tracking
```

#### Start the Objects

Starting the wheels object in Spin2 is also pretty simple:

```script

PUB main() | eOpStatus, nIdx, nCollId, eRxQStatus, eCmdId, tmpVar

    ' start our motor drivers (left and right)
    wheels.start(wheels.PINS_P0_P15, wheels.PINS_P16_P31, wheels.PWR_12V)

    ' just don't draw current at stop
    wheels.holdAtStop(false)

  ... and do your app stuff from here on ...
  
   wheels.stop()   ' if you wish to shutdown COGs and release motor pins
   
```


#### Using A Single Motor Object

- isp\_bldc\_motor_userconfig.spin2 - your configuration (motor connections, power, wheel size
- isp\_bldc_motor.spin2 - the motor object which includes a single motor tracking object

You simply include them with something like:

```script
OBJ { Objects Used by this Object }

    user    :    "isp_bldc_motor_userconfig"     ' project motor, power configuration
    wheel   :    "isp_bldc_motor"                ' motor driver
```

#### Start the Objects

Starting the wheel and tracking objects in Spin2 is also pretty simple:

```script

PUB main() | motorCog, senseCog, basePin, voltage

    basePin := wheel.validBasePinForChoice(user.ONLY_MOTOR_BASE)
    voltage := wheel.validVoltageForChoice(user.DRIVE_VOLTAGE)

    if basePin <> wheel.INVALID_PIN_BASE and voltage <> wheel.INVALID_VOLTAGE
        ' start our single motor driver
        motorCog := wheel.start(basePin, voltage)
 
        ' for single motor let's start the single motor sense task
        senseCog := wheel.startSenseCog()

        ' just don't draw current at stop
        wheel.holdAtStop(false)

  ... and do your app stuff from here on ...
  
        wheel.stop()   ' if you wish to shutdown COGs and release motor pins
   
```


### And you're off!  Add your own motor control code

You are now at the `... and do your app stuff from here on ...` section of this page.
From here on, just use any of the Public Methods found in the [Steering and Motor control](DRIVE-OBJECTS.md) interface description.  

**Remember:** if you are two wheeled you are calling methods of the [**isp\_steering_2wheel.spin2**](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DRIVE-OBJECTS.md#the-2-wheel-steering-object-public-interface) object `wheels.*` and if you are a single wheel then you are calling methods of the [**isp\_bldc_motor.spin2**](https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/main/DRIVE-OBJECTS.md#the-motor-object-public-interface) object `wheel.*`.

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

Copyright © 2022 Iron Sheep Productions, LLC. All rights reserved.

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765

