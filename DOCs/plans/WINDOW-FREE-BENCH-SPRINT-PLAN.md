# Window-free bench — sprint plan (Plan A)

**Written 2026-09-30.** Task: «#3576» (the floor visit), whose scope this plan replaces.

**Goal.** Get to the bench and capture driver readings with nothing in the way. Record every result, put the
results into every document and record that depends on them, and make the driver ready for release.

**What Plan A is not.** Plan B (not written yet) brings all public documentation up to date with the final driver. The
line between the two plans is Stephen's (2026-09-30): *"this needs to be two plans... This plan only covers those.
When the driver is ready, we go into the next plan to bring all of the documentation up to date and current with the
final state of the driver."*

---

## Sprint start (2026-09-30)

- **Build:** 6.0.0, settled by Stephen on 2026-09-20 (*"The way I think about ship: 6.0.0"*). `VERSION` reads 5.0.2
  until «#3516» bumps it at the tag.
- **Working tree:** clean, apart from Stephen's own `.vscode/settings.json` (not ours; untouched) and this plan,
  committed as the sprint's foundation. `main` is ahead of origin by 11; pushing is his.
- **Tracking readiness: READY.**
  - Archived 41 completed tasks (`tasks/archives/archive_20260930_194528.md`).
  - Context: deleted `sprint_panel_pl92_open` (panels are out of testing; PL-92 is in the punch-list archive) and
    `study_bench_logs_2026_09_21` (its study is `DOCs/analyses/BENCH-LOG-STUDY-2026-09-21.md`). Replaced
    `sprint_resume_2026_09_23_panels_certified` with `sprint_resume_2026_09_30_window_free`.
    `sprint_release_notes_pending` is kept until §1 checks it.
  - Auto-memory: the resume file was replaced (`project_window_free_bench_state_2026-09-30.md`); `MEMORY.md` is 3
    lines.
  - Live tasks:
    - «#3576» in progress (superseded by this plan's tasks);
    - «#3613» and «#3611» paused (§1);
    - «#3516», ship, pending after this plan;
    - five tasks Stephen ruled out of this release («#3506», «#3532», «#3562», «#3592», «#3602»), left as they are.
  - Task shape (backlog observation: all nine predate the creation-time checks): gist ≤ 60 characters 0/9, priority
    unset 0/9, `attention:` in body 5/9.

## Open questions

None. Every question was asked and answered on 2026-09-30 (below).

## Standing rulings this plan rests on

All are Stephen's, from 2026-09-30 unless dated otherwise.

| # | Ruling | His words |
|---|---|---|
| R1 | **No debug PLOT windows in testing.** The tests are plain executables that log. | *"We're going to remove all debug plot windows from the testing... All you do is run the executables and they log. No plot windows."* |
| R2 | **The panel technique itself is sound.** What failed was how we developed and packaged it. TECHNIQUES.md §3.8 stays. | *"that technique should work - the issue is how you were developing them was getting in the way"* |
| R3 | **A 10 s lead-in after load, and nothing more.** | *"let's go ahead and add a 10-second lead-in. Nothing more."* |
| R4 | **Each test does one action once. A repeat is a rerun, never a loop inside the test.** | *"Rather than having any kind of loop within the test so that we do it multiple times, we just run the test sequentially. Again."* |
| R5 | **The grab is timed from the start of motion.** | *"time it"* |
| R6 | **The Rev A test runs on the Rev A platform, with two Rev A boards, wheels up, and includes the hand grip.** Boards are never swapped between platforms. | *"Prepare it to run on the RevA platform that has two RevA boards"*; *"include it"*; *"we would never swap the rev A and B boards"* |
| R7 | **"1 rotation" comes out of the RC demos.** There is no switch E. | *"let's remove it as i can still command that to be done without it"* |
| R8 | **The run sheet is his only set of instructions,** and the FlySky run is guided, not scripted. | *"the FlySky testing is just me determining what to do on the robot, with a little bit of guidance"* |
| R9 | **The pack carries only what the visit runs.** | *"I have no reason why you'd carry anything that's done in the pack."* |
| R10 | **The countdown-board test is abandoned.** c289e1f needs nothing further. | *"we are abandoning that test and moving on the to new..."* |
| R11 | **Pack voltage with no sensor: leave the driver as it is.** Documenting it is Plan B. | *"yes leave as is"* |
| R12 | **Every record and document agrees with the tree and the logs. Any disagreement is fixed on sight, never asked about.** | *"If you see issues with this consistency, they need to be fixed immediately because that inconsistency keeps leading us down bad paths, such as testing three or four times only because we forgot to record the results."* |
| R14 | **Both grips are held until the program stops the motion:** one start cue, and no let-go count. | *"ok A"*, to option (a), "hold until it stops" |
| R13 | **Earlier, still in force:** incline postponed (2026-09-29); every mid-run stop is his own and physical (2026-09-29); floor motion limits of 1 m straight and one turn in place (2026-09-27); the fault return run uses `testForceFault()` (2026-09-28). | quoted in `DOCs/analyses/bench/VISIT-6B-FLOOR-RUNSHEET.md` |

---

## 1. Consistency first: correct every aged record (R12)

**Why.** Records that disagree with what is true are what sent the floor run back to the bench. This section runs
before any build.

**Items, each checked against the tree or the logs, then corrected or closed:**

- «#3613» (Visit 10, paused). Walk each cell its body names against the Visit 10 and release-candidate evaluations.
  Close the task if everything it names is certified or ruled out; otherwise rewrite the body to what remains.
- «#3611» (the pack sensor, paused). The body says the unit is not fitted. The bench config says it is:
  `PACK_SENSOR_FITTED = TRUE`, `PACK_SENSE_PIN = 0`, `PACK_SENSE_CAL_PERMILLE = 1012`
  (`src/isp_bldc_motor_userconfig_bench.spin2:96-98`), calibrated on 2026-09-26 (`PACK-CAL-EVALUATION.md`). Rewrite the
  body to what remains, which is the documentation (Plan B).
- «#3576» (this visit). Rewrite the body to this plan.
- `DOCs/analyses/bench/VISIT-10-RUNSHEET.md:201-204`, the "Board swap" rows: contradicts R6. Mark superseded.
- `tools/bench-run.sh:278-281`, the `t0-reva` PRECONDITION, tells him to swap a board: contradicts R6. Replaced in §3.
- `DOCs/PUNCH-LIST.md` PL-163: its disposition line speaks of a swapped-in board. It now closes on the Rev A platform
  (§3).
- The sprint-resume context key and the auto-memory resume file: repoint both to this plan.
- **`CHANGELOG.md` v6.0.0 lacks two changes recorded as landed** (found at sprint start, 2026-09-30, from the
  retired `sprint_release_notes_pending` key). Verify each against the source, then add each class-1 voiced:
  - the BREAKING renames in the support objects: `isp_flysky_rx` `swIsOn`/`swIsOff`/`swIsMiddle` became
    `isSwitchOn`/`isSwitchOff`/`isSwitchMiddle`, and `isp_queue_serial` `haveCommand`/`haveRxString` became
    `hasCommand`/`hasRxString` (STEPHEN 2026-09-18, "yes A");
  - `driveDirection()`'s positive direction now turns RIGHT, as DRIVE-OBJECTS.md and the serial protocol always
    documented, and the RC demos no longer invert the joystick («#3569», 57e5785). This is a behaviour change: users
    who compensated must remove their compensation.
  - At the same time, check the retired key's other "LANDED" lines against the entry. Each one either appears, or
    is added.

**Verify.** Each item cites the line or log that settled it, and no record touched still names a swap, a
countdown-board visit or an unfitted sensor.

## 2. The floor run as ten single-action commands, with no windows (R1, R3, R4, R5)

**Starting point.** One binary, part SPIN (`src/test_bench_dual.spin2`, tier `dual-spin`), runs four situations,
each with its repeats inside:

| Routine | What loops inside it today |
|---|---|
| `segBlock()` `:18969` | both OBSTACLE trials, `BLK_TRIALS = 2` (`:15681`) |
| `segLoad()` `:19387` | up to `LOAD_DRAG_TRIES = 3` grab tries (`:15777`) |
| `segSpin()` `:16230` | `SPIN_LEGS = 10` legs (`:15350`) |
| `segFaultRun()` `:18364` | runs once |

Every situation opens the operator panel (`panelSetup()` `:9002`) and waits on READY screens (`readyAsk()`). The
first READY waits for a START click that has never arrived on the platform's Pi.

**Target.** Ten tiers. Each builds part SPIN with one action selected by name (P2: no typed data):

| Tier | One run does |
|---|---|
| `floor-obstacle-coast` | OBSTACLE's coast trial: drive into the obstacle, the protective stop (coast), and the API checks after it |
| `floor-obstacle-short` | the brake trial, the control: the same, with the stop shorting |
| `floor-grab` | one grab try: a straight drive, his hold, on to the 1 m stop |
| `floor-faultrun` | the fault return run: 1 m out; back with the LEFT wheel faulted on purpose; the recovery; the drive back to the start. This is one sequence, not a repeat |
| `floor-spin-{slow,med,fast}-{left,right}` | one spin leg at that speed and direction |

**Behaviour of every floor tier:**

- **No PLOT window is opened, and no PC_KEY or PC_MOUSE is reached.** Under the window-free build the panel and board
  routines are compiled out, so the compiler, not a guard, proves that no call remains.
- **The 10 s lead-in** runs after the banner and build records, before anything moves. It beats the watchdog through
  the wait, because the watchdog stalls at 4 s (`wd_stall_ms,4_000` in the banner).
- **The first READY does not wait.** The lead-in replaces it. Countdowns inside a sequence stay: the fault run's
  5 s STAND CLEAR before its drive back and before its redrive.
- **Nothing after the action.** The obstacle's pull-back and the grab's drive back are removed. The run ends, and
  he returns the platform by hand between runs (his steps 2 and 5).
- **The grab's timing is unchanged in code** (R5, R14). The judged window starts `LOAD_PULL_LEAD_MS` (1 s) after the
  wheels pass `LOAD_GRAB_MM` (400 mm, about 2.6 s after rolling), and lasts `LOAD_WIN_MS` (2.5 s)
  (`:15762-15767`). His cue on the sheet: about 3 s after it starts rolling, take hold, and **keep holding until it
  stops by itself at 1 m**. The judged window then lies inside his hold by construction, and any grab from about 2.5 s
  to 3.5 s after rolling covers it.
  - **Build check:** a held drive covers the last 0.6 m at about half speed, roughly 7 s. Read the grab leg's time
    bound in `loadDrive()` (`:19545`); if it would end a held run before the 1 m stop, raise it. The release after a
    hold is no longer seen, and no judged cell reads it (LDPATH, LDHUNT, LDHOLD, HELDATSPD).
- **One plain text result line** prints last, before the session ends. Examples: `RESULT: GRAB -- judged` /
  `-- too light: hold harder next run` / `-- stalled: hold less next run`; `RESULT: OBSTACLE COAST -- latched
  SR_BLOCKED`. He reads it when he walks back to rerun.
- **Safety caps unchanged:** each leg armed at 1 m or less; the harness e-stops 6 ticks (35 mm) past a declared
  travel; the 10 A abort; one turn at most per spin.
- **The banner names the action**, so each log says which command made it.

**Cells.** Every cell keeps its criterion and its negative. Cells that span more than one trial, such as
R21-DUAL-HELDATSPD-P over every OBSTACLE drive and the GRAB window, are judged in the analysis across the logs of those
runs. That is reading, not tooling (overlay P10).

**Verify.**
- Normal: each of the ten tiers compiles. Its build log shows only its one action in `BM-PLAN`, and `BM-BANNER` names
  the action.
- Edge: a grab too light or stalled still prints its BM-LOAD and a result line that says so; a spin leg that does not
  end at its limit prints its END cause.
- Error: a steering start that fails prints `WHY_NO_COG` and the result line says the run did nothing.
- The window-free build contains no `PLOT` window creation and no `pc_key` or `pc_mouse` call. The compiler shows this:
  the routines are not compiled in.
- `tools/build-check.sh` passes, with every tier inside the DEBUG footprint.

## 3. The Rev A test on the Rev A platform, with no windows (R1, R3, R6)

**Starting point.** `src/test_bench_t0.spin2` under `-D T0_REVA` (tier `t0-reva`), T0-27 (`:5496-5565`). It:
- starts the RIGHT group, and stops at the first group that reads REV_A (`:5537-5557`), which assumes one swapped
  board;
- runs two unloaded legs, the negative (`t0vLeg()` `:5597`);
- runs the positive control as a hand hold that waits for a SPACE key in a PLOT window named `t0reva`
  (`t0vHoldLeg()` `:5657`, `bT0vWaitSpace()` `:5770`).

The limit is 2 A (`testSetCurrentLimits(2, 2)`).

**Target.**
- The 10 s lead-in.
- **Both groups** start, and each logs its detected board. A group that does not read REV_A is a finding: this
  platform has two Rev A boards.
- The two unloaded legs run **on each Rev A group**, for R22-T0-REVA-FOLD, the negative.
- The positive control, R22-T0-REVA-FOLDPOS, is **timed with no window**. After the legs, the RIGHT wheel speeds up to
  the hold power (`T0_27_POWER_HOLD` = 20). His sheet cue: when it speeds up, grip its tyre firmly and **hold until the
  program stops the wheel** (R14). The program's hold leg runs its settle and its judged window, then stops the wheel,
  so the window lies inside his grip by construction.
- The PLOT window and `bT0vWaitSpace()` are removed.
- The PL-163 residual is folded in: the cell's record and notes state the effective threshold, `FOLD_MIN_MV`
  (a fold needs 5 mV net), not the old floored-to-0 threshold (`DOCs/PUNCH-LIST.md` PL-163, "the residual").
- The tier's PRECONDITION in `tools/bench-run.sh` is rewritten for the Rev A platform: wheels up, no swap, what he
  sees, and the grip cue.

**Verify.**
- Normal: compiles. The log carries `T0-27,board` for both groups, a leg record per leg per Rev A group, and a hold
  record.
- Negative: an unloaded leg's `fold_win` of 0 is the pass. The pre-DRIVER_REV 38 defect would fold every frame
  (`T0_27_FRAMES_WIN`).
- Positive: with the grip, `fold_win` is above 0 on net readings of 5 mV or more.
- NOMEAS if the grip missed the window or never loaded the link, and the log says which.
- Error: a group that reads REV_B, or does not start, is printed and not driven.

## 4. "1 rotation" removed from the RC demos and the FlySky test (R7)

**Starting point.** Switch E is read as `remoteCtl.isSwitchOn(remoteCtl.CH_11)`. The receiver object decodes only
the switches in `validswitches` (A–D, `src/isp_flysky_rx.spin2:64`), and any other channel reads OFF
(`readSwitch()` `:178-180`). So `bOneRotation` is always FALSE. With the sticks disabled by swA, the loop runs
`doOneRotation()` once, unrequested, and can never re-arm it. The feature shipped in v5.0.2
(`git show v5.0.2:src/demo_dual_motor_rc.spin2`, lines 165, 192, 249).

| File | Lines |
|---|---|
| `src/demo_dual_motor_rc.spin2` | menu line `:166`, the read `:185`, the branch `:254-258`, `nDoingOneRotation` `:663`, `doOneRotation()` `:665-` |
| `src/demo_dual_motor_rc_hdmi.spin2` | `:183`, `:202`, and the same branch, variable and routine |
| `src/test_bench_rc.spin2` | `:299`, `:318`, `:387-391`, and the same variable and routine |

**Target.** The menu line, the read, the branch, the variable and `doOneRotation()` are removed from all three.
Everything else each demo does is unchanged. The README's control table (`README.md:151-166`) already lists no switch
E, so after this change the demos match their documentation.

**Verify.**
- No `CH_11`, `bOneRotation`, `nDoingOneRotation` or `doOneRotation` remains in `src/` (a search).
- The three files compile.
- The FlySky run (§5) exercises the same control loop on the floor, which certifies the loop.
- **Class search:** no other `isSwitch*()` call names a channel outside A–D.

## 5. The pack (R9)

`tools/make-bench-pack.sh:39` defaults to `t0-stopreason t0-reva dual-spin floor-rc`. Change the default to exactly
this visit: the ten floor tiers, `t0-reva` and `floor-rc`. `t0-stopreason` (done 2026-09-28, 19 of 19) and `dual-spin`
(abandoned, R10) are removed. `dist/bench-c289e1f.zip` is deleted.

**Verify.** The pack lists exactly twelve binaries, each with the bitmaps it loads. The window-free builds load none.

## 6. The run sheet: his only instructions (R8)

`DOCs/analyses/bench/VISIT-6B-FLOOR-RUNSHEET.md` is rewritten from the top; git keeps the old one. It holds:

- the seven attributes, and how to get the pack onto the Pi (push, or copy the zip);
- **the order of the day**: Rev A on the bench (wheels up); then the Rev B platform on the floor, in this order:
  obstacle coast, obstacle short, grab (rerun as its result line says), fault run, the six spins, then the FlySky run;
- **for each command**: its line to type; where he stands; the timeline from Enter (terminal start, then the 10 s
  lead-in, then the action); what he should see; the result line to expect; and what he does before the next run;
- **the FlySky run**: a short guidance list, not a script, taken from the `floor-rc` roster (spins left and right;
  forward and back; slow and rapid speed-ups; the stick straight from forward to reverse; centring from full speed;
  swD e-stop at speed, then up to re-arm; turning while moving; crawling). It adds one warning, that switch E does
  nothing, until §4 lands in the pack. It gives a notes table for how each one feels, since this is his first drive of
  the new ramps (PL-160, the feel);
- the banner line each log must carry, and the log files to send back.

**Verify.** A walk of the sheet, in order, against each tier's code: every timing on the sheet matches the constant
it comes from. No step asks for a screen, a click, a key or a swap.

## 7. The visit and its analysis

He runs the sheet. One analysis per set of logs, per `DOCs/procedures/BENCH-RUN-PROCESSING.md`, reading the logs
themselves. The report quotes log lines, states each cell's verdict (or the reason for having none), and judges each
cross-run cell across the logs it spans.

**Verify.** Every cell named in §2 and §3 has a verdict or a stated reason. Each certification it makes is recorded
in the same session (§8).

## 8. Results into every document and record that depends on them (R12)

Before anything else happens after the analysis:

- `DOCs/PUNCH-LIST.md`: the status line of each item the visit closes: PL-93, 95, 106, 111, 117, 132, 144, 150, the
  PL-160 feel, and 163;
- `MOTOR-6.5IN-TECHNICAL-MANUAL.md` §6.5 and §9, with the matching `DOCs/analyses/MOTOR-6.5IN-MANUAL-SOURCES.md`;
- `DRIVER-6.0-REWORK.md`, "How it was checked", item 4;
- `CHANGELOG.md`, the v6.0.0 entry: the RC demos no longer have "1 rotation" (class 1 voicing), and any behaviour the
  results change;
- the task records and the resume key.

**Verify.** A search for each closed PL id across the tree finds no stale status.

## 9. Driver ready

Each finding the analysis makes is root-caused at the desk and designed out (overlay P10). It is then built and gated,
and certified at the next visit only if the fix needs one. Any new driver function goes to Stephen with a measure of
benefit before it is built (overlay P5).

**Verify.** No finding is left without one of: fixed, certified, or ruled on by Stephen.

---

## Documentation blast radius

`tools/doc-audit.sh`, run 2026-09-30 at plan time:

```
-- ORPHAN: documented methods absent from src/ --
    ORPHAN tools/pasm_equiv/README.md: isqrt() exists in no src/*.spin2
    ORPHAN tools/pasm_equiv/README.md: pack_deltas() exists in no src/*.spin2
-- DUPLICATE: (none)
-- COUNT: (none)
```

Both orphans are Python functions of the `tools/pasm_equiv` desk harness, not Spin2 methods. They're a false positive
of the audit's pattern, and don't change with this plan.

| Artifact | Why it changes | Plan |
|---|---|---|
| `VISIT-6B-FLOOR-RUNSHEET.md` | rewritten | A §6 |
| `tools/bench-run.sh` PRECONDITIONs | ten new floor tiers; `t0-reva` rewritten | A §2, §3 |
| the pack's `README.txt` | generated from the PRECONDITIONs | A §5 |
| `test_bench_dual.spin2` / `test_bench_t0.spin2` headers | revision history, debug-record table | A §2, §3 |
| the three RC files' menus and doc comments | "1 rotation" removed | A §4 |
| `CHANGELOG.md` v6.0.0 | the RC demo change; results | A §8 |
| `DOCs/PUNCH-LIST.md` | statuses | A §1, §8 |
| manual, sources, REWORK | results | A §8 |
| `README.md` FlySky table | already lists no switch E: no change | — |
| `VOLTAGE-SENSOR.md` (DRAFT, unlinked), the HDMI demo's stale comment, the README "current state" note, Known Issues | public-doc currency | **Plan B** |

## Exit gate

1. **Standing rulings:** quoted above, R1–R13.
2. **Intent:** capture driver readings with nothing in the way; done means results recorded, documents updated, driver
   ready (Stephen, 2026-09-30).
3. **Decisions and open items:** every answer from 2026-09-30 maps to a section. The punch list's release items are all
   closed by §2 or §3. Everything else is dispositioned to Plan B.
4. **Premises measured:**
   - the driver's executable code is unchanged since the release-candidate pass: the only driver commits since
     (`80303a5`, `e586ae9`) change comments only, from a non-comment diff of each;
   - DRIVER_REV is 46 (`isp_bldc_motor.spin2:6796`);
   - switch E always reads OFF (§4, from source);
   - the grab constants (§2);
   - the Rev A test's current flow (§3).
5. **Research:**
   - the switch E defect class is searched in §4;
   - every file each section touches is cited;
   - the build gate, `tools/build-check.sh`, passed today at c289e1f (50/50, both demos certified, 45 tiers within
     the footprint).
6. **Named unknowns:**
   - **The window-free builds on the Pi:** load and logging are proven on the Pi (09-29, four runs). Motion from these
     builds is not. The first floor run of the day is the test.
   - **The grip's start cue**, the only timed act left (R14). A grab begun later than about 3.5 s after rolling starts
     after the judged window opens; the result line says so, and he reruns.
   - **The shipped `CFG_DUAL_MOTOR` block** puts LEFT on P16 and RIGHT on P32 (`isp_bldc_motor_userconfig.spin2`).
     The rig's bench config has LEFT on P32 and RIGHT on P16 (`BM-BANNER left_base,32,right_base,16`). This doesn't
     affect any bench run. Whether the shipped example is right is a Plan B question for Stephen.

## Revision history

- 2026-09-30: written.
- 2026-09-30: §2 and §3 grips changed from "count four, let go" to "hold until it stops" (R14). Cause: 2, research
  incomplete. The fixed windows' dependence on his count was named as an unknown, when a hold-until-stop design
  removes it.
