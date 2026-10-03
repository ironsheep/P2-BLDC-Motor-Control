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
release burn-down that headed this list until then is in git history (`git show d72e7ed:DOCs/PUNCH-LIST.md`).

### The register for 6.1.0 — 2026-10-01

Every open entry sits in exactly one group below; its own heading carries the detail. Each group was checked against
the tree on 2026-10-01, not against an earlier status line.

**Scope (STEPHEN 2026-10-01):** the planned scope (option (a)), then *"pull in any bench harness work that directly
relates to tests we will run during this plans effort, pull in the simple changes/fixes"*. The tests this plan runs are
the wheels-up checks of the PL-167 fix and the floor run that certifies it, on `test_bench_dual` and the runner.

**In 6.1.0 — the plan's work**

| Entry | What it is | What closes it |
| --- | --- | --- |
| PL-167 | Under a heavy load the drive gives up speed with torque to spare (the headline; a v6.0.0 Known Issue) | Speed held: CERTIFIED 2026-10-02. Shippable once PL-179 is fixed and certified |
| PL-179 | ⛔ Under D-5 a blocked platform does not stop itself (found 2026-10-02) | «#3662»: desk root cause, the fix, its visit |
| PL-180 | Lag faults on hard transients and a slow-down kick, new at DRIVER_REV 47 (found 2026-10-02) | «#3662», root cause first, with PL-179 |
| PL-168 | Floor-test premises the runs proved wrong | Four of five CERTIFIED 2026-10-02; the coast bound waits for PL-179's visit |
| PL-182, PL-183, PL-185 | Three more wrong premises the 2026-10-02 visit found (LIMGIVE in spin-up, SPINPEAK's limit, the grab) | Re-premised before each runs again |
| PL-132 | The blocked-wheel stop shorted the phases under coast (fixed DRIVER_REV 20) | Its COAST cell, on PL-179's visit |
| PL-160 | The quarter-speed start under load | CERTIFIED 2026-10-02 (SPINSTRT, drop 0) |
| PL-67 | Two motor pin groups that overlap are not refused | DONE 2026-10-01: refused at compile time, proved by `tools/build-check.sh` step 3a |

**In 6.1.0 — harness work for the tests this plan runs**

| Entry | What it is | What closes it |
| --- | --- | --- |
| PL-96 + PL-97 | A record label can print `?` or adjacent memory with no signal (four instances, the latest at `test_bench_dual` SRC_REV 70) | ✅ CERTIFIED 2026-10-02 (`dual-tokneg` FAIL, TOKTAB PASS elsewhere) |
| PL-68 | No bench log names the commit it was built from | ✅ CERTIFIED 2026-10-02 (every banner `0ba9b96`) |

**In 6.1.0 — simple fixes**

| Entry | What it is | What closes it |
| --- | --- | --- |
| PL-12 | The style gate's C4 check can flag a PRI code line carrying a trailing `''` | DONE 2026-10-01 (also A4, A5) |
| PL-172 | The style gate's `--self-test` fails: check T128 has no fixture | DONE 2026-10-01 |
| PL-23 | Booleans print as numbers in two places still: `test_bench_spin` and `testGetResults()`'s fault flag | FIXED IN THE TREE 2026-10-01; the next `t0` log shows it |
| PL-37 | Five panel bitmaps and their generator outlived the panel | DONE 2026-10-01 |
| PL-169 | The FlySky demos re-send the acceleration setting on knob noise | Deadband CERTIFIED 2026-10-02; the ends wait for a drive that turns both knobs to their stops |

**In 6.1.0 — watches from the 2026-10-02 visit:** PL-181 (the boost fires in calm running under load; SPINERR's band),
PL-184 (the schedule's current at the quarter by direction; information, not this fix), PL-186 (in a fast pivot turn
the coasting inner wheel is driven backward; a behaviour choice for Stephen).

**Fixed in the tree; waits for its binary's next run** (no planned run loads these binaries, so nothing is owed)

| Entry | Binary | What the tree holds |
| --- | --- | --- |
| PL-20, PL-21 | `char` | The overflow-proof running mean and the quiescent hold on a started driver (header, `:231`, `:268`) |
| PL-44 | `detect` | Its last trapped capture removed (`:1266`); the `t0` and `char` halves certified at Visit 2 |
| PL-53 | `char`, `detect` | Every record built through `isp_bench_log`; identical by construction |
| PL-64, PL-65 | `dual-ui`, `dual-floor` | The rebuilt walkthrough and the corrected plan labels (SRC_REV 12); neither tier has run since |
| PL-134 | `t0-stopmode` | The rate estimate counts only while holding (SRC_REV 17); no `t0-stopmode` run since 2026-09-24 |

**Dormant: the commutation scan** — PL-46, PL-98. 6.0.0 commutates from the motor's measured hall position and a lead
that follows speed (CHANGELOG v6.0.0), the scan last ran on 2026-09-21, and no plan uses it. They wake if a
characterisation plan takes up the scan.

**Deferred by Stephen's rulings**
- **Serial** (*"serial testing not in this initial release"*, 2026-09-27): PL-111's serial half, PL-148, PL-154, PL-157.
  All three builds are in the tree (`protclear`/`getprot`, the idle poll, the digits check, the 6.0 getters); what each
  waits for is a host-driven hardware run.
- **DocoEng** (*"doco support in subsequent release"*): PL-27, PL-71. PL-71 is a one-line fix, but it changes how the
  DocoEng motor starts and cannot be checked without that motor, so it stays with the DocoEng work.
- **After v6.0.0:** PL-102 (a "following" getter), PL-164 (clock range), PL-165 (the DEBUG footprint measure), PL-166
  (the inertia term).
- **Moved here from the task board at 6.1.0 start (2026-10-01)**, so the board carries only the sprint's work:
  PL-174 (vibration study), PL-175 (N-motor shape), PL-176 (motor-adoption
  tool), PL-177 (back-EMF delta release).

**Ships as a Known Issue:** PL-118 (phase-short braking is not current-limited; ruling 1 A).

**Watch** — each run carries what would make it actionable, at no extra load: PL-43 and PL-126 (silent stops, one
instance each since the supply repair), PL-120 (the right board's high side; no refusal in the 69 Rev B program loads
logged since 2026-09-27, 35 of them naming the right wheel, after the 2026-09-26 header reseat), PL-136 (the PREFLT diagnostics, which certify themselves on a wheel's first failure), PL-139
(the at-rest band, crossed once on each board).

**Ancillary, recorded and not chased:** PL-60, PL-63, PL-103, PL-105, PL-108, PL-109, PL-110, PL-119, PL-135, PL-170.

**Standing rulings carried from 6.0.0:** the fault-return run faults its wheel with the guarded `testForceFault()`, not
the wrong-offset write (STEPHEN 2026-09-28, *"fp1: A"*); a test built on a wrong premise is corrected before it runs
again (STEPHEN 2026-10-01).

### PL-12 -- latent: `check_pri_docs` conflates "has a trailing comment" with "is a comment line"

> **Status (2026-10-01): DONE** («#3646»). `check_pri_docs()` now ends the doc scan at any line whose code portion is
> not blank, as `check_pub_docs()` does. The audit of the other checks found the same conflation in two more: A5 (a CON
> constant with a trailing `' ----` counted as a separator line) and A4 (a code line with a trailing `''` at the top
> counted as header); both now require a comment-only line. C3a-C3f already read the code portion; C6, C6b and the
> signature's trailing-comment test are about declaration lines and are correct as written. `conformant.spin2` carries
> a PRI body line with a trailing `'`, one with a trailing `''`, and a CON constant with a trailing `' ----`; MEASURED:
> before the fixes the self-test reported C4 and then A5 on it, after them it exits 0 and `tools/check_style.sh` passes
> over `src/`.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (style-gate tooling, latent)

`tools/check_style.sh`'s C4 check (guide 4.4, PRI docs must use `'` not `''`)
tests `rec['comment_kind'] == "''"` line-by-line after a PRI signature without
first checking that the line's **code portion is blank**. `comment_kind` records
*"this line carries a comment"*, not *"this line is comment-only"* -- so a PRI
**code** line ending in a trailing `''` comment would be reported as "PRI method
doc uses `''`" when it is not a doc line at all.

**No in-tree site trips this today** -- verified independently, no PRI body line
in `src/` carries a trailing `''`. So C4's current count of 9 is correct and
there is no observable defect. It is recorded because it is *latent*: the first
PRI body line written with a trailing `''` comment turns it into a false
positive, and a gate's false positives are what get gates switched off.

This is the **same conflation class** that caused the C3c defect fixed during
#3471 (see the root cause note in `tools/check_style.sh`), found while auditing
the other checks for that pattern. C3a/C3b/C3c/C3d/C3e are not affected -- they
all read the `prologue` list, which the C3c fix corrected at source. The
remaining checks were not exhaustively audited for it; doing that audit is part
of this item.

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (Doco motor, after 6.0)

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

### PL-37 -- the meter-panel assets outlived the panel they drew

> **Status (2026-10-01): DONE** («#3648»). The five `bc_*.bmp` and `tools/gen_bench_char_assets.py` are removed
> (`git rm`); the note on measuring text width now lives in the `fit()` of `tools/gen_t0hand_assets.py` and
> `tools/gen_dual_assets.py`, and the two "same discipline" pointers name `tools/gen_dual_assets.py`. MEASURED: no
> reference outside `DOCs/` remains; both generators import; `test_bench_t0` (`t0-hand`) compiles.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (unused bench panel assets)

**Found 2026-09-14 in «#3521».** The meter-free rework removed `test_bench_char.spin2`'s PLOT panel
(commit `7595274`), so nothing in that binary references its layer assets any more.

**The assets:**
- `src/bc_bg.bmp`
- `src/bc_caption.bmp`
- `src/bc_digits.bmp`
- `src/bc_labels.bmp`
- `src/bc_button.bmp`
- the generator `tools/gen_bench_char_assets.py`

**Why they are still in the tree.** Deleting them first needs a tree-wide search confirming that
nothing else consumes them. Neither the arbiter nor its agents had a search tool in that session,
and the project does not search through the shell.

**Decision.** STEPHEN, 2026-09-14: *"leave them for now"*.

**What has been read so far:**
- There is no reference in `src/test_bench_char.spin2`, `tools/build-check.sh`,
  `tools/check_style.sh`, `tools/bench-run.sh` or `.gitignore`.
- The rest of the tree has not been searched.
- `DOCs/PUNCH-LIST.md` PL-19 still mentions the generator.

**To close:** in a session with a search tool, confirm there are no consumers, then delete the six
files and update PL-19's mention.

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

### PL-68 -- no bench log names the commit it was built from, so a visit ran on an older commit unnoticed

> **Status (2026-10-02): ✅ CERTIFIED by the 6.1.0 visit:** all seven logs print `commit,0ba9b96` (`BM-COMMIT` in the
> six dual logs, `RC-BANNER` in `floor-rc`), the pack's commit. **Earlier: BUILT** («#3652», c60c0df and its follow-up). Every harness
> banner prints the commit (`test_bench_dual`: a `BM-COMMIT` record after `BM-BANNER`); `src/isp_bench_commit.spin2`
> reads `NOT_A_PACK` in the tree and is rewritten only in the pack's archive copy. MEASURED: a pack from c60c0df holds
> `c60c0df` in `dual-a.bin` and `t0.bin` and no `NOT_A_PACK`; a source-tree build holds `NOT_A_PACK`; `git status` is
> clean after the pack build. The runner echoes `git rev-parse --short HEAD` and the `src`/`tools` status before a
> source-tree compile (both limbs exercised), and skips it in a pack build.
>
> **Earlier status (2026-10-01):** IN 6.1.0, harness work for this plan's runs. **Design RULED (STEPHEN 2026-10-01, "re pl68
> yes A"):** the pack builder writes a tiny object holding the commit into its temporary `git archive` copy (never this
> tree), and every harness banner prints it; a tracked default copy reads "not a pack", so a build from the tree says
> so; the runner also echoes `git rev-parse HEAD` and the tree's clean state before any source-tree compile.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench provenance tooling)

**Found 2026-09-16 in Visit 3** (`analyses/bench/2026-09-16/VISIT-3-RESULTS.md` §1).

**MEASURED:**
- The Visit 3 sheet was written for tree `9bdb9ea`, harness `SRC_REV 11 / FMT 3`.
- Both motion logs print `src_rev 7, fmt 1` (`debug_260916-120132.log:21`, `debug_260916-120254.log:21`).
- OVERSHT ran at 75 % with no `BM-FLTAPI`, and the runner was the one from before `13d5c46`.
- The four repairs the visit existed to certify did not run. It was found only by reading the banners.
- The cause, from `git reflog show origin/main`: the remote stood at `6aed714` until 2026-09-16 12:18, so the
  bench's pull (STEPHEN: *"i'll pull before running. I always do"*) got `6aed714`. The Visit 3 commits were not
  yet on the remote.

**The gap (DERIVED):**
- `SRC_REV` is hand-bumped per harness file, so it identifies the harness, not the tree.
- A library-only commit such as `17122f2` leaves every banner unchanged. So even a careful read cannot say
  whether a given driver fix was in the binary.
- Nothing on the console or in any log names the commit.

**Fix direction (for Stephen: the runner is a tool that fronts his toolchain, doctrine P2):** the bench
runner echoes the checkout's commit, and whether the tree is clean, before it compiles. Every console then
records what was built, visibly and replayably. Carrying the commit into the log banner too, via a `-D`
value, would make each log self-describing.

*Note, 2026-09-16:* the cause was commits not yet on the remote; the next run on `53c1f2b` had the right banners.
The finding stands: a log still cannot name its commit.

### PL-71 -- the DocoEng motor's minimum forward increment is `0 - VALUE_NOT_SET`, which is 1

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (Doco motor, after 6.0)

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

> **Filing correction, 2026-09-17.** PL-67 was sitting below *"Removed from this list"*, which
> reads as though it had been withdrawn. **It has not** — it is an open harness gap. It is restored
> to an open section here, and the *Removed* note has moved to the end of the file where it cannot
> capture a later entry the same way. No wording of PL-67 was changed.

### PL-67 -- `R2-DETECT-OVERLAP` is owed to a motors-unplugged session, but no build can produce it

> **Status (2026-10-01): DONE** («#3650»). Both configurations of `isp_bldc_motor_userconfig.spin2`, and the bench
> config, carry `CHECK_` constants that divide by "the base is a legal group" and (dual) "the bases are 16 or more
> apart"; each check line's comment tells the user what to change. `tools/build-check.sh` step 3a compiles temporary
> copies with a right base of 24, an overlapping 16/8, an equal 32/32 and a single base of 24, and requires each to
> refuse at its named `CHECK_` line; the swapped legal pair 32/16 must compile. MEASURED: all five behave; with the
> checks disarmed in a scratch copy the step fails all four refusals. `DEVELOP.md` says what the refusal looks like.
>
> **Earlier status (2026-10-01, closeout): 6.1.0 work, by Stephen's ruling.** *"it can be produced and should be failed at
> compile time."* Two motor pin groups that overlap are a configuration error the compiler can see (both bases are
> constants in `isp_bldc_motor_userconfig.spin2`), so the build is refused, and `tools/build-check.sh` proves the refusal
> the way it proves a build with no `CFG_*` selected. The runtime `GATE_OVERLAP` skip in `test_bench_detect` stays as it is.
>
> **Shape (2026-10-01, plan research).** The preprocessor cannot compare numbers (p2kb `p2kbSpin2PreprocessorOverview`: no
> `#IF`, no expression evaluation), so the refusal is a CON constant that divides by "the bases are legal and clear";
> pnut-ts refuses it with `Divide by zero (m145)` at that line and a non-zero exit (prototyped). Legal enums alone do not
> prevent an overlap: bases 0/8, 8/16 and 32/40 share pins, and equal bases are one group (Stephen asked 2026-10-01). So
> the config checks both membership in the legal set and the pair's separation (`|L - R| >= 16`). At run time `start()`
> already refuses both (`ERR_BAD_PIN_GROUP`, `ERR_PIN_GROUP_IN_USE`, `isp_bldc_motor.spin2:4107, :4122-4125`).
>
> *Was (2026-09-26 audit):* ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (detection harness gap)

**Found 2026-09-15** while writing the Visit 3 run sheet. DERIVED from source. It is a **gap in the harness**,
not a driver defect.

**The claim that fails.** Every record since Visit 1 says the deferred cell `R2-DETECT-OVERLAP` is "owed to the
first session where the motors are unplugged" (`plans/VISIT-SIGNOFF-DESIGN.md` §J.2), and the Visit 3 scope
carried it as a no-code rider on the Rev A swap load.

**MEASURED, in `src/test_bench_detect.spin2`:** the gate-input guard is computed at runtime from
`user.LEFT_MOTOR_BASE` and `user.RIGHT_MOTOR_BASE` "in every sweep of every build" (its header, and the
`-D DETECT_NO_TAIL` note states plainly that the guard is not disabled by any flag). The two cells the deferred
sign-off names -- `P40_P55` (sense pin P44 = the LEFT board's `pin_pwm_w_l`) and `NO_USE_P24_P39` (P28 = the
RIGHT board's) -- are therefore skipped as `GATE_OVERLAP` whatever is physically plugged in. **Unplugging the
motors is the safety precondition for relaxing the guard; the relaxation itself was never built.**

**What it costs.** `«#3500»`'s behaviour that an overlapping pin group reports *not detected* rather than Rev B
has no bench evidence, so the 6.0.0 release line for it stays DERIVED (`«#3515»` already treats it that way).
Nothing else waits on it.

**Fix direction, for its own scoping -- not a run-sheet rider.** A compile-time flag on the passive build
(`detect` / `detect-lib`, no driver cog at all) that suppresses `GATE_OVERLAP` only, leaving `COG_OVERLAP`
refused, plus a tier that states the motors-unplugged precondition in the log the way the other preconditions
are stated. It deliberately drives a board's gate input, so it is a change to a hardware safety guard and wants
a review before its first run, not a slot before a bench session.

### PL-96 -- an over-length record token prints as `?` with no signal, so a label can be lost silently

> **Status (2026-10-02): ✅ CERTIFIED by the 6.1.0 visit:** `dual-tokneg` FAILs on its planted token (`BM-TOKCHK
> ...first_bad,tokScope,...,ok,FALSE`) and every other dual log PASSes R21-DUAL-TOKTAB (45-70 tables). **Earlier (2026-10-01): BUILT** («#3651», `test_bench_dual` SRC_REV 71). Every count is
> derived from its enum; all 80 token tables end in a sentinel; `tokenTablesSelfTest()` walks every table the build
> holds, plus the sign-off cell and criterion strings, and prints `BM-TOKCHK` and cell `R21-DUAL-TOKTAB` in every dual
> build. Its negative is the one-off tier `dual-tokneg` (one table a token short, one token too long), which must print
> FAIL. Found while building it: `sFenWords`' fourth word was 37 bytes against `tokenAt()`'s 32-byte scan, so fence
> words 4 and up printed wrong text; the scan bound is now 40. Footprints unchanged within 4 bytes (dual-a 6,649,
> floor-auto 6,858, limit 12,404). The bench owes: the first dual log's cell PASS, and `dual-tokneg`'s FAIL.
>
> **Earlier status (2026-10-01):** IN 6.1.0, together with PL-97, as one start-up self-check (STEPHEN 2026-10-01: harness work
> for this plan's runs). **A fourth instance since this entry:** `sSfCritSpPeak` was `START_I_OVER_STEADY_X100`, 24
> bytes against `TOKMAX_CRIT` 18, and printed `?` until SRC_REV 70 shortened it (`test_bench_dual.spin2:3338`).
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record vocabulary)

**Found 2026-09-21 while judging Visit 7b.** Open. **One instance is fixed; the class is not.**

**MEASURED (`DOCs/analyses/bench/2026-09-21/debug_260921-124024.log`):** the visit's load-bearing cell
emitted `SIGNOFF,...,cell,R18-DUAL-OFFSETS-A,...,crit,?,...` -- the criterion name replaced by a single
question mark. **Cause proven by counting, not inferred:** `sSfCritOffsets` was
`"APPLIED_EQ_COMPILED"`, **19 bytes against `TOKMAX_CRIT = 18`** (`src/test_bench_dual.spin2:740`), and
`tokenField()` prints `@sBadTok` for any token longer than its declared max, by design and without
complaint (`src/isp_bench_log.spin2:121-131`). One byte over.

**FIXED at R18.2d («#3593»):** the token is now `"OFFSETS_AS_BUILT"` (16). An audit of every
`sSfCrit*` token found this was the **only** one over the limit; the next longest sit at exactly 18, so
`TOKMAX_CRIT` is correctly sized and this string was the outlier.

⚠ **WHAT IS NOT FIXED, and why this entry exists.** Shortening the string dodges today's instance of a
defect class that can recur on any future token edit with **no compile-time and no run-time signal**.
The verdict and the count survived here, so the A/B was not compromised -- but the cell that certifies
that the driver runs the offsets it was built with could not name its own criterion, and nothing
reported that. **The deeper fix belongs in the mechanism:** either a compile-time length check so an
over-length token fails the build loudly, or a start-up self-check over the token tables that emits a
verdict like every other mechanism does. Neither is in R18.2d's scope.

**Cost if left:** a silent `?` is indistinguishable from a criterion nobody named, and doctrine D2 is
explicit that a check reporting something ABSENT routes to opposite owners -- the run failed to emit
it, or the contract describes something never emitted. This defect makes the second case look like the
first.

---

### PL-97 -- a token table shorter than its enum walks off the end and prints adjacent DAT as text

> **Status (2026-10-01): BUILT with PL-96** («#3651»; see PL-96's status). **Earlier:** IN 6.1.0, together with PL-96 (one mechanism).
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record vocabulary)

**Found 2026-09-21 while adding the ALIGN segment.** Instance fixed; **the class is the same one as
PL-96 and is not fixed.**

`tokenAt()` (`src/test_bench_dual.spin2:8699-8711`) bounds the index against **`tokenCount`, which the
caller supplies** -- not against the table's actual length. Callers pass the *enum* count. So a token
table with fewer entries than its enum does not return `"?"`; it walks past its own last entry into
whatever `DAT` follows and returns that as the field's text.

**MEASURED, first instance:** `tokFinds` carried **15** entries against `SEG_COUNT` **16**.
`SEG_LOWSPD` is index 15, so `BM-PLAN`'s `finds` field for LOWSPD already indexed past the end.

**MEASURED, second instance — and it is the one that proves the class.** `tokPart` carried **9**
entries against `PART_COUNT` **10** from the moment `PART_ALIGN` joined the part enum. `PART_ID` is the
index, so an ALIGN build printed adjacent `DAT` in the `part` field of **`BM-BANNER`, `BM-PLAN`,
`BM-EXIT`, every `SIGNOFF` and the watchdog record** — five record types, the run's own identity among
them. ⚠ **It was introduced by the very commit that fixed the first instance** (`5a8969b`): the same
enum addition broke two tables, one was found and one was not, and nothing in between could tell.
That is the argument for the mechanism below rather than for another careful edit — a class this easy
to re-open while fixing it cannot be closed by attention.

⚠ **It never showed, because a second defect hid it:** `BM-PLAN` never emitted a LOWSPD row at all --
`PART_A` hard-codes four `emitPlan()` calls (the earlier study's F1, still open). **Two defects, each
concealing the other.** Fixing F1 alone would have started printing garbage into a user-visible field
with nothing reporting it.

**FIXED at R18.2e («#3590»):** `tokFinds` extended to `SEG_COUNT`, and the `estS`/`estKb` `lookupz`
tables extended with it -- those were also one entry short and would have returned 0 for a new segment
rather than failing. `tokPart` extended to `PART_COUNT` in the follow-on commit that built the ALIGN
measurement core.

**MEASURED, third instance (2026-09-22, found by «#3604»).** `SEG_LEAD` («#3583») and `SEG_TAKE` («#3584»)
joined the segment enum with no `tokFinds` row and no `estS`/`estKb` entry. The Visit 8b `dual-lead` log shows
it: `BM-PLAN,...,seg,LEAD,...,finds,?,est_s,0,est_kb,0` (`debug_260922-164207.log`). This time the adjacent DAT
happened to begin with `"?"`, so the field read as unknown rather than as a wrong word. **FIXED at «#3604»:** both
rows filled, the LIMITS part's three rows added after them, and part A now prints its LOWSPD and TAKE plan rows
(F1's two missing rows). The class below is still open, and this is its third instance in three segment additions.

⛔ **WHAT IS NOT FIXED.** Nothing prevents the next table from being short. **A table's length and its
enum's count are asserted nowhere**, in either direction, and the failure is silent in both: short
table prints adjacent memory, and PL-96's over-length token prints `?`. Both are the same underlying
gap -- **the record vocabulary has no self-check.** The fix is one mechanism, not two: a start-up pass
that walks every token table against its enum count and emits a verdict, which would have caught this,
PL-96, and the short `lookupz` tables in one run.

**Cost if left:** a `finds`, `crit` or `seg` field can misdescribe itself with no signal, and doctrine
17 requires that a field never print a value under a label that misdescribes it.

---

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

### PL-132 -- the blocked-wheel protective stop shorts the phases even when the user chose coast

> **6.1.0 status (2026-10-03): ✅ CERTIFIED** by the second visit: after a protective stop the COAST trial's phases read
> 166 / 160 mV (coasting, BLKCOAST PASS) and the BRAKE trial's 16 / 13 mV (shorted, BLKSHORT PASS)
> (`debug_261002-143413.log`).
>
> **Earlier 6.1.0 status (2026-10-02, the visit): STILL UNMEASURED.** The COAST trial never latched under DRIVER_REV 47 (PL-179),
> so BLKCOAST read NOMEAS; the BRAKE trial faulted at contact (PL-180), so BLKSHORT did too. The COAST half waits for
> PL-179's fix and its visit.
>
> **Earlier 6.1.0 status (2026-10-02):** the no-latch bound replaced by one timed from the driver's own count (735bc9d);
> D-5 was expected to make the COAST trial latch. It did not.
>
> **6.0 status (2026-10-01):** AWAITS CERT — the short control PASSed on both visits (BLKSHORT 14 / 15 / 13 mV); the COAST
> cell is NOMEAS twice: a lag fault pre-empted the latch (first visit), then the harness's no-latch bound gave up about
> 240 ms before the driver would have latched against a rocking obstacle (the rerun). Rerun once PL-168 corrects the bound.

**Found 2026-09-23** as fault study F-5, and **filed 2026-09-25** («#3609» phase 3). `frontProtectiveStop()` secures
the motor with `frontEStop(TRUE)`. The PASM e-stop takes `.shortBridge` "whatever the stop mode"
(`isp_bldc_motor.spin2`, the `.eStop` branch). So a blocked wheel under SM_FLOAT is shorted, and the user's
`holdAtStop(FALSE)` is not honoured on this path (P3: behaviour the API lets the user select is theirs). The wheel is
stationary by construction, so the short brakes nothing. The cost is on a slope: a short at rest creeps, and the user
who chose coast gets a state they did not choose. The e-stop itself stays a hard short by Stephen's ruling. Only its
reuse here is the defect.

**Disposition:** ⛔ fix in the driver, «#3609». The protective stop gets its own immediate stop that takes the stop mode's
at-rest state: SM_FLOAT coasts, SM_BRAKE holds, and the hold's own hand-off to the short still applies. It still latches
and refuses drives until `clearProtectiveStop()`. **Unmeasurable wheels-up** (PL-106: a lifted wheel cannot be
blocked), so it is certified by construction and by the floor run (the OBSTACLE runs, «#3628»). Building it gates no load on the current
bench pass.

**FIXED (DRIVER_REV 20, 2026-09-25), not bench-certified:** `e_stop` carries its kind: ES_OFF, ES_HARD (emergency
stop, walk guard, `frontSecure()`) or ES_PROTECT (`frontProtectiveStop()`), written in one store by `frontLatchStop()`.
The PASM latch calls `estopBridge` (LUT), which shorts for ES_HARD and for ES_PROTECT under SM_BRAKE, and coasts for
ES_PROTECT under SM_FLOAT. Every reader tests non-zero, so the refusal semantics are unchanged. DRIVE-OBJECTS.md's
*Protection and limits* says which state the stop takes. ⚠ It is a user-visible behaviour change, so it needs a release
note line («#3516»).

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

### PL-160 -- a user cannot shape the ramp for their robot: deceleration is fixed, settings are lost on start(), and every ramp starts and ends with a torque step

> **6.1.0 status (2026-10-02, the visit): the quarter-speed start under load CERTIFIED.** SPINSTRT PASS on both wheels,
> duty drop 0 at the arrival (`debug_261002-103332.log` `BM-SPINSTART` seq 420-421, 762-763), with no arrival spike in the
> trace. SPINPEAK's FAIL is its wheels-up limit read against the platform's spin-up current, not the start (PL-183).
>
> **Earlier 6.1.0 status (2026-10-02):** two-turn spins (735bc9d) for SPINSTRT / SPINPEAK.
>
> **6.0 status (2026-09-30):** RELEASE — wheels-up half certified 2026-09-28; the feel under load ✅ CERTIFIED by
> Stephen's first FlySky drive (*"very responsive... no clicking, no unusual motor movement or sounds. Its ramps are
> pretty good."*), which the telemetry agrees with; the second drive (2026-09-30 rerun) confirmed both knobs' rates reach
> the ramps exactly. SPINSTRT / SPINPEAK at the quarter need two-turn spins (PL-168, R20).

**Found 2026-09-26.** `setAcceleration(rate)` sets only speeding up. Every slow-down and stop runs at a fixed
`ramp_down` of about 1,470 mm/s², which only the raw `setRampingValues()` can change. `start()` discards the setting
(`init()`). The ramp steps acceleration from 0 to full and back in one drive pass at both ends. The desk study
(kick spec, 2026-09-26) and its model: the speed-change *current* kick is a separate one-pass defect (the field is not
advanced on the arrival pass, fixed under PL-78/87). The acceleration steps are what a user *feels*, and the jerk
limit is kept for that.

**STEPHEN 2026-09-26 (Q1):** *"yes sep calls"*. So `setDeceleration(rate)` in mm/s² is added beside `setAcceleration(rate)`,
which stays as it is.

**Disposition: ⛔ build**, from the kick spec's section B, as amended by the model:
- one jerk-limited trajectory generator per motor, continuous through every transition and reversal, with
  τ ≥ 250 ms if starts from the lowest speeds are in scope;
- acceleration and deceleration set independently, kept across `start()`, with getters and the steering and serial
  mirrors (`setdecel`);
- the stop prediction and `stopAfter*()` limits kept exact.

Open owner questions, asked one at a time: Q2 the built-in rates; Q3 `setRampingValues()`; Q4 reporting a held ramp;
Q5 the inertia term.

**2026-09-27, Visit 10 pass 7:** the API half — `setDeceleration()`, persistence across `start()`, and the getters —
is CERTIFIED by t0-api (10/10 families, 0 bad). The entry stays OPEN for the jerk-limited trajectory generator (the
feel). Its built-in rates (owner Q2) are unanswered, and do not block anything until that generator is built.

**2026-09-27, built (DRIVER_REV 38), the generator.** Not yet run on hardware.
- **One generator per motor** (`jerkStep`, LUT-resident, called once per drive pass while not at rest). State: v =
  `drv_incr`, a = its change per pass. Each pass, with e = target - v, s = sign(e), E = |e|, alpha = s a: the side toward
  s takes the speed-up pair when v is 0 or has s's sign, else the slow-down pair (J, A); x*(E) is the largest alpha from
  which a pure J ramp-out lands exactly on the target; U is the jerk-limited step toward A; alpha' = min(U, max(alpha -
  J, x*)). So every ramp eases its acceleration in and out, and lands exactly on its target with a = 0 (arrival advances
  the field: DRIVER_REV 34's kick fix kept). A reversal passes through zero in one continuous ramp; only a start from
  DCS_STOPPED seeds the field from the halls; SLOW_TO_CHG is only reported.
- **Departures from the survey spec, each for a stated reason.** (1) The survey's "|e| > dvStop + |a|, else toward 0"
  test is made exact by the x* bound, so the ramp-out lands on the target instead of creeping back to it in bumps; that
  is what lets the stop prediction be closed form. (2) The pair is chosen by the side a is on, not by the target's
  direction alone, and an acceleration on the far side (or above a lowered limit) unwinds at the larger jerk: with the
  target's pair, a stop read mid-speed-up unwound the up-ramp's acceleration at the slow-down jerk, for up to ~10 s at
  the setter limits (DERIVED, desk model). (3) At the target (e = 0) any |a| up to max(jerk_up, jerk_dn) ends at 0: with
  the survey's snap only (|a| <= J of the side), an arrival's last step met the other side's smaller jerk on the next
  pass and overshot (desk model); zeroing a on the arrival pass itself let a command on the next pass step it by 2J.
  (4) The LAG_SOFT gate eases a toward 0 by J, as specified. (5) x* costs two CORDIC divisions and a square root per
  pass (~230 clocks); the survey's own dvStop divides by J too. J itself is computed on the Spin2 side, as specified. No held-ramp count is kept: without an ABI long the Spin2 side cannot read a cog register, and a PASM
  debug() would print every pass.
- **ABI:** params run unchanged at 27 (`ramp_down`/`ramp_max`/`ramp_min`/`ramp_inc` reused in place as
  `accel_dn`/`accel_up`/`jerk_up`/`jerk_dn`); status run 21 -> 22 (`drv_accel_now` appended, `fault` after it;
  `isAbiLayoutValid()` checks it). `testGetAccelNow()` (motor) and `testGetAccelNow() : nLeftAccel, nRightAccel`
  (steering). The path-scale and hold-decay floor is the constant DRV_INCR_FLOOR (1_500), no longer `ramp_min`.
- **Built-in rates (owner Q2 still open; named constants a ruling only retunes):** ACCEL_BUILTIN_MM_S2 1_000,
  DECEL_BUILTIN_MM_S2 1_470, RAMP_TAU_MS 250. Each jerk = its limit / 478.3 passes, rounded, at least 1, on the Spin2
  side. `getAcceleration()` now returns 1_000 until set. `setRampingValues()`: maxRamp and decrRamp are the two limits,
  minRamp and incRamp have no effect (owner Q3 open); `getRampingValues()` returns the four driver parameters.
- **Stop prediction:** `frontStopTicks()` / `frontStopMs()` read one closed form of the rule (`stopPlan()`: take pass,
  unwind, rise, plateau, ramp-out, and the stop-at-zero corner). DERIVED against a pass-by-pass model of the rule over
  ~7_000 random stops: passes exact, travel within 0.02 tick. The PASM routine's own source lines, executed by an
  instruction-level interpreter, match that model on 4.5 million passes (desk checks, not bench).
- **Rev A fold-back (same revision):** the fold compares the whole-mV reading ABOVE the floored threshold (was at or
  above it). At the duty floor on Rev A the threshold is 0.375 x amps mV, which floored to 0 under ~2.7 A and folded
  every driven frame.
- **Negatives** (what shows it did not work): a ramp's drv_accel_now stepping by more than max(jerk_up, jerk_dn) in a
  pass other than a stop read just before a reversal's zero crossing; a drive that does not settle on its target with
  drv_accel_now 0 from the pass after its arrival, or overshoots it; a stop that crosses zero; the field stopping
  (DCS_STOPPED, a hall re-seed) at a reversal's crossing; a distance, rotation or time limit that no longer comes to
  rest inside the tolerance its existing cell judges; the speed-change current kick back above pass 7's 16/13 mV. Rev A: with `testSetCurrentLimits(2, 2)` a driven, unloaded
  wheel still counting foldback_frames every frame.
- **Costs:** cog RAM 403/496 (was 487), LUT 402/512 (was 293), read from the compiler listing. A stop now takes
  RAMP_TAU_MS longer and travels speed x 0.125 s further than DRIVER_REV 37's (DERIVED; ~100 ticks from 196 ticks/s,
  was 75 measured). `stopPlan()` adds Spin2 work to every front pass with a limit armed (unmeasured: PL-161's
  R16-DUAL-FRONTST re-certifies it).

**2026-09-27, owner Q3 RULED (STEPHEN: *"Yes, remove the set ramping values and get ramping values calls. We don't need
them."*).** DRIVER_REV 46: `setRampingValues()` / `getRampingValues()` are gone; `setAcceleration()` /
`setDeceleration()` (mm/s²) are the only ramp settings, identical on the motor and steering objects and over serial.
The four driver parameters stay readable to a harness as the TESTING USE `testGetRampLimits()`. The steering setters
now set the right wheel only once the left accepted (a rejected call changes neither wheel, by construction). README
lists the removal as BREAKING. Q2 (the built-in rates): Stephen asked whether the defaults make sense; the answer given
was keep them and confirm on the floor (the floor sheet's PL-160 feel line). Q4 RULED 2026-09-27 (STEPHEN: *"no
public api change"*): nothing is added for 6.0; the held-ramp report moves to PL-102, after v6.0.0. **Q5 RULED
2026-09-28 (STEPHEN: "Q5: A"): no inertia term in 6.0**; it is filed after v6.0.0 as PL-166. All of PL-160's owner
questions are now answered; what remains is the wheels-up re-run (t0 SRC_REV 28) and the feel on the floor.

**2026-09-28, Block A: the wheels-up half is CERTIFIED** (`analyses/bench/2026-09-28/blockA/BLOCK-A-EVALUATION.md`,
`debug_260928-113930.log`, t0 SRC_REV 28): R22-T0-RAMP-SHAPE, -REVERSE and -UNWIND PASS, every stop's largest step of
acceleration equal to the jerk (`jerk_pk,104`), the reversal `crossed,TRUE,stop_seen,FALSE`, STOPPLAN-C/-M PASS again.
PL-160 stays open only for the feel under load (the floor run).

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

### PL-167 -- under a heavy load the shipped commutation timing gives up speed with torque to spare

> **Status (2026-10-02, the 6.1.0 visit): SPEED HELD, CERTIFIED; NOT SHIPPABLE until PL-179.** (`DOCs/analyses/bench/2026-10-02/VISIT-6.1.0-EVALUATION.md`.)
> SPINRATE PASS (every leg 100-107 %, against 57-94 %), RAMPARR PASS (1,807 / 1,790 and 323 / 320 ms), no path limiting in
> the FlySky drive, SPINCTL judged 4.64 / 4.74, wheels-up SRVHUNT / SRVKEEP PASS; a hand's load is held. But the blocked
> stop no longer latches (PL-179), two lag faults and a slow-down kick are new (PL-180), and the boost fires in calm running
> (PL-181). SPINHOLD / LIMGIVE's single LEFT holds are PL-182; BLKLIMIT / BLKSTOP NOMEAS.
>
> **Earlier status (2026-10-02): BUILT, DRIVER_REV 47** (9ede499): D-1..D-3 plus PL-167 D-5, as Stephen ruled 2026-10-02 (*"ok
> let's go with A"*).
>
> **Earlier status (2026-10-01, R21):** a **v6.0.0 Known Issue**; the fix is **6.1.0** work. Stephen: *"ok yes, A lets get
> 6.0.0 to release first then we'll follow with this new effort"*. The CHANGELOG, the manual's §6.5 / §9, the REWORK page,
> and every "holds the fastest speed it can sustain" claim in the user docs now state what v6.0.0 does.
>
> *Was (2026-10-01):* RELEASE — Stephen, on hearing it: *"is there something we can do to address this to make
> it more like a professional driver? i'm assuming one wouldn't do this."* Desk work first (Plan A §11).
>
> **Design (2026-10-01):** `DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md`. The cause is proven for the quarter-speed
> contrast (schedule against fixed) and unproven for the slow/medium depth (§3.6). D-1 a calmer trim gain, D-2 a fast
> slope past `LAG_SOFT`, D-3 the field gives way only at a limiter, and D-4 `LAG_HOLD` 86 (decided (a), conditional:
> §7 Q1). Phase 2 approved with the slow/medium depth unproven (Stephen 2026-10-01, *"ok A"*; §7 Q3): the desk refit
> first, stopping to ask if it finds a second mechanism.

**Found 2026-09-30**, the hands-off floor rerun (`DOCs/analyses/bench/2026-09-30/floor2/FLOOR-RERUN-EVALUATION.md` §2.1, log
`debug_260930-181811.log`).
- **MEASURED:** spinning a 7.7 kg platform in place, every leg on the shipped lead table (17/336 at slow and medium,
  5-6/346-347 at the quarter) ran at 57-94 % of its commanded rate (`fol_pct`), with the lag at the limiter's hold
  (`err_pk` 84-113), the duty swinging 900-1,650 (SPINHUNT FAIL 4 of 4, both wheels), the mean error off its point
  (SPINERR FAIL) and the path limiter trimming (`path_pm` 629-861). The legacy pair (43/317, medium) and the fixed pair
  (14/338, quarter) held 100 % with the path limiter idle (`path_pm,1_000`) and `err_pk` 72-94, at about twice the current.
- **MEASURED:** the duty used on those schedule legs was 2,000-3,700 of 27,648, and the current 0.05-0.14 A: the drive
  gave up speed far from its current limit.
- **The same signature** appears in the FlySky drive's 200 mm/s² speed-up (about half the set rate realised, the lag
  limiter pulling the field back 15 times) and in the two ramp legs that arrived late.
- **What a professional drive does instead (DERIVED):** holds speed by raising torque up to the current limit and gives
  up speed only there; advances the field with load as well as speed.
- **Not established:** the cause -- the duty servo's authority and stability under load with this timing, the order in
  which the lag limiter and the servo act, the lead's load dependence, or several together.
- **Consequences:** SPINCTL's PASS (schedule current 1.89x / 2.40x below legacy) compares unequal delivered speeds;
  SPINSYM RIGHT 1.36 likely shares the cause.

### PL-168 -- floor-test premises the runs proved wrong

> **Status (2026-10-02, the 6.1.0 visit): four of five premises CERTIFIED; the coast bound UNEXERCISED.** Two-turn quarter
> spins measured SPINSTRT / SPINPEAK / SPINLEAD for the first time; SPINCTL was judged at equal speed; the obstacle trials
> printed their own RESULTs; the labels read true. The coast no-latch bound never ran (the trial timed out, PL-179). Three
> new wrong premises are PL-182 (LIMGIVE), PL-183 (SPINPEAK), PL-185 (the grab).
>
> **Earlier status (2026-10-02): CORRECTED in the tree** (735bc9d, `test_bench_dual` SRC_REV 74-76).
>
> **Earlier status (2026-10-01):** 6.1.0 work (R21); no test harness ships in a release archive set. To be corrected before any rerun (Stephen: *"if we deem a test needing to be run again and it's
> build on wrong premise we should correct that before running again, right?"*).

From `FLOOR-RERUN-EVALUATION.md` §4, §2.1, §7:
- **The coast trial's no-latch bound** (`BLK_STAND_HI_MS`, from `BLK_LAG_MS`) assumes the lag is at the hold at the
  wheel's last tick. On a rocking obstacle it was at -28 and took about 430 ms to reach the latch's 80, so the harness
  gave up about 240 ms before the driver would have latched (`l_stand,1_183`, bound 1,180).
- **SPINCTL** assumes both timings deliver the same speed; under load they did not (PL-167).
- **The obstacle RESULT** reads the session-wide BLKSTOP count, so a passing BRAKE trial printed "a check failed".
- **SPINSTRT / SPINPEAK and the quarter's window** need about 0.5 s at speed; a one-turn quarter spin holds about 0.3 s,
  and one leg missed its window (SPINLEAD NOMEAS). The platform is untethered (R20): two-turn quarter spins.
- **Labels:** a missed window prints `STEADY_TIMEOUT` (the 4 s bound was not reached) and SPINLEAD prints
  `JUDGED_ACROSS_RUNS` inside a single session.

### PL-169 -- the FlySky demos re-send the acceleration setting on knob noise

> **Status (2026-10-03): ✅ CERTIFIED** — the second visit's FlySky drive swept both knobs end to end (raw 240-1,807;
> rates 200-3,000 and 1,000-3,000 mm/s²), still sending only on a move. **Earlier (2026-10-02):** the deadband CERTIFIED; the ends NOT SHOWN. 47 rate updates in the FlySky
> drive (`debug_261002-104014.log`), each more than 10 mm/s² from the one before, and none while a knob stood still. The
> knobs were not turned to both stops (VRA 499-1,735, VRB 270-1,514 raw; rates 662-2,867 and 1,048-2,626), so "both ends
> reached" waits for the next FlySky drive.
>
> **Earlier status (2026-10-01): FIXED IN THE TREE** («#3649»). Both demos send a knob's rate only when it moves more than
> `RC_RATE_DEADBAND_MM_S2` (10) from the rate last sent, or reaches an end of its range (`bRateMoved()`). DERIVED (desk
> simulation of the demos' integer `map()` over the default 240..1807 calibration): a ±2-count still knob moves the rate
> at most 8 (VRA) / 6 (VRB) mm/s², so it sends nothing; one-count sweeps reach 200 / 3,000 and 1,000 / 3,000.

The VRA knob's ±2-count noise (raw 1,504 / 1,506) changes the mapped rate by 4 mm/s², and the demo calls
`setAcceleration()` on every change: about every 250 ms through the last minute of the 2026-09-30 rerun (2,458 / 2,462).
A deadband of a few counts on both knobs would stop it.

### PL-170 -- on Rev A the fold-back's noise margin is sized for ±3 mV, and the board reads 7

> **Status (2026-10-01):** ANCILLARY — reaches only TEST USE current limits; not in 6.1.0's tests. Opened from PL-163's
> residual when PL-163 itself was archived as certified ([archive](plans/archive/PUNCH-LIST-ARCHIVE-2026-10-01b.md)).

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

### PL-172 -- the style gate's self-test fails: check T128 has no fixture

> **Status (2026-10-01): DONE** («#3646»). `tools/fixtures/style/T128.spin2` fires T128 and only T128; MEASURED:
> `tools/check_style.sh --self-test` exits 0.

**MEASURED 2026-10-01:** `tools/check_style.sh --self-test` exits 1 and ends `SELF-TEST FAIL: no fixture exercises:
['T128']`. T128 (no parenthesis in display text, PL-128) joined `ALL_CHECK_IDS` (`tools/check_style.sh:1151`) in
`13495a7` with no `tools/fixtures/style/T128.spin2`, so since then the self-test cannot prove that every check fires.
The gate itself (`tools/check_style.sh` without `--self-test`) is unaffected. **Fix:** a `T128.spin2` fixture on which
T128 fires, and only T128.

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

### PL-179 -- under D-5 a blocked platform does not stop itself: the protective stop never latched

> **Status (2026-10-03): the DRIVER fix CERTIFIED by the second visit** — both obstacle trials latched, stands 1,022 / 1,002
> ms (`debug_261002-143413.log` seq 383, 757). BLKSTOP / BLKLIMIT still FAIL on the harness mirror (PL-188), and C4's gaps
> are PL-189.
>
> **Earlier status (2026-10-02): BUILT, DRIVER_REV 48; awaits the second visit** («#3662»). Cause SETTLED at the desk
> (`DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md` §4.10.3): at a low limit the fold-back acts in single frames (the stall's
> own counters: 1,677 / 914 fold frames in ~9.5 s, so at most 18 % / 10 % of passes), and the count needed 1,000 in a
> row. STEPHEN 2026-10-02 (*"yes, a"*) ruled all three parts: **F-a** the count's limiter half is sticky from the first
> limiter action after a tick until the next tick; **C4** the limit hold stays armed until the rotor ticks forward;
> **S-1** (PL-180). MODELLED: a solid object latches 1,010-1,116 ms after contact (4 of 4; 15 of 16 in the full grid),
> against never. DERIVED: with C4 and S-1 neutralised the image is equivalent to DRIVER_REV 47 (`tools/pasm_equiv`, 112
> of 112), so nothing else changed. **Earlier:** ⛔ FIX, found by the 6.1.0 visit (evaluation §3.2, F-1).

**MEASURED 2026-10-02** (`debug_261002-103634.log`, DRIVER_REV 47, 2 A obstacle limit): in the COAST obstacle trial both
wheels stood still against the object for about 9.2 s (trace `k` 675-2,975, `pos` frozen, state SPIN_UP), the lag at 64-77
on both, until the harness's own timeout stopped them (`BM-BLOCK` seq 327, `stop_by,TIMEOUT`). Four `EV_FOLDBACK` at contact,
none after. On DRIVER_REV 46 the same trial stood 1,183 / 1,092 ms (`2026-09-30/floor2/debug_260930-182135.log` seq 362).
- **The rule:** `bFrontProtect()` (`isp_bldc_motor.spin2:2896-2902`) counts a pass with no tick when `|err|` ≥ `LAG_SOFT`
  (80) or a limiter count advanced (SPIN_UP / AT_SPEED), and latches at 1,000 in a row. D-5 sets the field back to
  `LAG_LIM` (64) on a limiter pass, so `|err|` never reached 80; the limiter half never ran 1,000 in a row.
- **Not established:** the per-pass limiter counts (not recorded). *Consistent with* a limiter acting on many passes but
  not every one, against design 4.9.5's premise that one acts on every pass. The model (`block`, 2 A, D-5) separates it.
- **Not to do:** lower `LAG_LIM` or `BLOCKED_PASSES` to make it latch; the stop's timing is a safety bound.

### PL-180 -- lag faults on hard transients, and a slow-down current kick, new at DRIVER_REV 47

> **Status (2026-10-03, second visit):** the slow-down kick CERTIFIED gone (TRKICK-A 24 / 30 mV); no fault at obstacle
> contact (BLKFLT PASS); no reversal fault in the FlySky drive, on fewer reversals (9 samples at ≥ 150 tps against 27): not
> settled. A hand-slowed wheel faulted under the grab (PL-189).
>
> **Earlier status (2026-10-02): two of three BUILT, DRIVER_REV 48; the reversal fault UNEXPLAINED** («#3662»; design §4.10.4-5).
> - **The contact fault: consistent with, modelled.** Between fold-back frames the field walked back from 64 through
>   |err| 82..88, where one tick against it faults; C4 keeps it at 64 while blocked. Modelled lag faults against a
>   yielding object 7 → 0 of 16 (DRIVER_REV 46: 1).
> - **The slow-down kick: consistent with, modelled.** The PL-55 ceiling held duty down until the lag reached
>   `LAG_SOFT`, where D-2's boost started from the clamped duty. S-1 lifts it at `SERVO_SETPOINT`: modelled +115 → +52 mV.
> - **The FlySky reversal fault: NOT reproduced, cause not established.** No 6.1 change acts in a slow-down (D-5 acts
>   only in SPIN_UP / AT_SPEED; the "D-2 against D-5" hypothesis is refuted). The next FlySky drive's hard reversals are
>   its reading; if it recurs it is root-caused from that drive's log.
> **Earlier:** root cause first; found by the 6.1.0 visit (evaluation §3.2, §3.4, §2.2; F-2, F-3).

**MEASURED 2026-10-02:**
- **The BRAKE obstacle trial faulted at contact:** RIGHT re-synced and faulted about 80 ms after the wheels stopped
  (`debug_261002-103634.log` seq 336, 338; `o_e` −125). DRIVER_REV 46's trial latched with no fault.
- **A FlySky hard reversal faulted:** from reverse at 175 tps to 98 forward and back to 0; RIGHT in SPIN_DN at `r_err`
  100, duty 8,827, re-synced at 31,942 ms and faulted at 32,134 ms (`debug_261002-104014.log`). The two DRIVER_REV 46
  drives had more reversals at speed (78 and 53 SLOW_TO_CHG samples at ≥ 150 tps, against 27) and no fault.
- **Wheels up, the 80 → 20 ×10⁶ step-down now kicks:** TRKICK-A 79 / 89 mV against 50, `tr_err_pk` 101, `tr_cap` 367
  (`debug_261002-100025.log` seq 16_718-17_291). The same step on the last ladder (2026-09-22, driver 4) read 0-19 mV and
  `tr_err_pk` 84-92. No speed-up kicked.
- **Not established:** a cause, or whether they share one. D-2 acts on the lag in `drv_incr`'s direction and D-5 on
  `err_`'s sign; a slow-down or reversal is where they could disagree. That is a hypothesis for the model.

### PL-181 -- under the platform's load the lag peaks reach LAG_SOFT in calm running (design risk R2)

> **Status (2026-10-02): WATCH, 6.1.0** (evaluation §3.1, F-4 and F-8). No speed is lost; the bound or D-2 is not touched
> until the model says whether the boost firing in running matters.

**MEASURED 2026-10-02** (`debug_261002-103332.log` `BM-SPINW` seq 30-58): on the slow and medium schedule legs `err_pk`
read 79-90 on 7 of 8 wheel-legs (SPINHUNT FAIL LEFT 4 / RIGHT 3 of 4, bound 76); the duty swing fell to 95-539 from
DRIVER_REV 46's 900-1,650. The model predicted `err_pk` 67-76 (design §5; R2 named A-3's 76 as the guard). SPINERR's
means read 43-46 at slow against the wheels-up 47-49 band, as on 2026-09-30 (unchanged by the fix). **Settles it:** the
model's slow / medium legs at the floor's inertia, with and without D-2.

### PL-182 -- LIMGIVE's sampler scores a hold during the spin-up as the field giving way

> **Status (2026-10-02): CORRECTED, `test_bench_dual` SRC_REV 78** («#3664»): limb (a) counts a give-way only after the
> wheel's driver has read AT_SPEED on the leg (`bLgArrived`; the held pass itself reads SPIN_UP, since `holdDecay` turns
> AT_SPEED into SPIN_UP, so the arrival is latched rather than the sample's state tested). It still FAILs a decay at speed
> with no limiter (D-3's limiter test removed, by reading). Spin leg 2 (slow) is now traced. **Earlier:** OPEN (F-5).

**MEASURED 2026-10-02:** SPINHOLD LEFT FAIL (1 leg) and LIMGIVE FAIL (2 of 31,278 samples) are one held pass each, on
LEFT, in slow spin leg 2 and slow ramp leg 1 (`BM-LIMW` seq 43, 1_126); neither leg lost speed (`fol_pct` 107; arrival
1,807 / 1,790 ms). `limSample()` (`test_bench_dual.spin2:18120`) calls a held sample a give-way when the field speed is
under 98 % of the **target**, which in SPIN_UP it always is; `holdDecay` lowers the field only when a limiter acted (D-3,
`isp_bldc_motor.spin2:7786-7790`). **Fix:** judge limb (a) only in AT_SPEED, or record the state at each give-way; and the
next visit traces one slow leg so a breakaway hold is told from a hold at speed.

### PL-183 -- SPINPEAK's 1.80 limit is a wheels-up number; the floor reads the platform's spin-up current

> **Status (2026-10-02): CORRECTED, `test_bench_dual` SRC_REV 78** («#3664»): SPINPEAK reads the ARRIVAL (two samples from
> the first AT_SPEED sample), and judges the peak's excess over the steady mean in mV against TRKICK's 50 (criterion
> `ARRIVE_I_OVER_MV`), not a ratio: at a 12-19 mV floor tail one count is 5-8 %, and the ratio read 1.47-1.96 on single
> noisy samples. On the 2026-10-02 legs the excess is 7-13 mV (PASS); its negative is TRKICK's on-file pre-fix arrival kicks
> of 64-183 mV. **Earlier:** OPEN (F-6).

**MEASURED 2026-10-02**, the first measurement (two-turn legs): 3.74 / 4.06 (leg 7) and 3.39 / 3.25 (leg 8) against
1.80 (`BM-SPINSTART` seq 420-421, 762-763). The trace (tid 7) shows a plateau of about 180 ms while SPIN_UP pushes the
platform (LEFT 59-68 at `k` 272-325), falling to 26 by the arrival at `k` 420 with no spike, so the shape is acceleration,
not a kick. SPINSTRT, which judges the arrival, PASSes. The 1.80 came from Visit 8 wheels up, about a fifth of the
inertia. **Fix:** derive the floor limit from the spin-up's own current (the jerk-limited ramp's acceleration on the
platform's yaw inertia), or judge the arrival's excess over the plateau instead.

### PL-184 -- at the quarter, the lead schedule draws more current than the fixed pair turning one way

> **Status (2026-10-02): OPEN, information, not this fix** (evaluation §3.1, F-7). The timing (PL-105's area), which
> D-1..D-5 do not touch.

**MEASURED 2026-10-02**, the first measurement of SPINLEAD: 1.17 / 1.30 against 1.05. Clockwise (leg 7 against 9) the
schedule draws less than the fixed pair (`amps` 990 against 1,043, 779 against 856); counter-clockwise (leg 8 against
10) more (1,259 against 878, 1,824 against 1,137). One pass each way, no repeat. **Settles it:** a repeat of the quarter
pairs, both directions, before any claim about the schedule's saving at the quarter on the floor.

### PL-186 -- in a fast pivot turn the coasting inner wheel is driven backward, so the platform spins about its centre

> **Status (2026-10-03): ✅ CERTIFIED in the log** by the second visit: `RC-PIVOT,samples,378,moving,0,max_tps,25,unheld,0,
> ...,verdict,PASS` (`debug_261002-143653.log`); Stephen's word on the feel is still to come. **Earlier: BUILT** («#3663»). STEPHEN 2026-10-02 chose option (a), *"yes your
> recommendation"*: the FlySky demos (and `test_bench_rc`, SRC_REV 7) select `holdAtStop(true)`, and `DRIVE-OBJECTS.md`'s
> `driveDirection()` row says a pivot needs hold. Cell `RC-PIVOT` judges it (a wheel at rest in a pivot moving faster than
> 50 tps FAILs; desk arithmetic on the logs: the 2026-10-02 drive fails 65 of 547, the 2026-09-30 drive passes 126 of
> 126). If hold does not stop the spin, option (b), a pivot-only hold in the drive, is the fallback.

**Stephen, 2026-10-02:** in a full left or right turn, *"it would run really well for a little bit, and then ... the
robot would start spinning around its physical center instead of around the stock wheel."* **MEASURED**
(`debug_261002-104014.log`): right turn 118.6-119.2 s and left turn 144.1-145.5 s, the inner wheel at power 0, STOPPED and
coasting (`l_hs` / `r_hs` HS_OFF on every sample), driven backward up to 225-250 tps once the outer wheel passed about 300
tps. **Cause (settled):** in a full turn the steering object gives the inner wheel plain power 0
(`isp_steering_2wheel.spin2:2425-2426`); it ramps to STOPPED and takes the program's stop selection, which in the FlySky
programs is coast (`holdAtStop(false)`, `demo_dual_motor_rc.spin2:114`). A free wheel is pushed back by the platform's
yaw. **Not settled:** whether DRIVER_REV 47 made it worse. The 2026-09-30 pivots (also coasting) were slower and only
crept. **Options for Stephen:** select hold in the demo; or a pivot-only hold for the inner wheel (an exception to "stop
behaviour is the user's selection", needing a driver change); each with its cost (current at the held wheel, the hold's
10 % ceiling and 2-tick slip). *Corrected 2026-10-02:* the first entry read the right wheel's fault flag as its hold
status ("HOLDING while rolling"); no hold was ever engaged.

### PL-187 -- above about 175 ×10⁶ the wheel runs rough: gravelly, vibrating, never settling

> **Status (2026-10-03): T-1 BUILT, DRIVER_REV 49; awaits the third visit** (its `dual-limits` traces the edge rung; TOPSPD
> should read above 175). **Earlier: cause established at the desk; T-1 RULED** (STEPHEN 2026-10-03 *"yes a"*; design §4.11, «#3668»):
> at the duty ceiling the limit hold (D-5) and D-3 act on a duty-cap pass, yanking the field back every sector. T-1: only
> the current fold-back triggers the limit hold. The second visit's `dual-limits` read 185 ×10⁶ the same way (its
> negative). **Earlier:** OPEN, evidence only (Stephen's report of the first visit's `dual-limits`).

**Stephen, 2026-10-02:** *"at the highest speeds, the motor sounds gravelly. It's having a hard time spinning, and it's
making terrible noises and a huge amount of vibration. That would suggest that we're out of sync with our positioning at
the high speeds."* **MEASURED** (`DOCs/analyses/bench/2026-10-02/debug_261002-101625.log`, DRIVER_REV 47, wheels up,
pack about 20.5 V):
- **Clean through 175 ×10⁶ on all four wheel/direction pairs:** rate on the speed law (e.g. `rate_x10` −4,685 against
  −4,676), lag at the servo's point (`err` −48, `err_pk` 71-73), no missed, illegal or skipped hall reads, PWM room 36
  counts (`BM-RUNG2` / `BM-RUNG3` / `BM-CLIP` seq 141-145).
- **At 185 ×10⁶, on all four:** the rung never settles in 4 s (`STEADY_TIMEOUT`); the PWM sits at its rails
  (`lvl_min` 3, `lvl_max` 2,995 of 3,068, room 3, over about 3,017 samples); and the hall reader skips sectors (`hw_skip`
  3 / 4 / 6 / 2, rids 14, 35, 56, 77), none of which happens below.
- **The over-command (245 ×10⁶ at 1 A):** the field falls to 13 % of the command and the wheel follows 5 % of it
  (`BM-FOLLOW kind,OVER` seq 159, 268, 377, 486).
- **No lag fault and no re-sync anywhere in the segment** (`BM-SEG LIMTOP ... faults,0`), so the field never got 125
  counts from the rotor: whatever the noise is, it is not a pole slip the fault test sees.

**Rival explanations, none separated by this log:** (a) the drive runs out of voltage: at the rails the sine is clipped
and the current, and with it the torque, ripples; (b) the lag rises past the torque peak once the duty can rise no
further (held at `LAG_HOLD`, 140° electrical, PL-105's case), so the wheel labours; (c) commutation timing (the lead)
goes wrong at that speed. The hall skips fit (a) or (b) as vibration and (c) as mis-timing. **What would separate
them:** a trace of the 185 rung and of the over-command (`err`, duty, current per 2 ms sample), and a desk read of what
the drive does once the duty is at its ceiling. **Why it matters to a user:** full power is 165 ×10⁶, which ran clean
here at 92 % duty on a 20.5 V pack; on a pack at the nominal 18.5 V the same speed needs about 102 % of that duty
(DERIVED: 25,460 × 20.5 / 18.5 ≈ 28,200 against the 27,648 ceiling), so a user at full power on a lower pack may reach
this region. Evidence for the "less torque in reserve near top speed" Known Issue (P5).

### PL-188 -- the obstacle mirror zeroes its count on the pass that sees the latch

> **Status (2026-10-03): FIXED in `test_bench_dual` SRC_REV 80**, awaits the third visit (the count is kept on the pass that
> first sees ESTOP). **Earlier:** ⛔ FIX, harness, 6.1.0 («#3668»); found by the second 6.1.0 visit
> (`DOCs/analyses/bench/2026-10-02b/VISIT-6.1.0B-EVALUATION.md` §3.2, G-1).

**MEASURED 2026-10-02** (`debug_261002-143413.log` `BM-BLOCK` seq 383, 757): both trials latched with stands of 1,022 and
1,002 ms, yet `l_count,0,r_count,0`, so BLKSTOP and BLKLIMIT FAIL. `blockWatch()` (SRC_REV 77) applies the driver's state
test to its count; on the pass that sees the latch the wheel already reads ESTOP, so the count is zeroed before the latch
is checked. **Fix:** check the latch before the count's bookkeeping, or keep the count on the latching pass.

### PL-189 -- the limit hold (C4) protects a wheel only from its first set-back to its next forward tick, and keeps the field fast

> **Status (2026-10-03): BUILT, DRIVER_REV 49; awaits the third visit.** STEPHEN 2026-10-03 *"yes A"* (design §4.12): U-1 the
> hold arms at every fold-back action; U-2 it stays armed until the rotor crosses a whole sector forward with no fold; U-5 its
> release caps the field's speed at 4 sectors over the passes since the fold. MODELLED: over-command end 34 A → 3 A; obstacle
> fault-band readings 4 → 0; steady grab faults 1 → 0 of 16. Certified by BLKWIN, the new LDFLT and OVRSTEP (SRC_REV 81).
> **Earlier:** ⛔ FIX, design then driver; found by the second 6.1.0 visit (§3.2-3.4, §2.2; G-2, G-3, G-4).

**MEASURED 2026-10-02, DRIVER_REV 48:**
- **Before it arms:** on both obstacle trials the RIGHT wheel's lag reached 85 / 83 once inside the window after its first
  limiter action (BLKWIN FAIL; `BM-BLKWIN` seq 386, 760). C4 arms at the first set-back, not the first limiter action.
- **On a wheel the limit slows but does not stop:** under the grab at 2 A, LEFT (slowed to 19 %) re-synced and lag-faulted
  (`debug_261002-143538.log` seq 16, 19). C4 disarms at every forward tick, so the exposure returns each sector.
- **At the end of a sustained limit:** the 1 A over-command now ends with the field at 47-52 % of command (13 % on
  DRIVER_REV 47); the full-power step after it drew ~9.6 A on LEFT (`BM-ABORT ... ABS_CURRENT,value,1_445`, `debug_261002-
  142002.log` seq 161) and the board fell silent at the same step on RIGHT (reset or link, not separated).
**Candidate corrections (to design):** arm at the first limiter action; stay armed while the wheel is limited; let D-3 give
the field's speed way on armed passes at a sustained limit.

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

### PL-185 -- a hand cannot slow the platform at the grab's 4 A limit, so the grab cells measure nothing

> **Status (2026-10-02): CORRECTED, `test_bench_dual` SRC_REV 78** («#3664»): `LOAD_LIMIT_A` 4 → 2 A (derived: 2 A drove
> the platform to the obstacle on both 2026-10-02 trials; the hand reached the 4 A fold-back briefly, so at 2 A it is past it
> for most of the hold). `tools/gen_dual_assets.py` matches; the `dual-floor` UI panel bitmap it renders still reads 4 A
> until regenerated where its font exists (that tier is not on the next sheet). **Earlier:** OPEN (F-9).

**MEASURED 2026-10-02**, two runs (`debug_261002-103814.log`, `-103915.log`): `RESULT: GRAB -- too light`, `l_pct` 99 /
`r_pct` 101 and 99 / 98. While held, LEFT's duty rose from about 2,000 to 3,300-4,700 and its sense current from 7-12 to
41-85, and the speed held; the fold-back engaged briefly (`EV_FOLDBACK` 53, 44; 25). That is the fix doing its job, and
design R8 predicted it. **Fix:** a limit a hand can reach (well under 4 A), or a known drag in place of the hand, so
LDPATH / LDHUNT / LDHOLD see path limiting.

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
