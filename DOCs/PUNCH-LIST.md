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

> **DONE IN THE TREE — sweep at closeout.** MEASURED 2026-09-12 against source `d4f9d39`: the
> conditional is already deleted and `gapInMS := 260` is unconditional
> (`isp_bldc_motor.spin2:278-286`, with an A1/PL-9 comment). Bench Pass 1 printed
> `dead_gap = 70` under both Rev A and Rev B detection (`2026-09-12/debug_260912-153807.log:467`).
> The rename of `gapInMS` (it holds nanoseconds) is still owed.

> **Fixed in tree 2026-09-13 («#3533»):** `gapInMS` renamed to `gapInNs` throughout
> `src/isp_bldc_motor.spin2` (it is a PRI-local variable, never PASM-addressed, so the rename is
> pure text substitution -- confirmed by reading `init()`'s parameter list and both use sites
> before renaming). This is a static/compile-only property; the build and style gates cover it.
> No other `src/*.spin2` file names it.

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

**Fixed in tree 2026-09-14 («#3507»); certification is owed to Visit 2.** Design:
`plans/DEBUG-CHANNELS-DESIGN.md`.
- **The decision was taken the plan's way (§2):** compile-time DEBUG channels, not a runtime flag.
- **Every call is on a channel.** All 75 `debug()` statements in `isp_bldc_motor.spin2` and all 38
  in `isp_steering_2wheel.spin2` name one of ten channels (ERROR … HDMI_DUMP).
- **Where the masks live.** `MOTOR_DBG_MASK` and `STEER_DBG_MASK` are in the user config, outside the
  six config blocks, and the bench config mirrors them.
- **`useDebug` is deleted,** together with the equally dead `showHDMIDebug`.
- **Defaults reproduce today's output.** HDMI_DUMP is off; its lines never printed.
- **MEASURED:** with both masks at 0 the steering object's build shrinks from 24,477 to 20,262 bytes,
  and `debug[32]` fails with the documented error.
- **Still open:** a bench binary that needs quiet timed sections sets its own masks («#3508»).

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
  binary's deliverable is an uncorruptible log.
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
build job, and it must not ride on the critical path of a measurement session.

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
harness) will be the third**, which is where it clearly pays. *(2026-09-12: the offset scan
`test_bench_scan.spin2` («#3520») became the third consumer first. It copies the builder
byte-identical rather than extracting, because extracting would edit `test_bench_detect`, whose
log Bench Pass 2b diffs against Pass 1, and `test_bench_char` while «#3521» rewrites it. So
«#3508» extracts from three identical copies.)* Extracting now would
decertify two binaries that are verified and queued for Bench Pass 1, which the
sprint's standing rule exists to prevent. Do it as part of «#3508», not before.

⚠ Until then the two copies must not drift: the grouping behaviour is what makes
`sum`/`dwell_s` and every other numeric field parseable by the same analyser.

**Progress 2026-09-14 («#3508»):** the builder is extracted as `src/isp_bench_log.spin2`, with `src/test_bench_dual.spin2` its only consumer; adopting it in the scan, char and detection binaries is PL-53.

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

### PL-19 -- `test_bench_char.spin2` drives the right wheel in motor frame, but captions it in robot frame

**Found 2026-09-12 in Bench Pass 1 step 4, by Stephen at the bench** -- the right wheel turned
opposite to the plan on all four RIGHT holds (his meter sheet marks them `REV???` / `FWD???`).

`test_bench_spin.spin2:77-79` calls `wheelR.forwardIsReverse()`, because the two motors face
opposite directions on the chassis. `test_bench_char.spin2` `ensureSide()` (:604-609) starts
`wheelR` without it, so "RIGHT WHEEL FORWARD" commands a positive increment, which on the
right motor is robot-reverse. The correction was made to the spin binary at 23:40 on
2026-09-11 and never searched into its sibling -- a doctrine-overlay P8 miss.

**The data is valid.** `BC-HOLD` logs the signed `cmd_incre`, so every hold is attributable,
and motor frame is the frame that exposed the forward/reverse current asymmetry
([evaluation](analyses/bench/2026-09-12/CHAR-RUN-EVALUATION.md)).

**Fix (my call, per P3):** keep characterisation in motor frame -- it is a per-motor
measurement -- and make the frame explicit: captions name both frames (e.g. *RIGHT MOTOR +
INCREMENT (robot reverse)*), and `BC-HOLD` gains a `robot_dir` field. The captions are bitmaps,
so regenerate with `tools/gen_bench_char_assets.py`. Check `test_bench_t0.spin2` and
`test_bench_detect.spin2` for the same class in the same change.

### PL-20 -- `BC-SENSE` `i_mV_avg` overflows a long at the pre-S-3 scale

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

### PL-22 -- the two-wheel sync release is built from `start()`'s return, whose contract «#3499» changed

*(Corrected 2026-09-14: this entry said `start()` "was always 0" on success, so 5.0.2's steering
object "cannot start its motors". Its only measurement was a trapped capture, which always reads 0
-- PL-44. The 5.0.2 behaviour below is re-derived from the 2026-09-09 audit and the field report.)*

**Found 2026-09-12 while verifying «#3499».** `isp_steering_2wheel.spin2:110-118` starts both
motors with `startEx(..., sync: true)` -- each driver cog parks on `waitatn` -- then releases
them with a `cogatn` mask built from `startEx()`'s returns, `ltcog`/`rtcog`.

**What 5.0.2 did (DERIVED, `analyses/DRIVER-AUDIT-2026-09-09.md`, read from source before any
bench run):**
- Finding C: `ok := motorCog := coginit(NEWCOG, @driver, @pinbase) + 1` returned cog id + 1 on
  success and 0 on failure, while its doc comment promised the cog id or -1.
- So the mask `(1<<(ltcog-1))|(1<<(rtcog-1))` was `1<<cog` for each motor on success and released
  both. The audit records the two-motor sync handshake as correct (finding AH; "What is verifiably
  correct").
- The real 5.0.2 defect was finding AD: a **failed** start returned 0, the shift count became -1,
  and the surviving motor was never released, with no diagnostic.
- The field report agrees (DERIVED, `analyses/user-report-2026-09-09-ANALYSIS.md` observations 1
  and 4): the reporter's `demo_dual_motor` starts both motors through the steering object, and
  both motors drove. That is impossible if the mask selected no cog.

**What this entry got wrong.** It read `T0-10,start_return,0,raw_motor_cog,2`
(`analyses/bench/2026-09-11/debug_260911-143911.log:127`) as the return on success; that value is a
trapped capture, void as evidence (PL-44). Its supporting argument -- the chained assignment "does
not propagate" because `p2kbSpin2Operators` documents no assignment-as-expression -- was an
argument from absence, and the field report contradicts it.

**After «#3499»** `startEx()` returns the cog id (0-7), or -1 on failure (`isp_bldc_motor.spin2:116`).
`start()` now builds the mask as `(1<<ltcog)|(1<<rtcog)` (`isp_steering_2wheel.spin2:132`), so it is
correct by construction. *(Corrected 2026-09-13: this line said "cog id + 1", which was the draft
contract before Stephen's option B.)*

**Release note for «#3515» -- a contract change, not the fix of an always-0 return.** «#3499»
changed the success return from cog id + 1 to the documented cog id (0-7), and the failure return
from 0 to -1 (STEPHEN 2026-09-12 chose that contract, option B). That repairs finding C and AD's
unchecked failure. For a 5.0.2 caller it is a user-visible change: code that subtracts 1 from the
return, or tests it against 0 for failure, must change (DERIVED).

**Visit 1 ran the fixed path (MEASURED, `analyses/bench/2026-09-14/debug_260914-115953.log:402-420`):**
`sendatn: ltcog = 2 rtcog = 3`, then both wheels reached AT_SPEED and moved 13 ticks each. Cell
`R10-CHAR-STEERLIVE` signed off. It is coverage of the fixed path, not a falsifier of a 5.0.2
defect: 5.0.2's wheels would also have moved (DERIVED).

**Failed-start return — fixed in tree** (found 2026-09-13 while reviewing the «#3537» design; read
from source). This entry used to say *"`start()` here returns only the sense cog's result,
discarding a failed motor start"*. That is no longer true:
- A failed motor start stops whichever motor did start and returns -1
  (`isp_steering_2wheel.spin2:120-129`).
- A failed sense-cog start stops both motors and returns -1 (`:152-158`).

Visit 1 (2026-09-14): `R10-CHAR-STEERSTART` signed off. `R10-CHAR-STEERFAIL` FAILed only because
its return was read through an abort trap (PL-44). The library printed its −1 path, and free cogs
after the failed start equalled the baseline (`analyses/bench/2026-09-14/debug_260914-115953.log:268-281`,
`:420`). The return is re-measured at Visit 2, after the capture fix.

### PL-23 -- bench binaries print booleans as numbers

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

### PL-24 -- a second `start()` on a running motor orphans the first driver cog

**Found 2026-09-12 by the «#3500» agent** (DERIVED from source, not observed on hardware).
`startEx()` in `src/isp_bldc_motor.spin2` launches a new driver cog without stopping one this
instance already runs. The first cog keeps driving the same pins with no handle left to stop
it, and since «#3500» `getBoardType()` then returns the revision recorded at the first start --
possibly for a different pin group. **Being fixed in «#3499»:** `startEx()` calls `stop()`
first whenever this instance already runs a driver or holds a pin claim, so the cog is freed,
the pins and claim are released, and the new start begins clean -- an orphaned cog can never
exist. STEPHEN 2026-09-12: *"why wouldn't a second start do a driver stop to free the cog then
start?"* The same stop-first removes the stale claim `validatePinBase()` could leave when a
restart names an illegal group.

### PL-25 -- a board reported as not detected makes every current reading negative

**Found 2026-09-12 by the «#3500» agent** (DERIVED from source). `REV_Unknown` leaves
`rSenseForBoard` at -1 (VALUE_NOT_SET), and `getCurrent()` and the telemetry path divide
`sense_i_mV` by it, so current and watts come out negative. This already applied to an empty
pin group; since «#3500» the overlapping-group case reports `REV_Unknown` too. **Fix
direction:** a not-detected board yields a stated "no measurement" value, not a sign-flipped
reading; decide alongside «#3503», which changes the same scale path.

### PL-26 -- the commutation scheme departs from the board designer's principles

**Raised 2026-09-12** from the board designer's notes, relayed by Stephen and recorded in
[`analyses/BLDC-COMMUTATION-PRINCIPLES.md`](analyses/BLDC-COMMUTATION-PRINCIPLES.md): drive at
±90° electrical from the rotor's position, with electrical angle known to 12 bits.

DERIVED from `src/isp_bldc_motor.spin2`: the field angle is commanded and corrected, not placed
from the rotor's position; the duty servo holds the field **60°** (`256/6`) from a hall
estimate, not 90° from the rotor; rotor angle is known to **6 positions** per electrical cycle,
not 4,096; and each per-direction offset mixes hall alignment with lead angle.

**Disposition needs Stephen** -- this is a change to what the driver *is*, not a defect fix.
The offset scan («#3520», Bench Pass 2a) comes first and supplies the evidence: the midpoint of
the two per-direction minima estimates the hall zero, and whether the minima draw equal current
tests whether alignment alone explains the asymmetry. The candidate changes (separate alignment
from lead; a 90° lead target; sub-sector rotor angle by edge-time interpolation or from the
phase voltages already sampled) are written up in that document.

**Top speed is part of this.** The source records each speed ceiling as a fault point, and
anything that wastes torque per amp at speed lowers it. DERIVED prediction: on the 6.5″ hub the
negative-increment direction faults at a lower speed than the positive one; no per-direction
ceiling has ever been measured. Bench Pass 3's C-1 speed ladder (T1-3) should run in **both**
directions, before and after the scanned offsets are applied.

**Visit 2 ladder (2026-09-15):** it ran in both directions on the default offsets. No rung up to 165M
faulted on either motor in either direction, so the predicted lower NEG ceiling did not appear
unloaded. Above 100M the duty pins and current collapses while speed tracks — see PL-61.

### PL-27 -- the Doco motor's offset and speed-ceiling tables were characterised while board detection was broken

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

### PL-28 -- the test fault-recovery path cannot clear a fault on its own

**Found 2026-09-12 by the «#3520» design agent** (DERIVED from `src/isp_bldc_motor.spin2`, not
observed on hardware). Three related defects in the TEST-USE ONLY drive path:

1. **`testResetFault()` waits for a stop that never comes.** It clears the hub `fault` long and
   then waits for `isStopped()`, but the driver leaves `DCS_FAULTED` only when a *changed* command
   arrives. With the increment unchanged, the wait always runs to its timeout.
   `util_char_motor.spin2` escaped this only because its sense task's `stopAfterTime` zeroed the
   command. The offset scan works around it by sending a zero command before resetting.
2. **`stop()` leaves `drv_state` stale**, so `isReady()` / `isStopped()` still answer on a stopped
   instance -- the same mechanism behind PL-21's frozen telemetry. Callers must test
   `testGetMotorCog() <> 0` to know a cog is running.
3. **`util_char_motor.spin2` `clearFaultByMotMove()`** "pops" the saved offset into its local
   variables but never re-applies it to the driver, so a jog-recovered sweep continues on the jog
   offset.

**Fix direction:** `testResetFault()` issues the zero command itself; `stop()` sets `drv_state` to
a stated not-running value; the jog recovery re-applies the saved offsets. Worth doing before the
motion harness («#3508») reuses this path.

**Fixed in tree 2026-09-13 («#3533»):** `testResetFault()` now calls `setTargetAccel(0, false)`
before clearing the hub fault long and waiting, so the driver's `.newRqst` fault-clear path always
runs on its next pass instead of depending on the caller having sent zero first. `stop()` now sets
`drv_state := DCS_Unknown` (the same value `init()` gives a never-started instance) once its driver
cog is stopped, so `isReady()` and `isStopped()` both answer FALSE on a stopped instance instead of
echoing whatever the driver last reported. `util_char_motor.spin2`'s `clearFaultByMotMove()` now
re-applies the popped offset with `testSetFwdRevOffsets()` after the jog, instead of only restoring
its local copies. Run-time proof (fault clears within the stated bound; `isReady()`/`isStopped()`
FALSE post-stop) is owed to Visit 1.

### PL-29 -- a `? :` whose branches call methods ran both calls

**Found 2026-09-12 in the first Bench Pass 2a scan runs.** MEASURED:
`analyses/bench/2026-09-12/debug_260912-205538.log:39-40` and `-205612.log:39-40` each print
`getBoardType() pinbase: ** NOT SET **` then `getBoardType() driver running ... 22`. The scan has
one call site, `test_bench_scan.spin2` `sideBoardType()`:
`(side == SIDE_RIGHT) ? wheelR.getBoardType() : wheelL.getBoardType()`, called with side LEFT.
`wheelR` was never started (the NOT SET branch) and `wheelL` was running (the driver-running
branch), so both method bodies ran for one evaluation. The only other `getBoardType()` call, inside
`startEx()`, printed earlier (line 27).

**Not yet shown at compiler level.** The `pnut-ts -l` listing is a symbol table without readable
bytecode, so whether `? :` compiles as evaluate-both-then-select or as a branch is unconfirmed.
That is a `pnut-ts` question for Stephen, and the Spin2 language reference
(`p2kbSpin2OpOpTernary`) does not state which is intended.

**No harm today.** Every scan ternary that calls a wheel method (`isReady`, `isStopped`,
`isFaultSignal`, `getDriverState`, `getRawHallTicks`, `getBoardType`) only reads status, and every
motor command in the scan goes through `if`/`else`. **The hazard is the class:** a `? :` whose
branches have side effects acts on both, e.g. commanding both wheels. **Fix direction:** side
selection that calls methods uses `if`/`else`; a ternary selects values only.

### PL-30 -- the right board's current sense reads +73 mV at zero command, and Pass 1 did not

> **CAUSE FOUND 2026-09-13 in scan run 5 — see PL-32.** The 72–75 mV is not a board offset.
> After a driver restart the right motor's zero fell to 12.6 mV and then 12.1 mV, and the left
> motor's zero moved as well (MEASURED). Each driver start recalibrates the ADCs from one
> settling sample (DERIVED from source). The hypotheses below were written before this and are
> kept as history.

**Found 2026-09-12 in Bench Pass 2a scan run 3** (MEASURED,
`analyses/bench/2026-09-12/SCAN-RUN-3-EVALUATION.md` §6). The right motor's `BS-ZERO` read
73.4 mV (range 71–76) with its driver running at zero command; the left read 7.0 mV. The right
¼-speed points read 161.2 / 237.3 mV against Pass 1's 91.6 / 168.2. With the zero subtracted they
match Pass 1 within 6 %, and duty matches the left. So the right channel gained a constant
~0.45 A-equivalent offset since Pass 1, while the left is unchanged through the same source
changes.

**Two explanations, told apart only at the rig:** a sense-path offset on the right board
(ground or connector shift, or the amplifier), or a real ~0.45 A idle draw in the right bridge
(≈ 8 W, which would warm it). Raised with Stephen as a hardware confirm question.
STEPHEN 2026-09-13: *"no idea about the board. but the bench stand might be interferring...i'm
reseating it"*. That adds a third explanation, a mechanical one (DERIVED). A stand pressing on
the right wheel adds a roughly constant friction torque in motion, which shows as a constant
extra current in both directions, as measured. At zero command it would show only if the stand
pushes the held wheel to turn. The next scan's right-motor zero, taken after the reseat, is the
check.

**Scan run 4, after the reseat (MEASURED, `analyses/bench/2026-09-13/SCAN-RUN-4-EVALUATION.md`
§5):** the right zero read 72.1 / 72.6 / 71.4 mV, unchanged. Net of it, the ¼-speed currents
are 91.1 / 168.8 mV, matching the left motor within 10 % and Pass 1. DERIVED: a mechanical cause
is effectively excluded, because the reading is taken with the wheel stopped and the reseat did
not move it.

**Resolved from source, 2026-09-13 (DERIVED): it is a sense-path offset.**
- Every zero was already read with the drive floated: `isp_bldc_motor.spin2` `init()` sets
  `stop_mode := SM_FLOAT`, the scan never changes it, and `.checkstop` disables PWM at zero command
  in that mode.
- No bridge current can flow during the reading, so the idle-current explanation is excluded.

**Still open:**
1. Why the right board's sense path gained ~64 mV since Pass 1. This is a hardware finding for
   Stephen to look at when convenient, not a blocker. STEPHEN 2026-09-13: *"no idea about the
   board"*.

**Root-cause status, 2026-09-13 (DERIVED unless marked):**

Excluded:
- *Bridge current:* every zero is read floated.
- *Stand drag:* the reading is taken with the wheel stopped, and the reseat did not move it (MEASURED).
- *Scan/driver code:* the driver code is identical for both pin groups, and GIO/VIO calibration is per pin. The only arithmetic change since Pass 1 is the S-3 scale shift, which cannot add a constant to one board. The left board is unchanged (MEASURED).

Also:
- The sense node's discharge on the right board is normal: detection high time is 72–73 µs, against the left's 71–74 µs (MEASURED, run 4 detection lines). So the amplifier still drives it.
- The offset is new since 2026-09-12 15:44. Pass 1's single fit over both motors has a worst residual of 4.7 mV, which a 64 mV right-motor offset would have broken.

Remaining:
1. A ground or reference shift between the right board and the P2, such as connector or ribbon contact resistance. This would also shift the U/V/W phase-voltage channels.
2. A change in the current-sense path itself, such as amplifier offset or the shunt's Kelvin connection. This would shift only the current channel.

Scan v3.1 logs the phase-channel means with every zero, so run 5 separates the two.

**Instrument response (scan v3.1, «#3527»):** the self-check now judges zero *health* (not frozen,
small spread, below an absolute ceiling) and net-of-zero currents. A working channel that is
merely offset passes; a dead or railed one still fails. This is instrument design and the
arbiter's to decide (doctrine overlay P3), so the right motor is scanned in the same run as the
left. The scan's
zero band stopped the run correctly and is not loosened. Tier 0's T0-11 (quiescent sense
including the phase-voltage channels, «#3504») would separate a ground shift, which moves every
channel, from a current, which moves only the current channel.

### PL-31 -- the offset scan finds the no-load minimum but not the fault cliff beside it

**Found 2026-09-12 in scan run 3** (DERIVED from MEASURED, evaluation §4, §5, §8). On the left
motor every minimum-current offset sits within 10° of an offset that faults, measured with the
wheels unloaded:
- positive ¼: minimum −21°, fault by −8°;
- positive ½: still falling at −11°, fault at −6°;
- negative ¼: still falling at +13°, fault at +3°, so the minimum is not bracketed.

A no-load minimum therefore cannot be shipped as the offset without a margin measured under
load.

**Scan changes:**
1. fine-walk (5°) into a fault edge before declaring `EDGE_FAULT`;
2. report the cliff location and the minimum-to-cliff margin per leg;
3. re-measure the zero at every reference point, because a ~13–16 mV sense-side bias appeared
   after some high-current or fault events (coarse points read higher than fine points at the
   same offset, with the same duty).

**Scan v2 (`5ea0510`) in run 4 (MEASURED, `analyses/bench/2026-09-13/SCAN-RUN-4-EVALUATION.md`):**
- Both left cliffs were located: negative edge 5.5°, positive −15.5°, each 7.5° from its lowest
  point.
- The bias is a zero shift: references of 89.3 and 100.4 mV sat on zeros of 7.7 and 18.9, giving
  identical net readings of 81.6 and 81.5. The 18.9 zero was read 1.5 s after an `ABORT_I` restart.
- Remaining defect: `evaluateBracket` never brackets a side whose walk stopped on faults, even
  when the cliff probe rises above the low. Both legs therefore reported NOT_BRACKETED, neither
  fitted, and both ½-speed legs were skipped.

Scan v3 fixes it by ending the sweep window at the last good point, and reads the zero before
every point, including after every restart.

### PL-32 -- the driver calibrates its ADCs once, at start, from a single settling sample

**Found 2026-09-13 in Bench Pass 2a scan run 5.** This is the cause of PL-30's right-board
offset and PL-31's zero shifts.

**What was measured** (`analyses/bench/2026-09-13/debug_260913-120844.log`, `BS-ZERO` records).
Within one driver cog's lifetime the zeros are steady. At every `stop()`/`start()` each channel
takes a new value, independently of the others:

| Motor | Driver start | i | u | v | w |
|---|---|---|---|---|---|
| LEFT | 1st | 8.6 | 0.7 | 6.3 | 6.8 |
| LEFT | 2nd | 5.2 | 0.0 | 18.0 | 4.7 |
| LEFT | 3rd | 19.8 | -0.2 | 4.7 | 5.2 |
| RIGHT | 1st | 74.9 | 88.2 | 69.3 | -0.9 |
| RIGHT | 2nd | 12.6 | 17.6 | 0.7 | 1.4 |
| RIGHT | 3rd | 12.1 | 3.6 | 1.5 | 0.4 |

All values are mV. The "starts" are the ones logged within run 5.

**Mechanism, read from source:**
- `src/isp_bldc_motor.spin2:2065-2104` switches the ADC pins to GIO, raises DIR, and reads one
  frame. It then switches to VIO, raises DIR again, and reads one more frame. It computes
  `gio_levels` and `scl_levels` from those two samples and never revisits them.
- The control loop (`:2432-2452`) subtracts that frozen `gio_levels` every cycle.
- Chip's reference driver (`BLDC_Motor_Driver-REF.spin2:132-205`, repo root, read-only) instead
  cycles pin → GIO → VIO inside the loop, so it recalibrates on every pass.
- `p2kbAppNoteP2an001SinglePinInstrumentationAdc` `source_switch_flush`: *"discard 3 samples
  after each source switch (2 SINC2 + 1 front-end), then sum 8 clean"*.

**What that means (DERIVED):**
- The driver keeps exactly the sample the application note says to discard, and keeps it for
  the cog's lifetime.
- At `adc_fram` 6136 one count is about 0.54 mV (3300/6136). So PL-30's ~65 mV is a ~120-count
  error in one calibration sample. This is arithmetic from the constants, not a measurement.
  The ADC mode here is not SINC2, so the note's front-end-settling sample is the part that
  applies.

**User-visible consequence (DERIVED):**
- `getCurrent()` carries a per-start offset. Run 5 measured offsets up to 75 mV, about
  **0.5 A** at 150 mV/A, and the value changes every time the motor is started.
- The phase-voltage readings carry the same kind of offset.
- A future current limiter (S-2 / C-5) would inherit it.
- Every earlier on-board current reading in this sprint sits on an unknown per-start zero. The
  scans' net-of-zero figures are unaffected, because they subtract a zero read in the same
  driver lifetime.

**Fix direction:**
- Calibrate from settled, averaged samples: flush after each source switch, then sum several
  frames, as P2AN001 does. That leaves the control loop untouched.
- Whether to also recalibrate periodically, as the reference driver does, is a separate trade
  against control-loop cadence, and is decided with the fix.
- Run-time proof: repeated `stop()`/`start()` cycles show zeros that stay within a few mV of
  each other on every channel.

**Fixed in tree 2026-09-13 («#3529»):** the GIO/VIO calibration in `isp_bldc_motor.spin2`'s start
sequence now discards one settling read and keeps one averaged read, per level, where each read's
ADC count period is temporarily widened to 8 normal frames (`ADC_CAL_AVG_FRAMES`) so the hardware
sums 8 clean frames in silicon and the kept read is shifted right by 3 to renormalize -- a software
per-frame summing loop did not fit the driver's `fit 496` cog-RAM budget (baseline usage 476 longs,
~20 longs of headroom). Run-time proof owed to Visit 1 and Visit 2.

### PL-33 -- the steering object reads the user config even under `-D BENCH_CFG`

**Found 2026-09-13** by the «#3537» design agent. Confirmed by reading.

**The mismatch:**
- `src/isp_bldc_motor.spin2:61-65` selects its `user` object with `#ifdef BENCH_CFG`: the bench
  config under `-D BENCH_CFG`, otherwise the user config.
- `src/isp_steering_2wheel.spin2:90` declares `user : "isp_bldc_motor_userconfig"` with no switch.

So in a bench build the steering object reads the **user** config while its two wheels read the
**bench** config.

**Consequence (DERIVED):**
- `start()` takes `WHEEL_DIA_IN_INCH` from the user config to compute `tickInMM_x10` (`:138-140`).
  Distance conversions in a bench build therefore follow whatever wheel the active user-config
  block declares, not the bench rig's.
- Pin bases, voltage and detect mode are passed in as arguments, so starting the motors is not
  affected.
- The steering liveness cell judges hall ticks, not distance, so Visit 1's verdict is not affected.

**Fix direction:** give the steering object the same `#ifdef BENCH_CFG` OBJ switch as the motor
object. A candidate for «#3533»'s batch.

**Fixed in tree 2026-09-13 («#3533»):** `isp_steering_2wheel.spin2`'s `user` OBJ now carries the
same `#ifdef BENCH_CFG` / `#else` / `#endif` switch as `isp_bldc_motor.spin2`. Confirmed no top
compiles the steering object under `-D BENCH_CFG` today -- `tools/bench-run.sh` and every
`test_bench_*.spin2` OBJ block name `isp_bldc_motor` directly, never `isp_steering_2wheel` -- so
this closes the gap before the motion harness needs it rather than fixing an observed failure.
Run-time proof (a bench build of a steering-object consumer reads bench-config distances) is owed
to Visit 1 if and when such a consumer exists.

### PL-34 -- per-point `BS-ZERO` records print the motor block's zero-health verdict as their own

**Found 2026-09-13** by the «#3537» design agent. Confirmed against the source.

**The mislabel:**
- `measureZero()` passes `bZeroOk[slotIdx]` to `emitZero()` for every phase
  (`src/test_bench_scan.spin2:1157`).
- `bZeroOk` is set only when `phaseTag == PH_ZERO_INIT` (`:1148-1155`).

So every per-point `BS-ZERO` (phases REF_START, COARSE, FINE, CLIFF and so on) prints
`health_ok` from the motor block's first zero, under a field that reads as its own reading's
health. The project's record rule forbids that.

**Scope:** informational only. No scan judgement reads `health_ok` from a per-point zero; the
self-check uses `bZeroOk` directly. Run 5's evaluation did not rely on it.

**Fix:** scheduled in «#3537» phase 2 (`DOCs/plans/VISIT-SIGNOFF-DESIGN.md` §F.6). `health_ok`
prints `NA` for every phase except `ZERO_INIT`, at FMT 7.

**Fixed in tree 2026-09-14 (commit `b300660`, scan FMT 7):** `health_ok` prints `NA` for every
phase except `ZERO_INIT`. It is a record-label fix with no sign-off cell; the Visit 1 scan log
shows it.

### PL-35 -- the detection binary's safety notes describe the pin map from before the boards were measured

**Found 2026-09-13** while answering whether Visit 1's detection re-run needs the motors
unplugged. Read from `src/test_bench_detect.spin2` and its 2026-09-11 log.

**The binary still describes the rig as it was believed to be before 2026-09-11** (left board at
P0, right at P16). The boards were measured at LEFT P32 / RIGHT P16, and the bench config was
corrected in `fe83cb0`. The binary itself was not:
- The note (log `debug_260911-210229.log:51`) says the tail groups' sense pins are P12 and P28,
  "the LEFT and RIGHT boards' W low-side gate inputs".
  - P12 now sits on no board.
  - P28 is the RIGHT board's `pin_pwm_w_l`.
- **P44 is `PINS_P40_P55`'s sense pin, and it is the LEFT board's `pin_pwm_w_l` (32 + 12).**
  - The note at log `:55` and the CON comment at `:158-160` still say nothing is connected there.
    The newer comment at `:161-168` already knows, which is why the calibration pin moved to P15.
  - `P40_P55` is **not** a tail group, so `-D DETECT_NO_TAIL`, described as the rail-on-safe
    build, still pulses the LEFT board's gate input.
  - The rail is always on at this bench: the P2 runs from the pack.
- The overlap token strings are `"P0_P15+12_PWM_W_L"` / `"P16_P31+12_PWM_W_L"` (`:324-325`).
  Whether `overlapToken()` classifies from the configured bases is still to be confirmed.
- The group comments at `:108-113` name P0_P15 as the left board and P32_P47 as unpopulated.

**Consequence (DERIVED):** every sweep of today's binary pulses both boards' W low-side gate
inputs for about 1 ms, 32 times per cell, with the rail live. With the motors unplugged, as the
phase-2 precondition requires, there is no current path through a winding. With motors connected,
the effect depends on the gate driver's undriven-input behaviour, which is not in
`BOARD-REVISION-FACTS.md`.

**Fix:** «#3537» phase 2 (`DOCs/plans/VISIT-SIGNOFF-DESIGN.md` §C.3).
- The sweep skips any group whose sense pin lands on a configured board's pin, computed from the
  configured bases.
- Phase 2 refuses a driver cog whose pins overlap another board.
- The notes and tokens are corrected.
- The detect-phase2 precondition in `tools/bench-run.sh` changes in the same commit.

**Fixed in tree 2026-09-14 («#3537» P2d; `test_bench_detect.spin2` SRC_REV 3, FMT 2):**
- **Skipped groups.** `isGateOverlap()` computes, from `user.LEFT_MOTOR_BASE` / `RIGHT_MOTOR_BASE`
  in every sweep of every build, whether a group's sense pin lands on a board's pin other than
  that board's own sense pin.
  - On the bench bases it skips NO_USE_P24_P39 (P28) and P40_P55 (P44).
  - A skipped cell emits `BD-SKIPPED GATE_OVERLAP`, no `BD-REP`, and no library probe.
- **Refused driver cogs.** Phase 2 refuses a driver cog that overlaps another board
  (`COG_OVERLAP`). Neither phase-2 group does today.
- **Stale text corrected:**
  - the notes;
  - the overlap tokens (now `LEFT+12_PWM_W_L` / `RIGHT+12_PWM_W_L`);
  - the `DETECT_NO_TAIL` description, which now says it is not a safety build;
  - the group comments;
  - the header precondition, together with `tools/bench-run.sh`'s detect-phase2 precondition.
- **Not a pulse.** `clearSweptGroups()` still pinclears those groups. `PINCLEAR` sets DIR and the
  mode to 0 (`p2kbSpin2Pinclear`), so the pin is only released.
- **Proof owed to Visit 1:** cells `R2-DETECT-GUARD` and `R2-HOST-DETDIFF`. The overlap cells
  themselves are deferred to `R2-DETECT-OVERLAP`, owed to the first motors-unplugged session.

### PL-36 -- a failed `start()` kept its pin-range claim with no cog behind it

**Found 2026-09-14** by the «#3521» phase D agent. Confirmed by reading the source.

**The leak:**
- `startEx()` calls `init()`, which takes the instance's pin-range claim.
- On a failed `coginit` (`src/isp_bldc_motor.spin2` `startEx()` failure branch), it set
  `motorCog := 0` and returned -1 without releasing that claim.
- The two-wheel `start()` stops only a motor whose start succeeded
  (`src/isp_steering_2wheel.spin2` ~:124-133). Its failed wheel therefore kept the claim.

**Consequence:**
- Every OTHER instance was refused that pin group until the failed instance was `stop()`ped.
- The failed instance itself recovers on its next `startEx()`, which calls `stop()` first when it
  holds a claim.
- It is an invalid state: a claim with no running cog.

**Fixed in tree 2026-09-14.** The failure branch now calls `stop()`, which releases the claim and
clears the pins; with `motorCog` already 0 it stops no cog.

**Run-time proof owed to Visit 1:** `R10-CHAR-STEERFAIL` requires this file's own wheels to start
on the bench bases right after the failed two-wheel start.

**Certified at Visit 2 (2026-09-15):** `R10-CHAR-STEERFAIL` PASS. The failed steering start returned
−1 with 6 free cogs before and after, and the file's own wheels then started and moved 13 ticks
(`analyses/bench/2026-09-15/debug_260915-140100.log:354`).

### PL-37 -- the meter-panel assets outlived the panel they drew

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

### PL-38 -- the 6.5″ motor's 6.0 V and 7.4 V speed ceilings are the 11.1 V ceiling

**Found 2026-09-14** while checking `MOTOR_CHOICE.md` against the bench runs. Read from source.

**What the code does:**
- `confgurePowerLimits()`, `MOTR_6_5_INCH` branch (`src/isp_bldc_motor.spin2:1411-1419`), maps the
  range `PWR_6p0V..PWR_11p1V` to one ceiling. By the enum at `:29` that range is 6.0, 7.4 and
  11.1 V.
- All three get `90_000_000` / `-90_000_000`, which the comment at `:1412` records as the 11.1 V
  ceiling: 165.3 rpm, 248 ticks/s.
- 24.0 V gets the 22.2 V value, `172_000_000`, and the comment at `:1417` calls it `FAKE`.

**What the doc says:** `MOTOR_CHOICE.md` lists 6.0 V, 7.4 V and 24.0 V as *tba*. So the doc says
"not known" where the code has committed a value.

**Consequence (DERIVED, not bench-tested):**
- The measured rows scale at about 15 rpm per volt: 165.3 / 11.1 = 14.9, 181.3 / 12.0 = 15.1,
  224.0 / 14.8 = 15.1, 272.0 / 18.5 = 14.7, 320.0 / 22.2 = 14.4.
- On that slope a 6.0 V pack reaches about 90 rpm and 7.4 V about 110 rpm, while 100 % power
  requests 165.3 rpm.
- The table's own comments record a request above the reachable rate as the fault point ("until
  fault at"). So full power on a 2S pack or a 6 V supply is expected to fault.
- 24.0 V errs the other way. It under-limits by one voltage step, which costs top speed and does
  not fault.

**Fix direction:**
- Measure the 6.0, 7.4 and 24.0 V ceilings. Per PL-26 that means both directions, on the offsets
  that ship. This needs a supply or pack at each voltage, and that is Stephen's rig.
- Until they are measured, a placeholder must err low. Scale it from the measured slope rather
  than reuse a higher voltage's ceiling.
- `MOTOR_CHOICE.md` then states what the code does.

### PL-39 -- `MOTOR_CHOICE.md` labels the 6.5″ hall sequences opposite to the library's forward

**Found 2026-09-14** while checking `MOTOR_CHOICE.md` against the bench runs.

**The evidence:**
- `deltas65` (`src/isp_bldc_motor.spin2:1885-1892`, indexed `old<<3 | new`) adds +1 to `pos` along
  1-5-4-6-2-3 and −1 along 1-3-2-6-4-5. DERIVED, decoded by hand.
- A positive command raises `pos` on a wheel that does not call `forwardIsReverse()`. MEASURED:
  LEFT at +50 power moved +416 ticks, and at −50 moved −416
  (`analyses/bench/2026-09-11/debug_260911-234012.log:49`, `:65`).
- The driver's own table selection agrees. A rising `angle_` selects `offset_rev_` and the first
  half of `hall_angles`, copied from `hltbAngles`, whose rising order is 1-5-4-6-2-3. DERIVED,
  `:2524-2534` and `:1904-1911`.

**The mislabel:**
- `MOTOR_CHOICE.md:18` labels 1-3-2-6-4-5 "FWD (CW)" and 1-5-4-6-2-3 "REV (CCW)".
- So the doc's **REV** is the sequence the library drives for **positive** power. The label
  follows the naming inherited from Chip's driver, in which `offset_fwd` serves negative
  increments (`analyses/bench/2026-09-12/CHAR-RUN-EVALUATION.md` finding 1). It does not follow the
  library's public API.
- `MOTOR_CHOICE.md:26` labels the Doco motor the other way round (FWD = 1-5-4-6-2-3), yet
  `deltas4k` is byte-identical to `deltas65`. Either one row is wrong or the two motors' hall
  wiring differs. Nothing in the repo shows which.
- CW and CCW are given without a viewpoint, and no bench record ties a hall sequence to a
  rotation seen from a stated side.

**Fix direction:**
- Label each sequence in the library's frame: "positive power, ticks rising" and "negative power,
  ticks falling". Give CW/CCW only with a stated viewpoint, and only once observed.
- T0-12, the hand-rotation test, is the natural place to observe it: record which way the wheel
  was turned, seen from the hub side, alongside the sign of the tick change.
- Resolve the Doco row by the same observation when the Doco bench runs.
- Check whether `ADDING_MOTOR.md`'s procedure for building a deltas table reads these labels.
  That was not checked here.

**Direction settled for the 6.5″ motor at Visit 2 (2026-09-15, `analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §2):**
- MEASURED: T0-12 told the operator to turn the RIGHT wheel (P16) clockwise seen from the hub. It counted
  270 transitions, 0 illegal, ending at `pos` −270 (`debug_260915-142347.log:394`, `:531`). T0 does not call
  `forwardIsReverse()`, so this is the motor frame.
- DERIVED: clockwise from the hub is 1-3-2-6-4-5, which counts negative. `MOTOR_CHOICE.md:18`'s "CW" is right
  seen from the hub; its "FWD" is the library's negative direction.
- Still open: relabel the doc in the library's frame (with «#3515»), the Doco row, and the `ADDING_MOTOR.md` check.

### PL-40 -- the sign-off collation missed a verdict printed inside a corrupted log line

**Found 2026-09-14 evaluating Visit 1** (`analyses/bench/2026-09-14/VISIT-1-RESULTS.md`).

**What happened (MEASURED):**
- Tier 0 printed `SIGNOFF,...,cell,R1-T0-RESTART,...,measured,TRUE,...,verdict,PASS`.
- The terminal logged it on the tail of a hex-dump line that followed a
  `[ROUTING ERROR: Binary data in COG message]` block (`debug_260914-114636.log:994-1002`; the
  record starts after the dump's closing `|` on line 1002).
- `tools/signoff-collate.py` reported the cell NOMEAS (NOT_REACHED): declared, no SIGNOFF instance
  (`VISIT-1-SIGNOFF.md`, R1-T0-RESTART).

**Why it matters:** a verdict the binary did print was scored as never reached. The sheet's rule
that NOMEAS is never PASS held, so nothing was falsely signed off. But a real verdict was lost
without a word, and the corruption that causes it recurs (PL-41).

**Fix direction:**
- The collation finds a record token anywhere in a line, not only at the line's start.
- A record recovered from a routing-error or binary-data line is counted, and flagged on the sheet
  as recovered from a corrupted line.
- A fixture built from these exact lines proves both, and a record truncated inside the dump
  still reads as malformed.

**Fixed in tree 2026-09-14 («#3541»).** In `tools/signoff-collate.py`, `scan_line()` finds a record
token anywhere in a line, with two rules:
- **Never inside a hex dump's 16-character ASCII gutter.** On a dump row, only the text after the
  gutter is searched.
- **A message whose end is not observed on its line is never counted.** A SIGNOFF or SIGNOFF-DECL
  cut that way is MALFORMED; any other message is not read.

Recovered records are flagged in their proving lines and listed in a new sheet section.

**Selftest: 23 of 23**, including four new checks:
- (t) a SIGNOFF recovered after a dump;
- (u) a record cut across a dump, which is MALFORMED;
- (v) line-start parsing identical to the old reader over 13 logs;
- (w) SIGNOFF text inside a gutter, which is never a record.

**Visit 1 re-collated** with the same seven logs. The only change is R1-T0-RESTART, NOMEAS →
**PASS**, recovered from `debug_260914-114636.log:1002`; its manifest status went OWED → SIGNED_OFF.

### PL-41 -- the debug stream corrupts when bench binaries start and stop cogs in quick succession

**Found 2026-09-14 in Visit 1.** Every instance sits in a phase that starts or stops several cogs
within milliseconds.

**Instances (MEASURED):**

| Log line | What the log shows | What the binary was doing |
|---|---|---|
| `debug_260914-114636.log:983` | `Cog1  IN` cut off, then `Cog0` text | T0-15c: a second `start()` stops cog 1 about 5 ms after starting it |
| `…114636.log:994-1002` | routing error, byte `$F9`, `Cog1Cog0` | T0-15c, same restart |
| `…114636.log:1041`, `:1059` | `Cog1Cog1`, `Cog1Cog0` | T0-15b: spacer cogs started, then the exhaustion start |
| `debug_260914-115953.log:250-254` | `Cog2  IN` + `$FF`, then a full `Cog2  INIT` | char STEERFAIL: five spacer cogs started |
| `…115953.log:282-364` | 1,296 bytes, alternate bytes `$4F` | STEERFAIL: the failed steering start and the spacers' release |
| `…115953.log:375-379` | `Cog3` + `$FF` + `Cog0` | steering start's second motor cog |
| `…115953.log:432-459` | 273 + 142 bytes, a `$07` after most bytes, some low bits set | brake-start phase: a wheel stopped and restarted |

**What it costs:** records are lost or unparseable (PL-40), and a log cannot be trusted to be
complete through such a phase.

**Mechanism: not established.** The pattern of a cog's `INIT` line cut short fits a cog stopped
while its debug output is still being sent (DERIVED). Whether stopping a cog mid-output can
also leave the debug channel held -- one candidate for scan runs 5 and 6 going silent -- is a
P2 debugger question, answered from the P2 knowledge base or by measurement, not guessed.

What the knowledge base says (read 2026-09-14):
- **DEBUG output from every cog is serialised by lock 15.**
  - `p2kbSpin2Debug`, on `DLY()`: it *"RELEASES LOCK[15] while it waits, so other cogs can emit
    DEBUG output"*.
  - `p2kbPasm2Locktry` and `p2kbPasm2Lockrel` cite `Spin2_debugger.spin2` using lock 15.
- **What happens to a stopped cog's lock is not settled.**
  - `p2kbSpin2Cogstop` says locks owned by a stopped cog are **not** released.
  - `p2kbPasm2Cogstop` is silent on locks.

**That conflicts with the logs** (DERIVED from MEASURED). Output carried straight on after a cog was
cut off mid-`INIT` line (`debug_260914-114636.log:983-1002`, `debug_260914-115953.log:250-254`).
Only a truncated line and a partial byte (`$F9`, `$FF`) were lost. That fits the lock being freed
when its holder stops, which is not what `p2kbSpin2Cogstop` says.

**Settled by Stephen, 2026-09-14:** *"cogstop clears the locks but if the stopped cog didn't rlease
them first they are leaked and those locks will never be reallocted"*.
- A stopped cog's **held** locks are cleared, so another cog can take lock 15, and DEBUG output
  resumes. That matches the logs.
- A lock the stopped cog allocated and never released or returned is **leaked**. It is never
  reallocated.

**Consequences (DERIVED):**
- **The corruption is a message cut off mid-byte** when its cog is stopped: a truncated line and a
  partial byte. It is not a jammed channel.
- **A held lock 15 cannot explain scan runs 5 and 6 going silent.** That candidate is removed from
  PL-43.
- **`p2kbSpin2Cogstop`'s "Locks owned by cog are NOT released" is incomplete.** It is filed as a
  knowledge-base note.

**Disposition:** design the pattern out, not characterise it (doctrine overlay P7). «#3543» adopts
cog-lifecycle rules:
- no stopping a cog that may be mid-DEBUG output;
- cooperative task shutdown, with a bounded forced-stop fallback;
- no cog thrashing in tests;
- any cog that takes or allocates a lock releases and returns it before it can be stopped.

No probe binary is built.

**Fix direction:** establish the mechanism first. Then decide whether the bench binaries must
not stop a cog until its debug output has drained, and whether the library's own restart path
(`startEx()` calling `stop()`) has the same exposure.

**Deferred 2026-09-14 — not in the driver path.** STEPHEN: *"my goal right now is to get our driver
working per plan - i think adjusting scope keeps us away from that goal longer... punch list the need
then let's work on what we should be"*. «#3543» is moved to the backlog. Until it is scheduled, a
garbled line in a phase that stops cogs is a known cost. The collation already recovers a verdict
printed after a corruption (PL-40), and a verdict cut inside one stays MALFORMED.

**Recurred at Visit 2 (2026-09-15), same phases:** Tier 0 `debug_260915-140038.log:978,989-994,1004-1011,1050,1068`;
char `debug_260915-140100.log:250-254,282-287,309-313`. No verdict was lost; `R1-T0-RESTART` again printed on
the tail of a corrupted line (`140038:1011`).

### PL-42 -- T0-12's hand-rotation panel draws nothing, so the operator cannot see the prompt

**Found 2026-09-14 in Visit 1.** STEPHEN: *"the t0-hand test was aborted because the UI didn't draw
properly so i couldn't understand what was being asked."*

**Read from source (DERIVED):**
- `src/test_bench_t0.spin2:1232` declares `PLOT bench ... HIDEXY UPDATE` and never draws into it:
  no text, no layer, no `UPDATE`.
- The operator prompt at `:1233` is a plain `debug()` record, so it reaches only the terminal
  text, not the panel.
- The key poll at `:1239` targets the empty panel.
- `:1219-1221` records the pattern as "UNVERIFIED (compile-checked only)".

**What the log shows (MEASURED):** the declaration at `debug_260914-120126.log:22`, then `bench PC_KEY`
polls about every 64 ms and no `T0-12,started` line. No key was ever received, and the session was
closed from the host.

**Consequence:** 90 ticks per revolution is still not measured on the bench. T0-12 is its only
ground truth (PL-39).

**Fix direction:**
- Draw the prompt and state on the panel using Stephen's proven technique (PL-15;
  `DOCs/REF-NO-COMMIT/dbg-display-theory/`). The characterisation panel removed in `7595274` is the
  in-repo precedent that drew on this rig (`analyses/bench/2026-09-12/debug_260912-153807.log`).
- Verify that the panel renders before the visit.
- Record the direction turned alongside the sign of the tick change, per PL-39.

**Fixed in tree 2026-09-14 («#3542»); certification is owed to Visit 2 (Stephen's hands).**
- The panel draws with the documented LAYER/CROP/UPDATE technique. It shows the prompt, the state
  and the live transition and illegal counts.
- The assets come from `tools/gen_t0hand_assets.py` and are committed beside the source.
- `T0-12,started/running/end` log the told direction (CW from the hub) and a signed tick position.
  The position is decoded with `SIGNX 7` from a copy of `deltas65`.
- The direction is fixed, because the artwork bakes it in.
- DERIVED: compiles under the t0-hand tier's flags. UNVERIFIED: that the panel renders on the rig.

**Certified at Visit 2 (2026-09-15, `analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §2):** the panel
drew and took the S key, and T0-12 measured 270 transitions for 3 turns, 0 illegal
(`debug_260915-142347.log:394`, `:531`). **90 ticks per revolution: MEASURED.** Ready to sweep at closeout.

### PL-43 -- scan run 6 went silent under a load step, and the watchdog did not speak

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

### PL-45 -- `getCurrent()` reads about 0.05 A with the motor stopped on the left board

**Found 2026-09-14 in Visit 1.** DERIVED from `src/isp_bldc_motor.spin2:752-767`, confirmed
against the log.

- `getCurrent()` divides the hub long `sense_i_mV` by the board's sense scale and subtracts no zero.
  The only offset removed is the driver's start-time ADC calibration (`:2425-2427`).
- The left board's sense channel sits about 7.7 mV above that with the drive floated, and the right
  board about 0.4 mV. MEASURED: `zero_mV_x10` 72–82 left, 3–5 right,
  `analyses/bench/2026-09-14/debug_260914-115953.log:80-248`.
- So at rest the left board reports about 0.05 A, and 1 W at the nominal voltage: `amps_x10k` 535,
  `watts_mW` 990 at `:80`.
- Watts use the nominal drive voltage from the user config, not a measured one (`:767`, `:1427`).

**Why it matters:** small against a running motor, but it is a standing offset in a public reading.
A future current limiter (S-2 / C-5) and any user who thresholds on "current is zero" would
inherit it.

**Fix direction:** take a rest zero with the drive floated, then subtract it in `getCurrent()`.
The scan and char binaries already measure that zero this way. Decide it together with PL-25,
which touches the same scale path.

### PL-46 -- scan v4 cannot demonstrate a half-speed minimum, and its half-speed cell passes anyway

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

### PL-47 -- the library has no abort and error contract

**Raised 2026-09-14 by Stephen**, while PL-44 was discussed. His rules, verbatim:
- *"an abort can return a value, we should never return a zero from an abort as it wouldn't be
  recognizable as a bare abort returns zero"*
- *"if the rhs method that was aborted returnes a value when not aborted we can't let abort values be
  in the set of method returned values"*
- *"a bare abort returns 0 so a method that also returns zero won't see the abort case"*
- *"traps are an exeptional return path - not normal use (we likelly abort to protect hardware from
  being damaged - or actuators harming their environmnet"*
- *"if we are diving at high rate of speed and all of a sudden both motors start showing hi current
  this probably means the platorm is now blocked by something... continuing to drive the motors in
  this case would likely cause harm  this might be good cause for abortive behavior"*
- *"for methods that can't signal an error why don't we have an error variable (do we need this per
  calling cog) that carries the error or no-error which we then check in our tests"*

**The contract** (a DERIVED statement of those rules):
1. **No bare `abort`.** Every abort carries a named, non-zero code.
2. **An abort code is never a value its method returns normally.** A method whose normal returns
   span the whole range, such as a signed getter, has no free codes, so its errors go through
   rule 4.
3. **An abort is the exceptional, protective path.** It is used where continuing risks the hardware
   or the surroundings, such as a blocked platform. It is never a normal return path.
4. **Ordinary errors go to an error variable per calling cog.**
   - `LONG lastError[8]` per instance, indexed by `COGID()`. Cogs other than the application's call
     the same instance, for example the steering object's sense task.
   - The first error is sticky until the read-and-clear `getError()` collects it.
   - Codes are `ERR_*`, with `NO_ERROR = 0`, mirrored into `isp_steering_2wheel`.
   - A method records its code before any abort, and aborts with the same code.
   - The variable stays outside the PASM-addressed VAR runs, and separate from the driver's fault
     latch.
5. **A protective condition is acted on where it is detected** (DERIVED). The sense-task cog, not
   the caller, sees a blocked platform. It secures the motors itself. The caller learns of it
   through `getError()`, and through a non-zero abort from its next motion call, caught by its
   top-level trap. Ties to audit findings S-2, C-5, Z and AF.

**What exists today:** at least one bare abort, in `src/isp_bldc_motor.spin2`
`confgurePowerLimits()` ("SHOULD NEVER get here"). No error variable has been found. The full
inventory is not yet taken.

**Bench consequence:**
- Tests call library methods normally and check `getError()`.
- One top-level trap per binary secures the hardware and ends the run.
- Traps remain only where a test deliberately exercises an abort path.
- That removes the per-call traps behind PL-44's lost values.

**Fix direction (Batch 1b):**
- Inventory every abort in the library and bench binaries: its value, its method's return set, and
  whether a protective purpose justifies it.
- Apply rules 1–4.
- Document the codes and `getError()` in `DRIVE-OBJECTS.md`.
- Convert the bench harness.
- Rule 5's blocked-platform abort is designed together with the current-limit work (S-2 / C-5), not
  bolted on.

**Design written 2026-09-14** (`plans/ABORT-ERROR-CONTRACT-DESIGN.md`, «#3538» phase 1). Its
inventory: 22 aborts, 15 in the motor object and 7 in the steering object. Every one is bare, every
value lies in its method's normal return set, and none is protective. All become ordinary errors.

**Deferred 2026-09-14 — not in the driver path.** STEPHEN: *"my goal right now is to get our driver
working per plan - i think adjusting scope keeps us away from that goal longer... punch list the need
then let's work on what we should be"*.
- The need is held here, with the design on file.
- The inventory's defects are PL-48 and PL-49.
- «#3538» is paused. The bench harness («#3539») no longer depends on this contract: it calls
  normally and reads `start()`'s cog id or -1, with no `getError()`.
- The two open API questions (a result on methods that return nothing today, and the
  protective-stop names) are unasked and go to Stephen when this is scheduled.

### PL-48 -- validating a pin group then calling `start()` clears pins P0-P15, including the release demos' HDMI pins

**Found 2026-09-14** in «#3538»'s inventory. The arbiter confirmed it by reading source; it is not
observed on hardware.

**The chain (DERIVED):**
1. `validBasePinForChoice()` calls `validatePinBase()`, which calls `claimPinBase()`
   (`src/isp_bldc_motor.spin2:985-990`, `:250-260`, `:210-248`). That records the pin claim under
   this instance's `@pinbase`, but leaves the `pinbase` VAR at 0.
2. `start()` → `startEx()` sees the claim and calls `stop()` first (`:103-104`, the PL-24 restart
   rule).
3. `stop()`'s guard is `(pinbase <> VALUE_NOT_SET) and holdsPinBaseClaim()` (`:153`). On a fresh
   instance `pinbase` is 0, not `VALUE_NOT_SET`, so the guard passes, and it runs `pinclear(0 addpins
   7)` and `pinclear(8 addpins 7)` (`:154-155`).

**Exposed callers:**
- `src/demo_single_motor.spin2`, a certified release demo, starts HDMI on `PINS_P8_P15` (`:33`,
  `:55-57`), validates the motor base (`:61`), then starts (`:68`).
- `demo_dual_motor_hdmi.spin2` and `demo_dual_motor_rc_hdmi.spin2` use HDMI on P0-P7, and validate
  through the steering object first.

`PINCLEAR` zeroes each pin's smart-pin mode (`p2kbSpin2Pinclear`). Whether the HDMI output is
actually lost depends on how `p2videodrv` drives those pins, and is UNVERIFIED.

**When it came in (DERIVED):** this sprint. Both the stop-first restart (PL-24, «#3499») and the
full 16-pin clear in `stop()` («#3500») are new since 5.0.2. It is a regression candidate in a
release demo.

**Fix (correct by construction, in «#3538» phase 2):**
- `validBasePinForChoice()` becomes a pure check, as its own doc says ("VALIDATE users' base-pin
  choice").
- The claim is taken only by `start()`/`startEx()`/`testSetup()`, after validation.
- `stop()` clears pins only when this instance's `init()` completed.

### PL-49 -- «#3538»'s inventory found nine more defects in the start and stop-limit paths

**Found 2026-09-14.** DERIVED from source, not observed on hardware. Every one is removed by the
contract's construction in «#3538» phase 2. Evidence and line numbers are in
`plans/ABORT-ERROR-CONTRACT-DESIGN.md` §1.4.

- **F-2:** a `start()` rejected on its voltage keeps its pin claim with no cog behind it. The abort
  skips PL-36's release.
- **F-3:** `start()` with an illegal pin-group enum launches a driver cog on pins derived from −1.
- **F-4:** a rejected `stopAfterRotation()` has already erased an armed limit, and the steering
  object's `stopAfterDistance()` has already reset tracking.
- **F-5:** some stop limits silently arm nothing:
  - a request that rounds to 0 ticks;
  - a single-motor limit with no sense cog running;
  - a steering limit set before `start()`.
- **F-6:** `SyncStatus()` busy-waits without a bound, so the steering object's `driveAtPower()` can
  hang the application cog while a wheel is e-stopped or not started.
- **F-7:** the serial commands `stopaftrot 0`, `stopaftdist 0` and `stopafttime 0` pass the host
  validator, reach a bare abort, and end the serial program with the motors holding their last
  command.
- **F-8:** an illegal detection mode is silently replaced by auto-detect.
- **F-9:** the ABI layout guard only prints, and still launches the driver. `CLAUDE.md` is also
  stale: the status run is now 16 longs.
- **F-13:** an abort from the right wheel inside the steering `start()` strands the left wheel's
  driver cog, parked on `waitatn`.

### PL-50 -- measured tick rates sit 4.4 % below the C-1 speed model at both measured speeds

**Found 2026-09-14** in «#3508»'s design review (`plans/MOTION-HARNESS-DESIGN.md` Q9, §12.1).

**Evidence:**
- The model: `DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md:574-593`. `drv_incr` is applied every
  500 µs (2000 passes per second), so an increment of 36_750_000 predicts 102.7 ticks/s and
  73_500_000 predicts 205.4 (DERIVED).
- MEASURED on both motors at Visit 1: 98.2 and 196.4 ticks/s (`analyses/bench/2026-09-14/VISIT-1-RESULTS.md:90`).
  That is 4.4 % below at both speeds, so the ratio is constant, not speed-dependent.
- The same ratio implies about 1,912 passes per second rather than 2,000 (DERIVED).
- The study's own confirmation, `147_000_000` giving "RPM 272.0" against 273.8 (0.7 %), comes from a
  source comment with no log behind it.
- The scan's self-check band 90-106 around an "expected 99" (`src/test_bench_scan.spin2:283-284`,
  `:396`) is labelled DERIVED but carries no derivation.

**Why it matters:**
- Every speed, distance-time or rpm figure computed from the model is about 4 % high. That includes
  the study's C-1 table and any published speed data.
- A C-1 verdict judged against the model would report a departure at the first rung, so «#3509»
  judges linearity instead (§12.1 Q9).

**Fix direction:** derive the driver's real pass period from source (the PASM control loop and how its
period is set at the compiled `CLK_FREQ`), restate the model from it, and correct the scan's
"expected 99" derivation. The C-1 ladder at Visit 2 then confirms linearity against the corrected
model. Do not design a bench run to find the period.

**Visit 2 ladder (2026-09-15, `analyses/bench/2026-09-15/VISIT-2-RESULTS.md` §9.1):** the ratio is
constant across the whole range, not just at two speeds.
- `rate_x10 / pred_x10` is 0.946–0.965 from 10M to 165M on both motors and both signs, and 0.953–0.965
  from 40M up. The mean is about 0.957, 4.3 % below.
- The 5M rung reads 1.000 only because 14 ticks quantise to ±7 %.

**Fixed in tree 2026-09-15 («#3548»): a model error, derived from source. Certification is owed to the next visit.**
- **Mechanism (DERIVED, `src/isp_bldc_motor.spin2`):** `drv_incr` is applied once per drive pass, and a pass runs
  every **23** ADC frames.
  - `init()` sets `cfg_ctcks` to 500 µs and `frame_cnt` to one 44 kHz frame, both truncated to whole ticks.
  - `drvMotor` re-arms CT1 from its own start. `.ctlMotor` waits one ADC period per pass (`wait4adc`) and tests
    CT1 (`jnct1`) only at the end of each pass.
  - 22 frames fall just short of the deadline at every swept clock: 99_990 < 100_000 ticks at 200 MHz,
    134_992 < 135_000 at 270, 149_996 < 150_000 at 300. The pass runs on the 23rd frame: 522.7 µs, about
    1913.2 passes/s, **0.9566** of the model, against the MEASURED 0.957.
  - Authority: `p2kbPasm2Addct1`, `p2kbPasm2Pollct1`, `p2kbArchSmartPin01111CountHighsOptionalDec`.
- **Also consistent:** the DocoEng rows in `confgurePowerLimits()` match the corrected law
  (282_000_000 → 754 cts/s recorded, 753.7 DERIVED). The 6.5″ rows match the 2000-pass figure instead, so they
  were computed, not measured.
- **Not a driver defect (DERIVED).** This scheduling cannot meet "2 kHz" at any clock, because the deadline is
  re-armed from each pass's start and tested only at frame-aligned pass ends. Every speed, ramp and fault ceiling
  was characterised on the real period. Scheduling the pass in whole frames would make the period exact by
  construction, but it would raise every speed and ramp rate by 4.5 % and move every ceiling. That is a product
  change and is not taken here.
- **Corrected:**
  - the library's timing comments, and a note on the 6.5″ ceiling block (recorded lines and increments untouched);
  - `test_bench_scan.spin2` expected rates 98 / 196 (SRC_REV 11);
  - `test_bench_dual.spin2` `pred_x10` scaled by 22/23 (SRC_REV 8);
  - the study's C-1, by a dated revision block.
- **Still carrying the 2000-pass figures:** `MOTOR_CHOICE.md`'s attainable-RPM table, which is «#3515»'s.
- **Not swept:** the other bench binaries were not searched for further 2 kHz predictions (no search tool this
  session).
- **Certifies with:** the next ladder. `rate_x10 / pred_x10` should read about 0.99–1.01; today's spread,
  0.946–0.965, maps to 0.989–1.009.

### PL-51 -- the steering object's `getMaxSpeedForDistance()` returns the max speed, not the max speed for distance

**Found 2026-09-14** by «#3508» phase 2(b1), and confirmed by the arbiter reading source. DERIVED, not
observed on hardware.

- `src/isp_steering_2wheel.spin2:558-564`: the method's doc says *"Returns the last specified
  {maxSpeedForDistance}"*, but its body returns `rtWheel.getMaxSpeed()`. The commented-out line above it
  makes the same call on the left wheel.
- It sits directly below `getMaxSpeed()` (`:550-556`), whose body is identical, so this reads as a
  copy-paste defect.
- **Who is affected:** any caller that reads back the speed limit it set for distance moves. That
  includes a host driving the serial protocol, if it exposes this getter.
- **Not affected:** `driveForDistance()` itself, which reads the wheels directly (`:252`).

- **The correct getter exists:** `PUB getMaxSpeedForDistance() : nSpeed4dist` at
  `src/isp_bldc_motor.spin2:773-777`, returning `maxSpeed4dist`. The steering object's own
  `driveForDistance()` calls it on both wheels (`:252-253`).
- **The documentation describes the intended behaviour, which the code does not deliver:**
  `DRIVE-OBJECTS.md:71` (steering) and `:117` (motor).
- **Bench consequence:** «#3508»'s harness does not read this getter. It sets the distance speed
  itself and prints the value it set (`plans/MOTION-HARNESS-DESIGN.md` §12.8).

**Fix direction:** `nSpeed4dist := rtWheel.getMaxSpeedForDistance()`, a one-line change. Also check
whether the serial object exposes this getter.

### PL-52 -- `getPower()` keeps reporting the last power after the motor is stopped, against its own doc

**Found 2026-09-14** by «#3508» phase 2(b3), and confirmed by the arbiter reading source. DERIVED, not
observed on hardware.

- **The doc:** `src/isp_bldc_motor.spin2:744-748` says `getPower()` returns the last specified power
  *"(will be zero if the motor is stopped)"*. `DRIVE-OBJECTS.md:68` says the same for the steering
  object.
- **The code returns `motorPower` unchanged.** The stop paths never write it:
  - `stopMotor()` (`:664-669`) and `emergencyCutoff()` (`:671-677`) only call
    `setTargetAccel(0, false)`;
  - `setTargetAccel()` (`:1434-1440`) writes `targetIncre`, not `motorPower`;
  - the sense task's distance and time stops use the same `setTargetAccel(0)` path.
- **Who is affected:** any caller that reads `getPower()` to decide whether the motor is still
  commanded. After a stop or a completed distance move, it still sees the old power.
- **Not yet checked:** every writer of `motorPower` was not searched. A writer elsewhere, such as
  `driveAtPower(0)`, could make some stop paths read zero.
- **Bench consequence:** «#3508»'s BM-OUT `l_pwr`/`r_pwr` and BM-FLOOR print `getPower()` as the last
  specified power, which is what it returns. No harness change is needed
  (`plans/MOTION-HARNESS-DESIGN.md` §12.9).

**Fix direction:** first find every writer of `motorPower`. Then either clear it on every stop path, or
correct the doc to "last specified power", whichever the API intends.

### PL-53 -- the scan, char and detection binaries still carry their own copies of the record builder

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
- **Fix direction:** after Visit 2, replace each copy with `OBJ` instances of `isp_bench_log` (a second
  instance for a watchdog cog), bump each binary's `SRC_REV`, and prove with a before/after log diff that
  every record prints byte-identical. For the detection binary, `R2-HOST-DETDIFF` is that diff.

### PL-54 -- `src/test_dual_motor.spin2` names itself `demo_dual_motor.spin2`, and most of its body can never run

**Found 2026-09-14** by «#3508» (`plans/MOTION-HARNESS-DESIGN.md` §7.3), and confirmed by reading the
source in phase 2. DERIVED, not observed on hardware.

- **The wrong name:** `src/test_dual_motor.spin2:3` reads `File....... demo_dual_motor.spin2`, the name of
  the certified release demo, not this file's.
- **The unreachable code:** `:77` prints `* TEST complete, holding`, then `:78` is a bare `repeat` with no
  body and no exit. Nothing after it in the valid-configuration branch can run: the 1 ft distance drive,
  the two `driveDirection()` holds, the left and right wheel holds (`:80-106`) and `wheels.stop()`
  (`:109`). `debug("* DONE")` (`:113`) is reached only on the invalid-configuration path.
- **The class:** a program whose visible intent (its header, its later steps) differs from what
  executes, so a reader, or an agent trusting either, is misled. It is not a bench binary (no records,
  watchdog or sign-off), so no visit depends on it.
- **Fix direction:** correct the header's file name. Then either delete the unreachable steps or remove the
  holding `repeat` so they run, whichever this test is meant to do. That is Stephen's call: it is his test
  program.

### PL-55 -- stopping from 75 % speed or above draws more than 10 A

**Found 2026-09-15 in Visit 2** (`analyses/bench/2026-09-15/VISIT-2-RESULTS.md` §3).

**What was measured (MEASURED):**
- The harness's 10 A abort (1,500 mV on 4 consecutive reads) fired 8 times, every time on a stop:
  - FAULTB, stopping from 110.25M: LEFT NEG 1,506, RIGHT NEG 1,552 and RIGHT POS 1,519 mV
    (`debug_260915-135528.log:443,1831,2245`);
  - LIVE, stopping from 110.25M: RIGHT POS 1,586 (`debug_260915-134805.log:15079`);
  - LADDER, stopping from 165M: LEFT NEG 1,642, RIGHT NEG 1,513 and RIGHT POS 1,557
    (`…134805.log:15120,15197,15236`);
  - OVERSHT 10 ft, steering at 75 %: 1,646 mV, with the right wheel's current rising through SPIN_DN
    (`…135528.log:2973,3241`).
- LEFT POS never tripped.
- At half speed every stop's current rises 20–50 % above the running current: NEG from about 950 to
  1,150–1,220 mV, POS from about 500 to 640–720 mV (STOPMODE and BASELINE traces).

**Mechanism (DERIVED from source):**
- A zero request enters `.rampDn`. `drv_incr` steps down by `ramp_down` every 500 µs while the wheel
  is still driven (`src/isp_bldc_motor.spin2:2206-2211`, `:2303-2320`).
- Drive is released only at zero (`:2327-2333`).
- The wheel is therefore driven down its ramp. Running current at 75 % is 969–1,034 mV
  (`…134805.log:15072,15078`), so the rise puts a stop at the abort threshold.

**What it cost:** FAULTB trials 2–5 on three of the four motor/sign combinations, C-3 at 10 ft, and
`R14-DUAL-RSTPROV-B` RIGHT.

**Disposition, STEPHEN 2026-09-15:** *"put this as an item we need to research after our driver is back
in shape. That sounds like a new feature request to me, and yes, we want to address it at this release,
but not right now."*
- A research item for 6.0.0, scheduled after the driver repairs.
- Until then the bench harness keeps its 10 A abort unchanged. Trials that stop from 75 % stay NOMEAS.

### PL-56 -- `emergencyCutoff()` stops a half-speed wheel within one tick; the drive-off state may be a dynamic brake

**Found 2026-09-15 in Visit 2** (`VISIT-2-RESULTS.md` §5.2).

**What was measured (MEASURED, `debug_260915-135838.log`):**
- In the four e-stop FLOAT traces, `i` falls to 8–12 mV one sample after the mark (`:3296-3297`).
- `pos` and `hw` stop within one tick, and rest is confirmed 10–12 ms after the mark
  (`:3489,3713,4563,4787`).
- Baselines, same rig and speed:
  - `stopMotor()` takes 74–76 ticks;
  - `stop()`, which releases the pins, coasts 38–48 ticks (`debug_260915-134805.log` STOPMODE).

**Why the count is real (DERIVED):** the hall count runs in the control loop on every pass, whatever the
driver state (`src/isp_bldc_motor.spin2:2485-2495`). The e-stop only skips the request logic
(`:2141-2146`). So the wheel stopped, at an average deceleration of at least 19,000 ticks/s².

**Likely mechanism (DERIVED, one fact UNVERIFIED):**
- The e-stop calls `.driveoff`, which sets `driveoff := 1` (`:2144`, `:2572-2573`).
- The control loop then writes duty 0 to all six PWM pins (`:2468-2469`).
- The low-side pins use inverted output (`pwmn`, `P_INVERT_OUTPUT`, `:2615`; `:2465`), so duty 0 is a
  constant high on them.
- **UNVERIFIED:** that a high on the Rev B board's low-side input turns that FET on. If it does, all
  three phases are held low, which brakes the motor.

**If the premise holds (DERIVED):**
- The same `driveoff` state is the driver's FLOAT at rest (`checkstop`, `:2580-2585`) and its fault
  state (`:2539`). "Float" does not freewheel, and a fault at speed brakes hard.
- On the floor with the robot's mass, that braking current may not pass the sense resistor.
- PL-30's "no bridge current can flow during the reading" still holds at rest, where the wheel does not
  turn.

**Fix direction:**
1. Confirm the low-side input polarity from the board documentation or the schematic.
2. Then decide what FLOAT, e-stop and fault should each do to the bridge. That is an API and safety
   decision for Stephen.

**Polarity read from source, 2026-09-15 (DERIVED, resting on MEASURED operation) -- and it conflicts
with a recorded bench observation, so it is NOT settled:** the code implies a high on the low-side input
turns the low FET on.
- In normal drive the control loop writes each low-side pin the high side's duty plus `dead_gap`, on an
  inverted output (`src/isp_bldc_motor.spin2:2470-2483`). Its comment: *"make sure low side turns off
  (inverted) earlier than high side turns on"*. The low-side pin is therefore low across the whole
  high-side on-window plus the gap, and high otherwise.
- That is complementary drive with deadtime only if a high turns the low FET on. With the opposite
  polarity the low FET would be on exactly while the high FET is on: shoot-through on every PWM period.
  The driver has run for hours on this rig without it.
- The comment at `:2471` agrees: the board's safety interlock acts *"if both low and high side are high"*,
  the state that would command both FETs on.

**Float freewheels. That is Stephen's bench fact, and it settles this.**
- It was recorded before this sprint: `analyses/DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md:388-393`, *"Stephen's
  prior bench testing shows freewheel/float works and full braking works"*.
- STEPHEN 2026-09-15: *"we came into this work with float working as desired"*.
- **The derivation above is the suspect, not the hardware.** Either the reading "duty 0 on the inverted low-side pins
  holds the low FETs on" is wrong, or the float-at-rest and e-stop paths differ in a way not yet read.
- **Withdrawn:** "float does not freewheel" and "every fault brakes hard". The MEASURED 1-tick stop is a fact about
  `emergencyCutoff()` only.
- No question goes to Stephen. Whether the e-stop or fault path should behave differently is looked at only when a
  driver change needs it (doctrine overlay P10).
- This entry first read "settled" and then "a conflict for Stephen" on 2026-09-15; both were wrong.

### PL-57 -- after `emergencyCutoff()` then `clearEmergency()`, the driver keeps its old increment, and a restart at the same speed faults at once

**Found 2026-09-15 in Visit 2** (`VISIT-2-RESULTS.md` §5.3). A library defect.

**What was measured (MEASURED, four of four instances, `debug_260915-135838.log:3490-3502`,
`3714-3729`, `4564-4576`, `4788-4803`):** each follows an e-stop trial, then `clearEmergency()`, then a
zero command and STOPPED.
- The next start at the same speed shows k 0–1 STOPPED, then **k 2 AT_SPEED with `pos` 0** (`:3460`).
- Current stays at 12–21 mV while `e` runs from −19 to −111.
- **k 8 FAULTED** (`:3466`).
- Reset alone cleared it in 30 ms (`:3502`).

**Cause (DERIVED from source):**
- The e-stop path jumps to `.endRqst` without clearing `drv_incr` (`src/isp_bldc_motor.spin2:2141-2146`).
- The clear path only sets `DCS_STOPPED` (`:2148-2149`).
- A zero request while STOPPED exits without touching it (`:2156-2161`).
- On the next start, `.rampUp` sees `drv_incr` non-zero and skips the ramp start and
  `.checkstopfloaton` (`:2270-2272`). It finds `drv_incr` equal to the target and declares AT_SPEED
  (`:2274-2275`).
- `angle_` then advances at full speed against a stationary wheel, and the position-error check faults
  (`:2536-2541`).
- `.resetFault` does zero `drv_incr` (`:2195-2200`), which is why the start after each fault was clean.

**Also (DERIVED, not measured):** a restart at a different speed would ramp from the stale increment,
not from zero.

**Fix direction:** the e-stop entry (or the clear) resets the running state the same way `.resetFault`
does — `drv_incr`, `prior_incr`, `angle_` from the halls — so a start after an e-stop is an ordinary
start. Proof: an e-stop, clear, then a restart at the same speed reaches AT_SPEED through SPIN_UP.

**Fixed in tree 2026-09-15 («#3546»); certification is owed to the next visit.**
- `src/isp_bldc_motor.spin2` has one dot-local `.clearRun`, which zeroes `drv_incr`, `prior_incr`, `fwdrev` and
  `angle_`.
  - `.resetFault` now calls it, instead of carrying its own copy.
  - The e-stop entry calls it right after `.driveoff`, so no running increment survives an e-stop.
- Leaving ESTOP now also calls `checkstop`, as `.resetFault` does, so the drive state follows the stop mode.
- The next start takes `.rampUp`'s `drv_incr == 0` path: the ramp starts at `ramp_min`, drive is enabled, and the
  angle is taken from the halls.
- Gates: `tools/build-check.sh` 47/47 with both release demos certified; `tools/check_style.sh` PASS.
- The PASM-addressed VAR runs are untouched (`git diff`).
- **Certifies with:** `dual-c` POSTFLT's e-stop BRAKE traces, which reach AT_SPEED through SPIN_UP with no fault.
  They faulted 4 of 4 at Visit 2.

### PL-58 -- `holdAtStop()` does not change a stop from speed, although `stopMotor()` is documented as affected by it

**Found 2026-09-15 in Visit 2** (`VISIT-2-RESULTS.md` §4).

**MEASURED:** with `holdAtStop(FALSE)` and `holdAtStop(TRUE)`, `stopMotor()` takes the same distance in
every rep: 19–20 ticks from quarter speed and 74–76 from half, on both motors and both signs
(`debug_260915-134805.log` STOPMODE). The deceleration is about 254 ticks/s² at both speeds.

**DERIVED:**
- `.rampDn` never reads `stop_mode`. It is used only once the motor is STOPPED
  (`src/isp_bldc_motor.spin2:2156-2160`, `:2327-2333`).
- So the stop mode governs only what the bridge does at rest.
- `stopMotor()`'s doc line "AFFECTED BY: holdAtStop()" (`:666`) is true only at rest.

**Fix direction:** say in the doc (and `DRIVE-OBJECTS.md`) that `holdAtStop()` selects hold or release
**at rest**, and that every stop from speed follows the driver's ramp. Publish the C-4 data with it
(«#3514» / «#3515»). Decide together with PL-55 and PL-56.

### PL-59 -- POSTFLT's 3° offset does not provoke a fault at half speed, so the post-fault stop is unmeasured

**Found 2026-09-15 in Visit 2** (`VISIT-2-RESULTS.md` §5.1).

**MEASURED:**
- All four fault traces end `why,NO_FAULT` (`debug_260915-135838.log:2659,2969,3733,4043`).
- With the NEG offset written to 3° at half speed, current fell from about 945 mV to 21–32 mV
  (`:2916-2922`), speed held, and no fault came in 2 s on either motor.
- In the same visit, scan run 8's RIGHT NEG half-speed leg faulted at 4°, with 5° its last clean point
  (`debug_260915-140255.log`).

**DERIVED:**
- `FAULT_PROVOKE_NEG_DEG` = 3 was measured to fault at quarter speed (`plans/MOTION-HARNESS-DESIGN.md:487-493`).
- At half speed the fault edge depends on how it is approached: the scan steps and settles, while
  POSTFLT writes once at speed.
- S-9a's post-fault stop therefore has no data.

**Fix direction:** POSTFLT needs a provocation that faults on every instance, confirmed by its own
record, before S-9a can be judged. Decide the method at the harness's next revision; do not tune an
angle at the bench.

### PL-60 -- the left board's `ph_x10` reading sags with load and the right board's does not

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

### PL-61 -- above 100M the duty pins at maximum and current falls twentyfold while speed still tracks

**Found 2026-09-15 in Visit 2** (`VISIT-2-RESULTS.md` §9.1–9.3). Input to PL-26 and PL-50.

**MEASURED (`debug_260915-134805.log:15084-15233`):**
- All 48 ladder rungs are OK on both motors and both signs, including the 155M and 165M probes. The
  unloaded ceiling is above 165M, at least 12 % above the 147M limit.
- Duty reaches `duty_max` 24,264 by 120M.
- `inet_x10` peaks at 100M (10,186–12,612), then falls: 5,461–5,721 at 120M, about 1,500 at 140M, and
  435–653 at 155–165M.
- Speed still tracks the command at the same ratio, 0.956–0.958, while peak error grows from 64–77 to
  101–107.
- `rate_x10 / pred_x10` is 0.946–0.965 from 10M to 165M: a constant gain, not a speed-dependent
  departure (PL-50).

**Mechanism: not established.**

**Fix direction:** explain it from source before any change to the ceilings. It bears directly on
PL-26's commutation-angle question (lead angle at speed) and on the published speed limits.

### PL-62 -- the `dual-clock` tier accepts any number as the clock, so a ten-digit value reached the compiler

**Found 2026-09-15 in Visit 2.** STEPHEN: *"dual-clock2m.out three tests couldnt be run - this is the
console out from 1 of them"*.

**MEASURED (`analyses/bench/2026-09-15/dual-clock2m.out`):**
- The banner and the patch line both read `2000000000`, which is ten digits. The run sheet says
  `200000000` (`analyses/bench/VISIT-2-RUNSHEET.md:18`).
- Output stops at `Compiling with DEBUG`, with no error line and no log.

**DERIVED:**
- `tools/bench-run.sh:221` checks only that the value is digits, so any number passes.
- The script's own error lines go to stderr (`:254`), and this console capture does not show them.
- The other two clock loads left no output to read.

**Fix direction:**
- For `dual-clock`, refuse any value other than `200000000`, `270000000` and `300000000`, naming the
  three. That makes the typo impossible rather than detectable.
- Make sure the failure reason reaches the console the operator captures.

### PL-63 -- the right motor's quarter-speed NEG float stop never confirmed rest, in either rep

**Found 2026-09-15 in Visit 2.** Minor.

**MEASURED:** traces 25 and 28 end `why,NOT_REACHED` (`debug_260915-134805.log:7888,8787`), although
both reached STOPPED after 19 ticks, like every other quarter-speed stop. Every other STOPMODE trace
confirmed rest.

**Consequence:** the C-4 table has no time to rest for that one cell. Its tick count is complete.

**Fix direction:** read those two traces' last samples for the value that kept changing (`pos`, `hw`
or both), then decide whether the stillness rule or the reading is at fault.

### PL-64 -- the attended-test UI is out of step with what each test needs, and `dual-ui` failed itself

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

### PL-65 -- `BM-PLAN` names the wrong findings for the UICHECK and FLOOR parts

**Found 2026-09-15 in Visit 2** (`analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §3). Minor.

**MEASURED:** UICHECK's plan record says `finds AC` (`debug_260915-142103.log:26`); FLOOR's says `finds S-9a`
(`debug_260915-142650.log:26`).

**DERIVED:** FLOOR is the part that finds AC, and UICHECK finds none; S-9a belongs to part C.

**Fix direction:** correct the two labels in `src/test_bench_dual.spin2` at its next revision.

### PL-66 -- a faulted motor stays faulted when the caller sends the same power again

**Found 2026-09-15** while stating the fault-clearing rule for «#3547». DERIVED from source, not observed on
hardware.

**The mechanism (`src/isp_bldc_motor.spin2`, PASM driver):**
- The driver leaves `DCS_FAULTED` only through `.resetFault`, inside `.newRqst`.
- A stop always gets there: a zero request while not STOPPED jumps to `.newRqst`.
- A nonzero request gets there only if it differs from the last one. `.notRqStop` compares it with the saved
  request and, when they are equal, continues the current request (`.currRqst`).
- In `DCS_FAULTED`, `.currRqst` matches no state and falls through to `.justIncr`, which advances `angle_` with
  the drive off. The motor stays faulted.

**Who is affected:** a caller that retries after a fault by sending the power it was already running at, such as
`driveAtPower(50)` again, or a loop that re-sends its current command. The retry does nothing. Since «#3547»
`getStatus()` reports `DS_FAULTED`, so the state is visible, but nothing says the retry was ignored. The two-wheel
object and the serial protocol inherit it.

**Related:** PL-28 item 1 is the same mechanism on the test path. `testResetFault()` works around it by sending
zero first.

**Fix direction:** decide what a repeated command does while faulted.
- Treat it as a new request, so a retry restarts the motor. Correct by construction for a retry, but a fault at
  speed may mean a blocked wheel (PL-47 rule 5), and a retry would drive into it again.
- Or keep requiring a stop or a changed power first, and state that in `DRIVE-OBJECTS.md` and the method docs.

That is an API and safety decision for Stephen, taken when the fault path is next scheduled. «#3547» documents
today's rule: *the fault clears when a stop or a different power is commanded*.

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
