#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for src/test_bench_dual.spin2's operator panel (window bmpanel), drawn
by the attended OUTSIDE segment (-D DUAL_PART_BRAKE, bench-run.sh tier dual-brake) and FLOOR segment
(-D DUAL_PART_FLOOR, tier dual-floor), by the tethered spin-in-place floor tier's SPIN and CREEP segments
(-D DUAL_PART_SPIN, task 3591), and by the no-motor-control UICHECK walkthrough (-D DUAL_PART_UICHECK,
tier dual-ui) -- DOCs/plans/MOTION-HARNESS-DESIGN.md sec 8.2 and 8.3, rebuilt per
DOCs/analyses/ATTENDED-UI-AUDIT-2026-09-15.md sec 6 (PL-64).

Task 3591 added the SPIN and CREEP screens, the DONE button (row 1, key D: "I did what this screen asked", the
way T0-24's DONE means it -- DOCs/procedures/PLOT-DISPLAY-RULES.md rule 10) and two number labels: LEG, whose
digits show the running leg number instead of a countdown, and WATCHING. Inserting DONE at index 3 moved
the row-2 answers and the verdict pair one index on; every Spin2 use names them, so only the generated block
moves. The DejaVu fallback below is gen_t0stop_assets.py's: the build and doc gates also run on Linux, where
neither macOS face exists, so without it the panel would render in the bitmap default at one size.

Structured exactly like tools/gen_t0hand_assets.py, and follows the same crop-and-overlay technique in
DOCs/REF-NO-COMMIT/dbg-display-theory/: layers are loaded once with LAYER; a frame is composed by
blitting opaque cells with CROP and then one UPDATE. The layout constants AND THE SCREEN TABLE below are the
SINGLE SOURCE OF TRUTH -- this script draws the BMPs from them, prints a ready-to-paste Spin2 CON block and
DAT screen table of the same numbers, and writes the run sheet's screen list, so the artwork, the code and
the run sheet cannot drift. The BM_* block and the bmScreens table in test_bench_dual.spin2 are byte-for-byte
what con_block() and dat_block() print; if anything here changes, re-run this script and re-paste.

    python3 tools/gen_dual_assets.py                    # write src/bm_*.bmp and the screen list, print CON + DAT
    python3 tools/gen_dual_assets.py --preview          # also write PNGs for visual check
    python3 tools/gen_dual_assets.py --no-screen-list   # the BMPs and the CON + DAT only; the screen list is
                                                        #  left as it is (a run that may not touch DOCs/)

Layers (the Spin2 LAYER numbers):
    1 bm_bg.bmp       header, prompt well, state well, countdown wells, empty button frames, footer
    2 bm_prompt.bmp   one prompt cell per SCREEN (PROMPT_W x PROMPT_H): a screen owns its prompt
    3 bm_state.bmp    one state word per row (STATE_W x STATE_H)
    4 bm_buttons.bmp  one button per row; column 0 normal (drawn), column 1 highlighted (chosen)
    5 bm_digits.bmp   "0".."9" plus a blank at index 10, for the 3-digit countdown
    6 bm_cdlabel.bmp  one countdown label per countdown kind; row 0 blank (no countdown)
    7 bm_strip.bmp    the verdict strip's text; row 0 blank, row 1 the judge instruction (dual-ui only)
    8 bm_heart.bmp    the heartbeat dot, off and on

THE SCREEN TABLE (audit sec 6 item 1): every attended screen names its prompt, its state word, the buttons
drawn and live on it, and what its countdown means. The attended parts draw a screen by its id, and the
dual-ui walkthrough previews the same rows, so what it previews is by construction what the run draws.

DEBUG LAYER requires 24-bit uncompressed (BI_RGB) BMP with no alpha, which is exactly what Pillow
writes for an "RGB" image saved as .bmp.

Sprite cells are OPAQUE -- there is no alpha -- so every cell carries the same background colour as
the region it lands on, or the blit leaves a seam. A button slot is erased by restoring it from
layer 1, whose empty frame is drawn at exactly the slot rectangle (the verdict slots restore to plain
panel, so an attended run never shows a frame there).

The .bmp outputs are committed beside the source. Whether the panel draws and takes input is shown on the
rig by the dual-ui walkthrough, which runs before dual-brake (STEPHEN 2026-09-15).
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- layout ----
# Keep these numbers identical to test_bench_dual.spin2's BM_* CON block (con_block() prints it).
PANEL_W, PANEL_H = 480, 306
PANEL_POS_X, PANEL_POS_Y = 60, 80

LYR_BG, LYR_PROMPT, LYR_STATE, LYR_BUTTONS, LYR_DIGITS, LYR_CDLABEL, LYR_STRIP, LYR_HEART = range(1, 9)

HDR_X, HDR_Y, HDR_W, HDR_H = 0, 0, 480, 28
HDR_TEXT_W = 436                           # header text box; the heartbeat sits to its right
HEART_X, HEART_Y, HEART_W, HEART_H = 448, 4, 24, 20
HEART_CELLS = 2                            # 0 off, 1 on
PROMPT_X, PROMPT_Y, PROMPT_W, PROMPT_H = 12, 34, 456, 76
STATE_X, STATE_Y, STATE_W, STATE_H = 12, 116, 236, 32
CD_LBL_X, CD_LBL_Y, CD_LBL_W, CD_LBL_H = 256, 116, 144, 32
CD_X, CD_Y = 404, 116
CD_COUNT = 3                               # up to 999 seconds
CD_TOP_DIV = 10 ** (CD_COUNT - 1)          # place value of the leftmost countdown digit

DGT_W, DGT_H = 20, 32
DGT_CELLS = 11                             # "0".."9" plus a blank at index 10
DGT_BLANK = 10

BTN_W, BTN_H = 108, 36
BTN_COL0_X, BTN_PITCH = 12, 116
BTN_ROW1_Y, BTN_ROW2_Y = 156, 198
BTN_ROW2_FIRST = 4                         # buttons 0..3 on row 1, 4..7 on row 2 (task 3591: DONE joined row 1)
BTN_STRIP_FIRST = 8                        # buttons 8..9 in the verdict strip
BTN_NORMAL, BTN_HILITE = 0, 1              # column in bm_buttons.bmp
BTN_VARIANTS = 2

STRIP_X, STRIP_Y, STRIP_W, STRIP_H = 12, 242, 224, 36
STRIP_BTN_X0 = 244                         # first verdict slot; the second is one BTN_PITCH to its right

FOOT_X, FOOT_Y, FOOT_W, FOOT_H = 12, 284, 456, 18
CELL_PAD = 8

# Domain values baked into the prompt text -- MUST match test_bench_dual.spin2's FLOOR_RUN_MS / 1_000,
# FLOOR_POWER and FLOOR_DIRECTION, and "HALF POWER" its STEER_POWER_HALF (50). Regenerate if any changes.
FLOOR_RUN_S = 2                            # a brief turn-direction observation (design sec 12.1 Q10)
FLOOR_POWER = 50
FLOOR_DIRECTION = 50
# Task 3591 -- MUST match test_bench_dual.spin2's SPIN_LEGS (the LEG label's range) and SPIN_LEG_DEG (the prompts'
# "ONE TURN": the travel limit is one revolution of the platform). Regenerate if either changes.
SPIN_LEGS = 12
SPIN_LEG_DEG = 360

# State words, in BM_STATE_* order. A screen names its default state; a few screens draw another at run time
# (a UI check step's progress, and the end screens' outcome).
STATES = [
    ("WAITING", "WAITING FOR START"),
    ("STARTING", "STARTING"),
    ("BRAKE_NOW", "BRAKE THE LEFT WHEEL NOW"),
    ("RELEASE", "RELEASE THE WHEEL"),
    ("OBSERVING", "OBSERVING"),
    ("ASK", "WHICH WAY DID IT TURN?"),
    ("DONE", "DONE"),
    ("SKIPPED", "SKIPPED BY YOU"),
    ("TIMED_OUT", "TIMED OUT"),
    ("WHEELS_AGAIN", "HANDS CLEAR - WHEELS RUN"),
    ("UI_CHECK", "UI CHECK - NOTHING MOVES"),
    ("UI_PASSED", "UI CHECK PASSED"),
    ("UI_FAILED", "UI CHECK FAILED"),
    ("UI_NOW_CLICK", "GOT THE KEY - NOW CLICK IT"),
    ("UI_NOW_KEY", "GOT THE CLICK - NOW THE KEY"),
    ("STOPPING", "STOPPING - HANDS CLEAR"),
    ("LOGGING", "WRITING THE LOG"),
    ("STOPPED_BY_YOU", "STOPPED BY YOU"),
    ("ENDED_EARLY", "ENDED EARLY - SEE THE LOG"),
    # Task 3591, the SPIN segment. INDEXED BY ARITHMETIC in test_bench_dual.spin2, so the order is the contract
    #  (check_layout() asserts it): a leg's word is BASE + speed * 2 + direction, speed SLOW, MEDIUM, BRISK and
    #  direction RIGHT (clockwise seen from above) then LEFT -- SPIN_SPEED_* and SPIN_DIR_* there. NXT_ is the
    #  READY screen's word, SPN_ the DRIVE screen's. Every name stays within the CON block's 24-column name field.
    ("NXT_R_SLOW", "NEXT: SPIN RIGHT, SLOW"),
    ("NXT_L_SLOW", "NEXT: SPIN LEFT, SLOW"),
    ("NXT_R_MED", "NEXT: SPIN RIGHT, MEDIUM"),
    ("NXT_L_MED", "NEXT: SPIN LEFT, MEDIUM"),
    ("NXT_R_BRISK", "NEXT: SPIN RIGHT, BRISK"),
    ("NXT_L_BRISK", "NEXT: SPIN LEFT, BRISK"),
    ("SPN_R_SLOW", "SPINNING RIGHT, SLOW"),
    ("SPN_L_SLOW", "SPINNING LEFT, SLOW"),
    ("SPN_R_MED", "SPINNING RIGHT, MEDIUM"),
    ("SPN_L_MED", "SPINNING LEFT, MEDIUM"),
    ("SPN_R_BRISK", "SPINNING RIGHT, BRISK"),
    ("SPN_L_BRISK", "SPINNING LEFT, BRISK"),
    ("FLT_NEXT_R", "NEXT: FAULT LEG, RIGHT"),
    ("FLT_NEXT_L", "NEXT: FAULT LEG, LEFT"),
    ("FLT_R", "FAULT LEG: SPINNING RIGHT"),
    ("FLT_L", "FAULT LEG: SPINNING LEFT"),
    # SPUN_: the SPIN segment's outcome, drawn on the CREEP segment's first screen (rule 10.4: a step that did not run)
    ("SPUN_ALL", "SPIN LEGS: ALL RAN"),
    ("SPUN_EARLY", "SPIN LEGS: ENDED EARLY"),
    ("SPUN_STOP", "SPIN LEGS: STOPPED BY YOU"),
    ("SPUN_SKIP", "SPIN LEGS: SKIPPED BY YOU"),
    ("SPUN_TIMEOUT", "SPIN LEGS: TIMED OUT"),
    # the CREEP segment: BASE + trial kind, kind COAST, LOWCEIL, HOLD (CRK_* there)
    ("CRP_COAST", "COAST CONTROL"),
    ("CRP_LOWCEIL", "LOW-CEILING CONTROL"),
    ("CRP_HOLD", "HOLD AT THE CEILING"),
    ("EXP_COAST", "EXPECT: ROLLS DOWNHILL"),
    ("EXP_LOWCEIL", "EXPECT: SLIPS, THEN DRAGS"),
    ("EXP_HOLD", "EXPECT: DOES NOT MOVE"),
    # what a trial did, in the API's own words for the hold (getHoldStatus(): HOLDING, SLIPPED, LIMITED)
    ("RES_ROLLED", "RESULT: ROLLED, BRAKED"),
    ("RES_NOROLL", "RESULT: DID NOT ROLL"),
    ("RES_HOLDING", "RESULT: HOLDING, STILL"),
    ("RES_CREPT", "RESULT: HOLDING, CREPT"),
    ("RES_SLIPPED", "RESULT: SLIPPED"),
    ("RES_LIMITED", "RESULT: LIMITED"),
    ("RES_NOTRUN", "RESULT: NOT MEASURED"),
]
STATE = {name: idx for idx, (name, _) in enumerate(STATES)}

# Buttons, in BM_BTN_* order: (name, label, key hint). The keys are test_bench_dual.spin2's keyButton() map.
# LOOKS RIGHT and SOMETHING WRONG are the dual-ui verdict: their keys are used by no attended screen, and they
# are drawn only in the verdict strip, so no input can both operate a screen and judge it (audit sec 6 item 2).
# DONE (task 3591) takes row 1's fourth slot: one meaning, "I have done what this screen asks" (rule 10).
BUTTONS = [
    ("START", "START", "KEY S"),
    ("SKIP", "SKIP", "KEY K"),
    ("STOP", "STOP", "SPACE BAR"),
    ("DONE", "DONE", "KEY D"),
    ("LEFT", "LEFT", "KEY L"),
    ("RIGHT", "RIGHT", "KEY R"),
    ("STRAIGHT", "STRAIGHT", "KEY T"),
    ("NOMOVE", "DID NOT MOVE", "KEY N"),
    ("LOOKS_RIGHT", "LOOKS RIGHT", "KEY Y"),
    ("WRONG", "SOMETHING WRONG", "KEY W"),
]
BTN = {name: idx for idx, (name, _, _) in enumerate(BUTTONS)}

# Countdown kinds, in BM_CD_* order (audit sec 6 item 4): a number on the panel has one meaning, shown beside it.
CD_KINDS = [
    ("NONE", ""),
    ("GIVES_UP", "GIVES UP IN (SECONDS)"),
    ("DRIVES_AGAIN", "WHEELS DRIVE AGAIN IN (SECONDS)"),
    ("DRIVING_FOR", "DRIVING FOR (SECONDS)"),
    ("CLOSES_IN", "CLOSES IN (SECONDS)"),
    # task 3591: LEG's digits are the running leg number, 1-based as the run sheet and the log number them, and
    #  never count down; WATCHING counts the creep window down
    ("LEG", "LEG NUMBER (1 TO %d)" % SPIN_LEGS),
    ("WATCHING", "WATCHING FOR (SECONDS)"),
]
CD = {name: idx for idx, (name, _) in enumerate(CD_KINDS)}

# Verdict strip rows, in BM_STRIP_* order.
STRIPS = [
    ("BLANK", ""),
    ("JUDGE", "JUDGE THE SCREEN ABOVE. ITS OWN BUTTONS DO NOTHING HERE."),
]

# THE SCREEN TABLE, in BM_SCR_* order: (name, prompt, default state, buttons drawn and live, countdown kind,
# the Spin2 constant its countdown starts from). Prompt cell index == screen index. A screen whose buttons
# are chosen at run time (UI_CONTROL: the one button under test) lists none here.
# Preview rows: dual-ui walks BM_SCR_PREVIEW_FIRST..BM_SCR_PREVIEW_LAST, every screen dual-brake draws.
SCREENS = [
    ("BRAKE_START",
     "HANDS CLEAR. CLICK START (KEY S): BOTH WHEELS SPIN UP AT HALF POWER, THEN THIS PANEL TELLS YOU TO BRAKE "
     "THE LEFT WHEEL (P32 BOARD). NOTHING MOVES BEFORE START.",
     "WAITING", ["START"], "GIVES_UP", "OPER_START_TIMEOUT_MS"),
    ("BRAKE_SPINUP",
     "BOTH WHEELS ARE SPINNING UP AT HALF POWER. HANDS CLEAR UNTIL THIS PANEL SAYS BRAKE. STOP (SPACE BAR) "
     "STOPS BOTH WHEELS.",
     "STARTING", ["STOP"], "NONE", "0"),
    ("BRAKE_NOW",
     "BRAKE THE LEFT WHEEL (P32 BOARD) NOW AND HOLD IT UNTIL THIS PANEL SAYS RELEASE. SKIP (KEY K) ENDS THIS "
     "STEP. STOP (SPACE BAR) STOPS BOTH WHEELS.",
     "BRAKE_NOW", ["SKIP", "STOP"], "GIVES_UP", "BRAKE_WAIT_MS"),
    ("BRAKE_RELEASE",
     "RELEASE THE WHEEL AND STEP BACK. WHEN THE COUNT REACHES 0 THE HARNESS DRIVES BOTH WHEELS AGAIN BY "
     "ITSELF. STOP (SPACE BAR) STOPS THEM.",
     "RELEASE", ["STOP"], "DRIVES_AGAIN", "S5_UNTOUCHED_MS"),
    ("BRAKE_ZSTEPS",
     "HANDS CLEAR. THE HARNESS IS DRIVING BOTH WHEELS BY ITSELF: RUN, STOP, RUN AGAIN. STOP (SPACE BAR) "
     "STOPS THEM.",
     "WHEELS_AGAIN", ["STOP"], "NONE", "0"),
    ("STOPPING",
     "BOTH WHEELS ARE STOPPING. LET GO OF ANY WHEEL AND KEEP HANDS CLEAR UNTIL THEY REST.",
     "STOPPING", ["STOP"], "NONE", "0"),
    ("LOGGING",
     "BOTH WHEELS ARE STOPPED AND RELEASED. WRITING THE LOG: THE DOT MAY PAUSE FOR A FEW SECONDS, THEN THE "
     "RESULT IS SHOWN.",
     "LOGGING", [], "NONE", "0"),
    ("END",
     "FINISHED. BOTH WHEELS ARE STOPPED AND RELEASED. THE RESULT IS BELOW. CLICK START (KEY S) TO CLOSE.",
     "DONE", ["START"], "CLOSES_IN", "OPER_END_TIMEOUT_MS"),
    ("FLOOR_START",
     "PLATFORM ON THE FLOOR, SPACE CLEAR. CLICK START (KEY S): IT DRIVES ABOUT %d SECONDS, POWER %d, "
     "DIRECTION %+d. NOTHING MOVES BEFORE START." % (FLOOR_RUN_S, FLOOR_POWER, FLOOR_DIRECTION),
     "WAITING", ["START"], "GIVES_UP", "OPER_START_TIMEOUT_MS"),
    ("FLOOR_STARTING",
     "STARTING THE DRIVE. STOP (SPACE BAR) STOPS IT.",
     "STARTING", ["STOP"], "NONE", "0"),
    ("FLOOR_DRIVE",
     "DRIVING. WATCH WHICH WAY THE PLATFORM TURNS. STOP (SPACE BAR) STOPS IT.",
     "OBSERVING", ["STOP"], "DRIVING_FOR", "FLOOR_RUN_MS"),
    ("FLOOR_ASK",
     "WHICH WAY DID IT TURN?",
     "ASK", ["LEFT", "RIGHT", "STRAIGHT", "NOMOVE"], "GIVES_UP", "OPER_ANSWER_TIMEOUT_MS"),
    ("UI_CONTROL",
     "UI CHECK -- NO MOTOR RUNS. FOR THE ONE BUTTON SHOWN: CLICK IT, AND PRESS THE KEY NAMED ON IT, IN "
     "EITHER ORDER.",
     "UI_CHECK", [], "GIVES_UP", "UI_STEP_TIMEOUT_MS"),
    ("UI_INTRO",
     "UI CHECK -- NO MOTOR RUNS. EVERY DUAL-BRAKE SCREEN COMES NEXT, DRAWN AS THE RUN DRAWS IT; ITS OWN "
     "BUTTONS DO NOTHING HERE. JUDGE EACH WITH THE TWO BUTTONS AT THE BOTTOM. CLICK START (KEY S) TO BEGIN.",
     "UI_CHECK", ["START"], "GIVES_UP", "UI_STEP_TIMEOUT_MS"),
    ("UI_END",
     "UI CHECK FINISHED -- NO MOTOR RAN. THE RESULT IS BELOW. CLICK START (KEY S) TO CLOSE.",
     "UI_PASSED", ["START"], "CLOSES_IN", "OPER_END_TIMEOUT_MS"),
    # Task 3591, the tethered spin-in-place floor tier (dual-spin). Every screen says what runs now, the one thing
    #  to do next, and what he should see; the state line under the prompt names the leg or the trial (its word is
    #  chosen at run time), and on the LEG screens the digits are the leg number (PLOT-DISPLAY-RULES.md rule 10).
    ("SPIN_READY",
     "SPIN LEG READY. STAND OUTSIDE THE CIRCLE THE PLATFORM SWEEPS, TETHER SLACK. CLICK START (KEY S): IT SPINS "
     "IN PLACE AS THE LINE BELOW SAYS AND STOPS BY ITSELF WITHIN ONE TURN. SKIP (KEY K) ENDS THE SPIN LEGS.",
     "NXT_R_SLOW", ["START", "SKIP"], "LEG", "OPER_START_TIMEOUT_MS"),
    ("SPIN_FAULT_READY",
     "FAULT LEG READY. IT SPINS SLOWLY, THEN ONE WHEEL IS FAULTED ON PURPOSE: YOU SHOULD SEE BOTH WHEELS STOP "
     "WITHIN A MOMENT. STAND CLEAR. CLICK START (KEY S) TO RUN IT. SKIP (KEY K) ENDS THE SPIN LEGS.",
     "FLT_NEXT_R", ["START", "SKIP"], "LEG", "OPER_START_TIMEOUT_MS"),
    ("SPIN_SETUP",
     "STARTING THE DRIVERS AND SETTING UP THE NEXT LEGS. NOTHING SPINS YET -- STAND CLEAR, THE LEG FOLLOWS AT "
     "ONCE. STOP (SPACE BAR) CANCELS IT.",
     "STARTING", ["STOP"], "NONE", "0"),
    ("SPIN_DRIVE",
     "SPINNING IN PLACE. YOU SHOULD SEE A STEADY TURN WITH NO DRIFT ACROSS THE FLOOR, THEN A GENTLE STOP BY "
     "ITSELF WITHIN ONE TURN. STOP (SPACE BAR) STOPS IT NOW.",
     "SPN_R_SLOW", ["STOP"], "LEG", "SPIN_LEG_MS"),
    ("SPIN_FAULT_DRIVE",
     "SPINNING SLOWLY. IN ABOUT TWO SECONDS ONE WHEEL IS FAULTED ON PURPOSE: BOTH WHEELS SHOULD STOP WITHIN A "
     "MOMENT, THE FAULTED ONE COASTING. STOP (SPACE BAR) STOPS IT NOW.",
     "FLT_R", ["STOP"], "LEG", "SPIN_LEG_MS"),
    ("CREEP_MOVE",
     "NOW THE INCLINE. CARRY THE PLATFORM ONTO THE INCLINE YOU MEASURED, WHEELS ROLLING STRAIGHT DOWN THE SLOPE, "
     "AND HOLD IT STILL WITH ONE HAND: ITS WHEELS ROLL FREELY. CLICK START (KEY S) WHILE HOLDING IT. SKIP (KEY K) "
     "ENDS THE TIER.",
     "SPUN_ALL", ["START", "SKIP"], "GIVES_UP", "OPER_START_TIMEOUT_MS"),
    ("CREEP_SETUP",
     "KEEP HOLDING THE PLATFORM STILL. THE HARNESS IS STARTING THE DRIVERS AND SETTING UP THE TRIAL NAMED BELOW. "
     "NOTHING MOVES. WAIT FOR THE NEXT SCREEN.",
     "CRP_COAST", [], "NONE", "0"),
    ("CREEP_RELEASE",
     "LET GO OF THE PLATFORM AND KEEP YOUR HAND JUST BELOW IT, THEN CLICK DONE (KEY D). WHAT IT SHOULD DO IS ON "
     "THE LINE BELOW. STOP (SPACE BAR) BRAKES THE WHEELS AT ONCE.",
     "EXP_COAST", ["STOP", "DONE"], "GIVES_UP", "OPER_START_TIMEOUT_MS"),
    ("CREEP_WATCH",
     "WATCHING FOR CREEP. HANDS OFF, YOUR HAND NEAR. IF IT ROLLS A FEW CENTIMETRES THE HARNESS BRAKES THE WHEELS "
     "ITSELF. STOP (SPACE BAR) BRAKES THEM NOW.",
     "EXP_COAST", ["STOP"], "WATCHING", "CREEP_WIN_MS"),
    ("CREEP_CATCH",
     "TAKE HOLD OF THE PLATFORM AGAIN AND KEEP IT STILL, THEN CLICK DONE (KEY D). THE WHEELS ARE THEN SWITCHED "
     "OFF AND ROLL FREELY, AND THE NEXT TRIAL, IF ANY, SETS UP WHILE YOU HOLD IT.",
     "RES_HOLDING", ["DONE"], "GIVES_UP", "OPER_ANSWER_TIMEOUT_MS"),
    ("SPIN_END",
     "FINISHED. THE RESULT IS BELOW. WHEN THIS PANEL CLOSES THE WHEELS ARE OFF AND ROLL FREELY: IF THE PLATFORM "
     "IS ON THE INCLINE, HOLD IT OR LIFT IT OFF. CLICK START (KEY S) TO CLOSE.",
     "DONE", ["START"], "CLOSES_IN", "OPER_END_TIMEOUT_MS"),
]
SCR = {name: idx for idx, (name, *_rest) in enumerate(SCREENS)}
SCR_PREVIEW_FIRST, SCR_PREVIEW_LAST = SCR["BRAKE_START"], SCR["END"]
SCR_LONGS = 4                              # state, live mask, countdown kind, countdown start (ms)

HEADER_TEXT = "MOTION HARNESS -- OPERATOR PANEL"
FOOTER_TEXT = "CLICK THIS WINDOW FIRST -- DOT BLINKING = HARNESS RUNNING -- PANIC: DISCONNECT THE BATTERY"

SCREEN_LIST_PATH = os.path.join("DOCs", "analyses", "bench", "ATTENDED-PANEL-SCREENS.md")

# ---------------------------------------------------------------- colours ---
C_PANEL    = (28, 32, 38)
C_WELL     = (12, 13, 16)
C_HDR      = (48, 40, 20)
C_TEXT     = (232, 236, 240)
C_DIM      = (120, 128, 138)
C_AMBER    = (240, 176, 48)
C_FRAME    = (72, 80, 92)
C_BTN      = (40, 46, 56)
C_INK_DARK = (20, 20, 20)

FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(size):
    for path in FONTS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    sys.stderr.write("WARNING: no TrueType font found; falling back to the bitmap default\n")
    return ImageFont.load_default()


def text_width(d, text, fnt):
    l, _, r, _ = d.textbbox((0, 0), text, font=fnt)
    return r - l


def fit(d, text, size, max_w):
    """Largest font at or below `size` whose rendered text fits max_w. Measured, not guessed --
    see gen_bench_char_assets.py's own note on why a guessed size clips at the panel edge."""
    while size > 8:
        f = font(size)
        if text_width(d, text, f) <= max_w:
            return f
        size -= 1
    return font(8)


def wrap_lines(d, text, fnt, max_w):
    """Greedy word wrap at max_w; a single word wider than max_w stays on its own line (fit_wrapped()
    then shrinks the font until it fits)."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if not cur or text_width(d, trial, fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_wrapped(d, text, size, max_w, max_h, line_gap=3):
    """Largest font at or below `size` whose word-wrapped text fits max_w x max_h. Measured, not guessed."""
    while size > 8:
        f = font(size)
        lines = wrap_lines(d, text, f, max_w)
        widest = max(text_width(d, ln, f) for ln in lines)
        line_h = size + line_gap
        if widest <= max_w and line_h * len(lines) <= max_h:
            return f, lines, line_h
        size -= 1
    f = font(8)
    return f, wrap_lines(d, text, f, max_w), 8 + line_gap


def centre(d, box, text, fnt, fill):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + (w - (r - l)) / 2 - l, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


def wrapped_cell(d, box, text, size, fill, pad=CELL_PAD, gap=3):
    """Word-wrapped text, left-aligned and vertically centred in box."""
    x, y, w, h = box
    if not text:
        return
    f, lines, line_h = fit_wrapped(d, text, size, w - 2 * pad, h - 4, gap)
    top = y + (h - line_h * len(lines)) // 2
    for n, ln in enumerate(lines):
        l, t, _, _ = d.textbbox((0, 0), ln, font=f)
        d.text((x + pad - l, top + n * line_h - t), ln, font=f, fill=fill)


def slot(btn_idx):
    """Top-left of a button's slot on the panel -- the same arithmetic as test_bench_dual.spin2's
    buttonSlot(), and the bounding box its mouseButton() hit-tests."""
    if btn_idx >= BTN_STRIP_FIRST:
        return STRIP_BTN_X0 + (btn_idx - BTN_STRIP_FIRST) * BTN_PITCH, STRIP_Y
    if btn_idx >= BTN_ROW2_FIRST:
        return BTN_COL0_X + (btn_idx - BTN_ROW2_FIRST) * BTN_PITCH, BTN_ROW2_Y
    return BTN_COL0_X + btn_idx * BTN_PITCH, BTN_ROW1_Y


def live_mask_expr(names):
    """The Spin2 constant expression for a screen's live mask."""
    if not names:
        return "0"
    return " | ".join("DECOD BM_BTN_%s" % n for n in names)


def check_layout():
    """Refuse to write assets whose tables or geometry disagree with the constants."""
    for name, prompt, state, buttons, cd, cd_ms in SCREENS:
        assert state in STATE, "screen %s names an unknown state %r" % (name, state)
        assert cd in CD, "screen %s names an unknown countdown kind %r" % (name, cd)
        assert (cd == "NONE") == (cd_ms == "0"), "screen %s: a countdown kind needs a start, and only it" % name
        for b in buttons:
            assert b in BTN, "screen %s names an unknown button %r" % (name, b)
            assert BTN[b] < BTN_STRIP_FIRST, "screen %s draws a verdict button %r as its own control" % (name, b)
    texts = [s[1] for s in SCREENS] + [s[1] for s in STATES] + [c[1] for c in CD_KINDS] + [s[1] for s in STRIPS]
    texts += [b[1] for b in BUTTONS] + [b[2] for b in BUTTONS] + [HEADER_TEXT, FOOTER_TEXT]
    for text in texts:
        assert all(ord(ch) < 128 for ch in text), "non-ASCII panel text: %r" % text
    for idx in range(len(BUTTONS)):
        x, y = slot(idx)
        assert x + BTN_W <= PANEL_W and y + BTN_H <= FOOT_Y, "button %d slot leaves its area" % idx
    assert STRIP_X + STRIP_W <= STRIP_BTN_X0, "strip text overlaps the verdict buttons"
    assert BTN_ROW2_Y + BTN_H <= STRIP_Y, "button row 2 overlaps the verdict strip"
    assert HDR_TEXT_W <= HEART_X and HEART_X + HEART_W <= PANEL_W and HEART_Y + HEART_H <= HDR_H, "heartbeat misplaced"
    assert PROMPT_Y + PROMPT_H <= STATE_Y, "prompt well overlaps the state row"
    assert STATE_X + STATE_W <= CD_LBL_X, "state well overlaps the countdown label"
    assert CD_LBL_X + CD_LBL_W <= CD_X, "countdown label overlaps the digits"
    assert CD_X + CD_COUNT * DGT_W <= PANEL_W, "countdown digits leave the panel"
    assert STATE_Y + STATE_H <= BTN_ROW1_Y, "state row overlaps the buttons"
    assert FOOT_Y + FOOT_H <= PANEL_H, "footer leaves the panel"
    # task 3591: test_bench_dual.spin2 reaches these state words by BASE + offset, so their order is part of the contract
    runs = [("NXT_", ["R_SLOW", "L_SLOW", "R_MED", "L_MED", "R_BRISK", "L_BRISK"]),
            ("SPN_", ["R_SLOW", "L_SLOW", "R_MED", "L_MED", "R_BRISK", "L_BRISK"]),
            ("FLT_NEXT_", ["R", "L"]), ("FLT_", ["R", "L"]),
            ("CRP_", ["COAST", "LOWCEIL", "HOLD"]), ("EXP_", ["COAST", "LOWCEIL", "HOLD"])]
    for prefix, suffixes in runs:
        base = STATE[prefix + suffixes[0]]
        for offset, suffix in enumerate(suffixes):
            assert STATE[prefix + suffix] == base + offset, "state %s%s is out of its arithmetic order" % (prefix, suffix)
    # every generated name keeps the CON block's alignment (con_block() pads names to 24 columns)
    for group in con_groups():
        for name, _value in group:
            assert len(name) < 24, "generated name %s overruns the CON block's name column" % name


def draw_button(d, x, y, label, key, hilite):
    fill = C_AMBER if hilite else C_BTN
    ink = C_INK_DARK if hilite else C_TEXT
    sub = C_INK_DARK if hilite else C_DIM
    d.rectangle([x, y, x + BTN_W - 1, y + BTN_H - 1], fill=fill, outline=C_FRAME)
    half = BTN_H // 2
    centre(d, (x, y + 2, BTN_W, half), label, fit(d, label, 15, BTN_W - CELL_PAD), ink)
    centre(d, (x, y + half, BTN_W, half - 2), key, fit(d, key, 11, BTN_W - CELL_PAD), sub)


def build_background():
    img = Image.new("RGB", (PANEL_W, PANEL_H), C_PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle([HDR_X, HDR_Y, HDR_X + HDR_W - 1, HDR_Y + HDR_H - 1], fill=C_HDR)
    centre(d, (HDR_X, HDR_Y, HDR_TEXT_W, HDR_H), HEADER_TEXT, fit(d, HEADER_TEXT, 18, HDR_TEXT_W - 16), C_TEXT)

    # wells the prompt, state and digit cells blit into, so an un-blitted frame still looks deliberate
    d.rectangle([PROMPT_X, PROMPT_Y, PROMPT_X + PROMPT_W - 1, PROMPT_Y + PROMPT_H - 1], fill=C_WELL)
    d.rectangle([STATE_X, STATE_Y, STATE_X + STATE_W - 1, STATE_Y + STATE_H - 1], fill=C_PANEL)
    d.rectangle([CD_X, CD_Y, CD_X + CD_COUNT * DGT_W - 1, CD_Y + DGT_H - 1], fill=C_WELL)

    # empty button frames for the screen's own slots: exactly each slot rectangle, so restoring a slot from
    # this layer erases it. The verdict slots stay plain panel: an attended run never shows a frame there.
    for idx in range(BTN_STRIP_FIRST):
        x, y = slot(idx)
        d.rectangle([x, y, x + BTN_W - 1, y + BTN_H - 1], fill=C_PANEL, outline=C_FRAME)

    d.text((FOOT_X, FOOT_Y), FOOTER_TEXT, font=fit(d, FOOTER_TEXT, 13, FOOT_W), fill=C_AMBER)
    return img


def build_prompts():
    img = Image.new("RGB", (PROMPT_W, PROMPT_H * len(SCREENS)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, screen in enumerate(SCREENS):
        wrapped_cell(d, (0, i * PROMPT_H, PROMPT_W, PROMPT_H), screen[1], 18, C_TEXT)
    return img


def build_state():
    img = Image.new("RGB", (STATE_W, STATE_H * len(STATES)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, (_, text) in enumerate(STATES):
        centre(d, (0, i * STATE_H, STATE_W, STATE_H), text, fit(d, text, 20, STATE_W - 12), C_AMBER)
    return img


def build_buttons():
    img = Image.new("RGB", (BTN_W * BTN_VARIANTS, BTN_H * len(BUTTONS)), C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (_, label, key) in enumerate(BUTTONS):
        draw_button(d, BTN_NORMAL * BTN_W, i * BTN_H, label, key, False)
        draw_button(d, BTN_HILITE * BTN_W, i * BTN_H, label, key, True)
    return img


def build_digits():
    img = Image.new("RGB", (DGT_W * DGT_CELLS, DGT_H), C_WELL)
    d = ImageDraw.Draw(img)
    f = font(26)
    for i in range(10):
        centre(d, (i * DGT_W, 0, DGT_W, DGT_H), str(i), f, C_TEXT)
    # index 10 stays blank -- a leading zero, or no countdown at all
    return img


def build_cdlabels():
    img = Image.new("RGB", (CD_LBL_W, CD_LBL_H * len(CD_KINDS)), C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (_, text) in enumerate(CD_KINDS):
        wrapped_cell(d, (0, i * CD_LBL_H, CD_LBL_W, CD_LBL_H), text, 13, C_DIM, pad=2, gap=1)
    return img


def build_strip():
    img = Image.new("RGB", (STRIP_W, STRIP_H * len(STRIPS)), C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (_, text) in enumerate(STRIPS):
        wrapped_cell(d, (0, i * STRIP_H, STRIP_W, STRIP_H), text, 14, C_AMBER, pad=2, gap=1)
    return img


def build_heart():
    img = Image.new("RGB", (HEART_W * HEART_CELLS, HEART_H), C_HDR)
    d = ImageDraw.Draw(img)
    r = 7
    for i in range(HEART_CELLS):
        cx, cy = i * HEART_W + HEART_W // 2, HEART_H // 2
        box = [cx - r, cy - r, cx + r, cy + r]
        if i == 0:
            d.ellipse(box, outline=C_DIM, width=2)
        else:
            d.ellipse(box, fill=C_AMBER)
    return img


ASSETS = [
    ("bm_bg.bmp",      build_background),
    ("bm_prompt.bmp",  build_prompts),
    ("bm_state.bmp",   build_state),
    ("bm_buttons.bmp", build_buttons),
    ("bm_digits.bmp",  build_digits),
    ("bm_cdlabel.bmp", build_cdlabels),
    ("bm_strip.bmp",   build_strip),
    ("bm_heart.bmp",   build_heart),
]


def con_groups():
    return [
        [
            ("BM_PANEL_W", PANEL_W),
            ("BM_PANEL_H", PANEL_H),
            ("BM_PANEL_POS_X", PANEL_POS_X),
            ("BM_PANEL_POS_Y", PANEL_POS_Y),
        ],
        [
            ("BM_LYR_BG", LYR_BG),
            ("BM_LYR_PROMPT", LYR_PROMPT),
            ("BM_LYR_STATE", LYR_STATE),
            ("BM_LYR_BUTTONS", LYR_BUTTONS),
            ("BM_LYR_DIGITS", LYR_DIGITS),
            ("BM_LYR_CDLABEL", LYR_CDLABEL),
            ("BM_LYR_STRIP", LYR_STRIP),
            ("BM_LYR_HEART", LYR_HEART),
        ],
        [
            ("BM_PROMPT_X", PROMPT_X),
            ("BM_PROMPT_Y", PROMPT_Y),
            ("BM_PROMPT_W", PROMPT_W),
            ("BM_PROMPT_H", PROMPT_H),
        ],
        [("BM_SCR_%s" % name, idx) for idx, (name, *_r) in enumerate(SCREENS)] + [
            ("BM_SCR_COUNT", len(SCREENS)),
            ("BM_SCR_LONGS", SCR_LONGS),
            ("BM_SCR_PREVIEW_FIRST", SCR_PREVIEW_FIRST),
            ("BM_SCR_PREVIEW_LAST", SCR_PREVIEW_LAST),
        ],
        [
            ("BM_STATE_X", STATE_X),
            ("BM_STATE_Y", STATE_Y),
            ("BM_STATE_W", STATE_W),
            ("BM_STATE_H", STATE_H),
        ] + [("BM_STATE_%s" % name, idx) for idx, (name, _) in enumerate(STATES)],
        [
            ("BM_BTN_W", BTN_W),
            ("BM_BTN_H", BTN_H),
            ("BM_BTN_COL0_X", BTN_COL0_X),
            ("BM_BTN_PITCH", BTN_PITCH),
            ("BM_BTN_ROW1_Y", BTN_ROW1_Y),
            ("BM_BTN_ROW2_Y", BTN_ROW2_Y),
            ("BM_BTN_ROW2_FIRST", BTN_ROW2_FIRST),
            ("BM_BTN_STRIP_FIRST", BTN_STRIP_FIRST),
            ("BM_BTN_NORMAL", BTN_NORMAL),
            ("BM_BTN_HILITE", BTN_HILITE),
        ] + [("BM_BTN_%s" % name, idx) for idx, (name, _, _) in enumerate(BUTTONS)] + [
            ("BM_BTN_COUNT", len(BUTTONS)),
        ],
        [
            ("BM_STRIP_X", STRIP_X),
            ("BM_STRIP_Y", STRIP_Y),
            ("BM_STRIP_W", STRIP_W),
            ("BM_STRIP_H", STRIP_H),
            ("BM_STRIP_BTN_X0", STRIP_BTN_X0),
        ] + [("BM_STRIP_%s" % name, idx) for idx, (name, _) in enumerate(STRIPS)],
        [
            ("BM_DGT_W", DGT_W),
            ("BM_DGT_H", DGT_H),
            ("BM_DGT_BLANK", DGT_BLANK),
            ("BM_CD_X", CD_X),
            ("BM_CD_Y", CD_Y),
            ("BM_CD_COUNT", CD_COUNT),
            ("BM_CD_TOP_DIV", CD_TOP_DIV),
            ("BM_CD_LBL_X", CD_LBL_X),
            ("BM_CD_LBL_Y", CD_LBL_Y),
            ("BM_CD_LBL_W", CD_LBL_W),
            ("BM_CD_LBL_H", CD_LBL_H),
        ] + [("BM_CD_%s" % name, idx) for idx, (name, _) in enumerate(CD_KINDS)],
        [
            ("BM_HEART_X", HEART_X),
            ("BM_HEART_Y", HEART_Y),
            ("BM_HEART_W", HEART_W),
            ("BM_HEART_H", HEART_H),
        ],
    ]


def con_block():
    out = ["", "CON { operator panel geometry -- GENERATED by tools/gen_dual_assets.py, do not hand-edit }"]
    for group in con_groups():
        out.append("")
        for name, value in group:
            out.append("    %-24s= %d" % (name, value))
    out.append("")
    return "\n".join(out)


def dat_block():
    out = ["", "DAT { attended screen table -- GENERATED by tools/gen_dual_assets.py, do not hand-edit }", "",
           "' one row per BM_SCR_*, BM_SCR_LONGS longs: default state, buttons drawn and live, countdown kind,",
           "'  countdown start (ms)"]
    for idx, (name, _prompt, state, buttons, cd, cd_ms) in enumerate(SCREENS):
        label = "bmScreens" if idx == 0 else ""
        row = "%s, %s, BM_CD_%s, %s" % ("BM_STATE_" + state, live_mask_expr(buttons), cd, cd_ms)
        out.append("%-15s LONG    %-100s ' BM_SCR_%s" % (label, row, name))
    out.append("")
    return "\n".join(out)


def screen_list():
    """The run sheet's screen list: what each attended screen says and offers, from the same table."""
    out = ["# Attended operator panel -- every screen",
           "",
           "GENERATED by `tools/gen_dual_assets.py` from the same table `src/test_bench_dual.spin2` draws, so this",
           "list and the panel cannot disagree. Do not hand-edit; re-run the generator.",
           "",
           "- **The dot at the top right blinks while the harness runs.** If it stops blinking while a wheel can",
           "  move, the harness has stopped: note the time, and use the battery disconnect if a wheel is driven.",
           "- **STOP (space bar) is live on every screen where a wheel can move.**",
           "- **dual-ui** previews every `dual-brake` screen below, drawn as the run draws it. The screen's own",
           "  buttons are drawn but do nothing there; judge each with LOOKS RIGHT (key Y) or SOMETHING WRONG",
           "  (key W) in the strip at the bottom.",
           "",
           "| # | Screen | Prompt | State | Buttons (key) | Countdown |",
           "|---|---|---|---|---|---|"]
    state_text = dict(STATES)
    cd_text = dict(CD_KINDS)
    btn_text = {name: "%s (%s)" % (label, key) for name, label, key in BUTTONS}
    for idx, (name, prompt, state, buttons, cd, _cd_ms) in enumerate(SCREENS):
        shown = ", ".join(btn_text[b] for b in buttons) if buttons else ("the button under test" if name == "UI_CONTROL" else "none")
        out.append("| %d | %s | %s | %s | %s | %s |" % (idx, name, prompt, state_text[state], shown,
                                                       cd_text[cd] if cd != "NONE" else "none"))
    out.append("")
    out.append("End screens draw their outcome in place of DONE: %s." % ", ".join(
        state_text[s] for s in ("TIMED_OUT", "SKIPPED", "STOPPED_BY_YOU", "ENDED_EARLY")))
    out.append("")
    return "\n".join(out)


def main():
    check_layout()
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    out = os.path.join(root, "src")
    preview = "--preview" in sys.argv
    for name, build in ASSETS:
        img = build()
        path = os.path.join(out, name)
        img.save(path)
        sys.stderr.write(f"wrote {path}  {img.size[0]}x{img.size[1]}\n")
        if preview:
            png = os.path.join(out, name.replace(".bmp", ".png"))
            img.save(png)
            sys.stderr.write(f"      + {png}\n")
    if "--no-screen-list" in sys.argv:
        sys.stderr.write(f"--no-screen-list: {SCREEN_LIST_PATH} left as it is\n")
    else:
        list_path = os.path.join(root, SCREEN_LIST_PATH)
        with open(list_path, "w") as fh:
            fh.write(screen_list())
        sys.stderr.write(f"wrote {list_path}\n")
    print(con_block())
    print(dat_block())


if __name__ == "__main__":
    main()
