"""Unit tests for dataset loading / synthetic fallback."""

import os

from ml.datasets import load_verification_pairs, load_kinship_pairs, synthetic_verification_pairs


def test_synthetic_pairs_balanced():
    pairs = synthetic_verification_pairs(n_pairs=64, seed=1)
    assert len(pairs) == 64
    pos = [p for p in pairs if p.label == 1]
    neg = [p for p in pairs if p.label == 0]
    assert len(pos) == len(neg) == 32
    for p in pairs:
        assert os.path.exists(p.path_a)
        assert os.path.exists(p.path_b)


def test_missing_dataset_returns_empty():
    assert load_verification_pairs("data/does_not_exist") == []
    assert load_kinship_pairs("data/does_not_exist") == []
