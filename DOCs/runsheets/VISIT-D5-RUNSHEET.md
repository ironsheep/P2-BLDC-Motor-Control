# Doco visit D5 — the certification closeout on Rev A (your only instructions)

**Plan:** task «#3708». **Driver:** DRIVER_REV 60. **Harness:** `test_bench_single` SRC_REV 20 (fmt 16); the adoption tool
`util_adopt_motor` TOOL_REV 5. **Pack:** the `dist/bench-<commit>-doco.zip` the hand-back names; this sheet travels inside
it.

**What this visit is for** (Stephen 2026-10-08: "one more bench run only as a certification... not to discover any more
findings"): every Doco change since D4 is run once, on the driver that ships.
- **The speed range at every supply, on the final driver.** The field's advance is now damped at speed (the Doco's
  "second state" above ~2,500 rpm is gone), and the library's speed limits were lifted to match: 2,018 rpm at 7.4 V up to
  6,551 rpm at 24 V. Each row holds its new top with no fault, and the slowest speeds hold as well.
- **Timed stops end on time again.** D4 found them about 0.1 s late. Only a stop by turns now waits for the shaft.
- **The drive's checks at 7.4, 14.8 and 24 V,** with the supply check moved into its own short pass (about a minute
  per row) so the drive's timing no longer confuses it.
- **The hand load, with a grip on the shaft:** at a 2 A and a 4 A limit the shaft can be stopped by hand, and the
  current limit does not trip while the shaft turns free.
- **The current sense at rest at 300 and 350 MHz,** read before anything drives, to find where its noise starts.
- **The adoption tool on the Doco at 24 V,** as a user runs it, now that it climbs to the new top.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Doco bench: **unit 2, as D4 left it** (no swap) on the Rev A board (P16 group), the encoder on the shaft, the bench
supply. **The supply voltage you set must match the command's name** (`v7p4` is 7.4 V).

**Clamp the rig before row 1**, as at D4: the motor and the encoder fixed so they cannot slide or turn on the mat, the
encoder still coupled to the shaft and nothing else touching it.

**Rows 1–3 come first, on a cold motor.** The supply check in the drive's check assumes the motor is at room temperature,
and a hot motor reads high (at D4 the 24 V check followed 45 minutes of high-speed runs and read high for that reason).
If the motor has run in the last hour, let it cool before row 1.

**For rows 10–11, a grip on the shaft.** These rows ask you to slow the shaft by hand until it stops, and hold it, against
the motor pushing at about 60–80 mN·m. A bare shaft is too small to hold. Fit whatever grip suits you, about 25 mm in
radius (3–6 N at the rim). Rows 1–8 run with no grip.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The visit

| # | Supply | Command | What happens | You |
|---|---|---|---|---|
| 0 | — | ✋ **ATTENDED SET-UP: clamp the rig** (above) | — | ~10–15 minutes, once |
| 1 | **7.4 V** | `./bench-run.sh single-qualify-v7p4` | About 18 minutes: the drive's full check: power steps, speed ladder, the supply check, speed-up, stops, reversals | Nothing. Keep hands clear |
| 2 | **14.8 V** | `./bench-run.sh single-qualify-v14p8` | About 11 minutes | Nothing |
| 3 | **24.0 V** | `./bench-run.sh single-qualify-v24p0 ; ./bench-run.sh doco-adopt-v24p0 ; ./bench-run.sh single-range-v24p0` | About 1–1½ hours: the drive's check; the adoption tool (a timing scan each way at two speeds, then a climb to the top); then the speed range: down to a crawl, and up past 6,551 rpm about 140 rpm at a time until the motor cannot hold it | Nothing |
| 4 | **22.2 V** | `./bench-run.sh single-range-v22p2` | 15–30 minutes | Nothing |
| 5 | **18.5 V** | `./bench-run.sh single-range-v18p5` | 15–30 minutes | Nothing |
| 6 | **14.8 V** | `./bench-run.sh single-range-v14p8` | 15–30 minutes | Nothing |
| 7 | **11.1 V** | `./bench-run.sh single-passprobe-v11p1 clk-300 ; ./bench-run.sh single-passprobe-v11p1 clk-350 ; ./bench-run.sh single-stops-v11p1 ; ./bench-run.sh single-range-v11p1` | About 35–50 minutes: two short runs at 300 and 350 MHz (half speed each way), the twelve self-stopping drives, then the speed range | Nothing |
| 8 | **7.4 V** | `./bench-run.sh single-range-v7p4` | 10–15 minutes | Nothing |
| 9 | — | ✋ **ATTENDED SET-UP: fit the grip** (above) | — | at your pace |
| 10 | **11.1 V** | ✋ `./bench-run.sh single-handload-v11p1` | **ATTENDED, at the PC.** A panel opens. Three steps: a 4 A limit, a 2 A limit, then (only if the panel says the test has charge left) the default limits briefly. Each step: click START STEP, the shaft turns slowly (about 200 rpm); at the green YOUR TURN banner slow it by the grip until it stops and hold it; about a second later the drive stops itself; let go | Your hand on the grip, three times. About 5 minutes |
| 11 | **24.0 V** | ✋ `./bench-run.sh single-handload-v24p0` | **ATTENDED, at the PC.** The same, two steps: the 4 A limit, then the 2 A limit | Your hand on the grip, twice. About 5 minutes |

**Attended work, all of it:** clamping the rig before row 1; fitting the grip (row 9); your hand on the grip in rows 10
and 11 (about 10 minutes). Rows 1–8 are hands off, about 3–4½ hours, splittable at any row once rows 1–3 are done.

**What to watch for, named in advance:**
- **The climbs in rows 3–8 go higher than D4's** (the new tops). The motor may sound rougher at the top steps: that is
  measured. A fault at the top is the edge being found; the run carries on the other way.
- **The bench supply when the motor stops from the top.** A bench supply cannot take current back. If it trips, the run
  stops itself; send the logs and note the row.
- **If a check FAILs, carry on.** The log is what it is for.

**If a run goes silent** (nothing new on the terminal for two minutes): close the terminal and go on to the next row.

**A stop is yours: turn the supply off.** Send back every log in `logs/`.

---

## Check the first lines of each log

| Test | The banner must read |
|---|---|
| the harness runs (rows 1–8, 10, 11) | `B1-BANNER,src_rev,20,commit,<the commit in the pack's name>,fmt,16,driver_rev,60,...`, `told_mv` equal to the supply you set, and `B1-BOARD` reading Rev A |
| the adoption tool (row 3) | `MA-BANNER,tool_rev,5,...,build,DOCO_BENCH,clk_hz,270_000_000` |
| the clock runs (row 7) | `clk_hz` 300,000,000 and then 350,000,000 |

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of DRIVER_REV 60 on the Doco (Rev A, P16): the qualification at 7.4, 14.8 and 24 V on a cold motor, with the supply check's own pass; the timed and by-turns stops at 7.4 and 11.1 V; the speed range and the slowest speeds at all six supplies against the shipped limits; the hand load at 2 and 4 A with a grip; the rest-zero noise at 300 and 350 MHz before any drive; the adoption tool at 24 V. No new measurement: each row certifies a change made since D4 |
| **Hardware risk** | The library's own 40 A limit; the harness stops the run at 3.68 A of supply current, on a stall, a charge it did not expect, an encoder disagreement or its time cap. The climbs reach speeds not run before (bounded by the motor's no-load speed); their stops return energy to a supply that cannot take it. The hand-load rows push about 60–80 mN·m against your grip, and stop themselves |
| **Who acts** | You: the clamp, the supply for each row, the grip and your hand in rows 10–11 |
| **Runs that carry state** | None; rows 1–3 need a cold motor (above) |
| **Run length** | About 4–5 hours with the set-ups, splittable at any row after row 3 |
| **Repeatability** | Every run is repeatable and independent; a row can be rerun alone (rows 1–3 on a cold motor) |
| **Variant matrix** | Rev A board (P16), DocoEng unit 2, 7.4, 11.1, 14.8, 18.5, 22.2 and 24.0 V, 270 MHz (and 300 / 350 MHz in row 7), DRIVER_REV 60 |

## What this visit decides

Every cell prints its own verdict in the log; these are the bands that certify.

- **The qualification holds** (rows 1–3) if every `R23-SGL` cell PASSes. The supply check (`R23-SGL-MISDIAL`, fitted on
  its own pass at 650–1,400 rpm) reads within ±30 per mille. Every stop by turns rests within −240..+180 encoder counts
  (`R23-SGL-STOPROT`), and every timed stop ends within 100 ms of its limit (`R23-SGL-STOPTIME`).
- **The stops hold** (row 7) under the same two bands. D4 read timed stops +95 and +115 ms late on DRIVER_REV 57.
- **The speed limits hold** (rows 3–8) if, at every supply, the row's shipped top is reached and held. That means
  following at least 990 per mille, no held passes, no fault at or below the top, and the duty on the back-EMF line.
  The slowest speed held is 0.10 ticks/s from 11.1 V up and 4.00 at 7.4 V. Whatever ends each climb above the top is
  recorded with its kind (a lag or a hall fault) and the hall counts.
- **The hand load holds** (rows 10–11) if at 4 A and at 2 A the gripped shaft stops and the drive stops itself 988–1,168
  ms after it (`R23-SGL-BLKSTOP` measured and PASS). The limit must also hold with no fault (`R23-SGL-LIMHOLD`), and no
  fold may fire while the shaft turns free.
- **The rest-zero noise** (row 7): `B1-ZERO spread_mv` at 300 and 350 MHz, against the 3–5 mV every 270 MHz row prints.
  This places where the noise starts; the root cause then follows at the desk.
- **The adoption tool** (row 3) ends `MA-END` stopped, `NONE`, with the hall zero and timing pair it finds set against
  the Doco's shipped table, and its climb reaching the 24 V top.
- **Watched in every row:** no log stops before its end record.

## Not in this visit

- Unit 1: the tables are the two units' mean, so either unit certifies them.
- The 12.0 V row's range: it lies between 11.1 and 14.8 V, both measured.
- The 6.5″'s re-certification: the Rev B session's own sheet (`SESSION-6P5-RUNSHEET.md`), on its own platform.

## Revision history

- **2026-10-10** — written («#3708») after the v6.2.0 burn-down (DRIVER_REV 60) and the desk root cause of D4's high 24 V
  supply check (a hot motor; rows 1–3 now run first, cold).
