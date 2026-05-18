from __future__ import annotations

import argparse
import json
import math
import random
import runpy
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd


CURRENT_PARQUET_CD = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet"
)
TARGET_LT1B_PATH = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet"
)
DEFAULT_CACHE_DIR = CURRENT_PARQUET_CD.parent / "root_cause_exports" / "file_acceptance_cache_lt1b"
NY_TZ = "America/New_York"
TARGET_ISSUE = "trade_price_outside_daily_range"
TARGET_WARN_1M = "trade_price_outside_1m_range"
TRADE_COLUMNS = ["timestamp", "price", "size", "exchange", "conditions"]
M1_CANDIDATE_COLUMNS = ["ts_utc", "timestamp", "date", "l", "h", "vw"]


def _utcnow_iso() -> str:
    return pd.Timestamp.now("UTC").isoformat()


def _write_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def _read_parquet_columns(path: str | Path, preferred_columns: list[str]) -> pd.DataFrame:
    path_str = str(path)
    try:
        return pd.read_parquet(path_str, columns=preferred_columns)
    except Exception:
        return pd.read_parquet(path_str)


def load_target_lt1b_tickers(target_path: Path = TARGET_LT1B_PATH) -> set[str]:
    x = pd.read_parquet(target_path, columns=["ticker"]).copy()
    x["ticker"] = x["ticker"].astype(str).str.upper().str.strip()
    return set(x["ticker"].dropna().tolist())


def classify_abs_bucket(x: float) -> str:
    if pd.isna(x):
        return "NaN"
    if x <= 0.01:
        return "<=0.01"
    if x <= 0.05:
        return "0.01-0.05"
    if x <= 0.10:
        return "0.05-0.10"
    if x <= 0.25:
        return "0.10-0.25"
    if x <= 0.50:
        return "0.25-0.50"
    if x <= 1:
        return "0.50-1"
    if x <= 5:
        return "1-5"
    return ">5"


def _safe_list(value) -> list:
    if isinstance(value, np.ndarray):
        return _safe_list(value.tolist())
    if isinstance(value, list):
        out = []
        for x in value:
            if isinstance(x, (list, tuple, np.ndarray)):
                out.extend(_safe_list(x))
            else:
                out.append(x)
        return out
    if isinstance(value, tuple):
        return _safe_list(list(value))
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [value]


def _safe_float(value) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else np.nan
    except Exception:
        return np.nan


def _row_get(row, key: str, default=None):
    if isinstance(row, dict):
        return row.get(key, default)
    if hasattr(row, "get"):
        try:
            return row.get(key, default)
        except Exception:
            pass
    if hasattr(row, key):
        return getattr(row, key)
    try:
        return row[key]
    except Exception:
        return default


def _count_negative_rows(file_path: str | Path, column: str) -> int:
    try:
        x = pd.read_parquet(Path(file_path), columns=[column])
    except Exception:
        return 0
    s = pd.to_numeric(x[column], errors="coerce")
    return int((s < 0).sum())


def compute_break_abs_max(row: pd.Series) -> float:
    daily_low = _safe_float(row.get("m.l"))
    daily_high = _safe_float(row.get("m.h"))
    trade_min = _safe_float(row.get("m.price_min"))
    trade_max = _safe_float(row.get("m.price_max"))
    break_below = max(daily_low - trade_min, 0) if pd.notna(daily_low) and pd.notna(trade_min) else np.nan
    break_above = max(trade_max - daily_high, 0) if pd.notna(daily_high) and pd.notna(trade_max) else np.nan
    return np.nanmax([break_below, break_above])


def classify_sample_stratum(row: pd.Series) -> str:
    severity = str(row.get("severity", "UNKNOWN"))
    issue_set = set(_safe_list(row.get("issues_list")))
    warn_set = set(_safe_list(row.get("warns_list")))

    if TARGET_ISSUE not in issue_set:
        return f"{severity}__control"

    confirmed = TARGET_WARN_1M in warn_set
    bucket = classify_abs_bucket(compute_break_abs_max(row))
    conf = "confirmed" if confirmed else "unconfirmed"
    return f"{severity}__daily_range__{conf}__{bucket}"


def _update_reservoir(reservoir: dict[str, list[dict]], row_dict: dict, sample_size: int, seen_counter: dict[str, int], rng: random.Random) -> None:
    key = row_dict["sample_stratum"]
    seen_counter[key] += 1
    seen = seen_counter[key]
    bucket = reservoir[key]
    if len(bucket) < sample_size:
        bucket.append(row_dict)
        return
    j = rng.randint(0, seen - 1)
    if j < sample_size:
        bucket[j] = row_dict


def compute_layer1_artifacts(handle, target_tickers: set[str], batch_size: int, sample_per_stratum: int, max_batches: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    counters = Counter()
    severity_counter = Counter()
    examples: list[dict] = []
    reservoirs: dict[str, list[dict]] = defaultdict(list)
    seen_counter: dict[str, int] = defaultdict(int)
    rng = random.Random(42)

    cols = ["file", "ticker", "date", "severity", "issues", "warns", "metrics_json"]
    for batch_idx, df in enumerate(handle.stream(columns=cols, batch_size=batch_size, normalize=True), start=1):
        if max_batches is not None and batch_idx > max_batches:
            break
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
        df = df.loc[df["ticker"].isin(target_tickers)].copy()
        if df.empty:
            continue

        counters["files_total"] += len(df)
        severity_counter.update(df["severity"].astype(str).tolist())

        for _, row in df.iterrows():
            metrics = row.get("metrics", {}) if isinstance(row.get("metrics"), dict) else {}
            missing_required = _safe_list(metrics.get("missing_required_cols"))
            dtype_mismatches = _safe_list(metrics.get("dtype_mismatches"))
            neg_price_signal = _safe_float(metrics.get("negative_or_zero_price_rows"))
            neg_size_signal = _safe_float(metrics.get("negative_or_zero_size_rows"))
            ts_out = bool(metrics.get("timestamp_out_of_partition_day", False))
            rows_after_parse = _safe_float(metrics.get("rows_after_parse"))
            n_raw = _safe_float(metrics.get("n"))
            file_path = row.get("file")

            neg_price = _count_negative_rows(file_path, "price") if pd.notna(neg_price_signal) and neg_price_signal > 0 else 0
            neg_size = _count_negative_rows(file_path, "size") if pd.notna(neg_size_signal) and neg_size_signal > 0 else 0

            if missing_required:
                counters["files_missing_required_cols"] += 1
            if dtype_mismatches:
                counters["files_dtype_mismatch"] += 1
            if neg_price > 0:
                counters["files_negative_price"] += 1
            if neg_size > 0:
                counters["files_negative_size"] += 1
            if ts_out:
                counters["files_timestamp_out_of_partition"] += 1
            if pd.notna(rows_after_parse) and rows_after_parse <= 0:
                counters["files_empty_after_parse"] += 1
            if pd.notna(n_raw) and n_raw <= 0:
                counters["files_zero_raw_rows"] += 1

            hard_integrity_fail = bool(
                missing_required
                or (neg_price > 0)
                or (neg_size > 0)
                or ts_out
                or (pd.notna(rows_after_parse) and rows_after_parse <= 0)
            )
            if hard_integrity_fail and len(examples) < 200:
                examples.append(
                    {
                        "file": row.get("file"),
                        "ticker": row.get("ticker"),
                        "date": row.get("date"),
                        "severity": row.get("severity"),
                        "missing_required_cols": str(missing_required),
                        "dtype_mismatches": str(dtype_mismatches),
                        "negative_price_rows": neg_price,
                        "negative_size_rows": neg_size,
                        "timestamp_out_of_partition_day": ts_out,
                        "rows_after_parse": rows_after_parse,
                        "issues_list": str(_safe_list(row.get("issues_list"))),
                        "warns_list": str(_safe_list(row.get("warns_list"))),
                    }
                )

            row_dict = {
                "file": row.get("file"),
                "ticker": row.get("ticker"),
                "date": row.get("date"),
                "severity": row.get("severity"),
                "issues_list": _safe_list(row.get("issues_list")),
                "warns_list": _safe_list(row.get("warns_list")),
                "m.l": metrics.get("l"),
                "m.h": metrics.get("h"),
                "m.vw": metrics.get("vw"),
                "m.price_min": metrics.get("price_min"),
                "m.price_max": metrics.get("price_max"),
                "m.trade_vwap": metrics.get("trade_vwap"),
                "m.off_session_trade_pct": metrics.get("off_session_trade_pct"),
                "m.duplicate_excess_ratio_pct": metrics.get("duplicate_excess_ratio_pct"),
                "m.max_trades_same_timestamp": metrics.get("max_trades_same_timestamp"),
                "m.missing_required_cols": missing_required,
                "m.dtype_mismatches": dtype_mismatches,
                "m.timestamp_out_of_partition_day": ts_out,
                "m.rows_after_parse": rows_after_parse,
                "m.ohlcv_1m_found": metrics.get("ohlcv_1m_found"),
                "m.ohlcv_daily_found": metrics.get("ohlcv_daily_found"),
                "m.ohlcv_1m_path": metrics.get("ohlcv_1m_path"),
                "m.ohlcv_daily_path": metrics.get("ohlcv_daily_path"),
                "sample_stratum": None,
            }
            row_dict["sample_stratum"] = classify_sample_stratum(pd.Series(row_dict))
            _update_reservoir(reservoirs, row_dict, sample_per_stratum, seen_counter, rng)

        if batch_idx % 25 == 0:
            sample_rows = sum(len(v) for v in reservoirs.values())
            print(
                json.dumps(
                    {
                        "stage": "layer1_scan",
                        "batch_idx": batch_idx,
                        "files_total_seen_lt1b": counters["files_total"],
                        "sample_rows_current": sample_rows,
                        "strata_seen": len(reservoirs),
                    },
                    ensure_ascii=False,
                )
            )

    integrity_summary = pd.DataFrame(
        [
            {"metric": "files_total", "value": counters["files_total"]},
            {"metric": "pass_files", "value": severity_counter.get("PASS", 0)},
            {"metric": "soft_fail_files", "value": severity_counter.get("SOFT_FAIL", 0)},
            {"metric": "hard_fail_files", "value": severity_counter.get("HARD_FAIL", 0)},
            {"metric": "files_missing_required_cols", "value": counters["files_missing_required_cols"]},
            {"metric": "files_dtype_mismatch", "value": counters["files_dtype_mismatch"]},
            {"metric": "files_negative_price", "value": counters["files_negative_price"]},
            {"metric": "files_negative_size", "value": counters["files_negative_size"]},
            {"metric": "files_timestamp_out_of_partition", "value": counters["files_timestamp_out_of_partition"]},
            {"metric": "files_empty_after_parse", "value": counters["files_empty_after_parse"]},
            {"metric": "files_zero_raw_rows", "value": counters["files_zero_raw_rows"]},
        ]
    )

    sample_index = pd.DataFrame([row for rows in reservoirs.values() for row in rows]).drop_duplicates(subset=["file"]).reset_index(drop=True)
    integrity_examples = pd.DataFrame(examples)
    return integrity_summary, integrity_examples, sample_index


def _conditions_key(value) -> str:
    xs = _condition_codes(value)
    try:
        return json.dumps(xs, ensure_ascii=False)
    except Exception:
        return str(xs)


def _condition_codes(value) -> list[int]:
    out = []
    for x in _safe_list(value):
        try:
            out.append(int(x))
        except Exception:
            continue
    return out


def _classify_session(ts_local: pd.Timestamp) -> str:
    hm = (ts_local.hour, ts_local.minute)
    if hm < (9, 30):
        return "premarket"
    if hm < (16, 0):
        return "regular"
    return "afterhours"


@lru_cache(maxsize=8192)
def _load_m1_day_cached(m1_path: str, target_date_iso: str) -> pd.DataFrame:
    p = Path(str(m1_path))
    if not p.exists():
        return pd.DataFrame(columns=["minute_ts", "l", "h", "vw"])
    m1 = _read_parquet_columns(p, M1_CANDIDATE_COLUMNS)
    if "ts_utc" in m1.columns:
        m1["ts_utc"] = pd.to_datetime(m1["ts_utc"], format="%Y-%m-%dT%H:%M:%SZ", utc=True, errors="coerce")
    elif "timestamp" in m1.columns:
        m1["ts_utc"] = pd.to_datetime(m1["timestamp"], utc=True, errors="coerce")
    else:
        return pd.DataFrame(columns=["minute_ts", "l", "h", "vw"])
    target_date = pd.Timestamp(target_date_iso).date()
    if "date" in m1.columns:
        m1["date"] = pd.to_datetime(m1["date"], format="%Y-%m-%d", errors="coerce").dt.date
        m1 = m1.loc[m1["date"] == target_date]
    else:
        m1 = m1.loc[m1["ts_utc"].dt.date == target_date]
    if m1.empty:
        return pd.DataFrame(columns=["minute_ts", "l", "h", "vw"])
    m1["minute_ts"] = m1["ts_utc"].dt.floor("min")
    for col in ["l", "h", "vw"]:
        if col in m1.columns:
            m1[col] = pd.to_numeric(m1[col], errors="coerce")
    return m1[["minute_ts", "l", "h", "vw"]].copy()


def _load_m1_day(m1_path: str | None, date_value) -> pd.DataFrame:
    if not m1_path:
        return pd.DataFrame(columns=["minute_ts", "l", "h", "vw"])
    return _load_m1_day_cached(str(m1_path), str(pd.Timestamp(date_value).date()))


def _longest_consecutive_run(sorted_minutes: list[pd.Timestamp]) -> int:
    if not sorted_minutes:
        return 0
    current = 1
    best = 1
    for prev, cur in zip(sorted_minutes[:-1], sorted_minutes[1:]):
        if (cur - prev) == pd.Timedelta(minutes=1):
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


SCALE_TARGETS = [0.1, 0.2, 0.25, 0.3333, 0.5, 0.6667, 0.8, 0.9091, 1.0, 1.1111, 1.25, 1.5, 2, 3, 4, 5, 6, 10, 12, 15, 20, 100, 150, 300, 1000, 5000, 10000, 30000]


def _nearest_scale_bucket(x: float) -> str:
    if pd.isna(x) or x <= 0:
        return "nan"
    best = min(SCALE_TARGETS, key=lambda t: abs(np.log(x) - np.log(t)))
    rel = abs(x - best) / best
    if rel <= 0.03:
        return f"~{best:g}x"
    if rel <= 0.10:
        return f"near_{best:g}x"
    if x < 1:
        return "<1x_other"
    return ">1x_other"


def _is_scale_mismatch_bucket(bucket: str) -> bool:
    return bucket not in {"nan", "<1x_other", ">1x_other", "~1x"}


def _load_trade_frame_for_breakdown(row: pd.Series) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    file_path = Path(str(_row_get(row, "file")))
    trades = _read_parquet_columns(file_path, TRADE_COLUMNS)
    trades["timestamp"] = pd.to_datetime(trades["timestamp"], utc=True, errors="coerce")
    trades["price"] = pd.to_numeric(trades["price"], errors="coerce")
    trades["size"] = pd.to_numeric(trades["size"], errors="coerce")
    trades["conditions_key"] = trades["conditions"].map(_conditions_key)
    trades["condition_codes"] = trades["conditions"].map(_condition_codes)
    trades = trades.dropna(subset=["timestamp", "price", "size"]).sort_values("timestamp").copy()
    trades["timestamp_local"] = trades["timestamp"].dt.tz_convert(NY_TZ)
    trades["session"] = trades["timestamp_local"].map(_classify_session)
    trades["minute_ts"] = trades["timestamp"].dt.floor("min")

    daily_low = _safe_float(_row_get(row, "m.l"))
    daily_high = _safe_float(_row_get(row, "m.h"))
    outside_daily = pd.Series(False, index=trades.index)
    if pd.notna(daily_low) and pd.notna(daily_high):
        outside_daily = (trades["price"] < daily_low) | (trades["price"] > daily_high)

    outside_1m = pd.Series(False, index=trades.index)
    m1_day = _load_m1_day(_row_get(row, "m.ohlcv_1m_path"), _row_get(row, "date"))
    if not m1_day.empty:
        merged = trades.merge(m1_day, on="minute_ts", how="left")
        valid_1m = merged["l"].notna() & merged["h"].notna()
        outside_1m = valid_1m & ((merged["price"] < merged["l"]) | (merged["price"] > merged["h"]))
    return trades, outside_daily, outside_1m


def compute_raw_metrics_for_sample_row(row: pd.Series) -> dict:
    file_path = Path(str(_row_get(row, "file")))
    trades = _read_parquet_columns(file_path, TRADE_COLUMNS)
    trades["timestamp"] = pd.to_datetime(trades["timestamp"], utc=True, errors="coerce")
    trades["price"] = pd.to_numeric(trades["price"], errors="coerce")
    trades["size"] = pd.to_numeric(trades["size"], errors="coerce")
    trades["conditions_key"] = trades["conditions"].map(_conditions_key)
    trades = trades.dropna(subset=["timestamp", "price", "size"]).sort_values("timestamp").copy()
    trades["timestamp_local"] = trades["timestamp"].dt.tz_convert(NY_TZ)
    trades["session"] = trades["timestamp_local"].map(_classify_session)
    trades["minute_ts"] = trades["timestamp"].dt.floor("min")
    trades["size_bucket"] = np.where(trades["size"] < 100, "odd_lot", "round_lot")

    n_trades = int(len(trades))
    volume_total = float(trades["size"].sum()) if n_trades else 0.0
    premarket_mask = trades["session"] == "premarket"
    regular_mask = trades["session"] == "regular"
    afterhours_mask = trades["session"] == "afterhours"
    prepost_mask = premarket_mask | afterhours_mask
    odd_lot_mask = trades["size_bucket"] == "odd_lot"
    round_lot_mask = trades["size_bucket"] == "round_lot"
    core_mask = regular_mask & round_lot_mask

    dup_exact_mask = trades.duplicated(subset=["timestamp", "price", "size", "exchange", "conditions_key"], keep=False)
    dup_exact_ratio_pct = float(100 * dup_exact_mask.mean()) if n_trades else np.nan
    timestamp_counts = trades["timestamp"].value_counts()
    max_trades_same_timestamp_raw = int(timestamp_counts.max()) if not timestamp_counts.empty else 0
    negative_price_rows = int((trades["price"] < 0).sum()) if n_trades else 0
    negative_size_rows = int((trades["size"] < 0).sum()) if n_trades else 0

    daily_low = _safe_float(_row_get(row, "m.l"))
    daily_high = _safe_float(_row_get(row, "m.h"))
    daily_vw = _safe_float(_row_get(row, "m.vw"))

    outside_daily = pd.Series(False, index=trades.index)
    if pd.notna(daily_low) and pd.notna(daily_high):
        outside_daily = (trades["price"] < daily_low) | (trades["price"] > daily_high)

    outside_daily_pct = float(100 * outside_daily.mean()) if n_trades else np.nan
    outside_daily_volume_pct = float(100 * trades.loc[outside_daily, "size"].sum() / volume_total) if volume_total > 0 else np.nan
    outside_daily_premarket_pct = float(100 * outside_daily.loc[premarket_mask].mean()) if premarket_mask.any() else np.nan
    outside_daily_regular_pct = float(100 * outside_daily.loc[regular_mask].mean()) if regular_mask.any() else np.nan
    outside_daily_afterhours_pct = float(100 * outside_daily.loc[afterhours_mask].mean()) if afterhours_mask.any() else np.nan
    regular_volume = float(trades.loc[regular_mask, "size"].sum()) if regular_mask.any() else 0.0
    outside_daily_regular_volume_pct = float(100 * trades.loc[regular_mask & outside_daily, "size"].sum() / regular_volume) if regular_volume > 0 else np.nan
    outside_daily_prepost_pct = float(100 * outside_daily.loc[prepost_mask].mean()) if prepost_mask.any() else np.nan
    odd_lot_volume = float(trades.loc[odd_lot_mask, "size"].sum()) if odd_lot_mask.any() else 0.0
    round_lot_volume = float(trades.loc[round_lot_mask, "size"].sum()) if round_lot_mask.any() else 0.0
    outside_daily_odd_lot_pct = float(100 * outside_daily.loc[odd_lot_mask].mean()) if odd_lot_mask.any() else np.nan
    outside_daily_round_lot_pct = float(100 * outside_daily.loc[round_lot_mask].mean()) if round_lot_mask.any() else np.nan
    outside_daily_odd_lot_volume_pct = float(100 * trades.loc[odd_lot_mask & outside_daily, "size"].sum() / odd_lot_volume) if odd_lot_volume > 0 else np.nan
    outside_daily_round_lot_volume_pct = float(100 * trades.loc[round_lot_mask & outside_daily, "size"].sum() / round_lot_volume) if round_lot_volume > 0 else np.nan
    core_trades = int(core_mask.sum()) if n_trades else 0
    core_volume = float(trades.loc[core_mask, "size"].sum()) if core_mask.any() else 0.0
    core_outside_daily_pct = float(100 * outside_daily.loc[core_mask].mean()) if core_mask.any() else np.nan
    core_outside_daily_volume_pct = float(100 * trades.loc[core_mask & outside_daily, "size"].sum() / core_volume) if core_volume > 0 else np.nan

    m1_day = _load_m1_day(_row_get(row, "m.ohlcv_1m_path"), _row_get(row, "date"))
    outside_1m_pct = np.nan
    outside_1m_premarket_pct = np.nan
    outside_1m_regular_pct = np.nan
    outside_1m_afterhours_pct = np.nan
    outside_1m_volume_pct = np.nan
    outside_1m_odd_lot_pct = np.nan
    outside_1m_round_lot_pct = np.nan
    outside_1m_odd_lot_volume_pct = np.nan
    outside_1m_round_lot_volume_pct = np.nan
    core_outside_1m_pct = np.nan
    core_outside_1m_volume_pct = np.nan
    if not m1_day.empty:
        merged = trades.merge(m1_day, on="minute_ts", how="left")
        valid_1m = merged["l"].notna() & merged["h"].notna()
        outside_1m = valid_1m & ((merged["price"] < merged["l"]) | (merged["price"] > merged["h"]))
        if valid_1m.any():
            outside_1m_pct = float(100 * outside_1m.loc[valid_1m].mean())
            valid_volume = float(merged.loc[valid_1m, "size"].sum())
            outside_1m_volume_pct = float(100 * merged.loc[outside_1m, "size"].sum() / valid_volume) if valid_volume > 0 else np.nan
            valid_premarket = valid_1m & premarket_mask
            valid_regular = valid_1m & regular_mask
            valid_afterhours = valid_1m & afterhours_mask
            valid_odd_lot = valid_1m & odd_lot_mask
            valid_round_lot = valid_1m & round_lot_mask
            outside_1m_premarket_pct = float(100 * outside_1m.loc[valid_premarket].mean()) if valid_premarket.any() else np.nan
            outside_1m_regular_pct = float(100 * outside_1m.loc[valid_regular].mean()) if valid_regular.any() else np.nan
            outside_1m_afterhours_pct = float(100 * outside_1m.loc[valid_afterhours].mean()) if valid_afterhours.any() else np.nan
            outside_1m_odd_lot_pct = float(100 * outside_1m.loc[valid_odd_lot].mean()) if valid_odd_lot.any() else np.nan
            outside_1m_round_lot_pct = float(100 * outside_1m.loc[valid_round_lot].mean()) if valid_round_lot.any() else np.nan
            odd_lot_valid_volume = float(merged.loc[valid_odd_lot, "size"].sum()) if valid_odd_lot.any() else 0.0
            round_lot_valid_volume = float(merged.loc[valid_round_lot, "size"].sum()) if valid_round_lot.any() else 0.0
            outside_1m_odd_lot_volume_pct = float(100 * merged.loc[valid_odd_lot & outside_1m, "size"].sum() / odd_lot_valid_volume) if odd_lot_valid_volume > 0 else np.nan
            outside_1m_round_lot_volume_pct = float(100 * merged.loc[valid_round_lot & outside_1m, "size"].sum() / round_lot_valid_volume) if round_lot_valid_volume > 0 else np.nan
            valid_core = valid_1m & core_mask
            core_valid_volume = float(merged.loc[valid_core, "size"].sum()) if valid_core.any() else 0.0
            core_outside_1m_pct = float(100 * outside_1m.loc[valid_core].mean()) if valid_core.any() else np.nan
            core_outside_1m_volume_pct = float(100 * merged.loc[valid_core & outside_1m, "size"].sum() / core_valid_volume) if core_valid_volume > 0 else np.nan

    active_minutes = int(trades["minute_ts"].nunique()) if n_trades else 0
    outside_minutes = sorted(trades.loc[outside_daily, "minute_ts"].dropna().unique().tolist())
    outside_minutes_n = int(len(outside_minutes))
    outside_minutes_pct_active = float(100 * outside_minutes_n / active_minutes) if active_minutes > 0 else np.nan
    longest_outside_run_minutes = _longest_consecutive_run(outside_minutes)

    top_outside_minute_trade_share_pct = np.nan
    top_outside_minute_volume_share_pct = np.nan
    if outside_daily.any():
        per_min_count = trades.loc[outside_daily].groupby("minute_ts").size()
        per_min_vol = trades.loc[outside_daily].groupby("minute_ts")["size"].sum()
        top_outside_minute_trade_share_pct = float(100 * per_min_count.max() / max(int(outside_daily.sum()), 1))
        top_outside_minute_volume_share_pct = float(100 * per_min_vol.max() / max(float(trades.loc[outside_daily, "size"].sum()), 1.0))

    trade_vwap = float((trades["price"] * trades["size"]).sum() / volume_total) if volume_total > 0 else np.nan
    trade_vwap_vs_daily_vw_diff_pct_raw = float(100 * abs(trade_vwap - daily_vw) / abs(daily_vw)) if pd.notna(trade_vwap) and pd.notna(daily_vw) and daily_vw != 0 else np.nan
    daily_vw_to_trade_vw = float(daily_vw / trade_vwap) if pd.notna(daily_vw) and pd.notna(trade_vwap) and trade_vwap != 0 else np.nan
    daily_high_to_trade_max = float(daily_high / trades["price"].max()) if pd.notna(daily_high) and n_trades and trades["price"].max() != 0 else np.nan
    daily_low_to_trade_min = float(daily_low / trades["price"].min()) if pd.notna(daily_low) and n_trades and trades["price"].min() != 0 else np.nan
    scale_bucket_vw = _nearest_scale_bucket(daily_vw_to_trade_vw)
    scale_bucket_high = _nearest_scale_bucket(daily_high_to_trade_max)
    scale_bucket_low = _nearest_scale_bucket(daily_low_to_trade_min)

    baseline_eligible_mask = regular_mask & (trades["price"] >= 0) & (trades["size"] >= 0)
    baseline_eligible_trade_pct = float(100 * baseline_eligible_mask.mean()) if n_trades else np.nan
    baseline_eligible_volume_pct = float(100 * trades.loc[baseline_eligible_mask, "size"].sum() / volume_total) if volume_total > 0 else np.nan

    return {
        "file": _row_get(row, "file"),
        "ticker": _row_get(row, "ticker"),
        "date": _row_get(row, "date"),
        "severity": _row_get(row, "severity"),
        "sample_stratum": _row_get(row, "sample_stratum"),
        "n_trades": n_trades,
        "volume_total": volume_total,
        "premarket_trade_pct": float(100 * premarket_mask.mean()) if n_trades else np.nan,
        "regular_trade_pct": float(100 * regular_mask.mean()) if n_trades else np.nan,
        "afterhours_trade_pct": float(100 * afterhours_mask.mean()) if n_trades else np.nan,
        "prepost_trade_pct": float(100 * prepost_mask.mean()) if n_trades else np.nan,
        "off_session_trade_pct": float(100 * prepost_mask.mean()) if n_trades else np.nan,
        "premarket_volume_pct": float(100 * trades.loc[premarket_mask, "size"].sum() / volume_total) if volume_total > 0 else np.nan,
        "regular_volume_pct": float(100 * trades.loc[regular_mask, "size"].sum() / volume_total) if volume_total > 0 else np.nan,
        "afterhours_volume_pct": float(100 * trades.loc[afterhours_mask, "size"].sum() / volume_total) if volume_total > 0 else np.nan,
        "off_session_volume_pct": float(100 * trades.loc[prepost_mask, "size"].sum() / volume_total) if volume_total > 0 else np.nan,
        "odd_lot_trade_pct": float(100 * odd_lot_mask.mean()) if n_trades else np.nan,
        "round_lot_trade_pct": float(100 * round_lot_mask.mean()) if n_trades else np.nan,
        "core_regular_round_trade_pct": float(100 * core_mask.mean()) if n_trades else np.nan,
        "core_regular_round_trades": core_trades,
        "odd_lot_volume_pct": float(100 * trades.loc[odd_lot_mask, "size"].sum() / volume_total) if volume_total > 0 else np.nan,
        "round_lot_volume_pct": float(100 * trades.loc[round_lot_mask, "size"].sum() / volume_total) if volume_total > 0 else np.nan,
        "core_regular_round_volume_pct": float(100 * core_volume / volume_total) if volume_total > 0 else np.nan,
        "baseline_eligible_trade_pct": baseline_eligible_trade_pct,
        "baseline_eligible_volume_pct": baseline_eligible_volume_pct,
        "duplicate_exact_ratio_pct_raw": dup_exact_ratio_pct,
        "max_trades_same_timestamp_raw": max_trades_same_timestamp_raw,
        "negative_price_rows_raw": negative_price_rows,
        "negative_size_rows_raw": negative_size_rows,
        "condition_combo_nunique": int(trades["conditions_key"].nunique()) if n_trades else 0,
        "trade_vwap_raw": trade_vwap,
        "trade_vwap_vs_daily_vw_diff_pct_raw": trade_vwap_vs_daily_vw_diff_pct_raw,
        "daily_vw_to_trade_vw": daily_vw_to_trade_vw,
        "daily_high_to_trade_max": daily_high_to_trade_max,
        "daily_low_to_trade_min": daily_low_to_trade_min,
        "scale_bucket_vw": scale_bucket_vw,
        "scale_bucket_high": scale_bucket_high,
        "scale_bucket_low": scale_bucket_low,
        "outside_daily_pct": outside_daily_pct,
        "outside_daily_volume_pct": outside_daily_volume_pct,
        "outside_daily_premarket_pct": outside_daily_premarket_pct,
        "outside_daily_regular_pct": outside_daily_regular_pct,
        "outside_daily_afterhours_pct": outside_daily_afterhours_pct,
        "outside_daily_regular_volume_pct": outside_daily_regular_volume_pct,
        "outside_daily_prepost_pct": outside_daily_prepost_pct,
        "outside_daily_odd_lot_pct": outside_daily_odd_lot_pct,
        "outside_daily_round_lot_pct": outside_daily_round_lot_pct,
        "outside_daily_odd_lot_volume_pct": outside_daily_odd_lot_volume_pct,
        "outside_daily_round_lot_volume_pct": outside_daily_round_lot_volume_pct,
        "core_outside_daily_pct": core_outside_daily_pct,
        "core_outside_daily_volume_pct": core_outside_daily_volume_pct,
        "outside_1m_pct": outside_1m_pct,
        "outside_1m_premarket_pct": outside_1m_premarket_pct,
        "outside_1m_regular_pct": outside_1m_regular_pct,
        "outside_1m_afterhours_pct": outside_1m_afterhours_pct,
        "outside_1m_volume_pct": outside_1m_volume_pct,
        "outside_1m_odd_lot_pct": outside_1m_odd_lot_pct,
        "outside_1m_round_lot_pct": outside_1m_round_lot_pct,
        "outside_1m_odd_lot_volume_pct": outside_1m_odd_lot_volume_pct,
        "outside_1m_round_lot_volume_pct": outside_1m_round_lot_volume_pct,
        "core_outside_1m_pct": core_outside_1m_pct,
        "core_outside_1m_volume_pct": core_outside_1m_volume_pct,
        "outside_minutes_n": outside_minutes_n,
        "outside_minutes_pct_active": outside_minutes_pct_active,
        "longest_outside_run_minutes": longest_outside_run_minutes,
        "top_outside_minute_trade_share_pct": top_outside_minute_trade_share_pct,
        "top_outside_minute_volume_share_pct": top_outside_minute_volume_share_pct,
        "missing_required_cols_count": len(_safe_list(_row_get(row, "m.missing_required_cols"))),
        "dtype_mismatches_count": len(_safe_list(_row_get(row, "m.dtype_mismatches"))),
        "timestamp_out_of_partition_day": bool(_row_get(row, "m.timestamp_out_of_partition_day", False)),
        "rows_after_parse": _safe_float(_row_get(row, "m.rows_after_parse")),
        "has_1m_reference": bool(_row_get(row, "m.ohlcv_1m_found", False)),
        "has_daily_reference": bool(_row_get(row, "m.ohlcv_daily_found", False)),
    }


def classify_acceptance(row: pd.Series) -> str:
    integrity_fail = bool(
        row.get("missing_required_cols_count", 0) > 0
        or row.get("negative_price_rows_raw", 0) > 0
        or row.get("negative_size_rows_raw", 0) > 0
        or bool(row.get("timestamp_out_of_partition_day", False))
        or (pd.notna(row.get("rows_after_parse")) and row.get("rows_after_parse") <= 0)
    )
    if integrity_fail:
        return "bad_data"

    scale_bucket_candidates = [
        str(row.get("scale_bucket_vw", "nan")),
        str(row.get("scale_bucket_high", "nan")),
        str(row.get("scale_bucket_low", "nan")),
    ]
    scale_mismatch_flag = any(_is_scale_mismatch_bucket(x) for x in scale_bucket_candidates)
    extreme_reference_conflict = bool(
        (pd.notna(row.get("outside_daily_regular_pct")) and row.get("outside_daily_regular_pct") >= 25)
        or (pd.notna(row.get("outside_1m_regular_pct")) and row.get("outside_1m_regular_pct") >= 25)
    )
    extreme_vwap_scale_gap = bool(
        pd.notna(row.get("trade_vwap_vs_daily_vw_diff_pct_raw"))
        and row.get("trade_vwap_vs_daily_vw_diff_pct_raw") >= 20
        and pd.notna(row.get("outside_daily_regular_pct"))
        and row.get("outside_daily_regular_pct") >= 90
    )
    if (scale_mismatch_flag and extreme_reference_conflict) or extreme_vwap_scale_gap:
        return "reference_scale_mismatch"

    no_1m_reference = not bool(row.get("has_1m_reference", False))
    no_1m_reference_review = bool(
        no_1m_reference
        and pd.notna(row.get("outside_daily_regular_pct"))
        and row.get("outside_daily_regular_pct") >= 25
    )
    if no_1m_reference_review:
        return "review_no_1m_reference"

    odd_lot_dominant = bool(pd.notna(row.get("odd_lot_trade_pct")) and row.get("odd_lot_trade_pct") >= 80)
    odd_lot_reference_gap = bool(
        odd_lot_dominant
        and (
            (pd.notna(row.get("outside_1m_regular_pct")) and row.get("outside_1m_regular_pct") >= 25)
            or (
                not bool(row.get("has_1m_reference", False))
                and pd.notna(row.get("outside_daily_regular_pct"))
                and row.get("outside_daily_regular_pct") >= 90
            )
        )
    )
    if odd_lot_reference_gap:
        return "review_microstructure"

    odd_lot_heavy = bool(pd.notna(row.get("odd_lot_trade_pct")) and row.get("odd_lot_trade_pct") >= 60)
    odd_lot_moderate_conflict = bool(
        odd_lot_heavy
        and (
            (pd.notna(row.get("outside_1m_regular_pct")) and row.get("outside_1m_regular_pct") >= 15)
            or (
                pd.notna(row.get("outside_daily_regular_pct"))
                and row.get("outside_daily_regular_pct") >= 25
                and pd.notna(row.get("outside_daily_regular_volume_pct"))
                and row.get("outside_daily_regular_volume_pct") <= 15
            )
        )
    )
    if odd_lot_moderate_conflict:
        return "review_microstructure"

    core_trade_share = row.get("core_regular_round_trade_pct")
    core_outside_daily_pct = row.get("core_outside_daily_pct")
    core_outside_1m_pct = row.get("core_outside_1m_pct")
    core_clean = bool(
        pd.notna(core_trade_share)
        and core_trade_share > 0
        and (
            (pd.isna(core_outside_daily_pct) or core_outside_daily_pct <= 1)
            and (pd.isna(core_outside_1m_pct) or core_outside_1m_pct <= 1)
        )
    )
    if core_clean:
        if odd_lot_heavy or (
            pd.notna(row.get("outside_1m_regular_pct")) and row.get("outside_1m_regular_pct") >= 15
        ) or (
            pd.notna(row.get("outside_daily_regular_pct")) and row.get("outside_daily_regular_pct") >= 15
        ):
            return "review_microstructure"
        return "review"

    one_minute_reference_alignment_review = bool(
        bool(row.get("has_1m_reference", False))
        and str(row.get("scale_bucket_vw", "nan")) in {"~1x", "near_1x"}
        and pd.notna(core_outside_1m_pct)
        and core_outside_1m_pct >= 25
        and pd.notna(core_outside_daily_pct)
        and core_outside_daily_pct <= 5
        and pd.notna(row.get("core_outside_daily_volume_pct"))
        and row.get("core_outside_daily_volume_pct") <= 5
        and pd.notna(row.get("trade_vwap_vs_daily_vw_diff_pct_raw"))
        and row.get("trade_vwap_vs_daily_vw_diff_pct_raw") <= 5
    )
    if one_minute_reference_alignment_review:
        return "review_1m_reference_alignment"

    good_rule = (
        pd.notna(row.get("outside_daily_regular_pct"))
        and pd.notna(row.get("outside_daily_regular_volume_pct"))
        and pd.notna(row.get("outside_minutes_pct_active"))
        and pd.notna(row.get("outside_1m_regular_pct"))
        and row.get("outside_daily_regular_pct") <= 1
        and row.get("outside_daily_regular_volume_pct") <= 1
        and row.get("outside_minutes_pct_active") <= 5
        and row.get("outside_1m_regular_pct") <= 1
        and row.get("duplicate_exact_ratio_pct_raw", 0) <= 0.5
    )
    if good_rule:
        return "good"

    bad_rule = (
        (pd.notna(core_outside_daily_pct) and core_outside_daily_pct >= 25)
        or (pd.notna(row.get("core_outside_daily_volume_pct")) and row.get("core_outside_daily_volume_pct") >= 25)
        or (pd.notna(core_outside_1m_pct) and core_outside_1m_pct >= 25)
        or (pd.notna(row.get("core_outside_1m_volume_pct")) and row.get("core_outside_1m_volume_pct") >= 25)
        or (pd.notna(row.get("outside_minutes_pct_active")) and row.get("outside_minutes_pct_active") >= 25)
    )
    if bad_rule:
        return "bad_data"
    return "review"


def build_sample_artifacts(sample_index: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metrics_rows = []
    condition_counter = Counter()
    condition_code_counter = Counter()
    combo_outside_daily_counter = Counter()
    combo_outside_1m_counter = Counter()
    code_outside_daily_counter = Counter()
    code_outside_1m_counter = Counter()
    total_rows = len(sample_index)
    for idx, (_, row) in enumerate(sample_index.iterrows(), start=1):
        metrics = compute_raw_metrics_for_sample_row(row)
        metrics_rows.append(metrics)

        trades, outside_daily, outside_1m = _load_trade_frame_for_breakdown(row)
        for sig, count in trades["conditions_key"].value_counts().items():
            condition_counter[sig] += int(count)
        for sig, count in trades.loc[outside_daily, "conditions_key"].value_counts().items():
            combo_outside_daily_counter[sig] += int(count)
        for sig, count in trades.loc[outside_1m, "conditions_key"].value_counts().items():
            combo_outside_1m_counter[sig] += int(count)
        for codes, is_out_daily, is_out_1m in zip(trades["condition_codes"], outside_daily.tolist(), outside_1m.tolist()):
            for code in codes:
                condition_code_counter[code] += 1
                if is_out_daily:
                    code_outside_daily_counter[code] += 1
                if is_out_1m:
                    code_outside_1m_counter[code] += 1

        if idx % 25 == 0 or idx == total_rows:
            print(
                json.dumps(
                    {
                        "stage": "sample_recompute",
                        "sample_done": idx,
                        "sample_total": total_rows,
                    },
                    ensure_ascii=False,
                )
            )

    raw_metrics = pd.DataFrame(metrics_rows)
    raw_metrics["acceptance_label"] = raw_metrics.apply(classify_acceptance, axis=1)
    condition_combo_summary = pd.DataFrame([{"conditions_key": k, "trades": v} for k, v in condition_counter.items()]).sort_values(["trades", "conditions_key"], ascending=[False, True]).reset_index(drop=True)
    if not condition_combo_summary.empty:
        condition_combo_summary["outside_daily_trades"] = condition_combo_summary["conditions_key"].map(combo_outside_daily_counter).fillna(0).astype(int)
        condition_combo_summary["outside_1m_trades"] = condition_combo_summary["conditions_key"].map(combo_outside_1m_counter).fillna(0).astype(int)
        condition_combo_summary["trade_pct"] = 100 * condition_combo_summary["trades"] / max(int(condition_combo_summary["trades"].sum()), 1)
        condition_combo_summary["outside_daily_pct_within_combo"] = 100 * condition_combo_summary["outside_daily_trades"] / condition_combo_summary["trades"].clip(lower=1)
        condition_combo_summary["outside_1m_pct_within_combo"] = 100 * condition_combo_summary["outside_1m_trades"] / condition_combo_summary["trades"].clip(lower=1)
    condition_code_summary = pd.DataFrame([{"condition_code": int(k), "trades": v} for k, v in condition_code_counter.items()])
    if not condition_code_summary.empty:
        condition_code_summary = condition_code_summary.sort_values(["trades", "condition_code"], ascending=[False, True]).reset_index(drop=True)
    if not condition_code_summary.empty:
        condition_code_summary["outside_daily_trades"] = condition_code_summary["condition_code"].map(code_outside_daily_counter).fillna(0).astype(int)
        condition_code_summary["outside_1m_trades"] = condition_code_summary["condition_code"].map(code_outside_1m_counter).fillna(0).astype(int)
        condition_code_summary["trade_pct"] = 100 * condition_code_summary["trades"] / max(int(condition_code_summary["trades"].sum()), 1)
        condition_code_summary["outside_daily_pct_within_code"] = 100 * condition_code_summary["outside_daily_trades"] / condition_code_summary["trades"].clip(lower=1)
        condition_code_summary["outside_1m_pct_within_code"] = 100 * condition_code_summary["outside_1m_trades"] / condition_code_summary["trades"].clip(lower=1)

    session_profile = pd.DataFrame(
        [
            {"metric": "median_premarket_trade_pct", "value": pd.to_numeric(raw_metrics["premarket_trade_pct"], errors="coerce").median()},
            {"metric": "median_regular_trade_pct_raw", "value": pd.to_numeric(raw_metrics["regular_trade_pct"], errors="coerce").median()},
            {"metric": "median_afterhours_trade_pct", "value": pd.to_numeric(raw_metrics["afterhours_trade_pct"], errors="coerce").median()},
            {"metric": "median_off_session_trade_pct_raw", "value": pd.to_numeric(raw_metrics["off_session_trade_pct"], errors="coerce").median()},
            {"metric": "files_with_off_session_gt_0_pct_raw", "value": 100 * (pd.to_numeric(raw_metrics["off_session_trade_pct"], errors="coerce") > 0).mean()},
            {"metric": "median_odd_lot_trade_pct", "value": pd.to_numeric(raw_metrics["odd_lot_trade_pct"], errors="coerce").median()},
            {"metric": "median_round_lot_trade_pct", "value": pd.to_numeric(raw_metrics["round_lot_trade_pct"], errors="coerce").median()},
            {"metric": "median_outside_daily_premarket_pct", "value": pd.to_numeric(raw_metrics["outside_daily_premarket_pct"], errors="coerce").median()},
            {"metric": "median_outside_daily_regular_pct", "value": pd.to_numeric(raw_metrics["outside_daily_regular_pct"], errors="coerce").median()},
            {"metric": "median_outside_daily_afterhours_pct", "value": pd.to_numeric(raw_metrics["outside_daily_afterhours_pct"], errors="coerce").median()},
            {"metric": "median_outside_1m_premarket_pct", "value": pd.to_numeric(raw_metrics["outside_1m_premarket_pct"], errors="coerce").median()},
            {"metric": "median_outside_1m_regular_pct", "value": pd.to_numeric(raw_metrics["outside_1m_regular_pct"], errors="coerce").median()},
            {"metric": "median_outside_1m_afterhours_pct", "value": pd.to_numeric(raw_metrics["outside_1m_afterhours_pct"], errors="coerce").median()},
            {"metric": "median_outside_daily_odd_lot_pct", "value": pd.to_numeric(raw_metrics["outside_daily_odd_lot_pct"], errors="coerce").median()},
            {"metric": "median_outside_daily_round_lot_pct", "value": pd.to_numeric(raw_metrics["outside_daily_round_lot_pct"], errors="coerce").median()},
            {"metric": "median_outside_1m_odd_lot_pct", "value": pd.to_numeric(raw_metrics["outside_1m_odd_lot_pct"], errors="coerce").median()},
            {"metric": "median_outside_1m_round_lot_pct", "value": pd.to_numeric(raw_metrics["outside_1m_round_lot_pct"], errors="coerce").median()},
        ]
    )
    mismatch = sample_index[["file", "m.off_session_trade_pct"]].merge(raw_metrics[["file", "off_session_trade_pct"]], on="file", how="inner")
    mismatch["legacy_minus_raw_off_session_pct"] = pd.to_numeric(mismatch["m.off_session_trade_pct"], errors="coerce") - pd.to_numeric(mismatch["off_session_trade_pct"], errors="coerce")
    mismatch = mismatch.sort_values("legacy_minus_raw_off_session_pct", ascending=False).reset_index(drop=True)
    return raw_metrics, condition_combo_summary, condition_code_summary, session_profile, mismatch


def build_layer_summaries(raw_metrics: pd.DataFrame) -> dict[str, pd.DataFrame]:
    layer2 = pd.DataFrame(
        [
            {"metric": "sample_files", "value": len(raw_metrics)},
            {"metric": "median_regular_trade_pct", "value": pd.to_numeric(raw_metrics["regular_trade_pct"], errors="coerce").median()},
            {"metric": "median_prepost_trade_pct", "value": pd.to_numeric(raw_metrics["prepost_trade_pct"], errors="coerce").median()},
            {"metric": "median_baseline_eligible_trade_pct", "value": pd.to_numeric(raw_metrics["baseline_eligible_trade_pct"], errors="coerce").median()},
            {"metric": "files_with_1m_reference_pct", "value": 100 * pd.to_numeric(raw_metrics["has_1m_reference"], errors="coerce").mean()},
            {"metric": "files_with_daily_reference_pct", "value": 100 * pd.to_numeric(raw_metrics["has_daily_reference"], errors="coerce").mean()},
        ]
    )

    layer3 = pd.DataFrame(
        [
            {"metric": "median_duplicate_exact_ratio_pct_raw", "value": pd.to_numeric(raw_metrics["duplicate_exact_ratio_pct_raw"], errors="coerce").median()},
            {"metric": "p95_duplicate_exact_ratio_pct_raw", "value": pd.to_numeric(raw_metrics["duplicate_exact_ratio_pct_raw"], errors="coerce").quantile(0.95)},
            {"metric": "median_max_trades_same_timestamp_raw", "value": pd.to_numeric(raw_metrics["max_trades_same_timestamp_raw"], errors="coerce").median()},
            {"metric": "median_condition_combo_nunique", "value": pd.to_numeric(raw_metrics["condition_combo_nunique"], errors="coerce").median()},
        ]
    )

    layer4 = pd.DataFrame(
        [
            {"metric": "median_outside_daily_pct", "value": pd.to_numeric(raw_metrics["outside_daily_pct"], errors="coerce").median()},
            {"metric": "median_outside_daily_regular_pct", "value": pd.to_numeric(raw_metrics["outside_daily_regular_pct"], errors="coerce").median()},
            {"metric": "median_outside_daily_volume_pct", "value": pd.to_numeric(raw_metrics["outside_daily_volume_pct"], errors="coerce").median()},
            {"metric": "median_outside_1m_pct", "value": pd.to_numeric(raw_metrics["outside_1m_pct"], errors="coerce").median()},
            {"metric": "median_outside_1m_regular_pct", "value": pd.to_numeric(raw_metrics["outside_1m_regular_pct"], errors="coerce").median()},
            {"metric": "median_trade_vwap_vs_daily_vw_diff_pct_raw", "value": pd.to_numeric(raw_metrics["trade_vwap_vs_daily_vw_diff_pct_raw"], errors="coerce").median()},
        ]
    )

    layer5 = pd.DataFrame(
        [
            {"metric": "median_outside_minutes_pct_active", "value": pd.to_numeric(raw_metrics["outside_minutes_pct_active"], errors="coerce").median()},
            {"metric": "median_longest_outside_run_minutes", "value": pd.to_numeric(raw_metrics["longest_outside_run_minutes"], errors="coerce").median()},
            {"metric": "median_top_outside_minute_trade_share_pct", "value": pd.to_numeric(raw_metrics["top_outside_minute_trade_share_pct"], errors="coerce").median()},
            {"metric": "median_top_outside_minute_volume_share_pct", "value": pd.to_numeric(raw_metrics["top_outside_minute_volume_share_pct"], errors="coerce").median()},
            {"metric": "median_outside_daily_prepost_pct", "value": pd.to_numeric(raw_metrics["outside_daily_prepost_pct"], errors="coerce").median()},
        ]
    )

    layer6 = raw_metrics.groupby("acceptance_label", observed=False).agg(
        files=("file", "size"),
        median_outside_daily_regular_pct=("outside_daily_regular_pct", "median"),
        median_outside_daily_regular_volume_pct=("outside_daily_regular_volume_pct", "median"),
        median_outside_1m_regular_pct=("outside_1m_regular_pct", "median"),
        median_outside_minutes_pct_active=("outside_minutes_pct_active", "median"),
        median_trade_vwap_vs_daily_vw_diff_pct_raw=("trade_vwap_vs_daily_vw_diff_pct_raw", "median"),
    ).reset_index().sort_values("files", ascending=False)

    return {
        "layer2_eligibility_summary": layer2,
        "layer3_tape_quality_summary": layer3,
        "layer4_reference_consistency_summary": layer4,
        "layer5_severity_real_summary": layer5,
        "layer6_policy_summary": layer6,
    }


def build_file_acceptance_artifacts_lt1b(
    current_parquet: Path = CURRENT_PARQUET_CD,
    target_lt1b_path: Path = TARGET_LT1B_PATH,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    batch_size: int = 50_000,
    sample_per_stratum: int = 20,
    max_batches: int | None = None,
) -> dict:
    base_dir = Path(__file__).resolve().parent
    mod00 = runpy.run_path(str(base_dir / "00_load_trades_run_artifacts.py"))
    handle = mod00["make_trades_audit_handle"](current_parquet)
    target_tickers = load_target_lt1b_tickers(target_lt1b_path)

    cache_dir.mkdir(parents=True, exist_ok=True)

    integrity_summary, integrity_examples, sample_index = compute_layer1_artifacts(
        handle=handle,
        target_tickers=target_tickers,
        batch_size=batch_size,
        sample_per_stratum=sample_per_stratum,
        max_batches=max_batches,
    )
    raw_metrics, condition_combo_summary, condition_code_summary, layer2_session_profile, layer2_session_mismatch = build_sample_artifacts(sample_index)
    summaries = build_layer_summaries(raw_metrics)

    _write_df(integrity_summary, cache_dir / "layer1_integrity_summary.parquet")
    _write_df(integrity_examples, cache_dir / "layer1_integrity_examples.parquet")
    _write_df(sample_index, cache_dir / "sample_index.parquet")
    _write_df(raw_metrics, cache_dir / "raw_file_metrics.parquet")
    _write_df(condition_combo_summary, cache_dir / "condition_combo_summary.parquet")
    _write_df(condition_code_summary, cache_dir / "condition_code_summary.parquet")
    _write_df(layer2_session_profile, cache_dir / "layer2_session_profile.parquet")
    _write_df(layer2_session_mismatch, cache_dir / "layer2_session_mismatch.parquet")
    for name, df in summaries.items():
        _write_df(df, cache_dir / f"{name}.parquet")

    policy_examples = raw_metrics.sort_values(["acceptance_label", "outside_daily_regular_pct", "outside_1m_regular_pct"], ascending=[True, False, False]).reset_index(drop=True)
    _write_df(policy_examples, cache_dir / "layer6_policy_examples.parquet")

    manifest = {
        "built_at_utc": _utcnow_iso(),
        "current_parquet": str(current_parquet),
        "target_lt1b_path": str(target_lt1b_path),
        "target_tickers": int(len(target_tickers)),
        "cache_dir": str(cache_dir),
        "batch_size": batch_size,
        "sample_per_stratum": sample_per_stratum,
        "max_batches": max_batches,
        "files_total": int(integrity_summary.loc[integrity_summary["metric"] == "files_total", "value"].iloc[0]),
        "sample_files": int(len(sample_index)),
        "artifacts": sorted([p.name for p in cache_dir.glob("*.parquet")]),
    }
    (cache_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-parquet", type=Path, default=CURRENT_PARQUET_CD)
    parser.add_argument("--target-lt1b-path", type=Path, default=TARGET_LT1B_PATH)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--batch-size", type=int, default=50_000)
    parser.add_argument("--sample-per-stratum", type=int, default=20)
    parser.add_argument("--max-batches", type=int, default=None)
    args = parser.parse_args()

    manifest = build_file_acceptance_artifacts_lt1b(
        current_parquet=args.current_parquet,
        target_lt1b_path=args.target_lt1b_path,
        cache_dir=args.cache_dir,
        batch_size=args.batch_size,
        sample_per_stratum=args.sample_per_stratum,
        max_batches=args.max_batches,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
