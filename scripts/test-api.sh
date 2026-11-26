#!/usr/bin/env bash
# Usage: ./scripts/test-api.sh http://<EC2-PUBLIC-IP>:8080
set -euo pipefail
BASE="${1:-http://localhost:8080}"

echo "== health";  curl -s "$BASE/health"; echo
echo "== create";  curl -s -X POST "$BASE/equipment" -H "Content-Type: application/json" \
                     -d '{"name":"Proyektor Epson","category":"AV"}'; echo
echo "== list";    curl -s "$BASE/equipment"; echo
echo "== borrow";  curl -s -X PUT "$BASE/equipment/1" -H "Content-Type: application/json" \
                     -d '{"status":"borrowed","borrower":"Budi"}'; echo
echo "== get";     curl -s "$BASE/equipment/1"; echo
echo "== delete";  curl -s -o /dev/null -w "HTTP %{http_code}\n" -X DELETE "$BASE/equipment/1"
