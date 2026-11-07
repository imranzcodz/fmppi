"""FMPPI robustness evaluation entry point: G4 gate.

Usage:
    python ml/eval/robustness.py --config ml/config/default.yaml --gate

Applies the degradation suite (blur/noise/low-res/pose/illum/occlusion/aging)
at mild/moderate/severe severity, computes verification accuracy delta vs. the
clean baseline, and checks G4 (robustness >= 60% under severe degradation).
Exits non-zero when the gate is not met.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

os.environ.setdefault("KERAS_BACKEND", "tensorflow")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import keras  # noqa: E402
from PIL import Image  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.config import load_config, resolve  # noqa: E402
from ml.datasets import load_verification_pairs, synthetic_verification_pairs  # noqa: E402
from ml.robustness.eval import evaluate_robustness  # noqa: E402
from ml.model.siamese import build_encoder, encode  # noqa: E402
from ml.preprocess import preprocess  # noqa: E402


class _EncoderVerifier:
    def __init__(self, encoder, size: int, normalization: str):
        self.encoder = encoder
        self.size = size
        self.normalization = normalization

    def verify(self, path_a, path_b):
        img_a = np.asarray(Image.open(path_a).convert("RGB"))
        img_b = np.asarray(Image.open(path_b).convert("RGB"))
        ea = encode(self.encoder, preprocess(img_a, size=self.size, normalization=self.normalization)[None, :])[0]
        eb = encode(self.encoder, preprocess(img_b, size=self.size, normalization=self.normalization)[None, :])[0]
        from ml.inference import cosine_similarity

        score = float(cosine_similarity(ea[None, :], eb[None, :])[0, 0])
        return {"score": score, "similarity": score, "match": score >= 0.5}


def evaluate(config_path="config/default.yaml", gate=False):
    settings = load_config(config_path)
    size = settings.image.size[0]
    dim = settings.image.embedding_dim

    ckpt_dir = resolve(settings.mlflow.artifact_root)
    encoder_path = os.path.join(ckpt_dir, "fmppt_encoder.keras")
    if os.path.exists(encoder_path):
        encoder = keras.models.load_model(encoder_path, compile=False, safe_mode=False)
        source = "checkpoint"
    else:
        encoder = build_encoder(input_shape=(size, size, 3), embedding_dim=dim)
        source = "random-init"

    verifier = _EncoderVerifier(encoder, size, settings.image.normalization)

    pairs = load_verification_pairs(settings.datasets.lfw_root)
    if not pairs and settings.datasets.synthetic_fallback:
        pairs = synthetic_verification_pairs(
            n_pairs=128, image_size=(size, size), seed=settings.seed
        )
    if not pairs:
        raise RuntimeError("No verification pairs available for robustness eval.")

    # Write pairs to temp images if they are synthetic (already have paths); for real pairs paths exist.
    pair_dicts = [{"path_a": p.path_a, "path_b": p.path_b, "label": p.label} for p in pairs]

    results = evaluate_robustness(
        verifier,
        pair_dicts,
        degradations=settings.robustness.degradations,
        severities=settings.robustness.severities,
        size=size,
        seed=settings.seed,
    )

    summary = {
        "encoder_source": source,
        "n_pairs": len(pair_dicts),
        "g4": {
            "metric": "mean accuracy under severe degradation",
            "value": results["severe_mean_accuracy"],
            "target": settings.gates.g4_robustness_accuracy,
            "pass": bool(results["g4_pass"]),
        },
        "clean_accuracy": results["clean_accuracy"],
        "degradations": results["degradations"],
        "gate_min_accuracy": settings.robustness.gate_min_accuracy,
    }
    summary["all_gates_pass"] = bool(results["g4_pass"])

    print(json.dumps(summary, indent=2, default=str))

    if gate and not results["g4_pass"]:
        sys.exit(1)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate FMPPI robustness against gate G4")
    parser.add_argument("--config", default="config/default.yaml", help="Path to YAML config")
    parser.add_argument("--gate", action="store_true", help="Fail (exit 1) when gate is not met")
    args = parser.parse_args()
    evaluate(args.config, gate=args.gate)


if __name__ == "__main__":
    main()
