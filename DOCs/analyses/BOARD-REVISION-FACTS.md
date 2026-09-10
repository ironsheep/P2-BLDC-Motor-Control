# 64010 Universal Motor Driver — vendor hardware facts, by revision

**Created:** 2026-09-10
**Source:** Parallax 64010 board documentation, Rev A and Rev B manuals, supplied by Stephen.
**Status:** reference. Part 1 is **verbatim vendor text**; Part 2 is analysis and is clearly
marked as such.

---

## Why this file exists

Three findings in the 2026-09-09 studies were wrong because a hardware fact was **inferred
from our own driver source** instead of read from vendor documentation:

| Finding | The inference | What the vendor documentation actually says |
| --- | --- | --- |
| **A1** | Rev B needs a shorter (52 ns) dead gap; the code failing to apply it is the defect | **Both** revisions specify a **250 ns minimum**. 52 ns is ~5× out of spec; the code's accidental 260 ns is correct. The *distinction itself* does not exist |
| **C-6b** | `pin_adc_x_i` is "never `wrpin`'d" | It is inside `adc_pins` and has been a live, calibrated, frame-locked ADC all along — merely never *read* |
| **C-6b** | `pwm_x_l`/`pwm_x_h` are "declared and never configured" | They are **not declared anywhere** in this driver |

**Rule going forward: a hardware claim cites this file or the vendor manual. It is never
derived from what the driver appears to assume.**

---

# Part 1 — Verbatim vendor text

Reproduced exactly. Emphasis and section numbers are the vendor's.

## 1.1 Hall Effect inputs

> **Both revisions carry this section word for word identically.** Reproduced once; the
> Rev A and Rev B manuals do not differ by a single character here.

### Rev A §7 and Rev B §7 — *Hall Effect or General Purpose Feedback Inputs*

> The HALL/INPUTS header is populated with a standard 5 way 0.1" male header, and is
> typically used to connect the Hall effect sensor cable of a 3-phase Hub (BDLC) type motor,
> such as our Hub Motor #27860.
>
> The 5V output is provided to power a low current hall sensor (or similar sensor up to
> 100 mA), and the three signal pins (U, V, W) are each pulled up to 3.3 V via a 3.9 kΩ
> resistor and are each connected to the P2 Accessory Header via a series 3.9 kΩ resistor to
> protect the microcontroller from 5 V signals.

## 1.2 Current sense — **this is where the revisions differ**

### Rev A §8 — *Current Sense Resistor*

> Total MOSFET load current can be measured with the current sense resistor, and the data is
> typically used to determine system load and provide overcurrent protection.
>
> This board uses a low-side sensing technique with a 5 mΩ current sense resistor connected
> between common MOSFET GND and common system GND. The voltage level can be measured across
> this sense resistor and converted to current with this formula:
>
> I = Vsense / Rsense (Rsense = 5 mΩ)
>
> Example: If the voltage measured at Sense Common (Vsense) = 30 mV then the MOSFET current
> would be 30 mV / 5 mΩ = 6 Amp.

### Rev B §8 — *Current Sense Resistor with Amplifier*

> Total MOSFET load current can be measured with the current sense resistor, and the data is
> typically used to determine system load and provide overcurrent protection.
>
> This board uses a low-side sensing technique with a 3 mΩ current sense resistor connected
> between common MOSFET GND and common system GND.
>
> A dedicated current sense amplifier beside the shunt resistor (INA180B2) boosts the signal
> with a gain of 50 V/V. Refer to the Texas Instruments INAx180 datasheet, and in particular
> the section "Precise Low-Side Current Sensing" to help with interpreting the current sense
> readings. In addition the same datasheet has an elaborated Typical Application for Low-Side
> Sensing in section 9.2.
>
> The voltage level can be measured across this sense resistor and converted to current with
> this formula:
>
> Vsense = 3mOhms \* 50V/V gain = 150mV per Amp (mV/A)
>
> This can be simplified as: Isense = Vsense / 150
>
> Example: If the voltage measured at Sense Common (Vsense) = 1500mV then the MOSFET current
> would be 1500mV / 150 (mV/A) = 10 Amp.

## 1.3 Deadtime — **same requirement, different drivers**

### Rev A — MOSFET driver **MIC4604**

> Even though the MOSFET Drivers feature a fast 39 ns propagation delay and typically 20 ns
> rise/fall time, the MOSFETs require some time to respond to the control signal from the
> MOSFET Drivers. This means it is possible, for fractions of a second during fast switching,
> that both high and low MOSFETs might be partially on and causing momentary overcurrent.
> Therefore, the recommended minimum pause (deadtime) is 250 ns after switching off one
> MOSFET and before switching on the other MOSFET in the same channel. Using a deadtime pause
> is standard practice for Half-Bridge motor controllers, and ensures the highest efficiency
> and lowest power losses, including lower current-surge requirements from the power source
> and overall cooler operation of the motor controller PCB.

### Rev B — MOSFET driver **UCC27211D**

> Even though the MOSFET Drivers feature a fast ~20ns propagation delay and typically 7.2ns
> rise, 5.5ns fall time, the MOSFETs also require some time to respond to the control signal
> from the MOSFET Drivers. This means it is possible, for fractions of a second during fast
> switching, that both high and low MOSFETs might be partially on and causing momentary
> overcurrent. Therefore, the recommended minimum pause (deadtime) is 250 ns after switching
> off one MOSFET and before switching on the other MOSFET in the same channel. Using a
> deadtime pause is standard practice for Half-Bridge motor controllers, and ensures the
> highest efficiency and lowest power losses, including lower current-surge requirements from
> the power source and overall cooler operation of the motor controller PCB.

---

# Part 2 — What this settles, and what it moves

**Everything below this line is analysis, not vendor text.**

## 2.1 Summary table

| Property | Rev A | Rev B | Differs? |
| --- | --- | --- | --- |
| Hall header | 5-way 0.1", 5 V @ ≤100 mA | identical | **no** |
| Hall U/V/W pull-up | 3.9 kΩ to 3.3 V | identical | **no** |
| Hall U/V/W series R | 3.9 kΩ | identical | **no** |
| Current sense topology | **low-side**, shunt in MOSFET-GND return | **low-side**, same position | **no** |
| Shunt value | 5 mΩ | 3 mΩ | yes |
| Amplifier | none (gain 1) | INA180B2, **50 V/V** | yes |
| **Scale at the pin** | **5 mV/A** | **150 mV/A** | **yes — 30×** |
| MOSFET driver | MIC4604 | UCC27211D | yes |
| Driver propagation | 39 ns | ~20 ns | yes |
| Driver rise / fall | ~20 ns / ~20 ns | 7.2 ns / 5.5 ns | yes |
| **Minimum deadtime** | **250 ns** | **250 ns** | **no** |

## 2.2 CONFIRMED — our `rSenseForBoard` constants are exactly right

`isp_bldc_motor.spin2:1183-1184`:

```spin2
F_REV_A_RSENSE = 5        ' .005 Ohms
F_REV_B_RSENSE = 3*50     ' .003 Ohms * gain 50 from INA180B2
```

Vendor: Rev A `I = Vsense / 5`; Rev B `Isense = Vsense / 150`. **Both match, including the
INA180B2 part number and the 50 V/V gain already named in the source comment.** The
`getCurrent()` divisor is correct and needs no change.

## 2.3 SETTLED — the current channel *is* a DC-link shunt. **S-2 is buildable.**

The vendor calls it *"Total MOSFET load current"*, sensed *"between common MOSFET GND and
common system GND"* — the return path of the entire bridge. That is DC-link sensing, on
**both** revisions.

This closes a question that was going to be answered on the bench:

- **T1-5's proportionality check** was designed to discover whether the board's channel is a
  DC-link shunt or something else. **It is.** The check downgrades from a determination to a
  sanity check.
- **S-2 — "no driver-side current limit"** was blocked on exactly this. A current limit
  *can* be built on this channel, because the channel measures total bridge current. The
  question is now design, not feasibility.

## 2.4 SHARPENED — S-3 stands, and now has an exact expected value

**S-3 is unaffected as a defect.** It concerns the ADC normalisation — the four dropped
`sar sense_x_, #11` instructions and `numerator := 3300 * adc_fram` — not the shunt constant.
The vendor data does not touch that code path.

But it makes **T1-5** much stronger. On Rev B the true relationship is exactly:

```
sense_i_mV(true)  =  150 × amps
```

So the S-3 error factor is `sense_i_mV(observed) / (150 × amps)`, and the prediction is that
it comes out at `adc_fram` — 6136 at 270 MHz. That is the *same constant* **T1-4** derives
from the clock sweep with no external reference at all. Two independent routes to one number,
with the vendor supplying the scale for one of them.

## 2.5 CONFIRMED — the Rev-B-only bench policy, quantitatively

5 mV/A vs 150 mV/A is exactly the **30×** ratio the second study asserted. At 10 A, Rev A
presents 50 mV to a 3.3 V ADC; Rev B presents 1.5 V. Rev B is the better instrument by a wide
margin, and the policy stands on measured grounds.

## 2.6 EXPLAINED — why `getBoardType()` works

`getBoardType()` (`isp_bldc_motor.spin2:600`) drives `pinbase+4` high, floats it, and counts
500 reads: Rev A always 0 *("a 1K pulldown on that board")*, Rev B 40–180 *(0.1 µF cap
discharge)*, no board >250.

`pinbase+4` is `pin_adc_cur_i` — **the current-sense pin**. So the detection keys off exactly
the sub-system the two revisions actually differ in: Rev A exposes the bare shunt node with a
pulldown; Rev B exposes the INA180B2 output with its filter capacitor. The heuristic is sound
and the vendor data explains *why*, which the code only asserted.

## 2.7 NEW QUESTION — the hall front end is identical, so why is the DocoEng offset per-revision?

`offsetsForMotor()` gives `MOTR_DOCO_4KRPM` two different offset tables:

| | 7.4 V | 11.1 V | 12 V | 14.8 V | 18.5 V | 22.2 V | 24 V |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Rev A | 52 | 53 | 53 | 53 | 54 | 54 | 53 |
| Rev B | 33 | 33 | 39 | 40 | 36 | 37 | 45 |

That is a **~15–20° shift attributed to board revision.** But §1.1 shows the hall input path
is *character-for-character identical* between revisions — same pull-ups, same series
resistors, same header, same 5 V rail.

**No hardware delay difference between the revisions can account for it.** Commutation offset
compensates total loop delay. The delays that *do* differ are the gate-driver propagation
(39 ns vs ~20 ns, a 19 ns difference) and, in principle, the dead gap (260 ns — and identical
in practice, per **A1**). Converted to electrical degrees:

- 6.5″ hub motor, 15 electrical cycles/rev (from **C-1**'s exact speed law), at ~274 RPM →
  68.4 electrical Hz → 14.6 ms per electrical cycle.
- **18° = 730 µs.**
- The candidate hardware differences are **19 ns and ~260 ns** — three orders of magnitude
  too small.

So the per-revision table is **not explicable by the electrical differences between the
boards.**

**Leading hypothesis — it is an instrumentation artifact, and it points straight at S-3.**
The offsets were selected empirically by minimum current draw and fault behaviour (the bench
notes in the source say so: *"51-54 best, 55 fault?!"*). Rev A and Rev B present current to
the P2 at scales **30× apart**, and `sense_i_mV` is additionally wrong by `adc_fram` (**S-3**).
A selection criterion resting on current readings and fault thresholds would therefore return
**different answers on the two boards for reasons of measurement rather than physics.**

**This inverts AJ's framing.** The audit treated the DocoEng table as the mature
characterisation and the 6.5″ motor's single hardcoded `43` as the immature one. The better
question is: **why does the DocoEng offset vary by board revision at all, and is that table
measuring the motor or measuring the instrument?**

**Resolvable on the bench as planned** — **T1-10** and **T1-11** sweep offsets and are valid
before S-3 is fixed, because a constant scale error does not move the location of a current
minimum. But a *30× difference in scale between boards* is not a constant error across the
comparison, which is precisely why the two tables could diverge. Worth running T1-10 on a
Rev B board and comparing against the Rev A column.

## 2.8 OPEN — can the board see regeneration? (INA180B2 directionality)

Both revisions sense low-side. Under regenerative braking, current reverses through the shunt,
which drives the sense node **below system ground**.

- **Rev A** exposes the bare shunt node. A negative excursion at a P2 pin is clamped by the
  protection diode; the P2 cannot read below GND. **Regen is very likely invisible.**
- **Rev B** interposes the INA180B2. Whether regen is visible depends on whether that specific
  variant is unidirectional or bidirectional, and on how its reference pin is tied. **Not
  determined here** — the vendor points at the TI INAx180 datasheet, "Precise Low-Side Current
  Sensing" and §9.2, which has not been consulted (no standing outward network reach in this
  project).

**Why it matters:** **T1-1** wants regen current during braking, and battery safety during
regen is a question nobody has been able to ask. If the board cannot see it, the §2A front
end's **bidirectional** Hall sensor (ACS758, chosen for exactly this) is not a luxury — it is
the only instrument that can answer it.

**Action:** read the INA180B2 datasheet before T1-1, or accept the front end as the sole regen
instrument.

## 2.9 NOTE — the hall header's 5 V rail is a convenient supply for the §2A front end

The vendor rates the HALL/INPUTS 5 V output for *"a low current hall sensor (or similar sensor
up to 100 mA)"*. The §2A front end's ACS758 needs 5 V at roughly 10 mA. §2A currently plans to
take 5 V from the P2 Eval board; the motor board's hall header is an equally valid source and
is physically closer to the current path being measured.

## 2.10 Also confirmed: the 3.9 kΩ / 3.9 kΩ hall network is safe by the P2's own limits

Pull-up 3.9 kΩ to 3.3 V, series 3.9 kΩ to the P2 pin. With a 5 V push-pull sensor driving the
node, current into the P2's protection diode is `(5 − 3.3) / 3.9 kΩ ≈ 0.44 mA` — well under
the P2's **±10 mA** protection-diode limit and its ±30 mA per-pin limit (P2 datasheet,
absolute maximum ratings). The vendor's stated purpose — *"to protect the microcontroller from
5 V signals"* — checks out numerically.

---

## Findings this file touches

| Finding | Effect |
| --- | --- |
| **A1** | Revised — see §1.3. Both revisions specify 250 ns; delete the conditional |
| **S-2** | **Unblocked** — §2.3, the channel is a DC-link shunt on both boards |
| **S-3** | Unchanged as a defect; **T1-5 sharpened** with an exact expected value — §2.4 |
| **AJ** | **Reframed** — §2.7, the per-revision DocoEng table may be measuring the instrument |
| **AI** | T1-10/T1-11 gain a second purpose — §2.7 |
| **T1-1** | Regen visibility now an open hardware question — §2.8 |
| **T1-5** | Downgraded from determination to sanity check — §2.3 |
| Rev-B-only policy | Confirmed quantitatively — §2.5 |
