"""Unit tests for FMPPI metrics."""

import numpy as np

from ml.metrics import (
    accuracy_at_threshold,
    auc,
    best_threshold,
    eer,
    kinship_report,
    tar_at_far,
    verification_report,
)


def test_accuracy_at_threshold():
    scores = np.array([0.9, 0.8, 0.2, 0.1])
    labels = np.array([1, 1, 0, 0])
    assert accuracy_at_threshold(scores, labels, 0.5) == 1.0
    assert accuracy_at_threshold(scores, labels, 0.85) == 0.75


def test_best_threshold():
    scores = np.array([0.9, 0.8, 0.7, 0.1])
    labels = np.array([1, 1, 0, 0])
    t, acc = best_threshold(scores, labels)
    assert acc == 1.0
    assert 0.7 <= t <= 0.8


def test_auc_perfect_and_random():
    scores = np.array([0.9, 0.8, 0.2, 0.1])
    labels = np.array([1, 1, 0, 0])
    assert auc(scores, labels) == 1.0
    scores_rev = np.array([0.1, 0.2, 0.8, 0.9])
    assert auc(scores_rev, labels) == 0.0


def test_eer():
    scores = np.array([0.9, 0.8, 0.2, 0.1])
    labels = np.array([1, 1, 0, 0])
    e, t = eer(scores, labels)
    assert 0.0 <= e <= 1.0
    assert 0.0 <= t <= 1.0


def test_tar_at_far():
    scores = np.array([0.99, 0.98, 0.02, 0.01])
    labels = np.array([1, 1, 0, 0])
    tar, thr = tar_at_far(scores, labels, far_target=1e-3)
    assert 0.0 <= tar <= 1.0
    assert thr is not None


def test_verification_report_structure():
    scores = np.array([0.9, 0.8, 0.2, 0.1])
    labels = np.array([1, 1, 0, 0])
    rep = verification_report(scores, labels, far_target=1e-3)
    for key in ("accuracy", "auc", "eer", "tar_at_far_0.001", "n_samples"):
        assert key in rep
    assert rep["n_samples"] == 4


def test_kinship_report_structure():
    scores = np.array([0.9, 0.8, 0.2, 0.1])
    labels = np.array([1, 1, 0, 0])
    rep = kinship_report(scores, labels)
    assert rep["accuracy"] == 1.0
    assert rep["n_samples"] == 4


def test_single_class_auc_degrades_gracefully():
    scores = np.array([0.5, 0.6])
    labels = np.array([1, 1])
    assert auc(scores, labels) == 0.5
