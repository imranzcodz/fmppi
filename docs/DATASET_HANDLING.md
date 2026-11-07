# Dataset Handling

## Datasets
- KinFaceW (I/II): kinship pairs (parent-child, siblings)
- LFW: face verification pairs
- YouTubeFaceDB: video frames, pose/illumination variation
- CCTV samples: low-quality, occlusion, aging

## Acquisition & Licensing
- Download via official sources; record license; store raw in `data/raw/` (gitignored)
- Checksum verification; metadata manifest (JSON)

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
