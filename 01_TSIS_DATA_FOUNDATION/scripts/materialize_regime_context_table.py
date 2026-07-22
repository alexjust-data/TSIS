from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pyarrow.parquet as pq


DATASET_ID = "regime_context_table_v0_1"
SCHEMA_VERSION = "regime_context_table_v0_1"
QUALITY_POLICY_VERSION = "regime_context_table_policy_v0_1"
MATERIALIZATION_SCOPE = "regime_indicators_minute_aggregated_daily_context_v0_1"
SOURCE_DATASET_ID = "regime_indicators_v0_1"

DEFAULT_SOURCE_ROOT = Path(r"E:\TSIS\data\regime_indicators")
DEFAULT_MARKET_CALENDAR = Path(
    r"E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet"
)
DEFAULT_MARKET_CALENDAR_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\market_calendar\_market_calendar_manifest_v0_1.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\regime_context_table")

CONTRACTS = {
    "schema": "01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/regime_context_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/regime_context_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/regime_context_table_registry_entry.yaml",
    "validator": "01_foundations/validators/outputs/regime_context_table_validators.md",
    "source_regime_indicators_contract": "01_foundations/contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md",
    "source_regime_indicators_policy": "01_foundations/data_consumption_policies/regime_indicators_consumption_policy.md",
    "source_regime_indicators_quality_notes": "01_foundations/canonical_schemas/regime_indicators/regime_indicators_quality_notes.md",
    "output_target_contract": "01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md",
    "materializer": "scripts/materialize_regime_context_table.py",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _path_for_json(path: Path | str | None) -> str | None:
    if path is None:
        return None
    return str(path).replace("\\", "/")


def _sql_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _json_default(value: Any) -> str | int | float | bool | None:
    if isinstance(value, Path):
        return _path_for_json(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


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
        size = path.stat().st_size
        file_hash = _sha256(path)
        total_bytes += size
        digest.update(rel.encode("utf-8"))
        digest.update(str(size).encode("ascii"))
        digest.update(file_hash.encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": digest.hexdigest(),
    }


def _safe_remove_dataset_dir(dataset_dir: Path, output_root: Path) -> None:
    resolved_dataset = dataset_dir.resolve()
    resolved_root = output_root.resolve()
    if resolved_dataset == resolved_root:
        raise RuntimeError(f"Refusing to delete output root: {dataset_dir}")
    if "regime_context_table" not in str(resolved_dataset):
        raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _source_pattern(source_root: Path) -> str:
    return _sql_path(source_root / "**" / "minute.parquet")


def _source_inventory(source_root: Path) -> dict[str, Any]:
    minute_files = sorted(path for path in source_root.rglob("minute.parquet") if path.is_file())
    day_files = sorted(path for path in source_root.rglob("day.parquet") if path.is_file())
    rows: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    total_rows = 0
    total_bytes = 0
    for path in minute_files:
        rel = path.relative_to(source_root).as_posix()
        pf = pq.ParquetFile(path)
        row_count = int(pf.metadata.num_rows)
        size = int(path.stat().st_size)
        total_rows += row_count
        total_bytes += size
        schema_names = list(pf.schema_arrow.names)
        family = path.relative_to(source_root).parts[0]
        symbol_dir = path.relative_to(source_root).parts[1]
        rows.append(
            {
                "relative_path": rel,
                "source_proxy_family": "etf" if family == "etfs" else "index",
                "source_symbol_dir": symbol_dir,
                "row_count": row_count,
                "bytes": size,
                "schema_columns": schema_names,
            }
        )
        digest.update(rel.encode("utf-8"))
        digest.update(str(row_count).encode("ascii"))
        digest.update(str(size).encode("ascii"))
        digest.update(",".join(schema_names).encode("utf-8"))
    return {
        "source_root": _path_for_json(source_root),
        "minute_file_count": len(minute_files),
        "day_file_count_blocked": len(day_files),
        "minute_row_count": total_rows,
        "minute_total_bytes": total_bytes,
        "minute_inventory_hash": digest.hexdigest(),
        "inventory_hash_semantics": "sha256(relative_path,row_count,bytes,schema_columns); not full file content hash",
        "minute_files": rows,
    }


def _prepare_lookup_tables(
    con: duckdb.DuckDBPyConnection,
    market_calendar: Path,
) -> None:
    con.execute("pragma threads=8")
    con.execute("pragma preserve_insertion_order=false")
    con.execute(
        f"""
        create or replace temp table market_calendar as
        select
            cast(session_date as date) as session_date,
            open_utc,
            close_utc,
            open_et,
            close_et,
            cast(session_minutes as double) as session_minutes,
            cast(is_early_close as boolean) as is_early_close,
            calendar,
            timezone,
            build_run_id as market_calendar_build_run_id,
            schema_version as market_calendar_schema_version
        from read_parquet('{_sql_path(market_calendar)}')
        """
    )


def _create_aggregates(
    con: duckdb.DuckDBPyConnection,
    source_root: Path,
    market_calendar: Path,
    build_run_id: str,
    created_at_utc: str,
) -> None:
    source_root_sql = _sql_path(source_root)
    pattern = _source_pattern(source_root)
    con.execute(
        f"""
        create or replace temp table minute_daily_base as
        with raw_minute as (
            select
                case
                    when regexp_extract(replace(filename, '\\', '/'), '/(etfs|indices)/', 1) = 'etfs'
                        then 'etf'
                    else 'index'
                end as source_proxy_family,
                regexp_extract(replace(filename, '\\', '/'), '/(etfs|indices)/([^/]+)/minute.parquet', 2) as source_symbol_dir,
                replace(filename, '\\', '/') as source_file,
                replace(
                    replace(filename, '\\', '/'),
                    '{source_root_sql}/',
                    ''
                ) as source_file_relative_path,
                timestamp,
                cast(timestamp as date) as trading_date,
                cast(open as double) as open,
                cast(high as double) as high,
                cast(low as double) as low,
                cast(close as double) as close,
                cast(volume as double) as volume,
                cast(vwap as double) as vwap
            from read_parquet(
                '{pattern}',
                union_by_name=true,
                filename=true
            )
            where timestamp is not null
        ),
        mapped as (
            select
                source_proxy_family,
                source_symbol_dir,
                case
                    when source_proxy_family = 'index'
                        then replace(source_symbol_dir, 'I_', 'I:')
                    else source_symbol_dir
                end as regime_symbol,
                case
                    when source_symbol_dir in ('SPY', 'DIA') then 'broad_market_large_cap'
                    when source_symbol_dir in ('QQQ', 'I_NDX') then 'nasdaq_growth_tech'
                    when source_symbol_dir in ('I_COMP') then 'nasdaq_composite_index'
                    when source_symbol_dir in ('IWM', 'SPSM', 'VB') then 'small_cap_proxy'
                    when source_symbol_dir in ('UVXY', 'VIXY', 'VXX') then 'volatility_etp'
                    when source_symbol_dir in ('TLT') then 'rates_duration'
                    when source_symbol_dir in ('HYG', 'LQD') then 'credit_liquidity'
                    when source_symbol_dir in ('UUP', 'FXE') then 'currency_proxy'
                    when source_symbol_dir in ('GLD', 'SLV') then 'precious_metals'
                    when source_symbol_dir in ('USO', 'UNG') then 'energy_commodity'
                    when source_symbol_dir in ('EEM', 'EFA') then 'international_equity'
                    when source_symbol_dir in ('XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY') then 'sector_etf'
                    else 'regime_proxy'
                end as regime_proxy_role,
                source_file,
                source_file_relative_path,
                timestamp,
                trading_date,
                open,
                high,
                low,
                close,
                volume,
                vwap
            from raw_minute
        )
        select
            source_proxy_family,
            source_symbol_dir,
            regime_symbol,
            regime_proxy_role,
            source_file,
            source_file_relative_path,
            trading_date,
            extract(year from trading_date)::integer as observation_year,
            min(timestamp) as first_bar_timestamp,
            max(timestamp) as last_bar_timestamp,
            count(*)::bigint as bars_observed,
            count(distinct timestamp)::bigint as distinct_timestamp_count,
            (count(*) - count(distinct timestamp))::bigint as duplicate_timestamp_rows,
            arg_min(open, timestamp) as open_price,
            max(high) as high_price,
            min(low) as low_price,
            arg_max(close, timestamp) as close_price,
            sum(volume) as volume,
            case
                when sum(case when volume is not null and volume > 0 and vwap is not null then volume else 0 end) > 0
                    then sum(case when volume is not null and volume > 0 and vwap is not null then vwap * volume else 0 end)
                         / sum(case when volume is not null and volume > 0 and vwap is not null then volume else 0 end)
                else null
            end as vwap,
            sum(case when open is null or high is null or low is null or close is null then 1 else 0 end)::bigint as null_ohlc_bar_count,
            sum(case when open <= 0 or high <= 0 or low <= 0 or close <= 0 then 1 else 0 end)::bigint as non_positive_price_bar_count,
            sum(case when high < greatest(open, close, low) or low > least(open, close, high) then 1 else 0 end)::bigint as source_bad_ohlc_bar_count,
            sum(case when source_proxy_family = 'etf' and volume is not null and volume < 0 then 1 else 0 end)::bigint as negative_volume_bar_count,
            sum(case when source_proxy_family = 'etf' and volume is null then 1 else 0 end)::bigint as missing_volume_bar_count,
            sum(case when source_proxy_family = 'etf' and vwap is null then 1 else 0 end)::bigint as missing_vwap_bar_count
        from mapped
        group by
            source_proxy_family,
            source_symbol_dir,
            regime_symbol,
            regime_proxy_role,
            source_file,
            source_file_relative_path,
            trading_date
        """
    )
    con.execute(
        f"""
        create or replace temp table regime_context_output as
        with lagged as (
            select
                b.*,
                lag(close_price) over (
                    partition by regime_symbol
                    order by trading_date
                ) as previous_close_price
            from minute_daily_base b
        ),
        calendar_joined as (
            select
                l.*,
                m.session_date is not null as market_calendar_covered,
                m.open_utc as session_open_utc,
                m.close_utc as session_close_utc,
                m.open_et as session_open_et,
                m.close_et as session_close_et,
                m.session_minutes,
                m.is_early_close,
                m.calendar as market_calendar,
                m.timezone as market_timezone,
                m.market_calendar_build_run_id,
                m.market_calendar_schema_version
            from lagged l
            left join market_calendar m
              on l.trading_date = m.session_date
        )
        select
            sha256(
                coalesce(regime_symbol, '') || '|' ||
                coalesce(cast(trading_date as varchar), '') || '|' ||
                coalesce(source_proxy_family, '') || '|minute_aggregated_daily'
            ) as regime_context_id,
            regime_symbol,
            source_symbol_dir,
            source_proxy_family,
            regime_proxy_role,
            '{SOURCE_DATASET_ID}' as source_dataset_id,
            'minute' as source_granularity,
            'minute_aggregated_daily' as context_granularity,
            trading_date,
            observation_year,
            session_open_utc,
            session_close_utc as as_of_utc,
            trading_date as as_of_date,
            'session_close_aggregate_from_minute_bars' as as_of_semantics,
            first_bar_timestamp,
            last_bar_timestamp,
            bars_observed,
            distinct_timestamp_count,
            duplicate_timestamp_rows,
            case
                when bars_observed >= 360 then 'regular_session_like_or_better'
                when bars_observed >= 60 then 'partial_session_like'
                else 'sparse'
            end as bar_coverage_state,
            open_price,
            high_price,
            low_price,
            close_price,
            previous_close_price,
            case
                when open_price > 0 then (close_price / open_price) - 1
                else null
            end as intraday_return,
            case
                when previous_close_price > 0 then (close_price / previous_close_price) - 1
                else null
            end as close_to_previous_close_return,
            case
                when open_price > 0 then (high_price / open_price) - 1
                else null
            end as high_to_open_return,
            case
                when open_price > 0 then (low_price / open_price) - 1
                else null
            end as low_to_open_return,
            case
                when open_price > 0 then (high_price - low_price) / open_price
                else null
            end as intraday_range_pct,
            volume,
            vwap,
            null_ohlc_bar_count,
            non_positive_price_bar_count,
            source_bad_ohlc_bar_count,
            negative_volume_bar_count,
            missing_volume_bar_count,
            missing_vwap_bar_count,
            market_calendar_covered,
            session_minutes,
            is_early_close,
            market_calendar,
            market_timezone,
            'vendor_naive_timestamp_review' as timestamp_timezone_state,
            true as daily_source_files_blocked,
            false as built_from_blocked_day_parquet,
            true as built_from_minute_parquet,
            false as intraday_regime_features_source_included,
            case
                when trading_date is null then 'bad_missing_trading_date'
                when not market_calendar_covered then 'review_no_market_calendar_session'
                when bars_observed < 60 then 'review_sparse_minute_coverage'
                when null_ohlc_bar_count > 0
                  or non_positive_price_bar_count > 0
                  or source_bad_ohlc_bar_count > 0
                  or negative_volume_bar_count > 0
                    then 'review_source_bar_integrity'
                else 'good_minute_aggregated_regime_context'
            end as regime_quality_state,
            case
                when market_calendar_covered
                 and bars_observed >= 60
                 and null_ohlc_bar_count = 0
                 and non_positive_price_bar_count = 0
                 and source_bad_ohlc_bar_count = 0
                 and negative_volume_bar_count = 0
                    then true
                else false
            end as valid_for_event_context_candidate,
            case
                when market_calendar_covered
                 and bars_observed >= 60
                 and previous_close_price is not null
                 and null_ohlc_bar_count = 0
                 and non_positive_price_bar_count = 0
                 and source_bad_ohlc_bar_count = 0
                 and negative_volume_bar_count = 0
                    then true
                else false
            end as valid_for_ml_feature_candidate,
            case
                when market_calendar_covered
                 and bars_observed >= 60
                 and null_ohlc_bar_count = 0
                 and non_positive_price_bar_count = 0
                 and source_bad_ohlc_bar_count = 0
                 and negative_volume_bar_count = 0
                    then true
                else false
            end as valid_for_state_component_candidate,
            false as valid_for_backtest_core_direct,
            false as valid_for_rl_training_direct,
            true as requires_asof_filter,
            true as contains_future_information_without_event_filter,
            false as same_session_intraday_causal_claim_allowed,
            false as execution_truth,
            '{_path_for_json(source_root)}' as source_root,
            source_file,
            source_file_relative_path,
            '{_path_for_json(market_calendar)}' as market_calendar_source,
            market_calendar_build_run_id,
            market_calendar_schema_version,
            false as full_universe_claim,
            '{MATERIALIZATION_SCOPE}' as materialization_scope,
            '{QUALITY_POLICY_VERSION}' as quality_policy_version,
            '{SCHEMA_VERSION}' as schema_version,
            '{build_run_id}' as build_run_id,
            '{created_at_utc}' as created_at_utc
        from calendar_joined
        """
    )


def _copy_output(con: duckdb.DuckDBPyConnection, dataset_dir: Path) -> None:
    con.execute(
        f"""
        copy regime_context_output
        to '{_sql_path(dataset_dir)}'
        (
            format parquet,
            compression zstd,
            partition_by (source_proxy_family, observation_year),
            overwrite_or_ignore true
        )
        """
    )


def _validations(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    def scalar(sql: str) -> Any:
        return con.execute(sql).fetchone()[0]

    def dict_counts(sql: str) -> dict[str, int]:
        return {str(key): int(value) for key, value in con.execute(sql).fetchall()}

    row_count = int(scalar("select count(*) from regime_context_output"))
    unique_ids = int(scalar("select count(distinct regime_context_id) from regime_context_output"))
    quality_counts = dict_counts(
        """
        select regime_quality_state, count(*)
        from regime_context_output
        group by 1
        order by 1
        """
    )
    proxy_counts = dict_counts(
        """
        select source_proxy_family, count(*)
        from regime_context_output
        group by 1
        order by 1
        """
    )
    role_counts = dict_counts(
        """
        select regime_proxy_role, count(*)
        from regime_context_output
        group by 1
        order by 1
        """
    )
    source_minute_rows = int(scalar("select sum(bars_observed) from regime_context_output"))
    bad_rows = int(
        scalar(
            """
            select count(*)
            from regime_context_output
            where regime_quality_state like 'bad_%'
            """
        )
    )
    return {
        "row_count": row_count,
        "unique_regime_context_id_count": unique_ids,
        "duplicate_regime_context_id_count": row_count - unique_ids,
        "regime_symbol_count": int(scalar("select count(distinct regime_symbol) from regime_context_output")),
        "source_proxy_family_counts": proxy_counts,
        "regime_proxy_role_counts": role_counts,
        "quality_state_counts": quality_counts,
        "first_trading_date": str(scalar("select min(trading_date) from regime_context_output")),
        "last_trading_date": str(scalar("select max(trading_date) from regime_context_output")),
        "source_minute_rows_aggregated": source_minute_rows,
        "calendar_covered_rows": int(
            scalar("select count(*) from regime_context_output where market_calendar_covered")
        ),
        "no_calendar_rows": int(
            scalar("select count(*) from regime_context_output where not market_calendar_covered")
        ),
        "valid_for_event_context_candidate_rows": int(
            scalar("select count(*) from regime_context_output where valid_for_event_context_candidate")
        ),
        "valid_for_ml_feature_candidate_rows": int(
            scalar("select count(*) from regime_context_output where valid_for_ml_feature_candidate")
        ),
        "valid_for_state_component_candidate_rows": int(
            scalar("select count(*) from regime_context_output where valid_for_state_component_candidate")
        ),
        "valid_for_backtest_core_direct_rows": int(
            scalar("select count(*) from regime_context_output where valid_for_backtest_core_direct")
        ),
        "valid_for_rl_training_direct_rows": int(
            scalar("select count(*) from regime_context_output where valid_for_rl_training_direct")
        ),
        "bad_rows": bad_rows,
        "source_bad_ohlc_bar_count": int(
            scalar("select coalesce(sum(source_bad_ohlc_bar_count), 0) from regime_context_output")
        ),
        "duplicate_timestamp_rows": int(
            scalar("select coalesce(sum(duplicate_timestamp_rows), 0) from regime_context_output")
        ),
        "null_ohlc_bar_count": int(
            scalar("select coalesce(sum(null_ohlc_bar_count), 0) from regime_context_output")
        ),
        "non_positive_price_bar_count": int(
            scalar("select coalesce(sum(non_positive_price_bar_count), 0) from regime_context_output")
        ),
        "negative_volume_bar_count": int(
            scalar("select coalesce(sum(negative_volume_bar_count), 0) from regime_context_output")
        ),
        "daily_source_files_blocked_rows": int(
            scalar("select count(*) from regime_context_output where daily_source_files_blocked")
        ),
        "built_from_blocked_day_parquet_rows": int(
            scalar("select count(*) from regime_context_output where built_from_blocked_day_parquet")
        ),
        "built_from_minute_parquet_rows": int(
            scalar("select count(*) from regime_context_output where built_from_minute_parquet")
        ),
        "intraday_regime_features_source_included_rows": int(
            scalar("select count(*) from regime_context_output where intraday_regime_features_source_included")
        ),
        "hard_fail_count": 0,
    }


def _write_summary(con: duckdb.DuckDBPyConnection, summary_path: Path) -> None:
    con.execute(
        f"""
        copy (
            select
                source_proxy_family,
                regime_proxy_role,
                regime_quality_state,
                count(*) as rows,
                count(distinct regime_symbol) as symbols,
                min(trading_date) as first_trading_date,
                max(trading_date) as last_trading_date,
                sum(bars_observed) as source_minute_rows,
                sum(case when valid_for_event_context_candidate then 1 else 0 end) as event_context_candidate_rows,
                sum(case when valid_for_ml_feature_candidate then 1 else 0 end) as ml_feature_candidate_rows
            from regime_context_output
            group by 1,2,3
            order by 1,2,3
        )
        to '{_sql_path(summary_path)}'
        (header true, delimiter ',')
        """
    )


def materialize(
    source_root: Path = DEFAULT_SOURCE_ROOT,
    market_calendar: Path = DEFAULT_MARKET_CALENDAR,
    market_calendar_manifest: Path = DEFAULT_MARKET_CALENDAR_MANIFEST,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    keep_existing: bool = False,
) -> dict[str, Any]:
    _require(source_root, "regime_indicators source root")
    _require(market_calendar, "market calendar")
    _require(market_calendar_manifest, "market calendar manifest")

    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / DATASET_ID
    summary_path = output_root / "_regime_context_table_summary_v0_1.csv"
    manifest_path = output_root / "_regime_context_table_manifest_v0_1.json"

    if not keep_existing:
        _safe_remove_dataset_dir(dataset_dir, output_root)
    dataset_dir.mkdir(parents=True, exist_ok=True)

    now = _utc_now()
    created_at_utc = now.isoformat()
    build_run_id = f"{DATASET_ID}_{now.strftime('%Y%m%dT%H%M%SZ')}"

    source_inventory = _source_inventory(source_root)
    market_calendar_manifest_data = _load_manifest(market_calendar_manifest)

    con = duckdb.connect()
    _prepare_lookup_tables(con, market_calendar)
    _create_aggregates(con, source_root, market_calendar, build_run_id, created_at_utc)
    validations = _validations(con)
    _copy_output(con, dataset_dir)
    _write_summary(con, summary_path)

    output_tree = _sha256_parquet_tree(dataset_dir)
    validations["parquet_file_count"] = output_tree["parquet_file_count"]
    validations["hard_fail_count"] = int(
        validations["duplicate_regime_context_id_count"]
        + validations["bad_rows"]
        + validations["built_from_blocked_day_parquet_rows"]
        + validations["intraday_regime_features_source_included_rows"]
    )

    manifest = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "materialization_scope": MATERIALIZATION_SCOPE,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "status": "materialized_validated_for_declared_scope",
        "dataset_path": _path_for_json(dataset_dir),
        "manifest_path": _path_for_json(manifest_path),
        "summary_path": _path_for_json(summary_path),
        "output_root": _path_for_json(output_root),
        "source_dataset_id": SOURCE_DATASET_ID,
        "source_root": _path_for_json(source_root),
        "source_inventory": source_inventory,
        "source_semantics": {
            "used_source_granularity": "minute.parquet",
            "blocked_source_granularity": "day.parquet",
            "blocked_reason": "regime_indicators_v0_1 daily files have invalid 1970 date semantics",
            "intraday_regime_features_included": False,
            "intraday_regime_features_reason": "pilot ticker-day feature layer, not global regime context source for v0.1",
            "timestamp_timezone_state": "vendor_naive_timestamp_review",
            "as_of_semantics": "session_close_aggregate_from_minute_bars",
        },
        "market_calendar": {
            "dataset": _path_for_json(market_calendar),
            "manifest": _path_for_json(market_calendar_manifest),
            "manifest_dataset_id": market_calendar_manifest_data.get("dataset_id"),
            "manifest_build_run_id": market_calendar_manifest_data.get("build_run_id"),
            "manifest_output_sha256": market_calendar_manifest_data.get("output_sha256"),
        },
        "contracts": CONTRACTS,
        "full_universe_claim": False,
        "direct_rl_training_allowed": False,
        "execution_truth": False,
        "requires_asof_filter": True,
        "contains_future_information_without_event_filter": True,
        "same_session_intraday_causal_claim_allowed": False,
        "validations": validations,
        "output_tree": output_tree,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, default=_json_default),
        encoding="utf-8",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize regime_context_table_v0_1.")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--market-calendar", type=Path, default=DEFAULT_MARKET_CALENDAR)
    parser.add_argument(
        "--market-calendar-manifest",
        type=Path,
        default=DEFAULT_MARKET_CALENDAR_MANIFEST,
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--keep-existing", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = materialize(
        source_root=args.source_root,
        market_calendar=args.market_calendar,
        market_calendar_manifest=args.market_calendar_manifest,
        output_root=args.output_root,
        keep_existing=args.keep_existing,
    )
    print(json.dumps(manifest["validations"], indent=2, sort_keys=True))
    print(f"Manifest: {manifest['manifest_path']}")
    print(f"Dataset: {manifest['dataset_path']}")


if __name__ == "__main__":
    main()
