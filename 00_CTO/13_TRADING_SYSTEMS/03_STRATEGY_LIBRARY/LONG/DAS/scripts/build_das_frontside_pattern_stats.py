from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BUILDER_ID = "build_das_frontside_pattern_stats"
BUILDER_VERSION = "0.1.0"
OUTPUT_DIRNAME = "frontside_pattern_stats"
REPORT_NAME = "DAS_FRONTSIDE_PATTERN_STATS_REPORT_v0_1.md"
CASES_BASENAME = "frontside_pattern_cases"
NY_TZ = "America/New_York"

SCRIPT_ROOT = Path(__file__).resolve().parent
STRATEGY_ROOT = SCRIPT_ROOT.parent

DEFAULT_RUN_DIR = STRATEGY_ROOT / "runs" / "das_scanner_appearance_20260628T114046Z"
DEFAULT_QUOTES_ROOT = Path(r"C:\TSIS_Data\data\quotes")
DEFAULT_TRADES_ROOT = Path(r"E:\TSIS\data\trades_ticks_prod_2005_2026")
DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)

PATTERN_DEFINITIONS = {
    "single_candle_rebreak": (
        "La ruptura del high estructural del primer push ocurre en una sola vela 1m. "
        "Es el caso mas directo: el dip no necesita construir una base larga."
    ),
    "last_red_high_break": (
        "La reactivacion rompe el high de la ultima vela roja relevante del pullback. "
        "Cuele capturar entradas tempranas antes de que el mercado confirme un nuevo high completo."
    ),
    "multi_candle_flag_break": (
        "El precio consolida durante varias velas despues del primer push y rompe la estructura al alza. "
        "Es una banderita general, sin exigir necesariamente higher lows perfectos."
    ),
    "ascending_flag_break": (
        "La consolidacion muestra lows crecientes antes del rebreak. "
        "Es una variante mas ordenada de bandera alcista."
    ),
    "flat_shelf_break": (
        "El precio acepta una zona relativamente plana despues del push y rompe el techo de esa meseta. "
        "Interesa porque indica absorcion antes de la nueva expansion."
    ),
    "vwap_reclaim_rebreak": (
        "El dip interactua con VWAP y la reactivacion recupera control alcista. "
        "Eebe tratarse como contexto de control, no como regla de entrada por si sola."
    ),
    "unclear": (
        "El rebreak existe, pero la forma del pullback no queda claramente clasificada por la heuristica actual."
    ),
}

QUALITY_DEFINITIONS = {
    "a_plus_frontside_candidate": (
        "Movimiento fuerte, dip no destructivo, rebreak rapido y extension posterior material. "
        "No significa trade bueno; significa muestra prioritaria de estudio."
    ),
    "constructive_frontside_candidate": (
        "Frontside util para estudiar DAS: rebreak confirmado y continuidad razonable, pero menos limpio que A+."
    ),
    "fragile_or_late_frontside_review": (
        "Hay rebreak o continuidad, pero con retraso de scanner, dip profundo o estructura menos estable."
    ),
    "fade_push_review": (
        "El push existe pero la continuidad posterior es pobre o el primer dip parece destruir demasiado."
    ),
    "manual_review": "La heuristica no tiene evidencia suficiente para clasificar con confianza.",
}


@dataclass(frozen=True)
class BuildConfig:
    run_dir: Path
    output_dir: Path
    data_root: Path
    quotes_root: Path
    trades_root: Path
    instrument_master_path: Path
    whole_dollar_abs_tolerance: float = 0.03
    whole_dollar_pct_tolerance: float = 1.0
    resistance_abs_tolerance: float = 0.03
    resistance_pct_tolerance: float = 1.0
    max_cases: int | None = None
    no_plots: bool = False
    progress_every: int = 50


class OhlcvCache:
    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root
        self._cache: dict[tuple[str, int, int], pd.DataFrame] = {}

    def get_month(self, ticker: str, year: int, month: int) -> pd.DataFrame:
        key = (ticker.upper(), int(year), int(month))
        if key in self._cache:
            return self._cache[key]
        path = (
            self.data_root
            / f"ticker={ticker.upper()}"
            / f"year={year}"
            / f"month={month:02d}"
            / f"minute_aggs_{ticker.upper()}_{year}_{month:02d}.parquet"
        )
        if not path.exists():
            self._cache[key] = pd.DataFrame()
            return self._cache[key]
        df = pd.read_parquet(path)
        if df.empty or "ts_utc" not in df.columns:
            self._cache[key] = pd.DataFrame()
            return self._cache[key]
        out = df.copy()
        out["ts_utc_dt"] = pd.to_datetime(out["ts_utc"], utc=True, errors="coerce")
        out = out.dropna(subset=["ts_utc_dt"]).sort_values("ts_utc_dt")
        out["ts_et"] = out["ts_utc_dt"].dt.tz_convert(NY_TZ)
        out["session_date"] = out["ts_et"].dt.date.astype(str)
        out["minute_of_day"] = out["ts_et"].dt.hour * 60 + out["ts_et"].dt.minute
        rename = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "vw": "vwap_raw"}
        out = out.rename(columns={k: v for k, v in rename.items() if k in out.columns})
        self._cache[key] = out
        return out

    def get_session(self, ticker: str, session_date: str) -> pd.DataFrame:
        ts = pd.Timestamp(session_date)
        df = self.get_month(ticker, ts.year, ts.month)
        if df.empty:
            return df
        out = df[df["session_date"].eq(str(session_date))].copy()
        return out[(out["minute_of_day"] >= 240) & (out["minute_of_day"] <= 1200)]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_candidates(run_dir: Path) -> tuple[pd.DataFrame, str]:
    for name in ["candidate_events.parquet", "candidate_events.csv", "candidate_events_partial.csv"]:
        path = run_dir / name
        if path.exists():
            if path.suffix == ".parquet":
                return pd.read_parquet(path), name
            return pd.read_csv(path), name
    raise FileNotFoundError(f"No candidate_events file found in {run_dir}")


def _safe_float(value: Any) -> float:
    try:
        if pd.isna(value):
            return math.nan
        return float(value)
    except Exception:
        return math.nan


def _safe_int(value: Any) -> int | None:
    try:
        if pd.isna(value):
            return None
        return int(value)
    except Exception:
        return None


def _parse_ts(value: Any) -> pd.Timestamp | pd.NaT:
    if value is None or pd.isna(value):
        return pd.NaT
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    return ts.tz_convert(NY_TZ)


def _minutes_between(start: pd.Timestamp | pd.NaT, end: pd.Timestamp | pd.NaT) -> float:
    if pd.isna(start) or pd.isna(end):
        return math.nan
    return (end - start).total_seconds() / 60.0


def _pct(a: float, b: float) -> float:
    if not np.isfinite(a) or not np.isfinite(b) or b == 0:
        return math.nan
    return (a - b) / b * 100.0


def _bars_between(df: pd.DataFrame, start: pd.Timestamp | pd.NaT, end: pd.Timestamp | pd.NaT) -> pd.DataFrame:
    if df.empty or pd.isna(start) or pd.isna(end):
        return pd.DataFrame()
    if end < start:
        return pd.DataFrame()
    return df[(df["ts_et"] >= start) & (df["ts_et"] <= end)].copy()


def _sum_volume(df: pd.DataFrame) -> float:
    if df.empty or "volume" not in df.columns:
        return math.nan
    return float(pd.to_numeric(df["volume"], errors="coerce").fillna(0).sum())


def _sum_dollar_volume(df: pd.DataFrame) -> float:
    if df.empty or not {"close", "volume"}.issubset(df.columns):
        return math.nan
    close = pd.to_numeric(df["close"], errors="coerce")
    volume = pd.to_numeric(df["volume"], errors="coerce")
    return float((close * volume).fillna(0).sum())


def _hour_label(ts: pd.Timestamp | pd.NaT) -> str:
    if pd.isna(ts):
        return "<NA>"
    return f"{int(ts.hour):02d}:00"


def _bucket(value: float, edges: list[float], labels: list[str]) -> str:
    if not np.isfinite(value):
        return "<NA>"
    for idx in range(len(labels)):
        if edges[idx] <= value < edges[idx + 1]:
            return labels[idx]
    return labels[-1]


def _whole_dollar_metrics(price: float, abs_tolerance: float, pct_tolerance: float) -> dict[str, Any]:
    if not np.isfinite(price):
        return {
            "frontside_high_nearest_whole_dollar": math.nan,
            "frontside_high_distance_to_whole_dollar": math.nan,
            "frontside_high_near_whole_dollar": False,
        }
    nearest = round(price)
    distance = abs(price - nearest)
    pct_dist = distance / price * 100.0 if price else math.inf
    return {
        "frontside_high_nearest_whole_dollar": float(nearest),
        "frontside_high_distance_to_whole_dollar": distance,
        "frontside_high_near_whole_dollar": bool(distance <= abs_tolerance or pct_dist <= pct_tolerance),
    }


def _prior_resistance_metrics(
    month_df: pd.DataFrame,
    session_date: str,
    level: float,
    abs_tolerance: float,
    pct_tolerance: float,
) -> dict[str, Any]:
    if month_df.empty or not np.isfinite(level):
        return {
            "prior_resistance_current_month_hits": 0,
            "prior_resistance_current_month_volume": 0.0,
            "prior_resistance_current_month_first_ts": pd.NA,
            "prior_resistance_current_month_last_ts": pd.NA,
        }
    tol = max(abs_tolerance, level * pct_tolerance / 100.0)
    prior = month_df[month_df["session_date"] < str(session_date)].copy()
    if prior.empty:
        return {
            "prior_resistance_current_month_hits": 0,
            "prior_resistance_current_month_volume": 0.0,
            "prior_resistance_current_month_first_ts": pd.NA,
            "prior_resistance_current_month_last_ts": pd.NA,
        }
    high = pd.to_numeric(prior["high"], errors="coerce")
    low = pd.to_numeric(prior["low"], errors="coerce")
    mask = (high >= level - tol) & (low <= level + tol)
    hits = prior[mask]
    if hits.empty:
        return {
            "prior_resistance_current_month_hits": 0,
            "prior_resistance_current_month_volume": 0.0,
            "prior_resistance_current_month_first_ts": pd.NA,
            "prior_resistance_current_month_last_ts": pd.NA,
        }
    return {
        "prior_resistance_current_month_hits": int(len(hits)),
        "prior_resistance_current_month_volume": _sum_volume(hits),
        "prior_resistance_current_month_first_ts": str(hits["ts_et"].iloc[0]),
        "prior_resistance_current_month_last_ts": str(hits["ts_et"].iloc[-1]),
    }


def _exists_any(paths: list[Path]) -> bool:
    return any(path.exists() for path in paths)


def _quotes_file_available(root: Path, ticker: str, session_date: str) -> bool:
    ts = pd.Timestamp(session_date)
    paths = [
        root / ticker.upper() / f"year={ts.year}" / f"month={ts.month:02d}" / f"day={ts.day:02d}" / "quotes.parquet",
        root / ticker.upper() / f"year={ts.year}" / f"month={ts.month:02d}" / f"day={session_date}" / "quotes.parquet",
        root / f"ticker={ticker.upper()}" / f"year={ts.year}" / f"month={ts.month:02d}" / f"day={ts.day:02d}" / "quotes.parquet",
        root / f"ticker={ticker.upper()}" / f"year={ts.year}" / f"month={ts.month:02d}" / f"day={session_date}" / "quotes.parquet",
    ]
    return _exists_any(paths)


def _trades_file_available(root: Path, ticker: str, session_date: str) -> bool:
    ts = pd.Timestamp(session_date)
    paths = [
        root / ticker.upper() / f"year={ts.year}" / f"month={ts.month:02d}" / f"day={session_date}" / "market.parquet",
        root / ticker.upper() / f"year={ts.year}" / f"month={ts.month:02d}" / f"day={ts.day:02d}" / "market.parquet",
        root / f"ticker={ticker.upper()}" / f"year={ts.year}" / f"month={ts.month:02d}" / f"day={session_date}" / "market.parquet",
        root / f"ticker={ticker.upper()}" / f"year={ts.year}" / f"month={ts.month:02d}" / f"day={ts.day:02d}" / "market.parquet",
    ]
    return _exists_any(paths)


def _classify_quality(row: dict[str, Any]) -> str:
    max_momentum = _safe_float(row.get("max_momentum_pct_from_pm_open"))
    dip_depth = _safe_float(row.get("first_dip_depth_pct"))
    rebreak_to_max = _safe_float(row.get("rebreak_to_max_high_pct"))
    rebreak_minutes = _safe_float(row.get("rebreak_minutes_after_first_push_high"))
    scanner_quality = str(row.get("scanner_trigger_quality") or "")
    destroyed = bool(row.get("first_dip_destroyed_structure"))

    if destroyed or (np.isfinite(rebreak_to_max) and rebreak_to_max < 5.0):
        return "fade_push_review"
    if (
        max_momentum >= 100.0
        and dip_depth <= 25.0
        and rebreak_to_max >= 20.0
        and rebreak_minutes <= 20.0
        and scanner_quality != "late_but_pre_high"
    ):
        return "a_plus_frontside_candidate"
    if max_momentum >= 50.0 and dip_depth <= 30.0 and rebreak_to_max >= 10.0:
        return "constructive_frontside_candidate"
    if max_momentum >= 50.0:
        return "fragile_or_late_frontside_review"
    return "manual_review"


def _load_instrument_master(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()
    if "ticker" not in df.columns:
        return pd.DataFrame()
    keep = [
        "ticker",
        "company_name",
        "name",
        "primary_exchange",
        "exchange",
        "sic_description",
        "overview_sic_description",
        "sector",
        "industry",
    ]
    keep = [c for c in keep if c in df.columns]
    return df[keep].drop_duplicates("ticker")


def _build_cases(config: BuildConfig) -> tuple[pd.DataFrame, dict[str, Any]]:
    candidates, candidate_file = _read_candidates(config.run_dir)
    manifest = _read_json(config.run_dir / "manifest.json")
    if config.max_cases is not None:
        candidates = candidates.head(config.max_cases).copy()

    cache = OhlcvCache(config.data_root)
    records: list[dict[str, Any]] = []

    total = len(candidates)
    print(f"cases_to_analyze={total}", flush=True)
    for position, (_, src) in enumerate(candidates.iterrows(), start=1):
        ticker = str(src.get("ticker") or "").upper()
        session_date = str(src.get("session_date") or "")
        if not ticker or not session_date:
            continue

        if position == 1 or (config.progress_every > 0 and position % config.progress_every == 0):
            print(
                f"progress cases_analyzed={position}/{total} records={len(records)} current={ticker} {session_date}",
                flush=True,
            )

        session_df = cache.get_session(ticker, session_date)
        session_ts = pd.Timestamp(session_date)
        month_df = cache.get_month(ticker, session_ts.year, session_ts.month)

        scanner_ts = _parse_ts(src.get("scanner_trigger_ts_utc"))
        first_push_start_ts = _parse_ts(src.get("first_push_start_ts_utc"))
        first_push_high_ts = _parse_ts(src.get("first_push_high_ts_utc"))
        first_dip_low_ts = _parse_ts(src.get("first_dip_low_ts_utc"))
        first_rebreak_ts = _parse_ts(src.get("first_rebreak_ts_utc"))
        max_high_ts = _parse_ts(src.get("max_momentum_high_ts_utc")) or _parse_ts(src.get("max_high_after_trigger_ts_utc"))
        momentum_end_ts = _parse_ts(src.get("momentum_end_ts_utc"))

        first_push_bars = _bars_between(session_df, first_push_start_ts, first_push_high_ts)
        pullback_bars = _bars_between(session_df, first_push_high_ts, first_rebreak_ts)
        frontside_bars = _bars_between(session_df, first_push_start_ts, max_high_ts)
        trigger_to_max_bars = _bars_between(session_df, scanner_ts, max_high_ts)

        pm_open_price = _safe_float(src.get("pm_open_price"))
        prior_close = _safe_float(src.get("prior_close"))
        first_push_high = _safe_float(src.get("selected_first_push_high"))
        if not np.isfinite(first_push_high):
            first_push_high = _safe_float(src.get("first_push_high"))
        max_momentum_high = _safe_float(src.get("max_momentum_high"))
        if not np.isfinite(max_momentum_high):
            max_momentum_high = _safe_float(src.get("max_high_after_trigger"))
        rebreak_price = _safe_float(src.get("rebreak_close"))
        if not np.isfinite(rebreak_price):
            rebreak_price = _safe_float(src.get("rebreak_high"))
        scanner_price = _safe_float(src.get("price_at_trigger"))

        rebreak_to_max_pct = _pct(max_momentum_high, rebreak_price)
        first_push_duration = _minutes_between(first_push_start_ts, first_push_high_ts)
        frontside_duration = _minutes_between(first_push_start_ts, max_high_ts)
        trigger_to_high_duration = _minutes_between(scanner_ts, max_high_ts)
        rebreak_to_high_duration = _minutes_between(first_rebreak_ts, max_high_ts)

        first_push_volume = _sum_volume(first_push_bars)
        first_push_dollar_volume = _sum_dollar_volume(first_push_bars)
        frontside_volume = _sum_volume(frontside_bars)
        frontside_dollar_volume = _sum_dollar_volume(frontside_bars)
        trigger_to_max_volume = _sum_volume(trigger_to_max_bars)

        first_push_clock_minutes = max(first_push_duration, 1.0) if np.isfinite(first_push_duration) else math.nan
        frontside_clock_minutes = max(frontside_duration, 1.0) if np.isfinite(frontside_duration) else math.nan

        record: dict[str, Any] = {
            "candidate_id": src.get("candidate_id"),
            "ticker": ticker,
            "session_date": session_date,
            "tradingview_symbol": src.get("tradingview_symbol"),
            "primary_exchange": src.get("primary_exchange"),
            "company_name": src.get("security_name") if pd.notna(src.get("security_name")) else src.get("name"),
            "candidate_file": candidate_file,
            "run_id": manifest.get("run_id") or config.run_dir.name,
            "run_dir": str(config.run_dir),
            "data_root": str(config.data_root),
            "builder_id": BUILDER_ID,
            "builder_version": BUILDER_VERSION,
            "built_at_utc": datetime.now(timezone.utc).isoformat(),
            "scanner_trigger_ts_et": str(scanner_ts) if pd.notna(scanner_ts) else pd.NA,
            "scanner_trigger_hour_et": _hour_label(scanner_ts),
            "scanner_trigger_quality": src.get("scanner_trigger_quality"),
            "scanner_trigger_price": scanner_price,
            "scanner_trigger_gap_pct_from_prior_close": _safe_float(src.get("day_gap_pct")),
            "scanner_trigger_pct_from_pm_open": _safe_float(src.get("pm_open_to_scanner_pct")),
            "scanner_trigger_volume_today": _safe_float(src.get("session_volume_at_trigger")),
            "scanner_trigger_premarket_volume": _safe_float(src.get("premarket_volume_at_trigger")),
            "scanner_delay_minutes": _safe_float(src.get("scanner_delay_minutes")),
            "scanner_after_first_push": bool(src.get("scanner_trigger_after_first_push"))
            if not pd.isna(src.get("scanner_trigger_after_first_push"))
            else pd.NA,
            "stale_scanner_trigger": bool(src.get("stale_scanner_trigger"))
            if not pd.isna(src.get("stale_scanner_trigger"))
            else pd.NA,
            "pm_open_ts_et": str(_parse_ts(src.get("pm_open_ts_utc")))
            if pd.notna(src.get("pm_open_ts_utc"))
            else pd.NA,
            "pm_open_price": pm_open_price,
            "prior_close": prior_close,
            "first_push_start_ts_et": str(first_push_start_ts) if pd.notna(first_push_start_ts) else pd.NA,
            "first_push_high_ts_et": str(first_push_high_ts) if pd.notna(first_push_high_ts) else pd.NA,
            "first_push_high_hour_et": _hour_label(first_push_high_ts),
            "first_push_start_price": _safe_float(src.get("first_push_start_price")),
            "first_push_high": first_push_high,
            "first_push_pct_from_pm_open": _safe_float(src.get("pm_open_to_first_push_high_pct")),
            "first_push_pct_from_push_start": _safe_float(src.get("first_push_pct_from_push_start")),
            "first_push_pct_from_prior_close": _pct(first_push_high, prior_close),
            "first_push_duration_min": first_push_duration,
            "first_push_observed_bar_count": len(first_push_bars) if not first_push_bars.empty else _safe_int(round(first_push_duration + 1)) if np.isfinite(first_push_duration) else None,
            "first_push_volume_ohlcv": first_push_volume,
            "first_push_dollar_volume_ohlcv": first_push_dollar_volume,
            "first_push_volume_per_clock_min": first_push_volume / first_push_clock_minutes
            if np.isfinite(first_push_volume) and np.isfinite(first_push_clock_minutes)
            else math.nan,
            "first_push_volume_per_observed_bar": first_push_volume / len(first_push_bars)
            if not first_push_bars.empty and np.isfinite(first_push_volume)
            else math.nan,
            "first_dip_low_ts_et": str(first_dip_low_ts) if pd.notna(first_dip_low_ts) else pd.NA,
            "first_dip_low": _safe_float(src.get("first_dip_low")),
            "first_dip_depth_pct": _safe_float(src.get("first_dip_depth_pct")),
            "first_pullback_depth_pct": _safe_float(src.get("first_pullback_depth_pct")),
            "first_push_retention_pct": _safe_float(src.get("first_push_retention_pct")),
            "first_dip_destroyed_structure": bool(src.get("first_dip_destroyed_structure"))
            if not pd.isna(src.get("first_dip_destroyed_structure"))
            else pd.NA,
            "pullback_duration_to_rebreak_min": _minutes_between(first_push_high_ts, first_rebreak_ts),
            "pullback_observed_bar_count": len(pullback_bars) if not pullback_bars.empty else 0,
            "first_rebreak_ts_et": str(first_rebreak_ts) if pd.notna(first_rebreak_ts) else pd.NA,
            "first_rebreak_hour_et": _hour_label(first_rebreak_ts),
            "first_rebreak_type": src.get("first_rebreak_type"),
            "rebreak_minutes_after_first_push_high": _safe_float(src.get("minutes_to_first_rebreak")),
            "rebreak_price": rebreak_price,
            "rebreak_volume": _safe_float(src.get("rebreak_volume")),
            "rebreak_close_above_vwap": src.get("rebreak_close_above_vwap"),
            "rebreak_to_max_high_pct": rebreak_to_max_pct,
            "rebreak_to_max_high_minutes": rebreak_to_high_duration,
            "max_momentum_high_ts_et": str(max_high_ts) if pd.notna(max_high_ts) else pd.NA,
            "max_momentum_high_hour_et": _hour_label(max_high_ts),
            "max_momentum_high": max_momentum_high,
            "max_momentum_pct_from_pm_open": _safe_float(src.get("max_momentum_pct_from_pm_open")),
            "max_momentum_pct_from_push_start": _safe_float(src.get("max_momentum_pct_from_push_start")),
            "max_momentum_pct_from_prior_close": _pct(max_momentum_high, prior_close),
            "frontside_duration_to_high_min": frontside_duration,
            "scanner_to_frontside_high_min": trigger_to_high_duration,
            "frontside_observed_bar_count": len(frontside_bars) if not frontside_bars.empty else 0,
            "frontside_volume_ohlcv": frontside_volume,
            "frontside_dollar_volume_ohlcv": frontside_dollar_volume,
            "frontside_volume_per_clock_min": frontside_volume / frontside_clock_minutes
            if np.isfinite(frontside_volume) and np.isfinite(frontside_clock_minutes)
            else math.nan,
            "frontside_volume_per_observed_bar": frontside_volume / len(frontside_bars)
            if not frontside_bars.empty and np.isfinite(frontside_volume)
            else math.nan,
            "trigger_to_max_volume_ohlcv": trigger_to_max_volume,
            "momentum_end_ts_et": str(momentum_end_ts) if pd.notna(momentum_end_ts) else pd.NA,
            "momentum_end_reason": src.get("momentum_end_reason"),
            "das_state": src.get("das_state"),
            "event_quality_state": src.get("event_quality_state"),
            "pattern_family_refined": src.get("first_rebreak_type") if pd.notna(src.get("first_rebreak_type")) else "unclear",
            "first_green_wick_dip_type": src.get("first_green_wick_dip_type"),
            "quotes_file_available": _quotes_file_available(config.quotes_root, ticker, session_date),
            "trades_regular_file_available": _trades_file_available(config.trades_root, ticker, session_date),
            "premarket_volume_source": "ohlcv_1m",
            "quotes_use": "microstructure_context_only_when_available",
            "trades_use": "regular_session_validation_only_when_available",
        }
        record.update(
            _whole_dollar_metrics(
                max_momentum_high,
                config.whole_dollar_abs_tolerance,
                config.whole_dollar_pct_tolerance,
            )
        )
        record.update(
            _prior_resistance_metrics(
                month_df,
                session_date,
                max_momentum_high,
                config.resistance_abs_tolerance,
                config.resistance_pct_tolerance,
            )
        )
        record["first_push_bucket"] = _bucket(
            _safe_float(record["first_push_pct_from_pm_open"]),
            [-999, 20, 50, 100, 200, 500, 999999],
            ["<20%", "20-50%", "50-100%", "100-200%", "200-500%", ">=500%"],
        )
        record["max_momentum_bucket"] = _bucket(
            _safe_float(record["max_momentum_pct_from_pm_open"]),
            [-999, 20, 50, 100, 200, 500, 999999],
            ["<20%", "20-50%", "50-100%", "100-200%", "200-500%", ">=500%"],
        )
        record["first_dip_depth_bucket"] = _bucket(
            _safe_float(record["first_dip_depth_pct"]),
            [-999, 5, 10, 20, 35, 50, 999999],
            ["<5%", "5-10%", "10-20%", "20-35%", "35-50%", ">=50%"],
        )
        record["frontside_duration_bucket"] = _bucket(
            _safe_float(record["frontside_duration_to_high_min"]),
            [-999, 5, 15, 30, 60, 120, 240, 999999],
            ["<5m", "5-15m", "15-30m", "30-60m", "60-120m", "120-240m", ">=240m"],
        )
        record["algorithmic_quality_bucket"] = _classify_quality(record)
        records.append(record)

    cases = pd.DataFrame(records)
    instrument = _load_instrument_master(config.instrument_master_path)
    if not instrument.empty and not cases.empty:
        cases = cases.merge(instrument, on="ticker", how="left", suffixes=("", "_instrument"))
        for dst, candidates in {
            "sector_or_sic": ["sector", "overview_sic_description", "sic_description", "industry"],
            "instrument_company_name": ["company_name_instrument", "name"],
        }.items():
            value = pd.Ceries([pd.NA] * len(cases), index=cases.index)
            for col in candidates:
                if col in cases.columns:
                    value = value.fillna(cases[col])
            cases[dst] = value

    meta = {
        "builder_id": BUILDER_ID,
        "builder_version": BUILDER_VERSION,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(config.run_dir),
        "candidate_file": candidate_file,
        "rows": int(len(cases)),
        "data_root": str(config.data_root),
        "quotes_root": str(config.quotes_root),
        "trades_root": str(config.trades_root),
        "instrument_master_path": str(config.instrument_master_path),
        "progress_every": config.progress_every,
    }
    return cases, meta


def _write_dataframe_outputs(cases: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{CASES_BASENAME}.csv"
    parquet_path = output_dir / f"{CASES_BASENAME}.parquet"
    cases.to_csv(csv_path, index=False)
    cases.to_parquet(parquet_path, index=False)


def _summary_tables(cases: pd.DataFrame, output_dir: Path) -> dict[str, pd.DataFrame]:
    tables_dir = output_dir / "summary_tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    tables: dict[str, pd.DataFrame] = {}

    def add(name: str, df: pd.DataFrame) -> None:
        tables[name] = df
        df.to_csv(tables_dir / f"{name}.csv", index=False)

    if cases.empty:
        return tables

    for col in [
        "pattern_family_refined",
        "algorithmic_quality_bucket",
        "first_rebreak_hour_et",
        "max_momentum_bucket",
        "first_dip_depth_bucket",
        "first_push_bucket",
        "frontside_duration_bucket",
        "primary_exchange",
        "sector_or_sic",
    ]:
        if col in cases.columns:
            vc = cases[col].fillna("<NA>").value_counts(dropna=False).rename_axis(col).reset_index(name="count")
            vc["pct"] = vc["count"] / len(cases) * 100.0
            add(f"counts_by_{col}", vc)

    if {"max_momentum_bucket", "first_dip_depth_pct"}.issubset(cases.columns):
        dip_by_momentum = (
            cases.groupby("max_momentum_bucket", dropna=False, observed=False)["first_dip_depth_pct"]
            .agg(["count", "mean", "median"])
            .reset_index()
        )
        add("first_dip_depth_by_max_momentum_bucket", dip_by_momentum)

    if {"pattern_family_refined", "max_momentum_pct_from_pm_open"}.issubset(cases.columns):
        by_pattern = (
            cases.groupby("pattern_family_refined", dropna=False, observed=False)
            .agg(
                count=("candidate_id", "count"),
                median_max_momentum_pct=("max_momentum_pct_from_pm_open", "median"),
                median_first_dip_depth_pct=("first_dip_depth_pct", "median"),
                median_frontside_duration_min=("frontside_duration_to_high_min", "median"),
                median_frontside_volume_per_min=("frontside_volume_per_clock_min", "median"),
                median_rebreak_to_max_high_pct=("rebreak_to_max_high_pct", "median"),
            )
            .reset_index()
        )
        add("pattern_quality_metrics", by_pattern)

    if {"quotes_file_available", "trades_regular_file_available"}.issubset(cases.columns):
        coverage = pd.DataFrame(
            [
                {"dataset": "quotes", "rows_available": int(cases["quotes_file_available"].sum())},
                {"dataset": "trades_regular", "rows_available": int(cases["trades_regular_file_available"].sum())},
            ]
        )
        coverage["rows_total"] = len(cases)
        coverage["pct_available"] = coverage["rows_available"] / len(cases) * 100.0
        add("quotes_trades_coverage", coverage)

    top_cols = [
        "ticker",
        "session_date",
        "tradingview_symbol",
        "max_momentum_pct_from_pm_open",
        "first_push_pct_from_pm_open",
        "first_dip_depth_pct",
        "first_rebreak_type",
        "algorithmic_quality_bucket",
        "frontside_duration_to_high_min",
        "frontside_volume_per_clock_min",
    ]
    top_cols = [c for c in top_cols if c in cases.columns]
    if "max_momentum_pct_from_pm_open" in cases.columns:
        add("top_examples_by_max_momentum", cases.sort_values("max_momentum_pct_from_pm_open", ascending=False)[top_cols].head(50))
    if "frontside_high_near_whole_dollar" in cases.columns:
        add("frontside_high_near_whole_dollar_examples", cases[cases["frontside_high_near_whole_dollar"].eq(True)][top_cols + ["frontside_high_nearest_whole_dollar", "frontside_high_distance_to_whole_dollar"]].head(100))

    return tables


def _plot_bar(df: pd.DataFrame, x: str, y: str, title: str, path: Path, rotate: int = 35) -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df[x].astype(str), df[y].astype(float), color="#3b82f6")
    ax.set_title(title)
    ax.set_ylabel(y)
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=rotate)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_box(cases: pd.DataFrame, category: str, value: str, title: str, path: Path) -> None:
    if cases.empty or category not in cases.columns or value not in cases.columns:
        return
    data = []
    labels = []
    for label, group in cases.groupby(category, dropna=False, observed=False):
        values = pd.to_numeric(group[value], errors="coerce").dropna()
        if values.empty:
            continue
        labels.append(str(label))
        data.append(values.to_numpy())
    if not data:
        return
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.set_title(title)
    ax.set_ylabel(value)
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_scatter(cases: pd.DataFrame, x: str, y: str, color_col: str, title: str, path: Path) -> None:
    if cases.empty or x not in cases.columns or y not in cases.columns:
        return
    fig, ax = plt.subplots(figsize=(11, 7))
    labels = cases[color_col].fillna("<NA>").astype(str) if color_col in cases.columns else pd.Ceries(["all"] * len(cases))
    for label, group in cases.groupby(labels, observed=False):
        ax.scatter(
            pd.to_numeric(group[x], errors="coerce"),
            pd.to_numeric(group[y], errors="coerce"),
            s=24,
            alpha=0.65,
            label=str(label),
        )
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.grid(alpha=0.25)
    if len(set(labels)) <= 12:
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_heatmap(cases: pd.DataFrame, row_col: str, col_col: str, title: str, path: Path) -> None:
    if cases.empty or row_col not in cases.columns or col_col not in cases.columns:
        return
    ct = pd.crosstab(cases[row_col].fillna("<NA>"), cases[col_col].fillna("<NA>"))
    if ct.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 7))
    im = ax.imshow(ct.to_numpy(), aspect="auto", cmap="Blues")
    ax.set_title(title)
    ax.set_xticks(range(len(ct.columns)))
    ax.set_xticklabels([str(c) for c in ct.columns], rotation=35, ha="right")
    ax.set_yticks(range(len(ct.index)))
    ax.set_yticklabels([str(i) for i in ct.index])
    for i in range(ct.shape[0]):
        for j in range(ct.shape[1]):
            ax.text(j, i, str(int(ct.iloc[i, j])), ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _write_plots(cases: pd.DataFrame, tables: dict[str, pd.DataFrame], output_dir: Path) -> list[Path]:
    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    plot_specs = [
        ("counts_by_pattern_family_refined", "pattern_family_refined", "count", "01_rebreak_type_counts.png", "DAS pattern / rebreak type counts"),
        ("counts_by_algorithmic_quality_bucket", "algorithmic_quality_bucket", "count", "02_pattern_quality_counts.png", "Algorithmic quality buckets"),
        ("counts_by_first_rebreak_hour_et", "first_rebreak_hour_et", "count", "03_rebreak_hour_counts.png", "Rebreak hour distribution"),
        ("counts_by_max_momentum_bucket", "max_momentum_bucket", "count", "04_max_momentum_bucket_counts.png", "Max momentum buckets"),
        ("counts_by_frontside_duration_bucket", "frontside_duration_bucket", "count", "05_frontside_duration_bucket_counts.png", "Frontside duration buckets"),
    ]
    for table_name, x, y, filename, title in plot_specs:
        path = plots_dir / filename
        _plot_bar(tables.get(table_name, pd.DataFrame()), x, y, title, path)
        if path.exists():
            created.append(path)

    for category, value, filename, title in [
        ("pattern_family_refined", "max_momentum_pct_from_pm_open", "06_max_momentum_by_rebreak_type.png", "Max momentum by rebreak type"),
        ("max_momentum_bucket", "first_dip_depth_pct", "07_first_dip_depth_by_max_momentum_bucket.png", "First dip depth by max momentum bucket"),
        ("pattern_family_refined", "frontside_volume_per_clock_min", "08_frontside_volume_per_min_by_pattern.png", "Frontside volume/min by pattern"),
        ("algorithmic_quality_bucket", "frontside_duration_to_high_min", "09_frontside_duration_by_quality.png", "Frontside duration to high by quality"),
    ]:
        path = plots_dir / filename
        _plot_box(cases, category, value, title, path)
        if path.exists():
            created.append(path)

    path = plots_dir / "10_first_push_vs_max_momentum.png"
    _plot_scatter(
        cases,
        "first_push_pct_from_pm_open",
        "max_momentum_pct_from_pm_open",
        "algorithmic_quality_bucket",
        "First push vs max momentum",
        path,
    )
    if path.exists():
        created.append(path)

    path = plots_dir / "11_pattern_by_momentum_bucket_heatmap.png"
    _plot_heatmap(cases, "pattern_family_refined", "max_momentum_bucket", "Pattern by max momentum bucket", path)
    if path.exists():
        created.append(path)

    path = plots_dir / "12_quality_by_dip_bucket_heatmap.png"
    _plot_heatmap(cases, "algorithmic_quality_bucket", "first_dip_depth_bucket", "Quality by first dip bucket", path)
    if path.exists():
        created.append(path)

    if "frontside_high_near_whole_dollar" in cases.columns:
        wh = cases["frontside_high_near_whole_dollar"].value_counts(dropna=False).rename_axis("near_whole_dollar").reset_index(name="count")
        path = plots_dir / "13_whole_dollar_frontside_highs.png"
        _plot_bar(wh, "near_whole_dollar", "count", "Frontside high near whole dollar", path, rotate=0)
        if path.exists():
            created.append(path)

    if {"quotes_file_available", "trades_regular_file_available"}.issubset(cases.columns):
        coverage = pd.DataFrame(
            [
                {"dataset": "quotes", "available": int(cases["quotes_file_available"].sum())},
                {"dataset": "trades_regular", "available": int(cases["trades_regular_file_available"].sum())},
            ]
        )
        path = plots_dir / "14_quotes_trades_coverage.png"
        _plot_bar(coverage, "dataset", "available", "Quotes/trades file coverage", path, rotate=0)
        if path.exists():
            created.append(path)

    return created


def _fmt(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(_fmt(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def _rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except Exception:
        return path.as_posix()


def _write_report(cases: pd.DataFrame, tables: dict[str, pd.DataFrame], plots: list[Path], meta: dict[str, Any], output_dir: Path) -> Path:
    report_path = output_dir / REPORT_NAME
    lines: list[str] = []
    lines.extend(
        [
            "# DAS Frontside Pattern Stats Report v0.1",
            "",
            "Estado: `experimental_research_report`",
            f"Builder: `{BUILDER_ID} {BUILDER_VERSION}`",
            f"Run: `{meta.get('run_dir')}`",
            f"Rows: `{len(cases)}`",
            "",
            "## 1. Proposito",
            "",
            "Este reporte intenta convertir el run DAS en una lectura visual y estadistica del frontside.",
            "",
            "No es un backtest. No mide edge institucional. No decide entradas, stops, targets ni sizing.",
            "",
            "Cu objetivo es responder preguntas practicas:",
            "",
            "- cuanto dura la extension hasta el high del frontside;",
            "- a que horas aparecen los frontsides;",
            "- que forma toma el rebreak despues del primer dip;",
            "- que profundidad tiene el primer dip por bucket de momentum;",
            "- que volumen/minuto tienen los tramos utiles;",
            "- cuantos highs terminan cerca de numeros enteros;",
            "- que cobertura de quotes/trades existe para enriquecer microestructura.",
            "",
            "## 2. Advertencia metodologica",
            "",
            "Este run ya viene condicionado por el detector DAS actual.",
            "",
            "Por tanto, este reporte puede estudiar la estructura de los candidatos detectados, pero todavia no puede medir falsos positivos reales del universo completo.",
            "",
            "Para medir falsos positivos reales hace falta que el detector emita tambien:",
            "",
            "- `scanner_only`;",
            "- `first_push_only`;",
            "- `push_destroyed_before_rebreak`;",
            "- `no_rebreak_after_first_dip`.",
            "",
            "Mientras eso no exista, los resultados deben leerse como:",
            "",
            "```text",
            "conditional_on_current_das_detector",
            "```",
            "",
        ]
    )

    lines.extend(["## 3. Definiciones de patrones", ""])
    for name, text in PATTERN_DEFINITIONS.items():
        lines.append(f"- `{name}`: {text}")
    lines.append("")

    lines.extend(["## 4. Definiciones de calidad heuristica", ""])
    for name, text in QUALITY_DEFINITIONS.items():
        lines.append(f"- `{name}`: {text}")
    lines.append("")

    lines.extend(["## 5. Graficos", ""])
    if plots:
        for path in plots:
            rel = _rel(path, output_dir)
            title = path.stem.replace("_", " ")
            lines.append(f"![{title}]({rel})")
            lines.append("")
    else:
        lines.append("_No plots generated._")
        lines.append("")

    lines.extend(
        [
            "## 6. Tablas principales",
            "",
            "### 6.1. Patrones por tipo de rebreak",
            "",
            _markdown_table(tables.get("counts_by_pattern_family_refined", pd.DataFrame())),
            "",
            "### 6.2. Calidad heuristica",
            "",
            _markdown_table(tables.get("counts_by_algorithmic_quality_bucket", pd.DataFrame())),
            "",
            "### 6.3. Horario de rebreak",
            "",
            _markdown_table(tables.get("counts_by_first_rebreak_hour_et", pd.DataFrame())),
            "",
            "### 6.4. Profundidad del primer dip por bucket de max momentum",
            "",
            _markdown_table(tables.get("first_dip_depth_by_max_momentum_bucket", pd.DataFrame())),
            "",
            "### 6.5. Metricas por patron",
            "",
            _markdown_table(tables.get("pattern_quality_metrics", pd.DataFrame())),
            "",
            "### 6.6. Cobertura quotes/trades",
            "",
            _markdown_table(tables.get("quotes_trades_coverage", pd.DataFrame())),
            "",
            "### 6.7. Top ejemplos por max momentum",
            "",
            _markdown_table(tables.get("top_examples_by_max_momentum", pd.DataFrame()), max_rows=25),
            "",
        ]
    )

    lines.extend(
        [
            "## 7. Lectura sobre trades y quotes",
            "",
            "`trades_ticks_prod_2005_2026` se trata aqui como validacion de sesion regular cuando existe archivo.",
            "",
            "`quotes` se trata como contexto de microestructura cuando existe archivo.",
            "",
            "Para volumen/minuto premarket, este reporte usa `ohlcv_1m`, porque los trades revisados hasta ahora aparecen como regular-session-only y quotes no son volumen ejecutado.",
            "",
            "## 8. Outputs",
            "",
            f"- casos CSV: `{CASES_BASENAME}.csv`",
            f"- casos parquet: `{CASES_BASENAME}.parquet`",
            "- tablas: `summary_tables/*.csv`",
            "- graficos: `plots/*.png`",
            "",
            "## 9. Ciguiente paso",
            "",
            "El siguiente builder DAS v2 debe emitir tambien casos fallidos/no-rebreak para medir falsos positivos reales y no solo estructura de candidatos confirmados.",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def build(config: BuildConfig) -> dict[str, Any]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    cases, meta = _build_cases(config)
    _write_dataframe_outputs(cases, config.output_dir)
    tables = _summary_tables(cases, config.output_dir)
    plots = [] if config.no_plots else _write_plots(cases, tables, config.output_dir)
    report_path = _write_report(cases, tables, plots, meta, config.output_dir)
    meta_path = config.output_dir / "BUILD_METADATA.json"
    meta.update(
        {
            "output_dir": str(config.output_dir),
            "report_path": str(report_path),
            "plots": [str(p) for p in plots],
            "case_rows": int(len(cases)),
            "case_columns": int(len(cases.columns)),
        }
    )
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return meta


def _manifest_data_root(run_dir: Path) -> Path | None:
    manifest = _read_json(run_dir / "manifest.json")
    config = manifest.get("config") or {}
    data_root = config.get("data_root") if isinstance(config, dict) else None
    if data_root:
        return Path(data_root)
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build DAS frontside pattern statistics for one run.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--quotes-root", type=Path, default=DEFAULT_QUOTES_ROOT)
    parser.add_argument("--trades-root", type=Path, default=DEFAULT_TRADES_ROOT)
    parser.add_argument("--instrument-master-path", type=Path, default=DEFAULT_INSTRUMENT_MASTER)
    parser.add_argument("--whole-dollar-abs-tolerance", type=float, default=0.03)
    parser.add_argument("--whole-dollar-pct-tolerance", type=float, default=1.0)
    parser.add_argument("--resistance-abs-tolerance", type=float, default=0.03)
    parser.add_argument("--resistance-pct-tolerance", type=float, default=1.0)
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument("--progress-every", type=int, default=50)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir
    data_root = args.data_root or _manifest_data_root(run_dir) or Path(r"E:\TSIS\data\ohlcv_1m")
    output_dir = args.output_dir or (run_dir / OUTPUT_DIRNAME)
    config = BuildConfig(
        run_dir=run_dir,
        output_dir=output_dir,
        data_root=data_root,
        quotes_root=args.quotes_root,
        trades_root=args.trades_root,
        instrument_master_path=args.instrument_master_path,
        whole_dollar_abs_tolerance=args.whole_dollar_abs_tolerance,
        whole_dollar_pct_tolerance=args.whole_dollar_pct_tolerance,
        resistance_abs_tolerance=args.resistance_abs_tolerance,
        resistance_pct_tolerance=args.resistance_pct_tolerance,
        max_cases=args.max_cases,
        no_plots=args.no_plots,
        progress_every=args.progress_every,
    )
    meta = build(config)
    print(f"output_dir={meta['output_dir']}")
    print(f"report_path={meta['report_path']}")
    print(f"rows={meta['case_rows']}")
    print(f"plots={len(meta['plots'])}")


if __name__ == "__main__":
    main()
