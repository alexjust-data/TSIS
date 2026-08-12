#!/usr/bin/env python
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.blockers import blocker_details
from sec_pit.float_estimate_v2 import resolve_owner_exclusion_float_v0_2
from sec_pit.holders_v3 import build_holder_position_ledger_v0_9
from sec_pit.ownership_class_reconcile import reconcile_multiclass_proxy_positions
from sec_pit.ownership_baseline import (
    BASELINE_FORMS,
    classify_baseline_document,
    classify_missing_opening_baseline_blocker,
)
from sec_pit.ownership_v2 import (
    FORM_345,
    PROXY_FORMS,
    SCHEDULE_FORMS,
    extract_document_identity,
    extract_holder_class_components,
    extract_name_change_events,
    extract_normalized_ownership_snapshots,
    issuer_name_present_in_text,
    issuer_name_match_basis,
    normalized_name_key,
)


def sha256_file(path: Path) -> str:
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
    for source in rows:
        row = dict(source)
        attributes = row.pop("attributes", None)
        if attributes is not None:
            row["attributes_json"] = json.dumps(attributes, sort_keys=True, default=str)
        blockers = row.get("blocker_codes")
        if blockers is not None:
            row["blocker_codes_json"] = json.dumps(blockers, sort_keys=True)
            del row["blocker_codes"]
        normalized.append(row)
    pd.DataFrame(normalized).to_parquet(path, index=False)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def connected_aliases(
    canonical_name: str,
    events: list[dict[str, Any]],
) -> set[str]:
    graph: dict[str, set[str]] = {}
    for event in events:
        left = normalized_name_key(event.get("prior_name"))
        right = normalized_name_key(event.get("new_name"))
        if not left or not right:
            continue
        graph.setdefault(left, set()).add(right)
        graph.setdefault(right, set()).add(left)
    start = normalized_name_key(canonical_name)
    if not start:
        return set()
    found = {start}
    frontier = [start]
    while frontier:
        current = frontier.pop()
        for neighbor in graph.get(current, set()):
            if neighbor not in found:
                found.add(neighbor)
                frontier.append(neighbor)
    return found


def execute(config_path: Path, run_id: str) -> Path:
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("network_requests_authorized") is not False:
        raise ValueError("no-network probe requires network_requests_authorized=false")

    selection_path = Path(config["selection_plan"]).resolve()
    acquisition_path = Path(config["acquisition_ledger"]).resolve()
    metadata_path = Path(config["metadata_inventory"]).resolve()
    daily_os_path = Path(config["daily_os_state"]).resolve()
    split_events_path = Path(config["split_events"]).resolve()
    if not split_events_path.is_file():
        raise FileNotFoundError(split_events_path)
    run_root = Path(config["output_root"]).resolve() / "runs" / run_id
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite run root: {run_root}")
    run_root.mkdir(parents=True)

    selection_hash = sha256_file(selection_path)
    if selection_hash != config["selection_plan_sha256"]:
        raise ValueError("selection-plan hash mismatch")

    component_files = [
        Path(__file__).resolve(),
        SCRIPTS / "sec_pit" / "availability.py",
        SCRIPTS / "sec_pit" / "models.py",
        SCRIPTS / "sec_pit" / "extract.py",
        SCRIPTS / "sec_pit" / "blockers.py",
        SCRIPTS / "sec_pit" / "ownership_html.py",
        SCRIPTS / "sec_pit" / "ownership_v2.py",
        SCRIPTS / "sec_pit" / "ownership_class_reconcile.py",
        SCRIPTS / "sec_pit" / "ownership_baseline.py",
        SCRIPTS / "sec_pit" / "holders.py",
        SCRIPTS / "sec_pit" / "holders_v2.py",
        SCRIPTS / "sec_pit" / "holders_v3.py",
        SCRIPTS / "sec_pit" / "float_estimate.py",
        SCRIPTS / "sec_pit" / "float_estimate_v2.py",
    ]
    pre_manifest = {
        "run_id": run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "mode": "NO_NETWORK_LOCAL_OBJECT_REPLAY",
        "network_requests_authorized": False,
        "config_path": config_path.as_posix(),
        "config_sha256": sha256_file(config_path),
        "selection_plan_path": selection_path.as_posix(),
        "selection_plan_sha256": selection_hash,
        "acquisition_ledger_path": acquisition_path.as_posix(),
        "acquisition_ledger_sha256": sha256_file(acquisition_path),
        "metadata_inventory_path": metadata_path.as_posix(),
        "metadata_inventory_sha256": sha256_file(metadata_path),
        "daily_os_state_path": daily_os_path.as_posix(),
        "daily_os_state_sha256": sha256_file(daily_os_path),
        "split_events_path": split_events_path.as_posix(),
        "split_events_sha256": sha256_file(split_events_path),
        "component_hashes": {
            path.name: sha256_file(path) for path in component_files
        },
        "ticker": config["ticker"],
        "cik": config["cik"],
        "instrument_id": config["instrument_id"],
        "security_class_id": config.get("security_class_id"),
        "target_class_label": config["target_class_label"],
        "governed_interval_state": config.get("governed_interval_state"),
        "methodology_id": config["methodology_id"],
    }
    write_json(run_root / "pre_manifest.json", pre_manifest)

    selection = pd.read_parquet(selection_path)
    ticker_rows = selection[selection["ticker"].eq(config["ticker"])].copy()
    ownership = ticker_rows[
        ticker_rows["roles_v0_2"].map(
            lambda roles: "OWNERSHIP_EVIDENCE_CANDIDATE" in list(roles)
        )
        | ticker_rows.get(
            "stratified_selection_reasons",
            pd.Series([[] for _ in range(len(ticker_rows))], index=ticker_rows.index),
        ).map(
            lambda reasons: bool(
                {
                    "OWNERSHIP_BASELINE_LATEST",
                    "OWNERSHIP_BASELINE_CANDIDATE_CHAIN",
                }
                & set(reasons)
            )
        )
    ].copy()
    acquisition = read_jsonl(acquisition_path)
    acquired_by_url = {row["url"]: row for row in acquisition}
    metadata = pd.read_parquet(metadata_path)
    metadata_by_accession = {
        row["accession_number"]: row for row in metadata.to_dict("records")
    }
    availability = EdgarAvailabilityPolicy()

    payload_by_accession: dict[str, bytes] = {}
    identity_by_accession: dict[str, dict[str, Any]] = {}
    name_change_events: list[dict[str, Any]] = []
    for row in ticker_rows.to_dict("records"):
        acquired = acquired_by_url.get(row["primary_document_url"])
        if not acquired or acquired.get("status") not in {"FETCHED", "FETCHED_REUSED"}:
            raise ValueError(f"missing local object for {row['accession_number']}")
        with gzip.open(acquired["object_path"], "rb") as handle:
            payload = handle.read()
        if hashlib.sha256(payload).hexdigest() != acquired["sha256"]:
            raise ValueError(f"payload hash mismatch for {row['accession_number']}")
        payload_by_accession[row["accession_number"]] = payload
        identity_by_accession[row["accession_number"]] = extract_document_identity(
            payload
        )
        for event in extract_name_change_events(payload):
            name_change_events.append(
                {**event, "source_accession": row["accession_number"]}
            )

    aliases = connected_aliases(config["issuer_name"], name_change_events)
    canonical_name_key = normalized_name_key(config["issuer_name"])
    canonical_name_source_evidence = any(
        issuer_name_present_in_text(config["issuer_name"], identity.get("source_text"))
        for identity in identity_by_accession.values()
    )
    interval_resolution_allowed = (
        config.get("governed_interval_state") != "TICKER_REUSE_CONFLICT"
    )
    target_cusips = {
        str(identity["issuer_cusip"]).upper()
        for accession, identity in identity_by_accession.items()
        if identity.get("issuer_cusip")
        and str(
            ticker_rows.loc[
                ticker_rows["accession_number"].eq(accession),
                "temporal_scope_state",
            ].iloc[0]
        )
        == "TARGET_INTERVAL"
    }

    dispositions: list[dict[str, Any]] = []
    raw_observations: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []
    rows_by_accession: dict[str, list[dict[str, Any]]] = {}
    expected_position_forms = FORM_345 | SCHEDULE_FORMS | set(BASELINE_FORMS)

    for row in ownership.sort_values(["filing_date", "accession_number"]).to_dict(
        "records"
    ):
        accession = row["accession_number"]
        payload = payload_by_accession[accession]
        acquired = acquired_by_url[row["primary_document_url"]]
        metadata_row = metadata_by_accession.get(accession)
        accepted_at = (
            str(metadata_row.get("acceptance_datetime"))
            if metadata_row and metadata_row.get("acceptance_datetime")
            else None
        )
        extracted = extract_normalized_ownership_snapshots(
            payload,
            cik=config["cik"],
            accession_number=accession,
            form=row["form"],
            accepted_at=accepted_at,
            instrument_id=config["instrument_id"],
            security_class_id=config.get("security_class_id"),
            source_url=row["primary_document_url"],
            source_sha256=acquired["sha256"],
            availability_policy=availability,
        )
        rows = [item.to_dict() for item in extracted]
        rows_by_accession[accession] = rows
        raw_observations.extend(rows)
        components.extend(extract_holder_class_components(payload, extracted))

        identity = identity_by_accession[accession]
        issuer_name_key = normalized_name_key(identity.get("issuer_name"))
        cik_match = str(identity.get("issuer_cik") or config["cik"]).zfill(10) == str(
            config["cik"]
        ).zfill(10)
        document_name_match_basis = issuer_name_match_basis(
            config["issuer_name"], identity.get("source_text")
        )
        document_name_evidence = bool(document_name_match_basis)
        name_match = bool(
            issuer_name_key and issuer_name_key in aliases
        ) or document_name_evidence
        cusip_match = bool(
            identity.get("issuer_cusip")
            and str(identity["issuer_cusip"]).upper() in target_cusips
        )
        identity_admitted = (
            interval_resolution_allowed
            and cik_match
            and (name_match or cusip_match)
        )
        identity_admission_basis = None
        if identity_admitted:
            if cusip_match:
                identity_admission_basis = "CLASS_CUSIP_EVIDENCE"
            elif issuer_name_key and issuer_name_key in aliases:
                identity_admission_basis = "NAME_CHANGE_ALIAS_EVIDENCE"
            else:
                identity_admission_basis = document_name_match_basis
        normalized_form = row["form"].upper()
        expects_rows = normalized_form in expected_position_forms
        dispositions.append(
            {
                "accession_number": accession,
                "form": row["form"],
                "filing_date": row["filing_date"],
                "temporal_scope_state": row["temporal_scope_state"],
                "issuer_cik": identity.get("issuer_cik"),
                "issuer_name": identity.get("issuer_name"),
                "issuer_cusip": identity.get("issuer_cusip"),
                "security_class_title": identity.get("security_class_title"),
                "identity_admission_state": (
                    "ADMITTED_BY_NAME_CHANGE_CONTINUITY_OR_CLASS_CUSIP"
                    if identity_admitted
                    else "UNRESOLVED_IDENTITY_OR_CLASS"
                ),
                "identity_admission_basis": identity_admission_basis,
                "structured_position_rows": len(rows),
                "position_rows_expected": expects_rows,
                "extraction_state": (
                    "ROWS_EXTRACTED"
                    if rows
                    else "NO_ROWS_EXPECTED"
                    if not expects_rows
                    else "EXPECTED_ROWS_NOT_EXTRACTED"
                ),
                "source_url": row["primary_document_url"],
                "source_sha256": acquired["sha256"],
            }
        )

    first_session = config["first_observed_session"]
    full_interval_mode = (
        config.get("session_scope_mode") == "FULL_GOVERNED_INTERVAL"
    )
    disposition_by_accession = {
        row["accession_number"]: row for row in dispositions
    }
    baseline_candidates = [
        row
        for row in ownership.to_dict("records")
        if str(row.get("form") or "").upper() in BASELINE_FORMS
        and str(row.get("filing_date") or "")
        <= (
            config["last_observed_session"]
            if full_interval_mode
            else first_session
        )
    ]
    baseline_candidates.sort(
        key=lambda row: (
            str(row.get("filing_date") or ""),
            str(row.get("accession_number") or ""),
        ),
        reverse=not full_interval_mode,
    )
    baseline_resolution: list[dict[str, Any]] = []
    baseline_family_head_accession = (
        str(
            baseline_candidates[-1 if full_interval_mode else 0][
                "accession_number"
            ]
        )
        if baseline_candidates
        else None
    )
    opening_baseline_accession = None
    opening_baseline_eligible = None
    reconciled_proxy: list[dict[str, Any]] = []
    class_readout: dict[str, Any] | None = None
    selected_baseline_count = 0
    for depth, candidate in enumerate(baseline_candidates):
        accession = str(candidate["accession_number"])
        candidate_rows = rows_by_accession.get(accession, [])
        classification = classify_baseline_document(
            payload_by_accession[accession],
            form=str(candidate["form"]),
            extracted_rows=candidate_rows,
        )
        disposition = disposition_by_accession.get(accession, {})
        identity_admitted = disposition.get("identity_admission_state") == (
            "ADMITTED_BY_NAME_CHANGE_CONTINUITY_OR_CLASS_CUSIP"
        )
        candidate_eligible = max(
            (
                str(row.get("eligible_from_session") or "")
                for row in candidate_rows
            ),
            default="",
        )
        candidate_components = [
            row
            for row in components
            if str(row.get("eligible_from_session") or "") <= candidate_eligible
            and disposition_by_accession.get(
                str(row.get("source_accession") or ""), {}
            ).get("identity_admission_state")
            == "ADMITTED_BY_NAME_CHANGE_CONTINUITY_OR_CLASS_CUSIP"
        ]
        candidate_reconciled, candidate_class_readout = (
            reconcile_multiclass_proxy_positions(
                proxy_observations=candidate_rows,
                class_components=candidate_components,
                target_class_label=config["target_class_label"],
            )
        )
        selected = bool(
            identity_admitted
            and classification["baseline_content_complete_candidate"]
            and candidate_class_readout["row_level_class_allocation_complete"]
        )
        baseline_resolution.append(
            {
                "accession_number": accession,
                "form": candidate["form"],
                "filing_date": candidate["filing_date"],
                "fallback_depth": depth,
                "identity_admitted": identity_admitted,
                **classification,
                "class_allocation_complete": candidate_class_readout[
                    "row_level_class_allocation_complete"
                ],
                "selected_as_opening_baseline": selected,
            }
        )
        if selected:
            if opening_baseline_accession is None:
                opening_baseline_accession = accession
                opening_baseline_eligible = candidate_eligible
            reconciled_proxy.extend(candidate_reconciled)
            class_readout = candidate_class_readout
            selected_baseline_count += 1
            if not full_interval_mode:
                break
    if class_readout is None:
        reconciled_proxy, class_readout = reconcile_multiclass_proxy_positions(
            proxy_observations=[],
            class_components=[],
            target_class_label=config["target_class_label"],
        )

    target_rows = []
    for row in raw_observations:
        accession = str(row.get("accession_number") or "")
        disposition = disposition_by_accession.get(accession, {})
        if disposition.get("temporal_scope_state") != "TARGET_INTERVAL":
            continue
        if disposition.get("identity_admission_state") != (
            "ADMITTED_BY_NAME_CHANGE_CONTINUITY_OR_CLASS_CUSIP"
        ):
            continue
        if (row.get("eligible_from_session") or "") > config["last_observed_session"]:
            continue
        if str(row.get("form") or "").upper() in BASELINE_FORMS:
            continue
        target_rows.append(row)
    scoped_observations = reconciled_proxy + target_rows

    broad_ledger, broad_dedup = build_holder_position_ledger_v0_9(
        raw_observations
    )
    class_a_ledger, holder_dedup = build_holder_position_ledger_v0_9(
        scoped_observations
    )
    holder_dedup["broad_source_position_rows"] = broad_dedup[
        "source_position_rows"
    ]

    expected_but_empty = [
        row["accession_number"]
        for row in dispositions
        if row["extraction_state"] == "EXPECTED_ROWS_NOT_EXTRACTED"
    ]
    unresolved_expected_identity = [
        row
        for row in dispositions
        if row["temporal_scope_state"] == "TARGET_INTERVAL"
        and row["structured_position_rows"] > 0
        and row["identity_admission_state"] != (
            "ADMITTED_BY_NAME_CHANGE_CONTINUITY_OR_CLASS_CUSIP"
        )
    ]
    if opening_baseline_accession:
        proxy_disposition = disposition_by_accession[opening_baseline_accession]
        if (
            proxy_disposition["identity_admission_state"]
            != "ADMITTED_BY_NAME_CHANGE_CONTINUITY_OR_CLASS_CUSIP"
            and all(
                row["accession_number"] != opening_baseline_accession
                for row in unresolved_expected_identity
            )
        ):
            unresolved_expected_identity.append(proxy_disposition)
    bridge_complete = bool(
        interval_resolution_allowed
        and canonical_name_source_evidence
        and not unresolved_expected_identity
    )
    methodology_complete = bool(
        reconciled_proxy
        and class_readout["row_level_class_allocation_complete"]
        and holder_dedup["row_level_economic_position_resolution_complete"]
        and bridge_complete
    )
    methodology_blocker_codes: list[str] = []
    if not interval_resolution_allowed:
        methodology_blocker_codes.append("TICKER_REUSE_CONFLICT")
    elif not bridge_complete:
        methodology_blocker_codes.append("INSTRUMENT_INTERVAL_CONFLICT")
    if not opening_baseline_accession and interval_resolution_allowed:
        baseline_blocker = classify_missing_opening_baseline_blocker(
            baseline_resolution
        )
        if baseline_blocker:
            methodology_blocker_codes.append(baseline_blocker)
    if not holder_dedup["row_level_economic_position_resolution_complete"]:
        methodology_blocker_codes.append("HOLDER_OVERLAP_UNRESOLVED")
    methodology_blocker_codes = sorted(set(methodology_blocker_codes))
    coverage = {
        "policy_id": "methodology_scoped_ownership_source_coverage_v0_1",
        "ownership_candidate_documents": len(ownership),
        "ownership_acquired_documents": len(dispositions),
        "ownership_documents_with_rows": sum(
            row["structured_position_rows"] > 0 for row in dispositions
        ),
        "expected_rows_not_extracted_accessions": sorted(expected_but_empty),
        "broad_structured_extraction_complete": not expected_but_empty,
        "methodology_structured_extraction_complete": methodology_complete,
        "methodology_blocker_codes": methodology_blocker_codes,
        "methodology_blockers": blocker_details(methodology_blocker_codes),
        "baseline_family_head_accession": baseline_family_head_accession,
        "opening_baseline_accession": opening_baseline_accession,
        "opening_baseline_eligible_from_session": opening_baseline_eligible,
        "opening_baseline_fallback_depth": next(
            (
                row["fallback_depth"]
                for row in baseline_resolution
                if row["selected_as_opening_baseline"]
            ),
            None,
        ),
        "opening_proxy_accession": opening_baseline_accession,
        "opening_proxy_eligible_from_session": opening_baseline_eligible,
        "baseline_candidates_evaluated": len(baseline_resolution),
        "selected_causal_baseline_count": selected_baseline_count,
        "session_scope_mode": config.get(
            "session_scope_mode", "BOUNDED_TAIL_PROBE"
        ),
        "identity_alias_count": len(aliases),
        "identity_name_change_event_count": len(name_change_events),
        "identity_continuity_complete": bridge_complete,
        "canonical_name_source_evidence": canonical_name_source_evidence,
        "governed_interval_state": config.get("governed_interval_state"),
        "interval_resolution_allowed": interval_resolution_allowed,
        "unresolved_expected_identity_accessions": sorted(
            row["accession_number"] for row in unresolved_expected_identity
        ),
        "target_class_cusips": sorted(target_cusips),
        "status": "PASS_WITH_RESTRICTIONS" if methodology_complete else "FAIL",
    }

    daily_os = pd.read_parquet(daily_os_path).to_dict("records")
    split_events = pd.read_parquet(split_events_path).to_dict("records")
    for row in daily_os:
        session = row.get("session_date")
        if isinstance(session, (date, datetime)):
            row["session_date"] = session.isoformat()[:10]
    daily_float, float_readout = resolve_owner_exclusion_float_v0_2(
        daily_os_rows=daily_os,
        holder_ledger=class_a_ledger,
        ownership_coverage=coverage,
        holder_deduplication=holder_dedup,
        split_events=split_events,
        methodology_authorized=bool(config["methodology_authorized"]),
        methodology_id=config["methodology_id"],
    )

    changes: list[dict[str, Any]] = []
    previous: tuple[Any, ...] | None = None
    for row in daily_float:
        state = (
            row.get("float_owner_exclusion_estimate_as_known"),
            row.get("unique_supported_excluded_shares"),
            row.get("ownership_baseline_accession"),
            row.get("estimation_state"),
        )
        if state == previous:
            continue
        changes.append(
            {
                "session_date": row["session_date"],
                "float_owner_exclusion_estimate_as_known": state[0],
                "unique_supported_excluded_shares": state[1],
                "ownership_baseline_accession": state[2],
                "estimation_state": state[3],
                "review_verdict": "SYSTEM_EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING",
            }
        )
        previous = state

    write_parquet(run_root / "ownership_document_disposition.parquet", dispositions)
    write_parquet(run_root / "ownership_baseline_resolution.parquet", baseline_resolution)
    write_parquet(run_root / "ownership_source_observations.parquet", raw_observations)
    write_parquet(run_root / "ownership_class_components.parquet", components)
    write_parquet(run_root / "holder_position_ledger_broad.parquet", broad_ledger)
    write_parquet(run_root / "holder_position_ledger_class_a.parquet", class_a_ledger)
    write_parquet(run_root / "daily_float_state.parquet", daily_float)
    write_parquet(run_root / "float_change_explanation.parquet", changes)
    write_json(run_root / "identity_name_change_events.json", name_change_events)
    write_json(run_root / "ownership_class_reconciliation.json", class_readout)
    write_json(run_root / "ownership_baseline_resolution.json", baseline_resolution)
    write_json(run_root / "holder_deduplication.json", holder_dedup)
    write_json(run_root / "ownership_source_coverage.json", coverage)
    write_json(run_root / "float_methodology_readout.json", float_readout)

    audit = {
        "S5_OS_MANUAL_GATE": "PASS_HUMAN_CONFIRMED_2026_08_11",
        "S6_NEUTRAL_OWNERSHIP_EXTRACTION": (
            "PASS_WITH_RESTRICTIONS" if coverage["ownership_acquired_documents"] == len(ownership) else "FAIL"
        ),
        "S7_HOLDER_AND_CLASS_RECONCILIATION": (
            "PASS_WITH_RESTRICTIONS" if methodology_complete else "FAIL"
        ),
        "S8_OWNER_EXCLUSION_FLOAT": float_readout["status"],
        "S9_FLOAT_CHANGE_AUDIT": "EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING",
        "network_requests": 0,
        "daily_float_rows": len(daily_float),
        "daily_float_nonnull_rows": sum(
            row.get("float_owner_exclusion_estimate_as_known") is not None
            for row in daily_float
        ),
        "float_change_rows": len(changes),
        "class_reconciliation": class_readout,
        "ownership_coverage": coverage,
        "holder_deduplication": holder_dedup,
        "float_readout": float_readout,
    }
    write_json(run_root / "variable_audit.json", audit)

    output_names = [
        "ownership_document_disposition.parquet",
        "ownership_baseline_resolution.parquet",
        "ownership_source_observations.parquet",
        "ownership_class_components.parquet",
        "holder_position_ledger_broad.parquet",
        "holder_position_ledger_class_a.parquet",
        "daily_float_state.parquet",
        "float_change_explanation.parquet",
        "identity_name_change_events.json",
        "ownership_class_reconciliation.json",
        "ownership_baseline_resolution.json",
        "holder_deduplication.json",
        "ownership_source_coverage.json",
        "float_methodology_readout.json",
        "variable_audit.json",
    ]
    final = {
        **pre_manifest,
        "ended_at_utc": datetime.now(UTC).isoformat(),
        "status": (
            "COMPLETE_EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING"
            if audit["daily_float_nonnull_rows"]
            else "COMPLETE_WITH_BLOCKERS"
        ),
        "result": "S6_TO_S8_EXECUTED_S9_HUMAN_CONFIRMATION_PENDING",
        "network_requests": 0,
        "counts": audit,
        "output_files": {
            name: {
                "sha256": sha256_file(run_root / name),
                "bytes": (run_root / name).stat().st_size,
            }
            for name in output_names
        },
    }
    write_json(run_root / "final_manifest.json", final)
    return run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(args.config, args.run_id))
