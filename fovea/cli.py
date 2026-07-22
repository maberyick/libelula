"""Fovea CLI — drive the pipeline from the terminal.

    fovea models              list registered models
    fovea suggest "<task>"    ask the assistant which models to run
    fovea run [--demo]        run a case through the pipeline
    fovea serve               start the submission API (needs the [web] extra)
"""
from __future__ import annotations
import argparse
import json
import sys


BANNER = r"""
   __
  / _|_____   _____  __ _
 | |_/ _ \ \ / / _ \/ _` |   Fovea
 |  _| (_) \ V /  __/ (_| |   medical-imaging AI pipeline skeleton
 |_|  \___/ \_/ \___|\__,_|   bartekllc.org
"""


def _load_models():
    # importing registers the example models; swap for your own package
    from .models import example_model  # noqa: F401
    from .models import registry
    return registry


def cmd_models(args):
    reg = _load_models()
    for m in reg.catalog():
        print(f"  {m['name']:<22} [{m['modality']}]  {m['description']}")


def cmd_suggest(args):
    _load_models()
    from .assistant.suggest import suggest_pipeline
    plan = suggest_pipeline(task=args.task, modality=args.modality)
    print(json.dumps(plan))


def cmd_run(args):
    import numpy as np
    reg = _load_models()
    from .assistant.suggest import suggest_pipeline
    from .pipeline.orchestrator import run_case
    if args.demo or not args.image:
        img = np.zeros((64, 64)); img[20:44, 20:44] = 1.0
    else:
        img = np.load(args.image)                       # your .npy image
    plan = args.models.split(",") if args.models else suggest_pipeline(
        task="run pipeline", modality=args.modality)
    rep = run_case({"case_id": args.case_id, "image": img}, plan)
    print(json.dumps({"case_id": rep.case_id, "status": rep.status,
                      "plan": plan, "outputs": {k: str(type(v).__name__) for k, v in rep.stage_outputs.items()},
                      "score": rep.stage_outputs.get("region-scorer"),
                      "qc": rep.qc, "timings": rep.timings}, indent=2))


def cmd_serve(args):
    try:
        import uvicorn
    except ImportError:
        sys.exit('serve needs the web extra:  pip install -e ".[web]"')
    uvicorn.run("fovea.web.app:app", host=args.host, port=args.port, reload=args.reload)


def main(argv=None):
    p = argparse.ArgumentParser(prog="fovea", description="Fovea — medical-imaging AI pipeline skeleton")
    p.add_argument("--no-banner", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

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
    r.set_defaults(fn=cmd_run)

    v = sub.add_parser("serve", help="start the submission API")
    v.add_argument("--host", default="127.0.0.1"); v.add_argument("--port", type=int, default=8000)
    v.add_argument("--reload", action="store_true")
    v.set_defaults(fn=cmd_serve)

    args = p.parse_args(argv)
    if not args.no_banner and args.cmd in ("models", "run"):
        print(BANNER)
    args.fn(args)


if __name__ == "__main__":
    main()
