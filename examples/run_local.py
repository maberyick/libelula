"""End-to-end demo — runs the skeleton on a dummy image with zero setup.

    python examples/run_local.py

Shows: assistant suggests a pipeline -> orchestrator runs the models -> QC ->
a run report. Replace the dummy image + example models with your own to build
a real pipeline.
"""
import numpy as np
from openmedpipe.models import example_model  # noqa: F401  (registers the models)
from openmedpipe.assistant.suggest import suggest_pipeline
from openmedpipe.pipeline.orchestrator import run_case


def main():
    # a fake 64x64 image with a bright square (stand-in for a real scan)
    img = np.zeros((64, 64)); img[20:44, 20:44] = 1.0
    case = {"case_id": "demo-001", "image": img}

    # 1. assistant proposes which models to run (falls back to a rule if no Ollama)
    plan = suggest_pipeline(task="segment the bright region and score it",
                            modality="generic-image")
    print("Suggested pipeline:", plan)

    # 2. orchestrator runs them, with QC
    report = run_case(case, model_names=plan)

    # 3. results
    print("Status:", report.status)
    print("Score:", report.stage_outputs.get("region-scorer"))
    print("QC:", report.qc)
    print("Timings:", report.timings)


if __name__ == "__main__":
    main()
