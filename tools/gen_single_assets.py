#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for src/test_bench_single.spin2's attended hand tests on the Doco bench (window
sgpanel): the hand load at low speed (-D SINGLE_PART_HANDLOAD, tiers single-handload-v12p0 / -v24p0), the held stop
pushed by hand (-D SINGLE_PART_HELDPUSH, single-heldpush-v12p0 / -v24p0) -- task 3679 phase 2c; and the hand turn with the
motor UNPOWERED (-D SINGLE_PART_HANDTURN, tier single-recheck-v12p0) -- task 3692, D1a. The supply sag and the
cloth pinch were removed 2026-10-04 (STEPHEN: qualify the Doco as the 6.5in, no new measurements; task 3691).

EXTENDS tools/gen_t0stop_assets.py's pattern (T0-24's stop-state hand test, PL-127; DOCs/plans/T0-24-INTERACTION-
DESIGN.md), the panel that ran on this rig and drew, took every click on a titled button, and redid a row
(DOCs/analyses/bench/2026-09-25/VISIT-10-DUALFAULT-T0-EVALUATION.md sec 5: UI-CLICK PASS, UI-WAIT PASS, REDO works).
Its geometry is kept (560 x 470, the eight layers, the card, status, reading and button slots), and its drawing helpers
(font(), fit(), wrap_lines(), centre(), left(), draw_card(), build_digits()) are IMPORTED from it, not copied, so the two
panels cannot drift apart in how they draw. What this script adds, and only this:
  - a step line in place of T0-24's row line: STEP n OF N (both digits blitted: a leg has one to three steps), the
    step's name, and the TOLD supply (this bench senses none, so the panel repeats what the runner's banner says);
  - its own tables: steps, phases (INTRO, SETUP, ACT, RESULT, SKIP for the default-limit step the
    program does not run), banners, status phrases, reading labels, buttons and the whole-run screens;
  - NO KEYS (PLOT-DISPLAY-RULES.md rule 10; the dispatch for task 3679 phase 2c): a button is the only control, so a
    button cell carries its title alone, and the footer says no key is read.
The crop-and-overlay technique is the supplied one (DOCs/REF-NO-COMMIT/dbg-display-theory/): layers are loaded once with
LAYER; a frame is composed by blitting opaque cells with CROP and then one UPDATE.

THE SCREEN TABLE IS THE CONTRACT. For each step and phase, SCREENS below names the banner, the card, the two reading
labels and the two buttons; the whole-run screens (starting, the run stopped, all done) are SPECIALS. The harness reads
the same tables (printed as DAT sgScreenTab and sgSpecialTab), and --storyboard renders them in the order each tier
shows them. So the screens reviewed at the desk are the screens the harness draws.

    python3 tools/gen_single_assets.py                      # write src/sg_*.bmp, print CON + DAT
    python3 tools/gen_single_assets.py --preview            # also write a PNG of each layer beside it
    python3 tools/gen_single_assets.py --storyboard DIR     # also render every screen of every tier, in order, to DIR

DEBUG LAYER requires 24-bit uncompressed (BI_RGB) BMP with no alpha, which is exactly what Pillow writes for an "RGB"
image saved as .bmp. Sprite cells are OPAQUE, so every cell carries the colour of the region it lands on.
"""

import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_t0stop_assets as base  # noqa: E402  -- the pattern this extends; its helpers draw every cell here

font, fit, wrap_lines, centre, left = base.font, base.fit, base.wrap_lines, base.centre, base.left

# ---------------------------------------------------------------- layout ----
# T0-24's geometry where the two panels share an element (base.*), so its proven slots are the slots here.
PANEL_W, PANEL_H = base.PANEL_W, base.PANEL_H              # also the literal SIZE in sgSetupPanel()'s PLOT create
HDR_H = base.HDR_H
STEP_LINE_Y = base.ROW_LINE_Y                               # "STEP" (background), digit, "OF" (background), digit, name, supply
STEPLBL_X = 12
SNUM_X = 64
OF_X = 96
SCOUNT_X = 126
NAME_X, NAME_W, NAME_H = 160, 266, base.NAME_H
SUP_X, SUP_W = 432, 116                                     # the told supply: a names-layer row, blitted this wide
BAN_X, BAN_Y, BAN_W, BAN_H = base.BAN_X, base.BAN_Y, base.BAN_W, base.BAN_H
CARD_X, CARD_Y, CARD_W, CARD_H = base.CARD_X, base.CARD_Y, base.CARD_W, base.CARD_H
SEEN_LBL_X, SEEN_Y, SEEN_LBL_W = base.SEEN_LBL_X, base.SEEN_Y, base.SEEN_LBL_W
STAT_X, STAT_W, STAT_H = base.STAT_X, base.STAT_W, base.STAT_H
LBL_X, LBL_W, LBL_H = base.LBL_X, base.LBL_W, base.LBL_H
READ1_Y, READ2_Y = base.READ1_Y, base.READ2_Y
READ_X, READ_PITCH, READ_COUNT = base.READ_X, base.READ_PITCH, base.READ_COUNT
DGT_W, DGT_H, DGT_BLANK = base.DGT_W, base.DGT_H, base.DGT_BLANK
BTN_W, BTN_H = base.BTN_W, base.BTN_H
BTN_L_X, BTN_R_X, BTN_Y = base.BTN_L_X, base.BTN_R_X, base.BTN_Y
FOOT_X, FOOT_Y, FOOT_W, FOOT_H = base.FOOT_X, base.FOOT_Y, base.FOOT_W, base.FOOT_H

HEADER_TEXT = "DOCO BENCH  --  HAND TESTS ON THE SHAFT  --  ONE MOTOR, P16 BOARD"
FOOTER_TEXT = "PANIC: TURN THE SUPPLY OFF.   CLICK THE BUTTONS -- NO KEY IS READ."

# ---------------------------------------------------------------- tables ----
# Phase banners (layer 3): (id, text, fill).
C_GREY, C_AMBER_BAN, C_RED_BAN, C_GREEN_BAN, C_BLUE_BAN = (70, 76, 86), (150, 104, 20), (160, 40, 36), (34, 120, 60), (36, 84, 150)
BANNERS = [
    ("B_INTRO", "READ THIS STEP, THEN CLICK START STEP", C_GREY),
    ("B_SETUP", "HANDS OFF  --  SETTING UP", C_AMBER_BAN),
    ("B_SETUP_DRIVE", "HANDS OFF  --  THE SHAFT IS SPEEDING UP", C_RED_BAN),
    ("B_TURN", "YOUR TURN", C_GREEN_BAN),
    ("B_TURN_POWERED", "YOUR TURN  --  THE SHAFT IS POWERED", C_GREEN_BAN),
    ("B_RESULT", "RESULT  --  READ IT, THEN CHOOSE A BUTTON", C_BLUE_BAN),
    ("B_SKIPPED", "NOT RUN  --  READ WHY, THEN CLICK THE BUTTON", C_AMBER_BAN),
    ("B_STARTING", "HANDS OFF  --  STARTING", C_AMBER_BAN),
    ("B_STOPPED", "THE RUN STOPPED ITSELF", C_RED_BAN),
    ("B_ALLDONE", "ALL STEPS DONE", C_GREY),
    ("B_WIRING", "HANDS OFF  --  THE MOTOR STARTS AND TURNS A LITTLE", C_RED_BAN),
]

# Status phrases under SEEN NOW (layer 6): (id, text, ink) -- "wait" neutral, "good" green (the program has what it
# needs), "warn" amber (not measured, or the run stopped). The measure cog publishes the live ones; cog 0 the rest.
STATUSES = [
    ("ST_BLANK", "", "wait"),
    ("ST_WAIT_START", "WAITING FOR YOU TO CLICK START STEP", "wait"),
    ("ST_STARTING", "READING THE BOARD, STARTING THE MOTOR -- NOTHING TURNS", "wait"),
    # setup
    ("ST_SET_LIMIT", "SETTING THE TEST LIMIT", "wait"),
    ("ST_SET_DEFAULT", "SETTING THE DEFAULT LIMIT", "wait"),
    ("ST_SPEEDING", "SPEEDING UP  --  HANDS OFF", "wait"),
    ("ST_ARM_HOLD", "ARMING THE HOLD  --  HANDS OFF", "wait"),
    # the hand load's ACT
    ("ST_GRIP_NOW", "TURNING  --  SLOW IT BY HAND NOW", "wait"),
    ("ST_SLOWING", "SLOWING UNDER YOUR HAND  --  KEEP HOLDING", "wait"),
    ("ST_STANDING", "STOPPED IN YOUR HAND  --  HOLD IT STILL", "wait"),
    ("ST_LATCHED", "IT STOPPED ITSELF  --  GOT IT, LET GO", "good"),
    ("ST_NOLATCH", "STOOD STILL, NO STOP  --  THE PROGRAM STOPPED IT", "warn"),
    ("ST_STEPCAP", "STEP CHARGE LIMIT  --  THE PROGRAM STOPPED IT", "warn"),
    # the held stop's ACT
    ("ST_TURN_NOW", "HOLDING  --  TURN THE SHAFT SLOWLY NOW", "wait"),
    ("ST_TURNED_FREE", "TURNED  --  THE HOLD HAS NOT SEEN IT YET", "wait"),
    ("ST_PUSHING", "THE HOLD PUSHES BACK  --  RISING", "wait"),
    ("ST_AT_CEIL", "AT ITS CEILING  --  KEEP TURNING", "wait"),
    ("ST_GAVE_WAY", "IT GAVE WAY  --  GOT IT, LET GO", "good"),
    ("ST_HOLD_LIMITED", "IT LET GO AT ITS TIME LIMIT", "warn"),
    # results
    ("ST_MEASURED", "MEASURED", "good"),
    ("ST_NM_NO_SPEED", "NOT MEASURED  --  IT NEVER REACHED SPEED", "warn"),
    ("ST_NM_SETUP", "NOT MEASURED  --  THE SETUP FAILED", "warn"),
    ("ST_NM_STOPPED", "NOT MEASURED  --  YOU STOPPED IT", "warn"),
    ("ST_NM_NO_GRIP", "NOT MEASURED  --  NO GRIP SEEN", "warn"),
    ("ST_NM_NO_STAND", "NOT MEASURED  --  THE SHAFT NEVER STOOD STILL", "warn"),
    ("ST_NM_STEPCAP", "NOT MEASURED  --  THE STEP CHARGE LIMIT CAME FIRST", "warn"),
    ("ST_NM_NOT_FRESH", "NOT MEASURED  --  THE HOLD WAS NOT FRESH", "warn"),
    ("ST_NM_NO_TURN", "NOT MEASURED  --  NO TURN SEEN", "warn"),
    ("ST_NM_NO_SLIP", "NOT MEASURED  --  IT DID NOT GIVE WAY", "warn"),
    ("ST_RISE_TOO_FAST", "GAVE WAY  --  TOO FAST FOR THE RISE, REDO SLOWER", "warn"),
    ("ST_SAME_WAY", "SAME WAY AS STEP 1  --  REDO, TURN IT THE OTHER WAY", "warn"),
    ("ST_NM_FAULT", "THE DRIVE FAULTED UNDER YOUR HAND  --  A FINDING", "warn"),
    ("ST_DEF_SKIPPED", "NOT RUN  --  TOO LITTLE CHARGE LEFT IN THIS TEST", "warn"),
    # the hand turn (task 3692: the motor is unpowered)
    ("ST_HT_WAIT", "UNPOWERED  --  TURN THE SHAFT CLOCKWISE NOW", "wait"),
    ("ST_HT_TURNING", "TURNING  --  KEEP GOING, ABOUT THREE TURNS", "wait"),
    ("ST_HT_ENOUGH", "ABOUT THREE TURNS  --  CLICK DONE", "good"),
    ("ST_NM_FEW_TURNS", "NOT MEASURED  --  UNDER TWO TURNS SEEN, REDO", "warn"),
    ("ST_NM_TOO_FAST", "NOT MEASURED  --  TOO FAST TO COUNT, REDO SLOWER", "warn"),
    ("ST_WIRING", "STARTING THE MOTOR, THE WIRING CHECK  --  HANDS OFF", "wait"),
    # whole-run screens
    ("ST_ALL_DONE", "ALL STEPS DONE  --  THE MOTOR IS STOPPED", "good"),
    ("ST_NO_STEPS", "THIS SUPPLY HAS NO STEPS IN THIS TEST  --  NOTHING RAN", "warn"),
    ("ST_RS_BOARD", "THE BOARD DID NOT READ AS A REV A  --  NOTHING RAN", "warn"),
    ("ST_RS_START", "THE MOTOR DID NOT START  --  NOTHING RAN", "warn"),
    ("ST_RS_ENCODER", "THE ENCODER DID NOT START  --  NOTHING RAN", "warn"),
    ("ST_RS_ZERO", "THE CURRENT SENSE ZERO IS OUT OF BAND  --  NOTHING RAN", "warn"),
    ("ST_RS_LIMIT", "A CURRENT LIMIT DID NOT TAKE  --  STOPPED", "warn"),
    ("ST_RS_SETTING", "A SETTING DID NOT TAKE  --  STOPPED", "warn"),
    ("ST_RS_OVERCURRENT", "OVER-CURRENT  --  THE RUN STOPPED", "warn"),
    ("ST_RS_CHARGE", "THE RUN CHARGE CAP  --  THE RUN STOPPED", "warn"),
    ("ST_RS_LEGCAP", "THE TEST CHARGE CAP  --  THE RUN STOPPED", "warn"),
    ("ST_RS_TIME", "THE RUN TIME CAP  --  THE RUN STOPPED", "warn"),
    ("ST_RS_ENCWIN", "THE ENCODER DISAGREED WITH THE HALLS  --  STOPPED", "warn"),
    ("ST_RS_WIRING", "THE WIRING CHECK DID NOT PASS  --  STOPPED", "warn"),
    ("ST_RS_OTHER", "THE RUN STOPPED  --  THE LOG SAYS WHY", "warn"),
]

# Reading labels (layer 7).
LABELS = [
    ("L_BLANK", ""),
    ("L_RPM", "SPEED, RPM"),
    ("L_MA", "CURRENT, MA"),
    ("L_LATCH_MS", "STOPPED ITSELF AFTER, MS"),
    ("L_PEAK_MA", "PEAK CURRENT, MA"),
    ("L_DEG", "TURNED, DEGREES"),
    ("L_HOLD_PCT", "HOLD EFFORT, % OF CEILING"),
    ("L_SLIP_DEG", "GAVE WAY AT, DEGREES"),
    ("L_RISE_MS", "RISE TO CEILING, MS"),
    ("L_HALL_TICKS", "HALL TICKS COUNTED"),
    ("L_ENC_COUNTS", "ENCODER COUNTS"),
    ("L_TPR_X10", "HALL TICKS A TURN, X10"),
    ("L_TURNS_X10", "ENCODER TURNS, X10"),
]

# Buttons (layer 8): (id, title, slot). The forward action is always the RIGHT slot, STOP MOTOR and REDO STEP the LEFT,
# T0-24's rule. No key: a cell carries its title alone.
BUTTONS = [
    ("BT_NONE", "", None),
    ("BT_START", "START STEP", "R"),
    ("BT_DONE", "DONE", "R"),
    ("BT_NEXT", "NEXT STEP", "R"),
    ("BT_FINISH", "FINISH", "R"),
    ("BT_STOP", "STOP MOTOR", "L"),
    ("BT_REDO", "REDO STEP", "L"),
]

PHASES = ["PH_INTRO", "PH_SETUP", "PH_ACT", "PH_RESULT", "PH_SKIP"]

# The told supply, one names-layer row per Rev A row in the library's order (test_bench_single.spin2 DAT rowMv).
SUPPLIES = ["TOLD 7.4 V", "TOLD 11.1 V", "TOLD 12 V", "TOLD 14.8 V", "TOLD 18.5 V", "TOLD 22.2 V", "TOLD 24 V"]

# ---------------------------------------------------------------- the steps --
# Each step: id; name (the step line); kind (hand, held); powered (the shaft is driven in SETUP and ACT, so
# STOP MOTOR is live there); the cards (intro: THIS STEP / YOU WILL / YOU SHOULD FEEL; act: NOW / YOU / FEEL / ENDS;
# expect: the RESULT's EXPECTED line; skip: the default step's SKIP card); the reading
# labels in ACT and in RESULT. The FEEL lines are the analysis's predictions (DOCs/analyses/DOCO-DESK-MODEL-2026-10-03.md
# sec 4.1 P-H1/P-H2, sec 4.2 P-H4), in the operator's words.
HAND_ENDS = "By itself, when the drive stops itself. STOP MOTOR stops it now."
STEPS = [
    dict(id="HL_4A", name="HAND LOAD, 4 A TEST LIMIT", kind="hand", powered=True, setup="ST_SET_LIMIT",
         intro=("The shaft turns slowly by itself, about 200 rpm, under a 4 A test current limit. You slow it by hand "
                "until it stops, and hold it still.",
                "Click START STEP, wait for YOUR TURN, then slow the shaft by hand until it stops, and hold it still.",
                "A steady push, about 60 to 80 mN.m, a firm finger twist, that does not grow. About a second after the "
                "shaft stops, the drive stops itself and the push ends."),
         act=("The shaft turns slowly under a 4 A test limit.",
              "Slow it by hand until it stops, then hold it still.",
              "A steady push that does not grow; about a second after it stops, the push ends.",
              HAND_ENDS),
         expect="The drive stopped itself 1.0 to 1.17 s after the shaft stood still, with no fault.",
         act_lbl=("L_RPM", "L_MA"), res_lbl=("L_LATCH_MS", "L_PEAK_MA")),
    dict(id="HL_2A", name="HAND LOAD, 2 A TEST LIMIT", kind="hand", powered=True, setup="ST_SET_LIMIT",
         intro=("As the last step, under a 2 A test limit: the shaft turns slowly by itself and you slow it by hand "
                "until it stops, and hold it still.",
                "Click START STEP, wait for YOUR TURN, then slow the shaft by hand until it stops, and hold it still.",
                "A steady push, about 55 to 80 mN.m; at 24 V it may feel the same as the 4 A step. About a second "
                "after the shaft stops, the drive stops itself."),
         act=("The shaft turns slowly under a 2 A test limit.",
              "Slow it by hand until it stops, then hold it still.",
              "A steady push that does not grow; about a second after it stops, the push ends.",
              HAND_ENDS),
         expect="The drive stopped itself 1.0 to 1.17 s after the shaft stood still, with no fault.",
         act_lbl=("L_RPM", "L_MA"), res_lbl=("L_LATCH_MS", "L_PEAK_MA")),
    dict(id="HL_DEF", name="HAND LOAD, DEFAULT LIMIT", kind="hand", powered=True, setup="ST_SET_DEFAULT",
         intro=("No test limit this time, at 12 V only, and briefly: the push is much stronger. The shaft turns "
                "slowly by itself; you grip it firmly, stop it and hold it still.",
                "Click START STEP, wait for YOUR TURN, then grip the shaft firmly and hold it still. Do not let it creep.",
                "A strong push, about 120 mN.m, twice the last steps, and a hum. About a second after the shaft stops, "
                "the drive stops itself. If you cannot hold it still, click STOP MOTOR."),
         act=("The shaft turns slowly with the default limit: nothing limits the current.",
              "Grip it firmly, stop it, and hold it still.",
              "A strong push and a hum, for about a second.",
              "By itself when the drive stops itself, or the program stops it about a second after it stood still. "
              "STOP MOTOR stops it now."),
         expect="The drive stopped itself 1.0 to 1.17 s after the shaft stood still. Nothing folded the current back.",
         skip=("This step draws about 6 A for a second. The charge cap of this test has too little left for that, so "
               "the program did not run it.",
               "Nothing. Click the button to go on."),
         act_lbl=("L_RPM", "L_MA"), res_lbl=("L_LATCH_MS", "L_PEAK_MA")),
    dict(id="HP_ONE", name="HELD STOP, TURN IT ONE WAY", kind="held", powered=False, setup="ST_ARM_HOLD",
         intro=("The held stop. The motor is stopped and holds the shaft where it stopped. You turn the shaft slowly "
                "by hand until the hold gives way.",
                "Click START STEP, wait for YOUR TURN, then turn the shaft slowly either way, about a twelfth of a turn, "
                "until it gives way. Then let go.",
                "Almost nothing for up to 15 degrees, then a light push back, about 20 to 45 mN.m, that firms up in a "
                "quarter second, then it gives way by 30 degrees and drags."),
         act=("The hold is on: the stopped motor holds the shaft.",
              "Turn the shaft slowly by hand until it gives way, then let go.",
              "A light push back that firms up, then it gives way and drags.",
              "By itself, a second after it gave way and you let go. DONE ends it now."),
         expect="The push back began at the first hall edge, reached its ceiling in about 0.25 s, and gave way at the "
                "second edge, 15 to 30 degrees from where it rested.",
         act_lbl=("L_DEG", "L_HOLD_PCT"), res_lbl=("L_SLIP_DEG", "L_RISE_MS")),
    dict(id="HP_OTHER", name="HELD STOP, THE OTHER WAY", kind="held", powered=False, setup="ST_ARM_HOLD",
         intro=("The held stop again, a new hold. This time turn the shaft the OTHER way from step 1.",
                "Click START STEP, wait for YOUR TURN, then turn the shaft slowly the other way from step 1 until it "
                "gives way. Then let go.",
                "As in step 1: almost nothing for up to 15 degrees, a light push back that firms up, then it gives way."),
         act=("The hold is on: the stopped motor holds the shaft.",
              "Turn the shaft slowly the OTHER way from step 1, until it gives way, then let go.",
              "A light push back that firms up, then it gives way and drags.",
              "By itself, a second after it gave way and you let go. DONE ends it now."),
         expect="As step 1, turned the other way: the push back began at the first edge, rose in about 0.25 s, and "
                "gave way at the second edge.",
         act_lbl=("L_DEG", "L_HOLD_PCT"), res_lbl=("L_SLIP_DEG", "L_RISE_MS")),
    # task 3692, D1a: T0-12's hand-rotation anchor mirrored on the Doco. The motor is UNPOWERED (no driver started), so
    # nothing is felt but the magnets' cogging; the step ends on his DONE. "turn" kind: DONE is his end, nothing to stop.
    dict(id="HT", name="HAND TURN, MOTOR UNPOWERED", kind="turn", powered=False, setup="ST_BLANK",
         intro=("The motor is NOT powered and nothing moves by itself. You turn the shaft by hand while the program "
                "counts the hall ticks and the encoder counts.",
                "Click START STEP, wait for YOUR TURN. Looking at the ENCODER end of the shaft, turn it CLOCKWISE, "
                "about three full turns, steadily, without going back. Then click DONE.",
                "Nothing from the drive. A free shaft with a soft notchy drag from the magnets."),
         act=("The motor is unpowered. The program counts hall ticks and encoder counts as you turn.",
              "Turn the shaft clockwise, looking at the encoder end, about three full turns, steadily. Then click DONE.",
              "A free shaft with a soft notchy drag. Nothing pushes back.",
              "When you click DONE. It ends by itself after two minutes."),
         expect="About 240 hall ticks a turn x10, that is 24 a turn, and about 30 encoder turns x10, that is three turns.",
         begin="START STEP starts the count at once. Then the green YOUR TURN banner.",
         forward="NEXT STEP starts the motor and runs the wiring check: the shaft turns a little one way and back. "
                 "Take your hands off first.",
         act_lbl=("L_HALL_TICKS", "L_ENC_COUNTS"), res_lbl=("L_TPR_X10", "L_TURNS_X10")),
]

# The whole-run screens: (id, name text, banner, card, right button).
SPECIALS = [
    ("SP_STARTING", "STARTING", "B_STARTING",
     [("NOW", "The program reads the board and, when the test needs them, starts the motor under a 2 A test limit "
              "and the encoder. Nothing turns."),
      ("YOU", "Nothing yet. The first step's screen comes next.")], "BT_NONE"),
    ("SP_STOPPED", "RUN STOPPED", "B_STOPPED",
     [("WHAT HAPPENED", "The run stopped itself; the line below says why. The motor and the drive are stopped."),
      ("YOU", "Click FINISH. The log has the details. Repeat the test with the same command once the cause is clear.")],
     "BT_FINISH"),
    ("SP_ALLDONE", "ALL STEPS DONE", "B_ALLDONE",
     [("DONE", "Every step of this test has run. The motor and the drive are stopped."),
      ("YOU", "Click FINISH to close this window. It closes by itself after two minutes.")], "BT_FINISH"),
    # task 3692: shown after the hand turn, while the motor is started and checkWiring() turns the shaft a little
    ("SP_WIRING", "WIRING CHECK", "B_WIRING",
     [("NOW", "The program starts the motor, asks it for a distance, which it must refuse, then turns the shaft a "
              "little, about a quarter turn one way and back."),
      ("YOU", "Take your hands off and keep clear of the shaft until the next screen.")], "BT_NONE"),
]

FORWARD = "NEXT STEP moves on; on the last step FINISH ends the test."


def ids(table):
    return {entry[0]: i for i, entry in enumerate(table)}


BAN = ids(BANNERS)
STAT = ids(STATUSES)
LBL = ids(LABELS)
BTN = ids(BUTTONS)
PH = {name: i for i, name in enumerate(PHASES)}
STEP = {s["id"]: i for i, s in enumerate(STEPS)}
SPEC = ids(SPECIALS)

# Cards (layer 4): per step its INTRO (also its SETUP card), ACT and RESULT, then a SKIP
# where it has one; then the specials'. card_index() is the one place a (step, phase) finds its card.
CARD_TABLE = []
CARD_OF = {}
for _s in STEPS:
    _begin = _s.get("begin", "START STEP sets the step up, hands off, in about a second" +
                    (" and the shaft speeds up." if _s["powered"] else ".") + " Then the green YOUR TURN banner.")
    CARD_OF[(_s["id"], "PH_INTRO")] = len(CARD_TABLE)
    CARD_TABLE.append([("THIS STEP", _s["intro"][0]), ("YOU WILL", _s["intro"][1]),
                       ("YOU SHOULD FEEL", _s["intro"][2]), ("START STEP", _begin)])
    CARD_OF[(_s["id"], "PH_SETUP")] = CARD_OF[(_s["id"], "PH_INTRO")]
    CARD_OF[(_s["id"], "PH_ACT")] = len(CARD_TABLE)
    CARD_TABLE.append(list(zip(("NOW", "YOU", "FEEL", "ENDS"), _s["act"])))
    CARD_OF[(_s["id"], "PH_RESULT")] = len(CARD_TABLE)
    CARD_TABLE.append([("EXPECTED", _s["expect"]),
                       ("NOT MEASURED?", "REDO STEP runs this step again from its setup. Follow the YOU line again."),
                       ("OTHERWISE", _s.get("forward", FORWARD))])
    if "skip" in _s:
        CARD_OF[(_s["id"], "PH_SKIP")] = len(CARD_TABLE)
        CARD_TABLE.append([("WHAT HAPPENED", _s["skip"][0]), ("YOU", _s["skip"][1]), ("THEN", FORWARD)])
SPECIAL_CARD0 = len(CARD_TABLE)
for _sp in SPECIALS:
    CARD_TABLE.append(_sp[3])
CARD_COUNT = len(CARD_TABLE)

# Names layer (layer 2): the step names, the specials' names, then the told supplies (SUPPLY_ROW0 + the row index).
NAMES = [s["name"] for s in STEPS] + [sp[1] for sp in SPECIALS] + SUPPLIES
NAME_SPECIAL0 = len(STEPS)
SUPPLY_ROW0 = len(STEPS) + len(SPECIALS)


def screen_for(step_idx, phase):
    """The one place a step's screen is chosen: (banner, card, label1, label2, left button, right button). None for a
    phase the step does not have."""
    s = STEPS[step_idx]
    key = (s["id"], phase)
    if key not in CARD_OF:
        return None
    card = CARD_OF[key]
    if phase == "PH_INTRO":
        return BAN["B_INTRO"], card, LBL["L_BLANK"], LBL["L_BLANK"], BTN["BT_NONE"], BTN["BT_START"]
    if phase == "PH_SETUP":
        if s["powered"]:
            return BAN["B_SETUP_DRIVE"], card, LBL[s["act_lbl"][0]], LBL[s["act_lbl"][1]], BTN["BT_STOP"], BTN["BT_NONE"]
        return BAN["B_SETUP"], card, LBL["L_BLANK"], LBL["L_BLANK"], BTN["BT_NONE"], BTN["BT_NONE"]
    if phase == "PH_ACT":
        if s["kind"] == "hand":                       # the latch, a sensor, ends it; he may stop the motor
            return BAN["B_TURN_POWERED"], card, LBL[s["act_lbl"][0]], LBL[s["act_lbl"][1]], BTN["BT_STOP"], BTN["BT_NONE"]
        if s["kind"] in ("held", "turn"):             # nothing is driven: DONE is his end, the encoder the sensor's
            return BAN["B_TURN"], card, LBL[s["act_lbl"][0]], LBL[s["act_lbl"][1]], BTN["BT_NONE"], BTN["BT_DONE"]
        raise AssertionError("no step kind %r" % s["kind"])
    if phase == "PH_SKIP":
        return BAN["B_SKIPPED"], card, LBL["L_BLANK"], LBL["L_BLANK"], BTN["BT_NONE"], BTN["BT_NEXT"]
    return BAN["B_RESULT"], card, LBL[s["res_lbl"][0]], LBL[s["res_lbl"][1]], BTN["BT_REDO"], BTN["BT_NEXT"]


def special_for(sp_idx):
    """A whole-run screen: (name, banner, card, left button, right button)."""
    sp = SPECIALS[sp_idx]
    return NAME_SPECIAL0 + sp_idx, BAN[sp[2]], SPECIAL_CARD0 + sp_idx, BTN["BT_NONE"], BTN[sp[4]]


def check_tables():
    """Refuse to write assets whose tables break the panel's rules."""
    for si, s in enumerate(STEPS):
        for p in PHASES:
            scr = screen_for(si, p)
            if scr is None:
                continue
            _, _, _, _, bl, br = scr
            assert BUTTONS[bl][2] in (None, "L") and BUTTONS[br][2] in (None, "R"), (s["id"], p)   # the slot rule
            if p in ("PH_INTRO", "PH_RESULT", "PH_SKIP"):    # cog 0 waits on these alone: a way on
                assert br != BTN["BT_NONE"], (s["id"], p)
            if p in ("PH_SETUP", "PH_ACT") and s["powered"]:           # a driven shaft can always be stopped
                assert bl == BTN["BT_STOP"], (s["id"], p)
            if not s["powered"]:                                         # nothing to stop: no STOP drawn
                assert bl != BTN["BT_STOP"], (s["id"], p)
        assert len(s["intro"]) == 3 and len(s["act"]) == 4, s["id"]
    for sp_idx in range(len(SPECIALS)):
        assert special_for(sp_idx)[3] == BTN["BT_NONE"]
    texts = [t for _, t, _ in BANNERS] + [t for _, t, _ in STATUSES] + [t for _, t in LABELS]
    texts += [t for _, t, _ in BUTTONS] + NAMES + [HEADER_TEXT, FOOTER_TEXT]
    texts += [txt for card in CARD_TABLE for _, txt in card]
    for text in texts:
        assert all(ord(ch) < 128 for ch in text), "non-ASCII panel text: %r" % text
    assert SUP_X + SUP_W <= PANEL_W and NAME_X + NAME_W <= SUP_X, "the step line overruns"
    assert SCOUNT_X + DGT_W <= NAME_X and OF_X < SCOUNT_X and SNUM_X + DGT_W <= OF_X, "the step line's digits overlap"
    assert len(BANNERS) < 256 and len(STATUSES) < 256 and CARD_COUNT < 256 and len(NAMES) < 256


# ---------------------------------------------------------------- layers ----
def build_background():
    img = Image.new("RGB", (PANEL_W, PANEL_H), base.C_PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PANEL_W - 1, HDR_H - 1], fill=base.C_HDR)
    centre(d, (0, 0, PANEL_W, HDR_H), HEADER_TEXT, fit(d, HEADER_TEXT, 17, PANEL_W - 16), base.C_TEXT)
    f = font(18)
    left(d, (STEPLBL_X, STEP_LINE_Y, SNUM_X - STEPLBL_X, NAME_H), "STEP", f, base.C_DIM)
    d.rectangle([SNUM_X, STEP_LINE_Y, SNUM_X + DGT_W - 1, STEP_LINE_Y + DGT_H - 1], fill=base.C_WELL)
    left(d, (OF_X, STEP_LINE_Y, SCOUNT_X - OF_X, NAME_H), "OF", f, base.C_DIM)
    d.rectangle([SCOUNT_X, STEP_LINE_Y, SCOUNT_X + DGT_W - 1, STEP_LINE_Y + DGT_H - 1], fill=base.C_WELL)
    d.rectangle([NAME_X, STEP_LINE_Y, NAME_X + NAME_W - 1, STEP_LINE_Y + NAME_H - 1], fill=base.C_WELL)
    d.rectangle([SUP_X, STEP_LINE_Y, SUP_X + SUP_W - 1, STEP_LINE_Y + NAME_H - 1], fill=base.C_WELL)
    d.rectangle([BAN_X, BAN_Y, BAN_X + BAN_W - 1, BAN_Y + BAN_H - 1], fill=base.C_WELL)
    d.rectangle([CARD_X, CARD_Y, CARD_X + CARD_W - 1, CARD_Y + CARD_H - 1], fill=base.C_WELL)
    left(d, (SEEN_LBL_X, SEEN_Y, SEEN_LBL_W, STAT_H), "SEEN NOW", fit(d, "SEEN NOW", 15, SEEN_LBL_W - 4), base.C_LABEL)
    d.rectangle([STAT_X, SEEN_Y, STAT_X + STAT_W - 1, SEEN_Y + STAT_H - 1], fill=base.C_WELL)
    for y in (READ1_Y, READ2_Y):
        d.rectangle([READ_X, y, READ_X + READ_PITCH * READ_COUNT - 1, y + DGT_H - 1], fill=base.C_WELL)
    d.text((FOOT_X, FOOT_Y), FOOTER_TEXT, font=fit(d, FOOTER_TEXT, 12, FOOT_W), fill=base.C_DIM)
    return img


def build_names():
    img = Image.new("RGB", (NAME_W, NAME_H * len(NAMES)), base.C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(NAMES):
        if i >= SUPPLY_ROW0:                          # a supply: drawn to SUP_W, the width it is blitted at
            left(d, (0, i * NAME_H, SUP_W, NAME_H), text, fit(d, text, 18, SUP_W - 12), base.C_AMBER, pad=6)
        else:
            left(d, (0, i * NAME_H, NAME_W, NAME_H), text, fit(d, text, 18, NAME_W - 12), base.C_AMBER, pad=6)
    return img


def build_banners():
    img = Image.new("RGB", (BAN_W, BAN_H * len(BANNERS)), base.C_WELL)
    d = ImageDraw.Draw(img)
    for i, (_, text, fill) in enumerate(BANNERS):
        d.rectangle([0, i * BAN_H, BAN_W - 1, i * BAN_H + BAN_H - 1], fill=fill)
        centre(d, (0, i * BAN_H, BAN_W, BAN_H), text, fit(d, text, 17, BAN_W - 16), base.C_TEXT)
    return img


def build_cards():
    img = Image.new("RGB", (CARD_W, CARD_H * CARD_COUNT), base.C_WELL)
    d = ImageDraw.Draw(img)
    for i, fields in enumerate(CARD_TABLE):
        base.draw_card(d, i * CARD_H, fields)
    return img


def build_statuses():
    img = Image.new("RGB", (STAT_W, STAT_H * len(STATUSES)), base.C_WELL)
    d = ImageDraw.Draw(img)
    ink = {"wait": base.C_TEXT, "good": base.C_GOOD, "warn": base.C_WARN}
    for i, (_, text, kind) in enumerate(STATUSES):
        if text:
            left(d, (0, i * STAT_H, STAT_W, STAT_H), text, fit(d, text, 15, STAT_W - 12), ink[kind], pad=6)
    return img


def build_labels():
    img = Image.new("RGB", (LBL_W, LBL_H * len(LABELS)), base.C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (_, text) in enumerate(LABELS):
        if text:
            left(d, (0, i * LBL_H, LBL_W, LBL_H), text, fit(d, text, 16, LBL_W - 8), base.C_DIM)
    return img


def draw_button(d, x, y, title, hilite):
    if title == "":
        d.rectangle([x, y, x + BTN_W - 1, y + BTN_H - 1], fill=base.C_PANEL)   # BT_NONE: the bare panel
        return
    d.rectangle([x, y, x + BTN_W - 1, y + BTN_H - 1], fill=base.C_BTN_HI if hilite else base.C_BTN, outline=base.C_FRAME)
    centre(d, (x, y, BTN_W, BTN_H), title, fit(d, title, 19, BTN_W - 12), (20, 20, 20) if hilite else base.C_TEXT)


def build_buttons():
    img = Image.new("RGB", (BTN_W * 2, BTN_H * len(BUTTONS)), base.C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (_, title, _) in enumerate(BUTTONS):
        draw_button(d, 0, i * BTN_H, title, False)
        draw_button(d, BTN_W, i * BTN_H, title, True)
    return img


ASSETS = [
    ("sg_bg.bmp", build_background),        # layer 1
    ("sg_names.bmp", build_names),          # layer 2
    ("sg_banners.bmp", build_banners),      # layer 3
    ("sg_cards.bmp", build_cards),          # layer 4
    ("sg_digits.bmp", base.build_digits),   # layer 5: T0-24's own digit strip, drawn by its function
    ("sg_status.bmp", build_statuses),      # layer 6
    ("sg_labels.bmp", build_labels),        # layer 7
    ("sg_buttons.bmp", build_buttons),      # layer 8
]


# ---------------------------------------------------------------- spin2 -----
def con_block():
    lines = ["CON { the hand tests' panel -- GENERATED by tools/gen_single_assets.py, do not hand-edit }", "",
             "' Layers: 1 background, 2 step names / whole-run names / told supplies, 3 banners, 4 cards, 5 digits,",
             "' 6 status phrases, 7 reading labels, 8 buttons. A DEBUG backtick command takes the layer as a literal, so",
             "' the layer numbers live in sgSetupPanel() / sgDraw() and here only as this comment.", ""]
    geo = [("SG_STEP_COUNT", len(STEPS)), ("SG_PHASE_COUNT", len(PHASES)),
           ("SG_SNUM_X", SNUM_X), ("SG_SCOUNT_X", SCOUNT_X), ("SG_STEP_LINE_Y", STEP_LINE_Y),
           ("SG_NAME_X", NAME_X), ("SG_NAME_W", NAME_W), ("SG_NAME_H", NAME_H), ("SG_SUP_X", SUP_X), ("SG_SUP_W", SUP_W),
           ("SG_NAME_SPECIAL0", NAME_SPECIAL0), ("SG_SUPPLY_ROW0", SUPPLY_ROW0),
           ("SG_BAN_X", BAN_X), ("SG_BAN_Y", BAN_Y), ("SG_BAN_W", BAN_W), ("SG_BAN_H", BAN_H),
           ("SG_CARD_X", CARD_X), ("SG_CARD_Y", CARD_Y), ("SG_CARD_W", CARD_W), ("SG_CARD_H", CARD_H),
           ("SG_STAT_X", STAT_X), ("SG_STAT_Y", SEEN_Y), ("SG_STAT_W", STAT_W), ("SG_STAT_H", STAT_H),
           ("SG_LBL_X", LBL_X), ("SG_LBL_W", LBL_W), ("SG_LBL_H", LBL_H),
           ("SG_READ1_Y", READ1_Y), ("SG_READ2_Y", READ2_Y), ("SG_READ_X", READ_X),
           ("SG_READ_PITCH", READ_PITCH), ("SG_READ_COUNT", READ_COUNT),
           ("SG_DGT_W", DGT_W), ("SG_DGT_H", DGT_H), ("SG_DGT_BLANK", DGT_BLANK),
           ("SG_BTN_W", BTN_W), ("SG_BTN_H", BTN_H), ("SG_BTN_L_X", BTN_L_X), ("SG_BTN_R_X", BTN_R_X),
           ("SG_BTN_Y", BTN_Y),
           ("SG_SCREEN_BYTES", 6), ("SG_SCR_BANNER", 0), ("SG_SCR_CARD", 1), ("SG_SCR_LBL1", 2),
           ("SG_SCR_LBL2", 3), ("SG_SCR_BTN_L", 4), ("SG_SCR_BTN_R", 5),
           ("SG_SPECIAL_BYTES", 5), ("SG_SPC_NAME", 0), ("SG_SPC_BANNER", 1), ("SG_SPC_CARD", 2),
           ("SG_SPC_BTN_L", 3), ("SG_SPC_BTN_R", 4)]
    lines += ["    %-24s = %d" % (n, v) for n, v in geo]
    for title, table in (("steps, in sgScreenTab order", [("STEP_" + s["id"],) for s in STEPS]),
                         ("phases", [(p,) for p in PHASES]), ("whole-run screens", SPECIALS), ("banners", BANNERS),
                         ("status phrases", STATUSES), ("reading labels", LABELS), ("buttons", BUTTONS)):
        lines += ["", "' %s" % title]
        lines += ["    %-24s = %d" % ("SG_" + entry[0], i) for i, entry in enumerate(table)]
    return "\n".join(lines)


def dat_block():
    lines = ["DAT { the hand tests' screen table -- GENERATED by tools/gen_single_assets.py, do not hand-edit }", "",
             "' One entry per (step, phase), step-major in SG_STEP_* order then SG_PH_* order, SG_SCREEN_BYTES bytes each",
             "' (SG_SCR_*): banner, card, reading label 1, reading label 2, left button, right button. A phase a step does",
             "' not have is all zeros, and is never shown. The generator's --storyboard renders these same entries.",
             "sgScreenTab"]
    for si, s in enumerate(STEPS):
        for p in PHASES:
            scr = screen_for(si, p)
            vals = scr if scr is not None else (0, 0, 0, 0, 0, 0)
            lines.append("    BYTE    %s   ' %s %s%s" % (", ".join("%2d" % v for v in vals), s["id"], p,
                                                         "" if scr is not None else " (none)"))
    lines += ["", "' One entry per whole-run screen (SG_SP_*), SG_SPECIAL_BYTES bytes each (SG_SPC_*): name, banner, card,",
              "' left button, right button.",
              "sgSpecialTab"]
    for spi, sp in enumerate(SPECIALS):
        lines.append("    BYTE    %s   ' %s" % (", ".join("%2d" % v for v in special_for(spi)), sp[0]))
    return "\n".join(lines)


# ---------------------------------------------------------------- storyboard
def compose(layers, step_name_row, seq_num, step_count, supply_row, banner, card, stat, lbl1, lbl2, r1, r2, btn_l,
            btn_r, hilite=None):
    """Compose one frame exactly as sgDraw() blits it (same pieces, same places)."""
    bg, names, bans, crds, dgts, stats, lbls, btns = layers
    img = bg.copy()
    for x, num in ((SNUM_X, seq_num), (SCOUNT_X, step_count)):
        cell = num if num > 0 else DGT_BLANK
        img.paste(dgts.crop((cell * DGT_W, 0, cell * DGT_W + DGT_W, DGT_H)), (x, STEP_LINE_Y))
    img.paste(names.crop((0, step_name_row * NAME_H, NAME_W, step_name_row * NAME_H + NAME_H)), (NAME_X, STEP_LINE_Y))
    img.paste(names.crop((0, supply_row * NAME_H, SUP_W, supply_row * NAME_H + NAME_H)), (SUP_X, STEP_LINE_Y))
    img.paste(bans.crop((0, banner * BAN_H, BAN_W, banner * BAN_H + BAN_H)), (BAN_X, BAN_Y))
    img.paste(crds.crop((0, card * CARD_H, CARD_W, card * CARD_H + CARD_H)), (CARD_X, CARD_Y))
    img.paste(stats.crop((0, stat * STAT_H, STAT_W, stat * STAT_H + STAT_H)), (STAT_X, SEEN_Y))
    for y, lbl, val in ((READ1_Y, lbl1, r1), (READ2_Y, lbl2, r2)):
        img.paste(lbls.crop((0, lbl * LBL_H, LBL_W, lbl * LBL_H + LBL_H)), (LBL_X, y))
        digits = "" if val is None else str(val)
        cells = [DGT_BLANK] * (READ_COUNT - len(digits)) + [int(c) for c in digits]
        for col, cell in enumerate(cells):
            img.paste(dgts.crop((cell * DGT_W, 0, cell * DGT_W + DGT_W, DGT_H)), (READ_X + col * READ_PITCH, y))
    for x, b in ((BTN_L_X, btn_l), (BTN_R_X, btn_r)):
        col = BTN_W if (hilite == b and b != BTN["BT_NONE"]) else 0
        img.paste(btns.crop((col, b * BTN_H, col + BTN_W, b * BTN_H + BTN_H)), (x, BTN_Y))
    return img


# Each tier's steps, in the order the harness runs them (test_bench_single.spin2 legSteps()), and its row index.
TIERS = [
    ("single-handload-v12p0", 2, ["HL_4A", "HL_2A", "HL_DEF"]),
    ("single-handload-v24p0", 6, ["HL_4A", "HL_2A"]),
    ("single-heldpush-v12p0", 2, ["HP_ONE", "HP_OTHER"]),
    ("single-recheck-v12p0", 2, ["HT"]),                        # task 3692: the hand turn, then the wiring screen
]
# The live phrases a normal step passes through (storyboard only; the measure cog publishes them), its RESULT phrase,
# and sample readings (ACT, RESULT).
WALK = {
    "hand": (["ST_SPEEDING"], ["ST_GRIP_NOW", "ST_SLOWING", "ST_STANDING", "ST_LATCHED"], "ST_MEASURED", (207, 412), (1012, 790)),
    "held": (["ST_ARM_HOLD"], ["ST_TURN_NOW", "ST_TURNED_FREE", "ST_PUSHING", "ST_AT_CEIL", "ST_GAVE_WAY"], "ST_MEASURED",
             (19, 100), (24, 251)),
    "turn": (["ST_BLANK"], ["ST_HT_WAIT", "ST_HT_TURNING", "ST_HT_ENOUGH"], "ST_MEASURED", (72, 4320), (240, 30)),
}


def storyboard(out_dir, layers):
    """Every screen each tier shows on a normal run, in order, one PNG each -- for the desk walk -- then the screens a
    run shows when something goes other than planned."""
    os.makedirs(out_dir, exist_ok=True)
    n = 0

    def save(img, tag):
        nonlocal n
        n += 1
        img.save(os.path.join(out_dir, "%03d_%s.png" % (n, tag)))

    for tier, row, steps in TIERS:
        name, ban, card, bl, br = special_for(SPEC["SP_STARTING"])
        save(compose(layers, name, 0, 0, SUPPLY_ROW0 + row, ban, card, STAT["ST_STARTING"], LBL["L_BLANK"],
                     LBL["L_BLANK"], None, None, bl, br), tier + "_starting")
        for k, sid in enumerate(steps):
            si = STEP[sid]
            s = STEPS[si]
            setup, act, res, act_r, res_r = WALK[s["kind"]]
            seq = (("PH_INTRO", "ST_WAIT_START", None),) + tuple(("PH_SETUP", st, None) for st in setup)
            seq += tuple(("PH_ACT", st, act_r) for st in act)
            seq += (("PH_RESULT", res, res_r),)
            for p, st, rd in seq:
                ban, cd, l1, l2, bl, br = screen_for(si, p)
                if p == "PH_RESULT" and k == len(steps) - 1 and s["kind"] != "turn":
                    br = BTN["BT_FINISH"]             # the harness's rule: the last step's forward button is FINISH
                    #  (the hand turn is never the test's last: the wiring check follows, so it keeps NEXT STEP)
                v1, v2 = (rd if rd is not None else (None, None))
                save(compose(layers, si, k + 1, len(steps), SUPPLY_ROW0 + row, ban, cd, STAT[st], l1, l2, v1, v2, bl, br),
                     "%s_step%d_%s_%s" % (tier, k + 1, p[3:].lower(), st[3:].lower()))
            if s["kind"] == "turn":                   # then the wiring check's own screen, until the run ends
                name, ban, card, bl, br = special_for(SPEC["SP_WIRING"])
                save(compose(layers, name, 0, 0, SUPPLY_ROW0 + row, ban, card, STAT["ST_WIRING"], LBL["L_BLANK"],
                             LBL["L_BLANK"], None, None, bl, br), tier + "_wiring")
        name, ban, card, bl, br = special_for(SPEC["SP_ALLDONE"])
        save(compose(layers, name, 0, 0, SUPPLY_ROW0 + row, ban, card, STAT["ST_ALL_DONE"], LBL["L_BLANK"],
                     LBL["L_BLANK"], None, None, bl, br), tier + "_alldone")
    # other than planned: a step not measured, the default step not run, the same way twice, a click lit, the run stopped
    alt = [("HL_4A", 1, 2, "PH_RESULT", "ST_NM_NO_STAND", None), ("HL_DEF", 3, 3, "PH_SKIP", "ST_DEF_SKIPPED", None),
           ("HP_OTHER", 2, 2, "PH_RESULT", "ST_SAME_WAY", None), ("HP_ONE", 1, 2, "PH_RESULT", "ST_RISE_TOO_FAST", None),
           ("HL_2A", 2, 3, "PH_ACT", "ST_NOLATCH", BTN["BT_STOP"]),
           ("HT", 1, 1, "PH_RESULT", "ST_NM_FEW_TURNS", None), ("HT", 1, 1, "PH_RESULT", "ST_NM_TOO_FAST", None),
           ("HT", 1, 1, "PH_ACT", "ST_HT_ENOUGH", BTN["BT_DONE"])]
    for sid, seq_num, count, p, st, lit in alt:
        si = STEP[sid]
        ban, cd, l1, l2, bl, br = screen_for(si, p)
        save(compose(layers, si, seq_num, count, SUPPLY_ROW0 + 2, ban, cd, STAT[st], l1, l2, None, None, bl, br,
                     hilite=lit), "alt_%s_%s_%s" % (sid.lower(), p[3:].lower(), st[3:].lower()))
    name, ban, card, bl, br = special_for(SPEC["SP_STOPPED"])
    save(compose(layers, name, 0, 0, SUPPLY_ROW0 + 2, ban, card, STAT["ST_RS_OVERCURRENT"], LBL["L_BLANK"],
                 LBL["L_BLANK"], None, None, bl, br), "alt_run_stopped")
    sys.stderr.write("storyboard: %d screens in %s\n" % (n, out_dir))


def main():
    check_tables()
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(os.path.dirname(here), "src")
    preview = "--preview" in sys.argv
    layers = []
    for name, build in ASSETS:
        img = build()
        layers.append(img)
        path = os.path.join(out, name)
        img.save(path)
        sys.stderr.write("wrote %s  %dx%d\n" % (path, img.size[0], img.size[1]))
        if preview:
            img.save(path.replace(".bmp", ".png"))
    if "--storyboard" in sys.argv:
        storyboard(sys.argv[sys.argv.index("--storyboard") + 1], layers)
    print(con_block())
    print()
    print(dat_block())


if __name__ == "__main__":
    main()
