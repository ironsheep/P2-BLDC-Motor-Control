# P2-BLDC-Motor-Control - Serial Control

Control our single-motor and two-wheel drive objects from an RPi, an Arduino or any other serial host, over a 2-wire serial link.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

**NOTE:** *Serial control has not been re-qualified on hardware for v6.2.0; it is planned for the next minor release.*

## Table of Contents

On this Page:

- [The Project](#the-project) - what serial control is
- [Current status](#current-status) - where to find what changed in each release
- [System Diagram](#system-diagram) - what are we setting up?
- [Download the project files](#download-the-project-files) - get the latest project files
- [Configuring your RPi](#configuring-your-rpi) - one time configure your RPi
- [Wiring the Serial Connection](#wiring-the-serial-connection) - connect the RPi to the P2
- [Flashing your P2 Edge](#flashing-your-p2-edge) - flash to P2 with the drive code
- [Developing your own drive code](#developing-your-own-drive-code) - write your own drive code
- [Checking the drive's status](#checking-the-drives-status) - the status numbers and what your code should do

Additional pages:

- [Main Page](README.md) - Return to the top of this repo
- [Serial Interface of Steering Object](DRIVE-OBJECTS-SERIAL.md) - Every serial command and its reply
- [Steering and Motor control](DRIVE-OBJECTS.md) - The object public interfaces
- [Start your drive project using these objects](DEVELOP.md) - Walks through configuration and setup of your own project using these objects
- [Drawings](DRAWINGS.md) - Files (.dwg) that you can use to order your own platform inexpensively
- [To-scale drawings](DOCs/bot-layout.pdf) of possible rectangular and round robotic drive platforms for Edge Mini Break and JonnyMac P2 Development boards
- [The author's development platform](AUTHORS-Platform.md) - Overview of the robot platform used when developing and testing the code for this project

---

## The Project

Instead of using the FlySky for remote control, this document describes how to use a 2-wire serial interface to control the P2 hardware on your robot platform.

The code for this project implements an active serial receiver running on the P2 and a top-level application which listens for drive/status commands arriving via serial and then forwards the requests to the 2-wheel steering system and sends responses back over serial to the host.

## Current status

What changed in each release, serial control included, is in the project's [CHANGELOG](CHANGELOG.md).

## System Diagram

The following diagram shows the top-level serial object which hands off commands to the drive subsystem as they are received. It also shows the nested motor control and sense subsystem comprised of the two objects: steering and motor control.

```text
  Raspberry Pi: P2-BLDC-Motor-Control-Demo.py
                         │ commands, serial at 624,000 baud
  ╔══════════════════════▼═════════════════════╗
  ║ receive cog (Spin2): isp_queue_serial      ║   ← 1 cog: queues each line
  ║ holds each line the host sends             ║     the host sends
  ╚══════════════════════╤═════════════════════╝
                         │ queued lines (hub)
  ╔══════════════════════▼═════════════════════╗
  ║ isp_steering_serial: the top-level cog     ║   ← 1 cog: reads each command,
  ║ parses commands and sends the replies      ║     calls the steering object,
  ╚══════════════════════╤═════════════════════╝     and answers the host
                         │ request (hub)
  ╔══════════════════════▼═════════════════════╗
  ║ front cog (Spin2), 1 kHz                   ║   ← 1 cog, run by isp_steering_2wheel
  ║ requests · tracking · limits · protection  ║
  ╚══════════╤═════════════════════╤═══════════╝
             │ commands (hub)      │ commands (hub)
  ╔══════════▼══════════╗ ╔════════▼════════════╗
  ║ PASM2 driver cog    ║ ║ PASM2 driver cog    ║   ← 1 cog per motor
  ║ left motor          ║ ║ right motor         ║
  ╚═════════════════════╝ ╚═════════════════════╝
```

**Figure 1**: *The serial control system: five cogs. The receive cog queues what the host sends; the top-level cog reads each command, calls the steering object and sends the reply back to the host; the steering object's front cog runs both motors' driver cogs.*

The objects themselves (`isp_steering_serial`, `isp_host_serial`, `isp_queue_serial`, `isp_steering_2wheel` and `isp_bldc_motor`) run no cog of their own beyond the ones shown: their methods run in whichever cog calls them.

Video of author running the system: [Control our 2-wheel BLDC robot platform from an RPi](https://youtu.be/QF4qI9yVwWc) @ youtube

## Download the project files

Head to the BLDC Motor repository [releases page](https://github.com/ironsheep/P2-BLDC-Motor-Control/releases) and download the `serial-control-archive-set.zip` file from the Assets section of the latest release. *(only present in v2.0.0 and later releases)*

Create a working directory and unpack this .zip there. It holds one folder, `serial-control-archive-set/`, with two folders inside: `p2Src/`, the P2 project files, and `pythonSrc/`, the RPi side files. Each has a `_README_.txt` saying what it holds. We'll use all of these files in later steps. Meanwhile, let's set up your RPi.

## Configuring your RPi

Setting up your RPi is nearly the same as we did for setting up the RPi for P2 IoT Gateway use.

But, first, if you are configuring a bare new RPi then do: [Setting up your 1st Raspberry Pi](https://github.com/ironsheep/P2-RPi-IoT-gateway/blob/main/RPI-SETUP.md)

If you have a well set up RPi and just need to configure it for use in this context then do the following.

First install the two Python packages the script needs, `pyserial` and `colorama`.

### Packages for Ubuntu, Raspberry pi OS, and the like

```bash
sudo apt-get install python3 python3-serial python3-colorama
```

That is all the script needs; there is no `pip` step on these systems. (Current Raspberry Pi OS refuses a system-wide `sudo pip3 install`, so the packages come from `apt`.)

### On any other system

Install the packages into a Python virtual environment, from the folder you put the script in (next step). On a Debian-based system the `venv` module comes in its own package, `python3-venv`.

```bash
python3 -m venv .venv                    # make a private Python environment here
.venv/bin/pip install -r requirements.txt   # pyserial and colorama
```

Then run the script with `.venv/bin/python3 P2-BLDC-Motor-Control-Demo.py` instead of `./P2-BLDC-Motor-Control-Demo.py`.

### Finish the project install on the RPi

You need to select a location to install your platform-drive python script.

If you were installing in say your home directory/projects/ it might look something like this:

```bash
cd<return>  # ensure you are in home directory

mkdir -p ~/projects/platform-drive    # make new directory (inclu. ~/projects/ if it doesn't exist)

cd ~/projects/platform-drive
```

Head back to the folder where you unpacked the `serial-control-archive-set.zip` file. Copy the files from its `serial-control-archive-set/pythonSrc/` folder into this new directory on your RPi: the demo script `P2-BLDC-Motor-Control-Demo.py` and its `requirements.txt`. If you installed the packages with `apt` above, your system prep is done. Otherwise, run the virtual-environment step above in this folder now.

## Wiring the Serial Connection

The **P2-BLDC-Motor-Control-Demo.py** script is built to use the main serial I/O channel at the RPi GPIO Interface. These are GPIO pins 14 & 15 (header pins 8 & 10).

**NOTE:** *A good reference is the [pinout diagram for RPi GPIO Pins](https://pinout.xyz/)*

**RPi Wiring for Daemon use:**

| RPi Hdr Pin# | RPi GPIO Name | RPi Purpose | P2 Purpose | P2 Pin # |
| --- | --- | --- | --- | --- |
| 6 | GND | Signal ground | Signal ground | GND near Tx/Rx Pins |
| 8 | GPIO 14 | Uart Tx | Serial Rx (from RPi) | 57 |
| 10 | GPIO 15 | Uart Rx | Serial Tx (to RPi) | 56 |

Pick two pins on your P2 dev board to be used for RPi serial communications. The top-level file provided by this project defines these two pins as 56, 57. This was due to the two motor control boards occupying most of the remaining pins on the Mini Edge Breakout board. Feel free to choose different pins. Just remember to adjust the constants in your code to use your pin choices.

## Flashing your P2 Edge

The code for this project is set up for the P2 Mini Edge Breakout board with the two BLDC motor controllers installed at each of the dual-header locations. This leaves one single header where you just connected the serial wires from the RPi.

Head back to the folder where you unpacked the `serial-control-archive-set.zip` file, and open its `serial-control-archive-set/p2Src/` folder.

There, `isp_steering_serial.spin2` is the top-level file. Compile it and download it to FLASH with PNut-TS, which needs nothing more: the file selects the two-wheel configuration itself. With PNut, first select that configuration in `isp_bldc_motor_userconfig.spin2`, as [Building with PNut](DEVELOP.md#building-with-pnut) describes.

**NOTE:** *The pins are set in two files. The serial pins to the RPi are in `isp_steering_serial.spin2`. The motor boards' pin groups, the motor type and the drive voltage are in `isp_bldc_motor_userconfig.spin2`. If you are not set up as the demo specified, make your changes there before you flash the code.*

This should be all you need to test your new installation. The demo file will drive the motors as if the platform is driving in a square (drive straight, turn right, drive straight, turn right, etc.)

You can test by running the following command on your RPi. Start the script first, then reset or power up the P2, so the script sees the P2's `ident:` line:

```bash
cd ~/projects/platform-drive            # make sure we are where your project files are
./P2-BLDC-Motor-Control-Demo.py -d -v   # run with debug and verbose messaging enabled
```

If this is working for you, congratulations, you are all set up and ready to do your own drive code!

## Developing your own drive code

On your RPi copy the `P2-BLDC-Motor-Control-Demo.py` file to your own name:

```bash
cd ~/projects/platform-drive                        # make sure we are where your project files are
cp P2-BLDC-Motor-Control-Demo.py {newName}.py       # create new copy
```

Do all your development in this new file. Start by replacing the square-pattern drive code with your own.

The full command set, with every reply, is in [Serial Interface of Steering Object](DRIVE-OBJECTS-SERIAL.md).

### Checking the drive's status

Send `getstatus`; the reply is `stat {left} {right}`, one number per wheel:

| Number | Status | Means | What your code should do |
| --- | --- | --- | --- |
| 10 | DS\_Unknown | the drive is not running | check that the P2 started the motors |
| 11 | DS\_MOVING | the wheel is being driven | nothing |
| 12 | DS\_HOLDING | stopped, holding position | nothing |
| 13 | DS\_OFF | stopped, coasting | nothing |
| 14 | **DS\_FAULTED** | the motor could not follow its command, or a hall sensor failed | send a stop or a new power to clear it; if it recurs, reduce the load or the speed |
| 15 | **DS\_ESTOP** | emergency-stopped, or protectively stopped (a commanded wheel that could not turn) | drives are refused: send `emerclear` after an emergency stop, `protclear` after a protective stop (`getprot` says which) |

A drive command that the P2 refuses tells you why in its reply, for example
`ERROR drivepwr failed: ERR_EMERGENCY_STOPPED (-1016)`, so your code can read the reason instead of polling for it.
Every form of `ERROR` reply is listed in [Commands and replies](DRIVE-OBJECTS-SERIAL.md#commands-and-replies).

Send every value as a decimal integer, and send true and false as `-1` and `0`. The demo's wrappers do this for you.

Every reply is one line, ending with a single LF. Read one line per command you send.

The P2 checks for a new command every 1 ms, so it answers within a few ms. The exceptions are `checkwiring`, which
takes about 1.3 s (at most about 4 s), and a restart with `setstartchecks 0`. The demo's own reply loop checks every
0.2 s. If you use `settimeout`, shorten that loop or send your drive commands well inside the timeout.

The P2 never reports a command timeout by itself. After one, `getstopreason` reads 46 (SR\_LINK\_LOST) for each wheel
and `geterror` reads -1019 (ERR\_COMMAND\_TIMEOUT). See
[How your host learns of a command timeout](DRIVE-OBJECTS-SERIAL.md#how-your-host-learns-of-a-command-timeout).

Have fun!

## How to Contribute

This is a project supporting our P2 Development Community. Please feel free to contribute to this project. You can contribute in the following ways:

- File **Feature Requests** or **Issues** (describing things you are seeing while using our code) at the [Project Issue Tracking Page](https://github.com/ironsheep/P2-BLDC-Motor-Control/issues)
- Fork this repo and then add your code to it. Finally, create a Pull Request to contribute your code back to this repository for inclusion with the projects code. See [CONTRIBUTING](CONTRIBUTING.md)

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
