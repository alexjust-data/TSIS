from __future__ import annotations

from pathlib import Path
import ast

import ipywidgets as widgets
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, clear_output, display


NY_TZ = "America/New_York"

QUOTES_ROOTS = [
    Path(r"D:\quotes"),
    Path(r"C:\TSIS_Data\data\quotes"),
]

TRADES_ROOTS = [
    Path(r"C:\TSIS_Data\data\trades_ticks_prod_2005_2026"),
    Path(r"D:\trades_ticks_prod_2005_2026"),
]

CASE_LEGEND = {
    "ticker_change_near_quotes_anomaly": (
        "Cambio de ticker de `reference` muy cercano a una anomalia real en `quotes`. "
        "El objetivo es ver si la fragilidad microestructural parece convivir con el cambio "
        "administrativo/corporativo y no solo con ruido aislado."
    ),
    "ticker_change_near_halt": (
        "Cambio de ticker de `reference` muy cercano a un `halt` oficial. Aqui el chart "
        "debe ayudar a ver si el evento de identidad convive con una interrupcion operativa "
        "del mercado."
    ),
    "split_explains_trade_scale_mismatch": (
        "Split de `reference` que encaja con un `scale_suspect` ya detectado en `trades`. "
        "El objetivo es validar si el ratio del split da contexto visual razonable al raw intradia."
    ),
    "split_near_scale_mismatch_review": (
        "Split cercano a un caso `scale_suspect`, pero con timing no lo bastante estrecho para "
        "cerrarlo sin revision manual."
    ),
}


def _parse_list_like(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except Exception:
        pass
    return [text]


def _to_ny_from_quotes_timestamp(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        ts = pd.to_datetime(series, unit="ns", utc=True, errors="coerce")
    else:
        ts = pd.to_datetime(series, utc=True, errors="coerce")
    return ts.dt.tz_convert(NY_TZ).dt.tz_localize(None)


def _to_ny_from_trade_timestamp(series: pd.Series) -> pd.Series:
    ts = pd.to_datetime(series, utc=True, errors="coerce")
    return ts.dt.tz_convert(NY_TZ).dt.tz_localize(None)


def _safe_read_parquet(path: str | Path, columns: list[str]) -> pd.DataFrame:
    p = Path(str(path))
    if not p.exists():
        return pd.DataFrame(columns=columns)
    return pd.read_parquet(p, columns=columns)


def _locate_quotes_file(ticker: str, dt: pd.Timestamp) -> Path | None:
    if pd.isna(dt):
        return None
    ticker = str(ticker).upper()
    year = int(dt.year)
    month = int(dt.month)
    day_num = int(dt.day)
    day_full = dt.strftime("%Y-%m-%d")
    candidates = []
    for root in QUOTES_ROOTS:
        candidates.extend(
            [
                root / ticker / f"year={year}" / f"month={month:02d}" / f"day={day_num:02d}" / "quotes.parquet",
                root / ticker / f"year={year}" / f"month={month:02d}" / f"day={day_full}" / "quotes.parquet",
            ]
        )
    for p in candidates:
        if p.exists():
            return p
    return None


def _locate_trades_file(ticker: str, dt: pd.Timestamp) -> Path | None:
    if pd.isna(dt):
        return None
    ticker = str(ticker).upper()
    year = int(dt.year)
    month = int(dt.month)
    day_full = dt.strftime("%Y-%m-%d")
    candidates = []
    for root in TRADES_ROOTS:
        candidates.append(root / ticker / f"year={year}" / f"month={month:02d}" / f"day={day_full}" / "market.parquet")
    for p in candidates:
        if p.exists():
            return p
    return None


def _prepare_quotes_view(file_path: str | Path | None) -> pd.DataFrame:
    cols = ["timestamp", "bid_price", "ask_price", "bid_size", "ask_size", "bid_exchange", "ask_exchange"]
    if file_path is None:
        return pd.DataFrame(columns=cols + ["timestamp_ny"])
    df = _safe_read_parquet(file_path, cols)
    if df.empty:
        return df
    df = df.copy()
    df["timestamp_ny"] = _to_ny_from_quotes_timestamp(df["timestamp"])
    df["bid_price"] = pd.to_numeric(df["bid_price"], errors="coerce")
    df["ask_price"] = pd.to_numeric(df["ask_price"], errors="coerce")
    df["mid_price"] = (df["bid_price"] + df["ask_price"]) / 2.0
    df["cross_positive"] = df["bid_price"].gt(df["ask_price"]) & df["ask_price"].gt(0)
    df["spread_bps"] = np.where(
        df["mid_price"].gt(0),
        (df["ask_price"] - df["bid_price"]) / df["mid_price"] * 10000.0,
        np.nan,
    )
    df["cross_gap_bps"] = np.where(
        df["mid_price"].gt(0),
        (df["bid_price"] - df["ask_price"]) / df["mid_price"] * 10000.0,
        np.nan,
    )
    return df.sort_values("timestamp_ny").reset_index(drop=True)


def _prepare_trades_view(file_path: str | Path | None) -> pd.DataFrame:
    cols = ["timestamp", "price", "size", "exchange", "conditions"]
    if file_path is None:
        return pd.DataFrame(columns=cols + ["timestamp_ny"])
    df = _safe_read_parquet(file_path, cols)
    if df.empty:
        return df
    df = df.copy()
    df["timestamp_ny"] = _to_ny_from_trade_timestamp(df["timestamp"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["size"] = pd.to_numeric(df["size"], errors="coerce")
    df["regular_lot"] = df["size"].fillna(0).ge(100)
    return df.sort_values("timestamp_ny").reset_index(drop=True)


def _downsample(df: pd.DataFrame, max_points: int = 30_000) -> pd.DataFrame:
    if df.empty or len(df) <= max_points:
        return df
    step = max(1, int(np.ceil(len(df) / max_points)))
    return df.iloc[::step].copy()


def _clip_intraday(quotes_df: pd.DataFrame, trades_df: pd.DataFrame, pad_minutes: int, full_day: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    if full_day:
        return quotes_df, trades_df
    times = []
    if not quotes_df.empty:
        times.append(quotes_df["timestamp_ny"])
    if not trades_df.empty:
        times.append(trades_df["timestamp_ny"])
    if not times:
        return quotes_df, trades_df
    start = min(s.min() for s in times if not s.empty)
    end = max(s.max() for s in times if not s.empty)
    if pd.isna(start) or pd.isna(end):
        return quotes_df, trades_df
    midpoint = start + (end - start) / 2
    lo = midpoint - pd.Timedelta(minutes=pad_minutes)
    hi = midpoint + pd.Timedelta(minutes=pad_minutes)
    if not quotes_df.empty:
        quotes_df = quotes_df.loc[quotes_df["timestamp_ny"].between(lo, hi)].copy()
    if not trades_df.empty:
        trades_df = trades_df.loc[trades_df["timestamp_ny"].between(lo, hi)].copy()
    return quotes_df, trades_df


def _robust_limits(quotes_df: pd.DataFrame, trades_df: pd.DataFrame) -> tuple[float | None, float | None]:
    vals = []
    for col in ["bid_price", "ask_price"]:
        if not quotes_df.empty and col in quotes_df.columns:
            vals.append(pd.to_numeric(quotes_df[col], errors="coerce"))
    if not trades_df.empty and "price" in trades_df.columns:
        vals.append(pd.to_numeric(trades_df["price"], errors="coerce"))
    if not vals:
        return None, None
    s = pd.concat(vals, ignore_index=True).dropna()
    s = s[s > 0]
    if s.empty:
        return None, None
    q1 = float(s.quantile(0.02))
    q2 = float(s.quantile(0.98))
    spread = max(q2 - q1, q2 * 0.03, 0.02)
    lo = max(0.0, q1 - spread * 0.9)
    hi = q2 + spread * 1.1
    return lo, hi


def _detect_extreme_outlier_clipping(quotes_df: pd.DataFrame, trades_df: pd.DataFrame, lo: float | None, hi: float | None) -> bool:
    if lo is None or hi is None:
        return False
    vals = []
    for col in ["bid_price", "ask_price"]:
        if not quotes_df.empty and col in quotes_df.columns:
            vals.append(pd.to_numeric(quotes_df[col], errors="coerce"))
    if not trades_df.empty and "price" in trades_df.columns:
        vals.append(pd.to_numeric(trades_df["price"], errors="coerce"))
    if not vals:
        return False
    s = pd.concat(vals, ignore_index=True).dropna()
    s = s[s > 0]
    if s.empty:
        return False
    return bool((s > hi * 3.0).any() or (s < max(lo * 0.2, 1e-9)).any())


def _build_timeline_events(row: pd.Series) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    if pd.notna(row.get("event_date")):
        events.append({"ts": pd.Timestamp(row["event_date"]), "label": "reference_event", "color": "#1d4ed8"})
    if pd.notna(row.get("execution_date")):
        events.append({"ts": pd.Timestamp(row["execution_date"]), "label": "split_execution", "color": "#7c3aed"})
    if pd.notna(row.get("trade_date")):
        events.append({"ts": pd.Timestamp(row["trade_date"]), "label": "linked_trade_day", "color": "#b45309"})
    if pd.notna(row.get("date")):
        events.append({"ts": pd.Timestamp(row["date"]), "label": "linked_quotes_day", "color": "#047857"})
    if pd.notna(row.get("halt_date")):
        events.append({"ts": pd.Timestamp(row["halt_date"]), "label": "linked_halt_day", "color": "#b91c1c"})
    uniq = {}
    for item in events:
        key = (item["label"], pd.Timestamp(item["ts"]))
        uniq[key] = item
    return list(uniq.values())


def _timeline_bounds(events: list[dict[str, object]]) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    if not events:
        return None, None
    ts_list = [pd.Timestamp(x["ts"]) for x in events]
    start = min(ts_list) - pd.Timedelta(days=4)
    end = max(ts_list) + pd.Timedelta(days=4)
    return start, end


def _plot_timeline(ax, row: pd.Series) -> None:
    events = _build_timeline_events(row)
    start, end = _timeline_bounds(events)
    if start is None or end is None:
        ax.text(0.5, 0.5, "Sin linea temporal disponible", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
        return
    ax.hlines(0.5, start, end, color="#94a3b8", linewidth=2.0)
    for idx, item in enumerate(events):
        ts = pd.Timestamp(item["ts"])
        color = str(item["color"])
        label = str(item["label"])
        ax.scatter([ts], [0.5], color=color, s=60, zorder=4)
        yoff = 10 + (idx % 3) * 8
        ax.annotate(label, xy=(ts, 0.5), xytext=(0, yoff), textcoords="offset points", ha="center", fontsize=8, color=color)
    ax.set_xlim(start, end)
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([])
    ax.set_title("Linea temporal del caso", fontsize=11)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    for label in ax.get_xticklabels():
        label.set_rotation(20)
        label.set_ha("right")
    ax.grid(axis="x", alpha=0.2)


def _plot_halt_interval(ax, row: pd.Series, ymin: float | None, ymax: float | None) -> None:
    halt_ts = pd.to_datetime(row.get("halt_start_et"), errors="coerce")
    resume_ts = pd.to_datetime(row.get("resume_trade_et"), errors="coerce")
    if pd.isna(halt_ts):
        return
    ax.axvline(halt_ts, color="#b91c1c", linestyle="--", linewidth=1.2, alpha=0.9, label="halt_start_et")
    if pd.notna(resume_ts):
        ax.axvline(resume_ts, color="#15803d", linestyle="--", linewidth=1.2, alpha=0.9, label="resume_trade_et")
        if resume_ts >= halt_ts:
            ax.axvspan(halt_ts, resume_ts, color="#fee2e2", alpha=0.18)
            if ymin is not None and ymax is not None and np.isfinite(ymin) and np.isfinite(ymax):
                y = ymin + (ymax - ymin) * 0.08
                ax.hlines(y=y, xmin=halt_ts, xmax=resume_ts, colors="#7c3aed", linewidth=3.0, alpha=0.9, label="halt interval")


def _case_markdown(row: pd.Series, quotes_path: Path | None, trades_path: Path | None) -> str:
    lines = []
    bucket = str(row.get("viewer_bucket", ""))
    lines.append(f"### {row.get('ticker')} | {bucket}")
    legend = CASE_LEGEND.get(bucket)
    if legend:
        lines.append(legend)
        lines.append("")
    lines.append("**Como leer el grafico**")
    lines.append("")
    lines.append("- `Linea temporal`: coloca en dias el evento de `reference` y el dia de mercado enlazado.")
    lines.append("- `Quotes`: libro `bid/ask` del dia enlazado. Si hay `crossed`, suele verse como compresion rara o gap anomalo.")
    lines.append("- `Trades`: prints reales del dia enlazado. Sirve para ver si el tape acompana o contradice a `quotes`.")
    lines.append("- `Diagnostico`: `spread_bps`, `cross_gap_bps` y `trades/min` para cuantificar si el caso es fragil o limpio.")
    lines.append("")
    lines.append("| campo | valor |")
    lines.append("|---|---|")
    for key in [
        "event_type",
        "event_date",
        "execution_date",
        "date",
        "trade_date",
        "halt_date",
        "event_quotes_timing_bucket",
        "event_halt_timing_bucket",
        "split_timing_bucket",
        "severity",
        "reference_quotes_bucket",
        "reference_halt_bucket",
        "reference_market_bucket",
        "m.crossed_ratio_pct",
        "m.crossed_rows",
        "split_ratio",
        "final_bucket",
    ]:
        if key in row.index and pd.notna(row.get(key)):
            lines.append(f"| `{key}` | `{row.get(key)}` |")
    if quotes_path is not None:
        lines.append(f"| `quotes_file` | `{quotes_path}` |")
    if trades_path is not None:
        lines.append(f"| `trades_file` | `{trades_path}` |")
    warns = _parse_list_like(row.get("warns_list"))
    issues = _parse_list_like(row.get("issues_list"))
    if warns:
        lines.append(f"| `warns_list` | `{', '.join(warns[:8])}` |")
    if issues:
        lines.append(f"| `issues_list` | `{', '.join(issues[:8])}` |")
    return "\n".join(lines)


def _visible_window_text(quotes_df: pd.DataFrame, trades_df: pd.DataFrame) -> str | None:
    pools = []
    if not quotes_df.empty:
        pools.append(quotes_df["timestamp_ny"])
    if not trades_df.empty:
        pools.append(trades_df["timestamp_ny"])
    if not pools:
        return None
    start = min(s.min() for s in pools if not s.empty)
    end = max(s.max() for s in pools if not s.empty)
    if pd.isna(start) or pd.isna(end):
        return None
    return f"Ventana visible NY: `{start.strftime('%H:%M')}` -> `{end.strftime('%H:%M')}`"


def _render_case(row: pd.Series, pad_minutes: int = 90, full_day: bool = False) -> None:
    market_date = pd.to_datetime(row.get("date"), errors="coerce")
    if pd.isna(market_date):
        market_date = pd.to_datetime(row.get("trade_date"), errors="coerce")
    if pd.isna(market_date):
        market_date = pd.to_datetime(row.get("halt_date"), errors="coerce")

    quotes_path = None
    if pd.notna(market_date):
        quotes_path = _locate_quotes_file(str(row.get("ticker")), pd.Timestamp(market_date))

    trades_path = None
    if pd.notna(row.get("file")):
        p = Path(str(row.get("file")))
        if p.exists():
            trades_path = p
    if trades_path is None and pd.notna(market_date):
        trades_path = _locate_trades_file(str(row.get("ticker")), pd.Timestamp(market_date))

    quotes_df = _downsample(_prepare_quotes_view(quotes_path))
    trades_df = _downsample(_prepare_trades_view(trades_path))
    quotes_df, trades_df = _clip_intraday(quotes_df, trades_df, pad_minutes=pad_minutes, full_day=full_day)

    display(Markdown(_case_markdown(row, quotes_path, trades_path)))
    window_text = _visible_window_text(quotes_df, trades_df)
    if window_text:
        display(Markdown(window_text))

    fig = plt.figure(figsize=(16, 11.8))
    gs = fig.add_gridspec(4, 1, height_ratios=[0.9, 2.5, 2.1, 1.5], hspace=0.14)
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[2, 0], sharex=ax1)
    ax3 = fig.add_subplot(gs[3, 0], sharex=ax1)

    _plot_timeline(ax0, row)
    ax0.tick_params(axis="x", labelbottom=False)

    if not quotes_df.empty:
        ax1.step(quotes_df["timestamp_ny"], quotes_df["bid_price"], where="post", color="#0f766e", linewidth=1.2, label="bid_price")
        ax1.step(quotes_df["timestamp_ny"], quotes_df["ask_price"], where="post", color="#dc2626", linewidth=1.2, label="ask_price")
        crossed = quotes_df.loc[quotes_df["cross_positive"]]
        if not crossed.empty:
            ax1.scatter(crossed["timestamp_ny"], crossed["ask_price"], s=14, color="#f59e0b", alpha=0.8, label="crossed ask")
    else:
        ax1.text(0.5, 0.5, "Sin raw quotes disponible", ha="center", va="center", transform=ax1.transAxes)
    lo, hi = _robust_limits(quotes_df, trades_df)
    clipped_by_outliers = _detect_extreme_outlier_clipping(quotes_df, trades_df, lo, hi)
    if lo is not None and hi is not None:
        ax1.set_ylim(lo, hi)
    _plot_halt_interval(ax1, row, lo, hi)
    ax1.set_ylabel("price")
    ax1.legend(loc="upper left")
    ax1.grid(alpha=0.25)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.tick_params(axis="x", labelbottom=True)
    for label in ax1.get_xticklabels():
        label.set_rotation(0)
        label.set_ha("center")
    if clipped_by_outliers:
        ax1.text(
            0.99,
            0.98,
            "axis clipped by extreme outliers",
            transform=ax1.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            color="#b91c1c",
            bbox={"facecolor": "#fee2e2", "edgecolor": "#fecaca", "boxstyle": "round,pad=0.2"},
        )

    if not trades_df.empty:
        reg = trades_df.loc[trades_df["regular_lot"]]
        odd = trades_df.loc[~trades_df["regular_lot"]]
        if not reg.empty:
            ax2.scatter(reg["timestamp_ny"], reg["price"], s=12, color="#2563eb", alpha=0.85, label="round_lot >= 100")
        if not odd.empty:
            ax2.scatter(odd["timestamp_ny"], odd["price"], s=12, color="#f97316", alpha=0.75, label="odd_lot < 100")
    else:
        ax2.text(0.5, 0.5, "Sin raw trades disponible", ha="center", va="center", transform=ax2.transAxes)
    _plot_halt_interval(ax2, row, lo, hi)
    if lo is not None and hi is not None:
        ax2.set_ylim(lo, hi)
    ax2.set_ylabel("trade price")
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.25)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax2.tick_params(axis="x", labelbottom=True)
    for label in ax2.get_xticklabels():
        label.set_rotation(0)
        label.set_ha("center")

    if not quotes_df.empty:
        ax3.plot(quotes_df["timestamp_ny"], quotes_df["spread_bps"], color="#94a3b8", linewidth=1.0, label="spread_bps")
        cross_only = quotes_df.loc[quotes_df["cross_positive"] & quotes_df["cross_gap_bps"].notna()]
        if not cross_only.empty:
            ax3.scatter(cross_only["timestamp_ny"], cross_only["cross_gap_bps"], s=12, color="#ef4444", alpha=0.85, label="cross_gap_bps")
    if not trades_df.empty:
        trades_per_min = (
            trades_df.set_index("timestamp_ny")["price"]
            .resample("1min")
            .count()
            .rename("trades_per_min")
            .reset_index()
        )
        ax3b = ax3.twinx()
        ax3b.plot(trades_per_min["timestamp_ny"], trades_per_min["trades_per_min"], color="#10b981", linewidth=1.0, label="trades_per_min")
        ax3b.set_ylabel("trades/min", color="#059669")
        ax3b.tick_params(axis="y", colors="#059669")
    _plot_halt_interval(ax3, row, None, None)
    ax3.set_ylabel("bps")
    ax3.grid(alpha=0.25)
    ax3.legend(loc="upper left")
    ax3.set_xlabel("timestamp NY")
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    title_dt = market_date.date().isoformat() if pd.notna(market_date) else "no_market_date"
    fig.suptitle(f"{row.get('ticker')} | {title_dt} | {row.get('viewer_bucket')}", y=0.98, fontsize=14)
    fig.subplots_adjust(top=0.93, bottom=0.07)
    plt.show()


def build_reference_visual_case_index(
    event_quotes_df: pd.DataFrame,
    event_halts_df: pd.DataFrame,
    split_market_df: pd.DataFrame,
) -> pd.DataFrame:
    frames = []

    if not event_quotes_df.empty:
        eq = event_quotes_df.loc[event_quotes_df["reference_quotes_bucket"].isin(["ticker_change_near_quotes_anomaly"])].copy()
        if not eq.empty:
            eq["viewer_bucket"] = eq["reference_quotes_bucket"]
            eq["sort_score"] = np.where(eq["severity"].eq("HARD_FAIL"), 2, 1)
            eq["sort_aux"] = pd.to_numeric(eq["m.crossed_ratio_pct"], errors="coerce").fillna(0.0)
            eq["market_date"] = pd.to_datetime(eq["date"], errors="coerce")
            eq["visual_key"] = (
                "quotes|"
                + eq["ticker"].astype("string")
                + "|"
                + pd.to_datetime(eq["event_date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("na")
            )
            frames.append(eq)

    if not event_halts_df.empty:
        eh = event_halts_df.loc[event_halts_df["reference_halt_bucket"].isin(["ticker_change_near_halt"])].copy()
        if not eh.empty:
            eh["viewer_bucket"] = eh["reference_halt_bucket"]
            eh["sort_score"] = np.where(eh["event_halt_timing_bucket"].eq("same_day"), 2, 1)
            eh["sort_aux"] = -pd.to_numeric(eh["abs_days_event_to_halt"], errors="coerce").fillna(99)
            eh["market_date"] = pd.to_datetime(eh["halt_date"], errors="coerce")
            eh["visual_key"] = (
                "halt|"
                + eh["ticker"].astype("string")
                + "|"
                + pd.to_datetime(eh["event_date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("na")
            )
            frames.append(eh)

    if not split_market_df.empty:
        sm = split_market_df.loc[
            split_market_df["reference_market_bucket"].isin(["split_explains_trade_scale_mismatch", "split_near_scale_mismatch_review"])
        ].copy()
        if not sm.empty:
            sm["viewer_bucket"] = sm["reference_market_bucket"]
            sm["sort_score"] = np.where(sm["reference_market_bucket"].eq("split_explains_trade_scale_mismatch"), 2, 1)
            sm["sort_aux"] = pd.to_numeric(sm["m.possible_price_scale_factor_vs_1m"], errors="coerce").fillna(0.0)
            sm["market_date"] = pd.to_datetime(sm["trade_date"], errors="coerce")
            sm["event_date"] = pd.to_datetime(sm["execution_date"], errors="coerce")
            sm["visual_key"] = (
                "split|"
                + sm["ticker"].astype("string")
                + "|"
                + pd.to_datetime(sm["execution_date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("na")
            )
            frames.append(sm)

    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True, sort=False)
    out = out.sort_values(["viewer_bucket", "sort_score", "sort_aux"], ascending=[True, False, False]).drop_duplicates("visual_key")
    return out.reset_index(drop=True)


def render_reference_causal_overlay_widget(
    event_quotes_df: pd.DataFrame,
    event_halts_df: pd.DataFrame,
    split_market_df: pd.DataFrame,
) -> pd.DataFrame:
    cases = build_reference_visual_case_index(event_quotes_df, event_halts_df, split_market_df)
    if cases.empty:
        display(Markdown("No hay casos visuales de `reference` disponibles."))
        return cases

    bucket_options = ["all"] + sorted(cases["viewer_bucket"].dropna().astype(str).unique().tolist())
    bucket_dropdown = widgets.Dropdown(options=bucket_options, value="all", description="bucket")
    pad_slider = widgets.IntSlider(value=120, min=30, max=240, step=15, description="pad min")
    full_day_toggle = widgets.Checkbox(value=True, description="full day")
    search_box = widgets.Text(value="", description="buscar")
    case_dropdown = widgets.Dropdown(description="caso")
    out = widgets.Output()

    state = {"refreshing": False}

    def _filtered() -> pd.DataFrame:
        df = cases.copy()
        if bucket_dropdown.value != "all":
            df = df.loc[df["viewer_bucket"].eq(bucket_dropdown.value)].copy()
        query = search_box.value.strip().upper()
        if query:
            df = df.loc[df["ticker"].astype("string").str.contains(query, na=False)].copy()
        return df.sort_values(["viewer_bucket", "sort_score", "sort_aux"], ascending=[True, False, False]).reset_index(drop=True)

    def _refresh_cases(*_):
        state["refreshing"] = True
        df = _filtered()
        options = []
        for _, row in df.head(400).iterrows():
            label = (
                f"{row.get('ticker')} | {pd.to_datetime(row.get('event_date'), errors='coerce').date()} | "
                f"{row.get('viewer_bucket')} | "
                f"mkt={pd.to_datetime(row.get('market_date'), errors='coerce').date() if pd.notna(pd.to_datetime(row.get('market_date'), errors='coerce')) else 'na'}"
            )
            options.append((label, str(row["visual_key"])))
        case_dropdown.options = options
        case_dropdown.value = options[0][1] if options else None
        state["refreshing"] = False
        _render()

    def _render(*_):
        if state["refreshing"]:
            return
        key = case_dropdown.value
        with out:
            clear_output(wait=True)
            if not key:
                display(Markdown("No hay casos que coincidan con el filtro."))
                return
            row = cases.loc[cases["visual_key"].eq(key)]
            if row.empty:
                display(Markdown("Caso no encontrado."))
                return
            _render_case(row.iloc[0], pad_minutes=int(pad_slider.value), full_day=bool(full_day_toggle.value))

    bucket_dropdown.observe(_refresh_cases, names="value")
    search_box.observe(_refresh_cases, names="value")
    case_dropdown.observe(_render, names="value")
    pad_slider.observe(_render, names="value")
    full_day_toggle.observe(_render, names="value")

    controls = widgets.VBox(
        [
            widgets.HBox([bucket_dropdown, search_box]),
            widgets.HBox([case_dropdown]),
            widgets.HBox([pad_slider, full_day_toggle]),
        ]
    )
    display(controls, out)
    _refresh_cases()
    return cases
