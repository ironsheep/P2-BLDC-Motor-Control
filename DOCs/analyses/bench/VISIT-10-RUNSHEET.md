# Visit 10 — run sheet, pass 5 (the right wheel diagnosed where it fails; stop reasons, events and start refusal certified)

**Task:** «#3613» runs it. **Built by:**
- «#3621»: stop reasons, the event log, start refusal with retries, public fault and hold setters, the fold-back counter.
- «#3613»: PL-136, a wheel dead at pre-flight retried and diagnosed.
- «#3610»: PL-137, each wiring-walk leg recorded.

**Plan:** `BENCH-READINESS-SPRINT-PLAN.md`, R20.6. **Design and cells:** `DOCs/plans/DRIVER-REPORTING-DESIGN.md` §6 and its build notes.

**Done so far:**
- Pass 3 (09-24, three evaluations under `2026-09-24/` and `2026-09-25/`):
  - certified the fault fallback, the graded short (BRAKE_PCT 10), the hold's rise, the start checks, the REST window and the rest-zero band;
  - the right wheel's fault cells were owed (PL-120).
- 11:41 pass 4 [evaluation](2026-09-25/VISIT-10-PASS4-EVALUATION.md):
  - the winding check certified on both wheels (363–460 mΩ) with its negative;
  - the right wheel died on its first drive and was never retried (PL-120, PL-136);
  - one false wiring-walk FAIL on the left (PL-137).

---

## ⛔ First: PUSH, then pull at the bench

`main` is ahead of origin. **Push from the authoring tree first**, then pull at the bench. `git log --oneline -1 -- src/`
at the bench must show **57fe70a** or later.

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| every `dual-*` tier | `BM-BANNER,...,src_rev,47,fmt,31` and `BM-BUILD ... drv_rev,24`. Anything lower means an old tree: stop and report |
| `dual-fault-rightfirst` | part `FRESP`; `BM-FRDIAG ... right_first,TRUE,pf_tries,3,pf_gap_ms,1_000` |
| `dual-start` | part `START`; `BM-SKBUILD ... walks,10,no_walk,FALSE ... neg,NONE ... wd_walk_ms,4_134` |
| `dual-start-phaseneg` | part `START`; `BM-SKBUILD` negative `PHASE`; 12 lifetimes |
| `dual-start-swapneg` | part `START`; `BM-SKBUILD` negative `SWAP` |
| `dual-d` | part `D` |
| `t0-stopreason` | the t0 banner at `src_rev,18`; test T0-25 only |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification and diagnosis.** It certifies every R20.1 mechanism on the bench: stop reasons, the event log, start refusal and its retries, and the fold-back counter. It diagnoses PL-120 wherever it strikes, because a wheel dead at pre-flight is now retried at once, dumped mid-drive, traced per phase, and then probed. It re-runs every right-wheel fault cell and the platform stop. It catches the wiring walk's false FAIL in its own record, over 10 walks. It measures the steering front cog's worst pass with the new event writes. |
| **Hardware risk** | `dual-fault-rightfirst` **faults the wheels on purpose at up to about 220 rpm**, and each stops by a short, a coast, a ramp or the graded short. **Run it on the pack.** `dual-d` stops the wheels dead, latches an e-stop, and **lowers the current limit until the motor cannot turn.** `t0-stopreason` includes an **e-stop that brakes the right wheel abruptly.** `dual-start-swapneg`: **the left wheel may jerk or buzz for up to 2 s at a time.** **Wheels up throughout. Hands off in every tier. Panic: physical battery disconnect.** |
| **Who can observe** | No tier needs anyone. |
| **Runs that carry state** | None across runs. |
| **Run length** | `dual-fault-rightfirst` about 6 minutes: about 8.5 if the right needs the 20 s probe, at most about 10.5. `dual-start` about 1. `dual-start-phaseneg` about 2. `dual-start-swapneg` under 1. `dual-d` about 1.5. `t0-stopreason` under 1. **Total about 13–17 minutes.** |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack, 270 MHz. `test_bench_dual` parts FAULTRESP (right first), START (three builds) and D; `test_bench_t0` T0-25. |

---

## The commands — six, all hands off, about 15 minutes

```bash
tools/bench-run.sh dual-fault-rightfirst  # 1: On the pack. Faults each wheel on purpose at speed, RIGHT wheel first. If a wheel won't turn at the start, the program retries it by itself (up to ~2 min)
tools/bench-run.sh dual-start             # 2: 10 starts; the wheels twitch at the first two, and at EVERY start both turn a little one way and back
tools/bench-run.sh dual-start-phaseneg    # 3: 12 starts with a faked dead LEFT motor wire; 3 are refused on purpose ("start refused" lines are expected)
tools/bench-run.sh dual-start-swapneg     # 4: Fakes crossed LEFT hall wires; the LEFT wheel may jerk or buzz briefly, 3 times
tools/bench-run.sh dual-d                 # 5: Stops dead, holds an e-stop, lowers the current limit until the wheels can't turn, then restores it
tools/bench-run.sh t0-stopreason          # 6: The RIGHT wheel driven slowly and stopped every way a program can, including one abrupt e-stop
```

**No run depends on another run's result, and nothing needs rewiring or touching.**

**Not run this pass, and why:**
- **`dual-fault` (left first):** its case is on disk three times.
- **`t0-stopmode`** (attended): it would only add R20-T0-EV-HOLD, a consistency check of the hold's events. That check prints NOMEAS here and rides along the next time a hold change needs the tier (overlay P10).
- **`dual-start-nowalk`** (attended, hall connector unplugged): it would only add R20-DUAL-EV-HALLILL, which prints NOMEAS here for the same reason.
- **The pack-voltage tier:** the sensor is not fitted yet («#3611»). R20-PACK-EV prints NOMEAS / NOT_BUILT.

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). The cells print their own verdicts. Each cell's exact negative is
in `DRIVER-REPORTING-DESIGN.md` §6 and the part 3 build notes; the lines below are what the report judges.

### 1 · `dual-fault-rightfirst` — PL-120 where it strikes, and every right-wheel cell

| What | Decides it |
|---|---|
| **PL-120's stage**, from `BM-FRRECSUM r_pf` | `NO_FAIL`: the right drove. `RETRY`: a transient first-drive failure. `PROBE`: time inside one program clears it. `DEAD`: only a reload clears it. **Falsifier of the build:** `r_pf,NO_FAIL` after a `BM-PREFLT ... RIGHT ... moved,FALSE` |
| **PL-120's signature**, from the right's PREFLT `BM-TRACE`/`BM-TS` (`u,v,w,i,d`) against the left's healthy trace and the right's own coasting floor (56–62 mV) | **Pre-registered, corrected 2026-09-25 before any pass 5 log was read** (desk read, PL-120 entry): the earlier sheet named *low sides off*, but pass 1 and 21:21 read phases **below** the coasting floor, which only a conducting low side can do. So: phases **below the floor** (10–30 mV) with `i` near 0 and `d` rising → **high-side drive lost** (low sides working): the board's high-side gate supply or the high-side P2 outputs. Phases **at or above the floor**, or pinned high → low sides not conducting. A brief rise at the start (21:21 read 2,194 mV) then a fall below the floor fits a high side that conducts and then loses its gate drive |
| The right's fault cells (BLUNT, GRADED, GRD100, RESYNC, RESTFLAT, SHORTTK, COASTEMF, FRREST, HOOKREST, FORCED) | as pass 3; the left's pass 3 values are the comparison |
| **PLATSTOP** and **R20-DUAL-SR-PARTNER** | never yet measured: the other wheel stops, and it reads `SR_PARTNER` |
| R20-DUAL-SR-FAULT, R20-DUAL-SR-FLOST | the re-synced trial reads `SR_FAULT_CONTROLLED`; the hard ones read `SR_FAULT_LOST`; each is the other's negative |
| **R20-DUAL-FRONTST-EV** | the steering front cog's worst pass ≤ 950 µs, 0 late passes, stack under its allocation |

**Pre-registered:** the left reproduces pass 4's chains within hall quantisation, since nothing under them changed.

### 2 · `dual-start` — the walk caught in the act, and start refusal's positive

| What | Decides it |
|---|---|
| R19-DUAL-WALK-X, per wheel, now over 10 walks | 0 failed walks. A false FAIL is now read from its `BM-SKWLEG` pair (below) |
| **PL-137's reading**, from `BM-SKWLEG` (not a cell) | limit tracked ticks > the true distance from the post → hall chatter counted twice; settle ≠ end → the rotor moved after the judgement read; a TIMEOUT end or a large lag-held count → a stall; limit at 6–7 with the settle at 5 → spring-back |
| R20-DUAL-NOREFUSE | 10 of 10 starts return ≥ 0 |
| R20-DUAL-RETRY (positive half) | no start reports a recovered check and no EV_CHECK_RETRY: a spurious retry fails it |
| R20-DUAL-EV-WALKGUARD, -HALLMISSED (negative halves) | 0 guard events and 0 hall events on the healthy walks |
| WINDR, WINDSPR, HEALTH, RZSPREAD, PROBE, PRBFLR, PACK | as pass 4 (363–460 mΩ; wheels within 20 %) |

### 3 · `dual-start-phaseneg` — refusal, opt-out and retry

| What | Decides it |
|---|---|
| **R20-DUAL-REFUSE** | the 3 refusal starts return −1 with `ERR_START_CHECK_FAILED` for the platform and the LEFT, and `getHealth()` names exactly the withheld phase |
| **R20-DUAL-OPTOUT** | the opt-out starts return ≥ 0 with the same bit failed. REFUSE and OPTOUT are each other's control |
| **R20-DUAL-RETRY** (positive half) | the withhold-first starts return ≥ 0, report the withheld bit as recovered, and log EV_CHECK_RETRY |
| PHNEG-X, WINDNEG-X | as pass 4, judged on the 6 opt-out starts |

### 4 · `dual-start-swapneg` — the event halves of the wiring negative

| What | Decides it |
|---|---|
| R20-DUAL-EV-WALKGUARD (positive half) | each swapped LEFT walk the guard ends logs EV_WALK_GUARD with a value at or over the guard's limit |
| R20-DUAL-EV-HALLMISSED (positive half) | the sum of the LEFT's EV_HALL_MISSED values equals its missed-count growth |
| the existing swap negative's cells | as pass 2 |

### 5 · `dual-d` — fold-back and the limit events

| What | Decides it |
|---|---|
| **R20-DUAL-EV-FOLDBACK** | an engage/release pair in the lowered-limit steps; none at default limits |
| R20-DUAL-EV-CLIMIT | events match what the derate step saw. **NOMEAS if no wheel derates wheels-up**; it then moves to the floor run |
| R20-DUAL-EV-PATH | an engage/release pair in the blocked step, and none in STEERSEG. **NOMEAS if no wheel falls short** |
| R20-T0-EV-LATE | a late pass if and only if an EV_LATE_PASS. The positive side is NOMEAS while late stays 0 |
| the part D cells | as Visit 8 |

### 6 · `t0-stopreason` — every stop reason a lifted wheel can show, and the event log

| Cell | Decides it |
|---|---|
| R20-T0-SR-COMMANDED, -ATLIMIT, -ESTOP, -LINKLOST | each reason reads correctly, and its negative reads `SR_COMMANDED` or `SR_NONE` as §6 states |
| R20-T0-EV-STOP | exactly `41 42 41 47 41 46 41`, in rising ms |
| **R20-T0-EV-LOST** | EV_LOST comes first, counts what was dropped, and 16 are kept. **A dropped event never reads as none** |
| R20-T0-EV-TOTAL, -2COG | the totals count drained and dropped alike; two reading cogs each see every event |

---

## What this visit cannot measure, named

- **SR_BLOCKED:** a lifted wheel cannot be blocked (PL-106). It belongs to the floor run («#3576»).
- **The hold's events (EV-HOLD) and the hall-illegal event (EV-HALLILL):** their tiers are attended and not run this pass.
- **The pack voltage:** no sensor is fitted.
- **Anything loaded:** the hold's creep, the fault responses under load, and the path limiter on a real platform.
- **Whether the right bridge's cause is ours or the board's.** This pass can only locate it: low sides against everything else, and transient against persistent.

---

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then:
- **If the right wheel's fault cells certify,** land FR_GRADED as the default (Stephen, *"yes A"*, conditional on this pass). It is one constant and a driver revision.
- Size START_CHECK_RETRIES and the retry gap from what the refusal and retry cells saw.
- Read PL-137's cause from the leg records, and fix it.
