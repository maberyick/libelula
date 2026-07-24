"""libélula CLI — drive the pipeline from the terminal.

    libe                      show the dragonfly banner + commands
    libe run [--demo]         run a case through the pipeline
    libe models               list registered models
    libe suggest "<task>"     ask the assistant which models to run
    libe serve                start the submission API (needs the [web] extra)

Style note: ✦ header · ✓ steps · ◆ result · › input — a nod to colibri's clean CLI.
"""
from __future__ import annotations
import argparse
import json
import sys

VERSION = "0.1.0"
TEAL, PINK, LAV, DIM, RED, RST = "\033[96m", "\033[95m", "\033[94m", "\033[2m", "\033[91m", "\033[0m"


def _c(s, color):
    return f"{color}{s}{RST}" if sys.stdout.isatty() else s


def header():
    print(_c(f"  ✦ libélula v{VERSION}", TEAL) +
          _c("  — medical-imaging AI pipeline · agile, precise", DIM))


# Pixel-art dragonfly (matches assets/logo.svg), rendered with half-blocks + truecolor.
_ART = [
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
_ART_RGB = {
    "e": (255, 217, 138),  # eyes — peach
    "h": (127, 209, 184),  # head — teal
    "a": (168, 230, 207),  # body — mint
    "U": (201, 182, 228),  # front wings — lavender
    "P": (247, 183, 210),  # hind wings — pink
}


def mascot():
    """Compact colored dragonfly for the terminal (empty string when piped)."""
    if not sys.stdout.isatty():
        return ""
    grid = _ART + (["." * len(_ART[0])] if len(_ART) % 2 else [])
    fg = lambda c: f"\033[38;2;{c[0]};{c[1]};{c[2]}m"
    bg = lambda c: f"\033[48;2;{c[0]};{c[1]};{c[2]}m"
    lines = []
    for y in range(0, len(grid), 2):
        top, bot, s = grid[y], grid[y + 1], "   "
        for x in range(len(top)):
            t, b = _ART_RGB.get(top[x]), _ART_RGB.get(bot[x])
            if t and b:
                s += fg(t) + bg(b) + "▀" + RST
            elif t:
                s += fg(t) + "▀" + RST
            elif b:
                s += fg(b) + "▄" + RST
            else:
                s += " "
        lines.append(s)
    return "\n".join(lines)


def banner():
    art = mascot()
    if art:
        print("\n" + art + "\n")
    header()
    print(_c("  \U0001fab0 all eyes · precise · agile — a skeleton for medical-imaging AI pipelines", DIM))


def cmd_banner(args):
    banner()


def _load_models():
    from .models import example_model  # noqa: F401  (registers example models)
    from .models import registry
    return registry


def cmd_models(args):
    header()
    for m in _load_models().catalog():
        print("  " + _c("◆", PINK) + f" {m['name']:<20} " +
              _c(f"[{m['modality']}]", DIM) + f"  {m['description']}")


def cmd_suggest(args):
    header()
    _load_models()
    from .assistant.suggest import suggest_pipeline
    plan = suggest_pipeline(task=args.task, modality=args.modality)
    print("  " + _c("›", DIM) + f" {args.task}")
    print("  " + _c("◆", PINK) + " " + _c(" → ".join(plan), LAV))


def cmd_run(args):
    import numpy as np
    header()
    _load_models()
    from .assistant.suggest import suggest_pipeline
    from .pipeline.orchestrator import run_case
    img = np.load(args.image) if (args.image and not args.demo) else _demo_image()
    plan = args.models.split(",") if args.models else suggest_pipeline(
        task="run pipeline", modality=args.modality)
    print("  " + _c("✓", TEAL) + " pipeline: " + _c(" → ".join(plan), LAV))
    rep = run_case({"case_id": args.case_id, "image": img}, plan)
    qc_ok = all(v.get("pass", True) for v in rep.qc.values() if isinstance(v, dict))
    ms = sum(rep.timings.values()) * 1000
    score = rep.stage_outputs.get("region-scorer")
    line = f"  ◆ status {rep.status}"
    if score is not None:
        line += f" · score {score.get('score')}"
    line += f" · QC {'pass' if qc_ok else 'FLAGGED'} · {ms:.1f}ms"
    print(_c(line, PINK if qc_ok else RED))
    if args.json:
        print(json.dumps({"case_id": rep.case_id, "status": rep.status, "plan": plan,
                          "score": score, "qc": rep.qc, "timings": rep.timings}, indent=2))


def cmd_serve(args):
    try:
        import uvicorn
    except ImportError:
        sys.exit('serve needs the web extra:  pip install -e ".[web]"')
    uvicorn.run("libelula.web.app:app", host=args.host, port=args.port, reload=args.reload)


def _demo_image():
    import numpy as np
    img = np.zeros((64, 64)); img[20:44, 20:44] = 1.0
    return img


def main(argv=None):
    p = argparse.ArgumentParser(prog="libe", description="libélula — medical-imaging AI pipeline skeleton")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("banner", help="show the dragonfly banner").set_defaults(fn=cmd_banner)
    sub.add_parser("models", help="list registered models").set_defaults(fn=cmd_models)

    s = sub.add_parser("suggest", help="assistant suggests which models to run")
    s.add_argument("task"); s.add_argument("--modality", default="generic-image")
    s.set_defaults(fn=cmd_suggest)

    r = sub.add_parser("run", help="run a case through the pipeline")
    r.add_argument("--image", help="path to a .npy image (omit for --demo)")
    r.add_argument("--demo", action="store_true", help="run on a built-in dummy image")
    r.add_argument("--models", help="comma-separated model ids (else assistant decides)")
    r.add_argument("--modality", default="generic-image")
    r.add_argument("--case-id", default="case")
    r.add_argument("--json", action="store_true", help="also print the full JSON report")
    r.set_defaults(fn=cmd_run)

    v = sub.add_parser("serve", help="start the submission API")
    v.add_argument("--host", default="127.0.0.1"); v.add_argument("--port", type=int, default=8000)
    v.add_argument("--reload", action="store_true")
    v.set_defaults(fn=cmd_serve)

    args = p.parse_args(argv)
    if not args.cmd:
        banner()
        print(_c("  run 'libe --help' for commands", DIM))
        return
    args.fn(args)


if __name__ == "__main__":
    main()
