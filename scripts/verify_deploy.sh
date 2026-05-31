#!/usr/bin/env bash
# Verify the deployed Renty container is healthy and DB-connected.
set -u
echo "=== container status ==="
docker ps --filter name=renty-analytics --format '{{.Names}} | {{.Status}} | {{.Ports}}'

echo "=== DB password tail (must end in kP9) ==="
docker exec renty-analytics sh -c 'printf "%s\n" "$DB_PASSWORD" | sed -E "s/.*(...)$/...\1/"'

echo "=== DB driver in .env passed to container ==="
docker exec renty-analytics sh -c 'printf "DB_DRIVER=%s\n" "$DB_DRIVER"'

echo "=== ODBC drivers registered ==="
docker exec renty-analytics sh -c 'odbcinst -q -d 2>/dev/null || echo "odbcinst not found"'

echo "=== Streamlit health endpoint ==="
sleep 3
docker exec renty-analytics sh -c 'curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8501/_stcore/health' 2>/dev/null || echo "curl failed"

echo "=== DB connectivity smoke test ==="
docker exec renty-analytics python -c "from dotenv import load_dotenv; load_dotenv(override=True); import db; print('row counts:', db.smoke_test())" 2>&1 | tail -5

echo "=== recent app logs ==="
docker logs renty-analytics 2>&1 | tail -12
