# Cog lifecycle and lock rules -- design («#3543», PL-41, PL-85)

**Status:** approved by Stephen 2026-09-18 ("yes let's do it") and implemented the same day. §7 records
what implementation changed or added.

## 1. The problem, in one paragraph

DEBUG output from every cog is serialised by LOCK[15] (`p2kbSpin2Debug`, on `DLY()`), and `cogstop`
runs no cleanup in the stopped cog (`p2kbSpin2Cogstop`). The bench logs show records damaged next to
cog start/stop bursts: a stopped cog's `INIT` line cut short (PL-41, Visit 1), and at Visit 5 a
**cog 0 record that lost its tail on the wire** (PL-85, USB capture `usb-traffic_260917-174323.log`
L1266). Cog 0 was never stopped, so stopping alone does not explain the damage: **starting** cogs
while another cog prints is implicated too. The exact mechanism is not established, and this design
does not need it (overlay P7: design the pattern out, don't characterise it). Every damaged line is
next to a burst of cog starts or stops.

## 2. The rules

- **R1 -- Stop only a quiet cog.** A cog that may be executing a DEBUG statement is never stopped
  outright. It is asked to exit, it acknowledges and parks with no output, and only then is it
  stopped. If it doesn't answer within a bound, it is stopped anyway and the stopper logs that it
  did so.
- **R2 -- Quiet window around every cog start and stop** (bench programs). Nothing prints for
  `QUIET_BEFORE_MS` before a cog event, so the last record has left the pin, and cog 0 prints nothing
  for `QUIET_AFTER_MS` after one, so the new cogs' `INIT` lines have finished. A burst (several
  starts or stops back to back) gets one window around the whole burst, not one per cog.
- **R3 -- No cog thrashing in tests.** A cell that needs cogs occupied occupies them once and releases
  them once. Cells that need the same occupancy share it.
- **R4 -- Locks.** A cog that takes or allocates a lock releases and returns it before it can be
  stopped. **No authored file uses `LOCKNEW`/`LOCKTRY`/`LOCKREL`/`LOCKRET` today** (inventory §3), so
  this rule changes no code; it's recorded so new code follows it.
- **R5 -- Spacers** (cogs started only to occupy a cog) never print, hold no lock, and pace themselves.

Quiet-window sizes (DERIVED, from the default `DEBUG_BAUD` of 2 Mbaud, which no bench program changes;
at 10 bits per byte that is 5 µs a byte):
- A record of up to ~200 bytes leaves the pin in about 1 ms, so `QUIET_BEFORE_MS = 2`.
- An `INIT` line is about 50 bytes, so seven cogs starting together emit about 1.75 ms of output;
  `QUIET_AFTER_MS = 10` covers that with margin.

A bench program runs for minutes, so ~70 windows of 12 ms cost under a second in total.

## 3. Inventory (every `cogstop` / `coginit` / `cogspin` in authored files)

| Site | Stopped cog prints? | How it's stopped today | Complies? |
|---|---|---|---|
| `isp_bldc_motor` driver (PASM) | No: its only DEBUG line is inside a `{ }` comment; no lock instructions | `cogstop` after the front cog is gone | Yes |
| `isp_bldc_motor` front cog | Error channel only | EXIT request, acknowledged, parked, then `cogstop` (bounded; PL-41) | Yes |
| `isp_steering_2wheel` front cog | Error channel only | Same EXIT protocol (`stopFrontCog`) | Yes |
| `isp_hdmi_debug` task + video cog | No live DEBUG in the task loop; the video driver is imported | `cogstop` | Yes |
| `isp_3wire_joystick` task | Yes: a start banner, and a line on every switch press | `cogstop` at any moment | **No** |
| `isp_4button_af1332` task | Yes: a start banner, and a line on every press | `cogstop` at any moment | **No** |
| `isp_queue_serial` RX task | Yes: a line for every received string, and on overflow | `cogstop` at any moment | **No** |
| Bench watchdogs (scan, char, dual) | Only after declaring a stall | `cogstop` guarded by `wdDeclaring` (never stopped mid-declaration) | Yes |
| `test_bench_dual` instrument cog | No ("emits nothing") | EXIT, parks, then `cogstop` | Yes |
| `test_bench_dual` ordered-stop helper | No; its library calls report on the error channel only | run flag lowered, bounded wait for its done flag, then `cogstop` | Yes |
| Spacers (t0, char) | No; `waitms` loop, no lock | burst of `cogstop` | R5 yes; R2/R3 **no** |
| Library `start()`/`stop()` from bench programs (72 sites: t0 29, dual 16, char 13, scan 8, spin 4, detect 2) | new cogs emit `INIT` | back to back with cog 0's records | R2 **no** |

Imported objects (`jm_sbus_rx`, `p2videodrv`, `p2textdrv`, `jm_*`, `hng034rm`) are out of scope,
as for the style gate.

## 4. Changes

**Library (three objects):**
1. `isp_3wire_joystick`, `isp_4button_af1332`: **the task cogs stop printing** (R1 by construction).
   The start banner moves to the starter after a successful `cogspin`; the per-press lines go.
   A cooperative-exit protocol for a debounce loop would add a flag, an acknowledgement and a bounded
   wait just to keep a diagnostic line, so I prefer removing the line.
2. `isp_queue_serial` RX task: **cooperative exit.** Its lines are worth keeping (a received string,
   a lost string). `stop()` sets an exit request. The task checks it every pass: `rxtime(1000)`
   returns at least once a second with no input, and after every character with input. The task
   acknowledges and parks with no output, then `stop()` stops it. If there's no answer within 1.5 s,
   `stop()` stops it anyway and logs that on the error channel. This is the motor front cog's
   pattern, so the codebase has one shape for "stop a task".

**Bench programs:**
3. **One quiet-window helper in `isp_bench_log`**, beside the record builders «#3574» moves there
   (PL-53): `cogEventBegin()` waits `QUIET_BEFORE_MS`; `cogEventEnd()` waits `QUIET_AFTER_MS`. Every
   library `start()`/`stop()` and every spacer burst in the six bench programs is bracketed by the
   pair, and nothing prints between them. Programs that don't include `isp_bench_log` yet get it as
   an OBJ now, not later.
4. **t0: one exhaustion phase** (R3). T0-8, T0-15b and T0-22 each start and stop seven spacers. They
   are ordered to run together, with one occupy burst and one release burst: 14 cog events instead of
   42. Cell ids and criteria are unchanged; only their order in the log moves.
5. **char STEERFAIL:** its spacer burst and the failed steering start get the same brackets. Its
   spacers already comply with R5.
6. `SRC_REV` bumps on every changed bench program.

**No change:** the PASM driver, both front cogs, the HDMI object, the instrument cog, the ordered-stop
helper, the watchdogs, and the spacers' own code. The Spin2<->PASM2 VAR runs are not touched: the
only VAR additions are the RX task's exit/acknowledge longs in `isp_queue_serial`, which no PASM
addresses.

## 5. Not chosen

- **`DEBUG_COGS = %0000_0001` in t0** (only cog 0 may print). Tempting, since t0 has no watchdog and
  prints its records from cog 0. But cog numbers are assigned at run time, so the mask can't select
  "the spacers" or "the front cog"; it would also silence the library's error channel, and P2KB does
  not say whether it suppresses the `INIT` line. It rests on an unknown; R2 doesn't.
- **A probe binary to establish the mechanism.** Ruled out by the task body and overlay P7.

## 6. Verification

- `tools/build-check.sh` green with both release demos; `tools/check_style.sh` exit 0; the
  motor/steering VAR runs byte-identical by content diff (they aren't edited).
- Run-time proof, owed to Visit 6 (never claimed here): a t0 log, and each bench log, with no
  run-together `CogN` prefixes and no truncated record, read against the USB capture if one is taken.
- PL-41 and PL-85 record the mechanism as designed out once the proof is in.

## 7. As implemented -- what changed from §4, and why

- **A stop gets no closing wait.** R2's closing wait exists for the `INIT` lines a *start* produces;
  a stop launches nothing, and R1 makes every stopped cog quiet. `test_bench_detect` takes a pin
  snapshot "within a millisecond of `stop()`", which a 10 ms wait would have broken. So a stop gets
  `cogEventBegin()` only; a start (or a burst containing one) gets both.
- **Free cogs are counted with `COGCHK()`**, which starts nothing. `countFreeCogs()` in t0 and char used
  to start spacers until one failed and stop them all -- up to 14 cog events per count, and t0 counts
  in T0-15, T0-16, T0-19 and T0-22. It measures the same quantity; this is R3 applied, not a new rule.
- **t0's exhaustion phase** (`runExhaustionPhase()`): count, occupy every spare cog once, T0-8, T0-15b's
  start, release one spacer so exactly one cog is free, T0-22's start, release the rest, count once;
  both T0-15b and T0-22 still judge `free_after == baseline`. T0-8 and T0-15b lost their private spacer
  loops. A `T0-EXH` begin/end line brackets the phase. Cell ids, criteria and record formats unchanged.
- **The joystick's analog channels start on the caller's cog.** The imported `jm_ez_analog`'s `start()`
  prints, and we don't edit it. Moving both `start()` calls into `startJoyStickCog()` means the reader
  cog never runs it, so the reader cog never prints at all (a first cut instead made `stop()` wait,
  bounded, for a setup-done flag -- replaced in review as the shallower fix). `read()` is an `RDPIN`, so
  any cog can read the channels; `stop()` now releases them with `jm_ez_analog.stop()`, which prints
  nothing.
- **The RX task polls for EXIT every 100 ms** (`RX_POLL_MS`, its receive timeout), not once a second,
  so `stop()`'s bound is 250 ms rather than 1.5 s.
- **`isp_queue_serial` stored the raw cog id but stopped `rxCogId - 1`** -- the wrong cog, and never cog 0.
  It now keeps cog id + 1 like every other object, and treats any negative `cogspin()` return as failure.
- `test_bench_spin` (4 sites) was missing from §3's count; it is bracketed too.
- **R2 is enforced by the style gate (T41), not by memory.** Review pointed out that ~90 hand-placed
  brackets leave the next call site free to forget one. In any file that includes `isp_bench_log`,
  `tools/check_style.sh` now fails a cog start or stop with no `cogEventBegin()` before it (or a print
  in between), and a start that prints before its `cogEventEnd()`. Fixture: `tools/fixtures/style/T41.spin2`.
- **`countFreeCogs()` lives in `isp_bench_log`**, one copy shared by t0 and char.
