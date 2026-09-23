# Visit 10 — run sheet, pass 2 (the drive ends well: the hold, the fault responses, the platform policy, startup checks)

**Task:** «#3613» runs it. **Built by:** «#3608» (hold), «#3612» (platform policy), «#3609» (fault response), «#3610»
(start checks), «#3607» (T0-24), «#3614» (the firmware negatives). **Plan:** `BENCH-READINESS-SPRINT-PLAN.md`, R19.

**Pass 1 (2026-09-23 16:03–16:06):** three runs came back. The right board drove nothing (PL-120), and T0-24's rows
ended before a hand was on the wheel (PL-121, fixed). No fault-response or hold cell was measured.
[Evaluation](2026-09-23/VISIT-10-PASS1-EVALUATION.md).

---

## Before the session — the right board

**The right motor board put no voltage on any motor lead in every run of pass 1** (PL-120). The left board, on the
same program, did. Every load below that drives the right wheel measures nothing until that board drives again.
Check its power and motor connections before run 1. Run 1 then shows in its log whether it drives.

---

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `dual-*` tiers | `BM-BUILD ... drv_rev,13`. Anything lower means an old tree was built: stop and report |
| `dual-start` | part `START`, `BM-SKBUILD ... no_walk,FALSE`, negative `NONE` |
| `dual-start-phaseneg` | part `START`, `BM-SKBUILD` negative `PHASE`, a `BM-SKNEG` record before every `BM-SSTART` |
| `dual-start-swapneg` | part `START`, `BM-SKBUILD` negative `SWAP`, a `BM-SKNEG` record before each of the last 3 `BM-SSTART` |
| `dual-start-nowalk` | part `START`, `BM-SKBUILD ... no_walk,TRUE`, negative `NONE` |
| `dual-fault` | part `FRESP`; a `BM-FRBUILD` record; `BM-NOTBUILT` for `B4PULSE` only |
| `t0-stopmode` | `src_rev 12`; `T0-24,row,...` records numbered 1 to 8 |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Measurement and certification**, as pass 1 declared it. It sizes the hold's ceiling in amps, the graded short's duty, the rest-zero band, the lead-check thresholds and the wiring walk's power. It certifies the hold's hand-offs, the re-synced stop, the graded-short fallback, the platform stop when one wheel faults, the forced-fault hook's own negative, the stop-state coasts, and each start check against a negative it must catch. |
| **Hardware risk** | `dual-fault` **faults the wheels on purpose at up to about 220 rpm commanded**. Each fault ends in a phase short, a free coast, a controlled ramp down, or the graded short. **The graded short regenerates into the supply, so it needs the pack, not a bench supply.** The 10 A abort and the fold-back limiter apply throughout. `dual-start-swapneg` drives the left wheel as if two hall wires were swapped. A swapped pair reverses the hall sequence the driver reads, so the wheel may jerk, buzz or turn briefly the wrong way, for up to 2 s per leg at power 10, until its fault test or the 10 A abort stops it. `t0-stopmode` spins the right wheel under power in rows 6 and 7. **Wheels up throughout. Hands off in every unattended tier. Panic: physical battery disconnect.** |
| **Who can observe** | `t0-stopmode` is attended. Each row waits for you after START ROW and says on its panel what to do and what you should feel. The unattended tiers need nobody. One observation is worth having near `dual-fault`: does a 100 % graded stop sound or look like the full short? That is an observation, not a verdict. |
| **Runs that carry state** | None. The firmware negatives apply to one start each, and the next start reads the wiring as it is. |
| **Run length** | About 15 minutes of unattended runs, 2 minutes of rewiring for run 4, and about 10 minutes attended for run 6. |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack, 270 MHz. `test_bench_dual.spin2` parts START (four builds) and FAULTRESP; `test_bench_t0.spin2` T0-24. |

---

## The commands — run every one, in this order

```bash
tools/bench-run.sh dual-start             # 1: the start checks, wiring as built -- and whether the right board drives
tools/bench-run.sh dual-start-phaseneg    # 2: firmware negative: one LEFT lead withheld per start. Nothing moves
tools/bench-run.sh dual-start-swapneg     # 3: firmware negative: LEFT halls read as swapped in the walk -- the left wheel may jerk or turn the wrong way
tools/bench-run.sh dual-start-nowalk      # 4: ATTENDED WIRING -- RIGHT hall connector unplugged (B-1). Nothing moves
tools/bench-run.sh dual-fault             # 5: the fault responses, the platform policy, the hook's negative control
tools/bench-run.sh t0-stopmode            # 6: ATTENDED -- the hold rows and the stop states at the RIGHT wheel
```

**Run 4's wiring change:** disconnect the battery, unplug the RIGHT wheel's hall connector, reconnect the battery, and
run. Then disconnect the battery again, replug the connector, and reconnect.

**No run depends on another run's result.** If run 1 shows the right board still dead, the right-wheel cells of runs
5 and 6 come back NOMEAS, and the analysis says so.

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). Cells print their own verdict. The rest are judged in the report
from the named records.

### `dual-start` — the start checks and the wiring walk (startup study §6)

Ten steering lifetimes. Each start records `BM-SSTART`, `BM-SKHEALTH` (both wheels) and one `BM-SKPROBE` per wheel.
The last three also record `BM-SKWALK`, and the segment ends with one `BM-SKSUM` per wheel.

| Cell | Criterion | Fails if | Control | Sizes |
|---|---|---|---|---|
| **R19-DUAL-PRBFLR-X**, per wheel, **judged first** | the largest coasting-floor phase reading ≤ 99 mV | the floor reaches 100 mV | this *is* the probe's able-to-report control | the floor the follow threshold must stay above |
| **R19-DUAL-HEALTH-X**, per wheel | 0 of 10 starts with any failed bit | any bit in `l_fail`/`r_fail` | runs 2 and 4 | — |
| **R19-DUAL-RZSPREAD-X**, per wheel | 0 rest zeros outside −100…+200 mV | one outside the band | — | **REST_ZERO_MIN_MV/MAX_MV** from `BM-SKSUM`. Pass 1 measured the left at 7.7–8.5 mV and the right at 0.3–2.4 mV |
| **R19-DUAL-PROBE-X**, per wheel | 0 of 30 probes whose driven phase reads under 200 mV, or any follower under 50 % of it | any bad probe | PRBFLR; run 2 | **CONT_MIN_DRIVEN_MV**, **CONT_FOLLOW_PCT**. Pass 1 left: driven ≥ 782 mV, followers ≥ 95 % |
| **R19-DUAL-WALK-X**, per wheel | 0 of 3 walks failing: HLT_WIRING passes, both legs 6–9 ticks in opposite directions, no hall events | `l_ok`/`r_ok` FALSE | run 3 | **WALK_POWER** (10, provisional), the overshoot allowance |
| **R19-DUAL-PACK-X** | every start reads PACK_NOT_FITTED, 0 mV, no HLT_PACK | any other reading | — | none: no sensor fitted |

⚠ **A wheel's walk is judged only when its partner's walk moved.** Both wheels walk at once, and the platform policy
stops one wheel when the other cannot move. In pass 1 the left's legs came up 3 ticks against a dead right. A walk
whose partner moved 0 ticks is recorded as partner-limited, not as a verdict.

### `dual-start-phaseneg` — B-3's negative, in firmware

The rig cannot open a motor lead (Rig facts, 2026-09-23). Instead each start's lead check leaves one LEFT lead undriven,
rotating U, V, W, so the probe reads a real undriven output. That is the reading a dead switch gives. The right wheel
is the in-run control.

| Cell | Criterion | Fails if |
|---|---|---|
| **R19-DUAL-PHNEG-X**, LEFT | every start's `l_fail` is **exactly** the withheld lead's bit ($0004 / $0008 / $0010) | any start with no bit, another bit, or more than one. $001C, a whole dead bridge as in pass 1, FAILS it |
| R19-DUAL-HEALTH-X, RIGHT | 0 of 10 | any failed bit on the untouched wheel |

**What it cannot show:** an open *winding*, which fails the follow test rather than the drive test. The rig cannot make
one, and firmware cannot fake one honestly. That half of the lead check stays unexercised by a negative.

### `dual-start-swapneg` — B-5's negative, in firmware

The rig cannot swap hall wires. Instead, in the three walk lifetimes, the LEFT driver reads hall bits 0 and 1 as
swapped. It commutes and counts exactly as it would with those two wires crossed.

| Cell | Criterion | Fails if |
|---|---|---|
| **R19-DUAL-SWNEG-X**, LEFT | 0 of 3 walks in which the left's HLT_WIRING was not judged failed | the swap went undetected, or was never judged, in any walk. NOMEAS if no walk ran |

⚠ **SWNEG's PASS counts only if run 1's LEFT walk passed and the right wheel moved in these walks.** A left walk cut
short by a partner that cannot move also fails HLT_WIRING, and that failure would have nothing to do with the swap.
Run 1 is this cell's control, and the report judges it from the logs.
| R19-DUAL-HEALTH-X, LEFT | 0 of 10 | a start check fires: the start checks cannot see a swap, so a FAIL here is a finding |

### `dual-start-nowalk` with the right hall connector unplugged — B-1

- **Must read:** every start still succeeds (`BM-SSTART ret_ok,TRUE`); `r_fail` has HLT_HALLS ($0001) set, and
  `r_ill_lo + r_ill_hi > 0`.
- **Verdicts:** HEALTH-X RIGHT FAIL 10/10 and LEFT PASS; PROBE, RZSPREAD and PRBFLR PASS on both. WALK is NOT_BUILT.

### `dual-fault` — the fault responses (fault study §7)

Unchanged from pass 1, where the preflight aborted on the dead right board and nothing ran. Every fault is forced
through `testForceFault()`, each trial in its own driver lifetime. Speeds are 40, 80 and 120 × 10⁶, all negative.

| Cell | Judged by | Criterion | Fails if | Control |
|---|---|---|---|---|
| **R19-DUAL-HOOKREST-X** | `BM-FRHOOK`, per motor, **first** | a forced fault at rest (hold off, bridge coasting) latches nothing; the state stays STOPPED for 500 ms | the hook faults an undriven motor | **The hook's own negative control** |
| **R19-DUAL-FORCED-X** | `BM-FRTRIAL outcome`, `BM-ABORT NO_FAULT` | every requested first fault latches within 8 ms | the hook failed to fault a driven motor | HOOKREST |
| **R19-DUAL-RESTFLAT-X** | `BM-FRPHASE PRE/REST` | every phase under 50 mV p-p at rest | a channel swings with nothing turning | measured first |
| **R19-DUAL-COASTEMF-X** | `BM-FRPHASE MOVE`, FR_SHIPPED, FLOAT, 3 speeds | every phase ≥ 50 mV p-p, crossing at the hall rate, while coasting | flat while the halls tick | RESTFLAT |
| **R19-DUAL-SHORTTK-X** | `BM-FRSTAT`, FR_SHIPPED BRAKE against FLOAT | the short stops in fewer ticks than the coast | short ≥ coast at any speed | paired speeds |
| **R19-DUAL-SHORTI-X** | `BM-FRCUR`, `BM-FRWIND` | peak current rises with speed | no rise | **Expected NOMEAS**: the shunt cannot see a short (PL-118) |
| **R19-DUAL-RESYNC-X** | FR_GRADED 25 %, FLOAT, 80 × 10⁶ | exactly one re-sync, FC_LAG, never FAULTED, SPIN_DN then STOPPED, rest within 50–150 % of the ramp's time | any of those | the re-sync count before the fault |
| **R19-DUAL-BLUNT-X** | the second forced fault on a re-synced ramp | reads DCS_FAULTED | the fallback is not taken | — |
| **R19-DUAL-GRADED-X** | `BM-FRSTAT f2_k`: coast, then 10, 25, 50, 100 % | ticks and time to rest never rise as brake % rises; 100 % below the coast | a rise, or no overall fall | **Sizes BRAKE_PCT_DEFAULT (25, provisional)** |
| **R19-DUAL-GRD100-X** | 100 % graded against the full short at 80 × 10⁶ | within 2 ticks | differs by more | — |
| **R19-DUAL-PLATSTOP-X** | `BM-FRPLAT`, power 50: LEFT faulted under FR_SHIPPED, then RIGHT under FR_GRADED | the watched wheel falls to ≤ 10 % of its rate within 2 s | it keeps driving (PL-117) | NOMEAS unless it turned ≥ 10 ticks before |
| **R19-DUAL-FRREST-X** | `BM-FRREST` after each trial | FR_SHIPPED, the lifetime's brake_y, HS_OFF | a restore did not take | — |
| R19-DUAL-B4PULSE-X | — | NOT_BUILT (PL-118) | — | — |

### `t0-stopmode` — the hold rows and the stop states at the wheel (ATTENDED, right wheel)

**Every row waits for you.** After START ROW, nothing is timed until you touch the wheel. A hold row's clock starts at
your first push, and a coast row ends only after the wheel has turned and come to rest (PL-121's fix). DONE or ABORT
ends a row early. A row nobody touches ends after 2 minutes, marked as not done. **FREEREF is emitted first:** if it
fails, the instrument has not shown it can report a coast, and every coast cell is read with that in mind.

| Row | He clicks, then | He should feel | Cell | Pre-registered reading | Fails if |
|---|---|---|---|---|---|
| 1 HOLD-RISE | START ROW, pushes the wheel off where it stopped and holds it, DONE | the resistance **grow** over about ¼ s | R17-T0-HOLDRISE | HS_HOLDING throughout; duty reaches the ceiling within 400 ms of the first displacement. **Records sense_i at the ceiling** | the ceiling is not reached in time, or SLIPPED, LIMITED or FAULTED |
| 2 HOLD-SLIP | START ROW, pushes past a 2 % ceiling, DONE | it **give way**, then a drag that grows with speed | R17-T0-HOLDSLIP | HS_SLIPPED before any DCS_FAULTED; the slip count advances | the hold persists, or FAULTED comes first |
| 3 HOLD-LIMIT | START ROW, a steady push at the ceiling for about 2 s | it hold, then **let go** after about 2 s | R17-T0-HOLDLIMIT | HS_LIMITED within 7 s of the first push | it never hands off |
| 4 COAST AT REST | START ROW, spins briskly, lets go | it spin freely and coast | R17-T0-RESTCOAST | half-rate time ≥ 150 ms | < 150 ms |
| 5 E-STOP AT REST | START ROW, spins briskly, lets go | it resist harder the faster it turns, then stop quickly | R17-T0-RESTSHORT | half-rate time ≤ 60 ms | > 60 ms |
| (4 − 5) | — | — | R17-T0-STOPGAP | ≥ 100 ms apart | < 100 ms |
| 6 FAULT, COAST MODE | START ROW; **hands off**, it drives and faults itself; ABORT if needed | the wheel coasts after the fault | R17-T0-FLTCOAST | half-rate ≥ 150 ms and still FAULTED | either false, or it never reached AT_SPEED |
| 7 FAULT, HOLD MODE | as row 6 | the wheel brakes hard after the fault | R17-T0-FLTSHORT | half-rate ≤ 60 ms and still FAULTED | either false, or it never reached AT_SPEED |
| (6 − 7) | — | — | R17-T0-FLTGAP | ≥ 100 ms apart | < 100 ms |
| 8 DRIVER COG STOPPED | START ROW, spins briskly, lets go | it coast exactly as row 4 did | **R17-T0-FREEREF** | half-rate ≥ 150 ms | < 150 ms |

**PL-116's order-swapped build (`t0-stopmode-fltfirst`) is off this sheet.** Its question assumed a right bridge that
drives. If rows 6–7 block with the bridge shown alive in run 1, the next sheet carries it unconditionally.

---

## What this visit cannot measure, named

- **Any loaded value**: the hold's creep on a slope and its ceiling under load belong to the floor run («#3576»).
- **A phase short's current** (PL-118).
- **The pack voltage**: no sensor is fitted («#3611»).
- **An open motor winding, or a hall pair actually crossed at the connector**: the rig cannot make either. The
  firmware negatives cover a dead switch and a swapped reading.

---

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then every R19 parameter gets a sized
value or a stated reason it has none. The P5 questions go to Stephen, each with its measured benefit:

- Should FR_GRADED become the default?
- Should the hold limits and the fault response become public setters?
- Should a re-synced fault be reported through getError()?
- What should start() do when a check fails? Pass 1 gave this a measured case: ten successful starts over a right
  board that could not drive.
