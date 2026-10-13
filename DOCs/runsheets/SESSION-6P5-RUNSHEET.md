# 6.5″ session — the certification closeout on Rev B (your only instructions)

**Plan:** task «#3708» (the certification closeout), carrying `DOCs/plans/DOCO-AND-CLOCK-SPRINT-PLAN.md` §10 (the 6.5″
session), §1.4, §8, §9. **Driver:** DRIVER_REV 62. **Pack:** the `dist/bench-<commit>-platform.zip` the hand-back names for
the **Rev B platform**; this sheet travels inside it. **The host script** `serial_certify.py` is in your checkout's
`pythonSrc/` at the same commit.

**What this session is for:** certifying the driver on the 6.5″ for release. The 6.5″ last ran at DRIVER_REV 49
(2026-10-02). Since then the driver changed in ways that reach every 6.5″ drive: the field moves a frame at a time
(54), stops by rotation hold their planned travel (57/58), the front cog counts time in 1 ms slots at any clock (50/51),
a command's answer may take up to 40 ms (60), and a stood wheel held at its lag limit is blocked (61). And three release
claims have never run on hardware: the lowest clock (130 MHz), the serial top level, and both release demos on this
driver. **Every run below certifies one of those; nothing else is in this session.**

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Rev B platform **on blocks, wheels up, both wheels free**, the pack connected as for the earlier sessions. For row 3
only: a USB-serial adapter from your host to P56/P57 (host Tx to P57, host Rx from P56, ground shared), as
`SERIAL-CONTROL.md` describes. The host script takes the port by name: `--port usb-auto` if the host has exactly one
USB-serial adapter, otherwise the name `./serial_certify.py --list-ports` prints for it.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The session — 10 runs, about 1 hour

| # | Command | What it certifies | You |
|---|---|---|---|
| 1 | `./bench-run.sh dual-a ; ./bench-run.sh dual-kick ; ./bench-run.sh dual-d ; ./bench-run.sh dual-reg ; ./bench-run.sh demo-dual ; ./bench-run.sh demo-single` | About 40 minutes. **dual-a:** the speed range, low speeds and stops under the frame-at-a-time field (54, 57/58). **dual-kick:** speed changes at the top of the range, where the field's stepping acts most (54). **dual-d:** the front cog's contract, e-stop, current limits and the protective stop (51, 60, 61). **dual-reg:** distance stops on both wheels and a forced fault's recovery (57/58). **demo-dual, demo-single:** the two release demos, as shipped | Nothing. Keep hands clear |
| 2 | `./bench-run.sh dual-clock clk-floor ; ./bench-run.sh t0 clk-floor` | A few minutes at **130 MHz**, the lowest clock the library accepts (50, 51): both wheels under the heaviest front-cog load; then Tier 0 (no motion: the frame budget, dead gap and sense noise) | Nothing |
| 3 | Two pairs — P2 first, then the host: **(a)** `./bench-run.sh serial-top-plain clk-270` → host `./serial_certify.py --port <yours> --clock clk-270 --build plain` · **(b)** `./bench-run.sh serial-top clk-floor` → `--clock clk-floor --build debug` | About 5 minutes each. The serial top level as users ship it (270 MHz, plain), and at its worst case (130 MHz with debug output). The wheels turn at power 30 when the script asks | Start the P2 command, then the host command. **When the script finishes, close the P2's terminal**, then the next pair |

**Attended work:** row 3 only — starting each host command and closing the P2 terminal after it (twice). Rows 1–2 are
hands off.

**What to watch for, named in advance:**
- **Row 2 runs at 130 MHz.** A run refused there (`ERR_CLOCK_TOO_SLOW`, -1023) means the clock name built the wrong
  frequency: send the log.
- **Row 3:** if the script stops at once with `REPLY_NOT_LF_TERMINATED` or no ident line, the P2 is not running the serial
  top or the wiring is crossed: check the adapter's Tx/Rx and rerun that pair.
- **If a run goes silent** (nothing new on the terminal for two minutes) **or the terminal fills with garbage**: before
  you touch anything, note two things — **is the P2 board's power light on**, and **does the pack or supply read any
  current**? Then close the terminal and rerun that command once. Those two answers are the only observations this sheet
  asks for.

**A stop is yours: disconnect the pack.** Send back every log in `logs/` and every log the host script wrote.

---

## Check the first lines of each log

| Test | The first lines must read |
|---|---|
| the dual runs (rows 1, 2) | `BM-COMMIT,src_rev,87,commit,<the commit in the pack's name>`, and `BM-BUILD` with `drv_rev,62` |
| Tier 0 (row 2) | `src_rev 36 -- commit <the commit>` in its banner, and its `T0-1,dead_gap` line ending `clkfreq,130000000` |
| the serial runs (row 3) | the script's `SER-CLOCK` line naming the clock you gave it |

## The session, declared

| | |
|---|---|
| **Purpose** | **Certification** of DRIVER_REV 62 on the 6.5″ (Rev B): every run reached by a driver change since DRIVER_REV 49, both release demos, the 130 MHz floor, and the serial top level |
| **Hardware risk** | Wheels up throughout; the library's own current limits; the runs' own stops and the 10 A abort, as at every earlier platform session. The release demos run each wheel at full power for 15 s |
| **Who acts** | You: start each row; in row 3, start the host script after each P2 command and close the terminal after it |
| **Runs that carry state** | None |
| **Run length** | About 1 hour with the adapter |
| **Repeatability** | Every run is repeatable and independent; a run or one pair of row 3 can be rerun alone |
| **Variant matrix** | Rev B boards (P16 right, P32 left), the 6.5″ motors, 18.5 V pack, 270 MHz and 130 MHz, plain and debug serial builds, wheels up, DRIVER_REV 62 |

## What this session decides

Every cell prints its own verdict in the log.

- **Row 1:** every cell passes at the bars of the 6.5″'s last certification. One is read with its known limit:
  `R22-DUAL-SRVKEEP-A` compares the steady duty and current with a fixed reference taken on 2026-09-27, and one day's
  spread has read 5.6–7.7 % over it on an unchanged drive. Both demos run to their end.
- **Row 2:** `dual-clock clk-floor` reads late 0 and the worst front-cog pass under 900 µs; `t0 clk-floor` passes its
  frame-budget, dead-gap and sense-noise cells and prints `rev_b,TRUE`.
- **Row 3:** `serial_certify.py`'s cells PASS in both pairs (a protective stop read and cleared, numbers parsed, the reply
  latency, the getters). The two halves that cannot be provoked from the host (a latched protective stop, a refused
  start) are stated in the script as not measured by construction.
- **Watched in every row:** no log stops before its end record; no start check refuses the right board; a wheel's first
  pre-flight failure, if one comes, prints its retry (`BM-PFRETRY`).

## Not in this session, and why

Each was dropped on 2026-10-13 because it certifies no change and no release claim (doctrine overlay P1):

- **`dual-limits`** — drives each wheel past its top speed until it faults: it finds limits, it does not certify the
  shipped range, which `dual-a`'s ladder covers.
- **`adopt-wheel`** — the adoption tool is certified (tool_rev 6, the Doco, D6); the 6.5″'s shipped hall zero and pair
  are measured, and `dual-a` drives on them.
- **The 270 MHz debug and 130 MHz plain serial pairs** — the two kept bracket them: the shipped build, and the slowest
  clock with the debug load.
- **The floor row (`floor-auto`, `floor-grab`)** — declared as information read once; it gated no cell.
- **DRIVER_REV 59's and 62's damping and release (H-2, H-1b)** — they act only at 201 × 10⁶ and above; the 6.5″'s top on
  its 18.5 V pack is 165 × 10⁶.
- The obstacle trials and the RC drives, Rev A on the platform, the left board's supply-reading sag: as before.

## Revision history

- **2026-10-06** — written («#3687»), after the driver change that moves the field a frame at a time (Stephen: the driver
  supports both motors, the 6.5″ re-certified), the 130 MHz floor, and the new serial tiers (no hand edit of the clock).
- **2026-10-10** — rebuilt for DRIVER_REV 60 as the Rev B certification closeout («#3708»). It gains the floor row
  (Stephen 2026-10-10, "Q1 B"), last, with its change of set-up, and the banners move to the current harness revisions.
- **2026-10-12** — re-cut for DRIVER_REV 62 («#3688»): the banners read `drv_rev,62` and the adoption tool `tool_rev,6`;
  a run that goes silent asks in advance for two observations (PL-126).
- **2026-10-13** — cut to certification only (Stephen: *"cut down to essential tests from which we're actually going to
  learn something that actually proves and certifies the driver"*): 16 runs and about 2½ hours become 10 runs and about
  1 hour. Each kept run names the driver change or release claim it certifies; `dual-limits`, `adopt-wheel`, two serial
  pairs and the floor row are dropped, with the reason above.
- **2026-10-13** — run: rows 1 and 2 (`DOCs/analyses/bench/2026-10-13/REVB-EVALUATION.md`, no fault). Row 3 (serial) not
  run: Stephen, *"We are not going to qualify serial for this release"*; the next minor release qualifies it.
