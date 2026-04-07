#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JOB_SCRIPT="$SCRIPT_DIR/scripts/run_speedtest_job.sh"
SCHEDULE="${1:-*/30 * * * *}"
CRON_LINE="$SCHEDULE /usr/bin/env bash $JOB_SCRIPT"

TMP_FILE="$(mktemp)"
cleanup() {
  rm -f "$TMP_FILE"
}
trap cleanup EXIT

if crontab -l > "$TMP_FILE" 2>/dev/null; then
  :
else
  : > "$TMP_FILE"
fi

if grep -Fq "$JOB_SCRIPT" "$TMP_FILE"; then
  echo "Speedtest cron job already installed:"
  grep -F "$JOB_SCRIPT" "$TMP_FILE"
  exit 0
fi

printf '%s\n' "$CRON_LINE" >> "$TMP_FILE"
crontab "$TMP_FILE"

echo "Installed speedtest cron job:"
echo "$CRON_LINE"
