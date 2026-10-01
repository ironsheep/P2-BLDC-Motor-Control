# Window-free bench (Plan A) — closeout, 2026-10-01

**Plan:** `DOCs/plans/archive/WINDOW-FREE-BENCH-SPRINT-PLAN.md` (written 2026-09-30, closed 2026-10-01).
**Outcome:** the plan's 6.0.0 scope shipped. v6.0.0 is tagged at `ccef603` (VERSION 6.0.0, CHANGELOG entry dated
2026-10-01) and its release workflow opened the draft. §11 (PL-167, holding speed under load) and §12 (PL-168, the test
premises) were moved to 6.1.0 by Stephen's ruling R21: *"ok yes, A lets get 6.0.0 to release first then we'll follow
with this new effort"*.

**Method.** The plan was walked section by section against the tree at `050b8cd` by a read-only audit, and each finding
below was re-checked here. Verdicts: SHIPPED (with the line that shows it), PARTIAL, MISSING, SUPERSEDED (by a later
ruling, named), CARRIED (moved to 6.1.0 by R21).

## Per section

| § | Commitment | Verdict | Evidence |
|---|---|---|---|
| 1 | «#3613» walked and closed; «#3611» rewritten; «#3576» superseded | SHIPPED | the board export below: «#3613» CLOSED 2026-09-30 with its evidence; «#3576» SUPERSEDED 2026-09-30 |
| 1 | Visit 10 "Board swap" rows superseded | SHIPPED | `DOCs/analyses/bench/VISIT-10-RUNSHEET.md:196-199` |
| 1 | `t0-reva` PRECONDITION with no swap | SHIPPED | `tools/bench-run.sh:303` |
| 1 | PL-163 closes on the Rev A platform | SHIPPED | `DOCs/PUNCH-LIST.md:2496-2500` |
| 1 | CHANGELOG: the support-object renames; `driveDirection()` turns right | SHIPPED | `CHANGELOG.md:93-102`; `src/isp_flysky_rx.spin2:147,155,163` |
| 2 | Fourteen single-action floor tiers, window-free, 10 s lead-in, RESULT line, banner names the action | SHIPPED | `tools/bench-run.sh:450-515`; `src/test_bench_dual.spin2:15835` (`LEAD_IN_MS`), `:20894-20902`, `:616-618` |
| 2 | Grab time bound raised for a held drive | SHIPPED | `src/test_bench_dual.spin2:16088` (`LOAD_LEG_MS` 20_000) |
| 2 | "Nothing after the action"; "one turn at most per spin" | SUPERSEDED by R15 (sessions drive back to start) and R20 (untethered) | the single tiers keep it; the tether and one-turn wording left in `bench-run.sh:231-232,473` and the run sheet is CARRIED (PL-168, item 6) |
| 3 | Rev A test on both groups, lead-in, no window, `FOLD_MIN_MV` stated, PRECONDITION rewritten | SHIPPED | `src/test_bench_t0.spin2:5513,5579,5654,5726-5727,1259-1264`; `tools/bench-run.sh:296-303` |
| 3 | The grip as the positive control | SUPERSEDED by R15 (§10 session 1: a hard speed-up, hands-off) | `src/test_bench_t0.spin2:5487-5495` |
| 4 | "1 rotation" removed from three programs; class search | SHIPPED | a search of `src/` finds only the `CH_11` enum (`isp_flysky_rx.spin2:24`); every `isSwitch*()` names A-D |
| 5 | The pack: fourteen tiers + `t0-reva` + `floor-rc` | SUPERSEDED by R15 | `tools/make-bench-pack.sh:42` (the five sessions); `dist/bench-c289e1f.zip` deleted |
| 6 | The run sheet as his only instructions | SHIPPED | `DOCs/analyses/bench/VISIT-6B-FLOOR-RUNSHEET.md` (rewritten; the rerun section for the five sessions) |
| 7 | Both visits analysed per the processing procedure | SHIPPED | `DOCs/analyses/bench/2026-09-30/{reva,floor,reva2,floor2}/*-EVALUATION.md` |
| 8 | Punch-list statuses: PL-93, 95, 106, 111, 144, 150, PL-160's feel | SHIPPED | `DOCs/PUNCH-LIST.md` status rows; PL-150's stale disposition corrected at closeout |
| 8 | PL-132 | PARTIAL | `DOCs/PUNCH-LIST.md:80`: AWAITS CERT, its COAST cell NOMEAS twice. Carried (below) |
| 8 | PL-163 | PARTIAL | cells NOMEAS at the 2 A test limit; the every-frame fold absent on both boards; ancillary. No more Rev A runs for 6.0 |
| 8 | PL-117 (archived 2026-09-26, certified wheels up) | SHIPPED | also certified on the floor: SPINPLAT RIGHT 0 % (`floor2/FLOOR-RERUN-EVALUATION.md`, X-5). The archive entry is left as written: archives are never re-edited |
| 8 | Manual §6.5 / §9 and sources; REWORK item 4; CHANGELOG | SHIPPED | `MOTOR-6.5IN-TECHNICAL-MANUAL.md:621-638, 850`; `DRIVER-6.0-REWORK.md:92-103`. The stale "feel on the floor not yet known" line (§7.5) corrected at closeout, with its source row |
| 9 | Every finding fixed, certified or ruled | SHIPPED | PL-167 ruled a Known Issue and 6.1.0 work (R21); PL-168 carried (R21) |
| 10 | Hands-off sessions, fence, H1-H7, `test_bench_t0` SRC_REV 30, FlySky controls and telemetry | SHIPPED | `tools/bench-run.sh:296-303, 460-463, 526-534, 628`; `src/test_bench_dual.spin2:794, 16185-16198, 16906`; `README.md:165`; `CHANGELOG.md:68` |
| 11 | PL-167 design and fix | CARRIED 6.1.0 (R21) | `DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md` (approved; phase 2 desk steps `d748331`) |
| 12 | PL-168 premises | CARRIED 6.1.0 (R21) | `DOCs/PUNCH-LIST.md` PL-168 |
| 13 | PL-167 Known Issue; REWORK, manual, user-doc claims restated; VOLTAGE-SENSOR as built; README note; HDMI stale comments; Known Issues whole; ship | SHIPPED | `CHANGELOG.md` Known Issues; `3ca3d05`, `03233dd`, `80551bb`, `cc0b7bc`, `ccef603`; `src/demo_dual_motor_hdmi.spin2` and `_rc_hdmi` connect routines |

**Cross-reference table.** Sections 10-13 had no row in the plan's task table (added after it was generated); their
tasks were «#3637»-«#3642» and «#3516». Its §2 row and the blast-radius row still said "ten" tiers. Both are
corrected in the archived plan's lifecycle note.

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
    strength: reference
  - surface: "src/test_bench_*.spin2 -- DEBUG PLOT panel source, and any tier's debug() volume"
    guide: DOCs/procedures/PLOT-DISPLAY-RULES.md
    when: authoring or editing a PLOT panel, or adding debug() output to a bench tier
    strength: gate
```

- `tools/check_style.sh`: PASS, 45 files (2026-10-01 at `cc0b7bc`; no source changed since).
- The CHANGELOG was audited against `central:changelog-voicing` on 2026-10-01 at Stephen's request and corrected before
  the tag was moved (`ccef603`).
- Surfaces with no row: `SERIAL-CONTROL.md`, `VOLTAGE-SENSOR.md` and the other user Markdown pages carry the project's
  user-register rule (overlay P8) but no conformance row. **Proposed row:** `*.md` user set, guide overlay P8, strength
  reference.

**Assertions.** The audit listed user-facing claims added since `d109813` that state a P2 fact. The one silicon claim,
`start()` returning a cog id 0-7 or -1, is confirmed by `p2kbSpin2Coginit` (returns 0-7, or -1 when no cog is free).
The rest are the project's own measurements (sourced in `DOCs/analyses/MOTOR-6.5IN-MANUAL-SOURCES.md`) or its own
design.

## Exit baseline

| Gate | Entry (`d109813`, 2026-09-30) | Exit (`cc0b7bc`, 2026-10-01) |
|---|---|---|
| `tools/build-check.sh` | PASS 50/50, both demos, 0 warnings | PASS 50/50, both demos certified plain and `-d`, 0 warnings |
| `tools/check_style.sh` | FAIL, 2 findings in 1 file | PASS, 45 files |
| `tools/doc-audit.sh` | 2 ORPHAN (false positives) | the same 2 |

Not worsened; the style gate improved. No source or gate script changed between `cc0b7bc` and this closeout.

## Verification, stated honestly

- **Verified on the canonical target (the floor and the Rev A bench):** everything §10 lists as certified (PL-93, 95,
  106, 111 API, 144, 150, PL-160's feel, X-5).
- **Code-complete, not certified:** PL-132's coast cell (NOMEAS twice); PL-163's fold cells (NOMEAS at the 2 A limit).
- **Release packages:** each top compiled from its own archive folder, plain and `-d`, 2026-10-01; every file
  byte-identical to `ccef603`.

## Carryover (into the 6.1.0 plan)

- **PL-167** — implement D-1..D-3 of `HOLD-SPEED-UNDER-LOAD-DESIGN.md` in `src/isp_bldc_motor.spin2` (`SERVO_ACC_SHIFT`
  14 → 16; the fast slope past `LAG_SOFT` in `.servoTrim`; `holdDecay` gated on `duty_capped_ + foldback_cnt_`), after
  designing out the modelled regression (a 4 N·m load 0.45 s after a speed change: 40 % after release against 84 %
  today). `LAG_HOLD` stays 100 (D-4 failed its desk condition).
- **PL-168** — in `src/test_bench_dual.spin2`, `tools/bench-run.sh` and the run sheet: the coast no-latch bound, SPINCTL
  at equal speed, per-trial obstacle RESULTs, two-turn quarter spins, the `STEADY_TIMEOUT` / `JUDGED_ACROSS_RUNS`
  labels, and the tether and one-turn wording (`bench-run.sh:231-232,473`; run sheet `:77,116-117,188,190`).
- **PL-132** — the coast-stop cell on the floor (NOMEAS twice); rides on the 6.1.0 floor run's obstacle session.
- **PL-169** — the FlySky knob deadband (ancillary).
- **The CHANGELOG's "up to 43 % slow"** — corrected on main at closeout. v6.0.0 was already published reading 40 %, and
  stays so (Stephen 2026-10-01: *"it's published so C"*); 6.1.0's entry carries the corrected figure if the issue
  remains.

## The board at close

Captured with `export_markdown include_completed:true` before archiving. Completed this sprint: «#3627»-«#3635»,
«#3637»-«#3639», «#3642», «#3611», «#3516», «#3613» (closed on evidence). Superseded: «#3576» (by Plan A, 2026-09-30).
Paused: «#3640», the PL-167 design, by R21 (the blockage stands until the 6.1.0 plan starts it). Pending and carried:
«#3636», «#3641» (6.1.0). Out of the release by Stephen's rulings: «#3506», «#3532», «#3562», «#3592», «#3602».

**Task cards read against tasks started (this session):** 4 started or resumed («#3640», «#3642», «#3611», «#3516»);
the card was read at 1 start («#3642») and at no close. A process miss, recorded for the retrospective.
