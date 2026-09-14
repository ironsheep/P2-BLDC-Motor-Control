#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for src/test_bench_t0.spin2's T0-12 hand-rotation panel
(-D T0_HAND, bench-run.sh tier t0-hand).

Follows the crop-and-overlay technique in DOCs/REF-NO-COMMIT/dbg-display-theory/, the same
discipline tools/gen_bench_char_assets.py used for the (since-removed) characterisation panel:
layers are loaded once with LAYER; a frame is composed by blitting opaque cells with CROP and
then one UPDATE. The layout constants below are the SINGLE SOURCE OF TRUTH -- this script draws
the BMPs from them and prints a ready-to-paste Spin2 CON block of the same numbers, so the
artwork and the code cannot drift. The T0H_* block already pasted into test_bench_t0.spin2 was
computed by hand from these same numbers (task 3542) -- if this script's constants ever change,
re-run it and re-paste, exactly as gen_bench_char_assets.py's own header instructs.

    python3 tools/gen_t0hand_assets.py            # write src/t0h_*.bmp, print the CON block
    python3 tools/gen_t0hand_assets.py --preview  # also write PNGs for visual check

DEBUG LAYER requires 24-bit uncompressed (BI_RGB) BMP with no alpha, which is exactly what
Pillow writes for an "RGB" image saved as .bmp.

Sprite cells are OPAQUE -- there is no alpha -- so every cell carries the same background colour
as the region it lands on, or the blit leaves a seam.

NOT RUN as part of task 3542: that task's tool rules permitted no shell invocation of any kind,
so this script is authored but its .bmp outputs do not exist in the tree yet. Run it (and then
compile with the t0-hand tier) before relying on T0-12's panel actually rendering.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- layout ----
# Keep these numbers identical to test_bench_t0.spin2's T0H_* CON block (task 3542).
PANEL_W, PANEL_H = 420, 240
PANEL_POS_X, PANEL_POS_Y = 60, 80

HDR_X, HDR_Y, HDR_W, HDR_H = 0, 0, 420, 32
PROMPT_X, PROMPT_Y, PROMPT_W, PROMPT_H = 12, 40, 396, 56
STATE_X, STATE_Y, STATE_W, STATE_H = 12, 104, 200, 32
TRANS_LBL_X, TRANS_LBL_Y = 12, 144
TRANS_X, TRANS_Y = 140, 140
TRANS_PITCH = 34
TRANS_COUNT = 4                            # up to 9999 transitions
ILL_LBL_X, ILL_LBL_Y = 12, 188
ILL_X, ILL_Y = 140, 184
ILL_PITCH = 34
ILL_COUNT = 3                              # up to 999 illegal-code entries
FOOT_X, FOOT_Y, FOOT_W, FOOT_H = 12, 220, 396, 16

DGT_W, DGT_H = 32, 40
DGT_CELLS = 11                             # "0".."9" plus a blank at index 10
DGT_BLANK = 10

STATE_CELLS = 3                            # WAITING TO START / COUNTING / DONE
STATE_WAITING, STATE_COUNTING, STATE_DONE = 0, 1, 2

# Domain text baked into the static background -- MUST match test_bench_t0.spin2's
# T0_12_REVOLUTIONS / T0_12_TOLD_CCW (task 3542). Regenerate this asset if either changes.
REVOLUTIONS = 3
TOLD_DIRECTION = "CW (viewed from hub)"    # fixed: the panel bakes it in, and one known direction plus the
                                           # signed tick change answers PL-39, so there is no CCW build to mismatch

# ---------------------------------------------------------------- colours ---
C_BG      = (18, 20, 24)
C_PANEL   = (28, 32, 38)
C_WELL    = (12, 13, 16)
C_HDR     = (48, 40, 20)
C_TEXT    = (232, 236, 240)
C_DIM     = (120, 128, 138)
C_AMBER   = (240, 176, 48)

STATE_LABELS = ["WAITING TO START", "COUNTING", "DONE"]

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
    """Largest font at or below `size` whose rendered text fits max_w. Measured, not guessed --
    see gen_bench_char_assets.py's own note on why a guessed size clips at the panel edge."""
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


def left(d, box, text, fnt, fill, pad=0):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + pad, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


def build_background():
    img = Image.new("RGB", (PANEL_W, PANEL_H), C_PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle([HDR_X, HDR_Y, HDR_X + HDR_W - 1, HDR_Y + HDR_H - 1], fill=C_HDR)
    hdr = "T0-12 HAND-ROTATION ANCHOR"
    centre(d, (HDR_X, HDR_Y, HDR_W, HDR_H), hdr, fit(d, hdr, 20, HDR_W - 16), C_TEXT)

    l1 = "TURN THE TEST WHEEL BY HAND, %s," % TOLD_DIRECTION.upper()
    l2 = "EXACTLY %d FULL REVOLUTION%s." % (REVOLUTIONS, "" if REVOLUTIONS == 1 else "S")
    d.text((PROMPT_X, PROMPT_Y), l1, font=fit(d, l1, 16, PROMPT_W), fill=C_TEXT)
    d.text((PROMPT_X, PROMPT_Y + 26), l2, font=fit(d, l2, 16, PROMPT_W), fill=C_TEXT)

    # well the state word blits into, so an un-blitted frame still looks deliberate
    d.rectangle([STATE_X, STATE_Y, STATE_X + STATE_W - 1, STATE_Y + STATE_H - 1], fill=C_WELL)

    left(d, (TRANS_LBL_X, TRANS_LBL_Y, 120, 32), "TRANSITIONS", fit(d, "TRANSITIONS", 16, 120), C_DIM)
    d.rectangle([TRANS_X, TRANS_Y, TRANS_X + TRANS_PITCH * TRANS_COUNT - 1, TRANS_Y + DGT_H - 1], fill=C_WELL)

    left(d, (ILL_LBL_X, ILL_LBL_Y, 120, 32), "ILLEGAL", fit(d, "ILLEGAL", 16, 120), C_DIM)
    d.rectangle([ILL_X, ILL_Y, ILL_X + ILL_PITCH * ILL_COUNT - 1, ILL_Y + DGT_H - 1], fill=C_WELL)

    foot = "PRESS ANY KEY TO START, THEN AGAIN TO STOP (WINDOW NEEDS FOCUS)"
    d.text((FOOT_X, FOOT_Y), foot, font=fit(d, foot, 13, FOOT_W), fill=C_DIM)
    return img


def build_state():
    img = Image.new("RGB", (STATE_W, STATE_H * STATE_CELLS), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(STATE_LABELS):
        centre(d, (0, i * STATE_H, STATE_W, STATE_H), text, fit(d, text, 22, STATE_W - 12), C_AMBER)
    return img


def build_digits():
    img = Image.new("RGB", (DGT_W * DGT_CELLS, DGT_H), C_WELL)
    d = ImageDraw.Draw(img)
    f = font(30)
    for i in range(10):
        centre(d, (i * DGT_W, 0, DGT_W, DGT_H), str(i), f, C_TEXT)
    # index 10 stays blank -- used to suppress a leading zero
    return img


ASSETS = [
    ("t0h_bg.bmp",    build_background),
    ("t0h_state.bmp", build_state),
    ("t0h_digits.bmp", build_digits),
]

CON_BLOCK = f"""
CON {{ T0-12 panel geometry -- GENERATED by tools/gen_t0hand_assets.py, do not hand-edit }}

    T0H_PANEL_W       = {PANEL_W}
    T0H_PANEL_H       = {PANEL_H}
    T0H_PANEL_POS_X   = {PANEL_POS_X}
    T0H_PANEL_POS_Y   = {PANEL_POS_Y}

    T0H_LYR_BG        = 1
    T0H_LYR_STATE     = 2
    T0H_LYR_DGT       = 3

    T0H_STATE_X       = {STATE_X}
    T0H_STATE_Y       = {STATE_Y}
    T0H_STATE_W       = {STATE_W}
    T0H_STATE_H       = {STATE_H}
    T0H_STATE_WAITING = {STATE_WAITING}
    T0H_STATE_COUNTING = {STATE_COUNTING}
    T0H_STATE_DONE    = {STATE_DONE}

    T0H_DGT_W         = {DGT_W}
    T0H_DGT_H         = {DGT_H}
    T0H_DGT_BLANK     = {DGT_BLANK}

    T0H_TRANS_X       = {TRANS_X}
    T0H_TRANS_Y       = {TRANS_Y}
    T0H_TRANS_PITCH   = {TRANS_PITCH}
    T0H_TRANS_COUNT   = {TRANS_COUNT}

    T0H_ILL_X         = {ILL_X}
    T0H_ILL_Y         = {ILL_Y}
    T0H_ILL_PITCH     = {ILL_PITCH}
    T0H_ILL_COUNT     = {ILL_COUNT}
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
