#!/usr/bin/env python3
"""Generate the pixel-art dragonfly logo (libélula) as an SVG.
Run: python assets/make_logo.py  ->  assets/logo.svg
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
BG = "#0f1622"        # dark tile so pastels pop (set to None for transparent)

PX = 12               # pixel size
PAD = 14
COLS = max(len(r) for r in GRID)
ROWS = len(GRID)
W = COLS * PX + PAD * 2
H = ROWS * PX + PAD * 2


def main():
    out = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="libelula dragonfly logo" '
           f'shape-rendering="crispEdges">']
    if BG:
        r = min(W, H) * 0.22
        out.append(f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="{r:.0f}" fill="{BG}"/>')
    for y, row in enumerate(GRID):
        for x, ch in enumerate(row):
            c = COLORS.get(ch)
            if not c:
                continue
            px = PAD + x * PX
            py = PAD + y * PX
            out.append(f'<rect x="{px}" y="{py}" width="{PX}" height="{PX}" fill="{c}"/>')
    out.append("</svg>\n")
    path = os.path.join(os.path.dirname(__file__), "logo.svg")
    open(path, "w").write("\n".join(out))
    print("wrote", path, f"({COLS}x{ROWS} px, {W}x{H} viewport)")


if __name__ == "__main__":
    main()
