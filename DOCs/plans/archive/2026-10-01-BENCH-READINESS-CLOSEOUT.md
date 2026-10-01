# Bench Readiness (the 6.0.0 sprint) — closeout, 2026-10-01

**Plan:** `DOCs/plans/archive/BENCH-READINESS-SPRINT-PLAN.md` (written 2026-09-10; revised through 2026-09-25; closed
2026-10-01). Its floor visit («#3576») was replaced on 2026-09-30 by Plan A, closed the same day:
`2026-10-01-WINDOW-FREE-BENCH-CLOSEOUT.md`.
**Outcome:** v6.0.0 shipped. Tagged at `ccef603` and published by Stephen on 2026-10-01. The target moved from 5.0.3 to
6.0.0 on 2026-09-11 and the release widened on 2026-09-17 (night); both revisions govern this audit.

**Method.** A read-only audit walked the plan end to end, honouring its own rule that a later Sprint Revision governs
earlier text, against `src/`, `tools/`, `CHANGELOG.md`, the punch list and its archives, and the bench evaluations.
Each item it could not mark shipped was re-checked here and dispositioned with Stephen on 2026-10-01.

## What shipped (grouped; the audit's evidence)

| Area | Evidence |
|---|---|
| §1 / §1b, the style gate, green tree-wide | `tools/check_style.sh` (PL-10 at `:1091`, PL-11 at `:724`, T41); PASS 45 files at `cc0b7bc` |
| §2, DEBUG channels | `isp_bldc_motor.spin2:268` (`DEBUG_MASK = user.MOTOR_DBG_MASK`), `isp_steering_2wheel.spin2:231`; `useDebug` gone |
| §3-§5, harnesses and runner | `test_bench_t0`, `test_bench_dual`, `test_bench_char`, `test_bench_scan`, `test_bench_detect`, `isp_bench_log`; `tools/bench-run.sh` |
| §8-§9, the bench passes and their write-back | evaluations for Pass 1, Visits 1-10, the scan runs, the RC and floor runs; punch-list sweeps in `DOCs/plans/archive/` |
| Silos | the restored sense scaling (`isp_bldc_motor.spin2:7816-7830`, `:8183`); `pinclear` detection fix (`:400`, `:1990`); hall counters (`:1881`); `wheelGeometry()` (`:2171`); `start()` returns a cog id or -1; the front cog (`startOwned` `:343`, `front*` from `:2746`); the dead-gap conditional deleted (`:4395-4401`) |
| R16-R20, the API and the driver | no `abort` in the library objects; `ERR_BOARD_NOT_DETECTED`; `setCommandTimeout`, `setFaultResponse`, `setHoldLimits`, `setStartChecks`, `getStopReason`, `getEvent`, `clearProtectiveStop`, `checkWiring`, `getPackVoltage`, `getHealth`, `getDriveVoltage`, `getHoldStatus`, `getFaultCause`; `I_PEAK_A` 40 / `I_CONT_A` 27; DRIVER_REV 46; `FR_GRADED` default |
| R17-R18, commutation | hall zero Z −4 and lead L 18 (`:4986-4987`); the dynamic-lead table (`:5009-5019`); limits ceiling 165×10⁶ / floor 100,000, confirmed at Visit 9b |
| §10, release documentation | `VERSION`, the tag, `CHANGELOG.md`, `DRIVE-OBJECTS.md` / `-SERIAL.md`, `DEVELOP.md`, `SERIAL-CONTROL.md`, `MOTOR_CHOICE.md`; `isp_bldc_motor.txt` untracked (`be98cf8`) |
| Exit criteria | the A/B detection sweep on both rigs; hall-rotation ground truth (Visit 2) |

## Superseded and deferred

- **Superseded within the plan or by Plan A:** the §6 analyser (withdrawn 2026-09-15); the §7 reading sheet and §8.1
  meter (deleted with the meter); the 5.0.3 target; "force BRD_REV_B"; the Sequencing section; «#3523» (by R18.2a);
  «#3573»'s driver half (into R18.4); «#3538» (by «#3554»/«#3555»); the floor items R17.9b, R19.8, «#3591», R18.7 E5 and
  R17.8's floor spin (by Plan A).
- **Deferred by Stephen's rulings:** «#3506» (*"we are not doing any external measurement"*, 2026-09-14), «#3532» and
  «#3562» (*"no those three are not in"*, 2026-09-17), «#3592», back-EMF «#3602» and PL-105 (*"defer back EMF"*,
  2026-09-22), the 2026-09-27 release scope (serial testing, DocoEng, the clock range, PL-102 Q4, PL-165, PL-166; PL-118
  as a Known Issue), PL-167 (a Known Issue, fixed in 6.1.0, R21).

## Items not shipped, and their disposition (Stephen, 2026-10-01)

| # | Item | Disposition |
|---|---|---|
| M1 | `DRIVER_BOARDS.md`, one section per board revision (asked for 2026-09-16) | **6.1.0 scope**: *"yes do this"* |
| P1 | `images/objects-cogs.png` predates the front cog | **Stephen's own**: *"for me to do, not for you to track"* |
| P2 | `CLAUDE.md`'s stale board-revision and `isp_bldc_motor.txt` paragraphs | **Fixed at closeout** (*"never leave this file outdated, fix as soon as seen always!"*) |
| P3 | LIMITS-RESET L3 (`ACCEL_MAX`, PL-109), L6 (`duty_min`, PL-110), E5 | open on the punch list as before; E5 rides on the floor runs |
| P4 | LIMITS-RESET L4, the 75 % default top speed | **Closed as implemented** (*"leave it as implemeted"*) |
| P5 | `DRIVE-OBJECTS.md:378`'s ≈100-tick stop travel "derived, not measured" | an honest hedge; left as written |
| P6 | PL-53: the confirming `char` / `detect` run of the record builders | open on the punch list |
| P7 | PL-67, `R2-DETECT-OVERLAP` | **6.1.0 scope**: overlapping pin groups refused at compile time, the refusal proven by `build-check.sh` (*"it can be produced and should be failed at compile time"*) |
| P8 | PL-136 status | **Fixed at closeout**: built, never provoked |
| P9 | `SERIAL-CONTROL.md` said DS_ESTOP clears with `emerclear` | **Fixed at closeout**: it also reports a protective stop, released by `protclear` (`isp_bldc_motor.spin2:1821`) |
| — | `doc-audit.sh`'s two false ORPHANs (Python names in `tools/pasm_equiv/README.md`) | **Fixed at closeout** (*"fix the audit"*): docs under `tools/` skip the ORPHAN check |
| — | PASM memory WP6-WP9 | **Not tracked**: *"we can reevaluate what we need when we next need the space"* |

**Cross-reference tables.** The plan carries nine task tables and no single live one; the 2026-09-10 table is marked
STALE. Mismatches the audit found: §2A is cited but defined only in `BENCH-TEST-PLAN-2026-09-10.md`; «#3537», «#3524»,
«#3519», «#3520» are named in text with no row; R17.x and R18.x carry rows without headed sections or ids;
«#3597»-«#3600», «#3606», «#3625», «#3626» appear in no table. Recorded, not repaired: the plan is archived as written.

## Design documents

Stamped in place with their status, not moved, because the tagged driver source cites their paths in comments:
IMPLEMENTED — ABORT-ERROR-CONTRACT, COG-LIFECYCLE, CURRENT-LIMIT-AND-STOP, DEBUG-CHANNELS, DRIVER-REPORTING,
FRONT-COG-IMPLEMENTATION, MOTION-HARNESS, STOP-STATE, T0-24-INTERACTION (its panel half retired by Plan A R1);
PARTLY IMPLEMENTED, STILL GOVERNS — DRIVE-INTEGRATION (§7 → «#3602»), FIXED-COG-SHAPE («#3562»), LIMITS-RESET;
PARTLY IMPLEMENTED — PASM-MEMORY-REDUCTION (WP6-9 re-evaluated when next needed); RETIRED — VISIT-SIGNOFF.

## Baselines

| Gate | Entry (`a80f8e6`, 2026-09-10) | Exit (`cc0b7bc`, 2026-10-01) |
|---|---|---|
| Compile | PASS 39/39 tops, both demos, 1 exclusion (`hng034rm`, PL-1) | PASS 50/50, both demos certified plain and `-d`, 0 warnings, the same exclusion |
| Style | RED (the new instrument) | PASS, 45 files |
| doc-audit | 1 ORPHAN, 6 DUPLICATE, 0 COUNT | 0 ORPHAN (after the closeout fix), 0 DUPLICATE, 0 COUNT |

Not worsened on any gate.

## Verification, stated honestly

v6.0.0's features were certified wheels-up through Visits 1-10 and the release-candidate pass, and the loaded
behaviours on the floor (Plan A). Validated on the 6.5″ hub motor at 270 MHz on Rev B boards; the DocoEng motor, the
serial path on hardware and other clocks are not validated (the v6.0.0 Known Issues). The release packages were each
compiled from their own folders on 2026-10-01.
