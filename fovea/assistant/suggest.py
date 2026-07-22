"""Optional LLM assistant — suggests which models to run for a case.

Pattern: a LOCAL model (via Ollama) reads the case description + the model
catalog and proposes an ordered pipeline. Local = data never leaves your
hardware. This is a *suggestion* the operator accepts or edits — not autopilot.

Falls back to a deterministic rule if Ollama isn't available, so the skeleton
runs with zero external dependencies.
"""
from __future__ import annotations
import json
import urllib.request
from ..models import registry

OLLAMA_URL = "http://localhost:11434/api/generate"


def suggest_pipeline(task: str, modality: str = "generic-image",
                     model: str = "llama3") -> list[str]:
    """Return an ordered list of model names to run for `task`.

    Tries a local Ollama model; if unavailable, falls back to a simple rule.
    """
    catalog = registry.catalog()
    try:
        prompt = (
            "You are a medical-imaging pipeline planner. Given a task and the available "
            "models, return ONLY a JSON list of model names in run order.\n"
            f"Task: {task}\nModality: {modality}\n"
            f"Available models: {json.dumps(catalog)}\n"
            'Answer with e.g. ["model-a","model-b"] and nothing else.'
        )
        body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(OLLAMA_URL, data=body,
                                     headers={"Content-Type": "application/json"})
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
        names = json.loads(resp["response"].strip())
        valid = {m["name"] for m in catalog}
        return [n for n in names if n in valid] or _fallback(modality)
    except Exception:
        return _fallback(modality)


def _fallback(modality: str) -> list[str]:
    """Deterministic default: run every model whose modality matches, in registry order."""
    return [m["name"] for m in registry.catalog()
            if m["modality"] in (modality, "generic", "generic-image")]
