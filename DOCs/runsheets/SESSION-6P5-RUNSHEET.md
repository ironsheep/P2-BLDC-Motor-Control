# 6.5″ session — re-certify the 6.5″ on the fixed driver, the clock floor and serial (your only instructions)

**Plan:** `DOCs/plans/DOCO-AND-CLOCK-SPRINT-PLAN.md` §10 (the 6.5″ session), §1.4, §8, §9 (task «#3687»). **Driver:**
DRIVER_REV 55. **Pack:** the `dist/bench-<commit>.zip` the hand-back names for the **Rev B platform**; this sheet
travels inside it. **The host script** `serial_certify.py` is in your checkout's `pythonSrc/` at the same commit.

**What this session is for:** the driver changed for every motor — the field now moves a frame at a time instead of in
one step per drive pass (it fixed the Doco's top speed; on the 6.5″ it removes a smaller, harmless swing) — so the 6.5″
is **re-certified** on its own qualification runs. Then the lowest supported clock, 130 MHz: the two-wheel front-cog
load, the frame budget, the dead gap and the current-sense noise. Then the serial top level answered by a real host, at
270 MHz and at 130 MHz, in plain and debug builds. Last, the motor-adoption tool on one wheel.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Rev B platform **on blocks, wheels up, both wheels free**, the pack connected as for the earlier sessions. For row 4
only: a USB-serial adapter from your host to P56/P57 (host Tx to P57, host Rx from P56, ground shared), as
`SERIAL-CONTROL.md` describes. **Before row 4, tell me which host and which port name** (`./serial_certify.py
--list-ports` on the host prints the names it knows) — or use `--port usb-auto` if the host has exactly one USB-serial
adapter.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The session

| # | Command | What happens | You |
|---|---|---|---|
| 1 | `./bench-run.sh dual-a ; ./bench-run.sh dual-limits ; ./bench-run.sh dual-kick ; ./bench-run.sh dual-d ; ./bench-run.sh dual-reg ; ./bench-run.sh demo-dual ; ./bench-run.sh demo-single` | About 50 minutes: the ladder and low speeds, the top speed, ramps and low-speed floor, the top-of-range speed changes, the current limit and front-cog contract, distance and forced faults, then both release demos | Nothing. Keep hands clear |
| 2 | `./bench-run.sh dual-clock clk-floor ; ./bench-run.sh t0 clk-floor` | A few minutes at **130 MHz**: both wheels under the heaviest front-cog load, then Tier 0 (no motion: the frame budget, dead gap and sense-noise cells) | Nothing |
| 3 | `./bench-run.sh adopt-wheel` | 15–30 minutes: the adoption tool on the RIGHT wheel, as a user runs it | Nothing |
| 4 | Four runs, each a pair — P2 first, then the host: **(a)** `./bench-run.sh serial-top clk-270` → host `./serial_certify.py --port <yours> --clock clk-270 --build debug` · **(b)** `./bench-run.sh serial-top-plain clk-270` → `--clock clk-270 --build plain` · **(c)** `./bench-run.sh serial-top clk-floor` → `--clock clk-floor --build debug` · **(d)** `./bench-run.sh serial-top-plain clk-floor` → `--clock clk-floor --build plain` | About 5 minutes each. The P2 loads and waits; the host script drives it. The wheels turn at power 30 when the script asks | Start the P2 command, then the host command. **When the script finishes, close the P2's terminal** (the serial top runs until stopped), then the next pair |

**What to watch for, named in advance:**
- **Row 1 is the comparison with the 6.5″'s earlier certification** — same runs, same bars. A cell that passed before and
  fails now is the finding this session exists for; let the run finish and send the log.
- **Row 2 runs at 130 MHz**, the slowest clock the library now accepts. A run that is refused there (`ERR_CLOCK_TOO_SLOW`,
  -1023) means the clock name built the wrong frequency: send the log.
- **Row 4:** if the script stops at once with `REPLY_NOT_LF_TERMINATED` or no ident line, the P2 is not running the serial
  top or the wiring is crossed: check the adapter's Tx/Rx and rerun that pair.
- **Heat** on the motors after row 1: wait before row 3 if they are hot.

**If a run goes silent** (nothing new on the terminal for two minutes): close the terminal and go on to the next row.

**A stop is yours: disconnect the pack.** Send back every log in `logs/` and every log the host script wrote.

---

## Check the first lines of each log

| Test | The first lines must read |
|---|---|
| the dual runs (rows 1, 2) | `BM-COMMIT,src_rev,85,commit,<the commit in the pack's name>`, and `BM-BUILD` with `drv_rev,55` |
| Tier 0 (row 2) | `src_rev 35 -- commit <the commit>` in its banner, and its `T0-1,dead_gap` line ending `clkfreq,130000000` |
| the adoption tool (row 3) | `MA-BANNER` with `tool_rev,2` |
| the serial runs (row 4) | the script's `SER-CLOCK` line naming the clock you gave it |

## The session, declared

| | |
|---|---|
| **Purpose** | **Re-certification** of the 6.5″ on DRIVER_REV 55 (the field moves a frame at a time; Rev B's current limit is unchanged, proven frame for frame at the desk): its qualification runs and both release demos. **The clock floor** (plan §1.4) at 130 MHz: the front cog's late count 0 and worst pass under 900 µs with two wheels, the worst request acknowledgement under its bound, the frame budget and dead gap, the current-sense noise against the fold floor. **Serial** (plan §9): `serial_certify.py`'s cells at 270 and 130 MHz, plain and debug builds, and the receive loop's worst cost. **The adoption tool** (plan §8) against the 6.5″'s shipped hall zero (−4°) and pair |
| **Hardware risk** | Wheels up throughout; the library's own current limits; the runs' own stops, as at every earlier platform session. The release demos run each wheel at full power for 15 s |
| **Who acts** | You: start each row; in row 4, start the host script after each P2 command and close the terminal after it |
| **Runs that carry state** | None |
| **Run length** | About 1 hour 45 minutes of runs; about 2 hours 15 minutes with set-up and the adapter |
| **Repeatability** | Every run is repeatable and independent; a row, or one pair of row 4, can be rerun alone |
| **Variant matrix** | Rev B boards (P16 right, P32 left), the 6.5″ motors, 18.5 V pack, 270 MHz and 130 MHz, plain and debug serial builds, DRIVER_REV 55 |

## What this session does not measure

- The floor runs, the obstacle and the RC demo: nothing that changed reaches them beyond what row 1 re-certifies.
- Rev A on the platform (not in this plan).

## Revision history

- **2026-10-06** — written («#3687»), after the driver change that moves the field a frame at a time (Stephen: the driver
  supports both motors, the 6.5″ re-certified), the 130 MHz floor, and the new serial tiers (no hand edit of the clock).
