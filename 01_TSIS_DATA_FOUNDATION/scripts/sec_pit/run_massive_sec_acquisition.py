# ruff: noqa: E402
"""Plan or execute the hash-bound, page-resumable Massive SEC acquisition."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.massive_sec_authorization import (
    FrozenTarget,
    validate_authorization,
    validate_config,
    validate_frozen_target,
)
from sec_pit.massive_sec_client import MassiveResponseContractError, MassiveSecClient
from sec_pit.massive_sec_models import (
    ENDPOINT_SPECS,
    EndpointSpec,
    TargetGroup,
    canonical_request_key,
    normalize_cik,
    stable_json_hash,
)
from sec_pit.massive_sec_storage import (
    DuplicateWriterError,
    MassiveSecStorage,
    OutputWriterLock,
    append_jsonl_durable,
    file_sha256,
)
from sec_pit.massive_sec_telemetry import MassiveSecTelemetry, utc_now, write_pid_manifest
from sec_pit.storage import atomic_write_json

TERMINAL_STATUSES = {
    "COMPLETE",
    "FAILED",
    "INTERRUPTED",
    "STOPPED_LOW_DISK",
}


class LowDiskStop(RuntimeError):
    """Clean, resumable hard stop before the output reserve is consumed."""


def _git_value(arguments: list[str], fallback: str = "UNKNOWN") -> str:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=Path(__file__).resolve().parents[3],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return completed.stdout.strip() or fallback
    except (OSError, subprocess.SubprocessError):
        return fallback


def _component_hashes(monitor_path: Path) -> dict[str, str]:
    paths = (
        Path(__file__).resolve(),
        SCRIPT_DIR / "massive_sec_authorization.py",
        SCRIPT_DIR / "massive_sec_client.py",
        SCRIPT_DIR / "massive_sec_models.py",
        SCRIPT_DIR / "massive_sec_storage.py",
        SCRIPT_DIR / "massive_sec_telemetry.py",
        monitor_path,
    )
    return {path.name: file_sha256(path) for path in paths}


def load_target_groups(target: FrozenTarget, *, execution_mode: str) -> tuple[list[TargetGroup], int]:
    frame = pd.read_parquet(
        target.path, columns=["selection_order", "instrument_id", "ticker", "cik"]
    ).sort_values("selection_order", kind="stable")
    frame["ticker"] = frame["ticker"].astype(str).str.strip().str.upper()
    frame["cik"] = frame["cik"].map(normalize_cik)
    if execution_mode == "PROBE":
        frame = frame.head(250).copy()
    groups: list[TargetGroup] = []
    for cik, rows in frame.groupby("cik", sort=False):
        groups.append(
            TargetGroup(
                cik=str(cik),
                tickers=tuple(rows["ticker"].astype(str).tolist()),
                instrument_ids=tuple(rows["instrument_id"].astype(str).tolist()),
            )
        )
    return groups, len(frame)


def build_chain_plan(
    endpoint_ids: tuple[str, ...], target_groups: list[TargetGroup]
) -> list[tuple[EndpointSpec, TargetGroup | None]]:
    plan: list[tuple[EndpointSpec, TargetGroup | None]] = []
    for endpoint_id in endpoint_ids:
        spec = ENDPOINT_SPECS[endpoint_id]
        if spec.query_strategy == "SINGLETON":
            plan.append((spec, None))
        elif spec.query_strategy == "PER_ISSUER_CIK":
            plan.extend((spec, target) for target in target_groups)
        else:
            raise ValueError(
                f"{endpoint_id} requires a separate governed query-plan implementation"
            )
    return plan


def _monitor_command(run_root: Path) -> str:
    monitor = SCRIPT_DIR / "monitor_massive_sec_acquisition.ps1"
    return (
        "powershell -NoProfile -ExecutionPolicy Bypass -File "
        f'"{monitor}" -RunRoot "{run_root}" -Compact -Watch -IntervalSeconds 10'
    )


def _resume_command(args: argparse.Namespace) -> str:
    return (
        f'python "{Path(__file__).resolve()}" --config "{args.config.resolve()}" '
        f'--target-manifest "{args.target_manifest.resolve()}" '
        f'--authorization "{args.authorization.resolve()}" '
        f'--run-id "{args.run_id}" --execution-mode {args.execution_mode} --resume'
    )


def _fresh_command(args: argparse.Namespace) -> str:
    authorization = (
        f' --authorization "{args.authorization.resolve()}"' if args.authorization else ""
    )
    return (
        f'python "{Path(__file__).resolve()}" --config "{args.config.resolve()}" '
        f'--target-manifest "{args.target_manifest.resolve()}"{authorization} '
        f'--run-id "{args.run_id}" --execution-mode {args.execution_mode} --execute'
    )


def _print_header(manifest: dict[str, Any]) -> None:
    fields = {
        "run_id": manifest["run_id"],
        "mode": manifest["mode"],
        "input_root": manifest["target_path"],
        "output_root": manifest["output_root"],
        "pre_manifest": manifest["pre_manifest_path"],
        "heartbeat": manifest["heartbeat_latest_path"],
        "log": manifest["log_path"],
        "pid_manifest": manifest["pid_manifest_path"],
        "monitor": manifest["monitor_command"],
        "success_rule": manifest["success_rule"],
        "resume_policy": manifest["resume_policy"],
    }
    for key, value in fields.items():
        print(f"{key}={value}", flush=True)


def _frozen_manifest(
    *,
    args: argparse.Namespace,
    config: dict[str, Any],
    target: FrozenTarget,
    target_groups: list[TargetGroup],
    target_case_count: int,
    chain_count: int,
    run_root: Path,
    authorization_sha256: str | None,
) -> dict[str, Any]:
    monitor_path = SCRIPT_DIR / "monitor_massive_sec_acquisition.ps1"
    objective_path = Path(str(config["objective_path"])).resolve()
    if not objective_path.is_file():
        raise FileNotFoundError(objective_path)
    manifest = {
        "manifest_version": "massive_sec_pre_manifest_v0_1",
        "run_id": args.run_id,
        "status": "STARTING" if args.execute or args.resume else "PLANNED",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "component_sha256": _component_hashes(monitor_path),
        "command_line": subprocess.list2cmdline(sys.argv),
        "cwd": Path.cwd().resolve().as_posix(),
        "host": socket.gethostname(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER") or "UNKNOWN",
        "parent_pid": os.getppid(),
        "wrapper_pid": os.getpid(),
        "git_branch": _git_value(["branch", "--show-current"]),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_dirty_state": bool(_git_value(["status", "--porcelain"], "")),
        "mode": "RESUME" if args.resume else ("EXECUTE" if args.execute else "PLAN"),
        "execution_mode": args.execution_mode,
        "config_path": args.config.resolve().as_posix(),
        "config_sha256": file_sha256(args.config.resolve()),
        "target_manifest_path": args.target_manifest.resolve().as_posix(),
        "target_manifest_sha256": file_sha256(args.target_manifest.resolve()),
        "target_path": target.path.as_posix(),
        "target_sha256": target.sha256,
        "target_case_count": target_case_count,
        "target_unique_cik_count": len(target_groups),
        "target_group_membership_sha256": stable_json_hash(
            [target_group.to_dict() for target_group in target_groups]
        ),
        "objective_path": objective_path.as_posix(),
        "objective_sha256": file_sha256(objective_path),
        "authorization_path": (
            args.authorization.resolve().as_posix() if args.authorization else None
        ),
        "authorization_sha256": authorization_sha256,
        "endpoint_ids": list(config["endpoint_ids"]),
        "endpoint_specs_sha256": stable_json_hash(
            {
                endpoint_id: ENDPOINT_SPECS[endpoint_id].__dict__
                for endpoint_id in config["endpoint_ids"]
            }
        ),
        "planned_chain_count": chain_count,
        "http_workers": int(config["http_workers"]),
        "maximum_http_workers_after_probe": int(
            config["maximum_http_workers_after_probe"]
        ),
        "requests_per_second": float(config["requests_per_second"]),
        "rate_limit_semantics": (
            "ENGINEERING_CEILING_NOT_VENDOR_LIMIT; adaptive decrease on HTTP 429"
        ),
        "output_root": Path(str(config["output_root"])).resolve().as_posix(),
        "control_runtime_root": Path(str(config["control_runtime_root"])).resolve().as_posix(),
        "run_root": run_root.as_posix(),
        "pre_manifest_path": (run_root / "pre_manifest.json").as_posix(),
        "pid_manifest_path": (run_root / "pid_manifest.json").as_posix(),
        "heartbeat_latest_path": (run_root / "heartbeat_latest.json").as_posix(),
        "heartbeat_history_path": (run_root / "heartbeat.jsonl").as_posix(),
        "log_path": (run_root / "acquisition.log").as_posix(),
        "minimum_free_space_gib": float(config["minimum_free_space_gib"]),
        "resume_policy": (
            "same run_id + --resume; validate frozen hashes; follow COMMITTED receipts; "
            "redownload only an uncommitted in-flight page"
        ),
        "overwrite_policy": (
            "raw CAS is immutable; normalized work_id collision must be byte-identical; "
            "no in-place dataset overwrite"
        ),
        "success_rule": (
            "all planned pagination chains terminal, zero hard failures, every fetched page "
            "has raw CAS + normalized shard + COMMITTED receipt, rebuilt ledgers pass audit"
        ),
        "monitor_command": _monitor_command(run_root),
        "safe_stop": "Ctrl+C; committed pages remain durable; then use exact resume command",
        "resume_command": _resume_command(args) if args.authorization else None,
        "network_access": "AUTHORIZED" if args.execute or args.resume else "NONE",
    }
    return manifest


def _assert_resume_compatible(existing: dict[str, Any], current: dict[str, Any]) -> None:
    fields = (
        "config_sha256",
        "target_manifest_sha256",
        "target_sha256",
        "target_group_membership_sha256",
        "objective_sha256",
        "authorization_sha256",
        "endpoint_specs_sha256",
        "execution_mode",
        "output_root",
    )
    drift = [field for field in fields if existing.get(field) != current.get(field)]
    if existing.get("component_sha256") != current.get("component_sha256"):
        drift.append("component_sha256")
    if drift:
        raise RuntimeError(f"resume hash/scope drift: {sorted(set(drift))}")


def _write_control_pointer(config: dict[str, Any], manifest: dict[str, Any]) -> None:
    root = Path(str(config["control_runtime_root"])).resolve() / str(manifest["run_id"])
    root.mkdir(parents=True, exist_ok=True)
    atomic_write_json(
        root / "run_pointer.json",
        {
            "run_id": manifest["run_id"],
            "status": manifest["status"],
            "durable_run_root": manifest["run_root"],
            "pre_manifest_path": manifest["pre_manifest_path"],
            "monitor_command": manifest["monitor_command"],
            "created_at_utc": manifest["created_at_utc"],
        },
    )


def _write_error_parquet(run_root: Path) -> dict[str, Any]:
    path = run_root / "error_ledger.jsonl"
    rows: list[dict[str, Any]] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    columns = ("observed_at_utc", "endpoint_id", "target_cik", "error_type", "error")
    parquet = run_root / "error_ledger.parquet"
    frame = pd.DataFrame(rows, columns=columns)
    temp = parquet.with_name(f".{parquet.name}.{os.getpid()}.tmp")
    try:
        frame.to_parquet(temp, index=False)
        with temp.open("r+b") as handle:
            os.fsync(handle.fileno())
        os.replace(temp, parquet)
    finally:
        temp.unlink(missing_ok=True)
    return {
        "error_count": len(rows),
        "error_ledger_jsonl": path.as_posix(),
        "error_ledger_parquet": parquet.as_posix(),
        "error_ledger_parquet_sha256": file_sha256(parquet),
    }


def _plan_only(
    args: argparse.Namespace,
    config: dict[str, Any],
    target: FrozenTarget,
    target_groups: list[TargetGroup],
    target_case_count: int,
    chain_count: int,
) -> int:
    output_root = Path(str(config["output_root"])).resolve()
    run_root = (
        Path(str(config["control_runtime_root"])).resolve()
        / args.run_id
        / "plan_only"
    )
    run_root.mkdir(parents=True, exist_ok=True)
    manifest = _frozen_manifest(
        args=args,
        config=config,
        target=target,
        target_groups=target_groups,
        target_case_count=target_case_count,
        chain_count=chain_count,
        run_root=run_root,
        authorization_sha256=(
            file_sha256(args.authorization.resolve()) if args.authorization else None
        ),
    )
    manifest.update(
        {
            "status": "COMPLETE",
            "result": "PLAN_ONLY_NO_NETWORK_NO_D_DRIVE_WRITE",
            "output_root_exists": output_root.exists(),
            "output_free_gib": (
                shutil.disk_usage(output_root).free / (1024**3) if output_root.exists() else None
            ),
            "exact_execute_command": _fresh_command(args),
            "ended_at_utc": utc_now(),
        }
    )
    atomic_write_json(run_root / "pre_manifest.json", manifest)
    atomic_write_json(run_root / "final_manifest.json", manifest)
    _print_header(manifest)
    print(json.dumps(manifest, indent=2), flush=True)
    return 0


def execute(args: argparse.Namespace) -> int:
    config = validate_config(args.config.resolve())
    governed_target_manifest = Path(str(config["target_manifest_path"])).resolve()
    if governed_target_manifest != args.target_manifest.resolve():
        raise ValueError("--target-manifest drifts from the governed config")
    target = validate_frozen_target(args.target_manifest.resolve())
    target_groups, target_case_count = load_target_groups(
        target, execution_mode=args.execution_mode
    )
    objective_path = Path(str(config["objective_path"])).resolve()
    component_bundle_sha256 = stable_json_hash(
        _component_hashes(SCRIPT_DIR / "monitor_massive_sec_acquisition.ps1")
    )
    endpoint_ids = tuple(config["endpoint_ids"])
    chain_plan = build_chain_plan(endpoint_ids, target_groups)
    if not (args.execute or args.resume):
        return _plan_only(
            args,
            config,
            target,
            target_groups,
            target_case_count,
            len(chain_plan),
        )

    if not args.authorization:
        raise ValueError("--authorization is required for network execution")
    decision = validate_authorization(
        args.authorization.resolve(),
        config_path=args.config.resolve(),
        target_manifest_path=args.target_manifest.resolve(),
        objective_path=objective_path,
        component_bundle_sha256=component_bundle_sha256,
        target=target,
        requested_endpoint_ids=endpoint_ids,
        execution_mode=args.execution_mode,
        requested_target_case_count=target_case_count,
        requested_unique_cik_count=len(target_groups),
    )
    if decision.gate != "PASS":
        raise RuntimeError(f"Massive SEC authorization failed: {decision.reason}")
    api_key = os.environ.get("MASSIVE_API_KEY")
    if not api_key:
        raise ValueError("MASSIVE_API_KEY environment variable is required")

    output_root = Path(str(config["output_root"])).resolve()
    if not output_root.is_dir():
        raise FileNotFoundError(f"governed output root does not exist: {output_root}")
    minimum_free = float(config["minimum_free_space_gib"])
    free_gib = shutil.disk_usage(output_root).free / (1024**3)
    if free_gib < minimum_free:
        raise LowDiskStop(f"output free space {free_gib:.2f} < {minimum_free:.2f} GiB")

    storage = MassiveSecStorage(output_root, args.run_id)
    run_root = storage.run_root
    if run_root.exists() and not args.resume:
        raise FileExistsError(f"run exists; use --resume with exact frozen inputs: {run_root}")
    if args.resume and not run_root.is_dir():
        raise FileNotFoundError(f"resume run root does not exist: {run_root}")

    writer_lock = OutputWriterLock(output_root, args.run_id)
    writer_lock.acquire(allow_stale_takeover=args.resume)
    telemetry: MassiveSecTelemetry | None = None
    final_status = "FAILED"
    exit_code = 1
    failure_reason: str | None = None
    try:
        storage.prepare_topology(
            ENDPOINT_SPECS[endpoint_id].dataset_directory for endpoint_id in endpoint_ids
        )
        manifest = _frozen_manifest(
            args=args,
            config=config,
            target=target,
            target_groups=target_groups,
            target_case_count=target_case_count,
            chain_count=len(chain_plan),
            run_root=run_root,
            authorization_sha256=file_sha256(args.authorization.resolve()),
        )
        pre_manifest_path = run_root / "pre_manifest.json"
        if args.resume:
            existing = json.loads(pre_manifest_path.read_text(encoding="utf-8-sig"))
            _assert_resume_compatible(existing, manifest)
            manifest = {**existing, "status": "RUNNING", "resumed_at_utc": utc_now()}
        else:
            atomic_write_json(pre_manifest_path, manifest)
        _write_control_pointer(config, manifest)
        write_pid_manifest(
            run_root, run_id=args.run_id, expected_alive=True, stage="MASSIVE_SEC_ACQUISITION"
        )
        _print_header(manifest)

        state_lock = threading.Lock()
        stop_event = threading.Event()
        observed_fields: dict[str, set[str]] = defaultdict(set)
        state: dict[str, Any] = {
            "status": "RUNNING",
            "stage": "MASSIVE_SEC_ACQUISITION",
            "current_index": 0,
            "total_count": len(chain_plan),
            "current_item": "initializing",
            "chains_completed": 0,
            "chains_failed": 0,
            "pages_committed": 0,
            "pages_resumed": 0,
            "rows_committed": 0,
            "bytes_fetched": 0,
            "retry_count": 0,
            "http_429_count": 0,
            "active_http_workers": 0,
            "configured_http_workers": int(config["http_workers"]),
            "current_requests_per_second": float(config["requests_per_second"]),
        }

        def snapshot() -> dict[str, Any]:
            with state_lock:
                return dict(state)

        telemetry = MassiveSecTelemetry(
            run_root=run_root,
            output_root=output_root,
            run_id=args.run_id,
            interval_seconds=float(config["telemetry_interval_seconds"]),
            state_snapshot=snapshot,
        )
        telemetry.log_event(
            "run_started",
            mode=manifest["mode"],
            chains=len(chain_plan),
            workers=config["http_workers"],
            rps=config["requests_per_second"],
        )
        telemetry.start()
        client = MassiveSecClient(
            api_key=api_key,
            base_url=str(config["base_url"]),
            requests_per_second=float(config["requests_per_second"]),
            timeout_seconds=float(config["timeout_seconds"]),
            max_attempts=int(config["max_attempts"]),
        )
        max_pages = int(config["maximum_pages_per_chain"])

        def process_chain(spec: EndpointSpec, target_group: TargetGroup | None) -> dict[str, Any]:
            target_cik = target_group.cik if target_group else None
            url = client.build_initial_url(spec, cik=target_cik)
            seen_urls: set[str] = set()
            pages = rows = committed = resumed = 0
            with state_lock:
                state["active_http_workers"] += 1
                state["current_item"] = f"{spec.endpoint_id}:{target_cik or 'singleton'}"
            try:
                while url:
                    if stop_event.is_set():
                        raise RuntimeError("chain stopped after peer failure")
                    if url in seen_urls:
                        raise MassiveResponseContractError(
                            f"pagination loop for {spec.endpoint_id}:{target_cik}"
                        )
                    seen_urls.add(url)
                    pages += 1
                    if pages > max_pages:
                        raise MassiveResponseContractError(
                            f"maximum pages exceeded for {spec.endpoint_id}:{target_cik}"
                        )
                    work_id = canonical_request_key(spec.endpoint_id, url)
                    receipt = storage.load_receipt(spec.endpoint_id, work_id)
                    if receipt is not None:
                        resumed += 1
                        rows += int(receipt["result_count"])
                        url = receipt.get("next_url")
                        with state_lock:
                            state["pages_resumed"] += 1
                            state["rows_committed"] += int(receipt["result_count"])
                        continue
                    if shutil.disk_usage(output_root).free / (1024**3) < minimum_free:
                        raise LowDiskStop("free-space reserve reached before request")
                    page = client.fetch_page(spec=spec, url=url, target_cik=target_cik)
                    commit = storage.commit_page(
                        endpoint_id=spec.endpoint_id,
                        dataset_directory=spec.dataset_directory,
                        work_id=work_id,
                        target_cik=target_cik,
                        sanitized_url=page.sanitized_url,
                        request_id=page.request_id,
                        retrieved_at_utc=page.retrieved_at_utc,
                        response_bytes=page.response_bytes,
                        results=page.results,
                        next_url=page.next_url,
                        http_status=page.http_status,
                        attempts=page.attempts,
                        retry_count=page.retry_count,
                        http_429_count=page.http_429_count,
                        elapsed_seconds=page.elapsed_seconds,
                        observed_fields=page.observed_fields,
                    )
                    committed += 1
                    rows += commit.result_count
                    with state_lock:
                        observed_fields[spec.endpoint_id].update(page.observed_fields)
                        state["pages_committed"] += 1
                        state["rows_committed"] += commit.result_count
                        state["bytes_fetched"] += commit.raw_bytes
                        state["retry_count"] += commit.retry_count
                        state["http_429_count"] += commit.http_429_count
                        state["current_requests_per_second"] = (
                            client.rate_limiter.current_requests_per_second
                        )
                    telemetry.log_event(
                        "page_committed",
                        endpoint=spec.endpoint_id,
                        cik=target_cik,
                        work_id=work_id,
                        rows=commit.result_count,
                        raw_bytes=commit.raw_bytes,
                        request_id=commit.request_id,
                    )
                    url = page.next_url
                return {
                    "endpoint_id": spec.endpoint_id,
                    "target_cik": target_cik,
                    "pages": pages,
                    "pages_committed": committed,
                    "pages_resumed": resumed,
                    "rows": rows,
                }
            finally:
                with state_lock:
                    state["active_http_workers"] -= 1

        chain_results: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        interrupted = False
        try:
            with ThreadPoolExecutor(
                max_workers=int(config["http_workers"]),
                thread_name_prefix="massive-sec-http",
            ) as executor:
                futures = {
                    executor.submit(process_chain, spec, target_group): (spec, target_group)
                    for spec, target_group in chain_plan
                }
                try:
                    for index, future in enumerate(as_completed(futures), start=1):
                        spec, target_group = futures[future]
                        try:
                            result = future.result()
                            chain_results.append(result)
                            with state_lock:
                                state["current_index"] = index
                                state["chains_completed"] += 1
                        except Exception as exc:
                            stop_event.set()
                            error = {
                                "observed_at_utc": utc_now(),
                                "endpoint_id": spec.endpoint_id,
                                "target_cik": target_group.cik if target_group else None,
                                "error_type": type(exc).__name__,
                                "error": str(exc),
                            }
                            errors.append(error)
                            append_jsonl_durable(run_root / "error_ledger.jsonl", error)
                            with state_lock:
                                state["current_index"] = index
                                state["chains_failed"] += 1
                            for pending in futures:
                                if not pending.done():
                                    pending.cancel()
                            break
                except KeyboardInterrupt:
                    interrupted = True
                    stop_event.set()
                    for pending in futures:
                        if not pending.done():
                            pending.cancel()
        except KeyboardInterrupt:
            interrupted = True
            stop_event.set()

        if interrupted:
            final_status = "INTERRUPTED"
            failure_reason = "KeyboardInterrupt: safe stop requested by operator"
            exit_code = 130
        else:
            if errors:
                if any(error["error_type"] == "LowDiskStop" for error in errors):
                    final_status = "STOPPED_LOW_DISK"
                    exit_code = 2
                else:
                    final_status = "FAILED"
                    exit_code = 1
                failure_reason = errors[0]["error"]
            elif len(chain_results) == len(chain_plan):
                final_status = "COMPLETE"
                exit_code = 0
            else:
                final_status = "FAILED"
                exit_code = 1
                failure_reason = "not all planned chains reached a terminal success"

        with state_lock:
            state.update({"status": final_status, "stage": "FINALIZING"})
        telemetry.stop()
        ledger_summary = storage.rebuild_request_ledgers()
        error_summary = _write_error_parquet(run_root)
        endpoint_summary = {
            "run_id": args.run_id,
            "generated_at_utc": utc_now(),
            "status": final_status,
            "endpoints": {},
        }
        for endpoint_id in endpoint_ids:
            endpoint_rows = [
                row for row in storage.iter_receipts() if row["endpoint_id"] == endpoint_id
            ]
            for row in endpoint_rows:
                observed_fields[endpoint_id].update(row.get("observed_fields") or ())
            endpoint_summary["endpoints"][endpoint_id] = {
                "committed_pages": len(endpoint_rows),
                "rows": sum(int(row["result_count"]) for row in endpoint_rows),
                "raw_bytes": sum(int(row["raw_bytes"]) for row in endpoint_rows),
                "observed_fields": sorted(observed_fields[endpoint_id]),
                "schema_status": "PROVISIONAL_PENDING_VERSIONED_SAMPLE_AUDIT",
            }
        atomic_write_json(run_root / "endpoint_summary.json", endpoint_summary)
        final = {
            **manifest,
            "status": final_status,
            "ended_at_utc": utc_now(),
            "exit_code": exit_code,
            "failure_reason": failure_reason,
            "chains_planned": len(chain_plan),
            "chains_completed_this_process": len(chain_results),
            "runtime_counters": snapshot(),
            "ledger_summary": ledger_summary,
            "error_summary": error_summary,
            "endpoint_summary_path": (run_root / "endpoint_summary.json").as_posix(),
            "resource_peaks": telemetry.peaks,
            "resume_instructions": manifest["resume_command"],
            "promotion_state": "RAW_VENDOR_EVIDENCE_NOT_INSTITUTIONAL",
        }
        atomic_write_json(run_root / "final_manifest.json", final)
        with state_lock:
            state.update({"status": final_status, "stage": "FINAL"})
        terminal = {
            **telemetry.last_sample,
            **snapshot(),
            "run_id": args.run_id,
            "observed_at_utc": utc_now(),
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": True,
            "expected_alive": False,
        }
        atomic_write_json(run_root / "heartbeat_latest.json", terminal)
        append_jsonl_durable(run_root / "heartbeat.jsonl", terminal)
        write_pid_manifest(
            run_root, run_id=args.run_id, expected_alive=False, stage=final_status
        )
        telemetry.log_event(
            "run_terminal", status=final_status, exit_code=exit_code, errors=len(errors)
        )
        print(json.dumps(final, indent=2), flush=True)
        return exit_code
    except DuplicateWriterError:
        raise
    except Exception as exc:
        failure_reason = f"{type(exc).__name__}: {exc}"
        if run_root.is_dir():
            atomic_write_json(
                run_root / "final_manifest.json",
                {
                    "run_id": args.run_id,
                    "status": "FAILED",
                    "ended_at_utc": utc_now(),
                    "exit_code": 1,
                    "failure_reason": failure_reason,
                    "resume_instructions": (
                        _resume_command(args) if args.authorization else None
                    ),
                },
            )
        raise
    finally:
        if telemetry is not None and telemetry.last_sample.get("status") == "RUNNING":
            try:
                telemetry.stop()
            except Exception:
                pass
        writer_lock.release()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--execution-mode", choices=("PROBE", "FULL"), default="FULL")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> int:
    return execute(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
