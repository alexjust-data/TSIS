from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DATASET_ID = "microstructure_features_table_v0_1"
SCHEMA_VERSION = "microstructure_features_table_v0_1"
QUALITY_POLICY_VERSION = "microstructure_features_table_policy_v0_1"
MATERIALIZATION_SCOPE = "seed_event_window_smoke"

MODULE_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_WINDOWS_CSV = MODULE_ROOT / "configs" / "data_foundation_outputs" / "microstructure_features_seed_windows_v0_1.csv"
DEFAULT_QUOTES_ROOT = Path(r"D:\quotes")
DEFAULT_FUTURE_OFFICIAL_QUOTES_ROOT = Path(r"E:\TSIS\data\quotes")
DEFAULT_QUOTES_STAGING_ROOT = Path(r"E:\TSIS\data\quotes_")
DEFAULT_TRADES_ROOT = Path(r"E:\TSIS\data\trades_ticks_prod_2005_2026")
DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)
DEFAULT_INSTRUMENT_MASTER_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\_instrument_master_manifest_v0_1.json"
)
DEFAULT_DATASET_CERTIFICATION_MATRIX = Path(
    r"E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\dataset_certification_matrix_v0_1.parquet"
)
DEFAULT_DATASET_CERTIFICATION_MATRIX_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\_dataset_certification_matrix_manifest_v0_1.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\microstructure_features_table")


def _path_for_json(path: Path | str | None) -> str | None:
    if path is None:
        return None
    return str(path).replace("\\", "/")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_parquet_tree(root: Path) -> dict[str, Any]:
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


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_remove_dataset_dir(dataset_dir: Path, output_root: Path) -> None:
    resolved_dataset = dataset_dir.resolve()
    resolved_root = output_root.resolve()
    if resolved_dataset == resolved_root:
        raise RuntimeError(f"Refusing to delete output root: {dataset_dir}")
    if "microstructure_features_table" not in str(resolved_dataset):
        raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
    shutil.rmtree(dataset_dir)


def _pct(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return float("nan")
    return float(numerator) / float(denominator) * 100.0


def _iso(ts: pd.Timestamp | None) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.Timestamp(ts).isoformat()


def _event_id(*parts: object) -> str:
    text = "|".join(str(part) for part in parts)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _locate_quotes_file(root: Path, ticker: str, session_date: pd.Timestamp) -> Path:
    return (
        root
        / ticker
        / f"year={session_date.year:04d}"
        / f"month={session_date.month:02d}"
        / f"day={session_date.day:02d}"
        / "quotes.parquet"
    )


def _locate_trades_file(root: Path, ticker: str, session_date: pd.Timestamp) -> Path:
    day = session_date.strftime("%Y-%m-%d")
    return (
        root
        / ticker
        / f"year={session_date.year:04d}"
        / f"month={session_date.month:02d}"
        / f"day={day}"
        / "market.parquet"
    )


def _read_windows(path: Path) -> pd.DataFrame:
    _require(path, "event windows csv")
    windows = pd.read_csv(path)
    required = {
        "event_window_id",
        "ticker",
        "session_date",
        "window_start_utc",
        "window_end_utc",
        "window_label",
        "source_scope_note",
    }
    missing = required - set(windows.columns)
    if missing:
        raise ValueError(f"Missing window columns: {sorted(missing)}")
    windows["ticker"] = windows["ticker"].astype(str).str.upper().str.strip()
    windows["session_date"] = (
        pd.to_datetime(windows["session_date"], utc=True, errors="raise")
        .dt.tz_convert(None)
        .dt.normalize()
    )
    windows["window_start_utc"] = pd.to_datetime(windows["window_start_utc"], utc=True, errors="raise")
    windows["window_end_utc"] = pd.to_datetime(windows["window_end_utc"], utc=True, errors="raise")
    if (windows["window_end_utc"] <= windows["window_start_utc"]).any():
        raise ValueError("Every event window must have window_end_utc > window_start_utc")
    if windows["event_window_id"].duplicated().any():
        raise ValueError("event_window_id must be unique in the seed input")
    return windows


def _read_instrument_master(path: Path) -> pd.DataFrame:
    columns = [
        "instrument_id",
        "ticker",
        "valid_from",
        "valid_to",
        "is_common_stock",
        "is_lt1b_operational",
        "lt1b_classification_1b",
        "build_run_id",
        "schema_version",
    ]
    frame = pd.read_parquet(path, columns=columns)
    frame["ticker"] = frame["ticker"].astype(str).str.upper()
    frame["valid_from"] = pd.to_datetime(frame["valid_from"], errors="coerce").dt.normalize()
    frame["valid_to"] = pd.to_datetime(frame["valid_to"], errors="coerce").dt.normalize()
    return frame


def _instrument_for_window(instruments: pd.DataFrame, ticker: str, session_date: pd.Timestamp) -> dict[str, Any]:
    matches = instruments[instruments["ticker"].eq(ticker)].copy()
    if matches.empty:
        return {
            "instrument_id": None,
            "instrument_identity_temporal_match": False,
            "is_common_stock": None,
            "is_lt1b_operational": None,
            "lt1b_classification_1b": None,
            "instrument_master_build_run_id": None,
            "instrument_master_schema_version": None,
        }
    valid = matches[
        (matches["valid_from"].isna() | (matches["valid_from"] <= session_date))
        & (matches["valid_to"].isna() | (matches["valid_to"] >= session_date))
    ].copy()
    chosen = valid.iloc[0] if not valid.empty else matches.iloc[0]
    return {
        "instrument_id": chosen["instrument_id"],
        "instrument_identity_temporal_match": bool(not valid.empty),
        "is_common_stock": bool(chosen["is_common_stock"]) if pd.notna(chosen["is_common_stock"]) else None,
        "is_lt1b_operational": bool(chosen["is_lt1b_operational"]) if pd.notna(chosen["is_lt1b_operational"]) else None,
        "lt1b_classification_1b": chosen["lt1b_classification_1b"],
        "instrument_master_build_run_id": chosen["build_run_id"],
        "instrument_master_schema_version": chosen["schema_version"],
    }


def _read_family_gates(path: Path) -> dict[str, dict[str, Any]]:
    columns = [
        "dataset_family",
        "data_quality_verdict",
        "foundations_completion_status",
        "visual_inspection_status",
        "production_use_gate",
        "event_consumption_gate",
        "quality_policy_version",
        "build_run_id",
    ]
    frame = pd.read_parquet(path, columns=columns)
    gates: dict[str, dict[str, Any]] = {}
    for family in ["quotes", "trades"]:
        row = frame[frame["dataset_family"].eq(family)]
        if row.empty:
            gates[family] = {}
        else:
            gates[family] = row.iloc[0].to_dict()
    return gates


def _quotes_metrics(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> dict[str, Any]:
    if not path.exists():
        return {
            "source_quotes_file_present": False,
            "source_quotes_file_sha256": None,
            "quotes_rows": 0,
            "quotes_window_rows": 0,
            "quotes_first_ts_utc": None,
            "quotes_last_ts_utc": None,
            "quotes_ask_zero_pct": float("nan"),
            "quotes_bid_zero_pct": float("nan"),
            "quotes_ask_size_zero_pct": float("nan"),
            "quotes_bid_size_zero_pct": float("nan"),
            "quotes_two_sided_rows": 0,
            "quotes_crossed_rows": 0,
            "quotes_locked_rows": 0,
            "quotes_crossed_ratio_pct_all_rows": float("nan"),
            "quotes_crossed_ratio_pct_two_sided": float("nan"),
            "quotes_locked_ratio_pct_two_sided": float("nan"),
            "quotes_spread_bps_median": float("nan"),
            "quotes_spread_bps_p90": float("nan"),
            "quotes_top_depth_mean": float("nan"),
        }

    frame = pd.read_parquet(path)
    frame["ts_utc"] = pd.to_datetime(frame["timestamp"], unit="ns", utc=True, errors="coerce")
    frame = frame[(frame["ts_utc"] >= start) & (frame["ts_utc"] < end)].copy()
    rows = len(frame)
    if rows == 0:
        return {
            "source_quotes_file_present": True,
            "source_quotes_file_sha256": _sha256(path),
            "quotes_rows": int(len(pd.read_parquet(path, columns=["timestamp"]))),
            "quotes_window_rows": 0,
            "quotes_first_ts_utc": None,
            "quotes_last_ts_utc": None,
            "quotes_ask_zero_pct": float("nan"),
            "quotes_bid_zero_pct": float("nan"),
            "quotes_ask_size_zero_pct": float("nan"),
            "quotes_bid_size_zero_pct": float("nan"),
            "quotes_two_sided_rows": 0,
            "quotes_crossed_rows": 0,
            "quotes_locked_rows": 0,
            "quotes_crossed_ratio_pct_all_rows": float("nan"),
            "quotes_crossed_ratio_pct_two_sided": float("nan"),
            "quotes_locked_ratio_pct_two_sided": float("nan"),
            "quotes_spread_bps_median": float("nan"),
            "quotes_spread_bps_p90": float("nan"),
            "quotes_top_depth_mean": float("nan"),
        }

    ask = pd.to_numeric(frame["ask_price"], errors="coerce")
    bid = pd.to_numeric(frame["bid_price"], errors="coerce")
    ask_size = pd.to_numeric(frame["ask_size"], errors="coerce")
    bid_size = pd.to_numeric(frame["bid_size"], errors="coerce")
    two_sided = ask.gt(0) & bid.gt(0)
    crossed = two_sided & ask.lt(bid)
    locked = two_sided & ask.eq(bid)
    valid_spread = two_sided & ask.gt(bid)
    mid = (ask + bid) / 2.0
    spread_bps = ((ask - bid) / mid * 10_000.0).where(valid_spread & mid.gt(0))
    depth = (ask_size + bid_size).where(two_sided)
    return {
        "source_quotes_file_present": True,
        "source_quotes_file_sha256": _sha256(path),
        "quotes_rows": int(rows),
        "quotes_window_rows": int(rows),
        "quotes_first_ts_utc": _iso(frame["ts_utc"].min()),
        "quotes_last_ts_utc": _iso(frame["ts_utc"].max()),
        "quotes_ask_zero_pct": _pct(ask.le(0).sum(), rows),
        "quotes_bid_zero_pct": _pct(bid.le(0).sum(), rows),
        "quotes_ask_size_zero_pct": _pct(ask_size.le(0).sum(), rows),
        "quotes_bid_size_zero_pct": _pct(bid_size.le(0).sum(), rows),
        "quotes_two_sided_rows": int(two_sided.sum()),
        "quotes_crossed_rows": int(crossed.sum()),
        "quotes_locked_rows": int(locked.sum()),
        "quotes_crossed_ratio_pct_all_rows": _pct(crossed.sum(), rows),
        "quotes_crossed_ratio_pct_two_sided": _pct(crossed.sum(), two_sided.sum()),
        "quotes_locked_ratio_pct_two_sided": _pct(locked.sum(), two_sided.sum()),
        "quotes_spread_bps_median": float(spread_bps.median(skipna=True)) if spread_bps.notna().any() else float("nan"),
        "quotes_spread_bps_p90": float(spread_bps.quantile(0.9)) if spread_bps.notna().any() else float("nan"),
        "quotes_top_depth_mean": float(depth.mean(skipna=True)) if depth.notna().any() else float("nan"),
    }


def _trades_metrics(path: Path, start: pd.Timestamp, end: pd.Timestamp) -> dict[str, Any]:
    if not path.exists():
        return {
            "source_trades_file_present": False,
            "source_trades_file_sha256": None,
            "trades_rows": 0,
            "trades_window_rows": 0,
            "trades_first_ts_utc": None,
            "trades_last_ts_utc": None,
            "trades_invalid_price_rows": 0,
            "trades_invalid_size_rows": 0,
            "trades_odd_lot_ratio_pct": float("nan"),
            "trades_duplicate_exact_ratio_pct": float("nan"),
            "trades_off_regular_session_ratio_pct": float("nan"),
            "trades_total_volume": float("nan"),
            "trades_dollar_volume": float("nan"),
            "trades_price_min": float("nan"),
            "trades_price_max": float("nan"),
            "trades_price_last": float("nan"),
            "trades_size_median": float("nan"),
            "trades_size_p90": float("nan"),
        }

    frame = pd.read_parquet(path)
    frame["ts_utc"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    frame = frame[(frame["ts_utc"] >= start) & (frame["ts_utc"] < end)].copy()
    rows = len(frame)
    if rows == 0:
        return {
            "source_trades_file_present": True,
            "source_trades_file_sha256": _sha256(path),
            "trades_rows": int(len(pd.read_parquet(path, columns=["timestamp"]))),
            "trades_window_rows": 0,
            "trades_first_ts_utc": None,
            "trades_last_ts_utc": None,
            "trades_invalid_price_rows": 0,
            "trades_invalid_size_rows": 0,
            "trades_odd_lot_ratio_pct": float("nan"),
            "trades_duplicate_exact_ratio_pct": float("nan"),
            "trades_off_regular_session_ratio_pct": float("nan"),
            "trades_total_volume": float("nan"),
            "trades_dollar_volume": float("nan"),
            "trades_price_min": float("nan"),
            "trades_price_max": float("nan"),
            "trades_price_last": float("nan"),
            "trades_size_median": float("nan"),
            "trades_size_p90": float("nan"),
        }

    price = pd.to_numeric(frame["price"], errors="coerce")
    size = pd.to_numeric(frame["size"], errors="coerce")
    conditions = frame["conditions"].map(str) if "conditions" in frame.columns else ""
    duplicate_cols = pd.DataFrame(
        {
            "timestamp": frame["ts_utc"].astype(str),
            "price": price,
            "size": size,
            "exchange": frame["exchange"].astype(str) if "exchange" in frame.columns else "",
            "conditions": conditions,
        }
    )
    duplicate_rows = duplicate_cols.duplicated(keep=False)
    local = frame["ts_utc"].dt.tz_convert("America/New_York")
    minute_of_day = local.dt.hour * 60 + local.dt.minute
    regular = (minute_of_day >= 9 * 60 + 30) & (minute_of_day < 16 * 60)
    valid_price_size = price.gt(0) & size.gt(0)
    return {
        "source_trades_file_present": True,
        "source_trades_file_sha256": _sha256(path),
        "trades_rows": int(rows),
        "trades_window_rows": int(rows),
        "trades_first_ts_utc": _iso(frame["ts_utc"].min()),
        "trades_last_ts_utc": _iso(frame["ts_utc"].max()),
        "trades_invalid_price_rows": int(price.le(0).sum()),
        "trades_invalid_size_rows": int(size.le(0).sum()),
        "trades_odd_lot_ratio_pct": _pct((size.gt(0) & size.lt(100)).sum(), rows),
        "trades_duplicate_exact_ratio_pct": _pct(duplicate_rows.sum(), rows),
        "trades_off_regular_session_ratio_pct": _pct((~regular).sum(), rows),
        "trades_total_volume": float(size.where(size.gt(0)).sum(skipna=True)),
        "trades_dollar_volume": float((price * size).where(valid_price_size).sum(skipna=True)),
        "trades_price_min": float(price.where(price.gt(0)).min(skipna=True)),
        "trades_price_max": float(price.where(price.gt(0)).max(skipna=True)),
        "trades_price_last": float(price.where(price.gt(0)).dropna().iloc[-1]) if price.where(price.gt(0)).notna().any() else float("nan"),
        "trades_size_median": float(size.where(size.gt(0)).median(skipna=True)) if size.gt(0).any() else float("nan"),
        "trades_size_p90": float(size.where(size.gt(0)).quantile(0.9)) if size.gt(0).any() else float("nan"),
    }


def _quality_state(row: dict[str, Any]) -> str:
    if not row["source_quotes_file_present"] and not row["source_trades_file_present"]:
        return "hard_fail_source_missing"
    if row["trades_invalid_price_rows"] > 0 or row["trades_invalid_size_rows"] > 0:
        return "review_trade_integrity"
    crossed = row.get("quotes_crossed_ratio_pct_all_rows")
    if pd.notna(crossed) and crossed > 5.0:
        return "review_quote_crossed_high"
    if not row["source_quotes_file_present"] or not row["source_trades_file_present"]:
        return "review_partial_source"
    return "pass_seed_window"


def _write_dataset(frame: pd.DataFrame, dataset_dir: Path) -> None:
    for (year, month), part in frame.groupby(["year", "month"], dropna=False):
        part_dir = dataset_dir / f"year={int(year):04d}" / f"month={int(month):02d}"
        part_dir.mkdir(parents=True, exist_ok=True)
        part_path = part_dir / "part-0000.parquet"
        part.drop(columns=["year", "month"]).to_parquet(part_path, index=False)


def materialize_microstructure_features_table(
    windows_csv: Path,
    quotes_root: Path,
    future_official_quotes_root: Path,
    quotes_staging_root: Path,
    trades_root: Path,
    instrument_master: Path,
    instrument_master_manifest: Path,
    dataset_certification_matrix: Path,
    dataset_certification_matrix_manifest: Path,
    output_root: Path,
    overwrite: bool,
    dataset_id: str = DATASET_ID,
    schema_version: str = SCHEMA_VERSION,
    quality_policy_version: str = QUALITY_POLICY_VERSION,
    materialization_scope: str = MATERIALIZATION_SCOPE,
    dataset_dir_name: str = "microstructure_features_table_v0_1",
    summary_name: str = "_microstructure_features_table_summary_v0_1.csv",
    manifest_name: str = "_microstructure_features_table_manifest_v0_1.json",
    quotes_root_state: str = "provisional_d_legacy_recovery_root_pending_e_parity",
    trades_root_state: str = "official_e_raw_root",
) -> dict[str, Any]:
    _require(windows_csv, "event windows csv")
    _require(quotes_root, "quotes root")
    _require(trades_root, "trades root")
    _require(instrument_master, "instrument master")
    instrument_manifest = _load_manifest(instrument_master_manifest)
    _require(dataset_certification_matrix, "dataset certification matrix")
    dcm_manifest = _load_manifest(dataset_certification_matrix_manifest)

    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / dataset_dir_name
    summary_path = output_root / summary_name
    manifest_path = output_root / manifest_name

    if dataset_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Output exists. Pass --overwrite to replace: {dataset_dir}")
        _safe_remove_dataset_dir(dataset_dir, output_root)

    build_run_id = datetime.now(timezone.utc).strftime(f"{dataset_id}_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()

    windows = _read_windows(windows_csv)
    instruments = _read_instrument_master(instrument_master)
    gates = _read_family_gates(dataset_certification_matrix)
    rows: list[dict[str, Any]] = []

    for item in windows.itertuples(index=False):
        session_date = pd.Timestamp(item.session_date)
        ticker = str(item.ticker).upper()
        start = pd.Timestamp(item.window_start_utc)
        end = pd.Timestamp(item.window_end_utc)
        quotes_file = _locate_quotes_file(quotes_root, ticker, session_date)
        trades_file = _locate_trades_file(trades_root, ticker, session_date)
        instrument = _instrument_for_window(instruments, ticker, session_date)
        row: dict[str, Any] = {
            "microstructure_feature_id": _event_id(item.event_window_id, ticker, start.isoformat(), end.isoformat()),
            "event_window_id": item.event_window_id,
            "ticker": ticker,
            "session_date": session_date.date().isoformat(),
            "year": int(session_date.year),
            "month": int(session_date.month),
            "window_start_utc": start.isoformat(),
            "window_end_utc": end.isoformat(),
            "window_label": item.window_label,
            "source_scope_note": item.source_scope_note,
            "quotes_root_used": _path_for_json(quotes_root),
            "quotes_root_state": quotes_root_state,
            "future_official_quotes_root": _path_for_json(future_official_quotes_root),
            "quotes_staging_root": _path_for_json(quotes_staging_root),
            "trades_root_used": _path_for_json(trades_root),
            "trades_root_state": trades_root_state,
            "source_quotes_file": _path_for_json(quotes_file),
            "source_trades_file": _path_for_json(trades_file),
            **instrument,
        }
        row.update(_quotes_metrics(quotes_file, start, end))
        row.update(_trades_metrics(trades_file, start, end))
        row["quotes_family_data_quality_verdict"] = gates["quotes"].get("data_quality_verdict")
        row["quotes_family_event_consumption_gate"] = gates["quotes"].get("event_consumption_gate")
        row["quotes_family_production_use_gate"] = gates["quotes"].get("production_use_gate")
        row["trades_family_data_quality_verdict"] = gates["trades"].get("data_quality_verdict")
        row["trades_family_event_consumption_gate"] = gates["trades"].get("event_consumption_gate")
        row["trades_family_production_use_gate"] = gates["trades"].get("production_use_gate")
        row["dataset_certification_matrix_build_run_id"] = dcm_manifest.get("build_run_id")
        row["microstructure_quality_state"] = _quality_state(row)
        row["event_research_microstructure_candidate"] = row["microstructure_quality_state"] in {
            "pass_seed_window",
            "review_quote_crossed_high",
            "review_trade_integrity",
        }
        row["execution_sim_candidate"] = False
        row["backtest_core_microstructure_candidate"] = False
        row["full_universe_claim"] = False
        row["materialization_scope"] = materialization_scope
        row["quality_policy_version"] = quality_policy_version
        row["schema_version"] = schema_version
        row["build_run_id"] = build_run_id
        row["created_at_utc"] = created_at_utc
        rows.append(row)

    frame = pd.DataFrame(rows)
    duplicate_key_groups = int(
        frame.groupby(["event_window_id", "ticker", "window_start_utc", "window_end_utc"]).size().gt(1).sum()
    )
    _write_dataset(frame, dataset_dir)

    output_tree = _sha256_parquet_tree(dataset_dir)
    summary = pd.DataFrame(
        [
            {
                "dataset_id": dataset_id,
                "build_run_id": build_run_id,
                "materialization_scope": materialization_scope,
                "row_count": int(len(frame)),
                "ticker_count": int(frame["ticker"].nunique()),
                "window_count": int(frame["event_window_id"].nunique()),
                "quotes_file_present_rows": int(frame["source_quotes_file_present"].sum()),
                "trades_file_present_rows": int(frame["source_trades_file_present"].sum()),
                "hard_fail_count": int(frame["microstructure_quality_state"].astype(str).str.startswith("hard_fail").sum()),
                "execution_sim_candidate_rows": int(frame["execution_sim_candidate"].sum()),
                "backtest_core_microstructure_candidate_rows": int(frame["backtest_core_microstructure_candidate"].sum()),
                "full_universe_claim_rows": int(frame["full_universe_claim"].sum()),
                "duplicate_key_groups": duplicate_key_groups,
                "output_tree_sha256": output_tree["tree_sha256"],
            }
        ]
    )
    summary.to_csv(summary_path, index=False)

    validations = summary.iloc[0].to_dict()
    validations.update(
        {
            "source_quotes_rows_total": int(frame["quotes_rows"].sum()),
            "source_trades_rows_total": int(frame["trades_rows"].sum()),
            "instrument_identity_temporal_match_rows": int(frame["instrument_identity_temporal_match"].sum()),
        }
    )
    manifest = {
        "dataset_id": dataset_id,
        "schema_version": schema_version,
        "quality_policy_version": quality_policy_version,
        "materialization_scope": materialization_scope,
        "full_universe_claim": False,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": str(dataset_dir),
        "summary_path": str(summary_path),
        "manifest_path": str(manifest_path),
        "output_tree": output_tree,
        "source_windows_csv": str(windows_csv),
        "source_windows_csv_sha256": _sha256(windows_csv),
        "source_quotes_root": str(quotes_root),
        "source_quotes_root_state": quotes_root_state,
        "future_official_quotes_root": str(future_official_quotes_root),
        "quotes_staging_root": str(quotes_staging_root),
        "source_trades_root": str(trades_root),
        "source_trades_root_state": trades_root_state,
        "source_instrument_master": str(instrument_master),
        "source_instrument_master_sha256": _sha256(instrument_master),
        "source_instrument_master_manifest": str(instrument_master_manifest),
        "source_instrument_master_build_run_id": instrument_manifest.get("build_run_id"),
        "source_dataset_certification_matrix": str(dataset_certification_matrix),
        "source_dataset_certification_matrix_sha256": _sha256(dataset_certification_matrix),
        "source_dataset_certification_matrix_manifest": str(dataset_certification_matrix_manifest),
        "source_dataset_certification_matrix_build_run_id": dcm_manifest.get("build_run_id"),
        "source_files": frame[
            [
                "event_window_id",
                "ticker",
                "source_quotes_file",
                "source_quotes_file_sha256",
                "source_trades_file",
                "source_trades_file_sha256",
            ]
        ].to_dict(orient="records"),
        "contracts": {
            "schema": "01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md",
            "dataset_contract": "01_foundations/contract_registry/dataset_contracts/microstructure_features_table_dataset_contract_v0_1.md",
            "consumption_policy": "01_foundations/data_consumption_policies/microstructure_features_table_consumption_policy.md",
            "registry_entry": "01_foundations/dataset_registry/outputs/microstructure_features_table_registry_entry.yaml",
            "validators": "01_foundations/validators/outputs/microstructure_features_table_validators.md",
            "output_target_contract": "01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md",
            "materializer": "scripts/materialize_microstructure_features_table.py",
        },
        "validations": validations,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize scoped microstructure event-window features.")
    parser.add_argument("--windows-csv", type=Path, default=DEFAULT_WINDOWS_CSV)
    parser.add_argument("--quotes-root", type=Path, default=DEFAULT_QUOTES_ROOT)
    parser.add_argument("--future-official-quotes-root", type=Path, default=DEFAULT_FUTURE_OFFICIAL_QUOTES_ROOT)
    parser.add_argument("--quotes-staging-root", type=Path, default=DEFAULT_QUOTES_STAGING_ROOT)
    parser.add_argument("--trades-root", type=Path, default=DEFAULT_TRADES_ROOT)
    parser.add_argument("--instrument-master", type=Path, default=DEFAULT_INSTRUMENT_MASTER)
    parser.add_argument("--instrument-master-manifest", type=Path, default=DEFAULT_INSTRUMENT_MASTER_MANIFEST)
    parser.add_argument("--dataset-certification-matrix", type=Path, default=DEFAULT_DATASET_CERTIFICATION_MATRIX)
    parser.add_argument(
        "--dataset-certification-matrix-manifest",
        type=Path,
        default=DEFAULT_DATASET_CERTIFICATION_MATRIX_MANIFEST,
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--dataset-id", default=DATASET_ID)
    parser.add_argument("--schema-version", default=SCHEMA_VERSION)
    parser.add_argument("--quality-policy-version", default=QUALITY_POLICY_VERSION)
    parser.add_argument("--materialization-scope", default=MATERIALIZATION_SCOPE)
    parser.add_argument("--dataset-dir-name", default="microstructure_features_table_v0_1")
    parser.add_argument("--summary-name", default="_microstructure_features_table_summary_v0_1.csv")
    parser.add_argument("--manifest-name", default="_microstructure_features_table_manifest_v0_1.json")
    parser.add_argument(
        "--quotes-root-state",
        default="provisional_d_legacy_recovery_root_pending_e_parity",
    )
    parser.add_argument("--trades-root-state", default="official_e_raw_root")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest = materialize_microstructure_features_table(
        windows_csv=args.windows_csv,
        quotes_root=args.quotes_root,
        future_official_quotes_root=args.future_official_quotes_root,
        quotes_staging_root=args.quotes_staging_root,
        trades_root=args.trades_root,
        instrument_master=args.instrument_master,
        instrument_master_manifest=args.instrument_master_manifest,
        dataset_certification_matrix=args.dataset_certification_matrix,
        dataset_certification_matrix_manifest=args.dataset_certification_matrix_manifest,
        output_root=args.output_root,
        overwrite=args.overwrite,
        dataset_id=args.dataset_id,
        schema_version=args.schema_version,
        quality_policy_version=args.quality_policy_version,
        materialization_scope=args.materialization_scope,
        dataset_dir_name=args.dataset_dir_name,
        summary_name=args.summary_name,
        manifest_name=args.manifest_name,
        quotes_root_state=args.quotes_root_state,
        trades_root_state=args.trades_root_state,
    )
    print(json.dumps({"status": "ok", "manifest": manifest["manifest_path"], "validations": manifest["validations"]}, indent=2))


if __name__ == "__main__":
    main()
