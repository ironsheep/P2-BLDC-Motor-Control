# Scan run with self-locating rungs — 2026-09-21 19:26, ABORTED

**Log:** `debug_260921-192618.log` (this folder), 942 lines. `test_bench_scan.bin`, 53,858 bytes,
`src_rev 17`. Source `8ade2cb` — the commit that made every rung walk and locate its own minimum.

**Outcome:** `BS-END exit,ABORTED, reason,ABS_CURRENT, elapsed_s,401, points,68, faults,0,
aborts_i,4, left_done,FALSE, right_done,FALSE`.

**The run died on its 68th point.** The LEFT motor's half-speed leg tripped the absolute current
abort, which is **run-scope**. The RIGHT motor never ran at all, and no half-speed minimum was
obtained — the third point on the speed law, which is the reason this run existed, was not taken.

**Provenance:** **MEASURED** = a log line. **DERIVED** = arithmetic on measured values.
**PRIOR** = the 2026-09-21 17:47 shakedown (`SHAKEDOWN-EVALUATION.md`) or scan run 7 (`../2026-09-14/`).

---

## 1 · Why the run died — root cause, and it is one line of arithmetic

MEASURED, the two points that matter:

| seq | rung | swept | result | `i_mean_mV_x10` | `follow_pct` | `span_duty_max` |
|---|---|---|---|---|---|---|
| 67 | HALF NEG `REF_START` | 43 | OK | **9,529** | 82 | 18,953 |
| 68 | HALF NEG `COARSE` | **53** | `WINDOW_TIMEOUT` | — | **44** | 21,590 |

`BS-ABORT, scope,RUN, reason,ABS_CURRENT, value,1_583`.

**DERIVED — the guards are in the wrong order.** The per-point relative abort is
`pointLimitMv = leg reference × POINT_ABORT_X100/100`, i.e. **2.5× the leg's own reference current**:

```
leg reference at HALF (seq 67)   =   952.9 mV
point-scope abort  = 2.5 x 952.9 = 2_382 mV     <-- survivable, ends ONE point
absolute abort     = ABS_ABORT_MV = 1_500 mV    <-- fatal, ends the RUN
```

⛔ **The graduated guard sits 59 % ABOVE the fatal one.** At half speed the point-scope abort can
never fire first, so the first genuinely high-current point takes the whole run with it. This is
structural, not bad luck: any rung whose reference exceeds `1_500 / 2.5 = 600 mV` has its relative
guard disarmed, and the half-speed reference is 953 mV.

**Why it did not bite before.** At the LOW rung the reference is small enough that 2.5× stays under
1,500 — the PRIOR shakedown took **four point-scope `ABORT_I`s and survived all four**. The guard has
only ever been exercised where it happened to be in the right order.

**Why swept 53 in particular.** `walkSide()` walks outward from `defSwept` in both directions. The UP
side goes *away* from where the half-speed optimum lies (§3 says it is at low swept values), so the
very first UP step lands ~47° off optimum at double the speed, in a basin the same run measures as
steep. It was the most dangerous point in the whole run and the walk took it first.

⭐ **The rebuild earned its keep even in the failure.** seq 68 records `follow_pct,44` with
`span_duty_max,21_590` — the drive had collapsed to 44 % of commanded while demanding maximum duty.
That is the droop signature, captured *at the point that killed the run*. Run 7 would have recorded
`rate_x10,NA` here and the failure would have been a bare token.

---

## 2 · What self-locating the rungs did — it worked, and it revealed a bias

MEASURED, LEFT motor, quarter rung, the same leg measured two ways:

| | centre used | arc reached | `neg_min` | `pos_min` | **L** |
|---|---|---|---|---|---|
| PRIOR shakedown — centre **inherited** from the walk | 25 | `10…40` = 33° | +15.3° | −23.3° | **19.3°** |
| this run — rung **walks and locates its own** | 13 | `−7…53` = **60°** | +11.9° | −19.8° | **15.85°** |

Two things follow.

**The arcs nearly doubled** (33° → 60° and 30° → 50°), because a rung walking for itself is no longer
confined to a ±15° window centred on somebody else's answer.

⚠ **And the answer moved by 3.5°.** The inherited centre was biasing the fit: the confirm points sat
where the *walking* rung's minimum was, and the quadratic came out pulled toward that centre.
**So the PRIOR shakedown's quarter-speed L values are biased high**, and any number derived from them
carries the bias.

**Cross-checking against self-located quarter measurements only** (run 7 walked *at* quarter, so its
values were self-located):

| source | rung walked itself? | LEFT L | RIGHT L |
|---|---|---|---|
| run 7 (PRIOR) | yes | 17.2° | 18.0° |
| shakedown (PRIOR) | **no — inherited** | 19.3° | 18.95° |
| this run | yes | **15.85°** | *never ran* |

Self-located quarter values: **17.2, 18.0, 15.85** — spread ~2°. The inherited values sit at the top
of and above that spread. The bias is real but modest, roughly **2–3°**.

---

## 3 · The speed law, with the bias removed

DERIVED from self-located measurements only. `Z` = (neg+pos)/2, `L` = (neg−pos)/2.

| rung | motor | run | **Z** | **L** |
|---|---|---|---|---|
| **eighth** | LEFT | this run | **−3.15°** | **27.95°** |
| **eighth** | RIGHT | shakedown | −3.4° | 28.5° |
| **quarter** | LEFT | this run | **−3.95°** | **15.85°** |
| **quarter** | LEFT | run 7 | −3.8° | 17.2° |
| **quarter** | RIGHT | run 7 | −4.3° | 18.0° |
| **half** | — | — | *never obtained, in any run* | |

### What is now solid

- **`L` at an eighth is 28°**, from two motors on two different days (27.95 and 28.5). Reproducible.
- **`L` at a quarter is 16–18°**, from three self-located measurements.
- **`L` therefore moves by about 10–12° per halving of speed.** Larger than the 9.55° first reported,
  because that comparison used a biased quarter value.
- **`Z` is stable but not to 0.15°.** Across five measurements it spans **−3.15° to −4.3°**, so the
  honest figure is **≈ −3.7° ± 0.6°**. The earlier "0.15°" was one motor's coincidence, not the
  population. ⚠ *This corrects the `SHAKEDOWN-EVALUATION.md` §4 claim.*

### What is still missing, and it is the same thing as last time

**No half-speed point.** Two rungs is a slope, not a law. The half rung has now failed to yield a
minimum in three consecutive attempts, for three different reasons: run 7 (pinned against a fault
edge), the shakedown (confirm span centred in the wrong place), and this run (the walk killed the run
before it measured anything).

---

## 4 · Other findings

| # | Finding | Evidence |
|---|---|---|
| **R-1** | `BS-WALK` and `BS-BRACKET` label every walk `speed,LOW`, including the quarter walks. | MEASURED — all ten `BS-WALK` rows read `speed,LOW` though four are quarter-rung walks. Introduced by me: the field was hardcoded to `speedToken(SPEED_WALK)` when only one rung walked. |
| **R-2** | The old driver's faults have become droops, as `«#3595»` assumed. Run 7's LEFT quarter leg FAULTED at swept +7, −3, −7. This run's LEFT quarter leg reached **−7 cleanly** and stopped on `RISE`. | MEASURED — `BS-ARC … QTR,NEG, arc_lo_deg,−7, bound_lo,RISE`. The lag limiter (task 3558) is why. |
| **R-3** | At half speed, at the *legacy* offset (swept 43), the drive already follows at only **82 %** of commanded with `span_duty_mean 15_245`. | MEASURED seq 67. The half-speed regime is marginal even at the reference point. |
| **R-4** | `Z` from `BS-PAIR` on the LEFT pair: `mid_deg_x10,−31, mid_se_deg_x10,3` → −3.1° ± 0.3°. Agrees with the DERIVED −3.15°. | MEASURED — the on-board pair arithmetic is correct. |
| **R-5** | Zero faults in the whole run (`faults,0`), as in the shakedown. The torque wall remains absent at the rungs that completed. | MEASURED. |
| **R-6** | The droop stop **again never fired** — no `DROOP` token anywhere. Three runs, zero occurrences. | MEASURED. Still unvalidated. |

---

## 5 · Findings register — dispositions

| # | Finding | Disposition |
|---|---|---|
| **T-1** | The point-scope current abort (2.5× leg reference) sits above the run-scope absolute abort (1,500 mV) whenever a rung's reference exceeds 600 mV. One point ends the run. | ⛔ **FIX FIRST, before any further scan run.** Clamp `pointLimitMv` below `ABS_ABORT_MV`. Do **not** touch the absolute abort — it is the unattended-safety backstop and lowering a safety limit to make a test pass is the error D1 forbids. |
| **T-2** | The walk's first UP step goes away from the optimum, into the steepest region, at every rung. | Largely **fixed by T-1**: with the point guard restored to its intended order, that step aborts point-scope, the side records as current-bounded, and the leg continues downward. Re-assess after T-1 rather than adding a second mechanism. |
| **T-3** | `BS-WALK` / `BS-BRACKET` mislabel every walk's rung (R-1). | **Fix** — pass the leg's rung to the emitter. Mine, introduced at `8ade2cb`. |
| **T-4** | Self-locating works: arcs nearly doubled, and it removed a 2–3° bias in the quarter-speed answer. | Closed — keep. |
| **T-5** | The inherited-centre bias means the shakedown's quarter-speed L values are high by 2–3°, and the speed effect is correspondingly larger (10–12°, not 9.55°). | **Corrects `SHAKEDOWN-EVALUATION.md` §4.** Carry the corrected figures to `«#3589»`. |
| **T-6** | `Z` is −3.7° ± 0.6° across five measurements, not ±0.15°. | **Corrects `SHAKEDOWN-EVALUATION.md` §4.** Still speed-invariant within its own spread, which is the property the driver needs. |
| **T-7** | No half-speed minimum, three attempts, three different causes. | Carry to the next run. It is the one gate on the speed law. |
| **T-8** | Droop stop unvalidated after three runs. | Carry. Do not claim it. |

---

## 6 · What is NOT established

- **The speed law.** Two rungs. The half rung has never yielded a minimum.
- **Anything about the RIGHT motor in this run.** It never started.
- **The droop detector.** Zero firings in three runs.
- **Whether `L`'s trend is linear.** Linear extrapolation from 28° at an eighth and 16° at a quarter
  would put half speed near 4° and full speed *negative*, which is physically suspicious and is
  precisely why a third point is needed rather than a fitted line through two.
