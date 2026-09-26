# Visit 10 — run sheet, pass 7 (the path limiter's hunt fixed, one "following" meaning, and PL-120's recovery timed)

**Task:** «#3613» runs it. **Plan:** `BENCH-READINESS-SPRINT-PLAN.md`, R20.6.

**Built for this pass (DRIVER_REV 30; `test_bench_dual` SRC_REV 52; `test_bench_t0` SRC_REV 20):**
- PL-144: the steering path limiter releases only once both fields have reached the present scale, so it no longer
  cycles between 8 % and 100 %. New cell R20-DUAL-PATH-HUNT.
- PL-147: the following percentage is of the user's command, so it agrees with the limiter's reading (R18-DUAL-NOTFOL-D).
- PL-146: part D's event drains wait for both drivers to stop before settling (R20-DUAL-EV-FOLDBACK).
- R20-DUAL-EV-PATH's positive precondition: a wheel held while its commanded partner is not.
- PL-120: after a refused right, T0-25 tries the right every 10 s for up to 3 min and prints when it comes back.

**Done so far:**
- Passes 3–5 (09-24/25): the fault responses on both wheels, the hold, the start checks, the winding check, and
  refusal / opt-out / retry certified.
- Pass 6 (09-26 12:33), [evaluation](2026-09-26/VISIT-10-PASS6-EVALUATION.md):
  - T0-25 certified, 8 of 8 on the left;
  - the walk fix (PL-137), the gate-pin fix (PL-138) and the no-engage-at-start fix (PL-141) certified;
  - PL-120 struck at the first load, after the reseat, and was back in under 2 minutes;
  - PL-144 and PL-147 found, now built.

---

## ⛔ First: PUSH, then pull at the bench

`main` is ahead of origin. **Push from the authoring tree first**, then pull at the bench. `git log --oneline -1 -- src/`
at the bench must show the commit that carries **DRIVER_REV 30** (this sheet's commit or later).

## ⭐ Before anything: note the time you connect the pack

**Write down the clock time when you connect the battery to the platform**, and whether it was connected already.
PL-120 struck on the first load of the day at passes 4 and 6. The log alone cannot say whether that load came right
after power-on.

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `t0-stopreason` | the t0 banner at `src_rev 20` |
| every `dual-*` tier | `BM-BANNER,...,src_rev,52,fmt,34` and `BM-BUILD ... drv_rev,30`. Anything lower means an old tree: stop and report |
| `dual-start` | part `START`; `BM-SKBUILD ... walks,10,no_walk,FALSE ... neg,NONE` |
| `dual-d` | part `D`; `SIGNOFF-DECL ... R20-DUAL-PATH-HUNT` present |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of DRIVER_REV 30: PL-144 (PATH-HUNT), PL-147 (NOTFOL-D), PL-146 (EV-FOLDBACK), EV-PATH's positive. It re-proves STEERSEG, RESTCOAST and the walk on the changed limiter. **Measurement:** PL-120's recovery time, if the right is refused at load, placed against the pack's power-on time. |
| **Hardware risk** | • `t0-stopreason`: **an e-stop brakes one wheel abruptly.**<br>• `dual-d`: **the wheels stop dead**; an e-stop is latched; **the current limit is lowered until a wheel cannot keep up**; and **twice the platform is switched off while the wheels spin**.<br>**Wheels up throughout. Hands off in every tier. Panic: physical battery disconnect.** |
| **Who can observe** | No tier needs anyone. One note from you: the pack's power-on time (above). |
| **Runs that carry state** | None across runs. PL-120, if it strikes, can outlast a reload for up to about 2 minutes. `t0-stopreason` now waits it out and times it. |
| **Run length** | `t0-stopreason` under 1 minute, or up to about 4 if the right is refused. `dual-start` about 1. `dual-d` about 2 to 2.5. **Total about 4–7 minutes.** |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack, 270 MHz. `test_bench_t0` T0-25; `test_bench_dual` part START and part D. |

---

## The commands — three, all hands off

```bash
tools/bench-run.sh t0-stopreason        # 1: FIRST, right after power-on if you can. One wheel driven slowly and stopped every way, one abrupt e-stop. If the right is refused, it keeps trying the right for up to 3 minutes
tools/bench-run.sh dual-start           # 2: 10 starts; the wheels twitch at the first two, and at EVERY start both turn a little one way and back
tools/bench-run.sh dual-d               # 3: Stops dead, holds an e-stop, lowers the current limit until a wheel can't keep up; twice switches the platform off while the wheels spin
```

**No run depends on another run's result, and nothing needs rewiring or touching.**

**Not run this pass, and why:**
- **`dual-start-swapneg`:** certified 3/3 at pass 6, and the walk runs outside the changed limiter.
- **`dual-fault-rightfirst`:** the fault path is unchanged. RESTFLAT (PL-139) rides with the next fault-response change.
- **`dual-start-phaseneg`, `t0-stopmode`, `dual-start-nowalk`, the pack tier:** unchanged paths, or no sensor fitted.

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). The cells print their own verdicts.

### 1 · `t0-stopreason`

| What | Decides it |
|---|---|
| T0-25's eight cells | as pass 6 (the reporting code did not change): a regression check |
| PL-120 (not a cell) | if refused: `T0-25,recover,try,N,ms,...` lines and `T0-25,recovered,...,ms,M`, each try with its `refused`/`health` and `rprobe` lines. Read against your power-on time. `recovered,...,ms,NA` means it outlasted 3 minutes |

### 2 · `dual-start`

| What | Decides it |
|---|---|
| R19-DUAL-WALK-X, per wheel | 0 of 10; no `BM-SKWLEG` ending `OTHER` |
| No path engage at a start | no `EV PATH_LIMIT` in the run |
| Every other START cell | as pass 6 |

### 3 · `dual-d`

| What | Decides it |
|---|---|
| **R20-DUAL-PATH-HUNT** | **exactly 1** engage/release pair in the behind wheel's log in the BLOCK step. Pass 6's pre-fix driver logged 5, which is the negative. NOMEAS if no wheel is seen held while its partner is not |
| **R18-DUAL-NOTFOL-D**, the held wheel | PASS: both readings below their thresholds together (pass 6: 84 ‰ against 105 %) |
| **R20-DUAL-EV-FOLDBACK** | 0 bad: every LIMIT stage's fold-back log engage, release … ending on a release |
| **R20-DUAL-EV-PATH** | positive on the new precondition, and still no engage in STEERSEG |
| R20-DUAL-RESTCOAST, STEERSEG steps, LAGBND, FRONTST | as pass 6 |
| R16-DUAL-WTIMSTOP-D | judged as declared. Its 20 ms slack is known to sit inside its own spread (PL-145), so a FAIL up to about +30 ms is read against that |
| DERATE, CLIMIT, BLOCKED | NOMEAS wheels-up, as declared |

---

## What this visit cannot measure, named

- **SR_BLOCKED and how the limiter settles on the floor:** the floor run («#3576»).
- **PL-120's cause:** this pass times the recovery. The board's high side is the reading it cannot see into.
- **The hold's events, the hall-illegal event, the pack voltage:** their tiers are not run.

## Open questions

- What does PL-120's first-load failure follow, and how long does it last?
- Does the fixed limiter hold one engage per shortfall?

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then close PL-144, PL-146 and PL-147 on
their cells.
