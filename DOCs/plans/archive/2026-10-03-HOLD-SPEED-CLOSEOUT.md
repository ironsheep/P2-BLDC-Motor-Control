# Hold Speed Under Load (6.1.0) — closeout, 2026-10-03

*Retrospective: `DOCs/plans/archive/2026-10-03-6.1.0-SPRINT-Retrospective.md`*

**Plan:** `DOCs/plans/archive/HOLD-SPEED-SPRINT-PLAN.md` (written 2026-10-01, closed 2026-10-03).
**Outcome:** the plan shipped whole. v6.1.0 is tagged at `54f7c43` (VERSION 6.1.0, CHANGELOG entry dated 2026-10-03,
every archive set carrying LICENSE and CHANGELOG.md); Stephen pushed main and the tag, and the release workflow opens the
draft. The driver is DRIVER_REV 49, certified on the third bench visit. Two harness corrections from that visit
(PL-182, PL-192) were made at closeout, `test_bench_dual` SRC_REV 82.

**Method.** The plan was walked section by section against the tree at closeout (`54f7c43` plus the SRC_REV 82 harness
change). The plan's §15 cross-reference table was reconciled first: it had no rows for the eight tasks the visits added
(«#3662»-«#3669»); they were added at closeout and the table now names every numbered section. Verdicts: SHIPPED (with
the line that shows it), PARTIAL, MISSING, SUPERSEDED.

## Per section

| § | Commitment | Verdict | Evidence |
|---|---|---|---|
| 1.1 | Design D-5, the held field at the limit; Stephen rules («#3645») | SHIPPED | `DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md` §4.9; ruled 2026-10-01 |
| 1.2 | Build D-1..D-3 + D-5 («#3655») | SHIPPED | `src/isp_bldc_motor.spin2:7116` (`SERVO_ACC_SHIFT` 16), `:7095` (`LAG_LIM` 64), `:7854` (the servo's setpoint test) |
| 1.3 | Rev A: no separate build | SHIPPED | the same image; current scaling still branches on `eDetectedBoard` |
| 1.4 | The events' meaning (Q4 (a)) | SHIPPED | `DRIVE-OBJECTS.md` event rows (860fc13) |
| 1.5 | The blocked stop latches under D-5; the lag faults and the slow-down kick («#3662») | SHIPPED, CERTIFIED | `src/isp_bldc_motor.spin2:2913-2916` (`bLimSinceTick`); third visit: obstacle cells PASS, counts 997 / 1,003; no reversal fault over 123 samples |
| 1.6 | The pivot's inner wheel holds («#3663», Stephen: "yes your recommendation") | SHIPPED, CERTIFIED | `src/demo_dual_motor_rc.spin2:121`, `src/demo_dual_motor_rc_hdmi.spin2:135` (`holdAtStop(true)`); RC-PIVOT PASS (third visit) |
| 1.7 | Smooth top speed: T-1 and the limit hold's three gaps («#3668», Stephen: "yes a", "yes A") | SHIPPED, CERTIFIED | `src/isp_bldc_motor.spin2:8435` (`fold_seen`), `:7103` (`LIM_SPAN`), `:7105` (`LIM_CAP_K`), `:8169` (`holdRelease`); TOPSPD 245 on all four wheel-directions, OVRSTEP PASS, LDFLT PASS |
| 2 | Ladder A-3 / A-5 verdicts in the log («#3654») | SHIPPED | `src/test_bench_dual.spin2:3698` (SRVHUNT, A-3), `:3700` (SRVKEEP, A-5) |
| 3 | Floor premises and the fix's floor cells («#3656», «#3657») | SHIPPED, CERTIFIED | `src/test_bench_dual.spin2:3704` (SPINRATE), `:3712` (BLKLIMIT); PL-168 |
| 3.1 | The premises the first visit disproved; no act the log can carry («#3664») | SHIPPED | PL-182 / PL-183 / PL-185 CORRECTED; LIMGIVE and SPINPEAK PASS. **The traced slow leg's full emission** failed on the third visit (391 of 1,712 samples) and was corrected at closeout (SRC_REV 82, below): code-complete, not yet run |
| 4 | Record labels check themselves («#3651») | SHIPPED | `src/test_bench_dual.spin2:3695`, `:29852` (TOKTAB) |
| 5 | Every bench log names its commit («#3652») | SHIPPED | `src/isp_bench_commit.spin2:27`; every third-visit banner read `e1b412d` |
| 6 | Style gate PRI docs and T128 fixture; booleans as words; `bc_*` assets deleted; FlySky deadband («#3646»-«#3649») | SHIPPED | `tools/fixtures/style/T128.spin2`; `--self-test` exit 0 at closeout; `src/demo_dual_motor_rc.spin2:667` (`RC_RATE_DEADBAND_MM_S2`) |
| 7 | Pin groups refused at compile («#3650») | SHIPPED | `src/isp_bldc_motor_userconfig.spin2:162`, `:184`; `tools/build-check.sh:218` (step 3a) |
| 8 | `DRIVER_BOARDS.md` («#3653») | SHIPPED | `DRIVER_BOARDS.md` |
| 9 | The first visit: pack, sheet, evaluation («#3658», «#3659») | SHIPPED | `DOCs/analyses/bench/2026-10-02/VISIT-6.1.0-EVALUATION.md` (local, ignored by design) |
| 9.1 | The second visit («#3665», «#3667») | SHIPPED | `DOCs/analyses/bench/2026-10-02b/VISIT-6.1.0B-EVALUATION.md` |
| 9.2 | The third visit («#3668», «#3669») | SHIPPED | `DOCs/analyses/bench/2026-10-02c/VISIT-6.1.0C-EVALUATION.md`; recorded in `57eb218` |
| 10 | The release («#3666»; «#3661» SUPERSEDED 2026-10-01, the release returned 2026-10-02) | SHIPPED | `VERSION`; `CHANGELOG.md:6`; `tools/make-release.sh:161` (LICENSE and CHANGELOG.md in each set, Stephen 2026-10-03) |
| Blast Radius | The user docs brought to the certified driver («#3660») | SHIPPED | `860fc13`: README, DRIVER-THEORY, the 6.5″ manual and its sources page, DRIVE-OBJECTS, DEVELOP, DRIVER_BOARDS, TECHNIQUES, ADDING_MOTOR, MOTOR_CHOICE, a pointer from DRIVER-6.0-REWORK |

**Fixed at closeout, `test_bench_dual` SRC_REV 82** (the closeout's "fix before closing"):

- **PL-182:** `traceWalk()` capped emission at `TRACE_EMIT_MAX` apart from `trEmitMax`, so the slow leg's full trace
  stopped at the usual cap. It now caps at `TRACE_EMIT_MAX #> trEmitMax`.
- **PL-192:** LDHUNT counted a wheel's first in-window path-limiter engage as a transition, so a hold that engaged once
  and held to the stop read 1 and failed. `evDrain()` keeps that onset apart (`evdPathOn`), and it counts toward the
  engaged precondition, not the flips. The third visit's hold now reads 0; the hunting negative (an engage and release
  every 720-790 ms) still reads several.

## Conformance

Quoted from `.claude/skill-conventions.md`:

```yaml
  - surface: "src/**/*.spin2"
    guide: central:spin2-authoring-guide
    when: authoring or editing any P2 source
    strength: gate
  - surface: "CHANGELOG.md"
    guide: central:changelog-voicing
    when: any changelog entry
    strength: gate
  - surface: "src/test_bench_*.spin2 -- DEBUG PLOT panel source, and any tier's debug() volume"
    guide: DOCs/procedures/PLOT-DISPLAY-RULES.md
    when: authoring or editing a PLOT panel, or adding debug() output to a bench tier
    strength: gate
  - surface: "the user Markdown set (README.md, DRIVE-OBJECTS*.md, DEVELOP.md, SERIAL-CONTROL.md, VOLTAGE-SENSOR.md, the motor and driver pages)"
    guide: .claude/doctrine-overlay.md P8 (the user register: no visit, cell, PL or task ids; current state only)
    when: any edit to a user-facing page
    strength: reference
```

- `src/**/*.spin2`: `tools/check_style.sh` PASS, 46 files, at closeout.
- `CHANGELOG.md`: the v6.1.0 entry was checked against the guide's released-mode rules before `54f7c43`: no test-evidence
  lines; the three sprint-internal regressions fixed before release carry no entry; Known Issues reconciled with Stephen.
- PLOT rules: no panel was edited; rule 1 (the DEBUG footprint) is enforced by `tools/build-check.sh` (below).
- User Markdown: `860fc13` searched for `PL-`, `Visit` and `«#` in the user set; none.
- **A surface with no row:** `tools/*.sh` (this sprint changed `tools/make-release.sh`, `tools/make-bench-pack.sh`,
  `tools/bench-run.sh`, `tools/build-check.sh`). They follow doctrine P2 (a script that fronts Stephen's tools echoes
  every command and changes nothing behind him), but no row binds it. **Proposed row:** surface `tools/*.sh`, guide
  `.claude/doctrine-overlay.md` P2, when "any edit to a script that runs his tools", strength reference.

**Assertions.** The user-facing claims this sprint added are the drive's own measured behaviour (the third visit's
certification, summarised in the 6.5″ manual with its sources page) or its own design. One is unverified: the manual's
§3.2 feedforward row reads "at 18.5 V" and may be the bench pack's voltage rather than a property of the motor. It is a
labelled measurement condition in a human-facing page, not a contradicted claim; it is carried below.

## Exit baseline

| Gate | Entry (`54c4a1e`, 2026-10-01) | Exit (closeout tree, 2026-10-03) |
|---|---|---|
| `tools/build-check.sh` | PASS 50/50, both demos certified, 60 bench tiers in footprint, 0 warnings | PASS 51/51, both demos certified plain and `-d`, all 61 bench tiers in footprint, 0 warnings |
| `tools/check_style.sh` | PASS, 45 files | PASS, 46 files |
| `tools/check_style.sh --self-test` | FAIL (T128 had no fixture) | exit 0 |
| `tools/doc-audit.sh` | clean | clean (advisory) |

Not worsened; the self-test's failure group was fixed in the sprint as planned (§6). The extra top is
`src/isp_bench_commit.spin2` (§5); the extra bench tier is `dual-tokneg` (§4's negative).

## Verification, stated honestly

- **Verified on the canonical target (the bench and the floor, DRIVER_REV 49, third visit 2026-10-02c):** the hold under
  load, the blocked stop, the limit hold's release, top speed, the over-command step, the grab's faults, the pivot, and
  every regression guard on the sheet (TRKICK-A, SRVHUNT / SRVKEEP, SPINRATE, RAMPARR, BLKFLT).
- **Code-complete, not yet run:** SRC_REV 82's two harness corrections (PL-182's full slow trace; PL-192's LDHUNT
  count). Neither changes the driver or a certified verdict; they run on the next floor-auto and floor-grab.
- **Release packages:** `tools/make-release.sh --preview` built the three sets at `54f7c43`; the workflow builds them
  again from the tag.

## Carryover

- **PL-182 / PL-192** — run SRC_REV 82 on the next floor visit (`floor-auto`, `floor-grab`): the slow leg's trace emits
  every sample and places LIMGIVE's held passes; LDHUNT reads 0 on a single held engagement.
- **PL-192's watch: SPINSTOP** — one medium leg stopped one tick past its tolerance (216 against 212) on the third visit,
  1 of 20 stops, new on DRIVER_REV 49. Watch it on the next floor-auto; act if it repeats.
- **S-b** — while a wheel is held at its current limit, `drv_incr` is not the field's speed. The harness reads it so
  (LDPATH NOMEAS LIMIT_HELD; FOLLOW's OVER readings marked FIELD_NOT_SPEED). Recorded in the design §4.12.7; no user
  effect.
- **The manual's §3.2 "at 18.5 V"** — confirm against `DOCs/analyses/MOTOR-6.5IN-MANUAL-SOURCES.md` whether it is the pack
  voltage of the measurement or a motor property, and update both pages together.
- **DocoEng** — the next plan: the 4,000 RPM motor's qualification (CHANGELOG Known Issue).

## The board at close

Captured with `export_markdown include_completed:true` before archiving: 24 completed, 0 pending, 0 in progress,
**0 paused**. Completed this sprint: «#3645»-«#3660», «#3662»-«#3669». Superseded: «#3661» (2026-10-01, the release
moved out of the plan; it returned as «#3666»). `session_summary` for 2026-10-03: 5 tasks completed («#3667», «#3668»,
«#3669», «#3660», «#3666»), 2 h 59 m tracked. Sprint total: 6 h 27 m tracked against 56 h 5 m estimated.

**Task cards read against tasks started.** The board does not count reads. The session transcripts show the card
referenced in three of the sprint's four sessions; the second session of 2026-10-01 (nine starts) shows no reference. A
process miss, recorded for the retrospective.
