# Doco visit D6 — the confirm run after D5's fixes (your only instructions)

**Plan:** task «#3688». **Driver:** DRIVER_REV 61. **Harness:** `test_bench_single` SRC_REV 21 (fmt 17); the adoption tool
`util_adopt_motor` TOOL_REV 6. **Pack:** the `dist/bench-<commit>-doco.zip` the hand-back names; this sheet travels inside
it.

**What this visit is for:** one short run that says *D5's findings are fixed*, and repeats nothing D5 already
certified. D5 certified the speed tops at all six supplies, the supply check (cold), the stops at 11.1, 14.8 and 24 V,
the slowest speeds at 22.2, 18.5 and 14.8 V, and the 11.1 V hand load; none of those is run again. This visit runs only:
- **The 7.4 V stops**, which D5 never reached.
- **The full-speed reversal at 24 V**, twice. It faulted once at D5; its record now names the fault if it happens again.
- **The slowest speeds at 11.1 and 24 V**, which fell short of their band at D5.
- **The hand load at 24 V** (the drive now stops a wheel held this way), and at 11.1 V to show the change broke nothing.
- **The clock ceiling:** a 350 MHz build must now refuse to start.
- **The adoption tool at 24 V**, which now stops its timing scan before the point where the motor slipped.

**Each supply is set once.** 7.4 V, then 11.1 V, then 24 V; never back.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Doco bench as D5 left it: **unit 2** on the Rev A board (P16 group), the encoder on the shaft, the bench supply, the
rig clamped. **The supply voltage you set must match the command's name** (`v7p4` is 7.4 V). No cold-motor rule this
time: nothing on this sheet depends on the motor's temperature.

**The grip** (the one you used at D5) goes on once, after the 11.1 V hands-off runs, and comes off once, after the 24 V
hand load.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The visit

| # | Supply | Command | What happens | You |
|---|---|---|---|---|
| 1 | **7.4 V** | `./bench-run.sh single-stops-v7p4` | About 2½ minutes: twelve drives that stop themselves, at the top speed and at a crawl, each way | Nothing. Keep hands clear |
| 2 | **11.1 V** | `./bench-run.sh single-mininc-v11p1 ; ./bench-run.sh single-passprobe-v11p1 clk-350` | 2 to 9 minutes: the slowest steady speed each way (the slowest steps barely move); then a 350 MHz build that **must refuse to start**: a few seconds, the motor does not move | Nothing |
| 3 | — | ✋ **FIT THE GRIP** | — | at your pace |
| 4 | **11.1 V** | ✋ `./bench-run.sh single-handload-v11p1` | **ATTENDED, at the PC**, as at D5: the panel's 4 A step, then the 2 A step (and the default limits only if the panel offers them). Each step: START STEP, the shaft turns slowly; at the green YOUR TURN banner slow it by the grip until it stops and hold it; about a second later the drive stops itself; let go | Your hand on the grip. About 5 minutes |
| 5 | **24.0 V** | ✋ `./bench-run.sh single-handload-v24p0` | **ATTENDED**, the same: the 4 A step, then the 2 A step | Your hand on the grip. About 5 minutes |
| 6 | — | ✋ **REMOVE THE GRIP** | — | at your pace |
| 7 | **24.0 V** | `./bench-run.sh single-ramp-v24p0 ; ./bench-run.sh single-ramp-v24p0 ; ./bench-run.sh single-mininc-v24p0 ; ./bench-run.sh doco-adopt-v24p0` | About 25–40 minutes: twice, the built-in speed-up and stop each way and a reversal straight through zero at 6,550 rpm (1½ minutes each); the slowest steady speed each way; then the adoption tool (a timing scan each way at two speeds, then a climb to the top) | Nothing |

**Attended work, all of it:** the grip on and off (rows 3 and 6) and your hand on the grip in rows 4 and 5 (about 10
minutes). The hands-off rows total about 30–50 minutes. **The whole visit is about 45–65 minutes.**

**What to watch for, named in advance:**
- **Row 2's second run does nothing on purpose.** The 350 MHz build refuses to start; the motor must not move.
- **Row 7's reversals** at the top: the motor sounds the same as D5's. A fault is recorded and the run carries on.
- **If a check FAILs, carry on.** The log is what it is for.

**If a run goes silent** (nothing new on the terminal for two minutes): close the terminal and go on to the next row.

**A stop is yours: turn the supply off.** Send back every log in `logs/`.

---

## Check the first lines of each log

| Test | The banner must read |
|---|---|
| the harness runs (rows 1, 2, 4, 5, 7) | `B1-BANNER,src_rev,21,commit,<the commit in the pack's name>,fmt,17,driver_rev,61,...`, `told_mv` equal to the supply you set, and `B1-BOARD` reading Rev A |
| the 350 MHz run (row 2) | `clkfreq,350_000_000`, then `B1-START,cog,-1,err,-1_024` |
| the adoption tool (row 7) | `MA-BANNER,tool_rev,6,...,build,DOCO_BENCH,clk_hz,270_000_000` |

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of D5's fixes on DRIVER_REV 61 (Rev A, P16, the Doco): the 7.4 V stops (PL-218's last supply; PL-221), the 24 V full-speed reversal (PL-222), the slowest speeds at 11.1 and 24 V (PL-216), the hand load at 24 V with its 11.1 V guard (PL-223, PL-170, PL-210), the clock ceiling's refusal (PL-199), the adoption tool at 24 V (PL-176). No new measurement |
| **Hardware risk** | The library's own 40 A limit; the harness stops a run at 3.68 A of supply current, on a stall, a charge it did not expect, an encoder disagreement or its time cap. The reversals and the adoption tool's climb reach 6,550 rpm as at D5. The hand-load rows push about 60–80 mN·m against your grip, and stop themselves. The 350 MHz run drives nothing |
| **Who acts** | You: the supply for each voltage, the grip on and off, your hand in rows 4–5 |
| **Runs that carry state** | None |
| **Run length** | About 45–65 minutes with the set-ups |
| **Repeatability** | Every run is repeatable and independent; a row can be rerun alone |
| **Variant matrix** | Rev A board (P16), DocoEng unit 2, 7.4, 11.1 and 24.0 V, 270 MHz (and 350 MHz in row 2), DRIVER_REV 61 |

## What this visit decides

Every cell prints its own verdict in the log; these are the bands that certify. They are D5's, unchanged.

- **The 7.4 V stops** (row 1): every `R23-SGL-STOPROT` within −240..+180 encoder counts and every `R23-SGL-STOPTIME`
  within ±100 ms. If the harness's current guard ends the run instead, its `B1-GUARD` line records the drive's duty, lag
  and state at that moment: that is the answer PL-221 needs, and the decision goes to Stephen.
- **The reversal** (row 7, twice): `B1-REVERSE ... faulted,FALSE,resyncs,0` both times, `R23-SGL-SMOOTH` and
  `R23-SGL-TOPSPD` REVERSAL PASS. A fault prints its `fault_kind`, phase, speed and lag (PL-222).
- **The slowest speeds** (rows 2 and 7): `R23-SGL-MININC` PASS — 0.10 ticks/s each way at 11.1 and 24 V.
- **The hand load** (rows 4 and 5): at 4 A and 2 A, at both supplies, `R23-SGL-BLKSTOP` measured and PASS (the drive
  stops itself 988–1,168 ms after the shaft stands) and `R23-SGL-LIMHOLD` PASS.
- **The clock ceiling** (row 2): the 350 MHz build ends `B1-END,abort,START,detail,-1_024` with nothing driven.
- **The adoption tool** (row 7): `MA-END stopped,NONE`, its climb reaching the 24 V top (`MA-RESULT ... ceil_found,TRUE`).
- **Watched in every row:** no log stops before its end record.

## Open questions

- PL-221: is the 7.4 V over-current a breakaway pulse against a rotor stuck near the end of a stop?
- PL-222: does the 24 V full-speed reversal fault again, and if so, of what kind and where?
- PL-216: do the 11.1 V and 24 V floors hold 0.10 ticks/s on a second run?

## Not in this visit

- Everything D5 certified (above). The 14.8, 18.5 and 22.2 V supplies.
- The supply check: closed by D5, cold, at three voltages.
- The 6.5″'s session: its own sheet (`SESSION-6P5-RUNSHEET.md`), re-cut for DRIVER_REV 61 before it runs.

## Revision history

- **2026-10-12** — written («#3688») from D5's evaluation (`DOCs/analyses/bench/2026-10-11/D5-EVALUATION.md`): its
  findings fixed at DRIVER_REV 61 / SRC_REV 21 / TOOL_REV 6, each supply set once (doctrine overlay P1).
