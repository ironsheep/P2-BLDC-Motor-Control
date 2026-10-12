# Doco visit D7 — the slow-down fix, at every supply (your only instructions)

**Plan:** task «#3688». **Driver:** DRIVER_REV 62. **Harness:** `test_bench_single` SRC_REV 22 (fmt 18). **Pack:** the
`dist/bench-<commit>-doco.zip` the hand-back names; this sheet travels inside it.

**What this visit is for:** the last Doco run. D5 and D6 found one fault left: slowing down from full speed at 24 V
(a reversal or a stop) faulted. The cause is now found at the desk and fixed in the driver. The fix changes every
slow-down above about 1,340 rpm at every supply, so this visit runs the speed-up, stop and reversal, and the stops, at
**each supply once**.

**This run gives an answer either way.** Pass: the Doco is certified on DRIVER_REV 62. Fault: the log now prints the
drive's last second before it (`B1-FTRACE`), which is what a fix needs; no rerun is needed to find out why.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Doco bench as D6 left it: **unit 2** on the Rev A board (P16 group), the encoder on the shaft, the bench supply, the
rig clamped, **no grip**. **The supply voltage you set must match the command's name** (`v7p4` is 7.4 V).

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The visit — hands off throughout

| # | Supply | Command | What happens |
|---|---|---|---|
| 1 | **7.4 V** | `./bench-run.sh single-ramp-v7p4 ; ./bench-run.sh single-stops-v7p4` | About 4 minutes: speed-up and stop each way, a reversal at full speed; then twelve drives that stop themselves |
| 2 | **11.1 V** | `./bench-run.sh single-ramp-v11p1 ; ./bench-run.sh single-stops-v11p1` | About 4 minutes, the same |
| 3 | **14.8 V** | `./bench-run.sh single-ramp-v14p8 ; ./bench-run.sh single-stops-v14p8` | About 4 minutes, the same |
| 4 | **18.5 V** | `./bench-run.sh single-ramp-v18p5 ; ./bench-run.sh single-stops-v18p5` | About 4 minutes, the same |
| 5 | **22.2 V** | `./bench-run.sh single-ramp-v22p2 ; ./bench-run.sh single-stops-v22p2` | About 4½ minutes, the same |
| 6 | **24.0 V** | `./bench-run.sh single-ramp-v24p0 ; ./bench-run.sh single-ramp-v24p0 ; ./bench-run.sh single-stops-v24p0` | About 6 minutes: the speed-up, stop and reversal twice, then the stops |

**Attended work:** none beyond setting the supply six times. **The whole visit is about 30–40 minutes.**

**What to watch for, named in advance:**
- **If a run goes silent or the terminal fills with garbage** (as at D6, 13:35): before you touch anything, note two
  things — **is the P2 board's power light on**, and **does the supply's current read 0**? Then close the terminal and
  rerun that command once. Those two answers are the only observations this sheet asks for.
- **If a check FAILs, carry on.** The log is what it is for.

**A stop is yours: turn the supply off.** Send back every log in `logs/`.

---

## Check the first lines of each log

| Test | The banner must read |
|---|---|
| every run | `B1-BANNER,src_rev,22,commit,<the commit in the pack's name>,fmt,18,driver_rev,62,...`, `told_mv` equal to the supply you set, and `B1-BOARD` reading Rev A |

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of DRIVER_REV 62 on the Doco (Rev A, P16): the slow-down from each supply's top, as a stop and as a reversal (PL-222), and every stop by rotation and by time at each supply, which the change also reaches. No new measurement |
| **Hardware risk** | The library's own 40 A limit; the harness stops a run at 3.68 A of supply current, on a stall, a charge it did not expect, an encoder disagreement or its time cap. Each supply's top as shipped, up to 6,551 rpm at 24 V, as at D5 and D6 |
| **Who acts** | You: the supply for each row |
| **Runs that carry state** | None |
| **Run length** | About 30–40 minutes with the supply changes |
| **Repeatability** | Every run is repeatable and independent; a row can be rerun alone |
| **Variant matrix** | Rev A board (P16), DocoEng unit 2, 7.4, 11.1, 14.8, 18.5, 22.2 and 24.0 V, 270 MHz, DRIVER_REV 62. 12.0 V lies between 11.1 and 14.8 V, both measured, as at D5 |

## What this visit decides

Every cell prints its own verdict in the log; these are the bands that certify, unchanged from D5 and D6.

- **The slow-down** (every ramp run): `R23-SGL-SMOOTH` NEG, POS and REVERSAL PASS (no fault, no re-sync, climb and stop
  alike); `R23-SGL-TOPSPD` PASS; `R23-SGL-RAMPARR` within ±100 ‰; `B1-REVERSE ... faulted,FALSE,resyncs,0`; no
  `B1-FTRACE` line.
- **The stops** (every stops run): every `R23-SGL-STOPROT` within −240..+180 encoder counts and every
  `R23-SGL-STOPTIME` within ±100 ms.
- **Watched in every row:** no log stops before its end record.

**Why the fix can be read this way:** at the desk the servo model reproduces D5 and D6's fault (24 V, about 3 s into the
slow-down) and finds the same fault at 18.5 and 22.2 V; with DRIVER_REV 62 it is clean at every supply's top, as a stop
and as a reversal, across the motor's uncertain inertia and friction and around its measured inductance, and a stop's
field travel moves under a hall tick.

## Open questions

- None the visit leaves to the bench: a fault prints its own trace.

## Not in this visit

- Everything D5 and D6 certified that DRIVER_REV 62 does not reach: the hand load, the slowest speeds, the speed range,
  the clock ceiling, the adoption tool, the supply check. The change acts only while the motor slows from above about
  1,340 rpm; none of those runs judges such a slow-down.
- The 6.5″'s session (`SESSION-6P5-RUNSHEET.md`, the Rev B platform): DRIVER_REV 62 does not reach the 6.5″ on its
  18.5 V pack, whose top (165 × 10⁶) is under the damping's gate (201 × 10⁶).

## Revision history

- **2026-10-12** — written («#3688») from D6's evaluation (`DOCs/analyses/bench/2026-10-12/D6-EVALUATION.md`) and the
  desk root cause of PL-222: DRIVER_REV 62, SRC_REV 22. Each supply set once; a fault prints its own trace (doctrine
  overlay P1, *every bench run yields a usable result whichever way it goes*).
