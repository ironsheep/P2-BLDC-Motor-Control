# Bench Test Plan — settling the two driver studies

**Date:** 2026-09-10
**Closes bench citations in:** [`DRIVER-AUDIT-2026-09-09.md`](DRIVER-AUDIT-2026-09-09.md)
and [`DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md`](DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md)
**Hardware policy:** 6.5″ hub motors, **Rev B boards only** (see §1).
**Design goal:** the fewest physical setups, the most verdicts, the least bench time.

---

## 0. The idea that shapes this plan

Bench time is the expensive thing, so the plan is built backwards from that:

1. **Prove everything provable with no motor first.** A surprising number of the
   open findings are arithmetic or configuration defects that need a P2 and a
   board but *no motor, no battery, no motion*. Tier 0 closes nine of them in
   half an hour at zero risk.
2. **Make the P2 its own instrument wherever the P2 is not the thing under
   test.** Speed, overshoot, fault boundaries, coast-down and ramp behaviour can
   all be measured from `pos` and `getct()` — no scope, no encoder, no tape
   measure. And a **≈$15 front end (§2A)** puts bus voltage, bus current and board
   temperature on three spare P2 pins, so even the electrical reference readings
   are captured by the harness rather than read off a panel meter by a human.
3. **Write the pass/fail thresholds into the harness before the session.** Every
   test below has a pre-stated numeric criterion. The bench session should end
   with verdicts, not with a pile of CSV to interpret next week.
4. **One physical rig for almost everything.** Only one test in the entire suite
   genuinely needs the platform on the floor.

Net: **Tier 0 ≈ 30 min (no motor) · Tier 1 ≈ 2 h (wheels up) · Tier 2 ≈ 5 min
(wheels down).** One evening.

---

## 1. On the Rev A / Rev B decision

> *"No Rev A use until we get the driver protecting the boards correctly — the
> Rev B's protect themselves."*

**This holds, and the code supports it more strongly than the safety argument
alone.** Three independent reasons, in order of weight:

1. **The driver contributes zero protection today.** Finding **S-2**: `sense_i_`
   is sampled every 22.7 µs and is never the subject of a `cmp` anywhere in the
   PASM. There is no current limit. So on a board that does not protect itself,
   the *only* thing standing between a stalled 6.5″ hub motor and the FETs is
   how quickly a human notices. Deferring Rev A until the limiter exists is the
   correct sequencing, not caution.
2. **Rev B is also the better instrument.** Rev A is 0.005 Ω at gain 1 → 50 mV
   at 10 A, about 1.5 % of the 3.3 V ADC span. Rev B is 0.003 Ω × 50 → 1.5 V at
   10 A, about 45 % of span. **Rev B's current signal is 30× larger.** For
   settling **S-3** (the current-scaling defect) you want the channel with
   thirty times the signal-to-noise, and you want it before you trust any
   number Rev A produces.
3. **Nothing in the open findings actually requires Rev A.** The board-revision
   defects — audit root cause **A** (**A1**, **A2**, **A3**) — are about the
   *branching*, and every one of them is provable from variables printed on a
   Rev B board in Tier 0. Rev A's own constants (`F_REV_A_RSENSE`, its detection
   path) can be derived arithmetically once the Rev B scale factor is known, and
   confirmed on hardware later, after the limiter lands.

**Two consequences worth carrying forward:**

- The **C-6** bus-voltage divider constant this suite produces will be
  **Rev B specific**. If the two revisions divide the phase pins differently the
  constant will not transfer, and Rev A will need its own single confirming
  reading when it comes back into play. Noted, not blocking.
- Rev B's self-protection means a Rev B trip may be **invisible to the P2** — the
  board may current-limit or shut a gate driver without the driver code ever
  seeing anything but a growing angle error. Worth watching for in **T1-7**: a
  fault that occurs at *lower* commanded speed than the model predicts, with
  `duty_` **not** saturated, is a signature that the board intervened, not the
  driver. That is useful information, not a problem.

**One safety consequence of a finding, for the session itself:** do not use
`emergencyCutoff()` as your panic button. Finding **S-4** — it self-cancels in
about 250 ms. Keep a physical battery disconnect within reach and use that.

---

## 2. Rigs and instruments

**Confirmed 2026-09-10: the dual platform goes up on blocks, and each motor can
be run independently in isolation in that configuration.** So there is exactly
**one physical setup** for the entire suite, and it supports both single-motor
and two-wheel tests without rebuilding anything.

### Rig A — "wheels up" (Tier 0 and Tier 1)

Assembled dual platform on blocks, both wheels free to spin, both Rev B boards
powered. Single-motor tests drive one wheel and leave the other stopped. For
Tier 0 the motor rail stays **off** and the motors may stay unplugged; the P2 and
board logic alone are enough.

### Rig B — "wheels down" (Tier 2)

The same platform, lowered. One 30-second observation, then done.

**What the dual rig buys that a single-motor fixture would not:** a matched pair
of channels, which turns several tests into controlled A/B comparisons —
**T1-11** (are the two wheels running equivalent commutation?) and **T1-12** (the
channel-swap discriminator for the user's field fault). Both are new, both are
high value, and neither was plannable before the rig was known.

### Instruments

**None. Build a front end instead — see §2A.**

An inline watt meter was the original recommendation and it is the wrong tool,
for the reason Stephen raised: **you cannot get at it from the harness.** Reading
it means holding a condition steady long enough for a human to look at it or
photograph it, which

- breaks the automation the whole plan is built on,
- forces the motor to sit at each rung longer than the test needs, and
- is **useless for every transient measurement** — the ramp captures in
  **T1-7**, the coast-down in **T1-1**, the moment of a fault. Those are the
  measurements that matter most, and a panel meter cannot see them at all.

One watt meter is still worth having for a **single** one-time validation of the
front end at build time (§2A). After that it goes back in the drawer.

---

## 2A. The bench front end — let the P2 be its own instrument

### The key fact

**Every P2 pin has an ADC.** The motor driver already uses exactly this —
`P_ADC_1X | P_COUNT_HIGHS` with GIO/VIO self-calibration
(`isp_bldc_motor.spin2:1644-1689`). So a front end needs **no ADC chip, no I²C,
no microcontroller**. It only needs to *scale* bus voltage and bus current into
0–3.3 V and hand them to two spare pins. That is a handful of passives and one
sensor.

Everything is then sampled by the P2, synchronously with the tests, at whatever
rate we choose, with timestamps from the same `getct()` the measurements use.

### Three channels

| Ch | Measures | Range | Front end |
| --- | --- | --- | --- |
| **V** | bus voltage at the battery | 0–30 V | resistive divider, ~10:1 |
| **I** | bus current, **bidirectional** | ±30 A | Hall current sensor + output divider |
| **T** | board / FET temperature | ambient–100 °C | 10 kΩ NTC + 10 kΩ divider |

**Why bidirectional current matters:** it makes **regeneration visible**.
**T1-1**'s brake test should show current flowing *back into the battery*, and
nothing in this system can see that today. That is a battery-safety question
nobody has been able to ask.

**Why the temperature channel is worth $0.50:** the plan currently says *"put a
hand on the board's FETs between trials"* — because there is no thermal sensing
anywhere in this system (**S-1**). An NTC taped to a FET package turns that into
a logged number, and turns **T1-7**'s repeated-fault trials into a thermal
record. It does not need to be accurate; the *rise* is the signal.

### Bill of materials

| Part | Purpose | ~Cost |
| --- | --- | --- |
| **ACS758LCB-050B** Hall current sensor (or clone breakout) | ±50 A, bidirectional, **galvanically isolated**, 100 µΩ insertion | $6–12 |
| 91 kΩ + 10 kΩ, 1 % | bus voltage divider (10.1:1 → 30 V = 2.97 V) | $0.20 |
| 10 kΩ + 10 kΩ, 1 % | halve the sensor's 5 V-centred output into P2 range | $0.20 |
| 10 kΩ NTC + 10 kΩ 1 % | temperature divider | $0.50 |
| 3 × 1 kΩ | series pin protection | $0.10 |
| 3 × BAT54S (or 3.3 V zeners) | clamp to rails | $0.50 |
| 3 × 1–10 nF | anti-alias / noise | $0.20 |
| Protoboard, header, bullet/XT60 pigtails | build | ~$5 |
| | **Total** | **≈ $15** |

**Current-sensor choice — two options:**

- **ACS758LCB-050B (recommended).** Screw terminals, through-hole, easy to put in
  a 25 A lead. 100 µΩ insertion resistance → ~60 mW at 25 A, no heat problem.
  Bidirectional, ~40 mV/A at 5 V → 2.5 V ± 2.0 V; halve it → 1.25 V ± 1.0 V,
  **20 mV/A at the pin**. Isolated, so it can go in the *high* side with no
  level-shifting risk.
- **ACS712-30A** is the cheap-and-common alternative (~$3) but its internal
  conductor is 1.2 mΩ → **750 mW at 25 A in a SOIC-8**. It will run hot and it
  saturates right where a stalled hub motor gets interesting. Use it only if
  currents stay well under 20 A.
- A 1 mΩ shunt + INA181A3 is cheaper and more accurate but is not isolated and
  needs SMD soldering. Fine if that is preferred; it changes nothing downstream.

### Where it goes

- **Voltage divider** across the battery terminals. **Verify P2 ground and
  battery negative are actually common before connecting it** — they should be
  through the motor board, but a floating ground gives a meaningless reading.
- **Current sensor** in **one board's positive lead**, not the battery main. Then
  it reads *that wheel's* current directly. Because the rig runs each motor
  independently, every test that needs per-wheel current is a single-motor test
  anyway — one sensor is sufficient. Add a second only if simultaneous dual-wheel
  current is wanted for **T1-11**.
- **NTC** taped or thermal-glued to a FET package on the board under test.
- **5 V** for the Hall sensor from the P2 Eval's 5 V rail.

### Pin budget

Both dual-motor 6.5″ config blocks are covered by **P50, P51, P52**:

| Config | Boards occupy | P50–P52 free? |
| --- | --- | --- |
| `LEFT=PINS_P0_P15, RIGHT=PINS_P16_P31` | P0–P13, P16–P29 | yes |
| `LEFT=PINS_P16_P31, RIGHT=PINS_P32_P47` | P16–P29, P32–P45 | yes |

P50–P52 also avoids the commented-out LA header (P40–P47) and the optional
optical encoder (P48–P49) at `isp_bldc_motor.spin2:1217, 1195`, so enabling that
instrumentation later does not collide.

### Pin protection — do not skip this

A divider whose bottom resistor goes open puts the full bus on a P2 pin and kills
the chip. Each analog input gets **1 kΩ in series plus a Schottky clamp to 3.3 V
and to ground**. Ten cents and thirty seconds. The Hall channel is inherently
safe (isolated), but clamp it anyway for uniformity.

### The bench-instrument cog

Four of eight cogs are in use in the dual configuration (2 drivers, 1 sense,
1 main). **Dedicate one spare cog to sampling.**

It does nothing but: configure the three pins as `P_ADC_1X | P_COUNT_HIGHS`,
sample them in a tight loop, and write `(getct(), V, I, T)` records into a hub
ring buffer. Tests then simply say *start capture / stop capture / dump*, and get
a timestamped trace of exactly what the battery and the board were doing,
synchronised with everything else the harness logged.

**Sample rate:** the resolution/rate trade is the same one the driver makes at
`isp_bldc_motor.spin2:188` — a longer `X` count window gives more bits and fewer
samples. **10 kHz is a good default**: five samples per 500 µs drive-loop step,
which is enough to see a ramp evolve and a fault arrive, with ~14 bits of
resolution.

**This one facility serves T1-1, T1-3, T1-5, T1-6 and T1-7 simultaneously.**

### Calibration

1. **Self-zero, automatically, before every run.** With the motors stopped,
   whatever the current channel reads *is* zero amps. Logging and subtracting it
   each time removes the Hall sensor's offset and its drift entirely — the single
   largest error term, eliminated for free by automation.
2. **Voltage channel needs no calibration** beyond the resistor tolerance; 1 %
   parts give ~1 % accuracy, which is far better than needed to settle **C-6**.
3. **One-time validation at build time.** Put the watt meter in line *once*,
   run a couple of steady load points, confirm the front end agrees. Then remove
   it permanently. Human in the loop once, at build, not once per test.
4. **Write the ADC scaling correctly in the harness** — including the `sar`
   normalisation the driver omits (**S-3**). This is deliberate: the harness then
   contains a **correct reference implementation** of the same computation the
   driver gets wrong, so comparing the two is the cleanest possible statement of
   the bug — and the corrected routine is the one the fix sprint will need.

### What this changes in the plan

| Test | Before | After |
| --- | --- | --- |
| **T1-5** absolute current calibration | 3 manual meter readings | fully automatic; runs as part of the T1-3 ladder |
| **T1-6** bus voltage | 2 discrete battery states, manual DMM | **no discrete states needed** — run the ladder as the pack drains and get a continuum of bus voltages, logged |
| **T1-7** ramp/fault | current and thermal invisible | current trace through the fault, and a temperature record across trials |
| **T1-1** coast-down | position only | **plus regen current during braking** |

**Manual acts in the whole suite drop from six to three:** one hand-brake
(**T1-9**), one cable swap (**T1-12**), one observation (**T2-1**).

### One assumption this front end tests rather than trusts

The board presents a single current channel (`pin_adc_cur_i`, base+4) alongside
three phase channels, which strongly suggests a **DC-link shunt** — in which case
the front end's bus amps and the board's `sense_i_mV` are directly comparable and
**T1-5**'s calibration is valid.

**T1-5 checks this rather than assuming it**, by looking for proportionality
across the whole ladder. If they track, it is bus current. If they do not track
at all, the board's channel is measuring something else — useful to know, and
**T1-4**'s clock-dependence proof of **S-3** stands regardless, because it never
depends on an external reference.

### Scope: these are test fixtures

**Everything in §2A is bench equipment, not product hardware.** Nothing here is
proposed for the shipped library or for users to build. It exists so the harness
can measure what the board claims, and it stays on the bench.

**Where a genuine product-side need does exist** — exactly one — see **C-6c** in
the study: there is **no low-voltage cutoff**, so this library will drive a LiPo
flat and damage it with no warning. That gap is closed by a *configuration*
change (ask for `BATTERY_CELLS` instead of a voltage enum) plus runtime voltage,
not by asking users to build hardware. It ranks below **C-5**, the
fault-visibility work, and **S-3**.

### It is not throwaway

The same front end is what validates the current limiter when **S-2**/**C-5** are
built in the fix sprint. Build it once, keep it on the bench.

## 2B. The meter already on the system — anchors, not traces

**Added 2026-09-10, revised the same day when the meter's specification arrived.** Stephen has
a watt/voltage meter inline on the system, human-readable only.

### The instrument — vendor specification, verbatim

> Provides 8 Electrical Readings: Current (A), Voltage (V), Watts (W), Amp-hours (Ah),
> Watt-hours (Wh), Peak Amps (Ap), Minimum Volts (Vm), Peak Watts (Wp).
>
> High Precision: Measures 0-150 Amps, Resolution 0.01 Amps. Measures 0-60 volts, Resolution
> 0.01 volts. 0 - 6554W, resolution 0.1W. 0 - 65Ah, resolution 0.001Ah. 0 - 6554Wh, resolution
> 0.1Wh.

**Placement, confirmed:** between the pack and the whole system.

### This is not the instrument §2 dismissed

§2 rejected "an inline watt meter" as useless for transients. That judgement was made against
an assumed 3-reading meter. **This one has three latching extremum registers — `Ap`, `Vm`,
`Wp` — and two accumulators, `Ah` and `Wh`.** A latch converts a transient into a number a
human can read *after* the event. That is a different instrument, and it reaches several
measurements the plan had assigned to the §2A front end.

The limitation that survives: **you get the extremum, never the shape.** The peak current at a
fault is readable; the current *trajectory* into the fault is not. Anything needing a waveform
— C-5's lag-vs-duty relationship, the 500 µs ramp evolution — stays inside the harness.

### What each reading buys

| Reading | Serves | Notes |
| --- | --- | --- |
| **V** | **T1-6 / C-6**, AK, C-6c | 0.01 V on an 18.5 V pack = **0.05 %** — far finer than C-6's few-percent criterion needs |
| **A** | **T1-5 / S-3** absolute anchor | 0.01 A; steady-rung reads only (the live display averages) |
| **W** | T1-3 efficiency cross-check | derived |
| **Ah** | T1-1, T1-7 energy — **only with repetition**, see below | 0.001 Ah |
| **Wh** | coarser than Ah for our energies | 0.1 Wh = 360 J — too coarse for anything here |
| **Ap** — peak amps | **T1-7 current at fault**; sizing the §2A sensor | **the big one** — see below |
| **Vm** — minimum volts | **C-6c low-voltage cutoff**, AK, C-5 | the worst sag under aggressive ramp, latched |
| **Wp** — peak watts | T1-7 severity | derived from the same event as Ap |

### `Ap` gives T1-7 its current-at-fault — without the front end

**T1-7 provokes faults deliberately by sweeping `ramp_inc`.** The plan assumed the current at
the moment of fault needed a logged trace. It does not: **reset the peak registers, run one
ramp trial, let it fault, read `Ap` and `Wp`.** That is the fault current, latched.

Repeat per `ramp_inc` value and you get the fault boundary *in amps*, which is the number
**S-2**'s current limiter will eventually be designed against.

`Vm` from the same trial gives the sag floor at fault — which is the other half of the story,
and feeds **C-6c** directly.

> ### ANSWERED 2026-09-10 (Stephen): **the peak registers reset ONLY on a power cycle.**
>
> There is no reset control. Every `Ap` / `Vm` / `Wp` reading is the extremum since the meter
> last received power, so **each trial that needs a fresh peak needs a power cycle first.**
>
> **The harness already accommodates this and needs no change** — T1-7 is trial-selectable by
> design (prompt for a `ramp_inc` index, or `0` for the whole sequence). Under this regime the
> operator runs trials one at a time and the power cycle *is* the natural boundary. That was
> the point of building it that way before the answer was known.
>
> **What it costs is pacing, and the size of that cost turns on one thing not yet
> determined:**
>
> > **Does the P2 survive a pack disconnect?** The meter sits between the pack and the whole
> > system, so cycling it means breaking the pack connection. **If the P2 Edge is USB-powered
> > from the Mac it stays alive** — the motor rail drops, the meter resets, and the harness
> > keeps running, so trials can be prompted in sequence within a single run. **If the P2 dies
> > with the pack**, it is one trial per program invocation and T1-7's sweep costs a full
> > load-and-run each. Determine this at **§8.1**; it changes session length substantially and
> > changes no code either way.
>
> **Two consequences to build into the procedure:**
>
> - **Re-take the quiescent zero after every power cycle.** If the peaks reset with power, so
>   do `Ah`/`Wh`. Never carry a zero across a cycle.
> - **That reset is also a convenience:** each cycle hands you a clean `Ah` baseline, which is
>   exactly what the N-repetition energy method (above) wants — no arithmetic to subtract a
>   previous run's accumulation.
>
> ### ALSO 2026-09-10 (Stephen): **the display CYCLES, one reading every two seconds.**
>
> The meter does not show all eight readings at once — it rotates through them. **A full
> rotation is therefore ~16 s for 8 readings**, and two values you want are never on screen
> at the same instant.
>
> **This sets the hold dwell, and the plan's original ~10 s is too short.** A steady rung must
> be held for **at least one full rotation plus margin — budget 20-25 s per anchored rung**,
> not 10. Holding for less means the operator either misses a reading or has to command the
> rung twice.
>
> **What it does *not* affect:** the latched extrema. `Ap`/`Vm`/`Wp` hold their value until the
> next power cycle, so they can be read at leisure *after* the event, however long the rotation
> takes. This is a second, independent reason the latched registers are the right instrument
> for **T1-7** and the live display is not.
>
> **Two procedural consequences:**
>
> - **Enter-driven, never timer-driven.** The harness must wait for Enter rather than advancing
>   on a fixed dwell — a fixed dwell that happens to be shorter than the rotation silently
>   costs a reading. The dwell is a *minimum*, the keypress is the advance.
> - **Order the reading sheet's columns to match the display rotation**, so the operator writes
>   values down in the order they appear instead of hunting for them. Record the actual
>   rotation order at §8.1 and generate the sheet's column order from it.
>
> **Still to check:** **the peak detector's sampling bandwidth.** Unspecified by the vendor. A
> detector sampling at ~100 Hz will under-capture a fast excursion, so treat `Ap` as a **lower
> bound** on true peak current until it is sanity-checked against a rung whose steady current
> is already known from the `A` reading.

### The Ah accumulator needs repetition — a single stop is far below resolution

**Correcting an earlier claim in this file.** `Ah` was described as giving T1-1 an energy
column per stop mode. Run the numbers and a *single* stop does not reach the resolution:

- 0.001 Ah at 18.5 V = 0.0185 Wh = **66.6 J per count**.
- A 6.5″ hub wheel, ~2 kg effectively at the rim, r ≈ 0.083 m → I ≈ 0.0136 kg·m². At ~274 RPM
  (28.7 rad/s), its kinetic energy is ½Iω² ≈ **5.6 J**.

**One stop is ~5 J against a 66 J resolution — an order of magnitude below the noise floor.**

**The save is repetition, and the harness can automate it.** Run *N* identical
accelerate-then-stop cycles in one stop mode, read `Ah` before and after, and A/B against the
same *N* cycles in another mode with an identical acceleration profile. The drive energy
dominates and is common to both, so **the difference isolates the stop mode.** At N = 50 the
per-mode term is ~280 J ≈ 4 counts — resolvable.

> This is the general pattern worth remembering: **accumulator + N repetitions turns an
> unreadable single event into a readable number.** The human reads two values; the harness
> does the fifty repetitions.

### What the front end is still needed for

Genuinely narrowed. After this meter, the §2A front end's irreplaceable jobs are:

- the **shape** of a transient, not its extremum — C-5's lag-vs-duty evolution;
- **regen magnitude** (this meter is very likely unidirectional — see below);
- **thermal** (**S-1**) — nothing here measures it;
- **validating the current limiter** when **S-2** is built, which acts faster than any
  human-read register.

**But three open questions need a steady-state anchor, not a trace**, and an anchor is exactly
what a human-read meter is good for. The rest of this section is how to use it without giving
up the automation.

### What it unlocks

| Question | Was | With the meter |
| --- | --- | --- |
| **T1-5 / S-3** absolute current | cross-check only; the true scale factor had no anchor | **fully anchored** — read amps at 3–4 steady rungs against logged `sense_i_mV` |
| **T1-6 / C-6** Vbus inference | blocked — no true Vbus reference | **runnable** — read volts at each rung |
| **T1-1** regen during braking | invisible | **detectable** — see below |
| **AK / C-6c** declared vs. actual volts | unmeasurable | **quantified** — sag under load, per rung |

### The sag trick — the ladder is already a voltage sweep

The original plan wanted discrete battery states, or a ladder repeated as the pack drained,
to get a range of Vbus for **C-6**. Neither is needed: **the pack sags under load**, so
reading volts at each rung of the T1-3 ladder gives a spread of bus voltages *within a single
pass*. Higher rungs pull harder and sag further. That is the range C-6's ratio test needs, and
it arrives free.

### Regen is visible as a voltage *rise*, not a current

Most inline watt meters are unidirectional and will read ~0 A into a braking regen. **Pack
voltage is the better tell**: during a hard brake from speed, regenerated energy pushes the
pack voltage *up*, and unlike a current spike that excursion lasts long enough for a human to
see it.

> **T1-1, brake mode: watch the volts, not the amps.** A visible upward blip on braking =
> regen is real and reaching the pack. No blip = either no regen path or it is being
> dissipated in the bridge. Either answer is worth having, and neither is available any other
> way today (§2.8 of `BOARD-REVISION-FACTS.md` — the board's own low-side shunt may not see
> reverse current at all).

### Protocol — how a human anchor joins the machine log

The analyser already expects `manual.csv` alongside the captured stream. Make the harness
cooperate:

1. **Add a hold-and-announce mode.** At each ladder rung the harness drives the rung, waits
   for the reading to settle, then prints `#HOLD,<test>,<rung>,<incr>` and **holds until Enter**.
   **Minimum dwell 20-25 s**, because the meter's display rotates one reading every 2 s and a
   full rotation is ~16 s — a 10 s window silently costs a reading. The dwell is a floor; the
   keypress is what advances.
2. **Read and write down** volts / amps / watts against the rung number. Paper is fine.
3. **Type it into `manual.csv`** after the session, keyed by `<test>,<rung>`, and let
   `bench-verdict.py` join it to the logged `sense_*_mV`.

**Take a zero first.** System powered, motors stopped: whatever the meter reads is the
quiescent draw (logic, P2, both boards). Subtract it. Same self-zero discipline the §2A front
end would have automated.

### Placement — CONFIRMED 2026-09-10: between the pack and the whole system

So every reading is **pack-side and system-total**: both boards' bridges, the P2, and all
logic. Two consequences shape the protocol.

**1. Float the idle wheel, or the comparison is polluted.** Each board has its own shunt, so
the driver's `sense_i_mV` is *per board* while the meter is *system total*. Comparing them
(T1-5) requires the other wheel to draw ~nothing — which means **float, not brake**. A wheel
held at stop with `holdAtStop(true)` draws real holding current and lands squarely in the
meter reading. Verify the idle wheel's stop mode before every anchored rung. (T1-1
characterises those modes, so run it first — which the ordering already requires.)

**2. The wiring drop is a trap that can produce a FALSE REJECTION of C-6.**

The meter reads **pack-side** voltage. The board sees pack-side **minus** the drop across the
leads, connectors and the meter's own shunt. That drop is `I × R_wiring` — so it **grows along
the ladder**, because higher rungs draw more current.

C-6's rejection criterion is *"ratio varying with commanded duty → the centring assumption is
wrong; C-6 withdrawn."* A current-dependent error in the Vbus reference produces **exactly
that signature**. At 25 A through a plausible 20 mΩ of leads, connectors and meter shunt,
the drop is 0.5 V — **2.7 % at 18.5 V**, comparable to the drift C-6 is looking for.

> **Do not withdraw C-6 on a ratio drift smaller than the computable wiring-drop bound.**
>
> Bound it rather than guess: at one high rung, put a DMM directly across the board's own
> supply terminals while the meter reads pack-side. The difference *is* `I × R_wiring` at that
> current; divide by the meter's amps to get `R_wiring`, then correct every rung. One extra
> reading, and it converts a systematic error into a known constant.
>
> If that reading is not taken, treat C-6 as **inconclusive** on a small drift — never as
> withdrawn.

**3. The Ah / Wh accumulator reads transients that the instantaneous display cannot.**

If the meter totalises amp-hours or watt-hours, that changes what a human can measure.
Instantaneous readings average away a transient; **an accumulator integrates it.** Read the
total before a manoeuvre, run it, read after — the difference is the energy through the pack
for that manoeuvre, transient included.

Useful for — **all of these requiring the N-repetition method above, not single events**:

- **T1-1** — energy per stop mode, A/B'd across the four modes at N ≈ 50 cycles with an
  identical acceleration profile, adding an energy column to the **C-4** decel table.
- **T1-7** — energy delivered into a fault event, per ramp aggressiveness. **`Ap` is the
  better instrument here** — it latches the peak directly and needs no repetition.
- **T1-3** — cumulative energy per ladder pass, as an efficiency cross-check. This one *is*
  a sustained run, so it clears the resolution floor without repetition.

**Caveat on regen:** a unidirectional meter will not *decrement* on regenerated current — it
will simply stop counting. That is still informative. If the accumulator does not advance
during a hard brake, no forward current is flowing, which is consistent with regen (or with a
float). Combine it with the **voltage-rise** observation above: accumulator flat **and** volts
rising is a much stronger regen signature than either alone.

### Limits — state them so the numbers are not over-trusted

- **Averaging.** Inline meters average over ~100 ms or more, so the instantaneous display
  **under-reads peaks**. A steady rung is valid; anything approaching a fault boundary is not.
  The accumulator does not share this limitation.
- **It cannot certify a protection threshold.** It anchors a *calibration* (**S-3**); it
  cannot validate a current *limiter* (**S-2**), which acts on fast excursions the display
  averages away. That remains the §2A front end's job.

### What this does to the front end

The front end is no longer on the critical path for **S-3** or **C-6**. Its remaining
irreplaceable jobs are the transient ones: the current trace through a fault (**T1-7**),
regen *magnitude* during braking (**T1-1**), thermal (**S-1**), and validating the current
limiter when **S-2** is built. Build it before the limiter, not before this bench run.

## 3. TIER 0 — no motor, no motion, no risk

**Rig:** P2 + Rev B board on the bench. Motor rail off. Motor may be unplugged.
**Harness:** `src/test_bench_t0.spin2`, built against the **single-motor 6.5″**
config block.
**Why this works:** `testSetup()` (`isp_bldc_motor.spin2:125`) runs the whole of
`init()` — board detection, constant derivation, power tables, unit conversion —
**without starting the driver cog.** Every derived value can be read back and
printed. Nothing can move.

**Fully automated. Zero instruments. ~30 minutes including builds.**

| ID | Finding | What we're looking for | Method | Pass / fail criterion |
| --- | --- | --- | --- | --- |
| **T0-1** | **A1**, **A3** | Which dead gap does a Rev B board actually get? **(criterion INVERTED 2026-09-10 — read A1's revision first)** | `testSetup(…, BRD_AUTO_DET)`; print `eDetectedBoard`, `dead_gap`, `rSenseForBoard`, `frame_cnt`, `pwm_limit`, `duty_min`, `duty_max`, `adc_fram`, `CLKFREQ` | At 270 MHz: **`dead_gap == 70` → A1's enum defect CONFIRMED, and the board is running 260 ns — which is COMPLIANT** with the 250 ns minimum that *both* manuals specify. **`dead_gap == 14` would mean the comparison matched and the board is running ~52 ns, ~5× BELOW the vendor minimum — stop and do not run Tier 1 until it is corrected.** The defect and the safe value coincide here; see A1 |
| **T0-2** | **A2**, **A3** | User's board override silently ignored | `testSetup(…, BRD_REV_A)` on the Rev B board; print `eDetectedBoard`, `bUserForced`, `boardIdString()` | Override honoured → `eDetectedBoard == REV_A`. **Detected value unchanged → A2 CONFIRMED.** String claiming "USER FORCED" while the value was ignored → **A3 CONFIRMED** |
| **T0-3** | **F** | `stopAfterDistance(_, DDU_M)` is 10× short | Call `stopAfterDistance()` with 1 DDU_M, 100 DDU_CM, 1000 DDU_MM; print `motorStopHallTicks` after each | All three equal → correct. **DDU_M one tenth of the other two → F CONFIRMED** |
| **T0-4** | **O** | `PWR_25p9V` validates then aborts | For each `PWR_*`: print `validVoltageForChoice()`, then `\testSetup()` inside an abort trap; print which unwound | A voltage that passes validation must not abort. **`PWR_25p9V` passes then aborts → O CONFIRMED** |
| **T0-5** | **G** | `setAcceleration()` accepts corrupting values | Call `setAcceleration()` with 0, −1, 1, 10_000_000; print `getRampingValues()` after each | Any value written through unvalidated → **G CONFIRMED**. Also records the accepted range for the units work in **C-2c** |
| **T0-6** | **I/T**, **K** | Getters that unwind their caller | `\getDistance(DDU_KM)`, `\getDistance(DDU_MI)`, `\getRotationCount(99)`, `\stopAfterDistance(0, DDU_IN)`; record which abort | Any *getter* that aborts → **I/T CONFIRMED**. A unit readable but not commandable → **K CONFIRMED** |
| **T0-7** | **AE** | No check that two pin groups overlap | Two motor instances, `testSetup()` both on deliberately overlapping groups | No complaint → **AE CONFIRMED** |
| **T0-8** | **C**, **AD** | `start()`'s return contract | Occupy all free cogs, then `start()`; print the return value | Return must be distinguishable from success. **Returns 0/garbage with no error path → AD CONFIRMED**, and the documented contract checked against **C** |
| **T0-9** | **N** | DocoEng low-power floor from an unassigned sentinel | *Skipped this round* — needs the DocoEng config, and we have no DocoEng motor. Pure arithmetic; provable by inspection | — |
| **T0-10** | **C-6b** | What does the X node read with both its FETs off? | With the motor rail **on** but motors stopped, `RQPIN` `base+3` (`pin_adc_x_i`). **No configuration needed** — the driver already has it running as an ADC inside `adc_pins`; it simply never reads it. **`RQPIN`, not `RDPIN`** (§6 hazard 3) | *Populated confirmed 2026-09-10, so this is now characterisation, not existence.* Expect near-zero if the board's divider pulls the floating node to ground. Establishes the baseline that **T1-13**'s switched reading is measured against |

**Output:** one CSV per test tagged `#T0-n,…` on the debug stream.

---

## 4. TIER 1 — wheels up

**Rig A.** Rev B, 6.5″ motor, single-motor config, `DRIVE_VOLTAGE = PWR_18p5V`
so the numbers line up with the shipped dual-motor demo.
**Harness:** `src/test_bench_t1.spin2`.
**~2 hours**, including the three clock builds for **T1-4** and enough ladder
repeats for the pack to drain across a useful voltage range (**T1-6**).

### Ordering is not negotiable

**T1-1 runs first.** It tells us what the hardware actually does every time the
driver stops — and the rest of the suite stops the motor several hundred times.

---

### T1-1 — Characterise the four ways this driver stops *(**S-9a**, feeds **C-4**)*

**S-9 is withdrawn.** Prior bench testing confirms freewheel/float works and full
braking works. This test is no longer a pass/fail on that question — it is a
**measurement of all four stop behaviours**, producing numbers the documentation
does not currently contain.

> **CAVEAT ADDED 2026-09-10 — the board may not be able to see regeneration at all.**
> Both revisions sense **low-side**, so during regenerative braking the reversed current
> drives the sense node *below system ground*. Rev A exposes the bare shunt node, where a
> P2 pin cannot read below GND — regen is very likely invisible there. Rev B interposes the
> **INA180B2**, and whether *that* can see reverse current depends on the variant's
> directionality and how its reference is tied — **not yet determined**
> ([`BOARD-REVISION-FACTS.md`](BOARD-REVISION-FACTS.md) §2.8).
>
> **Consequence for this test:** the §2A front end's **bidirectional** ACS758 may be the
> *only* instrument that can measure braking regen, which is exactly why bidirectionality was
> specified. Either read the TI INAx180 datasheet before this run, or treat the front end as
> the sole regen instrument and do not expect `sense_i_mV` to show it.

**Looking for**, in order of value:

1. **Does a fault silently downgrade brake to coast?** The fault path calls
   `.driveoff` unconditionally, without consulting `stop_mode_`
   (`isp_bldc_motor.spin2:2103-2108`), and `.checkstop` does not run again until
   a new drive command arrives. So a user who asked for `holdAtStop(true)` should
   get a freewheel from the moment of the fault. **A robot that faults on a slope
   would coast away in the configuration chosen to prevent exactly that.**
2. **The actual deceleration of each mode**, in ticks/s² and in
   revolutions-to-rest from a known speed — what `DRIVE-OBJECTS.md` should say
   and doesn't (**C-4**).
3. `emergencyCutoff()` routes through `.driveoff` too, so it should behave as
   coast regardless of stop mode. Same test, one more condition.

**Four conditions, `holdAtStop(true)` set throughout** so that any coast is a
downgrade rather than a request:

| | Condition | Expectation if S-9a holds |
| --- | --- | --- |
| a | `stopMotor()` with `holdAtStop(false)` | coast — the float baseline |
| b | `stopMotor()` with `holdAtStop(true)` | brake — fast decel |
| c | `stop()` (cogstop + `pinclear`) | coast — absolute reference, pins released |
| d | **after a provoked fault, `holdAtStop(true)`** | **coasts like (a)/(c), not like (b)** |
| e | `emergencyCutoff()`, `holdAtStop(true)` | coasts like (d) |

**How to measure it — fully automated, no instrument, no hand-spin:**

- spin up with `testDriveAtMotorIncrement()` to a repeatable set point; wait for
  `getDriverState() == DCS_AT_SPEED`; settle 500 ms
- command the stop condition
- **poll `getRawHallTicks()` directly from the harness cog** — not through the
  8 Hz sense task, which is far too slow — logging `(getct(), pos)` pairs into a
  hub buffer every 2 ms until `pos` stops changing or 4 s elapses
- 2000 samples × 2 longs = 16 KB of hub. Dump the buffer as CSV afterwards

**Resolution:** at the top of the coast-down, ~411 ticks/s means ~0.8 ticks per
2 ms sample, so differentiate over a sliding window rather than sample-to-sample.
Resolution improves as the wheel slows, which is where the modes separate anyway.
If finer resolution is wanted at speed, log `getct()` on each *change* of `pos`
instead of on a fixed interval — that timestamps individual hall ticks.

**Criteria:**

- **(d) tracking (a)/(c) rather than (b) → S-9a CONFIRMED**: the fault path
  ignores `stop_mode`, and a faulted robot freewheels even when configured to
  brake. Same for (e).
- (b) decelerating markedly faster than (a) → brake and float are distinct, as
  Stephen's earlier testing already indicates; this run just puts numbers on it.
- (a) vs (c): if float and pins-cleared coast identically, then `SM_FLOAT` truly
  releases the windings. Any difference between them is residual drive-side drag
  worth knowing about.

**Deliverable:** a small table — mode, deceleration, time-to-rest, revolutions-to-
rest, from a stated starting speed — that should end up in `DRIVE-OBJECTS.md`.

**Ordering note:** condition (d) needs a provoked fault, so run (a)/(b)/(c)/(e)
early and come back for (d) after **T1-7**.

### T1-2 — Is any speed telemetry alive? *(finding **W**)*

**Looking for:** `hallWindowSum += hallCntsIn8thSec` at
`isp_bldc_motor.spin2:1303` adds a variable that is only ever zeroed, so every
RPM and speed reading the library produces should be identically zero.

**Method:** drive at 25 / 50 / 75 %; at each, print `getRawHallTicks()` delta
over 1 s alongside `rpm`, `cntsInSec`, `hallWindowSum`.

**Criterion:** raw ticks advance while `rpm == 0` and `hallWindowSum == 0` →
**W CONFIRMED.** *Automated, no instrument.*

---

### T1-3 — The speed law and the real ceiling *(**C-1**, feeds **C-5**, **S-3**, **C-6**)*

**The highest-value single run in the suite.** One ladder produces the data for
four findings.

**Looking for:** confirmation that
`RPM = incr × 2000 × 60 / (2³² × 15)` for the 6.5″ motor, and the increment at
which the motor stops following — the real back-EMF ceiling, as against the
hand-measured `147_000_000` in the table at `isp_bldc_motor.spin2:973`.

**Method:** `testDriveAtMotorIncrement()` over a ladder — 5, 10, 20, 40, 60, 80,
100, 120, 140, 147, 155, 165 (×10⁶). At each rung: wait for
`getDriverState() == DCS_AT_SPEED`, settle 500 ms, then sample for 1 s.

**Measure, per rung:** predicted RPM, measured RPM (from `pos` delta ÷ elapsed
`getct()`), `duty`, `err`, `sense_i_mV`, `sense_u/v/w_mV`, `getCurrent()`,
`drv_state`, faulted y/n.

**Resolution check:** 411 ticks/s at top speed over a 1 s window is ±0.25 %.
Ample.

**Criteria:**
- measured RPM within 2 % of predicted across the linear region → **C-1
  CONFIRMED**, and the per-voltage tables are re-characterised as back-EMF
  ceilings rather than calibration.
- the rung at which measured RPM departs from predicted, or `drv_state` goes
  `DCS_FAULTED`, **is** the real ceiling at today's battery voltage. Compare to
  147 × 10⁶.
- `duty` at the departure rung answers the question **C-5** depends on: *is
  `duty_` saturated at `duty_max_` before the lag runs away?* If yes, C-5's
  gating condition is sound as proposed. If the fault arrives with `duty_` still
  in range, C-5 needs a different gate and the design changes.

*Fully automated. No instrument.* If the 360 P/R encoder is mounted, its reading
is logged alongside as a free independent cross-check.

---

### T1-4 — Is the current reading clock-dependent? *(finding **S-3**, no instrument)*

**This proves the defect without measuring anything external**, which is why it
is separated from the absolute calibration in T1-5.

**Looking for:** the study's claim that the four missing `sar` instructions
leave every `sense_*_mV` scaled by `adc_fram`, which varies with `_clkfreq`.

**Why it is a clean experiment:** the drive loop is 500 µs and the PWM is 44 kHz
at *any* system clock, because both are derived from `CLKFREQ` in `init()`. So
the same commanded increment produces the **same physical speed and the same
physical current** at every clock. Only `adc_fram` changes.

**Method:** three builds — `CLK_FREQ` = 200, 270, 300 MHz — each running one
mid-ladder rung from T1-3 (75 × 10⁶). Print `adc_fram`, `sense_i_mV`,
`sense_u/v/w_mV`, `getCurrent()`, and measured RPM (to prove the speed really
was identical).

**Criterion:** with RPM equal across the three builds, the expected `adc_fram`
values are 4545 / 6136 / 6818.

| Comparison | Expected ratio if S-3 holds |
| --- | --- |
| 270 MHz ÷ 200 MHz | **1.350** |
| 300 MHz ÷ 270 MHz | **1.111** |

`sense_i_mV` tracking those ratios → **S-3 CONFIRMED**, and the scale factor is
`adc_fram`, exactly as the missing `sar` predicts. `sense_i_mV` unchanged across
clocks → the study is wrong and S-3 is withdrawn.

*Automated via a shell loop that patches `CLK_FREQ`, builds, loads and captures —
the config-block rewriting machinery in `tools/build-check.sh` already does this
kind of edit-build-restore cycle and should be reused.*

---

### T1-5 — Absolute current calibration *(finding **S-3**, uses the §2A front end)*

**Looking for:** what `getCurrent()` should have returned.

> **UPDATED 2026-09-10 — the topology question is settled on paper.** Parallax documents both
> revisions as *"Total MOSFET load current"* sensed *"between common MOSFET GND and common
> system GND"* — a **DC-link shunt**, on both boards
> ([`BOARD-REVISION-FACTS.md`](BOARD-REVISION-FACTS.md) §2.3). So the proportionality check
> below is now a **sanity check, not a determination**, and **S-2 is unblocked**: a current
> limit *can* be built on this channel.
>
> The vendor also supplies the exact scale, which sharpens the test considerably. On Rev B:
> **`sense_i_mV(true) = 150 × amps`** (3 mΩ × 50 V/V, INA180B2). So the S-3 error factor is
> `sense_i_mV(observed) / (150 × amps)` and should land on `adc_fram` — **6136 at 270 MHz** —
> the same constant **T1-4** derives independently from the clock sweep. Our
> `F_REV_A_RSENSE = 5` / `F_REV_B_RSENSE = 3*50` constants are **confirmed correct** (§2.2).

**Method:** no separate run needed — the §2A front end logs bus current at every
rung of the T1-3 ladder automatically.

**Measure:** front-end amps vs. `sense_i_mV` vs. `getCurrent()`, at every rung
rather than at three hand-picked points.

**Criteria:**
- front-end amps proportional to `sense_i_mV` across the whole ladder → the channel is
  **DC-link current** and the calibration is valid. Not proportional → the
  channel measures something else; record and defer.
- true scale = `sense_i_mV / (front-end A × rSenseForBoard)`. **If S-3 is right this
  comes out at ≈ `adc_fram`** — 6136 at 270 MHz — which is the same number T1-4
  derives independently. **Two independent routes to the same constant is the
  strongest evidence this suite can produce.**
- `getCurrent()` vs. front-end amps gives the error factor the README's *"fixed in
  v5.0.0"* claim has to answer for.

*Fully automated. No manual readings.*

---

### T1-6 — Can we sense bus voltage? *(finding **C-6**)*

**Looking for:** whether `(sense_u + sense_v + sense_w) / 3` is a fixed fraction
of the battery voltage — which would mean bus-voltage sensing already exists in
hardware and needs only a constant.

**Rationale:** the three phase drives are centred on `bias = frame_cnt/4` within
a `frame_cnt/2` PWM window, so the average of the three duties is 50 % by
construction, independent of angle and of commanded duty.

**Method (revised 2026-09-10 — runnable with the meter already on the system):**
no front end and no discrete battery states are needed. Run the T1-3 ladder once
in hold-and-announce mode (**§2B**) and read pack volts at each rung. **Load sag
supplies the voltage range for free** — higher rungs pull harder and sag further —
so a single ladder pass yields the spread the ratio test needs, logged against the
three phase readings at every rung.

**Measure:** `ratio = mean(sense_u, sense_v, sense_w) / Vbus`, at every rung, at
both voltages.

**Criteria:**
- ratio constant to within a few percent across the whole ladder **and** across
  both voltages → **C-6 CONFIRMED**; the divider constant is the ratio, and
  bus-voltage sensing becomes available for the price of an add and a shift.
- ratio varying with commanded duty → the centring assumption is wrong; C-6 is
  withdrawn and the docs should say plainly that voltage cannot be sensed.

**Note:** this measurement is unaffected by **S-3** — the `adc_fram` scale error
is common to all four channels and cancels in the ratio. Only the final absolute
constant needs S-3 settled first. *So T1-6 is valid data even if T1-5 goes badly.*

---

### T1-7 — Where is the fault boundary, and is C-5 buildable? *(**C-5**, **Z**, **S-1**)*

**The test the highest-value recommendation depends on.**

**Looking for:** whether an over-aggressive ramp can drive the motor into a
fault **on wheel inertia alone** — no load fixture, no gravel, no robot — and
whether `duty_` saturates before the lag runs away.

> **UPDATED 2026-09-10 — the current at fault is readable without the front end.** The
> system meter latches **Peak Amps (`Ap`)**, **Peak Watts (`Wp`)** and **Minimum Volts
> (`Vm`)**.
>
> **Procedure per trial, given the peaks reset only on a power cycle (confirmed 2026-09-10):**
>
> 1. **Power-cycle the pack** — this is the only way to clear `Ap`/`Vm`/`Wp`.
> 2. **Re-read the quiescent zero** (motors stopped, rail on) — `Ah`/`Wh` reset too.
> 3. Select the `ramp_inc` trial index at the harness prompt.
> 4. Run it; let it fault.
> 5. Read `Ap`, `Vm`, `Wp` and write them on the sheet against this trial index.
>
> Then read all three: `Ap` is
> the fault current, `Vm` the sag floor at fault (feeding **C-6c**), `Wp` the severity. Repeat
> per `ramp_inc` value to map the fault boundary **in amps** — the number **S-2**'s limiter
> will be designed against. See **§2B**, including the two things to verify about the meter's
> reset behaviour and peak-detector bandwidth before trusting `Ap` as more than a lower bound.
>
> What still needs the harness: the *shape* — whether `duty_` saturates before the lag runs
> away — which is C-5's actual gate and is a trajectory, not an extremum.

**Why no load rig is needed:** a 6.5″ hub motor is heavy. Commanding a
sufficiently steep ramp makes the rotor fall behind on its own inertia, which is
the same failure mode as a loaded start, reached with software alone. This is
what removes the load-fixture from the plan.

**Method:** sweep `setRampingValues(ramp_min, ramp_max, ramp_inc, ramp_down)`
with `ramp_inc` ∈ {22 (shipped), 100, 500, 2_000, 10_000}. For each: from a
standstill, command 0 → 75 %, and log at 500 µs granularity until the motor
either reaches `DCS_AT_SPEED` or faults.

**Measure, per trial:** faulted y/n; `drv_incr` at the moment of fault; peak
`err`; peak `duty` and whether it reached `duty_max_`; peak `sense_i_mV`;
time-to-speed when it succeeded.

**Criteria:**
- **The C-5 gate test.** At the fault, `duty ≥ duty_max_` **and** `|err|` still
  growing → the proposed gate (*"stop advancing `drv_incr` while lag is large and
  duty is saturated"*) sees the condition in time and is buildable as specified.
  Fault with `duty` **not** saturated → the board intervened (see §1) or the
  model is incomplete; either way C-5's design changes and we want to know now,
  before writing PASM.
- `ramp_inc = 22` should **not** fault unloaded. If it does, the shipped default
  has no margin at all even with no load — a much more urgent finding than
  anything in either study.
- the `ramp_inc` at which faulting begins gives the real margin the shipped
  default is carrying.

**Session discipline:** this test deliberately faults the motor repeatedly. Cap
it at the five trials listed, and **put a hand on the board's FETs between
trials** — there is no thermal sensing anywhere in this system (**S-1**), so the
back of your hand is the only over-temperature protection in the building.
*Automated between trials via `testResetFault()`.*

---

### T1-8 — Distance overshoot *(finding **C-3**)*

**Looking for:** the study's ~1.2 m overshoot model — 8 Hz check granularity
plus no braking-distance lookahead.

**This runs wheels-up, not on the floor.** The overshoot is dominated by an
*active* ramp-down rather than a coast, so the wheels-up figure should be close
to the floor figure, and it is measurable in hall ticks by the P2 itself.

**Method:** `driveForDistance(2, DDU_FT)` and `(10, DDU_FT)` at default
`maxSpeed4dist`. Log `posTrkHallTicks` at three moments — the target,
the pass where the stop is commanded, and final rest.

**Measure:** ticks between the commanded target and final rest, converted to mm
with the object's own `tickInMM_x10`.

**Criteria:** predicted ≈ 1.2 m total (≈ 221 mm of 8 Hz latency + ≈ 974 mm of
ramp-down) at 18.5 V, `maxSpeed4dist = 75`. Within ~20 % → **C-3 CONFIRMED and
quantified.** *Optional:* one tape-measured run on the floor as a cross-check of
the tick→mm conversion.

*Automated, no instrument.*

---

### T1-9 — What a fault looks like from the outside *(**M**, **AF**, **Z**, **S-5**, **S-6**)*

**Looking for:** the end-to-end propagation failure the user's field report
describes.

**Method:** while driving at 50 %, provoke a fault (hand-brake the wheel, or use
the T1-7 ramp). Then, once per 100 ms for 5 s, log `getStatus()`, `isFaulted()`,
`isFaultSignal()`, `isTurning()`, `getDriverState()`. Then command a fresh drive
and log recovery.

**Criteria:**
- `getStatus()` returning `DS_MOVING` while `getDriverState() == DCS_FAULTED` →
  **M CONFIRMED**, and by extension the serial `getstatus` defect **S-6**.
- `isFaultSignal()` going false on its own → the auto-clear. On the *single-motor*
  object nothing should clear it; **the 3 s auto-clear lives in the steering
  object** (`isp_steering_2wheel.spin2:418-447`), so if the two-wheel build is
  available, repeat this test there and watch the latch vanish at 3 s → **S-5
  CONFIRMED.**
- recovery behaviour after re-command → **Z**, plus whether `duty_` restarts from
  `duty_min_` or from wherever the fault left it.

*Automated except for the hand-brake.*

---

### T1-10 — Reverse commutation offset *(finding **AI**)*

**Looking for:** the true reverse offset for the 6.5″ motor. Today it is simply
`360 − fwd` (`isp_bldc_motor.spin2:offsetsForMotor`), derived rather than
measured — and the user's field fault is on one wheel in one direction, which is
exactly what a wrong reverse offset would look like.

**Method: reuse what exists.** `src/util_char_motor.spin2` already sweeps
`testSetFwdRevOffsets()` and records current draw and fault behaviour per offset,
forward and reverse; `src/test_motor_char_ofsts.spin2` is the narrower variant.
Run the existing harness — do not write a new one.

**Measure:** current at a fixed commanded speed, per offset, both directions.
**Criterion:** the reverse minimum-current offset. If it is not `360 − 43` the
derived value is wrong and **AI** is confirmed with a replacement number.

**Caveat:** the current readings this harness produces are subject to **S-3**.
That does not matter here — we are looking for the *minimum*, and a constant
scale error does not move the location of a minimum. **T1-10 is valid before
S-3 is fixed.**

---

### T1-11 — Are the two wheels running equivalent commutation? *(**AI**, **AJ**, and the field report)*

**This test exists because the rig is a dual platform with independently
runnable motors.** It was not possible to plan before that was known.

**The mechanism.** `isp_steering_2wheel.spin2:112` calls `rtWheel.forwardIsReverse()`,
because the two motors face opposite directions on the chassis. That flips the
sign of the commanded power, hence the sign of the commanded increment
(`driveAtPowerEx`), and the increment's sign selects which commutation offset the
driver applies (`isp_bldc_motor.spin2:offsetsForMotor` supplies both;
`initAngleFmHall` and the main loop select between them on the sign bit).

For the 6.5″ motor those two offsets are `43°` and `360 − 43 = 317°` — and in
32-bit `frac 360` arithmetic they are **exact negatives of each other**, because
one was derived from the other rather than measured. The source says as much:
*"from characterization at 18v5: fwdDegrees := ofsDegr := 43"*, with the reverse
value assigned as `360 - fwdDegrees`. That is finding **AI**.

**Therefore: when the robot drives straight forward, its two wheels are running
on two different commutation offsets — one characterised on the bench, one
derived and never measured.** The two wheels are not electrically equivalent.
*Which* wheel gets which is exactly what this test resolves; the fwd/rev labels
in the source contradict each other across `offsetsForMotor()` and
`initAngleFmHall()`, so it should be measured rather than reasoned about.

**And that asymmetry is the precise shape of a one-wheel-only fault** — which is
what the 2026-09-09 user report describes
([`user-report-2026-09-09-ANALYSIS.md`](user-report-2026-09-09-ANALYSIS.md)).

**Method:** run the **identical T1-3 increment ladder** on the left motor alone,
then on the right motor alone, on the assembled rig, at the same battery state.
Then repeat both with `forwardIsReverse()` deliberately **not** applied, so each
motor is measured on both offsets.

**Measure, per motor per offset:** the rung at which it departs from the
predicted speed law or faults; `sense_i_mV` at each matched rung; peak `duty`.

**Criteria:**
- both motors, on the *same* offset, behaving alike → the motors and wiring are
  equivalent, and any left/right difference in service is attributable to the
  offset, not the hardware
- one offset consistently drawing more current or faulting at a lower rung than
  the other, **on both motors** → **AI CONFIRMED with a magnitude**, and the
  derived reverse offset is the field fault's mechanism
- the offset that performs worse is the one **T1-10** should sweep first

*Fully automated — the §2A front end logs per-wheel current throughout.*

---

### T1-13 — Direct bus-voltage read from the unused 4th channel *(**C-6b**)*

**Looking for:** a *direct* Vbus measurement, as against **C-6**'s inference from
the average of the three phase senses.

**Why it may be better:** it does not rest on the drive being centred at 50 %,
and **it works with the motor stopped** — which is when you actually need to know
the voltage, because that is when the speed ceiling gets chosen.

> **UPDATED 2026-09-10 — Stephen confirms all four channels are populated (U, V,
> W, X).** The prerequisite below is satisfied; this test is live. Two source
> claims in the original wording were wrong, and one new hazard appears precisely
> *because* the FETs are real.

**The read side is free — X is already a running ADC.** `pin_adc_x_i` (base+3)
falls *inside* `adc_pins` (`(4 << 6) + 0` = base+0 addpins 4 = five pins), so the
driver already has it in `P_ADC_1X | P_COUNT_HIGHS`, phase-locked to the PWM
frame, GIO/VIO mode-cycled with the rest. It is simply never read. A harness cog
needs **no configuration whatsoever** to sample it.

**But it must read with `RQPIN`, never `RDPIN`** — see the harness rule in §6.

**Calibration caveat:** the driver reads GIO/VIO levels for U, V, W and CUR only,
so there is no `scl_levels` entry for X. Absolute mV on X requires the harness to
run its own GIO/VIO pass. **C-6b's ratio does not need it**; the absolute divider
constant does.

**The write side is where the risk moved.** `pwm_x_l` / `pwm_x_h` are **not
declared in this driver at all** — the pin list ends at `pin_pwm_w_h` (base+13).
The board's fourth-channel gate pins are base+14/15 by position and are free
within the 16-pin group, but our source never names them.

> ### HAZARD — shoot-through. Read before driving base+14/15.
>
> Now that the FETs are known populated, **driving base+14 and base+15 both
> active simultaneously shorts the bus through the half-bridge** and destroys it,
> and possibly the board. The U/V/W channels are safe only because the driver's
> `pwmt`/`pwmn` pair plus its board-revision `dead_gap` guarantee they never
> overlap. A harness hand-rolling PWM on base+14/15 has **none of that
> machinery** and must supply it.
>
> **The bootstrap tension is real and has no free answer.** Holding only the high
> side on is shoot-through-proof but does not work: a bootstrap gate driver
> charges its cap only while the *low* side conducts, so a high-side-only drive
> either never turns on or droops within milliseconds. Getting a sustained
> high-side on therefore *requires* switching the low side too — which is exactly
> the case that needs correct dead time.
>
> **The number is not a guess — both vendor manuals state it.** Rev A and Rev B each say:
> *"the recommended minimum pause (deadtime) is **250 ns** after switching off one MOSFET
> and before switching on the other MOSFET in the same channel."* They say it despite
> shipping different drivers — Rev A a MIC4604 (39 ns propagation, ~20 ns rise/fall), Rev B
> a UCC27211D (~20 ns propagation, 7.2/5.5 ns) — because **the MOSFETs, not the drivers, are
> the limiting element.** Sizing deadtime from the driver numbers lands near 50 ns and is
> wrong. Whatever drives base+14/15 must honour **≥ 250 ns**; use **260 ns**, since the
> `(ticks1us * ns) / 1_000` form truncates and a literal 250 gives 248.1 ns at 270 MHz.
>
> **Two ways to do this safely; pick one before the bench session:**
>
> 1. **Borrow the driver's own dead-gap discipline** — replicate `pwmt`/`pwmn`
>    and the Rev-A/Rev-B `dead_gap` value on base+14/15 in the harness, verified
>    against a scope on the two gate pins *before* the rail is live.
> 2. **Do it in the driver instead** — extend the existing, proven PWM setup to
>    the fourth channel. Safer, because the dead-gap logic is already correct per
>    board revision, but it is a driver change and therefore a fix-sprint act,
>    not a bench act.
>
> **Do not improvise a third option at the bench with a live battery.**

**Method:** with the motor stopped and the rail live, PWM the fourth channel's
half-bridge at a known duty (say 25 %) using whichever safe route above was
chosen, and read `base+3` with `RQPIN`.

**Measure:** `reading / duty`, against the §2A front end's true bus voltage, at
three or four battery states as the pack drains.

**Criteria:**
- `reading / duty` proportional to true Vbus across the range → **C-6b
  CONFIRMED**, and the board divider constant falls out. This becomes the
  preferred voltage source over **C-6**.
- nothing sensible → **not** an unpopulated channel (that is settled — all four
  are populated), so suspect the switching: bootstrap not charging, dead-time
  wrong, or the X node's divider not wired to the sense pin the way U/V/W are.
  Check the two gate pins on a scope before changing anything else, and fall back
  to **C-6** for this round.

**Prerequisite: SATISFIED 2026-09-10.** Stephen confirms all four channels are
populated — U, V, W and X. **T0-10** is still worth running first, but now as a
characterisation of what the X node reads with both FETs off, not as a
does-it-exist check.

**Also worth logging while here (free):** `sense_u_mV / (drive_u_ / frame)` during
the T1-3 ladder — a third, independent Vbus estimate that makes no centring
assumption. Three routes to one number is a good position to be in.

---

### T1-12 — Channel-swap discriminator *(the user's open field question)*

**Carried over from 2026-09-09 as unresolved.** A five-minute test was
recommended to the user in the field and never run. The dual rig lets us run it
here, instrumented, instead of asking him to do it by eye.

**Method:** run the T1-3 ladder on both channels. Then **swap the two motor
cables at the board end** and re-run.

**Criteria:**
- the worse-performing behaviour **follows the cable** → the motor or its harness
  is the cause; no code fix will help him
- the worse behaviour **stays on the same board channel** → it is the board or the
  offset path, and **T1-11** says which

**Why it is worth the ten minutes:** it is the difference between writing him a
code fix and telling him to check his wiring, and we currently cannot tell him
which.

*Two runs of an existing automated ladder, plus one cable swap.*

---

## 5. TIER 2 — wheels down

**Rig B. One test. Two motors, two Rev B boards, dual-motor config.**

### T2-1 — Which way does it turn? *(finding **AC**)*

**Looking for:** `driveDirection()`'s sign convention. The code contradicts its
own comment, and `README.md` and `DRIVE-OBJECTS.md` contradict each other.

**Method:** on the floor, `driveDirection(50, +50)`. Watch.

**Criterion:** it turns left, or it turns right. Write down which. Then fix
whichever of the three sources is wrong.

**Automatable:** no, and it does not need to be. **Thirty seconds, and it settles
a documentation contradiction that has outlived several releases** — the highest
value-per-second in this entire plan.

*If the two-wheel platform is assembled anyway, also re-run **T1-9** on it to
catch the 3 s fault-latch erasure (**S-5**) and the steering-level e-stop
auto-cancel (**S-4**), both of which exist only at that layer.*

---

## 6. Automation and harness structure

**Architecture (Stephen, 2026-09-10): the test program stands in for the dual
drive demo — it runs the real system, through the real object stack, and its
`debug()` output is captured live by `pnut-term-ts`.**

This is better than a purpose-built single-motor harness, for three reasons:

1. **One config block, one rig, essentially one binary.** The dual-motor 6.5″
   config covers Tier 0, Tier 1 and Tier 2 without touching
   `isp_bldc_motor_userconfig.spin2` mid-session.
2. **It exercises the layer where the worst findings live.** **S-4** (steering
   e-stop auto-cancel), **S-5** (the 3-second fault-latch erasure), **M**/**AF**
   (fault invisibility) exist *only* in `isp_steering_2wheel.spin2`. A
   single-motor harness would have missed all four.
3. **It is the shipped configuration**, so every verdict is about what users
   actually run, and it reuses the demo's proven bring-up rather than new
   bench-only startup code.

### Files

```
src/test_bench_dual.spin2    ' the suite — shaped like demo_dual_motor.spin2,
                             '   drives the real isp_steering_2wheel stack
src/test_bench_t0.spin2      ' dry tier — one isp_bldc_motor, testSetup() only,
                             '   never starts a driver cog, motor rail off
```

**The flagship demos stay untouched.** `tools/build-check.sh` certifies both
`demo_single_motor` and `demo_dual_motor` before any release; the test programs
are *additional* top-levels. Note that the gate also requires every `src/*.spin2`
to compile under at least one config block, so both new files must build under
the dual-motor config or the gate will flag them.

### What the steering object has to expose

`isp_steering_2wheel.spin2` currently hides most of what the suite needs —
`getDriverState()` and `getFaultStatus()` are `PRI`, and there is no pass-through
for `testDriveAtMotorIncrement()`, `testSetFwdRevOffsets()`, `testGetResults()`,
`testResetFault()`, `getRawHallTicks()` or per-wheel `getCurrent()`. A top-level
cannot reach around it: declaring its own `isp_bldc_motor` would create a second
instance fighting the steering object's for the same pins.

**Recommendation: add a `CON ' --- TEST-USE ONLY Methods ---` section to
`isp_steering_2wheel.spin2`** with thin left/right pass-throughs, mirroring the
convention `isp_bldc_motor.spin2` already uses for `testSetLimit()`,
`testGetResults()` and friends. That keeps the study/fix boundary clean.

Worth noticing, though: three of the needed pass-throughs — `isFaulted()`, a
fault-flags query, and `clearFault()` — **are finding AF's fix**, which is #2 on
the study's priority list. The bench prep and the second-ranked repair are the
same work. Whether to add them as `test*` scaffolding now and design the real API
in the fix sprint, or pull the AF fix forward and have the harness exercise the
thing we intend to ship, is a call for next session.

### RESOLVED 2026-09-10 — Stephen chose the `test*` scaffolding route

**AF stays in the fix sprint**; the study/fix boundary is intact. The section was
built and the compile gate is green (39/39 tops, both release demos certified).

`isp_steering_2wheel.spin2` now carries `CON ' --- TEST-USE ONLY Methods ---`
with 19 pass-throughs: `testGetDriverState()`, `testGetFaultStatus()`,
`testGetRawHallTicks()`, and left/right pairs of `testGetTelemetry()`,
`testGetResults()`, `testDriveAtMotorIncrement()`, `testSetFwdRevOffsets()`,
`testSetLimit()`, `testSetMotorReversed()`, `testResetFault()` and
`testResetMaxValues()`. Two supporting methods were added to
`isp_bldc_motor.spin2`'s existing TEST-USE ONLY section:

- **`testGetTelemetry()`** — the record format below wants `duty`, `err`,
  `sense_u/v/w/i_mV` and `drv_state`, and no getter existed for any of them. One
  call snapshots the group, which is far tighter than N separate calls (though
  still not atomic against the driver's per-cycle block copy — a sample can
  straddle an update).
- **`testSetMotorReversed()`** — `forwardIsReverse()` is one-way by design, and
  **T1-11** requires measuring both wheels with the reversal *and* without it.

**Two design points the harness author must know:**

1. **`testGetFaultStatus()` deliberately does not call the steering object's
   `getFaultStatus()`.** That method is where **S-5** lives — it clears the fault
   latch 3 s after the fault appears. A test calling it would destroy the very
   thing the test is watching. The pass-through reads `isFaulted()` /
   `isFaultSignal()` off each wheel directly and has no side effects — which also
   means **T1-9 can watch S-5 erase the latch underneath it**, live.
2. **`testDriveAtMotorIncrement()` bypasses both `incrementForPower()` and the
   reversed-motor flag.** The sign passed in is the sign the driver sees, and the
   sign is what selects the commutation offset. That is what makes **T1-10** and
   **T1-11** able to put either wheel on either offset deliberately.

### Three hazards to design around

**1. `debug()` will corrupt timed measurements.** Debug output is a serial
stream; emitting a line per sample during **T1-1**'s 2 ms coast-down polling, or
**T1-7**'s 500 µs ramp capture, would dominate the very timing being measured.

> **Rule: inside any timed section, log `(getct(), value)` tuples into a hub
> buffer and emit nothing. Dump the buffer as CSV after the section ends.**

**2. The library talks over the test.** The motor object, the sense task and the
steering object all emit their own `debug()` lines — at 8 Hz × 2 wheels plus
driver chatter, the captured log interleaves. Mitigations: prefix every harness
record with a unique tag so the analyser can filter (`#T1-3,…`), and quiet the
library during timed sections.

> **Corrected 2026-09-10.** This section previously said to quiet the library via
> the `useDebug` / `showHDMIDebug` flags "the motor object already carries."
> **`useDebug` does not work** — it is declared in the VAR block and set `FALSE`
> in `testSetup()`, and **nothing ever reads it**; every `debug()` in the motor
> object is unconditional. `showHDMIDebug` is real, but it gates only the HDMI
> display list, not the serial `debug()` stream. So there is currently **no
> working way to silence library chatter**, which matters most for T1-1's 2 ms
> coast-down polling and T1-7's 500 µs ramp capture. Tracked as **PL-8**; the
> harness author must either wire `useDebug` up first or accept the interleave
> and rely on tag filtering. Buffer-then-dump (hazard 1) remains the primary
> defense either way.

**3. `RDPIN` on a driver-owned pin steals the driver's sample.** *(Added
2026-09-10, confirmed against p2kb-mcp.)*

The P2's smart pins are global — any cog can read any pin — but **`RDPIN`
acknowledges the smart pin and lowers its `IN` signal**, exactly as `WRPIN` /
`WXPIN` / `WYPIN` / `AKPIN` do. `RQPIN` ("read quiet") is the deliberate
exception: it does *not* acknowledge, which is why the silicon documentation
states it "can be used by any number of cogs, concurrently, to read a pin without
bus conflict."

> **Rule: the harness reads driver-owned pins with `RQPIN` only. Never `RDPIN`.**

This is not a style preference. The driver's control loop reads
`pin_adc_u/v/w_i` and `pin_adc_cur_i` every cycle with `rdpin`. A harness cog
issuing its own `rdpin` on any of those races the driver for the acknowledge and
**silently corrupts the drive loop under test** — the worst possible failure
mode, because the numbers still look plausible.

Applies to every phase/current sense read, and to `base+3` in **T1-13**. It does
*not* apply to the harness's own §2A pins (P50/P51/P52), which no other cog
touches — `RDPIN` is fine there.

### Record format

One tagged line per data point, so the analyser needs no parsing cleverness:

```
#T1-3,wheel,rung,incr,predRPM,measRPM,duty,err,sense_i,sense_u,sense_v,sense_w,state,faulted
```

### Runner and analyser

```
tools/bench-run.sh <tier> [clkfreq]     ' build, load, capture to a dated file
tools/bench-verdict.py                  ' captured CSV + manual.csv -> verdicts
```

`bench-run.sh` patches `CLK_FREQ` for **T1-4**'s three builds and captures the
`pnut-term-ts` stream to
`DOCs/analyses/bench/2026-09-10/<tier>-<clk>.log`. Reuse the config-block
activate/restore machinery already in `tools/build-check.sh`, including its
restore-on-interrupt handling.

`bench-verdict.py` prints one line per test:

```
T0-1   A1    dead_gap=70 expected=14                CONFIRMED
T1-1   S-9a  post-fault decel matches float, not brake   CONFIRMED
T1-4   S-3   ratio 270/200 = 1.349 (exp 1.350)      CONFIRMED
T1-7   C-5   fault @ duty=duty_max, err rising      GATE VALID
T1-11  AI    rev-offset rung 9 vs fwd rung 12       CONFIRMED
```

**The thresholds go into this script before the bench session, not after.** That
is the point of the whole structure: the session ends with a verdict list, and
the hardware goes back on the shelf the same night.

### Effort

`test_bench_t0.spin2` half a day — it is mostly print statements.
`test_bench_dual.spin2` a day or so; `demo_dual_motor.spin2` is the skeleton and
`util_char_motor.spin2` already solves the drive-measure-fault-reset loop that
**T1-3**, **T1-7**, **T1-10** and **T1-11** all need. Pass-throughs and tools, a
few hours.

## 7. Deliberately not tested this round

| Finding | Why deferred |
| --- | --- |
| **N** | Needs the DocoEng config and motor; pure arithmetic, provable by inspection |
| **AJ** | DocoEng offsets vs. voltage and board rev — no DocoEng motor |
| Rev A anything | Policy §1 — after the current limiter exists |
| **AB** (`driveForDistance()` cannot turn) | Software-only; provable by inspection, no bench value |
| **P**, **H**, **J**, **Q**, **Y**, **S** | Software-only; inspection or Tier 0 at most |
| Thermal behaviour | No temperature sensing exists anywhere. Hand on the FETs is the state of the art. This is itself a finding |

---

## 8. Run order, condensed

```
BUILD FIRST (off-bench, ~an evening of soldering)
  the §2A front end: V + I + T on P50/P51/P52, validated once against a watt meter

TIER 0  (30 min, no motor, no risk)
  T0-1 … T0-9          all automated, all dry
  T0-10  passive read of base+3   <-- is the 4th channel alive? gates T1-13

TIER 1  (~2 h, wheels up, Rev B, 18.5 V)
  T1-1   stop behaviour        <-- FIRST, gates everything after it
  T1-2   telemetry liveness
  T1-3   speed ladder          <-- feeds C-1, C-5, S-3, C-6
  T1-4   clock sweep           <-- 3 builds, no external reference needed
  T1-5   current calibration   <-- rides along with T1-3; front end supplies amps
  T1-6   bus-voltage sweep     <-- repeat the ladder as the pack drains
  T1-7   ramp aggression       <-- faults on purpose; watch board temp
  T1-8   distance overshoot
  T1-9   fault as seen from outside
  T1-10  reverse offset sweep  <-- existing util_char_motor.spin2
  T1-11  left vs right, both offsets  <-- dual rig only; feeds the field report
  T1-12  channel swap discriminator   <-- dual rig only; answers the user
  T1-13  4th-channel direct Vbus read <-- only if T0-10 says the channel is alive
  T1-1d  coast-down after a fault + after e-stop (needs T1-7 first)

TIER 2  (5 min, wheels down)
  T2-1   driveDirection(50, +50) — watch
  T1-9'  repeat on the two-wheel build if assembled
```

---

## 9. What this suite decides

By the end of one evening we should be able to state, with numbers:

- **S-9a** — whether a fault silently downgrades `holdAtStop(true)` to a
  freewheel, plus deceleration numbers for all four stop modes (**C-4**)
- whether the two wheels run equivalent commutation, and whether the derived
  reverse offset is the mechanism behind the user's one-wheel field fault
- whether **S-3** stands, by two independent routes — the clock sweep (**T1-4**,
  needing no external reference at all) and the front end (**T1-5**) — and what
  the true scale factor is
- whether bus voltage can be sensed with the hardware we have, by up to three
  routes: the direct 4th-channel read (**C-6b**, preferred, **T1-13**), the
  three-phase average (**C-6**, **T1-6**), and the duty-referenced per-phase
  estimate logged free during **T1-3**
- whether **C-5** is buildable as specified — does `duty_` saturate before the
  lag runs away
- the real speed ceiling and the real fault margin of the shipped ramp defaults
- **C-3**'s overshoot, quantified in hall ticks
- **AI**'s reverse offset, measured rather than derived — and whether it is the
  field fault's cause
- for the user: whether his fault follows the cable or the channel
- **A1**, **A2**, **A3**, **F**, **O**, **G**, **I/T**, **K**, **AE**, **AD**,
  **W**, **M** — all confirmed or withdrawn, most of them before the motor ever
  turns
- **AC** — which way it turns

- whether the board's current channel is a DC-link shunt (**T1-5**'s
  proportionality check) — which decides whether a current limit can be built on
  it at all

That is enough to plan the fix sprint with no remaining unknowns of consequence.

**The question that used to sit here is answered.** Whether the 64010's
fourth-channel FETs are populated was the one thing this suite could not settle.
**Stephen confirmed 2026-09-10: all four are populated — U, V, W and X.** So
**C-6b** is live, its read side costs nothing (X is already a running ADC), and
the remaining work is doing the *switching* safely — see the shoot-through hazard
in **T1-13**.

---

*Plan written 2026-09-10. No source modified. The harnesses described in §6 do
not exist yet.*
