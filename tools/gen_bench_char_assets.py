#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for src/test_bench_char.spin2.

Follows the crop-and-overlay technique in DOCs/REF-NO-COMMIT/dbg-display-theory/,
as demonstrated by DOCs/REF-NO-COMMIT/test_dog_panel.spin2 (a panel known to work
on this bench). Layers are loaded once with `LAYER`; a frame is composed by
blitting opaque cells with `CROP` and then one `UPDATE`.

The layout constants below are the SINGLE SOURCE OF TRUTH: this script draws the
BMPs from them and prints a ready-to-paste Spin2 CON block of the same numbers,
so the artwork and the code cannot drift.

    python3 tools/gen_bench_char_assets.py            # write src/*.bmp, print the CON block
    python3 tools/gen_bench_char_assets.py --preview  # also write PNGs for visual check

DEBUG LAYER requires 24-bit uncompressed (BI_RGB) BMP with no alpha, which is
exactly what Pillow writes for an "RGB" image saved as .bmp.

Sprite cells are OPAQUE -- there is no alpha -- so every cell carries the same
background colour as the region it lands on, or the blit leaves a seam.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- layout ----
PANEL_W, PANEL_H = 640, 400
PANEL_POS_X, PANEL_POS_Y = 60, 80

HDR_X, HDR_Y, HDR_W, HDR_H = 0, 0, 640, 44
CAP_X, CAP_Y, CAP_W, CAP_H = 16, 52, 608, 48
MODE_X, MODE_Y = 16, 110
CHIP_X, CHIP_Y = 16, 286
LBL_W, LBL_H = 268, 44                     # one cell size, two destinations
DGT_X, DGT_Y, DGT_W, DGT_H = 16, 164, 72, 104
DGT_PITCH = 82
DGT_COUNT = 3                              # seconds can exceed 99 once held
BTN_X, BTN_Y, BTN_W, BTN_H = 300, 150, 316, 120
FOOT_X, FOOT_Y, FOOT_W, FOOT_H = 0, 340, 640, 60

CAP_CELLS = 9                              # one per hold
DGT_CELLS = 11                             # "0".."9" plus a blank at index 10
DGT_BLANK = 10
LBL_CELLS = 5                              # 0,1 mode  ·  2,3,4 status
BTN_CELLS = 3                              # inert · live · acknowledged

# ---------------------------------------------------------------- colours ---
C_BG        = (18, 20, 24)
C_PANEL     = (28, 32, 38)
C_WELL      = (12, 13, 16)
C_HDR       = (48, 40, 20)
C_TEXT      = (232, 236, 240)
C_DIM       = (120, 128, 138)
C_AMBER     = (240, 176, 48)
C_FLASH     = (255, 255, 255)
C_BTN_INERT = (42, 47, 54)
C_BTN_LIVE  = (39, 176, 63)
C_BTN_ACK   = (20, 104, 42)
C_OK        = (120, 200, 130)
C_WARN      = (230, 90, 70)

HOLDS = [
    "HOLD 1 of 9  -  QUIESCENT ZERO",
    "HOLD 2 of 9  -  LEFT WHEEL FORWARD  -  1/4 SPEED",
    "HOLD 3 of 9  -  LEFT WHEEL REVERSE  -  1/4 SPEED",
    "HOLD 4 of 9  -  RIGHT WHEEL FORWARD  -  1/4 SPEED",
    "HOLD 5 of 9  -  RIGHT WHEEL REVERSE  -  1/4 SPEED",
    "HOLD 6 of 9  -  LEFT WHEEL FORWARD  -  1/2 SPEED",
    "HOLD 7 of 9  -  LEFT WHEEL REVERSE  -  1/2 SPEED",
    "HOLD 8 of 9  -  RIGHT WHEEL FORWARD  -  1/2 SPEED",
    "HOLD 9 of 9  -  RIGHT WHEEL REVERSE  -  1/2 SPEED",
]
LABELS = [
    ("DWELL REMAINING", C_AMBER),
    ("HELD - SEC",      C_OK),
    ("ZERO COMMAND",    C_DIM),
    ("MOTOR RUNNING",   C_OK),
    ("DRIVER FAULT",    C_WARN),
]
BUTTONS = [
    ("GO AHEAD", "(WAIT)",       C_BTN_INERT, C_DIM,   (70, 78, 88)),
    ("GO AHEAD", "CLICK OR 'G'", C_BTN_LIVE,  C_TEXT,  (140, 240, 160)),
    ("ADVANCING", "",            C_BTN_ACK,   C_TEXT,  (30, 80, 45)),
]

FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
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
    """Largest font at or below `size` whose rendered text fits max_w.

    Guessing a point size and eyeballing the result is how text ends up clipped at
    the panel edge -- which happened on the first render of this very file. Measure
    instead; the cost is a few textbbox calls at build time.
    """
    while size > 8:
        f = font(size)
        l, _, r, _ = d.textbbox((0, 0), text, font=f)
        if (r - l) <= max_w:
            return f
        size -= 1
    return font(8)


def centre(d, box, text, fnt, fill):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + (w - (r - l)) / 2 - l, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


def left(d, box, text, fnt, fill, pad=10):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + pad, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


def build_background():
    img = Image.new("RGB", (PANEL_W, PANEL_H), C_PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle([HDR_X, HDR_Y, HDR_X + HDR_W - 1, HDR_Y + HDR_H - 1], fill=C_HDR)
    hdr = "BENCH CHARACTERISATION  --  HOLD FOR METER READ"
    centre(d, (HDR_X, HDR_Y, HDR_W, HDR_H), hdr, fit(d, hdr, 22, HDR_W - 24), C_TEXT)
    # wells the dynamic cells land in, so an un-blitted frame still looks deliberate
    for box in [(CAP_X, CAP_Y, CAP_W, CAP_H),
                (MODE_X, MODE_Y, LBL_W, LBL_H),
                (CHIP_X, CHIP_Y, LBL_W, LBL_H),
                (DGT_X, DGT_Y, DGT_PITCH * DGT_COUNT - (DGT_PITCH - DGT_W), DGT_H),
                (BTN_X, BTN_Y, BTN_W, BTN_H)]:
        d.rectangle([box[0], box[1], box[0] + box[2] - 1, box[1] + box[3] - 1], fill=C_WELL)
    d.rectangle([FOOT_X, FOOT_Y, FOOT_X + FOOT_W - 1, FOOT_Y + FOOT_H - 1], fill=C_BG)
    l1 = "WRITE DOWN the AMPS reading for this row, then click GO AHEAD."
    l2 = "Keyboard: G (needs focus).   PANIC: DISCONNECT THE BATTERY."
    d.text((16, FOOT_Y + 8),  l1, font=fit(d, l1, 17, FOOT_W - 32), fill=C_TEXT)
    d.text((16, FOOT_Y + 32), l2, font=fit(d, l2, 17, FOOT_W - 32), fill=C_DIM)
    return img


def build_captions():
    img = Image.new("RGB", (CAP_W, CAP_H * CAP_CELLS), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(HOLDS):
        left(d, (0, i * CAP_H, CAP_W, CAP_H), text, fit(d, text, 24, CAP_W - 24), C_TEXT)
    return img


def build_digits():
    """Two colour rows: 0 = amber (normal), 1 = white (early-press flash)."""
    img = Image.new("RGB", (DGT_W * DGT_CELLS, DGT_H * 2), C_WELL)
    d = ImageDraw.Draw(img)
    f = font(88)
    for row, colour in ((0, C_AMBER), (1, C_FLASH)):
        for i in range(10):
            centre(d, (i * DGT_W, row * DGT_H, DGT_W, DGT_H), str(i), f, colour)
        # index 10 stays blank -- used to suppress a leading zero
    return img


def build_labels():
    img = Image.new("RGB", (LBL_W, LBL_H * LBL_CELLS), C_WELL)
    d = ImageDraw.Draw(img)
    for i, (text, colour) in enumerate(LABELS):
        centre(d, (0, i * LBL_H, LBL_W, LBL_H), text, fit(d, text, 21, LBL_W - 16), colour)
    return img


def build_buttons():
    img = Image.new("RGB", (BTN_W, BTN_H * BTN_CELLS), C_WELL)
    d = ImageDraw.Draw(img)
    big, small = font(38), font(17)
    for i, (top, sub, fill, tcol, border) in enumerate(BUTTONS):
        y = i * BTN_H
        d.rectangle([0, y, BTN_W - 1, y + BTN_H - 1], fill=fill, outline=border, width=3)
        if sub:
            centre(d, (0, y + 8, BTN_W, BTN_H - 40), top, big, tcol)
            centre(d, (0, y + BTN_H - 42, BTN_W, 32), sub, small, tcol)
        else:
            centre(d, (0, y, BTN_W, BTN_H), top, big, tcol)
    return img


ASSETS = [
    ("bc_bg.bmp",      build_background),
    ("bc_caption.bmp", build_captions),
    ("bc_digits.bmp",  build_digits),
    ("bc_labels.bmp",  build_labels),
    ("bc_button.bmp",  build_buttons),
]

CON_BLOCK = f"""
CON {{ panel geometry -- GENERATED by tools/gen_bench_char_assets.py, do not hand-edit }}

    PANEL_W          = {PANEL_W}
    PANEL_H          = {PANEL_H}
    PANEL_POS_X      = {PANEL_POS_X}
    PANEL_POS_Y      = {PANEL_POS_Y}

    LYR_BG           = 1
    LYR_CAP          = 2
    LYR_DGT          = 3
    LYR_LBL          = 4
    LYR_BTN          = 5

    CAP_X            = {CAP_X}
    CAP_Y            = {CAP_Y}
    CAP_W            = {CAP_W}
    CAP_H            = {CAP_H}

    MODE_X           = {MODE_X}
    MODE_Y           = {MODE_Y}
    CHIP_X           = {CHIP_X}
    CHIP_Y           = {CHIP_Y}
    LBL_W            = {LBL_W}
    LBL_H            = {LBL_H}

    DGT_X            = {DGT_X}
    DGT_Y            = {DGT_Y}
    DGT_W            = {DGT_W}
    DGT_H            = {DGT_H}
    DGT_PITCH        = {DGT_PITCH}
    DGT_COUNT        = {DGT_COUNT}
    DGT_BLANK        = {DGT_BLANK}
    DGT_ROW_NORM     = 0
    DGT_ROW_FLASH    = {DGT_H}

    BTN_X            = {BTN_X}
    BTN_Y            = {BTN_Y}
    BTN_W            = {BTN_W}
    BTN_H            = {BTN_H}

    LBL_MODE_DWELL   = 0
    LBL_MODE_HELD    = 1
    LBL_STAT_ZERO    = 2
    LBL_STAT_RUN     = 3
    LBL_STAT_FAULT   = 4

    BTN_INERT        = 0
    BTN_LIVE         = 1
    BTN_ACK          = 2
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
