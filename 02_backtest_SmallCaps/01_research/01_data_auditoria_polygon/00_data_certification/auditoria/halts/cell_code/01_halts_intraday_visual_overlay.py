from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import Markdown, display, clear_output


NY_TZ = "America/New_York"

BUCKET_LEGEND = {
    "confirmed_halt_microstructure_coherent": (
        "Evento de halt oficial con reaccion microestructural coherente en `quotes` y/o "
        "`trades` cerca del halt o del reopen."
    ),
    "halt_with_quotes_signal_only": (
        "El halt oficial existe y `quotes` dejan senal util, pero `trades` no confirman "
        "con la misma claridad."
    ),
    "halt_with_trades_signal_only": (
        "El halt oficial existe y `trades` dejan senal util, pero `quotes` no confirman "
        "con la misma claridad."
    ),
    "halt_present_but_market_clean": (
        "Hay halt oficial, pero el raw visual disponible no muestra anomalia clara en mercado."
    ),
    "market_signal_without_clear_halt_window": (
        "La senal de mercado existe, pero no queda alineada de forma limpia con la ventana "
        "temporal del halt."
    ),
    "review_timestamp_alignment": (
        "El caso necesita revisar tiempos antes de concluir nada: timezone, fecha efectiva, "
        "`resume_trade_et` o granularidad del source."
    ),
}


def _parse_marker_list(value: object) -> list[pd.Timestamp]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    parts = [x.strip() for x in text.split("|") if x.strip()]
    out: list[pd.Timestamp] = []
    for part in parts:
        ts = pd.to_datetime(part, errors="coerce")
        if pd.notna(ts):
            out.append(ts)
    out = sorted(pd.Series(out).dropna().drop_duplicates().tolist())
    return out


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
    target = Path(str(path))
    if not target.exists():
        return pd.DataFrame(columns=columns)
    return pd.read_parquet(target, columns=columns)


def _prepare_quotes_view(file_path: str | Path) -> pd.DataFrame:
    cols = [
        "timestamp",
        "bid_price",
        "ask_price",
        "bid_size",
        "ask_size",
        "bid_exchange",
        "ask_exchange",
    ]
    df = _safe_read_parquet(file_path, cols)
    if df.empty:
        return df
    df = df.copy()
    df["timestamp_ny"] = _to_ny_from_quotes_timestamp(df["timestamp"])
    df["bid_price"] = pd.to_numeric(df["bid_price"], errors="coerce")
    df["ask_price"] = pd.to_numeric(df["ask_price"], errors="coerce")
    df["bid_size"] = pd.to_numeric(df["bid_size"], errors="coerce")
    df["ask_size"] = pd.to_numeric(df["ask_size"], errors="coerce")
    df["cross_positive"] = df["bid_price"].gt(df["ask_price"]) & df["ask_price"].gt(0)
    df["mid_price"] = (df["bid_price"] + df["ask_price"]) / 2.0
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
    df = df.sort_values("timestamp_ny").reset_index(drop=True)
    return df


def _prepare_trades_view(file_path: str | Path) -> pd.DataFrame:
    cols = ["timestamp", "price", "size", "exchange", "conditions"]
    df = _safe_read_parquet(file_path, cols)
    if df.empty:
        return df
    df = df.copy()
    df["timestamp_ny"] = _to_ny_from_trade_timestamp(df["timestamp"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["size"] = pd.to_numeric(df["size"], errors="coerce")
    df["regular_lot"] = df["size"].fillna(0).ge(100)
    df = df.sort_values("timestamp_ny").reset_index(drop=True)
    return df


def _clip_to_window(
    quotes_df: pd.DataFrame,
    trades_df: pd.DataFrame,
    halt_markers: list[pd.Timestamp],
    resume_markers: list[pd.Timestamp],
    pad_minutes: int = 20,
    show_full_day: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp | None, pd.Timestamp | None]:
    if show_full_day:
        start = None
        end = None
    else:
        anchors = halt_markers + resume_markers
        anchors = [x for x in anchors if pd.notna(x)]
        if anchors:
            start = min(anchors) - pd.Timedelta(minutes=pad_minutes)
            end = max(anchors) + pd.Timedelta(minutes=pad_minutes)
        else:
            start = None
            end = None

    if start is not None and end is not None:
        if not quotes_df.empty:
            quotes_df = quotes_df.loc[quotes_df["timestamp_ny"].between(start, end)].copy()
        if not trades_df.empty:
            trades_df = trades_df.loc[trades_df["timestamp_ny"].between(start, end)].copy()

    if start is None or end is None:
        series_pool = []
        if not quotes_df.empty:
            series_pool.append(quotes_df["timestamp_ny"])
        if not trades_df.empty:
            series_pool.append(trades_df["timestamp_ny"])
        if series_pool:
            start = min(s.min() for s in series_pool if not s.empty)
            end = max(s.max() for s in series_pool if not s.empty)
        else:
            start = None
            end = None
    return quotes_df, trades_df, start, end


def _downsample(df: pd.DataFrame, max_points: int = 25_000) -> pd.DataFrame:
    if df.empty or len(df) <= max_points:
        return df
    step = max(1, int(np.ceil(len(df) / max_points)))
    return df.iloc[::step].copy()


def _plot_marker_lines(ax, halt_markers: list[pd.Timestamp], resume_markers: list[pd.Timestamp]) -> None:
    first_halt = True
    first_resume = True
    for ts in halt_markers:
        ax.axvline(ts, color="#b91c1c", linestyle="--", linewidth=1.2, alpha=0.9, label="halt_start_et" if first_halt else None)
        first_halt = False
    for ts in resume_markers:
        ax.axvline(ts, color="#15803d", linestyle="--", linewidth=1.2, alpha=0.9, label="resume_trade_et" if first_resume else None)
        first_resume = False
    for halt_ts, resume_ts in zip(halt_markers, resume_markers):
        if pd.notna(halt_ts) and pd.notna(resume_ts) and resume_ts >= halt_ts:
            ax.axvspan(halt_ts, resume_ts, color="#fee2e2", alpha=0.18)


def _infer_halt_anchor_price(
    halt_ts: pd.Timestamp,
    quotes_df: pd.DataFrame,
    trades_df: pd.DataFrame,
) -> float | None:
    if pd.isna(halt_ts):
        return None

    if not quotes_df.empty:
        q = quotes_df.loc[quotes_df["timestamp_ny"].le(halt_ts)].copy()
        if not q.empty:
            last_q = q.iloc[-1]
            mid = last_q.get("mid_price")
            if pd.notna(mid) and float(mid) > 0:
                return float(mid)
            bid = last_q.get("bid_price")
            ask = last_q.get("ask_price")
            if pd.notna(bid) and float(bid) > 0:
                return float(bid)
            if pd.notna(ask) and float(ask) > 0:
                return float(ask)

    if not trades_df.empty:
        t = trades_df.loc[trades_df["timestamp_ny"].le(halt_ts)].copy()
        if not t.empty:
            price = t.iloc[-1].get("price")
            if pd.notna(price) and float(price) > 0:
                return float(price)
    return None


def _draw_halt_price_segments(
    ax,
    halt_markers: list[pd.Timestamp],
    resume_markers: list[pd.Timestamp],
    quotes_df: pd.DataFrame,
    trades_df: pd.DataFrame,
) -> None:
    used_label = False
    for idx, halt_ts in enumerate(halt_markers):
        resume_ts = resume_markers[idx] if idx < len(resume_markers) else pd.NaT
        if pd.isna(halt_ts) or pd.isna(resume_ts) or resume_ts < halt_ts:
            continue
        anchor_price = _infer_halt_anchor_price(halt_ts, quotes_df=quotes_df, trades_df=trades_df)
        if anchor_price is None or not np.isfinite(anchor_price):
            continue
        ax.hlines(
            y=anchor_price,
            xmin=halt_ts,
            xmax=resume_ts,
            colors="#7c3aed",
            linewidth=3.0,
            alpha=0.9,
            label="halt interval @ anchor price" if not used_label else None,
            zorder=6,
        )
        mid_ts = halt_ts + (resume_ts - halt_ts) / 2
        ax.annotate(
            f"H{idx + 1}",
            xy=(mid_ts, anchor_price),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#5b21b6",
            zorder=7,
        )
        used_label = True


def _robust_price_limits(quotes_df: pd.DataFrame, trades_df: pd.DataFrame) -> tuple[float | None, float | None]:
    values: list[pd.Series] = []
    if not quotes_df.empty:
        for col in ["bid_price", "ask_price", "mid_price"]:
            if col in quotes_df.columns:
                values.append(pd.to_numeric(quotes_df[col], errors="coerce"))
    if not trades_df.empty and "price" in trades_df.columns:
        values.append(pd.to_numeric(trades_df["price"], errors="coerce"))
    if not values:
        return None, None
    all_values = pd.concat(values, ignore_index=True).replace([np.inf, -np.inf], np.nan).dropna()
    all_values = all_values.loc[all_values.gt(0)]
    if all_values.empty:
        return None, None
    lo = float(all_values.quantile(0.02))
    hi = float(all_values.quantile(0.98))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return None, None
    pad = max((hi - lo) * 0.08, 0.01)
    return max(0.0, lo - pad), hi + pad


def _context_price_limits(
    quotes_df: pd.DataFrame,
    trades_df: pd.DataFrame,
    halt_markers: list[pd.Timestamp],
    resume_markers: list[pd.Timestamp],
) -> tuple[float | None, float | None]:
    values: list[pd.Series] = []
    if not quotes_df.empty:
        for col in ["bid_price", "ask_price", "mid_price"]:
            if col in quotes_df.columns:
                values.append(pd.to_numeric(quotes_df[col], errors="coerce"))
    if not trades_df.empty and "price" in trades_df.columns:
        values.append(pd.to_numeric(trades_df["price"], errors="coerce"))
    if not values:
        return None, None
    all_values = pd.concat(values, ignore_index=True).replace([np.inf, -np.inf], np.nan).dropna()
    all_values = all_values.loc[all_values.gt(0)]
    if all_values.empty:
        return None, None

    median_val = float(all_values.median())
    if not np.isfinite(median_val) or median_val <= 0:
        return _robust_price_limits(quotes_df=quotes_df, trades_df=trades_df)

    focus = all_values.loc[all_values.between(median_val / 4.0, median_val * 4.0)]
    if focus.empty:
        focus = all_values

    lo = float(focus.quantile(0.01))
    hi = float(focus.quantile(0.99))

    anchor_prices: list[float] = []
    for halt_ts in halt_markers:
        anchor = _infer_halt_anchor_price(halt_ts, quotes_df=quotes_df, trades_df=trades_df)
        if anchor is not None and np.isfinite(anchor) and anchor > 0:
            anchor_prices.append(float(anchor))
    if anchor_prices:
        lo = min(lo, float(np.nanmin(anchor_prices)))
        hi = max(hi, float(np.nanmax(anchor_prices)))

    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return _robust_price_limits(quotes_df=quotes_df, trades_df=trades_df)

    pad = max((hi - lo) * 0.25, max(0.03, median_val * 0.03))
    return max(0.0, lo - pad), hi + pad


def _interval_summary_frame(halt_markers: list[pd.Timestamp], resume_markers: list[pd.Timestamp]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for idx, halt_ts in enumerate(halt_markers):
        resume_ts = resume_markers[idx] if idx < len(resume_markers) else pd.NaT
        duration_min = None
        if pd.notna(halt_ts) and pd.notna(resume_ts) and resume_ts >= halt_ts:
            duration_min = round((resume_ts - halt_ts).total_seconds() / 60.0, 2)
        rows.append(
            {
                "halt_n": idx + 1,
                "halt_start_et": halt_ts,
                "resume_trade_et": resume_ts if pd.notna(resume_ts) else pd.NaT,
                "duration_min": duration_min,
            }
        )
    return pd.DataFrame(rows)


def _case_summary_frame(case_row: pd.Series, quotes_df: pd.DataFrame, trades_df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticker": case_row.get("ticker"),
                "visual_date": case_row.get("visual_date"),
                "bucket": case_row.get("visual_case_bucket"),
                "events_in_visual": case_row.get("events_in_visual"),
                "halt_markers": case_row.get("halt_markers_count"),
                "resume_markers": case_row.get("resume_markers_count"),
                "quotes_rows": int(len(quotes_df)),
                "trades_rows": int(len(trades_df)),
                "quotes_link_strength": case_row.get("quotes_link_strength"),
                "trades_link_strength": case_row.get("trades_link_strength"),
            }
        ]
    )


def render_visual_case(
    case_row: pd.Series,
    pad_minutes: int = 90,
    show_full_day: bool = False,
    max_points: int = 25_000,
) -> None:
    bucket = str(case_row.get("visual_case_bucket", ""))
    legend = BUCKET_LEGEND.get(bucket, "Bucket sin leyenda registrada.")
    display(Markdown(f"**{bucket}**  \n{legend}"))

    quotes_df = _prepare_quotes_view(case_row.get("quotes_file_visual"))
    trades_df = _prepare_trades_view(case_row.get("trades_file_visual"))
    halt_markers = _parse_marker_list(case_row.get("halt_markers_et"))
    resume_markers = _parse_marker_list(case_row.get("resume_markers_et"))
    quotes_df, trades_df, start, end = _clip_to_window(
        quotes_df=quotes_df,
        trades_df=trades_df,
        halt_markers=halt_markers,
        resume_markers=resume_markers,
        pad_minutes=pad_minutes,
        show_full_day=show_full_day,
    )
    quotes_df = _downsample(quotes_df, max_points=max_points)
    trades_df = _downsample(trades_df, max_points=max_points)

    display(_case_summary_frame(case_row, quotes_df, trades_df))
    if halt_markers:
        display(Markdown("**Intervalos oficiales del halt en esta vista**"))
        display(_interval_summary_frame(halt_markers, resume_markers))

    if quotes_df.empty and trades_df.empty:
        display(Markdown("No hay raw intradia disponible para este `visual_key`."))
        return

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(16, 11),
        sharex=True,
        gridspec_kw={"height_ratios": [2.4, 1.6, 1.1]},
    )

    if not quotes_df.empty:
        axes[0].step(
            quotes_df["timestamp_ny"],
            quotes_df["bid_price"],
            where="post",
            color="#0f766e",
            linewidth=1.15,
            alpha=0.95,
            label="bid_price",
        )
        axes[0].step(
            quotes_df["timestamp_ny"],
            quotes_df["ask_price"],
            where="post",
            color="#b91c1c",
            linewidth=1.15,
            alpha=0.95,
            label="ask_price",
        )
        crossed = quotes_df.loc[quotes_df["cross_positive"]].copy()
        if not crossed.empty:
            axes[0].scatter(
                crossed["timestamp_ny"],
                crossed["ask_price"],
                s=20,
                color="#f59e0b",
                alpha=0.85,
                label="crossed bid > ask > 0",
            )
        _draw_halt_price_segments(axes[0], halt_markers=halt_markers, resume_markers=resume_markers, quotes_df=quotes_df, trades_df=trades_df)
        axes[0].set_ylabel("price")
        axes[0].legend(loc="upper left")
    else:
        axes[0].text(0.5, 0.5, "Sin raw de quotes", ha="center", va="center", transform=axes[0].transAxes)
        axes[0].set_ylabel("price")

    if not trades_df.empty:
        trade_sizes = trades_df["size"].fillna(0).clip(lower=1)
        marker_sizes = np.clip(np.sqrt(trade_sizes) * 2.5, 12, 80)
        colors = np.where(trades_df["regular_lot"], "#2563eb", "#f97316")
        axes[1].scatter(
            trades_df["timestamp_ny"],
            trades_df["price"],
            s=marker_sizes,
            c=colors,
            alpha=0.65,
            edgecolors="none",
            label="trades",
        )
        axes[1].set_ylabel("trade price")
        axes[1].scatter([], [], s=35, color="#2563eb", label="round_lot >= 100")
        axes[1].scatter([], [], s=35, color="#f97316", label="odd_lot < 100")
        _draw_halt_price_segments(axes[1], halt_markers=halt_markers, resume_markers=resume_markers, quotes_df=quotes_df, trades_df=trades_df)
        axes[1].legend(loc="upper left")
    else:
        axes[1].text(0.5, 0.5, "Sin raw de trades", ha="center", va="center", transform=axes[1].transAxes)
        axes[1].set_ylabel("trade price")

    if not quotes_df.empty:
        gap = quotes_df.loc[quotes_df["cross_positive"]].copy()
        if not gap.empty:
            axes[2].scatter(gap["timestamp_ny"], gap["cross_gap_bps"], s=18, color="#dc2626", alpha=0.85, label="cross_gap_bps")
        spread = quotes_df.loc[quotes_df["spread_bps"].notna(), ["timestamp_ny", "spread_bps"]].copy()
        if not spread.empty:
            axes[2].plot(spread["timestamp_ny"], spread["spread_bps"], color="#64748b", linewidth=0.8, alpha=0.7, label="spread_bps")
    trade_count_ax = axes[2].twinx()
    if not trades_df.empty:
        minute_counts = (
            trades_df.assign(minute=trades_df["timestamp_ny"].dt.floor("min"))
            .groupby("minute", as_index=False)
            .agg(trades=("price", "size"))
        )
        if not minute_counts.empty:
            trade_count_ax.plot(minute_counts["minute"], minute_counts["trades"], color="#10b981", linewidth=1.0, alpha=0.75, label="trades_per_min")
            trade_count_ax.set_ylabel("trades/min", color="#10b981")
            trade_count_ax.tick_params(axis="y", labelcolor="#10b981")

    axes[2].axhline(0, color="black", linewidth=0.8, alpha=0.5)
    axes[2].set_ylabel("bps")
    handles_left, labels_left = axes[2].get_legend_handles_labels()
    handles_right, labels_right = trade_count_ax.get_legend_handles_labels()
    if handles_left or handles_right:
        axes[2].legend(handles_left + handles_right, labels_left + labels_right, loc="upper left")

    for ax in axes:
        _plot_marker_lines(ax, halt_markers=halt_markers, resume_markers=resume_markers)
        if start is not None and end is not None:
            ax.set_xlim(start, end)

    y0_lo, y0_hi = _context_price_limits(
        quotes_df=quotes_df,
        trades_df=trades_df,
        halt_markers=halt_markers,
        resume_markers=resume_markers,
    )
    if y0_lo is not None and y0_hi is not None:
        axes[0].set_ylim(y0_lo, y0_hi)
        axes[1].set_ylim(y0_lo, y0_hi)

    fig.suptitle(
        f"{case_row.get('ticker')} | {case_row.get('visual_date')} | {bucket} | events={case_row.get('events_in_visual')}",
        y=0.98,
    )
    axes[2].set_xlabel("timestamp NY")
    plt.tight_layout()
    plt.show()


def build_intraday_overlay_widget(cases_df: pd.DataFrame) -> widgets.VBox:
    work = cases_df.copy()
    if work.empty:
        return widgets.VBox([widgets.HTML("<b>No hay casos visuales materializados.</b>")])

    work["display_option"] = (
        work["display_label"].astype("string")
        + " | events="
        + work["events_in_visual"].astype("Int64").astype("string")
        + " | rank="
        + work["rank_score"].astype("Int64").astype("string")
    )
    work = work.sort_values(["visual_case_bucket", "rank_score", "ticker", "visual_date"], ascending=[True, False, True, True]).reset_index(drop=True)

    bucket_options = ["all"] + sorted(work["visual_case_bucket"].dropna().astype(str).unique().tolist())
    bucket_dropdown = widgets.Dropdown(options=bucket_options, value="all", description="bucket", layout=widgets.Layout(width="360px"))
    only_problem_toggle = widgets.Checkbox(value=False, description="solo problem")
    show_full_day_toggle = widgets.Checkbox(value=False, description="full day")
    pad_slider = widgets.IntSlider(value=90, min=15, max=240, step=5, description="pad min", layout=widgets.Layout(width="320px"))
    max_points_slider = widgets.IntSlider(value=25000, min=2000, max=50000, step=1000, description="max pts", layout=widgets.Layout(width="320px"))
    search_box = widgets.Text(value="", description="search", placeholder="ticker o fecha", layout=widgets.Layout(width="320px"))
    case_dropdown = widgets.Dropdown(description="case", layout=widgets.Layout(width="1200px"))
    out = widgets.Output()
    render_state = {"suspend": False}

    def _filtered_cases() -> pd.DataFrame:
        subset = work.copy()
        if bucket_dropdown.value != "all":
            subset = subset.loc[subset["visual_case_bucket"].astype(str) == str(bucket_dropdown.value)].copy()
        if only_problem_toggle.value:
            subset = subset.loc[
                subset["quotes_problem_flag"].fillna(False).astype(bool)
                | subset["trades_problem_flag"].fillna(False).astype(bool)
            ].copy()
        text = search_box.value.strip().lower()
        if text:
            mask = pd.Series(False, index=subset.index)
            for col in ["ticker", "display_label", "visual_date", "visual_case_bucket", "event_ids_in_visual"]:
                mask = mask | subset[col].astype("string").str.lower().str.contains(text, na=False)
            subset = subset.loc[mask].copy()
        subset = subset.sort_values(["rank_score", "events_in_visual", "ticker", "visual_date"], ascending=[False, False, True, True])
        return subset.reset_index(drop=True)

    def _refresh_cases(*_):
        render_state["suspend"] = True
        subset = _filtered_cases()
        if subset.empty:
            case_dropdown.options = [("sin casos", None)]
            case_dropdown.value = None
            case_dropdown._subset = subset
            render_state["suspend"] = False
            return
        options = [(row["display_option"], idx) for idx, row in subset.iterrows()]
        current_value = case_dropdown.value
        case_dropdown.options = options
        case_dropdown._subset = subset
        valid_values = {value for _, value in options}
        if current_value in valid_values:
            case_dropdown.value = current_value
        else:
            case_dropdown.value = options[0][1]
        render_state["suspend"] = False
        _render_case()

    def _render_case(*_):
        if render_state["suspend"]:
            return
        with out:
            clear_output(wait=True)
            subset = getattr(case_dropdown, "_subset", _filtered_cases())
            if case_dropdown.value is None or subset.empty:
                display(Markdown("No hay casos para el filtro actual."))
                return
            row = subset.iloc[int(case_dropdown.value)]
            display(
                Markdown(
                    "**Viewer `<1B>` deduplicado por `visual_key`**  \n"
                    "Cada opcion representa una sola vista fisica `ticker-day`, aunque ese dia agregue multiples halts."
                )
            )
            render_visual_case(
                row,
                pad_minutes=int(pad_slider.value),
                show_full_day=bool(show_full_day_toggle.value),
                max_points=int(max_points_slider.value),
            )

    for control in [bucket_dropdown, only_problem_toggle, search_box]:
        control.observe(_refresh_cases, names="value")
    for control in [case_dropdown, show_full_day_toggle, pad_slider, max_points_slider]:
        control.observe(_render_case, names="value")

    _refresh_cases()
    ui = widgets.VBox(
        [
            widgets.HBox([bucket_dropdown, only_problem_toggle, show_full_day_toggle]),
            widgets.HBox([pad_slider, max_points_slider, search_box]),
            case_dropdown,
            out,
        ]
    )
    return ui
