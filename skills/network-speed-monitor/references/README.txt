Local outputs for the network-speed-monitor skill:

- speed-log.jsonl: append-only raw measurements
- speed-log.csv: spreadsheet-friendly export

Thresholds in use:
- under 50 Mbps: unstable
- 50 to under 80 Mbps: weak
- 80 Mbps and above: good

Each measurement includes timestamp, download/upload Mbps, ping, status label, and server metadata when available.
