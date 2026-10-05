# Doco visit D1b — measure the motor on the driver (your only instructions)

**Plan:** `DOCs/plans/DOCO-AND-CLOCK-SPRINT-PLAN.md` §10, step 3 (task «#3696»). **Driver:** DRIVER_REV 53 — the Doco's
commutation pair corrected (the first D1b try showed the motor did not turn under drive). **Harness:** `test_bench_single`
SRC_REV 14 — the motor now runs under the library's own current limit (40 A), not the 2 A test limit, which on this Rev A
board fired on sense noise and cost the drive its following at every voltage. **Pack:** the `dist/bench-<commit>.zip` the
hand-back names; this sheet travels inside it.

**THIS RE-RUN (2026-10-05, third pass): rows 2–7's measure runs only, the `single-measure-*` commands.** The align (row
1) is done and resolved; the six clock probes are done (their results stand). Skip both.

**What this visit is for:** the measurements the driver's Doco tables are made from, the way the 6.5″'s were. First the
cold hall zero by hand (the 6.5″'s align method). Then, at each tested voltage, hands off: the hall map in both directions,
the timing (offset) scan, the slowest steady speed, the speed ladder to the top, the built-in speed-up and stop, and the
stop limits — all judged on the encoder. At 11.1 V, the drive's timing at five system clocks. This visit measures; the
next one (D2) qualifies the tuned driver.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Doco bench as at D1a: the motor on the Rev A board (P16 group), the encoder on the shaft at the motor's back, the
bench supply, nothing on the shaft but the encoder. **The supply voltage you set must match the command's name**
(`v11p1` is 11.1 V): the harness is told the voltage, it does not measure it.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The visit

| # | Supply | Command | What happens | You |
|---|---|---|---|---|
| 1 | **11.1 V** | `./bench-run.sh single-align-v11p1` — **from the align pack the hand-back names** (reworked 2026-10-05; the first pack's align could not pass on this board) | A few minutes. A panel: **two steps, one each way**, the motor started but never driven (its drive stays off). Each step: click START STEP, keep the shaft still about a second while it reads the rest level, then at YOUR TURN, **looking at the encoder end**, in the direction the step names, **flick the shaft in bursts, as fast as is comfortable, as many times as it takes** — there is no pace to hold. The panel counts the crossings it has collected against its target of 36 and ends the step by itself when it has them (or click DONE). | Flick in bursts. **If a result says NOT RESOLVED, click REDO and flick a little harder** — the signal was too small to read, not a fault. NEXT when it says MEASURED |
| 2 | **11.1 V** | `./bench-run.sh single-measure-v11p1 ; ./bench-run.sh single-passprobe-v11p1 clk-floor ; ./bench-run.sh single-passprobe-v11p1 clk-200 ; ./bench-run.sh single-passprobe-v11p1 clk-270 ; ./bench-run.sh single-passprobe-v11p1 clk-300 ; ./bench-run.sh single-passprobe-v11p1 clk-350 ; ./bench-run.sh single-passprobe-v11p1 clk-frac` | About 23 minutes of measuring, then six runs of under a minute each (half speed each way at six system clocks) | Nothing. Keep hands clear |
| 3 | **7.4 V** | `./bench-run.sh single-measure-v7p4` | About 23 minutes | Nothing |
| 4 | **14.8 V** | `./bench-run.sh single-measure-v14p8` | About 23 minutes | Nothing |
| 5 | **18.5 V** | `./bench-run.sh single-measure-v18p5` | About 23 minutes | Nothing |
| 6 | **22.2 V** | `./bench-run.sh single-measure-v22p2` | About 23 minutes | Nothing |
| 7 | **24.0 V** | `./bench-run.sh single-measure-v24p0` | About 23 minutes | Nothing |

**What to watch for, named in advance:**
- **The bench supply when the motor stops from its top speed.** A bench supply cannot take current back. If it trips or
  drops out during a stop, the run stops itself; send the logs and note the row.
- **At 11.1 V the top of the ladder may hold back or fault** — the desk model predicts it. That is a measurement.
- **The encoder check:** if the terminal shows `B1-CHECK ... FAIL`, the encoder and the halls disagreed; send the log.
- **Heat:** if the motor is too hot to hold comfortably, wait before the next row.
- **The panel in row 1 is a little larger than any we have loaded before** (11.8 MB of images; 25 MB is the size that
  failed once): if the panel does not draw within a minute, close it and send the log.

**If a run goes silent** (nothing new on the terminal for two minutes): close the terminal and go on to the next row.

**A stop is yours: turn the supply off.** Send back every log in `logs/`.

---

## Check the first lines of each log

| Test | The banner must read |
|---|---|
| every run | `B1-BANNER,src_rev,13,commit,<the commit in the pack's name>,fmt,11,driver_rev,53,...`, `told_mv` equal to the supply you set, and `B1-BOARD` reading Rev A |
| the six probes | `clkfreq` 120000000, 200000000, 270000000, 300000000, 350000000, 271250000 |

## The visit, declared

| | |
|---|---|
| **Purpose** | **Measurement** for the driver's Doco tables (plan §6): the cold hall zero (align, per hall edge); per tested voltage the hall map both ways (the hall order for both power signs), the timing scan's current minimum (the offset, and whether the best timing moves with speed), the slowest steady speed each way, the speed ladder (the duty line, the top speed with the 6.5″'s duty reserve, the feedforward line, the misdial check), the built-in speed-up and stop, the stop limits; at 11.1 V the drive pass at five clocks and the front cog's worst pass. Today's tables are measured as the "before" |
| **Hardware risk** | Align: the drive is never commanded. Hands-off rows: the library's own 40 A current limit, so the bench's protection is the harness's stop at 3.68 A of DC link (it ended the 7.4 V check run cleanly at a 4.48 A peak on a deliberately mistimed point; the timing scan now stays within ±20°), a run charge cap, and the harness's stops on stall, time or an encoder disagreement. No hand loads this visit. Stops from top speed return energy to a supply that cannot take it (*What to watch for*). **If a run ends `GUARD ... OVER_CURRENT`, that is the stop working: send the log and go on to the next row** |
| **Who acts** | You: the two hand steps in row 1 (bursts, one each way); set the supply for each row |
| **Runs that carry state** | None |
| **Run length** | About 2 hours 30 minutes of runs; about 3 hours with set-up |
| **Repeatability** | Every run is repeatable and independent; a row can be rerun alone |
| **Variant matrix** | Rev A board (P16), DocoEng motor, the tested voltages 7.4, 11.1, 14.8, 18.5, 22.2 and 24.0 V (12.0 V is not tested), 270 MHz (and five probe clocks at 11.1 V), DRIVER_REV 53 |

## What this visit does not measure

- The hand-load and held-stop behaviour, and the lowest and highest speeds on the tuned driver: D2.
- 12.0 V (not tested, by ruling).

## Revision history

- **2026-10-04** — written («#3696»).
- **2026-10-05** — row 1 reworked («#3697»): the first align read CLIPPED on every try because Rev A's undriven phases rest
  on the instrument's low rail; it now reads where the phases cross each other, from bursty flicks, two steps.
- **2026-10-05** — re-run on DRIVER_REV 53: the first try's hands-off rows showed the motor did not turn under drive
  (the Doco's commutation pair was in the wrong frame for the 6.x driver; corrected); a `clk-300` probe is added to place
  where the 350 MHz current-sense noise starts.
- **2026-10-05** — third pass, SRC_REV 14: the second pass's hands-off rows lost following at every voltage because the
  2 A test current limit's fold-back fired on Rev A's sense noise (a 7.4 V check at 40 A followed cleanly). The measure
  rows run again under the library's 40 A limit, the timing scan at ±20°; the align and the probes stand.
