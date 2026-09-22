# Scan run with the clamped point guard — 2026-09-21 20:09, ABORTED IDENTICALLY

**Log:** `debug_260921-200935.log` (this folder), `test_bench_scan.bin` 53,878 bytes, rebuilt
02:09:34. Source `6b72ad0` — the commit that clamped the point-scope current guard below the
absolute one.

**Outcome:** `BS-END exit,ABORTED, reason,ABS_CURRENT, elapsed_s,401, points,68, left_done,FALSE,
right_done,FALSE`. **The same abort, at the same point, at the same second** as the previous run.

**The fix was present and did not work.** `BS-LIMITS` carries `point_abort_ceil_mV,1_200`, so the new
code ran. Verified before anything else, because a load that re-exercises an unchanged binary
certifies nothing.

---

## 1 · Why the clamp did not help — I fixed the threshold and left the race

MEASURED, from `BS-LIMITS` of this run:

| guard | threshold | samples required | **time to fire** | scope |
|---|---|---|---|---|
| absolute | `abs_abort_mV 1_500` | `abs_abort_samples 4` | **20 ms** | ends the **RUN** |
| point, relative | ≤ `point_abort_ceil_mV 1_200` | `point_abort_samples 40` | **200 ms** | ends one **point** |

At `SAMPLE_MS 5`, **the fatal guard fires ten times faster than the survivable one.** Bringing the
point threshold *below* the absolute achieved nothing, because current rising from 1,200 through
1,500 crosses both long before 200 ms elapses. **The previous evaluation named the level and missed
the time constant** — the ordering defect had two halves and only one was fixed.

**And the spike is in spin-up, not in the measured window.** MEASURED seq 68:
`result,WINDOW_TIMEOUT`, `steady_ms,1_320`, `follow_pct,44`, `span_duty_max,21_807`. The point never
reached AT_SPEED. `POINT_ABORT_SAMPLES 40` is *deliberately* slow so a start transient does not abort
a good point — so a genuine spin-up overcurrent falls in the gap between a guard that is too slow by
design and one that is fatal by design.

⛔ **The invariant that is actually violated:** *one point's current must never be able to end the
run.* A scan whose job is to locate current walls will, by construction, walk into them.

---

## 2 · The other half of the cause — the walk takes the dangerous step first

MEASURED, the half-speed leg's two walk sides:

```
HALF,NEG,side,UP  ,pts,1,last_swept_deg,53,stop,RUN_ABORT
HALF,NEG,side,DOWN,pts,0,last_swept_deg,43,stop,RUN_ABORT
```

**The UP side took one point and died. The DOWN side took none.** `walkSide()` is called UP first, and
UP is the direction *away* from the minimum at every rung measured: from the legacy `defSwept 43`, the
minimum sits at **25** (eighth), **12** (quarter) and — by trend — near **4** at half. Downward is
where current falls; upward is where it explodes. **The walk always tries the explosive direction
first**, and at half speed the first step of it is fatal.

Had it walked down first it would have descended 33, 23, 13, 3 through *falling* current, found its
minimum, and only then met the wall going up — where a working point-scope guard would have ended one
point rather than the run.

⚠ **Third-order consequence, which would have bitten the very next run even with the guards fixed.**
`run_abort_i_cap 6`, and the LOW and QTR legs legitimately spend **4** of it finding their outer
walls (MEASURED: four `scope,POINT` aborts at 47 s, 149 s, 217 s, 337 s). With three rungs there are
**12 legs**, each of which may legitimately find one current wall, so the expected abort count is
around 12 against a cap of 6. **The cap was sized when a current abort was an anomaly; with the arc
now bounded by current at every rung, it is an expected and informative outcome.**

---

## 3 · What the repeat bought: the instrument is far more precise than I credited

The run aborting at the same place twice means the LEFT motor's LOW and QTR legs were measured
**twice, independently**. DERIVED from `BS-PAIR` and `BS-RESULT-HALF` of both runs:

| | run 19:26 | run 20:09 | spread |
|---|---|---|---|
| **L at an eighth** | 28.0° | 28.1° | **0.1°** |
| **Z at an eighth** | −3.1° | −3.6° | 0.5° |
| **L at a quarter** | 15.85° | 15.9° | **0.05°** |
| **Z at a quarter** | −3.95° | −3.8° | 0.15° |

⭐ **`L` reproduces to a tenth of a degree, run to run, at both rungs.** That is much better than the
2° spread the earlier cross-run comparison suggested — that spread came from comparing *self-located*
against *inherited-centre* measurements, not from instrument noise.

**So the numbers now stand as:**

| | value | basis |
|---|---|---|
| **L at an eighth** | **28.05° ± 0.05°** | 2 runs, LEFT; RIGHT gave 28.5° once |
| **L at a quarter** | **15.88° ± 0.03°** | 2 runs, LEFT |
| **ΔL per halving** | **12.2°** | the two above |
| **Z** | **−3.6° ± 0.4°** | 4 measurements, both rungs |
| **L at a half** | *never obtained* | 4 attempts, 4 causes |

⚠ **`Z` still differs slightly between rungs** (−3.88 at quarter, −3.35 at an eighth, a 0.5° step that
is larger than either rung's own 0.15–0.5° repeatability). Z is supposed to be geometry. Either the
difference is real and Z has a small speed term, or the fit's vertex carries a little of the basin's
asymmetry. Not resolvable from two rungs; worth watching once a third exists.

---

## 4 · Findings register

| # | Finding | Disposition |
|---|---|---|
| **G-1** | The fatal absolute guard fires in 20 ms; the survivable point guard needs 200 ms. Clamping the threshold could not fix a race. | ⛔ **FIX** — add a **fast** point-scope guard at the ceiling, firing on the same sample count as the absolute, so a point at 1,200 mV is abandoned before 1,500 mV can end the run. Keep the slow relative guard for the 2.5×-of-reference case it was built for. Do **not** touch the absolute abort or slow the safety path. |
| **G-2** | The walk takes the UP side first, which is the away-from-optimum, rising-current direction at every rung. At half speed its first step is fatal. | ⛔ **FIX** — walk the DOWN side first. It costs nothing, it descends into falling current, and if the assumption about which way is safe were ever wrong the UP walk still runs afterward and still brackets. |
| **G-3** | `RUN_ABORT_I_CAP 6` against ~12 legs each expected to find one current wall. LOW and QTR already spend 4. | ⛔ **FIX** — raise to cover one wall-find per leg with margin. A current abort at the outer wall is now an expected, informative outcome, not an anomaly. |
| **G-4** | `BS-WALK` / `BS-BRACKET` now name their own rung correctly (LOW / QTR / HALF all appear). | Closed — the `6b72ad0` fix worked. |
| **G-5** | `L` reproduces to 0.1° run-to-run at both rungs; the earlier 2° spread was a methodology artifact, not noise. | Closed — and it raises confidence in §3's figures considerably. |
| **G-6** | `Z` steps 0.5° between rungs, larger than its own repeatability. | Watch. Needs a third rung; do not act on it. |
| **G-7** | Droop stop: **still zero firings, four runs.** | Unvalidated. Do not claim it. |
| **G-8** | Half-speed minimum: **four attempts, four distinct causes** — pinned (run 7), wrong confirm span (shakedown), run killed by the walk (19:26), run killed again (20:09). | The one gate on the speed law. |

---

## 5 · What is NOT established

- **The speed law.** Two rungs, precisely measured; the third has never been reached.
- **Anything about the RIGHT motor in either aborted run.** It never started in either.
- **Whether the half rung can be measured at all at 18.5 V.** If its optimum sits where spin-up
  current necessarily exceeds 10 A, that is a fact about the motor and the answer is that the rung is
  unmeasurable on this rig — which would itself be a finding worth having, and one the fixes above
  will distinguish from an instrument failure.
- **The droop detector** (G-7).
