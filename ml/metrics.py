"""Face verification and kinship metrics.

Standard metrics: accuracy, AUC, EER, TAR@FAR=1e-3 (verification);
accuracy/AUC/EER (kinship). Thresholds are calibrated on scores and labels.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
from sklearn import metrics as skm


def _as_arrays(scores: np.ndarray | list, labels: np.ndarray | list) -> Tuple[np.ndarray, np.ndarray]:
    s = np.asarray(scores, dtype=np.float64).ravel()
    y = np.asarray(labels, dtype=np.int64).ravel()
    if s.shape != y.shape:
        raise ValueError(f"scores and labels must have same shape, got {s.shape} and {y.shape}")
    return s, y


def accuracy_at_threshold(scores: np.ndarray | list, labels: np.ndarray | list, threshold: float) -> float:
    s, y = _as_arrays(scores, labels)
    preds = (s >= threshold).astype(np.int64)
    return float(np.mean(preds == y))


def best_threshold(scores: np.ndarray | list, labels: np.ndarray | list) -> Tuple[float, float]:
    """Threshold maximizing accuracy; returns (threshold, accuracy)."""
    s, y = _as_arrays(scores, labels)
    candidates = np.unique(s)
    best_t, best_acc = float(candidates[0]), 0.0
    for t in candidates:
        acc = accuracy_at_threshold(s, y, float(t))
        if acc > best_acc:
            best_t, best_acc = float(t), acc
    return best_t, best_acc


def auc(scores: np.ndarray | list, labels: np.ndarray | list) -> float:
    s, y = _as_arrays(scores, labels)
    if len(np.unique(y)) < 2:
        return 0.5
    return float(skm.roc_auc_score(y, s))


def eer(scores: np.ndarray | list, labels: np.ndarray | list) -> Tuple[float, float]:
    """Equal-error rate and the threshold at which FPR == FNR."""
    s, y = _as_arrays(scores, labels)
    if len(np.unique(y)) < 2:
        return 0.5, float(np.mean(s))
    fpr, tpr, thresholds = skm.roc_curve(y, s)
    fnr = 1.0 - tpr
    idx = int(np.argmin(np.abs(fpr - fnr)))
    return float(fpr[idx]), float(thresholds[idx])


def tar_at_far(
    scores: np.ndarray | list,
    labels: np.ndarray | list,
    far_target: float = 1e-3,
) -> Tuple[float, float]:
    """TAR at a target FAR. Returns (TAR, threshold).

    Scores are assumed to be similarities where larger = more likely same.
    FAR = P(score >= t | different). We pick the highest threshold with FAR <=
    target, then TAR = P(score >= t | same). If no threshold meets the FAR
    target, we use the most conservative threshold (highest) and report its TAR.
    """
    s, y = _as_arrays(scores, labels)
    same = s[y == 1]
    diff = s[y == 0]
    if len(diff) == 0 or len(same) == 0:
        return 0.0, float(np.mean(s)) if len(s) else 0.0

    # Candidate thresholds: sorted unique scores. For a threshold t, FAR = frac(diff >= t).
    thresholds = np.unique(np.concatenate([diff, same]))
    best_tar, best_t = 0.0, float(thresholds[-1])
    for t in thresholds:
        far = float(np.mean(diff >= t))
        if far <= far_target:
            tar = float(np.mean(same >= t))
            if tar > best_tar:
                best_tar, best_t = tar, float(t)
    # If nothing met the target, keep the most conservative (highest) threshold result
    if best_tar == 0.0:
        t = float(thresholds[-1])
        best_tar = float(np.mean(same >= t))
        best_t = t
    return best_tar, best_t


def verification_report(scores: np.ndarray | list, labels: np.ndarray | list, far_target: float = 1e-3) -> dict:
    s, y = _as_arrays(scores, labels)
    thr, acc = best_threshold(s, y)
    auc_score = auc(s, y)
    eer_val, eer_thr = eer(s, y)
    tar, tar_thr = tar_at_far(s, y, far_target)
    return {
        "accuracy": float(acc),
        "threshold": float(thr),
        "auc": float(auc_score),
        "eer": float(eer_val),
        "eer_threshold": float(eer_thr),
        f"tar_at_far_{far_target:g}": float(tar),
        f"tar_at_far_{far_target:g}_threshold": float(tar_thr),
        "far_target": float(far_target),
        "n_samples": int(len(s)),
        "n_positive": int(np.sum(y == 1)),
        "n_negative": int(np.sum(y == 0)),
    }


def kinship_report(scores: np.ndarray | list, labels: np.ndarray | list) -> dict:
    s, y = _as_arrays(scores, labels)
    thr, acc = best_threshold(s, y)
    auc_score = auc(s, y)
    eer_val, _ = eer(s, y)
    return {
        "accuracy": float(acc),
        "threshold": float(thr),
        "auc": float(auc_score),
        "eer": float(eer_val),
        "n_samples": int(len(s)),
        "n_positive": int(np.sum(y == 1)),
        "n_negative": int(np.sum(y == 0)),
    }
