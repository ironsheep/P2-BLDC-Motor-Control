# Bench Pass 2a — scan run 3

**Log:** `debug_260912-230836.log` (this folder, 447 lines).
**Source:** `f1fead2`, `-D BENCH_CFG`. **Run:** Stephen, 23:08:36, ended on its own at 229 s.
**Result:** `BS-END ABORTED SELF_CHECK_MISS` on the RIGHT motor. The LEFT motor completed both
of its ¼-speed legs and its positive ½-speed leg (40 points, 7 faults, 2 current aborts, all
recovered).

**Provenance tags:** MEASURED = a log line · DERIVED = my calculation or reading of source ·
STEPHEN = his words. Sense readings are mV at 150 mV/A (Pass 1 finding 2).

---

## 1 · The start fix holds — MEASURED

`illegal 0` and `missed 0` on all seven `BS-START` records, both motors (log:43, 63, 83, 134,
262, 425), and `illegal_d 0` on every point. Rev B at every start. «#3524» is confirmed.

## 2 · LEFT self-check passed

| Check | Band | Measured |
|---|---|---|
| zero | −10..30 mV | 7.0 (4–12) |
| +¼ at 317° | 68–114 | 88.5 |
| −¼ at 43° | 127–212 | 171.3 |
| ratio | 1.55–2.20 | 1.935 |
| rate | 90–106 | 98.2 |

These match Bench Pass 1's left wheel (90.7, 169.5 mV): the instrument agrees with itself
across binaries and days.

## 3 · LEFT offset curves — MEASURED

"Swept" is the scan's signed offset: the `offset_fwd` value for a negative increment, and
`offset_rev − 360` for a positive one. Defaults are +43 and −43.

**Negative increment (`offset_fwd`), ¼ speed**

| swept | 63 | 53 | **43** | 33 | 23 | 13 | 3 | −7 |
|---|---|---|---|---|---|---|---|---|
| mV | ABORT_I | 391.9 | **171.3 / 171.1 / 183.8** | 85.1 | 43.2 | 33.8 | FAULT | FAULT |

`NOT_BRACKETED, EDGE_FAULT`: the current was still falling at 13° when the next step faulted.
There is no fit, and the ½-speed leg was skipped.

**Positive increment (`offset_rev`), ¼ speed**

| swept | −63 | −53 | **−43** | −38 | −33 | −28 | −23 | −18 | −13 | −8 | −3 | +7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coarse mV | ABORT_I | 219.0 | **101.2** | | 50.0 | | 32.5 | | 39.2 | | FAULT | FAULT |
| fine mV | | | **88.4 / 87.6** | 55.2 | 36.9 | 22.3 | 17.4 | 21.3 | 23.6 | FAULT | FAULT | |

Fit: minimum at **−21.1° ± 0.7 (offset_rev 339°)**, 16.3 mV against 94.4 mV at the default, an
82.7 % saving, rms 2.8 mV, n 7. It is bracketed by a genuine rise (17.4 → 21.3 → 23.6) before
the fault at −8°. `drift_flag TRUE` (see §5).

**Positive increment, ½ speed**

| swept | **−43** | −36 | −31 | −26 | −21 | −16 | −11 | −6 |
|---|---|---|---|---|---|---|---|---|
| mV | **473.6 / 470.5** | 231.8 | 132.6 | 68.8 | 35.2 | 25.0 | 22.2 | FAULT |

Fit `POOR`: minimum at −15.4° ± 0.8, a shift of +5.7° from ¼ speed (significant). Current was
still falling at −11° when −6° faulted, so at ½ speed the minimum is bounded by the fault, not by
a rise.

## 4 · What the curves say — DERIVED

- **The default offsets waste most of the drive power, and more so at speed.** Positive
  increment, ½ speed: 472 mV ≈ **3.1 A** at the default against 22.2 mV ≈ **0.10 A** net of the
  zero at −11°, the same tick rate (196.5/s) and a lower duty (15 717 → 11 333). At ¼ speed it is
  ≈ 0.54 A against ≈ 0.07 A. This matches Pass 1's finding that doubling speed cost 5.5× the
  power.
- **Both directions have a fault cliff near swept 0.** The negative cliff lies between +3 and
  +13, and the positive one between −8 and −13 (¼) or −6 and −11 (½). The cliffs are roughly
  mirror images, which puts the hall pattern's electrical zero near 0.
- **The minimum-current offset sits beside the cliff.** Positive: minimum at −21, cliff past
  −13. Negative: still falling at +13, cliff by +3. **The margin is 10° or less, measured with the
  wheels unloaded.** Load increases the lag the driver must carry, so an offset at a no-load
  minimum may fault under a robot's weight. No-load current alone cannot choose the shipped
  offset.
- **Near-identical load in both directions is within reach.** At mirror offsets the
  negative/positive ratio is 1.94 at ±43, 2.5 at ±23 and 1.4 at ±13. Negative +13 (33.8 mV)
  against positive −33 (36.9 mV) is within 10 %, at a fifth of today's negative-direction
  current. Neither side has a margin measured under load.
- **The optimum moves with speed** (+5.7° from ¼ to ½), so one fixed offset cannot be
  minimum-current at every speed.

## 5 · A bias on some points — MEASURED, cause unknown

At the same positive offsets the coarse points read higher than the later fine points:
- 13 mV at −33,
- 15 mV at −23,
- 16 mV at −13.

The −43° reference read 101.2 at the start of the leg, against 88.5, 88.4 and 87.6 elsewhere.
The negative reference read 183.8 after the negative leg's faults, against 171.3 before. Duty is
the same in both readings (5967 vs 5978 at −23), so the motor is not doing more work. It is a
sense-side shift of ~13–16 mV that appears after some high-current or fault events and is gone
later. It moves the fit by a few degrees at most, and it does not change §4.

## 6 · RIGHT self-check failed on the zero — MEASURED

| Check | Band | Right now | Right, Pass 1 | Left now |
|---|---|---|---|---|
| zero | −10..30 | **73.4** (71–76) | ≈ 9 (fit) | 7.0 |
| +¼ | 68–114 | **161.2** | 91.6 | 88.5 |
| −¼ | 127–212 | **237.3** | 168.2 | 171.3 |
| rate | 90–106 | 98.2 | 96 | 98.2 |

**DERIVED:** with its zero subtracted the right wheel reads 87.8 / 163.9 mV. That is Pass 1's
right wheel within 6 %, and a net ratio of 1.87, inside the band. Duty matches the left
(7249 / 8133 vs 7147 / 8116). The right channel therefore carries a **constant +64–73 mV**
(≈ 0.45 A equivalent) that it did not carry in Pass 1, while the left is unchanged.

The driver code is identical for both pin groups, and the left reproduces Pass 1 through every
change since, so the source does not explain a right-only shift. Two physical explanations fit
equally, because both add a constant through the shunt or amplifier:
1. an offset in the right board's sense path, such as a ground or connector shift or the
   amplifier;
2. a real ~0.45 A drawn by the right bridge at idle.

The second would warm the board, roughly 8 W at 18.5 V. **Which one it is is a question about
the rig, and it goes to Stephen** (doctrine P8). The self-check stopped correctly; its band is
not loosened.

## 7 · Disposition

**Do not apply** («#3523» does not run):
- the negative minimum is not bracketed;
- the right motor produced no scan data;
- the ½-speed minimum moved and is bounded by a fault;
- every minimum sits within 10° of a fault measured without load.

## 8 · Instrument changes this run motivates

- **Fine-walk into a fault edge** before declaring `EDGE_FAULT`. A 5° step between the last good
  point and the fault would bracket or locate the cliff; the negative leg stopped 10° short.
- **Locate the cliff deliberately and report the margin**, because the usable offset is set by
  the cliff under load, not by the no-load minimum.
- **Re-measure the zero at each reference point** and log it, so a sense-side bias (§5) is
  measured rather than inferred.
