# Visit 10 — run sheet, pass 6 (stop reasons and the event log at last; the walk, path-limiter and gate-pin fixes certified)

**Task:** «#3613» runs it. **Plan:** `BENCH-READINESS-SPRINT-PLAN.md`, R20.6.

**Built for this pass:**
- «#3610» PL-137: the walk no longer runs under the path limiter.
- «#3622» PL-141: the limiter engages only for a wheel behind its partner, and never scales to zero (this also
  restores SR_BLOCKED under steering).
- «#3623» PL-138: every gate is held off through a driver's start, and released before `stop()`'s cogstop.
- «#3613»:
  - a refused start prints its probe mV (`BM-RPROBE`, `T0-25,rprobe`);
  - T0-25 falls back to the LEFT wheel if the right is refused;
  - START prints `BM-FRONTST` after each walk (PL-140).

**Done so far:**
- Pass 3 (09-24): the fault fallback, graded short, hold rise, start checks, REST window and rest-zero band certified.
- Pass 4 (09-25 11:41): the winding check certified with its negative.
- Pass 5 (09-25 19:52), [evaluation](2026-09-25/VISIT-10-PASS5-EVALUATION.md):
  - the right certified its fault cells;
  - refusal, opt-out and retry certified;
  - PL-137 and PL-141 were found;
  - PL-120 struck twice and outlasted a reload, so T0-25 was voided.

---

## ⛔ First: PUSH, then pull at the bench

`main` is ahead of origin. **Push from the authoring tree first**, then pull at the bench. `git log --oneline -1 -- src/`
at the bench must show **b262f2e** or later.

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| every `dual-*` tier | `BM-BANNER,...,src_rev,51,fmt,34` and `BM-BUILD ... drv_rev,29`. Anything lower means an old tree: stop and report |
| `t0-stopreason` | the t0 banner at `src_rev 19`, saying `(THE LEFT IF THE RIGHT IS REFUSED)` |
| `dual-start` | part `START`; `BM-SKBUILD ... walks,10,no_walk,FALSE ... neg,NONE` |
| `dual-start-swapneg` | part `START`; `BM-SKBUILD ... neg,SWAP` |
| `dual-d` | part `D`; its STEERSEG `BM-PLAN` names `PL138` |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification.** First measure of every stop reason and event-log cell (T0-25). It certifies:<br>• the walk fix (PL-137): 10 walks per wheel, plus the swapped-left negative with a healthy right;<br>• the path-limiter fix (PL-141): no engage at a healthy steering start;<br>• the gate-pin fix (PL-138): RESTCOAST;<br>• part D's owed cells: ORDERED..DIRSIGN, the LIMIT segment, EV-FOLDBACK/CLIMIT.<br>If PL-120 strikes, the refusal now records the dead bridge's per-phase millivolts. |
| **Hardware risk** | • `t0-stopreason`: **an e-stop brakes one wheel abruptly.**<br>• `dual-start-swapneg`: **the left wheel may jerk or buzz for up to 2 s at a time.**<br>• `dual-d`: **the wheels stop dead**; an e-stop is latched; **the current limit is lowered until the motor cannot turn**; and **twice the platform is switched off while the wheels spin**, the second time straight back on.<br>**Wheels up throughout. Hands off in every tier. Panic: physical battery disconnect.** |
| **Who can observe** | No tier needs anyone. |
| **Runs that carry state** | None across runs. PL-120, if it strikes, can outlast a reload for about 80–100 s. The t0 fallback and the refusal records cover that; nothing waits on it. |
| **Run length** | `t0-stopreason` under 1 minute. `dual-start` about 1. `dual-start-swapneg` under 1. `dual-d` about 2 to 2.5 (RESTCOAST adds about 25 s, at most about 60). **Total about 5–6 minutes.** |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack, 270 MHz. `test_bench_t0` T0-25; `test_bench_dual` part START (two builds) and part D. |

---

## The commands — four, all hands off, about 6 minutes

```bash
tools/bench-run.sh t0-stopreason        # 1: FIRST. One wheel driven slowly and stopped every way a program can, including one abrupt e-stop (the LEFT if the right won't start)
tools/bench-run.sh dual-start           # 2: 10 starts; the wheels twitch at the first two, and at EVERY start both turn a little one way and back
tools/bench-run.sh dual-start-swapneg   # 3: Fakes crossed LEFT hall wires; the LEFT wheel may jerk or buzz briefly, 3 times
tools/bench-run.sh dual-d               # 4: Stops dead, holds an e-stop, lowers the current limit until the wheels can't turn; twice switches the platform off while the wheels spin
```

**No run depends on another run's result, and nothing needs rewiring or touching.**

**Not run this pass, and why:**
- **`dual-fault-rightfirst`:** the right certified at pass 5, and nothing under the fault responses changed. RESTFLAT
  (PL-139) rides with the next fault-response change.
- **`dual-start-phaseneg`:** refusal, opt-out and retry certified 3/3, 6/6, 3/3. The start checks are unchanged.
- **`t0-stopmode`, `dual-start-nowalk`:** attended, and they add only EV-HOLD / EV-HALLILL, whose paths did not change.
- **The pack tier:** no sensor is fitted («#3611»).

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). The cells print their own verdicts.

### 1 · `t0-stopreason` — every stop reason and the event log (never measured)

| Cell | Decides it |
|---|---|
| R20-T0-SR-COMMANDED, -ATLIMIT, -ESTOP, -LINKLOST | each reason reads correctly, and its negative reads `SR_COMMANDED` or `SR_NONE` (`DRIVER-REPORTING-DESIGN.md` §6) |
| R20-T0-EV-STOP | exactly `41 42 41 47 41 46 41`, in rising ms |
| R20-T0-EV-LOST | EV_LOST first, counting what was dropped; 16 kept. **A dropped event never reads as none** |
| R20-T0-EV-TOTAL, -2COG | totals count drained and dropped alike; two reading cogs each see every event |
| Which wheel | `T0-25,fallback` present means the right was refused. Its `T0-25,refused` / `rprobe` lines are PL-120's signature: phases **below** the 56–62 mV floor while driven mean the high side is lost |

### 2 · `dual-start` — the walk fix

| What | Decides it |
|---|---|
| **R19-DUAL-WALK-X**, per wheel | **0 of 10 failed walks.** Any `BM-SKWLEG` ending `OTHER` fails the PL-137 fix |
| R20-DUAL-NOREFUSE | 10 of 10 start. A refusal that does happen must carry `BM-RPROBE` for both wheels (PL-120) |
| PL-140 (not a cell) | each `EV LATE_PASS` placed against the lifetime's `BM-FRONTST` (`max_us`, `late`) |
| RETRY, EV-WALKGUARD, EV-HALLMISSED negatives; WINDR, WINDSPR, HEALTH, RZSPREAD, PROBE, PRBFLR, PACK | as pass 5 |

### 3 · `dual-start-swapneg` — the walk fix's other side

| What | Decides it |
|---|---|
| **R19-DUAL-WALK-X RIGHT** | **0 of 3**: the healthy right passes while its partner is miswired (pass 5: 2 of 3 failed, PL-137) |
| R19-DUAL-SWNEG-X LEFT | the swapped left still fails every walk |
| R20-DUAL-EV-WALKGUARD LEFT (positive) | one EV_WALK_GUARD per swapped walk, at or over the guard's limit |

### 4 · `dual-d` — the path limiter, the gate pins, and part D's owed cells

| What | Decides it |
|---|---|
| **R20-DUAL-EV-PATH, negative** | **no EV_PATH_LIMIT in STEERSEG** (pass 5 engaged at every healthy start: PL-141). The positive half is expected NOMEAS wheels-up: the BLOCK step stalls both wheels together, and no wheel falls behind |
| **R20-DUAL-RESTCOAST**, per wheel | the restarted platform keeps **≥ 80 %** of the same run's free coast over 250 ms. Its negative is the pre-fix driver, which parked with every low side ON |
| ORDERED, TIMESTOP, CMDTIMEOUT, DIRSIGN | owed since pass 5 (NOT_REACHED); as Visit 8 |
| The LIMIT segment's steps, R20-DUAL-EV-FOLDBACK, -EV-CLIMIT | FOLDBACK: an engage/release pair in the lowered-limit steps. CLIMIT NOMEAS if no wheel derates wheels-up |
| R16-DUAL-BLOCKED-D | still cannot fail on a lifted rig (Visit 8 F-3). SR_BLOCKED stays with the floor run («#3576») |
| R20-T0-EV-LATE, FRONTST, LAGBND | as pass 5 |

---

## What this visit cannot measure, named

- **SR_BLOCKED and the path limiter's positive half:** a lifted wheel cannot be blocked alone. Both belong to the
  floor run («#3576»).
- **PL-141's turn-from-rest case:** STEERSEG may or may not command a turn from rest. `PATH_BEHIND_PERMILLE` is sized
  from any gap this pass shows, else on the floor.
- **PL-120's cause:** this pass can only record the signature if it strikes.
- **The hold's events, the hall-illegal event, the pack voltage:** their tiers are not run.

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then:
- close «#3621» if every T0-25 cell certifies;
- close «#3610»'s PL-137 if the walk and swap cells pass;
- close PL-141 and PL-138 on EV-PATH and RESTCOAST.
