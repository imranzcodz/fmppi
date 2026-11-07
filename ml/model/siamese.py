"""FMPPI Siamese CNN: weight-tied shared encoder.

Architecture: twin branches share one encoder (Conv -> BN -> ReLU -> MaxPool
blocks) -> global pooling -> dense projection -> L2-normalized 512-d embedding.
The siamese model takes two (or three) face chips and outputs the concatenated
embeddings for contrastive/triplet loss.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
import keras


def _conv_block(x, filters: int, kernel_size: int = 3, strides: int = 1, name: str = ""):
    x = keras.layers.Conv2D(
        filters, kernel_size, strides=strides, padding="same",
        kernel_initializer="he_normal", name=f"{name}_conv",
    )(x)
    x = keras.layers.BatchNormalization(name=f"{name}_bn")(x)
    x = keras.layers.Activation("relu", name=f"{name}_relu")(x)
    x = keras.layers.MaxPooling2D(pool_size=2, name=f"{name}_pool")(x)
    return x


def build_encoder(
    input_shape: Tuple[int, int, int] = (112, 112, 3),
    embedding_dim: int = 512,
    name: str = "fmppi_encoder",
) -> keras.Model:
    """Shared weight-tied encoder."""
    inputs = keras.Input(shape=input_shape, name=f"{name}_input")
    x = _conv_block(inputs, 32, name=f"{name}_b1")
    x = _conv_block(x, 64, name=f"{name}_b2")
    x = _conv_block(x, 128, name=f"{name}_b3")
    x = _conv_block(x, 256, name=f"{name}_b4")
    x = keras.layers.GlobalAveragePooling2D(name=f"{name}_gap")(x)
    x = keras.layers.Dense(512, activation="relu", kernel_initializer="he_normal", name=f"{name}_dense")(x)
    x = keras.layers.Dropout(0.3, name=f"{name}_dropout")(x)
    embeddings = keras.layers.Dense(embedding_dim, name=f"{name}_embedding")(x)
    return keras.Model(inputs, embeddings, name=name)


def build_siamese(
    input_shape: Tuple[int, int, int] = (112, 112, 3),
    embedding_dim: int = 512,
    n_inputs: int = 2,
    name: str = "fmppi_siamese",
) -> keras.Model:
    """Siamese model with weight-tied encoder shared across all branches."""
    encoder = build_encoder(input_shape=input_shape, embedding_dim=embedding_dim, name=f"{name}_encoder")
    inputs = []
    embeddings = []
    for i in range(n_inputs):
        inp = keras.Input(shape=input_shape, name=f"{name}_input_{i}")
        emb = encoder(inp)
        inputs.append(inp)
        embeddings.append(emb)
    merged = keras.layers.Concatenate(name=f"{name}_concat")(embeddings)
    return keras.Model(inputs, merged, name=name)


def encode(encoder: keras.Model, faces) -> np.ndarray:
    """Encode a batch of face chips to L2-normalized embeddings."""
    arr = np.asarray(faces, dtype=np.float32)
    if arr.ndim == 3:
        arr = arr[None, ...]
    emb = np.asarray(encoder(arr, training=False))
    # L2-normalize so cosine similarity and Euclidean distance are consistent.
    n = np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12
    return (emb / n).astype(np.float32)
