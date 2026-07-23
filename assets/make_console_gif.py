#!/usr/bin/env python3
"""Render an animated GIF of the libélula web console (idle -> running -> result).
Screenshots the console at each pipeline stage via headless Edge/Chrome, then
assembles a GIF. Run: python assets/make_console_gif.py -> assets/console.gif
"""
import os
import subprocess
import tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = "file://" + os.path.join(HERE, "..", "libelula", "web", "static", "index.html")
BROWSER = "/opt/microsoft/msedge/msedge"
FRAMES = [-1, 0, 1, 2, 3, 4, 5]          # idle, running stages 0..4, done+result
DUR = [900, 380, 380, 380, 380, 380, 2400]


def shot(stage, out):
    subprocess.run([BROWSER, "--headless", "--disable-gpu", "--no-sandbox",
                    "--disable-dev-shm-usage", "--window-size=1120,560",
                    f"--screenshot={out}", f"{HTML}?stage={stage}"],
                   env={**os.environ, "TMPDIR": "/tmp"},
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    imgs = []
    with tempfile.TemporaryDirectory() as td:
        for i, s in enumerate(FRAMES):
            p = os.path.join(td, f"f{i}.png")
            shot(s, p)
            if os.path.exists(p):
                # crop to the content area (drop empty bottom)
                im = Image.open(p).convert("RGB")
                imgs.append(im.crop((0, 0, im.width, min(510, im.height))))
    if not imgs:
        print("no frames captured"); return
    out = os.path.join(HERE, "console.gif")
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=DUR[:len(imgs)],
                 loop=0, optimize=True)
    print("wrote", out, f"({len(imgs)} frames)")


if __name__ == "__main__":
    main()
