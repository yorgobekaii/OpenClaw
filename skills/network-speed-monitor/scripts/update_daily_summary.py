#!/usr/bin/env python3
import json
import statistics
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
JSONL_PATH = BASE / 'references' / 'speed-log.jsonl'
OUT_PATH = BASE / 'references' / 'daily-summary-values.json'

priority = {'good': 0, 'weak': 1, 'unstable': 2}
rows = []
if JSONL_PATH.exists():
    grouped = defaultdict(list)
    for line in JSONL_PATH.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        day = item.get('timestamp', '')[:10]
        if day:
            grouped[day].append(item)

    for day in sorted(grouped):
        items = grouped[day]
        dl = [float(x.get('download_mbps', 0) or 0) for x in items]
        ul = [float(x.get('upload_mbps', 0) or 0) for x in items]
        ping = [float(x.get('ping_ms', 0) or 0) for x in items]
        statuses = [x.get('status', 'good') for x in items]
        worst = sorted(statuses, key=lambda s: priority.get(s, 99))[-1] if statuses else ''
        note = 'Healthy day overall.'
        if worst == 'unstable':
            note = 'At least one unstable run. Review congestion, Wi-Fi quality, and ISP path.'
        elif worst == 'weak':
            note = 'Mostly usable, but below preferred target on one or more runs.'
        rows.append([
            day,
            len(items),
            round(statistics.mean(dl), 2) if dl else '',
            round(statistics.mean(ul), 2) if ul else '',
            round(statistics.mean(ping), 2) if ping else '',
            worst,
            round(max(dl), 2) if dl else '',
            note,
        ])

payload = [
    ["Daily Network Summary", "", "", "", "", "", "", ""],
    ["date", "runs", "avg_download_mbps", "avg_upload_mbps", "avg_ping_ms", "worst_status", "best_download_mbps", "notes"],
] + rows
OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
print(str(OUT_PATH))
