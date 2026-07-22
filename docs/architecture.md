# Architecture & how to extend

## The one idea
Give every model the **same interface** (`ModelPlugin`), so the orchestrator, QC,
and assistant are model-agnostic. Everything else follows from that.

## Stages
1. **Ingest / submit** (`web/`) — a case enters (paths, arrays, metadata).
2. **Preprocess** — normalize/clean (your function).
3. **Models** (`models/`) — each registered `ModelPlugin` runs in order; later
   models read earlier outputs via `case["stage_outputs"]`.
4. **Aggregate** — combine outputs (in the orchestrator or a final model).
5. **QC** (`qc/`) — gate results before they're trusted (empty masks, ranges, drift).
6. **Output** — mask / score / run report.

## The assistant (optional)
A **local** LLM (Ollama) reads the case + the model catalog and *suggests* an
ordered pipeline. It's a recommendation the operator accepts or edits. Local =
sensitive data never leaves your hardware. Off by default is fine.

## Going to production
- Replace `pipeline/orchestrator.py` with an **Airflow/Prefect/Dagster** DAG.
- Put each model behind `containers/Dockerfile.model`.
- Add a database for run tracking and a UI for submission/monitoring.
- The **model contract, registry, QC, and assistant do not change.**

## Design rules
- Deterministic, side-effect-free model `run()` where possible → reproducibility.
- Version data + weights + environment so any result can be regenerated.
- Health-gate models so a bad node refuses work instead of failing mid-run.
