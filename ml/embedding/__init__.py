"""Embedding strategy package re-exports."""

from .base import (
    ArcFaceEmbedder,
    DeepFaceEmbedderWrapper,
    Embedder,
    FaceNetEmbedder,
    VGGFaceEmbedder,
    build_embedder,
    deterministic_fallback_embedding,
    l2_normalize,
)

__all__ = [
    "ArcFaceEmbedder",
    "DeepFaceEmbedderWrapper",
    "Embedder",
    "FaceNetEmbedder",
    "VGGFaceEmbedder",
    "build_embedder",
    "deterministic_fallback_embedding",
    "l2_normalize",
]
