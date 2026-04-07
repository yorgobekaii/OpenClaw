---
name: network-speed-monitor
description: Measure and log internet speed test results on the local machine and summarize network stability over time. Use when setting up recurring bandwidth checks, classifying download/upload performance, comparing results against thresholds, or reviewing saved speed logs for patterns and degradation.
---

# Network Speed Monitor

## Overview

Use this skill to run a local network speed test, append the results to machine-local logs, and generate short human-readable summaries with simple threshold-based classification.

## Workflow

1. Ensure a speed test CLI is available.
2. Prefer `speedtest-cli` on this machine. Fall back to `speedtest` if unavailable.
3. If speedtest.net returns 403/blocked, automatically fall back to `librespeed-cli`.
4. Run the measurement script.
5. Save one JSON line per run to the log file.
6. Compare the new result with recent history.
7. Classify the connection using the current thresholds.
8. Send a short chat-friendly summary.

## Default thresholds

Use these download-speed labels for this setup:

- Under 50 Mbps: unstable
- 50 to under 80 Mbps: weak
- 80 Mbps and above: good

Treat 80 Mbps as the practical target. The closer the result is to 80 Mbps or above, the better.

If ping is unusually high, packet path looks bad, or the change versus recent runs is large, mention that in the summary together with likely causes and what to check next.

## Local files

- Raw log: `skills/network-speed-monitor/references/speed-log.jsonl`
- CSV export: `skills/network-speed-monitor/references/speed-log.csv`
- Runner: `skills/network-speed-monitor/scripts/run_speedtest.py`

## Running manually

Run:

```bash
python3 skills/network-speed-monitor/scripts/run_speedtest.py
```

The script prints a concise summary and updates both JSONL and CSV logs.

## Summary format

Keep outbound summaries compact and useful. Include:

- current download/upload/ping
- current label
- comparison against recent average when enough history exists
- a warning if the result is below the unstable threshold

Example style:

- `Speedtest 10:00 — 42.3↓ / 18.9↑ Mbps, ping 31 ms. Status: unstable. This is 38% below your recent average.`
- `Speedtest 14:00 — 185.6↓ / 52.4↑ Mbps, ping 14 ms. Status: okay. Roughly in line with recent runs.`

## Installing CLIs

- **speedtest-cli** (Python, uses speedtest.net): `pip install speedtest-cli`
- **speedtest** (Ookla official): Follow https://www.speedtest.net/apps/cli
- **librespeed-cli** (LibreSpeed, fallback): `npm install -g librespeed-cli` or via package manager

The script auto-falls back in this order: `speedtest-cli` → `speedtest` → `librespeed-cli`.

## Notes

Prefer local logging first. If the user later wants Google Sheets or another destination, add that as a separate integration rather than replacing the local log.
