# FMPPI Model Card

**Model:** FMPPI Siamese CNN (custom, weight-tied shared encoder)
**Task:** Face verification (1:1 / 1:N) and kinship verification
**Framework:** TensorFlow/Keras 3 + OpenCV
**Serving:** ONNX (CPU) via ONNX Runtime
**Owner:** A1 ML-Engineer (FMPPI project)
**Status:** Baseline implementation — train from scratch; quality gates G2–G4 pending held-out results

---

## 1. Intended Use

- **local-verify**: 1:N search of an uploaded face photo against enrolled evidence embeddings; ranked matches with score + case link.
- **global-verify**: reverse-image search across web engines/APIs (orchestrated by the ML service, not the encoder itself).
- **kinship-verify**: two-photo kin/non-kin check with confidence.
- Designed for missing-person casework where model provenance, thresholds, and deployment control matter.

---

## 2. Architecture

Twin CNN branches share one weight-tied encoder:

```
Image -> Detect (YoloFace/DeepFace) -> Align (5-pt landmarks) -> Normalize
  -> Shared CNN Encoder -> Embedding (512-d)
Embedding A, Embedding B -> Distance (L2 / cosine) -> Threshold -> Decision + Confidence
```

- Encoder: 4× (Conv2D → BN → ReLU → MaxPool) + GAP → Dense(512) → Dropout → Dense(embedding_dim) + L2-normalize.
- Embedding dimension: 512 (configurable).
- Input: aligned face chips 112×112 (or 160×160), mean/std normalized.
- Loss: contrastive or triplet (margin-tuned).
- Optimizer: Adam with cosine/step LR schedule + early stopping.

---

## 3. Training Data

| Dataset | Use | Notes |
|---|---|---|
| KinFaceW I/II | Kinship pairs (parent–child, siblings) | gitignored; `data/raw/kinfacew` |
| LFW | Face verification pairs | gitignored; `data/raw/lfw` |
| YouTubeFaceDB | Pose/illumination variation | gitignored; `data/raw/youtube_facedb` |
| CCTV samples | Low-quality, occlusion, aging | gitignored; `data/raw/cctv` |

Splits: stratified by identity (no leakage), age bin, pose, illumination, occlusion; train/val/test = 70/15/15. Synthetic fallback used when real datasets are absent (smoke tests only — not for gate measurement).

---

## 4. Evaluation Metrics

- Face verification: accuracy, AUC, EER, **TAR@FAR=1e-3** (LFW).
- Kinship: accuracy, AUC, EER (KinFaceW).
- Robustness: accuracy delta under blur/noise/low-res/pose/illum/occlusion/aging.

## 5. Quality Gates (targets vs. current status)

| Gate | Metric | Target | Status |
|---|---|---|---|
| G2 | TAR@FAR=1e-3 on LFW | ≥ 99% | Not measured (no trained checkpoint yet) |
| G3 | Kinship accuracy on KinFaceW | ≥ 75% | Not measured |
| G4 | Accuracy under severe degradation | ≥ 60% | Not measured |

Run `cd ml && python train.py --config config/default.yaml` then
`python eval/run.py --gate` and `python eval/robustness.py --gate` to measure.

---

## 6. Baseline Embedders (Strategy interface)

| Embedder | Dimension | Backend |
|---|---|---|
| FaceNet | 128 | DeepFace.represent ("Facenet") |
| ArcFace | 512 | DeepFace.represent ("ArcFace") |
| VGGFace | 4096 | DeepFace.represent ("VGGFace") |
| DeepFace | 4096 | DeepFace.represent ("DeepFace") |

All L2-normalized; deterministic pixel-derived fallback when DeepFace models unavailable.

---

## 7. Serving

- Export to ONNX (`models/registry/fmppt.onnx`) via tf2onnx; CPU execution provider.
- Inference: p95 target < 2 s/image (excluding detection); batch inference supported.
- Model registry: MLflow experiment `fmppi`, registered model `fmppt-siamese`, stage Promotion via config flag.
- Versioned checkpoints; rollback via config flag / model version.

---

## 8. Known Limitations

- Custom Siamese trained from scratch is a SOTA-comparable *candidate*; it must be benchmarked against FaceNet/ArcFace/VGGFace/DeepFace baselines on LFW/KinFaceW/YouTubeFaceDB before production use.
- G2/G3/G4 require real, held-out datasets; synthetic fallback does not satisfy the gates.
- Face detection (YoloFace/DeepFace) and embedding backends require their weights; pipeline degrades to OpenCV Haar / deterministic embeddings when unavailable.
- No demographic bias audit performed yet (see docs/ETHICS_PRIVACY.md).

---

## 9. Ethics & Compliance

- Datasets acquired via official sources; licenses recorded in `data/manifests/`.
- Raw data gitignored; PII removed/anonymized; filenames hashed; consent log maintained.
- IRB/ethics review and bias audit across demographics required before deployment in casework.
