#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/gog_env.sh"

SHEET_ID="1yOUa-F6o7-5CtnRnKxkjLxjvNwrYhch_LSPuQMNjfEs"
ACCOUNT="shareq.org@gmail.com"

# Rename the default tab for readability if it still exists.
gog sheets rename-tab "$SHEET_ID" "Sheet1" "Speed Log" --account "$ACCOUNT" >/dev/null 2>&1 || true
# Create/update the main log header area.
gog sheets update "$SHEET_ID" "Speed Log!A1:O2" --account "$ACCOUNT" --input USER_ENTERED --values-json '[
  ["Network Speed Monitor", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
  ["timestamp_utc", "local_time", "download_mbps", "upload_mbps", "ping_ms", "status", "target_delta_mbps", "server_name", "isp", "external_ip", "failure_reason", "cli_used", "server_host", "server_country", "summary"]
]'
