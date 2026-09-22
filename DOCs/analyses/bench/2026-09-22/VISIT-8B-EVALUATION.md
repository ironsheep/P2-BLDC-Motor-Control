# Visit 8b — the filled lead table cuts cruise current by up to three quarters, and frees the top of the range

**Task:** «#3601». **Run sheet:** [`../VISIT-8B-RUNSHEET.md`](../VISIT-8B-RUNSHEET.md). **Before it:**
[`VISIT-8-EVALUATION.md`](VISIT-8-EVALUATION.md). **Procedure:** `DOCs/procedures/BENCH-RUN-PROCESSING.md`.

| Log | Load | Binary | Size | Rebuilt (UTC) | Source |
|---|---|---|---|---|---|
| `debug_260922-161317.log` | `dual-a` | `test_bench_dual.bin`, part A | 88,002 | 22:13:15 | `a1c4970` |
| `debug_260922-164207.log` | `dual-lead` | same, part LEAD | 88,002 | 22:42:06 | `a1c4970` |

**Outcome.** Both logs end `exit,COMPLETE … trap_code,0,unrecov,0`, with 0 faults and 0 aborts. `dual-a` ran 12 min,
and `dual-lead` ran 144 steps in 4.9 min.

**Banner check, verified first.** `src_rev,30,fmt,17`, `drv_rev,4`, parts `A` and `LEAD`, as the sheet requires.
`R18-DUAL-OFFSETS-A` is PASS under the lead schedule, so the offsets fix took.

---

## §1 · Headline

| Learning | The number that carries it |
|---|---|
| ⭐ **The filled lead table cuts cruise current sharply** | net current **22–74 % below the old driver** at rungs 3–8 (for example rung 7: 29–35 mV against 112–128), and 24–78 % below Visit 8's flat 18° |
| ⭐ **It frees the top of the speed range** | rungs 9–10 (147, 155 × 10⁶) run at duty **22,400–23,900**, no longer pinned at 24,264; duty is 5–13 % lower everywhere from rung 3 |
| The start surge stays gone | duty drop **0.01–0.02**, start peak **1.24–1.33×** settled |
| **The table is confirmed; no refinement is worth a bench pass** | all 16 minima bracketed, each table value inside its measured flat region (within a few %) |
| Speed-change kicks keep shrinking | peak current at speed changes **mean 124 → 84**; the TRKICK maximum is **183 / 182** (Visit 8 233 / 222, old 221 / 214) |
| ⚠ The lead tool compared steps the wheel did not follow | at an eighth, 3° ran at **91 %** of the commanded rate and −2° at **51 %**; their low current was the wheel slowing |

---

## §2 · Root cause

No run aborted.

---

## §3 · The measurements, against the sheet

### 3.1 Cells

All `dual-a` cells PASS except `R17-DUAL-TRKICK-A`: FAIL at `measured,183` (LEFT) and `182` (RIGHT) against
[0..50]. `R18-DUAL-TAKE-A` and `R18-DUAL-FOLAGREE-A` PASS (`take_ms,1`; 1,000 ‰ against 101 % and 100 %).
`R18-DUAL-LEAD-BRKT` PASS at `measured,8` of 8 on both motors.

### 3.2 A-1, A-2 — re-confirmed

```
tid 1  LEFT  -36750000  drop 0.01  i_ratio 1.31
tid 8  LEFT   36750000  drop 0.02  i_ratio 1.32
tid 27 RIGHT -36750000  drop 0.02  i_ratio 1.33
tid 34 RIGHT  36750000  drop 0.02  i_ratio 1.24
```

**PASS** (≤ 0.10, ≤ 1.8). The peak ratio rose slightly against Visit 8 (1.15–1.53). The settled current it is
divided by fell with the new table, so the ratio moves up while the peak itself fell.

### 3.3 A-5 — re-judged: PASS

Net current at rungs 3–8, against pass 2 (the old driver) and against Visit 8 (flat 18°), both motors and signs:

| Rung | vs old driver | vs Visit 8 | Duty vs old |
|---|---|---|---|
| 3 | −22 to −27 % | −24 to −31 % | −4.9 to −5.2 % |
| 4 | −40 to −45 % | −47 to −52 % | −6.1 to −6.6 % |
| 5 | −52 to −57 % | −59 to −63 % | −8.1 to −8.6 % |
| 6 | −62 to −67 % | −68 to −72 % | −9.9 to −10.6 % |
| 7 | −70 to −74 % | −74 to −78 % | −11.8 to −12.6 % |
| 8 | −65 to −70 % | −64 to −69 % | −11.2 to −12.0 % |

Speed tracks within **0.04–0.47 %** at rungs 4–8 (judged at rungs ≥ 4 per Visit 8's F-6). Rung 3 reads 0.19–0.75 %,
which is at the instrument's one-tick resolution.

### 3.4 A-3 — re-read

- **Duty swing at rungs 1–2: PASS**, 178–364 (≤ 400).
- **err_pk: FAIL** on 19 of 28 instances, 77–83 (≤ 76). Visit 8 read 76–86, so it is slightly better but still over.

### 3.5 The top of the range

```
LEFT   9  -147000000  duty 22383  duty_pk 22472  err -48  err_pk 73
LEFT  10  -155000000  duty 23603  duty_pk 23707  err -48  err_pk 73
LEFT  11  -165000000  duty 24243  duty_pk 24264  err -51  err_pk 76
```

At Visit 8 and before, rungs 9–11 all pinned at 24,245–24,264 and err drifted to −52…−60. Now only the probe rung
at 165 × 10⁶ saturates. **The speed ceiling the power table publishes (147 × 10⁶ at 18.5 V) is now conservative.**
That is the invalidation of PL-26 / PL-38 the build task predicted, now measured.

### 3.6 The lead run — with the steps the wheel did not follow set aside

`BM-LEADMIN`'s verdicts compared net current across every measured step. Some steps did not follow:

```
rid,4,...,incre,-18_375_000,result,OK,off_neg,359,off_pos,353,...,rate_x10,-448,pred_x10,-491   (3 deg: 91 %)
rid,5,...,incre,-18_375_000,result,OK,off_neg,354,off_pos,358,...,rate_x10,-249,pred_x10,-491   (-2 deg: 51 %)
rid,6,...,incre,-18_375_000,result,STEADY_TIMEOUT,off_neg,349,off_pos,3,...                     (-7 deg: never steady)
```

A slower wheel draws less current for that reason alone, so those points are not comparable (F-10). Counting
only steps within 2 % of the commanded rate:

| Speed | Visit 8 minima | Visit 8b minima | Table (rev 4) | Flat region |
|---|---|---|---|---|
| eighth | 23, 18, 23, 18 | 18, 18, 18, 13 | 20.5 | 13–23 within ~6 mV |
| quarter | 8, 3, 3, 3 | 8, 3, 3, −2 | 5 | −2 to 8 within ~15 % |
| half | 3, 8, 8, 8 | 3, 3, 3, 3 | 8 | 3 and 8 within 1–3 % |
| full | 8, 8, 8, 8 | 8, 8, 8, 8 | 8 | 13 costs 2× |

**Every table value sits inside its measured flat region.** A refinement would move current by a few percent at
most, which is not worth a bench pass. **The table is confirmed.**

### 3.7 Speed changes (`BM-RUNGTR`, against Visit 8)

| | UP: i_pk mean / max | UP: err_pk max | DOWN: i_pk mean / max | DOWN: err_pk max |
|---|---|---|---|---|
| Visit 8 | 125 / 341–375 | 86 | 116–121 / 273–291 | 84–88 |
| Visit 8b | **79–84 / 255–270** | **80–81** | **84 / 253–263** | 88–92 |

The absolute transition current fell by about a third in both directions. The angle overshoot fell on
speed-ups and held on slow-downs, which matches Stephen's "smaller, but still there" in both directions.

---

## §4 · What this means for the driver

### 4a · What it now DOES

- **Confirmed:** the lead table at DRIVER_REV 4, the core of R18.4's efficiency result, with no change needed.
- **Licensed now:** stating the new cruise current and the headroom at the top of the range in the release
  notes, **as measured wheels-up** («#3515»).
- **Not licensed yet:**
  - **Raising the published speed ceiling.** It needs a ladder to the fault edge, and first F-11 (the
    feedforward's scale is that same number).
  - Refining the table on these numbers. The flat regions say it would not pay.

### 4b · What it now KNOWS

The drive now places its field by speed from a measured table. The halls are used for more than commutation
steps, and the drive acts on its own shortfall. Back-EMF is deferred by ruling.

---

## §5 · What this changes about the next run

- **Nothing more is owed on the lead table.** The next loads belong to the loaded floor run («#3591» at «#3576»),
  where the lead's benefit under load is judged.
- **A ceiling ladder** (to the fault edge, both directions) becomes worth running once F-11 is fixed, so it
  measures the new ceiling rather than a feedforward that moves with it.

---

## §6 · Findings register

| Id | Finding | Disposition |
|---|---|---|
| F-10 | The lead tool's minimum counts steps the wheel did not follow | ⛔ **FIX** — the harness excludes steps below 98 % of the commanded rate (SRC_REV 31) |
| F-11 | `ff_ceiling` is the power table's ceiling increment: raising the ceiling would silently weaken the feedforward | ⛔ **Punch list — PL-107** |
| F-12 | The published speed ceiling is now conservative (rungs 9–10 unsaturated) | **Punch list — PL-107**, with F-11; Stephen's limits study (2026-09-22) owns both |
| F-13 | The table is confirmed; «#3601»'s criterion holds (current below 18° at every rung) | **Closed** |
| F-7 | A-3 err_pk 77–83 at rungs 1–2 | **Watch** — the floor run re-reads it loaded |
| F-8 | TRKICK 183 / 182, improved but over 50 | **Watch** — PL-87 |
| F-14 | At full speed, the saturated plateau (leads ≥ 13°) reads 103–106 mV against 57–60 at Visit 8 | **Watch** — unexplained; bus voltage is unmeasured (H-8) |

---

## §7 · What is NOT established

- Anything loaded.
- The protective stop (PL-106).
- The path limiter engaging.
- The new speed ceiling. Rungs 9–10 are unsaturated, but no ladder has gone to the fault edge.
- F-14's cause.

---

## §8 · FRONTS, after

```
FRONTS  (after this run)
  completion   driver last changed 2 commits ago (DRIVER_REV 4); the R18.4 drive change is certified wheels-up
  information  0 loads ready and unrun -- the loaded floor run waits on «#3591» / «#3585»
  robustness   sensors the DRIVER acts on: halls y  current y  back-EMF n (deferred)  follow y
```

- **Completion: advanced.** The lead table is confirmed and the drive change certified, wheels-up.
- **Information: advanced.** The lead curves and the freed headroom are measured.
- **Robustness: unchanged this pass.** It certified what was built and integrated nothing new.
