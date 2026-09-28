# Techniques — how we measured the motor and built the driver

![Project Maintenance][maintenance-shield]

[![License][license-shield]](LICENSE)

The 6.0 driver was rebuilt around measurement: every constant that places the motor's field, limits
its speed or stops it came from the motor itself, read through the driver's own sense channels. This
page collects the methods that got us there, so you can reuse them. You don't have to repeat our
work to use the driver. You only need these if you are adding a motor, changing the driver, or
building something of your own on the P2.

Each technique is written the same way: **the idea**, **how**, **a worked example** with our real
numbers, and **where it lives** in this repo.

| If you are… | Read |
|---|---|
| adding a motor | [Part 1](#part-1--characterizing-a-motor), then [ADDING_MOTOR.md](ADDING_MOTOR.md), which turns it into steps |
| deciding whether to trust a number — ours or yours | [Part 2](#part-2--trusting-a-measurement) |
| changing the driver, or writing your own P2 code | [Part 3](#part-3--engineering-on-the-p2) |

The worked examples are the 6.5″ hub motor. Its full record is the
[6.5″ motor technical manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md), and how the driver works is in
[Driver Theory of Operations](DRIVER-THEORY-OF-OPERATIONS.md).

---

## Part 1 — Characterizing a motor

### 1.1 Count revolutions by hand; don't calculate them

**The idea.** A motor's pole count sets every distance and speed the driver reports. Measure it with
a ground truth that shares nothing with the constant you are checking.

**How.** With the motor unpowered, mark the shaft or wheel and turn it a counted number of whole
revolutions by hand while a program counts hall transitions. Ticks per revolution is transitions ÷
revolutions, and electrical cycles per revolution is that ÷ 6. Two checks come for free: the hall code
at the end must equal the code at the start, and no illegal code (`%000` or `%111`) may appear.

**Worked example.** Three revolutions of a 6.5″ wheel gave **270 transitions**, 0 illegal, and the same
start and end code: exactly 90 ticks per revolution, 15 electrical cycles, 30 magnets. A figure of
"about 23 electrical cycles" had been suggested for hoverboard motors; it would have needed 414
transitions, and would have made every distance reading 53 % wrong.

⚠ **Beware circular checks.** Wheel travel per tick, a speed sweep's ticks per second, and the driver's
RPM against a program's RPM all *look* like confirmations, but each divides by the same 90 it claims to
confirm. Only the hand count doesn't.

**Where it lives.** `src/test_bench_t0.spin2` built with `-D T0_HAND` (its log lines begin `T0-12`) counts for you, with a
panel that tells you what to do. A program that starts the motor with no drive command and prints
`getRawHallTicks()` works just as well.

### 1.2 The hall order and the transition table

**The idea.** Three hall sensors give six legal codes, and there are only two orders they can come in:
`1-5-4-6-2-3` or `1-3-2-6-4-5`. Which one a motor calls "forward" is up to its maker.

**How.** With the driver not running, turn the wheel by hand in the direction you will call forward
and print the hall code: the three hall inputs are pins `basePin + 5` to `basePin + 7` of the motor's
pin group (U, V, W), so `pinread(basePin + 5 addpins 2)` returns the code as the driver sees it. Then write the motor's two tables in
`isp_bldc_motor.spin2`: an angle table (the rotor angle within the electrical cycle for each code) and
a delta table (the position step −1, 0 or +1 for each `old → new` transition).

**Worked example.** Both motors we support use the same delta table, in which the position rises through
1-5-4-6-2-3. They differ in which way is "forward": forward power drives the 6.5″ motor with positive
increments and the DocoEng motor with negative ones. So the table and the forward direction are two
separate facts to get right.

**What a wrong order looks like:** the motor won't turn, or moves a little and stops, or runs one way
but not the other.

**Where it lives.** `deltas65` / `hltbAngles` in `DAT { MOTOR-TYPE TABLES }`. `start()` refuses any
delta-table entry outside −1..+1 (`ERR_BAD_MOTOR_TABLE`), and the driver counts missed and illegal
transitions as it runs (`getHallIntegrityCounts()`).

### 1.3 Find the hall zero from the two directions' current minima

**The idea.** The halls tell you which 60° sector the rotor is in, not where the sector boundary sits
against true electrical zero. That offset, **Z**, is a fixed property of sensor placement. The field also
has to *lead* the rotor by some amount **L**. Sweep the commutation offset in each direction and find
where the current is lowest. If both directions want the same lead, their two minima sit symmetrically
about Z, and the midpoint gives you Z with L cancelled out.

**How.** At a fixed, moderate speed, for each direction, step the offset across its reachable range and
record net current (the reading less its rest zero) at each step. Find each direction's minimum. Z is
their midpoint; L is half their separation. Repeat at a second speed. **Z must not move with speed
(it's geometry), and L may.** That is the method's own check.

**Worked example.** At 49 ticks/s: Z = −3.8° ± 0.3 on one motor and −4.0° ± 0.3 on the other. At twice
the speed Z moved only 0.2–0.55°, while L moved 12.2°: geometry held still, and the drive parameter
didn't.

⚠ **The window you can sweep is bounded.** Too much lead and current climbs until the run has to abort.
Too little and the motor can't make torque, so it slows or faults. On this motor that left about 126° of
the 360° cycle to sweep. The minimum you find is a true local minimum, and theory says it is the only
one, but that is an argument, not a measurement.

**Where it lives.** `src/test_bench_scan.spin2` runs the sweep unattended, per motor and per direction,
fitting each minimum and reporting how close it sits to the fault edge.

### 1.4 Find the hall zero cold, from the motor's own voltage

**The idea.** Turn a motor with the bridge switched off and the magnets induce a sine wave on each phase.
Where that wave crosses and peaks is fixed to where the magnets are. Timestamp the hall edges and those
waves on one clock, and you have placed the halls against the magnets directly. No drive, no current and
no offset are involved.

**How.** Coast the bridge (all FETs off). Turn the wheel by hand in both directions, slowly and then
briskly, while the driver samples the three phase voltages every frame. For each phase, take the
**midpoint** between its rising and falling crossings, because the sense channels clip the negative
half-wave, which shifts each crossing. Average the two directions to cancel the halls' own hysteresis.

**Worked example.** Z came out at −3.31° and −3.25° on the two motors, within 0.35–0.7° of §1.3's
result, which is inside the constant's 1° resolution. Two methods that share no signal path agree. Slow
and brisk runs agree within 0.12°, and the three phases' peaks fall 120° apart in the order the drive's
phase convention predicts, so the frame the method assumes is itself tested.

**Why it matters for you:** this needs no current resolution at all, so it works just as well on a Rev A
board (5 mV/A) as on Rev B (150 mV/A). Nothing is driven, so nothing can fault or run away.

**Where it lives.** The `dual-align` tier of `src/test_bench_dual.spin2`.

### 1.5 Measure the lead at several speeds — it is not a constant

**The idea.** The lead that gives least current changes with speed, so a single fixed offset pair is a
one-speed tune. Measure L at several speeds, one octave apart, and let the driver interpolate.

**How.** Hold Z fixed. At each speed, step L across the reachable window in both directions and record
net current. Keep only steps where the wheel held its commanded rate. Record the **flat region**, not
just the minimum, and choose a table value inside it.

**Worked example.** At 49 ticks/s the lowest-current lead was 13–23°; at 98 ticks/s it was −2 to 8°; at
196 and 393 ticks/s, 3–8°. The table holds 20.5°, 5°, 8° and 8°. Against a flat 18°, the table draws
**24–78 % less current** from 107 to 374 ticks/s.

⚠ **The textbook model gives the wrong sign.** It says the lead should *grow* with speed, because
current lags voltage more at higher frequency. On this motor it falls, then holds. Measure; don't design
from the model.

⚠ **The offset and the duty servo's setpoint add.** Both place the field. Carry the lead in the offset,
which acts instantly, and leave the setpoint alone. Correcting both counts the same correction twice, in
a basin where 30° of error costs 12.7× the current.

**Where it lives.** The `dual-lead` tier of `src/test_bench_dual.spin2`; the table is `leadIncrTbl` /
`leadTenthsTbl` in `src/isp_bldc_motor.spin2`.

### 1.6 Choose the speed ceiling by duty reserve, not by where the motor gives up

**The idea.** Driven faster and faster, a motor keeps following well past the point where the drive runs
out of voltage. It does so by field weakening, at a steep cost in current, and it can slip. Put `power`
100 where the drive still has output in hand.

**How.** Step the commanded speed up on a lifted wheel, recording duty against its ceiling and current.
Find the **knee**, where duty first reaches its ceiling. Set the ceiling at the fastest speed that keeps
your chosen reserve. Step down to find the floor: the slowest speed that still turns steadily at its
commanded rate.

**Worked example.** At 18.5 V duty first capped between 175 and 185 × 10⁶ (the speed increment per drive
pass). Above that, the wheel still followed up to 245 × 10⁶, drawing 2.3–2.6 A unloaded against 0.3–0.4 A
at the knee, and one motor lost synchronism with a 23–25 A peak. The ceiling is 165 × 10⁶, where duty sits
at 92–93 % of its maximum: 294 RPM, 2.54 m/s. Every speed down to 100,000 (about 0.2 RPM) turned steadily.
The other voltages' ceilings are that one number scaled by voltage, and our earlier measurements at other
voltages followed that line to within 2.5 %.

**Where it lives.** The `dual-limits` and `dual-limits-top` tiers of `src/test_bench_dual.spin2`;
`confgurePowerLimits()` in the driver.

### 1.7 Let the driver measure the winding

**The idea.** The driver already has a current sense and a bridge, so it can measure winding resistance
itself at start, without a meter.

**How.** Drive each phase pair in turn (U→V, V→W, W→U) at low duty with the rotor still, since back-EMF
would bias the reading, and read the DC-link current: R = d² × V × rSense ÷ net mV. Use the *measured*
supply voltage.

**Worked example.** About 0.48 Ω phase to phase on both motors, each reading good to about ±6 %. The first
calculation used the nominal 18.5 V and came out 12 % low, which is exactly 18.5 ÷ 20.72, the pack's real
voltage. The instrument's assumption was wrong, not the motor. The negative case: with one lead withheld
in firmware, the two pairs through it read "not visible" and the third still measures, in 10 of 10
starts.

**Where it lives.** The opt-in winding check of `start()` (`getHealth()` reports it); the optional
[pack voltage sensor](VOLTAGE-SENSOR.md) supplies V.

### 1.8 Characterize how it stops, not only how it runs

**The idea.** Coasting and shorting the phases differ by two orders of magnitude, and what matters to a
robot is between them. Measure each from speed.

**How.** From several speeds, force the stop and count ticks and milliseconds to rest.

**Worked example.** From about 1.2 m/s, one wheel coasted 54 ticks in 536 ms and stopped in 1–2 ticks,
9 ms, when shorted. Shorting 10 % of each 10 ms period stopped it in 282 ms, and the braking grows
strongly non-linearly with the percentage (10 / 25 / 50 % added about 0.8×, 5× and 30× the coast's drag).
That is why the driver's default fault response uses a gentle graded short rather than a hard one: a hard
short behind a tall platform is a tip-over.

**Where it lives.** The `dual-fault` tier of `src/test_bench_dual.spin2`; `setFaultResponse()` and
`BRAKE_PCT` in the driver.

---

## Part 2 — Trusting a measurement

These are general. They are what separated the numbers we trust from the ones we threw away.

### 2.1 A check that cannot fail proves nothing — measure the negative case

**The idea.** A test has only been shown to work once it has been shown to *fail* on a case that
should fail. An instrument shown only healthy input hasn't been tested.

**How.** For every check, build the failing case, and build it in firmware where you can, so it can be
made on demand and costs no wear: a lead withheld, a hall pair read as swapped, a limit set below the
load. Run the negative first.

**Worked example.** The start checks were certified by making them fail: a withheld lead read ≤ 31 mV
against 777–823 mV healthy; a hall pair swapped in firmware failed the wiring walk 3 of 3; an unplugged
hall connector was caught 10 of 10. The same discipline found a real hazard. An unguarded walk on a
miswired motor drew a 26 A peak, so the walk now trips at about 1 A.

### 2.2 Independent routes that agree

**The idea.** One measurement can be wrong in a way you can't see. Two methods that share no signal path
and agree are much harder to fool, so look for them deliberately.

**Worked example.** The hall zero came from current minima (§1.3) and from back-EMF with nothing driven
(§1.4), and they agree within 0.7°. The value of alignment showed up on three observables that share no
path: the current sense, the duty servo's own demand (83.7 % → 53.9 %), and the wheel meeting its
commanded rate within 1 % in both cases.

### 2.3 Every test prints its own verdict

**The idea.** A run should need no interpretation to say whether it passed. Each check prints `PASS`,
`FAIL` or `NOMEAS`, with the value it judged and the band it judged it against, so the log alone is the
record.

**How.** Write the pass criterion into the program before the run. Treat `NOMEAS`, meaning *the
condition never arose*, as its own result: it is not a pass. A zero can mean the defect is absent, or it
can mean the thing that triggers it never happened.

**Where it lives.** The `SIGNOFF` records in every `src/test_bench_*.spin2`.

### 2.4 When the measurement and the system disagree, suspect the measurement

**The idea.** Before concluding the motor or the driver is wrong, check the instrument's assumptions:
its scale, its zero, its supply voltage, its timing.

**Worked example.** The winding resistance read 12 % low: a nominal voltage, not the winding (§1.7). The
current sense's rest offset differs per board and per start, so every reading here is *net* of a zero
taken with nothing driven, and a zero is only valid within the driver session that took it.

### 2.5 A desk model before a bench run

**The idea.** When a defect has a known symptom, reason out what produces it from the source, and
reproduce it in a model on the desk, before spending bench time. The bench then certifies a fix instead
of exploring.

**Worked example.** A current kick at every speed change grew with the speed arrived at, not with the
size of the step. The cause was in the code: on the one pass where a ramp reached its target, the field
did not advance, so every arrival stepped the field back by a whole increment. A desk model reproduced
the logged kicks to within about 10 mV before the fix was built. After the fix the worst kick fell from
64–183 mV to 13–16 mV. The start surge of the 5.x driver was predicted the same way: an integral servo
whose fixed gain was too high for a rotor that is only slightly stiff at low speed.

### 2.6 Say what is not known

**The idea.** Record the conditions a number was measured under, and what it does not cover. Our speed,
current and stop figures are all with the wheels lifted. The [manual](MOTOR-6.5IN-TECHNICAL-MANUAL.md)
keeps a list of what is not yet known, and why each item matters.

---

## Part 3 — Engineering on the P2

### 3.1 One owner for shared state

**The idea.** When two cogs can write the same hub long, sooner or later they write it in the wrong order.
Give every piece of shared state exactly one writer, and have everyone else *ask* it.

**How.** The 6.0 driver runs one Spin2 **front cog** per drive. It is the only writer of the driver's
command, the e-stop, the stop limits and the tracking, and the only caller of `cogatn`. A public method
validates its arguments on the caller's cog, posts a request into that cog's own slot (indexed by
`COGID()`), and waits, bounded, for the answer. Each slot is written sequence-number-*last* by the caller
and answered sequence-number-last by the front cog, so every long has one writer.

**Worked example.** In 5.x, the drive command, the e-stop, the stop limits and the tracking window each had
two writers: the caller's cog and the sense cog. The consequences included a stop arriving between two
synchronized writes and stranding an ATN, and stop limits checked 8 times a second, so a stop could be up
to 125 ms (about 29 cm at top speed) late. With a single owner, limits are checked every millisecond
against the driver's own stop plan, and they land within 2 ticks.

**Where it lives.** `frontLoop()` in `src/isp_bldc_motor.spin2`;
[Theory of Operations §1 and §5](DRIVER-THEORY-OF-OPERATIONS.md).

### 3.2 Check the Spin2 ↔ PASM2 memory layout at start

**The idea.** The PASM driver reads and writes Spin2 `VAR` longs by their offset from one pointer. Spin2
declaration order *is* the interface, and nothing in the compiler checks it. So check it yourself, at
run time, before the cog launches.

**How.** `isAbiLayoutValid()` compares the addresses of the first and last long of each shared run
against the count constants, `DRVR_STATUS_LONGS_COUNT` (24) and `DRVR_PARAMS_LONGS_COUNT` (27), and checks
that named longs sit at their index constants. A mismatch refuses `start()` with `ERR_ABI_MISMATCH` instead
of running a driver that reads the wrong longs.

**The rule that goes with it:** append only. A new long goes at the end of its run, and the Spin2 `VAR`
order, the PASM register block and the count constant change together.

### 3.3 Prove a PASM rewrite identical before you trust it

**The idea.** When you rewrite assembly to save space, "it still runs" isn't proof. Run the old and new
images side by side in an emulator on the same stimulus, and compare everything they do.

**How.** `tools/pasm_equiv` compiles the baseline and the candidate driver, runs both in an
instruction-level P2 cog emulator, and at every PWM frame compares every hub write, every pin operation,
every CORDIC input, and every live register by name. It stops at the first difference and prints the
instructions that led to it. It executes the compiled longs, never the source, and refuses any opcode it
doesn't model rather than skipping it.

**Worked example.** Five rounds of reduction took the driver from **492 to 441 of 496 cog longs**, and its
LUT use from 507 to 457 of 512, each round proved equivalent. The first round was checked over 2,055
scenarios and 8.1 million frames. The tool also found a real latent defect on its first run: the first drive
pass read a register that no frame had yet written.

**Where it lives.** `tools/pasm_equiv/` (its README explains the method and its limits).

### 3.4 Two code images in the LUT

**The idea.** Code that runs only once, the start sequence, is dead once it has run. Load it into the
LUT, run it, and then load the run-time code over it at the same addresses.

**How.** Partition the code by its call graph, so nothing in cog RAM or the run image ever calls into the
start image. The start sequence's last act loads the run image over itself. LUT use is then the larger of
the two images, not their sum. The same trick applies to cog RAM: longs used only during start can be
reused as registers that only the drive loop uses. In this driver, 21 of them are.

**Where it lives.** `lutCodeStart` / `runCodeStart` and `loadOverlay` in `src/isp_bldc_motor.spin2`;
[Theory of Operations §4](DRIVER-THEORY-OF-OPERATIONS.md).

### 3.5 Read all three halls in one instruction

**The idea.** Read the three hall lines separately and a switching transient can land between the reads
and combine into a code the motor never produced. Read them together.

**How.** Read the three pins in a single instruction, so all three bits come from the same instant. Then
look up the `old → new` transition in a table that gives the step and flags a missed or illegal
transition.

### 3.6 Select configuration at compile time, and gate every configuration

**The idea.** When one configuration file serves programs that need different settings, let each program
select its settings by name at compile time, rather than having someone comment blocks in and out. Then
"it compiles" can be checked for every configuration, and a program that selects nothing is an error
rather than a silent default.

**How.** `isp_bldc_motor_userconfig.spin2` carries a single-motor and a two-wheel configuration inside
`#IFDEF CFG_SINGLE_MOTOR` / `#ELSEIFDEF CFG_DUAL_MOTOR`, ending in `#ERROR`. A top-level program
`#DEFINE`s its symbol and `#PRAGMA EXPORTDEF`s it, which carries it into every object it includes (a plain
`#DEFINE` reaches only its own file). The PNut-TS-only directives, `#PRAGMA` and `#ERROR`, sit inside
`#IFDEF __PNUT_TS__`, a symbol only PNut-TS defines, so the same files still build with PNut, where the
selection is made in the configuration file instead. `tools/build-check.sh` then compiles every library object under
each symbol with `-D`, compiles every program as written, checks that a build selecting neither is refused
with its message, and builds both flagship demos with and without `-d` (DEBUG). It never edits a source
file to do it.

### 3.7 Budget your DEBUG output, and keep headroom

**The idea.** A debug build has a fixed budget for its `debug()` data. Past it, the build fails, or the
output you needed isn't there. Treat the budget as a design limit, with room to spare.

**How.** Route output through channels (`DBGCH_*`) that a mask compiles in or out. Keep strings in hub
memory and build lines at run time through one shared helper, rather than writing many literal
`debug()` statements.

**Worked example.** Rebuilding the demos' output through shared helpers cut the R/C demo's DEBUG data
from 13,406 to 10,488 bytes against a 12,404-byte limit, with the output unchanged line for line. Every
debug build now has at least 1,374 bytes spare.

### 3.8 DEBUG PLOT panels as a bench UI

**The idea.** A test that needs a person needs a screen that keeps them in step: what the program is
doing, the one thing to do next, what they should see, and a button to say done. The P2 DEBUG `PLOT`
window can be that screen, with no host software.

**How.** Draw the panel as bitmap layers, and make every action a **titled button** hit-tested through
`PC_MOUSE`. A click costs less than focusing a window to press a key. Two traps: declare `cartesian 1`
right after opening the window, since the default coordinate basis puts y up from the bottom-left and
your hit tests will miss; and put window titles in single quotes with no parentheses, because a
double-quoted title is silently dropped and a `)` ends the `debug()` call.

**Where it lives.** `bmpanel` in `src/test_bench_dual.spin2`, with its art generated by
`tools/gen_dual_assets.py`.

### 3.9 Let the driver publish its own stop plan

**The idea.** A distance or time limit has to fire *before* the limit, by the stopping distance. Rather
than have Spin2 estimate that, have the driver, which owns the ramp, work it out and publish it.

**How.** After each drive pass the PASM driver computes the jerk-limited stop's closed form in integer
arithmetic, spreading the work a third of a plan per frame over the next nine frames, and publishes
passes-to-rest and travel-to-rest in its status block. The front cog only reads and compares.

**Worked example.** Stop limits armed at cruise and mid-ramp came to rest within 2 ticks and 3 ms of
their limits. A stop from about 1.25 m/s ran 122 ticks against the driver's own prediction of 120.

### 3.10 Scripts that show their commands

**The idea.** A helper script that runs your tools should never hide what it runs.

**How.** `tools/bench-run.sh` compiles and loads one test by a short name, and echoes every command
verbatim before running it, so the transcript can be replayed by hand. Every value the run needs is chosen
by name, never typed.

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
