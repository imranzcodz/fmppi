# Deployment (cPanel)

## Local
- Docker Compose: api, web, db, ml (GPU optional)
- `docker compose up --build`

## Staging
- GitHub Actions → self-hosted runner → docker compose

## Production (shared cPanel)

### Prerequisites
- cPanel account with MySQL database, FTP access, and SSH access
- GitHub Secrets configured (see "Secrets" below)
- cPanel "Setup Python App" for the backend (or PM2 via SSH)

### Directory Structure on cPanel
| Component | Path | Purpose |
|-----------|------|---------|
| Frontend static files | `/home/zcodz/public_html/fmppi.zcodz.com/` | React Vite build output served by Apache/Nginx |
| Backend application | `/home/zcodz/fmppi/` | FastAPI app, Alembic migrations, PM2 process |

### Deployment Flow (GitHub Actions → cPanel)
On every push to `main` (or manual `workflow_dispatch`):

1. **Build** — Frontend is built with Vite (`npm run build`) producing `frontend/dist/`
2. **Deploy Frontend** — `frontend/dist/` is uploaded via FTP to `/home/zcodz/public_html/fmppi.zcodz.com/`
3. **Deploy Backend** — `backend/` source files are uploaded via FTP to `/home/zcodz/fmppi/`
   - Excludes: `.env`, `.env.example`, `tests/`, `__pycache__/`, `*.db`, `uploads/`, `.git/`
4. **Migrate & Restart** — SSH into cPanel, run `alembic upgrade head`, then restart `fmppi-api` via PM2

### Secrets (GitHub Secrets → cPanel)
Add these to your repository **Settings → Secrets and variables → Actions**:

| Secret | Description | Example |
|--------|-------------|---------|
| `CPANEL_FTP_HOST` | cPanel FTP host | `ftp.zcodz.com` or `zcodz.com` |
| `CPANEL_FTP_USER` | cPanel FTP username | `zcodz` |
| `CPANEL_FTP_PASS` | cPanel FTP password | *(your password)* |
| `CPANEL_SSH_HOST` | cPanel SSH host | `zcodz.com` |
| `CPANEL_SSH_USER` | cPanel SSH username | `zcodz` |
| `CPANEL_SSH_KEY` | cPanel SSH private key | OpenSSH private key |
| `CPANEL_DATABASE_URL` | cPanel MySQL connection string | `mysql+pymysql://user:pass@localhost/db` |
| `CPANEL_SECRET_KEY` | Django/FastAPI secret key | *(random string)* |
| `MODEL_VERSION` | ML model version tag | `v1` |
| `GLOBAL_VERIFY_ENABLED` | Enable global web search | `true` |

### cPanel Setup Steps (One-Time)

#### 1. Create MySQL Database
- cPanel → MySQL Databases → Create database `fmppi`
- Create MySQL user and assign to database with all privileges
- Note the connection string for `CPANEL_DATABASE_URL`

#### 2. Setup Python App (Optional - if using cPanel Python App)
- cPanel → Software → "Setup Python App"
- Python version: 3.11
- Application root: `/home/zcodz/fmppi`
- Application URL: `fmppi.zcodz.com` or subdomain
- Entry point: `main:app` (or `backend/app/main:app` depending on structure)
- Add environment variables from secrets above
- Click "Create"

#### 3. Setup PM2 (Alternative to cPanel Python App)
- SSH into cPanel: `ssh zcodz@zcodz.com`
- Install PM2: `npm install -g pm2` (or use Node.js selector in cPanel)
- The GitHub Action will start `pm2 start main.py --name fmppi-api`

#### 4. Frontend Domain
- cPanel → Domains → Add `fmppi.zcodz.com` as an addon domain or subdomain
- Document root: `/home/zcodz/public_html/fmppi.zcodz.com`

### Rollback
- On deployment failure, the `rollback` job runs:
  1. `alembic downgrade -1` then `alembic upgrade head`
  2. `pm2 restart fmppi-api`
- Custom rollback script: `deploy/rollback.sh`

### Files NOT Deployed to cPanel
The following are excluded from FTP upload:
- `.env`, `.env.example` (secrets — set via cPanel environment variables)
- `tests/`, `test_*.py`, `conftest.py`
- `__pycache__/`, `*.pyc`, `*.pyo`
- `*.db`, `*.sqlite` (local databases)
- `uploads/` (user-uploaded evidence — managed separately)
- `.git/`, `.gitignore`
- `.ruff_cache/`, `coverage/`, `.coverage`

### Environment Variables on cPanel
Set these in cPanel → Software → "Setup Python App" → Environment Variables, or via `.env` file in `/home/zcodz/fmppi/`:

```
DATABASE_URL=mysql+pymysql://user:pass@localhost/fmppi
SECRET_KEY=your-secret-key-here
MODEL_VERSION=v1
GLOBAL_VERIFY_ENABLED=true
ML_SERVICE_URL=http://localhost:8001
```

### Troubleshooting
- **403 Forbidden on verify endpoints**: Ensure the user role has `verify:local` permission (Reporter role cannot run matches; Investigator/Admin can)
- **Alembic migration fails**: Check `DATABASE_URL` matches cPanel MySQL credentials
- **PM2 not found**: Install Node.js via cPanel "Setup Node.js App" then `npm install -g pm2`
- **Frontend not loading**: Verify addon domain document root matches `/home/zcodz/public_html/fmppi.zcodz.com/`
