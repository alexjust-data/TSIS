#!/usr/bin/env python3
"""Governed multisession runner for experimental Trading Activity Binding A."""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
import threading
import traceback
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq
from evaluate_trading_activity_trade_eligibility import load_condition_matrix
from trading_activity_binding_a_multisession_engine import (
    atomic_write_json,
    atomic_write_parquet,
    atomic_write_text,
    audit_session_variable_families,
    build_dense_input_manifest,
    coverage_gate_from_audit,
    expected_row_counts,
    load_foundation_evidence,
    materialize_baseline_and_surprise,
    materialize_current_state,
    materialize_multiscale_contrast,
    normalize_utc,
    resolve_identity,
    select_calendar_block,
    sha256_file,
    utc_now,
    utc_text,
    validate_event_index_equivalence,
)
from trading_activity_binding_a_multisession_runtime import (
    choose_evaluation_dates,
    load_acquisition_evidence_bounded,
    load_and_evaluate_events,
)


class ControlledStop(RuntimeError):
    pass


class Telemetry:
    def __init__(self, root: Path, run_id: str, interval_seconds: int) -> None:
        self.root = root
        self.run_id = run_id
        self.interval_seconds = interval_seconds
        self.started_at = utc_now()
        self.status = "STARTING"
        self.stage = "STAGE_0"
        self.current_session: str | None = None
        self.counters: dict[str, int | float] = {}
        self.message = "initializing"
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

    @property
    def stop_requested(self) -> bool:
        return (self.root / "stop_requested.json").exists()

    def start(self, argv: list[str]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        atomic_write_json(
            self.root / "pid_manifest.json",
            {
                "run_id": self.run_id,
                "pid": os.getpid(),
                "argv": argv,
                "started_at_utc": utc_text(self.started_at),
                "host": os.environ.get("COMPUTERNAME"),
            },
        )
        self.emit(status="RUNNING", message="runner started")
        self._thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._thread.start()

    def _snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "run_id": self.run_id,
                "timestamp_utc": utc_text(),
                "status": self.status,
                "stage": self.stage,
                "pid": os.getpid(),
                "current_session": self.current_session,
                "message": self.message,
                "elapsed_seconds": (utc_now() - self.started_at).total_seconds(),
                "counters": dict(self.counters),
            }

    def _write_snapshot(self) -> None:
        snapshot = self._snapshot()
        atomic_write_json(self.root / "heartbeat_latest.json", snapshot)
        with (self.root / "heartbeat_history.jsonl").open(
            "a", encoding="utf-8"
        ) as handle:
            handle.write(json.dumps(snapshot, sort_keys=True, default=str) + "\n")

    def _heartbeat_loop(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            self._write_snapshot()

    def emit(
        self,
        *,
        stage: str | None = None,
        status: str | None = None,
        message: str | None = None,
        current_session: str | None = None,
        counters: dict[str, int | float] | None = None,
    ) -> None:
        with self._lock:
            if stage is not None:
                self.stage = stage
            if status is not None:
                self.status = status
            if message is not None:
                self.message = message
            if current_session is not None:
                self.current_session = current_session
            if counters:
                self.counters.update(counters)
        self._write_snapshot()
        with (self.root / "run.log").open("a", encoding="utf-8") as handle:
            handle.write(
                f"{utc_text()} status={self.status} stage={self.stage} "
                f"session={self.current_session} message={self.message}\n"
            )

    def check_stop(self) -> None:
        if self.stop_requested:
            raise ControlledStop("cooperative stop requested")

    def close(self, status: str, message: str) -> None:
        self.emit(status=status, message=message)
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--session-date", action="append", default=[])
    parser.add_argument("--session-limit", type=int)
    parser.add_argument("--decision-seconds-limit", type=int)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--pointer-root", type=Path)
    parser.add_argument("--skip-disk-gate", action="store_true")
    parser.add_argument("--stop-after-stage")
    return parser


def _load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _verify_source(path: Path, expected_sha256: str | None) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = sha256_file(path)
    if expected_sha256 and actual != expected_sha256:
        raise ValueError(f"Source hash mismatch for {path}: {actual}")
    return {"path": str(path), "sha256": actual, "bytes": path.stat().st_size}


def _validate_run_roots(
    output_run_root: Path, runtime_run_root: Path, *, resume: bool
) -> None:
    if output_run_root.exists() and not resume:
        raise FileExistsError(f"Output run already exists: {output_run_root}")
    final_path = runtime_run_root / "final_manifest.json"
    if final_path.exists() and not resume:
        raise FileExistsError(f"Runtime run already finalized: {runtime_run_root}")
    if resume and not output_run_root.exists():
        raise FileNotFoundError(f"Cannot resume missing output run: {output_run_root}")


def _existing_partition(path: Path) -> dict[str, Any] | None:
    hash_path = path.with_suffix(path.suffix + ".sha256")
    if not path.exists() and not hash_path.exists():
        return None
    if not path.exists() or not hash_path.exists():
        raise ValueError(f"Incomplete resumable partition: {path}")
    expected = hash_path.read_text(encoding="ascii").strip()
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"Resumable partition hash mismatch: {path}")
    metadata = pq.ParquetFile(path).metadata
    return {
        "path": str(path),
        "sha256": actual,
        "rows": metadata.num_rows,
        "bytes": path.stat().st_size,
        "resumed": True,
    }


def _write_partition(
    frame: pd.DataFrame, path: Path, compression: str, *, resume: bool
) -> dict[str, Any]:
    existing = _existing_partition(path)
    if existing is not None:
        if not resume:
            raise FileExistsError(path)
        return existing
    return atomic_write_parquet(frame, path, compression=compression)


def _partition_path(root: Path, family: str, ticker: str, value: date) -> Path:
    return (
        root
        / family
        / f"ticker={ticker}"
        / f"session_date={value.isoformat()}"
        / "part-00000.parquet"
    )


def _read_partitions(
    paths: Iterable[Path], columns: list[str] | None = None
) -> pd.DataFrame:
    frames = [pd.read_parquet(path, columns=columns) for path in paths]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _schema_payload(paths: list[Path]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for path in paths:
        if path.is_file():
            schema = pq.read_schema(path)
            payload[str(path)] = {field.name: str(field.type) for field in schema}
    return payload


def _stop_after(telemetry: Telemetry, requested: str | None, stage: str) -> None:
    telemetry.check_stop()
    if requested and requested.upper() == stage.upper():
        raise ControlledStop(f"controlled test stop after {stage}")


def _selected_calendar(
    config: dict[str, Any], args: argparse.Namespace
) -> tuple[pd.DataFrame, bool]:
    scope = config["scope"]
    smoke_mode = bool(
        args.session_date or args.session_limit or args.decision_seconds_limit
    )
    calendar = select_calendar_block(
        Path(config["sources"]["calendar_path"]),
        calendar_name=scope["calendar"],
        start=date.fromisoformat(scope["session_start"]),
        end=date.fromisoformat(scope["session_end"]),
        expected_count=None if smoke_mode else int(scope["expected_session_count"]),
        session_limit=args.session_limit,
    )
    if args.session_date:
        requested = {date.fromisoformat(value) for value in args.session_date}
        calendar = calendar.loc[calendar["session_date"].isin(requested)].copy()
        if set(calendar["session_date"]) != requested:
            missing = sorted(requested - set(calendar["session_date"]))
            raise ValueError(f"Requested smoke sessions absent from calendar: {missing}")
    return calendar.reset_index(drop=True), smoke_mode


def _actual_expected_counts(
    calendar: pd.DataFrame,
    evaluation_dates: set[date],
    decision_seconds_limit: int | None,
) -> dict[str, int]:
    if decision_seconds_limit is None:
        return expected_row_counts(calendar, evaluation_dates)
    seconds_by_date = {
        row.session_date: min(
            decision_seconds_limit,
            int((normalize_utc(row.close_utc) - normalize_utc(row.open_utc)).total_seconds())
            - 1,
        )
        for row in calendar.itertuples(index=False)
    }
    total = sum(seconds_by_date.values())
    evaluation = sum(
        seconds for key, seconds in seconds_by_date.items() if key in evaluation_dates
    )
    return {
        "decision_seconds_total": total,
        "current_state_rows": total * 5,
        "multiscale_rows": total * 2,
        "baseline_rows": evaluation * 5 * 3,
    }


def run(args: argparse.Namespace) -> int:
    config_path = args.config.resolve()
    config = copy.deepcopy(_load_config(config_path))
    output_base = args.output_root or Path(config["outputs"]["heavy_output_root"])
    runtime_base = args.runtime_root or Path(config["outputs"]["runtime_root"])
    pointer_base = args.pointer_root or Path(config["outputs"]["pointer_root"])
    output_run_root = output_base / f"run_id={args.run_id}"
    runtime_run_root = runtime_base / args.run_id
    pointer_root = pointer_base / args.run_id
    _validate_run_roots(output_run_root, runtime_run_root, resume=args.resume)
    output_run_root.mkdir(parents=True, exist_ok=True)
    runtime_run_root.mkdir(parents=True, exist_ok=True)
    pointer_root.mkdir(parents=True, exist_ok=True)

    config_sha256 = sha256_file(config_path)
    premanifest_path = runtime_run_root / "pre_manifest.json"
    if not premanifest_path.exists():
        atomic_write_json(
            premanifest_path,
            {
                "run_id": args.run_id,
                "operation": "trading_activity_binding_a_multisession_pilot",
                "created_at_utc": utc_text(),
                "config_path": str(config_path),
                "config_sha256": config_sha256,
                "output_run_root": str(output_run_root),
                "runtime_run_root": str(runtime_run_root),
                "smoke_overrides": {
                    "session_dates": args.session_date,
                    "session_limit": args.session_limit,
                    "decision_seconds_limit": args.decision_seconds_limit,
                },
                "promotion_status": "NOT_AUTHORIZED",
            },
        )
    elif json.loads(premanifest_path.read_text(encoding="utf-8"))[
        "config_sha256"
    ] != config_sha256:
        raise ValueError("Resume config hash differs from pre-manifest")

    telemetry = Telemetry(
        runtime_run_root,
        args.run_id,
        int(config["operation"]["heartbeat_interval_seconds"]),
    )
    telemetry.start(sys.argv)
    partition_records: list[dict[str, Any]] = []
    resumed_partitions: list[str] = []
    warnings: list[str] = []
    final_status = "FAILED"
    final_message = "unhandled failure"
    try:
        telemetry.emit(stage="STAGE_0", message="validating invocation")
        _stop_after(telemetry, args.stop_after_stage, "STAGE_0")

        telemetry.emit(stage="STAGE_1", message="resolving governed scope")
        source_bindings = {
            "calendar": _verify_source(
                Path(config["sources"]["calendar_path"]),
                config["sources"].get("calendar_expected_sha256"),
            ),
            "instrument_master": _verify_source(
                Path(config["sources"]["instrument_master_path"]),
                config["sources"].get("instrument_master_expected_sha256"),
            ),
            "condition_policy_matrix": _verify_source(
                Path(config["sources"]["condition_policy_matrix_path"]),
                config["sources"].get("condition_policy_matrix_expected_sha256"),
            ),
        }
        calendar, smoke_mode = _selected_calendar(config, args)
        selected_dates = set(calendar["session_date"])
        scope = config["scope"]
        resolve_identity(
            Path(config["sources"]["instrument_master_path"]),
            ticker=scope["ticker"],
            instrument_id=scope["instrument_id"],
            start=min(selected_dates),
            end=max(selected_dates),
        )
        evaluation_dates = choose_evaluation_dates(
            sorted(selected_dates),
            evaluation_start=date.fromisoformat(scope["evaluation_start"]),
            evaluation_end=date.fromisoformat(scope["evaluation_end"]),
            smoke_mode=smoke_mode,
        )
        telemetry.emit(counters={"sessions_total": len(calendar)})
        _stop_after(telemetry, args.stop_after_stage, "STAGE_1")

        telemetry.emit(stage="STAGE_2", message="joining source evidence")
        foundation = load_foundation_evidence(
            Path(config["sources"]["foundation_57f_shards_root"]),
            ticker=scope["ticker"],
            selected_dates=selected_dates,
        )
        acquisition = load_acquisition_evidence_bounded(
            Path(config["sources"]["acquisition_manifest_root"]),
            ticker=scope["ticker"],
            selected_dates=selected_dates,
        )
        dense = build_dense_input_manifest(
            calendar,
            raw_root=Path(config["sources"]["raw_trade_root"]),
            ticker=scope["ticker"],
            instrument_id=scope["instrument_id"],
            foundation=foundation,
            acquisition_records=acquisition,
        )
        dense["acquisition_evidence_state"] = dense.apply(
            lambda row: (
                "RESOLVED"
                if row["acquisition_evidence_state"] == "RESOLVED"
                else "SOURCE_EXISTS_ACQUISITION_EVIDENCE_PENDING"
                if row["source_exists"]
                else "SOURCE_AND_ACQUISITION_EVIDENCE_MISSING"
            ),
            axis=1,
        )
        scope_root = output_run_root / "scope"
        dense_record = _write_partition(
            dense,
            scope_root / "dense_input_manifest.parquet",
            config["outputs"]["parquet_compression"],
            resume=args.resume,
        )
        partition_records.append(dense_record)
        if dense_record["resumed"]:
            resumed_partitions.append(dense_record["path"])
        atomic_write_text(scope_root / "dense_input_manifest.csv", dense.to_csv(index=False))
        _stop_after(telemetry, args.stop_after_stage, "STAGE_2")

        telemetry.emit(stage="STAGE_3", message="executing selected-session local audit")
        matrix = load_condition_matrix(Path(config["sources"]["condition_policy_matrix_path"]))
        events_by_date: dict[date, list[dict[str, Any]]] = {}
        audit_rows: list[dict[str, Any]] = []
        session_counters: dict[date, dict[str, int]] = {}
        for manifest_row in dense.to_dict("records"):
            telemetry.check_stop()
            session_date = manifest_row["session_date"]
            events, counters = load_and_evaluate_events(
                Path(manifest_row["source_path"]),
                matrix=matrix,
                session_open=normalize_utc(manifest_row["open_utc"]),
                session_close=normalize_utc(manifest_row["close_utc"]),
                simulated_latency_ms=int(config["binding"]["simulated_latency_ms"]),
            )
            events_by_date[session_date] = events
            session_counters[session_date] = counters
            audit_rows.extend(audit_session_variable_families(manifest_row, events))
            telemetry.emit(
                current_session=session_date.isoformat(),
                counters={
                    "sessions_audited": len(events_by_date),
                    "source_trade_rows": sum(
                        item["source_trade_rows"] for item in session_counters.values()
                    ),
                    "eligible_trade_rows": sum(
                        item["eligible_trade_rows"] for item in session_counters.values()
                    ),
                    "unknown_fail_closed_rows": sum(
                        item["unknown_fail_closed_rows"]
                        for item in session_counters.values()
                    ),
                },
            )
        audits = pd.DataFrame(audit_rows)
        audit_record = _write_partition(
            audits,
            scope_root / "selected_session_local_audit.parquet",
            config["outputs"]["parquet_compression"],
            resume=args.resume,
        )
        partition_records.append(audit_record)
        if audit_record["resumed"]:
            resumed_partitions.append(audit_record["path"])
        _stop_after(telemetry, args.stop_after_stage, "STAGE_3")

        telemetry.emit(stage="STAGE_4", message="running sizing and kernel-equivalence probes")
        equivalence: dict[str, Any] = {"sessions": {}, "status": "PASS"}
        for manifest_row in dense.to_dict("records"):
            session_date = manifest_row["session_date"]
            audit_for_session = [
                row for row in audit_rows if row["session_date"] == session_date
            ]
            result = validate_event_index_equivalence(
                events_by_date[session_date],
                session_open=normalize_utc(manifest_row["open_utc"]),
                session_close=normalize_utc(manifest_row["close_utc"]),
                coverage_gate_pass=coverage_gate_from_audit(audit_for_session),
                seed=int(config["operation"]["kernel_equivalence_seed"]),
                random_sample_count=int(
                    config["operation"]["kernel_equivalence_random_samples_per_session"]
                ),
            )
            equivalence["sessions"][session_date.isoformat()] = result
            if result["status"] != "PASS":
                equivalence["status"] = "FAIL"
        if equivalence["status"] != "PASS":
            raise ValueError("Kernel equivalence probe failed")
        validation_root = output_run_root / "validation"
        atomic_write_json(validation_root / "kernel_equivalence_validation.json", equivalence)

        first_manifest = dense.iloc[0].to_dict()
        first_date = first_manifest["session_date"]
        first_audit = [row for row in audit_rows if row["session_date"] == first_date]
        sizing_current = materialize_current_state(
            events_by_date[first_date],
            config=config,
            manifest_row=first_manifest,
            coverage_gate_pass=coverage_gate_from_audit(first_audit),
            decision_seconds_limit=min(args.decision_seconds_limit or 120, 120),
        )
        sizing_multiscale = materialize_multiscale_contrast(sizing_current, config=config)
        probe_dir = validation_root / ".sizing_probe"
        probe_dir.mkdir(parents=True, exist_ok=True)
        current_probe = probe_dir / "current.parquet"
        multiscale_probe = probe_dir / "multiscale.parquet"
        sizing_current.to_parquet(current_probe, compression="zstd", index=False)
        sizing_multiscale.to_parquet(multiscale_probe, compression="zstd", index=False)
        expected = _actual_expected_counts(
            calendar, evaluation_dates, args.decision_seconds_limit
        )
        current_bpr = current_probe.stat().st_size / max(1, len(sizing_current))
        multiscale_bpr = multiscale_probe.stat().st_size / max(1, len(sizing_multiscale))
        projected_bytes = int(
            current_bpr * expected["current_state_rows"]
            + multiscale_bpr * expected["multiscale_rows"]
            + current_bpr * 1.8 * expected["baseline_rows"]
        )
        current_probe.unlink()
        multiscale_probe.unlink()
        probe_dir.rmdir()
        free_bytes = shutil.disk_usage(output_run_root).free
        sizing = {
            "current_compressed_bytes_per_row": current_bpr,
            "multiscale_compressed_bytes_per_row": multiscale_bpr,
            "baseline_projected_bytes_per_row": current_bpr * 1.8,
            "projected_bytes": projected_bytes,
            "projected_gib": projected_bytes / 1024**3,
            "free_bytes": free_bytes,
            "free_gib": free_bytes / 1024**3,
            "expected_counts": expected,
        }
        atomic_write_json(validation_root / "serialization_sizing_probe.json", sizing)
        if not smoke_mode and not args.skip_disk_gate:
            maximum = int(config["operation"]["maximum_projected_output_gib"]) * 1024**3
            required = max(
                int(config["operation"]["minimum_free_space_gib"]) * 1024**3,
                int(config["operation"]["minimum_free_space_multiplier"])
                * projected_bytes,
            )
            if projected_bytes > maximum:
                raise ValueError("Projected output exceeds configured maximum")
            if free_bytes < required:
                raise ValueError("Insufficient free space for governed disk gate")
        _stop_after(telemetry, args.stop_after_stage, "STAGE_4")

        compression = config["outputs"]["parquet_compression"]
        ticker = scope["ticker"]
        current_paths: dict[date, Path] = {}
        telemetry.emit(stage="STAGE_5", message="materializing CURRENT_STATE")
        for manifest_row in dense.to_dict("records"):
            telemetry.check_stop()
            session_date = manifest_row["session_date"]
            path = _partition_path(output_run_root, "current_state", ticker, session_date)
            current_paths[session_date] = path
            existing = _existing_partition(path) if args.resume else None
            if existing is None:
                audit_for_session = [
                    row for row in audit_rows if row["session_date"] == session_date
                ]
                frame = materialize_current_state(
                    events_by_date[session_date],
                    config=config,
                    manifest_row=manifest_row,
                    coverage_gate_pass=coverage_gate_from_audit(audit_for_session),
                    decision_seconds_limit=args.decision_seconds_limit,
                )
                record = _write_partition(frame, path, compression, resume=args.resume)
            else:
                record = existing
            partition_records.append(record)
            if record["resumed"]:
                resumed_partitions.append(record["path"])
            telemetry.emit(
                current_session=session_date.isoformat(),
                counters={
                    "current_state_sessions": len(current_paths),
                    "current_state_rows": sum(
                        item["rows"]
                        for item in partition_records
                        if "current_state" in item["path"]
                    ),
                    "partitions_written": len(partition_records),
                    "bytes_written": sum(item["bytes"] for item in partition_records),
                },
            )
        _stop_after(telemetry, args.stop_after_stage, "STAGE_5")

        telemetry.emit(stage="STAGE_6", message="materializing MULTISCALE_CONTRAST")
        multiscale_paths: dict[date, Path] = {}
        for session_date, current_path in current_paths.items():
            telemetry.check_stop()
            path = _partition_path(
                output_run_root, "multiscale_contrast", ticker, session_date
            )
            multiscale_paths[session_date] = path
            existing = _existing_partition(path) if args.resume else None
            if existing is None:
                frame = materialize_multiscale_contrast(
                    pd.read_parquet(current_path), config=config
                )
                record = _write_partition(frame, path, compression, resume=args.resume)
            else:
                record = existing
            partition_records.append(record)
            if record["resumed"]:
                resumed_partitions.append(record["path"])
            telemetry.emit(
                current_session=session_date.isoformat(),
                counters={
                    "multiscale_sessions": len(multiscale_paths),
                    "multiscale_rows": sum(
                        item["rows"]
                        for item in partition_records
                        if "multiscale_contrast" in item["path"]
                    ),
                    "partitions_written": len(partition_records),
                    "bytes_written": sum(item["bytes"] for item in partition_records),
                },
            )
        _stop_after(telemetry, args.stop_after_stage, "STAGE_6")

        telemetry.emit(stage="STAGE_7", message="building cached PIT baseline distributions")
        baseline_columns = [
            "session_date",
            "decision_timestamp",
            "window_seconds",
            "calculation_state",
            "eligible_trade_count",
            "eligible_share_volume",
            "eligible_dollar_volume",
            "trade_arrival_rate",
            "median_intertrade_duration_us",
            "feature_input_max_available_at",
        ]
        prior_frames = _read_partitions(
            [current_paths[key] for key in sorted(current_paths)],
            columns=baseline_columns,
        )
        _stop_after(telemetry, args.stop_after_stage, "STAGE_7")

        telemetry.emit(stage="STAGE_8", message="materializing PIT_BASELINE_AND_SURPRISE")
        baseline_paths: dict[date, Path] = {}
        for session_date in sorted(evaluation_dates):
            telemetry.check_stop()
            path = _partition_path(
                output_run_root, "pit_baseline_and_surprise", ticker, session_date
            )
            baseline_paths[session_date] = path
            existing = _existing_partition(path) if args.resume else None
            if existing is None:
                current = pd.read_parquet(current_paths[session_date])
                frame = materialize_baseline_and_surprise(
                    current,
                    prior_current=prior_frames,
                    config=config,
                    evaluation_session_date=session_date,
                )
                record = _write_partition(frame, path, compression, resume=args.resume)
            else:
                record = existing
            partition_records.append(record)
            if record["resumed"]:
                resumed_partitions.append(record["path"])
            telemetry.emit(
                current_session=session_date.isoformat(),
                counters={
                    "baseline_sessions": len(baseline_paths),
                    "baseline_rows": sum(
                        item["rows"]
                        for item in partition_records
                        if "pit_baseline_and_surprise" in item["path"]
                    ),
                    "partitions_written": len(partition_records),
                    "bytes_written": sum(item["bytes"] for item in partition_records),
                },
            )
        _stop_after(telemetry, args.stop_after_stage, "STAGE_8")

        telemetry.emit(stage="STAGE_9", message="validating outputs")
        actual = {
            "current_state_rows": sum(pq.ParquetFile(path).metadata.num_rows for path in current_paths.values()),
            "multiscale_rows": sum(pq.ParquetFile(path).metadata.num_rows for path in multiscale_paths.values()),
            "baseline_rows": sum(pq.ParquetFile(path).metadata.num_rows for path in baseline_paths.values()),
        }
        row_count_status = all(actual[key] == expected[key] for key in actual)
        row_count_validation = {
            "status": "PASS" if row_count_status else "FAIL",
            "expected": expected,
            "actual": actual,
        }
        atomic_write_json(validation_root / "row_count_validation.json", row_count_validation)
        if not row_count_status:
            raise ValueError("Output row-count validation failed")

        grain_failures: list[str] = []
        temporal_failures: list[str] = []
        for _family, paths, key_columns in (
            (
                "current_state",
                current_paths.values(),
                ["instrument_id", "session_date", "decision_timestamp", "window_seconds"],
            ),
            (
                "multiscale_contrast",
                multiscale_paths.values(),
                ["instrument_id", "session_date", "decision_timestamp", "pair_id"],
            ),
            (
                "pit_baseline_and_surprise",
                baseline_paths.values(),
                [
                    "instrument_id",
                    "session_date",
                    "decision_timestamp",
                    "window_seconds",
                    "baseline_candidate_id",
                ],
            ),
        ):
            for path in paths:
                frame = pd.read_parquet(
                    path,
                    columns=list(
                        dict.fromkeys(
                            key_columns
                            + [
                                "feature_input_max_available_at",
                                "future_window_used",
                                "decision_timestamp",
                            ]
                        )
                    ),
                )
                if frame.duplicated(key_columns).any():
                    grain_failures.append(str(path))
                available = pd.to_datetime(frame["feature_input_max_available_at"], utc=True)
                decision = pd.to_datetime(frame["decision_timestamp"], utc=True)
                if (available.notna() & (available > decision)).any():
                    temporal_failures.append(f"future_available_at:{path}")
                if frame["future_window_used"].fillna(True).any():
                    temporal_failures.append(f"future_window:{path}")
        atomic_write_json(
            validation_root / "grain_uniqueness_validation.json",
            {"status": "PASS" if not grain_failures else "FAIL", "failures": grain_failures},
        )
        atomic_write_json(
            validation_root / "temporal_legality_validation.json",
            {"status": "PASS" if not temporal_failures else "FAIL", "failures": temporal_failures},
        )
        if grain_failures or temporal_failures:
            raise ValueError("Grain or temporal validation failed")
        baseline_reference_validation = {
            "status": "PASS",
            "evaluation_dates": sorted(value.isoformat() for value in evaluation_dates),
            "rule": "REFERENCE_SESSION_DATE_STRICTLY_BEFORE_EVALUATION_SESSION_DATE",
        }
        atomic_write_json(
            validation_root / "baseline_reference_validation.json",
            baseline_reference_validation,
        )
        hash_frame = pd.DataFrame(partition_records).drop_duplicates("path", keep="last")
        hash_record = _write_partition(
            hash_frame,
            validation_root / "output_hashes.parquet",
            compression,
            resume=args.resume,
        )
        partition_records.append(hash_record)
        _stop_after(telemetry, args.stop_after_stage, "STAGE_9")

        telemetry.emit(stage="STAGE_10", message="writing final metadata and pointer")
        metadata_root = output_run_root / "metadata"
        representative_paths = [
            next(iter(current_paths.values())),
            next(iter(multiscale_paths.values())),
            next(iter(baseline_paths.values())),
        ]
        atomic_write_json(
            metadata_root / "output_schema_manifest.json",
            {
                "run_id": args.run_id,
                "schemas": _schema_payload(representative_paths),
                "schema_status": "EXPERIMENTAL_NOT_CANONICAL",
            },
        )
        atomic_write_json(
            metadata_root / "lineage_manifest.json",
            {
                "run_id": args.run_id,
                "config_sha256": config_sha256,
                "source_bindings": source_bindings,
                "binding": config["binding"],
                "scope": config["scope"],
                "foundation_labels_are_automatic_filters": False,
                "future_window_used": False,
                "promotion_status": "NOT_AUTHORIZED",
            },
        )
        summary = {
            "run_id": args.run_id,
            "run_completion": "PASS",
            "smoke_mode": smoke_mode,
            "scope_sessions": len(calendar),
            "evaluation_sessions": len(evaluation_dates),
            "row_counts": actual,
            "expected_row_counts": expected,
            "resumed_partitions": sorted(set(resumed_partitions)),
            "warnings": warnings,
            "promotion_status": "NOT_AUTHORIZED",
        }
        atomic_write_json(metadata_root / "run_summary.json", summary)
        pointer_payload = {
            "run_id": args.run_id,
            "status": "COMPLETE",
            "output_run_root": str(output_run_root),
            "runtime_run_root": str(runtime_run_root),
            "run_summary_path": str(metadata_root / "run_summary.json"),
            "config_path": str(config_path),
            "config_sha256": config_sha256,
            "row_counts": actual,
            "promotion_status": "NOT_AUTHORIZED",
        }
        atomic_write_json(pointer_root / "run_pointer_manifest.json", pointer_payload)
        final_status = "COMPLETE"
        final_message = "governed run completed"
        return 0
    except ControlledStop as exc:
        final_status = "INTERRUPTED_COOPERATIVE"
        final_message = str(exc)
        return 2
    except Exception as exc:
        final_status = "FAILED"
        final_message = f"{type(exc).__name__}: {exc}"
        with (runtime_run_root / "run.log").open("a", encoding="utf-8") as handle:
            handle.write(traceback.format_exc())
        return 1
    finally:
        final_payload = {
            "run_id": args.run_id,
            "status": final_status,
            "message": final_message,
            "finished_at_utc": utc_text(),
            "output_run_root": str(output_run_root),
            "runtime_run_root": str(runtime_run_root),
            "partition_count": len(partition_records),
            "resumed_partitions": sorted(set(resumed_partitions)),
            "promotion_status": "NOT_AUTHORIZED",
        }
        attempts = sorted(runtime_run_root.glob("final_manifest_attempt_*.json"))
        attempt_path = runtime_run_root / f"final_manifest_attempt_{len(attempts) + 1:03d}.json"
        atomic_write_json(attempt_path, final_payload)
        atomic_write_json(runtime_run_root / "final_manifest.json", final_payload)
        telemetry.close(final_status, final_message)


def main() -> int:
    return run(_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())

