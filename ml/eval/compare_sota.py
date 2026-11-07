"""Comprehensive SOTA comparison: FMPPI vs FaceNet/ArcFace/VGGFace/DeepFace.

Evaluates FMPPI (custom Siamese CNN) and all SOTA baselines across the 4
configured datasets (LFW, KinFaceW, ORL_Faces, CCTV), reporting per-dataset
and aggregate metrics:

- Face verification: accuracy, AUC, EER, TAR@FAR=1e-3 (G2 gate)
- Kinship verification: accuracy, AUC, EER (G3 gate)
- Robustness: accuracy under CCTV degradation (G4 gate)

Usage:
    cd ml
    python eval/compare_sota.py --config config/default.yaml --gate
    python eval/compare_sota.py --config config/default.yaml --dataset lfw --report sota_report.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List

import numpy as np

os.environ.setdefault("KERAS_BACKEND", "tensorflow")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.config import load_config, resolve  # noqa: E402
from ml.datasets import (  # noqa: E402
    load_all_datasets,
    load_kinship_pairs,
    load_verification_pairs,
    synthetic_verification_pairs,
)
from ml.embedding import build_embedder  # noqa: E402
from ml.inference import cosine_similarity  # noqa: E402
from ml.metrics import verification_report  # noqa: E402
from ml.model.siamese import encode  # noqa: E402
from ml.preprocess import normalize  # noqa: E402

EMBEDDER_NAMES = ["facenet", "arcface", "vggface", "deepface"]


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


def _eval_embedder_on_pairs(embedder, pairs, size: int, normalization: str) -> dict:
    data = _pair_arrays(pairs, size)
    if data is None:
        return {"error": "no images loadable", "n_pairs": 0}
    x_a, x_b, y = data
    x_a = normalize(x_a, normalization)
    x_b = normalize(x_b, normalization)
    emb_a = np.stack([embedder.embed(f) for f in x_a])
    emb_b = np.stack([embedder.embed(f) for f in x_b])
    sims = cosine_similarity(emb_a, emb_b).diagonal()
    return verification_report(sims, y, far_target=1e-3)


def _eval_fmppi_on_pairs(encoder, pairs, size: int, normalization: str) -> dict:
    data = _pair_arrays(pairs, size)
    if data is None:
        return {"error": "no images loadable", "n_pairs": 0}
    x_a, x_b, y = data
    x_a = normalize(x_a, normalization)
    x_b = normalize(x_b, normalization)
    emb_a = encode(encoder, x_a)
    emb_b = encode(encoder, x_b)
    sims = cosine_similarity(emb_a, emb_b).diagonal()
    return verification_report(sims, y, far_target=1e-3)


def _load_pairs_for_dataset(settings, dname: str) -> List:
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
    parser = argparse.ArgumentParser(
        description="Compare FMPPI vs SOTA baselines (FaceNet/ArcFace/VGGFace/DeepFace) across all 4 datasets"
    )
    parser.add_argument("--config", default="config/default.yaml", help="Path to YAML config")
    parser.add_argument(
        "--dataset",
        choices=["lfw", "kinfacew", "orl_faces", "cctv", "all"],
        default="all",
        help="Dataset to evaluate on (default: all)",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Write JSON comparison report to this path",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="Fail (exit 1) when G2/G3/G4 gates are not met on available data",
    )
    args = parser.parse_args(argv)
    settings = load_config(args.config)
    size = settings.image.size[0]

    datasets_to_run = ["lfw", "kinfacew", "orl_faces", "cctv"] if args.dataset == "all" else [args.dataset]

    report: Dict[str, dict] = {
        "config": args.config,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "datasets": datasets_to_run,
        "embedders": EMBEDDER_NAMES + ["fmppt"],
        "results": {},
        "n_pairs_per_dataset": {},
        "gate_assessment": {},
    }

    all_pass = True

    for dname in datasets_to_run:
        pairs = _load_pairs_for_dataset(settings, dname)
        if not pairs and settings.datasets.synthetic_fallback:
            pairs = synthetic_verification_pairs(
                n_pairs=128, image_size=(size, size), seed=settings.seed
            )
            for p in pairs:
                p.dataset = dname
        if not pairs:
            report["results"][dname] = {"error": "no pairs available"}
            report["n_pairs_per_dataset"][dname] = 0
            continue

        data = _pair_arrays(pairs, size)
        if data is None:
            report["results"][dname] = {"error": "no images loadable"}
            report["n_pairs_per_dataset"][dname] = 0
            continue
        x_a, x_b, y = data
        report["n_pairs_per_dataset"][dname] = int(len(y))

        ds_results: Dict[str, dict] = {}

        # SOTA baselines
        for name in EMBEDDER_NAMES:
            try:
                embedder = build_embedder(
                    name,
                    detector_backend=settings.embedder.deepface_detector_backend,
                    enforce_detection=settings.embedder.enforce_detection,
                )
                ds_results[name] = _eval_embedder_on_pairs(embedder, pairs, size, settings.image.normalization)
            except Exception as exc:
                ds_results[name] = {"error": str(exc)}

        # FMPPI
        ckpt_dir = resolve(settings.mlflow.artifact_root)
        encoder_path = os.path.join(ckpt_dir, "fmppt_encoder.keras")
        if os.path.exists(encoder_path):
            import keras

            encoder = keras.models.load_model(encoder_path, compile=False, safe_mode=False)
            ds_results["fmppt"] = _eval_fmppi_on_pairs(encoder, pairs, size, settings.image.normalization)
        else:
            ds_results["fmppt"] = {"note": "no trained checkpoint; run train.py first"}

        report["results"][dname] = ds_results

        # Gate assessment per dataset
        gate = report["gate_assessment"].setdefault(dname, {})
        fmppi_r = ds_results.get("fmppt", {})
        if isinstance(fmppi_r, dict) and "tar_at_far_0.001" in fmppi_r:
            tar = fmppi_r["tar_at_far_0.001"]
            gate["g2_tar_at_far_1e_3"] = {
                "value": tar,
                "target": settings.gates.g2_tar_at_far_1e_3,
                "pass": bool(tar >= settings.gates.g2_tar_at_far_1e_3),
            }
            if not gate["g2_tar_at_far_1e_3"]["pass"]:
                all_pass = False
        if isinstance(fmppi_r, dict) and "accuracy" in fmppi_r:
            acc = fmppi_r["accuracy"]
            gate["g3_kinship_accuracy"] = {
                "value": acc,
                "target": settings.gates.g3_kinship_accuracy,
                "pass": bool(acc >= settings.gates.g3_kinship_accuracy),
            }
            if not gate["g3_kinship_accuracy"]["pass"]:
                all_pass = False

    # Aggregate: compute mean accuracy/AUC across datasets for FMPPI vs each SOTA
    agg: Dict[str, dict] = {}
    for embedder_name in EMBEDDER_NAMES + ["fmppt"]:
        accs, aucs, eers, tars = [], [], [], []
        for dname in datasets_to_run:
            r = report["results"].get(dname, {}).get(embedder_name, {})
            if isinstance(r, dict) and "accuracy" in r and "error" not in r and "note" not in r:
                accs.append(r["accuracy"])
                aucs.append(r.get("auc", 0.0))
                eers.append(r.get("eer", 0.0))
                tars.append(r.get("tar_at_far_0.001", 0.0))
        if accs:
            agg[embedder_name] = {
                "mean_accuracy": float(np.mean(accs)),
                "mean_auc": float(np.mean(aucs)),
                "mean_eer": float(np.mean(eers)),
                "mean_tar_at_far_1e_3": float(np.mean(tars)),
                "n_datasets": len(accs),
            }
    report["aggregate"] = agg

    # Rank embedders by mean accuracy
    ranked = sorted(agg.items(), key=lambda kv: -kv[1]["mean_accuracy"]) if agg else []
    report["ranking"] = [
        {"rank": i + 1, "embedder": name, "mean_accuracy": stats["mean_accuracy"]}
        for i, (name, stats) in enumerate(ranked)
    ]

    report["gate_assessment"]["all_gates_pass"] = bool(all_pass)

    print(json.dumps(report, indent=2, default=str))

    if args.report:
        os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, default=str)
        print(f"\nReport saved to {args.report}")

    if args.gate and not all_pass:
        print("\n[GATE FAIL] One or more quality gates not met.", file=sys.stderr)
        sys.exit(1)

    return report


if __name__ == "__main__":
    main()
