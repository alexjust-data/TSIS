#!/usr/bin/env python
from __future__ import annotations

# ruff: noqa: E402
import argparse
import json
import os
import socket
import subprocess
import sys
import traceback
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit import PIPELINE_VERSION
from sec_pit.assignment_restriction_extract import extract_assignment_restriction_events
from sec_pit.availability import EdgarAvailabilityPolicy
from sec_pit.client import SecClient
from sec_pit.extract import (
    extract_companyfacts_os,
    extract_cover_page_os,
    extract_form345_owner_snapshot,
    stable_id,
)
from sec_pit.float_estimate import resolve_owner_exclusion_float
from sec_pit.holders import build_holder_position_ledger
from sec_pit.metadata import (
    COMPANYFACTS_URL,
    SUBMISSIONS_URL,
    filing_roles,
    normalize_cik,
    parse_submissions_root,
    parse_submissions_supplement,
    primary_document_url,
    stratified_primary_selection,
)
from sec_pit.models import InstrumentScope
from sec_pit.ownership_html import HTML_OWNERSHIP_FORMS, extract_html_ownership_snapshots
from sec_pit.reconcile import reconcile_os_anchors
from sec_pit.registration_os_reconcile import reconcile_registration_components_to_os
from sec_pit.resolver import resolve_daily_os
from sec_pit.restriction_clause_extract import extract_restriction_clause_candidates
from sec_pit.restriction_conditions import resolve_registration_component_conditions
from sec_pit.restriction_estimate import resolve_tradability_eligibility
from sec_pit.restriction_event_reconcile import reconcile_assignment_restriction_events
from sec_pit.restriction_extract import (
    extract_effect_event,
    extract_registration_component_candidate,
    extract_registration_scope_clause_candidates,
    extract_selling_holder_share_lots,
    reconcile_registration_to_selling_lots,
    summarize_registration_component_conflicts,
)
from sec_pit.storage import ContentAddressedStore, append_jsonl, atomic_write_json


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def git_value(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def load_scope(instrument_master: Path, *, ticker: str | None, cik: str | None) -> InstrumentScope:
    columns = [
        "instrument_id",
        "ticker",
        "cik",
        "share_class_figi",
        "is_common_stock",
        "valid_from",
        "valid_to",
    ]
    table = pq.read_table(instrument_master, columns=columns)
    frame = table.to_pandas()
    frame["cik"] = (
        frame["cik"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(10)
    )
    if ticker:
        matches = frame[frame["ticker"].str.upper().eq(ticker.upper())]
    else:
        matches = frame[frame["cik"].eq(normalize_cik(cik or ""))]
    if matches.empty:
        raise ValueError("No instrument-master row matches the requested ticker/CIK")
    # A one-ticker pilot must not silently merge multiple share classes.
    common = matches[matches["is_common_stock"].eq(True)]
    candidates = common if not common.empty else matches
    row = candidates.sort_values(["valid_to", "valid_from"], na_position="last").iloc[-1]
    return InstrumentScope(
        instrument_id=str(row["instrument_id"]),
        ticker=str(row["ticker"]),
        cik=normalize_cik(row["cik"]),
        share_class_figi=None if row["share_class_figi"] is None else str(row["share_class_figi"]),
        is_common_stock=None if row["is_common_stock"] is None else bool(row["is_common_stock"]),
        valid_from=None if row["valid_from"] is None else str(row["valid_from"]),
        valid_to=None if row["valid_to"] is None else str(row["valid_to"]),
    )


class RunTelemetry:
    def __init__(self, run_root: Path, manifest: dict[str, Any]) -> None:
        self.run_root = run_root
        self.manifest = manifest
        self.heartbeat_path = run_root / "heartbeat_latest.json"
        self.heartbeat_log = run_root / "heartbeat.jsonl"
        self.log_path = run_root / "run.log"

    def update(self, stage: str, status: str = "RUNNING", **extra: Any) -> None:
        payload = {
            "run_id": self.manifest["run_id"],
            "observed_at_utc": utc_now(),
            "status": status,
            "stage": stage,
            "wrapper_pid": os.getpid(),
            "pid_alive": True,
            "log_path": self.log_path.as_posix(),
            **extra,
        }
        atomic_write_json(self.heartbeat_path, payload)
        append_jsonl(self.heartbeat_log, payload)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"[{payload['observed_at_utc']}] status={status} stage={stage} {json.dumps(extra, default=str)}\n"
            )


def write_parquet(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")


def load_sessions(calendar_root: Path, instrument_id: str) -> list[date]:
    dataset = ds.dataset(calendar_root, format="parquet", partitioning="hive")
    table = dataset.to_table(
        columns=["session_date"],
        filter=(ds.field("dataset_family") == "daily_raw")
        & (ds.field("instrument_id") == instrument_id)
        & (ds.field("expected_session") == True),  # noqa: E712
    )
    return sorted(set(table.column("session_date").to_pylist()))


def enrich_companyfacts_availability(
    observations: list[dict[str, Any]],
    inventory: list[dict[str, Any]],
    policy: EdgarAvailabilityPolicy,
) -> None:
    by_accession = {row["accession_number"]: row for row in inventory}
    for observation in observations:
        if observation.get("extraction_method") != "SEC_COMPANYFACTS_XBRL":
            continue
        filing = by_accession.get(observation.get("accession_number"))
        if not filing:
            continue
        decision = policy.resolve(filing.get("acceptance_datetime"), filing.get("form"))
        observation["filing_accepted_at"] = filing.get("acceptance_datetime")
        observation["eligible_from_session"] = (
            decision.eligible_from_session.isoformat() if decision.eligible_from_session else None
        )
        observation["availability_policy_id"] = decision.policy_id
        observation["causality_state"] = decision.state
        observation["quality_state"] = "CANDIDATE_REQUIRES_RECONCILIATION"


def execute(args: argparse.Namespace) -> int:
    run_id = args.run_id or f"sec_pit_one_ticker_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    run_root = args.output_root / "runs" / run_id
    run_root.mkdir(parents=True, exist_ok=False)
    scope = load_scope(args.instrument_master, ticker=args.ticker, cik=args.cik)
    owner_exclusion_methodology = json.loads(
        args.owner_exclusion_methodology_config.read_text(encoding="utf-8")
    )
    manifest = {
        "run_id": run_id,
        "status": "STARTING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "pipeline_version": PIPELINE_VERSION,
        "command_line": sys.argv,
        "cwd": Path.cwd().as_posix(),
        "host": socket.gethostname(),
        "parent_pid": os.getppid(),
        "wrapper_pid": os.getpid(),
        "git_branch": git_value(["branch", "--show-current"]),
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["status", "--porcelain"])),
        "mode": "execute" if args.execute else "plan",
        "input_roots": [
            args.instrument_master.as_posix(),
            args.owner_exclusion_methodology_config.as_posix(),
        ],
        "owner_exclusion_methodology_id": owner_exclusion_methodology["methodology_id"],
        "output_root": args.output_root.as_posix(),
        "scope": asdict(scope),
        "resume_policy": "new_run_only_content_store_reusable",
        "overwrite_policy": "forbidden",
        "success_criteria": "metadata inventory and OS candidate gates emitted",
        "monitor_command": f'powershell -NoProfile -File "{(SCRIPT_DIR / "monitor_sec_pit_run.ps1").as_posix()}" -RunRoot "{run_root.as_posix()}" -Compact',
    }
    atomic_write_json(run_root / "pre_manifest.json", manifest)
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "run_id": run_id,
            "wrapper_pid": os.getpid(),
            "started_at_utc": utc_now(),
            "expected_alive": True,
        },
    )
    telemetry = RunTelemetry(run_root, manifest)
    telemetry.update("PREFLIGHT", scope=asdict(scope))
    print(manifest["monitor_command"], flush=True)

    plan = {
        "scope": asdict(scope),
        "resources": [
            {"type": "submissions_root", "url": SUBMISSIONS_URL.format(cik=scope.cik)},
            {"type": "companyfacts", "url": COMPANYFACTS_URL.format(cik=scope.cik)},
        ],
        "primary_document_policy": "selected forms only; no complete submission by default",
    }
    atomic_write_json(run_root / "acquisition_plan.json", plan)
    if not args.execute:
        telemetry.update("PLAN_COMPLETE", status="COMPLETE")
        atomic_write_json(
            run_root / "final_manifest.json",
            {**manifest, "status": "COMPLETE", "ended_at_utc": utc_now(), "result": "PLAN_ONLY"},
        )
        return 0
    if not args.user_agent:
        raise ValueError("--user-agent is required with --execute")

    store = ContentAddressedStore(args.output_root / "objects")
    client = SecClient(
        user_agent=args.user_agent,
        store=store,
        acquisition_log=run_root / "acquisition.jsonl",
        requests_per_second=args.requests_per_second,
    )
    availability = EdgarAvailabilityPolicy()

    telemetry.update("ACQUIRE_METADATA")
    submissions_result, submissions = client.fetch_json(
        SUBMISSIONS_URL.format(cik=scope.cik), f"submissions/{scope.cik}.json"
    )
    companyfacts_result, companyfacts = client.fetch_json(
        COMPANYFACTS_URL.format(cik=scope.cik), f"companyfacts/{scope.cik}.json"
    )
    if submissions is None:
        raise RuntimeError("SEC submissions root acquisition failed")

    records, supplements = parse_submissions_root(submissions, submissions_result.object_path or "")
    for supplement_name in supplements:
        result, payload = client.fetch_json(
            f"https://data.sec.gov/submissions/{supplement_name}",
            f"submissions/{scope.cik}/{supplement_name}",
        )
        if payload is not None:
            records.extend(
                parse_submissions_supplement(scope.cik, payload, result.object_path or "")
            )

    inventory: list[dict[str, Any]] = []
    for record in records:
        row = asdict(record)
        row["roles"] = filing_roles(record)
        row["primary_document_url"] = primary_document_url(record)
        decision = availability.resolve(record.acceptance_datetime, record.form)
        row["eligible_from_session"] = (
            decision.eligible_from_session.isoformat() if decision.eligible_from_session else None
        )
        row["availability_state"] = decision.state
        row["availability_policy_id"] = decision.policy_id
        inventory.append(row)
    inventory.sort(key=lambda item: (item.get("filing_date") or "", item["accession_number"]))
    write_parquet(run_root / "filing_inventory.parquet", inventory)
    telemetry.update("INVENTORY_COMPLETE", filing_count=len(inventory))

    observations: list[dict[str, Any]] = []
    if companyfacts is not None and companyfacts_result.sha256:
        observations.extend(
            item.to_dict()
            for item in extract_companyfacts_os(
                companyfacts,
                instrument_id=scope.instrument_id,
                security_class_id=scope.share_class_figi,
                source_url=companyfacts_result.url,
                source_sha256=companyfacts_result.sha256,
                availability_policy=availability,
            )
        )

    enrich_companyfacts_availability(observations, inventory, availability)

    selected = stratified_primary_selection(inventory, args.max_primary_documents)
    write_parquet(run_root / "selected_primary_documents.parquet", selected)
    selected_filing_bytes_upper_bound = sum(int(row.get("filing_size_bytes") or 0) for row in selected)
    atomic_write_json(
        run_root / "selected_primary_documents_readout.json",
        {
            "selected_count": len(selected),
            "selected_filing_bytes_upper_bound": selected_filing_bytes_upper_bound,
            "selected_filing_gib_upper_bound": round(
                selected_filing_bytes_upper_bound / (1024**3), 6
            ),
            "size_semantics": (
                "SEC filing size is a conservative planning proxy; it is not the "
                "primary-document response size."
            ),
            "complete_submission_default": False,
            "exhibits_default": False,
        },
    )
    if args.metadata_only:
        gates = {
            "G0_IDENTITY": "PASS_WITH_RESTRICTIONS",
            "METADATA_PREFLIGHT": "PASS",
            "PRIMARY_DOCUMENT_ACQUISITION": "NOT_EXECUTED",
            "DOWNSTREAM_GATES": "NOT_EXECUTED",
        }
        atomic_write_json(run_root / "gate_readout.json", gates)
        telemetry.update(
            "METADATA_PREFLIGHT_COMPLETE",
            status="COMPLETE",
            selected_count=len(selected),
            selected_filing_bytes_upper_bound=selected_filing_bytes_upper_bound,
        )
        atomic_write_json(
            run_root / "final_manifest.json",
            {
                **manifest,
                "status": "COMPLETE",
                "ended_at_utc": utc_now(),
                "result": "METADATA_ONLY",
                "filing_count": len(inventory),
                "selected_primary_document_count": len(selected),
                "selected_filing_bytes_upper_bound": selected_filing_bytes_upper_bound,
                "gates": gates,
            },
        )
        return 0
    valid_from_session = scope.valid_from[:10] if scope.valid_from else None
    valid_to_session = scope.valid_to[:10] if scope.valid_to else None

    def ownership_in_instrument_scope(row: dict[str, Any]) -> bool:
        eligible = row.get("eligible_from_session")
        if not eligible:
            return False
        return (valid_from_session is None or eligible >= valid_from_session) and (
            valid_to_session is None or eligible <= valid_to_session
        )

    ownership_broad_accessions = {
        row["accession_number"]
        for row in inventory
        if "OWNERSHIP_EVIDENCE_CANDIDATE" in row["roles"]
    }
    ownership_scope_accessions = {
        row["accession_number"]
        for row in inventory
        if "OWNERSHIP_EVIDENCE_CANDIDATE" in row["roles"] and ownership_in_instrument_scope(row)
    }
    restriction_scope_accessions = {
        row["accession_number"]
        for row in inventory
        if "RESTRICTION_EVIDENCE_CANDIDATE" in row["roles"] and ownership_in_instrument_scope(row)
    }
    restriction_selected_count = sum(
        row["accession_number"] in restriction_scope_accessions for row in selected
    )
    ownership_inventory_count = len(ownership_scope_accessions)
    ownership_selected_count = sum(
        row["accession_number"] in ownership_scope_accessions for row in selected
    )
    ownership_acquired_count = 0
    restriction_acquired_count = 0
    effect_expected_accessions: set[str] = set()
    effect_extracted_accessions: set[str] = set()
    registration_component_expected_accessions: set[str] = set()
    registration_component_extracted_accessions: set[str] = set()
    structured_owner_accessions: set[str] = set()
    structured_owner_accessions_with_rows: set[str] = set()
    structured_owner_position_rows = 0
    structured_owner_expected_rows: set[str] = set()
    structured_owner_expected_but_empty: set[str] = set()
    telemetry.update("ACQUIRE_SELECTED_PRIMARY", selected_count=len(selected))
    for index, row in enumerate(selected, 1):
        result = client.fetch(
            row["primary_document_url"],
            f"filings/{scope.cik}/{row['accession_number']}/primary/{row['primary_document']}",
        )
        if result.status == "FETCHED" and result.object_path and result.sha256:
            payload = store.read(Path(result.object_path))
            if "OWNERSHIP_EVIDENCE_CANDIDATE" in row["roles"]:
                if row["accession_number"] in ownership_scope_accessions:
                    ownership_acquired_count += 1
                decision = availability.resolve(row["acceptance_datetime"], row["form"])
                observations.append(
                    {
                        "observation_id": stable_id(
                            "ownership_document", scope.cik, row["accession_number"]
                        ),
                        "observation_type": "OWNERSHIP_DOCUMENT_EVIDENCE",
                        "cik": scope.cik,
                        "accession_number": row["accession_number"],
                        "form": row["form"],
                        "instrument_id": scope.instrument_id,
                        "security_class_id": scope.share_class_figi,
                        "value": None,
                        "unit": None,
                        "measurement_at": row.get("report_date"),
                        "effective_at": None,
                        "filing_accepted_at": row["acceptance_datetime"],
                        "eligible_from_session": decision.eligible_from_session.isoformat()
                        if decision.eligible_from_session
                        else None,
                        "availability_policy_id": decision.policy_id,
                        "source_url": result.url,
                        "source_sha256": result.sha256,
                        "source_excerpt": None,
                        "extraction_method": "SEC_PRIMARY_DOCUMENT_ACQUISITION_V0_1",
                        "quality_state": "REQUIRES_STRUCTURED_EXTRACTION",
                        "causality_state": decision.state,
                        "attributes": {"roles": row["roles"]},
                    }
                )
            if (
                "RESTRICTION_EVIDENCE_CANDIDATE" in row["roles"]
                and row["accession_number"] in restriction_scope_accessions
            ):
                restriction_acquired_count += 1
                decision = availability.resolve(row["acceptance_datetime"], row["form"])
                observations.append(
                    {
                        "observation_id": stable_id(
                            "restriction_document", scope.cik, row["accession_number"]
                        ),
                        "observation_type": "RESTRICTION_DOCUMENT_EVIDENCE",
                        "cik": scope.cik,
                        "accession_number": row["accession_number"],
                        "form": row["form"],
                        "instrument_id": scope.instrument_id,
                        "security_class_id": scope.share_class_figi,
                        "value": None,
                        "unit": None,
                        "measurement_at": row.get("report_date"),
                        "effective_at": None,
                        "filing_accepted_at": row["acceptance_datetime"],
                        "eligible_from_session": decision.eligible_from_session.isoformat()
                        if decision.eligible_from_session
                        else None,
                        "availability_policy_id": decision.policy_id,
                        "source_url": result.url,
                        "source_sha256": result.sha256,
                        "source_excerpt": None,
                        "extraction_method": "SEC_RESTRICTION_DOCUMENT_ACQUISITION_V0_1",
                        "quality_state": "REQUIRES_EVENT_AND_SHARE_LOT_EXTRACTION",
                        "causality_state": decision.state,
                        "attributes": {"roles": row["roles"]},
                    }
                )
            if row["accession_number"] in restriction_scope_accessions:
                observations.extend(
                    item.to_dict()
                    for item in extract_restriction_clause_candidates(
                        payload,
                        cik=scope.cik,
                        accession_number=row["accession_number"],
                        form=row["form"],
                        accepted_at=row["acceptance_datetime"],
                        instrument_id=scope.instrument_id,
                        security_class_id=scope.share_class_figi,
                        source_url=result.url,
                        source_sha256=result.sha256,
                        availability_policy=availability,
                    )
                )
                observations.extend(
                    item.to_dict()
                    for item in extract_assignment_restriction_events(
                        payload,
                        cik=scope.cik,
                        accession_number=row["accession_number"],
                        form=row["form"],
                        accepted_at=row["acceptance_datetime"],
                        instrument_id=scope.instrument_id,
                        security_class_id=scope.share_class_figi,
                        source_url=result.url,
                        source_sha256=result.sha256,
                        availability_policy=availability,
                    )
                )
            observations.extend(
                item.to_dict()
                for item in extract_cover_page_os(
                    payload,
                    cik=scope.cik,
                    accession_number=row["accession_number"],
                    form=row["form"],
                    accepted_at=row["acceptance_datetime"],
                    instrument_id=scope.instrument_id,
                    security_class_id=scope.share_class_figi,
                    source_url=result.url,
                    source_sha256=result.sha256,
                    availability_policy=availability,
                )
            )
            effect_rows = [
                item.to_dict()
                for item in extract_effect_event(
                    payload,
                    cik=scope.cik,
                    accession_number=row["accession_number"],
                    form=row["form"],
                    accepted_at=row["acceptance_datetime"],
                    instrument_id=scope.instrument_id,
                    security_class_id=scope.share_class_figi,
                    source_url=result.url,
                    source_sha256=result.sha256,
                    availability_policy=availability,
                )
            ]
            if (
                row["form"].upper() == "EFFECT"
                and row["accession_number"] in restriction_scope_accessions
            ):
                effect_expected_accessions.add(row["accession_number"])
                if effect_rows:
                    effect_extracted_accessions.add(row["accession_number"])
            observations.extend(effect_rows)
            registration_rows = [
                item.to_dict()
                for item in extract_registration_component_candidate(
                    payload,
                    cik=scope.cik,
                    accession_number=row["accession_number"],
                    form=row["form"],
                    accepted_at=row["acceptance_datetime"],
                    instrument_id=scope.instrument_id,
                    security_class_id=scope.share_class_figi,
                    source_url=result.url,
                    source_sha256=result.sha256,
                    availability_policy=availability,
                )
            ]
            if (
                row["form"].upper() == "424B3"
                and row["accession_number"] in restriction_scope_accessions
            ):
                registration_component_expected_accessions.add(row["accession_number"])
                if registration_rows:
                    registration_component_extracted_accessions.add(row["accession_number"])
            observations.extend(registration_rows)
            registration_scope_rows = [
                item.to_dict()
                for item in extract_registration_scope_clause_candidates(
                    payload,
                    cik=scope.cik,
                    accession_number=row["accession_number"],
                    form=row["form"],
                    accepted_at=row["acceptance_datetime"],
                    instrument_id=scope.instrument_id,
                    security_class_id=scope.share_class_figi,
                    source_url=result.url,
                    source_sha256=result.sha256,
                    availability_policy=availability,
                )
            ]
            observations.extend(registration_scope_rows)
            selling_holder_rows = [
                item.to_dict()
                for item in extract_selling_holder_share_lots(
                    payload,
                    cik=scope.cik,
                    accession_number=row["accession_number"],
                    form=row["form"],
                    accepted_at=row["acceptance_datetime"],
                    instrument_id=scope.instrument_id,
                    security_class_id=scope.share_class_figi,
                    source_url=result.url,
                    source_sha256=result.sha256,
                    availability_policy=availability,
                )
            ]
            observations.extend(selling_holder_rows)
            normalized_form = row["form"].upper()
            owner_rows: list[dict[str, Any]] = []
            if normalized_form in {"3", "3/A", "4", "4/A", "5", "5/A"}:
                owner_rows = [
                    item.to_dict()
                    for item in extract_form345_owner_snapshot(
                        payload,
                        cik=scope.cik,
                        accession_number=row["accession_number"],
                        form=row["form"],
                        accepted_at=row["acceptance_datetime"],
                        source_url=result.url,
                        source_sha256=result.sha256,
                        availability_policy=availability,
                    )
                ]
                structured_owner_accessions.add(row["accession_number"])
            elif normalized_form in HTML_OWNERSHIP_FORMS:
                owner_rows = [
                    item.to_dict()
                    for item in extract_html_ownership_snapshots(
                        payload,
                        cik=scope.cik,
                        accession_number=row["accession_number"],
                        form=row["form"],
                        accepted_at=row["acceptance_datetime"],
                        instrument_id=scope.instrument_id,
                        security_class_id=scope.share_class_figi,
                        source_url=result.url,
                        source_sha256=result.sha256,
                        availability_policy=availability,
                    )
                ]
                structured_owner_accessions.add(row["accession_number"])
            expects_position_rows = (
                normalized_form == "DEF 14A"
                or normalized_form.startswith("SC 13")
                or normalized_form.startswith("SCHEDULE 13")
            )
            if expects_position_rows:
                structured_owner_expected_rows.add(row["accession_number"])
                if not owner_rows:
                    structured_owner_expected_but_empty.add(row["accession_number"])
            observations.extend(owner_rows)
            if owner_rows:
                structured_owner_accessions_with_rows.add(row["accession_number"])
                structured_owner_position_rows += len(owner_rows)
        if index % 25 == 0 or index == len(selected):
            telemetry.update(
                "ACQUIRE_SELECTED_PRIMARY",
                completed=index,
                total=len(selected),
                observation_count=len(observations),
            )

    unique = {row["observation_id"]: row for row in observations}
    observations = sorted(
        unique.values(),
        key=lambda item: (item.get("eligible_from_session") or "", item["observation_id"]),
    )
    admitted_anchors, reconciliation = reconcile_os_anchors(observations)
    observations.extend(admitted_anchors)
    observations.sort(
        key=lambda item: (item.get("eligible_from_session") or "", item["observation_id"])
    )
    atomic_write_json(run_root / "os_anchor_reconciliation.json", reconciliation)
    ownership_coverage = {
        "ownership_broad_inventory_count": len(ownership_broad_accessions),
        "ownership_inventory_count": ownership_inventory_count,
        "ownership_selected_count": ownership_selected_count,
        "ownership_acquired_count": ownership_acquired_count,
        "structured_owner_accession_count": len(
            structured_owner_accessions & ownership_scope_accessions
        ),
        "structured_owner_accessions_with_rows": len(
            structured_owner_accessions_with_rows & ownership_scope_accessions
        ),
        "structured_owner_position_rows_broad": structured_owner_position_rows,
        "instrument_valid_from_session": valid_from_session,
        "instrument_valid_to_session": valid_to_session,
        "structured_owner_expected_rows_count": len(
            structured_owner_expected_rows & ownership_scope_accessions
        ),
        "structured_owner_expected_but_empty_count": len(
            structured_owner_expected_but_empty & ownership_scope_accessions
        ),
        "structured_owner_expected_but_empty_accessions": sorted(
            structured_owner_expected_but_empty & ownership_scope_accessions
        ),
        "structured_extraction_attempt_complete": (
            len(structured_owner_accessions & ownership_scope_accessions)
            == ownership_inventory_count
        ),
        "acquisition_complete": ownership_acquired_count == ownership_inventory_count,
        "structured_extraction_complete": (
            len(structured_owner_accessions & ownership_scope_accessions)
            == ownership_inventory_count
            and not (structured_owner_expected_but_empty & ownership_scope_accessions)
        ),
    }
    ownership_coverage["status"] = (
        "PASS_WITH_RESTRICTIONS" if ownership_coverage["acquisition_complete"] else "FAIL"
    )
    atomic_write_json(run_root / "ownership_source_coverage.json", ownership_coverage)
    broad_holder_ledger, broad_holder_deduplication = build_holder_position_ledger(observations)
    scoped_holder_observations = [
        row
        for row in observations
        if row.get("observation_type") == "HOLDER_POSITION_SNAPSHOT"
        and ownership_in_instrument_scope(row)
    ]
    holder_ledger, holder_deduplication = build_holder_position_ledger(scoped_holder_observations)
    holder_deduplication["broad_source_position_rows"] = broad_holder_deduplication[
        "source_position_rows"
    ]
    atomic_write_json(run_root / "holder_deduplication.json", holder_deduplication)
    write_parquet(run_root / "holder_position_ledger_broad.parquet", broad_holder_ledger)
    write_parquet(run_root / "holder_position_ledger.parquet", holder_ledger)
    write_parquet(run_root / "source_observations.parquet", observations)
    sessions = load_sessions(args.session_calendar_root, scope.instrument_id)
    daily_os = [
        asdict(item)
        for item in resolve_daily_os(
            instrument_id=scope.instrument_id,
            sessions=sessions,
            observations=observations,
        )
    ]
    write_parquet(run_root / "daily_os_state.parquet", daily_os)
    daily_float, float_readout = resolve_owner_exclusion_float(
        daily_os_rows=daily_os,
        holder_ledger=holder_ledger,
        ownership_coverage=ownership_coverage,
        holder_deduplication=holder_deduplication,
        methodology_authorized=owner_exclusion_methodology["experimental_execution_authorized"],
        methodology_id=owner_exclusion_methodology["methodology_id"],
    )
    write_parquet(run_root / "daily_float_state.parquet", daily_float)
    atomic_write_json(run_root / "float_methodology_readout.json", float_readout)

    restriction_events = [
        row
        for row in observations
        if row.get("observation_type") == "SHARE_RESTRICTION_EVENT"
        and ownership_in_instrument_scope(row)
    ]
    restriction_clause_candidates = [
        row
        for row in observations
        if row.get("observation_type") == "SHARE_RESTRICTION_CLAUSE_CANDIDATE"
        and ownership_in_instrument_scope(row)
    ]
    write_parquet(
        run_root / "restriction_clause_candidate_ledger.parquet",
        restriction_clause_candidates,
    )
    restriction_clause_types = sorted(
        {
            row.get("attributes", {}).get("restriction_clause_type")
            for row in restriction_clause_candidates
            if row.get("attributes", {}).get("restriction_clause_type")
        }
    )
    restriction_clause_readout = {
        "status": (
            "PASS_WITH_RESTRICTIONS" if restriction_clause_candidates else "BLOCKED_BY_INPUT_GATES"
        ),
        "candidate_rows": len(restriction_clause_candidates),
        "source_accessions": len(
            {row.get("accession_number") for row in restriction_clause_candidates}
        ),
        "clause_type_counts": {
            clause_type: sum(
                row.get("attributes", {}).get("restriction_clause_type") == clause_type
                for row in restriction_clause_candidates
            )
            for clause_type in restriction_clause_types
        },
        "share_lot_linked_rows": 0,
        "condition_resolved_rows": 0,
        "tradable_supply_confirmed_rows": 0,
    }
    atomic_write_json(
        run_root / "restriction_clause_candidate_readout.json",
        restriction_clause_readout,
    )
    assignment_restriction_events = [
        row
        for row in observations
        if row.get("observation_type") == "SHARE_RESTRICTION_EVENT_CANDIDATE"
        and ownership_in_instrument_scope(row)
    ]
    write_parquet(
        run_root / "assignment_restriction_event_ledger.parquet",
        assignment_restriction_events,
    )
    assignment_event_types = sorted(
        {
            row.get("attributes", {}).get("restriction_event_type")
            for row in assignment_restriction_events
            if row.get("attributes", {}).get("restriction_event_type")
        }
    )
    assignment_restriction_readout = {
        "status": (
            "PASS_WITH_RESTRICTIONS" if assignment_restriction_events else "BLOCKED_BY_INPUT_GATES"
        ),
        "event_candidate_rows": len(assignment_restriction_events),
        "event_type_counts": {
            event_type: sum(
                row.get("attributes", {}).get("restriction_event_type") == event_type
                for row in assignment_restriction_events
            )
            for event_type in assignment_event_types
        },
        "source_numeric_conflict_rows": sum(
            row.get("quality_state") == "SOURCE_NUMERIC_CONFLICT"
            for row in assignment_restriction_events
        ),
        "share_lot_linked_rows": 0,
        "tradable_supply_confirmed_rows": 0,
    }
    atomic_write_json(
        run_root / "assignment_restriction_event_readout.json",
        assignment_restriction_readout,
    )
    (
        reconciled_assignment_restriction_events,
        assignment_restriction_reconciliation_readout,
    ) = reconcile_assignment_restriction_events(assignment_restriction_events)
    write_parquet(
        run_root / "assignment_restriction_event_reconciled_ledger.parquet",
        reconciled_assignment_restriction_events,
    )
    atomic_write_json(
        run_root / "assignment_restriction_event_reconciliation_readout.json",
        assignment_restriction_reconciliation_readout,
    )
    registration_components = [
        row
        for row in observations
        if row.get("observation_type") == "REGISTRATION_SHARE_COMPONENT_CANDIDATE"
        and ownership_in_instrument_scope(row)
    ]
    write_parquet(
        run_root / "registration_component_ledger.parquet",
        registration_components,
    )
    registration_scope_components = [
        row
        for row in observations
        if row.get("observation_type") == "REGISTRATION_SCOPE_COMPONENT_CANDIDATE"
        and ownership_in_instrument_scope(row)
    ]
    write_parquet(
        run_root / "registration_scope_component_ledger.parquet",
        registration_scope_components,
    )
    registration_scope_file_numbers = {
        row.get("attributes", {}).get("file_number")
        for row in registration_scope_components
        if row.get("attributes", {}).get("file_number")
    }
    registration_scope_classifications = sorted(
        {
            row.get("attributes", {}).get("component_classification")
            for row in registration_scope_components
            if row.get("attributes", {}).get("component_classification")
        }
    )
    registration_scope_classification_counts = {
        classification: sum(
            row.get("attributes", {}).get("component_classification") == classification
            for row in registration_scope_components
        )
        for classification in registration_scope_classifications
    }
    registration_scope_unresolved_count = registration_scope_classification_counts.get(
        "UNRESOLVED", 0
    )
    selling_holder_share_lots = [
        row
        for row in observations
        if row.get("observation_type") == "SELLING_HOLDER_SHARE_LOT_CANDIDATE"
        and ownership_in_instrument_scope(row)
    ]
    write_parquet(
        run_root / "selling_holder_share_lot_ledger.parquet",
        selling_holder_share_lots,
    )
    selling_lot_file_numbers = {
        row.get("attributes", {}).get("file_number")
        for row in selling_holder_share_lots
        if row.get("attributes", {}).get("file_number")
    }
    effect_file_numbers = {
        row.get("attributes", {}).get("file_number")
        for row in restriction_events
        if row.get("attributes", {}).get("file_number")
    }
    registration_file_numbers = {
        row.get("attributes", {}).get("file_number")
        for row in registration_components
        if row.get("attributes", {}).get("file_number")
    }
    registration_selling_lot_reconciliation = reconcile_registration_to_selling_lots(
        registration_components,
        selling_holder_share_lots,
    )
    registration_selling_lot_mismatches = {
        file_number: evidence
        for file_number, evidence in registration_selling_lot_reconciliation.items()
        if evidence.get("status") == "MISMATCH"
    }
    registration_selling_lot_mixed_issuer_partials = {
        file_number: evidence
        for file_number, evidence in registration_selling_lot_reconciliation.items()
        if evidence.get("status") == "PARTIAL_MATCH_MIXED_ISSUER_ISSUANCE"
    }
    registration_component_source_conflicts = summarize_registration_component_conflicts(
        registration_components
    )
    registration_component_conditions, component_condition_readout = (
        resolve_registration_component_conditions(
            registration_scope_components=registration_scope_components,
            effect_events=restriction_events,
        )
    )
    write_parquet(
        run_root / "registration_component_condition_ledger.parquet",
        registration_component_conditions,
    )
    atomic_write_json(
        run_root / "registration_component_condition_readout.json",
        component_condition_readout,
    )
    registration_os_reconciliation, registration_os_readout = (
        reconcile_registration_components_to_os(
            component_condition_rows=registration_component_conditions,
            daily_os_rows=daily_os,
        )
    )
    write_parquet(
        run_root / "registration_component_os_reconciliation_ledger.parquet",
        registration_os_reconciliation,
    )
    atomic_write_json(
        run_root / "registration_component_os_reconciliation_readout.json",
        registration_os_readout,
    )
    restriction_coverage = {
        "restriction_inventory_count": len(restriction_scope_accessions),
        "restriction_clause_candidate_readout": restriction_clause_readout,
        "assignment_restriction_event_readout": assignment_restriction_readout,
        "assignment_restriction_event_reconciliation_readout": (
            assignment_restriction_reconciliation_readout
        ),
        "assignment_restriction_event_row_count": len(assignment_restriction_events),
        "assignment_restriction_economic_event_row_count": len(
            reconciled_assignment_restriction_events
        ),
        "restriction_clause_candidate_row_count": len(restriction_clause_candidates),
        "restriction_selected_count": restriction_selected_count,
        "restriction_acquired_count": restriction_acquired_count,
        "acquisition_complete": (restriction_acquired_count == len(restriction_scope_accessions)),
        "effect_expected_count": len(effect_expected_accessions),
        "effect_extracted_count": len(effect_extracted_accessions),
        "effect_extraction_complete": (effect_expected_accessions == effect_extracted_accessions),
        "registration_component_expected_count": len(registration_component_expected_accessions),
        "registration_component_extracted_count": len(registration_component_extracted_accessions),
        "registration_file_number_count": len(registration_file_numbers),
        "registration_scope_component_row_count": len(registration_scope_components),
        "registration_scope_component_file_number_count": len(registration_scope_file_numbers),
        "registration_scope_component_classification_counts": (
            registration_scope_classification_counts
        ),
        "registration_scope_component_unresolved_count": (
            registration_scope_classification_counts.get("UNRESOLVED", 0)
        ),
        "registration_scope_component_classification_complete": (
            registration_scope_unresolved_count == 0
        ),
        "registration_selling_lot_reconciliation": (registration_selling_lot_reconciliation),
        "registration_selling_lot_mismatch_count": len(registration_selling_lot_mismatches),
        "registration_selling_lot_mixed_issuer_partial_count": len(
            registration_selling_lot_mixed_issuer_partials
        ),
        "registration_component_source_conflicts": (registration_component_source_conflicts),
        "registration_component_source_conflict_count": len(
            registration_component_source_conflicts
        ),
        "registration_component_condition_readout": component_condition_readout,
        "registration_component_os_reconciliation_readout": registration_os_readout,
        "registration_component_os_reconciliation_row_count": len(registration_os_reconciliation),
        "registration_component_condition_row_count": len(registration_component_conditions),
        "registration_component_tradable_supply_confirmed_rows": (
            component_condition_readout["tradable_supply_confirmed_rows"]
        ),
        "effect_file_number_count": len(effect_file_numbers),
        "selling_holder_share_lot_row_count": len(selling_holder_share_lots),
        "selling_holder_share_lot_file_number_count": len(selling_lot_file_numbers),
        "registration_to_selling_lot_file_number_links": len(
            registration_file_numbers & selling_lot_file_numbers
        ),
        "unlinked_registration_file_numbers": sorted(
            registration_file_numbers - selling_lot_file_numbers
        ),
        "selling_lot_rows_exceeding_current_beneficial": sum(
            bool(row.get("attributes", {}).get("offered_exceeds_current_beneficial"))
            for row in selling_holder_share_lots
        ),
        "effect_to_registration_file_number_links": len(
            effect_file_numbers & registration_file_numbers
        ),
        "unlinked_effect_file_numbers": sorted(effect_file_numbers - registration_file_numbers),
        "structured_extraction_complete": False,
        "condition_resolution_complete": False,
        "methodology_authorized": False,
        "restriction_event_count": len(restriction_events),
        "status": "BLOCKED_BY_INPUT_GATES",
        "blocker_codes": [
            *(
                ["SELLING_HOLDER_LOT_RECONCILIATION_MISMATCH"]
                if registration_selling_lot_mismatches
                else []
            ),
            *(
                ["REGISTRATION_COMPONENT_SOURCE_CONFLICT"]
                if registration_component_source_conflicts
                else []
            ),
            *(
                ["REGISTRATION_SCOPE_COMPONENTS_UNRESOLVED"]
                if registration_scope_unresolved_count
                else []
            ),
            "RESTRICTION_STRUCTURED_EXTRACTION_INCOMPLETE",
            "RESTRICTION_CONDITIONS_UNRESOLVED",
            "TRADABILITY_METHODOLOGY_NOT_AUTHORIZED",
        ],
    }
    atomic_write_json(run_root / "restriction_source_coverage.json", restriction_coverage)
    daily_tradability, tradability_readout = resolve_tradability_eligibility(
        daily_float_rows=daily_float,
        restriction_events=restriction_events,
        restriction_coverage=restriction_coverage,
    )
    write_parquet(run_root / "daily_tradability_state.parquet", daily_tradability)
    atomic_write_json(run_root / "tradability_methodology_readout.json", tradability_readout)

    gates = {
        "G0_IDENTITY_AND_SECURITY_CLASS": "PASS" if scope.cik and scope.instrument_id else "FAIL",
        "G1_EDGAR_METADATA_COMPLETENESS": "PASS" if inventory else "FAIL",
        "G2_AVAILABILITY_POLICY": "PASS_WITH_RESTRICTIONS"
        if any(row.get("eligible_from_session") for row in inventory)
        else "FAIL",
        "G3_OS_ANCHOR_EXTRACTION": "PASS_WITH_RESTRICTIONS" if observations else "FAIL",
        "G4_OS_EVENT_RECONCILIATION": reconciliation["status"],
        "G5_OWNERSHIP_SOURCE_COVERAGE": ownership_coverage["status"],
        "G6_HOLDER_DEDUPLICATION": holder_deduplication["status"],
        "G7_OWNER_EXCLUSION_METHODOLOGY": float_readout["status"],
        "G8_RESTRICTION_AND_TRADABILITY": tradability_readout["status"],
        "G9_CORPORATE_ACTION_ALIGNMENT": "NOT_EXECUTED",
        "G10_PRESESSION_MARKET_CAP": "NOT_EXECUTED",
        "G11_HISTORICAL_CUSIP": "NOT_EXECUTED",
        "G12_INSTITUTIONAL_13F": "NOT_EXECUTED",
        "G13_CASH_DEBT_AND_EV": "NOT_EXECUTED",
        "G14_DAILY_PIT_RESOLUTION": "PASS_WITH_RESTRICTIONS" if daily_os else "FAIL",
        "G15_STORAGE_AND_REACQUISITION": "PASS"
        if all(item.get("source_sha256") for item in observations)
        else "PASS_WITH_RESTRICTIONS",
        "G16_MANUAL_CHANGE_EXPLANATION": "NOT_EXECUTED",
    }
    atomic_write_json(run_root / "gate_readout.json", gates)
    telemetry.update(
        "COMPLETE",
        status="COMPLETE",
        filing_count=len(inventory),
        observation_count=len(observations),
        daily_os_rows=len(daily_os),
        daily_float_rows=len(daily_float),
        daily_tradability_rows=len(daily_tradability),
    )
    atomic_write_json(
        run_root / "final_manifest.json",
        {
            **manifest,
            "status": "COMPLETE",
            "ended_at_utc": utc_now(),
            "filing_count": len(inventory),
            "observation_count": len(observations),
            "daily_os_rows": len(daily_os),
            "daily_float_rows": len(daily_float),
            "daily_tradability_rows": len(daily_tradability),
            "gates": gates,
        },
    )
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Governed one-ticker SEC PIT pilot")
    value.add_argument(
        "--instrument-master",
        type=Path,
        default=Path(
            r"G:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
        ),
    )
    value.add_argument(
        "--output-root", type=Path, default=Path(r"D:\TSIS\fundamental_context\sec_pit_v0_1")
    )
    value.add_argument(
        "--session-calendar-root",
        type=Path,
        default=Path(
            r"G:\TSIS\data\data_foundation_outputs\expected_data_calendar\expected_data_calendar_v0_1"
        ),
    )
    group = value.add_mutually_exclusive_group(required=True)
    group.add_argument("--ticker")
    group.add_argument("--cik")
    value.add_argument("--run-id")
    value.add_argument("--execute", action="store_true")
    value.add_argument(
        "--metadata-only",
        action="store_true",
        help="Acquire metadata and emit a document forecast without primary documents.",
    )
    value.add_argument("--user-agent", default=os.environ.get("SEC_USER_AGENT"))
    value.add_argument("--requests-per-second", type=float, default=5.0)
    value.add_argument(
        "--owner-exclusion-methodology-config",
        type=Path,
        default=Path(
            r"C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs"
            r"\sec_pit_owner_exclusion_methodology_v0_1.json"
        ),
    )
    value.add_argument("--max-primary-documents", type=int, default=100)
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        return execute(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
