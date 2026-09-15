# Visit 2 — run sheet

Run each command from the project root, in order. Do the physical steps in bold. I read every log.

**Panic: PHYSICAL BATTERY DISCONNECT.** `emergencyCutoff()` is not a panic button.

---

## Rig for steps 1–13

**Rev B platform · on blocks, both wheels up and free · both motors connected · pack charged**

## Unattended — no hands

| # | Command | Notes |
|---|---|---|
| 1 | `tools/bench-run.sh dual-a` | up to 25 min; the two top ladder rungs may fault on purpose |
| 2 | `tools/bench-run.sh dual-clock 200000000` | about 1 min |
| 3 | `tools/bench-run.sh dual-clock 270000000` | about 1 min |
| 4 | `tools/bench-run.sh dual-clock 300000000` | about 1 min |
| 5 | `tools/bench-run.sh dual-b` | up to 20 min; faults on purpose |
| 6 | `tools/bench-run.sh dual-c` | up to 15 min; provoked faults and e-stops |
| 7 | `tools/bench-run.sh t0` | nothing turns |
| 8 | `tools/bench-run.sh char` | both wheels turn |
| 9 | `tools/bench-run.sh scan` | up to 30 min |

## Attended

### 10 · `tools/bench-run.sh t0-hand` — no motor power

**Click the panel. Press S. Turn the RIGHT wheel (P16 board) by hand, 3 full turns, clockwise seen from the
hub. Press SPACE.**

### 11 · `tools/bench-run.sh dual-ui` — nothing moves

**Click the panel. Do what it asks:** click each button shown, press each key named, then read each screen
(START = reads right, SKIP = something is wrong). The last screen says **PASSED** or **FAILED**; click START
to close.

**FAILED → skip 12 and 13.** They run at the next visit.

### 12 · `tools/bench-run.sh dual-brake` — wheels up

**Click START. When the panel says so, brake the LEFT wheel (P32 board) and hold it until it says RELEASE.
Release, step back, hands clear** — the harness drives both wheels again when the countdown ends.

### 13 · `tools/bench-run.sh dual-floor` — wheels down

**Lower the platform to the floor, space clear.** Click START. It drives about 2 s; STOP or SPACE any time.
Answer which way it turned.

### 14 · `tools/bench-run.sh detect-phase2` — Rev A, no motion

**Swap to the Rev A platform. Unplug the A motors.** Then run the command.

---

## Stop and tell me if

- a wheel moves during step 10, 11 or 14
- anything hangs, smells, or gets hot
- anything happens the sheet didn't say would

Notes go in `BENCH-OBSERVATIONS.md` — what you saw, not what you think it means.
