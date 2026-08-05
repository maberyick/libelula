#!/usr/bin/env python3
"""Animated wing-flap dragonfly for libélula (LinkedIn-ready gif).
Fore and hind wings beat out of phase, like a real dragonfly.
Run: python assets/make_wing_gif.py  ->  assets/wing.gif
"""
import os, math
from PIL import Image, ImageDraw

# same pixel map as make_logo.py
GRID = [
    ".....ee.ee.....",
    ".....ee.ee.....",
    ".......h.......",
    ".UUUUUUaUUUUUU.",
    "UUUUUUUaUUUUUUU",
    ".UUUUUUaUUUUUU.",
    "..PPPPPaPPPPP..",
    "...PPPPaPPPP...",
    "....PPPaPPP....",
    ".......a.......",
    ".......a.......",
    ".......a.......",
    ".......a.......",
    "......aaa......",
    ".......a.......",
]
COLORS = {"e": "#ffd98a", "h": "#7fd1b8", "a": "#a8e6cf", "U": "#c9b6e4", "P": "#f7b7d2"}
OUTLINE = "#5a6b7a"
TILE = "#0f1622"
PX, PAD = 16, 22
COLS = max(len(r) for r in GRID); ROWS = len(GRID)
W = COLS * PX + PAD * 2; H = ROWS * PX + PAD * 2
CX = 7                 # center column (body)
NFRAMES = 16
AMP = 12.0             # max wing-tip lift in screen px

def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

DMAX = max(abs(x - CX) for y, row in enumerate(GRID)
           for x, ch in enumerate(row) if ch in ("U", "P")) or 1

def yoff(ch, x, phase):
    dist = abs(x - CX)
    s = math.sin(phase + (math.pi if ch == "P" else 0.0))   # hind wings out of phase
    return AMP * s * (dist / DMAX)

def draw_px(d, x, y, color, oy=0.0):
    x0 = PAD + x * PX; y0 = PAD + y * PX + oy
    d.rectangle([x0 - 1, y0 - 1, x0 + PX + 1, y0 + PX + 1], fill=rgb(OUTLINE))
    d.rectangle([x0, y0, x0 + PX, y0 + PX], fill=rgb(color))

def frame(phase):
    img = Image.new("RGB", (W, H), rgb(TILE))
    d = ImageDraw.Draw(img)
    # wings first (behind the body)
    for y, row in enumerate(GRID):
        for x, ch in enumerate(row):
            if ch in ("U", "P"):
                draw_px(d, x, y, COLORS[ch], yoff(ch, x, phase))
    # body, head, eyes on top so the wing roots tuck behind the body
    for y, row in enumerate(GRID):
        for x, ch in enumerate(row):
            if ch in ("a", "h", "e"):
                draw_px(d, x, y, COLORS[ch])
    return img

frames = [frame(2 * math.pi * i / NFRAMES) for i in range(NFRAMES)]
out = os.path.join(os.path.dirname(__file__) or ".", "wing.gif")
frames[0].save(out, save_all=True, append_images=frames[1:],
               duration=70, loop=0, optimize=True, disposal=2)
print(f"wrote {out}  {W}x{H}  {NFRAMES} frames")
