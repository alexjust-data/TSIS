from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_RAW_ROOT = Path(r"E:/TSIS/data/ohlcv_1m")
DEFAULT_OUTPUT_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1"
)
DEFAULT_REPAIR_SHARD_ROOTS = [
    Path(r"C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838/repair_shards"),
    Path(r"C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_lt1b_missing180_20260703_092956/repair_shards"),
    Path(r"C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_lt1b_licn_repair_20260703/repair_shards"),
]
DATASET_ID = "ohlcv_1m_quote_guarded_full_universe_v0_1"
SCRIPT_CONTRACT_VERSION = "v0_1"
REPAIR_SUFFIX = "_repair_manifest.parquet"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_years(value: str) -> List[int]:
    years: List[int] = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start, end = chunk.split("-", 1)
            years.extend(range(int(start), int(end) + 1))
        else:
            years.append(int(chunk))
    return sorted(set(years))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def atomic_write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}.{time.time_ns()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True, default=str) + "\n")


def human_bytes(n: Optional[float]) -> str:
    if n is None:
        return "unknown"
    value = float(n)
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(value) < 1024.0:
            return f"{value:.2f}{unit}"
        value /= 1024.0
    return f"{value:.2f}PiB"


def script_sha256(path: Path) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(block)
        return h.hexdigest()
    except OSError:
        return None


def git_context(cwd: Optional[Path] = None) -> Dict[str, Any]:
    root = cwd or Path.cwd()
    result: Dict[str, Any] = {}
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(root), text=True, stderr=subprocess.DEVNULL
        ).strip()
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(root), text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = subprocess.check_output(
            ["git", "status", "--short"], cwd=str(root), text=True, stderr=subprocess.DEVNULL
        ).strip()
        result.update({"git_branch": branch, "git_commit": commit, "git_dirty_state": bool(dirty)})
    except Exception:
        result.update({"git_branch": None, "git_commit": None, "git_dirty_state": None})
    return result


def build_run_root(output_root: Path, run_id: str) -> Path:
    return output_root / "_build_runs" / run_id


def make_run_id(prefix: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{stamp}"


def base_manifest(
    *,
    run_id: str,
    script_path: Path,
    command_line: Sequence[str],
    mode: str,
    input_roots: Dict[str, str],
    output_roots: Dict[str, str],
    expected_scope: Dict[str, Any],
    monitor_command: str,
    resume_policy: str,
    overwrite_policy: str,
    success_criteria: Sequence[str],
) -> Dict[str, Any]:
    payload = {
        "run_id": run_id,
        "status": "starting",
        "created_at_utc": utc_now(),
        "script_path": str(script_path),
        "script_version_or_hash": script_sha256(script_path),
        "command_line": " ".join(str(x) for x in command_line),
        "cwd": str(Path.cwd()),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.executable,
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "parent_pid": os.getppid(),
        "wrapper_pid": os.getpid(),
        "mode": mode,
        "input_roots": input_roots,
        "output_roots": output_roots,
        "expected_scope": expected_scope,
        "resume_policy": resume_policy,
        "overwrite_policy": overwrite_policy,
        "success_criteria": list(success_criteria),
        "monitor_command": monitor_command,
    }
    payload.update(git_context(Path(r"C:/TSIS_Data")))
    return payload


def write_heartbeat(run_root: Path, payload: Dict[str, Any]) -> None:
    payload = dict(payload)
    payload.setdefault("observed_at_utc", utc_now())
    atomic_write_json(run_root / "heartbeat_latest.json", payload)
    append_jsonl(run_root / "heartbeat.jsonl", payload)


def parse_raw_partition(path: Path) -> Optional[Dict[str, Any]]:
    parts = path.parts
    ticker = None
    year = None
    month = None
    for part in parts:
        if part.startswith("ticker="):
            ticker = part.split("=", 1)[1]
        elif part.startswith("year="):
            try:
                year = int(part.split("=", 1)[1])
            except ValueError:
                return None
        elif part.startswith("month="):
            m = part.split("=", 1)[1]
            try:
                month = int(m)
            except ValueError:
                return None
    if ticker is None or year is None or month is None:
        return None
    return {"ticker": ticker, "year": year, "month": month, "path": str(path)}


def parse_repair_shard(path: Path) -> Optional[Dict[str, Any]]:
    name = path.name
    if not name.endswith(REPAIR_SUFFIX):
        return None
    stem = name[: -len(REPAIR_SUFFIX)]
    parts = stem.rsplit("_", 2)
    if len(parts) != 3:
        return None
    ticker, year_s, month_s = parts
    try:
        return {"ticker": ticker, "year": int(year_s), "month": int(month_s), "path": str(path)}
    except ValueError:
        return None


def iter_raw_files(raw_root: Path, years: Iterable[int]) -> Iterable[Path]:
    for year in sorted(set(years)):
        pattern = f"ticker=*/year={year}/month=*/*.parquet"
        yield from raw_root.glob(pattern)


def iter_repair_shards(roots: Sequence[Path], years: Iterable[int]) -> Iterable[Path]:
    allowed = set(int(y) for y in years)
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob(f"*{REPAIR_SUFFIX}"):
            meta = parse_repair_shard(path)
            if meta and meta["year"] in allowed:
                yield path


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], fieldnames: Sequence[str]) -> int:
    ensure_dir(path.parent)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
            count += 1
    return count


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def file_stat(path: Path) -> Dict[str, Any]:
    st = path.stat()
    return {
        "bytes": st.st_size,
        "mtime_utc": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
    }


def compact_log_line(payload: Dict[str, Any]) -> str:
    return (
        f"[{payload.get('observed_at_utc')}] status={payload.get('status')} "
        f"stage={payload.get('stage')} elapsed_sec={payload.get('elapsed_seconds')} "
        f"progress={payload.get('completed_tickers')}/{payload.get('total_tickers')} "
        f"item={payload.get('active_ticker')} rows={payload.get('rows_written')} "
        f"repairs={payload.get('repairs_applied')} failures={payload.get('failed_tickers')}"
    )
