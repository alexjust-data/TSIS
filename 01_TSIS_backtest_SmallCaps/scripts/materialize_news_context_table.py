from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb


DATASET_ID = "news_context_table_v0_1"
SCHEMA_VERSION = "news_context_table_v0_1"
QUALITY_POLICY_VERSION = "news_context_table_policy_v0_1"
MATERIALIZATION_SCOPE = "additional_news_lt1b_published_utc_context_v0_1"
SOURCE_DATASET_ID = "additional_v0_1"
SOURCE_SUBBLOCK = "news"

DEFAULT_SOURCE_ROOT = Path(r"E:\TSIS\data\additional\news")
DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)
DEFAULT_INSTRUMENT_MASTER_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\_instrument_master_manifest_v0_1.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\news_context_table")

CONTRACTS = {
    "schema": "01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/news_context_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/news_context_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/news_context_table_registry_entry.yaml",
    "validator": "01_foundations/validators/outputs/news_context_table_validators.md",
    "source_additional_contract": "01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md",
    "source_additional_news_schema": "01_foundations/canonical_schemas/additional/additional_news_schema_contract.md",
    "source_additional_policy": "01_foundations/data_consumption_policies/additional_consumption_policy.md",
    "output_target_contract": "01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md",
    "materializer": "scripts/materialize_news_context_table.py",
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
    if "news_context_table" not in str(resolved_dataset):
        raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _source_pattern(source_root: Path) -> str:
    return _sql_path(source_root / "news" / "ticker=*" / "news_*.parquet")


def _prepare_instrument_tables(
    con: duckdb.DuckDBPyConnection,
    instrument_master: Path,
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


def _create_source_inventory(
    con: duckdb.DuckDBPyConnection,
    source_root: Path,
) -> None:
    source_root_sql = _sql_path(source_root)
    pattern = _source_pattern(source_root)
    con.execute(
        f"""
        create or replace temp table source_file_inventory as
        select
            replace(filename, '\\', '/') as source_file,
            replace(
                replace(filename, '\\', '/'),
                '{source_root_sql}/',
                ''
            ) as source_file_relative_path,
            regexp_extract(replace(filename, '\\', '/'), 'ticker=([^/]+)', 1) as source_path_ticker,
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


def _source_inventory(con: duckdb.DuckDBPyConnection, source_root: Path) -> dict[str, Any]:
    rows = con.execute(
        """
        select
            source_file_relative_path,
            source_path_ticker,
            metadata_rows,
            business_rows,
            empty_sentinel
        from source_file_inventory
        order by source_file_relative_path
        """
    ).fetchall()
    digest = hashlib.sha256()
    for relative_path, source_path_ticker, metadata_rows, business_rows, empty_sentinel in rows:
        digest.update(str(relative_path).encode("utf-8"))
        digest.update(str(source_path_ticker).encode("utf-8"))
        digest.update(str(metadata_rows).encode("ascii"))
        digest.update(str(business_rows).encode("ascii"))
        digest.update(str(bool(empty_sentinel)).encode("ascii"))
    return {
        "source_root": _path_for_json(source_root),
        "file_count": len(rows),
        "business_file_count": int(sum(1 for row in rows if int(row[3]) > 0)),
        "empty_sentinel_file_count": int(sum(1 for row in rows if bool(row[4]))),
        "metadata_row_count": int(sum(int(row[2]) for row in rows)),
        "business_row_count": int(sum(int(row[3]) for row in rows)),
        "source_inventory_hash": digest.hexdigest(),
        "inventory_hash_semantics": "sha256(relative_path,source_path_ticker,metadata_rows,business_rows,empty_sentinel); not full file content hash",
    }


def _materialize_output(
    con: duckdb.DuckDBPyConnection,
    source_root: Path,
    dataset_dir: Path,
    build_run_id: str,
    created_at_utc: str,
) -> None:
    source_root_sql = _sql_path(source_root)
    pattern = _source_pattern(source_root)
    con.execute(
        f"""
        create or replace temp table raw_business as
        select
            row_number() over (
                partition by filename
                order by
                    try_cast(published_utc as timestamp) nulls last,
                    id nulls last,
                    article_url nulls last
            ) - 1 as source_file_row_number,
            upper(trim(coalesce(ticker, regexp_extract(replace(filename, '\\', '/'), 'ticker=([^/]+)', 1)))) as ticker_clean,
            regexp_extract(replace(filename, '\\', '/'), 'ticker=([^/]+)', 1) as source_path_ticker,
            replace(filename, '\\', '/') as source_file_norm,
            replace(
                replace(filename, '\\', '/'),
                '{source_root_sql}/',
                ''
            ) as source_file_relative_path,
            cast(id as varchar) as article_id,
            title,
            sha256(coalesce(title, '')) as title_hash,
            author,
            try_cast(published_utc as timestamp) as published_utc_ts,
            published_utc as published_utc_raw,
            cast(try_cast(published_utc as timestamp) as date) as published_date,
            extract(year from try_cast(published_utc as timestamp))::integer as published_year,
            article_url,
            sha256(coalesce(article_url, '')) as article_url_hash,
            tickers as payload_tickers,
            cast(tickers as varchar) as payload_tickers_text,
            array_length(tickers) as payload_ticker_count,
            case when tickers is null then false else list_contains(tickers, upper(trim(coalesce(ticker, regexp_extract(replace(filename, '\\', '/'), 'ticker=([^/]+)', 1))))) end as requested_ticker_in_payload_tickers,
            image_url,
            description,
            keywords,
            cast(keywords as varchar) as keywords_text,
            insights,
            cast(insights as varchar) as insights_text,
            "publisher.name" as publisher_name,
            "publisher.homepage_url" as publisher_homepage_url,
            "publisher.logo_url" as publisher_logo_url,
            "publisher.favicon_url" as publisher_favicon_url,
            amp_url,
            _dataset,
            _ingested_utc
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
         and b.published_date is not null
         and (i.valid_from is null or i.valid_from <= b.published_date)
         and (i.valid_to is null or i.valid_to >= b.published_date)
        """
    )
    con.execute(
        f"""
        create or replace temp table news_context_output as
        select
            sha256(concat_ws(
                chr(31),
                '{DATASET_ID}',
                b.source_file_relative_path,
                cast(b.source_file_row_number as varchar),
                b.ticker_clean,
                coalesce(b.article_id, ''),
                coalesce(cast(b.published_utc_ts as varchar), ''),
                coalesce(b.article_url, '')
            )) as news_context_id,
            b.ticker_clean as ticker,
            b.source_path_ticker,
            m.instrument_id,
            '{SOURCE_DATASET_ID}' as source_dataset_id,
            '{SOURCE_SUBBLOCK}' as source_subblock,
            b.article_id,
            b.article_url,
            b.article_url_hash,
            b.title,
            b.title_hash,
            b.author,
            b.publisher_name,
            b.publisher_homepage_url,
            b.publisher_logo_url,
            b.publisher_favicon_url,
            b.image_url,
            b.amp_url,
            b.description,
            b.published_utc_ts as published_utc,
            b.published_utc_raw,
            b.published_date,
            b.published_year,
            b.published_utc_ts as as_of_utc,
            b.published_date as as_of_date,
            'published_utc_vendor_timestamp' as as_of_semantics,
            b.payload_tickers,
            b.payload_tickers_text,
            b.payload_ticker_count,
            b.requested_ticker_in_payload_tickers,
            (b.payload_ticker_count = 1 and b.requested_ticker_in_payload_tickers) as is_mono_ticker_article,
            (b.payload_ticker_count > 1 and b.requested_ticker_in_payload_tickers) as is_multi_ticker_article,
            case
                when b.payload_ticker_count is null then 'review_missing_article_tickers'
                when not b.requested_ticker_in_payload_tickers then 'review_requested_ticker_not_in_payload'
                when b.payload_ticker_count = 1 then 'good_mono_ticker_attributed'
                when b.payload_ticker_count > 1 then 'review_multi_ticker_attributed'
                else 'review_unclassified_ticker_attribution'
            end as ticker_attribution_state,
            b.keywords,
            b.keywords_text,
            b.insights,
            b.insights_text,
            (p.ticker is not null) as instrument_master_ticker_present,
            (m.instrument_id is not null) as instrument_identity_temporal_match,
            case
                when p.ticker is null then 'review_no_instrument_master_ticker'
                when b.published_date is null then 'bad_missing_published_utc'
                when m.instrument_id is null then 'review_no_temporal_identity'
                else 'good_temporal_match'
            end as instrument_identity_state,
            m.is_common_stock,
            m.is_lt1b_operational,
            m.lt1b_classification_1b,
            case
                when b.published_utc_ts is null then 'bad_missing_published_utc'
                when b.article_id is null or trim(b.article_id) = '' then 'bad_missing_article_id'
                when b.article_url is null or trim(b.article_url) = '' then 'bad_missing_article_url'
                when b.title is null or trim(b.title) = '' then 'bad_missing_title'
                when b.payload_ticker_count is null then 'review_missing_article_tickers'
                when not b.requested_ticker_in_payload_tickers then 'review_requested_ticker_not_in_payload'
                when m.instrument_id is null then 'review_no_temporal_identity'
                when b.payload_ticker_count = 1 then 'good_mono_ticker_news_context'
                when b.payload_ticker_count > 1 then 'good_review_multi_ticker_news_context'
                else 'review_unclassified_news_context'
            end as news_quality_state,
            case
                when b.published_utc_ts is null then false
                when b.article_id is null or trim(b.article_id) = '' then false
                when b.article_url is null or trim(b.article_url) = '' then false
                when b.title is null or trim(b.title) = '' then false
                when not b.requested_ticker_in_payload_tickers then false
                when m.instrument_id is null then false
                else true
            end as valid_for_event_context_candidate,
            case
                when b.published_utc_ts is null then false
                when b.article_id is null or trim(b.article_id) = '' then false
                when b.article_url is null or trim(b.article_url) = '' then false
                when b.title is null or trim(b.title) = '' then false
                when not b.requested_ticker_in_payload_tickers then false
                when m.instrument_id is null then false
                else true
            end as valid_for_catalyst_timing_candidate,
            case
                when b.published_utc_ts is null then false
                when b.article_id is null or trim(b.article_id) = '' then false
                when b.article_url is null or trim(b.article_url) = '' then false
                when b.title is null or trim(b.title) = '' then false
                when not b.requested_ticker_in_payload_tickers then false
                when m.instrument_id is null then false
                else true
            end as valid_for_ml_feature_candidate,
            case
                when b.published_utc_ts is null then false
                when b.article_id is null or trim(b.article_id) = '' then false
                when b.article_url is null or trim(b.article_url) = '' then false
                when b.title is null or trim(b.title) = '' then false
                when not b.requested_ticker_in_payload_tickers then false
                when m.instrument_id is null then false
                else true
            end as valid_for_state_component_candidate,
            false as valid_for_rl_training_direct,
            true as requires_event_time_filter,
            true as prohibited_without_asof_filter,
            true as contains_future_information_without_event_filter,
            false as causal_proof_by_itself,
            false as same_day_causal_claim_allowed_without_intraday_ordering,
            true as timezone_alignment_required_for_intraday_claims,
            '{source_root_sql}' as source_root,
            b.source_file_norm as source_file,
            b.source_file_relative_path,
            b.source_file_row_number,
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
            '{created_at_utc}' as created_at_utc
        from raw_business b
        left join temporal_instrument_match m
          on b.source_file_relative_path = m.source_file_relative_path
         and b.source_file_row_number = m.source_file_row_number
         and m.rn = 1
        left join ticker_presence p
          on b.ticker_clean = p.ticker
        """
    )
    con.execute(
        f"""
        copy news_context_output
        to '{_sql_path(dataset_dir)}'
        (
            format parquet,
            compression zstd,
            partition_by (published_year),
            overwrite_or_ignore true
        )
        """
    )


def _fetch_one(con: duckdb.DuckDBPyConnection, sql: str) -> Any:
    return con.execute(sql).fetchone()[0]


def _fetch_dict(con: duckdb.DuckDBPyConnection, sql: str) -> dict[str, int]:
    return {str(key): int(value) for key, value in con.execute(sql).fetchall()}


def _validations(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    return {
        "row_count": int(_fetch_one(con, "select count(*) from news_context_output")),
        "unique_news_context_id_count": int(
            _fetch_one(con, "select count(distinct news_context_id) from news_context_output")
        ),
        "duplicate_news_context_id_count": int(
            _fetch_one(con, "select count(*) - count(distinct news_context_id) from news_context_output")
        ),
        "duplicate_source_key_count": int(
            _fetch_one(
                con,
                """
                select count(*) - count(distinct sha256(concat_ws(
                    chr(31),
                    coalesce(article_id, ''),
                    coalesce(published_utc_raw, ''),
                    ticker
                )))
                from news_context_output
                """,
            )
        ),
        "ticker_count": int(_fetch_one(con, "select count(distinct ticker) from news_context_output")),
        "instrument_count": int(
            _fetch_one(con, "select count(distinct instrument_id) from news_context_output")
        ),
        "publisher_count": int(
            _fetch_one(con, "select count(distinct publisher_name) from news_context_output")
        ),
        "first_published_utc": str(
            _fetch_one(con, "select min(published_utc) from news_context_output")
        ),
        "last_published_utc": str(
            _fetch_one(con, "select max(published_utc) from news_context_output")
        ),
        "news_quality_state_counts": _fetch_dict(
            con,
            """
            select news_quality_state, count(*)
            from news_context_output
            group by news_quality_state
            order by news_quality_state
            """,
        ),
        "ticker_attribution_state_counts": _fetch_dict(
            con,
            """
            select ticker_attribution_state, count(*)
            from news_context_output
            group by ticker_attribution_state
            order by ticker_attribution_state
            """,
        ),
        "instrument_identity_state_counts": _fetch_dict(
            con,
            """
            select instrument_identity_state, count(*)
            from news_context_output
            group by instrument_identity_state
            order by instrument_identity_state
            """,
        ),
        "published_year_counts": _fetch_dict(
            con,
            """
            select published_year, count(*)
            from news_context_output
            group by published_year
            order by published_year
            """,
        ),
        "missing_published_utc_rows": int(
            _fetch_one(con, "select count(*) from news_context_output where published_utc is null")
        ),
        "missing_article_id_rows": int(
            _fetch_one(
                con,
                "select count(*) from news_context_output where article_id is null or trim(article_id) = ''",
            )
        ),
        "missing_article_url_rows": int(
            _fetch_one(
                con,
                "select count(*) from news_context_output where article_url is null or trim(article_url) = ''",
            )
        ),
        "missing_title_rows": int(
            _fetch_one(
                con,
                "select count(*) from news_context_output where title is null or trim(title) = ''",
            )
        ),
        "requested_ticker_not_in_payload_rows": int(
            _fetch_one(
                con,
                "select count(*) from news_context_output where not requested_ticker_in_payload_tickers",
            )
        ),
        "mono_ticker_article_rows": int(
            _fetch_one(con, "select count(*) from news_context_output where is_mono_ticker_article")
        ),
        "multi_ticker_article_rows": int(
            _fetch_one(con, "select count(*) from news_context_output where is_multi_ticker_article")
        ),
        "valid_for_event_context_candidate_rows": int(
            _fetch_one(
                con,
                "select count(*) from news_context_output where valid_for_event_context_candidate",
            )
        ),
        "valid_for_catalyst_timing_candidate_rows": int(
            _fetch_one(
                con,
                "select count(*) from news_context_output where valid_for_catalyst_timing_candidate",
            )
        ),
        "valid_for_ml_feature_candidate_rows": int(
            _fetch_one(con, "select count(*) from news_context_output where valid_for_ml_feature_candidate")
        ),
        "valid_for_state_component_candidate_rows": int(
            _fetch_one(
                con,
                "select count(*) from news_context_output where valid_for_state_component_candidate",
            )
        ),
        "valid_for_rl_training_direct_rows": int(
            _fetch_one(con, "select count(*) from news_context_output where valid_for_rl_training_direct")
        ),
        "full_universe_claim_rows": int(
            _fetch_one(con, "select count(*) from news_context_output where full_universe_claim")
        ),
    }


def _write_summary(con: duckdb.DuckDBPyConnection, summary_path: Path) -> None:
    summary = con.execute(
        """
        select
            news_quality_state,
            ticker_attribution_state,
            instrument_identity_state,
            count(*) as rows,
            count(distinct ticker) as tickers,
            count(distinct instrument_id) as instruments,
            min(published_utc) as first_published_utc,
            max(published_utc) as last_published_utc,
            sum(case when valid_for_event_context_candidate then 1 else 0 end) as valid_for_event_context_candidate_rows,
            sum(case when valid_for_ml_feature_candidate then 1 else 0 end) as valid_for_ml_feature_candidate_rows,
            sum(case when valid_for_state_component_candidate then 1 else 0 end) as valid_for_state_component_candidate_rows
        from news_context_output
        group by news_quality_state, ticker_attribution_state, instrument_identity_state
        order by news_quality_state, ticker_attribution_state, instrument_identity_state
        """
    ).fetchdf()
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)


def materialize_news_context_table(
    source_root: Path,
    instrument_master: Path,
    instrument_master_manifest: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(source_root, "additional news source root")
    _require(instrument_master, "instrument master")
    instrument_manifest = _load_manifest(instrument_master_manifest)

    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / DATASET_ID
    manifest_path = output_root / "_news_context_table_manifest_v0_1.json"
    summary_path = output_root / "_news_context_table_summary_v0_1.csv"

    if overwrite:
        _safe_remove_dataset_dir(dataset_dir, output_root)
    if dataset_dir.exists() and any(dataset_dir.rglob("*.parquet")):
        raise FileExistsError(f"Output exists; rerun with --overwrite: {dataset_dir}")
    dataset_dir.mkdir(parents=True, exist_ok=True)

    build_started = _utc_now()
    build_run_id = f"{DATASET_ID}_{build_started.strftime('%Y%m%dT%H%M%SZ')}"
    created_at_utc = build_started.isoformat()

    con = duckdb.connect()
    _prepare_instrument_tables(con, instrument_master)
    _create_source_inventory(con, source_root)
    _materialize_output(con, source_root, dataset_dir, build_run_id, created_at_utc)
    _write_summary(con, summary_path)
    validations = _validations(con)
    source_inventory = _source_inventory(con, source_root)

    hard_failures = {
        "duplicate_news_context_id_count": validations["duplicate_news_context_id_count"],
        "duplicate_source_key_count": validations["duplicate_source_key_count"],
        "missing_published_utc_rows": validations["missing_published_utc_rows"],
        "missing_article_id_rows": validations["missing_article_id_rows"],
        "missing_article_url_rows": validations["missing_article_url_rows"],
        "missing_title_rows": validations["missing_title_rows"],
    }
    hard_fail_count = int(sum(int(value) for value in hard_failures.values()))
    validations["hard_failures"] = hard_failures
    validations["hard_fail_count"] = hard_fail_count
    if hard_fail_count > 0:
        raise RuntimeError(
            "Hard validation failed: "
            + json.dumps(hard_failures, indent=2, sort_keys=True, default=_json_default)
        )

    output_tree = _sha256_parquet_tree(dataset_dir)
    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "materialization_scope": MATERIALIZATION_SCOPE,
        "source_dataset_id": SOURCE_DATASET_ID,
        "source_subblock": SOURCE_SUBBLOCK,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "build_finished_at_utc": _utc_now().isoformat(),
        "dataset_path": _path_for_json(dataset_dir),
        "summary_path": _path_for_json(summary_path),
        "source_root": _path_for_json(source_root),
        "source_pattern": _source_pattern(source_root),
        "source_inventory": source_inventory,
        "source_instrument_master": _path_for_json(instrument_master),
        "source_instrument_master_sha256": _sha256(instrument_master),
        "source_instrument_master_manifest": _path_for_json(instrument_master_manifest),
        "source_instrument_master_build_run_id": instrument_manifest.get("build_run_id"),
        "source_instrument_master_schema_version": instrument_manifest.get("schema_version"),
        "output_tree": output_tree,
        "validations": validations,
        "full_universe_claim": False,
        "direct_rl_training_allowed": False,
        "requires_event_time_filter": True,
        "prohibited_without_asof_filter": True,
        "causal_proof_by_itself": False,
        "contracts": CONTRACTS,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True, default=_json_default))
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materializa news_context_table_v0_1.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--instrument-master", default=str(DEFAULT_INSTRUMENT_MASTER))
    parser.add_argument("--instrument-master-manifest", default=str(DEFAULT_INSTRUMENT_MASTER_MANIFEST))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    materialize_news_context_table(
        source_root=Path(args.source_root),
        instrument_master=Path(args.instrument_master),
        instrument_master_manifest=Path(args.instrument_master_manifest),
        output_root=Path(args.output_root),
        overwrite=args.overwrite,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
