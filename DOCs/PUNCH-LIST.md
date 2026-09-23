# P2-BLDC-Motor-Control — Punch List

Active outstanding work. Confirmed-done items are swept to a dated archive by
`punch-list-maintenance` at sprint closeout.

Opened 2026-09-09 by the `bootstrap-conventions` / `baseline-health` bootstrap.

---

## Open

Confirmed-done entries swept on 2026-09-23 are in
[`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-23.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-23.md).

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

**Status 2026-09-23 («#3515»): three of the six are resolved.** The "two objects" and "This steering object"
paragraphs, and the "provides the following methods" line, now live only in `DRIVE-OBJECTS.md`, which also holds
the one canonical account of the cog cost (`#objects-and-cogs`); `README.md` and `DRIVE-OBJECTS-SERIAL.md` link to
it. `tools/doc-audit.sh` no longer reports them. **Still duplicated:** the project tagline, the FlySky wiring
paragraph and the "Video of author" line.

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

**Ruling, STEPHEN 2026-09-17:** *"yes the spin2 style guide is a gate for this project - we deliver
code, it MUST match our style guide (all .spin2 files in repo that we produced in project - not those
copied from other developers)"*. The gate is earned, not downgraded («#3517»), and its surface is every
`.spin2` this project authored; the imported files (`p2videodrv`, `p2textdrv`, `jm_*`, `hng034rm`) stay
out. That ruling also brings PL-10 and PL-11 into this release -- see their entries.

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

**FIXED IN SOURCE (aged-state sweep 2026-09-17, found reading `init()` for «#3568»):** `init()` now honours the
caller's `eMotorVoltage` rather than re-reading `user.DRIVE_VOLTAGE` (`src/isp_bldc_motor.spin2`, the block
commented *"PL-14: honour the caller's eMotorVoltage parameter"*, just before `confgurePowerLimits()`), which makes
the parameter and `validVoltageForChoice()` meaningful and lets two motors run at different voltages. This entry
had gone on saying "an API decision"; the decision was taken the parameter-honouring way. No isolating cell exists:
every shipped caller passes the configured voltage, so the change is behaviour-neutral for them.

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

> ## ⭐ ACCEPTANCE CRITERION WRITTEN 2026-09-17, at Stephen's request
>
> **STEPHEN:** *"i think we need a test for PL-26 - how would we know if noticibly better?"*
>
> **Full design:** [`analyses/BLDC-COMMUTATION-PRINCIPLES.md`](analyses/BLDC-COMMUTATION-PRINCIPLES.md),
> section *"How we would know it is noticeably better"*. In short:
>
> **THE BEFORE-MEASUREMENT ALREADY EXISTS.** Visit 4 ran the ladder in BOTH directions on BOTH
> motors, so no new baseline run is needed. **MEASURED**, LEFT motor, `amps_x10k` reverse over
> forward at the same commanded speed: **2.16x** (rung 2), **2.00x** (3), **2.02x** (4), **1.97x**
> (5). RIGHT motor 1.88x and 1.86x at rungs 4 and 5. **One direction costs about twice the current
> of the other**, and this independently reproduces the 1.76-1.97x measured on 2026-09-12 from a
> completely different run.
>
> **THE METRIC:** reverse-over-forward current at rungs 3-5 -- today ~2.0, predicted 1.0 if the
> principle holds. The window is rungs 3-5 because below it the current is 0.04-0.12 A and noise
> dominates, and above it the duty saturates so the asymmetry cannot show.
>
> > ## ⛔ THE RATIO ALONE IS NOT A SUFFICIENT CRITERION. Corrected 2026-09-17, same day, by STEPHEN.
> >
> > **STEPHEN 2026-09-17:** *"If our phase is off, one direction is always going to take more power...
> > If we fix the drive phasing, wouldn't that say the forward or reverse are going to be more
> > consistent and not 2:1, like you're seeing?"* -- and that framing is right, and it is sharper than
> > the one this entry was written with.
> >
> > **THE ARITHMETIC, and it is what makes the ratio insufficient.** The driver places the field at
> > `hall_estimate + offset`. With a fixed hall-zero error **E** per motor, the ACTUAL lead is
> > `offset + E` one way and `-offset + E` the other. The offsets in force are symmetric by
> > construction (`off_neg 43, off_pos 317`, and 317 = 360 - 43), so:
> >
> > - **E = 0 would give equal currents in both directions.** They are 2:1, so **E is not 0, and the
> >   asymmetry IS the evidence of the phase error** -- MEASURED three times now (2026-09-12, Visit 4,
> >   Visit 5), on both motors, with LEFT 2.02/2.03/1.98 and RIGHT 1.90/1.88/1.86 at rungs 3-5.
> > - **Both motors show nearly the same error.** DERIVED: that points at the model (the offset pair
> >   and the hall tables) rather than per-unit sensor placement scatter, which would differ more.
> >
> > ⛔ **AND THIS IS WHY RATIO -> 1.0 CANNOT BE THE CRITERION: correcting the hall zero ALONE
> > equalises the two directions at roughly their average.** Today forward sits near `43 + E` and
> > reverse near `43 - E`; zero out E and both go to 43. Reverse improves, **forward gets slightly
> > worse**, and the ratio reads a perfect 1.0. **A criterion that a regression can satisfy is not a
> > criterion** -- the same defect class as PL-79, PL-80, PL-82, PL-83 and PL-87, written into this
> > entry hours before those were repaired.
> >
> > ### THE CRITERION, RESTATED -- BOTH CONDITIONS, NOT ONE
> >
> > 1. **Symmetry:** reverse-over-forward current at rungs 3-5 falls from ~2.0 toward 1.0.
> > 2. **NO REGRESSION IN ABSOLUTE COST:** the current in the CHEAPER of today's two directions must
> >    not rise. Visit 5's forward figures are the baseline and they are already recorded --
> >    `amps_x10k` LEFT 6_692 / 18_302 / 38_051 and RIGHT 7_269 / 19_819 / 41_075 at rungs 3/4/5.
> >
> > **Both, or the change has not earned its place.** Meeting only (1) means the alignment was
> > corrected and the LEAD was left wrong, which is exactly the half-fix the designer's "separate
> > alignment from lead" warns against: one number cannot carry both the hall-zero correction and the
> > lead angle, and ours does.
> >
> > ⭐ **What this also says about the prize.** The full gain is not "one direction gets better". It is
> > both directions landing at the optimum lead, which is BELOW today's cheaper direction. The scan
> > («#3520») measures the two per-direction minima; their midpoint estimates E and their depth
> > estimates what the lead correction is worth.
> >
> > ⭐ **And the user-facing consequence of NOT fixing it is now recorded separately: PL-88** -- the
> > platform drives its two wheels in opposite increment signs, so straight-line driving puts one
> > wheel in the expensive direction and the asymmetry never averages out.
>
> **THE TEST RUNS BEFORE ANY CODE CHANGES, AND IT MEASURES THE PRIZE.** The offset scan («#3520»)
> is already designed and its predictions are already written. Its three outcomes each decide:
> minima symmetric about one hall zero with about equal current at each -> the model holds and the
> depth below today's default IS the gain, so build it; a residual imbalance at the minima -> the
> simple model is falsified, name the remaining cause before redesigning; shallow minima -> we are
> already near optimum and the ~2x is elsewhere, so do not build it.
>
> ⚠ **The principles document's own prediction warns the prize may be small:** the minimum is
> BROAD, and +/-15 degrees from optimum costs only a few percent. If we are already within that, the
> ~2x is not the offsets' doing, and the alternatives already named there -- unequal hall sectors,
> sensor placement, the one-sector shift between the two tables -- are where it lives.
>
> ⭐ **A second independent route, new 2026-09-17:** the Doco's 360 P/R shaft encoder (1_440
> counts/rev, 0.25 deg) measures the hall zero DIRECTLY rather than inferring it from a current
> sweep, so it can confirm or refute the scan by a different physical path. It cannot reach the
> 6.5in -- the motor is the wheel and there is no shaft.
>
> ⛔ **One axis this rig cannot show:** higher top speed under load. Every run is wheels-lifted and
> Visit 4 found no rung up to 165M faulted in either direction, so the ceiling stays unmeasured by
> ruling rather than by a failed run.

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

**Partly fixed in tree 2026-09-16 («#3556»).** `confgurePowerLimits()`'s `MOTR_6_5_INCH` branch
(`src/isp_bldc_motor.spin2:1798-1815`) now gives 6.0 V and 7.4 V their own placeholder ceilings,
`48_400_000` (~89 RPM) and `59_800_000` (~110 RPM), scaled from the 11.1 V row (`90_000_000` ->
165.3 RPM, the nearest measured point) at the table's own ~14.8 RPM/V slope and rounded DOWN so a
placeholder never promises a speed unmeasured at that voltage. Both rows are labelled PLACEHOLDER
/ not measured in the comment. Not fixed here (out of this task's scope): the 24.0 V FAKE row, and
`MOTOR_CHOICE.md` itself, which stays owed to «#3515» per the task text. No bench observation of
these two rows exists yet -- run-time proof is Stephen's rig, per the task's own note.

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

### PL-41 -- the debug stream corrupts when bench binaries start and stop cogs in quick succession

> **DESIGNED OUT 2026-09-18 («#3543»); run-time proof owed to Visit 6.** Design and as-built record:
> `DOCs/plans/COG-LIFECYCLE-DESIGN.md`. A cog that may print is never stopped outright (the RX task of
> `isp_queue_serial` gained the front cog's EXIT protocol; the joystick and button tasks no longer print);
> every cog start and stop in the six bench programs sits in a `benchLog` quiet window; free cogs are
> counted with `COGCHK()`, not by starting spacers; t0's three exhaustion cells share one occupancy. No
> authored file allocates a lock. Proof: a t0 log (and each bench log) with no run-together `CogN` prefix
> and no truncated record.

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

**IN THIS RELEASE (aged-state sweep 2026-09-17).** The 2026-09-14 deferral above is overtaken:
STEPHEN 2026-09-17, *"your outstanding tasks must be completed before this release"*, and «#3543» is one
of them. Visit 5 also proved the cost is on the wire, not in the terminal, and lost a verdict that a
USB capture alone recovered (PL-85).

**Recurred at Visit 2 (2026-09-15), same phases:** Tier 0 `debug_260915-140038.log:978,989-994,1004-1011,1050,1068`;
char `debug_260915-140100.log:250-254,282-287,309-313`. No verdict was lost; `R1-T0-RESTART` again printed on
the tail of a corrupted line (`140038:1011`).

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

**Status (aged-state sweep 2026-09-17):** the contract that removes all nine was built («#3554»,
«#3555») and no `abort` remains in either library object. Certified by cell at Visit 5
(`debug_260917-172913.log`): **F-3** `R16-T0-BADGROUP` (:158), **F-4** `R16-T0-LIMKEEP` (:59), **F-5c**
`R16-T0-STRNOTSTART` (:91). **F-6** is bounded in source (`SyncStatus()` by `SYNC_TIMEOUT_MS`). **F-13**
cannot occur without an abort. **F-2, F-5a/b, F-7, F-8 and F-9 have no isolating cell**; they are removed
by construction and stay unmeasured. F-9's `CLAUDE.md` staleness is Stephen's file (raised through «#3515»).

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

**Fixed in tree 2026-09-16 («#3556»).** `getMaxSpeedForDistance()` (`src/isp_steering_2wheel.spin2:769-775`)
now calls `rtWheel.getMaxSpeedForDistance()`, matching `driveForDistance()`'s own call. The serial
object was not checked for the same getter -- out of this task's scope.

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

**Fixed in tree 2026-09-16 («#3556»).** *(Aged-state sweep 2026-09-17: no cell isolates `getPower()`
after a stop; Visit 5's t0 certifies the error contract it rides on, not this getter. It stays
certified by construction only.)* The rule: `getPower()`
reads 0 whenever the front cog has left the motor commanded to stop. The line numbers above predate
the front cog («#3513»).
- **Writers:** `motorPower` is written by `frontDrive()` (a commanded power) and by the stop paths:
  `frontZeroPower()`, `frontEStop(TRUE)`, `frontSecure()` and `stop()`.
- **Stops that zero it, in both objects:**
  - `REQ_STOP`
  - the distance/rotation/time limits
  - the e-stop
  - a synced command the driver did not take (`ERR_SYNC_TIMEOUT`)
- **While FAULTED** it keeps the last commanded power: nothing commanded a stop.
- **Exception:** `REQ_TEST_INCREMENT` writes a raw increment, not a power, and leaves it unchanged; its
  doc says so.

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

**SUPERSEDED 2026-09-17 by PL-89** (read its correction box first). The polarity argument above stands
and settles PL-89's "one link". What moved is the disposition: STEPHEN 2026-09-17, *"isn't there a set*()
which specifies motor stop condition? so user would select it for their application"*. `holdAtStop()`
IS that selection, so the fix is that **every stop path -- at rest, on a fault, and on an e-stop per its
own documentation -- delivers the user's selection**. That is an API-contract fix (doctrine overlay P3),
not a behaviour question, and his hand test certifies it afterwards.

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

**Doc corrected in tree 2026-09-16 («#3556»).** `holdAtStop()` and `stopMotor()`/`stopMotors()`
doc comments (`src/isp_bldc_motor.spin2:681-686`, `:879-882`; `src/isp_steering_2wheel.spin2:279-284`,
`:551-554`) now say hold-or-release is chosen once AT REST, and every stop from speed follows the
driver's own ramp regardless of the setting, citing the Visit 2 measurement. `DRIVE-OBJECTS.md`
stays owed to «#3514»/«#3515» -- out of this task's DOCs scope.

### PL-59 -- POSTFLT's 3° offset does not provoke a fault at half speed, so the post-fault stop is unmeasured

> **FIXED IN THE HARNESS 2026-09-17, night («#3572»); build gate green 2026-09-18; run-time proof owed to Visit 6.**
> POSTFLT's `EVT_OFFSET` now shifts both of the wheel's offsets by the computed `faultShiftDeg()` at speed -- the
> construction in PL-86's box, direction-independent because it reads the wheel's own error. `FAULT_PROVOKE_NEG_DEG`
> is deleted. The post-fault stop is judged by the new `R17-DUAL-FLTSTOP-C` (a FLOAT fault coasts at least 10 ticks
> further to rest than a BRAKE fault; the old driver shorted on every fault, so it fails there).

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

**IN THIS RELEASE (aged-state sweep 2026-09-17)** as part of fault handling (STEPHEN 2026-09-17, *"fix fault
handling"*). It is the same need as PL-86: one provocation that faults on today's lag-limited driver under the
harness's 10 A abort. S-9a's question is now "does a fault deliver the user's `holdAtStop()` selection" (PL-89).

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

**Explained (aged-state sweep 2026-09-17; DERIVED from MEASURED):** duty saturates at `duty_max` from about
120M, so the applied phase voltage stops rising while back-EMF keeps rising with speed; the difference that
drives current shrinks and current collapses, as a lifted wheel needs almost no torque. Visit 5 shows the same
shape: current peaks at ~6.7 A at rung 6 and falls as speed rises, with `duty` pinned at 24_264 from rung 7
(`analyses/bench/2026-09-17/VISIT-5-RESULTS.md` §5b). **Top speed unloaded is set by bus voltage, not current.**
What stays open is PL-26's part: whether a correct lead angle at speed moves that point.

**Fix direction:** explain it from source before any change to the ceilings. It bears directly on
PL-26's commutation-angle question (lead angle at speed) and on the published speed limits.

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

**Status (aged-state sweep 2026-09-17): FIXED IN TREE, NOT YET RUN.** The rebuild (SRC_REV 12) is re-walked
against source in `analyses/ATTENDED-UI-AUDIT-2026-09-15.md` §7: the verdict has its own strip, STOP is live
whenever a wheel is driven, every countdown is labelled, a heartbeat shows a silent P2. No attended load has run
since (Visit 3 did not carry the pair; Visits 4-5 were unattended). **It certifies at the next attended visit**,
which now exists: the spin-in-place floor run STEPHEN approved on 2026-09-17 needs `dual-ui` first.

### PL-65 -- `BM-PLAN` names the wrong findings for the UICHECK and FLOOR parts

**Found 2026-09-15 in Visit 2** (`analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §3). Minor.

**MEASURED:** UICHECK's plan record says `finds AC` (`debug_260915-142103.log:26`); FLOOR's says `finds S-9a`
(`debug_260915-142650.log:26`).

**DERIVED:** FLOOR is the part that finds AC, and UICHECK finds none; S-9a belongs to part C.

**Fix direction:** correct the two labels in `src/test_bench_dual.spin2` at its next revision.

**FIXED IN TREE (aged-state sweep 2026-09-17):** `tokFinds` carried one extra S-9a, shifting FLOOR and UICHECK
by one; corrected in the SRC_REV 12 rebuild (`analyses/ATTENDED-UI-AUDIT-2026-09-15.md` §7). Visible in the
next attended log's `BM-PLAN`.

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

**Fixed in tree 2026-09-16 («#3556»). Run-time proof STILL MISSING (aged-state sweep 2026-09-17):**
`R16-DUAL-FLTRETRY-B` was NOMEAS at Visits 4 and 5 because the fault provocation trips the harness's own
10 A abort first (PL-86). IN THIS RELEASE with fault handling. Decided by Stephen's
2026-09-16 API rule: a retry restarts the motor.

**Where the fix lives, and why.** The fault-clear edge is made in the front cog, not the driver.
`drvMotor` copies `tgt_incr` into `sv_tgt_incr` every pass, so its "same request" compare means "the
command is still standing". An edge taken there would clear a fault on the very next pass, and the
fault would never latch. The PASM is unchanged.

**What happens on a drive while FAULTED.** `frontClearFault()`, called from `frontDrive()`, runs
first. It writes a zero command, and waits a bounded `FRONT_SYNC_WAIT_PASSES` drive passes for
`drv_state` to leave `DCS_FAULTED`. A zero request reaches `.newRqst` -> `.resetFault` in one pass.
- On success, the requested command is written.
- On expiry, it returns `ERR_NO_RESPONSE` and the zero stays written.
- The wait is counted in `bDidWait` and in `requestWaits()`.

**Two wheels.** `frontDriveWheels()` clears both selected wheels before writing either. If either
fails, both are zeroed. Invariant: *a platform never drives one selected wheel while refusing the
other.*

### PL-68 -- no bench log names the commit it was built from, so a visit ran on an older commit unnoticed

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

### PL-69 -- illegal hall codes on the right motor at 200 MHz, none at 270 or 300

**Found 2026-09-16 in Visit 3** (`analyses/bench/2026-09-16/VISIT-3-RESULTS.md` §1).

**MEASURED (`debug_260916-123557.log:57,63`):**
- `BM-RUNG3 … motor RIGHT … illegal_d 3` (NEG 75M) and `illegal_d 5` (POS 75M), each in one 1-second, 201-tick
  window.
- `missed_d` 0 in both. The instrument's independent hall count agrees with `pos` (`hw_ticks` ±201, `hw_skip` 0).
- LEFT at 200 MHz: 0 and 0. Both motors at 270 MHz (`…123637.log`) and 300 MHz (`…123717.log`), ten and thirty
  seconds later: 0. Every Visit 1 and Visit 2 hold at 270 MHz: 0.

**What it does and does not establish (DERIVED):**
- The driver's hall read entered %000 or %111 eight times on one motor at one clock; the position count was not
  harmed.
- It does not establish that the clock is the cause. It is one run, and the same motor read clean at the next
  clock. The condition may be transient: a connector, or a read landing on a hall edge (doctrine D2).
- 200 MHz is not the library's default clock (270 MHz).

**Fix direction:** none yet. Before any code change, name what would distinguish a clock-dependent sampling
edge from a transient: the illegal count is already in every rung record, so the next clock load answers it
for free.

**IN THIS RELEASE (aged-state sweep 2026-09-17):** STEPHEN 2026-09-17, *"fix hall and charaterize"*. The hall
input network is on file (`analyses/BOARD-REVISION-FACTS.md` §1.1: 3.9 kΩ pull-up to 3.3 V and 3.9 kΩ series,
identical on Rev A and Rev B; STEPHEN confirmed 2026-09-17). ⚠ PL-90's torn-read mechanism cannot by itself
produce `%000`/`%111` -- see the correction to PL-90 when the hall work starts. Work and characterisation plan:
the hall task, not this entry.

### PL-71 -- the DocoEng motor's minimum forward increment is `0 - VALUE_NOT_SET`, which is 1

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

### PL-73 -- a board that fails detection drives with no current limit

**Found 2026-09-16 in «#3557»'s design** (`DOCs/plans/CURRENT-LIMIT-AND-STOP-DESIGN.md` §3.6). DERIVED from source.

The fold-back and derate limits are converted to millivolts through `rSenseForBoard`. When board detection
fails, `rSenseForBoard` is `VALUE_NOT_SET` (`src/isp_bldc_motor.spin2`, `init()`), so no scale exists to convert
them, and the design sets `i_limit_k` so the test is never met: the motor drives unprotected. `start()` does not refuse
an undetected board today, and changing that is an API contract change.

**Fix direction:** decide whether `start()` refuses a board it cannot detect (a new `ERR_*`), or drives with a
conservative limit computed at the less sensitive Rev A scale (5 mV/A), which errs toward folding back early on
Rev B.

**DECIDED, STEPHEN 2026-09-17 ("yes to all"), IN THIS RELEASE:** `start()` refuses a board it cannot detect with
the existing `ERR_BOARD_NOT_DETECTED`, unless the user has forced a revision (`BRD_REV_A` / `BRD_REV_B`), in
which case the forced revision's scale sets the limit.

**FIXED IN SOURCE 2026-09-17 («#3570»), run-time proof owed to Visit 6.** The refusal is in `launchDriver()`, the
path every start takes (`start()`, `startEx()`, and `startOwned()` under the steering object), after
`setupForStart()` and before any cog is launched: an auto-detect that found no board `stop()`s (releasing the
claim and the pins) and records `ERR_BOARD_NOT_DETECTED`. It is deliberately NOT in `setupForStart()`, so
`testSetup()` still initialises an empty group for the detection cells (`R2-T0-EMPTY`, `R16-T0-NOBOARD`). The
certifying cell is `R17-T0-NOBOARDSTART` (t0 `T0-23`, SRC_REV 4): a start on the empty P0 group must return -1
with the code, take no cog and release the claim; on the unfixed library the start succeeds, so the cell FAILs.

### PL-76 -- `driveAtPowerEx()` reports "motor not started" immediately after a `start()` that succeeded

**Found 2026-09-17 in «#3561»**, Visit 4 part D. **MEASURED**,
`DOCs/analyses/bench/2026-09-17/debug_260917-125859.log` L86-95, in order:

```
L86  BM-START seg,LIMIT motor,LEFT life,5 cog_ret,3 cog_ok,TRUE board,REV_B ready,TRUE ... why,NONE
L87  ! ERROR: driveAtPowerEx() motor not started
L88  ! ERROR: driveAtPowerEx() motor not started
L91  ! ERROR: clearEmergency() not cleared eError = -1_007
L93  ! ERROR: driveAtPowerEx() motor not started
L94  ! ERROR: stopAfterTime() rejected eError = -1_007, nTime = 2_000, eTimeUnits = 1
L95  BM-DSTEP step,TIMESTOP motor,LEFT ... result,NOMEAS why,STOP_TIMEOUT
```

`start()` returned cog 3 with `cog_ok,TRUE`, `ready,TRUE` and `why,NONE`, and the very next `driveAtPowerEx()`
call says the motor is not started.

**This is an API-contract defect of the class doctrine overlay P3 names:** a member that does not keep the
promise its name and its documentation make. Under P3 it is fixed, not parked as a question -- what stays with
Stephen is only a choice between two clean readings, and there is no second clean reading of "started, but not
started".

**What it costs.** Three cells lost to it, all reported as NOMEAS rather than as passes:
`R16-DUAL-TIMESTOP-D` (BOTH, L108), `R16-DUAL-WTIMSTOP-D` (LEFT, L117), and the `STOP_TIMEOUT` behind both.

**Not yet determined:** whether the `-1007` from `clearEmergency()` shares this root cause or is a second
defect. **Fix direction:** read the started-state predicate in `src/isp_bldc_motor.spin2` and the single-motor
path through the front cog. No bench cell is proposed for it -- the bench certifies, it never engineers (P10).

> ## SOURCE READ 2026-09-17 -- the refusal is BY DESIGN, so the defect is upstream of it. And three cells passed anyway.
>
> **The predicate, verified in source.** `driveAtPowerEx()` (`src/isp_bldc_motor.spin2:787-790`):
>
> ```spin2
>     if senseCog == 0
>         ' started means the driver and the front cog both run, and only the front cog commands the driver
>         eError := recordError(ERR_NOT_STARTED)
> ```
>
> `ERR_NOT_STARTED` is **-1_007** (`:92`), which is exactly the code `clearEmergency()` and
> `stopAfterTime()` also returned -- **one cause, not three.**
>
> **`senseCog` is written in exactly one place:** `launchFront()` at `:417`. `launchDriver()`
> (`:359-392`) sets only `motorCog`. **So a start path that launches the driver WITHOUT a front cog
> leaves every drive call correctly refusing** -- which is the documented contract, not a defect:
> only the front cog commands the driver.
>
> ⛔ **So the defect is not in the refusal. It is in whatever started that instance.**
>
> ### RESOLVED 2026-09-17 -- HARNESS DEFECT. The single-wheel half commands a stopped steering object.
>
> **The chain, every link verified in source:**
>
> 1. **The harness used the full `start()`.** `test_bench_dual.spin2:6501`:
>    `stCogRet := wheelL.start(LEFT_TEST_BASE, TEST_VOLTAGE, TEST_DET_MODE)`.
> 2. **That start fully succeeded.** `startEx()` sets `ok := motorCog - 1` **only** after
>    `launchFront()` returns `NO_ERROR` (`isp_bldc_motor.spin2:166-171`), and `launchFront()` calls
>    `stop()` on any failure (`:415, :426`). So `cog_ret,3` **proves the front cog launched and
>    `senseCog` was set.** `wheelL` was properly started and could be driven.
> 3. **`wheelStart()` stops the steering object first.** `test_bench_dual.spin2:6491-6493`:
>    `steerStop()`, then `wheelStopRaw(SIDE_LEFT)`, then `wheelStopRaw(SIDE_RIGHT)`.
> 4. **But the LIMIT segment's step helpers command through `steering.`, not through the wheel.**
>    `dProtectiveStop()` calls `steering.getProtectiveStop()` (`:4288`), `dClearProtective()` calls
>    `steering.clearProtectiveStop()` (`:4297`), and the `dDrive()` / `dClearEstop()` family are the
>    same shape. `dLimitRestore()`'s own comment (`:4300-4302`) confirms the segment has a steering
>    half **"before the single-wheel half runs"**.
> 5. **The steering object's wheels return `ERR_NOT_STARTED` by contract.** `startOwned()`'s
>    doc-comment states it outright: *"Commands on this instance itself return ERR_NOT_STARTED"*
>    (`isp_bldc_motor.spin2:177`).
>
> ⭐ **The error count confirms it.** A `steering.` drive fans out to **both** internal wheels, so
> each refused call prints **two** error lines -- which is exactly what the log shows at `:87-88`.
> A defect in `wheelL` itself would print one.
>
> **So no driver defect exists here.** `wheelL` was started, had a front cog, and would have driven.
> **The single-wheel half of part D's LIMIT segment simply never commanded it** -- it kept calling
> through the steering object that `wheelStart()` had just stopped.
>
> **Fix direction (harness, ours):** the single-wheel half takes wheel-scoped helpers that command
> `wheelL` / `wheelR` directly, or `wheelStart()` does not run for a segment whose steps are
> steering-scoped. **Correct by construction (P10):** a step helper should not be able to address an
> object the segment has stopped -- pass the target in rather than letting the helper choose.
>
> *Consistent with everything else in the run:* PREFLT started each wheel and then drove it through
> wheel-scoped calls, and moved (`BM-PREFLT ... moved,TRUE`); part A's ladder did the same across 24
> lifecycles. Only this half of this segment mixes the two scopes.
>
> **Hypothesis raised and REFUTED, recorded so it is not raised again:** the error line renders as
> `driveAtPowerEx() motor not started` with an **empty** motorId, which looked like an
> uninitialised instance. It is not -- `init()` sets `byte[@motorId] := 0` deliberately, *"terminate
> an empty string"* (`:454`). An empty id is the normal state for an instance nobody named.
>
> ### ⛔ WITHDRAWN 2026-09-17, same day: "three cells PASSED on a dead motor" is REFUTED
>
> **I was wrong, and the source says so plainly.** `dStepEstopSet()`
> (`test_bench_dual.spin2:3862-3866`) opens with:
>
> ```spin2
>     bAtSpeed := bArmed and dToSpeed(side)
>     if bAtSpeed == FALSE
>         dStepSkip(DST_ESTOP_REFUSE, side, bArmed ? WHY_NOT_REACHED : WHY_INST_NOACK)
>         dStepSkip(DST_ESTOP_LATCH,  side, ...)
>         dStepSkip(DST_ESTOP_CLEAR,  side, ...)
>     else
> ```
>
> **The positive limb IS established first.** All three cells are SKIPPED, as NOMEAS with a why,
> unless the platform actually reached speed. They cannot pass on a motor that never moved, which is
> exactly the property I claimed was missing.
>
> **So the PASSes mean the motor DID reach speed** -- `dToSpeed()` drives and waits for
> `DCS_AT_SPEED`, and returns FALSE if the drive returns anything but `NO_ERROR`
> (`:3718-3724`). **The single-motor e-stop limb is therefore certified after all**, and the
> withdrawal I recorded in the Visit 4 report is itself withdrawn.
>
> ⚠ **What genuinely remains unexplained, stated as an open question rather than a finding.** Two
> `driveAtPowerEx() motor not started` lines and one `clearEmergency() ... -1_007` appear in that
> segment, between the start and the cells that passed. Since the cells passed, those errors came
> from calls the cells do not depend on -- **and I have not identified which.** Worse,
> `ESTOP_CLEAR` recorded `measured,0` (`NO_ERROR`) on the line after a `clearEmergency()` printed
> −1_007, so either a different object printed it or an error was aggregated away between the inner
> call and the outer return. **An error nothing catches is still a finding**; I simply do not yet
> know whose.
>
> ⛔ **Do not reconstruct a story for it.** Two attempts today built plausible mechanisms that the
> next read refuted. The next step is to identify the emitting call, not to infer it.
>
> ### ⭐ EMITTING CALL IDENTIFIED 2026-09-17, BY READING. It is PL-29's ternary, measured a second time.
>
> **The three commanding dispatch helpers selected their object with `? :`:**
>
> ```spin2
> eError := (side == SIDE_RIGHT) ? wheelR.driveAtPower(powerValue) : wheelL.driveAtPower(powerValue)   ' dDrive()
> eError := (side == SIDE_RIGHT) ? wheelR.clearEmergency() : wheelL.clearEmergency()                   ' dClearEstop()
> eError := (side == SIDE_RIGHT) ? wheelR.stopAfterTime(...) : wheelL.stopAfterTime(...)               ' dStopAfterTime()
> ```
>
> **PL-29 MEASURED that a `? :` whose two branches each call a method RUNS BOTH CALLS for one
> evaluation.** With `side` SIDE_LEFT, every one of these also commanded `wheelR` -- which the LIMIT
> segment's single-wheel half never started -- so `wheelR` refused, **printed**, and the expression
> nonetheless returned `wheelL`'s value. The cell got the right answer; the log got a stray error line.
>
> **THE CORRESPONDENCE IS EXACT, and that is the evidence.** Five error lines, five commanding-ternary
> calls in the wheel half, in order (`debug_260917-125859.log`, with its timestamps):
>
> | Line | t | The call | wheelL returned |
> | --- | --- | --- | --- |
> | L87 | 12:59:43.914, the same ms as BM-START | `dToSpeed()`'s drive, in `dStepEstopSet` | NO_ERROR -- it reached AT_SPEED 2.3 s later |
> | L88 | 12:59:46.227, 16 ms before the cell | the refused drive, `dStepEstopSet` step 1 | ERR_EMERGENCY_STOPPED -- ESTOP_REFUSE PASS |
> | L91 | 12:59:48.053, between LATCH and CLEAR | `dClearEstop()`, `dStepEstopSet` step 3 | NO_ERROR -- ESTOP_CLEAR PASS |
> | L93 | 12:59:48.860 | `dToSpeed()`'s drive, in `dStepTimeStop` | NO_ERROR |
> | L94 | 12:59:51.186 | `dStopAfterTime()` | NO_ERROR |
>
> **And the negative limb is in the same log.** The steering half (`SIDE_BOTH`) takes the `if` limb and
> evaluates no ternary: it makes far more library calls than the wheel half and prints **no** error at all
> (L58-L69). Parts A, B and C command through the `wheel*()` wrappers, which are `if`/`else` throughout,
> and print none either. The getter ternaries (`dRawTicks`, `dPowerSum`, `dIsEstopped`, `wheelIsReady`,
> `wheelIsUp`, `wheelRpm`) behave the same way; they merely say nothing about it.
>
> ⭐ **This also explains the `-1_007` beside a PASSing `ESTOP_CLEAR`** -- the entry's own open question
> above. Nothing was aggregated away: two different objects answered, and only one of them was printed.
>
> ### FIXED IN TREE 2026-09-17 -- eleven sites, and the rule is stated where the next one would be written
>
> Every `? :` in `test_bench_dual.spin2` that selected between two METHOD CALLS is now `if`/`else`:
> `dDrive`, `dClearEstop`, `dStopAfterTime`, `dResetTracking`, `dIsEstopped` (two), `dPowerSum`,
> `dRawTicks`, `dTrackTicks`, `wheelIsReady`, `wheelIsUp`, `wheelRpm`. A `? :` that selects a **value** is
> untouched and correct. The rule, its evidence and the correspondence table above are written into the
> part-D dispatch header so the next helper is written the right way round (P10: the construction, not a
> reminder).
>
> **The sweep covered the two dispatch families** -- the `d*()` part-D helpers and the `wheel*()` wrappers
> -- which is where every library call on a side-selected object goes. A residual elsewhere in the file is
> possible and is **not** claimed to be absent; the durable answer is a checker rule, and that belongs to
> «#3517» (see PL-29).
>
> ⚠ **This does NOT explain the lost TIMESTOP cells.** `R16-DUAL-TIMESTOP-D` (BOTH) read
> NOMEAS/STOP_TIMEOUT in the STEERING half too, which evaluates no ternary. That is a separate criterion
> defect and it is filed as **PL-83**.
>
> *(The original claim is preserved below as written, per this list's convention of keeping what was
> said and dating what overturned it.)*
>
> ### THE CLAIM AS ORIGINALLY FILED -- three cells PASSED in a segment where the motor was never started
>
> **MEASURED**, `bench/2026-09-17/debug_260917-125859.log:89-92`, interleaved with the errors:
>
> ```
> :89  BM-DSTEP step,ESTOP_REFUSE motor,LEFT seg,LIMIT measured,1     lo,0     hi,50    result,PASS
> :90  BM-DSTEP step,ESTOP_LATCH  motor,LEFT seg,LIMIT measured,1_500 lo,1_500 hi,1_500 result,PASS
> :91  ! ERROR: clearEmergency() not cleared eError = -1_007
> :92  BM-DSTEP step,ESTOP_CLEAR  motor,LEFT seg,LIMIT measured,0     lo,0     hi,0     result,PASS
> ```
>
> **`ESTOP_CLEAR` reports PASS on the line immediately after the clear it is testing returned an
> error.** All three e-stop cells pass on a motor that was never started and could not move.
>
> **That is a gate that cannot fail** (doctrine D2: a control that cannot exhibit the difference
> proves nothing; a check must be able to fail on the thing it names). A motor that is refusing
> every command trivially satisfies "did not move when e-stopped" and "is at rest after the clear".
> **These cells measure absence of motion without establishing that motion was ever possible.**
>
> ⚠ **This casts doubt on the LEFT-motor e-stop rows of the Visit 4 report**, which recorded
> `R16-DUAL-WESTOP-D` PASS. The BOTH-motor e-stop evidence from STEERSEG (`:61-63`) is unaffected --
> that segment drove successfully. **The single-motor e-stop limb is not certified**, and the
> report's §3 table should say so.
>
> **Fix direction:** every e-stop cell first establishes the motor is moving -- a positive limb --
> and only then asserts the stop. A cell whose criterion is satisfied by a dead motor is measuring
> the wrong thing (compare PL-79, PL-80, PL-82: **a criterion is an instrument and needs its own
> negative case**).

### PL-77 -- `BM-DISTM` metres read ~1000x low and sign-inverted

**Found 2026-09-17 in «#3561»**, Visit 4 part B. **MEASURED**,
`DOCs/analyses/bench/2026-09-17/debug_260917-130012.log` L7547:

```
BM-DISTM l_ticks,2_688 r_ticks,2_688 l_m,-14_640 r_m,-14_640 l_pred_m,15 r_pred_m,15 mm_x100,576 agree,FALSE
```

**DERIVED:** `mm_x100 576` is 5.76 mm per tick, so 2 688 ticks is **15 483 mm = 15.48 m**, against
`l_pred_m 15`. The magnitude is therefore *correct* -- `l_m` is carrying **millimetres in a field the record
and the criterion both read as metres** -- and the **sign is additionally inverted**. Two independent faults in
one reading, which is why `R16-DUAL-DISTM-B` reads `METRES_AGREE FALSE` (L7573).

**Undetermined, and it matters which:** whether the fault is in the driver's `DDU_M` conversion or only in the
harness record that reports it. Both motors read identically, which does not discriminate.

**What it costs beyond the cell.** «#3515» already carries a 6.0.0 release line saying `stopAfterDistance` with
`DDU_M` "stops ten times further, i.e. correctly". **That promise does not survive this measurement** and must
be re-checked against the source before it ships in the README (doctrine overlay P8: a written record is a
claim, and the measurement outranks it).

> ## RESOLVED TO THE HARNESS 2026-09-17 -- the driver is correct. Two harness defects confirmed; the magnitude is undiagnosable BY CONSTRUCTION.
>
> **The source read this entry named as its discriminator has been done. THE DRIVER IS NOT AT FAULT.**
>
> **Eliminated, each verified in source:**
>
> | Candidate | Finding |
> | --- | --- |
> | The motor object's `DDU_M` arm | **correct** -- `round(fValue /. 1000.0)`, `src/isp_bldc_motor.spin2:1041-1043` |
> | The steering object's `DDU_M` arm | **correct** -- `round(fValue /. 1000.0)`, `src/isp_steering_2wheel.spin2:743-744` |
> | The `DDU_M` enum alias | **correct** -- `DDU_M = ltWheel.DDU_M`, `isp_steering_2wheel.spin2:43` |
> | Which object the harness calls | **correct** -- `steering : "isp_steering_2wheel"` (`test_bench_dual.spin2:1002`); the call is `steering.getDistance(steering.DDU_M)` (`:3268`) |
> | `tickInMM_x100`'s scale | **correct** -- `wheelGeometry()` yields 576 for the 6.5", and the steering captures that same value at `isp_steering_2wheel.spin2:204` |
>
> **CONFIRMED HARNESS DEFECT 1 -- the sign belongs to the harness, not the driver.**
> `ticksToMetres()` (`test_bench_dual.spin2:3260`) computes
> `(abs(nTicks) * tickMmX100 + ...) / MM_PER_M_X100`. It takes **`abs()`**, so the prediction is
> always positive, while the library's getter is **signed** and these trials ran negative. The two
> sides disagree in sign by construction, on every trial.
>
> **CONFIRMED HARNESS DEFECT 2 -- the two sides are NOT from the same instant, and the code claims
> they are.** At `:3241-3244` the harness sets `dmLeftTicks := ovLeftTrk`, a **snapshot** saved by
> the overshoot trial, then calls `steerDistanceM()`, a **live** read of
> `ltWheel.getposTrkHallTicks()`. The emitter's comment at `:8242-8244` states: *"Both sides come
> from the same instant, so the comparison is of the conversion alone."* **That comment is false**,
> and it is why the cell cannot do what it claims.
>
> ⛔ **Why the ~1000x magnitude cannot be settled from this log, and why that IS the finding.**
> `l_m` is consistent with the millimetre figure for roughly 2 541 ticks, against `l_ticks 2_688`
> from the snapshot -- but **the cell never records the tick count the getter actually read.** There
> is therefore no way to separate a conversion fault from two reads taken moments apart. **The cell
> is undiagnosable by construction: it prints its prediction's input and not its measurement's
> input.** Further inference from the arithmetic would be speculation, so it stops here.
>
> **Fix direction (harness, ours, correct-by-construction -- P10):** take both sides from a single
> read of the tick counter, as the comment already promises; **record that tick count in the
> record**; drop the `abs()` so predicted and measured carry the same sign. The cell then either
> agrees or names a real conversion fault, and its own record says which.
>
> ⭐ **CONSEQUENCE FOR THE RELEASE.** The «#3515» line above is **no longer blocked by this entry** --
> both `DDU_M` arms are verified correct in source. It is still **not bench-certified**, because
> this cell could certify nothing. Say that plainly rather than citing Visit 4 as support.
>
> ### FIXED IN TREE 2026-09-17 -- both harness defects, in the three lines that carried them
>
> - **One read, and the record carries the measurement's own input.** `overshootFoldCells()` no longer
>   takes the ticks from `ovLeftTrk` / `ovRightTrk`, the snapshot the overshoot trial saved earlier. It
>   calls `steerTrackTicks()` immediately before `steerDistanceM()`, and `dmLeftTicks` / `dmRightTicks`
>   -- the `l_ticks` / `r_ticks` the record prints -- are now the counts the getter saw. The emitter's
>   comment, which claimed that and was false, now says it and is true.
> - **The conversion is signed.** `ticksToMetres()` no longer takes `abs(nTicks)`; it carries the sign,
>   with the rounding term applied away from zero on both limbs so a reverse trial is not biased by a
>   metre. Every reverse trial used to disagree with its own prediction by construction, whatever the
>   conversion did.
>
> **The ~1000x magnitude remains undiagnosed and that is the point of the fix:** the cell could not
> separate a conversion fault from two reads taken moments apart, so nothing could be concluded from
> Visit 4's reading. It can now, and the next visit's `BM-DISTM` either agrees or names a real fault with
> both of its inputs in the record.
>
> ### ⭐ AND THE MAGNITUDE IS NOW EXPLAINED, hours later, by PL-84 -- it was neither of those
>
> **It was not the conversion and it was not two reads: the steering object's own `tickInMM_x100` held
> about -544_643.** `convertDistance()` multiplies by it, so -14_640 from 2_688 ticks is exactly that
> value, and the SAME number makes `driveForDistance()` refuse every trial in the segment. **One value,
> both the magnitude and the sign.** Arithmetic and log lines: **PL-84**.
>
> ⚠ **The two harness defects this entry fixed were real and the fixes stand** -- the `abs()` and the
> snapshot-versus-live read were both there, and either alone would have kept the cell from certifying.
> They were simply not the whole of what Visit 4 measured. What was missing was the field that could
> show the third thing, and PL-84 adds it.

### PL-78 -- the lag error clamps at 115-116 against a 110 bound, and commanded velocity is not rate-limited (the slam)

> **STATUS 2026-09-18 («#3573»):** the first half (`LAGBND`) is certified at Visit 5. The second half -- the slam --
> is judged at Visit 6 by `R17-DUAL-TRKICK-A` on the new `BM-RUNGTR` transition record (PL-87's box). A source
> re-read of the speed-change entry found no further construction defect for a same-sign speed-up: the
> `.doSpdChange` ramp reset is the only inherited state, and it is in the binary. If TRKICK fails, the failing
> transitions' `incre` pairs name which path to read next (speed-up, ramp-down, or direction change via
> `.slow2Chg`); the driver comment no longer cites the withdrawn Visit 4 `err_pk` table as evidence.

**Found 2026-09-17 in «#3561»**, Visit 4, all four dual parts. This entry carries both the failing cell and the
physical effect Stephen reported, because the open question is whether they are one finding or two.

**MEASURED -- `R16-DUAL-LAGBND` `MAX_ABS_ERR`, bound `lo 0 hi 110`, `sat 127` in every record:**

| Part | LEFT | RIGHT | samples (L / R) | Log |
| --- | --- | --- | --- | --- |
| A | **115** | **115** | 63 947 / 63 998 | `debug_260917-131445.log` L15301-15302 |
| B | **115** | **115** | 19 761 / 19 862 | `debug_260917-130012.log` L7574-7575 |
| C | **116** | **116** | 19 933 / 19 922 | `debug_260917-131237.log` L5621-5622 |
| D | **115** | 87 | 3 293 / 2 308 | `debug_260917-125859.log` L119-120 |

**«#3558»'s lag limiter is working:** the measurement never reaches `sat 127`, which is where the unfixed driver
pegs the stored `err` field.

**DERIVED -- the number is too repeatable to be a transient.** 115 / 115 / 115 / 115 / 116 / 116 / 115
across four parts with completely different motion profiles, sample counts from 2 308 to 63 998, and both
motors. A peak driven by motion would scatter. Part D's RIGHT reaching only 87 fits: it is the shortest run and
never demanded enough.

**SETTLED FROM THE SOURCE 2026-09-17, and it makes this an INSTRUMENT defect, not a driver defect.**
`src/isp_bldc_motor.spin2:3344-3346`:

```spin2
    ' C-5 (DOCs/plans/CURRENT-LIMIT-AND-STOP-DESIGN.md section 3.2): lag thresholds, err_ units (256 per hall cycle)
    LAG_SOFT                    = 80        ' 112.5 deg: the ramp waits for the rotor; the PL-55 duty ceiling lifts
    LAG_HOLD                    = 100       ' 140.6 deg: the field stops advancing (the fault test is at 125)
```

and `src/isp_bldc_motor.spin2:3803-3804`:

```spin2
.justIncr   ' just do our increment of angle and we're done!
                cmps    lag_s, #LAG_HOLD            wc  ' C-5: the field advances only while the rotor trails it by
    if_c        add     angle_, drv_incr                '  less than LAG_HOLD, so |err_| stays under the 125 fault test
```

**The clamp is at 100, not at 115.** The test is taken on `lag_s` sampled at the *top* of the pass
(`:3560`), and the field then advances by one whole `drv_incr` before the next test. So the largest `err_` any
sampler can observe is **`LAG_HOLD` plus one pass's field advance**, and at the ladder's top rung that quantum is
roughly 15-16 err units -- which is exactly the 115-116 measured, and exactly why it barely moves between parts.

⛔ **The 110 bound was therefore wrong, not the driver.** It was written as `LAG_HOLD + 10`, under-estimating
the one-pass quantum at `ladder_max 165_000_000`. The driver is doing precisely what C-5 designed it to do, and
the fault test at 125 is still never reached -- which is the property that actually matters.

**Fix direction:** set the bound from the design, not from a round number: `LAG_HOLD` plus the maximum per-pass
field advance at `ladder_max`, computed rather than guessed, with the 125 fault threshold as the hard ceiling the
cell really guards. **This is the one case where raising the bound is correct** -- not because it turns the cell
green, but because the old bound described a state the design never promised. Record the arithmetic in the cell
so the next reader can check it (doctrine D2: a criterion that cannot be met by a correct system has not passed,
it has misreported).

> ## ⛔ CORRECTED 2026-09-17, BEFORE THE FIX WAS BUILT: "LAG_HOLD + one pass ~= 15-16" DOES NOT COMPUTE.
>
> **The arithmetic is checkable and it fails.** `err_` is `(hall angle + offset) - angle_` shifted right
> by 24 bits (`src/isp_bldc_motor.spin2`, the `.noFault` block), so **256 units make one electrical
> cycle**, and the design document states the same conversion and works it out:
> *"At the 6.5in ceiling of 172,000,000 it advances `angle_` by 10.25 units per drive pass. At 75 %
> (110,250,000) it advances 6.57 units"* (`plans/CURRENT-LIMIT-AND-STOP-DESIGN.md`, Units). At the
> ladder's own top rung, 165,000,000, the advance is **9.8 units**, not 15-16.
>
> ⛔ **And the measurement refutes the model outright: part A (a ladder to 165,000,000) and part D (a
> steady power 50, where the advance is a fraction of that) BOTH read 115.** A bound generated from the
> per-pass advance would differ by several units between those two parts. It does not. **So the gap
> between `LAG_HOLD` 100 and the observed 115-116 is UNDETERMINED** -- that is a deliverable, not a gap
> (doctrine overlay P8), and it is recorded here rather than filled with a mechanism.
>
> The design's own invariant is written the same way and is equally not what is observed:
> *"`|err_|` cannot exceed `LAG_HOLD` plus one pass's increment (100 + 10.25 < 125)"* (section 3.2). The
> **conclusion** of that sentence holds -- `|err_|` stays under the 125 fault test, in every part, on both
> motors -- and its arithmetic does not generate the 115. Only the conclusion is used.
>
> ### FIXED IN TREE 2026-09-17 -- the bound is the driver's own fault test
>
> `LAG_MAX_HI` is now `LAG_FAULT_TEST - 1` = **124**, with `LAG_FAULT_TEST = 125` named and sourced to the
> driver's `cmp tmpY, #125 wc`. That is the only number here the design actually promises, it is what the
> lag limiter exists to guarantee, and **it has a real negative case**: a driver with no limiter pegs the
> stored field at its 127 saturation and fails it. `LAG_HOLD_REF = 100` is carried alongside, and
> `BM-LAG` now prints `hold` and `fault` beside `max_err` and `hi`, so the whole band is in the record and
> a reading between the gate and the criterion reads as the normal state rather than as a near-miss.
>
> **What is NOT claimed:** that 115 is now explained. It is bounded, and the bound is sourced. If a future
> visit reads a `max_err` that walks toward 124, the record now carries every number needed to see it.

**STEPHEN 2026-09-17, the physical effect:** *"On your dual A run, you're making a bunch of speed changes. One of
the things I noticed in the speed changes is that we are physically slamming the platform... I would think speed
changes should be really smooth, but they're not, so we need to understand what this effect is."*

**MEASURED -- the slam's signature**, `debug_260917-131445.log` L15170-15205, `BM-RUNG2` LEFT forward:

```
rung     0    1    2    3    4    5    6    7    8    9   10   11
err     34   48   48   48   49   48   48   55   63   65   68   73
err_pk  56   75   71   71   72   72   73   80   88   91   94   98
gap     22   27   23   23   23   24   25   25   25   26   26   25
```

**`err_pk` sits ~25 counts above the steady `err` at every rung change, independent of step size.**

**THE MECHANISM, SETTLED FROM THE SOURCE 2026-09-17. It is NOT a missing ramp.** The ramp is applied to every
change of target -- `.doSpdChange` (`src/isp_bldc_motor.spin2:3655`) routes a speed change to `.rampUp`,
`.rampDn` or `.slow2Chg` exactly as a start from rest does. **The defect is the ramp's starting RATE.**
`:3706-3707`, in `.rampUp`:

```spin2
                or      drv_incr, drv_incr          wz  ' -and- are we stopped, just about to spin up?
    if_z        mov     ramp_curr, ramp_min_            ' set initial ramp if starting from 0
```

and `:3715-3718`, the growth:

```spin2
                mov     curr_ramp, ramp_curr            ' current ramp
                add     ramp_curr, ramp_inc_            ' increase ramp for next time
                cmps    ramp_curr, ramp_max_        wc  ' too high?
    if_nc       mov     ramp_curr, ramp_max_            ' Y set to ramp_max
```

**`ramp_curr` is reset to `ramp_min_` only when `drv_incr` is zero -- i.e. only when starting from rest.** On a
speed change from a *running* speed, `drv_incr` is non-zero, so `ramp_curr` is **inherited from the previous
ramp** and keeps accumulating, while a start from rest begins gently at `ramp_min_` (1 500) and grows.

> **CORRECTED 2026-09-17, same day, before this entry was acted on.** A first draft of this entry said the
> inherited value is `ramp_max_`. **It is not, and finding C-2b in the companion study already established
> why:** `ramp_curr` grows by `ramp_inc` = 22 per drive pass from 1 500, and `ramp_max_` = 200 000 is
> unreachable in every shipped configuration. Growth also stops the moment the ramp completes
> (`.endRUpAtSpeed`), so it accumulates only across the *ramping* portion of each rung -- roughly 107 to 618
> passes at Visit 4's measured `steady_ms` of 56-323. Verified in source: `ramp_min := 1_500`,
> `ramp_max := 200_000`, `ramp_inc := 22` (`src/isp_bldc_motor.spin2:526-528`). **The defect and the fix are
> unchanged; the magnitude claim was wrong and is withdrawn.**

**What actually limits the jolt, and it is the cleaner explanation.** The ramp is gated by `LAG_SOFT` = 80
(`:3345`), tested at `:3712`: `cmps lag_s, #LAG_SOFT wc` / `if_nc jmp #.justIncr` -- *the ramp waits for the
rotor this pass*. So on a transition that starts with a large inherited `ramp_curr`, the ramp drives the lag
straight into the `LAG_SOFT` gate and is throttled there.

⭐ **The measurement lands exactly where that predicts, and rung 0 is the control.**

| | `err_pk` | vs `LAG_SOFT` = 80 |
| --- | --- | --- |
| **rung 0** -- the only transition starting from rest, `ramp_curr` = `ramp_min_` = 1 500 | **56** | **below** -- the limiter is never reached, the ramp is never throttled |
| rungs 1-11 -- every transition inheriting an accumulated `ramp_curr` | **71-98** | **at or above** -- the ramp hits the lag gate on every one |

The one rung that gets the soft start is the one that stays under the limiter, and it is the one that does not
slam. Rungs 1-11 each drive the rotor into the lag gate and are held there -- that repeated hit is what is felt
through the platform.

**Fix direction -- correct by construction (P10):** reset `ramp_curr` to `ramp_min_` at the start of **every**
new ramp, not only when `drv_incr` is zero. The soft start then applies to every speed change, acceleration is
continuous at each transition, and `err_pk` should fall toward `err` at rungs 1-11 while rung 0 is unchanged --
a directly measurable prediction for the next visit, with rung 0 as the built-in control.

**Note what this is NOT.** It is not a missing slew-rate limit (the ramp exists), and it is not the lag clamp
(see above -- that half is an instrument bound, and `LAG_HOLD` is doing its job). The two halves of this entry
are two different findings that happened to be found together; **only this half is a driver defect.**

**Status (aged-state sweep 2026-09-17):**
- **First half (the bound): CLOSED.** `LAGBND` PASS on every part at Visit 5 against the driver's own fault test
  (115-116 vs 124).
- **Second half (the slam): fix IN THE BINARY, effect UNMEASURED, and STILL OPEN.** `mov ramp_curr, ramp_min_` at
  `.doSpdChange` (`src/isp_bldc_motor.spin2:3668`) resets the ramp on every new request. STEPHEN at Visit 5:
  *"some are not kicking but many still are... so your remove kicking on ramp up is only partially working."* The
  table above was never a measurement of the slam -- `err`/`err_pk` are steady-window statistics and rung 0 reads
  the same gap as every other rung (PL-87). The transition instrument (PL-87) comes first; then whatever still
  kicks is a driver question with evidence behind it. IN THIS RELEASE.

### PL-85 -- t0's cog bursts truncate DEBUG records ON THE WIRE; a verdict was lost and only a USB capture recovered it

> ⛔ **THE LOST VERDICT IS RE-ATTRIBUTED 2026-09-23 («#3585»): it was the DEBUG data cap (PL-114), not the cog
> burst.** Rebuilt from `18207c0` (40,918 B, the size downloaded), the `R1-T0-EXHAUST` record's byte 13,683 is
> the `,` that arrived after `TRUE`, and byte 13,684 is the `l` of `,lo,TRUE,`, which never did. It is the same
> byte that cut PL-94's record and the 2026-09-20 panel. **What this entry still holds:** the run-together
> `CogN` prefixes (`CogCog1Cog0`) are a separate observation, and the quiet windows below stay. **What it no
> longer holds:** the claim that a cog burst cut the record. Nothing that sits below the limit has been shown
> to be cut by a burst. ✅ **2026-09-22 23:42:** `R1-T0-EXHAUST` reported whole, PASS, through the same
> exhaustion burst, and no line in any of that pass's three logs carries two `CogN` prefixes. The quiet windows
> hold. **This entry can close at the next closeout.**

> **DESIGNED OUT 2026-09-18 («#3543»), with PL-41; run-time proof owed to Visit 6.** t0 no longer makes the
> bursts this entry measured: `countFreeCogs()` uses `COGCHK()` and starts nothing, T0-8 / T0-15b / T0-22
> share one occupy burst and one release burst (`runExhaustionPhase()`), and cog 0 prints nothing across any
> cog start or stop (2 ms before; 10 ms after a start). Cell ids, criteria and record formats are unchanged.

**Found 2026-09-17 at Visit 5**, raised by Stephen from the log before I read it. **Harness defect, and
it is a TEST SHAPE defect, not a terminal or driver one.**

**STEPHEN 2026-09-17:** *"t0 is constructed so that debug messages from cogs are overlapping causing
logging problems. So at the end of the runs i ran t0 again this time emitting a USB log so that you can
reconstruct the data that was omitted from the log. this is a test shape problem!"*

**MEASURED**, `analyses/bench/2026-09-17/debug_260917-172913.log`:

```
L147  Cog1Cog1  INIT ...
L149  CogCog1   INIT ...
L151  CogCog1Cog0  T0-15c,baseline,7,...
L168  [BINARY DATA: 80 bytes - displaying as hex]      <- the terminal gave up and dumped hex
L169    0000: 43 6F FF 43 6F 67 31 43 6F 67 30  |Co.Cog1Cog0|
L221  SIGNOFF,...,R1-T0-EXHAUST,...,measured,TRUE,     <- the record ends here
```

⭐ **IT IS NOT THE TERMINAL. MEASURED on the raw USB stream**, `usb-traffic_260917-174323.log` L1266:

```
0020: $2C $6D $65 $61 $73 $75 $72 $65  $64 $2C $54 $52 $55 $45 $2C $0D   ,measured,TRUE,.
0030: $0A $43 $6F $67 $30 $20 $20 $54  $30 $2D $54 $52 $41 $50           .Cog0  T0-TRAP
```

**The P2 emitted `,measured,TRUE,` then CR LF and moved to the next record.** The rest --
`lo,TRUE,hi,TRUE,units,BOOL,n,1,verdict,PASS` -- was never transmitted. The run-together prefixes are on
the wire too (USB L1217-1218, L1248-1249).

**DERIVED -- this is PL-41's mechanism seen at wire level for the first time.** DEBUG output is
serialised by LOCK[15]; a cog stopped mid-message leaves it unterminated and the next cog's prefix
follows behind it. **Every damaged line is adjacent to a `CogN INIT` burst**, and the bursts come from
T0-8, T0-15b and T0-22, each of which starts and stops **seven spacer cogs**, plus T0-15's restart and
T0-19's three-cog steering start.

**What it cost:** `R1-T0-EXHAUST`'s verdict. It was recovered **by construction** -- `emitSignoffBool()`
prints `measured` as the criterion result and computes PASS exactly when measured and met, so
`measured,TRUE` IS PASS -- and its substance survived in the record before it (`T0-15b,cogs_occupied,7,
start_return,-1,raw_motor_cog,0,baseline,7,free_after,7`). **The next loss in a record whose `measured`
field is not the verdict is unrecoverable.**

⛔ **A RECOVERY THAT DEPENDS ON AN OPERATOR HAVING CAPTURED USB IS NOT A PROPERTY OF THE HARNESS.** The
verdict survived because Stephen happened to run it again with a USB log. That must not be the design.

**Fix direction -- design the shape out, do not widen a tolerance (P10).** This is «#3543» (Batch 1b)
arriving with a measurement behind it at last: a cog that may be emitting DEBUG is never stopped; the
spacers used for cog-exhaustion and restart cells never print and hold no lock; and cog 0 does not print
across a start/stop burst. **«#3543» should now be scheduled on this evidence** -- it has been deferred
since 2026-09-14 on a garbled-log observation, and this is the same mechanism with a lost verdict
attached.

**IN THIS RELEASE (aged-state sweep 2026-09-17):** STEPHEN 2026-09-17, *"your outstanding tasks must be
completed before this release"* -- «#3543» is one of them.

### PL-86 -- the fault-API provocation is stronger than the abort watching it, and has cost two cells at two visits

> ## ⭐ CAUSE IDENTIFIED 2026-09-19 at Visit 6a, and it is NOT the provocation.
>
> **The computed provocation's arithmetic is correct.** DERIVED by inverting the shifts the run printed
> (`BM-FLTAPI … l_shift,240, r_shift,108`): the LEFT wheel's mean `err` at speed was **+43** and the
> RIGHT's **−51** (opposite signs are right -- the steering object reverses the right wheel), and
> 43 − 171 = **−128**, −51 − 77 = **−128**. Both land exactly on the wrap, three units past the
> `|err| >= 125` fault test, as designed.
>
> ⛔ **What stops the fault is the driver's LAG LIMITER.** It holds the field back as `err` grows, so
> `err` never reaches the fault test; the motor sits badly commutated and draws current until the
> harness's abort fires. MEASURED: `ABS_CURRENT` at 2_655 mV (`dual-b`), 3_435 and 3_771 mV (`dual-c`)
> against a 1_500 mV threshold, where half-speed running current is about 900 mV.
>
> ⭐ **This is the same mechanism as PL-46**, already recorded against the commutation scan: *"its
> window edge is found by walking until the motor FAULTS … the lag limiter now makes it DROOP
> instead."* **The scan and the fault provocation are two instruments with one broken assumption**, and
> «#3575» already owns the redesign of the first. Whatever replaces "walk until it faults" should serve
> both.
>
> **It does fault once per wheel**, on the first trial, and then every later trial on that wheel aborts
> -- that second behaviour is its own finding, **PL-93**.
>
> Full reading: `analyses/bench/2026-09-19/VISIT-6A-RESULTS.md` §5.

**Found 2026-09-17 at Visit 5.** **Harness stimulus defect, mine (P3). NOT a driver defect.**

**MEASURED**, `analyses/bench/2026-09-17/debug_260917-173141.log` L7653-7656:

```
BM-ABORT  seg,OVERSHT tid,25 reason,ABS_CURRENT value,2_445 scope,TRIAL
BM-FLTAPI tid,25 want_off,180 l_off,223 r_off,223 power,50 rows,2 ... why,ABORTED
```

The fault-API trial provokes a fault by writing a commutation offset **180 degrees from the running pair
on both wheels**, holding the field where the rotor cannot follow. Current reaches **2_445 mV, about
16 A**, within roughly 100 ms -- past the harness's own `ABS_ABORT_MV` of 1_500 (10 A). The abort stops
the trial before the driver's own fault test is reached.

**Visit 4 measured the same thing at 2_217 mV.** So `R14-DUAL-FLTAPI-B` and `R16-DUAL-FLTRETRY-B` are
NOMEAS for the second visit running, and task 3547's fault-API reporting and PL-66's same-power retry
are **still uncertified**.

**DERIVED: the driver is doing exactly what a 180-degree offset demands**, and the abort is the
instrument working. The defect is that the provocation and the guard were chosen independently.

**Fix direction, and there are two clean options -- this is instrument design and mine (P3):**
1. **A gentler provocation.** The offset only has to exceed the driver's fault test (125 err units,
   about 176 degrees of the 256-unit cycle); 180 degrees is the maximum possible, chosen when the old
   ramp-based provocation stopped faulting. A smaller offset should fault without a 16 A surge.
2. **Exempt the trial from the absolute-current abort**, the way `bInstLagExempt` already exempts
   deliberately-provoked lag -- but only with a stated ceiling, because the abort exists to protect the
   hardware.

⭐ **Option 1 is preferred and is testable without the bench:** the fault test's threshold is a known
constant, so the offset needed to cross it is arithmetic, not a sweep.

**Correction and status (aged-state sweep 2026-09-17):**
- ⚠ **"task 3547's fault-API reporting is still uncertified" is wrong.** It was certified at **Visit 3** with the
  older ramp provocation: `R14-DUAL-FLTAPI-B` PASS, both wheels FAULTED at 101 ms, `getStatus()` FAULTED,
  steering `isFaulted()` TRUE, the latch held 5.8 s (`analyses/bench/2026-09-16/VISIT-3-RESULTS.md` §2.3). That
  certified M, AF and S-5. What is genuinely uncertified is **PL-66's same-power retry** (`FLTRETRY`, added
  later) and **everything a fault does on today's lag-limited driver**.
- **IN THIS RELEASE** as fault handling (STEPHEN 2026-09-17, *"fix fault handling"*), with PL-59, PL-66 and the
  fault half of PL-89.

> ## FIXED IN THE HARNESS 2026-09-17, night («#3572») -- option 1, computed; run-time proof owed to Visit 6
>
> **Why the 180-degree write never faulted, DERIVED from source:** it was written AT REST, before the drive. The start
> re-seeds the field from the halls plus the new offset (`initAngleFmHall`), so the error starts at zero, and the lag
> limiter then holds the field at `LAG_HOLD` while the rotor fights a reversed torque -- the error never reaches the
> fault test at 125, and the current climbs to the 10 A abort. And even written at speed, a fixed 180 degrees lands
> the 8-bit error at `128 - |err_before|`, which misses 125 whenever the running error exceeds 3 units.
>
> **The construction (`test_bench_dual.spin2` `faultShiftDeg()`):** drive to speed, average the wheel's own error over
> 16 reads, and shift its offsets by exactly `(err + 128) mod 256` units, converted to degrees. The driver computes
> `err = field angle - (hall angle + offset)` and maps offset degrees positively, so a larger offset LOWERS the error:
> the shift lands it on -128, the wrap, in the next control frame, 3 units past the fault test on either side --
> before the current can build.
> OVERSHT's fault-API trial (both wheels, through the steering object) and POSTFLT (PL-59, each wheel) both use it;
> `FLTAPI_OFFSET_DEG` and `FAULT_PROVOKE_NEG_DEG` are deleted. `BM-FLTAPI` prints each wheel's computed shift.
> With the provocation faulting, `R14-DUAL-FLTAPI-B`, `R16-DUAL-FLTRETRY-B` (PL-66) and the new
> `R17-DUAL-FLTCAUSE-B` (S-7), `R17-DUAL-OFFREST-B` and `R17-DUAL-FLTSTOP-C` (a fault delivers `holdAtStop()`, PL-89's
> fault half) all become measurable.

### PL-87 -- the ladder's err_pk is a STEADY-WINDOW statistic, so no cell can see a transition kick

> **Status 2026-09-22, Visit 8:** `R17-DUAL-TRKICK-A` is still FAIL at 233 / 222 mV on DRIVER_REV 3 (221 / 214
> before). The R18.4 drive change did not move the transition kick, although «#3583» was scoped to subsume it.
> It remains open (Visit 8 evaluation F-8).

> ## BOTH FIXES LANDED 2026-09-20 («#3580» R18.1, dual SRC_REV 21 / FMT 9); run-time proof owed to Visit 7
>
> The box below asked for exactly two things, and both are in the tree:
>
> 1. **`R17-DUAL-TRKICK-A` is re-judged on current.** The criterion is `tr_i_over` -- the transition
>    current peak less the rung's **own** steady `i_max`, a new `BM-RUNGTR` field -- above
>    `TRKICK_EXCESS_MV` (50 sense mV, about a third of an amp at the 150 mV/A the harness aborts on).
>    The from-rest control machinery is **deleted** rather than repointed: an instrument built on a
>    clamped observable is blind whatever control it is given.
>    **The number and its negative case are MEASURED**, from all four ladders of
>    `debug_260919-173751.log`, as `tr_i_pk - i_max` per rung:
>
>    | ladder | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
>    |---|---|---|---|---|---|---|---|---|---|---|---|---|
>    | LEFT reverse | -2 | 0 | -2 | -10 | -38 | -66 | **+157** | **+646** | **+401** | **+81** | **+128** | **+128** |
>    | LEFT forward | +1 | +1 | -3 | -7 | -21 | -34 | -76 | **+506** | **+397** | **+91** | **+112** | **+192** |
>    | RIGHT reverse | 0 | 0 | -4 | -22 | -46 | -69 | **+186** | **+677** | **+403** | **+87** | **+110** | -52 |
>    | RIGHT forward | +2 | +1 | -2 | -2 | -10 | -47 | -137 | **+580** | **+412** | **+82** | **+113** | **+214** |
>
>    ⭐ **Below the knee a change of speed costs NOTHING above steady running** -- every reading is at
>    or below zero. At and above it the transition draws two to three times the steady peak. The two
>    populations are separated by a gap running from **-137 to +81 with nothing in it**, so the
>    criterion is not a judgement call. **Visit 6a would have FAILED this cell 11 times of 22 on the
>    LEFT motor and 10 of 22 on the RIGHT** -- against the 0 of 22 that `tr_over` reported.
> 2. **The short ramps are instrumented.** `LIVE` now emits `BM-RUNGTR` and the new `BM-RUNGHL` for
>    every rung. It does **not** fold `TRKICK`: its settle is `LIVE_SETTLE_MS` against the ladder's
>    `LADDER_SETTLE_MS`, so its transition window is a different length, and one verdict over two
>    populations can fail on the mixture rather than on the drive (doctrine D2).
>
> **Also landed with them**, because the same instrument is what Visit 7 reads: `BM-RUNGTR` gains
> `from_incre`, the speed the wheel was holding when the command arrived, so a transition's **delta and
> its direction** come off the record; and the ladder walk gains a **descent** and six **delta cells**
> (a small and a large change of speed at low, at the knee and at the ceiling, each taken up and down).
>
> **What is still owed:** a run. The criterion has never judged a live ladder, and the driver half of
> the kick is **PL-95**'s, fixed in R18.4.

> ## ⛔ THE REPLACEMENT INSTRUMENT IS ALSO BLIND -- and Visit 6a's own log already holds the reading
> that is not. Recorded 2026-09-20.
>
> **STEPHEN 2026-09-20, the observation the run sheet asked for in advance:** *"there we two fwd/rev
> ramps short/long for each motor. in the short ramps they kicked between 2 and 3. in the long ramps
> they kicked at each increment"*.
>
> **`R17-DUAL-TRKICK-A` PASSED with 0 kicks of 22 per wheel. It is a FALSE PASS.** His hand is the
> control, and doctrine D2 puts the suspicion on the measurement.
>
> **MEASURED, `debug_260919-173751.log`, the LEFT reverse ladder, twelve rungs in order** (every ramp
> in the load has the same shape):
>
> | rung | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
> |---|---|---|---|---|---|---|---|---|---|---|---|---|
> | `tr_err_pk` | 98 | 76 | 73 | 75 | 75 | 75 | 78 | 85 | 95 | 97 | 102 | 105 |
> | `tr_over` **(what TRKICK judged)** | 36 | 3 | 2 | 4 | 3 | 3 | 1 | 0 | 0 | -1 | 0 | -1 |
> | `tr_i_pk` **(recorded, never judged)** | 19 | 25 | 55 | **234** | **583** | **1197** | **1439** | **1264** | 599 | 200 | 192 | 226 |
>
> ⭐ **The error says nothing and the current says everything.** Across the ramp `tr_err_pk` moves
> within a 73-106 band -- about +-15% -- while `tr_i_pk` rises **seventy-five fold** and peaks at rung 7.
> At the sense calibration the harness uses for its own abort (150 mV/A) rung 7 is **about 9.6 A**, and
> the RIGHT reverse ladder's rung 7 reads 1_522, **above the 1_500 abort threshold** -- it does not
> abort only because the abort wants four consecutive samples and this is a transient.
>
> **DERIVED, and it is the SAME root cause as PL-86, PL-46 and PL-93:** `tr_err_pk` sits in a narrow
> band around 100 because **the lag limiter holds it there** (`LAG_HOLD` = 100). Position error is a
> CLAMPED observable, so any instrument built on it is blind by construction -- which is why the Visit 5
> instrument could not see the kick, and why its replacement cannot either. **Current is not clamped,
> and it was being recorded beside the error the whole time.**
>
> **So the kick is MEASURED, on this visit's data, with no further bench time:** it is real, it is on
> every speed change of the long ramps, it grows with the size of the increment, and it peaks near 10 A.
> That matches his hand exactly, including "at each increment".
>
> **Two fixes, both free of a new run:**
> 1. **Re-judge `TRKICK` on `tr_i_pk`**, not `tr_over`. The criterion becomes a transition current
>    ceiling, or a rise over the from-rest rung, and its negative case is on file in this very table.
> 2. **The short ramps emit no `BM-RUNGTR` at all** -- only LADDER and CLOCK rungs do, so the LIVE
>    segment, where he felt a kick between rungs 2 and 3, has **no transition record**. Instrument it.
>
> ⭐ **AND «#3573»'S DRIVER HALF IS NEEDED.** The plan made it conditional on "if Visit 6a's TRKICK says
> the kick survives". TRKICK said no; the current and his hand both say yes. **The kick survives.**

> ## FIXED IN THE HARNESS 2026-09-18 («#3573», dual SRC_REV 16 / FMT 7); run-time proof owed to Visit 6
>
> - `rungMeasure()` now marks the ring at the drive command, and `transitionStats()` walks [command mark ..
>   window start] -- the ramp and the settle -- for peak |err| and peak |i|. Every LADDER and CLOCK rung prints
>   them in a new record, `BM-RUNGTR` (177 bytes worst case; `BM-RUNG2` had no room at 269), with `tr_over`: the
>   transition peak less the rung's own steady `err_pk`, so the servo ripple common to both cancels.
> - **The control is by state, not index:** `from_rest` is TRUE for the first rung of each motor and sign and for
>   the first rung after a recovered fault. A command whose ring sample was overwritten prints NA
>   (`WHY_RING_LOST_HEAD`), never a partial peak.
> - **New cell `R17-DUAL-TRKICK-A`** (per motor): counts the running-speed changes whose `tr_over` exceeds the
>   control's by more than `TRKICK_MARGIN` (10 err units, ~14 degrees electrical); PASS at 0. The margin is
>   DERIVED; the negative case is Stephen's Visit 5 observation that many transitions still kicked, which this
>   cell must then fail.
> - `BM-RUNG2`'s `err_pk` stays in the record as the steady statistic it is; its comment now says so.
> - **Limit, stated:** the instrument samples at 500 Hz, so a kick shorter than ~2 ms can fall between samples.
>   If the cell passes while a kick is still felt, that is the instrument's limit, not the driver's.

**Found 2026-09-17 at Visit 5**, checking Stephen's observation against the data. **Instrument defect,
mine (P3).** ⛔ **It invalidates the evidence PL-78's second half was built on.**

**STEPHEN 2026-09-17:** *"the ramps from dual-a some are not kicking but many still are... so your
remove kicking on ramp up is only partially working."*

**The driver fix IS in the binary** -- verified in source, `src/isp_bldc_motor.spin2:3668`,
`mov ramp_curr, ramp_min_` at `.doSpdChange`, reached once per request from `.newRqst`.

**MEASURED**, LEFT forward, Visit 5 (`debug_260917-173713.log` L15161-15196) against Visit 4's same
block:

| rung | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `err` V5 | 33 | 48 | 48 | 48 | 48 | 48 | 48 | 55 | 63 | 66 | 69 | 74 |
| `err_pk` V5 | 57 | 77 | 71 | 72 | 72 | 72 | 72 | 81 | 88 | 91 | 94 | 100 |
| `err_pk` V4 | 56 | 75 | 71 | 71 | 72 | 72 | 73 | 80 | 88 | 91 | 94 | 98 |
| gap V5 | 24 | 29 | 23 | 24 | 24 | 24 | 24 | 26 | 25 | 25 | 25 | 26 |

**Unchanged within 1-2 counts at every rung. PL-78's prediction did not happen.**

⭐ **AND THE REASON IS THAT THIS TABLE WAS NEVER A MEASUREMENT OF THE SLAM.**

- `err` and `err_pk` come from `windowStats()`, over the window `rungWindow()` opens **after** AT_SPEED
  and after the settle. **The transition is over before the window opens.**
- **Rung 0 is the proof.** It is the only rung that starts from rest, so it always had the soft start and
  never had the defect -- and its gap is **24**, the same as every other rung's, at **both** visits. A
  statistic that reads the same on the control and on the suspects is not measuring the difference
  between them (doctrine D2).
- **DERIVED:** the ~25-count gap is the AT_SPEED duty-servo ripple. `CURRENT-LIMIT-AND-STOP-DESIGN.md`
  section 3.2 records the unloaded trace swinging -22 to -70 about a set point of 42 -- a peak about 25
  above the mean, which is exactly what `err_pk - err` reports.

⛔ **So PL-78's second half rests on window statistics read as transition statistics.** Whether the
driver change is right, wrong or partial, **this instrument cannot say, and could not have said at
Visit 4 either.** What Stephen felt with his hands is currently the only evidence about the slam, and it
says the fix helped some transitions and not others.

**Fix direction -- the measurement already exists and costs NO bench time.** `rungMeasure()` arms the
instrument at the command, so the ring **already holds every sample of the transition**; `windowStats()`
simply never reads them. Add a second statistics pass over [arm .. window start] -- the transition --
giving the peak |err| during the ramp, per rung, and print it in `BM-RUNG2` beside the steady pair.
**Rung 0 is the built-in control**, and the next ladder load then measures the slam directly instead of
inferring it.

**IN THIS RELEASE (aged-state sweep 2026-09-17)** -- it gates PL-78's second half, which is a behaviour Stephen
felt and ruled not shippable.

### PL-88 -- driving the platform STRAIGHT runs one wheel in its expensive direction, so the two wheels do not cost the same

**Found 2026-09-17** while checking the direction-asymmetry measurement against how the platform is
actually driven. **DERIVED from measurements, with a supporting trace; not yet measured directly at
steady state.**

**The two facts, each MEASURED, that combine into this:**

1. **Negative increments cost about twice positive ones, on BOTH motors.** Visit 5 ladder,
   `analyses/bench/2026-09-17/debug_260917-173713.log`, `amps_x10k` at the same commanded speed:

   | rung | LEFT rev/fwd | RIGHT rev/fwd |
   | --- | --- | --- |
   | 3 | 13_547 / 6_692 = **2.02** | 13_821 / 7_269 = **1.90** |
   | 4 | 37_162 / 18_302 = **2.03** | 37_355 / 19_819 = **1.88** |
   | 5 | 75_274 / 38_051 = **1.98** | 76_316 / 41_075 = **1.86** |

   Third independent measurement of the same effect (Visit 4, and a different run on 2026-09-12).

2. **The platform drives its two wheels in OPPOSITE increment signs.** The motors are mounted
   mirror-image, so `start()` calls `rtWheel.forwardIsReverse()` (`src/isp_steering_2wheel.spin2`,
   and CLAUDE.md's Cog model section). Platform-forward is therefore LEFT positive, RIGHT negative.

⛔ **So going straight forward, the RIGHT wheel runs in the 2x direction and the LEFT wheel does not.
Going straight backward, they swap.** The asymmetry does not cancel on the platform -- it lands
entirely on one wheel at a time.

**Supporting trace, MEASURED**, `debug_260917-173141.log` L7625-7629, an OVERSHT straight-line distance
drive: primary LEFT `pos` runs positive and `o_pos` (RIGHT) negative, confirming the sign split; at the
same samples `i` (LEFT) reads 27, 21, 14 while `o_i` (RIGHT) reads 91, 74, 47.

⚠ **Those are SPIN_DN samples, so the ratio there is not a steady-state figure and is not quoted as
one.** What they establish is the SIGN of the effect and that it appears in ordinary straight-line
driving, not only in the ladder's raw-increment test.

**What a user would feel, DERIVED:**
- **One motor and one board run hotter than the other**, and which one depends on travel direction.
- **Battery life is worse than the wheels' average would predict**, because one wheel is always paying
  the penalty.
- **The two wheels' thermal derate points differ**, so under sustained load the current limiting will
  engage on one wheel first -- and that wheel's speed droops first, which on a two-wheel platform is a
  veer.

**This is the same root cause as PL-26** (the commutation scheme departs from the board designer's
principles) and it is the reason that entry matters to a *user* rather than only to efficiency: the
offsets in force are symmetric (`off_neg 43, off_pos 317`, and 317 = 360 - 43) while the currents are
2:1, which says the hall zero is not where that symmetric pair assumes.

**No fix is proposed here and none should be until the offset scan («#3520») has run** -- its three
outcomes each decide something different, and they are already written up in
`analyses/BLDC-COMMUTATION-PRINCIPLES.md`.

**Owed, and cheap:** a steady-state per-wheel current reading during a straight-line steering drive.
The motion harness already drives straight through the steering object and already records per-wheel
current; nothing new has to be provoked.

**Status (aged-state sweep 2026-09-17): IN THIS RELEASE through the offsets.** STEPHEN 2026-09-17 requires the
commutation offsets confirmed before release, by the lifted scan and then an attended **spin-in-place** floor
run (*"yes spin in place but max revolutions limit so we don't stress cable"*; the tether rules out a long
straight run). Spinning one way runs both mirror-mounted motors in one increment sign and the other way in the
other, so it measures each motor's LOADED current in both directions -- the quantity this entry needs --
without travel. The straight-line figure is then derived from the two directions, not measured.

### PL-89 -- "float" is a powered hold, not a coast, and every fault and e-stop hard-brakes regardless of holdAtStop()

> ## ⛔ CORRECTED 2026-09-17, evening, by the completed findings audit (`analyses/FINDINGS-AUDIT-2026-09-17.md` §2.1). The table below is BACKWARDS, and the entry contradicts a settled bench fact.
>
> **The source, read end to end:** `holdAtStop(bEnable)` sets `stop_mode := (bEnable) ? SM_BRAKE : SM_FLOAT`
> (`src/isp_bldc_motor.spin2:713`). `checkstop` (`:4078-4085`) runs `cmp stop_mode_, #SM_FLOAT wz` then
> `modz _nz wz`, so Z is set when the mode is **not** FLOAT:
> - **SM_BRAKE** (`holdAtStop(TRUE)`): `driveoff := 0`, PWM on at `duty_min` at a hall-derived angle -- a
>   **powered position hold**, as its doc promises;
> - **SM_FLOAT** (`holdAtStop(FALSE)`): `driveoff := 1`, so the loop runs `wypin #0, drive_pins`.
>
> **So if `wypin #0` shorts the phases, the short is FLOAT's, not BRAKE's.** The table's first two rows are
> swapped, and the headline "float is a powered hold" is wrong. (The subject of commit `578f3ef` says the
> same wrong thing; this entry carries the correction.)
>
> **The "one link not established" below was established on 2026-09-15, in PL-56**, which this entry did
> not cite: the low side is written the high side's duty plus `dead_gap` on an inverted output, which is
> complementary drive with deadtime only if a high turns the low FET on; the opposite polarity would be
> shoot-through every PWM period, never seen on this rig.
>
> ⛔ **THAT MAKES THE CONFLICT SHARPER, NOT SETTLED.** The derivation now says FLOAT at rest shorts the
> windings. **PL-56 records Stephen's bench fact that float freewheels** -- the safety study's pre-sprint
> record, and STEPHEN 2026-09-15: *"we came into this work with float working as desired"*. Doctrine
> overlay P8: **the derivation is the suspect.** Something between `driveoff = 1` and the FET gates is not
> what this reading says -- candidates, none checked: what an inverted triangle-PWM smart pin actually
> outputs at Y = 0; the board's added logic buffer; or the state he tested differing from the at-rest
> FLOAT path.
>
> **His hand test decides, with the predictions corrected:**
> 1. `holdAtStop(TRUE)` then `stopMotor()` -- held at a fixed angle: moderate, cogging resistance.
> 2. `holdAtStop(FALSE)` then `stopMotor()` -- **freewheels if his bench fact holds; resists harder the
>    faster it is turned if this derivation holds.** This is the discriminating state.
> 3. `stop()` -- freewheels in either case.
>
> **FIX DIRECTION, STEPHEN 2026-09-17:** *"isn't there a set*() which specifies motor stop condition? so user
> would select it for their application"*. **`holdAtStop()` is the user's selection, so every stop path -- at
> rest, on a fault, and on an e-stop as its own documentation promises -- must deliver it.** That is an
> API-contract fix (doctrine overlay P3), IN THIS RELEASE; the hand test then certifies it rather than
> deciding anything.
>
> **Supporting reading, found by the 2026-09-17 bench-emission inventory:** the char tier's quiescent hold (a
> started motor at zero command in the default `SM_FLOAT`) reads `duty_mean 24_264` -- exactly `duty_max` --
> with `err_mean 115` and near-zero current (`analyses/bench/2026-09-17/debug_260917-125254.log:91-93`). DERIVED:
> the duty servo keeps winding while `driveoff = 1`, and no PWM is applied, or that duty at rest would draw a
> large current. So FLOAT at rest **is** the `driveoff` path. It says nothing about whether that path shorts the
> windings: with the wheel still, a short carries no current either. Leaving float resets `duty_` to `duty_min`
> (`.checkstopfloaton`), so the wound-up register is telemetry only, not a start-up defect.
>
> ### FIXED IN TREE 2026-09-17 («#3568», design `plans/STOP-STATE-DESIGN.md`)
>
> - **p2kb closed the one open link:** a triangle-PWM pin with `Y = 0` is constant LOW, and `Y = frame` is
>   constant HIGH (`p2kbArchSmartPin01000PwmTriangle`). With the low side inverted and PL-56's polarity, the old
>   `wypin #0, drive_pins` was SHORT.
> - **The driver now has one `bridge` register holding `BR_DRIVE`, `BR_SHORT` or `BR_COAST`**, each written so its
>   meaning does not depend on a pin's inversion: COAST writes `Y = 0` to the high sides and `Y = frame` to the
>   inverted low sides, so all six FETs are off.
> - **Every path now delivers the user's selection:** at rest `SM_FLOAT` → COAST (was SHORT), `SM_BRAKE` → the
>   powered hold (unchanged); a fault → COAST under `SM_FLOAT`, SHORT under `SM_BRAKE`; an e-stop → SHORT always,
>   per its doc's *"Immediately stop"*. The bridge also comes up COASTING at driver start (it came up shorted for a
>   frame), and the duty servo no longer winds `duty_` up while the bridge is not driven.
> - Gates: `tools/build-check.sh` 47/47 with both release demos certified; `tools/check_style.sh` PASS. The
>   PASM-addressed VAR runs are unchanged (the `fault` line's comment only).
> - **Run-time proof is owed to the bench**: the hand test above. **Built 2026-09-19 («#3578») as bench tier
>   `t0-stopmode`** (`test_bench_t0.spin2` T0-24, six rows, eight cells; `plans/STOP-STATE-DESIGN.md` §5).
> - **"Did the OLD build brake in float?" is settled by construction, so no unfixed binary is run.** `BR_SHORT`
>   writes `wypin #0, drive_pins` on all six pins, the identical instruction the old `driveoff = 1` path ran
>   for FLOAT at rest -- so the hand test's **e-stop row measures the old build's float state** on the fixed
>   binary. The release note is worded from that row's reading.
>
> Everything below this box is the original entry, kept as written.

**Found 2026-09-17** by the findings audit, chasing the unverified hardware fact recorded in
`analyses/bench/2026-09-15/VISIT-2-RESULTS.md` section 0. **DERIVED from source, and it confirms that
hypothesis.** Raised by Stephen, who proposed the hand test that closes the one remaining link.

**THE SOURCE, `src/isp_bldc_motor.spin2`:**

```spin2
pwmt   LONG %000_000000_01_01000_0  ' PWM true (P_BITDAC | P_PWM_TRIANGLE | P_OE)
pwmn   LONG %001_000000_01_01000_0  ' PWM not  (P_INVERT_OUTPUT | ...)
       wrpin pwmn, pin_pwm_u_l      ' set up PWM pins, LOW SIDE IS INVERTED
       wrpin pwmt, pin_pwm_u_h      ' high side is not inverted
```

and the drive-off action in the control loop:

```spin2
       testb driveoff, #0       wc
if_c   wypin #0, drive_pins         ' "make sure pwm is off and all drive pins low"
```

**DERIVED:** `wypin #0` on all six pins gives a high side (non-inverted) that stays LOW -- high FETs
off -- and a low side (P_INVERT_OUTPUT) that stays **HIGH** -- **all three low-side FETs ON**. The three
motor phases are shorted together. **That is a dead short across the windings: dynamic braking.**

⛔ **THE COMMENT ON THAT LINE IS WRONG** and is probably why this stood so long: it says "all drive pins
low", which describes the register value written, not the resulting pin state on the inverted half.

### THERE ARE THREE STOP BEHAVIOURS, NOT TWO

| Caller does | `driveoff` | Bridge | Actual behaviour |
| --- | --- | --- | --- |
| `stopMotor()` + `holdAtStop(FALSE)` | 0 | PWM **still enabled**, `duty_` reset to `duty_min` | **powered hold at ~6.6 % modulation -- NOT a coast** |
| `stopMotor()` + `holdAtStop(TRUE)` | 1 | `wypin #0`, low sides on | **dead short, dynamic brake** |
| `stop()` | n/a | Spin2 `pinclear` releases the pins | **true float, coasts** |
| **any FAULT** (`.driveoff` on the fault path) | 1 | low sides on | **brake, whatever holdAtStop() says** |
| **any E-STOP** (`.driveoff`, commented *"regardless of stop mode"*) | 1 | low sides on | **brake, whatever holdAtStop() says** |

⭐ **This explains Visit 2's measurement exactly** (MEASURED there): `emergencyCutoff()` stops a
half-speed wheel **within one tick**, while `stop()` lets it coast **38-48 ticks**. One is a short, the
other is an open circuit.

### WHY IT MATTERS TO A USER -- this is an API-contract defect (doctrine overlay P3)

1. **`holdAtStop(FALSE)` is documented as coast/freewheel and does not coast.** It leaves the bridge
   driving at minimum duty at a fixed angle, which holds position weakly AND draws current and makes
   heat at standstill. The only true freewheel is `stop()`, which ends the driver cog.
2. **A user who selects FLOAT still gets a dead short on every fault and every e-stop.** Nothing in the
   documented contract says so.
3. **The internal naming is inverted against the effect:** `driveoff = 1` is commented "drive pwm output
   disabled" and is the state that actively brakes; `driveoff = 0` is "enabled" and is the state
   selected by SM_FLOAT.

### ⛔ ONE LINK IS NOT ESTABLISHED, AND IT IS A HARDWARE FACT (P8)

Whether the board's gate driver adds a further inversion between the P2 pin and the FET gate. Rev A uses
a MIC4604 and Rev B a UCC27211D; `BOARD-REVISION-FACTS.md` has not been read for this. **If either
inverts the low-side input, the conclusion flips.**

**THE TEST, proposed by STEPHEN 2026-09-17:** *"you drive motor tell me is floating or brake and i try
to spin it. I'll be able to confirm with one hand test."* An attended tier that announces the state and
waits on a keypress between each, in the shape of the existing `t0-hand` rotation cell.

**THE PREDICTIONS, so the test can fail** (doctrine D2 -- name what the negative case looks like before
the run):
1. `holdAtStop(FALSE)` then `stopMotor()` -- lightly held, cogging, moderate steady effort to turn.
2. `holdAtStop(TRUE)` then `stopMotor()` -- strongly resistant, and **harder the faster it is turned**;
   speed-dependent resistance is the short-circuited-generator signature and is what distinguishes it
   from detent torque.
3. `stop()` -- spins freely and coasts.

**If 1 and 2 feel the same, or 1 spins free, the polarity is opposite to this reading and this entry is
withdrawn.** The driver's own hall counter records how far the wheel turned in each state, so the log
carries a number beside his judgement.

### PL-90 -- the hall triple is read by three separate TESTP instructions, so the three bits are not from one instant

> ## FIXED IN SOURCE 2026-09-17, night («#3571») -- build gate green 2026-09-18 (47/47); run-time proof owed to Visit 6
>
> - **One read.** Every hall read site (the `.ctlMotor` loop, `initAngleFmHall`, and the start priming) is now one
>   `INA`/`INB` read through `ALTS`, with the port and shift chosen once at driver start.
> - **An input filter, decided (Q2):** each hall pin's `WRPIN %FFF = %101` routes it through the global `filt1`, whose
>   reset default is 3 flip-flops every 32nd clock (~96 clocks: 0.48 us at 200 MHz). Latency against >= 2 ms between
>   hall edges at top speed is negligible. Smart-pin mode stays off and DIR stays low; the driver does not rewrite the
>   global filter (`HUBSET`), it relies on the chip default.
> - **The counter is split** without changing the status ABI: `hall_illegal` carries `%000` entries in its low word and
>   `%111` in its high word, each saturating. `getHallIntegrityCounts()` still returns the total; new
>   `getHallIllegalCodes()` (motor and steering objects) returns the split.
> - **Timing (DO item 3):** `analyses/HALL-READ-TIMING-2026-09-17.md`. The read sits ~190 clocks into the frame; at high
>   modulation a switching edge can land on it at every clock, and at 200 MHz two edges can, reached at lower duty -- a
>   clock-dependent candidate for PL-69 that the tear hypothesis could not supply. DERIVED, not established.
> - **Certification:** `R17-DUAL-HALL-K200/-K270/-K300` on the three clock loads, with `BM-HALLINT` printing
>   `%000` / `%111` / missed per lifetime. Visit 3's 200 MHz RIGHT reading (3 and 5 illegal codes) is the before.

> ## ⛔ CORRECTED 2026-09-17, night -- the torn read cannot by itself make `%000`/`%111`, and Q1 was already answered on file
>
> **1. The central claim below fails against the driver's own table.** The `deltas` table
> (`src/isp_bldc_motor.spin2`, the `deltas` DAT block) gives a ±1 step only between codes that differ in
> **exactly one** hall line: every legal step is one line changing (001↔011, 001↔101, 010↔011, 010↔110,
> 100↔101, 100↔110). A read torn across a one-line change returns either the old or the new code, **both
> legal**. To land on `%000` or `%111`, a line that is NOT changing must be read wrong -- a real glitch on the
> wire -- and an atomic read that coincided with that glitch would read it wrong too. **So the atomic read stays
> worth doing (it is three instructions instead of six and has no skew), but it is not a PL-69 fix, and "35 %
> wider at 200 MHz" is not a mechanism for illegal codes.** The 200 MHz-only pattern still needs one.
>
> **2. Q1 (pull-up/pull-down) was answerable from our own file,** and was filed as needing a schematic.
> `analyses/BOARD-REVISION-FACTS.md` §1.1 has carried the vendor text since 2026-09-10: each of U, V, W is pulled up
> to 3.3 V through 3.9 kΩ and reaches the P2 through a series 3.9 kΩ, word for word identical on Rev A and Rev B
> (STEPHEN re-supplied it 2026-09-17: *"REV A/B hall signals are conditioned identically"*). **Answer: no internal
> pull is needed, and adding one would hurt.** The P2 "pull" is a weak DRIVE, live only with DIR high
> (p2kb `p2kbArchPinDriveConfiguration`); through the 3.9 kΩ series resistor a 1.5 kΩ pull-up lifts a sensor-held
> LOW to about 3.3 × 3.9/5.4 ≈ 2.4 V (reads HIGH), and a 15 kΩ one to about 0.7 V; pull-downs damage the HIGH
> level the same way (DERIVED, divider arithmetic).
>
> **3. What the network does suggest (DERIVED, unmeasured):** a HIGH line is held through ~7.8 kΩ (pull-up plus
> series), a LOW line by the sensor's output stage through 3.9 kΩ, so coupled switching noise most easily drags a
> HIGH line low -- which predicts `%000` far more often than `%111`. The driver counts both into one
> `hall_illegal_`, so splitting that counter is a free discriminator. And the hall read happens a fixed number of
> CLOCKS after `wait4adc`, while switching edges sit at fixed NANOSECONDS (260 ns dead time) and move within the
> frame with duty: a candidate for a clock-dependent collision, not yet checked against the frame timing.
>
> **IN THIS RELEASE:** STEPHEN 2026-09-17, *"fix hall and charaterize"*. Q2 (a filtered or Schmitt input mode):
> p2kb's `HUBSET` entry documents no input-filter mode; the smart-pin filter field is still to be read.

**Found 2026-09-17**, chasing PL-69 (illegal hall codes on the right motor at 200 MHz only). Raised by
Stephen: *"is the hall sampling edge driven or clocked? are we setting clock correctly?"* **DERIVED from
source and from the domain authority. Not yet confirmed as PL-69's cause.**

**HOW IT IS READ, `src/isp_bldc_motor.spin2` (the `.ctlMotor` loop, and again in `wait4adc` and at
driver start):**

```spin2
                testp   pin_hall_w                  wc  ' read hall effect sensor
                rcl     hall_, #1
                testp   pin_hall_v                  wc
                rcl     hall_, #1
                testp   pin_hall_u                  wc
                rcl     hall_, #1
```

- **CLOCKED, not edge-driven.** `TESTP` returns the pin state **registered two clocks before the
  instruction** (p2kb `p2kbArchIoPinTiming`, Silicon Doc :2005). No edge capture, no smart pin.
- **NO INPUT CONDITIONING.** The hall pins get no `WRPIN`, so no Schmitt mode and no filter -- the
  driver's own comment says *"hall pins are inputs: nothing ever raises their DIR"*.

⭐ **THE THREE BITS COME FROM THREE DIFFERENT INSTANTS.** `TESTP` and `RCL` are 2 clocks each, so the
three samples are 4 clocks apart and the read spans 8 clocks end to end:

| clock | step | W->U span |
| --- | --- | --- |
| 200 MHz | 20 ns | **40 ns** |
| 270 MHz | 14.8 ns | 29.6 ns |
| 300 MHz | 13.3 ns | 26.7 ns |

**A transient shorter than that span can be caught by one read and missed by the others, producing a
triple that never physically existed -- which is exactly `%000` or `%111`.** The span is **35 % wider at
200 MHz**, which is the direction PL-69 observed.

⛔ **THIS IS A CANDIDATE FOR PL-69, NOT ITS ESTABLISHED CAUSE** (doctrine overlay P8). What it does
explain that a clock-rate argument cannot: the sample RATE is 44 kHz at every clock by design (MEASURED
at Visit 3: 44_004 / 44_003 / 44_001 Hz), so rate cannot be the variable, while **skew scales with the
clock period and therefore is**. What it does NOT explain on its own is why only the RIGHT motor showed
it -- that still needs a marginal signal on that motor for the tear to have anything to catch.

**And the clock IS set correctly.** MEASURED at Visit 3: frame rate within 4 Hz of 44 kHz at all three
clocks, dead time 259-260 ns at all three, and the drive pass lands on the 23rd frame at all three.
Nothing is mis-scaled; the tear window is an artefact of the read, not of the clock setup.

### FIX DIRECTION -- one atomic read, and it is CHEAPER than what is there

The hall pins are always three consecutive pins inside a single 32-pin half. For every legal base
(0, 8, 16, 24, 32, 40) the triple is 5-7, 13-15, 21-23, 29-31, 37-39 or 45-47 -- **none straddles the
pin-31 boundary** -- so one port register always holds all three:

```spin2
                mov     hall_, ina          ' or inb, selected once at driver start
                shr     hall_, #hallShift
                and     hall_, #%111
```

**Three instructions instead of six, no tear window, and no clock dependence.** The INA/INB choice and
the shift are computed at init from `pinbase`, where the other pin constants already are. `INA` is read
3 clocks old rather than `TESTP`'s 2, which is immaterial against a 22.7 us frame.

⭐ **Correct by construction (P10):** it removes the mechanism rather than characterising it, and it is
smaller and faster than the code it replaces.

**A second, independent candidate, recorded not proposed:** the hall inputs could use a Schmitt or
filtered pin mode. p2kb notes the P2 has Schmitt input modes but that **no Parallax source states the
hysteresis they produce**, so nothing is claimed for it here.

**Verification, and it needs no new stimulus:** the driver already counts illegal codes on every rung of
every part. Visit 3's evidence was 8 events in two 1-second windows; part A at 200 MHz gives 48 rungs
across both motors, before and after the change.

### ⭐ THREE OPEN QUESTIONS FROM STEPHEN, 2026-09-17 -- answer these before designing the change

**STEPHEN:** *"do we need a pull-up/down effect on the hall pins? we can add this in code... and is
there any smart pin mode that can make reading the hall sensor more accurate? where do the hall pins
sit? are they close enough that we can sample all at the same time?"*

**Q3 -- ANSWERED, and it is the one this entry already rests on.** The halls are `base+5`, `base+6`,
`base+7`: three CONSECUTIVE pins. For every legal base (0, 8, 16, 24, 32, 40) the triple is 5-7, 13-15,
21-23, 29-31, 37-39 or 45-47, and **none straddles the pin-31 boundary**, so one `INA`/`INB` read always
captures all three at the same instant. **Yes -- they can be sampled simultaneously, in software, today.**

**Q1 -- PULL-UP / PULL-DOWN: OPEN, and it may be the missing half of PL-69.** Hall-effect sensors are
commonly open-drain or open-collector and need a pull-up to produce a clean high. The driver sets **no
`WRPIN` at all** on these pins, so whatever the pin's reset drive configuration is, is what they have.
**If the board relies on the P2's internal pull-up and the driver never enables it, the hall lines are
weakly driven** -- slow edges, poor noise margin -- **which is exactly the "marginal signal" PL-90's tear
window needs in order to catch anything, and it would differ between two motors' harnesses.**
- ⛔ **NOT ESTABLISHED. It needs the board schematic** -- whether the 64010 fits its own pull-ups --
  read from `analyses/BOARD-REVISION-FACTS.md` and Parallax's documentation, NOT inferred.
- The P2 can supply one in code: the drive-mode field of `WRPIN` selects 1.5 k / 15 k / 150 k pull-ups
  and pull-downs (`p2kbArchIoPinTiming` cites the datasheet's eight drive modes;
  `architecture/pin-drive-configuration.yaml` is the authority for the encodings).
- **If the board DOES fit pull-ups, adding an internal one in parallel is still a change to a working
  electrical design and is Stephen's to approve, not mine.**

**Q2 -- A BETTER PIN MODE: OPEN.** Two candidates, neither yet checked against p2kb:
- **Schmitt-trigger input** (`P_SCHMITT_A` and variants). p2kb records that the P2 HAS these modes but
  that **no Parallax source states the hysteresis they produce**, so the benefit cannot be quantified
  from the documentation we hold.
- **The global input filters**, selected per pin through `WRPIN`'s input-selector field and configured by
  `HUBSET`. A filter that rejects transients shorter than a chosen window would attack the same noise the
  tear catches, and would do it in hardware rather than by timing.
- ⚠ Either is a `WRPIN` on a pin the driver currently leaves alone, so it changes the pin's reset state.
  **Read the authority before proposing one**, and note that a filter adds latency to a signal the
  commutation depends on -- the trade is noise rejection against hall-edge timing, and the driver's
  position estimate rests on that timing.

**ORDER OF WORK, DERIVED:** the atomic read (Q3) is free, cheaper than the current code, and independent
of the other two -- it should not wait on them. Q1 and Q2 are electrical changes to a working design and
want the schematic and p2kb read first.

---

## Archived

Confirmed-done items are swept out of this file, not kept here. **This list carries outstanding
work only** — that is the one question it answers.

| Archive | Swept |
| --- | --- |
| [`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-17.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-17.md) | PL-3, PL-4, PL-5, **PL-9**, **PL-24** |

An archive file is never re-edited. If an archived item must be reopened, it comes back here as a
**new** item that references the archive.

---

## Open (continued)

> **Filing correction, 2026-09-17.** PL-67 was sitting below *"Removed from this list"*, which
> reads as though it had been withdrawn. **It has not** — it is an open harness gap. It is restored
> to an open section here, and the *Removed* note has moved to the end of the file where it cannot
> capture a later entry the same way. No wording of PL-67 was changed.

### PL-91 -- t0's DEBUG budget sits between the build that went silent (PL-74) and the one that emitted

**Found 2026-09-19 in «#3577»**, adding three cells to `src/test_bench_t0.spin2`. **Open; latent.** It could cost
the whole `t0` load at Visit 6a, the way PL-74 cost it at Visit 4.

**MEASURED** from the compiler's own listing (`pnut-ts -l -d -D BENCH_CFG [-D BENCH_QUIET] test_bench_t0.spin2`,
the `.lst` lines `DEBUG records` and `DEBUG data`), pnut-ts 1.55.8:

| Build | Image | DEBUG records | DEBUG data | On hardware |
|---|---|---|---|---|
| SRC_REV 2, not quiet | 43_792 B | 210 of 255 | 12_898 of 15_872 B (81.3%) | silent, twice (PL-74) |
| SRC_REV 3, quiet (Visit 5) | 40_918 B | 151 | 10_490 B (66.1%) | emitted, 24 PASS |
| SRC_REV 7, quiet (before «#3577») | 43_564 B | 161 | 11_252 B (70.9%) | never run |
| SRC_REV 8, quiet («#3577») | 44_685 B | 166 | 11_595 B (73.1%) | owed to Visit 6a |
| SRC_REV 9, quiet («#3574», prints retired) | 44_337 B | 158 | 11_143 B (70.2%) | owed to Visit 6a |

**What is and is not established.** Both silent runs were INSIDE the limits the compiler reports, so whatever
silenced them is not one of those two limits -- the mechanism is **undetermined** (PL-74's residue). What is
measured is only where each build sits. «#3577» built its cells through one shared emitter so that three cells
cost 343 bytes of DEBUG data rather than the 1_353 a literal line per verdict cost in its first draft.

**Disposition.** (1) «#3574» retires t0 prints for findings already fixed in source (T0-1, T0-2, T0-4, T0-10's
start_return), which recovers budget before Visit 6a -- measure the listing again when it lands. (2) The runner's
PL-74 guard refuses a silent load in seconds, so the failure mode costs a re-run, not a visit. (3) Why an image
inside the compiler's limits emits nothing is a question for Stephen's compiler (P7), raised with him at the
«#3577» hand-back with these numbers.

### PL-67 -- `R2-DETECT-OVERLAP` is owed to a motors-unplugged session, but no build can produce it

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

### PL-95 -- the drive does not integrate hall and current: above mid-range it runs saturated, field parked, and calls it AT_SPEED

> ## THE INSTRUMENT HALF IS LANDED 2026-09-20 («#3580» R18.1); THE DRIVE IS UNCHANGED
>
> Everything this entry says about the drive still stands -- **no control-path statement has been
> touched**, deliberately, so Visit 7 characterises today's drive and not a half-changed one. What has
> changed is what the drive **publishes** and what the harness **asks of it**:
>
> - The driver counts the passes on which each limit ACTED -- `lag_held` (the limiter withheld the field
>   advance) and `duty_capped` (the duty demand exceeded the cap), read through `testGetDriveHealth()`.
>   A count has no ceiling, which is the whole point: `err` is held near `LAG_HOLD` and bounded by its
>   own +-127, and `duty` pins at `duty_max`, so both stop reporting exactly where this entry's
>   behaviour lives. `err` and `duty` stay beside them, unchanged, for continuity with Visits 5 and 6a.
> - The harness differences both across the **transition** and across the **steady window** of every
>   measured rung, as the new `BM-RUNGHL` record. **No cell judges them** -- the acceptance numbers are
>   R18.3's to choose before R18.4 builds against them (doctrine D2).
> - **The command space this entry says is unmeasured is now reachable.** The ladder walk gains a
>   descent and six delta cells -- a small and a large change of speed at low, at the knee and at the
>   ceiling, each taken up and down -- and `LIVE` emits a transition record at last. The "speed DOWN,
>   any" row of the table below stops being empty at Visit 7.
> - The kick's cell is re-judged on current rather than on the clamped error: see PL-87.
>
> **Still owed: the drive change itself (R18.4), and Visit 7 to characterise against.**

**Found 2026-09-20, re-reading Visit 6a's ladder as a RAMP rather than as a set of rungs.** STEPHEN
2026-09-20: *"you are too focused on the braking when the ramps and proper integration of hall and
current into motor drive is much more important"*. He is right, and the data he already had says so
louder than anything in the stop-state work.

**MEASURED, `debug_260919-173751.log`, LEFT reverse ladder, twelve rungs:**

| rung | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| commanded incre (x10^6) | 5 | 10 | 20 | 40 | 60 | 80 | **100** | 120 | 140 | 147 | 155 | 165 |
| `duty_pk` | 2_066 | 2_792 | 4_686 | 9_460 | 14_955 | 21_081 | **24_264** | 24_264 | 24_264 | 24_264 | 24_264 | 24_264 |
| steady current | 13 | 17 | 48 | 213 | 571 | 1_146 | **1_162** | 524 | 140 | 78 | 48 | 65 |
| `err_pk` | 98 | 76 | 73 | 75 | 75 | 75 | 78 | 85 | 95 | 97 | **102** | **105** |

**Three things happen at once at rung 7, and they are the whole finding:**

1. **`duty_pk` reaches `duty_max` (24_264) and STAYS THERE for the top half of the range.** From rung 7
   up the driver has no authority left -- it is commanding full duty and cannot command more.
2. **The steady current PEAKS and then FALLS** -- 1_162 at rung 7 down to 48 at rung 11 -- while the
   commanded speed keeps rising. Current falling as commanded speed rises, at saturated duty, is the
   signature of a drive that has stopped delivering torque.
3. **`err_pk` climbs from 75 toward 105**, i.e. toward `LAG_HOLD` (100). The field is running further
   and further ahead of the rotor, and the limiter parks it there.

⛔ **And the driver reports AT_SPEED throughout.** Rungs 8-12 are a motor that is not tracking its
command, at full duty, with the field parked at a large angular error -- reported as healthy.

⭐ **THIS IS THE SAME STATE AS PL-93**, which was reached through a provoked fault: `duty_max`, `err`
pinned near the limiter hold, `AT_SPEED`, current set by the load rather than by control. **PL-93 is not
an edge case -- it is the normal top half of this driver's speed range**, and a loaded wheel in that
state is what drew 25 A.

⭐ **And it explains the kick (PL-87).** The transition current peaks at **rung 7**, exactly where duty
saturates: every ramp step throws the field further ahead before the rotor can follow, and the step that
lands in saturation is the worst. Stephen feels one at each increment because each increment does it.

**What is actually missing, stated as the design gap rather than as symptoms:**

- **The halls are used coarsely and the field is advanced open-loop between them.** The rotor's position
  is known six times per electrical cycle; between those edges the driver advances `angle_` at the
  commanded rate and hopes. When the command exceeds what the rotor can do, nothing closes that loop --
  the limiter only clamps the reported error.
- **Current is not feedback.** It is read for the S-2 fold-back threshold and for telemetry, and
  nowhere does it inform commutation. Yet the table above shows current is the only observable that
  tracks what the drive is actually doing -- error is clamped, duty saturates, and current is neither.
- **The ramp commands a rate, not an achievable acceleration.** `ramp_inc` advances the commanded
  increment by a fixed step per drive pass regardless of whether the rotor is following, so every step
  is an open-loop lunge and the error absorbs the difference.

### ⭐ THE OBSERVABLES THEMSELVES MUST BE RESPECIFIED -- a measure that tops out is not a measure

**STEPHEN 2026-09-20:** *"if we have measures that are topping out we need to respecify them so they do
not - as they are not useful once topped out"*. That is the general statement of why every instrument
built on this driver has been blind, and it applies to the driver's own control as much as to the bench.

| Observable | How it tops out | What it should be instead -- unbounded where it matters |
|---|---|---|
| `err` (position error) | **Twice over.** The lag limiter holds it near `LAG_HOLD` (100), and the stored field is bounded by its own +-127 representation -- the tree already notes a driver with no limiter simply prints 127. | **The limiting actually applied** -- the field advance the limiter withheld this pass. When the drive is keeping up it is zero; when it cannot, it grows without bound. That is the same information `err` was supposed to carry, in a form that does not stop. |
| `duty` | Saturates at `duty_max` (24_264) and pins there for the whole top half of the range. | **Duty DEMAND before the cap**, or the **deficit** (demand less cap). Once duty pins, the deficit is what says how far past capability the command is; duty itself says only "still pinned". |
| `tr_over` (the kick cell) | Derived from `err`, so it inherits both ceilings -- which is why it read 0 of 22 while the transition current rose seventy-five fold. | Transition **current**, already recorded as `tr_i_pk`. Not clamped. |
| `AT_SPEED` | A boolean meaning "my own increment reached its target" -- true by construction even when the motor never got there. | **Measured rate against commanded rate**, a ratio that keeps informing on both sides of the limit. |

⭐ **This is not only a telemetry fix. The respecified quantities are exactly what the drive needs as
feedback**: "how much am I withholding" and "how much duty did I want beyond what I have" are the two
numbers that say the command is unachievable, and a drive that has them does not need a separate droop
detector bolted on -- it can hold at the achievable rate by construction. The instrument and the control
want the same respecification, which is a sign it is the right one.

**Cog space is a constraint to respect, not a gate** (STEPHEN 2026-09-20: *"you are fretting too much
about cog space, the lut addition just doubled it. we have room we just have to be mindful"*).

**Fix direction (this is the 6.0.0 driver work, and everything else is downstream of it):** close the
loop the halls and the current are already giving us -- correct the field against hall edges rather than
free-running between them, bound the ramp by measured acceleration rather than a fixed increment step,
and use current as the signal for commutation quality rather than only as a fold-back trigger. **A
droop detector, which this list previously proposed, is a guard around this defect and not a fix for
it** (doctrine D1: fix the system, not the display).

### What the user can actually command -- the space the drive has to be good across

**STEPHEN 2026-09-20:** *"if we also weigh-in what a user can command we are going to have to handle
small delta speed-up/slow-down requests as well as large, near max throttle... our drive mech. has to
handle this well"*. That is the acceptance space, and measuring against it exposes two gaps.

⛔ **CORRECTION to an earlier reading of mine: the kick does NOT scale with the size of the speed
change.** MEASURED, the SAME 20x10^6 step taken at six places in the range:

| step | 20->40 | 40->60 | 60->80 | **80->100** | 100->120 | 120->140 |
|---|---|---|---|---|---|---|
| transition current | 234 | 583 | 1_197 | **1_439** | 1_264 | 599 |

**Identical command, six-fold difference in what the motor does** -- peaking at the step that lands on
the saturation knee (rung 7). So the same user action, a modest throttle bump, behaves completely
differently depending on where in the range it is made. **Where the change happens dominates; how big it
is does not.** That is a property of the drive, not of the request, and it is exactly what "handle this
well" has to mean.

⛔ **AND EVERY TRANSITION WE HAVE EVER MEASURED IS A SPEED-UP.** MEASURED across the whole load: **44
speed-up steps recorded, ZERO speed-down steps.** The ladder only climbs, and the LIVE segment
(QTR -> HALF -> TOP) climbs too and emits no transition record at all. **A user slowing from 80% to 60%
is completely uncharacterised** -- and slowing is the direction where the field must fall BACK through
the rotor, which is the opposite sign of error and a different failure if it is wrong.

**The space, and what we hold for each cell:**

| | small delta | medium delta | large delta | near-max |
|---|---|---|---|---|
| **speed UP, low in range** | not measured | MEASURED (rungs 3-5) | not measured | n/a |
| **speed UP, at the knee** | not measured | **MEASURED, and it is the worst case** | not measured | n/a |
| **speed UP, high in range** | not measured | MEASURED (rungs 9-12, already saturated) | not measured | MEASURED, saturated |
| **speed DOWN, any** | **NOTHING** | **NOTHING** | **NOTHING** | **NOTHING** |

**So the acceptance test for the corrected drive is a ladder that also descends, that includes a small
delta and a large one at each of low / knee / high, and that records a transition for every step
including the LIVE-style ones.** The instrument change is small -- `BM-RUNGTR` already carries the right
fields and simply is not emitted for every segment -- and it must land with the drive fix, not after it,
or the fix is verified only on the quarter of the space we happen to have.

**Verification is already paid for on the part we do cover:** the ladder prints `duty_pk`, steady
current, `err_pk` and the transition current per rung, so the table above IS the acceptance test. A corrected drive flattens the
transition current, keeps duty off its ceiling until genuinely at the ceiling, and does not report
AT_SPEED while the field is parked.

### PL-92 -- the bench runner runs the terminal in console mode, so no attended tier can draw its panel

> ⛔ **CAUSE FOUND 2026-09-23 («#3585»): PL-114, the DEBUG data cap.** Neither the runner nor the display name
> was the cause. The panel records sat past image offset 13,684, so the P2 never sent them: the `-u` captures
> of 2026-09-22 carry no `PLOT` byte, and 2026-09-20's create command stopped at that exact byte. **FIXED** by
> the same change, and ✅ **CERTIFIED 2026-09-22 23:37-23:42**: both panels drew through this runner (see
> PL-114). Sweep at the next closeout. The audit table below says the DEBUG budget
> was *"11,470 of 15,872 bytes -- neither near a limit"*. **That row is wrong.** It came from a count, not from
> the subtraction DBG-1 prescribes, and the real footprint was 15,619.

**Found 2026-09-19 at Visit 6a**, when `t0-stopmode` put up no UI and Stephen could not tell what to do.
**MINE, not the tier's.** Open; it blocks every attended tier we have.

**MEASURED (`analyses/bench/2026-09-19/debug_260919-174735.log`):** the image ran -- banner, all eight
`SIGNOFF-DECL` lines, `T0-24,begin`, and the driver's two cogs started. Row 0 announced itself, then
nothing for 95 s until `[TX] s<cr>` (Stephen typing `s` at the terminal) ended the session. The log
carries **zero backtick display commands and zero `PC_KEY`** across about 1,900 key-poll iterations.
The 2026-09-15 `t0-hand` log, whose panel drew on this rig, carries **718 backticks and 487 `PC_KEY`**.

**MEASURED, it is not the tier's code:** a byte scan of the compiled image finds `` `PLOT t0stop TITLE
… SIZE 480 300 POS 60 80 HIDEXY UPDATE `` and its four `LAYER` commands present, in the same shape as
`t0-hand`'s working set. The four `.bmp` assets are committed and present.

**MEASURED:** `tools/bench-run.sh` has run `pnut-term-ts -r <binary> --console-mode
--exit-on-end-session` since 2026-09-10 (`07f2509`), its own comment choosing `--console-mode` over
`--ide` for a batch run. **RECORDED:** the 2026-09-15 run whose panel drew built and ran Tier 0 *"as
built at the bench"* (`VISIT-2-ATTENDED-RESULTS.md`), i.e. not through the runner. **MEASURED:** every
log in the tree that ever carried a display command is dated 2026-09-11 to 2026-09-15 -- thirteen of
them, none later.

**DERIVED (the only part of the mechanism that is settled):** the P2 emits the same bytes whatever the
host does, so the loss is on the host side. With no window there is no `PC_KEY`, so an attended tier
waits forever; the `s` he typed went out over the serial line as terminal input, which no harness reads.

> ## ⛔ MY FIRST CAUSE WAS WRONG, and STEPHEN caught it. `--console-mode` is NOT it.
>
> **STEPHEN 2026-09-20:** *"we have run plot windows before and i'm not sure the --console-mode prevents
> them i'm suspecting a code problem"* -- and he was right on the first half.
>
> **The tool's own help settles it** (P7: a tool's behaviour is read from the tool, never inferred from a
> flag's name -- which is exactly the rule I broke):
> - `--console-mode` = *"Running with console output - adds delay before close"*. It does not suppress
>   windows.
> - `--headless` = *"Run without GUI windows (file logging only, for CI/AI agents)"* -- the flag that
>   would have done it, and one this script has never passed.
> - `--exit-on-end-session` = *"**Headed** batch mode: exit the app (draining in-flight saves/logs) on
>   the end-session marker"*, with the help's own example headed *"Headed batch mode (render windows,
>   then auto-exit)"*.
>
> **And the tree already carried the counter-example I never looked for.** `BENCH-PASS-1-RUNSHEET.md`
> has the operator typing `tools/bench-run.sh char` (there was even a `char-nopanel` tier beside it),
> and the 2026-09-12 `char` log carries a `PLOT` window and 18,738 display commands -- **a panel drawn
> through this runner, with `--console-mode` already in it** (added 2026-09-10, `07f2509`).
>
> **What my argument actually rested on:** every log that ever carried a display command is dated
> 2026-09-11 to 2026-09-15, and the one panel run I checked the provenance of was made by hand. That is
> a correlation, and I reported it as a cause. The `--console-mode` removal below stands on his separate
> ruling that the flag buys us nothing; **it is not the fix for this finding, and this finding has no
> confirmed cause yet.**

### The code audit he asked for -- and it comes back clean

Every check that can be made without the rig, on the committed `t0-*` code:

| Checked | Result |
|---|---|
| A `PLOT` window-create call exists | Yes -- `t0sSetupPanel()`, and it is the FIRST statement of `testT0_24()` |
| It is reached | Yes -- the records emitted on either side of it are in the log |
| `LAYER` calls | Four, one per asset, immediately after the create |
| `UPDATE` calls | `crop 1` + `update` at setup; every frame ends `crop`s then one `update` (`t0sDrawPanel()`) |
| Structure vs the proven panel | Identical to `t0hSetupPanel()`/`t0hDrawPanel()` line for line, differing only in name, size, layer count and asset names |
| Compiled into the image | Yes -- and encoded **identically**: `06 60 'PLOT t0stop'` against `06 60 'PLOT bench'` |
| Assets | 24-bit, uncompressed, 54-byte header -- the same `file` signature as `t0h_*.bmp` and `bc_*.bmp`; committed, beside the source |
| DEBUG budget | 164 of 255 records, 11_470 of 15_872 bytes -- neither near a limit |
| `BENCH_QUIET` | Not referenced anywhere in `test_bench_t0.spin2`; it masks the library's channels only |
| Display name `t0stop` | A legal identifier (letter first, then letters/digits) -- p2kb's own valid examples include `cog0` and `pin56` |

### The sequence comparison he asked for next -- and the one hard fact it produced

**STEPHEN 2026-09-20:** *"the display name is not the problem - look at the overall sequence of debug()
statements routed to the plot window see if they differ in your latest and the working prior"*.

⭐ **MEASURED, and it is the useful result: not one display statement of the WORKING T0-12 panel has
changed since the run that drew it.** `git diff 6b727d1..HEAD -- src/test_bench_t0.spin2` restricted to
`` debug(` `` lines is **all `+` and no `-`**: thirteen added lines, every one of them mine. The
2026-09-15 run that drew was made after the `#ifdef T0_HAND` split (`6b727d1`, 13:24; the run, 14:23),
so **the `t0-hand` tier as it stands today is the same panel that worked.** That is what makes the A/B
below decisive rather than merely interesting.

**The sequences themselves, normalised (name, asset names, constants and numbers replaced) and diffed:
no structural difference.** Same create-directive order (`TITLE`, `SIZE`, `POS`, `HIDEXY`, `UPDATE`),
`LAYER`s then `crop 1` then `update`, and per frame a run of crops ended by exactly one `update`. What
differs is only:

| Difference | Working T0-12 | T0-24 | Against it |
|---|---|---|---|
| Layers | 3 | **4** | `char`'s panel used **5** and drew (2026-09-12) |
| Crops in the first frame | 7 | **13** | more of the same command, and they follow the create |
| Digit blit | inline in `t0hDrawPanel()` | factored into `t0sBlitNum()` | a method boundary, not a stream difference -- execution order still ends on `update` |
| Display name | `bench` | `t0stop` | his call, above; he says it is not the problem |

**So the audit finds nothing wrong with the code, and I could not reproduce the failure from here.**

⚠ **What the domain authority says about this exact symptom, recorded because it is the only documented
cause that fits.** p2kb `p2kbSpin2Debug` `window_name_rules` gives the failure mode as **"SILENT AT BOTH
LAYERS … no display is declared, the window never opens, and every later feed addressed to that name
goes nowhere"** -- which is precisely what the log shows, PC_KEY included. It lists 103 reserved
debug-display words and five rules; **`t0stop` violates none of them** (it leads with a letter and is not
reserved). So either the symptom has a second cause not documented there, or the rules and the
implementation differ for this name. Both are worth knowing, and only the rig can tell them apart.

**The next step is one A/B at the rig, and it costs about a minute.** Run `t0-hand` -- an existing tier
whose panel is known to have drawn on this rig (2026-09-15) -- through `bench-run.sh`, then
`t0-stopmode`:

- **`t0-hand` draws, `t0-stopmode` does not** -> the defect is in the new tier, and the display name is
  the first thing to change.
- **Neither draws** -> the path is at fault, not the tier, and the 2026-09-12 `char` log says the path
  used to work, so what changed under it is the question.

This is the negative control the tier never had (doctrine D2: establish that the simple layer responds
before analysing the sophisticated one).

**Blast radius, and it is now a question rather than a claim:** `t0-hand`, `dual-brake`, `dual-floor`,
`dual-ui` and `t0-stopmode` have all gone unrun through this path since their panels were added, so it
is not known whether any of them draws. **`dual-ui` and the floor tier are Visit 6b's first two loads**,
which is why the `t0-hand` A/B above is worth its minute before that visit rather than during it.

**Why it got past review (the doctrine half).** Overlay P7 says a step a person uses at the bench is
built on the proven technique and reviewed against it. I checked that the *panel technique* was proven
and never checked that the *path that would run it* had ever carried a panel. The runner is part of the
step. **The rule this earns: an attended tier's review covers the whole path -- binary, panel, and the
invocation that will run it -- and "has this path ever drawn a panel?" is a question with an answer in
the logs.**

### `--console-mode` REMOVED 2026-09-19 on his ruling -- and it is NOT this finding's fix

**STEPHEN 2026-09-19:** *"i don't think there is any benefit to our running with --console-mode"*.

⚠ **This removal is his ruling about a flag that buys us nothing. It does not fix the panel** -- see the
correction box above; the flag's documented job is *"adds delay before close"*, and with
`--exit-on-end-session` already draining in-flight saves that delay is redundant. The proposed
attended/unattended mode switch is dropped for the same reason: with nothing on either side of the
switch there is nothing to select, so **`--console-mode` is simply gone and one invocation serves every
tier**:
`pnut-term-ts -r <binary> --exit-on-end-session`. An unattended tier draws no window because it creates
none, not because the terminal was told it may not -- which is the same shape as PL-62's fix, one
value with one meaning, rather than a mode that can disagree with the tier it is running.

- `tools/bench-run.sh`: the flag is removed from the invocation, from the error line that replays it,
  and from both comments; the surviving comment records what it cost and why it went.
- **Run-time proof is owed to the bench.** Nothing here can run `pnut-term-ts` (macOS-only, no board),
  so the next load is the confirmation: an unattended tier must still close itself on
  `DEBUG_END_SESSION`, and an attended tier must draw its panel.
- **First loads that exercise it:** any unattended tier for the first half, then `t0-stopmode` or
  `dual-ui` for the second.

*Superseded fix direction, kept for the record: "give `bench-run.sh` the invocation that yields a GUI
session for attended tiers and keep console mode for unattended ones." The premise that console mode
bought anything was mine, and it did not survive his answer.*

### PL-93 -- after a real fault and a successful recovery, the next drive-up draws 3-4x current and aborts

**Found 2026-09-19 at Visit 6a.** A new defect class, and it was unreachable until this visit: the
fault provocation had never actually faulted before (PL-86), so nothing downstream of a real fault had
ever run.

**MEASURED (`debug_260919-173537.log`, `dual-c` POSTFLT, all twelve traces):** the first trace on each
wheel faults properly (`st,FAULTED, flt,TRUE, e,-101`) and coasts to rest -- LEFT tid 9 `rest_k 278`,
RIGHT tid 15 `rest_k 257`. **Every trace after it aborts**: tid 10-14 and 16-20, on
`reason,ABS_CURRENT`, `value,3_435` (LEFT) and `3_771` (RIGHT) mV against `ABS_ABORT_MV 1_500`
(10 A at 150 mV/A). Half-speed running current is about **900 mV** (Visit 3,
`debug_260916-123957.log` tid 11). The aborted traces carry **no samples at all** -- the abort fires
during the next trial's drive-up, before the instrument arms -- and that includes the e-stop traces,
which write no offsets. The offsets were correctly restored each time (`BM-OFFREST … ok,TRUE`), and the
harness's recovery reports success (`BM-RECOVER … step,RESET, cleared,TRUE, ms,31, st,STOPPED,
flt,FALSE`).

**MEASURED, why it is new:** at Visit 3 the same segment ran **all twenty traces to `end,REST` with
zero aborts**.

**Not settled by these logs:** whether this belongs to the driver's post-fault state or to the
harness's recovery sequence. **It is user-visible either way** -- fault, recover, drive again is an
ordinary thing for an application to do -- so it is chased before the release, and the discriminating
read is the driver's own state after `.resetFault` against what the harness commands next.

**Cost this visit:** it is the reason every cell downstream of the first fault is NOMEAS, including
`R17-DUAL-FLTSTOP-C`.

### ⛔ THE MECHANISM, read from the samples 2026-09-20 -- and it is a DRIVER defect, not a harness one

**MEASURED** (`debug_260919-173537.log`, tid 16, RIGHT wheel, eight consecutive samples k 64-71):

| | reading |
|---|---|
| `i` | **3_742 -> 3_772 mV**, i.e. about **25 A** at the harness's own 150 mV/A calibration |
| `d` | **23_891 -> 24_264**, and 24_264 **is `duty_max`** -- the servo wound to the ceiling and stayed |
| `e` | **pinned at -101**, just under the driver's `\|err\| >= 125` fault test, and right at `LAG_HOLD` (100) |
| `st` | **AT_SPEED** throughout |

**DERIVED, and every step is visible in the numbers above:** the lag limiter holds the field so `err`
sits at its hold threshold and **never reaches the fault test**; the duty servo, seeing an error it
cannot clear, **winds `duty_` to `duty_max`**; S-2's current fold-back computes its threshold as
`max(duty_, duty_floor_) * i_limit_k_ >> 16`, so **at `duty_max` that threshold is at its most
permissive** and no fold-back occurred (duty rose into the ceiling rather than backing off); the
protective stop did not fire either. The driver therefore sat at **maximum duty drawing ~25 A while
reporting AT_SPEED**, and the only thing that stopped it was the harness's external 10 A abort.

⛔ **A USER HAS NO SUCH ABORT.** This is the same shape as a stalled or blocked wheel -- "commanded rate
cannot be reached" -- so it is reachable outside a provoked fault. It is filed here because a fault
exposed it, but **the condition is general and it is the most consequential thing Visit 6a found.**

**Fix direction (driver, and it subsumes PL-86 and PL-46's instrument problem):** a **droop detector** --
compare commanded tick rate against measured tick rate, and when they diverge for N consecutive frames
act on it (fault, or the protective stop that already exists). One mechanism then serves three needs:
the driver gets the protection it is missing, the commutation scan gets the stop condition the limiter
took away (PL-46), and the fault provocation gets a reachable edge (PL-86). The current-limit threshold
scaling with duty should be re-read at the same time: it is most permissive exactly when duty is
highest, which is backwards for this failure.

### PL-94 -- `t0` still loses records at cog-start bursts, despite the quiet windows (PL-85's remainder)

> ⛔ **CAUSE FOUND 2026-09-23 («#3585»): PL-114, the DEBUG data cap, not cog-start bursts.** Rebuilt from
> `60e135b` (44,665 B, the size downloaded), `T0-23,begin,no_bo` ends on byte 13,683, and every later record
> fell past the limit. That is why `R17-T0-NOBOARDSTART` and `R1-T0-EXHAUST`, which are late in the file,
> are the two cells that never reported. It also explains why the quiet windows reduced nothing here.
> **FIXED** by the same change (the `t0` footprint went from 16,004 to 10,511 bytes). ✅ **CERTIFIED 2026-09-22
> 23:42**: `t0` reported 24 of 24 declared cells, `R17-T0-NOBOARDSTART` and `R1-T0-EXHAUST` among them, with no
> line carrying two `CogN` prefixes (`analyses/bench/2026-09-22/debug_260922-234144.log`). Sweep at the next
> closeout.

**Found 2026-09-19 at Visit 6a.** Open. **PL-85 is reduced, not closed.**

**MEASURED (`debug_260919-172524.log`):** the `t0` log declares 24 cells and emits 22.
**`R17-T0-NOBOARDSTART` and `R1-T0-EXHAUST` are declared and never report a verdict.** The source emits
`T0-23,begin,no_board_start` (`test_bench_t0.spin2:1812`); the log carries `T0-23,begin,no_bo` (`:180`)
-- **cut off mid-word**, immediately before the library's refusal line and a `Cog1`/`Cog2` start burst.
`T0-23`'s `end` record and its SIGNOFF never appear. `R1-T0-EXHAUST`'s verdict goes missing inside the
seven-cog exhaustion burst the same way.

**MEASURED, where the fix DID work:** across all ten Visit 6a logs, **zero** log lines carry more than
one `CogN` prefix and **no `BM-*` record is truncated** -- 27,000+ records in the dual harness, clean.
So `cc491bd`'s quiet windows work where they were measured; they are not sufficient in `t0`, which
starts and stops far more cogs than any other tier.

⚠ **Method note, recorded because it nearly shipped as a wrong finding.** My first pass checked only
the dual harness's `BM-*` record shape, found it clean, and concluded PL-85 was closed. The `t0` tier
uses a different record dialect (`T0-nn,…`) and that is where the losses are. **A check that covers one
record dialect has not checked the tier that uses the other** (doctrine D2: suspect the measurement).

**Cost this visit:** PL-73's board-refusal certification is still owed -- the cell ran and the driver
behaved (the refusal line is in the log), but the verdict did not survive the wire.

---

### PL-96 -- an over-length record token prints as `?` with no signal, so a label can be lost silently

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

### PL-104 -- the driver discards a speed command unless it is stopped, at speed or faulted

**Found 2026-09-22 at «#3589»**, reading the command path to design path-preserving speed limiting.

`drvMotor`'s `.notRqStop` accepts a new non-zero command only in `STOPPED`, `AT_SPEED` or `FAULTED`, and
otherwise restores the old target and carries on (`isp_bldc_motor.spin2:4160-4167`). A ramp that is
waiting on its rotor (`lag_s >= LAG_SOFT`) never completes, so an overloaded wheel stays in `SPIN_UP`, and
**every slower command is thrown away**. Only a stop gets through, because a zero target takes another
branch. A user easing off a struggling motor is ignored. That breaks the API's promise (doctrine P3), and
it would silently defeat the hold at the achievable rate and the two-wheel path limiter.

**BUILT 2026-09-22 at «#3583» (DRIVER_REV 2); not yet certified: Visit 8's A-6 judges it.**

**Disposition: designed into «#3589», built by «#3583».** `DRIVE-INTEGRATION-DESIGN.md` §5.3 D-4 removes the
busy test. `.newRqst`'s own branches already handle a change from any running speed and either sign, so
the fix deletes code. Visit 8's A-6 certifies it, and the shipped binary fails that cell by construction.

---

### PL-105 -- the lag limiter holds an overloaded rotor well past its torque peak

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

### PL-106 -- the blocked-motor protective stop cannot be provoked on a lifted rig, so no driver change to it is certified

**Found 2026-09-22 at Visit 8** ([evaluation](analyses/bench/2026-09-22/VISIT-8-EVALUATION.md) §3.4, F-3).
`R16-DUAL-BLOCKED-D` has read NOMEAS (`why,NOT_BLOCKED`) in **every** part-D log on record: 2026-09-17 twice,
2026-09-19, and Visit 8. At the 1 A limit the step sets, a lifted wheel keeps turning, so the front cog never
sees a motor commanded to move and standing still. The cell cannot fail on this rig. The Visit 8 run sheet
wrongly claimed it would certify DRIVER_REV 3's fix: the overload hold's decay now stops at `ramp_min_`, so a
stall keeps the lag the protective stop needs. **That fix is correct by reading and unmeasured.**

**What it would take:** a stall built by construction. For example, a test-only driver command that holds the
field still (an increment of 0 with the bridge driven), or a limit low enough to stop a lifted wheel, found
by stepping it down until the hall ticks stop. Either must be shown able to reach `NOT_BLOCKED`'s negative
case before the cell is trusted. **The floor run («#3591»)** is the other place a real stall can happen.

⚠ **2026-09-22 23:40 -- the stop DID fire on a lifted rig, possibly for the wrong reason (PL-116).** T0-24's
two powered rows each latched `ERR_PLATFORM_BLOCKED` at power 50, straight after the e-stop row's
`clearEmergency()`. Until PL-116 separates "the drive did not resume" from "the test false-fired", this does not
certify the blocked test.

**A construction found, 2026-09-23 (Visit 9b, [evaluation](analyses/bench/2026-09-23/VISIT-9B-EVALUATION.md) §5, G-3).**
`dual-limits-top`'s over-command step lowers the limits to 1 A and commands 245 × 10⁶. On three wheel-directions
the wheel fell to **2–4 % of command** (`h_pct` 2–4, the field walked down to 6–19 × 10⁶), with no fault. The
fold-back limits estimated *phase* current, which rises as duty falls, so once it bites it keeps biting. That is
the nearest a lifted rig has come to "commanded and standing still". The BLOCKED step's 1 A limit at power 50 never
crosses, because a lifted wheel there draws about 0.14 A. The same limit under an over-command does cross. Whether it
reaches a true stall, and so the protective stop, is untried.

---

### PL-107 -- the speed ceilings predate the R18.4 drive, and the feedforward's scale is the same number

**Found 2026-09-22, Visit 8b** ([evaluation](analyses/bench/2026-09-22/VISIT-8B-EVALUATION.md) §3.5, F-11/F-12).
- **The ceilings are now conservative.** The power table's ceiling increments (`confgurePowerLimits()`: 147 × 10⁶
  at 18.5 V) were set when the drive saturated duty at rung 8. On DRIVER_REV 4, rungs 9 and 10 (147, 155 × 10⁶)
  run at duty 22,400–23,900, below the 24,264 cap. Only the 165 × 10⁶ probe rung saturates. MEASURED.
- **One value carries two meanings.** `ff_ceiling := abs(maxFwdIncreAtPwr)`, so D-1's feedforward scale IS the
  command ceiling. Raising the ceiling would silently weaken the feedforward and hand its work back to the trim.
  Doctrine D7: one value, one meaning.

**Disposition:** the limits study Stephen asked for on 2026-09-22 (*"move them purposefully"*,
[plan](plans/LIMITS-RESET-PLAN.md)) owns both.
- **Two meanings: FIXED.** E0 («#3603», `06cdb2c`, DRIVER_REV 5) gave the feedforward the motor's own back-EMF
  line, `HUB_FF_INCR_AT_NOMINAL`. «#3604» (DRIVER_REV 6) keeps that line's slope when `duty_max` moves:
  `ff_ceiling` scales by `duty_max` over the duty the line was measured against.
- **The ceilings: MOVED in «#3605»** from Visit 9 ([evaluation](analyses/bench/2026-09-23/VISIT-9-EVALUATION.md)):
  147 → 165 × 10⁶ at 18.5 V on the raised duty ceiling, the other voltages scaled by voltage. Confirmed by the next
  `dual-limits` run.

---

### PL-108 -- a rotor that slips out of field-weakened synchronism draws a single ~25 A peak

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

### PL-112 -- `demo_single_motor.spin2` still calls `startSenseCog()`

**Found 2026-09-23 in «#3515»**, writing `DEVELOP.md`'s single-motor example. `src/demo_single_motor.spin2:88`
calls `startSenseCog()` after `start()`, and treats a negative result as a failed start. It works: since the front
cog became part of `start()`, `startSenseCog()` starts nothing and returns the front cog's id. But the flagship
single-motor demo is the example users copy, and it shows a call the documentation now describes as kept only so
5.x programs compile. **Fix direction:** drop the call and test `start()`'s own result, as `DEVELOP.md` now shows;
the demo is certified by `tools/build-check.sh`, so the change rides the gate.

**FIXED 2026-09-23 («#3606»):** the call is gone and the demo tests `start()`'s result;
`demo_single_motor` CERTIFIED by `tools/build-check.sh`. The start path is unchanged at run time (`startSenseCog()`
started nothing), so no bench run is owed. Sweep at the next closeout.

### PL-113 -- the user configuration's "NO SUPPORT FOR" note lists voltages the 6.5" motor now supports

**Found 2026-09-23 in «#3515».** `src/isp_bldc_motor_userconfig.spin2:47-49`, in section (1), the part users are
told not to edit, says `NO SUPPORT FOR PWR_6p0V`, `PWR_7p4V` and `PWR_24p0V`, and that a motor given one "won't
go". The 6.5" motor's power table has had rows for all three since the limits reset (scaled from the 18.5 V
measurement, not yet run on our hardware); the DocoEng motor supports 7.4 V and 24 V and refuses only 6.0 V
(`powerTableIndex()`). A user reading the config is told the opposite of what `validVoltageForChoice()` does.
**Fix direction:** replace the note with a pointer to `MOTOR_CHOICE.md`'s table, which states per motor which
voltages exist and which are verified. The file is the one end users edit, so the change is small and visible.

**FIXED 2026-09-23 («#3606»):** the note now points to `MOTOR_CHOICE.md` and names the two voltages that are refused
(DocoEng 6.0 V; 25.9 V for both). Comment only; no constant moved. Sweep at the next closeout.

### PL-114 -- a `-d` image loses every `debug()` record whose bytes lie past offset 13,684: the cause behind PL-85, PL-92 and PL-94

**Found 2026-09-23 in «#3585».** The attended panels, PL-94's lost cells and PL-85's lost verdict all have
this one cause. It is P2-HAZARD-REGISTER **DBG-1**: the DEBUG data has a hard end, and crossing it produces no
error at compile time or at run time. **A record whose bytes lie past image offset 13,684 is cut at that byte,
or never sent at all.** Earlier records print normally, so the log looks like a program that emits some
lines and drops others.

**MEASURED -- the same byte, four times, on three days.** Each image below was rebuilt from the commit that
ran and matches the downloaded size exactly. Each cut ends on the byte before 13,684:

| Run | Commit, image | What arrived | Byte 13,684 is |
|---|---|---|---|
| 2026-09-17 `t0` (PL-85) | `18207c0`, 40,918 B | `...RET_NEG_NOLEAK,measured,TRUE,` then CR LF | the `l` of `,lo,TRUE,` |
| 2026-09-20 `t0` (PL-94) | `60e135b`, 44,665 B | `T0-23,begin,no_bo` | the next letter of `no_board_start` |
| 2026-09-20 `t0-hand` (PL-92) | `a37bac1`, 44,439 B | `` `PLOT bench TITLE 'T0-12 hand-rotation an`` | the `c` of `anchor` |
| 2026-09-22 `t0-hand`, `t0-stopmode` | working tree | no display command at all | below every panel record |

⭐ **The 2026-09-22 run settled which side the loss is on.** It was made with `-u` (`8b94f60`), and
`usb-traffic_260922-215918.log` / `usb-traffic_260922-220003.log` carry **no `PLOT`, `LAYER` or `crop` byte**.
The P2 never sent them, and only cog 0 was running. The panel code is the last in the file, so its records
were the first to fall past the end. The 2026-09-15 `t0-hand` that drew (`6aed714`, 28,520 B) had its panel
records at bytes 10,829-11,028.

**The measure that would have caught it** is the register's own: the `-d` image's size minus the same
build's size without `-d`. The footprint grew from **12,404** (2026-09-15, drew) to **15,619** (2026-09-20,
cut). PL-92's code audit recorded *"11,470 of 15,872 bytes -- neither near a limit"*. That figure came from a
count, which DBG-2 says gives confident wrong answers, and it closed the question that would have found this.

**FIXED 2026-09-23 («#3585»), no output cut** (the register's mitigations; Stephen: *"All can come into play
while not having to reduce the debug output volume we need for testing"*):

- **DBG-16, compile out rather than skip at run time.** `T0_ATTENDED` (set by `T0_HAND` and `T0_STOPMODE`)
  compiles the unattended test bodies out of both attended builds. Before this they were skipped only at the
  call site, and each attended build still carried every one of their records.
- **DBG-2, text from hub, not from the record.** Forty-seven literal `SIGNOFF` / `SIGNOFF-DECL` lines now go
  through `emitCellBool()`, `emitCellDecl()` and the new `emitCellNum()`. A script check rendered each
  removed line and its replacement from the same arguments, and every field matched.
- **Footprints:** `t0` 16,004 -> **10,511**; `t0-hand` 15,674 -> **7,592** (panel at 6,789); `t0-stopmode`
  16,611 -> **8,529** (panel at 7,551).
- **DBG-1, the gate.** `tools/bench-run.sh` builds each tier without and with `-d`, subtracts, and refuses to
  start the terminal over **12,404**: the largest footprint measured to run intact, not the documented cap.
  `tools/build-check.sh` step 5 checks every tier the same way at commit time, through the runner's own tier
  table. Every tier is measured: the largest after `t0` is `char` at 9,572, and `dual` is 6,861.

**Owed at the rig:** `t0-hand` and `t0-stopmode` draw their panels, and `t0` emits all of its declared cells,
`R17-T0-NOBOARDSTART` and `R1-T0-EXHAUST` included. That run is the certification. It stays open until then.

✅ **CERTIFIED 2026-09-22 23:37-23:42** ([evaluation](analyses/bench/2026-09-22/PANEL-CERTIFICATION-EVALUATION.md)).
Binaries from `4d5772b`. Both panels drew, and their USB captures carry the whole stream: `t0-hand` 1 `PLOT`,
3 `LAYER`, 249 `crop`; `t0-stopmode` 1 `PLOT`, 4 `LAYER`, 1,996 `crop`. `t0` reported 24 of 24 declared cells,
30 lines, all PASS, and every record shape matches 2026-09-19's. Sweep at the next closeout.

### PL-115 -- T0-24 times the coast from the SPACE press, and the wheel has already stopped by then

**Found 2026-09-22 23:39** ([evaluation](analyses/bench/2026-09-22/PANEL-CERTIFICATION-EVALUATION.md) §3.3, F3), on
the first T0-24 run with a working panel. Open. **Instrument defect; the drive is not implicated.**

**MEASURED.** Every row reads `after_ticks,0,after_ms,0,half_ms,0`. That includes row 6, where the driver cog is
stopped and the wheel is free. The panel's hand-tick readout, decoded from its digit crops, shows the count
stopping **1.3-2.4 s before the release registered** on every row: row 6 held at 584 from 23:40:47.47 until
the release at 23:40:49.12. `t0sProbe()` starts the coast phase at the SPACE press and ends it after 400 ms
without a hall change, so it only ever timed a wheel at rest. As a result `RESTCOAST`, `STOPGAP` and `FREEREF`
FAIL on the instrument. `RESTSHORT` PASSes with a reading that could not have failed (0 is inside 0-60).

**Fix direction.** Time the coast from the wheel, not the key. Keep the hand phase's tick timestamps, take the
release as the last tick of the hand-driven rate, and let SPACE only end the row ("spin it, let go, press SPACE
when it has stopped"). `FREEREF` must then show a free coast above its 150 ms floor, which is the check that
this instrument can report a coast at all. That check comes first, before any other cell is read (register
INS-14). Key checks ran every 112 ms (median) against PC_KEY's ~100 ms latch; the rebuild should read the key
at least every ~50 ms.

**Owner:** «#3607», the run-time proof of the stop states («#3578», done, built the tier). It is in the release.

### PL-116 -- after T0-24's e-stop row, a lifted wheel did not turn under power 50, and the blocked stop latched

**Found 2026-09-22 23:40** ([evaluation](analyses/bench/2026-09-22/PANEL-CERTIFICATION-EVALUATION.md) §3.3, F4).
Open. **Possibly a driver defect; undetermined.**

**MEASURED.** Both powered rows (the fault provocations, under FLOAT then BRAKE) report
`why,NOT_AT_SPEED,note,no_offset_was_written` and `protective,-2_001`, which is `ERR_PLATFORM_BLOCKED`. So the
driver's blocked test (`isp_bldc_motor.spin2:1895`) saw a commanded motor at `LAG_SOFT` or beyond with no
position change, on a lifted wheel, within 4 s of `driveAtPower(50)`. The panel showed the `POWERED` card (hands
off) on both rows. Both rows come directly after row 3's `emergencyCutoff()` and the teardown's
`clearEmergency()`, and no certified run has ever driven a wheel after `clearEmergency()`: dual-d's
`DST_ESTOP_CLEAR` checks only that the platform stays at rest.

**The two readings, and the discriminator.** Either (a) drive does not resume after an e-stop is cleared,
which is a driver defect in the clear path and in the release, or (b) the blocked test false-fires on a
lifted start at power 50. **Run T0-24's powered rows before its e-stop row** (one build flag), wheels up.
Reaching AT_SPEED and faulting as designed implicates (a); a second block implicates (b). Either result also
bears on PL-106.

**Owner:** «#3607» (the discriminator); a driver change, if (a), is a new task.

**2026-09-23 -- PL-120 is NOT this defect.** An earlier note here said the right bridge being dead explained these
rows. That was wrong: the same rows blocked at Visit 6a, while the dual tiers still drove the right wheel (last on
2026-09-22 19:30). T0-24's powered rows have never been seen to drive, so readings (a) and (b) stand. The
order-swapped run waits until the right wheel drives again (PL-120), then runs unconditionally.

**The limit is a floor, not a measurement of the edge.** 12,404 ran and 15,619 did not; the register's own
measurements put the edge in (13,332, 15,347]. Raise `DEBUG_FOOTPRINT_MAX` only on a larger build shown, on the
wire, to deliver its last record.

### PL-117 -- on a two-wheel platform, a position fault on one wheel does not stop the other

**Found 2026-09-23 in the «#3609» desk study** (`DOCs/analyses/FAULT-STRATA-STUDY-2026-09-23.md` F-1).

**MEASURED (source):** steering's front loop secures both wheels only when a wheel is *blocked*
(`isp_steering_2wheel.spin2:1754-1759`, whose comment reads *"a platform never drives one wheel"*). Nothing in
that loop reacts to one wheel reading `DCS_FAULTED`. A search for `isFaulted` in the file finds only getters
(`:881`, `:1295`, `:1467`); the control search `bFrontProtect` finds `:1755`.

**DERIVED:** the healthy wheel keeps its command, so the platform pivots about the faulted wheel. Whether
the path limiter (`frontLimitPath`, `:1782`) scales the healthy wheel down after the fault is undetermined.

**Fixed 2026-09-23 («#3612», plan R19.2):** `frontPlatformFaultStop()` in steering's front loop ramps the other
wheel to rest on the pass one wheel first reads `DCS_FAULTED`. **Not yet certified:** cell X-5 at Visit 10
(«#3613») must show the healthy wheel's ticks falling along its ramp.

**Owner:** «#3613» (certification).

### PL-118 -- the board cannot measure a phase short's current: the shunt does not carry it

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

**Found 2026-09-23** at Visit 10 pass 1 ([evaluation](analyses/bench/2026-09-23/VISIT-10-PASS1-EVALUATION.md) §3.1).
Open. **Rig evidence; waiting on Stephen's confirm answer.**

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

**Two readings, undetermined:** (a) the right board's switches are not getting pack voltage; (b) a DRIVER_REV 8–12 change
stops the right wheel only. **Discriminator:** the same preflight nudge built at `3403024` (tier `dual-clock-270`, about 1
minute). If the right moves, it is (b), and DRIVER_REV 8–12 get bisected. If not, it is (a).

**Owner:** «#3613». Nothing that drives the right wheel can certify anything until this clears.

### PL-121 -- T0-24's hand rows ended on a clock that started at START

**Found 2026-09-23** at Visit 10 pass 1 (Stephen: *"I press start, and it automatically completes, and I haven't done
anything yet"*). **Fixed the same day.**

**MEASURED:** in `debug_260923-160616.log`, rows 1 and 2 ended after 146 and 217 samples (about 2 s and 3 s, their
`T0_24_HOLD_*_WATCH_MS`), each `displaced,FALSE,aborted,FALSE`. The coast rows' 400 ms rest test counted from START
too, so a wheel not yet spun read as at rest.

**Fix:** `test_bench_t0.spin2` SRC_REV 12. A hold row's bound runs from the first displacement, and a coast row can
end at rest only after its first hall tick. Otherwise only DONE, ABORT or the 120 s cap ends a row. It is certified
at the next T0-24 run.

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

*This section is last on purpose: anything appended to the file lands after it, in a section of its
own, rather than reading as though it had been removed (see the 2026-09-17 filing correction above).*
