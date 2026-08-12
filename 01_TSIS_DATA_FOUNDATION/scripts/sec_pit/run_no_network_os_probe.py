#!/usr/bin/env python
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.class_os_extract_v2 import (
    COMMON_EQUITY_CLASS_CANDIDATE,
    admit_target_instrument_document,
    extract_cover_page_class_os_v0_2,
    resolve_common_equity_class_candidate,
    strip_instrument_class_suffix,
)
from sec_pit.class_os_reconcile_v2 import reconcile_class_os_anchors_v0_3
from sec_pit.companyfacts_reconcile import (
    promote_companyfacts_validated_primary_anchors,
    reconcile_companyfacts_to_primary_os,
)
from sec_pit.ixbrl_class_os_extract_v2 import extract_ixbrl_class_os_v0_2
from sec_pit.resolver import resolve_daily_os


BLOCKED_INTERVAL_STATES = frozenset({"TICKER_REUSE_CONFLICT"})


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    normalized: list[dict[str, Any]] = []
    for value in rows:
        row = dict(value)
        attributes = row.pop("attributes", None)
        if attributes is not None:
            row["attributes_json"] = json.dumps(attributes, sort_keys=True, default=str)
        blockers = row.pop("blocker_codes", None)
        if blockers is not None:
            row["blocker_codes_json"] = json.dumps(blockers, sort_keys=True)
        normalized.append(row)
    pd.DataFrame(normalized).to_parquet(path, index=False)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def interval_resolution_allowed(governed_interval_state: str | None) -> bool:
    return str(governed_interval_state or "") not in BLOCKED_INTERVAL_STATES


def selected_for_os_probe(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[
        frame["stratified_selection_reasons"].map(
            lambda reasons: "OS_PERIODIC_LATEST_TWO" in list(reasons)
        )
    ].copy()


def execute(
    *,
    config_path: Path,
    probe_root: Path,
    acquisition_ledger: Path,
    ticker: str,
    output_root: Path,
    run_id: str,
    companyfacts_observations: Path | None = None,
) -> Path:
    config_path = config_path.resolve()
    probe_root = probe_root.resolve()
    acquisition_ledger = acquisition_ledger.resolve()
    output_root = output_root.resolve()
    companyfacts_observations = (
        companyfacts_observations.resolve()
        if companyfacts_observations is not None
        else None
    )
    if (
        companyfacts_observations is not None
        and not companyfacts_observations.is_file()
    ):
        raise FileNotFoundError(companyfacts_observations)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    probe_manifest = json.loads(
        (probe_root / "final_manifest.json").read_text(encoding="utf-8")
    )
    if probe_manifest.get("status") != "COMPLETE" or probe_manifest.get("probe_gate") != "PASS":
        raise ValueError("stratified selection probe is not COMPLETE/PASS")
    selection_path = probe_root / "document_selection_plan_v0_1.parquet"
    if file_sha256(selection_path) != probe_manifest["output_hashes"][selection_path.name]:
        raise ValueError("selection-plan hash mismatch")
    case_rows = json.loads((probe_root / "case_matrix.json").read_text(encoding="utf-8"))
    matching = [row for row in case_rows if row["ticker"] == ticker]
    if len(matching) != 1:
        raise ValueError(f"expected one case row for {ticker}, found {len(matching)}")
    case = matching[0]
    if case["probe_gate"] != "ELIGIBLE":
        raise ValueError(f"{ticker} is not eligible: {case['probe_gate']}")

    run_root = output_root / "runs" / run_id
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite run root: {run_root}")
    run_root.mkdir(parents=True)
    component_paths = [
        Path(__file__).resolve(),
        SCRIPTS / "sec_pit" / "class_os_extract_v2.py",
        SCRIPTS / "sec_pit" / "ixbrl_class_os_extract_v2.py",
        SCRIPTS / "sec_pit" / "class_os_reconcile_v2.py",
        SCRIPTS / "sec_pit" / "companyfacts_reconcile.py",
        SCRIPTS / "sec_pit" / "resolver.py",
    ]
    metadata_path = Path(
        config["metadata_run_template"].format(ticker_lower=ticker.lower())
    ).resolve()
    pre_manifest = {
        "run_id": run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "status": "RUNNING",
        "mode": "NO_NETWORK_LOCAL_OBJECT_REPLAY",
        "network_requests_authorized": False,
        "ticker": ticker,
        "cik": case["cik"],
        "instrument_id": case["instrument_id"],
        "security_class_id": case.get("security_class_id"),
        "issuer_name": case["issuer_name"],
        "target_class_label": case["target_class_label"],
        "governed_interval_state": case.get("governed_interval_state"),
        "probe_first_session": case["probe_first_session"],
        "probe_last_session": case["probe_last_session"],
        "config_path": config_path.as_posix(),
        "config_sha256": file_sha256(config_path),
        "selection_plan_path": selection_path.as_posix(),
        "selection_plan_sha256": file_sha256(selection_path),
        "acquisition_ledger_path": acquisition_ledger.as_posix(),
        "acquisition_ledger_sha256": file_sha256(acquisition_ledger),
        "companyfacts_observations_path": (
            companyfacts_observations.as_posix()
            if companyfacts_observations is not None
            else None
        ),
        "companyfacts_observations_sha256": (
            file_sha256(companyfacts_observations)
            if companyfacts_observations is not None
            else None
        ),
        "metadata_inventory_path": metadata_path.as_posix(),
        "metadata_inventory_sha256": file_sha256(metadata_path),
        "component_hashes": {path.name: file_sha256(path) for path in component_paths},
        "output_schema_version": "sec_pit_resolved_daily_states_v0_2",
    }
    write_json(run_root / "pre_manifest.json", pre_manifest)

    selection = pd.read_parquet(selection_path)
    selected = selected_for_os_probe(selection[selection["ticker"].eq(ticker)])
    if selected.empty:
        raise ValueError(f"no O/S probe documents selected for {ticker}")
    acquisition_by_url = {
        row["url"]: row
        for row in read_jsonl(acquisition_ledger)
        if row.get("status") in {"FETCHED", "FETCHED_REUSED"}
    }
    metadata = pd.read_parquet(metadata_path)
    metadata_by_accession = {
        str(row["accession_number"]): row for row in metadata.to_dict("records")
    }
    interval_allowed = interval_resolution_allowed(case.get("governed_interval_state"))
    interval_blockers = [] if interval_allowed else ["UNRESOLVED_INSTRUMENT_INTERVAL_STATE"]
    admissions: list[dict[str, Any]] = []
    raw_observations: list[dict[str, Any]] = []
    resolved_target_class_labels: set[str] = set()
    availability = EdgarAvailabilityPolicy()
    for row in selected.sort_values(["filing_date", "accession_number"]).to_dict("records"):
        acquired = acquisition_by_url.get(row["primary_document_url"])
        if not acquired:
            raise ValueError(f"missing acquired object for {row['accession_number']}")
        object_path = Path(acquired["object_path"])
        with gzip.open(object_path, "rb") as handle:
            payload = handle.read()
        if hashlib.sha256(payload).hexdigest() != acquired["sha256"]:
            raise ValueError(f"payload hash mismatch for {row['accession_number']}")
        if len(payload) != int(acquired["bytes"]):
            raise ValueError(f"payload byte mismatch for {row['accession_number']}")
        effective_target_class_label = case["target_class_label"]
        if effective_target_class_label == COMMON_EQUITY_CLASS_CANDIDATE:
            resolved_label, decision = resolve_common_equity_class_candidate(
                payload,
                temporal_scope_state=row["temporal_scope_state"],
                accession_link_state=row["accession_link_state"],
                registrant_name=case["issuer_name"],
                ticker=ticker,
            )
            if resolved_label is not None:
                effective_target_class_label = resolved_label
                resolved_target_class_labels.add(resolved_label)
        else:
            decision = admit_target_instrument_document(
                payload,
                temporal_scope_state=row["temporal_scope_state"],
                accession_link_state=row["accession_link_state"],
                registrant_name=case["issuer_name"],
                ticker=ticker,
                target_class_label=effective_target_class_label,
            )
        effective_decision = decision.decision
        effective_reason = decision.reason
        if not interval_allowed:
            effective_decision = "BLOCKED_GOVERNED_INTERVAL_STATE"
            effective_reason = str(case.get("governed_interval_state"))
        admissions.append({
            "ticker": ticker,
            "instrument_id": case["instrument_id"],
            "security_class_id": case.get("security_class_id"),
            "accession_number": row["accession_number"],
            "form": row["form"],
            "filing_date": row["filing_date"],
            "admission_decision": effective_decision,
            "admission_reason": effective_reason,
            "registrant_match": decision.registrant_match,
            "ticker_class_match": decision.ticker_class_match,
            "resolved_target_class_label": (
                effective_target_class_label
                if decision.decision == "ADMITTED_TARGET_INSTRUMENT_CLASS"
                else None
            ),
            "evidence_excerpt": decision.evidence_excerpt,
            "source_url": row["primary_document_url"],
            "source_sha256": acquired["sha256"],
        })
        if effective_decision != "ADMITTED_TARGET_INSTRUMENT_CLASS":
            continue
        metadata_row = metadata_by_accession.get(str(row["accession_number"]))
        if metadata_row is None or not metadata_row.get("acceptance_datetime"):
            continue
        kwargs = {
            "cik": str(case["cik"]),
            "accession_number": str(row["accession_number"]),
            "form": str(row["form"]),
            "accepted_at": str(metadata_row["acceptance_datetime"]),
            "instrument_id": str(case["instrument_id"]),
            "security_class_id": case.get("security_class_id"),
            "target_class_label": str(effective_target_class_label),
            "source_url": str(row["primary_document_url"]),
            "source_sha256": str(acquired["sha256"]),
            "availability_policy": availability,
        }
        raw_observations.extend(
            asdict(item)
            for item in [
                *extract_cover_page_class_os_v0_2(payload, **kwargs),
                *extract_ixbrl_class_os_v0_2(payload, **kwargs),
            ]
        )

    admitted_anchors, primary_reconciliation = reconcile_class_os_anchors_v0_3(
        raw_observations if interval_allowed else []
    )
    companyfacts_readout = None
    if companyfacts_observations is not None and interval_allowed:
        companyfacts_rows = pd.read_parquet(companyfacts_observations)
        if "ticker" in companyfacts_rows.columns:
            companyfacts_rows = companyfacts_rows[
                companyfacts_rows["ticker"].astype(str).eq(ticker)
            ]
        companyfacts_records = companyfacts_rows.to_dict("records")
        for fact in companyfacts_records:
            encoded = fact.pop("attributes_json", None)
            fact["attributes"] = json.loads(encoded) if encoded else {}
        resolved_class = (
            next(iter(resolved_target_class_labels))
            if len(resolved_target_class_labels) == 1
            else ""
        )
        compared, comparison_readout = reconcile_companyfacts_to_primary_os(
            companyfacts_records,
            raw_observations,
            target_class_label=resolved_class,
            security_class_gate="PASS" if resolved_class else "HALT",
        )
        promoted, promotion_readout = (
            promote_companyfacts_validated_primary_anchors(
                raw_observations,
                compared,
                reconciliation_artifact_sha256=file_sha256(
                    companyfacts_observations
                ),
            )
        )
        companyfacts_readout = {
            "comparison": comparison_readout,
            "promotion": promotion_readout,
        }

        def anchor_key(row: dict[str, Any]) -> tuple[str, str, float, str]:
            attributes = row.get("attributes") or {}
            return (
                str(row.get("accession_number") or ""),
                str(row.get("measurement_at") or ""),
                float(row.get("value") or 0.0),
                str(attributes.get("security_class_label") or ""),
            )

        merged = {anchor_key(row): row for row in promoted}
        merged.update({anchor_key(row): row for row in admitted_anchors})
        admitted_anchors = list(merged.values())
    reconciliation = {
        "policy_id": "class_os_multi_evidence_reconciliation_v0_4",
        "primary_dual_extraction": primary_reconciliation,
        "companyfacts": companyfacts_readout,
        "admitted_anchor_count": len(admitted_anchors),
    }
    companyfacts_conflict = bool(
        companyfacts_readout
        and companyfacts_readout["comparison"].get("value_conflicts", 0) > 0
    )
    session_values = pd.date_range(
        case["probe_first_session"], case["probe_last_session"], freq="B"
    ).strftime("%Y-%m-%d").tolist()
    configured_count = int(config["probe_session_count"])
    if len(session_values) != configured_count:
        calendar = pd.read_parquet(config["market_calendar"], columns=["session_date"])
        session_values = calendar[
            calendar["session_date"].astype(str).between(
                case["probe_first_session"], case["probe_last_session"]
            )
        ]["session_date"].astype(str).tolist()
    sessions = [date.fromisoformat(value) for value in session_values]
    daily = [
        asdict(item)
        for item in resolve_daily_os(
            instrument_id=case["instrument_id"],
            sessions=sessions,
            observations=admitted_anchors,
        )
    ]
    for row in daily:
        blockers = list(interval_blockers)
        if row.get("shares_outstanding_estimate_as_known") is None:
            blockers.append("NO_CAUSAL_ADMITTED_OS_ANCHOR")
            if companyfacts_conflict:
                blockers.append("COMPANYFACTS_OS_VALUE_CONFLICT")
        row["blocker_codes"] = sorted(set(blockers))

    write_parquet(run_root / "accession_instrument_admission.parquet", admissions)
    write_parquet(run_root / "os_source_observations.parquet", raw_observations)
    write_parquet(run_root / "admitted_os_anchors.parquet", admitted_anchors)
    write_parquet(run_root / "daily_os_state.parquet", daily)
    write_json(run_root / "os_anchor_reconciliation.json", reconciliation)
    nonnull = sum(row.get("shares_outstanding_estimate_as_known") is not None for row in daily)
    future = sum(
        bool(row.get("anchor_eligible_from_session"))
        and str(row["anchor_eligible_from_session"]) > str(row["session_date"])
        for row in daily
    )
    audit = {
        "ticker": ticker,
        "selected_os_documents": len(selected),
        "admission_counts": pd.DataFrame(admissions)["admission_decision"].value_counts().to_dict(),
        "raw_observations": len(raw_observations),
        "admitted_anchors": len(admitted_anchors),
        "daily_rows": len(daily),
        "daily_nonnull_rows": nonnull,
        "daily_null_rows": len(daily) - nonnull,
        "future_anchor_rows": future,
        "governed_interval_state": case.get("governed_interval_state"),
        "interval_resolution_allowed": interval_allowed,
        "blocker_codes": sorted({code for row in daily for code in row["blocker_codes"]}),
        "status": (
            "PASS_WITH_RESTRICTIONS"
            if len(daily) == configured_count and nonnull == len(daily) and future == 0
            else "BLOCKED_WITH_EXPLICIT_NULLS"
        ),
        "network_requests": 0,
        "resolved_target_class_labels": sorted(resolved_target_class_labels),
    }
    write_json(run_root / "variable_audit.json", audit)
    output_names = (
        "accession_instrument_admission.parquet",
        "os_source_observations.parquet",
        "admitted_os_anchors.parquet",
        "daily_os_state.parquet",
        "os_anchor_reconciliation.json",
        "variable_audit.json",
    )
    final = {
        **pre_manifest,
        "ended_at_utc": datetime.now(UTC).isoformat(),
        "status": "COMPLETE",
        "result": audit["status"],
        "resolved_target_class_label": (
            next(iter(resolved_target_class_labels))
            if len(resolved_target_class_labels) == 1
            else None
        ),
        "resolved_registrant_name": strip_instrument_class_suffix(case["issuer_name"]),
        "counts": audit,
        "output_files": {
            name: {
                "sha256": file_sha256(run_root / name),
                "bytes": (run_root / name).stat().st_size,
            }
            for name in output_names
        },
        "network_requests": 0,
    }
    write_json(run_root / "final_manifest.json", final)
    return run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--probe-root", type=Path, required=True)
    parser.add_argument("--acquisition-ledger", type=Path, required=True)
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--companyfacts-observations", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(
        config_path=args.config,
        probe_root=args.probe_root,
        acquisition_ledger=args.acquisition_ledger,
        ticker=args.ticker,
        output_root=args.output_root,
        run_id=args.run_id,
        companyfacts_observations=args.companyfacts_observations,
    ))
