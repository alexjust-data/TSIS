"""Render interactive Event Discovery candlestick panels."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq


DEFAULT_DATA_ROOT = Path(r"E:\TSIS\data\ohlcv_1m")
DEFAULT_REFERENCE_OVERVIEW_ROOT = Path(r"E:\TSIS\data\reference\overview")
ET_TZ = "America/New_York"
TRADINGVIEW_EXCHANGE_PREFIX = {
    "XNAS": "NASDAQ",
    "XNYS": "NYSE",
    "ARCX": "AMEX",
    "XASE": "AMEX",
    "BATS": "BATS",
    "IEXG": "IEX",
}


def _months_between(start: pd.Timestamp, end: pd.Timestamp) -> list[tuple[int, int]]:
    periods = pd.period_range(start=start.to_period("M"), end=end.to_period("M"), freq="M")
    return [(int(p.year), int(p.month)) for p in periods]


def _file_for_month(data_root: Path, ticker: str, year: int, month: int) -> Path:
    raw_path = (
        data_root
        / f"ticker={ticker.upper()}"
        / f"year={year}"
        / f"month={month:02d}"
        / f"minute_aggs_{ticker.upper()}_{year}_{month:02d}.parquet"
    )
    if raw_path.exists():
        return raw_path
    split_path = raw_path.with_name(f"minute_aggs_{ticker.upper()}_{year}_{month:02d}_split_normalized.parquet")
    if split_path.exists():
        return split_path
    return raw_path


def load_event_window(
    ticker: str,
    event_ts_utc: str,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    days_before: int = 3,
    days_after: int = 3,
    price_view: str = "raw",
) -> pd.DataFrame:
    data_root = Path(data_root)
    event_ts = pd.Timestamp(event_ts_utc)
    if event_ts.tzinfo is None:
        event_ts = event_ts.tz_localize("UTC")
    else:
        event_ts = event_ts.tz_convert("UTC")
    start = event_ts - pd.Timedelta(days=days_before)
    end = event_ts + pd.Timedelta(days=days_after)

    frames: list[pd.DataFrame] = []
    for year, month in _months_between(start.tz_localize(None), end.tz_localize(None)):
        path = _file_for_month(data_root, ticker, year, month)
        if not path.exists():
            continue
        frames.append(_read_price_file(path, price_view))
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df = df[(df["ts_utc_dt"] >= start) & (df["ts_utc_dt"] <= end)].copy()
    df = df.sort_values("ts_utc_dt").reset_index(drop=True)
    df["ts_et_naive"] = df["ts_utc_dt"].dt.tz_convert(ET_TZ).dt.tz_localize(None)
    df["session_segment"] = _session_segment(df["ts_utc_dt"].dt.tz_convert(ET_TZ))
    return df


def _read_price_file(path: Path, price_view: str) -> pd.DataFrame:
    schema_names = set(pq.ParquetFile(path).schema_arrow.names)
    cols = [
        "ticker",
        "ts_utc",
        "o",
        "h",
        "l",
        "c",
        "v",
        "o_split_normalized",
        "h_split_normalized",
        "l_split_normalized",
        "c_split_normalized",
    ]
    table = pq.ParquetFile(path).read(columns=[c for c in cols if c in schema_names])
    df = table.to_pandas()
    if df.empty:
        return df
    if price_view == "split_normalized":
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
    return df.dropna(subset=["ts_utc_dt", "px_o", "px_h", "px_l", "px_c"])


def _session_segment(ts_et: pd.Series) -> pd.Series:
    minutes = ts_et.dt.hour * 60 + ts_et.dt.minute
    out = pd.Series("overnight", index=ts_et.index, dtype="object")
    out[(minutes >= 4 * 60) & (minutes < 9 * 60 + 30)] = "premarket"
    out[(minutes >= 9 * 60 + 30) & (minutes < 16 * 60)] = "regular"
    out[(minutes >= 16 * 60) & (minutes < 20 * 60)] = "afterhours"
    return out


def _tradingview_symbol(ticker: str, primary_exchange: str | None) -> str:
    exchange = str(primary_exchange or "").strip().upper()
    prefix = TRADINGVIEW_EXCHANGE_PREFIX.get(exchange)
    if prefix:
        return f"{prefix}:{ticker.upper()}"
    return ticker.upper()


def _latest_reference_metadata(ticker: str, reference_overview_root: str | Path) -> dict:
    ticker_dir = Path(reference_overview_root) / f"ticker={ticker.upper()}"
    files = sorted(ticker_dir.glob("*.parquet"))
    if not files:
        return {}
    latest = files[-1]
    schema_names = set(pq.ParquetFile(latest).schema_arrow.names)
    cols = [c for c in ["ticker", "primary_exchange", "market", "name", "request_date"] if c in schema_names]
    if not cols:
        return {}
    df = pq.ParquetFile(latest).read(columns=cols).to_pandas()
    if df.empty:
        return {}
    row = df.iloc[-1].to_dict()
    primary_exchange = row.get("primary_exchange")
    row["tradingview_symbol"] = _tradingview_symbol(ticker, primary_exchange)
    return row


def _enrich_candidate_reference(candidate: dict, reference_overview_root: str | Path) -> dict:
    out = dict(candidate)
    ticker = str(out.get("ticker", "")).upper()
    if not ticker:
        return out
    if out.get("tradingview_symbol"):
        return out
    if not out.get("primary_exchange"):
        out.update({k: v for k, v in _latest_reference_metadata(ticker, reference_overview_root).items() if pd.notna(v)})
    out["tradingview_symbol"] = _tradingview_symbol(ticker, out.get("primary_exchange"))
    return out


def make_event_chart(
    df: pd.DataFrame,
    candidate: dict,
    y_padding_pct: float = 0.40,
    title: str | None = None,
    compact_xaxis: bool = True,
) -> go.Figure:
    if df.empty:
        raise ValueError("No rows available for event window.")

    event_start = pd.Timestamp(candidate["event_ts_utc"])
    event_end = pd.Timestamp(candidate["event_end_ts_utc"])
    event_start_et = event_start.tz_convert(ET_TZ).tz_localize(None)
    event_end_et = event_end.tz_convert(ET_TZ).tz_localize(None)
    chart_df = df.reset_index(drop=True).copy()
    chart_df["bar_index"] = chart_df.index
    chart_df["hover_time"] = chart_df["ts_et_naive"].dt.strftime("%Y-%m-%d %H:%M ET")
    chart_df["hover_time_utc"] = chart_df["ts_utc_dt"].dt.strftime("%Y-%m-%d %H:%M UTC")
    if compact_xaxis:
        x_values = chart_df["bar_index"]
        event_positions = chart_df[
            (chart_df["ts_utc_dt"] >= event_start) & (chart_df["ts_utc_dt"] <= event_end)
        ]["bar_index"]
        if event_positions.empty:
            event_x0 = int(chart_df["bar_index"].iloc[0])
            event_x1 = event_x0 + 1
        else:
            event_x0 = int(event_positions.min())
            event_x1 = int(event_positions.max()) + 1
    else:
        x_values = chart_df["ts_et_naive"]
        event_x0 = event_start_et
        event_x1 = event_end_et + pd.Timedelta(minutes=1)

    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=x_values,
            open=chart_df["px_o"],
            high=chart_df["px_h"],
            low=chart_df["px_l"],
            close=chart_df["px_c"],
            hoverinfo="skip",
            increasing_line_color="black",
            decreasing_line_color="black",
            increasing_fillcolor="rgba(0,0,0,0)",
            decreasing_fillcolor="rgba(0,0,0,0)",
            name="1m candles",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=chart_df["px_c"],
            mode="markers",
            marker=dict(size=14, color="rgba(0,0,0,0.01)", line=dict(width=0)),
            customdata=chart_df[
                [
                    "hover_time",
                    "hover_time_utc",
                    "session_segment",
                    "px_o",
                    "px_h",
                    "px_l",
                    "px_c",
                    "v",
                ]
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "UTC: %{customdata[1]}<br>"
                "Session: %{customdata[2]}<br>"
                "Open: %{customdata[3]:.4f}<br>"
                "High: %{customdata[4]:.4f}<br>"
                "Low: %{customdata[5]:.4f}<br>"
                "Close: %{customdata[6]:.4f}<br>"
                "Volume: %{customdata[7]:,.0f}"
                "<extra></extra>"
            ),
            name="OHLC",
            showlegend=False,
        )
    )

    if compact_xaxis:
        _add_compact_session_backgrounds(fig, chart_df)
    else:
        _add_session_backgrounds(fig, chart_df)
    fig.add_vrect(
        x0=event_x0,
        x1=event_x1,
        fillcolor="rgba(255,0,0,0.16)",
        line_width=1,
        line_color="rgba(180,0,0,0.9)",
        annotation_text="3-bar push",
        annotation_position="top left",
    )

    low = float(chart_df["px_l"].min())
    high = float(chart_df["px_h"].max())
    span = max(high - low, high * 0.05, 0.01)
    pad = span * y_padding_pct

    ticker = candidate.get("ticker", "")
    push = candidate.get("push_pct", "")
    security_label = candidate.get("tradingview_symbol") or ticker
    chart_title = title or f"{security_label} 1m Event Discovery | 3-bar push {push}%"
    fig.update_layout(
        title=chart_title,
        template="plotly_white",
        height=850,
        hovermode="closest",
        hoverdistance=-1,
        spikedistance=-1,
        dragmode="pan",
        xaxis_rangeslider_visible=True,
        margin=dict(l=30, r=70, t=55, b=35),
        showlegend=False,
    )
    spike_style = dict(
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikedash="dot",
        spikecolor="rgba(20,20,20,0.65)",
        spikethickness=1,
    )
    fig.update_yaxes(range=[low - pad, high + pad], side="right", fixedrange=False, **spike_style)
    if compact_xaxis:
        tick_step = max(len(chart_df) // 12, 1)
        tick_positions = chart_df["bar_index"].iloc[::tick_step].tolist()
        tick_labels = chart_df["ts_et_naive"].iloc[::tick_step].dt.strftime("%b %d<br>%H:%M").tolist()
        fig.update_xaxes(
            type="linear",
            rangeslider_thickness=0.06,
            tickmode="array",
            tickvals=tick_positions,
            ticktext=tick_labels,
            title_text="ET time, observed 1m bars (gaps compressed)",
            **spike_style,
        )
    else:
        fig.update_xaxes(type="date", rangeslider_thickness=0.06, title_text="ET time", **spike_style)
    return fig


def _add_session_backgrounds(fig: go.Figure, df: pd.DataFrame) -> None:
    if df.empty:
        return
    dates = pd.Series(df["ts_et_naive"].dt.date).drop_duplicates().sort_values()
    for day in dates:
        base = pd.Timestamp(day)
        fig.add_vrect(
            x0=base + pd.Timedelta(hours=4),
            x1=base + pd.Timedelta(hours=9, minutes=30),
            fillcolor="rgba(255,174,66,0.28)",
            line_width=0,
            layer="below",
        )
        fig.add_vrect(
            x0=base + pd.Timedelta(hours=16),
            x1=base + pd.Timedelta(hours=20),
            fillcolor="rgba(90,140,255,0.18)",
            line_width=0,
            layer="below",
        )


def _add_compact_session_backgrounds(fig: go.Figure, df: pd.DataFrame) -> None:
    if df.empty:
        return
    grouped = (
        df[df["session_segment"].isin(["premarket", "afterhours"])]
        .groupby(["session_segment", df["ts_et_naive"].dt.date], sort=True)["bar_index"]
        .agg(["min", "max"])
        .reset_index()
    )
    colors = {
        "premarket": "rgba(255,174,66,0.28)",
        "afterhours": "rgba(90,140,255,0.18)",
    }
    for row in grouped.itertuples(index=False):
        fig.add_vrect(
            x0=int(row.min),
            x1=int(row.max) + 1,
            fillcolor=colors.get(row.session_segment, "rgba(0,0,0,0)"),
            line_width=0,
            layer="below",
        )


def render_candidate(
    candidate: dict,
    data_root: str | Path = DEFAULT_DATA_ROOT,
    days_before: int = 3,
    days_after: int = 3,
    y_padding_pct: float = 0.40,
    compact_xaxis: bool = True,
    reference_overview_root: str | Path = DEFAULT_REFERENCE_OVERVIEW_ROOT,
) -> go.Figure:
    candidate = _enrich_candidate_reference(candidate, reference_overview_root)
    df = load_event_window(
        ticker=candidate["ticker"],
        event_ts_utc=candidate["event_ts_utc"],
        data_root=data_root,
        days_before=days_before,
        days_after=days_after,
        price_view=candidate.get("price_view", "split_normalized"),
    )
    return make_event_chart(df, candidate, y_padding_pct=y_padding_pct, compact_xaxis=compact_xaxis)


def _load_candidate(path: Path, candidate_id: str | None) -> dict:
    if path.suffix.lower() == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"No candidates in {path}")
    if candidate_id:
        df = df[df["candidate_id"].eq(candidate_id)]
        if df.empty:
            raise ValueError(f"candidate_id not found: {candidate_id}")
    return df.iloc[0].to_dict()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render Event Discovery case panel.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--candidate-id")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--reference-overview-root", default=str(DEFAULT_REFERENCE_OVERVIEW_ROOT))
    parser.add_argument("--output-html")
    parser.add_argument("--y-padding-pct", type=float, default=0.40)
    parser.add_argument("--real-time-axis", action="store_true")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    candidate = _load_candidate(Path(args.candidates), args.candidate_id)
    fig = render_candidate(
        candidate,
        data_root=args.data_root,
        reference_overview_root=args.reference_overview_root,
        y_padding_pct=args.y_padding_pct,
        compact_xaxis=not args.real_time_axis,
    )
    if args.output_html:
        fig.write_html(args.output_html, include_plotlyjs="cdn", config={"scrollZoom": True})
        print(args.output_html)
    else:
        fig.show(config={"scrollZoom": True, "displaylogo": False})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
