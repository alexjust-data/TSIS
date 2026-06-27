from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


QUOTE_GUARDED_VIEW_NAME = "ohlcv_1m_quote_guarded_v0_1"
NY_TZ = "America/New_York"


@dataclass(frozen=True)
class QuoteGuardConfig:
    bid_quantile: float = 0.01
    ask_quantile: float = 0.99
    tolerance_pct: float = 0.003
    abs_tolerance: float = 0.0001
    min_quote_count: int = 3


def to_utc_datetime(series: pd.Series) -> pd.Series:
    """Parse vendor timestamps as UTC, including epoch ns/us/ms/s integers."""
    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")
        finite = numeric[np.isfinite(numeric)]
        unit = "ns"
        if not finite.empty:
            median_abs = float(finite.abs().median())
            if median_abs < 1e11:
                unit = "s"
            elif median_abs < 1e14:
                unit = "ms"
            elif median_abs < 1e17:
                unit = "us"
        return pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    return pd.to_datetime(series, utc=True, errors="coerce")


def build_quote_minute_envelope(
    quotes: pd.DataFrame,
    *,
    timestamp_col: str = "timestamp",
    bid_col: str = "bid_price",
    ask_col: str = "ask_price",
    config: QuoteGuardConfig | None = None,
    max_spread_pct: float | None = None,
) -> pd.DataFrame:
    """
    Build a conservative minute-level quote envelope.

    The envelope is not declared NBBO. It is a robust bid/ask context derived
    from available quote observations for the same ticker-minute.
    """
    cfg = config or QuoteGuardConfig()
    required = {timestamp_col, bid_col, ask_col}
    missing = required - set(quotes.columns)
    if missing:
        raise ValueError(f"quotes missing required columns: {sorted(missing)}")

    frame = quotes[[timestamp_col, bid_col, ask_col]].copy()
    frame["quote_ts_utc"] = to_utc_datetime(frame[timestamp_col])
    frame["bid_price"] = pd.to_numeric(frame[bid_col], errors="coerce")
    frame["ask_price"] = pd.to_numeric(frame[ask_col], errors="coerce")
    frame = frame.loc[
        frame["quote_ts_utc"].notna()
        & frame["bid_price"].gt(0)
        & frame["ask_price"].gt(0)
        & frame["bid_price"].le(frame["ask_price"])
    ].copy()
    if frame.empty:
        return _empty_envelope()

    frame["mid"] = (frame["bid_price"] + frame["ask_price"]) / 2.0
    frame["spread"] = frame["ask_price"] - frame["bid_price"]
    frame["spread_pct"] = np.where(frame["mid"].gt(0), frame["spread"] / frame["mid"], np.nan)
    if max_spread_pct is not None:
        frame = frame.loc[frame["spread_pct"].le(float(max_spread_pct))].copy()
    if frame.empty:
        return _empty_envelope()

    frame["minute_ny"] = frame["quote_ts_utc"].dt.tz_convert(NY_TZ).dt.floor("min")
    grouped = frame.groupby("minute_ny", dropna=False)
    out = grouped.agg(
        quote_bid_floor=("bid_price", lambda s: float(s.quantile(cfg.bid_quantile))),
        quote_bid_p50=("bid_price", "median"),
        quote_ask_p50=("ask_price", "median"),
        quote_ask_cap=("ask_price", lambda s: float(s.quantile(cfg.ask_quantile))),
        quote_mid_p50=("mid", "median"),
        quote_spread_p50=("spread", "median"),
        quote_spread_pct_p50=("spread_pct", "median"),
        quote_count=("bid_price", "size"),
    ).reset_index()
    out["minute_utc"] = out["minute_ny"].dt.tz_convert("UTC")
    out["session_date"] = out["minute_ny"].dt.date.astype(str)
    return out[
        [
            "minute_ny",
            "minute_utc",
            "session_date",
            "quote_bid_floor",
            "quote_bid_p50",
            "quote_ask_p50",
            "quote_ask_cap",
            "quote_mid_p50",
            "quote_spread_p50",
            "quote_spread_pct_p50",
            "quote_count",
        ]
    ].copy()


def detect_quote_guarded_repairs(
    minute_bars: pd.DataFrame,
    quote_envelope: pd.DataFrame,
    *,
    config: QuoteGuardConfig | None = None,
    ticker: str | None = None,
    source_ohlcv_path: str = "",
    source_quotes_path_col: str | None = None,
) -> pd.DataFrame:
    cfg = config or QuoteGuardConfig()
    if minute_bars.empty or quote_envelope.empty:
        return _empty_repairs()
    if "ts_utc" not in minute_bars.columns:
        raise ValueError("minute_bars must include ts_utc")

    bars = minute_bars.copy()
    bars["minute_utc"] = to_utc_datetime(bars["ts_utc"]).dt.floor("min")
    bars["minute_ny"] = bars["minute_utc"].dt.tz_convert(NY_TZ)
    bars["session_date"] = bars["minute_ny"].dt.date.astype(str)
    for col in ("o", "h", "l", "c", "vw", "v", "n"):
        if col in bars.columns:
            bars[col] = pd.to_numeric(bars[col], errors="coerce")

    env_cols = [
        "minute_ny",
        "quote_bid_floor",
        "quote_bid_p50",
        "quote_ask_p50",
        "quote_ask_cap",
        "quote_mid_p50",
        "quote_spread_p50",
        "quote_spread_pct_p50",
        "quote_count",
    ]
    if source_quotes_path_col and source_quotes_path_col in quote_envelope.columns:
        env_cols.append(source_quotes_path_col)
    merged = bars.merge(quote_envelope[env_cols], on="minute_ny", how="left", validate="many_to_one")
    matched = merged["quote_count"].ge(cfg.min_quote_count)
    upper = merged["quote_ask_cap"] * (1.0 + cfg.tolerance_pct) + cfg.abs_tolerance
    lower = merged["quote_bid_floor"] * (1.0 - cfg.tolerance_pct) - cfg.abs_tolerance

    o_bad = matched & (merged["o"].gt(upper) | merged["o"].lt(lower))
    h_bad = matched & merged["h"].gt(upper)
    l_bad = matched & merged["l"].lt(lower)
    c_bad = matched & (merged["c"].gt(upper) | merged["c"].lt(lower))
    vw_bad = pd.Series(False, index=merged.index)
    if "vw" in merged.columns:
        vw_bad = matched & merged["vw"].notna() & (
            merged["vw"].gt(upper)
            | merged["vw"].lt(lower)
            | merged["vw"].gt(merged["h"])
            | merged["vw"].lt(merged["l"])
        )
    repair_mask = o_bad | h_bad | l_bad | c_bad
    out = merged.loc[repair_mask | vw_bad].copy()
    if out.empty:
        return _empty_repairs()

    for col in ("o", "h", "l", "c"):
        out[f"{col}_raw"] = out[col]
        out[f"{col}_qg"] = out[col].clip(lower=out["quote_bid_floor"], upper=out["quote_ask_cap"])

    out["h_qg"] = pd.concat([out["h_qg"], out["o_qg"], out["c_qg"]], axis=1).max(axis=1)
    out["l_qg"] = pd.concat([out["l_qg"], out["o_qg"], out["c_qg"]], axis=1).min(axis=1)
    out["quote_guarded_repair_applied"] = repair_mask.loc[out.index].astype(bool).to_numpy()
    out["vw_quote_guarded_status"] = np.where(
        vw_bad.loc[out.index].to_numpy(),
        "invalid_not_repaired_from_quotes",
        "raw_preserved",
    )
    out["repair_state"] = np.select(
        [
            out["quote_guarded_repair_applied"] & (out["vw_quote_guarded_status"] == "invalid_not_repaired_from_quotes"),
            out["quote_guarded_repair_applied"],
            out["vw_quote_guarded_status"] == "invalid_not_repaired_from_quotes",
        ],
        [
            "quote_repairable_ohlc_vw_invalid",
            "quote_repairable_ohlc",
            "vw_invalid_only",
        ],
        default="clean_no_repair",
    )
    out["repair_reason"] = [
        _repair_reason(bool(o_bad.loc[idx]), bool(h_bad.loc[idx]), bool(l_bad.loc[idx]), bool(c_bad.loc[idx]), bool(vw_bad.loc[idx]))
        for idx in out.index
    ]
    out["quote_guarded_view"] = QUOTE_GUARDED_VIEW_NAME
    out["quote_guard_config"] = (
        f"bid_q={cfg.bid_quantile};ask_q={cfg.ask_quantile};"
        f"tol_pct={cfg.tolerance_pct};abs_tol={cfg.abs_tolerance};"
        f"min_quote_count={cfg.min_quote_count}"
    )
    out["source_ohlcv_path"] = source_ohlcv_path
    if source_quotes_path_col and source_quotes_path_col in out.columns:
        out["source_quotes_path"] = out[source_quotes_path_col].astype(str)
    else:
        out["source_quotes_path"] = ""
    if ticker is not None:
        out["ticker"] = ticker.upper()
    elif "ticker" in out.columns:
        out["ticker"] = out["ticker"].astype(str).str.upper()

    columns = [
        "quote_guarded_view",
        "ticker",
        "ts_utc",
        "minute_utc",
        "minute_ny",
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
        "quote_bid_p50",
        "quote_ask_p50",
        "quote_ask_cap",
        "quote_mid_p50",
        "quote_spread_p50",
        "quote_spread_pct_p50",
        "quote_count",
        "quote_guard_config",
        "source_ohlcv_path",
        "source_quotes_path",
    ]
    for col in columns:
        if col not in out.columns:
            out[col] = np.nan
    return out[columns].reset_index(drop=True)


def apply_quote_guarded_repairs(
    minute_bars: pd.DataFrame,
    repair_manifest: pd.DataFrame,
    *,
    preserve_raw: bool = True,
    price_cols: Sequence[str] = ("o", "h", "l", "c"),
) -> pd.DataFrame:
    """Apply a quote-guarded repair manifest to an in-memory 1m dataframe."""
    out = minute_bars.copy()
    if out.empty or repair_manifest.empty:
        out["quote_guarded_repair_applied"] = False
        out["quote_guarded_view"] = QUOTE_GUARDED_VIEW_NAME
        return out
    if "ts_utc" not in out.columns or "ts_utc" not in repair_manifest.columns:
        raise ValueError("minute_bars and repair_manifest must include ts_utc")

    out["_qg_key"] = to_utc_datetime(out["ts_utc"]).dt.floor("min")
    repairs = repair_manifest.copy()
    repairs["_qg_key"] = to_utc_datetime(repairs["ts_utc"]).dt.floor("min")
    if "ticker" in out.columns and "ticker" in repairs.columns:
        out["_qg_ticker"] = out["ticker"].astype(str).str.upper()
        repairs["_qg_ticker"] = repairs["ticker"].astype(str).str.upper()
        key_cols = ["_qg_ticker", "_qg_key"]
    else:
        key_cols = ["_qg_key"]

    repair_cols = key_cols + [f"{col}_qg" for col in price_cols if f"{col}_qg" in repairs.columns]
    repair_cols += ["repair_state", "repair_reason", "vw_quote_guarded_status"]
    repair_cols = list(dict.fromkeys([c for c in repair_cols if c in repairs.columns]))
    merged = out.merge(repairs[repair_cols], on=key_cols, how="left", validate="many_to_one")
    applied = merged["repair_state"].notna() & merged["repair_state"].astype(str).str.contains("ohlc", na=False)
    for col in price_cols:
        qg_col = f"{col}_qg"
        if qg_col not in merged.columns:
            continue
        if preserve_raw and f"{col}_raw" not in merged.columns:
            merged[f"{col}_raw"] = merged[col]
        merged[col] = np.where(applied & merged[qg_col].notna(), merged[qg_col], merged[col])
    merged["quote_guarded_repair_applied"] = applied.astype(bool)
    merged["quote_guarded_view"] = QUOTE_GUARDED_VIEW_NAME
    drop_cols = ["_qg_key", "_qg_ticker", *[f"{col}_qg" for col in price_cols]]
    return merged.drop(columns=[c for c in drop_cols if c in merged.columns])


def load_quote_guarded_ohlcv_month(
    minute_path: Path,
    repair_manifest_path: Path,
    *,
    preserve_raw: bool = True,
) -> pd.DataFrame:
    frame = pd.read_parquet(minute_path)
    if not repair_manifest_path.exists():
        return apply_quote_guarded_repairs(frame, pd.DataFrame(), preserve_raw=preserve_raw)
    manifest = pd.read_parquet(repair_manifest_path)
    return apply_quote_guarded_repairs(frame, manifest, preserve_raw=preserve_raw)


def _repair_reason(o_bad: bool, h_bad: bool, l_bad: bool, c_bad: bool, vw_bad: bool) -> str:
    reasons: list[str] = []
    if o_bad:
        reasons.append("open_outside_quote_envelope")
    if h_bad:
        reasons.append("high_above_quote_ask_cap")
    if l_bad:
        reasons.append("low_below_quote_bid_floor")
    if c_bad:
        reasons.append("close_outside_quote_envelope")
    if vw_bad:
        reasons.append("vw_invalid_against_quote_or_raw_ohlc")
    return "|".join(reasons)


def _empty_envelope() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "minute_ny",
            "minute_utc",
            "session_date",
            "quote_bid_floor",
            "quote_bid_p50",
            "quote_ask_p50",
            "quote_ask_cap",
            "quote_mid_p50",
            "quote_spread_p50",
            "quote_spread_pct_p50",
            "quote_count",
        ]
    )


def _empty_repairs() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "quote_guarded_view",
            "ticker",
            "ts_utc",
            "minute_utc",
            "minute_ny",
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
            "quote_bid_p50",
            "quote_ask_p50",
            "quote_ask_cap",
            "quote_mid_p50",
            "quote_spread_p50",
            "quote_spread_pct_p50",
            "quote_count",
            "quote_guard_config",
            "source_ohlcv_path",
            "source_quotes_path",
        ]
    )
