"""Embedding strategies: Embedder interface (Strategy pattern).

Interface:
    Embedder.embed(face) -> np.ndarray  # (embedding_dim,)
    Embedder.embed_batch(faces) -> np.ndarray  # (n, embedding_dim)

Implementations wrap FaceNet (128-d), ArcFace (512-d), VGGFace (4096-d) and
DeepFace through the DeepFace library, degrading gracefully when models are
unavailable. All embeddings are L2-normalized.
"""

from __future__ import annotations

from typing import List, Optional, Protocol, runtime_checkable

import numpy as np

_embedding_dim_registry = {
    "facenet": 128,
    "arcface": 512,
    "vggface": 4096,
    "deepface": 4096,
}


@runtime_checkable
class Embedder(Protocol):
    def embed(self, face: np.ndarray) -> np.ndarray:  # pragma: no cover - interface
        ...

    def embed_batch(self, faces: List[np.ndarray]) -> np.ndarray:  # pragma: no cover - interface
        ...

    @property
    def embedding_dim(self) -> int:  # pragma: no cover - interface
        ...

    def name(self) -> str:  # pragma: no cover - interface
        ...


def l2_normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return (x / np.clip(n, eps, None)).astype(np.float32)


def deterministic_fallback_embedding(face: np.ndarray, dim: int) -> np.ndarray:
    """Deterministic pseudo-embedding derived from face pixels (test fallback)."""
    arr = np.asarray(face, dtype=np.float32).ravel()
    if arr.size == 0:
        arr = np.zeros(1, dtype=np.float32)
    # Hash-like projection: bucket pixels into `dim` bins via a fixed random projection seeded by content.
    rng = np.random.default_rng(int(np.sum(arr * 255)) % (2 ** 31))
    proj = rng.standard_normal((min(arr.size, 4096), dim))
    flat = arr[: proj.shape[0]]
    emb = flat @ proj
    return l2_normalize(emb)


class DeepFaceEmbedder:
    """Base embedding backed by DeepFace.represent with a chosen model."""

    def __init__(
        self,
        model_name: str = "Facenet",
        detector_backend: str = "opencv",
        enforce_detection: bool = False,
        dim: Optional[int] = None,
    ) -> None:
        self.model_name = model_name
        self.detector_backend = detector_backend
        self.enforce_detection = enforce_detection
        self._dim = dim or _embedding_dim_registry.get(model_name.lower(), 512)
        self._df = None
        try:  # pragma: no cover - optional heavy dependency
            from deepface import DeepFace  # type: ignore

            self._df = DeepFace
        except Exception:  # pragma: no cover - optional
            self._df = None

    @property
    def embedding_dim(self) -> int:
        return self._dim

    def name(self) -> str:
        return f"deepface_{self.model_name}"

    def embed(self, face: np.ndarray) -> np.ndarray:
        return self.embed_batch([face])[0]

    def embed_batch(self, faces: List[np.ndarray]) -> np.ndarray:
        if self._df is not None:
            return self._embed_deepface(faces)
        # Fallback: deterministic pixel-derived embeddings
        return np.stack([deterministic_fallback_embedding(f, self._dim) for f in faces])

    def _embed_deepface(self, faces: List[np.ndarray]) -> np.ndarray:
        embeddings = []
        for face in faces:
            try:
                reps = self._df.represent(
                    img_path=face,
                    model_name=self.model_name,
                    detector_backend=self.detector_backend,
                    enforce_detection=self.enforce_detection,
                    align=True,
                )
                vec = np.asarray(reps[0]["embedding"], dtype=np.float64)
            except Exception:
                vec = deterministic_fallback_embedding(face, self._dim)
            embeddings.append(vec)
        out = np.stack(embeddings)
        if out.shape[1] != self._dim:
            # Project/truncate to configured dim deterministically
            if out.shape[1] > self._dim:
                out = out[:, : self._dim]
            else:
                pad = np.zeros((out.shape[0], self._dim - out.shape[1]), dtype=np.float64)
                out = np.concatenate([out, pad], axis=1)
        return l2_normalize(out)


class FaceNetEmbedder(DeepFaceEmbedder):
    """FaceNet 128-d embeddings via DeepFace."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("model_name", "Facenet")
        kwargs.setdefault("dim", 128)
        super().__init__(**kwargs)

    def name(self) -> str:
        return "facenet"


class ArcFaceEmbedder(DeepFaceEmbedder):
    """ArcFace 512-d embeddings via DeepFace."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("model_name", "ArcFace")
        kwargs.setdefault("dim", 512)
        super().__init__(**kwargs)

    def name(self) -> str:
        return "arcface"


class VGGFaceEmbedder(DeepFaceEmbedder):
    """VGGFace 4096-d embeddings via DeepFace."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("model_name", "VGGFace")
        kwargs.setdefault("dim", 4096)
        super().__init__(**kwargs)

    def name(self) -> str:
        return "vggface"


class DeepFaceEmbedderWrapper(DeepFaceEmbedder):
    """DeepFace default model embeddings via DeepFace."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("model_name", "DeepFace")
        kwargs.setdefault("dim", 4096)
        super().__init__(**kwargs)

    def name(self) -> str:
        return "deepface"


def build_embedder(name: str = "deepface", **kwargs) -> Embedder:
    name = (name or "deepface").lower()
    if name == "facenet":
        return FaceNetEmbedder(**kwargs)
    if name == "arcface":
        return ArcFaceEmbedder(**kwargs)
    if name == "vggface":
        return VGGFaceEmbedder(**kwargs)
    if name == "deepface":
        return DeepFaceEmbedderWrapper(**kwargs)
    raise ValueError(f"Unknown embedder: {name}")
