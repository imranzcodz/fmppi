"""Kinship verification using the FMPPI Siamese encoder.

Given two face chips, compute embeddings via the shared encoder, compare with
a distance metric, and produce a kin / non-kin decision with a confidence score
mapped to [0, 1] via a sigmoid over the (margin - distance).
"""

from __future__ import annotations


import numpy as np

from .inference import cosine_similarity, euclidean_distance
from .model.siamese import build_encoder


class KinshipVerifier:
    def __init__(
        self,
        encoder=None,
        threshold: float = 0.5,
        metric: str = "cosine",
        temperature: float = 1.0,
        embedding_dim: int = 512,
        input_size: int = 112,
    ) -> None:
        self.encoder = encoder
        self._owns_encoder = encoder is None
        if self._owns_encoder:
            self.encoder = build_encoder(
                input_shape=(input_size, input_size, 3), embedding_dim=embedding_dim
            )
        self.threshold = threshold
        self.metric = metric
        self.temperature = temperature

    def encode(self, face) -> np.ndarray:
        from .model.siamese import encode

        return encode(self.encoder, face)

    def verify(
        self, face_a, face_b
    ) -> dict:
        emb_a = self.encode(face_a).ravel()
        emb_b = self.encode(face_b).ravel()
        if self.metric == "cosine":
            score = float(cosine_similarity(emb_a[None, :], emb_b[None, :])[0, 0])
            distance = 1.0 - score
        else:
            distance = float(euclidean_distance(emb_a[None, :], emb_b[None, :])[0, 0])
            score = -distance
        # Sigmoid-based confidence mapped to [0,1]
        confidence = float(1.0 / (1.0 + np.exp((distance - self.threshold) / max(self.temperature, 1e-6))))
        is_kin = bool(confidence >= 0.5)
        return {
            "score": score,
            "distance": float(distance),
            "confidence": confidence,
            "is_kin": is_kin,
            "threshold": self.threshold,
            "metric": self.metric,
        }

    def calibrate_threshold(self, scores, labels) -> float:
        """Choose threshold maximizing kinship accuracy on a validation set."""
        from .metrics import best_threshold

        # For kinship, higher similarity = more likely kin
        thr, _ = best_threshold(np.asarray(scores, dtype=np.float64), np.asarray(labels, dtype=np.int64))
        self.threshold = float(thr)
        return self.threshold
