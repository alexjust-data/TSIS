from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import Markdown, clear_output, display


def build_trade_price_outside_daily_range_cases(events_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    daily_range_hard = events_df.loc[
        events_df["issues_list"].map(lambda xs: "trade_price_outside_daily_range" in set(xs))
    ].copy()

    for c in [
        "m.price_min",
        "m.price_max",
        "m.trade_vwap",
        "m.vw",
        "m.l",
        "m.h",
        "m.ohlcv_1m_low_min",
        "m.ohlcv_1m_high_max",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
    ]:
        if c in daily_range_hard.columns:
            daily_range_hard[c] = pd.to_numeric(daily_range_hard[c], errors="coerce")

    daily_range_hard["outside_below_abs"] = (
        daily_range_hard["m.l"] - daily_range_hard["m.price_min"]
    ).clip(lower=0)

    daily_range_hard["outside_above_abs"] = (
        daily_range_hard["m.price_max"] - daily_range_hard["m.h"]
    ).clip(lower=0)

    daily_range_hard["daily_span"] = daily_range_hard["m.h"] - daily_range_hard["m.l"]

    daily_range_hard["outside_abs_max"] = daily_range_hard[
        ["outside_below_abs", "outside_above_abs"]
    ].max(axis=1)

    daily_range_hard["outside_pct_of_daily_span"] = (
        100 * daily_range_hard["outside_abs_max"] / daily_range_hard["daily_span"].replace(0, np.nan)
    )

    rank_cols = [
        "ticker",
        "date",
        "batch_id",
        "severity",
        "outside_abs_max",
        "outside_pct_of_daily_span",
        "m.price_min",
        "m.price_max",
        "m.l",
        "m.h",
        "m.trade_vwap",
        "m.vw",
        "m.ohlcv_1m_low_min",
        "m.ohlcv_1m_high_max",
        "file",
    ]

    ranked_cases = (
        daily_range_hard[rank_cols]
        .sort_values(["outside_pct_of_daily_span", "outside_abs_max"], ascending=[False, False])
        .reset_index(drop=True)
    )

    return daily_range_hard, ranked_cases


def load_trade_daily_1m_case_refs(
    case_row: pd.Series,
    ohlcv_daily_root: Path,
    ohlcv_1m_root: Path,
) -> dict[str, Any]:
    ticker = str(case_row["ticker"])
    date_ts = pd.Timestamp(case_row["date"])
    date_str = str(date_ts.date())
    trade_path = Path(case_row["file"])

    daily_path = (
        ohlcv_daily_root
        / f"ticker={ticker}"
        / f"year={date_ts.year:04d}"
        / f"day_aggs_{ticker}_{date_ts.year:04d}.parquet"
    )

    m1_path = (
        ohlcv_1m_root
        / f"ticker={ticker}"
        / f"year={date_ts.year:04d}"
        / f"month={date_ts.month:02d}"
        / f"minute_aggs_{ticker}_{date_ts.year:04d}_{date_ts.month:02d}.parquet"
    )

    if not trade_path.exists():
        raise FileNotFoundError(f"Trade file no existe: {trade_path}")
    if not daily_path.exists():
        raise FileNotFoundError(f"Daily file no existe: {daily_path}")
    if not m1_path.exists():
        raise FileNotFoundError(f"1m file no existe: {m1_path}")

    trades_df = pd.read_parquet(trade_path).copy()
    trades_df["timestamp"] = pd.to_datetime(trades_df["timestamp"], utc=True, errors="coerce")
    trades_df["price"] = pd.to_numeric(trades_df["price"], errors="coerce")
    trades_df["size"] = pd.to_numeric(trades_df["size"], errors="coerce")
    trades_df = trades_df.dropna(subset=["timestamp", "price"]).sort_values("timestamp").copy()

    daily_df = pd.read_parquet(daily_path).copy()
    daily_match = daily_df.loc[daily_df["date"].astype(str) == date_str]
    if daily_match.empty:
        raise ValueError(f"No hay fila daily para {ticker} {date_str} en {daily_path}")
    daily_row = daily_match.iloc[0]

    m1_df = pd.read_parquet(m1_path).copy()
    m1_day = m1_df.loc[m1_df["date"].astype(str) == date_str].copy()

    if "ts_utc" in m1_day.columns:
        m1_day["ts_utc"] = pd.to_datetime(m1_day["ts_utc"], utc=True, errors="coerce")
    elif "timestamp" in m1_day.columns:
        m1_day["ts_utc"] = pd.to_datetime(m1_day["timestamp"], utc=True, errors="coerce")

    m1_day = m1_day.sort_values("ts_utc").copy()

    return {
        "ticker": ticker,
        "date_ts": date_ts,
        "date_str": date_str,
        "trade_path": trade_path,
        "daily_path": daily_path,
        "m1_path": m1_path,
        "trades_df": trades_df,
        "daily_row": daily_row,
        "m1_day": m1_day,
    }


def annotate_trade_outside_daily(
    trades_df: pd.DataFrame,
    daily_row: pd.Series,
) -> tuple[pd.DataFrame, float, float, float, float, float]:
    out = trades_df.copy()

    daily_low = float(daily_row["l"])
    daily_high = float(daily_row["h"])
    daily_open = float(daily_row["o"])
    daily_close = float(daily_row["c"])
    daily_vw = float(daily_row["vw"]) if pd.notna(daily_row["vw"]) else np.nan

    out["below_daily"] = out["price"] < daily_low
    out["above_daily"] = out["price"] > daily_high
    out["outside_daily"] = out["below_daily"] | out["above_daily"]

    return out, daily_low, daily_high, daily_open, daily_close, daily_vw


def build_case_summary_table(
    trades_df: pd.DataFrame,
    daily_low: float,
    daily_high: float,
    daily_vw: float,
) -> pd.DataFrame:
    summary_rows = pd.DataFrame([
        ["trades_total", int(len(trades_df))],
        ["outside_daily_count", int(trades_df["outside_daily"].sum())],
        ["outside_daily_pct", round(100 * trades_df["outside_daily"].mean(), 4)],
        ["trade_min", float(trades_df["price"].min())],
        ["trade_max", float(trades_df["price"].max())],
        ["daily_low", daily_low],
        ["daily_high", daily_high],
        [
            "min_below_low",
            float((daily_low - trades_df.loc[trades_df["below_daily"], "price"]).max())
            if trades_df["below_daily"].any()
            else 0.0,
        ],
        [
            "max_above_high",
            float((trades_df.loc[trades_df["above_daily"], "price"] - daily_high).max())
            if trades_df["above_daily"].any()
            else 0.0,
        ],
        [
            "trade_vwap",
            float((trades_df["price"] * trades_df["size"].fillna(0)).sum() / trades_df["size"].fillna(0).sum())
            if trades_df["size"].fillna(0).sum() > 0
            else np.nan,
        ],
        ["daily_vw", daily_vw],
    ])
    return summary_rows


def plot_trade_vs_daily_1m_case(
    ticker: str,
    date_str: str,
    trades_df: pd.DataFrame,
    m1_day: pd.DataFrame,
    daily_low: float,
    daily_high: float,
    daily_open: float,
    daily_close: float,
    daily_vw: float,
    summary_rows: pd.DataFrame,
) -> None:
    fig = plt.figure(figsize=(18, 14))
    gs = fig.add_gridspec(3, 2, height_ratios=[2.2, 1.2, 1.2], width_ratios=[3.2, 1.2])

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0], sharex=ax1)
    ax4 = fig.add_subplot(gs[1, 1])
    ax5 = fig.add_subplot(gs[2, 0])
    ax6 = fig.add_subplot(gs[2, 1])

    ax1.scatter(
        trades_df.loc[~trades_df["outside_daily"], "timestamp"],
        trades_df.loc[~trades_df["outside_daily"], "price"],
        s=6,
        alpha=0.45,
        color="#457b9d",
        label="trades inside daily range",
    )
    ax1.scatter(
        trades_df.loc[trades_df["outside_daily"], "timestamp"],
        trades_df.loc[trades_df["outside_daily"], "price"],
        s=10,
        alpha=0.85,
        color="#d62828",
        label="trades outside daily range",
    )

    ax1.axhspan(daily_low, daily_high, alpha=0.16, color="#2a9d8f", label="daily low/high band")
    ax1.axhline(daily_low, ls="--", lw=1.2, color="#1b7f6b")
    ax1.axhline(daily_high, ls="--", lw=1.2, color="#1b7f6b")
    ax1.axhline(daily_open, ls=":", lw=1.1, color="#264653", label="daily open")
    ax1.axhline(daily_close, ls="-.", lw=1.1, color="#6d597a", label="daily close")
    if pd.notna(daily_vw):
        ax1.axhline(daily_vw, ls="-", lw=1.1, color="#f4a261", label="daily vw")

    if not m1_day.empty:
        ax1.fill_between(
            m1_day["ts_utc"],
            pd.to_numeric(m1_day["l"], errors="coerce"),
            pd.to_numeric(m1_day["h"], errors="coerce"),
            color="#e9c46a",
            alpha=0.22,
            label="1m low/high envelope",
        )

    ax1.set_title(f"Trades vs daily range and 1m envelope: {ticker} {date_str}")
    ax1.set_ylabel("price")
    ax1.legend(loc="best", fontsize=9)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    ax2.hist(trades_df["price"], bins=60, orientation="horizontal", color="#457b9d", alpha=0.8)
    ax2.axhspan(daily_low, daily_high, alpha=0.16, color="#2a9d8f")
    ax2.axhline(daily_low, ls="--", lw=1.2, color="#1b7f6b")
    ax2.axhline(daily_high, ls="--", lw=1.2, color="#1b7f6b")
    ax2.set_title("Price distribution")
    ax2.set_xlabel("count")
    ax2.set_ylabel("price")

    sizes_scaled = np.clip(np.sqrt(trades_df["size"].fillna(0)), 3, 80)
    ax3.scatter(
        trades_df["timestamp"],
        trades_df["price"],
        s=sizes_scaled,
        c=np.where(trades_df["outside_daily"], "#d62828", "#457b9d"),
        alpha=0.35,
    )
    ax3.axhline(daily_low, ls="--", lw=1.0, color="#1b7f6b")
    ax3.axhline(daily_high, ls="--", lw=1.0, color="#1b7f6b")
    ax3.set_title("Trade size-weighted view")
    ax3.set_ylabel("price")
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    outside_prices = trades_df.loc[trades_df["outside_daily"], "price"].copy()
    dist_below = (daily_low - outside_prices[outside_prices < daily_low]).rename("dist")
    dist_above = (outside_prices[outside_prices > daily_high] - daily_high).rename("dist")
    dist_df = pd.concat(
        [
            pd.DataFrame({"side": "below_low", "dist": dist_below}),
            pd.DataFrame({"side": "above_high", "dist": dist_above}),
        ],
        ignore_index=True,
    )

    if not dist_df.empty:
        ax4.boxplot(
            [
                dist_df.loc[dist_df["side"] == "below_low", "dist"],
                dist_df.loc[dist_df["side"] == "above_high", "dist"],
            ],
            labels=["below_low", "above_high"],
        )
    ax4.set_title("Distance outside daily range")
    ax4.set_xlabel("")
    ax4.set_ylabel("absolute distance")

    if not m1_day.empty:
        x = m1_day["ts_utc"]
        o = pd.to_numeric(m1_day["o"], errors="coerce")
        h = pd.to_numeric(m1_day["h"], errors="coerce")
        l = pd.to_numeric(m1_day["l"], errors="coerce")
        c = pd.to_numeric(m1_day["c"], errors="coerce")

        ax5.vlines(x, l, h, color="#6c757d", alpha=0.8, lw=1)
        up = c >= o
        down = ~up
        ax5.bar(x[up], (c - o)[up], bottom=o[up], width=0.0009, color="#2a9d8f", alpha=0.7)
        ax5.bar(x[down], (c - o)[down], bottom=o[down], width=0.0009, color="#e76f51", alpha=0.7)

        ax5.scatter(
            trades_df.loc[trades_df["outside_daily"], "timestamp"],
            trades_df.loc[trades_df["outside_daily"], "price"],
            s=14,
            color="#d62828",
            alpha=0.9,
            label="outside daily",
        )
        ax5.axhline(daily_low, ls="--", lw=1.2, color="#1b7f6b")
        ax5.axhline(daily_high, ls="--", lw=1.2, color="#1b7f6b")
        ax5.set_title("1m candles + offending trades")
        ax5.set_ylabel("price")
        ax5.legend(loc="best", fontsize=9)
        ax5.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    ax6.axis("off")
    tbl = ax6.table(cellText=summary_rows.values, colLabels=["metric", "value"], loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.5)
    ax6.set_title("Case summary")

    plt.tight_layout()
    plt.show()


def plot_trade_vs_reference_scale_comparison(
    trades_df: pd.DataFrame,
    m1_day: pd.DataFrame,
    daily_low: float,
    daily_high: float,
    daily_close: float,
    daily_vw: float,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))

    m1_plot = m1_day.copy()
    if not m1_plot.empty:
        if "ts_utc" in m1_plot.columns:
            m1_plot["ts_utc"] = pd.to_datetime(m1_plot["ts_utc"], utc=True, errors="coerce")
        m1_plot["l_num"] = pd.to_numeric(m1_plot["l"], errors="coerce")
        m1_plot["h_num"] = pd.to_numeric(m1_plot["h"], errors="coerce")
        m1_plot = m1_plot.dropna(subset=["ts_utc", "l_num", "h_num"]).copy()

    trade_base = trades_df["price"].median()
    if pd.isna(trade_base) or trade_base <= 0:
        trade_base = trades_df["price"].mean()

    ref_base = daily_vw if pd.notna(daily_vw) and daily_vw > 0 else daily_close

    ax = axes[0, 0]
    ax.scatter(
        trades_df["timestamp"],
        trades_df["price"],
        s=10,
        color="#d62828",
        alpha=0.7,
        label="trades",
    )
    ax.axhspan(daily_low, daily_high, alpha=0.18, color="#2a9d8f", label="daily low/high")
    if pd.notna(daily_vw):
        ax.axhline(daily_vw, color="#f4a261", lw=1.2, ls="--", label="daily vw")
    if not m1_plot.empty:
        ax.fill_between(
            m1_plot["ts_utc"],
            m1_plot["l_num"],
            m1_plot["h_num"],
            color="#f5b617",
            alpha=0.22,
            label="1m envelope",
        )
    ax.set_title("A. Escala real completa")
    ax.set_ylabel("price")
    ax.legend(loc="best", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    ax = axes[0, 1]
    ax.scatter(
        trades_df["timestamp"],
        trades_df["price"],
        s=12,
        color="#d62828",
        alpha=0.8,
    )
    pmin = trades_df["price"].min()
    pmax = trades_df["price"].max()
    pspan = max(pmax - pmin, 1e-9)
    ax.set_ylim(pmin - 0.02 * pspan, pmax + 0.02 * pspan)
    ax.set_title("B. Zoom trades")
    ax.set_ylabel("price")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    ax = axes[1, 0]
    if not m1_plot.empty:
        ax.fill_between(
            m1_plot["ts_utc"],
            m1_plot["l_num"],
            m1_plot["h_num"],
            color="#e7ac17",
            alpha=0.22,
            label="1m envelope",
        )
    ax.axhspan(daily_low, daily_high, alpha=0.18, color="#2a9d8f", label="daily low/high")
    if pd.notna(daily_vw):
        ax.axhline(daily_vw, color="#f4a261", lw=1.2, ls="--", label="daily vw")
    dspan = max(daily_high - daily_low, 1e-9)
    ax.set_ylim(daily_low - 0.05 * dspan, daily_high + 0.05 * dspan)
    ax.set_title("C. Zoom referencias")
    ax.set_ylabel("price")
    ax.legend(loc="best", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    ax = axes[1, 1]
    trades_norm = trades_df.copy()
    trades_norm["price_norm"] = trades_norm["price"] / trade_base
    ax.scatter(
        trades_norm["timestamp"],
        trades_norm["price_norm"],
        s=10,
        color="#d62828",
        alpha=0.7,
        label="trades / trade_median",
    )
    if not m1_plot.empty and pd.notna(ref_base) and ref_base > 0:
        m1_norm = m1_plot.copy()
        m1_norm["l_norm"] = m1_norm["l_num"] / ref_base
        m1_norm["h_norm"] = m1_norm["h_num"] / ref_base
        ax.fill_between(
            m1_norm["ts_utc"],
            m1_norm["l_norm"],
            m1_norm["h_norm"],
            color="#f9b406",
            alpha=0.22,
            label="1m envelope / daily_ref",
        )
    if pd.notna(ref_base) and ref_base > 0:
        ax.axhspan(
            daily_low / ref_base,
            daily_high / ref_base,
            alpha=0.18,
            color="#2a9d8f",
            label="daily band / daily_ref",
        )
    ax.axhline(1.0, color="#264653", lw=1.1, ls="--")
    ax.set_title("D. Escala normalizada")
    ax.set_ylabel("normalized price")
    ax.legend(loc="best", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    plt.tight_layout()
    plt.show()


def _sort_ranked_cases(ranked_cases: pd.DataFrame, sort_mode: str) -> pd.DataFrame:
    if sort_mode == "Peor outside_pct":
        return ranked_cases.sort_values(
            ["outside_pct_of_daily_span", "outside_abs_max"],
            ascending=[False, False],
        ).reset_index(drop=True)
    if sort_mode == "Mayor outside_abs":
        return ranked_cases.sort_values(
            ["outside_abs_max", "outside_pct_of_daily_span"],
            ascending=[False, False],
        ).reset_index(drop=True)
    return ranked_cases.sort_values(["ticker", "date"], ascending=[True, True]).reset_index(drop=True)


def _format_case_label(case_idx: int, row: pd.Series) -> str:
    ticker = str(row["ticker"])
    date_str = str(row["date"])
    gap_pct = row.get("outside_pct_of_daily_span", np.nan)
    gap_abs = row.get("outside_abs_max", np.nan)

    if pd.notna(gap_pct) and pd.notna(gap_abs):
        return f"{case_idx:04d} | {ticker} | {date_str} | gap_pct={gap_pct:,.2f}% | gap_abs={gap_abs:,.4f}"
    return f"{case_idx:04d} | {ticker} | {date_str}"


def _build_case_options(ranked_cases: pd.DataFrame) -> list[tuple[str, int]]:
    return [
        (_format_case_label(i, row), i)
        for i, row in ranked_cases.reset_index(drop=True).iterrows()
    ]


def run_trade_price_outside_daily_range_widget(
    events_df: pd.DataFrame,
    ohlcv_daily_root: Path,
    ohlcv_1m_root: Path,
    initial_case_idx: int = 0,
    initial_sort_mode: str = "Peor outside_pct",
) -> None:
    _, ranked_cases_base = build_trade_price_outside_daily_range_cases(events_df)
    ranked_cases = _sort_ranked_cases(ranked_cases_base, initial_sort_mode)

    case_dropdown = widgets.Dropdown(
        options=_build_case_options(ranked_cases),
        value=min(initial_case_idx, max(len(ranked_cases) - 1, 0)),
        description="Caso",
        layout=widgets.Layout(width="1400px"),
        style={"description_width": "80px"},
    )

    case_slider = widgets.IntSlider(
        value=min(initial_case_idx, max(len(ranked_cases) - 1, 0)),
        min=0,
        max=max(len(ranked_cases) - 1, 0),
        step=1,
        description="IDX",
        continuous_update=False,
        layout=widgets.Layout(width="900px"),
    )

    sort_selector = widgets.Dropdown(
        options=["Peor outside_pct", "Mayor outside_abs", "Ticker/date"],
        value=initial_sort_mode,
        description="Orden",
        layout=widgets.Layout(width="420px"),
    )

    controls_box = widgets.VBox([sort_selector, case_dropdown, case_slider])

    def render_case(case_idx: int) -> None:
        case = ranked_cases.iloc[int(case_idx)]
        case_ctx = load_trade_daily_1m_case_refs(
            case_row=case,
            ohlcv_daily_root=ohlcv_daily_root,
            ohlcv_1m_root=ohlcv_1m_root,
        )

        trades_df, daily_low, daily_high, daily_open, daily_close, daily_vw = annotate_trade_outside_daily(
            case_ctx["trades_df"],
            case_ctx["daily_row"],
        )

        summary_rows = build_case_summary_table(
            trades_df,
            daily_low,
            daily_high,
            daily_vw,
        )

        clear_output(wait=True)
        display(controls_box)
        display(Markdown(
            f"""
### Caso {int(case_idx)}

- `ticker`: `{case_ctx['ticker']}`
- `date`: `{case_ctx['date_str']}`
- `batch_id`: `{case['batch_id']}`
- `file`: `{case_ctx['trade_path']}`
- `daily_path`: `{case_ctx['daily_path']}`
- `m1_path`: `{case_ctx['m1_path']}`
"""
        ))

        plot_trade_vs_daily_1m_case(
            ticker=case_ctx["ticker"],
            date_str=case_ctx["date_str"],
            trades_df=trades_df,
            m1_day=case_ctx["m1_day"],
            daily_low=daily_low,
            daily_high=daily_high,
            daily_open=daily_open,
            daily_close=daily_close,
            daily_vw=daily_vw,
            summary_rows=summary_rows,
        )

        display(Markdown(
            """
**Lectura de la figura forense principal**

- Panel superior izquierdo: sitúa todos los `trades` del file frente al rango `daily` y, si existe, frente a la envolvente `1m`.
- Panel superior derecho: muestra la distribución de precios del file y permite ver cuánto cae fuera del rango `daily`.
- Panel central izquierdo: pondera visualmente por tamaño (`size`) para distinguir si la ruptura está dominada por prints pequeños o por volumen relevante.
- Panel central derecho: resume la distancia absoluta de los trades ofensivos respecto a `daily_low` y `daily_high`.
- Panel inferior izquierdo: superpone velas `1m` y trades ofensivos para ver si la ruptura también queda fuera del contexto intradía agregado.
- Panel inferior derecho: resume las métricas clave del caso (`outside count`, extremos de precio, ruptura máxima, VWAP de trades y referencia daily).
"""
        ))

        plot_trade_vs_reference_scale_comparison(
            trades_df=trades_df,
            m1_day=case_ctx["m1_day"],
            daily_low=daily_low,
            daily_high=daily_high,
            daily_close=daily_close,
            daily_vw=daily_vw,
        )

        display(Markdown(
            """
**Lectura de la comparativa de escala**

- Panel A: muestra la incompatibilidad de escala en valores absolutos entre `trades` y referencias.
- Panel B: muestra la coherencia interna de los `trades` cuando se observan en su propia escala.
- Panel C: muestra la coherencia relativa entre `daily` y `1m` dentro de la escala de referencia.
- Panel D: compara forma temporal tras normalización, separando morfología de nivel absoluto.

Nota técnica:
- `trades` se normaliza por `trade_median`
- `daily/1m` se normalizan por `daily_vw` o, en su ausencia, `daily_close`
"""
        ))

    def sync_case_controls(case_idx: int) -> None:
        case_idx = int(case_idx)
        if case_dropdown.value != case_idx:
            case_dropdown.value = case_idx
        if case_slider.value != case_idx:
            case_slider.value = case_idx

    def update_case_order(sort_mode: str) -> None:
        nonlocal ranked_cases
        ranked_cases = _sort_ranked_cases(ranked_cases_base, sort_mode)
        case_dropdown.options = _build_case_options(ranked_cases)
        case_slider.max = max(len(ranked_cases) - 1, 0)
        case_idx = min(int(case_slider.value), max(len(ranked_cases) - 1, 0))
        sync_case_controls(case_idx)
        render_case(case_idx)

    def on_case_dropdown(change: dict[str, Any]) -> None:
        if change["name"] == "value" and change["new"] is not None:
            if case_slider.value != change["new"]:
                case_slider.value = change["new"]
            else:
                render_case(change["new"])

    def on_case_slider(change: dict[str, Any]) -> None:
        if change["name"] == "value":
            if case_dropdown.value != change["new"]:
                case_dropdown.value = change["new"]
            else:
                render_case(change["new"])

    case_dropdown.observe(on_case_dropdown, names="value")
    case_slider.observe(on_case_slider, names="value")
    sort_selector.observe(
        lambda change: update_case_order(change["new"]) if change["name"] == "value" else None,
        names="value",
    )

    display(controls_box)
    render_case(case_dropdown.value)
