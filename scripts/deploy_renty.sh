#!/usr/bin/env bash
# Server-side deploy script for the Renty AI Analytics app.
# Run on the server: bash ~/deploy_renty.sh
set -euo pipefail

APP_DIR="$HOME/renty"
TARBALL="$HOME/renty_deploy.tar.gz"

echo "==> Cleaning previous extract"
if [ -d "$APP_DIR" ]; then
    find "$APP_DIR" -type d -exec chmod u+rwx {} + 2>/dev/null || true
    rm -rf "$APP_DIR"
fi
mkdir -p "$APP_DIR"

echo "==> Extracting (delay-directory-restore handles read-only dirs)"
tar --delay-directory-restore --no-same-owner --no-same-permissions \
    -xzf "$TARBALL" -C "$APP_DIR" 2>/dev/null || true
chmod -R u+rwX "$APP_DIR"

cd "$APP_DIR"

echo "==> Patching ODBC driver 17 -> 18 in .env"
sed -i 's/ODBC Driver 17 for SQL Server/ODBC Driver 18 for SQL Server/' .env
grep '^DB_DRIVER' .env

echo "==> Verifying key files"
for f in Dockerfile.deploy docker-compose.deploy.yml app.py db.py backend.py \
         prompts.py requirements.txt metadata/renty/_schema.json; do
    if [ -f "$f" ]; then echo "  ok   $f"; else echo "  MISSING $f"; exit 1; fi
done

echo "==> Building and starting container"
docker compose -f docker-compose.deploy.yml up -d --build

echo "==> Status"
docker compose -f docker-compose.deploy.yml ps
echo "==> Done. App should be on http://172.86.86.16:8501"
