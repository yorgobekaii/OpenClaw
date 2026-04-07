#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/gog_env.sh"

SHEET_ID="1yOUa-F6o7-5CtnRnKxkjLxjvNwrYhch_LSPuQMNjfEs"
TAB="Speed Log"
ACCOUNT="shareq.org@gmail.com"
JSON_PATH="$1"

python3 - "$JSON_PATH" <<'PY' | gog sheets append "$SHEET_ID" "${TAB}!A:O" --account "$ACCOUNT" --values-json @- --insert INSERT_ROWS
import json, sys, datetime as dt
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    row = json.load(f)
ts = row['timestamp']
local = dt.datetime.fromisoformat(ts).astimezone().strftime('%Y-%m-%d %H:%M:%S')
server = row.get('server') or ''
summary = row.get('summary') or ''
values = [[
    ts,
    local,
    row.get('download_mbps', ''),
    row.get('upload_mbps', ''),
    row.get('ping_ms', ''),
    row.get('status', ''),
    row.get('target_delta_mbps', ''),
    server,
    row.get('isp', ''),
    row.get('external_ip', ''),
    row.get('failure_reason', ''),
    row.get('cli_used', ''),
    row.get('server_host', ''),
    row.get('server_country', ''),
    summary,
]]
print(json.dumps(values, ensure_ascii=False))
PY
