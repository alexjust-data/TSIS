# ruff: noqa: E402
"""Resume-safe acquisition of a hash-authorized SEC PIT v0.2 selection plan."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.authorization import file_sha256, validate_download_authorization
from sec_pit.client import SecClient
from sec_pit.storage import ContentAddressedStore, append_jsonl, atomic_write_json, read_jsonl
from sec_pit.telemetry import LiveResourceTelemetry, percentile, summarize_document_performance


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def completed_urls(log_path: Path) -> set[str]:
    if not log_path.is_file():
        return set()
    return {
        str(row["url"])
        for row in read_jsonl([log_path])
        if row.get("status") == "FETCHED" and row.get("sha256")
    }


def classify_acquisition_scope(gates: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    state = gates["primary_document_acquisition_state"].astype(str)
    eligible = sorted(
        gates.loc[state.eq("ELIGIBLE_FOR_GOVERNED_REVIEW"), "ticker"]
        .astype(str)
        .unique()
    )
    security_class_halts = sorted(
        gates.loc[state.eq("HALT_SECURITY_CLASS"), "ticker"].astype(str).unique()
    )
    local_complete = sorted(
        gates.loc[state.eq("LOCAL_EVIDENCE_COMPLETE"), "ticker"].astype(str).unique()
    )
    return eligible, security_class_halts, local_complete


def parse_args() -> argparse.Namespace:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--probe-root", type=Path, required=True)
    value.add_argument("--authorization", type=Path)
    value.add_argument("--output-root", type=Path, required=True)
    value.add_argument("--run-id", required=True)
    value.add_argument("--execute", action="store_true")
    value.add_argument("--resume", action="store_true")
    value.add_argument("--user-agent", default=os.environ.get("SEC_USER_AGENT"))
    value.add_argument("--requests-per-second", type=float, default=5.0)
    value.add_argument("--minimum-free-space-gib", type=float, default=100.0)
    value.add_argument("--telemetry-interval-seconds", type=float, default=10.0)
    return value.parse_args()


def main() -> int:
    args = parse_args()
    probe_root = args.probe_root.resolve()
    final_path = probe_root / "final_manifest.json"
    selection_path = probe_root / "document_selection_plan_v0_2.parquet"
    gates_path = probe_root / "gate_matrix.parquet"
    for required in (final_path, selection_path, gates_path):
        if not required.is_file():
            raise FileNotFoundError(required)
    probe = json.loads(final_path.read_text(encoding="utf-8-sig"))
    if probe.get("status") != "COMPLETE" or probe.get("probe_gate") != "PASS":
        raise RuntimeError("Predownload probe is not COMPLETE/PASS")
    gates = pd.read_parquet(gates_path)
    eligible, security_class_halts, local_complete = classify_acquisition_scope(gates)
    rows = pd.read_parquet(selection_path)

    run_root = args.output_root.resolve() / "runs" / args.run_id
    if run_root.exists() and not args.resume:
        raise FileExistsError(f"Run exists; use --resume: {run_root}")
    run_root.mkdir(parents=True, exist_ok=True)
    monitor_path = SCRIPT_DIR / "monitor_authorized_primary_acquisition_v0_2.ps1"
    monitor_command = (
        "powershell -NoProfile -ExecutionPolicy Bypass -File "
        f'"{monitor_path}" -RunRoot "{run_root}" -IntervalSeconds 10 -Compact -Watch'
    )
    free_gib = shutil.disk_usage(args.output_root.resolve()).free / (1024**3)
    if free_gib < args.minimum_free_space_gib:
        raise RuntimeError(
            f"Free-space gate failed: {free_gib:.2f} < {args.minimum_free_space_gib:.2f} GiB"
        )
    manifest: dict[str, Any] = {
        "run_id": args.run_id,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "component_sha256": {
            path.name: file_sha256(path)
            for path in (
                Path(__file__).resolve(),
                SCRIPT_DIR / "authorization.py",
                SCRIPT_DIR / "client.py",
                SCRIPT_DIR / "storage.py",
                SCRIPT_DIR / "telemetry.py",
                monitor_path,
            )
        },
        "host": socket.gethostname(),
        "wrapper_pid": os.getpid(),
        "mode": "execute" if args.execute else "plan",
        "probe_manifest_path": final_path.as_posix(),
        "probe_manifest_sha256": file_sha256(final_path),
        "selection_plan_path": selection_path.as_posix(),
        "selection_plan_sha256": file_sha256(selection_path),
        "eligible_tickers": eligible,
        "security_class_halts": security_class_halts,
        "local_evidence_complete_tickers": local_complete,
        "requests_per_second": args.requests_per_second,
        "minimum_free_space_gib": args.minimum_free_space_gib,
        "free_space_gib_at_start": round(free_gib, 3),
        "concurrency": 1,
        "resume_policy": "skip_urls_with_prior_FETCHED_sha256",
        "overwrite_policy": "content_addressed_objects_never_overwritten",
        "network_access": "NOT_EXECUTED" if not args.execute else "AUTHORIZED_ONLY",
        "telemetry": {
            "interval_seconds": args.telemetry_interval_seconds,
            "heartbeat_latest": (run_root / "heartbeat_latest.json").as_posix(),
            "heartbeat_history": (run_root / "heartbeat.jsonl").as_posix(),
            "document_performance": (run_root / "document_performance.jsonl").as_posix(),
            "performance_summary": (run_root / "performance_summary.json").as_posix(),
            "monitor_command": monitor_command,
            "semantic_status": "RUNTIME_DIAGNOSTIC_NOT_INSTITUTIONAL_EVIDENCE",
        },
    }
    atomic_write_json(run_root / "pre_manifest.json", manifest)
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "wrapper_pid": os.getpid(),
            "started_at_utc": utc_now(),
            "expected_alive": args.execute,
        },
    )
    print(f"run_root={run_root}")
    print(f"monitor={monitor_command}")
    if not args.execute:
        final = {**manifest, "status": "COMPLETE", "result": "PLAN_ONLY", "ended_at_utc": utc_now()}
        atomic_write_json(run_root / "final_manifest.json", final)
        atomic_write_json(run_root / "heartbeat_latest.json", final)
        print(json.dumps(final, indent=2))
        return 0
    if not args.authorization:
        raise ValueError("--authorization is required with --execute")
    if not args.user_agent:
        raise ValueError("--user-agent or SEC_USER_AGENT is required with --execute")
    decision = validate_download_authorization(
        args.authorization.resolve(),
        probe_manifest_path=final_path,
        selection_plan_path=selection_path,
        technically_eligible_tickers=eligible,
    )
    if decision.gate != "PASS":
        raise RuntimeError(f"Download authorization failed: {decision.reason}")
    planned = rows.loc[rows["ticker"].isin(decision.allowed_tickers)].copy()
    if planned.empty:
        raise RuntimeError("Authorized selection is empty")
    acquisition_log = run_root / "acquisition.jsonl"
    performance_log = run_root / "document_performance.jsonl"
    already = completed_urls(acquisition_log)
    client = SecClient(
        user_agent=args.user_agent,
        store=ContentAddressedStore(args.output_root.resolve() / "objects"),
        acquisition_log=acquisition_log,
        telemetry_log=performance_log,
        requests_per_second=args.requests_per_second,
    )
    fetched = 0
    skipped = 0
    failed = 0
    bytes_fetched = 0
    retry_count = 0
    http_429_count = 0
    total = len(planned)
    started = time.monotonic()
    state_lock = threading.Lock()
    state: dict[str, Any] = {
        "status": "RUNNING",
        "stage": "PRIMARY_ACQUISITION",
        "current_index": 0,
        "total_count": total,
        "current_item": "initializing",
        "current_ticker": None,
        "current_accession": None,
        "current_form": None,
        "fetched": 0,
        "skipped_complete": 0,
        "failed": 0,
        "bytes_fetched": 0,
        "documents_per_minute": 0.0,
        "mib_per_minute": 0.0,
        "http_p95_ms": None,
        "retry_count": 0,
        "http_429_count": 0,
        "latest_document_age_seconds": None,
    }
    last_completed_at: float | None = None
    request_latencies: list[float] = []

    def snapshot() -> dict[str, Any]:
        with state_lock:
            value = dict(state)
        if last_completed_at is not None:
            value["latest_document_age_seconds"] = time.monotonic() - last_completed_at
        return value

    telemetry = LiveResourceTelemetry(
        run_root=run_root,
        output_root=args.output_root.resolve(),
        run_id=args.run_id,
        interval_seconds=args.telemetry_interval_seconds,
        state_snapshot=snapshot,
    )
    telemetry.start()
    failure_reason: str | None = None
    try:
        for index, row in enumerate(planned.to_dict("records"), start=1):
            url = str(row["primary_document_url"])
            with state_lock:
                state.update(
                    {
                        "current_index": index,
                        "current_item": f"{row['ticker']}:{row['accession_number']}",
                        "current_ticker": row["ticker"],
                        "current_accession": row["accession_number"],
                        "current_form": row.get("form"),
                    }
                )
            if url in already:
                skipped += 1
                last_completed_at = time.monotonic()
                with state_lock:
                    state["skipped_complete"] = skipped
                telemetry.sample()
                continue
            if (
                shutil.disk_usage(args.output_root.resolve()).free / (1024**3)
                < args.minimum_free_space_gib
            ):
                raise RuntimeError("Free-space gate failed during acquisition")
            filename = Path(urlparse(url).path).name or "primary.bin"
            logical = f"primary/{row['ticker']}/{row['accession_number']}/{filename}"
            result = client.fetch(
                url,
                logical,
                telemetry_context={
                    "ticker": row["ticker"],
                    "accession_number": row["accession_number"],
                    "form": row.get("form"),
                    "selection_index": index,
                },
            )
            fetched += result.status == "FETCHED"
            failed += result.status != "FETCHED"
            bytes_fetched += int(result.bytes or 0)
            latest = client.last_performance or {}
            request_latencies.extend(
                float(value) for value in latest.get("request_attempt_seconds", [])
            )
            retry_count += int(latest.get("retry_count") or 0)
            http_429_count += int(latest.get("http_429_count") or 0)
            last_completed_at = time.monotonic()
            elapsed_minutes = max((last_completed_at - started) / 60.0, 1e-9)
            with state_lock:
                state.update(
                    {
                        "fetched": fetched,
                        "skipped_complete": skipped,
                        "failed": failed,
                        "bytes_fetched": bytes_fetched,
                        "documents_per_minute": (fetched + failed) / elapsed_minutes,
                        "mib_per_minute": (bytes_fetched / (1024**2)) / elapsed_minutes,
                        "http_p95_ms": (
                            percentile(request_latencies, 0.95) * 1000.0
                            if request_latencies
                            else None
                        ),
                        "retry_count": retry_count,
                        "http_429_count": http_429_count,
                    }
                )
            telemetry.sample()
            if result.status != "FETCHED":
                failure_reason = result.error
                break
    except Exception as exc:
        failed += 1
        failure_reason = f"{type(exc).__name__}: {exc}"
    status = "COMPLETE" if failed == 0 and fetched + skipped == total else "FAILED"
    with state_lock:
        state.update({"status": status, "stage": "FINAL", "failed": failed})
    telemetry.stop()
    performance = summarize_document_performance(
        read_jsonl([performance_log]) if performance_log.is_file() else []
    )
    performance.update(
        {
            "run_id": args.run_id,
            "generated_at_utc": utc_now(),
            "resource_peaks": telemetry.peaks,
            "failure_reason": failure_reason,
        }
    )
    atomic_write_json(run_root / "performance_summary.json", performance)
    final = {
        **manifest,
        "status": status,
        "ended_at_utc": utc_now(),
        "authorization_path": args.authorization.resolve().as_posix(),
        "authorization_sha256": file_sha256(args.authorization.resolve()),
        "allowed_tickers": list(decision.allowed_tickers),
        "planned": total,
        "fetched": fetched,
        "skipped_complete": skipped,
        "failed": failed,
        "bytes_fetched": bytes_fetched,
        "retry_count": retry_count,
        "http_429_count": http_429_count,
        "failure_reason": failure_reason,
        "performance_summary_path": (run_root / "performance_summary.json").as_posix(),
        "provisional_bottleneck_candidate": performance["provisional_bottleneck_candidate"],
        "resource_peaks": telemetry.peaks,
    }
    atomic_write_json(run_root / "final_manifest.json", final)
    terminal_heartbeat = {
        **telemetry.last_sample,
        **snapshot(),
        **{
            "run_id": args.run_id,
            "observed_at_utc": utc_now(),
            "elapsed_seconds": time.monotonic() - started,
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": True,
        },
    }
    atomic_write_json(run_root / "heartbeat_latest.json", terminal_heartbeat)
    append_jsonl(run_root / "heartbeat.jsonl", terminal_heartbeat)
    print(json.dumps(final, indent=2))
    return 0 if status == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
