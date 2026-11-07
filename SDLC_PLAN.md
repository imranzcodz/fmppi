# FMPPI — Agile SDLC Plan

## 1. Vision & Scope
**FMPPI** (Finding Missing Person's Proof of Identity): AI/ML system for identifying missing/unidentified persons via facial recognition and kinship verification, delivered as a secured web UI with case management, RBAC, and (later) a mobile app.

**Core capabilities**
- Face detection (YoloFace, DeepFace detectors), embedding extraction (FaceNet, ArcFace, VGGFace, DeepFace)
- **Custom AI/ML model** (CNN/Siamese, OpenCV+TensorFlow) trained to be a SOTA-comparable candidate for face verification and kinship verification
- Kinship verification (FMPPI Siamese CNN, pairwise kin/non-kin)
- Robustness: low-quality CCTV, pose, illumination, occlusion, age gaps
- Case management + RBAC web UI; mobile app as add-on

## 2. SDLC Model — Agile (Scrum)
- Cadence: 2-week sprints, 6 sprints total (12 weeks) per release increment
- Ceremonies: Sprint planning (4h), daily standup (15m), review (2h), retro (1h)
- Backlog refinement: weekly, mid-sprint

## 3. Phases & Milestones
| Phase | Weeks | Milestone |
|---|---|---|
| P0 Discovery & Data | 1–2 | M0 Data inventory & ethics review approved |
| P1 ML Foundation | 3–4 | M1 Baseline face pipeline (FaceNet/ArcFace) ≥95% LFW |
| P2 Kinship Model | 5–6 | M2 Siamese kinship model trained on KinFaceW |
| P3 Robustness & Validation | 7–8 | M3 Robustness report (CCTV, pose, illum, occlusion, age) |
| P4 Web Platform & RBAC | 9–10 | M4 Secured web UI with case management |
| P5 Integration & Hardening | 11–12 | M5 End-to-end release candidate |
| P6 Mobile App (add-on) | 13+ | M6 Mobile client MVP |

## 4. Product Backlog (Epics & Stories)
**E1 Data & Ethics** (high)
- Dataset acquisition: KinFaceW, LFW, YouTubeFaceDB, CCTV samples
- Data anonymization & consent compliance; DPA/IRB sign-off
- Stratified splits by age, pose, illumination, occlusion

**E2 Face Detection & Embeddings** (high)
- YoloFace, DeepFace detector integration
- Embedders: FaceNet/ArcFace/VGGFace/DeepFace embedding extractors behind common interface (Strategy pattern)
- 1:N search against local DB (local-verify) and web index (global-verify via reverse image search/API)

**E3 Kinship Verification** (high)
- Siamese CNN architecture (DRY: shared encoder) — FMPPI model benchmarked against FaceNet/ArcFace/VGGFace/DeepFace baselines
- Pairwise distance metrics & threshold calibration
- Kin vs non-kin classification with confidence
- Standard evaluation metrics: accuracy, AUC, EER, TAR@FAR=1e-3

**E4 Robustness & Augmentation** (medium)
- Augmentation: blur, noise, low-res, pose, illumination, occlusion, aging
- Evaluation harness across scenarios (pytest + MLflow)

**E5 Model Lifecycle & MLOps** (medium)
- Custom model training pipeline (TensorFlow/Keras + OpenCV)
- Benchmark FMPPI model vs SOTA baselines on LFW/KinFaceW/YouTubeFaceDB
- Experiment tracking (MLflow), model registry, versioning
- Reproducible training (seeded, config-driven)

**E6 Web Platform & Case Management** (high)
- Backend API (FastAPI/Node) with RBAC (Admin/Investigator/Reviewer/Reporter)
- Case CRUD, evidence upload, match results (local-verify), global-verify (web reverse image search), kinship-verify (2-photo kin check), audit log
- Secured auth (JWT/OAuth2, MFA)

**E7 Mobile App** (low, add-on)
- React Native client: search, capture, view matches

**E8 Quality, Security, DevOps** (high)
- CI/CD (GitHub Actions), Docker, IaC
- Security: OWASP, secrets mgmt, encryption at rest/transit
- Observability: logging, metrics, tracing

## 5. Sprint Cadence & Tracking
- Sprint length: 2 weeks
- Story points: Fibonacci (1,2,3,5,8,13); capacity ~40 pts/sprint (team of 5)
- Definition of Ready (DoR): acceptance criteria clear, dependencies met, sized ≤13 pts, ethics/privacy reviewed if data-related
- Tracking: Jira/Linear board with burndown; daily standup; sprint velocity chart
- Definition of Done (DoD): code reviewed, tests pass, docs updated, deployed to staging, acceptance criteria met

## 6. Quality Gates
- G1: unit test coverage ≥80% (backend & ML wrappers)
- G2: face verification TAR@FAR=1e-3 ≥ 99% on LFW
- G3: kinship verification accuracy ≥ 75% on KinFaceW (state-of-art baseline)
- G4: robustness: ≥60% accuracy under severe degradation (low-res/occlusion)
- G5: security scan (SAST/DAST) zero critical; OWASP top-10 checklist
- G6: performance: API p95 < 500ms (excluding inference), inference < 2s/image

## 7. Metrics (KPIs)
- ML: accuracy, TAR@FAR, AUC, EER, robustness delta
- Eng: velocity, cycle time, defect density, test coverage
- Product: case resolution time, false-positive rate, user satisfaction

## 8. Risks & Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| Dataset bias/ethics | High | Ethics review, diverse datasets, fairness audit |
| Low-quality CCTV accuracy | High | Augmentation, super-resolution pre-step, confidence thresholds |
| Model overfitting | Medium | Cross-dataset eval, regularization, early stopping |
| Privacy/regulatory (GDPR) | High | Data minimization, retention policy, audit logs |
| Scope creep (mobile) | Medium | Mobile as separate phase, MVP only |
| Compute cost | Medium | GPU scheduling, model optimization (ONNX) |

## 9. Architecture & Best Practices
- **SOLID**: single-responsibility modules (detector, embedder, verifier, case service); open/closed via strategy interfaces
- **DRY**: shared encoder, common preprocessing, reusable UI components
- **Patterns**: Strategy (model backends), Factory (model loading), Repository (data access), Observer (events/audit)
- **Layering**: presentation → application → domain → infrastructure
- **Config-driven**: YAML/JSON configs for models, thresholds, envs
- **Testing**: unit (pytest/Jest), integration, e2e (Playwright), ML regression tests
- **Security**: RBAC, JWT, input validation, rate limiting, secure storage
- **Observability**: structured logging, metrics, tracing

## 10. Deliverables
- Trained models + model cards
- ML pipeline & evaluation reports
- Secured web app (frontend + backend)
- Mobile app (phase 2)
- Documentation: API docs, user manual, ethics/compliance report
- CI/CD pipelines & deployment manifests

## 11. Progress Tracking Template
- Sprint burndown (points remaining vs ideal)
- Story states: To Do / In Progress / Review / Done
- Milestone checklist with gate sign-offs
- Risk register updated each sprint
- Weekly metrics dashboard (ML + eng + product)

---
*Generated plan for FMPPI. Adjust sprint capacity and team size as needed.*
