"""Offline post-download auditor for a hash-authorized SEC PIT acquisition run.

The auditor never performs network requests and never mutates the acquisition
run or the content-addressed store.  It reconciles the frozen authorization,
selection plan, acquisition/performance JSONL and referenced CAS objects.  Its
own output is a separate, resumable, long-running-operation evidence root.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import socket
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import psutil

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.authorization import file_sha256
from sec_pit.storage import append_jsonl, atomic_write_json
from sec_pit.telemetry import percentile

AUDITOR_VERSION = "sec_pit_authorized_primary_postdownload_audit_v0_1"
TERMINAL_RUN_STATUSES = {"COMPLETE", "FAILED", "STOPPED_LOW_DISK", "INTERRUPTED"}
ELIGIBLE_GATE_STATES = {
    "ELIGIBLE_FOR_GOVERNED_REVIEW",
    "ELIGIBLE_FOR_REVIEW_NOT_AUTHORIZED",
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def iter_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                yield line_number, json.loads(line)


def quantiles(values: Iterable[float | int]) -> dict[str, float | int | None]:
    data = [float(value) for value in values]
    if not data:
        return {"count": 0, "p50": None, "p95": None, "max": None}
    maximum = max(data)
    if all(value.is_integer() for value in data):
        maximum = int(maximum)
    return {
        "count": len(data),
        "p50": percentile(data, 0.50),
        "p95": percentile(data, 0.95),
        "max": maximum,
    }


def git_state(repo_root: Path) -> dict[str, Any]:
    def run(*args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    status = run("status", "--short")
    return {
        "branch": run("branch", "--show-current"),
        "commit": run("rev-parse", "HEAD"),
        "dirty": bool(status),
        "dirty_paths": status.splitlines(),
    }


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def planned_logical_path(row: dict[str, Any]) -> str:
    url = str(row["primary_document_url"])
    filename = Path(urlparse(url).path).name or "primary.bin"
    return f"primary/{row['ticker']}/{row['accession_number']}/{filename}"


def summarize_plan(
    selection: pd.DataFrame,
    gates: pd.DataFrame,
    authorization: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    allowed = [str(value).strip().upper() for value in authorization.get("allowed_tickers", [])]
    allowed_count = int(authorization.get("allowed_ticker_count") or len(allowed))
    gate_state = gates["primary_document_acquisition_state"].astype(str)
    eligible = set(
        gates.loc[gate_state.isin(ELIGIBLE_GATE_STATES), "ticker"]
        .astype(str)
        .str.upper()
    )
    order = (
        selection[["ticker", "cohort_selection_order"]]
        .drop_duplicates()
        .assign(ticker=lambda value: value["ticker"].astype(str).str.upper())
        .sort_values(["cohort_selection_order", "ticker"])
    )
    ordered_eligible = [
        str(row.ticker) for row in order.itertuples(index=False) if str(row.ticker) in eligible
    ]
    expected_allowed = ordered_eligible[:allowed_count]
    if len(allowed) != allowed_count:
        issues.append({"code": "AUTHORIZATION_ALLOWED_COUNT_MISMATCH"})
    if len(set(allowed)) != len(allowed):
        issues.append({"code": "AUTHORIZATION_DUPLICATE_TICKER"})
    if allowed != expected_allowed:
        issues.append(
            {
                "code": "AUTHORIZATION_NOT_EXACT_FIRST_ELIGIBLE_ROWS",
                "expected_first": expected_allowed[:5],
                "actual_first": allowed[:5],
                "expected_last": expected_allowed[-5:],
                "actual_last": allowed[-5:],
            }
        )
    if not set(allowed).issubset(eligible):
        issues.append({"code": "AUTHORIZATION_CONTAINS_INELIGIBLE_TICKER"})
    planned = selection.loc[
        selection["ticker"].astype(str).str.upper().isin(set(allowed))
    ].copy()
    records = planned.to_dict("records")
    for index, row in enumerate(records, start=1):
        row["selection_index"] = index
        row["ticker"] = str(row["ticker"]).upper()
        row["primary_document_url"] = str(row["primary_document_url"])
        row["logical_path"] = planned_logical_path(row)
        row["filing_year"] = str(row.get("filing_date") or "")[:4] or "UNKNOWN"
    if len(records) != int(authorization.get("planned_document_count") or -1):
        issues.append(
            {
                "code": "AUTHORIZED_PLAN_COUNT_MISMATCH",
                "recalculated": len(records),
                "authorization": authorization.get("planned_document_count"),
            }
        )
    identities = [
        (row["ticker"], str(row["accession_number"]), row["primary_document_url"])
        for row in records
    ]
    if len(identities) != len(set(identities)):
        issues.append({"code": "AUTHORIZED_PLAN_DUPLICATE_IDENTITY"})
    blocked = sorted(set(order["ticker"].astype(str)) - set(allowed))
    summary = {
        "c01_rows": int(len(gates)),
        "technically_eligible_rows": len(ordered_eligible),
        "authorized_rows": len(allowed),
        "blocked_or_unapproved_rows": len(blocked),
        "authorized_document_count": len(records),
        "authorized_first_ticker": allowed[0] if allowed else None,
        "authorized_last_ticker": allowed[-1] if allowed else None,
        "gate_state_counts": {
            str(key): int(value)
            for key, value in gates["primary_document_acquisition_state"]
            .value_counts(dropna=False)
            .items()
        },
    }
    return records, summary, issues


def reconcile_logs(
    plan: list[dict[str, Any]],
    acquisition_path: Path,
    performance_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    fallback_details: list[dict[str, Any]] = []
    {
        (row["primary_document_url"], row["logical_path"]): row for row in plan
    }
    plan_by_index = {int(row["selection_index"]): row for row in plan}
    acquisition_by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    all_acquisition: list[dict[str, Any]] = []
    acquisition_status = Counter()
    acquisition_http = Counter()
    acquisition_invalid = 0
    for line_number, row in iter_jsonl(acquisition_path):
        row["_line_number"] = line_number
        all_acquisition.append(row)
        acquisition_status[str(row.get("status"))] += 1
        acquisition_http[str(row.get("http_status"))] += 1
        key = (str(row.get("url") or ""), str(row.get("logical_path") or ""))
        acquisition_by_key[key].append(row)
        if not row.get("url") or not row.get("status"):
            acquisition_invalid += 1

    final_records: list[dict[str, Any]] = []
    recognized_lines: set[int] = set()
    ticker_docs = Counter()
    ticker_bytes = Counter()
    fallback_actual_keys: set[tuple[str, str]] = set()
    for expected in plan:
        key = (expected["primary_document_url"], expected["logical_path"])
        rows = acquisition_by_key.get(key, [])
        fetched = [row for row in rows if row.get("status") == "FETCHED"]
        failed = [row for row in rows if row.get("status") == "FAILED"]
        if len(fetched) != 1:
            issues.append(
                {
                    "code": "EXPECTED_IDENTITY_FETCHED_CARDINALITY",
                    "ticker": expected["ticker"],
                    "accession_number": expected["accession_number"],
                    "url": expected["primary_document_url"],
                    "fetched_rows": len(fetched),
                    "failed_rows": len(failed),
                }
            )
            continue
        terminal = fetched[0]
        recognized_lines.add(int(terminal["_line_number"]))
        for failed_row in failed:
            recognized_lines.add(int(failed_row["_line_number"]))
        if failed:
            if len(failed) != 1 or failed[0].get("http_status") != 404:
                issues.append(
                    {
                        "code": "UNCONTROLLED_PRIMARY_FAILURE_PATTERN",
                        "ticker": expected["ticker"],
                        "accession_number": expected["accession_number"],
                    }
                )
            fallback_url = str(terminal.get("fallback_resolved_url") or "")
            fallback_logical = (
                f"complete_submission_fallback/{expected['ticker']}/"
                f"{expected['accession_number']}.txt"
            )
            fallback_key = (fallback_url, fallback_logical)
            actual_rows = acquisition_by_key.get(fallback_key, [])
            if len(actual_rows) != 1 or actual_rows[0].get("status") != "FETCHED":
                issues.append(
                    {
                        "code": "FALLBACK_FETCH_RECORD_MISSING_OR_DUPLICATED",
                        "ticker": expected["ticker"],
                        "accession_number": expected["accession_number"],
                    }
                )
            else:
                actual = actual_rows[0]
                recognized_lines.add(int(actual["_line_number"]))
                fallback_actual_keys.add(fallback_key)
                for field in ("sha256", "object_path", "bytes"):
                    if terminal.get(field) != actual.get(field):
                        issues.append(
                            {
                                "code": "FALLBACK_ALIAS_CONTENT_MISMATCH",
                                "field": field,
                                "ticker": expected["ticker"],
                                "accession_number": expected["accession_number"],
                            }
                        )
                fallback_details.append(
                    {
                        "selection_index": expected["selection_index"],
                        "ticker": expected["ticker"],
                        "accession_number": expected["accession_number"],
                        "form": str(expected.get("form") or ""),
                        "filing_year": expected["filing_year"],
                        "primary_url": expected["primary_document_url"],
                        "primary_http_status": failed[0].get("http_status"),
                        "fallback_url": fallback_url,
                        "sha256": terminal.get("sha256"),
                        "bytes": int(terminal.get("bytes") or 0),
                    }
                )
        elif terminal.get("fallback_resolved_url"):
            issues.append(
                {
                    "code": "FALLBACK_ALIAS_WITHOUT_PRIMARY_FAILURE",
                    "ticker": expected["ticker"],
                    "accession_number": expected["accession_number"],
                }
            )
        terminal["_selection_index"] = expected["selection_index"]
        terminal["_ticker"] = expected["ticker"]
        terminal["_accession_number"] = expected["accession_number"]
        terminal["_form"] = str(expected.get("form") or "")
        terminal["_filing_year"] = expected["filing_year"]
        final_records.append(terminal)
        ticker_docs[expected["ticker"]] += 1
        ticker_bytes[expected["ticker"]] += int(terminal.get("bytes") or 0)

    unrecognized = [
        row for row in all_acquisition if int(row["_line_number"]) not in recognized_lines
    ]
    for row in unrecognized[:100]:
        issues.append(
            {
                "code": "UNRECOGNIZED_ACQUISITION_ROW",
                "line_number": row["_line_number"],
                "status": row.get("status"),
                "url": row.get("url"),
                "logical_path": row.get("logical_path"),
            }
        )
    if len(unrecognized) > 100:
        issues.append(
            {"code": "UNRECOGNIZED_ACQUISITION_ROWS_TRUNCATED", "count": len(unrecognized)}
        )

    performance_by_index: dict[int, list[dict[str, Any]]] = defaultdict(list)
    performance_status = Counter()
    performance_http = Counter()
    performance_retry_total = 0
    performance_http_429_total = 0
    for line_number, row in iter_jsonl(performance_path):
        row["_line_number"] = line_number
        index = int(row.get("selection_index") or 0)
        performance_by_index[index].append(row)
        performance_status[str(row.get("status"))] += 1
        performance_http[str(row.get("http_status"))] += 1
        performance_retry_total += int(row.get("retry_count") or 0)
        performance_http_429_total += int(row.get("http_429_count") or 0)

    logical_latencies: list[float] = []
    logical_retries: list[int] = []
    logical_http_429: list[int] = []
    logical_terminal_failed = 0
    failed_call_retries = 0
    for index, expected in plan_by_index.items():
        rows = performance_by_index.get(index, [])
        if not rows:
            issues.append(
                {
                    "code": "PERFORMANCE_SELECTION_INDEX_MISSING",
                    "selection_index": index,
                }
            )
            continue
        if any(str(row.get("ticker") or "").upper() != expected["ticker"] for row in rows):
            issues.append(
                {"code": "PERFORMANCE_TICKER_MISMATCH", "selection_index": index}
            )
        if any(str(row.get("accession_number") or "") != str(expected["accession_number"]) for row in rows):
            issues.append(
                {"code": "PERFORMANCE_ACCESSION_MISMATCH", "selection_index": index}
            )
        terminal = rows[-1]
        logical_terminal_failed += terminal.get("status") != "FETCHED"
        logical_latencies.append(sum(float(row.get("total_seconds") or 0.0) for row in rows))
        logical_retries.append(sum(int(row.get("retry_count") or 0) for row in rows))
        logical_http_429.append(sum(int(row.get("http_429_count") or 0) for row in rows))
        failed_call_retries += sum(
            int(row.get("retry_count") or 0)
            for row in rows
            if row.get("status") == "FAILED"
        )
        failed_rows = [row for row in rows if row.get("status") == "FAILED"]
        if failed_rows:
            if not (
                len(rows) == 2
                and len(failed_rows) == 1
                and rows[0].get("http_status") == 404
                and rows[1].get("status") == "FETCHED"
                and rows[1].get("fallback_policy_id")
            ):
                issues.append(
                    {"code": "PERFORMANCE_UNRESOLVED_FAILURE_PATTERN", "selection_index": index}
                )
    unexpected_indices = sorted(set(performance_by_index) - set(plan_by_index) - {0})
    if unexpected_indices:
        issues.append(
            {
                "code": "PERFORMANCE_UNEXPECTED_SELECTION_INDEX",
                "count": len(unexpected_indices),
                "sample": unexpected_indices[:20],
            }
        )

    fallback_by_form = Counter(row["form"] for row in fallback_details)
    fallback_by_year = Counter(row["filing_year"] for row in fallback_details)
    fallback_by_ticker = Counter(row["ticker"] for row in fallback_details)
    summary = {
        "acquisition_rows": len(all_acquisition),
        "acquisition_status_counts": dict(acquisition_status),
        "acquisition_http_status_counts": dict(acquisition_http),
        "acquisition_invalid_rows": acquisition_invalid,
        "recalculated_terminal_documents": len(final_records),
        "recalculated_terminal_failures": len(plan) - len(final_records),
        "recalculated_bytes": sum(int(row.get("bytes") or 0) for row in final_records),
        "performance_rows": sum(performance_status.values()),
        "performance_status_counts": dict(performance_status),
        "performance_http_status_counts": dict(performance_http),
        "performance_retry_total": performance_retry_total,
        "performance_http_429_total": performance_http_429_total,
        "logical_terminal_failures": logical_terminal_failed,
        "resolved_primary_404_fallbacks": len(fallback_details),
        "unresolved_raw_fetch_failures": max(
            0, int(performance_status.get("FAILED", 0)) - len(fallback_details)
        ),
        "failed_primary_call_retries": failed_call_retries,
        "document_bytes": quantiles(int(row.get("bytes") or 0) for row in final_records),
        "documents_per_ticker": quantiles(ticker_docs.values()),
        "bytes_per_ticker": quantiles(ticker_bytes.values()),
        "logical_document_latency_seconds": quantiles(logical_latencies),
        "logical_document_retries": quantiles(logical_retries),
        "logical_documents_with_retry": sum(value > 0 for value in logical_retries),
        "logical_http_429_total": sum(logical_http_429),
        "fallback_by_form": dict(sorted(fallback_by_form.items())),
        "fallback_by_year": dict(sorted(fallback_by_year.items())),
        "fallback_by_ticker": dict(sorted(fallback_by_ticker.items())),
        "unrecognized_acquisition_rows": len(unrecognized),
        "recognized_fallback_actual_keys": len(fallback_actual_keys),
    }
    return summary, final_records, fallback_details, issues


def verify_cas_object(item: dict[str, Any], object_root: Path) -> dict[str, Any]:
    path = Path(str(item["object_path"]))
    expected_sha = str(item["sha256"])
    expected_bytes = int(item["bytes"])
    result = {
        "object_path": path.as_posix(),
        "sha256": expected_sha,
        "expected_bytes": expected_bytes,
        "status": "FAIL",
        "error": None,
    }
    try:
        if not path_is_within(path, object_root):
            raise ValueError("OBJECT_PATH_OUTSIDE_GOVERNED_CAS")
        if not path.is_file():
            raise FileNotFoundError(path)
        name_digest = path.name.split(".", 1)[0]
        if name_digest != expected_sha:
            raise ValueError("OBJECT_FILENAME_SHA_MISMATCH")
        if path.parent.name != expected_sha[2:4] or path.parent.parent.name != expected_sha[:2]:
            raise ValueError("OBJECT_SHARD_PATH_MISMATCH")
        digest = hashlib.sha256()
        actual_bytes = 0
        opener = gzip.open if path.suffix.lower() == ".gz" else Path.open
        if opener is gzip.open:
            handle_context = gzip.open(path, "rb")
        else:
            handle_context = path.open("rb")
        with handle_context as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                actual_bytes += len(chunk)
        actual_sha = digest.hexdigest()
        if actual_sha != expected_sha:
            raise ValueError("OBJECT_CONTENT_SHA_MISMATCH")
        if actual_bytes != expected_bytes:
            raise ValueError("OBJECT_UNCOMPRESSED_SIZE_MISMATCH")
        stat = path.stat()
        result.update(
            {
                "status": "PASS",
                "actual_bytes": actual_bytes,
                "stored_bytes": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
            }
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


class AuditTelemetry:
    def __init__(self, audit_root: Path, run_id: str, interval_seconds: float) -> None:
        self.audit_root = audit_root
        self.run_id = run_id
        self.interval_seconds = interval_seconds
        self.started = time.monotonic()
        self.stage = "INITIALIZING"
        self.current = 0
        self.total = 0
        self.current_item: str | None = None
        self.failures = 0
        self.bytes_verified = 0
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self.sample()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            self.sample()

    def update(
        self,
        *,
        stage: str | None = None,
        current: int | None = None,
        total: int | None = None,
        current_item: str | None = None,
        failures: int | None = None,
        bytes_verified: int | None = None,
    ) -> None:
        with self._lock:
            if stage is not None:
                self.stage = stage
            if current is not None:
                self.current = current
            if total is not None:
                self.total = total
            if current_item is not None:
                self.current_item = current_item
            if failures is not None:
                self.failures = failures
            if bytes_verified is not None:
                self.bytes_verified = bytes_verified

    def snapshot(self, status: str = "RUNNING") -> dict[str, Any]:
        with self._lock:
            stage = self.stage
            current = self.current
            total = self.total
            current_item = self.current_item
            failures = self.failures
            bytes_verified = self.bytes_verified
        process = psutil.Process(os.getpid())
        memory = process.memory_info()
        return {
            "run_id": self.run_id,
            "status": status,
            "stage": stage,
            "observed_at_utc": utc_now(),
            "elapsed_seconds": time.monotonic() - self.started,
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": status == "RUNNING",
            "current_index": current,
            "total_count": total,
            "progress_percent": (current / total * 100.0) if total else None,
            "current_item": current_item,
            "failures": failures,
            "bytes_verified": bytes_verified,
            "process_rss_gib": memory.rss / (1024**3),
        }

    def sample(self, status: str = "RUNNING") -> dict[str, Any]:
        heartbeat = self.snapshot(status)
        atomic_write_json(self.audit_root / "heartbeat_latest.json", heartbeat)
        append_jsonl(self.audit_root / "heartbeat.jsonl", heartbeat)
        return heartbeat

    def stop(self, status: str) -> dict[str, Any]:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.interval_seconds + 2.0)
        return self.sample(status)


def verify_cas(
    final_records: list[dict[str, Any]],
    object_root: Path,
    audit_root: Path,
    telemetry: AuditTelemetry,
    workers: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    by_path: dict[str, dict[str, Any]] = {}
    sha_paths: dict[str, set[str]] = defaultdict(set)
    for row in final_records:
        path = str(row.get("object_path") or "")
        sha = str(row.get("sha256") or "")
        byte_count = int(row.get("bytes") or 0)
        if not path or not sha:
            issues.append(
                {
                    "code": "TERMINAL_FETCH_WITHOUT_CAS_IDENTITY",
                    "ticker": row.get("_ticker"),
                    "accession_number": row.get("_accession_number"),
                }
            )
            continue
        existing = by_path.get(path)
        if existing and (
            existing["sha256"] != sha or int(existing["bytes"]) != byte_count
        ):
            issues.append({"code": "CAS_PATH_REFERENCED_WITH_CONFLICTING_METADATA", "path": path})
        by_path[path] = {"object_path": path, "sha256": sha, "bytes": byte_count}
        sha_paths[sha].add(path)
    items = [by_path[key] for key in sorted(by_path)]
    checkpoint = audit_root / "cas_verification.jsonl"
    completed: dict[str, dict[str, Any]] = {}
    if checkpoint.is_file():
        for _, row in iter_jsonl(checkpoint):
            if row.get("status") == "PASS":
                path = Path(str(row.get("object_path") or ""))
                try:
                    stat = path.stat()
                except OSError:
                    continue
                if (
                    int(row.get("stored_bytes") or -1) == stat.st_size
                    and int(row.get("mtime_ns") or -1) == stat.st_mtime_ns
                ):
                    completed[str(path)] = row
    pending = [item for item in items if item["object_path"] not in completed]
    total = len(items)
    pass_count = len(completed)
    fail_count = 0
    verified_uncompressed = sum(int(row.get("actual_bytes") or 0) for row in completed.values())
    telemetry.update(
        stage="CAS_FULL_SHA256",
        current=pass_count,
        total=total,
        failures=fail_count,
        bytes_verified=verified_uncompressed,
    )
    if pending:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            for result in executor.map(
                lambda item: verify_cas_object(item, object_root), pending
            ):
                append_jsonl(checkpoint, result)
                if result["status"] == "PASS":
                    pass_count += 1
                    verified_uncompressed += int(result.get("actual_bytes") or 0)
                else:
                    fail_count += 1
                    issues.append(
                        {
                            "code": "CAS_OBJECT_VERIFICATION_FAILED",
                            "object_path": result["object_path"],
                            "error": result["error"],
                        }
                    )
                telemetry.update(
                    current=pass_count + fail_count,
                    current_item=result["object_path"],
                    failures=fail_count,
                    bytes_verified=verified_uncompressed,
                )
                if (pass_count + fail_count) % 250 == 0:
                    telemetry.sample()
    results: dict[str, dict[str, Any]] = {}
    for _, row in iter_jsonl(checkpoint):
        results[str(row.get("object_path"))] = row
    final_pass = sum(row.get("status") == "PASS" for row in results.values())
    final_fail = sum(row.get("status") != "PASS" for row in results.values())
    stored_bytes = sum(
        int(row.get("stored_bytes") or 0)
        for row in results.values()
        if row.get("status") == "PASS"
    )
    return (
        {
            "mode": "FULL_REFERENCED_CAS",
            "logical_document_references": len(final_records),
            "unique_object_paths": total,
            "unique_sha256": len(sha_paths),
            "sha256_with_multiple_object_paths": sum(
                len(paths) > 1 for paths in sha_paths.values()
            ),
            "verified_pass": final_pass,
            "verified_fail": final_fail,
            "verified_uncompressed_bytes": sum(
                int(row.get("actual_bytes") or 0)
                for row in results.values()
                if row.get("status") == "PASS"
            ),
            "referenced_stored_bytes": stored_bytes,
            "deduplicated_logical_references": len(final_records) - total,
        },
        issues,
    )


def scan_heartbeat(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    count = 0
    wrapper_pids: set[int] = set()
    totals: set[int] = set()
    previous_index = -1
    regressions = 0
    first_observed = last_observed = None
    min_free = math.inf
    max_rss = 0.0
    for _, row in iter_jsonl(path):
        count += 1
        first_observed = first_observed or row.get("observed_at_utc")
        last_observed = row.get("observed_at_utc")
        if row.get("wrapper_pid") is not None:
            wrapper_pids.add(int(row["wrapper_pid"]))
        if row.get("total_count") is not None:
            totals.add(int(row["total_count"]))
        index = int(row.get("current_index") or 0)
        if index < previous_index:
            regressions += 1
        previous_index = max(previous_index, index)
        if row.get("output_free_gib") is not None:
            min_free = min(min_free, float(row["output_free_gib"]))
        max_rss = max(max_rss, float(row.get("process_tree_rss_gib") or 0.0))
    if len(wrapper_pids) != 1:
        issues.append({"code": "HEARTBEAT_MULTIPLE_WRAPPER_PIDS", "pids": sorted(wrapper_pids)})
    if len(totals) != 1:
        issues.append({"code": "HEARTBEAT_TOTAL_COUNT_DRIFT", "totals": sorted(totals)})
    if regressions:
        issues.append({"code": "HEARTBEAT_PROGRESS_REGRESSION", "count": regressions})
    return (
        {
            "rows": count,
            "wrapper_pids": sorted(wrapper_pids),
            "total_counts": sorted(totals),
            "progress_regressions": regressions,
            "first_observed_at_utc": first_observed,
            "last_observed_at_utc": last_observed,
            "minimum_output_free_gib": None if min_free is math.inf else min_free,
            "max_process_tree_rss_gib": max_rss,
        },
        issues,
    )


def duration_seconds(start: str, end: str) -> float:
    return (
        datetime.fromisoformat(end.replace("Z", "+00:00"))
        - datetime.fromisoformat(start.replace("Z", "+00:00"))
    ).total_seconds()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--probe-root", type=Path, required=True)
    parser.add_argument("--object-root", type=Path, required=True)
    parser.add_argument("--audit-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(r"C:\TSIS_Data"))
    parser.add_argument("--cas-workers", type=int, default=2)
    parser.add_argument("--heartbeat-interval-seconds", type=float, default=10.0)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = args.run_root.resolve()
    probe_root = args.probe_root.resolve()
    object_root = args.object_root.resolve()
    audit_root = args.audit_root.resolve()
    if audit_root.exists() and not args.resume:
        raise FileExistsError(f"Audit root exists; use --resume: {audit_root}")
    audit_root.mkdir(parents=True, exist_ok=True)
    required_run = [
        "pre_manifest.json",
        "pid_manifest.json",
        "heartbeat_latest.json",
        "heartbeat.jsonl",
        "acquisition.jsonl",
        "document_performance.jsonl",
        "run.log",
        "performance_summary.json",
        "final_manifest.json",
    ]
    for name in required_run:
        if not (run_root / name).is_file():
            raise FileNotFoundError(run_root / name)
    final = load_json(run_root / "final_manifest.json")
    wrapper_pid = int(final.get("wrapper_pid") or 0)
    wrapper_alive = bool(wrapper_pid and psutil.pid_exists(wrapper_pid))
    if final.get("status") not in TERMINAL_RUN_STATUSES or wrapper_alive:
        print("AUDIT_NOT_STARTED_RUN_NOT_TERMINAL")
        print(
            json.dumps(
                {
                    "final_manifest_status": final.get("status"),
                    "wrapper_pid": wrapper_pid,
                    "wrapper_alive": wrapper_alive,
                },
                indent=2,
            )
        )
        return 3

    monitor = (
        "Get-Content -Wait -Tail 1 -LiteralPath "
        f"'{(audit_root / 'heartbeat.jsonl').as_posix()}'"
    )
    pre_manifest = {
        "audit_id": audit_root.name,
        "auditor_version": AUDITOR_VERSION,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": file_sha256(Path(__file__).resolve()),
        "command_line": subprocess.list2cmdline(sys.argv),
        "cwd": Path.cwd().as_posix(),
        "host": socket.gethostname(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "wrapper_pid": os.getpid(),
        "git": git_state(args.repo_root.resolve()),
        "mode": "FULL_REFERENCED_CAS_OFFLINE",
        "network_access": "PROHIBITED_AND_NOT_USED",
        "input_roots": {
            "run_root": run_root.as_posix(),
            "probe_root": probe_root.as_posix(),
            "object_root": object_root.as_posix(),
            "authorization": args.authorization.resolve().as_posix(),
        },
        "output_root": audit_root.as_posix(),
        "expected_scope": {
            "ticker_rows": final.get("allowed_tickers") and len(final["allowed_tickers"]),
            "documents": final.get("planned"),
        },
        "resume_policy": "reuse PASS CAS checkpoints only when size and mtime_ns are unchanged",
        "overwrite_policy": "acquisition run and CAS are read-only; audit outputs are separate",
        "success_criteria": "all six audit gates PASS",
        "monitor_command": monitor,
    }
    if not (audit_root / "pre_manifest.json").is_file():
        atomic_write_json(audit_root / "pre_manifest.json", pre_manifest)
    atomic_write_json(
        audit_root / "pid_manifest.json",
        {
            "wrapper_pid": os.getpid(),
            "started_at_utc": utc_now(),
            "stage": "INITIALIZING",
            "expected_alive": True,
        },
    )
    print(f"audit_root={audit_root}")
    print(f"monitor={monitor}")
    telemetry = AuditTelemetry(
        audit_root,
        audit_root.name,
        args.heartbeat_interval_seconds,
    )
    telemetry.start()
    started = time.monotonic()
    all_issues: list[dict[str, Any]] = []
    try:
        telemetry.update(stage="INPUT_AND_SCOPE_RECONCILIATION")
        authorization = load_json(args.authorization.resolve())
        probe_manifest_path = probe_root / "final_manifest.json"
        selection_path = probe_root / "document_selection_plan_v0_2.parquet"
        gates_path = probe_root / "gate_matrix.parquet"
        selection = pd.read_parquet(selection_path)
        gates = pd.read_parquet(gates_path)
        plan, scope, plan_issues = summarize_plan(selection, gates, authorization)
        all_issues.extend(plan_issues)
        input_hashes = {
            "authorization": file_sha256(args.authorization.resolve()),
            "probe_manifest": file_sha256(probe_manifest_path),
            "selection_plan": file_sha256(selection_path),
            "gate_matrix": file_sha256(gates_path),
        }
        expected_hashes = {
            "authorization": final.get("authorization_sha256"),
            "probe_manifest": final.get("probe_manifest_sha256"),
            "selection_plan": final.get("selection_plan_sha256"),
            "gate_matrix": final.get("gate_matrix_sha256"),
        }
        for name, actual in input_hashes.items():
            if actual != expected_hashes[name] or actual != authorization.get(
                {
                    "probe_manifest": "probe_manifest_sha256",
                    "selection_plan": "selection_plan_sha256",
                    "gate_matrix": "gate_matrix_sha256",
                    "authorization": "_not_present",
                }[name]
            ) and name != "authorization":
                all_issues.append(
                    {
                        "code": "FROZEN_INPUT_HASH_MISMATCH",
                        "artifact": name,
                        "actual": actual,
                        "expected": expected_hashes[name],
                    }
                )
        telemetry.update(stage="ACQUISITION_AND_PERFORMANCE_RECONCILIATION")
        log_summary, final_records, fallbacks, log_issues = reconcile_logs(
            plan,
            run_root / "acquisition.jsonl",
            run_root / "document_performance.jsonl",
        )
        all_issues.extend(log_issues)
        heartbeat_summary, heartbeat_issues = scan_heartbeat(run_root / "heartbeat.jsonl")
        all_issues.extend(heartbeat_issues)
        for path in (run_root / "run.log",):
            line_count = sum(1 for _ in path.open("r", encoding="utf-8"))
            heartbeat_summary["run_log_rows"] = line_count

        telemetry.update(stage="CAS_FULL_SHA256")
        cas_summary, cas_issues = verify_cas(
            final_records,
            object_root,
            audit_root,
            telemetry,
            args.cas_workers,
        )
        all_issues.extend(cas_issues)

        for target in (audit_root / "fallback_records.jsonl", audit_root / "issues.jsonl"):
            target.unlink(missing_ok=True)
        for row in fallbacks:
            append_jsonl(audit_root / "fallback_records.jsonl", row)
        for row in all_issues:
            append_jsonl(audit_root / "issues.jsonl", row)

        pre_run = load_json(run_root / "pre_manifest.json")
        component_stable = pre_run.get("component_sha256") == final.get("component_sha256")
        current_component_hashes: dict[str, str | None] = {}
        current_component_drift: dict[str, dict[str, str | None]] = {}
        for name, frozen_hash in (final.get("component_sha256") or {}).items():
            path = SCRIPT_DIR / name
            actual = file_sha256(path) if path.is_file() else None
            current_component_hashes[name] = actual
            if actual != frozen_hash:
                current_component_drift[name] = {
                    "frozen": frozen_hash,
                    "current": actual,
                }
        manifest_reconciliation = {
            "planned": [final.get("planned"), len(plan)],
            "fetched": [final.get("fetched"), log_summary["recalculated_terminal_documents"]],
            "failed": [final.get("failed"), log_summary["logical_terminal_failures"]],
            "bytes_fetched": [final.get("bytes_fetched"), log_summary["recalculated_bytes"]],
            "retry_count_manifest": final.get("retry_count"),
            "retry_count_all_fetch_calls": log_summary["performance_retry_total"],
            "retry_count_recovered_primary_failures": log_summary[
                "failed_primary_call_retries"
            ],
            "http_429": [final.get("http_429_count"), log_summary["performance_http_429_total"]],
            "performance_failed_is_raw_fetch_calls": log_summary[
                "performance_status_counts"
            ].get("FAILED", 0),
            "resolved_primary_404_fallbacks": log_summary[
                "resolved_primary_404_fallbacks"
            ],
        }
        manifest_counts_match = all(
            pair[0] == pair[1]
            for name, pair in manifest_reconciliation.items()
            if isinstance(pair, list) and name != "retry_count"
        )
        hard_issue_codes = {row["code"] for row in all_issues}
        scope_fail = any(
            code.startswith("AUTHORIZATION_")
            or code.startswith("AUTHORIZED_PLAN_")
            or code in {"UNRECOGNIZED_ACQUISITION_ROW", "UNRECOGNIZED_ACQUISITION_ROWS_TRUNCATED"}
            for code in hard_issue_codes
        )
        acquisition_fail = (
            not manifest_counts_match
            or log_summary["logical_terminal_failures"] != 0
            or log_summary["unresolved_raw_fetch_failures"] != 0
            or any(
                code.startswith("EXPECTED_IDENTITY_")
                or code.startswith("UNCONTROLLED_")
                or code.startswith("FALLBACK_")
                or code.startswith("PERFORMANCE_")
                for code in hard_issue_codes
            )
        )
        cas_fail = cas_summary["verified_fail"] != 0 or (
            cas_summary["verified_pass"] != cas_summary["unique_object_paths"]
        )
        resume_control_findings = []
        required_pre_manifest_fields = ("command_line", "cwd", "git_branch", "git_commit", "git_dirty_state")
        missing_pre_fields = [name for name in required_pre_manifest_fields if name not in pre_run]
        if missing_pre_fields:
            resume_control_findings.append(
                {"code": "RUN_PREMANIFEST_MISSING_REPRODUCIBILITY_FIELDS", "fields": missing_pre_fields}
            )
        if current_component_drift:
            resume_control_findings.append(
                {
                    "code": "CURRENT_SOURCE_DIFFERS_FROM_EXECUTED_COMPONENT_HASHES",
                    "components": sorted(current_component_drift),
                }
            )
        resume_gate = "PASS"
        if not component_stable or missing_pre_fields or current_component_drift:
            resume_gate = "FAIL"
        if heartbeat_summary["wrapper_pids"] != [wrapper_pid]:
            resume_gate = "FAIL"

        duration = duration_seconds(final["created_at_utc"], final["ended_at_utc"])
        bytes_fetched = int(log_summary["recalculated_bytes"])
        performance = load_json(run_root / "performance_summary.json")
        performance_readout = {
            "status": "COMPLETE_WITH_TELEMETRY_LIMITATIONS",
            "wall_duration_seconds": duration,
            "documents_per_minute": len(plan) / (duration / 60.0),
            "mib_per_minute": (bytes_fetched / (1024**2)) / (duration / 60.0),
            "uncompressed_bytes": bytes_fetched,
            "referenced_stored_bytes": cas_summary["referenced_stored_bytes"],
            "free_space_gib_at_start": final.get("free_space_gib_at_start"),
            "minimum_free_space_gib_observed": heartbeat_summary["minimum_output_free_gib"],
            "peak_rss_gib": heartbeat_summary["max_process_tree_rss_gib"],
            "performance_summary": performance,
            "invalid_metric": (
                "resource_peaks.process_cpu_core_percent is invalid because concurrent "
                "telemetry sampling raced on the shared previous-sample state"
                if float((performance.get("resource_peaks") or {}).get("process_cpu_core_percent") or 0)
                > 1600.0
                else None
            ),
        }
        gates_out = {
            "ACQUISITION_INTEGRITY_GATE": "FAIL" if acquisition_fail else "PASS",
            "SCOPE_MEMBERSHIP_GATE": "FAIL" if scope_fail else "PASS",
            "CAS_HASH_GATE": "FAIL" if cas_fail else "PASS",
            "RESUME_LINEAGE_GATE": resume_gate,
            "PERFORMANCE_AND_STORAGE_READOUT": performance_readout["status"],
            "DOWNSTREAM_READINESS_GATE": (
                "PASS_WITH_RESTRICTIONS"
                if not acquisition_fail and not scope_fail and not cas_fail
                else "FAIL"
            ),
        }
        global_pass = all(
            gates_out[name] == "PASS"
            for name in (
                "ACQUISITION_INTEGRITY_GATE",
                "SCOPE_MEMBERSHIP_GATE",
                "CAS_HASH_GATE",
                "RESUME_LINEAGE_GATE",
            )
        ) and gates_out["DOWNSTREAM_READINESS_GATE"] == "PASS"
        verdict = "PASS" if global_pass else "FAIL_CLOSED"
        report = {
            "audit_id": audit_root.name,
            "auditor_version": AUDITOR_VERSION,
            "generated_at_utc": utc_now(),
            "network_access": "PROHIBITED_AND_NOT_USED",
            "run_id": final.get("run_id"),
            "run_terminal_status": final.get("status"),
            "run_exit_code": final.get("exit_code"),
            "wrapper_pid": wrapper_pid,
            "wrapper_alive_at_audit_start": wrapper_alive,
            "scope": scope,
            "input_hashes": input_hashes,
            "expected_hashes": expected_hashes,
            "component_hashes_stable_pre_to_final": component_stable,
            "current_component_hashes": current_component_hashes,
            "current_component_drift": current_component_drift,
            "manifest_reconciliation": manifest_reconciliation,
            "log_reconciliation": log_summary,
            "heartbeat_and_log": heartbeat_summary,
            "cas": cas_summary,
            "performance_and_storage": performance_readout,
            "resume_lineage_findings": resume_control_findings,
            "issue_count": len(all_issues),
            "gates": gates_out,
            "global_verdict": verdict,
            "authorization_decision": {
                "next_c01_tranche": "NOT_AUTHORIZED",
                "cohorts_c02_c05": "NOT_AUTHORIZED",
                "os_float_resolution": "NOT_AUTHORIZED",
                "institutional_promotion": "NOT_AUTHORIZED",
                "read_only_parser_preparation": (
                    "ALLOWED_WITH_EXPLICIT_COMPLETE_SUBMISSION_BOUNDARY_HANDLING"
                    if gates_out["DOWNSTREAM_READINESS_GATE"] == "PASS_WITH_RESTRICTIONS"
                    else "BLOCKED"
                ),
            },
        }
        atomic_write_json(audit_root / "audit_report.json", report)
        status = "COMPLETE" if verdict == "PASS" else "COMPLETE_FAIL_CLOSED"
        terminal = telemetry.stop(status)
        final_audit = {
            "audit_id": audit_root.name,
            "status": status,
            "global_verdict": verdict,
            "started_at_utc": pre_manifest["created_at_utc"],
            "ended_at_utc": utc_now(),
            "duration_seconds": time.monotonic() - started,
            "exit_code": 0 if verdict == "PASS" else 2,
            "gates": gates_out,
            "audit_report_path": (audit_root / "audit_report.json").as_posix(),
            "fallback_records_path": (audit_root / "fallback_records.jsonl").as_posix(),
            "issues_path": (audit_root / "issues.jsonl").as_posix(),
            "cas_verification_path": (audit_root / "cas_verification.jsonl").as_posix(),
            "terminal_heartbeat": terminal,
        }
        atomic_write_json(audit_root / "final_manifest.json", final_audit)
        atomic_write_json(
            audit_root / "pid_manifest.json",
            {
                "wrapper_pid": os.getpid(),
                "stage": "FINAL",
                "expected_alive": False,
                "ended_at_utc": final_audit["ended_at_utc"],
                "exit_code": final_audit["exit_code"],
            },
        )
        print(json.dumps(final_audit, indent=2))
        return int(final_audit["exit_code"])
    except Exception as exc:
        telemetry.update(stage="FAILED", failures=1)
        terminal = telemetry.stop("FAILED")
        failure = {
            "audit_id": audit_root.name,
            "status": "FAILED",
            "ended_at_utc": utc_now(),
            "exit_code": 1,
            "failure_reason": f"{type(exc).__name__}: {exc}",
            "terminal_heartbeat": terminal,
            "resume_instructions": "rerun the exact command with --resume",
        }
        atomic_write_json(audit_root / "final_manifest.json", failure)
        atomic_write_json(
            audit_root / "pid_manifest.json",
            {
                "wrapper_pid": os.getpid(),
                "stage": "FAILED",
                "expected_alive": False,
                "ended_at_utc": failure["ended_at_utc"],
                "exit_code": 1,
            },
        )
        print(json.dumps(failure, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
