"""Quality-control stubs — run after models, before results are trusted.

In production this is where you catch drift, empty masks, out-of-range scores,
and failed cases. Return {"pass": bool, ...} per check so the orchestrator can
flag a run instead of silently shipping a bad result.
"""
from __future__ import annotations
import numpy as np


def run_all(stage_outputs: dict) -> dict:
    out = {}
    if "threshold-segmenter" in stage_outputs:
        out["nonempty_mask"] = check_nonempty_mask(stage_outputs["threshold-segmenter"])
    return out


def check_nonempty_mask(mask) -> dict:
    frac = float(np.asarray(mask).mean())
    return {"pass": 0.0 < frac < 1.0, "coverage": round(frac, 4),
            "note": "mask should not be all-empty or all-full"}
