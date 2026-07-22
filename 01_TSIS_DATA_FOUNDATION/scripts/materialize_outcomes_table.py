from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


DATASET_ID = "outcomes_table_v0_1"
SCHEMA_VERSION = "outcomes_table_v0_1"
QUALITY_POLICY_VERSION = "outcomes_table_policy_v0_1"
MATERIALIZATION_SCOPE = "halt_next_session_daily_outcomes_v0_1"
OUTCOME_HORIZON = "next_session_regular_daily"
SOURCE_EVENT_WINDOWS_DATASET_ID = "event_windows_table_v0_1"
SOURCE_DAILY_DATASET_ID = "master_daily_table_v0_1"

DEFAULT_EVENT_WINDOWS_TABLE = Path(
    r"E:\TSIS\data\data_foundation_outputs\event_windows_table\event_windows_table_v0_1.parquet"
)
DEFAULT_EVENT_WINDOWS_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\event_windows_table\_event_windows_table_manifest_v0_1.json"
)
DEFAULT_MASTER_DAILY_DATASET = Path(
    r"E:\TSIS\data\data_foundation_outputs\master_daily_table\master_daily_table_v0_1"
)
DEFAULT_MASTER_DAILY_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\master_daily_table\_master_daily_table_manifest_v0_1.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\outcomes_table")

CONTRACTS = {
    "schema": "01_foundations/canonical_schemas/outputs/outcomes_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/outcomes_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/outcomes_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/outcomes_table_registry_entry.yaml",
    "validator": "01_foundations/validators/outputs/outcomes_table_validators.md",
    "source_event_windows_contract": "01_foundations/contract_registry/dataset_contracts/event_windows_table_dataset_contract_v0_1.md",
    "source_master_daily_contract": "01_foundations/contract_registry/dataset_contracts/master_daily_table_dataset_contract_v0_1.md",
    "output_target_contract": "01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md",
    "materializer": "scripts/materialize_outcomes_table.py",
}


def _sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_parquet_tree(root: Path) -> dict[str, int | str]:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*.parquet") if path.is_file())
    total_bytes = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        file_hash = _sha256(path)
        size = path.stat().st_size
        total_bytes += size
        digest.update(rel.encode("utf-8"))
        digest.update(str(size).encode("ascii"))
        digest.update(file_hash.encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return str(value).strip()


def _hash_parts(parts: list[Any]) -> str:
    payload = "\x1f".join(_norm(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _dataset_glob(dataset_root: Path) -> str:
    return (dataset_root / "**" / "*.parquet").as_posix()


def _build_joined_frame(event_windows_table: Path, master_daily_dataset: Path) -> pd.DataFrame:
    con = duckdb.connect()
    con.execute("PRAGMA threads=8")
    event_windows_path = event_windows_table.as_posix()
    master_daily_glob = _dataset_glob(master_daily_dataset)

    con.execute(
        f"""
        create temp table windows as
        select
            event_window_id,
            source_event_id,
            event_source_dataset_id,
            event_family,
            event_type,
            event_code,
            event_source,
            ticker,
            instrument_id,
            issuer_name,
            listing_exchange,
            cast(session_date as date) as event_session_date,
            year as event_year,
            month as event_month,
            event_time_utc,
            resume_trade_utc,
            event_session_phase,
            window_role,
            window_start_utc,
            window_end_utc,
            window_duration_minutes,
            event_window_quality_state,
            event_window_consumption_state,
            source_event_quality_state,
            source_halt_event_state,
            source_resume_trade_observed,
            event_response_end_observed,
            cast(next_session_date as date) as outcome_session_date,
            calendar,
            timezone,
            instrument_identity_temporal_match,
            is_common_stock,
            is_lt1b_operational,
            lt1b_classification_1b,
            valid_for_outcome_window_candidate,
            valid_for_backtest_event_window_candidate,
            full_universe_claim as source_full_universe_claim,
            materialization_scope as source_event_window_materialization_scope,
            quality_policy_version as source_event_window_quality_policy_version,
            schema_version as source_event_window_schema_version,
            build_run_id as source_event_window_build_run_id
        from read_parquet('{event_windows_path}')
        where window_role = 'next_session_regular'
          and valid_for_outcome_window_candidate
        """
    )
    con.execute(
        """
        create temp table needed_daily_keys as
        select distinct instrument_id, ticker, event_session_date as session_date from windows
        union
        select distinct instrument_id, ticker, outcome_session_date as session_date from windows
        """
    )
    con.execute(
        f"""
        create temp table daily_filtered as
        select
            d.master_daily_id,
            d.instrument_id,
            d.ticker,
            cast(d.session_date as date) as session_date,
            d.price_view,
            d.quality_gate_family,
            d.source_dataset,
            d.source_root,
            d.expected_session,
            d.expected_reason,
            d.data_present,
            d.missing_expected_data,
            d.source_daily_present,
            d.source_adjusted_present,
            d.open,
            d.high,
            d.low,
            d.close,
            d.volume,
            d.vwap,
            d.source_raw_vwap,
            d.transaction_count,
            d.prior_close,
            d.gap_pct,
            d.daily_return_pct,
            d.intraday_return_pct,
            d.daily_range_pct,
            d.dollar_volume,
            d.rvol_20d,
            d.future_split_factor,
            d.future_dividend_sum,
            d.future_dividend_factor,
            d.future_adjustment_factor,
            d.corporate_action_count,
            d.split_action_count,
            d.dividend_action_count,
            d.ticker_change_action_count,
            d.has_split_action,
            d.has_dividend_action,
            d.has_ticker_change_action,
            d.has_any_corporate_action,
            d.row_level_price_integrity_state,
            d.selected_price_hard_invalid,
            d.negative_volume,
            d.backtest_core_row_candidate,
            d.family_data_quality_verdict,
            d.family_foundations_completion_status,
            d.family_visual_inspection_status,
            d.family_production_use_gate,
            d.family_event_consumption_gate,
            d.gate_quality_policy_version,
            d.expected_data_calendar_build_run_id,
            d.dataset_certification_matrix_build_run_id,
            d.corporate_actions_build_run_id,
            d.expectation_policy_version,
            d.quality_policy_version,
            d.schema_version,
            d.build_run_id,
            d.created_at_utc
        from read_parquet('{master_daily_glob}', hive_partitioning=true) d
        join needed_daily_keys k
          on d.instrument_id = k.instrument_id
         and d.ticker = k.ticker
         and cast(d.session_date as date) = k.session_date
        """
    )

    return con.execute(
        """
        select
            w.*,
            e.price_view,
            e.master_daily_id as event_master_daily_id,
            n.master_daily_id as outcome_master_daily_id,
            e.quality_gate_family as event_quality_gate_family,
            n.quality_gate_family as outcome_quality_gate_family,
            e.source_dataset as event_daily_source_dataset,
            n.source_dataset as outcome_daily_source_dataset,
            e.source_root as event_daily_source_root,
            n.source_root as outcome_daily_source_root,
            coalesce(e.expected_session, false) as event_expected_session,
            coalesce(n.expected_session, false) as outcome_expected_session,
            e.expected_reason as event_expected_reason,
            n.expected_reason as outcome_expected_reason,
            coalesce(e.data_present, false) as event_data_present,
            coalesce(n.data_present, false) as outcome_data_present,
            coalesce(e.missing_expected_data, false) as event_missing_expected_data,
            coalesce(n.missing_expected_data, false) as outcome_missing_expected_data,
            coalesce(e.source_daily_present, false) as event_source_daily_present,
            coalesce(n.source_daily_present, false) as outcome_source_daily_present,
            coalesce(e.source_adjusted_present, false) as event_source_adjusted_present,
            coalesce(n.source_adjusted_present, false) as outcome_source_adjusted_present,
            e.open as event_open,
            e.high as event_high,
            e.low as event_low,
            e.close as event_close,
            e.volume as event_volume,
            e.vwap as event_vwap,
            e.source_raw_vwap as event_source_raw_vwap,
            e.transaction_count as event_transaction_count,
            e.prior_close as event_prior_close,
            e.gap_pct as event_gap_pct,
            e.daily_return_pct as event_daily_return_pct,
            e.intraday_return_pct as event_intraday_return_pct,
            e.daily_range_pct as event_daily_range_pct,
            e.dollar_volume as event_dollar_volume,
            e.rvol_20d as event_rvol_20d,
            n.open as outcome_open,
            n.high as outcome_high,
            n.low as outcome_low,
            n.close as outcome_close,
            n.volume as outcome_volume,
            n.vwap as outcome_vwap,
            n.source_raw_vwap as outcome_source_raw_vwap,
            n.transaction_count as outcome_transaction_count,
            n.prior_close as outcome_prior_close,
            n.gap_pct as outcome_gap_pct,
            n.daily_return_pct as outcome_daily_return_pct,
            n.intraday_return_pct as outcome_intraday_return_pct,
            n.daily_range_pct as outcome_daily_range_pct,
            n.dollar_volume as outcome_dollar_volume,
            n.rvol_20d as outcome_rvol_20d,
            e.future_split_factor as event_future_split_factor,
            n.future_split_factor as outcome_future_split_factor,
            e.future_dividend_sum as event_future_dividend_sum,
            n.future_dividend_sum as outcome_future_dividend_sum,
            e.future_dividend_factor as event_future_dividend_factor,
            n.future_dividend_factor as outcome_future_dividend_factor,
            e.future_adjustment_factor as event_future_adjustment_factor,
            n.future_adjustment_factor as outcome_future_adjustment_factor,
            e.corporate_action_count as event_corporate_action_count,
            n.corporate_action_count as outcome_corporate_action_count,
            e.split_action_count as event_split_action_count,
            n.split_action_count as outcome_split_action_count,
            e.dividend_action_count as event_dividend_action_count,
            n.dividend_action_count as outcome_dividend_action_count,
            e.ticker_change_action_count as event_ticker_change_action_count,
            n.ticker_change_action_count as outcome_ticker_change_action_count,
            coalesce(e.has_split_action, false) as event_has_split_action,
            coalesce(n.has_split_action, false) as outcome_has_split_action,
            coalesce(e.has_dividend_action, false) as event_has_dividend_action,
            coalesce(n.has_dividend_action, false) as outcome_has_dividend_action,
            coalesce(e.has_ticker_change_action, false) as event_has_ticker_change_action,
            coalesce(n.has_ticker_change_action, false) as outcome_has_ticker_change_action,
            coalesce(e.has_any_corporate_action, false) as event_has_any_corporate_action,
            coalesce(n.has_any_corporate_action, false) as outcome_has_any_corporate_action,
            e.row_level_price_integrity_state as event_row_level_price_integrity_state,
            n.row_level_price_integrity_state as outcome_row_level_price_integrity_state,
            coalesce(e.selected_price_hard_invalid, false) as event_selected_price_hard_invalid,
            coalesce(n.selected_price_hard_invalid, false) as outcome_selected_price_hard_invalid,
            coalesce(e.negative_volume, false) as event_negative_volume,
            coalesce(n.negative_volume, false) as outcome_negative_volume,
            coalesce(e.backtest_core_row_candidate, false) as event_daily_backtest_core_row_candidate,
            coalesce(n.backtest_core_row_candidate, false) as outcome_daily_backtest_core_row_candidate,
            e.family_data_quality_verdict as event_family_data_quality_verdict,
            n.family_data_quality_verdict as outcome_family_data_quality_verdict,
            e.family_foundations_completion_status as event_family_foundations_completion_status,
            n.family_foundations_completion_status as outcome_family_foundations_completion_status,
            e.family_visual_inspection_status as event_family_visual_inspection_status,
            n.family_visual_inspection_status as outcome_family_visual_inspection_status,
            e.family_production_use_gate as event_family_production_use_gate,
            n.family_production_use_gate as outcome_family_production_use_gate,
            e.family_event_consumption_gate as event_family_event_consumption_gate,
            n.family_event_consumption_gate as outcome_family_event_consumption_gate,
            e.gate_quality_policy_version as event_gate_quality_policy_version,
            n.gate_quality_policy_version as outcome_gate_quality_policy_version,
            e.expected_data_calendar_build_run_id,
            e.dataset_certification_matrix_build_run_id,
            e.corporate_actions_build_run_id,
            e.expectation_policy_version,
            e.quality_policy_version as event_daily_quality_policy_version,
            n.quality_policy_version as outcome_daily_quality_policy_version,
            e.schema_version as event_daily_schema_version,
            n.schema_version as outcome_daily_schema_version,
            e.build_run_id as event_daily_build_run_id,
            n.build_run_id as outcome_daily_build_run_id
        from windows w
        left join daily_filtered e
          on e.instrument_id = w.instrument_id
         and e.ticker = w.ticker
         and e.session_date = w.event_session_date
        left join daily_filtered n
          on n.instrument_id = w.instrument_id
         and n.ticker = w.ticker
         and n.session_date = w.outcome_session_date
         and n.price_view = e.price_view
        order by w.event_session_date, w.ticker, w.source_event_id, e.price_view
        """
    ).fetchdf()


def _add_outcome_semantics(frame: pd.DataFrame, build_run_id: str, created_at_utc: str) -> pd.DataFrame:
    output = frame.copy()
    output["outcome_horizon"] = OUTCOME_HORIZON
    output.insert(
        0,
        "outcome_id",
        [
            _hash_parts([DATASET_ID, row.event_window_id, row.price_view, OUTCOME_HORIZON])
            for row in output.itertuples(index=False)
        ],
    )

    event_close = pd.to_numeric(output["event_close"], errors="coerce")

    def return_from_event_close(column: str) -> pd.Series:
        value = pd.to_numeric(output[column], errors="coerce")
        return ((value / event_close) - 1.0).where(event_close.gt(0)) * 100.0

    output["event_close_to_outcome_open_return_pct"] = return_from_event_close("outcome_open")
    output["event_close_to_outcome_high_return_pct"] = return_from_event_close("outcome_high")
    output["event_close_to_outcome_low_return_pct"] = return_from_event_close("outcome_low")
    output["event_close_to_outcome_close_return_pct"] = return_from_event_close("outcome_close")
    output["outcome_intraday_open_to_close_return_pct"] = (
        (pd.to_numeric(output["outcome_close"], errors="coerce") / pd.to_numeric(output["outcome_open"], errors="coerce"))
        - 1.0
    ).where(pd.to_numeric(output["outcome_open"], errors="coerce").gt(0)) * 100.0
    output["outcome_intraday_range_pct"] = (
        (pd.to_numeric(output["outcome_high"], errors="coerce") - pd.to_numeric(output["outcome_low"], errors="coerce"))
        / pd.to_numeric(output["outcome_low"], errors="coerce")
    ).where(pd.to_numeric(output["outcome_low"], errors="coerce").gt(0)) * 100.0

    good_candidate = (
        output["event_daily_backtest_core_row_candidate"].eq(True)
        & output["outcome_daily_backtest_core_row_candidate"].eq(True)
        & event_close.gt(0)
    )
    output["outcome_quality_state"] = "good_daily_outcome"
    output.loc[
        output["event_data_present"].eq(False) & output["outcome_data_present"].eq(False),
        "outcome_quality_state",
    ] = "review_event_and_outcome_daily_missing"
    output.loc[
        output["event_data_present"].eq(False) & output["outcome_data_present"].eq(True),
        "outcome_quality_state",
    ] = "review_event_daily_missing"
    output.loc[
        output["event_data_present"].eq(True) & output["outcome_data_present"].eq(False),
        "outcome_quality_state",
    ] = "review_outcome_daily_missing"
    output.loc[
        output["event_data_present"].eq(True) & output["outcome_data_present"].eq(True) & ~good_candidate,
        "outcome_quality_state",
    ] = "review_daily_quality_gate"

    output["valid_for_outcome_research"] = output["outcome_quality_state"].eq("good_daily_outcome")
    output["valid_for_ml_label_candidate"] = output["valid_for_outcome_research"]
    output["valid_for_strategy_label_candidate"] = output["valid_for_outcome_research"]
    output["valid_for_backtest_outcome_candidate"] = output["valid_for_outcome_research"]
    output["valid_for_rl_reward_candidate"] = False
    output["contains_post_event_information"] = True
    output["prohibited_as_pre_event_feature"] = True
    output["requires_feature_label_separation"] = True
    output["full_universe_claim"] = False

    close_ret = output["event_close_to_outcome_close_return_pct"]
    high_ret = output["event_close_to_outcome_high_return_pct"]
    low_ret = output["event_close_to_outcome_low_return_pct"]
    open_ret = output["event_close_to_outcome_open_return_pct"]
    usable = output["valid_for_outcome_research"]
    output["label_next_close_positive"] = usable & close_ret.gt(0)
    output["label_next_close_ge_5pct"] = usable & close_ret.ge(5.0)
    output["label_next_close_ge_10pct"] = usable & close_ret.ge(10.0)
    output["label_next_close_le_minus_5pct"] = usable & close_ret.le(-5.0)
    output["label_next_close_le_minus_10pct"] = usable & close_ret.le(-10.0)
    output["label_next_high_ge_10pct"] = usable & high_ret.ge(10.0)
    output["label_next_high_ge_20pct"] = usable & high_ret.ge(20.0)
    output["label_next_low_le_minus_10pct"] = usable & low_ret.le(-10.0)
    output["label_next_open_ge_5pct"] = usable & open_ret.ge(5.0)
    output["label_next_open_le_minus_5pct"] = usable & open_ret.le(-5.0)

    output["materialization_scope"] = MATERIALIZATION_SCOPE
    output["quality_policy_version"] = QUALITY_POLICY_VERSION
    output["schema_version"] = SCHEMA_VERSION
    output["build_run_id"] = build_run_id
    output["created_at_utc"] = created_at_utc
    return output


def _rows_by_price_view(frame: pd.DataFrame) -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    for price_view, group in frame.groupby("price_view", dropna=False):
        rows[str(price_view)] = {
            "rows": int(len(group)),
            "event_data_present_rows": int(group["event_data_present"].sum()),
            "outcome_data_present_rows": int(group["outcome_data_present"].sum()),
            "good_daily_outcome_rows": int(group["outcome_quality_state"].eq("good_daily_outcome").sum()),
            "valid_for_ml_label_candidate_rows": int(group["valid_for_ml_label_candidate"].sum()),
        }
    return rows


def _summary_rows(validations: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"metric": "rows", "value": validations["row_count"]},
            {"metric": "source_events", "value": validations["source_event_count"]},
            {"metric": "event_windows", "value": validations["event_window_count"]},
            {"metric": "tickers", "value": validations["ticker_count"]},
            {"metric": "instruments", "value": validations["instrument_count"]},
            {"metric": "price_views", "value": validations["price_view_count"]},
            {"metric": "good_daily_outcome_rows", "value": validations["good_daily_outcome_rows"]},
            {"metric": "review_rows", "value": validations["review_rows"]},
            {"metric": "valid_for_ml_label_candidate_rows", "value": validations["valid_for_ml_label_candidate_rows"]},
            {"metric": "valid_for_rl_reward_candidate_rows", "value": validations["valid_for_rl_reward_candidate_rows"]},
            {"metric": "full_universe_claim_rows", "value": validations["full_universe_claim_rows"]},
            {"metric": "duplicate_outcome_id_count", "value": validations["duplicate_outcome_id_count"]},
        ]
    )


def materialize_outcomes_table(
    event_windows_table: Path,
    event_windows_manifest: Path,
    master_daily_dataset: Path,
    master_daily_manifest: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(event_windows_table, "event_windows_table parquet")
    _require(event_windows_manifest, "event_windows_table manifest")
    _require(master_daily_dataset, "master_daily_table parquet dataset")
    _require(master_daily_manifest, "master_daily_table manifest")

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "outcomes_table_v0_1.parquet"
    summary_path = output_root / "_outcomes_table_summary_v0_1.csv"
    manifest_path = output_root / "_outcomes_table_manifest_v0_1.json"

    if output_path.exists():
        if not overwrite:
            raise FileExistsError(f"Output exists. Pass --overwrite to replace: {output_path}")
        output_path.unlink()

    build_run_id = datetime.now(timezone.utc).strftime("outcomes_table_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()

    event_windows_sha256 = _sha256(event_windows_table)
    event_windows_manifest_sha256 = _sha256(event_windows_manifest)
    master_daily_tree = _sha256_parquet_tree(master_daily_dataset)
    master_daily_manifest_sha256 = _sha256(master_daily_manifest)
    event_windows_manifest_payload = _load_manifest(event_windows_manifest)
    master_daily_manifest_payload = _load_manifest(master_daily_manifest)

    frame = _build_joined_frame(
        event_windows_table=event_windows_table,
        master_daily_dataset=master_daily_dataset,
    )
    output = _add_outcome_semantics(frame, build_run_id, created_at_utc)
    output["source_event_windows_table_path"] = event_windows_table.as_posix()
    output["source_event_windows_table_sha256"] = event_windows_sha256
    output["source_master_daily_table_path"] = master_daily_dataset.as_posix()
    output["source_master_daily_table_tree_sha256"] = master_daily_tree["tree_sha256"]

    ordered_columns = [
        "outcome_id",
        "event_window_id",
        "source_event_id",
        "event_source_dataset_id",
        "event_family",
        "event_type",
        "event_code",
        "event_source",
        "ticker",
        "instrument_id",
        "issuer_name",
        "listing_exchange",
        "event_session_date",
        "outcome_session_date",
        "outcome_horizon",
        "price_view",
        "event_time_utc",
        "resume_trade_utc",
        "event_session_phase",
        "window_role",
        "window_start_utc",
        "window_end_utc",
        "window_duration_minutes",
        "event_window_quality_state",
        "event_window_consumption_state",
        "source_event_quality_state",
        "source_halt_event_state",
        "source_resume_trade_observed",
        "event_response_end_observed",
        "calendar",
        "timezone",
        "instrument_identity_temporal_match",
        "is_common_stock",
        "is_lt1b_operational",
        "lt1b_classification_1b",
        "event_master_daily_id",
        "outcome_master_daily_id",
        "event_quality_gate_family",
        "outcome_quality_gate_family",
        "event_daily_source_dataset",
        "outcome_daily_source_dataset",
        "event_daily_source_root",
        "outcome_daily_source_root",
        "event_expected_session",
        "outcome_expected_session",
        "event_expected_reason",
        "outcome_expected_reason",
        "event_data_present",
        "outcome_data_present",
        "event_missing_expected_data",
        "outcome_missing_expected_data",
        "event_source_daily_present",
        "outcome_source_daily_present",
        "event_source_adjusted_present",
        "outcome_source_adjusted_present",
        "event_open",
        "event_high",
        "event_low",
        "event_close",
        "event_volume",
        "event_vwap",
        "event_source_raw_vwap",
        "event_transaction_count",
        "event_prior_close",
        "event_gap_pct",
        "event_daily_return_pct",
        "event_intraday_return_pct",
        "event_daily_range_pct",
        "event_dollar_volume",
        "event_rvol_20d",
        "outcome_open",
        "outcome_high",
        "outcome_low",
        "outcome_close",
        "outcome_volume",
        "outcome_vwap",
        "outcome_source_raw_vwap",
        "outcome_transaction_count",
        "outcome_prior_close",
        "outcome_gap_pct",
        "outcome_daily_return_pct",
        "outcome_intraday_return_pct",
        "outcome_daily_range_pct",
        "outcome_dollar_volume",
        "outcome_rvol_20d",
        "event_future_split_factor",
        "outcome_future_split_factor",
        "event_future_dividend_sum",
        "outcome_future_dividend_sum",
        "event_future_dividend_factor",
        "outcome_future_dividend_factor",
        "event_future_adjustment_factor",
        "outcome_future_adjustment_factor",
        "event_corporate_action_count",
        "outcome_corporate_action_count",
        "event_split_action_count",
        "outcome_split_action_count",
        "event_dividend_action_count",
        "outcome_dividend_action_count",
        "event_ticker_change_action_count",
        "outcome_ticker_change_action_count",
        "event_has_split_action",
        "outcome_has_split_action",
        "event_has_dividend_action",
        "outcome_has_dividend_action",
        "event_has_ticker_change_action",
        "outcome_has_ticker_change_action",
        "event_has_any_corporate_action",
        "outcome_has_any_corporate_action",
        "event_row_level_price_integrity_state",
        "outcome_row_level_price_integrity_state",
        "event_selected_price_hard_invalid",
        "outcome_selected_price_hard_invalid",
        "event_negative_volume",
        "outcome_negative_volume",
        "event_daily_backtest_core_row_candidate",
        "outcome_daily_backtest_core_row_candidate",
        "event_family_data_quality_verdict",
        "outcome_family_data_quality_verdict",
        "event_family_foundations_completion_status",
        "outcome_family_foundations_completion_status",
        "event_family_visual_inspection_status",
        "outcome_family_visual_inspection_status",
        "event_family_production_use_gate",
        "outcome_family_production_use_gate",
        "event_family_event_consumption_gate",
        "outcome_family_event_consumption_gate",
        "event_gate_quality_policy_version",
        "outcome_gate_quality_policy_version",
        "event_close_to_outcome_open_return_pct",
        "event_close_to_outcome_high_return_pct",
        "event_close_to_outcome_low_return_pct",
        "event_close_to_outcome_close_return_pct",
        "outcome_intraday_open_to_close_return_pct",
        "outcome_intraday_range_pct",
        "label_next_close_positive",
        "label_next_close_ge_5pct",
        "label_next_close_ge_10pct",
        "label_next_close_le_minus_5pct",
        "label_next_close_le_minus_10pct",
        "label_next_high_ge_10pct",
        "label_next_high_ge_20pct",
        "label_next_low_le_minus_10pct",
        "label_next_open_ge_5pct",
        "label_next_open_le_minus_5pct",
        "outcome_quality_state",
        "valid_for_outcome_research",
        "valid_for_ml_label_candidate",
        "valid_for_strategy_label_candidate",
        "valid_for_backtest_outcome_candidate",
        "valid_for_rl_reward_candidate",
        "contains_post_event_information",
        "prohibited_as_pre_event_feature",
        "requires_feature_label_separation",
        "full_universe_claim",
        "expected_data_calendar_build_run_id",
        "dataset_certification_matrix_build_run_id",
        "corporate_actions_build_run_id",
        "expectation_policy_version",
        "event_daily_quality_policy_version",
        "outcome_daily_quality_policy_version",
        "event_daily_schema_version",
        "outcome_daily_schema_version",
        "event_daily_build_run_id",
        "outcome_daily_build_run_id",
        "source_event_window_materialization_scope",
        "source_event_window_quality_policy_version",
        "source_event_window_schema_version",
        "source_event_window_build_run_id",
        "source_full_universe_claim",
        "materialization_scope",
        "quality_policy_version",
        "schema_version",
        "build_run_id",
        "created_at_utc",
        "source_event_windows_table_path",
        "source_event_windows_table_sha256",
        "source_master_daily_table_path",
        "source_master_daily_table_tree_sha256",
    ]
    output = output[ordered_columns]
    output.to_parquet(output_path, index=False, compression="zstd")
    output_sha256 = _sha256(output_path)

    quality_counts = {
        str(k): int(v) for k, v in output["outcome_quality_state"].value_counts(dropna=False).items()
    }
    validations: dict[str, Any] = {
        "row_count": int(len(output)),
        "unique_outcome_id_count": int(output["outcome_id"].nunique()),
        "duplicate_outcome_id_count": int(output["outcome_id"].duplicated().sum()),
        "event_window_count": int(output["event_window_id"].nunique()),
        "source_event_count": int(output["source_event_id"].nunique()),
        "ticker_count": int(output["ticker"].nunique()),
        "instrument_count": int(output["instrument_id"].nunique()),
        "price_view_count": int(output["price_view"].nunique()),
        "outcome_horizon_counts": {
            str(k): int(v) for k, v in output["outcome_horizon"].value_counts(dropna=False).items()
        },
        "rows_by_price_view": _rows_by_price_view(output),
        "outcome_quality_state_counts": quality_counts,
        "good_daily_outcome_rows": int(output["outcome_quality_state"].eq("good_daily_outcome").sum()),
        "review_rows": int(output["outcome_quality_state"].ne("good_daily_outcome").sum()),
        "event_data_present_rows": int(output["event_data_present"].sum()),
        "outcome_data_present_rows": int(output["outcome_data_present"].sum()),
        "event_missing_expected_data_rows": int(output["event_missing_expected_data"].sum()),
        "outcome_missing_expected_data_rows": int(output["outcome_missing_expected_data"].sum()),
        "event_daily_join_missing_rows": int(output["event_master_daily_id"].isna().sum()),
        "outcome_daily_join_missing_rows": int(output["outcome_master_daily_id"].isna().sum()),
        "valid_for_outcome_research_rows": int(output["valid_for_outcome_research"].sum()),
        "valid_for_ml_label_candidate_rows": int(output["valid_for_ml_label_candidate"].sum()),
        "valid_for_strategy_label_candidate_rows": int(output["valid_for_strategy_label_candidate"].sum()),
        "valid_for_backtest_outcome_candidate_rows": int(output["valid_for_backtest_outcome_candidate"].sum()),
        "valid_for_rl_reward_candidate_rows": int(output["valid_for_rl_reward_candidate"].sum()),
        "full_universe_claim_rows": int(output["full_universe_claim"].sum()),
        "source_event_windows_candidate_window_rows": int(
            event_windows_manifest_payload["validations"]["window_role_counts"]["next_session_regular"]
        ),
        "source_master_daily_row_count": int(master_daily_manifest_payload["validations"]["row_count"]),
    }
    _summary_rows(validations).to_csv(summary_path, index=False)

    manifest = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "materialization_scope": MATERIALIZATION_SCOPE,
        "outcome_horizon": OUTCOME_HORIZON,
        "source_event_windows_dataset_id": SOURCE_EVENT_WINDOWS_DATASET_ID,
        "source_daily_dataset_id": SOURCE_DAILY_DATASET_ID,
        "full_universe_claim": False,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": output_path.as_posix(),
        "output_sha256": output_sha256,
        "summary_path": summary_path.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "source_event_windows_table": event_windows_table.as_posix(),
        "source_event_windows_table_sha256": event_windows_sha256,
        "source_event_windows_manifest": event_windows_manifest.as_posix(),
        "source_event_windows_manifest_sha256": event_windows_manifest_sha256,
        "source_event_windows_build_run_id": event_windows_manifest_payload.get("build_run_id"),
        "source_master_daily_dataset": master_daily_dataset.as_posix(),
        "source_master_daily_tree": master_daily_tree,
        "source_master_daily_manifest": master_daily_manifest.as_posix(),
        "source_master_daily_manifest_sha256": master_daily_manifest_sha256,
        "source_master_daily_build_run_id": master_daily_manifest_payload.get("build_run_id"),
        "contracts": CONTRACTS,
        "validations": validations,
        "known_limitations": [
            "v0.1 materializes next-session daily outcomes for halt-derived event windows only.",
            "v0.1 is not an intraday execution outcome table and is not an RL reward table.",
            "v0.1 preserves rows with missing expected daily data as review labels, not as valid training labels.",
            "v0.1 uses master_daily_table price views and must not mix adjusted labels with raw execution prices.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-windows-table", type=Path, default=DEFAULT_EVENT_WINDOWS_TABLE)
    parser.add_argument("--event-windows-manifest", type=Path, default=DEFAULT_EVENT_WINDOWS_MANIFEST)
    parser.add_argument("--master-daily-dataset", type=Path, default=DEFAULT_MASTER_DAILY_DATASET)
    parser.add_argument("--master-daily-manifest", type=Path, default=DEFAULT_MASTER_DAILY_MANIFEST)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest = materialize_outcomes_table(
        event_windows_table=args.event_windows_table,
        event_windows_manifest=args.event_windows_manifest,
        master_daily_dataset=args.master_daily_dataset,
        master_daily_manifest=args.master_daily_manifest,
        output_root=args.output_root,
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "manifest": manifest["manifest_path"],
                "output_path": manifest["output_path"],
                "validations": manifest["validations"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
