# Speedtest Cron

## What this does

- runs the speedtest job on a schedule
- avoids overlapping runs with `flock`
- writes all cron output to `skills/network-speed-monitor/logs/cron.log`
- treats measurement failures as handled/logged events instead of uncaught cron noise
- records failed runs in the JSONL/CSV logs with `status=error` and `failure_reason`

## Install

Default schedule: every 30 minutes

```bash
bash skills/network-speed-monitor/install_cron.sh
```

Custom schedule example: every hour at minute 5

```bash
bash skills/network-speed-monitor/install_cron.sh '5 * * * *'
```

## Files

- Job wrapper: `skills/network-speed-monitor/scripts/run_speedtest_job.sh`
- Python runner: `skills/network-speed-monitor/scripts/run_speedtest.py`
- Cron log: `skills/network-speed-monitor/logs/cron.log`
- Structured results: `skills/network-speed-monitor/references/speed-log.jsonl`
- CSV export: `skills/network-speed-monitor/references/speed-log.csv`

## Notes

The wrapper exits cleanly even when the measurement fails, because the failure is already captured in the structured logs. That keeps cron from producing unaccounted-for failures while preserving the error details for diagnosis.
