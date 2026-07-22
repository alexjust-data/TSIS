from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeaturesConfig:
    raw_root: Path
    normalized_root: Path
    output_root: Path
    overwrite: bool


def _iter_ticker_dirs(root: Path, tickers: set[str] | None = None) -> Iterable[Path]:
    for p in sorted(root.glob("ticker=*")):
        if not p.is_dir():
            continue
        ticker = p.name.replace("ticker=", "", 1).upper()
        if tickers and ticker not in tickers:
            continue
        yield p


def _iter_normalized_files(ticker_dir: Path) -> Iterable[Path]:
    yield from sorted(ticker_dir.rglob("*_split_normalized.parquet"))


def _raw_path_for(normalized_root: Path, raw_root: Path, normalized_path: Path) -> Path:
    rel = normalized_path.relative_to(normalized_root)
    raw_name = rel.name.replace("_split_normalized.parquet", ".parquet")
    return raw_root / rel.parent / raw_name


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    v = pd.to_numeric(values, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce")
    mask = v.notna() & w.notna() & (w > 0)
    if not mask.any():
        return float(v.mean()) if v.notna().any() else np.nan
    return float(np.average(v[mask], weights=w[mask]))


def _safe_ratio(num: pd.Series | float, den: pd.Series | float) -> pd.Series | float:
    num_s = pd.Series(num) if not isinstance(num, pd.Series) else num
    den_s = pd.Series(den) if not isinstance(den, pd.Series) else den
    out = pd.Series(np.nan, index=num_s.index, dtype="float64")
    mask = den_s.notna() & (den_s != 0) & num_s.notna()
    out.loc[mask] = num_s.loc[mask] / den_s.loc[mask]
    return out if isinstance(num, pd.Series) or isinstance(den, pd.Series) else float(out.iloc[0])


def _session_stats_raw(group: pd.DataFrame) -> pd.Series:
    g = group.sort_values("ts_utc").reset_index(drop=True)
    first_open = pd.to_numeric(g["o"], errors="coerce").iloc[0]
    last_close = pd.to_numeric(g["c"], errors="coerce").iloc[-1]
    session_high = pd.to_numeric(g["h"], errors="coerce").max()
    session_low = pd.to_numeric(g["l"], errors="coerce").min()
    volume = pd.to_numeric(g["v"], errors="coerce").sum()
    session_vwap = _weighted_mean(g["vw"], g["v"])

    opening_window = g.iloc[:30].copy()
    opening_drive_close = pd.to_numeric(opening_window["c"], errors="coerce").iloc[-1]

    return pd.Series(
        {
            "ticker": str(g["ticker"].iloc[0]),
            "bar_count_raw": int(len(g)),
            "open_raw": first_open,
            "close_raw": last_close,
            "high_raw": session_high,
            "low_raw": session_low,
            "cum_volume_session_raw": volume,
            "session_vwap_raw": session_vwap,
            "intraday_return_since_open_raw": (last_close / first_open - 1.0) if pd.notna(first_open) and first_open != 0 else np.nan,
            "session_range_pct_raw": ((session_high - session_low) / first_open) if pd.notna(first_open) and first_open != 0 else np.nan,
            "opening_drive_30m_raw": (opening_drive_close / first_open - 1.0) if pd.notna(first_open) and first_open != 0 else np.nan,
            "pullback_from_session_high_raw": (last_close / session_high - 1.0) if pd.notna(session_high) and session_high != 0 else np.nan,
            "session_vwap_distance_raw": (last_close / session_vwap - 1.0) if pd.notna(session_vwap) and session_vwap != 0 else np.nan,
        }
    )


def _session_stats_normalized(group: pd.DataFrame) -> pd.Series:
    g = group.sort_values("ts_utc").reset_index(drop=True)
    close_norm = pd.to_numeric(g["c_split_normalized"], errors="coerce")
    open_norm = pd.to_numeric(g["o_split_normalized"], errors="coerce").iloc[0]
    close_last = close_norm.iloc[-1]
    high_norm = pd.to_numeric(g["h_split_normalized"], errors="coerce").max()
    low_norm = pd.to_numeric(g["l_split_normalized"], errors="coerce").min()
    factor = pd.to_numeric(g["future_split_factor"], errors="coerce").max()
    log_rets = np.log(close_norm / close_norm.shift(1))
    realized_vol = float(np.sqrt(np.nansum(np.square(log_rets.to_numpy(dtype="float64")))))

    return pd.Series(
        {
            "open_norm": open_norm,
            "close_norm": close_last,
            "high_norm": high_norm,
            "low_norm": low_norm,
            "session_range_abs_norm": (high_norm - low_norm) if pd.notna(high_norm) and pd.notna(low_norm) else np.nan,
            "realized_vol_1d_norm": realized_vol,
            "max_future_split_factor_in_day": factor,
        }
    )


def _daily_raw_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    out = (
        df.groupby("date", sort=True, as_index=False)
        .apply(_session_stats_raw, include_groups=False)
        .reset_index(drop=True)
    )
    return out


def _daily_normalized_features(norm_df: pd.DataFrame) -> pd.DataFrame:
    df = norm_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    out = (
        df.groupby("date", sort=True, as_index=False)
        .apply(_session_stats_normalized, include_groups=False)
        .reset_index(drop=True)
    )
    return out


def _build_cross_session_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values("date").reset_index(drop=True).copy()

    prev_close = out["close_norm"].shift(1)
    prev_high = out["high_norm"].shift(1)
    prev_low = out["low_norm"].shift(1)
    prev_range = out["session_range_abs_norm"].shift(1)
    prev_range_center = (prev_high + prev_low) / 2.0

    gap = _safe_ratio(out["open_norm"], prev_close) - 1.0
    out["gap_open_vs_prev_close"] = gap
    out["open_vs_prev_session_close"] = gap
    out["open_vs_prev_session_high"] = _safe_ratio(out["open_norm"], prev_high) - 1.0
    out["open_vs_prev_session_low"] = _safe_ratio(out["open_norm"], prev_low) - 1.0
    out["multi_session_return_3d_to_open"] = _safe_ratio(out["open_norm"], out["close_norm"].shift(3)) - 1.0
    out["multi_session_return_5d_to_open"] = _safe_ratio(out["open_norm"], out["close_norm"].shift(5)) - 1.0
    out["distance_to_prev_day_range_center"] = _safe_ratio(out["open_norm"], prev_range_center) - 1.0
    out["prev_day_range_pct_norm"] = _safe_ratio(prev_high - prev_low, prev_close)
    out["range_expansion_vs_prev_day_norm"] = _safe_ratio(out["session_range_abs_norm"], prev_range) - 1.0

    prev_5d_high = out["high_norm"].shift(1).rolling(5, min_periods=2).max()
    prev_5d_low = out["low_norm"].shift(1).rolling(5, min_periods=2).min()
    out["distance_to_n_day_high_5"] = _safe_ratio(out["open_norm"], prev_5d_high) - 1.0
    out["distance_to_n_day_low_5"] = _safe_ratio(out["open_norm"], prev_5d_low) - 1.0

    out["realized_vol_prev_3_sessions_norm"] = out["realized_vol_1d_norm"].shift(1).rolling(3, min_periods=1).mean()
    gap_mean = gap.shift(1).rolling(20, min_periods=5).mean()
    gap_std = gap.shift(1).rolling(20, min_periods=5).std()
    out["overnight_gap_zscore_20"] = (gap - gap_mean) / gap_std.replace(0, np.nan)
    return out


def _merge_feature_families(raw_df: pd.DataFrame, norm_df: pd.DataFrame) -> pd.DataFrame:
    raw_daily = _daily_raw_features(raw_df)
    norm_daily = _daily_normalized_features(norm_df)
    if raw_daily.empty or norm_daily.empty:
        return pd.DataFrame()

    out = raw_daily.merge(norm_daily, on="date", how="inner")
    out = _build_cross_session_features(out)
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["year"] = out["date"].dt.year.astype("Int64")
    out["feature_contract"] = "intraday_regime_features_v0_1"
    out["feature_grain"] = "ticker_day"
    out["cross_session_price_view"] = "1m_split_normalized_v0_1"
    out["intraday_price_view"] = "1m_raw"
    return out


def _output_path(output_root: Path, ticker: str, year: int) -> Path:
    return output_root / f"ticker={ticker}" / f"year={year}" / f"day_features_{ticker}_{year}.parquet"


def _load_ticker_frames(ticker_dir: Path, cfg: FeaturesConfig) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    raw_frames: list[pd.DataFrame] = []
    norm_frames: list[pd.DataFrame] = []
    files_seen = 0

    for norm_path in _iter_normalized_files(ticker_dir):
        files_seen += 1
        raw_path = _raw_path_for(cfg.normalized_root, cfg.raw_root, norm_path)
        if not raw_path.exists():
            raise FileNotFoundError(f"Missing raw 1m source for normalized file: {raw_path}")
        norm_frames.append(pd.read_parquet(norm_path))
        raw_frames.append(pd.read_parquet(raw_path))

    raw_df = pd.concat(raw_frames, ignore_index=True) if raw_frames else pd.DataFrame()
    norm_df = pd.concat(norm_frames, ignore_index=True) if norm_frames else pd.DataFrame()
    return raw_df, norm_df, files_seen


def materialize_ticker(ticker_dir: Path, cfg: FeaturesConfig) -> dict[str, int | str]:
    ticker = ticker_dir.name.replace("ticker=", "", 1).upper()
    raw_df, norm_df, files_seen = _load_ticker_frames(ticker_dir, cfg)
    if raw_df.empty or norm_df.empty:
        return {
            "ticker": ticker,
            "files_seen": files_seen,
            "years_written": 0,
            "days_written": 0,
        }

    features = _merge_feature_families(raw_df, norm_df)
    years_written = 0
    days_written = 0

    for year, year_df in features.groupby("year", dropna=True):
        if pd.isna(year):
            continue
        out_path = _output_path(cfg.output_root, ticker, int(year))
        if out_path.exists() and not cfg.overwrite:
            continue
        year_df = year_df.sort_values("date").reset_index(drop=True).copy()
        year_df["source_raw_root"] = str(cfg.raw_root)
        year_df["source_split_normalized_root"] = str(cfg.normalized_root)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        year_df.to_parquet(out_path, index=False)
        years_written += 1
        days_written += int(len(year_df))

    return {
        "ticker": ticker,
        "files_seen": files_seen,
        "years_written": years_written,
        "days_written": days_written,
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Materializa `intraday_regime_features` a grano ticker-day desde `1m raw` y `1m_split_normalized`."
    )
    ap.add_argument("--raw-root", required=True)
    ap.add_argument("--normalized-root", required=True)
    ap.add_argument("--output-root", required=True)
    ap.add_argument("--tickers", nargs="*", default=None)
    ap.add_argument("--limit-tickers", type=int, default=None)
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    tickers = {t.upper() for t in args.tickers} if args.tickers else None
    cfg = FeaturesConfig(
        raw_root=Path(args.raw_root),
        normalized_root=Path(args.normalized_root),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )

    ticker_dirs = list(_iter_ticker_dirs(cfg.normalized_root, tickers=tickers))
    if args.limit_tickers is not None:
        ticker_dirs = ticker_dirs[: int(args.limit_tickers)]

    rows: list[dict[str, int | str]] = []
    for ticker_dir in ticker_dirs:
        rows.append(materialize_ticker(ticker_dir, cfg))

    if rows:
        summary = pd.DataFrame(rows)
        cfg.output_root.mkdir(parents=True, exist_ok=True)
        summary.to_csv(cfg.output_root / "_intraday_regime_features_materialization_summary.csv", index=False)
        print(summary.to_string(index=False))
    else:
        print("No ticker directories selected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
