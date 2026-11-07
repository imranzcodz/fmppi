"""Robustness evaluation: degradation sweep and G4 gate check.

Degrades verification/kinship pairs, computes accuracy before/after each
degradation/severity, and reports the accuracy delta vs. a clean baseline.
"""

from __future__ import annotations

from typing import Callable, List, Tuple

import numpy as np
from PIL import Image

from .augmentations import DEGRADATIONS, degrade
from ..metrics import verification_report
from ..preprocess import preprocess


def _embed_pair(embed_fn: Callable[[np.ndarray], np.ndarray], img_a, img_b, size: int = 112) -> Tuple[np.ndarray, np.ndarray]:
    ea = preprocess(img_a, size=size)
    eb = preprocess(img_b, size=size)
    return embed_fn(ea), embed_fn(eb)


def evaluate_robustness(
    verifier,
    pairs: List[dict],
    degradations: List[str] | None = None,
    severities: List[str] | None = None,
    size: int = 112,
    seed: int = 42,
) -> dict:
    """Run the degradation suite.

    ``pairs`` entries: dict(path_a, path_b, label). ``verifier`` must expose
    ``verify(img_a, img_b) -> dict`` returning a ``score`` and ``is_kin``/
    ``match`` decision, or a ``similarity`` field. Returns per-degradation
    reports and the G4 pass/fail vs ``gate_min_accuracy``.
    """

    degradations = degradations or list(DEGRADATIONS.keys())
    severities = severities or ["mild", "moderate", "severe"]

    # Clean baseline
    clean_scores, clean_labels = [], []
    for p in pairs:
        res = verifier.verify(p["path_a"], p["path_b"])
        clean_scores.append(res.get("score", res.get("similarity", 0.0)))
        clean_labels.append(int(p["label"]))
    clean_report = verification_report(clean_scores, clean_labels)

    results = {"clean": clean_report, "degradations": {}}
    for deg in degradations:
        deg_results = {}
        for sev in severities:
            scores, labels = [], []
            for i, p in enumerate(pairs):

                img_a = np.asarray(Image.open(p["path_a"]).convert("RGB"))
                img_b = np.asarray(Image.open(p["path_b"]).convert("RGB"))
                da = degrade(img_a, deg, sev, seed + i)
                db = degrade(img_b, deg, sev, seed + i + 1000)
                tmp_a = f"/tmp/fmppi_rob_a_{i}.png"
                tmp_b = f"/tmp/fmppi_rob_b_{i}.png"
                Image.fromarray(da).save(tmp_a)
                Image.fromarray(db).save(tmp_b)
                res = verifier.verify(tmp_a, tmp_b)
                scores.append(res.get("score", res.get("similarity", 0.0)))
                labels.append(int(p["label"]))
            rep = verification_report(scores, labels)
            delta = rep["accuracy"] - clean_report["accuracy"]
            deg_results[sev] = {
                "accuracy": rep["accuracy"],
                "delta": delta,
                "auc": rep["auc"],
                "eer": rep["eer"],
                "tar_at_far_1e-3": rep.get("tar_at_far_0.001", 0.0),
            }
        results["degradations"][deg] = deg_results

    severe_accs = [
        results["degradations"][deg]["severe"]["accuracy"]
        for deg in degradations
        if "severe" in results["degradations"].get(deg, {})
    ]
    results["severe_mean_accuracy"] = float(np.mean(severe_accs)) if severe_accs else 0.0
    results["g4_pass"] = bool(results["severe_mean_accuracy"] >= 0.60)
    results["clean_accuracy"] = clean_report["accuracy"]
    return results
