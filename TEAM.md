# FMPPI — Agentic Coding Team

## Prerequisite
- Run `git init` and create `develop` branch before spawning Agent Manager worktree sessions.

| Agent | Role | Scope | Deliverables |
|---|---|---|---|
| A1 ML-Engineer | Face pipeline & embeddings | YoloFace, DeepFace, FaceNet, ArcFace, VGGFace, FMPPI Siamese (SOTA-comparable), 1:N search, global-verify | `ml/` package, trained FMPPI model vs SOTA baselines, eval reports |
| A2 Backend-Engineer | API & case management | FastAPI, RBAC, JWT, audit, DB | `backend/` |
| A3 Frontend-Engineer | Secured web UI | React + RBAC views, case dashboard | `frontend/` |
| A4 DevOps-Engineer | CI/CD & deploy | GitHub Actions, Docker, cPanel deploy | `.github/workflows/`, `deploy/` |
| A5 QA-Engineer | Testing & quality gates | pytest, Jest, Playwright, ML regression | `tests/` |
| A6 Mobile-Engineer (add-on) | Mobile client | React Native MVP | `mobile/` |

## Coordination
- Shared board: post INFO/RESULT/HOLD/VETO between agents
- Integration branch: `develop`; feature branches `feat/<agent>/<topic>`
- Merge via PR with QA review gate

## Spawn command (after `git init`)
Use Agent Manager `mode: worktree`, one task per agent with role prompt + baseBranch `develop`.

## CI/CD Targets
- Local: Docker Compose (ml + api + web + db)
- Staging: GitHub Actions → self-hosted runner
- Production: shared cPanel (PHP/Node-friendly); ML inference via external API or ONNX in container behind reverse proxy
