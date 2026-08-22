#!/usr/bin/env python
# ruff: noqa: E402
"""Build the network-free post-metadata gate for one frozen 4,824 cohort.

The output is evidence for a later human primary-download decision.  It never
downloads a primary document and never grants download authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.models import FilingRecord
from sec_pit.predownload_control import (
    POLICY_ID,
    accession_link_state,
    filing_roles_v0_2,
    security_class_gate,
    selection_plan_v0_2,
    temporal_scope_state,
)
from sec_pit.storage import atomic_write_json, read_jsonl
from sec_pit.telemetry import summarize_document_performance


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=Path(__file__).resolve().parents[3], text=True
        ).strip()
    except Exception:
        return None


def cik(value: Any) -> str:
    return "".join(character for character in str(value or "") if character.isdigit()).zfill(10)


def serial(value: Any) -> Any:
    if isinstance(value, list | tuple | dict):
        return value
    missing = pd.isna(value)
    return None if isinstance(missing, bool) and missing else value


def record_from_row(row: dict[str, Any]) -> FilingRecord:
    return FilingRecord(
        cik=cik(row.get("cik")),
        accession_number=str(row.get("accession_number") or ""),
        form=str(row.get("form") or ""),
        filing_date=serial(row.get("filing_date")),
        report_date=serial(row.get("report_date")),
        acceptance_datetime=serial(row.get("acceptance_datetime")),
        primary_document=serial(row.get("primary_document")),
        primary_document_description=serial(row.get("primary_document_description")),
        items=serial(row.get("items")),
        is_xbrl=serial(row.get("is_xbrl")),
        is_inline_xbrl=serial(row.get("is_inline_xbrl")),
        filing_size_bytes=serial(row.get("filing_size_bytes")),
        metadata_source=str(row.get("metadata_source") or ""),
    )


def distribution(values: pd.Series) -> dict[str, float | int | None]:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        return {"count": 0, "p50": None, "p95": None, "max": None}
    return {
        "count": int(len(clean)),
        "p50": float(clean.quantile(0.50)),
        "p95": float(clean.quantile(0.95)),
        "max": float(clean.max()),
    }


def projected_full_universe_bytes(
    observed_bytes: int, cohort_rows: int, parent_rows: int
) -> int:
    if cohort_rows <= 0:
        raise ValueError("cohort_rows must be positive")
    return int(round(observed_bytes * parent_rows / cohort_rows))


def execute(args: argparse.Namespace) -> Path:
    pool_path = args.candidate_pool.resolve()
    metadata_root = args.metadata_root.resolve()
    full_order_path = args.full_order.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"Output exists; version or remove explicitly: {output}")

    metadata_manifest_path = metadata_root / "final_manifest.json"
    if not metadata_manifest_path.is_file():
        raise FileNotFoundError(metadata_manifest_path)
    metadata_manifest = json.loads(metadata_manifest_path.read_text(encoding="utf-8-sig"))
    if metadata_manifest.get("status") != "COMPLETE":
        raise RuntimeError("metadata run is not COMPLETE")
    if metadata_manifest.get("candidate_pool_sha256") != sha256(pool_path):
        raise RuntimeError("metadata candidate-pool hash does not match frozen cohort")

    pool = pd.read_parquet(pool_path).sort_values("selection_order").reset_index(drop=True)
    full_order = pd.read_parquet(full_order_path)
    expected = len(pool)
    if int(metadata_manifest.get("completed_tickers") or 0) != expected:
        raise RuntimeError("metadata completeness gate failed")

    output.mkdir(parents=True)
    pre = {
        "run_id": output.name,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": sha256(Path(__file__).resolve()),
        "policy_id": POLICY_ID,
        "candidate_pool_path": pool_path.as_posix(),
        "candidate_pool_sha256": sha256(pool_path),
        "metadata_root": metadata_root.as_posix(),
        "metadata_manifest_sha256": sha256(metadata_manifest_path),
        "full_order_path": full_order_path.as_posix(),
        "full_order_sha256": sha256(full_order_path),
        "network_access": "PROHIBITED_AND_NOT_USED",
        "primary_document_acquisition": "NOT_EXECUTED",
        "download_authorization": "NOT_AUTHORIZED_PENDING_HUMAN_GATE",
        "git_branch": git_value("branch", "--show-current"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty_state": bool(git_value("status", "--porcelain")),
    }
    atomic_write_json(output / "pre_manifest.json", pre)
    atomic_write_json(
        output / "pid_manifest.json",
        {"wrapper_pid": os.getpid(), "stage": "POST_METADATA_GATE", "expected_alive": True},
    )

    all_candidates_by_cik: dict[str, list[dict[str, Any]]] = {}
    for row in full_order.to_dict("records"):
        normalized = {
            "cik": cik(row.get("cik")),
            "instrument_id": str(row.get("instrument_id") or ""),
            "valid_from": serial(row.get("first_seen_date")),
            "valid_to": serial(row.get("last_observed_date")),
        }
        all_candidates_by_cik.setdefault(normalized["cik"], []).append(normalized)

    selected_rows: list[dict[str, Any]] = []
    gate_rows: list[dict[str, Any]] = []
    total_accessions = 0
    for position, case in enumerate(pool.to_dict("records"), start=1):
        ticker = str(case["ticker"])
        inventory_path = metadata_root / "tickers" / ticker.lower() / "filing_inventory.parquet"
        profile_path = metadata_root / "tickers" / ticker.lower() / "profile.json"
        if not inventory_path.is_file() or not profile_path.is_file():
            raise RuntimeError(f"{ticker}: missing complete metadata artifacts")
        inventory = pd.read_parquet(inventory_path)
        total_accessions += len(inventory)
        rows: list[dict[str, Any]] = []
        ambiguous_links = 0
        for raw in inventory.to_dict("records"):
            row = {key: serial(value) for key, value in raw.items()}
            row["roles_v0_2"] = filing_roles_v0_2(record_from_row(row))
            row["temporal_scope_state"] = temporal_scope_state(
                row.get("filing_date"), case.get("first_seen_date"), case.get("last_observed_date")
            )
            link_state, candidates = accession_link_state(
                filing_cik=row.get("cik", ""),
                candidate_instruments=all_candidates_by_cik.get(cik(row.get("cik")), []),
                filing_date=row.get("filing_date"),
            )
            row["accession_link_state"] = link_state
            row["candidate_instrument_ids"] = candidates
            ambiguous_links += link_state == "REVIEW_MULTIPLE_INSTRUMENT_CANDIDATES"
            rows.append(row)

        plan = selection_plan_v0_2(rows, capacity=None)
        class_gate, class_reason = security_class_gate(
            {
                "name": case.get("name"),
                "is_common_stock": bool(case.get("is_common_stock")),
                "instrument_id": case.get("instrument_id"),
            }
        )
        identity_conflict = bool(case.get("instrument_identity_cik_conflict"))
        if identity_conflict:
            acquisition_state = "HALT_CROSS_CIK_IDENTITY_CONFLICT"
        elif class_gate != "PASS":
            acquisition_state = "HALT_SECURITY_CLASS"
        elif ambiguous_links:
            acquisition_state = "HALT_LIFECYCLE_IDENTITY_REVIEW"
        elif plan.gate != "PASS":
            acquisition_state = "HALT_SELECTION_CONTROL"
        else:
            acquisition_state = "ELIGIBLE_FOR_REVIEW_NOT_AUTHORIZED"

        for selected in plan.selected:
            filing_date = str(selected.get("filing_date") or "")[:10]
            selected_rows.append(
                {
                    "ticker": ticker,
                    "cohort_selection_order": position,
                    "cik": cik(case.get("cik")),
                    "instrument_id": case.get("instrument_id"),
                    "accession_number": selected.get("accession_number"),
                    "form": selected.get("form"),
                    "filing_date": selected.get("filing_date"),
                    "roles_v0_2": selected.get("roles_v0_2"),
                    "temporal_scope_state": selected.get("temporal_scope_state"),
                    "accession_link_state": selected.get("accession_link_state"),
                    "filing_size_bytes": selected.get("filing_size_bytes"),
                    "primary_document_url": selected.get("primary_document_url"),
                    "pre_xbrl_proxy": bool(filing_date and filing_date < "2009-01-01"),
                    "ticker_acquisition_state": acquisition_state,
                }
            )
        gate_rows.append(
            {
                "ticker": ticker,
                "metadata_inventory_count": len(inventory),
                "selected_document_count": len(plan.selected),
                "required_document_count": plan.required_count,
                "selection_gate": plan.gate,
                "security_class_gate": class_gate,
                "security_class_reason": class_reason,
                "identity_reused": bool(case.get("instrument_identity_reused_in_parent_universe")),
                "cross_cik_identity_conflict": identity_conflict,
                "ambiguous_accession_link_count": ambiguous_links,
                "primary_document_acquisition_state": acquisition_state,
            }
        )

    selected = pd.DataFrame(selected_rows)
    gates = pd.DataFrame(gate_rows).sort_values("ticker")
    selected = selected.sort_values(["cohort_selection_order", "filing_date", "accession_number"])
    selected.to_parquet(output / "document_selection_plan_v0_2.parquet", index=False)
    gates.to_parquet(output / "gate_matrix.parquet", index=False)
    gates.to_csv(output / "gate_matrix.csv", index=False)

    per_ticker_selected = selected.groupby("ticker", as_index=False).agg(
        selected_documents=("accession_number", "size"),
        selected_filing_size_upper_bound_bytes=("filing_size_bytes", "sum"),
    )
    per_ticker = gates[["ticker"]].merge(
        per_ticker_selected, on="ticker", how="left", validate="one_to_one"
    )
    per_ticker[["selected_documents", "selected_filing_size_upper_bound_bytes"]] = (
        per_ticker[["selected_documents", "selected_filing_size_upper_bound_bytes"]]
        .fillna(0)
    )
    known_sizes = pd.to_numeric(selected["filing_size_bytes"], errors="coerce")
    observed_upper_bound = int(known_sizes.fillna(0).sum())
    request_log = metadata_root / "request_performance.jsonl"
    request_summary = summarize_document_performance(
        read_jsonl([request_log]) if request_log.is_file() else []
    )
    metadata_gate = (
        "PASS"
        if int(metadata_manifest.get("completed_tickers") or 0) == expected
        and int(request_summary["failed"]) == 0
        else "FAIL"
    )
    halted = int((gates["primary_document_acquisition_state"] != "ELIGIBLE_FOR_REVIEW_NOT_AUTHORIZED").sum())
    final = {
        **pre,
        "status": "COMPLETE" if metadata_gate == "PASS" else "FAILED",
        "completed_at_utc": utc_now(),
        "metadata_gate": metadata_gate,
        "probe_gate": metadata_gate,
        "metadata_completeness": f"{expected}/{expected}",
        "metadata_request_summary": {
            "request_count": int(request_summary["document_count"]),
            "fetched": int(request_summary["fetched"]),
            "failed": int(request_summary["failed"]),
            "retry_count": int(request_summary["retry_count"]),
            "http_429_count": int(request_summary["http_429_count"]),
        },
        "total_accessions": int(total_accessions),
        "selected_document_count": int(len(selected)),
        "selected_documents_per_ticker": distribution(per_ticker["selected_documents"]),
        "selected_filing_size_upper_bound_bytes": observed_upper_bound,
        "selected_filing_size_per_ticker_upper_bound_bytes": distribution(
            per_ticker["selected_filing_size_upper_bound_bytes"]
        ),
        "selected_documents_with_known_filing_size": int(known_sizes.notna().sum()),
        "selected_documents_with_missing_filing_size": int(known_sizes.isna().sum()),
        "pre_xbrl_proxy_count": int(selected["pre_xbrl_proxy"].sum()),
        "pre_xbrl_proxy_pct": round(float(selected["pre_xbrl_proxy"].mean() * 100.0), 6),
        "fallback_expected_state": "NOT_CERTIFIABLE_FROM_SUBMISSIONS_METADATA_ONLY",
        "fallback_risk_proxy": "PRE_XBRL_PROXY_REPORTED_SEPARATELY",
        "identity_reused_ticker_rows": int(gates["identity_reused"].sum()),
        "cross_cik_identity_conflict_ticker_rows": int(gates["cross_cik_identity_conflict"].sum()),
        "lifecycle_or_identity_review_ticker_rows": halted,
        "eligible_for_review_not_authorized_ticker_rows": int(len(gates) - halted),
        "projected_full_universe_selected_filing_size_upper_bound_bytes": projected_full_universe_bytes(
            observed_upper_bound, expected, args.parent_universe_rows
        ),
        "projection_warning": (
            "C01 is modern-only and not historically representative; filing_size_bytes is a "
            "filing-level upper bound, not measured compressed primary storage"
        ),
        "primary_document_acquisition": "NOT_EXECUTED",
        "download_authorization": "NOT_AUTHORIZED_PENDING_HUMAN_GATE",
        "next_gate": "HUMAN_REVIEW_C01_METADATA_SELECTION_STORAGE_AND_LIFECYCLE",
        "output_artifacts": {
            name: sha256(output / name)
            for name in (
                "document_selection_plan_v0_2.parquet",
                "gate_matrix.parquet",
                "gate_matrix.csv",
            )
        },
    }
    atomic_write_json(output / "final_manifest.json", final)
    atomic_write_json(output / "heartbeat_latest.json", final)
    atomic_write_json(
        output / "pid_manifest.json",
        {
            "wrapper_pid": os.getpid(),
            "stage": final["status"],
            "expected_alive": False,
            "ended_at_utc": final["completed_at_utc"],
            "exit_code": 0 if metadata_gate == "PASS" else 1,
        },
    )
    print(json.dumps(final, indent=2))
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-pool", type=Path, required=True)
    parser.add_argument("--metadata-root", type=Path, required=True)
    parser.add_argument("--full-order", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--parent-universe-rows", type=int, default=4824)
    return parser.parse_args()


if __name__ == "__main__":
    print(execute(parse_args()))
