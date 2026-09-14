# Bench Pass 2a — scan run 7 (scan v4)

**Log:** `debug_260914-114703.log` (this folder, 1,412 lines, COMPLETE).
**Source:** `fa8819d`. Banner: `src_rev 9, fmt 9, cfg_id BENCH`, left base 32, right base 16,
voltage enum 6, defaults 43 / 317 (L21).
**Run:** 11:47:05 → `BS-END COMPLETE` 11:59:13 (L1411), 728 s, 106 points.
- Stephen ran it after hardening the supply connections.
- Run 6 (`debug_260914-113610.log`) went silent 36 s in; see
  [`VISIT-1-RESULTS.md`](VISIT-1-RESULTS.md) §8 and PL-43.
- Run 6's completed self-check corroborates run 7's below.

**Provenance tags:** **MEASURED** = a log line (`Lnnn` = this run's log, `r6:nnn` = run 6's).
**DERIVED** = a calculation or source reading (`src:nnn` = `src/test_bench_scan.spin2`).
**STEPHEN** = his words.

**Units and conventions:**
- Sense readings are mV at 150 mV/A.
- **Net** = a point's raw mean minus the `BS-ZERO` read immediately before it, in the same
  driver lifetime.
- A negative increment is served by `offset_fwd` (default +43); a positive increment by
  `offset_rev` (default 317, swept as −43).

---

## 1 · Foundations — MEASURED

- **Starts:** 9 per motor. Every one reads `cog_ok TRUE`, `REV_B`, offsets read back 43/317,
  `missed 0`, `illegal 0`, `result OK`. `dead_gap 70` on all 18 inits.
- **Offset read-backs:** 0 bad of 64 (left) and 60 (right) (L1372, L1393).
- **Hall integrity:** 0 across 62 and 58 start-and-point records (L1370, L1391).
- **No corrupted lines** in all 1,412. The corruption seen today in Tier 0 and char (PL-41) is
  absent from this run.

**Self-check — both motors PASS.** Net is against `ZERO_INIT`, the verdict basis.

| | ZERO_INIT | +¼ net | −¼ net | ratio | rate |
|---|---|---|---|---|---|
| LEFT | 8.0 (L191) | 84.3 (L200) | 168.0 (L209) | 1.992 (L210) | 98.1 / 98.1 |
| RIGHT | 0.8 (L858) | 92.5 (L867) | 171.6 (L876) | 1.855 (L877) | 98.1 / 98.1 |

- **Run 6 corroborates the left** (MEASURED): +¼ 83.7, −¼ 166.3, ratio 1.986 (r6:200-210).
- **Run 5 agrees within 2%.**

**The «#3529» calibration fix held.** Zero spread across starts, max − min, mV:

| | i | u | v | w | source |
|---|---|---|---|---|---|
| L, 5 back-to-back starts | 1.6 | 1.7 | 1.2 | 0.7 | L1376-1379 |
| L, all 8 driver lifetimes | 2.1 | 2.0 | 1.2 | 1.7 | L1388 |
| R, 5 back-to-back starts | 1.4 | 1.6 | 1.3 | 1.8 | L1397-1400 |
| R, all 8 driver lifetimes | 1.6 | 1.9 | 1.8 | 2.1 | L1409 |

- **Spread.** Run 5's spread reached 62 mV on current and 85 mV on a phase channel.
- **Level — the stronger evidence** (DERIVED). The right motor's zero read 71–76 mV in runs 3–5,
  and reads 0.2–1.8 mV in all 8 of run 7's lifetimes. The left's ~8 mV is steady across runs 3–7,
  a property of that board, not a per-start draw.

## 2 · The curves

Net mV. Repeats are shown as `a / b`.

### LEFT, quarter speed, negative increment

| swept | 63 | 53 | **43** | 33 | 28 | 23 | 18 | **13** | 8 | 3 | −7 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| net | ABORT_I | 392.8 | **167.1 / 165.5** | 67.2 / 66.7 | 40.5 | 23.7 / 23.8 | 14.6 | **13.1 / 13.0** | 15.1 / 14.5 | FAULT | FAULT |

- **Fit:** OK, **+13.4° ± 0.5**, rms 1.4 mV (L745). **Cliff:** 8 / 3 → edge 5.5°, margin 7.9°
  (L373).
- **Negative case: met** (DERIVED). The floor is 13.05 at 13°. Above it, 18° reads +1.55 and
  23° reads +10.7. Below it, 8° reads +1.75 on two repeats, against 0.6 mV scatter. The low-side
  rise rests on one offset, as in run 5.

### LEFT, quarter speed, positive increment

| swept | −63 | −53 | **−43** | −38 | −33 | −28 | **−23** | −18 | −13 | −11 | −8 | −3 | +7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| net | ABORT_I | 205.1 | **83.1 / 84.0 / 83.3** | 49.6 | 29.4 / 30.1 | 17.4 | **11.4 / 11.5** | 14.0 | 16.1 / 16.8 | FAULT | FAULT | FAULT | FAULT |

- **Fit:** OK, **−20.9° ± 0.7** (L747). **Cliff:** −13 / −11 → edge −12.0°, margin 8.9° (L565).
- **Negative case: met** (DERIVED). −28° reads +6.0 and −18° reads +2.55 above the 11.45 floor.

### RIGHT, quarter speed, positive increment

| swept | −63 | −53 | **−43** | −38 | −33 | −28 | **−23** | −18 | −13 | −3 |
|---|---|---|---|---|---|---|---|---|---|---|
| net | ABORT_I | 224.0 | **92.1 / 92.1 / 91.7** | 57.0 | 33.8 / 34.3 | 20.5 | **13.2 / 12.0** | 16.9 / 16.9 | FAULT | FAULT |

- **Fit:** OK, **−22.3° ± 0.4** (L1362). **Cliff:** −18 / −13 → edge −15.5°, margin 6.8°
  (L1032).
- **Negative case: met** (DERIVED). −28° reads +7.9 and −18° reads +4.3 above the floor.

### RIGHT, quarter speed, negative increment

| swept | 63 | 53 | **43** | 33 | 28 | 23 | **18** | 13 | 8 | 3 | −7 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| net | ABORT_I | 397.6 | **171.4 / 170.6** | 70.0 / 70.0 | 43.0 | 25.4 / 25.4 | **15.9** | 16.0 / 16.5 | 17.2 / 16.9 | FAULT | FAULT |

- **Fit:** OK, **+13.7° ± 0.7** (L1364). **Cliff:** 8 / 3 → edge 5.5°, margin 8.2° (L1196).
- **Negative case: marginal** (DERIVED). The floor is flat from 8° to 18°: 15.9–17.2 mV. Above it
  the rise is clear (23°: +9.5). Below it, 8° is only +0.8 above 13°, within repeat scatter. A local
  parabola through 13/18/23 gives +15.7°. Run 5 saw the same rise at 8°.

### Half speed — no minimum was demonstrated

| Leg | Points (net) | Lowest at | Fit (status) | Cliff | Negative case |
|---|---|---|---|---|---|
| L NEG | 43: 942.6/936.1 · 28: 219.7 · 23: 121.9 · 18: 62.6 · 13: 29.9 · **8: 18.0/18.2** · 3: FAULT | 8 (last clean) | 9.2, **EDGE**, pinned (L645-646) | 8 / 3 (L647) | **fails** — the low sits at the edge |
| L POS | −43: 460.5/465.3 · −36: 224.9 · −31: 122.0 · −26: 61.6 · −21: 29.0 · −16: 18.4 · **−11: 15.3** · −9, −6: FAULT | −11 (last clean) | −15.5, **POOR**, pinned (L741-742) | −11 / −9 (L743) | **fails** — −16 is above −11 |
| R POS | −43: 504.6/500.3 · −37: 273.0 · −32: 154.9 · −27: 81.2 · −22: 39.6 · **−17: 22.3/22.0** · −12: FAULT | −17 (last clean) | −17.6, **EDGE**, pinned (L1276-1277) | −17 / −12 (L1278) | **fails** |
| R NEG | 43: 923.1/923.6 · 29: 246.4 · 24: 139.7 · 19: 73.3 · 14: 37.0 · **9: 22.7/22.3** · 4: FAULT | 9 (last clean) | 9.9, **EDGE**, pinned (L1358-1359) | 9 / 4 (L1360) | **fails** |

- **In every half-speed leg the lowest current is at the last clean point before a fault**, and
  nothing between it and the fault was measured.
- **Local parabolas put the half-speed minima at about** +7.7 (L NEG), −11.4 (L POS), −15.9 (R POS)
  and +8.2 (R NEG) (DERIVED). These are extrapolations. They sit 2.4–4.7° from a fault.
- **L POS reports a shift that is not a measured minimum.** It prints a POOR, pinned fit with
  shift +5.4°, `shift_sig TRUE` (L748), yet its data are lowest at −11° with −16° higher.

## 3 · Agreement, hall zero, ratios

**Quarter speed — the motors agree** (the fine step is 5°):
- **Negative:** +13.4 vs +13.7, Δ 0.3° (L745, L1364).
- **Positive:** −20.9 vs −22.3, Δ 1.4° (L747, L1362).
- **Fault edges:** the negative edges match, both 5.5°. The positive edges differ: −12.0 left,
  −15.5 right. −13° ran clean on the left and faulted on the right.

**Hall electrical zero** (BS-PAIR midpoint): L −3.8 ± 0.4 (L749), R −4.3 ± 0.4 (L1366).

**Negative / positive current ratio:**

| | LEFT | RIGHT | source |
|---|---|---|---|
| ¼, defaults (self-check) | 1.992 | 1.855 | L210, L877 |
| ½, defaults (reference means) | 2.029 | 1.838 | L746, L748, L1363, L1365 (DERIVED) |
| ¼, fitted minima (BS-PAIR2) | 1.155, imbalance TRUE | 1.026, imbalance FALSE | L750, L1367 |
| ¼, measured floors | 13.05 / 11.45 = 1.14 | 16.25 / 12.6 = 1.29 | DERIVED |
| ½, at the ¼ minima | 1.03 | 0.93 | DERIVED |

- **The right motor's pair verdict uses fitted, not measured, minimum currents** (defect D3). By
  the measured floors its ratio is 1.29, not 1.026.
- **The ~2× asymmetry at the defaults collapses** to 0.93–1.29 near the minima.

**Across runs** (quarter speed unless marked):

| | Run 3 | Run 4 | Run 5 | Run 7 |
|---|---|---|---|---|
| L NEG minimum | not bracketed | ≈ +11.9 | +13.9 ± 0.4 | **+13.4 ± 0.5** |
| L POS minimum | −21.1 ± 0.7 | ≈ −22.9 | −20.9 ± 0.6 | **−20.9 ± 0.7** |
| R NEG minimum | — | — | ≈ +15.7 | **+13.7 ± 0.7** (local +15.7) |
| R POS minimum | — | — | ≈ −22.3 | **−22.3 ± 0.4** |
| L / R hall zero | — / — | −5.5 / — | −3.5 / ≈ −3.3 | **−3.8 / −4.3** |
| L NEG / L POS edge | — / −10.5 | 5.5 / −15.5 | 5.5 / −12.0 | **5.5 / −12.0** |
| R NEG / R POS edge | — | — | 5.5 / −15.5 | **5.5 / −15.5** |
| L ½ POS | POOR −15.4 | skipped | TOO_FEW | **POOR −15.5, low at −11** |
| R ZERO_INIT (mV) | 73.4 | ≈ 72 | 74.9 | **0.8** |

**The quarter-speed minima and edges reproduce within about 2° across runs 4–7, and so does the
half-speed failure mode.**

## 4 · Faults, current aborts, caps

- **15 faults, every one during acceleration.** Faulted points left the steady loop at
  696–922 ms; clean points reached speed at 921–922 ms (quarter speed) and 1,319–1,320 ms (half
  speed). All 15 recovered in session. Reset alone cleared a fault on both motors (L288, L913;
  R10-SCAN-RSTALONE).
- **4 current aborts (ABORT_I)**, all at ±63° at quarter speed. Each was followed by a restart whose
  start checks passed.
- **Run-level caps.** Time 728 of 1,800 s. Charge 54,198 of 432,000 mV·s. Faults 15 of 24.
  ABORT_I 4 of 6: each motor block uses two, so the abort cap has little headroom.
- **Ended by cog 0** (L1410), with no watchdog record. All 41 scan sign-off cells PASS
  (L1368-1410).

## 5 · Instrument defects in scan v4 — mine to fix (doctrine overlay P3)

Found by reading the emitters against this log (DERIVED unless marked).

1. **D1 — the half-speed cliff probe stops at the first clean probe, and R9-SCAN-HALFLEG cannot
   see that.**
   - `probeConfirmCliff()` probes the last good point ±5°, and probes ±2° only when the 5° probe
     faulted or was not measured (src:3050-3058). The window then closes at the clean probe
     (src:3004, src:2916-2925), and the fit ends EDGE (src:3258-3259).
   - The cell's criterion `CLIFF_PROBED` counts "a probe point measured after a probeable fault"
     (src:580-586, src:4716-4732). It never asks whether the minimum was resolved.
   - **The consequence:** run 5's defect recurs one step narrower while all four cells PASS
     (L1380-1381, L1401-1402). **This is a criterion the unfixed path also satisfies.** The
     quarter-speed `refineCliffEdge()` has the same gate (src:2769-2774).
2. **D2 — nothing applies the negative case, and `pinned` influences nothing.**
   - Half-speed legs are marked bracketed by assignment (src:2462).
   - `hasMinimum()` accepts POOR fits (src:4345-4351).
   - `fitPinnedNearLimit()` is read only by `emitFit` (src:4167), although its own comment says a
     pinned minimum "must never read as a free minimum" (src:2928-2930).
   - `emitResultHalf` reports a shift and `shift_sig` from any POOR fit (src:4404-4423), which is
     L748.
3. **D3 — `BS-RESULT` and `BS-PAIR2` use fitted minimum currents, not measured floors**
   (src:4368-4371, src:4490-4509).
   - The fits read 11.3, 9.8, 13.2 and 13.5 mV; the measured floors are 13.0, 11.4, 12.0 and
     15.9 mV.
   - The right motor's `imbalance FALSE` (L1367) rests on the fits.
4. **D4 — edge resolution is not reported.** The cliff edge is a midpoint (src:4236), resolved to
   ±1° or ±2.5°, and `margin_deg` inherits that unstated. The L ½ NEG EDGE verdict turned on 0.05°
   (9.2 vs 9.25; L646, src:3258).
5. **D5 — label defects.** `low_mV_x10` in `BS-WALK` / `BS-BRACKET` and `BS-LEG`'s `ref_start` /
   `ref_end` are raw means under neutral names (src:4138-4145, src:4310-4327). No verdict uses them.
6. **D6 — coverage only.** R9-SCAN-OWNZERO and R9-SCAN-PAIR2 would also pass on the unfixed path.
   Their PASS is not evidence of the «#3530» fixes.
7. **D7 — sign-off instances carry no slot identity.** The two R9-SCAN-HALFLEG lines per motor are
   byte-identical (L1380 = L1381), so the sheet reads "4 of 2".
8. **D8 — R8's falsifier is unverified under back-to-back starts.** The unfixed spreads behind its
   5 mV limit came from restarts after aborts. The decisive «#3529» evidence is the right zero's
   level falling from 72 to 1 mV, not the R8 PASS.

## 6 · Disposition — do not apply

| Criterion («#3522») | Verdict |
|---|---|
| Banner BENCH, left 32, right 16 | met (L21) |
| Self-check did not abort | met — PASS on both motors (L210, L877) |
| Both motors agree on each sign's minimum within the sweep resolution | **met** — Δ 0.3° negative, Δ 1.4° positive, against a 5° step |
| Negative case at each reported quarter-speed minimum | met on L NEG, L POS, R POS; **marginal on R NEG** |
| Half-speed confirmation holds | **not met** — 0 of 4 half-speed minima pass the negative case; every low sits at a fault-bounded edge (D1, D2) |

**DO NOT APPLY.** The motors agree, so there is no disagreement to raise.

**Candidate pair, carried forward — not a value to ship:**
- `offset_fwd` ≈ **14°** (negative increments; the scan's applied value is 13 on the left and 14
  on the right, L745/L1364, indistinguishable).
- `offset_rev` ≈ **338°** (positive increments, −22°; 339 on the left, 338 on the right,
  L747/L1362).

**What it would buy, at no load** (DERIVED): current at the candidate is 86–92% below the
defaults at quarter speed and 92–97% below at half speed. The left motor at −½ speed drops from
6.26 A to about 0.20 A.

**The margin, for Stephen:**
- At no load, the candidate sits about 6.5–8.5° from a fault edge at quarter speed. That is 4–5°
  from the last offset known to run clean on the tightest leg, R POS.
- The half-speed minima move toward the edges, to 2.4–4.7° from a fault by extrapolation.
- All 15 faults happened during acceleration, where load is transient; a loaded robot adds load.
- **What margin is enough is Stephen's decision.** Nothing forces it now: the rule is not met
  until the half-speed confirmation is measured.

**Next:** scan v5 in Batch 1b.
- It fixes D1–D3: probe toward the fault in 2° steps after a clean probe; do not count POOR or
  pinned fits as minima; apply the rise-on-both-sides test at half speed; judge pair ratios on
  measured floors.
- R9-SCAN-HALFLEG then fails when the lowest point sits at the window edge.
- It re-runs at Visit 2.
