# FMPPI ML Pipeline (`ml/`)

Face detection, embedding extraction, custom FMPPI Siamese CNN training, 1:N search,
robustness evaluation, MLflow tracking, model registry, and ONNX export.

## Layout

```
ml/
  config/default.yaml          # training & serving configuration
  config.py                    # YAML settings loader
  preprocess.py                # face alignment + normalization
  datasets.py                  # dataset manifests + loaders (synthetic fallback)
  metrics.py                   # accuracy, AUC, EER, TAR@FAR=1e-3
  detection/                   # FaceDetector strategies (YoloFace, DeepFace)
  embedding/                   # Embedder strategies (FaceNet, ArcFace, VGGFace, DeepFace)
  model/                       # FMPPI Siamese CNN + contrastive/triplet loss
  kinship.py                   # KinshipVerifier
  search.py                    # 1:N search index
  inference.py                 # ONNX export + ONNXRuntime encoder + similarity
  mlflow_tracking.py           # MLflow experiment tracking + model registry
  robustness/                  # degradation augmentations + robustness eval
  train.py                     # training entry point
  eval/run.py                  # G2/G3 gate evaluation
  eval/robustness.py           # G4 gate evaluation
  tests/                       # pytest suite
  model_card.md                # model card
  requirements.txt             # Python dependencies
```

## Setup

```bash
cd ml
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
```

## Run

```bash
# Train (config-driven; synthetic fallback if real datasets absent)
python train.py --config config/default.yaml

# Evaluate against gates G2/G3
python eval/run.py --config config/default.yaml --gate

# Robustness gate G4
python eval/robustness.py --config config/default.yaml --gate

# Unit tests
pytest tests
```

## Quality Gates

- G2: TAR@FAR=1e-3 ≥ 99% on LFW
- G3: Kinship accuracy ≥ 75% on KinFaceW
- G4: Robustness ≥ 60% accuracy under severe degradation

Real datasets (gitignored) go under `data/raw/{kinfacew,lfw,youtube_facedb,cctv}`.