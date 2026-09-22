# Visit 8b — run sheet (the filled lead table, confirmed; the quarter, bracketed)

**Task:** «#3601». **Why this pass:** Visit 8 ([evaluation](2026-09-22/VISIT-8-EVALUATION.md)) found the
flat 18° lead over-leading under the new servo, and filled the table from the lead run. This pass
confirms the table and finishes the one speed that did not bracket.

---

## Check the banner before reading anything else

| Load | Every `BM-BANNER` / `BM-BUILD` must read |
|---|---|
| both | `src_rev,30` · `fmt,17` · `drv_rev,4` |
| `dual-a` | part `A`. Its `BM-RUNG` offsets now **change with speed** (the lead table); `R18-DUAL-OFFSETS-A` expects the table's pair at each rung, so it must still PASS |
| `dual-lead` | part `LEAD`; nine steps per speed, from −7° to 33° |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of the filled lead table (does it beat the flat 18° and pass 2 at every rung?), **plus one measurement**: the quarter's minimum below 3°. |
| **Hardware risk** | As Visit 8. The one new thing is `dual-lead`'s leads of −2° and −7° at the higher speeds, which may reach the torque wall and fault a wheel **on purpose**. It is recovered in-run; no step faulted at 3° even at full speed. Wheels up, no hands near the rig. Panic: physical battery disconnect. |
| **Who can observe** | Nobody needs to. **Two observations are worth having if you are near:** does a start still sound quiet, and **are the kicks at speed changes smaller again**, speeding up and slowing down? Observations, not verdicts. |
| **Runs that carry state** | None. `dual-lead` re-enables the lead schedule at the end of every lifetime. |
| **Run length** | **About 17 minutes (ESTIMATED):** `dual-a` MEASURED 12 min at Visit 8; `dual-lead` MEASURED 3.5 min for seven steps, so ~4.5 min for nine. |
| **Repeatability** | Both repeatable and idempotent. |
| **Variant matrix** | One source, two part builds of `test_bench_dual.spin2`, on the same rig as Visit 8 (Rev B, paired 6.5in hubs, 18.5 V, 270 MHz). Two logs. |

---

## The commands

```bash
tools/bench-run.sh dual-a      # 1: the filled table on the ladder, the START trace and TAKE
tools/bench-run.sh dual-lead   # 2: the lead run again, now down to -7 deg
```

`dual-d` is not re-run. Its timing cell passed at Visit 8, and its stall cannot be provoked on this rig
(PL-106), so a re-run would measure nothing new.

---

## What each load decides, and how each can fail

| Id | Judged by | Criterion | Fails if |
|---|---|---|---|
| **A-5 (re-judged)** | report, ladder rungs 3–8 against pass 2 and against Visit 8 | net current at or **below pass 2** at rungs 4–7, and **below Visit 8's flat-18°** figures at every rung from 3 to 7; rate judged at rungs ≥ 4 only (F-6) | the table is wrong, or the extra current was not the lead |
| **A-3 (re-read)** | report, rungs 1–2 | `err_pk` ≤ 76 and swing ≤ 400, as before | the low-speed residual is not the lead |
| **A-1 / A-2 (re-confirmed)** | report, START traces | unchanged: ≤ 0.10 and ≤ 1.8 | the table disturbed the start |
| **The table's quarter** | `BM-LEADMIN` at 36.75 × 10⁶ | the minimum is **bracketed**, not EDGE | the optimum is below −7°, or the torque wall hides it |
| **Speed-change kicks** | report, `BM-RUNGTR` UP / DOWN against Visit 8 | mean current overshoot on speed-ups falls from 45 toward the old 28 | the kick is not the lead |
