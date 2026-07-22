"""Tests for the libélula skeleton — enough to prove it works and stays working."""
import numpy as np
import pytest

from libelula.models import example_model  # noqa: F401  (registers example models)
from libelula.models import registry
from libelula.models.base import ModelPlugin, ModelResult
from libelula.pipeline.orchestrator import run_case
from libelula.qc import checks
from libelula.assistant.suggest import suggest_pipeline


@pytest.fixture
def demo_case():
    img = np.zeros((32, 32)); img[10:22, 10:22] = 1.0
    return {"case_id": "t", "image": img}


# --- registry / contract -----------------------------------------------------
def test_models_registered():
    names = {m.name for m in registry.all_models()}
    assert {"threshold-segmenter", "region-scorer"} <= names


def test_catalog_shape():
    for m in registry.catalog():
        assert {"name", "modality", "description"} <= set(m)


def test_register_rejects_duplicates():
    class Dup(ModelPlugin):
        name = "threshold-segmenter"
        def run(self, case): ...
    with pytest.raises(ValueError):
        registry.register(Dup)


def test_model_result_is_uniform():
    m = registry.get("threshold-segmenter")
    res = m.run({"image": np.ones((8, 8))})
    assert isinstance(res, ModelResult)
    assert res.name == "threshold-segmenter"


# --- orchestrator ------------------------------------------------------------
def test_run_case_end_to_end(demo_case):
    rep = run_case(demo_case, ["threshold-segmenter", "region-scorer"])
    assert rep.status == "ok"
    assert "region-scorer" in rep.stage_outputs
    assert rep.stage_outputs["region-scorer"]["score"] > 0


def test_later_stage_reads_earlier_output(demo_case):
    rep = run_case(demo_case, ["threshold-segmenter", "region-scorer"])
    # region-scorer depends on the segmenter's mask; the score = mask coverage % (rounded)
    expected = float((demo_case["image"] > demo_case["image"].mean()).mean()) * 100
    assert rep.stage_outputs["region-scorer"]["score"] == pytest.approx(expected, abs=0.01)


def test_health_gate_skips_unhealthy(demo_case, monkeypatch):
    m = registry.get("threshold-segmenter")
    monkeypatch.setattr(m, "health_check", lambda: False)
    rep = run_case(demo_case, ["threshold-segmenter"])
    assert rep.status == "error"


# --- QC ----------------------------------------------------------------------
def test_qc_flags_empty_mask():
    out = checks.check_nonempty_mask(np.zeros((8, 8)))
    assert out["pass"] is False


def test_qc_passes_partial_mask():
    mask = np.zeros((8, 8)); mask[0:4] = 1
    assert checks.check_nonempty_mask(mask)["pass"] is True


# --- assistant ---------------------------------------------------------------
def test_suggest_falls_back_without_ollama():
    # no local Ollama in CI -> deterministic fallback returns matching-modality models
    plan = suggest_pipeline("segment and score", "generic-image")
    assert plan and set(plan) <= {m.name for m in registry.all_models()}
