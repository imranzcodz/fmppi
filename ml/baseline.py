"""Baseline benchmark harness: FaceNet/ArcFace/VGGFace/DeepFace vs FMPPI.

Evaluates each embedding strategy (and the trained FMPPI encoder) on verification
and kinship pairs across all configured datasets (LFW, KinFaceW, ORL_Faces, CCTV),
reporting accuracy, AUC, EER and TAR@FAR=1e-3 per dataset. Runs on
synthetic data as a smoke test and on real datasets when present.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

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


def _load_dataset_pairs(settings, dname: str) -> List:
    """Load pairs for a specific dataset."""
    if dname == "lfw":
        pairs = load_verification_pairs(settings.datasets.lfw_root)
        for p in pairs:
            p.dataset = "lfw"
            p.pair_type = "verification"
    elif dname == "kinfacew":
        pairs = load_kinship_pairs(settings.datasets.kinfacew_root)
        for p in pairs:
            p.dataset = "kinfacew"
            p.pair_type = "kinship"
    elif dname == "orl_faces":
        from ml.datasets import load_orl_faces

        pairs = load_orl_faces(settings.datasets.orl_faces_root)
        for p in pairs:
            p.dataset = "orl_faces"
            p.pair_type = "verification"
    elif dname == "cctv":
        from ml.datasets import load_cctv_detection

        pairs = load_cctv_detection(settings.datasets.cctv_root)
        for p in pairs:
            p.dataset = "cctv"
            p.pair_type = "verification"
    else:
        pairs = []
    return pairs


def main(argv=None):
    parser = argparse.ArgumentParser(description="Baseline benchmark: FaceNet/ArcFace/VGGFace/DeepFace vs FMPPI")
    parser.add_argument("--config", default="ml/config/default.yaml", help="Path to YAML config")
    parser.add_argument(
        "--dataset",
        choices=["lfw", "kinfacew", "orl_faces", "cctv", "all"],
        default="all",
        help="Dataset to evaluate on (default: all)",
    )
    args = parser.parse_args(argv)
    settings = load_config(args.config)
    size = settings.image.size[0]

    datasets_to_run = ["lfw", "kinfacew", "orl_faces", "cctv"] if args.dataset == "all" else [args.dataset]

    results: Dict[str, dict] = {"n_pairs_per_dataset": {}, "source": "synthetic" if settings.datasets.synthetic_fallback else "real"}

    for dname in datasets_to_run:
        pairs = _load_dataset_pairs(settings, dname)
        if not pairs and settings.datasets.synthetic_fallback:
            pairs = synthetic_verification_pairs(
                n_pairs=128, image_size=(size, size), seed=settings.seed
            )
            for p in pairs:
                p.dataset = dname
        if not pairs:
            results[dname] = {"error": "no pairs available"}
            continue

        data = _pair_arrays(pairs, size)
        if data is None:
            results[dname] = {"error": "no images loadable"}
            continue
        x_a, x_b, y = data
        results["n_pairs_per_dataset"][dname] = int(len(y))

        ds_results: Dict[str, dict] = {}

        # Baselines
        for name in ("facenet", "arcface", "vggface", "deepface"):
            try:
                embedder = build_embedder(
                    name,
                    detector_backend=settings.embedder.deepface_detector_backend,
                    enforce_detection=settings.embedder.enforce_detection,
                )
                ds_results[name] = evaluate_embedder(
                    embedder, x_a, x_b, y, settings.image.normalization
                )
            except Exception as exc:  # pragma: no cover - backend dependent
                ds_results[name] = {"error": str(exc)}

        # FMPPI custom encoder
        ckpt_dir = resolve(settings.mlflow.artifact_root)
        encoder_path = os.path.join(ckpt_dir, "fmppt_encoder.keras")
        if os.path.exists(encoder_path):
            import keras

            encoder = keras.models.load_model(encoder_path, compile=False, safe_mode=False)
            ds_results["fmppt"] = evaluate_fmppi(
                encoder, x_a, x_b, y, settings.image.normalization
            )
        else:
            ds_results["fmppt"] = {"note": "no trained checkpoint; run train.py first"}

        results[dname] = ds_results

    print(json.dumps(results, indent=2, default=str))
    return results


if __name__ == "__main__":
    main()
