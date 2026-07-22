#!/usr/bin/env python3
"""Render a terminal-style demo GIF of `libe run`.
Run: python assets/make_demo.py  ->  assets/demo.gif
"""
import os
import matplotlib
from PIL import Image, ImageDraw, ImageFont

FONT = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data/fonts/ttf/DejaVuSansMono.ttf")
BG = (13, 17, 23)
GREEN, WHITE, TEAL, PINK, DIM = (126, 231, 135), (230, 237, 243), (43, 212, 192), (247, 183, 210), (139, 148, 158)

# (text, color) segments per line; lines revealed one at a time
LINES = [
    [("$ ", GREEN), ("libe run --demo", WHITE)],
    [("  ✦ libelula v0.1.0", TEAL), ("  — medical-imaging AI pipeline · agile, precise", DIM)],
    [("  ✓ pipeline: ", TEAL), ("threshold-segmenter → region-scorer", (201, 182, 228))],
    [("  ◆ status ok · score 14.06 · QC pass · 0.1ms", PINK)],
]

W, H = 880, 210
PAD, LH, FS = 22, 34, 20
font = ImageFont.truetype(FONT, FS)


def frame(n_lines, cmd_chars=None, cursor=False):
    """Render the terminal. n_lines = how many lines shown; cmd_chars limits the
    typed command length (for the typing effect); cursor draws a block cursor."""
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([PAD + i * 22, 16, PAD + i * 22 + 12, 28], fill=c)
    y = 48
    for li, line in enumerate(LINES[:n_lines]):
        x = PAD
        for text, color in line:
            # on the command line, optionally show only the first cmd_chars of the command
            if li == 0 and color == WHITE and cmd_chars is not None:
                text = text[:cmd_chars]
            if text:
                d.text((x, y), text, font=font, fill=color)
                x += d.textlength(text, font=font)
        if cursor and li == n_lines - 1:
            d.rectangle([x + 1, y + 3, x + 11, y + FS + 2], fill=(230, 237, 243))
        y += LH
    return im


def main():
    cmd = "libe run --demo"
    frames, durations = [], []
    # 1. type the command char-by-char (with cursor)
    for k in range(1, len(cmd) + 1):
        frames.append(frame(1, cmd_chars=k, cursor=True)); durations.append(70)
    frames.append(frame(1, cmd_chars=len(cmd), cursor=True)); durations.append(450)  # pause before "enter"
    # 2. stream the output lines one at a time
    for i in range(2, len(LINES) + 1):
        frames.append(frame(i, cursor=(i < len(LINES)))); durations.append(600)
    # 3. hold the final frame
    frames.append(frame(len(LINES))); durations.append(2400)
    out = os.path.join(os.path.dirname(__file__), "demo.gif")
    frames[0].save(out, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)
    print("wrote", out, f"({len(frames)} frames)")


if __name__ == "__main__":
    main()
