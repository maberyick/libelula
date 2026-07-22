"""The model contract — every model in the pipeline implements this.

The whole point of the skeleton: give every model (yours, open-source, or a
hosted API) ONE common interface, so the orchestrator, QC, and assistant don't
care what's inside. Add a new model = implement this class, register it. That's it.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelResult:
    """Uniform output every model returns (so downstream stages are model-agnostic)."""
    name: str
    output: Any                       # mask, features, score, dict — whatever the model produces
    meta: dict = field(default_factory=dict)   # timings, version, params used


class ModelPlugin(ABC):
    """Base class for a pipeline model. Subclass + register (see registry.py)."""

    #: short unique id used in configs and by the assistant
    name: str = "unnamed-model"
    #: what kind of input this model expects (e.g. "wsi", "oct-bscan", "ct-volume")
    modality: str = "generic"
    #: free-text description the LLM assistant reads when choosing models
    description: str = ""

    def load(self) -> None:
        """Load weights / warm up. Called once before the first run. Override if needed."""
        return None

    @abstractmethod
    def run(self, case: dict) -> ModelResult:
        """Run inference on one case.

        `case` is a dict the orchestrator passes along (paths, arrays, prior-stage
        outputs). Return a ModelResult. Keep it deterministic and side-effect-free
        where possible so runs are reproducible.
        """
        raise NotImplementedError

    def health_check(self) -> bool:
        """Return True if the model can actually run (GPU visible, weights present).

        The orchestrator can refuse to dispatch to an unhealthy model instead of
        failing mid-run — a pattern worth keeping in production.
        """
        return True
