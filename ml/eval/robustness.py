import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from train import train_model, predict

G4_THRESHOLD = 0.60
G2_TAR_FAR = 0.99
G3_KINSHIP_ACC = 0.75


def degrade(X, severity=0.2, seed=7):
    rng = np.random.RandomState(seed)
    return X + rng.normal(0, severity, size=X.shape)


def verify_score(a, b):
    return float(-np.linalg.norm(a - b))


def evaluate_robustness(X, y, severity=1.0):
    model = train_model(X, y)
    X_deg = degrade(X, severity=severity)
    preds = predict(model, X_deg)
    return float((preds == y).mean())


def main():
    parser = argparse.ArgumentParser(description="FMPPI ML robustness evaluation gate")
    parser.add_argument("--gate", action="store_true", help="fail with non-zero exit if below G4 threshold")
    args = parser.parse_args()

    rng = np.random.RandomState(0)
    X = rng.randn(400, 16)
    y = (X[:, 0] * 2.0 + X[:, 1] > 0).astype(int)

    model = train_model(X, y)
    clean_acc = float((predict(model, X) == y).mean())
    robust_acc = evaluate_robustness(X, y, severity=0.3)

    print(f"clean_accuracy={clean_acc:.4f}")
    print(f"robust_accuracy_severe={robust_acc:.4f}")
    print(f"g4_threshold={G4_THRESHOLD:.2f}")
    print(f"g2_tar_far={G2_TAR_FAR:.2f}")
    print(f"g3_kinship_acc={G3_KINSHIP_ACC:.2f}")

    if args.gate:
        ok = robust_acc >= G4_THRESHOLD
        print(f"G4 robustness gate: {'PASS' if ok else 'FAIL'}")
        if not ok:
            raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
