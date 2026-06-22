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


DATASET_ID = "expected_data_calendar_v0_1"
SCHEMA_VERSION = "expected_data_calendar_v0_1"
POLICY_VERSION = "expected_data_calendar_policy_v0_1"

DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)
DEFAULT_INSTRUMENT_MASTER_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\_instrument_master_manifest_v0_1.json"
)
DEFAULT_MARKET_CALENDAR = Path(
    r"E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet"
)
DEFAULT_MARKET_CALENDAR_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\market_calendar\_market_calendar_manifest_v0_1.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\expected_data_calendar")


FAMILY_POLICIES = [
    {
        "dataset_family": "daily_raw",
        "expected_dataset_id": "daily_core_v0_1",
        "expected_source_root": "E:/TSIS/data/ohlcv_daily",
        "expectation_scope": "core_session_presence",
    },
    {
        "dataset_family": "ohlcv_1m_raw",
        "expected_dataset_id": "ohlcv_1m_raw_v0_1",
        "expected_source_root": "E:/TSIS/data/ohlcv_1m",
        "expectation_scope": "core_session_presence",
    },
    {
        "dataset_family": "trades_raw",
        "expected_dataset_id": "trades_core_v0_1",
        "expected_source_root": "E:/TSIS/data/trades_ticks_prod_2005_2026",
        "expectation_scope": "core_session_presence",
    },
    {
        "dataset_family": "quotes_raw",
        "expected_dataset_id": "quotes_core_v0_1",
        "expected_source_root": "E:/TSIS/data/quotes",
        "expectation_scope": "core_session_presence",
    },
]


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
        file_hash = _sha256(path)
        size = path.stat().st_size
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


def _family_values_sql() -> str:
    rows = []
    for item in FAMILY_POLICIES:
        rows.append(
            "('"
            + item["dataset_family"]
            + "','"
            + item["expected_dataset_id"]
            + "','"
            + item["expected_source_root"]
            + "','"
            + item["expectation_scope"]
            + "')"
        )
    return ",".join(rows)


def _dataset_glob(dataset_dir: Path) -> str:
    return _sql_path(dataset_dir / "**" / "*.parquet")


def materialize_expected_data_calendar(
    instrument_master: Path,
    instrument_master_manifest: Path,
    market_calendar: Path,
    market_calendar_manifest: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(instrument_master, "instrument master parquet")
    _require(market_calendar, "market calendar parquet")
    instrument_manifest = _load_manifest(instrument_master_manifest)
    market_manifest = _load_manifest(market_calendar_manifest)

    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / "expected_data_calendar_v0_1"
    summary_path = output_root / "_expected_data_calendar_summary_v0_1.csv"
    manifest_path = output_root / "_expected_data_calendar_manifest_v0_1.json"

    if dataset_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Output exists. Pass --overwrite to replace: {dataset_dir}")
        if dataset_dir.resolve() == output_root.resolve() or "expected_data_calendar" not in str(dataset_dir):
            raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
        shutil.rmtree(dataset_dir)

    build_run_id = datetime.now(timezone.utc).strftime("expected_data_calendar_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()

    con = duckdb.connect()
    families_sql = _family_values_sql()
    source_query = f"""
    with family_policy(dataset_family, expected_dataset_id, expected_source_root, expectation_scope) as (
        values {families_sql}
    ),
    instruments as (
        select
            instrument_id,
            ticker,
            cast(valid_from as date) as valid_from,
            cast(valid_to as date) as valid_to,
            schema_version as instrument_master_schema_version,
            build_run_id as instrument_master_build_run_id
        from read_parquet('{_sql_path(instrument_master)}')
        where is_lt1b_operational = true
    ),
    sessions as (
        select
            cast(session_date as date) as session_date,
            cast(year as integer) as year,
            cast(month as integer) as month,
            calendar,
            timezone,
            schema_version as market_calendar_schema_version,
            build_run_id as market_calendar_build_run_id
        from read_parquet('{_sql_path(market_calendar)}')
        where calendar = 'XNYS'
    )
    select
        fp.dataset_family,
        fp.expected_dataset_id,
        fp.expected_source_root,
        i.instrument_id,
        i.ticker,
        s.session_date,
        true as expected_session,
        'instrument_valid_window_and_xnys_session' as expected_reason,
        fp.expectation_scope,
        s.calendar,
        s.timezone,
        s.year,
        s.month,
        i.valid_from,
        i.valid_to,
        i.instrument_master_schema_version,
        i.instrument_master_build_run_id,
        s.market_calendar_schema_version,
        s.market_calendar_build_run_id,
        '{POLICY_VERSION}' as expectation_policy_version,
        '{build_run_id}' as build_run_id,
        '{SCHEMA_VERSION}' as schema_version,
        '{created_at_utc}' as created_at_utc
    from instruments i
    join sessions s
      on s.session_date between i.valid_from and i.valid_to
    cross join family_policy fp
    """

    con.execute(
        f"""
        copy ({source_query})
        to '{_sql_path(dataset_dir)}'
        (format parquet, compression zstd, partition_by (dataset_family, year))
        """
    )

    dataset_glob = _dataset_glob(dataset_dir)
    validations = con.execute(
        f"""
        with rows as (
            select * from read_parquet('{dataset_glob}', hive_partitioning=true)
        ),
        dupes as (
            select count(*) as duplicate_key_groups
            from (
                select dataset_family, ticker, session_date, count(*) as n
                from rows
                group by 1, 2, 3
                having count(*) > 1
            )
        )
        select
            count(*)::bigint as row_count,
            count(distinct dataset_family)::integer as dataset_family_count,
            count(distinct ticker)::integer as ticker_count,
            count(distinct instrument_id)::integer as instrument_id_count,
            min(session_date)::varchar as first_session,
            max(session_date)::varchar as last_session,
            sum(case when expected_session then 0 else 1 end)::bigint as unexpected_false_count,
            sum(case when session_date < valid_from or session_date > valid_to then 1 else 0 end)::bigint as invalid_window_count,
            (select duplicate_key_groups from dupes)::bigint as duplicate_key_groups
        from rows
        """
    ).fetchdf().iloc[0].to_dict()

    rows_by_family = con.execute(
        f"""
        select dataset_family, count(*)::bigint as rows, count(distinct ticker)::integer as tickers
        from read_parquet('{dataset_glob}', hive_partitioning=true)
        group by dataset_family
        order by dataset_family
        """
    ).fetchdf()
    validations["rows_by_family"] = {
        row["dataset_family"]: {"rows": int(row["rows"]), "tickers": int(row["tickers"])}
        for _, row in rows_by_family.iterrows()
    }
    validations = {
        key: int(value) if hasattr(value, "item") and str(getattr(value, "dtype", "")).startswith("int") else value
        for key, value in validations.items()
    }
    validations["hard_fail_count"] = int(
        validations["unexpected_false_count"]
        + validations["invalid_window_count"]
        + validations["duplicate_key_groups"]
        + (1 if validations["row_count"] == 0 else 0)
        + (1 if validations["dataset_family_count"] != len(FAMILY_POLICIES) else 0)
    )

    if validations["hard_fail_count"] > 0:
        raise RuntimeError(f"Hard validation failed: {validations}")

    tree = _sha256_tree(dataset_dir)
    summary_rows = [
        {"metric": "rows", "value": validations["row_count"]},
        {"metric": "dataset_families", "value": validations["dataset_family_count"]},
        {"metric": "tickers", "value": validations["ticker_count"]},
        {"metric": "first_session", "value": validations["first_session"]},
        {"metric": "last_session", "value": validations["last_session"]},
        {"metric": "duplicate_key_groups", "value": validations["duplicate_key_groups"]},
        {"metric": "invalid_window_count", "value": validations["invalid_window_count"]},
        {"metric": "hard_fail_count", "value": validations["hard_fail_count"]},
        {"metric": "parquet_file_count", "value": tree["parquet_file_count"]},
        {"metric": "tree_sha256", "value": tree["tree_sha256"]},
    ]
    for family, payload in validations["rows_by_family"].items():
        summary_rows.append({"metric": f"rows_{family}", "value": payload["rows"]})
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)

    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "expectation_policy_version": POLICY_VERSION,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": str(dataset_dir),
        "summary_path": str(summary_path),
        "output_tree": tree,
        "source_instrument_master": str(instrument_master),
        "source_instrument_master_sha256": _sha256(instrument_master),
        "source_instrument_master_manifest": str(instrument_master_manifest),
        "source_instrument_master_build_run_id": instrument_manifest.get("build_run_id"),
        "source_market_calendar": str(market_calendar),
        "source_market_calendar_sha256": _sha256(market_calendar),
        "source_market_calendar_manifest": str(market_calendar_manifest),
        "source_market_calendar_build_run_id": market_manifest.get("build_run_id"),
        "family_policies": FAMILY_POLICIES,
        "validations": validations,
        "contracts": {
            "dataset_contract": "01_foundations/contract_registry/dataset_contracts/expected_data_calendar_dataset_contract_v0_1.md",
            "schema_contract": "01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md",
            "consumption_policy": "01_foundations/data_consumption_policies/expected_data_calendar_consumption_policy.md",
            "registry_entry": "01_foundations/dataset_registry/outputs/expected_data_calendar_registry_entry.yaml",
            "validators": "01_foundations/validators/outputs/expected_data_calendar_validators.md",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa expected_data_calendar_v0_1.")
    ap.add_argument("--instrument-master", default=str(DEFAULT_INSTRUMENT_MASTER))
    ap.add_argument("--instrument-master-manifest", default=str(DEFAULT_INSTRUMENT_MASTER_MANIFEST))
    ap.add_argument("--market-calendar", default=str(DEFAULT_MARKET_CALENDAR))
    ap.add_argument("--market-calendar-manifest", default=str(DEFAULT_MARKET_CALENDAR_MANIFEST))
    ap.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    materialize_expected_data_calendar(
        instrument_master=Path(args.instrument_master),
        instrument_master_manifest=Path(args.instrument_master_manifest),
        market_calendar=Path(args.market_calendar),
        market_calendar_manifest=Path(args.market_calendar_manifest),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

