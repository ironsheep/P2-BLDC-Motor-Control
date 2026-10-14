# P2-BLDC-Motor-Control - Testing the Motors

How the two motors were studied and the version 6 driver was built: what we wanted to know, how we found out, what we got wrong on the way, and what the driver does differently because of it.

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

## Table of Contents

On this Page:

- [The map](#the-map) - every aspect we studied, what changed, and in which release
- [Where it started](#where-it-started) - the report that began version 6
- [How we tested](#how-we-tested) - the rigs, the order of the work, and how a test says pass or fail
- [Placing the field on the 6.5″ motor](#placing-the-field-on-the-65-motor) - counting ticks, the hall zero, the lead
- [The duty servo, and holding speed under load](#the-duty-servo-and-holding-speed-under-load) - the start surge, and the platform that spun slow
- [Ramps and stops](#ramps-and-stops) - the current kick, easing in and out, stopping on the mark
- [Current sensing, protection and the two boards](#current-sensing-protection-and-the-two-boards) - what the current channel can tell you, and what the driver does with it
- [Start checks and the halls](#start-checks-and-the-halls) - proving a motor before driving it
- [The DocoEng motor](#the-docoeng-motor) - a motor that did not turn, and the full range it now runs
- [The system clock](#the-system-clock) - from one clock to any clock from 130 to 300 MHz
- [What the testing taught us about testing](#what-the-testing-taught-us-about-testing) - the lessons that cut across every aspect
- [What we do not know yet](#what-we-do-not-know-yet) - the open questions
- [Going further](#going-further) - where to read next

Additional pages:

- [Main Page](README.md) - Return to the top of this repo
- [Techniques](TECHNIQUES.md) - The methods on this page, written so you can reuse them
- [6.5″ Motor Technical Manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md) - The 6.5″ motor as measured
- [DocoEng Motor Technical Manual](MOTOR-DOCO-TECHNICAL-MANUAL.md) - The DocoEng motor as measured
- [The 6.0 Driver Rework](DRIVER-6.0-REWORK.md) - The 6.0 changes in brief

---

The motor manuals give the numbers, and [TECHNIQUES.md](TECHNIQUES.md) gives the methods. This page is the story that joins them: for each part of the drive, the question we started with, how we studied it, what we learned, where we were wrong, and what changed in the driver. It covers the work behind versions 6.0.0, 6.1.0 and 6.2.0.

Each finding says how it is known. **Measured** means read on our hardware. **Calculated** means worked out from measured values. **Modelled** means predicted by a model of the motor or the driver, then checked where we could. **Vendor** means taken from a data sheet or a board manual.

## The map

| Aspect | What we wanted to know | What the driver does now | Release |
| --- | --- | --- | --- |
| Reporting and ownership | Why a faulted wheel said nothing | Reports faults, stops and their causes; one cog owns every drive command; no call aborts | 6.0 |
| Placing the field (6.5″) | Where the magnets are, and how far ahead to put the field | A measured hall zero plus a lead that follows speed | 6.0 |
| The duty servo | Why every start surged, and why a loaded platform spun slow | Feedforward plus a calm trim; a fast answer to a real load | 6.0, 6.1 |
| Ramps and stops | Why speed changes kicked, and whether stops land on the mark | Jerk-limited ramps; the driver plans its own stop | 6.0, 6.2 |
| Current and protection | What protects the board, and what to do when control is lost | Fold-back and derate limits, a blocked-wheel stop, a graded fault response | 6.0, 6.1, 6.2 |
| Start checks and halls | Whether a motor is sound before it is driven | Hall, current-sense and lead checks at every start; one-instruction hall reads | 6.0 |
| The DocoEng motor | Why it moved a few ticks and stopped, and its real range | Turns and holds speed from 2,018 to 6,551 rpm, 7.4 to 24 V | 6.2 |
| The system clock | Whether the driver works at the clock you choose | The same behaviour at any clock from 130 to 300 MHz | 6.2 |

## Where it started

A user wrote in about a two-wheel platform: two 6.5″ hub motors, an 18.5 V pack and the dual-motor demo. The first run on a fresh battery was fine. Later runs faulted a motor, usually the right one. The demo kept driving the other wheel and reported nothing. The single-motor demos ran both motors without trouble. They asked whether there was a known reason.

A line-by-line reading of the driver was already under way, and it had found most of the causes. They were not bugs in one place. They were missing pieces:

- **Nothing could report a fault.** A faulted motor reported that it was moving, and the two-wheel object had no way to ask.
- **One protection, and it gave up.** The driver switched the motor off once the rotor fell about 176° behind the field, where the motor makes only a few percent of its torque. The current was sampled every frame and used for nothing. There was no current limit and no stall detection.
- **One offset, mirrored.** The 6.5″ motor used one commutation offset (43°) and its arithmetic mirror (317°) for the other direction. A two-wheel platform runs its right motor mirrored, so one wheel always used the guessed value.
- **No margin.** The speed table at 18.5 V sat about 2 % below the speed where the motor was measured to fault, and a full 5S pack is 21 V, not 18.5.

So the question grew from "why does this wheel fault?" into "what should a motor driver do?" The rest of this page is how we answered it.

## How we tested

**The rigs.**

- **Wheels lifted.** Both 6.5″ motors on a platform up on blocks, on Rev B boards, at 270 MHz. Most of the 6.5″ figures were measured this way.
- **The floor.** A 7.7 kg two-wheel platform driving hands-off inside a fenced area: distance stops, spins in place, a forced fault, a solid obstacle, and drives under a FlySky remote.
- **The encoder bench.** One DocoEng motor on a Rev A board, with a 360-line quadrature encoder on its shaft (1,440 counts a turn, one electrical degree a count). It gives an independent measure of where the shaft really is. The 6.5″ hub motor is the wheel and has no shaft to fit one to.
- **Supplies.** The 6.5″ ran on a bench pack. The DocoEng ran at 7.4, 11.1, 14.8, 18.5, 22.2 and 24 V, the nominal 2S to 6S packs plus its rated 24 V.

**The driver measures itself.** Every current and voltage figure on this page was read through the board's own sense channels, by the driver. A meter on the pack checked the current scale once, and agreed: 150.1 mV per amp, against the board's 150. After that, no meter readings were copied by hand. Test programs record the driver's own status, current and hall counts with timestamps.

**The order of the work.** Each step was used only for questions the step before it could not answer:

1. **At the desk.** Read the code against the P2 documentation, then model the motor and the driver. A defect with a known symptom was reproduced in a model before anything was built.
2. **At compile time.** Every object compiles under every configuration.
3. **On the bench, wheels lifted.**
4. **On the floor, loaded.**

**Every test judges itself.** Each check carries its numeric limit in the test program before the run, and prints `PASS`, `FAIL` or `NOMEAS` with the value beside it. `NOMEAS` means the condition never arose. It is never counted as a pass.

**Every check was shown failing.** A check that has only been seen to pass has not been tested. Each one was also run against a case built to fail it: a motor lead withheld in firmware, a hall pair read as swapped, a hall cable unplugged.

**PASM rewrites were proved identical.** To make room in the driver cog, parts of the PASM driver were rewritten. Each rewrite ran beside the original in an instruction-level emulator, on the same input. Every hub write, pin operation and register was compared at every PWM frame, across 55 named edge cases and random seeds. A rewrite that was meant to change behaviour was compared with a copy of the old code, so that only the intended difference could appear.

## Placing the field on the 6.5″ motor

**The question.** Where are the magnets relative to the hall sensors, and how far ahead of the rotor should the field sit? The old answer was one offset each way, one of them a mirror. The first measurements showed one direction drawing about twice the current of the other, on both motors.

**How we studied it.**

- **Counting the ticks by hand.** Turning the wheel three times by hand gave exactly 270 hall transitions, so 90 a revolution and 15 pole pairs. A figure we had been given for this motor would have needed 414. The count settled it, and nothing else could have: every later calculation divides by the same 90, so none of them could catch a wrong 90.
- **The hall zero (Z) from both directions.** Sweep the offset in each direction and find each one's current minimum. The midpoint of the two is the hall zero, because the lead cancels out. Z must not move with speed while the lead does. That is the check that the two have been separated.
- **The hall zero cold.** Turn the wheel by hand with the bridge switched off and read the motor's own voltage on the phases. This method shares nothing with the first one.
- **The lead (L) at several speeds,** one octave apart.

**What we learned.**

- **Z is −4° on both units (measured).** The two methods agree within 0.35°: −3.8° and −4.0° from the current minima, −3.3° from the motor's own voltage.
- **The lead is not a constant (measured).** The best lead runs from about 20° at a crawl to 5–8° from a quarter of top speed upward.
- **Getting it right matters (measured).** A field placed 25° from the best position draws 15 to 26 times the current for the same speed. Letting the lead follow speed saves a further 22–74 %. The two directions now draw the same current within a few percent.
- **The lead curves (modelled, fitted to 32 sweeps).** Sweeping the offset at one speed gives two bowls. The bottom of the current bowl is the most efficient lead. The bottom of the duty bowl leaves the most voltage in reserve. The two coincide at low speed and part as speed rises, and the drive cannot hold the rotor past the duty bowl's bottom. [Driver Theory of Operations](DRIVER-THEORY-OF-OPERATIONS.md#the-lead-curves-where-the-offset-should-sit) explains why.
- **The top speed is chosen, not found (measured).** The duty first reaches its ceiling at 175–185 × 10⁶. The wheel keeps up beyond that, to at least 245 × 10⁶, by letting the rotor fall further behind the field, and that costs current: 3.6 A at 245 against about 0.5 A at 175. The shipped ceiling is the fastest speed that keeps a duty reserve: 294 rpm, 2.54 m/s on the 6.5″ wheel.

**What we got wrong.**

- **We read the lead's direction backwards.** As the driver writes the 6.5″ pair, a larger L puts the field *less* far ahead. So the table's L falling with speed means the real lead rises with speed, the direction textbooks predict. The lead-curve model found this.
- **Lower current was not always a better lead.** At an eighth of top speed, one setting drew less current because the wheel was turning at only half its commanded speed. The sweep tool now compares only settings at which the wheel follows its command to within 2 %.
- **A current offset looked like a board property.** One run read a 72 mV current zero on one board, and that was written down as a fact about the board. The next run read 12 mV. The driver had calibrated from a single sample at start. Every current figure is now net of a zero taken in the same session.

**What changed.** In 6.0 the 6.5″ commutation became the measured zero plus a lead table against speed, the same for both units and both directions.

**Do it yourself.** [TECHNIQUES.md](TECHNIQUES.md) §1.1 to §1.6. The full record is in the [6.5″ manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md) §2, §4 and §5.

## The duty servo, and holding speed under load

**The question.** Every start from rest passed through a current surge, 1.9 to 3.0 times the settled current. At low speed the duty swung 40–60 % above its mean while the speed was constant. Then, after 6.0 shipped, a loaded platform spinning in place ran as much as 43 % slow, with its current nowhere near the limit.

**How we studied it.** A desk model of the servo was built from the driver's own arithmetic, frame by frame. It reproduced the measured steady duty, the size of the swing and its roughly 150 ms period from one fitted value. For the floor problem, a model of the two-wheel platform (7.7 kg, 387 mm between the wheels) was added.

**What we learned.**

- **Why it hunted (modelled).** The rotor behaves like a weight on a spring, and the spring is weak at low duty. A servo with one fixed gain strong enough for top speed is too strong for that weak spring, and it oscillates.
- **The fix (modelled, then measured).** The duty now comes from a feedforward, the duty a speed needs according to the motor's measured back-EMF, plus a small trim whose gain scales with duty. Peak start current fell to 1.2–1.5 times settled.
- **Why the platform spun slow (modelled, then confirmed on the floor).** The most efficient lead sits close to the motor's strongest angle, which leaves the servo little stiffness to spare. A platform puts about five times a wheel's own inertia behind each wheel. With that behind it, the trim oscillated at 3–4 Hz. Each swing reached the point where the driver holds the field back, and each held pass took a little speed away.

**What we got wrong.**

- **A start fix that did not work.** A first fix pre-set the duty at start. It was built and run, it did not remove the surge, and it was taken out. The servo hunting during the ramp was the real cause.
- **The model's depth.** The platform model reproduced the slow spins but not how slow they were. The one result that held at every setting of the model was that a quarter of the trim's gain removed the oscillation. That is what shipped. Exactly how deep the loss was remains unexplained.
- **Each fix uncovered the next thing.** Giving the drive more authority in 6.1 exposed three mechanisms that had relied on the old timidity. The blocked-wheel stop stopped latching, because the current limiter now acted in single frames instead of whole passes. The field could walk into a window where one hall tick would fault it. And the top speed ran rough, which the author heard before any test measured it: a voltage ceiling was being treated like a current limit. All three were fixed before 6.1 shipped.

**What changed.** 6.0 brought the feedforward and the scaled trim. 6.1 cut the trim's gain to a quarter. It added a fast response once the rotor falls well behind the field, so a real load is answered with torque straight away, up to the current limit. It also added a hold at the motor's strongest angle while the current limit is acting. On the floor, spins in place now run at 100–107 % of command.

**Do it yourself.** [TECHNIQUES.md](TECHNIQUES.md) §2.5, a desk model before a bench run. How the servo works is in [Driver Theory of Operations](DRIVER-THEORY-OF-OPERATIONS.md#the-frame-loop-duty).

## Ramps and stops

**The question.** Stopping from three-quarter speed or more drew over 10 A. The author's hand on the motor felt a kick at every speed change. Every ramp started and ended with a step in torque. `holdAtStop()` was documented as changing how a motor stops, but a stop from speed took the same distance either way. And a distance or time limit has to end with the wheel at rest on the limit, not past it.

**How we studied it.** The current was sampled at 500 Hz through the board's own sense channel, on lifted wheels. A pass-by-pass model of the servo reproduced each defect before it was fixed. The stop arithmetic was checked against about 7,000 random stops in a model, then in the emulator. For the stop modes, a hand test was built with predictions that could fail: a coasting wheel must take more than 150 ms to fall to half speed, and a shorted one less than 60 ms.

**What we learned.**

- **Stop current (measured).** The servo regulates the rotor's angle, not its current. During a slow-down it held the duty up while the motor's own voltage fell, so the winding current rose 20–50 % above running current. A cap on the duty in proportion to speed, lifted as soon as the rotor starts to trail, fixed it.
- **The speed-change kick (measured, then fixed).** At the moment a ramp arrived, the field skipped one whole step, and the rotor rang at about 18 Hz. The worst kicks fell from 64–183 mV to 13–16 mV over the settled current.
- **Jerk-limited ramps (measured).** The acceleration now eases in and out over 250 ms, and a reversal passes through zero in one continuous ramp. On the floor, ramps at 200, 1,000 and 3,000 mm/s² arrived within 1 % of the set rate. The cost is calculated: every stop takes about 0.25 s longer.
- **The stop plan (measured).** The driver works out its own distance and time to rest on every pass and publishes them. A limit starts the stop early by exactly that amount. Stops on lifted wheels came to rest within 2 ticks and 3 ms of their limits. On the floor, spins and 1 m runs ended within 3 ticks.
- **Coast or short (measured).** From 1.2 m/s a coasting wheel ran 54 ticks over 536 ms; a shorted one stopped in 1–2 ticks, 9 ms. A graded short, shorted for part of each 10 ms, lies between. At 10 % it stops in about half the coast's time, with about 28 times less deceleration than a full short.

**What we got wrong.**

- **A check that passed while the motor kicked.** The first speed-change check judged the rotor's position error. But the driver clamps that error, so it can never show a kick. The check reported no kicks out of 22 while the current spiked to about 9.6 A. The author's hand was the control. The check now judges current.
- **A stop fix that broke the other stop.** On the DocoEng at low supply, distance stops ended short. Holding the speed plan still while the rotor caught up fixed them. It also made timed stops end up to 105 ms late. A stop by distance promises distance and a stop by time promises time, so the fix now applies only to distance stops. Timed stops end within −55 to +15 ms.
- **"Coast" at rest may never have coasted.** Reading the code suggested the old "float" was really a short, while an older note said it had worked. The new code builds coast, hold and short as explicit states, so the question no longer matters. The hand test confirmed each one.

**What changed.** 6.0 brought the stop-current cap, the jerk-limited ramps set in mm/s² at the wheel, the stop plan and the explicit stop states. 6.1 removed a smaller kick on slow-downs. 6.2 made low-voltage distance stops and timed stops land on their limits.

**Do it yourself.** [TECHNIQUES.md](TECHNIQUES.md) §1.8, characterize how it stops, and §3.9, let the driver publish its own stop plan. The record is in the [6.5″ manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md#65-stopping-faulting-and-holding) §6.5 and §7.5.

## Current sensing, protection and the two boards

**The question.** What protects the board? What limit do its transistors need? And when control is lost, is there something better than switching off at full speed? A coast lets a platform run away on a slope; a full short behind a tall platform can tip it.

**How we studied it.**

- The vendor manuals for both board revisions and the transistor data sheet were read, and their facts written down verbatim, kept apart from our own analysis.
- The limits were derived from the data sheet with every assumption stated.
- Every way a drive can end was listed, with what the driver can still sense at that moment.
- Faults were provoked on demand with a guarded forced fault.
- Limits were set far below what a wheel needs, so the fold-back and the blocked-wheel stop would fire on an unloaded wheel.
- Rev A's current noise was modelled at the desk before any filter was run.

**What we learned.**

- **The two boards (vendor).** Rev A reads current at 5 mV per amp, and Rev B at 150 mV per amp: one millivolt is 0.2 A on Rev A and about 7 mA on Rev B. The channel measures the whole bridge's return current, not each phase. The other three sense channels are phase voltages. Both boards use the same transistors.
- **The limits (calculated from the data sheet).** The limits are 40 A peak and 27 A continuous. The board measures the bridge's current, but the transistors carry phase current, so the threshold is scaled by duty.
- **The current is not zero at rest (measured).** The two 6.5″ boards read 6.4–9.4 mV and −0.3–3.1 mV at rest. The driver now takes a zero at start and subtracts it.
- **Stopping a blocked wheel (measured).** A commanded wheel that does not turn latches the protective stop in about 1.0 s. On the floor it latched against a solid obstacle in both stop modes, with no fault.
- **Losing control gracefully (measured).** After a fault the driver can still read its halls, so by default it places the field from them again and ramps down. From 1.2 m/s that took 1,106 ms and 122 ticks, against the 120 its own plan predicted. On the floor, a forced fault on one wheel stopped the other at once, and the platform's heading changed by less than 2°.

**What we got wrong.**

- **A hardware fact taken from our own code.** An early study concluded Rev B needed a much shorter dead gap (52 ns). Both vendor manuals say 250 ns minimum on both boards, so 52 ns would have been five times out of spec. The per-board value was deleted and both boards use 260 ns. Since then, a claim about the hardware cites the vendor's manual, never what our code seems to assume.
- **The current reading was wrong by a clock-dependent factor.** A scaling step had been lost, and the error moved with the clock. It was hidden because the wrong number happened to be close to the right one.
- **A sound circuit, an unsound read.** The board revision is detected from the current-sense pin, and the circuit really does differ between revisions. But a Rev B board read as Rev A after a stop and restart, because the pin was left in its old state. That would have scaled every current reading about 30 times wrong. The repair was checked with 12 start-stop cycles per motor, with no misdetection.
- **Rev A folded back on noise.** At low test limits on Rev A, noise alone crossed the threshold. The driver now smooths Rev A's reading over 16 frames (0.36 ms), and still acts on a single frame far over the limit. Users run at the 40 A limit, where this never arose; a low limit was a test stimulus.
- **A fallback that never ran.** A second fault during a controlled stop should fall back to a graded short. It was latched, then cleared half a millisecond later by a rule meant for something else. The test sampled too slowly to see that; the wheel's full coast time in the log gave it away.
- **10 % was a guess, and braking is not linear.** At 10, 25 and 50 % the short added about 0.8, 5 and 30 times the coast's own drag. The default was chosen only after that was measured.

**What changed.** 6.0 brought the fold-back and derate limits, the rest-zero capture, the protective stop and the graded fault response. On two wheels it added stopping both wheels together. 6.1 made a wheel held at its limit unable to fault when pushed back. 6.2 added the Rev A filtered fold-back, a blocked-wheel stop that also latches at 24 V, and the clock range.

**Do it yourself.** [DRIVER_BOARDS.md](DRIVER_BOARDS.md) for the boards; [TECHNIQUES.md](TECHNIQUES.md) §2.1, a check that cannot fail proves nothing.

## Start checks and the halls

**The question.** `start()` used to prove the P2 side and nothing about the motor. A hall cable could be unplugged, a lead missing or a current channel dead, and `start()` still succeeded. The first sign came later, as a fault at speed that looked like a load problem. Separately, the right-hand motor showed a few impossible hall codes a second at a 200 MHz clock, and none at 270 or 300 MHz.

**How we studied it.** Each proposed check was listed with its blind spots and the case built to fail it. Each failing case was paired with a healthy control, and each refusal with a run that opts out of the checks, so the two prove each other. The position of the hall read within the PWM frame was worked out in clocks.

**What we learned.**

- **The lead check (measured).** Driving one phase at 50 % with the others off moves nothing, because no current path exists. A healthy lead reads 777–823 mV. A withheld lead reads 31 mV or less, and the right lead was named in 10 of 10 starts.
- **The hall check (measured).** An unplugged hall cable reads `%111`, an impossible code, and was caught 10 of 10 times.
- **The winding (measured).** The driver measures about 0.48 Ω phase to phase, through its own bridge.
- **The wiring walk (measured).** An opt-in check moves the wheel one electrical cycle each way. 20 of 20 healthy walks passed, and a swapped hall pair failed 3 of 3.
- **Hall integrity (measured).** The three halls are now read in one instruction, through the P2's input filter. That gave zero impossible codes at 200, 270 and 300 MHz on both wheels. We did not separate how much each change contributed.

**What we got wrong.**

- **A torn read was blamed, and could not cause it.** Three separate hall reads can catch a hall changing. But a torn read across a legal change returns either the old code or the new one, and both are legal. To produce an impossible code, a line that is not changing must be misread, which is a glitch on the wire. The single read was still worth doing, but it was not the explanation.
- **A failing check found a real hazard.** On a miswired wheel the first wiring walk drew about 26 A. The walk now ends a leg at about 1 A.
- **A board that stopped driving.** One board repeatedly failed the lead check for a minute or two at a time. Its phases read below the level they float at, which only a conducting low side can cause, so its high-side drive had stopped. Four explanations were ruled out. It has not recurred since the board was reseated on its headers, but the cause is not established. The start check refused that board every time, which is what it is for.

**What changed.** In 6.0, `start()` began checking the halls, the current sense and each lead with nothing moving. A failing check is retried, and a motor that still fails is refused. `getHealth()` reports what the checks found, and `getHallIntegrityCounts()` reports the halls' health while running.

**Do it yourself.** [TECHNIQUES.md](TECHNIQUES.md) §2.1, §2.3 and §3.5. What the driver proves at start is in the [6.5″ manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md#66-what-the-driver-can-prove-about-the-motor-at-start) §6.6.

## The DocoEng motor

**The question.** Versions 6.0 and 6.1 shipped DocoEng settings that had never been checked against an independent measure. Did it really run well at every supply voltage?

**How we studied it.** On the encoder bench, at six supply voltages, on a Rev A board. The rule was to qualify it the same way as the 6.5″. Desk models came first: a servo model built from the data sheet, and the lead-curve model fitted to 894 points from every sweep on disk.

**What we learned.**

- **It did not turn (measured).** On the 6.x driver the motor moved one to five hall ticks and stopped, at every voltage. The encoder showed every first step going backward. The 2023 offsets were written in a different convention from the one the 6.x driver uses, and its start, servo and current hold all depend on that convention. The 5.x driver had used only the size of the rotor's lag, not its direction, so it had never noticed. Correcting the pair made it turn.
- **The geometry (measured).** It has 24 ticks a revolution and 4 pole pairs. Its six hall sectors are unequal, 54° to 67° each, and repeat on each unit within about 1°. The driver's table now carries the two units' mean widths. Equal 60° sectors would misplace the field by up to 6°.
- **Its current barely tells you anything (measured).** Unloaded, its current hardly changes across ±20° of timing, so on Rev A the current minima were often too shallow to find. The voltage the drive needs always resolved. On this motor, timing shows in the voltage needed rather than the current, the reverse of the 6.5″.
- **The lead curves hold across supplies (modelled, checked against the sweeps).** The duty bowl's bottom fits 19 speeds at every supply from 7.4 to 24 V within 0.9°. The supply does not move it. The lead table follows the efficiency curve, from 52° at low speed to 68° near the top.
- **It hunted at speed (modelled, then measured).** Above about 2,500 rpm the rotor's angle swung on its own at 40–70 Hz. Once the winding's inductance matters, nothing damps that swing in a drive that commands the field's speed. The driver now damps it, using the rotor's lag at each hall edge.
- **The range (measured).** It runs from 2,018 rpm at 7.4 V to 6,551 rpm at 24 V. Each top is the fastest speed held with duty to spare, and each held with room above it.

**What we got wrong.**

- **The wiring walk had passed a motor that did not run.** The walk reached 4 of its 6 ticks, and its limits allowed 3. It passed the same fault the encoder later caught.
- **A cap reported as the motor's top.** The first speed survey's tops were where the hunt began, not where the motor gave out. A top speed is now found by measuring to where the motor or the drive actually gives out. Any limit below that is reported as a limit, with its reason.
- **A test limit blamed on the drive.** A pass lost speed at every voltage. The cause was the 2 A test limit on Rev A, where noise crossed the threshold. The same rows at 40 A followed perfectly.
- **A new top that faulted on the way down.** Raising the 24 V top made the slow-down from it fault, 3 times in 3. The model reproduced it: the damping was switched off during slow-downs. Keeping it on, and letting it follow faster while slowing, fixed it. That held through 21 reversals and 14 slow-downs from the top, with no fault.
- **Per-board tables that were measurement artifacts.** The 2023 settings had separate tables for each board revision. They had been chosen by minimum current, on boards whose current resolution differs 30 times. The motor's halls and the boards' transistors are the same on both revisions, so one table now serves both boards.

**What changed.** In 6.2 the DocoEng turns and holds speed across 7.4–24 V. It has measured sector widths, a lead table, damping at speed, and one table for either board.

**Do it yourself.** [ADDING_MOTOR.md](ADDING_MOTOR.md) and `util_adopt_motor.spin2`. The tool finds a new motor's offsets and speed ceiling from its halls and supply current, with no encoder. We checked it against the encoder bench. The full record is in the [DocoEng manual](MOTOR-DOCO-TECHNICAL-MANUAL.md).

## The system clock

**The question.** Every demo and every test had run at 270 MHz. Does the driver work at the clock you choose? Our rule was that it must. A part of the driver that does not work at your clock is a defect to fix, not a limit to document.

**How we studied it.** We listed every mechanism whose timing depends on the clock: the PWM frame, the drive pass, the dead gap, the front cog's 1 ms pass, the current-sense converter, serial bit timing and the demos' long waits. Each was traced from the running clock, then measured at the ends of the range.

**What we learned.**

- **The low end is set by work per frame (calculated, then measured).** The driver's busiest frame does a fixed number of clocks of work. At 130 MHz that fills three quarters of the frame, which leaves a quarter in reserve. At 130 MHz both wheels showed the right frame and pass, and a 261 ns dead gap.
- **The high end is set by the current sense (measured).** The board's current reading comes from the P2 pin's own converter, which runs straight from the system clock. Its rest reading spread 3–5 mV from 200 to 300 MHz. At 350 MHz on Rev A it read 35 mV once, and every other start was refused. No P2 document gives that converter's top clock, and nothing above 300 MHz was measured.
- **Timing now follows the clock (measured).** The drive pass measured within −3 to +7 parts per million of its design at every clock tested from 120 to 300 MHz.

**What we got wrong.** A margin was hidden in the 270 MHz habit. The drive pass's timing rested on a margin of 2 to 22 clocks, and the front cog would run late below about 160 MHz. Neither showed up at 270 MHz.

**What changed.** In 6.2 every timing is derived from the running clock at `start()`. A clock under 130 or over 300 MHz is refused before any pin is touched. Set your clock before calling `start()`.

**Do it yourself.** [Choosing a clock](DEVELOP.md#choosing-a-clock).

## What the testing taught us about testing

These lessons came up again and again, across every part of the drive. [TECHNIQUES.md](TECHNIQUES.md) Part 2 has the methods.

- **When the measurement and the system disagree, suspect the measurement first.** At one early bench session, seven of thirteen failures were faults in the tests' own limits, not the driver. Examples: a limit narrower than the measurement's resolution, and a check judging the wrong quantity.
- **Never judge a quantity the driver clamps.** A clamped value cannot show the event you are looking for. The speed-change check that read "no kicks" was looking at a value the driver holds within bounds.
- **A circuit that can tell two cases apart is necessary, not sufficient.** Board detection had a sound circuit and still misread.
- **A count that everything else depends on needs a check that depends on nothing.** Counting ticks by hand was the only check that could catch a wrong ticks-per-revolution, because every other figure divides by it.
- **A fix is checked against every promise it touches.** The distance-stop fix kept its own promise and broke the timed stop's.
- **A cap is not a limit.** A speed reached under a limit we imposed is reported as that limit, never as what the motor can do.
- **Your hands and ears are instruments.** A kick felt at the motor and roughness heard at top speed were both found before any test found them, and both were real.
- **Say what is not known.** Every manual has a section for it, and so does this page.

## What we do not know yet

- **The pack voltage.** The optional pack sensor reads the pack, but the drive does not use it yet. Watts and the speed table assume the configured voltage.
- **Regenerative current.** The driver cannot see current returned to the supply.
- **Shorted-phase braking.** It is not current-limited, and the current channel cannot see it.
- **Loaded behaviour.** It is certified on the 6.5″ on Rev B boards. The DocoEng was measured on Rev A, with no wheel.
- **Inductance.** Neither motor's inductance has been measured.
- **Two units each.** Two units of each motor are not a population.
- **The 6.5″ lead's rise at walking pace,** which is faster than the windings alone explain.
- **The serial control path,** which has not yet been validated on hardware for 6.2.

The CHANGELOG's Known Issues and each manual's "What we do not know yet" section ([6.5″](MOTOR-6.5IN-TECHNICAL-MANUAL.md#9-what-we-do-not-know-yet), [DocoEng](MOTOR-DOCO-TECHNICAL-MANUAL.md#9-what-we-do-not-know-yet)) carry the full list.

## Going further

- **The methods, step by step:** [TECHNIQUES.md](TECHNIQUES.md).
- **The numbers:** the [6.5″ manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md) and the [DocoEng manual](MOTOR-DOCO-TECHNICAL-MANUAL.md).
- **How the driver works inside:** [Driver Theory of Operations](DRIVER-THEORY-OF-OPERATIONS.md).
- **Adding your own motor:** [ADDING_MOTOR.md](ADDING_MOTOR.md).
- **What each release changed:** [CHANGELOG.md](CHANGELOG.md).

---

## How to Contribute

This is a project supporting our P2 Development Community. Please feel free to contribute to this project. You can contribute in the following ways:

- File **Feature Requests** or **Issues** (describing things you are seeing while using our code) at the [Project Issue Tracking Page](https://github.com/ironsheep/P2-BLDC-Motor-Control/issues)
- Fork this repo and then add your code to it. Finally, create a Pull Request to contribute your code back to this repository for inclusion with the projects code. See [CONTRIBUTING](CONTRIBUTING.md)

---

> If you find this kind of written explanation useful, helpful I would be honored by your helping me out for a couple of :coffee:'s or :pizza: slices -or- you can support my efforts by contributing at my Patreon site!
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
