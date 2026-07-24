#!/usr/bin/env python3
"""Render an animated terminal GIF of the `libe` banner (typing + dragonfly reveal).
Run: python assets/make_banner_gif.py  ->  assets/libe-banner.gif
"""
import os
from PIL import Image, ImageDraw, ImageFont

ART = [
    ".....ee.ee.....", ".....ee.ee.....", ".......h.......",
    ".UUUUUUaUUUUUU.", "UUUUUUUaUUUUUUU", ".UUUUUUaUUUUUU.",
    "..PPPPPaPPPPP..", "...PPPPaPPPP...", "....PPPaPPP....",
    ".......a.......", ".......a.......", ".......a.......",
    ".......a.......", "......aaa......", ".......a.......",
]
RGB = {"e": (255, 217, 138), "h": (127, 209, 184), "a": (168, 230, 207),
       "U": (201, 182, 228), "P": (247, 183, 210)}
if len(ART) % 2:
    ART = ART + ["." * len(ART[0])]

BG = (13, 16, 28)
GREEN, WHITE, TEAL, DIM = (126, 209, 132), (222, 227, 237), (127, 225, 220), (140, 150, 170)
CW, CH = 15, 30
COLS = len(ART[0])
PAD = 26
DRAGON_ROWS = len(ART) // 2
HDR = "✦ libélula v0.1.0  — medical-imaging AI pipeline · agile, precise"
TAG = "all eyes · precise · agile — medical-imaging AI pipelines"
W, H = 780, PAD * 2 + 34 + DRAGON_ROWS * CH + 70

D = os.path.dirname(os.path.abspath(__file__))
try:
    MONO = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 18)
    MONOB = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", 18)
except OSError:
    MONO = MONOB = ImageFont.load_default()


def frame(cmd, rows, header=False, tag=False, cursor=False, wing_dy=0):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((PAD, PAD), "$ ", font=MONOB, fill=GREEN)
    d.text((PAD + 20, PAD), cmd + ("█" if cursor else ""), font=MONO, fill=WHITE)
    top = PAD + 42
    for cy in range(rows):
        for x in range(COLS):
            tc, bc = ART[2 * cy][x], ART[2 * cy + 1][x]
            t, b = RGB.get(tc), RGB.get(bc)
            dy = wing_dy if (tc in "UP" or bc in "UP") else 0  # flap the wings
            px, py = PAD + x * CW, top + cy * CH + dy
            if t:
                d.rectangle([px, py, px + CW - 1, py + CH // 2 - 1], fill=t)
            if b:
                d.rectangle([px, py + CH // 2, px + CW - 1, py + CH - 1], fill=b)
    ty = top + DRAGON_ROWS * CH + 12
    if header:
        d.text((PAD, ty), "✦ libélula v0.1.0", font=MONOB, fill=TEAL)
        w = d.textlength("✦ libélula v0.1.0", font=MONOB)
        d.text((PAD + w, ty), HDR.split("v0.1.0", 1)[1], font=MONO, fill=DIM)
    if tag:
        d.text((PAD, ty + 26), TAG, font=MONO, fill=DIM)
    return im


def main():
    frames, durs = [], []
    cmd = "libe"
    for k in range(len(cmd) + 1):          # typing
        frames.append(frame(cmd[:k], 0, cursor=True)); durs.append(150)
    frames.append(frame(cmd, 0)); durs.append(300)
    for r in range(1, DRAGON_ROWS + 1):    # dragonfly draws in
        frames.append(frame(cmd, r)); durs.append(70)
    frames.append(frame(cmd, DRAGON_ROWS, header=True)); durs.append(300)
    for _ in range(2):                     # two wing-flaps, then settle
        for off in (-4, -7, -4, 0):
            frames.append(frame(cmd, DRAGON_ROWS, header=True, tag=True, wing_dy=off)); durs.append(90)
    frames.append(frame(cmd, DRAGON_ROWS, header=True, tag=True)); durs.append(2400)
    out = os.path.join(D, "libe-banner.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
    frames[-1].save(os.path.join(D, "libe-banner.png"))
    print("wrote libe-banner.gif +", f"{len(frames)} frames")


if __name__ == "__main__":
    main()
