"""Tests for search module edge cases."""
import numpy as np

from ml.search import FaceSearchIndex


class TestFaceSearchIndex:
    def test_add_concatenate(self):
        idx = FaceSearchIndex(distance="cosine", threshold=0.4)
        idx.add(np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32), ["a", "b"])
        idx.add(np.array([[0.0, 1.0]], dtype=np.float32), ["c"])
        assert len(idx.identities) == 3

    def test_search_empty_gallery(self):
        idx = FaceSearchIndex()
        results = idx.search(np.array([1.0, 0.0], dtype=np.float32))
        assert results == []

    def test_search_euclidean_distance(self):
        idx = FaceSearchIndex(distance="euclidean", threshold=1.0)
        idx.add(np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32), ["a", "b"])
        results = idx.search(np.array([1.0, 0.0], dtype=np.float32), top_k=2)
        assert len(results) == 2
        assert results[0]["identity"] == "a"

    def test_search_cosine_distance(self):
        idx = FaceSearchIndex(distance="cosine", threshold=0.0)
        idx.add(np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32), ["a", "b"])
        results = idx.search(np.array([1.0, 0.0], dtype=np.float32), top_k=2)
        assert len(results) == 2

    def test_search_metadata(self):
        idx = FaceSearchIndex()
        idx.add(
            np.array([[1.0, 0.0]], dtype=np.float32),
            ["a"],
            metadata=[{"case_id": 1}],
        )
        results = idx.search(np.array([1.0, 0.0], dtype=np.float32))
        assert results[0]["metadata"] == {"case_id": 1}
