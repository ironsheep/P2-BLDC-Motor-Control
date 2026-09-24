# T0-24 — the stop-state hand test, designed as a lesson

**Task:** «#3619». **Finding:** PL-127. **Supersedes** the interaction half of «#3607»/«#3617». It keeps their
instrument: re-armed holds, `band_ticks`, forced faults, and the e-stop applied at the band.

Stephen, 2026-09-24: *"It really should tell me which wheel, what you need me to do, and then wait for me to do it
before it moves on to the next one... Study the interaction pedagogically, figure out how to tell me everything I
need to know for each step and how to give me a restart step. Your abort and done buttons are not working at all."*

---

## 1 · What went wrong, as a lesson would see it

A bench row is a small lesson. The program has to say what is about to happen and what the operator does. It has to
say what they should notice, and then let them do it at their own pace. It shows what was seen, and it lets them
try again. The src_rev 13 panel breaks each of those:

| A lesson needs | src_rev 13 did |
|---|---|
| **An overview before acting** (advance organiser) | showed only the row's name and "click START ROW"; the action appeared after START |
| **One instruction at a time, in a fixed place** | one run-on paragraph per phase, with instructions, the meanings of the readings and status codes mixed together |
| **Prediction before the act** | the feel was buried mid-paragraph, and missing on several phases |
| **The learner sets the pace** | rows ended on timers: 2–7 s after the first push, 400 ms after rest, or 120 s with nobody there |
| **Feedback on the act, in words** | "READING 1/2/3" wells, hold state as a number (`0 OFF 1 HOLDING…`), and the result screen replaced within 20 ms |
| **Controls that visibly work** | three buttons always drawn and mostly dead; no sign that a click registered |
| **Recovery** | none: a spoilt row was spent |

## 2 · Principles the new panel follows

1. **Every screen answers five questions in fixed places:** which wheel and which row (header and row line), what
   the program is doing (**NOW**), the one thing to do (**YOU**), what to notice (**FEEL**), and what ends the
   step (**ENDS**).
2. **A row is previewed before it starts.** The row's first screen shows its whole plan: what the row tests, what
   you will do, and what you should feel. Only then START ROW.
3. **You end every step you take part in.** Hand rows end only on DONE or ABORT. The program says when it has what
   it needs ("GOT IT — CLICK DONE"), and waits.
4. **The program ends only its own steps.** Setup and the powered fault rows end by themselves, because you are
   not part of them. A powered row always shows ABORT.
5. **The result stays until you choose.** Every row ends on a RESULT screen: what was expected, what was seen, and
   whether it was measured and, if not, why. Its buttons are **NEXT ROW** and **REDO ROW**.
6. **Every row can be redone.** REDO ROW re-runs its setup and its step. The log keeps every try, and the cells use
   the last one.
7. **Only live buttons are drawn,** and a clicked button lights before the screen changes, so you can see the
   click registered. The forward action (START ROW, DONE, NEXT ROW) is always the **right** button, and the other
   one (ABORT, REDO ROW) is always the **left**. The hand does not move to go forward. Keys only duplicate them:
   Enter for the right button, Esc for the left.
8. **No double-advance:** after any screen change, input is ignored for 300 ms and until the mouse button has been
   seen up. A double click on DONE cannot also press NEXT ROW.
9. **Words, not codes:** the live line under **SEEN NOW** says in words what the program sees ("PUSH SEEN — HOLD
   RISING", "SPINNING — NOT FAST ENOUGH YET"). Each reading's label names its quantity and unit for that row.

## 3 · The screen, top to bottom (560 × 470)

| Zone | Content | Source |
|---|---|---|
| Header | `T0-24 STOP-STATE HAND TEST — RIGHT WHEEL (P16 BOARD)` | background |
| Row line | `ROW n OF 8 —` row name | digit + name strip |
| Phase banner | the kind of step, coloured (below) | banner strip |
| Card | four labelled lines: NOW / YOU / FEEL / ENDS on an act screen; THIS ROW / YOU WILL / YOU SHOULD FEEL / TO BEGIN on an intro; EXPECTED / … on a result | card strip, one card per (row, screen) |
| SEEN NOW | a status phrase | status strip |
| Readings | two, each with its own label and unit | label strip + digits |
| Buttons | left slot, right slot; only live buttons drawn | button strip |
| Footer | `PANIC: PULL THE PACK — CLICK THE WINDOW FIRST — ENTER = RIGHT BUTTON, ESC = LEFT BUTTON` | background |

**Phase banners:** `READ THIS ROW, THEN CLICK START ROW` (grey) · `HANDS OFF — SETTING UP` (amber) · `YOUR TURN`
(green) · `HANDS OFF — THE WHEEL IS POWERED` (red) · `RESULT — NEXT ROW OR REDO ROW` (blue) · `ALL ROWS DONE`
(grey) · `DRIVER DID NOT START` (red).

## 4 · The storyboard — every row, every screen

Each row runs **INTRO → SETUP → ACT → RESULT**. SETUP shows the INTRO card under the amber banner, with the
setup's own phrase under SEEN NOW. RESULT → REDO ROW goes back to SETUP. RESULT → NEXT ROW goes to the next
row's INTRO.

### Rows 1–3: the hold (the driver holds the stopped wheel; you push against it)

| Screen | Row 1 HOLD-RISE | Row 2 HOLD-SLIP | Row 3 HOLD-LIMIT |
|---|---|---|---|
| INTRO: this row | The driver holds the stopped wheel. You check the hold gets stronger when you push. | The hold is set weak on purpose. You check it gives way and hands over to the brake. | You push steadily at the hold's limit. You check it lets go after about 2 s. |
| INTRO: you will | Push the right wheel a little and keep pushing, then let go. | Turn the right wheel firmly, about a quarter turn. | Push the right wheel and hold it steady for about 3 s. |
| INTRO: feel | The resistance grows over about ¼ s, then stays firm. | It gives way almost at once, then drags against your turn. | It holds firm, then lets go. |
| SETUP phrase | `ARMING THE HOLD` | `ARMING A WEAK HOLD` | `ARMING THE HOLD` |
| ACT (YOUR TURN) | NOW: the hold is on. YOU: push and keep pushing. FEEL: as above. ENDS: when you have felt it, let go and click DONE. | same shape | same shape |
| SEEN NOW | `WAITING FOR YOUR PUSH` → `PUSH SEEN — HOLD RISING` → `AT THE CEILING — GOT IT, LET GO AND CLICK DONE` (or `SLIPPED` / `FAULTED`, not expected) | `WAITING FOR YOUR PUSH` → `PUSH SEEN` → `SLIPPED — IT GAVE WAY — GOT IT, CLICK DONE` | … → `AT THE CEILING — KEEP HOLDING` → `LIMITED — IT LET GO — GOT IT, CLICK DONE` |
| Readings (act) | HOLD DUTY % · PUSHED BY (TICKS) | same | same |
| RESULT: expected | The hold reaches its ceiling within 0.4 s of your push, and never slips. | It slips (gives way) before any fault. | It lets go (LIMITED) while you hold it at the ceiling. |
| Readings (result) | MS TO CEILING · PUSHED BY (TICKS) | MS TO SLIP · PUSHED BY (TICKS) | MS TO LET GO · PUSHED BY (TICKS) |

### Rows 4, 5 and 8: you spin the wheel

| Screen | Row 4 COAST AT REST | Row 5 E-STOP AS IT COASTS | Row 8 DRIVER COG STOPPED |
|---|---|---|---|
| INTRO: this row | The stopped wheel is set to coast. You check it spins freely. | You check the e-stop brakes the wheel hard. The program applies it as the wheel slows. | The driver is stopped and the pins are released: the free reference every coast is compared with. |
| INTRO: you will | Spin the right wheel hard by hand and let go. | Spin the right wheel hard by hand and let go. | Spin the right wheel hard by hand and let go. |
| INTRO: feel | It spins freely and coasts to a stop. | It starts to coast, then stops abruptly. | It coasts to a stop, just like row 4. |
| SETUP phrase | `SETTING COAST MODE` | `SETTING COAST MODE` | `STOPPING THE DRIVER` |
| ACT ENDS | when it has stopped, click DONE. Too slow? Spin it again, as often as you like. | same | same |
| SEEN NOW | `WAITING FOR YOUR SPIN` → `SPINNING — NOT FAST ENOUGH YET` / `FAST ENOUGH — LET GO` → `SLOWING — MEASURING` → `STOPPED — GOT IT, CLICK DONE` or `STOPPED — TOO SLOW, SPIN AGAIN HARDER` | adds `E-STOP APPLIED` | as row 4 |
| Readings (act) | SPEED (TICKS/S) · HALL TICKS | same | same |
| RESULT: expected | A coast: 7 or more ticks from the measuring speed to rest. | A short: 4 or fewer ticks from the measuring speed to rest. | A coast: 7 or more ticks, as row 4. |
| Readings (result) | BAND TICKS · BAND MS | same | same |

The measuring speed is 120 ticks/s. Every spin is its own **try**: it ends when the wheel has been still for
400 ms, and it is logged. The row's reading is the last try that passed the measuring speed. A slower spin after it
does not erase it, and SEEN NOW says which applies. Row 5 releases the e-stop at rest after each try, so the next
spin starts free.

### Rows 6–7: the program drives and faults the wheel (hands off)

| Screen | Row 6 FAULT, COAST MODE | Row 7 FAULT, BRAKE MODE |
|---|---|---|
| INTRO: this row | The program spins the right wheel under power and then faults it on purpose, in coast mode. | The same in brake mode. |
| INTRO: you will | Nothing: hands off. Watch the wheel. ABORT stops it at once. | same |
| INTRO: feel | After the fault it coasts to a stop. | After the fault it stops almost at once. |
| ACT (red banner) | NOW: driving the wheel. YOU: hands off, watch. ENDS: by itself when the wheel stops; ABORT stops it now. | same |
| SEEN NOW | `SPINNING UP` → `AT SPEED — FAULT COMING` → `FAULT FORCED — WATCH IT STOP` → result | same |
| Readings (act) | SPEED (TICKS/S) · HALL TICKS | same |
| RESULT: expected | A coast: 7 or more ticks, and the driver still faulted. | A short: 4 or fewer ticks, and still faulted. |

### Result "why" phrases (under SEEN NOW on a RESULT screen)

`MEASURED` · `NOT MEASURED — NO PUSH SEEN` · `NOT MEASURED — THE HOLD WAS NOT FRESH` ·
`NOT MEASURED — NO SPIN WAS FAST ENOUGH` · `NOT MEASURED — THE E-STOP WAS NOT APPLIED` ·
`NOT MEASURED — YOU ABORTED IT` · `NOT MEASURED — IT NEVER REACHED SPEED` ·
`NOT MEASURED — THE FAULT DID NOT HAPPEN` · `NOT MEASURED — THE SETUP FAILED` ·
`STOPPED AT THE 10 A LIMIT — NOT MEASURED`

The exact text of every phrase is `STATUSES` in `tools/gen_t0stop_assets.py`, the one source. Row 8's SETUP screen shows
no ABORT: its setup is `stop()`, run on the panel cog, and nothing polls a button during it.

## 5 · Why the clicks were lost, and the construction that cannot lose them

`PC_MOUSE`'s button is a **live** state (p2kb `p2kbSpin2DbgPcMouse`: *"0, or -1 if pressed"*), not a latch. A click is
seen only when a poll lands while the button is down. src_rev 13 measured and polled on one cog. It polled every
~100–150 ms, and not at all while the wheel turned, because each poll stops the cog for ~30 ms (measured,
`debug_260923-193439.log:36-60`), and that merges hall ticks.

**Construction:** two cogs, the shape of the proven `test_dog_panel.spin2` (its UI loop polls key and mouse every
25 ms, and all the real work runs elsewhere).

- **The panel cog (cog 0)** runs the row sequence and the screen. It polls `PC_MOUSE` on every pass, and `PC_KEY`
  on every third pass. With a 10 ms wait, that is one mouse read about every 30 ms, well inside any click. It
  redraws only on a change, and readings at most 5 times a second.
- **The measure cog** owns the hall poll, the hold sampling and every timed act: the e-stop at the band entry, the
  forced fault and the 10 A abort. It takes a job from hub (SETUP, ACT or TEARDOWN for a row), publishes its
  status phrase and live readings to hub, and watches hub flags for DONE and ABORT on every 1 ms poll.
- **The measure cog prints nothing while it measures.** DEBUG output is serialised on `LOCK[15]` (hazard register
  DBG-10), so a print could wait on the panel's 30 ms input read, and a stalled hall poll merges ticks. It buffers
  every try's record and every 10 ms hold sample in hub. The panel cog prints them after the step, outside the
  measured interval (doctrine D6). The hold buffer is a ring. If a row outruns it, the log says how many samples
  were dropped. Nothing is silently capped.
- Every motor call a row makes goes from the measure cog, so its errors land in that cog's `getError()` slot, and
  it drains them.

## 6 · The log

| Record | When |
|---|---|
| `T0-24,screen,row,N,id,R,phase,P,status,S` | every screen change |
| `T0-24,input,via,MOUSE|KEY,x,…,y,…,key,…,hit,<BUTTON>|MISS,live,<mask>` | every press, including a miss |
| `T0-24,row,N,try,K,…` | each try, printed after the step |
| `T0-24,hold_log,…` | the hold samples, printed after the step, with `dropped,N` |
| `T0-24,row,N,result,measured,…,why,…` | each RESULT screen |
| the ten cells | once, after the last row, from each row's last try |

## 7 · Verification

- **Desk walk:** a script renders every screen of every row from the generated art, in sequence order, and they
  are read as the operator will read them: which wheel, what to do, what to feel, what ends the step, and whether
  the buttons shown are exactly the live ones.
- **Construction checks in the source:** no hand step ends on a timer; every hand step's wait loop exits only on
  DONE or ABORT; the measure cog contains no `debug()`.
- **Compile:** `t0-stopmode` and `t0-stopmode-fltfirst` build with a DEBUG footprint under PLOT-DISPLAY-RULES rule
  1's limit; build-check and style are green.
- **At the rig (the next `t0-stopmode`):** every click appears in the log as an input record. Every row waits for
  DONE or ends by itself only when it is a powered row. REDO ROW re-runs a row. The ten cells report.
