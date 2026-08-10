from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pyarrow.parquet as pq


DATASET_ID = "trading_activity_rth_coverage_sidecar_candidate_v0_1"
SPECIFICATION_VERSION = "v0_2"
SOURCE_DATASET_ID = "trades_ticks_prod_2005_2026_legacy_rth_reduced"
AUDITED_DOWNLOADER_COMMIT = "3121664a5948b93c1d212d5ffedd4f101ac3f8a9"
AUDITED_DOWNLOADER_CONTENT_HASH = "7ca8f21c9a8252bb7186d6c1e2a89a6cd0129139"
PAGINATION_EVIDENCE_MODE = "INFERRED_FROM_AUDITED_DOWNLOADER_TERMINAL_RETURN"
REQUIRED_TRADE_COLUMNS = {
    "ticker",
    "date",
    "timestamp",
    "price",
    "size",
    "exchange",
    "conditions",
    "year",
    "month",
    "day",
}
TERMINAL_STATUSES = {"DOWNLOADED_OK", "DOWNLOADED_EMPTY", "DOWNLOAD_FAIL"}


@dataclass(frozen=True)
class ExpectedTask:
    task_key: str
    ticker: str
    date: str
    session: str
    expected_file: str
    source_run_id: str


@dataclass(frozen=True)
class TerminalEvent:
    task_key: str
    status: str
    rows: int | None
    file: str
    processed_at_utc: str
    error: str


OUTPUT_COLUMNS = [
    "task_key",
    "ticker",
    "trading_date",
    "session",
    "source_run_id",
    "source_dataset_id",
    "source_schema_version",
    "historical_expected_file",
    "active_physical_file",
    "acquisition_status",
    "acquisition_rows",
    "terminal_event_count",
    "downloader_commit",
    "downloader_content_hash",
    "downloader_identity_state",
    "pagination_evidence_mode",
    "physical_file_exists",
    "physical_file_readable",
    "physical_row_count",
    "row_count_match",
    "required_schema_state",
    "schema_fingerprint",
    "physical_file_sha256",
    "acquisition_hash_comparison_state",
    "coverage_gate_state",
    "coverage_restriction_reason_codes",
    "window_zero_assertion_capability",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _schema_fingerprint(schema: Any) -> str:
    payload = schema.to_string().encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _active_file_path(source_root: Path, task: ExpectedTask) -> Path:
    date = datetime.strptime(task.date, "%Y-%m-%d")
    return (
        source_root
        / task.ticker
        / f"year={date.year:04d}"
        / f"month={date.month:02d}"
        / f"day={task.date}"
        / f"{task.session}.parquet"
    )


def _read_expected_tasks(path: Path, source_run_id: str) -> list[ExpectedTask]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"task_key", "ticker", "date", "session", "expected_file"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing expected-manifest columns in {path}: {sorted(missing)}")
        return [
            ExpectedTask(
                task_key=str(row["task_key"]).strip(),
                ticker=str(row["ticker"]).strip().upper(),
                date=str(row["date"]).strip(),
                session=str(row["session"]).strip(),
                expected_file=str(row["expected_file"]).strip(),
                source_run_id=source_run_id,
            )
            for row in reader
        ]


def _read_terminal_events(path: Path, wanted: set[str]) -> dict[str, list[TerminalEvent]]:
    events: dict[str, list[TerminalEvent]] = {key: [] for key in wanted}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"task_key", "status", "rows", "file", "processed_at_utc", "error"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing terminal-event columns in {path}: {sorted(missing)}")
        for row in reader:
            key = str(row["task_key"]).strip()
            if key not in wanted:
                continue
            status = str(row["status"]).strip()
            if status not in TERMINAL_STATUSES:
                continue
            events[key].append(
                TerminalEvent(
                    task_key=key,
                    status=status,
                    rows=_parse_optional_int(row.get("rows")),
                    file=str(row.get("file") or "").strip(),
                    processed_at_utc=str(row.get("processed_at_utc") or "").strip(),
                    error=str(row.get("error") or "").strip(),
                )
            )
    return events


def _inspect_parquet(path: Path, *, hash_file: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "physical_file_exists": path.exists(),
        "physical_file_readable": False,
        "physical_row_count": None,
        "required_schema_state": "NOT_INSPECTED",
        "source_schema_version": "UNRESOLVED",
        "schema_fingerprint": "",
        "physical_file_sha256": "",
    }
    if not path.exists():
        return result
    try:
        parquet = pq.ParquetFile(path)
        schema = parquet.schema_arrow
        names = set(schema.names)
        missing = sorted(REQUIRED_TRADE_COLUMNS - names)
        result.update(
            {
                "physical_file_readable": True,
                "physical_row_count": int(parquet.metadata.num_rows),
                "required_schema_state": "PASS" if not missing else f"FAIL_MISSING:{','.join(missing)}",
                "source_schema_version": _schema_fingerprint(schema),
                "schema_fingerprint": _schema_fingerprint(schema),
            }
        )
        if hash_file:
            result["physical_file_sha256"] = _sha256_file(path)
    except Exception as exc:  # pragma: no cover - exact backend error is environment-specific
        result["required_schema_state"] = f"FAIL_UNREADABLE:{type(exc).__name__}"
    return result


def _evaluate_task(
    task: ExpectedTask,
    terminal_events: list[TerminalEvent],
    *,
    source_root: Path,
    downloader_commit: str,
    downloader_content_hash: str,
    hash_files: bool,
) -> dict[str, Any]:
    active_file = _active_file_path(source_root, task)
    identity_pass = (
        downloader_commit == AUDITED_DOWNLOADER_COMMIT
        and downloader_content_hash == AUDITED_DOWNLOADER_CONTENT_HASH
    )
    event = terminal_events[0] if len(terminal_events) == 1 else None
    status = event.status if event is not None else "MISSING_OR_DUPLICATE_TERMINAL_EVENT"
    acquisition_rows = event.rows if event is not None else None
    reasons: list[str] = []

    if len(terminal_events) == 0:
        reasons.append("MISSING_TERMINAL_EVENT")
    elif len(terminal_events) > 1:
        reasons.append("DUPLICATE_TERMINAL_EVENTS")
    if not identity_pass:
        reasons.append("DOWNLOADER_IDENTITY_MISMATCH")

    parquet_info = {
        "physical_file_exists": active_file.exists(),
        "physical_file_readable": False,
        "physical_row_count": None,
        "required_schema_state": "NOT_APPLICABLE",
        "source_schema_version": "UNRESOLVED",
        "schema_fingerprint": "",
        "physical_file_sha256": "",
    }
    row_count_match: bool | None = None

    if event is not None and event.status == "DOWNLOADED_OK":
        parquet_info = _inspect_parquet(active_file, hash_file=hash_files)
        if not parquet_info["physical_file_exists"]:
            reasons.append("ACTIVE_FILE_MISSING")
        elif not parquet_info["physical_file_readable"]:
            reasons.append("ACTIVE_FILE_UNREADABLE")
        if parquet_info["required_schema_state"] != "PASS":
            reasons.append("REQUIRED_SCHEMA_FAILED")
        if acquisition_rows is not None and parquet_info["physical_row_count"] is not None:
            row_count_match = acquisition_rows == parquet_info["physical_row_count"]
            if not row_count_match:
                reasons.append("ROW_COUNT_MISMATCH")
        else:
            reasons.append("ROW_COUNT_NOT_COMPARABLE")
    elif event is not None and event.status == "DOWNLOADED_EMPTY":
        row_count_match = acquisition_rows == 0
        if not row_count_match:
            reasons.append("EMPTY_STATUS_WITH_NONZERO_ROWS")
    elif event is not None and event.status == "DOWNLOAD_FAIL":
        reasons.append("DOWNLOAD_FAILED")

    gate_pass = (
        event is not None
        and len(terminal_events) == 1
        and identity_pass
        and event.status in {"DOWNLOADED_OK", "DOWNLOADED_EMPTY"}
        and row_count_match is True
        and (
            event.status == "DOWNLOADED_EMPTY"
            or (
                parquet_info["physical_file_exists"]
                and parquet_info["physical_file_readable"]
                and parquet_info["required_schema_state"] == "PASS"
            )
        )
    )
    coverage_gate_state = "PASS_WITH_RESTRICTIONS" if gate_pass else "FAIL_UNAVAILABLE"
    zero_capability = (
        "CAN_ASSERT_WINDOW_ZERO_WITH_RESTRICTIONS" if gate_pass else "CANNOT_ASSERT_WINDOW_ZERO"
    )

    return {
        "task_key": task.task_key,
        "ticker": task.ticker,
        "trading_date": task.date,
        "session": task.session,
        "source_run_id": task.source_run_id,
        "source_dataset_id": SOURCE_DATASET_ID,
        "source_schema_version": parquet_info["source_schema_version"],
        "historical_expected_file": task.expected_file,
        "active_physical_file": str(active_file),
        "acquisition_status": status,
        "acquisition_rows": acquisition_rows,
        "terminal_event_count": len(terminal_events),
        "downloader_commit": downloader_commit,
        "downloader_content_hash": downloader_content_hash,
        "downloader_identity_state": "PASS" if identity_pass else "FAIL",
        "pagination_evidence_mode": PAGINATION_EVIDENCE_MODE if identity_pass else "UNAVAILABLE",
        "physical_file_exists": parquet_info["physical_file_exists"],
        "physical_file_readable": parquet_info["physical_file_readable"],
        "physical_row_count": parquet_info["physical_row_count"],
        "row_count_match": row_count_match,
        "required_schema_state": parquet_info["required_schema_state"],
        "schema_fingerprint": parquet_info["schema_fingerprint"],
        "physical_file_sha256": parquet_info["physical_file_sha256"],
        "acquisition_hash_comparison_state": "NOT_COMPARABLE_NO_EXPECTED_HASH",
        "coverage_gate_state": coverage_gate_state,
        "coverage_restriction_reason_codes": "|".join(sorted(set(reasons))),
        "window_zero_assertion_capability": zero_capability,
    }


def _iter_run_dirs(run_root: Path) -> Iterable[Path]:
    for path in sorted(run_root.iterdir()):
        if not path.is_dir():
            continue
        if (path / "expected_manifest_trades_ticks.csv").exists():
            yield path


def build_sidecar(
    *,
    run_root: Path,
    source_root: Path,
    output_dir: Path,
    run_id: str,
    max_tasks: int,
    downloader_commit: str,
    downloader_content_hash: str,
    hash_inputs: bool,
    hash_files: bool,
    overwrite: bool,
) -> dict[str, Any]:
    if not run_root.exists():
        raise FileNotFoundError(f"Missing run root: {run_root}")
    if not source_root.exists():
        raise FileNotFoundError(f"Missing source root: {source_root}")
    if max_tasks < 0:
        raise ValueError("max_tasks must be zero (all) or positive")

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{DATASET_ID}.csv"
    manifest_path = output_dir / f"{DATASET_ID}.manifest.json"
    if not overwrite and (csv_path.exists() or manifest_path.exists()):
        raise FileExistsError(f"Output exists; pass --overwrite: {output_dir}")

    rows: list[dict[str, Any]] = []
    input_artifacts: list[dict[str, Any]] = []
    remaining = max_tasks

    for run_dir in _iter_run_dirs(run_root):
        if max_tasks and remaining <= 0:
            break
        expected_path = run_dir / "expected_manifest_trades_ticks.csv"
        events_path = run_dir / "download_events_trades_ticks_current.csv"
        if not events_path.exists():
            raise FileNotFoundError(f"Missing current terminal events: {events_path}")

        expected = _read_expected_tasks(expected_path, run_dir.name)
        if max_tasks:
            expected = expected[:remaining]
        wanted = {task.task_key for task in expected}
        events = _read_terminal_events(events_path, wanted)
        for task in expected:
            rows.append(
                _evaluate_task(
                    task,
                    events.get(task.task_key, []),
                    source_root=source_root,
                    downloader_commit=downloader_commit,
                    downloader_content_hash=downloader_content_hash,
                    hash_files=hash_files,
                )
            )
        if max_tasks:
            remaining -= len(expected)

        input_artifacts.extend(
            [
                {
                    "path": str(expected_path),
                    "size_bytes": expected_path.stat().st_size,
                    "sha256": _sha256_file(expected_path) if hash_inputs else "NOT_COMPUTED_PILOT",
                },
                {
                    "path": str(events_path),
                    "size_bytes": events_path.stat().st_size,
                    "sha256": _sha256_file(events_path) if hash_inputs else "NOT_COMPUTED_PILOT",
                },
            ]
        )

    rows.sort(key=lambda row: (row["source_run_id"], row["task_key"]))
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    state_counts: dict[str, int] = {}
    for row in rows:
        state = str(row["coverage_gate_state"])
        state_counts[state] = state_counts.get(state, 0) + 1

    manifest = {
        "dataset_id": DATASET_ID,
        "specification_version": SPECIFICATION_VERSION,
        "run_id": run_id,
        "created_at_utc": _utc_now_iso(),
        "scope_id": "legacy_rth_reconciled_event_time_research_only",
        "source_dataset_id": SOURCE_DATASET_ID,
        "source_root": str(source_root),
        "run_root": str(run_root),
        "audited_downloader_commit": downloader_commit,
        "audited_downloader_content_hash": downloader_content_hash,
        "downloader_identity_matches": (
            downloader_commit == AUDITED_DOWNLOADER_COMMIT
            and downloader_content_hash == AUDITED_DOWNLOADER_CONTENT_HASH
        ),
        "pagination_evidence_mode": PAGINATION_EVIDENCE_MODE,
        "pilot_max_tasks": max_tasks,
        "full_universe_claim": False,
        "hash_inputs": hash_inputs,
        "hash_files": hash_files,
        "row_count": len(rows),
        "coverage_gate_state_counts": state_counts,
        "output_csv": str(csv_path),
        "output_csv_sha256": _sha256_file(csv_path),
        "input_artifacts": input_artifacts,
        "massive_backfill_state": "DEFERRED_PENDING_MASSIVE_BACKFILL",
        "canonical_promotion": "NOT_AUTHORIZED",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"csv": str(csv_path), "manifest": str(manifest_path), "summary": manifest}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--max-tasks", type=int, default=0, help="0 means all tasks")
    parser.add_argument("--downloader-commit", default=AUDITED_DOWNLOADER_COMMIT)
    parser.add_argument("--downloader-content-hash", default=AUDITED_DOWNLOADER_CONTENT_HASH)
    parser.add_argument("--hash-inputs", action="store_true")
    parser.add_argument("--hash-files", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    result = build_sidecar(
        run_root=args.run_root,
        source_root=args.source_root,
        output_dir=args.output_dir,
        run_id=args.run_id,
        max_tasks=args.max_tasks,
        downloader_commit=args.downloader_commit,
        downloader_content_hash=args.downloader_content_hash,
        hash_inputs=bool(args.hash_inputs),
        hash_files=bool(args.hash_files),
        overwrite=bool(args.overwrite),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

