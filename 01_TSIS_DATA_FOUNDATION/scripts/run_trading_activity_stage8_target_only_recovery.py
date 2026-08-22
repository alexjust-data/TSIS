"""Inventory and certify frozen Stage-8 TARGET partitions without recomputation."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

import psutil
import pyarrow as pa
import pyarrow.parquet as pq

import trading_activity_stage8_target_only_contract as contract

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
MONITOR_PATH = SCRIPT_DIR / "monitor_trading_activity_stage8_target_only_recovery.ps1"
EXPECTED_PLAN_SCHEMA = "trading_activity_stage8_target_only_recovery_plan_v0_2"
HASH_CHUNK_BYTES = 8 * 1024 * 1024


def utc_text() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp"
    )
    temporary.write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    error: OSError | None = None
    for attempt in range(8):
        try:
            os.replace(temporary, path)
            return
        except PermissionError as exc:
            error = exc
            time.sleep(0.025 * (attempt + 1))
    temporary.unlink(missing_ok=True)
    if error is not None:
        raise error


def append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(payload), default=str) + "\n")
        handle.flush()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_path(path: str | Path) -> str:
    return os.path.normcase(os.path.abspath(os.fspath(path)))


def git_value(*args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=SCRIPT_DIR.parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    value = result.stdout.strip()
    return value or None


def schema_descriptor(schema: pa.Schema) -> list[dict[str, str]]:
    return [{"name": field.name, "type": str(field.type)} for field in schema]


def schema_sha256(schema: pa.Schema) -> str:
    encoded = json.dumps(schema_descriptor(schema), separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def load_plan(path: Path) -> dict[str, Any]:
    plan = read_json(path)
    if plan.get("plan_schema_version") != EXPECTED_PLAN_SCHEMA:
        raise ValueError("Unsupported target-only recovery plan schema")
    mode = plan.get("mode")
    if mode not in {"PROBE", "FULL"}:
        raise ValueError(f"Unsupported mode: {mode}")
    if mode == "PROBE":
        if plan.get("artifact_status") != "PREREGISTERED_PROBE_AUTHORIZED":
            raise ValueError("Probe plan is not preregistered and authorized")
    else:
        if plan.get("artifact_status") != "PREREGISTERED_HUMAN_AUTHORIZED":
            raise ValueError("Full recovery is not human-authorized")
        if not str(plan.get("human_authorization", "")).startswith("AUTHORIZED_"):
            raise ValueError("Explicit full-recovery human authorization is missing")
    if plan.get("source_blocks_recomputed") != 0:
        raise ValueError("Target-only recovery must never recompute source blocks")
    if plan.get("canonical_promotion_authorized") is not False:
        raise ValueError("Canonical promotion must remain false")
    shards = plan.get("source_shards", [])
    indices = sorted(int(item["shard_index"]) for item in shards)
    if indices != [0, 1, 2, 3]:
        raise ValueError("Source shards must be exactly 0,1,2,3")
    if sum(int(item["expected_block_count"]) for item in shards) != 240:
        raise ValueError("Source shards must cover exactly 240 blocks")
    controls = plan.get("inherited_incident_controls", [])
    if {item.get("control_id") for item in controls} != {
        "RM-MAT-CTRL-001",
        "RM-MAT-CTRL-002",
        "RM-MAT-CTRL-003",
        "RM-MAT-CTRL-004",
        "RM-MAT-CTRL-005",
    }:
        raise ValueError("The exact inherited control set 001..005 is required")
    return plan


def selected_run_root(plan: Mapping[str, Any], probe_shard: int | None) -> Path:
    if plan["mode"] == "PROBE":
        if probe_shard not in {0, 1, 2, 3}:
            raise ValueError("PROBE mode requires --probe-shard 0,1,2 or 3")
        return Path(plan["probe_run_roots"][str(probe_shard)]).resolve()
    if probe_shard is not None:
        raise ValueError("--probe-shard is prohibited for FULL mode")
    return Path(plan["run_root"]).resolve()


def verify_static_hashes(plan: Mapping[str, Any], plan_path: Path) -> None:
    expected = {
        SCRIPT_PATH: plan["runner_sha256"],
        Path(contract.__file__).resolve(): plan["contract_sha256"],
        MONITOR_PATH.resolve(): plan["monitor_sha256"],
        Path(plan["target_table"]).resolve(): plan["target_table_sha256"],
        Path(plan["sample_manifest"]).resolve(): plan["sample_manifest_sha256"],
    }
    for path, digest in expected.items():
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = sha256_file(path)
        if actual != digest:
            raise ValueError(f"Frozen hash mismatch: {path} {actual} != {digest}")
    if not plan_path.is_file():
        raise FileNotFoundError(plan_path)


def active_duplicate(run_root: Path) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    needle = normalized_path(run_root)
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        if process.pid == os.getpid():
            continue
        try:
            command = " ".join(process.info.get("cmdline") or [])
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
        if SCRIPT_PATH.name in command and needle in normalized_path(command):
            matches.append(
                {
                    "pid": process.pid,
                    "name": process.info.get("name"),
                    "command": command,
                }
            )
    return matches


def load_block_map(plan: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    source_runtime = Path(plan["source_runtime_root"]).resolve()
    expected_engine = plan["expected_stage8_engine_fingerprint"]
    block_map: dict[str, dict[str, Any]] = {}
    for shard in plan["source_shards"]:
        parent_path = source_runtime / str(shard["run_id"]) / "final_manifest.json"
        parent = read_json(parent_path)
        completed = parent.get("completed_blocks", [])
        if parent.get("final_status") != "COMPLETE":
            raise AssertionError(f"Source parent is not COMPLETE: {parent_path}")
        if len(completed) != int(shard["expected_block_count"]):
            raise AssertionError(f"Unexpected source block count: {parent_path}")
        for item in completed:
            block_id = str(item["block_id"])
            if block_id in block_map:
                raise AssertionError(f"Duplicate block_id across shards: {block_id}")
            block_run_id = str(item["block_run_id"])
            block_final_path = (
                parent_path.parent / "blocks" / block_run_id / "final_manifest.json"
            )
            block_final = read_json(block_final_path)
            engine = block_final.get("stage8_engine", {})
            if block_final.get("status") != "COMPLETE":
                raise AssertionError(f"Source block is not COMPLETE: {block_final_path}")
            if engine.get("engine_fingerprint_sha256") != expected_engine:
                raise AssertionError(f"Source block engine mismatch: {block_final_path}")
            output_root = Path(block_final["output_run_root"]).resolve()
            if not normalized_path(output_root).startswith(
                normalized_path(Path(plan["source_output_root"]).resolve())
            ):
                raise AssertionError(f"Block output escapes source root: {output_root}")
            block_map[block_id] = {
                "block_id": block_id,
                "block_run_id": block_run_id,
                "shard_index": int(shard["shard_index"]),
                "output_root": output_root,
                "block_final_path": block_final_path,
                "block_final_sha256": sha256_file(block_final_path),
            }
    if len(block_map) != 240:
        raise AssertionError(f"Expected 240 exact blocks, got {len(block_map)}")
    return block_map


def load_target_rows(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    table = pq.read_table(Path(plan["target_table"]).resolve())
    required = {
        "block_id",
        "target_ordinal",
        "instrument_id",
        "ticker_as_of_session",
        "session_date",
        "decision_seconds",
        "session_minutes",
        "is_early_close",
    }
    missing = sorted(required - set(table.column_names))
    if missing:
        raise ValueError(f"Target table missing columns: {missing}")
    rows = table.select(sorted(required)).to_pylist()
    full_contract = contract.aggregate_contract(rows)
    if full_contract != plan["full_scope_contract"]:
        raise AssertionError("Full frozen target contract differs from the plan")
    if len(rows) != 2400:
        raise AssertionError(f"Expected exactly 2,400 target rows, got {len(rows)}")
    return rows


def select_rows(
    plan: Mapping[str, Any],
    rows: list[dict[str, Any]],
    block_map: Mapping[str, Mapping[str, Any]],
    probe_shard: int | None,
) -> list[dict[str, Any]]:
    for row in rows:
        if str(row["block_id"]) not in block_map:
            raise AssertionError(f"Target references unknown block: {row['block_id']}")
    if plan["mode"] == "FULL":
        selected = rows
        expected = plan["full_scope_contract"]
    else:
        wanted = {
            contract.exact_target_key(item)
            for item in plan["probe_target_keys_by_shard"][str(probe_shard)]
        }
        selected = [row for row in rows if contract.exact_target_key(row) in wanted]
        if {contract.exact_target_key(row) for row in selected} != wanted:
            raise AssertionError("Probe exact-target selection is incomplete")
        for row in selected:
            if int(block_map[str(row["block_id"])]["shard_index"]) != probe_shard:
                raise AssertionError("Probe target does not belong to requested shard")
        expected = plan["probe_scope_contracts"][str(probe_shard)]
    actual = contract.aggregate_contract(selected)
    if actual != expected:
        raise AssertionError(f"Selected target contract differs: {actual} != {expected}")
    return selected


def _validation_evidence(output_root: Path) -> dict[str, Any]:
    validation_root = output_root / "validation"
    names = (
        "grain_uniqueness_validation.json",
        "temporal_legality_validation.json",
        "baseline_reference_validation.json",
    )
    result: dict[str, Any] = {}
    for name in names:
        path = validation_root / name
        payload = read_json(path)
        if payload.get("status") != "PASS":
            raise AssertionError(f"Inherited block validator is not PASS: {path}")
        result[name] = {"path": str(path), "sha256": sha256_file(path)}
    lineage_path = output_root / "metadata" / "lineage_manifest.json"
    lineage = read_json(lineage_path)
    if lineage.get("future_window_used") is not False:
        raise AssertionError(f"future_window_used is not false: {lineage_path}")
    result["lineage_manifest.json"] = {
        "path": str(lineage_path),
        "sha256": sha256_file(lineage_path),
    }
    return result


def build_inventory(
    selected: list[dict[str, Any]],
    block_map: Mapping[str, Mapping[str, Any]],
    expected_engine: str,
) -> list[dict[str, Any]]:
    index_cache: dict[str, dict[str, dict[str, Any]]] = {}
    evidence_cache: dict[str, dict[str, Any]] = {}
    inventory: list[dict[str, Any]] = []
    for target in selected:
        block = block_map[str(target["block_id"])]
        block_run_id = str(block["block_run_id"])
        output_root = Path(block["output_root"])
        if block_run_id not in index_cache:
            index_path = output_root / "validation" / "output_hashes.parquet"
            sidecar_path = index_path.with_name(index_path.name + ".sha256")
            recorded_index_hash = sidecar_path.read_text(encoding="utf-8").strip()
            actual_index_hash = sha256_file(index_path)
            if actual_index_hash != recorded_index_hash:
                raise AssertionError(f"Hash-index sidecar mismatch: {index_path}")
            rows = pq.ParquetFile(index_path).read().to_pylist()
            index_cache[block_run_id] = {
                normalized_path(item["path"]): item for item in rows
            }
            if len(index_cache[block_run_id]) != len(rows):
                raise AssertionError(f"Duplicate paths in hash index: {index_path}")
            evidence_cache[block_run_id] = _validation_evidence(output_root)
        expected_counts = contract.expected_physical_counts(target)
        session_date = contract.normalized_session_date(target["session_date"])
        ticker = str(target["ticker_as_of_session"])
        for family in contract.PHYSICAL_FAMILY_KEYS:
            source_path = (
                output_root
                / family
                / f"ticker={ticker}"
                / f"session_date={session_date}"
                / "part-00000.parquet"
            ).resolve()
            record = index_cache[block_run_id].get(normalized_path(source_path))
            if record is None:
                raise FileNotFoundError(
                    f"Exact target partition missing from hash index: {source_path}"
                )
            if int(record["rows"]) != int(expected_counts[family]):
                raise AssertionError(
                    f"Indexed row count differs for {source_path}: "
                    f"{record['rows']} != {expected_counts[family]}"
                )
            sidecar_path = source_path.with_name(source_path.name + ".sha256")
            sidecar_hash = sidecar_path.read_text(encoding="utf-8").strip()
            if sidecar_hash != record["sha256"]:
                raise AssertionError(f"Partition sidecar differs from index: {source_path}")
            inventory.append(
                {
                    "block_id": str(target["block_id"]),
                    "block_run_id": block_run_id,
                    "shard_index": int(block["shard_index"]),
                    "target_ordinal": int(target["target_ordinal"]),
                    "instrument_id": str(target["instrument_id"]),
                    "ticker": ticker,
                    "session_date": session_date,
                    "is_early_close": bool(target["is_early_close"]),
                    "decision_points": contract.decision_points(target),
                    "family": family,
                    "source_path": str(source_path),
                    "source_bytes": int(record["bytes"]),
                    "recorded_source_sha256": str(record["sha256"]),
                    "recorded_rows": int(record["rows"]),
                    "expected_rows": int(expected_counts[family]),
                    "source_engine_fingerprint": expected_engine,
                    "block_final_manifest": str(block["block_final_path"]),
                    "block_final_sha256": str(block["block_final_sha256"]),
                    "validation_evidence_json": json.dumps(
                        evidence_cache[block_run_id], sort_keys=True
                    ),
                }
            )
    expected_partitions = len(selected) * len(contract.PHYSICAL_FAMILY_KEYS)
    if len(inventory) != expected_partitions:
        raise AssertionError(
            f"Expected {expected_partitions} inventory rows, got {len(inventory)}"
        )
    exact_pairs = {
        (
            item["block_id"],
            item["instrument_id"],
            item["ticker"],
            item["session_date"],
            item["family"],
        )
        for item in inventory
    }
    if len(exact_pairs) != len(inventory):
        raise AssertionError("Duplicate target/family inventory rows")
    return inventory


def _column_statistics_match(
    parquet_file: pq.ParquetFile, column: str, expected: Any
) -> bool:
    schema_names = parquet_file.schema_arrow.names
    if column not in schema_names:
        return False
    index = schema_names.index(column)
    expected_text = str(expected)
    for row_group in range(parquet_file.metadata.num_row_groups):
        stats = parquet_file.metadata.row_group(row_group).column(index).statistics
        if stats is None or not stats.has_min_max:
            return False
        minimum = stats.min
        maximum = stats.max
        if isinstance(minimum, bytes):
            minimum = minimum.decode("utf-8")
        if isinstance(maximum, bytes):
            maximum = maximum.decode("utf-8")
        if isinstance(minimum, (date, datetime)):
            minimum = minimum.isoformat()[:10]
        if isinstance(maximum, (date, datetime)):
            maximum = maximum.isoformat()[:10]
        if str(minimum) != expected_text or str(maximum) != expected_text:
            return False
    return True


def verify_partition(item: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(item["source_path"])
    stat = path.stat()
    if stat.st_size != int(item["source_bytes"]):
        raise AssertionError(f"File size mismatch: {path}")
    actual_hash = sha256_file(path)
    if actual_hash != item["recorded_source_sha256"]:
        raise AssertionError(f"SHA-256 mismatch: {path}")
    parquet_file = pq.ParquetFile(path)
    if parquet_file.metadata.num_rows != int(item["expected_rows"]):
        raise AssertionError(f"Parquet footer row mismatch: {path}")
    schema = parquet_file.schema_arrow
    missing = sorted(set(contract.required_columns(str(item["family"]))) - set(schema.names))
    if missing:
        raise AssertionError(f"Required columns missing from {path}: {missing}")
    identity_checks = {
        "instrument_id": item["instrument_id"],
        "ticker": item["ticker"],
        "session_date": item["session_date"],
    }
    for column, expected in identity_checks.items():
        if not _column_statistics_match(parquet_file, column, expected):
            raise AssertionError(
                f"Parquet statistics do not prove exact {column}={expected}: {path}"
            )
    sample_columns = [
        column
        for column in (
            "instrument_id",
            "ticker",
            "session_date",
            "decision_timestamp",
            "future_window_used",
            "coverage_state",
            "calculation_state",
        )
        if column in schema.names
    ]
    sample = parquet_file.read(columns=sample_columns).slice(0, 3).to_pylist()
    if any(row.get("future_window_used") is not False for row in sample):
        raise AssertionError(f"Sample future_window_used is not false: {path}")
    return {
        "status": "PASS",
        "source_path": str(path),
        "actual_sha256": actual_hash,
        "actual_bytes": stat.st_size,
        "actual_rows": parquet_file.metadata.num_rows,
        "schema_sha256": schema_sha256(schema),
        "schema_descriptor": schema_descriptor(schema),
        "sample_values": sample,
        "verified_at_utc": utc_text(),
    }


def load_resume_results(path: Path) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return results
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("status") == "PASS" and item.get("source_path"):
                results[normalized_path(item["source_path"])] = item
    return results


def write_parquet(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    data = [dict(item) for item in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    pq.write_table(pa.Table.from_pylist(data), temporary, compression="zstd")
    os.replace(temporary, path)


def execute(plan_path: Path, probe_shard: int | None, resume: bool) -> int:
    plan_path = plan_path.resolve()
    plan = load_plan(plan_path)
    run_root = selected_run_root(plan, probe_shard)
    runtime_root = run_root / "runtime"
    artifacts_root = run_root / "artifacts"
    pre_path = runtime_root / "pre_manifest.json"
    pid_path = runtime_root / "pid_manifest.json"
    heartbeat_path = runtime_root / "heartbeat_latest.json"
    heartbeat_history = runtime_root / "heartbeat_history.jsonl"
    log_path = runtime_root / "run.log"
    final_path = runtime_root / "final_manifest.json"
    inventory_path = artifacts_root / "target_partition_inventory.parquet"
    inventory_summary_path = artifacts_root / "target_partition_inventory_summary.json"
    verification_path = artifacts_root / "partition_verification.jsonl"
    reference_manifest_path = artifacts_root / "verified_reference_manifest.parquet"
    started = time.monotonic()
    plan_sha = sha256_file(plan_path)
    runner_sha = sha256_file(SCRIPT_PATH)
    verify_static_hashes(plan, plan_path)
    duplicates = active_duplicate(run_root)
    if duplicates:
        raise RuntimeError(f"Duplicate target-only writer detected: {duplicates}")
    if resume:
        if not pre_path.is_file():
            raise FileNotFoundError("Resume requires the original pre-manifest")
        prior = read_json(pre_path)
        if prior.get("plan_sha256") != plan_sha or prior.get("script_sha256") != runner_sha:
            raise ValueError("Resume identity differs from original plan/script")
    elif run_root.exists():
        raise FileExistsError(f"Fresh target-only run root already exists: {run_root}")
    runtime_root.mkdir(parents=True, exist_ok=True)
    artifacts_root.mkdir(parents=True, exist_ok=True)
    monitor_command = (
        f'powershell -File "{MONITOR_PATH}" -RunRoot "{runtime_root}" '
        "-IntervalSeconds 10 -Compact -Watch"
    )
    if not resume:
        pre = {
            "run_id": plan["run_id"] if plan["mode"] == "FULL" else f"{plan['run_id']}_s{probe_shard}",
            "status": "starting",
            "created_at_utc": utc_text(),
            "script_path": str(SCRIPT_PATH),
            "script_sha256": runner_sha,
            "contract_path": str(Path(contract.__file__).resolve()),
            "contract_sha256": plan["contract_sha256"],
            "plan_path": str(plan_path),
            "plan_sha256": plan_sha,
            "command_line": subprocess.list2cmdline(sys.argv),
            "cwd": os.getcwd(),
            "host": socket.gethostname(),
            "user": getpass.getuser(),
            "wrapper_pid": os.getpid(),
            "git_branch": git_value("branch", "--show-current"),
            "git_commit": git_value("rev-parse", "HEAD"),
            "git_dirty_state": bool(git_value("status", "--porcelain")),
            "mode": plan["mode"],
            "probe_shard": probe_shard,
            "source_run_root": plan["source_run_root"],
            "target_table": plan["target_table"],
            "output_root": str(run_root),
            "runtime_root": str(runtime_root),
            "artifacts_root": str(artifacts_root),
            "resume_policy": plan["resume_policy"],
            "overwrite_policy": "NEVER",
            "source_blocks_recomputed": 0,
            "success_criteria": plan["success_criteria"],
            "monitor_command": monitor_command,
            "inherited_incident_controls": plan["inherited_incident_controls"],
        }
        atomic_json(pre_path, pre)
    atomic_json(
        pid_path,
        {
            "run_id": plan["run_id"],
            "wrapper_pid": os.getpid(),
            "process_name": psutil.Process().name(),
            "started_at_utc": utc_text(),
            "stage": "PREFLIGHT",
            "expected_alive": True,
        },
    )
    log_path.touch(exist_ok=True)
    print(f"run_id={plan['run_id']}", flush=True)
    print(f"mode={plan['mode']}", flush=True)
    print(f"source_root={plan['source_run_root']}", flush=True)
    print(f"output_root={run_root}", flush=True)
    print(f"pre_manifest={pre_path}", flush=True)
    print(f"heartbeat={heartbeat_path}", flush=True)
    print(f"log={log_path}", flush=True)
    print(f"pid_manifest={pid_path}", flush=True)
    print(f"monitor_command={monitor_command}", flush=True)
    print(f"success_rule={plan['success_criteria']}", flush=True)
    print(f"resume_policy={plan['resume_policy']}", flush=True)
    process = psutil.Process()
    last_io = process.io_counters()
    last_emit = time.monotonic()
    verified = 0
    failures = 0
    current_item = "preflight"

    def log(message: str) -> None:
        stamped = f"[{utc_text()}] {message}"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(stamped + "\n")
        print(stamped, flush=True)

    def emit(stage: str, total: int, force: bool = False) -> None:
        nonlocal last_io, last_emit
        now = time.monotonic()
        if not force and now - last_emit < 5:
            return
        io = process.io_counters()
        elapsed_delta = max(now - last_emit, 0.001)
        free = shutil.disk_usage(run_root.anchor).free / 1024**3
        payload = {
            "run_id": plan["run_id"],
            "observed_at_utc": utc_text(),
            "status": "running",
            "stage": stage,
            "elapsed_seconds": round(now - started, 3),
            "wrapper_pid": os.getpid(),
            "active_pid": os.getpid(),
            "active_pid_alive": True,
            "current_item": current_item,
            "current_index": verified,
            "total_count": total,
            "verified_partitions": verified,
            "failed_partitions": failures,
            "process_cpu_pct": psutil.cpu_percent(interval=None),
            "io_read_bytes_per_sec": round((io.read_bytes - last_io.read_bytes) / elapsed_delta, 2),
            "io_write_bytes_per_sec": round((io.write_bytes - last_io.write_bytes) / elapsed_delta, 2),
            "output_drive_free_gb": round(free, 3),
            "target_root": str(run_root),
            "log_path": str(log_path),
        }
        atomic_json(heartbeat_path, payload)
        append_jsonl(heartbeat_history, payload)
        last_io = io
        last_emit = now

    try:
        log("PREFLIGHT: loading 240 immutable block identities")
        block_map = load_block_map(plan)
        rows = load_target_rows(plan)
        selected = select_rows(plan, rows, block_map, probe_shard)
        selected_contract = contract.aggregate_contract(selected)
        total_partitions = int(selected_contract["metadata_scalars"]["partition_count"])
        emit("PREFLIGHT", total_partitions, force=True)
        log(f"INVENTORY: exact targets={len(selected)} partitions={total_partitions}")
        inventory = build_inventory(
            selected, block_map, plan["expected_stage8_engine_fingerprint"]
        )
        write_parquet(inventory_path, inventory)
        inventory_summary = {
            "status": "PASS",
            "created_at_utc": utc_text(),
            "exact_target_contract": selected_contract,
            "inventory_rows": len(inventory),
            "inventory_sha256": sha256_file(inventory_path),
            "source_blocks_recomputed": 0,
        }
        atomic_json(inventory_summary_path, inventory_summary)
        emit("VERIFY_SELECTED_PARTITIONS", total_partitions, force=True)
        prior_results = load_resume_results(verification_path) if resume else {}
        results: list[dict[str, Any]] = []
        schema_variants: dict[str, set[str]] = {
            family: set() for family in contract.PHYSICAL_FAMILY_KEYS
        }
        actual_counts: Counter[str] = Counter()
        samples: dict[str, Any] = {}
        for index, item in enumerate(inventory, start=1):
            current_item = f"{item['ticker']}:{item['session_date']}:{item['family']}"
            if (runtime_root / "stop_requested.json").is_file():
                raise InterruptedError("Safe stop requested")
            key = normalized_path(item["source_path"])
            prior = prior_results.get(key)
            if (
                prior is not None
                and prior.get("actual_sha256") == item["recorded_source_sha256"]
                and int(prior.get("actual_rows", -1)) == int(item["expected_rows"])
                and int(prior.get("actual_bytes", -1)) == int(item["source_bytes"])
            ):
                result = prior
                result = {**result, "resume_state": "REUSED_HASH_VALIDATED_PASS"}
            else:
                result = verify_partition(item)
                append_jsonl(verification_path, result)
            verified = index
            family = str(item["family"])
            schema_variants[family].add(str(result["schema_sha256"]))
            actual_counts[family] += int(result["actual_rows"])
            samples.setdefault(family, result["sample_values"])
            results.append({**dict(item), **result})
            emit("VERIFY_SELECTED_PARTITIONS", total_partitions)
            if index % 25 == 0 or index == total_partitions:
                log(f"VERIFY: {index}/{total_partitions} PASS")
        expected_physical = selected_contract["physical_family_row_counts"]
        contract.assert_physical_counts(actual_counts, expected_physical)
        bad_schema = {
            family: sorted(values)
            for family, values in schema_variants.items()
            if len(values) != 1
        }
        if bad_schema:
            raise AssertionError(f"Schema variants are not one per family: {bad_schema}")
        write_parquet(reference_manifest_path, results)
        controls = []
        for item in plan["inherited_incident_controls"]:
            controls.append(
                {
                    **item,
                    "runtime_status": "PASS",
                    "runtime_evidence": {
                        "exact_target_count": len(selected),
                        "partition_count": len(results),
                        "typed_physical_counts": dict(actual_counts),
                        "metadata_scalars": selected_contract["metadata_scalars"],
                        "schema_variants": {
                            family: len(values) for family, values in schema_variants.items()
                        },
                    },
                }
            )
        final = {
            "run_id": plan["run_id"],
            "status": "PASS",
            "mode": plan["mode"],
            "probe_shard": probe_shard,
            "started_at_utc": read_json(pre_path)["created_at_utc"],
            "completed_at_utc": utc_text(),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "calculation_status": "NOT_EXECUTED_REUSED_FROZEN_OUTPUTS",
            "inventory_status": "PASS",
            "certification_status": "PASS",
            "source_run_status": "FAILED_NOT_PROMOTED",
            "source_blocks_recomputed": 0,
            "exact_target_contract": selected_contract,
            "actual_physical_family_row_counts": dict(actual_counts),
            "schema_variants": {
                family: sorted(values) for family, values in schema_variants.items()
            },
            "hash_validation": {
                "selected": len(results),
                "passed": len(results),
                "failed": 0,
            },
            "validation_inheritance": "BLOCK_VALIDATORS_BOUND_BY_SELECTED_FILE_SHA256",
            "sample_values_by_family": samples,
            "inherited_incident_controls": controls,
            "artifacts": {
                "inventory": str(inventory_path),
                "inventory_sha256": sha256_file(inventory_path),
                "inventory_summary": str(inventory_summary_path),
                "inventory_summary_sha256": sha256_file(inventory_summary_path),
                "partition_verification": str(verification_path),
                "partition_verification_sha256": sha256_file(verification_path),
                "verified_reference_manifest": str(reference_manifest_path),
                "verified_reference_manifest_sha256": sha256_file(reference_manifest_path),
            },
            "plan_sha256": plan_sha,
            "script_sha256": runner_sha,
            "contract_sha256": plan["contract_sha256"],
            "canonical_promotion_authorized": False,
            "promotion_status": "EXPERIMENTAL_NOT_CANONICAL",
            "resume_instructions": "NOT_REQUIRED_TERMINAL_PASS",
        }
        atomic_json(final_path, final)
        current_item = "complete"
        terminal_heartbeat = {
            "run_id": plan["run_id"],
            "observed_at_utc": utc_text(),
            "status": "completed",
            "stage": "FINAL",
            "elapsed_seconds": final["elapsed_seconds"],
            "wrapper_pid": os.getpid(),
            "active_pid": os.getpid(),
            "active_pid_alive": False,
            "current_item": current_item,
            "current_index": len(results),
            "total_count": len(results),
            "verified_partitions": len(results),
            "failed_partitions": 0,
            "output_drive_free_gb": round(shutil.disk_usage(run_root.anchor).free / 1024**3, 3),
            "target_root": str(run_root),
            "log_path": str(log_path),
            "final_manifest": str(final_path),
        }
        atomic_json(heartbeat_path, terminal_heartbeat)
        append_jsonl(heartbeat_history, terminal_heartbeat)
        atomic_json(
            pid_path,
            {
                "run_id": plan["run_id"],
                "wrapper_pid": os.getpid(),
                "completed_at_utc": utc_text(),
                "stage": "FINAL",
                "expected_alive": False,
            },
        )
        log("FINAL: PASS")
        return 0
    except BaseException as exc:
        failures += 1
        interrupted = isinstance(exc, (KeyboardInterrupt, InterruptedError))
        status = "INTERRUPTED" if interrupted else "FAILED"
        failure = {
            "run_id": plan["run_id"],
            "status": status,
            "mode": plan["mode"],
            "probe_shard": probe_shard,
            "failed_at_utc": utc_text(),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "failure_type": type(exc).__name__,
            "failure_reason": str(exc),
            "traceback": traceback.format_exc(),
            "calculation_status": "NOT_EXECUTED_REUSED_FROZEN_OUTPUTS",
            "inventory_status": "PASS" if inventory_path.is_file() else "FAILED_OR_NOT_REACHED",
            "certification_status": status,
            "source_run_status": "FAILED_NOT_PROMOTED",
            "source_blocks_recomputed": 0,
            "verified_partitions": verified,
            "failed_partitions": failures,
            "plan_sha256": plan_sha,
            "script_sha256": runner_sha,
            "canonical_promotion_authorized": False,
            "promotion_status": "NOT_AUTHORIZED",
            "resume_instructions": (
                f'python "{SCRIPT_PATH}" --plan "{plan_path}" '
                + (f"--probe-shard {probe_shard} " if probe_shard is not None else "")
                + "--resume"
            ),
        }
        atomic_json(final_path, failure)
        terminal_heartbeat = {
            "run_id": plan["run_id"],
            "observed_at_utc": utc_text(),
            "status": "failed" if not interrupted else "interrupted",
            "stage": "FINAL",
            "elapsed_seconds": failure["elapsed_seconds"],
            "wrapper_pid": os.getpid(),
            "active_pid": os.getpid(),
            "active_pid_alive": False,
            "current_item": current_item,
            "current_index": verified,
            "total_count": 0,
            "verified_partitions": verified,
            "failed_partitions": failures,
            "last_error": str(exc),
            "target_root": str(run_root),
            "log_path": str(log_path),
            "final_manifest": str(final_path),
        }
        atomic_json(heartbeat_path, terminal_heartbeat)
        append_jsonl(heartbeat_history, terminal_heartbeat)
        atomic_json(
            pid_path,
            {
                "run_id": plan["run_id"],
                "wrapper_pid": os.getpid(),
                "completed_at_utc": utc_text(),
                "stage": "FINAL",
                "expected_alive": False,
            },
        )
        log(f"FINAL: {status}: {exc}")
        return 130 if interrupted else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--probe-shard", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    return execute(args.plan, args.probe_shard, args.resume)


if __name__ == "__main__":
    raise SystemExit(main())
