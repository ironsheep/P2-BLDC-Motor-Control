# Shakedown of the two rebuilt instruments — 2026-09-21 evening

> ⚠ **Two figures in §4 are superseded by `SCAN-SELFLOCATE-EVALUATION.md` (same folder).** That run
> let every rung locate its own minimum and showed this one's quarter-speed values were biased by the
> inherited centre. **`L` moves 10–12° per halving, not 9.55°** (the effect is larger), and **`Z` is
> −3.7° ± 0.6° across five measurements, not stable to 0.15°** (that was one motor's coincidence).
> The *direction and substance* of §4 stand and were strengthened; the two numbers did not.
> Everything else in this report is unaffected.

**Logs (this folder, both COMPLETE):**
- `debug_260921-174553.log` — 2,381 lines, tier `dual-align`, `test_bench_dual.bin`, ALIGN part.
- `debug_260921-174731.log` — 1,702 lines, tier `scan`, `test_bench_scan.bin`, `src_rev 17, fmt 10`.

**Source:** `b37b89c`. Scan banner: `cfg_id BENCH`, left base 32, right base 16, voltage enum 6,
`def_neg_deg 43 / def_pos_deg 317` (the scan's own sweep reference, not the driver's shipped pair).

**Purpose.** Neither instrument had ever touched hardware in its rebuilt form. This was a shakedown:
does each emit what it was built to emit? It was **not** run against a run sheet with falsifiers fixed
in advance, so nothing here is a certification — the loads that certify are `«#3594»`.

**Provenance tags:** **MEASURED** = a log line. **DERIVED** = arithmetic on measured values.
**PRIOR** = scan run 7 (`../2026-09-14/`), for cross-run comparison only.

---

## 1 · Headline

| | |
|---|---|
| **The scan rebuild took.** | Non-OK points now carry real following data where run 7 had `NA` at 19 of 19. |
| **The arc widened, and the torque wall disappeared.** | **0 faults** this run against run 7's **15**. Every walk side stopped on `RISE`. |
| **No fit is pinned.** | `pinned,FALSE` on all **12** fits. Run 7 had all four half-speed fits pinned against a fault edge. |
| **`Z` is a constant; `L` is not.** | Halving the commanded speed moved `Z` by **0.15°** and `L` by **9.55°**. This is the finding that matters to the driver. |
| **ALIGN is safe and its operator protocol works — but it measured nothing.** | Peak current **15 mV** against a 150 mV band. All 8 legs ran. All 8 came back `CLIPPED`, and the cells refused to report a `Z`. |

---

## 2 · ALIGN tier — the procedure works, the signal conditioning does not

### 2.1 What held — MEASURED

- **The no-drive invariant, decisively.** `R18-DUAL-ALIGN-ND` **PASS**, measured **15 mV** against a
  0–150 mV band — about **100× below** the harness's 1,500 mV abort. Per-leg `peak_i_mV` ran 4–15 mV.
  The bridge genuinely never drove. The tier is safe as designed.
- **The operator protocol.** 8 of 8 legs ran. Every leg reached its full `ticks ±270`. No stalls.
  `BM-SEG END … why,NONE`, `BM-END exit,COMPLETE, trap_code,0`. Total **64 s**.
- **The bias fix worked.** `bias_still,TRUE` and `bias_tries,1` on **all eight** legs — every bias
  landed first try. The 2 s → 10 s budget raised the day of the run was not even needed, but the
  reason it was raised (a coasting wheel) never got to bite.
- **Direction labelling proved itself.** All four **RIGHT** legs measured the *opposite* of what was
  asked (`ask_dir,FORWARD` → `meas_dir,REVERSE`). That is the platform's geometry — the right motor
  faces the other way — and the design choice to label a leg by what it **measured** meant four legs
  of good data were filed correctly instead of being mislabelled or discarded.
- **Sector accounting is exact.** `sectors,269` on every leg (270 ticks → 269 closed sectors), and
  `unusable,0` everywhere — not one sector exceeded the 2 s "this is not a turn" bound.

### 2.2 What failed — MEASURED

`R18-DUAL-ALIGN-CLIP` **FAIL**, measured **631,752** railed phase readings against a band of 0.
Every leg's outcome is `CLIPPED`. Consequently `-COVER` and `-RES` are **NOMEAS** and `-MTRX` is
**FAIL**: no leg reached `ALEG_OK`, so no wheel×direction combination was ever marked.

⭐ **The cells did their job.** 2,301 `BM-ACROSS` records were produced. Without the clip detector the
tier would have reported a confident `Z` computed from them. It reported **no `Z` at all**, which is
the correct answer. This is the one place in the run where a check built for a negative case earned
its keep.

### 2.3 Root cause — two distinct defects

**Defect A — the resting point has almost no headroom below it.** MEASURED: the stationary phase
level is **51–63 mV** on both motors, all three phases, extremely stable. The ADC range is 0–3,300 mV.
So the channel's representation of "zero back-EMF" sits only about **55 mV above the bottom rail**. A
back-EMF swing larger than that clips its negative half. DERIVED: 631,752 railed readings against
4,035,642 phase readings taken (3 × the 1,345,214 samples summed across the eight legs) is **15.7 %**
of readings at or below the 20 mV threshold.

⚠ **But clipping the PEAKS does not destroy the ZERO CROSSING.** The crossing happens *at* the bias,
around 55 mV, which is comfortably inside range; only the extremes flatten. **So `ALIGN_CLIP_LO_MV`
judges the wrong thing** — it disqualifies a leg for peak railing when the measurement only needs the
crossing region clean. That criterion is mine and it is wrong.

**Defect B — the crossing detector has no hysteresis, and this one is real.** MEASURED, leg 0's first
sector (`dur_us 185_577`): crossings arrive as falling/rising **pairs about 50–150 µs apart** —
`t_us 1_834` falling then `1_887` rising; `45_630`/`45_684`; `47_805`/`47_859`; `49_884`/`49_986`.
A back-EMF zero crossing does not reverse in 50 µs. These are **jitter at the bias level**, not signal.

DERIVED: a leg should yield 3 turns × 15 electrical cycles × 3 phases × 2 crossings = **270**. Leg 0
produced `cross,288` (the buffer cap) plus `dropped,1_199` — about **1,487**, some **5.5×** the
physical count. The buffer overflow is a *consequence* of B, not an independent problem.

⚠ **Note where the jitter is worst:** the first sector lasts 185 ms, i.e. the hand is barely moving,
where back-EMF is near zero and the signal is pure noise. `dropped` falls sharply on the faster legs
(leg 2: `dropped,0`). So the noise dominates at the **start of each leg**, before the operator is up
to pace.

---

## 3 · Scan rebuild — every mechanism the rebuild added worked

### 3.1 The defect the rebuild existed to fix — MEASURED

Run 7 carried `rate_x10,NA` at **19 of 19** non-OK points. This run's four `ABORT_I` points each carry
the full drive-span record:

| seq | motor | `span_ms` | `span_rate_x10` | `follow_pct` | `span_duty_mean` | `span_duty_max` |
|---|---|---|---|---|---|---|
| 5 | LEFT | 830 | 228 | **46** | 3,298 | 6,400 |
| 25 | LEFT | 849 | 235 | **47** | 2,927 | 5,266 |
| 79 | RIGHT | 810 | 222 | **45** | 2,864 | 5,339 |

⭐ **And the numbers are informative, not merely present.** At the instant the current wall was hit,
the drive was following at **45–47 % of commanded** with duty demand saturating. Run 7 recorded a
result token and nothing else at exactly these points. The boundary is now *characterised* rather than
crashed into, which was the whole point.

### 3.2 The arc widened and the torque wall vanished — MEASURED

| leg | run 7 (walked at **quarter**) | this run (walked at **an eighth**) |
|---|---|---|
| LEFT NEG reachable | `8 … 53` = **45°**, inner wall a **FAULT** | `3 … 53` = **50°**, inner stop a **RISE** |
| LEFT POS reachable | — | `-53 … -13` = **40°**, outer stop **CURRENT** |
| Faults in the whole run | **15** | **0** |

Every `BS-WALK` side stopped on `RISE`. `BS-ARC` labels the outer stops `CURRENT` and the inner ones
`RISE`. **The motor never hit a torque wall at an eighth speed** — walking slower did exactly what it
was predicted to do, and the walk now ends on the good condition rather than on a fault.

The `boundTypeFor()` reclassification also worked: a current abort reaches the walk as `WS_RISE`
(because `isFaultLikeIdx` excludes `PR_ABORT_I` while `isHighIdxFor` counts it as high), and `BS-ARC`
correctly reports those ends as `CURRENT` rather than `RISE`.

### 3.3 The bracketing verdicts — MEASURED

`R18-SCAN-LEGBRACKET`, six instances per motor:

| rung | LEFT NEG | LEFT POS | RIGHT NEG | RIGHT POS |
|---|---|---|---|---|
| **LOW** (walk) | PASS | PASS | PASS | PASS |
| **QTR** | PASS | PASS | PASS | PASS |
| **HALF** | **FAIL** | **FAIL** | **FAIL** | **FAIL** |

⭐ The half-speed rung still cannot bracket its minimum — run 7's finding, unchanged. The difference
is that it is now **reported as a FAIL** instead of passing silently, and each instance names its sign
and rung so the four are distinguishable. All twelve fits report `pinned,FALSE`, so this is no longer
a minimum jammed against a wall; the half-speed fits are simply `POOR`.

### 3.4 Other mechanisms — MEASURED

- **Fold-back headroom, settled.** Worst `i_max_mV` anywhere in the run: **1,036 mV** (≈6.9 A at
  150 mV/A), against a 1,500 mV harness abort and the driver's 40 A fold-back. **No reading was
  capped**, so no fit arm was flattened. The concern is closed with a number.
- **`R9-SCAN-OWNZERO` now reports real counts** (`n,16`, `n,9`, …) rather than the vacuous
  `measured 0 of n 0` its hardcoded `TRUE` used to print.
- **Run health:** `elapsed_s,905`, 142 points, `faults,0`, `aborts_i,4`, `trap_value,0`, both motors
  completed. The third rung cost about 177 s over run 7's 728 s and stayed well inside the 1,800 s cap
  — the "half the ticks at half the rate" budgeting held.

---

## 4 · The measurement: `Z` is a constant, `L` is not

All values DERIVED from `BS-PAIR` and `BS-RESULT-HALF` of this run. `Z` = (neg_min + pos_min)/2,
`L` = (neg_min − pos_min)/2, both in electrical degrees.

| motor | rung | neg min | pos min | **Z** | **L** |
|---|---|---|---|---|---|
| RIGHT | **LOW** (1/8) | +25.1° | −31.9° | **−3.4°** (se 0.3°) | **28.5°** |
| RIGHT | **QTR** (1/4) | +15.4° | −22.5° | **−3.55°** | **18.95°** |
| LEFT | **QTR** (1/4) | +15.3° | −23.3° | **−4.0°** | **19.3°** |
| LEFT | **LOW** | *fit POOR, no minimum* | −32.5° | — | — |

**Cross-run agreement is good** (PRIOR, run 7 at quarter): RIGHT `Z −4.3 / L 18.0`, LEFT
`Z −3.8 / L 17.2`. This run's quarter rung gives RIGHT `L 18.95` and LEFT `L 19.3` — within 1–2° of a
measurement taken on a different day with a different binary. That agreement is what licenses
comparing the rungs at all.

### ⭐ The result

Within **one run, one motor, one pair of wheels**, halving the commanded speed moved:

- **`Z` by 0.15°** (−3.55 → −3.4). Z is geometry. It held.
- **`L` by 9.55°** (18.95 → 28.5). **L is strongly speed-dependent.**

### The alternative explanation, tested and REFUTED

The LOW and QTR fits do not span the same arc (LOW `3…43`, QTR `10…40`), and the basin is not a true
parabola — so a quadratic fitted over a wider span could in principle place its vertex differently
even if the underlying minimum had not moved. That had to be excluded before believing §4, and it
**was excluded from this log, with no new run and ultimately with no fitting at all.**

**The raw measured points settle it.** RIGHT NEG, `net_mV_x10` against swept offset, both rungs:

| swept | 10 | 13 | 15 | 18 | 20 | 23 | 25 | 28 | 30 | 33 | 35 | 38 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **QTR** | 168 | | **132** | | 194 | | 310 | | 525 | | 843 | | 1333 |
| **LOW** | | 178 | | 154 | | 122 | | **96** | | 150 | | 217 | |

The **lowest point actually measured** is at swept **15** at quarter speed and swept **28** at an
eighth — **13° apart, from raw data, with no curve fitted to anything.** At quarter, the current at
swept 28 is about 450 (interpolated) against its minimum of 132; at an eighth, the current at swept 15
is about 165 against its minimum of 96. Each rung's basin is plainly centred somewhere the other's is
not.

For completeness, re-fitting the LOW leg's points over QTR's restricted span (13…38) gives a vertex at
**24.7°** against the full-span fit's 25.1° — a shift of 0.4°. The span is not what put the LOW
minimum where it is.

⚠ **One honest qualification on precision, not on direction.** At the LOW rung the basin is shallower
and asymmetric, so its *fit* is less well determined than the quarter rung's: measured floor 28,
fitted 25.1, three-point fit about 27.1 — a spread of roughly 3°. The quarter rung is tight (floor 15,
fit 15.4). So the *size* of the shift is 9.7° by fit or 13° by measured floor. **The direction and the
order of magnitude are not in doubt; the third significant figure is.**

⚠ **And one that does not apply.** The scan minimises DC-side `sense_i`, not duty-compensated phase
current, so a reading means something slightly different at different duties. That would matter if we
compared *current magnitudes* across rungs — but we are comparing the *location* of each minimum, and
speed is constant within a leg. The comparison is sound.

---

## 5 · What this means for the driver

**The shipped pair is a quarter-speed tune.** `«#3593»` adopted `offset_fwd 14 / offset_rev 338` from
run 7's quarter-speed data. This run's quarter rung puts the optimum at about `15 / 337` — so the
shipped pair is **right, to about 1°, at quarter speed** (MEASURED). That is a genuine confirmation of
the adopted offsets and it should be said plainly.

**But at an eighth speed the same motor wants about `25 / 328` by fit, and its lowest measured point
sits at `28`** — roughly **11–14° away** from the shipped `14` (MEASURED). Since §4's speed dependence
survived the test that could have refuted it:

1. **A single compile-time commutation offset cannot be correct across the speed range.** It is
   correct at the one speed it was tuned at and drifts by ~10° per halving below it.
2. **The low-speed regime is where the shipped offsets are worst**, and that is the same regime
   `«#3589»` already owns for the start transient. Those two problems are now pointing at the same
   place.
3. **This constrains "which knob carries the lead", which is R18.3's correction 2.** The commutation
   offset is feedforward and fixed at compile time; the duty-servo setpoint is regulated. A quantity
   that must vary with speed **cannot live in the fixed knob**. That is an argument from measurement
   rather than from theory, and it is exactly what `«#3589»` was waiting for.

⚠ **What this does NOT license.** It does not say what the speed law is — **two points do not define a
curve**, and a third rung (half speed) produced no usable minimum on any leg. It does not say the
mechanism is current lag; in fact **the sign is opposite to the naive current-lag model**, which
predicts *more* lead needed at *higher* speed, and we measured the reverse. Naming that mechanism is
`«#3589»`'s work, and it should start from the fact that the simple model is not merely imprecise but
**pointing the wrong way**.

**The cheapest way to get a third point** is the existing half-speed rung, which currently yields
`POOR` fits on all four legs. Its confirm span (`10…40`, inherited from the walk's centre) is now
known to be centred roughly 10° away from where a half-speed basin would sit if the trend continues —
which would explain the POOR fits entirely. Re-centring the half rung's confirm set on its *own*
extrapolated optimum, rather than on the walk's, is a one-constant change and would likely convert
four POOR fits into four usable minima.

---

## 6 · Findings register

| # | Finding | Disposition |
|---|---|---|
| **S-1** | ALIGN's no-drive invariant held at 15 mV against a 150 mV band. The tier is safe by construction and now by measurement. | Closed — evidence on file. |
| **S-2** | ALIGN's operator protocol works end to end: 8/8 legs, bias first try, no stalls, 64 s. | Closed. |
| **S-3** | `ALIGN_CLIP_LO_MV` judges peak railing, but only the crossing region needs to be clean. The criterion disqualifies legs that may carry a usable `Z`. | **Fix in the instrument** — judge the crossing neighbourhood, not the peaks. |
| **S-4** | The crossing detector has no hysteresis and fires on bias-level jitter: ~5.5× the physical crossing count, buffer overflow. | **Fix in the instrument** — hysteresis band, and ignore sectors below a minimum edge rate. |
| **S-5** | ALIGN's `clip` counter saturates at `LIM_BIG`, so per-leg values (99,999) are uninformative. | **Fix** — report a rate or a per-phase count. |
| **S-6** | The drive-span observables work and are informative at the boundary (45–47 % following at the current wall). | Closed — the rebuild's purpose is discharged. |
| **S-7** | Walking at an eighth removed the torque wall entirely: 0 faults vs run 7's 15, all stops `RISE`, no fit pinned. | Closed. |
| **S-8** | The half-speed rung still cannot bracket its minimum, on all four legs — now correctly reported as FAIL. | Carry to `«#3589»`: decide whether a half-speed confirm is worth keeping. |
| **S-9** | `Z` stable to 0.15° across a 2× speed change; `L` moved 9.7° by fit, 13° by measured floor. | **Carry to `«#3589»` as the primary input.** Survived S-10. |
| **S-10** | Tested whether S-9 was a fitting artifact of the wider LOW span. **REFUTED** — the raw measured floors are 13° apart (swept 15 vs 28) with nothing fitted, and a restricted-span re-fit moves the LOW vertex by 0.4°. | Closed from this log. No run was needed. |
| **S-13** | The half rung's confirm set is centred on the *walk's* optimum, which the trend says is ~10° from where a half-speed basin sits. This plausibly explains all four POOR fits (S-8). | **Carry to `«#3595»`'s successor / `«#3594»`** — re-centre the confirm set per rung; one constant, likely converts 4 POOR fits to usable minima and yields the third point S-9 needs. |
| **S-11** | No swept reading came near the fold-back limit (worst 1,036 mV of a 6,000 mV cap). | Closed. |
| **S-12** | The droop stop **never fired** — 0 occurrences. The condition did not arise, which is not evidence the detector works. | **Unvalidated.** Carry to `«#3594»`; do not claim it. |

---

## 7 · What is NOT established

- **No `Z` from ALIGN.** The tier's whole purpose is undischarged. `Z` in §4 comes from the *driven*
  scan, which is the indirect route ALIGN was built to replace.
- **The droop detector is unproven** (S-12).
- **Nothing here is certified.** No run sheet, no falsifiers fixed in advance. These were shakedowns.
  The *direction* of S-9 is solid because it survived a test that could have killed it; its *shape*
  is not, and a certification run still owes it.
- **The speed law for `L` is unknown** — two usable points is a direction, not a curve. S-13 is the
  cheap route to a third.
- **The mechanism behind S-9 is unnamed.** We know the naive current-lag model has the wrong sign. We
  do not know what does. That is `«#3589»`'s to settle and it should not be guessed here.
