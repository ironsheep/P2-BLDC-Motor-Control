# P2-BLDC-Motor-Control — Punch List

Active outstanding work. Confirmed-done items are swept to a dated archive by
`punch-list-maintenance` at sprint closeout.

Opened 2026-09-09 by the `bootstrap-conventions` / `baseline-health` bootstrap.

---

## Open

Confirmed-done entries swept on 2026-09-23 are in
[`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-23.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-23.md), and those
closed by the 2026-09-26 release audit are in
[`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-26.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-26.md).

### Release burn-down — 2026-09-26

The owner's rule for 6.0.0 (Stephen, 2026-09-26): *"What we need is not an eye towards looking for things we
can address, but an eye towards whether we have everything we need to meet the criteria for the features that
we're trying to release in 6."* Only work that makes a 6.0 feature (README.md "Latest Changes", v6.0.0) operational
is chased; everything else is recorded and waits. Each remaining entry carries its status under its heading.

**Release — chased**

| Entry | What it is | What closes it |
| --- | --- | --- |
| PL-78 | The platform jolts ("slams") at each speed change | R17-DUAL-TRKICK-A PASS on the current driver (last FAIL at Visit 8b, 183/182 mV) |
| PL-87 | The instrument that measures that speed-change kick | Same cell as PL-78, judged on the current driver |
| PL-106 | The stop that protects a blocked wheel has never been seen on a blocked wheel | A blocked-wheel cell that trips SR_BLOCKED (the floor run «#3576» has none today) |
| PL-143 | The command timeout cuts short a drive whose own stop limit already bounds it | Stephen's ruling, then the doc or code follows it |

**Awaits certification** (fix built, not yet run)

| Entry | What it is | What closes it |
| --- | --- | --- |
| PL-14 | The voltage argument to `start()` used to be ignored | A code-reading sign-off or a t0 cell |
| PL-51 | The steering getter for distance speed returned the wrong value | A cell, or a code-reading sign-off |
| PL-52 | `getPower()` kept reporting power after a stop | A cell, or a code-reading sign-off |
| PL-66 | Re-sending the same power did not clear a fault | FLTRETRY once dual-b provokes with `testForceFault()` (PL-119) |
| PL-93 | After a fault and recovery, the next drive drew 3-4x current | The loaded floor run |
| PL-95 | The drive ran saturated above mid-range and still reported AT_SPEED | The kick (PL-87) and the loaded floor run |
| PL-111 | A serial host could not clear a protective stop | A provoked protective stop (PL-106) |
| PL-132 | The blocked-wheel stop shorted the phases even under coast | The floor run |
| PL-144 | The two-wheel path limiter cycled the platform between crawl and full | Pass 7 dual-d PATH-HUNT = 1 |
| PL-146 | Part D read a stalled wheel's events before its fold-back released | Pass 7 EV-FOLDBACK 0 bad |
| PL-147 | The two "is it following?" readings used different commands | Pass 7 NOTFOL-D PASS |

**Watch**

| Entry | What it is | What closes it |
| --- | --- | --- |
| PL-120 | The right board's high side sometimes delivers no voltage; the start check refuses it correctly | Pass 7 times its recovery; evidence so far points at the board, not the driver |

Ancillary, recorded but not chased for 6.0: PL-7, PL-12, PL-16, PL-19, PL-20, PL-21, PL-23, PL-27, PL-31, PL-37,
PL-43, PL-44, PL-46, PL-53, PL-54, PL-60, PL-63, PL-64, PL-65, PL-67, PL-68, PL-71, PL-96, PL-97, PL-98, PL-102,
PL-103, PL-105, PL-108, PL-109, PL-110, PL-118, PL-119, PL-126, PL-134, PL-135, PL-136, PL-139, PL-145.

### PL-7 — Six blocks of prose are maintained in two or more documents

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (duplicated documentation prose)

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

### PL-12 -- latent: `check_pri_docs` conflates "has a trailing comment" with "is a comment line"

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (style-gate tooling, latent)

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

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: no cell; certify by code reading or a t0 cell.

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

### PL-16 -- `util_char_motor.spin2` drive helpers: comment says 10 s, constant is 5 s

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (characterisation utility comment)

**Found 2026-09-11 while building `src/test_bench_char.spin2` («#3497»).**

`src/util_char_motor.spin2:455` and `:476` (lines updated 2026-09-26; first filed as `:379` and `:392`):

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

### PL-19 -- `test_bench_char.spin2` drives the right wheel in motor frame, but captions it in robot frame

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench harness captions)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench harness accumulator)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench harness quiescent hold)

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

### PL-23 -- bench binaries print booleans as numbers

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record formatting)

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

### PL-27 -- the Doco motor's offset and speed-ceiling tables were characterised while board detection was broken

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (Doco motor, after 6.0)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (commutation scan instrument)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (unused bench panel assets)

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

### PL-43 -- scan run 6 went silent under a load step, and the watchdog did not speak

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench silence; rig supply)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench harness trap captures)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (commutation scan instrument)

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
- **2026-09-26:** D6/D8 moved to PL-98.

### PL-51 -- the steering object's `getMaxSpeedForDistance()` returns the max speed, not the max speed for distance

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: no cell.

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

**Fixed in tree 2026-09-16 («#3556»).** `getMaxSpeedForDistance()` (`src/isp_steering_2wheel.spin2` ~:1383-1390; line updated 2026-09-26, first filed as `:769-775`)
now calls `rtWheel.getMaxSpeedForDistance()`, matching `driveForDistance()`'s own call. The serial
object was not checked for the same getter -- out of this task's scope.

### PL-52 -- `getPower()` keeps reporting the last power after the motor is stopped, against its own doc

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: no cell.

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record builder)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (test program, Stephen's call)

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

**2026-09-26:** the header is fixed (`src/test_dual_motor.spin2:3` now reads `test_dual_motor.spin2`); only the
unreachable body remains (the bare `repeat` at `:86`, then `:87-117` including `wheels.stop()`).

### PL-60 -- the left board's `ph_x10` reading sags with load and the right board's does not

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (board telemetry reading; DMM check)

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

### PL-63 -- the right motor's quarter-speed NEG float stop never confirmed rest, in either rep

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench stop-rest reading)

**Found 2026-09-15 in Visit 2.** Minor.

**MEASURED:** traces 25 and 28 end `why,NOT_REACHED` (`debug_260915-134805.log:7888,8787`), although
both reached STOPPED after 19 ticks, like every other quarter-speed stop. Every other STOPMODE trace
confirmed rest.

**Consequence:** the C-4 table has no time to rest for that one cell. Its tick count is complete.

**Fix direction:** read those two traces' last samples for the value that kept changing (`pos`, `hw`
or both), then decide whether the stillness rule or the reading is at fault.

### PL-64 -- the attended-test UI is out of step with what each test needs, and `dual-ui` failed itself

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (attended bench UI)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench plan labels)

**Found 2026-09-15 in Visit 2** (`analyses/bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` §3). Minor.

**MEASURED:** UICHECK's plan record says `finds AC` (`debug_260915-142103.log:26`); FLOOR's says `finds S-9a`
(`debug_260915-142650.log:26`).

**DERIVED:** FLOOR is the part that finds AC, and UICHECK finds none; S-9a belongs to part C.

**Fix direction:** correct the two labels in `src/test_bench_dual.spin2` at its next revision.

**FIXED IN TREE (aged-state sweep 2026-09-17):** `tokFinds` carried one extra S-9a, shifting FLOOR and UICHECK
by one; corrected in the SRC_REV 12 rebuild (`analyses/ATTENDED-UI-AUDIT-2026-09-15.md` §7). Visible in the
next attended log's `BM-PLAN`.

### PL-66 -- a faulted motor stays faulted when the caller sends the same power again

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: FLTRETRY cannot certify until dual-b's provocation uses testForceFault (PL-119).

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench provenance tooling)

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

### PL-71 -- the DocoEng motor's minimum forward increment is `0 - VALUE_NOT_SET`, which is 1

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (Doco motor, after 6.0)

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

### PL-78 -- the lag error clamps at 115-116 against a 110 bound, and commanded velocity is not rate-limited (the slam)

> **6.0 status (2026-09-26 audit):** RELEASE — the speed-change kick. Stephen ruled the slam not shippable (2026-09-17); R17-DUAL-TRKICK-A was still FAIL at Visit 8b (183/182 mV) and has not been judged on the current driver.

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

### PL-87 -- the ladder's err_pk is a STEADY-WINDOW statistic, so no cell can see a transition kick

> **6.0 status (2026-09-26 audit):** RELEASE — the speed-change kick. Stephen ruled the slam not shippable (2026-09-17); R17-DUAL-TRKICK-A was still FAIL at Visit 8b (183/182 mV) and has not been judged on the current driver.

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

---

## Archived

Confirmed-done items are swept out of this file, not kept here. **This list carries outstanding
work only** — that is the one question it answers.

| Archive | Swept |
| --- | --- |
| [`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-17.md`](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-17.md) | PL-3, PL-4, PL-5, **PL-9**, **PL-24** |
| [plans/archive/PUNCH-LIST-ARCHIVE-2026-09-26.md](plans/archive/PUNCH-LIST-ARCHIVE-2026-09-26.md) | the 50 entries closed by the 2026-09-26 release audit (PL-142 fixed the same evening) |

An archive file is never re-edited. If an archived item must be reopened, it comes back here as a
**new** item that references the archive.

---

## Open (continued)

> **Filing correction, 2026-09-17.** PL-67 was sitting below *"Removed from this list"*, which
> reads as though it had been withdrawn. **It has not** — it is an open harness gap. It is restored
> to an open section here, and the *Removed* note has moved to the end of the file where it cannot
> capture a later entry the same way. No wording of PL-67 was changed.

### PL-67 -- `R2-DETECT-OVERLAP` is owed to a motors-unplugged session, but no build can produce it

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (detection harness gap)

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

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: the kick (PL-87) and the floor run remain.

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

**2026-09-26:** R18.4 was built and measured unloaded at Visits 8, 8b, 9 and 9b; what remains is the loaded floor run and the kick, PL-87.

### PL-93 -- after a real fault and a successful recovery, the next drive-up draws 3-4x current and aborts

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: the loaded case needs the floor run.

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

**2026-09-26:** R18.4 was built and measured unloaded at Visits 8, 8b, 9 and 9b; what remains is the loaded floor run.

---

### PL-96 -- an over-length record token prints as `?` with no signal, so a label can be lost silently

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record vocabulary)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record vocabulary)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (scan sign-off cells)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (capability not in 6.0)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (alignment tier instrument)

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

### PL-105 -- the lag limiter holds an overloaded rotor well past its torque peak

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (study; needs sub-sector angle)

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

> **6.0 status (2026-09-26 audit):** RELEASE — the protective stop (and SR_BLOCKED) has never been measured on a blocked wheel; it fired once on a dead bridge (2026-09-24, before DRIVER_REV 20). Needs a blocked-wheel cell (floor run «#3576» has none today).

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

**2026-09-24:** the protective stop fired about 1 s in on the dead right bridge (VISIT-10-DUALFAULT-T0-EVALUATION.md §4), before DRIVER_REV 20 made it honour the stop mode (PL-132); a blocked wheel has still never been measured.

---

### PL-108 -- a rotor that slips out of field-weakened synchronism draws a single ~25 A peak

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (outside the published speed range)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (ramp-rate criteria study)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (crawl-duty tuning study)

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

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: needs a provoked protective stop (PL-106).

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

### PL-118 -- the board cannot measure a phase short's current: the shunt does not carry it

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (board limit; external sensor)

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

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench fault provocation)

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

> **6.0 status (2026-09-26 audit):** WATCH (release-relevant) — the right board's high side intermittently delivers no voltage; the start check refuses it correctly (certified); evidence points at the board, not the driver; pass 7 times its recovery.

**Found 2026-09-23** at Visit 10 pass 1 ([evaluation](analyses/bench/2026-09-23/VISIT-10-PASS1-EVALUATION.md) §3.1).
Open. **Rig evidence; Stephen confirmed both boards share one supply (2026-09-23); see the dated updates below.**

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

**Reading (a), no supply, is REFUTED.** STEPHEN 2026-09-23: *"both boards are hardwired to distribution, if one gets
power they both do."* So this is a defect in our code, and DRIVER_REV 8–12 is where it entered. Checked and cleared by
reading:
- the parameter and status contract (22 and 20 longs, same order on both sides);
- the LUT loader count (label-derived);
- the pack pin;
- the preflight code (unchanged);
- `forwardIsReverse()` (power sign only);
- every pin write for a pin-base dependence.

**MEASURED 2026-09-23 17:48, `debug_260923-174816.log` (`spin`, current driver):**
- **The right wheel turns and its board is fine**: `SP-PHASE,phase,FWD,wheel,RIGHT,power,50,ticks,-453,...,MOVED`,
  and REV 454.
- Its start check passes: `healthFailed = $0000_0000, ... @probeMv = 789 784 788 788 783 787 788 783 787`.

So the harnesses that fail are the ones that differ. Every one of them (dual, T0) auto-detects the board (`spin`
forces Rev B) and builds with `-D BENCH_QUIET` (`spin` does not). **Both factors are CLEARED:** `spin-auto` and
`spin-quiet` (`debug_260923-180445.log`, `-180517.log`) drove the right 453–454 ticks each way. So the cause is in the
dual (and possibly T0) harness path, and in `dual-start` it shows inside `steering.start()`
([evaluation](analyses/bench/2026-09-23/PL-120-SPIN-EVALUATION.md)). **Next:** «#3615» dumps both drivers' shared runs
at the start check and at the preflight nudge, inside that harness, and lets `dual-fault` carry on with the wheel that
moves. It rides on Visit 10 pass 2.

**2026-09-23 19:23, Visit 10 pass 2 — DID NOT REPRODUCE.** The right wheel drove in every run
([evaluation](analyses/bench/2026-09-23/VISIT-10-PASS2-EVALUATION.md) §3.1, §3.3). Its first `BM-ABI*` dump reads the
same 22 parameters as the left. Everything since pass 1 has run DRIVER_REV 13 and harness src_rev 37–38; pass 1 ran 12
and 36. **Undetermined** between a change in that range and a transient rig state. **Watch:** the dump stays in every
START lifetime and every PREFLT, so a recurrence is captured on its first run.

**2026-09-24 16:15, pass 3 re-run — RECURRED, SECOND FORM** ([evaluation](analyses/bench/2026-09-24/VISIT-10-PASS3-RERUN-EVALUATION.md)
§4). In `dual-fault` the right drove at PREFLT (`ticks,18,moved,TRUE`). Then all 12 of its own-object trials timed out
with the phases at 15–170 mV (`pos,0`). Then it drove again through the steering object at 16:20:47. So this form
follows the left wheel's trials, on the standalone right-wheel path. The shared driver image is **cleared by
reading**. No dump fell in a failing lifetime. **Built:** `test_bench_dual` src_rev 41 dumps the wheel's driver runs at
any FLTRESP timeout (`BM-ABI* where,TIMEOUT`), so the next recurrence is captured while it fails.

**2026-09-24 21:21, Visit 10 `dual-fault` at 62366a5 -- RECURRED, AND THE DUMP LANDED**
([evaluation](analyses/bench/2026-09-25/VISIT-10-DUALFAULT-T0-EVALUATION.md) §4).
- **MEASURED:** the right drove its own trials 13–16 (40 and 80 × 10⁶, two full shorts from speed). From trial 17
  (21:24:33, its first 120 × 10⁶ start) it produced no motion in 8 fresh driver lifetimes.
  - Trial 17's phase reading rose to 2_194 mV as the drive started, then drained to 18 mV within about 200 ms while
    duty rose to 5_101. The DC-link current stayed at 0–9 mV throughout.
  - Trials 18–24 read 30–50 mV from their first frame (`BM-TS ... ph`).
  - The protective stop latched about 1 s into each: the TIMEOUT dump reads `drv_state,7`, `e_stop,-1`, `pos,0`,
    `lag_held,1_852`.
  - The closing platform trial (steering) at 21:26 shows the right at 14 ticks/s against the left's 217.
- **Then at 21:29, in a fresh program load (`t0-stopmode`), the right drove normally**, powered rows included.
- **CLEARED:**
  - *Orphan cogs:* every lifetime's driver took cog 3 and its front cog took cog 4 (`Cog3/Cog4 INIT`). A leftover cog
    would have pushed them to 5 and 6.
  - *The LA marker pins:* every use is inside a `{ ... '}` comment block (no symbol in the compiler listing).
  - *Board detection leaving a pin driven:* `pinfloat()` always follows `pinhigh()` after 1 ms.
  - *A supply loss:* ruled out by Stephen's rig fact (one distribution).
- So the failing state survives driver restarts within one program and is gone after a reload. **Undetermined**
  whether time or the reload clears it.
- **NEXT (built for the next pass):**
  - A dump at the first 150 ms of commanded drive with no hall tick, before the protective stop overwrites the state.
  - A same-run recovery probe after a no-motion failure: a 2 s drive at 40 × 10⁶ in a fresh lifetime every 20 s for
    2 minutes, logging phase voltage and current. It decides time against reload.
  - A `dual-fault-rightfirst` tier, which decides whether the left's trials are a precondition.

**2026-09-25 11:41, pass 4 `dual-fault-rightfirst` at 2783921 -- RECURRED ON THE FIRST DRIVE OF A FRESH LOAD**
([evaluation](analyses/bench/2026-09-25/VISIT-10-PASS4-EVALUATION.md) §2, §4).
- **MEASURED:** `BM-PREFLT,...,motor,RIGHT,...,ticks,0,hw_ticks,0,moved,FALSE`, before any left trial. The wheel was
  retired, so all 12 right trials and both platform trials printed `NOT_RUN ... MOTOR_RETIRED`.
- **MEASURED:** its PREFLT dump shows `lag_held,637` and `duty_capped,1_474`. The same wheel's five healthy PREFLT dumps
  show 0 and 165–189. Every parameter matches the healthy dumps.
- **MEASURED:** the next program load, 3 minutes later (`dual-start`), drove the right normally in every lifetime.
- **Settled:** the left's trials are **not** a precondition.
- **Corrected:** "gone after a reload" was too strong, but this run shows only that **one** drive failed. The harness
  started the right once and never retried it (PL-136), so a transient first-drive failure is not ruled out. The next
  two program loads turned the right in every start: 20 starts, 6 walk legs, 36 winding pulses.
- **Still open:** whether time clears it inside one program, and what the phases do during the failing drive. Neither
  diagnostic could fire (PL-136).

**2026-09-25, desk read of the pin path (read-only survey).**
- **The pin set-up has no dependence on the pin group:**
  - pins base+8..13 are u_l, u_h, v_l, v_h, w_l, w_h;
  - the high sides run in `pwmt`, the low sides in `pwmn` (inverted);
  - dead time is in software;
  - only the driver cog writes them, and every bridge state writes Y only.
  Nothing else in `src/` touches P16–P47. So no code path found treats base 16 differently from base 32.
- **The measured levels contradict the "low sides off" hypothesis** stated in the pass 4 evaluation. Two readings
  sit below the right's own 56–62 mV coasting floor:
  - the lead probe's 11–27 mV driven (pass 1);
  - the 18 mV drain at 21:21, with duty in BR_DRIVE.

  Only a conducting low side pulls a phase below the float level. **DERIVED, moderate confidence: the high-side
  drive is what fails.** Candidates:
  - the Rev B high-side gate supply or bootstrap/UVLO on the right board;
  - the high-side outputs P25, P27 and P29 not reaching it.
  The one fact against hardware is that a later load has always cleared it.
- **Survives a driver restart, not a reload, and is not in the dumps:** the shared driver image (`bias`, `fram`,
  `hall_angles`, `deltas`), which both motor instances share and `init()` rewrites before each launch. **Next dump
  should carry these.**
- The pass 5 sheet's signature row was corrected to this reading before any pass 5 log was read.

**2026-09-25 19:52-20:11, Visit 10 pass 5 at 24d2cb9 (DRIVER_REV 25) -- STRUCK TWICE AFTER DRIVING, OUTLASTED A RELOAD,
AND START REFUSAL CAUGHT IT** ([evaluation](analyses/bench/2026-09-25/VISIT-10-PASS5-EVALUATION.md) §2, §3).
- **MEASURED, the fault tier did not see it:** `dual-fault-rightfirst` `BM-FRRECSUM,...,r_pf,NO_FAIL`. The right drove
  all 13 of its own lifetimes (40-120 × 10⁶, shorts, coasts, graded shorts) and both platform trials.
- **MEASURED, death 1 (`dual-start`, about 20:05:04):** life 5's walk BACK leg, right
  `end,OTHER,...,peak,0,...,lag,325`. The left was healthy but scaled by the path limiter, `peak,-3`. Lives 6-10: every
  start refused after its 3 retries (about 4.0 s each):
  `BM-SREFUSE,...,r_err,-1_020,...,r_fail,$001C`, with the left clean (`l_fail,$0000`).
- **MEASURED, death 2 (`dual-d`, between 20:10:22.9 and 20:10:29.2):** after ESTOP_LATCH/ESTOP_CLEAR the platform never
  reached speed. Then ORDERED..DIRSIGN were `NOT_REACHED`, `BM-EVTOT ... l_path,2,r_path,56`, and the LIMIT segment's
  start was refused, `r_fail,$001C`.
- **MEASURED, a reload did NOT clear it:** `t0-stopreason`, a fresh program load at 20:11:43 (about 80 s after death 2),
  was refused at its first start: `healthFailed = $0000_001C`. **This falsifies "a later load has always cleared it"**,
  the one fact recorded above against a hardware cause.
- **MEASURED, time did:** `dual-start-phaseneg` loaded about 100 s after death 1 and probed the right healthy in every
  lifetime (`p_uu,796 ... p_ww,798`).
- **So:** the failing state survives driver restarts **and** a program reload, and clears within about 80-100 s. That
  weighs against anything the program image holds (the shared driver image included, which the reload rewrites) and
  toward a state in the right board that recovers with time. A time-recovering high-side gate supply fits the corrected
  reading.
- **The probe fits the corrected reading, but the signature was not printed.** The lead probe drives each phase's high
  side at 50 % (`probeLeads()`), and all three failing means no high side raised its phase. But the harness read probe
  mV only when `start()` returned a cog, so the refused starts printed NA. **BUILT 2026-09-26:** `BM-RPROBE` after every
  refusal (`test_bench_dual` src_rev 49), and `test_bench_t0` src_rev 19 prints `T0-25,rprobe` and then falls back to
  the LEFT wheel, so the next death records its per-phase millivolts and voids nothing.
- **Still open:** the trigger (both deaths followed ordinary driving, one right after an e-stop; the fault tier's harder
  use did not trigger it), and whether the board or our pin handling holds the state.
- **2026-09-26, rig fact from Stephen:** the RIGHT motor had a weak connection, found several runs ago. He re-checks it
  before pass 6.
  - All three phases failing at once fits a shared path better than one phase lead: the board's supply or ground, or
    the high-side gate supply. Recovery with time fits an intermittent contact.
  - **Pass 6 will be confounded.** The reseat and three driver-side changes (PL-138 parts 1-2, PL-141) land together.
    A pass with no death clears neither by itself. The reading that tells them apart is the next death's
    `BM-RPROBE` / `T0-25,rprobe` signature, if one comes. PL-138's all-low-sides window
  touches this path and is the next driver-side candidate.

**2026-09-26 12:33, Visit 10 pass 6 -- RECURRED on the first load after the reseat, WITH its signature**
([evaluation](analyses/bench/2026-09-26/VISIT-10-PASS6-EVALUATION.md) §3).
- **MEASURED:** Stephen remade and checked every right-motor connection before the pass. The first program load
  (`t0-stopreason`, DRIVER_REV 29, so PL-138 parts 1-2 and PL-141 in the image) was refused:
  `T0-25,refused,wheel,RIGHT_P16,chk,$1F,fail,$1C,rec,$0`, after 3 retries.
- **The per-phase signature, first time printed:** `T0-25,rprobe,driven,0,u_mV,20,v_mV,17,w_mV,19`,
  `driven,1,...,20,16,19`, `driven,2,...,20,17,20`. Every phase reads 16-20 mV **with itself driven**: below its own
  56-62 mV coasting floor, where a live lead reads 777-823 mV. No high side raised its own pin.
- **MEASURED, back by 12:35:18** (under 2 minutes): `dual-start` started the right healthy in all 10 lifetimes (probes
  from 789 mV, walks 7/-7, windings 345-431 mΩ), and it stayed healthy for the rest of the pass.
- **DERIVED, the connection reading weakened:** a motor lead cannot lower the voltage on the board's own driven pin, so
  a loose phase connection at the motor does not produce this signature, and the reseat did not prevent it. What fits
  is the board's high-side drive (gate supply or bootstrap) not switching, and recovering within ~2 min. Pass 4's death
  (11:41) was also the day's first load. **Not established:** whether the pack had just been connected in either case,
  since nobody was asked to note the power-on time.
- **Also refuted as the trigger:** PL-138's all-low-sides windows (removed at DRIVER_REV 27/29, in this image).
- **Built for pass 7:** `test_bench_t0` SRC_REV 20 times the recovery. After a refused right and the left's cells,
  it tries the right every 10 s for up to 3 min, with each try's per-phase readings (`T0-25,recover` / `recovered`).
  The pass 7 sheet asks Stephen, in advance, to note when the pack is connected.

### PL-126 -- the P2's output stopped mid-record 2 s into right trial 19, and the wire then carried lone zero bytes

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench watch, one instance)

**Found 2026-09-24** in the first `dual-fault` try of pass 3 (evaluation §3). This ran the pass 2 binary.

**MEASURED:** the last record is `BM-START,seq,4_886,...,RIGHT,life,23` at 13:42:15.410. Then
`usb-traffic_260924-133841.log` shows `$20 $00` at 13:42:17.554 and four lone `$00` bytes over 49 s. No other capture in
the set holds one. The harness watchdog printed nothing. The rerun and pass 2 both passed the same trial.

**Undetermined:** a P2 reset, a supply loss, or a hang with its TX line disturbed. The log cannot separate them.
**Watch:** the next run sheet says in advance what to look at if the log stops scrolling. A second instance, or that
observation, makes it actionable. Owner «#3613».

### PL-132 -- the blocked-wheel protective stop shorts the phases even when the user chose coast

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: the floor run.

**Found 2026-09-23** as fault study F-5, and **filed 2026-09-25** («#3609» phase 3). `frontProtectiveStop()` secures
the motor with `frontEStop(TRUE)`. The PASM e-stop takes `.shortBridge` "whatever the stop mode"
(`isp_bldc_motor.spin2`, the `.eStop` branch). So a blocked wheel under SM_FLOAT is shorted, and the user's
`holdAtStop(FALSE)` is not honoured on this path (P3: behaviour the API lets the user select is theirs). The wheel is
stationary by construction, so the short brakes nothing. The cost is on a slope: a short at rest creeps, and the user
who chose coast gets a state they did not choose. The e-stop itself stays a hard short by Stephen's ruling. Only its
reuse here is the defect.

**Disposition:** ⛔ fix in the driver, «#3609». The protective stop gets its own immediate stop that takes the stop mode's
at-rest state: SM_FLOAT coasts, SM_BRAKE holds, and the hold's own hand-off to the short still applies. It still latches
and refuses drives until `clearProtectiveStop()`. **Unmeasurable wheels-up** (PL-106: a lifted wheel cannot be
blocked), so it is certified by construction and by the floor run («#3576»). Building it gates no load on the current
bench pass.

**FIXED (DRIVER_REV 20, 2026-09-25), not bench-certified:** `e_stop` carries its kind: ES_OFF, ES_HARD (emergency
stop, walk guard, `frontSecure()`) or ES_PROTECT (`frontProtectiveStop()`), written in one store by `frontLatchStop()`.
The PASM latch calls `estopBridge` (LUT), which shorts for ES_HARD and for ES_PROTECT under SM_BRAKE, and coasts for
ES_PROTECT under SM_FLOAT. Every reader tests non-zero, so the refusal semantics are unchanged. DRIVE-OBJECTS.md's
*Protection and limits* says which state the stop takes. ⚠ It is a user-visible behaviour change, so it needs a release
note line («#3516»).

### PL-134 -- HOLD-RISE's rate estimate kept counting after the hold slipped

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench estimator)

**Found 2026-09-24** at `t0-stopmode` 21:29 (`debug_260924-212939.log`, row 1 run 1). `rise_ms,16_539`: he pushed past the
hold, it slipped at 2_328 ms with the duty frozen at 2_684 (ceiling 2_764), and the wheel stayed displaced for seconds.
Pairs with no duty gain piled up time. Up to the slip, the rate reads **251 ms**, the same as runs 2 and 3 (250, 249).
The cell's FAIL for that run was right (the hold gave way before its ceiling). The printed number was not.
**FIXED** (`test_bench_t0` SRC_REV 17): a pair counts only while `getHoldStatus()` reads HS_HOLDING at both ends.

### PL-135 -- a card that asks for a deliberate act does not get it: the interaction's negatives are still unmeasured

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench interaction negatives)

**Found 2026-09-24**, same run. Rows 1, 4 and 6 now asked on their cards for the three acts that make UI-MISS, UI-REDO and
UI-ABORT able to fail (PL-131). None was made: no `hit,MISS` input, row 4 ran once, and row 6 took no ABORT. A line of
card text competes with the row's own instructions and is read past.
**FIX, correct by construction:** the program *requires* each act on the first run of its row, and draws only the
control that performs it.
- Row 1's intro screen shows no START ROW until one click lands on the marked empty area, which reads `hit,MISS`.
- Row 4's first RESULT draws REDO ROW only.
- Row 6's first run draws ABORT as its only control, and its RESULT draws REDO ROW only.
- Each screen says in one line why it asks.
Later runs of those rows are unchanged.

### PL-136 -- PL-120's diagnostics are reachable only from a fault trial, so a wheel dead at PREFLT is never diagnosed

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench diagnostics)

**Found 2026-09-25** at Visit 10 pass 4 ([evaluation](analyses/bench/2026-09-25/VISIT-10-PASS4-EVALUATION.md) §4a).
The right wheel failed PREFLT. `BM-FRRECSUM,...,probed,FALSE`, and no `where,NOMOTION` dump fell on it.
- Both diagnostics are reached only from `frTrial()`: the NOMOTION dump through `frWaitAtSpeed()`, the recovery probe
  through `bTimedOut`.
- `bSegPreflight()` retires a non-moving wheel before FLTRESP, and its trials are then skipped.
- `bPreflightWheel()` also drains the instrument ring to count ticks but never emits it, so the failing drive's
  per-frame phase voltage, current and duty were measured and discarded.
- The run sheet and the runner's precondition text both promised the probe "if a wheel stops driving". The build did
  not keep that promise.

**Disposition:** ⛔ **FIX** in `test_bench_dual`, correct by construction. The diagnostics key on *a commanded wheel that
does not move*, wherever it happens:
- a PREFLT nudge with no hall tick by FR_NOMOTION_MS dumps (`where,NOMOTION`) mid-nudge;
- a PREFLT that fails emits its ring as a trace;
- **first, PREFLT retries the non-moving wheel at once**, in 3 fresh lifetimes about 1 s apart, each dumped and traced
  like the first. Pass 4 started the right exactly once (`BM-START ... motor,RIGHT` occurs once in the log), so one
  failed attempt could not tell a transient first-drive failure from a persistent one. Stephen, 2026-09-25: *"the
  right wheel is turning and providing results in the other two tests.... so maybe didn't retry?"*;
- only if all of those fail, arm the recovery probe on that wheel (20 s gaps), run before FLTRESP.
A wheel either stage recovers is un-retired and runs its trials. Rides on the next `dual-fault-rightfirst`.

**2026-09-25 -- BUILT (not yet certified).** `test_bench_dual` SRC_REV 46, FMT 30; no library object changed.
- **Every part's PREFLT:** the nudge's wait is `waitWatchedNoMo()` (FLTRESP's NOMOTION loop, moved out of
  `frWaitAtSpeed()` unchanged), so a nudge with no hall tick by FR_NOMOTION_MS dumps `BM-ABI* where,NOMOTION` mid-nudge.
  A nudge that does not move emits its ring as a trace (`BM-TRACE seg,PREFLT,cause,START`, `BM-TS`, `BM-TRACE-END`),
  drained before any fault recovery re-arms the ring. In FAULTRESP every nudge is traced, so a moving wheel's nudge is the
  in-run control.
- **The three phases:** the ring always stored u, v and w apart (`instPackSense()`); `BM-TS` printed only their sum.
  `BM-TS` now appends `u`, `v`, `w` (mV, NA when the driver is down), in every trace.
- **FAULTRESP only, the stages:** a wheel whose nudge does not move is retried at once in PF_RETRY_TRIES = 3 fresh
  lifetimes, PF_RETRY_GAP_MS = 1 s apart, each nudged, dumped and traced like the first. New record **`BM-PFRETRY`**
  (motor, try, life, ms from the first failure, moved, ticks, hw, tid of its trace, why). Only if every retry fails,
  and it is the only such wheel, the recovery probe runs on it before FLTRESP (`BM-FRRECOV` gains `seg`, here `PREFLT`).
  A wheel either stage moves is not retired. Its cells read NOMEAS while the stages run and live again when one moves;
  `bSlotRetired` is set only after both fail, since it would refuse the retries' own starts. FLTRESP's own probe keeps
  its one turn.
- **Records:** `BM-FRRECSUM` gains `l_pf`/`r_pf` (NO_FAIL, RETRY, PROBE, DEAD, UNDECIDED), `l_pf_rec`/`r_pf_rec`
  (TRUE, FALSE, NA only when nothing was decided), `l_pf_n`/`r_pf_n` (retries made) and `l_pf_try`/`r_pf_try`. Its
  `recovered` and `tries` now print NA when the FLTRESP probe did not run (they read FALSE and 0: silent zeros).
  `BM-FRDIAG` gains `pf_tries`, `pf_gap_ms`.
- **Why the stages are FAULTRESP's only:** every other part ends its run on a PREFLT failure by contract. A retried wheel
  would be measured there as though it had not failed. The dump and the trace change no outcome, so they run
  everywhere.
- **Compiled** (pnut-ts 1.55.8, scratch copy, first dual config block, the runner's `-D` sets): `dual-fault` and
  `dual-fault-rightfirst` 133_736 plain / 141_175 with `-d`, DEBUG footprint 7_439 (limit 12_404, unchanged from src_rev
  45). Style gate PASS.
- **Worst case, `dual-fault-rightfirst`:** about 6 minutes planned; plus about 2.2 minutes for a wheel dead through
  PREFLT (retries of about 15 s, then the probe's 2 minutes); plus 2.2 more if a wheel then dies mid-run. At most about
  10.5 minutes, under the 15-minute cap.

### PL-139 -- RESTFLAT's 50 mV at-rest band was set on the left board, and the right's coast rest read 51

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench cell band, watch)

**Found 2026-09-26** at Visit 10 pass 5 ([evaluation](analyses/bench/2026-09-25/VISIT-10-PASS5-EVALUATION.md) §2).
- **MEASURED:** `R19-DUAL-RESTFLAT-X` RIGHT FAIL, 1 of 6 windows. It is trial 5 (X-3, coast from −80 × 10⁶), REST
  window: `BM-FRPHASE,...,tid,5,motor,RIGHT,win,REST,n,154,ticks,0,pp_u,35,pp_v,51,pp_w,23,...,flat,FALSE`.
  `FR_FLAT_MV` is 50.
- The right's other X-3 rest windows read 40 and 15 mV peak to peak. The left's read 38, 19 and 38.
- No hall tick moved in the window. The swing is under one hall step of rotor settling after a free coast.
- **The verdict stands (D2):** the criterion was fixed before the run.

**Why it matters:** RESTFLAT is COASTEMF's negative control. A band that the healthy right touches at rest cannot
separate "flat" from "turning" on that board with margin.

**Disposition: Watch.** It bears on the coast measurement's control, not on any fault response. What would make it
actionable is a second right rest window over 50 mV with no tick. The band is then sized from both boards' rest
windows, never from one run's worst. The next `dual-fault-rightfirst` carries it as is.

### PL-143 -- the command timeout watches a drive whose own limit bounds it, so "arm a limit, then drive" is cut short

> **6.0 status (2026-09-26 audit):** RELEASE — Stephen's ruling on the command timeout versus an armed stopAfter* limit.

**Found 2026-09-26** while updating the RC demo («#3624»).
- **DERIVED from the source:** `REQ_DRIVE` marks every non-zero drive as open-ended for the command timeout
  (`isp_steering_2wheel.spin2` ~:2816, `frontWatchCommand()`). That includes a `driveDirection()` or `driveAtPower()`
  after `stopAfterTime()`, `stopAfterRotation()` or `stopAfterDistance()`. Only `driveForDistance()` is exempt, "a
  bounded move" (DRIVE-OBJECTS.md, `setCommandTimeout()`).
- So with `setCommandTimeout()` on, the library's own recommended pattern ("arm the limit BEFORE the drive") stops at
  the timeout unless the program re-sends the drive. Re-sending may itself disturb the armed limit; that is not checked.
- The RC demo's slow one-rotation drive is exactly that pattern. It would be cut after the timeout, so the demo does
  not turn the guard on yet.

**Disposition: question for Stephen** (the API contract is his, D10). Either a drive with an armed platform limit is
bounded and not watched, as `driveForDistance()` is; or it is watched, the doc says so, and a program re-sends it.
Once ruled, the RC demo gains `setCommandTimeout()` as its link-loss guard for wheels-down driving.

### PL-144 -- the path limiter hunts: a wheel that cannot sustain its command cycles the platform between 8 % and 100 %

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: pass 7 dual-d PATH-HUNT = 1.

**Found 2026-09-26** at Visit 10 pass 6 ([evaluation](analyses/bench/2026-09-26/VISIT-10-PASS6-EVALUATION.md) §5).
- **MEASURED** (`dual-d`, BLOCK step at a 1 A limit, the left weaker than the right): five cycles in 4 s.
  - `PATH_LIMIT,wheel,LEFT` engages at 82, 95, 81, 80 and 85 ‰ (ms 64_946, 65_730, 66_450, 67_162, 67_954);
  - each is followed by a full release to 1_000 about 430 ms later;
  - the next engage comes about 300-350 ms after that, a period of 720-790 ms.
- **The design says otherwise:** DRIVE-INTEGRATION-DESIGN.md §3 requires the limiter to release *"without hunting
  between the two"*.
- **Cause, read in `frontLimitPath()`.** A slot counted as clean when no field was held. But the fields ramp toward
  each released scale at their acceleration, so the scale reached full about 0.4 s before the weak wheel's field did.
  At full the wheel fell behind again, and the limiter re-engaged from full.
- On a floor, that is a platform surging between a crawl and full command every ~0.75 s whenever one wheel is
  overloaded.

**Disposition: ⛔ FIX, built** (DRIVER_REV 30, `isp_steering_2wheel.spin2`). A slot counts as clean only when both
fields have reached the present scale, within one release step. So the release never outruns the fields, and a wheel
that cannot sustain its command falls back from near its limit, not from full. No PASM change.
- **Cell:** R20-DUAL-PATH-HUNT (`test_bench_dual` SRC_REV 52): the BLOCK step's most EV_PATH_LIMIT pairs in one log.
  PASS at exactly 1. Its negative is pass 6's log: 5 on the pre-fix driver.
- **Not established:** how the fixed limiter settles on a floor. A wheel behind by less than one release step can still
  drift slowly, deepening without an event; the floor run shows it.
- **By design, stated:** a field that stops short of the scale without being held (its ramp waiting at LAG_SOFT) now
  keeps the scale where it is until the fields catch up or a new command arrives. The path is kept, just slower.

### PL-145 -- R16-DUAL-TIMESTOP's 20 ms slack sits inside the step's own measured spread

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench cell slack, watch)

**Found 2026-09-26** at Visit 10 pass 6 (evaluation §5).
- **MEASURED:** the single-wheel form failed, `BM-DSTEP,...,TIMESTOP,motor,LEFT,seg,LIMIT,measured,329,...,hi,320`,
  which is rest confirmed 29 ms after the deadline.
- Every TIMESTOP on file reads 254-329 ms (7 runs, both forms). That is -46 to +29 ms against the deadline, once the
  300 ms rest-confirmation dwell is taken off. One earlier run also failed, at 321 (STEERSEG).
- **DERIVED:** the stop is timed so the FIELD reaches zero at the deadline (`bFrontLimitsDue()`, `frontStopMs()`). Rest
  is then confirmed by the last hall tick. At the end of a ramp a tick is tens of ms long, so where the last tick falls
  scatters the reading by about that much.
- **The verdict stands (D2).** The 20 ms slack is tighter than the reading's own resolution at the end of a ramp, so
  the cell can fail a correct stop.

**Disposition: Watch.** The fix is a bound derived from the last tick's duration at the ramp's end, stated before a
run. It is never the worst reading seen. What would make it actionable: a TIMESTOP later than about 60 ms past its
deadline, which the tick scatter cannot explain.

### PL-146 -- part D's event drains read a stalled wheel's log before its fold-back released

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: pass 7 EV-FOLDBACK 0 bad.

**Found 2026-09-26** at Visit 10 pass 6 (evaluation §5).
- **MEASURED:** R20-DUAL-EV-FOLDBACK FAIL, 1 bad. The BLOCK drain holds `FOLDBACK,wheel,LEFT,...,value,0` (engage, ms
  64_326) and no left release. The right's pair is complete: engage 64_334, release 69_310 with 4_295 frames.
- **DERIVED:** the drain waited EV_SETTLE_MS (1_032 ms) after the step's rest wait, which confirms rest by *position*.
  The left was stalled at 1 A, so it read at rest while its field was still ramping down under the fold-back. Its
  release, queued after a second of quiet, fell after the drain at about ms 69_790.
- **Not a driver defect:** the driver logged the engage, and would log the release after its quiet second, as
  designed.

**Disposition: ⛔ FIX, built** (`test_bench_dual` SRC_REV 52). Each part D drain first waits, bounded by D_REST_MS,
for both drivers to read DCS_STOPPED; the settle counts from there. Certifies at pass 7 (EV-FOLDBACK 0 bad).

### PL-147 -- the two "following" readings measured against different commands while the path limiter scaled

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: pass 7 NOTFOL-D PASS.

**Found 2026-09-26** at Visit 10 pass 6 (evaluation §5).
- **MEASURED:** R18-DUAL-NOTFOL-D LEFT FAIL: `BM-HOLD,...,LEFT,...,short_permille,84,short_pct,105`.
- The limiter's fraction (`shortfallNow()`) is taken against `userCmdIncr`, the user's command.
- The rpm window's percentage (`updateFollowing()`, `testGetFollowing()`) was taken against `targetIncre`, which a
  path scale rewrites. So a wheel scaled to 8 % "followed" at 105 % of the scaled command, while the other reading
  said 84 ‰ of the user's.
- One value, two meanings (D7).
- The cell was right to fail. A-8 requires the two readings to agree.

**Disposition: ⛔ FIX, built** (DRIVER_REV 30, `isp_bldc_motor.spin2`). The percentage is now of `userCmdIncr`.
`targetIncre` still gates validity, so a stopped or e-stopped wheel (driver command zeroed, user command kept) is not
reported as not following. Test-use observable; no PASM or ABI change. Certifies at pass 7 (NOTFOL-D PASS on a
behind wheel).

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
