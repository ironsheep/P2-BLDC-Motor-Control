# Doco visit D2 — qualify the tuned driver, and measure a second motor (your only instructions)

**Plan:** `DOCs/plans/DOCO-AND-CLOCK-SPRINT-PLAN.md` §10 step 5, `DOCs/plans/D1B-FOLLOW-ON-PLAN.md` §6 (task «#3687»).
**Driver:** DRIVER_REV 55 — the field now moves a frame at a time (the top-speed fix), the Doco's tables from D1b, and
Rev A's current limit reads a filtered current. Start refuses a clock under 130 MHz. **Harness:** `test_bench_single`
SRC_REV 15; the adoption tool `util_adopt_motor` TOOL_REV 2. **Pack:** the `dist/bench-<commit>.zip` the hand-back
names for the **Doco bench**; this sheet travels inside it.

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
| 1 | **11.1 V** | `./bench-run.sh single-qualify-v11p1 ; ./bench-run.sh single-measure-v11p1 ; ./bench-run.sh doco-adopt-v11p1 ; ./bench-run.sh single-passprobe-v11p1 clk-floor ; ./bench-run.sh single-passprobe-v11p1 clk-under` | About 1 hour: the qualification (~12 min), the 11.1 V measurements D1b could not finish (~23 min), the adoption tool (15–30 min), then two short clock runs. **The last one is meant to be refused**: built at 120 MHz, under the driver's floor, it must stop at its start with nothing turning | Nothing. Keep hands clear |
| 2 | **11.1 V** | `./bench-run.sh single-handload-v11p1 ; ./bench-run.sh single-heldpush-v11p1` | About 7 minutes, on a panel. **The hand load:** the shaft turns slowly; at YOUR TURN slow it by hand to a stop and hold it — at a 4 A limit, then 2 A, then briefly the default limits. **The held stop:** the stopped motor holds the shaft; turn it slowly by hand until the hold gives way, one way then the other | Follow the panel. At the 4 A and 2 A steps the motor should keep pushing smoothly until you stop it — **say in your notes if it stutters or gives up early** |
| 3 | **7.4 V** | `./bench-run.sh single-qualify-v7p4 ; ./bench-run.sh single-mininc-v7p4 ; ./bench-run.sh doco-adopt-v7p4` | 30–45 minutes | Nothing |
| 4 | **14.8 V** | `./bench-run.sh single-qualify-v14p8 ; ./bench-run.sh single-mininc-v14p8 ; ./bench-run.sh doco-adopt-v14p8` | 30–45 minutes | Nothing |
| 5 | **18.5 V** | `./bench-run.sh single-qualify-v18p5 ; ./bench-run.sh single-mininc-v18p5 ; ./bench-run.sh doco-adopt-v18p5` | 30–45 minutes | Nothing |
| 6 | **22.2 V** | `./bench-run.sh single-qualify-v22p2 ; ./bench-run.sh single-mininc-v22p2 ; ./bench-run.sh doco-adopt-v22p2` | 30–45 minutes | Nothing |
| 7 | **24.0 V** | `./bench-run.sh single-qualify-v24p0 ; ./bench-run.sh single-mininc-v24p0 ; ./bench-run.sh single-noise-v24p0 ; ./bench-run.sh doco-adopt-v24p0` | 30–45 minutes | Nothing |
| 8 | **24.0 V** | `./bench-run.sh single-handload-v24p0 ; ./bench-run.sh single-heldpush-v24p0` | About 7 minutes, on the panel, as row 2 (no default-limit step at 24 V) | As row 2 |
| 9 | **14.8 V**, **unit 2** | **First: supply OFF. Swap unit 1 for unit 2** — its three phase leads and its hall connector on the P16 board, and the encoder coupled to **its** shaft. Then: `./bench-run.sh single-hallmap-v14p8 ; ./bench-run.sh single-offscan-v14p8` | About 12 minutes: eight short crawls (the hall map), then the timing scan | Nothing after the swap |

**What to watch for, named in advance:**
- **The top speed is higher than at D1b** — about 2,800 rpm from 14.8 V up (D1b's rows topped at 2,500–2,660). That is
  the top-speed fix being qualified. If the top of a ladder roughens or faults, that is a measurement: let it run.
- **The bench supply when the motor stops from its top speed.** A bench supply cannot take current back. If it trips or
  drops out during a stop, the run stops itself; send the logs and note the row.
- **Row 1's last run ends at once, nothing turns.** That is the pass: the terminal shows `B1-START` with `err,-1_023`
  and the run ends. If the motor turns in that run, stop and send the log.
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
| every harness run | `B1-BANNER,src_rev,15,commit,<the commit in the pack's name>,fmt,12,driver_rev,55,...`, `told_mv` equal to the supply you set, and `B1-BOARD` reading Rev A |
| the adoption tool | `MA-BANNER` with `tool_rev,2` and `clk_hz,270_000_000` |
| row 1's two clock runs | `clkfreq` 130000000, then 120000000 (the refused one) |

## The visit, declared

| | |
|---|---|
| **Purpose** | **Qualification** of DRIVER_REV 55 on the Doco (plan §7): at 7.4, 11.1, 14.8, 18.5, 22.2 and 24.0 V the start and wiring checks, the power steps within 3 % on the encoder, the speed ladder (following, the misdial check, top speed smooth both ways and through reversals), the ramps within 10 %, the stop limits; the slowest steady speed per voltage on the new tables (Stephen's lowest-controllable-speed check); the adoption tool per voltage against D1b's offsets and ceilings; by hand at 11.1 and 24 V the current limit holding at 4 A and 2 A on Rev A's filtered sense, the blocked stop, the held stop. **Measurement:** 11.1 V's row in full (D1b lost it), the current sense frame by frame at 11.1 and 24 V (whether Rev A's noise is independent frame to frame — the filter's premise), and unit 2's hall map and timing scan. **The refusal:** a start at 120 MHz refused with nothing driven; the pass rate at 130 MHz |
| **Hardware risk** | The library's own 40 A current limit, so the bench's protection is the harness's stop at 3.68 A of supply current, a run charge cap, and its stops on stall, time or an encoder disagreement. The tops now reach about 2,800 rpm (D1b reached 2,660 hands-off). Hand loads at a 4 A and 2 A limit, and at 11.1 V briefly the default limits (about 110 mN·m), as D1b's plan sized them. Stops from top speed return energy to a supply that cannot take it. **If a run ends `GUARD ... OVER_CURRENT`, that is the stop working: send the log and go on to the next row** |
| **Who acts** | You: set the supply for each row; the two panel rows (2 and 8); the motor swap before row 9 |
| **Runs that carry state** | None |
| **Run length** | About 4 hours 30 minutes of runs; 5 to 5½ hours with set-up and the swap. Rows are independent: it can be split across sittings at any row boundary |
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
