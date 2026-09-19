#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for src/test_bench_t0.spin2's T0-24 stop-state hand test
(-D T0_STOPMODE, bench-run.sh tier t0-stopmode).

Same technique, and the same single-source-of-truth discipline, as tools/gen_t0hand_assets.py:
layers are loaded once with LAYER, a frame is composed by blitting opaque cells with CROP and
then one UPDATE, and the layout constants below are the only place the numbers live -- this
script draws the BMPs from them and prints a ready-to-paste Spin2 CON block of the same numbers.

    python3 tools/gen_t0stop_assets.py            # write src/t0s_*.bmp, print the CON block
    python3 tools/gen_t0stop_assets.py --preview  # also write PNGs for visual check

WHY THIS PANEL HAS TWO TEXT LAYERS. Every row of the test asks the operator for a DIFFERENT
physical action, and overlay P1 requires the panel to name that action BEFORE the row runs. So
the row name and the action live on separate layers: the row layer says which of the six states
is in force, the action layer says what to do right now. Neither is ever inferred from the other.

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
# Keep these numbers identical to test_bench_t0.spin2's T0S_* CON block (task 3578).
PANEL_W, PANEL_H = 480, 300
PANEL_POS_X, PANEL_POS_Y = 60, 80

HDR_X, HDR_Y, HDR_W, HDR_H = 0, 0, 480, 28
ROW_X, ROW_Y, ROW_W, ROW_H = 12, 36, 456, 28
ACT_X, ACT_Y, ACT_W, ACT_H = 12, 70, 456, 64

DGT_W, DGT_H = 28, 36
DGT_CELLS = 11                             # "0".."9" plus a blank at index 10
DGT_BLANK = 10

READ_LBL_X = 12                            # the three readout labels, baked into the background
READ_X = 170                               # where each readout's digits start
READ_PITCH = 30
HAND_Y = 146                               # phase 1: travel while his hand is on the wheel
AFTER_Y = 190                              # phase 2: travel after he lets go
MS_Y = 234                                 # phase 2: how long that took
HAND_COUNT = 4                             # up to 9999 ticks
AFTER_COUNT = 4                            # up to 9999 ticks
MS_COUNT = 5                               # up to 99999 ms, past the coast cap

FOOT_X, FOOT_Y, FOOT_W, FOOT_H = 12, 276, 456, 16

# Domain text baked into the static background -- MUST match test_bench_t0.spin2 (task 3578).
# The wheel named here is T0_MOTOR_BASE (PINS_P16_P31): the right board is at P16 (STEPHEN 2026-09-11).
WHEEL_TEXT = "RIGHT WHEEL (P16 BOARD)"
HEADER_TEXT = "T0-24 STOP-STATE HAND TEST"
FOOTER_TEXT = "S STARTS A ROW, SPACE ENDS A TURN -- CLICK THIS WINDOW FIRST -- PANIC: PULL THE PACK"

ROW_LABELS = [
    "ROW 1 - HOLD AT REST",
    "ROW 2 - COAST AT REST",
    "ROW 3 - E-STOP AT REST",
    "ROW 4 - POWERED FAULT, COAST MODE",
    "ROW 5 - POWERED FAULT, HOLD MODE",
    "ROW 6 - DRIVER COG STOPPED",
    "ALL ROWS DONE",
]

# Every action the operator is ever asked for. Each row names its own before it runs (overlay P1),
# and no action is ever implied by a row name alone.
ACTION_TEXTS = [
    "PRESS S TO START THIS ROW. HANDS OFF THE WHEEL UNTIL THIS PANEL SAYS TURN OR SPIN.",
    "SETTING THIS ROW UP -- HANDS OFF THE WHEEL.",
    "HANDS OFF -- THE %s SPINS UNDER POWER AND IS FAULTED ON PURPOSE. SPACE ABORTS." % WHEEL_TEXT,
    "TURN THE %s SLOWLY BY HAND, ABOUT HALF A TURN, THEN PRESS SPACE." % WHEEL_TEXT,
    "SPIN THE %s BRISKLY BY HAND, LET GO, AND PRESS SPACE AS YOU LET GO." % WHEEL_TEXT,
    "HANDS OFF -- MEASURING HOW FAR IT CARRIES ON.",
    "ROW DONE -- ITS READING IS BELOW.",
    "ALL SIX ROWS DONE. NOTHING MORE TO DO AT THE RIG.",
]

# ---------------------------------------------------------------- colours ---
C_PANEL   = (28, 32, 38)
C_WELL    = (12, 13, 16)
C_HDR     = (48, 40, 20)
C_TEXT    = (232, 236, 240)
C_DIM     = (120, 128, 138)
C_AMBER   = (240, 176, 48)

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

    # wells the two text layers blit into, so an un-blitted frame still looks deliberate
    d.rectangle([ROW_X, ROW_Y, ROW_X + ROW_W - 1, ROW_Y + ROW_H - 1], fill=C_WELL)
    d.rectangle([ACT_X, ACT_Y, ACT_X + ACT_W - 1, ACT_Y + ACT_H - 1], fill=C_WELL)

    # Each readout says in its own words WHEN it was taken, so no row's reading can be misread as
    # the other phase's: the left label names the quantity, the right one names the phase.
    note_x = READ_X + READ_PITCH * MS_COUNT + 10
    note_w = PANEL_W - note_x - 12
    for lbl_y, lbl, count, phase in ((HAND_Y, "HAND TICKS", HAND_COUNT, "WHILE YOU TURN IT"),
                                     (AFTER_Y, "AFTER TICKS", AFTER_COUNT, "ONCE YOU LET GO"),
                                     (MS_Y, "AFTER MS", MS_COUNT, "ONCE YOU LET GO")):
        left(d, (READ_LBL_X, lbl_y, READ_X - READ_LBL_X - 8, DGT_H), lbl,
             fit(d, "AFTER TICKS", 17, READ_X - READ_LBL_X - 8), C_DIM)
        readout_well(d, READ_X, lbl_y, count)
        left(d, (note_x, lbl_y, note_w, DGT_H), phase,
             fit(d, "WHILE YOU TURN IT", 13, note_w), C_DIM)

    d.text((FOOT_X, FOOT_Y), FOOTER_TEXT, font=fit(d, FOOTER_TEXT, 12, FOOT_W), fill=C_DIM)
    return img


def build_rows():
    img = Image.new("RGB", (ROW_W, ROW_H * len(ROW_LABELS)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(ROW_LABELS):
        centre(d, (0, i * ROW_H, ROW_W, ROW_H), text, fit(d, text, 21, ROW_W - 12), C_AMBER)
    return img


def build_actions():
    img = Image.new("RGB", (ACT_W, ACT_H * len(ACTION_TEXTS)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(ACTION_TEXTS):
        fnt, lines = fit_wrapped(d, text, 19, ACT_W - 16, ACT_H - 12)
        _, t, _, b = d.textbbox((0, 0), "Ag", font=fnt)
        line_h = (b - t) + 4
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


ASSETS = [
    ("t0s_bg.bmp", build_background),
    ("t0s_rows.bmp", build_rows),
    ("t0s_actions.bmp", build_actions),
    ("t0s_digits.bmp", build_digits),
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
