# Visit 7c — three loads, two answered, and the new cell caught a real driver defect

**Processed per [`DOCs/procedures/BENCH-RUN-PROCESSING.md`](../../../procedures/BENCH-RUN-PROCESSING.md)** — its first use.

| Load | Log (this folder) | Source | Outcome |
|---|---|---|---|
| `scan-droop` | `debug_260921-223042.log`, 4,132 B, 04:30 | `14071ed`, `src_rev 18`, `fmt 11` | **COMPLETE**, 0 s |
| `scan` | `debug_260921-223111.log`, 301,592 B, 04:46 | `14071ed`, `src_rev 18`, `fmt 11` | **ABORTED**, `ABORT_I_CAP`, 914 s, 155 points |
| `dual-a` | `debug_260921-224820.log`, 3,253,494 B, 05:00 | `src_rev 23`, `fmt 11`, part A | **COMPLETE**, 5 segs, 17,154 records |

**Banner check — PASSED, verified before anything was read.** `scan-droop` carries
`droop_selftest,TRUE`; `scan` carries `droop_selftest,FALSE` and `wd_selftest,FALSE`; `dual-a` carries
`off_neg,14,off_pos,338` on **all 252** `BM-RUNG` records. Both scan loads are `src_rev 18`, so the
loop inversion and the follow cell are in the image.

---

## 1 · Headline

| | |
|---|---|
| ⭐ **The loop inversion took, and it is the difference between a lost run and a good one.** | The scan aborted — and still returned `left_rungs,3 right_rungs,2` of 3. The two prior aborts returned **five legs for LEFT and zero for RIGHT**. |
| ⭐ **The new follow cell FAILED — and it was right to.** | It caught a genuine driver defect: `updateFollowing()` reads `targetIncre` **without masking `SYNC_BIT`**, so the commanded rate reads ~5,650 ticks/s at every speed instead of 49 / 98. Predicted-by-factor, exactly as designed. |
| ⭐ **The start transient's mechanism is SETTLED — the deadband story HOLDS.** | All four START traces: duty pinned at 1,600 for **464 ms** while `\|err\|` climbs, first moving at `\|err\|` **57–59** against the 60° threshold of **42** units. Duty did **not** move before the crossing. |
| **The droop stop is certified.** | Fires at exactly point 2; silent on the isolated shape and across a fault. First execution of that branch, ever. |
| ⛔ **The half rung failed a fifth time — with a new and more informative cause.** | All four HALF legs `NOT_BRACKETED`, on a reachable arc only **20°** wide bounded `TORQUE` at *both* ends, sitting entirely on the far side of where the trend puts the optimum. |
| ⛔ **My own negative limb cannot fire.** | `FOLLOW_COLLAPSED` is `NOMEAS, n,0` — and **16 of 16** drooping points had the driver reading `NA`. The cell is structurally unreachable. |

---

## 2 · Why the scan aborted — `ABORT_I_CAP`, and it is the intended behaviour

`BS-END … reason,ABORT_I_CAP, elapsed_s,914, points,155, faults,0, aborts_i,16`.

`RUN_ABORT_I_CAP` was raised 6 → 16 at `caf1c88`. The run used **all 16** and stopped. **`faults,0`** —
not one fault in 155 points, against run 7's 15.

This is not the same failure as the two 401 s aborts. Those died at `ABS_CURRENT` on a single fatal
step. This one spent its full budget of *expected, informative* wall-finds and stopped when the budget
ran out, after completing **11 of 12 legs**.

⚠ **The cap is now the binding constraint on run length, not safety.** 12 legs × 2 walls = 24 wall-finds
is the natural budget; 16 stops the run five sixths of the way through.

---

## 3 · The loop inversion — the falsifier it was given, and the result

The run sheet fixed this in advance: *if the run aborts and one motor shows 0 rungs, the inversion did
not take.*

| | prior aborts (`192618`, `200935`) | this run |
|---|---|---|
| LEFT | 5 legs | **3 of 3 rungs**, `left_done TRUE` |
| RIGHT | **0 legs — never started** | **2 of 3 rungs** |
| points | 68 | **155** |

**The inversion took.** The abort landed in RIGHT's HALF rung; everything at LOW and QTR for both
motors was already banked. Under the old order that same abort would have cost the entire RIGHT motor.

The `left_rungs` / `right_rungs` fields did their job too: `left_done,TRUE right_done,FALSE` alone
would not have said that RIGHT completed two thirds of its work.

---

## 4 · R18-SCAN-FOLLOW — FAIL, and the defect it found

**Verdict: `FOLLOW_AGREES_PCT` FAIL on both motors, worst disagreement 89 against a limit of 20, over
66 and 65 points.**

The cell is doing exactly what it was built to do. From `BS-POINT3`:

| seq | motor | harness `follow_pct` | driver `drv_follow_pct` | `drv_meas_tps` | `drv_cmd_tps` |
|---|---|---|---|---|---|
| 1 | LEFT | 90 | **100** | 98 | **98** |
| 2 | LEFT | 90 | **1** | 99 | **5,640** |
| 5 | LEFT | 87 | **0** | 49 | **5,689** |

**`drv_meas_tps` tracks the harness perfectly** — 49 at an eighth, 98 at a quarter. The *measured* side
of the driver's reading is correct. **`drv_cmd_tps` is near-constant at ~5,650 regardless of commanded
speed**, which is the signature of a denominator that does not depend on the command at all.

### Root cause — `SYNC_BIT` is not masked, and the arithmetic proves it

`isp_bldc_motor.spin2:3650`:

```spin2
followCmdTicksSec := muldiv64(abs(targetIncre) >> 9, ...
    HALL_TICKS_PER_CYCLE * (PWM_RATE_IN_HZ / DRIVE_PASS_FRAMES), 1 << 23)
```

`SYNC_BIT = $8000_0000` is **bit 31 of `targetIncre`** (`:2996`). Every other reader in the file masks
it — `targetIncre & !SYNC_BIT` at `:1790`, `:1849`, `:3432`. **This line does not.** With the bit set,
`targetIncre` reads as a large negative number and `abs()` returns ≈2³¹ minus the real increment.

Computed against the shipped constants (`HALL_TICKS_PER_CYCLE 6`, `PWM_RATE_IN_HZ 44_000`,
`DRIVE_PASS_FRAMES 23` → K = 11,478):

| command | clean | with `SYNC_BIT` set | **logged** |
|---|---|---|---|
| eighth, `incre 18_375_000` | 49 | **5,689** | **5,689** |
| quarter, `incre 36_750_000` | 98 | **5,640** | **5,640** |

**Exact match on both.** The formula and the shift pair are correct; only the mask is missing. `seq 1`
and `seq 3` read 98 correctly because the driver had already taken the command and cleared the bit.

⭐ **This is front 3 working as designed.** The harness's `follow_pct` and the driver's `nPctOfCmd`
were built as independent computations precisely so that a wrong denominator would show up as a gross
disagreement — *"a wrong denominator misses by a factor, not by points"*, stated in the cell's own CON
block before the run. It missed by a factor of 57–115 and the cell caught it on its first outing.

### ⛔ And the cell's other limb cannot fire — my defect, not the driver's

`FOLLOW_COLLAPSED` returned `NOMEAS, n,0` on both motors. Counting `BS-POINT3` directly:

| harness `follow_pct` | points | of which driver `NA` |
|---|---|---|
| **< 60 (drooping)** | **16** | **16** |
| 60–79 | 8 | — |
| ≥ 80 | 131 | — |

**Every drooping point had the driver reading `NA`.** The cause is structural: a point droops because
it was cut short by `ABORT_I`, and a point cut short never fills the driver's 1 s rpm window, so
`bFollowValid` is FALSE — and `accumFollowPoint()` excludes exactly those points by design.

The guard is right (an unfilled window *would* read as a false collapse). The **limb** is wrong: it can
never be measured, so it is a cell that cannot fail on the path it exists to police. That is PL-98's
shape, and it is the **second** instance found in this cell family tonight.

---

## 5 · The START trace — the falsifier was specific, and the answer is clean

The sheet fixed it in advance: *if the surge is the servo's 60° deadband, duty stays pinned at
`duty_min_` while `|err|` climbs and current surges only as `|err|` crosses 60°; **if duty moves
before that crossing, the deadband story is wrong.***

60° = `256/6` = **42** err units. Four traces, both motors, both directions:

| tid | motor | dir | duty pinned at | first duty change | `\|err\|` there | verdict |
|---|---|---|---|---|---|---|
| 1 | LEFT | −36,750,000 | 1,600 | k=232 (464 ms) | **57** | HOLDS |
| 8 | LEFT | +36,750,000 | 1,600 | k=232 | **57** | HOLDS |
| 27 | RIGHT | −36,750,000 | 1,600 | k=232 | **58** | HOLDS |
| 34 | RIGHT | +36,750,000 | 1,600 | k=233 | **59** | HOLDS |

**Duty did not move before the crossing on any of the four.** It sat pinned for 464 ms while `|err|`
climbed past 42, and only then began to rise; peak current followed *after* duty began climbing (i=87
at duty 5,357, k=369). `err` reads −1 from k=2 — `initAngleFmHall()` forcing `err_ = 0` at start, as
the mechanism predicts.

**The deadband story is confirmed, not refuted.** «#3593» built this trigger and it sat unrun for five
sessions; its first run settles the question outright.

⚠ Magnitude is **not** established: wheels up, peak current 64–100. Stephen felt a thump under load.
The *mechanism* is resolved; its size under load is not.

---

## 6 · The measurements

**Walking rung (an eighth) and quarter — 8 of 12 legs bracketed, all `OK`.**

| motor | rung | NEG min | POS min | **Z** | **L** |
|---|---|---|---|---|---|
| LEFT | eighth | 24.1 | −31.6 | **−3.8** ± 0.3 | **27.8** |
| RIGHT | eighth | 24.3 | −32.3 | **−4.0** ± 0.3 | **28.3** |
| LEFT | quarter | 12.0 | −19.7 | −3.85 | **15.85** |
| RIGHT | quarter | 12.6 | −19.5 | −3.45 | **15.55** |

These reproduce the prior self-located values (L 28.05 ± 0.05 at an eighth, 15.88 ± 0.03 at a quarter;
Z −3.6 ± 0.4) **to within their stated errors, on an independent run**. `Z` is speed-invariant across
both rungs on both motors; `L` moves 12.2° per halving. Both prior claims are confirmed.

**The half rung — NOT_BRACKETED on all four legs, fifth failure, new cause.**

| motor | sign | arc | width | bounds |
|---|---|---|---|---|
| LEFT / RIGHT | NEG | 23 … 43 | 20° | `TORQUE` / `TORQUE` |
| LEFT / RIGHT | POS | −43 … −23 | 20° | `TORQUE` / `TORQUE` |

Against the eighth's 40–50° arcs bounded `RISE`/`CURRENT`, the half rung's reachable window is half as
wide and bounded by torque at **both** ends. Extrapolating L (27.9 → 15.7 → ~3.5), the half-speed
optimum should sit near swept **3–4** — **outside** the 23…43 window entirely. Current at the default
is 950 mV (`i_def_mV_x10,9_531`) against 170 mV at a quarter.

⛔ **Interpretation is NOT settled here.** The arc bounds and the extrapolation are measured; *why* the
reachable window sits where it does is «#3589»'s work. What this run establishes is that the half-rung
failure is **not** an instrument failure — the guards worked, no fits pinned, the legs reported
honestly that they did not bracket.

---

## 7 · Findings register

| # | Finding | Disposition |
|---|---|---|
| **C-1** | `updateFollowing()` does not mask `SYNC_BIT`; commanded rate reads ~5,650 at all speeds. Root cause proven to the digit. | ⛔ **FIX** — one mask, `abs(targetIncre & !SYNC_BIT)`, matching `:1790`/`:1849`/`:3432`. Driver change; bump nothing else. |
| **C-2** | `FOLLOW_COLLAPSED` cannot fire: droop ⟹ short point ⟹ window unfilled ⟹ excluded. 16/16. | ⛔ **FIX** — the limb needs a driver reading that survives a short point, or a different negative case. Do **not** simply drop the validity guard; it prevents a false collapse. Redesign with C-1. |
| **C-3** | `DROOP_FAULT_RESETS` passes but cannot fail (found at the desk pre-run; confirmed PASS here). | ⛔ **FIX** — `DSQ_BOTH`, already specified and mutation-verified. |
| **C-4** | The loop inversion preserved 2 of 3 rungs on the motor that used to be lost entirely. | **Closed** — falsifier passed. |
| **C-5** | Droop stop fires at exactly 2, silent on isolated and across a fault. First execution ever. | **Closed** (with C-3's caveat on the third limb). |
| **C-6** | Deadband mechanism confirmed on 4/4 START traces. | **Closed** — feeds «#3589» correction 2. |
| **C-7** | Z and L reproduced independently at two rungs, both motors, within stated error. | **Closed** — the speed dependence is now confirmed, not provisional. |
| **C-8** | Half rung: 5th failure, reachable arc 20° bounded TORQUE/TORQUE, optimum extrapolates outside it. | **Watch** → feeds «#3589». Not an instrument fault. |
| **C-9** | `ABORT_I_CAP 16` is now the binding constraint on run length; 12 legs imply up to 24 wall-finds. | ⛔ **FIX** — raise to cover one wall per leg-end with margin. `faults,0` says the walls are safe to find. |
| **C-10** | `R10-SCAN-RSTALONE` NOMEAS both motors — no eligible fault arose (`faults,0`). | Correct behaviour. No action. |

---

## 8 · What is NOT established

- **The half-speed minimum.** Fifth attempt, fifth distinct cause. Still the one gate on the speed law.
- **The speed law itself.** Two rungs confirmed; a curve through two points is a line by assumption.
- **The start transient's MAGNITUDE under load.** Mechanism settled, size not — wheels were up.
- **Whether the driver's following reading is usable at all.** C-1 makes every `nPctOfCmd` in this run
  wrong whenever a sync command was outstanding. The *measured* half is confirmed correct; the ratio
  is not certified until C-1 lands and a run re-judges it.
- **`DROOP_FAULT_RESETS`'s claim** (C-3) — coverage, not evidence.
- **`Z` absolutely and cold.** The ALIGN tier did not run (PL-99 / PL-100).

---

## 9 · The outcome

### 9a · What it means for the driver — what it now DOES *(front: completion)*

- **C-1 is a driver fix and it is the immediate harvest.** One mask on `:3650`. Until it lands, the
  drive's own answer to *"am I following?"* is wrong by a factor of 57–115 whenever a synchronized
  command is outstanding — which is most of the time under the steering object.
- **Correction 2 has its evidence.** The deadband is confirmed: `initAngleFmHall()` forces `err_ = 0`,
  the servo sits inert for 464 ms until `|err|` passes its 60° setpoint, and the catch-up is the
  surge. **Moving lead out of the setpoint and into the feedforward offset should shrink the start
  transient** — that is now an argument from measurement, and it is what «#3589» was waiting for.
- **Z is safe to fix in the compile-time offset; L is not.** Confirmed independently at two rungs on
  two motors. Z moved 0.2–0.55° across a doubling; L moved 12.2°.

⚠ **What this does NOT license.** It does not fix the half-speed offset — the optimum there is not
measured, and the arc suggests it may not be reachable. It does not license acting on `nPctOfCmd`
anywhere in the control path: R18.1's rule stands, and the reading is provably wrong today besides.

### 9b · What it means for the driver — what it now KNOWS *(front: robustness)*

**Front 3 did not advance this run, and that is the honest reading.** `testGetFollowing()` was
certified *and failed*. The drive still cannot correctly tell whether it is following its own command.
It is closer than it was — the measured half is proven correct and the defect is localised to one
unmasked bit — but the capability is not yet real, and **C-1 must land before front 3 can be claimed
to have moved at all.**

### 9c · What it changes about the next run *(carries forward as the next sheet's draft loads)*

1. **`scan` again after C-1 + C-9**, to re-judge `FOLLOW_AGREES_PCT` against a corrected denominator
   and to let the run reach 12 of 12 legs.
2. **`scan-droop` again after C-3** — seconds, and it closes the last uncertified limb.
3. **A half-rung load that does not assume the optimum is inside the arc.** The sweep must be able to
   report *"the optimum is outside the reachable window"* as a result. This is the fifth attempt;
   attempt six should change what is being asked, not retry the same question.
4. **Drop:** the ALIGN tier stays out until PL-99/PL-100 land.
5. **`dual-a` need not repeat** — the START question is answered. It returns only for the loaded
   magnitude, which belongs to the tethered floor tier «#3591».

### 9d · Questions left open

| Question | What would settle it | Owner |
|---|---|---|
| What is the speed law for `L`? | A third rung — or a principled reason the half rung is unreachable | «#3589» |
| Is the half-speed optimum reachable at 18.5 V at all? | Load 3 above, designed to report "outside the window" | «#3589» |
| Which knob carries the lead? | Deadband now confirmed; needs the setpoint A/B, still unbuilt | «#3589» |
| How large is the start surge under load? | The tethered floor tier | «#3591» |

### 9e · FRONTS ledger, after this run

```
FRONTS
  completion   driver last changed 4 commits ago (31c8b91)  -- C-1 is the pending harvest
  information  0 loads ready and unrun     -- all three carried loads ran
  robustness   sensors the DRIVER acts on: halls y  current y  back-EMF n  follow NO
                 (follow declared at isp_bldc_motor.spin2:1468 but PROVEN WRONG -- C-1)
```

⛔ **`robustness` reads `follow NO` deliberately.** The `PUB` exists, so a declaration check passes —
but the run proved the value it returns is wrong. **A capability that is declared and wrong is not
integrated**, and recording it as `y` here would be the word-grep failure wearing a better disguise.
