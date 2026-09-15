#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for src/test_bench_dual.spin2's operator panel (window bmpanel), drawn
by the attended OUTSIDE segment (-D DUAL_PART_BRAKE, bench-run.sh tier dual-brake) and FLOOR segment
(-D DUAL_PART_FLOOR, tier dual-floor), and by the no-motor-control UICHECK walkthrough (-D DUAL_PART_UICHECK,
tier dual-ui) -- DOCs/plans/MOTION-HARNESS-DESIGN.md sec 8.2 and 8.3.

Structured exactly like tools/gen_t0hand_assets.py, and follows the same crop-and-overlay technique in
DOCs/REF-NO-COMMIT/dbg-display-theory/: layers are loaded once with LAYER; a frame is composed by
blitting opaque cells with CROP and then one UPDATE. The layout constants below are the SINGLE SOURCE OF
TRUTH -- this script draws the BMPs from them and prints a ready-to-paste Spin2 CON block of the same
numbers, so the artwork and the code cannot drift. The BM_* block in test_bench_dual.spin2 is
byte-for-byte what con_block() prints; if a constant here changes, re-run this script and re-paste.

    python3 tools/gen_dual_assets.py            # write src/bm_*.bmp, print the CON block
    python3 tools/gen_dual_assets.py --preview  # also write PNGs for visual check

Layers (the Spin2 LAYER numbers):
    1 bm_bg.bmp       header, prompt well, state well, countdown well, empty button frames, footer
    2 bm_prompt.bmp   one prompt cell per row (PROMPT_W x PROMPT_H): every sec 8.3 prompt string
    3 bm_state.bmp    one state word per row (STATE_W x STATE_H)
    4 bm_buttons.bmp  one button per row; column 0 normal (live), column 1 highlighted (chosen)
    5 bm_digits.bmp   "0".."9" plus a blank at index 10, for the 3-digit countdown

DEBUG LAYER requires 24-bit uncompressed (BI_RGB) BMP with no alpha, which is exactly what Pillow
writes for an "RGB" image saved as .bmp.

Sprite cells are OPAQUE -- there is no alpha -- so every cell carries the same background colour as
the region it lands on, or the blit leaves a seam. A button slot is erased by restoring it from
layer 1, whose empty frame is drawn at exactly the slot rectangle.

The .bmp outputs are committed beside the source, and the printed CON block is compared with the one in
test_bench_dual.spin2 whenever this script is re-run (design sec 12.1 Q6, sec 12.9). Whether the panel
draws and takes input is shown on the rig by the dual-ui walkthrough, which runs before dual-brake and
dual-floor (STEPHEN 2026-09-15).
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- layout ----
# Keep these numbers identical to test_bench_dual.spin2's BM_* CON block (con_block() prints it).
PANEL_W, PANEL_H = 480, 260
PANEL_POS_X, PANEL_POS_Y = 60, 80

LYR_BG, LYR_PROMPT, LYR_STATE, LYR_BUTTONS, LYR_DIGITS = 1, 2, 3, 4, 5

HDR_X, HDR_Y, HDR_W, HDR_H = 0, 0, 480, 28
PROMPT_X, PROMPT_Y, PROMPT_W, PROMPT_H = 12, 34, 456, 76
STATE_X, STATE_Y, STATE_W, STATE_H = 12, 116, 300, 32
CD_LBL_X, CD_LBL_Y, CD_LBL_W, CD_LBL_H = 320, 116, 80, 32
CD_X, CD_Y = 404, 116
CD_COUNT = 3                               # up to 999 seconds
CD_TOP_DIV = 10 ** (CD_COUNT - 1)          # place value of the leftmost countdown digit

DGT_W, DGT_H = 20, 32
DGT_CELLS = 11                             # "0".."9" plus a blank at index 10
DGT_BLANK = 10

BTN_W, BTN_H = 108, 36
BTN_COL0_X, BTN_PITCH = 12, 116
BTN_ROW1_Y, BTN_ROW2_Y = 156, 198
BTN_ROW2_FIRST = 3                         # buttons 0..2 on row 1, 3..6 on row 2
BTN_NORMAL, BTN_HILITE = 0, 1              # column in bm_buttons.bmp
BTN_VARIANTS = 2

FOOT_X, FOOT_Y, FOOT_W, FOOT_H = 12, 240, 456, 18
CELL_PAD = 8

# Domain values baked into the prompt text -- MUST match test_bench_dual.spin2's FLOOR_RUN_MS / 1_000,
# FLOOR_POWER and FLOOR_DIRECTION, and "HALF POWER" its STEER_POWER_HALF (50). Regenerate if any changes.
FLOOR_RUN_S = 2                            # a brief turn-direction observation (design sec 12.1 Q10)
FLOOR_POWER = 50
FLOOR_DIRECTION = 50

# Prompt cells, in BM_PROMPT_* order, ASCII only. The first five are design sec 8.3's prompts; the rest were
# added 2026-09-15 for "a very careful working user interface" (STEPHEN): the braked wheel is named by its
# board (the LEFT board is at P32, MEASURED 2026-09-11), the operator is told before the harness drives the
# wheels again, and the UICHECK walkthrough has its own prompts.
(PROMPT_BRAKE_START, PROMPT_BRAKE_NOW, PROMPT_BRAKE_RELEASE, PROMPT_FLOOR_START, PROMPT_FLOOR_ASK,
 PROMPT_BRAKE_RUNNING, PROMPT_UI_CLICK, PROMPT_UI_KEY, PROMPT_UI_PREVIEW, PROMPT_UI_END) = range(10)
PROMPTS = [
    "HANDS CLEAR. CLICK START: BOTH WHEELS RUN AT HALF POWER, THEN THE PANEL TELLS YOU TO BRAKE THE LEFT "
    "WHEEL (P32 BOARD).",
    "BRAKE THE LEFT WHEEL (P32 BOARD) NOW -- HOLD IT UNTIL THE PANEL SAYS RELEASE.",
    "RELEASE THE WHEEL AND STEP BACK. KEEP HANDS CLEAR: THE HARNESS DRIVES BOTH WHEELS AGAIN WHEN THE "
    "COUNTDOWN ENDS.",
    "PLATFORM ON THE FLOOR, SPACE CLEAR. CLICK START: IT DRIVES ABOUT %d SECONDS, POWER %d, DIRECTION %+d. "
    "CLICK STOP OR PRESS SPACE ANY TIME." % (FLOOR_RUN_S, FLOOR_POWER, FLOOR_DIRECTION),
    "WHICH WAY DID IT TURN?",
    "HANDS CLEAR -- THE HARNESS IS DRIVING BOTH WHEELS AGAIN BY ITSELF. WAIT FOR DONE.",
    "UI CHECK -- NO MOTOR RUNS. CLICK THE ONE BUTTON SHOWN, WITH THE MOUSE.",
    "UI CHECK -- NO MOTOR RUNS. PRESS THE KEY NAMED ON THE ONE BUTTON SHOWN.",
    "UI CHECK -- NO MOTOR RUNS. EACH ATTENDED SCREEN COMES NEXT: CLICK START IF IT READS RIGHT, SKIP IF "
    "ANYTHING IS WRONG. CLICK START TO BEGIN.",
    "UI CHECK FINISHED -- NO MOTOR RAN. THE RESULT IS BELOW. CLICK START TO CLOSE.",
]

# State words, in BM_STATE_* order (design sec 8.2; the last four added 2026-09-15 with the prompts above).
(STATE_WAITING, STATE_STARTING, STATE_BRAKE_NOW, STATE_RELEASE, STATE_OBSERVING, STATE_ASK,
 STATE_DONE, STATE_SKIPPED, STATE_TIMED_OUT, STATE_WHEELS_AGAIN, STATE_UI_CHECK, STATE_UI_PASSED,
 STATE_UI_FAILED) = range(13)
STATE_LABELS = [
    "WAITING FOR START",
    "STARTING",
    "BRAKE THE LEFT WHEEL NOW",
    "RELEASE THE WHEEL",
    "OBSERVING",
    "WHICH WAY DID IT TURN?",
    "DONE",
    "SKIPPED",
    "TIMED OUT",
    "HANDS CLEAR - WHEELS RUN",
    "UI CHECK - NOTHING MOVES",
    "UI CHECK PASSED",
    "UI CHECK FAILED",
]

# Buttons, in BM_BTN_* order: (label, key hint). The keys are test_bench_dual.spin2's keyButton() map.
BTN_START, BTN_SKIP, BTN_STOP, BTN_LEFT, BTN_RIGHT, BTN_STRAIGHT, BTN_NOMOVE = range(7)
BUTTONS = [
    ("START", "KEY S"),
    ("SKIP", "KEY K"),
    ("STOP", "SPACE BAR"),
    ("LEFT", "KEY L"),
    ("RIGHT", "KEY R"),
    ("STRAIGHT", "KEY T"),
    ("DID NOT MOVE", "KEY N"),
]

HEADER_TEXT = "MOTION HARNESS -- OPERATOR PANEL"
CD_LABEL_TEXT = "SECONDS"
FOOTER_TEXT = "CLICK THIS WINDOW FIRST -- PANIC: DISCONNECT THE BATTERY"

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


def left(d, box, text, fnt, fill, pad=0):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((x + pad, y + (h - (b - t)) / 2 - t), text, font=fnt, fill=fill)


def slot(btn_idx):
    """Top-left of a button's slot on the panel -- the same arithmetic as test_bench_dual.spin2's
    buttonSlot(), and the bounding box its mouseButton() hit-tests."""
    if btn_idx >= BTN_ROW2_FIRST:
        return BTN_COL0_X + (btn_idx - BTN_ROW2_FIRST) * BTN_PITCH, BTN_ROW2_Y
    return BTN_COL0_X + btn_idx * BTN_PITCH, BTN_ROW1_Y


def check_layout():
    """Refuse to write assets whose tables or geometry disagree with the constants."""
    assert len(PROMPTS) == PROMPT_UI_END + 1, "PROMPTS does not match the BM_PROMPT_* indices"
    assert len(STATE_LABELS) == STATE_UI_FAILED + 1, "STATE_LABELS does not match the BM_STATE_* indices"
    assert len(BUTTONS) == BTN_NOMOVE + 1, "BUTTONS does not match the BM_BTN_* indices"
    for text in PROMPTS + STATE_LABELS + [HEADER_TEXT, CD_LABEL_TEXT, FOOTER_TEXT]:
        assert all(ord(ch) < 128 for ch in text), "non-ASCII panel text: %r" % text
    for idx in range(len(BUTTONS)):
        x, y = slot(idx)
        assert x + BTN_W <= PANEL_W and y + BTN_H <= FOOT_Y, "button %d slot leaves its area" % idx
    assert PROMPT_Y + PROMPT_H <= STATE_Y, "prompt well overlaps the state row"
    assert STATE_X + STATE_W <= CD_LBL_X, "state well overlaps the countdown label"
    assert CD_LBL_X + CD_LBL_W <= CD_X, "countdown label overlaps the digits"
    assert CD_X + CD_COUNT * DGT_W <= PANEL_W, "countdown digits leave the panel"
    assert STATE_Y + STATE_H <= BTN_ROW1_Y, "state row overlaps the buttons"
    assert FOOT_Y + FOOT_H <= PANEL_H, "footer leaves the panel"


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
    centre(d, (HDR_X, HDR_Y, HDR_W, HDR_H), HEADER_TEXT, fit(d, HEADER_TEXT, 18, HDR_W - 16), C_TEXT)

    # wells the prompt, state and digit cells blit into, so an un-blitted frame still looks deliberate
    d.rectangle([PROMPT_X, PROMPT_Y, PROMPT_X + PROMPT_W - 1, PROMPT_Y + PROMPT_H - 1], fill=C_WELL)
    d.rectangle([STATE_X, STATE_Y, STATE_X + STATE_W - 1, STATE_Y + STATE_H - 1], fill=C_WELL)
    left(d, (CD_LBL_X, CD_LBL_Y, CD_LBL_W, CD_LBL_H), CD_LABEL_TEXT, fit(d, CD_LABEL_TEXT, 14, CD_LBL_W), C_DIM)
    d.rectangle([CD_X, CD_Y, CD_X + CD_COUNT * DGT_W - 1, CD_Y + DGT_H - 1], fill=C_WELL)

    # empty button frames: exactly each slot rectangle, so restoring a slot from this layer erases it
    for idx in range(len(BUTTONS)):
        x, y = slot(idx)
        d.rectangle([x, y, x + BTN_W - 1, y + BTN_H - 1], fill=C_PANEL, outline=C_FRAME)

    d.text((FOOT_X, FOOT_Y), FOOTER_TEXT, font=fit(d, FOOTER_TEXT, 13, FOOT_W), fill=C_AMBER)
    return img


def build_prompts():
    img = Image.new("RGB", (PROMPT_W, PROMPT_H * len(PROMPTS)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(PROMPTS):
        f, lines, line_h = fit_wrapped(d, text, 18, PROMPT_W - 2 * CELL_PAD, PROMPT_H - 2 * CELL_PAD)
        top = i * PROMPT_H + (PROMPT_H - line_h * len(lines)) // 2
        for n, ln in enumerate(lines):
            l, t, _, _ = d.textbbox((0, 0), ln, font=f)
            d.text((CELL_PAD - l, top + n * line_h - t), ln, font=f, fill=C_TEXT)
    return img


def build_state():
    img = Image.new("RGB", (STATE_W, STATE_H * len(STATE_LABELS)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, text in enumerate(STATE_LABELS):
        centre(d, (0, i * STATE_H, STATE_W, STATE_H), text, fit(d, text, 20, STATE_W - 12), C_AMBER)
    return img


def build_buttons():
    img = Image.new("RGB", (BTN_W * BTN_VARIANTS, BTN_H * len(BUTTONS)), C_PANEL)
    d = ImageDraw.Draw(img)
    for i, (label, key) in enumerate(BUTTONS):
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


ASSETS = [
    ("bm_bg.bmp",      build_background),
    ("bm_prompt.bmp",  build_prompts),
    ("bm_state.bmp",   build_state),
    ("bm_buttons.bmp", build_buttons),
    ("bm_digits.bmp",  build_digits),
]

# One group per blank-line-separated run of the printed CON block.
CON_GROUPS = [
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
    ],
    [
        ("BM_PROMPT_X", PROMPT_X),
        ("BM_PROMPT_Y", PROMPT_Y),
        ("BM_PROMPT_W", PROMPT_W),
        ("BM_PROMPT_H", PROMPT_H),
        ("BM_PROMPT_BRAKE_START", PROMPT_BRAKE_START),
        ("BM_PROMPT_BRAKE_NOW", PROMPT_BRAKE_NOW),
        ("BM_PROMPT_BRAKE_RELEASE", PROMPT_BRAKE_RELEASE),
        ("BM_PROMPT_FLOOR_START", PROMPT_FLOOR_START),
        ("BM_PROMPT_FLOOR_ASK", PROMPT_FLOOR_ASK),
        ("BM_PROMPT_BRAKE_RUNNING", PROMPT_BRAKE_RUNNING),
        ("BM_PROMPT_UI_CLICK", PROMPT_UI_CLICK),
        ("BM_PROMPT_UI_KEY", PROMPT_UI_KEY),
        ("BM_PROMPT_UI_PREVIEW", PROMPT_UI_PREVIEW),
        ("BM_PROMPT_UI_END", PROMPT_UI_END),
    ],
    [
        ("BM_STATE_X", STATE_X),
        ("BM_STATE_Y", STATE_Y),
        ("BM_STATE_W", STATE_W),
        ("BM_STATE_H", STATE_H),
        ("BM_STATE_WAITING", STATE_WAITING),
        ("BM_STATE_STARTING", STATE_STARTING),
        ("BM_STATE_BRAKE_NOW", STATE_BRAKE_NOW),
        ("BM_STATE_RELEASE", STATE_RELEASE),
        ("BM_STATE_OBSERVING", STATE_OBSERVING),
        ("BM_STATE_ASK", STATE_ASK),
        ("BM_STATE_DONE", STATE_DONE),
        ("BM_STATE_SKIPPED", STATE_SKIPPED),
        ("BM_STATE_TIMED_OUT", STATE_TIMED_OUT),
        ("BM_STATE_WHEELS_AGAIN", STATE_WHEELS_AGAIN),
        ("BM_STATE_UI_CHECK", STATE_UI_CHECK),
        ("BM_STATE_UI_PASSED", STATE_UI_PASSED),
        ("BM_STATE_UI_FAILED", STATE_UI_FAILED),
    ],
    [
        ("BM_BTN_W", BTN_W),
        ("BM_BTN_H", BTN_H),
        ("BM_BTN_COL0_X", BTN_COL0_X),
        ("BM_BTN_PITCH", BTN_PITCH),
        ("BM_BTN_ROW1_Y", BTN_ROW1_Y),
        ("BM_BTN_ROW2_Y", BTN_ROW2_Y),
        ("BM_BTN_ROW2_FIRST", BTN_ROW2_FIRST),
        ("BM_BTN_NORMAL", BTN_NORMAL),
        ("BM_BTN_HILITE", BTN_HILITE),
        ("BM_BTN_START", BTN_START),
        ("BM_BTN_SKIP", BTN_SKIP),
        ("BM_BTN_STOP", BTN_STOP),
        ("BM_BTN_LEFT", BTN_LEFT),
        ("BM_BTN_RIGHT", BTN_RIGHT),
        ("BM_BTN_STRAIGHT", BTN_STRAIGHT),
        ("BM_BTN_NOMOVE", BTN_NOMOVE),
        ("BM_BTN_COUNT", len(BUTTONS)),
    ],
    [
        ("BM_DGT_W", DGT_W),
        ("BM_DGT_H", DGT_H),
        ("BM_DGT_BLANK", DGT_BLANK),
        ("BM_CD_X", CD_X),
        ("BM_CD_Y", CD_Y),
        ("BM_CD_COUNT", CD_COUNT),
        ("BM_CD_TOP_DIV", CD_TOP_DIV),
    ],
]


def con_block():
    out = ["", "CON { operator panel geometry -- GENERATED by tools/gen_dual_assets.py, do not hand-edit }"]
    for group in CON_GROUPS:
        out.append("")
        for name, value in group:
            out.append("    %-24s= %d" % (name, value))
    out.append("")
    return "\n".join(out)


def main():
    check_layout()
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
    print(con_block())


if __name__ == "__main__":
    main()
