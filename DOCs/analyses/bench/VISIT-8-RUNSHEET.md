# Visit 8 — run sheet (the drive change, certified; the lead table, measured)

**Plan section:** R18.5 of [`../../plans/BENCH-READINESS-SPRINT-PLAN.md`](../../plans/BENCH-READINESS-SPRINT-PLAN.md),
with the phasing Stephen set on 2026-09-22 (*dynamic lead in, back-EMF deferred*).
**Design and acceptance numbers:** [`../../plans/DRIVE-INTEGRATION-DESIGN.md`](../../plans/DRIVE-INTEGRATION-DESIGN.md) §5.5 (A-1 to A-10).
**Task:** «#3584». The lead table is filled afterwards by «#3601».

---

## Check the banner before reading anything else

| Load | Every `BM-BANNER` / `BM-BUILD` must read |
|---|---|
| all three | `src_rev,28` · `fmt,16` · `drv_rev,3` |
| `dual-a` | part `A`; every `BM-RUNG` `off_neg,14 off_pos,338` |
| `dual-d` | part `D` |
| `dual-lead` | part `LEAD`; `off_neg` / `off_pos` step through Z ± L, with Z = −4 |

A load reporting anything else ran a different tree. **Stop**, and every number from it is about
something else.

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of the drive change (DRIVER_REV 3), judged against numbers fixed before the build, **plus one measurement**: `dual-lead` fills the dynamic-lead table. |
| **Hardware risk** | **This is the first time the new driver code runs on hardware.** The duty servo, the feedforward, the overload hold and command handling are all new. What bounds a mistake is unchanged: the per-frame current fold-back, the 10 A abort, the lag limiter and the fault test at 125. The worst plausible fault is a mis-scaled feedforward, which would show as higher current at speed, not as a runaway. `dual-d` stalls both wheels at a 1 A limit **on purpose** (as every `dual-d` has). `dual-lead` may fault a wheel **on purpose** at a low lead and high speed (the torque wall); it is recovered and the run goes on. Wheels up, no hands near the rig. Panic throughout: physical battery disconnect. |
| **Who can observe** | **Nobody needs to — every verdict is printed.** All three loads are unattended. One observation is worth having if you are near the rig: **does a start sound or feel different from before?** The start surge was felt through the frame. That is an observation, not a verdict. |
| **Runs that carry state** | **None across loads.** `dual-lead` sets offsets by hand, and the harness turns the lead schedule back on at the end of every lifetime. `dual-d` lowers the current limits and restores them, reading them back (I11). A load that stops early leaves nothing on the board: each start re-initialises the driver. |
| **Run length** | **About 30–40 minutes for all three (ESTIMATED).** `dual-a` MEASURED 693 s on 2026-09-20, and TAKE adds about 15 s, so ~12 min. `dual-d`: no recent duration on record; its cap is 15 min. `dual-lead`: 112 measured steps of ~3 s plus lifetimes, ~8–12 min estimated; cap 25 min. |
| **Repeatability** | Each load is repeatable and idempotent. The provoked faults are recovered in-run, and no power cycle is needed between loads. |
| **Variant matrix** | One source, three part builds of `test_bench_dual.spin2`, on one rig: Rev B, the paired 6.5in hub motors, 18.5 V, 270 MHz. Three logs. |

---

## The commands

**Order matters: `dual-a` first.** It is the gentlest first contact with the new driver, and its
START trace and ladder carry most of the certification.

```bash
tools/bench-run.sh dual-a      # 1: START trace, ladder, low speed, and the new TAKE segment
tools/bench-run.sh dual-d      # 2: steering front cog, current limits, and the stall that is also A-7
tools/bench-run.sh dual-lead   # 3: the live lead-step run -- fills the dynamic-lead table
```

If `dual-a` shows anything alarming, **stop there**. The other two can wait for its analysis.

---

## What each load decides, and how each judgement can fail

The "shipped" figures are MEASURED on the drive this change replaces. Each judgement below is shown
able to fail: the old drive fails it, or a named defect in the new one would.

### `dual-a`

| Id | Judged by | Criterion | Shipped | Fails if |
|---|---|---|---|---|
| **A-1** | report, from the 4 START `BM-TS` traces (`servo-model/start_metrics.py`, run the same way on the shipped logs) | largest duty drop during acceleration **≤ 0.10** | 0.34–0.53 | the servo still hunts during a start |
| **A-2** | report, same traces | start current peak ÷ settled **≤ 1.8** | 1.94–3.04 | the surge survives |
| **A-3** | report, ladder rungs 1–2 (`BM-RUNG2`) | `duty_pk − duty` **≤ 400** and `err_pk` **≤ 76** | 800–1,650 and 75–89 | low-speed hunting survives |
| **A-4** | report, ladder rungs 1–8 | mean `err` **47–49** at every rung | 45 at rung 2 | the servo does not hold a point |
| **A-5** | report, rungs 3–8 against pass 2 (`debug_260922-122752.log`) | `duty` and `inet_x10` within **±5 %**, rate within **0.5 %** of `pred_x10` | — | the change cost efficiency or speed |
| **A-6** | cell `R18-DUAL-TAKE-A`, per motor (`BM-TAKE`) | a speed-down issued while `SPIN_UP` at or above QTR: `drv_incr` falls within **20 ms** | the command was discarded; the field climbs to HALF | PL-104's fix is not in effect |
| **A-8** following | cell `R18-DUAL-FOLAGREE-A`, per motor | at a steady QTR, the path limiter's fraction ÷ 10 and the rpm window's % agree within **5 points** | — (new) | the two readings measure different things |

The part's standing cells still run and are read as always. **`R17-DUAL-TRKICK-A`** (the transition
kick at a speed change) FAILED at 221 / 214 on the old drive. Its result on the new one is recorded,
not predicted.

### `dual-d`

| Id | Judged by | Criterion | Fails if |
|---|---|---|---|
| **`R16-DUAL-BLOCKED-D`** (existing) | cell | the stall still latches the protective stop, refuses, and releases only on its own clear | **the overload hold defeated the protective stop.** That is the regression DRIVER_REV 3 exists to prevent, so this cell is a certification of the change, not background. |
| **A-7** | cell `R18-DUAL-HOLDSET-D`, per wheel | 200 ms after the wheel first reads SHORT in the stall, `\|drv_incr\|` **≤ 10 %** of the commanded increment | the field is still at the command, as the shipped driver held it |
| **A-8** not-following | cell `R18-DUAL-NOTFOL-D`, per wheel | on the last poll before the latch, the path limiter's fraction **< 500 ‰** and the rpm window's % **< 50** | either reading says a stalled wheel is following |
| **A-10** | report, `BM-FRONTST` | steering front cog worst pass **≤ 950 µs**, `late` 0 | the path limiter or the lead schedule overran the tightest budget (8.6 % headroom before them) |

### `dual-lead`

| Id | Judged by | Criterion | Fails if |
|---|---|---|---|
| coverage | cell `R18-DUAL-LEAD-BRKT`, per motor | at least **4 of 8** speed × sign combinations bracket their minimum (`BM-LEADMIN verdict BRACKETED`) | the stepped range misses the optimum where it has always been found |
| known answer | cell `R18-DUAL-LEAD-KNOWN`, per motor | the quarter's bracketed minimum, mean of the signs, is **8–23°** | the instrument disagrees with the 15.6–15.9° every scan measured there |
| the table | `BM-LEADMIN`, all 16 combinations | **not judged here.** «#3601» reads it to fill the table, with the saving in amperes against L = 18 | — |

### Not on this visit

- **A-9** (the driver still fits) is judged at the desk from the compiler: cog RAM **480 / 496**, LUT
  **144 / 512** (recounted at DRIVER_REV 3).
- **Anything loaded.** Every cell here is wheels-up. The loaded expectations (§5.5, right-hand column)
  wait for the floor run, «#3591» at «#3576».
- **Back-EMF.** Deferred to a delta release by Stephen (task «#3602»).

---

## After the run

One analysis per set of logs, reading the logs themselves (`DOCs/procedures/BENCH-RUN-PROCESSING.md`,
step 0 first). Every A-number gets a verdict or a stated reason it has none.
