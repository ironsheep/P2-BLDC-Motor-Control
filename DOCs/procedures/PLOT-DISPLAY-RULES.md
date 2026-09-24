# PLOT display rules -- what keeps a DEBUG panel drawing

**What this is.** The rules a DEBUG `PLOT` panel in this tree must follow, each with the log line, commit or
named authority that earned it. Stephen, 2026-09-21: *"We get these working! then we produce a document that
precludes these failures of PLOT display from biting us ever again... too many hours lost."*

**How to build a panel** is not repeated here. It is Stephen's supplied reference set, read in full before
building (doctrine overlay P7): `DOCs/REF-NO-COMMIT/dbg-display-theory/`
(`THEORY-OF-OPERATION-crop-overlay.md`, `DISPLAY-PATTERNS-builders-guide.md`,
`HOWTO-build-debug-displays-with-claude.md`), and `DOCs/REF-NO-COMMIT/P2-HAZARD-REGISTER.md` section A for the
debug channel. This page adds what those documents do not: what failed on *this* rig, and the rule that
prevents it.

**Where it is enforced.** Rule 1 is a gate: `tools/bench-run.sh` refuses a tier over the limit before the
terminal starts, and `tools/build-check.sh` step 5 checks every tier at commit time. The rest are review rules
(`.claude/skill-conventions.md` `CONFORMANCE_GUIDES`, strength gate).

---

## 1 · The image's DEBUG data must fit, measured by subtraction

**Rule.** A tier's DEBUG footprint is the size of its `-d` image minus the same build's size without `-d`
(register DBG-1). It must not exceed `DEBUG_FOOTPRINT_MAX` in `tools/bench-run.sh`, currently **12,404 bytes**:
the largest measured to run intact, never the documented cap. Never estimate it by counting literals: DBG-2
warns that counting gives confident wrong answers.

**Why.** A `-d` image loses every `debug()` record whose bytes lie past image offset 13,684. The record is cut
at that byte or never sent. Neither the compiler nor the terminal reports it, and records before the edge
print normally. Panel code sits late in a file, so it is the first to go (PL-114).

**Evidence.** The same byte, four times, each image rebuilt from the commit that ran and matched to the
downloaded size:

- `18207c0` (40,918 B): `...RET_NEG_NOLEAK,measured,TRUE,` stopped at byte 13,683. Before this finding it was
  read as a cog-burst loss (PL-85).
- `60e135b` (44,665 B): `T0-23,begin,no_bo` (PL-94).
- `a37bac1` (44,439 B): `` `PLOT bench TITLE 'T0-12 hand-rotation an`` (`debug_260920-182345.log:23`).
- 2026-09-22: the `-u` captures `usb-traffic_260922-215918.log` and `usb-traffic_260922-220003.log` contain no
  `PLOT`, `LAYER` or `crop` byte. The P2 never sent them, with only cog 0 running.

The build that drew, `6aed714` (2026-09-15), measured 12,404 bytes. The first that lost its panel measured
15,619. PL-92's audit had recorded *"11,470 of 15,872 bytes -- neither near a limit"*: a count, and wrong.

## 2 · Over the limit, keep every line of output

**Rule.** Never delete or shorten a diagnostic to fit (DBG-2: *"gate the call sites -- never delete the
diagnostic"*). Use the register's mitigations, all of which keep the output:

| Mitigation | Register | What it does here |
|---|---|---|
| Compile out what the build never runs | DBG-16, TCH-3 | `#ifdef` the **bodies**, not just the calls. A call skipped at run time still compiles its records. `T0_ATTENDED` in `test_bench_t0.spin2` |
| Text from hub, not from the record | DBG-2 | Pass tokens as `@"..."` / `DAT` strings through the `zstr_` debug formatter: `emitCellBool()`, `emitCellDecl()`, `emitCellNum()` |
| Merge statements | DBG-4 | Several values in one line, one record |
| Channel it | DBG-5, DBG-6 | `debug[N]()` under a per-object `DEBUG_MASK`. Plain `debug()` ignores every mask |

**Evidence.** `f34e6fd` took `t0` from 16,004 to 10,511 bytes, `t0-hand` from 15,674 to 7,592 and `t0-stopmode`
from 16,611 to 8,529. The unattended build's gating left it byte-identical, and a script check found every
field of the helper-rendered lines matched the literals they replaced. Stephen, 2026-09-23: *"All can come
into play while not having to reduce the debug output volume we need for testing."*

## 3 · Establish what the P2 sent before reasoning about anything else

**Rule.** Every bench run carries a USB-level capture: `tools/bench-run.sh` runs `pnut-term-ts -u -r <binary>`,
`-u` first (Stephen, 2026-09-23). The first question about a missing or damaged display command is whether it
is in the `usb-traffic_*.log`. Answer that before any theory.

**Why.** The debug log is not the wire (register OUT-7). Two wrong causes were filed for this failure before
anyone read the wire: the runner's `--console-mode` (PL-92) and cog bursts (PL-85/PL-94). The first capture
that was read settled it (rule 1).

## 4 · Presume the terminal correct -- the defect is ours

**Rule.** A display defect seen only in this tree is looked for in this tree. `pnut-term-ts` draws panels
correctly in Stephen's other repositories. Stephen, 2026-09-23: *"the fix is on our side not pnut-term-ts...
i have many repo's doing this correctly"*. The capture in rule 3 locates the fault on our side; it is not a
way to put the terminal back in the running (doctrine overlay P7).

## 5 · Build the panel exactly on the supplied technique

**Rule.** Every panel follows the builder's guide:

- `{Spin2_v50}` is the source's first line (guide section 9).
- The window is created with `HIDEXY UPDATE`; layers are loaded once; each frame is its crops then exactly
  one `UPDATE` (guide sections 2-3).
- `CROP` takes the source rectangle first and the destination last (guide section 3).
- Artwork is 24-bit, uncompressed, no-alpha BMP, beside the `.spin2`. The terminal runs from `src/`, so bare
  `LAYER` names resolve and the log lands in `src/logs/` (guide section 6; HOWTO section 5).
- Layout constants come from the asset generator's printed `CON` block, never typed by hand (HOWTO section 3;
  `tools/gen_t0hand_assets.py`, `tools/gen_t0stop_assets.py`).

**Why.** Panels built off the technique failed at the rig twice. On 2026-09-11 a supplied display technique was
overridden on a spec lookup, and the panel drew blank at a lost bench trip (doctrine overlay P7). At Visit 1,
T0-12 was built as an empty PLOT window that only hosted `PC_KEY`, and the cell was lost (PL-42,
`plans/archive/PUNCH-LIST-ARCHIVE-2026-09-23.md`).

## 6 · Window names and display text follow p2kb's rules

**Rule.** A window name starts with a letter or `_`, is none of the 103 reserved debug-display words, and is
unique within its first 30 characters; matching is case-insensitive. Text arguments (`TITLE`, `LAYER` file
names) are in **single** quotes, and contain **no apostrophe and no parenthesis**. A `)` in the text closes the
`debug()` call, and the rest of the line becomes a Spin2 comment. It compiles clean. `tools/check_style.sh`
check T128 enforces the parenthesis half.

**Why.** Both failures are silent at compile time and at run time. A bad name opens no window, and every later
command to it goes nowhere. A double-quoted title is silently dropped (p2kb `p2kbSpin2Debug`,
`window_name_rules` and `string_quoting`). `bench` and `t0stop` are both legal; the 2026-09-20 probe drew
both (`debug_260920-215353.log`).

**The parenthesis (PL-128).** T0-24's title `'... RIGHT WHEEL (P16 BOARD)'` lost the `' SIZE 560 470 POS 60 60 HIDEXY
UPDATE` after it. The window opened at the host's default size, showing a quarter of the panel. The wire capture
`usb-traffic_260924-162831.log` ends the create at `(P16 BOARD`; the image built from that source holds no
`HIDEXY UPDATE`, and the fixed source's does. The storyboard review could not catch it, because it renders the art,
not the create command.

## 7 · Declare the coordinate basis; never rely on the default

**Rule.** A panel that reads the mouse declares `cartesian 1` right after its window opens. On this host, that
makes `PC_MOUSE` report y **down from the top-left**, the basis the asset generators author slots in
(`test_bench_dual.spin2:6736`, `:6758`). Never mix a guide example's `y` with ours without first checking which
basis that example used (guide section 4).

**Why.** The two authorities disagree about the default. The builder's guide section 4 gives top-left and y
down; p2kb `p2kbSpin2Plot` gives bottom-left and y up, *"hardware-verified EF-020"*. The rig sided with p2kb:
the 2026-09-15 `dual-ui` panel, built on the guide's default, registered no click on any button while three
key presses arrived (`debug_260915-134659.log`; `MOTION-HARNESS-DESIGN.md` 12.9 correction). Declaring
`cartesian 1` fixed it. The only panel that hit-tests, `bmpanel` in `test_bench_dual.spin2`, declares it.

## 8 · `PC_KEY` / `PC_MOUSE` are last in their statement, and a lone poll means no window

**Rule.** `pc_key` and `pc_mouse` are each the last element of their `debug()`. `pc_mouse` gets seven
consecutive longs. The window must have focus (guide section 7).

**Diagnostic.** A log with **one** `` `name PC_KEY`` line and then silence means the window never existed: the
poll waits for a host answer that cannot come. `debug_260922-215919.log` shows one `PC_KEY` at 21:59:20.613,
then nothing for 20 s. The same tier with a window, even a misshapen one, polled 196 times
(`debug_260920-182345.log`).

## 9 · No output across a cog start or stop

**Rule.** No cog prints across a cog start or stop. `benchLog.cogEventBegin()` / `cogEventEnd()` bracket every
one (the quiet window).

**Why.** Output interleaves at cog-start bursts: `CogCog1Cog0` run-together prefixes on the wire
(`usb-traffic_260917-174323.log`, PL-85). This is separate from rule 1. PL-85's lost *verdict* was the data
limit, but the interleaving is real.

## 10 · The screen keeps the operator in step with the program

**Rule.** Every screen states four things:

1. what the program is doing now;
2. the one thing the operator does next;
3. what they should feel or see while doing it -- the row's prediction, in plain words, on the panel and not
   only in the log;
4. when a step did not run, that it did not and why.

**Every operator action is a titled button, clicked, not a keystroke.** The button's title is the action
("START ROW", "DONE", "ABORT"), hit-tested through `PC_MOUSE` under `cartesian 1`, as `bmpanel` in
`test_bench_dual.spin2` does. A key may duplicate a button, but is never the only control. A keystroke first
costs the operator focusing the window; a click does not. Count what each step costs them (reach, focus,
read, act) before the panel is built, and remove what can be removed.

**The operator ends every step they take part in.** A timer may end only a step they are not part of. A step's result
stays on the screen, saying what the program saw and whether it counted, until they click NEXT or REDO. Every step can
be redone. Only live buttons are drawn, and the input is polled often enough that a click cannot fall between polls.
Every input taken is logged, with the button it hit or the position it missed at. **The review renders every screen
of the sequence, in order, and reads them at the desk before the visit** (PL-127).

One control has one meaning. Rows use one numbering (1-based) in the runner's banner, the panel and the log.
One vocabulary, matching the API, names each state. The operator is never asked for sub-second timing: take
the moment from a sensor, and let the button say only "done".

**Why.** Stephen, 2026-09-23, after T0-24's first run with a working panel: *"the instructions were really
confusing, and I got out of sync with what you were trying to do."* That panel had S and SPACE carrying three
meanings between them. It numbered rows 1-6 while the log numbered them 0-5. It called the SM_BRAKE row "HOLD
MODE". It never said what a row should feel like. It asked for SPACE "as you let go" (PL-115). And it left a
"HANDS OFF -- spins under power" card up for two rows that never spun (PL-116). Doctrine overlay P7 carries
the rule. On buttons, Stephen, the same day: *"buttons with titles should be all we need in this case vs.
keystrokes. I have to focus the panel to press keys so mouse clicks is less effort -- always think about the
interaction effort when designing UIs."*

## 11 · Signals that are not signals

- **`[SYSTEM] WINDOW_PLACED` does not mean a window opened.** It is absent from the 2026-09-20 probe log, whose
  two windows both drew (`BENCH-LOG-STUDY-2026-09-21.md` F3 amendment).
- **A present display command in the log does not mean a complete one.** Check it against the source byte
  for byte; the 2026-09-20 create stopped mid-title and the window opened anyway.

---

*Written 2026-09-23 under «#3585». Change a rule only with the evidence that moves it, and update its citation.*
