from __future__ import annotations

from pathlib import Path

import ipywidgets as widgets
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display


NY_TZ = "America/New_York"

DEFAULT_ADDITIONAL_AUDIT_CACHE = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2"
)
DEFAULT_HALTS_CACHE = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cache_v2"
)

QUOTES_ROOTS = [
    Path(r"D:\quotes"),
    Path(r"C:\TSIS_Data\data\quotes"),
]
TRADES_ROOTS = [
    Path(r"C:\TSIS_Data\data\trades_ticks_prod_2005_2026"),
    Path(r"D:\trades_ticks_prod_2005_2026"),
]
DAILY_ROOTS = [
    Path(r"D:\ohlcv_daily"),
    Path(r"C:\TSIS_Data\data\ohlcv_daily"),
]


def _read(cache_root: Path, name: str) -> pd.DataFrame:
    path = cache_root / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def load_additional_viewer_inputs(cache_root: Path = DEFAULT_ADDITIONAL_AUDIT_CACHE) -> dict[str, pd.DataFrame]:
    return {
        "news_candidates": _read(cache_root, "additional_news_market_link_candidates.parquet"),
        "ipo_candidates": _read(cache_root, "additional_ipo_market_link_candidates.parquet"),
    }


def _safe_read_parquet(path: str | Path, columns: list[str]) -> pd.DataFrame:
    p = Path(str(path))
    if not p.exists():
        return pd.DataFrame(columns=columns)
    return pd.read_parquet(p, columns=columns)


def _to_ny_from_quotes_timestamp(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        ts = pd.to_datetime(series, unit="ns", utc=True, errors="coerce")
    else:
        ts = pd.to_datetime(series, utc=True, errors="coerce")
    return ts.dt.tz_convert(NY_TZ).dt.tz_localize(None)


def _to_ny_from_trade_timestamp(series: pd.Series) -> pd.Series:
    ts = pd.to_datetime(series, utc=True, errors="coerce")
    return ts.dt.tz_convert(NY_TZ).dt.tz_localize(None)


def _to_ny_from_utc(value: object) -> pd.Timestamp:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    return ts.tz_convert(NY_TZ).tz_localize(None)


def _locate_quotes_file(ticker: str, dt: pd.Timestamp) -> Path | None:
    if pd.isna(dt):
        return None
    ticker = str(ticker).upper()
    year = int(dt.year)
    month = int(dt.month)
    day_num = int(dt.day)
    day_full = dt.strftime("%Y-%m-%d")
    candidates: list[Path] = []
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
    candidates: list[Path] = []
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


def _load_daily_window(ticker: str, event_date: pd.Timestamp, pad_days: int = 30) -> pd.DataFrame:
    ticker = str(ticker).upper()
    start = (event_date - pd.Timedelta(days=pad_days)).normalize()
    end = (event_date + pd.Timedelta(days=pad_days)).normalize()
    years = list(range(int(start.year), int(end.year) + 1))
    frames: list[pd.DataFrame] = []
    for year in years:
        found = None
        for root in DAILY_ROOTS:
            candidate = root / f"ticker={ticker}" / f"year={year}" / f"day_aggs_{ticker}_{year}.parquet"
            if candidate.exists():
                found = candidate
                break
        if found is None:
            continue
        try:
            part = pd.read_parquet(found, columns=["ticker", "date", "o", "h", "l", "c", "v", "vw", "n"])
        except Exception:
            continue
        frames.append(part)
    if not frames:
        return pd.DataFrame(columns=["ticker", "date", "o", "h", "l", "c", "v", "vw", "n"])
    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    for col in ["o", "h", "l", "c", "v", "vw", "n"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[df["date"].between(start, end)].sort_values("date").reset_index(drop=True)


def _load_halt_visual_row(ticker: str, event_date: pd.Timestamp) -> pd.Series | None:
    path = DEFAULT_HALTS_CACHE / "halts_quotes_trades_visual_cases.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(
            path,
            columns=["ticker", "visual_date", "visual_case_bucket", "halt_markers_et", "resume_markers_et", "rank_score"],
        )
    except Exception:
        return None
    df["visual_date"] = pd.to_datetime(df["visual_date"], errors="coerce").dt.normalize()
    sub = df[(df["ticker"].astype(str).str.upper() == str(ticker).upper()) & (df["visual_date"] == event_date.normalize())]
    if sub.empty:
        return None
    return sub.sort_values("rank_score", ascending=False).iloc[0]


def _parse_marker_list(value: object) -> list[pd.Timestamp]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    out: list[pd.Timestamp] = []
    for part in [x.strip() for x in text.split("|") if x.strip()]:
        ts = pd.to_datetime(part, errors="coerce")
        if pd.notna(ts):
            out.append(ts)
    if not out:
        return []
    return list(pd.Series(out).dropna().drop_duplicates().sort_values())


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


def _plot_event_timestamp(ax, event_ts: pd.Timestamp | None, label: str, color: str = "#7c3aed") -> None:
    if event_ts is None or pd.isna(event_ts):
        return
    ax.axvline(event_ts, color=color, linestyle="-.", linewidth=1.4, alpha=0.95, label=label)


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


def _render_market_overlay(
    ticker: str,
    event_date: pd.Timestamp,
    event_label: str,
    summary_lines: list[str],
    event_ts_intraday: pd.Timestamp | None = None,
) -> None:
    daily_df = _load_daily_window(ticker, event_date, pad_days=30)
    quotes_df = _prepare_quotes_view(_locate_quotes_file(ticker, event_date))
    trades_df = _prepare_trades_view(_locate_trades_file(ticker, event_date))
    halt_row = _load_halt_visual_row(ticker, event_date)
    halt_markers = _parse_marker_list(halt_row["halt_markers_et"]) if halt_row is not None else []
    resume_markers = _parse_marker_list(halt_row["resume_markers_et"]) if halt_row is not None else []

    daily_event = daily_df.loc[daily_df["date"] == event_date].copy()
    daily_close = float(daily_event["c"].iloc[0]) if not daily_event.empty and pd.notna(daily_event["c"].iloc[0]) else np.nan
    daily_range_pct = (
        float((daily_event["h"].iloc[0] - daily_event["l"].iloc[0]) / daily_close * 100.0)
        if not daily_event.empty and pd.notna(daily_close) and daily_close > 0
        else np.nan
    )
    daily_return_pct = np.nan
    if not daily_event.empty:
        prev = daily_df.loc[daily_df["date"] < event_date].tail(1)
        if not prev.empty and pd.notna(prev["c"].iloc[0]) and float(prev["c"].iloc[0]) > 0:
            daily_return_pct = (daily_close / float(prev["c"].iloc[0]) - 1.0) * 100.0

    display(
        Markdown(
            "**Cruce con mercado**  \n"
            + "\n".join(summary_lines)
            + f"\n- `daily_close`: `{daily_close if pd.notna(daily_close) else None}`  "
            + f"\n- `daily_return_pct`: `{round(float(daily_return_pct), 2) if pd.notna(daily_return_pct) else None}`  "
            + f"\n- `daily_range_pct`: `{round(float(daily_range_pct), 2) if pd.notna(daily_range_pct) else None}`  "
            + f"\n- `halt_visual_bucket`: `{halt_row['visual_case_bucket'] if halt_row is not None else None}`"
        )
    )

    fig, axes = plt.subplots(4, 1, figsize=(14, 12), gridspec_kw={"height_ratios": [1.2, 1.8, 1.6, 1.1]})

    if not daily_df.empty:
        axes[0].plot(daily_df["date"], daily_df["c"], color="#1f77b4", lw=1.6, label="daily close")
        axes[0].vlines(daily_df["date"], daily_df["l"], daily_df["h"], color="#94a3b8", alpha=0.7, linewidth=1.0, label="daily range")
        axes[0].axvline(event_date, color="crimson", lw=1.4, ls="--", label=event_label)
        axes[0].set_ylabel("daily px")
        axes[0].set_title(f"{ticker} daily price around {event_date.date()}")
        axes[0].legend(loc="upper left")
    else:
        axes[0].text(0.5, 0.5, "No daily window available", ha="center", va="center", transform=axes[0].transAxes)

    if not quotes_df.empty:
        axes[1].step(quotes_df["timestamp_ny"], quotes_df["bid_price"], where="post", color="#0f766e", lw=1.2, label="bid_price")
        axes[1].step(quotes_df["timestamp_ny"], quotes_df["ask_price"], where="post", color="#dc2626", lw=1.2, label="ask_price")
        crossed = quotes_df.loc[quotes_df["cross_positive"]]
        if not crossed.empty:
            axes[1].scatter(crossed["timestamp_ny"], crossed["ask_price"], color="#f59e0b", s=12, label="crossed ask", zorder=5)
        _plot_marker_lines(axes[1], halt_markers, resume_markers)
        _plot_event_timestamp(axes[1], event_ts_intraday, event_label)
        lo, hi = _robust_limits(quotes_df, trades_df)
        if lo is not None and hi is not None:
            axes[1].set_ylim(lo, hi)
        axes[1].set_ylabel("quote px")
        axes[1].legend(loc="upper left")
    else:
        axes[1].text(0.5, 0.5, "No intraday quotes raw", ha="center", va="center", transform=axes[1].transAxes)

    if not trades_df.empty:
        regular = trades_df.loc[trades_df["regular_lot"]]
        odd = trades_df.loc[~trades_df["regular_lot"]]
        if not regular.empty:
            axes[2].scatter(regular["timestamp_ny"], regular["price"], s=10, color="#2563eb", alpha=0.75, label="round_lot >= 100")
        if not odd.empty:
            axes[2].scatter(odd["timestamp_ny"], odd["price"], s=10, color="#f97316", alpha=0.75, label="odd_lot < 100")
        _plot_marker_lines(axes[2], halt_markers, resume_markers)
        _plot_event_timestamp(axes[2], event_ts_intraday, event_label)
        lo, hi = _robust_limits(quotes_df, trades_df)
        if lo is not None and hi is not None:
            axes[2].set_ylim(lo, hi)
        axes[2].set_ylabel("trade px")
        axes[2].legend(loc="upper left")
    else:
        axes[2].text(0.5, 0.5, "No intraday trades raw", ha="center", va="center", transform=axes[2].transAxes)

    diag_done = False
    if not quotes_df.empty:
        axes[3].plot(quotes_df["timestamp_ny"], quotes_df["spread_bps"], color="#94a3b8", lw=1.0, label="spread_bps")
        crossed = quotes_df.loc[quotes_df["cross_positive"] & quotes_df["cross_gap_bps"].notna()]
        if not crossed.empty:
            axes[3].scatter(crossed["timestamp_ny"], crossed["cross_gap_bps"], color="#ef4444", s=12, label="cross_gap_bps")
        diag_done = True
    if not trades_df.empty:
        tpm = trades_df.set_index("timestamp_ny").resample("1min").size()
        ax_r = axes[3].twinx()
        ax_r.plot(tpm.index, tpm.values, color="#10b981", lw=1.0, label="trades/min")
        ax_r.set_ylabel("trades/min", color="#10b981")
        ax_r.tick_params(axis="y", labelcolor="#10b981")
        diag_done = True
    _plot_marker_lines(axes[3], halt_markers, resume_markers)
    _plot_event_timestamp(axes[3], event_ts_intraday, event_label)
    if diag_done:
        axes[3].set_ylabel("bps")
        axes[3].legend(loc="upper left")
    else:
        axes[3].text(0.5, 0.5, "No diagnostics available", ha="center", va="center", transform=axes[3].transAxes)

    for ax in axes[1:]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    axes[-1].set_xlabel("timestamp NY")
    fig.subplots_adjust(hspace=0.28)
    plt.show()


def _render_news_case(case: pd.Series) -> None:
    ticker = str(case["ticker"])
    event_date = pd.to_datetime(case["news_date"]).normalize()
    published_ny = _to_ny_from_utc(case.get("published_utc"))
    published_text = published_ny.strftime("%Y-%m-%d %H:%M") if pd.notna(published_ny) else None
    display(
        Markdown(
            f"**{ticker} | {event_date.date()} | news**  \n"
            f"- `news_link_bucket`: `{case.get('news_link_bucket')}`  \n"
            f"- `title`: {case.get('title')}  \n"
            f"- `publisher`: `{case.get('publisher_name')}`  \n"
            f"- `published_ny`: `{published_text}`  \n"
            f"- `n_tickers`: `{case.get('n_tickers')}`  \n"
            f"- `is_multi_ticker`: `{bool(case.get('is_multi_ticker'))}`"
        )
    )
    summary = [
        f"- `quotes_severity`: `{case.get('quotes_severity')}`  ",
        f"- `trades_severity`: `{case.get('trades_severity')}`  ",
        f"- `short_market_link_bucket`: `{case.get('short_market_link_bucket')}`  ",
        f"- `short_volume_ratio`: `{round(float(case.get('short_volume_ratio')), 2) if pd.notna(case.get('short_volume_ratio')) else None}`  ",
        f"- `published_ny`: `{published_text}`  ",
    ]
    _render_market_overlay(ticker, event_date, "published_ny", summary, event_ts_intraday=published_ny)


def _render_ipo_case(case: pd.Series) -> None:
    ticker = str(case["ticker"])
    event_ts = pd.to_datetime(case["listing_date"], errors="coerce")
    event_date = event_ts.normalize() if pd.notna(event_ts) else pd.NaT
    if pd.isna(event_date):
        display(Markdown(f"**{ticker}**: `listing_date` nula, no hay overlay de mercado útil."))
        return
    display(
        Markdown(
            f"**{ticker} | {event_date.date()} | ipo**  \n"
            f"- `ipo_link_bucket`: `{case.get('ipo_link_bucket')}`  \n"
            f"- `issuer_name`: `{case.get('issuer_name')}`  \n"
            f"- `ipo_status`: `{case.get('ipo_status')}`  \n"
            f"- `primary_exchange`: `{case.get('primary_exchange')}`  \n"
            f"- `final_issue_price`: `{case.get('final_issue_price')}`  \n"
            f"- `shares_outstanding`: `{case.get('shares_outstanding')}`"
        )
    )
    summary = [
        f"- `quotes_severity`: `{case.get('quotes_severity')}`  ",
        f"- `trades_severity`: `{case.get('trades_severity')}`  ",
        f"- `halt_visual_bucket`: `{case.get('halt_visual_bucket')}`  ",
        f"- `security_type`: `{case.get('security_type')}`  ",
    ]
    _render_market_overlay(ticker, event_date, "listing_date", summary)


def build_additional_viewer(cache_root: Path = DEFAULT_ADDITIONAL_AUDIT_CACHE) -> widgets.VBox:
    payload = load_additional_viewer_inputs(cache_root)
    news = payload["news_candidates"].copy()
    ipos = payload["ipo_candidates"].copy()

    mode = widgets.ToggleButtons(
        options=[("news", "news"), ("ipos", "ipos")],
        description="mode",
    )
    bucket = widgets.Dropdown(description="bucket")
    search = widgets.Text(description="search", placeholder="ticker o texto")
    limit = widgets.IntSlider(value=100, min=25, max=300, step=25, description="top N")
    case = widgets.Dropdown(description="case", layout=widgets.Layout(width="95%"))
    out = widgets.Output()
    case._current_df = pd.DataFrame()
    sync_state = {"busy": False}

    def refresh_buckets(*_):
        sync_state["busy"] = True
        df = news if mode.value == "news" else ipos
        bucket_col = "news_link_bucket" if mode.value == "news" else "ipo_link_bucket"
        opts = sorted(df[bucket_col].dropna().astype(str).unique().tolist()) if not df.empty else []
        case._current_df = pd.DataFrame()
        case.options = []
        bucket.options = opts
        bucket.value = opts[0] if opts else None
        sync_state["busy"] = False
        refresh_cases()

    def refresh_cases(*_):
        if sync_state["busy"]:
            return
        df = news if mode.value == "news" else ipos
        bucket_col = "news_link_bucket" if mode.value == "news" else "ipo_link_bucket"
        current = df.loc[df[bucket_col].astype("string") == str(bucket.value)].copy() if bucket.value else df.iloc[0:0].copy()
        search_text = str(search.value or "").strip().lower()
        if search_text:
            if mode.value == "news":
                mask = (
                    current["ticker"].astype("string").str.lower().str.contains(search_text, na=False)
                    | current["title"].astype("string").str.lower().str.contains(search_text, na=False)
                    | current["publisher_name"].astype("string").str.lower().str.contains(search_text, na=False)
                )
            else:
                mask = (
                    current["ticker"].astype("string").str.lower().str.contains(search_text, na=False)
                    | current["issuer_name"].astype("string").str.lower().str.contains(search_text, na=False)
                )
            current = current.loc[mask].copy()
        if mode.value == "news":
            current["sort_score"] = np.where(current["news_link_bucket"].eq("news_near_halt_market_event"), 3, np.where(current["is_multi_ticker"], 1, 2))
            current["sort_aux"] = pd.to_numeric(current["halt_rank_score"], errors="coerce").fillna(-1)
            current = current.sort_values(["sort_score", "sort_aux", "ticker", "news_date"], ascending=[False, False, True, False])
            current["case_label"] = current.apply(
                lambda r: f"{r['ticker']} | {pd.to_datetime(r['news_date']).date()} | {r['news_link_bucket']} | {str(r.get('title', ''))[:90]}",
                axis=1,
            )
        else:
            current["sort_score"] = np.where(current["ipo_link_bucket"].eq("ipo_near_halt_market_event"), 2, 1)
            current["sort_aux"] = pd.to_numeric(current["halt_rank_score"], errors="coerce").fillna(-1)
            current = current.sort_values(["sort_score", "sort_aux", "ticker", "listing_date"], ascending=[False, False, True, False])
            current["case_label"] = current.apply(
                lambda r: f"{r['ticker']} | {pd.to_datetime(r['listing_date']).date() if pd.notna(r.get('listing_date')) else 'na'} | {r['ipo_link_bucket']} | {str(r.get('issuer_name', ''))[:70]}",
                axis=1,
            )
        current = current.head(int(limit.value)).reset_index(drop=True)
        case._current_df = current
        case.options = list(current["case_label"]) if not current.empty else []
        case.value = case.options[0] if case.options else None
        render()

    def render(*_):
        if sync_state["busy"]:
            return
        with out:
            out.clear_output(wait=True)
            df = case._current_df
            if df.empty or not case.value:
                display(Markdown("_No hay casos para el bucket seleccionado._"))
                return
            row = df.loc[df["case_label"] == case.value].iloc[0]
            if mode.value == "news":
                _render_news_case(row)
            else:
                _render_ipo_case(row)

    mode.observe(refresh_buckets, names="value")
    bucket.observe(refresh_cases, names="value")
    search.observe(refresh_cases, names="value")
    limit.observe(refresh_cases, names="value")
    case.observe(render, names="value")
    refresh_buckets()
    return widgets.VBox([mode, bucket, search, limit, case, out])
