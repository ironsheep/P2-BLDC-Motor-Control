#!/usr/bin/env python3
"""Generate the DEBUG PLOT assets for the floor run's COUNTDOWN BOARD (window fboard) in src/test_bench_dual.spin2,
drawn by part SPIN (-D DUAL_PART_SPIN, tools/bench-run.sh tier dual-spin) from SRC_REV 65.

WHY IT EXISTS. Stephen, 2026-09-29: "I'll be 4 ft away from the monitor telling me what to do when i'm at the platform...
so there can't be any interaction by me with the plot window after the test is running... i'll need to know before test
starts what to look for to know when to interact. a timer-countdown with large numbers could tell me when to interact."
So after ONE START (on the operator panel, bmpanel), this board is the only instruction: the situation's name, ONE action
word in a colour that says whether it is his move or the platform's, a countdown in seconds large enough to read at 4 ft,
the step's detail in plain words, and a small readout (the held wheel's speed during GRAB, the leg number during SPINS).
Nothing on it is clicked. A step he takes part in ends on a timer he agreed (2026-09-29) or on the wheels' own sensors.

Built on the supplied crop-and-overlay technique (DOCs/REF-NO-COMMIT/dbg-display-theory/, read in full 2026-09-29) and
DOCs/procedures/PLOT-DISPLAY-RULES.md, exactly as tools/gen_dual_assets.py builds bmpanel: every layer is loaded once
with LAYER; a frame restores the changing region from layer 1, blits opaque cells with CROP, then one UPDATE. The
layout and THE STEP TABLE below are the SINGLE SOURCE OF TRUTH: this script draws the BMPs from them and prints the
Spin2 CON block and DAT step table of the same numbers, so art, code and run sheet cannot drift.

    python3 tools/gen_floor_assets.py              # write src/fb_*.bmp, print CON + DAT
    python3 tools/gen_floor_assets.py --preview    # also write one PNG per step (every screen, in order) for the review

Layers (the Spin2 LAYER numbers):
    1 fb_bg.bmp      the whole board, empty: name band, action band, detail well, readout well, digit wells, footer
    2 fb_name.bmp    one situation name per row (NAME_W x NAME_H)
    3 fb_action.bmp  one action word per row, on its own colour (ACT_W x ACT_H)
    4 fb_detail.bmp  one detail cell per STEP (DET_W x DET_H)
    5 fb_big.bmp     "0".."9" plus a blank at index 10, the big countdown
    6 fb_small.bmp   "0".."9" plus a blank at index 10, the small readout
    7 fb_slabel.bmp  one readout label per kind; row 0 blank
    8 fb_brief.bmp   the briefing, over the whole lower area, shown until START

DEBUG LAYER needs 24-bit, uncompressed, no-alpha BMP: what Pillow writes for an "RGB" image saved as .bmp. Cells are
opaque, so each carries the background of the region it lands on.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
PREVIEW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist", "fboard-preview")

# ----------------------------------------------------------------- layout ---
W, H = 1000, 620                              # the window, SIZE W H
POS_X, POS_Y = 560, 40                        # where it opens, clear of bmpanel (POS 60 80, 480 x 306)
NAME_X, NAME_Y, NAME_W, NAME_H = 0, 0, W, 90
ACT_X, ACT_Y, ACT_W, ACT_H = 0, 96, W, 170
LOW_Y = 276                                   # the lower area: restored from layer 1 before every frame
LOW_H = H - LOW_Y
DET_X, DET_Y, DET_W, DET_H = 16, 286, 500, 250
SLBL_X, SLBL_Y, SLBL_W, SLBL_H = 16, 546, 330, 64
SDG_X, SDG_Y, SDG_W, SDG_H = 350, 546, 48, 64
SDG_COUNT = 3
BIG_W, BIG_H = 215, 300
BIG_COUNT = 2                                 # up to 99 s: every step's own countdown is 60 s or less
BIG_X, BIG_Y = W - 20 - BIG_COUNT * BIG_W, 290
DGT_CELLS, DGT_BLANK = 11, 10

# ---------------------------------------------------------------- colours ---
C_PANEL = (22, 26, 32)
C_WELL = (10, 11, 14)
C_TEXT = (240, 242, 245)
C_DIM = (130, 138, 148)
C_NAME_BG = (44, 38, 20)
C_DIGIT = (255, 214, 64)

# action classes: what the colour tells him from 4 ft
ACT_CLASSES = {
    "YOU":   ((250, 196, 36), (16, 16, 16)),    # amber: your move now
    "CLEAR": ((200, 32, 32), (255, 255, 255)),  # red: it is about to move -- stand clear
    "WATCH": ((30, 90, 180), (255, 255, 255)),  # blue: hands off, it is working
    "WAIT":  ((70, 76, 86), (255, 255, 255)),   # grey: nothing moves, nothing to do
    "DONE":  ((24, 140, 60), (255, 255, 255)),  # green: finished
}

NAMES = ["FLOOR RUN", "OBSTACLE STOP", "GRAB ONE SIDE", "FAULT RETURN RUN", "SPINS"]
NAME = {n: i for i, n in enumerate(NAMES)}

# action word, class
ACTIONS = [
    ("CLICK START", "YOU"),
    ("TAKE YOUR PLACE", "YOU"),
    ("STAND STILL", "YOU"),
    ("WATCH", "WATCH"),
    ("PULL IT BACK", "YOU"),
    ("WAIT", "WAIT"),
    ("AIM IT DOWN THE LANE", "YOU"),
    ("HOLD HARDER", "YOU"),
    ("HOLD LESS", "YOU"),
    ("GET READY", "YOU"),
    ("GRAB NOW", "YOU"),
    ("LET GO", "YOU"),
    ("STAND CLEAR", "CLEAR"),
    ("MOVE IT TO THE SPIN SPACE", "YOU"),
    ("STOPPING", "WATCH"),
    ("DONE", "DONE"),
    ("ENDED EARLY", "CLEAR"),
]
ACT = {a: i for i, (a, _) in enumerate(ACTIONS)}

SMALL_KINDS = ["", "WHEEL SPEED  % OF COMMAND", "SPIN LEG  (OF 10)"]
SK_NONE, SK_SPEED, SK_LEG = 0, 1, 2

# THE STEP TABLE. (id, action, detail, small readout, countdown ms: the step's own timer, 0 when the harness counts it
# some other way or not at all). The durations are Stephen's, 2026-09-29 ("durations seem ok"), except OBS_PLACE before
# the second trial, which is 20 s like the first: he has to get back in front of the platform after pulling it back.
STEPS = [
    ("BRIEF", "CLICK START",
     "Click START on the small operator panel, then walk to the platform. After that you never touch the PC: this "
     "board says what to do and counts down to it.", SK_NONE, 0),
    ("OBS_PLACE", "TAKE YOUR PLACE",
     "Stand 0.3 to 0.8 m in front of the platform, square across its path, and stand still. When the count ends it "
     "drives slowly into you.", SK_NONE, 20_000),
    ("OBS_DRIVE", "STAND STILL",
     "It drives slowly into you and pushes gently. About 1 second after it is blocked it stops itself.", SK_NONE, 0),
    ("OBS_CHECK", "WATCH",
     "It checks it can drive again: it may push once more, for an instant, and stop.", SK_NONE, 0),
    ("OBS_BACK", "PULL IT BACK",
     "Pull it back to where it started, aimed at you again, then let go. The count ends early once its wheels "
     "have been still for 3 seconds.", SK_NONE, 60_000),
    ("SETUP", "WAIT",
     "Starting the motors. Nothing moves yet.", SK_NONE, 0),
    ("GRAB_AIM", "AIM IT DOWN THE LANE",
     "Aim it down the 1.5 m lane and stand at its LEFT side, hands off. When the count ends it drives straight at a "
     "slow walk.", SK_NONE, 30_000),
    ("GRAB_HARDER", "HOLD HARDER",
     "The last try was too light. Aim it down the lane again and stand at its LEFT side; this time hold harder.",
     SK_NONE, 15_000),
    ("GRAB_LESS", "HOLD LESS",
     "The last try stalled it. Aim it down the lane again and stand at its LEFT side; this time hold less.",
     SK_NONE, 15_000),
    ("GRAB_DRIVE", "GET READY",
     "It drives slowly. Walk beside its LEFT side. When the count reaches 0, take hold of its LEFT side.",
     SK_NONE, 0),
    ("GRAB_HOLD", "GRAB NOW",
     "Hold it back, firmly and steadily, so the wheel speed below falls to about 50, never to 0. Keep holding "
     "until LET GO.", SK_SPEED, 0),
    ("GRAB_LETGO", "LET GO",
     "Let go and step away. It picks up speed and stops itself at 1 m.", SK_NONE, 0),
    ("GRAB_BACK", "PULL IT BACK",
     "Push it back to its start. The count ends early once its wheels have been still for 3 seconds.",
     SK_NONE, 60_000),
    ("RET_CLEAR", "STAND CLEAR",
     "Stand clear of the lane behind it. When the count ends it drives straight back to its start and stops.",
     SK_NONE, 5_000),
    ("RET_DRIVE", "WATCH",
     "Driving back to the start. It stops by itself.", SK_NONE, 0),
    ("FR_OUT_CLEAR", "STAND CLEAR",
     "Leave it aimed down the lane and stand clear. When the count ends it drives 1 m forward and stops.",
     SK_NONE, 15_000),
    ("FR_OUT", "WATCH",
     "Driving 1 m forward. It stops by itself.", SK_NONE, 0),
    ("FR_BACK_CLEAR", "STAND CLEAR",
     "When the count ends it drives back. About 1 second in, its LEFT wheel is faulted on purpose: both wheels stop "
     "within half a second, turning it a few degrees.", SK_NONE, 5_000),
    ("FR_BACK", "WATCH",
     "Driving back. The LEFT wheel will be faulted on purpose and both wheels will stop.", SK_NONE, 0),
    ("FR_RD_CLEAR", "STAND CLEAR",
     "The fault is cleared. When the count ends the drive back goes on to its start.", SK_NONE, 5_000),
    ("SPIN_MOVE", "MOVE IT TO THE SPIN SPACE",
     "Move it to level floor with 1 m clear all round, then stand outside that circle. It will spin in place.",
     SK_LEG, 45_000),
    ("SPIN_CLEAR", "STAND CLEAR",
     "Stay outside the circle. When the count ends it spins in place, at most one turn, and stops.", SK_LEG, 5_000),
    ("SPIN_DRIVE", "WATCH",
     "Spinning in place. Stay outside the circle.", SK_LEG, 0),
    ("STOPPING", "STOPPING",
     "The wheels are stopping.", SK_NONE, 0),
    ("LOGGING", "WAIT",
     "Writing results. Nothing moves.", SK_NONE, 0),
    ("END", "DONE",
     "The floor run is over and the wheels are off. Lift the wheels or disconnect the battery.", SK_NONE, 0),
    ("ENDED", "ENDED EARLY",
     "The run ended before its last step. The wheels are off. The log says why.", SK_NONE, 0),
]
STEP = {s[0]: i for i, s in enumerate(STEPS)}

BRIEF_LINES = [
    "THE FLOOR RUN -- WHAT YOU WILL DO",
    "1  OBSTACLE STOP    be the obstacle, twice; pull it back after each",
    "2  GRAB ONE SIDE    hold its LEFT side back when GRAB NOW shows; up to 3 tries",
    "3  FAULT RETURN RUN   stand clear and watch",
    "4  SPINS    move it to a clear space; ten spins; stay outside the circle",
    "Every drive starts after a red STAND CLEAR countdown.  AMBER = your move.  BLUE = hands off.",
    "PANIC: lift the wheels, disconnect the battery.",
]

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


def text_w(d, text, f):
    l, _, r, _ = d.textbbox((0, 0), text, font=f)
    return r - l


def fit(d, text, size, max_w):
    while size > 8:
        f = font(size)
        if text_w(d, text, f) <= max_w:
            return f
        size -= 1
    return font(8)


def centre(d, box, text, f, fill):
    x, y, w, h = box
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text((x + (w - (r - l)) / 2 - l, y + (h - (b - t)) / 2 - t), text, font=f, fill=fill)


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if not cur or text_w(d, trial, f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def wrapped(d, box, text, size, fill, pad=10, gap=6):
    x, y, w, h = box
    while size > 10:
        f = font(size)
        lines = wrap(d, text, f, w - 2 * pad)
        if max(text_w(d, ln, f) for ln in lines) <= w - 2 * pad and (size + gap) * len(lines) <= h - 2 * pad:
            break
        size -= 1
    top = y + pad
    for n, ln in enumerate(lines):
        l, t, _, _ = d.textbbox((0, 0), ln, font=f)
        d.text((x + pad - l, top + n * (size + gap) - t), ln, font=f, fill=fill)


def check_layout():
    assert BIG_X > DET_X + DET_W, "the countdown overlaps the detail"
    assert SDG_X + SDG_COUNT * SDG_W <= BIG_X, "the small readout overlaps the countdown"
    assert BIG_Y + BIG_H <= H and SLBL_Y + SLBL_H <= H and DET_Y + DET_H <= SLBL_Y
    assert len(STEPS) < 64 and len(ACTIONS) < 32


def draw_bg():
    img = Image.new("RGB", (W, H), C_PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle((NAME_X, NAME_Y, NAME_X + NAME_W - 1, NAME_Y + NAME_H - 1), fill=C_NAME_BG)
    d.rectangle((ACT_X, ACT_Y, ACT_X + ACT_W - 1, ACT_Y + ACT_H - 1), fill=C_WELL)
    d.rectangle((DET_X, DET_Y, DET_X + DET_W - 1, DET_Y + DET_H - 1), fill=C_WELL)
    d.rectangle((SLBL_X, SLBL_Y, SDG_X + SDG_COUNT * SDG_W - 1, SLBL_Y + SLBL_H - 1), fill=C_WELL)
    d.rectangle((BIG_X, BIG_Y, BIG_X + BIG_COUNT * BIG_W - 1, BIG_Y + BIG_H - 1), fill=C_WELL)
    centre(d, (BIG_X, BIG_Y + BIG_H + 2, BIG_COUNT * BIG_W, H - BIG_Y - BIG_H - 4), "SECONDS", font(18), C_DIM)
    return img


def draw_strip(rows, w, h, painter):
    img = Image.new("RGB", (w, h * len(rows)), C_WELL)
    d = ImageDraw.Draw(img)
    for i, row in enumerate(rows):
        painter(d, (0, i * h, w, h), row)
    return img


def paint_name(d, box, name):
    x, y, w, h = box
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=C_NAME_BG)
    centre(d, box, name, fit(d, name, 64, w - 40), C_TEXT)


def paint_action(d, box, action):
    word, cls = action
    bgc, ink = ACT_CLASSES[cls]
    x, y, w, h = box
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=bgc)
    centre(d, box, word, fit(d, word, 132, w - 40), ink)


def paint_detail(d, box, step):
    x, y, w, h = box
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=C_WELL)
    wrapped(d, box, step[2], 34, C_TEXT)


def digit_font(d, cell_w, cell_h):
    """The largest face whose every digit fits the cell with a margin -- measured, never guessed (a 290 px face
    clipped a 150 px cell in the first draft)."""
    size = cell_h
    while size > 8:
        f = font(size)
        widest = max(text_w(d, str(n), f) for n in range(10))
        l, t, r, b = d.textbbox((0, 0), "0123456789", font=f)
        if widest <= cell_w - 12 and (b - t) <= cell_h - 12:
            return f
        size -= 2
    return font(8)


def paint_digit(fnt, color):
    def painter(d, box, n):
        x, y, w, h = box
        d.rectangle((x, y, x + w - 1, y + h - 1), fill=C_WELL)
        if n != DGT_BLANK:
            centre(d, box, str(n), fnt, color)
    return painter


def paint_slabel(d, box, text):
    x, y, w, h = box
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=C_WELL)
    if text:
        wrapped(d, box, text, 24, C_DIM, pad=10, gap=2)


def draw_digits(cell_w, cell_h, _size, color):
    img = Image.new("RGB", (cell_w * DGT_CELLS, cell_h), C_WELL)
    d = ImageDraw.Draw(img)
    fnt = digit_font(d, cell_w, cell_h)
    for n in range(DGT_CELLS):
        paint_digit(fnt, color)(d, (n * cell_w, 0, cell_w, cell_h), n)
    return img


def draw_brief():
    img = Image.new("RGB", (W, LOW_H), C_PANEL)
    d = ImageDraw.Draw(img)
    d.rectangle((10, 6, W - 11, LOW_H - 7), fill=C_WELL)
    y = 18
    for n, ln in enumerate(BRIEF_LINES):
        size = 30 if n == 0 else 25
        fnt = fit(d, ln, size, W - 60)
        d.text((28, y), ln, font=fnt, fill=C_DIGIT if n == 0 else C_TEXT)
        y += size + 18
    return img


def con_block():
    out = ["CON { the floor countdown board (fboard) -- printed by tools/gen_floor_assets.py; re-run it, never edit }", ""]
    for k, v in [("FB_W", W), ("FB_H", H), ("FB_POS_X", POS_X), ("FB_POS_Y", POS_Y),
                 ("FB_NAME_X", NAME_X), ("FB_NAME_Y", NAME_Y), ("FB_NAME_W", NAME_W), ("FB_NAME_H", NAME_H),
                 ("FB_ACT_X", ACT_X), ("FB_ACT_Y", ACT_Y), ("FB_ACT_W", ACT_W), ("FB_ACT_H", ACT_H),
                 ("FB_LOW_Y", LOW_Y), ("FB_LOW_H", LOW_H),
                 ("FB_DET_X", DET_X), ("FB_DET_Y", DET_Y), ("FB_DET_W", DET_W), ("FB_DET_H", DET_H),
                 ("FB_SLBL_X", SLBL_X), ("FB_SLBL_Y", SLBL_Y), ("FB_SLBL_W", SLBL_W), ("FB_SLBL_H", SLBL_H),
                 ("FB_SDG_X", SDG_X), ("FB_SDG_Y", SDG_Y), ("FB_SDG_W", SDG_W), ("FB_SDG_H", SDG_H),
                 ("FB_SDG_COUNT", SDG_COUNT), ("FB_BIG_X", BIG_X), ("FB_BIG_Y", BIG_Y), ("FB_BIG_W", BIG_W),
                 ("FB_BIG_H", BIG_H), ("FB_BIG_COUNT", BIG_COUNT), ("FB_DGT_BLANK", DGT_BLANK)]:
        out.append(f"    {k:<18}= {v}")
    out.append("")
    out.append("    " + "#0, " + ", ".join(f"FB_NM_{n.replace(' ', '_')}" for n in NAMES))
    out.append("    " + "#0, " + ", ".join(f"FB_SK_{k}" for k in ("NONE", "SPEED", "LEG")))
    rows = [f"FB_ST_{s[0]}" for s in STEPS]
    out.append("    " + "#0, " + ", ...\n        ".join(", ".join(rows[i:i + 6]) for i in range(0, len(rows), 6)))
    out.append(f"    FB_ST_COUNT       = {len(STEPS)}")
    out.append("    FB_ST_LONGS       = 3                  ' fbSteps: action row, readout kind, countdown ms")
    return "\n".join(out)


def dat_block():
    out = ["DAT { the floor board's step table -- printed by tools/gen_floor_assets.py; re-run it, never edit }", ""]
    for i, (sid, act, _det, sk, ms) in enumerate(STEPS):
        lead = "fbSteps         LONG    " if i == 0 else "                LONG    "
        out.append(f"{lead}{ACT[act]:>2}, {sk}, {ms:>6}          ' FB_ST_{sid}: {act}")
    return "\n".join(out)


def save(img, name):
    img.save(os.path.join(SRC, name))


def preview():
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    bg = draw_bg()
    names = draw_strip(NAMES, NAME_W, NAME_H, paint_name)
    acts = draw_strip(ACTIONS, ACT_W, ACT_H, paint_action)
    dets = draw_strip(STEPS, DET_W, DET_H, paint_detail)
    big = draw_digits(BIG_W, BIG_H, 290, C_DIGIT)
    small = draw_digits(SDG_W, SDG_H, 56, C_TEXT)
    slbl = draw_strip(SMALL_KINDS, SLBL_W, SLBL_H, paint_slabel)
    brief = draw_brief()
    name_of = {"OBS": "OBSTACLE STOP", "GRAB": "GRAB ONE SIDE", "RET": "GRAB ONE SIDE", "FR": "FAULT RETURN RUN",
               "SPIN": "SPINS"}
    for i, (sid, act, _det, sk, ms) in enumerate(STEPS):
        frame = bg.copy()
        nm = name_of.get(sid.split("_")[0], "FLOOR RUN")
        frame.paste(names.crop((0, NAME[nm] * NAME_H, NAME_W, (NAME[nm] + 1) * NAME_H)), (NAME_X, NAME_Y))
        frame.paste(acts.crop((0, ACT[act] * ACT_H, ACT_W, (ACT[act] + 1) * ACT_H)), (ACT_X, ACT_Y))
        if sid == "BRIEF":
            frame.paste(brief, (0, LOW_Y))
        else:
            frame.paste(dets.crop((0, i * DET_H, DET_W, (i + 1) * DET_H)), (DET_X, DET_Y))
            frame.paste(slbl.crop((0, sk * SLBL_H, SLBL_W, (sk + 1) * SLBL_H)), (SLBL_X, SLBL_Y))
            shown = {SK_SPEED: 48, SK_LEG: 3}.get(sk)
            for c in range(SDG_COUNT):
                digit = DGT_BLANK
                if shown is not None:
                    div = 10 ** (SDG_COUNT - 1 - c)
                    if div == 1 or shown >= div:
                        digit = (shown // div) % 10
                frame.paste(small.crop((digit * SDG_W, 0, (digit + 1) * SDG_W, SDG_H)), (SDG_X + c * SDG_W, SDG_Y))
            secs = (ms // 1000) if ms else None
            for c in range(BIG_COUNT):
                digit = DGT_BLANK
                if secs is not None:
                    div = 10 ** (BIG_COUNT - 1 - c)
                    if div == 1 or secs >= div:
                        digit = (secs // div) % 10
                frame.paste(big.crop((digit * BIG_W, 0, (digit + 1) * BIG_W, BIG_H)), (BIG_X + c * BIG_W, BIG_Y))
        frame.save(os.path.join(PREVIEW_DIR, f"{i:02d}_{sid}.png"))
    print(f"previews: {PREVIEW_DIR}/NN_<step>.png, one per step")


def main():
    check_layout()
    save(draw_bg(), "fb_bg.bmp")
    save(draw_strip(NAMES, NAME_W, NAME_H, paint_name), "fb_name.bmp")
    save(draw_strip(ACTIONS, ACT_W, ACT_H, paint_action), "fb_action.bmp")
    save(draw_strip(STEPS, DET_W, DET_H, paint_detail), "fb_detail.bmp")
    save(draw_digits(BIG_W, BIG_H, 290, C_DIGIT), "fb_big.bmp")
    save(draw_digits(SDG_W, SDG_H, 56, C_TEXT), "fb_small.bmp")
    save(draw_strip(SMALL_KINDS, SLBL_W, SLBL_H, paint_slabel), "fb_slabel.bmp")
    save(draw_brief(), "fb_brief.bmp")
    if "--preview" in sys.argv:
        preview()
    print(con_block())
    print()
    print(dat_block())


if __name__ == "__main__":
    main()
