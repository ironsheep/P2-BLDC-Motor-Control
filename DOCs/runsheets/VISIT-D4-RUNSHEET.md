# Doco visit D4 — prove the fixes, then the final speed range (your only instructions)

**Plan:** task «#3704». **Driver:** DRIVER_REV 57. **Harness:** `test_bench_single` SRC_REV 18 (fmt 15).
**Pack:** the `dist/bench-<commit>-doco.zip` the hand-back names; this sheet travels inside it.

**What this visit is for** (Stephen 2026-10-08: "we retest only to prove the fixes and then gather final top numbers"):
- **The stop fix** — a stop by turns going POS at low supply should now land where it was told (it rested up to a
  quarter turn short).
- **The new timing** — the Doco now gets more lead as it speeds up, as the 6.5″ does, and its hall sectors are read at
  their measured widths instead of 60° each. Proven by the drive's own checks at the lowest, middle and highest supply.
- **The final speed range at every voltage** — the slowest and fastest speed the motor holds, on the new timing,
  measured once (Stephen: "not some artificial limits"). The library's speed limits are set from these.

**Held back on purpose:** the hand-load rows (they still wait on a grip for the shaft), the adoption tool, and the
voltages' full qualification between the three named — the timing change is the same at every supply (the lead model
shows the curves do not move with voltage), so three supplies spanning the range prove it.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Doco bench: **unit 2, as D3 left it** (STEPHEN 2026-10-08: no swap) on the Rev A board (P16 group), the encoder
on the shaft, the bench supply. Either unit proves the fixes: the tables are the two units' mean. **The supply
voltage you set must match the command's name** (`v7p4` is 7.4 V).

⭐ **New this visit — clamp the rig before row 1.** The motor and the encoder sit loose on the rubber mat, and at some
speeds the pair shakes and walks. Fix them to something solid (or at least so they cannot slide or turn on the mat),
with the encoder still coupled to the shaft and nothing else touching it. The speed-ripple numbers from D3 were the
loose rig's; this visit's are the clamped rig's.

**Get the tests:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The visit

| # | Supply | Command | What happens | You |
|---|---|---|---|---|
| 0 | — | ✋ **ATTENDED SET-UP: clamp the rig** (above) | — | ~10–15 minutes, once |
| 1 | **7.4 V** | `./bench-run.sh single-qualify-v7p4 ; ./bench-run.sh single-range-v7p4` | About 25 minutes: the drive's full check (power steps, speed ladder, speed-up, stops, reversals), then the speed range — down to a crawl, then up ~140 rpm at a time until the motor can't hold it | Nothing. Keep hands clear |
| 2 | **11.1 V** | `./bench-run.sh single-stops-v11p1 ; ./bench-run.sh single-range-v11p1` | About 20 minutes: the twelve self-stopping drives, then the speed range | Nothing |
| 3 | **14.8 V** | `./bench-run.sh single-qualify-v14p8 ; ./bench-run.sh single-range-v14p8` | About 35 minutes | Nothing |
| 4 | **18.5 V** | `./bench-run.sh single-range-v18p5` | 15–30 minutes | Nothing |
| 5 | **22.2 V** | `./bench-run.sh single-range-v22p2` | 15–30 minutes | Nothing |
| 6 | **24.0 V** | `./bench-run.sh single-qualify-v24p0 ; ./bench-run.sh single-range-v24p0` | 30–50 minutes: the highest climb, possibly past 4,500 rpm | Nothing |

**Attended work, all of it:** clamping the rig before row 1. Rows 1–6 are hands off, about 2½–3½ hours, splittable
at any row. No motor swap.

**What to watch for, named in advance:**
- **The climbs go faster than D3's** — the new timing is expected to raise the top. The motor may sound rougher at the
  top steps: that is measured. A fault at the top is the edge being found; the run carries on with the other way.
- **The bench supply when the motor stops from the top.** A bench supply cannot take current back. If it trips, the run
  stops itself; send the logs and note the row.
- **If a stop or a check FAILs in rows 1, 3 or 6, carry on** — the log is what it is for.
- **Heat:** if the motor is too hot to hold comfortably, wait before the next row.

**If a run goes silent** (nothing new on the terminal for two minutes): close the terminal and go on to the next row.

**A stop is yours: turn the supply off.** Send back every log in `logs/`.

---

## Check the first lines of each log

| Test | The banner must read |
|---|---|
| every run | `B1-BANNER,src_rev,18,commit,<the commit in the pack's name>,fmt,15,driver_rev,57,...`, `told_mv` equal to the supply you set, and `B1-BOARD` reading Rev A |

## The visit, declared

| | |
|---|---|
| **Purpose** | **Proof** of DRIVER_REV 57 on the Doco: the stop fix (STOPROT at 7.4 V in the qualification and at 11.1 V); the lead table and the measured sector table (the qualification at 7.4, 14.8 and 24 V — power steps, ladder, ramps, stops, reversals — judged on the encoder); then **measurement** of the final speed range at every supply (slowest and fastest held, what ended each climb, the timing sweep about the new lead at each step, the ripple on a clamped rig), all on unit 2 |
| **Hardware risk** | The library's own 40 A limit; the harness stops the run at 3.68 A of supply current, on a stall, a charge it did not expect (now counted without overflow), an encoder disagreement or its time cap. The climbs may reach speeds not run before (bounded at 1.02e9, the motor's no-load speed); their stops return more energy to a supply that cannot take it |
| **Who acts** | You: the clamp, and the supply for each row |
| **Runs that carry state** | None |
| **Run length** | About 3–4 hours with the set-ups, splittable at any row |
| **Repeatability** | Every run is repeatable and independent |
| **Variant matrix** | Rev A board (P16), DocoEng unit 2, 7.4, 11.1, 14.8, 18.5, 22.2 and 24.0 V, 270 MHz, DRIVER_REV 57 |

## What this visit decides

- **The stop fix holds** if every distance stop rests within its band (−240..+180 counts) at 7.4 and 11.1 V, POS
  included.
- **The new timing holds** if the qualification passes at 7.4, 14.8 and 24 V as D2's did on the old timing.
- **The final speed limits** are the range's slowest and fastest held speeds at each supply, with the library's
  usual reserve.
- **The lead model** is checked against each step's timing sweep, now taken about the new lead.

## Not in this visit

- The hand-load and held-stop rows — they wait on a grip about 25 mm in radius on the shaft.
- The 6.5″'s re-certification on DRIVER_REV 57 (its stop changed too; its lead values did not) — the 6.5″ session's
  own sheet, on its own platform.

## Revision history

- **2026-10-08** — written («#3704») after the D3 evaluation, the lead model and DRIVER_REV 57.
- **2026-10-08 (later)** — all rows on unit 2, which is on the bench; no swap (Stephen). The tables are the two units'
  mean, so either unit proves them; D3's unit-1 tops stay as unit 1's.
