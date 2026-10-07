# Doco visit D2 — qualify the tuned driver, and measure a second motor (your only instructions)

**Plan:** `DOCs/plans/DOCO-AND-CLOCK-SPRINT-PLAN.md` §10 step 5, `DOCs/plans/D1B-FOLLOW-ON-PLAN.md` §6 (tasks «#3687»,
«#3700»). **Driver:** DRIVER_REV 56. **Harness:** `test_bench_single` SRC_REV 17 (the speed-range test is new); the
adoption tool `util_adopt_motor` TOOL_REV 4. **Pack:** the `dist/bench-<commit>-doco.zip` the hand-back names for the
**Doco bench**; this sheet travels inside it.

> **SUPERSEDED 2026-10-07 — do not run this sheet's third pass.** Its runs were cut to the four the next changes need
> and moved to their own visit: `VISIT-D3-RUNSHEET.md`. This sheet stays as D2's record.

**THIRD PASS (2026-10-07): what is DONE stays done.** These stand and are NOT run again: every voltage's qualification
(7.4–24 V), the slowest-speed runs, the 11.1 V measure row, the 24 V noise captures, the clock runs, and 11.1 V's held
stop. This pass runs: **the speed-range test at every voltage** (your "lowest and highest we can command and hold"), the
**adoption tool** again (it no longer walks into the motor's torque wall), the **stop-after-N-turns test at 7.4 and
11.1 V** with its new record (why POS stops land early), and then the attended rows and unit 2.

**What this visit is for:** D1b measured the Doco; this visit **qualifies** the driver built from those measurements, at
every tested voltage, judged on the encoder: power steps hold speed, ramps arrive on time, stops come to rest where they
should, the top speed runs smoothly both ways and through reversals — including the speeds above about 2,400 rpm where
D1b found the drive misbehaving. It also confirms **the slowest speed the motor is controllable at and the highest it
reaches**, now the timing is right; runs the motor-adoption tool at each voltage; and tests by hand that the current limit
holds on this Rev A board at a low limit. Last, **a second Doco motor** gets its hall map and timing scan, to decide
whether the first motor's measured tables belong to the model or to that one unit.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Doco bench as at D1b: the motor (**unit 1, the one measured at D1b**) on the Rev A board (P16 group), the encoder
on the shaft at the motor's back, the bench supply, nothing on the shaft but the encoder. **The supply voltage you set
must match the command's name** (`v11p1` is 11.1 V): the harness is told the voltage, it does not measure it.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The visit

Rows 1–8 are unit 1. Row 9 is unit 2, after the swap.

| # | Supply | Command | What happens | You |
|---|---|---|---|---|
| 1 | **7.4 V** | `./bench-run.sh single-stops-v7p4 ; ./bench-run.sh single-range-v7p4 ; ./bench-run.sh doco-adopt-v7p4` | 30–60 minutes: the stop limits (~2.5 min), then **the speed range** — the slowest speed each way down to a quarter rpm, then a climb past the top about 140 rpm at a time until the motor can't hold it — then the adoption tool | Nothing. Keep hands clear |
| 2 | **11.1 V** | `./bench-run.sh single-stops-v11p1 ; ./bench-run.sh single-range-v11p1 ; ./bench-run.sh doco-adopt-v11p1` | 30–60 minutes, as row 1 | Nothing |
| 3 | **14.8 V** | `./bench-run.sh single-range-v14p8 ; ./bench-run.sh doco-adopt-v14p8` | 25–60 minutes | Nothing |
| 4 | **18.5 V** | `./bench-run.sh single-range-v18p5 ; ./bench-run.sh doco-adopt-v18p5` | 25–60 minutes | Nothing |
| 5 | **22.2 V** | `./bench-run.sh single-range-v22p2 ; ./bench-run.sh doco-adopt-v22p2` | 25–60 minutes | Nothing |
| 6 | **24.0 V** | `./bench-run.sh single-range-v24p0 ; ./bench-run.sh doco-adopt-v24p0` | 25–60 minutes: the highest climb of the pass — possibly past 4,000 rpm | Nothing |
| 7 | **11.1 V** | ✋ **ATTENDED — your hand on the shaft, ONCE THERE IS SOMETHING TO GRIP** (about 25 mm radius: a bare shaft cannot be held at 2–4 A). `./bench-run.sh single-handload-v11p1` | About 5 minutes, on a panel: the shaft turns slowly; at YOUR TURN slow it to a stop and hold it — at 4 A, then 2 A, then briefly the default limits | Follow the panel; hold it still for about a second each step |
| 8 | **24.0 V** | ✋ **ATTENDED — as row 7, with the grip.** `./bench-run.sh single-handload-v24p0 ; ./bench-run.sh single-heldpush-v24p0` | About 7 minutes: the hand load (4 A, 2 A), then the held stop (turn the stopped shaft until the hold gives way, each way) | Follow the panel |
| 9 | **14.8 V**, **unit 2** | ✋ **ATTENDED SET-UP — the motor swap.** **First: supply OFF. Swap unit 1 for unit 2** — its three phase leads and its hall connector on the P16 board, and the encoder coupled to **its** shaft. Then: `./bench-run.sh single-hallmap-v14p8 ; ./bench-run.sh single-offscan-v14p8 ; ./bench-run.sh single-range-v14p8` | About 40 minutes: the hall map, the timing scan, and unit 2's own speed range | Nothing after the swap |

**Attended work in this pass, all of it:** rows 7 and 8 (hand on the shaft, ~5 and ~7 min, and only once the shaft has a
grip), and the motor swap before row 9. Rows 1–6 are hands off: about 3–6 hours, splittable at any row.

**What to watch for, named in advance:**
- **The speed-range climb goes past every speed run before** — up to wherever the motor stops holding its speed, perhaps
  well past 4,000 rpm at 24 V. It may sound rougher and vibrate more at the top steps: that is what it measures. A fault
  at the top is the edge being found, recorded; the run carries on with the other direction.
- **The bench supply when the motor stops from the top of the climb.** A bench supply cannot take current back, and
  these stops return more energy than any before. If it trips or drops out, the run stops itself; send the logs and note
  the row.
- **POS stops from the top may still rest early** (rows 1 and 2): that is the known finding the stop record explains;
  it is not a reason to stop.
- **Unit 2 (row 9):** if its first crawl does not turn, or the terminal shows `B1-CHECK ... FAIL`, its hall or phase
  wiring differs from unit 1's — supply off and send the log; nothing is harmed.
- **The encoder check:** a `B1-CHECK ... FAIL` on unit 1 means the encoder and the halls disagreed; send the log.
- **Heat:** if the motor is too hot to hold comfortably, wait before the next row.

**If a run goes silent** (nothing new on the terminal for two minutes): close the terminal and go on to the next row.

**A stop is yours: turn the supply off.** Send back every log in `logs/`.

---

## Check the first lines of each log

| Test | The banner must read |
|---|---|
| every harness run | `B1-BANNER,src_rev,17,commit,<the commit in the pack's name>,fmt,14,driver_rev,56,...`, `told_mv` equal to the supply you set, and `B1-BOARD` reading Rev A |
| the adoption tool | `MA-BANNER` with `tool_rev,4` and `clk_hz,270_000_000`, and `MA-RECORD ... scan_a,40,ladder_a,40` |

## The visit, declared

| | |
|---|---|
| **Purpose** | **Qualification** of DRIVER_REV 55 on the Doco (plan §7): at 7.4, 11.1, 14.8, 18.5, 22.2 and 24.0 V the start and wiring checks, the power steps within 3 % on the encoder, the speed ladder (following, the misdial check, top speed smooth both ways and through reversals), the ramps within 10 %, the stop limits; the slowest steady speed per voltage on the new tables (Stephen's lowest-controllable-speed check); the adoption tool per voltage against D1b's offsets and ceilings; by hand at 11.1 and 24 V the current limit holding at 4 A and 2 A on Rev A's filtered sense, the blocked stop, the held stop. **Measurement:** 11.1 V's row in full (D1b lost it), the current sense frame by frame at 11.1 and 24 V (whether Rev A's noise is independent frame to frame — the filter's premise), and unit 2's hall map and timing scan. **The refusal:** a start at 120 MHz refused with nothing driven; the pass rate at 130 MHz |
| **Hardware risk** | The library's own 40 A current limit, so the bench's protection is the harness's stop at 3.68 A of supply current, a run charge cap, and its stops on stall, time or an encoder disagreement. The tops now reach about 2,800 rpm (D1b reached 2,660 hands-off). Hand loads at a 4 A and 2 A limit, and at 11.1 V briefly the default limits (about 110 mN·m), as D1b's plan sized them. Stops from top speed return energy to a supply that cannot take it. **If a run ends `GUARD ... OVER_CURRENT`, that is the stop working: send the log and go on to the next row** |
| **Who acts** | You: set the supply for each row; the two panel rows (2 and 8); the motor swap before row 9 |
| **Runs that carry state** | None |
| **Run length** | Third pass: rows 1–6 about 3–6 hours (the speed-range climbs run until the motor's edge, so their length is not known in advance); rows 7–9 about an hour with the swap. Rows are independent: it can be split across sittings at any row boundary |
| **Repeatability** | Every run is repeatable and independent; a row can be rerun alone |
| **Variant matrix** | Rev A board (P16), DocoEng motor units 1 and 2, 7.4, 11.1, 14.8, 18.5, 22.2 and 24.0 V (12.0 V is not tested), 270 MHz (and 130 / 120 MHz in row 1), DRIVER_REV 55 |

## How unit 2 decides the tables

Stephen 2026-10-06: measure a second unit, then decide. **Hall sectors:** if each of unit 2's sector widths is within
about 2° of unit 1's (D1b: 53.6–67.8°, each repeatable to 1.1°), the pattern is the model's and the measured table
ships; if not, the shipped table stays equal-sector and the adoption tool measures each user's motor. **Timing:** if
unit 2's half-speed minima at 14.8 V land within about ±3° of unit 1's (−62.2° / +53.4°), the committed offsets stand
for the model.

## What this visit does not measure

- Speeds above 419e6 increments (about 2,800 rpm): the harness and the tables stay capped there until this visit
  certifies the tops on the fixed driver.
- 12.0 V (not tested, by ruling). The Doco on a Rev B board (not in this plan).
- The 6.5″: its re-certification on the fixed driver is the 6.5″ session's sheet, on its own platform.

## Revision history

- **2026-10-06** — written («#3687»), after the batch that fixed the top-speed regime, tuned the Doco's tables, filtered
  Rev A's current limit and set the 130 MHz floor; unit 2 added at Stephen's direction.
- **2026-10-06 (evening)** — second pass after the first rows' evaluation (`DOCs/analyses/bench/2026-10-06/
  D2-PARTIAL-EVALUATION.md`): 11.1 V's qualification and clock runs and 7.4 V's qualification stand; row 1 reruns the
  measure run (the scan's walk fixed) and the tool (at 40 A); row 3 reruns the tool, the slowest speed on the raised
  minimum, and the stop limits with their decision recorded. Attended work named per row.
- **2026-10-07** — third pass («#3700»): the speed-range test at every voltage (Stephen: "the lowest RPM we can command
  and hold, and the highest... not some artificial limits"), with vibration and best timing per step; the adoption tool
  again (its sides end 20° past their minimum); the stops at 7.4 and 11.1 V with the record that explains the early POS
  rests; the hand rows wait on a grip; unit 2 adds its own speed range.
