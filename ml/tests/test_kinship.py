"""Tests for kinship module."""
import numpy as np

from ml.kinship import KinshipVerifier


class TestKinshipVerifier:
    def test_verify_with_mock_encoder_cosine(self):
        class MockEncoder:
            def __call__(self, faces, training=False):
                return np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

        verifier = KinshipVerifier(encoder=MockEncoder(), metric="cosine", threshold=0.5, temperature=1.0)
        result = verifier.verify(np.zeros((1, 112, 112, 3)), np.zeros((1, 112, 112, 3)))
        assert "score" in result
        assert "confidence" in result
        assert "is_kin" in result
        assert "distance" in result
        assert "threshold" in result
        assert "metric" in result
        assert result["metric"] == "cosine"

    def test_verify_with_mock_encoder_euclidean(self):
        class MockEncoder:
            def __call__(self, faces, training=False):
                return np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

        verifier = KinshipVerifier(encoder=MockEncoder(), metric="euclidean", threshold=0.5, temperature=1.0)
        result = verifier.verify(np.zeros((1, 112, 112, 3)), np.zeros((1, 112, 112, 3)))
        assert result["metric"] == "euclidean"

    def test_calibrate_threshold(self):
        class MockEncoder:
            def __call__(self, faces, training=False):
                return np.eye(2, dtype=np.float32)

        verifier = KinshipVerifier(encoder=MockEncoder(), metric="cosine", threshold=0.5, temperature=1.0)
        scores = [0.9, 0.8, 0.2, 0.1]
        labels = [1, 1, 0, 0]
        thr = verifier.calibrate_threshold(scores, labels)
        assert isinstance(thr, float)
        assert verifier.threshold == thr

    def test_confidence_mapping(self):
        class MockEncoder:
            def __call__(self, faces, training=False):
                return np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float32)

        verifier = KinshipVerifier(encoder=MockEncoder(), metric="cosine", threshold=0.5, temperature=1.0)
        result = verifier.verify(np.zeros((1, 112, 112, 3)), np.zeros((1, 112, 112, 3)))
        assert result["is_kin"] is True
        assert result["confidence"] >= 0.5
