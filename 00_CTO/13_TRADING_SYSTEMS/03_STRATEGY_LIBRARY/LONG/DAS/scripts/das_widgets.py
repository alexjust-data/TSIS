"""DAS exploratory search and notebook widgets.

This module is exploratory. It searches for strategy samples, not promoted
events, trades, edge, entries, stops, targets, or sizing.
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import html as html_lib
import json
from pathlib import Path
import re
import sys
from typing import Callable, Iterable
from urllib.parse import urlencode
from uuid import uuid4

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

import plotly.graph_objects as go
from plotly.subplots import make_subplots


SCRIPT_ROOT = Path(__file__).resolve().parent
STRATEGY_ROOT = SCRIPT_ROOT.parent
STRATEGY_LIBRARY_ROOT = STRATEGY_ROOT.parent.parent
SHARED_ROOT = STRATEGY_LIBRARY_ROOT / "_shared"
if str(SHARED_ROOT) not in sys.path:
    sys.path.insert(0, str(SHARED_ROOT))

from strategy_widgets_common import (  # noqa: E402
    DEFAULT_DATA_ROOT,
    DEFAULT_LT1B_UNIVERSE_PATH,
    DEFAULT_REFERENCE_OVERVIEW_ROOT,
    DEFAULT_REFERENCE_SPLITS_ROOT,
    ET_TZ,
    _compute_vwap,
    _delete_run_command,
    _load_market_cap_history,
    _market_cap_asof,
    _months_between,
    _parse_csv,
    _parse_years,
    _ps_quote,
    _read_1m_file,
    _reference_asof,
    _run_datetime_utc_label,
    _safe_filename,
    _select_vwap,
    _session_segment,
    _tradingview_symbol,
    load_lt1b_universe,
    load_split_events_for_chart,
    make_strategy_1m_chart,
)


DEFAULT_RUNS_ROOT = STRATEGY_ROOT / "runs"
DEFAULT_DAILY_ROOT = Path(r"E:\TSIS\data\ohlcv_daily")
QUERY_NAME = "das_scanner_appearance"
NOTEBOOK_SQUARE_CHART_HEIGHT = 1275
EXPORT_SQUARE_CHART_WIDTH = 1530
EXPORT_SQUARE_CHART_HEIGHT = EXPORT_SQUARE_CHART_WIDTH
VOLUME_PANEL_DOMAIN = (0.0, 0.20)
PRICE_PANEL_DOMAIN = (0.22, 1.0)
INHERITED_GAP_TRACE_NAMES = {"official open gap", "premarket high gap"}

FIELD_DEFINITIONS = [
    ("1m root", "Carpeta operativa de velas 1m usada para buscar candidatos."),
    ("Reference", "Carpeta de referencia usada para leer exchange, market cap y compania."),
    ("Universe", "Source of truth LT1B que limita los tickers elegibles."),
    ("Tickers", "Lista manual de tickers; vacio significa usar universo LT1B."),
    ("Years", "Anios a escanear; acepta 2025 o 2022-2025."),
    ("Session", "Segmentos donde simular aparicion en screener."),
    (
        "Session Vol >",
        "Volumen acumulado desde el inicio de premarket; debe alcanzarse mientras se construye el primer push.",
    ),
    (
        "Momentum %",
        "Extension minima desde apertura de premarket para marcar el trigger de momentum temprano.",
    ),
    ("Price >=", "Precio minimo observado en la vela de aparicion."),
    ("Price <=", "Precio maximo observado en la vela de aparicion."),
    ("MCap <", "Market cap maximo permitido cuando existe dato de referencia."),
    ("No MCap", "Politica cuando falta market cap: include, exclude o flag."),
    ("DAS state", "Clasificacion posterior: scanner_only, push_detected, push_and_dip, rebreak_confirmed o failed_before_rebreak."),
    ("Green wick dip", "Dip intrabar en vela verde de continuacion: barre bajo el cierre previo y recupera con momentum."),
    ("Price", "Vista de precio usada: raw o split_normalized."),
    ("VWAP", "Linea VWAP del chart: calculated usa VWAP acumulada calculada; raw usa la columna vw del parquet."),
    ("Y padding", "Aire visual arriba y abajo del chart interactivo."),
    ("Progress", "Cada cuantos archivos escaneados se imprime progreso en terminal."),
    ("Flush hits", "Cada cuantos candidatos nuevos se actualiza candidate_events_partial.csv."),
]


@dataclass(frozen=True)
class DasConfig:
    data_root: str = str(DEFAULT_DATA_ROOT)
    reference_overview_root: str = str(DEFAULT_REFERENCE_OVERVIEW_ROOT)
    output_root: str = str(DEFAULT_RUNS_ROOT)
    universe_path: str = str(DEFAULT_LT1B_UNIVERSE_PATH)
    use_lt1b_universe: bool = True
    query_name: str = QUERY_NAME
    tickers: tuple[str, ...] = ()
    years: tuple[int, ...] = ()
    start_date: str | None = None
    end_date: str | None = None
    session_scope: str = "premarket"
    push_label_pct: float = 20.0
    dip_label_pct: float = 3.0
    momentum_trigger_pct: float = 50.0
    min_session_volume: float = 500_000.0
    min_price: float = 0.5
    max_price: float = 20.0
    max_market_cap: float | None = 100_000_000.0
    missing_market_cap_policy: str = "include"
    price_view: str = "raw"
    vwap_source: str = "calculated"
    max_candidates: int | None = None
    progress_every: int = 250
    partial_flush_every: int = 1
    workers: int = 1


def _format_field_definitions_html() -> str:
    rows = "".join(
        f"<tr><td><code>{name}</code></td><td>{description}</td></tr>" for name, description in FIELD_DEFINITIONS
    )
    return (
        "<details open><summary><b>Definiciones de controles</b></summary>"
        "<table>"
        "<thead><tr><th>Control</th><th>Significado</th></tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table>"
        "</details>"
    )


def _terminal_command_from_config(config: DasConfig, pretty: bool = True) -> str:
    parts = [
        ("--data-root", _ps_quote(config.data_root)),
        ("--reference-overview-root", _ps_quote(config.reference_overview_root)),
        ("--output-root", _ps_quote(config.output_root)),
        ("--universe-path", _ps_quote(config.universe_path)),
        ("--session-scope", config.session_scope),
        ("--push-label-pct", str(config.push_label_pct)),
        ("--dip-label-pct", str(config.dip_label_pct)),
        ("--momentum-trigger-pct", str(config.momentum_trigger_pct)),
        ("--min-session-volume", str(config.min_session_volume)),
        ("--min-price", str(config.min_price)),
        ("--max-price", str(config.max_price)),
        ("--max-market-cap", str(config.max_market_cap)),
        ("--missing-market-cap-policy", config.missing_market_cap_policy),
        ("--price-view", config.price_view),
        ("--vwap-source", config.vwap_source),
        ("--progress-every", str(config.progress_every)),
        ("--partial-flush-every", str(config.partial_flush_every)),
    ]
    if config.tickers:
        parts.append(("--tickers", _ps_quote(",".join(config.tickers))))
    if config.years:
        parts.append(("--years", _ps_quote(",".join(str(year) for year in config.years))))
    flags = []

    if not pretty:
        flat = [
            f"Set-Location {_ps_quote(str(STRATEGY_ROOT))};",
            "python",
            _ps_quote(str(SCRIPT_ROOT / "das_widgets.py")),
        ]
        for name, value in parts:
            flat.extend([name, value])
        flat.extend(flags)
        return " ".join(flat)

    lines = [
        f"Set-Location {_ps_quote(str(STRATEGY_ROOT))}",
        f"python {_ps_quote(str(SCRIPT_ROOT / 'das_widgets.py'))} `",
    ]
    command_lines = [f"  {name} {value}" for name, value in parts] + [f"  {flag}" for flag in flags]
    for idx, line in enumerate(command_lines):
        suffix = " `" if idx < len(command_lines) - 1 else ""
        lines.append(line + suffix)
    return "\n".join(lines)


def _scope_mask(df: pd.DataFrame, session_scope: str) -> pd.Series:
    if session_scope == "premarket":
        return df["session_segment"].eq("premarket")
    if session_scope == "regular":
        return df["session_segment"].eq("regular")
    if session_scope == "premarket_regular":
        return df["session_segment"].isin(["premarket", "regular"])
    raise ValueError(f"Unsupported session_scope: {session_scope}")


def _classify_rebreak_type(dip_to_break: pd.DataFrame, rebreak_row: pd.Series, vwap_at_rebreak: float | None) -> str:
    if len(dip_to_break) <= 1:
        return "single_candle_rebreak"
    lows = dip_to_break["px_l"].astype(float).to_numpy()
    highs = dip_to_break["px_h"].astype(float).to_numpy()
    closes = dip_to_break["px_c"].astype(float).to_numpy()
    if len(lows) >= 3 and all(lows[i] >= lows[i - 1] for i in range(1, len(lows))):
        return "ascending_flag_break"
    if len(closes) >= 3:
        close_range_pct = (max(closes) - min(closes)) / max(float(rebreak_row["px_c"]), 0.01) * 100.0
        high_range_pct = (max(highs) - min(highs)) / max(float(rebreak_row["px_c"]), 0.01) * 100.0
        if close_range_pct <= 6.0 and high_range_pct <= 10.0:
            return "flat_shelf_break"
    if len(dip_to_break) >= 3:
        return "multi_candle_rebreak"
    return "unclear"


def _find_first_green_wick_dip_after_rebreak(
    work: pd.DataFrame, rebreak_row: pd.Series | None
) -> tuple[pd.Series | None, str | None, float | None, float | None]:
    if rebreak_row is None:
        return None, None, None, None
    rebreak_pos = int(rebreak_row.name)
    previous_close = float(rebreak_row["px_c"])
    previous_high = float(rebreak_row["px_h"])
    for _, row in work.iloc[rebreak_pos + 1 :].iterrows():
        open_px = float(row["px_o"])
        high_px = float(row["px_h"])
        low_px = float(row["px_l"])
        close_px = float(row["px_c"])
        if close_px <= open_px:
            previous_close = close_px
            previous_high = high_px
            continue
        dipped_below_previous_close = low_px < previous_close
        recovered_green = close_px > open_px and close_px >= previous_close
        if dipped_below_previous_close and recovered_green:
            depth_pct = (previous_close - low_px) / previous_close * 100.0 if previous_close > 0 else None
            recovery_pct = (close_px - low_px) / low_px * 100.0 if low_px > 0 else None
            label = "green_wick_dip_new_high" if high_px > previous_high else "green_wick_dip_reactivation"
            return row, label, depth_pct, recovery_pct
        previous_close = close_px
        previous_high = high_px
    return None, None, None, None


def _clean_value(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return value


def _run_dir_path_from_text(value: str) -> Path | None:
    text = str(value or "").strip()
    if not text:
        return None
    lines = [line.strip() for line in text.replace("\r", "\n").split("\n") if line.strip()]
    selected = lines[0] if lines else text
    for line in lines:
        lower = line.lower()
        if lower.startswith("run_dir="):
            selected = line.split("=", 1)[1].strip()
            break
        if lower.startswith("run_dir:"):
            selected = line.split(":", 1)[1].strip()
            break
        if lower.startswith("run dir:"):
            selected = line.split(":", 1)[1].strip()
            break
        if ":\\" in line or line.startswith("\\\\"):
            selected = line
            break
    if selected.lower().startswith("run_dir="):
        selected = selected.split("=", 1)[1].strip()
    if selected.lower().startswith("run_dir:"):
        selected = selected.split(":", 1)[1].strip()
    if selected.lower().startswith("run dir:"):
        selected = selected.split(":", 1)[1].strip()
    selected = selected.strip().strip("'\"")
    return Path(selected) if selected else None


def _iso_or_none(row: pd.Series | None, column: str) -> str | None:
    if row is None:
        return None
    value = _clean_value(row.get(column))
    return value.isoformat() if value is not None else None


def _et_or_none(row: pd.Series | None, column: str) -> str | None:
    if row is None:
        return None
    value = _clean_value(row.get(column))
    return value.strftime("%Y-%m-%d %H:%M:%S %Z") if value is not None else None


def _float_or_none(value) -> float | None:
    value = _clean_value(value)
    return float(value) if value is not None else None


def _pct_change(start: float | None, end: float | None) -> float | None:
    if start is None or end is None or start <= 0:
        return None
    return (end - start) / start * 100.0


def _premarket_open_row(session_df: pd.DataFrame) -> pd.Series | None:
    if session_df.empty:
        return None
    session = session_df.sort_values("ts_utc_dt").copy()
    event_midnight = session["ts_et"].iloc[0].normalize()
    pm_start_et = event_midnight + pd.Timedelta(hours=4)
    pm_rows = session[session["session_segment"].eq("premarket") & (session["ts_et"] >= pm_start_et)]
    if pm_rows.empty:
        pm_rows = session[session["ts_et"] >= pm_start_et]
    if pm_rows.empty:
        return None
    return pm_rows.iloc[0]


def _das_iter_parquet_files(
    data_root: Path,
    tickers: Iterable[str],
    years: Iterable[int],
    universe: pd.DataFrame | None,
    discovery_progress_every: int = 0,
) -> list[Path]:
    requested_tickers = {str(t).upper() for t in tickers}
    ticker_filter = set(requested_tickers)
    year_filter = {int(y) for y in years}
    if universe is not None:
        universe_tickers = set(universe.index.astype(str))
        ticker_filter = requested_tickers & universe_tickers if requested_tickers else universe_tickers
        if not ticker_filter:
            return []

    files: list[Path] = []
    if year_filter:
        if ticker_filter:
            ticker_iterable = sorted(ticker_filter)
        else:
            ticker_iterable = [
                ticker_dir.name.split("=", 1)[-1].upper()
                for ticker_dir in sorted(data_root.glob("ticker=*"))
                if ticker_dir.is_dir()
            ]

        total_tickers = len(ticker_iterable)
        for ticker_position, ticker in enumerate(ticker_iterable, start=1):
            ticker_dir = data_root / f"ticker={ticker}"
            if not ticker_dir.is_dir():
                if discovery_progress_every > 0 and ticker_position % discovery_progress_every == 0:
                    print(
                        "discovery "
                        f"tickers_checked={ticker_position}/{total_tickers} "
                        f"files_found={len(files)} current={ticker}",
                        flush=True,
                    )
                continue
            for year in sorted(year_filter):
                if universe is not None:
                    row = universe.loc[ticker]
                    if year < int(row["first_seen_date"].year) or year > int(row["last_observed_date"].year):
                        continue
                year_dir = ticker_dir / f"year={year}"
                if not year_dir.is_dir():
                    continue
                files.extend(sorted(year_dir.glob("month=*/*.parquet")))
            if discovery_progress_every > 0 and (
                ticker_position == 1 or ticker_position % discovery_progress_every == 0
            ):
                print(
                    "discovery "
                    f"tickers_checked={ticker_position}/{total_tickers} "
                    f"files_found={len(files)} current={ticker}",
                    flush=True,
                )
        return files

    for ticker_dir in sorted(data_root.glob("ticker=*")):
        if not ticker_dir.is_dir():
            continue
        ticker = ticker_dir.name.split("=", 1)[-1].upper()
        if ticker_filter and ticker not in ticker_filter:
            continue
        for year_dir in sorted(ticker_dir.glob("year=*")):
            if not year_dir.is_dir():
                continue
            try:
                year = int(year_dir.name.split("=", 1)[-1])
            except ValueError:
                continue
            if universe is not None:
                row = universe.loc[ticker]
                if year < int(row["first_seen_date"].year) or year > int(row["last_observed_date"].year):
                    continue
            files.extend(sorted(year_dir.glob("month=*/*.parquet")))
    return files


def _das_file_for_month(data_root: Path, ticker: str, year: int, month: int) -> Path:
    return (
        data_root
        / f"ticker={ticker.upper()}"
        / f"year={year}"
        / f"month={month:02d}"
        / f"minute_aggs_{ticker.upper()}_{year}_{month:02d}.parquet"
    )


def _visible_maxpush_pct(candidate: dict) -> float | None:
    for key in [
        "first_push_pct_from_pm_open",
        "pm_open_to_first_push_high_pct",
        "max_momentum_pct_from_pm_open",
        "pm_open_to_max_high_after_trigger_pct",
        "max_push_pct_after_trigger",
    ]:
        value = _float_or_none(candidate.get(key))
        if value is not None:
            return value
    return None


def _row_pos(row: pd.Series | None) -> int | None:
    return int(row.name) if row is not None else None


def _is_red_candle(row: pd.Series) -> bool:
    return float(row["px_c"]) < float(row["px_o"])


def _is_green_candle(row: pd.Series) -> bool:
    return float(row["px_c"]) > float(row["px_o"])


def _scanner_seed_row(premarket: pd.DataFrame, config: DasConfig) -> pd.Series | None:
    if premarket.empty:
        return None
    mask = (
        (premarket["premarket_cum_volume"] >= config.min_session_volume)
        & (premarket["px_c"].astype(float) >= config.min_price)
        & (premarket["px_c"].astype(float) <= config.max_price)
    )
    if not mask.any():
        return None
    return premarket.loc[mask.idxmax()]


def _momentum_trigger_row(premarket: pd.DataFrame, pm_open_price: float | None, config: DasConfig) -> pd.Series | None:
    if premarket.empty or pm_open_price is None or pm_open_price <= 0:
        return None
    threshold = pm_open_price * (1.0 + config.momentum_trigger_pct / 100.0)
    rows = premarket[premarket["px_h"].astype(float) >= threshold]
    if rows.empty:
        return None
    return rows.iloc[0]


def _find_awakening_start(premarket: pd.DataFrame, pm_open_price: float | None, threshold_pos: int) -> pd.Series:
    if premarket.empty:
        raise ValueError("Cannot find awakening start in an empty premarket frame.")
    if pm_open_price is None or pm_open_price <= 0:
        return premarket.iloc[0]
    search = premarket.iloc[: threshold_pos + 1].copy()
    if search.empty:
        return premarket.iloc[0]
    min_awake_pct = 5.0
    awake_threshold = pm_open_price * (1.0 + min_awake_pct / 100.0)
    awake_rows = search[search["px_h"].astype(float) >= awake_threshold]
    if awake_rows.empty:
        return search.iloc[0]
    first_awake_pos = int(awake_rows.iloc[0].name)
    lookback = search.iloc[max(0, first_awake_pos - 8) : first_awake_pos + 1]
    if lookback.empty:
        return awake_rows.iloc[0]
    low_idx = lookback["px_l"].astype(float).idxmin()
    return search.loc[low_idx]


def _find_first_push(
    premarket: pd.DataFrame, pm_open_price: float | None, config: DasConfig
) -> tuple[pd.Series | None, pd.Series | None, pd.Series | None]:
    """Find first push -> first red pullback using the DAS human sequence.

    Semantics:
    - first push is the first green expansion sequence after the ticker wakes up;
    - first push high is the max high through the first red candle that interrupts it;
    - first dip is the first red/non-green pullback sequence after that push;
    - first dip low is the lowest low inside that first pullback sequence.
    """
    if premarket.empty or pm_open_price is None or pm_open_price <= 0:
        return None, None, None

    push_threshold = pm_open_price * (1.0 + config.push_label_pct / 100.0)
    threshold_rows = premarket[premarket["px_h"].astype(float) >= push_threshold]
    if threshold_rows.empty:
        return None, None, None

    first_threshold_row = threshold_rows.iloc[0]
    threshold_pos = int(first_threshold_row.name)
    awakening_row = _find_awakening_start(premarket, pm_open_price, threshold_pos)
    awakening_pos = int(awakening_row.name)

    first_green_pos: int | None = None
    for _, row in premarket.iloc[awakening_pos : threshold_pos + 1].iterrows():
        if _is_green_candle(row):
            first_green_pos = int(row.name)
            break
    if first_green_pos is None:
        return None, None, None

    threshold_reached = False
    first_red_pos: int | None = None
    current_high = float("-inf")
    current_high_row: pd.Series | None = None

    for _, row in premarket.iloc[first_green_pos:].iterrows():
        high = float(row["px_h"])
        if high > current_high:
            current_high = high
            current_high_row = row
        if high >= push_threshold:
            threshold_reached = True
        if _is_red_candle(row) and threshold_reached:
            first_red_pos = int(row.name)
            break

    if first_red_pos is None or current_high_row is None:
        return None, None, None

    # The first red candle starts the dip, but its upper wick can still be the true first push high.
    push_window = premarket.iloc[first_green_pos : first_red_pos + 1]
    if push_window.empty:
        return None, None, None
    high_idx = push_window["px_h"].astype(float).idxmax()
    first_push_high_row = premarket.loc[high_idx]

    dip_end_pos = len(premarket)
    for _, row in premarket.iloc[first_red_pos + 1 :].iterrows():
        if _is_green_candle(row):
            # The first green recovery candle can still print the true dip low with its wick.
            dip_end_pos = int(row.name) + 1
            break
    dip_window = premarket.iloc[first_red_pos:dip_end_pos]
    if dip_window.empty:
        return None, None, None
    dip_low_idx = dip_window["px_l"].astype(float).idxmin()
    first_dip_low_row = premarket.loc[dip_low_idx]

    push_start_row = premarket.loc[first_green_pos]
    return push_start_row, first_push_high_row, first_dip_low_row

def _last_red_high_before_rebreak(
    premarket: pd.DataFrame,
    first_push_high_row: pd.Series,
    first_dip_low_row: pd.Series,
) -> tuple[float | None, pd.Series | None]:
    first_push_pos = int(first_push_high_row.name)
    first_dip_pos = int(first_dip_low_row.name)
    pullback = premarket.iloc[first_push_pos + 1 : first_dip_pos + 1]
    if pullback.empty:
        return _float_or_none(first_dip_low_row["px_h"]), first_dip_low_row
    red_mask = pullback["px_c"].astype(float) < pullback["px_o"].astype(float)
    red_rows = pullback[red_mask]
    if red_rows.empty:
        return _float_or_none(first_dip_low_row["px_h"]), first_dip_low_row
    row = red_rows.iloc[-1]
    return float(row["px_h"]), row


def _find_structural_rebreak(
    premarket: pd.DataFrame,
    first_push_high_row: pd.Series,
    first_dip_low_row: pd.Series,
) -> tuple[pd.Series | None, float | None, str | None, pd.Series | None, list[int]]:
    """Find the first valid breakout/rebreak of the first push high.

    Valid rebreak v0.2:
    - at or after the first dip low;
    - green candle;
    - high breaks first_push_high;
    - close confirms above first_push_high;
    - volume is at least the volume of the dip-low candle.
    """
    first_dip_pos = int(first_dip_low_row.name)
    first_push_high = float(first_push_high_row["px_h"])
    first_push_ts = first_push_high_row.get("ts_utc_dt")
    _, last_red_row = _last_red_high_before_rebreak(premarket, first_push_high_row, first_dip_low_row)
    rows_since_dip: list[int] = []
    max_initial_rebreak_minutes = 45.0
    dip_volume = _float_or_none(first_dip_low_row.get("v")) or 0.0

    for _, row in premarket.iloc[first_dip_pos:].iterrows():
        row_ts = row.get("ts_utc_dt")
        if pd.notna(first_push_ts) and pd.notna(row_ts):
            elapsed_minutes = (row_ts - first_push_ts).total_seconds() / 60.0
            if elapsed_minutes > max_initial_rebreak_minutes:
                break

        rows_since_dip.append(int(row.name))
        close_px = float(row["px_c"])
        high_px = float(row["px_h"])
        volume = _float_or_none(row.get("v")) or 0.0
        breaks_high = high_px > first_push_high
        confirms_close = close_px > first_push_high
        volume_confirms = volume >= dip_volume

        if _is_green_candle(row) and breaks_high and confirms_close and volume_confirms:
            return row, first_push_high, "first_push_high", last_red_row, rows_since_dip

    return None, first_push_high, "first_push_high", last_red_row, rows_since_dip

def _find_momentum_end(
    session_df: pd.DataFrame,
    push_start_row: pd.Series,
    selected_first_push_high: float | None,
) -> tuple[pd.Series | None, pd.Series | None, str | None]:
    if session_df.empty:
        return None, None, None
    start_ts = push_start_row["ts_utc_dt"]
    work = session_df[session_df["session_segment"].isin(["premarket", "regular"])].copy()
    work = work[work["ts_utc_dt"] >= start_ts].sort_values("ts_utc_dt").reset_index(drop=True)
    if work.empty:
        return None, None, None
    work["vwap"] = _compute_vwap(work)
    max_high_row = work.loc[work["px_h"].astype(float).idxmax()]
    max_pos = int(max_high_row.name)
    end_row = work.iloc[-1]
    reason = "window_end"
    if selected_first_push_high is not None:
        after_max = work.iloc[max_pos + 1 :]
        for _, row in after_max.iterrows():
            close_px = float(row["px_c"])
            vwap = _float_or_none(row.get("vwap"))
            if vwap is not None and close_px < vwap and close_px < float(selected_first_push_high):
                end_row = row
                reason = "vwap_loss_and_structure_break"
                break
    return max_high_row, end_row, reason


def _das_rows_for_session_v1(session_df: pd.DataFrame, prior_close: float | None, config: DasConfig) -> list[dict]:
    work = session_df[_scope_mask(session_df, config.session_scope)].copy()
    if work.empty:
        return []

    work = work.sort_values("ts_utc_dt").reset_index(drop=True)
    work["session_cum_volume"] = work["v"].astype(float).cumsum()
    scanner_mask = (
        (work["session_cum_volume"] >= config.min_session_volume)
        & (work["px_c"].astype(float) >= config.min_price)
        & (work["px_c"].astype(float) <= config.max_price)
    )
    if not scanner_mask.any():
        return []

    scanner_row = work.loc[scanner_mask.idxmax()]
    scanner_pos = int(scanner_row.name)
    after_trigger = work.iloc[scanner_pos:].copy()
    if after_trigger.empty:
        return []

    pre_trigger = work.iloc[:scanner_pos].copy()
    push_start_row = scanner_row
    first_push_start_price = float(push_start_row["px_o"])
    trigger_price = float(scanner_row["px_c"])
    pm_open_row = _premarket_open_row(session_df)
    pm_open_price = _float_or_none(pm_open_row["px_o"] if pm_open_row is not None else None)
    pm_open_ts_utc = _iso_or_none(pm_open_row, "ts_utc_dt")
    pm_open_ts_et = _et_or_none(pm_open_row, "ts_et")
    pre_trigger_high = float(pre_trigger["px_h"].astype(float).max()) if not pre_trigger.empty else None
    pre_trigger_high_pct_above_trigger = (
        (pre_trigger_high - trigger_price) / trigger_price * 100.0
        if pre_trigger_high is not None and trigger_price > 0 and pre_trigger_high > trigger_price
        else 0.0
    )
    prior_extension_before_trigger = pre_trigger_high_pct_above_trigger >= config.push_label_pct
    max_high_idx = after_trigger["px_h"].astype(float).idxmax()
    max_high_row = after_trigger.loc[max_high_idx]
    max_high_after_trigger = float(max_high_row["px_h"])
    max_push_pct_after_trigger = (
        (max_high_after_trigger - trigger_price) / trigger_price * 100.0 if trigger_price > 0 else 0.0
    )
    pm_open_to_scanner_pct = _pct_change(pm_open_price, trigger_price)
    pm_open_to_max_high_after_trigger_pct = _pct_change(pm_open_price, max_high_after_trigger)

    first_push_high_row: pd.Series | None = None
    first_dip_low_row: pd.Series | None = None
    rebreak_row: pd.Series | None = None
    rows_since_dip: list[int] = []
    das_state = "scanner_only"

    # Human DAS rule: a dip cannot start from any arbitrary low. It starts only
    # after the first red pullback candle following the initial push. The first
    # green recovery candle may still contribute the dip low via its wick.
    detected_push_start_row, detected_push_high_row, detected_dip_low_row = _find_first_push(
        work, pm_open_price, config
    )
    if detected_push_start_row is not None:
        push_start_row = detected_push_start_row
        first_push_start_price = float(_float_or_none(push_start_row.get("px_l")) or push_start_row["px_o"])
    if detected_push_high_row is not None:
        first_push_high_row = detected_push_high_row
        das_state = "push_detected"
    if detected_dip_low_row is not None and first_push_high_row is not None:
        first_dip_low_row = detected_dip_low_row
        das_state = "push_and_dip"
        first_push_high = float(first_push_high_row["px_h"])
        first_dip_pos = int(first_dip_low_row.name)
        for _, row in work.iloc[first_dip_pos + 1 :].iterrows():
            rows_since_dip.append(int(row.name))
            if float(row["px_h"]) >= first_push_high:
                rebreak_row = row
                das_state = "rebreak_confirmed"
                break
        if rebreak_row is None:
            post_dip = work.iloc[first_dip_pos + 1 :]
            if not post_dip.empty and float(post_dip["px_l"].min()) < trigger_price:
                das_state = "failed_before_rebreak"

    session_for_vwap = work.copy()
    session_for_vwap["vwap"] = _compute_vwap(session_for_vwap)
    vwap_at_rebreak = None
    if rebreak_row is not None and rebreak_row.name in session_for_vwap.index and pd.notna(session_for_vwap.loc[rebreak_row.name, "vwap"]):
        vwap_at_rebreak = float(session_for_vwap.loc[rebreak_row.name, "vwap"])

    dip_to_break = work.loc[rows_since_dip].copy() if rows_since_dip else pd.DataFrame()
    rebreak_type = _classify_rebreak_type(dip_to_break, rebreak_row, vwap_at_rebreak) if rebreak_row is not None else None
    green_wick_dip_row, green_wick_dip_type, green_wick_dip_depth_pct, green_wick_dip_recovery_pct = (
        _find_first_green_wick_dip_after_rebreak(work, rebreak_row)
    )
    first_push_high = _float_or_none(first_push_high_row["px_h"] if first_push_high_row is not None else None)
    first_push_pct = (
        (first_push_high - first_push_start_price) / first_push_start_price * 100.0
        if first_push_high is not None and first_push_start_price > 0
        else None
    )
    pm_open_to_first_push_high_pct = _pct_change(pm_open_price, first_push_high)
    first_dip_low = _float_or_none(first_dip_low_row["px_l"] if first_dip_low_row is not None else None)
    first_dip_depth_pct = (
        (first_push_high - first_dip_low) / first_push_high * 100.0
        if first_push_high is not None and first_dip_low is not None and first_push_high > 0
        else None
    )
    first_push_retention_pct = (
        (first_dip_low - first_push_start_price) / max(first_push_high - first_push_start_price, 0.01) * 100.0
        if first_push_high is not None and first_dip_low is not None
        else None
    )
    first_dip_destroyed_structure = (
        first_push_retention_pct is not None
        and first_dip_low is not None
        and (first_push_retention_pct <= 0.0 or first_dip_low <= first_push_start_price)
    )
    if das_state == "rebreak_confirmed" and first_dip_destroyed_structure:
        das_state = "structure_destroyed_before_rebreak"
    if das_state == "rebreak_confirmed" and prior_extension_before_trigger:
        das_state = "prior_extension_before_trigger"
    minutes_to_rebreak = (
        (rebreak_row["ts_et"] - first_push_high_row["ts_et"]).total_seconds() / 60.0
        if rebreak_row is not None and first_push_high_row is not None
        else None
    )
    minutes_from_trigger_to_rebreak = (
        (rebreak_row["ts_et"] - scanner_row["ts_et"]).total_seconds() / 60.0 if rebreak_row is not None else None
    )
    prior_close_value = float(prior_close) if prior_close and prior_close > 0 else None
    day_gap_pct = (
        (trigger_price - prior_close_value) / prior_close_value * 100.0
        if prior_close_value
        else None
    )

    return [
        {
            "candidate_id": f"{QUERY_NAME}:{scanner_row['ticker']}:{scanner_row['ts_utc_dt'].isoformat()}",
            "strategy_id": "das",
            "ticker": str(scanner_row["ticker"]).upper(),
            "session_date": str(scanner_row["session_date"]),
            "prior_close": prior_close_value,
            "regular_open": float(session_df[session_df["session_segment"].eq("regular")].iloc[0]["px_o"])
            if not session_df[session_df["session_segment"].eq("regular")].empty
            else None,
            "day_gap_pct": round(float(day_gap_pct), 4) if day_gap_pct is not None else None,
            "session_volume": float(work["v"].sum()),
            "scanner_trigger_ts_utc": scanner_row["ts_utc_dt"].isoformat(),
            "scanner_trigger_ts_et": scanner_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "price_at_trigger": trigger_price,
            "session_volume_at_trigger": float(scanner_row["session_cum_volume"]),
            "pm_open_ts_utc": pm_open_ts_utc,
            "pm_open_ts_et": pm_open_ts_et,
            "pm_open_price": pm_open_price,
            "pm_open_to_scanner_pct": round(float(pm_open_to_scanner_pct), 4)
            if pm_open_to_scanner_pct is not None
            else None,
            "pre_trigger_high": pre_trigger_high,
            "pre_trigger_high_pct_above_trigger": round(float(pre_trigger_high_pct_above_trigger), 4),
            "prior_extension_before_trigger": bool(prior_extension_before_trigger),
            "max_high_after_trigger": max_high_after_trigger,
            "max_high_after_trigger_ts_utc": max_high_row["ts_utc_dt"].isoformat(),
            "max_high_after_trigger_ts_et": max_high_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "scanner_to_max_high_pct": round(float(max_push_pct_after_trigger), 4),
            "max_push_pct_after_trigger": round(float(max_push_pct_after_trigger), 4),
            "pm_open_to_max_high_after_trigger_pct": round(float(pm_open_to_max_high_after_trigger_pct), 4)
            if pm_open_to_max_high_after_trigger_pct is not None
            else None,
            "first_push_start_ts_utc": push_start_row["ts_utc_dt"].isoformat(),
            "first_push_start_ts_et": push_start_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "first_push_start_price": first_push_start_price,
            "first_push_high": first_push_high,
            "first_push_high_ts_utc": _iso_or_none(first_push_high_row, "ts_utc_dt"),
            "first_push_high_ts_et": _et_or_none(first_push_high_row, "ts_et"),
            "first_push_pct": round(float(first_push_pct), 4) if first_push_pct is not None else None,
            "pm_open_to_first_push_high_pct": round(float(pm_open_to_first_push_high_pct), 4)
            if pm_open_to_first_push_high_pct is not None
            else None,
            "first_dip_low": first_dip_low,
            "first_dip_low_ts_utc": _iso_or_none(first_dip_low_row, "ts_utc_dt"),
            "first_dip_low_ts_et": _et_or_none(first_dip_low_row, "ts_et"),
            "first_dip_depth_pct": round(float(first_dip_depth_pct), 4) if first_dip_depth_pct is not None else None,
            "first_push_retention_pct": round(float(first_push_retention_pct), 4) if first_push_retention_pct is not None else None,
            "first_dip_destroyed_structure": bool(first_dip_destroyed_structure),
            "first_rebreak_ts_utc": _iso_or_none(rebreak_row, "ts_utc_dt"),
            "first_rebreak_ts_et": _et_or_none(rebreak_row, "ts_et"),
            "minutes_to_first_rebreak": round(float(minutes_to_rebreak), 2) if minutes_to_rebreak is not None else None,
            "minutes_from_trigger_to_rebreak": round(float(minutes_from_trigger_to_rebreak), 2)
            if minutes_from_trigger_to_rebreak is not None
            else None,
            "first_rebreak_type": rebreak_type,
            "rebreak_open": _float_or_none(rebreak_row["px_o"] if rebreak_row is not None else None),
            "rebreak_high": _float_or_none(rebreak_row["px_h"] if rebreak_row is not None else None),
            "rebreak_low": _float_or_none(rebreak_row["px_l"] if rebreak_row is not None else None),
            "rebreak_close": _float_or_none(rebreak_row["px_c"] if rebreak_row is not None else None),
            "rebreak_volume": _float_or_none(rebreak_row["v"] if rebreak_row is not None else None),
            "vwap_at_rebreak": vwap_at_rebreak,
            "rebreak_close_above_vwap": bool(float(rebreak_row["px_c"]) >= vwap_at_rebreak)
            if vwap_at_rebreak is not None and rebreak_row is not None
            else None,
            "first_green_wick_dip_ts_utc": _iso_or_none(green_wick_dip_row, "ts_utc_dt"),
            "first_green_wick_dip_ts_et": _et_or_none(green_wick_dip_row, "ts_et"),
            "first_green_wick_dip_low": _float_or_none(
                green_wick_dip_row["px_l"] if green_wick_dip_row is not None else None
            ),
            "first_green_wick_dip_close": _float_or_none(
                green_wick_dip_row["px_c"] if green_wick_dip_row is not None else None
            ),
            "first_green_wick_dip_type": green_wick_dip_type,
            "first_green_wick_dip_depth_pct": round(float(green_wick_dip_depth_pct), 4)
            if green_wick_dip_depth_pct is not None
            else None,
            "first_green_wick_dip_recovery_pct": round(float(green_wick_dip_recovery_pct), 4)
            if green_wick_dip_recovery_pct is not None
            else None,
            "das_state": das_state,
            "das_sequence_active": das_state == "rebreak_confirmed",
            "event_quality_state": "candidate_event" if das_state == "rebreak_confirmed" else "review_event",
        }
    ]


def _das_rows_for_session(session_df: pd.DataFrame, prior_close: float | None, config: DasConfig) -> list[dict]:
    session = session_df.sort_values("ts_utc_dt").reset_index(drop=True)
    premarket = session[session["session_segment"].eq("premarket")].copy()
    if premarket.empty:
        return []

    premarket = premarket.sort_values("ts_utc_dt").reset_index(drop=True)
    premarket["premarket_cum_volume"] = premarket["v"].astype(float).cumsum()

    pm_open_row = _premarket_open_row(session)
    pm_open_price = _float_or_none(pm_open_row["px_o"] if pm_open_row is not None else None)
    pm_open_ts_utc = _iso_or_none(pm_open_row, "ts_utc_dt")
    pm_open_ts_et = _et_or_none(pm_open_row, "ts_et")
    if pm_open_price is None or pm_open_price <= 0:
        return []

    push_start_row, first_push_high_row, first_dip_low_row = _find_first_push(premarket, pm_open_price, config)
    if push_start_row is None or first_push_high_row is None or first_dip_low_row is None:
        return []

    first_push_high_pos = int(first_push_high_row.name)
    scanner_window = premarket.iloc[: first_push_high_pos + 1].copy()
    scanner_row = _scanner_seed_row(scanner_window, config)
    if scanner_row is None:
        return []

    scanner_pos = int(scanner_row.name)
    push_start_pos = int(push_start_row.name)
    trigger_price = float(scanner_row["px_c"])
    prior_close_value = float(prior_close) if prior_close and prior_close > 0 else None
    first_push_start_price = min(float(push_start_row["px_o"]), float(push_start_row["px_l"]))
    first_push_high = float(first_push_high_row["px_h"])
    first_push_body_high = max(float(first_push_high_row["px_o"]), float(first_push_high_row["px_c"]))
    momentum_trigger_row = _momentum_trigger_row(premarket, pm_open_price, config)
    momentum_trigger_price = _float_or_none(momentum_trigger_row["px_h"] if momentum_trigger_row is not None else None)
    momentum_trigger_volume = _float_or_none(
        momentum_trigger_row["premarket_cum_volume"] if momentum_trigger_row is not None else None
    )
    premarket_extension_high_row = premarket.loc[premarket["px_h"].astype(float).idxmax()]
    premarket_extension_high = float(premarket_extension_high_row["px_h"])

    (
        rebreak_row,
        structural_rebreak_level,
        structural_rebreak_level_type,
        last_red_pullback_row,
        rows_since_dip,
    ) = _find_structural_rebreak(premarket, first_push_high_row, first_dip_low_row)
    if rebreak_row is None:
        return []

    session_for_vwap = premarket.copy()
    session_for_vwap["vwap"] = _compute_vwap(session_for_vwap)
    vwap_at_rebreak = None
    if rebreak_row.name in session_for_vwap.index and pd.notna(session_for_vwap.loc[rebreak_row.name, "vwap"]):
        vwap_at_rebreak = float(session_for_vwap.loc[rebreak_row.name, "vwap"])

    dip_to_break = premarket.loc[rows_since_dip].copy() if rows_since_dip else pd.DataFrame()
    rebreak_type = _classify_rebreak_type(dip_to_break, rebreak_row, vwap_at_rebreak)
    if structural_rebreak_level_type == "last_red_pullback_high" and rebreak_type == "unclear":
        rebreak_type = "last_red_high_break"

    green_wick_dip_row, green_wick_dip_type, green_wick_dip_depth_pct, green_wick_dip_recovery_pct = (
        _find_first_green_wick_dip_after_rebreak(premarket, rebreak_row)
    )

    max_momentum_row, momentum_end_row, momentum_end_reason = _find_momentum_end(
        session,
        push_start_row,
        first_push_high,
    )
    max_momentum_high = _float_or_none(max_momentum_row["px_h"] if max_momentum_row is not None else None)
    max_momentum_pct_from_pm_open = _pct_change(pm_open_price, max_momentum_high)
    max_momentum_pct_from_push_start = _pct_change(first_push_start_price, max_momentum_high)

    after_trigger = premarket.iloc[scanner_pos:].copy()
    max_high_after_trigger_row = after_trigger.loc[after_trigger["px_h"].astype(float).idxmax()]
    max_high_after_trigger = float(max_high_after_trigger_row["px_h"])
    max_push_pct_after_trigger = _pct_change(trigger_price, max_high_after_trigger) or 0.0

    pm_open_to_scanner_pct = _pct_change(pm_open_price, trigger_price)
    prior_close_to_scanner_pct = _pct_change(prior_close_value, trigger_price)
    pm_open_to_momentum_trigger_pct = _pct_change(pm_open_price, momentum_trigger_price)
    prior_close_to_momentum_trigger_pct = _pct_change(prior_close_value, momentum_trigger_price)
    pm_open_to_premarket_extension_high_pct = _pct_change(pm_open_price, premarket_extension_high)
    prior_close_to_premarket_extension_high_pct = _pct_change(prior_close_value, premarket_extension_high)
    pm_open_to_first_push_high_pct = _pct_change(pm_open_price, first_push_high)
    first_push_pct_from_push_start = _pct_change(first_push_start_price, first_push_high)
    first_dip_low = float(first_dip_low_row["px_l"])
    first_dip_depth_pct = _pct_change(first_push_high, first_dip_low)
    first_dip_depth_pct = abs(first_dip_depth_pct) if first_dip_depth_pct is not None else None
    first_push_retention_pct = (
        (first_dip_low - first_push_start_price) / max(first_push_high - first_push_start_price, 0.01) * 100.0
        if first_push_high > first_push_start_price
        else None
    )
    first_dip_destroyed_structure = bool(
        first_push_retention_pct is not None and first_push_retention_pct <= 0.0
    )

    pre_scanner = premarket.iloc[:scanner_pos].copy()
    pre_trigger_high = float(pre_scanner["px_h"].astype(float).max()) if not pre_scanner.empty else None
    pre_trigger_high_pct_above_trigger = (
        (pre_trigger_high - trigger_price) / trigger_price * 100.0
        if pre_trigger_high is not None and trigger_price > 0 and pre_trigger_high > trigger_price
        else 0.0
    )
    pre_scanner_high_pct_from_pm_open = _pct_change(pm_open_price, pre_trigger_high)
    prior_extension_before_trigger = bool(
        pre_scanner_high_pct_from_pm_open is not None
        and pre_scanner_high_pct_from_pm_open >= config.push_label_pct
    )

    if scanner_pos <= push_start_pos:
        scanner_trigger_quality = "early"
    elif scanner_pos < first_push_high_pos:
        scanner_trigger_quality = "acceptable"
    else:
        scanner_trigger_quality = "late_but_pre_high"

    scanner_delay_bars = max(0, scanner_pos - push_start_pos)
    scanner_delay_minutes = (
        (scanner_row["ts_et"] - push_start_row["ts_et"]).total_seconds() / 60.0
        if scanner_pos >= push_start_pos
        else 0.0
    )
    scanner_delay_pct_from_awakening = _pct_change(first_push_start_price, trigger_price)

    minutes_to_rebreak = (
        (rebreak_row["ts_et"] - first_push_high_row["ts_et"]).total_seconds() / 60.0
        if rebreak_row is not None and first_push_high_row is not None
        else None
    )
    minutes_from_trigger_to_rebreak = (
        (rebreak_row["ts_et"] - scanner_row["ts_et"]).total_seconds() / 60.0 if rebreak_row is not None else None
    )
    day_gap_pct = (
        (trigger_price - prior_close_value) / prior_close_value * 100.0
        if prior_close_value
        else None
    )

    return [
        {
            "candidate_id": f"{QUERY_NAME}:{scanner_row['ticker']}:{scanner_row['ts_utc_dt'].isoformat()}",
            "strategy_id": "das",
            "ticker": str(scanner_row["ticker"]).upper(),
            "session_date": str(scanner_row["session_date"]),
            "prior_close": prior_close_value,
            "regular_open": float(session[session["session_segment"].eq("regular")].iloc[0]["px_o"])
            if not session[session["session_segment"].eq("regular")].empty
            else None,
            "day_gap_pct": round(float(day_gap_pct), 4) if day_gap_pct is not None else None,
            "session_volume": float(premarket["v"].sum()),
            "premarket_volume": float(premarket["v"].sum()),
            "scanner_eligibility_ts_utc": scanner_row["ts_utc_dt"].isoformat(),
            "scanner_eligibility_ts_et": scanner_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "scanner_trigger_ts_utc": scanner_row["ts_utc_dt"].isoformat(),
            "scanner_trigger_ts_et": scanner_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "scanner_trigger_quality": scanner_trigger_quality,
            "scanner_delay_bars": int(scanner_delay_bars),
            "scanner_delay_minutes": round(float(scanner_delay_minutes), 2),
            "scanner_delay_pct_from_awakening": round(float(scanner_delay_pct_from_awakening), 4)
            if scanner_delay_pct_from_awakening is not None
            else None,
            "scanner_trigger_after_first_push": False,
            "stale_scanner_trigger": False,
            "price_at_trigger": trigger_price,
            "session_volume_at_trigger": float(scanner_row["premarket_cum_volume"]),
            "premarket_volume_at_trigger": float(scanner_row["premarket_cum_volume"]),
            "pm_open_ts_utc": pm_open_ts_utc,
            "pm_open_ts_et": pm_open_ts_et,
            "pm_open_price": pm_open_price,
            "pm_open_to_scanner_pct": round(float(pm_open_to_scanner_pct), 4)
            if pm_open_to_scanner_pct is not None
            else None,
            "prior_close_to_scanner_pct": round(float(prior_close_to_scanner_pct), 4)
            if prior_close_to_scanner_pct is not None
            else None,
            "momentum_trigger_pct_threshold": float(config.momentum_trigger_pct),
            "momentum_trigger_ts_utc": _iso_or_none(momentum_trigger_row, "ts_utc_dt"),
            "momentum_trigger_ts_et": _et_or_none(momentum_trigger_row, "ts_et"),
            "momentum_trigger_price": momentum_trigger_price,
            "momentum_trigger_volume": momentum_trigger_volume,
            "pm_open_to_momentum_trigger_pct": round(float(pm_open_to_momentum_trigger_pct), 4)
            if pm_open_to_momentum_trigger_pct is not None
            else None,
            "prior_close_to_momentum_trigger_pct": round(float(prior_close_to_momentum_trigger_pct), 4)
            if prior_close_to_momentum_trigger_pct is not None
            else None,
            "premarket_extension_high": premarket_extension_high,
            "premarket_extension_high_ts_utc": premarket_extension_high_row["ts_utc_dt"].isoformat(),
            "premarket_extension_high_ts_et": premarket_extension_high_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "pm_open_to_premarket_extension_high_pct": round(float(pm_open_to_premarket_extension_high_pct), 4)
            if pm_open_to_premarket_extension_high_pct is not None
            else None,
            "prior_close_to_premarket_extension_high_pct": round(float(prior_close_to_premarket_extension_high_pct), 4)
            if prior_close_to_premarket_extension_high_pct is not None
            else None,
            "awakening_start_ts_utc": push_start_row["ts_utc_dt"].isoformat(),
            "awakening_start_ts_et": push_start_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "awakening_start_price": first_push_start_price,
            "awakening_reason": "premarket_range_volume_expansion",
            "pre_trigger_high": pre_trigger_high,
            "pre_trigger_high_pct_above_trigger": round(float(pre_trigger_high_pct_above_trigger), 4),
            "pre_scanner_high_pct_from_pm_open": round(float(pre_scanner_high_pct_from_pm_open), 4)
            if pre_scanner_high_pct_from_pm_open is not None
            else None,
            "prior_extension_before_trigger": prior_extension_before_trigger,
            "max_high_after_trigger": max_high_after_trigger,
            "max_high_after_trigger_ts_utc": max_high_after_trigger_row["ts_utc_dt"].isoformat(),
            "max_high_after_trigger_ts_et": max_high_after_trigger_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "scanner_to_max_high_pct": round(float(max_push_pct_after_trigger), 4),
            "max_push_pct_after_trigger": round(float(max_push_pct_after_trigger), 4),
            "pm_open_to_max_high_after_trigger_pct": round(float(_pct_change(pm_open_price, max_high_after_trigger)), 4)
            if _pct_change(pm_open_price, max_high_after_trigger) is not None
            else None,
            "first_push_start_ts_utc": push_start_row["ts_utc_dt"].isoformat(),
            "first_push_start_ts_et": push_start_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "first_push_start_price": first_push_start_price,
            "first_push_high": first_push_high,
            "first_push_high_ts_utc": _iso_or_none(first_push_high_row, "ts_utc_dt"),
            "first_push_high_ts_et": _et_or_none(first_push_high_row, "ts_et"),
            "first_push_pct": round(float(first_push_pct_from_push_start), 4)
            if first_push_pct_from_push_start is not None
            else None,
            "first_push_pct_from_pm_open": round(float(pm_open_to_first_push_high_pct), 4)
            if pm_open_to_first_push_high_pct is not None
            else None,
            "first_push_pct_from_push_start": round(float(first_push_pct_from_push_start), 4)
            if first_push_pct_from_push_start is not None
            else None,
            "pm_open_to_first_push_high_pct": round(float(pm_open_to_first_push_high_pct), 4)
            if pm_open_to_first_push_high_pct is not None
            else None,
            "first_push_wick_high": first_push_high,
            "first_push_body_high": first_push_body_high,
            "selected_first_push_high": first_push_high,
            "first_push_structural_high": structural_rebreak_level,
            "first_push_high_selection_reason": structural_rebreak_level_type,
            "first_dip_low": first_dip_low,
            "first_dip_low_ts_utc": _iso_or_none(first_dip_low_row, "ts_utc_dt"),
            "first_dip_low_ts_et": _et_or_none(first_dip_low_row, "ts_et"),
            "first_pullback_low": first_dip_low,
            "first_pullback_low_ts_utc": _iso_or_none(first_dip_low_row, "ts_utc_dt"),
            "first_pullback_low_ts_et": _et_or_none(first_dip_low_row, "ts_et"),
            "first_dip_depth_pct": round(float(first_dip_depth_pct), 4) if first_dip_depth_pct is not None else None,
            "first_pullback_depth_pct": round(float(first_dip_depth_pct), 4) if first_dip_depth_pct is not None else None,
            "first_push_retention_pct": round(float(first_push_retention_pct), 4) if first_push_retention_pct is not None else None,
            "first_dip_destroyed_structure": first_dip_destroyed_structure,
            "last_red_pullback_high": structural_rebreak_level
            if structural_rebreak_level_type == "last_red_pullback_high"
            else _float_or_none(last_red_pullback_row["px_h"] if last_red_pullback_row is not None else None),
            "last_red_pullback_high_ts_utc": _iso_or_none(last_red_pullback_row, "ts_utc_dt"),
            "last_red_pullback_high_ts_et": _et_or_none(last_red_pullback_row, "ts_et"),
            "structure_alive_after_pullback": True,
            "structural_rebreak_level": structural_rebreak_level,
            "structural_rebreak_level_type": structural_rebreak_level_type,
            "rebreak_close_above_required_level": bool(
                structural_rebreak_level is not None and float(rebreak_row["px_c"]) > float(structural_rebreak_level)
            ),
            "first_rebreak_ts_utc": _iso_or_none(rebreak_row, "ts_utc_dt"),
            "first_rebreak_ts_et": _et_or_none(rebreak_row, "ts_et"),
            "minutes_to_first_rebreak": round(float(minutes_to_rebreak), 2) if minutes_to_rebreak is not None else None,
            "minutes_from_trigger_to_rebreak": round(float(minutes_from_trigger_to_rebreak), 2)
            if minutes_from_trigger_to_rebreak is not None
            else None,
            "first_rebreak_type": rebreak_type,
            "rebreak_open": _float_or_none(rebreak_row["px_o"] if rebreak_row is not None else None),
            "rebreak_high": _float_or_none(rebreak_row["px_h"] if rebreak_row is not None else None),
            "rebreak_low": _float_or_none(rebreak_row["px_l"] if rebreak_row is not None else None),
            "rebreak_close": _float_or_none(rebreak_row["px_c"] if rebreak_row is not None else None),
            "rebreak_volume": _float_or_none(rebreak_row["v"] if rebreak_row is not None else None),
            "vwap_at_rebreak": vwap_at_rebreak,
            "rebreak_close_above_vwap": bool(float(rebreak_row["px_c"]) >= vwap_at_rebreak)
            if vwap_at_rebreak is not None and rebreak_row is not None
            else None,
            "first_green_wick_dip_ts_utc": _iso_or_none(green_wick_dip_row, "ts_utc_dt"),
            "first_green_wick_dip_ts_et": _et_or_none(green_wick_dip_row, "ts_et"),
            "first_green_wick_dip_low": _float_or_none(
                green_wick_dip_row["px_l"] if green_wick_dip_row is not None else None
            ),
            "first_green_wick_dip_close": _float_or_none(
                green_wick_dip_row["px_c"] if green_wick_dip_row is not None else None
            ),
            "first_green_wick_dip_type": green_wick_dip_type,
            "first_green_wick_dip_depth_pct": round(float(green_wick_dip_depth_pct), 4)
            if green_wick_dip_depth_pct is not None
            else None,
            "first_green_wick_dip_recovery_pct": round(float(green_wick_dip_recovery_pct), 4)
            if green_wick_dip_recovery_pct is not None
            else None,
            "max_momentum_high": max_momentum_high,
            "max_momentum_high_ts_utc": _iso_or_none(max_momentum_row, "ts_utc_dt"),
            "max_momentum_high_ts_et": _et_or_none(max_momentum_row, "ts_et"),
            "max_momentum_pct_from_pm_open": round(float(max_momentum_pct_from_pm_open), 4)
            if max_momentum_pct_from_pm_open is not None
            else None,
            "max_momentum_pct_from_push_start": round(float(max_momentum_pct_from_push_start), 4)
            if max_momentum_pct_from_push_start is not None
            else None,
            "momentum_end_ts_utc": _iso_or_none(momentum_end_row, "ts_utc_dt"),
            "momentum_end_ts_et": _et_or_none(momentum_end_row, "ts_et"),
            "momentum_end_reason": momentum_end_reason,
            "das_state": "rebreak_confirmed",
            "state_reason": "structural_rebreak_confirmed",
            "das_sequence_active": True,
            "event_quality_state": "candidate_event",
        }
    ]


def _candidate_rows_for_file(path: Path, config: DasConfig, start_date: str | None, end_date: str | None) -> list[dict]:
    df = _read_1m_file(path, config.price_view)
    if df.empty:
        return []
    if start_date:
        df = df[df["session_date"] >= start_date]
    if end_date:
        df = df[df["session_date"] <= end_date]
    if df.empty:
        return []

    regular_closes = (
        df[df["session_segment"].eq("regular")]
        .groupby("session_date", sort=True)["px_c"]
        .last()
        .sort_index()
    )
    rows: list[dict] = []
    for session_date, session_df in df.groupby("session_date", sort=True):
        prior_dates = regular_closes.index[regular_closes.index < session_date]
        prior_close = float(regular_closes.loc[prior_dates[-1]]) if len(prior_dates) else None
        rows.extend(_das_rows_for_session(session_df.sort_values("ts_utc_dt"), prior_close, config))
    return rows


def _postprocess_candidates(candidates: list[dict], config: DasConfig) -> pd.DataFrame:
    out = pd.DataFrame(candidates)
    if out.empty:
        return out

    overview_root = Path(config.reference_overview_root)
    market_cap_cache: dict[str, pd.DataFrame] = {}
    enriched: list[dict] = []
    for row in out.itertuples(index=False):
        ticker = row.ticker
        if ticker not in market_cap_cache:
            market_cap_cache[ticker] = _load_market_cap_history(overview_root, ticker)
        hist = market_cap_cache[ticker]
        cap, cap_date = _market_cap_asof(hist, row.session_date)
        ref = _reference_asof(hist)
        rec = row._asdict()
        rec["market_cap"] = cap
        rec["market_cap_asof"] = cap_date
        rec["primary_exchange"] = ref.get("primary_exchange")
        rec["security_name"] = ref.get("name")
        rec["name"] = ref.get("name")
        rec["tradingview_symbol"] = _tradingview_symbol(ticker, ref.get("primary_exchange"))
        enriched.append(rec)
    out = pd.DataFrame(enriched)

    if config.max_market_cap is not None:
        cap = pd.to_numeric(out["market_cap"], errors="coerce")
        if config.missing_market_cap_policy == "exclude":
            out = out[cap.notna() & (cap <= config.max_market_cap)].copy()
        elif config.missing_market_cap_policy == "include":
            out = out[cap.isna() | (cap <= config.max_market_cap)].copy()
        elif config.missing_market_cap_policy == "flag":
            out["market_cap_filter_pass"] = cap.isna() | (cap <= config.max_market_cap)
        else:
            raise ValueError(f"Unsupported missing_market_cap_policy: {config.missing_market_cap_policy}")
    return _sort_candidates_for_review(out)


def _sort_candidates_for_review(candidates: pd.DataFrame, mode: str = "max_push_pct_desc") -> pd.DataFrame:
    if candidates.empty:
        return candidates
    out = candidates.copy()
    sort_maxpush_col = "_sort_visible_maxpush_pct"
    out[sort_maxpush_col] = pd.to_numeric(
        out["pm_open_to_first_push_high_pct"] if "pm_open_to_first_push_high_pct" in out.columns else pd.Series(pd.NA, index=out.index),
        errors="coerce",
    )
    if "pm_open_to_max_high_after_trigger_pct" in out.columns:
        out[sort_maxpush_col] = out[sort_maxpush_col].fillna(
            pd.to_numeric(out["pm_open_to_max_high_after_trigger_pct"], errors="coerce")
        )
    if "max_push_pct_after_trigger" in out.columns:
        out[sort_maxpush_col] = out[sort_maxpush_col].fillna(
            pd.to_numeric(out["max_push_pct_after_trigger"], errors="coerce")
        )
    if mode == "ticker_grouped":
        sort_cols = ["ticker", "session_date", sort_maxpush_col, "das_state"]
        ascending = [True, True, False, False]
    elif mode == "rebreak_fastest":
        sort_cols = ["minutes_from_trigger_to_rebreak", sort_maxpush_col]
        ascending = [True, False]
    else:
        sort_cols = [sort_maxpush_col, "first_push_retention_pct", "first_dip_depth_pct"]
        ascending = [False, False, True]
    sort_cols = [col for col in sort_cols if col in out.columns]
    ascending = ascending[: len(sort_cols)]
    if not sort_cols:
        return out.drop(columns=[sort_maxpush_col], errors="ignore").reset_index(drop=True)
    return (
        out.sort_values(sort_cols, ascending=ascending, na_position="last")
        .drop(columns=[sort_maxpush_col], errors="ignore")
        .reset_index(drop=True)
    )


def _write_manifest(
    run_dir: Path,
    config: DasConfig,
    run_status: str,
    total_files: int,
    files_scanned: int,
    raw_candidate_count: int,
    candidate_count: int,
    partial_output: str | None = None,
    error: str | None = None,
) -> None:
    manifest = {
        "run_id": run_dir.name,
        "run_datetime_utc": _run_datetime_utc_label(run_dir.name),
        "query_name": config.query_name,
        "strategy_id": "das",
        "run_status": run_status,
        "config": asdict(config),
        "total_files": int(total_files),
        "files_scanned": int(files_scanned),
        "raw_candidate_count": int(raw_candidate_count),
        "candidate_count": int(candidate_count),
        "partial_output": partial_output,
        "terminal_launcher_pretty": _terminal_command_from_config(config, pretty=True),
        "terminal_launcher_one_line": _terminal_command_from_config(config, pretty=False),
        "error": error,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (run_dir / "terminal_launcher.ps1").write_text(_terminal_command_from_config(config, pretty=True), encoding="utf-8")
    _write_run_metadata(run_dir, manifest)


def _write_run_metadata(run_dir: Path, manifest: dict) -> None:
    lines = [
        f"# DAS Run Metadata - {manifest.get('run_id')}",
        "",
        f"- status: `{manifest.get('run_status')}`",
        f"- strategy_id: `{manifest.get('strategy_id')}`",
        f"- query_name: `{manifest.get('query_name')}`",
        f"- run_datetime_utc: `{manifest.get('run_datetime_utc')}`",
        f"- total_files: `{manifest.get('total_files')}`",
        f"- files_scanned: `{manifest.get('files_scanned')}`",
        f"- raw_candidate_count: `{manifest.get('raw_candidate_count')}`",
        f"- candidate_count: `{manifest.get('candidate_count')}`",
        f"- partial_output: `{manifest.get('partial_output')}`",
        "",
        "## Terminal launcher",
        "",
        "```powershell",
        manifest.get("terminal_launcher_pretty") or "",
        "```",
        "",
        "## Field definitions",
        "",
    ]
    lines.extend(f"- `{name}`: {description}" for name, description in FIELD_DEFINITIONS)
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `candidate_events_partial.csv`: candidatos parciales durante el run.",
            "- `candidate_events.csv`: candidatos finales en CSV.",
            "- `candidate_events.parquet`: candidatos finales en Parquet cuando existen filas.",
            "",
            "## Delete command",
            "",
            "```powershell",
            _delete_run_command(run_dir),
            "```",
            "",
        ]
    )
    (run_dir / "RUN_METADATA.md").write_text("\n".join(lines), encoding="utf-8")


def create_run_dir(config: DasConfig) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path(config.output_root)
    run_dir = root / f"{config.query_name}_{ts}"
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_manifest(run_dir, config, "running", 0, 0, 0, 0)
    return run_dir


def _flush_partial(run_dir: Path, candidates: list[dict], config: DasConfig, files_scanned: int, total_files: int) -> None:
    partial = pd.DataFrame(candidates)
    partial_path = run_dir / "candidate_events_partial.csv"
    if not partial.empty:
        partial = _sort_candidates_for_review(partial)
        partial.to_csv(partial_path, index=False)
    else:
        pd.DataFrame().to_csv(partial_path, index=False)
    _write_manifest(
        run_dir,
        config,
        "running",
        total_files,
        files_scanned,
        len(candidates),
        len(partial),
        partial_output=partial_path.name,
    )


def find_das_candidates(config: DasConfig, run_dir: Path | None = None) -> pd.DataFrame:
    universe = load_lt1b_universe(Path(config.universe_path)) if config.use_lt1b_universe else None
    print(
        "discovering_files "
        f"data_root={config.data_root} years={','.join(str(year) for year in config.years) or 'all'}",
        flush=True,
    )
    files = _das_iter_parquet_files(
        Path(config.data_root),
        config.tickers,
        config.years,
        universe,
        discovery_progress_every=config.progress_every,
    )
    print(f"files_to_scan={len(files)}", flush=True)
    raw_candidates: list[dict] = []
    last_flush_count = 0
    idx = 0
    for idx, path in enumerate(files, start=1):
        raw_candidates.extend(_candidate_rows_for_file(path, config, config.start_date, config.end_date))
        if config.max_candidates is not None and len(raw_candidates) >= config.max_candidates:
            raw_candidates = raw_candidates[: config.max_candidates]
        new_hits = len(raw_candidates) - last_flush_count
        should_flush = run_dir is not None and config.partial_flush_every > 0 and new_hits >= config.partial_flush_every
        if idx == 1 or (config.progress_every > 0 and idx % config.progress_every == 0):
            print(
                f"progress files_scanned={idx}/{len(files)} raw_candidates={len(raw_candidates)} current={path}",
                flush=True,
            )
        if should_flush:
            _flush_partial(run_dir, raw_candidates, config, idx, len(files))
            last_flush_count = len(raw_candidates)
        if config.max_candidates is not None and len(raw_candidates) >= config.max_candidates:
            break

    if run_dir is not None:
        _flush_partial(run_dir, raw_candidates, config, min(len(files), idx if files else 0), len(files))
    return _postprocess_candidates(raw_candidates, config)


def finalize_run(run_dir: Path, candidates: pd.DataFrame, config: DasConfig) -> None:
    if not candidates.empty:
        candidates.to_parquet(run_dir / "candidate_events.parquet", index=False)
        candidates.to_csv(run_dir / "candidate_events.csv", index=False)
    else:
        pd.DataFrame().to_csv(run_dir / "candidate_events.csv", index=False)
    manifest = _read_manifest(run_dir)
    _write_manifest(
        run_dir,
        config,
        "completed",
        int(manifest.get("total_files", 0)),
        int(manifest.get("files_scanned", 0)),
        int(manifest.get("raw_candidate_count", len(candidates))),
        len(candidates),
        partial_output="candidate_events_partial.csv",
    )


def _read_manifest(run_dir: Path) -> dict:
    path = run_dir / "manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_candidates_from_run(run_dir: Path) -> pd.DataFrame:
    parquet_path = run_dir / "candidate_events.parquet"
    csv_path = run_dir / "candidate_events.csv"
    partial_path = run_dir / "candidate_events_partial.csv"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    for path in [csv_path, partial_path]:
        if path.exists() and path.stat().st_size > 0:
            try:
                return pd.read_csv(path)
            except pd.errors.EmptyDataError:
                return pd.DataFrame()
    return pd.DataFrame()


def _load_partial_candidates_from_run(run_dir: Path) -> pd.DataFrame:
    partial_path = run_dir / "candidate_events_partial.csv"
    if not partial_path.exists() or partial_path.stat().st_size <= 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(partial_path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _load_chart_window(
    ticker: str,
    event_ts_utc: str,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    days_before: int = 3,
    days_after: int = 3,
    price_view: str = "raw",
    vwap_source: str = "calculated",
) -> pd.DataFrame:
    data_root = Path(data_root)
    event_ts = pd.Timestamp(event_ts_utc)
    event_ts = event_ts.tz_localize("UTC") if event_ts.tzinfo is None else event_ts.tz_convert("UTC")
    start = event_ts - pd.Timedelta(days=days_before)
    end = event_ts + pd.Timedelta(days=days_after)
    frames: list[pd.DataFrame] = []
    for year, month in _months_between(start.tz_localize(None), end.tz_localize(None)):
        path = _das_file_for_month(data_root, ticker, year, month)
        if path.exists():
            frames.append(_read_1m_file(path, price_view))
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df = df[(df["ts_utc_dt"] >= start) & (df["ts_utc_dt"] <= end)].copy()
    df = df.sort_values("ts_utc_dt").reset_index(drop=True)
    df["vwap"] = pd.NA
    for _, idx in df.groupby("session_date").groups.items():
        session = df.loc[list(idx)]
        eligible = session["session_segment"].isin(["premarket", "regular", "afterhours"])
        if eligible.any():
            df.loc[session.index[eligible], "vwap"] = _select_vwap(
                session.loc[eligible], vwap_source=vwap_source
            ).to_numpy()
    df["vwap"] = pd.to_numeric(df["vwap"], errors="coerce")
    return df.reset_index(drop=True)


def _enrich_candidate_from_chart_window(candidate: dict, df: pd.DataFrame) -> dict:
    row = dict(candidate)
    if df.empty:
        return row
    session_date = str(row.get("session_date", ""))
    premarket = df[df["session_date"].astype(str).eq(session_date) & df["session_segment"].eq("premarket")].copy()
    if premarket.empty:
        return row
    premarket = premarket.sort_values("ts_utc_dt").reset_index(drop=True)
    premarket["premarket_cum_volume"] = premarket["v"].astype(float).cumsum()

    pm_open_price = _float_or_none(row.get("pm_open_price"))
    if pm_open_price is None:
        pm_open_price = _float_or_none(premarket.iloc[0]["px_o"])
        row["pm_open_price"] = pm_open_price
        row["pm_open_ts_utc"] = premarket.iloc[0]["ts_utc_dt"].isoformat()
        row["pm_open_ts_et"] = premarket.iloc[0]["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z")
    if pm_open_price is None or pm_open_price <= 0:
        return row

    prior_close = _float_or_none(row.get("prior_close"))
    if prior_close is None:
        regular_before = df[
            (df["session_date"].astype(str) < session_date) & df["session_segment"].eq("regular")
        ].copy()
        if not regular_before.empty:
            prior_close = _float_or_none(regular_before.sort_values("ts_utc_dt").iloc[-1]["px_c"])
            row["prior_close"] = prior_close

    scanner_price = _float_or_none(row.get("price_at_trigger"))
    if scanner_price is not None:
        row.setdefault("pm_open_to_scanner_pct", _pct_change(pm_open_price, scanner_price))
        if _clean_value(row.get("pm_open_to_scanner_pct")) is None:
            row["pm_open_to_scanner_pct"] = _pct_change(pm_open_price, scanner_price)
        if _clean_value(row.get("prior_close_to_scanner_pct")) is None:
            row["prior_close_to_scanner_pct"] = _pct_change(prior_close, scanner_price)

    threshold_pct = _float_or_none(row.get("momentum_trigger_pct_threshold")) or 50.0
    if _clean_value(row.get("momentum_trigger_ts_utc")) is None:
        threshold = pm_open_price * (1.0 + threshold_pct / 100.0)
        momentum_rows = premarket[premarket["px_h"].astype(float) >= threshold]
        if not momentum_rows.empty:
            momentum_row = momentum_rows.iloc[0]
            momentum_price = float(momentum_row["px_h"])
            row["momentum_trigger_pct_threshold"] = threshold_pct
            row["momentum_trigger_ts_utc"] = momentum_row["ts_utc_dt"].isoformat()
            row["momentum_trigger_ts_et"] = momentum_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z")
            row["momentum_trigger_price"] = momentum_price
            row["momentum_trigger_volume"] = float(momentum_row["premarket_cum_volume"])
            row["pm_open_to_momentum_trigger_pct"] = _pct_change(pm_open_price, momentum_price)
            row["prior_close_to_momentum_trigger_pct"] = _pct_change(prior_close, momentum_price)

    if _clean_value(row.get("premarket_extension_high")) is None:
        extension_row = premarket.loc[premarket["px_h"].astype(float).idxmax()]
        extension_high = float(extension_row["px_h"])
        row["premarket_extension_high"] = extension_high
        row["premarket_extension_high_ts_utc"] = extension_row["ts_utc_dt"].isoformat()
        row["premarket_extension_high_ts_et"] = extension_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z")
        row["pm_open_to_premarket_extension_high_pct"] = _pct_change(pm_open_price, extension_high)
        row["prior_close_to_premarket_extension_high_pct"] = _pct_change(prior_close, extension_high)

    return row


def _daily_file_for_year(daily_root: Path, ticker: str, year: int) -> Path:
    return daily_root / f"ticker={ticker.upper()}" / f"year={year}" / f"day_aggs_{ticker.upper()}_{year}.parquet"


def _load_daily_context(
    ticker: str,
    session_date: str,
    daily_root: str | Path = DEFAULT_DAILY_ROOT,
    lookback_rows: int = 180,
    lookahead_rows: int = 20,
) -> pd.DataFrame:
    daily_root = Path(daily_root)
    try:
        event_date = pd.Timestamp(str(session_date)).normalize()
    except Exception:
        return pd.DataFrame()
    frames: list[pd.DataFrame] = []
    for year in range(event_date.year - 1, event_date.year + 2):
        path = _daily_file_for_year(daily_root, ticker, year)
        if path.exists():
            try:
                frames.append(pd.read_parquet(path))
            except Exception:
                continue
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    required = {"date", "o", "h", "l", "c", "v"}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["date_dt", "o", "h", "l", "c", "v"]).copy()
    df = df.sort_values("date_dt").drop_duplicates(subset=["date_dt"], keep="last").reset_index(drop=True)
    before = df[df["date_dt"] < event_date].tail(lookback_rows)
    event_and_after = df[df["date_dt"] >= event_date].head(lookahead_rows + 1)
    out = pd.concat([before, event_and_after], ignore_index=True)
    return out.reset_index(drop=True)


def make_das_daily_context_chart(candidate: dict, height: int = NOTEBOOK_SQUARE_CHART_HEIGHT) -> go.Figure:
    df = _load_daily_context(str(candidate.get("ticker", "")), str(candidate.get("session_date", "")))
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.78, 0.22],
    )
    if df.empty:
        fig.add_annotation(
            text="No daily context data found",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16),
        )
        fig.update_layout(height=height, margin=dict(l=35, r=75, t=120, b=35))
        return fig

    x = list(range(len(df)))
    event_date = pd.Timestamp(str(candidate.get("session_date", ""))).normalize()
    event_matches = df.index[df["date_dt"].eq(event_date)].tolist()
    event_idx = event_matches[0] if event_matches else None
    colors = [
        "rgba(16,185,129,0.72)" if float(close) >= float(open_) else "rgba(239,68,68,0.72)"
        for open_, close in zip(df["o"], df["c"])
    ]
    fig.add_trace(
        go.Candlestick(
            x=x,
            open=df["o"],
            high=df["h"],
            low=df["l"],
            close=df["c"],
            increasing_line_color="#10b981",
            increasing_fillcolor="rgba(16,185,129,0.45)",
            decreasing_line_color="#ef4444",
            decreasing_fillcolor="rgba(239,68,68,0.45)",
            name="daily candles",
            text=[
                f"{date}<br>O {open_:.4f}<br>H {high:.4f}<br>L {low:.4f}<br>C {close:.4f}"
                for date, open_, high, low, close in zip(
                    df["date_dt"].dt.strftime("%Y-%m-%d"),
                    df["o"].astype(float),
                    df["h"].astype(float),
                    df["l"].astype(float),
                    df["c"].astype(float),
                )
            ],
            hoverinfo="text",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=x,
            y=df["v"],
            marker_color=colors,
            name="daily volume",
            hovertext=df["date_dt"].dt.strftime("%Y-%m-%d"),
            hovertemplate="%{hovertext}<br>Volume %{y:,.0f}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    if event_idx is not None:
        price_high = pd.to_numeric(df["h"], errors="coerce").max()
        if pd.notna(price_high):
            fig.add_annotation(
                x=event_idx,
                y=float(price_high),
                text="event day",
                showarrow=False,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=11, color="rgba(30,64,175,0.98)"),
                bgcolor="rgba(255,255,255,0.78)",
                bordercolor="rgba(37,99,235,0.35)",
                borderwidth=1,
                row=1,
                col=1,
            )
        prior = df.iloc[:event_idx].copy()
        for window, label, color in [
            (20, "prior 20D high", "rgba(234,88,12,0.85)"),
            (60, "prior 60D high", "rgba(124,58,237,0.85)"),
        ]:
            if len(prior) >= min(5, window):
                level = pd.to_numeric(prior.tail(window)["h"], errors="coerce").max()
                if pd.notna(level):
                    fig.add_shape(
                        type="line",
                        x0=max(0, event_idx - window),
                        x1=event_idx,
                        y0=float(level),
                        y1=float(level),
                        line=dict(color=color, width=1.2, dash="dash"),
                        row=1,
                        col=1,
                    )
                    fig.add_annotation(
                        x=event_idx,
                        y=float(level),
                        text=label,
                        showarrow=False,
                        xanchor="left",
                        yanchor="bottom",
                        font=dict(size=11, color=color),
                        bgcolor="rgba(255,255,255,0.70)",
                        row=1,
                        col=1,
                    )

    tick_step = max(1, len(df) // 8)
    tickvals = x[::tick_step]
    ticktext = df.loc[tickvals, "date_dt"].dt.strftime("%Y-%m-%d").tolist()
    symbol = candidate.get("tradingview_symbol") or candidate.get("ticker", "")
    fig.update_layout(
        title=dict(
            text=f"{symbol} DAS daily context | event_date={candidate.get('session_date')}",
            x=0.01,
            xanchor="left",
            font=dict(size=15),
        ),
        height=height,
        margin=dict(l=35, r=75, t=150, b=35),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(tickmode="array", tickvals=tickvals, ticktext=ticktext, rangeslider_visible=False)
    fig.update_yaxes(gridcolor="rgba(226,232,240,0.9)", zeroline=False)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig


def _candidate_for_base_chart(candidate: dict) -> dict:
    row = dict(candidate)
    level = _clean_value(row.get("first_push_high"))
    level_ts_utc = _clean_value(row.get("first_push_high_ts_utc"))
    level_ts_et = _clean_value(row.get("first_push_high_ts_et"))
    if level is None:
        level = _clean_value(row.get("max_high_after_trigger")) or _clean_value(row.get("price_at_trigger"))
        level_ts_utc = _clean_value(row.get("max_high_after_trigger_ts_utc")) or _clean_value(row.get("scanner_trigger_ts_utc"))
        level_ts_et = _clean_value(row.get("max_high_after_trigger_ts_et")) or _clean_value(row.get("scanner_trigger_ts_et"))
    event_ts_utc = _candidate_event_ts_utc(row)
    event_ts_et = _clean_value(row.get("first_rebreak_ts_et")) or _clean_value(row.get("scanner_trigger_ts_et"))
    row["pmh"] = level
    row["pmh_ts_utc"] = level_ts_utc
    row["pmh_ts_et"] = level_ts_et
    row["break_ts_utc"] = event_ts_utc
    row["break_ts_et"] = event_ts_et
    row["gap_pct"] = _visible_maxpush_pct(row)
    return row


def _candidate_event_ts_utc(candidate: dict) -> str:
    return (
        _clean_value(candidate.get("first_rebreak_ts_utc"))
        or _clean_value(candidate.get("scanner_trigger_ts_utc"))
        or _clean_value(candidate.get("max_high_after_trigger_ts_utc"))
    )


def _bar_x_for_ts(chart_df: pd.DataFrame, ts_utc: str | None) -> int | None:
    ts_value = _clean_value(ts_utc)
    if ts_value is None:
        return None
    try:
        ts = pd.Timestamp(ts_value)
    except Exception:
        return None
    if pd.isna(ts):
        return None
    ts = ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")
    if chart_df.empty:
        return None
    if ts < chart_df["ts_utc_dt"].min() or ts > chart_df["ts_utc_dt"].max():
        return None
    deltas = (chart_df["ts_utc_dt"] - ts).abs().dropna()
    if deltas.empty:
        return None
    return int(chart_df.loc[deltas.idxmin(), "bar_index"])


def _remove_inherited_gap_measurements(fig: go.Figure) -> None:
    fig.data = tuple(trace for trace in fig.data if getattr(trace, "name", None) not in INHERITED_GAP_TRACE_NAMES)
    kept_annotations = []
    for ann in fig.layout.annotations:
        text = str(getattr(ann, "text", ""))
        is_inherited_gap_pct = (text.startswith("+") or text.startswith("-")) and text.endswith("%")
        if not is_inherited_gap_pct:
            kept_annotations.append(ann)
    fig.layout.annotations = tuple(kept_annotations)


def _add_premarket_open_to_first_push_measurement(
    fig: go.Figure,
    chart_df: pd.DataFrame,
    candidate: dict,
    x_values: pd.Series,
) -> None:
    if chart_df.empty:
        return
    session_date = str(candidate.get("session_date", ""))
    premarket_rows = chart_df[chart_df["session_date"].eq(session_date) & chart_df["session_segment"].eq("premarket")]
    if premarket_rows.empty:
        return
    first_push_high = _clean_value(candidate.get("first_push_high"))
    push_high_ts = _clean_value(candidate.get("first_push_high_ts_utc"))
    if first_push_high is None or not push_high_ts:
        return
    push_x = _bar_x_for_ts(chart_df, str(push_high_ts))
    if push_x is None:
        return
    pm_open_row = premarket_rows.iloc[0]
    pm_open = float(pm_open_row["px_o"])
    if pm_open <= 0:
        return
    push_high = float(first_push_high)
    push_pct = (push_high - pm_open) / pm_open * 100.0
    x_value = x_values.iloc[push_x] if isinstance(x_values, pd.Series) else x_values[push_x]
    fig.add_trace(
        go.Scatter(
            x=[x_value, x_value],
            y=[pm_open, push_high],
            mode="lines",
            line=dict(color="rgba(37,99,235,0.62)", width=1),
            name="PM open to first push",
            hovertemplate="PM open to first push<br>%{y:.4f}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_annotation(
        x=x_value,
        y=(pm_open + push_high) / 2.0,
        text=f"{push_pct:+.1f}%",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        font=dict(size=12, color="rgba(37,99,235,0.95)"),
        bgcolor="rgba(255,255,255,0.72)",
        row=1,
        col=1,
    )


def _add_premarket_open_to_extension_high_measurement(
    fig: go.Figure,
    chart_df: pd.DataFrame,
    candidate: dict,
    x_values: pd.Series,
) -> None:
    if chart_df.empty:
        return
    extension_high = _clean_value(candidate.get("premarket_extension_high"))
    extension_ts = _clean_value(candidate.get("premarket_extension_high_ts_utc"))
    first_push_ts = _clean_value(candidate.get("first_push_high_ts_utc"))
    first_push_high = _clean_value(candidate.get("first_push_high"))
    if extension_high is None or not extension_ts:
        return
    if first_push_ts == extension_ts and _float_close(extension_high, first_push_high):
        return
    extension_x = _bar_x_for_ts(chart_df, str(extension_ts))
    if extension_x is None:
        return
    pm_open = _clean_value(candidate.get("pm_open_price"))
    if pm_open is None or float(pm_open) <= 0:
        return
    extension_pct = _clean_value(candidate.get("pm_open_to_premarket_extension_high_pct"))
    if extension_pct is None:
        extension_pct = _pct_change(float(pm_open), float(extension_high))
    x_value = _x_value_at(x_values, int(extension_x))
    fig.add_trace(
        go.Scatter(
            x=[x_value, x_value],
            y=[float(pm_open), float(extension_high)],
            mode="lines",
            line=dict(color="rgba(14,165,233,0.62)", width=1),
            name="PM open to PM extension high",
            hovertemplate="PM open to PM extension high<br>%{y:.4f}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_annotation(
        x=x_value,
        y=(float(pm_open) + float(extension_high)) / 2.0,
        text=f"PM ext {float(extension_pct):+.1f}%" if extension_pct is not None else "PM ext na",
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        font=dict(size=12, color="rgba(14,116,144,0.95)"),
        bgcolor="rgba(255,255,255,0.72)",
        row=1,
        col=1,
    )


def _float_close(left: object, right: object, tolerance: float = 1e-8) -> bool:
    left_value = _clean_value(left)
    right_value = _clean_value(right)
    if left_value is None or right_value is None:
        return False
    try:
        return abs(float(left_value) - float(right_value)) <= tolerance
    except Exception:
        return False


def _remove_inherited_first_push_level(fig: go.Figure, level: object) -> None:
    kept_shapes = []
    for shape in fig.layout.shapes:
        line = getattr(shape, "line", None)
        color = str(getattr(line, "color", "") or "")
        is_red_level = "220,38,38" in color or color.lower() in {"red", "#dc2626"}
        is_same_level = _float_close(getattr(shape, "y0", None), level) and _float_close(getattr(shape, "y1", None), level)
        if getattr(shape, "type", None) == "line" and is_red_level and is_same_level:
            continue
        kept_shapes.append(shape)
    fig.layout.shapes = tuple(kept_shapes)

    kept_annotations = []
    for ann in fig.layout.annotations:
        text = str(getattr(ann, "text", ""))
        if text in {"PMH", "first push high", "max high after trigger"}:
            continue
        kept_annotations.append(ann)
    fig.layout.annotations = tuple(kept_annotations)


def _x_value_at(x_values: pd.Series, idx: int):
    return x_values.iloc[idx] if isinstance(x_values, pd.Series) else x_values[idx]


def _add_first_push_level_segment(
    fig: go.Figure,
    chart_df: pd.DataFrame,
    candidate: dict,
    x_values: pd.Series,
) -> None:
    level = _clean_value(candidate.get("first_push_high")) or _clean_value(candidate.get("max_high_after_trigger"))
    level_ts = _clean_value(candidate.get("first_push_high_ts_utc")) or _clean_value(candidate.get("max_high_after_trigger_ts_utc"))
    if chart_df.empty or level is None or not level_ts:
        return
    end_x = _bar_x_for_ts(chart_df, str(level_ts))
    if end_x is None:
        return
    _remove_inherited_first_push_level(fig, level)
    start_value = _x_value_at(x_values, 0)
    end_value = _x_value_at(x_values, end_x)
    fig.add_trace(
        go.Scatter(
            x=[start_value, end_value],
            y=[float(level), float(level)],
            mode="lines",
            line=dict(color="rgba(220,38,38,0.95)", width=1.2, dash="dash"),
            name="first push high",
            hovertemplate="first push high<br>%{y:.4f}<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_annotation(
        x=end_value,
        y=float(level),
        text="first push high",
        showarrow=False,
        xanchor="right",
        yanchor="bottom",
        yshift=6,
        font=dict(size=11, color="rgba(127,29,29,0.95)"),
        bgcolor="rgba(255,255,255,0.62)",
        row=1,
        col=1,
    )


def _format_compact_volume(value: object) -> str:
    clean = _clean_value(value)
    if clean is None:
        return "na"
    try:
        volume = float(clean)
    except Exception:
        return "na"
    if abs(volume) >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    if abs(volume) >= 1_000:
        return f"{volume / 1_000:.0f}k"
    return f"{volume:.0f}"


def _trigger_marker_text(
    candidate: dict,
    pct_key: str,
    prior_pct_key: str,
    price_key: str,
    volume_key: str,
    label: str,
) -> str:
    pct = _clean_value(candidate.get(pct_key))
    prior_pct = _clean_value(candidate.get(prior_pct_key))
    price = _clean_value(candidate.get(price_key))
    volume = _clean_value(candidate.get(volume_key))
    pct_label = f"PM open {float(pct):+.1f}%" if pct is not None else "PM open na"
    prior_label = f"Prior close {float(prior_pct):+.1f}%" if prior_pct is not None else "Prior close na"
    price_label = f"${float(price):.4f}" if price is not None else "$na"
    volume_label = f"vol {_format_compact_volume(volume)}"
    return f"{pct_label}<br>{prior_label}<br>{price_label}<br>{volume_label}<br>{label}"


def _scanner_trigger_marker_text(candidate: dict) -> str:
    return _trigger_marker_text(
        candidate,
        "pm_open_to_scanner_pct",
        "prior_close_to_scanner_pct",
        "price_at_trigger",
        "premarket_volume_at_trigger",
        "scanner trigger",
    )


def _momentum_trigger_marker_text(candidate: dict) -> str:
    return _trigger_marker_text(
        candidate,
        "pm_open_to_momentum_trigger_pct",
        "prior_close_to_momentum_trigger_pct",
        "momentum_trigger_price",
        "momentum_trigger_volume",
        "momentum trigger",
    )


def _remove_selected_diagnostic_marker_traces(fig: go.Figure, names: set[str]) -> None:
    fig.data = tuple(trace for trace in fig.data if str(getattr(trace, "name", "")) not in names)


def make_das_chart(
    df: pd.DataFrame,
    candidate: dict,
    y_padding_pct: float = 0.40,
    compact_xaxis: bool = True,
    chart_label: str = "interactive",
    show_rangeslider: bool = True,
    height: int = 900,
    static_axes: bool = False,
    y_padding_override_pct: float | None = None,
    split_events: pd.DataFrame | None = None,
    show_diagnostic_markers: bool = True,
    show_legend: bool = True,
) -> go.Figure:
    base_candidate = _candidate_for_base_chart(candidate)
    fig = make_strategy_1m_chart(
        df,
        base_candidate,
        y_padding_pct=y_padding_pct,
        compact_xaxis=compact_xaxis,
        chart_label=chart_label,
        show_rangeslider=show_rangeslider,
        height=height,
        static_axes=static_axes,
        y_padding_override_pct=y_padding_override_pct,
        split_events=split_events,
    )
    symbol = candidate.get("tradingview_symbol") or candidate.get("ticker", "")
    visible_maxpush = _visible_maxpush_pct(candidate)
    visible_maxpush_label = f"{visible_maxpush:.4f}%" if visible_maxpush is not None else "na"
    title_text = (
        f"{symbol} DAS scanner candidate<br>"
        f"{chart_label} | state={candidate.get('das_state')} | "
        f"maxpush={visible_maxpush_label} | dip={candidate.get('first_dip_depth_pct')}%<br>"
        f"rebreak={candidate.get('first_rebreak_ts_et')} | "
        f"type={candidate.get('first_rebreak_type')} | wick={candidate.get('first_green_wick_dip_type')}"
    )
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.01,
            xanchor="left",
            font=dict(size=15),
        ),
        margin=dict(l=35, r=75, t=230, b=35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            tracegroupgap=10,
            entrywidth=185,
            entrywidthmode="pixels",
        ),
        showlegend=show_legend,
    )
    fig.layout.yaxis.domain = list(PRICE_PANEL_DOMAIN)
    fig.layout.yaxis2.domain = list(VOLUME_PANEL_DOMAIN)
    _remove_inherited_gap_measurements(fig)
    has_rebreak = _clean_value(candidate.get("first_rebreak_ts_utc")) is not None
    for trace in fig.data:
        if getattr(trace, "name", "") == "Gap and Go trigger":
            trace.name = "DAS rebreak trigger" if has_rebreak else "scanner trigger"
            trace.hovertemplate = (
                "DAS rebreak<br>first push high: %{y:.4f}<extra></extra>"
                if has_rebreak
                else "scanner trigger<br>reference level: %{y:.4f}<extra></extra>"
            )
    if not show_diagnostic_markers:
        _remove_selected_diagnostic_marker_traces(fig, {"DAS rebreak trigger"})
    chart_df = df.copy().reset_index(drop=True)
    chart_df["bar_index"] = chart_df.index
    x_values = chart_df["bar_index"] if compact_xaxis else chart_df["ts_et_naive"]
    _add_first_push_level_segment(fig, chart_df, candidate, x_values)
    _add_premarket_open_to_first_push_measurement(fig, chart_df, candidate, x_values)
    _add_premarket_open_to_extension_high_measurement(fig, chart_df, candidate, x_values)
    ts_to_x = {
        "scanner": _bar_x_for_ts(chart_df, candidate.get("scanner_trigger_ts_utc")),
        "momentum": _bar_x_for_ts(chart_df, candidate.get("momentum_trigger_ts_utc")),
        "push_high": _bar_x_for_ts(chart_df, candidate.get("first_push_high_ts_utc")),
        "dip_low": _bar_x_for_ts(chart_df, candidate.get("first_dip_low_ts_utc")),
        "rebreak": _bar_x_for_ts(chart_df, candidate.get("first_rebreak_ts_utc")),
    }
    hidden_marker_labels = {"first push high", "first dip low", "DAS rebreak"}
    marker_rows = [
        ("scanner trigger", ts_to_x.get("scanner"), candidate.get("price_at_trigger"), "rgba(59,130,246,0.85)"),
        (
            "momentum trigger",
            ts_to_x.get("momentum"),
            candidate.get("momentum_trigger_price"),
            "rgba(14,165,233,0.85)",
        ),
        ("first push high", ts_to_x["push_high"], candidate.get("first_push_high"), "rgba(37,99,235,0.85)"),
        ("first dip low", ts_to_x["dip_low"], candidate.get("first_dip_low"), "rgba(234,88,12,0.85)"),
        ("DAS rebreak", ts_to_x["rebreak"], candidate.get("first_push_high"), "rgba(37,99,235,0.95)"),
    ]
    for label, x, y, color in marker_rows:
        if not show_diagnostic_markers and label in hidden_marker_labels:
            continue
        if x is None or y is None or pd.isna(y):
            continue
        marker_x = _x_value_at(x_values, int(x))
        marker_y = float(y)
        marker_mode = "markers" if label in {"scanner trigger", "momentum trigger"} else (
            "markers+text"
            if label in {"first dip low", "DAS rebreak"}
            else "markers"
        )
        marker_text = "" if label in {"scanner trigger", "momentum trigger"} else (
            label if label in {"first dip low", "DAS rebreak"} else ""
        )
        trigger_text = (
            _scanner_trigger_marker_text(candidate)
            if label == "scanner trigger"
            else _momentum_trigger_marker_text(candidate)
            if label == "momentum trigger"
            else ""
        )
        fig.add_trace(
            go.Scatter(
                x=[marker_x],
                y=[marker_y],
                mode=marker_mode,
                marker=dict(size=16, color=color, line=dict(color="white", width=1)),
                text=[marker_text],
                textposition="top center",
                name=label,
                hovertemplate=(
                    f"{label}<br>"
                    f"{trigger_text.replace('<br>', '<br>')}<br>"
                    "%{y:.4f}<extra></extra>"
                    if label in {"scanner trigger", "momentum trigger"}
                    else f"{label}<br>%{{y:.4f}}<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
        if label in {"scanner trigger", "momentum trigger"}:
            x_position = int(x) / max(len(chart_df) - 1, 1)
            ax = -125 if x_position > 0.72 else 125
            ay = 105 if label == "scanner trigger" else 145
            fig.add_annotation(
                x=marker_x,
                y=marker_y,
                text=trigger_text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor="rgba(37,99,235,0.8)" if label == "scanner trigger" else "rgba(14,116,144,0.85)",
                ax=ax,
                ay=ay,
                align="left",
                xanchor="left" if ax > 0 else "right",
                yanchor="top",
                font=dict(
                    size=11,
                    color="rgba(30,64,175,0.98)"
                    if label == "scanner trigger"
                    else "rgba(14,116,144,0.98)",
                ),
                bgcolor="rgba(255,255,255,0.82)",
                bordercolor="rgba(37,99,235,0.35)"
                if label == "scanner trigger"
                else "rgba(14,116,144,0.35)",
                borderwidth=1,
                row=1,
                col=1,
            )
    return fig


def _detail_window_until_regular_close(df: pd.DataFrame, candidate: dict) -> pd.DataFrame:
    if df.empty:
        return df
    session_date = str(candidate.get("session_date", ""))
    event_rows = df[df["session_date"].eq(session_date)]
    if event_rows.empty:
        return df
    event_midnight = event_rows["ts_et"].iloc[0].normalize()
    end_et = event_midnight + pd.Timedelta(hours=16)
    prior_dates = sorted(date for date in df["session_date"].dropna().unique().tolist() if str(date) < session_date)
    if prior_dates:
        prior_rows = df[df["session_date"].eq(prior_dates[-1])]
        prior_midnight = prior_rows["ts_et"].iloc[0].normalize()
        start_et = prior_midnight + pd.Timedelta(hours=15)
    else:
        start_et = event_midnight + pd.Timedelta(hours=4)
    detail = df[(df["ts_et"] >= start_et) & (df["ts_et"] <= end_et)].copy()
    return detail if not detail.empty else event_rows.copy()


def _premarket_window_for_event_day(df: pd.DataFrame, candidate: dict) -> pd.DataFrame:
    if df.empty:
        return df
    session_date = str(candidate.get("session_date", ""))
    event_rows = df[df["session_date"].eq(session_date)].copy()
    if event_rows.empty:
        return df
    event_midnight = event_rows["ts_et"].iloc[0].normalize()
    start_et = event_midnight + pd.Timedelta(hours=3, minutes=30)
    end_et = event_midnight + pd.Timedelta(hours=10)
    morning = event_rows[(event_rows["ts_et"] >= start_et) & (event_rows["ts_et"] <= end_et)].copy()
    return morning if not morning.empty else event_rows


def _candidate_for_premarket_chart(candidate: dict, premarket_df: pd.DataFrame) -> dict:
    row = dict(candidate)
    if premarket_df.empty:
        return row
    start_ts = premarket_df["ts_utc_dt"].min()
    end_ts = premarket_df["ts_utc_dt"].max()

    def _inside(ts_utc: str | None) -> bool:
        if not ts_utc:
            return False
        ts = pd.Timestamp(ts_utc)
        ts = ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")
        return start_ts <= ts <= end_ts

    for prefix in ["first_rebreak", "first_green_wick_dip"]:
        ts_key = f"{prefix}_ts_utc"
        if not _inside(_clean_value(row.get(ts_key))):
            row[f"{prefix}_ts_utc"] = None
            row[f"{prefix}_ts_et"] = None

    for prefix in ["first_dip_low", "first_push_high", "first_push_start"]:
        ts_key = f"{prefix}_ts_utc"
        if not _inside(_clean_value(row.get(ts_key))):
            row[f"{prefix}_ts_utc"] = None
            row[f"{prefix}_ts_et"] = None

    row["regular_open"] = None
    return row


def render_candidate_charts(
    candidate: dict,
    data_root: str,
    price_view: str,
    vwap_source: str,
    y_padding_pct: float,
) -> list[tuple[str, go.Figure]]:
    df = _load_chart_window(
        candidate["ticker"],
        _candidate_event_ts_utc(candidate),
        data_root,
        price_view=price_view,
        vwap_source=vwap_source,
    )
    candidate = _enrich_candidate_from_chart_window(candidate, df)
    detail_until_close_df = _detail_window_until_regular_close(df, candidate)
    premarket_df = _premarket_window_for_event_day(df, candidate)
    premarket_candidate = _candidate_for_premarket_chart(candidate, premarket_df)
    split_events = load_split_events_for_chart(
        candidate["ticker"],
        str(df["session_date"].min()) if not df.empty else str(candidate.get("session_date", "")),
        str(df["session_date"].max()) if not df.empty else str(candidate.get("session_date", "")),
        splits_root=DEFAULT_REFERENCE_SPLITS_ROOT,
    )
    return [
        (
            "1. Interactive 3-day chart",
            make_das_chart(
                df,
                candidate,
                y_padding_pct=y_padding_pct,
                chart_label="interactive 3-day window",
                show_rangeslider=True,
                height=NOTEBOOK_SQUARE_CHART_HEIGHT,
                static_axes=False,
                split_events=split_events,
            ),
        ),
        (
            "2. Three-day overview",
            make_das_chart(
                df,
                candidate,
                y_padding_pct=y_padding_pct,
                chart_label="3-day overview",
                show_rangeslider=False,
                height=NOTEBOOK_SQUARE_CHART_HEIGHT,
                static_axes=True,
                y_padding_override_pct=0.03,
                split_events=split_events,
            ),
        ),
        (
            "3. Event-day premarket detail",
            make_das_chart(
                premarket_df,
                premarket_candidate,
                y_padding_pct=y_padding_pct,
                chart_label="03:30-10:00 NY detail",
                show_rangeslider=False,
                height=NOTEBOOK_SQUARE_CHART_HEIGHT,
                static_axes=True,
                y_padding_override_pct=0.015,
                split_events=split_events,
            ),
        ),
        (
            "4. Event-day detail until 16:00 NY",
            make_das_chart(
                detail_until_close_df,
                candidate,
                y_padding_pct=y_padding_pct,
                chart_label="detail until 16:00 NY",
                show_rangeslider=False,
                height=NOTEBOOK_SQUARE_CHART_HEIGHT,
                static_axes=True,
                y_padding_override_pct=0.03,
                split_events=split_events,
            ),
        ),
        (
            "5. Daily context",
            make_das_daily_context_chart(candidate, height=NOTEBOOK_SQUARE_CHART_HEIGHT),
        ),
    ]


def _ensure_plotly_png_export_available() -> None:
    try:
        import kaleido  # noqa: F401
    except Exception as exc:
        raise RuntimeError(
            "Could not export PNG. Plotly image export requires the `kaleido` package in the active Python environment."
        ) from exc


def _renderer_source_hash() -> str:
    path = Path(__file__).resolve()
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _visual_threshold_label(candidate: dict) -> str:
    value = _clean_value(candidate.get("momentum_trigger_pct_threshold"))
    if value is None:
        value = _clean_value(candidate.get("momentum_trigger_pct")) or 50.0
    try:
        numeric = float(value)
        return f"{numeric:g}"
    except Exception:
        return _safe_filename(str(value))


def _image_pixel_geometry(
    chart_df: pd.DataFrame,
    y_padding_override_pct: float = 0.03,
    axis_ranges: dict[str, tuple[float, float]] | None = None,
) -> dict[str, float]:
    image_width = float(EXPORT_SQUARE_CHART_WIDTH * 2)
    image_height = float(EXPORT_SQUARE_CHART_HEIGHT * 2)
    margin_left = 35.0 * 2.0
    margin_right = 75.0 * 2.0
    margin_top = 230.0 * 2.0
    margin_bottom = 35.0 * 2.0
    plot_width = image_width - margin_left - margin_right
    plot_height = image_height - margin_top - margin_bottom
    price_top = margin_top
    price_bottom = margin_top + (1.0 - PRICE_PANEL_DOMAIN[0]) * plot_height
    low = float(pd.to_numeric(chart_df["px_l"], errors="coerce").min())
    high = float(pd.to_numeric(chart_df["px_h"], errors="coerce").max())
    span = max(high - low, high * 0.05, 0.01)
    pad = span * y_padding_override_pct
    x_range = axis_ranges.get("xaxis") if axis_ranges else None
    y_range = axis_ranges.get("yaxis") if axis_ranges else None
    x_min, x_max = (float(x_range[0]), float(x_range[1])) if x_range else (0.0, float(max(len(chart_df) - 1, 1)))
    y_min, y_max = (float(y_range[0]), float(y_range[1])) if y_range else (low - pad, high + pad)
    return {
        "image_width": image_width,
        "image_height": image_height,
        "plot_left": margin_left,
        "plot_width": plot_width,
        "price_top": price_top,
        "price_bottom": price_bottom,
        "price_min": y_min,
        "price_max": y_max,
        "x_min": x_min,
        "x_max": x_max,
        "bar_count": float(max(len(chart_df), 1)),
    }


def _visual_anchor_px(chart_df: pd.DataFrame, geometry: dict[str, float], ts_utc: object, price: object) -> tuple[float, float] | None:
    x = _bar_x_for_ts(chart_df, str(ts_utc) if _clean_value(ts_utc) is not None else None)
    clean_price = _clean_value(price)
    if x is None or clean_price is None:
        return None
    x_min = geometry.get("x_min", 0.0)
    x_max = geometry.get("x_max", max(geometry["bar_count"] - 1.0, 1.0))
    x_span = max(float(x_max) - float(x_min), 1.0)
    anchor_x = geometry["plot_left"] + ((float(x) - float(x_min)) / x_span) * geometry["plot_width"]
    y_min = geometry["price_min"]
    y_max = geometry["price_max"]
    if y_max <= y_min:
        return None
    anchor_y = geometry["price_bottom"] - ((float(clean_price) - y_min) / (y_max - y_min)) * (
        geometry["price_bottom"] - geometry["price_top"]
    )
    return anchor_x, anchor_y


def _estimate_label_size(label_text: str) -> tuple[float, float]:
    lines = str(label_text).replace("<br>", "\n").splitlines() or [""]
    max_chars = max(len(line) for line in lines)
    width = min(max(136.0, max_chars * 8.4 + 24.0), 340.0)
    height = max(38.0, len(lines) * 20.0 + 16.0)
    return width, height


def _bbox_intersects(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> bool:
    return not (left[2] <= right[0] or right[2] <= left[0] or left[3] <= right[1] or right[3] <= left[1])


def _visual_candle_bboxes(chart_df: pd.DataFrame, geometry: dict[str, float]) -> list[tuple[float, float, float, float]]:
    blocked: list[tuple[float, float, float, float]] = []
    y_min = geometry["price_min"]
    y_max = geometry["price_max"]
    if y_max <= y_min:
        return blocked
    bar_denominator = max(geometry["bar_count"] - 1.0, 1.0)
    price_height = geometry["price_bottom"] - geometry["price_top"]
    for idx, row in chart_df.reset_index(drop=True).iterrows():
        high = _clean_value(row.get("px_h"))
        low = _clean_value(row.get("px_l"))
        if high is None or low is None:
            continue
        x = geometry["plot_left"] + (float(idx) / bar_denominator) * geometry["plot_width"]
        y_high = geometry["price_bottom"] - ((float(high) - y_min) / (y_max - y_min)) * price_height
        y_low = geometry["price_bottom"] - ((float(low) - y_min) / (y_max - y_min)) * price_height
        blocked.append((x - 22.0, min(y_high, y_low) - 16.0, x + 22.0, max(y_high, y_low) + 16.0))
    return blocked


def _visual_premarket_label_bounds(chart_df: pd.DataFrame, geometry: dict[str, float]) -> tuple[float, float, float, float]:
    working = chart_df.reset_index(drop=True)
    if "session_segment" in working.columns:
        mask = working["session_segment"].astype(str).eq("premarket")
        if mask.any():
            idxs = list(working.index[mask])
        else:
            idxs = list(working.index)
    else:
        idxs = list(working.index)
    if not idxs:
        idxs = [0]
    x_min_range = float(geometry.get("x_min", 0.0))
    x_max_range = float(geometry.get("x_max", max(geometry["bar_count"] - 1.0, 1.0)))
    x_span = max(x_max_range - x_min_range, 1.0)
    x_min = geometry["plot_left"] + ((float(min(idxs)) - x_min_range) / x_span) * geometry["plot_width"] + 12.0
    x_max = geometry["plot_left"] + ((float(max(idxs)) - x_min_range) / x_span) * geometry["plot_width"] - 12.0
    if x_max <= x_min:
        x_min = geometry["plot_left"] + 12.0
        x_max = geometry["plot_left"] + geometry["plot_width"] - 12.0
    return (
        max(12.0, x_min),
        max(12.0, geometry["price_top"] + 14.0),
        min(geometry["image_width"] - 12.0, x_max),
        min(geometry["image_height"] - 12.0, geometry["price_bottom"] - 14.0),
    )


def _place_visual_label(
    anchor_x: float,
    anchor_y: float,
    label_text: str,
    placed: list[tuple[float, float, float, float]],
    image_width: float,
    image_height: float,
    blocked: list[tuple[float, float, float, float]] | None = None,
    allowed_bounds: tuple[float, float, float, float] | None = None,
) -> tuple[float, float, float, float]:
    width, height = _estimate_label_size(label_text)
    blocked = blocked or []
    if allowed_bounds is None:
        allowed_bounds = (12.0, 12.0, image_width - 12.0, image_height - 12.0)
    min_x, min_y, max_x, max_y = allowed_bounds
    min_x = max(12.0, min_x)
    min_y = max(12.0, min_y)
    max_x = min(image_width - 12.0, max_x)
    max_y = min(image_height - 12.0, max_y)
    if max_x - min_x < width:
        min_x = 12.0
        max_x = image_width - 12.0
    if max_y - min_y < height:
        min_y = 12.0
        max_y = image_height - 12.0

    def _candidate(dx: float, dy: float) -> tuple[float, float, float, float]:
        x0 = min(max(anchor_x + dx, min_x), max_x - width)
        y0 = min(max(anchor_y + dy, min_y), max_y - height)
        return (x0, y0, x0 + width, y0 + height)

    offsets = [
        (72.0, -300.0),
        (-width - 72.0, -300.0),
        (260.0, -210.0),
        (-width - 260.0, -210.0),
        (72.0, 220.0),
        (-width - 72.0, 220.0),
        (340.0, 40.0),
        (-width - 340.0, 40.0),
        (72.0, -430.0),
        (-width - 72.0, -430.0),
        (72.0, 340.0),
        (-width - 72.0, 340.0),
    ]
    occupied = placed + blocked
    for dx, dy in offsets:
        bbox = _candidate(dx, dy)
        if not any(_bbox_intersects(bbox, existing) for existing in occupied):
            placed.append(bbox)
            return bbox

    # Grid search inside the premarket price panel. If this fails, do not silently print a bad chart.
    x_step = 36.0
    y_step = 28.0
    y = min_y
    while y + height <= max_y:
        x = min_x
        while x + width <= max_x:
            bbox = (x, y, x + width, y + height)
            if not any(_bbox_intersects(bbox, existing) for existing in occupied):
                placed.append(bbox)
                return bbox
            x += x_step
        y += y_step
    raise RuntimeError("Could not place visual label inside premarket window without overlapping candles or labels.")

def _format_compact_number(value: object) -> str:
    clean = _clean_value(value)
    if clean is None:
        return "na"
    try:
        number = float(clean)
    except Exception:
        return "na"
    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    if abs(number) >= 1_000:
        return f"{number / 1_000:.0f}k"
    return f"{number:.0f}"



def _same_timestamp_minute(left: object, right: object) -> bool:
    left_clean = _clean_value(left)
    right_clean = _clean_value(right)
    if left_clean is None or right_clean is None:
        return False
    try:
        left_ts = pd.Timestamp(left_clean)
        right_ts = pd.Timestamp(right_clean)
    except Exception:
        return False
    if left_ts.tzinfo is None:
        left_ts = left_ts.tz_localize("UTC")
    else:
        left_ts = left_ts.tz_convert("UTC")
    if right_ts.tzinfo is None:
        right_ts = right_ts.tz_localize("UTC")
    else:
        right_ts = right_ts.tz_convert("UTC")
    return left_ts.floor("min") == right_ts.floor("min")


def _visual_momentum_gate_fields(candidate: dict) -> dict[str, object]:
    scanner_ts = _clean_value(candidate.get("scanner_trigger_ts_utc"))
    momentum_ts = _clean_value(candidate.get("momentum_trigger_ts_utc"))
    scanner_pd = pd.Timestamp(scanner_ts) if scanner_ts is not None else None
    momentum_pd = pd.Timestamp(momentum_ts) if momentum_ts is not None else None
    use_scanner_gate = False
    if scanner_pd is not None and momentum_pd is not None:
        use_scanner_gate = scanner_pd >= momentum_pd
    elif scanner_pd is not None:
        use_scanner_gate = True

    if use_scanner_gate:
        gate_ts_utc = scanner_ts
        gate_ts_et = _clean_value(candidate.get("scanner_trigger_ts_et"))
        if _same_timestamp_minute(candidate.get("scanner_trigger_ts_utc"), candidate.get("first_push_high_ts_utc")):
            gate_price = _clean_value(candidate.get("first_push_high"))
        elif _same_timestamp_minute(candidate.get("scanner_trigger_ts_utc"), candidate.get("momentum_trigger_ts_utc")):
            gate_price = _clean_value(candidate.get("momentum_trigger_price")) or _clean_value(candidate.get("price_at_trigger"))
        else:
            gate_price = _clean_value(candidate.get("price_at_trigger"))
        gate_volume = _clean_value(candidate.get("premarket_volume_at_trigger")) or _clean_value(candidate.get("session_volume_at_trigger"))
        gate_source = "scanner_volume_gate"
    else:
        gate_ts_utc = momentum_ts
        gate_ts_et = _clean_value(candidate.get("momentum_trigger_ts_et"))
        gate_price = _clean_value(candidate.get("momentum_trigger_price"))
        gate_volume = _clean_value(candidate.get("momentum_trigger_volume"))
        gate_source = "momentum_threshold_gate"

    prior_pct = None
    prior_close = _clean_value(candidate.get("prior_close"))
    if prior_close is not None and gate_price is not None:
        prior_pct = _pct_change(float(prior_close), float(gate_price))
    prior_close_source = "candidate_prior_close"
    if prior_close is None:
        prior_close_source = "unavailable"
    return {
        "visual_momentum_gate_ts_utc": gate_ts_utc,
        "visual_momentum_gate_ts_et": gate_ts_et,
        "visual_momentum_gate_price": gate_price,
        "visual_momentum_gate_volume": gate_volume,
        "visual_momentum_gate_prior_close_pct": prior_pct,
        "visual_momentum_gate_source": gate_source,
        "visual_momentum_gate_prior_close_value": prior_close,
        "visual_momentum_gate_prior_close_source": prior_close_source,
        "visual_momentum_gate_prior_close_formula": "(visual_momentum_gate_price - prior_close) / prior_close * 100",
    }



def _format_visual_label_time(value: object) -> str:
    clean = _clean_value(value)
    if clean is None:
        return "time na"
    text = str(clean)
    m = re.search(r"\b(\d{1,2}:\d{2})(?::\d{2})?\b", text)
    if m:
        suffix = " EDT" if "EDT" in text else " EST" if "EST" in text else " ET"
        return m.group(1) + suffix
    try:
        ts = pd.Timestamp(text)
        tz_name = str(ts.tzname() or "ET") if ts.tzinfo is not None else "ET"
        return f"{ts.strftime('%H:%M')} {tz_name}"
    except Exception:
        return "time na"


def _scanner_filter_marker_text(candidate: dict) -> str:
    prior_pct = _clean_value(candidate.get("visual_momentum_gate_prior_close_pct"))
    price = _clean_value(candidate.get("visual_momentum_gate_price"))
    volume = _clean_value(candidate.get("visual_momentum_gate_volume"))
    ts_et = _clean_value(candidate.get("visual_momentum_gate_ts_et")) or _clean_value(candidate.get("visual_momentum_gate_ts_utc"))
    market_cap = _clean_value(candidate.get("market_cap"))
    threshold_pct = _clean_value(candidate.get("momentum_trigger_pct_threshold"))
    title = f"momentum trigger {_format_visual_label_time(ts_et)}"
    lines = [
        title,
        (f"prior close {float(prior_pct):+.1f}%" if prior_pct is not None else "prior close na")
        + " | "
        + (f"price ${float(price):.4f}" if price is not None else "price na"),
        (f"acc vol {_format_compact_number(volume)}" if volume is not None else "acc vol na")
        + " | "
        + (f"threshold +{float(threshold_pct):.0f}%" if threshold_pct is not None else "threshold na"),
        (f"mcap {_format_compact_number(market_cap)} <100M" if market_cap is not None else "mcap na <100M")
        + " | price $0.50-$20",
    ]
    return "\n".join(lines)


def _visual_label_specs(candidate: dict) -> list[dict[str, object]]:
    scanner_text = _scanner_filter_marker_text(candidate)
    push_pct = _clean_value(candidate.get("pm_open_to_first_push_high_pct"))
    dip_pct = _clean_value(candidate.get("first_dip_depth_pct"))
    rebreak_volume = _clean_value(candidate.get("rebreak_volume"))
    dip_to_high_pct = _clean_value(candidate.get("dip_to_next_structural_high_pct"))
    dip_to_high_start = _clean_value(candidate.get("dip_to_next_structural_high_start_price"))
    dip_to_high_end = _clean_value(candidate.get("dip_to_next_structural_high_price"))
    return [
        {
            "signal_name": "scanner_seed",
            "source_field": "visual_momentum_gate_ts_utc;visual_momentum_gate_price;visual_momentum_gate_volume;visual_momentum_gate_prior_close_value;visual_momentum_gate_prior_close_source;visual_momentum_gate_prior_close_pct;market_cap;momentum_trigger_pct_threshold",
            "ts_field": "visual_momentum_gate_ts_utc",
            "price_field": "visual_momentum_gate_price",
            "label_text": scanner_text,
            "placement_rule": "above_prior_close_row",
            "label_order_index": 1,
        },
        {
            "signal_name": "first_push_high",
            "source_field": "first_push_high_ts_utc;first_push_high;pm_open_to_first_push_high_pct",
            "ts_field": "first_push_high_ts_utc",
            "price_field": "first_push_high",
            "label_text": "first push high\n" + (f"push = {float(push_pct):+.1f}%" if push_pct is not None else "push = na"),
            "placement_rule": "above_prior_close_row",
            "label_order_index": 2,
        },
        {
            "signal_name": "first_dip_low",
            "source_field": "first_dip_low_ts_utc;first_dip_low;first_dip_depth_pct",
            "ts_field": "first_dip_low_ts_utc",
            "price_field": "first_dip_low",
            "label_text": "first dip low\n" + (f"dip = {float(dip_pct):.1f}%" if dip_pct is not None else "dip = na"),
            "placement_rule": "above_prior_close_row",
            "label_order_index": 3,
        },
        {
            "signal_name": "rebreak_confirmed",
            "source_field": "first_rebreak_ts_utc;first_push_high;rebreak_volume",
            "ts_field": "first_rebreak_ts_utc",
            "price_field": "first_push_high",
            "label_text": "rebreak confirmed\n" + f"vol {_format_compact_number(rebreak_volume)}",
            "placement_rule": "above_prior_close_row",
            "label_order_index": 4,
        },
        {
            "signal_name": "first_dip_to_next_structural_high",
            "source_field": "first_dip_low_ts_utc;first_dip_low;dip_to_next_structural_high_ts_utc;dip_to_next_structural_high_price;dip_to_next_structural_high_pct",
            "ts_field": "dip_to_next_structural_high_ts_utc",
            "price_field": "dip_to_next_structural_high_price",
            "secondary_ts_field": "dip_to_next_structural_high_start_ts_utc",
            "secondary_price_field": "dip_to_next_structural_high_start_price",
            "label_text": (
                "dip -> next structural high\n"
                + (f"{float(dip_to_high_start):.4f} -> {float(dip_to_high_end):.4f}\n" if dip_to_high_start is not None and dip_to_high_end is not None else "price path na\n")
                + (f"move = {float(dip_to_high_pct):+.1f}%" if dip_to_high_pct is not None else "move = na")
            ),
            "placement_rule": "above_prior_close_row",
            "label_order_index": 5,
        },
    ]


def _visual_price_to_px(geometry: dict[str, float], price: object) -> float | None:
    clean_price = _clean_value(price)
    if clean_price is None:
        return None
    y_min = geometry["price_min"]
    y_max = geometry["price_max"]
    if y_max <= y_min:
        return None
    return geometry["price_bottom"] - ((float(clean_price) - y_min) / (y_max - y_min)) * (
        geometry["price_bottom"] - geometry["price_top"]
    )




def _visual_px_to_bar_x(geometry: dict[str, float], x_px: float) -> float:
    x_min = float(geometry.get("x_min", 0.0))
    x_max = float(geometry.get("x_max", max(geometry["bar_count"] - 1.0, 1.0)))
    ratio = (float(x_px) - geometry["plot_left"]) / max(geometry["plot_width"], 1.0)
    return x_min + max(0.0, min(1.0, ratio)) * (x_max - x_min)


def _visual_px_to_price(geometry: dict[str, float], y_px: float) -> float:
    y_min = geometry["price_min"]
    y_max = geometry["price_max"]
    price_height = max(geometry["price_bottom"] - geometry["price_top"], 1.0)
    ratio = (geometry["price_bottom"] - float(y_px)) / price_height
    return y_min + ratio * (y_max - y_min)

def _visual_dip_to_next_structural_high_fields(candidate: dict) -> dict[str, object]:
    dip_low = _clean_value(candidate.get("first_dip_low"))
    dip_ts = _clean_value(candidate.get("first_dip_low_ts_utc"))
    next_high = _clean_value(candidate.get("rebreak_high"))
    next_high_ts = _clean_value(candidate.get("first_rebreak_ts_utc"))
    if next_high is None:
        next_high = _clean_value(candidate.get("max_momentum_high")) or _clean_value(candidate.get("first_push_high"))
        next_high_ts = _clean_value(candidate.get("max_momentum_high_ts_utc")) or _clean_value(candidate.get("first_push_high_ts_utc"))
    pct = _pct_change(float(dip_low), float(next_high)) if dip_low is not None and next_high is not None else None
    return {
        "dip_to_next_structural_high_start_ts_utc": dip_ts,
        "dip_to_next_structural_high_start_price": dip_low,
        "dip_to_next_structural_high_ts_utc": next_high_ts,
        "dip_to_next_structural_high_price": next_high,
        "dip_to_next_structural_high_pct": pct,
    }


def _visual_label_fixed_bboxes(
    prepared_rows: list[dict[str, object]],
    geometry: dict[str, float],
    allowed_bounds: tuple[float, float, float, float],
    blocked: list[tuple[float, float, float, float]],
    prior_close_y_px: float,
) -> list[tuple[float, float, float, float]]:
    min_x, min_y, max_x, max_y = allowed_bounds
    gap = 12.0
    out: list[tuple[float, float, float, float] | None] = [None] * len(prepared_rows)

    prior_items = [
        (idx, row)
        for idx, row in enumerate(prepared_rows)
        if row.get("placement_rule") == "above_prior_close_row"
    ]
    prior_items.sort(key=lambda item: int(item[1].get("label_order_index") or 999))
    sizes = [_estimate_label_size(str(row.get("label_text", ""))) for _, row in prior_items]
    total_width = sum(width for width, _ in sizes) + gap * max(0, len(sizes) - 1)
    available_width = max_x - min_x
    while total_width > available_width and gap > 4.0:
        gap -= 2.0
        total_width = sum(width for width, _ in sizes) + gap * max(0, len(sizes) - 1)
    if total_width > available_width:
        raise RuntimeError(f"visual_label_row_too_wide: total={total_width:.1f} available={available_width:.1f}")
    row_height = max((height for _, height in sizes), default=0.0)
    start_x = min_x + max(0.0, (available_width - total_width) / 2.0)
    # Visual contract: every label box sits just above the prior-close dotted line.
    row_bottom = prior_close_y_px - 8.0
    if row_bottom - row_height < min_y:
        row_bottom = min_y + row_height
    if row_bottom > max_y:
        row_bottom = max_y

    x = start_x
    for (idx, _), (width, height) in zip(prior_items, sizes):
        y0 = row_bottom - height
        bbox = (x, y0, x + width, row_bottom)
        out[idx] = bbox
        x += width + gap

    for idx, row in enumerate(prepared_rows):
        if out[idx] is not None:
            continue
        width, height = _estimate_label_size(str(row.get("label_text", "")))
        anchor_x = float(row["anchor_x_px"])
        anchor_y = float(row["anchor_y_px"])
        x0 = min(max(anchor_x - width / 2.0, min_x), max_x - width)
        y0c = min(max(anchor_y + 70.0, min_y), max_y - height)
        out[idx] = (x0, y0c, x0 + width, y0c + height)

    if any(item is None for item in out):
        missing = [str(prepared_rows[idx].get("signal_name")) for idx, item in enumerate(out) if item is None]
        raise RuntimeError("visual_label_bbox_missing: " + ",".join(missing))
    return [item for item in out if item is not None]


def _build_visual_inspection_rows(
    candidate: dict,
    chart_df: pd.DataFrame,
    image_path: Path,
    visual_case_id: str,
    image_kind: str,
    axis_ranges: dict[str, tuple[float, float]] | None = None,
) -> list[dict[str, object]]:
    if chart_df.empty:
        return []
    candidate = dict(candidate)
    candidate.update(_visual_momentum_gate_fields(candidate))
    candidate.update(_visual_dip_to_next_structural_high_fields(candidate))
    working = chart_df.copy().reset_index(drop=True)
    working["bar_index"] = working.index
    geometry = _image_pixel_geometry(working, y_padding_override_pct=0.03, axis_ranges=axis_ranges)
    blocked = _visual_candle_bboxes(working, geometry)
    allowed_bounds = _visual_premarket_label_bounds(working, geometry)
    prior_close_value = _clean_value(candidate.get("prior_close"))
    prior_close_y_px = _visual_price_to_px(geometry, prior_close_value)
    if prior_close_y_px is None:
        prior_close_y_px = geometry["price_bottom"] - 18.0

    renderer_path = str(Path(__file__).resolve())
    renderer_hash = _renderer_source_hash()
    source_row_id = candidate.get("candidate_id") or f"{candidate.get('ticker')}:{candidate.get('session_date')}"

    prepared: list[dict[str, object]] = []
    for idx, spec in enumerate(_visual_label_specs(candidate), start=1):
        ts_value = candidate.get(str(spec["ts_field"]))
        price_value = candidate.get(str(spec["price_field"]))
        anchor = _visual_anchor_px(working, geometry, ts_value, price_value)
        if anchor is None:
            continue
        secondary_anchor = None
        secondary_ts_field = spec.get("secondary_ts_field")
        secondary_price_field = spec.get("secondary_price_field")
        if secondary_ts_field and secondary_price_field:
            secondary_anchor = _visual_anchor_px(
                working,
                geometry,
                candidate.get(str(secondary_ts_field)),
                candidate.get(str(secondary_price_field)),
            )
        label_text = str(spec["label_text"])
        signal_name = str(spec["signal_name"])
        prepared.append(
            {
                "spec_index": idx,
                "visual_case_id": visual_case_id,
                "candidate_id": candidate.get("candidate_id"),
                "ticker": candidate.get("ticker"),
                "session_date": candidate.get("session_date"),
                "image_path": str(image_path),
                "image_kind": image_kind,
                "label_id": f"{visual_case_id}:{idx:02d}:{signal_name}",
                "signal_name": signal_name,
                "source_field": spec["source_field"],
                "label_text": label_text,
                "anchor_x_data": _bar_x_for_ts(working, str(ts_value) if _clean_value(ts_value) is not None else None),
                "anchor_y_data": float(_clean_value(price_value)) if _clean_value(price_value) is not None else None,
                "anchor_x_px": round(anchor[0], 3),
                "anchor_y_px": round(anchor[1], 3),
                "secondary_anchor_x_data": _bar_x_for_ts(
                    working,
                    str(candidate.get(str(secondary_ts_field))) if secondary_ts_field and _clean_value(candidate.get(str(secondary_ts_field))) is not None else None,
                ) if secondary_ts_field else None,
                "secondary_anchor_y_data": float(_clean_value(candidate.get(str(secondary_price_field)))) if secondary_price_field and _clean_value(candidate.get(str(secondary_price_field))) is not None else None,
                "secondary_anchor_x_px": round(secondary_anchor[0], 3) if secondary_anchor else None,
                "secondary_anchor_y_px": round(secondary_anchor[1], 3) if secondary_anchor else None,
                "renderer_source_path": renderer_path,
                "renderer_source_hash": renderer_hash,
                "visual_evidence_status": "ok",
                "formula_version": "das_visual_labels_v0_6_plotly_axis_calibrated_overlay",
                "detector_version": "das_widgets_v0_2",
                "source_row_id": source_row_id,
                "threshold_pct": _clean_value(candidate.get("momentum_trigger_pct_threshold")),
                "prior_close_value": _clean_value(candidate.get("visual_momentum_gate_prior_close_value")) if signal_name == "scanner_seed" else None,
                "prior_close_source": _clean_value(candidate.get("visual_momentum_gate_prior_close_source")) if signal_name == "scanner_seed" else None,
                "prior_close_pct_formula": _clean_value(candidate.get("visual_momentum_gate_prior_close_formula")) if signal_name == "scanner_seed" else None,
                "visual_gate_source": _clean_value(candidate.get("visual_momentum_gate_source")) if signal_name == "scanner_seed" else None,
                "placement_rule": spec.get("placement_rule"),
                "label_order_index": spec.get("label_order_index"),
                "prior_close_y_px": round(float(prior_close_y_px), 3),
                "measurement_pct": _clean_value(candidate.get("dip_to_next_structural_high_pct")) if signal_name == "first_dip_to_next_structural_high" else None,
            }
        )

    bboxes = _visual_label_fixed_bboxes(prepared, geometry, allowed_bounds, blocked, float(prior_close_y_px))
    rows: list[dict[str, object]] = []
    for row, bbox in zip(prepared, bboxes):
        label_x_px = (bbox[0] + bbox[2]) / 2.0
        label_y_px = bbox[3]
        row.update(
            {
                "bbox_x0_px": round(bbox[0], 3),
                "bbox_y0_px": round(bbox[1], 3),
                "bbox_x1_px": round(bbox[2], 3),
                "bbox_y1_px": round(bbox[3], 3),
                "label_x_data": round(_visual_px_to_bar_x(geometry, label_x_px), 3),
                "label_y_data": round(_visual_px_to_price(geometry, label_y_px), 6),
            }
        )
        rows.append(row)
    return rows

def _legacy_visual_text(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple)):
        return any(_legacy_visual_text(item) for item in value)
    lowered = str(value).lower()
    return (
        "<br>" in lowered
        and (
            "threshold" in lowered
            or "momentum trigger" in lowered
            or "scanner trigger" in lowered
            or "prior close" in lowered
            or "pm open" in lowered
            or "accu" in lowered
            or "acc vol" in lowered
        )
    ) or "threshold +" in lowered or "threshold+" in lowered or "accu" in lowered


def _strip_builtin_visual_label_text(fig: go.Figure) -> None:
    # Visual inspection owns all evidence labels. Remove inherited chart annotations
    # so legacy HTML/text overlays cannot leak into the PNG.
    fig.layout.annotations = tuple()

    removed_names = {
        "scanner trigger",
        "momentum trigger",
        "DAS rebreak",
        "DAS rebreak trigger",
        "first push high",
        "first dip low",
        "PM open to first push",
        "PM open to PM extension high",
        "first push high to rebreak",
        "rebreak cross",
    }
    kept_traces = []
    for trace in fig.data:
        name = str(getattr(trace, "name", ""))
        mode = str(getattr(trace, "mode", ""))
        if name in removed_names:
            continue
        if _legacy_visual_text(getattr(trace, "text", None)) or _legacy_visual_text(getattr(trace, "hovertemplate", None)):
            continue
        if "text" in mode and name not in {"1m candles", "1m volume"}:
            continue
        kept_traces.append(trace)
    fig.data = tuple(kept_traces)


def _assert_no_legacy_visual_text(fig: go.Figure) -> None:
    offenders: list[str] = []
    for ann in fig.layout.annotations:
        text = str(getattr(ann, "text", ""))
        if _legacy_visual_text(text):
            offenders.append(f"annotation:{text[:80]}")
    for trace in fig.data:
        name = str(getattr(trace, "name", ""))
        mode = str(getattr(trace, "mode", ""))
        if "text" in mode and (_legacy_visual_text(getattr(trace, "text", None)) or _legacy_visual_text(getattr(trace, "hovertemplate", None))):
            offenders.append(f"trace:{name}")
    if offenders:
        raise RuntimeError("legacy_visual_text_remaining_before_manifest: " + "; ".join(offenders[:5]))

def _visual_overlay_styles() -> dict[str, dict[str, object]]:
    return {
        "scanner_seed": {"rgb": (17, 24, 39), "fill": (255, 255, 255, 235), "marker": "circle"},
        "first_push_high": {"rgb": (22, 163, 74), "fill": (240, 253, 244, 235), "marker": "circle"},
        "first_dip_low": {"rgb": (220, 38, 38), "fill": (254, 242, 242, 235), "marker": "circle"},
        "rebreak_confirmed": {"rgb": (37, 99, 235), "fill": (239, 246, 255, 235), "marker": "x"},
        "first_dip_to_next_structural_high": {"rgb": (126, 34, 206), "fill": (250, 245, 255, 235), "marker": "diamond"},
    }


def _visual_font(bold: bool = False, size: int = 18) -> ImageFont.ImageFont:
    font_name = "arialbd.ttf" if bold else "arial.ttf"
    candidates = [
        Path(r"C:\Windows\Fonts") / font_name,
        Path(r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _draw_dotted_line(draw: ImageDraw.ImageDraw, xy: tuple[float, float, float, float], color: tuple[int, int, int], width: int = 2, dash: int = 9, gap: int = 7) -> None:
    x0, y0, x1, y1 = xy
    if abs(y1 - y0) <= 1e-6:
        if x1 < x0:
            x0, x1 = x1, x0
        x = x0
        while x < x1:
            draw.line((x, y0, min(x + dash, x1), y0), fill=color, width=width)
            x += dash + gap
        return
    draw.line(xy, fill=color, width=width)


def _draw_visual_marker(draw: ImageDraw.ImageDraw, x: float, y: float, color: tuple[int, int, int], marker: str) -> None:
    if marker == "x":
        r = 15
        draw.line((x - r, y - r, x + r, y + r), fill=color, width=5)
        draw.line((x - r, y + r, x + r, y - r), fill=color, width=5)
    elif marker == "diamond":
        r = 13
        draw.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=color, outline=color)
    else:
        r = 12
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color, outline=(255, 255, 255), width=2)


def _draw_visual_box(draw: ImageDraw.ImageDraw, row: dict[str, object], style: dict[str, object]) -> None:
    x0 = int(round(float(row["bbox_x0_px"])))
    y0 = int(round(float(row["bbox_y0_px"])))
    x1 = int(round(float(row["bbox_x1_px"])))
    y1 = int(round(float(row["bbox_y1_px"])))
    color = tuple(style["rgb"])
    fill = tuple(style["fill"])
    draw.rectangle((x0, y0, x1, y1), fill=fill, outline=color, width=2)
    lines = str(row.get("label_text", "")).splitlines() or [""]
    font_regular = _visual_font(False, 17)
    font_bold = _visual_font(True, 17)
    tx = x0 + 8
    ty = y0 + 7
    for idx, line in enumerate(lines):
        font = font_bold if idx == 0 else font_regular
        draw.text((tx, ty), line, font=font, fill=color)
        ty += 20


def _draw_visual_manifest_overlay(image_path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    styles = _visual_overlay_styles()
    with Image.open(image_path).convert("RGBA") as base:
        overlay_img = Image.new("RGBA", base.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay_img)
        by_signal = {str(row.get("signal_name")): row for row in rows}
        first_push = by_signal.get("first_push_high")
        rebreak = by_signal.get("rebreak_confirmed")
        if first_push and rebreak:
            y = float(first_push["anchor_y_px"])
            x_push = float(first_push["anchor_x_px"])
            x_rebreak = float(rebreak["anchor_x_px"])
            _draw_dotted_line(draw, (70.0, y, x_push, y), tuple(styles["first_push_high"]["rgb"]), width=2, dash=10, gap=8)
            _draw_dotted_line(draw, (x_push, y, x_rebreak, y), tuple(styles["rebreak_confirmed"]["rgb"]), width=2, dash=10, gap=8)
        for row in rows:
            signal = str(row.get("signal_name"))
            style = styles.get(signal, styles["scanner_seed"])
            _draw_visual_marker(
                draw,
                float(row["anchor_x_px"]),
                float(row["anchor_y_px"]),
                tuple(style["rgb"]),
                str(style.get("marker", "circle")),
            )
        for row in rows:
            signal = str(row.get("signal_name"))
            style = styles.get(signal, styles["scanner_seed"])
            _draw_visual_box(draw, row, style)
        out = Image.alpha_composite(base, overlay_img).convert("RGB")
        out.save(image_path)


def _write_visual_label_sidecar(labels_path: Path, rows: list[dict[str, object]]) -> None:
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    labels_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")




def _visual_axis_ranges_from_plotly(fig: go.Figure) -> dict[str, tuple[float, float]]:
    full = fig.full_figure_for_development(warn=False)
    out: dict[str, tuple[float, float]] = {}
    if full.layout.xaxis.range is not None:
        out["xaxis"] = (float(full.layout.xaxis.range[0]), float(full.layout.xaxis.range[1]))
    if full.layout.yaxis.range is not None:
        out["yaxis"] = (float(full.layout.yaxis.range[0]), float(full.layout.yaxis.range[1]))
    return out

def _export_visual_inspection_image(
    row: dict,
    position: int,
    run_dir: Path,
    premarket_df: pd.DataFrame,
    premarket_candidate: dict,
    split_events: pd.DataFrame | None,
    y_padding_pct: float,
) -> tuple[Path | None, list[dict[str, object]]]:
    if premarket_df.empty:
        return None, []
    threshold_label = _visual_threshold_label(row)
    visual_case_id = _safe_filename(
        f"{position:04d}_{row.get('ticker')}_{row.get('session_date')}_threshold{threshold_label}_visual"
    )
    visual_root = run_dir / "visual_inspection" / f"threshold={threshold_label}"
    images_root = visual_root / "images"
    labels_root = visual_root / "labels"
    images_root.mkdir(parents=True, exist_ok=True)
    image_path = images_root / f"{visual_case_id}_03_event_day_premarket_detail.png"
    fig = make_das_chart(
        premarket_df,
        premarket_candidate,
        y_padding_pct=y_padding_pct,
        chart_label="visual inspection | event-day 03:30-10:00 NY detail",
        show_rangeslider=False,
        height=EXPORT_SQUARE_CHART_HEIGHT,
        static_axes=True,
        y_padding_override_pct=0.03,
        split_events=split_events,
        show_diagnostic_markers=False,
        show_legend=True,
    )
    _strip_builtin_visual_label_text(fig)
    _assert_no_legacy_visual_text(fig)
    axis_ranges = _visual_axis_ranges_from_plotly(fig)
    rows = _build_visual_inspection_rows(row, premarket_df, image_path, visual_case_id, "event_day_premarket_detail", axis_ranges=axis_ranges)
    fig.write_image(str(image_path), width=EXPORT_SQUARE_CHART_WIDTH, height=EXPORT_SQUARE_CHART_HEIGHT, scale=2)
    _draw_visual_manifest_overlay(image_path, rows)
    _write_visual_label_sidecar(labels_root / f"{visual_case_id}_labels.json", rows)
    return image_path, rows

def _candidate_detail_image_name(position: int, candidate: dict) -> str:
    push = pd.to_numeric(pd.Series([_visible_maxpush_pct(candidate)]), errors="coerce").iloc[0]
    push_label = f"{push:.2f}" if pd.notna(push) else "na"
    state = str(candidate.get("das_state") or "state")
    state_label = {
        "rebreak_confirmed": "rebreak",
        "failed_before_rebreak": "failed",
        "no_rebreak_yet": "pending",
    }.get(state, state[:12])
    raw_name = f"{position:04d}_{candidate.get('ticker')}_{candidate.get('session_date')}_push{push_label}_{state_label}"
    return f"{_safe_filename(raw_name)}.png"


def export_run_event_day_detail_images(
    candidates: pd.DataFrame,
    run_dir: Path,
    data_root: str,
    price_view: str,
    vwap_source: str,
    y_padding_pct: float,
    sort_mode: str = "max_push_pct_desc",
    limit: int | None = None,
    progress_callback: Callable[[int, int, Path, dict], None] | None = None,
) -> tuple[Path, list[Path]]:
    if candidates.empty:
        return run_dir / "chart_exports", []
    _ensure_plotly_png_export_available()
    candidates = _sort_candidates_for_review(candidates, mode=sort_mode)
    if limit is not None:
        candidates = candidates.head(limit).copy()

    export_root = run_dir / "chart_exports"
    grouped_root = export_root / "event_day_details_grouped"
    export_variants = [
        ("three_day_overview", "02_three_day_overview.png", "3-day overview", 0.03),
        ("event_day_premarket_detail", "03_event_day_premarket_detail.png", "event-day 03:30-10:00 NY detail", 0.03),
        ("event_day_detail_until_1600_ny", "04_event_day_detail_until_1600_ny.png", "detail until 16:00 NY", 0.03),
    ]
    grouped_root.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    manifest_rows: list[dict] = []
    visual_manifest_rows: list[dict] = []
    error_rows: list[dict] = []
    rows = candidates.to_dict("records")
    total = len(rows)
    for position, row in enumerate(rows, start=1):
        try:
            image_name = _candidate_detail_image_name(position, row)
            candidate_export_dir = grouped_root / Path(image_name).stem
            candidate_export_dir.mkdir(parents=True, exist_ok=True)
            df = _load_chart_window(
                row["ticker"],
                _candidate_event_ts_utc(row),
                data_root,
                price_view=price_view,
                vwap_source=vwap_source,
            )
            row = _enrich_candidate_from_chart_window(row, df)
            detail_df = _detail_window_until_regular_close(df, row)
            premarket_df = _premarket_window_for_event_day(df, row)
            premarket_candidate = _candidate_for_premarket_chart(row, premarket_df)
            split_events = load_split_events_for_chart(
                row["ticker"],
                str(df["session_date"].min()) if not df.empty else str(row.get("session_date", "")),
                str(df["session_date"].max()) if not df.empty else str(row.get("session_date", "")),
                splits_root=DEFAULT_REFERENCE_SPLITS_ROOT,
            )
            variant_frames = {
                "three_day_overview": (df, row),
                "event_day_premarket_detail": (premarket_df, premarket_candidate),
                "event_day_detail_until_1600_ny": (detail_df, row),
            }
            row_paths: dict[str, str] = {"candidate_export_dir": str(candidate_export_dir)}
            for dirname, filename, chart_label, y_padding_override_pct in export_variants:
                path = candidate_export_dir / filename
                frame, chart_candidate = variant_frames[dirname]
                fig = make_das_chart(
                    frame,
                    chart_candidate,
                    y_padding_pct=y_padding_pct,
                    chart_label=chart_label,
                    show_rangeslider=False,
                    height=EXPORT_SQUARE_CHART_HEIGHT,
                    static_axes=True,
                    y_padding_override_pct=y_padding_override_pct,
                    split_events=split_events,
                    show_diagnostic_markers=False,
                    show_legend=True,
                )
                fig.write_image(str(path), width=EXPORT_SQUARE_CHART_WIDTH, height=EXPORT_SQUARE_CHART_HEIGHT, scale=2)
                paths.append(path)
                row_paths[f"{dirname}_image_path"] = str(path)
            visual_image_path, visual_rows = _export_visual_inspection_image(
                row,
                position,
                run_dir,
                premarket_df,
                premarket_candidate,
                split_events,
                y_padding_pct,
            )
            if visual_image_path is not None:
                paths.append(visual_image_path)
                row_paths["visual_inspection_image_path"] = str(visual_image_path)
            visual_manifest_rows.extend(visual_rows)
            daily_path = candidate_export_dir / "05_daily_context.png"
            daily_fig = make_das_daily_context_chart(row, height=EXPORT_SQUARE_CHART_HEIGHT)
            daily_fig.write_image(
                str(daily_path),
                width=EXPORT_SQUARE_CHART_WIDTH,
                height=EXPORT_SQUARE_CHART_HEIGHT,
                scale=2,
            )
            paths.append(daily_path)
            row_paths["daily_context_image_path"] = str(daily_path)
            if progress_callback:
                progress_callback(position, total, candidate_export_dir, row)
        except Exception as exc:
            error_rows.append(
                {
                    "position": position,
                    "candidate_id": row.get("candidate_id"),
                    "ticker": row.get("ticker"),
                    "session_date": row.get("session_date"),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue
        manifest_rows.append(
            {
                "position": position,
                **row_paths,
                "candidate_id": row.get("candidate_id"),
                "ticker": row.get("ticker"),
                "session_date": row.get("session_date"),
                "visible_maxpush_pct": _visible_maxpush_pct(row),
                "pm_open_to_first_push_high_pct": row.get("pm_open_to_first_push_high_pct"),
                "pm_open_to_momentum_trigger_pct": row.get("pm_open_to_momentum_trigger_pct"),
                "prior_close_to_momentum_trigger_pct": row.get("prior_close_to_momentum_trigger_pct"),
                "pm_open_to_scanner_pct": row.get("pm_open_to_scanner_pct"),
                "prior_close_to_scanner_pct": row.get("prior_close_to_scanner_pct"),
                "pm_open_to_premarket_extension_high_pct": row.get("pm_open_to_premarket_extension_high_pct"),
                "prior_close_to_premarket_extension_high_pct": row.get("prior_close_to_premarket_extension_high_pct"),
                "pm_open_to_max_high_after_trigger_pct": row.get("pm_open_to_max_high_after_trigger_pct"),
                "scanner_to_max_high_pct": row.get("scanner_to_max_high_pct"),
                "max_push_pct_after_trigger": row.get("max_push_pct_after_trigger"),
                "das_state": row.get("das_state"),
                "first_dip_depth_pct": row.get("first_dip_depth_pct"),
                "first_rebreak_type": row.get("first_rebreak_type"),
                "first_rebreak_ts_et": row.get("first_rebreak_ts_et"),
                "first_green_wick_dip_ts_et": row.get("first_green_wick_dip_ts_et"),
                "first_green_wick_dip_depth_pct": row.get("first_green_wick_dip_depth_pct"),
                "first_green_wick_dip_type": row.get("first_green_wick_dip_type"),
            }
        )
    pd.DataFrame(manifest_rows).to_csv(export_root / "EXPORT_MANIFEST.csv", index=False)
    visual_manifest = pd.DataFrame(visual_manifest_rows)
    if not visual_manifest.empty:
        visual_manifest.to_parquet(run_dir / "visual_inspection_manifest.parquet", index=False)
        visual_manifest.to_csv(run_dir / "visual_inspection_manifest.csv", index=False)
    if error_rows:
        pd.DataFrame(error_rows).to_csv(export_root / "EXPORT_ERRORS.csv", index=False)
    else:
        errors_path = export_root / "EXPORT_ERRORS.csv"
        if errors_path.exists():
            errors_path.unlink()
    return export_root, paths


def export_run_premarket_detail_images(
    candidates: pd.DataFrame,
    run_dir: Path,
    data_root: str,
    price_view: str,
    vwap_source: str,
    y_padding_pct: float,
    sort_mode: str = "max_push_pct_desc",
    limit: int | None = None,
    progress_callback: Callable[[int, int, Path, dict], None] | None = None,
) -> tuple[Path, list[Path]]:
    if candidates.empty:
        return run_dir / "chart_exports" / "event_day_premarket_detail_only", []
    _ensure_plotly_png_export_available()
    candidates = _sort_candidates_for_review(candidates, mode=sort_mode)
    if limit is not None:
        candidates = candidates.head(limit).copy()

    export_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    export_root = run_dir / "chart_exports" / "event_day_premarket_detail_only" / export_id
    images_root = export_root / "images"
    images_root.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    manifest_rows: list[dict] = []
    error_rows: list[dict] = []
    rows = candidates.to_dict("records")
    total = len(rows)
    for position, row in enumerate(rows, start=1):
        try:
            image_name = _candidate_detail_image_name(position, row).replace(
                ".png",
                "_03_event_day_premarket_detail.png",
            )
            path = images_root / image_name
            df = _load_chart_window(
                row["ticker"],
                _candidate_event_ts_utc(row),
                data_root,
                price_view=price_view,
                vwap_source=vwap_source,
            )
            row = _enrich_candidate_from_chart_window(row, df)
            premarket_df = _premarket_window_for_event_day(df, row)
            premarket_candidate = _candidate_for_premarket_chart(row, premarket_df)
            split_events = load_split_events_for_chart(
                row["ticker"],
                str(df["session_date"].min()) if not df.empty else str(row.get("session_date", "")),
                str(df["session_date"].max()) if not df.empty else str(row.get("session_date", "")),
                splits_root=DEFAULT_REFERENCE_SPLITS_ROOT,
            )
            fig = make_das_chart(
                premarket_df,
                premarket_candidate,
                y_padding_pct=y_padding_pct,
                chart_label="event-day 03:30-10:00 NY detail",
                show_rangeslider=False,
                height=EXPORT_SQUARE_CHART_HEIGHT,
                static_axes=True,
                y_padding_override_pct=0.03,
                split_events=split_events,
                show_diagnostic_markers=False,
                show_legend=True,
            )
            fig.write_image(str(path), width=EXPORT_SQUARE_CHART_WIDTH, height=EXPORT_SQUARE_CHART_HEIGHT, scale=2)
            paths.append(path)
            if progress_callback:
                progress_callback(position, total, path, row)
        except Exception as exc:
            error_rows.append(
                {
                    "position": position,
                    "candidate_id": row.get("candidate_id"),
                    "ticker": row.get("ticker"),
                    "session_date": row.get("session_date"),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue
        manifest_rows.append(
            {
                "position": position,
                "image_path": str(path),
                "candidate_id": row.get("candidate_id"),
                "ticker": row.get("ticker"),
                "session_date": row.get("session_date"),
                "visible_maxpush_pct": _visible_maxpush_pct(row),
                "pm_open_to_momentum_trigger_pct": row.get("pm_open_to_momentum_trigger_pct"),
                "pm_open_to_scanner_pct": row.get("pm_open_to_scanner_pct"),
                "pm_open_to_premarket_extension_high_pct": row.get("pm_open_to_premarket_extension_high_pct"),
                "das_state": row.get("das_state"),
                "first_dip_depth_pct": row.get("first_dip_depth_pct"),
                "first_rebreak_type": row.get("first_rebreak_type"),
                "first_rebreak_ts_et": row.get("first_rebreak_ts_et"),
            }
        )
    pd.DataFrame(manifest_rows).to_csv(export_root / "EXPORT_MANIFEST.csv", index=False)
    if error_rows:
        pd.DataFrame(error_rows).to_csv(export_root / "EXPORT_ERRORS.csv", index=False)
    return export_root, paths


def _format_run_option(run_dir: Path) -> tuple[str, str]:
    manifest = _read_manifest(run_dir)
    modified = datetime.fromtimestamp(run_dir.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    parts = [
        f"run_utc={manifest.get('run_datetime_utc') or _run_datetime_utc_label(run_dir.name)}",
        f"modified={modified}",
        f"{manifest.get('run_status', 'unknown')}",
    ]
    if manifest.get("candidate_count") is not None:
        parts.append(f"candidates={manifest.get('candidate_count')}")
    if manifest.get("raw_candidate_count") is not None:
        parts.append(f"raw={manifest.get('raw_candidate_count')}")
    parts.append(run_dir.name)
    return " | ".join(parts), str(run_dir)


def _list_run_options() -> list[tuple[str, str]]:
    if not DEFAULT_RUNS_ROOT.exists():
        return []
    runs = [p for p in DEFAULT_RUNS_ROOT.iterdir() if p.is_dir()]
    runs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [_format_run_option(path) for path in runs]


def launch_das_app():
    import ipywidgets as widgets
    from IPython.display import HTML, clear_output, display

    data_root = widgets.Text(value=str(DEFAULT_DATA_ROOT), description="1m root", layout=widgets.Layout(width="95%"))
    reference_root = widgets.Text(value=str(DEFAULT_REFERENCE_OVERVIEW_ROOT), description="Reference", layout=widgets.Layout(width="95%"))
    universe_path = widgets.Text(value=str(DEFAULT_LT1B_UNIVERSE_PATH), description="Universe", layout=widgets.Layout(width="95%"))
    tickers = widgets.Text(value="", description="Tickers", placeholder="empty = LT1B universe")
    years = widgets.Text(value="", description="Years", placeholder="e.g. 2025 or 2022-2025")
    session_scope = widgets.Dropdown(options=["premarket", "regular", "premarket_regular"], value="premarket", description="Session")
    momentum_trigger_pct = widgets.FloatText(value=50.0, description="Momentum %")
    min_session_volume = widgets.FloatText(value=500_000.0, description="Session Vol >")
    min_price = widgets.FloatText(value=0.5, description="Price >=")
    max_price = widgets.FloatText(value=20.0, description="Price <=")
    max_market_cap = widgets.FloatText(value=100_000_000.0, description="MCap <")
    missing_cap = widgets.Dropdown(options=["include", "exclude", "flag"], value="include", description="No MCap")
    price_view = widgets.Dropdown(options=["raw", "split_normalized"], value="raw", description="Price")
    vwap_source = widgets.Dropdown(
        options=[("Calculated", "calculated"), ("Raw vw", "raw")],
        value="calculated",
        description="VWAP",
    )
    y_padding = widgets.BoundedFloatText(value=0.40, min=0.05, max=1.00, step=0.05, description="Y padding")
    progress_every = widgets.IntText(value=250, description="Progress")
    partial_flush = widgets.IntText(value=1, description="Flush hits")
    command_preview = widgets.Textarea(value="", description="Terminal", layout=widgets.Layout(width="95%", height="360px"))
    command_preview_one_line = widgets.Textarea(value="", description="1 line", layout=widgets.Layout(width="95%", height="90px"))
    run_dropdown = widgets.Dropdown(options=[], description="Runs", layout=widgets.Layout(width="95%"))
    run_dir_text = widgets.Text(value="", description="Run dir", layout=widgets.Layout(width="95%"))
    candidate_dropdown = widgets.Dropdown(options=[], description="Candidate", layout=widgets.Layout(width="95%"))
    tradingview_symbol_text = widgets.Text(value="", description="TV symbol", layout=widgets.Layout(width="42%"))
    event_time_text = widgets.Text(value="", description="Event ET", layout=widgets.Layout(width="42%"))
    company_name_text = widgets.Text(value="", description="Company", layout=widgets.Layout(width="76%"))
    tradingview_copy_text = widgets.Textarea(value="", description="Copy TV", layout=widgets.Layout(width="95%", height="58px"))
    tradingview_interval = widgets.Text(value="1", description="TV int", layout=widgets.Layout(width="18%"))
    refresh_runs_button = widgets.Button(description="Refresh runs")
    load_selected_button = widgets.Button(description="Load selected", button_style="primary")
    load_latest_button = widgets.Button(description="Load latest")
    load_run_button = widgets.Button(description="Load run")
    refresh_partial_button = widgets.Button(description="Refresh partial")
    render_button = widgets.Button(description="Render selected")
    export_detail_run_button = widgets.Button(description="Export detail run")
    export_premarket_detail_button = widgets.Button(description="Export PM detail")
    tradingview_button = widgets.Button(description="TradingView selected")
    run_button = widgets.Button(description="Run in notebook")
    candidate_sort = widgets.Dropdown(
        options=[
            ("Max push % desc", "max_push_pct_desc"),
            ("Fastest rebreak", "rebreak_fastest"),
            ("Group same ticker", "ticker_grouped"),
        ],
        value="max_push_pct_desc",
        description="Sort",
    )
    out = widgets.Output()
    state: dict[str, object] = {}
    reference_cache: dict[str, pd.DataFrame] = {}

    def _config() -> DasConfig:
        return DasConfig(
            data_root=data_root.value,
            reference_overview_root=reference_root.value,
            universe_path=universe_path.value,
            tickers=_parse_csv(tickers.value),
            years=_parse_years(years.value),
            session_scope=session_scope.value,
            momentum_trigger_pct=float(momentum_trigger_pct.value),
            min_session_volume=float(min_session_volume.value),
            min_price=float(min_price.value),
            max_price=float(max_price.value),
            max_market_cap=float(max_market_cap.value),
            missing_market_cap_policy=missing_cap.value,
            price_view=price_view.value,
            vwap_source=vwap_source.value,
            progress_every=int(progress_every.value),
            partial_flush_every=int(partial_flush.value),
        )

    def _refresh_command(_change=None) -> None:
        cfg = _config()
        command_preview.value = _terminal_command_from_config(cfg, pretty=True)
        command_preview_one_line.value = _terminal_command_from_config(cfg, pretty=False)

    def _enrich_widget_reference(candidates: pd.DataFrame) -> pd.DataFrame:
        if candidates.empty or "ticker" not in candidates.columns:
            return candidates
        out_df = candidates.copy()
        for col in ["primary_exchange", "name", "tradingview_symbol", "market_cap", "market_cap_asof"]:
            if col not in out_df.columns:
                out_df[col] = pd.NA
        unique_tickers = sorted(out_df["ticker"].astype(str).str.upper().dropna().unique())
        if len(unique_tickers) > 50:
            missing_tv = (
                out_df["tradingview_symbol"].astype("string").isna()
                | ~out_df["tradingview_symbol"].astype("string").str.contains(":", regex=False, na=False)
            )
            if "primary_exchange" in out_df.columns:
                for idx in out_df.index[missing_tv]:
                    out_df.at[idx, "tradingview_symbol"] = _tradingview_symbol(
                        str(out_df.at[idx, "ticker"]),
                        out_df.at[idx, "primary_exchange"],
                    )
            return out_df
        overview_root = Path(reference_root.value)
        for ticker in unique_tickers:
            if ticker not in reference_cache:
                reference_cache[ticker] = _load_market_cap_history(overview_root, ticker)
            hist = reference_cache[ticker]
            ref = _reference_asof(hist)
            mask = out_df["ticker"].astype(str).str.upper().eq(ticker)
            if ref.get("primary_exchange") is not None:
                out_df.loc[mask, "primary_exchange"] = ref.get("primary_exchange")
            if ref.get("name") is not None:
                out_df.loc[mask, "name"] = ref.get("name")
            tv_symbol = _tradingview_symbol(ticker, ref.get("primary_exchange"))
            existing_tv = out_df.loc[mask, "tradingview_symbol"].astype("string")
            needs_tv = existing_tv.isna() | ~existing_tv.str.contains(":", regex=False, na=False)
            out_df.loc[mask[mask].index[needs_tv.to_numpy()], "tradingview_symbol"] = tv_symbol
            if "session_date" in out_df.columns:
                for idx, event_date in out_df.loc[mask, "session_date"].items():
                    if pd.isna(out_df.at[idx, "market_cap"]):
                        cap, cap_date = _market_cap_asof(hist, str(event_date))
                        out_df.at[idx, "market_cap"] = cap
                        out_df.at[idx, "market_cap_asof"] = cap_date
        return out_df

    def _set_candidates(candidates: pd.DataFrame, run_dir: Path | None = None) -> None:
        candidates = _enrich_widget_reference(candidates)
        candidates = _sort_candidates_for_review(candidates, mode=candidate_sort.value)
        if not candidates.empty and "ticker" in candidates.columns:
            candidates = candidates.copy()
            candidates["_ticker_review_index"] = candidates.groupby("ticker").cumcount() + 1
            candidates["_ticker_review_count"] = candidates.groupby("ticker")["ticker"].transform("size")
        state["candidates"] = candidates
        if run_dir is not None:
            run_dir_text.value = str(run_dir)
        options = []
        for row in candidates.itertuples(index=False):
            symbol = _clean_value(getattr(row, "tradingview_symbol", None)) or _clean_value(getattr(row, "ticker", ""))
            ticker_count = int(getattr(row, "_ticker_review_count", 1))
            ticker_index = int(getattr(row, "_ticker_review_index", 1))
            repeat_tag = f" [{ticker_index}/{ticker_count}]" if ticker_count > 1 else ""
            wick_type = _clean_value(getattr(row, "first_green_wick_dip_type", None))
            wick_tag = f" wick={wick_type}" if isinstance(wick_type, str) and wick_type else ""
            visible_maxpush = _visible_maxpush_pct(row._asdict())
            maxpush_label = f"{visible_maxpush:.2f}%" if visible_maxpush is not None else "na"
            trigger_ts = _clean_value(getattr(row, "scanner_trigger_ts_et", ""))
            options.append(
                (
                    f"{symbol}{repeat_tag} {row.session_date} state={row.das_state} "
                    f"maxpush={maxpush_label}{wick_tag} trigger={trigger_ts}",
                    row.candidate_id,
                )
            )
        candidate_dropdown.options = options
        option_values = [value for _, value in options]
        if option_values and candidate_dropdown.value not in option_values:
            candidate_dropdown.value = option_values[0]
        elif not option_values:
            candidate_dropdown.value = None
        _sync_tradingview_symbol()

    def _resort_loaded_candidates(_change=None) -> None:
        candidates = state.get("candidates")
        if isinstance(candidates, pd.DataFrame):
            current = candidate_dropdown.value
            _set_candidates(candidates, None)
            if current in [value for _, value in candidate_dropdown.options]:
                candidate_dropdown.value = current

    def _selected_candidate_row() -> dict | None:
        candidates = state.get("candidates")
        if not isinstance(candidates, pd.DataFrame) or not candidate_dropdown.value:
            return None
        selected = candidates[candidates["candidate_id"].eq(candidate_dropdown.value)]
        if selected.empty:
            return None
        return selected.iloc[0].to_dict()

    def _row_text(row: dict, *keys: str) -> str:
        for key in keys:
            value = _clean_value(row.get(key))
            if value is not None:
                return str(value)
        return ""

    def _sync_tradingview_symbol(_change=None) -> None:
        row = _selected_candidate_row()
        if not row:
            tradingview_symbol_text.value = ""
            event_time_text.value = ""
            company_name_text.value = ""
            tradingview_copy_text.value = ""
            return
        symbol = _row_text(row, "tradingview_symbol", "ticker")
        name = _row_text(row, "name", "security_name")
        event_time = _row_text(row, "first_rebreak_ts_et", "scanner_trigger_ts_et", "scanner_trigger_ts_utc")
        tradingview_symbol_text.value = symbol
        event_time_text.value = event_time
        company_name_text.value = name
        tradingview_copy_text.value = f"{symbol}\n{event_time}\n{name}".strip()

    def _refresh_run_list() -> None:
        run_dropdown.options = _list_run_options()
        if run_dropdown.options:
            run_dropdown.value = run_dropdown.options[0][1]
            run_dir_text.value = str(run_dropdown.value)

    def _on_run_dropdown_change(change) -> None:
        if change.get("new"):
            run_dir_text.value = str(change["new"])

    def _print_run_header(run_dir: Path, candidates: pd.DataFrame | None = None) -> None:
        manifest = _read_manifest(run_dir)
        print("Run metadata:")
        print(f"  run_id: {run_dir.name}")
        print(f"  run_datetime_utc: {manifest.get('run_datetime_utc') or _run_datetime_utc_label(run_dir.name)}")
        print(f"  run_dir: {run_dir}")
        print(f"  status: {manifest.get('run_status', 'unknown')}")
        print(f"  files: {manifest.get('files_scanned', 0)}/{manifest.get('total_files', 0)}")
        print(f"  raw_candidates: {manifest.get('raw_candidate_count', 0)}")
        print(f"  candidates: {len(candidates) if candidates is not None else manifest.get('candidate_count', 0)}")
        print(f"  metadata_file: {run_dir / 'RUN_METADATA.md'}")
        print(f"  launcher_file: {run_dir / 'terminal_launcher.ps1'}")

    def _run(_button) -> None:
        with out:
            clear_output()
            cfg = _config()
            run_dir = create_run_dir(cfg)
            print(f"Run: {run_dir.name}")
            print(f"Run date UTC: {_run_datetime_utc_label(run_dir.name)}")
            print(f"Run dir: {run_dir}")
            print("Status: running")
            try:
                candidates = find_das_candidates(cfg, run_dir=run_dir)
                finalize_run(run_dir, candidates, cfg)
            except Exception as exc:
                _write_manifest(run_dir, cfg, "failed", 0, 0, 0, 0, error=repr(exc))
                print("Status: failed")
                raise
            _set_candidates(candidates, run_dir)
            print("Status: completed")
            print(f"Candidates: {len(candidates)}")
            print("")
            _print_run_header(run_dir, candidates)
            print("Delete this run if needed:")
            print(_delete_run_command(run_dir))
            if not candidates.empty:
                display(candidates.head(20))
            _refresh_run_list()

    def _load_run_path(path: Path, partial: bool = False, quiet_partial: bool = False) -> None:
        candidates = _load_partial_candidates_from_run(path) if partial else _load_candidates_from_run(path)
        _set_candidates(candidates, path)
        print(f"Loaded run: {path.name}")
        print(f"Run date UTC: {_run_datetime_utc_label(path.name)}")
        print(f"Run dir: {path}")
        print(f"Candidates: {len(candidates)}")
        if not quiet_partial:
            print("")
            _print_run_header(path, candidates)
        print("Delete this run if needed:")
        print(_delete_run_command(path))
        if not candidates.empty:
            display(candidates.tail(5) if quiet_partial else candidates.head(20))

    def _load_run(_button) -> None:
        with out:
            clear_output()
            if not run_dir_text.value.strip():
                print("Paste a run_dir first, or use Load latest.")
                return
            path = _run_dir_path_from_text(run_dir_text.value)
            if path is None:
                print("Paste a run_dir first, or use Load latest.")
                return
            run_dir_text.value = str(path)
            if not path.exists():
                print(f"Run dir not found: {path}")
                return
            _load_run_path(path)

    def _load_selected(_button) -> None:
        if not run_dropdown.value:
            with out:
                clear_output()
                print("No run selected. Use Refresh runs first.")
            return
        run_dir_text.value = str(run_dropdown.value)
        _load_run(_button)

    def _load_latest(_button) -> None:
        with out:
            clear_output()
            _refresh_run_list()
            if not run_dropdown.value:
                print(f"No runs found under {DEFAULT_RUNS_ROOT}")
                return
            run_dir_text.value = str(run_dropdown.value)
        _load_run(_button)

    def _refresh_partial(_button) -> None:
        with out:
            clear_output()
            if not run_dir_text.value.strip():
                print("Paste a run_dir first, or use Load latest.")
                return
            path = _run_dir_path_from_text(run_dir_text.value)
            if path is None:
                print("Paste a run_dir first, or use Load latest.")
                return
            run_dir_text.value = str(path)
            if not path.exists():
                print(f"Run dir not found: {path}")
                return
            candidates = _load_partial_candidates_from_run(path)
            _set_candidates(candidates, path)
            print(f"Loaded partial run: {path.name}")
            print(f"Run date UTC: {_run_datetime_utc_label(path.name)}")
            print(f"Run dir: {path}")
            print(f"Partial candidates: {len(candidates)}")
            print("Delete this run if needed:")
            print(_delete_run_command(path))
            if not candidates.empty:
                display(candidates.tail(5))

    def _render(_button) -> None:
        with out:
            if "candidates" not in state:
                print("Load or run candidates first.")
                return
            if not candidate_dropdown.value:
                print("No candidate selected.")
                return
            row = _selected_candidate_row()
            if row is None:
                print("No candidate selected.")
                return
            clear_output()
            print(f"Rendering {row['candidate_id']}")
            print(f"TradingView symbol: {_row_text(row, 'tradingview_symbol', 'ticker')}")
            print(f"Company: {_row_text(row, 'name', 'security_name')}")
            print(f"DAS state: {row.get('das_state')}")
            print(f"Green wick dip: {_row_text(row, 'first_green_wick_dip_type')}")
            print(f"Green wick dip ET: {_row_text(row, 'first_green_wick_dip_ts_et')}")
            print(f"Green wick dip low: {_row_text(row, 'first_green_wick_dip_low')}")
            print(f"Green wick dip depth %: {_row_text(row, 'first_green_wick_dip_depth_pct')}")
            for idx, (title, fig) in enumerate(
                render_candidate_charts(
                    row,
                    data_root.value,
                    price_view.value,
                    vwap_source.value,
                    y_padding.value,
                ),
                start=1,
            ):
                display(HTML(f"<h3>{title}</h3>"))
                if idx == 1:
                    fig.show(config={"scrollZoom": True, "displaylogo": False})
                else:
                    fig.show(config={"staticPlot": True, "displayModeBar": False, "displaylogo": False})

    def _export_detail_run(_button) -> None:
        with out:
            clear_output()

            def _emit(message: str) -> None:
                out.append_stdout(f"{message}\n")

            if not run_dir_text.value.strip():
                _emit("Paste a run_dir first, or use Load latest.")
                return
            path = _run_dir_path_from_text(run_dir_text.value)
            if path is None:
                _emit("Paste a run_dir first, or use Load latest.")
                return
            run_dir_text.value = str(path)
            if not path.exists():
                _emit(f"Run dir not found: {path}")
                return
            candidates = _load_candidates_from_run(path)
            if candidates.empty:
                candidates = _load_partial_candidates_from_run(path)
            candidates = _enrich_widget_reference(candidates)
            if candidates.empty:
                _emit(f"No candidates found in run: {path}")
                return
            export_root = path / "chart_exports"
            _emit("Exporting grouped DAS chart 2, chart 3, chart 4 and daily context images...")
            _emit(f"Run dir: {path}")
            _emit(f"Export dir: {export_root}")
            _emit(f"Grouped details: {export_root / 'event_day_details_grouped'}")
            _emit(f"Candidates: {len(candidates)}")
            try:
                _ensure_plotly_png_export_available()
            except RuntimeError as exc:
                _emit(str(exc))
                return

            def _progress(position: int, total: int, image_path: Path, row: dict) -> None:
                _emit(f"exported {position}/{total} {row.get('ticker')} {row.get('session_date')} -> {image_path.name}/")

            export_root, paths = export_run_event_day_detail_images(
                candidates,
                path,
                data_root.value,
                price_view.value,
                vwap_source.value,
                y_padding.value,
                sort_mode=candidate_sort.value,
                progress_callback=_progress,
            )
            _emit(f"Done. Images: {len(paths)}")
            _emit(f"Manifest: {export_root / 'EXPORT_MANIFEST.csv'}")
            errors_path = export_root / "EXPORT_ERRORS.csv"
            if errors_path.exists():
                _emit(f"Errors: {errors_path}")

    def _export_premarket_detail_run(_button) -> None:
        with out:
            clear_output()

            def _emit(message: str) -> None:
                out.append_stdout(f"{message}\n")

            if not run_dir_text.value.strip():
                _emit("Paste a run_dir first, or use Load latest.")
                return
            path = _run_dir_path_from_text(run_dir_text.value)
            if path is None:
                _emit("Paste a run_dir first, or use Load latest.")
                return
            run_dir_text.value = str(path)
            if not path.exists():
                _emit(f"Run dir not found: {path}")
                return
            candidates = _load_candidates_from_run(path)
            if candidates.empty:
                candidates = _load_partial_candidates_from_run(path)
            candidates = _enrich_widget_reference(candidates)
            if candidates.empty:
                _emit(f"No candidates found in run: {path}")
                return
            _emit("Exporting only chart 03_event_day_premarket_detail...")
            _emit("This writes to a separate timestamped folder and does not delete other exports.")
            _emit(f"Run dir: {path}")
            _emit(f"Candidates: {len(candidates)}")
            try:
                _ensure_plotly_png_export_available()
            except RuntimeError as exc:
                _emit(str(exc))
                return

            def _progress(position: int, total: int, image_path: Path, row: dict) -> None:
                _emit(f"exported {position}/{total} {row.get('ticker')} {row.get('session_date')} -> {image_path.name}")

            export_root, paths = export_run_premarket_detail_images(
                candidates,
                path,
                data_root.value,
                price_view.value,
                vwap_source.value,
                y_padding.value,
                sort_mode=candidate_sort.value,
                progress_callback=_progress,
            )
            _emit(f"Done. Images: {len(paths)}")
            _emit(f"Export dir: {export_root}")
            _emit(f"Manifest: {export_root / 'EXPORT_MANIFEST.csv'}")
            errors_path = export_root / "EXPORT_ERRORS.csv"
            if errors_path.exists():
                _emit(f"Errors: {errors_path}")

    def _render_tradingview_selected(_button) -> None:
        with out:
            row = _selected_candidate_row()
            if row is None:
                print("No candidate selected.")
                return
            symbol = _row_text(row, "tradingview_symbol", "ticker").strip()
            if not symbol:
                print("Selected candidate has no TradingView symbol.")
                return
            tradingview_symbol_text.value = symbol
            print(f"TradingView symbol: {symbol}")
            print(f"Event time ET: {_row_text(row, 'first_rebreak_ts_et', 'scanner_trigger_ts_et', 'scanner_trigger_ts_utc')}")
            company = _row_text(row, "name", "security_name")
            if company:
                print(f"Company: {company}")
            display(tradingview_widget(symbol=symbol, interval=tradingview_interval.value.strip() or "1"))

    refresh_runs_button.on_click(lambda _button: _refresh_run_list())
    run_dropdown.observe(_on_run_dropdown_change, names="value")
    load_selected_button.on_click(_load_selected)
    load_latest_button.on_click(_load_latest)
    load_run_button.on_click(_load_run)
    refresh_partial_button.on_click(_refresh_partial)
    render_button.on_click(_render)
    export_detail_run_button.on_click(_export_detail_run)
    export_premarket_detail_button.on_click(_export_premarket_detail_run)
    tradingview_button.on_click(_render_tradingview_selected)
    run_button.on_click(_run)
    candidate_sort.observe(_resort_loaded_candidates, names="value")
    candidate_dropdown.observe(_sync_tradingview_symbol, names="value")
    for control in [
        data_root,
        reference_root,
        universe_path,
        tickers,
        years,
        session_scope,
        momentum_trigger_pct,
        min_session_volume,
        min_price,
        max_price,
        max_market_cap,
        missing_cap,
        price_view,
        vwap_source,
        progress_every,
        partial_flush,
    ]:
        control.observe(_refresh_command, names="value")
    _refresh_command()
    _refresh_run_list()

    help_text = widgets.HTML(
        value=(
            "<b>DAS scanner-first search:</b> candidate = first appearance in the screener "
            "(market cap, session volume and price). Push, dip, rebreak and DAS state are "
            "measured afterwards as diagnostics, not used as hard filters."
        )
    )
    definitions_text = widgets.HTML(value=_format_field_definitions_html())
    return widgets.VBox(
        [
            help_text,
            definitions_text,
            data_root,
            reference_root,
            universe_path,
            widgets.HBox([tickers, years, session_scope, momentum_trigger_pct, price_view, vwap_source]),
            widgets.HBox([min_session_volume, min_price, max_price, max_market_cap, missing_cap, y_padding]),
            widgets.HBox([progress_every, partial_flush]),
            command_preview,
            command_preview_one_line,
            widgets.HBox([refresh_runs_button, load_selected_button, load_latest_button]),
            run_dropdown,
            run_dir_text,
            widgets.HBox(
                [
                    load_run_button,
                    refresh_partial_button,
                    render_button,
                    export_detail_run_button,
                    export_premarket_detail_button,
                    run_button,
                ]
            ),
            candidate_sort,
            candidate_dropdown,
            widgets.HBox([tradingview_symbol_text, event_time_text, tradingview_interval, tradingview_button]),
            company_name_text,
            tradingview_copy_text,
            out,
        ]
    )


def launch_das_stats_app():
    import ipywidgets as widgets
    from IPython.display import HTML, Markdown, clear_output, display

    from build_das_candidate_state_table_experimental import write_outputs
    from build_das_experimental_stats_report import build_report

    variant_definitions = {
        "A_plus_continuation": (
            "Secuencia frontside limpia: primer push fuerte, dip controlado, rebreak y continuacion clara. "
            "Sirve como referencia de calidad alta, no como garantia de edge."
        ),
        "green_wick_reactivation": (
            "Reactivacion donde el dip aparece dentro de una vela que deja mecha inferior y cierra recuperando. "
            "La lectura es absorcion rapida del retroceso con momentum todavia vivo."
        ),
        "vwap_dip_reclaim": (
            "Dip que pierde o prueba VWAP y despues recupera/reclama la zona. "
            "La lectura es que VWAP funciona como frontera de control intradia."
        ),
        "early_red_high_break": (
            "Rebreak temprano del high de una vela roja relevante del primer push. "
            "La lectura es ruptura de defensa/fallo bajista antes de que se forme una base amplia."
        ),
        "unclear": (
            "El candidato cumple reglas mecanicas, pero la forma visual no permite clasificarlo con confianza. "
            "Debe revisarse manualmente antes de usarlo como ejemplo positivo."
        ),
    }
    rebreak_definitions = {
        "single_candle_rebreak": "Una sola vela rompe de nuevo el nivel relevante del primer push.",
        "multi_candle_flag_break": "Varias velas forman una bandera o compresion y luego rompen al alza.",
        "ascending_flag_break": "La base previa al rebreak sube gradualmente; hay lows o closes ascendentes antes de romper.",
        "flat_shelf_break": "El precio acepta una zona lateral elevada y rompe una meseta relativamente plana.",
        "last_red_high_break": "El trigger se produce al superar el high de la ultima vela roja defensiva.",

    }

    data_root = widgets.Text(value=str(DEFAULT_DATA_ROOT), description="1m root", layout=widgets.Layout(width="95%"))
    price_view = widgets.Dropdown(options=["raw", "split_normalized"], value="raw", description="Price")
    vwap_source = widgets.Dropdown(
        options=[("Calculated", "calculated"), ("Raw vw", "raw")],
        value="calculated",
        description="VWAP",
    )
    y_padding = widgets.BoundedFloatText(value=0.40, min=0.05, max=1.00, step=0.05, description="Y padding")
    run_dropdown = widgets.Dropdown(options=[], description="Runs", layout=widgets.Layout(width="95%"))
    run_dir_text = widgets.Text(value="", description="Run dir", layout=widgets.Layout(width="95%"))
    variant_dropdown = widgets.Dropdown(options=[], description="Variant", layout=widgets.Layout(width="70%"))
    example_dropdown = widgets.Dropdown(options=[], description="Example", layout=widgets.Layout(width="95%"))
    report_dropdown = widgets.Dropdown(options=[], description="Reports", layout=widgets.Layout(width="95%"))
    refresh_runs_button = widgets.Button(description="Refresh runs")
    load_selected_button = widgets.Button(description="Load selected", button_style="primary")
    load_latest_button = widgets.Button(description="Load latest")
    load_run_button = widgets.Button(description="Load stats")
    build_report_button = widgets.Button(description="Build MD report")
    refresh_reports_button = widgets.Button(description="Refresh reports")
    view_report_button = widgets.Button(description="View MD report")
    show_variant_button = widgets.Button(description="Show variant")
    render_example_button = widgets.Button(description="Render example")
    out = widgets.Output()
    state: dict[str, object] = {}

    def _run_path() -> Path | None:
        if not run_dir_text.value.strip():
            return None
        path = _run_dir_path_from_text(run_dir_text.value)
        if path is None or not path.exists():
            return None
        run_dir_text.value = str(path)
        return path

    def _refresh_run_list() -> None:
        run_dropdown.options = _list_run_options()
        if run_dropdown.options:
            run_dropdown.value = run_dropdown.options[0][1]
            run_dir_text.value = str(run_dropdown.value)

    def _on_run_dropdown_change(change) -> None:
        if change.get("new"):
            run_dir_text.value = str(change["new"])

    def _state_table_path(run_dir: Path) -> Path:
        return run_dir / "state_tables" / "das_candidate_state_table_experimental_v0_1.parquet"

    def _load_or_build_state_table(run_dir: Path) -> pd.DataFrame:
        table_path = _state_table_path(run_dir)
        if not table_path.exists():
            table_path = write_outputs(run_dir, run_dir / "state_tables")
        return pd.read_parquet(table_path)

    def _load_original_candidates(run_dir: Path) -> pd.DataFrame:
        candidates = _load_candidates_from_run(run_dir)
        if candidates.empty:
            candidates = _load_partial_candidates_from_run(run_dir)
        return candidates

    def _report_options(run_dir: Path) -> list[tuple[str, str]]:
        paths = []
        for path in [
            run_dir / "RUN_METADATA.md",
            run_dir / "state_tables" / "das_candidate_state_table_experimental_v0_1_summary.md",
            run_dir / "state_tables" / "das_candidate_state_table_experimental_v0_1_stats_report.md",
        ]:
            if path.exists():
                paths.append(path)
        state_dir = run_dir / "state_tables"
        if state_dir.exists():
            for path in sorted(state_dir.glob("*.md")):
                if path not in paths:
                    paths.append(path)
        return [(f"{path.relative_to(run_dir)}", str(path)) for path in paths]

    def _refresh_report_list(run_dir: Path | None = None) -> None:
        path = run_dir or _run_path()
        if path is None:
            report_dropdown.options = []
            report_dropdown.value = None
            return
        current = report_dropdown.value
        report_dropdown.options = _report_options(path)
        values = [value for _, value in report_dropdown.options]
        if current in values:
            report_dropdown.value = current
        elif values:
            report_dropdown.value = values[0]
        else:
            report_dropdown.value = None

    def _bucket_columns(df: pd.DataFrame) -> pd.DataFrame:
        out_df = df.copy()
        max_momentum = pd.to_numeric(out_df.get("frontside__max_momentum_pct_from_premarket_open"), errors="coerce")
        first_dip = pd.to_numeric(out_df.get("frontside__first_dip_depth_pct"), errors="coerce")
        out_df["_max_momentum_bucket"] = pd.cut(
            max_momentum,
            bins=[-99999, 20, 50, 100, 200, 500, 999999],
            labels=["<20%", "20-50%", "50-100%", "100-200%", "200-500%", ">=500%"],
            include_lowest=True,
            right=False,
        )
        out_df["_first_dip_bucket"] = pd.cut(
            first_dip,
            bins=[-99999, 5, 10, 20, 35, 50, 999999],
            labels=["<5%", "5-10%", "10-20%", "20-35%", "35-50%", ">=50%"],
            include_lowest=True,
            right=False,
        )
        return out_df

    def _definitions_html() -> str:
        variant_rows = "".join(
            "<tr><td><code>{}</code></td><td>{}</td></tr>".format(
                html_lib.escape(key), html_lib.escape(value)
            )
            for key, value in variant_definitions.items()
        )
        rebreak_rows = "".join(
            "<tr><td><code>{}</code></td><td>{}</td></tr>".format(
                html_lib.escape(key), html_lib.escape(value)
            )
            for key, value in rebreak_definitions.items()
        )
        return (
            "<h3>Definiciones de variantes DAS</h3>"
            "<table><thead><tr><th>Nombre</th><th>Lectura</th></tr></thead><tbody>"
            f"{variant_rows}</tbody></table>"
            "<h3>Definiciones de tipo de rebreak</h3>"
            "<table><thead><tr><th>Nombre</th><th>Lectura</th></tr></thead><tbody>"
            f"{rebreak_rows}</tbody></table>"
        )

    def _display_summary(df: pd.DataFrame, run_dir: Path) -> None:
        df = _bucket_columns(df)
        state["df"] = df
        candidates = state.get("candidates")
        print(f"Run: {run_dir.name}")
        print(f"Rows: {len(df)}")
        if "identity__ticker" in df.columns:
            print(f"Tickers: {df['identity__ticker'].nunique()}")
        if "identity__session_date" in df.columns:
            print(f"Dates: {df['identity__session_date'].min()} -> {df['identity__session_date'].max()}")
        if isinstance(candidates, pd.DataFrame):
            print(f"Original candidates loaded: {len(candidates)}")
        print("")
        display(HTML(_definitions_html()))

        variant_counts = df["das__variant"].fillna("unknown").value_counts() if "das__variant" in df.columns else pd.Series(dtype=int)
        fig = go.Figure(
            data=[
                go.Bar(
                    x=variant_counts.index.astype(str),
                    y=variant_counts.values,
                    marker_color="#3b82f6",
                    text=variant_counts.values,
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(
            title="DAS variants: cuantos candidatos hay por nombre de evento",
            xaxis_title="das__variant",
            yaxis_title="count",
            height=430,
            margin=dict(l=40, r=20, t=70, b=90),
        )
        fig.show(config={"displaylogo": False})

        bucket_counts = df["_max_momentum_bucket"].value_counts(sort=False, dropna=False)
        fig = go.Figure(
            data=[
                go.Bar(
                    x=bucket_counts.index.astype(str),
                    y=bucket_counts.values,
                    marker_color="#10b981",
                    text=bucket_counts.values,
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(
            title="Max momentum buckets desde apertura premarket",
            xaxis_title="max_momentum_bucket",
            yaxis_title="count",
            height=390,
            margin=dict(l=40, r=20, t=70, b=70),
        )
        fig.show(config={"displaylogo": False})

        crosstab_counts = pd.crosstab(df["_max_momentum_bucket"], df["_first_dip_bucket"], dropna=False)
        crosstab_pct = crosstab_counts.div(crosstab_counts.sum(axis=1).replace(0, pd.NA), axis=0) * 100.0
        fig = go.Figure(
            data=go.Heatmap(
                z=crosstab_pct.fillna(0).values,
                x=[str(x) for x in crosstab_pct.columns],
                y=[str(y) for y in crosstab_pct.index],
                colorscale="YlGnBu",
                text=crosstab_pct.round(1).astype(str).values,
                texttemplate="%{text}%",
                hovertemplate="max momentum=%{y}<br>dip depth=%{x}<br>row pct=%{z:.2f}%<extra></extra>",
            )
        )
        fig.update_layout(
            title="Profundidad del primer dip dentro de cada bucket de max momentum",
            xaxis_title="first_dip_depth_bucket",
            yaxis_title="max_momentum_bucket",
            height=470,
            margin=dict(l=90, r=20, t=80, b=70),
        )
        fig.show(config={"displaylogo": False})

        display(HTML("<h3>Tabla: profundidad del primer dip por bucket de max momentum</h3>"))
        display(crosstab_pct.round(2))

        grouped = (
            df.groupby("_max_momentum_bucket", observed=False)["frontside__first_dip_depth_pct"]
            .agg(["count", "mean", "median"])
            .reset_index()
        )
        display(HTML("<h3>Resumen numerico de dip por bucket de max momentum</h3>"))
        display(grouped)

        fig = go.Figure()
        for bucket, group in df.groupby("_max_momentum_bucket", observed=False):
            values = pd.to_numeric(group["frontside__first_dip_depth_pct"], errors="coerce").dropna()
            if values.empty:
                continue
            fig.add_trace(go.Box(y=values, name=str(bucket), boxmean=True))
        fig.update_layout(
            title="Distribucion de profundidad del primer dip por max momentum bucket",
            xaxis_title="max_momentum_bucket",
            yaxis_title="first_dip_depth_pct",
            height=430,
            margin=dict(l=50, r=20, t=70, b=70),
        )
        fig.show(config={"displaylogo": False})

        if {"frontside__max_momentum_pct_from_premarket_open", "frontside__first_dip_depth_pct", "das__variant"}.issubset(df.columns):
            fig = go.Figure()
            for variant, group in df.groupby("das__variant", dropna=False):
                fig.add_trace(
                    go.Scatter(
                        x=pd.to_numeric(group["frontside__max_momentum_pct_from_premarket_open"], errors="coerce"),
                        y=pd.to_numeric(group["frontside__first_dip_depth_pct"], errors="coerce"),
                        mode="markers",
                        name=str(variant),
                        text=group.get("identity__tradingview_symbol", group.get("identity__ticker", "")),
                        hovertemplate="%{text}<br>max momentum=%{x:.2f}%<br>dip depth=%{y:.2f}%<extra></extra>",
                    )
                )
            fig.update_layout(
                title="Relacion max momentum vs profundidad del primer dip",
                xaxis_title="frontside__max_momentum_pct_from_premarket_open",
                yaxis_title="frontside__first_dip_depth_pct",
                height=520,
                margin=dict(l=50, r=20, t=70, b=70),
            )
            fig.show(config={"displaylogo": False})

    def _set_variant_options() -> None:
        df = state.get("df")
        if not isinstance(df, pd.DataFrame) or "das__variant" not in df.columns:
            variant_dropdown.options = []
            example_dropdown.options = []
            return
        variants = sorted(str(v) for v in df["das__variant"].dropna().unique())
        variant_dropdown.options = [(variant, variant) for variant in variants]
        if variants and variant_dropdown.value not in variants:
            variant_dropdown.value = variants[0]
        _set_example_options()

    def _set_example_options() -> None:
        df = state.get("df")
        if not isinstance(df, pd.DataFrame) or not variant_dropdown.value:
            example_dropdown.options = []
            return
        subset = df[df["das__variant"].astype(str).eq(str(variant_dropdown.value))].copy()
        if "frontside__max_momentum_pct_from_premarket_open" in subset.columns:
            subset["_sort"] = pd.to_numeric(subset["frontside__max_momentum_pct_from_premarket_open"], errors="coerce")
            subset = subset.sort_values("_sort", ascending=False)
        options = []
        for row in subset.head(100).itertuples(index=False):
            data = row._asdict()
            symbol = data.get("identity__tradingview_symbol") or data.get("identity__ticker")
            date = data.get("identity__session_date")
            max_momentum = pd.to_numeric(pd.Series([data.get("frontside__max_momentum_pct_from_premarket_open")]), errors="coerce").iloc[0]
            dip = pd.to_numeric(pd.Series([data.get("frontside__first_dip_depth_pct")]), errors="coerce").iloc[0]
            max_label = f"{max_momentum:.2f}%" if pd.notna(max_momentum) else "na"
            dip_label = f"{dip:.2f}%" if pd.notna(dip) else "na"
            candidate_id = data.get("identity__das_candidate_id")
            options.append((f"{symbol} {date} max={max_label} dip={dip_label}", candidate_id))
        example_dropdown.options = options
        if options and example_dropdown.value not in [value for _, value in options]:
            example_dropdown.value = options[0][1]

    def _load_stats_for_run(run_dir: Path) -> None:
        candidates = _load_original_candidates(run_dir)
        state["candidates"] = candidates
        df = _load_or_build_state_table(run_dir)
        _display_summary(df, run_dir)
        _set_variant_options()
        _refresh_report_list(run_dir)

    def _load_run(_button) -> None:
        with out:
            clear_output()
            path = _run_path()
            if path is None:
                print("Paste a valid run_dir first, or use Load latest.")
                return
            _load_stats_for_run(path)

    def _load_selected(_button) -> None:
        if not run_dropdown.value:
            with out:
                clear_output()
                print("No run selected. Use Refresh runs first.")
            return
        run_dir_text.value = str(run_dropdown.value)
        _load_run(_button)

    def _load_latest(_button) -> None:
        with out:
            clear_output()
            _refresh_run_list()
            if not run_dropdown.value:
                print(f"No runs found under {DEFAULT_RUNS_ROOT}")
                return
            run_dir_text.value = str(run_dropdown.value)
        _load_run(_button)

    def _build_markdown_report(_button) -> None:
        with out:
            path = _run_path()
            if path is None:
                print("Paste a valid run_dir first, or use Load latest.")
                return
            table_path = _state_table_path(path)
            if not table_path.exists():
                table_path = write_outputs(path, path / "state_tables")
            report_path = table_path.with_name("das_candidate_state_table_experimental_v0_1_stats_report.md")
            build_report(table_path, report_path)
            _refresh_report_list(path)
            report_dropdown.value = str(report_path)
            print(f"Markdown report written: {report_path}")

    def _refresh_reports(_button) -> None:
        with out:
            clear_output()
            path = _run_path()
            if path is None:
                print("Paste a valid run_dir first, or use Load latest.")
                return
            _refresh_report_list(path)
            print(f"Reports refreshed for: {path.name}")
            print(f"Reports found: {len(report_dropdown.options)}")

    def _view_report(_button) -> None:
        with out:
            clear_output()
            if not report_dropdown.value:
                print("No report selected.")
                return
            path = Path(str(report_dropdown.value))
            if not path.exists():
                print(f"Report not found: {path}")
                return
            display(Markdown(path.read_text(encoding="utf-8")))

    def _show_variant(_button) -> None:
        with out:
            df = state.get("df")
            if not isinstance(df, pd.DataFrame):
                print("Load stats first.")
                return
            variant = str(variant_dropdown.value or "")
            clear_output()
            print(f"Variant: {variant}")
            print(variant_definitions.get(variant, "No definition yet."))
            subset = df[df["das__variant"].astype(str).eq(variant)].copy()
            if "frontside__max_momentum_pct_from_premarket_open" in subset.columns:
                subset["_sort"] = pd.to_numeric(subset["frontside__max_momentum_pct_from_premarket_open"], errors="coerce")
                subset = subset.sort_values("_sort", ascending=False)
            cols = [
                "identity__tradingview_symbol",
                "identity__session_date",
                "frontside__max_momentum_pct_from_premarket_open",
                "frontside__first_dip_depth_pct",
                "frontside__rebreak_type",
                "scanner__trigger_gap_pct_from_prior_close",
                "scanner__trigger_volume_today",
            ]
            display(subset[[c for c in cols if c in subset.columns]].head(20))
            _set_example_options()

    def _render_example(_button) -> None:
        with out:
            candidates = state.get("candidates")
            if not isinstance(candidates, pd.DataFrame):
                print("Load stats first.")
                return
            if not example_dropdown.value:
                print("Select an example first.")
                return
            selected = candidates[candidates["candidate_id"].eq(example_dropdown.value)]
            if selected.empty:
                print(f"Candidate not found in original run: {example_dropdown.value}")
                return
            row = selected.iloc[0].to_dict()
            clear_output()
            print(f"Rendering example: {row.get('candidate_id')}")
            print(f"Ticker: {row.get('tradingview_symbol') or row.get('ticker')}")
            print(f"Variant: {variant_dropdown.value}")
            for idx, (title, fig) in enumerate(
                render_candidate_charts(
                    row,
                    data_root.value,
                    price_view.value,
                    vwap_source.value,
                    y_padding.value,
                ),
                start=1,
            ):
                display(HTML(f"<h3>{title}</h3>"))
                if idx == 1:
                    fig.show(config={"scrollZoom": True, "displaylogo": False})
                else:
                    fig.show(config={"staticPlot": True, "displayModeBar": False, "displaylogo": False})

    refresh_runs_button.on_click(lambda _button: _refresh_run_list())
    run_dropdown.observe(_on_run_dropdown_change, names="value")
    load_selected_button.on_click(_load_selected)
    load_latest_button.on_click(_load_latest)
    load_run_button.on_click(_load_run)
    build_report_button.on_click(_build_markdown_report)
    refresh_reports_button.on_click(_refresh_reports)
    view_report_button.on_click(_view_report)
    show_variant_button.on_click(_show_variant)
    render_example_button.on_click(_render_example)
    variant_dropdown.observe(lambda _change: _set_example_options(), names="value")
    _refresh_run_list()

    help_text = widgets.HTML(
        value=(
            "<b>DAS statistics app:</b> esta celda no busca candidatos. "
            "Carga runs ya creados por la celda superior, construye/lee la tabla experimental "
            "y muestra estadisticas visuales del embudo DAS confirmado."
        )
    )
    return widgets.VBox(
        [
            help_text,
            data_root,
            widgets.HBox([price_view, vwap_source, y_padding]),
            widgets.HBox([refresh_runs_button, load_selected_button, load_latest_button, load_run_button]),
            run_dropdown,
            run_dir_text,
            widgets.HBox([build_report_button, refresh_reports_button, view_report_button]),
            report_dropdown,
            widgets.HBox([variant_dropdown, show_variant_button, render_example_button]),
            example_dropdown,
            out,
        ]
    )


def tradingview_widget(symbol: str = "NASDAQ:CCSC", interval: str = "1"):
    from IPython.display import HTML

    symbol = str(symbol or "").strip().upper()
    interval = str(interval or "1").strip()
    frame_id = f"tradingview_{uuid4().hex}"
    params = {
        "frameElementId": frame_id,
        "symbol": symbol,
        "interval": interval,
        "hidesidetoolbar": "0",
        "symboledit": "1",
        "saveimage": "1",
        "toolbarbg": "f1f3f6",
        "studies": "[]",
        "theme": "light",
        "style": "1",
        "timezone": "America/New_York",
        "withdateranges": "1",
        "hideideas": "1",
        "locale": "en",
    }
    src = "https://www.tradingview.com/widgetembed/?" + urlencode(params)
    safe_symbol = html_lib.escape(symbol)
    safe_src = html_lib.escape(src, quote=True)
    safe_id = html_lib.escape(frame_id)
    html = f"""
    <div class="tradingview-widget-container" style="height:760px;width:100%; border:1px solid #d8dee9;">
      <div style="font-family:Arial,sans-serif;font-size:13px;padding:6px 8px;background:#f8fafc;border-bottom:1px solid #d8dee9;">
        TradingView: <code>{safe_symbol}</code>
      </div>
      <iframe
        id="{safe_id}"
        src="{safe_src}"
        title="TradingView {safe_symbol}"
        style="height:724px;width:100%;border:0;margin:0;padding:0;"
        allowtransparency="true"
        scrolling="no"
        allowfullscreen>
      </iframe>
    </div>
    """
    return HTML(html)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find exploratory DAS candidates.")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--reference-overview-root", default=str(DEFAULT_REFERENCE_OVERVIEW_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--universe-path", default=str(DEFAULT_LT1B_UNIVERSE_PATH))
    parser.add_argument("--tickers")
    parser.add_argument("--years")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--session-scope", choices=["premarket", "regular", "premarket_regular"], default="premarket")
    parser.add_argument("--push-label-pct", type=float, default=20.0)
    parser.add_argument("--dip-label-pct", type=float, default=3.0)
    parser.add_argument("--momentum-trigger-pct", type=float, default=50.0)
    parser.add_argument("--min-session-volume", type=float, default=500_000.0)
    parser.add_argument("--min-price", type=float, default=0.5)
    parser.add_argument("--max-price", type=float, default=20.0)
    parser.add_argument("--max-market-cap", type=float, default=100_000_000.0)
    parser.add_argument("--missing-market-cap-policy", choices=["include", "exclude", "flag"], default="include")
    parser.add_argument("--price-view", choices=["raw", "split_normalized"], default="raw")
    parser.add_argument("--vwap-source", choices=["calculated", "raw"], default="calculated")
    parser.add_argument("--max-candidates", type=int)
    parser.add_argument("--progress-every", type=int, default=250)
    parser.add_argument("--partial-flush-every", type=int, default=1)
    parser.add_argument("--export-detail-images-run-dir")
    parser.add_argument("--export-detail-limit", type=int)
    return parser


def config_from_args(args: argparse.Namespace) -> DasConfig:
    return DasConfig(
        data_root=args.data_root,
        reference_overview_root=args.reference_overview_root,
        output_root=args.output_root,
        universe_path=args.universe_path,
        tickers=_parse_csv(args.tickers),
        years=_parse_years(args.years),
        start_date=args.start_date,
        end_date=args.end_date,
        session_scope=args.session_scope,
        push_label_pct=args.push_label_pct,
        dip_label_pct=args.dip_label_pct,
        momentum_trigger_pct=args.momentum_trigger_pct,
        min_session_volume=args.min_session_volume,
        min_price=args.min_price,
        max_price=args.max_price,
        max_market_cap=args.max_market_cap,
        missing_market_cap_policy=args.missing_market_cap_policy,
        price_view=args.price_view,
        vwap_source=args.vwap_source,
        max_candidates=args.max_candidates,
        progress_every=args.progress_every,
        partial_flush_every=args.partial_flush_every,
    )


def main() -> int:
    args = build_arg_parser().parse_args()
    config = config_from_args(args)

    if args.export_detail_images_run_dir:
        run_dir = Path(args.export_detail_images_run_dir)
        candidates = _load_candidates_from_run(run_dir)
        if candidates.empty:
            candidates = _load_partial_candidates_from_run(run_dir)
        if candidates.empty:
            print(f"no_candidates={run_dir}", flush=True)
            return 1
        export_root, paths = export_run_event_day_detail_images(
            candidates,
            run_dir,
            config.data_root,
            config.price_view,
            config.vwap_source,
            0.40,
            limit=args.export_detail_limit,
        )
        print(f"export_dir={export_root}", flush=True)
        print(f"images={len(paths)}", flush=True)
        print(f"manifest={export_root / 'EXPORT_MANIFEST.csv'}", flush=True)
        return 0

    run_dir = create_run_dir(config)
    print(f"run_dir={run_dir}", flush=True)
    print("run_status=running", flush=True)
    try:
        candidates = find_das_candidates(config, run_dir=run_dir)
        finalize_run(run_dir, candidates, config)
    except Exception as exc:
        _write_manifest(run_dir, config, "failed", 0, 0, 0, 0, error=repr(exc))
        print("run_status=failed", flush=True)
        raise
    print(f"candidates={len(candidates)}", flush=True)
    print("run_status=completed", flush=True)
    print(f"delete_command={_delete_run_command(run_dir)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())







