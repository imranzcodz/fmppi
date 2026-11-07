"""Unit tests for the 1:N face search index."""

import numpy as np
import os

from ml.search import FaceSearchIndex


def _embeddings(n, dim=8, seed=0):
    rng = np.random.default_rng(seed)
    emb = rng.standard_normal((n, dim))
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)
    return emb.astype(np.float32)


def test_add_and_search_returns_top_k():
    idx = FaceSearchIndex(distance="cosine", threshold=0.5)
    embs = _embeddings(20, seed=1)
    ident = [f"id_{i}" for i in range(20)]
    idx.add(embs, ident)
    q = embs[3]
    res = idx.search(q, top_k=5)
    assert len(res) == 5
    assert res[0]["identity"] == "id_3"
    assert res[0]["rank"] == 1
    assert res[0]["match"] is True  # self-similarity = 1 >= threshold


def test_search_empty():
    idx = FaceSearchIndex()
    assert idx.search(np.zeros(8), top_k=5) == []


def test_save_and_load(tmp_path):
    idx = FaceSearchIndex(distance="cosine", threshold=0.5)
    embs = _embeddings(10, seed=2)
    ident = [f"id_{i}" for i in range(10)]
    meta = [{"case": i} for i in range(10)]
    idx.add(embs, ident, meta)
    path = os.path.join(tmp_path, "index.json")
    idx.save(path)
    idx2 = FaceSearchIndex()
    idx2.load(path)
    assert idx2.identities == ident
    assert len(idx2.metadata) == 10
    res = idx2.search(embs[0], top_k=3)
    assert res[0]["identity"] == "id_0"


def test_threshold_match_flag():
    idx = FaceSearchIndex(distance="cosine", threshold=0.9)
    embs = _embeddings(5, seed=3)
    ident = [f"id_{i}" for i in range(5)]
    idx.add(embs, ident)
    res = idx.search(embs[0], top_k=5)
    assert res[0]["match"] is True
    # others should be well below 0.9 with random embeddings
    assert all(r["match"] is False for r in res[1:])
