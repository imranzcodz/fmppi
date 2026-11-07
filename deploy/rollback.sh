#!/usr/bin/env bash
set -euo pipefail

PUBLIC_HTML="${CPANEL_PUBLIC_HTML:-/public_html}"
BACKEND_DIR="${BACKEND_DIR:-~/fmppi/backend}"
KEEP="${KEEP_LAST_BUILDS:-3}"

echo "==> Rollback: restore previous frontend build (keep last ${KEEP})"
if [ -d "${PUBLIC_HTML}/builds" ]; then
  PREVIOUS=$(ls -1d "${PUBLIC_HTML}/builds"/* 2>/dev/null | sort -r | sed -n "2p" | head -n1)
  if [ -n "${PREVIOUS}" ]; then
    ln -sfn "${PREVIOUS}" "${PUBLIC_HTML}/latest"
    echo "restored previous build: ${PREVIOUS}"
  else
    echo "no previous build found to restore"
  fi
else
  echo "no builds directory; skipping frontend rollback"
fi

echo "==> Rollback: DB down-migration (Alembic)"
cd "${BACKEND_DIR}"
alembic downgrade -1

echo "==> Rollback complete"
