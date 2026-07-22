"""A minimal orchestrator — the backbone that runs a case through the stages.

This is a plain-Python stand-in for a production orchestrator (Airflow, Prefect,
Dagster, etc.). It shows the *pattern*: ingest -> preprocess -> run models ->
aggregate -> QC -> output, with each stage isolated, logged, and reproducible.

Swap this file for an Airflow DAG when you go to production; the model interface,
registry, QC, and assistant all stay the same.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Callable
from ..models import registry
from ..qc import checks


@dataclass
class RunReport:
    case_id: str
    stage_outputs: dict = field(default_factory=dict)
    model_meta: dict = field(default_factory=dict)
    qc: dict = field(default_factory=dict)
    timings: dict = field(default_factory=dict)
    status: str = "pending"


def run_case(case: dict, model_names: list[str],
             preprocess: Callable[[dict], dict] | None = None) -> RunReport:
    """Run one case through the pipeline.

    Args:
        case: dict with at least an 'image' (and a 'case_id'). Carries state across stages.
        model_names: ordered list of registered model ids to run (later models can read
                     earlier outputs via case['stage_outputs']).
        preprocess: optional callable to clean/normalize the input first.
    """
    rep = RunReport(case_id=case.get("case_id", "case"))
    case.setdefault("stage_outputs", {})

    # 1. preprocess
    if preprocess:
        t = time.perf_counter(); case = preprocess(case)
        rep.timings["preprocess"] = round(time.perf_counter() - t, 4)

    # 2. run each model (health-gated), collecting uniform results
    for name in model_names:
        model = registry.get(name)
        if not model.health_check():
            rep.status = "error"; rep.qc[name] = "unhealthy — skipped"
            continue
        model.load()
        t = time.perf_counter()
        result = model.run(case)
        rep.timings[name] = round(time.perf_counter() - t, 4)
        case["stage_outputs"][name] = result.output
        rep.stage_outputs[name] = result.output
        rep.model_meta[name] = result.meta

    # 3. QC (before anything is trusted)
    rep.qc.update(checks.run_all(rep.stage_outputs))
    rep.status = "ok" if all(v.get("pass", True) for v in rep.qc.values()
                             if isinstance(v, dict)) else "qc-flagged"
    return rep
