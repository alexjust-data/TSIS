from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


DEFAULT_REFERENCE_ROOT = Path(r"E:\TSIS\data\reference")
DEFAULT_LT1B_PARQUET = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\backtest"
    r"\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff"
    r"\market_cap_cutoff_lt_1b_active_inactive.parquet"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\instrument_master")

SCHEMA_VERSION = "instrument_master_v0_1"
DATASET_ID = "instrument_master_v0_1"


def _sql_path(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _require_path(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def build_instrument_master(
    reference_root: Path,
    lt1b_parquet: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require_path(reference_root, "reference root")
    _require_path(lt1b_parquet, "lt1b parquet")

    all_tickers_glob = reference_root / "all_tickers" / "snapshot_date=*.parquet"
    overview_glob = reference_root / "overview" / "ticker=*" / "overview_*.parquet"
    events_glob = reference_root / "events" / "ticker=*" / "events_*.parquet"
    exchanges_path = reference_root / "exchanges" / "exchanges.parquet"
    ticker_types_path = reference_root / "ticker_types" / "ticker_types.parquet"

    for path, label in (
        (exchanges_path, "exchanges parquet"),
        (ticker_types_path, "ticker_types parquet"),
    ):
        _require_path(path, label)

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "instrument_master_v0_1.parquet"
    summary_path = output_root / "_instrument_master_summary_v0_1.csv"
    manifest_path = output_root / "_instrument_master_manifest_v0_1.json"

    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists. Pass --overwrite to replace: {output_path}")

    build_run_id = datetime.now(timezone.utc).strftime("instrument_master_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()

    query = f"""
with lt1b as (
    select
        upper(ticker) as ticker,
        cast(first_seen_date as date) as lt1b_first_seen_date,
        cast(last_observed_date as date) as lt1b_last_observed_date,
        cast(anchor_date_used as date) as lt1b_anchor_date_used,
        status_rebuilt as lt1b_status_rebuilt,
        classification_1b as lt1b_classification_1b,
        classification_reason_1b as lt1b_classification_reason_1b,
        market_cap_t as lt1b_market_cap_t,
        is_small_cap_t as lt1b_is_small_cap_t,
        shares_source as lt1b_shares_source,
        cast(shares_observed_date as date) as lt1b_shares_observed_date,
        shares_age_days as lt1b_shares_age_days,
        coalesce(cast(anchor_date_used as date), cast(last_observed_date as date)) as anchor_date_for_reference
    from read_parquet('{_sql_path(lt1b_parquet)}', union_by_name=true)
),
all_ranked as (
    select
        upper(a.ticker) as ticker,
        a.name as reference_name,
        a.market as reference_market,
        a.locale as reference_locale,
        a.primary_exchange as reference_primary_exchange,
        a.type as reference_type,
        a.active as reference_active,
        a.currency_name as reference_currency_name,
        a.cik as reference_cik,
        a.composite_figi as reference_composite_figi,
        a.share_class_figi as reference_share_class_figi,
        a.last_updated_utc as reference_last_updated_utc,
        try_cast(a.snapshot_date as date) as reference_snapshot_date,
        case
            when try_cast(a.snapshot_date as date) = l.anchor_date_for_reference then 'exact_anchor'
            when try_cast(a.snapshot_date as date) < l.anchor_date_for_reference then 'before_anchor'
            when try_cast(a.snapshot_date as date) > l.anchor_date_for_reference then 'after_anchor'
            else 'unknown'
        end as reference_snapshot_timing,
        row_number() over (
            partition by upper(a.ticker)
            order by
                case
                    when try_cast(a.snapshot_date as date) <= l.anchor_date_for_reference then 0
                    else 1
                end,
                case
                    when try_cast(a.snapshot_date as date) <= l.anchor_date_for_reference then try_cast(a.snapshot_date as date)
                    else null
                end desc,
                case
                    when try_cast(a.snapshot_date as date) > l.anchor_date_for_reference then try_cast(a.snapshot_date as date)
                    else null
                end asc
        ) as rn
    from read_parquet('{_sql_path(all_tickers_glob)}', union_by_name=true) a
    inner join lt1b l on upper(a.ticker) = l.ticker
),
overview_ranked as (
    select
        upper(o.ticker) as ticker,
        o.name as overview_name,
        o.market as overview_market,
        o.locale as overview_locale,
        o.primary_exchange as overview_primary_exchange,
        o.type as overview_type,
        o.active as overview_active,
        o.currency_name as overview_currency_name,
        o.cik as overview_cik,
        o.composite_figi as overview_composite_figi,
        o.share_class_figi as overview_share_class_figi,
        o.market_cap as overview_market_cap,
        o.sic_code as overview_sic_code,
        o.sic_description as overview_sic_description,
        o.list_date as overview_list_date,
        o.ticker_root as overview_ticker_root,
        o.weighted_shares_outstanding as overview_weighted_shares_outstanding,
        try_cast(o.request_date as date) as overview_request_date,
        row_number() over (
            partition by upper(o.ticker)
            order by
                case
                    when try_cast(o.request_date as date) <= l.anchor_date_for_reference then 0
                    else 1
                end,
                case
                    when try_cast(o.request_date as date) <= l.anchor_date_for_reference then try_cast(o.request_date as date)
                    else null
                end desc,
                case
                    when try_cast(o.request_date as date) > l.anchor_date_for_reference then try_cast(o.request_date as date)
                    else null
                end asc
        ) as rn
    from read_parquet('{_sql_path(overview_glob)}', union_by_name=true) o
    inner join lt1b l on upper(o.ticker) = l.ticker
),
event_rows as (
    select upper(ticker) as ticker, unnest(events) as e
    from read_parquet('{_sql_path(events_glob)}', union_by_name=true)
),
event_summary as (
    select
        ticker,
        true as has_reference_events,
        count(*) filter (where e.type = 'ticker_change') as ticker_change_event_count,
        min(try_cast(e.date as date)) filter (where e.type = 'ticker_change') as first_ticker_change_date,
        max(try_cast(e.date as date)) filter (where e.type = 'ticker_change') as latest_ticker_change_date
    from event_rows
    group by ticker
),
exchange_map as (
    select exchange_mic, exchange_name, exchange_acronym, exchange_operating_mic
    from (
        select
            mic as exchange_mic,
            name as exchange_name,
            acronym as exchange_acronym,
            operating_mic as exchange_operating_mic,
            row_number() over (partition by mic order by id) as rn
        from read_parquet('{_sql_path(exchanges_path)}', union_by_name=true)
        where mic is not null
    )
    where rn = 1
),
type_map as (
    select
        code as ticker_type_code,
        description as ticker_type_description
    from read_parquet('{_sql_path(ticker_types_path)}', union_by_name=true)
),
joined as (
    select
        l.*,
        a.* exclude(ticker, rn),
        o.* exclude(ticker, rn),
        ev.has_reference_events,
        coalesce(ev.ticker_change_event_count, 0) as ticker_change_event_count,
        ev.first_ticker_change_date,
        ev.latest_ticker_change_date
    from lt1b l
    left join all_ranked a on l.ticker = a.ticker and a.rn = 1
    left join overview_ranked o on l.ticker = o.ticker and o.rn = 1
    left join event_summary ev on l.ticker = ev.ticker
)
select
    case
        when nullif(coalesce(reference_share_class_figi, overview_share_class_figi), '') is not null
            then 'figi_share_class:' || coalesce(reference_share_class_figi, overview_share_class_figi)
        when nullif(coalesce(reference_composite_figi, overview_composite_figi), '') is not null
            then 'figi_composite:' || coalesce(reference_composite_figi, overview_composite_figi)
        when nullif(coalesce(reference_cik, overview_cik), '') is not null
            then 'cik_ticker:' || coalesce(reference_cik, overview_cik) || ':' || ticker
        else 'ticker:' || ticker
    end as instrument_id,
    ticker,
    case
        when nullif(coalesce(reference_share_class_figi, overview_share_class_figi), '') is not null then 'share_class_figi'
        when nullif(coalesce(reference_composite_figi, overview_composite_figi), '') is not null then 'composite_figi'
        when nullif(coalesce(reference_cik, overview_cik), '') is not null then 'cik_ticker'
        else 'ticker_only_fallback'
    end as identity_resolution_level,
    'lt1b_ticker_grain_v0_1' as ticker_identity_scope,
    lt1b_first_seen_date as valid_from,
    lt1b_last_observed_date as valid_to,
    coalesce(overview_name, reference_name) as name,
    coalesce(overview_market, reference_market) as market,
    coalesce(overview_locale, reference_locale) as locale,
    coalesce(overview_primary_exchange, reference_primary_exchange) as primary_exchange,
    coalesce(overview_type, reference_type) as ticker_type_code,
    tm.ticker_type_description,
    coalesce(overview_type, reference_type) = 'CS' as is_common_stock,
    coalesce(overview_active, reference_active) as active_in_reference,
    coalesce(overview_currency_name, reference_currency_name) as currency_name,
    coalesce(reference_cik, overview_cik) as cik,
    coalesce(reference_composite_figi, overview_composite_figi) as composite_figi,
    coalesce(reference_share_class_figi, overview_share_class_figi) as share_class_figi,
    em.exchange_name,
    em.exchange_acronym,
    em.exchange_mic,
    em.exchange_operating_mic,
    overview_request_date,
    overview_market_cap,
    overview_sic_code,
    overview_sic_description,
    try_cast(overview_list_date as date) as overview_list_date,
    overview_ticker_root,
    overview_weighted_shares_outstanding,
    true as is_lt1b_operational,
    lt1b_first_seen_date,
    lt1b_last_observed_date,
    lt1b_anchor_date_used,
    lt1b_status_rebuilt,
    lt1b_classification_1b,
    lt1b_classification_reason_1b,
    lt1b_market_cap_t,
    lt1b_is_small_cap_t,
    lt1b_shares_source,
    lt1b_shares_observed_date,
    lt1b_shares_age_days,
    coalesce(has_reference_events, false) as has_reference_events,
    ticker_change_event_count,
    first_ticker_change_date,
    latest_ticker_change_date,
    reference_snapshot_date,
    coalesce(reference_snapshot_timing, 'missing_reference_snapshot') as reference_snapshot_timing,
    reference_last_updated_utc,
    '{_sql_path(reference_root)}' as source_reference_root,
    '{_sql_path(lt1b_parquet)}' as source_lt1b_universe_path,
    '{build_run_id}' as build_run_id,
    '{SCHEMA_VERSION}' as schema_version,
    '{created_at_utc}' as created_at_utc
from joined j
left join exchange_map em
    on coalesce(j.overview_primary_exchange, j.reference_primary_exchange) = em.exchange_mic
left join type_map tm
    on coalesce(j.overview_type, j.reference_type) = tm.ticker_type_code
order by ticker
"""

    con = duckdb.connect()
    df = con.execute(query).fetchdf()

    validations: dict[str, Any] = {
        "row_count": int(len(df)),
        "ticker_count": int(df["ticker"].nunique(dropna=True)),
        "duplicate_ticker_count": int(df["ticker"].duplicated().sum()),
        "missing_ticker_count": int(df["ticker"].isna().sum()),
        "missing_instrument_id_count": int(df["instrument_id"].isna().sum()),
        "invalid_window_count": int(
            (pd.to_datetime(df["valid_from"], errors="coerce") > pd.to_datetime(df["valid_to"], errors="coerce")).sum()
        ),
        "identity_resolution_counts": df["identity_resolution_level"].value_counts(dropna=False).to_dict(),
        "ticker_type_counts": df["ticker_type_code"].fillna("<NA>").value_counts(dropna=False).head(50).to_dict(),
        "non_common_stock_count": int((df["is_common_stock"] != True).sum()),  # noqa: E712
        "ticker_change_review_count": int((df["ticker_change_event_count"] > 0).sum()),
        "reference_snapshot_timing_counts": df["reference_snapshot_timing"].value_counts(dropna=False).to_dict(),
    }
    validations["hard_fail_count"] = int(
        validations["duplicate_ticker_count"]
        + validations["missing_ticker_count"]
        + validations["missing_instrument_id_count"]
        + validations["invalid_window_count"]
    )

    if validations["hard_fail_count"] > 0:
        raise RuntimeError(f"Hard validation failed: {validations}")

    df.to_parquet(output_path, index=False)

    summary_rows = [
        {"metric": "rows", "value": validations["row_count"]},
        {"metric": "tickers", "value": validations["ticker_count"]},
        {"metric": "duplicate_ticker_count", "value": validations["duplicate_ticker_count"]},
        {"metric": "missing_instrument_id_count", "value": validations["missing_instrument_id_count"]},
        {"metric": "invalid_window_count", "value": validations["invalid_window_count"]},
        {"metric": "non_common_stock_count", "value": validations["non_common_stock_count"]},
        {"metric": "ticker_change_review_count", "value": validations["ticker_change_review_count"]},
    ]
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)

    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "source_reference_root": str(reference_root),
        "source_lt1b_universe_path": str(lt1b_parquet),
        "output_path": str(output_path),
        "summary_path": str(summary_path),
        "validations": validations,
        "contracts": {
            "dataset_contract": "01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md",
            "schema_contract": "01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md",
            "consumption_policy": "01_foundations/data_consumption_policies/instrument_master_consumption_policy.md",
            "registry_entry": "01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml",
            "validators": "01_foundations/validators/outputs/instrument_master_validators.md",
        },
    }
    manifest["output_sha256"] = _sha256(output_path)

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa instrument_master_v0_1 desde reference + lt1b_universe.")
    ap.add_argument("--reference-root", default=str(DEFAULT_REFERENCE_ROOT))
    ap.add_argument("--lt1b-parquet", default=str(DEFAULT_LT1B_PARQUET))
    ap.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    build_instrument_master(
        reference_root=Path(args.reference_root),
        lt1b_parquet=Path(args.lt1b_parquet),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
