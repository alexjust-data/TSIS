"""Gap and Go exploratory search and notebook widgets.

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
from typing import Callable, Iterable
from urllib.parse import urlencode
from uuid import uuid4

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pyarrow.parquet as pq


STRATEGY_ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_ROOT = Path(r"E:\TSIS\data\ohlcv_1m")
DEFAULT_REFERENCE_OVERVIEW_ROOT = Path(r"E:\TSIS\data\reference\overview")
DEFAULT_REFERENCE_SPLITS_ROOT = Path(r"E:\TSIS\data\reference\splits")
DEFAULT_RUNS_ROOT = STRATEGY_ROOT / "runs"
DEFAULT_LT1B_UNIVERSE_PATH = Path(
    r"C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest"
    r"\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff"
    r"\market_cap_cutoff_lt_1b_active_inactive.parquet"
)
QUERY_NAME = "gap_and_go_pmh_break"
ET_TZ = "America/New_York"
TRADINGVIEW_EXCHANGE_PREFIX = {
    "XNAS": "NASDAQ",
    "NASDAQ": "NASDAQ",
    "XNYS": "NYSE",
    "NYSE": "NYSE",
    "ARCX": "AMEX",
    "XASE": "AMEX",
    "AMEX": "AMEX",
    "BATS": "BATS",
    "IEXG": "IEX",
    "IEX": "IEX",
}

FIELD_DEFINITIONS = [
    ("1m root", "Carpeta operativa de velas 1m usada para buscar candidatos."),
    ("Reference", "Carpeta de referencia usada para leer exchange, market cap y contexto descriptivo disponible."),
    ("Universe", "Source of truth del universo LT1B que limita los tickers elegibles."),
    ("Tickers", "Lista manual de tickers; vacio significa usar el universo LT1B."),
    ("Years", "Anios a escanear; acepta formatos como 2025 o 2022-2025."),
    ("Gap % >", "Gap minimo frente al prior close para considerar que el mercado repricio el ticker antes de abrir."),
    ("PM Vol >", "Volumen minimo acumulado en premarket."),
    ("Price >", "Precio minimo del PMH para filtrar acciones demasiado bajas."),
    ("MCap <", "Market cap maximo permitido cuando existe dato de referencia."),
    ("No MCap", "Politica cuando falta market cap: include, exclude o flag."),
    ("Break <= min", "Minutos maximos tras la apertura regular para aceptar la ruptura del PMH."),
    ("Break Vol x", "Multiplicador minimo del volumen de la vela de ruptura frente al volumen reciente."),
    ("PMH buf %", "Buffer porcentual por encima del Premarket High para evitar rupturas por toque minimo."),
    ("break close > PMH", "Exige que la vela de ruptura cierre por encima del PMH/buffer, no solo que lo toque con el high."),
    ("require no PMH fail", "Exige que no haya fallo inmediato bajo PMH tras la ruptura."),
    ("Price", "Vista de precio usada para la busqueda: raw o split_normalized."),
    ("Y padding", "Aire visual arriba y abajo del chart."),
    ("Progress", "Cada cuantos archivos escaneados se imprime progreso en terminal."),
    ("Flush hits", "Cada cuantos candidatos nuevos se actualiza candidate_events_partial.csv."),
]


@dataclass(frozen=True)
class GapAndGoConfig:
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
    min_gap_pct: float = 20.0
    min_premarket_volume: float = 500_000.0
    min_price: float = 0.5
    max_market_cap: float | None = 100_000_000.0
    missing_market_cap_policy: str = "include"
    max_minutes_after_open_for_break: int = 30
    min_breakout_volume_ratio: float = 1.5
    pmh_break_buffer_pct: float = 0.0
    require_break_close_above_pmh: bool = True
    require_no_immediate_pmh_failure: bool = False
    immediate_failure_minutes: int = 5
    price_view: str = "raw"
    max_candidates: int | None = None
    progress_every: int = 250
    partial_flush_every: int = 1
    workers: int = 1


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _format_field_definitions_text() -> str:
    return "\n".join(f"{name}: {description}" for name, description in FIELD_DEFINITIONS)


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


def _terminal_command_from_config(config: "GapAndGoConfig", pretty: bool = True) -> str:
    parts = [
        ("--data-root", _ps_quote(config.data_root)),
        ("--reference-overview-root", _ps_quote(config.reference_overview_root)),
        ("--output-root", _ps_quote(config.output_root)),
        ("--universe-path", _ps_quote(config.universe_path)),
        ("--min-gap-pct", str(config.min_gap_pct)),
        ("--min-premarket-volume", str(config.min_premarket_volume)),
        ("--min-price", str(config.min_price)),
        ("--max-market-cap", str(config.max_market_cap)),
        ("--missing-market-cap-policy", config.missing_market_cap_policy),
        ("--max-minutes-after-open-for-break", str(config.max_minutes_after_open_for_break)),
        ("--min-breakout-volume-ratio", str(config.min_breakout_volume_ratio)),
        ("--pmh-break-buffer-pct", str(config.pmh_break_buffer_pct)),
        ("--price-view", config.price_view),
        ("--progress-every", str(config.progress_every)),
        ("--partial-flush-every", str(config.partial_flush_every)),
    ]
    if config.tickers:
        parts.append(("--tickers", _ps_quote(",".join(config.tickers))))
    if config.years:
        parts.append(("--years", _ps_quote(",".join(str(year) for year in config.years))))

    flags = []
    if not config.require_break_close_above_pmh:
        flags.append("--no-require-break-close-above-pmh")
    if config.require_no_immediate_pmh_failure:
        flags.append("--require-no-immediate-pmh-failure")

    if not pretty:
        flat = [
            f"Set-Location {_ps_quote(str(STRATEGY_ROOT))};",
            "python",
            _ps_quote(str(STRATEGY_ROOT / "gap_and_go_widgets.py")),
        ]
        for name, value in parts:
            flat.extend([name, value])
        flat.extend(flags)
        return " ".join(flat)

    lines = [
        f"Set-Location {_ps_quote(str(STRATEGY_ROOT))}",
        f"python {_ps_quote(str(STRATEGY_ROOT / 'gap_and_go_widgets.py'))} `",
    ]
    command_lines = [f"  {name} {value}" for name, value in parts] + [f"  {flag}" for flag in flags]
    for idx, line in enumerate(command_lines):
        suffix = " `" if idx < len(command_lines) - 1 else ""
        lines.append(line + suffix)
    return "\n".join(lines)


def _run_datetime_utc_label(run_id: str) -> str:
    suffix = str(run_id).rsplit("_", 1)[-1]
    try:
        dt = datetime.strptime(suffix, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def _parse_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part.strip().upper() for part in value.split(",") if part.strip())


def _parse_years(value: str | None) -> tuple[int, ...]:
    if not value:
        return ()
    years: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            years.extend(range(int(start), int(end) + 1))
        else:
            years.append(int(part))
    return tuple(sorted(set(years)))


def _session_segment(ts_et: pd.Series) -> pd.Series:
    minutes = ts_et.dt.hour * 60 + ts_et.dt.minute
    out = pd.Series("overnight", index=ts_et.index, dtype="object")
    out[(minutes >= 4 * 60) & (minutes < 9 * 60 + 30)] = "premarket"
    out[(minutes >= 9 * 60 + 30) & (minutes < 16 * 60)] = "regular"
    out[(minutes >= 16 * 60) & (minutes < 20 * 60)] = "afterhours"
    return out


def _read_1m_file(path: Path, price_view: str) -> pd.DataFrame:
    schema_names = set(pq.ParquetFile(path).schema_arrow.names)
    cols = [
        "ticker",
        "ts_utc",
        "date",
        "o",
        "h",
        "l",
        "c",
        "v",
        "vw",
        "o_split_normalized",
        "h_split_normalized",
        "l_split_normalized",
        "c_split_normalized",
        "vw_split_normalized",
    ]
    table = pq.ParquetFile(path).read(columns=[c for c in cols if c in schema_names])
    df = table.to_pandas()
    if df.empty:
        return df

    if price_view == "split_normalized":
        required = {
            "o_split_normalized",
            "h_split_normalized",
            "l_split_normalized",
            "c_split_normalized",
        }
        if not required.issubset(df.columns):
            raise ValueError(f"{path} lacks split-normalized price columns")
        df["px_o"] = df["o_split_normalized"]
        df["px_h"] = df["h_split_normalized"]
        df["px_l"] = df["l_split_normalized"]
        df["px_c"] = df["c_split_normalized"]
    elif price_view == "raw":
        df["px_o"] = df["o"]
        df["px_h"] = df["h"]
        df["px_l"] = df["l"]
        df["px_c"] = df["c"]
    else:
        raise ValueError(f"Unsupported price_view: {price_view}")

    df["ts_utc_dt"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce", format="ISO8601")
    df = df.dropna(subset=["ts_utc_dt", "px_o", "px_h", "px_l", "px_c", "v"]).copy()
    df["ts_et"] = df["ts_utc_dt"].dt.tz_convert(ET_TZ)
    df["ts_et_naive"] = df["ts_et"].dt.tz_localize(None)
    df["session_date"] = df["ts_et"].dt.date.astype(str)
    df["session_segment"] = _session_segment(df["ts_et"])
    return df.sort_values("ts_utc_dt").reset_index(drop=True)


def load_lt1b_universe(universe_path: Path) -> pd.DataFrame:
    required = {"ticker", "first_seen_date", "last_observed_date", "classification_1b"}
    schema_names = set(pq.ParquetFile(universe_path).schema_arrow.names)
    missing = required - schema_names
    if missing:
        raise ValueError(f"{universe_path} lacks required universe columns: {sorted(missing)}")
    df = pq.ParquetFile(universe_path).read(columns=sorted(required)).to_pandas()
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["first_seen_date"] = pd.to_datetime(df["first_seen_date"], errors="coerce")
    df["last_observed_date"] = pd.to_datetime(df["last_observed_date"], errors="coerce")
    df = df.dropna(subset=["ticker", "first_seen_date", "last_observed_date"])
    allowed = {"active_lt_1b_last_classifiable", "inactive_died_lt_1b"}
    df = df[df["classification_1b"].isin(allowed)].copy()
    return df.drop_duplicates(subset=["ticker"], keep="last").set_index("ticker", drop=False).sort_index()


def _iter_parquet_files(
    data_root: Path,
    tickers: Iterable[str],
    years: Iterable[int],
    universe: pd.DataFrame | None,
) -> list[Path]:
    requested_tickers = {t.upper() for t in tickers}
    ticker_filter = set(requested_tickers)
    year_filter = {int(y) for y in years}
    if universe is not None:
        universe_tickers = set(universe.index.astype(str))
        ticker_filter = requested_tickers & universe_tickers if requested_tickers else universe_tickers
        if not ticker_filter:
            return []

    files: list[Path] = []
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
            if year_filter and year not in year_filter:
                continue
            if universe is not None:
                row = universe.loc[ticker]
                if year < int(row["first_seen_date"].year) or year > int(row["last_observed_date"].year):
                    continue
            files.extend(sorted(year_dir.glob("month=*/*.parquet")))
    return files


def _load_market_cap_history(overview_root: Path, ticker: str) -> pd.DataFrame:
    ticker_dir = overview_root / f"ticker={ticker.upper()}"
    rows: list[pd.DataFrame] = []
    for path in sorted(ticker_dir.glob("*.parquet")):
        schema_names = set(pq.ParquetFile(path).schema_arrow.names)
        if "request_date" not in schema_names:
            continue
        cols = [
            c
            for c in ["ticker", "market_cap", "request_date", "market", "primary_exchange", "name"]
            if c in schema_names
        ]
        df = pq.ParquetFile(path).read(columns=cols).to_pandas()
        if not df.empty:
            rows.append(df)
    if not rows:
        return pd.DataFrame(columns=["ticker", "market_cap", "request_date", "primary_exchange", "name"])
    hist = pd.concat(rows, ignore_index=True)
    hist["request_date"] = pd.to_datetime(hist["request_date"], errors="coerce")
    return hist.dropna(subset=["request_date"]).sort_values("request_date").reset_index(drop=True)


def _market_cap_asof(hist: pd.DataFrame, event_date: str) -> tuple[float | None, str | None]:
    if hist.empty or "market_cap" not in hist.columns:
        return None, None
    event_ts = pd.Timestamp(event_date)
    eligible = hist[hist["request_date"] <= event_ts]
    if eligible.empty:
        eligible = hist
    row = eligible.iloc[-1]
    cap = pd.to_numeric(pd.Series([row.get("market_cap")]), errors="coerce").iloc[0]
    cap_date = row.get("request_date")
    return (float(cap) if pd.notna(cap) else None, str(cap_date.date()) if pd.notna(cap_date) else None)


def _reference_asof(hist: pd.DataFrame) -> dict:
    if hist.empty:
        return {}
    row = hist.iloc[-1].to_dict()
    return {k: v for k, v in row.items() if pd.notna(v)}


def _tradingview_symbol(ticker: str, primary_exchange: str | None) -> str:
    exchange = str(primary_exchange or "").strip().upper()
    prefix = TRADINGVIEW_EXCHANGE_PREFIX.get(exchange)
    return f"{prefix}:{ticker.upper()}" if prefix else ticker.upper()


def _compute_vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df["px_h"] + df["px_l"] + df["px_c"]) / 3.0
    pv = typical * df["v"].astype(float)
    cum_vol = df["v"].astype(float).cumsum().replace(0, pd.NA)
    return pv.cumsum() / cum_vol


def _gap_and_go_rows_for_session(session_df: pd.DataFrame, prior_close: float, config: GapAndGoConfig) -> list[dict]:
    pre = session_df[session_df["session_segment"].eq("premarket")].copy()
    regular = session_df[session_df["session_segment"].eq("regular")].copy()
    if pre.empty or regular.empty or prior_close <= 0:
        return []

    pm_volume = float(pre["v"].sum())
    if pm_volume < config.min_premarket_volume:
        return []

    regular_open = float(regular.iloc[0]["px_o"])
    pm_last = float(pre.iloc[-1]["px_c"])
    gap_pct = max((regular_open - prior_close) / prior_close * 100.0, (pm_last - prior_close) / prior_close * 100.0)
    if gap_pct < config.min_gap_pct:
        return []

    pmh_idx = pre["px_h"].astype(float).idxmax()
    pmh_row = pre.loc[pmh_idx]
    pmh = float(pmh_row["px_h"])
    if pmh < config.min_price:
        return []

    open_ts = regular.iloc[0]["ts_et"]
    deadline = open_ts + pd.Timedelta(minutes=config.max_minutes_after_open_for_break)
    early = regular[regular["ts_et"] <= deadline].copy()
    if early.empty:
        return []

    break_level = pmh * (1.0 + config.pmh_break_buffer_pct / 100.0)
    breaks = early[early["px_h"] >= break_level].copy()
    if config.require_break_close_above_pmh:
        breaks = breaks[breaks["px_c"] >= break_level]
    if breaks.empty:
        return []

    break_row = breaks.iloc[0]
    break_pos = int(session_df.index.get_loc(break_row.name))
    before = session_df.iloc[max(0, break_pos - 10) : break_pos]
    volume_baseline = float(before["v"].tail(10).mean()) if not before.empty else 0.0
    if volume_baseline <= 0:
        volume_baseline = float(pre["v"].tail(20).mean()) if not pre.empty else 0.0
    breakout_volume_ratio = float(break_row["v"]) / volume_baseline if volume_baseline > 0 else float("nan")
    if pd.isna(breakout_volume_ratio) or breakout_volume_ratio < config.min_breakout_volume_ratio:
        return []

    failure_end = break_row["ts_et"] + pd.Timedelta(minutes=config.immediate_failure_minutes)
    after_break = regular[(regular["ts_et"] > break_row["ts_et"]) & (regular["ts_et"] <= failure_end)]
    immediate_failure = bool((after_break["px_c"] < pmh).any()) if not after_break.empty else False
    if config.require_no_immediate_pmh_failure and immediate_failure:
        return []

    hold_minutes = 0
    for row in after_break.itertuples(index=False):
        if float(row.px_c) >= pmh:
            hold_minutes += 1
        else:
            break

    session_for_vwap = session_df[session_df["session_segment"].isin(["premarket", "regular"])].copy()
    session_for_vwap["vwap"] = _compute_vwap(session_for_vwap)
    vwap_at_break = session_for_vwap.loc[break_row.name, "vwap"] if break_row.name in session_for_vwap.index else pd.NA

    event_ts_et = break_row["ts_et"]
    return [
        {
            "candidate_id": f"{QUERY_NAME}:{break_row['ticker']}:{break_row['ts_utc_dt'].isoformat()}",
            "strategy_id": "gap_and_go",
            "ticker": str(break_row["ticker"]).upper(),
            "session_date": str(break_row["session_date"]),
            "prior_close": float(prior_close),
            "regular_open": regular_open,
            "pm_last": pm_last,
            "gap_pct": round(float(gap_pct), 4),
            "pm_volume": pm_volume,
            "pmh": pmh,
            "pmh_ts_utc": pmh_row["ts_utc_dt"].isoformat(),
            "pmh_ts_et": pmh_row["ts_et"].strftime("%Y-%m-%d %H:%M:%S %Z"),
            "break_ts_utc": break_row["ts_utc_dt"].isoformat(),
            "break_ts_et": event_ts_et.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "minutes_after_open": round((event_ts_et - open_ts).total_seconds() / 60.0, 2),
            "break_open": float(break_row["px_o"]),
            "break_high": float(break_row["px_h"]),
            "break_low": float(break_row["px_l"]),
            "break_close": float(break_row["px_c"]),
            "break_volume": float(break_row["v"]),
            "breakout_volume_ratio": round(float(breakout_volume_ratio), 4),
            "vwap_at_break": float(vwap_at_break) if pd.notna(vwap_at_break) else None,
            "break_close_above_vwap": bool(float(break_row["px_c"]) >= float(vwap_at_break))
            if pd.notna(vwap_at_break)
            else None,
            "immediate_pmh_failure": immediate_failure,
            "pmh_hold_minutes_after_break": int(hold_minutes),
            "event_quality_state": "review_event" if immediate_failure else "candidate_event",
        }
    ]


def _candidate_rows_for_file(path: Path, config: GapAndGoConfig, start_date: str | None, end_date: str | None) -> list[dict]:
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
        if len(prior_dates) == 0:
            continue
        prior_close = float(regular_closes.loc[prior_dates[-1]])
        rows.extend(_gap_and_go_rows_for_session(session_df.sort_values("ts_utc_dt"), prior_close, config))
    return rows


def _postprocess_candidates(candidates: list[dict], config: GapAndGoConfig) -> pd.DataFrame:
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


def _sort_candidates_for_review(candidates: pd.DataFrame, mode: str = "gap_pct_desc") -> pd.DataFrame:
    if candidates.empty:
        return candidates

    out = candidates.copy()
    if "ticker" in out.columns:
        out["ticker"] = out["ticker"].astype(str).str.strip().str.upper()
    for col in ["gap_pct", "breakout_volume_ratio", "pm_volume"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    ticker_col = "ticker" if "ticker" in out.columns else None
    if ticker_col and "gap_pct" in out.columns:
        out["_ticker_max_gap_pct_sort"] = out.groupby(ticker_col)["gap_pct"].transform("max")
    elif "gap_pct" in out.columns:
        out["_ticker_max_gap_pct_sort"] = out["gap_pct"]
    else:
        out["_ticker_max_gap_pct_sort"] = 0.0

    if "break_ts_utc" in out.columns:
        out["_event_ts_sort"] = pd.to_datetime(out["break_ts_utc"], utc=True, errors="coerce")
    elif "session_date" in out.columns:
        out["_event_ts_sort"] = pd.to_datetime(out["session_date"], errors="coerce")
    else:
        out["_event_ts_sort"] = pd.NaT

    if mode == "ticker_grouped":
        sort_cols = ["_ticker_max_gap_pct_sort"]
        ascending = [False]
        if ticker_col:
            sort_cols.append(ticker_col)
            ascending.append(True)
        sort_cols.extend(["_event_ts_sort", "gap_pct", "breakout_volume_ratio", "pm_volume"])
        ascending.extend([True, False, False, False])
    else:
        sort_cols = ["gap_pct", "breakout_volume_ratio", "pm_volume"]
        ascending = [False, False, False]
        if ticker_col:
            sort_cols.append(ticker_col)
            ascending.append(True)
        sort_cols.append("_event_ts_sort")
        ascending.append(True)

    sort_cols = [col for col in sort_cols if col in out.columns]
    ascending = ascending[: len(sort_cols)]

    out = out.sort_values(sort_cols, ascending=ascending, na_position="last").reset_index(drop=True)
    return out.drop(columns=[c for c in ["_ticker_max_gap_pct_sort", "_event_ts_sort"] if c in out.columns])


def _write_manifest(
    run_dir: Path,
    config: GapAndGoConfig,
    run_status: str,
    files_scanned: int,
    total_files: int,
    raw_candidate_count: int,
    candidate_count: int,
    partial_output: str | None = None,
    error: str | None = None,
) -> None:
    command_pretty = _terminal_command_from_config(config, pretty=True)
    command_flat = _terminal_command_from_config(config, pretty=False)
    manifest = {
        "run_id": run_dir.name,
        "run_datetime_utc": _run_datetime_utc_label(run_dir.name),
        "query_name": config.query_name,
        "strategy_id": "gap_and_go",
        "run_status": run_status,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files_scanned": int(files_scanned),
        "total_files": int(total_files),
        "raw_candidate_count": int(raw_candidate_count),
        "candidate_count": int(candidate_count),
        "partial_output": partial_output,
        "error": error,
        "terminal_launcher": command_flat,
        "terminal_launcher_pretty": command_pretty,
        "run_metadata_markdown": "RUN_METADATA.md",
        "terminal_launcher_file": "terminal_launcher.ps1",
        "config": asdict(config),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (run_dir / "terminal_launcher.ps1").write_text(command_pretty + "\n", encoding="utf-8")
    _write_run_metadata(run_dir, manifest)


def _write_run_metadata(run_dir: Path, manifest: dict) -> None:
    config = manifest.get("config", {})
    lines = [
        "# Gap and Go Run Metadata",
        "",
        "## Run",
        "",
        f"- run_id: `{manifest.get('run_id')}`",
        f"- run_datetime_utc: `{manifest.get('run_datetime_utc')}`",
        f"- query_name: `{manifest.get('query_name')}`",
        f"- strategy_id: `{manifest.get('strategy_id')}`",
        f"- status: `{manifest.get('run_status')}`",
        f"- updated_at_utc: `{manifest.get('updated_at_utc')}`",
        f"- files_scanned: `{manifest.get('files_scanned')}/{manifest.get('total_files')}`",
        f"- raw_candidate_count: `{manifest.get('raw_candidate_count')}`",
        f"- candidate_count: `{manifest.get('candidate_count')}`",
        f"- partial_output: `{manifest.get('partial_output')}`",
        f"- error: `{manifest.get('error')}`",
        "",
        "## Terminal Launcher",
        "",
        "```powershell",
        manifest.get("terminal_launcher_pretty", ""),
        "```",
        "",
        "## Field Definitions",
        "",
    ]
    lines.extend(f"- `{name}`: {description}" for name, description in FIELD_DEFINITIONS)
    lines.extend(
        [
            "",
            "## Config",
            "",
            "```json",
            json.dumps(config, indent=2),
            "```",
            "",
            "## Outputs",
            "",
            "- `candidate_events_partial.csv`: candidatos parciales durante el run.",
            "- `candidate_events.csv`: candidatos finales en CSV.",
            "- `candidate_events.parquet`: candidatos finales en Parquet cuando existen filas.",
            "- `manifest.json`: metadata estructurada del run.",
            "- `terminal_launcher.ps1`: lanzadera PowerShell usada para reproducir el run.",
        ]
    )
    (run_dir / "RUN_METADATA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_run_dir(config: GapAndGoConfig) -> Path:
    run_id = f"{config.query_name}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = Path(config.output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "query_config.json").write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
    _write_manifest(run_dir, config, "created", 0, 0, 0, 0)
    return run_dir


def _flush_partial(run_dir: Path, candidates: list[dict], config: GapAndGoConfig, files_scanned: int, total_files: int) -> None:
    partial = pd.DataFrame(candidates)
    partial_path = run_dir / "candidate_events_partial.csv"
    if not partial.empty:
        partial = partial.sort_values(["gap_pct", "breakout_volume_ratio"], ascending=[False, False])
        partial.to_csv(partial_path, index=False)
    else:
        pd.DataFrame().to_csv(partial_path, index=False)
    _write_manifest(
        run_dir,
        config,
        "running",
        files_scanned,
        total_files,
        len(candidates),
        len(partial),
        partial_output=partial_path.name,
    )


def find_gap_and_go_candidates(config: GapAndGoConfig, run_dir: Path | None = None) -> pd.DataFrame:
    data_root = Path(config.data_root)
    universe = load_lt1b_universe(Path(config.universe_path)) if config.use_lt1b_universe else None
    files = _iter_parquet_files(data_root, config.tickers, config.years, universe)
    print(f"files_to_scan={len(files)}", flush=True)
    if run_dir is not None:
        _write_manifest(run_dir, config, "running", 0, len(files), 0, 0)

    raw_candidates: list[dict] = []
    last_flush_count = 0
    for idx, path in enumerate(files, start=1):
        raw_candidates.extend(_candidate_rows_for_file(path, config, config.start_date, config.end_date))
        if config.max_candidates is not None and len(raw_candidates) >= config.max_candidates:
            raw_candidates = raw_candidates[: config.max_candidates]
        new_hits = len(raw_candidates) - last_flush_count
        should_flush = run_dir is not None and config.partial_flush_every > 0 and new_hits >= config.partial_flush_every
        should_progress = config.progress_every > 0 and (idx == 1 or idx % config.progress_every == 0)
        if should_progress:
            print(
                f"progress files_scanned={idx}/{len(files)} raw_candidates={len(raw_candidates)} current={path}",
                flush=True,
            )
        if should_flush or (should_progress and run_dir is not None):
            _flush_partial(run_dir, raw_candidates, config, idx, len(files))
            last_flush_count = len(raw_candidates)
        if config.max_candidates is not None and len(raw_candidates) >= config.max_candidates:
            break

    if run_dir is not None:
        _flush_partial(run_dir, raw_candidates, config, min(len(files), idx if files else 0), len(files))
    return _postprocess_candidates(raw_candidates, config)


def finalize_run(run_dir: Path, candidates: pd.DataFrame, config: GapAndGoConfig) -> None:
    if not candidates.empty:
        candidates.to_parquet(run_dir / "candidate_events.parquet", index=False)
        candidates.to_csv(run_dir / "candidate_events.csv", index=False)
    else:
        pd.DataFrame().to_csv(run_dir / "candidate_events.csv", index=False)
    _write_manifest(
        run_dir,
        config,
        "completed",
        _read_manifest(run_dir).get("files_scanned", 0),
        _read_manifest(run_dir).get("total_files", 0),
        _read_manifest(run_dir).get("raw_candidate_count", len(candidates)),
        len(candidates),
        partial_output="candidate_events_partial.csv",
    )


def _read_manifest(run_dir: Path) -> dict:
    path = run_dir / "manifest.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


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


def _months_between(start: pd.Timestamp, end: pd.Timestamp) -> list[tuple[int, int]]:
    periods = pd.period_range(start=start.to_period("M"), end=end.to_period("M"), freq="M")
    return [(int(p.year), int(p.month)) for p in periods]


def _file_for_month(data_root: Path, ticker: str, year: int, month: int) -> Path:
    return (
        data_root
        / f"ticker={ticker.upper()}"
        / f"year={year}"
        / f"month={month:02d}"
        / f"minute_aggs_{ticker.upper()}_{year}_{month:02d}.parquet"
    )


def load_split_events_for_chart(
    ticker: str,
    start_session_date: str,
    end_session_date: str,
    splits_root: Path = DEFAULT_REFERENCE_SPLITS_ROOT,
) -> pd.DataFrame:
    path = splits_root / f"ticker={ticker.upper()}" / f"splits_{ticker.upper()}.parquet"
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pq.ParquetFile(path).read().to_pandas()
    except Exception:
        return pd.DataFrame()
    if df.empty or "execution_date" not in df.columns:
        return pd.DataFrame()

    df["execution_date"] = pd.to_datetime(df["execution_date"], errors="coerce").dt.date.astype(str)
    df = df[(df["execution_date"] >= str(start_session_date)) & (df["execution_date"] <= str(end_session_date))].copy()
    if df.empty:
        return df

    df["split_from"] = pd.to_numeric(df.get("split_from"), errors="coerce")
    df["split_to"] = pd.to_numeric(df.get("split_to"), errors="coerce")
    df["split_type"] = [
        "reverse_split" if pd.notna(frm) and pd.notna(to) and frm > to else "split"
        for frm, to in zip(df["split_from"], df["split_to"])
    ]
    df["split_label"] = [
        f"{kind} {frm:g}:{to:g}" if pd.notna(frm) and pd.notna(to) else kind
        for kind, frm, to in zip(df["split_type"], df["split_from"], df["split_to"])
    ]
    return df


def _safe_filename(value: str) -> str:
    safe = []
    for char in str(value):
        if char.isalnum() or char in {"-", "_", "."}:
            safe.append(char)
        else:
            safe.append("_")
    return "".join(safe).strip("_")[:180] or "candidate"


def load_chart_window(
    ticker: str,
    break_ts_utc: str,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    days_before: int = 3,
    days_after: int = 3,
    price_view: str = "raw",
) -> pd.DataFrame:
    data_root = Path(data_root)
    break_ts = pd.Timestamp(break_ts_utc)
    break_ts = break_ts.tz_localize("UTC") if break_ts.tzinfo is None else break_ts.tz_convert("UTC")
    start = break_ts - pd.Timedelta(days=days_before)
    end = break_ts + pd.Timedelta(days=days_after)
    frames: list[pd.DataFrame] = []
    for year, month in _months_between(start.tz_localize(None), end.tz_localize(None)):
        path = _file_for_month(data_root, ticker, year, month)
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
            df.loc[session.index[eligible], "vwap"] = _compute_vwap(session.loc[eligible]).to_numpy()
    df["vwap"] = pd.to_numeric(df["vwap"], errors="coerce")
    return df.reset_index(drop=True)


def make_gap_and_go_chart(
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
) -> go.Figure:
    if df.empty:
        raise ValueError("No rows available for chart window.")

    chart_df = df.copy().reset_index(drop=True)
    chart_df["bar_index"] = chart_df.index
    chart_df["hover_time"] = chart_df["ts_et"].dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    chart_df["hover_time_utc"] = chart_df["ts_utc_dt"].dt.strftime("%Y-%m-%d %H:%M UTC")
    chart_df["volume_color"] = [
        "rgba(16,185,129,0.75)" if c >= o else "rgba(239,68,68,0.75)"
        for o, c in zip(chart_df["px_o"], chart_df["px_c"])
    ]
    x_values = chart_df["bar_index"] if compact_xaxis else chart_df["ts_et_naive"]

    break_ts = pd.Timestamp(candidate["break_ts_utc"])
    break_ts = break_ts.tz_localize("UTC") if break_ts.tzinfo is None else break_ts.tz_convert("UTC")
    break_positions = chart_df[chart_df["ts_utc_dt"].eq(break_ts)]["bar_index"]
    if break_positions.empty:
        nearest_idx = (chart_df["ts_utc_dt"] - break_ts).abs().idxmin()
        break_x = int(chart_df.loc[nearest_idx, "bar_index"])
    else:
        break_x = int(break_positions.iloc[0])
    pmh = float(candidate["pmh"])
    prior_close = float(candidate["prior_close"]) if pd.notna(candidate.get("prior_close")) else None
    regular_open = float(candidate["regular_open"]) if pd.notna(candidate.get("regular_open")) else None

    pmh_ts = pd.Timestamp(candidate["pmh_ts_utc"]) if candidate.get("pmh_ts_utc") else pd.NaT
    if pd.notna(pmh_ts):
        pmh_ts = pmh_ts.tz_localize("UTC") if pmh_ts.tzinfo is None else pmh_ts.tz_convert("UTC")
        pmh_x = int(chart_df.loc[(chart_df["ts_utc_dt"] - pmh_ts).abs().idxmin(), "bar_index"])
    else:
        pmh_x = break_x

    session_date = str(candidate.get("session_date", ""))
    regular_rows = chart_df[chart_df["session_date"].eq(session_date) & chart_df["session_segment"].eq("regular")]
    open_x = int(regular_rows.iloc[0]["bar_index"]) if not regular_rows.empty else break_x

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.02,
    )
    fig.add_trace(
        go.Candlestick(
            x=x_values,
            open=chart_df["px_o"],
            high=chart_df["px_h"],
            low=chart_df["px_l"],
            close=chart_df["px_c"],
            increasing_line_color="rgb(16,185,129)",
            decreasing_line_color="rgb(239,68,68)",
            increasing_fillcolor="rgba(16,185,129,0.65)",
            decreasing_fillcolor="rgba(239,68,68,0.65)",
            hoverinfo="skip",
            name="1m candles",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=chart_df["vwap"],
            mode="lines",
            line=dict(color="rgb(37,99,235)", width=1.4),
            name="VWAP",
            hoverinfo="skip",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=x_values,
            y=chart_df["v"],
            marker_color=chart_df["volume_color"],
            name="1m volume",
            customdata=chart_df[
                ["hover_time", "hover_time_utc", "session_segment", "px_o", "px_h", "px_l", "px_c", "v", "vwap"]
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "UTC: %{customdata[1]}<br>"
                "Session: %{customdata[2]}<br>"
                "Open: %{customdata[3]:.4f}<br>"
                "High: %{customdata[4]:.4f}<br>"
                "Low: %{customdata[5]:.4f}<br>"
                "Close: %{customdata[6]:.4f}<br>"
                "Volume: %{customdata[7]:,.0f}<br>"
                "VWAP: %{customdata[8]:.4f}"
                "<extra></extra>"
            ),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=chart_df["px_c"],
            mode="markers",
            marker=dict(size=14, color="rgba(0,0,0,0.01)", line=dict(width=0)),
            customdata=chart_df[
                ["hover_time", "hover_time_utc", "session_segment", "px_o", "px_h", "px_l", "px_c", "v", "vwap"]
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "UTC: %{customdata[1]}<br>"
                "Session: %{customdata[2]}<br>"
                "Open: %{customdata[3]:.4f}<br>"
                "High: %{customdata[4]:.4f}<br>"
                "Low: %{customdata[5]:.4f}<br>"
                "Close: %{customdata[6]:.4f}<br>"
                "Volume: %{customdata[7]:,.0f}<br>"
                "VWAP: %{customdata[8]:.4f}"
                "<extra></extra>"
            ),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    _add_compact_session_backgrounds(fig, chart_df)
    if prior_close is not None:
        fig.add_hline(
            y=prior_close,
            line=dict(color="rgba(75,85,99,0.65)", width=1, dash="dot"),
            annotation_text="prior close",
            annotation_position="bottom right",
            row=1,
            col=1,
        )
    fig.add_hline(
        y=pmh,
        line=dict(color="rgba(220,38,38,0.95)", width=1.5, dash="dash"),
        annotation_text="PMH",
        annotation_position="top right",
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=[break_x],
            y=[pmh],
            mode="markers",
            marker=dict(size=28, color="rgba(37,99,235,0.24)", line=dict(color="rgba(37,99,235,0.95)", width=2)),
            name="Gap and Go trigger",
            hovertemplate="Gap and Go trigger<br>PMH break: %{y:.4f}<extra></extra>",
        ),
        row=1,
        col=1,
    )

    if prior_close is not None:
        if regular_open is not None:
            official_gap = (regular_open - prior_close) / prior_close * 100.0 if prior_close else float("nan")
            fig.add_trace(
                go.Scatter(
                    x=[open_x, open_x],
                    y=[prior_close, regular_open],
                    mode="lines",
                    line=dict(color="rgba(17,24,39,0.55)", width=1),
                    name="official open gap",
                    hoverinfo="skip",
                    showlegend=False,
                ),
                row=1,
                col=1,
            )
            fig.add_annotation(
                x=open_x,
                y=(prior_close + regular_open) / 2.0,
                text=f"{official_gap:+.1f}%",
                showarrow=False,
                xanchor="left",
                yanchor="middle",
                font=dict(size=12, color="rgba(17,24,39,0.85)"),
                bgcolor="rgba(255,255,255,0.65)",
                row=1,
                col=1,
            )
        pmh_gap = (pmh - prior_close) / prior_close * 100.0 if prior_close else float("nan")
        fig.add_trace(
            go.Scatter(
                x=[pmh_x, pmh_x],
                y=[prior_close, pmh],
                mode="lines",
                line=dict(color="rgba(37,99,235,0.55)", width=1),
                name="premarket high gap",
                hoverinfo="skip",
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig.add_annotation(
            x=pmh_x,
            y=(prior_close + pmh) / 2.0,
            text=f"{pmh_gap:+.1f}%",
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(size=12, color="rgba(37,99,235,0.9)"),
            bgcolor="rgba(255,255,255,0.65)",
            row=1,
            col=1,
        )

    if split_events is not None and not split_events.empty:
        for split in split_events.itertuples(index=False):
            split_rows = chart_df[chart_df["session_date"].eq(str(split.execution_date))]
            if split_rows.empty:
                continue
            split_x = int(split_rows.iloc[0]["bar_index"])
            fig.add_vline(
                x=split_x,
                line=dict(color="rgba(126,34,206,0.9)", width=1, dash="dot"),
                annotation_text=str(split.split_label),
                annotation_position="top",
                row=1,
                col=1,
            )

    low = float(chart_df["px_l"].min())
    high = float(chart_df["px_h"].max())
    span = max(high - low, high * 0.05, 0.01)
    effective_padding = y_padding_override_pct if y_padding_override_pct is not None else y_padding_pct
    pad = span * effective_padding
    symbol = candidate.get("tradingview_symbol") or candidate.get("ticker", "")
    title = (
        f"{symbol} Gap and Go candidate | {chart_label} | gap={candidate.get('gap_pct')}% "
        f"PMH={pmh:.4f} break={candidate.get('break_ts_et')}"
    )
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=height,
        hovermode="closest",
        hoverdistance=-1,
        spikedistance=-1,
        dragmode=False if static_axes else "pan",
        xaxis_rangeslider_visible=show_rangeslider,
        margin=dict(l=35, r=75, t=60, b=35),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    spike_style = dict(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="dot",
        spikecolor="rgba(20,20,20,0.7)",
        spikethickness=1,
    )
    fig.update_yaxes(range=[low - pad, high + pad], side="right", fixedrange=static_axes, row=1, col=1, **spike_style)
    fig.update_yaxes(title_text="Volume", side="right", fixedrange=static_axes, row=2, col=1, **spike_style)
    tick_step = max(len(chart_df) // 12, 1)
    tick_positions = chart_df["bar_index"].iloc[::tick_step].tolist()
    tick_labels = chart_df["ts_et"].iloc[::tick_step].dt.strftime("%b %d<br>%H:%M %Z").tolist()
    fig.update_xaxes(
        type="linear",
        rangeslider_thickness=0.05,
        rangeslider_visible=show_rangeslider,
        tickmode="array",
        tickvals=tick_positions,
        ticktext=tick_labels,
        title_text="New York time, observed 1m bars (non-trading gaps compressed)",
        row=2,
        col=1,
        **spike_style,
    )
    fig.update_xaxes(fixedrange=static_axes, showticklabels=False, rangeslider_visible=False, row=1, col=1, **spike_style)
    fig.update_xaxes(fixedrange=static_axes, row=2, col=1, **spike_style)
    return fig


def _add_compact_session_backgrounds(fig: go.Figure, df: pd.DataFrame) -> None:
    grouped = (
        df[df["session_segment"].isin(["premarket", "afterhours"])]
        .groupby(["session_segment", df["ts_et_naive"].dt.date], sort=True)["bar_index"]
        .agg(["min", "max"])
        .reset_index()
    )
    colors = {"premarket": "rgba(255,174,66,0.25)", "afterhours": "rgba(90,140,255,0.16)"}
    for row in grouped.itertuples(index=False):
        for panel_row in [1, 2]:
            fig.add_vrect(
                x0=int(row.min),
                x1=int(row.max) + 1,
                fillcolor=colors.get(row.session_segment, "rgba(0,0,0,0)"),
                line_width=0,
                layer="below",
                row=panel_row,
                col=1,
            )


def _detail_window_until_hour(df: pd.DataFrame, candidate: dict, end_hour_ny: int) -> pd.DataFrame:
    if df.empty:
        return df

    session_date = str(candidate.get("session_date", ""))
    event_rows = df[df["session_date"].eq(session_date)]
    if event_rows.empty:
        return df

    event_midnight = event_rows["ts_et"].iloc[0].normalize()
    end_et = event_midnight + pd.Timedelta(hours=end_hour_ny)

    prior_dates = sorted(date for date in df["session_date"].dropna().unique().tolist() if str(date) < session_date)
    if prior_dates:
        prior_rows = df[df["session_date"].eq(prior_dates[-1])]
        prior_midnight = prior_rows["ts_et"].iloc[0].normalize()
        start_et = prior_midnight + pd.Timedelta(hours=15)
    else:
        start_et = event_midnight + pd.Timedelta(hours=4)

    detail = df[(df["ts_et"] >= start_et) & (df["ts_et"] <= end_et)].copy()
    return detail if not detail.empty else event_rows.copy()


def _detail_window_until_noon(df: pd.DataFrame, candidate: dict) -> pd.DataFrame:
    return _detail_window_until_hour(df, candidate, 12)


def _detail_window_until_regular_close(df: pd.DataFrame, candidate: dict) -> pd.DataFrame:
    return _detail_window_until_hour(df, candidate, 16)


def render_candidate(candidate: dict, data_root: str, price_view: str, y_padding_pct: float) -> go.Figure:
    df = load_chart_window(candidate["ticker"], candidate["break_ts_utc"], data_root, price_view=price_view)
    split_events = load_split_events_for_chart(
        candidate["ticker"],
        str(df["session_date"].min()) if not df.empty else str(candidate.get("session_date", "")),
        str(df["session_date"].max()) if not df.empty else str(candidate.get("session_date", "")),
    )
    return make_gap_and_go_chart(
        df,
        candidate,
        y_padding_pct=y_padding_pct,
        chart_label="interactive 3-day window",
        show_rangeslider=True,
        height=900,
        static_axes=False,
        split_events=split_events,
    )


def render_candidate_charts(
    candidate: dict,
    data_root: str,
    price_view: str,
    y_padding_pct: float,
) -> list[tuple[str, go.Figure]]:
    df = load_chart_window(candidate["ticker"], candidate["break_ts_utc"], data_root, price_view=price_view)
    detail_until_close_df = _detail_window_until_regular_close(df, candidate)
    split_events = load_split_events_for_chart(
        candidate["ticker"],
        str(df["session_date"].min()) if not df.empty else str(candidate.get("session_date", "")),
        str(df["session_date"].max()) if not df.empty else str(candidate.get("session_date", "")),
    )
    return [
        (
            "1. Interactive 3-day chart",
            make_gap_and_go_chart(
                df,
                candidate,
                y_padding_pct=y_padding_pct,
                chart_label="interactive 3-day window",
                show_rangeslider=True,
                height=900,
                static_axes=False,
                y_padding_override_pct=None,
                split_events=split_events,
            ),
        ),
        (
            "2. Three-day overview",
            make_gap_and_go_chart(
                df,
                candidate,
                y_padding_pct=y_padding_pct,
                chart_label="3-day overview",
                show_rangeslider=False,
                height=780,
                static_axes=True,
                y_padding_override_pct=0.03,
                split_events=split_events,
            ),
        ),
        (
            "3. Event-day detail until 16:00 NY",
            make_gap_and_go_chart(
                detail_until_close_df,
                candidate,
                y_padding_pct=y_padding_pct,
                chart_label="detail until 16:00 NY",
                show_rangeslider=False,
                height=780,
                static_axes=True,
                y_padding_override_pct=0.03,
                split_events=split_events,
            ),
        ),
    ]


def render_candidate_detail_chart(candidate: dict, data_root: str, price_view: str, y_padding_pct: float) -> go.Figure:
    df = load_chart_window(candidate["ticker"], candidate["break_ts_utc"], data_root, price_view=price_view)
    detail_df = _detail_window_until_regular_close(df, candidate)
    split_events = load_split_events_for_chart(
        candidate["ticker"],
        str(df["session_date"].min()) if not df.empty else str(candidate.get("session_date", "")),
        str(df["session_date"].max()) if not df.empty else str(candidate.get("session_date", "")),
    )
    return make_gap_and_go_chart(
        detail_df,
        candidate,
        y_padding_pct=y_padding_pct,
        chart_label="detail until 16:00 NY",
        show_rangeslider=False,
        height=780,
        static_axes=True,
        y_padding_override_pct=0.03,
        split_events=split_events,
    )


def export_candidate_chart_images(
    candidate: dict,
    data_root: str,
    price_view: str,
    y_padding_pct: float,
    output_root: Path,
    width: int = 1800,
    height: int = 950,
    scale: int = 2,
) -> list[Path]:
    charts = render_candidate_charts(candidate, data_root, price_view, y_padding_pct)
    candidate_key = _safe_filename(
        f"{candidate.get('ticker')}_{candidate.get('session_date')}_{candidate.get('candidate_id')}"
    )
    out_dir = output_root / "chart_exports" / candidate_key
    out_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for idx, (title, fig) in enumerate(charts, start=1):
        name = _safe_filename(title.lower().replace(" ", "_"))
        path = out_dir / f"{idx:02d}_{name}.png"
        try:
            fig.write_image(str(path), width=width, height=height, scale=scale)
        except Exception as exc:
            raise RuntimeError(
                "Could not export PNG. Plotly image export requires the `kaleido` package in the active kernel."
            ) from exc
        paths.append(path)
    return paths


def _ensure_plotly_png_export_available() -> None:
    try:
        import kaleido  # noqa: F401
    except Exception as exc:
        raise RuntimeError(
            "Could not export PNG. Plotly image export requires the `kaleido` package in the active Python environment."
        ) from exc


def _candidate_detail_image_name(position: int, candidate: dict) -> str:
    gap = pd.to_numeric(pd.Series([candidate.get("gap_pct")]), errors="coerce").iloc[0]
    gap_label = f"{gap:.2f}" if pd.notna(gap) else "na"
    raw_name = (
        f"{position:04d}_{candidate.get('ticker')}_{candidate.get('session_date')}"
        f"_gap_{gap_label}_{candidate.get('candidate_id')}"
    )
    return f"{_safe_filename(raw_name)}.png"


def export_run_event_day_detail_images(
    candidates: pd.DataFrame,
    run_dir: Path,
    data_root: str,
    price_view: str,
    y_padding_pct: float,
    sort_mode: str = "gap_pct_desc",
    limit: int | None = None,
    width: int = 1800,
    height: int = 950,
    scale: int = 2,
    progress_callback: Callable[[int, int, Path, dict], None] | None = None,
) -> tuple[Path, list[Path]]:
    if candidates.empty:
        return run_dir / "chart_exports" / "event_day_detail_until_1600_ny", []

    _ensure_plotly_png_export_available()

    candidates = _sort_candidates_for_review(candidates, mode=sort_mode)
    if limit is not None and limit > 0:
        candidates = candidates.head(limit).copy()

    export_root = run_dir / "chart_exports" / "event_day_detail_until_1600_ny"
    images_dir = export_root / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict] = []
    paths: list[Path] = []
    rows = candidates.to_dict("records")
    total = len(rows)
    for position, row in enumerate(rows, start=1):
        path = images_dir / _candidate_detail_image_name(position, row)
        fig = render_candidate_detail_chart(row, data_root, price_view, y_padding_pct)
        try:
            fig.write_image(str(path), width=width, height=height, scale=scale)
        except Exception as exc:
            raise RuntimeError(
                "Could not export PNG. Plotly image export requires the `kaleido` package in the active Python environment."
            ) from exc
        paths.append(path)
        manifest_rows.append(
            {
                "position": position,
                "candidate_id": row.get("candidate_id"),
                "ticker": row.get("ticker"),
                "tradingview_symbol": row.get("tradingview_symbol"),
                "session_date": row.get("session_date"),
                "gap_pct": row.get("gap_pct"),
                "pmh": row.get("pmh"),
                "break_ts_utc": row.get("break_ts_utc"),
                "break_ts_et": row.get("break_ts_et"),
                "image_path": str(path),
            }
        )
        if progress_callback is not None:
            progress_callback(position, total, path, row)

    pd.DataFrame(manifest_rows).to_csv(export_root / "EXPORT_MANIFEST.csv", index=False)
    return export_root, paths


def _delete_run_command(run_dir: Path) -> str:
    return f"Remove-Item -LiteralPath {_ps_quote(str(run_dir))} -Recurse -Force"


def _format_run_option(run_dir: Path) -> tuple[str, str]:
    manifest = _read_manifest(run_dir)
    modified = datetime.fromtimestamp(run_dir.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    run_datetime = manifest.get("run_datetime_utc") or _run_datetime_utc_label(run_dir.name)
    parts = []
    if run_datetime:
        parts.append(f"run_utc={run_datetime}")
    parts.extend([f"modified={modified}", manifest.get("run_status", "unknown")])
    if manifest.get("candidate_count") is not None:
        parts.append(f"candidates={manifest.get('candidate_count')}")
    if manifest.get("raw_candidate_count") is not None:
        parts.append(f"raw={manifest.get('raw_candidate_count')}")
    if manifest.get("files_scanned") is not None and manifest.get("total_files") is not None:
        parts.append(f"files={manifest.get('files_scanned')}/{manifest.get('total_files')}")
    parts.append(run_dir.name)
    return (" | ".join(str(x) for x in parts), str(run_dir))


def _list_run_options() -> list[tuple[str, str]]:
    root = Path(DEFAULT_RUNS_ROOT)
    if not root.exists():
        return []
    runs = sorted((p for p in root.glob("*") if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
    return [_format_run_option(p) for p in runs]


def launch_gap_and_go_app():
    import ipywidgets as widgets
    from IPython.display import HTML, clear_output, display

    data_root = widgets.Text(value=str(DEFAULT_DATA_ROOT), description="1m root", layout=widgets.Layout(width="95%"))
    reference_root = widgets.Text(
        value=str(DEFAULT_REFERENCE_OVERVIEW_ROOT),
        description="Reference",
        layout=widgets.Layout(width="95%"),
    )
    universe_path = widgets.Text(value=str(DEFAULT_LT1B_UNIVERSE_PATH), description="Universe", layout=widgets.Layout(width="95%"))
    tickers = widgets.Text(value="", description="Tickers", placeholder="empty = LT1B universe")
    years = widgets.Text(value="", description="Years", placeholder="e.g. 2025 or 2022-2025")
    min_gap = widgets.FloatText(value=20.0, description="Gap % >")
    min_pm_volume = widgets.FloatText(value=500_000.0, description="PM Vol >")
    min_price = widgets.FloatText(value=0.5, description="Price >")
    max_market_cap = widgets.FloatText(value=100_000_000.0, description="MCap <")
    missing_cap = widgets.Dropdown(options=["include", "exclude", "flag"], value="include", description="No MCap")
    max_minutes = widgets.IntText(value=30, description="Break <= min")
    min_vol_ratio = widgets.FloatText(value=1.5, description="Break Vol x")
    pmh_buffer = widgets.FloatText(value=0.0, description="PMH buf %")
    close_above = widgets.Checkbox(value=True, description="break close > PMH")
    no_fail = widgets.Checkbox(value=False, description="require no PMH fail")
    price_view = widgets.Dropdown(options=["raw", "split_normalized"], value="raw", description="Price")
    y_padding = widgets.BoundedFloatText(value=0.40, min=0.05, max=1.00, step=0.05, description="Y padding")
    progress_every = widgets.IntText(value=250, description="Progress")
    partial_flush = widgets.IntText(value=1, description="Flush hits")
    command_preview = widgets.Textarea(value="", description="Terminal", layout=widgets.Layout(width="95%", height="320px"))
    command_preview_one_line = widgets.Textarea(
        value="",
        description="1 line",
        layout=widgets.Layout(width="95%", height="90px"),
    )
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
    export_png_button = widgets.Button(description="Export PNGs")
    export_detail_run_button = widgets.Button(description="Export detail run")
    tradingview_button = widgets.Button(description="TradingView selected")
    run_button = widgets.Button(description="Run in notebook")
    candidate_sort = widgets.Dropdown(
        options=[
            ("Gap % desc", "gap_pct_desc"),
            ("Group same ticker", "ticker_grouped"),
        ],
        value="gap_pct_desc",
        description="Sort",
    )
    out = widgets.Output()
    state: dict[str, object] = {}
    reference_cache: dict[str, pd.DataFrame] = {}

    def _config() -> GapAndGoConfig:
        return GapAndGoConfig(
            data_root=data_root.value,
            reference_overview_root=reference_root.value,
            universe_path=universe_path.value,
            tickers=_parse_csv(tickers.value),
            years=_parse_years(years.value),
            min_gap_pct=float(min_gap.value),
            min_premarket_volume=float(min_pm_volume.value),
            min_price=float(min_price.value),
            max_market_cap=float(max_market_cap.value),
            missing_market_cap_policy=missing_cap.value,
            max_minutes_after_open_for_break=int(max_minutes.value),
            min_breakout_volume_ratio=float(min_vol_ratio.value),
            pmh_break_buffer_pct=float(pmh_buffer.value),
            require_break_close_above_pmh=bool(close_above.value),
            require_no_immediate_pmh_failure=bool(no_fail.value),
            price_view=price_view.value,
            progress_every=int(progress_every.value),
            partial_flush_every=int(partial_flush.value),
        )

    def _terminal_command() -> str:
        return _terminal_command_from_config(_config(), pretty=True)

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
            event_dates = out_df.loc[mask, "session_date"] if "session_date" in out_df.columns else pd.Series([], dtype="object")

            if ref.get("primary_exchange") is not None:
                out_df.loc[mask, "primary_exchange"] = ref.get("primary_exchange")
            if ref.get("name") is not None:
                out_df.loc[mask, "name"] = ref.get("name")

            tv_symbol = _tradingview_symbol(ticker, ref.get("primary_exchange"))
            existing_tv = out_df.loc[mask, "tradingview_symbol"].astype("string")
            needs_tv = existing_tv.isna() | ~existing_tv.str.contains(":", regex=False, na=False)
            out_df.loc[mask[mask].index[needs_tv.to_numpy()], "tradingview_symbol"] = tv_symbol

            for idx, event_date in event_dates.items():
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
            symbol = getattr(row, "tradingview_symbol", None) or getattr(row, "ticker")
            ticker_count = int(getattr(row, "_ticker_review_count", 1))
            ticker_index = int(getattr(row, "_ticker_review_index", 1))
            repeat_tag = f" [{ticker_index}/{ticker_count}]" if ticker_count > 1 else ""
            options.append(
                (
                    f"{symbol}{repeat_tag} {row.session_date} gap={row.gap_pct:.2f}% volx={row.breakout_volume_ratio:.2f} PMH={row.pmh:.4f}",
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

    def _sync_tradingview_symbol(_change=None) -> None:
        row = _selected_candidate_row()
        if not row:
            tradingview_symbol_text.value = ""
            event_time_text.value = ""
            company_name_text.value = ""
            tradingview_copy_text.value = ""
            return
        symbol = str(row.get("tradingview_symbol") or row.get("ticker") or "")
        name = str(row.get("name") or "")
        event_time = str(row.get("break_ts_et") or row.get("break_ts_utc") or "")
        tradingview_symbol_text.value = symbol
        event_time_text.value = event_time
        company_name_text.value = name
        tradingview_copy_text.value = f"{symbol}\n{event_time}\n{name}".strip()

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
        print("")
        print("Terminal launcher:")
        print(manifest.get("terminal_launcher_pretty") or _terminal_command())
        print("")
        print("Field definitions:")
        for name, description in FIELD_DEFINITIONS:
            print(f"  {name}: {description}")
        print("")

    def _refresh_run_list() -> None:
        run_dropdown.options = _list_run_options()
        if run_dropdown.options:
            run_dropdown.value = run_dropdown.options[0][1]
            run_dir_text.value = str(run_dropdown.value)

    def _on_run_dropdown_change(change) -> None:
        if change.get("new"):
            run_dir_text.value = str(change["new"])

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
                candidates = find_gap_and_go_candidates(cfg, run_dir=run_dir)
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
            path = Path(run_dir_text.value.strip())
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
            path = Path(run_dir_text.value.strip())
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
            candidates = state["candidates"]
            assert isinstance(candidates, pd.DataFrame)
            if not candidate_dropdown.value:
                print("No candidate selected.")
                return
            row = _selected_candidate_row()
            if row is None:
                print("No candidate selected.")
                return
            clear_output()
            print(f"Rendering {row['candidate_id']}")
            print(f"TradingView symbol: {row.get('tradingview_symbol') or row.get('ticker')}")
            for idx, (title, fig) in enumerate(render_candidate_charts(row, data_root.value, price_view.value, y_padding.value), start=1):
                display(HTML(f"<h3>{title}</h3>"))
                if idx == 1:
                    fig.show(config={"scrollZoom": True, "displaylogo": False})
                else:
                    fig.show(config={"staticPlot": True, "displayModeBar": False, "displaylogo": False})

    def _export_pngs(_button) -> None:
        with out:
            if "candidates" not in state:
                print("Load or run candidates first.")
                return
            candidates = state["candidates"]
            assert isinstance(candidates, pd.DataFrame)
            if not candidate_dropdown.value:
                print("No candidate selected.")
                return
            row = _selected_candidate_row()
            if row is None:
                print("No candidate selected.")
                return
            output_root = Path(run_dir_text.value.strip()) if run_dir_text.value.strip() else DEFAULT_RUNS_ROOT
            print(f"Exporting PNGs for {row['candidate_id']}")
            try:
                paths = export_candidate_chart_images(row, data_root.value, price_view.value, y_padding.value, output_root)
            except RuntimeError as exc:
                print(str(exc))
                return
            for path in paths:
                print(path)

    def _export_detail_run(_button) -> None:
        with out:
            clear_output()
            def _emit(message: str) -> None:
                out.append_stdout(f"{message}\n")

            _emit("Export detail run clicked.")
            if not run_dir_text.value.strip():
                _emit("Paste a run_dir first, or use Load latest.")
                return
            path = Path(run_dir_text.value.strip())
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

            export_root = path / "chart_exports" / "event_day_detail_until_1600_ny"
            _emit("Exporting Event-day detail until 16:00 NY images...")
            _emit(f"Run dir: {path}")
            _emit(f"Export dir: {export_root}")
            _emit(f"Candidates: {len(candidates)}")
            _emit("Checking Plotly PNG exporter...")
            try:
                _ensure_plotly_png_export_available()
            except RuntimeError as exc:
                _emit(str(exc))
                _emit("Install kaleido in the active notebook kernel, then click this button again.")
                return
            _emit("PNG exporter available. Starting image export.")

            def _progress(position: int, total: int, image_path: Path, row: dict) -> None:
                _emit(
                    "exported "
                    f"{position}/{total} "
                    f"{row.get('ticker')} {row.get('session_date')} -> {image_path.name}"
                )

            try:
                export_root, paths = export_run_event_day_detail_images(
                    candidates,
                    path,
                    data_root.value,
                    price_view.value,
                    y_padding.value,
                    sort_mode=candidate_sort.value,
                    progress_callback=_progress,
                )
            except RuntimeError as exc:
                _emit(str(exc))
                return
            except Exception as exc:
                _emit(f"Export failed: {type(exc).__name__}: {exc}")
                return

            _emit(f"Done. Images: {len(paths)}")
            _emit(f"Manifest: {export_root / 'EXPORT_MANIFEST.csv'}")
            if paths:
                _emit(f"First image: {paths[0]}")
                _emit(f"Last image: {paths[-1]}")

    def _render_tradingview_selected(_button) -> None:
        with out:
            row = _selected_candidate_row()
            if row is None:
                print("No candidate selected.")
                return
            symbol = str(row.get("tradingview_symbol") or row.get("ticker") or "").strip()
            if not symbol:
                print("Selected candidate has no TradingView symbol.")
                return
            tradingview_symbol_text.value = symbol
            print(f"TradingView symbol: {symbol}")
            print(f"Event time ET: {row.get('break_ts_et') or row.get('break_ts_utc')}")
            if row.get("name"):
                print(f"Company: {row.get('name')}")
            display(tradingview_widget(symbol=symbol, interval=tradingview_interval.value.strip() or "1"))

    refresh_runs_button.on_click(lambda _button: _refresh_run_list())
    run_dropdown.observe(_on_run_dropdown_change, names="value")
    load_selected_button.on_click(_load_selected)
    load_latest_button.on_click(_load_latest)
    load_run_button.on_click(_load_run)
    refresh_partial_button.on_click(_refresh_partial)
    render_button.on_click(_render)
    export_png_button.on_click(_export_pngs)
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
        min_gap,
        min_pm_volume,
        min_price,
        max_market_cap,
        missing_cap,
        max_minutes,
        min_vol_ratio,
        pmh_buffer,
        close_above,
        no_fail,
        price_view,
        progress_every,
        partial_flush,
    ]:
        control.observe(_refresh_command, names="value")
    _refresh_command()
    _refresh_run_list()

    help_text = widgets.HTML(
        value=(
            "<b>Gap and Go search:</b> candidate = gap + PM volume + clear PMH + early PMH break with volume. "
            "<b>PMH hold/failure is measured separately</b> unless the checkbox requires it."
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
            widgets.HBox([tickers, years, price_view]),
            widgets.HBox([min_gap, min_pm_volume, min_price, max_market_cap, missing_cap]),
            widgets.HBox([max_minutes, min_vol_ratio, pmh_buffer, close_above, no_fail, y_padding]),
            widgets.HBox([progress_every, partial_flush]),
            command_preview,
            command_preview_one_line,
            widgets.HBox([refresh_runs_button, load_selected_button, load_latest_button]),
            run_dropdown,
            run_dir_text,
            widgets.HBox(
                [load_run_button, refresh_partial_button, render_button, export_png_button, export_detail_run_button, run_button]
            ),
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
    parser = argparse.ArgumentParser(description="Find exploratory Gap and Go candidates.")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--reference-overview-root", default=str(DEFAULT_REFERENCE_OVERVIEW_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--universe-path", default=str(DEFAULT_LT1B_UNIVERSE_PATH))
    parser.add_argument("--tickers")
    parser.add_argument("--years")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--min-gap-pct", type=float, default=20.0)
    parser.add_argument("--min-premarket-volume", type=float, default=500_000.0)
    parser.add_argument("--min-price", type=float, default=0.5)
    parser.add_argument("--max-market-cap", type=float, default=100_000_000.0)
    parser.add_argument("--missing-market-cap-policy", choices=["include", "exclude", "flag"], default="include")
    parser.add_argument("--max-minutes-after-open-for-break", type=int, default=30)
    parser.add_argument("--min-breakout-volume-ratio", type=float, default=1.5)
    parser.add_argument("--pmh-break-buffer-pct", type=float, default=0.0)
    parser.add_argument("--no-require-break-close-above-pmh", action="store_true")
    parser.add_argument("--require-no-immediate-pmh-failure", action="store_true")
    parser.add_argument("--price-view", choices=["raw", "split_normalized"], default="raw")
    parser.add_argument("--max-candidates", type=int)
    parser.add_argument("--progress-every", type=int, default=250)
    parser.add_argument("--partial-flush-every", type=int, default=1)
    parser.add_argument("--export-detail-images-run-dir")
    parser.add_argument("--export-detail-limit", type=int)
    return parser


def config_from_args(args: argparse.Namespace) -> GapAndGoConfig:
    return GapAndGoConfig(
        data_root=args.data_root,
        reference_overview_root=args.reference_overview_root,
        output_root=args.output_root,
        universe_path=args.universe_path,
        tickers=_parse_csv(args.tickers),
        years=_parse_years(args.years),
        start_date=args.start_date,
        end_date=args.end_date,
        min_gap_pct=args.min_gap_pct,
        min_premarket_volume=args.min_premarket_volume,
        min_price=args.min_price,
        max_market_cap=args.max_market_cap,
        missing_market_cap_policy=args.missing_market_cap_policy,
        max_minutes_after_open_for_break=args.max_minutes_after_open_for_break,
        min_breakout_volume_ratio=args.min_breakout_volume_ratio,
        pmh_break_buffer_pct=args.pmh_break_buffer_pct,
        require_break_close_above_pmh=not args.no_require_break_close_above_pmh,
        require_no_immediate_pmh_failure=args.require_no_immediate_pmh_failure,
        price_view=args.price_view,
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
        candidates = find_gap_and_go_candidates(config, run_dir=run_dir)
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
