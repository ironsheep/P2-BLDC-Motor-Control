# Bench Pass 1 — run sheet

Run the commands. Do the physical steps. Write down only what the meter tells you.
**Everything else — banners, counts, verdicts — I read out of the logs afterwards.**

**Panic: PHYSICAL BATTERY DISCONNECT.** `emergencyCutoff()` is not a panic button.
The pack is connected for every step; the P2 is powered from it.

---

## Status

| | step | state |
|---|---|---|
| 1 | B · `detect` | ✅ done — 21:00 |
| 2 | B · `detect-lib` | ✅ done — 21:01 |
| 3 | B · `detect-phase2` · motors unplugged | ✅ done — 21:02 |
| 4 | B · `char` | ❌ **blocked** — PLOT panel was blank. Defect found and being fixed; do not re-run yet. |
| 5 | A · `detect-lib` | ⬜ not run |
| 6 | A · `detect-phase2` · motors unplugged | ⬜ not run |

Logs 1–3 are good and are being analysed. **Nothing to redo.**

---

## Remaining steps

### Step 5 — swap to the A boards · NO MOTOR MOVEMENT

```bash
tools/bench-run.sh detect-lib
```

### Step 6 — ⚠ UNPLUG THE A MOTORS ⚠

```bash
tools/bench-run.sh detect-phase2
```

### Step 4 (re-run) — B boards · MOTORS CONNECTED · wheels will turn

**Wait for me** — the panel defect is not fixed yet. When it is:

```bash
tools/bench-run.sh char
```

A window opens. At each hold: read the meter, write the row, click **GO AHEAD** (or press **G**
with the window focused). The button stays inert for 25 s after the motor settles; that is
deliberate, it is waiting out your meter's screen rotation.

**Say the pack voltage before you start and write it here: __________**

| # | Hold | Amps |
|---|---|---|
| 0 | quiescent zero | |
| 1 | LEFT forward ¼ | |
| 2 | LEFT reverse ¼ | |
| 3 | RIGHT forward ¼ | |
| 4 | RIGHT reverse ¼ | |
| 5 | LEFT forward ½ | |
| 6 | LEFT reverse ½ | |
| 7 | RIGHT forward ½ | |
| 8 | RIGHT reverse ½ | |

While the wheels are turning, three things only you can see:

1. Does **Ah/Wh** reset with the peaks, or separately? ______
2. **Quiescent zero** — V, A, W with the rail on, motors stopped? ______
3. Does **Ap latch** after the current drops, or decay? ______

---

## Stop and tell me if

- A wheel turns on the **A** boards — the one hard constraint there
- Anything hangs, smells, or gets hot
- A step needs a source edit to proceed
- Anything happens that the sheet did not say would

Free-text notes go in `BENCH-OBSERVATIONS.md`. Say what you saw; don't classify it.

---

## Tiers

`t0` · `detect` · `detect-lib` · `detect-phase2` · `char` · `char-nopanel`

`tools/bench-run.sh <tier>` echoes both commands before running them.
Logs land in `src/logs/` by timestamp.
