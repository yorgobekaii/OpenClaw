#!/usr/bin/env bash
set -euo pipefail
KEY_FILE="$HOME/.config/network-speed-monitor/gog_keyring_password"
if [[ -f "$KEY_FILE" ]]; then
  export GOG_KEYRING_PASSWORD="$(cat "$KEY_FILE")"
fi
export GOG_ACCOUNT="shareq.org@gmail.com"
