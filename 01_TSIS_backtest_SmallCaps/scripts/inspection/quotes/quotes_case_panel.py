from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Iterable

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, clear_output, display


QUOTES_CACHE_DIR = Path(
    r"C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache_v2"
)
DAILY_OHLCV_ROOT = Path(r"D:\ohlcv_daily")
REFERENCE_IDENTITY_SNAPSHOT_PATH = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\cache_v2\reference_identity_snapshot.parquet"
)
REFERENCE_DIVIDEND_CASE_INDEX_PATH = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\cache_v2\reference_dividend_case_index.parquet"
)
REFERENCE_SPLIT_CASE_INDEX_PATH = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\auditoria\reference\cache_v2\reference_split_case_index.parquet"
)

QUOTES_CERT_IMG_DIR = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\certification\quotes\img"
)

QUOTES_GOOD_BUCKETS = [
    "clean_pass_or_other",
    "soft_crossed_micro_noise",
    "persistent_soft_crossed_low",
    "utc_rollover_large_day_clean",
]

QUOTES_REVIEW_BUCKETS = [
    "persistent_soft_crossed_mid_large_scale",
    "large_file_threshold_edge_hard_many_crosses",
]

QUOTES_BAD_BUCKETS = [
    "medium_file_threshold_edge_hard_many_crosses",
    "high_hard_crossed_10_to_20",
]

POSITIVE_BUCKET_LABELS = {
    "no_positive_cross": "no positive cross",
    "positive_cross_mild_lt5bps": "mild <5 bps",
    "positive_cross_moderate_5to25bps": "moderate 5-25 bps",
    "positive_cross_severe_ge25bps": "severe >=25 bps",
}

PRIMARY_EXCHANGE_LABELS = {
    "XNAS": "NASDAQ",
    "XNYS": "NYSE",
    "XASE": "NYSE American",
    "ARCX": "NYSE Arca",
}

HISTORICAL_CONTEXT_CASES = {
    ("AMC", "2021-06-03"): "01_persistent_mid_large_explained_amc_2021_06_03.png",
    ("MRIN", "2021-06-29"): "02_persistent_mid_large_explained_mrin_2021_06_29.png",
    ("GLXG", "2025-04-08"): "03_persistent_mid_large_unexplained_glxg_2025_04_08.png",
    ("WLGS", "2025-06-11"): "04_persistent_mid_large_unexplained_wlgs_2025_06_11.png",
    ("SNDL", "2021-01-28"): "05_large_file_threshold_explained_sndl_2021_01_28.png",
    ("WKHS", "2021-02-23"): "06_large_file_threshold_explained_wkhs_2021_02_23.png",
    ("CTIC", "2006-09-19"): "07_large_file_threshold_unexplained_ctic_2006_09_19.png",
    ("CNTB", "2022-06-29"): "08_large_file_threshold_unexplained_cntb_2022_06_29.png",
    ("BJDX", "2024-12-12"): "09_medium_file_threshold_halt_context_bjdx_2024_12_12.png",
    ("GTE", "2005-08-01"): "10_medium_file_threshold_halt_context_gte_2005_08_01.png",
    ("UFAB", "2023-03-09"): "11_medium_file_threshold_unexplained_ufab_2023_03_09.png",
    ("DGLY", "2011-10-06"): "12_medium_file_threshold_unexplained_dgly_2011_10_06.png",
    ("CTNT", "2024-05-20"): "13_high_hard_crossed_halt_context_ctnt_2024_05_20.png",
    ("DNA", "2005-03-14"): "14_high_hard_crossed_halt_context_dna_2005_03_14.png",
    ("SGC", "2013-11-04"): "15_high_hard_crossed_unexplained_sgc_2013_11_04.png",
    ("SELF", "2016-06-28"): "16_high_hard_crossed_unexplained_self_2016_06_28.png",
}

_REFERENCE_IDENTITY_CACHE: pd.DataFrame | None = None
_REFERENCE_DIVIDEND_CACHE: pd.DataFrame | None = None
_REFERENCE_SPLIT_CACHE: pd.DataFrame | None = None


@dataclass(frozen=True)
class QuotesInspectionScope:
    name: str
    buckets: tuple[str, ...]
    export_folder: str
    notes: str


SCOPES = {
    "good": QuotesInspectionScope(
        name="good",
        buckets=tuple(QUOTES_GOOD_BUCKETS),
        export_folder="good_sample",
        notes="Muestra historica representativa de la franja buena de quotes.",
    ),
    "review": QuotesInspectionScope(
        name="review",
        buckets=tuple(QUOTES_REVIEW_BUCKETS),
        export_folder="review",
        notes="Casos review donde contexto y calidad local deben separarse.",
    ),
    "bad": QuotesInspectionScope(
        name="bad",
        buckets=tuple(QUOTES_BAD_BUCKETS),
        export_folder="bad",
        notes="Casos bad con crossed economicamente demasiado agresivo.",
    ),
}


def get_scope(name: str) -> QuotesInspectionScope:
    if name not in SCOPES:
        raise KeyError(f"Unknown quotes inspection scope: {name}")
    return SCOPES[name]


def expected_output_dir(project_root: Path, scope_name: str) -> Path:
    scope = get_scope(scope_name)
    return (
        project_root
        / "01_foundations"
        / "inspection_dossiers"
        / "quotes"
        / "evidence_assets"
        / scope.export_folder
    )


def flatten_buckets(scope_names: Iterable[str]) -> list[str]:
    buckets: list[str] = []
    for scope_name in scope_names:
        for bucket in get_scope(scope_name).buckets:
            if bucket not in buckets:
                buckets.append(bucket)
    return buckets


def _read_cache(name: str) -> pd.DataFrame:
    path = QUOTES_CACHE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Quotes historical cache not found: {path}")
    return pd.read_parquet(path)


def load_quotes_taxonomy_summary() -> pd.DataFrame:
    return _read_cache("taxonomy_summary_cd_lt1b.parquet")


def load_quotes_case_index() -> pd.DataFrame:
    return _read_cache("case_index_top50_cd_lt1b.parquet")


def load_quotes_crossed_gap_cases() -> pd.DataFrame:
    return _read_cache("crossed_gap_severity_cases_cd_lt1b.parquet")


def load_quotes_positive_cross_review_cases() -> pd.DataFrame:
    return _read_cache("positive_cross_review_cases_cd_lt1b.parquet")


def load_quotes_micro_sample() -> pd.DataFrame:
    return _read_cache("micro_sample_cd_lt1b.parquet")


def load_quotes_severity_counts() -> pd.DataFrame:
    return _read_cache("severity_counts_cd_lt1b.parquet")


def load_quotes_root_mix() -> pd.DataFrame:
    return _read_cache("root_mix_cd_lt1b.parquet")


def load_quotes_crossed_gap_summary() -> pd.DataFrame:
    return _read_cache("crossed_gap_severity_summary_cd_lt1b.parquet")


def load_quotes_positive_cross_summary() -> pd.DataFrame:
    return _read_cache("positive_cross_review_summary_cd_lt1b.parquet")


def load_quotes_integer_anomaly() -> pd.DataFrame:
    return _read_cache("integer_anomaly_cd_lt1b.parquet")


def load_quotes_timestamp_view() -> pd.DataFrame:
    return _read_cache("timestamp_view_cd_lt1b.parquet")


def build_quotes_case_pool() -> pd.DataFrame:
    base = load_quotes_positive_cross_review_cases().copy()
    if base.empty:
        return base

    focus_taxonomies = QUOTES_REVIEW_BUCKETS + QUOTES_BAD_BUCKETS
    base = base.loc[base["taxonomy"].isin(focus_taxonomies)].copy()
    base = base.loc[
        pd.to_numeric(base["crossed_rows_ask_positive"], errors="coerce").fillna(0).gt(0)
    ].copy()
    if base.empty:
        return base

    base["scope_name"] = "other"
    base.loc[base["taxonomy"].isin(QUOTES_REVIEW_BUCKETS), "scope_name"] = "review"
    base.loc[base["taxonomy"].isin(QUOTES_BAD_BUCKETS), "scope_name"] = "bad"

    base["date_str"] = pd.to_datetime(base["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    base["case_label"] = (
        base["ticker"].astype(str)
        + " | "
        + base["date_str"].astype(str)
        + " | "
        + base["positive_cross_bucket"].astype(str)
        + " | med="
        + pd.to_numeric(base["cross_rel_bps_median_ask_positive"], errors="coerce").round(2).astype(str)
        + " bps"
        + " | +"
        + pd.to_numeric(base["crossed_rows_ask_positive"], errors="coerce")
        .fillna(0)
        .astype(int)
        .astype(str)
    )
    return base.sort_values(
        [
            "taxonomy",
            "positive_cross_bucket",
            "cross_rel_bps_median_ask_positive",
            "crossed_rows_ask_positive",
        ],
        ascending=[True, True, False, False],
    ).reset_index(drop=True)


def _classify_positive_cross_bucket_from_file(df: pd.DataFrame) -> str:
    positive = pd.to_numeric(df.loc[df["cross_positive"], "gap_bps"], errors="coerce").dropna()
    if positive.empty:
        return "no_positive_cross"
    p90 = float(positive.quantile(0.90))
    if p90 < 5.0:
        return "positive_cross_mild_lt5bps"
    if p90 < 25.0:
        return "positive_cross_moderate_5to25bps"
    return "positive_cross_severe_ge25bps"


def _select_good_examples() -> pd.DataFrame:
    df = load_quotes_micro_sample().copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["severity"] = df["severity"].astype(str)
    df["root"] = df["root"].astype(str)
    df["rows"] = pd.to_numeric(df["rows"], errors="coerce")
    df["m.crossed_ratio_pct"] = pd.to_numeric(df["m.crossed_ratio_pct"], errors="coerce")
    df["m.crossed_rows"] = pd.to_numeric(df["m.crossed_rows"], errors="coerce")
    df["m.ask_integer_pct"] = pd.to_numeric(df["m.ask_integer_pct"], errors="coerce")
    df["m.ask_eq_round_bid_pct"] = pd.to_numeric(df["m.ask_eq_round_bid_pct"], errors="coerce")
    df["m.timestamp_out_of_partition_day"] = df["m.timestamp_out_of_partition_day"].fillna(False).astype(bool)

    selections: list[pd.DataFrame] = []

    clean = df.loc[
        df["severity"].eq("PASS")
        & df["m.crossed_ratio_pct"].fillna(0).eq(0)
        & (~df["m.timestamp_out_of_partition_day"])
    ].sort_values(["rows", "m.ask_integer_pct"], ascending=[False, True]).head(3).copy()
    clean["taxonomy"] = "clean_pass_or_other"
    selections.append(clean)

    micro = df.loc[
        df["severity"].eq("SOFT_FAIL")
        & df["m.crossed_ratio_pct"].gt(0)
        & df["m.crossed_ratio_pct"].le(0.05)
        & (~df["m.timestamp_out_of_partition_day"])
    ].sort_values(["rows", "m.crossed_ratio_pct"], ascending=[False, True]).head(3).copy()
    micro["taxonomy"] = "soft_crossed_micro_noise"
    selections.append(micro)

    low = df.loc[
        df["severity"].eq("SOFT_FAIL")
        & df["m.crossed_ratio_pct"].gt(0.05)
        & df["m.crossed_ratio_pct"].le(0.5)
        & (~df["m.timestamp_out_of_partition_day"])
    ].sort_values(["rows", "m.crossed_ratio_pct"], ascending=[False, True]).head(3).copy()
    low["taxonomy"] = "persistent_soft_crossed_low"
    selections.append(low)

    rollover = df.loc[
        df["severity"].isin(["PASS", "SOFT_FAIL"])
        & df["m.timestamp_out_of_partition_day"]
        & df["m.crossed_ratio_pct"].le(0.05)
    ].sort_values(["rows", "m.crossed_ratio_pct"], ascending=[False, True]).head(3).copy()
    rollover["taxonomy"] = "utc_rollover_large_day_clean"
    selections.append(rollover)

    out = pd.concat(selections, ignore_index=True)
    out["scope_name"] = "good"
    out["date_str"] = out["date"].dt.strftime("%Y-%m-%d")
    out["case_label"] = (
        out["taxonomy"].astype(str)
        + " | "
        + out["ticker"].astype(str)
        + " | "
        + out["date_str"].astype(str)
        + " | rows="
        + out["rows"].fillna(0).astype(int).astype(str)
    )
    return out.reset_index(drop=True)


def build_quotes_good_pool() -> pd.DataFrame:
    base = _select_good_examples().copy()
    rows: list[dict[str, object]] = []
    for _, row in base.iterrows():
        case_df = _load_case_frame(row["file"])
        crossed = case_df.loc[case_df["crossed"]].copy()
        positive = case_df.loc[case_df["cross_positive"]].copy()
        gap_pos = pd.to_numeric(positive["gap_bps"], errors="coerce").dropna()
        bucket = _classify_positive_cross_bucket_from_file(case_df)
        crossed_total = int(crossed.shape[0])
        crossed_ask_zero = int(case_df["ask_zero_cross"].sum())
        crossed_ask_positive = int(case_df["ask_positive_cross"].sum())
        ask_zero_share = (crossed_ask_zero / crossed_total * 100.0) if crossed_total > 0 else 0.0
        ask_positive_share = (crossed_ask_positive / crossed_total * 100.0) if crossed_total > 0 else 0.0
        rows.append(
            {
                "scope_name": "good",
                "taxonomy": row["taxonomy"],
                "ticker": str(row["ticker"]).upper(),
                "date": row["date"],
                "date_str": row["date_str"],
                "severity": row["severity"],
                "root": row["root"],
                "rows": int(row["rows"]),
                "m.crossed_ratio_pct": float(pd.to_numeric(row["m.crossed_ratio_pct"], errors="coerce")),
                "crossed_rows_raw": crossed_total,
                "crossed_rows_ask_zero": crossed_ask_zero,
                "crossed_rows_ask_positive": crossed_ask_positive,
                "crossed_ask_zero_share_pct": ask_zero_share,
                "crossed_ask_positive_share_pct": ask_positive_share,
                "m.ask_integer_pct": float(pd.to_numeric(row["m.ask_integer_pct"], errors="coerce")),
                "m.ask_eq_round_bid_pct": float(pd.to_numeric(row["m.ask_eq_round_bid_pct"], errors="coerce")),
                "cross_rel_bps_median_ask_positive": float(gap_pos.median()) if not gap_pos.empty else 0.0,
                "cross_rel_bps_p90_ask_positive": float(gap_pos.quantile(0.90)) if not gap_pos.empty else 0.0,
                "positive_cross_bucket": bucket,
                "file": row["file"],
                "case_label": row["case_label"],
            }
        )
    out = pd.DataFrame(rows)
    return out.sort_values(["taxonomy", "rows"], ascending=[True, False]).reset_index(drop=True)


def _load_case_frame(file_path: str) -> pd.DataFrame:
    cols = [
        "timestamp",
        "bid_price",
        "ask_price",
        "bid_size",
        "ask_size",
        "bid_exchange",
        "ask_exchange",
    ]
    df = pd.read_parquet(file_path, columns=cols)
    df["bid_price"] = pd.to_numeric(df["bid_price"], errors="coerce")
    df["ask_price"] = pd.to_numeric(df["ask_price"], errors="coerce")
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["ts_ny"] = pd.to_datetime(df["timestamp"], unit="ns", utc=True, errors="coerce").dt.tz_convert(
        "America/New_York"
    )
    df["cross_positive"] = df["bid_price"].gt(df["ask_price"]) & df["ask_price"].gt(0)
    df["crossed"] = df["bid_price"].gt(df["ask_price"])
    df["gap"] = df["bid_price"] - df["ask_price"]
    df["mid"] = (df["bid_price"] + df["ask_price"]) / 2.0
    df["gap_bps"] = np.where(df["mid"] > 0, df["gap"] / df["mid"] * 10000.0, np.nan)
    df["ask_zero_cross"] = df["crossed"] & df["ask_price"].eq(0)
    df["ask_positive_cross"] = df["cross_positive"]
    df["bid_integer_like"] = np.isclose(df["bid_price"] % 1.0, 0.0, atol=1e-9)
    df["ask_integer_like"] = np.isclose(df["ask_price"] % 1.0, 0.0, atol=1e-9)
    df["ask_eq_round_bid_like"] = np.isclose(df["ask_price"], np.round(df["bid_price"]), atol=1e-9)
    return df


def _build_window_view(df: pd.DataFrame, window: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    cross_idx = np.flatnonzero(df["cross_positive"].fillna(False).to_numpy())
    if len(cross_idx) == 0:
        return df.iloc[0:0].copy(), df.iloc[0:0].copy()
    start = max(int(cross_idx.min()) - window, 0)
    end = min(int(cross_idx.max()) + window + 1, len(df))
    view = df.iloc[start:end].copy()
    if len(view) > 4000:
        step = max(int(np.ceil(len(view) / 4000)), 1)
        sampled = view.iloc[::step].copy()
        crossed_view = view.loc[view["cross_positive"]].copy()
        view = (
            pd.concat([sampled, crossed_view], ignore_index=False)
            .sort_index()
            .loc[lambda x: ~x.index.duplicated(keep="first")]
            .copy()
        )
    crossed_view = view.loc[view["cross_positive"]].copy()
    return view, crossed_view


def _safe_case_slug(row: pd.Series) -> str:
    return f"{str(row['ticker']).upper()}_{str(row['date_str']).replace('-', '_')}"


def _match_historical_context_image(row: pd.Series) -> Path | None:
    key = (str(row["ticker"]).upper(), str(row["date_str"]))
    fname = HISTORICAL_CONTEXT_CASES.get(key)
    if not fname:
        return None
    path = QUOTES_CERT_IMG_DIR / fname
    return path if path.exists() else None


def _summary_frame(row: pd.Series) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "scope": row["scope_name"],
                "taxonomy": row["taxonomy"],
                "positive_cross_bucket": row["positive_cross_bucket"],
                "ticker": row["ticker"],
                "date": row["date_str"],
                "severity": row["severity"],
                "root": row["root"],
                "rows_file": int(row["rows"]),
                "crossed_ratio_pct": float(row["m.crossed_ratio_pct"]),
                "crossed_rows_raw": int(row["crossed_rows_raw"]),
                "crossed_rows_ask_zero": int(row["crossed_rows_ask_zero"]),
                "crossed_rows_ask_positive": int(row["crossed_rows_ask_positive"]),
                "ask_zero_share_pct": float(row["crossed_ask_zero_share_pct"]),
                "ask_positive_share_pct": float(row["crossed_ask_positive_share_pct"]),
                "ask_integer_pct": float(row["m.ask_integer_pct"]),
                "median_bps_ask_positive": float(row["cross_rel_bps_median_ask_positive"]),
                "p90_bps_ask_positive": float(row["cross_rel_bps_p90_ask_positive"]),
                "file": row["file"],
            }
        ]
    )


def _load_reference_identity_snapshot() -> pd.DataFrame:
    global _REFERENCE_IDENTITY_CACHE
    if _REFERENCE_IDENTITY_CACHE is None:
        df = pd.read_parquet(
            REFERENCE_IDENTITY_SNAPSHOT_PATH,
            columns=["ticker", "name", "market", "locale", "primary_exchange"],
        ).copy()
        df["ticker"] = df["ticker"].astype(str).str.upper()
        _REFERENCE_IDENTITY_CACHE = df.drop_duplicates(subset=["ticker"], keep="first")
    return _REFERENCE_IDENTITY_CACHE.copy()


def _lookup_company_metadata(ticker: str) -> dict[str, str]:
    df = _load_reference_identity_snapshot()
    hit = df.loc[df["ticker"].eq(str(ticker).upper())]
    if hit.empty:
        return {
            "company_name": "",
            "primary_exchange": "",
            "primary_exchange_label": "",
            "market": "",
            "locale": "",
        }
    row = hit.iloc[0]
    primary_exchange = str(row.get("primary_exchange", "") or "").strip()
    return {
        "company_name": str(row.get("name", "") or "").strip(),
        "primary_exchange": primary_exchange,
        "primary_exchange_label": PRIMARY_EXCHANGE_LABELS.get(primary_exchange, primary_exchange),
        "market": str(row.get("market", "") or "").strip(),
        "locale": str(row.get("locale", "") or "").strip(),
    }


def _load_reference_dividend_case_index() -> pd.DataFrame:
    global _REFERENCE_DIVIDEND_CACHE
    if _REFERENCE_DIVIDEND_CACHE is None:
        df = pd.read_parquet(
            REFERENCE_DIVIDEND_CASE_INDEX_PATH,
            columns=["ticker", "cash_amount", "dividend_type", "ex_dividend_date"],
        ).copy()
        df["ticker"] = df["ticker"].astype(str).str.upper()
        df["cash_amount"] = pd.to_numeric(df["cash_amount"], errors="coerce").fillna(0.0)
        df["ex_dividend_date"] = pd.to_datetime(df["ex_dividend_date"], errors="coerce")
        _REFERENCE_DIVIDEND_CACHE = df
    return _REFERENCE_DIVIDEND_CACHE.copy()


def _load_post_event_dividends(ticker: str, event_day: pd.Timestamp) -> pd.DataFrame:
    df = _load_reference_dividend_case_index()
    out = df.loc[df["ticker"].eq(str(ticker).upper())].copy()
    out = out.loc[out["ex_dividend_date"].gt(event_day)].copy()
    out = out.loc[out["cash_amount"].gt(0)].sort_values("ex_dividend_date").reset_index(drop=True)
    return out


def _load_reference_split_case_index() -> pd.DataFrame:
    global _REFERENCE_SPLIT_CACHE
    if _REFERENCE_SPLIT_CACHE is None:
        df = pd.read_parquet(
            REFERENCE_SPLIT_CASE_INDEX_PATH,
            columns=["ticker", "execution_date", "split_from", "split_to", "split_ratio", "split_bucket"],
        ).copy()
        df["ticker"] = df["ticker"].astype(str).str.upper()
        df["execution_date"] = pd.to_datetime(df["execution_date"], errors="coerce")
        for col in ["split_from", "split_to", "split_ratio"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        _REFERENCE_SPLIT_CACHE = df
    return _REFERENCE_SPLIT_CACHE.copy()


def _load_future_splits(ticker: str, event_day: pd.Timestamp) -> pd.DataFrame:
    df = _load_reference_split_case_index()
    out = df.loc[df["ticker"].eq(str(ticker).upper())].copy()
    out = out.loc[out["split_bucket"].eq("good_split_event")].copy()
    out = out.loc[out["execution_date"].gt(event_day)].copy()
    out = out.loc[out["split_ratio"].gt(0)].sort_values("execution_date").reset_index(drop=True)
    return out


def _load_daily_series_for_window(ticker: str, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    years = sorted({start_date.year, end_date.year})
    frames: list[pd.DataFrame] = []
    ticker = str(ticker).upper()

    for year in years:
        path = DAILY_OHLCV_ROOT / f"ticker={ticker}" / f"year={year:04d}" / f"day_aggs_{ticker}_{year:04d}.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path, columns=["date", "o", "h", "l", "c", "v"]).copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        for col in ["o", "h", "l", "c", "v"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        frames.append(df)

    if not frames:
        return pd.DataFrame(columns=["date", "o", "h", "l", "c", "v"])

    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    mask = out["date"].between(start_date, end_date)
    return out.loc[mask].reset_index(drop=True)


def _build_dividend_adjustment_payload(
    ticker: str,
    daily_ctx: pd.DataFrame,
    dividends: pd.DataFrame,
) -> pd.DataFrame:
    out = daily_ctx.copy()
    if out.empty:
        return out

    out["future_dividend_sum"] = 0.0
    out["future_dividend_factor"] = 1.0
    for src, dst in [("o", "o_adj_proxy"), ("h", "h_adj_proxy"), ("l", "l_adj_proxy"), ("c", "c_adj_proxy")]:
        out[dst] = pd.to_numeric(out[src], errors="coerce")

    if dividends.empty:
        return out

    start_date = pd.Timestamp(out["date"].min()) - pd.Timedelta(days=7)
    end_date = pd.Timestamp(dividends["ex_dividend_date"].max()) + pd.Timedelta(days=7)
    daily_full = _load_daily_series_for_window(ticker, start_date, end_date).sort_values("date").reset_index(drop=True)
    if daily_full.empty:
        return out

    dividend_rows: list[dict[str, float | pd.Timestamp]] = []
    for _, div in dividends.iterrows():
        ex_date = pd.Timestamp(div["ex_dividend_date"])
        cash = float(div["cash_amount"])
        prev = daily_full.loc[daily_full["date"].lt(ex_date)].sort_values("date")
        if prev.empty:
            continue
        prev_close = float(pd.to_numeric(prev.iloc[-1]["c"], errors="coerce"))
        if not np.isfinite(prev_close) or prev_close <= 0 or cash <= 0 or cash >= prev_close:
            continue
        factor = 1.0 - (cash / prev_close)
        if factor <= 0 or not np.isfinite(factor):
            continue
        dividend_rows.append(
            {
                "ex_dividend_date": ex_date,
                "cash_amount": cash,
                "prev_close": prev_close,
                "adj_factor": factor,
            }
        )

    if not dividend_rows:
        return out

    divf = pd.DataFrame(dividend_rows).sort_values("ex_dividend_date").reset_index(drop=True)
    future_sums: list[float] = []
    future_factors: list[float] = []

    for d in out["date"]:
        active = divf.loc[divf["ex_dividend_date"].gt(pd.Timestamp(d))]
        future_sums.append(float(active["cash_amount"].sum()) if not active.empty else 0.0)
        future_factors.append(float(active["adj_factor"].prod()) if not active.empty else 1.0)

    out["future_dividend_sum"] = future_sums
    out["future_dividend_factor"] = future_factors
    for src, dst in [("o", "o_adj_proxy"), ("h", "h_adj_proxy"), ("l", "l_adj_proxy"), ("c", "c_adj_proxy")]:
        out[dst] = pd.to_numeric(out[src], errors="coerce") * pd.to_numeric(out["future_dividend_factor"], errors="coerce")
    return out


def _summarize_event_quote_scale(row: pd.Series) -> dict[str, float]:
    df = _load_case_frame(row["file"])
    valid = df.loc[df["bid_price"].gt(0) & df["ask_price"].gt(0)].copy()
    if valid.empty:
        return {"quote_mid_raw_event": np.nan, "quote_mid_split_norm_event": np.nan}
    valid["mid"] = (valid["bid_price"] + valid["ask_price"]) / 2.0
    quote_mid_raw_event = float(valid["mid"].median()) if valid["mid"].dropna().size else np.nan
    return {"quote_mid_raw_event": quote_mid_raw_event}


def _build_split_normalization_series(dates: pd.Series, splits: pd.DataFrame) -> pd.Series:
    factors: list[float] = []
    for d in pd.to_datetime(dates, errors="coerce"):
        active = splits.loc[splits["execution_date"].gt(pd.Timestamp(d))]
        factor = float(active["split_ratio"].prod()) if not active.empty else 1.0
        factors.append(factor if np.isfinite(factor) and factor > 0 else 1.0)
    return pd.Series(factors, index=dates.index if hasattr(dates, "index") else None, dtype=float)


def _candidate_daily_quote_path(source_file: Path, ticker: str, day: pd.Timestamp) -> Path:
    ticker_idx = source_file.parts.index(ticker)
    root = Path(*source_file.parts[:ticker_idx])
    return (
        root
        / ticker
        / f"year={day.year:04d}"
        / f"month={day.month:02d}"
        / f"day={day.day:02d}"
        / "quotes.parquet"
    )


def _load_quote_daily_context(row: pd.Series, days_before: int = 15, days_after: int = 15) -> pd.DataFrame:
    event_day = pd.Timestamp(str(row["date_str"]))
    source_file = Path(str(row["file"]))
    ticker = str(row["ticker"])
    records: list[dict[str, float | str]] = []

    for day in pd.date_range(event_day - pd.Timedelta(days=days_before), event_day + pd.Timedelta(days=days_after), freq="D"):
        candidate = _candidate_daily_quote_path(source_file, ticker, day)
        if not candidate.exists():
            records.append(
                {
                    "date": day,
                    "available": 0,
                    "rows": np.nan,
                    "median_mid": np.nan,
                    "last_mid": np.nan,
                    "crossed_ratio_pct": np.nan,
                    "median_gap_bps_pos": np.nan,
                    "max_gap_bps_pos": np.nan,
                }
            )
            continue

        df = pd.read_parquet(candidate, columns=["bid_price", "ask_price"])
        bid = pd.to_numeric(df["bid_price"], errors="coerce")
        ask = pd.to_numeric(df["ask_price"], errors="coerce")
        mid = (bid + ask) / 2.0
        valid_mid = mid.where(bid.gt(0) & ask.gt(0))
        cross_pos = bid.gt(ask) & ask.gt(0)
        gap = bid - ask
        gap_bps = np.where(valid_mid > 0, gap / valid_mid * 10000.0, np.nan)
        gap_bps_pos = pd.Series(gap_bps).where(cross_pos)

        records.append(
            {
                "date": day,
                "available": 1,
                "rows": int(len(df)),
                "median_mid": float(valid_mid.dropna().median()) if valid_mid.dropna().size else np.nan,
                "last_mid": float(valid_mid.dropna().iloc[-1]) if valid_mid.dropna().size else np.nan,
                "crossed_ratio_pct": float(cross_pos.mean() * 100.0) if len(df) else np.nan,
                "median_gap_bps_pos": float(gap_bps_pos.dropna().median()) if gap_bps_pos.dropna().size else np.nan,
                "max_gap_bps_pos": float(gap_bps_pos.dropna().max()) if gap_bps_pos.dropna().size else np.nan,
            }
        )

    return pd.DataFrame(records)


def _load_quote_month_session_trace(row: pd.Series, days_before: int = 15, days_after: int = 15) -> pd.DataFrame:
    event_day = pd.Timestamp(str(row["date_str"]))
    source_file = Path(str(row["file"]))
    ticker = str(row["ticker"])
    frames: list[pd.DataFrame] = []
    day_counter = 0

    for day in pd.date_range(event_day - pd.Timedelta(days=days_before), event_day + pd.Timedelta(days=days_after), freq="D"):
        candidate = _candidate_daily_quote_path(source_file, ticker, day)
        if not candidate.exists():
            day_counter += 1
            continue

        df = pd.read_parquet(candidate, columns=["timestamp", "bid_price", "ask_price"]).copy()
        if df.empty:
            day_counter += 1
            continue

        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
        df["ts_ny"] = pd.to_datetime(df["timestamp"], unit="ns", utc=True, errors="coerce").dt.tz_convert(
            "America/New_York"
        )
        df["bid_price"] = pd.to_numeric(df["bid_price"], errors="coerce")
        df["ask_price"] = pd.to_numeric(df["ask_price"], errors="coerce")
        df = df.dropna(subset=["ts_ny", "bid_price", "ask_price"]).copy()
        if df.empty:
            day_counter += 1
            continue

        # Monthly context should be readable, not microsecond-noisy: resample to 1-minute buckets.
        df["ts_min"] = df["ts_ny"].dt.floor("min")
        df["cross_positive"] = df["bid_price"].gt(df["ask_price"]) & df["ask_price"].gt(0)
        mid = (df["bid_price"] + df["ask_price"]) / 2.0
        gap = df["bid_price"] - df["ask_price"]
        df["gap_bps"] = np.where(mid > 0, gap / mid * 10000.0, np.nan)

        grouped = (
            df.groupby("ts_min", dropna=True)
            .agg(
                bid_price=("bid_price", "median"),
                ask_price=("ask_price", "median"),
                cross_positive=("cross_positive", "max"),
                gap_bps=("gap_bps", "median"),
                gap_bps_max=("gap_bps", "max"),
            )
            .reset_index()
            .rename(columns={"ts_min": "ts_ny"})
        )
        if grouped.empty:
            day_counter += 1
            continue

        secs = grouped["ts_ny"].dt.hour.astype(int) * 3600 + grouped["ts_ny"].dt.minute.astype(int) * 60
        session_x = day_counter + secs / (16 * 3600.0)
        grouped["session_x"] = session_x
        grouped["date"] = day.normalize()
        grouped["cross_positive"] = grouped["cross_positive"].fillna(False).astype(bool)
        grouped["gap_bps"] = pd.to_numeric(grouped["gap_bps"], errors="coerce")
        grouped["gap_bps_max"] = pd.to_numeric(grouped["gap_bps_max"], errors="coerce")
        frames.append(grouped[["date", "ts_ny", "session_x", "bid_price", "ask_price", "cross_positive", "gap_bps", "gap_bps_max"]])
        day_counter += 1

    if not frames:
        return pd.DataFrame(columns=["date", "ts_ny", "session_x", "bid_price", "ask_price", "cross_positive", "gap_bps", "gap_bps_max"])
    return pd.concat(frames, ignore_index=True)


def _load_daily_month_context(row: pd.Series, days_before: int = 15, days_after: int = 15) -> pd.DataFrame:
    event_day = pd.Timestamp(str(row["date_str"]))
    ticker = str(row["ticker"]).upper()
    years = sorted(
        {
            (event_day - pd.Timedelta(days=days_before)).year,
            event_day.year,
            (event_day + pd.Timedelta(days=days_after)).year,
        }
    )
    frames: list[pd.DataFrame] = []

    for year in years:
        path = DAILY_OHLCV_ROOT / f"ticker={ticker}" / f"year={year:04d}" / f"day_aggs_{ticker}_{year:04d}.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path, columns=["date", "o", "h", "l", "c", "v"]).copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        for col in ["o", "h", "l", "c", "v"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        frames.append(df)

    if not frames:
        return pd.DataFrame(columns=["date", "o", "h", "l", "c", "v"])

    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    mask = out["date"].between(event_day - pd.Timedelta(days=days_before), event_day + pd.Timedelta(days=days_after))
    return out.loc[mask].reset_index(drop=True)


def _save_event_month_context(row: pd.Series, out_path: Path, days_before: int = 15, days_after: int = 15) -> None:
    daily_ctx = _load_daily_month_context(row, days_before=days_before, days_after=days_after)
    quote_ctx = _load_quote_daily_context(row, days_before=days_before, days_after=days_after)
    event_day = pd.Timestamp(str(row["date_str"]))

    merged = pd.merge(daily_ctx, quote_ctx, on="date", how="left")
    merged = merged.sort_values("date").reset_index(drop=True)
    if merged.empty:
        raise RuntimeError(f"No monthly context available for {row['ticker']} {row['date_str']}")

    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.2]})
    x = np.arange(len(merged))
    candle_width = 0.65

    for idx, rec in merged.iterrows():
        low = rec["l"]
        high = rec["h"]
        opn = rec["o"]
        cls = rec["c"]
        if pd.isna(low) or pd.isna(high) or pd.isna(opn) or pd.isna(cls):
            continue
        body_low = min(opn, cls)
        body_high = max(opn, cls)
        color = "#166534" if cls >= opn else "#991b1b"
        axes[0].vlines(idx, low, high, color="#111827", linewidth=0.8, alpha=0.9, zorder=1)
        body_height = max(body_high - body_low, 1e-6)
        rect = plt.Rectangle(
            (idx - candle_width / 2, body_low),
            candle_width,
            body_height,
            facecolor=color,
            edgecolor=color,
            alpha=0.9,
            zorder=2,
        )
        axes[0].add_patch(rect)

    event_mask = merged["date"].eq(event_day)
    if event_mask.any():
        event_idx = int(np.flatnonzero(event_mask.to_numpy())[0])
        axes[0].axvspan(event_idx - 0.55, event_idx + 0.55, color="#fde68a", alpha=0.35, zorder=0)
        event_close = float(merged.loc[event_mask, "c"].iloc[0])
        axes[0].annotate(
            f"event day\n{row['taxonomy']}\n{POSITIVE_BUCKET_LABELS.get(str(row['positive_cross_bucket']), str(row['positive_cross_bucket']))}",
            xy=(event_idx, event_close),
            xytext=(18, 24),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.35", fc="#fff7ed", ec="#d97706", alpha=0.95),
            arrowprops=dict(arrowstyle="->", color="#d97706"),
            fontsize=10,
        )

    axes[0].plot(x, merged["c"], color="#0f766e", linewidth=1.0, alpha=0.55, label="daily close")
    axes[0].set_title(f"{row['ticker']} | {row['date_str']} | contexto mensual del evento (-15d / +15d)")
    axes[0].set_ylabel("daily price")
    axes[0].legend(loc="upper right", frameon=True)

    axes[1].bar(x, merged["crossed_ratio_pct"], width=0.8, color="#93c5fd", alpha=0.8, label="crossed_ratio_pct")
    axes[1].plot(x, merged["max_gap_bps_pos"], color="#dc2626", marker="o", linewidth=1.2, label="max_gap_bps_pos")
    if event_mask.any():
        axes[1].axvspan(event_idx - 0.55, event_idx + 0.55, color="#fde68a", alpha=0.35)
    axes[1].axhline(5.0, color="#2563eb", linestyle="--", linewidth=1.0)
    axes[1].axhline(25.0, color="#111827", linestyle="--", linewidth=1.0)
    axes[1].set_ylabel("crossed_ratio / max_gap_bps")
    axes[1].set_xlabel("date")
    axes[1].set_title("El evento frente a sus dias vecinos")
    axes[1].legend(loc="upper right", frameon=True)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([d.strftime("%Y-%m-%d") for d in merged["date"]], rotation=45, ha="right")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_event_month_adjusted_proxy_context(
    row: pd.Series,
    out_path: Path,
    days_before: int = 15,
    days_after: int = 15,
) -> dict[str, float] | None:
    event_day = pd.Timestamp(str(row["date_str"]))
    daily_ctx = _load_daily_month_context(row, days_before=days_before, days_after=days_after)
    dividends = _load_post_event_dividends(str(row["ticker"]), event_day)
    splits = _load_future_splits(str(row["ticker"]), event_day)
    if daily_ctx.empty or (dividends.empty and splits.empty):
        return None

    adj = _build_dividend_adjustment_payload(str(row["ticker"]), daily_ctx, dividends).sort_values("date").reset_index(drop=True)
    total_future_div = float(dividends["cash_amount"].sum())
    split_factor_series = _build_split_normalization_series(adj["date"], splits)
    adj["future_split_factor"] = split_factor_series.to_numpy()
    adj["daily_split_norm_proxy"] = np.where(
        pd.to_numeric(adj["future_split_factor"], errors="coerce").gt(0),
        pd.to_numeric(adj["c"], errors="coerce") / pd.to_numeric(adj["future_split_factor"], errors="coerce"),
        np.nan,
    )

    event_mask = adj["date"].eq(event_day)
    event_close_raw = float(adj.loc[event_mask, "c"].iloc[0]) if event_mask.any() else np.nan
    event_close_adj = float(adj.loc[event_mask, "c_adj_proxy"].iloc[0]) if event_mask.any() else np.nan
    event_split_factor = float(adj.loc[event_mask, "future_split_factor"].iloc[0]) if event_mask.any() else 1.0
    event_daily_split_norm = float(adj.loc[event_mask, "daily_split_norm_proxy"].iloc[0]) if event_mask.any() else np.nan
    event_quote_meta = _summarize_event_quote_scale(row)
    event_quote_mid_raw = float(event_quote_meta.get("quote_mid_raw_event", np.nan))
    event_quote_mid_split_norm = event_quote_mid_raw / event_split_factor if np.isfinite(event_quote_mid_raw) and event_split_factor > 0 else np.nan

    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True, gridspec_kw={"height_ratios": [2.0, 1.1]})
    x = np.arange(len(adj))
    axes[0].plot(x, adj["c"], color="#0f766e", linewidth=1.5, label="daily close raw")
    axes[0].plot(x, adj["c_adj_proxy"], color="#b91c1c", linewidth=1.4, label="daily close adjusted_proxy")

    if event_mask.any():
        event_idx = int(np.flatnonzero(event_mask.to_numpy())[0])
        axes[0].axvspan(event_idx - 0.55, event_idx + 0.55, color="#fed7aa", alpha=0.35, zorder=0)
        if np.isfinite(event_quote_mid_raw):
            axes[0].scatter([event_idx], [event_quote_mid_raw], color="#7c3aed", s=48, zorder=5, label="event quote mid raw")
        if np.isfinite(event_quote_mid_split_norm):
            axes[0].scatter([event_idx], [event_quote_mid_split_norm], color="#2563eb", s=48, zorder=5, label="event quote mid split_normalized")
        anchor_y = event_close_adj if np.isfinite(event_close_adj) else event_close_raw
        axes[0].annotate(
            (
                "event day\n"
                f"raw close={event_close_raw:.4f}\n"
                f"adjusted_proxy={event_close_adj:.4f}\n"
                f"quote mid raw={event_quote_mid_raw:.4f}\n"
                f"quote mid split_norm={event_quote_mid_split_norm:.4f}\n"
                f"future split factor={event_split_factor:.4f}\n"
                f"future dividends={total_future_div:.4f}"
            ),
            xy=(event_idx, anchor_y),
            xytext=(18, 18),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.35", fc="#fff7ed", ec="#d97706", alpha=0.95),
            arrowprops=dict(arrowstyle="->", color="#d97706"),
            fontsize=10,
        )

    axes[0].set_title(f"{row['ticker']} | {row['date_str']} | semantica de precio: quotes raw, daily raw y adjusted_proxy")
    axes[0].set_ylabel("price")
    axes[0].legend(loc="upper right", ncol=2, frameon=True)

    axes[1].bar(x, adj["future_dividend_sum"], width=0.75, color="#fde68a", alpha=0.45, label="future dividend sum")
    ax2 = axes[1].twinx()
    ax2.plot(x, adj["future_dividend_factor"], color="#b91c1c", linewidth=1.2, marker="o", markersize=3, label="future dividend factor")
    ax2.plot(x, adj["future_split_factor"], color="#2563eb", linewidth=1.2, marker="o", markersize=3, label="future split factor")
    if event_mask.any():
        axes[1].axvspan(event_idx - 0.55, event_idx + 0.55, color="#fed7aa", alpha=0.35)
    axes[1].set_ylabel("cumulative future dividends")
    ax2.set_ylabel("future factors")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([d.strftime("%Y-%m-%d") for d in adj["date"]], rotation=45, ha="right")
    axes[1].set_title("Cadena futura de dividendos y split normalization")
    h1, l1 = axes[1].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc="upper right", ncol=3, frameon=True)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return {
        "post_event_dividend_sum": total_future_div,
        "event_close_raw": event_close_raw,
        "event_close_adjusted_proxy": event_close_adj,
        "post_event_dividend_count": float(len(dividends)),
        "future_split_factor": event_split_factor,
        "future_split_count": float(len(splits)),
        "event_quote_mid_raw": event_quote_mid_raw,
        "event_quote_mid_split_normalized": event_quote_mid_split_norm,
        "event_daily_split_normalized": event_daily_split_norm,
    }


def _save_event_month_quotes_context(row: pd.Series, out_path: Path, days_before: int = 15, days_after: int = 15) -> None:
    quote_ctx = _load_quote_month_session_trace(row, days_before=days_before, days_after=days_after)
    daily_quote_ctx = _load_quote_daily_context(row, days_before=days_before, days_after=days_after)
    event_day = pd.Timestamp(str(row["date_str"]))
    if quote_ctx.empty:
        raise RuntimeError(f"No quote month session trace available for {row['ticker']} {row['date_str']}")

    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=False, gridspec_kw={"height_ratios": [2.2, 1.2]})

    first_bid = True
    first_ask = True
    for d, sub in quote_ctx.groupby("date", dropna=True):
        sub = sub.sort_values("session_x")
        axes[0].plot(
            sub["session_x"],
            sub["bid_price"],
            color="#0f766e",
            linewidth=0.9,
            label="bid_price" if first_bid else None,
        )
        axes[0].plot(
            sub["session_x"],
            sub["ask_price"],
            color="#b91c1c",
            linewidth=0.9,
            label="ask_price" if first_ask else None,
        )
        first_bid = False
        first_ask = False
    crossed = quote_ctx.loc[quote_ctx["cross_positive"]].copy()
    if not crossed.empty:
        axes[0].scatter(
            crossed["session_x"],
            crossed["bid_price"],
            color="#f59e0b",
            s=10,
            alpha=0.85,
            label="crossed bid > ask > 0",
        )
        axes[0].scatter(
            crossed["session_x"],
            crossed["ask_price"],
            color="#7c3aed",
            s=10,
            alpha=0.55,
            label="ask en crossed",
        )

    available_days = sorted(pd.to_datetime(quote_ctx["date"]).dt.normalize().unique())
    day_positions = []
    for d in available_days:
        sub = quote_ctx.loc[pd.to_datetime(quote_ctx["date"]).dt.normalize().eq(pd.Timestamp(d))]
        if sub.empty:
            continue
        day_positions.append((pd.Timestamp(d), float(sub["session_x"].iloc[0]), float(sub["session_x"].iloc[-1])))
        axes[0].axvline(float(sub["session_x"].iloc[-1]), color="#d1d5db", linewidth=0.5, alpha=0.6)

    event_sub = quote_ctx.loc[pd.to_datetime(quote_ctx["date"]).dt.normalize().eq(event_day)]
    if not event_sub.empty:
        start_x = float(event_sub["session_x"].iloc[0])
        end_x = float(event_sub["session_x"].iloc[-1])
        axes[0].axvspan(start_x, end_x, color="#fde68a", alpha=0.30, zorder=0)
        event_bid = float(event_sub["bid_price"].dropna().median()) if event_sub["bid_price"].dropna().size else 0.0
        axes[0].annotate(
            f"event session\n{row['taxonomy']}\n{POSITIVE_BUCKET_LABELS.get(str(row['positive_cross_bucket']), str(row['positive_cross_bucket']))}",
            xy=((start_x + end_x) / 2.0, event_bid),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.35", fc="#fff7ed", ec="#d97706", alpha=0.95),
            arrowprops=dict(arrowstyle="->", color="#d97706"),
            fontsize=10,
        )

    axes[0].set_title(f"{row['ticker']} | {row['date_str']} | quotes mensual por sesiones (-15d / +15d)")
    axes[0].set_ylabel("quote price")
    axes[0].legend(loc="upper right", ncol=2, frameon=True)

    visible_prices = pd.concat(
        [
            pd.to_numeric(quote_ctx["bid_price"], errors="coerce"),
            pd.to_numeric(quote_ctx["ask_price"], errors="coerce"),
        ],
        ignore_index=True,
    ).dropna()
    visible_prices = visible_prices.loc[visible_prices.gt(0)]
    if not visible_prices.empty:
        p01 = float(visible_prices.quantile(0.01))
        p99 = float(visible_prices.quantile(0.99))
        if np.isfinite(p01) and np.isfinite(p99) and p99 > p01:
            pad = max((p99 - p01) * 0.15, 0.01)
            y_low = max(p01 - pad, 0)
            y_high = p99 + pad
            axes[0].set_ylim(y_low, y_high)
            outlier_count = int((visible_prices.gt(y_high) | visible_prices.lt(y_low)).sum())
            if outlier_count > 0:
                axes[0].text(
                    0.01,
                    0.02,
                    f"visual range clipped to robust band; outliers hidden: {outlier_count}",
                    transform=axes[0].transAxes,
                    fontsize=9,
                    color="#7c2d12",
                    bbox=dict(boxstyle="round,pad=0.25", fc="#fff7ed", ec="#fdba74", alpha=0.9),
                )

    daily_quote_ctx = daily_quote_ctx.sort_values("date").reset_index(drop=True)
    x2 = np.arange(len(daily_quote_ctx))
    axes[1].bar(x2, daily_quote_ctx["rows"], width=0.8, color="#cbd5e1", alpha=0.8, label="quote rows")
    ax2 = axes[1].twinx()
    ax2.plot(x2, daily_quote_ctx["crossed_ratio_pct"], color="#2563eb", linewidth=1.2, marker="o", label="crossed_ratio_pct")
    ax2.plot(x2, daily_quote_ctx["max_gap_bps_pos"], color="#dc2626", linewidth=1.2, marker="o", label="max_gap_bps_pos")
    ax2.axhline(5.0, color="#2563eb", linestyle="--", linewidth=1.0)
    ax2.axhline(25.0, color="#111827", linestyle="--", linewidth=1.0)

    if not event_sub.empty:
        event_idx = int(np.flatnonzero(pd.to_datetime(daily_quote_ctx["date"]).dt.normalize().eq(event_day).to_numpy())[0])
        axes[1].axvspan(event_idx - 0.5, event_idx + 0.5, color="#fde68a", alpha=0.30)

    tick_labels = [pd.Timestamp(d).strftime("%Y-%m-%d") for d in daily_quote_ctx["date"]]
    axes[1].set_xticks(x2)
    axes[1].set_xticklabels(tick_labels, rotation=45, ha="right")
    axes[1].set_ylabel("quote rows")
    ax2.set_ylabel("crossed pct / max gap bps")
    axes[1].set_title("Disponibilidad daily de quotes y severidad del episodio")

    h1, l1 = axes[1].get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc="upper right", frameon=True)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_raw_window(row: pd.Series, out_path: Path, window: int = 600, use_index_x: bool = False) -> None:
    df = _load_case_frame(row["file"])
    view, crossed_view = _build_window_view(df, window)
    no_positive = crossed_view.empty
    if view.empty:
        if df.empty:
            raise RuntimeError(f"Empty quotes file: {row['file']}")
        view = df.copy()
    if no_positive:
        if len(view) > 4000:
            step = max(int(np.ceil(len(view) / 4000)), 1)
            view = view.iloc[::step].copy()

    x = np.arange(len(view)) if use_index_x else view["ts_ny"]
    x_cross = np.flatnonzero(view["cross_positive"].to_numpy()) if use_index_x else crossed_view["ts_ny"]
    regime_label = POSITIVE_BUCKET_LABELS.get(str(row["positive_cross_bucket"]), str(row["positive_cross_bucket"]))

    fig, axes = plt.subplots(
        2, 1, figsize=(16, 9), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.2]}
    )
    axes[0].plot(x, view["bid_price"], color="#0f766e", linewidth=1.2, label="bid_price")
    axes[0].plot(x, view["ask_price"], color="#b91c1c", linewidth=1.2, label="ask_price")
    if not no_positive:
        axes[0].scatter(
            x_cross,
            crossed_view["bid_price"],
            color="#f59e0b",
            s=18,
            alpha=0.9,
            label="crossed bid > ask > 0",
        )
        axes[0].scatter(
            x_cross,
            crossed_view["ask_price"],
            color="#7c3aed",
            s=18,
            alpha=0.6,
            label="ask en crossed",
        )
    axes[0].set_title(
        f"{row['ticker']} | {row['date_str']} | {regime_label} | ventana raw"
    )
    axes[0].set_ylabel("price")
    axes[0].legend(loc="upper right", ncol=2, frameon=True)

    if no_positive:
        axes[1].plot(x, view["gap_bps"], color="#1d4ed8", linewidth=0.9, alpha=0.9)
        axes[1].axhline(0.0, color="#111827", linewidth=1.0, alpha=0.7)
    else:
        axes[1].scatter(x_cross, crossed_view["gap_bps"], color="#dc2626", s=18, alpha=0.85)
        axes[1].fill_between(x_cross, crossed_view["gap_bps"], 0, color="#fca5a5", alpha=0.25)
    axes[1].axhline(5.0, color="#2563eb", linestyle="--", linewidth=1.0, label="5 bps")
    axes[1].axhline(25.0, color="#111827", linestyle="--", linewidth=1.0, label="25 bps")
    axes[1].set_ylabel("gap bps")
    axes[1].set_xlabel("row index en ventana" if use_index_x else "timestamp NY")
    axes[1].legend(loc="upper right", frameon=True)
    axes[1].set_title("Severidad del crossed positivo" if not no_positive else "Gap bps del libro en ausencia de crossed positivo")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_full_session_context(row: pd.Series, out_path: Path) -> None:
    df = _load_case_frame(row["file"])
    crossed_view = df.loc[df["cross_positive"]].copy()
    x = df["ts_ny"]
    x_cross = crossed_view["ts_ny"] if not crossed_view.empty else np.array([])

    fig, axes = plt.subplots(
        2, 1, figsize=(18, 10), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.2]}
    )
    axes[0].plot(x, df["bid_price"], color="#0f766e", linewidth=1.0, label="bid_price")
    axes[0].plot(x, df["ask_price"], color="#b91c1c", linewidth=1.0, label="ask_price")
    if not crossed_view.empty:
        axes[0].scatter(
            x_cross,
            crossed_view["bid_price"],
            color="#f59e0b",
            s=14,
            alpha=0.9,
            label="crossed bid > ask > 0",
        )
        axes[0].scatter(
            x_cross,
            crossed_view["ask_price"],
            color="#7c3aed",
            s=14,
            alpha=0.6,
            label="ask en crossed",
        )
    axes[0].set_title(f"{row['ticker']} | {row['date_str']} | sesion completa 04:00-20:00 NY")
    axes[0].set_ylabel("price")
    axes[0].legend(loc="upper right", ncol=2, frameon=True)

    axes[1].plot(x, df["gap_bps"], color="#1d4ed8", linewidth=0.9, label="gap_bps")
    axes[1].axhline(0.0, color="#111827", linewidth=1.0, alpha=0.7)
    axes[1].axhline(5.0, color="#2563eb", linestyle="--", linewidth=1.0)
    axes[1].axhline(25.0, color="#111827", linestyle="--", linewidth=1.0)
    if not crossed_view.empty:
        axes[1].scatter(x_cross, crossed_view["gap_bps"], color="#ea580c", s=12, alpha=0.75)
    axes[1].set_ylabel("gap bps")
    axes[1].set_xlabel("timestamp NY")
    axes[1].set_title("Contexto de sesion completa")
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_structure_diagnostics(row: pd.Series, out_path: Path) -> None:
    df = _load_case_frame(row["file"])
    crossed = df.loc[df["crossed"]].copy()
    positive = df.loc[df["cross_positive"]].copy()

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    ax = axes[0, 0]
    counts = {
        "crossed_total": int(crossed.shape[0]),
        "ask=0": int(df["ask_zero_cross"].sum()),
        "ask>0": int(df["ask_positive_cross"].sum()),
    }
    ax.bar(list(counts.keys()), list(counts.values()), color=["#475569", "#f59e0b", "#dc2626"])
    ax.set_title("A. Composicion del crossed")
    ax.set_ylabel("rows")

    ax = axes[0, 1]
    ax.hist(pd.to_numeric(positive["gap_bps"], errors="coerce").dropna(), bins=25, color="#dc2626", alpha=0.8)
    ax.axvline(5.0, color="#2563eb", linestyle="--", linewidth=1.0)
    ax.axvline(25.0, color="#111827", linestyle="--", linewidth=1.0)
    ax.set_title("B. Distribucion gap_bps | ask>0")
    ax.set_xlabel("bps")

    ax = axes[1, 0]
    diag = {
        "ask_integer_like %": float(df["ask_integer_like"].mean() * 100.0),
        "bid_integer_like %": float(df["bid_integer_like"].mean() * 100.0),
        "ask_eq_round_bid_like %": float(df["ask_eq_round_bid_like"].mean() * 100.0),
    }
    ax.bar(list(diag.keys()), list(diag.values()), color=["#7c3aed", "#0f766e", "#b91c1c"])
    ax.tick_params(axis="x", rotation=12)
    ax.set_title("C. Patrones estructurales")
    ax.set_ylabel("pct rows")

    ax = axes[1, 1]
    summary = _summary_frame(row).iloc[0]
    table = ax.table(
        cellText=[
            ["severity", summary["severity"]],
            ["root", summary["root"]],
            ["rows", int(summary["rows_file"])],
            ["crossed_ratio_pct", round(float(summary["crossed_ratio_pct"]), 6)],
            ["ask_integer_pct", round(float(summary["ask_integer_pct"]), 6)],
            ["median_bps_ask_positive", round(float(summary["median_bps_ask_positive"]), 6)],
            ["p90_bps_ask_positive", round(float(summary["p90_bps_ask_positive"]), 6)],
        ],
        colLabels=["metric", "value"],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.3)
    ax.axis("off")
    ax.set_title("D. Variables de corte")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_summary_card(row: pd.Series, out_path: Path) -> None:
    summary = _summary_frame(row)
    fig, ax = plt.subplots(figsize=(14, 4.5))
    ax.axis("off")
    table = ax.table(
        cellText=[[c, summary.iloc[0][c]] for c in summary.columns],
        colLabels=["metric", "value"],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.25)
    ax.set_title(f"{row['ticker']} | {row['date_str']} | resumen institucional", pad=16)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _build_case_note(row: pd.Series, historical_img: Path | None) -> str:
    scope_name = str(row["scope_name"])
    if scope_name == "good":
        decision = "good"
        reading = (
            "El caso pertenece a la franja buena de `quotes` porque el libro se mantiene limpio o el residuo observado "
            "permanece en una franja leve compatible con consumo principal del bloque."
        )
    elif scope_name == "review":
        decision = "review"
        reading = (
            "El caso no es `good`, pero tampoco cae en exclusion dura. "
            "Debe leerse como libro con problema real que exige flag y contexto."
        )
    else:
        decision = "bad"
        reading = (
            "El caso cae en `bad` porque el crossed positivo y su severidad economica siguen siendo demasiado agresivos para uso core."
        )

    context = (
        "Existe ademas una imagen historica de certificacion con narrativa contextual asociada."
        if historical_img is not None
        else "No existe imagen historica de certificacion asociada para este caso concreto."
    )
    return "\n".join(
        [
            f"- `decision`: `{decision}`",
            f"- `taxonomy`: `{row['taxonomy']}`",
            f"- `positive_cross_bucket`: `{row['positive_cross_bucket']}`",
            f"- `lectura`: {reading}",
            f"- `contexto`: {context}",
        ]
    )


def _scope_color_for_taxonomy(taxonomy: str) -> str:
    if taxonomy in QUOTES_GOOD_BUCKETS:
        return "#16a34a"
    if taxonomy in QUOTES_REVIEW_BUCKETS:
        return "#d97706"
    if taxonomy in QUOTES_BAD_BUCKETS:
        return "#dc2626"
    return "#475569"


def _save_taxonomy_distribution(out_path: Path) -> None:
    df = load_quotes_taxonomy_summary().copy().sort_values("pct", ascending=True)
    colors = [_scope_color_for_taxonomy(t) for t in df["taxonomy"]]
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.barh(df["taxonomy"], df["pct"], color=colors, alpha=0.9)
    ax.set_title("Quotes | Distribucion de taxonomias | universo canonical C+D <1B")
    ax.set_xlabel("share pct del universo")
    ax.set_ylabel("taxonomy")
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(
            float(row["pct"]) + 0.15,
            i,
            f"{int(row['files']):,} files | median crossed={float(row['crossed_ratio_median_pct']):.3f}%",
            va="center",
            fontsize=8,
        )
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_severity_and_root_mix(out_path: Path) -> None:
    sev = load_quotes_severity_counts().copy()
    root = load_quotes_root_mix().copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    sev_count_col = next((c for c in sev.columns if c not in {"severity"}), None)
    if sev_count_col is None:
        sev_count_col = sev.columns[-1]
    axes[0].bar(sev["severity"], sev[sev_count_col], color=["#16a34a", "#d97706", "#dc2626"][: len(sev)])
    axes[0].set_title("A. Severity counts")
    axes[0].set_ylabel("files")

    root_count_col = next((c for c in root.columns if c not in {"root"}), None)
    if root_count_col is None:
        root_count_col = root.columns[-1]
    axes[1].bar(root["root"].astype(str), root[root_count_col], color="#475569")
    axes[1].set_title("B. Root mix")
    axes[1].set_ylabel("files")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_positive_cross_policy(out_path: Path) -> None:
    df = load_quotes_positive_cross_summary().copy()
    order = QUOTES_REVIEW_BUCKETS + QUOTES_BAD_BUCKETS
    bucket_order = [
        "positive_cross_mild_lt5bps",
        "positive_cross_moderate_5to25bps",
        "positive_cross_severe_ge25bps",
    ]
    df["taxonomy"] = pd.Categorical(df["taxonomy"], categories=order, ordered=True)
    df["positive_cross_bucket"] = pd.Categorical(
        df["positive_cross_bucket"], categories=bucket_order, ordered=True
    )
    df = df.sort_values(["taxonomy", "positive_cross_bucket"])

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    pivot = df.pivot(index="taxonomy", columns="positive_cross_bucket", values="sample_files").fillna(0)
    x = np.arange(len(pivot.index))
    width = 0.22
    for idx, bucket in enumerate(bucket_order):
        vals = pivot[bucket].to_numpy() if bucket in pivot.columns else np.zeros(len(pivot.index))
        axes[0, 0].bar(x + (idx - 1) * width, vals, width=width, label=POSITIVE_BUCKET_LABELS[bucket])
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(pivot.index, rotation=18, ha="right")
    axes[0, 0].set_title("A. Casos por taxonomy y regimen positivo")
    axes[0, 0].legend(frameon=True)

    axes[0, 1].scatter(
        df["crossed_ask_zero_share_pct_median"],
        df["cross_rel_bps_median_ask_positive"],
        s=df["sample_files"] * 18,
        c=[_scope_color_for_taxonomy(t) for t in df["taxonomy"].astype(str)],
        alpha=0.8,
    )
    axes[0, 1].set_xlabel("median crossed ask=0 share pct")
    axes[0, 1].set_ylabel("median gap bps ask>0")
    axes[0, 1].set_title("B. ask=0 share vs severidad economica")

    axes[1, 0].scatter(
        df["cross_rel_bps_median_ask_positive"],
        df["cross_rel_bps_p90_ask_positive"],
        s=df["sample_files"] * 18,
        c=[_scope_color_for_taxonomy(t) for t in df["taxonomy"].astype(str)],
        alpha=0.8,
    )
    axes[1, 0].axvline(5.0, color="#2563eb", linestyle="--", linewidth=1.0)
    axes[1, 0].axvline(25.0, color="#111827", linestyle="--", linewidth=1.0)
    axes[1, 0].axhline(5.0, color="#2563eb", linestyle="--", linewidth=1.0)
    axes[1, 0].axhline(25.0, color="#111827", linestyle="--", linewidth=1.0)
    axes[1, 0].set_xlabel("median gap bps ask>0")
    axes[1, 0].set_ylabel("p90 gap bps ask>0")
    axes[1, 0].set_title("C. Umbrales economicos del crossed positivo")

    table_df = df[
        [
            "taxonomy",
            "positive_cross_bucket",
            "sample_files",
            "crossed_ask_zero_share_pct_median",
            "cross_rel_bps_median_ask_positive",
            "cross_rel_bps_p90_ask_positive",
        ]
    ].copy()
    table_df["positive_cross_bucket"] = table_df["positive_cross_bucket"].map(POSITIVE_BUCKET_LABELS)
    table_df = table_df.round(3)
    axes[1, 1].axis("off")
    table = axes[1, 1].table(
        cellText=table_df.values.tolist(),
        colLabels=[
            "taxonomy",
            "regime",
            "sample_files",
            "ask0_share_med",
            "median_bps",
            "p90_bps",
        ],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1, 1.15)
    axes[1, 1].set_title("D. Resumen policy de crossed positivo")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_integer_and_timestamp_diagnostics(out_path: Path) -> None:
    integer_df = load_quotes_integer_anomaly().copy()
    ts_df = load_quotes_timestamp_view().copy()
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    axes[0, 0].hist(
        pd.to_numeric(integer_df["rows"], errors="coerce").dropna(),
        bins=30,
        color="#7c3aed",
        alpha=0.85,
    )
    axes[0, 0].set_title("A. Integer anomalies | distribucion de rows")
    axes[0, 0].set_xlabel("rows")

    axes[0, 1].scatter(
        pd.to_numeric(integer_df["m.ask_integer_pct"], errors="coerce"),
        pd.to_numeric(integer_df["m.ask_eq_round_bid_pct"], errors="coerce"),
        s=np.clip(pd.to_numeric(integer_df["rows"], errors="coerce").fillna(1), 5, 90),
        color="#dc2626",
        alpha=0.6,
    )
    axes[0, 1].set_xlabel("ask_integer_pct")
    axes[0, 1].set_ylabel("ask_eq_round_bid_pct")
    axes[0, 1].set_title("B. Patrones integerizados duros")

    ts_rows = pd.to_numeric(ts_df["rows"], errors="coerce")
    axes[1, 0].hist(ts_rows.dropna(), bins=30, color="#0f766e", alpha=0.85)
    axes[1, 0].set_title("C. Timestamp rollover candidates | distribucion de rows")
    axes[1, 0].set_xlabel("rows")

    sample = ts_df.head(12).copy()
    sample["utc_dates"] = sample["m.actual_timestamp_dates_utc"].astype(str)
    axes[1, 1].axis("off")
    table = axes[1, 1].table(
        cellText=sample[["ticker", "date", "root", "severity", "rows", "utc_dates"]].values.tolist(),
        colLabels=["ticker", "date", "root", "severity", "rows", "actual_utc_dates"],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.0)
    table.scale(1, 1.12)
    axes[1, 1].set_title("D. Muestra de rollover UTC / drift temporal")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _save_open_bucket_diagnostics(out_path: Path) -> None:
    df = load_quotes_crossed_gap_cases().copy()
    focus = df.loc[df["taxonomy"].isin(QUOTES_REVIEW_BUCKETS + QUOTES_BAD_BUCKETS)].copy()
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    axes[0, 0].scatter(
        pd.to_numeric(focus["m.crossed_ratio_pct"], errors="coerce"),
        pd.to_numeric(focus["cross_rel_bps_median_ask_positive"], errors="coerce"),
        c=[_scope_color_for_taxonomy(t) for t in focus["taxonomy"].astype(str)],
        s=np.clip(pd.to_numeric(focus["crossed_rows_ask_positive"], errors="coerce").fillna(1) * 2.5, 10, 120),
        alpha=0.65,
    )
    axes[0, 0].set_xlabel("crossed_ratio_pct")
    axes[0, 0].set_ylabel("median gap bps ask>0")
    axes[0, 0].set_title("A. crossed_ratio vs severidad economica")

    axes[0, 1].scatter(
        pd.to_numeric(focus["crossed_ask_zero_share_pct"], errors="coerce"),
        pd.to_numeric(focus["m.ask_integer_pct"], errors="coerce"),
        c=[_scope_color_for_taxonomy(t) for t in focus["taxonomy"].astype(str)],
        s=np.clip(pd.to_numeric(focus["rows"], errors="coerce").fillna(1) / 40, 8, 120),
        alpha=0.65,
    )
    axes[0, 1].set_xlabel("crossed ask=0 share pct")
    axes[0, 1].set_ylabel("ask_integer_pct")
    axes[0, 1].set_title("B. ask=0 share vs integerization")

    axes[1, 0].scatter(
        pd.to_numeric(focus["rows"], errors="coerce"),
        pd.to_numeric(focus["crossed_rows_ask_positive"], errors="coerce"),
        c=[_scope_color_for_taxonomy(t) for t in focus["taxonomy"].astype(str)],
        s=18,
        alpha=0.65,
    )
    axes[1, 0].set_xlabel("rows file")
    axes[1, 0].set_ylabel("crossed_rows_ask_positive")
    axes[1, 0].set_title("C. Tamaño de file vs crossed positivo")

    sample = (
        focus.sort_values(
            ["taxonomy", "cross_rel_bps_p90_ask_positive", "crossed_rows_ask_positive"],
            ascending=[True, False, False],
        )
        .groupby("taxonomy", dropna=False)
        .head(3)
        .copy()
    )
    axes[1, 1].axis("off")
    table = axes[1, 1].table(
        cellText=sample[
            ["taxonomy", "ticker", "date", "m.crossed_ratio_pct", "cross_rel_bps_median_ask_positive"]
        ].round(3).values.tolist(),
        colLabels=["taxonomy", "ticker", "date", "crossed_ratio_pct", "median_bps"],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.2)
    table.scale(1, 1.15)
    axes[1, 1].set_title("D. Casos dominantes por taxonomy abierta")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def export_quotes_global_policy(
    project_root: Path,
    clean_output_dir: bool = True,
) -> pd.DataFrame:
    out_root = (
        project_root
        / "01_foundations"
        / "inspection_dossiers"
        / "quotes"
        / "evidence_assets"
        / "global_policy"
    )
    if clean_output_dir and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    outputs = [
        ("01_taxonomy_distribution.png", _save_taxonomy_distribution),
        ("02_severity_and_root_mix.png", _save_severity_and_root_mix),
        ("03_positive_cross_policy.png", _save_positive_cross_policy),
        ("04_integer_and_timestamp_diagnostics.png", _save_integer_and_timestamp_diagnostics),
        ("05_open_bucket_diagnostics.png", _save_open_bucket_diagnostics),
    ]

    rows: list[dict[str, str]] = []
    for fname, fn in outputs:
        path = out_root / fname
        fn(path)
        rows.append({"asset": fname, "path": str(path)})

    manifest = pd.DataFrame(rows)
    manifest.to_csv(out_root / "quotes_global_policy_manifest.csv", index=False)
    return manifest


def _md_rel(target: Path, doc_path: Path) -> str:
    return Path(
        shutil.os.path.relpath(str(target), start=str(doc_path.parent))
    ).as_posix()


def _taxonomy_implication(taxonomy: str) -> str:
    taxonomy = str(taxonomy)
    mapping = {
        "clean_pass_or_other": "La taxonomy `clean_pass_or_other` implica que el bloque no necesita defensa causal compleja: el libro ya pasa su prueba economica minima y no exige reinterpretacion forense intensa.",
        "soft_crossed_micro_noise": "La taxonomy `soft_crossed_micro_noise` implica que existen micro-contradicciones locales, pero tan pequenas o escasas que la prioridad institucional es no sobrecastigar residuo inocuo.",
        "persistent_soft_crossed_low": "La taxonomy `persistent_soft_crossed_low` implica persistencia real de crossed, aunque en una banda todavia compatible con uso principal si el dano economico sigue contenido.",
        "utc_rollover_large_day_clean": "La taxonomy `utc_rollover_large_day_clean` implica que parte de la rareza pertenece al eje temporal y no al eje economico del spread; su lectura correcta evita castigar como libro roto un efecto de rollover bien entendido.",
        "persistent_soft_crossed_mid_large_scale": "La taxonomy `persistent_soft_crossed_mid_large_scale` implica un problema repetido y distribuido, no un simple pinchazo local. Por eso empuja a `review`: ya hay dano real, aunque no necesariamente exclusion dura universal.",
        "large_file_threshold_edge_hard_many_crosses": "La taxonomy `large_file_threshold_edge_hard_many_crosses` implica un libro grande con muchas contradicciones, pero cerca del borde decisional. La dificultad analitica esta en decidir si el volumen de crossed es ruido absorbible o evidencia de degradacion suficientemente seria.",
        "medium_file_threshold_edge_hard_many_crosses": "La taxonomy `medium_file_threshold_edge_hard_many_crosses` implica que el mismo tipo de dano aparece en un file menos grande y por eso pesa mas: hay menos masa para diluir la anomalia y la exclusion se vuelve mas defendible.",
        "high_hard_crossed_10_to_20": "La taxonomy `high_hard_crossed_10_to_20` implica una franja donde la contradiccion ya no es una simple sospecha: el dano positivo del crossed entra en una zona donde ejecucion, mark-to-market y aprendizaje pueden dejar de ser creibles.",
    }
    return mapping.get(taxonomy, f"La taxonomy `{taxonomy}` indica una familia de dano ya distinguible del resto del universo y debe leerse junto con severidad, persistencia y composicion del crossed.")


def _regime_implication(bucket: str) -> str:
    bucket = str(bucket)
    mapping = {
        "no_positive_cross": "El regimen `no positive cross` significa que el caso no presenta contradiccion economica positiva directa; cualquier rareza restante debe interpretarse como estructura, cobertura o residuo no decisional.",
        "positive_cross_mild_lt5bps": "El regimen `mild <5 bps` significa que existe contradiccion economica positiva, pero aun en una banda donde un uso prudente puede seguir siendo defendible si la persistencia y la estructura no agravan el caso.",
        "positive_cross_moderate_5to25bps": "El regimen `moderate 5-25 bps` ya entra en zona donde el crossed tiene capacidad real de contaminar simulacion de ejecucion y features microestructurales, aunque todavia puede requerir lectura contextual antes de exclusion dura.",
        "positive_cross_severe_ge25bps": "El regimen `severe >=25 bps` empuja el caso a una lectura economicamente dura: el crossed deja de ser cosmetico y pasa a cuestionar si el libro sigue siendo interpretable como mercado negociable.",
    }
    return mapping.get(bucket, f"El regimen `{bucket}` debe leerse como una medida de severidad economica del crossed y no solo como una etiqueta visual.")


def _cross_composition_implication(crossed_zero: int, crossed_pos: int) -> str:
    total = crossed_zero + crossed_pos
    if total <= 0:
        return "Como no hay crossed material en el file, la composicion `ask=0` vs `ask>0` no es el eje que decide el caso."
    zero_share = crossed_zero / total
    pos_share = crossed_pos / total
    if crossed_zero > 0 and crossed_pos == 0:
        return "Toda la composicion crossed cae en `ask=0`. Eso desplaza la lectura hacia degeneracion estructural o representacional y reduce la fuerza de una interpretacion puramente economica del spread."
    if crossed_pos > 0 and crossed_zero == 0:
        return "Toda la composicion crossed cae en `ask>0`. Eso endurece la lectura economica del caso: el dano no depende de ceros mecanicos, sino de contradiccion positiva dentro de precios aparentemente vivos."
    if zero_share >= 0.7:
        return "La mayor parte del crossed vive en `ask=0`, pero existe una cola `ask>0` que impide absolver el caso como simple glitch. La lectura correcta es mixta: dano estructural dominante con residuo economico que aun puede justificar bandera o exclusion."
    if pos_share >= 0.7:
        return "La mayor parte del crossed vive en `ask>0`, de modo que el corazon del problema sigue siendo economico. La parte `ask=0`, si existe, acompana pero no explica por si sola la anomalia."
    return "La composicion esta mezclada entre `ask=0` y `ask>0`. Eso obliga a una lectura dual: parte del patron pertenece a estructura y parte a contradiccion economica genuina, por lo que la decision debe apoyarse en ambas capas y no en una sola narrativa."


def _pipeline_implication(scope_name: str, bucket: str) -> str:
    bucket = str(bucket)
    if scope_name == "good":
        return "Para pipelines, esto significa que el caso puede seguir entrando en consumo principal con la salvedad de que cualquier residuo observado debe quedar trazado como tolerado y no ignorado por completo."
    if scope_name == "review":
        if bucket == "positive_cross_mild_lt5bps":
            return "Para pipelines, esto empuja a conservar el caso fuera de ejecucion limpia, pero todavia puede mantenerse en investigacion contextual y en analisis de sensibilidad donde interese entender fronteras de tolerancia."
        return "Para pipelines, esto bloquea su uso como libro sano en ejecucion y features microestructurales principales, aunque aun puede mantenerse para forense, sensibilidad y estudios donde la anomalia sea parte del objeto de investigacion."
    return "Para pipelines, esto implica exclusion de ejecucion realista, de mark-to-market intradiario defendible y de features microestructurales tratadas como si reflejaran un mercado normal. Solo debe sobrevivir en circuitos forenses o de calidad."


def _quotes_forensic_analysis(row: pd.Series) -> str:
    scope_name = str(row["scope"])
    taxonomy = str(row["taxonomy"])
    regime = POSITIVE_BUCKET_LABELS.get(str(row["positive_cross_bucket"]), str(row["positive_cross_bucket"]))
    crossed_ratio = float(row["crossed_ratio_pct"])
    crossed_pos = int(row["crossed_rows_ask_positive"])
    crossed_zero = int(row["crossed_rows_ask_zero"])
    ask_integer = float(row["ask_integer_pct"])
    med_bps = float(row["median_bps_ask_positive"])
    p90_bps = float(row["p90_bps_ask_positive"])

    if scope_name == "good":
        opening = (
            "La conclusion correcta del caso es que el libro mantiene semantica economica util. El residuo observado no cambia de forma material la lectura del spread ni invalida el uso operativo normal del dia."
        )
    elif scope_name == "review":
        opening = (
            "La conclusion correcta del caso es que ya existe contradiccion economica real dentro del libro, pero aun no con fuerza suficiente para justificar exclusion dura sin contexto adicional."
        )
    else:
        opening = (
            "La conclusion correcta del caso es que la contradiccion local entre bid y ask ya compromete la credibilidad economica del libro y bloquea su consumo como si fuera mercado normal."
        )

    details = [
        opening,
        f"La taxonomy historica es `{taxonomy}` y el regimen positivo dominante es `{regime}`. Esto importa porque la taxonomy no solo clasifica: resume que tipo de anomalia se esta viendo y que clase de decision contractual puede defenderse despues.",
        _taxonomy_implication(taxonomy),
        _regime_implication(str(row["positive_cross_bucket"])),
    ]

    if str(row["positive_cross_bucket"]) == "no_positive_cross":
        details.append(
            f"En terminos observables, el file tiene `crossed_ratio_pct={crossed_ratio:.6f}` sin filas `bid > ask > 0`; `crossed_rows_ask_positive={crossed_pos}` y `crossed_rows_ask_zero={crossed_zero}`. El hecho que esto prueba es que no aparece contradiccion economica positiva material."
        )
        details.append(
            "La decision que cambia es no escalar el caso artificialmente a `review` o `bad`. El error metodologico que evita es castigar rarezas visuales o ruido de libro sin dano economico real. Para backtest y ML esto protege el universo util: evita etiquetar como patologico un dia que sigue siendo compatible con consumo principal."
        )
    else:
        details.extend([
            (
                f"En terminos observables, el file tiene `crossed_ratio_pct={crossed_ratio:.6f}` con `crossed_rows_ask_positive={crossed_pos}` y `crossed_rows_ask_zero={crossed_zero}`."
            ),
            (
                f"La severidad economica del crossed ask>0 se resume en `median_bps_ask_positive={med_bps:.6f}` y `p90_bps_ask_positive={p90_bps:.6f}`. Estos dos numeros convierten una forma visual rara en una conclusion operativa sobre si el libro sigue representando o no un mercado negociable."
            ),
        ])
        if scope_name == "good":
            details.append(
                "La decision que cambia es mantener el caso dentro de la franja util, aunque con lectura consciente de que existe una huella positiva leve o acotada. En `good`, el objetivo no es negar toda irregularidad, sino demostrar que la anomalia no destruye la semantica economica minima del libro ni invalida su uso principal. El error que evita esta lectura es sobrecastigar micro-residuos y encoger artificialmente el universo util para backtest y ML."
            )
        elif scope_name == "review":
            details.append(
                "La decision que cambia es pasar de libro sano a libro util solo bajo cautela. `review` significa: no usar como si fuera ejecucion limpia, conservar para analisis contextual y sensibilidad. El error que evita es tratar como normal un episodio que ya contiene contradiccion economica real y contaminar simulaciones de ejecucion o validaciones demasiado optimistas."
            )
        else:
            details.append(
                "La decision que cambia es exclusion del consumo core del libro. `bad` significa que el estado local ya no puede alimentar ejecucion, mark-to-market intradiario ni aprendizaje de ML como si fuese microestructura defendible. El error que evita es construir decisiones sobre un libro que ha dejado de representar un mercado localmente creible."
            )

    details.append(
        f"El patron estructural muestra `ask_integer_pct={ask_integer:.6f}`. Este numero obliga a separar dos explicaciones rivales: contradiccion economica genuina del libro o mezcla con degeneracion estructural / integerizacion."
    )
    details.append(_cross_composition_implication(crossed_zero, crossed_pos))
    if ask_integer > 50:
        details.append(
            "Como `ask_integer_pct` es muy alto, parte del dano puede venir de estructura y no solo de economia del spread. La lectura inteligente ya no es 'todo es mercado roto', sino 'hay suficiente dano local para bloquear consumo sano, pero parte del patron puede estar mediado por representacion'."
        )
    elif ask_integer < 5:
        details.append(
            "Como `ask_integer_pct` es bajo, la hipotesis de simple degeneracion mecanica pierde fuerza. Eso endurece la interpretacion: el crossed se parece mas a contradiccion economica genuina y menos a artefacto."
        )
    else:
        details.append(
            "Como `ask_integer_pct` no es extremo, el caso exige leer geometria del crossed y estructura simultaneamente. No basta un solo numero; hay que combinar severidad, composicion y contexto."
        )

    event_close_raw = pd.to_numeric(row.get("event_close_raw"), errors="coerce")
    event_close_adj = pd.to_numeric(row.get("event_close_adjusted_proxy"), errors="coerce")
    event_quote_raw = pd.to_numeric(row.get("event_quote_mid_raw"), errors="coerce")
    event_quote_split = pd.to_numeric(row.get("event_quote_mid_split_normalized"), errors="coerce")
    future_split_factor = pd.to_numeric(row.get("future_split_factor"), errors="coerce")
    post_div_sum = pd.to_numeric(row.get("post_event_dividend_sum"), errors="coerce")
    if np.isfinite(event_close_raw) and (np.isfinite(event_quote_raw) or np.isfinite(event_quote_split) or np.isfinite(event_close_adj)):
        parts = [f"`daily raw close={float(event_close_raw):.4f}`"]
        if np.isfinite(event_quote_raw):
            parts.append(f"`quote mid raw={float(event_quote_raw):.4f}`")
        if np.isfinite(event_quote_split):
            parts.append(f"`quote mid split_normalized={float(event_quote_split):.4f}`")
        if np.isfinite(event_close_adj):
            parts.append(f"`daily adjusted_proxy={float(event_close_adj):.4f}`")
        sem_text = "En la capa de semantica de precio del evento aparecen " + ", ".join(parts) + "."
        if np.isfinite(future_split_factor) and float(future_split_factor) != 1.0:
            sem_text += f" La reconciliacion incluye `future_split_factor={float(future_split_factor):.4f}`."
        if np.isfinite(post_div_sum) and float(post_div_sum) > 0:
            sem_text += f" Ademas hay `post_event_dividend_sum={float(post_div_sum):.4f}`."
        details.append(sem_text)
        details.append(
            "La implicacion metodologica es crucial: una discrepancia entre `quotes`, `daily` y una plataforma externa no puede leerse automaticamente como fallo del dataset. Puede ser semantica de precio distinta. El error que evita esta capa es mezclar raw, split-normalized y adjusted dentro del mismo pipeline, rompiendo auditoria, benchmarking y labels."
        )
        details.append(_pipeline_implication(scope_name, str(row["positive_cross_bucket"])))

    if row.get("historical_context_png"):
        details.append(
            "Existe ademas una imagen historica de certificacion asociada. Su papel es poner el episodio en un marco causal mas amplio: halt, explained, not strongly explained o patron conocido."
        )
        details.append(
            "La regla que protege al proyecto es esta: el contexto externo se usa para explicar por que aparece el episodio, no para absolverlo. El error que evita es degradar el criterio de calidad del libro porque exista una historia plausible alrededor del caso."
        )
    else:
        details.append(
            "No existe imagen historica de certificacion asociada para este caso concreto. Por eso la decision descansa principalmente en la evidencia local del libro: geometria, severidad y estructura."
        )

    return " ".join(details)


def _image_explanation_raw(row: pd.Series) -> str:
    regime = POSITIVE_BUCKET_LABELS.get(str(row["positive_cross_bucket"]), str(row["positive_cross_bucket"]))
    if str(row["positive_cross_bucket"]) == "no_positive_cross":
        return (
            "Esta imagen responde a la primera pregunta decisiva: existe contradiccion economica positiva local o no. Arriba se comparan `bid_price` y `ask_price`; abajo se ve el `gap_bps` firmado. Si aqui no aparece `bid > ask > 0` material, no hay base para endurecer la clasificacion. La decision que protege es no convertir ruido inocuo en patologia."
        )
    scope_name = str(row["scope"])
    if scope_name == "good":
        return (
            f"Esta imagen responde a la primera pregunta decisiva del caso: el crossed observado, si existe, sigue siendo compatible con permanencia en `good` o no. Arriba ensena la geometria exacta del tramo conflictivo; abajo convierte esa geometria a bps y la enfrenta a los cortes `5 bps` y `25 bps`. El regimen dominante es `{regime}`. La decision que cambia es demostrar que el residuo permanece por debajo del dano que obligaria a mover el caso a `review` o `bad`. El error que evita es expulsar del universo util episodios leves cuyo impacto sobre ejecucion y features sigue siendo tolerable."
        )
    return (
        f"Esta imagen responde a la primera pregunta decisiva del caso: el crossed observado es economicamente bastante fuerte para justificar un cambio de clase. Arriba ensena la geometria exacta del tramo conflictivo; abajo convierte esa geometria a bps y la enfrenta a los cortes `5 bps` y `25 bps`. El regimen dominante es `{regime}`. La decision que cambia es pasar de anomalia interpretable a `review` o `bad`. El error que evita es decidir por apariencia visual sin medir el dano economico real del crossed. En terminos de pipeline, este panel decide si el problema afecta solo a la lectura forense o si invalida simulacion de ejecucion y microstructure features."
    )


def _image_explanation_event_month(row: pd.Series) -> str:
    return (
        "Esta imagen responde a la pregunta de persistencia temporal: estamos ante un accidente local o ante una fase mas amplia de inestabilidad. Arriba coloca el evento en la serie `daily` real del mes; abajo compara `crossed_ratio_pct` y `max_gap_bps_pos` del dia contra sus vecinos. La decision que cambia es el peso estructural que se le concede al caso. El error que evita es juzgar igual un shock aislado y una degradacion repetida del libro."
    )


def _image_explanation_adjusted_proxy(row: pd.Series) -> str:
    return (
        "Esta imagen responde a la pregunta de reconciliacion semantica: la discrepancia de precios viene de datos rotos o de vistas de precio distintas. Compara `daily raw`, `daily adjusted_proxy`, `quote mid raw` y `quote mid split_normalized`, y debajo ensena la cadena de dividendos y splits que produce la diferencia. La decision que cambia es si el inspector debe abrir una incidencia de calidad o cerrar el caso como diferencia legitima de semantica. El error que evita es mezclar series raw y adjusted como si fueran equivalentes. En pipelines reales, esto protege benchmarking, labels diarios y reconciliacion externa frente a falsas alarmas de precio."
    )


def _image_explanation_event_month_quotes(row: pd.Series) -> str:
    return (
        "Esta imagen responde a la pregunta de recurrencia mensual dentro de `quotes`: el problema se concentra en el evento o reaparece en varias sesiones. Arriba concatena sesiones con datos disponibles; abajo resume cobertura diaria, `crossed_ratio_pct` y `max_gap_bps_pos`. La decision que cambia es si el caso debe leerse como episodio puntual o como sintoma de una fase repetida de libro degradado. El error que evita es extrapolar desde un unico dia a todo el mes sin evidencia."
    )


def _image_explanation_session(row: pd.Series) -> str:
    return (
        "Esta imagen responde a la pregunta de extension intradiaria: el dano esta confinado a un bloque corto o contamina la sesion completa. Arriba se ve toda la sesion `04:00-20:00 NY`; abajo el `gap_bps` firmado. La decision que cambia es si el consumo debe penalizar solo un tramo o desechar el dia entero para uso operativo. El error que evita es tratar una cicatriz local como ruina total o, al reves, minimizar una degradacion distribuida a lo largo del dia. En ejecucion esto decide si la sesion puede seguir usandose con restricciones; en ML decide si las features intradiarias conservan significado economico."
    )


def _image_explanation_diagnostics(row: pd.Series) -> str:
    return (
        "Este panel responde a la pregunta de naturaleza del fallo: contradiccion economica genuina o mezcla con degeneracion estructural. Separa `ask=0` de `ask>0`, muestra la distribucion de `gap_bps` y resume patrones de integerizacion. La decision que cambia es como interpretar el dano: mercado localmente roto, artefacto de representacion o combinacion de ambos. El error que evita es sobrediagnosticar crossed reales cuando parte de la senal proviene de estructura degenerada del libro. Esta lectura afecta directamente a que el caso vaya a exclusion dura, a bandera contextual o a simple reconciliacion tecnica."
    )


def _image_explanation_summary(row: pd.Series) -> str:
    return (
        "Esta tarjeta responde a la pregunta de auditabilidad: cuales son exactamente las variables que sostienen la conclusion. Reune `severity`, `root`, `crossed_ratio_pct`, `ask_integer_pct`, `median_bps_ask_positive` y `p90_bps_ask_positive`. La decision que cambia es pasar de impresion visual a regla verificable. El error que evita es que dos inspectores lleguen a conclusiones distintas mirando la misma imagen sin una base numerica comun. Para gobernanza del proyecto, este panel es el que vuelve reproducible la decision para backtest, ML y auditoria."
    )


def _image_explanation_historical(row: pd.Series) -> str:
    return (
        "Esta imagen responde a la pregunta causal externa: existe un framing historico que ayude a entender por que ocurre el episodio. Puede aportar halt context, explained o not strongly explained. La decision que cambia es cuanto peso se concede al contexto en la narrativa final. El error que evita es doble: ignorar una explicacion real o usarla como excusa para absolver un libro que localmente sigue siendo problematico."
    )


def build_quotes_scope_document(project_root: Path, scope_name: str) -> Path:
    if scope_name not in {"good", "review", "bad"}:
        raise ValueError("Quotes scope document active only for `good`, `review` and `bad`.")

    assets_dir = expected_output_dir(project_root, scope_name)
    manifest_path = assets_dir / f"quotes_{scope_name}_case_packs_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Quotes manifest not found: {manifest_path}")

    manifest = pd.read_csv(manifest_path)
    if manifest.empty:
        raise RuntimeError(f"Quotes manifest empty for scope={scope_name}")

    sort_cols = ["taxonomy", "median_bps_ask_positive", "p90_bps_ask_positive", "crossed_rows_ask_positive"]
    manifest = manifest.sort_values(sort_cols, ascending=[True, False, False, False]).reset_index(drop=True)

    if scope_name == "good":
        doc_path = (
            project_root
            / "01_foundations"
            / "inspection_dossiers"
            / "quotes"
            / "good_justification"
            / "quotes_good_cases_v0_1.md"
        )
        title = "# Quotes Good Cases v0.1"
        intro = (
            "Este documento consolida una muestra historica representativa de la franja `good` de `quotes`. "
            "No enumera exhaustivamente todo el universo bueno: selecciona ejemplos de las familias buenas principales "
            "para justificar como se ve un libro sano, un residuo micro-noise aceptable, un persistent soft low compatible "
            "con consumo principal y un caso de rollover UTC limpio."
        )
    elif scope_name == "review":
        doc_path = (
            project_root
            / "01_foundations"
            / "inspection_dossiers"
            / "quotes"
            / "flagged_case_evidence_packs"
            / "quotes_review_cases_v0_1.md"
        )
        title = "# Quotes Review Cases v0.1"
        intro = (
            "Este documento consolida los casos `review` de `quotes` usando packs visuales completos. "
            "Cada caso presenta la ventana raw del crossed positivo, el contexto de sesion completa, "
            "diagnosticos estructurales y, cuando existe, la imagen historica de certificacion."
        )
    else:
        doc_path = (
            project_root
            / "01_foundations"
            / "inspection_dossiers"
            / "quotes"
            / "bad_case_evidence_packs"
            / "quotes_bad_cases_v0_1.md"
        )
        title = "# Quotes Bad Cases v0.1"
        intro = (
            "Este documento consolida los casos `bad` de `quotes` usando packs visuales completos. "
            "Cada caso presenta la ventana raw del crossed positivo, el contexto de sesion completa, "
            "diagnosticos estructurales y, cuando existe, la imagen historica de certificacion."
        )

    lines: list[str] = [title, "", intro, "", f"Total cases: `{len(manifest)}`", "", "## Menu", ""]
    for i, row in manifest.iterrows():
        slug = f"{str(row['ticker']).upper()} {str(row['date'])}"
        anchor = f"{str(row['ticker']).lower()}-{str(row['date'])}"
        lines.append(f"{i + 1}. [{slug}](#{anchor})")

    lines.extend(["", "## Cases", ""])

    for i, row in manifest.iterrows():
        ticker = str(row["ticker"]).upper()
        date_str = str(row["date"])
        meta = _lookup_company_metadata(ticker)
        anchor_title = f"### {i + 1}. {ticker} {date_str}"
        lines.extend(
            [
                anchor_title,
                "",
                f"company_name: `{meta['company_name']}`" if meta["company_name"] else "company_name: ``",
                (
                    f"primary_exchange: `{meta['primary_exchange_label']}` (`{meta['primary_exchange']}`)"
                    if meta["primary_exchange"]
                    else "primary_exchange: ``"
                ),
                (
                    f"market_locale: `{meta['market']}/{meta['locale']}`"
                    if meta["market"] or meta["locale"]
                    else "market_locale: ``"
                ),
                f"scope: `{row['scope']}`",
                f"ticker: `{ticker}`",
                f"date: `{date_str}`",
                f"taxonomy: `{row['taxonomy']}`",
                f"positive_cross_bucket: `{row['positive_cross_bucket']}`",
                f"severity: `{row['severity']}`",
                f"root: `{row['root']}`",
                f"rows: `{int(row['rows'])}`",
                f"crossed_ratio_pct: `{float(row['crossed_ratio_pct']):.6f}`",
                f"crossed_rows_raw: `{int(row['crossed_rows_raw'])}`",
                f"crossed_rows_ask_zero: `{int(row['crossed_rows_ask_zero'])}`",
                f"crossed_rows_ask_positive: `{int(row['crossed_rows_ask_positive'])}`",
                f"ask_integer_pct: `{float(row['ask_integer_pct']):.6f}`",
                f"median_bps_ask_positive: `{float(row['median_bps_ask_positive']):.6f}`",
                f"p90_bps_ask_positive: `{float(row['p90_bps_ask_positive']):.6f}`",
                f"file: `{row['source_file']}`",
                "",
                "#### Analisis Forense",
                _quotes_forensic_analysis(row),
                "",
                "#### 00 Event Month Context",
                _image_explanation_event_month(row),
                "",
                f"![{ticker} {date_str} month context]({_md_rel(Path(row['event_month_png']), doc_path)})",
                "",
            ]
        )
        adjusted_proxy = ""
        adjusted_proxy_value = row.get("adjusted_proxy_png", "")
        if pd.notna(adjusted_proxy_value):
            adjusted_proxy = str(adjusted_proxy_value).strip()
        if adjusted_proxy:
            lines.extend(
                [
                    "#### 00a Adjusted Proxy Contrast",
                    _image_explanation_adjusted_proxy(row),
                    "",
                    f"![{ticker} {date_str} adjusted proxy]({_md_rel(Path(adjusted_proxy), doc_path)})",
                    "",
                ]
            )
        lines.extend(
            [
                "#### 00b Event Month Quotes Context",
                _image_explanation_event_month_quotes(row),
                "",
                f"![{ticker} {date_str} month quotes context]({_md_rel(Path(row['event_month_quotes_png']), doc_path)})",
                "",
                "#### 01 Raw Window",
                _image_explanation_raw(row),
                "",
                f"![{ticker} {date_str} raw]({_md_rel(Path(row['raw_window_png']), doc_path)})",
                "",
                "#### 02 Full Session Context",
                _image_explanation_session(row),
                "",
                f"![{ticker} {date_str} session]({_md_rel(Path(row['full_session_png']), doc_path)})",
                "",
                "#### 03 Structure Diagnostics",
                _image_explanation_diagnostics(row),
                "",
                f"![{ticker} {date_str} diagnostics]({_md_rel(Path(row['structure_diag_png']), doc_path)})",
                "",
                "#### 04 Summary Card",
                _image_explanation_summary(row),
                "",
                f"![{ticker} {date_str} summary]({_md_rel(Path(row['summary_card_png']), doc_path)})",
            ]
        )
        historical_context = ""
        historical_context_value = row.get("historical_context_png", "")
        if pd.notna(historical_context_value):
            historical_context = str(historical_context_value).strip()
        if historical_context:
            lines.extend(
                [
                    "",
                    "#### 05 Historical Context",
                    _image_explanation_historical(row),
                    "",
                    f"![{ticker} {date_str} historical]({_md_rel(Path(historical_context), doc_path)})",
                ]
            )
        lines.extend(["", "---", ""])

    doc_path.write_text("\n".join(lines), encoding="utf-8")
    return doc_path


def export_quotes_case_packs(
    project_root: Path,
    scope_name: str,
    clean_output_dir: bool = True,
) -> pd.DataFrame:
    if scope_name not in {"good", "review", "bad"}:
        raise ValueError("Quotes exporter activo solo para `good`, `review` y `bad`.")

    scope = get_scope(scope_name)
    out_root = expected_output_dir(project_root, scope_name)
    if clean_output_dir and out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    if scope_name == "good":
        pool = build_quotes_good_pool().copy().reset_index(drop=True)
    else:
        pool = build_quotes_case_pool()
        pool = pool.loc[pool["scope_name"].eq(scope_name)].copy().reset_index(drop=True)
    exported_rows: list[dict[str, object]] = []

    for _, row in pool.iterrows():
        slug = _safe_case_slug(row)
        case_dir = out_root / slug
        case_dir.mkdir(parents=True, exist_ok=True)

        month_path = case_dir / "00_event_month_context.png"
        adjusted_proxy_path = case_dir / "00a_event_month_adjusted_proxy.png"
        month_quotes_path = case_dir / "00b_event_month_quotes_context.png"
        raw_path = case_dir / "01_raw_window.png"
        session_path = case_dir / "02_full_session_context.png"
        diag_path = case_dir / "03_structure_diagnostics.png"
        summary_path = case_dir / "04_summary_card.png"

        _save_event_month_context(row, month_path, days_before=15, days_after=15)
        adjusted_proxy_meta = _save_event_month_adjusted_proxy_context(
            row,
            adjusted_proxy_path,
            days_before=15,
            days_after=15,
        )
        _save_event_month_quotes_context(row, month_quotes_path, days_before=15, days_after=15)
        _save_raw_window(row, raw_path, window=180, use_index_x=False)
        _save_full_session_context(row, session_path)
        _save_structure_diagnostics(row, diag_path)
        _save_summary_card(row, summary_path)

        historical_img = _match_historical_context_image(row)
        historical_rel = ""
        if historical_img is not None:
            copied = case_dir / "05_historical_context.png"
            shutil.copy2(historical_img, copied)
            historical_rel = str(copied)

        note_path = case_dir / "case_note.md"
        note_path.write_text(_build_case_note(row, historical_img), encoding="utf-8")

        exported_rows.append(
            {
                "scope": scope_name,
                "ticker": row["ticker"],
                "date": row["date_str"],
                "taxonomy": row["taxonomy"],
                "positive_cross_bucket": row["positive_cross_bucket"],
                "severity": row["severity"],
                "root": row["root"],
                "rows": int(row["rows"]),
                "crossed_ratio_pct": float(row["m.crossed_ratio_pct"]),
                "crossed_rows_raw": int(row["crossed_rows_raw"]),
                "crossed_rows_ask_zero": int(row["crossed_rows_ask_zero"]),
                "crossed_rows_ask_positive": int(row["crossed_rows_ask_positive"]),
                "ask_integer_pct": float(row["m.ask_integer_pct"]),
                "median_bps_ask_positive": float(row["cross_rel_bps_median_ask_positive"]),
                "p90_bps_ask_positive": float(row["cross_rel_bps_p90_ask_positive"]),
                "case_dir": str(case_dir),
                "event_month_png": str(month_path),
                "adjusted_proxy_png": str(adjusted_proxy_path) if adjusted_proxy_meta is not None else "",
                "event_month_quotes_png": str(month_quotes_path),
                "raw_window_png": str(raw_path),
                "full_session_png": str(session_path),
                "structure_diag_png": str(diag_path),
                "summary_card_png": str(summary_path),
                "historical_context_png": historical_rel,
                "case_note_md": str(note_path),
                "source_file": row["file"],
                "post_event_dividend_sum": float(adjusted_proxy_meta["post_event_dividend_sum"]) if adjusted_proxy_meta is not None else 0.0,
                "post_event_dividend_count": int(adjusted_proxy_meta["post_event_dividend_count"]) if adjusted_proxy_meta is not None else 0,
                "future_split_factor": float(adjusted_proxy_meta["future_split_factor"]) if adjusted_proxy_meta is not None else 1.0,
                "future_split_count": int(adjusted_proxy_meta["future_split_count"]) if adjusted_proxy_meta is not None else 0,
                "event_close_raw": float(adjusted_proxy_meta["event_close_raw"]) if adjusted_proxy_meta is not None else np.nan,
                "event_close_adjusted_proxy": float(adjusted_proxy_meta["event_close_adjusted_proxy"]) if adjusted_proxy_meta is not None else np.nan,
                "event_quote_mid_raw": float(adjusted_proxy_meta["event_quote_mid_raw"]) if adjusted_proxy_meta is not None else np.nan,
                "event_quote_mid_split_normalized": float(adjusted_proxy_meta["event_quote_mid_split_normalized"]) if adjusted_proxy_meta is not None else np.nan,
                "event_daily_split_normalized": float(adjusted_proxy_meta["event_daily_split_normalized"]) if adjusted_proxy_meta is not None else np.nan,
            }
        )

    manifest = pd.DataFrame(exported_rows)
    manifest_path = out_root / f"quotes_{scope_name}_case_packs_manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    return manifest


def _render_quotes_positive_case(row: pd.Series, window: int, use_index_x: bool) -> None:
    summary = _summary_frame(row)
    display(summary)
    interpretation = (
        "Caso sin crossed positivo material; la lectura se apoya en limpieza local o residuo leve."
        if row["positive_cross_bucket"] == "no_positive_cross"
        else "Caso dominado por crossed positivo leve."
        if row["positive_cross_bucket"] == "positive_cross_mild_lt5bps"
        else "Caso dominado por crossed positivo moderado."
        if row["positive_cross_bucket"] == "positive_cross_moderate_5to25bps"
        else "Caso dominado por crossed positivo severo."
    )
    display(
        Markdown(
            f"**Lectura rapida:** {interpretation} El grafico muestra solo una ventana alrededor del bloque crossed relevante para que la lectura sea visualmente limpia."
        )
    )
    temp_dir = Path.cwd() / ".quotes_preview_tmp"
    temp_dir.mkdir(exist_ok=True)
    tmp_path = temp_dir / "preview.png"
    _save_raw_window(row, tmp_path, window=window, use_index_x=use_index_x)
    img = plt.imread(tmp_path)
    plt.figure(figsize=(16, 9))
    plt.imshow(img)
    plt.axis("off")
    plt.show()


def build_quotes_case_selector(scope_name: str = "review"):
    if scope_name == "good":
        positive_cases = build_quotes_good_pool().copy()
    else:
        positive_cases = build_quotes_case_pool()
        positive_cases = positive_cases.loc[positive_cases["scope_name"].eq(scope_name)].copy()
    if positive_cases.empty:
        raise RuntimeError(f"No hay casos historicos disponibles para scope={scope_name}.")

    taxonomy_labels = {
        tax: f"{tax} ({int((positive_cases['taxonomy'] == tax).sum())} casos)"
        for tax in sorted(positive_cases["taxonomy"].dropna().astype(str).unique().tolist())
    }

    taxonomy_dd = widgets.Dropdown(
        options=[(label, tax) for tax, label in taxonomy_labels.items()],
        description="taxonomy",
        layout=widgets.Layout(width="420px"),
    )
    bucket_dd = widgets.Dropdown(
        description="regime",
        layout=widgets.Layout(width="240px"),
    )
    case_dd = widgets.Dropdown(
        description="file",
        layout=widgets.Layout(width="900px"),
    )
    window_slider = widgets.IntSlider(
        value=600,
        min=100,
        max=5000,
        step=100,
        description="window",
        continuous_update=False,
        layout=widgets.Layout(width="420px"),
    )
    index_toggle = widgets.Checkbox(value=False, description="usar indice x", indent=False)

    summary_out = widgets.Output()
    is_initializing = {"value": True}

    def _bucket_options(taxonomy: str):
        sub = positive_cases.loc[positive_cases["taxonomy"].eq(taxonomy)].copy()
        order = [
            "no_positive_cross",
            "positive_cross_mild_lt5bps",
            "positive_cross_moderate_5to25bps",
            "positive_cross_severe_ge25bps",
        ]
        return [
            (f"{POSITIVE_BUCKET_LABELS.get(b, b)} ({int(sub['positive_cross_bucket'].eq(b).sum())})", b)
            for b in order
            if int(sub["positive_cross_bucket"].eq(b).sum()) > 0
        ]

    def _case_options(taxonomy: str, bucket: str):
        sub = positive_cases.loc[
            positive_cases["taxonomy"].eq(taxonomy)
            & positive_cases["positive_cross_bucket"].eq(bucket)
        ].copy()
        return [(row["case_label"], int(idx)) for idx, row in sub.iterrows()]

    def _refresh_bucket(*_):
        opts = _bucket_options(taxonomy_dd.value)
        bucket_dd.options = opts
        if opts:
            bucket_dd.value = opts[0][1]

    def _refresh_case(*_):
        opts = _case_options(taxonomy_dd.value, bucket_dd.value)
        case_dd.options = opts
        if opts:
            case_dd.value = opts[0][1]

    def _render(*_):
        if is_initializing["value"]:
            return
        if case_dd.value is None:
            return
        row = positive_cases.loc[int(case_dd.value)].copy()
        with summary_out:
            clear_output(wait=True)
            display(Markdown(f"## Quotes inspection | scope={scope_name}"))
            _render_quotes_positive_case(row, window_slider.value, index_toggle.value)

    taxonomy_dd.observe(_refresh_bucket, names="value")
    bucket_dd.observe(_refresh_case, names="value")
    for w in [taxonomy_dd, bucket_dd, case_dd, window_slider, index_toggle]:
        w.observe(_render, names="value")

    _refresh_bucket()
    _refresh_case()
    is_initializing["value"] = False

    box = widgets.VBox(
        [
            widgets.HBox([taxonomy_dd, bucket_dd]),
            case_dd,
            widgets.HBox([window_slider, index_toggle]),
            summary_out,
        ]
    )
    _render()
    return box
