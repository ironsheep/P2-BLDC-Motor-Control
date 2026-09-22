# Visit 8 — the start surge is GONE; the flat lead now over-leads, and the lead run says by how much

**Task:** «#3584» (Visit 8). **Run sheet:** [`../VISIT-8-RUNSHEET.md`](../VISIT-8-RUNSHEET.md).
**Design:** [`../../../plans/DRIVE-INTEGRATION-DESIGN.md`](../../../plans/DRIVE-INTEGRATION-DESIGN.md) §5.5.
**Procedure:** `DOCs/procedures/BENCH-RUN-PROCESSING.md`.

| Log | Load | Binary | Size | Rebuilt (UTC) | Source |
|---|---|---|---|---|---|
| `debug_260922-150505.log` | `dual-a` | `test_bench_dual.bin`, part A | 87,794 | 21:05:04 | `068bba1` |
| `debug_260922-151943.log` | `dual-d` | same, part D | 87,794 | 21:19:42 | `068bba1` |
| `debug_260922-152123.log` | `dual-lead` | same, part LEAD | 87,794 | 21:21:22 | `068bba1` |

**Outcome.** All three logs end `BM-END … exit,COMPLETE … trap_code,0,unrecov,0`. `dual-a` ran 12 min with 0 faults
and 0 aborts. `dual-d` ran 73 s: its whole plan, which is shorter than its estimates. `dual-lead` ran 3.5 min:
112 measured steps, 0 faults.

**Banner check, verified first.** Every `BM-BANNER` reads `src_rev,28,fmt,16`, part `A` / `D` / `LEAD`, and
every `BM-BUILD` reads `drv_rev,3`, as the sheet requires. `R18-DUAL-OFFSETS-A` is PASS (178 rungs, all
`off_neg,14 off_pos,338`), and the `dual-lead` steps applied Z ± L exactly: 18 → 14/338, 13 → 9/343,
8 → 4/348, 3 → 359/353.

---

## §1 · Headline

| Learning | The number that carries it |
|---|---|
| **The start surge is gone**, as the desk model predicted | largest duty drop during acceleration **0.01–0.03** (old driver 0.34–0.53; model 0.01–0.04) |
| **The start current peak fell** | peak ÷ settled **1.15–1.53** (old 1.94–3.04; model 1.13–1.80) |
| **Low-speed hunting fell by 2–4×, but not to the model's figure** | duty swing at rungs 1–2 **190–399** (old 800–1,650; model 40–153); err_pk 76–86 (old 75–89) |
| **The servo holds a point** | mean err **47–48** at every rung 1–8 |
| **A slower command is now taken while ramping (PL-104)** | the field fell **within 1 ms** of the command, on both wheels |
| ⛔ **At the flat 18° lead the new drive draws MORE current at cruise** | net current **+12–18 %** at rungs 4–7 vs pass 2, duty +1.0–1.6 % |
| ⭐ **…because the lowest-current lead has moved under the new servo** | minimum at **18–23°** at an eighth, **3–8°** at the quarter, **8°** at half and full |
| ⭐ **At the right lead, the new drive beats the old one** | at half speed, **17.7–19.5 mV** at 8° against 42.5–47.7 mV at 18° (2.3×); the old driver drew ~38 mV there (pass 2, interpolated between rungs 4 and 5) |
| The steering front cog has room | worst pass **847 µs** of 1,000, 0 late; stack 135 of 256 |
| ⚠ The blocked-motor protective stop has **never** been provoked on this rig | `R16-DUAL-BLOCKED-D` NOMEAS here and in every earlier `dual-d` |

---

## §2 · Root cause

No run aborted.

---

## §3 · The measurements, against the sheet

### 3.1 A-1, A-2 — the START trace (`start_metrics.py`, the same code on both drivers)

```
NEW (drv_rev 3)                              SHIPPED pass 1 / pass 2
tid 1  LEFT  -36750000  drop 0.02  i_ratio 1.16   0.42 / 0.38   2.57 / 2.03
tid 8  LEFT   36750000  drop 0.02  i_ratio 1.15   0.53 / 0.38   2.62 / 1.94
tid 27 RIGHT -36750000  drop 0.03  i_ratio 1.53   0.42 / 0.34   3.04 / 2.10
tid 34 RIGHT  36750000  drop 0.01  i_ratio 1.36   0.43 / 0.38   2.03 / 2.39
```

**A-1 PASS** (≤ 0.10), **A-2 PASS** (≤ 1.8), on all four starts. The mechanism the design named (§5.2) is the
one the fix removed: the swing amplitude collapsed, and it was amplitude the sheet judged, not timing.

### 3.2 A-3, A-4, A-5 — the ladder (`BM-RUNG2`, against pass 2 `debug_260922-122752.log`)

- **A-3, duty swing: PASS.** `duty_pk − duty` at rungs 1–2 is 190–399 across all 28 instances, against ≤ 400.
  RIGHT sits near the limit (345–399).
- **A-3, err_pk: FAIL.** 76–86 against ≤ 76. For example, RIGHT NEG rung 1 reads `err_pk,86`; LEFT POS rung 1
  reads 80–82. Some residual swing survives at the lowest rungs.
- **A-4: PASS.** Mean err reads −47 or −48 at every rung from 1 to 8, both motors, both signs.
- **A-5: FAIL.** Duty is within +1.6 %, but net current is outside ±5 % at rungs 4–7:

  | Rung | LEFT NEG | LEFT POS | RIGHT NEG | RIGHT POS |
  |---|---|---|---|---|
  | 3 | +6.8 % | −2.8 % | +4.2 % | +8.8 % |
  | 4 | +11.7 % | +13.4 % | +13.8 % | +16.5 % |
  | 5 | +17.7 % | +15.0 % | +16.4 % | +17.8 % |
  | 6 | +18.2 % | +16.9 % | +18.0 % | +17.9 % |
  | 7 | +16.8 % | +16.9 % | +16.8 % | +17.8 % |
  | 8 (duty pinned) | −4.0 % | −5.1 % | −3.9 % | −3.9 % |

  The sheet's rate criterion (within 0.5 % of `pred_x10`) reads 0.75–0.94 % at rung 3. **That criterion is
  below the instrument's resolution there**: one tick in 107 per second is 0.93 %. It is a sheet defect (F-6),
  not a driver result. Rungs 4–8 read 0.12–0.47 % and pass.

### 3.3 A-6, A-8 following — the TAKE segment (`BM-TAKE`)

```
BM-TAKE,...,motor,LEFT,drv_before,36_774_702,state,2,take_ran,TRUE,fell,TRUE,take_ms,1,permille,1_000,follow_pct,100
BM-TAKE,...,motor,RIGHT,drv_before,36_774_702,state,2,take_ran,TRUE,fell,TRUE,take_ms,1,permille,1_000,follow_pct,100
```

- **A-6 PASS**, both wheels. The eighth was commanded at `drv_incr` 36.77 × 10⁶ in `SPIN_UP` (state 2), and the
  field fell within 1 ms. The shipped driver would have discarded that command.
- **A-8 following PASS**, both wheels: 1,000 ‰ against 100 %, a difference of 0. It is a PASS on the case where
  both readings sit at their ceiling. The case that would show a disagreement is the not-following one (F-4).

### 3.4 A-7, A-8 not-following, A-10 — part D

```
SIGNOFF ... R16-DUAL-BLOCKED-D ... measured,NA ... verdict,NOMEAS      (BM-DSTEP ... why,NOT_BLOCKED)
SIGNOFF ... R18-DUAL-HOLDSET-D,motor,LEFT  ... verdict,PASS
SIGNOFF ... R18-DUAL-HOLDSET-D,motor,RIGHT ... n,0,verdict,NOMEAS
SIGNOFF ... R18-DUAL-NOTFOL-D,motor,LEFT   ... measured,FALSE ... verdict,FAIL
SIGNOFF ... R18-DUAL-NOTFOL-D,motor,RIGHT  ... n,0,verdict,NOMEAS
BM-FRONTST,...,motor,BOTH,passes,33_701,late,0,max_ticks,228_808,max_us,847,...,stack_hi,135,stack_of,256
BM-FRONTST,...,motor,LEFT,passes,17_818,late,0,max_ticks,141_040,max_us,522,...,stack_hi,115,stack_of,192
```

- **The 1 A stall is not a stall on this rig.** `R16-DUAL-BLOCKED-D` is NOMEAS (`why,NOT_BLOCKED`), as it was
  in every earlier part-D log (2026-09-17 twice, 2026-09-19): at a 1 A limit a lifted wheel keeps turning. The
  sheet claimed this cell would certify DRIVER_REV 3's protective-stop fix. **It cannot fail on this rig, so
  it certifies nothing** (F-3).
- **A-7: PASS on LEFT**, which read SHORT during the run and whose field then settled to ≤ 10 % of the command.
  **NOMEAS on RIGHT**, which never read SHORT at a 50 ms poll.
- **A-8 not-following: LEFT FAIL is an instrument defect, not a driver result.** The cell judged the last
  poll before the step's 4 s bound. The wheel was not stalled, and SHORT had only been seen at some earlier
  poll, so it judged a following wheel against a not-following criterion. It also emits none of the
  readings it judged (F-4).
- **A-10 PASS.** Worst steering pass 847 µs against ≤ 950, `late` 0. The stack high-water marks are 135 / 256
  (steering) and 115 / 192 (single wheel), the latter re-measured after the raise from 128.

Every other part-D cell PASSes. DERATE is NOMEAS as before (PL-80's rig condition).

### 3.5 The lead run — `BM-LEADMIN`

| Speed | LEFT NEG | LEFT POS | RIGHT NEG | RIGHT POS |
|---|---|---|---|---|
| eighth (18.4 × 10⁶) | **23** (5.8 vs 6.0 at 18) | **18** | **23** (4.4 vs 6.2) | **18** |
| quarter (36.75 × 10⁶) | **8** (10.4 vs 11.7) | 3 EDGE (9.1 vs 11.1) | 3 EDGE (8.9 vs 11.5) | 3 EDGE (9.0 vs 12.2) |
| half (73.5 × 10⁶) | 3 EDGE (18.9 vs 43.6) | **8** (17.7 vs 42.5) | **8** (19.4 vs 43.3) | **8** (19.5 vs 47.7) |
| full (147 × 10⁶) | **8** (39.6 vs 58.6) | **8** (39.1 vs 56.9) | **8** (44.0 vs 58.9) | 3 EDGE (45.7 vs 59.0) |

Values are the lead of least net current in degrees, followed by (net mV there vs net mV at 18°). EDGE means
the minimum is at the lowest step (3°), so the true minimum may be lower.

- **`R18-DUAL-LEAD-BRKT` PASS** on both motors (6 and 5 of 8 bracketed, ≥ 4).
- **`R18-DUAL-LEAD-KNOWN`:** LEFT PASS at 8, the band's lower edge. RIGHT NOMEAS: both its quarter minima are
  EDGE. **The cell's premise is refuted, not the drive (F-5).** The known 15.8° was measured under the OLD
  servo, and the new servo moves the optimum by more than the band allowed.
- **No step faulted**, including 3° at full speed. The torque wall the offset scan hit is not reached here.

### 3.6 Operator observation, and what the logs say about it

**STEPHEN, 2026-09-22:** *"many of the clicks are gone, but some of the 'kicks' in both increasing and decreasing
speed are still there. They're just smaller than they used to be."* The sheet asked him to watch starts only; the
speed-change kicks are an observation nobody asked for, so they are a finding to chase in the logs, never a
verdict (procedure, *Operator observations*). The next sheet names speed changes as a thing to watch.

The ladder's `BM-RUNGTR`, 84 speed changes per motor, old (pass 2) against new:

| | UP: err_pk mean / max | UP: i_over mean | DOWN: err_pk mean / max | DOWN: i_over mean |
|---|---|---|---|---|
| old | 73.5 / 92–93 | 28 | 76.5 / 88–89 | 34–38 |
| new | **70 / 86** | **45** | 76 / 84–88 | 34–38 |

- **The kicks are smaller in angle,** most clearly on speed-ups. That is consistent with what he felt.
- **The cell's maximum comes from the two probe rungs above the ceiling** (155 ↔ 165 × 10⁶, i_over 193–233),
  where duty is pinned on both drivers and the drive has no voltage left to absorb a change. That is why
  `R17-DUAL-TRKICK-A` barely moved while typical transitions did.
- **Current overshoot on speed-ups rose (28 → 45 mean),** consistent with the flat lead over-leading at cruise (F-2).
  The filled table is expected to bring it down, and the next `dual-a` re-reads it (F-8).

---

## §4 · What this means for the driver

### 4a · What it now DOES

- **Certified, and kept:** D-1 and D-2 (the surge and the start current, A-1 and A-2); D-4 (commands taken in every
  state, A-6, PL-104); the servo's point (A-4). **The shipped A/B, measured:** the desk model's predictions
  for A-1 and A-2 landed inside their predicted ranges.
- ⭐ **Licensed now: fill the lead table («#3601»).** The new servo moved the optimum lead well below 18° at the
  quarter and above, and it moved it by 5° at the eighth, as the design predicted (28 → ~23). Proposed
  provisional table: eighth **20°**, quarter **5°**, half **8°**, full **8°**. That is the measured minima,
  with the quarter at the midpoint of its bracketed 8 and its EDGE 3s. It is expected to turn A-5's +17 %
  into a reduction at every speed above the eighth.
- **Not licensed:**
  - Any change to `SERVO_SETPOINT`. The lead moves, never the setpoint (the same-knob rule, §3.3).
  - Treating the quarter's minimum as known below 3°. Three of four are EDGE, so the next run must step lower.
  - Any claim about the protective stop (F-3).
  - Any claim that the transition kick is fixed. `R17-DUAL-TRKICK-A` is still FAIL at 233 / 222 mV (old 221 / 214).
    The drive change did not touch it.

### 4b · What it now KNOWS

- **The drive now acts on its own shortfall** (D-5, certified on LEFT by A-7) **and knows its lead should change
  with speed**. The table is measured, but not yet filled.
- **Not advanced:** back-EMF, which is deferred by ruling («#3602»).

---

## §5 · What this changes about the next run (draft loads for the next sheet)

1. **`dual-a` on the filled table:** A-5 re-judged (expect net current at or below pass 2 at rungs 4–7), A-3
   re-read (the lead change may move the low-speed swing), and A-1 and A-2 confirmed unchanged.
2. **`dual-lead` with its steps extended below 3°** (−2° and −7°) at the quarter and above, so they bracket.
   The torque wall was not reached at 3°, even at full speed.
3. **`dual-d` with F-4's fix.** Its A-8 not-following limb still has no stall to judge until F-3 is resolved,
   so the part-D pass certifies the timing (A-10) and the not-following limb stays NOMEAS by construction.

---

## §6 · Findings register

| Id | Finding | Disposition |
|---|---|---|
| **F-1** | Start surge and start current certified gone (A-1, A-2) | **Closed** |
| **F-2** | The optimum lead moved under the new servo; 18° over-leads at the quarter and above, and that is A-5's +12–18 % | ⛔ **FIX** — «#3601» fills the table |
| **F-3** | The blocked-motor protective stop has never been provoked on this rig; DRIVER_REV 3's fix is uncertified | ⛔ **Punch list — PL-106** |
| **F-4** | A-8's not-following cell judges any poll after SHORT was ever seen, and emits no readings | ⛔ **FIX** — harness: judge only when SHORT at that poll; emit BM-HOLD |
| **F-5** | `R18-DUAL-LEAD-KNOWN` assumed the old servo's 15.8°; the premise is refuted by this run | ⛔ **FIX** — retire the cell; the table itself is now the known answer |
| **F-6** | A-5's 0.5 % rate criterion is below one hall tick at rung 3 (0.93 %) | **Closed** — recorded here; judge rate at rungs ≥ 4 |
| **F-7** | A-3 err_pk 76–86 at rungs 1–2; the duty swing passes | **Watch** — re-read on the filled table |
| **F-8** | `R17-DUAL-TRKICK-A` still FAIL (233 / 222) | **Watch** — PL-87 carries it; unchanged by R18.4 |
| **F-9** | The quarter's minimum is EDGE at 3° on 3 of 4 | ⛔ **FIX** — `dual-lead` steps extend to −7° |

---

## §7 · What is NOT established

- **The protective stop under DRIVER_REV 3.** It is untestable on a lifted wheel (F-3).
- **A-7 on RIGHT**, and **A-8's not-following case** on either wheel.
- **The path limiter (D-6) ever engaging.** No wheel was short long enough, and no record shows the scale below 1,000.
- **The quarter's true optimum below 3°.**
- **Anything loaded.**
- **Whether the filled table delivers the predicted current reduction.** It is inferred from the lead run's own
  measurements, and the next `dual-a` judges it.

---

## §8 · Questions left open

| Question | What would settle it | Owner |
|---|---|---|
| Where is the quarter's minimum below 3°? | `dual-lead` extended to −7° | «#3601» |
| Does the filled table beat pass 2 at every rung? | `dual-a` on the filled table | «#3601» |
| How can a lifted rig provoke a blocked motor? | a stall built by construction, not a 1 A limit | PL-106 |
| What leaves the residual err_pk at rungs 1–2? | a re-read on the filled table first | F-7 |

---

## §9 · FRONTS, after

```
FRONTS  (after this run)
  completion   driver last changed 0 commits ago (DRIVER_REV 3 at 068bba1); the lead table is next
  information  0 loads ready and unrun -- the next dual-a and extended dual-lead wait on «#3601»
  robustness   sensors the DRIVER acts on: halls y  current y  back-EMF n  follow y (D-5/D-6: shortfall from lag_held)
```

- **Completion: advanced.** The core drive change is certified on the start and command handling, and the table
  fill is licensed.
- **Information: advanced.** The lead against speed under the new servo is measured.
- **Robustness: advanced in part.** The drive acts on its own shortfall (certified on one wheel). Back-EMF is
  deferred by ruling.
