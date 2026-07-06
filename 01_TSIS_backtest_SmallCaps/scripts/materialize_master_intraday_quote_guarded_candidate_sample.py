from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api import types as pdt


DATASET_ID = "master_intraday_bar_table_v0_2_candidate_quote_guarded"
PHYSICAL_DATASET_ID = "master_intraday_bar_table_v0_2_candidate_quote_guarded_controlled_sample"
SCHEMA_VERSION = "master_intraday_bar_table_v0_2_candidate_quote_guarded_sample_v0_1"
QUALITY_POLICY_VERSION = "master_intraday_quote_guarded_candidate_sample_policy_v0_1"

DEFAULT_REPAIR_SAMPLE = Path(
    "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_sample.csv"
)
DEFAULT_OUTPUT_ROOT = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/master_intraday_quote_guarded_candidate_sample_v0_1"
)

RAW_COLUMNS = ["ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v", "vw", "n", "t"]
REPAIR_NUMERIC_COLUMNS = [
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
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "master_intraday_quote_guarded_candidate_sample_" + datetime.now(timezone.utc).strftime(
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


def _bool_series(values: pd.Series) -> pd.Series:
    if pdt.is_bool_dtype(values):
        return values.fillna(False).astype(bool)
    return values.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def _iso(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_repair_sample(path: Path, max_applied: int, max_unapplied: int) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"repair sample not found: {path}")
    df = pd.read_csv(path)
    required = {
        "ticker",
        "ts_utc",
        "session_date",
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
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"missing required repair sample columns: {missing}")
    for col in REPAIR_NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["quote_guarded_repair_applied_bool"] = _bool_series(df["quote_guarded_repair_applied"])
    df["ts_utc_norm"] = pd.to_datetime(df["ts_utc"], utc=True)
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    applied = df[df["quote_guarded_repair_applied_bool"]].head(max_applied)
    unapplied = df[~df["quote_guarded_repair_applied_bool"]].head(max_unapplied)
    selected = pd.concat([applied, unapplied], ignore_index=True)
    if selected.empty:
        raise ValueError("repair sample selection is empty")
    return selected


def _read_raw_rows(sample: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for source_path, group in sample.groupby("source_ohlcv_path"):
        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"source raw parquet not found: {path}")
        raw = pd.read_parquet(path, columns=RAW_COLUMNS)
        raw["ticker"] = raw["ticker"].astype(str).str.upper().str.strip()
        raw["ts_utc_norm"] = pd.to_datetime(raw["ts_utc"], utc=True)
        wanted = group[["ticker", "ts_utc_norm"]].drop_duplicates()
        merged = raw.merge(wanted, on=["ticker", "ts_utc_norm"], how="inner")
        merged["source_ohlcv_path"] = str(path)
        frames.append(merged)
    if not frames:
        raise ValueError("no raw frames read")
    return pd.concat(frames, ignore_index=True)


def _close_enough(a: pd.Series, b: pd.Series, tolerance: float = 1e-6) -> pd.Series:
    return (a.astype(float) - b.astype(float)).abs() <= tolerance


def _build_output(sample: pd.DataFrame, raw_rows: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    merged = sample.merge(
        raw_rows,
        on=["ticker", "ts_utc_norm", "source_ohlcv_path"],
        how="left",
        suffixes=("", "_raw_file"),
        validate="one_to_one",
    )
    merged["raw_row_found"] = merged["o"].notna()
    raw_match = (
        merged["raw_row_found"]
        & _close_enough(merged["o"], merged["o_raw"])
        & _close_enough(merged["h"], merged["h_raw"])
        & _close_enough(merged["l"], merged["l_raw"])
        & _close_enough(merged["c"], merged["c_raw"])
    )
    merged["raw_ohlc_matches_manifest"] = raw_match
    qg_changed = (
        ~_close_enough(merged["o_raw"], merged["o_qg"])
        | ~_close_enough(merged["h_raw"], merged["h_qg"])
        | ~_close_enough(merged["l_raw"], merged["l_qg"])
        | ~_close_enough(merged["c_raw"], merged["c_qg"])
    )
    merged["qg_ohlc_changed"] = qg_changed

    rows: list[dict[str, Any]] = []
    for row in merged.itertuples(index=False):
        for price_view in ["1m_raw", "1m_quote_guarded_raw"]:
            is_qg = price_view == "1m_quote_guarded_raw"
            open_value = row.o_qg if is_qg else row.o_raw
            high_value = row.h_qg if is_qg else row.h_raw
            low_value = row.l_qg if is_qg else row.l_raw
            close_value = row.c_qg if is_qg else row.c_raw
            repair_applied = bool(row.quote_guarded_repair_applied_bool) if is_qg else False
            vwap_blocked = "vw_invalid" in str(row.vw_quote_guarded_status).lower()
            rows.append(
                {
                    "master_intraday_bar_id": "master_intraday_qg_sample_"
                    + _stable_id(DATASET_ID, row.ticker, _iso(row.ts_utc_norm), price_view),
                    "dataset_id": DATASET_ID,
                    "physical_dataset_id": PHYSICAL_DATASET_ID,
                    "ticker": row.ticker,
                    "instrument_id": None,
                    "ts_utc": _iso(row.ts_utc_norm),
                    "session_date": str(row.session_date),
                    "year": int(row.year),
                    "month": int(row.month),
                    "bar_size": "1m",
                    "price_view": price_view,
                    "open": float(open_value),
                    "high": float(high_value),
                    "low": float(low_value),
                    "close": float(close_value),
                    "volume": float(row.v),
                    "vwap": None if vwap_blocked else float(row.vw),
                    "transaction_count": int(row.n) if pd.notna(row.n) else None,
                    "source_raw_open": float(row.o_raw),
                    "source_raw_high": float(row.h_raw),
                    "source_raw_low": float(row.l_raw),
                    "source_raw_close": float(row.c_raw),
                    "source_raw_vwap": float(row.vw) if pd.notna(row.vw) else None,
                    "source_raw_volume": float(row.v),
                    "source_raw_transaction_count": int(row.n) if pd.notna(row.n) else None,
                    "quote_guarded_view": "ohlcv_1m_quote_guarded_v0_1" if is_qg else "raw_ohlcv_1m",
                    "quote_guarded_repair_applied": repair_applied,
                    "repair_state": row.repair_state,
                    "repair_reason": row.repair_reason,
                    "vw_quote_guarded_status": row.vw_quote_guarded_status,
                    "quote_bid_floor": float(row.quote_bid_floor) if pd.notna(row.quote_bid_floor) else None,
                    "quote_ask_cap": float(row.quote_ask_cap) if pd.notna(row.quote_ask_cap) else None,
                    "quote_count": int(row.quote_count) if pd.notna(row.quote_count) else None,
                    "source_quote_guarded_repair_manifest": str(DEFAULT_REPAIR_SAMPLE).replace("_sample.csv", ".parquet"),
                    "source_quote_guarded_run_id": Path(str(row.run_root)).name,
                    "source_quotes_root": "D:/quotes",
                    "source_quotes_root_state": "provisional_d_legacy_recovery_root_pending_e_parity",
                    "source_ohlcv_path": row.source_ohlcv_path,
                    "source_quotes_path": row.source_quotes_path,
                    "raw_row_found": bool(row.raw_row_found),
                    "raw_ohlc_matches_manifest": bool(row.raw_ohlc_matches_manifest),
                    "qg_ohlc_changed": bool(row.qg_ohlc_changed),
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
    output = pd.DataFrame(rows)
    validations = {
        "source_sample_rows": int(len(sample)),
        "raw_rows_found": int(merged["raw_row_found"].sum()),
        "raw_rows_missing": int((~merged["raw_row_found"]).sum()),
        "raw_ohlc_match_rows": int(merged["raw_ohlc_matches_manifest"].sum()),
        "raw_ohlc_mismatch_rows": int((~merged["raw_ohlc_matches_manifest"]).sum()),
        "quote_guarded_repair_applied_source_rows": int(merged["quote_guarded_repair_applied_bool"].sum()),
        "qg_ohlc_changed_source_rows": int(merged["qg_ohlc_changed"].sum()),
        "output_rows": int(len(output)),
        "price_view_counts": {str(k): int(v) for k, v in output["price_view"].value_counts().sort_index().items()},
        "full_universe_claim_rows": int(output["full_universe_claim"].sum()),
        "ml_candidate_rows": int(output["valid_for_ml_feature_candidate"].sum()),
        "rl_candidate_rows": int(output["valid_for_rl_state_component_candidate"].sum()),
    }
    hard_failures: list[str] = []
    if validations["raw_rows_missing"]:
        hard_failures.append("raw_rows_missing")
    if validations["raw_ohlc_mismatch_rows"]:
        hard_failures.append("raw_ohlc_mismatch_rows")
    if validations["quote_guarded_repair_applied_source_rows"] == 0:
        hard_failures.append("no_quote_guarded_repair_applied_rows_selected")
    if validations["qg_ohlc_changed_source_rows"] == 0:
        hard_failures.append("no_qg_ohlc_changed_rows_selected")
    if validations["price_view_counts"] != {"1m_quote_guarded_raw": len(sample), "1m_raw": len(sample)}:
        hard_failures.append("price_view_counts_unexpected")
    if validations["full_universe_claim_rows"]:
        hard_failures.append("full_universe_claim_rows_present")
    if validations["ml_candidate_rows"] or validations["rl_candidate_rows"]:
        hard_failures.append("ml_or_rl_candidate_rows_present")

    validations["validator_status"] = "passed" if not hard_failures else "failed"
    validations["validator_hard_fail_count"] = len(hard_failures)
    validations["validator_hard_failures"] = hard_failures
    return output, validations


def build(args: argparse.Namespace) -> dict[str, Any]:
    output_root = args.output_root
    dataset_dir = output_root / PHYSICAL_DATASET_ID
    if dataset_dir.exists():
        if not args.overwrite:
            raise FileExistsError(f"output exists; pass --overwrite: {dataset_dir}")
        resolved = dataset_dir.resolve()
        allowed = output_root.resolve()
        if allowed not in resolved.parents and resolved != allowed:
            raise RuntimeError(f"refusing to delete outside output root: {resolved}")
        shutil.rmtree(dataset_dir)
    dataset_dir.mkdir(parents=True, exist_ok=True)

    created_at = args.created_at_utc or _utc_now()
    run_id = args.run_id or _run_id()
    sample = _read_repair_sample(args.repair_sample, args.max_applied_rows, args.max_unapplied_rows)
    raw_rows = _read_raw_rows(sample)
    output, validations = _build_output(sample, raw_rows)
    output_path = dataset_dir / "data.parquet"
    output.to_parquet(output_path, index=False)
    manifest_path = output_root / "_master_intraday_bar_table_v0_2_candidate_quote_guarded_controlled_sample_manifest.json"
    manifest = {
        "dataset_id": DATASET_ID,
        "physical_dataset_id": PHYSICAL_DATASET_ID,
        "status": "controlled_sample_materialized_not_official",
        "created_at_utc": created_at,
        "build_run_id": run_id,
        "materialization_scope": "quote_guarded_lt1b_controlled_sample",
        "output_path": output_path.as_posix(),
        "output_sha256": _sha256_file(output_path),
        "source_repair_sample": args.repair_sample.as_posix(),
        "source_repair_sample_sha256": _sha256_file(args.repair_sample),
        "source_raw_file_count": int(sample["source_ohlcv_path"].nunique()),
        "source_raw_files": sorted(sample["source_ohlcv_path"].unique().tolist()),
        "full_universe_claim": False,
        "official_dataset_created": False,
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
        raise RuntimeError(f"controlled sample validation failed: {validations}")
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize a controlled sample for master_intraday_bar_table_v0_2 quote-guarded overlay."
    )
    parser.add_argument("--repair-sample", type=Path, default=DEFAULT_REPAIR_SAMPLE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--max-applied-rows", type=int, default=20)
    parser.add_argument("--max-unapplied-rows", type=int, default=10)
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
