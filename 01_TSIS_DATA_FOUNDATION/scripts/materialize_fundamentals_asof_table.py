from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb


DATASET_ID = "fundamentals_asof_table_v0_1"
SCHEMA_VERSION = "fundamentals_asof_table_v0_1"
QUALITY_POLICY_VERSION = "fundamentals_asof_table_policy_v0_1"
MATERIALIZATION_SCOPE = "additional_financials_core_lt1b_statement_asof_v0_1"
SOURCE_DATASET_ID = "additional_v0_1"
SOURCE_SUBBLOCK = "financials_core"
SOURCE_STATEMENT_FAMILIES = (
    "income_statements",
    "balance_sheets",
    "cash_flow_statements",
)

METRIC_COLUMNS_BY_FAMILY = {
    "income_statements": (
        "revenue",
        "cost_of_revenue",
        "gross_profit",
        "selling_general_administrative",
        "other_operating_expenses",
        "total_operating_expenses",
        "operating_income",
        "interest_expense",
        "other_income_expense",
        "total_other_income_expense",
        "income_before_income_taxes",
        "income_taxes",
        "consolidated_net_income_loss",
        "net_income_loss_attributable_common_shareholders",
        "basic_earnings_per_share",
        "diluted_earnings_per_share",
        "basic_shares_outstanding",
        "diluted_shares_outstanding",
        "ebitda",
    ),
    "balance_sheets": (
        "cash_and_equivalents",
        "receivables",
        "inventories",
        "other_current_assets",
        "total_current_assets",
        "property_plant_equipment_net",
        "intangible_assets_net",
        "other_assets",
        "total_assets",
        "accounts_payable",
        "accrued_and_other_current_liabilities",
        "total_current_liabilities",
        "other_noncurrent_liabilities",
        "total_liabilities",
        "common_stock",
        "additional_paid_in_capital",
        "accumulated_other_comprehensive_income",
        "retained_earnings_deficit",
        "other_equity",
        "total_equity_attributable_to_parent",
        "total_equity",
        "total_liabilities_and_equity",
        "long_term_debt_and_capital_lease_obligations",
        "goodwill",
        "debt_current",
        "preferred_stock",
    ),
    "cash_flow_statements": (
        "other_operating_activities",
        "change_in_other_operating_assets_and_liabilities_net",
        "other_investing_activities",
        "long_term_debt_issuances_repayments",
        "dividends",
        "other_financing_activities",
        "net_income",
        "depreciation_depletion_and_amortization",
        "cash_from_operating_activities_continuing_operations",
        "net_cash_from_operating_activities",
        "purchase_of_property_plant_and_equipment",
        "sale_of_property_plant_and_equipment",
        "net_cash_from_investing_activities_continuing_operations",
        "net_cash_from_investing_activities",
        "net_cash_from_financing_activities_continuing_operations",
        "net_cash_from_financing_activities",
        "change_in_cash_and_equivalents",
        "effect_of_currency_exchange_rate",
    ),
}

ALL_METRIC_COLUMNS = tuple(
    dict.fromkeys(
        column
        for columns in METRIC_COLUMNS_BY_FAMILY.values()
        for column in columns
    )
)

DEFAULT_SOURCE_ROOT = Path(r"E:\TSIS\data\additional\financials")
DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)
DEFAULT_INSTRUMENT_MASTER_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\_instrument_master_manifest_v0_1.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\fundamentals_asof_table")

CONTRACTS = {
    "schema": "01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/fundamentals_asof_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/fundamentals_asof_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/fundamentals_asof_table_registry_entry.yaml",
    "validator": "01_foundations/validators/outputs/fundamentals_asof_table_validators.md",
    "source_additional_contract": "01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md",
    "source_additional_financials_schema": "01_foundations/canonical_schemas/additional/additional_financials_schema_contract.md",
    "source_additional_policy": "01_foundations/data_consumption_policies/additional_consumption_policy.md",
    "blocked_financial_policy": "01_foundations/data_consumption_policies/financial_consumption_policy.md",
    "output_target_contract": "01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md",
    "materializer": "scripts/materialize_fundamentals_asof_table.py",
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
    if "fundamentals_asof_table" not in str(resolved_dataset):
        raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "instrument master manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _source_select_sql(source_root: Path) -> str:
    parts = []
    for family in SOURCE_STATEMENT_FAMILIES:
        pattern = _sql_path(source_root / family / "ticker=*" / f"{family}_*.parquet")
        parts.append(
            f"""
            select
                '{family}' as statement_family,
                filename as source_file,
                *
            from read_parquet(
                '{pattern}',
                union_by_name=true,
                hive_partitioning=true,
                filename=true
            )
            """
        )
    return "\nunion all by name\n".join(parts)


def _family_pattern(source_root: Path, family: str) -> str:
    return _sql_path(source_root / family / "ticker=*" / f"{family}_*.parquet")


def _metric_select_sql(family: str) -> str:
    family_columns = set(METRIC_COLUMNS_BY_FAMILY[family])
    expressions = []
    for column in ALL_METRIC_COLUMNS:
        if column in family_columns:
            expressions.append(f"try_cast({column} as double) as {column}")
        else:
            expressions.append(f"cast(null as double) as {column}")
    return ",\n            ".join(expressions)


def _prepare_instrument_tables(
    con: duckdb.DuckDBPyConnection,
    instrument_master: Path,
) -> None:
    instrument_master_sql = _sql_path(instrument_master)

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
        from read_parquet('{instrument_master_sql}')
        """
    )
    con.execute(
        """
        create or replace temp table ticker_presence as
        select distinct ticker from instrument_master
        """
    )


def _create_source_inventory_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        create or replace temp table source_file_inventory (
            statement_family varchar,
            source_file varchar,
            metadata_rows bigint,
            business_rows bigint,
            empty_sentinel boolean
        )
        """
    )


def _process_statement_family(
    con: duckdb.DuckDBPyConnection,
    source_root: Path,
    dataset_dir: Path,
    family: str,
    build_run_id: str,
    created_at_utc: str,
) -> None:
    source_root_sql = _sql_path(source_root)
    pattern = _family_pattern(source_root, family)
    metric_select = _metric_select_sql(family)
    con.execute(
        f"""
        insert into source_file_inventory
        select
            '{family}' as statement_family,
            filename as source_file,
            count(*) as metadata_rows,
            sum(case when coalesce(_empty, false) then 0 else 1 end) as business_rows,
            bool_and(coalesce(_empty, false)) as empty_sentinel
        from read_parquet(
            '{pattern}',
            union_by_name=true,
            hive_partitioning=true,
            filename=true
        )
        group by filename
        """
    )
    con.execute(
        f"""
        create or replace temp table raw_business as
        select
            row_number() over (
                partition by filename
                order by
                    cast(period_end as date) nulls last,
                    cast(filing_date as date) nulls last,
                    fiscal_year nulls last,
                    fiscal_quarter nulls last,
                    timeframe nulls last
            ) - 1 as source_file_row_number,
            upper(trim(coalesce(ticker, regexp_extract(replace(filename, '\\\\', '/'), 'ticker=([^/]+)', 1)))) as ticker_clean,
            replace(filename, '\\\\', '/') as source_file_norm,
            replace(
                replace(filename, '\\\\', '/'),
                '{source_root_sql}/',
                ''
            ) as source_file_relative_path,
            regexp_extract(replace(filename, '\\\\', '/'), 'ticker=([^/]+)', 1) as source_path_ticker,
            cast(period_end as date) as period_end_date,
            cast(filing_date as date) as filing_date_date,
            extract(year from cast(filing_date as date))::integer as as_of_year,
            '{family}' as statement_family,
            ticker,
            tickers,
            cik,
            fiscal_year,
            fiscal_quarter,
            timeframe,
            _dataset,
            _ingested_utc,
            {metric_select}
        from read_parquet(
            '{pattern}',
            union_by_name=true,
            hive_partitioning=true,
            filename=true
        )
        where coalesce(_empty, false) = false
        """
    )
    con.execute(
        """
        create or replace temp table temporal_instrument_match as
        select
            b.source_file_relative_path,
            b.source_file_row_number,
            i.instrument_id,
            i.is_common_stock,
            i.is_lt1b_operational,
            i.lt1b_classification_1b,
            i.schema_version as instrument_master_schema_version,
            i.build_run_id as instrument_master_build_run_id,
            row_number() over (
                partition by b.source_file_relative_path, b.source_file_row_number
                order by i.valid_from desc nulls last, i.valid_to desc nulls last
            ) as rn
        from raw_business b
        join instrument_master i
          on b.ticker_clean = i.ticker
         and b.filing_date_date is not null
         and (i.valid_from is null or i.valid_from <= b.filing_date_date)
         and (i.valid_to is null or i.valid_to >= b.filing_date_date)
        """
    )
    con.execute(
        f"""
        create or replace temp table fundamentals_family_output as
        select
            sha256(concat_ws(
                chr(31),
                '{DATASET_ID}',
                b.source_file_relative_path,
                cast(b.source_file_row_number as varchar),
                b.statement_family,
                b.ticker_clean,
                coalesce(cast(b.period_end_date as varchar), ''),
                coalesce(cast(b.filing_date_date as varchar), ''),
                coalesce(cast(b.fiscal_year as varchar), ''),
                coalesce(cast(b.fiscal_quarter as varchar), ''),
                coalesce(cast(b.timeframe as varchar), '')
            )) as fundamental_asof_id,
            b.ticker_clean as ticker,
            m.instrument_id,
            b.statement_family,
            '{SOURCE_DATASET_ID}' as source_dataset_id,
            '{SOURCE_SUBBLOCK}' as source_subblock,
            b.period_end_date as period_end,
            b.filing_date_date as filing_date,
            b.filing_date_date as as_of_date,
            b.as_of_year,
            b.fiscal_year,
            b.fiscal_quarter,
            b.timeframe,
            cast(b.cik as varchar) as cik,
            cast(b.tickers as varchar) as source_tickers,
            (p.ticker is not null) as instrument_master_ticker_present,
            (m.instrument_id is not null) as instrument_identity_temporal_match,
            case
                when p.ticker is null then 'review_no_instrument_master_ticker'
                when b.filing_date_date is null then 'review_missing_as_of_date'
                when m.instrument_id is null then 'review_no_temporal_identity'
                else 'good_temporal_match'
            end as instrument_identity_state,
            m.is_common_stock,
            m.is_lt1b_operational,
            m.lt1b_classification_1b,
            case
                when b.filing_date_date is null then 'bad_missing_filing_date'
                when b.period_end_date is null then 'bad_missing_period_end'
                when b.period_end_date > b.filing_date_date then 'review_period_after_filing_date'
                when m.instrument_id is null then 'review_no_temporal_identity'
                else 'good_statement_asof'
            end as fundamental_quality_state,
            case
                when b.filing_date_date is null then false
                when b.period_end_date is null then false
                when b.period_end_date > b.filing_date_date then false
                when m.instrument_id is null then false
                else true
            end as valid_for_event_context_candidate,
            case
                when b.filing_date_date is null then false
                when b.period_end_date is null then false
                when b.period_end_date > b.filing_date_date then false
                when m.instrument_id is null then false
                else true
            end as valid_for_ml_feature_candidate,
            case
                when b.filing_date_date is null then false
                when b.period_end_date is null then false
                when b.period_end_date > b.filing_date_date then false
                when m.instrument_id is null then false
                else true
            end as valid_for_backtest_context_candidate,
            case
                when b.filing_date_date is null then false
                when b.period_end_date is null then false
                when b.period_end_date > b.filing_date_date then false
                when m.instrument_id is null then false
                else true
            end as valid_for_state_component_candidate,
            false as valid_for_rl_training_direct,
            'filing_date_available_from_date_only' as as_of_semantics,
            false as period_end_is_availability_date,
            true as requires_event_time_filter,
            true as prohibited_without_asof_filter,
            true as contains_future_information_without_event_filter,
            true as ratios_excluded_from_core_v0_1,
            true as standalone_financial_root_excluded_from_core_v0_1,
            '{source_root_sql}' as source_root,
            b.source_file_norm as source_file,
            b.source_file_relative_path,
            b.source_file_row_number,
            b.source_path_ticker,
            false as source_empty_sentinel,
            b._dataset,
            b._ingested_utc,
            m.instrument_master_build_run_id,
            m.instrument_master_schema_version,
            false as full_universe_claim,
            '{MATERIALIZATION_SCOPE}' as materialization_scope,
            '{QUALITY_POLICY_VERSION}' as quality_policy_version,
            '{SCHEMA_VERSION}' as schema_version,
            '{build_run_id}' as build_run_id,
            '{created_at_utc}' as created_at_utc,
            {", ".join("b." + column for column in ALL_METRIC_COLUMNS)}
        from raw_business b
        left join temporal_instrument_match m
          on b.source_file_relative_path = m.source_file_relative_path
         and b.source_file_row_number = m.source_file_row_number
         and m.rn = 1
        left join ticker_presence p
          on b.ticker_clean = p.ticker
        """
    )
    dataset_dir_sql = _sql_path(dataset_dir)
    con.execute(
        f"""
        copy fundamentals_family_output
        to '{dataset_dir_sql}'
        (
            format parquet,
            compression zstd,
            partition_by (statement_family, as_of_year),
            overwrite_or_ignore true
        )
        """
    )


def _fetch_one(con: duckdb.DuckDBPyConnection, sql: str) -> Any:
    return con.execute(sql).fetchone()[0]


def _fetch_dict(con: duckdb.DuckDBPyConnection, sql: str) -> dict[str, int]:
    return {str(key): int(value) for key, value in con.execute(sql).fetchall()}


def _source_inventory(con: duckdb.DuckDBPyConnection, source_root: Path) -> dict[str, Any]:
    family_rows = con.execute(
        """
        select
            statement_family,
            count(*) as files,
            sum(case when business_rows > 0 then 1 else 0 end) as business_files,
            sum(case when empty_sentinel then 1 else 0 end) as empty_sentinel_files,
            sum(metadata_rows) as metadata_rows,
            sum(business_rows) as business_rows
        from source_file_inventory
        group by statement_family
        order by statement_family
        """
    ).fetchall()
    file_rows = con.execute(
        """
        select
            statement_family,
            replace(source_file, '\\', '/') as source_file,
            metadata_rows,
            business_rows,
            empty_sentinel
        from source_file_inventory
        order by statement_family, source_file
        """
    ).fetchall()
    digest = hashlib.sha256()
    for statement_family, source_file, metadata_rows, business_rows, empty_sentinel in file_rows:
        rel = str(source_file).replace(_path_for_json(source_root) + "/", "")
        digest.update(str(statement_family).encode("utf-8"))
        digest.update(rel.encode("utf-8"))
        digest.update(str(metadata_rows).encode("ascii"))
        digest.update(str(business_rows).encode("ascii"))
        digest.update(str(bool(empty_sentinel)).encode("ascii"))
    return {
        "source_root": _path_for_json(source_root),
        "families": {
            str(family): {
                "files": int(files),
                "business_files": int(business_files),
                "empty_sentinel_files": int(empty_sentinel_files),
                "metadata_rows": int(metadata_rows),
                "business_rows": int(business_rows),
            }
            for family, files, business_files, empty_sentinel_files, metadata_rows, business_rows in family_rows
        },
        "file_count": int(sum(row[1] for row in family_rows)),
        "business_file_count": int(sum(row[2] for row in family_rows)),
        "empty_sentinel_file_count": int(sum(row[3] for row in family_rows)),
        "metadata_row_count": int(sum(row[4] for row in family_rows)),
        "business_row_count": int(sum(row[5] for row in family_rows)),
        "source_inventory_hash": digest.hexdigest(),
        "inventory_hash_semantics": "sha256(statement_family,relative_path,metadata_rows,business_rows,empty_sentinel); not full file content hash",
    }


def _validations(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    statement_family_counts: dict[str, dict[str, int]] = {}
    for row in con.execute(
        """
        select
            statement_family,
            count(*) as rows,
            count(distinct ticker) as tickers,
            count(distinct instrument_id) as instruments,
            sum(case when fundamental_quality_state = 'good_statement_asof' then 1 else 0 end) as good_statement_asof_rows,
            sum(case when valid_for_event_context_candidate then 1 else 0 end) as valid_for_event_context_candidate_rows,
            sum(case when source_empty_sentinel then 1 else 0 end) as empty_sentinel_rows
        from fundamentals_output
        group by statement_family
        order by statement_family
        """
    ).fetchall():
        family, rows, tickers, instruments, good_rows, event_rows, sentinel_rows = row
        statement_family_counts[str(family)] = {
            "rows": int(rows),
            "tickers": int(tickers),
            "instruments": int(instruments),
            "good_statement_asof_rows": int(good_rows),
            "valid_for_event_context_candidate_rows": int(event_rows),
            "empty_sentinel_rows": int(sentinel_rows),
        }

    return {
        "row_count": int(_fetch_one(con, "select count(*) from fundamentals_output")),
        "unique_fundamental_asof_id_count": int(
            _fetch_one(con, "select count(distinct fundamental_asof_id) from fundamentals_output")
        ),
        "duplicate_fundamental_asof_id_count": int(
            _fetch_one(
                con,
                "select count(*) - count(distinct fundamental_asof_id) from fundamentals_output",
            )
        ),
        "duplicate_source_key_count": int(
            _fetch_one(
                con,
                """
                select count(*) from (
                    select
                        source_file_relative_path,
                        source_file_row_number,
                        statement_family,
                        ticker,
                        period_end,
                        as_of_date,
                        fiscal_year,
                        fiscal_quarter,
                        timeframe,
                        count(*) as n
                    from fundamentals_output
                    group by all
                    having count(*) > 1
                )
                """,
            )
        ),
        "ticker_count": int(_fetch_one(con, "select count(distinct ticker) from fundamentals_output")),
        "instrument_count": int(_fetch_one(con, "select count(distinct instrument_id) from fundamentals_output")),
        "statement_family_count": int(
            _fetch_one(con, "select count(distinct statement_family) from fundamentals_output")
        ),
        "statement_family_counts": statement_family_counts,
        "fundamental_quality_state_counts": _fetch_dict(
            con,
            """
            select fundamental_quality_state, count(*)
            from fundamentals_output
            group by fundamental_quality_state
            order by fundamental_quality_state
            """,
        ),
        "good_statement_asof_rows": int(
            _fetch_one(
                con,
                "select count(*) from fundamentals_output where fundamental_quality_state = 'good_statement_asof'",
            )
        ),
        "review_rows": int(
            _fetch_one(
                con,
                "select count(*) from fundamentals_output where starts_with(fundamental_quality_state, 'review_')",
            )
        ),
        "bad_rows": int(
            _fetch_one(
                con,
                "select count(*) from fundamentals_output where starts_with(fundamental_quality_state, 'bad_')",
            )
        ),
        "missing_filing_date_rows": int(_fetch_one(con, "select count(*) from fundamentals_output where as_of_date is null")),
        "missing_period_end_rows": int(_fetch_one(con, "select count(*) from fundamentals_output where period_end is null")),
        "period_after_filing_date_rows": int(
            _fetch_one(con, "select count(*) from fundamentals_output where period_end > as_of_date")
        ),
        "instrument_temporal_match_rows": int(
            _fetch_one(con, "select count(*) from fundamentals_output where instrument_identity_temporal_match")
        ),
        "valid_for_event_context_candidate_rows": int(
            _fetch_one(con, "select count(*) from fundamentals_output where valid_for_event_context_candidate")
        ),
        "valid_for_ml_feature_candidate_rows": int(
            _fetch_one(con, "select count(*) from fundamentals_output where valid_for_ml_feature_candidate")
        ),
        "valid_for_backtest_context_candidate_rows": int(
            _fetch_one(con, "select count(*) from fundamentals_output where valid_for_backtest_context_candidate")
        ),
        "valid_for_state_component_candidate_rows": int(
            _fetch_one(con, "select count(*) from fundamentals_output where valid_for_state_component_candidate")
        ),
        "valid_for_rl_training_direct_rows": int(
            _fetch_one(con, "select count(*) from fundamentals_output where valid_for_rl_training_direct")
        ),
        "as_of_date_min": _fetch_one(con, "select cast(min(as_of_date) as varchar) from fundamentals_output"),
        "as_of_date_max": _fetch_one(con, "select cast(max(as_of_date) as varchar) from fundamentals_output"),
        "period_end_min": _fetch_one(con, "select cast(min(period_end) as varchar) from fundamentals_output"),
        "period_end_max": _fetch_one(con, "select cast(max(period_end) as varchar) from fundamentals_output"),
        "full_universe_claim_rows": int(_fetch_one(con, "select count(*) from fundamentals_output where full_universe_claim")),
    }


def materialize(
    source_root: Path,
    instrument_master: Path,
    instrument_master_manifest: Path,
    output_root: Path,
) -> dict[str, Any]:
    _require(source_root, "additional financials root")
    _require(instrument_master, "instrument master")
    _require(instrument_master_manifest, "instrument master manifest")

    created_at = _utc_now()
    created_at_utc = created_at.isoformat()
    build_run_id = f"{DATASET_ID}_{created_at.strftime('%Y%m%dT%H%M%SZ')}"
    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / DATASET_ID
    summary_path = output_root / "_fundamentals_asof_table_summary_v0_1.csv"
    manifest_path = output_root / "_fundamentals_asof_table_manifest_v0_1.json"
    _safe_remove_dataset_dir(dataset_dir, output_root)

    con = duckdb.connect()
    _prepare_instrument_tables(con=con, instrument_master=instrument_master)
    _create_source_inventory_table(con)
    for family in SOURCE_STATEMENT_FAMILIES:
        _process_statement_family(
            con=con,
            source_root=source_root,
            dataset_dir=dataset_dir,
            family=family,
            build_run_id=build_run_id,
            created_at_utc=created_at_utc,
        )
    dataset_glob = _sql_path(dataset_dir / "**" / "*.parquet")
    con.execute(
        f"""
        create or replace temp table fundamentals_output as
        select *
        from read_parquet('{dataset_glob}', union_by_name=true, hive_partitioning=true)
        """
    )
    validations = _validations(con)
    if validations["duplicate_fundamental_asof_id_count"] != 0:
        raise RuntimeError("fundamental_asof_id is not unique")
    if validations["statement_family_count"] != len(SOURCE_STATEMENT_FAMILIES):
        raise RuntimeError("Not all statement families were materialized")

    summary_path_sql = _sql_path(summary_path)
    con.execute(
        f"""
        copy (
            select
                statement_family,
                fundamental_quality_state,
                count(*) as rows,
                count(distinct ticker) as tickers,
                count(distinct instrument_id) as instruments,
                sum(case when valid_for_event_context_candidate then 1 else 0 end) as valid_for_event_context_candidate_rows
            from fundamentals_output
            group by statement_family, fundamental_quality_state
            order by statement_family, fundamental_quality_state
        )
        to '{summary_path_sql}'
        (header true, delimiter ',')
        """
    )

    instrument_manifest = _load_manifest(instrument_master_manifest)
    output_tree = _sha256_parquet_tree(dataset_dir)
    manifest = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "materialization_scope": MATERIALIZATION_SCOPE,
        "source_dataset_id": SOURCE_DATASET_ID,
        "source_subblock": SOURCE_SUBBLOCK,
        "source_statement_families": list(SOURCE_STATEMENT_FAMILIES),
        "excluded_source_subblocks": {
            "ratios": "review_sparse_vendor_derived_snapshot_not_statement_asof_core",
            "E:/TSIS/data/financial": "blocked_by_financial_consumption_policy_audit_status_FAIL",
        },
        "full_universe_claim": False,
        "output_root": _path_for_json(output_root),
        "dataset_path": _path_for_json(dataset_dir),
        "summary_path": _path_for_json(summary_path),
        "source_root": _path_for_json(source_root),
        "instrument_master_path": _path_for_json(instrument_master),
        "instrument_master_manifest_path": _path_for_json(instrument_master_manifest),
        "instrument_master_dataset_id": instrument_manifest.get("dataset_id"),
        "instrument_master_build_run_id": instrument_manifest.get("build_run_id"),
        "instrument_master_output_sha256": instrument_manifest.get("output_sha256"),
        "source_inventory": _source_inventory(con, source_root),
        "output_tree": output_tree,
        "validations": validations,
        "as_of_semantics": "filing_date_available_from_date_only",
        "period_end_semantics": "accounting_period_end_not_availability_date",
        "requires_event_time_filter": True,
        "direct_rl_training_allowed": False,
        "contracts": CONTRACTS,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False, default=_json_default))
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize fundamentals_asof_table_v0_1.")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--instrument-master", type=Path, default=DEFAULT_INSTRUMENT_MASTER)
    parser.add_argument(
        "--instrument-master-manifest",
        type=Path,
        default=DEFAULT_INSTRUMENT_MASTER_MANIFEST,
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    materialize(
        source_root=args.source_root,
        instrument_master=args.instrument_master,
        instrument_master_manifest=args.instrument_master_manifest,
        output_root=args.output_root,
    )


if __name__ == "__main__":
    main()
