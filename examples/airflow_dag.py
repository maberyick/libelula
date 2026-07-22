"""Example: run the SAME pipeline as an Airflow DAG (production reference).

This shows how to swap libélula's plain orchestrator for Airflow without changing
your models, QC, or the assistant. Drop this in your Airflow `dags/` folder.

It won't run without Airflow installed — it's a reference for the "productionize"
step. `pip install apache-airflow` to use it.

Pattern: one Airflow task per stage; each task calls into the same libélula models
(via the registry), so the model contract is identical to the local orchestrator.
"""
from __future__ import annotations
import numpy as np

try:
    from airflow.decorators import dag, task
    from datetime import datetime
except Exception:  # airflow not installed — this file is a reference
    dag = task = None


if dag:
    @dag(schedule=None, start_date=datetime(2026, 1, 1), catchup=False,
         tags=["libelula", "imaging"])
    def imaging_pipeline():

        @task
        def ingest() -> dict:
            img = np.zeros((64, 64)); img[20:44, 20:44] = 1.0
            return {"case_id": "airflow-001", "image": img.tolist(), "stage_outputs": {}}

        @task
        def segment(case: dict) -> dict:
            from libelula.models import example_model  # noqa: F401
            from libelula.models.registry import get
            case["image"] = np.asarray(case["image"])
            res = get("threshold-segmenter").run(case)
            case["stage_outputs"]["threshold-segmenter"] = res.output.tolist()
            return case

        @task
        def score(case: dict) -> dict:
            from libelula.models.registry import get
            case["stage_outputs"]["threshold-segmenter"] = np.asarray(
                case["stage_outputs"]["threshold-segmenter"])
            res = get("region-scorer").run(case)
            return {"case_id": case["case_id"], "score": res.output}

        @task
        def qc_and_publish(result: dict) -> dict:
            # add QC + persistence here (DB write, artifact store, notify)
            print("published:", result)
            return result

        qc_and_publish(score(segment(ingest())))

    imaging_pipeline()
