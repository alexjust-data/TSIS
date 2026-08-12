#!/usr/bin/env python
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.client import SecClient
from sec_pit.companyfacts_reconcile import reconcile_companyfacts_to_primary_os
from sec_pit.extract import extract_companyfacts_os
from sec_pit.metadata import COMPANYFACTS_URL
from sec_pit.models import AcquisitionResult
from sec_pit.storage import ContentAddressedStore, append_jsonl, atomic_write_json
from sec_pit.telemetry import summarize_document_performance


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    normalized = []
    for source in rows:
        row = dict(source)
        attributes = row.pop("attributes", None)
        if attributes is not None:
            row["attributes_json"] = json.dumps(
                attributes, sort_keys=True, default=str
            )
        for key, value in list(row.items()):
            if isinstance(value, list | dict):
                row[f"{key}_json"] = json.dumps(value, sort_keys=True, default=str)
                del row[key]
        normalized.append(row)
    pd.DataFrame(normalized).to_parquet(path, index=False)


def select_cases(
    cases: list[dict[str, Any]],
    requested_tickers: list[str] | None,
    *,
    eligible_only: bool = False,
) -> list[dict[str, Any]]:
    if eligible_only:
        cases = [case for case in cases if case.get("probe_gate") == "ELIGIBLE"]
    if not requested_tickers:
        return cases
    requested = {ticker.strip().upper() for ticker in requested_tickers}
    selected = [case for case in cases if str(case["ticker"]).upper() in requested]
    found = {str(case["ticker"]).upper() for case in selected}
    missing = sorted(requested - found)
    if missing:
        raise ValueError(f"requested tickers absent from case matrix: {missing}")
    return selected


def companyfacts_fetch_state(
    *, http_status: int | None, payload_available: bool
) -> str:
    if payload_available:
        return "AVAILABLE"
    if http_status == 404:
        return "COMPANYFACTS_NOT_AVAILABLE"
    return "ACQUISITION_FAILED"


def persist_failure(args: argparse.Namespace, exc: Exception) -> None:
    run_root = args.output_root.resolve() / "runs" / args.run_id
    pre_path = run_root / "pre_manifest.json"
    if not pre_path.is_file():
        return
    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    ended = datetime.now(UTC).isoformat()
    atomic_write_json(
        run_root / "final_manifest.json",
        {
            **pre,
            "status": "FAILED",
            "ended_at_utc": ended,
            "failure_reason": f"{type(exc).__name__}: {exc}",
        },
    )
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "run_id": args.run_id,
            "wrapper_pid": os.getpid(),
            "started_at_utc": pre["created_at_utc"],
            "ended_at_utc": ended,
            "expected_alive": False,
        },
    )


def read_reusable_companyfacts(
    row: dict[str, Any], *, expected_url: str
) -> tuple[AcquisitionResult, dict[str, Any]]:
    if row.get("status") not in {"FETCHED", "FETCHED_REUSED"}:
        raise ValueError("reusable acquisition row is not successful")
    if str(row.get("url")) != expected_url:
        raise ValueError("reusable acquisition URL mismatch")
    object_path = Path(str(row["object_path"]))
    with gzip.open(object_path, "rb") as handle:
        payload = handle.read()
    if len(payload) != int(row["bytes"]):
        raise ValueError("reusable Company Facts byte mismatch")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != str(row["sha256"]):
        raise ValueError("reusable Company Facts SHA-256 mismatch")
    result = AcquisitionResult(
        url=expected_url,
        status="FETCHED_REUSED",
        http_status=int(row.get("http_status") or 200),
        fetched_at_utc=datetime.now(UTC).isoformat(),
        sha256=digest,
        bytes=len(payload),
        content_type=row.get("content_type"),
        object_path=object_path.as_posix(),
        logical_path=row.get("logical_path"),
        attempts=0,
    )
    return result, json.loads(payload.decode("utf-8"))


def execute(args: argparse.Namespace) -> Path:
    config_path = args.config.resolve()
    probe_root = args.probe_root.resolve()
    output_root = args.output_root.resolve()
    run_root = output_root / "runs" / args.run_id
    if run_root.exists():
        raise FileExistsError(run_root)
    run_root.mkdir(parents=True)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    all_cases = json.loads(
        (probe_root / "case_matrix.json").read_text(encoding="utf-8")
    )
    cases = select_cases(
        all_cases, args.tickers, eligible_only=args.eligible_only
    )
    components = [
        Path(__file__).resolve(),
        SCRIPTS / "sec_pit" / "extract.py",
        SCRIPTS / "sec_pit" / "companyfacts_reconcile.py",
        SCRIPTS / "sec_pit" / "client.py",
        SCRIPTS / "sec_pit" / "storage.py",
    ]
    monitor = (
        'powershell -NoProfile -ExecutionPolicy Bypass -File '
        f'"{(SCRIPTS / "sec_pit" / "monitor_authorized_primary_acquisition_v0_2.ps1")}" '
        f'-RunRoot "{run_root}" -IntervalSeconds 10 -Compact -Watch'
    )
    pre_manifest = {
        "run_id": args.run_id,
        "status": "RUNNING",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "wrapper_pid": os.getpid(),
        "config_path": config_path.as_posix(),
        "config_sha256": sha256_file(config_path),
        "probe_root": probe_root.as_posix(),
        "case_matrix_sha256": sha256_file(probe_root / "case_matrix.json"),
        "component_hashes": {path.name: sha256_file(path) for path in components},
        "network_scope": (
            f"{len(cases)}_OFFICIAL_SEC_COMPANYFACTS_JSON_REQUESTS_MAX"
        ),
        "tickers": [str(case["ticker"]) for case in cases],
        "reuse_acquisition_ledger": (
            args.reuse_acquisition_ledger.resolve().as_posix()
            if args.reuse_acquisition_ledger is not None
            else None
        ),
        "reuse_acquisition_ledger_sha256": (
            sha256_file(args.reuse_acquisition_ledger.resolve())
            if args.reuse_acquisition_ledger is not None
            else None
        ),
        "companyfacts_role": "O/S_RECONCILIATION_ONLY_NOT_FLOAT_SOURCE",
        "monitor_command": monitor,
    }
    atomic_write_json(run_root / "pre_manifest.json", pre_manifest)
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "run_id": args.run_id,
            "wrapper_pid": os.getpid(),
            "started_at_utc": pre_manifest["created_at_utc"],
            "expected_alive": True,
        },
    )
    state = {"completed": 0, "total": len(cases), "ticker": None}

    def heartbeat(status: str, stage: str) -> None:
        payload = {
            "run_id": args.run_id,
            "status": status,
            "stage": stage,
            "observed_at_utc": datetime.now(UTC).isoformat(),
            "wrapper_pid": os.getpid(),
            "wrapper_pid_alive": True,
            **state,
        }
        atomic_write_json(run_root / "heartbeat_latest.json", payload)
        append_jsonl(run_root / "heartbeat.jsonl", payload)
        append_jsonl(run_root / "run.log", payload)

    heartbeat("RUNNING", "PREFLIGHT")
    client = SecClient(
        user_agent=args.user_agent,
        store=ContentAddressedStore(output_root / "objects"),
        acquisition_log=run_root / "acquisition.jsonl",
        requests_per_second=args.requests_per_second,
        telemetry_log=run_root / "document_performance.jsonl",
    )
    policy = EdgarAvailabilityPolicy()
    reusable_by_url: dict[str, dict[str, Any]] = {}
    if args.reuse_acquisition_ledger is not None:
        for line in args.reuse_acquisition_ledger.resolve().read_text(
            encoding="utf-8"
        ).splitlines():
            row = json.loads(line)
            if row.get("status") in {"FETCHED", "FETCHED_REUSED"}:
                reusable_by_url[str(row["url"])] = row
    all_facts: list[dict[str, Any]] = []
    all_reconciliation: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    performance: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []
    for case in cases:
        ticker = str(case["ticker"])
        state["ticker"] = ticker
        heartbeat("RUNNING", "ACQUIRE_COMPANYFACTS")
        cik = str(case["cik"]).zfill(10)
        companyfacts_url = COMPANYFACTS_URL.format(cik=cik)
        reusable = reusable_by_url.get(companyfacts_url)
        if reusable is not None:
            result, payload = read_reusable_companyfacts(
                reusable, expected_url=companyfacts_url
            )
            append_jsonl(run_root / "acquisition.jsonl", result.to_dict())
            performance.append(
                {
                    "status": "FETCHED_REUSED",
                    "http_status": result.http_status,
                    "bytes": result.bytes,
                    "retry_count": 0,
                    "http_429_count": 0,
                    "total_seconds": 0.0,
                    "throttle_seconds": 0.0,
                    "request_seconds": 0.0,
                    "request_attempt_seconds": [],
                    "retry_wait_seconds": 0.0,
                    "storage_seconds": 0.0,
                    "sha256_seconds": 0.0,
                    "gzip_seconds": 0.0,
                    "atomic_write_seconds": 0.0,
                    "stored_bytes": 0,
                    "deduplicated": True,
                    "url": result.url,
                }
            )
        else:
            result, payload = client.fetch_json(
                companyfacts_url,
                f"companyfacts/{cik}.json",
            )
            if client.last_performance:
                performance.append(client.last_performance)
        fetch_state = companyfacts_fetch_state(
            http_status=result.http_status,
            payload_available=payload is not None and bool(result.sha256),
        )
        if fetch_state == "COMPANYFACTS_NOT_AVAILABLE":
            unavailable.append(
                {
                    "ticker": ticker,
                    "cik": cik,
                    "state": fetch_state,
                    "http_status": result.http_status,
                    "source_url": result.url,
                }
            )
            summaries.append(
                {
                    "ticker": ticker,
                    "status": fetch_state,
                    "companyfacts_rows": 0,
                    "exact_same_accession_measurement_value": 0,
                    "value_conflicts": 0,
                    "class_validation_authorized_rows": 0,
                    "companyfacts_role": (
                        "O/S_RECONCILIATION_ONLY_NOT_FLOAT_SOURCE"
                    ),
                }
            )
            state["completed"] += 1
            heartbeat("RUNNING", "COMPANYFACTS_UNAVAILABLE_CONTINUE")
            continue
        if fetch_state == "ACQUISITION_FAILED":
            raise RuntimeError(f"Company Facts acquisition failed for {ticker}")
        facts = [
            item.to_dict()
            for item in extract_companyfacts_os(
                payload,
                instrument_id=case.get("instrument_id"),
                security_class_id=case.get("security_class_id"),
                source_url=result.url,
                source_sha256=result.sha256,
                availability_policy=policy,
            )
        ]
        metadata_path = Path(
            config["metadata_run_template"].format(ticker_lower=ticker.lower())
        )
        metadata = pd.read_parquet(metadata_path).to_dict("records")
        by_accession = {
            str(row["accession_number"]): row for row in metadata
        }
        for row in facts:
            filing = by_accession.get(str(row.get("accession_number") or ""))
            if filing:
                accepted = filing.get("acceptance_datetime")
                decision = policy.resolve(
                    str(accepted) if accepted is not None else None,
                    filing.get("form"),
                )
                row["filing_accepted_at"] = accepted
                row["eligible_from_session"] = (
                    decision.eligible_from_session.isoformat()
                    if decision.eligible_from_session
                    else None
                )
                row["availability_policy_id"] = decision.policy_id
                row["causality_state"] = decision.state
                row["quality_state"] = "CANDIDATE_REQUIRES_RECONCILIATION"
            row["ticker"] = ticker
        os_run = (
            args.os_output_root.resolve()
            / "runs"
            / args.os_run_template.format(
                ticker_lower=ticker.lower(), ticker=ticker
            )
        )
        primary = (
            pd.read_parquet(os_run / "os_source_observations.parquet").to_dict(
                "records"
            )
            if (os_run / "os_source_observations.parquet").is_file()
            else []
        )
        reconciled, readout = reconcile_companyfacts_to_primary_os(
            facts,
            primary,
            target_class_label=str(case.get("target_class_label") or ""),
            security_class_gate=str(case.get("security_class_gate") or ""),
        )
        for row in reconciled:
            row["ticker"] = ticker
            row["cik"] = cik
        all_facts.extend(facts)
        all_reconciliation.extend(reconciled)
        summaries.append({"ticker": ticker, **readout})
        state["completed"] += 1
        heartbeat("RUNNING", "RECONCILE_COMPANYFACTS")
    write_parquet(run_root / "companyfacts_os_observations.parquet", all_facts)
    write_parquet(
        run_root / "companyfacts_primary_os_reconciliation.parquet",
        all_reconciliation,
    )
    write_parquet(run_root / "companyfacts_case_summary.parquet", summaries)
    write_parquet(run_root / "companyfacts_unavailable.parquet", unavailable)
    performance_summary = summarize_document_performance(performance)
    atomic_write_json(run_root / "performance_summary.json", performance_summary)
    atomic_write_json(
        run_root / "variable_audit.json",
        {
            "companyfacts_os": "PASS_WITH_RESTRICTIONS",
            "rows": len(all_facts),
            "exact_matches": sum(
                row["reconciliation_state"]
                == "EXACT_SAME_ACCESSION_MEASUREMENT_VALUE"
                for row in all_reconciliation
            ),
            "value_conflicts": sum(
                row["reconciliation_state"]
                == "SAME_ACCESSION_MEASUREMENT_VALUE_CONFLICT"
                for row in all_reconciliation
            ),
            "unavailable_cases": len(unavailable),
            "semantic_restriction": (
                "Company Facts validates O/S candidates only; it never supplies "
                "owner-exclusion float and does not resolve multiclass scope."
            ),
        },
    )
    outputs = [
        "companyfacts_os_observations.parquet",
        "companyfacts_primary_os_reconciliation.parquet",
        "companyfacts_case_summary.parquet",
        "companyfacts_unavailable.parquet",
        "performance_summary.json",
        "variable_audit.json",
    ]
    final = {
        **pre_manifest,
        "status": "COMPLETE",
        "ended_at_utc": datetime.now(UTC).isoformat(),
        "requests": len(cases),
        "network_requests": len(cases) - sum(
            row.get("status") == "FETCHED_REUSED" for row in performance
        ),
        "reused_acquisitions": sum(
            row.get("status") == "FETCHED_REUSED" for row in performance
        ),
        "facts": len(all_facts),
        "value_conflicts": sum(
            row["reconciliation_state"]
            == "SAME_ACCESSION_MEASUREMENT_VALUE_CONFLICT"
            for row in all_reconciliation
        ),
        "unavailable_cases": len(unavailable),
        "outputs": {
            name: {
                "sha256": sha256_file(run_root / name),
                "bytes": (run_root / name).stat().st_size,
            }
            for name in outputs
        },
    }
    atomic_write_json(run_root / "final_manifest.json", final)
    state["ticker"] = None
    heartbeat("COMPLETE", "FINAL")
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "run_id": args.run_id,
            "wrapper_pid": os.getpid(),
            "started_at_utc": pre_manifest["created_at_utc"],
            "ended_at_utc": final["ended_at_utc"],
            "expected_alive": False,
        },
    )
    return run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--probe-root", type=Path, required=True)
    parser.add_argument("--os-output-root", type=Path, required=True)
    parser.add_argument("--os-run-template", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--user-agent", required=True)
    parser.add_argument("--requests-per-second", type=float, default=5.0)
    parser.add_argument("--tickers", nargs="*")
    parser.add_argument("--eligible-only", action="store_true")
    parser.add_argument("--reuse-acquisition-ledger", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    try:
        print(execute(arguments))
    except Exception as error:
        persist_failure(arguments, error)
        raise
