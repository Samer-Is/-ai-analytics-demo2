#!/usr/bin/env bash
# Point the deployed app at the reachable production SQL Server IP using the
# LEAST-PRIVILEGE read-only login (NOT sa). Password already lives (escaped)
# in the server .env, so no secrets are passed on the command line.
set -e
cd ~/renty

# DB_SERVER -> reachable IP; keep DB_USER=renty_readonly (read-only).
python3 - <<'PY'
import re
p = ".env"
s = open(p).read()
s = re.sub(r'(?m)^DB_SERVER=.*$', 'DB_SERVER=172.86.86.150', s)
if not re.search(r'(?m)^DB_SERVER=', s):
    s += "\nDB_SERVER=172.86.86.150\n"
s = re.sub(r'(?m)^DB_USER=.*$', 'DB_USER=renty_readonly', s)
open(p, "w").write(s)
print("DB_SERVER set to 172.86.86.150; DB_USER=renty_readonly")
PY

echo "=== recreate container ==="
docker compose -f docker-compose.deploy.yml up -d --force-recreate >/dev/null
sleep 4

echo "=== effective DB target in container ==="
docker exec renty-analytics sh -c 'printf "server=%s user=%s pwd_tail=" "$DB_SERVER" "$DB_USER"; printf "%s\n" "$DB_PASSWORD" | sed -E "s/.*(...)$/...\1/"'

echo "=== connection security audit (must be read-only) ==="
docker exec renty-analytics python -c "from dotenv import load_dotenv; load_dotenv(override=True); import db, json; print(json.dumps(db.get_connection_security(), default=str))"

echo "=== smoke query ==="
docker exec renty-analytics python -c "from dotenv import load_dotenv; load_dotenv(override=True); import db; print('smoke:', db.smoke_test())" 2>&1 | tail -4
