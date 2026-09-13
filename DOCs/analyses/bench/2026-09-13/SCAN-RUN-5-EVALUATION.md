# Bench Pass 2a — scan run 5 (scan v3.1)

**Log:** `debug_260913-120844.log` (this folder, 799 lines).
**Source:** `e39f98d`. Banner: `src_rev 4, fmt 4, cfg_id BENCH`, left base 32, right base 16.
**Run:** started 12:08:45. Stephen ran it.

**The log is incomplete.** Debug logging stopped at 12:16:50, about 485 s into the run, while
the right motor's negative quarter-speed leg was running fine points. The P2 kept running:
there was no reset and no loss of power (§7). Everything after that point, including the right
motor's fit, its half-speed legs, its results and `BS-END`, was never recorded.

**Provenance tags:**
- **MEASURED** = a log line.
- **DERIVED** = my calculation.
- **STEPHEN** = his words.

**Units and conventions:**
- Sense readings are mV at 150 mV/A.
- **Net** = a point's raw mean minus the `BS-ZERO` read immediately before it, in the same driver
  lifetime.
- Offsets are *swept* degrees. A negative increment is served by `offset_fwd` (default +43), a
  positive increment by `offset_rev` (default 317, written as −43).

---

## 1 · Foundations — MEASURED

- Rev B at all eight starts; `illegal 0` / `missed 0` at every start and across every point.
- `dead_gap 70` on every init.
- Offsets read back exactly at every start.

**Self-checks — both motors passed:**

| | zero | +¼ net | −¼ net | ratio | rate |
|---|---|---|---|---|---|
| LEFT | 8.6 | 83.2 | 164.9 | 1.981 | 98.1 / 98.2 |
| RIGHT | 74.9 | 93.4 | 172.5 | 1.846 | 98.1 / 98.2 |

This is the first run in which the right motor was scanned.

## 2 · LEFT motor, quarter speed — both legs fitted

**Negative increment (`offset_fwd`)**, net:

| swept | 53 | **43** | 33 | 28 | 23 | 18 | 13 | 8 | 3 | −7 |
|---|---|---|---|---|---|---|---|---|---|---|
| mV | 384.7 | **163.7 / 163.8** | 66.4 / 66.8 | 40.2 | 23.5 / 22.5 | 13.7 | 13.5 / 13.1 | 15.2 / 15.7 | FAULT | FAULT |

The 63° point hit the per-point current abort (`ABORT_I`).

- Fit `OK`: minimum **+13.9° ± 0.4**, 18.0 mV raw ≈ **11.5 mV net ≈ 0.077 A**, rms 1.2 mV.
- `BS-CLIFF`: edge 5.5°, margin 8.4° from the fit.

**Positive increment (`offset_rev`)**, net:

| swept | −63 | −53 | **−43** | −38 | −33 | −28 | −23 | −18 | −13 | −11 | −8 | −3 | +7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mV | ABORT_I | 203.4 | **82.5 / 82.2** | 50.4 | 29.9 / 29.4 | 16.8 | 10.6 / 11.3 | 14.5 | 16.1 / 16.4 | FAULT | FAULT | FAULT | FAULT |

- Fit `OK`: minimum **−20.9° ± 0.6**, 29.9 mV raw ≈ **9.9 mV net ≈ 0.066 A**, rms 2.5 mV.
- `BS-CLIFF`: last good −13, first fault −11, edge −12.0°, margin 8.9°.
- The edge is not sharp. −13° ran clean twice here and twice in run 3, but faulted in run 4.
- `drift_flag TRUE` is not a current change. The references read 82.5 and 82.2 net; the raw
  readings rose because the zero moved from 7 to 20 mV at a restart (§5).

## 3 · LEFT motor, half speed — neither leg could locate its minimum

| Leg | Points, net mV | Fault | Skipped | Status |
|---|---|---|---|---|
| NEG | 43: **920.1** · 29: 241.1 · 24: 135.8 · 19: 70.6 · 14: **34.5** | 4 | 9, −1 | `TOO_FEW` (4 of 5) |
| POS | −43: **452.9** · −36: 221.5 · −31: 121.3 · −26: 61.1 · −21: **29.8** | −11 | −16, −6 | `TOO_FEW` (4 of 5) |

- **Both curves are still falling at the last good point before the fault.** The negative
  minimum is at or below 14°; the positive minimum is at or above −21°. Neither is resolved.
- Why (DERIVED from source): after the first fault, the window limit is the last good point
  *measured in this leg*. At half speed that was the confirmation centre itself, so the points
  between it and the fault (9° and −16°) were never measured.
- **The half-speed confirmation the apply rule requires did not hold.** The quarter-speed
  minima (13.9° and −20.9°) sit on or inside the edge of the half-speed usable window.
- Even so, the reduction at the best measured points is large (DERIVED):
  - negative: 34.5 against 920.1 at the default (−96 %);
  - positive: 29.8 against 452.9 (−93 %).
- The half-speed negative/positive ratio at the defaults is 2.03 (quarter speed: 1.98).

## 4 · RIGHT motor, quarter speed

**Positive increment**, net:

| swept | −63 | −53 | **−43** | −33 | −23 | −18 | −13 | −3 |
|---|---|---|---|---|---|---|---|---|
| mV | ABORT_I | 218.6 | **94.1 / 90.6** | 33.5 | **13.0** | 16.3 | FAULT | FAULT |

- Reported `NOT_BRACKETED / EDGE_FAULT`. **This is an instrument defect** (§6.2): net, −18° is
  25 % above the low; raw, it is 3.6 % above, under the 4 % threshold.
- A three-point parabola through −33 / −23 / −18 gives a minimum near **−22.3°** at ≈12.9 mV
  net ≈ 0.086 A (DERIVED; no fit).
- `BS-CLIFF`: edge −15.5°, margin about 6.8°.

**Negative increment** (the log stops partway through), net:

| swept | 53 | **43** | 33 | 23 | 18 | 13 | 8 | 3 | −7 |
|---|---|---|---|---|---|---|---|---|---|
| mV | 402.4 | **170.0** | 71.3 / 72.5 | 25.9 / 26.1 | 15.2 | 15.4 / 15.8 | 17.6 | FAULT | FAULT |

The 63° point was `ABORT_I`.

- Bracketed `OK`. The log stops at the second 8° fine point, before the fit.
- A three-point parabola through 13 / 18 / 23 gives a minimum near **+15.7°** at ≈14.0 mV net
  ≈ 0.093 A (DERIVED). The bottom is flat from 13° to 18°.
- Edge 5.5°, the same as the left motor.

## 5 · The sense zero is re-drawn at every driver start — MEASURED; cause DERIVED

| Motor | Driver start | i | u | v | w |
|---|---|---|---|---|---|
| LEFT | motor-block start | 8.6 | 0.7 | 6.3 | 6.8 |
| LEFT | after `ABORT_I` restart (12:09:19) | 5.2 | 0.0 | 18.0 | 4.7 |
| LEFT | after `ABORT_I` restart (12:11:44) | 19.8 | −0.2 | 4.7 | 5.2 |
| RIGHT | motor-block start | 74.9 | 88.2 | 69.3 | −0.9 |
| RIGHT | after `ABORT_I` restart (12:15:23) | 12.6 | 17.6 | 0.7 | 1.4 |
| RIGHT | after `ABORT_I` restart (12:15:45) | 12.1 | 3.6 | 1.5 | 0.4 |

- Within one driver lifetime every zero is steady to about 1 mV (MEASURED). Across starts each
  channel changes independently, by up to 62 mV on the current channel and 85 mV on a phase
  channel.
- **PL-30's 72 mV "board offset" was one of those per-start values.** The right board reads
  12 mV after a restart.
- Cause, read from source and filed as **PL-32** (fix task «#3529»):
  - The driver calibrates GIO and VIO once, at cog start, from a single ADC frame each
    (`src/isp_bldc_motor.spin2:2065-2104`), and never recalibrates (`:2432-2452`).
  - Chip's reference driver recalibrates inside the loop (`BLDC_Motor_Driver-REF.spin2:132-205`).
  - `p2kbAppNoteP2an001SinglePinInstrumentationAdc` says to discard 3 samples after each source
    switch.
- **Consequence:** `getCurrent()` carries a per-start offset of up to about 0.5 A. Every
  net-of-zero figure in this evaluation is unaffected, because each zero comes from the same
  driver lifetime as its point.

## 6 · Instrument defects in scan v3.1 — mine to fix (doctrine overlay P3; task «#3530»)

1. **`BS-PAIR2` nets both minima with `ZERO_INIT`.**
   - After a restart that is the wrong zero, so it reports `imbalance TRUE`, ratio_net 0.440.
   - Each minimum netted with its own lifetime's zero gives **negative 11.5 / positive 9.9 =
     1.16**. There is no large imbalance.
2. **Rise and bracket tests compare raw means.**
   - A large zero compresses every relative rise. The right positive leg failed to bracket
     because of this.
   - The tests should compare net means.
3. **Half-speed legs cannot probe between the last good point and the first fault**, so their
   minima stay unresolved at the window edge (§3). They need the same cliff probe as the
   quarter-speed walk.
4. **The reference drift flag is computed on raw means**, so a zero shift reads as drift.

## 7 · Why the log stops

**What the log shows (MEASURED):**
- The last record is the library's `-MOT- inincr = -36_750_000` for point 75 (RIGHT, negative
  increment, fine, 8°), at 12:16:50.488.
- Every earlier point logged its zero command about 4.7 s after the drive command. This one did
  not.
- The session was closed at 12:18:52.

**STEPHEN, 2026-09-13:**
- *"the run just stopped??? with no indication why but didn't terminate correctly.... stopped
  like maybe processor was in a loop?"*
- Then, asked what the wheels were doing: *"both wheels were stopped and free (not breaking)"*.
- Then: *"processor was running, no power loss... just logging stopped so no furhter debug
  output. you can tell from the log that no P2 reset occurred"*.

**Reading:**
- The P2 and the scan kept running; debug logging on the host stopped. That is why the session
  never saw the scan's end marker and did not end on its own.
- The scan's own code is consistent with that. Every loop on the point path is time-bounded:
  steady 4 s, settle 1 s, window, stop 3 s (`test_bench_scan.spin2:1083-1102`, `:1182-1188`,
  `:1249-1281`, `:1414-1423`). Every library method it calls is loop-free or bounded, and the
  library's one unbounded loop, `SyncStatus()` (`isp_bldc_motor.spin2:1411`), has no caller
  (DERIVED).
- Wheels found stopped and free are consistent with the scan having finished or aborted and
  run `shutdownMotors()`, which stops both wheels. Whether it finished, and what it measured
  after 12:16:50, is not recoverable from the log.

**What the stop cost:** the right motor's negative-leg fit, both of its half-speed legs, the
RIGHT `BS-RESULT`/`BS-PAIR` records, and the run's end record.

## 8 · What run 5 establishes

- **Both motors put the hall electrical zero at the same place** (DERIVED):
  - LEFT midpoint −3.5° ± 0.4 (scan);
  - RIGHT about −3.3° (parabola estimates);
  - run 4's three-point estimate for the left was −5.5°.
- **Each direction's quarter-speed minimum agrees across motors within about 2°:**
  - negative +13.9° (L) / ≈+15.7° (R);
  - positive −20.9° (L) / ≈−22.3° (R).

  The fine step is 5°.
- **At those minima the 2× asymmetry is essentially gone:**
  - negative/positive 1.16 on the left, about 1.08 on the right;
  - at the defaults it is 1.98 and 1.85.
- **At quarter speed, no load, the defaults draw 8–14× the minimum current** (left: 163.7 against
  11.5 negative, 82.5 against 9.9 positive).
- **Each minimum sits about 7–10° from a fault edge with no load**, and at half speed the usable
  window closes in on the minimum.

## 9 · Disposition — do not apply

Against «#3522»'s rule:
- both motors agree on each sign's minimum within the sweep resolution: **met** (quarter speed);
- the half-speed confirmation holds: **not met**. Both left half-speed legs are `TOO_FEW`, with
  their minima unresolved at the fault-bounded window edge.
- The right motor's positive minimum comes from a parabola, not a fit (§6.2).
- The right motor's half-speed legs were not logged (§7).

**Carried forward as the candidate pair (not a value to ship):** `offset_fwd` ≈ 14° (negative
increments) and `offset_rev` ≈ 339° (positive increments). The margin question — what survives
load and higher speed with a fault edge 7–10° away — is unchanged from run 4, and that decision
is Stephen's.

**Next:** scan v4 («#3530») fixes §6 and re-runs.
