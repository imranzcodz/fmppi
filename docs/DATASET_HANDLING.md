# Dataset Handling

## Datasets
- KinFaceW (I/II): kinship pairs (parent-child, siblings)
- LFW: face verification pairs
- CCTV samples: low-quality, occlusion, aging
- ORL_Faces: 40 subjects × 10 images for face recognition training/eval

### Dataset download sources
| Dataset | Source URL | License | Use |
|---|---|---|---|
| KinFaceW I & II | https://www.kinfacew.com/ | Research use | Kinship pairs (parent-child, siblings) |
| LFW | https://www.kaggle.com/datasets/jessicali9530/lfw-dataset | Non-commercial research use | Face verification pairs |
| CCTV face detection | https://universe.roboflow.com/cadit/cctv-face-detection | Research use | Low-quality CCTV, occlusion, aging |
| ORL_Faces | https://cam-orl.co.uk/facedatabase.html | Research use | 40 subjects × 10 images, face recognition |

### Combined dataset config
All dataset roots are configured in `ml/config/default.yaml` under `datasets`:
- `kinfacew_root`, `lfw_root`, `cctv_root`, `orl_faces_root`

Raw data lives under `datasets/<dataset>/` (gitignored). Manifests with licenses and
checksums are tracked under `data/manifests/`.

### Dataset roles in training & evaluation
| Dataset | Training role | Evaluation role | Gate |
|---|---|---|---|
| LFW | Face verification pairs (same/different person) | Face verification: accuracy, AUC, EER, TAR@FAR=1e-3 | G2 |
| KinFaceW | Kinship pairs (kin/non-kin) | Kinship: accuracy, AUC, EER | G3 |
| ORL_Faces | Face recognition (same/different subject) | Face recognition: accuracy across 40 subjects | SOTA comparison |
| CCTV | Low-quality face pairs for robustness | Robustness under degradation (blur/noise/low-res/pose/illum/occlusion/aging) | G4 |

### Training data pipeline
`ml/train.py` loads all configured datasets via `load_all_datasets()` and trains the
FMPPI Siamese CNN on the combined verification pairs. Each pair retains its `dataset`
field so per-dataset metrics are reported during training.

### SOTA comparison
`ml/baseline.py` and `ml/eval/compare_sota.py` benchmark FaceNet, ArcFace, VGGFace,
DeepFace, and FMPPI on each dataset separately and in aggregate, reporting per-dataset
and aggregate accuracy/AUC/EER/TAR@FAR metrics.

## Preprocessing
- Face detection (YoloFace/DeepFace), alignment (5-point landmarks), resize 112x112/160x160
- Quality filtering: blur score, min face size, occlusion estimate
- Normalization: mean/std per dataset; augmentation pipeline

## Stratification & Splits
- Split by identity (no leakage), stratified by age bin, pose, illumination, occlusion
- Train/val/test = 70/15/15; k-fold for kinship

## Augmentation
- Blur, Gaussian noise, JPEG compression, low-res downscale, random occlusion, brightness/contrast, pose perturbation, aging (synthetic)

## Versioning & Storage
- DVC for dataset versioning; manifests in `data/manifests/`
- Anonymization: remove PII, hash filenames, consent log

## Ethics & Compliance
- IRB/ethics review; bias audit across demographics; fairness metrics
