# Attended bench steps — UI audit against test intent (2026-09-15)

**Asked for by STEPHEN, 2026-09-15:** *"regarding the use of the UI for the tests... it seems to be out of sync
with some of the test intent (controls offered/enabled) vs. what is needed for the test. please audit the tests
before we run them again."* Task «#3545»; punch list PL-64.

**What was audited:** every screen the four attended tiers draw, read from source at commit `34bd06d`.
- `t0-hand`: `src/test_bench_t0.spin2` `testT0_12()` and `tools/gen_t0hand_assets.py`.
- `dual-brake`, `dual-floor` and `dual-ui`: `src/test_bench_dual.spin2`, parts OUTSIDE, FLOOR and UICHECK, plus
  `tools/gen_dual_assets.py`.
- The run sheet's words for each step: `DOCs/analyses/bench/VISIT-2-RUNSHEET.md`.

**For every screen:** what it shows, which controls are drawn and live, what each input does, what the test
needs at that moment, and each mismatch. Everything here is DERIVED from source unless marked MEASURED.

**How the panel works (common to the three `dual-*` tiers):**
- A control is drawn and accepted only when its bit is in the screen's live mask. `panelRender()` draws it
  (`test_bench_dual.spin2:3123-3129`), and `keyButton()` and `mouseButton()` accept it (`:3218-3220`, `:3237`).
- Every operator wait goes through `operWait()`. It draws the whole seconds left in *that wait's timeout* on
  the countdown, whatever the wait is for (`:2972-2976`).

---

## 1 · `dual-brake` (part OUTSIDE)

**What the test needs:** both wheels at half power. The operator brakes the LEFT wheel until the driver faults,
then releases. The harness then watches the wheels untouched, and drives them again twice (Z steps).

| # | Screen (prompt / state) | Drawn and live | Countdown | What the test needs here | Source |
|---|---|---|---|---|---|
| B1 | "HANDS CLEAR. CLICK START: BOTH WHEELS RUN…" / WAITING FOR START | START | 120, the START timeout | START to begin; nothing moves yet | `:1599`, `:2927-2929` |
| B2 | same prompt / STARTING | none (START highlighted) | blank | the wheels spin up (≤ 6 s) and settle 1 s | `:2931`, `:2567-2573` |
| B3 | "BRAKE THE LEFT WHEEL (P32 BOARD) NOW…" / BRAKE THE LEFT WHEEL NOW | SKIP | 30, the brake wait | the operator brakes; the fault ends the wait | `:2618-2620` |
| B4 | "RELEASE THE WHEEL AND STEP BACK…" / RELEASE THE WHEEL | none | 5, the untouched window | hands off; the wheels are watched | `:2628`, `:2662` |
| B5 | "HANDS CLEAR -- THE HARNESS IS DRIVING BOTH WHEELS AGAIN…" / HANDS CLEAR - WHEELS RUN | none | blank | Z step 1 (2 s), stop (≤ 3 s), Z step 2 (2 s) | `:2664-2678` |
| B6 | the last prompt shown / DONE, SKIPPED or TIMED OUT | none | blank | the result; then the session ends | `:2590`, `:3049-3055` |

**Mismatches:**
- **B-1. No STOP while the wheels are driven.**
  - B2, B4 and B5 drive or watch driven wheels with no control live.
  - B3's only control is SKIP (`:2618`), which ends the brake step and stops the wheels (`:2632-2636`, then
    `:2582-2583`).
  - So the step with a person's hand on a driven wheel offers "SKIP" as its only way to stop, and B2 and B5
    offer nothing.
  - FLOOR, by contrast, keeps STOP live while it drives (`:2792`).
- **B-2. A stale instruction during motion.** B2 still shows "CLICK START" while both wheels spin up, because
  `panelShow()` keeps the start prompt (`:2931`).
- **B-3. The end screen contradicts itself, and nothing lets the operator read it.**
  - `panelEnd()` redraws whatever prompt was last shown (`:3055`), so it can read "BRAKE THE LEFT WHEEL NOW"
    with the state DONE or TIMED OUT.
  - No control is live, and the session ends at once.
- **B-4. The countdown means something different on every screen, with one label.** On B1 it is the time left
  to press START before the step gives up. On B3 it is the time left for a fault to arrive. On B4 it is the
  time until the harness drives the wheels again, which is a safety warning. The panel labels all three
  "SECONDS" (`gen_dual_assets.py:134`).
- **B-5. A silent P2 is invisible.**
  - When the P2 stops, the panel freezes as it was, countdown included.
  - MEASURED at Visit 2: frames 30, 29, 28, then nothing (`analyses/bench/2026-09-15/debug_260915-142454.log:122`;
    PL-43).
  - Nothing on screen or in the run sheet tells the operator that a frozen countdown means the harness has
    stopped.
- **B-6. The run sheet does not match the screens.** Step 12 says *"brake the LEFT wheel… and hold it until
  it says RELEASE"* (`VISIT-2-RUNSHEET.md:44-45`). It does not say that SKIP is the only way to stop the wheels,
  or that nothing on the panel stops them during spin-up or the Z steps.

## 2 · `dual-floor` (part FLOOR)

**What the test needs:** the platform on the floor. It drives about 2 s at power 50, direction +50, with STOP
available throughout. The operator then says which way it turned.

| # | Screen (prompt / state) | Drawn and live | Countdown | What the test needs here | Source |
|---|---|---|---|---|---|
| F1 | "PLATFORM ON THE FLOOR… CLICK START… CLICK STOP OR PRESS SPACE ANY TIME." / WAITING FOR START | START | 120, the START timeout | START to begin | `:1656`, `:2927-2929` |
| F2 | same prompt / STARTING | none | blank | steering start, arm, precondition | `:2931`, `:2770-2786` |
| F3 | same prompt / OBSERVING | STOP | 2, the drive | the drive; STOP must work | `:2792-2793` |
| F4 | same prompt / OBSERVING (unchanged) | none | frozen at its last value | the stop (≤ 3 s) | `:2797`, `:2809` |
| F5 | "WHICH WAY DID IT TURN?" / WHICH WAY DID IT TURN? | LEFT, RIGHT, STRAIGHT, DID NOT MOVE | 120, the answer timeout | one answer | `:2840-2842` |
| F6 | "WHICH WAY DID IT TURN?" / DONE or TIMED OUT | none (the answer highlighted) | blank | the result; then the session ends | `:2821`, `:3055` |

**Mismatches:**
- **F-1. The first screen promises a control it does not offer.** F1's prompt says *"CLICK STOP OR PRESS SPACE ANY
  TIME"*, but only START is live (`:2927`). STOP first becomes live after the drive has been commanded (`:2786`
  before `:2792`).
- **F-2. STOP is dead between the drive call and the panel update, and again during the stop wait.**
  - The drive is commanded at `:2786`. `getPower()` runs, and only then does STOP go live at `:2792`.
  - Once the 2 s run ends (`:2797-2809`), the wheels are still decelerating with no control live.
- **F-3. An answer is final on the first input.**
  - `floorAsk()` accepts the first live key or click (`:2842-2849`), with no confirmation and no chance to
    change it.
  - All four answers answer to single letters (`L` `R` `T` `N`, `:3208-3215`).
  - MEASURED at Visit 2: run 1 recorded STRAIGHT by key (`debug_260915-142650.log:303`), where STEPHEN's video
    shows a left turn. The slip became the record.
- **F-4. The end screen has the same defect as B-3, and the countdown the same defect as B-4.**

## 3 · `dual-ui` (part UICHECK)

**What the test needs (STEPHEN 2026-09-15):** *"a no-motor-control test form of run that takes me thru the series of
UI controls to make sure they work. If they do work then i run the attended test."* The run is a gate for
`dual-brake` and `dual-floor` (`VISIT-2-RUNSHEET.md:40`).

| # | Screen | Drawn and live | What each input does | Source |
|---|---|---|---|---|
| U1 | UI CHECK prompt / UI CHECK; one step per button | that one button | its key and its click must both arrive | `:1676-1677`, `:1705-1721` |
| U2 | "EACH ATTENDED SCREEN COMES NEXT: CLICK START IF IT READS RIGHT, SKIP IF ANYTHING IS WRONG" | START | START begins the previews | `:1678-1679` |
| U3 | seven previews: the real prompt and state | START and SKIP on every preview | START scores OK; SKIP scores WRONG and fails the gate | `:1749-1762` |
| U4 | "UI CHECK FINISHED…" / PASSED or FAILED | START | START closes | `:1682-1683` |

**Mismatches:**
- **U-1. The verdict uses the same controls as the screens it judges. This is the Visit 2 failure.**
  - Every preview draws START and SKIP in the two slots the real screens use for their own controls
    (`:1752`).
  - The previewed prompts themselves say "CLICK START". B3's real control is SKIP.
  - Once a preview is on screen, the instruction to *judge* it (U2) is gone, replaced by the previewed
    prompt.
  - So an operator following the screen in front of him operates it, and the walkthrough scores that input
    as a verdict.
  - MEASURED: four SKIPs scored WRONG (`debug_260915-142103.log:597`, `:626`, `:690`, `:748`).
  - STEPHEN: *"nothing was wrong that i could see. the test itself ruled it a fail."*
- **U-2. A preview is not the real screen.**
  - It never shows the real screen's controls: SKIP only on B3, nothing on B4 and B5, STOP on F3, and the four
    answers on F5.
  - Its countdown is the walkthrough's own 30 s step timeout (`:1754`), not the real screen's.
  - So what the operator is asked to confirm is not what the attended run will show.
- **U-3. Some real screens are never previewed.** B2 and F2 (STARTING), F4, and the end screens B6 and F6 (DONE,
  SKIPPED, TIMED OUT) are not in the preview list (`:1749-1750`).
- **U-4. The gate does not exercise the code the attended runs use.**
  - The previews go through `uiCheckScreen()`, which builds its own live mask (`:1752`).
  - The attended parts build theirs inside `outsideBrake()`, `floorRun()` and `floorAsk()`.
  - A wrong live mask in those three would pass `dual-ui`.

## 4 · `t0-hand` (T0-12)

**What the test needs:** the RIGHT wheel turned by hand 3 turns, clockwise seen from the hub, between a start and a
stop, counting hall transitions. No driver cog runs.

| # | Screen | Input | What it does | Source |
|---|---|---|---|---|
| T1 | static instructions ("PRESS S, TURN THE WHEEL, THEN PRESS SPACE") / WAITING TO START; no buttons | key S (after the window is clicked) | starts the count | `test_bench_t0.spin2:1251-1264`; `gen_t0hand_assets.py:128-147` |
| T2 | COUNTING, transitions "OF 270", illegal "EXPECT 0" | SPACE | stops the count | `:1271-1293` |
| T3 | DONE | none | the run ends | `:1295-1296` |

**Mismatches:**
- **T-1. None against the test's intent.** The screen names the wheel, the direction, the number of turns and
  both keys. It offers exactly S and then SPACE, and nothing else is accepted. MEASURED at Visit 2: it drew,
  took S and SPACE, and counted 270 (`debug_260915-142347.log:394`, `:531`).
- **T-2. Minor: the direction cannot be checked while counting.** The panel shows transitions but not the signed
  position, so a turn the wrong way also reads 270. The log records the sign (`:1296`), and the analysis reads
  it there. No change is needed for the test's purpose.
- **T-3. Not a mismatch: the wait for S has no timeout** (`:1258-1264`). The task specified that it waits rather
  than times out («#3504» verify line), and an abandoned run is ended from the terminal.

## 5 · Mismatches that cut across the three `dual-*` tiers

- **X-1. One countdown, many meanings (B-4, F-4, U-2).**
  - One unlabelled number variously means: time left to act, time before the step gives up, time until the
    harness moves the wheels, and how long a drive lasts.
  - That is one value carrying several meanings, and one of them is safety-relevant.
- **X-2. There is no stop control while wheels are driven (B-1, F-2).**
- **X-3. End screens keep a stale instruction and close unread (B-3, F-4).**
- **X-4. A stopped harness looks exactly like a waiting one (B-5).**
- **X-5. The run-sheet text and the panel text disagree** (B-6, F-1).
- **X-6. `BM-PLAN` names the wrong findings for UICHECK and FLOOR** (PL-65).

---

## 6 · Fix, correct by construction

Each item names the invariant the rebuild guarantees. The rebuild follows Stephen's panel technique, as the
panels that drew at Visit 2 did (doctrine overlay P7).

1. **The screen's controls are a table, not code at each call site** (U-2, U-3, U-4). One DAT table lists every
   attended screen: its prompt, state, live mask and countdown meaning. `outsideBrake()`, `floorRun()`,
   `floorAsk()`, `operStartPrompt()` and `panelEnd()` draw their screens by row id. `dual-ui` walks the same
   rows. *Invariant: what the walkthrough previews is, by construction, what the attended run draws.*
2. **The verdict controls live apart from the screen's controls** (U-1). The preview draws the real row
   unchanged, controls included, but those controls are drawn and never live. The verdict is two dedicated
   controls in a separate verdict strip: *LOOKS RIGHT* / *SOMETHING IS WRONG*, with keys that no attended screen
   uses. The judge instruction stays on screen in the strip. *Invariant: no input can both operate a screen and
   judge it.*
3. **STOP is live whenever a wheel is commanded or decelerating** (B-1, F-2), on every row whose phase drives
   motion, with the same stop path as FLOOR. In the brake step STOP and SKIP are separate controls: STOP stops
   the wheels, SKIP skips the step. It is live before the drive call is made, not after it. *Invariant: a
   person at the rig can always stop the wheels from the panel* (the battery disconnect stays the panic
   procedure).
4. **The countdown carries its meaning** (X-1). Each row names its countdown kind (`GIVES UP IN`, `WHEELS DRIVE
   AGAIN IN`, `DRIVING FOR`), drawn as its own label cell, or no countdown at all. *Invariant: a number on the
   panel has one meaning, shown beside it.*
5. **No stale prompt** (B-2, B-3, F-1). Motion phases and end states have their own prompt rows ("STARTING —
   STOP ANY TIME", "DONE — CLICK START TO CLOSE"). The end screen waits for START (bounded), as U4 already does.
6. **A stopped harness is visible** (B-5, X-4). A heartbeat cell alternates on every redraw, and every operator
   wait redraws at least once a second. The run sheet says that a heartbeat that stops moving means the harness
   has stopped: note the time and use the battery disconnect if the wheels are driven. *Invariant: a silence
   is something the operator was told to watch for* (doctrine overlay P1).
7. **An answer is confirmed** (F-3). Choosing an answer highlights it and makes *CONFIRM* live, and a different
   answer replaces it before confirming. The log records every choice and the confirmation.
8. **The run sheet quotes the panel** (B-6, X-5). Each attended step lists the panel's own controls, generated
   from the same table, so the two cannot drift.
9. **PL-65:** correct the two `BM-PLAN` labels in the same change.

**Verification of the rebuild:**
- `tools/build-check.sh` green with both release demos certified; `tools/check_style.sh` exit 0.
- The four attended builds compile under `-D BENCH_CFG`.
- The assets are regenerated from their generators.
- This audit is re-walked against the rebuilt source, leaving no open mismatch.
- **Run-time proof at Visit 3:** `dual-ui`, then `dual-brake` and `dual-floor`.

---

## 7 · Re-walk against the rebuilt source (`SRC_REV 12`, 2026-09-16)

Rebuilt in «#3553», STEPHEN 2026-09-16: *"fix the code now for the attended side"*. Scope: what `dual-ui` and
`dual-brake` need. `dual-floor` is no longer run, because AC was confirmed at Visit 2 and every run is
wheels-lifted. Its screens share every mechanism below, but it is not previewed and F-3 is not built.

| Mismatch | Now | Where |
|---|---|---|
| B-1 no STOP while driven | **Fixed.** STOP is live on the spin-up, brake, release, Z-step and stopping screens. The spin-up and settle waits (`waitWatched()`) and the Z steps (`steerPollPhase()`) end on it; the brake wait takes it as its own button. SKIP and STOP are separate controls. | `bmScreens` rows 1–5; `panelStopPressed()` |
| B-2 stale "CLICK START" during spin-up | **Fixed.** START moves at once to the spin-up screen. | `operStartPrompt()` |
| B-3 end screen stale and unread | **Fixed.** A LOGGING screen while records are written, then an END screen with the outcome that waits for START. | `panelEnd()`, `panelFinish()`, `outcomeState()` |
| B-4 one countdown, many meanings | **Fixed.** Each row names its countdown kind, drawn as a label beside the digits, or no countdown at all. | `bmScreens` column 3; layer 6 |
| B-5 a silent P2 looks like a waiting one | **Fixed.** A heartbeat dot changes every 500 ms in every panel wait. The screen list and run sheet say a stopped dot means the harness stopped. | `panelTick()`; layer 8 |
| B-6 run sheet differs from the screens | **Fixed.** The screen list is generated from the same table. | `DOCs/analyses/bench/ATTENDED-PANEL-SCREENS.md` |
| F-1 prompt promises STOP before it is live | **Fixed.** The start prompt no longer mentions STOP; the next screen offers it. | row 8 |
| F-2 STOP dead between drive and panel, and while stopping | **Fixed** for the stop wait (STOPPING screen). Between START and the drive call the STARTING screen has STOP live; it is first polled in the drive wait, milliseconds later. | rows 9, 10, 5 |
| F-3 answer final on first input | **Open.** Not built: `dual-floor` is not owed. | — |
| F-4 | **Fixed** with B-3 and B-4. | — |
| U-1 verdict shares the screen's controls | **Fixed.** The verdict is LOOKS RIGHT (key Y) / SOMETHING WRONG (key W) in a strip no attended screen draws; the generator refuses a screen that lists either. The judge instruction stays in the strip. | `uiCheckScreen()`; `check_layout()` |
| U-2 a preview is not the real screen | **Fixed.** A preview draws the row's own prompt, state, countdown label and start, and its own buttons, drawn but not live. | `panelCompose(..., bPreview TRUE)` |
| U-3 some screens never previewed | **Fixed for `dual-brake`:** rows 0–7, including STOPPING, LOGGING and END. Outcome variants of END are not previewed. | `BM_SCR_PREVIEW_FIRST..LAST` |
| U-4 the gate does not exercise the run's masks | **Fixed.** The run and the preview read the same `bmScreens` row, and `operWait()` accepts only what the screen on display has live. One exception, by design: the UI control step's single live button is set at run time. | `panelShow()`, `operWait()` |
| X-6 / PL-65 `BM-PLAN` finds | **Fixed.** `tokFinds` carried one extra `S-9a`, which shifted FLOOR and UICHECK by one. | `tokFinds` |
