"""A more realistic example model — real image segmentation, not a toy threshold.

Uses Otsu thresholding + connected-component labeling (scipy) to find and measure
"lesions" in a 2D image — the shape of a real imaging model, still generic.

Install the extra:  pip install -e ".[examples]"
"""
from __future__ import annotations
import numpy as np
from .base import ModelPlugin, ModelResult
from .registry import register


def _otsu(img: np.ndarray) -> float:
    """Otsu's threshold — the classic automatic image threshold."""
    hist, edges = np.histogram(img, bins=256)
    centers = (edges[:-1] + edges[1:]) / 2
    w = hist.cumsum().astype(float)
    total = w[-1]
    if total == 0:
        return float(img.mean())
    mu = (hist * centers).cumsum()
    mu_t = mu[-1]
    denom = w * (total - w)
    denom[denom == 0] = np.nan
    sigma_b = (mu_t * w - mu) ** 2 / denom
    return float(centers[np.nanargmax(sigma_b)])


@register
class LesionSegmenter(ModelPlugin):
    """Otsu segmentation + connected-component region metrics. Realistic stand-in."""
    name = "lesion-segmenter"
    modality = "generic-image"
    description = "Otsu threshold + connected-component labeling; reports region count and areas."

    #: drop connected components smaller than this (noise cleanup)
    min_area: int = 10

    def run(self, case: dict) -> ModelResult:
        from scipy import ndimage           # imported here so the core skeleton stays scipy-free
        img = np.asarray(case["image"], dtype=float)
        thr = _otsu(img)
        mask = (img > thr).astype("uint8")
        labels, n = ndimage.label(mask)
        # keep only regions >= min_area (realistic post-processing)
        clean = np.zeros_like(mask)
        areas = []
        for i in range(1, n + 1):
            a = int((labels == i).sum())
            if a >= self.min_area:
                clean[labels == i] = 1
                areas.append(a)
        return ModelResult(self.name, output=clean,
                           meta={"threshold": round(thr, 4), "n_regions": len(areas),
                                 "areas": sorted(areas, reverse=True),
                                 "largest_area": max(areas) if areas else 0})
