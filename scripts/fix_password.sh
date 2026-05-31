#!/usr/bin/env bash
# Escape the literal $ in DB_PASSWORD so docker compose env_file interpolation
# passes it through unchanged (R3nty!ReadOnly#2026$kP9), then recreate the container.
set -e
cd ~/renty
python3 - <<'PY'
p = ".env"
s = open(p).read()
# Only escape if a single (un-escaped) $kP9 is present.
if "$$kP9" not in s and "$kP9" in s:
    s = s.replace("$kP9", "$$kP9")
    open(p, "w").write(s)
    print("patched: $kP9 -> $$kP9")
else:
    print("no change needed")
PY
echo "=== recreate container ==="
docker compose -f docker-compose.deploy.yml up -d --force-recreate
sleep 4
echo "=== password tail in container (must be kP9) ==="
docker exec renty-analytics sh -c 'printf "%s\n" "$DB_PASSWORD" | sed -E "s/.*(...)$/...\1/"'
