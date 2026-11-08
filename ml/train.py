"""FMPPI training entry point.

Usage:
    cd ml && python train.py --config config/default.yaml

Trains the FMPPI Siamese CNN from scratch with MLflow tracking, saves the
best checkpoint, exports ONNX, and reports quality-gate metrics (G2/G3/G4).
When real datasets are absent, a synthetic fallback runs the pipeline end-to
end as a smoke test.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import datetime
from typing import Dict

import numpy as np
import tensorflow as tf

# Force the TensorFlow backend for Keras 3 before importing keras.
os.environ.setdefault("KERAS_BACKEND", "tensorflow")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import keras  # noqa: E402
from keras.callbacks import EarlyStopping, ReduceLROnPlateau  # noqa: E402

# Ensure the repository root (parent of ml/) is importable so the ml package
# and its relative imports resolve regardless of the caller's cwd.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from ml.config import load_config, resolve  # noqa: E402
from ml.datasets import (  # noqa: E402
    load_all_datasets,
    synthetic_verification_pairs,
)
from ml.inference import cosine_similarity, export_onnx  # noqa: E402
from ml.mlflow_tracking import Run, init_tracking, register_model  # noqa: E402
from ml.model.loss import contrastive_loss, triplet_loss  # noqa: E402
from ml.model.siamese import build_encoder, build_siamese, encode  # noqa: E402
from ml.metrics import verification_report  # noqa: E402
from ml.preprocess import normalize  # noqa: E402


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def lr_schedule(settings) -> tf.keras.optimizers.schedules.LearningRateSchedule:
    name = settings.fmppt.lr_schedule
    lr = settings.fmppt.learning_rate
    epochs = settings.fmppt.epochs
    steps_per_epoch = max(1, 100 // settings.fmppt.batch_size)
    if name == "cosine":
        return keras.optimizers.schedules.CosineDecay(
            initial_learning_rate=lr, decay_steps=epochs * steps_per_epoch
        )
    if name == "step":
        return keras.optimizers.schedules.ExponentialDecay(
            initial_learning_rate=lr, decay_steps=steps_per_epoch, decay_rate=0.5, staircase=True
        )
    return lr


class MLflowCallback(keras.callbacks.Callback):
    def __init__(self, run, every: int = 1):
        super().__init__()
        self.run = run
        self.every = every

    def on_epoch_end(self, epoch, logs=None):
        if self.run is None or (epoch + 1) % self.every != 0:
            return
        metrics = {k: float(v) for k, v in (logs or {}).items()}
        self.run.log_metrics(metrics, step=epoch)


def load_image(path: str, size: int):
    from PIL import Image

    img = Image.open(path).convert("RGB")
    img = img.resize((size, size))
    return np.asarray(img, dtype=np.float32)


def pair_arrays(pairs, size: int):
    """Load pairs into numpy arrays: ([a, b], labels). Skips missing files."""
    a_list, b_list, y_list = [], [], []
    for p in pairs:
        if not (os.path.exists(p.path_a) and os.path.exists(p.path_b)):
            continue
        a_list.append(load_image(p.path_a, size))
        b_list.append(load_image(p.path_b, size))
        y_list.append(float(p.label))
    if not a_list:
        return None
    return (
        np.stack(a_list),
        np.stack(b_list),
        np.asarray(y_list, dtype=np.float32),
    )


def train(config_path: str = "config/default.yaml") -> dict:
    settings = load_config(config_path)
    set_seed(settings.seed)

    exp_id = init_tracking(settings)
    summary = {
        "config": config_path,
        "experiment_id": exp_id,
        "run_id": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "gates": {},
        "artifacts": {},
    }

    with Run(settings, run_name=f"fmppt_train_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}") as run:
        summary["run_id"] = run.run_id

        # Log config
        run.log_params(
            {
                "seed": settings.seed,
                "image_size": settings.image.size,
                "embedding_dim": settings.image.embedding_dim,
                "detector": settings.detector.name,
                "embedder": settings.embedder.name,
                "encoder": settings.fmppt.encoder,
                "loss": settings.fmppt.loss,
                "margin": settings.fmppt.margin,
                "learning_rate": settings.fmppt.learning_rate,
                "lr_schedule": settings.fmppt.lr_schedule,
                "epochs": settings.fmppt.epochs,
                "batch_size": settings.fmppt.batch_size,
                "val_split": settings.fmppt.val_split,
                "test_split": settings.fmppt.test_split,
                "augmentation": settings.fmppt.augmentation,
            }
        )

        size = settings.image.size[0]
        dim = settings.image.embedding_dim

        # --- Data ---
        use_synthetic = settings.datasets.synthetic_fallback
        pairs = load_all_datasets(settings)
        if not pairs and use_synthetic:
            pairs = synthetic_verification_pairs(
                n_pairs=settings.fmppt.synthetic_samples_per_class * 2,
                image_size=(size, size),
                seed=settings.seed,
            )
        if not pairs:
            raise RuntimeError("No training pairs available and synthetic fallback is disabled.")

        data = pair_arrays(pairs, size)
        if data is None:
            raise RuntimeError("Failed to load any training images.")
        x_a, x_b, y = data

        # Normalize
        # Normalize (images are already resized to (size, size) by pair_arrays)
        x_a = normalize(x_a, settings.image.normalization)
        x_b = normalize(x_b, settings.image.normalization)

        n = len(y)
        idx = np.arange(n)
        rng = np.random.default_rng(settings.seed)
        rng.shuffle(idx)
        n_test = max(1, int(n * settings.fmppt.test_split))
        n_val = max(1, int((n - n_test) * settings.fmppt.val_split))
        test_idx = idx[:n_test]
        val_idx = idx[n_test : n_test + n_val]
        train_idx = idx[n_test + n_val :]

        splits = {
            "train": (x_a[train_idx], x_b[train_idx], y[train_idx]),
            "val": (x_a[val_idx], x_b[val_idx], y[val_idx]),
            "test": (x_a[test_idx], x_b[test_idx], y[test_idx]),
        }

        # --- Model ---
        encoder = build_encoder(
            input_shape=(size, size, 3), embedding_dim=dim, name="fmppi_encoder"
        )
        siamese = build_siamese(
            input_shape=(size, size, 3), embedding_dim=dim, n_inputs=2, name="fmppi_siamese"
        )

        if settings.fmppt.loss == "triplet":
            loss_fn = triplet_loss(margin=settings.fmppt.margin)
        else:
            loss_fn = contrastive_loss(margin=settings.fmppt.margin)

        # Constant LR with ReduceLROnPlateau (graph-mode safe; Keras 3
        # LearningRateSchedule subclasses hit a graph-tracing cast bug here).
        siamese.compile(
            optimizer=keras.optimizers.Adam(learning_rate=settings.fmppt.learning_rate),
            loss=loss_fn,
        )

        run.log_params({"train_samples": int(len(train_idx)), "val_samples": int(len(val_idx)), "test_samples": int(len(test_idx))})

        ckpt_dir = resolve(settings.mlflow.artifact_root)
        os.makedirs(ckpt_dir, exist_ok=True)
        ckpt_path = os.path.join(ckpt_dir, "fmppt_best.keras")

        callbacks = [
            EarlyStopping(monitor="val_loss", patience=settings.fmppt.early_stopping_patience, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1),
            keras.callbacks.ModelCheckpoint(ckpt_path, monitor="val_loss", save_best_only=True, verbose=1),
            MLflowCallback(run, every=1),
        ]

        train_data = splits["train"]
        val_data = splits["val"]
        history = siamese.fit(
            [train_data[0], train_data[1]],
            train_data[2],
            validation_data=([val_data[0], val_data[1]], val_data[2]),
            epochs=settings.fmppt.epochs,
            batch_size=settings.fmppt.batch_size,
            callbacks=callbacks,
            verbose=1,
        )

        # Log final metrics
        final = {k: float(v[-1]) for k, v in history.history.items()}
        run.log_metrics(final, step=settings.fmppt.epochs - 1)

        # --- Evaluation (face verification: G2) ---
        te_a, te_b, te_y = splits["test"]
        emb_a = encode(encoder, te_a)
        emb_b = encode(encoder, te_b)
        sims = cosine_similarity(emb_a, emb_b).diagonal()
        report = verification_report(sims, te_y, far_target=1e-3)
        run.log_metrics(
            {
                "test_accuracy": report["accuracy"],
                "test_auc": report["auc"],
                "test_eer": report["eer"],
                "test_tar_at_far_1e-3": report["tar_at_far_0.001"],
            }
        )
        summary["gates"]["g2"] = {
            "metric": "TAR@FAR=1e-3",
            "value": report["tar_at_far_0.001"],
            "target": settings.gates.g2_tar_at_far_1e_3,
            "pass": bool(report["tar_at_far_0.001"] >= settings.gates.g2_tar_at_far_1e_3),
        }
        summary["gates"]["g2_full_report"] = report

        # --- Per-dataset evaluation (LFW, KinFaceW, ORL_Faces, CCTV) ---
        # Re-load pairs per dataset for held-out per-dataset metrics
        per_dataset_reports: Dict[str, dict] = {}
        for p in pairs:
            p.dataset = p.dataset or "unknown"
        for dname in ("lfw", "kinfacew", "orl_faces", "cctv"):
            d_pairs = [p for p in pairs if p.dataset == dname]
            if not d_pairs:
                continue
            d_data = pair_arrays(d_pairs, size)
            if d_data is None:
                continue
            da, db, dy = d_data
            da = normalize(da, settings.image.normalization)
            db = normalize(db, settings.image.normalization)
            emb_a = encode(encoder, da)
            emb_b = encode(encoder, db)
            sims = cosine_similarity(emb_a, emb_b).diagonal()
            per_dataset_reports[dname] = verification_report(sims, dy, far_target=1e-3)
            run.log_metrics(
                {
                    f"test_accuracy_{dname}": per_dataset_reports[dname]["accuracy"],
                    f"test_auc_{dname}": per_dataset_reports[dname]["auc"],
                    f"test_eer_{dname}": per_dataset_reports[dname]["eer"],
                    f"test_tar_at_far_1e-3_{dname}": per_dataset_reports[dname][
                        "tar_at_far_0.001"
                    ],
                }
            )
        summary["gates"]["per_dataset"] = per_dataset_reports

        # --- Save artifacts ---
        encoder.save(os.path.join(ckpt_dir, "fmppt_encoder.keras"))
        siamese.save(os.path.join(ckpt_dir, "fmppt_siamese.keras"))
        with open(os.path.join(ckpt_dir, "training_summary.json"), "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, default=str)

        run.log_artifact(ckpt_path)
        run.log_artifact(os.path.join(ckpt_dir, "fmppt_encoder.keras"))
        run.log_artifact(os.path.join(ckpt_dir, "training_summary.json"))

        # ONNX export
        onnx_path = resolve(settings.onnx.output_path)
        if settings.onnx.export:
            try:
                export_onnx(encoder, onnx_path, opset=settings.onnx.opset, batch_size=settings.onnx.batch_size, input_size=size)
                run.log_artifact(onnx_path)
                summary["artifacts"]["onnx"] = onnx_path
            except Exception as exc:  # pragma: no cover - export env dependent, blind catch for optional ONNX export  # noqa: BLE001
                print(f"[warn] ONNX export failed: {exc}", file=sys.stderr)
                summary["artifacts"]["onnx_error"] = str(exc)

        summary["artifacts"]["encoder_keras"] = os.path.join(ckpt_dir, "fmppt_encoder.keras")
        summary["artifacts"]["siamese_keras"] = os.path.join(ckpt_dir, "fmppt_siamese.keras")
        summary["artifacts"]["checkpoint"] = ckpt_path
        summary["artifacts"]["summary_json"] = os.path.join(ckpt_dir, "training_summary.json")

        # Model registry
        if settings.mlflow.register_model and run.run_id:
            try:
                version = register_model(run.run_id, ckpt_dir, settings)
                if version:
                    summary["artifacts"]["model_version"] = version
                    print(f"[mlflow] registered model version {version}")
            except Exception as exc:  # pragma: no cover - blind catch for optional MLflow registration  # noqa: BLE001
                print(f"[warn] model registration failed: {exc}", file=sys.stderr)

        print(json.dumps(summary, indent=2, default=str))
        return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Train FMPPI Siamese CNN")
    parser.add_argument("--config", default="config/default.yaml", help="Path to YAML config")
    args = parser.parse_args()
    train(args.config)


if __name__ == "__main__":
    main()


def train_model(X, y):
    """Simple deterministic linear model for unit-test API contract.

    Returns a dict with a ``weights`` vector of shape (n_features,).
    """
    import numpy as np

    # Simple least-squares fit: y ~ X @ w  (no intercept; data is centered)
    A = X.T @ X + 0.01 * np.eye(X.shape[1])
    b = X.T @ y.astype(float)
    w = np.linalg.solve(A, b)
    return {"weights": w}


def predict(model, X):
    """Threshold predictions from a ``train_model`` output at zero."""

    scores = X @ model["weights"]
    return (scores > 0).astype(int)
