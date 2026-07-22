#!/usr/bin/env python3
"""Generate the pixel-art dragonfly logo (libélula).
Run: python assets/make_logo.py  ->  assets/logo.svg (transparent) + logo-tile.svg (dark tile)
"""
import os

# pixel map — top-down dragonfly (each row exactly 15 chars, center col 7).
#  . transparent  e eye  h head  a body  U front wings (lavender)  P hind wings (pink)
GRID = [
    ".....ee.ee.....",   # big compound eyes
    ".....ee.ee.....",
    ".......h.......",   # head / thorax
    ".UUUUUUaUUUUUU.",   # front wings — symmetric
    "UUUUUUUaUUUUUUU",
    ".UUUUUUaUUUUUU.",
    "..PPPPPaPPPPP..",   # hind wings
    "...PPPPaPPPP...",
    "....PPPaPPP....",
    ".......a.......",   # long abdomen
    ".......a.......",
    ".......a.......",
    ".......a.......",
    "......aaa......",   # tail detail
    ".......a.......",
]

COLORS = {
    "e": "#ffd98a",   # eye — pastel peach/yellow
    "h": "#7fd1b8",   # head — medium pastel teal
    "a": "#a8e6cf",   # body — light pastel mint
    "U": "#c9b6e4",   # front wings — pastel lavender
    "P": "#f7b7d2",   # hind wings — pastel pink
}
OUTLINE = "#5a6b7a"   # soft outline so pastels read on ANY background (light or dark)
PX = 12               # pixel size
PAD = 14
COLS = max(len(r) for r in GRID)
ROWS = len(GRID)
W = COLS * PX + PAD * 2
H = ROWS * PX + PAD * 2


def _pixels():
    """Dragonfly pixels + a 1px soft outline behind edge pixels (readable on light/dark)."""
    filled = {(x, y) for y, row in enumerate(GRID)
              for x, ch in enumerate(row) if COLORS.get(ch)}
    rects = []
    for (x, y) in sorted(filled):                     # outline layer first
        if any((x+dx, y+dy) not in filled for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            px, py = PAD + x*PX, PAD + y*PX
            rects.append(f'<rect x="{px-1}" y="{py-1}" width="{PX+2}" height="{PX+2}" fill="{OUTLINE}"/>')
    for y, row in enumerate(GRID):                    # color layer on top
        for x, ch in enumerate(row):
            c = COLORS.get(ch)
            if c:
                px, py = PAD + x*PX, PAD + y*PX
                rects.append(f'<rect x="{px}" y="{py}" width="{PX}" height="{PX}" fill="{c}"/>')
    return rects


def _svg(bg=None):
    head = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="libelula dragonfly logo" '
            f'shape-rendering="crispEdges">')
    body = []
    if bg:
        r = min(W, H) * 0.22
        body.append(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="{r:.0f}" fill="{bg}"/>')
    body += _pixels()
    return head + "\n" + "\n".join(body) + "\n</svg>\n"


def main():
    d = os.path.dirname(__file__)
    open(os.path.join(d, "logo.svg"), "w").write(_svg(bg=None))            # transparent (primary)
    open(os.path.join(d, "logo-tile.svg"), "w").write(_svg(bg="#0f1622"))  # dark-tile alternate
    print(f"wrote logo.svg (transparent) + logo-tile.svg  ({COLS}x{ROWS} px, {W}x{H})")


if __name__ == "__main__":
    main()
