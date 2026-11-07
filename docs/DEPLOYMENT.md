# Deployment (cPanel)

## Local
- Docker Compose: api, web, db, ml (GPU optional)

## Staging
- GitHub Actions → self-hosted runner → docker compose

## Production (shared cPanel)
- Frontend: build → upload `dist/` to `public_html/` via FTP
- Backend: Python/Node app via cPanel "Setup Python/Node App" (Passenger) or reverse proxy
- ML inference: ONNX runtime in backend process or external GPU endpoint
- DB: cPanel MySQL; migrations via Alembic
- Secrets: cPanel env vars / `.env` (not committed)
- Backups: nightly DB dump + evidence sync

## Rollback & Feature Flags
- Keep last 3 frontend builds; revert via FTP/SFTP or cPanel file manager.
- DB migrations include down-scripts (Alembic); test rollback in staging first.
- Feature flags (model version, global-verify on/off) in config/YAML; toggle without redeploy.
- Rollback trigger: quality gate failure, security incident, or regression in KPIs.
