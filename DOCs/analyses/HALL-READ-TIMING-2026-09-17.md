# Where the hall read falls in the PWM frame — «#3571», PL-90 / PL-69

Written 2026-09-17 (night) for «#3571» DO item 3: *from source, compute where the hall read falls in the PWM
frame (clocks after `wait4adc`) against the switching edges, at 200 / 270 / 300 MHz — does the 200 MHz read
land near an edge?* **Everything here is DERIVED from source and from p2kb. Nothing is measured.** The labels
follow doctrine overlay P8.

## 1 · The read's position, in clocks

`.ctlMotor` (`src/isp_bldc_motor.spin2`) starts each 22.7 µs frame by waiting for the current-sense ADC's IN flag
(`wait4adc`), then runs a fixed sequence before it reads the halls. Instruction costs are p2kb's: 2 clocks for
the ordinary instructions, `QROTATE` 2..9 (it waits for the cog's CORDIC slot, one per 8 clocks), and a result
available **55 clocks after issue** (`p2kbPasm2Qrotate`), which the `GETQY` waits for (`p2kbPasm2Getqy`).

| Step | Clocks | Running total |
| --- | --- | --- |
| `wait4adc` exit (poll loop of `TESTP`/`JMP`, then `RET`) | ~4-10 | ~7 |
| 4 × `RDPIN` | 8 | ~15 |
| 4 × (`SUB`, `MULS`, `SAR`) scaling | 24 | ~39 |
| `MOV`, `SHR`, `MOV` | 6 | ~45 |
| three `QROTATE`s 8 clocks apart, then three `GETQY`s; the third result is ready 55 + 16 after the first issue | ~75 | ~120 |
| min / max of the three phases (10 instructions) | 20 | ~140 |
| centring (`ADD`, `SAR`, 3 × `SUB`) and bias (3 × `ADD`) | 16 | ~156 |
| bridge state (`CMP` and four conditional instructions) | 10 | ~166 |
| the six `WYPIN`s with their dead-gap `ADD`/`SUB`s | 24 | ~190 |
| **hall read** | | **~190 ± 10 clocks** |

The old read spanned 8 clocks from there (`TESTP` W, V, U, 4 clocks apart); the new one is a single `INA`/`INB`
read, which samples the port 3 clocks before the instruction.

| Clock | ~190 clocks is | Frame (22.7 µs) fraction |
| --- | --- | --- |
| 200 MHz | **0.95 µs** | 4.2 % |
| 270 MHz | 0.70 µs | 3.1 % |
| 300 MHz | 0.63 µs | 2.8 % |

The read sits a fixed number of **clocks** after the frame starts, so in **time** it moves with the clock.

## 2 · Where the switching edges are

**Assumptions, each from the source's own comments and not independently checked:** `driveinit` raises the ADC
pins' DIR two instructions (4 clocks) before the PWM pins', so the ADC's count period ends ~4 clocks before the
PWM frame boundary; the triangle counter starts each frame at its top and counts down (the comment beside the
`bias` adds: *"the counter runs from the frame period down to 1 and back up"*); an output is high while the
counter is at or below its Y.

With `top` = half the frame in clocks (2 272 / 3 068 / 3 409 at 200 / 270 / 300 MHz), a high-side pin at duty
value Y rises at `t = top - Y` clocks into the frame. **An edge therefore lands on the read when
`Y ≈ top - 190`**, i.e. at a modulation `Y / top` of:

| Clock | high-side edge on the read | low-side edge (Y + dead_gap, 260 ns) on the read |
| --- | --- | --- |
| 200 MHz | **0.92** | **0.89** |
| 270 MHz | 0.94 | 0.92 |
| 300 MHz | 0.94 | 0.92 |

An edge that lands up to one ringing time *before* the read disturbs it too, so each figure is the lower edge of
a band that extends upward.

**How high Y actually goes.** `duty_max` is half of `pwm_limit`, so the phase amplitude is at most about
`top / 2` around a bias of `top / 2`, and the min/max centring caps the peak at roughly
`top/2 + 0.87 × top/2 ≈ 0.93 top` (DERIVED). So:

- at **200 MHz** both the high-side (0.92) and the low-side (0.89) coincidence are **inside** the reachable range,
  near full duty;
- at **270 / 300 MHz** the high-side coincidence (0.94) is just **outside** it and only the low-side edge
  (0.92) can reach the read.

**Answer to the task's question: yes, plausibly.** At high modulation a switching edge can land at, or ring
into, the hall read at every clock, and **at 200 MHz there are two edges that can, reached at lower duty, where
at 270 and 300 MHz there is one.** That is a clock-dependent mechanism of the kind PL-69 needs, which the
three-TESTP tear (PL-90's first hypothesis) could not supply. It is **not established** as PL-69's cause: the
table rests on the three assumptions above, the ringing time on this board is unknown, and PL-69's RIGHT-only
pattern still needs a per-motor difference (a harness, a connector, a sensor).

## 3 · What «#3571» does about it, by construction (doctrine overlay P10)

The read time is not moved: any fixed position in the frame is hit by some duty. Instead the edge is kept out
of the sample:

- **Each hall input is filtered through the P2's global `filt1`** (`WRPIN %FFF = %101`, `p2kbArchSmartPins`
  *input_logic_and_filtering*): three flip-flops clocked every 32nd clock, so a level must hold ~96 clocks —
  **0.48 µs at 200 MHz, 0.36 µs at 270, 0.32 µs at 300** — before `IN` follows it. A switching-edge glitch
  shorter than that is not seen at all.
- **Latency trade, stated:** the filter delays a real hall edge by at most ~96 clocks (< 0.5 µs). At the 6.5″
  motor's top speed (~480 ticks/s) hall edges are ≥ 2 ms apart, and the loop samples every 22.7 µs, so the
  delay is under 2.2 % of one sample period and 0.025 % of the edge spacing — invisible to the position
  estimate. The filter is `filt1` at its **chip reset default**; nothing in this project writes `HUBSET`
  filters, and the driver deliberately does not (they are global, and not the driver's to own).
- **The three lines are read at one instant** (one `INA`/`INB` read), so no skew between the lines remains either.
- **The illegal-code counter is split** into `%000` (low word) and `%111` (high word) of the same status long, so
  the next reading says which way a line was pulled. PL-90's network argument predicts `%000` if coupled noise
  drags a HIGH line low.

**Certification (Visit 6):** `R17-DUAL-HALL-K200 / -K270 / -K300`, one per clock load, zero illegal codes per
motor over the load, with `BM-HALLINT` printing `%000` / `%111` / missed per lifetime. **The "before" is already
on file**: Visit 3's 200 MHz load read 3 and 5 illegal codes on the RIGHT motor and none at 270 or 300 (PL-69).
The atomic read and the filter are certified together; separating their contributions would be characterising
our own former antipattern (P10), which the release does not need.

⚠ **A limit to state (doctrine D2):** the CLOCK load's one rung runs a lifted wheel at 75 000 000, well below
full duty, so it may never reach the coincidence band above. A zero there says the fix holds at that duty, not
at full duty. The ladder load (part A, 270 MHz) reaches the top rungs, and its per-rung integrity counts are the
wider reading.
