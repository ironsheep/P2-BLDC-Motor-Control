# Visit Sign-off Mechanism — Design («#3537», phase 1)

**Written:** 2026-09-13 · **Status:** DESIGN, ARBITER-REVIEWED 2026-09-13. **Built 2026-09-14**
(`--check-ready 1` exits 0). Where the build differs from the tables
below, the *As built* list after this header wins, and `DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv`
is the authority for every cell.

**Review changes are applied in place and marked *(arbiter review 2026-09-13)*:**
- booleans print as `TRUE`/`FALSE` in sign-off records (§B.1, §B.4);
- a rerun of the same build cannot hide a `FAIL` (§D.4);
- row 8 counts only the falsifiable channels (§A.5-e);
- J.1 and J.3 are ruled, not asked (§J);
- `BS-ZERO health_ok` is fixed in the same scan change (§F.6);
- the unverified assumptions about attention (`cogatn`/`waitatn`) and the rpm read are resolved (§K.1).

**J.2 is ruled** (no power-off and no unplugging: the detection sweep skips groups whose probe pin
lands on a board's gate input, §C.3). No open owner questions remain.
**Applies to:** every bench visit, starting with Visit 1 (Batch 1).

**As built — where the build differs from this design (arbiter review 2026-09-14):**
- **Multi-condition cells are BOOL.** Rule: a criterion with more than one condition prints its
  combined result as TRUE/FALSE, so no record can print an in-band number beside a `FAIL`.
  - As BOOL: `R1-T0-START`, `R1-T0-EXHAUST`, `R1-T0-RESTART`, `R4-T0-1M-TICKS` (commit 8413f69);
    `R10-CHAR-STEERSTART`, `R10-CHAR-STEERFAIL`, `R13-CHAR-BRAKESTART` (43bf7f2); `R5-SCAN-SELF`,
    `R12-SCAN-RATE`, `R11-SCAN-NOSTALL` (b300660).
  - `R1-SCAN-COGOK` also counts a start whose return is not `testGetMotorCog() − 1`, so PL-22's
    always-0 return fails it.
- **Row 9 (530961a):**
  - `R9-SCAN-HALFLEG` is crit `CLIFF_PROBED`, not `FIT_OR_CLIFF`: TRUE when every half-speed
    confirm fault that left a gap wider than `CLIFF_HALF_STEP_DEG` was followed by a measured probe
    point. It is NOMEAS when no leg had such a fault, and `min_inst` is 2.
    - Why: `FIT_OR_CLIFF` would have passed on run 5, because `computeLegCliff()` finds a good/fault
      pair without any probe.
    - The facts are counted in `runFinePoints()` (`halfProbeEvents`, `halfProbeMissed`), not from
      §F.2's `bResCliff`/`hasMinimum`.
  - `R9-SCAN-OWNZERO` and `R9-SCAN-PAIR2` are COVERAGE. Scan v3 already re-measured a zero before
    every point.
- **§A.5-e incidental lifetimes:** these print as a plain `BS-ZXSALL` record, not `ZXSALL_*`
  SIGNOFFs. A SIGNOFF with an unmanifested crit would read host-side as `CRIT_MISMATCH`.
- **Row 10:** `R10-SCAN-RSTALONE` is BOOL: stopped and not faulted after `testResetFault()` alone.
  The ms it took prints in `BS-RSTALONE`, and it is NOMEAS when a motor has no eligible fault.
  - The criterion is state-based, checked by reading the driver (`isp_bldc_motor.spin2` drive
    loop). A zero command while `DCS_FAULTED` goes `.newRqst` → `.resetFault`, which sets
    `DCS_STOPPED` on the next pass, so "stopped" never waits for a coasting wheel.
  - An unchanged non-zero command goes `.notRqStop` → `.currRqst` and stays `DCS_FAULTED`. That is
    the unfixed `FAIL`.
- **Row 11 (§B.3, §G.3, §G.4):**
  - The watchdog stack counts 43 longs, not 42.
  - The self-test build prints `bin SCANWD`.
  - `declareStall()` snapshots, stops both wheels, and only then emits, in both builds.
  - On the backstop path cog 0 prints the four `R11-WDT-*` records from `emitSignoffs()`, after
    `main()` has stopped the watchdog. `FIRES` measures the elapsed stall (≥ 12 000 ms) and `FAIL`s
    with that number; the other three are NOMEAS.
  - `CKPT`, `STOPPED` and `STACK` are COVERAGE.
- **Row 2, detection (§C.2, §C.3; `test_bench_detect.spin2` SRC_REV 3, FMT 2):**
  - **Detect binary:**
    - A skipped cell emits `BD-SKIPPED` with reason `GATE_OVERLAP` or `COG_OVERLAP`.
    - A skipped cell also skips the library probe, because `getBoardType()` drives the same sense
      pin.
    - `BD-MAP` gains `guard`, and `BD-SWEEP` end gains `cells`, `skipped` and `reps`. `BD-CELL`,
      `BD-ENUM` and `BD-PLAN` are unchanged, so the baseline diff still applies.
    - `clearSweptGroups()` still pinclears the gate-overlap groups. That is not a pulse: `PINCLEAR`
      sets DIR to 0 and the mode to 0 (`p2kbSpin2Pinclear`), so the pin is only released.
  - **Predictions:** they live in `DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv`, one line per
    field change, each with a status of `COMPARED`, `EXCLUDED_VOID` or `NOT_COMPARED_GATE_OVERLAP`.
    Sweep 7's predicted sum is the measured Rev B band 93..104.
  - **`R2-HOST-DETDIFF`:**
    - The baseline run against itself counts all 56 non-void predictions as not occurred, so it
      `FAIL`s: that is its unfixed value.
    - A skip that the log's own `BD-CFG` bases do not imply makes it NOMEAS `UNEXPECTED_SKIP`.
  - **`R2-DETECT-GUARD`:** it computes its skip set from the log's `BD-CFG` and needs no
    predictions file. Today's SRC_REV 2 binary emits `BD-REP` for P40_P55, which `FAIL`s it.

> **STEPHEN, 2026-09-13:** *"on the bench run have you added automated testing of the new
> features arriving so we can sign them off as present and working as desired?"*
> — and — *"this should be done in every bench run too so we are maximizing our progress with
> every run"*.

**Provenance tags used on every number:**
- **[M]** MEASURED, with the log or document it comes from.
- **[D]** DERIVED, with the derivation.
- **[S]** STEPHEN, verbatim.
- **UNVERIFIED** marks anything relied on that is neither visible in this repo nor measured
  (this design was written without `p2kb-mcp`).

**Sources read:**
- the sprint plan's *Sprint Revision — 2026-09-13*
- `src/test_bench_scan.spin2` (SRC_REV 6 / FMT 6), `src/test_bench_t0.spin2`,
  `src/test_bench_char.spin2`, `src/test_bench_detect.spin2`
- `src/isp_bldc_motor.spin2`, `src/isp_steering_2wheel.spin2`
- `tools/bench-run.sh`, and the headers of `tools/check_style.sh` and `tools/doc-audit.sh`
- scan run 5's log and evaluation
- `CHAR-RUN-EVALUATION.md`
- `DOCs/analyses/bench/2026-09-11/debug_260911-210229.log`
- PUNCH-LIST PL-9, PL-17, PL-21, PL-22, PL-23, PL-28, PL-32
- both project skill overlays

---

## 0 · The three rules the whole mechanism rests on

1. **A verdict exists only where a binary printed one.** The host never turns a measurement
   record (`BS-ZERO`, `BC-SENSE`, `T0-n`) into a verdict. There are three host-side cells, each
   named in the manifest with its own required input (§C). If that input is absent, the cell is
   `NOT_BUILT`.
2. **A cell starts at `NOT_BUILT` and reaches `PASS` only by positive evidence.** Positive evidence
   means at least `min_inst` `PASS` instances and no `FAIL` instance. `NOMEAS` and `NOT_BUILT`
   never count as `PASS`. No code path maps "no failure seen" to `PASS` (§E).
3. **A binary declares what it will judge before it judges anything.** At start-up it emits one
   `SIGNOFF-DECL` per cell, then emits a `SIGNOFF` for every declared cell on every exit path it
   controls.
   - A cell that was declared but has no verdict is `NOMEAS` (reason `NOT_REACHED`). That happens
     on a lock-up, an abort or a truncated log.
   - A cell that no log declared is `NOT_BUILT`.

   This separates "the test exists but did not get there" from "there is no test".

---

## A · The sign-off manifest

### A.1 Format and location — `DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv`, plus a generated `.md` view

**Choice: one tab-separated file is the only source.** `tools/signoff-collate.py` regenerates
`SIGNOFF-MANIFEST.md` beside it on every run. The `.md` is headed `GENERATED — edit the .tsv` and
is never edited by hand.

Why TSV:
- **A host script must parse it.** A Markdown table is fragile to parse: pipes inside prose, and
  alignment rows.
- **JSON** diffs badly in git: a status change rewrites nested lines.
- **YAML** needs a non-stdlib package.
- **CSV** collides with the provenance prose, which is full of commas. Tabs never occur in that
  prose.
- **One line per cell** makes every status change a one-line git diff, which is the audit trail.

**Why a generated view rather than two hand-kept files:** two hand-kept copies of the same table
drift (PL-7's lesson). A generated one cannot.

### A.2 Columns (one line per cell; a feature row is the set of cells sharing `row`)

| Column | Meaning |
|---|---|
| `cell` | Globally unique id, ≤ 20 chars, `R<row>-<BIN>-<SHORT>`. This is the join key to `SIGNOFF` records. |
| `row` | Feature row number (1..n). The row verdict aggregates its cells (§D.4). |
| `task` | todo-mcp task id without guillemets (e.g. `3499`). It is cross-checked against the record's `task` field. |
| `feature` | One-line feature statement (row-level; repeated on each cell line). |
| `bin` | Emitting binary token: `SCAN`, `SCANWD`, `T0`, `CHAR`, or `HOST` for the three host cells. |
| `test` | Where in that binary: test id, phase or method. |
| `crit` | Criterion token. It must equal the record's `crit`, or the record's `crit` must start with it followed by `_` (per-channel variants). |
| `lo` / `hi` | Numeric limits the binary compiles in, or `NA`. The collation checks that the record's `lo`/`hi` equal these, so a binary built with a stale limit is caught (`LIMIT_MISMATCH`). |
| `units` | Units token (`COUNT`, `MV_X10`, `RPM`, `TICKS`, `MS`, `PCT_X10`, `BOOL`, `COGID`). |
| `min_inst` | Minimum number of `PASS` instances for a cell `PASS`, e.g. both motors, all 8 holds. |
| `prov` | `M`, `D` or `S` for the tolerance. |
| `basis` | The provenance text: the log line or document for M, the derivation for D, the verbatim words for S. |
| `visit_owed` | Visit number the cell is owed to. |
| `status` | `OWED` · `SIGNED_OFF` · `FAILED`. |
| `status_ref` | For `SIGNED_OFF`/`FAILED`: `V<n>:<log file>:<line>[;…]`, one proving line per instance. Empty while `OWED`. |

**Status transitions**, written only by the collation, and only when run with `--update`:
- `OWED` → `SIGNED_OFF` on a cell `PASS`.
- `OWED` → `FAILED` on a cell `FAIL`.
- `FAILED` → `SIGNED_OFF` on a later visit's `PASS`; the earlier ref is kept in the sheet history.
- `NOMEAS` and `NOT_BUILT` leave the status `OWED` and append the reason to that visit's sheet.
  They never touch `SIGNED_OFF`.

### A.3 Standing rules (recorded here and in the overlay text of §I)

1. **A task that lands a feature or a fix adds its manifest cells in the same commit as the code.**
   Each cell names the binary and test that exercises it, the criterion, and the tolerance with
   provenance. The visit is the next one that has not yet been scheduled.
2. **A visit may not be scheduled while an `OWED` cell for it has no test.**
   - Checked mechanically by `tools/signoff-collate.py --check-ready <visit>` (§D.5): every
     `OWED` cell's `bin` source must contain a `SIGNOFF-DECL` for that cell id.
   - A cell whose binary is not yet built is itself the gap to close before the visit.
3. A tolerance is never a bare round number. `basis` states the data or the derivation. Where no
   baseline exists, the cell says that its first visit establishes the baseline, and the limit it
   uses meanwhile is `D`.

### A.4 The Batch 1 manifest — all 13 rows, filled in

**Visit owed is 1 on every line, and status is `OWED` on every line.** `inst` is `min_inst`.
Limits are as compiled. Derivations too long for a cell are expanded in §A.5; the cell points to
them.

**Row 1 — «#3499»: `start()` returns cog id 0–7 or −1; a second `start()` restarts with no
orphaned cog.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R1-SCAN-COGOK` | SCAN · every `startSide()` | `STARTS_COG_BAD` | 0 | 0 | COUNT | 2 | D — the contract is `@returns` at `isp_bldc_motor.spin2:86`; any start outside 0..7 is the defect |
| `R1-T0-START` | T0 · T0-15a | `RET_EQ_COG_M1` | 0 | 7 | COGID | 1 | D — `start()` returns `motorCog-1`, `testGetMotorCog()` returns `motorCog` (`:115-116`, `:1208`); the return must be in 0..7 and equal `testGetMotorCog()-1` |
| `R1-T0-EXHAUST` | T0 · T0-15b | `RET_NEG_NOLEAK` | -1 | -1 | COGID | 1 | D — `:110-113`; also requires `testGetMotorCog()==0` and the free-cog count after == before (§A.5-a) |
| `R1-T0-RESTART` | T0 · T0-15c | `NO_ORPHAN` | 0 | 0 | COUNT | 1 | D — PL-24 fix `:103-104`; the free-cog count after the 2nd start == after the 1st, and after `stop()` == baseline; measured = the difference |

**Row 2 — «#3500»: board detection.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R2-SCAN-REVB` | SCAN · every start | `STARTS_NOT_REVB` | 0 | 0 | COUNT | 2 | M — Rev B at all eight starts in run 5 (`SCAN-RUN-5-EVALUATION.md` §1) |
| `R2-T0-REPEAT` | T0 · T0-14a | `READS_NOT_REVB` | 0 | 0 | COUNT | 2 | D — N = 32 reads per populated base; N from `test_bench_detect.spin2:142-146` (a 1-in-10 flip mode is missed with probability 0.9³² = 3.4 %) |
| `R2-T0-DIRTY` | T0 · T0-14b | `POSTSTOP_REVB` | 1 | 1 | BOOL | 2 | M — before the fix, a Rev B board read Rev A after its own cog stopped, 4 of 4 (`CHAR-RUN-EVALUATION.md` §3). So this cell can FAIL on the defect. |
| `R2-T0-EMPTY` | T0 · T0-14c | `EMPTY_NODET` | 1 | 1 | BOOL | 1 | M — empty group P0_P15 read sum 500 → not detected (`debug_260911-210229.log:81-125`) |
| `R2-HOST-DETDIFF` | HOST · detect-phase2 log vs baseline | `ONLY_PREDICTED` | 0 | 0 | COUNT | 1 | D/M — §C.2; baseline `2026-09-11/debug_260911-210229.log`; the prediction list is «#3505»'s |
| `R2-CHAR-ISCALE` | CHAR · each motion hold | `RSENSE_IMPLIED` | 135 | 165 | COUNT | 8 | D — `getCurrent()` = `sense_i_mV×10000/rSenseForBoard` (`:749`); Rev B → 150, Rev A misdetect → 5 (`:1597-1598`); ±10 % of 150 absorbs non-atomic sampling of two means, and a 30× error cannot pass |

**Row 3 — «#3501»: hall integrity counters.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R3-SCAN-INTEG` | SCAN · all starts + every integrity-valid point | `MISSED_ILLEGAL_SUM` | 0 | 0 | COUNT | 2 | M — `missed 0 / illegal 0` at every start and every point of run 5 (evaluation §1); D — at ≤ 212 ticks/s against a 43.9 kHz loop no transition can be skipped (`:2363`) |
| `R3-CHAR-INTEG` | CHAR · every hold | `MISSED_ILLEGAL_SUM` | 0 | 0 | COUNT | 2 | same basis |
| `R3-T0-STOPPED` | T0 · T0-13 | `STOPPED_COUNTS` | 0 | 0 | COUNT | 1 | D — stationary halls never transition; hold window 1 000 ms = the scan's zero window (`ZERO_SAMPLES`×`SAMPLE_MS`), long enough to span the start transient that «#3524» fixed |

**Row 4 — «#3502»: rpm and mm/tick precision.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R4-T0-1M-TICKS` | T0 · T0-3 | `DDU_M_TICKS` | 173 | 174 | TICKS | 1 | D — §A.5-b; the pre-fix 175 [M `debug_260911-143911.log`, plan table "F"] and 17 (finding F) both FAIL |
| `R4-CHAR-RPM` | CHAR · each motion hold | `RPM_ERR` | -2 | 2 | RPM | 8 | D — §A.5-c; expected ≈ 64 rpm at 96 ticks/s and ≈ 131 at 196 [M ticks/s, `CHAR-RUN-EVALUATION.md` table] |

**Row 5 — «#3503»: S-3 ADC scale restore.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R5-SCAN-SELF` | SCAN · self-check | `NET_I_IN_BAND` | 1 | 1 | BOOL | 2 | M — existing net bands 59–105 / 118–203 mV (`test_bench_scan.spin2:313-316`); `BS-CHECKSUM pos_i_ok and neg_i_ok` |
| `R5-CHAR-SENSE` | CHAR · each motion hold | `NET_VS_PASS1_PCT` | -150 | 150 | PCT_X10 | 8 | D from M — §A.5-d |

**Row 6 — «#3519»: independent offset setter.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R6-SCAN-OFFSETS` | SCAN · every start + every `applyOffsets` | `READBACK_BAD` | 0 | 0 | COUNT | 2 | M — offsets read back exactly at every start of run 5 (§1); D — read-back is integer degrees, so exact |

**Row 7 — «#3524»: hall inputs not driven at start.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R7-SCAN-STARTILL` | SCAN · every start | `STARTS_ILLEGAL` | 0 | 0 | COUNT | 2 | M — `illegal 0` at every start since the fix (plan 2026-09-13 table); D — before the fix the first hall read went illegal (`:2945-2946`) |

**Row 8 — «#3529»: ADC calibration from a settled average.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R8-SCAN-ZXS` | SCAN · 5 deliberate starts per motor, each with a zero | `ZXS_I` `ZXS_U` `ZXS_V` `ZXS_W` | 0 | 50 | MV_X10 | 5 | D from M — §A.5-e; the unfixed run-5 spread was 62 mV on `i` and 85 mV on `u` [M]; `inst` counts only the falsifiable channel instances (§A.5-e) |
| `R8-T0-ZXS` | T0 · T0-11 (RIGHT, P16) | same four | 0 | 50 | MV_X10 | 3 | same basis |

**Row 9 — «#3530»: scan v4 logic ran.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R9-SCAN-HALFLEG` | SCAN · each half-speed leg | `FIT_OR_CLIFF` | 1 | 1 | BOOL | 4 | M — in run 5 both left half legs were `TOO_FEW` with no probe between the last good point and the fault (evaluation §3). v4 CHANGE 4 must end each leg at `OK`/`POOR` or with a `BS-CLIFF found TRUE`. A leg skipped because its quarter-speed prerequisite failed is `NOMEAS`, never `PASS`. |
| `R9-SCAN-OWNZERO` | SCAN · each fitted leg | `PTS_NO_OWN_ZERO` | 0 | 0 | COUNT | 4 | D — v4 CHANGE 2 invariant: every point that feeds a fit carries its own lifetime zero (`bPtZeroValid`); run 5's ratio 0.440 vs 1.16 came from violating it [M §6] |
| `R9-SCAN-PAIR2` | SCAN · each motor's `BS-PAIR2` | `NET_RATIO_ONLY` | 1 | 1 | BOOL | 2 | D — fmt 6 contract `:3704-3710`: `ratio_raw` is NA and `ratio_net` is present whenever `complete`; an incomplete pair is `NOMEAS` |

**Row 10 — «#3533»: PL-28, PL-22 and PL-9.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R10-SCAN-RSTALONE` | SCAN · first natural fault per motor — **or** CHAR, per open point J.1 | `RESET_ALONE_CLEARS` | 0 | 2030 | MS | 1 | D — PL-28 item 1: before the fix, `testResetFault()` with an unchanged command waits out 30 ms + 1000 × 2 ms = 2 030 ms and stays FAULTED (`:1114-1132`); measured = ms to cleared, and FAIL if not cleared |
| `R10-T0-STOPREADY` | T0 · T0-15d | `STOP_NOT_READY` | 1 | 1 | BOOL | 1 | D — PL-28 item 2: after `stop()`, `isReady()` must be FALSE and `isStopped()` FALSE; before the fix `drv_state` stays stale (`:916`, `:123-125`) |
| `R10-CHAR-STEERSTART` | CHAR · steering phase | `STEER_START_COG` | 0 | 7 | COGID | 1 | D — `isp_steering_2wheel.spin2:100`; also requires both wheel driver cogs non-zero via the existing TEST-USE pass-throughs (UNVERIFIED names, §K) |
| `R10-CHAR-STEERLIVE` | CHAR · steering phase | `WHEEL_TICKS` | 6 | NA | TICKS | 2 | D from M — §A.5-f |
| `R10-CHAR-STEERFAIL` | CHAR · steering phase under cog exhaustion | `RET_NEG_NOLEAK` | -1 | -1 | COGID | 1 | D — `:120-129`; the free-cog count after == before |
| `R10-HOST-PL9` | HOST · static source check, `--static-tree` only | `GAPINMS_ABSENT` | 0 | 0 | COUNT | 1 | D — PL-9 rename is **compile-only**: no run-time behaviour exists to test. The build gate proves it compiles; this cell proves the identifier `gapInMS` is gone from `src/isp_bldc_motor.spin2` (present today at `:253`, `:316-317`, so it can FAIL). |

**Row 11 — «#3534»: scan watchdog.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R11-SCAN-NOSTALL` | SCAN · end of a normal run (cog 0 PASS, or watchdog FAIL) | `ENDED_BY_COG0` | 1 | 1 | BOOL | 1 | M — run 5 stopped emitting without ending (evaluation §7) [S, same section] |
| `R11-WDT-FIRES` | SCANWD · watchdog cog | `STALL_MS` | 4000 | 4500 | MS | 1 | D — §G.4 |
| `R11-WDT-CKPT` | SCANWD · watchdog cog | `CKPT_IS_SELFTEST` | 1 | 1 | BOOL | 1 | D — the stall is placed at `CP_SELFTEST`; any other checkpoint means the heartbeat contract misattributes |
| `R11-WDT-STOPPED` | SCANWD · watchdog cog | `WHEELS_STOPPED` | 1 | 1 | BOOL | 1 | D — ≥ 1 driver cog running before the stall and both `testGetMotorCog()==0` after the watchdog's `stop()`s |
| `R11-WDT-STACK` | SCANWD · watchdog cog | `STACK_OK` | 1 | 1 | BOOL | 1 | D — `WD_STACK_SENTINEL` intact (`:4375`) |
| `R11-HOST-WDTEND` | HOST · SCANWD log | `FLAG_AND_END` | 1 | 1 | BOOL | 1 | D — `BS-BUILD wd_selftest TRUE` present (pnut-ts ignores an unknown `-D`, `bench-run.sh:98-104`), and `DEBUG_END_SESSION` follows the watchdog's verdicts |

**Row 12 — «#3535»: driver start code in the cog LUT.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R12-SCAN-ALIVE` | SCAN · every start | `STARTS_NOT_ALIVE` | 0 | 0 | COUNT | 2 | D from M — §A.5-g |
| `R12-SCAN-RATE` | SCAN · self-check | `RATE_IN_BAND` | 1 | 1 | BOOL | 2 | M — run 5 self-check rates 98.1/98.2 ticks/s in band 90–106 (evaluation §1; `:283-284`) |

**Row 13 — commit `b34e109` («#3535» review fix): `prior_angle` initialised at driver start.**

| cell | bin · test | crit | lo | hi | units | inst | prov · basis |
|---|---|---|---|---|---|---|---|
| `R13-CHAR-BRAKESTART` | CHAR · brake-start phase, each motor × each sign | `BRAKE_START_MOVE` | 6 | NA | TICKS | 4 | D — §A.5-h; tick sign must match increment sign [M: +18 375 000 moved +13 ticks, `debug_260913-120844.log:46`], and no fault |

### A.5 Derivations behind the tolerances

**a · Counting free cogs without a new getter** (R1, R10).
- Start spacer cogs with `cogspin` until one returns `< 0`, record the count, then stop them.
  This is `test_bench_t0.spin2` T0-8's method.
- The test must be `< 0`, not `== -1`. The library documents the `$8000_xxxx` exhaustion form
  (`isp_bldc_motor.spin2:110`), and T0-8 today tests `== -1` (§K defect 2).
- An orphaned driver cog shows as one fewer free cog. Measured = `(free after) − (free
  expected)`, and `PASS` requires 0.

**b · 1 m in hall ticks** (R4-T0).
- The 6.5″ wheel is 6.5 × 3.14159 × 25.4 = 518.68 mm [D], with 90 ticks/rev (`:1019`).
  - *(Corrected 2026-09-13, «#3502» review.)* The plan's 5186 was the ideal value. Before
    «#3502» the source truncated the circumference to whole mm, giving `circInMM_x10` = 5180.
  - «#3502» now rounds it to 5187.
  - Either way the pre-fix count for 1 m is 175, and the fixed count is 173.
- 1000 mm × 90 / 518.6 = **173.5** [D], matching the task body's 173.5.
- An integer tick target is either truncated (173) or rounded (174), depending on the rule
  «#3502» adopts, so the band is 173..174.
- The pre-fix 5.7 mm/tick truncation gives 175 [M], and finding F's ×10 error gives 17 [M]. Both
  sit outside the band.

**c · rpm tolerance ±2 rpm** (R4-CHAR).
- The library's `rpm = (cntsInSec×60×10/90)/10` (`:1795-1796`) truncates, which is ≤ 1 rpm.
- `cntsInSec` is an 8-slot × 125 ms moving sum of integer tick counts. The test's own tick rate
  comes from a different window, so ±1 tick/s appears between them: 60/90 = 0.67 rpm.
- 1 + 0.67 = 1.67, rounded up to **2 rpm** [D].
- The pre-fix `:1719` adds a stale `hallCntsIn8thSec` (always 0) instead of the new reading. The
  sum goes negative after ~1 s [D, plan amendment to T1-2], so pre-fix rpm fails by tens of rpm.
- **Preconditions:**
  - The char run must call `startSenseCog()`, since `rpm` is updated only by `taskPostionSense()`
    (`:1728-1779`). The scan never starts it.
  - The char run must read `rpm` at least 1 s after `AT_SPEED`, so the window is full.

**d · S-3 hold-for-hold band ±15 %** (R5-CHAR).
- Expected net mV = 150.1 × Pass 1 meter amps [M fit, `CHAR-RUN-EVALUATION.md` §2]. Net means
  the hold mean minus a zero read in the **same driver lifetime** (PL-32).
- Pass 1 meter amps, holds 1–8: 0.536 · 1.054 · 0.570 · 1.058 · 3.004 · 5.564 · 3.140 · 5.530
  [M]. Expected: 80.5 · 158.2 · 85.6 · 158.8 · 450.9 · 835.2 · 471.3 · 830.1 mV [D].
- Run-to-run deviation already measured at matching holds on the default offsets [M run 5]:
  | Point | Measured net mV | Expected mV | Deviation |
  |---|---|---|---|
  | L +¼ | 83.2 | 80.5 | +3.4 % |
  | L −¼ | 164.9 | 158.2 | +4.2 % |
  | R +¼ | 93.4 | 85.6 | +9.1 % |
  | R −¼ | 172.5 | 158.8 | +8.6 % |
  | L +½ (−43°) | 452.9 | 450.9 | +0.4 % |
  | L −½ (43°) | 920.1 | 835.2 | **+10.2 %** |
- Band = 1.5 × the largest (10.2 %) = 15.3 %, taken as **±15 %** [D].
- **What it can and cannot see:** it catches S-3's ×6136 error and any gross scale loss. It cannot
  certify a scale to better than ~15 %, and does not claim to. The Pass 1 fit's worst residual
  (4.7 mV [M]) is inside the band at every hold.
- The char run records measured as `(net − expected)×1000/expected`, i.e. PCT_X10.

**e · Cross-start zero spread ≤ 5.0 mV per channel, over 5 deliberate starts** (R8).
- **Defect signature** [M, PL-32 table]: across three starts the unfixed spreads were:
  | Motor | i | u | v | w |
  |---|---|---|---|---|
  | LEFT | 14.6 | 0.9 | 13.3 | 2.1 |
  | RIGHT | 62.8 | 84.6 | 68.6 | 2.3 |
- **Fixed prediction** [D]:
  - Within one lifetime a zero is steady to ~1 mV [M].
  - Single-frame sense samples span 6–8 mV over 200 samples [M `test_bench_scan.spin2:299-300`],
    so σ ≈ range/6 ≈ 1.3 mV.
  - The fix calibrates from an 8-frame hardware sum (`:2816-2834`), so calibration σ ≈
    1.3/√8 ≈ 0.47 mV. That assumes frame noise is white and that the telemetry value is one
    frame (UNVERIFIED).
  - The expected range of 5 normal draws is 2.33σ ≈ 1.1 mV. Adding ~1 mV lifetime drift predicts
    a fixed spread ≲ 2.5 mV.
- **Threshold** = 2 × that prediction = **5.0 mV**. It sits 2.9× below the smallest per-motor
  defect signature (LEFT `i`, 14.6 mV).
- **Which channel instances can fail on the defect.** *(Arbiter review 2026-09-13.)*
  - **Falsifiable:** the unfixed spreads above 5.0 mV were `i` and `v` on both motors and `u` on
    RIGHT [M, table above].
  - **Not falsifiable by this defect:** LEFT `u` (0.9) and `w` on both motors (2.1 / 2.3) were
    already under the limit unfixed, so a `PASS` there is not evidence of the fix.
- **How the collation uses that:**
  - Only the falsifiable instances count toward `min_inst`: scan 5 (`i`×2, `v`×2, RIGHT `u`); T0-11
    3 (RIGHT `i`, `u`, `v`).
  - The other instances are still emitted and still judged: a regression above 5 mV `FAIL`s the
    cell. The row-8 sheet line says which channels signed the fix off.
- The defect signature is one run's three starts [M]. If Visit 1's data shows a different channel
  pattern, this list is re-derived from that data, never widened to pass.
- **Why 5 starts:** a run-level verdict cannot rely on the scan's incidental restarts. Run 5 got
  three per motor only because of `ABORT_I`. Five deliberate starts make the range statistic
  2.33σ instead of 1.69σ for three draws [D, normal range table], at ~8 s per motor (§F.3).
- **First visit:**
  - Visit 1 establishes the fixed baseline, and the measured spread is printed in every record.
  - If a working fix spreads more than 5 mV, that is a `FAIL` the evaluation investigates. It is
    not a reason to widen the limit before the data exists.
  - Fewer than 5 valid zeros for a motor → `NOMEAS`.
- **Incidental lifetimes:** zeros after abort restarts are logged in an informational
  `crit ZXSALL_<ch>` record with `lo`/`hi` `NA`, verdict `NOMEAS`. That keeps a thermal
  after-current effect visible without letting it confound a verdict taken under a controlled
  condition.

**f · Liveness floor 6 ticks** (R10-STEERLIVE, R13).
- The known-good response to a 1/8-ceiling nudge held 700 ms is **13 ticks** [M
  `debug_260913-120844.log:46`].
- The floor is half of that, **6 ticks** [D]. It rejects the PL-22 defect (cogs parked on
  `waitatn` move exactly 0 ticks) and a wheel merely rocked by the other, while tolerating ramp
  variation.
- Condition: the test must use the same increment and duration, `PREFLIGHT_INCRE` / 700 ms. For
  the steering object, the power whose `incrementForPower()` is nearest 18 375 000 (§H.2).

**g · "Driver alive" per start** (R12).
- **There is no loop-progress counter in the published status block.**
  - Its 16 longs (`:1966-1973`) are `drive_u/v/w`, `sense_u/v/w/i_mV`, `hall`, `pos`, `duty`,
    `err`, `loop_ticks`, `loop_ctcks`, `drv_state`, `hall_missed`, `hall_illegal`.
  - `loop_ticks`/`loop_ctcks` are per-pass *durations*, not counts (`:2514-2515`, `:2324-2325`),
    and have no getter.
  - Adding a getter is a library change outside Batch 1's tasks, so it is not used (task rule:
    never invent a getter).
- **The proxy uses existing getters only** [D]:
  - `drv_state` leaves `DCS_Unknown`, which `init()` sets (`:363`) and only the driver's
    status-block write changes (`:2517-2518`), within `READY_TIMEOUT_MS` = 2000 (`:258`, the
    binary's existing bound).
  - **and** the first zero window of that lifetime is not frozen: `i` min ≠ max over 200
    samples. A live channel spans 6–8 mV [M `:299-300`]. A status block the driver is not
    rewriting reads min = max exactly [M PL-21, `debug_260912-153807.log:460`].
- Measured = count of starts failing either test.

**h · Brake-mode start** (R13).
- ~~The defect was that a start in `SM_BRAKE` read an uninitialised `prior_angle`.~~
  **Corrected 2026-09-14 («#3521» phase D review; verified by reading the source).**
  - At driver start `checkstop` runs `cmp stop_mode_, #SM_FLOAT wz` / `modz _nz wz` /
    `if_z call #initAngleFmHall`. MODZ sets Z to the selected combination of the current flags
    (`p2kbPasm2Modz`), so `_nz` inverts Z.
  - `initAngleFmHall` therefore runs only in **SM_BRAKE**, and it ends with
    `mov prior_angle, angle_`.
  - Before `b34e109` it was the default **SM_FLOAT** start that read an uninitialised
    `prior_angle`. b34e109's fix line covers that case; its in-source comment had the modes
    reversed and is corrected.
  - **So `R13-CHAR-BRAKESTART` cannot fail on the prior_angle defect.** It is kept as coverage
    of the brake-mode start path (no fault, correct direction), which no bench run had
    exercised.
  - The SM_FLOAT start is exercised at every hold and every scan start. An uninitialised
    register has no reliable negative limb to test.
- `startEx()` runs `init()`, which forces `stop_mode := SM_FLOAT` (`:336`) before `coginit`. So
  calling `holdAtStop(TRUE)` before `start()` does not produce a brake start.
- **Deterministic ordering** [D from `:2881-2919`]:
  1. `startEx(base, v, det, TRUE)`. The cog calibrates, then parks on `waitatn` *before* its
     first parameter read.
  2. `holdAtStop(TRUE)`.
  3. `cogatn(1 << cogId)`. The driver then reads `stop_mode_ = SM_BRAKE` and runs `checkstop`
     with it.

  The cogatn/waitatn semantics are verified (§K.1 item 1, arbiter review 2026-09-13).
- **Criterion**, per motor and per sign: command `±PREFLIGHT_INCRE` for 700 ms; no fault; tick
  delta sign equals increment sign; |delta| ≥ 6.
- **Limit of falsification, stated plainly:** before the fix `prior_angle` held whatever
  `COGINIT` left in that register. A `res` long has no hub bytes of its own (UNVERIFIED), so the
  defect is not guaranteed to reproduce. A `PASS` shows the fixed path works; it does not prove
  the old path would have failed.

---

## B · The verdict record convention (every bench binary)

### B.1 Two records

**Declaration**, emitted in the header, before anything moves, one per cell the build will judge:

```
SIGNOFF-DECL,sf,1,bin,<BIN>,cell,<CELL>,task,<TASK>
```

**Verdict**, one per instance: per motor, per hold, per channel:

```
SIGNOFF,sf,1,bin,<BIN>,cell,<CELL>,task,<TASK>,motor,<LEFT|RIGHT|NONE>,crit,<CRIT>,measured,<n|NA>,lo,<n|NA>,hi,<n|NA>,units,<UNITS>,n,<count>,verdict,<PASS|FAIL|NOT_BUILT|NOMEAS>
```

**Rules:**
- **Tag first, and the tag is `SIGNOFF`, never `BS-`/`BC-`/`T0-`.** One grep finds every verdict
  from every binary.
- `sf` is the sign-off format version. It is independent of each binary's own `FMT_VERSION`.
- **Fixed field order; every field always present; absence is the token `NA`** (existing
  discipline, `test_bench_scan.spin2:83-86`).
- **Numbers may carry the `_` digit grouping** that `lineAddNum`/`udec_`/`sdec_` print (PL-17).
  The parser strips `_` from numeric fields.
- `n` is the sample or instance count behind `measured`, e.g. starts counted or zeros in a spread.
  `n,0` with `verdict,NOMEAS` means nothing was measured.
- **`NOMEAS`** = the binary could not take the measurement (prerequisite skipped, run aborted,
  too few samples). **`NOT_BUILT`** may be printed by a binary for a cell compiled out of this
  build variant. The host treats that exactly like absence. **Neither is ever `PASS`.**
- **Booleans print `TRUE`/`FALSE` in `measured`/`lo`/`hi` too**, with `units,BOOL`. STEPHEN,
  2026-09-12: booleans print as TRUE/FALSE, never numbers. Sign-off records are not an exception.
  - The parser maps `TRUE`/`FALSE` to 1/0 for the range check, and only when `units` is `BOOL`.
  - A numeric value under `units,BOOL`, or a boolean token under any other unit, is `MALFORMED`.
  - The tables in §A.4 write `1` for `TRUE` as shorthand; the manifest file carries the tokens.
  - *(Arbiter review 2026-09-13: the first draft sanctioned 0/1 here.)*

### B.2 Worst-case bytes — 193, under the 280-byte bound

The tokens are bounded like every other builder token field: `BIN` ≤ 6, `CELL` ≤ 20,
`CRIT` ≤ 18, `UNITS` ≤ 8; task ≤ 5 as `3_537`. Numbers are clamped to `LIM_BIG` (≤ 12 bytes);
`n` is clamped to `LIM_SMALL` (≤ 7).

| Part | Bytes |
|---|---|
| `SIGNOFF` | 7 |
| `,sf,1` | 5 |
| `,bin,` + 6 | 11 |
| `,cell,` + 20 | 26 |
| `,task,` + 5 | 11 |
| `,motor,` + 5 | 12 |
| `,crit,` + 18 | 24 |
| `,measured,` + 12 | 22 |
| `,lo,` + 12 | 16 |
| `,hi,` + 12 | 16 |
| `,units,` + 8 | 15 |
| `,n,` + 7 | 10 |
| `,verdict,` + 9 | 18 |
| **Total** | **193** |

`SIGNOFF-DECL` worst case: 12 + 5 + 11 + 26 + 11 = **65**. The host's `[timestamp] CogN` prefix is
added by `pnut-term-ts` on the host, not inside the P2's debug string [M log format,
`debug_260913-120844.log:19`], so it does not count against the bound.

### B.3 Emitting it from a binary that uses the BS- line builder (scan, char)

**No builder method changes.** A new `PRI emitSignoff(...)` calls only the existing methods:
`lineReset`, `lineAddText`, `boundedField`, `naOrBoundedField`, `tokenField`, `lineEmit`.

- **So PL-17's byte-identity holds by construction.** Every existing record's bytes are unchanged,
  because no existing emitter is touched and no builder method is edited.
- New tokens are new `DAT` strings.
- The `TOKMAX_*` additions are `TOKMAX_BIN = 6`, `TOKMAX_CELL = 20`, `TOKMAX_CRIT = 18`,
  `TOKMAX_UNITS = 8` and `TOKMAX_SFVERDICT = 9`. An over-long token prints `?` and fails the
  host's cell-id match, so it becomes `NOT_BUILT`, never `PASS`.

**The watchdog cog emits through a mirrored `wdEmitSignoff()`.** It uses the existing `wd*`
builder plus one new mirror, `wdNaOrBoundedField()`, and never touches `lineBuf`
(`test_bench_scan.spin2:512-513`).
- **Stack re-count, same rule as `:460-478`:**
  | Frame | Longs |
  |---|---|
  | `watchdog` | 3 |
  | `declareStall` | 1 |
  | `wdEmitSignoff` (13 params) | 13 |
  | `wdNaOrBoundedField` | 4 |
  | `wdBoundedField` | 3 |
  | `wdLineField` | 2 |
  | `wdLineAddNum` | 15 |
  | `wdLineAddChar` | 1 |
  | **Total** | **42** |

  42 ≤ 128; `WD_STACK_LONGS` is unchanged.

**The scan's `FMT_VERSION` bumps to 7** for the `SIGNOFF*` records, the new `BS-BUILD` record and
the new `XSTART` zero phase token. No existing record's fields change.

`test_bench_char.spin2` keeps its own builder copy (PL-17) and gains the same `emitSignoff()`
body; «#3521» rewrites it anyway.

### B.4 Emitting it from T0's CSV style

T0 prints with plain `debug()` and literal text. The record is one `debug()` per line, built
entirely from literals plus `sdec_`/`zstr_`. The tag, task, cell, crit and units are constants
in the literal. Only measured, lo, hi, n and verdict vary:

```spin2
debug("SIGNOFF,sf,1,bin,T0,cell,R2-T0-DIRTY,task,3500,motor,NONE,crit,POSTSTOP_REVB,measured,", zstr_(bIsRevB ? @"TRUE" : @"FALSE"), ",lo,TRUE,hi,TRUE,units,BOOL,n,", sdec_(nBases), ",verdict,", zstr_(bPass ? @"PASS" : @"FAIL"))
```

- The ternary selects **pointers and values only**, never method calls (PL-29).
- `sdec_` groups digits with `_`, and the parser strips them (B.1).
- The widest T0 verdict line above is well under 255 data bytes (the single-`debug()` ceiling,
  `test_bench_scan.spin2:4186-4187`). T0's records are short enough not to need the builder.
  UNVERIFIED: whether `debug()`'s 255-byte limit counts literal text; if it does, T0 adopts the
  line builder for `SIGNOFF` records only.
- T0's existing `T0-n,…` lines are untouched.

### B.5 The host parser

A log line qualifies only if it matches:

```
^\[[^\]]+\] Cog[0-7]\s+(SIGNOFF(-DECL)?,.*)$
```

- **Any cog number is accepted.** The watchdog's records come from a cog other than 0.
- The payload is split on `,` into name/value pairs.
- A malformed record is a parse error: wrong pair count, unknown name order, non-numeric numeric
  field, unknown verdict token. It is reported with its line number and contributes **`NOMEAS`
  (reason `MALFORMED`)** to its cell, never `PASS`.

---

## C · Map — who emits which verdict

### C.1 On-board vs host

| Row | On-board emitter(s) | Host-side cell | Why host, if host |
|---|---|---|---|
| 1 | SCAN (`startSide`), T0 (T0-15) | — | |
| 2 | SCAN (`startSide`), T0 (T0-14), CHAR (`ISCALE`) | **`R2-HOST-DETDIFF`** | The criterion compares the visit's log with the 2026-09-11 baseline, taken in a different power cycle. No single binary run holds both. |
| 3 | SCAN, CHAR, T0 (T0-13) | — | |
| 4 | T0 (T0-3), CHAR (rpm) | — | |
| 5 | SCAN (self-check), CHAR | — | |
| 6 | SCAN | — | |
| 7 | SCAN | — | |
| 8 | SCAN, T0 (T0-11) | — | see below |
| 9 | SCAN | — | |
| 10 | SCAN or CHAR (J.1), T0 (T0-15d), CHAR (steering) | **`R10-HOST-PL9`** | A static source property; no binary can observe a rename. |
| 11 | SCAN cog 0 / watchdog; SCANWD watchdog | **`R11-HOST-WDTEND`** | "The session ended itself" is only visible after the P2's last byte, as the end marker in the host log. |
| 12 | SCAN | — | |
| 13 | CHAR | — | |

**Decision on row 8's across-lifetime spread: on-board, not host.**
- The state is 8 longs per motor (min and max × 4 channels), updated once per lifetime. A driver
  restart does not reset the test binary's `VAR`s: only the driver cog restarts, and cog 0 keeps
  running.
- Putting it on the host would mean the host computes a verdict from `BS-ZERO` measurement
  records, which is exactly the inference rule 0.1 forbids. It would also make row 8 depend on
  `BS-ZERO`'s field layout, which is not a sign-off contract.
- The one thing on-board cannot do is compare zeros **across binaries** (scan against T0-11).
  That comparison is not the criterion; each binary's own spread is.

### C.2 `R2-HOST-DETDIFF` — the detection-sweep diff

**Inputs:**
1. The visit's `detect-phase2` log. It qualifies only with `BD-BANNER … tool,test_bench_detect`,
   `BD-BUILD … phase2_compiled,1`, and `BD-CFG cfg_id,BENCH`.
2. The baseline `DOCs/analyses/bench/2026-09-11/debug_260911-210229.log`.
3. `DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv`. «#3505»'s prediction list is copied into
   it verbatim, one line per predicted change, with columns
   `sw · grp · field · baseline_value · predicted_value · note`.

**Void checks, from the binary's own VOID rules** (`debug_260911-210229.log:56-57`). Any of the
following makes the cell `NOMEAS` (reason `VOID`):
- `BD-CLK match 0`
- any `BD-ENUM match 0`
- missing banner
- a build-variant mismatch (`BD-NOTE DIFF` rule, `:69`)

**What is compared. Not a raw line diff, because a raw diff cannot pass on identical hardware:**
- `BD-REP` lines carry per-repeat timing (`sumtix`, `fltix`, `iter`), which varies within a
  single run: `fltix` 19_984 vs 20_408 across repeats of one cell [M `:126-157`]. So do `BD-RUN`
  (a timestamp), `BD-CAL` (timing) and `BD-BUILD src_rev`.
- `BD-NOTE` text has changed since the baseline. For example, the calibration pin moved from P44
  to P15 (`test_bench_detect.spin2:161-169` vs baseline `:55`).
- **So the diff runs over the semantic records** listed below, excluding `BD-LIB` brackets as the
  binary's own `DIFF` rule says (`:67-68`).

| Record, keyed by | Fields compared | "Unchanged" means |
|---|---|---|
| `BD-CELL` (`sw`,`grp`) | `modal`, `libvrd`, `agree`, `va`, `vb`, `vn` | exactly equal |
| `BD-CELL` (`sw`,`grp`) | `sum_min`, `sum_max`, `sum_mean` | exactly equal when the baseline value is 0 or 500. Otherwise within **±11**: the MEASURED cross-run Rev B band is 93–104 (`isp_bldc_motor.spin2:851-853`), so 104 − 93 = 11 [D]. |
| `BD-ENUM` (`grp`) | `local`, `lib`, `match` | exactly equal |
| `BD-PLAN` (`sw`) | all | exactly equal |

**Excluded by design, and printed as excluded:**
- Sweeps 3 and 6. They are running-driver cells, void by design (`:76-77`; «#3505»).
- `BD-CFG` and `BD-MAP`. They are operator-declared configuration, not measurement. The baseline
  says `left_base,0` (`:20`) while the boards sat at P32 (`test_bench_char.spin2:110`). If
  «#3505»'s list names a `BD-CFG`/`BD-MAP` change it is checked; otherwise the differences are
  printed as `INFO` and do not enter the verdict.

**Verdict:**
- Measured = count of unpredicted changes + count of predicted changes that did **not** occur.
- `PASS` iff 0 and every predicted cell is present in both logs.
- A prediction referencing a record absent from the visit log counts as not occurred. **Except
  when the visit log marks that cell `SKIPPED`** by the gate-input guard (§C.3). Such a
  prediction is `NOT_COMPARED`: it is listed on the sheet, and it counts neither toward `PASS`
  nor as a change. *(Arbiter review 2026-09-13.)*
- **`R2-HOST-DETDIFF` passes only if at least one post-stop cell was compared on each of P0_P15
  and P16_P31.** An all-skipped diff is `NOMEAS`, never `PASS`.

### C.3 Detection binary change for Visit 1 — never pulse a board's gate input

*(Arbiter ruling on J.2, 2026-09-13. Implemented in phase 2, in `src/test_bench_detect.spin2`.)*
1. **Skip any group whose sense pin (base+4) lands on a configured board's pin other than that
   board's own sense pin.** Compute it from `user.LEFT_MOTOR_BASE` / `user.RIGHT_MOTOR_BASE` and
   the 16-pin span, for every sweep. Its cells emit as `SKIPPED` with reason `GATE_OVERLAP`,
   fixed-field, so the record count still matches `BD-PLAN`.
   - Today that is `NO_USE_P24_P39` (P28) and `P40_P55` (P44).
   - Read `overlapToken()` first. If it already classifies from the configured bases, reuse it.
2. **Refuse to start a phase-2 driver cog whose driven pins overlap another configured board.**
   Emit the sweep as `SKIPPED`, reason `COG_OVERLAP`. Today neither phase-2 group overlaps a
   board: P0_P15 is empty, and P16_P31 is the right board itself.
3. **Fix the stale safety text** (PL-35):
   - the `BD-NOTE`s that name P12/P28 as the tail groups' gate pins and call P44 unconnected;
   - the overlap token strings that name `P0_P15`/`P16_P31` as the boards;
   - the `DETECT_NO_TAIL` description, since it no longer maps to the gate-adjacent groups;
   - the group comments at `:108-113`.
4. **Bump `SRC_REV`.** The detect-phase2 tier's precondition in `tools/bench-run.sh` changes from
   "MOTORS MUST BE PHYSICALLY UNPLUGGED" to a statement of the guard. It changes in the same
   commit, not before: the precondition stays true for the current binary until this lands.
5. **Proof the guard works** (sign-off cell `R2-DETECT-GUARD`, bin `HOST`, from the visit log):
   - no `BD-REP` exists for a skipped group;
   - `BD-MAP` shows those groups classified as gate overlaps;
   - every `BD-SWEEP` count matches the plan less the skipped cells.

   It can fail. A run of today's binary shows `BD-REP` records for P40_P55.
- The sheet lists every unpredicted change with both log line numbers.

---

## D · The collation script — `tools/signoff-collate.py`

### D.1 Language: Python 3, standard library only

**What `tools/` holds today** (read directly; this harness has no directory listing):
- **Bash:** `build-check.sh`, `bench-run.sh`, `check_style.sh`, `doc-audit.sh`.
  `check_style.sh`'s own header describes Python-style record handling (`rec['comment_kind']`,
  PL-12).
- **Python:** `test_bench_char.spin2:183` names `tools/gen_bench_char_assets.py` as the generator
  of its layer geometry (existence UNVERIFIED: not opened). PL-15 records Python 3.10.7 present on
  the bench Mac [M, 2026-09-11].

**Why Python, not bash:** the job is TSV rewrite-in-place, per-cell aggregation over repeated
instances, numeric comparison with `_`-grouped numbers, and a keyed semantic diff of `BD-CELL`
records. In bash each of those is a fragile `awk` program. Python's stdlib (`csv` with
`delimiter='\t'`, `re`, `argparse`, `pathlib`) does all of it with no install.

**External commands:** the script runs **none**. It reads files and writes two files. If a later
change needs one (e.g. `git rev-parse`), it goes through a single `run()` helper that prints
`+ <argv verbatim>` before running it, the same contract as `bench-run.sh:59-64`. A test in
`--selftest` asserts that no `subprocess` call exists outside `run()`.

### D.2 Invocation

```
tools/signoff-collate.py --visit 1 --date 2026-09-XX [--update] [--static-tree] \
    [--manifest DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv] \
    [--baseline-detect DOCs/analyses/bench/2026-09-11/debug_260911-210229.log] \
    [--out DOCs/analyses/bench/<date>/VISIT-<n>-SIGNOFF.md] \
    <log> [<log> ...]
tools/signoff-collate.py --check-ready <visit>
tools/signoff-collate.py --selftest
```

- **Inputs:** the visit's curated logs, named explicitly and never globbed by the script, plus the
  manifest. Also the detection predictions file and baseline when `R2-HOST-DETDIFF` is owed.
- **`--update`** rewrites manifest statuses and regenerates `SIGNOFF-MANIFEST.md`. Without it, the
  manifest is read-only. That is how the negative case (§E) runs without touching the record.
- **`--static-tree`** evaluates `HOST` static cells (`R10-HOST-PL9`) against the working tree.
  Without it they are `NOT_BUILT` (reason `STATIC_NOT_REQUESTED`), so a log-only run can never
  certify a source property.
- **Exit codes:** 0 = sheet written; 2 = usage, input or manifest error, and nothing written.
  Verdict content is in the sheet, not the exit code, so a `FAIL` never looks like a tool
  failure.

### D.3 Per log, before any verdict

1. **Identity:** record the first banner line (`BS-BANNER`, `BC-BANNER`, `* test_bench_t0`,
   `BD-BANNER`) and `BS-BUILD` if present.
2. **Completeness:** the log is `COMPLETE` iff a `CogN  DEBUG_END_SESSION` line exists.
   - Otherwise it is `TRUNCATED`: every `PASS` instance from it is downgraded to `NOMEAS`
     (reason `LOG_TRUNCATED`), and its `FAIL` instances are kept.
   - This honours the plan's rule that *"a truncated log must never yield a verdict"* (§6) for
     the direction that matters. A real failure printed before a truncation is still a failure.
3. **Declarations:** collect `SIGNOFF-DECL` records → the set of cells this log declares.
4. **Verdicts:** collect `SIGNOFF` records. Validate each:
   - `bin` equals the manifest cell's `bin`, else `NOMEAS` `BIN_MISMATCH`.
   - `task` equal, else `NOMEAS` `TASK_MISMATCH`.
   - `crit` matches, else `NOMEAS` `CRIT_MISMATCH`.
   - `lo`/`hi` equal the manifest's, else `NOMEAS` `LIMIT_MISMATCH`.
   - **Re-check the arithmetic:** a record printing `PASS` whose `measured` is outside `lo..hi`,
     or `FAIL` inside it, becomes `FAIL` (reason `VERDICT_INCONSISTENT`). The binary's judgement
     is trusted only when it agrees with its own numbers.
   - A cell id not in the manifest is listed as `UNMANIFESTED` and has no effect.

### D.4 Per cell, then per row

**Which logs speak for a cell — a rerun cannot hide a `FAIL`.** *(Arbiter review 2026-09-13. The
first draft let the latest declaring log supersede earlier ones, which makes rerunning until green
a way to reach `PASS`.)*
- **Group the declaring logs by build identity:** the binary's banner `src_rev` and `fmt`, plus
  `sf`.
- **Within the latest build that declares the cell, every log speaks.**
  - Any `FAIL` instance in any of its logs makes the cell `FAIL`, whatever a later log of that
    same build printed. A rerun of an unchanged binary is a second sample, not a correction.
  - `TRUNCATED` logs contribute only their `FAIL` instances (§D.3.2).
- **`min_inst` is met inside one `COMPLETE` log.** Instances are never pooled across logs, so two
  partial runs cannot add up to one whole one.
- **An earlier build's logs are listed as `superseded`,** with their verdicts. They are superseded
  only because the binary changed (a fix landed), and the sheet names both builds.

**Cell verdict:**

| Situation in the speaking log | Cell verdict |
|---|---|
| No log in the set declares the cell (and, for HOST cells, the required input is absent) | `NOT_BUILT` |
| Any instance `FAIL` | `FAIL` |
| Declared, zero `SIGNOFF` instances | `NOMEAS` (`NOT_REACHED`) |
| Any instance `NOMEAS`/`NOT_BUILT` and no `FAIL` | `NOMEAS` |
| Instances all `PASS` but fewer than `min_inst` | `NOMEAS` (`TOO_FEW_INSTANCES`) |
| At least `min_inst` instances, all `PASS` | `PASS` |

**Row verdict:** `FAIL` if any cell is `FAIL`; else `NOT_BUILT` if any cell is `NOT_BUILT`; else
`NOMEAS` if any cell is `NOMEAS`; else `PASS`.

**Precedence is deliberately pessimistic:** one unbuilt cell keeps a row out of `PASS` even if
every other cell passed.

### D.5 Outputs

**`DOCs/analyses/bench/<date>/VISIT-<n>-SIGNOFF.md`:**
- The header names the visit, date, script path, manifest path and every input log with its
  identity and `COMPLETE`/`TRUNCATED`.
- **One line per manifest row owed to this visit:** row, task, feature, **row verdict**.
- Then **one line per cell:** cell verdict, reason if not `PASS`, `measured`/`lo`/`hi`/`units`,
  and **the proving log line**, as `file:line`, for each instance.
- Every `OWED` cell for this visit with no verdict is listed under **`NOT_BUILT`**, explicitly and
  never omitted.
- Sections for `superseded`, `UNMANIFESTED`, parse errors, and the `DETDIFF` change list.

**With `--update`:**
- `SIGNOFF-MANIFEST.tsv` statuses move per A.2. `status_ref` is `V<n>:<file>:<line>;…`.
- `SIGNOFF-MANIFEST.md` is regenerated.

**`--check-ready <visit>`** — the scheduling gate of A.3 rule 2:
- For every `OWED` cell owed to that visit, it reads the `bin`'s source (`SCAN`/`SCANWD` →
  `src/test_bench_scan.spin2`, `T0` → `src/test_bench_t0.spin2`, `CHAR` →
  `src/test_bench_char.spin2`).
- It requires the literal cell id to appear in a `SIGNOFF-DECL` emission.
- `HOST` cells require their input paths or flags to be named in the manifest `test` column.
- Prints each gap and exits 3 if any exist.

### D.6 What «#3509» (the log-to-verdict analyser, Batch 2) keeps

This mechanism takes **sign-off**: is a landed feature present and working to its stated
criterion? «#3509» keeps **measurement analysis**, which produces numbers and findings rather than
feature verdicts:
- the speed law, C-4 deceleration and the fault boundary
- T1 curve fits and C-6 with its wiring-drop `INCONCLUSIVE` rule
- `BS-POINT`/`BC-SENSE` statistics and regression tables against Pass 1
- vibration evidence, and cross-run comparisons of offset minima

It should **import** this script's log reader (the `Cog[0-7]` line regex, `_` stripping and the
`COMPLETE`/`TRUNCATED` rule) rather than re-implement it. It must never emit `SIGNOFF` verdicts
of its own. If an analysis result becomes a certification criterion, the owning binary gains a
cell.

---

## E · The required negative case — scan run 5 must be `NOT_BUILT` everywhere

**Input:** `DOCs/analyses/bench/2026-09-13/debug_260913-120844.log`. FMT 4, 799 lines, no
`SIGNOFF*` records, no `DEBUG_END_SESSION` (the run locked up) [M, evaluation header and §7].

**Command** (written into `--selftest` and runnable by hand):

```
tools/signoff-collate.py --visit 1 --date NEGCASE --out <scratchpad>/NEG.md \
    DOCs/analyses/bench/2026-09-13/debug_260913-120844.log
```

**No `--update`, no `--static-tree`, no detect baseline.**

**Expected:** every one of the 13 rows is `NOT_BUILT`, every cell is `NOT_BUILT`, and the log
identity reads `TRUNCATED`. **Row 8 in particular is `NOT_BUILT`, never `PASS`, although the log
contains a `BS-ZERO` record before every one of its ~75 points, carrying per-lifetime zeros.**

**How the design guarantees it, and not merely expects it:**
1. **The only verdict-bearing parse is `^…Cog[0-7]\s+SIGNOFF(-DECL)?,`.** No code path reads
   `BS-ZERO`, `BS-START`, `BS-CHECKSUM` or any other measurement record for a verdict. Row 8
   cannot be computed from the zeros because nothing computes it host-side (§C.1 decision).
2. **The default is `NOT_BUILT`,** assigned before any log is read. A cell leaves it only through
   a declaring log (D.4 table), and this log declares nothing.
3. **`PASS` needs `min_inst` positive `PASS` instances** (D.4). "Zero FAIL instances" appears in
   no condition that yields `PASS`.
4. **The three HOST cells need named inputs this invocation does not supply:**
   - `DETDIFF` needs a detect log plus the baseline.
   - `PL9` needs `--static-tree`.
   - `WDTEND` needs a log whose `BS-BUILD` says `wd_selftest TRUE`, and run 5 has no `BS-BUILD`.

   So each is `NOT_BUILT`.
5. **Even if a `SIGNOFF` record were present, a `TRUNCATED` log cannot yield `PASS`** (D.3.2).
   That is a second, independent barrier for this specific log.

**`--selftest` asserts all of the above**, plus two falsification checks:
- **With `--static-tree` on today's tree, `R10-HOST-PL9` is `FAIL`**, because `gapInMS` is still
  at `isp_bldc_motor.spin2:253` and `:316-317`. That proves the static cell can fail.
- A synthetic in-memory log with one `SIGNOFF` whose `PASS` contradicts its own `measured` yields
  `FAIL` (`VERDICT_INCONSISTENT`).

The sheet produced by the negative case goes to the scratchpad, never to `DOCs/`.

---

## F · Scan changes — to be implemented later on the committed scan (SRC_REV 7, FMT 7)

### F.1 New state: one `VAR { sign-off accumulators }` block, indexed by `sideSlot()`/`resultSlot()`

| State | Size | Row |
|---|---|---|
| `sfStarts`, `sfCogBad`, `sfRevbBad`, `sfOffsetsBad`, `sfStartIllegal`, `sfNotAlive` | 6 × 2 | 1, 2, 6, 7, 12 |
| `sfIntegSum`, `sfIntegN` | 2 × 2 | 3 |
| `bSfLifetimeFresh`, `bSfReadyOk` | 2 × 2 | 12 |
| `zxsMin`, `zxsMax` (controlled starts) and `zxsAllMin`, `zxsAllMax` (every lifetime), each `[2 × 4]` channels i,u,v,w | 32 | 8 |
| `zxsN`, `zxsAllN` | 2 × 2 | 8 |
| `bSelfRan`, `bSelfIOk`, `bSelfRateOk` | 3 × 2 | 5, 12 |
| `bResLegRan`, `bResCliff`, `resZeroMissing` | 3 × `RESULT_SLOTS` | 9 |
| `bLegZeroValid[MAX_LEG_POINTS]` | 48 | 9 |
| `rstAloneState`, `rstAloneMs` (J.1 variant only) | 2 × 2 | 10 |

About 150 longs, all `VAR`, all cog-0-owned. The watchdog reads none of them.

### F.2 Where each run-level verdict is computed

- **`startSide()`** (`:1009-1049`), after the existing checks:
  - `sfStarts += 1`; `sfCogBad += not bCogOk`; `sfRevbBad += not bRevB`;
    `sfOffsetsBad += not bOffsetsOk`; `sfStartIllegal += (nIllegal <> 0)`.
  - `sfIntegSum += nMissed + nIllegal`.
  - `bSfLifetimeFresh := TRUE`. `bSfReadyOk := sideIsReady(side)` — `waitReady()` has just
    returned.
- **The site that raises `AR_OFFSET_READBACK`** (inside `applyOffsets`, not re-read for this
  design): `sfOffsetsBad += 1`.
- **`measureZero()`** (`:1063-1160`), after the sampling loop:
  - **If `bSfLifetimeFresh`:** alive = `bSfReadyOk and bValid and (minMv <> maxMv)`, and if not
    alive then `sfNotAlive += 1`. Fold the four channel means (`meanX10`, `senseU/V/Wmean`) into
    `zxsAll*` and `zxsAllN += 1`. `bSfLifetimeFresh := FALSE`.
  - **If `phaseTag == PH_XSTART`:** also fold them into the controlled `zxsMin/Max`, and
    `zxsN += 1`.
  - `emitZero()` is unchanged. The existing `BS-ZERO` bytes stay identical.
- **`measurePoint()`** (`:1353-1357`): when `bPtIntegValid`,
  `sfIntegSum += ptMissedD + ptIllegalD` and `sfIntegN += 1`.
- **`legMeasure()`:** store `bLegZeroValid[idx] := bPtZeroValid` beside the existing `legZeroX10`.
- **`runSelfCheck()`** (`:1266`): `bSelfRan := TRUE`, `bSelfIOk := bPosIOk and bNegIOk`,
  `bSelfRateOk := bRateOk`.
- **`runLeg()`** (`:1838-1861`, beside the existing result store):
  - `bResLegRan[slot] := (legExit <> LX_SKIPPED)`; `bResCliff[slot] := legCliffFound`.
  - `resZeroMissing[slot]` := count of stored points with `isValidIdx(i)` and not
    `bLegZeroValid[i]`.
- **`emitSignoffs()`** — new; runs once. Called from `main()` inside the
  `if wdDeclaring == FALSE` branch, **after** the existing `cogstop(wdCogId)` and **before**
  `emitEnd()` (`:841-846`), so it can never race the watchdog. It runs after `shutdownMotors()`,
  so no timed window contains a `debug()` (header rule `:92-93`). Instances:

| Cell | Instances | measured / n | NOMEAS when |
|---|---|---|---|
| R1-SCAN-COGOK, R2-SCAN-REVB, R6-SCAN-OFFSETS, R7-SCAN-STARTILL, R12-SCAN-ALIVE | per motor | the bad count / `sfStarts` | `sfStarts = 0` |
| R3-SCAN-INTEG | per motor | `sfIntegSum` / `sfStarts + sfIntegN` | `sfStarts = 0` |
| R5-SCAN-SELF, R12-SCAN-RATE | per motor | `bSelfIOk` / `bSelfRateOk` as 1/0 | `bSelfRan = FALSE` |
| R8-SCAN-ZXS | per motor × channel, `crit ZXS_<ch>` | `(zxsMax − zxsMin)` in mV×10 / `zxsN` | `zxsN < ZXS_STARTS` |
| (info) `ZXSALL_<ch>` | per motor × channel | `(zxsAllMax − zxsAllMin)` / `zxsAllN` | always, with `lo`/`hi` `NA` (§A.5-e) |
| R9-SCAN-HALFLEG | per half slot | `hasMinimum(slot) or bResCliff[slot]` | `bResLegRan[slot] = FALSE` |
| R9-SCAN-OWNZERO | per slot with `bResLegRan` and `resStatus <> FS_NOT_BRACKETED` | `resZeroMissing[slot]` | no such slot on that motor |
| R9-SCAN-PAIR2 | per motor | 1 when `bComplete` and the `ratio_net` value is valid; the `ratio_raw` NA is structural in `emitPair2` | `bComplete = FALSE` |
| R10-SCAN-RSTALONE | per motor (J.1 variant) | ms to cleared, or NA with FAIL | no natural fault on that motor |
| R11-SCAN-NOSTALL | one, motor NONE | 1 | never: reaching here is the evidence |

For the R9 cells, the half-speed `NOMEAS` case covers the leg skipped for a failed quarter-speed
prerequisite, and a run that aborted before the leg.

A motor whose block never ran (e.g. the run aborted on LEFT) emits its instances as `NOMEAS`,
`n,0`. **Every declared cell gets a verdict on every cog-0 exit path**, because `emitSignoffs()`
sits on the one path all of `main()`'s exits share.

### F.3 The deliberate cross-start zeros (row 8)

In `runMotorBlock()`, **before** the existing `restartSide(side)` at `:981`:

```
repeat ZXS_STARTS                       ' 5, A.5-e
    if abortReason <> AR_NONE
        quit
    restartSide(side)                   ' existing wrappers: CP_LIB_STOP / CP_LIB_START / CP_LOOP_WAITREADY
    if abortReason == AR_NONE
        measureZero(side, PH_XSTART)    ' existing loop: beat(CP_LOOP_ZERO) every SAMPLE_MS
    restLoop()                          ' the existing REST_MS beat-polled loop, factored out of measurePoint
```

- **`PH_XSTART` is appended at the end** of the `PH_*` enum, so no existing value renumbers.
- Its token is `XSTART` (6 ≤ `TOKMAX_PHASE` 9).
- **`phaseToken()` needs an explicit `PH_XSTART:` case.** Its `other:` maps any unlisted phase to
  `ZERO_INIT` (`:3897-3898`), which would silently mislabel it.
- The existing `restartSide` + `PH_ZERO_INIT` + self-check then proceed unchanged.
- **Cost** [D]: 5 × (1.0 s zero + 0.5 s rest + start and ready of a few ms) ≈ **7.6 s per motor**.
  That is negligible against `RUN_TIME_CAP_S` = 1800.
- **The wheel is floated throughout.** `init()` forces `SM_FLOAT` (`isp_bldc_motor.spin2:336`) and
  nothing is commanded, so no bridge current flows during these zeros. That matches the existing
  zero discipline (`:1074-1076`).

### F.4 Watchdog discipline for every new loop

- **No new timed loop is introduced.** The only loops added are the `repeat ZXS_STARTS` above,
  whose body is entirely existing beat-polled calls, and `emitSignoffs()`, which contains no wait.
  - `measureZero()` beats every `SAMPLE_MS` (5 ms).
  - `restLoop()` beats every `SAMPLE_MS`.
  - Every library call is bracketed by its `CP_LIB_*` beat.
  - Every `lineEmit()` beats `CP_EMIT`.
- **No `waitms()` argument added anywhere exceeds `SAMPLE_MS`**, except `WD_POLL_MS` (250 ms)
  inside the self-test stall (§G). That one is deliberately beat-free, and it is still far under
  `WD_STALL_MS` (4 000) and `WAITMS_MAX_MS` (7 953).
- **The longest legitimate un-beaten gap is unchanged:** `testResetFault()` at ≤ 2 030 ms, already
  the basis of `WD_STALL_MS` (`:444-456`). The J.1 scan variant calls it in the same
  `CP_LIB_RESETFAULT` bracket, so it adds no longer gap.
- **New checkpoint `CP_SELFTEST` is appended** at the end of the `CP_*` enum. Its token is
  `SELFTEST` (8 ≤ `TOKMAX_CP` 10), with a matching `checkpointToken()` case.

### F.5 New header records

- **`BS-BUILD`**, emitted immediately after `BS-BANNER`:
  `BS-BUILD,wd_selftest,<TRUE|FALSE>,sf,1,zxs_starts,5,zxs_max_mV_x10,50`.
  - `wd_selftest` comes from its own `#ifdef WD_SELFTEST` / `#else`, following `emitBanner()`'s
    existing `cfg_id` pattern (`:2960-2971`). A mistyped flag lands on the honest `FALSE`.
  - `BS-BANNER` itself is not changed.
- **Then one `SIGNOFF-DECL` per cell** this build judges:
  - normal build: R1, R2, R3, R5, R6, R7, R8, R9, R11-SCAN-NOSTALL, R12 (and R10 per J.1);
  - `WD_SELFTEST` build: the four `R11-WDT-*` cells only.

### F.6 Record fix carried in the same change — `BS-ZERO health_ok`

*(Arbiter review 2026-09-13, from §K.3 item 3.)*
- **The defect.** `measureZero()` passes `bZeroOk[slotIdx]` to `emitZero()` for every phase
  (`test_bench_scan.spin2:1157`). `bZeroOk` is set only by `PH_ZERO_INIT`, so every per-point
  `BS-ZERO` prints the motor block's `ZERO_INIT` health verdict under a label that reads as its own.
- **The fix (FMT 7).**
  - `health_ok` prints the zero's own health verdict when `phaseTag == PH_ZERO_INIT`, and `NA` for
    every other phase.
  - The field's name and position are unchanged.
  - The runsheet's `BS-ZERO` description is updated to match.
- **Why here.** It is the project's record rule: never print a value under a label that
  misdescribes it. The scan is being changed and re-versioned in this same step anyway.

---

## G · Watchdog self-test tier (row 11)

### G.1 Build flag

`-D WD_SELFTEST`, as named in the task. Because pnut-ts silently ignores an unknown `-D`
(`bench-run.sh:98-104`), the flag's effect is proven in the log three ways:
- `BS-BUILD wd_selftest,TRUE` (F.5).
- The declarations name `R11-WDT-*` and not the scan's cells.
- `R11-HOST-WDTEND` refuses a log lacking either.

A mistyped flag produces a normal scan, which declares a different cell set, so the self-test
cells are `NOT_BUILT` rather than silently passing.

### G.2 `tools/bench-run.sh` tier (proposed text only)

```bash
    scan-wdtest)    BENCH_FILE="test_bench_scan.spin2"
                    EXTRA_DEFS=(-D WD_SELFTEST)
                    PRECONDITION="MOTORS CONNECTED, BOTH WHEELS FREE TO TURN -- WATCHDOG SELF-TEST: a brief preflight nudge per wheel, then the scan stalls ON PURPOSE; the watchdog must stop both drivers and end the session within about 15 s"
                    ;;
```

Plus a `usage()` line:
`scan-wdtest    watchdog self-test: preflight, deliberate stall, watchdog ends the run  [MOTORS CONNECTED]`.

Every command is still echoed verbatim by the existing `run()` (`:61-64`).

### G.3 Where the deliberate stall goes

In `runScan()`, immediately after `preflightWheels()` (`:891-892`), and compiled only under
`#ifdef WD_SELFTEST`: `runWatchdogSelfTest()` followed by `return`. The motor blocks are never
compiled into the self-test's path.

```
PRI runWatchdogSelfTest() | stallStartMs
    if abortReason <> AR_NONE or wdCogId < 0
        emit the four R11-WDT-* SIGNOFFs as NOMEAS, n 0          ' no watchdog, or no preflight: nothing to test
        return
    emitSelfTestArm()        ' BS-WDTEST-ARM,l_cog,<n>,r_cog,<n>,checkpoint,<CP_SELFTEST>,stall_ms,4_000,poll_ms,250,backstop_ms,12_000
    beat(CP_SELFTEST)        ' the LAST beat
    stallStartMs := getms()
    repeat                   ' deliberate stall: NO beat() from here
        waitms(WD_POLL_MS)
        if wdDeclaring
            repeat
                waitms(WD_IDLE_MS)          ' the watchdog owns the session's end; never emit, never beat
        if (getms() - stallStartMs) >= WD_SELFTEST_BACKSTOP_MS
            quit
    emit R11-WDT-FIRES FAIL (measured NA), the other three NOMEAS    ' backstop: the watchdog never declared
```

The stall runs with the RIGHT driver cog still running at zero command. That is the state
`preflightWheels()` leaves (`:950-966`): `restartSide(RIGHT)` stopped LEFT, then the nudge,
`commandMotor(0)`, `waitStopped`. So there is a live driver cog for the watchdog to stop, with
the wheels at rest, as the task text requires. `BS-WDTEST-ARM` records that state before the
stall.

**`WD_SELFTEST_BACKSTOP_MS = 3 × WD_STALL_MS` = 12 000 ms** [D]. That is 2.7× the latest expected
declaration (4 500 ms, G.4), so a working watchdog is never pre-empted. A dead one cannot hang
the session: cog 0 resumes, returns to `main()`, stops both wheels, emits its verdicts and ends
normally. **Either way the session ends itself.**

### G.4 What the watchdog cog emits as its verdict

Changes to `declareStall()` (`:4301-4323`) under `#ifdef WD_SELFTEST`:
1. `wdDeclaring := TRUE` (unchanged), then `emitWatchdog(msSinceBeat)` (unchanged; it already
   reports `checkpoint`, `l_cog`, `r_cog` and `stack_ok`).
2. `bRunningBefore := (wheelL.testGetMotorCog() <> 0) or (wheelR.testGetMotorCog() <> 0)`.
3. `wheelL.stop()`, `wheelR.stop()` (unchanged).
4. `bStoppedAfter := (wheelL.testGetMotorCog() == 0) and (wheelR.testGetMotorCog() == 0)`.
5. Four `wdEmitSignoff` records, from this non-zero cog:

| Cell | measured | lo..hi | verdict |
|---|---|---|---|
| R11-WDT-FIRES | `msSinceBeat` | 4 000..4 500 | PASS iff in band |
| R11-WDT-CKPT | `wdCheckpoint == CP_SELFTEST` | 1..1 | PASS iff 1 |
| R11-WDT-STOPPED | `bRunningBefore and bStoppedAfter` | 1..1 | PASS iff 1 |
| R11-WDT-STACK | `wdStackSentinel == WD_STACK_SENTINEL` | 1..1 | PASS iff 1 |

6. `wdEmitEnd()` and the quoted marker (unchanged).

**The `FIRES` band** [D from `watchdog()`, `:4280-4299`]:
- `lastChangeMs` is taken at the poll that first sees the final beat. The stall is declared at the
  first later poll where `getms() − lastChangeMs ≥ WD_STALL_MS`.
- Polls are `WD_POLL_MS` apart, so the reported `msSinceBeat` is ≥ 4 000 by construction, and at
  most 4 000 plus one poll's scheduling jitter.
- `hi` = `WD_STALL_MS + 2 × WD_POLL_MS` = 4 500 allows a full poll of jitter on top of the
  sampling offset. A value above that means the poll loop is starved; below 4 000 is impossible
  unless the arithmetic is wrong. Both are FAIL.

**In a normal (non-self-test) build,** `declareStall()` also emits `R11-SCAN-NOSTALL` as
**`FAIL`** (measured 0) before `wdEmitEnd()`. Any real stall is thus a recorded failure of «#3534»'s
certification, and every other declared cell becomes `NOMEAS NOT_REACHED` host-side.

**`R11-HOST-WDTEND`** (host) is PASS iff all of the following hold:
- the self-test log is `COMPLETE`;
- `BS-BUILD wd_selftest,TRUE` is present;
- all four `R11-WDT-*` records carry `Cog`*k* with *k* ≠ 0, which proves the watchdog, not cog 0,
  emitted them;
- all four precede `DEBUG_END_SESSION`.

---

## H · Proposed sign-off additions for the not-yet-built binaries

This text is written to be **appended verbatim to the task bodies**. The arbiter appends it; this
design does not touch todo-mcp.

### H.1 Append to «#3504» — Tier 0 extension (T0-11 … T0-15)

> **Sign-off (design: `DOCs/plans/VISIT-SIGNOFF-DESIGN.md` §A, §B.4).**
>
> **Record style.** `test_bench_t0.spin2` emits `SIGNOFF-DECL` (after its banner lines) and
> `SIGNOFF` records with `bin,T0`, in plain `debug()` literals (§B.4).
> - Booleans in other fields print TRUE/FALSE (PL-23). This includes converting T0-3's `agree`
>   and T0-4's `legal`.
> - Every test emits its `SIGNOFF` even if a trapped call aborted: `NOMEAS`, `n,0`.
> - Every new wait is bounded, since T0 has no watchdog: ready ≤ 2000 ms, fixed sample counts.
>
> **Order.** T0-11 and T0-13 run before T0-10. T0-15b (exhaustion) runs **last**, after T0-8's
> slot, per the destructive-last note at `test_bench_t0.spin2:133-138`. T0-12 (hand rotation)
> stays separable and carries no sign-off cell.
>
> | Cell | Test cell | Criterion |
> |---|---|---|
> | `R8-T0-ZXS` | **T0-11**, on `T0_MOTOR_BASE` (P16, motor connected, rail on). 5 cycles of `start()` → wait ready (≤ 2000 ms) → 200 samples × 5 ms of `testGetTelemetry()` i, u, v, w at zero command (`SM_FLOAT`) → `stop()` → 500 ms rest. | Per channel (`crit ZXS_I/U/V/W`), max − min of the 5 lifetime means ≤ 5.0 mV (`lo 0 hi 50`, MV_X10); fewer than 5 valid lifetimes → NOMEAS. Basis §A.5-e. |
> | `R3-T0-STOPPED` | **T0-13**: start at zero command, wait ready, hold 1000 ms, `getHallIntegrityCounts()`. | missed + illegal = 0. |
> | `R2-T0-REPEAT` | **T0-14a**: 32 × `testSetup()` + `getBoardType()` on each populated base, P16 and P32. `stop()` `motorA`/`motorB` first so T0-7's claims are released. | reads ≠ `REV_B` = 0, per base (2 instances). |
> | `R2-T0-DIRTY` | **T0-14b**: on each populated base, `start()` → ready → `stop()`, then `testSetup()` + `getBoardType()`. | reads `REV_B` (1). Before the fix this read `REV_A` 4 of 4 [M]. |
> | `R2-T0-EMPTY` | **T0-14c**: `testSetup(PINS_P0_P15)` + `getBoardType()`. | `REV_Unknown` (1). **Do not probe `PINS_P40_P55`:** its sense pin P44 is the LEFT board's `pin_pwm_w_l` (32 + 12). `getBoardType()` drives it high for 1 ms (`isp_bldc_motor.spin2:889-890`), and T0 runs with the rail on; `test_bench_detect.spin2:161-165` records the same hazard. |
> | `R4-T0-1M-TICKS` | **T0-3**, existing reads. | `ticks(DDU_M)` in 173..174 **and** the three units agree, else FAIL. Basis §A.5-b. |
> | `R1-T0-START` | **T0-15a**: `start()` on P16. | return in 0..7 **and** `== testGetMotorCog() − 1`. |
> | `R1-T0-RESTART` | **T0-15c**: count free cogs (spacer method, `cogspin < 0`, §A.5-a) → baseline; `start()` → free₁; `start()` again with no `stop()` → free₂; `stop()` → free₃. | `|free₂ − free₁| + |free₃ − baseline|` = 0; also free₁ = baseline − 1. |
> | `R10-T0-STOPREADY` | **T0-15d**: after that `stop()`. | `isReady()` FALSE **and** `isStopped()` FALSE. Log `getDriverState()` beside the verdict for the value «#3533» states. |
> | `R1-T0-EXHAUST` | **T0-15b**, last: occupy every free cog, `start()`, release the spacers, count free cogs. | return = −1, `testGetMotorCog()` = 0, free after release = baseline. |

### H.2 Append to «#3521» — automated, meter-free characterisation run

> **Sign-off (design: `DOCs/plans/VISIT-SIGNOFF-DESIGN.md` §A, §B.3).**
>
> **Record style.** `test_bench_char.spin2` emits `SIGNOFF-DECL`/`SIGNOFF` with `bin,CHAR` through
> an `emitSignoff()` built on its own line-builder copy, with no builder method changed (PL-17).
> Every declared cell gets a verdict on every exit path (`NOMEAS` when not measured).
>
> **The run carries no panel, prompt, dwell floor or meter** (ruling 2026-09-12).
>
> **Holds** — the 8 motion holds of Pass 1 (L/R × +¼, −¼, +½, −½), motor frame, default offsets
> 43/317, idle wheel never started. For each hold:
> 1. Start the wheel and call `startSenseCog()` (rpm is written only by the sense task).
> 2. Take a 200 × 5 ms zero at zero command **in the same driver lifetime**.
> 3. Command the increment, wait `AT_SPEED` (bounded), settle 1000 ms.
> 4. Sample ≥ 2000 ms: `sense_i_mV`, `getCurrent()`, ticks, integrity counts. The sum is carried in
>    two longs or as per-second means (PL-20).
> 5. Read rpm ≥ 1 s after `AT_SPEED`.
> 6. Command zero and wait stopped, **then** emit.
>
> | Cell | Criterion per hold (8 instances) |
> |---|---|
> | `R5-CHAR-SENSE` | `(net − 150.1 × A_pass1) × 1000 / (150.1 × A_pass1)` within ±150 (PCT_X10). `A_pass1` per hold = 0.536 · 1.054 · 0.570 · 1.058 · 3.004 · 5.564 · 3.140 · 5.530 A (`CHAR-RUN-EVALUATION.md` table), compiled in as a CON table with its provenance comment. Basis §A.5-d. |
> | `R4-CHAR-RPM` | `rpm − round(ticks_per_s × 60 / 90)` within ±2. Basis §A.5-c. Read through the TEST-USE rpm getter «#3502» now adds, using its real name from source (§K.1 item 9). |
> | `R2-CHAR-ISCALE` | `mean(sense_i_mV) × 10000 / mean(fAmps)` within 135..165. |
> | `R3-CHAR-INTEG` | Per motor (2 instances), summed over its starts and holds: missed + illegal = 0. |
>
> **Steering phase** — after every `wheelL`/`wheelR` instance is `stop()`ped, so their pin claims
> are released (PL-18: the claim registry is shared DAT):
>
> | Cell | Test cell | Criterion |
> |---|---|---|
> | `R10-CHAR-STEERFAIL` | Count free cogs; occupy all but one; `steering.start(LEFT_TEST_BASE, RIGHT_TEST_BASE, PWR_18p5V, BRD_AUTO_DET, BRD_AUTO_DET)`; release the spacers. | return = −1 **and** free cogs = baseline. Left gets the one cog, right fails, left is stopped (`isp_steering_2wheel.spin2:120-129`). |
> | `R10-CHAR-STEERSTART` | `steering.start(...)` normally. | return in 0..7 **and** both wheel driver cogs non-zero via the existing TEST-USE pass-throughs (`c22dba1`; use them, add none). |
> | `R10-CHAR-STEERLIVE` | Drive both wheels through the steering object's public drive call at power **13**, for 700 ms; stop; per-wheel raw tick delta via pass-through. | `|Δticks|` ≥ 6 per wheel (2 instances); sign not judged, because `forwardIsReverse()` mirrors the right wheel. Power 13 [D]: `incrementForPower()` maps 1..100 onto 544 628..147 000 000 (`isp_bldc_motor.spin2:1236-1249`, `:1382`, `:1396`), a slope of ≈ 1 479 347 per step, so power 13 → ≈ 18 297 000, the nearest to `PREFLIGHT_INCRE` 18 375 000. The default `setMaxSpeed` 75 does not clamp it. Basis §A.5-f. |
>
> **Brake-start phase** — per motor × sign (4 instances), cell `R13-CHAR-BRAKESTART`:
> 1. `cog := wheel.startEx(base, PWR_18p5V, BRD_AUTO_DET, TRUE)`.
> 2. `wheel.holdAtStop(TRUE)`.
> 3. `cogatn(1 << cog)`.
> 4. Wait ready.
> 5. `testDriveAtMotorIncrement(±18_375_000)` for 700 ms.
> 6. Zero, wait stopped.
> 7. `holdAtStop(FALSE)`, `stop()`.
>
> Criterion: no fault, tick delta sign = increment sign, `|Δ|` ≥ 6. Basis §A.5-h, including its
> stated limit of falsification.
>
> **NOT BUILT — J.1 was ruled (b) (arbiter review 2026-09-13), so `R10-SCAN-RSTALONE` lives in the
> scan. Kept for the record only.** Option (a) would have been cell `R10-CHAR-RSTALONE`, per motor:
> 1. `testSetFwdRevIndep(3, 317)`.
> 2. Command −¼ (36 750 000) and wait for the fault flag, bounded at 4000 ms. Run 5 faulted at
>    swept 3° on both motors' negative legs [M evaluation §2, §4].
> 3. **Without** a zero command, call `testResetFault()` and time it.
> 4. Restore 43/317, zero, `stop()`.
>
> Criterion: stopped and not faulted, within ≤ 2030 ms. No fault → NOMEAS.

---

## I · The task template rule going forward

**Where it is recorded:** both project overlays exist.
- `.claude/skills/plan-to-tasks/project-overlay.md` has an *Augments §2 — verify criteria*
  section. That is where a task body's verify section is authored, so the primary rule goes
  there.
- `.claude/skills/task-execution/project-overlay.md` gets the landing-time half.

This is proposed text only. Neither file is edited by this task.

**Additive text for `.claude/skills/plan-to-tasks/project-overlay.md`, under *Augments §2 —
verify criteria*:**

> - **Every feature or fix task names its sign-off cells.**
>   - Its verify section lists each cell it will add to `DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv`:
>     the cell id, the binary and test that exercise it, the criterion, the tolerance with its
>     provenance (MEASURED with source, DERIVED with the derivation, or STEPHEN verbatim), and the
>     visit owed.
>   - A property no bench binary can observe says so and names its non-bench cell (a `HOST`
>     static check) instead.
>   - A task whose run-time behaviour has no cell is not ready to dispatch. STEPHEN, 2026-09-13:
>     *"this should be done in every bench run too so we are maximizing our progress with every
>     run"*. Mechanism: `DOCs/plans/VISIT-SIGNOFF-DESIGN.md`.
> - **A task that builds or changes a bench binary lists the cells that binary must declare**
>   (`SIGNOFF-DECL`), so the binary cannot ship without its verdicts.

**Additive text for `.claude/skills/task-execution/project-overlay.md`, as a new *Augments §8 —
landing a feature* section:**

> - **The commit that lands a feature adds its manifest cells** (status `OWED`, visit = the next
>   unscheduled visit) together with the emitting binary's `SIGNOFF-DECL`/`SIGNOFF` code. If the
>   emitting binary is another task's, the commit names that task, and the cell is a gap that
>   blocks the visit.
> - **A visit is scheduled only after `tools/signoff-collate.py --check-ready <visit>` exits 0.**
> - **A sign-off is reported as a sign-off:** "SIGNED_OFF at Visit *n*, `VISIT-n-SIGNOFF.md`
>   line …". Never "verified" from a compile gate or from reading a log by hand. `NOMEAS` and
>   `NOT_BUILT` are reported as themselves, never as passes.

---

## J · Open points: all three ruled by the arbiter (J.1, J.2, J.3)

Everything about how the instrument judges a measurement is decided and argued above.
- **J.1 and J.3 were drafted as owner questions.** On review they are instrument design, with the
  safety facts checked in source. So the arbiter rules on them (arbiter review 2026-09-13).
- **J.2 was asked.** Stephen's answer settled that the board stays powered. The gate-input fact
  behind the unplug rule is not in our records, so the instrument was changed to remove the
  exposure instead (§C.3).

### J.1 · How does the PL-28 "`testResetFault()` alone clears a fault" cell get its fault?

**Context.** The fix is proven only by a fault that is still latched with a **non-zero** command
when `testResetFault()` is called. The scan cannot observe this today: `measurePoint()` commands
zero and waits stopped **before** it calls `recoverFromFault()` (`test_bench_scan.spin2:1335-1337`).

**Option (a) — the char run provokes a fault on purpose.** One per motor: offset_fwd 3°, −¼ speed.
Run 5 faulted at exactly that point on both motors.
- *Pros:* deterministic and isolated. The scan's proven recovery sequence is untouched.
- *Cons:* two extra deliberate faults on the rig per visit, and the char run gains a fault path it
  otherwise does not need.

**Option (b) — the scan uses its own first natural fault per motor.** For that one point, the
scan skips the zero command and calls `testResetFault()` first. If the reset does not clear the
fault, the existing ZERO_CMD → JOG → RESTART sequence follows.
- *Pros:* no extra fault on the rig. The scan faults routinely anyway (run 5's legs are full of
  FAULT points, evaluation §2–§4).
- *Cons:* it changes the committed scan's fault exit for one point per motor. The driver sits
  FAULTED with a non-zero command for up to ~2 s. PWM is already disabled on the fault path
  (`isp_bldc_motor.spin2:2499-2504`, DERIVED), so no current flows. If no fault happens on a
  motor, the cell is NOMEAS.

**Arbiter ruling: (b).**
- It adds nothing to what the rig already endures.
- A motor that never faults in a scan is itself unlikely [M run 5].
- **Safety fact, checked by reading:** the driver's fault branch calls `.driveoff` (disable PWM)
  before it marks `DCS_FAULTED` (`isp_bldc_motor.spin2:2502-2503`). So no bridge current flows
  while the command stays non-zero.
- Option (a)'s block in §H.2 is therefore not built.

### J.2 · The detection-sweep re-run needs the motors physically unplugged — at Visit 1, how?

**Context.** `detect-phase2` starts a real driver cog, and its precondition is **MOTORS
PHYSICALLY UNPLUGGED** (`bench-run.sh:121-123`, `test_bench_detect.spin2:49-51`). The rest of
Visit 1 needs the motors connected. The baseline `debug_260911-210229.log` is a phase-2 build, and
the binary's own rule forbids diffing across build variants (`:69`).

**Option (a) — Stephen unplugs both motors for the `detect-phase2` run** (about a minute of run
time), then replugs.
- *Pros:* `R2-HOST-DETDIFF` runs against the real baseline and covers sweeps 4/5/7/8, the
  post-stop cells that are exactly «#3500»'s fix.
- *Cons:* hands at the bench, one unplug/replug cycle.

**Option (b) — run the passive `detect-lib` build with the motors connected.**
- *Pros:* no hands.
- *Cons:* different build variant, so no valid baseline exists and `R2-HOST-DETDIFF` is
  `NOT_BUILT` at Visit 1. «#3500»'s post-stop behaviour would be certified only by T0-14b's
  dirtied-pin cell, one cell per base instead of the full matrix.

**Recommendation in the first draft: (a).** **Superseded by the arbiter ruling below.**

**Arbiter ruling (2026-09-13): neither option as drafted. Motors stay plugged in, and the board
stays powered.**

**Why the question could not be settled from the records.** Stephen's answer was *"board will be
powered on when i run the bench... if you need it powered off during a run i can do that but it
will mess with the logs"*. The unplug precondition exists for a stated reason: *"with no motor
connected there is no current path whatever the output stage does"*. The electrical fact behind
it is whether a ~1 ms pulse on one board's W low-side gate input can put current through a
connected motor while that board's other gate inputs are undriven. That fact is not in
`DOCs/analyses/BOARD-REVISION-FACTS.md`, which carries no gate-driver input defaults.

**What actually creates the exposure.** The sweep pulses each group's sense pin (base+4). With
the boards where they are, two groups' sense pins land on a board's W low-side gate input:
- `NO_USE_P24_P39` → P28, the RIGHT board's `pin_pwm_w_l`;
- `P40_P55` → P44, the LEFT board's `pin_pwm_w_l`.

Those two groups are the only exposure. So the binary stops pulsing them (§C.3), and no gate input
is touched at all.

**What remains is ordinary.** Phase 2's driver cogs start at commanded zero in float mode (PWM
disabled), the same condition as every scan start with the motors connected. The P0_P15 cog's
driven pins P8–P13 sit on no board.

**Cost, stated plainly.** Two cells cannot run at Visit 1:
- «#3500»'s check that an overlapping group is not reported as Rev B (the P40_P55 cells);
- the `NO_USE_P24_P39` cells.

Both become the deferred cell `R2-DETECT-OVERLAP`, owed to the first session where the motors are
unplugged for another reason (e.g. around the Rev A swap). It is not re-asked. `R2-HOST-DETDIFF`
at Visit 1 still covers the post-stop poisoning cells: sweeps 4/5 on P0_P15, 7/8 on P16_P31, and
P32_P47. That is exactly the defect «#3500» fixed.

### J.3 · Watchdog self-test: stall with the wheels at rest (task text), or while one turns?

**Context.** The task text says the stall comes "after preflight with wheels stopped". A driver
cog is still running at zero command, and the watchdog's `stop()` of it is what the test proves.

**Option (a) — at rest (as designed in §G).**
- *Pros:* no unattended motion during a deliberate fault of the instrument.
- *Cons:* proves the watchdog stops a live driver cog, not that it stops a turning wheel. The
  call is the same `stop()`, so the difference is the physical observation only.

**Option (b) — stall while one wheel turns at ⅛ ceiling.**
- *Pros:* proves the physical outcome directly, via the tick count after the stop.
- *Cons:* a wheel turns unwatched by cog 0 for ~4.5 s. If the watchdog itself is dead, it turns
  until the 12 s backstop, where cog 0 stops it.

**Arbiter ruling: (a)** for Visit 1, per the task text.
- No unattended motion is added to a deliberate fault of the instrument.
- Revisit if Visit 1's `R11-WDT-STOPPED` ever reads anything surprising.

---

## K · Unverified assumptions, scope findings, and out-of-scope defects

### K.1 UNVERIFIED (not visible in repo source; no p2kb in this dispatch)

1. **VERIFIED (arbiter review 2026-09-13):** `startEx(…, TRUE)` + `holdAtStop(TRUE)` +
   `cogatn(1 << cog)` releases the driver *after* the parameter write lands.
   - `waitatn` (`isp_bldc_motor.spin2:2882`) precedes the first parameter read (`:2913`) and
     `checkstop` (`:2919`).
   - `p2kbPasm2Waitatn`: the attention flag is set by another cog's request and cleared only at
     cog start or by `WAITATN`/`POLLATN`/`JATN`/`JNATN`. A `WAITATN` whose flag is already set
     returns at once.
   - `p2kbSpin2Cogatn`: a strobe with no queue.
   - So a `cogatn` that lands while the driver is still calibrating is not lost, and the brake
     `stop_mode` is read either way.
2. **RESOLVED, and the in-source claim was wrong (2026-09-14).** `checkstop`'s `modz _nz` inverts
   the SM_FLOAT test, so `initAngleFmHall` (which sets `prior_angle`) runs at start only in
   **SM_BRAKE** (§A.5-h). `R13-CHAR-BRAKESTART` is start-path coverage, not a falsifier of
   b34e109.
3. A `res` long's cog-RAM content at `COGINIT` is undefined, so the pre-`b34e109` defect may not
   reproduce (§A.5-h).
4. The calibration's 8-frame hardware sum reduces frame noise by √8, and a telemetry value is one
   frame (§A.5-e threshold derivation).
5. `debug()`'s 255-byte statement limit counts literal text (§B.4). If it does, T0 uses the line
   builder for `SIGNOFF` records.
6. `pnut-term-ts` writes each `debug()` statement as one intact line when two cogs emit
   concurrently. This matters only on the self-test backstop path (§G.3).
7. `tools/gen_bench_char_assets.py` exists (named in `test_bench_char.spin2:183`, not opened), and
   Python 3 is still installed (PL-15, 2026-09-11).
8. The steering object's per-wheel TEST-USE pass-through names (`c22dba1`) and its public drive
   call name (§H.2). Not read.
9. **RESOLVED (arbiter review 2026-09-13):** no public read of `rpm` exists.
   - `rpm` is a `VAR` set only in the private `updateHdmiData()` (`isp_bldc_motor.spin2:1796`).
   - The only RPM-returning `PUB` is `testGetResults()`'s maximum.
   - «#3502»'s task body now requires a TEST-USE getter for the current value, with its
     precondition stated, so `R4-CHAR-RPM` is buildable.
10. «#3505»'s prediction list and «#3504»/«#3521»'s current bodies were not read (no todo-mcp in
    this phase). The list is taken from the dispatch summary and must be copied verbatim into
    `SIGNOFF-DETECT-PREDICTIONS.tsv`.

### K.2 Findings that bear on Batch 1 scope

- **PL-22's failed-start handling is already in the tree.** `isp_steering_2wheel.spin2:120-129`
  returns −1 and stops whatever started, and `:132` builds the mask from real cog ids. Yet the
  plan lists «#3533»'s PL-22 part as not landed. The Visit 1 cells still apply; the arbiter may
  want to reconcile «#3533»'s body.
  - **Reconciled (arbiter review 2026-09-13).** The sense-cog failure path returns −1 too
    (`:152-158`).
  - «#3533»'s PL-22 item is dropped. PUNCH-LIST PL-22, the sprint plan and the plan-state
    analysis are corrected.
  - The steering-object `BENCH_CFG` gap (§K.3 item 5) is filed as PL-33 and added to «#3533».
  - The `BS-ZERO` mislabel (§K.3 item 3) is filed as PL-34 and fixed by §F.6.
- **The published status block has no loop-progress counter**, and `loop_ticks`/`loop_ctcks` have
  no getter. Row 12 therefore uses the ready + not-frozen proxy (§A.5-g) rather than a counter.

### K.3 Out-of-scope defects noticed (not fixed)

1. `src/test_bench_scan.spin2:4031-4032`: `reasonToken()`'s `other:` returns `ABORT_I`, so an
   unlisted `AR_*` would print as a current abort.
2. `src/test_bench_scan.spin2:3897-3898`: `phaseToken()`'s `other:` returns `ZERO_INIT`, so any
   future phase silently mislabels. F.3 must add a case.
3. `src/test_bench_scan.spin2:1157`: `emitZero()` is passed `bZeroOk[slotIdx]` for every phase,
   so a point's `BS-ZERO health_ok` reports the motor block's `ZERO_INIT` verdict, not its own
   reading.
4. `src/test_bench_t0.spin2:370`: `if spacerCogId == -1` misses the `$8000_xxxx` exhaustion form
   the library documents (`src/isp_bldc_motor.spin2:110`). The spacer count and `cogstop` loop
   would then act on a negative id. Its header comment `:350-353` still describes the
   pre-«#3499» "start() adds one" contract.
5. `src/isp_steering_2wheel.spin2:90`: `user : "isp_bldc_motor_userconfig"` has no
   `#ifdef BENCH_CFG` switch, whereas `src/isp_bldc_motor.spin2:61-65` does. Under
   `-D BENCH_CFG`, the steering object reads the user config (e.g. `WHEEL_DIA_IN_INCH`) while its
   wheels read the bench config.
6. `src/isp_bldc_motor.spin2:1719`: `hallWindowSum += hallCntsIn8thSec` adds a `VAR` that is never
   updated instead of the local `nHallCntsIn8thSec`. This is the known rpm defect, in «#3502»'s
   scope.
7. `DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:20`: the baseline's `BD-CFG left_base,0`
   disagrees with the measured left board at P32 (`src/test_bench_char.spin2:110`). It is handled
   in §C.2 by excluding `BD-CFG`/`BD-MAP` from the verdict.
8. `tools/bench-run.sh:167`: the comment says CLK_FREQ is patched "in test_bench_t0.spin2", but
   the code patches whichever `$BENCH_FILE` the tier selected.
9. `src/test_bench_t0.spin2:36-37`: says output is consumed by `tools/bench-verdict.py`, which
   does not exist (read attempt: file absent).
10. Already on the punch list, noted only for completeness: PL-23 at `test_bench_char.spin2:435`
    and `isp_bldc_motor.spin2:1104-1111`; PL-28 at `isp_bldc_motor.spin2:1114-1134`.
