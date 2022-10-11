# P2-BLDC-Motor-Control - Adding support for a new motor

We just had the occasion to add support for a new BLDC Motor. This page helps us remember what we need to do to qualify the new motor.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Motors Supported

The motor currently supported by this driver (at the time of this writing):

| Category                   | Value          | Description                                      |
| -------------------------- | -------------- | ------------------------------------------------ |
| **-- 6.5" Wheel --**       |                | the Parallax Hoverboard-like motors              |
| Hall Tics per Revolution   | 90 ticks       |
| Degrees per hall tick      | 4 degrees      |
| Ticks per hall-cycle       | 6 ticks        | FWD (CW): 1-3-2-6-4-5</br>REV (CCW): 1-5-4-6-2-3 |
| Hall-cycles per Revolution | 15 hall-cycles |
| Degrees per Hall-cycle     | 24 degrees     |
| Magnets                    | 30 poles       |

The new Motor we're adding:

| Category                               | Value         | Description                                      |
| -------------------------------------- | ------------- | ------------------------------------------------ |
| **-- docoEng.com 4k RPM 24v motor --** |               | the new Parallax small motor                     |
| Hall Tics per Revolution               | 24 ticks      |
| Degrees per hall tick                  | 15 degrees    |
| Ticks per hall-cycle                   | 6 ticks       | FWD (CW): 1-5-4-6-2-3</br>REV (CCW): 1-3-2-6-4-5 |
| Hall-cycles per Revolution             | 4 hall-cycles |
| Degrees per Hall-cycle                 | 90 degrees    |
| Magnets                                | 8 poles       |

## Cabling of new Motor

We're adding the DocoEng.com BLDC motor - 4,000 RPM, 24V to the driver. The motor [specifications are here](./DOCs/DOCOMotor.pdf). These are the connections I used. I ended up cutting off the end of some female connector wires and soldering them to the motor wires to make a connector. While most of use would simply solder on connectors, I was on a road trip and this is what I had access to. ;-)

| Wire Color            | Purpose      | Adapter Wire Color           | board Connector |
| --------------------- | ------------ | ---------------------------- | --------------- |
| **Hall Sensor Wires** |              | _- 26 AWG wires (thinner) -_ |
| Red                   | +5V Hall Pwr | adapt Red                    | Hall IN: +v     |
| Yellow                | Hall U       | adapt Yellow                 | Hall IN: U      |
| Green                 | Hall V       | adapt Green                  | Hall IN: V      |
| Blue                  | Hall W       | adapt Orange                 | Hall IN: W      |
| Black                 | Ground       | adapt Brown                  | Hall IN: +v     |
| **Motor Drive Wires** |              | _- 20 AWG wires -_           |
| Yellow                | Phase U      | -no adapter-                 | Motor out U     |
| Green                 | Phase V      | -no adapter-                 | Motor out V     |
| Blue                  | Phase W      | -no adapter-                 | Motor out W     |

**FIGURE 1**: _This is the cabling per the table above._

![coffee](images/new-motor-connect.jpg)

**FIGURE 2**: _The new motor hooked up._

![coffee](images/motor-hooked-up.jpg)

\*NOTE: the electrical tape "flag" so i can tell relative position of shaft during movement.

## Process of adding a new motor

- Determine geometry of motor
- Validate hall sequence
- Add new enum value for motor
- Associate tables with new motor constant (creating new tables if needed)
- Determine new fwd/rev offset constants that yield lowest current draw at fixed speed/rpm
- Adjust motor position sense code to new motor hall geometry so rotation positon tracking are correct for the motor
- Determine and add max request values for each voltage we support
- Validate all your work, when it's complete, share it with us!

## What Driver needs to know about a motor

_I'm writing this section after the v3.0.0 release is completed. This release (v3.0.0) finished the implementation of the new docoEng Motor but leaves unfinished the re-evaluation of the new upper-limits possible with the 6.5" motor. In this release we fixed a BUG with PWM generation at higher RPMs. Therefore the 6.5" motor should be capable of running better than the limits we fixed in the driver. Read on as this will soon make sense._

Today our driver cannot detect the "hall order" or the "mechanical offset of hall sensors in degrees" at runtime. So, we build these values into our driver.

Also, our upper level API for the motor allows us to request power settings of 0-100% and it returns rotation count as Hall Tics, Degrees or Rotations. In order for this to work we have knowledge of hall cycles per rotation and the upper limits achivable for a given motor if we drive it at a given voltage also built into this driver.

Let's explore each of these further. But wait, if your are really adding a new motor let's address one thing that will make the remaining steps easier. That is you will need an Identifier for your new motor.

### Step 0 - Name your Motor

We have two identical enum's which contain our motor identifiers.
This should be thought of as the single source for motor identifiers used in this driver code. When you add a new motor you will come up with a name that is not generic that will describe your motor and that others will recognize as the type of motor you are adding. You will then make the identical changes to both of these lists.

Here's what the lists look like as of V3.0.0:

At the top of file: `isp_bldc_motor_userconfig.spin2`:

```spin2
    ' Names of supported Motors
    #0, MOTR_6_5_INCH, MOTR_DOCO_4KRPM
```

And at the top of file: `isp_bldc_motor.spin2`:

```spin2
    ' Names of supported Motors
    #0, MOTR_6_5_INCH, MOTR_DOCO_4KRPM
```

You will change these to look like:

```spin2
    ' Names of supported Motors
    #0, MOTR_6_5_INCH, MOTR_DOCO_4KRPM, {YOUR_NEW_MOTOR_IDENTIFER}
```

(replacing `YOUR_NEW_MOTOR_IDENTIFER}` with your name and remembering to do this in both places.

**NOTE:** _I'll be adding runtime checks to validate that these two lists are in the same order and contain the same set of values in an upcoming release. For now, please be careful to make sure both lists are identical._

### Low-Level: Hall Order

Our Hall sensors are 3 bits-wide yielding the values 1-6 with single-bit changes as we move from one value to the next. This leaves two possible orders [1,3,2,6,4,5 or 1,5,4,6,2,3]. While I showed these orders starting from 1, you will notice that these are simply reversed and offset from one another when shown this way.

A given motor works with one of these orders as forward while the other is reverse. What's "fun" is that which is forward or reverse appear to be up to the manufacturer. As you've seen earlier in this document, our two motors are different in the order they use. _We are two-for-two so far._

Symptoms when bad hall order: the motor may not turn at all, or may just move a short distance before stopping. Another, we've seen is that the motor will work in one direction (fwd or rev) but will not work at all in the other direction. So, if you see these types of things... recheck your hall order.

#### Driver Startup: Hall Order

When the user selects the motor type in their config file this tells our driver at runtime which hall sequence the motor needs and the appropriately ordered tables are copied into the driver image before the driver cog is started.

#### Refer to isp_bldc_motor.spin2:start() for Hall order setup

Refer to this code in the start() method. When adding a new motor you'll to add a value for your new motor which moves the correct table for your motor into place within the driver image.

```spin2
    ' new build up our hall angle table for specific motor
    case user.MOTOR_TYPE
        MOTR_DOCO_4KRPM:
            longmove(@hall_angles, @hltbAngl4k, 16)
        MOTR_6_5_INCH:
            longmove(@hall_angles, @hltbAngles, 16)
        other:
            ' default to our 6.5" motor form
            longmove(@hall_angles, @hltbAngles, 16)
```

### Low-Level: Mechanical offset of Hall Sensors

While I'm learning as I understand it at as of this writing the each motor design has an offset from the start of a hall cycle vs. the start of the mechanical cycle. (are my terms correct here?) This offset is unique to each motor design.

Symptoms when offsets are incorrect are of two forms: the motor will not turn or will fault immediately. Alternatively, if set badly the motor could draw full "Amps" of power instead of the "10th's or 100th's of amps" it might need to cause rotation. While likely all motors when driven at their highest RPMs will draw full Amps we are talking one or two orders of magnatitude in greater current draw when this value gets set badly. Simply put you are tring to find a value for your motor which allows it work in both directions at the highest RPMs without faulting and while drawing the least amount of current possible for your motor.

#### Driver Use: Mechanical offset

The offset values are passed to the driver as the `offset_fwd` and `offset_rev` values.

#### Refer to isp_bldc_motor.spin2:start() for Mechanical offset setup

Refer to this code in the `start()` method. You can see the method `offsetsForMotor()` being called to get values.

When adding a new motor you'll adjust the case statement within `offsetsForMotor()` to add value(s) for your new motor which assign the correct offset in degrees for your motor at the current user power voltage.

```spin2
    ' configure our offsets for specific motor
    fwdDegrees, revDegrees := offsetsForMotor(user.MOTOR_TYPE)
    offset_fwd  := fwdDegrees frac 360
    offset_rev  := revDegrees frac 360

```

When you get into the `offsetsForMotor()` routine... if things look a little wonky as you compare what's done for our two motors... just know that we took more time experimenting with the new motor to see how much change we get if we play with offets for each of our supported voltages. We left what we learned in the code.

### Upper-Level: Hall-cycles/Rotation, °/Hall Tick

The driver needs to know two values specific to your new motor in order for it to provide accurate feedback. More often than not you will not find this information in the motor docs. It is pretty simple to determine these numbers after you first connect your motor. Our single motor demo drives an HDMI display showing the hall sensor value so leave the motor drive power off, run the demo and then turn the shaft and record what you see. Likewise, put a simple marker on the shaft so you can tell when you have turned one rotation and count the number of hall ticks you saw during the one rotation. Simple, remember these and update the code and that's pretty much all you need for this. However, please be accurate!

Symptoms when these values are not correct. All your speed and rotation-rate feedback from the driver will be incorrect. Likewise, if you have a wheel on your motor and have specified its diameter to the driver all your distance reporting from the driver will also be incorrect.

#### Rotation Task use: Hall Cycles / Rotation

The hall geometry values are passed to the position tracking task as the degrees per tick `degrPerTic` and `hallTicsPerRotation` values.

#### Refer to isp_bldc_motor.spin2:start() for Hall Cycles / Rotation setup

Refer to this code in the `start()` method. You can see the method `hallTicInfoForMotor()` being called to set values.

When adding a new motor you'll adjust the case statement within `hallTicInfoForMotor()` to add value(s) for your new motor which assign the degrees per hall tick, as well as the number of hall ticks for a single full rotation.

```spin2
    degrPerTic, hallTicsPerRotation := hallTicInfoForMotor()
```

### Upper-Level: Max Speed for Given Power

For all of our BLDC motors you will see that for a given voltage used to drive the motor you will find that there is a maximum RPM that can be achieved. The "fun" part is that you can ask the motor to go faster but it will still max out at this same MAX RPM but it will continue to consume greater ammounts of current trying.

So, we optimize this system as if it were a battery powered system. As we add new motors we do our best to characterize the new motor to learn what these upper limits are. We back off the number we find, lowering it as far as possible while still achieveing the same top RPM. The number we record then represents the highest RPM we can achieve with the motor but at the lowest current possible while still achieving that RPM.

To sum up... the numbers we record for a given power then give us the 100% setting we use when the user calls for 100% power. It is also the value we use to scale the range so that value in the 0-100% range all get correctly representative values.

#### Refer to isp_bldc_motor.spin2:start() for Given Power setup

Refer to this code in the `start()` method. You can see the method `confgurePowerLimits()` being called to set values.

When adding a new motor you'll adjust the case statement within `confgurePowerLimits()` to add value(s) for your new motor which assign the correct upper limits for your motor at each of our supported voltages.

```spin2
    confgurePowerLimits(user.DRIVE_VOLTAGE)
```

### When you've finished

When you have finished characterizing your motor from all four of these perspectives and have updated your driver with your findings you should have really satisfying control over your motor using our rather extensive set of motor control methods.

Enjoy playing with this new capability you've added but, please remember to share what you've learned back to the author(s) of this repository! See [Contributing](/CONTRIBUTING.md) for ways you can best help us add your changes. This way we can keep growing this driver's coverage of motors we like to use!

## End for now...

This is what I can remember for now and should be all the critical areas.

If I find anything here I missed I'll update this list. Likewise, if you find something related to adding a new motor that I haven't addressed herein, please let me know and I'll get something added. And thank you, in advance, for helping me make this documentation better for all of us.

-Stephen
(last updated: 13 Sep 2022)

---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Disclaimer and Legal

> _Parallax, Propeller Spin, and the Parallax and Propeller Hat logos_ are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Copyright © 2022 Iron Sheep Productions, LLC. All rights reserved.

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge
[license-shield]: https://camo.githubusercontent.com/bc04f96d911ea5f6e3b00e44fc0731ea74c8e1e9/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f69616e74726963682f746578742d646976696465722d726f772e7376673f7374796c653d666f722d7468652d6261646765
