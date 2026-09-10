# Driver Audit — Study Charter

**Opened:** 2026-09-09 · **Type:** study (not a sprint — no fix commitment)

This is a **study**, confirmed with Stephen on 2026-09-09: *"stops at the
findings. fixes are another sprint."* Findings are reported, not fixed. Anything
trivially and obviously safe to fix is flagged in the findings as a one-liner for
a separate green-light rather than being fixed in place.

`sprint-plan` §1 correctly refuses study-shaped work and routes it here to
`ANALYSIS_DIR`, but no skill in the installed set *authors* a study — recorded as
a promotion candidate in `feedback_skill_evolution_candidates.md`. This charter
stands in for the plan document that skill would have produced.

## Scope — in

| # | Surface | Lines | Focus |
|---|---|---|---|
| 1 | `src/isp_bldc_motor.spin2` — Spin2 API layer | ~1130 | Public methods, validation, unit conversion, state reporting |
| 2 | `src/isp_bldc_motor.spin2` — PASM2 driver, `taskPostionSense`, the Spin2↔PASM ABI | ~1230 | Commutation, PWM, ramping, fault handling, hub-offset ABI correctness |
| 3 | `src/isp_steering_2wheel.spin2` | 909 | Two-wheel coordination, distance/rotation math |
| 4 | `src/isp_steering_serial.spin2` + `isp_queue_serial` interface | 532 | Serial command path |
| 5 | `src/isp_bldc_motor_userconfig.spin2`, `src/isp_dist_utils.spin2` | ~370 | Config surface, unit conversion |

**Also in scope by Stephen's direction, 2026-09-09:**

- **PL-2** — Spin2 conformance assessed against **`central:spin2-authoring-guide`**
  (`~/.claude/skills-docs/guides/spin2-authoring-guide.md`, 1469 lines). The
  central guide governs this project; no local copy is made. Conformance findings
  are reported in a **separate section** of the audit document so they do not
  bury the correctness findings.
- **PL-3** — build a documentation-drift instrument (`DOC_AUDIT_COMMAND`) that
  **includes the new documents this study produces**. Spec:
  `sprint-plan/references/doc-audit-instruments.md` — ORPHAN, DUPLICATE, COUNT;
  advisory only, never build-failing; discovers its file set mechanically.

## Scope — out

Third-party and support objects, except where they interact with the driver:
`p2videodrv.spin2`, `p2textdrv.spin2`, `jm_*.spin2`, `isp_serial*.spin2` internals,
`isp_hdmi_debug.spin2`, `isp_flysky_rx.spin2`, `isp_discon_tracker.spin2`.
Dead `hng034rm.spin2` (PL-1, already diagnosed). The `test_*` / `util_*` programs
are read as *evidence about driver behavior*, not audited as deliverables.

## Method

1. Read every in-scope line. No sampling.
2. **`p2kb-mcp` is `DOMAIN_AUTHORITY`** — every assertion about PASM2 encoding,
   flag effects, timing, or Spin2 semantics is verified against it before it is
   written down, never asserted from recall. A finding resting on an unverified
   language claim is marked unverified.
3. Cite `file:line` for every finding.
4. Severity: **Defect** (wrong behavior), **Latent** (wrong under conditions not
   currently hit), **Feature-gap** (documented or implied but not working),
   **Risk** (fragile, no current failure), **Conformance** (guide deviation).
5. Corroborate against the two known leads in `README.md` — *drive status
   reporting is not working in the base objects*, and *motor can fault under
   higher load* — rather than treating them as given.

## Deliverables

| Artifact | Location | Rationale |
|---|---|---|
| Theory of Operations | `DRIVER-THEORY-OF-OPERATIONS.md` (repo root) | Permanent developer reference; the project's user-facing `.md` docs live at the root (`DRIVE-OBJECTS.md`, `ADDING_MOTOR.md`, …) and ship in the release archive |
| Audit findings | `DOCs/analyses/DRIVER-AUDIT-2026-09-09.md` | Point-in-time study; `ANALYSIS_DIR` accumulates without an archival flow |
| Doc-drift instrument | `tools/doc-audit.sh` + `DOC_AUDIT_COMMAND` set | PL-3 |

## Entry baseline

Build clean, 0 warnings across all six library objects. `tools/build-check.sh`
PASS — 39/39 files certified, both release demos certified. Recorded 2026-09-09.
