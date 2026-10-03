# The Universal Motor Driver boards — Rev A and Rev B

The Parallax 64010 Universal Motor Driver P2 Add-on Board exists in two revisions, **Rev A** and **Rev B**. These
objects drive both. This page gives the facts for each revision, so you know what the board you have does, what
the driver does with it, and when to be careful. It is not a buying guide.

The board facts come from the two Parallax manuals for the board and the datasheet of its MOSFETs; the driver
behaviour is the driver's own, verified on our hardware. The driver's behaviour, including how it holds speed up
to its current limit, is validated on **Rev B** boards.

## Contents

- [Which revision do you have?](#which-revision-do-you-have)
- [Rev A](#rev-a)
- [Rev B](#rev-b)
- [What is the same on both](#what-is-the-same-on-both)
- [What the driver protects against, and what it does not](#what-the-driver-protects-against-and-what-it-does-not)
- [When to be careful](#when-to-be-careful)

## Which revision do you have?

You do not have to tell the driver. When it starts, it reads the board's current-sense pin and tells the two
revisions apart, because that pin's circuit is where they differ. `getBoardType()` then returns `REV_A` or `REV_B`
for the board at that pin group, or `REV_Unknown` when no board is detected there.

The board detection setting in your configuration (see [DEVELOP.md](DEVELOP.md)) chooses how the revision is found:

| Setting | What it does |
| --- | --- |
| `BRD_AUTO_DET` | Detect the revision at start-up. **Use this unless you have a reason not to.** If no board is detected, `start()` refuses that pin group (`ERR_BOARD_NOT_DETECTED`): without the revision the driver has no current scale, and so no current limit |
| `BRD_REV_A` / `BRD_REV_B` | Force the revision. Forcing one that does not match your hardware gives the driver the wrong current scale, and it will not work correctly |

## Rev A

| | |
| --- | --- |
| Gate supply | **10 V**, from a switching boost regulator fed by the VIO3V3 pin of the upper P2 Accessory Header; up to 50 mA for the MOSFET driver circuits |
| MOSFET drivers | Four Microchip **MIC4604** half-bridge drivers, one per output channel (U, V, W, X); 39 ns propagation delay, typically 20 ns rise and fall |
| Current sense | A **5 mΩ** low-side shunt between the MOSFETs' common ground and system ground, **no amplifier**: **5 mV per amp** at the P2 pin |
| Negative-spike protection | A fast reverse-biased diode between each switching node and ground |

**What the coarse current sense means.** At 5 mV per amp, one millivolt of sense is 0.2 A, so a single current
reading on Rev A resolves about 0.2 A (`getCurrent()`). Small currents, and low current limits, cannot be measured
finely on this board.

## Rev B

| | |
| --- | --- |
| Gate supply | **12 V**, from a switching boost regulator fed by the VIO3V3 pin of the upper P2 Accessory Header; up to 50 mA for the MOSFET driver circuits |
| MOSFET drivers | Four Texas Instruments **UCC27211D** half-bridge drivers, one per output channel (U, V, W, X); about 20 ns propagation delay, typically 7.2 ns rise and 5.5 ns fall |
| Current sense | A **3 mΩ** low-side shunt in the same place, followed by an **INA180B2** current-sense amplifier with a gain of 50 V/V: **150 mV per amp** at the P2 pin, 30 times finer than Rev A |
| Negative-spike protection | The UCC27211D's own protection against large negative spikes, at least down to −10 V on its high-side pin, plus the same fast diode between each switching node and ground. The manual says this protection makes the board *"particularly suitable for driving large BLDC type hub motors"* |

**What the finer current sense means.** One millivolt of sense is about 7 mA, so a single current reading on Rev B
resolves about 7 mA.

## What is the same on both

- **The MOSFETs.** Each of the four channels has two N-channel MOSFETs in a half-bridge, Micro Commercial
  **MCAC85N06Y-TP**: 60 V drain-source; 85 A continuous at a 25 °C case (limited by the package), 54 A at 100 °C;
  at most 3 mΩ on-resistance with a 10 V gate drive, which both boards provide (10 V on Rev A, 12 V on Rev B). The
  MOSFETs have large internal body diodes.
- **The MOSFET driver logic.** The high and low sides are controlled separately, through a logic buffer that lets
  the high side turn on only while the low side is off.
- **The dead-time.** Both manuals give a **250 ns minimum** pause between turning one MOSFET of a channel off and
  the other on. The limit is set by how fast the MOSFETs respond, not by the gate drivers, which is why Rev B's
  faster drivers do not shorten it. The driver uses **260 ns** on both revisions.
- **The current-sense position.** Both sense the total MOSFET current, low side, between the MOSFETs' common ground
  and system ground.
- **The hall sensor inputs.** A 5-way 0.1″ header with a 5 V output for the sensor (up to 100 mA); each of U, V, W is
  pulled up to 3.3 V through 3.9 kΩ and reaches the P2 through a series 3.9 kΩ, which protects the P2 from 5 V
  signals.

## What the driver protects against, and what it does not

**It protects:**

- **Against too much current while driving.** The driver folds a motor's output back above **40 A**, and derates it
  to **27 A** when the average stays high, on either revision. These limits protect the board's transistors, not
  the motor, and they are not user settings. Each logs an event when it acts (`EV_FOLDBACK`, `EV_CURRENT_LIMIT`;
  see [Drive Objects](DRIVE-OBJECTS.md)). A wheel at its limit keeps its torque and gives up speed only there.
- **Against a blocked wheel.** A motor commanded to move that does not turn for about a second, with its rotor
  held far behind the field or the current limit acting on it, is stopped and latched (the protective stop; see
  [Drive Objects](DRIVE-OBJECTS.md)).

**It does not:**

- **Limit braking by shorted phases.** `emergencyCutoff()`, and `holdAtStop(true)` once the hold hands off to the
  short, brake by shorting the motor's phases. That current circulates through the low-side MOSFETs, where the
  current sense does not see it, so it is not limited; from top speed on the 6.5″ hub motor it is tens of amps.
  Ramp down before stopping where you can, as `stopMotor()` does.
- **See current returned to your supply.** `getCurrent()` does not show regenerative current, the current a moving
  motor sends back when it is slowed or pushed. The driver neither measures nor limits it.

## When to be careful

- **Rev A with large hub motors.** Rev A boards have been damaged in use with large hub motors, and Rev B was made
  because of it. Rev A does not have the gate drivers' own negative-spike protection, which the Rev B manual ties to
  driving large hub motors; its only spike protection is the diode at each switching node.
- **Rev A and small currents.** A Rev A reading resolves about 0.2 A. Anything that depends on telling small
  currents apart, such as a low current limit or a reading at rest, is coarse on Rev A. That coarseness affects
  when the current limit acts on Rev A, and the driver's behaviour at its limit is validated on Rev B.
- **Forcing the revision.** `BRD_REV_A` or `BRD_REV_B` that does not match the board gives the driver a current scale
  30 times wrong, and its current limit with it. Leave detection on `BRD_AUTO_DET` unless you have a reason.
- **Either board, braking by shorted phases.** It is not current-limited (above). From speed, prefer a ramped stop.
