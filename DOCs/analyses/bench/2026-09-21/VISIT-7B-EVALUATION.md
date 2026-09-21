# Visit 7b — evaluation: the phasing A/B

**Run date:** 2026-09-21 · **Plan section:** R18.2c · **Task:** «#3588»
**Sheet this judges against:** [`../VISIT-7B-RUNSHEET.md`](../VISIT-7B-RUNSHEET.md)

| Leg | Log | Offsets | Banner |
|---|---|---|---|
| **CONTROL** | [`debug_260921-124024.log`](debug_260921-124024.log) | `off_neg,43 off_pos,317` | `src_rev,23 fmt,11 part,A` |
| **CANDIDATE** | [`debug_260921-125233.log`](debug_260921-125233.log) | `off_neg,14 off_pos,338` | `src_rev,23 fmt,11 part,A` |
| *baseline for comparison* | [`../2026-09-20/debug_260920-182503.log`](../2026-09-20/debug_260920-182503.log) | `43 / 317` | `src_rev,22 fmt,10` (Visit 7) |

---

## Verdict, stated against the table fixed before the run

> **Row 1 of the sheet's decision table.** *"The candidate's ratio moves materially toward 1.0 **and**
> absolute current at rungs 3–5 falls → apply the pair as the default; R18.3 designs against the
> corrected baseline, and the residual absolute current scopes correction 2."*

Both conditions are met, and the second is met by a margin nothing on the sheet anticipated. The
direction-to-direction ratio went from **2.06 to 1.01**; absolute netted current at rungs 3–5 fell by
**15× to 26×**. The middle row (residual imbalance) and the bottom row (ratio barely moves) are both
falsified. **«#3590» does not open** — its precondition was the ratio failing to move toward 1.0.

---

## The banner check, first

Per the sheet, nothing below is worth reading if this fails. It does not fail.

- Both legs: `BM-BANNER,seq,2,src_rev,23,fmt,11,part,A,cfg_id,BENCH,…,clkfreq,270_000_000,voltage_enum,6,motor_type,0`
- Control leg, every `BM-RUNG`: `off_neg,43,off_pos,317`
- Candidate leg, every `BM-RUNG`: `off_neg,14,off_pos,338`
- Both legs ended clean: `BM-END,…,exit,COMPLETE,part,A,segs,5,last_seg,LOWSPD,trap_code,0,unrecov,0,why,NONE`
- **Record counts are identical between legs** — 178 `BM-RUNGTR`, 178 `BM-RUNGHL`, 172 each of
  `BM-RUNG`/`BM-RUNG2`/`BM-RUNG3`, 48 `BM-TRACE`, 20 `BM-LOW`, 12 `BM-LADDER`. The two legs executed
  the same program over the same command space; the only difference is the compiled offset pair.
- **Zero faults in either leg.** Every `flt` field in all 14_904 / 14_925 `BM-TS` records reads
  `FALSE`; the only `why` tokens present anywhere are `NONE` (1_039 records) and `NO_COG`.

---

## §1 — The cells

All three new R18 cells **PASS on both legs**, and every inherited cell holds its Visit 7 verdict.

| Cell | Control | Candidate | Reading |
|---|---|---|---|
| `R18-DUAL-OFFSETS-A` | PASS, `measured,0` of `n,178` | PASS, `measured,0` of `n,178` | **«#3586»'s owed run-time read-back, now collected.** The driver runs the pair its build selects — the desk claim is a measurement. |
| `R18-DUAL-INSTWIDE-A` | PASS | PASS | **«#3587»'s owed falsifier.** See §5. |
| `R18-DUAL-PHSEP-A` | PASS, `n,206` | PASS, `n,206` | **«#3587»'s other owed item.** See §5. |
| `R17-DUAL-TRKICK-A` | **FAIL** L 38 / R 37 of 74 | **FAIL** L 19 / R 17 of 74 | Criterion is zero kicks, so both fail. The count **halved**; the magnitude fell 6×. See §4 and F3. |
| `R16-DUAL-LAGBND-A` | PASS, max_err L 115 / R 115 | PASS, max_err L 100 / R 113 | Bound is 124. The lag limiter never binds in either leg. |
| all other 19 | PASS | PASS | idle-fault, Rev-B detect, hall integrity, no-fold, rate-law, traces, quiet masks |

---

## §2 — The headline: the asymmetry is gone

**Direction convention.** The ratio below is *negative-increment current over positive-increment
current*, netted of each board's sense zero. That orientation is not chosen — it is the one that
reproduces the sheet's Visit 7 table exactly, so it is the sheet's "reverse over forward". Note that
the negative-increment direction is the one `offset_fwd` governs (the naming inversion «#3586»'s
hand-back flagged and PL-39 already records); the physics below is unaffected by what it is called.

| motor | rung | VISIT 7 | **CONTROL** | **CANDIDATE** |
|---|---|---|---|---|
| LEFT | 2 | 1.93 | 1.96 | **0.99** |
| LEFT | 3 | 2.02 | 2.04 | **1.01** |
| LEFT | 4 | 2.04 | 2.06 | **0.95** |
| LEFT | 5 | 1.97 | 1.99 | **0.98** |
| RIGHT | 2 | 1.88 | 1.89 | **0.95** |
| RIGHT | 3 | 1.91 | 1.92 | **1.01** |
| RIGHT | 4 | 1.93 | 1.94 | **0.92** |
| RIGHT | 5 | 1.87 | 1.88 | **0.91** |

⭐ **The control reproduces Visit 7 to within 0.02 on every one of the eight cells.** That is the
strongest thing in this run and it is worth stating before the result it supports: the rig, the
instrument and the platform are stable across a day and a source revision, so the candidate leg's
difference is attributable to the offsets and to nothing else. The A/B has a real control.

---

## §3 — The finding the sheet did not anticipate: absolute current collapses

The ratio was the declared metric. It is not the largest thing in the data.

Mean netted current `inet_x10`, and the duty servo's demand as a percentage of `duty_max`, at the
same commanded rung and the same met rate:

| motor | rung | CONTROL neg / pos | CANDIDATE neg / pos | current factor |
|---|---|---|---|---|
| LEFT | 3 | 1991 @ 37.1% / 977 @ 32.6% | **130 @ 26.9% / 129 @ 26.9%** | **15.3× / 7.6×** |
| LEFT | 4 | 5422 @ 59.1% / 2636 @ 51.3% | **230 @ 40.0% / 242 @ 40.0%** | **23.6× / 10.9×** |
| LEFT | 5 | 10879 @ 83.7% / 5461 @ 72.0% | **417 @ 53.9% / 424 @ 53.9%** | **26.1× / 12.9×** |
| RIGHT | 3 | 2041 @ 37.2% / 1063 @ 33.2% | **137 @ 27.2% / 136 @ 27.1%** | **14.9× / 7.8×** |
| RIGHT | 4 | 5514 @ 59.1% / 2850 @ 51.9% | **240 @ 40.3% / 262 @ 40.4%** | **23.0× / 10.9×** |
| RIGHT | 5 | 11016 @ 83.3% / 5875 @ 72.7% | **425 @ 54.1% / 469 @ 54.4%** | **25.9× / 12.5×** |

In calibrated amps (`amps_x10k`, rung 6, the control's worst): LEFT **7.40 A → 0.46 A**, RIGHT
**7.75 A → 0.49 A**.

**Why this is a measurement and not an artifact.** Three independent observables agree, and they do
not share a signal path:

1. **The current sense channel** (`inet_x10`, `amps_x10k`) — falls 15–26×.
2. **The duty servo's own demand** (`duty`) — falls from 83.7% to 53.9% at rung 5, from 99.9% to
   68.4% at rung 6. The servo is a closed loop on speed; it is asking for far less voltage to hold
   the same speed. This is not read through the sense channel at all.
3. **The commanded rate is met in both legs.** `rate_x10 / pred_x10` is 0.989–1.009 at every ladder
   rung in both legs, and the single worst deviation in the run — 1.0451, LEFT rung 0 — is
   *identical in all three logs*, so it is the lowest rung's quantisation, not a leg difference.

The machine is turning the same wheel at the same speed for between a seventh and a twenty-sixth of
the current. The sense zeros are unchanged between legs (LEFT ≈ 82 and ≈ 81, RIGHT ≈ 1 and ≈ 5.5), so
the netting is not doing the work.

---

## §4 — SS6.1a's falsifiable prediction: **HELD**

The current-collapse study left a prediction on the record, written before this run:

> *"The knee should pin at the same rung or slightly HIGHER on the candidate leg. If it moves DOWN,
> SS6.1a is wrong and reopens."*

**It moved up, by two rungs.**

| | CONTROL | CANDIDATE |
|---|---|---|
| duty first reaches ~99.9% | **rung 6** | **rung 8** |
| duty at rung 6 | 99.9% | **68.4%** |
| duty at rung 7 | 100.0% | **83.6%** |
| net current peaks at | **rung 6** (12_543) | **rung 8** (1_510) |
| `win_cap` frames, run total | 1_890_038 | **278_434** (6.8× fewer) |

SS6.1a said the rung-6 current collapse is a real voltage/back-EMF limit rather than a commutation
defect. If it had been a commutation defect, correcting the phase would have moved the knee *down* or
left it alone. Correcting the phase bought two rungs of headroom — exactly what a voltage-limit model
predicts when the current needed per unit torque falls. **SS6.1a survives its first real test**, and
`win_cap` corroborates it from a fourth, independent counter.

The ceiling has not been removed: at rungs 9–11 the candidate is also saturated (99.9–100.0%) and its
current falls away in the same manner. It has been **pushed two rungs further out**.

---

## §5 — «#3587» discharged, and what it bought

- **Instrument, at the widened sample.** `BM-INST,…,event,STOP,…,samples,300_922,late,0,skipped,0,max_late_us,0,clamps,0`
  (control) and `samples,301_108,late,0,skipped,0,max_late_us,0,clamps,0` (candidate). The falsifier
  was that a wider sample buys its width by dropping samples. It does not — at 9→11 longs, across
  ~301 k samples, **nothing was late, dropped or clamped in either leg**.
- **The phases really are carried apart.** Visit 7 (fmt 10): all 152 ladder records have
  `phu == phv == phw == 0` — the per-phase fields did not exist, which is precisely the defect
  §6.5/F13 recorded. Today (fmt 11): **zero records with the three equal, zero with all three zero**,
  and the per-record spread runs 1 / 216 / 445 (min/median/max) on the control and 18 / 225 / 478 on
  the candidate. The packing error the cell was built to catch did not happen, and R18.3 now has the
  per-phase signal it needs for a rotor-angle estimate.

---

## §6 — Findings register

| # | Finding | Status |
|---|---|---|
| **F1** | **The commutation asymmetry is eliminated.** Rungs 2–5, both motors: 1.87–2.06 → 0.91–1.01. | MEASURED, both legs |
| **F2** | **Absolute current falls 15–26× at rungs 3–5** at the same met rate, corroborated independently by the duty servo's demand. This is the release's largest single result. | MEASURED |
| **F3** | **The transition kick's magnitude fell ~6×**: worst `tr_i_over` 1_247 → 204; mean positive kick 261.0 → 49.9. | MEASURED |
| **F4** | ⚠ **`R17-DUAL-TRKICK-A` counts kicks, so it cannot see F3.** Kick *count* is 105 vs 109 of 178 — essentially unchanged — while magnitude fell 6×. The cell reports "no improvement" on the run's second-largest physical improvement. The criterion needs a magnitude term before Visit 8 judges the drive change by it. | CELL DEFECT, mine |
| **F5** | ⭐ **SS6.1a's prediction held**: the duty/current knee moved rung 6 → rung 8. The rung-6 collapse is a voltage limit, not a commutation defect. | PREDICTION CONFIRMED |
| **F6** | **The control reproduces Visit 7 within 0.02 on all eight ratio cells** across a day and a source revision (src_rev 22→23). The rig is stable; the A/B has a real control. | MEASURED |
| **F7** | **A small residual imbalance remains, and it has changed sign.** Candidate rungs 4–7: LEFT 0.95–1.02, RIGHT **0.88–0.93**. The candidate lead slightly *overshoots* on RIGHT. Consistent with the scan's per-motor minima differing (LEFT +13.4/−20.9, RIGHT +13.7/−22.3). Small — a few percent of a current that is already 20× smaller. | MEASURED, open for R18.3 |
| **F8** | **The low-speed regime is unchanged by the offsets.** `BM-LOW` hall-gap spread at 1e6: control 312–426, candidate 322–412, Visit 7 306–420 — indistinguishable across all three legs. **Correcting commutation phase does not address low speed**, which R18.3 must therefore still solve on its own terms. | MEASURED, negative result |
| **F9** | **`R18-DUAL-OFFSETS-A` emits `crit,?`.** `sSfCritOffsets` is `"APPLIED_EQ_COMPILED"` = **19 bytes** against `TOKMAX_CRIT = 18` (`src/test_bench_dual.spin2:740`), and `tokenField()` prints `?` for an over-length token by design (`src/isp_bench_log.spin2:121-131`). One byte over. The verdict and count are intact so the A/B is unaffected, but the load-bearing cell of this visit cannot name its own criterion in the log. | DEFECT, cause proven, mine |
| **F10** | **Hall integrity perfect in all three legs**: `missed_d` 0, `illegal_d` 0, `hw_skip` 0 summed across every ladder record. | MEASURED |
| **F11** | **The lag limiter never binds.** `win_lag` sum: control 0, candidate 0 (Visit 7: 10). Every observation in this visit is a duty-cap story, never a lag story. | MEASURED |
| **F13** | ⭐ **A start-transient surge of ~90–120 counts is present in all three legs and is untouched by the offsets**, while settled current fell from ~109 to ~32. Peak/settled goes 1.01 → 2.6–4.1. **The thump Stephen felt is not new; the quiet around it is.** Mechanism (hypothesis, source-grounded): the offset cancels between `initAngleFmHall` and `err_`, so every start begins at `err_ ≡ 0` against a servo setpoint of 60°, with `duty_` reset to `duty_min_`. See §7. | MEASURED + HYPOTHESIS |
| **F14** | **R18.3 must own the start transient.** It is now the drive's worst *relative* excursion, the commutation correction does nothing for it, and it fires at every spin-up from rest. It belongs with R18.3's low-speed/startup regime, where the halls stop informing. | OPEN, for «#3589» |
| **F15** | ⚠ **Instrument gap, mine: nothing covers a ramp start.** All 48 `BM-TS` traces trigger on stops (`seg,STOPMODE`); no cell, record or trace resolves the start. The run's most-repeated event (48 spin-ups in 209 s) was visible only to a person standing next to the rig. One added start trigger closes it. | DEFECT, mine |
| **F16** | ⛔ **The offset scan swept 126° of 360° electrical (~35%).** Bounded by `ABORT_I` at ±63° and by faulting below ~±3–13°. One minimum per direction inside that window, cross-confirmed and reproducible — but **the adopted pair is established as a true local minimum, not as the global one.** The wheel's 15 electrical cycles/rev mean any commutation feature repeats 15× around the circumference; those are one optimum seen 15 times, not 15 optima. See §8. | MEASURED LIMIT |
| **F17** | ⭐ **Correction to this report's own recommendation: «#3590» should stay open, rescoped.** It does not open on its original terms (the ratio *did* move to 1.0), but the full-electrical-cycle sweep is unmet and «#3590» is its only vehicle. Rescope: "sweep the full cycle once to establish the adopted basin is global." Not release-blocking. | RECOMMENDATION CHANGED |
| **F18** | **The principles doc's "broad minimum" prediction is contradicted, in our favour.** It predicted ±15° costs "only a few percent"; measured, LEFT/neg runs 167.1 → 13.1 mV over 43°→13°, a 12.7× change in 30°. Consistent with off-optimum current being largely non-torque-producing circulating current — the same reading that explains F2's 15–26× collapse. | MEASURED, contradicts authority |
| **F12** | **Evidence filed.** Both Visit 7b logs are now at `DOCs/analyses/bench/2026-09-21/`, and the Visit 7 baseline — which existed only in the runner's rotating gitignored `src/logs/_OLD/` — is now at `DOCs/analyses/bench/2026-09-20/`. This discharges the earlier study's F11. | DONE |

---

## §7 — The operator observation: a thump at every ramp start (candidate leg)

**Stephen, 2026-09-21, volunteered after the run:** *"In your second run, I was able to visually and
through touch observe that there is an interesting thump at every ramp start. It's not immediate;
it's just after the ramp starts, but it's every single ramp start for that second run."*

⛔ **The sheet should have asked for this and did not.** Its "who can observe" row asked only whether
either leg *sounds or feels different*, which is a comparison; it never asked what happens **at a
ramp start**. The STOPMODE segment performs 48 spin-ups from rest over 209 s — the single most
repeated event in the run — and no cell, record or trace covers the start transient. That is an
instrument gap, and it is mine.

### What the logs do carry, and it is decisive

The only from-rest starts that emit a transition record are the LIVE segment's, at
`incre,36_750_000` — the same speed the 48 STOPMODE spin-ups use:

| leg | motor | `tr_i_pk` (peak) | `tr_i_over` (peak − settled) | **implied settled** | **peak / settled** |
|---|---|---|---|---|---|
| VISIT 7 (43/317) | LEFT / RIGHT | 115 / 118 | 1 / 2 | 114 / 116 | **1.01 / 1.02** |
| CONTROL (43/317) | LEFT / RIGHT | 110 / 107 | 1 / −2 | 109 / 109 | **1.01 / 0.98** |
| CANDIDATE (14/338) | LEFT / RIGHT | 90 / 120 | **55 / 91** | **35 / 29** | **2.6 / 4.1** |

⭐ **The startup peak current is essentially unchanged across all three legs — 90 to 120 counts.
What collapsed is the settled current around it, from ~109 to ~32.**

**So the thump is not new. The silence around it is new.** On the control the motor drew ~109 counts
continuously, so a start surge to ~110 was not an event — there was nothing to feel it against. The
candidate leg drops the steady state 3.4×, and the same surge becomes a 2.6–4.1× excursion that is
plainly palpable. Stephen felt a transient that has been present at every start all along.

### Why it is offset-independent — from the source, and it cancels by construction

`initAngleFmHall` (`src/isp_bldc_motor.spin2:4570-4584`) seeds the field angle at every spin-up from
rest, reached from `.rampUp`'s `drv_incr == 0` path via `.checkstopfloaton` (`:4164-4166`, `:4538-4548`):

```
                alts    hall_, #hall_angles
                mov     angle_, 0-0
    if_c        add     angle_, offset_fwd_             ' adjust phase offset for hall sensor
    if_nc       add     angle_, offset_rev_
    _ret_       mov     prior_angle, angle_
```

The control loop then forms the error from the *same* table and the *same* offset (`:4458-4465`):

```
                alts    hall_, #hall_angles
                mov     err_, 0-0
    if_c        add     err_, offset_fwd_
    if_nc       add     err_, offset_rev_
                subr    err_, angle_                    ' difference from requested angle
```

**The offset appears on both sides and cancels: immediately after a start, `err_` is identically
zero, whatever the offset pair is.** But the duty servo's setpoint is not zero — it is
`sub tmpY, #256/6` (`:4477`), i.e. 42.67 counts of a 256-count turn = **60°**. So *every* start
begins 60° away from the servo's own target, with `duty_` reset to `duty_min_` (`:4546`), and the
servo must build that 60° of lead from scratch. None of that depends on the commutation offsets.

This also answers the *shape* Stephen described. It is **not immediate** because `duty_` starts at
`duty_min_` and the servo needs tens of passes (at ~1913 passes/s) to wind duty up against a rotor
that has not yet broken free; the surge lands once duty has wound up and before the rotor accelerates
away. And it is **every single start** because it is structural — every spin-up from rest runs the
same initialiser — rather than dependent on where the rotor happened to stop.

The original author knew a start jerk existed: `:4545-4546` carries the comments *"make sure angle
set correctly, so motor doesn't jerk when enters ctlMotor"* and *"reset duty, reduces jerk if not
fully aligned"*. Those are the existing mitigations. **What this run shows is that they leave a
residual surge of ~90–120 counts that the commutation correction does not touch.**

### Status, and the falsifier

⚠ **MECHANISM IS A SOURCE-GROUNDED HYPOTHESIS, NOT A PROVEN CAUSE.** The currents are measured; the
`err_ ≡ 0` cancellation is read directly from the driver; the link between them has no control yet.

- **Already-in-hand corroboration:** the mechanism predicts the startup peak is ~unchanged at *any*
  offset pair. Three legs across two pairs give 115/118, 110/107, 90/120 — consistent, 3 for 3.
- **The discriminating run, and it is cheap:** the `BM-TS` trace machinery already samples at 2 ms
  with 50 pre-trigger samples (~600 ms of window). It currently triggers on **stops only** — all 48
  traces are `seg,STOPMODE`. Pointing one trigger at a **start** resolves `duty`, `err`, `i` and the
  hall ticks through the first 600 ms and settles mechanism-versus-contrast outright. Unattended, no
  new tier, one added trigger.

### What it means for the release

- **F14 below is the consequence that matters:** R18.3 must own the start transient explicitly. The
  commutation correction is worth 15–26× in steady state and **zero** at the start, so the start is
  now the drive's worst relative excursion and is not addressed by anything R18.2 did.
- Nothing here argues against adopting 14/338. It makes an existing, unmeasured defect visible.

---

## §8 — "Why are there multiple low-current regions?" — and what this run did *not* establish

**Stephen, 2026-09-21:** *"What I saw when I was doing this all by hand was that the phasing appears
to have multiple low-current regions around the circumference of the wheel. How is the one you picked
the correct one, and why do multiple exist?"*

⚠ **Provenance, and it bounds how this is used.** Stephen, same day, when asked: *"i was working to
understand how to drive the motors and found competing offset references and was trying to understand
them so did some incomplete experiments and found multiples but never went further."* So the
observation is **informal and incomplete by his own account, and is not treated as evidence below.**
What it is — and it is the more valuable thing — is a well-founded doubt about a question no run has
asked. The answer that follows rests on the scan logs and the source, not on the recollection.

### Why multiple exist — the first reason is geometry, and it is not a choice

The library's own `hallTicInfoForMotor()` (`src/isp_bldc_motor.spin2:1464-1466`) gives the 6.5in hub
**15 electrical cycles per mechanical revolution** (30 poles), **90 hall ticks/rev**, **4° mechanical
per tick**. So:

> **One electrical cycle = 24° of wheel rotation. Everything commutation does repeats 15 times around
> the circumference.**

A low-current region observed while turning the wheel therefore appears **15 times per revolution,
once every 24°**. Those are not fifteen candidate optima — they are **one optimum, seen fifteen
times**. And there is nothing to pick among them: the offset is an *electrical* angle, a single number
in 0..359, applied identically inside every one of the 15 cycles. Picking "which one around the
circumference" is not a question the parameter can express.

### The second reason — and this one *is* a real pair

Within a single electrical cycle there are **two** minima, one per direction of travel: `offset_fwd`
for negative increments, `offset_rev` for positive. The principles document predicted they sit
**symmetric about the hall zero Z**, and the scan measured exactly that:

| | neg-incre minimum | pos-incre minimum | midpoint = hall zero |
|---|---|---|---|
| LEFT | **+13.4° ± 0.5** | **−20.9° ± 0.7** | **−3.8° ± 0.4** |
| RIGHT | **+13.7° ± 0.7** | **−22.3° ± 0.4** | **−4.3° ± 0.4** |

*(`DOCs/analyses/bench/2026-09-14/SCAN-RUN-7-EVALUATION.md` §2–§3.)* The shipped candidate Z = −4,
L = 18 → 14 / 338 sits on those fits.

### Why we believe this one is right — four independent confirmations

1. **The symmetry test passed.** The principles doc predicted the two per-direction minima would be
   symmetric about a common hall zero. On both motors they are, and the two midpoints agree within
   **0.5°**. A spurious or aliased minimum would not land symmetrically about a common Z.
2. **Two physically separate motors and boards agree** — 0.3° apart on the negative minimum, 1.4° on
   the positive.
3. **It reproduces.** The quarter-speed minima and cliff edges repeat within ~2° across scan runs 4–7.
4. **The running machine confirmed it (this visit).** At that pair the direction asymmetry went
   2.04 → 1.01 *and* absolute current fell 15–26×. Both were predictions of "this is the minimum",
   and both held.

### ⛔ The honest limit — we measured about a third of the circle

This is the part of the answer that matters, and it qualifies §2's verdict:

**The scan swept −63° to +63° electrical. That is 126° of 360° — about 35% of one electrical cycle.**
It is bounded at the outside by an over-current abort (`ABORT_I` at ±63°) and on the inside by the
motor faulting (below roughly ±3° to ±13°). LEFT, negative increment, net mV:

| swept | 63 | 53 | **43** | 33 | 28 | 23 | 18 | **13** | 8 | 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| net | ABORT_I | 392.8 | **167.1** | 67.2 | 40.5 | 23.7 | 14.6 | **13.1** | 15.1 | FAULT |

Inside that window there is exactly **one** minimum per direction, and the scan's "negative case" —
the check that current rises on *both* sides of the claimed floor — is reported **met** on three of
the four sweeps and **marginal** on RIGHT/negative. **The other ~234° of the electrical cycle was
never swept.** So what is established is that this pair is a true local minimum, deep, reproducible
and cross-confirmed — **not** that it is the only one or the global one.

Theory bounds it but does not close it: torque per amp goes roughly as the sine of the lead angle, so
one maximum per cycle per direction is expected, and the solution 180° away is the reverse-torque one,
excluded here because the wheel tracked its commanded direction at `rate/pred` ≈ 1.000 at every rung
in both legs. **That is an argument, not a measurement.**

⚠ **One prediction of the principles doc is contradicted by the data, in our favour.** It warned the
minimum would be *broad* — *"±15° from the optimum costs only a few percent."* The measured curve is
**steep**: LEFT/neg falls 167.1 → 13.1 mV between 43° and 13°, a 12.7× change over 30°. A basin that
deep is consistent with off-optimum current being dominated by **circulating current that produces no
torque** rather than by a modest loss of torque-per-amp — which is also the most natural reading of
this visit's 15–26× collapse.

### What could produce genuinely *extra* structure — and one of them is live

- **Unequal hall sectors.** The halls give 6 sectors of *nominally* 60°; real sensor placement makes
  them unequal, which would superimpose **6-fold structure inside each electrical cycle**. The
  principles doc names exactly this as what a residual imbalance would point to. **F7 of this visit
  left such a residual** (candidate RIGHT 0.88–0.93 at rungs 4–7), so this is not hypothetical.
- **Cogging / detent torque.** Magnetic detent between magnets and stator teeth is a property of the
  iron and exists with the drive *unpowered*. Turning the wheel by hand, it is strongly palpable and
  periodic around the circumference. It is not commutation at all, and it must not be read as
  evidence about the offsets.

### ⭐ Consequence: my recommendation to close «#3590» was wrong

I advised closing «#3590» as not-needed because the A/B confirmed the pair. That reasoning does not
survive this question. **The A/B answered "is this pair better?" — it did not answer "is this pair the
best?", and no run to date has swept the full electrical cycle.** «#3590»'s stated precondition (the
ratio failing to move toward 1.0) is still falsified, so it does not open *on its original terms* —
but the full-circle sweep is a real, unmet question, and closing the task would retire the only
vehicle for it.

**«#3590» is rescoped and stays open** (Stephen, 2026-09-21: *"You re-opened and newly spec'd #3590
should get us a formal answer"*): from *"redesign the scan because the offsets are wrong"* to
**"sweep the full electrical cycle and establish that the adopted basin is the global one."**

⭐ **And it is a keeper, not a one-off** — Stephen, same message: *"It's also (my guess) a tool we
should probably keep around when we need to adopt another motor (and also use to certify our doco
motor, too.)"*

⭐⭐ **The phasing, set by Stephen the same day, and it corrects an error in this report's first
rescope.** *"we could just build this as our standard instrument today and use it for this phase for
the 6.5, and use it for the doco when we get there. After having experience with it, we can
generalize it to a real tool and make that part of a later effort."*

This report's first rescope wrote into «#3590» that *"the motor under test is a parameter … and the
stop condition must hold for a motor whose fault behaviour is unknown."* **That was designing against
an imagined requirement.** The crux of generalising this instrument is exactly the stop condition, and
it is the one thing that cannot be derived today: the 6.5in's edge behaviour is measured (it droops
rather than faults), the Doco's is not observed at all. A general stop condition written now would be
invented — which is how this scan's stop condition failed silently the first time. The phasing gives
**two real motors before generalising, instead of one real and one imagined**, which is D7 (design
forward from measured capability) applied where this report had just violated it.

**Adopted, with one refinement:** build fit-for-6.5in, but keep the **seams** clean — the quantities
already known to vary by motor (motor type, hall-cycles/rev, sweep bounds, abort current, stop
thresholds) live in one named block rather than scattered. That costs nothing today, adds no guessed
decision, makes the Doco adaptation an edit of that block, and makes *what had to be edited* the
specification for the real tool. The parameterisation, the multi-motor stop condition and the user
documentation are **not** built here — they are **«#3592»**, out of this release, waiting on the Doco
run.

The consequences already on the books:

- **`ADDING_MOTOR.md` is the procedure this instrument serves.** That document walks a user through
  producing a new motor's offsets, and today it walks them through it by hand. A full-cycle sweep is
  the tool that step has always implied, so the sweep and the procedure are written to each other.
- **`MOTOR_CHOICE.md`'s per-motor table gains the offsets** under the 2026-09-17 ruling, and the
  sweep is what fills that column for any motor added later.
- **`ADDING_MOTOR.md` must not promise a generalised tool this release.** It describes the procedure
  as it actually is; the tool it has always implied arrives with «#3592».
- **The Doco certification use is OUT of this release** — Doco sits with «#3562» / PL-27, all ruled
  out of 6.0.0 (Stephen, 2026-09-17: *"no those three are not in"*). The **instrument** is built and
  used here for the 6.5in; **certifying the Doco motor with it is downstream work**, and this report
  does not pull it forward.

The stop condition remains the task's design work — the old fault-edge walk cannot fire now the lag
limiter droops instead of faulting — which is why «#3590» keeps its `task-design` lane even with the
generality removed.

---

## §9 — What the sheet asked that this run did not answer

- **The per-direction speed ceiling** was raised on the sheet and deliberately not built; it remains
  Stephen's to accept or decline, and Visit 8 remains its natural home. This run reinforces the case
  for deferring it: the ceiling moved two rungs out, so where it now sits is a different question
  from the one Visit 7 posed.
- **No observation was asked of Stephen**, and none is requested after the fact. The sheet named one
  optional observation — whether either leg sounds or feels different. If it was not made, nothing
  here depends on it.
