from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api import types as pdt


DATASET_ID = "master_intraday_bar_table_v0_2_candidate_quote_guarded"
DEFAULT_PHYSICAL_DATASET_ID = "master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped"
PHYSICAL_DATASET_ID = DEFAULT_PHYSICAL_DATASET_ID
SCHEMA_VERSION = "master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped_v0_1"
QUALITY_POLICY_VERSION = "master_intraday_quote_guarded_candidate_scoped_policy_v0_1"

DEFAULT_RAW_ROOT = Path("E:/TSIS/data/ohlcv_1m")
DEFAULT_SHARD_INDEX = Path(
    "C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/"
    "quote_guarded_lt1b_consolidation_manual_20260703_094500/lt1b_repair_shard_index.csv"
)
DEFAULT_OUTPUT_ROOT = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_scoped_v0_1"
)
DEFAULT_REPAIR_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet"
)
DEFAULT_REPAIR_SUMMARY = Path(
    "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_summary.json"
)
DEFAULT_CONSOLIDATION_SUMMARY = Path(
    "C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/"
    "quote_guarded_lt1b_consolidation_manual_20260703_094500/consolidation_summary.json"
)

RAW_COLUMNS = ["ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v", "vw", "n", "t"]
REPAIR_REQUIRED_COLUMNS = {
    "quote_guarded_view",
    "ticker",
    "ts_utc",
    "session_date",
    "year",
    "month",
    "repair_state",
    "repair_reason",
    "quote_guarded_repair_applied",
    "o_raw",
    "h_raw",
    "l_raw",
    "c_raw",
    "o_qg",
    "h_qg",
    "l_qg",
    "c_qg",
    "vw",
    "v",
    "n",
    "vw_quote_guarded_status",
    "quote_bid_floor",
    "quote_ask_cap",
    "quote_count",
    "source_ohlcv_path",
    "source_quotes_path",
    "run_root",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "master_intraday_quote_guarded_candidate_scoped_" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_id(*parts: Any, length: int = 20) -> str:
    payload = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _iso(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bool_series(values: pd.Series) -> pd.Series:
    if pdt.is_bool_dtype(values):
        return values.fillna(False).astype(bool)
    return values.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def _close_enough(a: pd.Series, b: pd.Series, tolerance: float = 1e-6) -> pd.Series:
    return (a.astype(float) - b.astype(float)).abs() <= tolerance


def _parse_ticker_month(value: str) -> tuple[str, int, int]:
    try:
        ticker, ym = value.split(":", 1)
        year_s, month_s = ym.split("-", 1)
        ticker = ticker.upper().strip()
        year = int(year_s)
        month = int(month_s)
    except Exception as exc:  # noqa: BLE001
        raise argparse.ArgumentTypeError("ticker-month must look like TICKER:YYYY-MM") from exc
    if not ticker or not (1 <= month <= 12):
        raise argparse.ArgumentTypeError("invalid ticker-month")
    return ticker, year, month


def _raw_path(raw_root: Path, ticker: str, year: int, month: int) -> Path:
    return raw_root / f"ticker={ticker}" / f"year={year}" / f"month={month:02d}" / f"minute_aggs_{ticker}_{year}_{month:02d}.parquet"


def _find_shards(shard_index: Path, scopes: list[tuple[str, int, int]]) -> dict[tuple[str, int, int], Path]:
    targets = {(ticker, str(year), str(month)) for ticker, year, month in scopes}
    found: dict[tuple[str, int, int], Path] = {}
    with shard_index.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = (row["ticker"].upper().strip(), row["year"], row["month"])
            if key in targets:
                found[(key[0], int(key[1]), int(key[2]))] = Path(row["repair_shard_path"])
                if len(found) == len(targets):
                    break
    missing = sorted(set(scopes) - set(found))
    if missing:
        raise FileNotFoundError(f"missing repair shard entries for {missing}")
    return found


def _read_scope(raw_root: Path, shard_path: Path, ticker: str, year: int, month: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_file = _raw_path(raw_root, ticker, year, month)
    if not raw_file.exists():
        raise FileNotFoundError(f"raw parquet not found: {raw_file}")
    if not shard_path.exists():
        raise FileNotFoundError(f"repair shard not found: {shard_path}")
    raw = pd.read_parquet(raw_file, columns=RAW_COLUMNS)
    raw["ticker"] = raw["ticker"].astype(str).str.upper().str.strip()
    raw = raw[(raw["ticker"] == ticker) & (raw["year"].astype(int) == year) & (raw["month"].astype(int) == month)].copy()
    raw["ts_utc_norm"] = pd.to_datetime(raw["ts_utc"], utc=True)
    raw["source_ohlcv_path"] = str(raw_file)

    repair = pd.read_parquet(shard_path)
    missing_cols = sorted(REPAIR_REQUIRED_COLUMNS - set(repair.columns))
    if missing_cols:
        raise ValueError(f"repair shard missing required columns {missing_cols}: {shard_path}")
    repair["ticker"] = repair["ticker"].astype(str).str.upper().str.strip()
    repair = repair[(repair["ticker"] == ticker) & (repair["year"].astype(int) == year) & (repair["month"].astype(int) == month)].copy()
    repair["ts_utc_norm"] = pd.to_datetime(repair["ts_utc"], utc=True)
    repair["quote_guarded_repair_applied_bool"] = _bool_series(repair["quote_guarded_repair_applied"])
    repair["source_repair_shard_path"] = str(shard_path)
    return raw, repair


def _merged_scope(raw: pd.DataFrame, repair: pd.DataFrame) -> pd.DataFrame:
    repair_cols = [
        "ticker",
        "ts_utc_norm",
        "repair_state",
        "repair_reason",
        "quote_guarded_repair_applied_bool",
        "o_raw",
        "h_raw",
        "l_raw",
        "c_raw",
        "o_qg",
        "h_qg",
        "l_qg",
        "c_qg",
        "vw_quote_guarded_status",
        "quote_bid_floor",
        "quote_ask_cap",
        "quote_count",
        "source_quotes_path",
        "run_root",
        "source_repair_shard_path",
    ]
    merged = raw.merge(repair[repair_cols], on=["ticker", "ts_utc_norm"], how="left", validate="one_to_one")
    in_manifest = merged["repair_state"].notna()
    merged["repair_manifest_row_present"] = in_manifest
    merged["quote_guarded_repair_applied_bool"] = merged["quote_guarded_repair_applied_bool"].map(lambda value: bool(value) if pd.notna(value) else False)
    for col, raw_col in [("o_raw", "o"), ("h_raw", "h"), ("l_raw", "l"), ("c_raw", "c")]:
        merged[col] = merged[col].fillna(merged[raw_col])
    for col, raw_col in [("o_qg", "o"), ("h_qg", "h"), ("l_qg", "l"), ("c_qg", "c")]:
        merged[col] = merged[col].fillna(merged[raw_col])
    merged["repair_state"] = merged["repair_state"].fillna("not_in_repair_manifest")
    merged["repair_reason"] = merged["repair_reason"].fillna("not_applicable")
    merged["vw_quote_guarded_status"] = merged["vw_quote_guarded_status"].fillna("usable_observed_raw_vwap")
    merged["raw_ohlc_matches_manifest"] = (~in_manifest) | (
        _close_enough(merged["o"], merged["o_raw"])
        & _close_enough(merged["h"], merged["h_raw"])
        & _close_enough(merged["l"], merged["l_raw"])
        & _close_enough(merged["c"], merged["c_raw"])
    )
    merged["manifest_qg_ohlc_differs_from_raw"] = (
        ~_close_enough(merged["o_raw"], merged["o_qg"])
        | ~_close_enough(merged["h_raw"], merged["h_qg"])
        | ~_close_enough(merged["l_raw"], merged["l_qg"])
        | ~_close_enough(merged["c_raw"], merged["c_qg"])
    )
    for qg_col, raw_col in [("o_qg", "o"), ("h_qg", "h"), ("l_qg", "l"), ("c_qg", "c")]:
        effective_col = "effective_" + qg_col
        merged[effective_col] = merged[raw_col]
        mask = merged["quote_guarded_repair_applied_bool"]
        merged.loc[mask, effective_col] = merged.loc[mask, qg_col]
    merged["manifest_qg_diff_not_applied"] = (
        merged["manifest_qg_ohlc_differs_from_raw"] & ~merged["quote_guarded_repair_applied_bool"]
    )
    merged["qg_ohlc_changed"] = (
        ~_close_enough(merged["o"], merged["effective_o_qg"])
        | ~_close_enough(merged["h"], merged["effective_h_qg"])
        | ~_close_enough(merged["l"], merged["effective_l_qg"])
        | ~_close_enough(merged["c"], merged["effective_c_qg"])
    )
    return merged


def _build_rows(merged: pd.DataFrame, physical_dataset_id: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in merged.itertuples(index=False):
        for price_view in ["1m_raw", "1m_quote_guarded_raw"]:
            is_qg = price_view == "1m_quote_guarded_raw"
            open_value = row.effective_o_qg if is_qg else row.o
            high_value = row.effective_h_qg if is_qg else row.h
            low_value = row.effective_l_qg if is_qg else row.l
            close_value = row.effective_c_qg if is_qg else row.c
            vwap_blocked = is_qg and "vw_invalid" in str(row.vw_quote_guarded_status).lower()
            rows.append(
                {
                    "master_intraday_bar_id": "master_intraday_qg_scoped_"
                    + _stable_id(DATASET_ID, row.ticker, _iso(row.ts_utc_norm), price_view),
                    "dataset_id": DATASET_ID,
                    "physical_dataset_id": physical_dataset_id,
                    "ticker": row.ticker,
                    "instrument_id": None,
                    "ts_utc": _iso(row.ts_utc_norm),
                    "session_date": str(row.date),
                    "year": int(row.year),
                    "month": int(row.month),
                    "bar_size": "1m",
                    "price_view": price_view,
                    "open": float(open_value),
                    "high": float(high_value),
                    "low": float(low_value),
                    "close": float(close_value),
                    "volume": float(row.v),
                    "vwap": None if vwap_blocked else (float(row.vw) if pd.notna(row.vw) else None),
                    "transaction_count": int(row.n) if pd.notna(row.n) else None,
                    "source_raw_open": float(row.o),
                    "source_raw_high": float(row.h),
                    "source_raw_low": float(row.l),
                    "source_raw_close": float(row.c),
                    "source_raw_vwap": float(row.vw) if pd.notna(row.vw) else None,
                    "source_raw_volume": float(row.v),
                    "source_raw_transaction_count": int(row.n) if pd.notna(row.n) else None,
                    "quote_guarded_view": "ohlcv_1m_quote_guarded_v0_1" if is_qg else "raw_ohlcv_1m",
                    "quote_guarded_repair_applied": bool(row.quote_guarded_repair_applied_bool) if is_qg else False,
                    "repair_manifest_row_present": bool(row.repair_manifest_row_present),
                    "repair_state": row.repair_state,
                    "repair_reason": row.repair_reason,
                    "vw_quote_guarded_status": row.vw_quote_guarded_status,
                    "quote_bid_floor": None if pd.isna(row.quote_bid_floor) else float(row.quote_bid_floor),
                    "quote_ask_cap": None if pd.isna(row.quote_ask_cap) else float(row.quote_ask_cap),
                    "quote_count": None if pd.isna(row.quote_count) else int(row.quote_count),
                    "source_quote_guarded_repair_manifest": str(DEFAULT_REPAIR_MANIFEST),
                    "source_repair_shard_path": row.source_repair_shard_path if isinstance(row.source_repair_shard_path, str) else None,
                    "source_quote_guarded_run_id": Path(str(row.run_root)).name if isinstance(row.run_root, str) else None,
                    "source_quotes_root": "D:/quotes",
                    "source_quotes_root_state": "provisional_d_legacy_recovery_root_pending_e_parity",
                    "source_ohlcv_path": row.source_ohlcv_path,
                    "source_quotes_path": row.source_quotes_path if isinstance(row.source_quotes_path, str) else None,
                    "raw_ohlc_matches_manifest": bool(row.raw_ohlc_matches_manifest),
                    "qg_ohlc_changed": bool(row.qg_ohlc_changed),
                    "manifest_qg_ohlc_differs_from_raw": bool(row.manifest_qg_ohlc_differs_from_raw),
                    "manifest_qg_diff_not_applied": bool(row.manifest_qg_diff_not_applied),
                    "vwap_consumption_state": "blocked_by_quote_guarded_status" if vwap_blocked else "usable_observed_raw_vwap",
                    "event_research_bar_candidate": True,
                    "backtest_core_bar_candidate": False,
                    "valid_for_ml_feature_candidate": False,
                    "valid_for_rl_state_component_candidate": False,
                    "full_universe_claim": False,
                    "execution_truth": False,
                    "schema_version": SCHEMA_VERSION,
                    "quality_policy_version": QUALITY_POLICY_VERSION,
                }
            )
    return pd.DataFrame(rows)


def build(args: argparse.Namespace) -> dict[str, Any]:
    scopes = args.ticker_month
    if not scopes:
        raise ValueError("at least one --ticker-month is required")
    output_root = args.output_root
    physical_dataset_id = args.physical_dataset_id
    dataset_dir = output_root / physical_dataset_id
    if dataset_dir.exists():
        if not args.overwrite:
            raise FileExistsError(f"output exists; pass --overwrite: {dataset_dir}")
        resolved = dataset_dir.resolve()
        allowed = output_root.resolve()
        if allowed not in resolved.parents and resolved != allowed:
            raise RuntimeError(f"refusing to delete outside output root: {resolved}")
        shutil.rmtree(dataset_dir)
    dataset_dir.mkdir(parents=True, exist_ok=True)

    shard_paths = _find_shards(args.shard_index, scopes)
    merged_parts: list[pd.DataFrame] = []
    source_raw_files: list[str] = []
    source_shards: list[str] = []
    scope_rows: list[dict[str, Any]] = []
    for ticker, year, month in scopes:
        raw, repair = _read_scope(args.raw_root, shard_paths[(ticker, year, month)], ticker, year, month)
        merged = _merged_scope(raw, repair)
        merged_parts.append(merged)
        raw_path = _raw_path(args.raw_root, ticker, year, month)
        source_raw_files.append(str(raw_path))
        source_shards.append(str(shard_paths[(ticker, year, month)]))
        scope_rows.append(
            {
                "ticker": ticker,
                "year": year,
                "month": month,
                "raw_rows": int(len(raw)),
                "repair_shard_rows": int(len(repair)),
                "repair_applied_rows": int(repair["quote_guarded_repair_applied_bool"].sum()),
                "qg_ohlc_changed_rows": int(merged["qg_ohlc_changed"].sum()),
                "manifest_qg_diff_not_applied_rows": int(merged["manifest_qg_diff_not_applied"].sum()),
            }
        )
    merged_all = pd.concat(merged_parts, ignore_index=True)
    output = _build_rows(merged_all, physical_dataset_id)
    output_path = dataset_dir / "data.parquet"
    output.to_parquet(output_path, index=False)

    price_view_counts = {str(k): int(v) for k, v in output["price_view"].value_counts().sort_index().items()}
    validations = {
        "scope_count": len(scopes),
        "source_raw_file_count": len(set(source_raw_files)),
        "source_repair_shard_count": len(set(source_shards)),
        "raw_rows": int(len(merged_all)),
        "repair_manifest_rows_in_scope": int(merged_all["repair_manifest_row_present"].sum()),
        "raw_ohlc_match_rows": int(merged_all["raw_ohlc_matches_manifest"].sum()),
        "raw_ohlc_mismatch_rows": int((~merged_all["raw_ohlc_matches_manifest"]).sum()),
        "quote_guarded_repair_applied_rows": int(merged_all["quote_guarded_repair_applied_bool"].sum()),
        "qg_ohlc_changed_rows": int(merged_all["qg_ohlc_changed"].sum()),
        "manifest_qg_diff_not_applied_rows": int(merged_all["manifest_qg_diff_not_applied"].sum()),
        "output_rows": int(len(output)),
        "price_view_counts": price_view_counts,
        "full_universe_claim_rows": int(output["full_universe_claim"].sum()),
        "ml_candidate_rows": int(output["valid_for_ml_feature_candidate"].sum()),
        "rl_candidate_rows": int(output["valid_for_rl_state_component_candidate"].sum()),
    }
    hard_failures: list[str] = []
    if validations["raw_rows"] <= 0:
        hard_failures.append("no_raw_rows")
    if validations["repair_manifest_rows_in_scope"] <= 0:
        hard_failures.append("no_repair_manifest_rows_in_scope")
    if validations["raw_ohlc_mismatch_rows"]:
        hard_failures.append("raw_ohlc_mismatch_rows")
    if validations["quote_guarded_repair_applied_rows"] <= 0:
        hard_failures.append("no_quote_guarded_repair_applied_rows")
    if validations["qg_ohlc_changed_rows"] <= 0:
        hard_failures.append("no_qg_ohlc_changed_rows")
    if validations["qg_ohlc_changed_rows"] > validations["quote_guarded_repair_applied_rows"]:
        hard_failures.append("qg_ohlc_changed_exceeds_repair_applied_rows")
    if validations["output_rows"] != validations["raw_rows"] * 2:
        hard_failures.append("output_rows_not_two_price_views")
    if validations["price_view_counts"] != {"1m_quote_guarded_raw": validations["raw_rows"], "1m_raw": validations["raw_rows"]}:
        hard_failures.append("price_view_counts_unexpected")
    if validations["full_universe_claim_rows"]:
        hard_failures.append("full_universe_claim_rows_present")
    if validations["ml_candidate_rows"] or validations["rl_candidate_rows"]:
        hard_failures.append("ml_or_rl_candidate_rows_present")
    validations["validator_status"] = "passed" if not hard_failures else "failed"
    validations["validator_hard_fail_count"] = len(hard_failures)
    validations["validator_hard_failures"] = hard_failures

    manifest_path = output_root / f"_{physical_dataset_id}_manifest.json"
    manifest = {
        "dataset_id": DATASET_ID,
        "physical_dataset_id": physical_dataset_id,
        "status": "scoped_candidate_materialized_not_official",
        "created_at_utc": args.created_at_utc or _utc_now(),
        "build_run_id": args.run_id or _run_id(),
        "materialization_scope": "quote_guarded_lt1b_scoped_ticker_month_candidate",
        "scope": scope_rows,
        "output_path": output_path.as_posix(),
        "output_sha256": _sha256_file(output_path),
        "source_raw_root": args.raw_root.as_posix(),
        "source_raw_files": source_raw_files,
        "source_shard_index": args.shard_index.as_posix(),
        "source_shard_index_sha256": _sha256_file(args.shard_index),
        "source_repair_shards": source_shards,
        "source_quote_guarded_repair_manifest": DEFAULT_REPAIR_MANIFEST.as_posix(),
        "source_quote_guarded_repair_summary": DEFAULT_REPAIR_SUMMARY.as_posix(),
        "source_consolidation_summary": DEFAULT_CONSOLIDATION_SUMMARY.as_posix(),
        "full_universe_claim": False,
        "official_dataset_created": False,
        "writes_e_root_target": output_path.as_posix().startswith("E:/TSIS/data/"),
        "valid_for_ml_feature_candidate": False,
        "valid_for_rl_state_component_candidate": False,
        "alphaevolve_evaluator_enabled": False,
        "not_allowed_actions": [
            "overwrite_raw_ohlcv_1m",
            "write_into_master_intraday_bar_table_v0_1",
            "claim_full_universe_state_table",
            "enable_ml_rl_alphaevolve",
        ],
        "validations": validations,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    if validations["validator_status"] != "passed":
        raise RuntimeError(f"scoped candidate validation failed: {validations}")
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize a scoped ticker-month candidate for master_intraday_bar_table_v0_2 quote-guarded overlay."
    )
    parser.add_argument("--ticker-month", action="append", type=_parse_ticker_month, default=[])
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--shard-index", type=Path, default=DEFAULT_SHARD_INDEX)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--physical-dataset-id", default=DEFAULT_PHYSICAL_DATASET_ID)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--created-at-utc", default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    manifest = build(args)
    print(json.dumps(manifest["validations"], indent=2))
    print(f"Wrote {manifest['output_path']}")


if __name__ == "__main__":
    main()
