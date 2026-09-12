# Bench Pass 1 — run sheet

Run the commands. Do the physical steps. Write down what the meter says.
**Banners, counts, verdicts — I read those out of the logs.**

**Panic: PHYSICAL BATTERY DISCONNECT.** The pack is connected for every step; the P2 runs off it.

---

## Status

| | step | state |
|---|---|---|
| 1 | B · `detect` | ✅ 21:00 |
| 2 | B · `detect-lib` | ✅ 21:01 |
| 3 | B · `detect-phase2` · motors unplugged | ✅ 21:02 |
| 4 | B · `char` | 🔁 **re-run — panel rebuilt** |
| 5 | A · `detect-lib` | ⬜ |
| 6 | A · `detect-phase2` · motors unplugged | ⬜ |

Logs 1–3 are good. Nothing to redo. **B is still the connected rig, so do step 4 first — one board swap.**

---

## Step 4 — B boards · MOTORS CONNECTED · wheels will turn

**Pack voltage, before you start: __________**

```bash
tools/bench-run.sh char
```

**First: does the panel look right?** You should see a dark 640×400 window — amber title bar,
a wide caption strip reading `HOLD 1 of 9 - QUIESCENT ZERO`, a big amber countdown at the left,
and a grey **GO AHEAD (WAIT)** button at the right that turns green.

**If it is blank, tiny, or garbled — stop, Ctrl-C, and run this instead:**

```bash
tools/bench-run.sh char-nopanel
```

Same run, no window: the terminal prints `BC-UI,hold,...,counter,<n>,btn,<n>` and you advance
with **G**. `btn,1` means live. Don't spend bench time on the panel.

Each hold: read the meter, write the row, click **GO AHEAD** or press **G** (window focused).
The button is inert for 25 s after the motor settles — that is waiting out your meter's rotation.

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

While the wheels turn — three things only you can see:

1. Does **Ah/Wh** reset with the peaks, or separately? ______
2. **Quiescent zero** — V, A, W, rail on, motors stopped? ______
3. Does **Ap latch** after the current drops, or decay? ______

---

## Step 5 — swap to the A boards · NO MOTOR MOVEMENT

```bash
tools/bench-run.sh detect-lib
```

## Step 6 — ⚠ UNPLUG THE A MOTORS ⚠

```bash
tools/bench-run.sh detect-phase2
```

---

## Stop and tell me if

- A wheel turns on the **A** boards
- Anything hangs, smells, or gets hot
- A step needs a source edit to proceed
- Anything happens the sheet didn't say would

Notes in `BENCH-OBSERVATIONS.md` — what you saw, not what you think it means.

---

## Reference

Tiers: `t0` · `detect` · `detect-lib` · `detect-phase2` · `char` · `char-nopanel`
`tools/bench-run.sh <tier>` echoes both commands before running them. Logs → `src/logs/`.

The panel needs `src/bc_*.bmp` (five files, committed). They are loaded by bare filename, so the
runner's `cd src` is what makes them resolve. If they are ever missing the panel comes up blank —
regenerate with `python3 tools/gen_bench_char_assets.py`.
