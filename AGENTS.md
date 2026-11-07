# FMPPI — Project Setup & Commands

## Repository Structure
```
fmppi/
  AGENTS.md            # this file: setup, commands, quality gates
  idea.txt             # original project idea
  SDLC_PLAN.md         # agile SDLC plan (phases, backlog, gates, metrics, risks)
  TEAM.md              # agentic team roster & coordination
  .github/workflows/   # CI (ci.yml) & cPanel deploy (deploy-cpanel.yml)
  deploy/              # deployment manifests
  docs/                # technical specifications
  ml/                  # ML pipeline (custom FMPPI model, training, eval)
  backend/             # FastAPI API, RBAC, case mgmt, audit
  frontend/            # React web UI (local/global/kinship-verify)
  mobile/              # React Native MVP (phase 2)
  data/                # datasets (gitignored), manifests
  tests/               # integration & e2e tests
```

## Docs Navigation
| Doc | Purpose | Owner |
|---|---|---|
| docs/ARCHITECTURE.md | System components, layers, patterns, data flow | A1/A2/A3 |
| docs/DATA_MODEL.md | Entities, relationships, MySQL schema | A2 |
| docs/DATASET_HANDLING.md | Acquisition, preprocessing, splits, augmentation, ethics | A1 |
| docs/FMPPI_MODEL_SPEC.md | Custom FMPPI Siamese model spec + references | A1 |
| docs/ML_PIPELINE.md | Training, validation, benchmarking vs SOTA, ONNX serving | A1 |
| docs/TRAINING_VALIDATION.md | Training strategy, metrics gates G2–G4 | A1/A5 |
| docs/API_SPEC.md | REST endpoints (auth, cases, verify/local/global/kinship, audit) | A2 |
| docs/VISUALS.md | Architecture + verify workflow + UI wireframes (mermaid) | All |
| docs/TESTING.md | Test levels, coverage gates, ML regression | A5 |
| docs/SECURITY.md | Auth, RBAC, OWASP, audit log, secrets | A2/A4 |
| docs/ETHICS_PRIVACY.md | GDPR, consent, retention, bias audit, use limitations | All |
| docs/DEPLOYMENT.md | Local Docker, staging, cPanel production, rollback | A4 |
| docs/MOBILE_SPEC.md | React Native MVP spec (phase 2) | A6 |
| docs/PROGRESS_TRACKING.md | How to check progress, identify last state, resume point | All |

## Prerequisites
- Python 3.11+, Node 20+, Docker (optional), Git

## Initialize repo (required before Agent Manager worktree mode)
```bash
git init
git branch -m develop
git add -A
git commit -m "chore: initial plan and docs"
```

## Environment
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r ml/requirements.txt -r backend/requirements.txt
npm install --prefix frontend
cp .env.example .env   # fill in secrets; never commit .env
```

## Run locally
```bash
# ML training/eval
cd ml && python train.py --config config/default.yaml
cd .. && python ml/eval/run.py --gate

# Backend
cd backend && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev   # http://localhost:5173

# All via Docker Compose
docker compose up --build
```

## Test & Lint
```bash
# Backend
cd backend && pytest --cov=. --cov-fail-under=80
ruff check .

# Frontend
cd frontend && npm run lint && npm test -- --coverage

# ML
cd ml && pytest tests && python eval/robustness.py --gate

# CI
# GitHub Actions runs on push/PR to develop/main
```

## Quality Gates (G1–G6)
- G1: unit test coverage ≥80% (backend & ML wrappers)
- G2: face verification TAR@FAR=1e-3 ≥99% on LFW
- G3: kinship verification accuracy ≥75% on KinFaceW
- G4: robustness ≥60% accuracy under severe degradation (low-res/occlusion)
- G5: SAST/DAST zero critical; OWASP top-10 checklist
- G6: API p95 <500ms (excluding inference); inference <2s/image

## Agent Assignment Mapping
| Agent | Role | Primary docs | Code dir |
|---|---|---|---|
| A1 ML-Engineer | Face pipeline, FMPPI model, 1:N search, global-verify | ARCHITECTURE, DATASET_HANDLING, FMPPI_MODEL_SPEC, ML_PIPELINE, TRAINING_VALIDATION | ml/ |
| A2 Backend-Engineer | API, RBAC, JWT, audit, MySQL | DATA_MODEL, API_SPEC, SECURITY | backend/ |
| A3 Frontend-Engineer | React UI, RBAC views, case dashboard, verify screens | ARCHITECTURE, VISUALS, API_SPEC | frontend/ |
| A4 DevOps-Engineer | CI/CD, Docker, cPanel deploy, rollback | DEPLOYMENT, SECURITY | .github/workflows/, deploy/ |
| A5 QA-Engineer | Testing, quality gates, ML regression | TESTING, TRAINING_VALIDATION | tests/ |
| A6 Mobile-Engineer (phase 2) | React Native MVP | MOBILE_SPEC, API_SPEC | mobile/ |

## Pre-Commit / Quality Gate Checklist
- [ ] Lint passes (ruff backend, eslint frontend)
- [ ] Type check passes (mypy backend, tsc frontend)
- [ ] Unit tests pass with coverage ≥80%
- [ ] ML metric gates G2–G4 pass on held-out data
- [ ] Security scan (bandit, npm audit) zero critical
- [ ] Docs updated for any API/schema change
- [ ] `.env` never committed; secrets in GitHub Secrets / cPanel env vars

## Progress Tracking & Resume
See docs/PROGRESS_TRACKING.md: check `git log --oneline -10`, `git status`, active branch, last Done story, MLflow last run, CHECKPOINT.json.

## Secrets
- Never commit `.env` or keys. Use cPanel env vars / GitHub Secrets.
