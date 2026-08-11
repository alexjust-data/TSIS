#!/usr/bin/env python
from __future__ import annotations

import argparse
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
            if isinstance(value, (list, dict)):
                row[f"{key}_json"] = json.dumps(value, sort_keys=True, default=str)
                del row[key]
        normalized.append(row)
    pd.DataFrame(normalized).to_parquet(path, index=False)


def execute(args: argparse.Namespace) -> Path:
    config_path = args.config.resolve()
    probe_root = args.probe_root.resolve()
    output_root = args.output_root.resolve()
    run_root = output_root / "runs" / args.run_id
    if run_root.exists():
        raise FileExistsError(run_root)
    run_root.mkdir(parents=True)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    cases = json.loads((probe_root / "case_matrix.json").read_text(encoding="utf-8"))
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
        "network_scope": "SEVEN_OFFICIAL_SEC_COMPANYFACTS_JSON_REQUESTS_MAX",
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
    all_facts: list[dict[str, Any]] = []
    all_reconciliation: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    performance: list[dict[str, Any]] = []
    for case in cases:
        ticker = str(case["ticker"])
        state["ticker"] = ticker
        heartbeat("RUNNING", "ACQUIRE_COMPANYFACTS")
        cik = str(case["cik"]).zfill(10)
        result, payload = client.fetch_json(
            COMPANYFACTS_URL.format(cik=cik),
            f"companyfacts/{cik}.json",
        )
        if client.last_performance:
            performance.append(client.last_performance)
        if payload is None or not result.sha256:
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
        "performance_summary.json",
        "variable_audit.json",
    ]
    final = {
        **pre_manifest,
        "status": "COMPLETE",
        "ended_at_utc": datetime.now(UTC).isoformat(),
        "requests": len(cases),
        "facts": len(all_facts),
        "value_conflicts": sum(
            row["reconciliation_state"]
            == "SAME_ACCESSION_MEASUREMENT_VALUE_CONFLICT"
            for row in all_reconciliation
        ),
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
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    print(execute(arguments))
