# ML Pipeline

## Custom Model (SOTA-comparable candidate)
- Custom CNN/Siamese network (OpenCV + TensorFlow/Keras) trained from scratch on KinFaceW/LFW/YouTubeFaceDB
- Benchmarked against FaceNet/ArcFace/VGGFace/DeepFace baselines using standard metrics
- Evaluation metrics: accuracy, AUC, EER, TAR@FAR=1e-3 (face verification); accuracy/AUC/EER (kinship)
- Model cards document performance vs SOTA across datasets and robustness scenarios

## Models
- Detector: YoloFace, DeepFace detectors (weights in registry)
- Embedders: FaceNet (128-d), ArcFace (512-d), VGGFace (4096-d), DeepFace (wrapper/unified API) via Strategy
- Kinship: FMPPI Siamese CNN (shared encoder) + contrastive/triplet loss

## Training
- Framework: TensorFlow/Keras + OpenCV
- Datasets: KinFaceW, LFW, YouTubeFaceDB, CCTV samples
- Splits: stratified by age/pose/illumination/occlusion
- Tracking: MLflow (params, metrics, artifacts)
- Reproducibility: seeded, config-driven YAML

## Evaluation
- Face verification: TAR@FAR=1e-3 on LFW
- Kinship: accuracy/AUC/EER on KinFaceW
- Robustness: degradation suite (blur, noise, low-res, pose, illum, occlusion, aging)

## Serving
- Export to ONNX for cPanel-friendly inference; GPU optional
- Versioned model registry; A/B via config flag
