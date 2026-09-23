# Punch-list archive — 2026-09-23

Items swept out of [`DOCs/PUNCH-LIST.md`](../../PUNCH-LIST.md) as confirmed done, during the
6.0.0 documentation task («#3515»). Each entry is copied verbatim; its own last status line is
what closed it. Two entries whose fix is in the tree but has never been exercised (PL-14, PL-51)
stay on the active list.

**This file is never re-edited.** If an archived item must be reopened, it returns to the active
punch list as a *new* item that references this archive.

**"What is outstanding?" is answered from the active punch list only** — never re-derived from
this file.

---

### PL-10 -- deferred: `@param`/`@returns` completeness (element->tag direction)

> **FIXED 2026-09-18 («#3517»), and enforced (`check_style.sh` C3f, which also requires every local's
> `@local`, guide 4.4).** About 1,430 missing tags across every authored file, each description written
> against its method's code rather than copied by name: the same name routinely means different things in
> different methods, so each pre-filled guess was checked and many were replaced. Along the way, doc text that
> contradicted the code was corrected (`map()` clamps; `getErrorCtrs()`'s counters are never incremented; a
> reverse drive commented as forward; two file headers naming the wrong file), and descriptions that had been sitting under commented-out code were
> moved back to the top of their methods. With C3f in, every check the gate implements now fails the build.

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

**IN THIS RELEASE (aged-state sweep 2026-09-17).** The 2026-09-10 deferral protected a bench sprint that
has since run five visits. STEPHEN 2026-09-17: *"we deliver code, it MUST match our style guide"* --
4.3 is part of that guide, so the ~621 sites are owed before release, on the authored files only (PL-2).

### PL-11 -- deferred: PUB-before-PRI ordering (guide 3.2)

> **FIXED 2026-09-18 («#3517»), and enforced (`check_style.sh` S3.2).** 235 PUB methods in nine files moved above
> their file's first PRI by whole top-level segment, nothing edited: each PUB carried the comment lines directly
> above it and any empty section-marker `CON` heading it. VAR, DAT, OBJ and constant-bearing CON blocks never
> moved, so the Spin2<->PASM2 hub layout is unchanged by construction; the move verified, per file, an identical
> line multiset, an identical VAR/DAT/OBJ/CON sequence and identical method segments, and all 47 tops compile.

`central:spin2-authoring-guide` 3.2 requires all `PUB` methods to precede all
`PRI` methods in a file. `tools/check_style.sh` does not check this --
detection is trivial, but the *fix* is bulk method reordering, and one of the
**10 files** with PUB/PRI interleaved is `src/isp_bldc_motor.spin2`: 2392
lines carrying the Spin2<->PASM2 hub-offset ABI (see CLAUDE.md, "The
Spin2<->PASM2 shared-memory contract") as an EXCLUSIVE_RESOURCE this sprint.
Bulk-reordering methods in that file is the wrong risk for a cosmetic pass,
and is deferred as its own reviewed change, not folded into #3471/#3472.

**IN THIS RELEASE (aged-state sweep 2026-09-17)** under STEPHEN's 2026-09-17 ruling that delivered code
MUST match the guide (PL-2). The ABI concern is narrower than written: the PASM driver addresses the
`VAR` runs and its own `DAT` image by offset, and moving `PUB`/`PRI` method bodies moves neither. It is
still done as its own reviewed change, with the ABI verified byte-identical by content diff.

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

**Fixed in tree 2026-09-16 («#3556»), Stephen's ruling taken: rename to match, consistent with
every other sibling.** `src/isp_serial_singleton.spin2:529` and `:552` are now `PUB fwoct(nNumber,
digits)` and `PUB fwqrt(nNumber, digits)`. Searched first: no caller anywhere in `src/` named
`foct(` or `fqrt(`, so the rename has no existing call site to break.

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
- ~~Still open: a bench binary that needs quiet timed sections sets its own masks («#3508»).~~
  **Done (aged-state sweep 2026-09-17):** every dual part and the t0 tiers build with `-D BENCH_QUIET`
  (`tools/bench-run.sh`), which sets the quiet masks; the t0 tier emitted and passed all 19 cells that
  way at Visit 5. Nothing of this entry is open.

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

**Closed 2026-09-16 («#3556»), not a defect.** Confirmed by reading `init()`: the motor type is
`user.MOTOR_TYPE` (`src/isp_bldc_motor.spin2:449`, `:459`), a compile-time constant from the user
config, identical for every instance in one build -- there is no runtime path by which two
`isp_bldc_motor` instances in the same top-level program can hold different motor types. The
mixed-type hazard this entry describes cannot occur; it stays as a record of why, per Stephen's
`ADDING_MOTOR.md` scope, not as an open defect.

### PL-25 -- a board reported as not detected makes every current reading negative

**Found 2026-09-12 by the «#3500» agent** (DERIVED from source). `REV_Unknown` leaves
`rSenseForBoard` at -1 (VALUE_NOT_SET), and `getCurrent()` and the telemetry path divide
`sense_i_mV` by it, so current and watts come out negative. This already applied to an empty
pin group; since «#3500» the overlapping-group case reports `REV_Unknown` too. **Fix
direction:** a not-detected board yields a stated "no measurement" value, not a sign-flipped
reading; decide alongside «#3503», which changes the same scale path.

**Fixed in tree 2026-09-16 («#3556»); CERTIFIED at Visit 5 (2026-09-17): `R16-T0-NOBOARD` PASS,
`analyses/bench/2026-09-17/debug_260917-172913.log:184`.** `getCurrent()` and the HDMI
telemetry (`updateHdmiData()`, which had the same divide) share one `PRI scaledCurrent()`: when the
board was never detected it returns `0, 0` instead of dividing by -1. `getCurrent()` alone also
records `ERR_BOARD_NOT_DETECTED` (`-1_018`); telemetry records nothing, since it is not a caller's
command.

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
its local copies.

**Status 2026-09-17 (aged-state sweep):** item 2 is CERTIFIED -- `R10-T0-STOPREADY` PASS at Visit 5
(`analyses/bench/2026-09-17/debug_260917-172913.log:154`): `isReady()`/`isStopped()` answer FALSE on a
stopped instance. Items 1 and 3 have **no isolating run-time proof**: every fault recovery run since
(scan run 8 cleared all 15 of its faults) sends the zero command itself before resetting, so it passes
whether or not `testResetFault()`'s own fix works, and `util_char_motor.spin2` has not run. Both are
TEST-USE paths; whether they earn a cell goes with the bench-emission cleanup, not a visit.

**Status 2026-09-19 («#3574») -- CLOSED. Item 1 was proven all along; the 09-17 note above was an asserted absence.**
- **Item 1 is CERTIFIED, twice.** `R10-SCAN-RSTALONE` is exactly the isolating proof that note said did not exist:
  at each motor's first natural fault the scan calls `testResetFault()` ALONE, with the faulted point's non-zero
  command still set, before any zero command. MEASURED: PASS on both motors at Visit 1
  (`analyses/bench/2026-09-14/debug_260914-114703.log`, `BS-RSTALONE ... ms,31 ... cleared,TRUE` / `ms,30`) and at
  Visit 2 (`analyses/bench/2026-09-15/debug_260915-140255.log`, `ms,31` both). Before the fix a reset alone waited
  out its 2 s timeout.
- **Item 3 is fixed in source and gets no run-time proof, deliberately.** `util_char_motor.spin2`
  `clearFaultByMotMove()` re-applies the popped offset with `testSetFwdRevOffsets()` (read 2026-09-19). The utility is
  not a bench tier and nothing in this release runs it; proving it would take a jog-recovered characterisation sweep,
  which is characterisation work, its own plan (doctrine overlay P10). Its next run is the proof.

### PL-29 -- a `? :` whose branches call methods ran both calls

> **CLOSED BY CONSTRUCTION 2026-09-18 («#3517»).** `tools/check_style.sh` check **T29** now fails any `? :` with a
> call in either branch, enforced on every authored file. It was validated against the known positives before it
> was believed: it found exactly the six `test_bench_scan.spin2` sites and the `test_bench_detect.spin2`
> `groupName(NO_GROUP)` site below, and none of `test_bench_t0.spin2`'s value-only `bPass ? @"TRUE" : @"FALSE"`
> ternaries (its first draft did flag those, by reading the false branch to the end of the line -- fixed to end
> the branch at its enclosing `)` or `,`). All seven sites are rewritten as `if`/`else`; the scan's "deliberately
> left" disposition below is superseded by Stephen's ruling that every authored file meets the guide.

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

> ## ⭐ MEASURED A SECOND TIME 2026-09-17, in a different binary, and this time it DID cost cells.
>
> **"No harm today" expired.** `test_bench_dual.spin2`'s part-D dispatch helpers commanded through the
> same construct, and at Visit 4 the never-started `wheelR` executed and printed on five calls addressed
> to `wheelL` -- see **PL-76** for the log lines, the timestamps and the call-for-line correspondence,
> including the steering half as the negative limb. It is the same mechanism this entry recorded on
> 2026-09-12 from a completely different run, so the behaviour is now MEASURED twice, independently
> (doctrine D2: record the agreement of independent readings as evidence).
>
> **Fixed in `test_bench_dual.spin2` 2026-09-17** (eleven sites, PL-76). `test_bench_scan.spin2`'s
> status-only ternaries are **not** changed: they are harmless today and the scan's logs are diffed
> against earlier runs, which an edit would decertify.
>
> ⛔ **STILL OPEN, and it is what makes this recur: nothing CHECKS for it.** The rule lives in prose in
> three places now, and prose does not catch the twelfth site. A `? :` with a method call in either branch
> is exactly a mechanically-checkable rule for `tools/check_style.sh` -- **assigned to «#3517»**, which
> owns the T1 checker coverage. Until then the entry stays open on that ground alone.
>
> ### ⭐ WHOLE-TREE SWEEP 2026-09-17, and the instrument was validated before it was believed
>
> The first pass was scoped to `test_bench_dual.spin2`, the file where Visit 4 showed the symptom --
> **the site tripped over, not the class** (doctrine D5: treat a shaping observation in its entirety).
> Swept `src/*.spin2` for a ternary with a call in either branch. The first regex returned NOTHING,
> which would have read as a clean tree; it was WRONG, and it was caught by asking for the known
> positive -- the six sites this entry says were deliberately LEFT in `test_bench_scan.spin2`. A search
> that cannot find what is known to be there has not searched (doctrine D2).
>
> | File | Sites | Disposition |
> | --- | --- | --- |
> | **`isp_bldc_motor.spin2`, `isp_steering_2wheel.spin2`** | **NONE** | ⭐ **The SHIPPING objects carry none of this class.** This is the release-relevant result: there is no user-facing defect here. |
> | `test_bench_t0.spin2` | none of this class | Every ternary is `bPass ? @"TRUE" : @"FALSE"` -- addresses of DAT strings, not calls. The tier that gates the 6.0.0 tag is clean. |
> | `test_bench_dual.spin2` | 2 residual | `? whyCode : segWhy()` in two segment ends. `segWhy()` is a pure read, so the cost was a wasted call; **fixed anyway**, because a counter-example inside the file that states the rule is how the rule stops being followed. |
> | `test_bench_char.spin2` | 1 | Values only, already annotated. |
> | `test_bench_scan.spin2` | 6 | Status getters. **Still deliberately left:** the scan's logs are diffed against earlier runs and it is not on the Visit 5 sheet. |
> | `test_bench_detect.spin2` | 1 | **NEW, see below.** |
>
> ⚠ **`test_bench_detect.spin2:1513` -- `(cogGrp == NO_GROUP) ? @sCstNone : groupName(cogGrp)`.** The
> false branch is a CALL, so `groupName(NO_GROUP)` runs even when the guard selected the other limb --
> and the guard exists precisely because `NO_GROUP` is not a valid group. Whether that call indexes out
> of bounds is **not established and is not asserted**; the site is recorded, not fixed. `detect` is not
> on the Visit 5 sheet, and editing it would decertify logs that are diffed against the 2026-09-11 run
> for exactly the reason this entry already gives for the scan. **Fix it when that binary is next built.**

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

**CLOSED 2026-09-17 (aged-state sweep).** The "still open" question that stood here -- why the right
board's sense path gained ~64 mV -- is answered: it was never the board. It was PL-32's one-sample
calibration, and since «#3529» the right motor's zero reads 0.1-1.8 mV. Visit 5's t0 tier certifies
the per-start zero on every channel (`R8-T0-ZXS` I/U/V/W PASS,
`analyses/bench/2026-09-17/debug_260917-172913.log:109-112`). Nothing here is Stephen's to look at.

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
~20 longs of headroom).

**CERTIFIED (aged-state sweep 2026-09-17):** the per-start zero holds within a few mV on every channel
-- `R8-T0-ZXS` I/U/V/W PASS at Visit 5 (`analyses/bench/2026-09-17/debug_260917-172913.log:109-112`),
and the right motor's zero fell from 71-76 mV to 0.1-1.8 mV. The periodic-recalibration trade stays
undecided because nothing has needed it.

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
**CERTIFIED (aged-state sweep 2026-09-17):** the consumer now exists -- `test_bench_dual.spin2` drives the
steering object under `-D BENCH_CFG` -- and at Visit 5 the steering object's travel-per-tick agreed with
the motor object's: `BM-DISTM ... mm_x100,576 str_mm_x100,576 agree,TRUE`
(`analyses/bench/2026-09-17/debug_260917-173141.log:7652`), `R16-DUAL-DISTM-B` PASS.

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
- **CERTIFIED at Visit 1 (aged-state sweep 2026-09-17):** `R2-DETECT-GUARD` and `R2-HOST-DETDIFF` both
  signed off (`analyses/bench/2026-09-14/VISIT-1-SIGNOFF.md`; DETDIFF 14 predicted changes, 0
  unpredicted). The overlap cell `R2-DETECT-OVERLAP` cannot be produced by any build today -- that
  gap is PL-67, not this entry.

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

**Fixed in tree 2026-09-16 («#3556»); CERTIFIED at Visit 5 (2026-09-17):** `R16-T0-RESTZERO` PASS on
both boards, rest current 3.5 mA LEFT and 6.5 mA RIGHT (`T0-20 ... mean_amps_x10k 35 / 65`,
`analyses/bench/2026-09-17/debug_260917-172913.log:176-181`), against 535 (53.5 mA) at Visit 1.
`getCurrent()` and the HDMI
telemetry net `sense_i_mV - restZeroSenseMv` (shared `scaledCurrent()`, PL-25). The rest zero is
sampled at start, once the driver is released and before any drive is posted. At that moment
`stop_mode` is still `init()`'s `SM_FLOAT` with a zero command, so the bridge is off.
- **Construction:** 200 samples, 5 ms apart, the scan and char binaries' own zero. DERIVED:
  `sense_i_mV` is one PWM frame's ADC read with no averaging in the driver, so no shorter window is
  equivalent.
- **Start point:** sampling begins only once hub `drv_state` leaves `init()`'s `DCS_Unknown`. The
  driver's status block-copy writes `drv_state` and `sense_i_mV` together, so that change proves a
  real reading. `init()` resets `drv_state` before every launch, so a restart cannot pass on the old
  instance's state.
- **Bound:** `REST_ZERO_READY_TIMEOUT_MS`, 10 ms, is its own constant. DERIVED from the driver's start
  path: calibration plus the first frame comes to under 1 ms. On expiry `restZeroSenseMv` stays 0 (no
  correction), never a stale value.
- **Cost:** `start()`/`startEx()` take about 1 s longer. The steering `start()` samples both wheels in
  the same ~1 s window, using the motor object's `restZeroBegin()` / `restZeroAddSample()` /
  `restZeroFinish()` steps.

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

**OVERTAKEN -- DONE AND CERTIFIED (aged-state sweep 2026-09-17).** The deferral above was reversed on
2026-09-16 and the contract was built («#3554», «#3555»): both API questions were asked and answered
(STEPHEN 2026-09-16, option B for command methods; protective stop "yes your A"). **Zero `abort` uses
remain in `isp_bldc_motor.spin2` or `isp_steering_2wheel.spin2`** (read 2026-09-17), and Visit 5's t0
tier certifies the error contract (all 19 cells PASS, `analyses/bench/2026-09-17/VISIT-5-RESULTS.md`
§2a). Nothing of this entry is open.

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

**FIXED AND CERTIFIED (aged-state sweep 2026-09-17):** `R16-T0-PINSKEEP` PASS at Visit 5
(`analyses/bench/2026-09-17/debug_260917-172913.log:163`) -- validate-then-start leaves P0-P15 alone.

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

**Certified 2026-09-15 without a re-run, and this is why that is legitimate.** «#3548»'s change to
`isp_bldc_motor.spin2` is **comment-only** — `git show 65bda4b -- src/isp_bldc_motor.spin2` is timing prose,
a stale local's description and a note on the 6.5″ ceiling block; not one executable line moved. The driver
binary therefore produces the *same* `rate_x10` it produced at Visit 2, and the only thing «#3548» changed is
the harness's printed `pred_x10`, scaled by exactly 22/23. So the new ratio is the old ratio × 23/22, which is
arithmetic on MEASURED Visit 2 data, not a prediction:

| Rung | Visit 2 ratio | × 23/22 |
|---|---|---|
| 10M | 0.964 | 1.008 |
| 20M | 0.946–0.962 | 0.989–1.006 |
| 40M–100M | 0.953–0.965 | 0.996–1.009 |
| 120M–165M | 0.956–0.959 | 0.999–1.002 |

Every rung from 10M up lands in the 0.99–1.01 window the fix predicted. (5M stays uninformative: 14 ticks
quantise to ±7 %.) **A `dual-a` re-run would measure the same rates against the same new prediction and do this
same division.** It was dropped from the Visit 3 run sheet for that reason. If a later change touches the drive
pass itself — not its comments — this reverts to owing a ladder.

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

**Visit 3, 2026-09-16** (`analyses/bench/2026-09-16/VISIT-3-RESULTS.md` §3; an older tree, same stop path):
- **All four combinations now trip on the FAULTB stop from 110.25M**, LEFT POS included: LEFT NEG 1,569, LEFT
  POS 1,536, RIGHT NEG 1,534 and RIGHT POS 1,638 mV (`debug_260916-120132.log:445,861,1275,1694`).
- OVERSHT 2 ft rep 1 at 75 % aborted at 1,571 mV (`:1714`), where Visit 2's same rep completed with a 1,570 mV
  peak.
- Trial-1 running peaks were 6.5–12 % above Visit 2. The "LEFT POS never tripped" line above describes Visit 2
  only; the stop sits at the threshold on every combination.
- **The same day on the current tree (`53c1f2b`, `debug_260916-123801.log:447,861,1277,1694`), all four aborted
  again.** The repairs did not touch the stop ramp, so this is the unchanged mechanism. At 50 % the OVERSHT stops
  complete and decelerate 75 ticks from 196 ticks/s, exactly the 254 ticks/s² ramp.
  - STEPHEN's condition for this research, *"after our driver is back in shape"*, is now met: the four repairs are
    certified (`analyses/bench/2026-09-16/VISIT-3-RESULTS.md` §0).

**CLOSED -- FIXED AND CERTIFIED (aged-state sweep 2026-09-17).** Visit 4: 20 stop trials at the same
±110_250_000 peaked at `stop_pk_mV` 971-1_055 against the 1_500 mV abort. Visit 5: `R16-DUAL-STOPCUR-B` PASS
on both motors (`analyses/bench/2026-09-17/VISIT-5-RESULTS.md` §4d). `VISIT-3-RESULTS.md` §6's description of
this as "the driver's largest open behaviour" is history, corrected there.

**Fixed in tree 2026-09-16 («#3558»).** The design is
`DOCs/plans/CURRENT-LIMIT-AND-STOP-DESIGN.md`.
- **Mechanism, from the Visit 2 trace** (`src/logs/_OLD/debug_260915-135838.log:97-199`): the rotor keeps its motoring
  lag through SPIN_DN, and the duty servo regulates that lag angle only. Duty therefore stays up while back-EMF falls, and
  the current rises.
- **Fix, the cause removed:** while ramping down, the driver caps duty in proportion to the field's speed
  (`duty0 × |drv_incr| / incr0`). The cap lifts whenever the rotor trails by `LAG_SOFT`.
- **Backstops:**
  - the fold-back current limit (40 A peak, 27 A continuous phase current, from the MOSFET ratings)
  - the lag-limited ramp: a rotor that leads holds the ramp-down
- **Unloaded deceleration** stays the 254 ticks/s² ramp. A loaded platform may stop later, within the limit.

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
- **CERTIFIED at Visit 3 (aged-state sweep 2026-09-17):** 4 of 4 brake-mode restarts after `clearEmergency()`
  reached AT_SPEED and rested after the e-stop, both motors, both signs (`analyses/bench/2026-09-16/VISIT-3-RESULTS.md`
  §4.2, `debug_260916-123957.log:3492-5599`).

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

**FIXED AND CERTIFIED (aged-state sweep 2026-09-17).** The clock is now part of the tier name --
`dual-clock-200`, `dual-clock-270`, `dual-clock-300` -- so nothing numeric is typed, and refusals go to both
stdout and stderr (`tools/bench-run.sh`). All three clock loads ran COMPLETE at Visit 3
(`analyses/bench/2026-09-16/VISIT-3-RESULTS.md`, logs `123557`, `123637`, `123717`).

### PL-70 -- the single-motor sense task divides by a tick count that is 0 until `start()` runs

**Found 2026-09-16 in «#3554»**, while removing the same construction from `getDistance()` and `getRotationCount()`.

**DERIVED (`src/isp_bldc_motor.spin2`, `updateHdmiData()`):** `tvRpm_x10 := ... / hallTicsPerRotation`. That VAR is
set only by `init()`. `startSenseCog()` does not require `start()`, so a sense task started first divides by 0 on
every pass until the motor is started. What a Spin2 integer or float division by zero yields is UNVERIFIED (the
P2 knowledge base does not state it).

**Fix direction:** read the geometry from `hallTicInfoForMotor()` (compile-time configuration), as «#3554» did for
the getters. It is not fixed there because that task leaves the sense task alone; the front cog («#3513») replaces
this loop and should be built on the compile-time geometry.

**CLOSED BY CONSTRUCTION (aged-state sweep 2026-09-17):** the premise is gone. `startSenseCog()` now starts
nothing -- `start()` always launches the front cog, and `startSenseCog()` only returns its id or -1 with
`ERR_NOT_STARTED` (`src/isp_bldc_motor.spin2:580-592`). No sense loop can run before `start()`, so there is no
pass that divides by an unset tick count.

### PL-72 -- the sense tasks wait 200 ms per pass while a driver is faulted or e-stopped, then wait on a past deadline

**Found 2026-09-16 in «#3513»'s phase-1 plan** (`DOCs/plans/FRONT-COG-IMPLEMENTATION-PLAN.md` §3.4).

**DERIVED:** while a driver reads `DCS_FAULTED` or `DCS_ESTOP`, both sense tasks call `resetWindowAccumulators()`
on every pass. That calls `resetTracking()`, which does `waitms(200)` (steering: twice, one per wheel). The pass then
calls `waitct(senseStartTicks + ticksSenseLp)`, whose target is already about 200-400 ms in the past. p2kb
(`p2kbSpin2Waitct`) says `WAITCT` "blocks execution until system counter matches Tick", which implies a wait for the
32-bit counter to wrap: about 15.9 s at 270 MHz.

**Contradiction, so this is not asserted:** «#3556» records the unfixed e-stop auto-clear at about 125 ms, which could
not happen with a 16 s stall on every e-stopped pass. The recorded measurement outranks this derivation (doctrine
overlay P8). What is certain from the source is a 200-400 ms pass while faulted or e-stopped, against a 7.8 ms period.

**Fix direction:** «#3513» (the front cog) removes the construct: no wait inside the loop body, and a late test before
every `waitct`. No bench run is proposed to characterise it (overlay P10).

**CLOSED (aged-state sweep 2026-09-17):** the front cog replaced both sense tasks («#3513»), and `resetTracking()`
now goes through the bounded request path (20 ms), not a `waitms(200)`. The front cog's pass timing is certified:
`R16-DUAL-FRONTST-D` PASS at Visit 5 (`analyses/bench/2026-09-17/VISIT-5-RESULTS.md` §3).

### PL-74 -- the Visit 4 `t0` binary carried no debug kernel, so the whole tier emitted nothing

**Found 2026-09-17 in «#3561»**, reading the Visit 4 logs. **It is a harness defect, and it is mine** (doctrine
overlay P2) -- not a driver defect and not a compiler defect (P7: presume the compiler is correct).

**MEASURED, `DOCs/analyses/bench/2026-09-17/debug_260917-125221.log`:** the whole log is 19 lines. Line 16 is
`[DOWNLOAD SUCCESS] test_bench_t0.bin | Size: 43780 bytes`; line 18 is `Session Ended`, 14 s later. Not one
program line, and **no `BC-BANNER`**, so the tier could not even be banner-checked.

**The tell is what is absent.** The `t0` log has **no `Cog0 INIT $0000_0FA8 ... jump` lines**. Every other Visit 4
log has them (`char` L18; each `dual` L17-19). Those INIT lines are emitted by the *debug kernel* at load, so
their total absence says the downloaded image carried **no debug kernel** -- i.e. it was built without `-d` --
rather than the program running and staying silent. A silent program would still have produced the INIT lines.

**STEPHEN 2026-09-17:** *"The T0 run didn't emit any debug output. I don't know why. It looks like it compiled
correctly from what I could see with the -d flag, but nothing happened, so that log is pretty sparse."*

**What it costs.** All ten `t0` cells are **NOT_BUILT**, reported as themselves and never as passes
(`task-execution` overlay §8): `R16-T0-BADGROUP`, `PINSKEEP`, `LIMKEEP`, `NOABORT`, `STRNOTSTART`, `STEERCOGS`,
`RESTZERO`, `NOBOARD`, `FRONTFAIL`, `R1-T0-RESTART`. **The error contract («#3554», «#3555») therefore has no
run-time evidence from Visit 4** except the single steering cell that rode the `char` tier
(`R16-CHAR-STEERERR`, PASS). This blocks the 6.0.0 tag.

**Fix direction:** root-cause the `t0` tier in `tools/bench-run.sh` -- whether `-d` reaches that one compile.
Then give the harness a construction that makes the failure impossible rather than detectable (P10): a load that
produces no banner should be refused by the runner before Stephen's time is spent on it, since a banner is the
one thing every tier emits within milliseconds of start.

> ## ROOT-CAUSED 2026-09-17: ⛔ THE MECHANISM ABOVE IS REFUTED. The image DID carry a debug kernel.
>
> **`-d` reaches every tier.** `tools/bench-run.sh` has exactly one compile line and it is
> `"$PNUT" -l -d -D BENCH_CFG ${EXTRA_DEFS[@]} "$BENCH_FILE"` -- there is no per-tier compile and no path
> that omits `-d`. So "it was built without `-d`" was an inference from the missing INIT lines, not a
> reading of the runner.
>
> **MEASURED 2026-09-17, and the sizes settle it.** Compiling `test_bench_t0.spin2` on today's tree:
>
> | Command | Binary |
> | --- | --- |
> | `pnut-ts -l -d -D BENCH_CFG test_bench_t0.spin2` | **43_784 bytes** |
> | `pnut-ts -D BENCH_CFG test_bench_t0.spin2` (no `-d`) | **25_764 bytes** |
> | Visit 4's downloaded image (`debug_260917-125221.log:14`) | **43_780 bytes** |
>
> 43_780 is unambiguously a **debug** build -- it is 18_016 bytes above the non-debug build and four bytes
> below today's, and those four bytes are exactly the one PASM long PL-78's fix added afterwards in
> `be61a7f`. **The compile was right and the image carried the debug kernel.**
>
> ⛔ **So the absence of `Cog0 INIT` does not mean "no debug kernel"; it means the kernel that was there
> never emitted.** That is a download or start anomaly on that one load, and **it is UNDETERMINED** -- the
> whole log is 19 lines, the P2 is not here, and nothing in the tree records what the board did between
> `DOWNLOAD SUCCESS` at 12:52:22.774 and `Session Ended` 13.3 s later. Per doctrine overlay P8, no
> mechanism is offered for it. It has not recurred: the five other Visit 4 loads all show `Cog0 INIT`
> within 20 ms of download.
>
> ### FIXED IN TREE 2026-09-17 -- the runner refuses a load that emitted nothing
>
> The half of the fix direction that survives is the one that does not depend on knowing the cause, and it
> is now in `tools/bench-run.sh`, immediately after the `pnut-term-ts` call:
>
> 1. **no new log** under `src/logs/` -> refuse, naming the tier;
> 2. **no `CogN INIT` line** in it -> refuse, saying every cell in the tier is NOT_BUILT and to power-cycle
>    and re-run. This is the Visit 4 failure, and it is now caught in the seconds after the load instead of
>    in the analysis hours later;
> 3. **INIT lines but not one program line** -> refuse, saying the image started and judged nothing.
>
> **The check is tier-independent on purpose.** It looks for the debug kernel's own `CogN INIT` line, which
> every `-d` image emits at load whatever the tier does next, rather than for a per-tier banner string the
> runner would have to keep in step with six binaries. It **reads** the newest log once and never writes,
> moves or renames it (doctrine overlay P2); the header comment says so.
>
> **The ten `t0` cells are still NOT_BUILT** and are owed to the next visit; that is a run-sheet item, not
> an open defect here.
>
> ### ⛔ IT REPRODUCED 2026-09-17 17:18. Not a one-off load anomaly. The guard caught it in seconds.
>
> **MEASURED**, `src/logs/t0-run.out` and `src/logs/debug_260917-171822.log`: `pnut-ts: Compiling with
> DEBUG`, `Wrote test_bench_t0.bin (43792 bytes)`, `[DOWNLOAD SUCCESS]` -- and **not one `Cog0 INIT`**,
> session ended 5.4 s later. Identical signature to Visit 4.
>
> **Two variables are eliminated by this run**, because it happened on a different machine:
>
> | | Visit 4 | 17:18 re-run |
> | --- | --- | --- |
> | Tree | this clone | a different clone (`.../Projects P2/P2-BLDC-Motor-Control/...`) |
> | Compiler | `pnut-ts 1.55.7` here | **`pnut-ts 1.55.5`**, build 8/30/2026 |
> | Image | 43_780 bytes, debug build | 43_792 bytes, debug build |
> | Result | nothing emitted | **nothing emitted** |
>
> **So it is neither the clone nor the toolchain version.** And the runner's PL-74 guard refused the load
> and said so on the console, which is the one thing that went right: the failure cost seconds instead of
> the tier.
>
> ⭐ **THE NARROWING THAT MATTERS, and it is a record search I should have done before the sheet was
> cut.** `t0` **has never emitted at `SRC_REV 2`.** It ran at Visit 2 under the earlier revision, and has
> failed both times since. `SRC_REV 2` (16 Sep, task 3560) is what added T0-16..T0-22 and with them
> `motorP` and `steer` -- taking this binary to **six `isp_bldc_motor` instances plus a steering object**,
> more than any other tier. It was also the only tier compiled WITHOUT `-D BENCH_QUIET`, so the library's
> nine debug channels were live in every one of those instances.
>
> **MEASURED:** `-D BENCH_QUIET` removes **2_866 bytes** of library debug data from this build
> (43_784 -> 40_918 with `-d`).
>
> ### CHANGED IN TREE 2026-09-17: the `t0` and `t0-hand` tiers are built quiet; `SRC_REV` is 3
>
> **Nothing this binary measures is lost.** The masks quiet the LIBRARY; t0 judges return codes, and all
> ten cells print through plain `debug()` in `test_bench_t0.spin2`, which no channel mask touches.
>
> ⛔ **THIS IS A HYPOTHESIS WITH A TEST, NOT AN ESTABLISHED CAUSE** (doctrine overlay P8). The 255-record
> ceiling that `test_bench_dual.spin2`'s header budgets against is **our own design document's figure,
> not p2kb's** -- p2kb's `DEBUG` entry records no such limit, so it is not quoted here as an authority.
> What is asserted is only the correlation above and the measured byte delta.
>
> **The next run discriminates, either way:**
> - **emits** -> the ten cells land, the 6.0.0 tag is unblocked, and the cause is localised to debug
>   volume in this binary. The residue is then *why* it fails silently rather than at compile time, which
>   is a question for Stephen's compiler and belongs to him (P7).
> - **still silent** -> the instance/channel-volume hypothesis is dead. **Do not run it a third time.**
>   The next step is a bisect build -- t0 with `steer` removed, then with `motorP` removed -- which costs
>   no bench time to prepare and one load to settle.
>
> ### CLOSED AT VISIT 5 (aged-state sweep 2026-09-17): it EMITTED
>
> The quiet `SRC_REV 3` build emitted and **all 19 t0 cells PASS**
> (`analyses/bench/2026-09-17/debug_260917-172913.log`, `VISIT-5-RESULTS.md` §2a). The first branch above
> happened. What stays **undetermined** is *why* `SRC_REV 2` was silent rather than refused at compile time;
> that residue is a question for Stephen's compiler if he wants it, and blocks nothing.

### PL-75 -- the steering front cog's stack is exactly full: `stack_hi == stack_of == 128`

**Found 2026-09-17 in «#3561»**, Visit 4 part D. **MEASURED**,
`DOCs/analyses/bench/2026-09-17/debug_260917-125859.log`. The two `BM-FRONTST` records differ in one field:

```
L67  BM-FRONTST motor,BOTH  passes,18_052 late,0 max_ticks,215_784 max_us,799 slot_us,1_000 stack_hi,128 stack_of,128
L96  BM-FRONTST motor,LEFT  passes,11_653 late,0 max_ticks,169_936 max_us,629 slot_us,1_000 stack_hi,114 stack_of,128
```

The steering object's front cog -- the one servicing *both* wheels in the 3-cog two-wheel form «#3513» ships --
has driven its stack high-water mark to **the full allocation**. The single-motor front cog peaks at 114 of 128
and passes. This is why `R16-DUAL-FRONTST-D` reads `FRONT_LOOP_HEALTH FALSE` for `BOTH` (L110) and `TRUE` for
`LEFT` (L118).

**DERIVED:** zero stack margin. One more nested call, or one deeper path than part D exercised, overruns it.
A high-water mark that has reached its allocation cannot be distinguished from one that has *exceeded* it, so
the true requirement is unknown and may already be above 128.

`max_us 799` against a `slot_us 1_000` budget is 80 % occupancy on the same cog, though `late,0` says it never
missed its slot. The stack is the defect; the occupancy is a number to watch, not a finding.

**Fix direction:** raise the steering front cog's stack allocation, then re-measure `stack_hi` against the new
`stack_of` -- sizing from a measured high-water mark plus margin is the construction that makes the overrun
impossible (P10). Do not relax the criterion.

> ## ROOT CAUSE FOUND IN SOURCE 2026-09-17 -- one constant sizes two different workloads
>
> **`src/isp_steering_2wheel.spin2:218` and `:1416`:**
>
> ```spin2
>     long    taskStack[ltWheel.STACK_SIZE_LONGS]                                  ' :1416
>     longfill(@taskStack, ltWheel.STACK_SENTINEL, ltWheel.STACK_SIZE_LONGS)       ' :218
> ```
>
> **The steering object sizes its own front-cog stack with the MOTOR object's constant.** But the two
> cogs do different amounts of work: the motor's front cog services **one** wheel and peaks at
> **114 of 128**; the steering's services **two** through the `front*()` routines and reaches
> **128 of 128**. One number cannot express both needs, and the heavier consumer has run out.
>
> **Hypothesis raised and REFUTED, recorded so it is not raised again:** that the `longfill` itself
> overruns. It does not -- the array at `:1416` is declared with the same constant the fill uses, so
> the fill is exactly in bounds.
>
> ⛔ **The real danger is that 128 of 128 is indistinguishable from an overrun.** The high-water mark
> is found by looking for surviving sentinel longs. When every sentinel has been overwritten, the
> measurement saturates: **we cannot tell "used exactly all of it" from "used more than all of it".**
> The true requirement is unknown and may already exceed 128.
>
> ### ⚠ WHAT AN OVERRUN WOULD CORRUPT -- and a possible link to PL-77
>
> `taskStack` is the last declaration in its VAR block (`:1416`). The **next** VAR block begins
> (`:1419-1422`):
>
> ```spin2
>     long    deltaTicks
>     long    tickInMM_x100
> ```
>
> **DERIVED, NOT ESTABLISHED -- stated as a hypothesis with its discriminator, not as a finding.**
> Spin2 lays VAR out in declaration order, so a stack overrun past `taskStack` writes into
> `deltaTicks` and then `tickInMM_x100`. **`tickInMM_x100` is the exact variable behind PL-77's
> unexplained ~1000x magnitude:** `convertDistance()` computes
> `fValue := float(nValue) *. float(tickInMM_x100) /. 100.0` (`:737`), and a corrupted
> `tickInMM_x100` scales every distance the steering object reports.
>
> **Why PL-77 could not see it.** `BM-DISTM` prints `mm_x100,576`, but the harness reads that from
> **`wheelL.wheelGeometry()`** (`test_bench_dual.spin2:3239`) -- the *motor* object's value -- and
> **never reads back the steering object's own `tickInMM_x100`.** So the record shows a healthy 576
> while the steering may have been using something else entirely, and the cell cannot tell. That is
> the same "undiagnosable by construction" PL-77 already names, now with a named suspect.
>
> ⛔ **Do not treat this as the explanation.** Two things are unaccounted for: the sign, and whether
> any overrun occurred at all. **The discriminators, in order of cost:**
> 1. Have the harness read back `steering`'s own `tickInMM_x100` and print it in `BM-DISTM`
>    alongside the motor's. Costs one field; settles whether the two ever disagree.
> 2. Enlarge the steering stack (the PL-75 fix), re-run, and see whether the DISTM magnitude
>    normalises. If it does, the two findings share one root cause.
>
> **Fix, correct by construction (P10):** give the steering object its own stack constant sized from
> its own measured high-water mark plus margin, so the two cogs stop sharing a number that cannot
> describe them both -- and so a saturated reading can never again be mistaken for a healthy one.
>
> ### ⭐ DISCRIMINATOR 1 IS BUILT, 2026-09-17, AND THE HYPOTHESIS HAS A MEASURED VALUE NOW
>
> **The hypothesis above is no longer free-floating: `tickInMM_x100` WAS wrong in the same visit, and it
> is measured.** Two independent readings in the part-B log put it at about **-544_643** --
> `getDistance(DDU_M)` returning -14_640 from 2_688 ticks, and `driveForDistance()` refusing every trial
> with `ERR_LIMIT_UNRESOLVABLE` because `304_800 / -544_643` truncates to 0. **It took out the entire
> OVERSHT segment.** Full arithmetic and the log lines: **PL-84**.
>
> **Discriminator 1 -- read back the steering object's own `tickInMM_x100` and print it in `BM-DISTM`
> -- is now in tree** (`testGetTickInMM()`, the `str_mm_x100` field, and the `DISTM` cell fails when the
> two copies differ). Discriminator 2 is the stack fix itself, already in tree.
>
> ⛔ **The link is still NOT established.** A corrupted value and a saturated stack in the same visit,
> with the variable two longs past the stack, is a strong conjunction and not a proof. Visit 5 answers
> it for free: `str_mm_x100` reads 576 with the 256-long stack, or it does not.
>
> ### CLOSED AT VISIT 5 (aged-state sweep 2026-09-17)
>
> `R16-DUAL-FRONTST-D BOTH` PASS on the steering object's own 256-long stack, and `str_mm_x100,576 agree,TRUE`
> (`analyses/bench/2026-09-17/debug_260917-173141.log:7652`). The prediction was made before the run and the run
> met it; that the overrun **wrote** the bad value is still not proven, and nothing depends on proving it.

### The Visit 5 certification banner that closed PL-79, PL-80, PL-82 and PL-83

These four entries end at "fixed in tree"; what closed them is this banner, which stood at the top of the
active list's Open section. It moves here with them, verbatim. (Its PL-78 line refers to an entry that
stays active.)

> ## ⭐ CERTIFIED AT VISIT 5, 2026-09-17 — read `analyses/bench/2026-09-17/VISIT-5-RESULTS.md`
>
> **Zero failed cells and zero NOT_BUILT cells across four loads and 66 cell instances**, against
> Visit 4's 13 FAILs and 10 NOT_BUILT. These entries are closed by measurement:
>
> | Entry | What the run showed |
> | --- | --- |
> | **PL-74** | t0 emits at `src_rev 3` (quiet build); **all 19 cells PASS**, so the 6.0.0 error contract has run-time evidence and **the tag is no longer gated**. Why `SRC_REV 2` was silent is still undetermined. |
> | **PL-75** | `FRONTST-D BOTH` PASS on the steering object's own 256-long stack (was `stack_hi 128 == stack_of 128`, FAIL). |
> | **PL-76** | Closed **by absence**: not one `driveAtPowerEx() motor not started` line in the whole part-D log, where Visit 4 had five. |
> | **PL-77** | `DISTM-B` PASS -- and see PL-84 for what the magnitude actually was. |
> | **PL-79** | `NOFOLD-A` and the new `RATELAW-A` both PASS on both motors (was one compound FAIL). |
> | **PL-80** | `DERATE-D RIGHT` PASS on the derated-and-restored criterion (was FAIL on an underivable window). |
> | **PL-82** | `STOPCUR-B` PASS both motors against the fixed bound (was FAIL on a warming reference). |
> | **PL-83** | `TIMESTOP-D` and `WTIMSTOP-D` both PASS (were NOMEAS `STOP_TIMEOUT` in both forms). |
> | **PL-84** | `str_mm_x100,576` -- the two travel-per-tick copies agree, the OVERSHT segment drives, and **C-3 is measured at last: a 10 ft stop lands 1 tick from a 529-tick target, worst of 4 trials.** |
> | **PL-78 (first half)** | `LAGBND` PASS on every part against the driver's own fault test (115-116 vs 124). |
>
> ⛔ **PL-78's SECOND half -- the slam -- is NOT certified and its evidence is withdrawn: see PL-87.**
> New at Visit 5: **PL-85** (t0's shape truncates DEBUG on the wire), **PL-86** (the fault-API
> provocation trips the abort watching it), **PL-87** (the ladder cannot see a transition kick).

### PL-79 -- `R16-DUAL-NOFOLD`'s band is narrower than its own tick quantisation at rung 0

**Found 2026-09-17 in «#3561»**, Visit 4 part A. **This is an instrument defect and it is mine** (doctrine
overlay P3: how my instrument judges a measurement is instrument design). **It is not a driver finding.**

**MEASURED**, `DOCs/analyses/bench/2026-09-17/debug_260917-131445.log`. `rate_x10` tracks `pred_x10` at every one
of 48 rungs, both motors, both directions, to better than 0.5 % -- except rung 0:

| Rung 0 | ticks | `rate_x10` | `pred_x10` | ratio | Line |
| --- | --- | --- | --- | --- | --- |
| L reverse | -14 | -139 | -133 | **104.5 %** | L15131 |
| L forward | 14 | 139 | 133 | **104.5 %** | L15170 |
| R reverse | -14 | -139 | -133 | **104.5 %** | L15209 |
| R forward | 13 | 129 | 133 | **97.0 %** | L15248 |

Representative of every other rung -- L forward rung 11: `rate_x10 4_415` vs `pred_x10 4_409` = **100.1 %**
(L15203).

**DERIVED:** at rung 0 (`incre 5_000_000`) the entire measurement is 13-14 ticks in a ~1 s window, so one tick
of quantisation is ~7.5 %. **A 97-103 % band cannot be met at rung 0 by construction** -- ±1 tick spans
97-105 %. The criterion is narrower than its own resolution, so `R16-DUAL-NOFOLD-A` reads
`RATE_HELD_NO_FOLD FALSE` (L15294, L15299) on a driver that is in fact tracking perfectly.

**What it hides, and this is the reason to fix rather than waive it** (doctrine D2: a gate that cannot fail on
the thing it names has not passed): while rung 0 fails unconditionally, the cell can never report a *real*
fold-back at any rung, because one compound verdict covers all of them.

**Fix direction:** widen the band at rung 0 to the tick-quantisation floor, or start the band-checked rungs
above the quantisation limit, and report the fold-back half separately from the rate half. **Do not touch the
driver for this.**

> ## FIXED IN TREE 2026-09-17 -- two cells, and the band now carries the rung's own resolution
>
> **The compound verdict is gone. `ladderNoFold()` folds two cells:**
>
> | Cell | Criterion | What it can now say |
> | --- | --- | --- |
> | `R16-DUAL-NOFOLD-A` | `NO_FOLD_AT_BASE` -- the front cog never derated at a base rung | the claim the cell is named for, judged alone |
> | `R16-DUAL-RATELAW-A` (new) | `RATE_MATCHES_LAW` -- the rate against the speed law | a real fold-back at any rung, because rung 0 no longer fails unconditionally |
>
> **The band is the criterion PLUS the resolution.** `rateBandPct()` returns what one tick is worth in
> percent at that rung's own measured count, rounded up: about 8 % at rung 0's 13-14 ticks and 1 % at rung
> 11's 441. So the +/-3 % band becomes 89-111 % where the count is 14 and 96-104 % where it is 441. Every
> Visit 4 reading passes it -- 104.5, 97.0, 100.1 -- and an 80 % fold-back at rung 11 still fails it.
>
> **The fold half is measured on any base rung whose wheel answered**, window or no window: reading
> `testGetCurrentLimitState()` needs no capture. The rate half is measured only where there is a valid
> window, a non-zero tick count and a prediction, so a lost window prints NOMEAS instead of passing by
> silence.
>
> ⭐ **The C-1 certification this data also carries is unaffected** and belongs in the «#3514» write-back,
> as this entry already says.

⭐ **What the same data certifies:** finding **C-1**'s speed law -- 48 rungs, two motors, two directions, under
0.5 % across a 33:1 speed range. That belongs in the «#3514» write-back.

### PL-80 -- `R16-DUAL-DERATE`'s band top sits below the measured lifted-wheel current

**Found 2026-09-17 in «#3561»**, Visit 4 part D. **Instrument defect, mine** (P3), not a driver finding.

**MEASURED**, `DOCs/analyses/bench/2026-09-17/debug_260917-125859.log` L78-80:

```
L78  BM-LIMST motor,LEFT  step,DERATE peak_a,20 cont_a,8 derated,FALSE phase_ma,2_357 limit_k,6_007 value,0
L79  BM-LIMST motor,RIGHT step,DERATE peak_a,20 cont_a,8 derated,FALSE phase_ma,2_632 limit_k,6_007 value,2_602
L80  BM-DSTEP step,DERATE motor,BOTH seg,LIMIT measured,2_602 lo,500 hi,2_500 result,FAIL
```

The measured 2 602 is **4 % over the band top of 2 500**, which is the whole of the FAIL.

**DERIVED:** with `peak_a 20` and `cont_a 8`, a lifted wheel never approaches the 8 A continuous limit, so
derating correctly never fired (`derated,FALSE` on both motors). The cell is judging **phase-current magnitude**
against a band the real lifted-wheel current slightly exceeds, rather than judging **whether derating
happened** -- so its name (`DERATED_IN_WINDOW`) and its test do not agree.

**Fix direction:** judge the property the cell is named for. If a lifted wheel cannot reach the derate
threshold, the honest result is **NOMEAS with a why**, exactly as `R16-DUAL-BLOCKED-D` already does
(`why,NOT_BLOCKED`, L81) and as the LEFT motor's own DERATE cell does (`n,0`, L113). A designed NOMEAS is a
result; a FAIL on an unrelated magnitude is noise.

> ## ⛔ THE DIAGNOSIS ABOVE IS WRONG, corrected 2026-09-17 by reading the step. The FIX DIRECTION survives.
>
> **`measured,2_602` is MILLISECONDS, not milliamps.** `dStepDerate()` hands `dStepDone()` `worstMs`, the
> later of the two wheels' derate times, against `D_DERATE_LO_MS` 500 and `D_DERATE_HI_MS` 2_500. The cell
> is judging **when** the derate arrived, which is the right quantity; it is the **band** that is wrong.
> `phase_ma 2_632` on the same line is a coincidence of magnitude and it is what I read it as.
>
> **What the run actually says**, and every row is consistent with it: RIGHT derated at **2_602 ms**, 102
> ms past the window, so its cell FAILed (L114, `n,1`); LEFT never derated inside `D_DERATE_WAIT_MS`
> 3_500, so `derateMs` stayed 0 and its cell is NOMEAS (L113, `n,0`), exactly as the fix direction asks
> for. `derated,FALSE` in both `BM-LIMST` rows is the state at EMIT time, after the restore -- not
> evidence that neither derated.
>
> ⭐ **The window could never have been generated from the design, and that is the finding.** The front
> cog derates when its ~1 s average of the phase-current lower bound CROSSES the continuous limit. How
> long that takes depends on how far above the limit the wheel sits -- and on a lifted 6.5in wheel it only
> just gets there, so the crossing time is unbounded in principle. Two wheels landed on opposite sides of
> the same window from one drive. A band nobody can derive is a guess wearing a criterion's clothes.
>
> ### FIXED IN TREE 2026-09-17
>
> - `D_DERATE_LO_MS` / `D_DERATE_HI_MS` are **deleted**, and the reasoning above is written where they
>   were (doctrine D5: delete the superseded mechanism in the same change).
> - The criterion is now the claim the cell is named for: **it derated, and the peak limit came back**
>   (`bSfDerateOk := bSfDerateRan and bRestored`). The arrival time is still measured and printed, judged
>   only against `1 .. D_DERATE_WAIT_MS` -- the bound on it arriving at all.
> - **A wheel that never derated no longer fails the BOTH step.** It is NOMEAS in its own cell and is
>   skipped in the step's conjunction, so a rig that can only provoke one wheel reports one measurement
>   and one NOMEAS instead of one FAIL.
>
> **The negative case is intact:** a derate that fires and never restores fails, and a step where neither
> wheel derates is NOMEAS `why,NOT_DERATED` rather than a silent pass.

### PL-82 -- `R16-DUAL-STOPCUR`'s reference drifts 25 % with motor temperature, so the cell fails on the reference, not the stop

**Found 2026-09-17 in «#3514»'s follow-up**, reading the per-sample `BM-STOPCUR` records that the
Visit 4 report had recorded as unread. **Instrument defect, mine** (doctrine overlay P3) -- **not a
driver defect.**

**THE TEST.** `bench/2026-09-17/debug_260917-130012.log`, segment `FAULTB`: 20 trials --
5 values of `ramp_inc` (22, 100, 500, 2_000, 10_000) x 2 directions x 2 motors -- at a constant
`incre` of ±110_250_000 (`BM-TRACE` at `:56, :334, :679, :1000, :1313, :1627, ...`).

**MEASURED, all 20 `BM-STOPCUR` records:**

| Quantity | Range | Behaviour |
| --- | --- | --- |
| `stop_pk_mV` | **971 - 1_055** | **flat, ±4 %**, across both motors, both directions and all five ramp rates |
| `hold_mV_x10` | 9_424 -> 6_995 | **declines ~25 % within each motor's ~2 min run, then RESETS when the other motor starts** |
| `abort_mV` | 1_500 | never approached -- the stop peak sits at about two thirds of it |

**DERIVED -- the decline is thermal, and the reset is what proves it.** LEFT runs `tid` 1-10 from
13:00:25 to 13:02:32 and falls 9_302 -> 6_995. RIGHT then runs `tid` 11-20 and **starts high again
at 9_424** before falling to 7_174. A sagging battery pack would keep sagging across both motors;
**a per-motor reset is each motor starting cool and warming.**

**So the criterion compares a rock-stable measurement against a reference that moves 25 % for
reasons that have nothing to do with stopping.** Cold it nearly passes (`stop_pk` 985 vs hold
930.2, over by 6 %); warm it fails badly (1_031 vs 699.5, over by 47 %). **The stop barely moved --
985 to 1_031 across the whole run.** `STOP_UNDER_HOLD_I` is therefore FALSE for a reason that is an
artefact of its own reference.

**Fix direction:** judge the stop against a **fixed design bound** -- the current limit the design
actually specifies -- not against a hold current measured moments earlier on a warming motor. If a
relative comparison is genuinely wanted, capture the hold reference at the same temperature as the
stop it is compared with, and say in the cell how that is guaranteed. Record the arithmetic in the
cell (compare PL-78's first half and PL-79: **a criterion is an instrument and needs its own
negative case**).

⭐ **ONE REAL PHYSICAL RESULT COMES FREE, and it confirms a source reading rather than resting on
it.** `stop_pk_mV` is **flat across a 455x sweep of `ramp_inc`** (22 to 10_000). That is exactly
what the source predicts: `.rampDn` loads `curr_ramp` from **`ramp_down_`** (a fixed 50_000,
`src/isp_bldc_motor.spin2:529, :3761`) and never reads `ramp_curr`, so **`ramp_inc` governs ramp-UP
only.** The slam analysis in PL-78 rests on that same reading, and this is an independent
measurement agreeing with it (doctrine D2: record the agreement of independent readings as
evidence). It also means **PL-78's fix cannot change stopping behaviour**, which is a useful
control for the next visit.

> ## FIXED IN TREE 2026-09-17 -- a fixed bound, and a THIRD defect found while fixing it
>
> ⭐ **THE THIRD DEFECT: it compared a PEAK against a MEAN.** `scStopPk` is the largest `sense_i` over the
> spin-down; `scHoldIX10` is the **mean** over the AT_SPEED hold. The AT_SPEED ripple alone can make a
> correct stop look worse than the hold, before any thermal drift is involved. Found by reading the fold,
> not by a run, and it is the same class as the drift: the reference was not the thing the claim is about.
>
> **The criterion is now a fixed bound.** `STOPCUR_BOUND_MV = ABS_ABORT_MV` (1_500 mV, 10 A at 150 mV/A),
> and the cell is `scStopPk <= STOPCUR_BOUND_MV` and no absolute-current abort. The criterion token
> changes from `STOP_UNDER_HOLD_I` to `STOP_UNDER_BOUND`, because the name was part of the defect.
>
> **Why THAT number, and what it does and does not do.** It is the bound the UNBOUNDED stop actually
> crossed: *"From 75 %, the same 20-50 % rise crosses the harness's 10 A abort"*
> (`plans/CURRENT-LIMIT-AND-STOP-DESIGN.md` section 1), and two Visit 2 trials aborted outright (PL-55).
> So the negative case is measured, not imagined. **It is a ceiling, not a tight bound, and the entry says
> so rather than implying more:** a stop that crept from 1_000 to 1_400 mV would still pass it.
>
> **What carries the design's own section 3.3 invariant** -- that current FALLS along the ramp instead of
> rising -- is now in the record rather than in the verdict: `BM-STOPCUR` gains `hold_pk_mV` (the hold's
> peak, so a peak is compared with a peak) and `bound_mV`, beside the `hold_mV_x10` this entry showed the
> thermal drift in. A reader sees the whole comparison and the arithmetic behind the verdict.

### PL-81 -- WITHDRAWN SAME DAY: `ticsPerRotation` = 90 was already anchored at Visit 2

> ## ⛔ WITHDRAWN 2026-09-17, hours after being raised. The premise was false.
>
> **I filed this saying "no bench visit has ever anchored it." That was wrong, and Stephen caught
> it:** *"wait, check our logs - we did a manual 3 rev pass... have it?"* We did.
>
> **MEASURED at Visit 2, 2026-09-15**, cell **T0-12**, the hand-rotation anchor
> (`bench/2026-09-15/debug_260915-142347.log`;
> [`VISIT-2-ATTENDED-RESULTS.md`](analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md) §2, whose
> heading reads *"T0-12 — hand rotation, 90 ticks per revolution"*):
>
> ```
> :22   T0-12,begin,told_direction,CW_FROM_HUB,revolutions,3,wheel,RIGHT_P16
> :394  T0-12,started,hall_pin,21,hall_code,6,told_direction,CW_FROM_HUB
> :531  T0-12,end,transitions,270,illegal,0,pos,-270,final_hall_code,6
> ```
>
> **270 ÷ 3 = exactly 90 ticks per revolution = 15 electrical cycles.** The designer's 23 would
> need 414. `final_hall_code` returns to the starting 6 as a whole number of cycles requires, and
> `illegal,0` throughout. **It is a direct count with no library constant anywhere in it** -- the
> one thing the circular checks I listed could not provide.
>
> **So the library is right and nothing is owed.** `getDistance()`, `getRotationCount()`,
> `stopAfterDistance()` and the mm-per-tick constant are all correctly based. The designer's
> *"I think ... like 23"* was hedged and reads as a recollection about hoverboard motors as a family.
>
> **THE PROCESS FAILURE IS THE PART WORTH KEEPING** (doctrine D3, overlay P8). I asserted an
> absence without searching the record that would have shown it. Two stale markers made the absence
> look real: the «#3514» task body still listed *"the hand-rotation anchor for
> hallTicsPerRotation"* among results owed from the certification pass, and I confirmed Visit 4's
> `char` tier carried no such cell -- true, and irrelevant, because Visit 2 had already run it.
> **A run-sheet "owed" marker is a claim like any other, and it is not retired automatically when
> the measurement lands.** Check the bench record before concluding a measurement was never made;
> a search costs seconds and this one would have prevented a filed finding built on nothing.
>
> **What survives from the original entry** is the half that was never in doubt: the designer's
> `electrical = mechanical_12bit x pole_pairs MOD $FFF` method presumes an absolute 12-bit
> mechanical sensor, and **we have three halls giving 6 states per electrical cycle**, so the method
> does not port even though the ±90° principle it serves still holds. That stays live under
> **PL-26** and in
> [`analyses/BLDC-COMMUTATION-PRINCIPLES.md`](analyses/BLDC-COMMUTATION-PRINCIPLES.md).

*Original entry, preserved below as filed.*

### PL-81 (as originally filed) -- `ticsPerRotation` = 90 has never been anchored, and the board designer says it should be 138

**Raised 2026-09-17** from the board designer's note relayed by Stephen, who confirms *"the 6.5" is
the hoverboard motor he refers to"*. Recorded in
[`analyses/BLDC-COMMUTATION-PRINCIPLES.md`](analyses/BLDC-COMMUTATION-PRINCIPLES.md).

**THE CONFLICT.**

| Source | Electrical cycles / mech rev | `ticsPerRotation` | `degreesPerTic` |
| --- | --- | --- | --- |
| The library, `src/isp_bldc_motor.spin2:1464-1466` | **15** | **90** | **4** |
| The board designer, hedged -- *"I think those hoverboard wheels are like 23"* | **23** | 138 | 2.61 |

⛔ **If the designer is right, `getDistance()`, `getRotationCount()`, `stopAfterDistance()`,
`stopAfterRotation()` and the mm-per-tick constant are all wrong by 53 %.** That is
release-blocking for 6.0.0.

**NOTHING WE HOLD DISCRIMINATES THEM, and I checked each candidate** (DERIVED 2026-09-17):

- The distance arithmetic (`mm_x100 576` = 5.76 mm/tick against a 518.6 mm circumference) **divides
  by the 90 under question** -- circular.
- The Visit 4 speed ladder measures **ticks per second**, and ticks/s = electrical-revs/s x 6.
  **That product does not depend on electrical-cycles-per-mechanical-revolution at all**, so the
  <0.5 % agreement across 48 rungs would have looked identical under either number.
- `R4-CHAR-RPM`'s ±1 rpm agreement uses the same `ticsPerRotation` on both sides of the comparison
  -- agreement with itself.

`ticsPerRotation := 90` is a **library constant, i.e. a claim** (doctrine overlay P8), and **no
bench visit has ever anchored it.** The hand-rotation anchor was listed as owed from the
certification pass and Visit 4 did not carry a cell for it.

**THE DISCRIMINATOR, and it is nearly free.** Rotate one wheel through exactly one mechanical
revolution by hand, motor unpowered, and count hall ticks: **90** confirms the library, **138**
confirms the designer and makes this release-blocking, anything else means the sector geometry
itself needs measuring first. No rail power, no commanded motion, no instrument beyond the driver's
own tick counter.

**This is the one open question where the bench can settle something the source cannot**, because
the source only restates the constant under question. It is the named cell owed against the
standing rule that a run must decide something no reading can.

*Note the designer's other number is not in conflict:* their *"little motor ... multiply by 7"* is
a different motor from either of ours (ours are 15 and 4 pole pairs), and their
`electrical = mechanical_12bit x pole_pairs MOD $FFF` method presumes an absolute 12-bit mechanical
sensor. **We have three halls and 6 states per electrical cycle**, so the method does not port even
though the ±90° principle it serves still holds -- see PL-26.

### PL-83 -- `R16-DUAL-TIMESTOP` could not pass in either form: the rest wait was as long as the limit it waited past

**Found 2026-09-17 in «#3563»**, while fixing PL-76. **Instrument defect, mine** (doctrine overlay P3) --
**not a driver defect.**

**MEASURED**, `DOCs/analyses/bench/2026-09-17/debug_260917-125859.log`: `R16-DUAL-TIMESTOP-D` reads
`measured,NA ... result,NOMEAS why,STOP_TIMEOUT` for `BOTH` (L66) **and** for `LEFT` (L95), and both
sign-off cells are NOMEAS (L108, L117).

⛔ **PL-76 attributed these to its own defect. That attribution is withdrawn:** the `BOTH` half is the
steering object, which evaluates no dispatch ternary at all, and it read STOP_TIMEOUT just the same. Two
reasons in the step itself account for both, and neither can be met by any driver:

1. **The wait was the same length as the limit it was waiting past.** `dStepTimeStop()` armed
   `stopAfterTime(D_TIMESTOP_MS)` -- 2_000 ms -- and then called `dRest()`, whose bound is `D_REST_MS`,
   also 2_000 ms. **The wait expired at the moment the stop was due to begin.** `bRest` was therefore
   FALSE on every run, which is what prints `NOMEAS why,STOP_TIMEOUT`.
2. **The criterion ignored its own confirmation dwell.** `waitRest()` returns when `pos` and `hwPos` have
   been unchanged for `REST_CONFIRM_MS` (300 ms), so `restMs` is at least 300 ms past the instant the
   platform actually came to rest -- against a criterion of `lateMs <= D_TIMESTOP_SLACK_MS` (20 ms). Even
   with the wait fixed, a perfect stop would have read about +300 and FAILed.

**THE THEME AGAIN** (compare PL-78's first half, PL-79, PL-80, PL-82): a criterion is an instrument and
needs its own negative case. Four of the five were bounds nobody could derive, compared against the wrong
reference, or narrower than their own resolution.

### FIXED IN TREE 2026-09-17

- The rest wait is `D_TIMESTOP_MS + D_REST_MS` -- the limit, and then the same bound every other step
  gives a stop -- through a new `dRestWithin(side, boundMs)`; `dRest()` is now a one-line caller of it, so
  no other step's bound moved.
- `D_TIMESTOP_LATE_HI = D_TIMESTOP_SLACK_MS + REST_CONFIRM_MS`, **computed from both constants rather
  than restated as a number**, is the criterion and the printed `hi`.
- The reasoning is written into the step, where the next person to set a bound there will read it.

**The negative case is intact:** the unfixed behaviour this cell exists to catch -- the stop BEGINNING at
the limit instead of finishing by it, which task 3559 changed -- lands hundreds of ms late and still
fails.

### PL-84 -- the steering object's own `tickInMM_x100` held about -544_643, and it took out the whole OVERSHT segment

**Found 2026-09-17 in «#3564»**, by reading the Visit 4 part-B log. **This is the discriminator PL-75
proposed and nobody built.** The instrument change is in tree; **the CAUSE is not established and no
driver change is made on it.**

> ⛔ **THIS ENTRY WAS FIRST FILED WRONG, AND BOTH HALVES OF THAT ARE WITHDRAWN.** It said "the OVERSHT
> distance stop still trips the 10 A abort", built on VISIT-4-RESULTS.md section 4d rather than on the
> log. The log says otherwise: **the abort is `tid,25`** -- the fault-API trial's deliberate 180-degree
> offset provocation, which is that stimulus doing its job -- and **not a distance stop at all**. The
> contrast I drew between a "bounded" FAULTB stop and an "unbounded" distance stop compared two things
> that never happened. Stephen caught the deferral that hid it: *"huh? you pended a read of a log?"* The
> original text is not preserved: it asserted a mechanism, and keeping a refuted mechanism where it can
> be quoted is the failure mode this list exists to avoid (compare PL-81, kept because its SUBJECT
> survived; nothing here does).

**MEASURED**, `DOCs/analyses/bench/2026-09-17/debug_260917-130012.log`:

```
L7281  ! ERROR: driveForDistance() rejected eError = -1_012, shorterDistance = 10, eDistanceUnits = 4
L7279  BM-OVERSHOOT tid,23 ... dist_ft,10 tgt,529 l_stop,NA r_stop,NA l_rest,NA r_rest,NA
                              l_trk,2_688 r_trk,2_688 t_stop,NA why,NOT_REACHED
L7280  BM-DISTM     tid,23 ... l_ticks,2_688 l_m,-14_640 l_pred_m,15 mm_x100,576 agree,FALSE
```

- **`-1_012` is `ERR_LIMIT_UNRESOLVABLE`** (`isp_bldc_motor.spin2`, the error enum). `eDistanceUnits 4`
  is `DDU_FT`, so the harness called it correctly.
- **NOTHING MOVED, in any trial.** Every `BM-TS` row of trials 23 and 24 reads `pos,0 hw,0 st,STOPPED
  d,1_600 i,~10` from k 0 to k 501, and `BM-TRACE-END ... end,TIMEOUT`. `R16-DUAL-STOPLIM-B` is NOMEAS
  with `n,0`, which says **no trial in the segment ever produced a stop to measure.**

⭐ **ONE CORRUPTED VALUE PRODUCES BOTH SYMPTOMS, and the arithmetic closes to the digit.**

`ticksForDistance()` (`isp_steering_2wheel.spin2`, the `DDU_FT` arm) computes
`round(3048.0 *. 100.0) / tickInMM_x100` = `304_800 / tickInMM_x100`, and refuses with
`ERR_LIMIT_UNRESOLVABLE` when the result is `< 1`. `convertDistance()` multiplies by the same variable:
`float(nValue) *. float(tickInMM_x100) /. 100.0`.

| Reading | What it needs `tickInMM_x100` to be |
| --- | --- |
| `getDistance(DDU_M)` returned **-14_640** from **2_688** ticks | `-14_640_000 * 100 / 2_688` = **about -544_643** |
| `driveForDistance(10, 10, DDU_FT)` returned **ERR_LIMIT_UNRESOLVABLE** | `304_800 / -544_643` truncates to **0**, and `0 < 1` ✅ |

**Two independent readings, one value, and the second is predicted by the first.** It also disposes of
PL-77's remaining "~1000x and sign-inverted" puzzle: **both the magnitude and the sign are that one
number**, not a conversion defect.

⛔ **WHY THE RECORD COULD NOT SEE IT, which is the instrument finding.** `BM-DISTM` printed
`mm_x100,576` -- a healthy value -- because the harness read it from **`wheelL.wheelGeometry()`, the
MOTOR object**. The steering object keeps its **own copy**, captured from that same call during
`start()`, and nothing outside could read it back. The record showed one copy while the object used the
other (PL-75 named exactly this and called it "undiagnosable by construction").

### FIXED IN TREE 2026-09-17 -- the discriminator, one field, built at last

- **`isp_steering_2wheel.spin2` gains `testGetTickInMM()`**, a TEST-USE read of its own copy.
- **`BM-DISTM` gains `str_mm_x100`** beside `mm_x100`. The two are equal by construction, so a
  difference IS a corrupted copy.
- **The `DISTM` cell now fails on the thing it can see:** `bSfDistMOk` requires the two copies to agree,
  not just the distances. Visit 4's data would have failed it and named the cause.

⛔ **WHAT IS NOT ESTABLISHED, and no change is made on it: HOW the value got corrupted.**

**The leading candidate is PL-75's**, and the conjunction is strong: `tickInMM_x100` is the **second long
past `taskStack`** in the steering object's VAR declaration order, and **the steering front cog's stack
read SATURATED in this very run** (`stack_hi 128 == stack_of 128`, `BM-FRONTST` L67 of the part-D log) --
a mark that cannot be told from an overrun. A stack overrun past `taskStack` writes `deltaTicks` and then
`tickInMM_x100`.

**It is not proof.** It does not show that an overrun wrote **that** value, -544_643 has no established
relation to anything a Spin2 frame holds, and part B and part D are different loads. Naming it as the
cause is the mistake this entry already made once.

⭐ **NOTHING MORE IS OWED BEFORE THE NEXT RUN, and that is the point of building the field now.** PL-75's
fix (the steering object's own 256-long stack) is already in tree. At Visit 5, `str_mm_x100` either reads
576 -- in which case the enlarged stack removed it and the two findings share one root cause -- or it does
not, and the cause is somewhere else with the evidence printed beside it. **Either answer costs one field
and no extra load.**

⭐ **AND THE WHOLE OVERSHT SEGMENT COMES BACK IF IT READS 576.** `R16-DUAL-STOPLIM-B`,
`R14-DUAL-FLTAPI-B` and `R16-DUAL-FLTRETRY-B` were NOMEAS because nothing ever drove, not because their
stimulus was wrong -- so **finding C-3, the distance overshoot, is unmeasured at Visit 4 and is the
segment's primary job.**

**CLOSED AT VISIT 5 (aged-state sweep 2026-09-17):** `str_mm_x100,576 agree,TRUE`, the segment drove, and C-3
is measured -- a 10 ft stop rests 1 tick past its 529-tick target, worst of 4 (`STOPLIM-B` PASS,
`debug_260917-173141.log:7651-7652, :7676`). The fault-API pair stayed NOMEAS for a different reason: PL-86.

### PL-99 -- the ALIGN crossing detector has no hysteresis, so it counts ~5.5x too many crossings

**CLOSED -- CERTIFIED 2026-09-22, Visit 7c pass 2.** All 16 legs of two `dual-align` runs counted
266-269 crossings against 270 physical, with `dropped,0`
([evaluation](analyses/bench/2026-09-22/VISIT-7C-PASS2-EVALUATION.md) §3.2).

**Status 2026-09-22 («#3594») -- FIXED IN TREE, NOT YET RUN.** `test_bench_dual.spin2` SRC_REV 24: a
per-phase hysteresis band sized from the bias read's own noise (largest stray + 4 mV), and each crossing
timed at the midpoint of its raw sign flips, so the band adds no speed-dependent delay. Desk model of the
new `alignCross()` (3 mV noise, the real 0.52 ms channel): **89 crossings of 89** on slow and brisk legs,
where the old detector counted **1,248** on the slow one; timing bias 0.28 deg slow. The first cut timed
at the LAST flip and the model showed it **9.1 deg late** on a slow leg -- caught at the desk, not the rig.
Certified by the next `dual-align` run: `cross` near 270 per leg and `dropped,0`
([run sheet](analyses/bench/VISIT-7C-RUNSHEET.md)).

**Found 2026-09-22 at «#3594», filed by the front ledger's override rule.** The cold hall-zero tier
`dual-align` («#3590») detects back-EMF zero crossings by sign change alone. With no hysteresis band,
sensor noise around the crossing produces a burst of sign flips instead of one edge: the observed rate
is about **5.5x** the number of real crossings, and the crossing buffer overflows before a leg
finishes.

**Why it is here and not fixed in «#3594».** The override rule: the deliverable wins unless it is
genuinely blocked, and the instrument defect in front of me goes to this list with its evidence
instead of being fixed because it is the thing in front of me. Left to instinct I would have fixed
this first -- it is the more interesting problem -- and the bench pass would have gone unbuilt.

**What it would take:** a hysteresis band on the crossing detector, sized from the measured noise
amplitude in the crossing region (**not** from the peak, see PL-100). Both defects are one task and
should be fixed together, because the clip criterion is what would tell you the band is right.

**Cost if left:** the ALIGN tier cannot run, so `Z` is never settled absolutely and cold. It is not
blocking today -- `Z` is held at **-3.6 +/- 0.4 deg** from four scan self-locations and is
speed-invariant within its own spread -- but the absolute, whole-circle, zero-current measurement is
the one that would retire the question rather than bound it, and it also stays unavailable for the
Doco motor when that effort starts («#3562», «#3592»).

---

### PL-100 -- the ALIGN clip detector judges peak railing when only the crossing region must be clean

**CLOSED 2026-09-22, Visit 7c pass 2 -- the criterion is right, and its first run found a different
defect, PL-103.** The band test failed five legs; each one's Z matches its clean twin within 0.3°, and
each had a band inflated by a bias read taken while the wheel still coasted. The criterion judges the
right region; what it is fed is the problem.

**Status 2026-09-22 («#3594») -- FIXED IN TREE, NOT YET RUN.** The crossing region is defined as each
phase's **band** -- resting level +/- its hysteresis -- which is where every crossing is detected; a phase
whose band reaches a rail disqualifies its leg (`R18-DUAL-ALIGN-CLIP`, crit now `BAND_NOT_RAILED`).
Railing inside the sample pair either side of a crossing was considered and rejected as the criterion:
the crossing is timed to one sample regardless, so a railed neighbour cannot move it, and on brisk legs it
would have discarded most falling edges. Peak railing is still reported, as `rail_pm` per leg, which also
retires the shakedown's S-5 (the clamped count that read 99,999 on every leg). Negative case, desk model:
a phase resting at 18 mV is refused.

**Found 2026-09-22 at «#3594»**, alongside PL-99 and in the same instrument.

`R18-DUAL-ALIGN-CLIP` exists so that a flattened back-EMF waveform cannot pass as a measurement. It
judges **peak** railing -- whether the waveform tops out at the rail. But the hall zero `Z` is derived
from **where the waveform crosses zero**, not from its amplitude, and the crossing region is the only
part of the trace the measurement reads.

**So the criterion is wrong in both directions.** A trace whose peaks rail but whose crossings are
clean is a perfectly good `Z` measurement that this cell would **fail**; a trace whose peaks are fine
but whose crossing region is noisy or flattened is a bad measurement this cell would **pass**. The
second is the dangerous one -- it is a cell that cannot fail on the path it exists to police, which is
PL-98's shape appearing in a second instrument.

**What it would take:** judge the clip criterion over the crossing region only -- the samples within
the interpolation window either side of the sign change -- rather than over the whole trace. Fix with
PL-99: the two are the same task, and the crossing-region statistic this needs is also what sizes
PL-99's hysteresis band.

**Cost if left:** even once PL-99 is fixed, the tier's own guard against a bad measurement does not
guard the thing that makes the measurement bad. `Z` would be reported with a verdict that means
something other than what the sheet says it means.

---

### PL-101 -- the duty servo holds a 21-degree band, not a setpoint, because its gain truncates

**RESOLVED IN DESIGN 2026-09-22 by «#3589»** (`DRIVE-INTEGRATION-DESIGN.md` §5.1-§5.3; built by «#3583»,
certified by Visit 8's A-3 and A-4).
- **The band is real only for a slowly changing error.** At running speed the 43-count hall sawtooth
  dithers it into a point: mean error 48 at every rung from 40 to 120 × 10⁶ (MEASURED, the pass 2 ladder).
- **The band and the 18 / 4 asymmetry are NOT the start surge's cause.** The desk model removes both and
  still hunts at the shipped servo's effective gain. The cause is an integral-only servo whose gain
  exceeds what the rotor's low-duty stiffness supports.
- D-2 replaces the servo with a symmetric, untruncated trim, so the band is gone by construction.

The history below is what was believed when the entry was raised.

**Raised in weight 2026-09-22, Visit 7c pass 2: this is now a prime suspect for the START SURGE.** The
surge is the servo HUNTING as the ramp accelerates -- `e` swinging -35 to -84 and duty 3,600 to 6,200 on
a ~150 ms cycle, a current peak at each swing's top, in both runs
([evaluation](analyses/bench/2026-09-22/VISIT-7C-PASS2-EVALUATION.md) §4.3). A band with no restoring
force inside it, plus gains of 18 up and 4 down, is the shape of a limit cycle. «#3589» decides the
servo; the START trace certifies it, judging swing amplitude rather than duty timing.

**Found 2026-09-22 at «#3600»**, reading the servo to seed a start at it.

The servo adds `((|err_| - SERVO_SETPOINT) * duty_up) SAR 8` to duty each pass (`isp_bldc_motor.spin2`,
drvMotor after `.noFault`). With the setpoint 42 and `duty_up` 18, **anything from 42 up to 56 adds
exactly 0**, while anything below 42 subtracts at least 1 (SAR rounds toward minus infinity). So duty
is steady anywhere in **|err_| 42-56, i.e. 59-79 deg**, and only rises from 57. MEASURED: Visit 7c's
four START traces first moved duty at |err| **57-59** (`2026-09-22/VISIT-7C-EVALUATION.md` sec 5).

**Why it matters.** Steady-state field placement is `setpoint - lead + const` only to within that band:
where in the 21 deg the servo sits depends on how the load and the ramp brought it there, not on any
knob. The lead `L` the scan measures is therefore measured against a setpoint that is itself a band, and
«#3589»'s "which knob carries the lead" design has to decide whether the drive should hold a *point*.
It is a pattern nobody chose by design (P10): an artifact of integer truncation, not a deadband anyone
specified.

**What it would take:** a decision in «#3589», not a patch here -- either round the servo step (a
symmetric band of about +/-7) or carry a fractional duty accumulator (no band). Either changes steady-state
behaviour of a working mechanism, so it is designed and certified, never slipped in (D5). «#3600»'s start
seed, which seeded a start at the band's upper edge, was measured at Visit 7c pass 2, did not remove the
surge, and was removed; `SERVO_SETPOINT`, `SERVO_DUTY_UP` and `SERVO_ENGAGE` stay as the names of the band.
