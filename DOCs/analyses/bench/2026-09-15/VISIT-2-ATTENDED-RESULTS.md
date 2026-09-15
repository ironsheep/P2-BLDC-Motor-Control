# Bench Visit 2, attended steps — what we learned (2026-09-15)

This covers run-sheet steps 10–14, run after the unattended suite. The unattended suite is in
[`VISIT-2-RESULTS.md`](VISIT-2-RESULTS.md).

**Rig:** Rev B dual 6.5″ platform for steps 10–13, and the Rev A platform for step 14.

**Binaries:**
- **Motion harness:** `src_rev 7`, which includes the panel input fix `6aed714`.
- **Tier 0 and the detection binary:** as built at the bench.

**Provenance tags:**
- **MEASURED** — a log line in this folder, cited `file:line`. Files are named by their time: `142347` =
  `debug_260915-142347.log`. Several records sit inside long panel-poll lines; for those the line
  number is the log line that carries them.
- **DERIVED** — a calculation, or a reading of source.
- **STEPHEN** — his words.

**STEPHEN, 2026-09-15:**
- *"some of the manual bench worked some did not"*
- *"i have video of the two dual-floor runs... i ran them elevated with me watching the wheels. no room
  to run on the ground. both runs were likely left turns"*

---

## 0 · The verdict

- **T0-12 ran: 270 hall transitions for 3 hand turns, 0 illegal.** That is 90 per revolution, the value
  the library assumes (§2). It confirms PL-42's panel fix.
- **The panel now takes input.**
  - All seven control buttons registered both the click and the key (§3).
  - The Visit 2 input fault (`6aed714`) is fixed.
  - **`R14-DUAL-UICHECK-U` FAILs, and the fail is the walkthrough's own.** It scored a SKIP input on 4 of
    the 7 attended-screen previews as "something is wrong". STEPHEN: *"on the UI test nothing was wrong that
    i could see. the test itself ruled it a fail."*
- **`dual-brake`: the P2 went silent about 3 s after the "BRAKE THE LEFT WHEEL NOW" prompt** (§4).
  - There was no abort record, no watchdog record and no end record.
  - That is PL-43's signature: silent under a load step, watchdog silent too.
  - M, Z, S-5, AF context and `BRAKEFLT` are NOMEAS.
- **`dual-floor`, run twice, both COMPLETE.** AC is **CONFIRMED for wheel direction**: the code, the
  telemetry and your video all say left (§5). The platform was elevated, so this is not a turn on the
  floor.
- **Rev A detection re-run (step 14) COMPLETE** (§6).
  - Both Rev A boards read Rev A in every sweep, before and after a driver cog runs.
  - The empty groups read "not detected", and the library agreed in every non-running cell.
  - The guard skipped both overlap groups in every sweep.
  - «#3505» step 4 is done. The detection binary still logs `start_ret 0` for a start that succeeded
    (PL-44 class).

---

## 1 · The runs

| Log | Step | Started | Result |
|---|---|---|---|
| `142103` | 11 `dual-ui` | 14:21:03 | COMPLETE (`142103:890`); `UICHECK-U` FAIL (`:888`) |
| `142347` | 10 `t0-hand` | 14:23:47 | COMPLETE; `T0-12,end` (`142347:531`), `T0-TRAP` 0 (`:532`) |
| `142454` | 12 `dual-brake` | 14:24:54 | **TRUNCATED.** No record after `BM-SSTART` (`142454:121`); session closed 14:26:02 (`:124`) |
| `142650` | 13 `dual-floor`, run 1 | 14:26:50 | COMPLETE (`142650:454`) |
| `142744` | 13 `dual-floor`, run 2 | 14:27:44 | COMPLETE (`142744:295`) |
| `143237` | 14 `detect-phase2`, Rev A | 14:32:37 | COMPLETE; `BD-DONE recs 784, phase2 RAN` (`143237:1270`) |

The sequence ran in the sheet's intent: `dual-ui` failed on screens, not controls, and brake and
floor were then run anyway.

---

## 2 · T0-12 — hand rotation, 90 ticks per revolution

MEASURED:
- The panel drew and took the S key.
- `T0-12,started,hall_pin,21,hall_code,6,told_direction,CW_FROM_HUB` (`142347:394`).
- The count climbed from 0 to −270 between 14:24:17 and 14:24:23, then held at −270 for 2 s
  (`:447-525`).
- `T0-12,end,transitions,270,illegal,0,pos,-270,final_hall_code,6` (`:531`).

DERIVED:
- **270 / 3 = 90 transitions per revolution.** The end hall code equals the start code, as it must
  after a whole number of electrical cycles.
- This rests on STEPHEN's 3 turns: 270 is exactly 3 × 90, and a turn short or over would land on
  another multiple of 6. **R4 90 ticks per revolution: MEASURED.** PL-39's owed anchor is met.
- **Direction:** the RIGHT motor (P16), turned clockwise seen from the hub, counts **negative** in the
  motor frame (T0 does not call `forwardIsReverse()`).
  - `deltas65` counts −1 along 1-3-2-6-4-5 (PL-39), so clockwise from the hub is that sequence.
  - `MOTOR_CHOICE.md:18` labels 1-3-2-6-4-5 "FWD (CW)". Its **CW** matches this observation from the
    hub side, but its **FWD** is the library's negative direction.
  - That settles PL-39 for the 6.5″ motor: keep "CW (from the hub)" on 1-3-2-6-4-5, and replace FWD/REV
    with the library's sign.

---

## 3 · `dual-ui` — controls pass, four screens rejected

**Controls, steps 1–7:** START, SKIP, STOP, LEFT, RIGHT, STRAIGHT and DID NOT MOVE all `result OK`, each
with both `key TRUE` and `click TRUE` (`142103:141-455`).

**Screens, steps 8–14.** Prompt and state rows are decoded from each screen's `crop 2` / `crop 3`
commands in the log (a 76-pixel prompt row and a 32-pixel state row) and named from
`tools/gen_dual_assets.py:82-119`:

| Step | Prompt shown | State shown | Verdict | Line |
|---|---|---|---|---|
| 8 | 0 — "HANDS CLEAR. CLICK START: BOTH WHEELS RUN AT HALF POWER, THEN THE PANEL TELLS YOU TO BRAKE THE LEFT WHEEL (P32 BOARD)." | WAITING FOR START | **SKIP** | `:597` |
| 9 | 1 — "BRAKE THE LEFT WHEEL (P32 BOARD) NOW -- HOLD IT UNTIL THE PANEL SAYS RELEASE." | BRAKE THE LEFT WHEEL NOW | **SKIP** | `:626` |
| 10 | 2 — "RELEASE THE WHEEL AND STEP BACK. KEEP HANDS CLEAR: THE HARNESS DRIVES BOTH WHEELS AGAIN WHEN THE COUNTDOWN ENDS." | RELEASE THE WHEEL | **SKIP** | `:690` |
| 11 | 5 — "HANDS CLEAR -- THE HARNESS IS DRIVING BOTH WHEELS AGAIN BY ITSELF. WAIT FOR DONE." | HANDS CLEAR - WHEELS RUN | START | `:724` |
| 12 | 3 — "PLATFORM ON THE FLOOR, SPACE CLEAR. CLICK START: IT DRIVES ABOUT 2 SECONDS, POWER 50, DIRECTION +50. …" | WAITING FOR START | **SKIP** | `:748` |
| 13 | 3 — same prompt | OBSERVING | START | `:798` |
| 14 | 4 — "WHICH WAY DID IT TURN?" | WHICH WAY DID IT TURN? | START | `:836` |

Final state: UI CHECK FAILED (`:837`); SIGNOFF `UI_CONTROLS_OK measured FALSE, n 14, FAIL` (`:888`).

**STEPHEN, 2026-09-15:** *"on the UI test nothing was wrong that i could see. the test itself ruled it a
fail."* So the SKIP rows above are inputs the walkthrough scored as rejections, not judgements that a
screen was wrong.

**DERIVED, from the crop commands in the log:**
- Every preview, whether it scored START or SKIP, drew the same live 30 s countdown and the same START/SKIP
  pair in the first two button slots.
- Those two slots are also where the real attended screens put their own controls. So a preview cannot
  show the real screen's controls, and an input meant to operate the previewed screen is indistinguishable
  from a verdict. The walkthrough cannot tell the two apart, and it failed itself.
- Text recognition could not read the BMP assets here, so the rendering was not checked from this side.

STEPHEN also: *"regarding the use of the UI for the tests... it seems to be out of sync with some of the test
intent (controls offered/enabled) vs. what is needed for the test. please audit the tests before we run them
again."* Filed as PL-64.

**Also:** the `BM-PLAN` records name the wrong findings for two parts. UICHECK says `finds AC`
(`142103:26`), and FLOOR says `finds S-9a` (`142650:26`). FLOOR finds AC, and UICHECK finds none.

---

## 4 · `dual-brake` — the P2 went silent during the brake window

MEASURED (`142454`):

| Time | Event |
|---|---|
| 14:25:03.256 | START key (`:117`) |
| 14:25:03.375 | Steering started, both boards Rev B, ret 5 (`:121`) |
| 14:25:08.612 | Panel changes to prompt 1, "BRAKE THE LEFT WHEEL (P32 BOARD) NOW", state BRAKE THE LEFT WHEEL NOW, SKIP button, a 30 s countdown (`:122`) |
| ~14:25:12 | Log line `:122` carries countdown frames 30, 29 and 28 and 55 key polls (about 4.4 s at 80 ms), then **stops mid-poll**. Nothing more ever arrives. |
| 14:26:02.590 | Session closed from the host (`:124`) |

**What is absent:** `BM-ABORT` (the 10 A trip), `BM-WATCHDOG` (a 4 s cog-0 stall), `BM-OPER TIMEOUT` (due
at 0 s), `BM-STRACE`, `BM-OUT` and `BM-END`.

**DERIVED:**
- **This is PL-43's signature**: silent under a load step, with the watchdog silent too, so it was not
  a cog-0-only stall. A hand-braked wheel at half power is the heaviest load step any harness segment
  makes.
- The 10 A abort did not print either. Either the current never reached it, or the P2 stopped first.
- PL-43's explanations still apply: a P2 brown-out or reset from supply sag, or a host/link loss. The
  log cannot separate them.
- **Nothing asked the operator to watch for this, so there is no observation to draw on.** STEPHEN: *"i
  don't know that dual-brake went silent"*.
- **That is a design item for the next run.** The harness and the run sheet must make a silence
  visible when it happens and record what separates the explanations. The log alone cannot.
- **NOMEAS:** M, Z, S-5, `R14-DUAL-BRAKEFLT-H`, and the NOSTALL/DBGMASK cells for part H.
- **Safety:** the step makes a person hold a driven wheel. If a brake load can drop the P2, the
  protective code cannot act while it is down. The run sheet's physical battery disconnect remains the
  only panic procedure.

---

## 5 · `dual-floor` — AC confirmed, elevated

MEASURED, both runs identical in everything that matters:
- **Commanded:** `driveDirection(50, 50)` gave `l_pwr 25, r_pwr 50` (`142650:305`, `142744:146`).
- **Rates:** `l_rate_x10 671`, `r_rate_x10 -1_106`, `slower LEFT`, `stop_by TIMER`, `run_ms` 2,006 and
  2,010 (`142650:447`, `142744:288`).
- **Currents:** left about 80–100 mV, right up to about 1,140 mV (NEG motor frame at half power). These
  match unloaded wheels, as STEPHEN says: elevated.
- **Recorded answers:** run 1 STRAIGHT by key (`142650:303`); run 2 LEFT by mouse (`142744:144`).
- **Cells:** `R14-DUAL-FLOORANS-F` PASS in both, with NOSTALL and DBGMASK PASS.

**AC (DERIVED):** the rule compares three sources.

| Source | Says |
|---|---|
| The code: `direction > 0` reduces the LEFT motor (`isp_steering_2wheel.spin2:848-849`) | left |
| The telemetry: the slower wheel is the side it turns to | left |
| STEPHEN's video: both runs "likely left turns" | left |

- **CONFIRMED** for the sign of the turn.
- Run 1's recorded STRAIGHT is an input slip, not an observation.
- It was measured on an elevated platform, so it is wheel direction, not a turn on the floor. A floor
  run, when there is room, adds no new direction evidence.
- **Owed from the AC rule:** checking which of the code comment, `DRIVE-OBJECTS.md` and `README.md` says
  otherwise. It was not done in this report.

---

## 6 · Rev A detection re-run (`detect-phase2`)

**Rig checks, MEASURED (`143237`):**
- `BD-CLK match 1` (`:21`), and every `BD-ENUM match 1` (`:24-29`).
- `BD-CAL tix_per_iter` is 408 at all three checks (`:78`, `:449`, `:1269`), so timing is valid.

**Phase 1** (no driver code running, sweeps 1–2, 32 reps per cell):
- P16_P31 and P32_P47 read **REVA**: sum 0, `fltix 472`, 32 of 32.
- P0_P15 and P8_P23 read **NODET**: sum 500, MAXED.
- Library verdict agrees in every cell.
- NO_USE_P24_P39 and P40_P55 were **skipped, `GATE_OVERLAP`**, in every sweep: 2 skipped, 4 cells, 128
  reps (`:263`, `:448`).

**Phase 2** (a driver cog started at commanded zero, forced `BRD_REV_B`, first on P0_P15, then on P16_P31):
- **While a driver runs on a group,** that group's pin reads sum 1–3 instead of 500 or 0, and the
  library returns the revision recorded at start (22). The cell reads `agree 0` (`:488`, `:896`). That
  is the documented "driver running, not measured" behaviour, not a detection error.
- **After each stop,** sweeps 4, 5, 7 and 8 read exactly as phase 1 did — REVA on both boards, NODET on
  both empty groups — and the library agrees (e.g. `:1219`, `:1265`).
- **Detection after a stop and restart is correct on Rev A**, as it was on Rev B.

**`start_ret` capture (MEASURED, DERIVED):** `BD-PH2 ... step,started,start_ret,0,motorcog,2` (`:465`,
`:873`). The library printed `* Motor COG #1`, so the return was 1. The detection binary still captures
its start return through the pattern PL-44 removed from the Tier 0 and char binaries. That was known
(PL-44 names it) and does not affect detection.

**Hall inputs (MEASURED):**
- The pre-fields read `$00A0` on P16 and `$0060` on P32 (`:596`, `:641`): valid hall codes 5 and 3.
- The binary's own note says a valid code means a motor's halls are connected and powered.
- The run sheet said to unplug the A motors. That makes no difference to detection here, but the
  record suggests they were still plugged in.

**Not done here:** `R2-HOST-DETDIFF`, the diff against the 2026-09-11 baseline, which needs a
same-variant log. `R2-DETECT-OVERLAP` needs a motors-unplugged session.

---

## 7 · Findings filed

Filed in `DOCs/PUNCH-LIST.md` on 2026-09-15:
1. **`dual-brake` went silent about 3 s into the brake window**, with no abort and no watchdog (§4): added to
   **PL-43** as a second occurrence after the repair, and the entry is open again.
2. **The walkthrough failed itself** (§3): nothing was wrong on any screen (STEPHEN). The attended UI is out
   of step with each test's intent, and every attended step is to be audited before the next run: **PL-64**.
3. **`BM-PLAN` `finds` labels** are wrong for UICHECK and FLOOR (§3): **PL-65**.
4. **Detection binary `start_ret` capture** still reads 0 (§6): noted in **PL-44**, fixed with PL-53.
5. **Direction for the 6.5″ motor:** clockwise from the hub = 1-3-2-6-4-5 = negative ticks (§2): added to
   **PL-39**.
6. **T0-12 panel certified**, 90 per revolution MEASURED (§2): added to **PL-42**.
