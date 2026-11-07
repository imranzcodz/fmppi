# FMPPI Model — Technical Specification

## 1. What It Is
**FMPPI** is a custom CNN-based Siamese network trained from scratch with OpenCV + TensorFlow/Keras for two tasks:
- **Face verification (1:1 / 1:N)**: determine whether two face images depict the same person.
- **Kinship verification**: determine whether two face images depict biologically related persons (e.g., parent–child, siblings) and with what confidence.

Architecture: twin CNN branches share identical weights (weight tying) → each branch outputs an embedding → embeddings are compared with a distance metric (Euclidean/cosine) → threshold → same/different or kin/non-kin decision with confidence score.

Embedding dimension: 512 (configurable). Input: aligned face chips (112×112 or 160×160), normalized.

## 2. Why It Is Used
- **SOTA-comparable candidate**: benchmarked against FaceNet, ArcFace, VGGFace, DeepFace on LFW/KinFaceW/YouTubeFaceDB using standard metrics (accuracy, AUC, EER, TAR@FAR=1e-3).
- **DRY/weight sharing**: one shared encoder instead of two independent networks (parameter efficiency, consistent embedding space).
- **Custom ownership**: full control over training data, thresholds, versioning, and deployment (ONNX) — important for missing-person casework where model provenance matters.
- **Robustness focus**: trained/validated under low-quality CCTV, pose, illumination, occlusion, and age gaps — realistic missing-person scenarios where SOTA models degrade.
- **Dual-task**: one model serves both identity matching (local-verify/global-verify) and kinship checking (kinship-verify), reducing deployment footprint.

## 3. How It Operates

### 3.1 Preprocessing (OpenCV)
- Detect face (YoloFace or DeepFace detector) → bounding box.
- Align via 5-point landmarks; crop face chip; resize; mean/std normalization.

### 3.2 Forward pass
```
Image → Detect → Align → Normalize → Shared CNN Encoder → Embedding (512-d)
Embedding A, Embedding B → Distance (L2 / cosine) → Threshold → Decision + Confidence
```

### 3.3 Training (TensorFlow/Keras)
- Loss: contrastive or triplet loss with margin α.
- Optimizer: Adam with learning-rate schedule; early stopping.
- Config-driven YAML; seeded for reproducibility.
- Datasets: KinFaceW, LFW, YouTubeFaceDB, CCTV samples; stratified splits by age/pose/illumination/occlusion; no identity leakage across train/val/test.
- Tracking: MLflow (params, metrics, artifacts); model registry with versioned checkpoints and model cards.

### 3.4 Inference / Serving
- Export to ONNX for CPU-friendly serving on cPanel hosting.
- Batch inference; p95 < 2 s per image target.
- Threshold calibrated on validation set; confidence = sigmoid-based score mapped to [0,1].

### 3.5 Evaluation metrics
- Face verification: accuracy, AUC, EER, TAR@FAR=1e-3 on LFW.
- Kinship: accuracy, AUC, EER on KinFaceW (target ≥75%).
- Robustness: accuracy delta under blur/noise/low-res/pose/illum/occlusion/aging vs baselines.

## 4. Where It Applies
| Use case | Endpoint | Description |
|---|---|---|
| local-verify | POST /verify/local | 1:N search of uploaded photo against MySQL evidence embeddings; ranked matches with score + case link. |
| global-verify | POST /verify/global | Reverse-image search across web engines/APIs; similar faces with source URLs + similarity score. |
| kinship-verify | POST /verify/kinship | Two-photo kin check; kin/non-kin score + confidence. |
| Case management | case detail / match results | Attach match/kinship results to a missing-person case; audit-logged. |

## 5. References
- Bromley, J., Guyon, I., LeCun, Y., Säckinger, E., & Shah, R. (1994). Signature verification using a "Siamese" time delay neural network. *Advances in Neural Information Processing Systems (NIPS)*, 7, 737–744. (NeurIPS proceedings)
- Koch, G., Zemel, R., & Salakhutdinov, R. (2015). Siamese neural networks for one-shot image recognition. *ICML Deep Learning Workshop*. https://www.cs.cmu.edu/~rsalakhu/papers/oneshot1.pdf
- Schroff, F., Kalenichenko, D., & Philbin, J. (2015). FaceNet: A unified embedding for face recognition and clustering. *CVPR*, 815–823. DOI: 10.1109/CVPR.2015.7298682. https://arxiv.org/abs/1503.03832
- Deng, J., Guo, J., Xue, N., & Zafeiriou, S. (2019). ArcFace: Additive angular margin loss for deep face recognition. *CVPR*, 4690–4699. DOI: 10.48550/arXiv.1801.07698. https://arxiv.org/abs/1801.07698
- Parkhi, O. M., Vedaldi, A., & Zisserman, A. (2015). Deep face recognition. *BMVC*, 1–12. DOI: 10.5244/C.29.3. http://www.robots.ox.ac.uk/~vgg/publications/2015/Parkhi15/
- Taigman, Y., Yang, M., Ranzato, M. A., & Wolf, L. (2014). DeepFace: Closing the gap to human-level performance in face verification. *CVPR*, 1701–1708. DOI: 10.1109/CVPR.2014.220. https://arxiv.org/abs/1404.3640
- Lu, J., Tan, Y.-P., & Zhou, X. (2012). KinFaceW database and kinship verification. *IEEE TIFS*, 7(5), 1509–1521. DOI: 10.1109/TIFS.2012.2197156
- Zhou, X., et al. (2014). Learning discriminative features for kinship verification. *IEEE TPAMI*.
- Meng, F., Zhao, S., Li, J., & Lu, J. (2021). MagFace: A universal representation for face recognition and quality assessment. *CVPR*, 14967–14976. https://arxiv.org/abs/2103.06698
- Deng, Y., Yang, J., Xu, S., Chen, D., & Wang, Y. (2022). AdaFace: Quality adaptive margin for face recognition. *CVPR*, 19246–19255. https://arxiv.org/abs/2204.00906

## Recent works (2023–2025)
- Bendib, N. (2023). Supervised Contrastive Learning and Feature Fusion for Improved Kinship Verification. *arXiv preprint*. https://arxiv.org/abs/2302.09556
- Unknown authors. (2023). Fusion of Deep and Shallow Features for Face Kinship Verification. *arXiv preprint*. https://arxiv.org/abs/2312.10462
- Gary, L. F. et al. (2023). KFC: Kinship Verification with Fair Contrastive Loss and Multi-Task Learning. *arXiv preprint*. DOI: 10.48550/arxiv.2309.10641. https://arxiv.org/abs/2309.10641
- Su, W.-T., Chen, M.-H., Wang, C.-Y., Lai, S.-H., & Chen, T. (2023/2024). Kinship Representation Learning with Face Componential Relation (FaCoRNet). *arXiv preprint*. https://arxiv.org/pdf/2304.04546v5.pdf
- Song, Y., & Wang, F. (2024). QGFace: Quality-Guided Joint Training for Mixed Quality Face Recognition. *18th IEEE International Conference on Automatic Face and Gesture Recognition (FG)*. https://arxiv.org/pdf/2312.17494
- Sedighi, E. et al. (2024). ARoFace: Alignment Robustness to Improve Low-Quality Face Recognition. *arXiv preprint*. https://arxiv.org/html/2407.14972v1
- Adapter-based FR in the wild. (2024). Effective Adapter for Face Recognition in the Wild. *arXiv preprint*. https://arxiv.org/html/2312.01734v2
- Occlusion reconstruction for face recognition. (2024). Reconstruction and enhancement techniques for overcoming occlusion in face recognition. DOI: 10.21203/rs.3.rs-4349727/v1
- Angle-aware loss + MAE pretraining for robust FR. (2024). *ICASSP 2024*. DOI: 10.1109/icassp48485.2024.10446956
