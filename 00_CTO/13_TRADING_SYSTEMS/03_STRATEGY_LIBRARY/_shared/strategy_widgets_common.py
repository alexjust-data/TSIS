"""Shared exploratory strategy widget utilities.

This module is neutral infrastructure for notebooks/scripts under
03_STRATEGY_LIBRARY/LONG. Strategy modules must not import helpers from each
other; common helpers live here instead.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pyarrow.parquet as pq


DEFAULT_DATA_ROOT = Path(r"E:\TSIS\data\ohlcv_1m")
DEFAULT_REFERENCE_OVERVIEW_ROOT = Path(r"E:\TSIS\data\reference\overview")
DEFAULT_REFERENCE_SPLITS_ROOT = Path(r"E:\TSIS\data\reference\splits")
DEFAULT_LT1B_UNIVERSE_PATH = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\backtest"
    r"\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff"
    r"\market_cap_cutoff_lt_1b_active_inactive.parquet"
)
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


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


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
            start, end = (item.strip() for item in part.split("-", 1))
            if not start or not end:
                continue
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
        df["px_vw"] = df["vw_split_normalized"] if "vw_split_normalized" in df.columns else pd.NA
    elif price_view == "raw":
        df["px_o"] = df["o"]
        df["px_h"] = df["h"]
        df["px_l"] = df["l"]
        df["px_c"] = df["c"]
        df["px_vw"] = df["vw"] if "vw" in df.columns else pd.NA
    else:
        raise ValueError(f"Unsupported price_view: {price_view}")

    df["px_vw"] = pd.to_numeric(df["px_vw"], errors="coerce")
    df.loc[df["px_vw"] <= 0, "px_vw"] = pd.NA
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


def _text_or_empty(value) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value) is True:
            return ""
    except Exception:
        pass
    return str(value)


def _tradingview_symbol(ticker: str, primary_exchange: str | None) -> str:
    exchange = _text_or_empty(primary_exchange).strip().upper()
    prefix = TRADINGVIEW_EXCHANGE_PREFIX.get(exchange)
    ticker_text = _text_or_empty(ticker).strip().upper()
    return f"{prefix}:{ticker_text}" if prefix else ticker_text


def _compute_vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df["px_h"] + df["px_l"] + df["px_c"]) / 3.0
    pv = typical * df["v"].astype(float)
    cum_vol = df["v"].astype(float).cumsum().replace(0, pd.NA)
    return pv.cumsum() / cum_vol


def _select_vwap(df: pd.DataFrame, vwap_source: str = "calculated") -> pd.Series:
    if vwap_source == "calculated":
        return _compute_vwap(df)
    if vwap_source == "raw":
        if "px_vw" not in df.columns:
            return pd.Series(pd.NA, index=df.index, dtype="Float64")
        raw_vwap = pd.to_numeric(df["px_vw"], errors="coerce")
        return raw_vwap.where(raw_vwap > 0, pd.NA)
    raise ValueError(f"Unsupported vwap_source: {vwap_source}")


def _months_between(start: pd.Timestamp, end: pd.Timestamp) -> list[tuple[int, int]]:
    periods = pd.period_range(start=start.to_period("M"), end=end.to_period("M"), freq="M")
    return [(int(p.year), int(p.month)) for p in periods]


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


def _delete_run_command(run_dir: Path) -> str:
    return f"Remove-Item -LiteralPath {_ps_quote(str(run_dir))} -Recurse -Force"


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


def _add_ema_wilder_columns(df: pd.DataFrame, length: int = 8) -> None:
    close = pd.to_numeric(df["px_c"], errors="coerce")
    df["ema8"] = close.ewm(span=length, adjust=False, min_periods=1).mean()
    df["wilder8"] = close.ewm(alpha=1.0 / length, adjust=False, min_periods=1).mean()


def _true_segments(mask: pd.Series) -> list[tuple[int, int]]:
    values = mask.fillna(False).astype(bool).tolist()
    segments: list[tuple[int, int]] = []
    start: int | None = None
    for idx, value in enumerate(values):
        if value and start is None:
            start = idx
        elif not value and start is not None:
            segments.append((start, idx - 1))
            start = None
    if start is not None:
        segments.append((start, len(values) - 1))
    return segments


def _plotly_slice(values: pd.Series, start: int, end: int) -> list:
    return values.iloc[start : end + 1].tolist() if isinstance(values, pd.Series) else list(values[start : end + 1])


def _add_regime_band(
    fig: go.Figure,
    chart_df: pd.DataFrame,
    x_values: pd.Series,
    mask: pd.Series,
    fillcolor: str,
) -> None:
    for start, end in _true_segments(mask):
        segment = chart_df.iloc[start : end + 1]
        if len(segment) < 2:
            continue
        lower = pd.concat([segment["ema8"], segment["wilder8"]], axis=1).min(axis=1)
        upper = pd.concat([segment["ema8"], segment["wilder8"]], axis=1).max(axis=1)
        x_segment = _plotly_slice(x_values, start, end)
        fig.add_trace(
            go.Scatter(
                x=x_segment,
                y=lower,
                mode="lines",
                line=dict(width=0, color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x_segment,
                y=upper,
                mode="lines",
                fill="tonexty",
                fillcolor=fillcolor,
                line=dict(width=0, color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                showlegend=False,
            ),
            row=1,
            col=1,
        )


def _add_masked_line(
    fig: go.Figure,
    x_values: pd.Series,
    y_values: pd.Series,
    mask: pd.Series,
    name: str,
    color: str,
    width: float = 1.15,
) -> None:
    y_masked = y_values.where(mask)
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_masked,
            mode="lines",
            line=dict(color=color, width=width),
            name=name,
            connectgaps=False,
            hoverinfo="skip",
        ),
        row=1,
        col=1,
    )


def _add_ema_wilder_overlay(fig: go.Figure, chart_df: pd.DataFrame, x_values: pd.Series) -> None:
    bullish = chart_df["ema8"] > chart_df["wilder8"]
    bearish = chart_df["ema8"] < chart_df["wilder8"]

    _add_regime_band(fig, chart_df, x_values, bullish, "rgba(16,185,129,0.18)")
    _add_regime_band(fig, chart_df, x_values, bearish, "rgba(239,68,68,0.16)")

    bullish_line = "rgb(22,163,74)"
    bearish_line = "rgb(220,38,38)"
    _add_masked_line(fig, x_values, chart_df["ema8"], bullish, "EMA8 bullish", bullish_line, width=1.2)
    _add_masked_line(fig, x_values, chart_df["wilder8"], bullish, "Wilder8 bullish", bullish_line, width=1.9)
    _add_masked_line(fig, x_values, chart_df["ema8"], bearish, "EMA8 bearish", bearish_line, width=1.2)
    _add_masked_line(fig, x_values, chart_df["wilder8"], bearish, "Wilder8 bearish", bearish_line, width=1.9)


def make_strategy_1m_chart(
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
    _add_ema_wilder_columns(chart_df)

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
    _add_ema_wilder_overlay(fig, chart_df, x_values)
    hover_cols = [
        "hover_time",
        "hover_time_utc",
        "session_segment",
        "px_o",
        "px_h",
        "px_l",
        "px_c",
        "v",
        "vwap",
        "ema8",
        "wilder8",
    ]
    hover_template = (
        "<b>%{customdata[0]}</b><br>"
        "UTC: %{customdata[1]}<br>"
        "Session: %{customdata[2]}<br>"
        "Open: %{customdata[3]:.4f}<br>"
        "High: %{customdata[4]:.4f}<br>"
        "Low: %{customdata[5]:.4f}<br>"
        "Close: %{customdata[6]:.4f}<br>"
        "Volume: %{customdata[7]:,.0f}<br>"
        "VWAP: %{customdata[8]:.4f}<br>"
        "EMA8: %{customdata[9]:.4f}<br>"
        "Wilder8: %{customdata[10]:.4f}"
        "<extra></extra>"
    )
    fig.add_trace(
        go.Bar(
            x=x_values,
            y=chart_df["v"],
            marker_color=chart_df["volume_color"],
            name="1m volume",
            customdata=chart_df[hover_cols],
            hovertemplate=hover_template,
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
            customdata=chart_df[hover_cols],
            hovertemplate=hover_template,
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
