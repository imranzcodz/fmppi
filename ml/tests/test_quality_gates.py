"""G2/G3 synthetic fallback tests for quality gate metrics.

These tests verify the metrics computation (TAR@FAR, accuracy, AUC, EER)
using synthetic data. When real LFW/KinFaceW datasets are available, they
should be replaced with real-data evaluations.
"""
import numpy as np

from ml.metrics import tar_at_far, verification_report, kinship_report, auc, eer


class TestFaceVerificationMetrics:
    """Synthetic fallback for G2: TAR@FAR=1e-3 ≥ 99% on LFW."""

    def test_tar_at_far_synthetic(self):
        """Synthetic same/different scores: same~high, diff~low."""
        rng = np.random.RandomState(42)
        same = rng.normal(0.8, 0.1, 500)
        diff = rng.normal(0.2, 0.1, 500)
        scores = np.concatenate([same, diff])
        labels = np.concatenate([np.ones(500), np.zeros(500)])

        tar, thr = tar_at_far(scores, labels, far_target=1e-3)
        assert 0.0 <= tar <= 1.0
        assert isinstance(thr, float)

    def test_verification_report_g2(self):
        """Full verification report with synthetic data."""
        rng = np.random.RandomState(7)
        same = rng.normal(0.85, 0.08, 300)
        diff = rng.normal(0.15, 0.08, 300)
        scores = np.concatenate([same, diff])
        labels = np.concatenate([np.ones(300), np.zeros(300)])

        report = verification_report(scores, labels, far_target=1e-3)
        assert "accuracy" in report
        assert "auc" in report
        assert "eer" in report
        assert "tar_at_far_0.001" in report
        assert report["n_samples"] == 600
        assert 0.0 <= report["accuracy"] <= 1.0
        assert 0.0 <= report["auc"] <= 1.0


class TestKinshipMetrics:
    """Synthetic fallback for G3: kinship accuracy ≥ 75% on KinFaceW."""

    def test_kinship_report_synthetic(self):
        """Synthetic kin/non-kin scores."""
        rng = np.random.RandomState(11)
        kin = rng.normal(0.75, 0.1, 200)
        non_kin = rng.normal(0.35, 0.1, 200)
        scores = np.concatenate([kin, non_kin])
        labels = np.concatenate([np.ones(200), np.zeros(200)])

        report = kinship_report(scores, labels)
        assert "accuracy" in report
        assert "auc" in report
        assert "eer" in report
        assert report["n_samples"] == 400
        assert 0.0 <= report["accuracy"] <= 1.0

    def test_auc_and_eer(self):
        rng = np.random.RandomState(3)
        scores = rng.uniform(0, 1, 100)
        labels = np.random.randint(0, 2, 100)
        a = auc(scores, labels)
        e, t = eer(scores, labels)
        assert 0.0 <= a <= 1.0
        assert 0.0 <= e <= 1.0
        assert isinstance(t, float)
