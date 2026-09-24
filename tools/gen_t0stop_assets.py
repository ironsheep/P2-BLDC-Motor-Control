#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for src/test_bench_t0.spin2's T0-24 stop-state hand test
(-D T0_STOPMODE, bench-run.sh tier t0-stopmode).

Same technique, and the same single-source-of-truth discipline, as tools/gen_t0hand_assets.py and
tools/gen_dual_assets.py: layers are loaded once with LAYER, a frame is composed by blitting opaque
cells with CROP and then one UPDATE, and the layout constants below are the only place the numbers
live -- this script draws the BMPs from them and prints a ready-to-paste Spin2 CON block of the same
numbers.

    python3 tools/gen_t0stop_assets.py            # write src/t0s_*.bmp, print the CON block
    python3 tools/gen_t0stop_assets.py --preview  # also write PNGs for visual check

REBUILT task 3607 (PANEL-CERTIFICATION-EVALUATION.md 2026-09-22, PL-115/PL-116, doctrine overlay P7,
DOCs/procedures/PLOT-DISPLAY-RULES.md rule 10): every operator action is now a TITLED BUTTON (START
ROW, DONE, ABORT), hit-tested with PC_MOUSE under CARTESIAN 1, exactly as bmpanel in
test_bench_dual.spin2 does (tools/gen_dual_assets.py's build_buttons()). Keys still exist (S / D /
SPACE) but only duplicate a button; the button titles are what the operator reads.

WHY THIS PANEL HAS TWO TEXT LAYERS PLUS A ROW-NUMBER DIGIT. Every row asks the operator for a
DIFFERENT physical action, and overlay P1 requires the panel to name that action BEFORE the row
runs. The row layer says which state is in force (by NAME only -- no baked-in row number, because
-D T0_24_FLT_FIRST runs the two fault rows ahead of the e-stop row (PL-116) and a number baked into
the art would then contradict the sequence actually running). The row-number digit (layer 4, shared
with the numeric readouts) is blitted from the loop position instead, so "row N" always means the
same thing in the panel, the log AND the runner banner, however the rows are ordered this run.

DEBUG LAYER requires 24-bit uncompressed (BI_RGB) BMP with no alpha, which is exactly what
Pillow writes for an "RGB" image saved as .bmp.

Sprite cells are OPAQUE -- there is no alpha -- so every cell carries the same background colour
as the region it lands on, or the blit leaves a seam.

The .bmp outputs are committed beside test_bench_t0.spin2. Whether the panel draws on the rig is
shown only by the t0-stopmode run itself.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- layout ----
# Keep these numbers identical to test_bench_t0.spin2's T0S_* CON block (task 3578, rebuilt 3607).
PANEL_W, PANEL_H = 480, 344
PANEL_POS_X, PANEL_POS_Y = 60, 80

HDR_X, HDR_Y, HDR_W, HDR_H = 0, 0, 480, 28

RNUM_X, RNUM_Y = 12, 32                    # the row-number digit, one cell, blitted from LAYER 4
ROW_X, ROW_Y, ROW_W, ROW_H = 56, 32, 412, 36
ACT_X, ACT_Y, ACT_W, ACT_H = 12, 76, 456, 64

DGT_W, DGT_H = 28, 36
DGT_CELLS = 11                             # "0".."9" plus a blank at index 10
DGT_BLANK = 10

READ_LBL_X = 12                            # the three readout labels, baked into the background
READ_X = 170                               # where each readout's digits start
READ_PITCH = 30
HAND_Y = 148                               # reading 1 (hand-phase ticks, or a hold row's own quantity)
AFTER_Y = 192                              # reading 2 (after-release ticks, or a hold row's own quantity)
MS_Y = 236                                 # reading 3 (elapsed ms, or a hold row's own quantity)
HAND_COUNT = 4                             # up to 9999
AFTER_COUNT = 4                            # up to 9999
MS_COUNT = 5                               # up to 99999

BTN_W, BTN_H = 108, 36
BTN_PITCH = 116
BTN_Y = 284
BTN_X0 = (PANEL_W - (BTN_W * 3 + (BTN_PITCH - BTN_W) * 2)) // 2
BTN_NORMAL, BTN_HILITE = 0, 1              # column in t0s_buttons.bmp

FOOT_X, FOOT_Y, FOOT_W, FOOT_H = 12, 328, 456, 14

# Domain text baked into the static background -- MUST match test_bench_t0.spin2 (task 3578, 3607).
# The wheel named here is T0_MOTOR_BASE (PINS_P16_P31): the right board is at P16 (STEPHEN 2026-09-11).
WHEEL_TEXT = "RIGHT WHEEL (P16 BOARD)"
# Task 3617 (PL-123 item 4): the header names the wheel, so every screen does from the first on.
HEADER_TEXT = "T0-24 STOP-STATE HAND TEST -- %s" % WHEEL_TEXT
# Task 3617: a spin row that never passes the measuring speed is tried again, up to this many times in
# all. The retry texts bake the number in -- keep it equal to test_bench_t0.spin2's T0_24_SPIN_TRIES.
SPIN_TRIES = 3
assert SPIN_TRIES == 3, "ACTION_TEXTS carries one retry cell per try after the first: 2 and 3"
FOOTER_TEXT = "CLICK START ROW, DONE OR ABORT -- CLICK THIS WINDOW FIRST -- PANIC: PULL THE PACK"

# Row NAMES only (task 3607: no baked-in "ROW N", the digit supplies the running number). Order here
# is index order = the semantic T0_24_ROW_* id, NOT necessarily execution order -- T0_24_FLT_FIRST
# changes execution order only, never these ids or their art.
ROW_LABELS = [
    "HOLD-RISE: PUSH AND HOLD DISPLACED",
    "HOLD-SLIP: PUSH PAST A LOW CEILING",
    "HOLD-LIMIT: SUSTAINED PUSH AT CEILING",
    "COAST AT REST",
    # task 3617: the e-stop is applied by the program to the coasting wheel, not held at rest
    "E-STOP AS IT COASTS",
    "FAULT, COAST MODE",
    # task 3617: SM_BRAKE is "brake" in the API; "hold" means only the hold at rest (PLOT-DISPLAY-RULES.md rule 10)
    "FAULT, BRAKE MODE",
    "DRIVER COG STOPPED (FREE YARDSTICK)",
    "ALL ROWS DONE",
]

# Every action the operator is ever asked for, indexed by T0_24_ACT_*. Each row names its own
# before it runs (overlay P1) and says what to FEEL (PLOT-DISPLAY-RULES.md rule 10.3).
ACTION_TEXTS = [
    "CLICK START ROW WHEN READY. HANDS OFF UNTIL THIS PANEL SAYS TURN, SPIN OR PUSH.",
    "SETTING THIS ROW UP -- HANDS OFF THE WHEEL.",
    "HANDS OFF -- THE %s SPINS UNDER POWER AND IS FAULTED ON PURPOSE. CLICK ABORT TO STOP IT." % WHEEL_TEXT,
    # task 3617: a HARD spin -- the reading starts only once the wheel slows through the measuring speed
    "SPIN THE %s HARD BY HAND AND LET GO -- IT MUST PASS THE MEASURING SPEED. YOU SHOULD SEE IT SPIN FREELY AND COAST TO A STOP. THE ROW ENDS BY ITSELF." % WHEEL_TEXT,
    # task 3617: the e-stop row spins the FREE wheel; the program shorts it at the measuring speed
    "SPIN THE %s HARD AND LET GO -- IT MUST PASS THE MEASURING SPEED. THE PROGRAM SHORTS IT AS IT SLOWS; YOU WILL SEE IT STOP ABRUPTLY. THE ROW ENDS BY ITSELF." % WHEEL_TEXT,
    "HANDS OFF -- MEASURING WHAT THE WHEEL DOES ON ITS OWN.",
    "ROW DONE -- ITS READING IS BELOW. CLICK START ROW FOR THE NEXT ONE.",
    "ALL ROWS DONE. NOTHING MORE TO DO AT THE RIG.",
    "PUSH THE WHEEL BY HAND AND HOLD IT DISPLACED. YOU SHOULD FEEL THE RESISTANCE GROW OVER ABOUT A QUARTER SECOND. READING 1 = HOLD DUTY %%, READING 2 = HOLD STATUS (0 OFF 1 HOLDING 2 SLIPPED 3 LIMITED). CLICK DONE ONCE YOU HAVE FELT IT.",
    "PUSH THE WHEEL PAST A LOW HOLD CEILING. IT SHOULD GIVE WAY AND THEN DRAG AGAINST YOUR TURN, NOT HOLD. READING 2 = HOLD STATUS. CLICK DONE ONCE YOU HAVE FELT IT.",
    "PUSH THE WHEEL TO THE CEILING AND HOLD IT THERE STEADILY FOR ABOUT TWO SECONDS. READING 2 = HOLD STATUS, READING 3 = MS AT THE CEILING. CLICK DONE ONCE IT HAS GIVEN WAY, OR KEEP HOLDING -- THE ROW TIMES ITSELF.",
    "THE DRIVER DID NOT COME UP READY. EVERY CELL BELOW IS NOMEAS. NOTHING TO DO AT THE RIG.",
    "THIS ROW COULD NOT REACH ITS STATE. ITS CELL IS NOMEAS. CLICK START ROW FOR THE NEXT ONE.",
    # task 3617: nothing silent -- a spin below the measuring speed is said so, and tried again
    # (T0_24_ACT_RETRY_FREE_2 .. T0_24_ACT_SPIN_NOMEAS). Each retry cell keeps the row's own prediction.
    "TOO SLOW TO MEASURE -- SPIN IT HARDER AND LET GO AGAIN (TRY 2 OF %d). IT SHOULD SPIN FREELY AND COAST TO A STOP." % SPIN_TRIES,
    "TOO SLOW TO MEASURE -- SPIN IT HARDER AND LET GO AGAIN (TRY 3 OF %d). IT SHOULD SPIN FREELY AND COAST TO A STOP." % SPIN_TRIES,
    "TOO SLOW TO MEASURE -- SPIN IT HARDER AND LET GO AGAIN (TRY 2 OF %d). THE PROGRAM SHORTS IT AS IT SLOWS; YOU WILL SEE IT STOP ABRUPTLY." % SPIN_TRIES,
    "TOO SLOW TO MEASURE -- SPIN IT HARDER AND LET GO AGAIN (TRY 3 OF %d). THE PROGRAM SHORTS IT AS IT SLOWS; YOU WILL SEE IT STOP ABRUPTLY." % SPIN_TRIES,
    "NOT MEASURED -- THE WHEEL NEVER PASSED THE MEASURING SPEED BEFORE THE ROW ENDED. ITS CELL IS NOMEAS. CLICK START ROW FOR THE NEXT ONE.",
]

# Buttons, in T0_24_BTN_* order: (name, title, key hint). Only three controls exist; each is ONE
# meaning (PLOT-DISPLAY-RULES.md rule 10: "One control has one meaning").
BUTTONS = [
    ("START", "START ROW", "S"),
    ("DONE", "DONE", "D"),
    ("ABORT", "ABORT", "SPACE"),
]

# ---------------------------------------------------------------- colours ---
C_PANEL   = (28, 32, 38)
C_WELL    = (12, 13, 16)
C_HDR     = (48, 40, 20)
C_TEXT    = (232, 236, 240)
C_DIM     = (120, 128, 138)
C_AMBER   = (240, 176, 48)
C_FRAME   = (90, 96, 106)
C_BTN     = (44, 50, 58)
C_BTN_HI  = (200, 84, 40)
C_BTN_SUB = (150, 156, 164)

# Both hosts: Stephen's Mac runs the bench, and the build/doc gates also run on Linux (613d2bf),
# so the artwork regenerates identically wherever this script is run.
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


def fit(d, text, size, max_w):
    """Largest font at or below `size` whose rendered text fits max_w. Measured, not guessed --
    see gen_t0hand_assets.py's own note on why a guessed size clips at the panel edge."""
    while size > 8:
        f = font(size)
        l, _, r, _ = d.textbbox((0, 0), text, font=f)
        if (r - l) <= max_w:
            return f
        size -= 1
    return font(8)


def wrap_lines(d, text, fnt, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = word if line == "" else line + " " + word
        l, _, r, _ = d.textbbox((0, 0), trial, font=fnt)
        if (r - l) <= max_w or line == "":
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit_wrapped(d, text, size, max_w, max_h, gap=4):
    """Largest font at or below `size` whose wrapped text fits the box. Measured, never guessed."""
    while size > 8:
        f = font(size)
        lines = wrap_lines(d, text, f, max_w)
        _, t, _, b = d.textbbox((0, 0), "Ag", font=f)
        if (len(lines) * (b - t)) + ((len(lines) - 1) * gap) <= max_h:
            return f, lines
        size -= 1
    f = font(8)
    return f, wrap_lines(d, text, f, max_w)


def centre(d, box, text, fnt, fill):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + (w - (r - l)) / 2 - l, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


def left(d, box, text, fnt, fill, pad=0):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + pad, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


def readout_well(d, x, y, count):
    d.rectangle([x, y, x + READ_PITCH * count - 1, y + DGT_H - 1], fill=C_WELL)


def build_background():
    img = Image.new("RGB", (PANEL_W, PANEL_H), C_PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle([HDR_X, HDR_Y, HDR_X + HDR_W - 1, HDR_Y + HDR_H - 1], fill=C_HDR)
    centre(d, (HDR_X, HDR_Y, HDR_W, HDR_H), HEADER_TEXT, fit(d, HEADER_TEXT, 19, HDR_W - 16), C_TEXT)

    # wells the text/digit layers blit into, so an un-blitted frame still looks deliberate
    d.rectangle([RNUM_X, RNUM_Y, RNUM_X + DGT_W - 1, RNUM_Y + DGT_H - 1], fill=C_WELL)
    d.rectangle([ROW_X, ROW_Y, ROW_X + ROW_W - 1, ROW_Y + ROW_H - 1], fill=C_WELL)
    d.rectangle([ACT_X, ACT_Y, ACT_X + ACT_W - 1, ACT_Y + ACT_H - 1], fill=C_WELL)

    # Each readout says only "READING n": the hand/after-ticks rows and the hold rows use the same
    # three slots for different quantities, and the ACTION text (per row) says which is which --
    # never the label, which cannot change per row (build_actions()'s text carries the meaning).
    note_x = READ_X + READ_PITCH * MS_COUNT + 10
    note_w = PANEL_W - note_x - 12
    for lbl_y, lbl, count in ((HAND_Y, "READING 1", HAND_COUNT),
                               (AFTER_Y, "READING 2", AFTER_COUNT),
                               (MS_Y, "READING 3", MS_COUNT)):
        left(d, (READ_LBL_X, lbl_y, READ_X - READ_LBL_X - 8, DGT_H), lbl,
             fit(d, "READING 1", 17, READ_X - READ_LBL_X - 8), C_DIM)
        readout_well(d, READ_X, lbl_y, count)

    d.text((FOOT_X, FOOT_Y), FOOTER_TEXT, font=fit(d, FOOTER_TEXT, 12, FOOT_W), fill=C_DIM)
    return img


def build_rows():
    img = Image.new("RGB", (ROW_W, ROW_H * len(ROW_LABELS)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(ROW_LABELS):
        centre(d, (0, i * ROW_H, ROW_W, ROW_H), text, fit(d, text, 19, ROW_W - 12), C_AMBER)
    return img


def build_actions():
    img = Image.new("RGB", (ACT_W, ACT_H * len(ACTION_TEXTS)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(ACTION_TEXTS):
        fnt, lines = fit_wrapped(d, text, 16, ACT_W - 16, ACT_H - 12)
        _, t, _, b = d.textbbox((0, 0), "Ag", font=fnt)
        line_h = (b - t) + 3
        top = (i * ACT_H) + ((ACT_H - (len(lines) * line_h)) / 2)
        for line_idx, line in enumerate(lines):
            d.text((8, top + line_idx * line_h), line, font=fnt, fill=C_TEXT)
    return img


def build_digits():
    img = Image.new("RGB", (DGT_W * DGT_CELLS, DGT_H), C_WELL)
    d = ImageDraw.Draw(img)
    f = font(28)
    for i in range(10):
        centre(d, (i * DGT_W, 0, DGT_W, DGT_H), str(i), f, C_TEXT)
    # index 10 stays blank -- used to suppress a leading zero
    return img


def draw_button(d, x, y, title, key, hilite):
    fill = C_BTN_HI if hilite else C_BTN
    ink = C_TEXT
    sub = C_TEXT if hilite else C_BTN_SUB
    d.rectangle([x, y, x + BTN_W - 1, y + BTN_H - 1], fill=fill, outline=C_FRAME)
    half = BTN_H // 2
    centre(d, (x, y + 1, BTN_W, half), title, fit(d, title, 15, BTN_W - 10), ink)
    centre(d, (x, y + half, BTN_W, half - 1), key, fit(d, key, 11, BTN_W - 10), sub)


def build_buttons():
    img = Image.new("RGB", (BTN_W * 2, BTN_H * len(BUTTONS)), C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (_, title, key) in enumerate(BUTTONS):
        draw_button(d, BTN_NORMAL * BTN_W, i * BTN_H, title, key, False)
        draw_button(d, BTN_HILITE * BTN_W, i * BTN_H, title, key, True)
    return img


ASSETS = [
    ("t0s_bg.bmp", build_background),
    ("t0s_rows.bmp", build_rows),
    ("t0s_actions.bmp", build_actions),
    ("t0s_digits.bmp", build_digits),
    ("t0s_buttons.bmp", build_buttons),
]

CON_BLOCK = f"""
CON {{ T0-24 panel geometry -- GENERATED by tools/gen_t0stop_assets.py, do not hand-edit }}

' The T0S_LYR_* numbers below RECORD which layer holds which artwork; they cannot be referenced
' from the code, because a DEBUG backtick command takes the window name and the layer as literal
' tokens rather than expressions. Changing one here moves nothing -- change the literal in
' t0sSetupPanel()/t0sDrawPanel() and this number together.

    T0S_PANEL_W       = {PANEL_W}
    T0S_PANEL_H       = {PANEL_H}
    T0S_PANEL_POS_X   = {PANEL_POS_X}
    T0S_PANEL_POS_Y   = {PANEL_POS_Y}

    T0S_LYR_BG        = 1
    T0S_LYR_ROW       = 2
    T0S_LYR_ACT       = 3
    T0S_LYR_DGT       = 4
    T0S_LYR_BTN       = 5

    T0S_RNUM_X        = {RNUM_X}
    T0S_RNUM_Y        = {RNUM_Y}

    T0S_ROW_X         = {ROW_X}
    T0S_ROW_Y         = {ROW_Y}
    T0S_ROW_W         = {ROW_W}
    T0S_ROW_H         = {ROW_H}

    T0S_ACT_X         = {ACT_X}
    T0S_ACT_Y         = {ACT_Y}
    T0S_ACT_W         = {ACT_W}
    T0S_ACT_H         = {ACT_H}

    T0S_DGT_W         = {DGT_W}
    T0S_DGT_H         = {DGT_H}
    T0S_DGT_BLANK     = {DGT_BLANK}

    T0S_READ_X        = {READ_X}
    T0S_READ_PITCH    = {READ_PITCH}
    T0S_HAND_Y        = {HAND_Y}
    T0S_AFTER_Y       = {AFTER_Y}
    T0S_MS_Y          = {MS_Y}
    T0S_HAND_COUNT    = {HAND_COUNT}
    T0S_AFTER_COUNT   = {AFTER_COUNT}
    T0S_MS_COUNT      = {MS_COUNT}

    T0S_BTN_W         = {BTN_W}
    T0S_BTN_H         = {BTN_H}
    T0S_BTN_X0        = {BTN_X0}
    T0S_BTN_PITCH     = {BTN_PITCH}
    T0S_BTN_Y         = {BTN_Y}
    T0S_BTN_NORMAL    = {BTN_NORMAL}
    T0S_BTN_HILITE    = {BTN_HILITE}
"""


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(os.path.dirname(here), "src")
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
    print(CON_BLOCK)


if __name__ == "__main__":
    main()
