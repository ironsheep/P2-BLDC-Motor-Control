# Path to Visit 6 — study, 2026-09-19

**Internal analysis document** (doctrine overlay P8): it carries task ids, `PL-N` findings, commit hashes and
bench cell ids, and the MEASURED / DERIVED / STEPHEN provenance labels. It is never user-facing.

## 1. Scope (agreed with Stephen, 2026-09-19)

**The question.** What is the shortest complete path from today's tree to a Visit 6 that certifies, on hardware,
everything that has landed since Visit 5 and confirms the commutation offsets, so 6.0.0 can ship?

**Surface.**
1. The plan: `DOCs/plans/BENCH-READINESS-SPRINT-PLAN.md`, *Sprint Revision — 2026-09-17 (night)* (the R17 table),
   its exit criteria, and the rulings register `DOCs/analyses/FINDINGS-AUDIT-2026-09-17.md` §7.
2. The Visit 5 record, **from the primary logs** (`DOCs/analyses/bench/2026-09-17/debug_*.log`), with the run
   sheet and `VISIT-5-RESULTS.md` as the index into them, not as the evidence.
3. Everything landed since Visit 5: the commits `88294d5` («#3568») through `cc491bd` («#3543»). For each
   user-visible or driver change: what Visit 6 must show, and whether a cell that can FAIL exists for it today.
4. The bench harness as it stands: `tools/bench-run.sh` tiers, the bench tops and their `SRC_REV`s, and whether
   everything compiles in this environment.
5. The open work between here and the visit: «#3574», «#3575», «#3576», and the open punch-list entries they
   cite.

**Excluded, with reasons.**
- «#3506» (measurement front end), «#3532» (vibration study), «#3562» (N-motor shape): out of this release by
  STEPHEN 2026-09-17, *"no those three are not in"*.
- Motor characterisation beyond what confirming the offsets needs (overlay P10: characterisation is its own
  plan).
- The Doco motor (out of this release with «#3562»).
- «#3515» documentation and «#3516» ship, except where Visit 6 must settle something first.
- No clean-room exclusion applies to this project (overlay P8).

**Severity scale.** *blocks the visit* · *leaves a landed fix unproven* · *spends bench time for no decision* ·
*housekeeping*.

**Done means.** The five surfaces above read in full, the register below filled, and an ordered path to Visit 6
checked against the R17 plan rather than replacing it. Anything that would change scope is raised with Stephen,
not pursued.

## 2. Read order (ticked as read)

- [x] 1. Plan R17 section, exit criteria, FINDINGS-AUDIT §7
- [x] 2. Visit 5: run sheet → `VISIT-5-RESULTS.md` (index) → the Visit 5 logs (primary: every `SIGNOFF` line in
  `debug_260917-172913/-173018/-173141/-173713/-174324.log`, tallied by cell, motor and verdict)
- [x] 3. Commits since Visit 5 (`a4a5aa4..HEAD`, `src/` and `tools/`), each against the cells that would certify it
- [x] 4. Bench harness: `tools/bench-run.sh` tiers and flags; every tier compiled here with the runner's exact flags
  in a scratch copy of `src/`; both gates run here
- [x] 5. «#3573», «#3574», «#3575», «#3576» bodies; the status lines of every `PL-N` they cite

## 3. What the read established first

**MEASURED — Visit 5 is the last visit, and it was clean.** Every `SIGNOFF` line in the five Visit 5 logs reads
PASS or a designed NOMEAS: t0 24 PASS (run twice, 17:29 and 17:43, the second with the USB capture); dual-d 17 PASS
+ 2 NOMEAS; dual-b 13 PASS + 4 NOMEAS; dual-a 17 PASS. Every load ended `BM-END exit,COMPLETE … trap_code,0`.

**MEASURED — the driver moved after Visit 5, so Visit 5 no longer certifies today's binary.** `88294d5` (stop
states), `57e5785` (API promises), `6be991a` (board refusal, command timeout, atomic hall read, fault cause) and
`caa5e3c` all change `src/isp_bldc_motor.spin2`, including its PASM driver; `5c5086f` reorders it (2 080 lines,
no behaviour change claimed). By overlay P10's load rule every dual part and the clock loads have something new
underneath them.

**MEASURED — the tree is ready to be built for a visit.** In this container (pnut-ts 1.55.8):
`tools/build-check.sh` PASS 47/47, both release demos certified; `tools/check_style.sh` PASS, no findings across
42 files; every bench tier compiles with the runner's flags (t0 43 564 B, t0-hand 43 426 B, each dual part
76 862 B, scan 54 470 B, char 49 206 B, detect 19 606 B, spin 26 840 B). The dual parts' identical sizes are
not a dropped flag: dual-A and dual-B images differ in 14 bytes (the `PART_ID` constant).

**MEASURED — what each landed item has to certify it at Visit 6:**

| Landed | What must be shown | Cell today |
|---|---|---|
| R17.1 stop paths («#3568») | FLOAT coasts, BRAKE holds, fault takes the user's mode, e-stop per its doc | fault path: `R17-DUAL-FLTSTOP-C`. At-rest and e-stop: the attended stop-mode hand test — **not built** («#3576» body) |
| R17.2 API promises («#3569») | AB unequal-distance turn · G acceleration in mm/s² + range · K KM/MI commandable · AC positive direction turns right · AK voltage getter | **none — see F1** |
| R17.3 board refusal, timeout («#3570») | undetected board refused; unrefreshed drive stops | `R17-T0-NOBOARDSTART`; `R17-DUAL-CMDTMO-D`, `-WCMDTMO-D` |
| R17.4 hall read («#3571») | no torn reads; %000/%111 split, at three clocks | `R17-DUAL-HALL-K200/-K270/-K300` (clock loads) |
| R17.5 fault handling («#3572») | computed provocation faults under the 10 A abort; cause; retry; idle wheel still | `R14-DUAL-FLTAPI-B`, `R16-DUAL-FLTRETRY-B`, `R17-DUAL-FLTCAUSE-B`, `-OFFREST-B`, `-FLTSTOP-C`, `-IDLEMOVE-A/B/C` |
| R17.6 transition («#3573») | a speed change from speed does not kick more than a start from rest | `R17-DUAL-TRKICK-A` (instrument only; the driver half of «#3573» waits on this verdict) |
| «#3543» cog lifecycle | no run-together `CogN` prefix, no truncated record | read from the logs (no cell can see its own output corrupted); t0 is the stressor |

## 4. Findings register

| # | Severity | Finding | Evidence | Mark | Root cause | Trivially safe? |
|---|---|---|---|---|---|---|
| F1 | leaves a landed fix unproven | **No cell certifies any of R17.2's five items.** The resume records "run-time proof owed Visit 6" for «#3569», but nothing Visit 6 can load would produce it. AB: the only `driveForDistance()` in any bench drives both wheels the same distance. G: `testT0_5` prints read-backs with no verdict. K: KM/MI are only *read* (`getDistance`), never commanded. AC: `dual-floor` is the only direction test, and it asks an operator. AK: `getDriveVoltage()` is called by no bench. | `src/test_bench_dual.spin2:3545`; `src/test_bench_t0.spin2:618-641, 644-665`; `grep getDriveVoltage src/test_bench_*` → 0 | MEASURED | G1 | no — new cells |
| F2 | leaves a landed fix unproven | **AC can be certified unattended, wheels lifted.** Which wheel a `driveDirection()` slows is a property of the command, and the harness already computes it from hall-tick rates (`floorRates()` → `slower`). A lifted cell judging `slower == RIGHT` for a positive direction proves the sign fix without the floor. | `src/test_bench_dual.spin2:5318-5351` | DERIVED | G1 | no |
| F3 | blocks the visit | **The attended stop-mode hand test does not exist**, and «#3576» lists it as a step. It is R17.1's only proof for FLOAT-at-rest and for the e-stop's promised state. | «#3576» body ("BUILD FOR IT"); `holdAtStop` occurs 0 times in `src/test_bench_t0.spin2` | MEASURED | G2 | no |
| F4 | blocks the visit (the floor step) | **The rig-facts entry still forbids floor testing** and marks `dual-floor` NOMEAS by ruling. Stephen's later ruling, recorded in the plan, allows the tethered spin-in-place run. A reader of the conventions file would refuse the floor tier. | `.claude/skill-conventions.md:255-260` vs `DOCs/plans/BENCH-READINESS-SPRINT-PLAN.md:2141-2143` | MEASURED | G3 (aged state) | yes — rewrite the entry to carry both rulings |
| F5 | blocks the visit (the floor step) | **The platform's track width is recorded nowhere.** «#3575» needs it to convert wheel travel into platform turns and says to ask Stephen with the design. | search of `*.md`, `*.spin2` for track width / wheelbase / axle: 0 hits | MEASURED (absence) | — | — |
| F6 | latent | **`steerSetRamp()` / `steerRestoreRamp()` call `steering.setAcceleration()` with raw `ramp_inc` values.** Since «#3569» that call takes mm/s² and sets `ramp_min = ramp_max = step, ramp_inc = 0`, so restoring "22" would neither restore nor pass. Both methods are **never called**, so nothing runs wrong today; revived, they would fail RAMPREST and leave the steering wheels on a constant ramp. | `src/test_bench_dual.spin2:7877-7920`; `src/isp_bldc_motor.spin2:326-346`; no call site | MEASURED | G1 (the API change was not searched into the harness) | yes — delete the two dead methods |
| F7 | housekeeping | `testT0_5`'s comment still says `setAcceleration()` "writes {rate} straight into ramp_inc with no validation"; that is the pre-«#3569» behaviour. | `src/test_bench_t0.spin2:618-619` | MEASURED | G1 | folds into F1's G cell |
| F8 | housekeeping | `tools/bench-run.sh`'s clock-override path uses BSD-only `mktemp -t` and `sed -i ''`, the pattern `613d2bf` fixed in the two gates. Harmless on the bench Mac; the clock tiers would fail if a bench run ever started from Linux. | `tools/bench-run.sh` (clock override block, ~l.282-294) | MEASURED | — | yes |
| F9 | housekeeping | `VISIT-5-RESULTS.md` under-counts instances (15/16/16 against 19/17/17 `SIGNOFF` lines for dual-d/b/a) and does not mention the second clean t0 run at 17:43. No verdict changes. | the tallies in §3 | MEASURED | — | yes |
| F10 | spends bench time for no decision (if loaded) | **Loads with nothing new underneath:** `char` (its cells are sensing and steering start; dual covers the hall read), `detect` family (no detection change beyond the refusal t0 covers), `dual-brake` (no cell in it certifies an R17 item). | commit stats §3; tier roster `tools/bench-run.sh:165-233` | DERIVED | — | — |
| F11 | blocks the visit (a false FAIL) | **Found during «#3577»:** STOPLIM would FAIL a correct stop at Visit 6a. «#3570»'s per-wheel check compares the right wheel's RAW rest (negative for forward travel -- the steering object reverses that wheel) against a positive target: Visit 5's own r_rest -529 against 529 reads 1_058 off, bound 2. At Visit 5 the cell judged `ovLeftRest #> ovRightRest` and never saw it. **Fixed in «#3577»** (judged in the platform frame). | `git show a4a5aa4:src/test_bench_dual.spin2` (`leadRest`); `6be991a` diff; `debug_260917-173141.log` L7651 | MEASURED | a harness judgement changed without its frame | done |
| F12 | latent (could cost the t0 load) | **t0's DEBUG budget sits between the build that went silent and the one that emitted.** Compiler listing: SRC_REV 2 unquiet (silent twice) 210 records / 12_898 B data (81.3%); SRC_REV 3 quiet (emitted, Visit 5) 151 / 10_490 (66.1%); SRC_REV 7 (HEAD before «#3577») 161 / 11_252 (70.9%); SRC_REV 8 («#3577») 166 / 11_595 (73.1%). Both silent runs were inside the compiler's own limits, so the mechanism is not one it reports -- undetermined. Filed as PL-91. | `pnut-ts -l -d -D BENCH_CFG [-D BENCH_QUIET] test_bench_t0.spin2`, the `.lst` `DEBUG records`/`DEBUG data` lines | MEASURED (numbers) / undetermined (mechanism) | -- | no |

## 5. Root-cause groups

- **G1 — «#3569» changed five promises and the bench was not changed with it** (F1, F2, F6, F7). Every R17 task
  after it added its own cells in the same change (CMDTMO, HALL-K*, FLTCAUSE, TRKICK, NOBOARDSTART); «#3569»'s
  verify line asked only for gates, so its proof was deferred to a sheet that has nothing to load. One small
  batch closes it: G, K and AK are pure checks for `t0` (no motion); AB (unequal distances, each wheel at its own
  limit) and AC (the slower wheel under a positive direction) are two trials in an unattended dual part.
- **G2 — the attended half of Visit 6 is unbuilt** (F3). The unattended half is ready today.
- **G3 — aged state about the rig** (F4). Overlay P11: cleaned first.

## 6. The path to Visit 6

Checked against the R17 table; it keeps the plan's order and adds only what the plan already needs.

1. **Close G1** (new, small): the R17.2 cells above, plus F6's dead code and F7's comment. Bench-only source;
   no library change.
2. **«#3574» bench cleanup** as planned. It narrows t0 and the scan/char/detect records before they are loaded.
3. **Build the stop-mode hand test** (F3), on the proven `t0-hand` panel technique.
4. **«#3575» scan redesign + floor tier**, which needs F5's answer and F4's cleanup.
5. **«#3576» Visit 6**, in this load order: unattended `t0` → `dual-d` → `dual-b` → `dual-c` → `dual-a` →
   `dual-clock-200/-270/-300` → `scan`; then attended `dual-ui` (certifies the PL-64 panel rebuild, a
   prerequisite for the floor panel) → the stop-mode hand test → the spin-in-place floor run. Not loaded: F10.
   Named **before** the run: Stephen notes which ladder rungs he feels kick (TRKICK's negative case).
6. **Then** «#3523» offsets → «#3515» docs → «#3516» ship, as planned; and «#3573»'s driver half if TRKICK
   says the kick survives.

**The one sequencing choice this study cannot make (it spends Stephen's bench time):** steps 1-3 are small and
make the unattended loads plus the hand test runnable; step 4 is the largest item left (a two-phase design). Running the unattended half as its own visit *before* step 4 would certify the PASM changes before the
scan is redesigned on top of them. That is a question for Stephen, §8 Q1.

## 7. Not read, and why

- The logs of Visits 1-4, and the evaluations before them: Visit 5 supersedes them for every cell it ran, and the
  plan-state audit of 2026-09-17 already read them.
- The body of every `PL-N` beyond its status line: the cells and tasks cite what they need, and none of this
  study's findings rests on an entry's narrative.
- `DOCs/plans/STOP-STATE-DESIGN.md` beyond its outline: F3 is about the test's absence; §5 of that design holds
  the predictions the test will print.
- Whether each new R17 cell **can FAIL** (D2): this study established that the cells exist and compile, not that
  each criterion has a negative case. That review belongs to «#3576»'s sheet review, before the visit.

## 8. Open questions

- **Q1** (Stephen's: bench time) — one Visit 6, or split it so the unattended half runs before the scan
  redesign? **ANSWERED — STEPHEN 2026-09-19: *"yes, let's split"*.** Visit 6a: t0, dual-d/-b/-c/-a, the three
  clock loads and the stop-mode hand test, after steps 1-3. Visit 6b: the redesigned scan, `dual-ui` and the
  floor run, after step 4.
- **Q2** (a rig fact only Stephen has) — the platform's track width (F5). **ANSWERED — STEPHEN 2026-09-19: *"15.25 inches tire center to center"*.**
