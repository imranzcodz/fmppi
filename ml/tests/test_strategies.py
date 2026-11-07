"""Unit tests for detection and embedding strategies (fallback path)."""

import numpy as np
import pytest

from ml.detection import build_detector
from ml.embedding import build_embedder


def test_build_detector_unknown():
    with pytest.raises(ValueError):
        build_detector("not_a_detector")


def test_detector_returns_list_of_detections():
    img = np.random.randint(0, 256, size=(64, 64, 3), dtype=np.uint8)
    det = build_detector("yolo_face", conf_threshold=0.5)
    dets = det.detect(img)
    assert isinstance(dets, list)
    for d in dets:
        assert d.bbox.shape == (4,)
        assert 0.0 <= d.confidence <= 1.0


def test_detector_name():
    assert build_detector("yolo_face").name() == "yolo_face"
    assert build_detector("deepface", detector_backend="opencv").name() == "deepface_opencv"


def test_build_embedder_unknown():
    with pytest.raises(ValueError):
        build_embedder("not_an_embedder")


def test_embedder_shapes():
    img = np.random.randint(0, 256, size=(112, 112, 3), dtype=np.uint8)
    for name, dim in (("facenet", 128), ("arcface", 512), ("vggface", 4096), ("deepface", 4096)):
        emb = build_embedder(name)
        assert emb.name() == name
        assert emb.embedding_dim == dim
        out = emb.embed(img)
        assert out.shape == (dim,)
        batch = emb.embed_batch([img, img])
        assert batch.shape == (2, dim)
        # L2 normalized
        assert np.allclose(np.linalg.norm(out), 1.0, atol=1e-5)


def test_deterministic_fallback_embedding_deterministic():
    from ml.embedding.base import deterministic_fallback_embedding

    img = np.random.randint(0, 256, size=(16, 16, 3), dtype=np.uint8)
    a = deterministic_fallback_embedding(img, 64)
    b = deterministic_fallback_embedding(img, 64)
    assert np.array_equal(a, b)
