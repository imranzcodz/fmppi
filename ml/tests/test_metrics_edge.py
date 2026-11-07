"""Additional metrics tests for uncovered branches."""
import pytest

from ml.metrics import accuracy_at_threshold, auc, eer, tar_at_far


class TestMetricsEdgeCases:
    def test_as_arrays_shape_mismatch(self):
        with pytest.raises(ValueError):
            accuracy_at_threshold([0.1, 0.2], [0, 1, 0], threshold=0.5)

    def test_accuracy_at_threshold(self):
        scores = [0.1, 0.4, 0.6, 0.9]
        labels = [0, 0, 1, 1]
        assert accuracy_at_threshold(scores, labels, 0.5) == 1.0
        assert accuracy_at_threshold(scores, labels, 0.95) == 0.5

    def test_auc_single_class(self):
        # All same label -> AUC returns 0.5
        assert auc([0.1, 0.2, 0.3], [0, 0, 0]) == 0.5
        assert auc([0.1, 0.2, 0.3], [1, 1, 1]) == 0.5

    def test_eer_single_class(self):
        e, t = eer([0.1, 0.2, 0.3], [0, 0, 0])
        assert e == 0.5
        assert abs(t - 0.2) < 1e-9

    def test_tar_at_far_empty_same(self):
        # No same-class samples
        tar, thr = tar_at_far([0.1, 0.2, 0.3], [0, 0, 0])
        assert tar == 0.0

    def test_tar_at_far_empty_diff(self):
        # No different-class samples
        tar, thr = tar_at_far([0.1, 0.2, 0.3], [1, 1, 1])
        assert tar == 0.0

    def test_tar_at_far_no_threshold_meets_target(self):
        # All diff scores are below any threshold that meets FAR target
        scores = [0.01, 0.02, 0.9, 0.95]
        labels = [0, 0, 1, 1]
        tar, thr = tar_at_far(scores, labels, far_target=1e-3)
        assert isinstance(tar, float)
        assert isinstance(thr, float)

    def test_best_threshold(self):
        scores = [0.1, 0.4, 0.6, 0.9]
        labels = [0, 0, 1, 1]
        thr, acc = __import__("ml.metrics", fromlist=["best_threshold"]).best_threshold(scores, labels)
        assert isinstance(thr, float)
        assert 0.0 <= acc <= 1.0
