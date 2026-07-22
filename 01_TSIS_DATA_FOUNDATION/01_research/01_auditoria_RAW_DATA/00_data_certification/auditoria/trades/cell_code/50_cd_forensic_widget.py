# ============================================================
# Widget final forense v4
# 24h linear + 24h log + zoom around daily + zoom around trades
# regular market en doble vista + distancia al rango daily
# separado en premarket / regular / after-hours
# con resumen por sesion y mensajes claros en paneles vacios
# trades en rojo como antes
# ============================================================

import math
from pathlib import Path
from zoneinfo import ZoneInfo

import ipywidgets as widgets
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from IPython.display import Markdown, display, clear_output

OHLCV_DAILY_ROOT = Path(r"D:\ohlcv_daily")
OHLCV_1M_ROOT = Path(r"D:\ohlcv_1m")
NY_TZ = ZoneInfo("America/New_York")

def run_full_forensic_widget(
    tax_df,
    initial_taxonomy: str = "__ALL__",
    initial_side: str = "__ALL__",
    initial_top_n: int = 250,
    top_n_options = [100, 250, 500, 1000, 2500],
    ranking_head: int = 40,
):
    # ------------------------------------------------------------------
    # 1. Base ranking
    # ------------------------------------------------------------------
    case_df = tax_df.copy()

    for c in [
        "break_abs_max",
        "break_pct_span_max",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.duplicate_excess_ratio_pct",
        "m.off_session_trade_pct",
    ]:
        case_df[c] = pd.to_numeric(case_df.get(c), errors="coerce")

    case_df["rank_score"] = (
        0.65 * np.log1p(case_df["break_pct_span_max"].fillna(0))
        + 0.35 * np.log1p(case_df["break_abs_max"].fillna(0))
    )

    case_df = case_df.sort_values(
        ["rank_score", "break_pct_span_max", "break_abs_max"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    case_df["rank"] = np.arange(1, len(case_df) + 1)

    display(Markdown("## Top casos ordenados descendente"))
    display(
        case_df[
            [
                "rank",
                "ticker",
                "date",
                "taxonomy",
                "break_side",
                "break_abs_max",
                "break_pct_span_max",
                "rank_score",
                "m.trade_volume_vs_daily_ratio",
                "m.trade_volume_vs_1m_ratio",
                "m.duplicate_excess_ratio_pct",
                "m.off_session_trade_pct",
            ]
        ].head(ranking_head)
    )

    # ------------------------------------------------------------------
    # 2. Helpers
    # ------------------------------------------------------------------
    def read_case_refs(row):
        ticker = str(row["ticker"])
        date_ts = pd.Timestamp(row["date"])
        year = int(date_ts.year)
        month = int(date_ts.month)
        date_str = str(date_ts.date())

        trade_path = Path(row["file"])
        daily_path = OHLCV_DAILY_ROOT / f"ticker={ticker}" / f"year={year:04d}" / f"day_aggs_{ticker}_{year:04d}.parquet"

        m1_dir = OHLCV_1M_ROOT / f"ticker={ticker}" / f"year={year:04d}" / f"month={month:02d}"
        m1_candidates = [
            m1_dir / f"minute_aggs_{ticker}_{year:04d}_{month:02d}.parquet",
            m1_dir / f"minute_aggs_{ticker}_{year:04d}{month:02d}.parquet",
        ]
        m1_path = next((p for p in m1_candidates if p.exists()), None)

        trades_df = pd.read_parquet(trade_path).copy()
        trades_df["timestamp"] = pd.to_datetime(trades_df["timestamp"], utc=True, errors="coerce")
        trades_df["timestamp_local"] = trades_df["timestamp"].dt.tz_convert(NY_TZ)
        trades_df["price"] = pd.to_numeric(trades_df["price"], errors="coerce")
        trades_df["size"] = pd.to_numeric(trades_df["size"], errors="coerce")
        trades_df = trades_df.dropna(subset=["timestamp", "timestamp_local", "price"]).sort_values("timestamp").copy()

        daily_df = pd.read_parquet(daily_path).copy()
        daily_df["date"] = pd.to_datetime(daily_df["date"], errors="coerce")
        daily_row = daily_df.loc[daily_df["date"] == pd.Timestamp(date_str)].iloc[0].copy()

        if m1_path is None:
            m1_day = pd.DataFrame(columns=["ts_utc", "ts_local", "o", "h", "l", "c", "vw", "v", "n"])
        else:
            m1_df = pd.read_parquet(m1_path).copy()

            if "ts_utc" in m1_df.columns:
                m1_df["ts_utc"] = pd.to_datetime(m1_df["ts_utc"], utc=True, errors="coerce")
            elif "timestamp" in m1_df.columns:
                m1_df["ts_utc"] = pd.to_datetime(m1_df["timestamp"], utc=True, errors="coerce")
            else:
                raise ValueError("No encuentro columna temporal en 1m parquet")

            if "date" in m1_df.columns:
                m1_df["date"] = pd.to_datetime(m1_df["date"], errors="coerce")
                m1_day = m1_df.loc[m1_df["date"] == pd.Timestamp(date_str)].copy()
            else:
                m1_day = m1_df.loc[m1_df["ts_utc"].dt.date == pd.Timestamp(date_str).date()].copy()

            m1_day["ts_local"] = m1_day["ts_utc"].dt.tz_convert(NY_TZ)

            for c in ["o", "h", "l", "c", "vw", "v", "n"]:
                if c in m1_day.columns:
                    m1_day[c] = pd.to_numeric(m1_day[c], errors="coerce")

            m1_day = m1_day.sort_values("ts_utc").copy()

        return trades_df, daily_row, m1_day


    def classify_session(ts_local):
        t = ts_local.timetz()
        hm = (t.hour, t.minute)
        if hm < (9, 30):
            return "premarket"
        if hm < (16, 0):
            return "regular"
        return "afterhours"


    def add_session_labels(df, ts_col):
        out = df.copy()
        out["session"] = out[ts_col].map(classify_session)
        return out


    def get_day_bounds_local(date_value):
        d = pd.Timestamp(date_value).date()
        start = pd.Timestamp(f"{d} 04:00:00", tz=NY_TZ)
        end = pd.Timestamp(f"{d} 20:00:00", tz=NY_TZ)
        return start, end


    def get_full_limits(daily_row, trades_seg, m1_seg):
        daily_low = float(daily_row["l"])
        daily_high = float(daily_row["h"])

        vals = [daily_low, daily_high]

        if len(trades_seg):
            vals.extend(pd.to_numeric(trades_seg["price"], errors="coerce").dropna().tolist())

        if len(m1_seg):
            if "l" in m1_seg.columns:
                vals.extend(pd.to_numeric(m1_seg["l"], errors="coerce").dropna().tolist())
            if "h" in m1_seg.columns:
                vals.extend(pd.to_numeric(m1_seg["h"], errors="coerce").dropna().tolist())

        vals = [v for v in vals if pd.notna(v)]
        if not vals:
            return 0.0, 1.0

        ymin_raw = min(vals)
        ymax_raw = max(vals)
        span = max(ymax_raw - ymin_raw, 1e-9)

        y_min = ymin_raw - span * 0.08
        y_max = ymax_raw + span * 0.20
        return y_min, y_max


    def get_log_limits(daily_row, trades_seg, m1_seg):
        vals = []

        for c in ["o", "h", "l", "c", "vw"]:
            v = daily_row.get(c)
            if pd.notna(v) and float(v) > 0:
                vals.append(float(v))

        if len(trades_seg):
            vals.extend(pd.to_numeric(trades_seg["price"], errors="coerce").dropna().tolist())

        if len(m1_seg):
            for c in ["l", "h", "o", "c", "vw"]:
                if c in m1_seg.columns:
                    vals.extend(pd.to_numeric(m1_seg[c], errors="coerce").dropna().tolist())

        vals = [float(v) for v in vals if pd.notna(v) and float(v) > 0]
        if not vals:
            return 1e-3, 1.0

        ymin_raw = min(vals)
        ymax_raw = max(vals)
        return ymin_raw * 0.7, ymax_raw * 1.35


    def get_zoom_limits(daily_row, trades_seg, m1_seg):
        daily_low = float(daily_row["l"])
        daily_high = float(daily_row["h"])
        daily_span = max(daily_high - daily_low, 1e-9)

        trades_p01 = np.nan
        trades_p99 = np.nan
        if len(trades_seg):
            trades_p01 = np.nanpercentile(trades_seg["price"], 1)
            trades_p99 = np.nanpercentile(trades_seg["price"], 99)

        m1_l_p01 = np.nan
        m1_h_p99 = np.nan
        if len(m1_seg) and "l" in m1_seg.columns and "h" in m1_seg.columns:
            m1_l_p01 = np.nanpercentile(pd.to_numeric(m1_seg["l"], errors="coerce"), 1)
            m1_h_p99 = np.nanpercentile(pd.to_numeric(m1_seg["h"], errors="coerce"), 99)

        zoom_floor_ref = np.nanmin([daily_low, trades_p01, m1_l_p01])
        zoom_ceiling_ref = np.nanmax([daily_high, trades_p99, m1_h_p99])

        span_ref = max(abs(zoom_ceiling_ref - zoom_floor_ref), 1e-9)
        pad = max(daily_span * 0.60, span_ref * 0.20)

        y_min_zoom = zoom_floor_ref - pad
        y_max_zoom = zoom_ceiling_ref + pad
        return y_min_zoom, y_max_zoom


    def get_trades_cluster_limits(trades_seg):
        if trades_seg.empty:
            return 0.0, 1.0

        px = pd.to_numeric(trades_seg["price"], errors="coerce").dropna()
        if px.empty:
            return 0.0, 1.0

        p01 = np.nanpercentile(px, 1)
        p99 = np.nanpercentile(px, 99)
        span = max(p99 - p01, 1e-9)
        pad = max(span * 0.25, abs(p99) * 0.05)

        return p01 - pad, p99 + pad


    def add_distance_to_daily(trades_seg, daily_row):
        out = trades_seg.copy()
        daily_low = float(daily_row["l"])
        daily_high = float(daily_row["h"])

        out["distance_to_band"] = 0.0
        out.loc[out["price"] < daily_low, "distance_to_band"] = out["price"] - daily_low
        out.loc[out["price"] > daily_high, "distance_to_band"] = out["price"] - daily_high
        return out


    def draw_candles(ax, m1_seg, width_minutes=0.65, up="#2a9d8f", down="#e76f51", alpha=0.75):
        if m1_seg.empty:
            return

        width_days = width_minutes / (24 * 60)
        x = mdates.date2num(m1_seg["ts_local"].dt.to_pydatetime())

        for xi, (_, row) in zip(x, m1_seg.iterrows()):
            o = row.get("o")
            h = row.get("h")
            l = row.get("l")
            c = row.get("c")
            if pd.isna(o) or pd.isna(h) or pd.isna(l) or pd.isna(c):
                continue
            color = up if c >= o else down
            ax.vlines(xi, l, h, color=color, linewidth=1.0, alpha=alpha, zorder=1)
            body_low = min(o, c)
            body_high = max(o, c)
            body_h = max(body_high - body_low, 1e-9)
            ax.add_patch(
                Rectangle(
                    (xi - width_days / 2, body_low),
                    width_days,
                    body_h,
                    facecolor=color,
                    edgecolor=color,
                    alpha=alpha,
                    zorder=2,
                )
            )


    def add_daily_guides(ax, daily_row):
        daily_low = float(daily_row["l"])
        daily_high = float(daily_row["h"])
        daily_open = float(daily_row["o"])
        daily_close = float(daily_row["c"])
        daily_vw = float(daily_row["vw"]) if pd.notna(daily_row.get("vw")) else np.nan

        ax.axhspan(daily_low, daily_high, color="#2a9d8f", alpha=0.10, zorder=0, label="daily low/high")
        ax.axhline(daily_low, color="#2a9d8f", lw=1.0, ls="--", alpha=0.9)
        ax.axhline(daily_high, color="#2a9d8f", lw=1.0, ls="--", alpha=0.9)
        ax.axhline(daily_open, color="#1d3557", lw=1.0, ls=":", alpha=0.9, label="daily open")
        ax.axhline(daily_close, color="#6d597a", lw=1.0, ls=":", alpha=0.9, label="daily close")
        if pd.notna(daily_vw):
            ax.axhline(daily_vw, color="#f4a261", lw=1.2, ls="-.", alpha=0.95, label="daily vw")


    def overlay_outlier_markers(ax, trades_seg, y_min, y_max):
        if trades_seg.empty:
            return

        below = trades_seg.loc[trades_seg["price"] < y_min].copy()
        above = trades_seg.loc[trades_seg["price"] > y_max].copy()

        if not below.empty:
            ax.scatter(
                below["timestamp_local"],
                np.repeat(y_min, len(below)),
                marker="v",
                s=60,
                color="#0b132b",
                alpha=0.9,
                zorder=5,
                label="below zoom",
            )

        if not above.empty:
            ax.scatter(
                above["timestamp_local"],
                np.repeat(y_max, len(above)),
                marker="^",
                s=60,
                color="#7f0000",
                alpha=0.9,
                zorder=5,
                label="above zoom",
            )


    def style_time_axis(ax, start_local, end_local, rotate=90):
        ax.set_xlim(start_local, end_local)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=NY_TZ))
        ax.tick_params(axis="x", rotation=rotate)


    def plot_price_panel(
        ax,
        trades_seg,
        m1_seg,
        daily_row,
        title,
        facecolor,
        start_local,
        end_local,
        yscale="linear",
        zoom_mode=False,
    ):
        ax.set_facecolor(facecolor)
        add_daily_guides(ax, daily_row)
        draw_candles(ax, m1_seg)

        has_trades = not trades_seg.empty
        has_m1 = not m1_seg.empty

        if has_trades:
            ax.scatter(
                trades_seg["timestamp_local"],
                trades_seg["price"],
                s=np.clip(np.sqrt(trades_seg["size"].fillna(1)) * 1.4, 12, 55),
                c="#d62828",
                alpha=0.50,
                edgecolors="none",
                zorder=3,
                label="trades",
            )

        if zoom_mode:
            y_min, y_max = get_zoom_limits(daily_row, trades_seg, m1_seg)
            ax.set_ylim(y_min, y_max)
            overlay_outlier_markers(ax, trades_seg, y_min, y_max)
        else:
            if yscale == "linear":
                y_min, y_max = get_full_limits(daily_row, trades_seg, m1_seg)
                ax.set_ylim(y_min, y_max)
            elif yscale == "log":
                y_min, y_max = get_log_limits(daily_row, trades_seg, m1_seg)
                ax.set_yscale("log")
                ax.set_ylim(y_min, y_max)

        style_time_axis(ax, start_local, end_local, rotate=90)
        ax.set_title(title)
        ax.set_ylabel("price")
        ax.grid(True, alpha=0.25)

        msg = []
        if not has_trades:
            msg.append("Sin trades")
        if not has_m1:
            msg.append("Sin velas 1m")

        if msg:
            ax.text(
                0.5,
                0.55,
                " | ".join(msg),
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=10,
                alpha=0.75,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="0.8", alpha=0.8),
            )


    def render_daily_inset(ax, daily_row, trades_df, m1_day):
        ax.set_title("Resumen diario")
        o = float(daily_row["o"])
        h = float(daily_row["h"])
        l = float(daily_row["l"])
        c = float(daily_row["c"])
        vw = float(daily_row["vw"]) if pd.notna(daily_row.get("vw")) else np.nan

        ax.vlines(0, l, h, color="#264653", linewidth=2.0)
        color = "#2a9d8f" if c >= o else "#e76f51"
        ax.add_patch(Rectangle((-0.15, min(o, c)), 0.3, max(abs(c - o), 1e-9), facecolor=color, edgecolor=color, alpha=0.8))

        if not trades_df.empty:
            ax.scatter(np.repeat(0.35, len(trades_df)), trades_df["price"], s=4, alpha=0.12, color="#d62828")
        if not m1_day.empty and "c" in m1_day.columns:
            ax.scatter(np.repeat(-0.35, len(m1_day)), m1_day["c"], s=6, alpha=0.20, color="#457b9d")

        if pd.notna(vw):
            ax.axhline(vw, color="#f4a261", ls="-.", lw=1.2)

        ax.set_xlim(-0.8, 0.8)
        ax.set_xticks([])
        ax.set_ylabel("price")
        ax.grid(True, axis="y", alpha=0.25)


    def build_filtered_cases():
        x = case_df.copy()
        if taxonomy_dd.value != "__ALL__":
            x = x.loc[x["taxonomy"] == taxonomy_dd.value].copy()
        if side_dd.value != "__ALL__":
            x = x.loc[x["break_side"] == side_dd.value].copy()
        if x.empty:
            return x
        return x.head(int(top_n_dd.value)).copy()


    def make_case_options(x):
        opts = []
        for _, row in x.iterrows():
            label = (
                f"#{int(row['rank']):04d} | {row['ticker']} | {row['date']} | "
                f"{row['taxonomy']} | {row['break_side']} | "
                f"pct={row['break_pct_span_max']:.1f} | abs={row['break_abs_max']:.4f}"
            )
            opts.append((label, int(row["rank"])))
        return opts


    def refresh_case_dropdown(*_):
        filtered = build_filtered_cases()
        case_dd.unobserve(render_selected_case, names="value")
        if filtered.empty:
            case_dd.options = [("Sin casos", None)]
            case_dd.value = None
            case_dd.observe(render_selected_case, names="value")
            render_selected_case()
            return
        case_dd.options = make_case_options(filtered)
        case_dd.value = filtered.iloc[0]["rank"]
        case_dd.observe(render_selected_case, names="value")
        render_selected_case()


    def render_selected_case(*_):
        with out:
            clear_output(wait=True)

            filtered = build_filtered_cases()
            if filtered.empty or case_dd.value is None:
                display(Markdown("## Sin casos para la selección actual"))
                return

            row = filtered.loc[filtered["rank"] == case_dd.value].iloc[0].copy()

            trades_df, daily_row, m1_day = read_case_refs(row)
            trades_df = add_session_labels(trades_df, "timestamp_local")
            if not m1_day.empty:
                m1_day = add_session_labels(m1_day, "ts_local")
            else:
                m1_day = m1_day.copy()
                m1_day["session"] = []

            day_start, day_end = get_day_bounds_local(row["date"])

            pre_start = pd.Timestamp(f"{pd.Timestamp(row['date']).date()} 04:00:00", tz=NY_TZ)
            pre_end = pd.Timestamp(f"{pd.Timestamp(row['date']).date()} 09:30:00", tz=NY_TZ)
            reg_start = pd.Timestamp(f"{pd.Timestamp(row['date']).date()} 09:30:00", tz=NY_TZ)
            reg_end = pd.Timestamp(f"{pd.Timestamp(row['date']).date()} 16:00:00", tz=NY_TZ)
            aft_start = pd.Timestamp(f"{pd.Timestamp(row['date']).date()} 16:00:00", tz=NY_TZ)
            aft_end = pd.Timestamp(f"{pd.Timestamp(row['date']).date()} 20:00:00", tz=NY_TZ)

            pre_trades = trades_df.loc[trades_df["session"] == "premarket"].copy()
            reg_trades = trades_df.loc[trades_df["session"] == "regular"].copy()
            aft_trades = trades_df.loc[trades_df["session"] == "afterhours"].copy()

            pre_m1 = m1_day.loc[m1_day["session"] == "premarket"].copy()
            reg_m1 = m1_day.loc[m1_day["session"] == "regular"].copy()
            aft_m1 = m1_day.loc[m1_day["session"] == "afterhours"].copy()

            session_summary = pd.DataFrame(
                [
                    {"session": "premarket", "trades_rows": int(len(pre_trades)), "m1_rows": int(len(pre_m1))},
                    {"session": "regular", "trades_rows": int(len(reg_trades)), "m1_rows": int(len(reg_m1))},
                    {"session": "afterhours", "trades_rows": int(len(aft_trades)), "m1_rows": int(len(aft_m1))},
                ]
            )
            extended_hours_present = bool(len(pre_trades) or len(aft_trades))

            header = pd.DataFrame(
                [
                    {
                        "rank": int(row["rank"]),
                        "ticker": row["ticker"],
                        "date": str(row["date"]),
                        "taxonomy": row["taxonomy"],
                        "break_side": row["break_side"],
                        "break_abs_max": round(float(row["break_abs_max"]), 6),
                        "break_pct_span_max": round(float(row["break_pct_span_max"]), 3),
                        "rank_score": round(float(row["rank_score"]), 6),
                        "trade_volume_vs_daily_ratio": round(float(row.get("m.trade_volume_vs_daily_ratio", np.nan)), 6),
                        "trade_volume_vs_1m_ratio": round(float(row.get("m.trade_volume_vs_1m_ratio", np.nan)), 6),
                        "dup_excess_ratio_pct": round(float(row.get("m.duplicate_excess_ratio_pct", np.nan)), 6),
                        "off_session_trade_pct": round(float(row.get("m.off_session_trade_pct", np.nan)), 6),
                    }
                ]
            )

            display(Markdown("## Caso seleccionado"))
            display(header.T)

            display(
                Markdown(
                    f"""
                    **extended_hours_present:** `{extended_hours_present}`
                    **issues:** `{row.get('issues_list', [])}`
                    **warns:** `{row.get('warns_list', [])}`
                    **file:** `{row['file']}`
                    """
                )
            )
            display(Markdown("### Cobertura por sesion"))
            display(session_summary)

            # -------- TAB 1: overview --------
            out_overview = widgets.Output()
            with out_overview:
                fig = plt.figure(figsize=(24, 14))
                gs = fig.add_gridspec(2, 2, width_ratios=[4.5, 1.5], height_ratios=[1, 1])

                ax_full_linear = fig.add_subplot(gs[0, 0])
                ax_day = fig.add_subplot(gs[0, 1])
                ax_full_log = fig.add_subplot(gs[1, 0])
                ax_zoom_daily = fig.add_subplot(gs[1, 1])

                plot_price_panel(
                    ax_full_linear, trades_df, m1_day, daily_row,
                    "24h full linear: contexto bruto",
                    "#fcfcfc", day_start, day_end, yscale="linear", zoom_mode=False
                )
                for left, right, color in [
                    (pre_start, pre_end, "#dceefb"),
                    (reg_start, reg_end, "#e5f6ea"),
                    (aft_start, aft_end, "#fff0db"),
                ]:
                    ax_full_linear.axvspan(left, right, color=color, alpha=0.15, zorder=0)

                plot_price_panel(
                    ax_full_log, trades_df.loc[trades_df["price"] > 0].copy(), m1_day, daily_row,
                    "24h full log: separacion multiplicativa",
                    "#fcfcfc", day_start, day_end, yscale="log", zoom_mode=False
                )
                plot_price_panel(
                    ax_zoom_daily, trades_df, m1_day, daily_row,
                    "Zoom around daily",
                    "#f9fbfd", day_start, day_end, yscale="linear", zoom_mode=True
                )
                render_daily_inset(ax_day, daily_row, trades_df, m1_day)

                ax_full_linear.legend(loc="upper left", fontsize=8)
                for ax in [ax_full_linear, ax_full_log, ax_zoom_daily]:
                    ax.set_xlabel("New York time")

                fig.suptitle(
                    f"{row['ticker']} {row['date']} | {row['taxonomy']} | {row['break_side']} | "
                    f"pct_break={row['break_pct_span_max']:.1f} | abs_break={row['break_abs_max']:.4f}",
                    fontsize=18,
                    y=0.99,
                )
                plt.tight_layout()
                plt.show()

            # -------- TAB 2: trades cluster --------
            out_cluster = widgets.Output()
            with out_cluster:
                fig = plt.figure(figsize=(24, 14))
                gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 1])

                ax_zoom_trades = fig.add_subplot(gs[0, 0])
                ax_reg_daily = fig.add_subplot(gs[1, 0])
                ax_reg_trades = fig.add_subplot(gs[2, 0])

                plot_price_panel(
                    ax_zoom_trades, trades_df, m1_day, daily_row,
                    "Zoom around trades cluster",
                    "#fffdf8", day_start, day_end, yscale="linear", zoom_mode=False
                )
                tmin, tmax = get_trades_cluster_limits(trades_df)
                ax_zoom_trades.set_ylim(tmin, tmax)

                plot_price_panel(
                    ax_reg_daily, reg_trades, reg_m1, daily_row,
                    "Regular Market around daily range",
                    "#f3fbf5", reg_start, reg_end, yscale="linear", zoom_mode=True
                )

                plot_price_panel(
                    ax_reg_trades, reg_trades, reg_m1, daily_row,
                    "Regular Market around trades cluster",
                    "#fffaf3", reg_start, reg_end, yscale="linear", zoom_mode=False
                )
                rtmin, rtmax = get_trades_cluster_limits(reg_trades)
                ax_reg_trades.set_ylim(rtmin, rtmax)

                for ax in [ax_zoom_trades, ax_reg_daily, ax_reg_trades]:
                    ax.set_xlabel("New York time")

                plt.tight_layout()
                plt.show()

            # -------- TAB 3: sessions --------
            out_sessions = widgets.Output()
            with out_sessions:
                fig = plt.figure(figsize=(24, 16))
                gs = fig.add_gridspec(3, 1)

                ax_pre = fig.add_subplot(gs[0, 0])
                ax_reg = fig.add_subplot(gs[1, 0])
                ax_aft = fig.add_subplot(gs[2, 0])

                plot_price_panel(
                    ax_pre, pre_trades, pre_m1, daily_row,
                    "Premarket", "#f2f8fd", pre_start, pre_end, yscale="linear", zoom_mode=True
                )
                plot_price_panel(
                    ax_reg, reg_trades, reg_m1, daily_row,
                    "Regular Market", "#f3fbf5", reg_start, reg_end, yscale="linear", zoom_mode=True
                )
                plot_price_panel(
                    ax_aft, aft_trades, aft_m1, daily_row,
                    "After-hours", "#fff7ed", aft_start, aft_end, yscale="linear", zoom_mode=True
                )

                for ax in [ax_pre, ax_reg, ax_aft]:
                    ax.set_xlabel("New York time")

                plt.tight_layout()
                plt.show()

            # -------- TAB 4: distance --------
            out_distance = widgets.Output()
            with out_distance:
                fig = plt.figure(figsize=(24, 10))
                ax_distance = fig.add_subplot(111)

                dist_df = add_distance_to_daily(reg_trades, daily_row)
                ax_distance.axhline(0, color="black", lw=1.0, ls="--")
                ax_distance.scatter(
                    dist_df["timestamp_local"],
                    dist_df["distance_to_band"],
                    s=np.clip(np.sqrt(dist_df["size"].fillna(1)) * 1.5, 14, 60),
                    c="#d62828",
                    alpha=0.55,
                    edgecolors="none",
                )
                ax_distance.set_title("Regular Market: distancia al rango daily")
                ax_distance.set_ylabel("trade price - nearest daily band")
                style_time_axis(ax_distance, reg_start, reg_end, rotate=90)
                ax_distance.set_xlabel("New York time")
                ax_distance.grid(True, alpha=0.25)

                plt.tight_layout()
                plt.show()

            # -------- TAB 5: summary --------
            out_summary = widgets.Output()
            with out_summary:
                daily_low = float(daily_row["l"])
                daily_high = float(daily_row["h"])
                daily_open = float(daily_row["o"])
                daily_close = float(daily_row["c"])
                daily_vw = float(daily_row["vw"]) if pd.notna(daily_row.get("vw")) else np.nan
                daily_vw_txt = f"{daily_vw:.6f}" if pd.notna(daily_vw) else "nan"

                txt = (
                    f"ticker={row['ticker']}  |  date={row['date']}  |  taxonomy={row['taxonomy']}  |  side={row['break_side']}\n"
                    f"break_abs_max={row['break_abs_max']:.6f}  |  break_pct_span_max={row['break_pct_span_max']:.3f}  |rank_score={row['rank_score']:.6f}\n"
                    f"daily: o={daily_open:.6f} h={daily_high:.6f} l={daily_low:.6f} c={daily_close:.6f} vw={daily_vw_txt}\n"
                    f"premarket trades={len(pre_trades)} m1={len(pre_m1)}  |  regular trades={len(reg_trades)} m1={len(reg_m1)}  |afterhours trades={len(aft_trades)} m1={len(aft_m1)}\n"
                    f"trade_volume_vs_daily_ratio={row.get('m.trade_volume_vs_daily_ratio', np.nan):.6f}  |  "
                    f"trade_volume_vs_1m_ratio={row.get('m.trade_volume_vs_1m_ratio', np.nan):.6f}\n"
                    f"dup_excess_ratio_pct={row.get('m.duplicate_excess_ratio_pct', np.nan):.6f}  |  "
                    f"off_session_trade_pct={row.get('m.off_session_trade_pct', np.nan):.6f}\n"
                    f"issues={row['issues_list']}\n"
                    f"warns={row['warns_list']}"
                )
                print(txt)

            tabs = widgets.Tab(children=[out_overview, out_cluster, out_sessions, out_distance, out_summary])
            tabs.set_title(0, "Overview")
            tabs.set_title(1, "Trades")
            tabs.set_title(2, "Sessions")
            tabs.set_title(3, "Distance")
            tabs.set_title(4, "Summary")

            display(tabs)


    # ------------------------------------------------------------------
    # 3. Widgets
    # ------------------------------------------------------------------
    taxonomy_dd = widgets.Dropdown(
        options=["__ALL__"] + sorted(case_df["taxonomy"].dropna().astype(str).unique().tolist()),
        value=initial_taxonomy,
        description="taxonomy",
        layout=widgets.Layout(width="420px"),
    )

    side_dd = widgets.Dropdown(
        options=["__ALL__"] + sorted(case_df["break_side"].dropna().astype(str).unique().tolist()),
        value=initial_side,
        description="side",
        layout=widgets.Layout(width="260px"),
    )

    top_n_dd = widgets.Dropdown(
        options=top_n_options,
        value=initial_top_n,
        description="top_n",
        layout=widgets.Layout(width="220px"),
    )

    case_dd = widgets.Dropdown(
        options=[],
        description="case",
        layout=widgets.Layout(width="1500px"),
    )

    out = widgets.Output()

    taxonomy_dd.observe(refresh_case_dropdown, names="value")
    side_dd.observe(refresh_case_dropdown, names="value")
    top_n_dd.observe(refresh_case_dropdown, names="value")
    case_dd.observe(render_selected_case, names="value")

    controls = widgets.VBox(
        [
            widgets.HBox([taxonomy_dd, side_dd, top_n_dd]),
            case_dd,
        ]
    )

    refresh_case_dropdown()
    display(controls)
    display(out)
