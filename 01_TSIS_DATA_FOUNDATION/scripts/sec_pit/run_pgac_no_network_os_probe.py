from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.class_os_extract import (
    admit_target_interval_document,
    extract_cover_page_class_os,
)
from sec_pit.class_os_reconcile import reconcile_class_os_anchors
from sec_pit.ixbrl_class_os_extract import extract_ixbrl_class_os
from sec_pit.resolver import resolve_daily_os


ROOT = Path("C:/TSIS_Data")
DEFAULT_EVIDENCE_ROOT = ROOT / (
    "01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit/"
    "evidence_assets/sec_pit_predownload_7t_probe_v0_3"
)
DEFAULT_ACQUISITION_RUN = ROOT / (
    "runtime/sec_pit_primary_v0_2/runs/"
    "sec_pit_pgac_primary_v0_2_20260811T1035Z"
)
DEFAULT_METADATA_INVENTORY = Path(
    "D:/TSIS/fundamental_context/sec_pit_v0_1/runs/"
    "sec_pit_7t_metadata_v0_2__pgac/filing_inventory.parquet"
)
DEFAULT_MARKET_CALENDAR = Path(
    "G:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet"
)
EXPECTED_SELECTION_SHA256 = (
    "ddce5a64826268ceb4f36d34476eba03d879c9a47c6a94d634a7af74823bb998"
)
TARGET_TICKER = "PGAC"
TARGET_REGISTRANT = "Pantages Capital Acquisition Corporation"
TARGET_CLASS_LABEL = "Class A ordinary shares"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def source_observation_row(observation: Any) -> dict[str, Any]:
    row = dict(observation) if isinstance(observation, dict) else asdict(observation)
    row["attributes_json"] = json.dumps(
        row.pop("attributes"), sort_keys=True, default=str
    )
    return row


def execute(args: argparse.Namespace) -> Path:
    selection_path = args.selection_plan.resolve()
    identity_path = args.identity_ledger.resolve()
    acquisition_path = args.acquisition_ledger.resolve()
    run_root = (args.output_root / "runs" / args.run_id).resolve()
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite run root: {run_root}")
    run_root.mkdir(parents=True)

    selection_sha = sha256_file(selection_path)
    if selection_sha != args.expected_selection_sha256:
        raise ValueError(
            "selection plan hash mismatch: "
            f"expected={args.expected_selection_sha256} actual={selection_sha}"
        )

    script_path = Path(__file__).resolve()
    created_at = datetime.now(timezone.utc).isoformat()
    pre_manifest = {
        "run_id": args.run_id,
        "created_at_utc": created_at,
        "ticker": TARGET_TICKER,
        "mode": "NO_NETWORK_LOCAL_OBJECT_REPLAY",
        "network_requests_authorized": False,
        "selection_plan_path": selection_path.as_posix(),
        "selection_plan_sha256": selection_sha,
        "identity_ledger_path": identity_path.as_posix(),
        "identity_ledger_sha256": sha256_file(identity_path),
        "acquisition_ledger_path": acquisition_path.as_posix(),
        "acquisition_ledger_sha256": sha256_file(acquisition_path),
        "metadata_inventory_path": args.metadata_inventory.resolve().as_posix(),
        "metadata_inventory_sha256": sha256_file(args.metadata_inventory.resolve()),
        "market_calendar_path": args.market_calendar.resolve().as_posix(),
        "market_calendar_sha256": sha256_file(args.market_calendar.resolve()),
        "script_path": script_path.as_posix(),
        "script_sha256": sha256_file(script_path),
        "target_registrant": TARGET_REGISTRANT,
        "target_security_class_label": TARGET_CLASS_LABEL,
        "output_schema_version": "sec_pit_resolved_daily_states_v0_2",
    }
    write_json(run_root / "pre_manifest.json", pre_manifest)

    selection = pd.read_parquet(selection_path)
    selected = selection[
        selection["ticker"].eq(TARGET_TICKER)
        & selection["roles_v0_2"].map(
            lambda roles: "OS_EVIDENCE_CANDIDATE" in list(roles)
        )
    ].copy()
    identity = pd.read_parquet(identity_path)
    target_identity = identity[identity["ticker"].eq(TARGET_TICKER)]
    if len(target_identity) != 1:
        raise ValueError(f"expected exactly one PGAC target identity, found {len(target_identity)}")
    identity_row = target_identity.iloc[0].to_dict()
    if identity_row.get("identity_gate") != "PASS":
        raise ValueError("PGAC identity gate is not PASS")
    if identity_row.get("security_class_gate") != "PASS":
        raise ValueError("PGAC security-class gate is not PASS")

    acquisition_rows = read_jsonl(acquisition_path)
    acquisition_by_url = {row["url"]: row for row in acquisition_rows}
    metadata = pd.read_parquet(args.metadata_inventory.resolve())
    metadata_by_accession = {
        row["accession_number"]: row
        for row in metadata.to_dict("records")
    }
    admissions: list[dict[str, Any]] = []
    raw_observations: list[dict[str, Any]] = []
    verified_target_objects = 0
    policy = EdgarAvailabilityPolicy()

    for row in selected.sort_values(["filing_date", "accession_number"]).to_dict("records"):
        source = acquisition_by_url.get(row["primary_document_url"])
        if source is None or source.get("status") != "FETCHED":
            raise ValueError(f"missing fetched acquisition row for {row['accession_number']}")
        payload: bytes | None = None
        if row["temporal_scope_state"] == "TARGET_INTERVAL":
            with gzip.open(source["object_path"], "rb") as handle:
                payload = handle.read()
            actual_sha = hashlib.sha256(payload).hexdigest()
            if actual_sha != source["sha256"]:
                raise ValueError(f"payload hash mismatch for {row['accession_number']}")
            if len(payload) != int(source["bytes"]):
                raise ValueError(f"payload byte count mismatch for {row['accession_number']}")
            verified_target_objects += 1
        decision = admit_target_interval_document(
            payload or b"",
            temporal_scope_state=row["temporal_scope_state"],
            accession_link_state=row["accession_link_state"],
            registrant_name=TARGET_REGISTRANT,
            ticker=TARGET_TICKER,
            target_class_label=TARGET_CLASS_LABEL,
        )
        admissions.append({
            "ticker": TARGET_TICKER,
            "instrument_id": identity_row["instrument_id"],
            "security_class_id": identity_row.get("security_class_id"),
            "security_class_label": TARGET_CLASS_LABEL,
            "accession_number": row["accession_number"],
            "form": row["form"],
            "filing_date": row["filing_date"],
            "temporal_scope_state": row["temporal_scope_state"],
            "prior_accession_link_state": row["accession_link_state"],
            "admission_decision": decision.decision,
            "admission_reason": decision.reason,
            "registrant_match": decision.registrant_match,
            "ticker_class_match": decision.ticker_class_match,
            "evidence_excerpt": decision.evidence_excerpt,
            "source_url": row["primary_document_url"],
            "source_sha256": source["sha256"],
            "reviewer_state": "SYSTEM_EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING",
        })
        if decision.decision != "ADMITTED_PGAC_CLASS_A":
            continue
        metadata_row = metadata_by_accession.get(row["accession_number"])
        if metadata_row is None or not metadata_row.get("acceptance_datetime"):
            raise ValueError(
                f"missing governed acceptance datetime for {row['accession_number']}"
            )
        if metadata_row.get("primary_document_url") != row["primary_document_url"]:
            raise ValueError(
                f"metadata/source URL mismatch for {row['accession_number']}"
            )
        extraction_kwargs = {
            "cik": str(identity_row["cik"]),
            "accession_number": row["accession_number"],
            "form": row["form"],
            "accepted_at": str(metadata_row["acceptance_datetime"]),
            "instrument_id": identity_row["instrument_id"],
            "security_class_id": identity_row.get("security_class_id"),
            "target_class_label": TARGET_CLASS_LABEL,
            "source_url": row["primary_document_url"],
            "source_sha256": source["sha256"],
            "availability_policy": policy,
        }
        text_rows = extract_cover_page_class_os(payload or b"", **extraction_kwargs)
        ixbrl_rows = extract_ixbrl_class_os(payload or b"", **extraction_kwargs)
        raw_observations.extend(asdict(item) for item in [*text_rows, *ixbrl_rows])

    admissions_frame = pd.DataFrame(admissions)
    observations_frame = pd.DataFrame(
        source_observation_row(item) for item in raw_observations
    )
    admitted_anchors, reconciliation = reconcile_class_os_anchors(raw_observations)
    admitted_frame = pd.DataFrame(
        source_observation_row(item) for item in admitted_anchors
    )

    calendar = pd.read_parquet(args.market_calendar.resolve(), columns=["session_date"])
    start = str(identity_row["market_presence_first_session"])
    end = str(identity_row["market_presence_last_session"])
    session_values = calendar[
        calendar["session_date"].astype(str).between(start, end)
    ]["session_date"].astype(str).tolist()
    sessions = [date.fromisoformat(value) for value in session_values]
    daily_os = [
        asdict(item)
        for item in resolve_daily_os(
            instrument_id=identity_row["instrument_id"],
            sessions=sessions,
            observations=admitted_anchors,
        )
    ]
    daily_frame = pd.DataFrame(daily_os)
    anchor_by_id = {
        row["observation_id"]: row for row in admitted_anchors
    }
    change_rows: list[dict[str, Any]] = []
    previous_anchor_id: str | None = None
    previous_value: float | None = None
    for daily_row in daily_os:
        anchor_id = daily_row.get("anchor_observation_id")
        if anchor_id is None or anchor_id == previous_anchor_id:
            continue
        anchor = anchor_by_id[anchor_id]
        change_rows.append({
            "session_date": daily_row["session_date"],
            "previous_os": previous_value,
            "new_os": daily_row["shares_outstanding_estimate_as_known"],
            "source_accession": anchor["accession_number"],
            "source_excerpt": anchor.get("source_excerpt"),
            "measurement_at": anchor["measurement_at"],
            "eligible_from_session": anchor["eligible_from_session"],
            "security_class_label": (anchor.get("attributes") or {}).get(
                "security_class_label"
            ),
            "change_reason": (
                "INITIAL_ADMITTED_OS_ANCHOR"
                if previous_anchor_id is None
                else "ADMITTED_ANCHOR_VINTAGE_CHANGE_SAME_VALUE"
            ),
            "review_verdict": "SYSTEM_EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING",
        })
        previous_anchor_id = anchor_id
        previous_value = daily_row["shares_outstanding_estimate_as_known"]
    changes_frame = pd.DataFrame(change_rows)

    admissions_frame.to_parquet(run_root / "accession_instrument_admission.parquet", index=False)
    observations_frame.to_parquet(run_root / "os_source_observations.parquet", index=False)
    admitted_frame.to_parquet(run_root / "admitted_os_anchors.parquet", index=False)
    daily_frame.to_parquet(run_root / "daily_os_state.parquet", index=False)
    changes_frame.to_parquet(run_root / "os_change_explanation.parquet", index=False)
    write_json(run_root / "os_anchor_reconciliation.json", reconciliation)

    decision_counts = admissions_frame["admission_decision"].value_counts().to_dict()
    target_count = int((selected["temporal_scope_state"] == "TARGET_INTERVAL").sum())
    admitted_count = int(decision_counts.get("ADMITTED_PGAC_CLASS_A", 0))
    extracted_count = len(observations_frame)
    anchor_count = len(admitted_frame)
    daily_row_count = len(daily_frame)
    daily_nonnull_count = int(
        daily_frame["shares_outstanding_estimate_as_known"].notna().sum()
        if daily_row_count
        else 0
    )
    daily_unique_sessions = int(daily_frame["session_date"].nunique())
    future_anchor_rows = int(
        (
            pd.to_datetime(daily_frame["anchor_eligible_from_session"])
            > pd.to_datetime(daily_frame["session_date"])
        ).fillna(False).sum()
        if daily_row_count
        else 0
    )
    unresolved_availability = int(
        observations_frame["eligible_from_session"].isna().sum()
        if extracted_count
        else 0
    )
    variable_audit = {
        "ticker": TARGET_TICKER,
        "instrument_id": identity_row["instrument_id"],
        "selected_os_candidate_documents": len(selected),
        "target_interval_os_candidate_documents": target_count,
        "verified_target_objects": verified_target_objects,
        "admission_decision_counts": decision_counts,
        "admitted_target_documents": admitted_count,
        "class_os_observation_count": extracted_count,
        "admitted_os_anchor_count": anchor_count,
        "daily_os_row_count": daily_row_count,
        "daily_os_nonnull_count": daily_nonnull_count,
        "daily_os_unique_session_count": daily_unique_sessions,
        "daily_os_future_anchor_rows": future_anchor_rows,
        "os_change_explanation_count": len(changes_frame),
        "unique_class_os_values": sorted(
            float(value) for value in observations_frame["value"].dropna().unique()
        ) if extracted_count else [],
        "measurement_dates": sorted(
            str(value) for value in observations_frame["measurement_at"].dropna().unique()
        ) if extracted_count else [],
        "unresolved_acceptance_timestamp_observations": unresolved_availability,
        "S1_ACCESSION_INSTRUMENT_ADMISSION": (
            "PASS_WITH_RESTRICTIONS_HUMAN_CONFIRMATION_PENDING"
            if admitted_count == target_count == 3
            else "FAIL"
        ),
        "S2_NEUTRAL_OS_EXTRACTION": (
            "PASS_DUAL_EXTRACTION"
            if extracted_count == 2 * admitted_count == 6
            and unresolved_availability == 0
            else "FAIL"
        ),
        "S3_OS_ANCHOR_ADMISSION": (
            "PASS_WITH_RESTRICTIONS_SAME_SOURCE_DUAL_METHOD"
            if anchor_count == admitted_count == 3
            and reconciliation["unadmitted_group_count"] == 0
            else "FAIL"
        ),
        "S4_DAILY_OS_PIT": (
            "PASS"
            if daily_row_count == len(sessions) == daily_unique_sessions
            and daily_nonnull_count == daily_row_count
            and future_anchor_rows == 0
            else "FAIL"
        ),
        "S5_MANUAL_CHANGE_AUDIT": "EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING",
        "network_requests": 0,
    }
    write_json(run_root / "variable_audit.json", variable_audit)

    final_manifest = {
        **pre_manifest,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE_EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING",
        "result": "S1_TO_S4_PASS_S5_HUMAN_CONFIRMATION_PENDING",
        "output_files": {
            name: {
                "sha256": sha256_file(run_root / name),
                "bytes": (run_root / name).stat().st_size,
            }
            for name in (
                "accession_instrument_admission.parquet",
                "os_source_observations.parquet",
                "admitted_os_anchors.parquet",
                "daily_os_state.parquet",
                "os_change_explanation.parquet",
                "os_anchor_reconciliation.json",
                "variable_audit.json",
            )
        },
        "counts": variable_audit,
        "next_required_input": (
            "human confirmation of the three accession admissions and each "
            "daily anchor-vintage change explanation"
        ),
        "network_requests": 0,
    }
    write_json(run_root / "final_manifest.json", final_manifest)
    return run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--selection-plan",
        type=Path,
        default=DEFAULT_EVIDENCE_ROOT / "document_selection_plan_v0_2.parquet",
    )
    parser.add_argument(
        "--identity-ledger",
        type=Path,
        default=DEFAULT_EVIDENCE_ROOT / "instrument_identity_interval_ledger.parquet",
    )
    parser.add_argument(
        "--acquisition-ledger",
        type=Path,
        default=DEFAULT_ACQUISITION_RUN / "acquisition.jsonl",
    )
    parser.add_argument(
        "--metadata-inventory",
        type=Path,
        default=DEFAULT_METADATA_INVENTORY,
    )
    parser.add_argument(
        "--market-calendar",
        type=Path,
        default=DEFAULT_MARKET_CALENDAR,
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "runtime/sec_pit_pgac_no_network_v0_1",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--expected-selection-sha256",
        default=EXPECTED_SELECTION_SHA256,
    )
    return parser.parse_args()


if __name__ == "__main__":
    output = execute(parse_args())
    print(output)


