from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


DATASET_ID = "corporate_actions_table_v0_1"
SCHEMA_VERSION = "corporate_actions_table_v0_1"

DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)
DEFAULT_INSTRUMENT_MASTER_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\_instrument_master_manifest_v0_1.json"
)
DEFAULT_REFERENCE_ROOT = Path(r"E:\TSIS\data\reference")
DEFAULT_ADDITIONAL_CA_ROOT = Path(r"E:\TSIS\data\additional\corporate_actions")
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\corporate_actions_table")


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
    files = sorted(p for p in root.rglob("*.parquet") if p.is_file())
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


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def materialize_corporate_actions_table(
    instrument_master: Path,
    instrument_master_manifest: Path,
    reference_root: Path,
    additional_ca_root: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(instrument_master, "instrument master parquet")
    instrument_manifest = _load_manifest(instrument_master_manifest)
    _require(reference_root / "splits", "reference splits root")
    _require(reference_root / "dividends", "reference dividends root")
    _require(reference_root / "events", "reference events root")
    _require(additional_ca_root / "splits", "additional splits root")
    _require(additional_ca_root / "dividends", "additional dividends root")
    _require(additional_ca_root / "ticker_events", "additional ticker_events root")

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "corporate_actions_table_v0_1.parquet"
    summary_path = output_root / "_corporate_actions_table_summary_v0_1.csv"
    manifest_path = output_root / "_corporate_actions_table_manifest_v0_1.json"

    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists. Pass --overwrite to replace: {output_path}")

    build_run_id = datetime.now(timezone.utc).strftime("corporate_actions_table_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()

    con = duckdb.connect()
    query = f"""
    with instruments as (
        select
            ticker,
            instrument_id,
            cast(valid_from as date) as valid_from,
            cast(valid_to as date) as valid_to,
            schema_version as instrument_master_schema_version,
            build_run_id as instrument_master_build_run_id
        from read_parquet('{_sql_path(instrument_master)}')
        where is_lt1b_operational = true
    ),
    ref_splits as (
        select
            'reference' as source_system,
            'splits' as source_dataset,
            'E:/TSIS/data/reference/splits' as source_root,
            1 as source_priority,
            upper(ticker) as ticker,
            'split' as action_type,
            cast(execution_date as date) as action_date,
            id as source_event_id,
            cast(split_from as double) as split_from,
            cast(split_to as double) as split_to,
            cast(split_to as double) / nullif(cast(split_from as double), 0) as split_ratio,
            null::double as cash_amount,
            null::varchar as currency,
            null::date as declaration_date,
            null::date as ex_dividend_date,
            null::date as pay_date,
            null::date as record_date,
            null::varchar as dividend_type,
            null::integer as dividend_frequency,
            null::date as ticker_change_date,
            null::varchar as ticker_change_ticker,
            null::varchar as event_name,
            _ingested_utc as source_ingested_utc
        from read_parquet('{_sql_path(reference_root / "splits" / "**" / "*.parquet")}', union_by_name=true)
        where execution_date is not null and split_from is not null and split_to is not null
    ),
    add_splits as (
        select
            'additional' as source_system,
            'splits' as source_dataset,
            'E:/TSIS/data/additional/corporate_actions/splits' as source_root,
            2 as source_priority,
            upper(ticker) as ticker,
            'split' as action_type,
            cast(execution_date as date) as action_date,
            id as source_event_id,
            cast(split_from as double) as split_from,
            cast(split_to as double) as split_to,
            cast(split_to as double) / nullif(cast(split_from as double), 0) as split_ratio,
            null::double as cash_amount,
            null::varchar as currency,
            null::date as declaration_date,
            null::date as ex_dividend_date,
            null::date as pay_date,
            null::date as record_date,
            null::varchar as dividend_type,
            null::integer as dividend_frequency,
            null::date as ticker_change_date,
            null::varchar as ticker_change_ticker,
            null::varchar as event_name,
            _ingested_utc as source_ingested_utc
        from read_parquet('{_sql_path(additional_ca_root / "splits" / "**" / "*.parquet")}', union_by_name=true)
        where coalesce(_empty, false) = false
          and execution_date is not null
          and split_from is not null
          and split_to is not null
    ),
    ref_dividends as (
        select
            'reference' as source_system,
            'dividends' as source_dataset,
            'E:/TSIS/data/reference/dividends' as source_root,
            1 as source_priority,
            upper(ticker) as ticker,
            'dividend' as action_type,
            cast(ex_dividend_date as date) as action_date,
            id as source_event_id,
            null::double as split_from,
            null::double as split_to,
            null::double as split_ratio,
            cast(cash_amount as double) as cash_amount,
            currency,
            cast(declaration_date as date) as declaration_date,
            cast(ex_dividend_date as date) as ex_dividend_date,
            cast(pay_date as date) as pay_date,
            cast(record_date as date) as record_date,
            dividend_type,
            cast(frequency as integer) as dividend_frequency,
            null::date as ticker_change_date,
            null::varchar as ticker_change_ticker,
            null::varchar as event_name,
            _ingested_utc as source_ingested_utc
        from read_parquet('{_sql_path(reference_root / "dividends" / "**" / "*.parquet")}', union_by_name=true)
        where ex_dividend_date is not null and cash_amount is not null
    ),
    add_dividends as (
        select
            'additional' as source_system,
            'dividends' as source_dataset,
            'E:/TSIS/data/additional/corporate_actions/dividends' as source_root,
            2 as source_priority,
            upper(ticker) as ticker,
            'dividend' as action_type,
            cast(ex_dividend_date as date) as action_date,
            id as source_event_id,
            null::double as split_from,
            null::double as split_to,
            null::double as split_ratio,
            cast(cash_amount as double) as cash_amount,
            currency,
            cast(declaration_date as date) as declaration_date,
            cast(ex_dividend_date as date) as ex_dividend_date,
            cast(pay_date as date) as pay_date,
            cast(record_date as date) as record_date,
            dividend_type,
            cast(frequency as integer) as dividend_frequency,
            null::date as ticker_change_date,
            null::varchar as ticker_change_ticker,
            null::varchar as event_name,
            _ingested_utc as source_ingested_utc
        from read_parquet('{_sql_path(additional_ca_root / "dividends" / "**" / "*.parquet")}', union_by_name=true)
        where coalesce(_empty, false) = false
          and ex_dividend_date is not null
          and cash_amount is not null
    ),
    ref_events_raw as (
        select
            upper(ticker) as ticker,
            name as event_name,
            _ingested_utc as source_ingested_utc,
            unnest(events) as e
        from read_parquet('{_sql_path(reference_root / "events" / "**" / "*.parquet")}', union_by_name=true)
        where events is not null
    ),
    ref_events as (
        select
            'reference' as source_system,
            'events' as source_dataset,
            'E:/TSIS/data/reference/events' as source_root,
            1 as source_priority,
            ticker,
            'ticker_change' as action_type,
            cast(e.date as date) as action_date,
            sha256(concat_ws('|', 'reference', ticker, e.type, cast(e.date as varchar), coalesce(e.ticker_change.ticker, ''))) as source_event_id,
            null::double as split_from,
            null::double as split_to,
            null::double as split_ratio,
            null::double as cash_amount,
            null::varchar as currency,
            null::date as declaration_date,
            null::date as ex_dividend_date,
            null::date as pay_date,
            null::date as record_date,
            null::varchar as dividend_type,
            null::integer as dividend_frequency,
            cast(e.date as date) as ticker_change_date,
            e.ticker_change.ticker as ticker_change_ticker,
            event_name,
            source_ingested_utc
        from ref_events_raw
        where e.type = 'ticker_change' and e.date is not null
    ),
    add_events as (
        select
            'additional' as source_system,
            'ticker_events' as source_dataset,
            'E:/TSIS/data/additional/corporate_actions/ticker_events' as source_root,
            2 as source_priority,
            upper(ticker) as ticker,
            'ticker_change' as action_type,
            cast(date as date) as action_date,
            sha256(concat_ws('|', 'additional', upper(ticker), type, cast(date as varchar), coalesce("ticker_change.ticker", ''))) as source_event_id,
            null::double as split_from,
            null::double as split_to,
            null::double as split_ratio,
            null::double as cash_amount,
            null::varchar as currency,
            null::date as declaration_date,
            null::date as ex_dividend_date,
            null::date as pay_date,
            null::date as record_date,
            null::varchar as dividend_type,
            null::integer as dividend_frequency,
            cast(date as date) as ticker_change_date,
            "ticker_change.ticker" as ticker_change_ticker,
            name as event_name,
            _ingested_utc as source_ingested_utc
        from read_parquet('{_sql_path(additional_ca_root / "ticker_events" / "**" / "*.parquet")}', union_by_name=true)
        where coalesce(_empty, false) = false
          and type = 'ticker_change'
          and date is not null
    ),
    unioned as (
        select * from ref_splits
        union all select * from add_splits
        union all select * from ref_dividends
        union all select * from add_dividends
        union all select * from ref_events
        union all select * from add_events
    ),
    joined as (
        select
            i.instrument_id,
            u.ticker,
            u.action_type,
            u.action_date,
            u.source_system,
            u.source_dataset,
            u.source_root,
            u.source_priority,
            u.source_event_id,
            u.split_from,
            u.split_to,
            u.split_ratio,
            u.cash_amount,
            u.currency,
            u.declaration_date,
            u.ex_dividend_date,
            u.pay_date,
            u.record_date,
            u.dividend_type,
            u.dividend_frequency,
            u.ticker_change_date,
            u.ticker_change_ticker,
            u.event_name,
            u.source_ingested_utc,
            i.valid_from,
            i.valid_to,
            u.action_date between i.valid_from and i.valid_to as within_instrument_valid_window,
            i.instrument_master_schema_version,
            i.instrument_master_build_run_id
        from unioned u
        inner join instruments i on u.ticker = i.ticker
    )
    select
        sha256(concat_ws('|',
            instrument_id,
            ticker,
            action_type,
            cast(action_date as varchar),
            source_system,
            source_dataset,
            coalesce(source_event_id, ''),
            coalesce(cast(split_from as varchar), ''),
            coalesce(cast(split_to as varchar), ''),
            coalesce(cast(cash_amount as varchar), ''),
            coalesce(ticker_change_ticker, '')
        )) as corporate_action_id,
        instrument_id,
        ticker,
        action_type,
        action_date,
        extract(year from action_date)::integer as action_year,
        source_system,
        source_dataset,
        source_root,
        source_priority,
        source_event_id,
        source_system = 'reference' as is_reference_primary_source,
        source_system = 'additional' as is_additional_secondary_source,
        split_from,
        split_to,
        split_ratio,
        cash_amount,
        currency,
        declaration_date,
        ex_dividend_date,
        pay_date,
        record_date,
        dividend_type,
        dividend_frequency,
        ticker_change_date,
        ticker_change_ticker,
        event_name,
        source_ingested_utc,
        valid_from,
        valid_to,
        within_instrument_valid_window,
        instrument_master_schema_version,
        instrument_master_build_run_id,
        '{build_run_id}' as build_run_id,
        '{SCHEMA_VERSION}' as schema_version,
        '{created_at_utc}' as created_at_utc
    from joined
    order by ticker, action_date, action_type, source_priority, source_event_id
    """

    df = con.execute(query).fetchdf()

    duplicate_id_count = int(df["corporate_action_id"].duplicated().sum())
    missing_action_date_count = int(df["action_date"].isna().sum())
    missing_instrument_id_count = int(df["instrument_id"].isna().sum())
    invalid_split_terms_count = int(
        ((df["action_type"] == "split") & ((df["split_from"] <= 0) | (df["split_to"] <= 0))).sum()
    )
    negative_dividend_amount_count = int(
        ((df["action_type"] == "dividend") & (df["cash_amount"] < 0)).sum()
    )
    missing_ticker_change_target_count = int(
        ((df["action_type"] == "ticker_change") & df["ticker_change_ticker"].isna()).sum()
    )
    hard_fail_count = int(
        duplicate_id_count
        + missing_action_date_count
        + missing_instrument_id_count
        + invalid_split_terms_count
        + negative_dividend_amount_count
        + (1 if len(df) == 0 else 0)
    )

    if hard_fail_count > 0:
        raise RuntimeError(
            "Hard validation failed: "
            + json.dumps(
                {
                    "duplicate_id_count": duplicate_id_count,
                    "missing_action_date_count": missing_action_date_count,
                    "missing_instrument_id_count": missing_instrument_id_count,
                    "invalid_split_terms_count": invalid_split_terms_count,
                    "negative_dividend_amount_count": negative_dividend_amount_count,
                    "hard_fail_count": hard_fail_count,
                },
                indent=2,
            )
        )

    df.to_parquet(output_path, index=False)

    action_type_counts = {str(k): int(v) for k, v in df["action_type"].value_counts().sort_index().items()}
    source_system_counts = {str(k): int(v) for k, v in df["source_system"].value_counts().sort_index().items()}
    counts_by_source_action = (
        df.groupby(["source_system", "action_type"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["source_system", "action_type"])
    )
    counts_by_source_action_dict = {
        f"{row.source_system}:{row.action_type}": int(row.rows)
        for row in counts_by_source_action.itertuples(index=False)
    }
    cross_source_overlap_groups = int(
        df.groupby(["ticker", "action_type", "action_date"], dropna=False)["source_system"]
        .nunique()
        .gt(1)
        .sum()
    )
    validations: dict[str, Any] = {
        "row_count": int(len(df)),
        "ticker_count": int(df["ticker"].nunique()),
        "instrument_id_count": int(df["instrument_id"].nunique()),
        "action_type_counts": action_type_counts,
        "source_system_counts": source_system_counts,
        "counts_by_source_action": counts_by_source_action_dict,
        "first_action_date": str(df["action_date"].min()),
        "last_action_date": str(df["action_date"].max()),
        "within_instrument_valid_window_false_count": int((~df["within_instrument_valid_window"]).sum()),
        "cross_source_overlap_groups": cross_source_overlap_groups,
        "duplicate_corporate_action_id_count": duplicate_id_count,
        "missing_action_date_count": missing_action_date_count,
        "missing_instrument_id_count": missing_instrument_id_count,
        "invalid_split_terms_count": invalid_split_terms_count,
        "negative_dividend_amount_count": negative_dividend_amount_count,
        "missing_ticker_change_target_count": missing_ticker_change_target_count,
        "hard_fail_count": hard_fail_count,
    }

    summary_rows = [
        {"metric": "rows", "value": validations["row_count"]},
        {"metric": "tickers", "value": validations["ticker_count"]},
        {"metric": "instrument_ids", "value": validations["instrument_id_count"]},
        {"metric": "first_action_date", "value": validations["first_action_date"]},
        {"metric": "last_action_date", "value": validations["last_action_date"]},
        {"metric": "hard_fail_count", "value": validations["hard_fail_count"]},
        {"metric": "duplicate_corporate_action_id_count", "value": duplicate_id_count},
        {"metric": "within_instrument_valid_window_false_count", "value": validations["within_instrument_valid_window_false_count"]},
        {"metric": "cross_source_overlap_groups", "value": cross_source_overlap_groups},
    ]
    for key, value in action_type_counts.items():
        summary_rows.append({"metric": f"action_type_{key}", "value": value})
    for key, value in source_system_counts.items():
        summary_rows.append({"metric": f"source_system_{key}", "value": value})
    for key, value in counts_by_source_action_dict.items():
        summary_rows.append({"metric": f"source_action_{key}", "value": value})
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)

    source_fingerprints = {
        "reference_splits": _sha256_tree(reference_root / "splits"),
        "reference_dividends": _sha256_tree(reference_root / "dividends"),
        "reference_events": _sha256_tree(reference_root / "events"),
        "additional_splits": _sha256_tree(additional_ca_root / "splits"),
        "additional_dividends": _sha256_tree(additional_ca_root / "dividends"),
        "additional_ticker_events": _sha256_tree(additional_ca_root / "ticker_events"),
    }

    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": str(output_path),
        "summary_path": str(summary_path),
        "source_instrument_master": str(instrument_master),
        "source_instrument_master_sha256": _sha256(instrument_master),
        "source_instrument_master_manifest": str(instrument_master_manifest),
        "source_instrument_master_build_run_id": instrument_manifest.get("build_run_id"),
        "source_reference_root": str(reference_root),
        "source_additional_corporate_actions_root": str(additional_ca_root),
        "source_fingerprints": source_fingerprints,
        "validations": validations,
        "contracts": {
            "dataset_contract": "01_foundations/contract_registry/dataset_contracts/corporate_actions_table_dataset_contract_v0_1.md",
            "schema_contract": "01_foundations/canonical_schemas/outputs/corporate_actions_table_schema_contract.md",
            "consumption_policy": "01_foundations/data_consumption_policies/corporate_actions_table_consumption_policy.md",
            "registry_entry": "01_foundations/dataset_registry/outputs/corporate_actions_table_registry_entry.yaml",
            "validators": "01_foundations/validators/outputs/corporate_actions_table_validators.md",
        },
    }
    manifest["output_sha256"] = _sha256(output_path)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa corporate_actions_table_v0_1.")
    ap.add_argument("--instrument-master", default=str(DEFAULT_INSTRUMENT_MASTER))
    ap.add_argument("--instrument-master-manifest", default=str(DEFAULT_INSTRUMENT_MASTER_MANIFEST))
    ap.add_argument("--reference-root", default=str(DEFAULT_REFERENCE_ROOT))
    ap.add_argument("--additional-ca-root", default=str(DEFAULT_ADDITIONAL_CA_ROOT))
    ap.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    materialize_corporate_actions_table(
        instrument_master=Path(args.instrument_master),
        instrument_master_manifest=Path(args.instrument_master_manifest),
        reference_root=Path(args.reference_root),
        additional_ca_root=Path(args.additional_ca_root),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

