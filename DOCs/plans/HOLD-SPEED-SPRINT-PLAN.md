# 6.1.0 — Hold Speed Under Load — sprint plan

**Status:** STARTED 2026-10-01 (§14 records the entry checks).
**Release:** 6.1.0. The version is settled; the ship call is Stephen's (doctrine overlay P5).
**Baseline at planning:** tree `54c4a1e` + the planning edits; `DRIVER_REV 46` (`src/isp_bldc_motor.spin2:6796`);
`test_bench_dual` SRC_REV 70 (`:794`); gates: see §13.

---

## 0. What this sprint is for

**Goal.** Ship a driver that holds its commanded speed under load with torque, up to the current limit, and gives way
only at the limit (PL-167, the v6.0.0 Known Issue "spins in place can run up to 43 % slow"). Certify it wheels up and
on the floor. Correct the floor tests' wrong premises before they run again, and land the release.

**Done means:** every section below is built and gated; the one bench visit (§9) has run and its evaluation records
each cell's verdict; the 6.1.0 CHANGELOG entry is voiced to `central:changelog-voicing`; Stephen tags.

**Scope, in Stephen's words (2026-10-01):** option (a) — the PL-167 fix, PL-168's premises, `DRIVER_BOARDS.md`, PL-67's
compile-time refusal, the release, with PL-132's coast cell, PL-160's quarter-speed start and PL-169's deadband riding
along — and then *"pull in any bench harness work that directly relates to tests we will run during this plans effort,
pull in the simple changes/fixes"*. The punch list's **"The register for 6.1.0"** groups every open entry; this plan
carries the three "In 6.1.0" groups and nothing else.

**How the work runs (standing, carried from 6.0.0):** P10 — a known defect is root-caused and designed out at the desk,
never re-measured; P5 — any new driver function goes to Stephen with a measure of benefit before it is built; the gate
runs once per complete batch (overlay P10); the bench is a separate machine fed by the pack (`tools/make-bench-pack.sh`),
and Stephen runs every tier; every hand-back ends `BENCH: READY -- <commit, commands>` or `BENCH: NOT READY -- <what
remains>` (overlay P1).

### 0.1 Standing rulings that bear on this scope

| Ruling | Words and date | Where it binds |
|---|---|---|
| PL-167 is fixed in 6.1.0, 6.0.0 ships it as a Known Issue | *"ok yes, A lets get 6.0.0 to release first then we'll follow with this new effort"* (2026-10-01) | §1 |
| D-4 (`LAG_HOLD` 86) conditional on a desk check | *"(a), conditional"* (2026-10-01); the condition FAILED, so `LAG_HOLD` stays 100 (design §7 Q1) | §1 |
| Phase 2 proceeds with the slow/medium depth unproven; a second mechanism stops it | Q3 *"ok A"* (2026-10-01) | §1, §3 (SPINRATE) |
| How the drive "says so": the existing events, documented | Q4 (a), reviewer's design-internal call (design §7) | §1.4 |
| A test built on a wrong premise is corrected before it runs again | *"if we deem a test needing to be run again and it's build on wrong premise we should correct that before running again, right?"* (2026-10-01) | §3 |
| Overlapping pin groups are refused at compile time | *"it can be produced and should be failed at compile time."* (2026-10-01) | §7 |
| The bench log names its commit, by the pack builder | *"re pl68 yes A"* (2026-10-01) | §5 |
| `DRIVER_BOARDS.md` | *"we need somthing for the boards too which are just facts for each... This is not to facilitate choice but to inform a user about the boards they have and when to be careful with each"* (2026-09-16); 6.1.0: *"yes do this"* (2026-10-01) | §8 |
| The floor runs are hands-off sessions, untethered, one command per physical setup | R9, R15, R20 (2026-09-30) | §3, §9 |
| Fault returns use the guarded `testForceFault()` | *"fp1: A"* (2026-09-28) | §9 |
| The v6.0.0 CHANGELOG stays as published; 6.1.0 carries the corrected figure if the issue remains | *"it's published so C"* (2026-10-01) | §10 |
| Serial, DocoEng, the clock range, a "following" getter and the inertia term are out | 2026-09-27 / 2026-09-28 rulings (punch list "Deferred by Stephen's rulings") | not in this plan |

### 0.2 Order

The fronts (overlay P12) advance together. The driver front is unblocked from the first day (§1.1 is desk work).

1. §6 simple fixes, §7 PL-67, §4 the token self-check, §5 the commit in the log — independent, any order.
2. §1.1 the desk design of D-5 → Stephen rules on its measure of benefit (the one owner decision this plan schedules).
3. §1.2 build → §2 wheels-up cells → §3 floor premises and cells (one batch, one gate).
4. §8 `DRIVER_BOARDS.md` — any time.
5. §9 the visit: pack, run sheet, `BENCH: READY`.
6. §10 the release: documentation, CHANGELOG, `VERSION`; Stephen tags.

**Bench visits remaining to the release: one** (§9), unless its evaluation finds a defect whose fix needs a run.

### 0.3 Established decisions for dispatch — regenerated

The `sprint_established_decisions` context key is stale (it carries the 6.0.0 ABI counts 17 / 16). Before any dispatch,
`plan-to-tasks` rewrites it from this section and the conventions file. What changes:
- **ABI (item 6):** the status run is `DRVR_STATUS_LONGS_COUNT` = 24 (`drive_u` … `drv_stop_fp`, `fault` after it), the
  params run `DRVR_PARAMS_LONGS_COUNT` = 27 (`offset_fwd` … `sense_zero`), at `src/isp_bldc_motor.spin2:6776-6783`;
  `isAbiLayoutValid()` checks both counts and the three status indexes (`:5300`). This plan changes neither run.
- **Dispatch shape (retrospective #7, #14):** split multi-part builds before sending; check a dispatch's changed-file list
  against its allowed set before trusting its report.
- Items 1-5 and 7-24 carry as written.

---

## 1. PL-167 — hold speed under load (driver)

**Why.** Spinning a 7.7 kg platform in place, the shipped lead schedule ran at 57-94 % of command with the lag at the
hold, the duty swinging and the path limiter trimming, at 0.05-0.14 A — far from any limit
(`DOCs/analyses/bench/2026-09-30/floor2/FLOOR-RERUN-EVALUATION.md` §2.1, N5). The cause, the design, its benefit and its
certification are in `DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md` (approved; phase 2 desk steps recorded there). This
section builds it.

**Starting point (DRIVER_REV 46, citations re-checked 2026-10-01):** `SERVO_ACC_SHIFT = 14` (`:7039`), `LAG_SOFT = 80`
(`:7028`), `LAG_HOLD = 100` (`:7029`); the frame trim `.servoTrim` (`:7986`); `passEnd` (`:8701`), `feedForward`
(`:8706`), `holdDecay` (`:8716`); `BLOCKED_PASSES = 1_000` (`:7245`) and `bFrontProtect()` (`:2864-2904`).

### 1.1 Desk first: design out the early-load regression (D-5) — then Stephen decides

**The regression (MODELLED, reproduced 2026-10-01).** Under D-1..D-3, a 4 N·m load held from 1.0 s to 2.0 s on a straight
drive at power 13 stalls the loaded wheel at its 27 A limit; over the 1.5 s after release the platform runs **40.4 /
41.0 %** of command, against **83.9 / 82.9 %** today (`python3 DOCs/plans/servo-model/spin2_model.py release
acc_shift=16 dB=1 boost_shift=10 dC=1`, against the same command without the design flags).

**Its mechanism, from the trace** (`spin2_model.py rtrace acc_shift=16 dB=1 boost_shift=10 dC=1`):
1. D-2 lifts the duty to the limit within ~60 ms of the load (duty 5,398 → 16,351, phase 27 A).
2. The field is held at `LAG_HOLD` 100, which sits 25-85° past the torque peak (design §3.5, PL-105), so 27 A buys about
   half the torque it could; the wheel stalls.
3. D-3 correctly lets the field give way at the limit — but the limit never releases at a stall, so `holdDecay` walks
   `drv_incr` to zero.
4. The steering path limiter scales both wheels to the stalled one's fraction (66 ‰); after release it climbs back 20 ‰
   per 8 ms slot (`isp_steering_2wheel.spin2:2787-2800`), and the field re-accelerates on the ramp.

**The lever is where the held field sits once a limiter has the duty.** A fixed lower hold was ruled out (D-4: a backward
tick from a lag of 82.3-88.3 wraps the 8-bit error past the 125 fault test). A field that retreats toward the torque
peak only while a limiter has the duty avoids that window, but changes what `bFrontProtect()` sees (it counts only
`|err| ≥ LAG_SOFT` with no tick), so the blocked-wheel stop must keep latching on a wheel stopped at its limit.

**Deliverable (task-design, phase 1 of 2: the design only, no driver code):** a D-5 section added to the design document:
- the mechanism, its invariant, and why it cannot reach the 82.3-88.3 fault window;
- what the blocked-wheel stop counts under it, so a wheel stopped at its limit still latches (BLKSTOP, BLKLIMIT stay
  meaningful);
- **its measure of benefit for Stephen** (P5), each row marked MODELLED / DERIVED / UNKNOWN: the release case; every row
  of design §5 re-run (no row may get worse); the `block` grid of design §7 Q1 at `LAG_HOLD` 100 (solid and rocking);
  the cost in cog/LUT longs and clocks per frame;
- **acceptance at the desk:** the release case ≥ today's 83.9 / 82.9 %; `design` legs still clean at the central, refit
  and adverse parameter sets; the `block` grid no worse than D-1..D-3's (latched / rocked / faulted per obstacle).

**Then Stephen decides**, from that table, between: building D-1..D-3 with D-5; building D-1..D-3 alone with the
regression carried (and stated as a Known Issue candidate); or another option the table shows. If no D-5 candidate
meets the acceptance, the table says so and the choice is the same minus the first option. Nothing in §1.2 is built
before his ruling.

### 1.2 Build

- **D-1:** `SERVO_ACC_SHIFT` 14 → 16 (a value in the params run; no ABI move).
- **D-2:** the fast slope past `LAG_SOFT` in the frame trim, in the LUT run image via one `CALL` (design §4.2, §4.4).
- **D-3:** `holdDecay` walks the field down only when `duty_capped_ + foldback_cnt_` changed since the previous pass
  (`lim_seen`, snapshotted in `passEnd`).
- **D-5:** as ruled in §1.1.
- `DRIVER_REV` 46 → 47 with its line in the revision comment.
- **Costs counted from the compiler**, not the sketch: cog and LUT `fit` lines updated; `tools/pasm_equiv` frame budget
  (fails any window over 75 % of the 160 MHz frame) and new scenarios at `duty_max` proving the accumulator range at
  shift 16 (design §4.4).
- **Conformance:** `central:spin2-authoring-guide` (gate) over every line touched; `tools/check_style.sh` with the batch.

**Verify.**
- *Normal:* the desk model and `pasm_equiv` agree with the built image (equivalence outside the changed routines);
  `isAbiLayoutValid()` unchanged; both gates green.
- *Edge:* the accumulator at `duty_max` with D-2's largest add; D-3 on a pass where only `duty_capped_` advanced; a
  reversal through zero with D-2 active.
- *Error:* the fault test unchanged at 125; no lag fault in the modelled load steps with D-2 present (design R5).
- Run-time certification is §2 (wheels up) and §3 (floor).

### 1.3 Rev A

Rev A resolves the fold-back 30× coarser (design R7), so D-3's "at the limit" may come later there. This sprint does not
certify Rev A (no Rev A run is planned). §10's release note states the validated board, as v6.0.0's did; whether that is
a Known Issue line is Stephen's ruling at release (P5), from §9's evidence.

### 1.4 What the user sees — the events' meaning (Q4 (a))

After D-3 every give-way coincides with a limiter count, so `EV_FOLDBACK` (and the duty ceiling) means "a wheel at its
limit" and `EV_PATH_LIMIT` "both wheels slowed together because one is at its limit". `DRIVE-OBJECTS.md` (the events and
`getEvent()` rows) and `DRIVER-THEORY-OF-OPERATIONS.md` §7 say so; §10 lists them.

---

## 2. Wheels-up verdicts for the fix (harness for this plan's runs)

**Why.** The design's wheels-up certification (§6 there: Visit 8's A-1, A-2, A-3, A-5) has been judged so far by
reading logs with `DOCs/plans/servo-model/start_metrics.py` and `rungs.py`. Established decision 19 requires a new
mechanism's test to print its verdict in the log.

**Starting point:** `dual-a` (`tools/bench-run.sh:349-351`, `-D DUAL_PART_A`: PREFLT, STOPMODE, LIVE, LADDER) prints
`BM-RUNG2` with `duty_pk`, `err_pk` and current per rung; `dual-limits` (`:592-599`, PART_LIMITS) commands
`LIMTOP_MAX_INCRE` with the current limits lowered to 1 A (PL-98 (3)), so the fold-back has the duty with the wheels up
(a no-regression run for the fix, not a discriminating one: see LIMGIVE below).

**Target.** In `src/test_bench_dual.spin2`, cells printed in the log, each with a negative that fails on today's image:
- **A-3 on the ladder:** duty swing ≤ 400 and `err_pk` ≤ 76 at rungs 1-2. *Negative:* today's gain read `err_pk` 76-86
  (Visit 8, `VISIT-8-EVALUATION.md` §3.2).
- **A-5 on the ladder:** rungs 3-8 duty and net current within ±5 % of the DRIVER_REV 46 reference, the reference values
  stated at their constant with the log they came from. *Negative:* a placement change (the legacy pair, `dual-a-legacy`)
  moves current 15-26×.
- A-1 and A-2 stay as the floor's SPINSTRT / SPINPEAK (§3) and the START trace.
- **LIMGIVE (I-2) is judged on the floor only (§3).** Wheels up, the only way to make the field give way is a capped
  over-command (`dual-limits`), and there a limiter has the duty on today's image too, so the cell would pass on the
  unfixed path (D2: a cell that cannot fail is not built). Its negative is the floor2 logs: decays with no limiter
  count.

**Verify.** Each cell's derivation at its constant; each fails on the unfixed path (the DRIVER_REV 46 logs on disk, or
the `-D` image of today); worst-case record bytes under 280 (decision 17); the DEBUG footprint under the tier cap
(`bench-run.sh:813`).

---

## 3. The floor run, corrected (PL-168, PL-132, PL-160, and the design's new cells)

**Why.** Five premises of the floor tests were proved wrong by the 2026-09-30 runs (PL-168), and the design adds cells
that certify the fix (design §6). A test is corrected before it runs again (Stephen, 2026-10-01).

**Starting point** (all `src/test_bench_dual.spin2`, read 2026-10-01):

| Item | Today | Correction |
|---|---|---|
| (1) Coast no-latch bound | `BLK_STAND_HI_MS` = `BLK_LATCH_MIN_MS` + `BLK_LAG_MS` + stamp (1,168), `BLK_NOLATCH_MS` 1,180 (`:15952-15967`); `BLK_LAG_MS` assumes the tick leaves the lag at −`LAG_HOLD` (comment `:15921-15935`) | Re-derived from the driver's own rule (`bFrontProtect()` `:2899`: the count runs only while `|err| ≥ LAG_SOFT` with no tick, and any tick or dip restarts it): the bound starts when the lag last crossed `LAG_SOFT` after the last tick, which the harness reads from its own `BM-TS` samples, not from the last tick |
| (2) SPINCTL | legacy over schedule mean current at medium ≥ 1.25 (`spinOverRatio`, `:18449-18469`, `SPINCTL_LO` `:15727`), with no speed check | Judged only when both legs read `fol` ≥ 97 %, else NOMEAS with its reason (design §6) |
| (3) Obstacle RESULT | `resultObstacle()` (`:21037-21056`) reads the session accumulators `sfBlkN` / `sfBlkBad` / `sfClrBad` | Each trial's RESULT from its own `bBad` (already computed per trial in `blockFold()`, `:20431-20444`) |
| (4) Quarter-speed window | one platform turn per leg (`SPIN_LEG_DEG` 360, `:15603`); BRISK window 300 ms (`spinWinMs`, `:16289-16291`); A-2 needs 420 + 60 ms at speed (`A2_REF_DELAY_MS`, `:15712`) | Two turns at the quarter (R20: untethered), with the window and SPINSTRT / SPINPEAK / SPINLEAD re-derived at their constants |
| (5) Labels | `WHY_STEADY_TIMEOUT` for any leg not sustaining AT_SPEED (`emitSpinW()` `:18734-18736`); `WHY_JUDGED_ACROSS_RUNS` printed inside a session (`emitAcrossRuns()` `:18792-18815`) | A label that says what happened; a session that holds the pair judges it |
| (6) Tether | `:253, :841, :15534, :15537, :15568, :15570, :16155, :17146`; `tools/bench-run.sh:231-232, :236`; `tools/gen_dual_assets.py:320, :360, :413` | Every reference removed; the one-turn rule's reason re-stated (R20) |

**New and re-premised cells (design §6),** each with the floor2 logs as its negative:
SPINRATE (every leg ≥ 97 %), SPINHOLD (no held pass, no `EV_PATH_LIMIT` in any spin leg), LIMGIVE (I-2: every slot whose field falls below 98 % of the command while held has `foldback_cnt` or `duty_capped`
advanced within its last 4 slots),
RAMPARR (arrival within 10 % of prediction on the four ramp legs, no `EV_PATH_LIMIT`), SPINCTL (re-premised, (2)),
BLKLIMIT (on the solid-object trial `EV_FOLDBACK` engages before the protective stop latches, the latch in 988-1,168 ms).
**Kept:** SPINHUNT, SPINERR, SPINFOL, SPINSYM (now judged at equal speed), SPINLEAD, SPINSTOP, SPINOFF, LAGBND, POSTFLT,
SPINPLAT, BLKSTOP, PROTCLR, BLKSHORT, BLKCOAST (PL-132), LDPATH / LDHUNT / LDHOLD.
- **The grab cells' premise holds as built.** Design R8 assumed the grab ran at the 27 A default; `floor-grab` lowers both
  limits to `LOAD_LIMIT_A` first (`:16000-16060`), so a hand still pulls past the limit after the fix.
- **If D-5 changes what the blocked stop counts (§1.1),** BLKSTOP's and the coast bound's derivations follow it in the
  same change.

**Cell map (overlay rule, a test that is reshaped keeps every cell):** every cell the 2026-09-30 `floor-auto` and
`floor-obstacle` sessions judged is listed above as kept, re-premised or new; none is dropped. The task writes the map
into its record, tier by tier.

**Verify.** Every corrected constant states its derivation and can fail; the 2026-09-30 logs, re-read against the new
criteria by arithmetic, fail SPINRATE / SPINHOLD / LIMGIVE / RAMPARR and read SPINCTL NOMEAS; all floor tiers compile
under `-D BENCH_CFG`; the DEBUG footprint stays under its cap; one gate with the §1-§2 batch.

---

## 4. A record label can never misdescribe itself silently (PL-96, PL-97)

**Why.** A token longer than its field prints `?`, and a table shorter than its enum walks into adjacent DAT — four
instances so far, the last fixed at SRC_REV 70 (`START_I_OVER_STEADY_X100`, 24 > 18). Nothing checks either.

**Starting point.** Only `test_bench_dual.spin2` has enum-indexed tables (survey 2026-10-01: about 80 tables, each with
its count constant; all match today). `tokenAt()` (`:25876-25895`) bounds by the caller's count, never the table's
length; `tokenField()` / `bTokenFits()` (`src/isp_bench_log.spin2:121-131, :274-287`). **Half the counts are literals**
(`SEG_COUNT = 34` `:2117`, `WHY_COUNT = 52` `:2130`, and others), so a check against them passes after an enum grows.

**Target, correct by construction.**
1. Every count constant derived from its enum's last member + 1, so the count cannot lag the enum.
2. A start-up self-check over every table compiled into the build: each table ends with a sentinel, the walker counts
   entries to it and compares with the count, and checks every entry against its field's `TOKMAX_*`; one record and one
   cell with its verdict. `#ifdef`-guarded tables are checked under the same guards.
3. The `sSfCell*` / `sSfCrit*` strings checked against `TOKMAX_CELL` / `TOKMAX_CRIT` in the same pass.

**Verify.** *Negative:* a scratch copy of the harness with one table entry removed and one token made over-long must
FAIL the cell. There is no P2 at the desk, so that copy is compiled here and its first run is a tier on the visit's pack
alongside the real one (the cost is one extra unattended load, a few seconds). The footprint stays under its cap.

---

## 5. Every bench log names its commit (PL-68)

**Ruled (Stephen, 2026-10-01, "yes A").**
- `tools/make-bench-pack.sh` already compiles inside a temporary `git archive` copy (`:46-55`). In that copy, before
  compiling, it writes a small object holding the commit (short SHA as a constant). The command is echoed.
- A tracked default of that object reads "not a pack", so a build straight from the tree says so.
- Every harness banner prints the field (`test_bench_dual` `:26095`, `test_bench_t0` `:1596-1608`, and the others with
  banners).
- `tools/bench-run.sh` echoes `git rev-parse HEAD` and whether the tree is clean before any source-tree compile
  (`:778`); package mode already echoes `BENCH-PACKAGE` (`:688`).

**Verify.** A pack built from a commit prints that SHA in every banner; a source-tree build prints "not a pack"; the
tracked default is never modified in the tree (`git status` clean after a pack build).

---

## 6. Simple fixes

| Entry | Change | Verify |
|---|---|---|
| PL-12 | `check_pri_docs()` (`tools/check_style.sh:532-553`) treats a line as a doc line only when its `code` is blank — both the `''` branch (`:544`) and the `'` branch (`:548`), as `check_pub_docs` does (`:444`) | A PRI body line `x := 1  ''` added to `fixtures/style/conformant.spin2` passes; `C4.spin2` still fires |
| PL-172 | `tools/fixtures/style/T128.spin2` | `tools/check_style.sh --self-test` exits 0 |
| PL-23 | TRUE / FALSE printed, never a number: `test_bench_spin.spin2:125, :177`; `test_bench_t0.spin2:2822` (`rev_b`) and `:6517` (the T0-24 try booleans; `measured` is tri-state and gets its own tokens); `testGetResults()`'s `bDidFault` returns TRUE / FALSE as `testGetTelemetry()` does (`isp_bldc_motor.spin2:2354` vs `:2416`); the class swept across `src/` | Every site prints a word; callers that branch on `bDidFault` unchanged in behaviour |
| PL-37 | Delete `src/bc_bg.bmp`, `bc_caption.bmp`, `bc_digits.bmp`, `bc_labels.bmp`, `bc_button.bmp` and `tools/gen_bench_char_assets.py`; move its `fit()` note (`:104-110`) into the generators that cite it (`gen_t0hand_assets.py:6, :98-99`, `gen_dual_assets.py:479-480`) and re-point `test_bench_t0.spin2:6036` | Nothing loads them (checked 2026-10-01: no `FILE`, no DEBUG asset name, no packaging glob); `make-bench-pack.sh` builds; build-check green |
| PL-169 | A deadband on the VRA and VRB readings in `demo_dual_motor_rc.spin2` (`:187-191`, `:227-241`) and `_rc_hdmi` (`:204-208`, `:244-258`): the setter is called only when the mapped rate moves by more than the knob's noise (±2 counts ≈ ±4 mm/s²) | The knob's full range still reaches both ends (200 / 3,000 and 1,000 / 3,000 mm/s²); no re-send on a still knob (desk arithmetic; Stephen's next FlySky drive confirms) |

---

## 7. Overlapping or illegal pin groups are refused at compile time (PL-67)

**Why.** Ruled 2026-10-01: *"it can be produced and should be failed at compile time."*

**Facts (research 2026-10-01).**
- The preprocessor cannot compare numbers (p2kb `p2kbSpin2PreprocessorOverview`: no `#IF`, no expression evaluation).
- A CON constant that divides by zero is refused by pnut-ts with `<file>:<line>:error:Divide by zero (m145)` and a
  non-zero exit; clear bases compile (prototyped in scratch, bases 16/32 compile, 24/32 and 32/32 refuse).
- **Legal enums alone do not prevent an overlap:** the base pins are 0, 8, 16, 32, 40 (`isp_bldc_motor_userconfig.spin2:31`)
  and a board uses 16 pins, so 0/8, 8/16 and 32/40 share pins, and equal bases are one group.
- At run time `start()` already refuses both: an illegal base (`ERR_BAD_PIN_GROUP`, `isp_bldc_motor.spin2:4107`) and a
  group another instance holds (`ERR_PIN_GROUP_IN_USE`, `:4122-4125`). Those stay.

**Target.**
- `isp_bldc_motor_userconfig.spin2`, in the `CFG_DUAL_MOTOR` block (`:161-176`): two constants, each a division whose
  divisor is 1 when the rule holds and 0 when it does not, each line carrying a comment that tells the user what is wrong
  and how to fix it — (i) each base is one of the five legal groups; (ii) `|LEFT_MOTOR_BASE − RIGHT_MOTOR_BASE| ≥ 16`.
- In the `CFG_SINGLE_MOTOR` block (`:147-159`): (i) only, on `ONLY_MOTOR_BASE`.
- `isp_bldc_motor_userconfig_bench.spin2` (`:63-64`): (i) and (ii).
- `tools/build-check.sh` proves each refusal flips, as it proves the no-CFG refusal (`:205-214`): it compiles a temporary
  copy of the config with an overlapping pair, an equal pair and an illegal base, and requires a non-zero exit at the
  check's line; the shipped configs compile. It edits no source file.
- DEVELOP.md's configuration section says what the refusal looks like.

**Verify.** *Normal:* every shipped config and the bench config compile. *Error:* overlap (16/24), equal (32/32) and
illegal (24, `PINS_NO_USE_P24_P39`) each refused in the gate's scratch copy; the gate fails if any is accepted.
*Edge:* adjacent groups (16/32) and the bench's swapped pair (32/16) compile. Step 3b's placement rule for PNut-TS
directives is unaffected (the check is plain CON, legal in PNut too).

---

## 8. `DRIVER_BOARDS.md` — the boards a user has, and when to be careful

**Why.** Stephen, 2026-09-16 (quoted in §0.1); in 6.1.0 by his 2026-10-01 disposition.

**Target.** A repo-root page, one section per board revision, in the user register (doctrine overlay P8: no visits,
cells, PL or task ids; current state only). Contents (the 2026-09-16 spec, `plans/archive/BENCH-READINESS-SPRINT-PLAN.md`
§ "Repo-root reference docs"):
- how to tell which revision you have, and what `getBoardType()` reports (and `BRD_AUTO_DET` / `BRD_REV_A` / `BRD_REV_B`);
- gate supply (Rev A 10 V, Rev B 12 V from a boost regulator on the accessory header's 3.3 V);
- gate driver (MIC4604 / UCC27211D), MOSFET (MCAC85N06Y: 60 V, 54 A at 100 °C, 4.5 mΩ);
- current-sense scale and resolution (5 mV/A against 150 mV/A);
- deadtime (250 ns minimum on both; the driver uses 260 ns);
- what the driver protects against and what it does not (the fold-back, the protective stop; phase-short braking is not
  current-limited; regeneration is not visible to the current sense);
- when to be careful: Rev A's damage history with large hub motors and its lack of Rev B's negative-spike protection
  (Stephen, 2026-09-16, `BOARD-REVISION-FACTS.md` §1.4, §2), and Rev A's coarse current sense.

**Source:** `DOCs/analyses/BOARD-REVISION-FACTS.md` (vendor manuals, verbatim in its Part 1), distilled; no
recommendation to buy one board over the other. Linked from `README.md`'s document list and from `CLAUDE.md`'s
documentation table (overlay P3: `CLAUDE.md` is kept current, never asked).

**Verify.** Every fact traces to `BOARD-REVISION-FACTS.md`'s Part 1 or to Stephen's words; the P8 register check (no
id, no history); `tools/doc-audit.sh` clean.

---

## 9. The bench visit — one, wheels up then the floor, the same day

**Earned by:** §1.2, §2, §3, §4, §5 landed and gated. **Carries:** everything those sections built (overlay P10: nothing
known and fixable stays unbuilt when the sheet goes out).

**What must be shown, and under what conditions (overlay P1 — Stephen says how):**
- *Wheels up, Rev B platform:* `dual-a` (A-3, A-5 on the new image) and `dual-limits` (its existing cells: no regression
  at a capped over-command). Unattended.
- *On the floor, Rev B platform, untethered:* `floor-auto` (the ten spins, the fault run, the four ramp legs —
  SPINRATE, SPINHOLD, LIMGIVE, RAMPARR, SPINCTL, the kept cells, the two-turn quarter); `floor-obstacle` (coast and brake
  trials — BLKCOAST, BLKSHORT, BLKSTOP, BLKLIMIT, PROTCLR, the per-trial RESULTs); `floor-grab` (LDPATH, LDHUNT, LDHOLD
  under the fix); `floor-rc` (Stephen's FlySky drive: the knobs' deadband, and whether speed-ups now arrive).
- The pack (`tools/make-bench-pack.sh`) carries those tiers; its banners carry the commit (§5).
- The run sheet declares the seven attributes for each command, one command per physical setup (R15), and the
  `BENCH: READY` line names the commit and says PUSH FIRST if `main` is ahead.

**Evaluation.** One analysis report from the logs (no tooling), each cell's verdict, and a disposition for every
finding. A finding that needs a fix and a run is the only way a second visit is added, and its count is stated then.

---

## 10. Documentation and the 6.1.0 release

**Release mechanics (as built):** `VERSION` → `6.1.0`; a `## v6.1.0 (<date>)` CHANGELOG entry voiced to
`central:changelog-voicing` (gate: released mode §4.1, length §4.7, exclusions §4.2, read against its own Known
Issues); `tools/make-release.sh v6.1.0 --preview` before the tag; Stephen pushes the tag, the workflow opens a DRAFT with
the three archive sets, and he publishes. The archive sets' file lists come from each top's OBJ closure
(`tools/release_closure.py`), so §8's page and the deletions in §6 change no packaging list.

**Known Issues.** What ships as a Known Issue is Stephen's (P5). The plan brings him, from §9's evidence, each v6.0.0
Known Issue this sprint touches — the "spins in place ... 43 % slow" line (PL-167), "speed changes arrive late"
(RAMPARR), "less torque in reserve near top speed" — with what a user would now experience, and the D-5 outcome of §1.1.

---

## Documentation Blast Radius

`tools/doc-audit.sh`, run 2026-10-01 at planning: **no ORPHAN, no DUPLICATE, no COUNT findings** (23 documents, 51
Spin2 sources). Composed by behaviour changed:

| Behaviour changed | Artifacts that describe it |
|---|---|
| Speed held under load; the field gives way only at the limit (§1) | `CHANGELOG.md` (6.1.0 entry; v6.0.0 stays as published); `MOTOR-6.5IN-TECHNICAL-MANUAL.md` §6.5 / §9 (`:851-852`: "designed and planned for the release after v6.0.0") and its sources page `DOCs/analyses/MOTOR-6.5IN-MANUAL-SOURCES.md` (a bench pass that changes a number updates both); `DRIVER-THEORY-OF-OPERATIONS.md` §7 and the servo description; `DRIVER-6.0-REWORK.md` (`:55-58`, "a wheel that can't keep up slows both" — true of 6.0; the page links the Known Issues, so it gains a pointer to 6.1.0 only if Stephen wants it); `README.md` "Current status" (`:45-51`, "New in v6.0.0") |
| Events mean "a wheel at its limit" (§1.4) | `DRIVE-OBJECTS.md` (event and `getEvent()` rows); `DRIVER-THEORY-OF-OPERATIONS.md` §7 |
| `SERVO_ACC_SHIFT`, `DRIVER_REV` 47, cog/LUT counts | the source's own `fit` and revision comments; `CLAUDE.md` if it cites a count (it cites the ABI runs only, unchanged) |
| Compile-time pin refusal (§7) | `DEVELOP.md` (configuration section); `isp_bldc_motor_userconfig.spin2` section (2) comments; `README.md` if it describes configuration errors |
| `testGetResults()` returns TRUE / FALSE (§6, PL-23) | its `''` doc comment (`isp_bldc_motor.spin2:2349`, already says T/F); `isp_steering_2wheel.spin2:1683, :1693` wrappers' docs |
| FlySky deadband (§6, PL-169) | the two RC demos' header comments; `README.md` demo table if it describes the knobs |
| `DRIVER_BOARDS.md` (§8) | new page; `README.md` document list; `CLAUDE.md` documentation table |
| Bench harness, runner, pack (§2-§5) | not user-facing; their own headers and revision lines; the run sheet |
| Style gate (§6, PL-12 / PL-172) | `tools/check_style.sh` header; `.claude/skill-conventions.md` if it lists the checks (it does not) |

**Counts:** none of the user pages asserts a count this sprint changes (doc-audit COUNT clean). **Duplication:** the
Known Issues live only in `CHANGELOG.md`; README points to it — keep it that way.

---

## 11. Named unknowns

| Unknown | Response when it resolves |
|---|---|
| Whether a D-5 exists that meets §1.1's acceptance | §1.1's table goes to Stephen either way; he rules before §1.2 |
| The slow/medium speed loss's full depth (design §3.6: the model reproduces the oscillation, not 57-94 %) | SPINRATE catches a residual on the floor; a residual is root-caused at the desk (P10), not re-measured |
| Platform yaw inertia and winding inductance (unmeasured; the design is clean across their brackets) | The floor's SPINHUNT / SPINRATE are the certification; no measurement is planned for them |
| Rev A under D-3 (design R7) | Not certified this sprint; stated at release (§1.3) |
| Whether PNut (not PNut-TS) refuses a CON divide-by-zero the same way | Constant folding is the same compiler lineage; DEVELOP.md's PNut guidance says the refusal is by error at that line. If a PNut user reports otherwise, the run-time refusals still stop the start |
| The obstacle's real stiffness (design §7 Q1, unmeasured) | BLKLIMIT and the latch-time comparison judge on the floor |

## 12. Not in this plan (declined visibly for 6.1.0)

Every other open punch-list entry, by its group in "The register for 6.1.0": fixed-in-tree awaiting their binaries
(PL-20, 21, 44, 53, 64, 65, 134), the dormant scan (PL-46, 98), the deferrals by ruling (serial, DocoEng, PL-102, 164,
165, 166), the Known Issue PL-118, the watches (PL-43, 120, 126, 136, 139, 171) and the ancillary entries (PL-60, 63,
103, 105, 108, 109, 110, 119, 135, 170). The paused «#3640» resumes as §1; «#3636» and «#3641» are superseded by §1 and
§3 when `plan-to-tasks` runs.

## 13. Exit gate (`sprint-plan` §5)

1. **Standing rulings:** §0.1, searched across memory, the doctrine overlay, the punch list, the design and the closeouts.
2. **Intent:** §0 (goal, done, how it runs) — Stephen's scope words quoted.
3. **Decisions and open items:** PL-68 and PL-67's shape ruled 2026-10-01; the one scheduled decision is §1.1's, after
   its desk work; every punch-list entry has a group (§12).
4. **Premises measured:** the regression reproduced (`spin2_model.py release`, `rtrace`); the compile-time refusal
   prototyped; the grab's limit read from source; the style self-test's failure run (`--self-test`, exit 1); the
   design's citations re-read at DRIVER_REV 46. Rig facts used: untethered floor (R20), one platform per board revision,
   the pack as the bench's input — all in `.claude/skill-conventions.md`.
5. **Research:** the PL-23 class swept across `src/`; the token-table class across every bench file; the PL-67 overlap
   class across every config; `tools/doc-audit.sh` run; baseline gates: `tools/build-check.sh` and
   `tools/check_style.sh` run at planning (result recorded below).
6. **Named unknowns:** §11.

**Baseline at planning (2026-10-01, tree `54c4a1e`):** `tools/build-check.sh` PASS — 50/50 tops, both release demos
certified, all 60 bench tiers within the DEBUG footprint; `tools/check_style.sh` PASS — 45 files, no enforced finding;
`tools/check_style.sh --self-test` **FAIL** (PL-172, §6); `tools/doc-audit.sh` clean.

**Questions:** none open on either side. The one owner decision is scheduled (§1.1) and needs the desk work first.

---

## 14. Sprint start (2026-10-01)

- **Build version: 6.1.0.** Settled by Stephen's 2026-10-01 rulings (R21); `VERSION` reads `6.0.0` until §10 bumps it.
- **Working tree:** clean apart from `.vscode/settings.json`, Stephen's own edit, outside every file this sprint touches;
  left as it is. No untracked source in `src/` or `tools/`.
- **Tracking (entry check):** the two completed tasks archived («#3643», «#3644»); 8 live tasks, no `seq` collision.
  Their shape (gist ≤ 60: 2/8; one tag: 0/8; no priority: 0/8; `attention:`: 4/8) predates the creation-time checks and
  is a backlog observation; `plan-to-tasks` writes this sprint's tasks to shape. Leftover tasks, disposed by §12:
  «#3640» resumes as §1; «#3636» and «#3641» are superseded by §1 and §3; «#3506», «#3532», «#3562», «#3592», «#3602»
  stay out of the release by Stephen's rulings. Context: 3 keys, all live; `sprint_established_decisions` is
  regenerated per §0.3 before any dispatch. Auto-memory: 4 files, index 4 lines. **Verdict: ready.**
- **Entry baseline** (the substitute gate, `baseline-health` §2a; the gate's inputs `src/`, `tools/`, `.github/` are
  byte-identical between the measured tree `54c4a1e` and the starting commit, so the planning measurement is this
  tree's):
  - `tools/build-check.sh`: PASS — 2 configurations, 50 files, **50/50 tops certified**, both release demos certified,
    all 60 bench tiers within the DEBUG footprint; **0 warning lines** in the whole log. Excluded, by name:
    `hng034rm.spin2` (PL-1).
  - `tools/check_style.sh`: PASS — 45 files, no enforced finding; the vendored files excluded by D1.
  - **One failure group:** `tools/check_style.sh --self-test` exits 1 (T128 has no fixture). **Fix-when: in this sprint,
    §6 PL-172** (Stephen's 2026-10-01 "pull in the simple changes/fixes").
  - **A green gate is a compile result only.** Behaviour is certified on the bench (§9).

## Revision history

- **2026-10-01** — written.
