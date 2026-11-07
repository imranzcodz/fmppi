"""Loss functions for FMPPI Siamese training.

Contrastive and triplet losses operate on embeddings packed into ``y_pred``:
- Contrastive: y_pred = concat(emb_a, emb_b), shape (batch, 2*dim)
- Triplet:     y_pred = concat(emb_a, emb_p, emb_n), shape (batch, 3*dim)
"""

from __future__ import annotations

import keras
import tensorflow as tf


def _split_embeddings(y_pred: tf.Tensor, embedding_dim: int, n: int) -> list[tf.Tensor]:
    return tf.split(y_pred, num_or_size_splits=[embedding_dim] * n, axis=1)


def _euclidean_distance(a: tf.Tensor, b: tf.Tensor) -> tf.Tensor:
    return tf.sqrt(tf.reduce_sum(tf.square(a - b), axis=1, keepdims=True) + 1e-8)


def contrastive_loss(margin: float = 1.0):
    """Contrastive loss (Hadsell et al. 2006).

    y_true in {0,1}; y_pred = concat(emb_a, emb_b).
    L = y * d^2 + (1 - y) * max(margin - d, 0)^2
    """

    def loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        emb_a, emb_b = _split_embeddings(y_pred, int(y_pred.shape[1] // 2), 2)
        d = _euclidean_distance(emb_a, emb_b)
        d_sq = tf.square(d)
        margin_sq = tf.square(margin - d)
        loss = y_true * d_sq + (1.0 - y_true) * tf.maximum(margin_sq, 0.0)
        return tf.reduce_mean(loss)

    return loss


def triplet_loss(margin: float = 1.0):
    """Triplet loss with semi-hard-friendly margin.

    y_true ignored; y_pred = concat(emb_a, emb_p, emb_n).
    L = max(d(a,p) - d(a,n) + margin, 0)
    """

    def loss(y_true, y_pred):
        del y_true
        emb_a, emb_p, emb_n = _split_embeddings(y_pred, int(y_pred.shape[1] // 3), 3)
        d_ap = _euclidean_distance(emb_a, emb_p)
        d_an = _euclidean_distance(emb_a, emb_n)
        return tf.reduce_mean(tf.maximum(d_ap - d_an + margin, 0.0))

    return loss


class ContrastiveLoss(keras.losses.Loss):
    def __init__(self, margin: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.margin = margin
        self._fn = contrastive_loss(margin)

    def call(self, y_true, y_pred):
        return self._fn(y_true, y_pred)

    def get_config(self):
        return {"margin": self.margin, **super().get_config()}


class TripletLoss(keras.losses.Loss):
    def __init__(self, margin: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.margin = margin
        self._fn = triplet_loss(margin)

    def call(self, y_true, y_pred):
        return self._fn(y_true, y_pred)

    def get_config(self):
        return {"margin": self.margin, **super().get_config()}
