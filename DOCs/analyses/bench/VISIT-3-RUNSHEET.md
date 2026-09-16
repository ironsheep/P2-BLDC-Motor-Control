# Visit 3 — run sheet

Run each command from the project root, in order. Do the physical steps in bold. I read every log.

**Panic: PHYSICAL BATTERY DISCONNECT.** `emergencyCutoff()` is not a panic button.

Tree: `7bf4aff`, both gates green. Harness `SRC_REV 11`, `FMT 3`.

---

## What this visit is for

Four repairs are committed and none has been on the bench yet. Every load below exists to certify one
or more of them:

| Repair | Certified by |
|---|---|
| «#3548» the drive-pass period — the ladder's rate against prediction (PL-50) | step 1 |
| «#3549» the clock tier refuses a clock it cannot sweep (PL-62) | steps 2–4 |
| «#3512» C-3, the distance and time stops within 8 ms of their limit | step 5 |
| «#3547» + «#3550» + «#3552» fault reporting through the steering object | step 5 |
| «#3546» the e-stop reset (PL-57) | step 6 |
| «#3505» step 4 — Rev A board detection | step 7 |

---

## Rig for steps 1–6

**Rev B platform · on blocks, both wheels up and free · both motors connected · pack charged**

## Unattended — no hands

| # | Command | Notes |
|---|---|---|
| 1 | `tools/bench-run.sh dual-a` | up to 25 min; the two top ladder rungs may fault on purpose |
| 2 | `tools/bench-run.sh dual-clock 200000000` | about 1 min |
| 3 | `tools/bench-run.sh dual-clock 270000000` | about 1 min |
| 4 | `tools/bench-run.sh dual-clock 300000000` | about 1 min |
| 5 | `tools/bench-run.sh dual-b` | up to 25 min; **faults on purpose twice** — see below |
| 6 | `tools/bench-run.sh dual-c` | up to 15 min; provoked faults and e-stops |

**Step 5 is new at the end.** After the four distance runs, the harness deliberately provokes one more
fault — both wheels commanded from standstill on a hard ramp — and then sits watching for about 6 s
while it reads the fault back through the public API. Both wheels will jerk and stop. That is the test
working. It runs last on purpose: a fault resets tracking, so it cannot come before the distance runs.

**Steps 2–4 are the first run of the clock guard.** A clock the tier cannot sweep is now refused before
anything compiles, so a mistyped frequency stops rather than reaching the compiler.

---

## Rev A — steps 7

### 7 · `tools/bench-run.sh detect-phase2` — Rev A, no motion

**Swap to the Rev A platform. Unplug the A motors.** Then run the command. Nothing should turn.

---

## Not in this visit, and why

- **`dual-ui`, `dual-brake`** — the attended pair. `dual-ui` failed itself at Visit 2 and the walkthrough
  is out of step with what the tests need (PL-64). They wait on that rebuild. **Your call** if you want
  them anyway.
- **`dual-floor`** — wheels-down, ruled out: every run is wheels-lifted. Finding AC is NOMEAS by that
  ruling, not by a failed run.
- **`R2-DETECT-OVERLAP`** — it was on my list as a rider on step 7 and **it cannot run**: the gate-input
  guard that skips those two cells is computed in every build with no flag to relax it, so unplugging the
  motors changes nothing. Filed as PL-67. Nothing else waits on it.
- **`scan`, `char`, `t0`** — nothing owed to them this visit.

---

## Stop and tell me if

- a wheel moves during step 7
- anything hangs, smells, or gets hot
- anything happens the sheet didn't say would

Notes go in `BENCH-OBSERVATIONS.md` — what you saw, not what you think it means.
