"""1:N local-verify search against a gallery of enrolled face embeddings."""

from __future__ import annotations

from typing import List, Optional

import numpy as np

from .inference import cosine_similarity, euclidean_distance, load_search_index, save_search_index


class FaceSearchIndex:
    def __init__(self, distance: str = "cosine", threshold: float = 0.4) -> None:
        self.distance = distance
        self.threshold = threshold
        self.embeddings: Optional[np.ndarray] = None
        self.identities: List[str] = []
        self.metadata: List[dict] = []

    def add(self, embeddings: np.ndarray, identities: List[str], metadata: Optional[List[dict]] = None) -> None:
        emb = np.asarray(embeddings, dtype=np.float32)
        if self.embeddings is None:
            self.embeddings = emb
        else:
            self.embeddings = np.concatenate([self.embeddings, emb], axis=0)
        self.identities.extend([str(i) for i in identities])
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(identities))

    def save(self, path: str) -> None:
        save_search_index(self.embeddings, self.identities, path)

    def load(self, path: str) -> None:
        emb, ident = load_search_index(path)
        self.embeddings = emb
        self.identities = ident
        self.metadata = [{}] * len(ident)

    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[dict]:
        if self.embeddings is None or len(self.identities) == 0:
            return []
        q = np.asarray(query_embedding, dtype=np.float32).ravel()
        if self.distance == "cosine":
            sims = cosine_similarity(self.embeddings, q[None, :]).ravel()
            order = np.argsort(-sims)
        else:
            dists = euclidean_distance(self.embeddings, q[None, :]).ravel()
            sims = -dists
            order = np.argsort(sims)[::-1]
        results = []
        for idx in order[:top_k]:
            results.append(
                {
                    "rank": len(results) + 1,
                    "identity": self.identities[int(idx)],
                    "similarity": float(sims[int(idx)]),
                    "distance": float(
                        euclidean_distance(self.embeddings[int(idx)][None, :], q[None, :])[0, 0]
                        if self.distance != "cosine"
                        else 1.0 - float(sims[int(idx)])
                    ),
                    "metadata": self.metadata[int(idx)],
                    "match": bool(
                        (sims[int(idx)] >= self.threshold)
                        if self.distance == "cosine"
                        else (euclidean_distance(self.embeddings[int(idx)][None, :], q[None, :])[0, 0] <= self.threshold)
                    ),
                }
            )
        return results
