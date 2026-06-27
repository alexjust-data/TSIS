"""DAS exploratory search and notebook widgets.

This module is exploratory. It searches for strategy samples, not promoted
events, trades, edge, entries, stops, targets, or sizing.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import html as html_lib
import json
from pathlib import Path
import sys
from typing import Callable, Iterable
from urllib.parse import urlencode
from uuid import uuid4

import pandas as pd
import plotly.graph_objects as go


STRATEGY_ROOT = Path(__file__).resolve().parent
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
            _ps_quote(str(STRATEGY_ROOT / "das_widgets.py")),
        ]
        for name, value in parts:
            flat.extend([name, value])
        flat.extend(flags)
        return " ".join(flat)

    lines = [
        f"Set-Location {_ps_quote(str(STRATEGY_ROOT))}",
        f"python {_ps_quote(str(STRATEGY_ROOT / 'das_widgets.py'))} `",
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
    if vwap_at_rebreak is not None and pd.notna(vwap_at_rebreak):
        below_vwap = (dip_to_break["px_c"].astype(float) < float(vwap_at_rebreak)).any()
        if below_vwap and float(rebreak_row["px_c"]) >= float(vwap_at_rebreak):
            return "vwap_reclaim_rebreak"
    if len(dip_to_break) >= 3:
        return "multi_candle_flag_break"
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
    if premarket.empty or pm_open_price is None or pm_open_price <= 0:
        return None, None, None
    push_threshold = pm_open_price * (1.0 + config.push_label_pct / 100.0)
    threshold_rows = premarket[premarket["px_h"].astype(float) >= push_threshold]
    if threshold_rows.empty:
        return None, None, None

    first_threshold_row = threshold_rows.iloc[0]
    threshold_pos = int(first_threshold_row.name)
    awakening_row = _find_awakening_start(premarket, pm_open_price, threshold_pos)

    current_high = float(first_threshold_row["px_h"])
    current_high_row = first_threshold_row
    first_dip_low_row: pd.Series | None = None

    for _, row in premarket.iloc[threshold_pos + 1 :].iterrows():
        high = float(row["px_h"])
        low = float(row["px_l"])
        if high > current_high:
            current_high = high
            current_high_row = row
            continue
        dip_depth_pct = (current_high - low) / current_high * 100.0 if current_high > 0 else 0.0
        if dip_depth_pct >= config.dip_label_pct:
            first_dip_low_row = row
            break

    return awakening_row, current_high_row, first_dip_low_row


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
    first_dip_pos = int(first_dip_low_row.name)
    first_push_high = float(first_push_high_row["px_h"])
    first_push_ts = first_push_high_row.get("ts_utc_dt")
    last_red_high, last_red_row = _last_red_high_before_rebreak(premarket, first_push_high_row, first_dip_low_row)
    active_level = last_red_high if last_red_high is not None else first_push_high
    active_level_kind = "last_red_pullback_high" if last_red_high is not None else "first_push_high"
    rows_since_dip: list[int] = []
    max_initial_rebreak_minutes = 45.0

    for _, row in premarket.iloc[first_dip_pos + 1 :].iterrows():
        row_ts = row.get("ts_utc_dt")
        if pd.notna(first_push_ts) and pd.notna(row_ts):
            elapsed_minutes = (row_ts - first_push_ts).total_seconds() / 60.0
            if elapsed_minutes > max_initial_rebreak_minutes:
                break

        rows_since_dip.append(int(row.name))
        close_px = float(row["px_c"])
        high_px = float(row["px_h"])

        if active_level is not None and _is_green_candle(row) and close_px > active_level and high_px > active_level:
            return row, active_level, active_level_kind, last_red_row, rows_since_dip
        if _is_green_candle(row) and close_px > first_push_high and high_px > first_push_high:
            return row, first_push_high, "first_push_high", last_red_row, rows_since_dip

    return None, active_level, active_level_kind, last_red_row, rows_since_dip


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

    push_threshold = trigger_price * (1.0 + config.push_label_pct / 100.0)
    threshold_rows = after_trigger[after_trigger["px_h"].astype(float) >= push_threshold]
    if not threshold_rows.empty:
        das_state = "push_detected"
        first_push_high_row = threshold_rows.iloc[0]
        current_high = float(first_push_high_row["px_h"])
        current_high_row = first_push_high_row
        first_threshold_pos = int(first_push_high_row.name)

        for _, row in work.iloc[first_threshold_pos + 1 :].iterrows():
            high = float(row["px_h"])
            low = float(row["px_l"])
            if high > current_high:
                current_high = high
                current_high_row = row
            dip_depth_pct = (current_high - low) / current_high * 100.0 if current_high > 0 else 0.0
            if dip_depth_pct >= config.dip_label_pct:
                first_push_high_row = current_high_row
                first_dip_low_row = row
                das_state = "push_and_dip"
                break

        if first_push_high_row is None:
            first_push_high_row = current_high_row

        if first_dip_low_row is not None:
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
    first_push_start_price = min(float(push_start_row["px_o"]), float(push_start_row["px_l"]))
    first_push_high = float(first_push_high_row["px_h"])
    first_push_body_high = max(float(first_push_high_row["px_o"]), float(first_push_high_row["px_c"]))

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


def _scanner_trigger_marker_text(candidate: dict) -> str:
    pct = _clean_value(candidate.get("pm_open_to_scanner_pct"))
    price = _clean_value(candidate.get("price_at_trigger"))
    volume = _clean_value(candidate.get("premarket_volume_at_trigger")) or _clean_value(
        candidate.get("session_volume_at_trigger")
    )
    pct_label = f"gap {float(pct):+.1f}%" if pct is not None else "gap na"
    price_label = f"${float(price):.4f}" if price is not None else "$na"
    volume_label = f"vol {_format_compact_volume(volume)}"
    return f"{pct_label}<br>{price_label}<br>{volume_label}<br>scanner trigger"


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
    ts_to_x = {
        "scanner": _bar_x_for_ts(chart_df, candidate.get("scanner_trigger_ts_utc")),
        "push_high": _bar_x_for_ts(chart_df, candidate.get("first_push_high_ts_utc")),
        "dip_low": _bar_x_for_ts(chart_df, candidate.get("first_dip_low_ts_utc")),
        "rebreak": _bar_x_for_ts(chart_df, candidate.get("first_rebreak_ts_utc")),
    }
    hidden_marker_labels = {"first push high", "first dip low", "DAS rebreak"}
    marker_rows = [
        ("scanner trigger", ts_to_x.get("scanner"), candidate.get("price_at_trigger"), "rgba(59,130,246,0.85)"),
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
        marker_mode = "markers" if label == "scanner trigger" else (
            "markers+text"
            if label in {"first dip low", "DAS rebreak"}
            else "markers"
        )
        marker_text = "" if label == "scanner trigger" else (
            label if label in {"first dip low", "DAS rebreak"} else ""
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
                    "scanner trigger<br>"
                    f"{_scanner_trigger_marker_text(candidate).replace('<br>', '<br>')}<br>"
                    "%{y:.4f}<extra></extra>"
                    if label == "scanner trigger"
                    else f"{label}<br>%{{y:.4f}}<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
        if label == "scanner trigger":
            x_position = int(x) / max(len(chart_df) - 1, 1)
            ax = -125 if x_position > 0.72 else 125
            ay = 105
            fig.add_annotation(
                x=marker_x,
                y=marker_y,
                text=_scanner_trigger_marker_text(candidate),
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor="rgba(37,99,235,0.8)",
                ax=ax,
                ay=ay,
                align="left",
                xanchor="left" if ax > 0 else "right",
                yanchor="top",
                font=dict(size=11, color="rgba(30,64,175,0.98)"),
                bgcolor="rgba(255,255,255,0.82)",
                bordercolor="rgba(37,99,235,0.35)",
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
    ]


def _ensure_plotly_png_export_available() -> None:
    try:
        import kaleido  # noqa: F401
    except Exception as exc:
        raise RuntimeError(
            "Could not export PNG. Plotly image export requires the `kaleido` package in the active Python environment."
        ) from exc


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
    if error_rows:
        pd.DataFrame(error_rows).to_csv(export_root / "EXPORT_ERRORS.csv", index=False)
    else:
        errors_path = export_root / "EXPORT_ERRORS.csv"
        if errors_path.exists():
            errors_path.unlink()
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
            _emit("Exporting grouped DAS chart 2, chart 3 and chart 4 images...")
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
            widgets.HBox([tickers, years, session_scope, price_view, vwap_source]),
            widgets.HBox([min_session_volume, min_price, max_price, max_market_cap, missing_cap, y_padding]),
            widgets.HBox([progress_every, partial_flush]),
            command_preview,
            command_preview_one_line,
            widgets.HBox([refresh_runs_button, load_selected_button, load_latest_button]),
            run_dropdown,
            run_dir_text,
            widgets.HBox([load_run_button, refresh_partial_button, render_button, export_detail_run_button, run_button]),
            candidate_sort,
            candidate_dropdown,
            widgets.HBox([tradingview_symbol_text, event_time_text, tradingview_interval, tradingview_button]),
            company_name_text,
            tradingview_copy_text,
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
