# P2-BLDC-Motor-Control — Punch List

Active outstanding work. Confirmed-done items are swept to a dated archive by
`punch-list-maintenance` at sprint closeout.

Opened 2026-09-09 by the `bootstrap-conventions` / `baseline-health` bootstrap.

---

## Open

### PL-1 — `src/hng034rm.spin2` is dead and unbuildable

Tracked in git, but:

- it cannot compile — needs a `DAT` preload of `vgafont.def`, which is not
  anywhere in the repo (`hng034rm.spin2:1199: error: DAT file not found`);
- its only reference is **commented out** — `isp_hdmi_debug.spin2` line 36,
  `'    hdmi    :   "hng034rm"`;
- nothing else in `src/` includes it.

It is excluded by name from `tools/build-check.sh`, so the gate stays honest,
but a 62 KB tracked file that builds under no configuration is dead weight.

**Decision needed:** delete the file, or restore `vgafont.def` and re-enable the
HDMI driver. Then drop it from `EXCLUDED` in `tools/build-check.sh`.

### PL-7 — Six blocks of prose are maintained in two or more documents

Found by `tools/doc-audit.sh` on its first run. Each pair will diverge; the only question
is when. The fix is **one canonical copy and links from the others**, never "edit both and
keep them aligned" — that arrangement is what produces the drift.

| Duplicated block | Copies |
| --- | --- |
| Project tagline ("Single and Two-motor driver objects…") | `README.md:3`, `CONTRIBUTING.md:3`, `DRAWINGS.md:3`, `DRIVE-OBJECTS.md:4`, `Movement-STUDY.md:3` |
| "There are two objects in our motor control system…" | `DRIVE-OBJECTS.md:10`, `DRIVE-OBJECTS-SERIAL.md:10` |
| "This steering object makes it easy to…" | `DRIVE-OBJECTS.md:17`, `DRIVE-OBJECTS-SERIAL.md:18` |
| "The object isp_steering_2wheel.spin2 provides…" | `DRIVE-OBJECTS.md:42`, `DRIVE-OBJECTS-SERIAL.md:46` |
| FlySky wiring paragraph | `README.md:231`, `AUTHORS-Platform.md:63` |
| "Video of author running the system…" | `SERIAL-CONTROL.md:55`, `AUTHORS-Platform.md:10` |

`DRIVE-OBJECTS.md` and `DRIVE-OBJECTS-SERIAL.md` share four of the six — they are largely
one document that was forked.

### PL-2 — Spin2 conformance gate is owed

`STYLE_GATE_COMMAND` is unset in `.claude/skill-conventions.md`. The
`central:spin2-authoring-guide` row is at `strength: gate`, so conformance is
supposed to be *checked* before work is called done — unset records the gate as
**owed, not waived** (central adoption action v8(h)).

**Next step:** adopt a conformance script (uSD's `tools/check_style.sh` is the
fleet reference) and set the slot.

**Evidence the gate is load-bearing (2026-09-10):** the TEST-USE ONLY
pass-throughs were first authored *without* consulting the guide and matched the
surrounding legacy style -- no blank `''` separator, no `@param` / `@returns`
tags, no blank line before code. Nothing caught it: `tools/build-check.sh`
compiles clean either way, because conformance is not a compile property. It was
found only by reading the guide by hand and reverting. A script would have caught
it in one second.

### PL-9 -- HAZARD GUARD: do not "fix" A1's enum comparison on its own

**This is a booby trap, and it looks like a one-word fix.**

`isp_bldc_motor.spin2:198` compares `eDetectedBoard` (which holds `REV_*`, 21/22)
against `BRD_REV_B` (32). It can never match, so **every board gets
`gapInMS := 260`** instead of Rev B's intended 52.

Parallax's **Rev B** board documentation states the **recommended minimum
deadtime is 250 ns**, because although the MOSFET drivers are fast (~20 ns
propagation, 7.2 ns rise, 5.5 ns fall) the **MOSFETs** need time to respond;
below that, both FETs are partially on and the channel draws momentary
overcurrent.

| | value | vs. 250 ns minimum |
| --- | --- | --- |
| what the code does today | **260 ns** | compliant |
| what the code intends for Rev B | **52 ns** | **~5x below** |

**So the defect is currently protecting the hardware.** Repairing the comparison
alone drops every Rev B board to ~52 ns and produces exactly the overcurrent the
vendor warns about.

**Both manuals carry the same 250 ns minimum**, despite Rev A using a MIC4604
(39 ns propagation, ~20 ns rise/fall) and Rev B a UCC27211D (~20 ns propagation,
7.2/5.5 ns rise/fall). Rev B's drivers are ~2x faster and the requirement is
identical -- because the limit is set by **MOSFET response, not driver speed**.

**So the per-revision distinction does not exist, and the fix is to DELETE the
conditional**, not to repair the comparison. A single `gapInNs := 260` for both
boards is exactly what the hardware already receives, so it changes nothing on
the bench, and it removes one of root-cause-A's three enum sites outright.

**Keep 260, do not tighten to 250:** `(ticks1us * gap) / 1_000` truncates, and a
literal 250 gives 67 clocks = **248.1 ns at 270 MHz, under spec**. 260 clears
250 ns at 200/270/300 MHz.

**And the prize for chasing a shorter gap is 0.9 % of duty range** (1.14 % at
260 ns vs 0.23 % at 52 ns). Too small to justify any deviation, and too small to
explain jerk -- so **commit `2269894`'s premise does not survive** on measurement
grounds as well as documentary ones. Jerk needs a different mechanism (most
likely C-5's ramp work). Rename `gapInMS` while there; it holds nanoseconds.

Full analysis: **A1** in `DOCs/analyses/DRIVER-AUDIT-2026-09-09.md`. Bench
criterion for T0-1 was inverted to match. Raised 2026-09-10 from vendor
documentation Stephen supplied.

### PL-8 -- `useDebug` is declared, cleared, and never read

`isp_bldc_motor.spin2` declares `LONG useDebug` in its VAR block and assigns it
`FALSE` in `testSetup()`. **Nothing ever reads it.** Every `debug()` in the motor
object is unconditional, so the flag gates nothing.

Two consequences:

- it reads as a working verbosity control and is not one -- a caller setting it
  would see no change in behavior;
- `DOCs/analyses/BENCH-TEST-PLAN-2026-09-10.md` (§6, "Two hazards to design
  around") tells the harness author to quiet library chatter during timed
  sections via `useDebug`. That instruction cannot work as written. The plan has
  been corrected to say so; the underlying gap is real and stays open.

The bench suite needs *some* way to silence library `debug()` during T1-1's 2 ms
coast-down polling and T1-7's 500 us ramp capture, or those measurements are
dominated by serial output. **Decision needed:** wire `useDebug` up for real
(gate the motor object's `debug()` calls on it), or delete the dead flag and
solve quieting another way.

Found 2026-09-10 while adding the TEST-USE ONLY pass-throughs.

---

## Recently closed

### PL-3 — Doc-drift instrument built — closed 2026-09-09

`tools/doc-audit.sh` written and wired to `DOC_AUDIT_COMMAND`, discharging central
adoption action v6(a). Detects ORPHAN (docs naming methods absent from `src/`, with a
Spin2 built-in allowlist so it does not cry wolf), DUPLICATE (the same prose maintained
in 2+ documents — the drift *mechanism*, not just a finding), and COUNT (asserted numbers
recomputed from their real source). Advisory only, always exits 0. File set discovered
mechanically.

Verified by negative test: perturbing `VERSION` produces a MISMATCH, restoring it returns
to clean — the checks demonstrably detect rather than merely passing.

**It found six real DUPLICATE pairs on first run**, listed in PL-7.

### PL-4 — README changelog brought current — closed 2026-09-09

README's *Current status → Latest Changes* block stopped at **11 August 2023 /
v3.0.0** while git tags reached **v5.0.2** — two major releases of user-facing
history unrecorded, with *Known Issues* still describing v4.1.0 as current.

Reconstructed from commit substance across six tag ranges and added entries for
**v4.0.0, v4.1.0, v4.2.0, v5.0.0, v5.0.1 and v5.0.2**. *Known Issues* gained a
v5.0.2 block carrying forward the two long-standing items, and now records that
the current/power calculation issue — listed since v3.0.0 — was fixed in v5.0.0
by commit `4c9e4ed`.

### PL-5 — Duplicate `angleTest.spin2` removed — closed 2026-09-09

The repo root held `angleTest.spin2`, byte-identical (1917 bytes) to
`src/test_angle.spin2`. Verified identical by `diff`, then deleted the root
copy. It was gitignored and untracked, so the removal touches no commit. The
`src/` copy is intact and remains covered by the build gate.

---

## Removed from this list

**Legacy sync scripts** (`src/chk`, `src/get`, `scripts/get`, `scripts/getKS`,
`scripts/diffSrc`). Tracked here briefly on 2026-09-09, then removed at
Stephen's direction — **their removal is his to do, not this list's**.

The operating rule stands and is recorded in `CLAUDE.md` and
`.claude/skill-conventions.md`: all work happens in this work tree, and these
five must not be run — `src/get` and `scripts/get*` copy *into* `src/` and would
overwrite the tree from a stale external source. They are vestiges of sharing
source between a Mac and a Windows machine, which the cross-platform
`pnut-ts` / `pnut-term-ts` toolset made unnecessary.
