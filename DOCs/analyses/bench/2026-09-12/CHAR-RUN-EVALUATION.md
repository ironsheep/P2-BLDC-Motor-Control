# Bench Pass 1, step 4 — characterisation run

**Run:** `src/test_bench_char.spin2` on the Rev B boards, 2026-09-12 15:38–15:44, source
`d4f9d39`. Log: `debug_260912-153807.log` (this folder). Meter readings: Stephen's sheet,
transcribed below.

**Valid.** `BC-BANNER` (log:19) reads `cfg_id BENCH`, `left_base 32`, `right_base 16`,
`voltage_enum 6` (18.5 V), `det_mode 30` (auto-detect), `hold_last 8`, `clkfreq 270_000_000`.
Preflight moved both wheels (log:35, log:48). All nine holds `result OK`, no faults; dwell
25–27 s against the 25 s floor.

**Provenance tags:** MEASURED = a log line or a meter reading · DERIVED = a calculation or a
source reading of mine · STEPHEN = his words or his observation at the bench.

---

## Frames — read this before the table

`BC-HOLD` logs the signed `cmd_incre`. The two motors are mounted mirror-image, and this binary
does **not** call `forwardIsReverse()` on the right wheel ([PL-19](../../../PUNCH-LIST.md)), so
a **positive increment on the right motor is robot-reverse** — STEPHEN, observed at the bench on
all four RIGHT holds. The table gives both frames.

## Readings

Meter columns are the mean of the five readings taken across the hold (A, V and W show on every
screen). Sense is the hold's `i_mV_avg` divided by `adc_fram` = 6136 (the S-3 error factor).
Duty and err are the last sample at exit.

| Hold | Motor | Incre | Robot | Meter A | Meter V | Meter W | Sense mV | Duty | Err | Ticks/s |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 quiescent | — | 0 | — | 0.000 | 20.430 | 0.0 | *(PL-21)* | 1 600 | 26 | 0 |
| 1 | L | +¼ | fwd | 0.536 | 20.408 | 10.9 | 90.7 | 7 323 | 58 | 96 |
| 2 | L | −¼ | rev | 1.054 | 20.344 | 21.4 | 169.5 | 8 272 | −44 | 100 |
| 3 | R | +¼ | rev | 0.570 | 20.354 | 11.6 | 91.6 | 7 337 | 44 | 96 |
| 4 | R | −¼ | fwd | 1.058 | 20.326 | 21.5 | 168.2 | 8 185 | −46 | 96 |
| 5 | L | +½ | fwd | 3.004 | 20.230 | 60.7 | 455.7 | 16 064 | 29 | 196 |
| 6 | L | −½ | rev | 5.564 | 20.078 | 111.7 | 839.3 † | 18 246 | −53 | 196 |
| 7 | R | +½ | rev | 3.140 | 20.100 | 63.1 | 483.8 | 16 070 | 37 | 196 |
| 8 | R | −½ | fwd | 5.530 | 19.972 | 110.4 | 843.6 † | 18 401 | −65 | 196 |
| post | — | — | — | 0.000 | 20.146 | 0.0 | — | — | — | — |

† The logged average overflowed a long ([PL-20](../../../PUNCH-LIST.md)); the value shown is
recovered exactly — the sum wraps once, and the result lands inside the logged `[min, max]`.

**Rotating values, as read during each hold:**

| Hold | Ah | Wh | Ap | Vm | Wp |
|---|---|---|---|---|---|
| 0 | 0.000 | 0.0 | 0.00 | 20.41 | 0.0 |
| 1 | 0.002 | 0.0 | 0.55 | 20.39 | 11.0 |
| 2 | 0.006 | 0.1 | 1.08 | 20.32 | 21.9 |
| 3 | 0.012 | 0.2 | 1.08 | 20.32 | 21.9 |
| 4 | 0.017 | 0.3 | 1.08 | 20.31 | 21.9 |
| 5 | 0.033 | 0.5 | 3.08 | 20.21 | 62.3 |
| 6 | 0.061 | 1.2 | 5.72 | 20.08 | 115.0 |
| 7 | 0.092 | 1.8 | 5.72 | 20.00 | 115.0 |
| 8 | 0.116 | 2.3 | 5.72 | 19.98 | 115.0 |
| post | 0.146 | 2.9 | 5.72 | 19.92 | 115.0 |

---

## Findings

### 1 · A negative increment draws 1.8–2× the current of a positive one, on both motors

MEASURED, by two independent instruments at matched tick rate:

| Pair | Meter − / + | Sense − / + (offset removed) |
|---|---|---|
| Left ¼ | 1.97 | 1.97 |
| Right ¼ | 1.86 | 1.93 |
| Left ½ | 1.85 | 1.86 |
| Right ½ | 1.76 | 1.76 |

The speed loop holds the rate by raising duty ~13% on the negative increment (MEASURED), and
`|err|` at half speed is larger on the negative increment (53, 65 against 29, 37 — single
samples, suggestive only).

**It follows the electrical direction, not the platform** (DERIVED). In motor frame both
motors agree; in robot frame they are opposite. A mechanical load — a rubbing tyre, a castor,
a bearing — follows either the robot's direction or one wheel, never the increment sign on
two mirror-mounted motors. Battery sag is excluded separately (finding 5).

**Which offset each direction uses** (DERIVED from source, CMPM semantics from `p2kbPasm2Cmpm`):
a negative increment sets C in both selection sites — `testb tgt_incr, #31` in
`initAngleFmHall` (`isp_bldc_motor.spin2:2416`) and `cmpm angle_, prior_angle` in the main loop
(`:2329`, C = MSB of the difference) — and C selects **`offset_fwd_` (43°)**. A positive
increment uses `offset_rev_` (317° = 360 − 43). **So the high-current direction runs on the
offset that was characterised, and the low-current direction on the derived one.** The names
contradict the behaviour; both sites agree with each other.

That does not clear the 43/317 pair — it relocates the suspicion. Using 43 and −43 assumes the
hall pattern's electrical zero sits exactly at 0°. If it does not, one direction gets more
lead than it needs and the other less, whichever value was measured. **A lower current is not
proof of a correct offset**; only the per-direction minimum-current sweep (T1-10) locates it.

**Link to the field report** (DERIVED): under `forwardIsReverse()` the right motor runs a
negative increment whenever the robot drives forward — the high-current direction. That is the
shape of *"right usually faults"* in [the user report](../../user-report-2026-09-09-ANALYSIS.md).

### 2 · S-3 is confirmed end to end, and the current channel is sound

Least-squares over the eight motion holds (DERIVED from MEASURED):
**sense_mV = 150.1 × meter_A + 9.1**, worst residual 4.7 mV (≈ 0.03 A).

- 150 mV/A is the Rev B scale the library already assumes — gain 50 × 3 mΩ
  (`isp_bldc_motor.spin2:692-694`).
- The implied error factor is **6138** against the predicted 6136 (0.03%).
- The channel is alive, linear from 0.5 A to 5.6 A, and load-responsive. «#3503» is
  verification, not an experiment.

### 3 · Board detection misreports a real Rev B board as Rev A after any stop/start

MEASURED: cold, both groups read Rev B — pinSum 103 on base 32 (log:21) and 100 on base 16
(log:36). Every later start of a group whose cog had already run read **pinSum 0 → "64010 Rev
A"**, 4 of 4 (log:463, 1252, 2061, 2856). Per pin group: base 16 read a clean Rev B immediately
after the base-32 cog stopped.

All eight motion holds therefore ran with the library believing Rev A. The raw sense data above
is unaffected (it precedes the board scale), and `dead_gap` printed 70 either way (log:467).

**Mechanism** (silicon doc v35 via `p2kbArchSmartPins`; source lines as cited): the driver
configures `base+0..4` as ADC smart pins (`:1929`); `stop()` pinclears only `base+8..15`
(`:127`). A smart pin whose DIR goes low is reset *"and it does NOT lose the configuration set
by the last WRPIN"*. When `getBoardType()` next runs, `base+4` is still a smart pin, so its IN
signal is the smart pin's **handshake flag, not the pin's level**; `pinfloat()` (`:781`) holds it
in reset, reset clears the flag, and all 500 `pinread()` calls (`:784`) return 0 — the
`pinSum == 0` branch, `REV_A`. Detail and fix: «#3500».

⚠ `p2kbSpin2Cogstop` says cogstop disables smart pin modes. The silicon-doc text says a DIR-low
reset keeps the configuration, and this measurement sides with the silicon doc.

### 4 · Meter behaviour

- **Ap latches** (MEASURED): 1.08 held through holds 3 and 4 (steady 0.57 A, 1.06 A); 5.72 held
  through holds 7, 8 and back to 0.00 A. **Vm latches the minimum and Wp the peak** the same
  way. The Ap-for-fault-current technique (T1-7) survives.
- **Ap does not over-read** (MEASURED): each new peak landed 1.5–3% above that hold's steady
  current (0.55/0.536, 1.08/1.054, 3.08/3.004, 5.72/5.564), and the ramped starts produced no
  surge. **No fast transient occurred, so capture of one is still unmeasured — Ap remains a
  lower bound for fault current.**
- **A pack disconnect clears Ah and Wh together with Ap, Vm and Wp.** MEASURED: at hold 0 all
  five read zero (Vm reading the live voltage), although the 2026-09-11 runs drew current.
  STEPHEN confirmed the pack was disconnected in between: *"yes battery would have been dead if
  i hadn't"*. Every power cycle therefore hands the next run a clean energy baseline — and, since
  the P2 runs from the pack, every run begins on one.
- **Quiescent zero** (MEASURED): 0.00 A, 20.43 V, 0.0 W, P2 and boards powered.
- **Every screen shows A, V and W** plus one rotating value (STEPHEN). Each hold therefore
  yielded five amp readings, not one.

### 5 · Battery sag does not explain finding 1

The meter's voltage reading is validated: it agrees with a DMM to 0.01 V on the Rev B system
(STEPHEN, 2026-09-12).

MEASURED: 20.43 V at rest → 19.97 V under the last 5.5 A hold → 20.15 V at rest after 0.146 Ah
and 2.9 Wh. Sorted by voltage, the holds fall in time order except where load pulls a hold
below its neighbour.

DERIVED: each negative-increment hold ran just after its positive partner at slightly lower
voltage; at a regulated speed that biases current by at most ~0.5%, against a 76–97% difference.
And hold 3 (right, +¼) ran *after* hold 2 at lower voltage yet drew half its current.

### 6 · The two motors are matched

MEASURED: at the same increment sign, left and right agree within 6% positive (0.536/0.570,
3.004/3.140) and within 1% negative (1.054/1.058, 5.564/5.530). The asymmetry is common to both
motors — not one bad motor or board.

### 7 · Doubling speed raises power ~5.5×

MEASURED: 96 → 196 ticks/s took positive-increment power 10.9 → 60.7 W (5.6×) and the left
negative-increment 21.4 → 111.7 W (5.2×). Two rungs only, so no exponent is claimed; no-load
losses are rising faster than the square of speed.

---

## Instrument defects found

| | Defect | Effect on this run |
|---|---|---|
| [PL-19](../../../PUNCH-LIST.md) | right-wheel captions in robot frame, drive in motor frame | none — `cmd_incre` attributes every hold |
| [PL-20](../../../PUNCH-LIST.md) | `i_mV_avg` overflows a long at the pre-S-3 scale | holds 6 and 8, recovered exactly |
| [PL-21](../../../PUNCH-LIST.md) | quiescent hold reads a stopped instance's frozen telemetry | no sense zero from hold 0; the fit supplies ~9 mV |

## Not answered by this run

- Whether **Ap captures a fast excursion** — none occurred.
- **The offset that minimises current in each direction** — T1-10's sweep.
- **Where the electrical zero of the hall pattern actually sits** — the question finding 1 now
  turns on.
- A **power-versus-speed curve** — two rungs are two points.
