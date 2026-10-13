# P2-BLDC-Motor-Control — Punch List

Active outstanding work. Confirmed-done items are swept to a dated archive by
`punch-list-maintenance` at sprint closeout.

Opened 2026-09-09 by the `bootstrap-conventions` / `baseline-health` bootstrap.

---

## Open

Confirmed-done entries swept on 2026-09-23 are in
[`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-23.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-23.md), those
closed by the 2026-09-26 release audit are in
[`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-26.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-26.md), and those
swept at the 6.0.0 sprint closeout are in
[`plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01.md). The study that
opened 6.1.0 planning swept PL-19, PL-31, PL-163 and the three 2026-09-20 driver notes to
[`plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01b.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01b.md). The 6.0.0
release burn-down that headed this list until then is in git history (`git show d72e7ed:DOCs/PUNCH-LIST.md`). The
6.1.0 closeout swept twenty entries (PL-167's fix and everything certified with it) to
[`plans/archive/PUNCH-LIST-ARCHIVE-2026-10-03.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-10-03.md).

### v6.2.0 is release quality; what we look at next — 2026-10-13

STEPHEN 2026-10-13, after the Rev B session: *"This is already release quality. It's already driven on the floor, so
I think we're ready to go."* *"We are not going to qualify serial for this release."* The open items below are what we
will look into for the next patch or minor release; none of them stops a user from driving the motors or the robot.
Which of them read as Known Issues in v6.2.0's CHANGELOG is Stephen's («#3690»).

**For this release (1):** PL-224 (process history out of the shipped comments), with the documentation and CHANGELOG
close-out.

**Next minor release — serial (4):** PL-111, PL-148, PL-154, PL-157: the serial top level and its host example have not
been run on hardware in v6.2.0; the next minor release qualifies serial.

**Next release — the driver under load (2):** PL-181 (lag peaks reach LAG_SOFT in calm running on the floor), PL-184
(at quarter speed one direction draws more current). The platform last ran on the floor at DRIVER_REV 49 (2026-10-02);
the 6.5″ is certified wheels up on DRIVER_REV 62.

**Next release — the demo (1):** PL-228 (the two-wheel demo's debug build logs late front-cog passes; every drive still
ends on time).

**Next release — our test harness (7), no user effect:** PL-225 (parameter names), PL-226 (lag bound on undriven
samples), PL-227 (front-cog stats at 130 MHz; PL-164 closes with it), PL-190 (SRVKEEP's drifting reference), PL-182 and
PL-192 (floor sampler corrections never run), PL-136 (pre-flight retry, certifies itself on a failure).

### The register after the v6.2.0 burn-down — 2026-10-10

STEPHEN 2026-10-08: *"Everything we find, we fix"*; *"clean up everything we can, test harness and all"*; then one
certification closeout, a Doco (Rev A) bench run and a Rev B boards run, *"not to discover any more findings"*. «#3707»
walked every open entry against the tree and the logs. **Before: 75 open. After: 39 open, 36 closed.** Every open entry
sits in exactly one group below, and none is open for desk work: each waits for a closeout row or is held by
Stephen's ruling. The closed ones carry a dated *Status (2026-10-10, burn-down)* line saying why, and are swept to the
archive at the sprint's closeout.

**Closed by the burn-down (36):**
- **Fixed at the desk in «#3707»:** PL-63 (a one-sample hall flicker read as rest), PL-139 (the coast's rest window
  opens at rest's confirmation), PL-178 (`pasm_equiv`'s baseline is the last commit), PL-197 (the answer bound counts
  two-stage requests: DRIVER_REV 60, 40 ms), PL-202 (T0-27 judges the filtered fold), PL-220 (the range record carries
  the fault's kind and the hall counts). Also PL-64's stale panel prompts, regenerated.
- **Fixed earlier and verified, or fixed in the tree for a binary no plan runs:** PL-20, PL-21, PL-27, PL-44, PL-53,
  PL-64, PL-65, PL-71, PL-103, PL-109, PL-134, PL-135, PL-198, PL-203, PL-204, PL-205, PL-206, PL-207, PL-208, PL-209,
  PL-213, PL-214, PL-217.
- **Moot, merged or subsumed:** PL-46 and PL-98 (the scan serves no release feature), PL-119 (no cell uses the
  offset-shift provocation), PL-200 (not reproduced; its path corrected at DRIVER_REV 58), PL-201 (merged into PL-170),
  PL-211 (subsumed by PL-219), PL-215 (a board's resolution, worked around).

**Certified by the Doco (Rev A) closeout (7):** PL-170 and PL-210 (the hand-load rows, with a grip), PL-199 (a
`clk-300` / `clk-350` rest-zero probe, then the desk), PL-212 and PL-216 (the range and L-mininc rows at all six
supplies), PL-218 (the stop rows at 7.4 and 11.1 V), PL-219 (the misdial pass in the qualify rows, run on a cold motor:
unit 2's +40 per mille at 24 V was root-caused at the desk 2026-10-10 to a hot motor, the supply ruled out by Stephen).

**Certified by the Rev B closeout (7):** PL-23 (`t0 clk-floor`), PL-111, PL-148, PL-154 and PL-157 (the serial pairs,
STEPHEN 2026-10-03 *"a lightweight certify of serial drive"*), PL-164 (the clock-floor rows), PL-176 (`adopt-wheel`).

**Watches the closeouts carry at no load of their own (4):** PL-43 and PL-126 (no log stops mid-run), PL-120 (no start
check refuses the right board), PL-136 (certifies itself on a wheel's first PREFLT failure).

**The 6.1.0 floor watches, certified by the Rev B closeout's floor row (4):** PL-181, PL-182, PL-184, PL-192, each read
by a floor tier (`floor-auto`, `floor-grab`); STEPHEN 2026-10-10, *"Q1 B"*, *"(only because we are doing a revB wheels up
so we are already at the platform)"*: the Rev B sheet carries those two tiers, last, after the wheels-up rows.
**Corrected 2026-10-10 («#3708», building the sheet):** this group listed six, and said each was read only by the floor
tiers; two were not. **PL-190** (SRVKEEP) is a part-A ladder cell, read wheels-up by the Rev B sheet's row 1 (`dual-a`).
**PL-191** was seen in an RC drive (`floor-rc`), which neither floor tier is. The ramp generator's path for a raised
speed is unchanged since (no commit since DRIVER_REV 48 touches it), so a run would re-measure it; it is Known Issue
evidence for Stephen's ruling in «#3690», not a closeout load. Stephen's floor-row ruling stands on its other four.

**Hardware, needing an act at the bench (1):** PL-60 (a DMM reading across each board's supply terminals). **Not on the
Rev B sheet** («#3708»): it is ancillary under STEPHEN 2026-09-26 (*only work that makes a 6.0 feature operational is
chased*), and it is a meter transcription, which a run sheet does not ask for again (overlay P1). It stays open.

**Held by Stephen's rulings (14):**
- **Ships as a Known Issue:** PL-118 (phase-short braking is not current-limited; ruling 1 A); PL-193 (the pack voltage
  is not used by the drive), PL-194 (regenerative current is not shown), PL-195 (the hold's defaults sized unloaded),
  PL-196 (`calibrate()` does nothing). Which ship in v6.2.0's Known Issues is his («#3690»).
- **After v6.0.0:** PL-102 (a "following" getter), PL-165 (the DEBUG footprint measure), PL-166 (the inertia term).
- **Not taken up, or measure only:** PL-105 (the lag hold past the torque peak), PL-108 (field-weakened slip, outside
  the published range: DRIVER_REV 59's ceilings stay on the back-EMF line), PL-110 (crawl duty on `duty_min`).
- **Deferred, starting when he calls them:** PL-174 (vibration study), PL-175 (N-motor shape), PL-177 (back-EMF delta
  release).

**Standing rulings carried from 6.0.0:** the fault-return run faults its wheel with the guarded `testForceFault()`, not
the wrong-offset write (STEPHEN 2026-09-28, *"fp1: A"*); a test built on a wrong premise is corrected before it runs
again (STEPHEN 2026-10-01).

### PL-20 -- `BC-SENSE` `i_mV_avg` overflows a long at the pre-S-3 scale

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree.** `test_bench_char.spin2` keeps the
> overflow-proof running mean (`:233`, `:1571`); no release plan runs `char`, so no run is owed.

> **Status (2026-10-01):** FIXED IN TREE, not yet run. `test_bench_char.spin2` keeps a running mean without storing
> the sum (`CON { overflow-proof running mean (PL-20) }`, :231; :1568). The `char` binary has not run since, and no
> plan runs it; its next run certifies this.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench harness accumulator)

**Found 2026-09-12 in Bench Pass 1 step 4.** `debug_260912-153807.log:2853` and `:3650` report
`i_mV_avg` -3_173_500 and -3_067_089 with `i_mV_min`/`i_mV_max` both positive. `senseSumMv`
(`test_bench_char.spin2:847`) adds ~516 samples of ~5.2x10^6 -- past 2^31.

Recovered exactly, because the sum wraps once and the result lands inside `[min, max]`:
5_150_080 and 5_176_610 raw, i.e. 839.3 and 843.6 mV after dividing by `adc_fram`.

«#3503» shrinks the readings ~6136x and hides this at today's dwell, but an accumulator's
correctness must not depend on another fix landing or on how long the operator waits. **Fix:**
carry the sum in two longs, or accumulate per-second means. The analyser («#3509») should
treat `avg` outside `[min, max]` as an instrument fault, never as a reading.

### PL-21 -- the quiescent-zero hold reads a stopped instance's frozen telemetry

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree.** The hold runs on a started driver
> (`test_bench_char.spin2` `:270`, `:1084`, `:1701`); no release plan runs `char`, so no run is owed.

> **Status (2026-10-01):** FIXED IN TREE, not yet run. Hold 0 now runs on the LEFT driver started at zero command
> (`HOLD_ZERO_SIDE`, `test_bench_char.spin2:268`), and telemetry is read only from a running cog (:1698). Its next
> `char` run certifies it; no plan runs it.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench harness quiescent hold)

**Found 2026-09-12 in Bench Pass 1 step 4.** `debug_260912-153807.log:460`: 542 samples with
`i_mV_min` = `i_mV_max` = `i_mV_avg` = 562_020, `drv_state` 1, while every motion hold swings
~±100 mV. That is not a noisy zero; it is no measurement at all.

Mechanism, from source: preflight leaves `currentSide` = RIGHT; hold 0's `ensureSide(SIDE_NONE)`
stops the right cog; `activeTelemetry(SIDE_NONE)` then reads `wheelL`
(`test_bench_char.spin2:671-674`), whose cog was stopped during preflight. Its status `VAR`
block is whatever the driver last copied out before `cogstop`.

**Consequence:** hold 0 gives the meter's zero (0.00 A) but not the sense channel's offset.
Until fixed, that offset comes from the 8-hold fit -- ~9 mV at 0 A, DERIVED. **Fix:** run the
quiescent hold with a driver started at zero command, so the bridge is idle and the ADC live,
or report the sense fields as `NOMEAS` when no cog is running.

### PL-23 -- bench binaries print booleans as numbers

> **Status (2026-10-13, Rev B evaluation): CLOSED CERTIFIED.** `t0 clk-floor` (`debug_261013-091507.log`) prints its
> board flag as a word on both boards (`T0-20,base,16,...,rev_b,TRUE`, `base,32 ... rev_b,TRUE`); 30 of 30 cells PASS.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT** -- its `t0 clk-floor` row: the T0-20 line
> prints `rev_b,TRUE`, a word.

> **Status (2026-10-01): FIXED IN THE TREE** («#3647»); the run-time half is the next `t0` log printing `rev_b` as a
> word (formatting only, no dedicated cell). Fixed: `test_bench_spin`'s SP-READY and SP-PHASE fault fields;
> `test_bench_t0`'s T0-20 `rev_b` and the T0-24 try row (four flags as TRUE/FALSE, `measured` as TRUE/FALSE/CUT,
> worst case 260 bytes); `testGetResults()` now returns TRUE/FALSE and its six print sites print the word. The class
> sweep over `src/` found two more, both fixed: the driver's wiring-walk line (`isp_bldc_motor`) and the steering
> object's platform-fault line. The `test_bench_t0` 0/1 count at the `n` field stays a count. The sites table below
> is history.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record formatting)

**Raised by Stephen 2026-09-12:** *"true and false are very large. One of them is a very large
value when printed as a decimal. I think when we're printing out boolean values, we have a new
debug directive that prints it as true and false."* A Spin2 `TRUE` is -1, so `udec_()` prints
`4_294_967_295` (MEASURED: `BC-PREFLIGHT,...,ok,4_294_967_295`,
`2026-09-12/debug_260912-153807.log:35`). The directive is `BOOL()` / `BOOL_()`
(`p2kbSpin2DbgDebugFormattersComplete`); a line-builder record emits the text token instead.

Sites found by search, 2026-09-12, with the task that owns each:

| Site | Form | Owner |
|---|---|---|
| `test_bench_char.spin2:435` `ok` | `udec_(moved <> 0)` -- prints the large value | «#3521» rewrites this binary |
| `test_bench_spin.spin2:106` `left`/`right`, `:158` `fault` | `udec_(ok <> 0)` -- large value | no task touches it -- fix when it is next built |
| `isp_bldc_motor.spin2` `testGetResults()` `bDidFault` | returns the raw `fault` long (`$FFFF_FFFF`), not TRUE/FALSE; `util_char_motor.spin2` prints it with `sdec` | found by the «#3501» design agent; fix when the test API is next touched |
| `test_bench_t0.spin2:236` `agree`, `:254` `legal` | `? 1 : 0` -- small, but a number | «#3504» extends this binary |
| `test_bench_detect.spin2` `agree` and similar 0/1 fields | `? 1 : 0` | **deliberately left** until Bench Pass 2b's re-run is diffed against the 2026-09-11 log, whose format it must match |

The rule now travels with every dispatch (sprint established decisions, item 13).

### PL-27 -- the Doco motor's offset and speed-ceiling tables were characterised while board detection was broken

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed.** The Rev A Doco tables were re-measured on a detected board
> (D1b..D4) and rewritten: the lead table (DRIVER_REV 57), the ceilings and floors (DRIVER_REV 59, PL-216). The Doco
> certification's range rows certify them, under PL-216.

> **Status (2026-10-05): OPEN, being fixed in v6.2.0 «#3684» (the Doco tables).** D1b measured the Rev A columns on
> DRIVER_REV 53 (`DOCs/analyses/bench/2026-10-05/D1B-EVALUATION.md` §2.2-2.3, D1B-2 / D1B-3): the half-speed current
> minimum sits at NEG −59.7° / POS +54.1° against the shipped −53° / +53°; the 11.1 V ceiling (545e6) is 116 % of the
> motor's no-load speed and runs duty-capped; 7.4 V and 14.8 V run NEG duty-capped at their tops. Closes when «#3684»
> rewrites the Rev A columns from that log. (Earlier status: ANCILLARY for 6.0, 2026-09-26; the v6.2.0 sprint took it.)

**Found 2026-09-12** (DERIVED from `src/isp_bldc_motor.spin2` `offsetsForMotor()` and
`confgurePowerLimits()`). For `MOTR_DOCO_4KRPM` both tables branch on `eDetectedBoard`: offsets
Rev B 33–45° vs Rev A 52–54°, and different speed ceilings per revision. Until «#3500», a Rev B
board read as Rev A after any stop and restart (MEASURED 2026-09-12). Two consequences:

1. **Behaviour changes for Doco users.** A Doco on a Rev B board that was stopped and restarted
   used to get the Rev A commutation offset (about 15–20° different) and the Rev A speed
   ceiling. It now keeps the Rev B values. That is a correct fix, but a user-visible one —
   release note for «#3515».
2. **Which board each Doco column was measured on is uncertain.** If characterisation involved
   stop/start cycles, a "Rev A" value may have come from a misdetected Rev B board. The Rev A
   ceiling column is also non-monotonic in voltage (282M at 7.4 V, 545M at 11.1 V, 335M at
   12 V). **The measurement history is Stephen's to confirm**: which boards the Doco columns came
   from, and whether motors were restarted between readings. It needs no answer before the 6.5″
   bench work; the Doco bench is deferred past the next release (decision 2026-09-11).

### PL-43 -- scan run 6 went silent under a load step, and the watchdog did not speak

> **Status (2026-10-10, burn-down «#3707»): A WATCH ON BOTH CLOSEOUTS** -- no log stops mid-run; a stall prints its
> watchdog line. One instance since the supply repair; `test_bench_scan` itself runs in no plan.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench silence; rig supply)

**Found 2026-09-14 in Visit 1** (`analyses/bench/2026-09-14/VISIT-1-RESULTS.md` §8). This is
«#3536»'s third outcome: a silent stop with no `BS-WATCHDOG` record.

**What the logs show (MEASURED):**
- At 11:35:47 the first download failed: "No Propeller v2 device found" (`debug_260914-113544.log:16-18`).
- Run 6 passed its left self-check and reference point (`debug_260914-113610.log:210-218`).
- It stepped to a 53° offset and commanded −¼ speed at 11:36:46.755 (`:220-222`). Nothing more
  came from the P2; the session was closed at 11:39:07 (`:224`).
- Run 7 drew about 2.7 A at that same point (`debug_260914-114703.log:224-226`). So the silence began
  within 16 ms of a step to the highest non-aborting current in the leg.
- No `BS-WATCHDOG` appeared. On a cog-0 stall the watchdog stops both wheels, then prints its
  records and ends the session within 4.0–4.5 s (`src/test_bench_scan.spin2:5453-5515`, DERIVED).
  In its self-test nine minutes later it did exactly that (`debug_260914-114523.log:74-82`).
- STEPHEN then hardened the supply connections: *"i think vibration affected the power supply (just a
  hypothesis)"*. Every later run completed, including run 7 through the same point.

**What that establishes (DERIVED):** the silence was not a cog-0-only stall, which is the case
«#3534»'s watchdog was built for. Three explanations remain, told apart by what the wheels did after
11:36:46:

| Explanation | The wheels would have… |
|---|---|
| P2 brown-out or reset | stopped and gone free at once |
| Debug channel held (every cog blocks at its next `debug()`; see PL-41) | finished the point, stopped and gone free about 4–5 s later |
| Host or link loss (the P2 carried on unheard) | kept stepping through points |

**Settled (see the closing note below):** the unsound supply connection was the cause. Stephen
certified the repair from the runs that completed after the rewiring.

**STEPHEN, 2026-09-14** (asked as «#3536» requires): *"i made no further checks as i was more
concerned about the stop with nothing reporting... i found a corrected a power supply connection
issue (was not sound). no other observations."*
- The supply connection **was** unsound, and it has been corrected (STEPHEN).
- Nobody watched the wheels, so a held debug channel is not excluded by observation.

**A held debug channel is ruled out** (STEPHEN, 2026-09-14): *"cogstop clears the locks"*. A
stopped cog therefore cannot leave lock 15 held (PL-41), and a jammed debug channel would need a cog
that is still running and never releases the lock. That leaves the explanations DERIVED from the
evidence:
- **most likely,** a P2 brown-out or reset from the unsound supply connection under a ~2.7 A step;
- **otherwise,** a host or link loss.

**Closed 2026-09-14 — cause repaired and certified.** STEPHEN: *"the repair is certified as proven
by the completed logs after the bench rewireing"*. After the rewiring, every run completed: the
watchdog self-test, detection, Tier 0, scan run 7 (including the same 53° load step) and the
characterisation run.

Run 5's silence on 2026-09-13 predates the repair. That it had the same cause is consistent with the
evidence (DERIVED), but not certified.

**Recurred at Visit 2 (2026-09-15), after the repair, under a hand-brake. Open again as a live finding.**
The repair's certification stands for the runs it covered; this occurrence is not explained by it.
- MEASURED (`analyses/bench/2026-09-15/debug_260915-142454.log`): `dual-brake` started both wheels at half
  power (`:121`). At 14:25:08.612 the panel told the operator to brake the LEFT wheel (`:122`). Line `:122`
  carries countdown frames 30, 29 and 28, then stops mid-poll, about 3–4 s into the brake. Nothing more came
  from the P2; the host closed the session at 14:26:02 (`:124`).
- Absent: `BM-ABORT` (the 10 A trip), `BM-WATCHDOG`, `BM-OPER TIMEOUT`, `BM-END`.
- DERIVED: the same signature as run 6 — silent under the heaviest load step the harness makes, with the
  watchdog silent too, so not a cog-0-only stall. The log cannot separate a brown-out or reset from a
  host or link loss.
- **Nobody was asked to watch for it**, so there is no observation to draw on (STEPHEN: *"i don't know that
  dual-brake went silent"*). Designing that out is mine (doctrine overlay P1): the next attended brake step
  must make a silence visible and record what separates the explanations.
- Safety (DERIVED): if a brake load can drop the P2, the protective code cannot act while it is down. The
  physical battery disconnect stays the only panic procedure.

### PL-44 -- every value captured through an abort trap in the bench binaries reads 0

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree.** The `t0` and `char` halves were certified at
> Visit 2; `detect`'s last trapped capture is removed (`:1266`) and no release plan runs `detect`.

> **Status (2026-10-01):** FIXED IN TREE; one half not yet run. The `t0` and `char` captures were certified at Visit 2.
> The detection binary's last trapped capture is gone: its phase-2 start is a plain call (`test_bench_detect.spin2:1266`,
> converted by «#3574», the record-builder conversion). `detect` has not run since; its next run certifies that half.
> The "NA reason tokens / sentinel pre-loads" residual below has no defect attached to it, so nothing is owed for it.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench harness trap captures)

**Found 2026-09-14 evaluating Visit 1** (`analyses/bench/2026-09-14/VISIT-1-RESULTS.md` §6).

**What was measured:** 12 logged instances at 6 source sites in `test_bench_t0.spin2` and
`test_bench_char.spin2`, and 0 counterexamples. Each expression-context trap, `x := \method()`,
logged 0 while the library took, and printed, a non-zero path:
- `* Motor COG #1` / `#2`;
- the −1 failure branches `!! ERROR filed to start Motor Control task` and
  `!! ERROR filed to start left/right drive cog(s)`.

Key lines: `debug_260914-114636.log:967-970`, `:1016-1018`, `:1038-1039`, `:1058-1059`;
`debug_260914-115953.log:268-281` with `:420`, `:470-471`, `:483-484`.

**What it is not (DERIVED from the same logs and source):**
- *Not the library.* `isp_bldc_motor.spin2:109-122` is correct. Untrapped calls to the same method
  return the printed cog: scan `BS-START`, char `BC-START` and `BC-PREFLIGHT`, and the steering
  object's `ltcog = 2 rtcog = 3` (`debug_260914-115953.log:402`).
- *Not caller and callee sharing a variable name.* T0-10 and T0-8 trap `\motor.start()` directly,
  with different names, and read 0 too.
- *Not the order in which the callee sets its result.*
- *Not an enclosing trap.* Untrapped calls made inside `\runSession()` and `\runScan()` return
  correctly.

**Not yet told apart:** every receiving variable was already 0 before its trap, so the logs cannot
separate "the trap yields 0" from "the trap assigns nothing". `p2kbSpin2Abort`, which cites
pnut_ts's own guide, says a trap returns the method's normal return value when no abort occurs.

**Direction (STEPHEN, 2026-09-14):**
- *"please expect the compiler to be behaving correctly and then chase to root cause... don't be
  giving up without do the proper work required"*. The cause is presumed to be in our code, harness
  or runtime interactions. It is not attributed to the tool (doctrine overlay P7). The root-cause
  study below settled the disposition, and no probe is built.
- *"traps are an exeptional return path - not normal use ... so we are we using them?"* We used a
  trap per call only so that a library abort would become NOMEAS instead of ending the binary. That
  is the exceptional path used as a routine capture. The harness calls normally, and keeps a single
  top-level trap to secure the hardware.

**Root-cause study (2026-09-14, [`analyses/PL-44-ROOT-CAUSE-STUDY.md`](analyses/PL-44-ROOT-CAUSE-STUDY.md)):**
- **No defect in our code explains the zeros.** Refuted, with evidence:
  - a wrong print path (the wrong value is in memory);
  - multi-result loss;
  - a real abort;
  - a shared variable name;
  - stack exhaustion.
- **Two hypotheses survive, confounded:**
  - **H1:** a `debug()` inside the trapped callee;
  - **H7:** a trap inside another trap's frame.

  Every failing capture had both.
- **The logs cannot tell "assigns 0" from "assigns nothing":** every receiver was already 0.
- **Disposition (2026-09-14): design the patterns out, do not characterise them.** STEPHEN: *"you
  are leaning to bench runs when you should be leaning to choosing code patterns that are not
  problemmatic... the possible patterns you cite sound like antipatterns that we shouldn't have in
  our code in the first place."*
  - The surviving suspects are a trap used to capture a return value and a trap nested inside a
    trap. Neither should exist in the harness.
  - «#3539» removes both. Calls are made normally, reading `start()`'s cog id or -1. One top-level
    trap prints its value on every run. Traps remain only in deliberate abort-path tests.
  - The library's error contract (PL-47) was deferred the same day, so none of this depends on
    `getError()`.
  - The probe in §3 of the study is not built, and no conclusion about the toolchain is drawn.
- **Other harness defects the study found:**
  - the char PL-36 claims check was masked;
  - T0 guards accept a stuck 0;
  - `aborted,DRIVE` reports a wrong value as an abort;
  - top-level trap values are printed only on abort.

  These are listed in §4 of the study and are in «#3539»'s scope.

**Fixed in tree 2026-09-14 («#3539»); certification is owed to Visit 2.**
- `test_bench_t0.spin2` and `test_bench_char.spin2` make every normal-path library call untrapped
  and judge its returned value, with a `testGetMotorCog()` cross-check as the positive control.
- Each binary keeps one top-level trap, whose value prints on every run.
- The remaining traps are the declared abort probes: T0-6, T0-7, and the char PL-36 claim starts.
  Each judges an abort by a completion flag, never by the trapped value.
- The char claim check now runs before cleanup, and `BC-STEER` reports `drive_done` separately.
- The four cells keep their Visit 1 status and are carried to Visit 2 by the collation's scope.
  `--check-ready` now checks that same scope, locked by selftest (y).
- Not done, and still in this entry's scope: NA reason tokens on every emit, and sentinel pre-loads.

**Certified at Visit 2 (2026-09-15, `analyses/bench/2026-09-15/VISIT-2-RESULTS.md` §2):** the capture fix
works.
- `R1-T0-START`: return 1, raw cog 2 (`debug_260915-140038.log:975-976`).
- `R1-T0-RESTART` (`:1011`).
- `R1-T0-EXHAUST`: return −1, no leak (`:1068-1069`).
- `R10-CHAR-STEERFAIL` (`debug_260915-140100.log:354`).
- `R13-CHAR-BRAKESTART` ×4: start return 2 (`:369-414`).

All PASS. The remaining scope items above stay open.

**Still present in the detection binary (Visit 2, 2026-09-15):** `BD-PH2 ... step,started,start_ret,0,motorcog,2`
(`analyses/bench/2026-09-15/debug_260915-143237.log:465`, `:873`) while the library printed `* Motor COG #1`.
`test_bench_detect.spin2` still captures its phase-2 start through a trap. It feeds no verdict and does not
affect detection. Fix it when PL-53 converts that binary.

**What it cost this visit:**
- R1-T0-START and R1-T0-EXHAUST FAILed.
- R10-CHAR-STEERFAIL FAILed.
- R13-CHAR-BRAKESTART was NOMEAS on all four instances: its guard correctly refused the untrusted
  cog id (`test_bench_char.spin2:2212-2213`).
- `steerDriveTrapped()` reported `aborted,DRIVE` for a drive that moved 13 ticks per wheel.
- `claimsFreeCheck()` accepts 0–7, so a stuck 0 passes it by accident.

**It reaches back into the record:** T0-10's `start_return,0` on 2026-09-11
(`analyses/bench/2026-09-11/debug_260911-143911.log:127`) came from the same trapped capture, as did
T0-8's `start_return,0` in that log, the detect binary's `start_ret 0`
(`analyses/bench/2026-09-12/DETECT-A-EVALUATION.md` §6) and the 2026-09-10 run. They were PL-22's
basis for "start() returned 0 on success", so they are void as evidence of library behaviour.

**Re-derived 2026-09-14 (DERIVED; see PL-22):**
- 5.0.2's `start()` returned cog id + 1 on success and 0 on failure
  (`analyses/DRIVER-AUDIT-2026-09-09.md` finding C).
- Its steering mask therefore released both motors on success; only a failed start stranded the
  survivor (findings AD and AH).
- The field report's `demo_dual_motor` drove both motors through that start
  (`analyses/user-report-2026-09-09-ANALYSIS.md` observations 1 and 4).

The sprint plan, the 2026-09-13 plan-state analysis, the sign-off design, the manifest and
DETECT-A-EVALUATION carry corrections dated 2026-09-14.

**Fix direction:**
- Capture a trapped call's result without depending on the trap's value: the callee writes its
  result to a VAR before returning, and the caller reads that VAR after the trap.
- Keep the completion flag for abort detection.
- Add a self-check that a known non-zero return reads back non-zero, so a capture defect can
  never again pass silently.

### PL-46 -- scan v4 cannot demonstrate a half-speed minimum, and its half-speed cell passes anyway

> **Status (2026-10-10, burn-down «#3707»): CLOSED, moot.** 6.0 commutates from the measured hall position and a lead
> table against speed, and the motor-adoption tool (`util_adopt_motor`) is the offset scan a user runs; `test_bench_scan`
> serves no release feature and no plan runs it.

> **Status (2026-10-01):** DORMANT. Its "IN THIS RELEASE" line below is aged: 6.0.0 shipped commutating from the
> motor's measured hall position and a lead that follows speed (CHANGELOG v6.0.0), not from a scanned offset pair.
> The scan last ran on 2026-09-21 (`2026-09-22/debug_260921-200935.log`), and no plan uses it. It wakes if a
> characterisation plan takes up the scan; the redesign (a droop stop instead of a fault walk) is recorded below for
> then.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (commutation scan instrument)

**Found 2026-09-14 in scan run 7** (`analyses/bench/2026-09-14/SCAN-RUN-7-EVALUATION.md` §5). Read
from `src/test_bench_scan.spin2` against the log; DERIVED unless marked.

**What was measured (MEASURED, `debug_260914-114703.log`):**
- In all four half-speed legs, the lowest current is at the last clean point before a fault, and
  nothing between the two was measured.
- The fits are EDGE, EDGE, EDGE and POOR-pinned (L645, L741, L1276, L1358).
- One leg printed a shift with `shift_sig TRUE` from that POOR fit (L748).
- All four R9-SCAN-HALFLEG cells PASS (L1380-1381, L1401-1402).

**The defects:**
1. **D1:** `probeConfirmCliff()` stops at the first clean ±5° probe and probes ±2° only after a
   fault (src:3050-3058). R9-SCAN-HALFLEG's `CLIFF_PROBED` counts that a probe ran, not that the
   minimum was resolved (src:580-586). **Its criterion is met by the defect it exists to catch.**
   The quarter-speed `refineCliffEdge()` has the same gate (src:2769-2774).
2. **D2:** nothing applies the negative case.
   - Half-speed legs are marked bracketed by assignment (src:2462).
   - `hasMinimum()` accepts POOR (src:4345-4351).
   - `fitPinnedNearLimit()` feeds only its print (src:4167), although its comment forbids a pinned
     minimum reading as free (src:2928-2930).
3. **D3:** `BS-RESULT` and `BS-PAIR2` use fitted minimum currents, not measured floors
   (src:4368-4371, src:4490-4509). The right motor's `imbalance FALSE` (L1367) reads 1.29 on its
   measured floors.
4. **D4:** cliff-edge resolution (±1° or ±2.5°) is not reported, and one EDGE verdict turned on 0.05°.
5. **D5:** raw means printed under neutral names (`low_mV_x10`, `ref_start` / `ref_end`).
6. **D6:** R9-SCAN-OWNZERO and R9-SCAN-PAIR2 would also pass on the unfixed path.
7. **D7:** duplicate SIGNOFF instances carry no slot identity, so the sheet reads "4 of 2".
8. **D8:** R8's 5 mV falsifier was not shown to fail under back-to-back starts.

**Consequence:** «#3522»'s half-speed confirmation cannot be met by this instrument, so no offset
pair can be applied on its evidence. Visit 1's R9 sign-offs certify that code ran, not that it
works.

**Fix direction (scan v5):**
- After a clean probe, keep probing toward the fault in 2° steps.
- Do not count POOR or pinned fits as minima.
- Apply the rise-on-both-sides test at half speed.
- Judge pair ratios on measured floors.
- Make R9-SCAN-HALFLEG fail when the lowest point sits at the window edge.
- Give each SIGNOFF instance a slot token.
- Report edge resolution beside every margin.

**Scan run 8 (Visit 2, 2026-09-15, `analyses/bench/2026-09-15/VISIT-2-RESULTS.md` §11):** D1's cell
now tells the truth.
- `R9-SCAN-HALFLEG` FAILs on LEFT POS, RIGHT NEG and RIGHT POS, and is NOMEAS on LEFT NEG.
- All three half-speed fits are POOR and pinned. Current is still falling at the last clean point
  (margins 4.0–4.4° from the fit).
- The half-speed minimum is still not demonstrated, so «#3523» stays blocked.
- Quarter-speed minima reproduce run 7 within 0.1–1.6°.

**Status 2026-09-17 (aged-state sweep) -- no longer "blocked", and IN THIS RELEASE.**
- STEPHEN 2026-09-17: *"we need confirmation of motor phase offsets before release - finish the commutation
  scan"*. Confirmation is a spin-in-place attended floor run after the lifted scan (STEPHEN: *"yes spin in
  place but max revolutions limit so we don't stress cable"*).
- **The half-speed legs failed on FAULTS, and that condition is gone:** the lag limiter («#3558») makes
  the driver droop instead of faulting (`RMPDROOP` PASS both motors, Visits 4 and 5).
- ⛔ **Which means the scan's own geometry is now wrong.** It finds each window edge by walking until the
  motor faults (`probeTowardFault()`, `refineCliffEdge()`, `probeConfirmCliff()`, `BS-CLIFF`,
  `R9-SCAN-HALFLEG`). Under the lag limiter it may never fault; the stop condition must become a droop
  detector (the scan's own `R12-SCAN-RATE` tick-rate check is the ready signal). Also check the
  fold-back limit against the worst swept current, which would otherwise flatten the curve the fit reads.
- D1, D2, D3, D4, D5 and D7 are fixed in scan fmt 10; **D6 and D8 are not confirmed** and are part of the
  redesign.
- **2026-09-26:** D6/D8 moved to PL-98.

### PL-53 -- the scan, char and detection binaries still carry their own copies of the record builder

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree.** `scan`, `char` and `detect` all build their
> records through `isp_bench_log`, identical by construction; every one compiles in the gate.

> **Status (2026-10-01):** FIXED IN TREE; `scan` has run on it (2026-09-21), `char` and `detect` have not. Their
> next runs are the check, and no plan runs them. The "IN THIS RELEASE" line below is aged.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record builder)

**Filed 2026-09-14** by «#3508» phase 2 (`plans/MOTION-HARNESS-DESIGN.md` §7.2; §12.1 Q5 ruled it a
punch-list item after Visit 2).

- **The class:** one tagged-record line builder kept as separate copies in several top-level programs.
  PL-17's hazard stands: the copies must stay byte-identical, because every analyser parses the same
  digit grouping.
- **Evidence (read 2026-09-14):**
  - `src/isp_bench_log.spin2` is the extracted builder. `src/test_bench_dual.spin2:680-681` declares it
    twice (`benchLog` for cog 0, `wdLog` for the watchdog) and is its only consumer.
  - `src/test_bench_char.spin2:3114-3203` still carries its own `lineReset` … `lineEmit`, plus a watchdog
    mirror at `:3492-3609`.
  - `src/test_bench_scan.spin2` and `src/test_bench_detect.spin2` carry theirs (the design cites the scan's
    at `:5460-5539`; not re-read for this entry).
- **Why not now:** all three are certified binaries that Visit 2 runs again: scan run 8, the char
  certification, and the detection re-run diffed against its baseline. Converting them now changes three
  binaries the visit certifies, for no change in what they measure.
- **The deferral's reason has expired (aged-state sweep 2026-09-17):** Visits 2 through 5 have run. The
  scan binary must change anyway for the commutation-scan redesign (PL-46), and the char binary still
  carries two private copies (confirmed 2026-09-17). IN THIS RELEASE as part of the bench cleanup.
- **Fix direction:** after Visit 2, replace each copy with `OBJ` instances of `isp_bench_log` (a second
  instance for a watchdog cog), bump each binary's `SRC_REV`, and prove with a before/after log diff that
  every record prints byte-identical. For the detection binary, `R2-HOST-DETDIFF` is that diff.

**FIXED IN TREE 2026-09-19 («#3574»).** `test_bench_scan`, `test_bench_char` and `test_bench_detect` now assemble every
record through `isp_bench_log` (`benchLog` on cog 0; `wdLog`, a second instance, on the scan's and char's watchdog
cogs). `isp_bench_log` gains `unclampedNumField()`, `hexField()` and `bareField()` for the detection binary's needs.
- **Byte identity, by construction rather than by run.** Every private builder method was compared with
  `isp_bench_log`'s, comments stripped and names normalised: all 46 are the same algorithm (the two `boolField`s
  choose the same tokens by if/else instead of a ternary). The call sites were translated one for one by script,
  with every count checked before writing (char 194 field calls and 20 record opens, scan 435 and 42, detect 146
  and 22). So a record prints the same bytes as before.
- **What the next load of each binary confirms:** the log's records against the previous run's. `scan` runs at
  Visit 6b. `char` and `detect` are not on a sheet; their next run is the check. `detect`'s diff will also show
  the fields «#3574» removed on purpose: `run_ts`, `bnc`, `bnc_max`, and `trapped` → `setup`.

### PL-60 -- the left board's `ph_x10` reading sags with load and the right board's does not

> **Status (2026-10-10, burn-down «#3707»): HARDWARE ONLY, AND IT NEEDS AN ACT.** Its close is one DMM reading across
> each board's supply terminals at a high rung; whether the Rev B closeout carries that reading is decided with its sheet
> («#3708»).

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (board telemetry reading; DMM check)

**Found 2026-09-15 in Visit 2** (`VISIT-2-RESULTS.md` §9.4).

**MEASURED (`debug_260915-134805.log` BM-RUNG2, rungs 20M–165M):**

| | `ph_x10` max / min | Drift | Largest current |
|---|---|---|---|
| LEFT NEG | 24,332 / 23,653 | 2.82 % | 7.9 A |
| LEFT POS | 24,335 / 23,754 | 2.40 % | 6.8 A |
| RIGHT NEG | 23,988 / 23,921 | 0.28 % | 8.4 A |
| RIGHT POS | 23,987 / 23,945 | 0.18 % | 7.2 A |

The left minima sit at the highest-current rung.

**DERIVED:** one pack cannot sag 2.4–2.8 % on one board and 0.2–0.3 % on the other at similar currents.
The two boards' readings respond differently to load. C-6 is CONSISTENT on the left and INCONCLUSIVE
on the right.

**Fix direction:** one DMM reading across each board's own supply terminals at a high rung — the
measurement C-6 names — on **both** boards. It can go alongside PL-45, which is also a left-board
reading offset.

### PL-63 -- the right motor's quarter-speed NEG float stop never confirmed rest, in either rep

> **Status (2026-10-10, burn-down «#3707»): FIXED at the desk, the stillness rule.** The reading was right: in traces 25
> and 28 `pos` held at -29 while `hw` went -29 -> -28 -> -29 for ONE 2 ms sample (k 213-214, and 208-209), a rotor resting
> on a hall edge. `waitRest()` polls every 5 ms, did not see it and confirmed rest; the stored-trace finder saw it,
> restarted its 300 ms, and ran out of capture (rest_k NA). `test_bench_dual` SRC_REV 87: both stored-trace rest finders
> read a one-sample hall flicker as rest (`bSmpStill()`), as the live wait already did; a hall reading that moves and
> stays is motion in both.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench stop-rest reading)

**Found 2026-09-15 in Visit 2.** Minor.

**MEASURED:** traces 25 and 28 end `why,NOT_REACHED` (`debug_260915-134805.log:7888,8787`), although
both reached STOPPED after 19 ticks, like every other quarter-speed stop. Every other STOPMODE trace
confirmed rest.

**Consequence:** the C-4 table has no time to rest for that one cell. Its tick count is complete.

**Fix direction:** read those two traces' last samples for the value that kept changing (`pos`, `hw`
or both), then decide whether the stillness rule or the reading is at fault.

### PL-64 -- the attended-test UI is out of step with what each test needs, and `dual-ui` failed itself

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree.** The walkthrough was rebuilt (SRC_REV 12); the
> panel's prompt bitmap is regenerated from `tools/gen_dual_assets.py` (three prompts' text had moved on, the grab's
> 2 A among them; the other seven bitmaps and the CON / DAT blocks were already byte-identical to the generator's).
> No release plan runs `dual-ui` or `dual-floor`.

> **Status (2026-10-01):** FIXED IN TREE, never run. `dual-ui` has not run since the rebuild (no log since 2026-09-17
> carries UICHECK), and the floor runs that followed use countdown boards instead of the attended panels. The
> paragraph below saying it "certifies at the next attended visit" is aged: no planned run loads `dual-ui`.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (attended bench UI)

**Found 2026-09-15 in Visit 2** (`analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §3).

**MEASURED (`debug_260915-142103.log`):**
- All seven controls passed by key and by click (`:141-455`). The input fix `6aed714` works.
- The walkthrough scored a SKIP input as "something is wrong" on four of the seven previews: step 8 (brake
  start, WAITING FOR START, `:597`), step 9 (brake now, `:626`), step 10 (release, `:690`) and step 12 (floor
  start, WAITING FOR START, `:748`). Steps 11, 13 and 14 scored START.
- STEPHEN, 2026-09-15: *"on the UI test nothing was wrong that i could see. the test itself ruled it a
  fail."* No screen was judged wrong.
- `R14-DUAL-UICHECK-U` FAIL (`:888`), so `dual-brake` and `dual-floor` were owed to the next visit. They were run
  anyway.

**DERIVED, from the crop commands in the log:**
- Every preview, accepted or rejected, drew a live 30 s countdown and the same START/SKIP verdict pair in
  the first two button slots. Nothing drawn separates the rejected screens from the accepted ones.
- **The defect:** a preview puts the verdict buttons in the slots where the real screen's own controls
  belong. It cannot show the real screen, and an input that operates the previewed screen scores as a
  verdict. The walkthrough failed on its own construction, not on anything the operator saw.

**The wider need, STEPHEN 2026-09-15:** *"regarding the use of the UI for the tests... it seems to be out of
sync with some of the test intent (controls offered/enabled) vs. what is needed for the test. please audit
the tests before we run them again."*

**Fix direction:**
- Before the next run, audit every attended step (`t0-hand`, `dual-ui`, `dual-brake`, `dual-floor`) screen
  by screen: the controls offered and enabled against what that step of the test needs, and what each
  input does.
- Rebuild the walkthrough so a verdict can never share a control with the screen it judges.
- Build on the proven panel technique (doctrine overlay P7). Re-run `dual-ui` before any attended motion
  step.

**Status (aged-state sweep 2026-09-17): FIXED IN TREE, NOT YET RUN.** The rebuild (SRC_REV 12) is re-walked
against source in `analyses/ATTENDED-UI-AUDIT-2026-09-15.md` §7: the verdict has its own strip, STOP is live
whenever a wheel is driven, every countdown is labelled, a heartbeat shows a silent P2. No attended load has run
since (Visit 3 did not carry the pair; Visits 4-5 were unattended). **It certifies at the next attended visit**,
which now exists: the spin-in-place floor run STEPHEN approved on 2026-09-17 needs `dual-ui` first.

### PL-65 -- `BM-PLAN` names the wrong findings for the UICHECK and FLOOR parts

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree** (the corrected labels, SRC_REV 12). No release
> plan runs either part.

> **Status (2026-10-01):** FIXED IN TREE, never run: neither UICHECK (`dual-ui`) nor FLOOR (`dual-floor`) has run since
> SRC_REV 12, and no plan runs them.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench plan labels)

**Found 2026-09-15 in Visit 2** (`analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §3). Minor.

**MEASURED:** UICHECK's plan record says `finds AC` (`debug_260915-142103.log:26`); FLOOR's says `finds S-9a`
(`debug_260915-142650.log:26`).

**DERIVED:** FLOOR is the part that finds AC, and UICHECK finds none; S-9a belongs to part C.

**Fix direction:** correct the two labels in `src/test_bench_dual.spin2` at its next revision.

**FIXED IN TREE (aged-state sweep 2026-09-17):** `tokFinds` carried one extra S-9a, shifting FLOOR and UICHECK
by one; corrected in the SRC_REV 12 rebuild (`analyses/ATTENDED-UI-AUDIT-2026-09-15.md` §7). Visible in the
next attended log's `BM-PLAN`.

### PL-71 -- the DocoEng motor's minimum forward increment is `0 - VALUE_NOT_SET`, which is 1

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed.** Both signs have measured minimums (DRIVER_REV 56: 4.00
> ticks/s at 7.4 V; DRIVER_REV 59: 0.10 from 11.1 V up), forward a negative increment. The Doco certification's
> L-mininc rows certify them, under PL-216.

> **Status (2026-10-05): OPEN, being fixed in v6.2.0 «#3684».** D1b measured the slowest steady speed on DRIVER_REV 53
> (`DOCs/analyses/bench/2026-10-05/D1B-EVALUATION.md` §2.4, D1B-6): forward (the NEG increment, `power_sign,1`) turns
> steadily at 1.00 ticks/s at 7.4 V and at 0.60 (the lowest rung) from 14.8 V up; reverse (POS) needs 4.00 ticks/s at
> 7.4 V — the shipped 544,628 (1.46) does not turn steadily there — and 0.60 from 14.8 V up. Closes when «#3684» sets
> both minimums from that log. (Earlier status: ANCILLARY for 6.0, 2026-09-26; the v6.2.0 sprint took it.)

**Found 2026-09-16 in «#3554»**, while folding `confgurePowerLimits()` onto one power-table lookup. The behaviour was
kept byte for byte.

**DERIVED (`src/isp_bldc_motor.spin2`, `confgurePowerLimits()`):** `minFwdIncreAtPwr` is preset to `VALUE_NOT_SET`
(-1), and the DocoEng branch then sets `minFwdIncreAtPwr := 0 - minFwdIncreAtPwr`, which is `1`. The 6.5″ branch
sets `minFwdIncreAtPwr := 544_628` and derives the reverse minimum from it, so the DocoEng line reads as the mirror
of that with the operand swapped: `0 - minRevIncreAtPwr` would give -544_628. `map()` for a +1 % forward request on
the DocoEng motor therefore starts from an increment of 1, where the reverse direction starts from 544_628.

**Fix direction:** confirm against the DocoEng motor's forward sign (its forward increments are negative in the
max table) and set the minimum from the named no-rotation threshold. The DocoEng tables are also the subject of
PL-27. Which sprint takes it is Stephen's call.

---

## Archived

Confirmed-done items are swept out of this file, not kept here. **This list carries outstanding
work only** — that is the one question it answers.

| Archive | Swept |
| --- | --- |
| [`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-17.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-17.md) | PL-3, PL-4, PL-5, **PL-9**, **PL-24** |
| [plans/archive/PUNCH-LIST-ARCHIVE-2026-09-26.md](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-26.md) | the 50 entries closed by the 2026-09-26 release audit (PL-142 fixed the same evening) |
| [plans/archive/PUNCH-LIST-ARCHIVE-2026-09-27.md](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-27.md) | the 12 entries certified by Visit 10 pass 7: PL-66, PL-78, PL-87, PL-143, PL-147, PL-151, PL-152, PL-153, PL-155, PL-156, PL-158, PL-159 |
| [plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01.md](plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01.md) | the 16 entries swept at the 6.0.0 sprint closeout |
| [plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01b.md](plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01b.md) | PL-19 (obsolete), PL-31 (delivered), PL-163 (certified; residual is PL-170), the three 2026-09-20 driver notes (superseded) |

An archive file is never re-edited. If an archived item must be reopened, it comes back here as a
**new** item that references the archive.

---

## Open (continued)

### PL-98 -- two scan sign-off cells cannot fail on the path they exist to police

> **Status (2026-10-10, burn-down «#3707»): CLOSED, moot,** with the scan (PL-46): no release feature or plan runs
> `test_bench_scan`.

> **Status (2026-10-01):** DORMANT with the scan (see PL-46): no plan runs `test_bench_scan`.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (scan sign-off cells)

**Found 2026-09-21 at «#3595», discharging scan run 7's D6 and D8.** One of the three was fixed in
that task; **the other two are recorded here because making them falsifiable needs a control run that
does not exist, and inventing one inside a build task is the error D2 exists to prevent.**

**FIXED at «#3595» — `R9-SCAN-OWNZERO`'s vacuous pass.** Its `bMeasured` argument was the literal
`TRUE`, so a result slot that examined **no** points printed `PASS` with `measured 0` of `n 0`. It
could not tell *"every point carried its own zero"* from *"no point was ever examined"* — and the
second is exactly what the pre-«#3530» path does. Now gated on the examined count, so an unexamined
slot prints `NOMEAS`.

⛔ **NOT FIXED (1) — `R9-SCAN-PAIR2` cannot distinguish net from raw.** The cell judges the
negative-over-positive minimum-current ratio against a band. Scan v4's fix was to compute that ratio
from **net** means rather than **raw** ones. A raw-derived ratio can land inside the same band, so the
cell passes either way and its `PASS` is not evidence that the fix is in force. **What it would take:**
a leg deliberately run with a large sense zero, where raw and net ratios provably differ — i.e. a
control, on hardware. Until then the cell is **coverage, not evidence**, and any sign-off reading must
say so rather than counting it.

⛔ **NOT FIXED (2) — `R8-SCAN-ZXS`'s falsifier is unverified under back-to-back starts.** The
zero-spread limit it enforces was set from spreads measured *after restarts following aborts*. Whether
the limit can fail under ordinary back-to-back starts has never been established, so a `PASS` may mean
*the condition never arose* rather than *the defect is absent* — the negative-measured-once trap. The
decisive evidence for the underlying «#3529» work was the right motor's zero level falling from 72 to
1 mV, **not** this cell's `PASS`.

**Cost if left:** two cells contribute a green line to every sign-off sheet while proving nothing, and
a reader counting greens over-counts the run's evidence by two per motor.

**RESOLVED (3) — `R18-SCAN-FOLLOW`'s negative limb could never fire, so the cell moved (Visit 7c C-2,
«#3597»).** MEASURED: all 16 points the scan scored below `FOLLOW_LOW_PCT` had the driver reading NA
(`VISIT-7C-EVALUATION.md` §4). This was structural, not bad luck. In the scan a point droops only at the
current wall, where `ABORT_I` cuts it short, and a point cut short never fills the driver's 1 s window. The
validity guard is right to exclude it, because an unfilled window reads low for reasons that have nothing to
do with the drive. The three options, judged on this cell's merits alone:
- **(a) a partial-window driver reading** — rejected. It is a driver change made for a harness's sake, and
  the path limiter no longer needs it (D-6 reads `lag_held` at slot rate).
- **(c) judge the raw measured/commanded pair** — rejected. The measured side *is* the same unfilled window,
  so it fails for the same reason.
- **(b) a not-following case that still completes its window** — **chosen, and built by construction.** The
  LIMITS part commands `LIMTOP_MAX_INCRE` **with the motor's current limits lowered to 1 A**, then puts them back
  and reads them back (`BM-OCLIM`). The over-command alone was not enough: Visit 9 measured three of four
  wheel-directions *following* it by field weakening (2.3–4.2 A), and the fourth falling short only by a slip with
  a ~25 A peak (PL-108). With the current capped, the drive has to fall back to what it holds at 1 A (about 76–80 % of
  the command on Visit 9's figures), while `targetIncre` stays at the command. The driver must read the shortfall
  with a full window, bounded by its own limiter. `test_bench_dual.spin2` judges both limbs with one criterion,
  split by the harness's own verdict: `R18-DUAL-FOLLOW-M` on following readings and `R18-DUAL-FOLFALL-M` below 90 %.
  A reading stuck at 100 fails the second. The same step gives A-8 a not-following case a lifted rig can reach,
  which part D's stall cannot (PL-106). It is also the fold-back's first exercise at a limit a lifted wheel
  actually crosses on the new drive: Visit 8's FOLDBACK passed at 695 mA against an 8 A limit.
- **The scan cell is retired, both instances** (`test_bench_scan.spin2` SRC_REV 20, fmt 12). A cell with one
  limb is the shape D2 forbids. `BS-POINT3` still prints both readings per point.

---

### PL-102 -- a user cannot learn that a motor is not meeting its command

> **AFTER v6.0.0 — STEPHEN 2026-09-27:** *"no public api change"* for 6.0. This entry now also carries PL-160's owner
> Q4 (report a ramp held by the rotor-lag gate): both are one user question, "is my motor doing what I asked?", and the
> candidate answer is one getter (e.g. `isFollowing()` on the motor and steering objects, from state the driver already
> computes), certified under load. 6.0 ships without it. Whether its symptom is listed as a v6.0.0 Known Issue is
> part of Stephen's pending ruling on the DEGRADED list.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (capability not in 6.0)

**Raised 2026-09-22 at «#3596», and parked by Stephen's ruling.** STEPHEN: *"let's keep in test only for
now, and punch-list the possible need thru API."*

The drive now measures whether each motor is turning at its commanded speed -- the hall-tick rate over a
1 s window against the rate the command asks for (`testGetFollowing()`, `isp_bldc_motor.spin2:1468`).
For 6.0.0 it stays TEST-USE: the drive and the steering object act on it internally (the hold at the
achievable rate, and path-preserving speed limiting), and no public member reports it.

**The possible need.** Unloaded the rotor meets its command to 0.2 % everywhere (MEASURED,
`BENCH-LOG-STUDY-2026-09-21.md` §6.1a), so today nothing would report differently. Under load the upper
~45 % of the range runs with no torque margin, and a user's platform will then run slower than commanded
with no way to know it -- nor to tell a struggling motor from a healthy one.

**What it would take:** promote the reading as `isFollowing() : bFollowing, bMeasured`, with `bMeasured`
FALSE until the window has filled, a threshold near 90 % of commanded, and a mirror in
`isp_steering_2wheel.spin2`. Shape and threshold are in `DOCs/plans/DRIVE-INTEGRATION-DESIGN.md` C-6.
**What would reopen it:** a loaded measurement -- the floor run «#3591» -- showing following below the
threshold in normal use, or a user report of the platform running short of its commanded speed.

---

### PL-103 -- the ALIGN band is sized from motion when the bias read lands on a coasting wheel

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree** (`test_bench_dual` SRC_REV 85, the bias read
> taken hall-still). No release plan runs the ALIGN part.

> **Status (2026-10-04):** FIXED IN THE TREE; certified by the next hand run. `test_bench_dual.spin2` SRC_REV 85
> (task «#3694»): a bias read is still only when no phase strays more than `ALIGN_BIAS_STRAY_MAX_MV` (8 mV), and the
> band is sized from the leg's quietest hall-still read when none passes (`alignApplyBias()`); `BM-AGUIDE` gains
> `stray_mV`. The Doco's align leg (`test_bench_single.spin2` L-align) inherits it.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (alignment tier instrument)

**Found 2026-09-22, Visit 7c pass 2** ([evaluation](analyses/bench/2026-09-22/VISIT-7C-PASS2-EVALUATION.md)
§3.4). `R18-DUAL-ALIGN-CLIP` failed five legs across the two runs, and every one had needed bias re-takes
(`bias_tries` 4-22) and came out with a wide hysteresis band (17-58 mV). Every leg whose bias landed first
try got 9-10 mV. `bAlignBias()` calls a read "still" when the **hall code** does not change, but a wheel
still coasting inside one sector passes that test while its back-EMF inflates the stray the band is sized
from. The band then reaches the rail and the leg is refused -- though those legs' Z matches their clean
twins within 0.3°.

**Why not fixed now:** the tier's job for these two motors is done (Z and H-3 answered and reproduced), and
the override rule puts driver work first. **It is needed before the tier's next use** -- the Rev A pair's
Z (manual §9.1) and the Doco motor («#3592»).

**What it would take:** require the read to be still in **voltage** as well as in hall code -- re-take while
any phase's stray exceeds a cap tied to the first-try population (9-10 mV here) -- or size the band from
the quietest of the re-takes. Either is a desk change certified by one hand run.

---

### PL-105 -- the lag limiter holds an overloaded rotor well past its torque peak

> **Status (2026-10-01, phase 2):** **NOT taken up.** PL-167's D-4 (`LAG_HOLD` 100 → 86) failed its desk condition: a
> wheel held at 86 and pushed back one hall sector reads 86 + 42.7, which the 8-bit error wraps to about -127 and the
> fault test (125) trips, so a rocking obstacle turned 9-10 of 16 modelled stands into lag faults (1-4 at 100). The
> fallback, option (c), was part of Stephen's decision. `LAG_HOLD` stays 100; PL-105 stays open for a sub-sector angle.
>
> *Was (2026-10-01):* PARTLY TAKEN UP by PL-167's design, D-4: `LAG_HOLD` 100 → 86, conditional on a desk
> check of the blocked-motor stop on a rocking stand (Stephen 2026-10-01: *"yes A"*). The design's trim fix makes calm
> running peak at 67-76 instead of 71-89, which is what makes a lower hold possible without a sub-sector angle. The
> choices, what they trade, and when to reopen are recorded in `DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md` §7 Q1.
> The full fix, a sub-sector angle, stays out of scope.
>
> *Was (2026-09-26 audit):* ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (study; needs sub-sector angle)

**Found 2026-09-22 at «#3589»**, DERIVED from the desk model (`DOCs/plans/servo-model/`). The model is fitted
to the ladder and START traces, and it puts the voltage at 90° from the magnets when the error is ~56
counts (bracket 52-60).
- In that frame, `LAG_SOFT` (80) is **δ ≈ 124°** and `LAG_HOLD` (100) is **δ ≈ 152°**.
- An overloaded motor is therefore held at roughly **half** the torque it could make, with the rest of
  its current producing none.

**Why not moved now.** The error the thresholds compare is the hall sawtooth, which rides ±21 counts on
the true lag. The shipped steady `err_pk` is already 71-75, so a threshold near the torque peak would trip
in normal running. Placing the hold at the peak needs a sub-sector angle, which «#3589» D-8 does not
integrate for 6.0.0.

**What would settle its cost:** the loaded floor run («#3591») reading current while held. **What would fix
it:** a sub-sector angle -- hall-timing interpolation or back-EMF -- against which the hold is compared.

---

---

### PL-108 -- a rotor that slips out of field-weakened synchronism draws a single ~25 A peak

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (outside the published speed range)

**Found 2026-09-23, Visit 9** ([evaluation](analyses/bench/2026-09-23/VISIT-9-EVALUATION.md) §2.2, F-3). RIGHT forward
at 235 × 10⁶ on the raised duty ceiling: `rate/pred 81.8`, `win_lag,23`, `err_pk,111`, `i_max,3_718` mV (about 25 A
at 150 mV/A), one sample, no fault and no abort (`debug_260922-185255.log`). The same wheel slipped at 245 on the old
ceiling with a small peak. It happens only where duty is pinned and the rotor follows by field weakening, which is
above every published ceiling after «#3605». A user reaches it only by commanding a raw increment.

**Repeated and sustained, 2026-09-23 (Visit 9b, §2, G-4).** The same wheel-direction slipped stepping from 235 to 245
× 10⁶: `tr_err_pk,113`, 9 lag holds, `tr_i_pk,3_495` mV (~23 A), and at least 10 A for the 4 consecutive samples the
harness's abort needs, which stopped it (`BM-ABORT,...,ABS_CURRENT,value,3_599`). No fault. That makes three runs
of three. **True size:** about 23 A for about 8 ms on a bridge whose peak rating is 40 A, stopped by the harness. It
happens only on raw increments above 225 × 10⁶, and the API's own ceiling is now 165 × 10⁶.

**What would make it actionable:** a load whose command can exceed the ceiling (a steering scale-up, or a user
increment) and a trace captured through a slip. The harness's LIMTOP climb stops at the first slip. **Cost if left:**
none inside the published range; unknown outside it.

---

### PL-109 -- the ramp criteria cannot rank ramp rates: A-2's denominator moves, and the speed-down "peak" is the cruise

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed and moot.** The ramp decision was made in 6.0 (DRIVER_REV 38's
> jerk-limited generator at built-in rates). A-2 was re-cut as this entry asked: its reference is steady running
> (`test_bench_dual` SRC_REV 60), judged as the arrival's excess over the steady mean (SRC_REV 78, PL-183). LIMRAMP now
> only traces; no cell ranks ramp rates or takes a speed-down "peak".

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (ramp-rate criteria study)

**Found 2026-09-23, Visit 9** (§3, F-5, F-6).
- **A-2 (START).** It divides the peak by the trace's last 60 ms. At `ramp_inc` 22 and 44 that tail is settled
  quarter-speed current. At 88 the capture ends at the instant of reaching speed, so its tail still carries
  acceleration current. Result: 88 "passed" (1.28–1.44) while 44 failed (1.82 / 1.85). On one settled denominator the
  order is the physical one: 1.3, then 1.5–1.8, then 1.6–2.1. A-2 was built to catch the old start surge, and a
  harder ramp draws more current by design, so it is also the wrong gate for ramp rate.
- **The speed-down criterion** takes the pre-fall cruise current as its "peak", so its own 50,000 control fails
  (4.5–10.7×).

**Fix when E5 is designed:** judge a ramp by what can go wrong with it. That means lag holds (already in `BM-RAMP`),
duty drop, and current **excess above the steady current at the same instantaneous speed**, not above a tail. The
floor run («#3591») is where the ramp decision is made, so the criterion lands with it.

---

### PL-110 -- at crawl speeds duty sits on `duty_min`, and halving it cuts the current 3-13x

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (crawl-duty tuning study)

**Found 2026-09-23, Visit 9** (§4, F-8). At every LIMLOW rung (544,628 down to 100,000) duty reads exactly
`duty_min`: 1,600 as built, 800 halved. Net current falls from 77–96 to 5–31 (mV × 10). Every rung still rotates at
its commanded rate, with the gap spread about twice as wide (for example 250,000: 1,254–1,710 ms against
786–1,998). `duty_min` is `100 << 4 #> (dead_gap / 2) << 4` in `init()`, Chip's original, and the plan marks it
**measure only** (L6).

**What it would take to move it:** loaded evidence that the lower floor still starts and holds a platform. That is
the floor run's crawl. The trade is crawl current against crawl smoothness, and a user feels both. **Cost if left:**
small: about 0.05 A net per motor at a crawl (8–9 mV at 150 mV/A), drawn for nothing. It is a cleanliness question,
not a battery one.

---

### PL-111 -- a serial host cannot clear a protective stop

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT** -- its serial pairs (`serial_certify.py`,
> STEPHEN 2026-10-03: *"we'll likely do a lightweight certify of serial drive too"*): `getprot` reads `0 0` with no stop
> latched, and `protclear` is harmless.

> **Status (2026-10-01):** the serial half is BUILT IN TREE (`protclear`, `getprot`, and the Python client) and
> deferred with serial (PL-148); its "Run-time proof owed" waits for that run.
>
> **6.0 status (2026-09-30):** ✅ API half CERTIFIED — R21-DUAL-PROTCLR-P PASS on floor-obstacle-short (refused −2,001;
> `clearEmergency()` held; `clearProtectiveStop()` 0; the next drive taken). The serial half is not in this release.

**Found 2026-09-23 in «#3515»**, writing the serial interface table from `src/isp_steering_serial.spin2`.

**DERIVED from source:** the serial top-level's command table (`cmdsFirst`, `CMD_*` 0-22) has no command that calls
`clearProtectiveStop()`, and `emerclear` calls `clearEmergency()`, which by its own documented contract does **not**
release a protective stop. So once the steering object latches `ERR_PLATFORM_BLOCKED`, every drive command from the
host is refused (`ERROR drivepwr failed: ERR_PLATFORM_BLOCKED (-2001)`), and the host has no command that can end
it. The only recovery is restarting the P2. There is also no serial form of `getProtectiveStop()`, so the host
learns the cause only from a refused command's reply.

**Why it is a defect, not a missing feature (overlay P3):** the serial protocol is the steering object's interface
for a host, and the steering object promises that `clearProtectiveStop()` releases the latch. The serial form keeps
that promise for `emercutoff`/`emerclear` and breaks it for the protective stop.

**Fix direction:** a `protclear` command calling `clearProtectiveStop()` and replying through `replyWithStatus()`,
and a `getprot` command replying `prot {leftCode} {rightCode}`; the same two in `pythonSrc/`'s demo client; both
rows in `DRIVE-OBJECTS-SERIAL.md`. Compile-checkable; the run-time proof needs the protective stop provoked, which
PL-106 says a lifted rig has not yet done.

**Fixed in tree 2026-09-23 («#3606»):** `protclear` and `getprot` in `isp_steering_serial.spin2` (`CMD_PROT_CLR`,
`CMD_GET_PROT`), `clearProtectiveStop()` / `getProtectiveStop()` in the Python client, both rows in
`DRIVE-OBJECTS-SERIAL.md`. `tools/build-check.sh` 48/48, `py_compile` clean. **Run-time proof owed**: a provoked
protective stop, which waits on PL-106's construction; until then this entry stays open.

### PL-118 -- the board cannot measure a phase short's current: the shunt does not carry it

> **STEPHEN RULED 2026-09-27 (1 A): ships as a Known Issue.** README's v6.0.0 Known Issues states that braking by
> shorting the phases (emergencyCutoff(), a stop held with holdAtStop(TRUE)) is not current-limited, and to ramp down
> before stopping where possible.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (board limit; external sensor)

**Found 2026-09-23** while building Visit 10's fault cells («#3613»).

**MEASURED (record):** the current channel is sensed *"between common MOSFET GND and common system GND"*
(`DOCs/analyses/BOARD-REVISION-FACTS.md` §2.3).

**DERIVED:** in BR_SHORT every low side is on, and the short-circuit current circulates phase to phase through the
low-side FETs and their common source node. It never passes from MOSFET ground to system ground, so the shunt reads
about zero while the short brakes. Consequences:
- the fault study's short-circuit current (tens of amps, modelled in «#3609»'s WHY) cannot be measured on this board;
- the fold-back current limit cannot see or limit it;
- X-2's current comparison is expected to read NOMEAS.

BR_BRAKE's regenerated current, which returns through the supply, is partly visible.

**Owner:** «#3609» phase 3 (the graded response is the only limiter a short has); a measurement would need the
deferred external sensor («#3506»).

### PL-119 -- the offset-shift fault provocation plugs the motor more often than it faults it

> **Status (2026-10-10, burn-down «#3707»): CLOSED.** The fault cells provoke with the guarded `testForceFault()`
> (STEPHEN 2026-09-28, *"fp1: A"*); the offset-shift provocation is used by none.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench fault provocation)

**Found 2026-09-23** while building Visit 10's fault cells («#3613»).

**MEASURED:** of five offset-shift provocations on file, three ended in `BM-ABORT ... reason,ABS_CURRENT` at 3,435,
3,771 and 2,655 mV (about 23, 25 and 18 A), not in a fault:
- `debug_260919-173537.log:2988` and `:3376` (POSTFLT);
- `debug_260919-172908.log:8352` (OVERSHT).

**DERIVED (the agent's trace reading, `debug_260919-173537.log:3041-3052`):** the error landed at -122, the lag
limiter held it just under the 125 fault test, and the stalled rotor drew rising current.

**Disposition:** Visit 10's fault cells use `testForceFault()` (DRIVER_REV 12) instead: a fault taken at the driver's
own fault test, on demand, with no plugging. Parts B and C still use the old provocation, behind the 10 A abort.
Moving them over is a change to certified tiers and is not made here.

### PL-120 -- the right board's bridge puts no voltage on any phase

> **Status (2026-10-13, Rev B evaluation): NOT RECURRED, still a watch.** Every start check took both boards (dual-a
> `R14-DUAL-REVB-A ... measured,0` both wheels; demo-dual `LEFT checked $5F, RIGHT checked $1F`) and both pre-flights
> moved (`BM-PREFLT ... ticks,32,hw_ticks,32,moved,TRUE`).

> **Status (2026-10-10, burn-down «#3707»): A WATCH ON THE REV B CLOSEOUT** -- no start check refuses the right board
> across the session's loads.

> **Status (2026-10-01):** WATCH. No refusal of the right board in the 69 Rev B program loads logged since 2026-09-27
> (35 of them name the right wheel), after Stephen's 2026-09-26 reseat of the board on its headers. The cause is not
> established, so the entry stays open; every run's start check and `T0-25` recovery timer keep watching it.
>
> **6.0 status (2026-09-26 audit):** WATCH (release-relevant) — the right board's high side intermittently delivers no voltage; the start check refuses it correctly (certified); evidence points at the board, not the driver; pass 7 times its recovery.

**Found 2026-09-23** at Visit 10 pass 1 ([evaluation](analyses/bench/2026-09-23/VISIT-10-PASS1-EVALUATION.md) §3.1).
Open. **Rig evidence; Stephen confirmed both boards share one supply (2026-09-23); see the dated updates below.**

**MEASURED:**
- In `debug_260923-160440.log`, every right-wheel phase probe over 10 starts reads 11–27 mV driven, below its own
  56–62 mV coasting floor. The left wheel reads 782–823 mV with the same binary.
- `r_fail,$001C` (all three phases) at every start, while the halls are legal and the board detects as REV_B.
- `debug_260923-160300.log` `BM-PREFLT ... RIGHT ... ticks,0,moved,FALSE`.
- The last right motion on file is `debug_260922-193000.log` `BM-PREFLT ... RIGHT ... ticks,19,moved,TRUE`.

**DERIVED:** the diff `3403024..HEAD` contains no change that acts on one pin base only. The pack pin is P48, outside both motor
groups (P16–P31, P32–P47). The preflight nudge that failed is unchanged since `3403024`, when it moved the right wheel;
only the driver underneath changed (DRIVER_REV 8–12). About 20 mV on a phase driven at 50 % is what a board with no bus
voltage would read.

**STEPHEN 2026-09-23:** *"i changed nothing on the motor boards... you should see them both move if you ask."*

**Reading (a), no supply, is REFUTED.** STEPHEN 2026-09-23: *"both boards are hardwired to distribution, if one gets
power they both do."* So this is a defect in our code, and DRIVER_REV 8–12 is where it entered. Checked and cleared by
reading:
- the parameter and status contract (22 and 20 longs, same order on both sides);
- the LUT loader count (label-derived);
- the pack pin;
- the preflight code (unchanged);
- `forwardIsReverse()` (power sign only);
- every pin write for a pin-base dependence.

**MEASURED 2026-09-23 17:48, `debug_260923-174816.log` (`spin`, current driver):**
- **The right wheel turns and its board is fine**: `SP-PHASE,phase,FWD,wheel,RIGHT,power,50,ticks,-453,...,MOVED`,
  and REV 454.
- Its start check passes: `healthFailed = $0000_0000, ... @probeMv = 789 784 788 788 783 787 788 783 787`.

So the harnesses that fail are the ones that differ. Every one of them (dual, T0) auto-detects the board (`spin`
forces Rev B) and builds with `-D BENCH_QUIET` (`spin` does not). **Both factors are CLEARED:** `spin-auto` and
`spin-quiet` (`debug_260923-180445.log`, `-180517.log`) drove the right 453–454 ticks each way. So the cause is in the
dual (and possibly T0) harness path, and in `dual-start` it shows inside `steering.start()`
([evaluation](analyses/bench/2026-09-23/PL-120-SPIN-EVALUATION.md)). **Next:** «#3615» dumps both drivers' shared runs
at the start check and at the preflight nudge, inside that harness, and lets `dual-fault` carry on with the wheel that
moves. It rides on Visit 10 pass 2.

**2026-09-23 19:23, Visit 10 pass 2 — DID NOT REPRODUCE.** The right wheel drove in every run
([evaluation](analyses/bench/2026-09-23/VISIT-10-PASS2-EVALUATION.md) §3.1, §3.3). Its first `BM-ABI*` dump reads the
same 22 parameters as the left. Everything since pass 1 has run DRIVER_REV 13 and harness src_rev 37–38; pass 1 ran 12
and 36. **Undetermined** between a change in that range and a transient rig state. **Watch:** the dump stays in every
START lifetime and every PREFLT, so a recurrence is captured on its first run.

**2026-09-24 16:15, pass 3 re-run — RECURRED, SECOND FORM** ([evaluation](analyses/bench/2026-09-24/VISIT-10-PASS3-RERUN-EVALUATION.md)
§4). In `dual-fault` the right drove at PREFLT (`ticks,18,moved,TRUE`). Then all 12 of its own-object trials timed out
with the phases at 15–170 mV (`pos,0`). Then it drove again through the steering object at 16:20:47. So this form
follows the left wheel's trials, on the standalone right-wheel path. The shared driver image is **cleared by
reading**. No dump fell in a failing lifetime. **Built:** `test_bench_dual` src_rev 41 dumps the wheel's driver runs at
any FLTRESP timeout (`BM-ABI* where,TIMEOUT`), so the next recurrence is captured while it fails.

**2026-09-24 21:21, Visit 10 `dual-fault` at 62366a5 -- RECURRED, AND THE DUMP LANDED**
([evaluation](analyses/bench/2026-09-25/VISIT-10-DUALFAULT-T0-EVALUATION.md) §4).
- **MEASURED:** the right drove its own trials 13–16 (40 and 80 × 10⁶, two full shorts from speed). From trial 17
  (21:24:33, its first 120 × 10⁶ start) it produced no motion in 8 fresh driver lifetimes.
  - Trial 17's phase reading rose to 2_194 mV as the drive started, then drained to 18 mV within about 200 ms while
    duty rose to 5_101. The DC-link current stayed at 0–9 mV throughout.
  - Trials 18–24 read 30–50 mV from their first frame (`BM-TS ... ph`).
  - The protective stop latched about 1 s into each: the TIMEOUT dump reads `drv_state,7`, `e_stop,-1`, `pos,0`,
    `lag_held,1_852`.
  - The closing platform trial (steering) at 21:26 shows the right at 14 ticks/s against the left's 217.
- **Then at 21:29, in a fresh program load (`t0-stopmode`), the right drove normally**, powered rows included.
- **CLEARED:**
  - *Orphan cogs:* every lifetime's driver took cog 3 and its front cog took cog 4 (`Cog3/Cog4 INIT`). A leftover cog
    would have pushed them to 5 and 6.
  - *The LA marker pins:* every use is inside a `{ ... '}` comment block (no symbol in the compiler listing).
  - *Board detection leaving a pin driven:* `pinfloat()` always follows `pinhigh()` after 1 ms.
  - *A supply loss:* ruled out by Stephen's rig fact (one distribution).
- So the failing state survives driver restarts within one program and is gone after a reload. **Undetermined**
  whether time or the reload clears it.
- **NEXT (built for the next pass):**
  - A dump at the first 150 ms of commanded drive with no hall tick, before the protective stop overwrites the state.
  - A same-run recovery probe after a no-motion failure: a 2 s drive at 40 × 10⁶ in a fresh lifetime every 20 s for
    2 minutes, logging phase voltage and current. It decides time against reload.
  - A `dual-fault-rightfirst` tier, which decides whether the left's trials are a precondition.

**2026-09-25 11:41, pass 4 `dual-fault-rightfirst` at 2783921 -- RECURRED ON THE FIRST DRIVE OF A FRESH LOAD**
([evaluation](analyses/bench/2026-09-25/VISIT-10-PASS4-EVALUATION.md) §2, §4).
- **MEASURED:** `BM-PREFLT,...,motor,RIGHT,...,ticks,0,hw_ticks,0,moved,FALSE`, before any left trial. The wheel was
  retired, so all 12 right trials and both platform trials printed `NOT_RUN ... MOTOR_RETIRED`.
- **MEASURED:** its PREFLT dump shows `lag_held,637` and `duty_capped,1_474`. The same wheel's five healthy PREFLT dumps
  show 0 and 165–189. Every parameter matches the healthy dumps.
- **MEASURED:** the next program load, 3 minutes later (`dual-start`), drove the right normally in every lifetime.
- **Settled:** the left's trials are **not** a precondition.
- **Corrected:** "gone after a reload" was too strong, but this run shows only that **one** drive failed. The harness
  started the right once and never retried it (PL-136), so a transient first-drive failure is not ruled out. The next
  two program loads turned the right in every start: 20 starts, 6 walk legs, 36 winding pulses.
- **Still open:** whether time clears it inside one program, and what the phases do during the failing drive. Neither
  diagnostic could fire (PL-136).

**2026-09-25, desk read of the pin path (read-only survey).**
- **The pin set-up has no dependence on the pin group:**
  - pins base+8..13 are u_l, u_h, v_l, v_h, w_l, w_h;
  - the high sides run in `pwmt`, the low sides in `pwmn` (inverted);
  - dead time is in software;
  - only the driver cog writes them, and every bridge state writes Y only.
  Nothing else in `src/` touches P16–P47. So no code path found treats base 16 differently from base 32.
- **The measured levels contradict the "low sides off" hypothesis** stated in the pass 4 evaluation. Two readings
  sit below the right's own 56–62 mV coasting floor:
  - the lead probe's 11–27 mV driven (pass 1);
  - the 18 mV drain at 21:21, with duty in BR_DRIVE.

  Only a conducting low side pulls a phase below the float level. **DERIVED, moderate confidence: the high-side
  drive is what fails.** Candidates:
  - the Rev B high-side gate supply or bootstrap/UVLO on the right board;
  - the high-side outputs P25, P27 and P29 not reaching it.
  The one fact against hardware is that a later load has always cleared it.
- **Survives a driver restart, not a reload, and is not in the dumps:** the shared driver image (`bias`, `fram`,
  `hall_angles`, `deltas`), which both motor instances share and `init()` rewrites before each launch. **Next dump
  should carry these.**
- The pass 5 sheet's signature row was corrected to this reading before any pass 5 log was read.

**2026-09-25 19:52-20:11, Visit 10 pass 5 at 24d2cb9 (DRIVER_REV 25) -- STRUCK TWICE AFTER DRIVING, OUTLASTED A RELOAD,
AND START REFUSAL CAUGHT IT** ([evaluation](analyses/bench/2026-09-25/VISIT-10-PASS5-EVALUATION.md) §2, §3).
- **MEASURED, the fault tier did not see it:** `dual-fault-rightfirst` `BM-FRRECSUM,...,r_pf,NO_FAIL`. The right drove
  all 13 of its own lifetimes (40-120 × 10⁶, shorts, coasts, graded shorts) and both platform trials.
- **MEASURED, death 1 (`dual-start`, about 20:05:04):** life 5's walk BACK leg, right
  `end,OTHER,...,peak,0,...,lag,325`. The left was healthy but scaled by the path limiter, `peak,-3`. Lives 6-10: every
  start refused after its 3 retries (about 4.0 s each):
  `BM-SREFUSE,...,r_err,-1_020,...,r_fail,$001C`, with the left clean (`l_fail,$0000`).
- **MEASURED, death 2 (`dual-d`, between 20:10:22.9 and 20:10:29.2):** after ESTOP_LATCH/ESTOP_CLEAR the platform never
  reached speed. Then ORDERED..DIRSIGN were `NOT_REACHED`, `BM-EVTOT ... l_path,2,r_path,56`, and the LIMIT segment's
  start was refused, `r_fail,$001C`.
- **MEASURED, a reload did NOT clear it:** `t0-stopreason`, a fresh program load at 20:11:43 (about 80 s after death 2),
  was refused at its first start: `healthFailed = $0000_001C`. **This falsifies "a later load has always cleared it"**,
  the one fact recorded above against a hardware cause.
- **MEASURED, time did:** `dual-start-phaseneg` loaded about 100 s after death 1 and probed the right healthy in every
  lifetime (`p_uu,796 ... p_ww,798`).
- **So:** the failing state survives driver restarts **and** a program reload, and clears within about 80-100 s. That
  weighs against anything the program image holds (the shared driver image included, which the reload rewrites) and
  toward a state in the right board that recovers with time. A time-recovering high-side gate supply fits the corrected
  reading.
- **The probe fits the corrected reading, but the signature was not printed.** The lead probe drives each phase's high
  side at 50 % (`probeLeads()`), and all three failing means no high side raised its phase. But the harness read probe
  mV only when `start()` returned a cog, so the refused starts printed NA. **BUILT 2026-09-26:** `BM-RPROBE` after every
  refusal (`test_bench_dual` src_rev 49), and `test_bench_t0` src_rev 19 prints `T0-25,rprobe` and then falls back to
  the LEFT wheel, so the next death records its per-phase millivolts and voids nothing.
- **Still open:** the trigger (both deaths followed ordinary driving, one right after an e-stop; the fault tier's harder
  use did not trigger it), and whether the board or our pin handling holds the state.
- **2026-09-26, rig fact from Stephen:** the RIGHT motor had a weak connection, found several runs ago. He re-checks it
  before pass 6.
  - All three phases failing at once fits a shared path better than one phase lead: the board's supply or ground, or
    the high-side gate supply. Recovery with time fits an intermittent contact.
  - **Pass 6 will be confounded.** The reseat and three driver-side changes (PL-138 parts 1-2, PL-141) land together.
    A pass with no death clears neither by itself. The reading that tells them apart is the next death's
    `BM-RPROBE` / `T0-25,rprobe` signature, if one comes. PL-138's all-low-sides window
  touches this path and is the next driver-side candidate.

**2026-09-26 12:33, Visit 10 pass 6 -- RECURRED on the first load after the reseat, WITH its signature**
([evaluation](analyses/bench/2026-09-26/VISIT-10-PASS6-EVALUATION.md) §3).
- **MEASURED:** Stephen remade and checked every right-motor connection before the pass. The first program load
  (`t0-stopreason`, DRIVER_REV 29, so PL-138 parts 1-2 and PL-141 in the image) was refused:
  `T0-25,refused,wheel,RIGHT_P16,chk,$1F,fail,$1C,rec,$0`, after 3 retries.
- **The per-phase signature, first time printed:** `T0-25,rprobe,driven,0,u_mV,20,v_mV,17,w_mV,19`,
  `driven,1,...,20,16,19`, `driven,2,...,20,17,20`. Every phase reads 16-20 mV **with itself driven**: below its own
  56-62 mV coasting floor, where a live lead reads 777-823 mV. No high side raised its own pin.
- **MEASURED, back by 12:35:18** (under 2 minutes): `dual-start` started the right healthy in all 10 lifetimes (probes
  from 789 mV, walks 7/-7, windings 345-431 mΩ), and it stayed healthy for the rest of the pass.
- **DERIVED, the connection reading weakened:** a motor lead cannot lower the voltage on the board's own driven pin, so
  a loose phase connection at the motor does not produce this signature, and the reseat did not prevent it. What fits
  is the board's high-side drive (gate supply or bootstrap) not switching, and recovering within ~2 min. Pass 4's death
  (11:41) was also the day's first load. **Not established:** whether the pack had just been connected in either case,
  since nobody was asked to note the power-on time.
- **Also refuted as the trigger:** PL-138's all-low-sides windows (removed at DRIVER_REV 27/29, in this image).
- **Built for pass 7:** `test_bench_t0` SRC_REV 20 times the recovery. After a refused right and the left's cells,
  it tries the right every 10 s for up to 3 min, with each try's per-phase readings (`T0-25,recover` / `recovered`).
  The pass 7 sheet asks Stephen, in advance, to note when the pack is connected.

**2026-09-26 night -- a supply we never checked, and the board reseated on its headers.**
- **MEASURED (record):** the gate drive does not come from the pack. On Rev B it is 12 V from a switching boost
  regulator fed by the P2's **VIO3V3 pin on the upper accessory header**, rated 50 mA, shared by all four half-bridges
  (BOARD-REVISION-FACTS.md §2, the manual text Stephen supplied). The 2026-09-23 refutation ("both boards share one
  pack") covered the bus, not this supply.
- **DERIVED:** a gate supply that is dead or restarting fits the whole signature: all three high sides dead at once,
  halls and phase sensing unaffected, recovery within minutes, and code identical on both boards. A marginal header
  contact or a regulator dropping out fits the timing. It is not established.
- **STEPHEN 2026-09-26:** *"i'll reseat the board on the headers (i only did motor to board) then we'll monitor..."*
  From the next run, a PL-120 episode is read against that reseat. T0-25's recovery timer records any episode's length
  with no extra load.

**2026-09-27, Visit 10 pass 7 (2026-09-26 17:42):** the board was reseated on its P2 headers beforehand. The pack was
connected at 17:41:56 (`pack-connect-now.txt`) and the first load came 37 s later. The right started first time in
every lifetime of every tier. One clean pass after a reseat is one observation, not a fix: **Watch**.

### PL-126 -- the P2's output stopped mid-record 2 s into right trial 19, and the wire then carried lone zero bytes

> **Status (2026-10-13, Rev B evaluation): NOT RECURRED (and PL-43 with it), still a watch.** All 8 Rev B logs reach
> their end record; the eight 292-byte logs are the terminal's header before each download.

> **Status (2026-10-12, D7 evaluation): NOT RECURRED, still a watch.** All 13 D7 runs (about 75 minutes on the Doco
> bench) end in `B1-END,abort,NONE`. The two 292-byte logs (`debug_261012-171850.log`, `-173149.log`) are the
> terminal's session header before a download, as D6's `-130447.log`: no run, each followed at once by the full run.
> The sheet's two observations (power light, supply current) were not needed. The Rev B session carries the watch.
>
> **Status (2026-10-12, D6 evaluation): RECURRED ONCE, still a watch.** `debug_261012-133443.log` (24 V ramp, Rev A,
> the Doco bench, a different rig from 2026-09-24's): 5.4 s into the POS climb the stream turned binary at 13:35:21.2
> and stopped; the next two downloads found no P2 ("No Propeller v2 device found"); the third ran, and the rerun
> completed. A reset, a supply loss or a USB drop: not separable. The next sheet asks in advance for the power and USB
> history around one (dual-agent-handoff overlay O5).
>
> **Status (2026-10-10, burn-down «#3707»): A WATCH ON BOTH CLOSEOUTS** -- every log runs to its end record.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench watch, one instance)

**Found 2026-09-24** in the first `dual-fault` try of pass 3 (evaluation §3). This ran the pass 2 binary.

**MEASURED:** the last record is `BM-START,seq,4_886,...,RIGHT,life,23` at 13:42:15.410. Then
`usb-traffic_260924-133841.log` shows `$20 $00` at 13:42:17.554 and four lone `$00` bytes over 49 s. No other capture in
the set holds one. The harness watchdog printed nothing. The rerun and pass 2 both passed the same trial.

**Undetermined:** a P2 reset, a supply loss, or a hang with its TX line disturbed. The log cannot separate them.
**Watch:** the next run sheet says in advance what to look at if the log stops scrolling. A second instance, or that
observation, makes it actionable. Owner: each visit's log analysis (now «#3634»; «#3613» closed 2026-09-30).

### PL-134 -- HOLD-RISE's rate estimate kept counting after the hold slipped

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree** (`test_bench_t0` SRC_REV 17). No release plan
> runs `t0-stopmode`.

> **Status (2026-10-01):** FIXED IN TREE, not yet run: no `t0-stopmode` run since the 2026-09-24 log that found it, and
> no plan runs one.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench estimator)

**Found 2026-09-24** at `t0-stopmode` 21:29 (`debug_260924-212939.log`, row 1 run 1). `rise_ms,16_539`: he pushed past the
hold, it slipped at 2_328 ms with the duty frozen at 2_684 (ceiling 2_764), and the wheel stayed displaced for seconds.
Pairs with no duty gain piled up time. Up to the slip, the rate reads **251 ms**, the same as runs 2 and 3 (250, 249).
The cell's FAIL for that run was right (the hold gave way before its ceiling). The printed number was not.
**FIXED** (`test_bench_t0` SRC_REV 17): a pair counts only while `getHoldStatus()` reads HS_HOLDING at both ends.

### PL-135 -- a card that asks for a deliberate act does not get it: the interaction's negatives are still unmeasured

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed in the tree.** The fix below is built (`test_bench_t0`
> SRC_REV 17, the panel tests in `t0sTestTab`: the grey box logs `hit,MISS`, row 4 draws REDO ROW only, row 6 ABORT then
> REDO ROW). No release plan runs the attended `t0stop` tier.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench interaction negatives)

**Found 2026-09-24**, same run. Rows 1, 4 and 6 now asked on their cards for the three acts that make UI-MISS, UI-REDO and
UI-ABORT able to fail (PL-131). None was made: no `hit,MISS` input, row 4 ran once, and row 6 took no ABORT. A line of
card text competes with the row's own instructions and is read past.
**FIX, correct by construction:** the program *requires* each act on the first run of its row, and draws only the
control that performs it.
- Row 1's intro screen shows no START ROW until one click lands on the marked empty area, which reads `hit,MISS`.
- Row 4's first RESULT draws REDO ROW only.
- Row 6's first run draws ABORT as its only control, and its RESULT draws REDO ROW only.
- Each screen says in one line why it asks.
Later runs of those rows are unchanged.

### PL-136 -- PL-120's diagnostics are reachable only from a fault trial, so a wheel dead at PREFLT is never diagnosed

> **Status (2026-10-13, Rev B evaluation): NOMEAS, still a watch.** No pre-flight failed in the session, so no
> `BM-PFRETRY` was printed; it certifies itself on a wheel's first PREFLT failure.

> **Status (2026-10-10, burn-down «#3707»): A WATCH ON THE REV B CLOSEOUT** -- built; it certifies itself on a wheel's
> first PREFLT failure (`BM-PFRETRY`), and is owed nothing while no wheel fails.

> **Status (2026-10-01, closeout):** BUILT 2026-09-25 (`test_bench_dual` SRC_REV 46) and never provoked: no wheel has
> failed PREFLT since, and no log on record carries `BM-PFRETRY`. ANCILLARY (bench diagnostics): it certifies itself the
> first time a wheel fails PREFLT.
>
> *Was (2026-09-26 audit):* ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench diagnostics)

**Found 2026-09-25** at Visit 10 pass 4 ([evaluation](analyses/bench/2026-09-25/VISIT-10-PASS4-EVALUATION.md) §4a).
The right wheel failed PREFLT. `BM-FRRECSUM,...,probed,FALSE`, and no `where,NOMOTION` dump fell on it.
- Both diagnostics are reached only from `frTrial()`: the NOMOTION dump through `frWaitAtSpeed()`, the recovery probe
  through `bTimedOut`.
- `bSegPreflight()` retires a non-moving wheel before FLTRESP, and its trials are then skipped.
- `bPreflightWheel()` also drains the instrument ring to count ticks but never emits it, so the failing drive's
  per-frame phase voltage, current and duty were measured and discarded.
- The run sheet and the runner's precondition text both promised the probe "if a wheel stops driving". The build did
  not keep that promise.

**Disposition:** ⛔ **FIX** in `test_bench_dual`, correct by construction. The diagnostics key on *a commanded wheel that
does not move*, wherever it happens:
- a PREFLT nudge with no hall tick by FR_NOMOTION_MS dumps (`where,NOMOTION`) mid-nudge;
- a PREFLT that fails emits its ring as a trace;
- **first, PREFLT retries the non-moving wheel at once**, in 3 fresh lifetimes about 1 s apart, each dumped and traced
  like the first. Pass 4 started the right exactly once (`BM-START ... motor,RIGHT` occurs once in the log), so one
  failed attempt could not tell a transient first-drive failure from a persistent one. Stephen, 2026-09-25: *"the
  right wheel is turning and providing results in the other two tests.... so maybe didn't retry?"*;
- only if all of those fail, arm the recovery probe on that wheel (20 s gaps), run before FLTRESP.
A wheel either stage recovers is un-retired and runs its trials. Rides on the next `dual-fault-rightfirst`.

**2026-09-25 -- BUILT (not yet certified).** `test_bench_dual` SRC_REV 46, FMT 30; no library object changed.
- **Every part's PREFLT:** the nudge's wait is `waitWatchedNoMo()` (FLTRESP's NOMOTION loop, moved out of
  `frWaitAtSpeed()` unchanged), so a nudge with no hall tick by FR_NOMOTION_MS dumps `BM-ABI* where,NOMOTION` mid-nudge.
  A nudge that does not move emits its ring as a trace (`BM-TRACE seg,PREFLT,cause,START`, `BM-TS`, `BM-TRACE-END`),
  drained before any fault recovery re-arms the ring. In FAULTRESP every nudge is traced, so a moving wheel's nudge is the
  in-run control.
- **The three phases:** the ring always stored u, v and w apart (`instPackSense()`); `BM-TS` printed only their sum.
  `BM-TS` now appends `u`, `v`, `w` (mV, NA when the driver is down), in every trace.
- **FAULTRESP only, the stages:** a wheel whose nudge does not move is retried at once in PF_RETRY_TRIES = 3 fresh
  lifetimes, PF_RETRY_GAP_MS = 1 s apart, each nudged, dumped and traced like the first. New record **`BM-PFRETRY`**
  (motor, try, life, ms from the first failure, moved, ticks, hw, tid of its trace, why). Only if every retry fails,
  and it is the only such wheel, the recovery probe runs on it before FLTRESP (`BM-FRRECOV` gains `seg`, here `PREFLT`).
  A wheel either stage moves is not retired. Its cells read NOMEAS while the stages run and live again when one moves;
  `bSlotRetired` is set only after both fail, since it would refuse the retries' own starts. FLTRESP's own probe keeps
  its one turn.
- **Records:** `BM-FRRECSUM` gains `l_pf`/`r_pf` (NO_FAIL, RETRY, PROBE, DEAD, UNDECIDED), `l_pf_rec`/`r_pf_rec`
  (TRUE, FALSE, NA only when nothing was decided), `l_pf_n`/`r_pf_n` (retries made) and `l_pf_try`/`r_pf_try`. Its
  `recovered` and `tries` now print NA when the FLTRESP probe did not run (they read FALSE and 0: silent zeros).
  `BM-FRDIAG` gains `pf_tries`, `pf_gap_ms`.
- **Why the stages are FAULTRESP's only:** every other part ends its run on a PREFLT failure by contract. A retried wheel
  would be measured there as though it had not failed. The dump and the trace change no outcome, so they run
  everywhere.
- **Compiled** (pnut-ts 1.55.8, scratch copy, first dual config block, the runner's `-D` sets): `dual-fault` and
  `dual-fault-rightfirst` 133_736 plain / 141_175 with `-d`, DEBUG footprint 7_439 (limit 12_404, unchanged from src_rev
  45). Style gate PASS.
- **Worst case, `dual-fault-rightfirst`:** about 6 minutes planned; plus about 2.2 minutes for a wheel dead through
  PREFLT (retries of about 15 s, then the probe's 2 minutes); plus 2.2 more if a wheel then dies mid-run. At most about
  10.5 minutes, under the 15-minute cap.

### PL-139 -- RESTFLAT's 50 mV at-rest band was set on the left board, and the right's coast rest read 51

> **Status (2026-10-10, burn-down «#3707»): FIXED at the desk, by its first stated fix.** The coast's REST window was the
> rest-confirmation interval itself, where a rotor that has just stopped crossing hall edges still rocks in its sector.
> `test_bench_dual` SRC_REV 87: the window opens where rest is confirmed (`REST_CONFIRM_MS` after the last tick,
> `FR_REST_CONFIRM_SAMPLES`) and the capture runs `FR_REST_WIN_MS` past it, the length of the control before spin-up.
> `FR_FLAT_MV` is unchanged; nothing was sized from these readings. Runs in `dual-fault`, which no release plan runs.

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench cell band, watch)

**Found 2026-09-26** at Visit 10 pass 5 ([evaluation](analyses/bench/2026-09-25/VISIT-10-PASS5-EVALUATION.md) §2).
- **MEASURED:** `R19-DUAL-RESTFLAT-X` RIGHT FAIL, 1 of 6 windows. It is trial 5 (X-3, coast from −80 × 10⁶), REST
  window: `BM-FRPHASE,...,tid,5,motor,RIGHT,win,REST,n,154,ticks,0,pp_u,35,pp_v,51,pp_w,23,...,flat,FALSE`.
  `FR_FLAT_MV` is 50.
- The right's other X-3 rest windows read 40 and 15 mV peak to peak. The left's read 38, 19 and 38.
- No hall tick moved in the window. The swing is under one hall step of rotor settling after a free coast.
- **The verdict stands (D2):** the criterion was fixed before the run.

**Why it matters:** RESTFLAT is COASTEMF's negative control. A band that the healthy right touches at rest cannot
separate "flat" from "turning" on that board with margin.

**Disposition: Watch.** It bears on the coast measurement's control, not on any fault response. What would make it
actionable is a second right rest window over 50 mV with no tick. The band is then sized from both boards' rest
windows, never from one run's worst. The next `dual-fault-rightfirst` carries it as is.

**2026-09-27, RC pass: second occurrence, now on the LEFT** (`debug_260927-141904.log`): `BM-FRPHASE,...,tid,3,motor,LEFT,
win,REST,...,ticks,0,pp_u,35,pp_v,52,pp_w,30` after a free coast from −40M; RESTFLAT LEFT 1 of 6. The actionable
condition in the disposition is met in form (a second >50 mV window with no tick), on the other board. It stays
ANCILLARY under the 6.0 rule: the band belongs to the coast measurement's negative control, not a 6.0 feature. The fix,
when taken: start the rest window after the rotor has settled by a derived time, or size the band from the physics of a
rotor rocking inside one hall sector — never from these readings.

### PL-148 -- the serial control path has never run on hardware

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT.** The serial deferral below was superseded
> by STEPHEN 2026-10-03 (*"we'll likely do a lightweight certify of serial drive too"*, DOCO-AND-CLOCK plan): the
> closeout's serial pairs run `serial_certify.py`'s cells at 270 MHz and the clock floor, plain and debug builds.

> **Status (2026-10-01):** DEFERRED to the serial release (STEPHEN 2026-09-27: *"serial testing not in this initial
> release"*). The "release work" disposition below is aged. Every serial build it would exercise is in the tree
> (PL-111, PL-154, PL-157); this entry is the host-driven hardware run they all wait for.
>
> **6.0 status (2026-09-26 audit):** RELEASE — a shipped deliverable with no hardware evidence.

**Found 2026-09-26** by the release audit (a read-only survey of every 6.0 feature against the bench evaluations).
- `isp_steering_serial.spin2`, `DRIVE-OBJECTS-SERIAL.md` and `pythonSrc/P2-BLDC-Motor-Control-Demo.py` are 6.0
  deliverables. So are the serial lines in the README: refusals reply with the error's name and code, and there are
  `settimeout`, `getvoltage`, `protclear` / `getprot`, `setfaultresp` / `getfaultresp`.
- **No bench log mentions the serial object or the Python demo.** Their only evidence is the compile gate and
  `py_compile` (PL-111).

**Disposition: ⛔ release work.** A host-driven run: an RPi or PC running the Python demo against the dual platform,
wheels up. It must exercise a refused command (error reply), `settimeout` with a silent host, `getvoltage`,
`setfaultresp`/`getfaultresp`, and `protclear` once PL-106 can provoke a protective stop. Needs a run sheet and
Stephen's host.

### PL-154 -- the serial path: hold cannot be set from the host example, every command can wait 1 s, and non-numbers become numbers

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT** -- the serial pairs' NUMPARSE and LATENCY
> cells (PL-148).

> **Status (2026-10-01):** BUILT IN TREE; the hardware run is deferred with serial (PL-148). The idle loop now waits
> `IDLE_POLL_MS`, not 1 s (`isp_steering_serial.spin2:296`), and a non-numeric parameter is refused
> (`isp_queue_serial.spin2:295`). The "⛔ build" disposition below is aged.
>
> **6.0 status (2026-09-26 audit):** RELEASE — the serial path is a deliverable; the 1 s wait also delays `emercutoff`.

**Found 2026-09-26** by the public-API audit (API-2, API-3 and API-10; API-2 and API-3 VERIFIED in source) and the
serial certification build.
- **API-2 — WITHDRAWN 2026-09-26, the premise was wrong.** The claim was that `holdAtStop()` sends `hold False` and
  the P2 rejects it. In fact the parser matches `true`/`false` case-insensitively before the number path
  (`isp_queue_serial.spin2` ~:798-800, `bStrHasLowCasePrefix`), so `hold False` always worked. The audit marked it
  VERIFIED having read only the number path, and I relayed that to Stephen as verified. The build found it. The
  wrapper now sends -1/0 anyway, which is harmless, and the words stay accepted as the documented form.
- **API-3:** `isp_steering_serial.spin2` ~:233-234 runs `waitms(1000)` whenever its queue is empty, which is the normal
  state between a host's commands. Every command can wait up to 1 s, `emercutoff` and `stopmotors` included, and a
  `settimeout` under about 2 s cannot be kept alive.
- **API-10:** any non-numeric parameter is silently turned into a number.
- **Serial doc gaps:** three undocumented ERROR forms (`isp_queue_serial.spin2` ~:252, :277, :284); how a host learns of a
  timeout (`geterror` -1019, stop reason 46) is not documented; the doc's example quotes the wrong message text.

**Disposition: ⛔ build.** The wrapper sends -1/0; the loop polls its receive queue at about 1 ms; parameters must be
digits or a leading minus, else ERROR; the doc says all of this. Certified by `pythonSrc/serial_certify.py` (PL-148).

### PL-157 -- the serial protocol and the Python host example have not kept up with the 6.0 getters

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT** -- the serial pairs' GETTERS cell (PL-148).

> **Status (2026-10-01):** BUILT IN TREE; the hardware run is deferred with serial (PL-148). The getters the list
> below names are in the command table (`getpackvolt`, `getcurrent`, `getfaultcause`, `getholdstatus`,
> `gethallcounts`, `getstopreason`, `getevent`, `geterror`, `gethealth`, `getfaultresp`, `getholdlimits`, …;
> `isp_steering_serial.spin2:87-116`). The "⛔ build" disposition below is aged.
>
> **6.0 status (2026-09-26 audit):** RELEASE — STEPHEN: *"when we added getters, we should have been keeping our serial
> interface up to date"* (API-9, API-13).

**Found 2026-09-26** by the public-API audit.
- **Serial lacks:** pack voltage, current, fault cause, hold status, hall counts, `checkWiring`, `setStartChecks`.
- **The Python example lacks:** stop reason, events, `geterror`, health, fault response and hold limits.

**Disposition: ⛔ build.** Every user-facing getter, and every setter a host needs, has a serial command, a
DRIVE-OBJECTS-SERIAL.md row and a Python wrapper. Measured speed is **not** in 6.0 (STEPHEN: *"I'm not saying add
measured speed right now"*); `getPower()` reports what was commanded.

### PL-164 -- the driver's supported clock range is one point, 270 MHz; users choose their own clock

> **Status (2026-10-13, Rev B evaluation): OPEN, all but one reading certified.** At 130 MHz on the 6.5″: the frame and
> drive pass right (`BM-CLOCK ... frame_cnt,2_954,exp_fram,2_954,pass_us,523,fram_ok,TRUE`, both wheels), halls clean,
> Tier 0 30 of 30 PASS with the dead gap 34 ticks (261 ns) and the sense noise 0.7-2.9 mV. The steering front cog's worst
> pass was not printed by the tier (PL-227); this closes with it.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT** -- the clock-floor rows (`dual-clock
> clk-floor`, `t0 clk-floor` at 130 MHz): the front cog's late count 0 and worst pass under 900 us with two wheels;
> the clock work itself is the DOCO-AND-CLOCK plan's (STEPHEN 2026-10-03: *"this driver is just supposed to work a
> users selected clock range"*).

> **Status (2026-09-27):** AFTER v6.0.0 — STEPHEN: *"user gets to chose clock freq to run their system. we need to be as
> capable as possible at a wide clock range... seems we need a post v6 study wherein we identify our limits/senitivities
> and move what we can by adjusting code to widen our supported range. it ships at v6 as stated testing conditions."*

**What is known (DERIVED unless marked):**
- The front cog's 1 ms pass scales with the clock: 533 µs worst MEASURED at 270 MHz would be ~900 µs at 160 MHz,
  against its 950 µs budget (PL-161's note).
- The driver's PWM frame and stop-planner stages fit at 160 MHz (worst stage 60.5 % of the frame, `tools/pasm_equiv`).
- PL-50: the 23-frame drive pass can be 22 frames at clocks that are exact multiples of 44 kHz (176, 264 MHz).
- Every demo and every bench pass ran at 270 MHz; `dual-clock-200/270/300` tiers exist for the frame constant only.

**The study:** find each clock-sensitive budget (front-cog pass, PWM frame and planner stages, drive-pass framing,
ADC periods, serial and debug timing), derive its limit, then move what code can move so the supported range widens;
certify at the range's ends. README states v6.0.0's supported condition (270 MHz).

### PL-165 -- the DEBUG footprint gate counts every -d-only byte, not only the debug records that can be lost

> **Status (2026-09-28):** AFTER v6.0.0 — found while fitting the RC demos.

**Found 2026-09-28.** The gate's footprint (PLOT-DISPLAY-RULES.md §1) is the `-d` image minus the plain image. The
hazard it guards is narrower: debug RECORDS past image offset 13,684 are cut or never sent. Code that exists only in
`-d` builds (e.g. helper bodies inside `#ifdef __DEBUG__`) is ordinary bytecode, yet it counts against the limit, so
gating a demo's line-builders out of plain builds (about 1.3-3.5 KB saved there) would cost the same bytes of margin.
**MEASURED** (scratch, demo-rc): ungated 10,488 footprint; demo helpers gated 11,504; demo and flysky gated 11,800; the
`-d` image identical (58,204) in every variant. **Not established:** where pnut-ts places `-d`-only code relative to the
debug record table. Settling that from a `-l` listing, then measuring the records themselves, would let plain builds
drop the builders without losing margin. v6.0.0 keeps the builders in both builds (under 1 % of hub RAM).

### PL-166 -- the ramp's rates take no account of the platform's mass (PL-160's owner Q5)

> **Status (2026-09-28):** AFTER v6.0.0 — STEPHEN: *"Q5: A"* (no inertia term in 6.0).

The acceleration and deceleration rates are rim rates in mm/s², the same whatever the robot weighs. On a heavy platform a
high rate asks for more current than the motors can give; the rotor-lag gate eases the ramp off or fold-back caps the
current, so nothing faults, but the robot accelerates more slowly than the rate set and the program is not told why
(PL-102 carries the "not told" half). The candidate: a platform-mass constant in the user config (0 = no cap) from which
the driver caps each rate at what the current limit can deliver, validated on the floor at known masses.

### PL-170 -- on Rev A the fold-back's noise margin is sized for ±3 mV, and the board reads 7
> **Status (2026-10-12, D6 evaluation): CLOSED, CERTIFIED** -- every hand-load step latched 999-1,054 ms (band
> 988-1,168) and held its limit, at 11.1 V (4 A, 2 A, default) and 24 V (4 A, 2 A) (`analyses/bench/2026-10-12/
> D6-EVALUATION.md`, `debug_261012-132446.log`, `-132655.log`).
>
> **Status (2026-10-12, D5 evaluation): HALF CERTIFIED.** 11.1 V: the 4 A and 2 A steps latched at 1,138 and 1,017 ms,
> the limit held (PASS). 24 V: the 4 A step never latched (PL-223, a driver fix at DRIVER_REV 61) and the 2 A step's
> reading was a harness reference error (PL-223). Both hand-load rows go on the D6 confirm sheet.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE DOCO CLOSEOUT** -- the hand-load rows with a grip (PL-210):
> at a 2 and a 4 A limit the gripped shaft stops (`R23-SGL-BLKSTOP` measured and PASS) and no fold fires while it turns
> free. D2's 24 V noise capture and `R23-SGL-LIMHOLD` PASS at 4 and 2 A showed only "no fault".

> **Status (2026-10-05, later): FIX BUILT, DRIVER_REV 55 («#3699»), awaiting D2.** Rev A's fold-back now compares a
> filtered DC-link reading (16-frame time constant) against a 3 mV floor, with a one-frame hard trip 14 mV over the
> threshold; Rev B's shift is 0, so its folds are unchanged frame for frame. The values are DERIVED on the premise that
> the noise is independent frame to frame; D2's per-frame capture (`B1-NOISE`, single-measure's first leg) tests the
> premise and sizes the window, and D2's hand-load cells at a low limit certify it. **To close:** both.
> **2026-10-06 — the premise MEASURED (D2 row 1, `B1-NOISE`, 11.1 V):** one frame's sd 0.50 mV coasting, 0.61–0.64 mV
> driven (4.8 mV peak to peak); neighbouring frames anti-correlated (lag-1 −0.19..−0.26), a slow wander of ~0.2–0.3 mV.
> A 16-frame average leaves < 0.4 mV against the 3 mV floor: the values hold, with margin. The 1.5–2.3 mV above was an
> over-statement. Remaining: the 24 V capture and the hand-load cells.
>
> **Status (2026-10-05): OPEN — measured again, now with a motor that draws real current.** Still reaches only TEST
> USE limits (`testSetCurrentLimits()`; no public method sets a limit, so a user runs at 40/27 A, ~15 mV on Rev A).
> D1b's second pass ran the Doco on a Rev A board at a 2 A test limit (`DOCs/analyses/bench/2026-10-05/
> debug_261004-213146` .. `-230018`, `debug_261005-002048`): the Doco's unloaded draw (0.2-0.5 A, 1-2.5 mV) lifts the
> mean toward the 5 mV fold, the folds armed the limit hold, and the drive lost following at every voltage (`err_pk`
> 101-111, held passes in the thousands, duty at duty_min); at 40 A the same row followed 1,000 per mille
> (`debug_261005-005643`). **The defect is Rev A's**, not a motor's: one frame's noise (driven σ ≈ 1.7 mV, peaks 7-8 mV
> above the mean, 2026-09-30) leaves no room under a 4 mV floor for any real draw. **It now matters to the plan:** a
> hand-load "limit holds" cell on the Doco (rated 1.84 A) needs a limit a hand can reach, which Rev A cannot resolve
> one frame at a time. (PL-201, filed 2026-10-05 for the same defect, is merged here.) Earlier status: ANCILLARY,
> 2026-10-01, opened from PL-163's residual ([archive](plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01b.md)).

**MEASURED** (`analyses/bench/2026-09-30/reva/REVA-PLATFORM-EVALUATION.md`, `debug_260930-155650.log`; rerun
`reva2/REVA-RERUN-EVALUATION.md`, `debug_260930-210953.log`): on Rev A the unloaded net reading peaks at 7 mV
(`net_max_mv,7`; zero 12-13 mV), against the ±3 mV that sized `FOLD_MIN_MV` = 4 (DRIVER_REV 40). At a 2 A limit the
fold therefore acts on noise, about 75 frames a second, and the LEFT board's power-5 leg folded 4.3 % of frames. Only
`testSetCurrentLimits()` sets a limit that low; at the shipped 40 A peak the Rev A threshold at the duty floor is about
15 mV, so no user reaches it.

**Fix direction, if taken:** `FOLD_MIN_MV` per board revision, sized from these readings. Its certification needs a
`t0-reva` that can measure:
- **FOLDPOS as built cannot.** The judged window must open at the speed-up (a grip latches the protective stop about
  1 s after the stall), with no duty gate, and a rate criterion against the unloaded legs' noise-fold rate that
  separates the acceleration's folds from the grip's.
- **Two harness gaps:** `t0vStart()` reports a refused start's board as `REV_Unknown`, so a start-check refusal reads as
  "not REV_A"; the hold record prints no stop reason.

### PL-174 -- STUDY: characterise the vibration seen at some speeds

> **Status (2026-10-01):** DEFERRED; moved here from task «#3532» at 6.1.0 start. Starts when Stephen calls it and the
> piezo hardware has arrived; he sets the scope. STEPHEN 2026-09-13: *"some speeds? show significant vibration... in a
> couple of days i'd like to characterise the cause so note this as an upcoming study."*; 2026-09-17: *"no those three
> are not in"*.

**Instrument (STEPHEN 2026-09-13):** two amplified piezo discs on the Rev B platform read by P2 ADC smart pins with
GIO/VIO calibration. Carry into the sensor code: discard settling samples after every GIO/VIO switch and average (PL-32,
p2kb `p2kbAppNoteP2an001SinglePinInstrumentationAdc`); pins clear of P40-P49 and inside one power group; log on the
driver status timebase. **Pointers, not conclusions:** unequal hall sectors; duty-servo hunting (the 6.1.0 servo change,
PL-167, alters this); mechanical resonance; the commutation placement (6.0.0 ships a speed-following lead). A
discriminator worth building: the same speeds on two placements. **First step when it starts:** record with Stephen which
speeds, wheels, load and direction. Execution: a two-phase design study.

### PL-175 -- the N-motor shape: one P2 driving 1-3 motors (after 6.0.0, with the DocoEng work)

> **Status (2026-10-01):** DEFERRED; moved here from task «#3562» at 6.1.0 start. STEPHEN 2026-09-16: the N-motor part is
> *"after 6.0.0"* and goes with the Doco effort; 2026-09-17: *"no those three are not in"*. Not started before Stephen
> schedules it.

**Scope** (`DOCs/plans/FIXED-COG-SHAPE-DESIGN.md` §1, §4, §6 roster rows, §7, §9), on the front cog already built: a
roster owner serving 1-3 motors (STEPHEN 2026-09-15: *"A single P2 is going to control 1 to 3 motors... The Docom motors
are the ones that drive CNCs"*), an indexed API plus roster-wide stop / e-stop and one synchronised drive; `demo_n_motor`
added beside the two existing demos (STEPHEN 2026-09-15); configuration for the N-motor form beside the two existing
ones (the config was re-shaped to `CFG_SINGLE_MOTOR` / `CFG_DUAL_MOTOR` on 2026-09-28, so this part is re-designed against
that, not the six blocks it was written for); `tools/build-check.sh` certifies three release demos; README / DEVELOP /
DRIVE-OBJECTS for the third form. **Open for Stephen when scheduled, asked before building:** the owner object's name and
the configuration names. Certification needs the DocoEng motors on the bench.

### PL-176 -- generalise the offset sweep into a real motor-adoption tool
> **Status (2026-10-12, D6 evaluation): CLOSED on the Doco, CERTIFIED** -- `MA-END stopped,NONE`, peak 4,740 mA; the
> 1,120 rpm scans stop before the slip; fast pair 309 / 49 (shipped 304 / 48); the climb clean to its last rung, 6,720 rpm,
> each way (`debug_261012-134722.log`). The D6 sheet's `ceil_found,TRUE` band was a sheet error: a climb clean to the
> ladder's end reads FALSE by construction. The Rev B closeout's `adopt-wheel` row still runs TOOL_REV 6 on the 6.5in.
>
> **Status (2026-10-12, D5 evaluation): FIXED at the desk, TOOL_REV 6; the D6 confirm sheet runs `doco-adopt-v24p0`.**
> D5's 24 V run ended `MA-END stopped,OVER_CURRENT` (8,460 mA): a side's bracket keyed on that side's own lowest clean
> point, a noisy dip at -15 walked the 1,120 rpm NEG minus side to -30, and the rotor slipped there (every TOOL_REV 3 run
> stopped at the same point). TOOL_REV 6 seeds the bracket from the scan's lowest clean point, either side, as the fit
> already selects its points (`fitScan()`), so the fit's input is unchanged and the walk stops at -15. Also: a SKIPPED
> point printed the previous scan's readings (the per-point arrays were not cleared); now zeros.

> **Status (2026-10-10, burn-down «#3707»): BUILT** (`util_adopt_motor` TOOL_REV 5; STEPHEN 2026-10-03 *"let's do B
> please"*); **CERTIFIED BY THE REV B CLOSEOUT** (`adopt-wheel`: `MA-END stopped,NONE`, Z and the ceiling found). Whether
> the Doco closeout also carries a `doco-adopt-<voltage>` row is decided with its sheet («#3708»). **Decided 2026-10-10:
> it does, `doco-adopt-v24p0` in the D5 sheet's row 3** — TOOL_REV 5's climb to 6,720 rpm is new since the tool last ran
> on the Doco (TOOL_REV 4), and only the 24 V row reaches it.

> **Status (2026-10-01):** DEFERRED; moved here from task «#3592» at 6.1.0 start. Goes with the DocoEng effort (PL-175,
> PL-27, PL-71). STEPHEN 2026-09-21, setting the phasing: *"we could just build this as our standard instrument today and
> use it for this phase for the 6.5, and use it for the doco when we get there. After having experience with it, we can
> generalize it to a real tool and make that part of a later effort."*

**Waits for** the alignment instrument (`dual-align`) to have run against both the 6.5″ and the DocoEng motor: a stop
condition that holds for a motor whose fault behaviour was unmeasured can be derived from two observed motors, not
invented from one. **Scope when it starts:** parameterise by motor rather than editing the instrument's named constants
(what had to be edited for the DocoEng IS the specification, so record it during that run); a stop condition derived
from both motors' measured edge behaviour; a stable record format; the `ADDING_MOTOR.md` integration, which today walks
a user through producing a new motor's offsets by hand. The user docs must not promise a generalised tool before it
exists. Verify when built: the stop condition derives from two motors' measurements; `ADDING_MOTOR.md`'s offset step
names the tool and is walkable end to end.

### PL-177 -- back-EMF as a position source, and the torque-peak hold it enables (a delta release)

> **Status (2026-10-01):** DEFERRED; moved here from task «#3602» at 6.1.0 start. STEPHEN 2026-09-22: *"I'm thinking the
> back EMF is an added capability, and so I might make that a delta release after we get the current driver
> stabilized. My current thinking is to defer back EMF."* Not started before Stephen schedules it.

**Scope, all priced in `DOCs/plans/DRIVE-INTEGRATION-DESIGN.md` §7:** C-B, back-EMF as a position source; C-D, holding an
overloaded wheel at its torque peak (PL-105, modelled at ~1.8-2.7× today's pull); C-C, hall-timing interpolation (C-D's
other route). First measurement: the release-window capture (§7 C-B) -- release the bridge for ~10 frames at a few
speeds, capture the phase pins in P_ADC_SCOPE, and read the decay time, settle time and clean window against current.
While driving, the drive senses back-EMF 0 % of the time today. **6.1.0 note:** PL-167's D-5 design (task «#3645»)
works on where the held field sits at the limit; if it lands, it changes this entry's measure of benefit for C-D.

### PL-178 -- `tools/pasm_equiv` compares against a baseline from before the hold-speed fix

> **Status (2026-10-10, burn-down «#3707»): FIXED.** The default baseline is the last commit (`--baseline-ref HEAD`), so
> an uncommitted change is proved against the driver it changes; `--baseline-ref v6.1.0` names a release
> (`tools/pasm_equiv/README.md`). MEASURED: `tools/pasm_equiv/run.sh --seeds 4 --no-named` on DRIVER_REV 60's tree,
> VERDICT EQUIVALENT.

> **Status (2026-10-02):** OPEN, tooling; found by «#3655» phase 1. Its other half is fixed: `compile_driver()` built the
> driver with no `-D`, which the user config has refused since 2026-09-28, so the tool could not build the tree at all; it
> now passes `-D CFG_DUAL_MOTOR` and echoes the command (MEASURED: `tools/pasm_equiv/run.sh` builds baseline and
> candidate).

**MEASURED 2026-10-02:** the tool's default baseline is the ref `mem-reduce-start`. With the hold-speed fix's boost
(D-2) in the tree it reports NOT EQUIVALENT (60 equal, 48 diverged), as it must: the boost changes behaviour by design.
«#3655» proved the rest of the image unchanged with a null-operand copy (108 of 108 equal) and the boost's add free of
overflow with a saturating oracle (258 of 258 over 200 seeds). Until the baseline moves, every later PASM change is
compared against an image that differs by the fix. **Fix:** once the fix is committed and certified, the default
baseline becomes that commit (a new ref, named in `tools/pasm_equiv/README.md`), so later changes are compared against
the driver that ships.

### PL-181 -- under the platform's load the lag peaks reach LAG_SOFT in calm running (design risk R2)

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT's floor row** (`floor-auto`, `floor-grab`;
> STEPHEN 2026-10-10 *"Q1 B"*): read under load as the watch below says.

> **Status (2026-10-02): WATCH, 6.1.0** (evaluation §3.1, F-4 and F-8). No speed is lost; the bound or D-2 is not touched
> until the model says whether the boost firing in running matters.

**MEASURED 2026-10-02** (`debug_261002-103332.log` `BM-SPINW` seq 30-58): on the slow and medium schedule legs `err_pk`
read 79-90 on 7 of 8 wheel-legs (SPINHUNT FAIL LEFT 4 / RIGHT 3 of 4, bound 76); the duty swing fell to 95-539 from
DRIVER_REV 46's 900-1,650. The model predicted `err_pk` 67-76 (design §5; R2 named A-3's 76 as the guard). SPINERR's
means read 43-46 at slow against the wheels-up 47-49 band, as on 2026-09-30 (unchanged by the fix). **Settles it:** the
model's slow / medium legs at the floor's inertia, with and without D-2.

### PL-182 -- LIMGIVE's sampler scores a hold during the spin-up as the field giving way

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT's floor row** (STEPHEN 2026-10-10 *"Q1 B"*):
> `floor-auto` emits every sample of the slow leg (the SRC_REV 82 correction's first run).

> **Status (2026-10-03, closeout): CORRECTED, `test_bench_dual` SRC_REV 82** — `traceWalk()` now caps at
> `TRACE_EMIT_MAX #> trEmitMax`, so the slow leg's trace emits every sample on the next floor-auto run. The held passes
> are placed by that run, which no 6.1.0 decision waits on (LIMGIVE is CERTIFIED).
>
> **Earlier status (2026-10-03): LIMGIVE CERTIFIED (PASS on two visits); the held passes still UNPLACED** — SRC_REV 80's full slow
> trace emitted 391 of 1,712 samples on the third visit: `traceWalk()` caps its emission at `TRACE_EMIT_MAX` as well as the
> fit (harness fix). The emitted samples peak at a lag of 82, never the 100 hold, and no leg gave way.
>
> **Earlier status (2026-10-02): CORRECTED, `test_bench_dual` SRC_REV 78** («#3664»): limb (a) counts a give-way only after the
> wheel's driver has read AT_SPEED on the leg (`bLgArrived`; the held pass itself reads SPIN_UP, since `holdDecay` turns
> AT_SPEED into SPIN_UP, so the arrival is latched rather than the sample's state tested). It still FAILs a decay at speed
> with no limiter (D-3's limiter test removed, by reading). Spin leg 2 (slow) is now traced. **Earlier:** OPEN (F-5).

**MEASURED 2026-10-02:** SPINHOLD LEFT FAIL (1 leg) and LIMGIVE FAIL (2 of 31,278 samples) are one held pass each, on
LEFT, in slow spin leg 2 and slow ramp leg 1 (`BM-LIMW` seq 43, 1_126); neither leg lost speed (`fol_pct` 107; arrival
1,807 / 1,790 ms). `limSample()` (`test_bench_dual.spin2:18120`) calls a held sample a give-way when the field speed is
under 98 % of the **target**, which in SPIN_UP it always is; `holdDecay` lowers the field only when a limiter acted (D-3,
`isp_bldc_motor.spin2:7786-7790`). **Fix:** judge limb (a) only in AT_SPEED, or record the state at each give-way; and the
next visit traces one slow leg so a breakaway hold is told from a hold at speed.

### PL-184 -- at the quarter, the lead schedule draws more current than the fixed pair turning one way

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT's floor row** (STEPHEN 2026-10-10 *"Q1 B"*):
> the quarter pairs' current in both directions, as information.

> **Status (2026-10-02): OPEN, information, not this fix** (evaluation §3.1, F-7). The timing (PL-105's area), which
> D-1..D-5 do not touch.

**MEASURED 2026-10-02**, the first measurement of SPINLEAD: 1.17 / 1.30 against 1.05. Clockwise (leg 7 against 9) the
schedule draws less than the fixed pair (`amps` 990 against 1,043, 779 against 856); counter-clockwise (leg 8 against
10) more (1,259 against 878, 1,824 against 1,137). One pass each way, no repeat. **Settles it:** a repeat of the quarter
pairs, both directions, before any claim about the schedule's saving at the quarter on the floor.

### PL-190 -- SRVKEEP's fixed reference reads a day's spread as a regression

> **Status (2026-10-13, Rev B evaluation): OPEN, measured again, same shape.** `debug_261013-084502.log`: LEFT FAIL,
> rung 7 reverse `inet_x10,301` (rid 22) against the reference 285, +5.6 %; its duty 18,575 against 18,486, +0.5 %;
> RIGHT PASS. Duty holds; only the net current wanders. Settles it, as before: a same-session control or a band from
> repeat runs. A harness cell, not a driver regression.

> **Status (2026-10-10, «#3708»): READ BY THE REV B CLOSEOUT's row 1** (`dual-a`, wheels up; SRVKEEP is a part-A ladder
> cell, not a floor one as the burn-down line below said). The sheet names its known limit beside the cell.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT's floor row** (STEPHEN 2026-10-10 *"Q1 B"*).

> **Status (2026-10-03): WATCH, harness** (second 6.1.0 visit §2.1, G-5).

**MEASURED 2026-10-02:** three re-visited rung windows read net current 5.6-7.7 % over the 2026-09-27 DRIVER_REV 46
reference (rid 22, 41, 136 of `debug_261002-134026.log`); duty within; pack 20.2 V against 20.5 the same morning; the
steady drive is unchanged by construction (`tools/pasm_equiv`, C4 / S-1 neutralised: 112 of 112 equal). **Settles it:** a
same-session control, or a band derived from repeat runs of one driver.

### PL-191 -- a speed raised while a wheel is still slowing dips before it climbs

> **Status (2026-10-10, «#3708»): NOT A CLOSEOUT LOAD; KNOWN ISSUE EVIDENCE FOR «#3690».** It was seen in an RC drive
> (`floor-rc`), and neither floor tier raises a speed while a wheel is slowing, so the floor row cannot read it. No commit
> since DRIVER_REV 48 touches the ramp generator's path for it, so a run would re-measure an unchanged behaviour (overlay
> P10). Whether it ships as a Known Issue is Stephen's (P5).

> **Status (2026-10-10, burn-down «#3707»), superseded above: CERTIFIED BY THE REV B CLOSEOUT's floor row** (STEPHEN 2026-10-10 *"Q1 B"*).

> **Status (2026-10-03): WATCH, the ramp generator (PL-160's)**; Known Issues evidence (second 6.1.0 visit §3.4, G-9).

**MEASURED 2026-10-02** (`debug_261002-143653.log` 161.1-161.5 s): the stick went 0 → 5 → 35 → 45 while LEFT was slowing
from 56.6 ×10⁶; the jerk-limited generator unwound the deceleration first, the field fell to 6.8 ×10⁶ (12 % of its new
target) for ~300 ms, the wheel stood, and the steering object scaled both wheels (`EV_PATH_LIMIT` 184 ‰). Twice in the drive.

### PL-192 -- LDHUNT fails a single clean limiter engagement by its own definition

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE REV B CLOSEOUT's floor row** (STEPHEN 2026-10-10 *"Q1 B"*):
> `floor-grab` reads `flips,0` on a single engagement (the SRC_REV 82 correction's first run).

> **Status (2026-10-03, closeout): CORRECTED, `test_bench_dual` SRC_REV 82** — `evDrain()` keeps each wheel's first
> in-window engage that found the limiter released apart as its onset (`evdPathOn`); `loadEngages()` counts it toward the
> engaged precondition, not the flips. The third visit's single held engagement reads 0 (PASS); its hunting negative
> (an engage and release every 720-790 ms) still reads several. The SPINSTOP watch stays open below.
>
> **Earlier status (2026-10-03): OPEN, harness** (third 6.1.0 visit §3.3, H-1; and SPINSTOP H-3 as a watch).

**MEASURED 2026-10-02** (`DOCs/analyses/bench/2026-10-02c/debug_261002-182037.log`): the grab reached OVERLOAD for the first
time (LEFT 31 %, RIGHT 70 %, `path_min` 733); the path limiter engaged once inside the judged window (`EV_PATH_LIMIT` 746 at
15,588 ms) and held until the stop (released at 19,252 ms). LDHUNT counts every transition in the window against a bound of
0, while its precondition accepts an engage inside the window, so a single held engagement FAILs (`flips,1`). Hunting, its
own negative, is an engage-release cycle every 720-790 ms. **Fix:** count the transitions after the window's first engage.
**Watch:** SPINSTOP failed once (`debug_261002-181611.log`, medium leg 3 RIGHT stopped at 216 against 212, one tick past its
tolerance), new on DRIVER_REV 49, once in 20 stops.

### PL-193 -- the drive does not use the pack sensor's voltage: watts and the speed table assume DRIVE_VOLTAGE

> **Status (2026-10-03): OPEN, a v6.1.0 Known Issue** (CHANGELOG v6.1.0). Filed at the 6.1.0 build wrap-up: the Known
> Issue had no entry behind it.

`getPackVoltage()` reads the optional sensor (`VOLTAGE-SENSOR.md`), but `getCurrent()`'s watts and the speed table use
the configured `user.DRIVE_VOLTAGE`. A pack below its nominal voltage reaches the duty ceiling at a lower speed than the
table predicts (PL-187's arithmetic: full power needs about 102 % duty at 18.5 V). **To close:** decide with Stephen whether the
drive reads the sensor when one is fitted, and where (watts only, or the speed table too).

### PL-194 -- `getCurrent()` does not show regenerative current

> **Status (2026-10-03): OPEN, a v6.1.0 Known Issue; a board limit.** Filed at the 6.1.0 build wrap-up.

The current a moving wheel returns to the supply when it is slowed or pushed is neither measured nor limited
(`DRIVER_BOARDS.md:93`); why the sense path cannot see it is not established here. Kin to PL-118 (the shunt does not carry a phase
short's current). **To close:** either a documented hardware limit Stephen rules permanent (and this entry is removed by
decision), or an estimate from the pack sensor's rise during braking, if a fitted sensor can see it.

### PL-195 -- `setHoldLimits()`'s defaults were sized with the wheels unloaded

> **Status (2026-10-03): OPEN, a v6.1.0 Known Issue.** Filed at the 6.1.0 build wrap-up. The defaults were made public
> and documented as sized unloaded in 6.0.0 (Bench Readiness plan, Stephen *"yes A"*).

The hold's ceiling, rise and limit times were set on lifted wheels. A platform at rest on a slope or pushed by hand loads
the hold the way a lifted wheel does not. **To close:** measure the hold on the floor (a held stop pushed by hand, the
platform on a slope) and either confirm the defaults or retune them with Stephen's ruling.

### PL-196 -- `calibrate()` is public and does nothing

> **Status (2026-10-03): OPEN, a v6.1.0 Known Issue.** Filed at the 6.1.0 build wrap-up. Since 6.0.0 it returns
> `ERR_NOT_IMPLEMENTED` and its doc says so (`src/isp_bldc_motor.spin2:601`; API-14 in the 2026-09-27 archive).

The method is kept so existing programs compile. **To close:** Stephen decides whether it gains a body (the offset sweep
generalised, PL-176, is the natural one) or is retired in a major release.

### PL-197 -- a two-stage request's acknowledgement bound reads 21 passes against a 20 ms timeout

> **Status (2026-10-10, burn-down «#3707»): FIXED at DRIVER_REV 60 (Spin2 only), by raising the timeout.** Re-derived:
> a two-stage request (the fault clear, then the synchronized take, each its own 3-pass bound) holds the slot order for
> at most 6 passes, so with every request ahead at two stages one motor's worst answer is the 36th pass, seen by the
> 37th ms; the platform's the 30th. `REQ_ACK_TIMEOUT_MS` 20 -> 40 covers both at any clock (36 n + 1 <= 40 n). Only a
> front cog that does not answer is reported later; the theory of operations states 40 ms.

> **Status (2026-10-03): OPEN, a finding (DERIVED from the source comment, not reproduced).** Filed during task 3671
> (front-cog clock independence), which did not change it.

`bFrontServiceRequests()`'s doc (`src/isp_bldc_motor.spin2`, *THE ACKNOWLEDGEMENT BOUND*) derives a posted request's
answer within 18 passes (19 ms with the caller's poll) under `REQ_ACK_TIMEOUT_MS` (20), then says a two-stage request
(a synchronized drive of a FAULTED motor) adds 3 passes when both its bounds go: 18 + 3 = 21 passes, over the 20 ms the
caller waits. The case needs five other application cogs' requests queued ahead AND a driver that never acts, so a caller
could see a timeout where the derivation promises an answer. **To close:** re-derive the bound with the two-stage case
in it, and either show it cannot reach 21 or raise the timeout (or the derivation) so it covers it; no bench run is
needed to decide it.

### PL-199 -- at 350 MHz the Rev A current sense at rest is ten times noisier
> **Status (2026-10-12, D6 evaluation): CLOSED, CERTIFIED** -- the 350 MHz build refused at start both times,
> `B1-START,cog,-1,err,-1_024`, nothing driven (`debug_261012-132251.log`, `-132350.log`).
>
> **Status (2026-10-12, D5 evaluation): FIXED at the desk, DRIVER_REV 61 -- the supported clock tops at 300 MHz.** D5
> placed it: `clk-300` rests at spread 3 mV (healthy); `clk-350` refused to start both times on `HLT_SENSE_ZERO`. Root
> cause (desk): the sense is the pin's sigma-delta ADC, clocked by sysclk with no divider in any smart-pin mode; the
> driver's own window is fixed in time and finer at a faster clock, so nothing in its arithmetic worsens at 350 -- the
> converter does, and no P2 document gives its maximum clock. Nothing above 300 MHz was ever measured on either board.
> `start()` now refuses a clock over `MAX_CLKFREQ_HZ` (300 MHz) with `ERR_CLOCK_TOO_FAST` (-1_024), before anything
> is claimed, as the floor does. DEVELOP.md and DRIVE-OBJECTS.md say so. The D6 sheet's `clk-350` probe must read the
> refusal.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE DOCO CLOSEOUT, then the desk.** A `single-passprobe` row at
> `clk-300` (and `clk-350`) records `B1-ZERO spread_mv` before it drives, which places where the noise starts; the desk
> root cause follows from that (the sense's sampling against the running clock).

> **Status (2026-10-05): OPEN, a finding (MEASURED once).** D1b's pass probe at `clk-350`
> (`DOCs/analyses/bench/2026-10-05/debug_261004-184638.log`).

Undriven, before any drive, `B1-ZERO ... spread_mv,35` at 350 MHz against 3-5 mV at 200, 270 and 271.25 MHz on the same
board and motor; the run then tripped the harness's over-current guard at a "5.4 A" reading (27 mV at Rev A's 5 mV/A,
inside that noise) on a motor that was not turning. A clock-dependent sensing defect falls under doctrine overlay P14.
**To close:** the next Doco visit's `clk-300` probe records the same rest-zero spread before it drives, which places
where the noise starts; then root-cause it at the desk (the sense ADC's sampling at the running clock — the frame and
the SINC window scale with it — before any hardware explanation).

### PL-198 -- `moveShaftToAngle()` has had no effect since DRIVER_REV 38

> **Status (2026-10-09): CLOSED at DRIVER_REV 58 (task 3705), by its first option.** `moveShaftToAngle()` and the dead
> *TEST-EXERCISER* PASM block are removed; the launch long it wrote is now PL-218's `stopHold`. `ERR_BUSY` keeps its
> value (the error names are a table indexed by it) and is marked reserved. No user page named the method.
>
> (2026-10-04: OPEN, a finding.) Found during task 3679 (looking for a fixed-field test path for the Doco's
> hall-zero reference).

`moveShaftToAngle()` (`src/isp_bldc_motor.spin2`, *TESTING USE*) writes `targetAngle`, but the PASM block that read it
(*TEST-EXERCISER SUPPORT CODE*, inside the drive pass's request handling) is commented out, and its own note says no path
reaches it since DRIVER_REV 38. So the method returns `NO_ERROR` and moves nothing; a second call returns `ERR_BUSY`
forever, because nothing clears `targetAngle`. **To close:** either remove the method and the dead block (and the
launch long's comment), or re-enable a fixed-field path deliberately (cog/LUT space is near full, overlay P13); the
Doco's hall zero is referenced to the offset scan's current minimum instead (task 3679).

### PL-200 -- a timed crawl stop on the Doco rested 120 ms after its field stopped

> **Status (2026-10-10, burn-down «#3707»): CLOSED, not reproduced and the path corrected.** D4's eight crawl stops rested
> -55 .. +15 ms from their limits (`R23-SGL-STOPTIME`), and a timed stop's path was corrected at DRIVER_REV 58 (PL-218),
> whose certification rows judge timed stops again.

> **Status (2026-10-05): OPEN, a finding (MEASURED once).** D1b third pass, 18.5 V
> (`DOCs/analyses/bench/2026-10-05/debug_261005-132917.log`, `B1-STOP,sign,NEG,kind,CRAWL,by,MS`; evaluation D1B-12).

A 3 s crawl at power 5 (NEG) stopped its field on time (`field_dev_ms,0`) and the shaft came to rest 120 ms later
(R23-SGL-STOPTIME `measured,120`, band ±100); its position was in band (`dev,120` counts of −240..+180). The other 23
stop-by-time instances across five voltages read −70..+95 ms. **To close:** D2 re-judges R23-SGL-STOPTIME at every
voltage on the tuned Doco tables; if the late rest recurs, root-cause at the desk why the shaft moves on after a
crawl's field stops (the hold the stop applies at power 5, against the cell's rival named in its own note).

### PL-201 -- on a Rev A board a low current limit folds back on sense noise and the motor stops following

> **Status (2026-10-10, burn-down «#3707»): CLOSED, merged into PL-170** (2026-10-05); it is tracked there.

> **MERGED into PL-170 (2026-10-05)** — the same defect, measured on the 6.5″ on 2026-09-30. Filed the same day with two
> errors corrected there: it is not user-affecting (no public method sets a limit; users run at 40/27 A), and the
> 6.5″ did not escape it (it folded on noise in 0.06-4.3 % of frames on Rev A at 2 A). The number is not reused.

### PL-202 -- T0-27 judges Rev A's fold-back on one frame's reading, which DRIVER_REV 55 no longer folds on

> **Status (2026-10-10, burn-down «#3707»): FIXED at the desk** (`test_bench_t0` SRC_REV 36). T0-27 judges the fold the
> driver runs, from `testGetFoldFloorMv()`: R22-T0-REVA-FOLD's threshold is that floor (3 mV filtered on Rev A) and its
> one-frame noise premise is judged only on a one-frame fold; R22-T0-REVA-FOLDPOS takes 0 as a reference, needs at
> least one fold, and on a filtered fold is MEASURED only when the speed-up's mean net reading is over its threshold.
> Tier `t0-reva` is in no release plan (the 6.5in is certified on Rev B).

> **Status (2026-10-05): OPEN, a harness defect (DESK, by construction).** Found while building «#3699».

DRIVER_REV 55 (PL-170's fix) makes Rev A's fold-back compare a FILTERED DC-link reading (`senseFilter`, a 16-frame
time constant) against a 3 mV floor (`FOLD_MIN_FILT_MV`), plus a one-frame trip 14 mV over the threshold. T0-27
(`test_bench_t0.spin2` `t0vLeg()` / `t0vKickLeg()`, tier `t0-reva`, R22-T0-REVA-FOLD) still judges the old premise:
its threshold must equal `testGetFoldMinMv()` (4 mV) and one frame's net reading of that floor + 1 counts as a
measurement. On REV 55 Rev A's threshold sits at the new floor, and one frame's net reading over 4 mV is ordinary
noise that folds nothing, so the cell would FAIL a correct driver. The parameter-run read itself is fixed (SRC_REV 35:
`sense_zero` at `motor.DRVR_PARAMS_SENSE_ZERO_IDX`). **To close:** redesign T0-27 on the filtered premise
(`testGetFoldFloorMv()`, the floor and the shift) before tier `t0-reva` runs again; the sprint plan runs no Rev A
floor tier for the 6.5″ (`DOCO-AND-CLOCK-SPRINT-PLAN.md` "Not in this plan"), so nothing runs it this cycle.

### PL-203 -- a POS stop by rotation from the Doco's top speed rests up to 12 hall ticks early

> **Status (2026-10-10, burn-down «#3707»): CLOSED, verified** (D4, below); DRIVER_REV 58 left stops by rotation as D4
> measured them (`tools/pasm_equiv --stop-hold`), and the certification's stop rows judge them again.

> **Status (2026-10-08, D4): VERIFIED (MEASURED, D4 rows 1–3 and 6).** All 16 R23-SGL-STOPROT cells PASS at 7.4,
> 11.1, 14.8 and 24 V. The POS top stops rest +58 / +46 (7.4 V) and +61 / +80 counts (11.1 V), against D3's −355 /
> −310 and −286 / −255, with the held passes still present (47–95). The hold also acts on timed stops, which now end
> late: PL-218.
>
> **Status (2026-10-08, later): FIXED in DRIVER_REV 57, awaiting D4** (STEPHEN 2026-10-08 "we fix everything"). A
> pass held while the drive is stopping now holds the trajectory generator too: the next pass skips `jerkStep`, so
> the field resumes at the speed it was held at and keeps the travel the stop planned (`.running`, three longs;
> `held_seen` after the status run; cog 495/496). A stop the rotor cannot follow at all now waits for it; the
> blocked-rotor stop (~1 s) bounds that. Proof: STOPROT in D4's 7.4 V qualification and `single-stops-v11p1`.
>
> **Status (2026-10-08): CAUSE FOUND (MEASURED, D3 rows 1 and 2); the fix is a driver change, to be priced to
> Stephen.** The field is HELD during the POS slowdown: held passes POS 164 / 110 at 7.4 V and 110 / 81 at 11.1 V, NEG
> 11–13 and 48–51; the shortfall follows them (about −2.5 counts a held pass across all eight top stops: POS −355 /
> −310 and −286 / −255, NEG +99 / +11 and −48 / −80). The stop fires on plan both ways, and the shaft stops 5–20 ms
> AFTER the field, so the rotor does not stall: that rival is ruled out. A held pass is field travel the stop never
> makes up. **To close:** the stop steered to its target position, so a held pass lengthens the stop instead of
> shortening it, priced first (P5); then the stops tier at 7.4 and 11.1 V.
>
> **Status (2026-10-06): OPEN, a drive finding (MEASURED, D2 rows 1 and 3).** Root-cause at the desk before any rerun.

`stopAfterRotation()` at the top, POS increment: the driver's own count rests at 7,196 / 9,596 ticks of 7,200 / 9,600 at
11.1 V and 7,194 / **9,588** at 7.4 V (R23-SGL-STOPROT −254 and −723 counts, band −240..+180); NEG lands within one tick
at both. DRIVER_REV 53 (D1b, 7.4 V) showed the same direction smaller (−186 / −120). The POS ramp-down also covers less
than the plan (7.4 V −300 counts, 11.1 V −185; NEG −18..+95); crawl stops and stops by time pass. The stop is commanded
early, not overrun: the front cog decides on the driver's plan, so the plan's POS travel or the decision's use of it is
biased. **To close:** the cause stated from the source and these logs; the fix, then R23-SGL-STOPROT at D2's remaining
voltages.
> **D2 second pass, 2026-10-07 (`B1-STOPDEC`, every voltage):** rivals (b) and (a) ruled out — the travel counted equals
> the net travel on every stop, and NEG and POS fire at the same travel with the same planned stop. The shortfall is
> after the decision, POS only, at low supply: 7.4 V −6 ticks, 11.1 V −3/−4, 14.8 V up within ±2 (cell PASS). Two
> rivals remain, neither in the logs: the field HELD during the stop (lag hold) losing travel, or the rotor stalling in
> the stop's final slow creep below this motor's slowest steady speed at low supply. **Next:** print the held passes and
> the encoder's last-moving time across each stop; then the fix. **Built (SRC_REV 17):** `B1-STOPDEC held_d`,
> `rest_after_zero_ms` (negative: the shaft stopped before the field did); D2's third pass runs the stops at 7.4 and
> 11.1 V.
>
> **Desk, 2026-10-06:** the logs cannot separate three rivals — (a) the plan's POS stopping distance overstates the
> field's real one, (b) the front cog's travel sum (`trkTravelTicks`, summed |steps| a pass) over-counts in POS when a
> hall code steps back and forth at a sample, (c) the rotor ends short of its field. (c) cannot reach 5–12 ticks: a rotor
> that far behind its field would have tripped the 176° fault test. DRIVER_REV 56 keeps the decision's own figures
> (`testGetLimitFire()`), and the harness prints them (`B1-STOPDEC`, SRC_REV 16): `fire_trk − fire_net` is (b),
> `(rest_net − fire_net) − stop_tk` is (a). The next D2 stops runs read them; the fix follows from that reading.

### PL-204 -- the timing scan's walk past its span walks into the torque wall (harness)

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed** (`test_bench_single` SRC_REV 16, `OFS_WALK_FALL_MA`, the
> walk at `:6343-6351`).

> **Status (2026-10-06, later): FIXED in SRC_REV 16, awaiting the rerun of `single-measure-v11p1`.** The walk goes on
> only while each point is at least `OFS_WALK_FALL_MA` (50 mA) BELOW the one before; PL-205 (a held pass makes a point
> unclean), PL-206 (MISDIAL judges the signs' mean), PL-207 (the tool's Doco record at 40 A, TOOL_REV 3) and PL-208 (the
> 7.4–12 V minimums 4.00 ticks/s each way, DRIVER_REV 56; MININC's bound read from the library) are fixed in the same
> change.
>
> **Status (2026-10-06): OPEN, a harness defect (MEASURED, D2 row 1).** Mine («#3698», D1B-11).

The walk continues while a side's current is "not rising by more than 50 mA" (`bOfsNotRising()`), where the design (the
constant's own note) says "still FALLING", and it walks even after the vertex resolved inside the span. At 11.1 V 50 %
NEG it went −20 (350 mA) → −25 (370) → −30, the motor's torque wall, and the harness's absolute guard ended the run at
5.24 A (`debug_261006-140240`): the 11.1 V measure row lost its POS scan, top-speed scan, slowest speed, ladder, ramp and
stops for the third time. **To close:** walk only while the last point is lower than the one before AND the vertex is not
resolved inside the span; rerun `single-measure-v11p1`.

### PL-205 -- the timing scan fits a point where the drive hunted (harness)

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed** (`test_bench_single` SRC_REV 16: a point with a held pass
> is not clean).

> **Status (2026-10-06): OPEN, a harness defect (MEASURED, D2 row 1).**

At 11.1 V 25 % NEG the −15° point held the field 54 passes with `err_pk` 104 and mean error 32 (the drive hunting), yet
`B1-OFSPT ... clean,TRUE`, so `ofsFit()` took it: the vertex moved to +9.5° (50 %: −2.7°) and R23-SGL-LEADMOVE FAILed on a
12.2° spread. **To close:** a point with held passes is not clean (as the adoption tool already rules: HUNT).

### PL-206 -- R23-SGL-MISDIAL judges each sign alone, so the direction asymmetry fails it (harness)

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed** (`test_bench_single` SRC_REV 16: the cell judges the two
> signs' mean and prints the asymmetry); the check's premise is PL-219's.

> **Status (2026-10-06): OPEN, a cell defect (MEASURED, D2 rows 1 and 3).**

The cell predicts the supply from each sign's duty line and fails either beyond ±30 ‰: 11.1 V NEG −22 / POS +37, 7.4 V
NEG −80 / POS +93. A misdialled supply moves both signs alike; the direction asymmetry moves them apart. Their mean,
+7.5 ‰ and +6.5 ‰, is the misdial reading (PASS); the half-difference is the asymmetry. **To close:** judge the mean of
the two signs; print the half-difference as the asymmetry, not judged here.

### PL-207 -- the adoption tool's Doco record scans at 2 A, a limit the harness left at D1b (tool)

> **Status (2026-10-10, burn-down «#3707»): CLOSED, fixed** (`util_adopt_motor` TOOL_REV 3: 40 / 40 A; D3 ran it).
> `ADDING_MOTOR.md`'s record table now shows the same.

> **Status (2026-10-06): OPEN, a stale record value (MEASURED, D2 rows 1 and 3).**

`util_adopt_motor.spin2`'s DocoEng record carries scan 2 A / ladder 3 A, the harness's test limits until SRC_REV 14 moved
it to the library's 40 A (STEPHEN 2026-10-05 "yes A"). At 2–3 A on Rev A this motor's crawl-speed phase current reaches
the limit: 5° from the start a point hunts and the next droops (7.4 V 560 rpm NEG: d+5 HUNT held 73, d+10 DROOP 469 ‰),
and the 280 rpm rung droops (488 ‰), so no fit resolves and no ceiling is found. **To close:** the record at the
library's limits, its abort at 3.68 A as the harness's; rerun `doco-adopt-v11p1` and `-v7p4`.

### PL-209 -- the adoption tool walks into the Doco's torque wall at 40 A and ends on an over-current (tool)

> **Status (2026-10-10, burn-down «#3707»): CLOSED, verified** (D3 row 2, below). TOOL_REV 5 (this task) also lifts the
> Doco record's ladder to 6,720 rpm, so its climb meets the reserve at every supply now that PK-1's cap is retired.

> **Status (2026-10-08): VERIFIED at 11.1 V (D3 row 2).** `MA-END stopped,NONE`. Every side ended BRACKETED or at
> WALL within 15–30° of the start, and no point went deep into the wall. 1,120 rpm resolved both ways (306° / 63°,
> +7° / +9° from the shipped pair). Ceilings NEG 377e6 (hunt), POS 398e6, beside the shipped 370.5e6. The 560 rpm
> POS fit missed at Rev A's sense resolution (PL-215), so the record stays PROVISIONAL. The other voltages run on the
> fixed drive.
>
> **Status (2026-10-07, later): FIXED in TOOL_REV 4, awaiting the reruns.** A side ends `BRACKETED` 20° past its lowest
> clean point; on D2's own points every side ends before the wall (11.1 V MINUS at −20°, 24 V at −25°, PLUS at +20°).
>
> **Status (2026-10-07): OPEN, a tool defect (MEASURED, D2 second pass, all six voltages).**

Each side walks outward "to the motor's edge". At 2–3 A the limit capped the current at the edge; at 40 A (PL-207)
nothing does, and every run ended `MA-END stopped,OVER_CURRENT` (4.5–10.2 A) on the NEG MINUS side at 1,120 rpm stepping
to ~270°, −30° from the start. The minimum was bracketed well before (11.1 V: 86 mA at 0°, 336 by −20°); the tool's 2.5×
WALL rule is off below its 400 mA floor, and this motor runs under it. **To close:** a side ends 20° past its lowest
clean point (the fit uses only ±20° of it), so a falling side walks on and a bracketed one stops short of the wall;
rerun `doco-adopt-<v>`.

### PL-212 -- above ~2,500 rpm the Doco still needs 55-67 % more duty than its back-EMF, and 14.8 V's top has no reserve
> **Status (2026-10-12, D5 evaluation): CERTIFIED (the range half).** At all six supplies every range step held: fol
> 999-1,000, held 0, folds 0, resyncs 0, fault_kind NONE; the shipped tops held with the climb going 4-40 % above them
> (ends DUTY_OUT or the increment bound). The full-speed REVERSAL at 24 V faulted once: PL-222.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE DOCO CLOSEOUT** -- its range rows at all six supplies: the
> duty on the back-EMF line at each step, held passes 0, no second state, no fault below the ceiling.

> **Status (2026-10-10): FIXED at DRIVER_REV 59 (desk-proven; the certification visit certifies).** Root cause
> (MODEL, `DOCs/analyses/PL-212-ROOT-CAUSE-2026-10-09.md` §2, §7.2): above `ωe·L/R` ≈ 1 the load angle oscillates on
> its own (40–70 Hz on the Doco). The field's speed is commanded open-loop, so nothing damps it. The one-sided
> `servoBoost` rectifies the hunt's peaks into duty, which is the second state, and the hunt's peak sets 24 V's
> position-fault edge. The fix:
> - **H-2:** fieldSteps damps the field's advance. It applies 1/8 count per count of the last hall edge's lag above
>   its 66 ms mean, at |drv_incr| ≥ 201e6 in SPIN_UP / AT_SPEED, and not while the limit hold is armed.
> - **H-1b:** at ≥ 2^28, a release starts from the held field. As built, it jumped 12/23 of a pass forward, which
>   faulted the rated step at 14.8 V.
>
> F-6, a gate on the boost, was designed and withdrawn: it made the Doco's hand stall worse (96 phases).
>
> Model results:
> - Doco: no hunt and no second state at any supply to 1,050e6, across the Lh and J brackets. The rated step at
>   the 2023 rows faults 0 of 96 (as built: 38 at 14.8 V, 3 at 22.2 V). `docohand` is identical to as built.
> - 6.5in: identical to the digit in every mode below 201e6. Above it, its own top-speed hunt is gone.
>
> pasm_equiv:
> - 2,062 scenarios equal to REV 58, with stop-hold false and true, and at 160 MHz.
> - With both gates shut, equal to REV 58.
> - 300 high-speed scenarios: 213 diverge, every one after a gate opened.
>
> Memory, after the layout moves: cog 475/496 (21 free), LUT run image 502/512 (10 free), start image 152 (`held_seen`
> now zeroed at start), release image 34. The ceilings are re-tabled under PL-216.
>
> **Found on the way:** without the hunt's surplus duty, the Doco's top runs field-weakened in the model (duty 14–33 %
> under the back-EMF line at 24 V). D4 measured the good state on the line, so this is the model's calibration, not the
> drive's (PL-216's note).
>
> **Status (2026-10-08, D4): the timing part VERIFIED as far as timing reaches; the servo part is ALL of what is left
> (MEASURED, D4 rows 1–6).** On the lead table the model holds (the DC-current minima sit 3–4° from the table, inside
> its 4.3° scatter), and 7.4 V stays at the servo's setpoint to its top. From 11.1 V up, the drive runs at the same
> speed, supply and timing in one of two states. In one the mean error is 42–48 and the duty sits on the back-EMF
> line (24 V POS 2,800 rpm 10.7k). In the other the mean error is 36–39 against 48, the peak 90–111, and the duty
> 30–62 % over the line. It switches inside a climb: 24 V POS goes 11.4k at 2,940 rpm to 19.8k at 3,080 (+73 % duty for
> +5 % speed), and 22.2 V POS switched on the sweep's +5° nudge at a fixed speed. Every top at 11.1–24 V ended inside
> the second state, so those tops are caps set by the defect. Leading hypothesis (DERIVED): `servoBoost` is one-sided,
> so the extra duty widens the lag swing (peak − mean 50–70 against ~27), which wakes more boost — two stable points.
> **Next:** the desk root cause with the servo model (mine), then the PASM change priced to Stephen.
> `DOCs/analyses/bench/2026-10-08/D4/D4-EVALUATION.md` §3.
>
> **Status (2026-10-08, later): the timing part BUILT in DRIVER_REV 57, awaiting D4; the servo part OPEN.** The
> lead model (`DOCs/analyses/LEAD-CURVE-MODEL-2026-10-08.md`) fits every Doco sweep: the duty bowl's bottom is
> 53.5° + atan(ω × 1.17 ms) at every supply (L ≈ 1.06 mH a phase), so at the top ωL exceeds R and the fixed pair sat
> 50–60° short of it. The Doco on Rev A now takes a lead table against speed (the efficiency curve, 52.3 → 68.0°),
> the 6.5in's mechanism made per motor. The other part: at 24 V's tops the mean servo error sits at 40–45 counts
> against 48 (the one-sided fast boost woken by peaks of 86–104), costing 4–11° of effective lead; a PASM change, not
> built — D4's range on the new lead says how much of it is left.
>
> **D3 (2026-10-08), the speed-range test:** every top at 7.4 and 24 V ended by running out of duty, not by the
> motor: 7.4 V NEG 1,931 / POS 2,212 rpm, 24 V NEG 4,343 rpm, and POS ≥ 3,782 (cut by PL-213). 10° more lead cuts the
> top steps' duty 11 % at 7.4 V and 20–26 % at 24 V NEG 3,900–4,343 rpm, with the minimum beyond ±10° on almost every
> step. Above ~2,800 rpm at 24 V the duty is uneven with speed (NEG 19.4k at 3,220 rpm, 25.3k at 3,497, 22.0k at
> 4,063), and the peak angle error is 86–104 on every step, above LAG_SOFT 80. Part of the excess is the servo's fast
> boost, not the motor. **Next:** the desk root cause separates the servo boost from timing; then the change is
> priced. Once-per-turn speed ripple peaks at 124–132 ‰ near 3,000 rpm and falls to 6–9 ‰ above 4,000 rpm: a rig
> resonance, the likely vibration heard. The rig sits unanchored on a rubberized mat and walks and turns on it at some
> speeds (Stephen 2026-10-08), so this ripple is amplified by the rig. The next visit clamps it. Unit 2's 14.8 V top runs at the duty limit too.
>
> **Status (2026-10-07): OPEN, a drive finding (MEASURED, D2 second pass).** The R1 fix (DRIVER_REV 54) removed the
> two-state switching and the swinging duty; it did not remove this.

At 2,799 rpm (419e6) the top rung's duty is 18,122 / 17,577 at 24 V and 19,077 / 20,551 at 22.2 V, against ~11,400 and
~12,300 the motor's back-EMF line predicts (+55..+67 %); at 11.1 V's 2,475 rpm (370.5e6) it was +5 %. Peak angle error
grows with speed (72 at low speed, 78–80 at 2,475 rpm, 86–93 at 2,799), so the servo's fast boost (past LAG_SOFT 80)
still engages at the top. At 14.8 V the cap runs at duty 27,532 of 27,648 (99.6 %): the reserve rule the ceiling was
set by is not met there. Rivals, from D1b and D2: the best timing moves with speed and the Doco has one fixed pair (its
D1b scan moved ≥ 6° toward more lead at the top; the 6.5in has a speed-dependent lead and the Doco does not); the hall
rotor estimate has no position within a sector, its error growing with speed; the unequal sectors (53.6–67.8°). **To
close:** the speed-range test's per-step timing sweep and vibration (task 3700) say how far timing alone moves the
excess; then a desk root cause, and the change priced to Stephen. Until then the 14.8 V top is above its own rule.

### PL-210 -- the Doco hand load needs something to grip: a bare shaft cannot be held at 2-4 A
> **Status (2026-10-12, D6 evaluation): CLOSED, CERTIFIED** with PL-170: the grip stood the shaft at every step, both
> supplies.
>
> **Status (2026-10-12, D5 evaluation):** the grip worked at both supplies (the shaft stood at 11.1 and 24 V); the 24 V
> verdicts are PL-223's. Rides with PL-170 on the D6 sheet.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE DOCO CLOSEOUT** -- the hand-load rows (`single-handload-
> v11p1`, `-v24p0`) with a grip on the shaft, set up by Stephen: at 2 and 4 A the shaft stops, `R23-SGL-BLKSTOP` measured.

> **Status (2026-10-07): OPEN, a test set-up gap (MEASURED, D2 row 2).** The set-up is Stephen's (overlay P1).

At 4 A and 2 A the limit acted with no fault (R23-SGL-LIMHOLD PASS), but the shaft never stopped (standing ≤ 5 ms,
creeping 48–104 thousand counts under the grip), so R23-SGL-BLKSTOP is NOMEAS at every step. 0.034 N·m/A: 136 mN·m at
4 A, 68 at 2 A — ~20–45 N at the fingertips on a shaft a few mm across; at a 25 mm radius, 3–6 N. **To close:** rows 2
and 8 again with a grip of about that radius on the shaft.

### PL-211 -- R23-SGL-MISDIAL fails at 14.8 and 22.2 V and passes at the rows between

> **Status (2026-10-10, burn-down «#3707»): CLOSED, subsumed by PL-219.**

> **Status (2026-10-08, D4): SUBSUMED by PL-219.** On the lead table the cell reads +96 / +204 / +250 ‰ at 7.4 / 14.8
> / 24 V, because its premise (fixed timing) no longer holds; D2's figures cannot be re-judged until it is fixed.
>
> **Status (2026-10-07): OPEN, unexplained (MEASURED, D2 second pass).**

The signs' mean reads +48 ‰ (14.8 V) and +68 ‰ (22.2 V), against +26 / +6 / +19 at 11.1 / 18.5 / 24 V. A Ke error would
move every row alike; a supply set 5–7 % high at those two rows, the supply rising under regeneration, or the cell's own
spread all fit. **To close:** the supply's setting at those rows (Stephen); then either nothing, or the cell's tolerance
re-derived from its measured spread.

### PL-208 -- the Doco's slowest steady speed at 7.4 V swapped direction between D1b and D2

> **Status (2026-10-10, burn-down «#3707»): CLOSED.** DRIVER_REV 56 ships 4.00 ticks/s each way at 7.4 V, and D3 held
> 3.00 steady both ways under it (below), so the shipped floor has a rung of margin in each direction. The Doco
> certification's L-mininc rows judge it again.

> **D3 (2026-10-08):** 7.4 V steady at 3.00 ticks/s both ways, 2.00 not (sub-window 471 / 483 ‰). The edge moves
> between 2 and 4 from visit to visit, so the shipped 4.00 each way (DRIVER_REV 56) stands. Every slow rung runs at the
> duty floor 1,600, which is a third of 24 V's voltage at 7.4 V; 24 V holds 0.10 ticks/s steady.
>
> **Status (2026-10-06): OPEN, a table value (MEASURED, D2 row 3).**

D1b (REV 53): NEG 1.00 ticks/s steady, POS 4.00. D2 (REV 55, the per-direction pair): NEG 4.00 (3.00 not), POS 1.00
(0.75 not) — so the shipped forward minimum (1.00, `confgurePowerLimits()`) did not crawl steadily, and R23-SGL-MININC
NEG FAILed. Each rung is one 2 s sample at the duty floor; the edge is not repeatable to one rung. **To close:** the
7.4 V minimum (and 11.1 / 12.0 V, DERIVED from it) set to the larger of both runs, 4.00 ticks/s each way, until a
repeated measurement shows a lower one steady every time.

### PL-213 -- the harness's run charge guard overflows 32 bits, ending long runs early (harness)

> **Status (2026-10-10, burn-down «#3707»): CLOSED, verified** (D4, below).

> **Status (2026-10-08, D4): VERIFIED.** The 22.2 and 24 V ranges ran to their ends at 857,598 and 949,350 mA·s.
>
> **Status (2026-10-08, later): FIXED in SRC_REV 18.** The charge is carried in whole mA·s (`chargeMaS`, the mA·ms
> remainder below one), compared with the cap in mA·s; `charge_mas` prints it. Proof: D4's 24 V range runs to its end.
>
> **Status (2026-10-08): OPEN, a harness defect (MEASURED, D3 row 3).** Mine.

`test_bench_single` compares `chargeMaMs >= RUN_CHARGE_CAP_MAS * wheel.MS_PER_SEC`. The range tier's cap is 4,800,400
mA·s, and ×1,000 is 4.8e9, which wraps to 505,432,704. The 24 V range run ended `GUARD CHARGE_CAP` at 505,434 mA·s,
exactly there, with the POS climb still holding at 3,782 rpm. The accumulator itself is in mA·ms and would wrap past
~2,147 A·s. **To close:** compare in mA·s (and keep the accumulator below its wrap); the 24 V POS top runs again on the
next verification visit.

### PL-214 -- the range test's once-per-turn ripple bins by encoder position, so a bin can be empty (harness)

> **Status (2026-10-10, burn-down «#3707»): CLOSED, verified** (D4, below).

> **Status (2026-10-08, D4): VERIFIED.** `turn_rip_pm` reads at every step both ways at all six supplies.
>
> **Status (2026-10-08, later): FIXED in SRC_REV 18.** The turn bin is the start edge's index in the turn: its encoder
> offset from the window's first edge, rounded to whole ticks, mod 24 (an edge sits within ~8 counts of its tick's
> grid). Proof: D4's `turn_rip_pm` reads at every step both ways.
>
> **Status (2026-10-08): OPEN, a harness defect (MEASURED, D3 row 1).** Mine.

`vibTakeEdges()` puts each hall interval in one of 24 bins of 60 encoder counts. The hall edges fall 52–68 counts
apart, so some bins catch two intervals and some none. `binRipplePm()` reads NA when one bin is empty: 7.4 V POS, all
five steps. **To close:** bin by the edge's index within the turn, so each bin takes exactly one interval a turn.

### PL-215 -- on Rev A the DC current is too coarse to locate the Doco's timing minimum below ~1 A (instrument)

> **Status (2026-10-10, burn-down «#3707»): CLOSED.** A board's resolution, not a defect: the lead model reads each
> sweep's duty bowl instead (below), and the lead table rests on it (DRIVER_REV 57).

> **Status (2026-10-08, later): WORKED AROUND at the desk.** The lead model reads each sweep's duty bowl, which Rev A
> resolves to 0.1–0.3 %: its bottom fixes the headroom curve and, through the model, the zero the efficiency curve
> starts from. The current minima stay coarse (±4°), and the Doco's table follows their fitted line, not any one point.
>
> **Status (2026-10-08): OPEN, a measurement limit (MEASURED, D3 rows 2 and 4).**

At the Doco's no-load currents (0.05–0.9 A), a timing sweep's DC current moves by about Rev A's noise (5 mV/A). The
adoption tool's 560 rpm POS fit missed (fit error 2.7 against 2.5, on 44–210 mA). Unit 2's timing scan resolved no
current minimum at any speed. The range test's sweeps resolved at only a few steps. Duty resolves, but it keeps
falling with more lead until the motor loses hold, so it has no clean minimum. This blocks the agreed test for unit 2's
offsets, and it shapes how the Doco's speed-dependent lead can be measured (PL-212). **To close:** a timing criterion
this board can resolve, decided with PL-212's desk work.

### PL-216 -- the Doco's shipped speed limits sit well inside its measured range
> **Status (2026-10-12, D6 evaluation): CLOSED, CERTIFIED** -- 0.10 ticks/s each way at 11.1 and 24 V, every rung
> steady (`debug_261012-130448.log`, `-133859.log`): D5's misses were a run's spread on an unchanged crawl path.
>
> **Status (2026-10-12, D5 evaluation): TOPS CERTIFIED; FLOORS NOT YET.** The slowest steady speed held 0.10 ticks/s at
> 22.2, 18.5 and 14.8 V and 0.75 at 7.4 V (band 4.00), but 0.15 at 11.1 V and 2.00 / 1.50 at 24 V (band 0.10; D4 held
> 0.10 at both). Desk: the crawl path is unchanged since D4 (DRIVER_REV 58-60 act only on a stop by rotation, at
> |incr| >= 201e6, or in Spin2; the rest is pasm_equiv-identical) and the duty floor is the same 1,600; 22.2 V, run
> minutes after the 24 V failure, held 0.10. Consistent with run-to-run stick-slip at the floor (11.1 V's 0.10 rung
> sits in the low tail of its spread) and a disturbed 24 V run (5 min after the adoption tool's 8.46 A slip); not
> settled. No code change: the D6 sheet re-runs `single-mininc` at 11.1 and 24 V. If a floor fails again, the shipped
> floor at that supply is set to what holds (`minFwdIncreAtPwr` / `minRevIncreAtPwr`), and that ruling is Stephen's.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE DOCO CLOSEOUT** -- the range and L-mininc rows: each row's
> ceiling held (following about 1,000 per mille, no fault) and the floors held (0.10 ticks/s from 11.1 V up, 4.00 at
> 7.4 V).

> **Status (2026-10-10): FIXED at DRIVER_REV 59 (the certification visit's range rows certify).** Stephen,
> 2026-10-10: the Doco serves gantries, so its limits are accurate speed and accurate distance (overlay P14).
>
> **Ceiling.** The 6.5in's rule: the fastest speed held on the back-EMF line with 7.5 % of duty in reserve, never by
> field weakening (PL-108). It is anchored on D4's measured 7.4 V point, 302.5e6 (130944:114, :118), so
> `DOCO_CEIL_INCR_AT_NOMINAL` is 756e6, scaled by the supply. `DOCO_CEIL_INCR_MAX` is removed, because H-2 removed
> the 24 V fault edge it stood for. The rows are 302.0 / 453.5 / 490.0 / 604.5 / 756.0 / 907.0 / 980.5e6
> (2,018 to 6,551 rpm), inside the sheet's no-load speed. MODEL (`$M pl212 doco=1 rev58=1 hcont=3 damp=3 dv=V
> pl_set=row`): every row follows 1,000 ‰, speed sd ≤ 1 ‰, err 47.9–48.0, peak 69–70, held 0.
>
> **Floor.** 11.1 V up take 0.10 ticks/s (37_418), MEASURED by D4 both ways at 11.1–24 V; 24 V holds it on both
> units. 12.0 V is DERIVED. 7.4 V keeps 4.00, the larger of the two units.
>
> **Harness.** test_bench_single SRC_REV 19 mirrors the ceilings and lifts PK1_CAP_INCR above them. PK-1's
> retirement and LIM_BIG's clamp above 999,999,999 are «#3707»'s.
>
> **Model calibration note (not a drive defect).** At these rows the model's duty sits 3–31 % under the line
> (field-weakened); D4's good state sat on it (+3.0 / +4.6 %, 150741:138, :142). The model's lead zero (lzero 53.5)
> is the likely gap. The bench's range rows read the true duty.

> **Status (2026-10-08, D4): MEASURED on unit 2; the ceilings at 11.1 V and up are caps of PL-212's servo state, so
> nothing is re-tabled yet.** Slowest steady: 0.10 ticks/s both ways at 11.1–24 V (the lowest tried), 0.20 / 0.30 at
> 7.4 V (unit 1, D3: 3.00). Fastest held NEG / POS: 7.4 V 2,352 / 2,211 rpm (a real top, duty out at the setpoint);
> 11.1 V 2,476 / 2,476; 14.8 V < 2,800 / 2,775; 18.5 V 3,221 / 3,220; 22.2 V 4,038 / 4,161; 24 V 4,888 / 4,733
> (position fault, re-synced). 24 V's 0.10 now holds on both units. **To close:** unchanged — re-table both ends
> once PL-212's servo fix is in.
>
> **Status (2026-10-08, later): waiting on D4**, whose range at every supply on the new lead sets the final values.
>
> **Status (2026-10-08): OPEN, table values waiting on PL-212 (MEASURED, D3 rows 1 and 3).**

Stephen 2026-10-07: "the lowest RPM we can command and hold, and the highest... not some artificial limits".

- 24 V: holds 0.10 ticks/s (0.25 rpm) steady both ways against a shipped minimum of 0.60 (1.5 rpm). It holds 4,343 rpm NEG and
  ≥ 3,782 POS against a ceiling of 2,800.
- 7.4 V: holds 1,931 / 2,212 rpm against 1,650.

Every top ended at the duty limit with timing that wastes duty (PL-212). **To close:** the ceilings and minimums
re-tabled from the speed range at every voltage once PL-212's fix is in.

### PL-217 -- the second Doco's hall sectors differ from the first's by up to 2.8°, past the agreed 2° bar

> **Status (2026-10-10, burn-down «#3707»): CLOSED, in service** (below): the two units' mean sector widths ship in
> `hltbAngl4k` / `hltbAngl4k2` (DRIVER_REV 57), and unit 2's ripple read 0-12 per mille at every D4 step.

> **Status (2026-10-08, D4): IN SERVICE.** Hall-sector speed ripple 0–12 ‰ at every step on unit 2, so the table does
> not shake the shaft; the 7.4 V crawl now holds 0.20 / 0.30 ticks/s, but the unit changed with the table, so the gain
> is not attributable to it alone. Nothing open beyond the record.
>
> **Status (2026-10-08, later): RULED and BUILT** — STEPHEN 2026-10-08 "yes a": the two units' mean widths
> (57.7 / 59.4 / 64.1 / 66.6 / 57.0 / 55.25° for codes 1–6) in `hltbAngl4k` / `hltbAngl4k2`, DRIVER_REV 57; the
> time-averaged angle moves 0.13°, so the offsets stand. The offsets: the shipped pair served both units, and the
> lead table now replaces it on Rev A with a direction offset of 4.0° (unit 1 5.1, unit 2 2.7). Proof: D4's unit-2
> range at 14.8 V.
>
> **Status (2026-10-08): OPEN, Stephen's ruling (MEASURED, D3 row 4).**

Unit 2's six code widths are 59.1 / 58.8 / 63.4 / 65.9 / 56.4 / 56.6° against unit 1's 56.3 / 60.0 / 64.8 / 67.3 / 57.6 /
53.9°. Codes 1 and 6 differ by +2.8° and +2.7°, the rest by 1.2–1.4°; both units repeat to ~1°. The pattern is shared
(codes 3 and 4 are the wide ones). By the rule as agreed (STEPHEN 2026-10-06) the measured table does not ship. A
two-unit mean would leave each unit within 1.4°, where equal sectors leave each up to 6° off. Unit 2's timing scan could
not apply the ±3° offsets test (PL-215). On the shipped pair it ran clean, with 15–20° to the hold edge each way, and it
draws 2–3× unit 1's current at the same speeds (more drag). **To close:** Stephen's ruling on the table; then the
offsets question.

### PL-218 -- since DRIVER_REV 57 a timed stop ends late by the passes held in its slowdown
> **Status (2026-10-12, D6 evaluation): CLOSED, CERTIFIED at 7.4 V too** -- STOPROT 21 / 88 / 40 / 70 counts, STOPTIME
> 10 / 5 / -10 / 0 ms, peak 1,260 mA (`debug_261012-130107.log`).
>
> **Status (2026-10-12, D5 evaluation): CERTIFIED at 11.1, 14.8 and 24 V** -- every timed stop ended within -55..+15 ms,
> every stop by rotation inside -240..+180 counts. **7.4 V not run:** the qualify row ended at its second top stop by
> rotation (PL-221); the D6 sheet runs `single-stops-v7p4`.

> **Status (2026-10-10, burn-down «#3707»): CERTIFIED BY THE DOCO CLOSEOUT** -- the stop rows at 7.4 and 11.1 V:
> `R23-SGL-STOPTIME` within its band at the top (D4 read +95 and +115 ms on DRIVER_REV 57) and `R23-SGL-STOPROT` inside
> its.

> **Status (2026-10-09): FIXED at DRIVER_REV 58 (task 3705; Stephen 2026-10-08, option a), to be certified by the
> certification visit's STOPTIME and STOPROT rows at 7.4 and 11.1 V.** The held-pass wait acts only while the launch
> long `stopHold` is TRUE: the front cog sets it when a distance limit fires (`bFrontLimitsDue()`), and
> `setTargetAccel()` clears it before any nonzero command. A timed or plain stop ramps on its plan as at DRIVER_REV 56;
> a stop by rotation is held as at 57. The long was `targetAngle`, freed by PL-198, so the ABI layout is unchanged.
> Checked at the desk against every stop's promise (overlay P10). It made room by building the memory plan's WP6..WP9
> first (cog 495 -> 461 of 496, LUT run image 510 -> 499 of 512, proven identical by `tools/pasm_equiv`); the fix
> itself takes 3 cog longs (464 of 496). Desk proof (`tools/pasm_equiv --stop-hold`, against DRIVER_REV 57's logic
> with the same three instructions' timing): with the flag set, all 2,062 scenarios equal (the stop by rotation is
> unchanged); without it, the only differences are held stopping passes that now ramp on plan.
>
> (2026-10-08: OPEN, a driver defect introduced by PL-203's fix (MEASURED, D4 rows 1 and 2).)

R23-SGL-STOPTIME 11.1 V NEG-TOP FAILs at +115 ms (band ±100); 7.4 V NEG-TOP reads +95. The field's own stop time
(`field_dev_ms`) is 85 / 30 ms at 7.4 V and 105 / 40 at 11.1 V (NEG / POS), against 0 on all four on DRIVER_REV 56
(D3). At 14.8 and 24 V, where few passes are held, it is 0. The hold in `.running` acts whenever `tgt_incr` is 0, on
every stop, so on a timed stop each held pass delays the generator's ramp by one pass (0.52 ms): ~200 held ≈ 105 ms.
A stop by rotation promises distance and a stop by time promises time; the fix kept the first and broke the second.
**To close:** hold the generator only on a stop by rotation; then STOPTIME and STOPROT at 7.4 and 11.1 V.

### PL-219 -- R23-SGL-MISDIAL's premise (fixed timing) fails on the lead table, so the check reads +96..+250 ‰ (harness)
> **Status (2026-10-12, D5 evaluation): CLOSED.** Cold, the pair reads -10, -1 and +11 per mille at 7.4, 14.8 and 24 V
> against +-30 (D4's +40 at 24 V was the hot motor, as the desk found).

> **Status (2026-10-10, burn-down «#3707»): FIXED at the desk (`test_bench_single` SRC_REV 20, fmt 16); CERTIFIED BY THE
> DOCO CLOSEOUT's qualify rows.** The check fits a dedicated pass, not the ladder: one climb a sign through 650, 900,
> 1,150 and 1,400 rpm (the same at every row) at ONE pair, 304 / 48 (the lead table's flat-region pair), the schedule put
> back after; `KE_FITTED_MV_PER_KRPM` 3,630 carries the pair's own factor (the timing scans' points at 304 / 48 read -28
> / -29 per mille on the sheet's Ke on both units). Re-fit from the logs: correct supplies -22 .. +14, an adjacent
> misdial 62-83 out (+-30). About 62 s a qualify row. One exception: D4's 24 V row (unit 2) re-fits to +40.
> B1-MISDIAL2 is new (the pair and the fit's span; B1-MISDIAL is at its 280-byte bound).
>
> **2026-10-10 (later, «#3708» at the desk): ROOT CAUSE — the motor was hot (DERIVED from MEASURED rows; the tolerance
> stays +-30).** D4's 24 V qualify row (`debug_261008-152558`) is the only 24 V row on either unit that ran straight after
> range climbs: 14.8 V (14:19), 18.5 V (14:48) and 22.2 V (15:07), dc up to 1,988 mA, about 45 minutes at 20-44 W into
> an unloaded motor. Unit 1's 24 V rows (D1b, D2) and unit 2's 7.4 and 14.8 V rows ran with no range climb before them
> (no `B1-RANGE` in D1b or D2). What the row shows is a uniform loss of back-EMF per rpm, which is what a hot magnet does:
> - **The POWER rows at identical commands** (same `lib_incr`, so the same speed and the same scheduled lead) need
>   duty x supply 3.6-4.5 % lower at 24 V than at 14.8 V (`141030`): POS 25/50/75 -4.0 / -4.4 / -3.6 %, NEG -4.1 / -4.5 /
>   -4.4 %, over 1,360-4,190 rpm, both directions.
> - **The ladder rungs** at 700 / 1,400 / 2,100 rpm read -3.4 .. -4.1 %, and the model-corrected Vph / E at <= 1,450 rpm
>   is 0.989 against 1.026 at 14.8 V and 1.046 at 7.4 V on the same unit. Unit 1 at 24 V reads 1.016 (D1b) and 1.027 (D2).
> - **Every rival needs the opposite sign or a speed-dependent deficit.** Supply sag under load, the dead gap and a low
>   supply all make the motor need MORE duty; the deficit is LESS. A lead-model error would differ between rungs whose
>   leads differ (53.6-64.2 degrees); the deficit does not. The IR term is the same volts at both supplies for the same
>   speed. A 4 % fall in Ke is what 20-35 K of magnet heating gives (ferrite about -0.2 %/K, NdFeB about -0.12 %/K).
>
> **Disposition:** the check's premise is that the motor's Ke is the one `KE_FITTED_MV_PER_KRPM` was fitted at (cold
> scans). That premise is made to hold by the sheet, not by widening the band: widening to cover +40 would let a 24 -> 22.2 V
> misdial (-52 .. -80 cold) pass. The Doco closeout sheet runs every qualify row before any range climb or hand-load row,
> and states why. A hot motor needs less duty, so the driver's duty reserve and ceilings only gain when it is hot: no
> driver change.

> **2026-10-10, the supply ruled out (STEPHEN: *"i have to carefully set the power supply to be correct. i dial in the
> values so they are less that .1 off of the target value"*):** 0.1 V is 4 per mille at 24 V, so the +40 is not the
> supply; unit 2's phase voltage at 24 V sits 3.4-4.1 % under 14.8 V's at the same speeds and lead. **OPEN, a desk
> root cause owed before the Doco closeout's 24 V qualify row** (in «#3708»'s body): from D4's 24 V logs, what moves
> unit 2's line at 24 V (the lead model's terms at 24 V, the duty-to-volts scale at that supply, the unit's own Ke);
> the tolerance widens only if the cause is physics both units share, never to fit the reading.

> **Status (2026-10-08): OPEN, a harness defect (MEASURED, D4 rows 1, 3 and 6).** Mine. Subsumes PL-211.

The cell predicts the supply from the clean rungs' duty-per-speed slope, assuming duty follows back-EMF at a fixed
timing. On the Doco's lead table the lead rises with speed (52.3° at ≤ 701 rpm, ~63° at 2,100), and more lead lowers
the duty a speed needs, so the slope flattens and the predicted supply reads high: +96 ‰ at 7.4 V (rungs to 1,650 rpm),
+204 at 14.8 V and +250 at 24 V (rungs to 2,100). D2's fixed pair read +6..+68. A check whose premise is broken is a
disarmed check: it would not catch a misdialled supply. **To close:** the prediction takes the schedule's lead at each
rung into account (or judges only rungs at one lead); the next qualification runs it.

### PL-220 -- the range test's record does not say which fault ended a climb, or count hall misses (harness)

> **Status (2026-10-10, burn-down «#3707»): FIXED at the desk** (`test_bench_single` SRC_REV 20). Each range step
> records the hall missed transitions and illegal codes over it and, on a fault or a re-sync, its kind
> (`getFaultCause()`: LAG or HALL), in B1-RANGEV (B1-RANGE is at its 280-byte bound); B1-RANGEEND carries the ending
> step's kind. The Doco certification's range rows run it.

> **Status (2026-10-08): OPEN, a harness gap (MEASURED, D4 row 6).** Mine.

Both 24 V climbs ended `outcome,FAULT` / `end,FAULT` with `resyncs 1` at 734e6 (4,888 rpm). The only re-sync path is
the position fault (|err| ≥ 125), and the peak error had climbed 96 → 111, which fits PL-212's servo state. A rival
the record cannot rule on: from ~4,780 rpm the hall edges arrive faster than one per drive pass on average, and
`B1-RANGE` carries neither `hall_missed` nor the fault's kind. **To close:** `B1-RANGE` prints the step's hall-missed
and hall-illegal deltas and the fault event's kind.

### PL-221 -- at 7.4 V a top stop by rotation ended on the harness's over-current guard, 5 ticks short

> **Status (2026-10-12, D6 evaluation): CLOSED, NOT RECURRED** -- the twelve stops at 7.4 V ran with peak 1,260 mA and
> no guard trip (`debug_261012-130107.log`). Its mechanism is unexplained, only absent; B1-GUARD stays in the harness.
>
> **Status (2026-10-12): OPEN, a finding (MEASURED once, D5 row 1); no driver change licensed.** Mine.

D5's 7.4 V qualify (`DOCs/analyses/bench/2026-10-11/debug_261011-130120.log:126-127, 153`): the second NEG top stop by
rotation (limit 9,600 from the 7.4 V top, 302e6, ~99 % of no-load speed) tripped the harness guard (>= 3,680 mA for 4
samples) at `rest_net 9,595`, peak 4,380 mA; the first (7,200) at the same speed and every stop at 11.1-24 V were clean.
Its stop rows (7 cells) never ran. **Desk (servo model, a copy with a stop-by-rotation mode):** the fitted Doco
reproduces the stop (3.41 s, 1,377 ticks, ~230 held passes) with no over-current; with the rotor's stiction doubled it
sticks near the end, the trim winds duty to `duty_max` in ~45 ms and the DC link reads ~3.75 A -- the full-duty stall
at 7.4 V over the Doco's ~1.8 ohm. PL-218's stop wait is NOT the cause (the model trips identically with the wait off).
Every candidate bound (end the wait early; freeze the duty while waiting; a lower ramp-down ceiling) either changes
nothing or costs the stop's rest accuracy or the torque that frees a stuck rotor. Consistent with a position-dependent
stick at the end of the stop, not settled. **Harness, SRC_REV 21:** a guard that ends a run now prints `B1-GUARD`
(duty, duty_capped, err, state, lag_held, drv_incr, pos, enc at the tripping reading), and an aborted stop's `travel`
is to the abort (it printed minus the start position: row 1's `travel,727_445`). **To close:** the D6 sheet's
`single-stops-v7p4` runs the 7.4 V stops; clean, the cells certify; tripped again, `B1-GUARD` says whether duty sat at
its cap against a stood rotor, and the remedy (a bounded duty in the stop's last ticks, or a guard allowance for a
breakaway pulse) goes to Stephen with that evidence.

### PL-222 -- the 24 V full-speed reversal faulted once on the way down

> **Status (2026-10-12, D7 evaluation): CLOSED CERTIFIED on DRIVER_REV 62.** D7 (13 runs, Rev A unit 2, binaries
> rebuilt from 258aca9 byte for byte: ramp 51,830, stops 50,426) ran the speed-up, stop and reversal from every
> supply's top -- 7.4, 11.1, 14.8, 18.5, 22.2 V once, 24 V twice -- and the stops at each: every `B1-REVERSE` reads
> `ran,3,faulted,FALSE,resyncs,0`, every `B1-RAMPDN` `faulted,FALSE,fault_kind,NONE`, R23-SGL-SMOOTH / TOPSPD /
> RAMPARR PASS in all 7 ramp logs (RAMPARR -40..+16 per mille), no `B1-FTRACE` in any log; 21 reversals and 14 plain
> slow-downs from the tops, 0 faults (D6: 3 of 3 and 1 of 7 at 24 V). All 48 stop cells PASS; the tops' stops at
> 22.2 / 24 V now spread -66..+129 counts per drive (D5 at 24 V: -21..+74), inside -240..+180, consistent with the
> fix's cuts acting during the slow-down; their mean moved toward zero (24 V: +14, D5 +45), so no systematic shortfall. `DOCs/analyses/bench/2026-10-12/D7-EVALUATION.md`.
>
> **Status (2026-10-12, desk root cause): FIXED at the desk, DRIVER_REV 62; `VISIT-D7-RUNSHEET.md` certifies.** The servo
> model (`DOCs/plans/servo-model/spin2_model.py`, run as D6's L-ramp: the top, 2 s held, then a reversal or a stop)
> reproduces the fault: 24 V, LAG, 3.1 s into the slow-down (bench 2.4-2.7 s), and finds it at 18.5 V (0.6 s) and
> 22.2 V (2.2 s) too, never reversed on the bench; 14.8 V peaks at 121, just clear. **Root cause:** at the tops DRIVER_REV
> 59 lifted, the load angle oscillates (the 40-70 Hz swing PL-212's H-2 damps); H-2 acts only in SPIN_UP / AT_SPEED, so
> from a slow-down's first pass the swing is undamped and grows -- rotor speed ±15 %, duty 19,000-23,800 -- until a
> peak crosses 125. A stop and a reversal slow down identically until the zero crossing, which the fault precedes: the
> bench's 1-in-7 against 3-in-3 is margin. **Rejected:** the trim on the signed lag (tsign=1 and 2), the boost only
> while running (boost_run=1): both still fault at 22.2 / 24 V; H-2 in the slow-down as built (d_state=3): clean, but
> its cuts sum to the mean's drift x 16, 8-9 hall ticks short over a stop from the top, outside STOPROT's band.
> **Fix (DRIVER_REV 62, PASM, fieldSteps +2 longs):** H-2 acts ramping down too, at its gate (201e6, so the end of a stop
> and a reversal's crossing are untouched), its mean following 2^DAMP_DN_SHIFT (16) x faster there, so the cuts sum to
> the drift x 1: at most 0.72 tick from any Rev A top. Model: clean at all seven tops, stop and reversal; across J
> 2-8e-6, Tc / Bv bracket, and Lh 0.8 / 1.06 / 1.3 mH (the lead fit's 1.06; as built faults 5 of 9 there); lag peak
> 106-121 (as built at 14.8 V: 121). Lh 0.5 mH at 24 V still faults late (5.2 s), a bracket the lead fit excludes.
> The 6.5in at its 18.5 V pack (top 165e6) is under the gate: unchanged. Harness SRC_REV 22 prints the last second
> before any fault in the ramp and stops tiers (B1-FTRACE), so D7 answers either way.
>
> **Status (2026-10-12, D6 evaluation): OPEN, REPRODUCED -- the slow-down from the 24 V top faults.** Mine; the next
> step is Stephen's (trace first, or a Known Issue). Both D6 reversals faulted (`debug_261012-132842.log`, `-133712.log`):
> `fault_kind,LAG`, phase 1, 2,434 / 2,733 ms after the flip, at 760e6 / 731e6 (about 5,000 rpm). One plain stop from
> the same top faulted at the same point (`-133712.log` B1-RAMPDN POS, 2.47 s in); stops from it: 1 in 7. Every
> reversal on record from a lower top passed (21 logs, DRIVER_REV 53-61, including 24 V at its old capped top); all
> three from the 980.5e6 top DRIVER_REV 59 lifted faulted. Desk: in a slow-down only the PL-55 ceiling and the
> generator's lag gate (ease at LAG_SOFT, by J a pass, ~0.5 s to zero) hold back a rotor running ahead of the field;
> at 5,000 rpm the field moves ~45 err units a pass, so 80 + 45 reaches the 125 fault line; the trim works on |err|.
> Three mechanisms predict this record; the second before the fault (lag, duty, ceiling, increment, speed) would
> separate them and no record carries it. Harness SRC_REV 22: a stop's fault now counts in SMOOTH and B1-RAMPDN
> names it (D6's stop fault read SMOOTH PASS). D6-EVALUATION.md has the full reading.
>
> **Status (2026-10-12): OPEN, a finding (MEASURED once, D5 row 3); no driver change licensed.** Mine.

D5's 24 V qualify (`debug_261011-133743.log:122`): `B1-REVERSE ... ran,2,faulted,TRUE,resyncs,1 ... fol1_pm,0` -- the
first reversal ever run from the new 24 V top (980.5e6, 6,551 rpm); every reversal from a lower top has passed, and the
plain ramp down from this top is clean both ways, as are four stops from it. Timing places the fault within about 2 s
of the flip, above ~5,000 rpm, not at the zero crossing; a re-sync is a position fault (|err| >= 125). Desk: the
generator, the damping (off in SLOW_TO_CHG as in SPIN_DN), the lead (keyed on |speed|) and the offset choice (the field's
direction of travel, not the command's sign) are symmetric with a stop, and all their arithmetic is in range over the
reversal. The log could not say more: `B1-REVERSE` carried no fault kind. **Harness, SRC_REV 21:** it now prints
`fault_kind`, `fault_phase`, `fault_ms`, `fault_incr`, `fault_err`. **To close:** the D6 sheet runs `single-ramp-v24p0`
twice (two reversals); clean, the SMOOTH / TOPSPD reversal cells certify; faulted, the record names the kind, speed and
lag, which is what a fix needs.

### PL-223 -- a wheel stood by hand at 24 V and a 4 A limit was never latched blocked

> **Status (2026-10-12, D6 evaluation): CLOSED, CERTIFIED** -- 24 V: 4 A latched at 999 ms, 2 A at 999 ms; 11.1 V
> unchanged, 1,006-1,054 ms (`debug_261012-132655.log`, `-132446.log`).
>
> **Status (2026-10-12): FIXED at the desk, DRIVER_REV 61 and `test_bench_single` SRC_REV 21; the D6 sheet certifies.**

D5's 24 V hand load (`debug_261011-170058.log`): at 4 A, `end,NO_LATCH` with the shaft stood 1,180 ms (53 counts of
creep, under one hall tick) and `ilim 0`; at 11.1 V both steps latched on time. **Root cause:** `bFrontProtect()` counts
toward the blocked stop only on a pass with |err| >= LAG_SOFT (80) or a limiter action since the last tick
(`duty_capped + foldback_frames`). A fold arms the limit hold, which then holds the field at LAG_LIM (64); at 24 V the
stood wheel's current sat just under the fold, so after its last tick no fold fired and |err| stayed at 64 -- neither
half counted, and the drive would have pushed on indefinitely. **Fix:** the limiter sum includes `lag_held`, so a pass
the lag limiter held counts as a limiter action. A held pass needs |err| at LAG_LIM (armed) or LAG_HOLD; the LAG_HOLD
case already counted through LAG_SOFT, a turning wheel's tick still restarts the count, and the limiter half still acts
only in SPIN_UP / AT_SPEED -- so a crawl, a stop and a slow-down are untouched. **The 2 A step's `latch_tick_ms,-3`**
was the harness: the reading that showed the latch also showed a tick stamped after it (the shaft relaxing as the stop
released it), which replaced the stand's last tick; SRC_REV 21 uses the tick before when one is stamped after the latch.
**To close:** D6's `single-handload-v24p0` (both steps latch 988-1,168 ms) and `single-handload-v11p1` as its guard.

### PL-224 -- shipped source carries our project history in its comments

> **Status (2026-10-13): OPEN, BEFORE RELEASE; not started by Stephen's instruction.** Stephen: *"None of that is
> useful to a reader who's using our code as the best possible example for how to drive BLDC motors. This stuff cannot
> be in shipping code."* Doctrine overlay P8 (*shipped source is a user-facing document*) now binds new code.

**The defect:** every file a release archive set carries is read as the reference for driving a BLDC motor, and its
comments tie back to our process: punch-list ids (`PL-N`), task ids, bench visit and cell ids, design-risk and
finding labels, "STEPHEN <date>" rulings, and a per-revision driver history. A reader cannot follow any of them, and
they bury the explanation of what the code does.

**Scope (counted 2026-10-13, lines matching a PL id, a task id, a `«#N»`, a ruling, a `DRIVER_REV N` or a visit sheet):**
the closure of the six release tops (`tools/release_closure.py` over `demo_single_motor`, the four `demo_dual_motor*`,
`isp_steering_serial`), 22 files. `isp_bldc_motor.spin2` 804 lines (its DRIVER_REV history alone is about 370 lines, 7225-7595),
`isp_steering_2wheel.spin2` 162, `isp_steering_serial.spin2` 19, `isp_queue_serial.spin2` 10, `isp_serial_singleton`
and `isp_hdmi_debug` 2 each; the rest are their authorship headers, which stay. The count is a pattern match and a
floor: labels such as finding letters, cell ids and "the D5 log" are not all caught by it.

**The fix:** rewrite each such comment to say what the code does and why, in the motor's and the P2's terms, keeping
every piece of reasoning a maintainer needs; remove the revision-by-revision history (git holds it) and keep
`DRIVER_REV` as the number only. Authorship and licence headers stay. `test_*`, `util_*` and `tools/` are not shipped
and are out of scope; so are `DOCs/`. Comment-only, so no binary changes: `tools/pasm_equiv` and an image compare
prove it, then the build gate. Also the Python host demo (`pythonSrc/P2-BLDC-Motor-Control-Demo.py`): no match today,
re-checked at the sweep.

**To close:** a sweep of the 22 files with the pattern widened to every label class finds none, and each release
top's binary is byte-identical before and after. Before «#3690» (release).

### PL-225 -- the dual harness's parameter names stop one long short of the driver's run

> **Status (2026-10-13, Rev B evaluation): OPEN, FIX (harness).** Every dual log of the Rev B session reads
> `R21-DUAL-TOKTAB ... FAIL`: `BM-TOKCHK ... bad_count,1 ... first_bad,tokAbiParams`. `tokAbiParams`
> (`test_bench_dual.spin2:25949-25955`) names 27 longs ending `sense_zero`; the driver's parameter run is 28 since
> DRIVER_REV 55 (`sense_shift`, `isp_bldc_motor.spin2:7209`). The 6.5″ had not run since DRIVER_REV 49. **Fix:** append
> `"sense_shift"`. **To close:** TOKTAB PASS on the next dual run.

### PL-226 -- dual-d's lag bound read 125 on the right wheel with no fault raised

> **Status (2026-10-13, Rev B evaluation): OPEN, FIX (harness), then a rerun of `dual-d`.**
> `debug_261013-090801.log`: `BM-LAG ... motor,RIGHT ... max_err,125 ... samples,3_671` (LEFT 120; bar 124), and dual-d
> has `faults,0` in every segment and no fault event. The driver tests |err| >= 125 every frame while the bridge is
> driven and faults at once (`isp_bldc_motor.spin2:8656-8662`), so the sample is *consistent with* one taken with the
> bridge not driven (an e-stop, a coast, a stop) -- a state the bound should not judge, as it already skips faulted and
> provoked samples (`test_bench_dual.spin2:24677-24687`). The record holds the maximum only, so it cannot separate that
> from a driven 125 that went unreported. Earlier dual-d peaks: 101 / 102 (2026-09-25), 111 / 111 (09-26).
> **Fix:** the bound folds only samples taken on a driven bridge (the driver's own rule), and `BM-LAG` prints the
> maximum's time, drive state and bridge state, so the next reading settles it either way (overlay P1). **To close:**
> dual-d's LAGBND PASS with the maximum placed, on the serial visit.

### PL-227 -- the 130 MHz clock run does not print the front cog's worst pass

> **Status (2026-10-13, Rev B evaluation): OPEN, FIX (harness), then a rerun of `dual-clock clk-floor`.** The Rev B
> sheet promised *"late 0 and the worst front-cog pass under 900 us"* at 130 MHz; part CLOCK (`segClock()`,
> `test_bench_dual.spin2:4993`) never emits the steering front cog's stats -- only part D does (`dStepFrontStats()`,
> `:8234`). What the run did show: frame and pass right (`frame_cnt,2_954`, `pass_us,523`), dead gap 34 ticks, halls
> clean, the instrument cog `late,0`. **Fix:** `segClock()` ends with the front-cog stats and a judged cell. **To close:**
> the front cog's worst pass under its bound and late 0 at 130 MHz; with it PL-164 closes.

### PL-228 -- the two-wheel demo's front cog runs late passes in its debug build

> **Status (2026-10-13, Rev B evaluation): OPEN, root cause at the desk first.** `debug_261013-091106.log` (demo-dual,
> 270 MHz, the library's debug channels on): 11 `PLATFORM EV_LATE_PASS` events in 64 s -- one a second at 1,344 /
> 2,344 / 3,344 / 4,344 ms, then at each drive's start and stop. dual-d, the same steering object at the same clock built
> `BENCH_QUIET`, reads `late,0` and FRONTST PASS; demo-single (its own front cog) logs none. Suspect, not settled: the
> front cog's own debug output in a debug build. **To close:** the cause named from the code (what runs on the front cog
> at those instants, with and without the channels), then fixed or documented; a plain build's behaviour stated.

---

## Removed from this list

**Killed by Stephen, 2026-10-01** (*"if we are not doing something by decision why put it in punch list? kill PL173,
PL171."*): **PL-173**, the external measurement front end (decided against 2026-09-14; its design stays in
`DOCs/plans/archive/BENCH-READINESS-SPRINT-PLAN.md` §2A), and **PL-171**, the watch on the Pi's loader checksum refusals.
Neither is raised again; their numbers are not reused.

**Legacy sync scripts** (`src/chk`, `src/get`, `scripts/get`, `scripts/getKS`,
`scripts/diffSrc`). Tracked here briefly on 2026-09-09, then removed at
Stephen's direction — **their removal is his to do, not this list's**.

The operating rule stands and is recorded in `CLAUDE.md` and
`.claude/skill-conventions.md`: all work happens in this work tree, and these
five must not be run — `src/get` and `scripts/get*` copy *into* `src/` and would
overwrite the tree from a stale external source. They are vestiges of sharing
source between a Mac and a Windows machine, which the cross-platform
`pnut-ts` / `pnut-term-ts` toolset made unnecessary.

*This section is last on purpose: anything appended to the file lands after it, in a section of its
own, rather than reading as though it had been removed (see the 2026-09-17 filing correction above).*
