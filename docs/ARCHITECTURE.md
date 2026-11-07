# Architecture

## System Components
- **ML Service** (`ml/`): detection (YoloFace, DeepFace detectors), embedding (FaceNet/ArcFace/VGGFace/DeepFace), kinship (FMPPI Siamese), robustness eval, 1:N search (local DB + web reverse-image via global-verify)
- **Backend API** (`backend/`): FastAPI, RBAC, case mgmt, auth, audit
- **Web UI** (`frontend/`): React + Vite, role-based views
- **DB**: MySQL (cPanel-compatible) for cases, users, matches, audit
- **Storage**: S3-compatible / cPanel file storage for evidence images
- **Mobile** (`mobile/`): React Native (phase 2)

## Layers (SOLID/DRY)
presentation → application → domain → infrastructure

## Key Interfaces
- `FaceDetector.detect(img) -> List[BBox]`
- `Embedder.embed(face) -> np.ndarray (512/128-d)`
- `KinshipVerifier.verify(a,b) -> {score, is_kin, confidence}`
- `CaseRepository` (CRUD), `UserRepository`, `AuditLogger`

## Patterns
Strategy (model backends), Factory (model loading), Repository (data), Observer (audit events), DTO validation (Pydantic)

## Data Flow
Image upload → detect → align → embed → match against case DB / kinship pairs → store result + audit → notify

## Deployment (cPanel)
Frontend static (dist/) → public_html; Backend via Passenger/Node app or reverse proxy to container; ML inference via ONNX runtime or external GPU service.
