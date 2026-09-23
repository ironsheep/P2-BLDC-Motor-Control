# Visit 9 — the limits reset: the wheels follow to the command cap by field weakening; the raised duty ceiling is clean and moves the usable top 13 %; the floor is five times lower

**Task:** «#3605». **Run sheet:** [`../VISIT-9-RUNSHEET.md`](../VISIT-9-RUNSHEET.md). **Plan:**
[`LIMITS-RESET-PLAN.md`](../../../plans/LIMITS-RESET-PLAN.md) §2 E1–E4. **Procedure:**
`DOCs/procedures/BENCH-RUN-PROCESSING.md`. Evaluated 2026-09-23.

| Log | Tier | Binary | Rebuilt (UTC) | Source |
|---|---|---|---|---|
| `debug_260922-184229.log` | `dual-limits` | `test_bench_dual.bin`, 91,409 B | 2026-09-23 00:42:28 | `2e54955` |
| `debug_260922-185255.log` | `dual-limits-svm` | `test_bench_dual.bin`, 91,449 B | 2026-09-23 00:52:54 | `2e54955` + `-D DUTY_MAX_SVM` |

**Outcome:** both `BM-END,...,exit,COMPLETE,...,trap_code,0,unrecov,0`. Run 1 took 9 min 30 s (LIMTOP 189 s, LIMRAMP
63 s, LIMLOW 289 s), and run 2 took 3 min 20 s. No segment faulted.

**Banner, checked first:** both `src_rev,32,fmt,18,part,LIM`, `drv_rev,6`, and `BM-CLIPTEST,...,judge_ok,TRUE`.
Every `BM-CLIP` reads `duty_max,24_264` on run 1 (80 of 80) and `duty_max,27_648` on run 2 (79 of 79).

---

## §1 Headline

| Learning | The number that carries it |
|---|---|
| ⭐ **The wheels follow to the 245 × 10⁶ command cap, but by field weakening, not by headroom** | 99.9–100.2 % to 245 on 6 of 8 climbs (RIGHT forward slipped near the top on both builds); duty pinned from 165 (run 1), current 0.31 → 3.8–4.2 A |
| **The usable top is where duty first caps** (`unsat`) | 155 × 10⁶ today's ceiling, **175 × 10⁶ on the raised ceiling (+12.9 %)**, all four wheel-directions |
| ⭐ **The raised duty ceiling is certified** | PWM room 2–4 counts on SVM (desk 1–2), 151 on the default (desk ~150); rungs 3–8 unchanged |
| It also cuts current wherever duty saturates | at 185 × 10⁶: 0.32–0.40 A against 0.87–1.06 A; at 245: 2.3–2.6 A against 3.8–4.2 A |
| A slip past the top draws a large single peak | RIGHT forward at 235 on SVM: 81.8 % following, `i_max` 3,718 mV (~25 A), no fault |
| **The low-speed floor is at least 5.4× lower** | every rung down to 100,000 rotates at exactly its commanded rate, steadily |
| Halving `duty_min` cuts crawl current 3–13× and still rotates | net 81 → 6 (mV × 10) RIGHT reverse at 544,628; gaps spread wider |
| Faster starts follow cleanly; **A-2 cannot rank them** | zero lag holds and drop ≤ 0.03 at `ramp_inc` 22/44/88; A-2's denominator differs at 88 |
| Faster slow-downs are clean; **the sheet's criterion for them was malformed** | current only falls; its "peak" was the 147 × 10⁶ cruise current, which the control fails too |

---

## §2 E1 and E2 — the top of the range

### 2.1 The climb, run 1 (default ceiling), LEFT reverse

```
incre  ticks   hw  rate/pred%  win_lag  win_cap   duty  err  inet  amps_x10k  room
 -155   -417 -417      100.0        0        0 23_713  -48   402      2_825   170
 -165   -443 -443      100.2        0    7_286 24_244  -51   451      3_074   152
 -175   -469 -469      100.2        0   12_599 24_252  -54   762      5_178   152
 -185   -495 -483      100.0        0   16_984 24_256  -57 1_294      8_674   152
 -205   -548 -454       99.9        0   23_443 24_261  -60 2_621     17_351   151
 -245   -657 -347      100.0        0   31_800 24_263  -65 5_640     37_703   151
```

The other three climbs read the same to within a few percent. Only RIGHT forward at 245 slipped:
`ticks 434 hw 426`, following 66.2 %, `BM-TOPSPD,...,RIGHT,sign,1,top,235_000_000,unsat,155_000_000,edge,245_000_000,edge_why,SLOW`.

**Is the rotor really turning at 245 × 10⁶? Yes, and here is what the instrument shows.** The instrument's own hall
count (`hw`, sampled at 500 Hz) peaks near 490 ticks/s and then *falls*, while the driver's count (`ticks`, decoded at
the drive rate) keeps rising. The instrument is the suspect, and `BM-RUNG3` convicts it. `hw_skip` is 0 up to 175,
then 8, 35, 90 … 312, and **`hw` + `hw_skip` equals `ticks` to within 2 at every rung** (245: 347 + 312 = 659 against
657). The driver reports `missed_d,0,illegal_d,0` throughout. At about one sample per hall edge the 500 Hz poll
aliases, as the harness header predicted ("1.1 samples per hall edge"). The rotor is at about 438 rpm.

**How it gets there.** Duty is at its cap from 165. Past that the only thing that can advance the rotor is more
lead. `err` grows from 48 to 65 units (about 24° electrical more field advance), and the current rises twelvefold.
That is field weakening: speed bought with current, not with voltage. It is the reason the plan's top (245, the cap)
is not a speed to publish, and the reason `BM-TOPSPD` also prints `unsat`.

### 2.2 The climb, run 2 (the raised ceiling)

```
BM-TOPSPD,...,LEFT,sign,-1,top,245_000_000,unsat,175_000_000,edge,NA,edge_why,NONE
BM-TOPSPD,...,LEFT,sign,1,top,245_000_000,unsat,175_000_000,edge,NA,edge_why,NONE
BM-TOPSPD,...,RIGHT,sign,-1,top,245_000_000,unsat,175_000_000,edge,NA,edge_why,NONE
BM-TOPSPD,...,RIGHT,sign,1,top,225_000_000,unsat,175_000_000,edge,235_000_000,edge_why,HOLD
```

| At | Default (run 1): duty, current (A × 10⁴) | SVM (run 2): duty, current |
|---|---|---|
| 165 × 10⁶ | 24,244–24,246 (capped), 3,074–3,711 | 25,334–25,582 (92–93 % of cap), 2,951–3,494 |
| 175 × 10⁶ | capped, 5,178–6,419 | 26,889–27,161 (97–98 %), 3,240–3,755 |
| 185 × 10⁶ | capped, 8,674–10,567 | capped, 3,187–4,057 |
| 245 × 10⁶ | capped, 37,703–42,379 | capped, 22,806–26,102 |

**The slip on SVM.** RIGHT forward at 235: `rate/pred 81.8`, `win_lag,23`, `err_pk,111`, **`i_max,3_718`** mV (≈ 25 A
at 150 mV/A, a single-sample peak, under the 4-sample 10 A abort). A rotor that loses its field-weakened
synchronism dumps current. Nothing faulted. This is one more reason the published ceiling stays below the cap.

### 2.3 E2's other two claims

- **No clip, and the instrument reaches the peaks.** `R18-DUAL-PWMCLIP-M` `measured,151` / `151` on run 1 and
  `measured,2` / `2` on run 2, both PASS. The desk predicted ~150 and 1–2 (`svm_bound.py`). The SVM figure sitting
  on its desk value is what shows the 500 Hz sample reaches the waveform's peaks. A room far above it would have
  meant the PASS certified nothing.
- **No side effect below the ceiling.** The table below gives net current at rungs 3–8, default vs SVM. Every pair
  is inside ±10 % / ±5 mV, and duty agrees within 0.5 %, so the feedforward's slope held.

  | Rung | LEFT − | LEFT + | RIGHT − | RIGHT + |
  |---|---|---|---|---|
  | 40 | 97 / 94 | 110 / 96 | 104 / 101 | 102 / 103 |
  | 60 | 137 / 134 | 144 / 133 | 158 / 148 | 157 / 160 |
  | 80 | 191 / 187 | 197 / 185 | 213 / 213 | 221 / 222 |
  | 100 | 241 / 242 | 244 / 236 | 276 / 264 | 278 / 286 |
  | 120 | 293 / 290 | 299 / 290 | 340 / 331 | 342 / 350 |
  | 140 | 354 / 362 | 361 / 349 | 408 / 400 | 412 / 419 |

  LEFT forward at 40 (110 / 96, −13 %) is the one pair outside 10 %, and it is inside the ±5 mV floor (14 in mV ×
  10 units is 1.4 mV). PASS.

---

## §3 E3 — ramps

### 3.1 Starts from rest to the quarter

```
tid ramp_inc  drop  i_ratio (start_metrics.py)   ramp_ms  lag_holds  followed
 1-18    22   0.02-0.03   1.25-1.34                927-929      0        TRUE  (x4)
         44   0.01-0.02   1.51-1.85                660-666      0        TRUE  (x4)
         88   0.00-0.03   1.28-1.44                474-476      0        TRUE  (x4)
```

**By the criteria fixed on the sheet:** drop ≤ 0.10 PASS everywhere; `followed,TRUE` everywhere; A-2 ≤ 1.8 PASS at 22
and 88, **FAIL at 44 on RIGHT** (tid 12 at 1.82, tid 17 at 1.85).

⚠ **The 88 pass rests on a different denominator, so it is not claimed.** A-2 divides the peak by the mean of the
trace's last 60 ms. At 22 and 44 the trace runs past the ramp and that tail is settled quarter-speed current
(20.5–21.4 mV LEFT, 14.1–16.0 RIGHT). At 88 the ramp ends inside the capture's dense window. The trace stops at the
instant of reaching speed, and its tail (23–26 mV, 30 samples) still carries acceleration current. On the settled
denominator the peaks rise with the ramp, as they must: **1.26–1.34 at 22, 1.51–1.83 at 44, 1.57–2.13 at 88.** Their
absolute size is about 0.2 A. A-2 was built to detect the old start *surge* (1.9–3.0×). A faster ramp draws more
current for the plain reason that it accelerates harder, so A-2 cannot rank ramp rates.

### 3.2 Slow-downs, from 147 × 10⁶ to the quarter

`followed,TRUE` and `lag_holds,0` on all eight. `ramp_ms` is 1,154–1,159 at 50,000 and 580 at 100,000. In every trace
the current peak (59–73 mV) sits in the cruise ripple **before** the fall begins (samples k 5–47, state AT_SPEED).
Through SPIN_DN the current only falls, to a trough of −3 to 11 mV. **There is no surge at either rate.**

⚠ **The sheet's criterion for this was malformed.** "Peak ÷ settled quarter mean ≤ 1.8" takes the cruise current at
147 × 10⁶ as the "peak", so even the 50,000 control reads 4.5–10.7× and fails. A criterion its own control fails has
measured nothing (D2). Physically both rates are clean. By the fixed criterion the result is **inconclusive**.

---

## §4 E4 — below the old floor

All 32 rungs `result,OK`. Expected edges per 7.5 s window: 11, 8, 5 and 2.

| Rung | edges, as built / halved `duty_min` | gap min–max (ms), as built | halved | net (mV × 10), as built / halved |
|---|---|---|---|---|
| 544,628 | 10–11 / 10–11 | 564–792 | 432–918 | 81–91 / 6–31 |
| 400,000 | 8 / 8 | 756–1,062 | 594–1,218 | 79–94 / 5–28 |
| 250,000 | 5 / 5 | 1,254–1,710 | 786–1,998 | 78–93 / 6–26 |
| 100,000 | 2 / 2 | one gap, 3,156–3,708 | 1,704–4,074 | 77–96 / 6–29 |

Every rung meets **rotates** (at least half the expected edges; all read the full count) and **steady** (`gap_max` ≤
2× the expected gap: 687 / 935 / 1,497 / 3,743 ms). `rate_x10` equals `pred_x10` at every rung. **The new floor is at
most 100,000, the lowest rung tested.** Where it really lies is unmeasured.

Duty sits at `duty_min` at every one of these rungs (1,600, then 800). So the floor, not the load, sets the crawl
current. Halving it cuts that current 3–13× and still turns every rung, with the gap spread about twice as wide.

---

## §5 Sign-off cells

| Cell | Run 1 | Run 2 |
|---|---|---|
| `R18-DUAL-NOSTALL-M`, `-DBGMASK-M` | PASS, PASS | PASS, PASS |
| `R14-DUAL-TRACES-M` | PASS (20 traces, 0 lost) | NOMEAS (the build takes no trace, by design) |
| `R18-DUAL-TOPSPD-M` LEFT / RIGHT | PASS 245 / 235 | PASS 245 / 225 |
| `R18-DUAL-PWMCLIP-M` LEFT / RIGHT | PASS 151 / 151 | PASS 2 / 2 |

`R18-DUAL-TOPSPD-M` is **coverage, not evidence**: a regression guard no drive on file fails, as the sheet said. Its
"top" is now also known to include field weakening (§2.1).

---

## §6 What this means for the driver

### 6a What it now DOES — the moves this licenses, made in «#3605»

- **L2: the raised duty ceiling becomes the drive.** Certified clean with room to spare only at the desk's 1–2 counts,
  more top speed, less current above it, and nothing changed below it. The `DUTY_MAX_SVM` `#ifdef` and the
  `dual-limits-svm` tier are deleted, because they are superseded (D5).
- **L1: the 18.5 V ceiling moves 147 → 165 × 10⁶, +12 %.** **The rule:** the fastest measured rung that keeps
  today's unloaded duty reserve. 147 runs at 92.7 % of its cap on today's drive (Visit 8b), and 165 on the raised
  ceiling runs at 92–93 %. 175 was `unsat` but had about 2 % reserve, and the field-weakening region above it slips
  and draws current. The other voltages scale by voltage, marked DERIVED. `power` 100 moves with it (Stephen's ruling).
- **L5: the floor moves 544,628 → 100,000**, the lowest rung that rotated steadily. `power` 1 now crawls at about
  0.27 hall ticks/s.

⚠ **What this does NOT license:**
- **A ceiling in the field-weakening region.** Following there is real, but it costs 4 A unloaded, and a slip dumps
  current.
- **Moving the default ramps (L3).** Starts at 2× and 4× follow cleanly, but A-2 cannot rank them. The stop ramp sets
  stopping distances, so it waits for the loaded floor run (E5).
- **Moving `duty_min` (L6).** It is a measure-only limit in the plan. The saving is recorded (PL-110) for a decision
  with loaded evidence.
- **Any loaded margin.** Every number here is unloaded.

### 6b What it now KNOWS

Nothing new. This run measured limits and certified a construction. It integrated no sensor into the drive. Front 3
does not move with this pass.

---

## §7 What this changes about the next run

The confirming run is **`tools/bench-run.sh dual-limits-top` on the moved drive** (LIMITS part, climb only), not
`dual-a`. The change is in the power table and the default duty ceiling. `dual-a`'s raw-increment ladder cannot see
the first, and run 2 has already measured the second. It carries:
- LIMTOP on the new default: TOPSPD, and PWMCLIP at room ~2 on every build now.
- **The power check, built for this run** (`BM-POWER`, `R18-DUAL-POWERMAP-M`): `power` ±100 and ±1 through the
  public API must hold exactly 165 × 10⁶ and 100,000. The table it replaces fails that by construction.
- «#3597»'s `R18-DUAL-FOLLOW-M` / `-FOLFALL-M`. The over-command step is exactly the field-weakening region above,
  where RIGHT forward slipped. **Expect FOLFALL to see real shortfalls on some climbs and none on others.**
- LIMRAMP and LIMLOW **dropped**, because nothing under them changed except the floor constant, which they do not use.

For E5 (the floor run, «#3591»): add a stop at `ramp_down` 100,000 beside 50,000. It is the one loaded question left
for L3.

---

## §8 Findings register

| Id | Finding | Disposition |
|---|---|---|
| F-1 | The wheels follow to the cap by field weakening; `unsat` is the usable top | **Closed**: L1 moves on `unsat`'s reserve rule (§6a) |
| F-2 | The instrument's 500 Hz hall count aliases above ~490 ticks/s (`hw` + `hw_skip` = `ticks`) | **Closed**, instrument property. The driver's count is the authority up there |
| F-3 | A slip past the top draws a ~25 A single peak | **Punch list** PL-108 |
| F-4 | The raised duty ceiling: certified | ⛔ **FIX**: L2 made the default in «#3605» |
| F-5 | A-2's denominator is not comparable across ramp rates | **Punch list** PL-109 |
| F-6 | The speed-down peak-ratio criterion's "peak" is the cruise current | **Punch list** PL-109 (same criterion family) |
| F-7 | The floor is at most 100,000 | ⛔ **FIX**: L5 moved in «#3605» |
| F-8 | Halving `duty_min` cuts crawl current 3–13× | **Punch list** PL-110 |
| F-9 | AT_SPEED persists ~120 ms after a slower command, in all 8 SLOWER traces, while A-6 saw the field fall within 20 ms | **Watch**: the next SLOWER trace reads `drv_incr` beside the state. Unexplained; not chased (central §8) |
| F-10 | The ceiling at 18.5 V | ⛔ **FIX**: 147 → 165 × 10⁶, «#3605» |

---

## §9 What is NOT established

- **Anything under load.** Every top, ramp and floor here is unloaded (E5).
- **Where the floor really is.** 100,000 rotated; nothing below it was tried.
- **Where the true `unsat` lies** between the 10 × 10⁶ rungs: (155, 165) on the old ceiling, (175, 185) on the new.
- **A clip's negative case on hardware.** The judge's negative case was shown (`BM-CLIPTEST`), and the sampling's
  was argued from the desk value, not from a clipping drive.
- **Ramp rate ranked by current.** A-2 cannot do it (F-5), and no replacement criterion has been run.
- **The speed-downs by their fixed criterion**, which was inconclusive (F-6).
- **The other voltages' ceilings.** They are DERIVED by scaling, not measured.

## §10 Questions left open

- Is the ~7 % unloaded duty reserve enough under load? **E5 settles it** («#3591» / «#3576»).
- Default `ramp_down` 50,000 or 100,000? **E5**, with stopping distance measured.
- A lower `duty_min`: less crawl current against a less even crawl. **PL-110**, with loaded evidence.
- F-9's 120 ms: a state label lagging, or a command taken late? **Watch**, next SLOWER trace.

## §11 FRONTS

```
FRONTS  (before this pass)
  completion   driver last changed 0 commits ago (2e54955)
  information  2 loads ready and unrun: dual-limits, dual-limits-svm
  robustness   sensors the DRIVER acts on: halls y  current y  back-EMF n  follow y
FRONTS  (after this pass, once «#3605»'s moves land)
  completion   advanced -- the ceiling, the duty ceiling and the floor move from measurement
  information  advanced -- both loads run; the confirming dual-limits is the next ready load
  robustness   not advanced -- this pass integrated no sensor
```
