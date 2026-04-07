#!/usr/bin/env python3
import csv
import datetime as dt
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REF = BASE / "references"
REF.mkdir(parents=True, exist_ok=True)
JSONL_PATH = REF / "speed-log.jsonl"
CSV_PATH = REF / "speed-log.csv"

THRESHOLDS = {
    "unstable": 50.0,
    "weak": 80.0,
}

TARGET_DOWNLOAD_MBPS = 80.0
MAX_REASONABLE_PING_MS = 10_000.0

# Preferred speedtest servers (Lebanon - closest to user)
# Ordered by preference; Antelias is primary (matches website tests)
PREFERRED_SERVERS = [
    "Antelias Gigabitpro ISP",
    "Kaslik Zina ISP",
    "Broummana FiberSkynet ISP",
    "Beirut IDM",
    "Jdeideh Ogero",
    "Adma Alfa - mic1",
    "Beirut Sodetel",
    "Beirut Pros-Services S.A.R.L.",
    "Beirut WIN-DSL s.a.r.l",
    "Naccache P Foundation / OpenIX Beirut",
]


def run_librespeed_fallback() -> dict:
    """Run librespeed-cli as a fallback when speedtest.net fails."""
    cmd = ["librespeed-cli", "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=420)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    
    if proc.returncode != 0:
        raise RuntimeError(f"librespeed-cli failed: {stderr or stdout or 'exit code ' + str(proc.returncode)}")
    if not stdout:
        raise RuntimeError("librespeed-cli returned empty output")
    
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"librespeed-cli returned non-JSON: {e}")
    
    # LibreSpeed JSON format: { "download": <mbps>, "upload": <mbps>, "ping": <ms>, ... }
    download_mbps = float(data.get("download", 0))
    upload_mbps = float(data.get("upload", 0))
    ping_ms = float(data.get("ping", 0))
    server = data.get("server", {}).get("name") if isinstance(data.get("server"), dict) else data.get("server")
    isp = data.get("isp") or data.get("client", {}).get("isp") if isinstance(data.get("client"), dict) else None
    external_ip = data.get("client", {}).get("ip") if isinstance(data.get("client"), dict) else None
    
    now = dt.datetime.now(dt.timezone.utc).astimezone()
    
    return {
        "timestamp": now.isoformat(),
        "download_mbps": round(download_mbps, 2),
        "upload_mbps": round(upload_mbps, 2),
        "ping_ms": round(ping_ms, 2),
        "status": classify(download_mbps),
        "target_delta_mbps": round(download_mbps - TARGET_DOWNLOAD_MBPS, 2),
        "server": server,
        "server_host": data.get("server", {}).get("host") if isinstance(data.get("server"), dict) else None,
        "server_country": data.get("server", {}).get("country") if isinstance(data.get("server"), dict) else None,
        "isp": isp,
        "external_ip": external_ip,
        "cli_used": "librespeed-cli",
    }


def classify(download_mbps: float) -> str:
    if download_mbps < THRESHOLDS["unstable"]:
        return "unstable"
    if download_mbps < THRESHOLDS["weak"]:
        return "weak"
    return "good"


def validate_measurement(row: dict) -> None:
    download = float(row.get("download_mbps", 0) or 0)
    upload = float(row.get("upload_mbps", 0) or 0)
    ping = float(row.get("ping_ms", 0) or 0)

    for name, value in [("download_mbps", download), ("upload_mbps", upload), ("ping_ms", ping)]:
        if not math.isfinite(value):
            raise RuntimeError(f"invalid {name}: non-finite value")
        if value < 0:
            raise RuntimeError(f"invalid {name}: negative value")

    if ping > MAX_REASONABLE_PING_MS:
        raise RuntimeError(f"invalid ping_ms: {ping:.2f} exceeds sanity limit {MAX_REASONABLE_PING_MS:.0f}")

    if download == 0 and upload == 0:
        raise RuntimeError("invalid measurement: both download and upload are zero")

    server = (row.get("server") or "").strip()
    if not server:
        raise RuntimeError("invalid measurement: missing server information")


def find_cli(prefer_librespeed: bool = False) -> list[str]:
    # If prefer_librespeed is True (fallback mode), try librespeed-cli first
    if prefer_librespeed:
        path = shutil.which("librespeed-cli")
        if path:
            return [path, "--json"]
    
    # Primary options: speedtest (Ookla official) first, then speedtest-cli
    # Ookla CLI matches the website results more closely
    for name in ["speedtest", "speedtest-cli"]:
        path = shutil.which(name)
        if path:
            if name == "speedtest":
                return [path, "--accept-license", "--accept-gdpr", "--format=json"]
            return [path, "--json"]
    
    # Final fallback: librespeed-cli
    path = shutil.which("librespeed-cli")
    if path:
        return [path, "--json"]
    
    raise FileNotFoundError("No speedtest CLI found. Install 'speedtest-cli', 'speedtest', or 'librespeed-cli'.")


def list_available_clis() -> list[list[str]]:
    candidates: list[list[str]] = []

    for name in ["speedtest", "speedtest-cli", "librespeed-cli"]:
        path = shutil.which(name)
        if not path:
            continue
        if name == "speedtest":
            candidates.append([path, "--accept-license", "--accept-gdpr", "--format=json"])
        else:
            candidates.append([path, "--json"])

    if not candidates:
        raise FileNotFoundError("No speedtest CLI found. Install 'speedtest-cli', 'speedtest', or 'librespeed-cli'.")

    return candidates


def should_try_next_cli(error: str) -> bool:
    text = (error or "").lower()
    fallback_markers = [
        "empty output",
        "non-json output",
        "forbidden",
        "403",
        "configuration",
        "cannot retrieve speedtest configuration",
        "failed to connect",
        "network is unreachable",
        "timed out",
        "timeout",
        "temporary failure",
        "temporarily unavailable",
        "ssl",
        "http error",
        "connection reset",
        "broken pipe",
    ]
    return any(marker in text for marker in fallback_markers)


def normalize_result(data: dict, cli_used: str) -> dict:
    is_librespeed = cli_used == "librespeed-cli"

    if "download" in data and isinstance(data["download"], dict):
        # Ookla format: download.bandwidth is in bytes/sec
        download_bps = float(data["download"].get("bandwidth", 0)) * 8
        upload_bps = float(data["upload"].get("bandwidth", 0)) * 8
        ping_ms = float(data.get("ping", {}).get("latency", 0))
        server = (data.get("server") or {}).get("name") or (data.get("server") or {}).get("host")
        isp = data.get("isp")
        external_ip = data.get("interface", {}).get("externalIp")
    elif is_librespeed:
        # LibreSpeed format: values already in Mbps
        download_mbps = float(data.get("download", 0))
        upload_mbps = float(data.get("upload", 0))
        ping_ms = float(data.get("ping", 0))
        server = data.get("server", {}).get("name") if isinstance(data.get("server"), dict) else data.get("server")
        isp = data.get("isp") or (data.get("client", {}).get("isp") if isinstance(data.get("client"), dict) else None)
        external_ip = data.get("client", {}).get("ip") if isinstance(data.get("client"), dict) else None
    else:
        # speedtest-cli format: download/upload in bps
        download_bps = float(data.get("download", 0))
        upload_bps = float(data.get("upload", 0))
        ping_ms = float(data.get("ping", 0))
        server = (data.get("server") or {}).get("name")
        isp = data.get("client", {}).get("isp")
        external_ip = data.get("client", {}).get("ip")

    if not is_librespeed:
        download_mbps = download_bps / 1_000_000
        upload_mbps = upload_bps / 1_000_000

    now = dt.datetime.now(dt.timezone.utc).astimezone()

    row = {
        "timestamp": now.isoformat(),
        "download_mbps": round(download_mbps, 2),
        "upload_mbps": round(upload_mbps, 2),
        "ping_ms": round(ping_ms, 2),
        "status": classify(download_mbps),
        "target_delta_mbps": round(download_mbps - TARGET_DOWNLOAD_MBPS, 2),
        "server": server,
        "server_host": (data.get("server") or {}).get("host") if isinstance(data.get("server"), dict) else None,
        "server_country": (data.get("server") or {}).get("country") if isinstance(data.get("server"), dict) else None,
        "isp": isp,
        "external_ip": external_ip,
        "cli_used": cli_used,
    }
    validate_measurement(row)
    return row


def find_preferred_server(cli_cmd: list[str]) -> list[str] | None:
    """
    List available servers and return --server-id arg for the best match from PREFERRED_SERVERS.
    Returns None if no preferred server is found (let CLI auto-select).
    """
    try:
        # Build server list command
        list_cmd = cli_cmd[:]
        if "speedtest" in list_cmd[0] and "--format=json" in list_cmd:
            # Ookla CLI: --list returns JSON when --format=json is set
            pass
        elif "speedtest-cli" in list_cmd[0]:
            # speedtest-cli: --list returns text
            list_cmd = [list_cmd[0], "--list"]
            proc = subprocess.run(list_cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode != 0:
                return None
            # Parse text output: ID, Name, Country, etc.
            for line in proc.stdout.split("\n"):
                line = line.strip()
                if not line or line.startswith("Retrieving"):
                    continue
                parts = line.split(")", 1)
                if len(parts) != 2:
                    continue
                server_id = parts[0].strip()
                server_info = parts[1]
                for preferred in PREFERRED_SERVERS:
                    if preferred.lower() in server_info.lower():
                        return ["--server", server_id]
            return None
        else:
            # Ookla CLI with --format=json
            list_cmd = [list_cmd[0]] + [a for a in list_cmd[1:] if a != "--format=json"] + ["--list"]
            proc = subprocess.run(list_cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode != 0:
                return None
            # Parse JSON list
            try:
                servers = json.loads(proc.stdout)
                for srv in servers:
                    name = srv.get("name", "") or ""
                    city = srv.get("city", "") or ""
                    full = f"{city} {name}".strip()
                    for preferred in PREFERRED_SERVERS:
                        if preferred.lower() in full.lower():
                            server_id = srv.get("id")
                            if server_id:
                                return ["--server-id", str(server_id)]
            except json.JSONDecodeError:
                pass
            return None
    except Exception:
        return None


def run_measurement() -> dict:
    last_error = None

    for base_cmd in list_available_clis():
        cli_used = Path(base_cmd[0]).name
        using_librespeed = cli_used == "librespeed-cli"

        server_arg = None
        if not using_librespeed:
            server_arg = find_preferred_server(base_cmd)

        cmd = base_cmd[:]
        if cli_used == "speedtest-cli":
            cmd.insert(1, "--secure")

        if server_arg:
            insert_pos = len(cmd)
            for i, part in enumerate(cmd):
                if part in ["--json", "--format=json"]:
                    insert_pos = i
                    break
            for arg in reversed(server_arg):
                cmd.insert(insert_pos, arg)

        attempt_cmds = [cmd[:]]
        if cli_used == "speedtest-cli" and "--secure" in cmd:
            attempt_cmds.append([part for part in cmd if part != "--secure"])

        for attempt_idx, attempt_cmd in enumerate(attempt_cmds, start=1):
            proc = subprocess.run(attempt_cmd, capture_output=True, text=True, timeout=420)
            stdout = (proc.stdout or "").strip()
            stderr = (proc.stderr or "").strip()

            if proc.returncode != 0:
                last_error = f"{cli_used} failed: {stderr or stdout or 'exit code ' + str(proc.returncode)}"
                if should_try_next_cli(last_error):
                    break
                continue

            if not stdout:
                last_error = f"{cli_used} returned empty output for command: {' '.join(attempt_cmd)}"
                break

            try:
                data = json.loads(stdout)
            except json.JSONDecodeError:
                last_error = f"{cli_used} returned non-JSON output. stdout={stdout[:300]!r} stderr={stderr[:300]!r}"
                break

            try:
                return normalize_result(data, cli_used)
            except Exception as exc:
                last_error = f"{cli_used} produced invalid measurement: {exc}"
                if attempt_idx < len(attempt_cmds):
                    continue
                break

        time.sleep(1)

    raise RuntimeError(last_error or "speedtest command failed across all available CLIs")


def load_history(limit: int = 20) -> list[dict]:
    if not JSONL_PATH.exists():
        return []
    rows = []
    with JSONL_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                if row.get("download_mbps") in (None, ""):
                    continue
                row["download_mbps"] = float(row["download_mbps"])
            except (TypeError, ValueError):
                continue
            rows.append(row)
    return rows[-limit:]


def append_logs(row: dict) -> None:
    with JSONL_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    write_header = not CSV_PATH.exists()
    with CSV_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "download_mbps", "upload_mbps", "ping_ms", "status", "target_delta_mbps", "server", "isp", "external_ip", "failure_reason", "cli_used", "server_host", "server_country", "summary"],
        )
        if write_header:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in writer.fieldnames})


def build_failure_row(reason: str) -> dict:
    now = dt.datetime.now(dt.timezone.utc).astimezone()
    message = (reason or "unknown error").strip()
    return {
        "timestamp": now.isoformat(),
        "download_mbps": "",
        "upload_mbps": "",
        "ping_ms": "",
        "status": "error",
        "target_delta_mbps": "",
        "server": "",
        "server_host": "",
        "server_country": "",
        "isp": "",
        "external_ip": "",
        "cli_used": "",
        "failure_reason": message,
        "summary": f"Speedtest failed: {message}",
    }


def append_to_sheet(row: dict) -> str | None:
    script = BASE / "scripts" / "append_to_sheet.sh"
    if not script.exists():
        return None
    if not shutil.which("gog"):
        return "Google Sheets sync skipped: gog CLI not found in PATH"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tmp:
        json.dump(row, tmp, ensure_ascii=False)
        tmp_path = tmp.name
    try:
        last_error = None
        for attempt in range(3):
            proc = subprocess.run([str(script), tmp_path], capture_output=True, text=True, timeout=120)
            if proc.returncode == 0:
                return None
            last_error = proc.stderr.strip() or proc.stdout.strip() or "sheet append failed"
            transient = any(token in last_error.lower() for token in ["timeout", "timed out", "deadline exceeded", "i/o timeout", "connection reset", "temporarily unavailable", "round trip"])
            if transient and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            return last_error
        return last_error
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def build_summary(current: dict, history: list[dict]) -> str:
    recent = [h for h in history if isinstance(h.get("download_mbps"), (int, float))]
    ts = dt.datetime.fromisoformat(current["timestamp"]).astimezone().strftime("%H:%M")
    base = (
        f"Speedtest {ts} — {current['download_mbps']}↓ / {current['upload_mbps']}↑ Mbps, "
        f"ping {current['ping_ms']} ms. Status: {current['status']}."
    )
    extras = []

    gap = current["download_mbps"] - TARGET_DOWNLOAD_MBPS
    if gap >= 0:
        extras.append(f"At or above your 80 Mbps target by {gap:.2f} Mbps.")
    else:
        extras.append(f"Below your 80 Mbps target by {abs(gap):.2f} Mbps.")

    if recent:
        avg = statistics.mean(float(h["download_mbps"]) for h in recent)
        if avg > 0:
            delta_pct = ((current["download_mbps"] - avg) / avg) * 100
            if delta_pct <= -20:
                extras.append(f"This is {abs(delta_pct):.0f}% below your recent average.")
            elif delta_pct >= 20:
                extras.append(f"This is {abs(delta_pct):.0f}% above your recent average.")
            else:
                extras.append("Roughly in line with recent runs.")

    if current["status"] == "unstable":
        extras.append("Likely issue: congestion, weak Wi-Fi, ISP slowdown, or another device saturating the line. Try checking router load, moving closer to the access point, or retesting over Ethernet.")
    elif current["status"] == "weak":
        extras.append("Throughput is usable but below your preferred range. Likely causes: mild congestion, Wi-Fi interference, or ISP/server-side variation. A quick router reboot or a test closer to the router may help confirm it.")
    else:
        extras.append("Throughput looks healthy for your usual line.")

    if current["ping_ms"] >= 120:
        extras.append("Latency is very high. That usually points to routing issues, congestion, VPN overhead, or weak wireless signal.")
    elif current["ping_ms"] >= 80:
        extras.append("Latency is on the high side. Expect lag in calls, gaming, and remote sessions.")
    elif current["ping_ms"] >= 40:
        extras.append("Latency is acceptable but not especially crisp.")
    else:
        extras.append("Latency looks good.")

    return " ".join([base] + extras)


def main() -> int:
    try:
        history = load_history()
        current = run_measurement()
        summary = build_summary(current, history)
        current["summary"] = summary
        sheet_error = append_to_sheet(current)
        if sheet_error:
            current["failure_reason"] = f"Google Sheets sync failed: {sheet_error}"
        append_logs(current)
        if sheet_error:
            print(f"{summary} Google Sheets sync failed this run: {sheet_error}")
        else:
            print(summary)
        return 0
    except Exception as e:
        msg = str(e)
        failure = build_failure_row(msg)
        try:
            append_logs(failure)
        except Exception:
            pass
        try:
            append_to_sheet(failure)
        except Exception:
            pass
        print(f"Speedtest failed: {msg}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
