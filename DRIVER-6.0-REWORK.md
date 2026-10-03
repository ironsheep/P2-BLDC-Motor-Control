# The 6.0 driver — what changed, and how we know

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

Version 6.0 is a rework of the drive, not a feature release. This page says why it was needed, what
changed, and how each change was checked. The full list of changes, and what still needs attention,
is the v6.0.0 entry in the [CHANGELOG](CHANGELOG.md). This page describes 6.0 as released; what 6.1.0 changed is in the
[CHANGELOG](CHANGELOG.md)'s v6.1.0 entry and in [Driver Theory of Operations](DRIVER-THEORY-OF-OPERATIONS.md).

## Where it started

A user's two-wheel platform ran cleanly on a fresh battery and then, on later runs, faulted a motor —
usually the right one. The demo kept driving the other wheel, and nothing in the program reported that
anything was wrong.

A line-by-line audit of the 5.x driver followed that report back to its causes, and found that most of
them were not bugs in one place. They were missing pieces:

- **No way to report a fault.** The status enum had no "faulted" or "e-stopped" value, so a faulted motor
  reported that it was moving. The serial interface passed the same wrong answer on.
- **One protection, and it gave up.** The only automatic protection was a last-resort test that switched
  the motor off once the rotor fell far enough behind the field. There was no current limit, no stall
  detection and no fallback.
- **One commutation offset, mirrored for the other direction.** The 6.5″ motor used one fixed offset
  (43°), and the other direction's offset was its arithmetic mirror (317°). On a two-wheel platform the
  right motor runs mirrored, so it always used the mirrored value.
- **A start-up surge.** The duty servo hunted at low speed, so every start passed through a current surge.
- **Errors that stopped the caller.** Bad arguments aborted the calling cog instead of returning an error.
- **Two writers for the same state.** The caller's cog and the sense cog both wrote the drive command, the
  e-stop and the stop limits, and stop limits were checked only 8 times a second.

## What changed

**The motor is driven where it wants to be driven.** The commutation for the 6.5″ motor is now built from
the motor's measured hall zero and a lead that follows speed, both measured on the motor itself. The effect
is large. Measured on the same driver with only the offsets changed, unloaded running current at low and
middle speeds is 8 to 25 times lower than with v5.0.2's offsets, and the two directions draw the same current
to within a few percent. The
[6.5″ motor manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md) says how each number was found.

**A servo that doesn't hunt.** The duty now comes from a feedforward, the duty a speed needs, plus a small
trim whose gain scales with duty. The start-up surge is gone: peak current at a start is 1.2–1.5 times the
settled value, against 1.9–3.0 with v5.0.2's duty servo (the same starts, on the same motors).

**Motion that eases in and out.** Every start, speed change, stop and reversal is jerk-limited: the
acceleration eases in and out over 250 ms, and a reversal passes through zero in one continuous ramp.
Acceleration and deceleration are set in mm/s² at the wheel.

**Stops that land where they should.** The driver works out its own stopping distance and time every drive
pass and publishes them. A distance or time limit fires early by exactly that amount, so the motor comes to
rest at the limit, not past it.

**Protection that responds instead of giving up.** Current folds back above 40 A and derates to 27 A under
sustained load. A motor that cannot keep up runs slower instead of faulting. A
wheel commanded but unable to turn is stopped after about a second. When control is truly lost, the default
response re-seeds the field from the halls and ramps down, rather than simply cutting power. On a two-wheel
platform, one wheel's fault stops the other, and a wheel that can't keep up slows both, so the platform
keeps its path.

**A driver that checks itself at start.** `start()` checks the halls, the current sense and each motor lead
with nothing moving, and refuses a motor that fails. An opt-in check moves each wheel a few centimetres to
prove its wiring, and another measures the windings.

**One owner for the drive.** A single front cog is now the only writer of the driver's commands. Public
methods post a request and get an answer, so two cogs of your program can command the same motor safely, and
every command returns `NO_ERROR` or an `ERR_*` code. The cog count is fixed: 2 for one motor, 3 for two.

**It reports what it did.** `getStatus()` reports faults and e-stops. `getStopReason()` says why a drive
ended, `getFaultCause()` why it faulted, `getHealth()` what the start checks found, and an event log records
what the drive handled on its own.

**Room to grow.** With these functions in, the PASM driver had filled its memory: 492 of 496 cog RAM longs
and 507 of 512 LUT longs. It was then reorganised, to 441 and 457, and every step was proved to behave
identically before it was accepted.

## How it was checked

Four kinds of evidence, used in this order, so the slow ones were spent only on questions the fast ones
couldn't answer:

1. **At the desk.** A defect with a known symptom was traced to the code that produced it and reproduced in
   a model before anything was built. The speed-change current kick was reproduced to within about 10 mV
   before its fix; the start surge was predicted from the servo's gain. Every memory-saving rewrite of the
   PASM driver was proved identical to the original, frame by frame, in an instruction-level emulator.
2. **At compile time.** Every object compiles under every configuration, and both flagship demos compile
   with and without DEBUG. At run time, `start()` refuses a driver whose shared-memory layout has drifted.
3. **On the bench, wheels lifted.** Test programs drive the motors and print a PASS, FAIL or NOMEAS verdict
   for every check, judged against a criterion written before the run. Each check was also shown to *fail*
   on a case built to fail it — a lead withheld in firmware, a hall pair read as swapped — because a check
   that has only been seen to pass hasn't been tested.
4. **On the floor, loaded.** How the platform behaves with its weight behind the wheels, on a 7.7 kg two-wheel
   platform: distance stops, the fault response, the current after a fault, the blocked-rotor stop, a one-sided
   load, and the feel of the ramps under a remote control. Each run starts by itself and needs no one at the
   keyboard; the loads that need a person are a hand on the frame and the remote.

The first three are complete for 6.0. The floor results are in the motor manual's
[§6.5](MOTOR-6.5IN-TECHNICAL-MANUAL.md#65-stopping-faulting-and-holding). One of them is a known issue of v6.0.0:
spinning a loaded platform in place, the lead table's timing gives up speed well inside its current range. A driver
change for it is designed and planned for the next release. Every other figure on this page and in the motor manual was measured
with the wheels lifted, and what that leaves unmeasured is listed in the Known Issues of the
[CHANGELOG](CHANGELOG.md)'s v6.0.0 entry and in the manual's
[What we do not know yet](MOTOR-6.5IN-TECHNICAL-MANUAL.md#9--what-we-do-not-know-yet).

**What was validated.** 6.0 is validated on the 6.5″ hub motor at a 270 MHz system clock; the measurements
were made on Rev B boards. The DocoEng motor and the serial control path are not validated for this release.

## Going further

- **How the driver works:** [Driver Theory of Operations](DRIVER-THEORY-OF-OPERATIONS.md).
- **How we measured, and how you can:** [TECHNIQUES.md](TECHNIQUES.md).
- **Adding your own motor:** [ADDING_MOTOR.md](ADDING_MOTOR.md).

---

> If you like my work and/or this has helped you in some way then feel free to help me out for a couple of :coffee:'s or :pizza: slices!
>
> [![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/ironsheep) &nbsp;&nbsp; -OR- &nbsp;&nbsp; [![Patreon](./images/patreon.png)](https://www.patreon.com/IronSheep?fan_landing=true)[Patreon.com/IronSheep](https://www.patreon.com/IronSheep?fan_landing=true)

---

## Disclaimer and Legal

> _Parallax, Propeller Spin, and the Parallax and Propeller Hat logos_ are trademarks of Parallax Inc., dba Parallax Semiconductor

---

## License

Licensed under the MIT License.

Follow these links for more information:

### [Copyright](copyright) | [License](LICENSE)

[maintenance-shield]: https://img.shields.io/badge/maintainer-stephen%40ironsheep%2ebiz-blue.svg?style=for-the-badge

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg
