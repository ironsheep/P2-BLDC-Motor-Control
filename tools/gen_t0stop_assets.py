#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for src/test_bench_t0.spin2's T0-24 stop-state hand test
(-D T0_STOPMODE, bench-run.sh tiers t0-stopmode and t0-stopmode-fltfirst).

Same technique, and the same single-source-of-truth discipline, as tools/gen_t0hand_assets.py and
tools/gen_dual_assets.py: layers are loaded once with LAYER, a frame is composed by blitting opaque
cells with CROP and then one UPDATE, and every number and every screen choice lives here. This script
draws the BMPs, and prints the Spin2 CON block (geometry and ids) and the DAT screen table the harness
composes each screen from.

    python3 tools/gen_t0stop_assets.py                      # write src/t0s_*.bmp, print CON + DAT
    python3 tools/gen_t0stop_assets.py --preview            # also write a PNG of each layer
    python3 tools/gen_t0stop_assets.py --storyboard DIR     # also render every screen, in order, to DIR

REBUILT task 3619 (PL-127, DOCs/plans/T0-24-INTERACTION-DESIGN.md). The panel is a lesson. Every
screen answers, in fixed places, which wheel and row, what the program is doing now, the one thing the
operator does, what they should feel, and what ends the step. A row is previewed before it starts. It
ends on a RESULT screen that waits for NEXT ROW or REDO ROW. Only live buttons are drawn: the forward
action is always the RIGHT slot, and ABORT or REDO is always the LEFT.

THE SCREEN TABLE IS THE CONTRACT. For each row and phase, SCREENS below names the banner, the card, the
two reading labels and the two buttons. The harness reads the same table (printed as DAT t0sScreenTab),
and --storyboard renders it. So the screens reviewed at the desk are the screens the harness draws.

DEBUG LAYER requires 24-bit uncompressed (BI_RGB) BMP with no alpha, which is exactly what Pillow
writes for an "RGB" image saved as .bmp. Sprite cells are OPAQUE, so every cell carries the colour of
the region it lands on.
"""

import functools
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- layout ----
PANEL_W, PANEL_H = 560, 470                    # also the literal SIZE in t0sSetupPanel()'s PLOT create: keep equal

HDR_H = 28
ROWLBL_X, ROW_LINE_Y = 12, 34                  # "ROW" (background), then the digit, then "OF 8"
RNUM_X = 64
OF_X = 96
NAME_X, NAME_W, NAME_H = 148, 400, 36
BAN_X, BAN_Y, BAN_W, BAN_H = 12, 76, 536, 30
CARD_X, CARD_Y, CARD_W, CARD_H = 12, 112, 536, 150
SEEN_LBL_X, SEEN_Y, SEEN_LBL_W = 12, 268, 92
STAT_X, STAT_W, STAT_H = 108, 440, 26
LBL_X, LBL_W, LBL_H = 12, 250, 36
READ1_Y, READ2_Y = 302, 344
READ_X, READ_PITCH, READ_COUNT = 270, 30, 5
DGT_W, DGT_H = 28, 36
DGT_BLANK = 10
BTN_W, BTN_H = 200, 40
BTN_L_X, BTN_R_X, BTN_Y = 40, 320, 392
FOOT_X, FOOT_Y, FOOT_W, FOOT_H = 12, 446, 536, 18

ROW_COUNT = 8

# The wheel T0_MOTOR_BASE drives: the right board is at P16 (STEPHEN 2026-09-11).
HEADER_TEXT = "T0-24 STOP-STATE HAND TEST  --  RIGHT WHEEL (P16 BOARD)"
FOOTER_TEXT = "PANIC: PULL THE PACK.   CLICK THE WINDOW FIRST.   ENTER = RIGHT BUTTON,  ESC = LEFT BUTTON."

# ---------------------------------------------------------------- ids -------
# Phase banners (layer 3). Each is (id, text, fill colour).
BANNERS = [
    ("B_INTRO", "READ THIS ROW, THEN CLICK START ROW", (70, 76, 86)),
    ("B_SETUP", "HANDS OFF  --  SETTING UP", (150, 104, 20)),
    ("B_TURN", "YOUR TURN", (34, 120, 60)),
    ("B_POWERED", "HANDS OFF  --  THE WHEEL IS POWERED", (160, 40, 36)),
    ("B_RESULT", "RESULT  --  READ IT, THEN CHOOSE A BUTTON", (36, 84, 150)),
    ("B_ALLDONE", "ALL ROWS DONE", (70, 76, 86)),
    ("B_NOTREADY", "THE DRIVER DID NOT START", (160, 40, 36)),
]

# Status phrases shown under SEEN NOW (layer 6). Each is (id, text, kind): kind picks the ink --
# "wait" neutral, "good" green (the program has what it needs), "warn" amber (not measured, redo).
STATUSES = [
    ("ST_BLANK", "", "wait"),
    ("ST_WAIT_START", "WAITING FOR YOU TO CLICK START ROW", "wait"),
    ("ST_ARM_HOLD", "ARMING THE HOLD", "wait"),
    ("ST_ARM_WEAK", "ARMING A WEAK HOLD", "wait"),
    ("ST_SET_COAST", "SETTING COAST MODE", "wait"),
    ("ST_STOP_DRIVER", "STOPPING THE DRIVER", "wait"),
    ("ST_PREP_FAULT", "PREPARING  --  HANDS OFF", "wait"),
    ("ST_WAIT_PUSH", "WAITING FOR YOUR PUSH", "wait"),
    ("ST_PUSH_RISING", "PUSH SEEN  --  HOLD RISING", "wait"),
    ("ST_PUSH_SEEN", "PUSH SEEN", "wait"),
    ("ST_CEIL_GOT", "AT THE CEILING  --  GOT IT, LET GO AND CLICK DONE", "good"),
    ("ST_CEIL_KEEP", "AT THE CEILING  --  KEEP HOLDING IT", "wait"),
    ("ST_SLIP_GOT", "IT GAVE WAY (SLIPPED)  --  GOT IT, CLICK DONE", "good"),
    ("ST_SLIP_BAD", "IT SLIPPED  --  NOT EXPECTED, CLICK DONE", "warn"),
    ("ST_LIMIT_GOT", "IT LET GO (LIMITED)  --  GOT IT, CLICK DONE", "good"),
    ("ST_LIMIT_BAD", "IT LET GO (LIMITED)  --  NOT EXPECTED, CLICK DONE", "warn"),
    ("ST_HOLD_FAULT", "THE DRIVER FAULTED  --  CLICK DONE", "warn"),
    ("ST_WAIT_SPIN", "WAITING FOR YOUR SPIN", "wait"),
    ("ST_SPIN_SLOW", "SPINNING  --  NOT FAST ENOUGH YET", "wait"),
    ("ST_SPIN_FAST", "FAST ENOUGH  --  LET GO", "wait"),
    ("ST_SLOWING", "SLOWING  --  MEASURING", "wait"),
    ("ST_ESTOP_ON", "E-STOP APPLIED", "wait"),
    ("ST_STOP_GOT", "STOPPED  --  GOT IT, CLICK DONE", "good"),
    ("ST_STOP_SLOW", "STOPPED  --  TOO SLOW, SPIN AGAIN HARDER", "warn"),
    ("ST_STOP_KEPT", "TOO SLOW  --  EARLIER READING KEPT, CLICK DONE", "good"),
    ("ST_STOP_AGAIN", "STOPPED  --  NOT MEASURED, SPIN IT AGAIN", "warn"),
    ("ST_SPINUP", "SPINNING UP", "wait"),
    ("ST_AT_SPEED", "AT SPEED  --  THE FAULT IS COMING", "wait"),
    ("ST_FAULTED", "FAULT FORCED  --  WATCH IT STOP", "wait"),
    ("ST_MEASURED", "MEASURED", "good"),
    ("ST_NM_NO_PUSH", "NOT MEASURED  --  NO PUSH SEEN", "warn"),
    ("ST_NM_NOT_FRESH", "NOT MEASURED  --  THE HOLD WAS NOT FRESH", "warn"),
    ("ST_NM_NO_SPIN", "NOT MEASURED  --  NO SPIN WAS FAST ENOUGH", "warn"),
    ("ST_NM_NO_ESTOP", "NOT MEASURED  --  THE E-STOP WAS NOT APPLIED", "warn"),
    ("ST_NM_ABORTED", "NOT MEASURED  --  YOU ABORTED IT", "warn"),
    ("ST_NM_NO_SPEED", "NOT MEASURED  --  IT NEVER REACHED SPEED", "warn"),
    ("ST_NM_NO_FAULT", "NOT MEASURED  --  THE FAULT DID NOT HAPPEN", "warn"),
    ("ST_NM_SETUP", "NOT MEASURED  --  THE SETUP FAILED", "warn"),
    ("ST_NM_10A", "STOPPED AT THE 10 A LIMIT  --  NOT MEASURED", "warn"),
    ("ST_CELLS_LOGGED", "THE CELLS ARE IN THE LOG", "good"),
    ("ST_NOT_READY", "THE DRIVER DID NOT START  --  NOTHING RAN", "warn"),
]

# Reading labels (layer 7).
LABELS = [
    ("L_BLANK", ""),
    ("L_HOLD_PCT", "HOLD  (% OF CEILING)"),
    ("L_PUSHED", "PUSHED BY  (TICKS)"),
    ("L_MS_CEIL", "MS TO CEILING"),
    ("L_MS_SLIP", "MS TO SLIP"),
    ("L_MS_LIMIT", "MS TO LET GO"),
    ("L_SPEED", "SPEED  (TICKS/S)"),
    ("L_TICKS", "HALL TICKS"),
    ("L_BAND_TICKS", "BAND TICKS"),
    ("L_BAND_MS", "BAND MS"),
]

# Buttons (layer 8). Each is (id, title, key, slot): the forward action is always RIGHT, the other LEFT.
BUTTONS = [
    ("BT_NONE", "", "", None),
    ("BT_START", "START ROW", "ENTER", "R"),
    ("BT_DONE", "DONE", "ENTER", "R"),
    ("BT_NEXT", "NEXT ROW", "ENTER", "R"),
    ("BT_FINISH", "FINISH", "ENTER", "R"),
    ("BT_ABORT", "ABORT", "ESC", "L"),
    ("BT_REDO", "REDO ROW", "ESC", "L"),
]

PHASES = ["PH_INTRO", "PH_SETUP", "PH_ACT", "PH_RESULT"]

# ---------------------------------------------------------------- the rows --
# Semantic row ids, in T0_24_ROW_* order (execution order can differ: -D T0_24_FLT_FIRST). Each row:
#   name   -- the row line's text
#   kind   -- "hold" (he pushes), "spin" (he spins), "power" (the program drives; hands off)
#   setup  -- the SETUP phase's status phrase
#   intro  -- THIS ROW / YOU WILL / YOU SHOULD FEEL (the preview, before START ROW)
#   act    -- NOW / YOU / FEEL / ENDS
#   expect -- the RESULT screen's EXPECTED line
#   act_lbl, res_lbl -- the two reading labels during ACT and on RESULT
#   walk   -- the SEEN NOW phrases a normal run passes through (storyboard only)
SPIN_ENDS = "When it has stopped, click DONE. Too slow? Spin it again, as often as you like."
ROWS = [
    dict(id="HOLDRISE", name="HOLD-RISE", kind="hold", setup="ST_ARM_HOLD",
         intro=("The driver holds the stopped wheel in place. You check the hold gets stronger when you push.",
                "Push the right wheel a little and keep pushing, then let go.",
                "The resistance grows over about a quarter second, then stays firm."),
         act=("The hold is ON.",
              "Push the right wheel a little by hand and keep pushing.",
              "The resistance grows over about a quarter second, then stays firm.",
              "When you have felt it, let go and click DONE."),
         expect="The hold reaches its ceiling within 0.4 s of your push, and never slips.",
         act_lbl=("L_HOLD_PCT", "L_PUSHED"), res_lbl=("L_MS_CEIL", "L_PUSHED"),
         walk=["ST_WAIT_PUSH", "ST_PUSH_RISING", "ST_CEIL_GOT"]),
    dict(id="HOLDSLIP", name="HOLD-SLIP", kind="hold", setup="ST_ARM_WEAK",
         intro=("The hold is set weak on purpose. You check it gives way and hands over to the brake.",
                "Turn the right wheel firmly by hand, about a quarter turn.",
                "It gives way almost at once, then drags against your turn."),
         act=("A weak hold is ON.",
              "Turn the right wheel firmly by hand, about a quarter turn.",
              "It gives way almost at once, then drags against your turn.",
              "When it has given way, click DONE."),
         expect="The hold gives way (SLIPPED) before any fault.",
         act_lbl=("L_HOLD_PCT", "L_PUSHED"), res_lbl=("L_MS_SLIP", "L_PUSHED"),
         walk=["ST_WAIT_PUSH", "ST_PUSH_SEEN", "ST_SLIP_GOT"]),
    dict(id="HOLDLIMIT", name="HOLD-LIMIT", kind="hold", setup="ST_ARM_HOLD",
         intro=("You push steadily at the hold's limit. You check it lets go after about 2 s at the ceiling.",
                "Push the right wheel and hold it steady for about 3 seconds.",
                "It holds firm, then lets go."),
         act=("The hold is ON, with a 2 s limit at its ceiling.",
              "Push the right wheel and hold it steady against the hold.",
              "It holds firm, then lets go after about 2 s.",
              "When it has let go, click DONE."),
         expect="The hold lets go (LIMITED) while you keep it at the ceiling.",
         act_lbl=("L_HOLD_PCT", "L_PUSHED"), res_lbl=("L_MS_LIMIT", "L_PUSHED"),
         walk=["ST_WAIT_PUSH", "ST_PUSH_RISING", "ST_CEIL_KEEP", "ST_LIMIT_GOT"]),
    dict(id="COAST", name="COAST AT REST", kind="spin", setup="ST_SET_COAST",
         intro=("The stopped wheel is set to coast. You check it spins freely.",
                "Spin the right wheel hard by hand and let go.",
                "It spins freely and coasts to a stop."),
         act=("Coast mode is set.",
              "Spin the right wheel hard by hand and let go. Hands off after.",
              "It spins freely and coasts to a stop.",
              SPIN_ENDS),
         expect="A coast: 7 or more ticks from the measuring speed (120 ticks/s) to rest.",
         act_lbl=("L_SPEED", "L_TICKS"), res_lbl=("L_BAND_TICKS", "L_BAND_MS"),
         walk=["ST_WAIT_SPIN", "ST_SPIN_FAST", "ST_SLOWING", "ST_STOP_GOT"]),
    dict(id="ESTOP", name="E-STOP AS IT COASTS", kind="spin", setup="ST_SET_COAST",
         intro=("You check the e-stop brakes the wheel hard. The program applies it as the wheel slows.",
                "Spin the right wheel hard by hand and let go.",
                "It starts to coast, then stops abruptly."),
         act=("Coast mode is set. The program applies the e-stop as the wheel slows.",
              "Spin the right wheel hard by hand and let go. Hands off after.",
              "It starts to coast, then stops abruptly.",
              SPIN_ENDS),
         expect="A short: 4 or fewer ticks from the measuring speed (120 ticks/s) to rest.",
         act_lbl=("L_SPEED", "L_TICKS"), res_lbl=("L_BAND_TICKS", "L_BAND_MS"),
         walk=["ST_WAIT_SPIN", "ST_SPIN_FAST", "ST_ESTOP_ON", "ST_STOP_GOT"]),
    dict(id="FLTCOAST", name="FAULT, COAST MODE", kind="power", setup="ST_PREP_FAULT",
         intro=("The program spins the right wheel under power, then faults it on purpose, in coast mode.",
                "Nothing: keep your hands off and watch the wheel. ABORT stops it at once.",
                "After the fault it coasts to a stop."),
         act=("Driving the right wheel, then faulting it on purpose.",
              "Hands off. Watch the wheel.",
              "After the fault it coasts to a stop.",
              "By itself, when the wheel stops. ABORT stops the wheel now."),
         expect="A coast: 7 or more ticks from the measuring speed, and the driver still faulted.",
         act_lbl=("L_SPEED", "L_TICKS"), res_lbl=("L_BAND_TICKS", "L_BAND_MS"),
         walk=["ST_SPINUP", "ST_AT_SPEED", "ST_FAULTED"]),
    dict(id="FLTHOLD", name="FAULT, BRAKE MODE", kind="power", setup="ST_PREP_FAULT",
         intro=("The program spins the right wheel under power, then faults it on purpose, in brake mode.",
                "Nothing: keep your hands off and watch the wheel. ABORT stops it at once.",
                "After the fault it stops almost at once."),
         act=("Driving the right wheel, then faulting it on purpose.",
              "Hands off. Watch the wheel.",
              "After the fault it stops almost at once.",
              "By itself, when the wheel stops. ABORT stops the wheel now."),
         expect="A short: 4 or fewer ticks from the measuring speed, and the driver still faulted.",
         act_lbl=("L_SPEED", "L_TICKS"), res_lbl=("L_BAND_TICKS", "L_BAND_MS"),
         walk=["ST_SPINUP", "ST_AT_SPEED", "ST_FAULTED"]),
    dict(id="COGSTOP", name="DRIVER COG STOPPED", kind="spin", setup="ST_STOP_DRIVER",
         intro=("The driver is stopped and the pins are released: the free reference every coast is compared with.",
                "Spin the right wheel hard by hand and let go.",
                "It coasts to a stop, just as in the COAST AT REST row."),
         act=("The driver is stopped; the pins are released.",
              "Spin the right wheel hard by hand and let go. Hands off after.",
              "It coasts to a stop, just as in the COAST AT REST row.",
              SPIN_ENDS),
         expect="A coast: 7 or more ticks from the measuring speed, as in the COAST AT REST row.",
         act_lbl=("L_SPEED", "L_TICKS"), res_lbl=("L_BAND_TICKS", "L_BAND_MS"),
         walk=["ST_WAIT_SPIN", "ST_SPIN_FAST", "ST_SLOWING", "ST_STOP_GOT"]),
]
assert len(ROWS) == ROW_COUNT

# Cards (layer 4): three per row, in row order -- INTRO, ACT, RESULT -- then the two whole-test cards.
CARD_INTRO, CARD_ACT, CARD_RESULT, CARDS_PER_ROW = 0, 1, 2, 3
CARD_NOTREADY = ROW_COUNT * CARDS_PER_ROW
CARD_ALLDONE = CARD_NOTREADY + 1
CARD_COUNT = CARD_ALLDONE + 1


def cards():
    # The INTRO card is also the SETUP screen's card, so its last line must read true both before and
    # just after START ROW (desk walk, 2026-09-24).
    out = []
    for r in ROWS:
        if r["kind"] == "power":
            begin = "START ROW prepares the row, then the wheel spins under power. Hands off throughout."
        else:
            begin = "START ROW sets the row up in about a second, hands off. Then the green YOUR TURN banner."
        out.append([("THIS ROW", r["intro"][0]), ("YOU WILL", r["intro"][1]),
                    ("YOU SHOULD FEEL", r["intro"][2]), ("START ROW", begin)])
        out.append(list(zip(("NOW", "YOU", "FEEL", "ENDS"), r["act"])))
        forward = "FINISH ends the test." if r["id"] == "COGSTOP" else "NEXT ROW moves on."
        out.append([("EXPECTED", r["expect"]),
                    ("NOT MEASURED?", "REDO ROW runs this row again from its setup. Follow the YOU line again."),
                    ("OTHERWISE", forward)])
    out.append([("WHAT HAPPENED", "The driver did not come up ready, so no row can run."),
                ("YOU", "Nothing more at the rig. The log says why.")])
    out.append([("DONE", "All eight rows are done."),
                ("YOU", "Nothing more at the rig. The ten cells are in the log.")])
    assert len(out) == CARD_COUNT
    return out


def ids(table):
    return {entry[0]: i for i, entry in enumerate(table)}


BAN = ids(BANNERS)
STAT = ids(STATUSES)
LBL = ids(LABELS)
BTN = ids(BUTTONS)
PH = {name: i for i, name in enumerate(PHASES)}


def screen_for(row_idx, phase):
    """The one place a screen's pieces are chosen: (banner, card, label1, label2, left button, right button)."""
    r = ROWS[row_idx]
    base = row_idx * CARDS_PER_ROW
    last = (r["id"] == "COGSTOP")                     # always the last row run (T0-24's own rule)
    if phase == "PH_INTRO":
        return BAN["B_INTRO"], base + CARD_INTRO, LBL["L_BLANK"], LBL["L_BLANK"], BTN["BT_NONE"], BTN["BT_START"]
    if phase == "PH_SETUP":
        # The COGSTOP row's setup is stop(), run on the panel cog itself (it ends two cogs, PLOT-DISPLAY-RULES
        # rule 9), so nothing polls a button during it: no ABORT is drawn, because only live buttons are.
        left = BTN["BT_NONE"] if last else BTN["BT_ABORT"]
        return BAN["B_SETUP"], base + CARD_INTRO, LBL["L_BLANK"], LBL["L_BLANK"], left, BTN["BT_NONE"]
    if phase == "PH_ACT":
        right = BTN["BT_NONE"] if r["kind"] == "power" else BTN["BT_DONE"]
        banner = BAN["B_POWERED"] if r["kind"] == "power" else BAN["B_TURN"]
        return banner, base + CARD_ACT, LBL[r["act_lbl"][0]], LBL[r["act_lbl"][1]], BTN["BT_ABORT"], right
    right = BTN["BT_FINISH"] if last else BTN["BT_NEXT"]
    return BAN["B_RESULT"], base + CARD_RESULT, LBL[r["res_lbl"][0]], LBL[r["res_lbl"][1]], BTN["BT_REDO"], right


def opening_status(row_idx, phase):
    """The phrase a screen opens with. The harness reads it from the table's last byte, so the measure cog
    publishes this, not a copy of it: SETUP the row's setup phrase, ACT the first phrase of its walk.
    INTRO and RESULT are shown by cog 0 with their own phrase, so their byte is blank."""
    r = ROWS[row_idx]
    if phase == "PH_SETUP":
        return STAT[r["setup"]]
    if phase == "PH_ACT":
        return STAT[r["walk"][0]]
    return STAT["ST_BLANK"]


for _r in range(ROW_COUNT):                           # the slot rule, checked rather than trusted
    for _p in PHASES:
        _, _, _, _, _l, _rt = screen_for(_r, _p)
        assert BUTTONS[_l][3] in (None, "L") and BUTTONS[_rt][3] in (None, "R"), (_r, _p)

# ---------------------------------------------------------------- colours ---
C_PANEL = (28, 32, 38)
C_WELL = (12, 13, 16)
C_HDR = (48, 40, 20)
C_TEXT = (232, 236, 240)
C_DIM = (130, 138, 148)
C_AMBER = (240, 176, 48)
C_LABEL = (200, 160, 80)
C_GOOD = (110, 220, 130)
C_WARN = (250, 150, 70)
C_FRAME = (90, 96, 106)
C_BTN = (54, 62, 72)
C_BTN_HI = (220, 200, 90)

FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


@functools.lru_cache(maxsize=None)
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
    """Largest font at or below `size` whose text fits max_w -- measured, never guessed."""
    while size > 8:
        f = font(size)
        if text_width(d, text, f) <= max_w:
            return f
        size -= 1
    return font(8)


def wrap_lines(d, text, fnt, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = word if line == "" else line + " " + word
        if text_width(d, trial, fnt) <= max_w or line == "":
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def centre(d, box, text, fnt, fill):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + (w - (r - l)) / 2 - l, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


def left(d, box, text, fnt, fill, pad=0):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + pad - l, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- layers ----
def build_background():
    img = Image.new("RGB", (PANEL_W, PANEL_H), C_PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PANEL_W - 1, HDR_H - 1], fill=C_HDR)
    centre(d, (0, 0, PANEL_W, HDR_H), HEADER_TEXT, fit(d, HEADER_TEXT, 17, PANEL_W - 16), C_TEXT)
    f = font(18)
    left(d, (ROWLBL_X, ROW_LINE_Y, RNUM_X - ROWLBL_X, NAME_H), "ROW", f, C_DIM)
    d.rectangle([RNUM_X, ROW_LINE_Y, RNUM_X + DGT_W - 1, ROW_LINE_Y + DGT_H - 1], fill=C_WELL)
    left(d, (OF_X, ROW_LINE_Y, NAME_X - OF_X, NAME_H), "OF %d" % ROW_COUNT, f, C_DIM)
    d.rectangle([NAME_X, ROW_LINE_Y, NAME_X + NAME_W - 1, ROW_LINE_Y + NAME_H - 1], fill=C_WELL)
    d.rectangle([BAN_X, BAN_Y, BAN_X + BAN_W - 1, BAN_Y + BAN_H - 1], fill=C_WELL)
    d.rectangle([CARD_X, CARD_Y, CARD_X + CARD_W - 1, CARD_Y + CARD_H - 1], fill=C_WELL)
    left(d, (SEEN_LBL_X, SEEN_Y, SEEN_LBL_W, STAT_H), "SEEN NOW", fit(d, "SEEN NOW", 15, SEEN_LBL_W - 4), C_LABEL)
    d.rectangle([STAT_X, SEEN_Y, STAT_X + STAT_W - 1, SEEN_Y + STAT_H - 1], fill=C_WELL)
    for y in (READ1_Y, READ2_Y):
        d.rectangle([READ_X, y, READ_X + READ_PITCH * READ_COUNT - 1, y + DGT_H - 1], fill=C_WELL)
    d.text((FOOT_X, FOOT_Y), FOOTER_TEXT, font=fit(d, FOOTER_TEXT, 12, FOOT_W), fill=C_DIM)
    return img


def build_names():
    names = [r["name"] for r in ROWS] + ["ALL ROWS DONE", "NO ROW RAN"]
    img = Image.new("RGB", (NAME_W, NAME_H * len(names)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(names):
        left(d, (0, i * NAME_H, NAME_W, NAME_H), "--  " + text, fit(d, "--  " + text, 20, NAME_W - 12), C_AMBER, pad=8)
    return img


def build_banners():
    img = Image.new("RGB", (BAN_W, BAN_H * len(BANNERS)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, (_, text, fill) in enumerate(BANNERS):
        d.rectangle([0, i * BAN_H, BAN_W - 1, i * BAN_H + BAN_H - 1], fill=fill)
        centre(d, (0, i * BAN_H, BAN_W, BAN_H), text, fit(d, text, 17, BAN_W - 16), C_TEXT)
    return img


CARD_LBL_W = 132


def draw_card(d, y0, fields):
    """Labelled lines, the largest font at or below 16 that fits the whole card -- measured."""
    for size in range(16, 9, -1):
        f = font(size)
        _, t, _, b = d.textbbox((0, 0), "Ag", font=f)
        line_h = (b - t) + 4
        laid = [(lbl, wrap_lines(d, txt, f, CARD_W - CARD_LBL_W - 12)) for lbl, txt in fields]
        total = sum(len(lines) for _, lines in laid) * line_h + (len(laid) - 1) * 5
        if total <= CARD_H - 10:
            break
    y = y0 + (CARD_H - total) / 2
    lf = fit(d, "YOU SHOULD FEEL", size - 2, CARD_LBL_W - 12)
    for lbl, lines in laid:
        d.text((8, y + 2), lbl, font=lf, fill=C_LABEL)
        for line in lines:
            d.text((CARD_LBL_W, y), line, font=f, fill=C_TEXT)
            y += line_h
        y += 5


def build_cards():
    all_cards = cards()
    img = Image.new("RGB", (CARD_W, CARD_H * len(all_cards)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, fields in enumerate(all_cards):
        draw_card(d, i * CARD_H, fields)
    return img


def build_statuses():
    img = Image.new("RGB", (STAT_W, STAT_H * len(STATUSES)), C_WELL)
    d = ImageDraw.Draw(img)
    ink = {"wait": C_TEXT, "good": C_GOOD, "warn": C_WARN}
    for i, (_, text, kind) in enumerate(STATUSES):
        if text:
            left(d, (0, i * STAT_H, STAT_W, STAT_H), text, fit(d, text, 15, STAT_W - 12), ink[kind], pad=6)
    return img


def build_labels():
    img = Image.new("RGB", (LBL_W, LBL_H * len(LABELS)), C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (_, text) in enumerate(LABELS):
        if text:
            left(d, (0, i * LBL_H, LBL_W, LBL_H), text, fit(d, text, 16, LBL_W - 8), C_DIM)
    return img


def build_digits():
    img = Image.new("RGB", (DGT_W * 11, DGT_H), C_WELL)
    d = ImageDraw.Draw(img)
    f = font(28)
    for i in range(10):
        centre(d, (i * DGT_W, 0, DGT_W, DGT_H), str(i), f, C_TEXT)
    return img                                     # cell 10 stays blank: a suppressed leading zero


def draw_button(d, x, y, title, key, hilite):
    if title == "":
        d.rectangle([x, y, x + BTN_W - 1, y + BTN_H - 1], fill=C_PANEL)   # BT_NONE: the bare panel
        return
    d.rectangle([x, y, x + BTN_W - 1, y + BTN_H - 1], fill=C_BTN_HI if hilite else C_BTN, outline=C_FRAME)
    ink = (20, 20, 20) if hilite else C_TEXT
    half = 24
    centre(d, (x, y + 2, BTN_W, half), title, fit(d, title, 18, BTN_W - 12), ink)
    centre(d, (x, y + half, BTN_W, BTN_H - half - 2), key, fit(d, key, 11, BTN_W - 12), ink if hilite else C_DIM)


def build_buttons():
    img = Image.new("RGB", (BTN_W * 2, BTN_H * len(BUTTONS)), C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (_, title, key, _) in enumerate(BUTTONS):
        draw_button(d, 0, i * BTN_H, title, key, False)
        draw_button(d, BTN_W, i * BTN_H, title, key, True)
    return img


ASSETS = [
    ("t0s_bg.bmp", build_background),        # layer 1
    ("t0s_names.bmp", build_names),          # layer 2
    ("t0s_banners.bmp", build_banners),      # layer 3
    ("t0s_cards.bmp", build_cards),          # layer 4
    ("t0s_digits.bmp", build_digits),        # layer 5
    ("t0s_status.bmp", build_statuses),      # layer 6
    ("t0s_labels.bmp", build_labels),        # layer 7
    ("t0s_buttons.bmp", build_buttons),      # layer 8
]

# ---------------------------------------------------------------- spin2 -----
def con_block():
    lines = ["CON { T0-24 panel -- GENERATED by tools/gen_t0stop_assets.py, do not hand-edit }", "",
             "' Layers: 1 background, 2 row names, 3 banners, 4 cards, 5 digits, 6 status phrases,",
             "' 7 reading labels, 8 buttons. A DEBUG backtick command takes the layer as a literal, so the",
             "' layer numbers live in t0sSetupPanel()/t0sDraw() and here only as this comment.", ""]
    geo = [("T0S_ROW_COUNT", ROW_COUNT), ("T0S_PHASE_COUNT", len(PHASES)),
           ("T0S_RNUM_X", RNUM_X), ("T0S_ROW_LINE_Y", ROW_LINE_Y),
           ("T0S_NAME_X", NAME_X), ("T0S_NAME_W", NAME_W), ("T0S_NAME_H", NAME_H),
           ("T0S_BAN_X", BAN_X), ("T0S_BAN_Y", BAN_Y), ("T0S_BAN_W", BAN_W), ("T0S_BAN_H", BAN_H),
           ("T0S_CARD_X", CARD_X), ("T0S_CARD_Y", CARD_Y), ("T0S_CARD_W", CARD_W), ("T0S_CARD_H", CARD_H),
           ("T0S_STAT_X", STAT_X), ("T0S_STAT_Y", SEEN_Y), ("T0S_STAT_W", STAT_W), ("T0S_STAT_H", STAT_H),
           ("T0S_LBL_X", LBL_X), ("T0S_LBL_W", LBL_W), ("T0S_LBL_H", LBL_H),
           ("T0S_READ1_Y", READ1_Y), ("T0S_READ2_Y", READ2_Y), ("T0S_READ_X", READ_X),
           ("T0S_READ_PITCH", READ_PITCH), ("T0S_READ_COUNT", READ_COUNT),
           ("T0S_DGT_W", DGT_W), ("T0S_DGT_H", DGT_H), ("T0S_DGT_BLANK", DGT_BLANK),
           ("T0S_BTN_W", BTN_W), ("T0S_BTN_H", BTN_H), ("T0S_BTN_L_X", BTN_L_X), ("T0S_BTN_R_X", BTN_R_X),
           ("T0S_BTN_Y", BTN_Y),
           ("T0S_CARD_NOTREADY", CARD_NOTREADY),
           ("T0S_CARD_ALLDONE", CARD_ALLDONE), ("T0S_NAME_ALLDONE", ROW_COUNT),
           ("T0S_NAME_NOTREADY", ROW_COUNT + 1),
           ("T0S_SCREEN_BYTES", 7), ("T0S_SCR_BANNER", 0), ("T0S_SCR_CARD", 1), ("T0S_SCR_LBL1", 2),
           ("T0S_SCR_LBL2", 3), ("T0S_SCR_BTN_L", 4), ("T0S_SCR_BTN_R", 5), ("T0S_SCR_STATUS", 6)]
    lines += ["    %-24s = %d" % (n, v) for n, v in geo]
    # The row ids: the harness defines its T0_24_ROW_* from these, so the table's row order and the
    # harness's ids cannot drift apart.
    for title, table in (("rows, in t0sScreenTab order", [("ROW_" + r["id"],) for r in ROWS]),
                         ("phases", [(p,) for p in PHASES]), ("banners", BANNERS), ("status phrases", STATUSES),
                         ("reading labels", LABELS), ("buttons", BUTTONS)):
        lines += ["", "' %s" % title]
        lines += ["    %-24s = %d" % ("T0S_" + entry[0], i) for i, entry in enumerate(table)]
    return "\n".join(lines)


def dat_block():
    lines = ["DAT { T0-24 screen table -- GENERATED by tools/gen_t0stop_assets.py, do not hand-edit }", "",
             "' One entry per (row, phase), row-major in T0_24_ROW_* order then PH_* order. Each entry is",
             "' T0S_SCREEN_BYTES bytes (T0S_SCR_*): banner, card, reading label 1, reading label 2, left button,",
             "' right button, and the phrase the screen opens with (blank where cog 0 supplies its own).",
             "' The generator's --storyboard renders these same entries, so the reviewed screens are these.",
             "t0sScreenTab"]
    for ri, r in enumerate(ROWS):
        for p in PHASES:
            vals = screen_for(ri, p) + (opening_status(ri, p),)
            lines.append("    BYTE    %s   ' %s %s" % (", ".join("%2d" % v for v in vals), r["id"], p))
    return "\n".join(lines)


# ---------------------------------------------------------------- storyboard
def compose(layers, row_idx, seq_num, banner, card, stat, lbl1, lbl2, r1, r2, btn_l, btn_r, hilite=None):
    """Compose one frame exactly as t0sDraw() blits it (same pieces, same places)."""
    bg, names, bans, crds, dgts, stats, lbls, btns = layers
    img = bg.copy()
    if seq_num > 0:
        img.paste(dgts.crop((seq_num * DGT_W, 0, seq_num * DGT_W + DGT_W, DGT_H)), (RNUM_X, ROW_LINE_Y))
    img.paste(names.crop((0, row_idx * NAME_H, NAME_W, row_idx * NAME_H + NAME_H)), (NAME_X, ROW_LINE_Y))
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


SAMPLE_READINGS = {"L_HOLD_PCT": 100, "L_PUSHED": 3, "L_MS_CEIL": 274, "L_MS_SLIP": 180, "L_MS_LIMIT": 2210,
                   "L_SPEED": 214, "L_TICKS": 61, "L_BAND_TICKS": 23, "L_BAND_MS": 412}


def storyboard(out_dir, layers):
    """Every screen a normal run shows, in the default execution order (row-id order; -D T0_24_FLT_FIRST
    moves the two fault rows ahead of the e-stop row, which changes only their row numbers), one PNG each --
    for the desk walk."""
    os.makedirs(out_dir, exist_ok=True)
    lbl_name = {i: e[0] for i, e in enumerate(LABELS)}
    n = 0
    for ri in range(ROW_COUNT):
        seq = ri + 1
        r = ROWS[ri]
        steps = [("PH_INTRO", "ST_WAIT_START"), ("PH_SETUP", r["setup"])]
        steps += [("PH_ACT", s) for s in r["walk"]]
        steps += [("PH_RESULT", "ST_MEASURED")]
        for p, st in steps:
            ban, card, l1, l2, bl, br = screen_for(ri, p)
            v1 = SAMPLE_READINGS.get(lbl_name[l1]) if p in ("PH_ACT", "PH_RESULT") else None
            v2 = SAMPLE_READINGS.get(lbl_name[l2]) if p in ("PH_ACT", "PH_RESULT") else None
            img = compose(layers, ri, seq, ban, card, STAT[st], l1, l2, v1, v2, bl, br)
            n += 1
            img.save(os.path.join(out_dir, "%02d_row%d_%s_%s.png" % (n, seq, p[3:].lower(), st[3:].lower())))
    img = compose(layers, ROW_COUNT, 0, BAN["B_ALLDONE"], CARD_ALLDONE, STAT["ST_CELLS_LOGGED"],
                  LBL["L_BLANK"], LBL["L_BLANK"], None, None, BTN["BT_NONE"], BTN["BT_NONE"])
    n += 1
    img.save(os.path.join(out_dir, "%02d_alldone.png" % n))
    # The screens a run shows when something goes other than planned, and a clicked button lit.
    alt = [(3, "PH_ACT", "ST_STOP_SLOW", None), (3, "PH_RESULT", "ST_NM_NO_SPIN", None),
           (0, "PH_RESULT", "ST_NM_ABORTED", None), (0, "PH_RESULT", "ST_NM_NOT_FRESH", None),
           (5, "PH_RESULT", "ST_NM_10A", None), (0, "PH_ACT", "ST_CEIL_GOT", BTN["BT_DONE"])]
    for ri, p, st, lit in alt:
        ban, card, l1, l2, bl, br = screen_for(ri, p)
        nm = st.startswith("ST_NM")
        v1 = None if nm else SAMPLE_READINGS.get(lbl_name[l1])
        v2 = None if nm else SAMPLE_READINGS.get(lbl_name[l2])
        img = compose(layers, ri, ri + 1, ban, card, STAT[st], l1, l2, v1, v2, bl, br, hilite=lit)
        n += 1
        img.save(os.path.join(out_dir, "%02d_alt_row%d_%s_%s.png" % (n, ri + 1, p[3:].lower(), st[3:].lower())))
    img = compose(layers, ROW_COUNT + 1, 0, BAN["B_NOTREADY"], CARD_NOTREADY, STAT["ST_NOT_READY"],
                  LBL["L_BLANK"], LBL["L_BLANK"], None, None, BTN["BT_NONE"], BTN["BT_NONE"])
    n += 1
    img.save(os.path.join(out_dir, "%02d_alt_notready.png" % n))
    sys.stderr.write("storyboard: %d screens in %s\n" % (n, out_dir))


def main():
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
