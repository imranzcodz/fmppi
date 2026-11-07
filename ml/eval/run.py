"""FMPPI evaluation entry point: face verification (G2) and kinship (G3).

Usage:
    python ml/eval/run.py --config ml/config/default.yaml --gate

Loads the trained encoder (or a fresh one), evaluates verification on LFW-style
pairs and kinship on KinFaceW-style pairs, checks quality gates G2/G3 and prints
a JSON summary. Exits non-zero when a gate is not met.
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.config import load_config, resolve  # noqa: E402
from ml.datasets import load_kinship_pairs, load_verification_pairs, synthetic_verification_pairs  # noqa: E402
from ml.inference import cosine_similarity  # noqa: E402
from ml.metrics import verification_report, kinship_report  # noqa: E402
from ml.model.siamese import build_encoder, encode  # noqa: E402
from ml.preprocess import normalize  # noqa: E402


def load_pairs(settings):
    pairs = []
    lfw = load_verification_pairs(settings.datasets.lfw_root)
    if lfw:
        pairs.extend(("verification", p) for p in lfw)
    kin = load_kinship_pairs(settings.datasets.kinfacew_root)
    if kin:
        pairs.extend(("kinship", p) for p in kin)
    if not pairs and settings.datasets.synthetic_fallback:
        syn = synthetic_verification_pairs(
            n_pairs=256,
            image_size=(settings.image.size[0], settings.image.size[1]),
            seed=settings.seed,
        )
        pairs = [("verification", p) for p in syn]
    return pairs


def pair_arrays(pairs, size):
    from PIL import Image

    a_list, b_list, y_list = [], [], []
    for _kind, p in pairs:
        if not (os.path.exists(p.path_a) and os.path.exists(p.path_b)):
            continue
        a_list.append(np.asarray(Image.open(p.path_a).convert("RGB").resize((size, size)), dtype=np.float32))
        b_list.append(np.asarray(Image.open(p.path_b).convert("RGB").resize((size, size)), dtype=np.float32))
        y_list.append(float(p.label))
    if not a_list:
        return None
    return np.stack(a_list), np.stack(b_list), np.asarray(y_list, dtype=np.float32)


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

    pairs = load_pairs(settings)
    if not pairs:
        raise RuntimeError("No evaluation pairs available.")

    data = pair_arrays(pairs, size)
    if data is None:
        raise RuntimeError("No evaluation images loadable.")
    x_a, x_b, y = data
    x_a = normalize(x_a, settings.image.normalization)
    x_b = normalize(x_b, settings.image.normalization)

    emb_a = encode(encoder, x_a)
    emb_b = encode(encoder, x_b)
    sims = cosine_similarity(emb_a, emb_b).diagonal()

    summary = {
        "encoder_source": source,
        "n_pairs": int(len(y)),
        "encoder_path": encoder_path if os.path.exists(encoder_path) else None,
        "gates": {},
    }

    # Face verification: G2
    vrep = verification_report(sims, y, far_target=1e-3)
    g2_pass = bool(vrep.get("tar_at_far_0.001", 0.0) >= settings.gates.g2_tar_at_far_1e_3)
    summary["gates"]["g2"] = {
        "metric": "TAR@FAR=1e-3 (LFW verification)",
        "value": vrep["tar_at_far_0.001"],
        "target": settings.gates.g2_tar_at_far_1e_3,
        "pass": g2_pass,
        "report": vrep,
    }

    # Kinship: G3 (if kinship pairs present)
    kin_pairs = [p for _kind, p in pairs if getattr(p, "pair_type", None) == "kinship"]
    if kin_pairs:
        kdata = pair_arrays([("kinship", p) for p in kin_pairs], size)
        if kdata is not None:
            ka, kb, ky = kdata
            ka = normalize(ka, settings.image.normalization)
            kb = normalize(kb, settings.image.normalization)
            ea = encode(encoder, ka)
            eb = encode(encoder, kb)
            ksims = cosine_similarity(ea, eb).diagonal()
            kreport = kinship_report(ksims, ky)
            g3_pass = bool(kreport["accuracy"] >= settings.gates.g3_kinship_accuracy)
            summary["gates"]["g3"] = {
                "metric": "kinship accuracy (KinFaceW)",
                "value": kreport["accuracy"],
                "target": settings.gates.g3_kinship_accuracy,
                "pass": g3_pass,
                "report": kreport,
            }

    all_pass = all(g["pass"] for g in summary["gates"].values())
    summary["all_gates_pass"] = bool(all_pass)

    print(json.dumps(summary, indent=2, default=str))

    if gate and not all_pass:
        sys.exit(1)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate FMPPI model against quality gates G2/G3")
    parser.add_argument("--config", default="config/default.yaml", help="Path to YAML config")
    parser.add_argument("--gate", action="store_true", help="Fail (exit 1) when any gate is not met")
    args = parser.parse_args()
    evaluate(args.config, gate=args.gate)


if __name__ == "__main__":
    main()
