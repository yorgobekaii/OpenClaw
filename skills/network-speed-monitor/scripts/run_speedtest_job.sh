#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$BASE_DIR/logs"
LOCK_DIR="$BASE_DIR/.locks"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUNNER="$SCRIPT_DIR/run_speedtest.py"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"

mkdir -p "$LOG_DIR" "$LOCK_DIR"

export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/v24.14.1/bin:/usr/bin:/bin:$HOME/.nvm/current/bin:$HOME/.npm-global/bin:$HOME/bin:$HOME/.volta/bin:$HOME/.asdf/shims:$HOME/.bun/bin:$HOME/.fnm/current/bin:$HOME/.local/share/pnpm:/usr/local/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:/snap/bin"
export PYTHONUNBUFFERED=1

LOG_FILE="$LOG_DIR/cron.log"
LOCK_FILE="$LOCK_DIR/run_speedtest.lock"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  printf '[%s] skipped: previous speedtest job still running\n' "$TIMESTAMP" >> "$LOG_FILE"
  exit 0
fi

{
  printf '[%s] starting speedtest job\n' "$TIMESTAMP"
  if output="$($PYTHON_BIN "$RUNNER" 2>&1)"; then
    printf '%s\n' "$output"
    printf '[%s] completed successfully\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
    exit 0
  else
    status=$?
    printf '%s\n' "$output"
    printf '[%s] completed with handled failure (exit=%s)\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$status"
    exit 0
  fi
} >> "$LOG_FILE"
