# Bench Pass 2a — scan run 4 (scan v2, stand reseated)

**Log:** `src/logs/debug_260913-012757.log` (342 lines; curation pending).
**Source:** `5ea0510`. Banner: `src_rev 2, fmt 2, cfg_id BENCH`, left 32, right 16.
**Run:** 01:27:57. It ended on its own at 134 s with `BS-END ABORTED SELF_CHECK_MISS` (RIGHT,
first miss ZERO), after the left motor finished both ¼-speed legs.

**Provenance:** MEASURED = a log line · DERIVED = my calculation · STEPHEN = his words.
Sense readings are in mV at 150 mV/A. "Net" is the reading minus the nearest `BS-ZERO`.

---

## 1 · Foundations — MEASURED

- `illegal 0` / `missed 0` on all six starts. Rev B at every start.
- LEFT self-check passed:

  | Check | Measured |
  |---|---|
  | zero | 6.7 mV |
  | +¼ | 90.1 mV |
  | −¼ | 170.7 mV |
  | ratio | 1.894 |
  | rate | 98.2 |

- Scan v2's new records all appeared: `BS-ZERO` phase tags, `CLIFF` points, `BS-CLIFF`.

## 2 · LEFT curves — MEASURED (net in brackets)

**Negative increment (`offset_fwd`)**, ¼ speed, zeros 7.2–8.0 mV:

| swept | 63 | 53 | **43** | 33 | 23 | 13 | 8 *(cliff probe)* | 3 | −7 |
|---|---|---|---|---|---|---|---|---|---|
| mV | ABORT_I | 389.1 | **170.9 / 169.8** | 71.4 [63.9] | 29.9 [22.4] | 20.4 [12.9] | 21.5 [14.0] | FAULT | FAULT |

`BS-CLIFF`: last good 8, first fault 3, edge 5.5°, margin 7.5° from the lowest point.

**Positive increment (`offset_rev`)**, ¼ speed, zero 7.7 at REF_START:

| swept | −63 | −53 | **−43** | −33 | −23 | −18 *(cliff probe)* | −13 | −3 |
|---|---|---|---|---|---|---|---|---|
| mV | ABORT_I | 209.4 [201.7] | **89.3 [81.6] / 100.4 [81.5]** | 37.3 [29.6] | 18.2 [10.5] | 22.6 [14.9] | FAULT | FAULT |

`BS-CLIFF`: last good −18, first fault −13, edge −15.5°, margin 7.5°.

**Both legs reported `NOT_BRACKETED`, so neither leg fitted and both ½-speed legs were skipped.**
The data do show a minimum inside each window: the cliff probe reads higher than the lowest
point in both legs. §6 covers why the scan still reported no bracket.

## 3 · The minima, the hall zero, and why the defaults are lopsided — DERIVED

A parabola through the three points around each low (net values):

| | points used | minimum | current at minimum |
|---|---|---|---|
| Negative | 8, 13, 23 | **+11.9°** | 12.8 mV ≈ 0.09 A |
| Positive | −33, −23, −18 | **−22.9°** | 10.5 mV ≈ 0.07 A |

Run 3's independent positive fit gave −21.1° ± 0.7.

- **The hall pattern's electrical zero sits near −5°**, not 0°. The midpoint of the two minima
  is −5.5° (−4.6° with run 3's positive fit), and the midpoint of the two fault edges is −5.0°
  (−2.5° with run 3's positive edge).
- **That explains the 2× asymmetry at the defaults.** Measured from −5°, the default 43 gives
  the negative direction about 48° of lead and the default 317 (−43) gives the positive direction
  about 38°. At those defaults the net currents are 163 vs 82 mV.
- **Each direction's minimum sits about 17° from that zero**, and the currents at the two minima
  are within 1.2× of each other. **A pair centred on the measured zero — about 12° / 337° —
  would make forward and reverse load near-identical at roughly a tenth of today's current**
  (≈ 0.09 / 0.07 A against ≈ 1.09 / 0.54 A at ¼ speed, no load).
- **But each minimum is only 6–7° from a fault edge, with no load.** The fault edge is also not
  sharp: −13° ran cleanly twice in run 3 and faulted in run 4. Run 3 showed the positive minimum
  moving 5.7° toward its edge at ½ speed. Nothing here says what margin survives a robot's weight
  or higher speeds.

## 4 · The drift was a zero shift — MEASURED

- The positive leg's references read 89.3 then 100.4 (`drift_flag TRUE`). The zeros taken just
  before them read 7.7 then **18.9**, so the net references are **81.6 and 81.5**: identical. The
  current did not change; the sense zero rose ~11 mV.
- The 18.9 zero was read 1.5 s after the driver restarted following the `ABORT_I` at −63. The
  negative leg's zero, read 32 s after its own `ABORT_I` restart, was normal (7.2).
- Run 3's unexplained ~13 mV-high stretches are consistent with the same shift. At the same
  offsets without it, runs 3 and 4 agree within 1 mV: positive −23: 17.4 / 18.2; −33: 36.9 / 37.3.
- **Consequence:** net-of-zero is the reliable measure, and a zero is needed after every driver
  restart, not only at the references.

## 5 · RIGHT motor — the reseat did not change the offset

| Reading | Run 3 | Run 4 (reseated) |
|---|---|---|
| zero | 73.4 | **72.1 / 72.6 / 71.4** |
| +¼ raw [net] | 161.2 [87.8] | 163.7 [91.1] |
| −¼ raw [net] | 237.3 [163.9] | 240.2 [168.8] |
| rate | 98.2 | 98.2 |

- MEASURED: the right zero is steady at 71–73 mV across runs and across the reseat. Net of it,
  the right motor behaves like the left (+10 % positive, +3 % negative) with a net ratio of 1.85.
- DERIVED: stand drag cannot explain a reading taken with the wheel stopped, and the reseat left
  it unchanged, so a mechanical cause is effectively ruled out. Two explanations remain: an offset
  in the right board's sense path, or a real ~0.45 A flowing in the right bridge at idle.
- **Resolved from source (DERIVED, 2026-09-13, while building scan v3): it is a sense-path
  offset.** The drive was already floated for every zero reading:
  - `isp_bldc_motor.spin2` `init()` sets `stop_mode := SM_FLOAT` (line 335);
  - the scan never changes it;
  - the driver's `.checkstop` disables PWM at zero command in that mode.

  No current can flow through the bridge during the reading, so the right motor's 72 mV is an
  offset in its sense path, not an idle current. The planned floated-zero check would have
  repeated the same reading and was dropped.

## 6 · Why run 4 produced no fits — the scan's bracket rule

`evaluateBracket` decides each side from the walk's stop reason. A walk that stopped on faults is
never bracketed, even when the cliff probe beside the low reads higher. Its rise rule (+15 % over
the low, and at least 2 points past it) cannot be met between a low and a fault edge 10° away.
Both legs stopped on faults this time, so neither fitted, and the ½-speed legs, which depend on
a ¼-speed fit, were skipped. I accepted this limitation when I reviewed scan v2. Its cost is the
fits and the ½-speed confirmation. Scan v3 bounds the sweep window at the last good point
instead.

## 7 · Disposition

**Do not apply.** The left motor has no fit and no ½-speed data; the right motor has no scan
data; every minimum sits 6–7° from a fault edge measured without load. §3's centred pair is the
candidate to carry forward, not a value to ship.
