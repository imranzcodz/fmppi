"""Unit tests for the FMPPI Siamese model and losses."""

import numpy as np
import tensorflow as tf

import os
os.environ.setdefault("KERAS_BACKEND", "tensorflow")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")


from ml.model.loss import ContrastiveLoss, TripletLoss  # noqa: E402
from ml.model.siamese import build_encoder, build_siamese, encode  # noqa: E402


def test_encoder_output_shape_and_l2norm():
    encoder = build_encoder(input_shape=(112, 112, 3), embedding_dim=512)
    x = np.random.rand(2, 112, 112, 3).astype(np.float32)
    emb = encode(encoder, x)
    assert emb.shape == (2, 512)
    norms = np.linalg.norm(emb, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)


def test_siamese_forward_shape():
    siamese = build_siamese(input_shape=(112, 112, 3), embedding_dim=512, n_inputs=2)
    xa = np.random.rand(2, 112, 112, 3).astype(np.float32)
    xb = np.random.rand(2, 112, 112, 3).astype(np.float32)
    out = siamese([xa, xb], training=False)
    assert out.shape == (2, 1024)


def test_weight_tying():
    siamese = build_siamese(input_shape=(112, 112, 3), embedding_dim=512, n_inputs=2)
    # Both branches share the same encoder object; verify output equality for identical input.
    x = np.random.rand(1, 112, 112, 3).astype(np.float32)
    out = siamese([x, x], training=False)
    ea, eb = out[:, :512], out[:, 512:]
    assert np.allclose(ea, eb, atol=1e-5)


def test_encode_helper():
    encoder = build_encoder(input_shape=(112, 112, 3), embedding_dim=512)
    faces = np.random.rand(3, 112, 112, 3).astype(np.float32)
    emb = encode(encoder, faces)
    assert emb.shape == (3, 512)


def test_contrastive_loss_value():
    loss_fn = ContrastiveLoss(margin=1.0)
    # identical embeddings, label 1 -> loss ~ 0
    emb = np.tile(np.array([1.0, 0.0]), (2, 1)).astype(np.float32)
    y_pred = tf.constant(np.concatenate([emb, emb], axis=1))
    y_true = tf.constant([1.0, 1.0])
    loss_val = float(loss_fn(y_true, y_pred))
    assert loss_val < 1e-3
    # far apart, label 0 within margin -> 0
    emb_a = np.array([[1.0, 0.0]], dtype=np.float32)
    emb_b = np.array([[0.0, 1.0]], dtype=np.float32)
    # distance sqrt(2) > margin 1 -> positive loss
    y_pred = tf.constant(np.concatenate([emb_a, emb_b], axis=1))
    y_true = tf.constant([0.0])
    loss_val = float(loss_fn(y_true, y_pred))
    assert loss_val > 0.0


def test_triplet_loss_value():
    loss_fn = TripletLoss(margin=1.0)
    # a close to p, far from n -> loss 0
    a = np.array([[1.0, 0.0]], dtype=np.float32)
    p = np.array([[1.0, 0.0]], dtype=np.float32)
    n = np.array([[0.0, 1.0]], dtype=np.float32)
    y_pred = tf.constant(np.concatenate([a, p, n], axis=1))
    loss_val = float(loss_fn(tf.constant([0.0]), y_pred))
    assert loss_val == 0.0
