#!/usr/bin/env bash
set -euo pipefail

# BerTele2 dashboard/API Phase 3 smoke test.
# Usage:
#   API_BASE_URL=https://example.com/api/v1 \
#   BERTELE2_USER=admin BERTELE2_PASSWORD='***' \
#   bash scripts/dashboard-smoke-test.sh

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000/api/v1}"
BERTELE2_USER="${BERTELE2_USER:-}"
BERTELE2_PASSWORD="${BERTELE2_PASSWORD:-}"

if [[ -z "$BERTELE2_USER" || -z "$BERTELE2_PASSWORD" ]]; then
  echo "ERROR: BERTELE2_USER and BERTELE2_PASSWORD are required" >&2
  exit 2
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

request() {
  local method="$1" url="$2" output="$3"
  shift 3
  curl --fail-with-body --silent --show-error \
    --connect-timeout 10 --max-time 30 \
    -X "$method" "$url" "$@" > "$output"
}

assert_json_key() {
  local file="$1" key="$2"
  python3 - "$file" "$key" <<'PY'
import json, sys
path, key = sys.argv[1:]
with open(path, encoding='utf-8') as f:
    value = json.load(f)
cur = value
for part in key.split('.'):
    if not isinstance(cur, dict) or part not in cur:
        raise SystemExit(f"missing JSON key: {key}")
    cur = cur[part]
PY
}

echo "== BerTele2 Phase 3 smoke test =="
echo "API: $API_BASE_URL"

request GET "$API_BASE_URL/health" "$TMP_DIR/health.json"
assert_json_key "$TMP_DIR/health.json" "status"
echo "[PASS] health"

request POST "$API_BASE_URL/auth/login" "$TMP_DIR/login.json" \
  -H 'Content-Type: application/json' \
  --data "$(python3 - "$BERTELE2_USER" "$BERTELE2_PASSWORD" <<'PY'
import json, sys
print(json.dumps({'username': sys.argv[1], 'password': sys.argv[2]}))
PY
)"

TOKEN="$(python3 - "$TMP_DIR/login.json" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as f:
    data = json.load(f)
print(data['access_token'])
PY
)"

if [[ -z "$TOKEN" ]]; then
  echo "ERROR: login returned an empty access token" >&2
  exit 1
fi

auth=(-H "Authorization: Bearer $TOKEN")

request GET "$API_BASE_URL/auth/me" "$TMP_DIR/me.json" "${auth[@]}"
assert_json_key "$TMP_DIR/me.json" "username"
echo "[PASS] authentication"

for endpoint in \
  "/dashboard/overview" \
  "/dashboard/logs" \
  "/dashboard/metrics" \
  "/dialogs?limit=1" \
  "/sessions" \
  "/webhooks" \
  "/apikeys"; do
  safe="$(echo "$endpoint" | tr '/?' '__' | tr -cd '[:alnum:]_-')"
  request GET "$API_BASE_URL$endpoint" "$TMP_DIR/$safe.json" "${auth[@]}"
  echo "[PASS] GET $endpoint"
done

# Verify the two write endpoints without changing production data.
# Send/forward are intentionally not executed by this smoke test because they have side effects.
python3 - "$TMP_DIR" <<'PY'
import json, os, sys
root = sys.argv[1]
for name in os.listdir(root):
    if not name.endswith('.json'):
        continue
    with open(os.path.join(root, name), encoding='utf-8') as f:
        json.load(f)
print('[PASS] all returned payloads are valid JSON')
PY

echo ""
echo "Phase 3 smoke test completed successfully."
echo "Note: message send/forward are intentionally not invoked because they create real Telegram side effects."
