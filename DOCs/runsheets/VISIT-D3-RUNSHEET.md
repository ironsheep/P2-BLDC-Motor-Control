# Doco visit D3 — four runs that the next fixes wait on (your only instructions)

**Plan:** `DOCs/plans/DOCO-AND-CLOCK-SPRINT-PLAN.md` §10, `DOCs/plans/D1B-FOLLOW-ON-PLAN.md` §6 (task «#3700»).
**Driver:** DRIVER_REV 56. **Harness:** `test_bench_single` SRC_REV 17; the adoption tool `util_adopt_motor` TOOL_REV 4.
**Pack:** the `dist/bench-<commit>-doco.zip` the hand-back names; this sheet travels inside it.

**What this visit is for:** D2 qualified the Doco at every voltage. These four runs are only what the next changes
need, nothing more:
- **Why "stop after N turns" lands early going one way at low voltage** — the stop tests at 7.4 and 11.1 V, now
  recording what the drive did during the stop.
- **The motor's real slowest and fastest speed, and the best timing up the range** — the new speed-range test, at 7.4 V
  (the one voltage with a real low-speed edge) and 24 V (the highest climb; its timing data is what fixing the extra
  duty above ~2,500 rpm needs).
- **Whether the adoption tool now runs clean** — one run, at 11.1 V.
- **Whether the first motor's sector timing belongs to the model or to that one unit** — the second Doco's hall map and
  timing scan.

**Held back on purpose:** the speed range at the other voltages, the tool at the other voltages, and unit 2's own speed
range. Today's top speed is set by the drive's extra duty, not the motor; measuring every voltage's top before that's
fixed would mean measuring them all again after. They come once, on the fixed drive. The hand-load rows wait on a grip
for the shaft.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Doco bench: the motor (**unit 1**) on the Rev A board (P16 group), the encoder on the shaft, the bench supply. **The
supply voltage you set must match the command's name** (`v7p4` is 7.4 V): the harness is told the voltage, it does not
measure it.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The visit

| # | Supply | Command | What happens | You |
|---|---|---|---|---|
| 1 | **7.4 V** | `./bench-run.sh single-stops-v7p4 ; ./bench-run.sh single-range-v7p4` | About 30 minutes: twelve drives that stop themselves (~2.5 min); then **the speed range** — the slowest speed each way, crawling down to a quarter of an rpm (the slowest steps barely move), then each way a climb past the top about 140 rpm at a time until the motor can't hold it | Nothing. Keep hands clear |
| 2 | **11.1 V** | `./bench-run.sh single-stops-v11p1 ; ./bench-run.sh doco-adopt-v11p1` | About 30 minutes: the stop drives again, then the adoption tool | Nothing |
| 3 | **24.0 V** | `./bench-run.sh single-range-v24p0` | 30–60 minutes: the speed range — the highest climb, possibly well past 4,000 rpm | Nothing |
| 4 | **14.8 V**, **unit 2** | ✋ **ATTENDED SET-UP — the motor swap.** **First: supply OFF. Swap unit 1 for unit 2** — its three phase leads and its hall connector on the P16 board, and the encoder coupled to **its** shaft. Then: `./bench-run.sh single-hallmap-v14p8 ; ./bench-run.sh single-offscan-v14p8` | About 12 minutes after the swap: eight short crawls (the hall map), then the timing scan | Nothing after the swap |

**Attended work, all of it:** the motor swap before row 4. Everything else is hands off. About 2 to 2½ hours in all.

**What to watch for, named in advance:**
- **The speed-range climbs (rows 1 and 3) go faster than anything run before.** The motor may sound rougher and vibrate
  more at the top steps: that is what is measured. A fault at the top is the edge being found; the run records it and
  carries on with the other direction.
- **The bench supply when the motor stops from the top of a climb.** A bench supply cannot take current back, and these
  stops return more energy than any before. If it trips, the run stops itself; send the logs and note the row.
- **POS stops at 7.4 and 11.1 V may still rest a little early** — that is the finding these runs explain.
- **Unit 2 (row 4):** if its first crawl does not turn, or the terminal shows `B1-CHECK ... FAIL`, its hall or phase
  wiring differs from unit 1's — supply off and send the log; nothing is harmed.
- **Heat:** if the motor is too hot to hold comfortably, wait before the next row.

**If a run goes silent** (nothing new on the terminal for two minutes): close the terminal and go on to the next row.

**A stop is yours: turn the supply off.** Send back every log in `logs/`.

---

## Check the first lines of each log

| Test | The banner must read |
|---|---|
| every harness run | `B1-BANNER,src_rev,17,commit,<the commit in the pack's name>,fmt,14,driver_rev,56,...`, `told_mv` equal to the supply you set, and `B1-BOARD` reading Rev A |
| the adoption tool | `MA-BANNER` with `tool_rev,4` |

## The visit, declared

| | |
|---|---|
| **Purpose** | **Measurement** for the next changes: the stop record behind POS stops resting early at low supply (7.4, 11.1 V); the speed range at 7.4 and 24 V — the slowest held speed each way, the highest held speed each way and what ended it, the shaft's speed ripple by sector and by turn, the current pulses by sector, and the best timing at every step; the adoption tool's run at 11.1 V after its fix; unit 2's hall sectors and timing minima at 14.8 V against unit 1's |
| **Hardware risk** | The library's own 40 A limit; the harness stops the run at 3.68 A of supply current, on a stall, a charge it did not expect, an encoder disagreement or its time cap. The climbs reach speeds not run before (bounded below the motor's no-load speed); their stops return more energy to a supply that cannot take it |
| **Who acts** | You: the supply for each row; the motor swap before row 4 |
| **Runs that carry state** | None |
| **Run length** | About 2 to 2½ hours, splittable at any row |
| **Repeatability** | Every run is repeatable and independent; a row can be rerun alone |
| **Variant matrix** | Rev A board (P16), DocoEng units 1 and 2, 7.4, 11.1, 14.8 and 24.0 V, 270 MHz, DRIVER_REV 56 |

## How unit 2 decides the tables

If each of unit 2's hall sector widths is within about 2° of unit 1's (53.6–67.8°, each repeatable to 1.1°), the
pattern is the model's and the measured sector table ships; if not, the shipped table stays equal-sector and the adoption
tool measures each user's motor. If unit 2's half-speed timing minima at 14.8 V land within about ±3° of unit 1's
(−62.2° / +53.4°), the committed offsets stand for the model.

## Revision history

- **2026-10-07** — written («#3700»): the D2 third pass cut to the four runs the next changes need, after Stephen's day of
  D2 runs (*"can't we do anything about the magnatude of this list"*).
