# 6.5″ session — the certification closeout on Rev B (your only instructions)

**Plan:** task «#3708» (the certification closeout), carrying `DOCs/plans/DOCO-AND-CLOCK-SPRINT-PLAN.md` §10 (the 6.5″
session), §1.4, §8, §9. **Driver:** DRIVER_REV 60. **Pack:** the `dist/bench-<commit>-platform.zip` the hand-back names for
the **Rev B platform**; this sheet travels inside it. **The host script** `serial_certify.py` is in your checkout's
`pythonSrc/` at the same commit.

**What this session is for** (Stephen 2026-10-08: the certification closeout, "not to discover any more findings"): the
driver changed for every motor since the 6.5″ last ran. The field now moves a frame at a time and its advance is damped at
speed; timed stops end on time; a command's answer may take up to 40 ms. So the 6.5″ is **re-certified** on its own
qualification runs and both release demos. Then:
- **the lowest supported clock, 130 MHz:** the two-wheel front-cog load, the frame budget, the dead gap and the
  current-sense noise;
- **the serial top level** answered by a real host, at 270 and 130 MHz, in plain and debug builds;
- **the motor-adoption tool** on one wheel;
- **last, on the floor:** the two floor sessions, because the platform is already at hand (Stephen 2026-10-10).

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

Rows 1–4: the Rev B platform **on blocks, wheels up, both wheels free**, the pack connected as for the earlier sessions.
For row 4 only: a USB-serial adapter from your host to P56/P57 (host Tx to P57, host Rx from P56, ground shared), as
`SERIAL-CONTROL.md` describes. The host script takes the port by name: `--port usb-auto` if the host has exactly one
USB-serial adapter, otherwise the name `./serial_certify.py --list-ports` prints for it.

Row 5: **the change of set-up — the platform off its blocks, on the floor, wheels down**, the serial adapter off, on your
2 m × 2 m square with the platform on its fixed start point (the axle 0.5 m in from the middle of one edge, facing across
the square), as at the earlier floor visits.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The session

| # | Command | What happens | You |
|---|---|---|---|
| 1 | `./bench-run.sh dual-a ; ./bench-run.sh dual-limits ; ./bench-run.sh dual-kick ; ./bench-run.sh dual-d ; ./bench-run.sh dual-reg ; ./bench-run.sh demo-dual ; ./bench-run.sh demo-single` | About 50 minutes: the ladder and low speeds, the top speed, ramps and low-speed floor, the top-of-range speed changes, the current limit and front-cog contract, distance and forced faults, then both release demos | Nothing. Keep hands clear |
| 2 | `./bench-run.sh dual-clock clk-floor ; ./bench-run.sh t0 clk-floor` | A few minutes at **130 MHz**: both wheels under the heaviest front-cog load, then Tier 0 (no motion: the frame budget, dead gap and sense-noise cells) | Nothing |
| 3 | `./bench-run.sh adopt-wheel` | 15–30 minutes: the adoption tool on the RIGHT wheel, as a user runs it | Nothing |
| 4 | Four runs, each a pair — P2 first, then the host: **(a)** `./bench-run.sh serial-top clk-270` → host `./serial_certify.py --port <yours> --clock clk-270 --build debug` · **(b)** `./bench-run.sh serial-top-plain clk-270` → `--clock clk-270 --build plain` · **(c)** `./bench-run.sh serial-top clk-floor` → `--clock clk-floor --build debug` · **(d)** `./bench-run.sh serial-top-plain clk-floor` → `--clock clk-floor --build plain` | About 5 minutes each. The P2 loads and waits; the host script drives it. The wheels turn at power 30 when the script asks | Start the P2 command, then the host command. **When the script finishes, close the P2's terminal** (the serial top runs until stopped), then the next pair |
| 5 | ✋ **ON THE FLOOR** (the set-up above): `./bench-run.sh floor-auto` then ✋ `./bench-run.sh floor-grab` | `floor-auto`, about 3 minutes: ten spins in place, the fault run, four ramp legs, all inside the square, ending on its start point. `floor-grab`, about 45 seconds: 1 m straight at a slow walk | **ATTENDED.** `floor-auto`: stand by outside the square. `floor-grab`: stand beside its LEFT side; about 3 s after it starts rolling, take hold of the frame and keep holding until it stops at 1 m, enough to slow it to about half speed, not to stop it. Its last line says whether to hold harder or less and run it again |

**Attended work, all of it:** in row 4, starting each host command and closing the P2 terminal after it (four times);
row 5's change of set-up to the floor, standing by for `floor-auto`, and your hold in `floor-grab` (about 15 minutes with
the set-up). Rows 1–3 are hands off.

**What to watch for, named in advance:**
- **Row 1 is the comparison with the 6.5″'s earlier certification**: same runs, same bars. A cell that passed before and
  fails now is what this session would find. Let the run finish and send the log.
- **Row 2 runs at 130 MHz**, the slowest clock the library accepts. A run that is refused there (`ERR_CLOCK_TOO_SLOW`,
  -1023) means the clock name built the wrong frequency: send the log.
- **Row 4:** if the script stops at once with `REPLY_NOT_LF_TERMINATED` or no ident line, the P2 is not running the serial
  top or the wiring is crossed: check the adapter's Tx/Rx and rerun that pair.
- **Row 5's last lines** start `RESULT:`: `floor-auto` says where the platform ended; `floor-grab` says whether the hold
  was read.
- **Heat** on the motors after row 1: wait before row 3 if they are hot.

**If a run goes silent** (nothing new on the terminal for two minutes): close the terminal and go on to the next row.

**A stop is yours: disconnect the pack** (on the floor: lift the wheels and disconnect the battery). Send back every log in
`logs/` and every log the host script wrote.

---

## Check the first lines of each log

| Test | The first lines must read |
|---|---|
| the dual and floor runs (rows 1, 2, 5) | `BM-COMMIT,src_rev,87,commit,<the commit in the pack's name>`, and `BM-BUILD` with `drv_rev,60` |
| Tier 0 (row 2) | `src_rev 36 -- commit <the commit>` in its banner, and its `T0-1,dead_gap` line ending `clkfreq,130000000` |
| the adoption tool (row 3) | `MA-BANNER` with `tool_rev,5` |
| the serial runs (row 4) | the script's `SER-CLOCK` line naming the clock you gave it |

## The session, declared

| | |
|---|---|
| **Purpose** | **Re-certification** of the 6.5″ on DRIVER_REV 60: its qualification runs and both release demos. **The clock floor** at 130 MHz: the front cog's late count 0 and worst pass under 900 µs with two wheels, the worst request acknowledgement under its bound, the frame budget and dead gap, the current-sense noise against the fold floor, and Tier 0 printing its board flag as a word (`rev_b,TRUE`). **Serial**: `serial_certify.py`'s cells at 270 and 130 MHz, plain and debug builds (a protective stop read and cleared, numbers parsed, the reply latency, the getters), and the receive loop's worst cost. **The adoption tool** against the 6.5″'s shipped hall zero (−4°) and pair. **On the floor**, as information under load: the lag peaks in calm spins, the slow leg's every sample, the quarter-speed current both ways, and the limiter's single engagement |
| **Hardware risk** | Rows 1–4 wheels up; the library's own current limits; the runs' own stops, as at every earlier platform session. The release demos run each wheel at full power for 15 s. Row 5 on the floor under its built-in rules: an armed distance limit on every drive, the square fence, the 10 A abort; `floor-grab` limits current to 4 A |
| **Who acts** | You: start each row; in row 4, start the host script after each P2 command and close the terminal after it; in row 5, the floor set-up, standing by, and the hold |
| **Runs that carry state** | None |
| **Run length** | About 2 hours of runs; about 2½ hours with the adapter and the floor set-up |
| **Repeatability** | Every run is repeatable and independent; a row, one pair of row 4, or one floor command can be rerun alone |
| **Variant matrix** | Rev B boards (P16 right, P32 left), the 6.5″ motors, 18.5 V pack, 270 MHz and 130 MHz, plain and debug serial builds, wheels up and (row 5) on the floor, DRIVER_REV 60 |

## What this session decides

Every cell prints its own verdict in the log.

- **Re-certification** (row 1): every cell that passed at the 6.5″'s last certification passes again, at the same bars.
  One is read with its known limit: `R22-DUAL-SRVKEEP-A` compares the steady duty and current with a fixed reference taken
  on 2026-09-27, and one day's spread has read 5.6–7.7 % over it on an unchanged drive.
- **The clock floor** (row 2): `dual-clock clk-floor` reads late 0 and the worst front-cog pass under 900 µs; `t0
  clk-floor` passes its frame-budget, dead-gap and sense-noise cells and prints `rev_b,TRUE`.
- **Serial** (row 4): `serial_certify.py`'s cells PASS in all four pairs. The two halves that cannot be provoked from the
  host (a latched protective stop, a refused start) are stated in the script as not measured by construction.
- **The adoption tool** (row 3): `MA-END` stopped, `NONE`; the hall zero and pair it finds sit by the shipped −4° and pair.
- **The floor** (row 5): four floor watches are read once, as information; nothing in them gates a cell.
- **Watched in every row:** no log stops before its end record; no start check refuses the right board; a wheel's first
  pre-flight failure, if one comes, prints its retry (`BM-PFRETRY`).

## What this session does not measure

- The obstacle trials and the RC drives: nothing that changed reaches them beyond what rows 1 and 5 re-certify. (A speed
  raised while a wheel is still slowing was seen in an RC drive; the ramp generator that does it has not changed since.)
- Rev A on the platform (not in this plan).
- The left board's supply-reading sag under load: a meter check, not chased for the release.

## Revision history

- **2026-10-06** — written («#3687»), after the driver change that moves the field a frame at a time (Stephen: the driver
  supports both motors, the 6.5″ re-certified), the 130 MHz floor, and the new serial tiers (no hand edit of the clock).
- **2026-10-10** — rebuilt for DRIVER_REV 60 as the Rev B certification closeout («#3708»). It gains the floor row
  (Stephen 2026-10-10, "Q1 B", "only because we are doing a revB wheels up so we are already at the platform"), last,
  with its change of set-up, and the banners move to the current harness revisions. Row 4 no longer asks you to report the
  port before the session.
