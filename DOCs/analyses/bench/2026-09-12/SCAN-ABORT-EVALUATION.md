# Bench Pass 2a — first two scan runs: start-check abort

**Logs:** `debug_260912-205538.log`, `debug_260912-205612.log` (identical outcome, 34 s apart).
**Binary:** `test_bench_scan.bin` at `73d528f` + `393f257`, `-D BENCH_CFG`.

## What the logs show — MEASURED

| Check | Result |
|---|---|
| Banner | `cfg_id BENCH`, left base 32, right base 16 — the run is valid |
| Board detection (left) | pinSum 101 / 99, high time 74 / 73 µs → Rev B |
| `start()` | cog 1, `cog_ok TRUE` |
| Offsets written and read back | 43 / 317 → 43 / 317, `offsets_ok TRUE` |
| Hall counters after start | `missed 0`, **`illegal 1`** → `integ_ok FALSE` |
| Outcome | `BS-ABORT RUN START_CHECK`, `BS-END ABORTED`; no increment ever commanded (`incre 0`, `points 0`) |
| Log close | `DEBUG_END_SESSION` received; the runner exited on its own |

The scan stopped where it was designed to: the self-check refuses to trust current readings from
a driver that reported a hall fault at start. Nothing moved.

## Why — DERIVED

The illegal count comes from «#3501»'s startup priming read, and the code puts that read inside
a glitch the driver creates for itself:

1. `.driveinit` raises DIR on `all_pins` = base+0..13. That range **includes the hall inputs**
   at base+5..7, so for a few instructions the P2 drives all three hall lines low. Only then
   does it `dirl` them.
2. Each hall line is a 3.9 kΩ pull-up to 3.3 V with 3.9 kΩ in series to the P2 pin
   (`BOARD-REVISION-FACTS.md`). While the pin is driven low the line side sits near 1.65 V; after
   release it recovers through 3.9 kΩ into the motor cable's capacitance.
3. The priming `testp` reads run nanoseconds after the release. A line that should read high can
   still read low, giving a code such as `%000`, which is counted as illegal.

This fits a count of exactly 1 on every start at the same resting position. It does not rule out
a genuine illegal code at that wheel position, which would also give exactly 1.

The same glitch predates «#3501». `.initAngleFmHall` (brake stop modes) reads the halls straight
after `.driveinit` too, so it can start from a wrong angle. «#3501»'s counter is what made the
glitch visible.

## Fix — «#3524»

Never drive the hall inputs: `.driveinit` raises DIR on `adc_pins` and `drive_pins` separately.
No settle delay is added. The ADC counts over a whole PWM frame, so enabling it two instructions
before the PWM cannot change a frame's reading.

## What the re-run decides

| Re-run shows | Meaning |
|---|---|
| `illegal 0` on both motors, self-check currents in band | Glitch confirmed as the cause; the ADC/PWM start offset is harmless |
| `illegal 1` persists | A genuine hall-code fault at that position — a finding, never suppressed |

## Side finding — the ternary runs both method calls

Both logs print `getBoardType() pinbase: ** NOT SET **` immediately before the left wheel's
`driver running … 22`. The scan has a single call site,
`(side == SIDE_RIGHT) ? wheelR.getBoardType() : wheelL.getBoardType()`, so with `side` LEFT the
unstarted right wheel's method ran as well (MEASURED from the log). Every ternary in the scan
that calls a wheel method is a status read, so no command reached the wrong motor. The `pnut-ts`
listing does not show bytecode, so the compiler-level cause is unconfirmed; filed as PL-29.
