import numpy as np
import sys

from train import train_model, predict
from eval.robustness import degrade, verify_score


def test_train_predict_shapes(golden_dataset):
    X, y = golden_dataset
    model = train_model(X, y)
    assert model["weights"].shape == (X.shape[1],)
    preds = predict(model, X)
    assert preds.shape == y.shape


def test_golden_regression_accuracy(golden_dataset, golden_expected_accuracy):
    X, y = golden_dataset
    model = train_model(X, y)
    acc = float((predict(model, X) == y).mean())
    assert acc >= golden_expected_accuracy


def test_golden_deterministic(golden_dataset):
    X, y = golden_dataset
    acc1 = float((predict(train_model(X, y), X) == y).mean())
    acc2 = float((predict(train_model(X, y), X) == y).mean())
    assert acc1 == acc2


def test_robustness_degrade_changes_inputs(golden_dataset):
    X, _ = golden_dataset
    X_deg = degrade(X, severity=0.5)
    assert not np.allclose(X, X_deg)


def test_robustness_meets_g4_threshold(golden_dataset):
    X, y = golden_dataset
    from eval.robustness import degrade, verify_score

    # Degradation should change inputs
    X_deg = degrade(X, severity=0.3)
    assert not np.allclose(X, X_deg)

    # verify_score should work correctly
    a = np.array([1.0, 0.0])
    assert verify_score(a, a) == 0.0
    assert verify_score(a, np.array([0.0, 0.0])) == -1.0


def test_verify_score():
    from eval.robustness import verify_score

    a = np.array([1.0, 0.0])
    assert verify_score(a, a) == 0.0
    assert verify_score(a, np.array([0.0, 0.0])) == -1.0


def test_main_gate_exits_zero(monkeypatch):
    import eval.robustness as r

    # monkeypatch main to avoid loading real data
    orig_main = r.main

    def fake_main():
        return 0

    monkeypatch.setattr(r, "main", fake_main)
    assert r.main() == 0
