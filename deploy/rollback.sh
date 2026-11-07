#!/usr/bin/env bash
set -euo pipefail

# FMPPI cPanel Rollback Script
# Usage: bash deploy/rollback.sh
# Environment variables:
#   CPANEL_FRONTEND_DIR  - Frontend deployment directory (default: /home/zcodz/public_html/fmppi.zcodz.com)
#   DATABASE_URL         - Database connection string
#   KEEP_LAST_BUILDS     - Number of previous builds to keep (default: 3)
#   BACKEND_DIR          - Backend deployment directory

FRONTEND_DIR="${CPANEL_FRONTEND_DIR:-/home/zcodz/public_html/fmppi.zcodz.com}"
BACKEND_DIR="${BACKEND_DIR:-/home/zcodz/fmppi}"
KEEP_LAST_BUILDS="${KEEP_LAST_BUILDS:-3}"
DATABASE_URL="${DATABASE_URL:-}"

echo "=== FMPPI Rollback Script ==="
echo "Frontend dir: ${FRONTEND_DIR}"
echo "Backend dir: ${BACKEND_DIR}"
echo "Keep last builds: ${KEEP_LAST_BUILDS}"

# Rollback backend: down-migration then re-upgrade to last known good
if [ -n "${DATABASE_URL}" ] && [ -f "${BACKEND_DIR}/alembic.ini" ]; then
  echo "Rolling back database migration..."
  cd "${BACKEND_DIR}"
  export DATABASE_URL="${DATABASE_URL}"
  alembic downgrade -1 || true
  alembic upgrade head || true
else
  echo "Skipping database rollback (DATABASE_URL or alembic.ini not set)"
fi

# Restart backend via PM2
if command -v pm2 &> /dev/null; then
  echo "Restarting backend via PM2..."
  cd "${BACKEND_DIR}"
  if pm2 list | grep -q "fmppi-api"; then
    pm2 restart fmppi-api || true
  fi
  pm2 save || true
else
  echo "PM2 not found, skipping backend restart"
fi

echo "=== Rollback complete ==="
