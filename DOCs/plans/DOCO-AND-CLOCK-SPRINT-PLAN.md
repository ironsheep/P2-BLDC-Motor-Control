# 6.2.0 — DocoEng qualification, clock independence, serial — sprint plan

**Status:** STARTED 2026-10-03 (`sprint-start`; entry record in §16).
**Release:** v6.2.0 at the end of this plan (§12; STEPHEN 2026-10-03, *"yes a"*). The ship word is his.
**Baseline at planning:** tree `08cad4f`; `DRIVER_REV 49` (`src/isp_bldc_motor.spin2:6818`); `test_bench_dual`
SRC_REV 82; gates: §15.

---

## 0. What this sprint is for

**Goal.** v6.2.0 ships with nothing left untested that the release claims. Three fronts:

1. **The DocoEng 4,000 RPM motor qualified** on the single-motor configuration, on a Rev A board, at every voltage the
   driver has a Doco row for, judged against an independent shaft encoder; its tables re-measured; any driver change the
   measurements require built (each brought to Stephen first); and the offset sweep generalised into a motor-adoption
   tool (PL-176) once two real motors have been measured.
2. **Clock independence.** Every mechanism that depends on the system clock is found and made clock-independent as far
   as the silicon allows; where a floor is real, it is derived, stated and refused at start.
3. **The serial control path tested** on hardware, enough to say it is tested.

**Done means:** every section below is built and gated; the bench visits (§10) have run and their evaluations give every
cell a verdict; the Doco, clock and serial Known Issues of v6.1.0 are gone from the v6.2.0 entry (or reworded to what
was tested, by Stephen's word); every user document is current; v6.2.0 is prepared for Stephen's tag.

**Scope, in Stephen's words (2026-10-03):**
- *"let's do B please"* — the Doco qualification plus PL-176, the motor-adoption tool.
- *"yes A"* (the bar) — the behaviours at every voltage judged against the encoder; the tables re-measured; the limit
  behaviour under a hand load; any driver change the measurements require, brought with its benefit first.
- *"yes a"* (the release) — v6.2.0 at the end of this plan; *"and we'll likely do a lightweight certify of serial drive
  too"*, *"i'm just trying to close all aspect so we no longer have anything untested for this release"*, *"so
  suffient is just that enough to say that we've tested it"*.
- *"no floor on revA, and no doco and revB, we have sufficient to not need this. You keep citing clock range issues -
  this driver is just supposed to work a users selected clock range. If we encoded mechanisms that are not clock
  independent then we maybe built this incorrectly. we need to understand exactly are sensative to clock speed and make
  adjustments to eliminate any such areas as much as feasible."*

**How the work runs (standing):** P10 — root cause and design at the desk, the bench certifies; P5 — a new driver
function or a changed driver behaviour goes to Stephen with its measure of benefit before it is built; P14 — the user's
clock is the user's choice (2026-10-03); the gate runs once per complete batch; the bench is fed by the pack
(`tools/make-bench-pack.sh`) and Stephen runs every tier; a follow-up visit carries only loads that feed a finding; no
run sheet asks Stephen to work a control to mark the log; every hand-back ends `BENCH: READY -- <commit, commands>` or
`BENCH: NOT READY -- <what remains>`.

### 0.1 Standing rulings that bear on this scope

| Ruling | Words and date | Where it binds |
|---|---|---|
| Build the instrument for the 6.5″, use it for the Doco, generalise after both | *"we could just build this as our standard instrument today and use it for this phase for the 6.5, and use it for the doco when we get there. After having experience with it, we can generalize it to a real tool"* (2026-09-21); the Doco run records what had to be edited, and that list is the tool's specification | §4, §8 |
| `ADDING_MOTOR.md` describes the procedure as it is, and promises no tool before it exists | Bench Readiness plan, 2026-09-21 | §8, §11 |
| The Doco was certified (2023) with an on-shaft encoder | *"the doco was certified with external position encoder on-shaft."* (2026-09-17) | §3 |
| The 2026-09-17 "pnut-ts only" instrument ruling | *"you only need pnut-ts for now"* — **superseded** by the Doco bench's encoder (2026-10-03); `.claude/skill-conventions.md` is updated in §3 | §3 |
| The Doco bench | Rev A board on P16-P31; encoder A/B on P48/P49 with resistors on the lines; 30 A bench supply, voltage dialable; no voltage sensing, so the voltage a program is told is the only source; no wheels; the shaft loaded by hand at low speed (2026-10-03) | §2, §3, §4, §7 |
| Not in this plan | No Rev A floor runs for the 6.5″; no Doco on a Rev B board (*"we have sufficient to not need this"*, 2026-10-03) | §14 |
| One P2 driving 1-3 motors, back-EMF, the vibration study | Not chosen (option (b) of the scope question, 2026-10-03); PL-175, PL-177, PL-174 stay on the list | §14 |
| Platforms are never swapped; Rev A boards on one platform, Rev B on the other | standing (memory, R20) | §9, §10 |
| A test built on a wrong premise is corrected before it runs again | 2026-10-01 | §4, §7 |
| Fault returns use the guarded `testForceFault()` | *"fp1: A"* (2026-09-28) | §7 |

### 0.2 Order and bench visits

The fronts advance together (overlay P12); the clock work lands first because every later measurement inherits it.

1. **§1 clock independence** (desk: fixes, start floor, harness clocks) — behaviour at 270 MHz kept identical except
   where a fix corrects it, shown by `tools/pasm_equiv`.
2. **§2 the Doco bench configuration, §3 the encoder instrument, §4 the Doco measurement harness, §5 the Doco desk work**
   (servo model Doco set, offset-voltage fix, PL-71's shape) — one batch, one gate.
3. **Visit D1 (Doco bench)** — measure: each voltage's tables, the encoder's hall map, today's behaviour as the
   reference; the clock probe on the encoder (§1.4).
4. **§6 tables and any ruled driver changes; §8 the motor-adoption tool** (from D1's record of what had to be edited);
   §7 the qualification cells; §9 serial desk re-check — one batch, one gate.
5. **Visit D2 (Doco bench) and the 6.5″ wheels-up session (Rev B platform)** — certify: the tool reproduces D1, every
   qualification cell at every voltage, the hand-load limit and hold; on the 6.5″, `serial_certify.py`, the front-cog
   load and the tool on one wheel at the lowest supported clock and at 270 MHz.
6. **§11 documentation; §12 release.**

**Bench visits in this plan: two Doco visits and one 6.5″ wheels-up session** (the last can share D2's day). A finding
that needs a fix and a run is the only way another is added (overlay P10).

### 0.3 Established decisions for dispatch

`plan-to-tasks` writes the `sprint_established_decisions` key fresh (the 6.1.0 key was cleared at closeout). This plan
changes neither ABI run (status 24, params 27; `isAbiLayoutValid()`); a section that finds it must is a scope change
brought to Stephen. P14 joins the list: no new timing, rate or budget may be fixed at a clock.

---

## 1. Clock independence (P14)

**Why.** Every demo and bench pass ran at 270 MHz; v6.1.0 lists *"below about 250 MHz its timing is unproven"*. Stephen
(2026-10-03): the driver works at the user's clock, and a mechanism that does not is a construction defect.

**Starting point** — the inventory of 2026-10-03 (a read-only survey; DERIVED unless marked; MODELED = `tools/pasm_equiv`):
- The PWM frame and the ADC period are derived at run time from `CLKFREQ`: `ticks1us = CLKFREQ/1e6`,
  `frame_cnt = ticks1us*22727/1000` (`src/isp_bldc_motor.spin2:4352-4354`, `:4405`), so the 44 kHz frame holds in real
  time. Frame-counted mechanisms (servo trim, fold-back, `BRAKE_PERIOD_FRAMES`, the release wait, calibration widening)
  are therefore clock-independent.
- **The drive pass's 23-frame count rests on a 2-22 clock margin.** The pass ends at the first frame end past
  `cfg_ctcks = ticks500us` (`:4354`, `:4450`, tested by `jnct1` at `:8128`). For a whole-MHz clock M, 22 frames fall short
  of the deadline by 0.006·M plus up to 22 clocks: 2 at 150 MHz, 4 at 300, 8 at 270. Wake-up jitter in `wait4adc`
  (`:8195-8198`, 0-5 clocks) and hub-window phase (0-7 clocks unless the frame is a multiple of 8 clocks — at 270 MHz it is,
  6136 = 8 × 767) can occasionally make a 22-frame pass at 150 or 300 MHz: field speed +4.5 % and acceleration +9 % on that
  pass. Everything counted in passes inherits it (ramp steps `:4609-4621`, hold decay `:7127`, `DRIVE_PASS_US` `:5520`,
  the speed table, `RELEASE_TIMEOUT_US` `:6812`). PL-50's note about 176/264 MHz is wrong for the code as written.
- **The front cog's 1 ms pass is timed from `CLKFREQ`** (`:5767`; steering `isp_steering_2wheel.spin2:2601-2602`), but its
  Spin2 body has a fixed cost in clocks: 533 µs worst MEASURED at 270 MHz (PL-161) is 143,910 clocks, late past 900 µs
  (`LATE_MARGIN_US` 100, `:5826`) below 159.9 MHz. A late pass is re-anchored, not replayed, so every front-counted time
  stretches (`WINDOW_PASSES`/`HALL_WINDOW_SIZE` `:5506-5507` — the speed window reads low —, `BLOCKED_PASSES` `:7332`,
  `CURRENT_AVG_SHIFT` `:7304`, the hold passes `:2971-2972`), and `REQ_ACK_TIMEOUT_MS` 20 (`:5523`) can expire.
- **Further items:** the dead gap rounds down (`:4422`; 248 ns for a literal 250 at 270 MHz, `DRIVER-THEORY-OF-OPERATIONS.md:461`);
  the duty floor is a fixed `100 << 4` (`:4427`); `FOLD_MIN_MV` 4 (`:7331`) was derived from noise measured at 270 MHz while
  the ADC resolves 3300/F mV (0.54 mV at 270, 1.45 at 100); the board-detect reads have a fixed instruction pitch
  (`:1996-1999`, `:4826-4829`); the `driveinit` 20-clock low-side blip must stay under 250 ns (≥ 80 MHz, `:8802-8808`); the
  PASM worst window is 1,959 clocks (MODELED), so a frame fits at ≥ 86 MHz, ≥ 115 MHz under the project's 75 % rule;
  the host serial's bit period is an integer (`isp_serial_singleton.spin2:116,128`; the SBUS receiver already uses the
  smart pin's fractional bits, `jm_sbus_rx.spin2:113`); the Spin2 serial receive loop has 16 µs per character at 624 kbaud
  (`isp_queue_serial.spin2:605-608`), its cost per character unmeasured.
- **Demos:** every demo and `isp_steering_serial.spin2:22` fix `CLK_FREQ = 270_000_000` (with `_clkfreq = CLK_FREQ`
  beside it); the HDMI demos `CLKSET` to the
  video mode's 270 MHz (`p2videodrv.spin2:325-331`), so they run at that clock only; **`demo_single_motor.spin2:185`'s
  `waitms(END_HOLD_MS)` (`END_HOLD_MS = 20_000`, `:51`) exceeds `waitms`'s 2^31-clock bound above ~107 MHz and returns at once (a defect today, at 270 MHz;
  p2kb `p2kbSpin2Waitms`).**
- **Silicon** (p2kb `p2kbArchClockSystem`): PLL output rated 3.33-320 MHz (180 typical), 350 overclock; a crystal-derived
  clock may miss `_clkfreq` by up to `_errfreq` (1 MHz default), so non-integer-MHz clocks occur.

**Target.**
1. **The pass deadline gets half a frame of margin:** `cfg_ctcks := DRIVE_PASS_FRAMES*frame_cnt - frame_cnt/2`, with
   `frame_cnt` derived from `CLKFREQ/PWM_RATE_IN_HZ` rounded and made even (the PWM half-period and the ADC period agree,
   `:4410`, `:8826`). K = 23 at every clock by construction.
2. **Dead gap rounded up** from a 64-bit `clkfreq` product (never under 250 ns, the manuals' minimum); **duty floor** as a
   fraction of the frame; **`DRIVE_PASS_US` computed** from K, F and the clock.
3. **The front cog is clock-independent in its counted times:** every front-counted duration is expressed in time and
   converted at start (or the pass's measured length is used), so a slower clock lengthens the pass, not the times; the
   stop-plan's read-to-write bound (archive `PUNCH-LIST-ARCHIVE-2026-10-01.md:800`) is re-derived. Its body cost is then
   the floor, measured (§1.4) for one motor and for two.
4. **`FOLD_MIN_MV` derived from the ADC's resolution at the running clock** (`max(4, k × 3300 / F)`), and the board-detect
   reads paced by `getct`.
5. **Serial:** the bit period with the smart pin's fractional bits; the receive loop's cost per character measured, and the
   loop moved to PASM only if it sets a floor above the driver's.
6. **One derived floor, refused at start:** `start()` returns a named error (new, `ERR_CLOCK_TOO_SLOW`) when `CLKFREQ` is under
   the highest of the derived floors (the PASM window under the 75 % rule, the front pass, `driveinit`, serial if used).
   **This is a new refusal: it comes to Stephen with its measure of benefit before it is built (P5).**
7. **Demos:** the 20 s hold in slices of at most 1 s; each demo's clock line says the range it supports; the HDMI demos say
   they run at the video clock.
8. **Harness at any clock:** `test_bench_dual`'s clock cells (`CLK_SWEEP_*`, `EXP_FRAME_*`, `:1786-1791`, `:2706`,
   `:28533-28545`) judge the frame and pass at any built clock, not three named ones; `tools/bench-run.sh:45-97` takes a
   clock; long waits sliced so no window exceeds the `waitms`/`getct` bound at 350 MHz.

**Integration.** No ABI change (all are values of existing parameters or Spin2-side constants). DRIVER_REV bump.
`tools/pasm_equiv` gains a clock argument for its frame budget.

**Verify.**
- *Normal:* at 270 MHz the image is equivalent to DRIVER_REV 49 outside the changed values (`pasm_equiv`), and every
  value changed at 270 is listed with its before/after (the dead gap 70 → 71 clocks is expected).
- *Edge:* desk tables, per clock 100-350 MHz in 1 MHz steps and at non-integer clocks: K = 23, dead gap ≥ 250 ns, frame
  even, duty floor fraction constant.
- *Error:* a build at a clock below the floor refuses `start()` with the new error and drives nothing.
- *Bench (§1.4).*

### 1.4 What the bench certifies for the clock — only what would catch a failure

- **Pass period, on the Doco with the encoder** (Visit D1): a constant command per direction for ≥ 10 s at the lowest
  supported clock, 200, 270 and the highest, and one non-integer-MHz clock; the encoder's speed against `incr × pass rate`
  to ±0.1 %. A 22-frame pass shows as a fast reading.
- **The front cog under the heaviest load** (6.5″ session, two wheels, the RC demo shape): `testGetFrontStats()`'s late
  count 0 and its worst pass under 900 µs at the lowest supported clock; the worst posted-request acknowledgement under
  `REQ_ACK_TIMEOUT_MS`.
- **Frame budget and dead gap** (6.5″ session, `test_bench_t0`'s frame-budget and T0-1 cells, `:673-675`, `:1749-1753`)
  at the lowest supported clock.
- **Current-sense noise** against the derived `FOLD_MIN_MV` at the lowest supported clock, on Rev A (Doco) and Rev B (6.5″).
- **Serial** at the lowest supported clock: `serial_certify.py` (§9) plus back-to-back maximum-length lines, in plain and
  `-d` builds.

---

## 2. The Doco bench configuration

**Why.** No bench tier can build for the Doco: `tools/bench-run.sh` always compiles with `-D BENCH_CFG`
(`:774-809`), which selects `src/isp_bldc_motor_userconfig_bench.spin2`, a fixed statement of the 6.5″ dual platform
(`:50`, LEFT P32, RIGHT P16, 18.5 V).

**Target.** A second fixed bench statement, the Doco bench as it is (2026-10-03): `MOTR_DOCO_4KRPM`, one motor on
`PINS_P16_P31`, `BRD_AUTO_DET` (it must read Rev A; a run that reads otherwise stops), no wheel (`WHEEL_DIA_IN_INCH` 0.0),
no pack sensor, the encoder pins reserved (P48/P49). Selected by its own define (`-D BENCH_CFG -D BENCH_DOCO`), so the
6.5″ statement is untouched. The drive voltage is a build parameter of the Doco tiers, one tier per Doco voltage, and the
log banner prints it: on this bench the voltage a program is told is the only source (Stephen, 2026-10-03).
`tools/make-bench-pack.sh` builds the Doco tiers on request. The pin-group compile checks apply to it.

**Verify.** Every Doco tier compiles; `tools/build-check.sh` examines them; the 6.5″ tiers' binaries are unchanged
(byte-compare before/after); a Doco build on a board that does not read Rev A stops before driving.

## 3. The encoder instrument

**Why.** The encoder is the independent judge of shaft position and speed; the Doco was certified with it in 2023
(Stephen, 2026-09-17), but no log of that exists in the repo.

**Starting point.** A 360 P/R incremental optical encoder, quadrature A/B (source comment: Signswise, DC 5-24 V;
`isp_bldc_motor.spin2:5663-5698`), on P48/P49, the lines carrying their own resistors (Stephen, 2026-10-03). The old
reader is commented out (`:5650-5723`): `pinstart(P48, P_QUADRATURE | P_PLUS1_B, 0, 0)`, a once-a-second RPM.
p2kb `p2kbArchSmartPin01011QuadratureEncoder`: the smart pin counts all four transitions per line as a signed 32-bit
total, so **1,440 counts per revolution (0.25°)**, 60 per Doco hall tick (24 per revolution, `DOCOENG_MOTOR.md:16`).

**Target.** A harness-side reader (not in the shipped driver — the library must not own two test pins in a user's
program): P48/P49 as plain inputs (no internal pull-ups), the smart pin in quadrature totaliser mode, read with
`rqpin`. Records: the encoder count at every hall edge (the hall map), and on the instrument's timebase the encoder
count, the hall position, the drive state, duty and current (stable labelled records, `isp_bench_log`, < 280 bytes).
A self-check cell: one hand-free revolution under drive reads 1,440 ± 2 counts per 24 hall ticks, or the run stops
(wrong P/R, a slipping coupling, a lost line). `.claude/skill-conventions.md` records the encoder as an instrument of
the Doco bench.

**Verify.** Normal: the count per revolution; edge: direction reversal (the count reverses sign), 4,000 RPM (96 kHz of
edges, within the smart pin); error: an unplugged line fails the self-check (the run sheet does not ask for it — the
self-check's negative is shown at the desk with a scratch build that ignores B).

## 4. The Doco measurement harness

**Why.** The motor-adoption tool (§8) is generalised from two measured motors (ruling 2026-09-21). The 6.5″'s
instruments (`test_bench_scan`, `dual-align`) hard-code 6.5″ numbers and two wheels (scan `:298-355`; align
`ALIGN_TICKS_PER_REV 90`, `ALIGN_MAX_CROSS 288`, `test_bench_dual.spin2:1793-1890`).

**Target.** A new single-motor harness, `src/test_bench_single.spin2`, built under §2, whose per-motor numbers sit in one
named-constants block. **Everything that had to change from the 6.5″'s values is recorded as it is changed** — that list
is §8's specification. Legs, each a labelled record set and, where a judgement is possible, a cell:
- **Hall map** (encoder): each hall edge's angle, sector uniformity, the true hall zero Z per direction.
- **Offsets by current minimum** (the scan's method at the Doco's numbers), cross-checked against the encoder's Z; the
  cold back-EMF Z is attempted only if the Doco's back-EMF at hand speed clears the align instrument's clip band (unknown,
  §13).
- **Speed ladder** to each voltage's ceiling: encoder speed against command, duty, current; the feedforward line (duty
  against increment, unloaded); the ceiling with the same duty reserve the 6.5″ keeps (`ADDING_MOTOR.md` step 6).
- **Minimum increment** each direction: the smallest command that turns the shaft steadily (PL-71).
- **Lead check:** the best offset at three speeds; a lead schedule is needed only if it moves (§6).
- **Misdial check:** at the ceiling with no load, the encoder's speed predicts the supply from the spec sheet's back-EMF
  constant (3.53 V/kRPM, `DOCs/DOCOMotor.pdf`); a run whose prediction misses its told voltage beyond a tolerance derived
  from the spec sheet and D1's first run is flagged and its rows are not used.
- **Today's behaviour as the reference:** the §7 behaviours run on the shipped tables, so D2's cells have a measured
  "before".
- **Hand load at low speed** (12 V and 24 V): the current limit holds, the blocked shaft stops itself in its time bound,
  a held stop pushed by hand (the hold defaults, PL-195).

Stop conditions: the scan's, re-expressed in amps through `eDetectedBoard` (its mV thresholds assume Rev B's 150 mV/A;
the Doco is on Rev A, 5 mV/A); a run charge cap for the Doco's 1.8 A rating; the encoder self-check; the misdial check.

**Verify.** Every leg compiles in a Doco tier; each cell shown able to fail by mutation at the desk; the plan's record of
edited constants exists before D1.

### 4.1 Edited from the 6.5″ instruments — the motor-adoption tool's specification (§8)

Kept as the legs land («#3679»; phase 1 wrote the rows below with the hall-map leg; phase 2a, the hands-off measuring
legs, changed the two run caps and added the rows from "The rows" on; phase 2b, the coast-down (removed 2026-10-04,
«#3691»: STEPHEN, qualify the Doco as the 6.5″, no new measurements), the offset scan and the
pass-period probe, changed the two run caps, the misdial and `ALIGN_MAX_CROSS` rows, and added the rows from "The 2b
rows" on; phase 2c, the attended legs, changed the two run caps and the `LEADMOVE_TOL_X10` row, and added the rows from
"The 2c rows" on; «#3686», the §7 qualification, changed the two run caps and the `KE_IS_FITTED` row, and added the rows
from "The 3686 rows" on; «#3694», the cold Z (L-align, D1b's first leg), changed the `ALIGN_MAX_CROSS` row and added the
rows from "The 3694 rows" on; «#3696», D1b's voltage ruling, added the rows from "The 3696 rows" on; «#3697», L-align by hand
in bursts after the 2026-10-05 bench, revised the `ALIGN_MAX_CROSS`, crossing-angle, pace, outcome, matrix and operator's-side
rows and added the rows from "The 3697 rows" on). One row per number the Doco
harness had to change from the 6.5″ instruments. The harness holds them in one block, `CON { the Doco's numbers }` in
`src/test_bench_single.spin2`, and prints them in `B1-MOTOR`. §8 turns each row into a field of a per-motor record. "None"
in the 6.5″ column means the 6.5″ instruments never needed the number. Line numbers are as of tree `1765b5a`; the task
body's `test_bench_dual.spin2:1821` and `:1860` for the ALIGN constants are `:1838` and `:1877` there.

| Harness name | 6.5″ value, where | Doco value | Why |
|---|---|---|---|
| `MOTOR_POLE_PAIRS` | 15 (`test_bench_dual.spin2:1838`, "6 hall ticks x 15 electrical cycles") | 4 | Sheet: 8 poles (`DOCs/DOCOMotor.pdf`) |
| `HALL_TICKS_PER_REV` | 90, `ALIGN_TICKS_PER_REV` (`test_bench_dual.spin2:1838`) | 24, `enc.HALL_TICKS_PER_REV` | The Doco's hall count (`DOCOENG_MOTOR.md`). **The encoder object hard-codes it** (`isp_bench_encoder.spin2:32-33`, with `COUNTS_PER_HALL_TICK` 60), so the tool must pass it to the instrument, not only to the harness |
| `ENC_COUNTS_PER_REV`, `ENC_COUNTS_PER_TICK` | none (no encoder fits the hub; archive `BENCH-READINESS-SPRINT-PLAN.md:195`) | 1,440 and 60 | 360 P/R × 4 edges; 1,440 / 24 |
| `ENC_COUNTS_PER_ECYCLE` | none | 360: **one count is one electrical degree** | 1,440 / 4 pole pairs. On another motor a count is `pp / 4` electrical degrees, and every `_x10` angle field changes meaning |
| Sector nominal (`ENC_COUNTS_PER_TICK`) | 4° mechanical a tick (`isp_bldc_motor_userconfig.spin2:62-69`) | 15° (60 counts) | Geometry |
| `EXPECTED_BOARD` | Rev B: cell R2-SCAN-REVB, `NOT_REVB_LO/HI` 0 (`test_bench_scan.spin2:736-737`) | Rev A (`isp_bldc_motor_userconfig_bench.spin2:66`); a mismatch starts nothing | The Doco bench is Rev A (STEPHEN 2026-10-03) |
| Current-sense scale | 150 mV/A, assumed inside every mV threshold (`test_bench_scan.spin2:567-570`, `:643`, `:657`) | Read from the detected board: `wheel.F_REV_A_RSENSE` 5 mV/A | Every current threshold is now in mA and converted through `eDetectedBoard`. Desk mutation: the scan's 150 mV/A applied to a Rev A stall reading of 25 mV reads 153 mA and never trips the abort; the board's 5 mV/A reads 4,600 mA and trips (desk model, «#3679» phase 1) |
| `ABS_ABORT_MA` | `ABS_ABORT_MV` 1,500 = 10 A at 150 mV/A (`test_bench_scan.spin2:643`) | 3,680 mA = 2 × rated (18.4 mV on Rev A) | The Doco is rated 1.84 A. 18.4 mV is 6× Rev A's ±3 mV frame noise, so 4 samples cannot trip on noise |
| `RUN_CHARGE_CAP_MAS` (base `RUN_CHARGE_BASE_MAS`) | `RUN_CHARGE_CAP_MVS` 432,000 mV·s = 0.8 Ah at 150 mV/A (`test_bench_scan.spin2:657`) | 110,400 mA·s = 1 minute at the rated 1.84 A (the hall map alone), plus `NO_LOAD_MA_MAX` 400 mA over each driven leg's estimated length (`LEGS_DRIVEN_EST_S`): 656,400 mA·s with every hands-off leg (684,400 until «#3691» removed L-coast, 70 s) (phase 2a's five: 374,400); an attended tier builds its one leg: L-handload 230,400, L-heldpush 254,400; «#3686»'s qualification chain (L-wiring 10 s, L-power 150, ladder, ramp, stops: 690 s) 386,400 | The Doco's rating, then the sheet's no-load ceiling over the run's length (phase 2a; phase 2b counts its legs too; phase 2c its two, `LEG_HANDLOAD_EST_S` 300, `_HELDPUSH_` 360, the time their steps run; `LEG_COAST_EST_S` 70, `_SAG_` 180 and `_PINCH_` 75 removed 2026-10-04, «#3691»): the unloaded model draws 0.02-0.16 A of DC link, the 2023 notes up to 0.89 A at a top for seconds. L-handload's own two stall caps (the 2c rows) bound its stalls first |
| `TEST_PEAK_A`, `TEST_CONT_A` | the library's `I_PEAK_A` 40 / `I_CONT_A` 27, the MOSFETs' (`isp_bldc_motor.spin2:7559-7560`); the scan runs at them | 2 / 2 A from the first leg (`testSetCurrentLimits()`) | A 1.84 A motor. MODELED (analysis F9, P-H2): on Rev A this holds a firm stall to 2.1 A at 12 V and 2.9 A at 24 V |
| Rest-zero health | `ZERO_ABS_MAX_MV` 300, one band (`test_bench_scan.spin2:570`) | The library's band for the detected board: Rev A ±17 mV (`isp_bldc_motor.spin2:7433-7434`) | Board-dependent; the scan's band assumed Rev B |
| `HALLMAP_SLOW_TPS`, `HALLMAP_FAST_TPS` | `LOW_SPEED_INCRE` 18,375,000 = 49 ticks/s, `RATE_LOW_*` 49 / 45 / 53 (`test_bench_scan.spin2:338`, `:345-347`) | 24 and 96 ticks/s (increments 8,980,386 and 35,921,544, by the drive law at run time) | 1 and 4 revolutions a second on a 24-tick motor; 3 % and 13 % of the lowest Rev A ceiling (7.4 V, 754 ticks/s) |
| `BURST_SPAN_TICKS`, `BURSTS_PER_SET` | `WIN_TICKS_LOW` 90 = one wheel revolution (`test_bench_scan.spin2:354`) | 48 ticks (2 revolutions, 49 edges) × 2 bursts | The encoder's 64-entry ring bounds a burst, so nothing is emitted while the shaft turns. The self-check needs a span of whole revolutions |
| `HALLMAP_STALL_MS` | `ALIGN_STALL_MS` 120,000, a hand turn (`test_bench_dual.spin2:1849`) | 1,000 ms, a driven crawl | The slow rung's edge comes every 42 ms |
| `RUN_TIME_CAP_S` (`RUN_TIME_FACTOR`, `LEG_*_EST_S`) | 1,800 (`test_bench_scan.spin2:656`) | 3 × the legs built: hall map 40 s, min increment 130, ladder 300, ramp 90, stops 140, offset scan 660, pass probe 45 (coast 70 removed 2026-10-04, «#3691») → 120 (hall map alone; phase 1 had 200 = 5 × 40) to 4,215 (every hands-off leg; 4,425 until «#3691»; 2,100 at phase 2a); an attended tier 3 × its leg's running time: hand load 900, held stop 1,080 (sag 540 and pinch 225 removed 2026-10-04); «#3686»'s qualification chain 2,070 (`LEG_WIRING_EST_S` 10, `LEG_POWER_EST_S` 150) | Leg length; 5 × a ~700 s chained run would leave an unwatched motor running an hour. The chain is 1,405 s at 12 V and 24 V, where the offset scan drives (1,475 s with the coast), ~745 s elsewhere; each leg's own bounds end a stuck drive long before the cap. Phase 2c: a screen waiting on the operator is not counted (`runIdleMs`): his reading time is not an unwatched motor |
| `KE_MV_PER_KRPM` | none in the instruments (the library's fitted back-EMF line, `HUB_FF_*`) | 3,530 | Sheet; phase 2's misdial check |
| `RATED_MA`, `NO_LOAD_MA_MAX` | none | 1,840 and 400 | Sheet (analysis §1.1) |
| `SECTOR_TOL_X10` (R23-SGL-SECTOR) | none (the hub has no shaft angle) | 60 = 6 counts: the **repeatability** tolerance, each hall code's width against that code's own mean (revised 2026-10-04 from "every sector within 6 counts of 60", «#3693», D1A-5) | New cell. The Doco's sectors are NOT equal (D1a: codes 1-6 mean 56.2, 59.8, 65.7, 66.9, 57.6, 54.2 counts, 13.5-16.7°), so the equal-sector bound would FAIL a healthy motor. The cell judges that a width repeats (D1a's worst wander 4.1 counts × 1.5 margin = 6) and records the six widths per set and direction (`B1-CODEW`: mean, min, max) so D1b can compare directions (hysteresis vs placement) and measure the crawl's own scatter. PROVISIONAL: D1b's records retune the bound; the arbiter rules |
| Direction names | Forward is positive increments | Forward is **negative** increments (`ADDING_MOTOR.md` step 6) | The harness names a set by increment sign and by the hall direction measured, never "forward" |
| `ALIGN_MAX_CROSS`, `ALIGN_MAX_EDGES` (L-align, «#3694»; revised «#3697») | 288 = 3 turns × 15 cycles × 3 phases × 2 = 270, + 18 (`test_bench_dual.spin2` `ALIGN_MAX_CROSS`); no edge buffer | «#3697»: 72 crossings = 2 × `ALIGN_TARGET_CROSS` (the step's own way stops at 36; the other way, a rock-back between flicks, stays under it) and 96 edges, (`ALIGN_TURNS` + 1) × 24, every edge 16 times. Was («#3694»): 96 each, 3 turns × 4 × 3 × 2 = 72 crossings and 72 hall edges, + a turn | Scales with pole pairs. Was "not built" until «#3694» (phase 2b had judged a hand spin unable to hold a speed; the 6.5″'s legs were turned by a hand that kept turning, and the encoder makes the angle independent of the pace — the 3694 rows) |
| The rows: DAT `rowMv`, `rowCeilIncr` (`ROW_COUNT` 7) | one measured ceiling scaled by the voltage, `HUB_CEIL_INCR_AT_NOMINAL` 165,000,000 (`isp_bldc_motor.spin2:5201`, used at `:5440`) | 7 Rev A rows, 7.4-24 V: 282, 545, 335, 376, 398, 470, 391 × 10⁶, MIRRORED from `confgurePowerLimits()` (`isp_bldc_motor.spin2:5418-5419`) | A table per voltage; the library has no getter for its ceiling, so the harness mirrors it and prints the increment the library actually wrote beside it (`B1-RAMP lib_incr`). The tool's per-motor record carries the table |
| `SHIPPED_MIN_INCR` | `HUB_FLOOR_INCR` 100,000 (`isp_bldc_motor.spin2:5203`) | 544,628 (reverse; the forward sign's is 1, PL-71) (`:5421`) | The shipped Rev A minimum; L-mininc runs it as a rung of its sweep |
| `PK1_CAP_INCR`, `PK1_CAP_FROM_MV` | none (the 6.5″'s top field step is 12.8 counts, analysis §5.1) | 419,000,000 from 12 V up; the 22.2 V top runs at 419e6 (power 89, `topPowerFor()`), 11.1 V's 545e6 uncapped (P-S2's own measurement) | Analysis F3 / PK-1: above 419.4e6 one drive pass's field step exceeds the LAG_HOLD-to-fault margin (25 counts) on this motor. The arbiter's 2a ruling: no hands-off rung past it at 12-24 V. Scales with the motor's hall rate per drive pass |
| DAT `rowLadderA` (the ladder's test limit) | none: the scan and the ladder run at the library's 40 / 27 A | 2 A at every row but 11.1 V, 3 A | 11.1 V's 75 % rung needs 2.57 A of phase current (MODELED, analysis §2.1); every other unloaded rung 0.12-0.25 A, climbs ≤ 0.68 A |
| DAT `ladderPcts`, `ladderExtIncr` (`LADDER_PCT_COUNT` 4, `LADDER_EXT_COUNT` 2, `LADDER_CEIL_RUNG` 3) | `LADDER_BASE_RUNGS` 10 at 5..147 × 10⁶ plus `LADDER_PROBES` 2 at 155, 165 × 10⁶ (`test_bench_dual.spin2:1659-1662`) | 25, 50, 75, 100 % of the row's ceiling (capped), then 360e6 and 400e6 at a capped row above its ceiling | The analysis's L2: rungs per row, and at 12-24 V rungs to 400e6 |
| The ladder's fault rule | `LADDER_FAULT_STOP` 2 consecutive faulted rungs end a sign's ladder (`test_bench_dual.spin2:1670`) | One rung that faults, is refused or does not arrive ends its entry's climb (from rest, or by steps) | The Doco's fault is predicted where the 6.5″ drooped (P-S2, F3); a hands-off run does not drive into a second one |
| The ladder's entries | one climb and one descent (`test_bench_dual.spin2:1666-1667`), `LADDER_SETTLE_MS` 500, `LADDER_STEADY_MS` 6,000 (`:1916-1918`) | each rung from rest on the built-in ramp AND by a step from the rung below; 1 s settle, 5 s window | The analysis's L2: the 1 mH limit cycle is excited by a step, not by the ramp |
| `MISDIAL_MIN_POINTS`, `MISDIAL_MIN_SPAN_PM` | none | 3 clean rungs spanning ≥ 50 % of the fastest one's speed | The misdial check's fit needs a line, not two points |
| `KE_IS_FITTED`, `KE_SHEET_TOL_PCT`, `MISDIAL_TOL_PM` | none (the 6.5″'s pack was sensed) | FALSE; 10 %; ±130 ‰ in every D1 run; the D2 build (`-D SINGLE_QUALIFY`, the `single-qualify` tiers, «#3686») sets `KE_IS_FITTED` TRUE and predicts from `KE_FITTED_MV_PER_KRPM` (the 3686 rows), ±30 ‰ | Plan §4: the tolerance "derived from the spec sheet and D1's first run". The sheet's ±10 % plus the ±3 % residual catches a gross misdial; only a fitted Ke separates adjacent rows (7.5-8 % apart). **Arbiter decision D5:** no rebuild in the middle of a visit; D1's evaluation fits Ke across the rows and applies ±30 ‰ offline to each row's logged raw ratio (`B1-MISDIAL ratio_ppm`, with `slope_e9`, `vpred_mv`, `told_mv`, `ke_mv_krpm`, `frame_cnt` to refit, phase 2b) |
| `DUTY_VOLT_DIV` | none | 8: the phase peak is Vbus × duty / (8 × frame_cnt) | MODELED (`DOCs/plans/servo-model/spin2_model.py:521`); the misdial check's duty-to-volts scale. The drive's, not the motor's, but no 6.5″ instrument needed it |
| DAT `minincTpsX100` (`MININC_RUNGS` 10, `MININC_SHIPPED_RUNG`) | Visit 9 E4's rungs, 544,628 down to 100,000 (`isp_bldc_motor.spin2:5437-5439` note) | 24, 12, 6, 4, 3, 2, the shipped 1.46, 1, 0.75, 0.6 hall ticks/s, descending until one is not steady | PL-71. From the hall map's slow rung past the shipped minimum to where one electrical cycle takes 10 s |
| `MININC_WIN_COUNTS`, `MININC_SYNC_TOL_COUNTS`, `MININC_SUBWINS`, `MININC_SUB_MIN_PCT` | none (Visit 9 E4 judged "exactly its commanded rate" on the hub's ticks) | 360 (one electrical cycle), 90 (a quarter cycle: a slipped pole pair reads 360), 4 sub-windows, 50 % of each one's share | "Steadily" from the encoder; scale with the counts per electrical cycle |
| `STOPS_CRAWL_POWER` | power 15, `T0_25_POWER` (~59 ticks/s of 90; `test_bench_t0.spin2:534`, `:563-564`) | 5 (30-42 ticks/s by the rows' tables) | A crawl on a 24-tick motor |
| DAT `stopTopTicks`, `stopCrawlTicks`; `STOPS_TOP_MS`, `STOPS_CRAWL_MS` | `T0_25_ROT_TURNS` 1 (90 ticks), `T0_25_PLAN_ROT_C` 2, `T0_25_PLAN_MS_C` 1,500 (`test_bench_t0.spin2:562`, `:632-634`) | 7,200 and 9,600 ticks (300 and 400 revolutions) at the top, 24 and 120 at the crawl; 15,000 ms and 3,000 ms | The Doco's tops stop over 50-181 revolutions (analysis §6): a limit inside that fires at once |
| `REST_JITTER_COUNTS`, `REST_QUIET_MS` | none (the hub has no shaft angle) | 1 count; 300 ms | The shaft's rest from the encoder |
| `STOPROT_EARLY_COUNTS`, `STOPROT_LATE_COUNTS` (R23-SGL-STOPROT) | `T0_25_ROT_TOL_TICKS` 3 late, `T0_25_PLAN_EARLY_TICKS` 1 more early, on the hub's ticks (`test_bench_t0.spin2:578`, `:666`) | −240 .. +180 counts: the same band in ticks, × 60 counts a tick, on the encoder | Carried in ticks; the counts per tick are the motor's |
| `STOPTIME_TOL_MS` (R23-SGL-STOPTIME) | `T0_25_TIME_EARLY_MS` / `_LATE_MS` −6 .. +4 ms on the field's zero (`test_bench_t0.spin2:660-661`) | ±100 ms on the shaft's rest | DERIVED: the built-in deceleration moves this shaft its last count in the final 46 ms of a stop, so the shaft's rest resolves to ~50 ms; the field's zero prints beside it |
| `MININC_HI_TPS_X100` (R23-SGL-MININC) | none | 146: the shipped minimum's own rate, 1.4555 ticks/s, rounded up | New cell |
| **The 2b rows.** DAT `rowL13` (the rows L-offscan drives at; L-coast, which also drove there, was removed 2026-10-04: STEPHEN, qualify the Doco as the 6.5″, no new measurements; «#3691») | none: the scan ran at the one pack voltage | 12 V and 24 V; another row prints `B1-LEGSKIP` and drives nothing | The analysis's §8 L3 names the two rows (L1's are gone with the leg) |
| DAT `speedPcts` (`SPEED_PCT_COUNT` 3) | the scan's QTR and HALF rungs, `RATE_QTR_EXPECTED` 98 / `RATE_HALF_EXPECTED` 196 ticks/s (`test_bench_scan.spin2:544-547`) | 25, 50, 100 % of the row's ceiling, capped at its top: 559 / 1,119 / 2,238 rpm at 12 V, 653 / 1,306 / 2,612 at 24 V | The analysis's L3 stimulus (L1's, removed with the coast-down 2026-10-04, «#3691»); a ceiling per row, not one wheel's rungs |
| ~~`COAST_SAMPLE_US`, `COAST_MAX_SAMPLES`, `COAST_WAIT_MAX_MS`, `COAST_STEADY_MS`, `COAST_FAULT_WAIT_MS`~~ | none (the fault study judged coasts on the halls, `test_bench_dual` FLTRESP) | **removed 2026-10-04** (STEPHEN: qualify the Doco as the 6.5″, no new measurements; «#3691») | Was: 500 µs (2 kHz), 4,000 readings, 3,000 ms, 2,000 ms, 50 ms, the analysis's "≥ 2 kHz until rest". The coast-down's desk role (inertia and friction for the model) stays a desk unknown (§13) |
| ~~`COAST_PTS_MAX`, `COAST_EMIT_GAP_MS`~~ | none | **removed 2026-10-04** (STEPHEN: qualify the Doco as the 6.5″, no new measurements; «#3691») | Was: `B1-COASTPT`'s thinning, 48 and 50 ms |
| ~~`COAST_EMF_MAX_PM`~~ | none (the 6.5″ never coasted from a floated bridge at a speed whose back-EMF neared its pack) | **removed 2026-10-04** (STEPHEN: qualify the Doco as the 6.5″, no new measurements; «#3691») | Was: 900 ‰, the regen guard for a floated bridge (§13) |
| ~~DAT `coastLoMs`, `coastHiMs` (R23-SGL-COAST)~~ | none | **removed 2026-10-04** (STEPHEN: qualify the Doco as the 6.5″, no new measurements; «#3691») | Was: 12 V 62 .. 738 ms, 24 V 71 .. 834, the cell's bracket. The cell is gone with the leg |
| `OFS_STEP_DEG`, `OFS_SPAN_DEG` (`OFS_SIDE_POINTS` 7, `OFS_POINTS` 14) | `COARSE_STEP_DEG` 10, `FINE_STEP_DEG` 5, `HARD_LIMIT_DEG` 90, a walk to the current wall (`test_bench_scan.spin2:587-590`) | 5° steps over ±30° of the shipped offset, a side at a time from the shipped one (each side entered from rest), so no step while driven exceeds 5° | The analysis's L3. Its two references (the shipped point of each side) read the drift |
| `OFS_SETTLE_MS`, `OFS_WINDOW_MS` | `SETTLE_MS` 1,000 (`:508`); windows in hall ticks, `WIN_TICKS_FINE` 270 (`:521`) | 1,000 ms; 5,000 ms by time | Rev A resolves a 5 s mean of the DC link to ~10 mA (one 5 ms reading is ±3 mV, 600 mA); a time window, as the ladder's |
| `OFS_POINT_X100`, `OFS_POINT_SAMPLES`, `OFS_CEIL_MA`, `OFS_POINT_FLOOR_MA` | `POINT_ABORT_X100` 250, `POINT_ABORT_SAMPLES` 40, `POINT_ABORT_CEIL_PCT` 80 of `ABS_ABORT_MV` (`:645-654`), all mV at 150 mV/A | 250, 40, 2,944 mA (80 % of `ABS_ABORT_MA`), floor 400 mA (`NO_LOAD_MA_MAX`); in mA through the detected board | The scan's point abort in amps. The floor is new: 2.5 × an unloaded reference near 0.05 A sits inside one Rev A reading's noise |
| `OFS_FIT_MIN_PTS`, `OFS_VERT_SE_MAX_X10` | `FIT_MIN_PTS` 6 / `CONFIRM_MIN_PTS` 5, the `FIT_POOR_*` rules (`:625-635`) | 5 points; resolved when the vertex's own standard error ≤ 2.5° | DERIVED (`sgl2b_model.py`): a rule on the curvature's significance alone let 26 of 1,000 noisy unloaded trials falsely FAIL the lead check; the vertex's error, none. Unloaded on Rev A the DC-link minimum resolves in 0-16 % of runs at the analysis's 0.02-0.11 A (58 % at 0.2 A), the duty minimum always — on phase 2b's I0/cos(d) curve; phase 2c's plant check says otherwise (the LEADMOVE row) |
| `LEADMOVE_TOL_X10`, `LEADMOVE_FITQ` (R23-SGL-LEADMOVE, and the Z reference `B1-OFSPAIR mid_x10`) | none | 100 = 10° of spread across 25 / 50 / 100 %; of the DC-LINK fit's vertices (`LEADMOVE_FITQ` `FITQ_DC`, arbiter decision D10, 2026-10-04, reversing D9 on the plant evidence below), the duty fit's recorded beside it | The analysis's P-S5 negative. PROVISIONAL (arbiter). New cell. ⚠ The analysis's own steady-state plant (`doco_need()`, «#3679» phase 2c `sgl2c_model.py` part 1) puts the duty's minimum `atan(ωL/R)` ahead of the current's — 7-61° — moving 20-37° between 25 and 100 % while the current minimum moves 0.3-1.3°; at 24 V, 0.5 mH the duty-fit spread FAILs a motor whose current minimum does not move (200 of 200 trials). The same plant's DC link rises 4-50× within 30° of its minimum (not 1.15×, phase 2b's assumption) and its fit resolves in 187-200 of 200 trials. `LEADMOVE_FITQ` is the one constant the arbiter's ruling on this turns |
| `PASSPRB_PCT`, `PASSPRB_WIN_MS`, `PASSPRD_TOL_PPM` (R23-SGL-PASSPRD) | none: `test_bench_dual`'s CLOCK part judged the frame and pass from the driver's own counters (`expectedPassUs()`) | 50 % of the row's ceiling; 10,000 ms by `getms()`, its time summed as seconds + clocks; ±1,000 ppm against the ACTUAL frame's pass rate (`clkfreq / (frame_cnt × 23)`) | Plan §1.4. 10 s at 1,119 rpm is 268,560 counts, 4 ppm a count; the frame's rounding moves the pass rate −267 .. +125 ppm from 44 kHz / 23 across the clock names. Floor: a 22-frame pass rarer than 1 in 43 reads inside. New cell |
| **The 2c rows.** DAT `rowL56`, `rowHandDef` (the rows each attended leg runs at); ~~`sagIncr`, `sagExpectFault`, `pinchIncr`~~ **removed 2026-10-04** (STEPHEN: qualify the Doco as the 6.5″, no new measurements; «#3691») | none: the 6.5″'s hand tests ran on wheels (T0-24, floor-grab) | L-handload and L-heldpush at 12 V and 24 V; the default-limit step at 12 V only, never 24 V. (Was also: L-sag at 22.2 V and 18.5 V, L-pinch at 18.5 V: removed) | The analysis's §8 L5 and L6 name the rows. Another row prints `B1-LEGSKIP` and the panel says no step runs there |
| `HAND_POWER` | the obstacle's `BLK_POWER` 7 at `BLK_LIMIT_A` 2 (`test_bench_dual.spin2:16664`) | 10 (207 rpm at 12 V, 241 at 24 V) | The analysis's L5 stimulus, by `driveAtPower()`: the API path a hand meets |
| DAT `handLimitA` | `BLK_LIMIT_A` 2, `LOAD_LIMIT_A` 2 | 4, 2, then 0 = the library's default (`I_PEAK_A` 40 / `I_CONT_A` 27) | L5: `testSetCurrentLimits(4, 4)`, then `(2, 2)`, then the default briefly at 12 V |
| `HAND_CONTACT_PM` | none (the obstacle was met by the halls' stand) | 500: the encoder's speed under half the command is his grip | DERIVED: an unloaded crawl follows at 100 % (P-S1) |
| `HAND_GRIP_WAIT_MS`, `HAND_ACT_MAX_MS` | none | 30,000; 60,000 | Bounds on his reach and on a creeping grip at a test limit |
| `HAND_STEP_CAP_MAS`, `HAND_LEG_CAP_MAS`, `HAND_DEF_NEED_MAS` | none (the run cap only) | 7,700 mA·s of STALL charge (the DC link above `NO_LOAD_MA_MAX`) a step; 15,400 the leg; the default step runs only while 7,700 is left | DERIVED, MODELED (`sgl2c_model.py` part 2a, the analysis's §4.1 stand currents with a 100 ms ramp): a 12 V default stall latches at 4.6-6.3 A·s, under the step cap; a 24 V one trips it 0.70-1.04 s after the grip, before the latch (1.16 s) — the leg cap the plan named; the test-limit stalls use ≤ 0.42 A·s, so at 12 V the default step runs, and once more on a redo |
| `HAND_DEF_ABORT_MA` | `ABS_ABORT_MV` 1,500 = 10 A at 150 mV/A | 8,000 mA, the default step's own drive only (every other drive keeps `ABS_ABORT_MA` 3,680) | 3,680 would trip a 12 V firm default stall (4.6-6.1 A) in 20 ms, before the stop it measures; 8 A is 31 % over it and the 24 V stall's bottom |
| `BLKSTOP_LO_MS` / `_HI_MS`, `HAND_STAMP_MS`, `HAND_NOLATCH_MS` (R23-SGL-BLKSTOP) | `BLK_STAND_LO_MS` 988 and, before `test_bench_dual` SRC_REV 76, its upper bound 1,168 (`:16669-16686`) | 988 .. 1,168 ms from the last hall tick (the library's `BLOCKED_PASSES` 1,000 ms ∓ 12 ms of stamps, + the 6.5″'s 156 ms field allowance, carried); a stand of 1,180 ms with no latch is stopped and reads 1,180 | The plan's BLKSTOP band (§7). The tick is stamped by the 5 ms reading that shows it, the latch by its `EV_STOP` event's own `getms()`; a correct driver reads 995-1,009 (`sgl2c_model.py` part 2b). New cell, with R23-SGL-LIMHOLD (0 faults under a test limit, judged when the grip and a fold-back were both seen) |
| `HELD_REARM_MS`, `HELD_SETTLE_MS`, `HELD_RELEASE_MS`, `HELD_WAIT_MS`, `HELD_ACT_MAX_MS`, `HELD_TURN_COUNTS` | T0-24's `T0_24_REARM_MS` 20 and its hold rows (`test_bench_t0.spin2:1117-1138`) | 20; 300; 1,000 (the encoder still after the hold gave way: he has let go, the sensor ends the step); 60,000; 120,000; 7 counts (an eighth of a tick, ~2°) | T0-24's re-arm carried; the release is the Doco's sensor-ended step |
| `HOLDRISE_LO_MS` / `_HI_MS`, `RISE_MIN_SPAN_MS` (R23-SGL-HOLDRISE); R23-SGL-HOLDSLIP's bound | T0-24's `T0_24_HOLD_RISE_LO_MS` 220 / `_HI_MS` 280 (the 6.5″'s HOLD-RISE) | `wheel.HOLD_RISE_MS` ∓ 30 (220 .. 280); a rate needs 50 ms of rising pairs; the slip at exactly `wheel.HOLD_SLIP_TICKS` (2) net hall ticks of the encoder object's captured edges | P-H4: on the Doco a tick is 15° of shaft, so the push back starts 0-15° from rest and the slip comes at 15-30°. New cells (`sgl2c_model.py` part 2d) |
| ~~`SAG_LOST_PM`, `SAG_LOST_MS`, `SAG_WAIT_MS`, `SAG_SETTLE_MS`, `SAG_TRACE_MS` (R23-SGL-SAGTYPE, OPTIONAL)~~ | none (the 6.5″'s pack was never dialled in a run) | **removed 2026-10-04** (STEPHEN: qualify the Doco as the 6.5″, no new measurements; «#3691») | Was: 980 ‰ of the command for 50 ms; 120,000; 1,000; 100. The cell, its bound `sagExpectFault`, the leg and its panel steps are gone |
| ~~`PINCH_IDLE_MS`, `PINCH_MEAN_N`, `PINCH_SEEN_MA`, `PINCH_GONE_MS`, `PINCH_WAIT_MS`, `PINCH_TRACE_MS` (OPTIONAL, records only)~~ | none | **removed 2026-10-04** (STEPHEN: qualify the Doco as the 6.5″, no new measurements; «#3691») | Was: 2,000; 20 readings; 300 mA; 200; 60,000; 20. The leg, its records and its panel steps are gone |
| **The 3686 rows** (the D2 qualification, §7). `KE_FITTED_MV_PER_KRPM` (R23-SGL-MISDIAL fitted) | none (the 6.5″'s pack was sensed) | 3,530, PROVISIONAL: the sheet's value until D1's evaluation fits Ke across the rows and sets it, before the D2 pack | Arbiter decision D5. A D2 build left at the sheet's value judges ±30 ‰ against a Ke that may be off the sheet by its 10 %: a correct motor 5 % under it reads +47 and FAILS (desk model, «#3686» `sgl3686_model.py`). The tool's per-motor record carries the fitted Ke |
| DAT `powerPcts` (`POWER_RUNG_COUNT` 4; R23-SGL-POWER) | the spin legs' and POWERMAP's powers, on the halls (`test_bench_dual`) | 25, 50, 75, 100, each capped at the row's top power (89 at 22.2 V), each power sign, each from rest; under DAT `rowLadderA` | The arbiter's D7 left the ladder commanding by increment, so the power path's rungs are their own leg (L-power); the quarters of the power range as the library maps it |
| `LEG_WIRING_EST_S`, `LEG_POWER_EST_S` | none | 10 s (`checkWiring()`'s two legs, at most 4 s, and the settle); 150 s (four rungs each power sign from rest, held ≥ 5 s, to 21 s a rung at 11.1 V's top) | The qualification chain's run caps (the `RUN_TIME_CAP_S` and `RUN_CHARGE_CAP_MAS` rows) |
| **The 3692 rows** (D1a, the hand recheck, §10 step 1). `HAND_TURN_REVS`, `HAND_TURN_MIN_COUNTS`, `HAND_TURN_MAX_MS` (L-handturn) | T0-12's `T0_12_REVOLUTIONS` 3, counted on the halls alone, ended by SPACE | 3 turns told; the turn counts only when the encoder saw 2 turns (2,880 counts); his DONE ends it, 120 s at the latest | The motor is UNPOWERED (no driver started), the encoder bolted to the shaft gives the exact turns and direction. T0-12's step, mirrored; nothing it did not have but the encoder as the yardstick |
| `HANDTICKS_TOL_X100` (R23-SGL-HANDTICKS) | T0-12's "expect 90 per revolution", by eye | 2,400 ∓ 13 (hall ticks per encoder revolution × 100), from the edge-to-edge span of the first and last captured edge | DERIVED: each edge within `SECTOR_TOL_X10` / 10 + 1 = 7 counts of its place on the grid, so a span of at least 2,760 counts is off by 14: 2,400 × 14 / 2,760 = 12.2, rounded up. New cell (`sgl3692_model.py`: worst 9 in 2,000 correct trials; ±5 fails 135) |
| `HAND_TOLD_SIGN_KNOWN`, `HAND_TOLD_TICK_SIGN` (R23-SGL-HANDDIR) | T0-12's `T0_12_TOLD_CCW` FALSE: clockwise from the hub, the sign logged | FALSE, 0: told **clockwise looking at the encoder end**; the hall sign is tied to the encoder's (counts = +60 × rising ticks) and the told way only recorded | Nothing on file says which way positive power turns the Doco's shaft; D1a's own turn measures it, and the evaluation sets both constants (task 3693) |
| `NOWHEEL_PROBE_IN`, `NOWHEEL_SETTLE_MS` (R23-SGL-NOWHEEL) | none (the 6.5″ has a wheel) | `driveForDistance(1, DDU_IN)` expects `ERR_NO_WHEEL_DIA`; the encoder watched 500 ms, within `REST_JITTER_COUNTS` | `MOTOR_CHOICE.md`: `WHEEL_DIA_IN_INCH = 0.0` disables the distance methods |
| **The 3694 rows** (L-align, the cold back-EMF Z: `dual-align` at the Doco's numbers, D1b's first leg; tier `single-align-v11p1`). ~~`ALIGN_LEG_TICKS`~~ (`ALIGN_TURNS` 3) | 270 = 3 × 90 (`test_bench_dual.spin2` `ALIGN_LEG_TICKS`) | **removed «#3697»**: a step ends on its target, not on ticks (the 3697 rows); `ALIGN_TURNS` 3 now sizes the target. Was 72 = 3 × 24 (`HALL_TICKS_PER_REV`, D1a) | Geometry: a leg's crossings are about its ticks |
| The angle each crossing is read at | `t_us / dur_us` across a sector taken as 60° electrical (the 7c evaluation's method) | The encoder count at each crossing (`B1-ACROSS enc_x10`, the mean of its two raw flips' counts) and the PASM-latched count at every hall edge (`B1-AEDGE`); `t_us` / `dur_us` dropped «#3697» (the encoder places a crossing, never time) | D1a: the Doco's sectors are 13.5-16.7°, so Z is read **per edge**, in counts (one count is one electrical degree). MODELED (`sgl3694_model.py`, D1a's widths, a hand stroking ±35 %): the equal-sector time placement reads Z 2-5° off; the encoder's within 0.6° in the two directions' mean, 0.5° of it the count's floor (the evaluation adds it) |
| ~~`ALIGN_SLOW_RPM`, `ALIGN_FAST_RPM`~~ (the pace asked) | "SLOW" / "FAST" in words; achieved 43 and 117 edges/s | **removed «#3697»**: no pace is asked or shown (STEPHEN 2026-10-05: "I cannot maintain a consistent speed"). Was 120 and 240 rpm on the ACT cards, the live rpm beside them | Was the amplitude's margin at an assumed Rev B scale. MEASURED on the 2026-10-05 log instead: the positive half rises 3.0-3.5 mV an electrical Hz above rest (the negative half cut at ~0 mV), and flicks reached 147-1,625 rpm in a sector |
| The leg's outcomes | `OK`, `STALLED`, `SHORT`, `CLIPPED`, `NOSTART` | `NOSTART` dropped (one motor: a failed start ends the run, `AR_START`); **`NOT_RESOLVED`** added — «#3697»: an electrical cycle turned, a level landed, and no phase rose above its rest by more than the widest pair half-band — reported with the swing (`B1-ALEG2 swing_*_mv`) and the leg's verdict (`B1-ASUM`), never a guess; **`CLIPPED` re-defined «#3697»**: short of 20 because more positive-half crossings were refused at a rail than kept (was: a band on a rail) | The small signal; the instrument says when it is under it |
| `ALIGN_ND_MA`, `ALIGN_LIVE_MS` (R23-SGL-ALIGN-ND) | `ALIGN_NODRIVE_MV` 150 = 1 A at 150 mV/A, judged on the worst single raw reading | 1,000 mA through the detected board, net of the rest zero, judged on the worst 250 ms mean | Rev A 5 mV/A: one reading is ±3 mV, 600 mA, within 2× of 1 A; the 250 ms mean's worst over 200 windows is 55 mA (model). Blind under ~1 A of DC link (the 2 A test-limit stall passes), stated in the cell |
| `ALIGN_BIAS_STRAY_MAX_MV` (PL-103) | 8 (`test_bench_dual.spin2` SRC_REV 85, the fix: first-try reads strayed 5-6 mV, coasting reads 15-54) | 8, carried, with the quietest-read fallback | Rev A's rest stray is not measured; a noisier channel lands on its quietest read (`B1-AGUIDE stray_mv`), never on a zero level |
| The matrix (R23-SGL-ALIGN-MTRX) | wheel × measured direction, 4 (`ALIGN_COMBOS`) | the two measured directions (RISE, FALL) — «#3697»: a step's, by the encoder's travel at its kept crossings (`AL_DIRS` removed) | One motor |
| The operator's side (`AL_STEPS`) | 8 legs, one plain printed line each, no redo; the cells over every leg | «#3697»: **2** sgpanel steps, one each way, the shaft flicked in bursts, each ending itself at 36 crossings one way (or DONE); the panel shows the crossings against the target and the largest swing, no rpm. Was 4 (two paces each way). INTRO, SETUP = the bias read, ACT, RESULT, each redoable; CLIP / COVER / RES / MTRX judge each step's last run, ND every run | The Doco harness's attended panel and its convention (L-handload, L-heldpush) |
| **The 3696 rows** (D1b at the 2026-10-04 voltage ruling: tested 7.4, 11.1, 14.8, 18.5, 22.2, 24.0 V; 12.0 V not tested; hand loads at 11.1 V and 24 V). DAT `rowL13` (L-offscan) | none (the 6.5″'s scan ran at its own pack voltage) | TRUE at all seven rows (was 12 V and 24 V); the leg runs under the row's ladder test limit (DAT `rowLadderA`: 3 A at 11.1 V, 2 A elsewhere) and puts the 2 A back on exit | Plan revision 2026-10-04, documentation coverage: the offset scan at every tested voltage. At 2 A the 11.1 V 100 % speed (545e6, past the 2.57 A the ladder's 75 % rung needs) could not follow and its points would read unclean; the limit is the ladder's, not a new number. ~11 minutes a voltage |
| DAT `rowL56`, `rowHandDef` (L-handload, L-heldpush) | floor-grab and T0-24 on wheels | 11.1 V and 24 V (was 12 V and 24 V); the default-limit step at 11.1 V only | The ruling. Default-limit stall at 11.1 V, DESK-SCALED from the 12 V model (§4.1 of the desk model: 8.75 A phase, 4.6-6.1 A DC link, 4.6-6.3 A·s to the latch, 122 mN·m) by 11.1 / 12 = 0.925, a stall being V over a fixed resistance: 8.1 A phase, 4.3-5.6 A DC link, 4.3-5.8 A·s, ~113 mN·m. `HAND_STEP_CAP_MAS` 7,700 still bounds it with 1.3 × to spare; `HAND_DEF_ABORT_MA` 8,000 stays 42 % over the stall's top. The screens say "11.1 V only", "about 110 mN.m", "about 5 A" |
| `HALLSEQ_LO`, `HALLSEQ_HI` (R23-SGL-HALLSEQ, L-hallmap) | T0-12's halls counted by eye, no encoder | 0, 0: every transition of every mapped burst (96 a set) the next code in the order for the way the encoder moved at that step (bad + against); B1-HALLSEQ and B1-SIGNMAP record which increment sign gave which hall and encoder direction, with the power sign the library maps to it | New cell: D1a's HANDSEQ rule (per step, the encoder's direction) on the driven crawl, for both signs. The "negative increments drive forward" claim is recorded here and judged in D2 |
| Run order and chain (`single-measure-<voltage>`) | none | hall map, offset scan, minimum increment, ladder, ramp, stops, ~23 minutes at every voltage (`LEGS_EST_S` 1,360, cap 4,080 s, charge cap 638,400 mA·s); the drive-pass probe is no longer in it (its own tier, `single-passprobe-<voltage> <clock>`, run at 11.1 V per clock name); the cold Z is not in it (attended: `single-align-v11p1`, run once, then every voltage hands-off) | A command boundary only where he must act (overlay P1). The align's drive is floated and never driven, so it does not vary by supply |
| **The 3697 rows** (L-align re-referenced for Rev A and turned in bursts: the 2026-10-05 bench, `DOCs/analyses/bench/2026-10-05/debug_261004-180537.log`, seven runs of step 1 at SRC_REV 12, every one `CLIPPED` with `band_railed` 3 at its bias read, before any turning). The crossing (`ALIGN_PAIRS` 3) | each phase against its own rest level, which sat mid-scale (46-63 mV on the 6.5″'s Rev B) | **LINE TO LINE**: each pair's difference (U−V, V−W, W−U) net of the two rest levels; a crossing is kept only when, at both polls that place it, the pair is on the positive half (the two net readings sum above its half-band) and no reading is on a rail, and the encoder moved across it | A floated Rev A phase rests at 16-24 mV, ON the 20 mV rail, its negative half cut at ~0 mV (`rail_pm` 419-455); the per-phase band could not leave the rail. Each pair's unclipped crossing (both phases at +half their peak) is clear of it |
| The mapping (off-board) | Visit 7c §3.3: `Z = 150° − c`, the 6.5″'s tables | The same rotor frame — TESTED on the 2026-10-05 log (each phase's peak V − U = −109..−125, W − U = +116..+126 counts going FALL; the other orientation predicts the reverse) — the unclipped crossing of pair p at θ = 30 − 120p, + 180 going RISE (U=V 210 / 30, V=W 90 / 270, W=U 330 / 150), rising through it exactly when the travel is RISE; `Z = 90° − c` | Visit 7c's algebra (Z the half-sum of the two directions' optimal offsets) used a reverse table one sector BEHIND the forward one (`hltbAngle2`); the Doco's (`hltbAngl4k2`) is one sector AHEAD, which moves the half-sum by −60°. On the log (FALL only, the per-phase peak method, legs at mixed speeds): Z ≈ −9° across all edges, ≈ −18° at the 0 Hz intercept — before the two-direction mean, so a number to compare, not a result |
| `ALIGN_TARGET_CROSS` | a leg's 270 ticks, about 270 crossings | 36 = 3 turns × 4 pole pairs × 3 pairs; compile-checked ≥ COVER's `ALIGN_MIN_CROSS` 20, and against the panel's `SG_AL_TARGET` | The step ends itself when one direction (the encoder's travel at each crossing) has it, over any number of flicks |
| The pair half-band | each phase's stray + `ALIGN_HYST_MARGIN_MV` | each pair difference's stray in the quietest still read + 4 (`B1-AGUIDE band_uv/vw/wu_mv`); PL-103's read and stillness rule unchanged | The detector watches the difference |
| R23-SGL-ALIGN-CLIP | per band: a band edge on a rail disqualifies the run (`BAND_NOT_RAILED`), n = steps | per kept crossing: those whose four placing readings include one on a rail, 0 .. 0 (`CROSS_NOT_RAILED`), n = crossings kept; an exclusion check (the keep rule refuses them) as COVER is | The band test assumed a mid-scale rest level. Model (`sgl3697_model.py`, the log's shape): 0 of 72 → PASS; the old rule on the log's seven reads → 3 a step → FAIL |
| `B1-ACROSS cps` | none | each kept crossing's own speed, encoder counts a second across its band | On the log the per-phase peaks' encoder → rotor offset moved with the local frequency, +0.52° a Hz (68-78° under 6 Hz, 106° at 20-40 Hz; rms 20; FALL only), as a phase-sense lag would. The two directions' mean cancels it only at matched speeds; bursts are not: the evaluation fits against `cps` and reads 0 Hz (model: the slope within 6 %) |
| The phase refresh (a correction) | — | the status block, phases included, is written every PWM frame (22.8 µs, `.ctlMotor`), the three phases from one ADC window (one smart-pin group); SRC_REV 11-12 said "about every 0.52 ms" (a drive pass) | Skew between two phases ≤ one frame: 0.08° at 150 rpm, 0.9° at 1,625 rpm |

Carried unchanged into L-align, and so not tool parameters: `ALIGN_TURNS` 3 (since «#3697» the target's turns), `ALIGN_BIAS_MS`
250, `ALIGN_BIAS_TRIES` 40, `ALIGN_SETTLE_MS` 400, `ALIGN_STALL_MS` 120,000, `ALIGN_MIN_CROSS` 20, `ALIGN_MIN_SAMP_SECT` 4,
`ALIGN_CLIP_LO_MV` 20 / `_HI_MV` 3,200, `ALIGN_HYST_MARGIN_MV` 4, `ALIGN_SECT_MAX_S` 2 (since «#3697» R23-SGL-ALIGN-RES's
alone); the phases read through the driver's status block, the halls polled, the crossing detector (PL-99; on each pair's
difference since «#3697»), the clip rails (PL-100; judged per crossing since «#3697»), the off-board Z (no fit on the board).

Carried unchanged, and so not tool parameters: `SAMPLE_MS` 5, `ZERO_SAMPLES` 200, `ABS_ABORT_SAMPLES` 4, the 280-byte
record bound, sign-off format sf 1, six hall ticks per electrical cycle (`wheel.HALL_TICKS_PER_CYCLE`), the hall order
1-5-4-6-2-3 (`TECHNIQUES.md` §1.2). Phase 2a: the duty reserve `DUTY_RESERVE_PM` 925 (`ADDING_MOTOR.md` step 6; the
6.5″'s 92-93 %), following within 3 % (`FOLLOW_TOL_PM` 30 = `SPINRATE_FOL_LO` 97, `test_bench_dual.spin2:16343`), ramps
within 10 % (`RAMPARR_TOL_PM` 100 = `RAMPARR_PCT` 10, `:16394`), the 5 s window, and the built-in ramp itself (the
library's, read with `testGetRampLimits()`). Phase 2b: the rest from the encoder (`REST_JITTER_COUNTS`, `REST_QUIET_MS`,
now the stop legs' alone: the coast it was carried for was removed 2026-10-04, «#3691»); following within 3 % for the offset scan's clean points; the 1 s settle; `ABS_ABORT_SAMPLES` for the
offset scan's ceiling; the front cog's statistics (`testGetFrontStats()`, `B1-FRONT`) are records, judged at the 6.5″
session (§1.4). «#3686»: the power rungs within 3 % (`POWER_TOL_PM` = `FOLLOW_TOL_PM` 30, SPINRATE's bar on the power
path); the ceiling's rate on the speed law within 2 %, two-sided (`TOPSPD_TOL_PM` 20 = the 6.5″'s `LIMTOP_FOLLOW_PCT`
98, `test_bench_dual.spin2:10262`; two-sided because the encoder needs no tick-quantisation allowance and a field fast of
the law is a defect too); the wiring walk's own band (`wheel.WALK_TICKS`, `WALK_SHORT_TICKS`, `WALK_OVERSHOOT_TICKS`,
referenced through the object, printed in `B1-WIRING`).

## 5. Doco desk work

- **The Doco's servo model set** (`DOCs/plans/servo-model/`): `pp = 4`, R 1.8 Ω phase-to-phase, Ke 3.53 V/kRPM, Kt
  0.034 N·m/A, no-load 0.4 A (`DOCs/DOCOMotor.pdf`); inertia and friction bracketed, then fitted from D1's ladder. The
  model predicts, before D2, whether the 6.1.0 servo (`SERVO_SETPOINT` 48, `SERVO_ACC_SHIFT` 16, `isp_bldc_motor.spin2:7113-7122`),
  the hold limits and the limit hold behave on the Doco.
- **The offset lookup reads the voltage given to `start()`** (`:5116` reads `user.DRIVE_VOLTAGE`; the ceilings use the
  started voltage, `:4491`; `getDriveVoltage()` already reports the started one, `:1800`). The PL-14 class: every
  remaining `user.DRIVE_VOLTAGE` read in the library is checked — at generation the only code read in the motor and
  steering objects is `:5116`; `isp_steering_serial.spin2:250` (`validVoltageForChoice(user.DRIVE_VOLTAGE)`) and
  `test_bench_t0.spin2:1747` read it too and are judged in the same pass.
- **Hall rate against the front pass:** the Doco's top hall rate (~1.3-1.5 k ticks/s, `MOTOR_CHOICE.md`) exceeds the
  1 kHz front pass, which the 6.5″ (≤ 572 ticks/s) never did. Every front-cog rule that compares positions or ticks per
  pass (`bFrontProtect()` `:2913-2916`, the speed window, the stop planner) is read for that case and tabulated.
- **The wheel-less built-in ramp:** with no wheel the Doco takes the 6.5″'s per-pass steps (`:4609-4610`, `builtinStep`
  `:4687-4699`), 3.75× faster in RPM/s and ~7.5 s to the ceiling. The model and D1's feel decide whether the Doco needs its
  own built-in; that is a behaviour change, brought with §6's.

## 6. Doco tables and driver changes

**Definite:** the Rev A Doco offsets per voltage (`offsetsForMotor()` `:5103`, its Rev A lookup `:5127-5134`), the Rev A
ceilings (`confgurePowerLimits()` `:5206`, the Rev A lookups `:5240-5241`), the forward and reverse minimum increments (PL-71, `:5242-5243`), and a measured
feedforward line for the Doco (today `ff_ceiling := abs(maxFwdIncreAtPwr)`, so no duty reserve at power 100,
`:4498-4505`) — each from D1, with its provenance at the constant. The Rev B Doco columns are left as they are and
labelled unverified at the constant.
**Conditional, each brought to Stephen with D1's measure of benefit before it is built (P5):** a per-sector hall angle
correction (D1a, 2026-10-04: the Doco's six hall sectors measure 13.5° to 16.7°, ±7° electrical — priced from D1b's offset
scan and ladder whether it costs the drive anything); a Doco lead schedule (if
the best offset moves with speed), Doco servo constants (if the model and D1 show the 6.5″ values misbehave), a Doco
wheel-less built-in ramp, any front-cog change §5's table requires. A change he declines becomes a v6.2.0 Known Issue
by his word.
**The harness follows the tables in the same change (from «#3686»):** `test_bench_single`'s `KE_FITTED_MV_PER_KRPM` is set
from D1's fitted Ke (left at the sheet's 3,530, a correct motor 5 % off reads +47 ‰ and fails the fitted misdial), and its
mirrored ceilings (DAT `rowCeilIncr`) are refreshed from the new `confgurePowerLimits()` values, or the D2 top-check ends
the run.
**Verify:** `pasm_equiv` shows only the intended changes; the 6.5″ path is identical (its tables are untouched; the
6.5″ dual tiers' binaries differ only in DRIVER_REV); D2 certifies (§7).

## 7. Doco qualification cells

At every Doco voltage, judged against the encoder where speed or position is involved (Stephen 2026-10-03, *"yes A"*),
each cell with a negative from D1's reference or a desk mutation:
- the start checks and `checkWiring()` pass;
- each power rung holds speed: encoder speed within 3 % of command (the 6.5″'s SPINRATE bar was 97 %);
- ramps arrive within 10 % of the prediction (RAMPARR's bar);
- `stopAfterTime` and `stopAfterRotation` come to rest within their tolerances (encoder);
- the ceiling runs smoothly: no lag fault, no re-sync, rate on the speed law (TOPSPD's bar), forward, reverse and
  reversals;
- the misdial check passes;
- at 12 V and 24 V under a hand load at low speed: the limit holds (no lag fault), the blocked shaft latches its
  protective stop in the 988-1,168 ms band (BLKSTOP's), the hold resists a hand push within its defaults.
Each criterion constant carries PRECONDITION / BOUND / CORRECT CASE (the `plan-to-tasks` overlay, 2026-10-03).

## 8. The motor-adoption tool (PL-176)

**Why.** `ADDING_MOTOR.md` walks a user through producing a new motor's offsets by hand; PL-176 makes the instrument a
tool, once two motors are measured (ruling 2026-09-21).

**Target**, from §4's record of edited constants and D1:
- the per-motor numbers become a parameter record keyed by `MOTOR_TYPE` (not CON edits), with an entry for each motor;
- a stop condition derived from both motors' measured edge behaviour (the 6.5″ droops rather than faults; the Doco's, from D1);
- one stable record format;
- `ADDING_MOTOR.md`'s offset step names the tool and is walkable end to end; the user docs promise only what exists.
**Verify:** run on the Doco at D2 it reproduces D1's offsets and ceilings within their measured spread; run on one 6.5″
wheel at the 6.5″ session (wheels up) it reproduces the 6.5″'s shipped Z (−4°) and pair; a motor type with no record is
refused.

**Built («#3685», 2026-10-04): `src/util_adopt_motor.spin2`, TOOL_REV 1, record format 1, output format 1 (`MA-`).**
- **Placement, and why.** A top a user compiles under their own `isp_bldc_motor_userconfig.spin2` (single-motor block;
  `#DEFINE CFG_SINGLE_MOTOR` with the PNut-guarded `#PRAGMA EXPORTDEF`), run from the debug terminal. ADDING_MOTOR.md's
  reader has their own motor, one board, their configuration file, pnut-ts and the debug terminal, and in general no
  shaft encoder, so the tool measures only what the board sees (halls, DC link, the drive's counters) and needs no bench
  file. The bench runs the same source: `tools/bench-run.sh doco-adopt-<voltage>` (Doco bench, `-D BENCH_DOCO` + the
  voltage symbol) and `adopt-wheel` (the 6.5″ platform's RIGHT wheel, the bench statement's `RIGHT_*`, as `demo-single`);
  both `-D BENCH_QUIET`, both take a clock NAME. The encoder judges the tool from outside, through the harness's
  L-offscan and L-ladder; it is not a tool input. The reason is also recorded in the source header.
- **What it generalises:** the offset-and-ceiling procedure only (ADDING_MOTOR.md steps 5 and 6's ceiling): per scan
  speed (two, one octave apart) and sign, the offset walked in 5° steps outward from the driver's starting pair, a side
  at a time from rest, to the motor's edge; a parabola to the DC link within ±20° of the lowest clean point (the scan's
  fine window); Z and L from the two signs' minima (taken round the circle); Z's agreement across the speeds; then the
  driver's own commutation restored and a ladder per sign to the duty reserve. Not carried: the floor (minimum
  increment), the hall map, the coast, the misdial check, the stops, the attended legs — each needs the encoder or is
  not part of adoption.
- **The record** (`DAT { motor records }`, keyed by a `CON { record keys }` alias of the user's `MOTR_*`; 13 longs: key,
  format, status, ticks/rev, rated mA, no-load mA, scan A, ladder A, slow rpm, fast rpm, ladder from / step / to rpm; an
  `END_OF_RECORDS` row ends the table). **6.5″, RS_MEASURED:** 90; 5,000 (no vendor rating: twice it is the scans' 10 A
  abort); 500 (pack current at the knee, manual §6.3); 4 / 4 A (over the 2.6 A DC link its scan read at the current wall);
  33 / 65 rpm (49.5 / 97.5 ticks/s, the speeds Z was measured at, manual §4.2); 30 / 15 / 435 rpm (to 244e6, inside the
  245e6 it followed smoothly). **DocoEng, RS_PROVISIONAL:** 24 (`DOCOENG_MOTOR.md`; checked by D1 L-hallmap's
  self-check); 1,840 and 400
  (sheet); 2 A scan (harness `TEST_PEAK_A`), 3 A ladder (`rowLadderA` at 11.1 V; set by D1 L-ladder); 560 / 1,120 rpm
  (25 / 50 % of the 12 V ceiling, L-offscan's lower speeds; set by D1 L-offscan, its fits must resolve at both); 280 / 140
  / 2,800 rpm (2,800 = PK-1's 419e6; set by D1 L-ladder's duty line). A record is refused, before anything starts, when
  absent (`NO_RECORD`), of another format (`RECORD_FORMAT`), or when its ticks/rev differ from `hallTicInfoForMotor()`
  (`GEOMETRY`); a plan the record cannot run (`RECORD_PLAN`) and an illegal configuration (`CONFIG`) likewise.
- **§4.1 rows used:** `HALL_TICKS_PER_REV` (record), `RATED_MA` / `NO_LOAD_MA_MAX` (record; the abort, the wall floor,
  the charge cap), `ABS_ABORT_MA` (2 × rated), `RUN_CHARGE_CAP_MAS` (a minute at rated + no-load × the estimated
  run), `RUN_TIME_CAP_S` (3 × the estimate), `TEST_PEAK_A` / `TEST_CONT_A` and `rowLadderA` (record), the current-sense
  scale through the detected board, the rest-zero band (the library's, per board), `PK1_CAP_INCR` (no scan speed or rung
  past it), the ladder's fault rule (one edge ends a climb), the 1 s settle and 5 s window, `OFS_STEP_DEG`, the point
  abort (`OFS_POINT_X100`, `_SAMPLES`, `OFS_CEIL_MA`, `OFS_POINT_FLOOR_MA`), `OFS_FIT_MIN_PTS`, `OFS_VERT_SE_MAX_X10`,
  `DUTY_RESERVE_PM`, `FOLLOW_TOL_PM`, the direction naming by increment sign. Not used (encoder, attended or outside
  adoption): the `ENC_*` rows, the hall-map rows, `KE_*` and the misdial rows, `DUTY_VOLT_DIV`, the min-increment rows,
  the stops rows, the coast rows, `LEADMOVE_*`, `PASSPRB_*`, every 2c and 3686 row. `OFS_SPAN_DEG` ±30 becomes a walk to
  the edge bounded at 90° (the scan's `HARD_LIMIT_DEG`), because a new motor's starting pair may sit far from its minimum.
- **The stop condition (the edge),** one rule from both motors: WALL (the scan's point abort, relative to the side's
  lowest clean point) and FAULT end a side at once; DROOP (following under 80 % on the halls, the scan's
  `FOLLOW_DROOP_PCT`: the 6.5″'s measured torque wall, manual §6.2 — −2° of lead held 51 %, no fault) and HUNT (a held
  pass in a window: the Doco's MODELED torque wall, P-S6 — PROVISIONAL, its count set by D1 L-offscan's held passes at
  ±30°) end it after two in a row; before a side's first clean point, a DROOP/HUNT point drawing less current than the
  one before does not count (the 2023 Doco pair may sit well ahead of the minimum, in the hunting region: desk model §1.2;
  with every edge point counted, the model's side ends before it reaches the minimum). The ladder ends on DROOP,
  HUNT, CAPPED (the 6.5″'s knee), FAULT, or BOUND at `PK1_CAP_INCR` (the Doco's fault-not-slip edge, F3). Per P12, D1
  sets these values; none gates the algorithm.
- **Guards:** start checks refusing; the record's test limit set and read back before driving; the rest zero in the
  library's band; the absolute abort, the charge cap and the time cap every 5 ms; a fault recovered from rest (one that
  will not clear ends the run); offsets restored and read back before the ladder; `stop()` on every way out.
- **Desk model** (scratchpad `adopt_model.py`, reads the tool's source for its constants and records): 31 of 31
  expectations — RECORD, FIT, Z, EDGE and CEILING each shown passing its correct case and failing (or refusing) a data
  or logic mutation. It found two defects in the tool before any compile could: the fit's level term and the hunting
  start. **The level-term defect is in the harness too:** `test_bench_single.spin2:5901` (`ofsFit()`) writes the third
  minor as `S3·T0 − S1·T2` (correct: `S3·T0 − T1·S2`), so B1-OFSFIT's `rms_x10`, `vse_x10` and `resolved` are wrong
  whenever the fitted points are not symmetric about the shipped offset; its vertex (from a and b) is right. Brought to
  the arbiter; not changed here.
- **Not yet verified:** D2 (the tool against D1's offsets and ceilings) and the 6.5″ session (the tool on one wheel) are
  the verification. The tool has run on no motor.

## 9. Serial: tested on hardware

**Starting point.** `pythonSrc/serial_certify.py` (1,146 lines; ten cells: R20-SER-ERRREPLY, -TIMEOUT, -VOLT, -FAULTRESP,
-PROTCLEAR, -LATENCY, -NUMPARSE, -GETTERS, -RAMP, -DEMOWRAP) was written against DRIVER_REV 40 and has never run on
hardware (PL-148, PL-154, PL-157, PL-111's serial half).
**Target.** A desk re-check of every expectation in the script against the current driver (the built-in rates, stop
reasons, start checks, the 6.1.0 and §1 changes, the serial bit period), corrected where they moved; one run on the 6.5″
Rev B platform, wheels up, from Stephen's host through a USB-serial adapter on P56/P57 (the run sheet asks which host and
port), at 270 MHz and at the lowest supported clock (§1.4); its findings fixed in this plan.
**Verify:** every cell a verdict (PROTCLEAR's latched half and GETTERS' refused-start half are NOMEAS by construction —
stated in the evaluation, not counted); PL-148/154/157/111 closed on the log.

## 10. The bench visits

Each visit's run sheet declares its seven attributes, one command per physical setup, what to watch named in advance,
and no act the log can carry. The pack names its commit in every banner.

**The Doco qualification, in order (STEPHEN 2026-10-04: the 6.5″'s sequence at the Doco's numbers, no new
measurements, hand loading only — the motor has no wheel; *"Yes, this looks good with these additional changes"*).** The
bolted-on shaft encoder judges every speed, direction and rest position.
1. **Session D1a — the motor recheck, by hand, unpowered** (the 6.5″'s first step, T0-12): the shaft turned about three
   turns in a told direction; hall ticks per revolution (the pole count) and the hall direction against the turn, the
   encoder giving the exact turns. **Then the start checks and `checkWiring()`.**
2. **Desk — the motor documentation on file corrected** (`DOCOENG_MOTOR.md`, `MOTOR_CHOICE.md`'s Doco rows) to what D1a
   showed.
3. **Session D1b — measure, per voltage** (7.4, 11.1, 12, 14.8, 18.5, 22.2, 24 V; Stephen dials the supply between runs):
   the commutation offsets by current minimum, cross-checked against the encoder's hall zero; the speed ladder on the
   encoder (the duty line, the top speed with the 6.5″'s duty reserve, the feedforward line, the slowest steady speed each
   way); the ramps and stops as the "before". At one voltage, the §1.4 pass-period probe at each test clock.
   **Done 2026-10-05 (third pass, 40 A limit; `DOCs/analyses/bench/2026-10-05/D1B-EVALUATION.md`):** five rows complete,
   11.1 V ended in its offset scan (its later legs are D2's to measure, its table values DERIVED meanwhile). The drive
   follows, ramps and stops on plan at every voltage; the tables' inputs are measured; above ≈ 2,400 rpm the drive enters
   a two-state high-duty regime that the ceilings must be set against (root-caused at the desk first, in «#3684»).
4. **Desk — the driver's Doco tables updated (§6)**, with the harness repairs D1b found («#3698») in the same batch;
   anything beyond a table value goes to Stephen first.
5. **Session D2 — qualify at every voltage on the updated driver (§7), judged on the encoder**: power rungs within 3 %;
   ramps within 10 %; the stop limits; top speed smooth forward, reverse and through reversals; **the lowest speed the
   motor is controllable at and the highest speed it reaches, confirmed once the offsets are right** (STEPHEN 2026-10-04:
   *"one thing I'd like to have us confirm is the lowest speed the motor is controllable at and the highest speed we can
   achieve once everything's dialed in correctly. Don't attempt that till we get the offsets correct"*); at 12 V and 24 V
   by hand: the limit holds, the blocked stop latches in its band, the hold resists a push. The tool (§8) per voltage.
- **6.5″ session — Rev B platform, wheels up.** `serial_certify.py` at 270 MHz and at the lowest supported clock; the
  front-cog load and frame-budget, dead-gap and noise cells at the lowest supported clock; the tool on one wheel.

## 11. Documentation

Deliverables, each against certified behaviour, in the user register (doctrine overlay P8). Conformance: the user
Markdown set — `.claude/doctrine-overlay.md` P8 (reference); `CHANGELOG.md` — `central:changelog-voicing` class 1,
released mode (gate); Spin2 sources — `central:spin2-authoring-guide` (gate, `tools/check_style.sh`); bench PLOT/debug
volume — `DOCs/procedures/PLOT-DISPLAY-RULES.md` (gate, the DEBUG footprint in `tools/build-check.sh`).

## Documentation Blast Radius

`tools/doc-audit.sh` at plan time (2026-10-03, tree `08cad4f`): **clean** — no ORPHAN, no DUPLICATE, no COUNT finding.
Behaviours this plan changes, and every artifact that describes them:

| Behaviour | Artifacts |
|---|---|
| The Doco's offsets, ceilings, minimums, feedforward; verified on Rev A | `MOTOR_CHOICE.md` Doco rows and their "not re-checked" lines (`:77-81`, `:92`); `DOCOENG_MOTOR.md` (verified conditions); `ADDING_MOTOR.md` (`:16-26`, `:52-59`, `:231-234`, `:256-259` "symmetric about zero", `:294-295`, step 6's ceiling rule); `README.md:32`; the source comments at the tables (`isp_bldc_motor.spin2:5118-5126` stale notes) |
| The motor-adoption tool | `ADDING_MOTOR.md` offset step; `TECHNIQUES.md` (characterising a motor); README document list if a page is added |
| The encoder as the Doco's reference | `TECHNIQUES.md` (trusting a measurement); `.claude/skill-conventions.md` instruments |
| Clock independence, the supported range, the start refusal; **the clock must be final before `start()`** (the motor objects derive their timing there; a later `CLKSET`, such as the HDMI video driver's when its display starts, invalidates it — the HDMI demos start the display first; found in «#3673») | `ADDING_MOTOR.md:47` ("The P2 at 270 MHz"); `DRIVER-THEORY-OF-OPERATIONS.md:223`, `:455`, `:461` (dead gap truncation), the pass/frame description; `MOTOR-6.5IN-TECHNICAL-MANUAL.md:221` (duty floor/ceiling "at 270 MHz") and `:890`, with `DOCs/analyses/MOTOR-6.5IN-MANUAL-SOURCES.md`; `DEVELOP.md` (choosing a clock); `DRIVE-OBJECTS.md` (`start()`'s errors, the new error); every demo's clock line and header; `README.md` |
| `demo_single_motor`'s hold and wiring-check comment | its header ("about 3.5 cm at the tyre" is the 6.5″'s) |
| Serial tested; any serial fix | `SERIAL-CONTROL.md`, `DRIVE-OBJECTS-SERIAL.md`, `pythonSrc/P2-BLDC-Motor-Control-Demo.py` docstrings if replies change |
| The release | `CHANGELOG.md` v6.2.0 entry; its Known Issues (the Doco, clock and serial lines resolved; PL-193-196 carried or ruled); `VERSION`; README "New in" |

Counts to re-check: tops certified by `tools/build-check.sh` (51 today; the new harness adds one), demos, archive-set
contents. No duplication finding; the clock statement lives in one place (`DEVELOP.md`) and the others link to it.

## 12. The release — v6.2.0

`VERSION` 6.2.0; a dated CHANGELOG entry per `central:changelog-voicing` class 1, released mode; the Known Issues
evidence brought to Stephen (P5: what ships as a Known Issue is his); `tools/make-release.sh --preview`; the release gates
(`tools/build-check.sh`, `tools/check_style.sh`, `tools/doc-audit.sh`) before the tag. Tag and push are his.

## 13. Named unknowns

| Unknown | Response when it resolves |
|---|---|
| The Doco's inertia and friction | bracketed in the model; fitted from D1's ladder before §6 |
| Whether the Doco needs a lead schedule or its own servo constants | D1's three-speed offsets and the model; a need goes to Stephen with its benefit (§6) |
| The Doco's back-EMF amplitude at hand speed | if under the align clip band, the cold Z is not attempted; the encoder Z and the current minimum stand |
| The front cog's worst body cost for one motor and after §1.3 | measured at D1 (one motor) and the 6.5″ session (two); it sets the floor in §1.6 |
| The serial receive loop's cost per character | measured at the desk-built scratch tier on the 6.5″ session; PASM only if it sets the highest floor |
| Whether PNut sets `clkfreq` to the achieved or the requested clock | read from the compiled image at the desk (non-integer clock build) |
| A supply over-voltage trip on hard stops from top speed (a bench supply cannot sink current) | the run sheet names it to watch; a trip stops the run and the stop is re-planned with a gentler deceleration |
| The misdial tolerance | derived from the spec sheet and D1's first runs |

## 14. Not in this plan (declined visibly)

PL-175 (1-3 motors per P2), PL-177 (back-EMF), PL-174 (vibration study), PL-105 (torque-peak hold) — not chosen at the
scope question. The 6.5″ on Rev A, and the Doco on Rev B — *"we have sufficient to not need this"*. PL-182 / PL-192 run
on the next 6.5″ floor visit (none in this plan). PL-193-196 (Known Issues) — carried; their wording is Stephen's at §12.
Every other open entry stays on the list unchanged.

## 15. Exit gate (`sprint-plan` §5)

1. **Standing rulings:** §0.1, searched across memory, the doctrine overlay, the archived plans and the punch list.
2. **Intent:** §0, Stephen's words quoted (seven answers, 2026-10-03).
3. **Decisions and open items:** each ruling maps to a section; the open punch list was presented whole with the scope
   question; the declined entries are §14.
4. **Premises measured:** the Doco spec sheet read (`DOCs/DOCOMotor.pdf`); the encoder's counting from p2kb; the offset
   lookup's voltage read from source (`:5116`, `:4491`, `:1800`); the clock inventory from source and `tools/pasm_equiv`
   (MODELED worst window 1,959 clocks); `waitms`'s bound from p2kb; the Doco harnesses' absence from `tools/bench-run.sh`;
   a scratch compile of `test_bench_scan`, `test_bench_dual` and `demo_single_motor` under `CFG_SINGLE_MOTOR`. Rig facts
   confirmed by Stephen: the Doco bench (Rev A, P16-P31, encoder P48/P49 with resistors, 30 A dialable supply, no
   voltage sensing, hand load).
5. **Research:** the clock class searched across every library object, the demos and the harnesses; the PL-14 class
   (a started parameter ignored) is in §5; baseline: `tools/build-check.sh` PASS 51/51 at `fb95df3` (2026-10-03,
   the 6.1.0 exit baseline; since then a comment and `tools/logfield.py`), `tools/check_style.sh` PASS, `tools/doc-audit.sh`
   clean.
6. **Named unknowns:** §13.

**Questions:** one for Stephen is scheduled inside the plan, not before it: §1's new start refusal (P5), with its
measured floor. Every other question is answered.

## 16. Sprint start (2026-10-03)

- **Outgoing build: v6.2.0** (STEPHEN 2026-10-03, *"yes a"*; §12). `VERSION` reads 6.1.0 until §12 sets it.
- **Working tree:** clean in the sprint's blast radius (`src/`, `tools/`, `pythonSrc/`, `DOCs/plans/`: no edits, no
  untracked files). One edit outside it, `.vscode/settings.json` — Stephen's VSCode extension settings; no task here
  touches it, so it is left as it is. `main` is 4 commits ahead of origin before this record's commit.
- **Tracking readiness: ready.** Board empty (0 tasks, nothing to archive); context holds one live key (the resume
  pointer); auto-memory 4 index lines, no misfiled judgement. Records corrected at start: `.claude/skill-conventions.md`
  *Rig facts* gains the Doco bench (the encoder supersedes "pnut-ts only" for Doco work — the §3 conventions update,
  applied now as record-keeping); the `baseline-health` overlay's "config block" wording now describes the two
  configuration symbols.
- **Entry baseline** (on tree `14eb9d7`; this record's commit changes no compiled file): `tools/build-check.sh` PASS —
  2 configurations, 51 files examined, 51/51 tops certified, both release demos certified, every bench tier within the
  DEBUG footprint; 0 warnings; exclusion: `hng034rm` (PL-1, cannot compile). No failure groups, so no fix-when decision.
  **A green gate is a compile result only**: behaviour is certified at the bench visits (§10).

## 17. Section ↔ task table (plan-to-tasks, 2026-10-03)

All tasks carry priority `high` and tag `v620`; `seq` is the order (plan-to-tasks overlay).

| Plan § | Deliverable | Task | seq |
| --- | --- | --- | --- |
| §1 (1-2) | Drive pass K = 23, dead gap rounded up, duty floor, `DRIVE_PASS_US` computed; `pasm_equiv` clock arg | «#3670» | 1 |
| §1 (3-4) | Front-cog counted times as time; `FOLD_MIN_MV` derived; board-detect paced | «#3671» | 2 |
| §1 (5) | Host serial fractional bit period; receive-cost record | «#3672» | 3 |
| §1 (7) | Demo waits sliced; clock-range lines | «#3673» | 4 |
| §1 (8) | Harness judges frame and pass at any clock; runner clock names | «#3674» | 5 |
| §2 | Doco bench configuration and voltage tiers | «#3675» | 6 |
| §3 | Encoder reader and self-check | «#3676» | 7 |
| §5 (offset) | Offset lookup reads the started voltage; PL-14 class sweep | «#3677» | 8 |
| §5 (model) | Doco servo model, hall-rate table, built-in ramp analysis | «#3678» | 9 |
| §4 | `test_bench_single` measurement harness (two-phase) | «#3679» | 10 |
| §10 D1 | Visit D1 run sheet, pack, hand-back | «#3680» | 11 |
| §9 (desk) | `serial_certify.py` reconciled with the current driver (D1 wait window) | «#3681» | 12 |
| §10 D1 | D1 trimmed to the 6.5″'s qualification set (STEPHEN 2026-10-04; added mid-sprint) | «#3691» | before 13 |
| §10 D1a | D1a: hand recheck, start and wiring checks — sheet, pack (STEPHEN 2026-10-04; added mid-sprint) | «#3692» | 2 |
| §10 desk | D1a evaluated; Doco motor docs corrected (added mid-sprint) | «#3693» | 3 |
| §9 | Empty counted loops run twice: fixed in the serial objects and harnesses (found by D1a; added mid-sprint) | «#3695» | 1 |
| §10 D1b | Align (cold back-EMF Z) at the Doco's numbers, PL-103 fixed; D1b's first leg (added mid-sprint) | «#3694» | 4 |
| §10 D1b | D1b ready: harness at the agreed voltages, sheet, pack (added mid-sprint) | «#3696» | 2 |
| §10 D1b | Align by hand in bursts: no pace, crossings counted (bench finding 2026-10-05; added mid-sprint) | «#3697» | 1 |
| §10 D1b | D1b (offsets, ladder, pass probe) evaluation | «#3682» | 13 |
| §1 (6) | Clock floor derived; `ERR_CLOCK_TOO_SLOW` ruled (P5), then built | «#3683» | 14 |
| §6 | Doco tables and ruled driver changes | «#3684» | 15 |
| §4, §10 D2 | Single-motor harness repaired from D1b's findings (added mid-sprint) | «#3698» | before 18 |
| §6 (driver) | Rev A current sensing fitted to its hardware; per-board drive (STEPHEN 2026-10-05; added mid-sprint) | «#3699» | before 18 |
| §8 | Motor-adoption tool (PL-176) | «#3685» | 16 |
| §7 | Doco qualification cells | «#3686» | 17 |
| §10 D2 + 6.5″ | D2 and 6.5″ session run sheets, pack, hand-back | «#3687» | 18 |
| §10 D2 + 6.5″, §9 | D2 and 6.5″ session evaluation; serial PLs closed | «#3688» | 19 |
| §11 | User documentation | «#3689» | 20 |
| §12 | v6.2.0 prepared for the tag | «#3690» | 21 |

**Dispatch:** `arbiter-serial` (the project default; `EXCLUSIVE_RESOURCES` puts `src/isp_bldc_motor.spin2` and the user
config under one writer). **Two-phase:** «#3679» (the harness's per-motor constants block is what «#3685»'s tool
inherits). **Batches and gates:** «#3670»-«#3679» gate once before «#3680»; «#3681»-«#3686» gate once before «#3687».
**Rework pass:** the clock work precedes every measurement (§0.2); the serial re-check follows the clock changes it
must reflect and runs in the D1 wait; the refusal follows D1's front-cog cost; docs and release follow certification.

## Revision history

- **2026-10-03** — written.
- **2026-10-03** — started: §16 records the build number, tree audit, tracking readiness and entry baseline.
- **2026-10-03** — tasked: §17. Anchors re-opened at generation; four corrected in place (`offsetsForMotor()` `:5103`,
  `confgurePowerLimits()` `:5206`, the demos' `CLK_FREQ` / `END_HOLD_MS` wording, `MOTOR_CHOICE.md:37` dropped) and the
  PL-14 sweep's three sites named in §5.
- **2026-10-04** — §9 finding fixed in «#3681»: `isp_queue_serial` freed only the truncated length of a line longer than
  `MAX_SINGLE_STRING_LEN`, leaking character-queue capacity until input stopped; it now frees the queued line's whole
  length (`wrappedStrSize()`), and `serial_certify.py`'s R20-SER-BACKTOBACK gains OVERLONG_LINES_ANSWERED. §4.1 gained
  the harness's edited-constants list («#3679»); D1's run sheet is `DOCs/analyses/bench/VISIT-D1-RUNSHEET.md` (pack
  `b30171a`).
- **2026-10-04** — STEPHEN: *"we are not doing anything that we didn't do for the 6.5" motor... we qualify/verify this
  doco motor the same way, no new measurements please"*. «#3691» added (§17): the coast-down, supply-sag and pinch legs
  and the inductance question are removed; the desk model's unknowns stay desk items. D1 gets a new pack.
- **2026-10-04** — §10 restructured to Stephen's approved sequence: D1a (hand recheck, start and wiring checks), the
  motor docs corrected, D1b (offsets and ladder per voltage), the tables, D2 (qualification, with the lowest controllable
  and highest reached speed confirmed on the tuned driver, and the hand loads). «#3692» is D1a, «#3693» its evaluation and
  the motor docs; «#3682» becomes D1b's evaluation.
- **2026-10-04** — STEPHEN: *"is there anything that we wrote in the documentation that we have not certified on this
  bench... we should probably expand the test to cover those other things so all of the documentation we've written has
  been measured, if possible."* The Doco claims were walked: D1a gains the hall-code sequence (DOCOENG_MOTOR.md's
  1-5-4-6-2-3 / 1-3-2-6-4-5) and the no-wheel refusal of the distance methods (MOTOR_CHOICE.md); **D1b's offset scan runs
  at all seven voltages** (it was built for 12 V and 24 V) and its hall map judges the sequence for both power signs. Not
  measurable here and stated as such in the docs: the wire colours (Stephen's cabling; the Ground row reads "Hall IN: +v",
  asked), the 6.0 V / 25.9 V refusals (configuration, desk), the Rev B Doco offsets (not tested by ruling), the vendor's
  4,000 RPM.
- **2026-10-04** — Align (the 6.5″'s cold back-EMF Z, `dual-align`) brought to the Doco: Stephen asked whether this bench
  should be its first Doco test (*"i don't want to skew our bench but i do want to complete these measurements"*). Ordering
  (arbiter): D1a as built; align, with PL-103 fixed, at the numbers D1a confirms, opens D1b ahead of the offset scan, which
  cross-checks it. «#3694» added (§17).
- **2026-10-04** — **The Doco voltages are 2S-6S plus 24 V** (STEPHEN: *"i'm thinking we test at 2s-6s voltages (nominal,
  not max charge)"*, then *"ok B then"*): 7.4, 11.1, 14.8, 18.5, 22.2 and 24.0 V — every LiPo pack at its nominal 3.7 V a
  cell, and the maker's rated 24 V, where the data sheet's speeds are stated. **12.0 V is not tested**: its table row
  stays in the driver and is labelled not re-checked in the user docs. The hand loads run at 11.1 V and 24 V (the low and
  high of the tested set) instead of 12 V and 24 V.
- **2026-10-05** — D1b's first try found the Doco does not turn under drive on 6.x: its 2023 commutation pair is in the
  wrong frame for the 6.x signed-lag mechanisms (root-caused at the desk, «#3682»); fixed in DRIVER_REV 53 (the pair
  swapped; §6's table work starts from it). The align's rest-level reference cannot work on Rev A (reworked, «#3697»).
  PL-199: 350 MHz sense noise. D1b re-runs whole on DRIVER_REV 53, with a 300 MHz probe added. v6.0.0 and v6.1.0 carried
  the Doco fault — its release-note wording is Stephen's at §12. Wherever §4, §7 and §10 say "every Doco voltage" or "12 V and 24 V",
  read this set.
- **2026-10-04** — D1a evaluated («#3693», `DOCs/analyses/bench/2026-10-04/D1A-RECHECK-EVALUATION.md`): 24 ticks, 4 pole
  pairs, the falling hall order and the hall/encoder direction confirmed; the start, wiring and no-wheel checks pass; the
  six hall sectors are uneven (13.5°-16.7°), so §6 gains a priced per-sector question and the hall map's SECTOR cell is
  re-defined to judge repeatability before D1b's pack. The motor docs carry what was verified.
- **2026-10-05** — D1b's second pass lost following at every voltage at the bench's 2 A test limit (Rev A's fold-back
  floor fires on noise; PL-201). STEPHEN *"yes A"*: the library's 40 A limit, the harness's 3.68 A stop as the bench's
  protection, the timing scan at ±20°. **The third pass measured the tables' inputs** (§10 step 3; evaluation
  `D1B-EVALUATION.md`, findings D1B-1..14): «#3684»'s body now carries them, a top-speed regime to root-cause first, and
  the 11.1 V row left to D2. «#3698» added (§17) for the harness repairs. **D2's hand legs revisit the 40 A test
  limit** (a hand load at 40 A is guarded only by the harness's abort).
- **2026-10-05** — STEPHEN: *"our goal is best possible drive for revA and then also for revB boards if we
  algorithmically are different for each to achieve then we need to be."* «#3699» added (§17): Rev A's current limit
  decided on a reading its hardware can resolve (PL-170, which PL-201 merged into), Rev B's path unchanged; it lands
  before D2, whose hand-load limit cell then certifies a low limit on the Doco.
