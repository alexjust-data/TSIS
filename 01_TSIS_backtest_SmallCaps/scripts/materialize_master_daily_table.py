from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


DATASET_ID = "master_daily_table_v0_1"
SCHEMA_VERSION = "master_daily_table_v0_1"
QUALITY_POLICY_VERSION = "master_daily_table_policy_v0_1"

DEFAULT_EXPECTED_DATA_CALENDAR = Path(
    r"E:\TSIS\data\data_foundation_outputs\expected_data_calendar\expected_data_calendar_v0_1"
)
DEFAULT_EXPECTED_DATA_CALENDAR_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\expected_data_calendar\_expected_data_calendar_manifest_v0_1.json"
)
DEFAULT_CORPORATE_ACTIONS = Path(
    r"E:\TSIS\data\data_foundation_outputs\corporate_actions_table\corporate_actions_table_v0_1.parquet"
)
DEFAULT_CORPORATE_ACTIONS_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\corporate_actions_table\_corporate_actions_table_manifest_v0_1.json"
)
DEFAULT_DATASET_CERTIFICATION_MATRIX = Path(
    r"E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\dataset_certification_matrix_v0_1.parquet"
)
DEFAULT_DATASET_CERTIFICATION_MATRIX_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\_dataset_certification_matrix_manifest_v0_1.json"
)
DEFAULT_RAW_DAILY_ROOT = Path(r"E:\TSIS\data\ohlcv_daily")
DEFAULT_DAILY_ADJUSTED_ROOT = Path(r"E:\TSIS\data\ohlcv_daily_adjusted")
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\master_daily_table")

PRICE_VIEWS = ("daily_raw", "split_normalized", "adjusted")


def _sql_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_tree(root: Path) -> dict[str, Any]:
    h = hashlib.sha256()
    files = sorted(path for path in root.rglob("*.parquet") if path.is_file())
    total_bytes = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        file_hash = _sha256(path)
        total_bytes += size
        h.update(rel.encode("utf-8"))
        h.update(str(size).encode("ascii"))
        h.update(file_hash.encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": h.hexdigest(),
    }


def _file_inventory(root: Path) -> dict[str, Any]:
    h = hashlib.sha256()
    files = sorted(path for path in root.rglob("*.parquet") if path.is_file())
    total_bytes = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total_bytes += size
        h.update(rel.encode("utf-8"))
        h.update(str(size).encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "path_size_inventory_sha256": h.hexdigest(),
    }


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _dataset_glob(dataset_dir: Path) -> str:
    return _sql_path(dataset_dir / "**" / "*.parquet")


def materialize_master_daily_table(
    expected_data_calendar: Path,
    expected_data_calendar_manifest: Path,
    corporate_actions: Path,
    corporate_actions_manifest: Path,
    dataset_certification_matrix: Path,
    dataset_certification_matrix_manifest: Path,
    raw_daily_root: Path,
    daily_adjusted_root: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(expected_data_calendar, "expected data calendar dataset")
    expected_manifest = _load_manifest(expected_data_calendar_manifest)
    _require(corporate_actions, "corporate actions table")
    corporate_manifest = _load_manifest(corporate_actions_manifest)
    _require(dataset_certification_matrix, "dataset certification matrix")
    dcm_manifest = _load_manifest(dataset_certification_matrix_manifest)
    _require(raw_daily_root, "raw daily root")
    _require(daily_adjusted_root, "daily adjusted root")

    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / "master_daily_table_v0_1"
    summary_path = output_root / "_master_daily_table_summary_v0_1.csv"
    manifest_path = output_root / "_master_daily_table_manifest_v0_1.json"

    if dataset_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Output exists. Pass --overwrite to replace: {dataset_dir}")
        if dataset_dir.resolve() == output_root.resolve() or "master_daily_table" not in str(dataset_dir):
            raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
        shutil.rmtree(dataset_dir)

    build_run_id = datetime.now(timezone.utc).strftime("master_daily_table_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()

    con = duckdb.connect()
    con.execute("set preserve_insertion_order=false")
    con.execute("set threads=8")

    expected_glob = _dataset_glob(expected_data_calendar)
    raw_glob = _sql_path(raw_daily_root / "**" / "*.parquet")
    adjusted_glob = _sql_path(daily_adjusted_root / "**" / "*.parquet")

    source_query = f"""
    with expected as (
        select
            instrument_id,
            ticker,
            cast(session_date as date) as session_date,
            cast(year as integer) as year,
            cast(month as integer) as month,
            valid_from,
            valid_to,
            expected_session,
            expected_reason,
            expected_dataset_id,
            expected_source_root,
            expectation_policy_version,
            build_run_id as expected_data_calendar_build_run_id
        from read_parquet('{expected_glob}', hive_partitioning=true)
        where dataset_family = 'daily_raw'
    ),
    raw_daily as (
        select
            upper(ticker) as ticker,
            cast(date as date) as session_date,
            cast(o as double) as raw_open,
            cast(h as double) as raw_high,
            cast(l as double) as raw_low,
            cast(c as double) as raw_close,
            cast(v as double) as raw_volume,
            cast(vw as double) as raw_vwap,
            cast(n as bigint) as raw_transaction_count,
            cast(t as bigint) as raw_source_t_epoch_ms
        from read_parquet('{raw_glob}', hive_partitioning=false)
    ),
    adjusted_daily as (
        select
            upper(ticker) as ticker,
            cast(date as date) as session_date,
            cast(future_split_factor as double) as future_split_factor,
            cast(future_dividend_sum as double) as future_dividend_sum,
            cast(future_dividend_factor as double) as future_dividend_factor,
            cast(future_adjustment_factor as double) as future_adjustment_factor,
            cast(o_split_normalized as double) as split_open,
            cast(h_split_normalized as double) as split_high,
            cast(l_split_normalized as double) as split_low,
            cast(c_split_normalized as double) as split_close,
            cast(o_adjusted as double) as adjusted_open,
            cast(h_adjusted as double) as adjusted_high,
            cast(l_adjusted as double) as adjusted_low,
            cast(c_adjusted as double) as adjusted_close,
            cast(o_adjusted_proxy as double) as adjusted_proxy_open,
            cast(h_adjusted_proxy as double) as adjusted_proxy_high,
            cast(l_adjusted_proxy as double) as adjusted_proxy_low,
            cast(c_adjusted_proxy as double) as adjusted_proxy_close,
            materialized_price_view as adjusted_materialized_price_view,
            source_daily_file,
            source_splits_file,
            source_dividends_file
        from read_parquet('{adjusted_glob}', hive_partitioning=false)
    ),
    corporate_actions_by_day as (
        select
            instrument_id,
            ticker,
            cast(action_date as date) as session_date,
            count(*)::integer as corporate_action_count,
            sum(case when action_type = 'split' then 1 else 0 end)::integer as split_action_count,
            sum(case when action_type = 'dividend' then 1 else 0 end)::integer as dividend_action_count,
            sum(case when action_type = 'ticker_change' then 1 else 0 end)::integer as ticker_change_action_count
        from read_parquet('{_sql_path(corporate_actions)}')
        group by instrument_id, ticker, cast(action_date as date)
    ),
    gates as (
        select
            dataset_family,
            data_quality_verdict,
            foundations_completion_status,
            visual_inspection_status,
            production_use_gate,
            event_consumption_gate,
            quality_policy_version as gate_quality_policy_version,
            build_run_id as dataset_certification_matrix_build_run_id
        from read_parquet('{_sql_path(dataset_certification_matrix)}')
        where dataset_family in ('daily', 'ohlcv_daily_adjusted')
    ),
    joined as (
        select
            e.*,
            rd.raw_open,
            rd.raw_high,
            rd.raw_low,
            rd.raw_close,
            rd.raw_volume,
            rd.raw_vwap,
            rd.raw_transaction_count,
            rd.raw_source_t_epoch_ms,
            ad.future_split_factor,
            ad.future_dividend_sum,
            ad.future_dividend_factor,
            ad.future_adjustment_factor,
            ad.split_open,
            ad.split_high,
            ad.split_low,
            ad.split_close,
            ad.adjusted_open,
            ad.adjusted_high,
            ad.adjusted_low,
            ad.adjusted_close,
            ad.adjusted_proxy_open,
            ad.adjusted_proxy_high,
            ad.adjusted_proxy_low,
            ad.adjusted_proxy_close,
            ad.adjusted_materialized_price_view,
            ad.source_daily_file,
            ad.source_splits_file,
            ad.source_dividends_file,
            coalesce(ca.corporate_action_count, 0) as corporate_action_count,
            coalesce(ca.split_action_count, 0) as split_action_count,
            coalesce(ca.dividend_action_count, 0) as dividend_action_count,
            coalesce(ca.ticker_change_action_count, 0) as ticker_change_action_count
        from expected e
        left join raw_daily rd
          on e.ticker = rd.ticker
         and e.session_date = rd.session_date
        left join adjusted_daily ad
          on e.ticker = ad.ticker
         and e.session_date = ad.session_date
        left join corporate_actions_by_day ca
          on e.instrument_id = ca.instrument_id
         and e.ticker = ca.ticker
         and e.session_date = ca.session_date
    ),
    view_rows as (
        select
            *,
            'daily_raw' as price_view,
            'daily' as quality_gate_family,
            'ohlcv_daily' as source_dataset,
            'E:/TSIS/data/ohlcv_daily' as source_root,
            raw_open as open,
            raw_high as high,
            raw_low as low,
            raw_close as close,
            raw_volume as volume,
            raw_vwap as vwap,
            raw_vwap as source_raw_vwap,
            raw_transaction_count as transaction_count,
            raw_source_t_epoch_ms as source_t_epoch_ms,
            raw_open is not null and raw_high is not null and raw_low is not null and raw_close is not null
                as data_present,
            raw_open is not null as source_daily_present,
            split_open is not null or adjusted_open is not null as source_adjusted_present
        from joined
        union all
        select
            *,
            'split_normalized' as price_view,
            'ohlcv_daily_adjusted' as quality_gate_family,
            'ohlcv_daily_adjusted' as source_dataset,
            'E:/TSIS/data/ohlcv_daily_adjusted' as source_root,
            split_open as open,
            split_high as high,
            split_low as low,
            split_close as close,
            raw_volume as volume,
            null::double as vwap,
            raw_vwap as source_raw_vwap,
            raw_transaction_count as transaction_count,
            raw_source_t_epoch_ms as source_t_epoch_ms,
            split_open is not null and split_high is not null and split_low is not null and split_close is not null
                as data_present,
            raw_open is not null as source_daily_present,
            split_open is not null as source_adjusted_present
        from joined
        union all
        select
            *,
            'adjusted' as price_view,
            'ohlcv_daily_adjusted' as quality_gate_family,
            'ohlcv_daily_adjusted' as source_dataset,
            'E:/TSIS/data/ohlcv_daily_adjusted' as source_root,
            adjusted_open as open,
            adjusted_high as high,
            adjusted_low as low,
            adjusted_close as close,
            raw_volume as volume,
            null::double as vwap,
            raw_vwap as source_raw_vwap,
            raw_transaction_count as transaction_count,
            raw_source_t_epoch_ms as source_t_epoch_ms,
            adjusted_open is not null and adjusted_high is not null and adjusted_low is not null and adjusted_close is not null
                as data_present,
            raw_open is not null as source_daily_present,
            adjusted_open is not null as source_adjusted_present
        from joined
    ),
    classified as (
        select
            v.*,
            g.data_quality_verdict as family_data_quality_verdict,
            g.foundations_completion_status as family_foundations_completion_status,
            g.visual_inspection_status as family_visual_inspection_status,
            g.production_use_gate as family_production_use_gate,
            g.event_consumption_gate as family_event_consumption_gate,
            g.gate_quality_policy_version,
            g.dataset_certification_matrix_build_run_id,
            expected_session and not data_present as missing_expected_data,
            data_present and (
                open is null or high is null or low is null or close is null
                or open <= 0 or high <= 0 or low <= 0 or close <= 0
                or high < low
            ) as selected_price_hard_invalid,
            data_present and volume is not null and volume < 0 as negative_volume,
            case
                when not data_present then 'missing_expected_data'
                when open is null or high is null or low is null or close is null then 'hard_invalid_price'
                when open <= 0 or high <= 0 or low <= 0 or close <= 0 then 'hard_invalid_price'
                when high < low then 'hard_invalid_price'
                when volume is not null and volume < 0 then 'hard_invalid_volume'
                else 'row_candidate'
            end as row_level_price_integrity_state
        from view_rows v
        left join gates g
          on v.quality_gate_family = g.dataset_family
    ),
    present_metrics as (
        select
            ticker,
            session_date,
            price_view,
            lag(close) over (partition by ticker, price_view order by session_date) as prior_close,
            avg(volume) over (
                partition by ticker, price_view
                order by session_date
                rows between 20 preceding and 1 preceding
            ) as volume_20d_avg
        from classified
        where data_present
          and not selected_price_hard_invalid
          and not negative_volume
    ),
    final_rows as (
        select
            sha256(concat_ws('|',
                c.instrument_id,
                c.ticker,
                cast(c.session_date as varchar),
                c.price_view,
                '{build_run_id}'
            )) as master_daily_id,
            c.instrument_id,
            c.ticker,
            c.session_date,
            c.year,
            c.month,
            c.price_view,
            c.quality_gate_family,
            c.source_dataset,
            c.source_root,
            c.expected_session,
            c.expected_reason,
            c.expected_dataset_id,
            c.expected_source_root,
            c.data_present,
            c.missing_expected_data,
            c.source_daily_present,
            c.source_adjusted_present,
            c.open,
            c.high,
            c.low,
            c.close,
            c.volume,
            c.vwap,
            c.source_raw_vwap,
            c.transaction_count,
            c.source_t_epoch_ms,
            m.prior_close,
            case when m.prior_close > 0 and c.open is not null then (c.open / m.prior_close) - 1 end as gap_pct,
            case when m.prior_close > 0 and c.close is not null then (c.close / m.prior_close) - 1 end as daily_return_pct,
            case when c.open > 0 and c.close is not null then (c.close / c.open) - 1 end as intraday_return_pct,
            case when c.low > 0 and c.high is not null then (c.high / c.low) - 1 end as daily_range_pct,
            case when c.close is not null and c.volume is not null then c.close * c.volume end as dollar_volume,
            m.volume_20d_avg,
            case when m.volume_20d_avg > 0 and c.volume is not null then c.volume / m.volume_20d_avg end as rvol_20d,
            c.future_split_factor,
            c.future_dividend_sum,
            c.future_dividend_factor,
            c.future_adjustment_factor,
            c.adjusted_materialized_price_view,
            c.adjusted_proxy_open,
            c.adjusted_proxy_high,
            c.adjusted_proxy_low,
            c.adjusted_proxy_close,
            c.source_daily_file,
            c.source_splits_file,
            c.source_dividends_file,
            c.corporate_action_count,
            c.split_action_count,
            c.dividend_action_count,
            c.ticker_change_action_count,
            c.split_action_count > 0 as has_split_action,
            c.dividend_action_count > 0 as has_dividend_action,
            c.ticker_change_action_count > 0 as has_ticker_change_action,
            c.corporate_action_count > 0 as has_any_corporate_action,
            c.row_level_price_integrity_state,
            c.selected_price_hard_invalid,
            c.negative_volume,
            c.data_present
              and not c.selected_price_hard_invalid
              and not c.negative_volume
              and c.family_production_use_gate = 'declared_scope_allowed'
                as backtest_core_row_candidate,
            c.family_data_quality_verdict,
            c.family_foundations_completion_status,
            c.family_visual_inspection_status,
            c.family_production_use_gate,
            c.family_event_consumption_gate,
            c.gate_quality_policy_version,
            c.expected_data_calendar_build_run_id,
            c.dataset_certification_matrix_build_run_id,
            '{corporate_manifest.get("build_run_id", "")}' as corporate_actions_build_run_id,
            c.expectation_policy_version,
            '{QUALITY_POLICY_VERSION}' as quality_policy_version,
            '{SCHEMA_VERSION}' as schema_version,
            '{build_run_id}' as build_run_id,
            '{created_at_utc}' as created_at_utc
        from classified c
        left join present_metrics m
          on c.ticker = m.ticker
         and c.session_date = m.session_date
         and c.price_view = m.price_view
    )
    select *
    from final_rows
    order by year, price_view, ticker, session_date
    """

    con.execute(
        f"""
        copy ({source_query})
        to '{_sql_path(dataset_dir)}'
        (format parquet, compression zstd, partition_by (year, price_view))
        """
    )

    dataset_glob = _dataset_glob(dataset_dir)
    validations = con.execute(
        f"""
        with rows as (
            select * from read_parquet('{dataset_glob}', hive_partitioning=true)
        ),
        dupes as (
            select count(*)::bigint as duplicate_key_groups
            from (
                select ticker, session_date, price_view, count(*) as n
                from rows
                group by 1, 2, 3
                having count(*) > 1
            )
        )
        select
            count(*)::bigint as row_count,
            count(distinct ticker)::integer as ticker_count,
            count(distinct instrument_id)::integer as instrument_id_count,
            count(distinct price_view)::integer as price_view_count,
            min(session_date)::varchar as first_session,
            max(session_date)::varchar as last_session,
            sum(case when data_present then 1 else 0 end)::bigint as data_present_rows,
            sum(case when missing_expected_data then 1 else 0 end)::bigint as missing_expected_data_rows,
            sum(case when selected_price_hard_invalid then 1 else 0 end)::bigint as selected_price_hard_invalid_rows,
            sum(case when negative_volume then 1 else 0 end)::bigint as negative_volume_rows,
            sum(case when backtest_core_row_candidate then 1 else 0 end)::bigint as backtest_core_row_candidate_rows,
            sum(case when has_any_corporate_action then 1 else 0 end)::bigint as rows_with_corporate_action,
            (select duplicate_key_groups from dupes)::bigint as duplicate_key_groups
        from rows
        """
    ).fetchdf().iloc[0].to_dict()

    by_price_view = con.execute(
        f"""
        select
            price_view,
            count(*)::bigint as rows,
            sum(case when data_present then 1 else 0 end)::bigint as present_rows,
            sum(case when missing_expected_data then 1 else 0 end)::bigint as missing_rows,
            sum(case when selected_price_hard_invalid then 1 else 0 end)::bigint as hard_invalid_rows,
            sum(case when backtest_core_row_candidate then 1 else 0 end)::bigint as backtest_core_candidate_rows
        from read_parquet('{dataset_glob}', hive_partitioning=true)
        group by price_view
        order by price_view
        """
    ).fetchdf()
    validations["rows_by_price_view"] = {
        row["price_view"]: {
            "rows": int(row["rows"]),
            "present_rows": int(row["present_rows"]),
            "missing_rows": int(row["missing_rows"]),
            "hard_invalid_rows": int(row["hard_invalid_rows"]),
            "backtest_core_candidate_rows": int(row["backtest_core_candidate_rows"]),
        }
        for _, row in by_price_view.iterrows()
    }
    validations = {
        key: int(value) if hasattr(value, "item") and str(getattr(value, "dtype", "")).startswith("int") else value
        for key, value in validations.items()
    }
    expected_daily_rows = int(validations["row_count"] // len(PRICE_VIEWS))
    validations["expected_daily_rows"] = expected_daily_rows
    validations["hard_fail_count"] = int(
        validations["duplicate_key_groups"]
        + (1 if validations["row_count"] == 0 else 0)
        + (1 if validations["price_view_count"] != len(PRICE_VIEWS) else 0)
        + (1 if validations["row_count"] != expected_daily_rows * len(PRICE_VIEWS) else 0)
    )
    if validations["hard_fail_count"] > 0:
        raise RuntimeError(f"Hard validation failed: {json.dumps(validations, indent=2)}")

    tree = _sha256_tree(dataset_dir)
    raw_inventory = _file_inventory(raw_daily_root)
    adjusted_inventory = _file_inventory(daily_adjusted_root)

    summary_rows = [
        {"metric": "rows", "value": validations["row_count"]},
        {"metric": "expected_daily_rows", "value": validations["expected_daily_rows"]},
        {"metric": "tickers", "value": validations["ticker_count"]},
        {"metric": "instrument_ids", "value": validations["instrument_id_count"]},
        {"metric": "first_session", "value": validations["first_session"]},
        {"metric": "last_session", "value": validations["last_session"]},
        {"metric": "data_present_rows", "value": validations["data_present_rows"]},
        {"metric": "missing_expected_data_rows", "value": validations["missing_expected_data_rows"]},
        {"metric": "selected_price_hard_invalid_rows", "value": validations["selected_price_hard_invalid_rows"]},
        {"metric": "backtest_core_row_candidate_rows", "value": validations["backtest_core_row_candidate_rows"]},
        {"metric": "rows_with_corporate_action", "value": validations["rows_with_corporate_action"]},
        {"metric": "duplicate_key_groups", "value": validations["duplicate_key_groups"]},
        {"metric": "hard_fail_count", "value": validations["hard_fail_count"]},
        {"metric": "parquet_file_count", "value": tree["parquet_file_count"]},
        {"metric": "tree_sha256", "value": tree["tree_sha256"]},
    ]
    for view, payload in validations["rows_by_price_view"].items():
        for metric, value in payload.items():
            summary_rows.append({"metric": f"{view}_{metric}", "value": value})
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)

    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": str(dataset_dir),
        "summary_path": str(summary_path),
        "output_tree": tree,
        "source_expected_data_calendar": str(expected_data_calendar),
        "source_expected_data_calendar_manifest": str(expected_data_calendar_manifest),
        "source_expected_data_calendar_build_run_id": expected_manifest.get("build_run_id"),
        "source_corporate_actions": str(corporate_actions),
        "source_corporate_actions_sha256": _sha256(corporate_actions),
        "source_corporate_actions_manifest": str(corporate_actions_manifest),
        "source_corporate_actions_build_run_id": corporate_manifest.get("build_run_id"),
        "source_dataset_certification_matrix": str(dataset_certification_matrix),
        "source_dataset_certification_matrix_sha256": _sha256(dataset_certification_matrix),
        "source_dataset_certification_matrix_manifest": str(dataset_certification_matrix_manifest),
        "source_dataset_certification_matrix_build_run_id": dcm_manifest.get("build_run_id"),
        "source_raw_daily_root": str(raw_daily_root),
        "source_raw_daily_inventory": raw_inventory,
        "source_daily_adjusted_root": str(daily_adjusted_root),
        "source_daily_adjusted_inventory": adjusted_inventory,
        "price_views": list(PRICE_VIEWS),
        "validations": validations,
        "contracts": {
            "dataset_contract": "01_foundations/contract_registry/dataset_contracts/master_daily_table_dataset_contract_v0_1.md",
            "schema_contract": "01_foundations/canonical_schemas/outputs/master_daily_table_schema_contract.md",
            "consumption_policy": "01_foundations/data_consumption_policies/master_daily_table_consumption_policy.md",
            "registry_entry": "01_foundations/dataset_registry/outputs/master_daily_table_registry_entry.yaml",
            "validators": "01_foundations/validators/outputs/master_daily_table_validators.md",
        },
        "known_limitations": [
            "family_level_quality_gate_only",
            "row_level_daily_quality_labels_not_joined_in_v0_1",
            "fundamentals_news_short_halts_regime_not_joined_in_v0_1",
            "vwap_not_adjusted_for_split_or_dividend_views",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa master_daily_table_v0_1.")
    ap.add_argument("--expected-data-calendar", default=str(DEFAULT_EXPECTED_DATA_CALENDAR))
    ap.add_argument("--expected-data-calendar-manifest", default=str(DEFAULT_EXPECTED_DATA_CALENDAR_MANIFEST))
    ap.add_argument("--corporate-actions", default=str(DEFAULT_CORPORATE_ACTIONS))
    ap.add_argument("--corporate-actions-manifest", default=str(DEFAULT_CORPORATE_ACTIONS_MANIFEST))
    ap.add_argument("--dataset-certification-matrix", default=str(DEFAULT_DATASET_CERTIFICATION_MATRIX))
    ap.add_argument(
        "--dataset-certification-matrix-manifest",
        default=str(DEFAULT_DATASET_CERTIFICATION_MATRIX_MANIFEST),
    )
    ap.add_argument("--raw-daily-root", default=str(DEFAULT_RAW_DAILY_ROOT))
    ap.add_argument("--daily-adjusted-root", default=str(DEFAULT_DAILY_ADJUSTED_ROOT))
    ap.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    materialize_master_daily_table(
        expected_data_calendar=Path(args.expected_data_calendar),
        expected_data_calendar_manifest=Path(args.expected_data_calendar_manifest),
        corporate_actions=Path(args.corporate_actions),
        corporate_actions_manifest=Path(args.corporate_actions_manifest),
        dataset_certification_matrix=Path(args.dataset_certification_matrix),
        dataset_certification_matrix_manifest=Path(args.dataset_certification_matrix_manifest),
        raw_daily_root=Path(args.raw_daily_root),
        daily_adjusted_root=Path(args.daily_adjusted_root),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
