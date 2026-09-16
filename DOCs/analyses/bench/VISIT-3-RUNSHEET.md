# Visit 3 — run sheet (unattended)

Run each command from the project root, in order. Do the physical steps in bold. I read every log.

**Panic: PHYSICAL BATTERY DISCONNECT.** `emergencyCutoff()` is not a panic button.

**Pull first. Every motion-harness banner must read `src_rev 12`, `fmt 3`** (updated 2026-09-16). The first
Visit 3 attempt ran `src_rev 7`: the Visit 3 commits had not yet reached the remote, so it certified
nothing (`2026-09-16/VISIT-3-RESULTS.md`).

Run steps 1–6 first (unattended), then the attended pair, steps 8–9, below. Step 7 is withdrawn.

---

## What this visit is for

Four repairs are committed and none has been on the bench. Every load below certifies one, and
**nothing below re-measures something Visit 2 already settled.** Times are what Visit 2 actually took,
not the worst-case caps.

| # | Command | Time | Certifies |
|---|---|---|---|
| 1 | `tools/bench-run.sh dual-clock-200` | ~1 min | `CLKFRAME` at 200 MHz — never measured |
| 2 | `tools/bench-run.sh dual-clock-270` | ~1 min | same, at 270 |
| 3 | `tools/bench-run.sh dual-clock-300` | ~1 min | same, at 300 |
| 4 | `tools/bench-run.sh dual-b` | ~5 min | «#3512» C-3, and «#3547»/«#3550»/«#3552» fault reporting |
| 5 | `tools/bench-run.sh dual-c` | ~2 min | «#3546» the e-stop reset (PL-57), and the e-stop hold at the new loop rate |
| 6 | `tools/bench-run.sh char` | ~2 min | rpm still reads true with the sense loop at 128 Hz («#3512») |
| 7 | `tools/bench-run.sh detect-phase2` | ~1 min | «#3505» step 4 — Rev A detection |

About 13 minutes of running, plus the Rev A swap.

---

## Rig for steps 1–6

**Rev B platform · on blocks, both wheels up and free · both motors connected · pack charged**

### Steps 1–3 · the three clock loads

All three were lost at Visit 2 and again at the first Visit 3 attempt, both times to a typed clock value.
**Nothing numeric is typed any more (2026-09-16):** each clock is its own tier name. A tier name with a
typo is refused on screen before anything compiles.

### Step 4 · `dual-b` — **faults on purpose twice**

The ramp sweep faults as it always has. Then, **new at the very end**, after the four distance runs, the
harness provokes one more fault — both wheels commanded from standstill on a hard ramp — and sits
watching for about 6 s while it reads the fault back through the public API. Both wheels jerk and stop.
That is the test working. It runs last on purpose: a fault resets tracking, so it cannot come before the
distance runs.

This load is also where C-3 is measured. At Visit 2 both 10 ft reps aborted at 75 % power and measured
nothing; they run at 50 % now.

### Step 5 · `dual-c` — provoked faults and e-stops

### Step 6 · `char` — nine holds, both wheels turn

---

## Step 7 · Rev A

**Swap to the Rev A platform. Unplug the A motors.** Then `tools/bench-run.sh detect-phase2`.
Nothing should turn.

> **Withdrawn 2026-09-16: this step certifies nothing.** It already ran at Visit 2, and «#3505» step 4 was
> recorded complete (`2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §6, log `143237`). The sheet copied it from a
> stale owed list. A Rev A run cannot tell a working detection fix from a broken one either: a stale read gives
> 0, which is also Rev A's correct answer (`2026-09-12/DETECT-A-EVALUATION.md` §2). If it was run, its log is
> read only for anomalies.

---

## Attended pair (added 2026-09-16, after the PL-64 rebuild)

**Before either:**
- Pull.
- Both banners must read `src_rev 12`.
- Rig: Rev B platform, on blocks, wheels up, both motors connected.

Every screen, with its buttons and keys, is in
[`ATTENDED-PANEL-SCREENS.md`](ATTENDED-PANEL-SCREENS.md), generated from the same table the panel draws.

**The dot at the top right of the panel blinks while the harness runs.** If it stops while a wheel can move,
the harness has stopped. Note the time, and use the battery disconnect if a wheel is driven. It may pause on
the WRITING THE LOG screen; the wheels are released there.

| # | Command | Nothing moves? | What you do |
|---|---|---|---|
| 8 | `tools/bench-run.sh dual-ui` | Nothing moves | Click each button shown and press its key. Then judge each `dual-brake` screen with LOOKS RIGHT (Y) or SOMETHING WRONG (W) at the bottom; the screen's own buttons do nothing there. Close with START. |
| 9 | `tools/bench-run.sh dual-brake` | Both wheels spin | Only if step 8 PASSED. START, then brake the LEFT wheel when told, release when told, hands clear while it drives again. STOP (space bar) stops both wheels on any screen where they can move. Close with START. |

`t0-hand`, `dual-floor` and `detect-phase2` are not owed (VISIT-2-ATTENDED-RESULTS.md §2, §5, §6).

---

## Dropped, and why — so nothing is re-run for its own sake

- **`dual-a`** (the 5 min part A: STOPMODE, LIVE, LADDER). Its one owed item was PL-50, the ladder's
  rate against prediction. **That is now answered without the bench:** «#3548»'s change to the library is
  *comment-only* — not one executable line moved — so the driver produces the same rates Visit 2
  measured, and the only thing that changed is the harness's printed prediction, scaled by exactly 22/23.
  Old ratio × 23/22 puts every rung from 10M up in the 0.99–1.01 window the fix predicted. Recorded under
  PL-50. STOPMODE and every part A sign-off cell passed at Visit 2 against a driver that has not changed
  since. `char` covers the one thing left — rpm through the sense loop, which «#3512» did change.
- **`R2-DETECT-OVERLAP`** — it was a rider on step 7 and **it cannot run**: the gate-input guard that
  skips those two cells is computed in every build with no flag to relax it, so unplugging the motors
  changes nothing. Filed as PL-67. Nothing else waits on it.
- **`dual-ui`, `dual-brake`** — tomorrow, after PL-64.
- **`dual-floor`** — wheels-down, ruled out: every run is wheels-lifted. Finding AC is NOMEAS by that
  ruling, not by a failed run.
- **`scan`** (12 min, the only genuinely long load) and **`t0`** — nothing owed to either this visit.

---

## Stop and tell me if

- a wheel moves during step 7
- anything hangs, smells, or gets hot
- anything happens the sheet didn't say would

Notes go in `BENCH-OBSERVATIONS.md` — what you saw, not what you think it means.
