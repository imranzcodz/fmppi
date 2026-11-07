# Deployment (cPanel)

## Local
- Docker Compose: api, web, db, ml (GPU optional)
- `docker compose up --build`

## Staging
- GitHub Actions → self-hosted runner → docker compose

## Production (shared cPanel)

### Prerequisites
- cPanel account with MySQL database, FTP/SFTP access, and "Setup Python App" or "Setup Node.js App" (Phusion Passenger)
- GitHub Secrets: `CPANEL_FTP_HOST`, `CPANEL_FTP_USER`, `CPANEL_FTP_PASS`, `CPANEL_SSH_HOST`, `CPANEL_SSH_USER`, `CPANEL_SSH_KEY`
- cPanel environment variables (set in cPanel → Environment Variables / `.env`): `SECRET_KEY`, `DATABASE_URL`, `MODEL_VERSION`, `GLOBAL_VERIFY_ENABLED`, `LOCAL_VERIFY_ENABLED`, `ML_SERVICE_URL`, `VITE_API_BASE_URL`

### Step 1: Build & Upload Frontend
```bash
# Local build
npm ci --prefix frontend
npm run build --prefix frontend   # outputs to frontend/dist/

# Upload to cPanel public_html via FTP (or cPanel File Manager)
# Target: public_html/ (or subdirectory like public_html/fmppi/)
```

### Step 2: Backend via cPanel "Setup Python App"
1. Log in to cPanel → Software → "Setup Python App"
2. Create application: Python 3.11, app root `/home/user/fmppi-backend`, app URL `/api` (or domain root)
3. Upload backend code (excluding `node_modules/`, `__pycache__/`, `.env`, `venv/`)
4. In cPanel "Setup Python App", enter the WSGI entry point: `backend.app.main:app` (FastAPI via Passenger)
5. Set environment variables from `.env` (never commit secrets)
6. Install dependencies: `pip install -r backend/requirements.txt`
7. Run DB migrations: `cd /home/user/fmppi-backend/backend && alembic upgrade head`
8. Restart app via cPanel

### Alternative: Backend via Node.js App (Passenger)
If using Node.js instead of Python for the API layer:
1. cPanel → Software → "Setup Node.js App"
2. App root `/home/user/fmppi-backend`, startup file `backend/main.py` (or adapter)
3. Set environment variables, install dependencies, restart

### Step 3: ML Inference (ONNX)
- Export model: `python ml/train.py --config config/default.yaml` → exports ONNX to `ml/models/`
- Upload ONNX model to cPanel (or serve from external GPU endpoint)
- Set `ML_SERVICE_URL` env var to point to the ONNX inference service
- If using cPanel Python app, `onnxruntime` must be in `requirements.txt`

### Step 4: Database (cPanel MySQL)
1. cPanel → Databases → MySQL Database → create DB and user
2. Update `DATABASE_URL` in cPanel environment variables: `mysql+pymysql://user:pass@localhost:3306/dbname`
3. Run migrations: `alembic upgrade head`
4. Nightly DB dump via cPanel Backup or cron job

### Step 5: Secrets (Never Commit)
- `.env` is gitignored — never commit it
- Set all secrets in cPanel environment variables or GitHub Secrets for CI/CD
- Rotate `SECRET_KEY` and DB credentials regularly

## CI/CD (GitHub Actions → cPanel)
- `.github/workflows/deploy-cpanel.yml` runs on push to `main` or `workflow_dispatch`
- Builds frontend, uploads `dist/` to `public_html/` via FTP
- Deploys backend via SSH (PM2 restart or cPanel app touch)
- Runs DB migrations via SSH

## Rollback & Feature Flags
- Keep last 3 frontend builds; revert via FTP/SFTP or cPanel File Manager.
- DB migrations include down-scripts (Alembic); test rollback in staging first.
- Feature flags (model version, global-verify on/off) in config/YAML; toggle without redeploy.
- Rollback trigger: quality gate failure, security incident, or regression in KPIs.

## Post-Deploy Verification
1. Run G6 measurement: `python scripts/measure_g6.py --base-url https://your-domain.com --n 50`
2. Verify reporter registration flow end-to-end
3. Verify local-verify / global-verify / kinship-verify endpoints
4. Check RBAC: reporter cannot access admin endpoints
5. Verify audit log entries are written
