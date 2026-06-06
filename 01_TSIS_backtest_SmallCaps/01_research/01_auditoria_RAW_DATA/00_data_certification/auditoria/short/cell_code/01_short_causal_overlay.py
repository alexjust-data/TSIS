from __future__ import annotations

from pathlib import Path

import ipywidgets as widgets
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display


NY_TZ = "America/New_York"

DEFAULT_SHORT_AUDIT_CACHE = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2"
)
DEFAULT_FINRA_ROOT = Path(r"C:\TSIS_Data\data\short_review\finra_short\normalized")
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


def load_short_viewer_inputs(cache_root: Path = DEFAULT_SHORT_AUDIT_CACHE) -> dict[str, pd.DataFrame]:
    return {
        "sv_candidates": _read(cache_root, "short_volume_market_link_candidates.parquet"),
        "sv_halt": _read(cache_root, "short_volume_halt_link_candidates.parquet"),
        "si_candidates": _read(cache_root, "short_interest_market_context_candidates.parquet"),
    }


def _load_series(root: Path, dataset: str, ticker: str) -> pd.DataFrame:
    path = root / dataset / f"{ticker}.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


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
    df = df[df["date"].between(start, end)].sort_values("date").reset_index(drop=True)
    return df


def _load_halt_visual_row(ticker: str, event_date: pd.Timestamp) -> pd.Series | None:
    path = DEFAULT_HALTS_CACHE / "halts_quotes_trades_visual_cases.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(
            path,
            columns=["ticker", "visual_date", "visual_case_bucket", "halt_markers_et", "resume_markers_et"],
        )
    except Exception:
        return None
    df["visual_date"] = pd.to_datetime(df["visual_date"], errors="coerce").dt.normalize()
    sub = df[(df["ticker"].astype(str).str.upper() == str(ticker).upper()) & (df["visual_date"] == event_date.normalize())]
    if sub.empty:
        return None
    return sub.iloc[0]


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
    if not out:
        return []
    ser = pd.Series(out).dropna().drop_duplicates().sort_values()
    return list(ser)


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


def _render_short_volume_market_overlay(case: pd.Series) -> None:
    ticker = str(case["ticker"])
    event_date = pd.to_datetime(case["date"]).normalize()
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
            f"**Cruce con mercado**  \n"
            f"- `daily_close`: `{daily_close if pd.notna(daily_close) else None}`  \n"
            f"- `daily_return_pct`: `{round(float(daily_return_pct), 2) if pd.notna(daily_return_pct) else None}`  \n"
            f"- `daily_range_pct`: `{round(float(daily_range_pct), 2) if pd.notna(daily_range_pct) else None}`  \n"
            f"- `quotes_severity`: `{case.get('quotes_severity')}`  \n"
            f"- `trades_severity`: `{case.get('trades_severity')}`  \n"
            f"- `halt_visual_bucket`: `{halt_row['visual_case_bucket'] if halt_row is not None else case.get('halt_visual_bucket')}`"
        )
    )

    fig, axes = plt.subplots(4, 1, figsize=(14, 12), gridspec_kw={"height_ratios": [1.2, 1.8, 1.6, 1.1]})

    if not daily_df.empty:
        axes[0].plot(daily_df["date"], daily_df["c"], color="#1f77b4", lw=1.6, label="daily close")
        axes[0].vlines(daily_df["date"], daily_df["l"], daily_df["h"], color="#94a3b8", alpha=0.7, linewidth=1.0, label="daily range")
        axes[0].axvline(event_date, color="crimson", lw=1.4, ls="--", label="event_date")
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


def _render_short_volume_case(case: pd.Series, finra_root: Path) -> None:
    ticker = str(case["ticker"])
    event_date = pd.to_datetime(case["date"]).normalize()
    df = _load_series(finra_root, "short_volume", ticker)
    if df.empty:
        display(Markdown(f"**{ticker}**: no se encontró serie FINRA `short_volume`."))
        return
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    window = df[(df["date"] >= event_date - pd.Timedelta(days=30)) & (df["date"] <= event_date + pd.Timedelta(days=30))].copy()
    display(
        Markdown(
            f"**{ticker} | {event_date.date()} | short_volume**  \n"
            f"- `market_link_bucket`: `{case.get('market_link_bucket')}`  \n"
            f"- `short_signal_bucket`: `{case.get('short_signal_bucket')}`  \n"
            f"- `short_volume_ratio`: `{case.get('short_volume_ratio'):.2f}`  \n"
            f"- `halt_visual_bucket`: `{case.get('halt_visual_bucket')}`  \n"
            f"- `quotes_severity`: `{case.get('quotes_severity')}`  \n"
            f"- `trades_severity`: `{case.get('trades_severity')}`"
        )
    )
    if window.empty:
        display(Markdown("_No hay ventana temporal disponible para este caso._"))
        return
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    axes[0].plot(window["date"], window["short_volume_ratio"], color="#1f77b4", lw=1.8, label="short_volume_ratio")
    axes[0].axvline(event_date, color="crimson", lw=1.5, ls="--", label="event_date")
    axes[0].set_ylabel("ratio %")
    axes[0].set_title(f"{ticker} short_volume_ratio around {event_date.date()}")
    axes[0].legend(loc="upper left")

    axes[1].bar(window["date"], window["total_volume"], color="#7f8c8d", alpha=0.8, width=0.8, label="total_volume")
    axes[1].bar(window["date"], window["short_volume"], color="#e67e22", alpha=0.8, width=0.8, label="short_volume")
    axes[1].axvline(event_date, color="crimson", lw=1.5, ls="--")
    axes[1].set_ylabel("volume")
    axes[1].legend(loc="upper left")
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.show()

    _render_short_volume_market_overlay(case)


def _render_short_interest_case(case: pd.Series, finra_root: Path) -> None:
    ticker = str(case["ticker"])
    settlement_date = pd.to_datetime(case["settlement_date"]).normalize()
    linked_halt_date = pd.to_datetime(case["linked_halt_date"]).normalize() if pd.notna(case.get("linked_halt_date")) else pd.NaT
    df = _load_series(finra_root, "short_interest", ticker)
    if df.empty:
        display(Markdown(f"**{ticker}**: no se encontró serie FINRA `short_interest`."))
        return
    df["settlement_date"] = pd.to_datetime(df["settlement_date"]).dt.normalize()
    window = df[(df["settlement_date"] >= settlement_date - pd.Timedelta(days=180)) & (df["settlement_date"] <= settlement_date + pd.Timedelta(days=180))].copy()
    display(
        Markdown(
            f"**{ticker} | {settlement_date.date()} | short_interest**  \n"
            f"- `context_bucket`: `{case.get('context_bucket')}`  \n"
            f"- `days_to_cover`: `{case.get('days_to_cover'):.2f}`  \n"
            f"- `dtc_z`: `{case.get('dtc_z'):.2f}`  \n"
            f"- `linked_halt_date`: `{linked_halt_date.date() if pd.notna(linked_halt_date) else None}`  \n"
            f"- `halt_visual_bucket`: `{case.get('halt_visual_bucket')}`"
        )
    )
    if window.empty:
        display(Markdown("_No hay ventana temporal disponible para este caso._"))
        return
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [2, 1.5, 1.5]})
    axes[0].plot(window["settlement_date"], window["days_to_cover"], color="#8e44ad", lw=1.8, label="days_to_cover")
    axes[0].axvline(settlement_date, color="crimson", lw=1.5, ls="--", label="settlement_date")
    if pd.notna(linked_halt_date):
        axes[0].axvline(linked_halt_date, color="green", lw=1.5, ls="--", label="linked_halt_date")
    axes[0].legend(loc="upper left")
    axes[0].set_ylabel("days")
    axes[0].set_title(f"{ticker} days_to_cover around {settlement_date.date()}")

    axes[1].plot(window["settlement_date"], window["short_interest"], color="#2c3e50", lw=1.8, label="short_interest")
    axes[1].axvline(settlement_date, color="crimson", lw=1.5, ls="--")
    if pd.notna(linked_halt_date):
        axes[1].axvline(linked_halt_date, color="green", lw=1.5, ls="--")
    axes[1].set_ylabel("shares")

    axes[2].plot(window["settlement_date"], window["avg_daily_volume"], color="#16a085", lw=1.8, label="avg_daily_volume")
    axes[2].axvline(settlement_date, color="crimson", lw=1.5, ls="--")
    if pd.notna(linked_halt_date):
        axes[2].axvline(linked_halt_date, color="green", lw=1.5, ls="--")
    axes[2].set_ylabel("ADV")
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.show()


def build_short_viewer(cache_root: Path = DEFAULT_SHORT_AUDIT_CACHE, finra_root: Path = DEFAULT_FINRA_ROOT) -> widgets.VBox:
    payload = load_short_viewer_inputs(cache_root)
    sv = payload["sv_candidates"].copy()
    si = payload["si_candidates"].copy()

    if not sv.empty:
        sv["case_label"] = sv.apply(
            lambda r: f"{r['ticker']} | {pd.to_datetime(r['date']).date()} | {r['market_link_bucket']} | ratio={r['short_volume_ratio']:.2f}",
            axis=1,
        )
    if not si.empty:
        si["case_label"] = si.apply(
            lambda r: f"{r['ticker']} | {pd.to_datetime(r['settlement_date']).date()} | {r['context_bucket']} | dtc={r['days_to_cover']:.2f}",
            axis=1,
        )

    mode = widgets.ToggleButtons(
        options=[("short_volume", "short_volume"), ("short_interest", "short_interest")],
        description="mode",
    )
    bucket = widgets.Dropdown(description="bucket")
    case = widgets.Dropdown(description="case", layout=widgets.Layout(width="95%"))
    out = widgets.Output()
    case._current_df = pd.DataFrame()
    sync_state = {"busy": False}

    def refresh_buckets(*_):
        sync_state["busy"] = True
        df = sv if mode.value == "short_volume" else si
        bucket_col = "market_link_bucket" if mode.value == "short_volume" else "context_bucket"
        opts = sorted(df[bucket_col].dropna().astype(str).unique().tolist()) if not df.empty else []
        case._current_df = pd.DataFrame()
        case.options = []
        bucket.options = opts
        if opts:
            bucket.value = opts[0]
        sync_state["busy"] = False

    def refresh_cases(*_):
        if sync_state["busy"]:
            return
        sync_state["busy"] = True
        df = sv if mode.value == "short_volume" else si
        bucket_col = "market_link_bucket" if mode.value == "short_volume" else "context_bucket"
        if df.empty or bucket.value is None:
            case._current_df = pd.DataFrame()
            case.options = []
            sync_state["busy"] = False
            return
        sub = df[df[bucket_col].astype(str) == str(bucket.value)].copy()
        sort_col = "short_volume_ratio" if mode.value == "short_volume" else "days_to_cover"
        sub = sub.sort_values(sort_col, ascending=False).reset_index(drop=True)
        case.options = [(lab, idx) for idx, lab in enumerate(sub["case_label"].tolist())]
        case._current_df = sub
        if len(sub):
            case.value = 0
        sync_state["busy"] = False

    def render(*_):
        if sync_state["busy"]:
            return
        out.clear_output(wait=True)
        with out:
            sub = getattr(case, "_current_df", pd.DataFrame())
            if sub.empty or case.value is None:
                display(Markdown("_No hay casos para el bucket seleccionado._"))
                return
            row = sub.iloc[int(case.value)]
            if mode.value == "short_volume":
                if "date" not in row.index:
                    display(Markdown("_Estado inconsistente del widget: faltan columnas de `short_volume`. Vuelve a seleccionar el bucket._"))
                    return
                _render_short_volume_case(row, finra_root)
            else:
                if "settlement_date" not in row.index:
                    display(Markdown("_Estado inconsistente del widget: faltan columnas de `short_interest`. Vuelve a seleccionar el bucket._"))
                    return
                _render_short_interest_case(row, finra_root)

    mode.observe(refresh_buckets, names="value")
    bucket.observe(refresh_cases, names="value")
    case.observe(render, names="value")
    refresh_buckets()
    refresh_cases()
    render()
    return widgets.VBox([mode, bucket, case, out])
