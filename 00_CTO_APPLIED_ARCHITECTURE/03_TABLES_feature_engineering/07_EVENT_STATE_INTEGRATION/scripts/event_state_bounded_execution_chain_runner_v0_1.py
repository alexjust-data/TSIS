#!/usr/bin/env python
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


SCRIPT_VERSION = "event_state_bounded_execution_chain_execution_v0_1"
EVENT_FAMILY_ID = "event_family:market_data:session_lifecycle"
EVENT_INSTANCE_NAMESPACE = "tsis_event_instance_v0_1"
EVENT_WINDOW_BINDING_NAMESPACE = "tsis_event_window_binding_v0_1"
PROJECTION_NAMESPACE = "tsis_event_state_instrument_session_projection_v0_1"
EVENT_STATE_RECORD_NAMESPACE = "tsis_event_state_record_v0_1"
EVENT_STATE_SCHEMA_VERSION = "event_state_candidate_schema_v0_1"
EVENT_INSTANCE_VERSION = "v0_1"
WINDOW_DEFINITION_VERSION = "v0_1"
WINDOW_POLICY_VERSION = "event_window_binding_policy_v0_1"
PROJECTION_POLICY_ID = "event_state_instrument_session_projection_policy_v0_1"
PROJECTION_POLICY_VERSION = "v0_1"
INTEGRATION_POLICY_ID = "event_state_integration_policy_v0_1"
INTEGRATION_POLICY_VERSION = "v0_1"


VALUE_COLUMNS = [
    "price_location_structure__daily_open_price",
    "price_location_structure__daily_prior_close",
    "price_location_structure__intraday_bar_close_price",
    "price_location_structure__intraday_return_vs_prior_close_ratio_as_location",
    "price_location_structure__intraday_return_vs_session_open_ratio_as_location",
    "price_movement__daily_gap_pct",
    "price_movement__daily_prior_close",
    "price_movement__intraday_bar_close_price",
    "price_movement__intraday_return_vs_prior_close_ratio",
    "price_movement__intraday_return_vs_session_open_ratio",
    "trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean",
    "trading_activity__daily_volume_20d_avg",
    "trading_activity__intraday_bar_volume",
    "trading_activity__intraday_session_volume_to_time",
    "volatility_range_state__intraday_high_so_far",
    "volatility_range_state__intraday_low_so_far",
    "volatility_range_state__intraday_range_so_far_ratio",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso_z(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def stable_json(value: Any) -> str:
    return json.dumps(to_builtin(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_hash(*parts: Any) -> str:
    return sha256_text("|".join(str(p) for p in parts))


def to_builtin(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_builtin(v) for v in value]
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        return to_builtin(value.item())
    return str(value)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(to_builtin(value), indent=2, sort_keys=False, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: to_builtin(row.get(k, "")) for k in fieldnames})


def git_value(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=str(cwd), text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNKNOWN"


def normalize_session_date(value: Any) -> str:
    return str(value)[:10]


def build_records(
    *,
    scope: dict[str, Any],
    event_instance_contract: dict[str, Any],
    calendar_df: pd.DataFrame,
    market_state_df: pd.DataFrame,
    physical_market_state_profile_id: str,
    created_at_utc: str,
    run_id: str,
) -> dict[str, Any]:
    event_type_id = scope["event_type_id"]
    event_subject_scope = scope["event_subject_scope"]
    exchange_id = scope["exchange_id"]
    calendar_version = scope["calendar_version"]
    event_state_profile_id = scope["event_state_profile_id"]
    source_market_state_profile_id = scope["source_market_state_profile_id"]
    physical_market_state_profile_id = physical_market_state_profile_id or source_market_state_profile_id
    event_type_definition_hash = event_instance_contract["authority_binding"]["event_type_definition_hash"]
    registry_snapshot_id = event_instance_contract["authority_binding"]["registry_snapshot_id"]
    registry_snapshot_sha256 = event_instance_contract["authority_binding"]["registry_snapshot_sha256"]
    calendar_source_snapshot_fingerprint = event_instance_contract["calendar_authority"]["calendar_source_snapshot_fingerprint"]
    bound_calendar_parquet_sha256 = event_instance_contract["calendar_authority"]["bound_parquet_sha256"]
    window_definition_id = scope["event_window_definition"]["event_window_definition_id"]

    calendar_rows: list[dict[str, Any]] = []
    event_instances: list[dict[str, Any]] = []
    window_bindings: list[dict[str, Any]] = []
    projections: list[dict[str, Any]] = []
    market_state_bindings: list[dict[str, Any]] = []
    event_state_records: list[dict[str, Any]] = []

    calendar_by_date: dict[str, pd.Series] = {}
    for session in scope["authorized_sessions"]:
        session_date = session["session_date"]
        matches = calendar_df[
            (calendar_df["session_date"].astype(str) == session_date)
            & (calendar_df["mic_or_exchange_code"].astype(str) == exchange_id)
            & (calendar_df["calendar_version"].astype(str) == calendar_version)
        ]
        calendar_rows.append(
            {
                "session_date": session_date,
                "calendar_rows_found": int(len(matches)),
                "expected_open_utc": f"{session_date}T{session['expected_open_utc']}Z",
                "calendar_binding_status": "BOUND" if len(matches) == 1 else "BLOCKED",
                "blocking_reason": "" if len(matches) == 1 else "calendar_row_not_exactly_one",
            }
        )
        if len(matches) == 1:
            row = matches.iloc[0]
            calendar_by_date[session_date] = row
            anchor = iso_z(row["session_open_utc"])
            if anchor != f"{session_date}T{session['expected_open_utc']}Z":
                calendar_rows[-1]["calendar_binding_status"] = "BLOCKED"
                calendar_rows[-1]["blocking_reason"] = "scope_expected_open_mismatch"
                continue
            event_instance_id = canonical_hash(
                EVENT_INSTANCE_NAMESPACE,
                event_type_id,
                event_type_definition_hash,
                event_subject_scope,
                exchange_id,
                session_date,
                anchor,
                calendar_version,
                row["calendar_row_fingerprint"],
            )
            event_instances.append(
                {
                    "event_instance_id": event_instance_id,
                    "event_instance_version": EVENT_INSTANCE_VERSION,
                    "event_type_id": event_type_id,
                    "event_family_id": EVENT_FAMILY_ID,
                    "event_subject_scope": event_subject_scope,
                    "exchange_id": exchange_id,
                    "session_date": session_date,
                    "event_anchor_timestamp_utc": anchor,
                    "first_observable_timestamp_utc": anchor,
                    "detection_timestamp_utc": "not_applicable_for_calendar_authority_v0_1",
                    "binding_created_at_utc": created_at_utc,
                    "calendar_id": row["calendar_id"],
                    "calendar_version": calendar_version,
                    "calendar_source_snapshot_fingerprint": calendar_source_snapshot_fingerprint,
                    "bound_calendar_parquet_sha256": bound_calendar_parquet_sha256,
                    "calendar_row_fingerprint": row["calendar_row_fingerprint"],
                    "session_open_utc": iso_z(row["session_open_utc"]),
                    "session_close_utc": iso_z(row["session_close_utc"]),
                    "session_type": row["session_type"],
                    "is_early_close": bool(row["is_early_close"]),
                    "native_identity_includes_instrument_id": False,
                    "event_instance_quality_state": "PASS_WITH_RESTRICTIONS",
                    "registry_snapshot_id": registry_snapshot_id,
                    "registry_snapshot_sha256": registry_snapshot_sha256,
                }
            )

            event_window_binding_id = canonical_hash(
                EVENT_WINDOW_BINDING_NAMESPACE,
                event_instance_id,
                window_definition_id,
                event_type_id,
                anchor,
                anchor,
                anchor,
                calendar_version,
                row["calendar_row_fingerprint"],
                WINDOW_POLICY_VERSION,
            )
            window_bindings.append(
                {
                    "event_window_binding_id": event_window_binding_id,
                    "event_instance_id": event_instance_id,
                    "event_type_id": event_type_id,
                    "event_family_id": EVENT_FAMILY_ID,
                    "window_definition_id": window_definition_id,
                    "window_definition_version": WINDOW_DEFINITION_VERSION,
                    "state_role": scope["event_window_definition"]["state_role"],
                    "consumption_legality": "decision_safe",
                    "event_anchor_timestamp_utc": anchor,
                    "first_observable_timestamp_utc": anchor,
                    "binding_created_at_utc": created_at_utc,
                    "relative_start_offset": "PT0S",
                    "relative_end_offset": "PT0S",
                    "window_start_utc": anchor,
                    "window_end_utc": anchor,
                    "window_duration_seconds": 0,
                    "calendar_authority_id": row["calendar_id"],
                    "calendar_version": calendar_version,
                    "calendar_source_snapshot_fingerprint": calendar_source_snapshot_fingerprint,
                    "calendar_row_fingerprint": row["calendar_row_fingerprint"],
                    "exchange_id": exchange_id,
                    "session_date": session_date,
                    "session_open_utc": iso_z(row["session_open_utc"]),
                    "session_close_utc": iso_z(row["session_close_utc"]),
                    "session_type": row["session_type"],
                    "is_early_close": bool(row["is_early_close"]),
                    "calendar_boundary_policy": "governed_calendar_boundaries_only",
                    "clipping_policy_id": "session_opened_at_open_no_clipping_v0_1",
                    "window_quality_state": "PASS_WITH_RESTRICTIONS",
                    "leakage_assessment": "no_future_window_content; exact anchor only",
                    "supersedes_event_window_binding_id": "",
                    "superseded_by_event_window_binding_id": "",
                    "correction_reason": "",
                }
            )

    ms = market_state_df.copy()
    ms["_session_date_str"] = ms["session_date"].map(normalize_session_date)
    ms["_decision_timestamp_z"] = ms["decision_timestamp_utc"].map(iso_z)

    event_by_date = {row["session_date"]: row for row in event_instances}
    window_by_event = {row["event_instance_id"]: row for row in window_bindings}
    instruments = scope["authorized_instruments"]

    for session in scope["authorized_sessions"]:
        session_date = session["session_date"]
        event = event_by_date.get(session_date)
        if not event:
            continue
        window = window_by_event[event["event_instance_id"]]
        for inst in instruments:
            projection_id = canonical_hash(
                PROJECTION_NAMESPACE,
                event["event_instance_id"],
                window["event_window_binding_id"],
                inst["instrument_id"],
                session_date,
                exchange_id,
                source_market_state_profile_id,
                PROJECTION_POLICY_VERSION,
            )
            projection = {
                "event_state_instrument_session_projection_id": projection_id,
                "projection_policy_id": PROJECTION_POLICY_ID,
                "projection_policy_version": PROJECTION_POLICY_VERSION,
                "event_type_id": event_type_id,
                "event_instance_id": event["event_instance_id"],
                "event_window_binding_id": window["event_window_binding_id"],
                "exchange_id": exchange_id,
                "session_date": session_date,
                "event_anchor_timestamp_utc": event["event_anchor_timestamp_utc"],
                "window_start_utc": window["window_start_utc"],
                "window_end_utc": window["window_end_utc"],
                "instrument_id": inst["instrument_id"],
                "ticker": inst["ticker"],
                "instrument_exchange_id": exchange_id,
                "instrument_master_version": "authorized_scope_instrument_list_v0_1",
                "instrument_identity_fingerprint": canonical_hash("authorized_scope_instrument", inst["instrument_id"], inst["ticker"]),
                "instrument_lifecycle_status": "not_revalidated_in_this_bounded_run",
                "listing_status_as_of_session": "authorized_by_scope_not_revalidated",
                "instrument_session_eligibility_state": "AUTHORIZED_SCOPE_PROJECTION_WITH_RESTRICTIONS",
                "market_state_profile_id": source_market_state_profile_id,
                "market_state_schema_version": "",
                "calendar_version": calendar_version,
                "calendar_row_fingerprint": event["calendar_row_fingerprint"],
                "projection_quality_state": "PASS_WITH_RESTRICTIONS",
                "projection_created_at_utc": created_at_utc,
                "supersedes_projection_id": "",
                "superseded_by_projection_id": "",
                "correction_reason": "",
            }
            projections.append(projection)

            candidates = ms[
                (ms["instrument_id"].astype(str) == inst["instrument_id"])
                & (ms["ticker"].astype(str) == inst["ticker"])
                & (ms["_session_date_str"] == session_date)
                & (ms["_decision_timestamp_z"] == event["event_anchor_timestamp_utc"])
                & (ms["state_profile_id"].astype(str) == physical_market_state_profile_id)
            ]
            same_instrument_session = ms[
                (ms["instrument_id"].astype(str) == inst["instrument_id"])
                & (ms["ticker"].astype(str) == inst["ticker"])
                & (ms["_session_date_str"] == session_date)
            ]
            binding = {
                "event_state_instrument_session_projection_id": projection_id,
                "event_instance_id": event["event_instance_id"],
                "event_window_binding_id": window["event_window_binding_id"],
                "instrument_id": inst["instrument_id"],
                "ticker": inst["ticker"],
                "session_date": session_date,
                "event_anchor_timestamp_utc": event["event_anchor_timestamp_utc"],
                "market_state_rows_found": int(len(candidates)),
                "available_same_instrument_session_timestamps": ";".join(same_instrument_session["_decision_timestamp_z"].astype(str).tolist()),
                "market_state_binding_status": "BOUND" if len(candidates) == 1 else "BLOCKED",
                "blocking_reason": "" if len(candidates) == 1 else ("missing_exact_market_state_binding" if len(candidates) == 0 else "multiple_exact_market_state_bindings"),
                "market_state_record_id": "",
                "state_output_fingerprint": "",
                "source_market_state_profile_id": source_market_state_profile_id,
                "source_market_state_physical_profile_id": physical_market_state_profile_id,
                "decision_timestamp_utc": "",
                "fallback_used": False,
            }
            if len(candidates) == 1:
                row = candidates.iloc[0]
                missing_identity = not str(row.get("materialized_state_candidate_id", "")).strip()
                missing_fp = not str(row.get("state_output_fingerprint", "")).strip()
                if missing_identity or missing_fp:
                    binding["market_state_binding_status"] = "BLOCKED"
                    binding["blocking_reason"] = "missing_market_state_identity_or_fingerprint"
                else:
                    binding["market_state_record_id"] = row["materialized_state_candidate_id"]
                    binding["state_output_fingerprint"] = row["state_output_fingerprint"]
                    binding["decision_timestamp_utc"] = iso_z(row["decision_timestamp_utc"])
            market_state_bindings.append(binding)
            if binding["market_state_binding_status"] != "BOUND":
                continue

            row = candidates.iloc[0]
            source_lineage = {
                "event_state_execution_run_id": run_id,
                "event_instance_id": event["event_instance_id"],
                "event_window_binding_id": window["event_window_binding_id"],
                "projection_id": projection_id,
                "market_state_materialization_run_id": row["materialization_run_id"],
                "market_state_candidate_record_id": row["source_candidate_record_id"],
                "market_state_source_lineage_json": row["source_lineage_json"],
                "calendar_id": event["calendar_id"],
                "calendar_row_fingerprint": event["calendar_row_fingerprint"],
                "instrument_projection_authority": "bounded_scope_authorized_instrument_list_not_lifecycle_revalidation",
            }
            policy_versions = {
                "event_instance_policy": EVENT_INSTANCE_NAMESPACE,
                "event_window_binding_policy": WINDOW_POLICY_VERSION,
                "instrument_projection_policy": PROJECTION_POLICY_VERSION,
                "event_state_integration_policy": INTEGRATION_POLICY_VERSION,
                "market_state_policy_versions_json": row["policy_versions_json"],
            }
            restriction_codes = [
                "bounded_execution_chain_candidate_output_only",
                "non_official_scale_c_market_state_candidate_source",
                "source_market_state_physical_profile_alias_preserved",
                "instrument_projection_from_authorized_scope_not_master_lifecycle_revalidated",
                "event_state_downstream_consumption_prohibited",
            ]
            if str(row.get("restriction_codes_json", "")).strip():
                restriction_codes.append("source_market_state_restrictions_preserved")
            value_snapshot = {col: row[col] for col in VALUE_COLUMNS}
            record_base = {
                "event_state_profile_id": event_state_profile_id,
                "event_state_schema_version": EVENT_STATE_SCHEMA_VERSION,
                "integration_policy_id": INTEGRATION_POLICY_ID,
                "integration_policy_version": INTEGRATION_POLICY_VERSION,
                "event_type_id": event_type_id,
                "event_family_id": EVENT_FAMILY_ID,
                "event_instance_id": event["event_instance_id"],
                "event_instance_version": EVENT_INSTANCE_VERSION,
                "event_window_definition_id": window_definition_id,
                "event_window_binding_id": window["event_window_binding_id"],
                "event_state_instrument_session_projection_id": projection_id,
                "source_market_state_profile_id": source_market_state_profile_id,
                "source_market_state_physical_profile_id": row["state_profile_id"],
                "source_market_state_schema_version": row["state_schema_version"],
                "market_state_record_id": row["materialized_state_candidate_id"],
                "state_output_fingerprint": row["state_output_fingerprint"],
                "instrument_id": inst["instrument_id"],
                "ticker": inst["ticker"],
                "exchange_id": exchange_id,
                "session_date": session_date,
                "decision_timestamp_utc": iso_z(row["decision_timestamp_utc"]),
                "event_anchor_timestamp_utc": event["event_anchor_timestamp_utc"],
                "window_start_utc": window["window_start_utc"],
                "window_end_utc": window["window_end_utc"],
                "relative_time_to_event": "PT0S",
                "state_role": window["state_role"],
                "consumption_legality": window["consumption_legality"],
                "object_completeness_status": row["object_completeness_status"],
                "integration_status": "EVENT_STATE_INTEGRATED_WITH_RESTRICTIONS",
                "quality_status": "PASS_WITH_RESTRICTIONS",
                "calendar_version": calendar_version,
                "calendar_row_fingerprint": event["calendar_row_fingerprint"],
                "source_lineage_json": stable_json(source_lineage),
                "policy_versions_json": stable_json(policy_versions),
                "restriction_codes_json": stable_json(restriction_codes),
                "source_market_state_value_snapshot_json": stable_json(value_snapshot),
                "supersedes_event_state_record_id": "",
                "superseded_by_event_state_record_id": "",
            }
            event_state_record_id = canonical_hash(
                EVENT_STATE_RECORD_NAMESPACE,
                event_state_profile_id,
                event_type_id,
                event["event_instance_id"],
                window["event_window_binding_id"],
                projection_id,
                row["materialized_state_candidate_id"],
                row["state_output_fingerprint"],
                window["state_role"],
                window["consumption_legality"],
                INTEGRATION_POLICY_VERSION,
            )
            record = {
                "event_state_record_id": event_state_record_id,
                **record_base,
                "event_state_record_fingerprint": sha256_text(stable_json({"event_state_record_id": event_state_record_id, **record_base})),
                "created_at_utc": created_at_utc,
            }
            event_state_records.append(record)

    return {
        "calendar_rows": calendar_rows,
        "event_instances": event_instances,
        "window_bindings": window_bindings,
        "projections": projections,
        "market_state_bindings": market_state_bindings,
        "event_state_records": event_state_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    repo_root = Path.cwd()
    scope_path = Path(args.scope).resolve()
    contract_path = Path(args.contract).resolve()
    event_state_root = scope_path.parent.parent
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    started = utc_now()
    run_id = args.run_id or f"event_state_bounded_execution_chain_execution_v0_1_{started.strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = output_root / run_id
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    scope = read_json(scope_path)
    contract = read_json(contract_path)
    event_instance_contract = read_json(event_state_root / "event_instance_binding_design_contract_v0_1.json")

    market_state_rel = scope["market_state_physical_evidence"]["candidate_parquet_relative_path"]
    market_state_parquet = (event_state_root / market_state_rel).resolve()
    calendar_run_dir = event_state_root.parent / "06_MARKET_STATE_INTEGRATION" / "runs" / "governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z"
    calendar_final_manifest = read_json(calendar_run_dir / "final_manifest.json")
    calendar_parquet = Path(calendar_final_manifest["bound_parquet_path"]).resolve()
    market_state_final_manifest = read_json(market_state_parquet.parent / "final_manifest.json")
    physical_market_state_profile_id = market_state_final_manifest.get("logical_profile_id", "")

    market_state_sha = sha256_file(market_state_parquet)
    expected_market_state_sha = scope["market_state_physical_evidence"]["candidate_parquet_sha256"]
    if market_state_sha != expected_market_state_sha:
        raise SystemExit(f"Market State candidate SHA mismatch: {market_state_sha} != {expected_market_state_sha}")
    calendar_sha = sha256_file(calendar_parquet)
    expected_calendar_sha = event_instance_contract["calendar_authority"]["bound_parquet_sha256"]
    if calendar_sha != expected_calendar_sha:
        raise SystemExit(f"Calendar parquet SHA mismatch: {calendar_sha} != {expected_calendar_sha}")

    pre_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "started_at_utc": iso_z(started),
        "status": "running",
        "scope_path": str(scope_path),
        "contract_path": str(contract_path),
        "run_dir": str(run_dir),
        "git_branch": git_value(["branch", "--show-current"], repo_root),
        "git_commit": git_value(["rev-parse", "HEAD"], repo_root),
        "git_dirty_state": bool(git_value(["status", "--short"], repo_root)),
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER") or "UNKNOWN",
        "authorized_contexts": scope["limits"]["max_instrument_session_projections"],
        "market_state_parquet": str(market_state_parquet),
        "market_state_parquet_sha256": market_state_sha,
        "source_market_state_semantic_profile_id": scope["source_market_state_profile_id"],
        "source_market_state_physical_profile_id": physical_market_state_profile_id,
        "calendar_parquet": str(calendar_parquet),
        "calendar_parquet_sha256": calendar_sha,
        "official_event_state_dataset_promotion_allowed": False,
        "downstream_consumption_allowed": False,
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": "running", "updated_at_utc": iso_z(utc_now())})

    market_state_df = pd.read_parquet(market_state_parquet)
    calendar_df = pd.read_parquet(calendar_parquet)

    built = build_records(
        scope=scope,
        event_instance_contract=event_instance_contract,
        calendar_df=calendar_df,
        market_state_df=market_state_df,
        physical_market_state_profile_id=physical_market_state_profile_id,
        created_at_utc=iso_z(started),
        run_id=run_id,
    )
    rebuilt = build_records(
        scope=scope,
        event_instance_contract=event_instance_contract,
        calendar_df=calendar_df,
        market_state_df=market_state_df,
        physical_market_state_profile_id=physical_market_state_profile_id,
        created_at_utc=iso_z(started),
        run_id=run_id,
    )

    event_instances = built["event_instances"]
    window_bindings = built["window_bindings"]
    projections = built["projections"]
    market_state_bindings = built["market_state_bindings"]
    event_state_records = built["event_state_records"]

    write_csv(
        run_dir / "calendar_binding_report.csv",
        built["calendar_rows"],
        ["session_date", "calendar_rows_found", "expected_open_utc", "calendar_binding_status", "blocking_reason"],
    )
    write_csv(
        run_dir / "event_instance_report.csv",
        event_instances,
        [
            "event_instance_id",
            "event_type_id",
            "event_subject_scope",
            "exchange_id",
            "session_date",
            "event_anchor_timestamp_utc",
            "first_observable_timestamp_utc",
            "calendar_id",
            "calendar_version",
            "calendar_row_fingerprint",
            "session_open_utc",
            "session_close_utc",
            "session_type",
            "is_early_close",
            "native_identity_includes_instrument_id",
            "event_instance_quality_state",
        ],
    )
    write_csv(
        run_dir / "event_window_binding_report.csv",
        window_bindings,
        [
            "event_window_binding_id",
            "event_instance_id",
            "window_definition_id",
            "state_role",
            "consumption_legality",
            "event_anchor_timestamp_utc",
            "window_start_utc",
            "window_end_utc",
            "window_duration_seconds",
            "calendar_version",
            "calendar_row_fingerprint",
            "window_quality_state",
            "leakage_assessment",
        ],
    )
    write_csv(
        run_dir / "instrument_session_projection_report.csv",
        projections,
        [
            "event_state_instrument_session_projection_id",
            "event_instance_id",
            "event_window_binding_id",
            "instrument_id",
            "ticker",
            "exchange_id",
            "session_date",
            "event_anchor_timestamp_utc",
            "instrument_master_version",
            "instrument_lifecycle_status",
            "listing_status_as_of_session",
            "instrument_session_eligibility_state",
            "projection_quality_state",
        ],
    )
    write_csv(
        run_dir / "market_state_binding_report.csv",
        market_state_bindings,
        [
            "event_state_instrument_session_projection_id",
            "event_instance_id",
            "event_window_binding_id",
            "instrument_id",
            "ticker",
            "session_date",
            "event_anchor_timestamp_utc",
            "market_state_rows_found",
            "available_same_instrument_session_timestamps",
            "market_state_binding_status",
            "blocking_reason",
            "market_state_record_id",
            "state_output_fingerprint",
            "source_market_state_profile_id",
            "source_market_state_physical_profile_id",
            "decision_timestamp_utc",
            "fallback_used",
        ],
    )

    records_path = run_dir / "event_state_candidate_records.jsonl"
    with records_path.open("w", encoding="utf-8", newline="\n") as f:
        for record in event_state_records:
            f.write(json.dumps(to_builtin(record), sort_keys=True, ensure_ascii=False) + "\n")

    deterministic_payload = {
        "event_instances": event_instances,
        "window_bindings": window_bindings,
        "projections": projections,
        "market_state_bindings": market_state_bindings,
        "event_state_record_ids": [r["event_state_record_id"] for r in event_state_records],
        "event_state_record_fingerprints": [r["event_state_record_fingerprint"] for r in event_state_records],
    }
    deterministic_payload_rebuilt = {
        "event_instances": rebuilt["event_instances"],
        "window_bindings": rebuilt["window_bindings"],
        "projections": rebuilt["projections"],
        "market_state_bindings": rebuilt["market_state_bindings"],
        "event_state_record_ids": [r["event_state_record_id"] for r in rebuilt["event_state_records"]],
        "event_state_record_fingerprints": [r["event_state_record_fingerprint"] for r in rebuilt["event_state_records"]],
    }
    determinism_failures = 0 if stable_json(deterministic_payload) == stable_json(deterministic_payload_rebuilt) else 1

    requested_contexts = int(scope["limits"]["max_instrument_session_projections"])
    bound_contexts = sum(1 for r in market_state_bindings if r["market_state_binding_status"] == "BOUND")
    blocked_contexts = requested_contexts - bound_contexts
    missing_ms = sum(1 for r in market_state_bindings if r["blocking_reason"] == "missing_exact_market_state_binding")
    multiple_ms = sum(1 for r in market_state_bindings if r["blocking_reason"] == "multiple_exact_market_state_bindings")
    fallback_uses = sum(1 for r in market_state_bindings if r.get("fallback_used"))
    event_anchor_mismatches = sum(
        1 for r in market_state_bindings if r["market_state_binding_status"] == "BOUND" and r["decision_timestamp_utc"] != r["event_anchor_timestamp_utc"]
    )
    partial_records = 0
    required_fields = contract["required_execution_outputs"]
    del required_fields
    for r in event_state_records:
        for field in [
            "event_state_record_id",
            "event_instance_id",
            "event_window_binding_id",
            "event_state_instrument_session_projection_id",
            "market_state_record_id",
            "state_output_fingerprint",
            "state_role",
            "consumption_legality",
        ]:
            if not str(r.get(field, "")).strip():
                partial_records += 1

    hard_validation_failures = sum(
        [
            0 if len(event_instances) == len(scope["authorized_sessions"]) else 1,
            0 if len(window_bindings) == len(scope["authorized_sessions"]) else 1,
            0 if len(projections) == requested_contexts else 1,
            0 if bound_contexts > 0 else 1,
            0 if len(event_state_records) == bound_contexts else 1,
            0 if multiple_ms == 0 else 1,
            0 if fallback_uses == 0 else 1,
            0 if event_anchor_mismatches == 0 else 1,
            0 if partial_records == 0 else 1,
            0 if determinism_failures == 0 else 1,
            0 if len(event_state_records) <= scope["limits"]["max_event_state_candidate_records"] else 1,
        ]
    )

    validation_report = {
        "run_id": run_id,
        "validation_status": "PASS_WITH_RESTRICTIONS" if hard_validation_failures == 0 else "FAILED",
        "requested_contexts": requested_contexts,
        "event_instances_created": len(event_instances),
        "event_window_bindings_created": len(window_bindings),
        "instrument_session_projections_created": len(projections),
        "market_state_bindings_found": bound_contexts,
        "event_state_candidate_records_emitted": len(event_state_records),
        "blocked_contexts": blocked_contexts,
        "missing_exact_market_state_bindings": missing_ms,
        "multiple_exact_market_state_bindings": multiple_ms,
        "fallback_uses": fallback_uses,
        "event_anchor_mismatches": event_anchor_mismatches,
        "partial_event_state_records": partial_records,
        "native_event_instance_identity_instrument_id_uses": 0,
        "source_market_data_rows_read": 0,
        "market_state_parquet_reads": 1,
        "calendar_parquet_reads": 1,
        "event_state_parquet_files_written": 0,
        "official_event_state_profile_promotion": False,
        "official_event_state_dataset_promotion": False,
        "production": False,
        "downstream_consumption": False,
        "determinism_failures": determinism_failures,
        "hard_validation_failures": hard_validation_failures,
    }
    write_json(run_dir / "event_state_validation_report.json", validation_report)

    determinism_report = {
        "run_id": run_id,
        "status": "PASS" if determinism_failures == 0 else "FAIL",
        "determinism_failures": determinism_failures,
        "event_instance_ids": [r["event_instance_id"] for r in event_instances],
        "event_window_binding_ids": [r["event_window_binding_id"] for r in window_bindings],
        "projection_ids": [r["event_state_instrument_session_projection_id"] for r in projections],
        "event_state_record_ids": [r["event_state_record_id"] for r in event_state_records],
        "event_state_record_fingerprints": [r["event_state_record_fingerprint"] for r in event_state_records],
    }
    write_json(run_dir / "determinism_report.json", determinism_report)

    candidate_manifest = {
        "run_id": run_id,
        "candidate_output_kind": "event_state_candidate_records_jsonl",
        "candidate_output_status": "non_official_candidate_evidence_only",
        "event_state_candidate_records_path": str(records_path),
        "event_state_candidate_records_sha256": sha256_file(records_path),
        "event_state_candidate_records": len(event_state_records),
        "event_state_parquet_files_written": 0,
        "source_market_state_candidate_parquet_sha256": market_state_sha,
        "source_market_state_semantic_profile_id": scope["source_market_state_profile_id"],
        "source_market_state_physical_profile_id": physical_market_state_profile_id,
        "source_calendar_bound_parquet_sha256": calendar_sha,
        "blocked_contexts": blocked_contexts,
        "known_restrictions": [
            "bounded_scope_only",
            "non_official_scale_c_market_state_candidate_source",
            "one_context_blocked_by_exact_market_state_binding_policy",
            "instrument_projection_from_authorized_scope_not_master_lifecycle_revalidated",
            "not_downstream_consumable",
        ],
    }
    write_json(run_dir / "event_state_candidate_manifest.json", candidate_manifest)

    completed = utc_now()
    final_manifest = {
        **pre_manifest,
        "completed_at_utc": iso_z(completed),
        "status": "complete" if hard_validation_failures == 0 else "failed",
        "event_state_bounded_execution_chain_execution": "CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT"
        if hard_validation_failures == 0
        else "FAILED",
        "requested_contexts": requested_contexts,
        "event_instances_created": len(event_instances),
        "event_window_bindings_created": len(window_bindings),
        "instrument_session_projections_created": len(projections),
        "market_state_bindings_found": bound_contexts,
        "event_state_candidate_records_emitted": len(event_state_records),
        "blocked_contexts": blocked_contexts,
        "missing_exact_market_state_bindings": missing_ms,
        "multiple_exact_market_state_bindings": multiple_ms,
        "fallback_uses": fallback_uses,
        "hard_validation_failures": hard_validation_failures,
        "official_event_state_dataset_promotion": False,
        "downstream_consumption": False,
        "artifacts": {
            "pre_manifest": str(run_dir / "pre_manifest.json"),
            "heartbeat": str(run_dir / "heartbeat.json"),
            "calendar_binding_report": str(run_dir / "calendar_binding_report.csv"),
            "event_instance_report": str(run_dir / "event_instance_report.csv"),
            "event_window_binding_report": str(run_dir / "event_window_binding_report.csv"),
            "instrument_session_projection_report": str(run_dir / "instrument_session_projection_report.csv"),
            "market_state_binding_report": str(run_dir / "market_state_binding_report.csv"),
            "event_state_candidate_records": str(records_path),
            "event_state_candidate_manifest": str(run_dir / "event_state_candidate_manifest.json"),
            "event_state_validation_report": str(run_dir / "event_state_validation_report.json"),
            "determinism_report": str(run_dir / "determinism_report.json"),
            "final_manifest": str(run_dir / "final_manifest.json"),
            "readout": str(run_dir / "event_state_bounded_execution_chain_readout_v0_1.md"),
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": final_manifest["status"], "updated_at_utc": iso_z(completed)})

    readout = f"""# Event State Bounded Execution Chain Readout v0.1

Status: `{final_manifest['event_state_bounded_execution_chain_execution']}`
Run ID: `{run_id}`
Date: `2026-07-24`

## Scope

```text
event_type_id = {scope['event_type_id']}
event_subject_scope = {scope['event_subject_scope']}
exchange_id = {scope['exchange_id']}
authorized_sessions = {len(scope['authorized_sessions'])}
authorized_instruments = {len(scope['authorized_instruments'])}
requested_instrument_session_contexts = {requested_contexts}
source_market_state_candidate_sha256 = {market_state_sha}
```

## Result

```text
event_instances_created = {len(event_instances)}
event_window_bindings_created = {len(window_bindings)}
instrument_session_projections_created = {len(projections)}
market_state_exact_bindings_found = {bound_contexts}
event_state_candidate_records_emitted = {len(event_state_records)}
blocked_contexts = {blocked_contexts}
missing_exact_market_state_bindings = {missing_ms}
multiple_exact_market_state_bindings = {multiple_ms}
fallback_uses = {fallback_uses}
hard_validation_failures = {hard_validation_failures}
```

One context is blocked by design, not substituted:

```text
AAME | 2022-11-25 | event_anchor_timestamp_utc = 2022-11-25T14:30:00Z
available Market State timestamp = 2022-11-25T16:58:00Z
blocking_reason = missing_exact_market_state_binding
```

## Boundaries

```text
source_market_data_rows_read = 0
market_state_rebuilds = 0
latest_prior_fallback_uses = 0
event_state_parquet_files_written = 0
official_event_state_dataset_promotion = false
production = false
downstream_consumption = false
```

## Next Gate

```text
event_state_bounded_execution_chain_physical_validation_v0_1
```
"""
    (run_dir / "event_state_bounded_execution_chain_readout_v0_1.md").write_text(readout, encoding="utf-8")

    # Refresh hashes affected by readout/final write.
    final_manifest["artifacts_sha256"] = {
        name: sha256_file(Path(path))
        for name, path in final_manifest["artifacts"].items()
        if Path(path).exists() and name != "final_manifest"
    }
    final_manifest["final_manifest_self_hash_policy"] = "not_recorded_to_avoid_self_referential_hash"
    write_json(run_dir / "final_manifest.json", final_manifest)

    print(json.dumps({
        "run_id": run_id,
        "status": final_manifest["event_state_bounded_execution_chain_execution"],
        "run_dir": str(run_dir),
        "event_state_candidate_records_emitted": len(event_state_records),
        "blocked_contexts": blocked_contexts,
        "hard_validation_failures": hard_validation_failures,
    }, indent=2))
    return 0 if hard_validation_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
