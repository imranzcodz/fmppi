"""Inference, ONNX export and serving utilities for FMPPI.

Exports the trained Keras siamese encoder to ONNX for CPU-friendly serving
(cPanel-compatible via onnxruntime), and provides a small inference wrapper
that computes embeddings and similarity scores.
"""

from __future__ import annotations

import json
import os
from typing import List, Tuple

import numpy as np
import onnxruntime as ort

from .config import resolve


class ONNXEncoder:
    """ONNXRuntime wrapper around the exported FMPPI encoder."""

    def __init__(self, model_path: str, input_size: int = 112) -> None:
        self.model_path = resolve(model_path) if not os.path.isabs(model_path) else model_path
        self.input_size = input_size
        self._session = None
        self._input_name = None
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"ONNX model not found: {self.model_path}")
        so = ort.SessionOptions()
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self._session = ort.InferenceSession(self.model_path, sess_options=so, providers=["CPUExecutionProvider"])
        self._input_name = self._session.get_inputs()[0].name

    def embed(self, faces) -> np.ndarray:
        import numpy as np

        arr = np.asarray(faces, dtype=np.float32)
        if arr.ndim == 3:
            arr = arr[None, ...]
        outs = self._session.run(None, {self._input_name: arr})
        emb = outs[0]
        # L2-normalize defensively
        n = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12
        return (emb / n).astype(np.float32)

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        a = np.asarray(a, dtype=np.float32).ravel()
        b = np.asarray(b, dtype=np.float32).ravel()
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
        return float(np.dot(a, b) / denom)


def export_onnx(keras_model, output_path: str, opset: int = 13, batch_size: int = 1, input_size: int = 112) -> str:
    """Export a Keras encoder model to ONNX via tf2onnx."""
    import os

    import tensorflow as tf
    from tf2onnx.convert import from_keras

    output_path = resolve(output_path) if not os.path.isabs(output_path) else output_path
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    input_signature = [
        tf.TensorSpec(
            shape=[batch_size, input_size, input_size, 3], dtype=tf.float32, name="input"
        )
    ]
    model_proto, _ = from_keras(
        keras_model,
        input_signature=input_signature,
        opset=opset,
        output_path=output_path,
    )
    return output_path


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    if a.ndim == 1:
        a = a[None, :]
    if b.ndim == 1:
        b = b[None, :]
    a_n = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-12)
    b_n = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-12)
    return a_n @ b_n.T


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    if a.ndim == 1:
        a = a[None, :]
    if b.ndim == 1:
        b = b[None, :]
    return np.sqrt(np.sum((a[:, None, :] - b[None, :, :]) ** 2, axis=-1) + 1e-8)


def save_search_index(embeddings: np.ndarray, identities: List[str], path: str) -> None:
    path = resolve(path) if not os.path.isabs(path) else path
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    payload = {
        "embeddings": embeddings.astype(np.float32).tolist(),
        "identities": [str(i) for i in identities],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)


def load_search_index(path: str) -> Tuple[np.ndarray, List[str]]:
    path = resolve(path) if not os.path.isabs(path) else path
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return np.asarray(payload["embeddings"], dtype=np.float32), [str(i) for i in payload["identities"]]
