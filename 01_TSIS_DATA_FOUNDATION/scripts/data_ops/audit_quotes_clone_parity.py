"""Audit D:/quotes vs E:/TSIS/data/quotes_ parity.

Read-only for source/target data roots. Writes manifests, heartbeat and
per-ticker evidence under E:/TSIS/data/data_ops_manifests/quotes_parity_audit.

Default check:
  - top-level ticker roster parity;
  - per-ticker relative file path inventory;
  - per-ticker file sizes and byte totals;
  - optional SHA256 hashing.

The script intentionally skips filesystem reparse points, matching the clone
script's robocopy /XJ behavior.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPARSE_POINT = 0x400


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat()


def atomic_write_json(path: Path, payload: dict[str, Any], *, indent: int | None = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    tmp.write_text(json.dumps(payload, indent=indent, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def get_git_snapshot(repo_root: Path) -> dict[str, Any]:
    snapshot: dict[str, Any] = {"branch": None, "commit": None, "dirty_state": "unknown"}
    try:
        snapshot["branch"] = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        snapshot["commit"] = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        snapshot["dirty_state"] = "clean" if not dirty.strip() else "dirty"
    except Exception:
        snapshot["dirty_state"] = "unavailable"
    return snapshot


def is_reparse_point(path: Path) -> bool:
    try:
        attrs = os.stat(path, follow_symlinks=False).st_file_attributes  # type: ignore[attr-defined]
        return bool(attrs & REPARSE_POINT)
    except AttributeError:
        return path.is_symlink()
    except OSError:
        return False


def iter_files_no_reparse(root: Path):
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        p = Path(entry.path)
                        if entry.is_dir(follow_symlinks=False):
                            if is_reparse_point(p):
                                continue
                            pending.append(p)
                        elif entry.is_file(follow_symlinks=False):
                            yield p
                    except OSError:
                        continue
        except OSError:
            continue


def inventory(root: Path) -> tuple[bool, dict[str, int], list[str]]:
    if not root.exists():
        return False, {}, ["missing_root"]
    if not root.is_dir():
        return False, {}, ["not_directory"]
    out: dict[str, int] = {}
    errors: list[str] = []
    root_resolved = root.resolve()
    for file_path in iter_files_no_reparse(root_resolved):
        try:
            rel = str(file_path.relative_to(root_resolved)).replace("/", "\\")
            key = rel.lower()
            out[key] = file_path.stat().st_size
        except Exception as exc:
            errors.append(f"file_error:{file_path}:{exc}")
    return True, out, errors


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_inventory(root: Path) -> tuple[dict[str, str], list[str]]:
    out: dict[str, str] = {}
    errors: list[str] = []
    root_resolved = root.resolve()
    for file_path in iter_files_no_reparse(root_resolved):
        try:
            rel = str(file_path.relative_to(root_resolved)).replace("/", "\\")
            out[rel.lower()] = sha256_file(file_path)
        except Exception as exc:
            errors.append(f"hash_error:{file_path}:{exc}")
    return out, errors


def audit_ticker(args: tuple[str, str, str, str, str, str]) -> dict[str, Any]:
    ticker, source_root_s, target_root_s, result_root_s, mismatch_root_s, hash_mode = args
    started = utc_now()
    source = Path(source_root_s) / ticker
    target = Path(target_root_s) / ticker
    result_root = Path(result_root_s)
    mismatch_root = Path(mismatch_root_s)

    source_exists, source_map, source_errors = inventory(source)
    target_exists, target_map, target_errors = inventory(target)

    source_keys = set(source_map)
    target_keys = set(target_map)
    missing = sorted(source_keys - target_keys)
    extra = sorted(target_keys - source_keys)
    common = source_keys & target_keys
    size_mismatch = sorted(k for k in common if source_map[k] != target_map[k])

    source_bytes = sum(source_map.values())
    target_bytes = sum(target_map.values())
    structural_ok = (
        source_exists
        and target_exists
        and not source_errors
        and not target_errors
        and not missing
        and not extra
        and not size_mismatch
        and len(source_map) == len(target_map)
        and source_bytes == target_bytes
    )

    hash_checked = False
    hash_ok: bool | None = None
    hash_mismatch_count: int | None = None
    hash_missing_count: int | None = None
    hash_extra_count: int | None = None
    hash_errors: list[str] = []
    if hash_mode == "full" or (hash_mode == "mismatches-only" and not structural_ok):
        hash_checked = True
        source_hashes, source_hash_errors = hash_inventory(source)
        target_hashes, target_hash_errors = hash_inventory(target)
        hash_errors = source_hash_errors + target_hash_errors
        source_hash_keys = set(source_hashes)
        target_hash_keys = set(target_hashes)
        hash_missing = sorted(source_hash_keys - target_hash_keys)
        hash_extra = sorted(target_hash_keys - source_hash_keys)
        hash_common = source_hash_keys & target_hash_keys
        hash_mismatch = sorted(k for k in hash_common if source_hashes[k] != target_hashes[k])
        hash_missing_count = len(hash_missing)
        hash_extra_count = len(hash_extra)
        hash_mismatch_count = len(hash_mismatch)
        hash_ok = not hash_errors and not hash_missing and not hash_extra and not hash_mismatch

    parity_ok = structural_ok and (not hash_checked or hash_ok is True)
    result: dict[str, Any] = {
        "ticker": ticker,
        "started_at_utc": iso(started),
        "ended_at_utc": iso(utc_now()),
        "source": str(source),
        "target": str(target),
        "source_exists": source_exists,
        "target_exists": target_exists,
        "source_file_count": len(source_map),
        "target_file_count": len(target_map),
        "source_bytes": source_bytes,
        "target_bytes": target_bytes,
        "file_count_delta": len(target_map) - len(source_map),
        "bytes_delta": target_bytes - source_bytes,
        "missing_relative_count": len(missing),
        "extra_relative_count": len(extra),
        "size_mismatch_count": len(size_mismatch),
        "missing_relative_sample": missing[:20],
        "extra_relative_sample": extra[:20],
        "size_mismatch_sample": size_mismatch[:20],
        "source_errors": source_errors[:50],
        "target_errors": target_errors[:50],
        "hash_mode": hash_mode,
        "hash_checked": hash_checked,
        "hash_ok": hash_ok,
        "hash_mismatch_count": hash_mismatch_count,
        "hash_missing_in_target_count": hash_missing_count,
        "hash_extra_in_target_count": hash_extra_count,
        "hash_errors": hash_errors[:50],
        "parity_ok": parity_ok,
    }
    result_path = result_root / f"{ticker}.json"
    atomic_write_json(result_path, result)
    if not parity_ok:
        atomic_write_json(mismatch_root / f"{ticker}.json", result)
    return result


def write_heartbeat(
    path: Path,
    *,
    run_id: str,
    status: str,
    stage: str,
    started_at: datetime,
    current: int,
    total: int,
    item: str,
    mismatch_count: int,
    failed_worker_count: int,
    source_root: Path,
    target_root: Path,
    hash_mode: str,
    message: str = "",
) -> None:
    free_gb = None
    try:
        usage = shutil.disk_usage(target_root.anchor)
        free_gb = round(usage.free / (1024**3), 2)
    except Exception:
        pass
    payload = {
        "run_id": run_id,
        "status": status,
        "stage": stage,
        "observed_at_utc": iso(utc_now()),
        "elapsed_seconds": round((utc_now() - started_at).total_seconds(), 1),
        "current_index": current,
        "total_count": total,
        "item": item,
        "mismatch_count": mismatch_count,
        "failed_worker_count": failed_worker_count,
        "hash_mode": hash_mode,
        "source_root": str(source_root),
        "target_root": str(target_root),
        "wrapper_pid": os.getpid(),
        "active_pid": os.getpid(),
        "output_free_gb": free_gb,
        "message": message,
    }
    atomic_write_json(path, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit D:/quotes vs E:/TSIS/data/quotes_ parity")
    parser.add_argument("--source-root", default=r"D:\quotes")
    parser.add_argument("--target-root", default=r"E:\TSIS\data\quotes_")
    parser.add_argument("--log-root", default=r"E:\TSIS\data\data_ops_manifests\quotes_parity_audit")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--hash-mode", choices=["none", "mismatches-only", "full"], default="mismatches-only")
    parser.add_argument("--heartbeat-seconds", type=int, default=30)
    parser.add_argument("--max-tickers", type=int, default=0)
    parser.add_argument("--start-at-ticker", default="")
    parser.add_argument("--tickers", default="", help="Comma-separated explicit ticker list; bypasses shard/start/max selection.")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--run-id", default="")
    parser.add_argument(
        "--resume-existing-results",
        action="store_true",
        help="Reuse valid per-ticker JSON files already present under this run_id ticker_results directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = utc_now()
    run_id = args.run_id or f"quotes_parity_audit_{started.strftime('%Y%m%dT%H%M%SZ')}"
    source_root = Path(args.source_root).resolve()
    target_root = Path(args.target_root).resolve()
    log_root = Path(args.log_root).resolve()
    log_root.mkdir(parents=True, exist_ok=True)

    result_root = log_root / f"{run_id}.ticker_results"
    mismatch_root = log_root / f"{run_id}.mismatches"
    result_root.mkdir(parents=True, exist_ok=True)
    mismatch_root.mkdir(parents=True, exist_ok=True)

    pre_manifest_path = log_root / f"{run_id}.pre_manifest.json"
    heartbeat_path = log_root / f"{run_id}.heartbeat.json"
    pid_manifest_path = log_root / f"{run_id}.pids.json"
    manifest_path = log_root / f"{run_id}.manifest.json"
    summary_csv_path = log_root / f"{run_id}.summary.csv"
    mismatch_csv_path = log_root / f"{run_id}.mismatches.csv"

    if not source_root.exists():
        raise SystemExit(f"Source root does not exist: {source_root}")
    if not target_root.exists():
        raise SystemExit(f"Target root does not exist: {target_root}")
    if source_root == target_root:
        raise SystemExit(f"Source and target are the same path: {source_root}")
    if args.shard_index < 0 or args.shard_index >= args.shard_count:
        raise SystemExit("--shard-index must be >=0 and lower than --shard-count")

    source_tickers = sorted(p.name for p in source_root.iterdir() if p.is_dir())
    target_tickers = sorted(p.name for p in target_root.iterdir() if p.is_dir())
    source_set = {t.lower() for t in source_tickers}
    target_set = {t.lower() for t in target_tickers}
    missing_top = [t for t in source_tickers if t.lower() not in target_set]
    extra_top = [t for t in target_tickers if t.lower() not in source_set]

    if args.tickers:
        if args.start_at_ticker or args.max_tickers > 0 or args.shard_count != 1 or args.shard_index != 0:
            raise SystemExit("--tickers cannot be combined with --start-at-ticker, --max-tickers, or sharding")
        requested_tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
        source_by_lower = {t.lower(): t for t in source_tickers}
        missing_requested = [t for t in requested_tickers if t.lower() not in source_by_lower]
        if missing_requested:
            raise SystemExit(f"Requested tickers not found in source root: {missing_requested}")
        audit_tickers = [source_by_lower[t.lower()] for t in requested_tickers]
    else:
        audit_tickers = list(source_tickers)
        if args.start_at_ticker:
            audit_tickers = [t for t in audit_tickers if t.lower() >= args.start_at_ticker.lower()]
        if args.shard_count > 1:
            total = len(audit_tickers)
            start = math.floor(total * (args.shard_index / args.shard_count))
            end = math.floor(total * ((args.shard_index + 1) / args.shard_count))
            audit_tickers = audit_tickers[start:end]
        if args.max_tickers > 0:
            audit_tickers = audit_tickers[: args.max_tickers]
    if not audit_tickers:
        raise SystemExit("No tickers selected for audit")

    resumed_results: list[dict[str, Any]] = []
    resumed_tickers: set[str] = set()
    resume_invalid_results = 0
    if args.resume_existing_results:
        for ticker in audit_tickers:
            result_path = result_root / f"{ticker}.json"
            if not result_path.exists():
                continue
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
            except Exception:
                resume_invalid_results += 1
                continue
            if str(result.get("ticker", "")).lower() != ticker.lower():
                resume_invalid_results += 1
                continue
            if result.get("hash_mode") != args.hash_mode:
                resume_invalid_results += 1
                continue
            if args.hash_mode == "full" and result.get("hash_checked") is not True:
                resume_invalid_results += 1
                continue
            if "parity_ok" not in result:
                resume_invalid_results += 1
                continue
            resumed_results.append(result)
            resumed_tickers.add(ticker)
    remaining_tickers = [ticker for ticker in audit_tickers if ticker not in resumed_tickers]
    resumed_mismatches = [r for r in resumed_results if not r.get("parity_ok", False)]

    monitor_cmd = (
        f'powershell -NoProfile -ExecutionPolicy Bypass -File '
        f'"C:\\TSIS_Data\\01_TSIS_DATA_FOUNDATION\\scripts\\monitor_long_running_operation.ps1" '
        f'-RunRoot "{log_root}" -RunId "{run_id}" -Compact -Watch'
    )

    pre_manifest = {
        "run_id": run_id,
        "script_path": str(Path(__file__).resolve()),
        "started_at_utc": iso(started),
        "source_root": str(source_root),
        "target_root": str(target_root),
        "log_root": str(log_root),
        "workers": args.workers,
        "hash_mode": args.hash_mode,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "max_tickers": args.max_tickers,
        "start_at_ticker": args.start_at_ticker,
        "tickers": args.tickers,
        "resume_existing_results": args.resume_existing_results,
        "resume_reused_result_count": len(resumed_results),
        "resume_invalid_result_count": resume_invalid_results,
        "resume_remaining_ticker_count": len(remaining_tickers),
        "source_ticker_dirs": len(source_tickers),
        "target_ticker_dirs": len(target_tickers),
        "audit_ticker_count": len(audit_tickers),
        "missing_top_level_count": len(missing_top),
        "extra_top_level_count": len(extra_top),
        "missing_top_level_sample": missing_top[:50],
        "extra_top_level_sample": extra_top[:50],
        "git": get_git_snapshot(Path(r"C:\TSIS_Data")),
        "parity_policy": (
            "pass requires target ticker exists, relative file paths equal, file sizes equal, "
            "byte totals equal, no source/target enumeration errors, and hashes equal when hash mode applies"
        ),
    }
    atomic_write_json(pre_manifest_path, pre_manifest)
    atomic_write_json(
        pid_manifest_path,
        {
            "run_id": run_id,
            "observed_at_utc": iso(utc_now()),
            "wrapper_pid": os.getpid(),
            "active_pid": os.getpid(),
            "active_stage": "ticker_parity_audit",
            "command": "python",
            "script_path": str(Path(__file__).resolve()),
            "monitor_command": monitor_cmd,
        },
    )
    write_heartbeat(
        heartbeat_path,
        run_id=run_id,
        status="running",
        stage="ticker_parity_audit",
        started_at=started,
        current=len(resumed_results),
        total=len(audit_tickers),
        item="",
        mismatch_count=len(resumed_mismatches),
        failed_worker_count=0,
        source_root=source_root,
        target_root=target_root,
        hash_mode=args.hash_mode,
        message=(
            f"resumed_existing_results={len(resumed_results)} remaining={len(remaining_tickers)}"
            if args.resume_existing_results
            else ""
        ),
    )

    print("TSIS quotes clone parity audit", flush=True)
    print(f"Run ID: {run_id}", flush=True)
    print(f"Source: {source_root}", flush=True)
    print(f"Target: {target_root}", flush=True)
    print(f"Log root: {log_root}", flush=True)
    print(f"Workers: {args.workers}", flush=True)
    print(f"HashMode: {args.hash_mode}", flush=True)
    print(f"Shard: {args.shard_index}/{args.shard_count}", flush=True)
    print(f"Audit tickers: {len(audit_tickers)}", flush=True)
    if args.resume_existing_results:
        print(
            f"Resume existing results: {len(resumed_results)} reused, "
            f"{len(remaining_tickers)} remaining, {resume_invalid_results} invalid",
            flush=True,
        )
    print(f"Pre-manifest: {pre_manifest_path}", flush=True)
    print(f"Heartbeat: {heartbeat_path}", flush=True)
    print(f"PID manifest: {pid_manifest_path}", flush=True)
    print("Monitor command:", flush=True)
    print(f"  {monitor_cmd}", flush=True)
    print("", flush=True)

    task_args = [
        (ticker, str(source_root), str(target_root), str(result_root), str(mismatch_root), args.hash_mode)
        for ticker in remaining_tickers
    ]
    completed = len(resumed_results)
    mismatches: list[dict[str, Any]] = list(resumed_mismatches)
    results: list[dict[str, Any]] = list(resumed_results)
    failed_workers = 0
    latest_item = f"resumed:{len(resumed_results)}" if resumed_results else ""
    last_heartbeat = 0.0

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(audit_ticker, item): item[0] for item in task_args}
        while futures:
            done, _ = concurrent.futures.wait(
                futures,
                timeout=max(1, args.heartbeat_seconds),
                return_when=concurrent.futures.FIRST_COMPLETED,
            )
            for fut in done:
                ticker = futures.pop(fut)
                try:
                    result = fut.result()
                except Exception as exc:
                    failed_workers += 1
                    result = {
                        "ticker": ticker,
                        "parity_ok": False,
                        "worker_error": repr(exc),
                    }
                    atomic_write_json(result_root / f"{ticker}.json", result)
                    atomic_write_json(mismatch_root / f"{ticker}.json", result)
                results.append(result)
                completed += 1
                latest_item = ticker
                if not result.get("parity_ok", False):
                    mismatches.append(result)

            now = time.monotonic()
            if now - last_heartbeat >= args.heartbeat_seconds or done:
                write_heartbeat(
                    heartbeat_path,
                    run_id=run_id,
                    status="running",
                    stage="ticker_parity_audit",
                    started_at=started,
                    current=completed,
                    total=len(audit_tickers),
                    item=latest_item,
                    mismatch_count=len(mismatches),
                    failed_worker_count=failed_workers,
                    source_root=source_root,
                    target_root=target_root,
                    hash_mode=args.hash_mode,
                )
                print(
                    f"[{datetime.now().isoformat(timespec='seconds')}] "
                    f"status=running stage=ticker_parity_audit progress={completed}/{len(audit_tickers)} "
                    f"mismatches={len(mismatches)} latest={latest_item}",
                    flush=True,
                )
                last_heartbeat = now

    result_by_ticker = {r.get("ticker"): r for r in results}
    missing_results = [t for t in audit_tickers if t not in result_by_ticker]

    fieldnames = [
        "ticker",
        "parity_ok",
        "source_file_count",
        "target_file_count",
        "file_count_delta",
        "source_bytes",
        "target_bytes",
        "bytes_delta",
        "missing_relative_count",
        "extra_relative_count",
        "size_mismatch_count",
        "hash_mode",
        "hash_checked",
        "hash_ok",
        "hash_mismatch_count",
        "hash_missing_in_target_count",
        "hash_extra_in_target_count",
        "worker_error",
    ]
    with summary_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(results, key=lambda r: str(r.get("ticker"))))
    with mismatch_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(mismatches, key=lambda r: str(r.get("ticker"))))

    status = "completed_pass" if not mismatches and not missing_results and failed_workers == 0 else "completed_fail"
    ended = utc_now()
    manifest = {
        "run_id": run_id,
        "status": status,
        "script_path": str(Path(__file__).resolve()),
        "source_root": str(source_root),
        "target_root": str(target_root),
        "log_root": str(log_root),
        "started_at_utc": iso(started),
        "ended_at_utc": iso(ended),
        "elapsed_seconds": round((ended - started).total_seconds(), 1),
        "workers": args.workers,
        "hash_mode": args.hash_mode,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "source_ticker_dirs": len(source_tickers),
        "target_ticker_dirs": len(target_tickers),
        "audit_ticker_count": len(audit_tickers),
        "result_count": len(results),
        "resume_existing_results": args.resume_existing_results,
        "resume_reused_result_count": len(resumed_results),
        "resume_invalid_result_count": resume_invalid_results,
        "resume_remaining_ticker_count": len(remaining_tickers),
        "missing_result_count": len(missing_results),
        "missing_result_sample": missing_results[:50],
        "parity_ok_count": sum(1 for r in results if r.get("parity_ok") is True),
        "mismatch_count": len(mismatches),
        "mismatch_sample": mismatches[:20],
        "missing_top_level_count": len(missing_top),
        "extra_top_level_count": len(extra_top),
        "summary_csv": str(summary_csv_path),
        "mismatch_csv": str(mismatch_csv_path),
        "ticker_results_root": str(result_root),
        "mismatch_root": str(mismatch_root),
        "pre_manifest_path": str(pre_manifest_path),
        "heartbeat_path": str(heartbeat_path),
        "pid_manifest_path": str(pid_manifest_path),
        "pass_policy": pre_manifest["parity_policy"],
    }
    atomic_write_json(manifest_path, manifest)
    write_heartbeat(
        heartbeat_path,
        run_id=run_id,
        status=status,
        stage="final_manifest_written",
        started_at=started,
        current=len(results),
        total=len(audit_tickers),
        item="",
        mismatch_count=len(mismatches),
        failed_worker_count=failed_workers,
        source_root=source_root,
        target_root=target_root,
        hash_mode=args.hash_mode,
        message=f"manifest={manifest_path}",
    )

    print("", flush=True)
    print("Completed.", flush=True)
    print(f"Status: {status}", flush=True)
    print(f"Audit tickers: {len(audit_tickers)}", flush=True)
    if args.resume_existing_results:
        print(
            f"Resume existing results: {len(resumed_results)} reused, "
            f"{len(remaining_tickers)} remaining, {resume_invalid_results} invalid",
            flush=True,
        )
    print(f"Results: {len(results)}", flush=True)
    print(f"Mismatches: {len(mismatches)}", flush=True)
    print(f"Missing results: {len(missing_results)}", flush=True)
    print(f"Manifest: {manifest_path}", flush=True)
    print(f"Summary CSV: {summary_csv_path}", flush=True)
    print(f"Mismatch CSV: {mismatch_csv_path}", flush=True)
    return 0 if status == "completed_pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
