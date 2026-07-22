"""Two example models so the skeleton runs end-to-end out of the box.

Replace these with real models — a segmentation net, a classifier, a foundation
model, a hosted API. The orchestrator only ever sees the ModelPlugin interface.
"""
from __future__ import annotations
import numpy as np
from .base import ModelPlugin, ModelResult
from .registry import register


@register
class ThresholdSegmenter(ModelPlugin):
    """Stand-in for a segmentation model. Real version: a U-Net / foundation model."""
    name = "threshold-segmenter"
    modality = "generic-image"
    description = "Segments bright regions in a 2D image. Placeholder for a real segmentation model."

    def run(self, case: dict) -> ModelResult:
        img = np.asarray(case["image"], dtype=float)
        mask = (img > img.mean()).astype("uint8")
        coverage = float(mask.mean())
        return ModelResult(self.name, output=mask,
                           meta={"coverage": coverage, "shape": list(img.shape)})


@register
class RegionScorer(ModelPlugin):
    """Stand-in for a downstream quantification/risk model."""
    name = "region-scorer"
    modality = "generic-image"
    description = "Turns a segmentation mask into a summary score. Placeholder for a risk/biomarker model."

    def run(self, case: dict) -> ModelResult:
        mask = np.asarray(case["stage_outputs"]["threshold-segmenter"], dtype=float)
        score = round(float(mask.mean() * 100), 2)     # e.g. % area involved
        return ModelResult(self.name, output={"score": score},
                           meta={"interpretation": "higher = more region involvement"})
