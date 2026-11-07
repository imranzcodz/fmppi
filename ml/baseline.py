"""Baseline benchmark harness: FaceNet/ArcFace/VGGFace/DeepFace vs FMPPI.

Evaluates each embedding strategy (and the trained FMPPI encoder) on verification
and kinship pairs, reporting accuracy, AUC, EER and TAR@FAR=1e-3. Runs on
synthetic data as a smoke test and on real KinFaceW/LFW when present.
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np

os.environ.setdefault("KERAS_BACKEND", "tensorflow")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.config import load_config, resolve  # noqa: E402
from ml.datasets import (  # noqa: E402
    load_kinship_pairs,
    load_verification_pairs,
    synthetic_verification_pairs,
)
from ml.embedding import build_embedder  # noqa: E402
from ml.inference import cosine_similarity  # noqa: E402
from ml.metrics import verification_report  # noqa: E402
from ml.model.siamese import encode  # noqa: E402
from ml.preprocess import normalize  # noqa: E402


def _pair_arrays(pairs, size: int):
    from PIL import Image

    a_list, b_list, y_list = [], [], []
    for p in pairs:
        if not (os.path.exists(p.path_a) and os.path.exists(p.path_b)):
            continue
        a_list.append(
            np.asarray(Image.open(p.path_a).convert("RGB").resize((size, size)), dtype=np.float32)
        )
        b_list.append(
            np.asarray(Image.open(p.path_b).convert("RGB").resize((size, size)), dtype=np.float32)
        )
        y_list.append(float(p.label))
    if not a_list:
        return None
    return np.stack(a_list), np.stack(b_list), np.asarray(y_list, dtype=np.float32)


def evaluate_embedder(embedder, x_a, x_b, y, normalization: str):
    x_a = normalize(x_a, normalization)
    x_b = normalize(x_b, normalization)
    emb_a = np.stack([embedder.embed(f) for f in x_a])
    emb_b = np.stack([embedder.embed(f) for f in x_b])
    sims = cosine_similarity(emb_a, emb_b).diagonal()
    return verification_report(sims, y, far_target=1e-3)


def evaluate_fmppi(encoder, x_a, x_b, y, normalization: str):
    x_a = normalize(x_a, normalization)
    x_b = normalize(x_b, normalization)
    emb_a = encode(encoder, x_a)
    emb_b = encode(encoder, x_b)
    sims = cosine_similarity(emb_a, emb_b).diagonal()
    return verification_report(sims, y, far_target=1e-3)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Baseline benchmark: FaceNet/ArcFace/VGGFace/DeepFace vs FMPPI")
    parser.add_argument("--config", default="ml/config/default.yaml", help="Path to YAML config")
    args = parser.parse_args(argv)
    settings = load_config(args.config)
    size = settings.image.size[0]

    pairs = load_verification_pairs(settings.datasets.lfw_root)
    if not pairs and settings.datasets.synthetic_fallback:
        pairs = synthetic_verification_pairs(
            n_pairs=128, image_size=(size, size), seed=settings.seed
        )
    if not pairs:
        raise RuntimeError("No verification pairs available.")

    data = _pair_arrays(pairs, size)
    if data is None:
        raise RuntimeError("No verification images loadable.")
    x_a, x_b, y = data

    results = {
        "n_pairs": int(len(y)),
        "source": "synthetic" if settings.datasets.synthetic_fallback else "real",
    }

    # Baselines
    for name in ("facenet", "arcface", "vggface", "deepface"):
        try:
            embedder = build_embedder(
                name,
                detector_backend=settings.embedder.deepface_detector_backend,
                enforce_detection=settings.embedder.enforce_detection,
            )
            results[name] = evaluate_embedder(
                embedder, x_a, x_b, y, settings.image.normalization
            )
        except Exception as exc:  # pragma: no cover - backend dependent
            results[name] = {"error": str(exc)}

    # FMPPI custom encoder
    ckpt_dir = resolve(settings.mlflow.artifact_root)
    encoder_path = os.path.join(ckpt_dir, "fmppt_encoder.keras")
    if os.path.exists(encoder_path):
        import keras

        encoder = keras.models.load_model(encoder_path, compile=False, safe_mode=False)
        results["fmppt"] = evaluate_fmppi(
            encoder, x_a, x_b, y, settings.image.normalization
        )
    else:
        results["fmppt"] = {"note": "no trained checkpoint; run train.py first"}

    # Kinship (KinFaceW) if available
    kin_pairs = load_kinship_pairs(settings.datasets.kinfacew_root)
    if not kin_pairs and settings.datasets.synthetic_fallback:
        kin_pairs = synthetic_verification_pairs(
            n_pairs=64, image_size=(size, size), seed=settings.seed + 1
        )
        for p in kin_pairs:
            p.pair_type = "kinship"
    if kin_pairs:
        kdata = _pair_arrays(kin_pairs, size)
        if kdata is not None:
            ka, kb, ky = kdata
            kin_results = {}
            for name in ("facenet", "arcface", "vggface", "deepface"):
                try:
                    embedder = build_embedder(
                        name,
                        detector_backend=settings.embedder.deepface_detector_backend,
                        enforce_detection=settings.embedder.enforce_detection,
                    )
                    kin_results[name] = evaluate_embedder(
                        embedder, ka, kb, ky, settings.image.normalization
                    )
                except Exception as exc:  # pragma: no cover
                    kin_results[name] = {"error": str(exc)}
            if os.path.exists(encoder_path):
                import keras

                encoder = keras.models.load_model(encoder_path, compile=False, safe_mode=False)
                kin_results["fmppt"] = evaluate_fmppi(
                    encoder, ka, kb, ky, settings.image.normalization
                )
            else:
                kin_results["fmppt"] = {"note": "no trained checkpoint"}
            results["kinship"] = kin_results

    import json

    print(json.dumps(results, indent=2, default=str))
    return results


if __name__ == "__main__":
    main()
