from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb


DATASET_ID = "short_context_table_v0_1"
SCHEMA_VERSION = "short_context_table_v0_1"
QUALITY_POLICY_VERSION = "short_context_table_policy_v0_1"
MATERIALIZATION_SCOPE = "short_and_short_review_source_scoped_context_v0_1"

DEFAULT_LOCAL_SHORT_ROOT = Path(r"E:\TSIS\data\short")
DEFAULT_FINRA_ROOT = Path(r"E:\TSIS\data\short_review\finra_short")
DEFAULT_LOCAL_CERTIFICATION = Path(
    r"C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\short_data_certification\lt1b_short_reference_certification_v2\short_data_certification_by_ticker.csv"
)
DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)
DEFAULT_INSTRUMENT_MASTER_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\_instrument_master_manifest_v0_1.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\short_context_table")

CONTRACTS = {
    "schema": "01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/short_context_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/short_context_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/short_context_table_registry_entry.yaml",
    "validator": "01_foundations/validators/outputs/short_context_table_validators.md",
    "source_short_contract": "01_foundations/contract_registry/dataset_contracts/short_dataset_contract_v0_1.md",
    "source_short_review_contract": "01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md",
    "source_short_policy": "01_foundations/data_consumption_policies/short_consumption_policy.md",
    "source_short_review_policy": "01_foundations/data_consumption_policies/short_review_consumption_policy.md",
    "output_target_contract": "01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md",
    "materializer": "scripts/materialize_short_context_table.py",
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
    if "short_context_table" not in str(resolved_dataset):
        raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _prepare_lookup_tables(
    con: duckdb.DuckDBPyConnection,
    instrument_master: Path,
    local_certification: Path,
) -> None:
    con.execute("pragma threads=8")
    con.execute("pragma preserve_insertion_order=false")
    con.execute(
        f"""
        create or replace temp table instrument_master as
        select
            instrument_id,
            upper(trim(ticker)) as ticker,
            cast(valid_from as date) as valid_from,
            cast(valid_to as date) as valid_to,
            is_common_stock,
            is_lt1b_operational,
            lt1b_classification_1b,
            schema_version,
            build_run_id
        from read_parquet('{_sql_path(instrument_master)}')
        """
    )
    con.execute(
        """
        create or replace temp table ticker_presence as
        select distinct ticker from instrument_master
        """
    )
    con.execute(
        f"""
        create or replace temp table local_short_certification as
        select
            upper(trim(ticker)) as ticker,
            certification_status,
            certification_reason,
            cast(certified_date_start as date) as certified_date_start,
            cast(certified_date_end as date) as certified_date_end,
            cast(entity_id_nunique as bigint) as entity_id_nunique,
            cast(panel_min_date as date) as panel_min_date,
            cast(panel_max_date as date) as panel_max_date,
            short_interest_file_present,
            short_interest_rows,
            cast(short_interest_date_min as date) as short_interest_date_min,
            cast(short_interest_date_max as date) as short_interest_date_max,
            short_interest_duplicate_date_rows,
            short_volume_file_present,
            short_volume_rows,
            cast(short_volume_date_min as date) as short_volume_date_min,
            cast(short_volume_date_max as date) as short_volume_date_max,
            short_volume_duplicate_date_rows
        from read_csv_auto('{_sql_path(local_certification)}', header=true, union_by_name=true)
        """
    )


def _copy_output(
    con: duckdb.DuckDBPyConnection,
    dataset_dir: Path,
) -> None:
    con.execute(
        f"""
        copy short_context_source_output
        to '{_sql_path(dataset_dir)}'
        (
            format parquet,
            compression zstd,
            partition_by (source_system, observation_family, observation_year),
            overwrite_or_ignore true
        )
        """
    )


def _create_short_context_source_output(
    con: duckdb.DuckDBPyConnection,
    raw_sql: str,
    source_system: str,
    source_dataset_id: str,
    source_family: str,
    source_scope: str,
    observation_family: str,
    observation_date_type: str,
    local_short_root: Path,
    finra_root: Path,
    build_run_id: str,
    created_at_utc: str,
) -> None:
    source_root = local_short_root if source_system == "local_polygon" else finra_root
    source_root_sql = _sql_path(source_root)
    con.execute(
        f"""
        create or replace temp table raw_source as
        {raw_sql}
        """
    )
    con.execute(
        f"""
        create or replace temp table raw_enriched as
        select
            *,
            count(*) over (
                partition by ticker_clean, observation_date
            ) as source_duplicate_key_count,
            row_number() over (
                partition by ticker_clean, observation_date
                order by source_file_norm, source_file_row_number
            ) as source_duplicate_key_ordinal
        from raw_source
        """
    )
    con.execute(
        f"""
        create or replace temp table temporal_instrument_match as
        select
            r.short_source_row_id,
            i.instrument_id,
            i.is_common_stock,
            i.is_lt1b_operational,
            i.lt1b_classification_1b,
            i.schema_version as instrument_master_schema_version,
            i.build_run_id as instrument_master_build_run_id,
            row_number() over (
                partition by r.short_source_row_id
                order by i.valid_from desc nulls last, i.valid_to desc nulls last
            ) as rn
        from raw_enriched r
        join instrument_master i
          on r.ticker_clean = i.ticker
         and r.observation_date is not null
         and (i.valid_from is null or i.valid_from <= r.observation_date)
         and (i.valid_to is null or i.valid_to >= r.observation_date)
        """
    )
    con.execute(
        f"""
        create or replace temp table short_context_source_output as
        select
            sha256(concat_ws(
                chr(31),
                '{DATASET_ID}',
                '{source_system}',
                '{observation_family}',
                r.ticker_clean,
                coalesce(cast(r.observation_date as varchar), ''),
                coalesce(cast(r.source_duplicate_key_ordinal as varchar), ''),
                coalesce(r.source_file_relative_path, ''),
                coalesce(cast(r.source_file_row_number as varchar), '')
            )) as short_context_id,
            r.ticker_clean as ticker,
            m.instrument_id,
            '{source_dataset_id}' as source_dataset_id,
            '{source_family}' as source_family,
            '{source_system}' as source_system,
            '{source_scope}' as source_scope,
            '{observation_family}' as observation_family,
            '{observation_date_type}' as observation_date_type,
            r.observation_date,
            extract(year from r.observation_date)::integer as observation_year,
            case when '{observation_family}' = 'short_interest' then r.observation_date else null::date end as settlement_date,
            case when '{observation_family}' = 'short_volume' then r.observation_date else null::date end as trade_date,
            r.observation_date as as_of_date,
            case
                when '{observation_family}' = 'short_interest' then 'settlement_date_observation_requires_lag_contract'
                else 'report_date_source_scope_requires_lag_contract'
            end as as_of_semantics,
            r.short_interest,
            r.avg_daily_volume,
            r.days_to_cover,
            r.total_volume,
            r.short_volume,
            r.exempt_volume,
            r.non_exempt_volume,
            r.short_volume_ratio,
            r.nyse_short_volume,
            r.nyse_short_volume_exempt,
            r.nasdaq_carteret_short_volume,
            r.nasdaq_carteret_short_volume_exempt,
            r.nasdaq_chicago_short_volume,
            r.nasdaq_chicago_short_volume_exempt,
            r.adf_short_volume,
            r.adf_short_volume_exempt,
            r.orf_short_volume,
            r.orf_short_volume_exempt,
            c.certification_status as local_certification_status,
            c.certification_reason as local_certification_reason,
            c.certified_date_start as local_certified_date_start,
            c.certified_date_end as local_certified_date_end,
            c.entity_id_nunique as local_entity_id_nunique,
            c.panel_min_date as local_panel_min_date,
            c.panel_max_date as local_panel_max_date,
            case
                when '{source_system}' <> 'local_polygon' then null::boolean
                when c.certified_date_start is null or c.certified_date_end is null then null::boolean
                else r.observation_date between c.certified_date_start and c.certified_date_end
            end as local_observation_inside_certified_window,
            (p.ticker is not null) as instrument_master_ticker_present,
            (m.instrument_id is not null) as instrument_identity_temporal_match,
            case
                when p.ticker is null then 'review_no_instrument_master_ticker'
                when r.observation_date is null then 'bad_missing_observation_date'
                when m.instrument_id is null then 'review_no_temporal_identity'
                else 'good_temporal_match'
            end as instrument_identity_state,
            m.is_common_stock,
            m.is_lt1b_operational,
            m.lt1b_classification_1b,
            (r.source_duplicate_key_count > 1) as source_duplicate_key_flag,
            r.source_duplicate_key_count,
            r.source_duplicate_key_ordinal,
            (r.source_duplicate_key_count > 1 and r.source_duplicate_key_ordinal > 1) as source_duplicate_excess_row,
            ('{source_system}' = 'finra_official_free') as finra_official_free_baseline,
            ('{source_system}' = 'local_polygon') as local_polygon_operational_source,
            ('{observation_family}' = 'short_volume') as short_volume_source_scope_not_consolidated_market_wide,
            ('{observation_family}' = 'short_interest' and '{source_system}' = 'finra_official_free' and r.observation_date < date '2021-06-01') as finra_pre_modern_short_interest_semantics_flag,
            ('{observation_family}' = 'short_volume' and '{source_system}' = 'finra_official_free' and r.observation_date < date '2018-08-01') as finra_pre_official_free_short_volume_window_flag,
            false as full_2005_2026_official_free_history_claim,
            false as borrow_data_present,
            false as ssr_data_present,
            false as execution_truth,
            true as requires_availability_lag_assumption,
            false as same_day_intraday_causal_claim_allowed,
            true as prohibited_without_asof_filter,
            true as contains_future_information_without_event_filter,
            case
                when r.ticker_clean is null or trim(r.ticker_clean) = '' then 'bad_missing_ticker'
                when r.observation_date is null then 'bad_missing_observation_date'
                when '{observation_family}' = 'short_interest' and r.short_interest is null then 'bad_missing_short_interest'
                when '{observation_family}' = 'short_volume' and r.short_volume is null then 'bad_missing_short_volume'
                when '{observation_family}' = 'short_volume' and r.total_volume is null then 'bad_missing_total_volume'
                when r.source_duplicate_key_count > 1 then 'review_source_duplicate_key'
                when '{source_system}' = 'local_polygon' and c.certification_status is null then 'review_local_missing_certification'
                when '{source_system}' = 'local_polygon' and c.certification_status like 'REVIEW_%' then 'review_local_certification_status'
                when '{source_system}' = 'local_polygon'
                     and c.certified_date_start is not null
                     and c.certified_date_end is not null
                     and not (r.observation_date between c.certified_date_start and c.certified_date_end) then 'review_local_outside_certified_window'
                when m.instrument_id is null then 'review_no_temporal_identity'
                when '{source_system}' = 'finra_official_free'
                     and '{observation_family}' = 'short_interest'
                     and r.observation_date < date '2021-06-01' then 'review_finra_pre_2021_short_interest_semantics'
                when '{source_system}' = 'finra_official_free'
                     and '{observation_family}' = 'short_interest' then 'good_finra_official_free_short_interest_context'
                when '{source_system}' = 'finra_official_free'
                     and '{observation_family}' = 'short_volume' then 'good_finra_official_free_short_volume_context'
                when '{source_system}' = 'local_polygon'
                     and '{observation_family}' = 'short_interest' then 'good_local_certified_short_interest_context'
                when '{source_system}' = 'local_polygon'
                     and '{observation_family}' = 'short_volume' then 'good_local_certified_short_volume_context'
                else 'review_unclassified_short_context'
            end as short_quality_state,
            case
                when r.ticker_clean is null or trim(r.ticker_clean) = '' then false
                when r.observation_date is null then false
                when m.instrument_id is null then false
                when r.source_duplicate_key_count > 1 then false
                when '{source_system}' = 'local_polygon' and c.certification_status not in ('CERTIFIED_OK', 'CERTIFIED_OK_WITH_LIMITED_WINDOW') then false
                when '{source_system}' = 'local_polygon' and c.certified_date_start is not null and c.certified_date_end is not null and not (r.observation_date between c.certified_date_start and c.certified_date_end) then false
                else true
            end as valid_for_event_context_candidate,
            case
                when r.ticker_clean is null or trim(r.ticker_clean) = '' then false
                when r.observation_date is null then false
                when m.instrument_id is null then false
                when r.source_duplicate_key_count > 1 then false
                when '{source_system}' = 'local_polygon' and c.certification_status not in ('CERTIFIED_OK', 'CERTIFIED_OK_WITH_LIMITED_WINDOW') then false
                when '{source_system}' = 'local_polygon' and c.certified_date_start is not null and c.certified_date_end is not null and not (r.observation_date between c.certified_date_start and c.certified_date_end) then false
                when '{source_system}' = 'finra_official_free' and '{observation_family}' = 'short_interest' and r.observation_date < date '2021-06-01' then false
                else true
            end as valid_for_ml_feature_candidate,
            case
                when r.ticker_clean is null or trim(r.ticker_clean) = '' then false
                when r.observation_date is null then false
                when m.instrument_id is null then false
                when r.source_duplicate_key_count > 1 then false
                when '{source_system}' = 'local_polygon' and c.certification_status not in ('CERTIFIED_OK', 'CERTIFIED_OK_WITH_LIMITED_WINDOW') then false
                when '{source_system}' = 'local_polygon' and c.certified_date_start is not null and c.certified_date_end is not null and not (r.observation_date between c.certified_date_start and c.certified_date_end) then false
                else true
            end as valid_for_backtest_context_candidate,
            case
                when r.ticker_clean is null or trim(r.ticker_clean) = '' then false
                when r.observation_date is null then false
                when m.instrument_id is null then false
                when r.source_duplicate_key_count > 1 then false
                when '{source_system}' = 'local_polygon' and c.certification_status not in ('CERTIFIED_OK', 'CERTIFIED_OK_WITH_LIMITED_WINDOW') then false
                when '{source_system}' = 'local_polygon' and c.certified_date_start is not null and c.certified_date_end is not null and not (r.observation_date between c.certified_date_start and c.certified_date_end) then false
                else true
            end as valid_for_state_component_candidate,
            false as valid_for_rl_training_direct,
            '{source_root_sql}' as source_root,
            r.source_file_norm as source_file,
            r.source_file_relative_path,
            r.source_file_row_number,
            m.instrument_master_build_run_id,
            m.instrument_master_schema_version,
            false as full_universe_claim,
            '{MATERIALIZATION_SCOPE}' as materialization_scope,
            '{QUALITY_POLICY_VERSION}' as quality_policy_version,
            '{SCHEMA_VERSION}' as schema_version,
            '{build_run_id}' as build_run_id,
            '{created_at_utc}' as created_at_utc
        from raw_enriched r
        left join local_short_certification c
          on r.ticker_clean = c.ticker
        left join temporal_instrument_match m
          on r.short_source_row_id = m.short_source_row_id
         and m.rn = 1
        left join ticker_presence p
          on r.ticker_clean = p.ticker
        """
    )


def _local_interest_sql(local_short_root: Path) -> str:
    root = _sql_path(local_short_root)
    pattern = _sql_path(local_short_root / "short_interest" / "*.parquet")
    return f"""
        select
            sha256(concat_ws(chr(31), 'local_polygon', 'short_interest', replace(filename, '\\', '/'), cast(row_number() over (partition by filename order by cast(settlement_date as date), ticker) - 1 as varchar))) as short_source_row_id,
            row_number() over (partition by filename order by cast(settlement_date as date), ticker) - 1 as source_file_row_number,
            upper(trim(ticker)) as ticker_clean,
            cast(settlement_date as date) as observation_date,
            replace(filename, '\\', '/') as source_file_norm,
            replace(replace(filename, '\\', '/'), '{root}/', '') as source_file_relative_path,
            cast(short_interest as double) as short_interest,
            cast(avg_daily_volume as double) as avg_daily_volume,
            cast(days_to_cover as double) as days_to_cover,
            null::double as total_volume,
            null::double as short_volume,
            null::double as exempt_volume,
            null::double as non_exempt_volume,
            null::double as short_volume_ratio,
            null::double as nyse_short_volume,
            null::double as nyse_short_volume_exempt,
            null::double as nasdaq_carteret_short_volume,
            null::double as nasdaq_carteret_short_volume_exempt,
            null::double as nasdaq_chicago_short_volume,
            null::double as nasdaq_chicago_short_volume_exempt,
            null::double as adf_short_volume,
            null::double as adf_short_volume_exempt,
            null::double as orf_short_volume,
            null::double as orf_short_volume_exempt
        from read_parquet('{pattern}', union_by_name=true, filename=true)
    """


def _local_volume_sql(local_short_root: Path) -> str:
    root = _sql_path(local_short_root)
    pattern = _sql_path(local_short_root / "short_volume" / "*.parquet")
    return f"""
        select
            sha256(concat_ws(chr(31), 'local_polygon', 'short_volume', replace(filename, '\\', '/'), cast(row_number() over (partition by filename order by cast(date as date), ticker) - 1 as varchar))) as short_source_row_id,
            row_number() over (partition by filename order by cast(date as date), ticker) - 1 as source_file_row_number,
            upper(trim(ticker)) as ticker_clean,
            cast(date as date) as observation_date,
            replace(filename, '\\', '/') as source_file_norm,
            replace(replace(filename, '\\', '/'), '{root}/', '') as source_file_relative_path,
            null::double as short_interest,
            null::double as avg_daily_volume,
            null::double as days_to_cover,
            cast(total_volume as double) as total_volume,
            cast(short_volume as double) as short_volume,
            cast(exempt_volume as double) as exempt_volume,
            cast(non_exempt_volume as double) as non_exempt_volume,
            cast(short_volume_ratio as double) as short_volume_ratio,
            cast(nyse_short_volume as double) as nyse_short_volume,
            cast(nyse_short_volume_exempt as double) as nyse_short_volume_exempt,
            cast(nasdaq_carteret_short_volume as double) as nasdaq_carteret_short_volume,
            cast(nasdaq_carteret_short_volume_exempt as double) as nasdaq_carteret_short_volume_exempt,
            cast(nasdaq_chicago_short_volume as double) as nasdaq_chicago_short_volume,
            cast(nasdaq_chicago_short_volume_exempt as double) as nasdaq_chicago_short_volume_exempt,
            cast(adf_short_volume as double) as adf_short_volume,
            cast(adf_short_volume_exempt as double) as adf_short_volume_exempt,
            null::double as orf_short_volume,
            null::double as orf_short_volume_exempt
        from read_parquet('{pattern}', union_by_name=true, filename=true)
    """


def _finra_interest_sql(finra_root: Path) -> str:
    source_file = _sql_path(finra_root / "artifacts" / "short_interest_all_biweekly_finra.parquet")
    rel = "artifacts/short_interest_all_biweekly_finra.parquet"
    return f"""
        select
            sha256(concat_ws(chr(31), 'finra_official_free', 'short_interest', '{rel}', cast(row_number() over (order by ticker, cast(settlement_date as date), short_interest) - 1 as varchar))) as short_source_row_id,
            row_number() over (order by ticker, cast(settlement_date as date), short_interest) - 1 as source_file_row_number,
            upper(trim(ticker)) as ticker_clean,
            cast(settlement_date as date) as observation_date,
            '{source_file}' as source_file_norm,
            '{rel}' as source_file_relative_path,
            cast(short_interest as double) as short_interest,
            cast(avg_daily_volume as double) as avg_daily_volume,
            cast(days_to_cover as double) as days_to_cover,
            null::double as total_volume,
            null::double as short_volume,
            null::double as exempt_volume,
            null::double as non_exempt_volume,
            null::double as short_volume_ratio,
            null::double as nyse_short_volume,
            null::double as nyse_short_volume_exempt,
            null::double as nasdaq_carteret_short_volume,
            null::double as nasdaq_carteret_short_volume_exempt,
            null::double as nasdaq_chicago_short_volume,
            null::double as nasdaq_chicago_short_volume_exempt,
            null::double as adf_short_volume,
            null::double as adf_short_volume_exempt,
            null::double as orf_short_volume,
            null::double as orf_short_volume_exempt
        from read_parquet('{source_file}', union_by_name=true)
    """


def _finra_volume_sql(finra_root: Path) -> str:
    source_file = _sql_path(finra_root / "artifacts" / "short_volume_all_daily_finra.parquet")
    rel = "artifacts/short_volume_all_daily_finra.parquet"
    return f"""
        select
            sha256(concat_ws(chr(31), 'finra_official_free', 'short_volume', '{rel}', cast(row_number() over (order by ticker, cast(date as date), total_volume, short_volume) - 1 as varchar))) as short_source_row_id,
            row_number() over (order by ticker, cast(date as date), total_volume, short_volume) - 1 as source_file_row_number,
            upper(trim(ticker)) as ticker_clean,
            cast(date as date) as observation_date,
            '{source_file}' as source_file_norm,
            '{rel}' as source_file_relative_path,
            null::double as short_interest,
            null::double as avg_daily_volume,
            null::double as days_to_cover,
            cast(total_volume as double) as total_volume,
            cast(short_volume as double) as short_volume,
            cast(exempt_volume as double) as exempt_volume,
            cast(non_exempt_volume as double) as non_exempt_volume,
            cast(short_volume_ratio as double) as short_volume_ratio,
            cast(nyse_short_volume as double) as nyse_short_volume,
            cast(nyse_short_volume_exempt as double) as nyse_short_volume_exempt,
            cast(nasdaq_carteret_short_volume as double) as nasdaq_carteret_short_volume,
            cast(nasdaq_carteret_short_volume_exempt as double) as nasdaq_carteret_short_volume_exempt,
            cast(nasdaq_chicago_short_volume as double) as nasdaq_chicago_short_volume,
            cast(nasdaq_chicago_short_volume_exempt as double) as nasdaq_chicago_short_volume_exempt,
            cast(adf_short_volume as double) as adf_short_volume,
            cast(adf_short_volume_exempt as double) as adf_short_volume_exempt,
            cast(orf_short_volume as double) as orf_short_volume,
            cast(orf_short_volume_exempt as double) as orf_short_volume_exempt
        from read_parquet('{source_file}', union_by_name=true)
    """


def _process_all_sources(
    con: duckdb.DuckDBPyConnection,
    local_short_root: Path,
    finra_root: Path,
    dataset_dir: Path,
    build_run_id: str,
    created_at_utc: str,
) -> None:
    source_specs = [
        {
            "raw_sql": _local_interest_sql(local_short_root),
            "source_system": "local_polygon",
            "source_dataset_id": "short_v0_1",
            "source_family": "short",
            "source_scope": "local_polygon_short_interest_vendor_scope",
            "observation_family": "short_interest",
            "observation_date_type": "settlement_date",
        },
        {
            "raw_sql": _local_volume_sql(local_short_root),
            "source_system": "local_polygon",
            "source_dataset_id": "short_v0_1",
            "source_family": "short",
            "source_scope": "local_polygon_short_volume_vendor_scope",
            "observation_family": "short_volume",
            "observation_date_type": "trade_date",
        },
        {
            "raw_sql": _finra_interest_sql(finra_root),
            "source_system": "finra_official_free",
            "source_dataset_id": "short_review_finra_v0_1",
            "source_family": "short_review",
            "source_scope": "finra_official_free_equity_short_interest",
            "observation_family": "short_interest",
            "observation_date_type": "settlement_date",
        },
        {
            "raw_sql": _finra_volume_sql(finra_root),
            "source_system": "finra_official_free",
            "source_dataset_id": "short_review_finra_v0_1",
            "source_family": "short_review",
            "source_scope": "finra_official_free_daily_short_sale_volume",
            "observation_family": "short_volume",
            "observation_date_type": "trade_date",
        },
    ]
    for spec in source_specs:
        _create_short_context_source_output(
            con=con,
            local_short_root=local_short_root,
            finra_root=finra_root,
            build_run_id=build_run_id,
            created_at_utc=created_at_utc,
            **spec,
        )
        _copy_output(con, dataset_dir)


def _fetch_one(con: duckdb.DuckDBPyConnection, sql: str) -> Any:
    return con.execute(sql).fetchone()[0]


def _fetch_dict(con: duckdb.DuckDBPyConnection, sql: str) -> dict[str, int]:
    return {str(key): int(value) for key, value in con.execute(sql).fetchall()}


def _source_file_counts(root: Path) -> dict[str, int]:
    return {
        "short_interest_files": len(list((root / "short_interest").glob("*.parquet"))),
        "short_volume_files": len(list((root / "short_volume").glob("*.parquet"))),
    }


def _validations(con: duckdb.DuckDBPyConnection, dataset_dir: Path) -> dict[str, Any]:
    glob = _sql_path(dataset_dir / "**" / "*.parquet")
    source_counts: dict[str, dict[str, int]] = {}
    for source_system, observation_family, rows, tickers in con.execute(
        f"""
        select
            source_system,
            observation_family,
            count(*) as rows,
            count(distinct ticker) as tickers
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        group by source_system, observation_family
        order by source_system, observation_family
        """
    ).fetchall():
        source_counts[f"{source_system}:{observation_family}"] = {
            "rows": int(rows),
            "tickers": int(tickers),
        }
    return {
        "row_count": int(_fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)")),
        "unique_short_context_id_count": int(
            _fetch_one(con, f"select count(distinct short_context_id) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)")
        ),
        "duplicate_short_context_id_count": int(
            _fetch_one(con, f"select count(*) - count(distinct short_context_id) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)")
        ),
        "ticker_count": int(
            _fetch_one(con, f"select count(distinct ticker) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)")
        ),
        "instrument_count": int(
            _fetch_one(con, f"select count(distinct instrument_id) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)")
        ),
        "first_observation_date": str(
            _fetch_one(con, f"select min(observation_date) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)")
        ),
        "last_observation_date": str(
            _fetch_one(con, f"select max(observation_date) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)")
        ),
        "source_observation_counts": source_counts,
        "short_quality_state_counts": _fetch_dict(
            con,
            f"""
            select short_quality_state, count(*)
            from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
            group by short_quality_state
            order by short_quality_state
            """,
        ),
        "source_system_counts": _fetch_dict(
            con,
            f"""
            select source_system, count(*)
            from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
            group by source_system
            order by source_system
            """,
        ),
        "observation_family_counts": _fetch_dict(
            con,
            f"""
            select observation_family, count(*)
            from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
            group by observation_family
            order by observation_family
            """,
        ),
        "local_certification_status_counts": _fetch_dict(
            con,
            f"""
            select coalesce(local_certification_status, 'NULL') as status, count(*)
            from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
            group by status
            order by status
            """,
        ),
        "duplicate_key_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where source_duplicate_key_flag")
        ),
        "duplicate_key_excess_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where source_duplicate_excess_row")
        ),
        "finra_short_volume_duplicate_key_excess_rows": int(
            _fetch_one(
                con,
                f"""
                select count(*)
                from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
                where source_system = 'finra_official_free'
                  and observation_family = 'short_volume'
                  and source_duplicate_excess_row
                """,
            )
        ),
        "bad_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where short_quality_state like 'bad_%'")
        ),
        "valid_for_event_context_candidate_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where valid_for_event_context_candidate")
        ),
        "valid_for_ml_feature_candidate_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where valid_for_ml_feature_candidate")
        ),
        "valid_for_state_component_candidate_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where valid_for_state_component_candidate")
        ),
        "valid_for_rl_training_direct_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where valid_for_rl_training_direct")
        ),
        "full_universe_claim_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where full_universe_claim")
        ),
        "borrow_data_present_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where borrow_data_present")
        ),
        "ssr_data_present_rows": int(
            _fetch_one(con, f"select count(*) from read_parquet('{glob}', union_by_name=true, hive_partitioning=true) where ssr_data_present")
        ),
    }


def _write_summary(con: duckdb.DuckDBPyConnection, dataset_dir: Path, summary_path: Path) -> None:
    glob = _sql_path(dataset_dir / "**" / "*.parquet")
    summary = con.execute(
        f"""
        select
            source_system,
            observation_family,
            short_quality_state,
            count(*) as rows,
            count(distinct ticker) as tickers,
            count(distinct instrument_id) as instruments,
            min(observation_date) as first_observation_date,
            max(observation_date) as last_observation_date,
            sum(case when source_duplicate_key_flag then 1 else 0 end) as duplicate_key_rows,
            sum(case when source_duplicate_excess_row then 1 else 0 end) as duplicate_key_excess_rows,
            sum(case when valid_for_event_context_candidate then 1 else 0 end) as valid_for_event_context_candidate_rows,
            sum(case when valid_for_ml_feature_candidate then 1 else 0 end) as valid_for_ml_feature_candidate_rows,
            sum(case when valid_for_state_component_candidate then 1 else 0 end) as valid_for_state_component_candidate_rows
        from read_parquet('{glob}', union_by_name=true, hive_partitioning=true)
        group by source_system, observation_family, short_quality_state
        order by source_system, observation_family, short_quality_state
        """
    ).fetchdf()
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)


def materialize_short_context_table(
    local_short_root: Path,
    finra_root: Path,
    local_certification: Path,
    instrument_master: Path,
    instrument_master_manifest: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(local_short_root, "local short root")
    _require(finra_root, "FINRA short_review root")
    _require(local_certification, "local short certification")
    _require(instrument_master, "instrument master")
    instrument_manifest = _load_manifest(instrument_master_manifest)

    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / DATASET_ID
    manifest_path = output_root / "_short_context_table_manifest_v0_1.json"
    summary_path = output_root / "_short_context_table_summary_v0_1.csv"

    if overwrite:
        _safe_remove_dataset_dir(dataset_dir, output_root)
    if dataset_dir.exists() and any(dataset_dir.rglob("*.parquet")):
        raise FileExistsError(f"Output exists; rerun with --overwrite: {dataset_dir}")
    dataset_dir.mkdir(parents=True, exist_ok=True)

    build_started = _utc_now()
    build_run_id = f"{DATASET_ID}_{build_started.strftime('%Y%m%dT%H%M%SZ')}"
    created_at_utc = build_started.isoformat()

    con = duckdb.connect()
    _prepare_lookup_tables(con, instrument_master, local_certification)
    _process_all_sources(con, local_short_root, finra_root, dataset_dir, build_run_id, created_at_utc)
    _write_summary(con, dataset_dir, summary_path)
    validations = _validations(con, dataset_dir)

    hard_failures = {
        "duplicate_short_context_id_count": validations["duplicate_short_context_id_count"],
        "bad_rows": validations["bad_rows"],
    }
    hard_fail_count = int(sum(int(value) for value in hard_failures.values()))
    validations["hard_failures"] = hard_failures
    validations["hard_fail_count"] = hard_fail_count
    if hard_fail_count > 0:
        raise RuntimeError(
            "Hard validation failed: "
            + json.dumps(hard_failures, indent=2, sort_keys=True, default=_json_default)
        )

    finra_interest_file = finra_root / "artifacts" / "short_interest_all_biweekly_finra.parquet"
    finra_volume_file = finra_root / "artifacts" / "short_volume_all_daily_finra.parquet"
    output_tree = _sha256_parquet_tree(dataset_dir)
    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "materialization_scope": MATERIALIZATION_SCOPE,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "build_finished_at_utc": _utc_now().isoformat(),
        "dataset_path": _path_for_json(dataset_dir),
        "summary_path": _path_for_json(summary_path),
        "local_short_root": _path_for_json(local_short_root),
        "finra_root": _path_for_json(finra_root),
        "local_certification": _path_for_json(local_certification),
        "source_instrument_master": _path_for_json(instrument_master),
        "source_instrument_master_sha256": _sha256(instrument_master),
        "source_instrument_master_manifest": _path_for_json(instrument_master_manifest),
        "source_instrument_master_build_run_id": instrument_manifest.get("build_run_id"),
        "source_instrument_master_schema_version": instrument_manifest.get("schema_version"),
        "local_short_file_counts": _source_file_counts(local_short_root),
        "finra_manifests": {
            "short_interest": _load_optional_json(finra_root / "artifacts" / "short_interest_manifest.json"),
            "short_volume": _load_optional_json(finra_root / "artifacts" / "short_volume_manifest.json"),
        },
        "source_file_hashes": {
            "finra_short_interest_all_biweekly": _sha256(finra_interest_file),
            "finra_short_volume_all_daily": _sha256(finra_volume_file),
        },
        "output_tree": output_tree,
        "validations": validations,
        "full_universe_claim": False,
        "direct_rl_training_allowed": False,
        "borrow_data_present": False,
        "ssr_data_present": False,
        "execution_truth": False,
        "requires_availability_lag_assumption": True,
        "prohibited_without_asof_filter": True,
        "contracts": CONTRACTS,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True, default=_json_default))
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materializa short_context_table_v0_1.")
    parser.add_argument("--local-short-root", default=str(DEFAULT_LOCAL_SHORT_ROOT))
    parser.add_argument("--finra-root", default=str(DEFAULT_FINRA_ROOT))
    parser.add_argument("--local-certification", default=str(DEFAULT_LOCAL_CERTIFICATION))
    parser.add_argument("--instrument-master", default=str(DEFAULT_INSTRUMENT_MASTER))
    parser.add_argument("--instrument-master-manifest", default=str(DEFAULT_INSTRUMENT_MASTER_MANIFEST))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    materialize_short_context_table(
        local_short_root=Path(args.local_short_root),
        finra_root=Path(args.finra_root),
        local_certification=Path(args.local_certification),
        instrument_master=Path(args.instrument_master),
        instrument_master_manifest=Path(args.instrument_master_manifest),
        output_root=Path(args.output_root),
        overwrite=args.overwrite,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
