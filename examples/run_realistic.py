"""Realistic example — segment 'lesions' in a synthetic image with a real algorithm.

    pip install -e ".[examples]"
    python examples/run_realistic.py

Builds a synthetic image with a few bright blobs (stand-in for lesions/cells),
runs Otsu + connected-component segmentation, and reports real region metrics.
Swap the synthetic image for your own .npy to use it for real.
"""
import numpy as np
from libelula.models import example_realistic  # noqa: F401  (registers lesion-segmenter)
from libelula.pipeline.orchestrator import run_case


def synthetic_image(size=96, n_blobs=3, seed=0):
    rng = np.random.default_rng(seed)
    img = rng.normal(0.15, 0.03, (size, size))          # background noise
    yy, xx = np.mgrid[0:size, 0:size]
    for _ in range(n_blobs):
        cy, cx = rng.integers(15, size - 15, 2)
        r = rng.integers(6, 12)
        img += 0.9 * np.exp(-((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * r ** 2))
    return np.clip(img, 0, 1)


def main():
    img = synthetic_image()
    rep = run_case({"case_id": "realistic-001", "image": img}, ["lesion-segmenter"])
    meta = rep.model_meta["lesion-segmenter"]
    print("status:", rep.status)
    print("Otsu threshold:", meta["threshold"])
    print("regions found:", meta["n_regions"], "| areas:", meta["areas"])
    print("QC:", rep.qc)


if __name__ == "__main__":
    main()
