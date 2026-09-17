# Punch-list archive — 2026-09-17

Items swept out of [`DOCs/PUNCH-LIST.md`](../../PUNCH-LIST.md) as confirmed done, during the
Bench Readiness sprint's Visit 4 write-back («#3514»).

**This file is never re-edited.** If an archived item must be reopened, it returns to the active
punch list as a *new* item that references this archive.

**"What is outstanding?" is answered from the active punch list only** — never re-derived from
this file.

---

## PL-9 — HAZARD GUARD: do not "fix" A1's enum comparison on its own

**Closed 2026-09-17.** Swept on the disposition its own entry carried: *"DONE IN THE TREE — sweep
at closeout."*

**Verified against the tree before sweeping** (doctrine overlay P8 — a record is a claim):
`src/isp_bldc_motor.spin2:497-498` now reads

```spin2
    gapInNs := 260
    dead_gap    := (ticks1us * gapInNs) / 1_000 ' (was OFFSET) 260 of these made into "value nS"
```

— **unconditional, with no board-revision branch**, and the variable renamed from `gapInMS` to
`gapInNs` as the guard required (it holds nanoseconds and always did).

**Confirmed on hardware at Visit 4**, `DOCs/analyses/bench/2026-09-17/debug_260917-125254.log:475`:
`dead_gap = 70` — 70 clocks at 270 MHz = **259.3 ns**, clearing the 250 ns minimum that *both*
Parallax manuals specify. Visit 3 had already measured 260 ns across 200 / 270 / 300 MHz.

**What the guard was for, preserved because it is the reason the entry existed.** Audit finding
**A1** looked like a one-word fix: a comparison of `eDetectedBoard` (holding `REV_*`, 21/22)
against `BRD_REV_B` (32) that can never match, so every board got 260 ns instead of Rev B's
intended 52. Repairing the comparison *alone* would have dropped every Rev B board to ~52 ns —
roughly five times below the vendor minimum — and produced exactly the shoot-through overcurrent
the manuals warn about. **The bug was protecting the hardware.** The correct fix was to delete the
conditional, because the distinction it encoded does not exist: deadtime here is set by MOSFET
response, not by driver speed, and Rev B's ~2× faster UCC27211D carries the identical 250 ns
requirement as Rev A's MIC4604.

The guard did its job — the naive fix was never applied.

**Full reasoning, kept live:** `DOCs/analyses/DRIVER-AUDIT-2026-09-09.md`, finding **A1**, with
its 2026-09-10 revision and its 2026-09-17 hardware confirmation.

---

## PL-24 — a second `start()` on a running motor orphans the first driver cog

**Closed 2026-09-17.**

**Original entry, 2026-09-12 («#3500» agent, DERIVED from source, not then observed on hardware):**
`startEx()` in `src/isp_bldc_motor.spin2` launched a new driver cog without stopping one this
instance already ran. The first cog kept driving the same pins with no handle left to stop it, and
since «#3500» `getBoardType()` then returned the revision recorded at the first start — possibly
for a different pin group. The same stale claim `validatePinBase()` could leave behind when a
restart named an illegal group was part of the same defect.

**STEPHEN, 2026-09-12:** *"why wouldn't a second start do a driver stop to free the cog then
start?"* and *"why would we ever let the orphaned cog state exist?"*

**Fixed** in `4e82b08`, *"Make start() report success and failure, and stop leaking detection state
across restarts"*: `startEx()` calls `stop()` first whenever this instance already runs a driver or
holds a pin claim, so the cog is freed, the pins and the claim are released, and the new start
begins clean. **An orphaned cog can no longer exist** — the state is designed out rather than
detected, which is the construction Stephen's second question asked for.

**Confirmed on hardware at Visit 4** — this is what moved it from "being fixed" to closed:

- `DOCs/analyses/bench/2026-09-17/debug_260917-131445.log` part A performs **24 start/stop
  lifecycles** (`life,1` … `life,24`), and every `BM-START` reports `cog_ret,3 cog_ok,TRUE`.
  **The same cog id is reused every time.** An orphaning defect would have climbed through the
  cog ids and exhausted them long before the twenty-fourth start.
- `R14-DUAL-REVB-A` measured **0 starts not Rev B out of n=12** per motor (`:15292, :15297`) — the
  detection-state leak named in the original entry is gone too.

⚠ **One limb is NOT covered by this closure, and it is tracked elsewhere.** The *failure* path —
`start()` with no free cog returning −1 and `ERR_NO_FREE_COG` without leaking — has no run-time
evidence, because `R16-T0-FRONTFAIL` was lost when the Visit 4 `t0` binary emitted nothing. That is
**PL-74**, and audit finding **AD** stays open on it. PL-24 closes on the orphaning defect it
actually describes; it does not close AD.

---

## PL-3 — Doc-drift instrument built — closed 2026-09-09

`tools/doc-audit.sh` written and wired to `DOC_AUDIT_COMMAND`, discharging central
adoption action v6(a). Detects ORPHAN (docs naming methods absent from `src/`, with a
Spin2 built-in allowlist so it does not cry wolf), DUPLICATE (the same prose maintained
in 2+ documents — the drift *mechanism*, not just a finding), and COUNT (asserted numbers
recomputed from their real source). Advisory only, always exits 0. File set discovered
mechanically.

Verified by negative test: perturbing `VERSION` produces a MISMATCH, restoring it returns
to clean — the checks demonstrably detect rather than merely passing.

**It found six real DUPLICATE pairs on first run**, listed in PL-7.

---

## PL-4 — README changelog brought current — closed 2026-09-09

README's *Current status → Latest Changes* block stopped at **11 August 2023 /
v3.0.0** while git tags reached **v5.0.2** — two major releases of user-facing
history unrecorded, with *Known Issues* still describing v4.1.0 as current.

Reconstructed from commit substance across six tag ranges and added entries for
**v4.0.0, v4.1.0, v4.2.0, v5.0.0, v5.0.1 and v5.0.2**. *Known Issues* gained a
v5.0.2 block carrying forward the two long-standing items, and now records that
the current/power calculation issue — listed since v3.0.0 — was fixed in v5.0.0
by commit `4c9e4ed`.

---

## PL-5 — Duplicate `angleTest.spin2` removed — closed 2026-09-09

The repo root held `angleTest.spin2`, byte-identical (1917 bytes) to
`src/test_angle.spin2`. Verified identical by `diff`, then deleted the root
copy. It was gitignored and untracked, so the removal touches no commit. The
`src/` copy is intact and remains covered by the build gate.
