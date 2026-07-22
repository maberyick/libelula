"""Minimal submission API stub (FastAPI).

    pip install -e ".[web]"
    uvicorn openmedpipe.web.app:app --reload

POST a case; it runs through the pipeline and returns the report. Replace the
in-memory demo with real storage + a queue for production.
"""
from __future__ import annotations
import numpy as np
from openmedpipe.models import example_model  # noqa: F401 (registers models)
from openmedpipe.assistant.suggest import suggest_pipeline
from openmedpipe.pipeline.orchestrator import run_case

try:
    from fastapi import FastAPI
except ImportError:  # keep import-safe without the web extra
    FastAPI = None

app = FastAPI(title="OpenMedPipe") if FastAPI else None

if app:
    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/run")
    def run(case_id: str = "case", size: int = 64):
        img = np.zeros((size, size)); img[size//3:2*size//3, size//3:2*size//3] = 1.0
        plan = suggest_pipeline("segment and score", "generic-image")
        rep = run_case({"case_id": case_id, "image": img}, plan)
        return {"case_id": rep.case_id, "status": rep.status,
                "score": rep.stage_outputs.get("region-scorer"), "qc": rep.qc}
