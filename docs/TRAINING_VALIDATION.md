# Training & Validation

## Custom Model vs SOTA Benchmarking
- Train FMPPI Siamese CNN from scratch; benchmark against FaceNet/ArcFace/VGGFace/DeepFace on LFW (verification) and KinFaceW (kinship)
- Standard metrics: accuracy, AUC, EER, TAR@FAR=1e-3 (face verification); accuracy/AUC/EER (kinship)
- Robustness suite vs baselines under degradation (blur/noise/low-res/pose/illum/occlusion/aging); report accuracy delta

## Training Strategy
- Custom Siamese CNN with shared encoder (DRY); Loss: contrastive/triplet (margin tuned); Optimizer: Adam, lr schedule, early stopping; Config-driven YAML; seeded reproducibility; MLflow tracking
- Models Trained: Face verification baseline (FaceNet/ArcFace/VGGFace/DeepFace embeddings) + FMPPI Siamese on KinFaceW + cross-dataset eval (LFW/YTDB)

## Validation Protocol
- Hold-out test sets per dataset; no identity leakage
- Face verification: TAR@FAR=1e-3, AUC, EER on LFW
- Kinship: accuracy, AUC, EER on KinFaceW (target ≥75%)
- Robustness suite: degrade test images (blur/noise/low-res/pose/illum/occlusion/aging) and report accuracy delta (target ≥60% severe)

## Hyperparameter Tuning
- Grid/random search on val set; log to MLflow

## Model Selection & Registry
- Promote best checkpoint to registry with model card (dataset, metrics, limitations)
- Version tags; rollback via config flag

## Serving
- Export to ONNX; inference service with batching; p95 < 2s/image

## Validation Gates (CI)
- G2: TAR@FAR=1e-3 ≥ 99% LFW
- G3: kinship acc ≥ 75% KinFaceW
- G4: robustness ≥ 60% severe degradation
