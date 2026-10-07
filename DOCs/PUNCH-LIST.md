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

### The register after 6.1.0 — 2026-10-03

Every open entry sits in exactly one group below; its own heading carries the detail. Each group was checked against
the tree and the three 6.1.0 visits' logs on 2026-10-03, at the HOLD-SPEED sprint closeout. v6.1.0 is tagged
(`54f7c43`); the next plan is the DocoEng motor's qualification.

**Harness, corrected at the 6.1.0 closeout; runs on the next floor visit** (`test_bench_dual` SRC_REV 82)

| Entry | What it is | What closes it |
| --- | --- | --- |
| PL-182 | The slow spin leg's full trace stopped at the usual cap, so LIMGIVE's held passes are unplaced | `floor-auto` emits every sample of the slow leg |
| PL-192 | LDHUNT counted a single held limiter engagement as hunting; also watches SPINSTOP (one stop a tick past tolerance) | `floor-grab` reads 0 on a single engagement; SPINSTOP over the next `floor-auto` |

**Watches from the 6.1.0 visits** — each needs no load of its own: PL-181 (the boost fires in calm running under load;
SPINERR's band), PL-184 (the schedule's current at the quarter by direction; information), PL-190 (SRVKEEP's fixed
reference reads a day's spread as a regression), PL-191 (a speed raised while a wheel is still slowing dips first; the
ramp generator's, with PL-160).

**Tooling:** PL-178 (`tools/pasm_equiv` compares against a baseline from before the hold-speed fix).

**Fixed in the tree; waits for its binary's next run** (no planned run loads these binaries, so nothing is owed)

| Entry | Binary | What the tree holds |
| --- | --- | --- |
| PL-23 | `t0`, `spin` | Booleans print as TRUE/FALSE; the next `t0` log shows `rev_b` as a word |
| PL-20, PL-21 | `char` | The overflow-proof running mean and the quiescent hold on a started driver (header, `:231`, `:268`) |
| PL-44 | `detect` | Its last trapped capture removed (`:1266`); the `t0` and `char` halves certified at Visit 2 |
| PL-53 | `char`, `detect` | Every record built through `isp_bench_log`; identical by construction |
| PL-64, PL-65 | `dual-ui`, `dual-floor` | The rebuilt walkthrough and the corrected plan labels (SRC_REV 12); neither tier has run since. The `dual-floor` panel bitmap still reads the grab's old 4 A limit (now 2 A): regenerate it with `tools/gen_dual_assets.py` where its font exists, before that tier next runs |
| PL-134 | `t0-stopmode` | The rate estimate counts only while holding (SRC_REV 17); no `t0-stopmode` run since 2026-09-24 |

**Dormant: the commutation scan** — PL-46, PL-98. 6.0.0 commutates from the motor's measured hall position and a lead
that follows speed (CHANGELOG v6.0.0), the scan last ran on 2026-09-21, and no plan uses it. They wake if a
characterisation plan takes up the scan.

**Deferred by Stephen's rulings**
- **Serial** (*"serial testing not in this initial release"*, 2026-09-27): PL-111's serial half, PL-148, PL-154, PL-157.
  All three builds are in the tree (`protclear`/`getprot`, the idle poll, the digits check, the 6.0 getters); what each
  waits for is a host-driven hardware run.
- **DocoEng** — no longer deferred: the v6.2.0 sprint (the DocoEng qualification) takes PL-27 and PL-71 in «#3684»,
  from D1b's measurements (2026-10-05).
- **After v6.0.0:** PL-102 (a "following" getter), PL-164 (clock range), PL-165 (the DEBUG footprint measure), PL-166
  (the inertia term).
- **Moved here from the task board at 6.1.0 start (2026-10-01)**, so the board carries only the sprint's work:
  PL-174 (vibration study), PL-175 (N-motor shape), PL-176 (motor-adoption
  tool), PL-177 (back-EMF delta release).

**Ships as a Known Issue:** PL-118 (phase-short braking is not current-limited; ruling 1 A); PL-193 (the pack voltage
is not used by the drive), PL-194 (regenerative current is not shown), PL-195 (the hold's defaults sized unloaded),
PL-196 (`calibrate()` does nothing) — the v6.1.0 entry's other Known Issues are PL-164 (clock), the DocoEng group and
the serial group below.

**Watch** — each run carries what would make it actionable, at no extra load: PL-43 and PL-126 (silent stops, one
instance each since the supply repair), PL-120 (the right board's high side; no refusal in the 69 Rev B program loads
logged since 2026-09-27, 35 of them naming the right wheel, after the 2026-09-26 header reseat), PL-136 (the PREFLT diagnostics, which certify themselves on a wheel's first failure), PL-139
(the at-rest band, crossed once on each board).

**Ancillary, recorded and not chased:** PL-60, PL-63, PL-103, PL-105, PL-108, PL-109, PL-110, PL-119, PL-135, PL-170.

**Found during v6.2.0** (2026-10-03 onward; each heading carries its evidence): PL-197 (a two-stage request's ack
bound, desk), PL-198 (`moveShaftToAngle()` does nothing), PL-199 (350 MHz sense noise), PL-200 (a timed crawl stop
rested late once); PL-201 merged into PL-170 (listed under Ancillary above: Rev A's fold at a test-use limit fires on
noise — measured again on the Doco, and now needed by D2's hand-load limit cell); PL-202 (T0-27's one-frame premise,
superseded on Rev A by DRIVER_REV 55's filtered fold); from D2's first rows (2026-10-06): PL-203 (POS stops by rotation
rest early at the top), PL-204 / PL-205 / PL-206 (harness: the scan's walk, a hunting point fitted, MISDIAL per sign),
PL-207 (the adoption tool's stale 2 A record), PL-208 (the 7.4 V slowest speed swapped direction).

**Standing rulings carried from 6.0.0:** the fault-return run faults its wheel with the guarded `testForceFault()`, not
the wrong-offset write (STEPHEN 2026-09-28, *"fp1: A"*); a test built on a wrong premise is corrected before it runs
again (STEPHEN 2026-10-01).

### PL-20 -- `BC-SENSE` `i_mV_avg` overflows a long at the pre-S-3 scale

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench stop-rest reading)

**Found 2026-09-15 in Visit 2.** Minor.

**MEASURED:** traces 25 and 28 end `why,NOT_REACHED` (`debug_260915-134805.log:7888,8787`), although
both reached STOPPED after 19 ticks, like every other quarter-speed stop. Every other STOPMODE trace
confirmed rest.

**Consequence:** the C-4 table has no time to rest for that one cell. Its tick count is complete.

**Fix direction:** read those two traces' last samples for the value that kept changing (`pos`, `hw`
or both), then decide whether the stillness rule or the reading is at fault.

### PL-64 -- the attended-test UI is out of step with what each test needs, and `dual-ui` failed itself

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench watch, one instance)

**Found 2026-09-24** in the first `dual-fault` try of pass 3 (evaluation §3). This ran the pass 2 binary.

**MEASURED:** the last record is `BM-START,seq,4_886,...,RIGHT,life,23` at 13:42:15.410. Then
`usb-traffic_260924-133841.log` shows `$20 $00` at 13:42:17.554 and four lone `$00` bytes over 49 s. No other capture in
the set holds one. The harness watchdog printed nothing. The rerun and pass 2 both passed the same trial.

**Undetermined:** a P2 reset, a supply loss, or a hang with its TX line disturbed. The log cannot separate them.
**Watch:** the next run sheet says in advance what to look at if the log stops scrolling. A second instance, or that
observation, makes it actionable. Owner: each visit's log analysis (now «#3634»; «#3613» closed 2026-09-30).

### PL-134 -- HOLD-RISE's rate estimate kept counting after the hold slipped

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

> **Status (2026-10-02): WATCH, 6.1.0** (evaluation §3.1, F-4 and F-8). No speed is lost; the bound or D-2 is not touched
> until the model says whether the boost firing in running matters.

**MEASURED 2026-10-02** (`debug_261002-103332.log` `BM-SPINW` seq 30-58): on the slow and medium schedule legs `err_pk`
read 79-90 on 7 of 8 wheel-legs (SPINHUNT FAIL LEFT 4 / RIGHT 3 of 4, bound 76); the duty swing fell to 95-539 from
DRIVER_REV 46's 900-1,650. The model predicted `err_pk` 67-76 (design §5; R2 named A-3's 76 as the guard). SPINERR's
means read 43-46 at slow against the wheels-up 47-49 band, as on 2026-09-30 (unchanged by the fix). **Settles it:** the
model's slow / medium legs at the floor's inertia, with and without D-2.

### PL-182 -- LIMGIVE's sampler scores a hold during the spin-up as the field giving way

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

> **Status (2026-10-02): OPEN, information, not this fix** (evaluation §3.1, F-7). The timing (PL-105's area), which
> D-1..D-5 do not touch.

**MEASURED 2026-10-02**, the first measurement of SPINLEAD: 1.17 / 1.30 against 1.05. Clockwise (leg 7 against 9) the
schedule draws less than the fixed pair (`amps` 990 against 1,043, 779 against 856); counter-clockwise (leg 8 against
10) more (1,259 against 878, 1,824 against 1,137). One pass each way, no repeat. **Settles it:** a repeat of the quarter
pairs, both directions, before any claim about the schedule's saving at the quarter on the floor.

### PL-190 -- SRVKEEP's fixed reference reads a day's spread as a regression

> **Status (2026-10-03): WATCH, harness** (second 6.1.0 visit §2.1, G-5).

**MEASURED 2026-10-02:** three re-visited rung windows read net current 5.6-7.7 % over the 2026-09-27 DRIVER_REV 46
reference (rid 22, 41, 136 of `debug_261002-134026.log`); duty within; pack 20.2 V against 20.5 the same morning; the
steady drive is unchanged by construction (`tools/pasm_equiv`, C4 / S-1 neutralised: 112 of 112 equal). **Settles it:** a
same-session control, or a band derived from repeat runs of one driver.

### PL-191 -- a speed raised while a wheel is still slowing dips before it climbs

> **Status (2026-10-03): WATCH, the ramp generator (PL-160's)**; Known Issues evidence (second 6.1.0 visit §3.4, G-9).

**MEASURED 2026-10-02** (`debug_261002-143653.log` 161.1-161.5 s): the stick went 0 → 5 → 35 → 45 while LEFT was slowing
from 56.6 ×10⁶; the jerk-limited generator unwound the deceleration first, the field fell to 6.8 ×10⁶ (12 % of its new
target) for ~300 ms, the wheel stood, and the steering object scaled both wheels (`EV_PATH_LIMIT` 184 ‰). Twice in the drive.

### PL-192 -- LDHUNT fails a single clean limiter engagement by its own definition

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

> **Status (2026-10-05): OPEN, a finding (MEASURED once).** D1b's pass probe at `clk-350`
> (`DOCs/analyses/bench/2026-10-05/debug_261004-184638.log`).

Undriven, before any drive, `B1-ZERO ... spread_mv,35` at 350 MHz against 3-5 mV at 200, 270 and 271.25 MHz on the same
board and motor; the run then tripped the harness's over-current guard at a "5.4 A" reading (27 mV at Rev A's 5 mV/A,
inside that noise) on a motor that was not turning. A clock-dependent sensing defect falls under doctrine overlay P14.
**To close:** the next Doco visit's `clk-300` probe records the same rest-zero spread before it drives, which places
where the noise starts; then root-cause it at the desk (the sense ADC's sampling at the running clock — the frame and
the SINC window scale with it — before any hardware explanation).

### PL-198 -- `moveShaftToAngle()` has had no effect since DRIVER_REV 38

> **Status (2026-10-04): OPEN, a finding.** Found during task 3679 (looking for a fixed-field test path for the Doco's
> hall-zero reference).

`moveShaftToAngle()` (`src/isp_bldc_motor.spin2`, *TESTING USE*) writes `targetAngle`, but the PASM block that read it
(*TEST-EXERCISER SUPPORT CODE*, inside the drive pass's request handling) is commented out, and its own note says no path
reaches it since DRIVER_REV 38. So the method returns `NO_ERROR` and moves nothing; a second call returns `ERR_BUSY`
forever, because nothing clears `targetAngle`. **To close:** either remove the method and the dead block (and the
launch long's comment), or re-enable a fixed-field path deliberately (cog/LUT space is near full, overlay P13); the
Doco's hall zero is referenced to the offset scan's current minimum instead (task 3679).

### PL-200 -- a timed crawl stop on the Doco rested 120 ms after its field stopped

> **Status (2026-10-05): OPEN, a finding (MEASURED once).** D1b third pass, 18.5 V
> (`DOCs/analyses/bench/2026-10-05/debug_261005-132917.log`, `B1-STOP,sign,NEG,kind,CRAWL,by,MS`; evaluation D1B-12).

A 3 s crawl at power 5 (NEG) stopped its field on time (`field_dev_ms,0`) and the shaft came to rest 120 ms later
(R23-SGL-STOPTIME `measured,120`, band ±100); its position was in band (`dev,120` counts of −240..+180). The other 23
stop-by-time instances across five voltages read −70..+95 ms. **To close:** D2 re-judges R23-SGL-STOPTIME at every
voltage on the tuned Doco tables; if the late rest recurs, root-cause at the desk why the shaft moves on after a
crawl's field stops (the hold the stop applies at power 5, against the cell's rival named in its own note).

### PL-201 -- on a Rev A board a low current limit folds back on sense noise and the motor stops following

> **MERGED into PL-170 (2026-10-05)** — the same defect, measured on the 6.5″ on 2026-09-30. Filed the same day with two
> errors corrected there: it is not user-affecting (no public method sets a limit; users run at 40/27 A), and the
> 6.5″ did not escape it (it folded on noise in 0.06-4.3 % of frames on Rev A at 2 A). The number is not reused.

### PL-202 -- T0-27 judges Rev A's fold-back on one frame's reading, which DRIVER_REV 55 no longer folds on

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

> **Status (2026-10-06): OPEN, a harness defect (MEASURED, D2 row 1).**

At 11.1 V 25 % NEG the −15° point held the field 54 passes with `err_pk` 104 and mean error 32 (the drive hunting), yet
`B1-OFSPT ... clean,TRUE`, so `ofsFit()` took it: the vertex moved to +9.5° (50 %: −2.7°) and R23-SGL-LEADMOVE FAILed on a
12.2° spread. **To close:** a point with held passes is not clean (as the adoption tool already rules: HUNT).

### PL-206 -- R23-SGL-MISDIAL judges each sign alone, so the direction asymmetry fails it (harness)

> **Status (2026-10-06): OPEN, a cell defect (MEASURED, D2 rows 1 and 3).**

The cell predicts the supply from each sign's duty line and fails either beyond ±30 ‰: 11.1 V NEG −22 / POS +37, 7.4 V
NEG −80 / POS +93. A misdialled supply moves both signs alike; the direction asymmetry moves them apart. Their mean,
+7.5 ‰ and +6.5 ‰, is the misdial reading (PASS); the half-difference is the asymmetry. **To close:** judge the mean of
the two signs; print the half-difference as the asymmetry, not judged here.

### PL-207 -- the adoption tool's Doco record scans at 2 A, a limit the harness left at D1b (tool)

> **Status (2026-10-06): OPEN, a stale record value (MEASURED, D2 rows 1 and 3).**

`util_adopt_motor.spin2`'s DocoEng record carries scan 2 A / ladder 3 A, the harness's test limits until SRC_REV 14 moved
it to the library's 40 A (STEPHEN 2026-10-05 "yes A"). At 2–3 A on Rev A this motor's crawl-speed phase current reaches
the limit: 5° from the start a point hunts and the next droops (7.4 V 560 rpm NEG: d+5 HUNT held 73, d+10 DROOP 469 ‰),
and the 280 rpm rung droops (488 ‰), so no fit resolves and no ceiling is found. **To close:** the record at the
library's limits, its abort at 3.68 A as the harness's; rerun `doco-adopt-v11p1` and `-v7p4`.

### PL-209 -- the adoption tool walks into the Doco's torque wall at 40 A and ends on an over-current (tool)

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

> **Status (2026-10-07): OPEN, a test set-up gap (MEASURED, D2 row 2).** The set-up is Stephen's (overlay P1).

At 4 A and 2 A the limit acted with no fault (R23-SGL-LIMHOLD PASS), but the shaft never stopped (standing ≤ 5 ms,
creeping 48–104 thousand counts under the grip), so R23-SGL-BLKSTOP is NOMEAS at every step. 0.034 N·m/A: 136 mN·m at
4 A, 68 at 2 A — ~20–45 N at the fingertips on a shaft a few mm across; at a 25 mm radius, 3–6 N. **To close:** rows 2
and 8 again with a grip of about that radius on the shaft.

### PL-211 -- R23-SGL-MISDIAL fails at 14.8 and 22.2 V and passes at the rows between

> **Status (2026-10-07): OPEN, unexplained (MEASURED, D2 second pass).**

The signs' mean reads +48 ‰ (14.8 V) and +68 ‰ (22.2 V), against +26 / +6 / +19 at 11.1 / 18.5 / 24 V. A Ke error would
move every row alike; a supply set 5–7 % high at those two rows, the supply rising under regeneration, or the cell's own
spread all fit. **To close:** the supply's setting at those rows (Stephen); then either nothing, or the cell's tolerance
re-derived from its measured spread.

### PL-208 -- the Doco's slowest steady speed at 7.4 V swapped direction between D1b and D2

> **Status (2026-10-06): OPEN, a table value (MEASURED, D2 row 3).**

D1b (REV 53): NEG 1.00 ticks/s steady, POS 4.00. D2 (REV 55, the per-direction pair): NEG 4.00 (3.00 not), POS 1.00
(0.75 not) — so the shipped forward minimum (1.00, `confgurePowerLimits()`) did not crawl steadily, and R23-SGL-MININC
NEG FAILed. Each rung is one 2 s sample at the duty floor; the edge is not repeatable to one rung. **To close:** the
7.4 V minimum (and 11.1 / 12.0 V, DERIVED from it) set to the larger of both runs, 4.00 ticks/s each way, until a
repeated measurement shows a lower one steady every time.

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
