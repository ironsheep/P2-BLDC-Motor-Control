# P2-BLDC-Motor-Control — Punch List

Active outstanding work. Confirmed-done items are swept to a dated archive by
`punch-list-maintenance` at sprint closeout.

Opened 2026-09-09 by the `bootstrap-conventions` / `baseline-health` bootstrap.

---

## Open

### PL-1 — `src/hng034rm.spin2`: superseded, unused, uncompilable — **kept on purpose**

**Disposition decided 2026-09-10 (Stephen): KEEP the file. Do not delete.** This entry now
exists to record *why*, so the question is not reopened every time someone trips over it.

The file is *"Nostalgic displaylisted HDMI for P2 Retromachine"* v0.34 alpha,
© 2012-2021 Piotr Kardasz (pik33@o2.pl), MIT.

**It cannot compile — and it needs four files, not one.** `hng034rm.spin2:1199-1205` pulls
in external data through `DAT` `file` directives:

```spin2
vga_font       file "vgafont.def"
st_font        file "st4font.def"
a8_font        file "atari8.fnt"
ataripalette   file "ataripalettep2.def"
```

`vgafont.def` is merely the first one the compiler trips on. **None of the four is in the
repo, and none has ever been in git history** (searched across all refs and the full object
list). **These four lines are the only external file dependency anywhere in `src/`.**

They are also not reachable through the tooling here: the object was distributed via the
Parallax forums rather than OBEX, and the OBEX index carries no objects by that author.

**Nothing requires it — it was replaced.** `hng034rm` is named exactly once in the tree, and
that line is commented out:

```
src/isp_hdmi_debug.spin2:36:'    hdmi    :   "hng034rm"  ' our HDMI driver (HDMI Eval Adapter)
```

`isp_hdmi_debug` itself is **alive and shipping** — eight top-levels use it, including the
certified release demo `demo_single_motor.spin2` and `util_char_motor.spin2`, which bench
test T1-10 reuses. But it drives HDMI through **`p2textdrv.spin2`**, which is present,
compiles under every config, and needs no external files. **So HDMI debug works today and
loses nothing by this file being unbuildable.**

**Consequences, recorded at each place someone would trip over it:**

| Location | What it says |
| --- | --- |
| `tools/build-check.sh` `EXCLUDED` | Names the file with the full reason; printed on every run, so the gate is never silently incomplete |
| `tools/check_style.sh` `EXCLUDED` | Same file, excluded from the style gate too -- but for the D1 authorship reason (pik33/MIT, vendored, not Stephen's), not the compile reason. See `.claude/skill-conventions.md`'s D1 note next to `CONFORMANCE_GUIDES`, task #3471, 2026-09-10 |
| `src/hng034rm.spin2` header | A banner: not built, not used, cannot compile, superseded, see PL-1 |
| `src/isp_hdmi_debug.spin2:36` | A note at the commented-out reference: superseded by `p2textdrv`, do not uncomment |
| This entry | The reasoning and the decision |

**Cost of keeping it:** the compile gate covers 39 of 40 files rather than 40 of 40, and the
one gap is named and printed on every run. `tools/check_style.sh` covers 34 of 40 -- this file
plus the five other D1-excluded, not-Stephen's-code files (`p2videodrv.spin2`,
`p2textdrv.spin2`, `jm_ez_analog.spin2`, `jm_nstr.spin2`, `jm_sbus_rx.spin2`).

**If it is ever wanted back**, this is a *feature* — re-enabling the HDMI debug display —
not a font-file restoration, and it needs all four data files supplied first. Restoring them
alone would make a 62 KB file compile and change nothing else.

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

**Update 2026-09-10 (task #3471):** `tools/check_style.sh` now exists and
`STYLE_GATE_COMMAND` is set -- the *tooling* debt this item describes is
discharged. The tree itself reports RED under it (576 findings across 34 of
40 `src/*.spin2` files, by design -- the tree predates the guide). That is
`tools/check_style.sh` surfacing latent findings, not a regression, and is
task #3472's job to clear. This item stays open until the tree is green.

### PL-10 -- deferred: `@param`/`@returns` completeness (element->tag direction)

`central:spin2-authoring-guide` 4.3 requires, in full, that every parameter
has a matching `@param` tag and every return value has a matching `@returns`
tag (the element->tag direction), in addition to the direction
`tools/check_style.sh` actually enforces (every *existing* tag must name a
real signature element -- the tag->element direction). Measured 2026-09-10:
approximately **621 sites** across the 34 in-scope files would need a new
tag added.

**Deferred by Stephen, 2026-09-10**, to protect the bench-readiness sprint:
a 621-site documentation pass is a different shape of work than the bench
sessions this sprint exists to unblock, and `tools/check_style.sh` says so
plainly in its own header comment rather than silently under-enforcing 4.3.
Revisit as its own sprint.

### PL-11 -- deferred: PUB-before-PRI ordering (guide 3.2)

`central:spin2-authoring-guide` 3.2 requires all `PUB` methods to precede all
`PRI` methods in a file. `tools/check_style.sh` does not check this --
detection is trivial, but the *fix* is bulk method reordering, and one of the
**10 files** with PUB/PRI interleaved is `src/isp_bldc_motor.spin2`: 2392
lines carrying the Spin2<->PASM2 hub-offset ABI (see CLAUDE.md, "The
Spin2<->PASM2 shared-memory contract") as an EXCLUSIVE_RESOURCE this sprint.
Bulk-reordering methods in that file is the wrong risk for a cosmetic pass,
and is deferred as its own reviewed change, not folded into #3471/#3472.

### PL-12 -- latent: `check_pri_docs` conflates "has a trailing comment" with "is a comment line"

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

### PL-13 -- `isp_serial` and `isp_serial_singleton` disagree on two method names

The two objects are the same serial interface, one adapted as a singleton
("singleton adaptation by Stephen M. Moraco" in its header), and their method
families otherwise mirror each other exactly. Two names do not match:

| `isp_serial.spin2` | `isp_serial_singleton.spin2` |
| --- | --- |
| `PUB fwoct(nNumber, digits)` | `PUB foct(nNumber, digits)` |
| `PUB fwqrt(nNumber, digits)` | `PUB fqrt(nNumber, digits)` |

Every sibling in that family agrees across both files -- `fwdec`, `fwhex`,
`fwbin` are `fw`-prefixed in both -- so the singleton's `foct`/`fqrt` read as
typos rather than as a deliberate difference.

**Why it matters:** the two objects are meant to be interchangeable at the
call site; an application that swaps one for the other silently loses those
two methods and fails to compile on a line that has nothing obviously wrong
with it. **Not fixed here** because renaming a `PUB` is an API change, not a
style finding -- it needs Stephen's call on whether to rename the singleton's
two to match (consistent, but breaks any existing caller) or to add aliases.

Found while verifying the #3472 conformance renames, which touched both
files' parameter lists and so put the two families side by side.

### PL-14 -- `eMotorVoltage` is a documented public parameter that does nothing

**Found 2026-09-10 while building the Tier 0 harness («#3474»). Not in the
24 findings of `DRIVER-AUDIT-2026-09-09.md` -- this is a new one.**

`start()`, `startEx()` and `testSetup()` all take `eMotorVoltage` and all
document it:

```
'' @param eMotorVoltage - The voltage ENUM (PWR_*) for this motor
```

It is never read. The parameter appears **only** in method signatures and in
those doc comments; no method body references it. `init()` passes the
compile-time constant instead:

```
isp_bldc_motor.spin2:259:    confgurePowerLimits(user.DRIVE_VOLTAGE)
```

So `start(pins, PWR_18p5V, mode)` and `start(pins, PWR_25p9V, mode)` behave
identically, and the drive voltage is whatever `isp_bldc_motor_userconfig.spin2`
was compiled with. A user following the published interface can select a
voltage, observe no change, and have no way to tell why -- the API accepts the
argument and the documentation promises it means something.

**Likely history:** voltage selection moved to the user-config file (the
documented mechanism -- users edit section 2) and the parameter was left in
place rather than removed.

**Two possible fixes, and it is an API decision, not a defect fix:** honour the
parameter (a behaviour change for every existing caller, and it would then
disagree with the compile-time power tables), or delete it from all three
signatures and the docs (a breaking signature change for every caller). Either
way `DRIVE-OBJECTS.md` and the generated `isp_bldc_motor.txt` move with it.

**Consequence for the bench suite, already absorbed:** T0-4 (finding O,
voltage legality) cannot sweep voltages through `testSetup()` in a single
build -- only the active config's voltage is ever exercised. Confirming O for
a second voltage needs a rebuild with `DRIVE_VOLTAGE` changed. The harness
documents this inline.

Write this back into `DRIVER-AUDIT-2026-09-09.md` as a new finding when
«#3481» runs.

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

### PL-15 -- no way for a bench binary to ask the operator a question

**Found 2026-09-11 during «#3496» (the A/B detection sweep binary). Raised by
Stephen, not by the code.**

`src/test_bench_detect.spin2` wanted an operator confirmation at the bench --
"the motors are physically unplugged, proceed" -- before starting a driver cog.
There is currently **no established way for a bench binary to prompt and read a
reply.** Three candidate channels were considered and none is usable today:

- **`PC_KEY` via a `` `Term `` debug display.** No precedent anywhere in `src/`;
  this would be its first use. Its documented failure mode is that it compiles
  clean and fails silently at runtime. It is additionally **line-buffered** --
  Stephen confirms the console transmits only when Enter is pressed -- so a
  design waiting on a bare keystroke would hang with the operator sitting there
  having pressed it.
- **Plain serial to `pnut-term-ts`'s terminal.** `pnut-ts` classifies traffic
  and routes anything that is not a cog message or a tick message to the
  terminal, so the path exists. But **the serial singleton would have to share
  the debug port**, which Stephen states is not an easy thing to do, and this
  binary's deliverable is an uncorruptible one-shot log.
- **A DEBUG `PLOT` panel with clickable controls.** ✅ **This is the answer, and
  it is not an experiment.** Stephen has a documented, exercised technique for
  it -- see `DOCs/REF-NO-COMMIT/dbg-display-theory/` (crop-and-overlay sprite
  blitting, a Pillow asset pipeline, and `pc_key`/`pc_mouse` input). It sidesteps
  the port-sharing problem entirely by staying **inside** the DEBUG channel that
  already owns the port. `pc_mouse` fills 7 consecutive longs
  (`xpos, ypos, wheeldelta, lbutton, mbutton, rbutton, pixel`), buttons read
  `-1` when down, and clicks are hit-tested against bounding boxes -- an OK
  button and a typed value field are both standard patterns there.

**Disposition for «#3496»: the question was designed out rather than answered.**
Phase 2 is gated at COMPILE TIME (`-D DETECT_PHASE2`) instead. That is not a
downgrade -- `tools/bench-run.sh` echoes the compile command and Stephen runs it
by hand at the bench, so the flag is a deliberate operator act at the moment it
matters, and its absence makes the binary physically incapable of starting a
driver cog. It also leaves that binary with no runtime branch at all, which is
what the task text asked for.

**Why this stays on the list:** the need recurs. Any future bench binary that
wants a **mid-run** operator decision hits the same wall, because compile-time
gating only works for a decision that can be made *before* the run.

**Corrected 2026-09-11, same day, and the correction makes this CHEAPER than
first written.** This entry originally claimed a PLOT panel could not run under
`tools/bench-run.sh` because that script passes `--console-mode`. That was
wrong, and it was wrong by inference rather than by evidence. `pnut-term-ts
--help` states: `--console-mode` "adds delay before close"; `--headless` is the
flag that suppresses GUI windows; and `--exit-on-end-session`, which the script
also passes, is documented as **"Headed batch mode"**. `bench-run.sh` never
passes `--headless`, so **the bench has been running windowed all along and
PLOT windows, `pc_key` and `pc_mouse` work in the existing invocation
unchanged.** There is therefore NO runner integration cost -- the estimate this
entry was filed with was simply wrong.

Also resolved by the same `--help` read: `-b` defaults to *read from the binary
being downloaded, else 2000000*, which confirms this project's standing rule
never to pass it. The `-b 2000000` "mandatory" claim in
`HOWTO-build-debug-displays-with-claude.md` §5 is scoped to headless runs or to
an older build, and should not be copied into this project.

**Tooling confirmed present 2026-09-11:** Pillow 11.3.0 on Python 3.10.7 for the
BMP art, `pnut-ts -d` for the `{Spin2_v50}` PLOT syntax, PNG round-trip so the
artwork can be verified before a run, and `src/logs/debug_*.log` for the
after-action read. Nothing needs installing. What this project does NOT yet have
is any precedent: no `{Spin2_v50}` file in `src/`, no BMP assets, no generator
script. So the first panel here is a build job, not a rediscovery -- but it is a
build job, and it must not ride on a one-shot hardware session.

**Two defects in the reference docs, to fix at their source (they are not in
this repo):** `DISPLAY-PATTERNS-builders-guide.md:246` uses
`(ypos => 129) and (ypos =< 179)`, which its own companion HOWTO §5 says fails
in `pnut-ts` with "Expected end of line" -- copying that line reproduces the
error the other document warns about. And `DOCs/REF-NO-COMMIT/` is **not
gitignored** despite its name; it is currently untracked, so a `git add -A`
would sweep it in.

### PL-16 -- `util_char_motor.spin2` drive helpers: comment says 10 s, constant is 5 s

**Found 2026-09-11 while building `src/test_bench_char.spin2` («#3497»).**

`src/util_char_motor.spin2:379` and `:392`:

```
wheel.stopAfterTime(DRIVE_AT_SPEED_SECS, wheel.DTU_SEC)      ' set to hold at speed for 10 Sec
```

`DRIVE_AT_SPEED_SECS = 5` at `:57`. The comment says ten seconds on both lines; the
constant has been five. A reader trusting the comment mis-times every
characterisation run made with this tool, and the error is invisible because a
five-second drive still looks like a drive.

**This nearly propagated.** «#3497»'s task body said to reuse
`driveForwardAtSpeed()` / `driveReverseAtSpeed()` for operator-held meter reads.
An operator hold is indefinite; either helper would have stopped the motor five
seconds in, collapsing the meter reading toward zero **while the panel kept
displaying a correct-looking hold**, and the operator would have written down a
number taken from a stopped motor. `test_bench_char.spin2` therefore commands
motion with `testDriveAtMotorIncrement()` and no stop timer at all.

**Fix:** correct both comments to match the constant, or name the constant in the
comment rather than restating its value -- a comment that repeats a number is a
second place for that number to be wrong.

### PL-17 -- the bench line-builder is now duplicated across two binaries

**Found 2026-09-11 during «#3497»'s quality pass.**

`src/test_bench_detect.spin2` and `src/test_bench_char.spin2` each carry their own
copy of the tagged-record line builder -- `lineReset` / `lineAddChar` /
`lineAddText` / `lineAddNum` / `lineField` / `lineTextField` / `lineEmit`, roughly
110 lines including the `udec_()`-compatible underscore grouping that the record
formats depend on being byte-identical.

The duplication is **structural, not careless**: both files are top-level programs,
Spin2 cannot share `PRI` methods between them, and neither can `OBJ`-include the
other. Extraction means a new shared object, e.g. `isp_bench_log.spin2`.

**Deliberately deferred, with the shape recorded so it is not re-derived.** Two
consumers is the point where extraction is arguable; **«#3508» (the motion
harness) will be the third**, which is where it clearly pays. Extracting now would
decertify two binaries that are verified and queued for Bench Pass 1, which the
sprint's standing rule exists to prevent. Do it as part of «#3508», not before.

⚠ Until then the two copies must not drift: the grouping behaviour is what makes
`sum`/`dwell_s` and every other numeric field parseable by the same analyser.

### PL-18 -- two motor instances share one DAT region, so `init()` writes one driver image

**Found 2026-09-11 while checking why two wheels reported identical tick counts.**

`p2kbSpin2ObjectImageDedup`: *"DAT is shared per compiled image; VAR is per instance."*
pnut-ts de-duplicates object images by compiled-image content, so two `OBJ` declarations
of the same file **with no overrides** resolve to ONE image and therefore ONE DAT region.

Measured on `test_bench_spin.spin2`, which declares `wheelL` and `wheelR` with no
overrides -- from the `-m` map:

```
WHEELL : isp_bldc_motor (6911 bytes)     GOWNERP0P15  $00308     DRIVER  HUB $00188
WHEELR : isp_bldc_motor (6911 bytes)     GOWNERP0P15  $00308     DRIVER  HUB $00188
```

Same DAT symbol address, same driver hub address, both instances.

**Mostly this is fine, and one part of it is deliberate.** The `gOwner*` pin-range registry
at `isp_bldc_motor.spin2:144` is DAT *on purpose* -- its comment says so, and shared is
exactly what overlap detection needs. The Spin2/PASM2 status block (`drive_u` .. `drv_state`,
including `pos`) is in `VAR`, so per-wheel position and telemetry are correctly per-instance.
`coginit` snapshots the image into cog RAM at launch, so sharing the code is harmless.

**The latent hazard is `init()`.** It copies the selected motor's `deltas*` / `hltbAngles*`
tables **into the shared driver image** before starting the cog. With two instances of the
same motor type -- every current configuration -- both write identical bytes and nothing is
wrong. **With two instances of DIFFERENT motor types, the second `init()` overwrites the
first's tables in the shared image**, and whether the first cog is affected depends only on
whether it has already latched its copy. That is an ordering-dependent corruption with no
diagnostic.

Nothing in the library prevents or detects the mixed-type case, and `ADDING_MOTOR.md` does
not mention it.

**Options, if it is ever wanted:** fork the image per instance by seeding a DAT long from an
overridable CON (the documented mechanism), or assert at `init()` that a second instance's
motor type matches the first's and abort if not. The second is cheap and turns silent
corruption into a refusal.

⚠ Not a defect in any shipped configuration today -- both wheels are always the same motor.
Recorded because the mechanism is invisible at the `OBJ` line and the failure would look
like flaky hardware.

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
