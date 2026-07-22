from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


ADDITIONAL_ROOT = Path(r"C:\TSIS_Data\data\additional")
UNIVERSE_PARQUET = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet"
)
PRIOR_AUDIT_ROOT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\additional_audit\20260405_additional_lt1b_coverage"
)
OUT_ROOT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\additional\cache_v2"
)
HALTS_CACHE = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\halts\cache_v2"
)
SHORT_CACHE = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\short\cache_v2"
)
QUOTES_CURRENT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet"
)
TRADES_CURRENT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet"
)
REFERENCE_RAW_ROOT = Path(r"D:\reference")

TICKER_DATASETS = {
    "splits": ("corporate_actions", "splits"),
    "dividends": ("corporate_actions", "dividends"),
    "ticker_events": ("corporate_actions", "ticker_events"),
    "news": ("news", "news"),
    "ipos": ("ipos", "ipos"),
    "income_statements": ("financials", "income_statements"),
    "balance_sheets": ("financials", "balance_sheets"),
    "cash_flow_statements": ("financials", "cash_flow_statements"),
    "ratios": ("financials", "ratios"),
}
MACRO_DATASETS = ["inflation", "inflation_expectations", "treasury_yields"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_universe() -> list[str]:
    df = pd.read_parquet(UNIVERSE_PARQUET, columns=["ticker"])
    ser = df["ticker"].astype("string").str.strip().dropna()
    return sorted({x.upper() for x in ser.tolist() if x})


def read_prior_summary() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ticker_summary = pd.read_parquet(PRIOR_AUDIT_ROOT / "additional_ticker_datasets_summary.parquet")
    by_file = pd.read_parquet(PRIOR_AUDIT_ROOT / "additional_ticker_datasets_by_file.parquet")
    macro_summary = pd.read_parquet(PRIOR_AUDIT_ROOT / "additional_macro_datasets_summary.parquet")
    return ticker_summary, by_file, macro_summary


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_parquet_file(path: str | Path) -> pd.DataFrame:
    pf = pq.ParquetFile(str(path))
    return pf.read().to_pandas()


def infer_family(dataset: str) -> str:
    if dataset in {"income_statements", "balance_sheets", "cash_flow_statements"}:
        return "financials_core"
    if dataset == "ratios":
        return "financials_ratios"
    if dataset == "news":
        return "news"
    if dataset == "ipos":
        return "ipos"
    if dataset in {"splits", "dividends", "ticker_events"}:
        return "corporate_actions_additional"
    if dataset in MACRO_DATASETS:
        return "economic"
    return "unknown"


def build_dataset_inventory(by_file: pd.DataFrame) -> pd.DataFrame:
    df = by_file.copy()
    df["dataset_family"] = df["dataset"].map(infer_family)
    return df.sort_values(["dataset", "ticker"]).reset_index(drop=True)


def build_effective_coverage_summary(ticker_summary: pd.DataFrame, macro_summary: pd.DataFrame) -> pd.DataFrame:
    t = ticker_summary.copy()
    t["dataset_family"] = t["dataset"].map(infer_family)
    t["dataset_kind"] = "ticker_based"
    t["effective_rows_total"] = t["rows_total"]
    t["effective_non_empty_pct"] = t["coverage_non_empty_pct"]

    m = macro_summary.copy()
    m["dataset_family"] = m["dataset"].map(infer_family)
    m["dataset_kind"] = "macro"
    m["effective_rows_total"] = m["rows_total"]
    m["effective_non_empty_pct"] = 100.0
    for col in t.columns:
        if col not in m.columns:
            m[col] = pd.NA
    for col in m.columns:
        if col not in t.columns:
            t[col] = pd.NA
    cols = sorted(set(t.columns) | set(m.columns))
    return pd.concat([t[cols], m[cols]], ignore_index=True)


def build_family_summary(coverage_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for family, grp in coverage_summary.groupby("dataset_family", dropna=False):
        ticker_grp = grp[grp["dataset_kind"].eq("ticker_based")].copy()
        macro_grp = grp[grp["dataset_kind"].eq("macro")].copy()
        rows.append(
            {
                "dataset_family": family,
                "datasets": sorted(grp["dataset"].astype(str).tolist()),
                "ticker_based_datasets": sorted(ticker_grp["dataset"].astype(str).tolist()),
                "macro_datasets": sorted(macro_grp["dataset"].astype(str).tolist()),
                "mean_effective_non_empty_pct": float(pd.to_numeric(ticker_grp["effective_non_empty_pct"], errors="coerce").mean()) if not ticker_grp.empty else pd.NA,
                "min_effective_non_empty_pct": float(pd.to_numeric(ticker_grp["effective_non_empty_pct"], errors="coerce").min()) if not ticker_grp.empty else pd.NA,
                "rows_total_sum": int(pd.to_numeric(grp["effective_rows_total"], errors="coerce").fillna(0).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("dataset_family").reset_index(drop=True)


def build_schema_samples(by_file: pd.DataFrame) -> pd.DataFrame:
    samples: list[dict[str, Any]] = []
    for dataset in list(TICKER_DATASETS.keys()):
        sub = by_file[(by_file["dataset"] == dataset) & (by_file["is_non_empty"])].copy()
        if sub.empty:
            samples.append(
                {
                    "dataset": dataset,
                    "dataset_family": infer_family(dataset),
                    "sample_file": None,
                    "sample_rows": 0,
                    "columns": [],
                    "has_empty_flag": False,
                    "has_array_fields": False,
                    "has_nested_object_fields": False,
                }
            )
            continue
        sample_path = Path(str(sub.iloc[0]["file_path"]))
        pf = pq.ParquetFile(str(sample_path))
        table = pf.read()
        cols = table.schema.names
        pdf = table.to_pandas()
        has_array = any(isinstance(v, (list, tuple)) or getattr(v, "ndim", 0) == 1 for v in pdf.iloc[0].tolist()) if not pdf.empty else False
        has_nested = any(isinstance(v, dict) for v in pdf.iloc[0].tolist()) if not pdf.empty else False
        samples.append(
            {
                "dataset": dataset,
                "dataset_family": infer_family(dataset),
                "sample_file": str(sample_path),
                "sample_rows": int(table.num_rows),
                "columns": cols,
                "has_empty_flag": "_empty" in cols,
                "has_array_fields": bool(has_array),
                "has_nested_object_fields": bool(has_nested),
            }
        )
    for dataset in MACRO_DATASETS:
        sample_path = ADDITIONAL_ROOT / "economic" / f"{dataset}.parquet"
        pf = pq.ParquetFile(str(sample_path))
        table = pf.read()
        cols = table.schema.names
        samples.append(
            {
                "dataset": dataset,
                "dataset_family": infer_family(dataset),
                "sample_file": str(sample_path),
                "sample_rows": int(table.num_rows),
                "columns": cols,
                "has_empty_flag": "_empty" in cols,
                "has_array_fields": False,
                "has_nested_object_fields": False,
            }
        )
    return pd.DataFrame(samples).sort_values("dataset").reset_index(drop=True)


def build_financials_summary(by_file: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for dataset in ["income_statements", "balance_sheets", "cash_flow_statements", "ratios"]:
        sub = by_file[(by_file["dataset"] == dataset) & (by_file["is_non_empty"])].copy()
        if sub.empty:
            rows.append({"dataset": dataset, "dataset_family": infer_family(dataset), "non_empty_files": 0})
            continue
        sample_path = Path(str(sub.iloc[0]["file_path"]))
        df = read_parquet_file(sample_path)
        rows.append(
            {
                "dataset": dataset,
                "dataset_family": infer_family(dataset),
                "non_empty_files": int(len(sub)),
                "sample_rows": int(len(df)),
                "sample_columns": list(df.columns),
                "has_period_end": "period_end" in df.columns,
                "has_filing_date": "filing_date" in df.columns,
                "has_timeframe": "timeframe" in df.columns,
                "sample_timeframes": sorted(df["timeframe"].dropna().astype(str).unique().tolist()) if "timeframe" in df.columns else [],
                "sample_has_multi_tickers_array": "tickers" in df.columns,
            }
        )
    return pd.DataFrame(rows)


def build_news_summary(by_file: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sub = by_file[(by_file["dataset"] == "news") & (by_file["is_non_empty"])].copy()
    if sub.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    ticker_density = sub[["ticker", "rows"]].rename(columns={"rows": "news_rows"}).sort_values("news_rows", ascending=False).reset_index(drop=True)

    sample_path = Path(str(sub.iloc[0]["file_path"]))
    df = read_parquet_file(sample_path)
    summary = pd.DataFrame(
        [
            {
                "dataset": "news",
                "non_empty_files": int(len(sub)),
                "sample_rows": int(len(df)),
                "sample_columns": list(df.columns),
                "has_published_utc": "published_utc" in df.columns,
                "has_multi_ticker_field": "tickers" in df.columns,
                "has_keywords": "keywords" in df.columns,
                "has_insights": "insights" in df.columns,
                "sample_publishers": sorted(df["publisher.name"].dropna().astype(str).unique().tolist())[:10] if "publisher.name" in df.columns else [],
            }
        ]
    )

    multi_rows: list[dict[str, Any]] = []
    for path in sub["file_path"].head(50):
        frame = read_parquet_file(path)
        if frame.empty:
            continue
        if "tickers" in frame.columns:
            counts = frame["tickers"].apply(lambda x: len(x) if hasattr(x, "__len__") and not isinstance(x, str) else (1 if pd.notna(x) else 0))
            multi_rows.append(
                {
                    "file_path": str(path),
                    "ticker": str(frame["ticker"].iloc[0]) if "ticker" in frame.columns and not frame.empty else None,
                    "rows": int(len(frame)),
                    "mean_tickers_per_news": float(pd.to_numeric(counts, errors="coerce").mean()),
                    "max_tickers_per_news": int(pd.to_numeric(counts, errors="coerce").max()),
                }
            )
    multi_summary = pd.DataFrame(multi_rows)
    return summary, ticker_density, multi_summary


def _len_like(value: Any) -> int:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    if isinstance(value, str):
        return 1 if value.strip() else 0
    try:
        return int(len(value))
    except Exception:
        return 0


def build_news_event_index(by_file: pd.DataFrame) -> pd.DataFrame:
    sub = by_file[(by_file["dataset"] == "news") & (by_file["is_non_empty"])].copy()
    if sub.empty:
        return pd.DataFrame()
    records: list[dict[str, Any]] = []
    for path_str in sub["file_path"]:
        path = Path(str(path_str))
        frame = read_parquet_file(path)
        if frame.empty:
            continue
        frame = frame.copy()
        frame["published_utc"] = pd.to_datetime(frame["published_utc"], utc=True, errors="coerce")
        frame["news_date"] = frame["published_utc"].dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
        for _, row in frame.iterrows():
            records.append(
                {
                    "ticker": str(row.get("ticker")).upper() if pd.notna(row.get("ticker")) else None,
                    "id": row.get("id"),
                    "published_utc": row.get("published_utc"),
                    "news_date": row.get("news_date"),
                    "title": row.get("title"),
                    "publisher_name": row.get("publisher.name"),
                    "article_url": row.get("article_url"),
                    "n_tickers": _len_like(row.get("tickers")),
                    "n_keywords": _len_like(row.get("keywords")),
                    "n_insights": _len_like(row.get("insights")),
                    "is_multi_ticker": _len_like(row.get("tickers")) > 1,
                }
            )
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    return df.sort_values(["ticker", "published_utc"]).reset_index(drop=True)


def build_news_causal_links(news_event_index: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if news_event_index.empty:
        return pd.DataFrame(), pd.DataFrame()

    halts = pd.read_parquet(
        HALTS_CACHE / "halts_quotes_trades_visual_cases.parquet",
        columns=["ticker", "visual_date", "visual_case_bucket", "rank_score", "events_in_visual"],
    ).rename(
        columns={
            "visual_date": "news_date",
            "visual_case_bucket": "halt_visual_bucket",
            "rank_score": "halt_rank_score",
            "events_in_visual": "halt_events_in_visual",
        }
    )
    halts["ticker"] = halts["ticker"].astype(str).str.upper()
    halts["news_date"] = pd.to_datetime(halts["news_date"], errors="coerce").dt.normalize()

    quotes = pd.read_parquet(
        QUOTES_CURRENT,
        columns=["ticker", "date", "severity", "issues", "warns", "action", "rows"],
    ).rename(
        columns={
            "date": "news_date",
            "severity": "quotes_severity",
            "issues": "quotes_issues",
            "warns": "quotes_warns",
            "action": "quotes_action",
            "rows": "quotes_rows",
        }
    )
    quotes["ticker"] = quotes["ticker"].astype(str).str.upper()
    quotes["news_date"] = pd.to_datetime(quotes["news_date"], errors="coerce").dt.normalize()

    trades = pd.read_parquet(
        TRADES_CURRENT,
        columns=["ticker", "date", "severity", "issues", "warns", "action", "rows"],
    ).rename(
        columns={
            "date": "news_date",
            "severity": "trades_severity",
            "issues": "trades_issues",
            "warns": "trades_warns",
            "action": "trades_action",
            "rows": "trades_rows",
        }
    )
    trades["ticker"] = trades["ticker"].astype(str).str.upper()
    trades["news_date"] = pd.to_datetime(trades["news_date"], errors="coerce").dt.normalize()

    short_sv = pd.read_parquet(
        SHORT_CACHE / "short_volume_market_link_candidates.parquet",
        columns=["ticker", "date", "market_link_bucket", "short_volume_ratio"],
    ).rename(columns={"date": "news_date", "market_link_bucket": "short_market_link_bucket"})
    short_sv["ticker"] = short_sv["ticker"].astype(str).str.upper()
    short_sv["news_date"] = pd.to_datetime(short_sv["news_date"], errors="coerce").dt.normalize()

    df = news_event_index.copy()
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df["news_date"] = pd.to_datetime(df["news_date"], errors="coerce").dt.normalize()
    df = df.merge(halts, on=["ticker", "news_date"], how="left")
    df = df.merge(quotes, on=["ticker", "news_date"], how="left")
    df = df.merge(trades, on=["ticker", "news_date"], how="left")
    df = df.merge(short_sv, on=["ticker", "news_date"], how="left")

    q_problem = df["quotes_severity"].astype(str).isin(["HARD_FAIL", "SOFT_FAIL"])
    t_problem = df["trades_severity"].astype(str).isin(["HARD_FAIL", "SOFT_FAIL"])
    has_halt = df["halt_visual_bucket"].notna()
    has_short = df["short_market_link_bucket"].notna()
    mono = ~df["is_multi_ticker"].fillna(False)

    df["news_link_bucket"] = "news_context_only"
    df.loc[has_halt & (q_problem | t_problem) & mono, "news_link_bucket"] = "news_near_halt_market_event"
    df.loc[(~has_halt) & (q_problem | t_problem) & mono, "news_link_bucket"] = "news_near_market_anomaly"
    df.loc[(~has_halt) & (~q_problem) & (~t_problem) & has_short, "news_link_bucket"] = "news_near_short_flow_only"
    df.loc[df["is_multi_ticker"].fillna(False) & (q_problem | t_problem | has_halt), "news_link_bucket"] = "review_multi_ticker_ambiguous_news"

    summary = (
        df.groupby("news_link_bucket", dropna=False)
        .agg(
            events=("id", "count"),
            tickers=("ticker", "nunique"),
            mean_tickers_per_news=("n_tickers", "mean"),
        )
        .reset_index()
        .sort_values("events", ascending=False)
        .reset_index(drop=True)
    )
    return df, summary


def build_corporate_actions_summary(by_file: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for dataset in ["splits", "dividends", "ticker_events"]:
        sub = by_file[(by_file["dataset"] == dataset) & (by_file["is_non_empty"])].copy()
        sample_cols: list[str] = []
        sample_rows = 0
        if not sub.empty:
            sample_path = Path(str(sub.iloc[0]["file_path"]))
            frame = read_parquet_file(sample_path)
            sample_cols = list(frame.columns)
            sample_rows = int(len(frame))
        rows.append(
            {
                "dataset": dataset,
                "dataset_family": infer_family(dataset),
                "non_empty_files": int(len(sub)),
                "sample_rows": sample_rows,
                "sample_columns": sample_cols,
            }
        )
    return pd.DataFrame(rows)


def build_ipo_event_index(by_file: pd.DataFrame) -> pd.DataFrame:
    sub = by_file[(by_file["dataset"] == "ipos") & (by_file["is_non_empty"])].copy()
    if sub.empty:
        return pd.DataFrame()
    frames: list[pd.DataFrame] = []
    for path_str in sub["file_path"]:
        frame = read_parquet_file(path_str)
        if frame.empty:
            continue
        frame = frame.copy()
        if "listing_date" not in frame.columns:
            frame["listing_date"] = pd.NaT
        if "announced_date" not in frame.columns:
            frame["announced_date"] = pd.NaT
        frame["listing_date"] = pd.to_datetime(frame["listing_date"], errors="coerce").dt.normalize()
        frame["announced_date"] = pd.to_datetime(frame["announced_date"], errors="coerce").dt.normalize()
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    return df.sort_values(["ticker", "listing_date"]).reset_index(drop=True)


def build_ipo_market_links(ipo_event_index: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if ipo_event_index.empty:
        return pd.DataFrame(), pd.DataFrame()
    halts = pd.read_parquet(
        HALTS_CACHE / "halts_quotes_trades_visual_cases.parquet",
        columns=["ticker", "visual_date", "visual_case_bucket", "rank_score", "events_in_visual"],
    ).rename(
        columns={
            "visual_date": "listing_date",
            "visual_case_bucket": "halt_visual_bucket",
            "rank_score": "halt_rank_score",
            "events_in_visual": "halt_events_in_visual",
        }
    )
    halts["ticker"] = halts["ticker"].astype(str).str.upper()
    halts["listing_date"] = pd.to_datetime(halts["listing_date"], errors="coerce").dt.normalize()

    quotes = pd.read_parquet(
        QUOTES_CURRENT,
        columns=["ticker", "date", "severity", "issues", "warns", "action", "rows"],
    ).rename(
        columns={
            "date": "listing_date",
            "severity": "quotes_severity",
            "issues": "quotes_issues",
            "warns": "quotes_warns",
            "action": "quotes_action",
            "rows": "quotes_rows",
        }
    )
    quotes["ticker"] = quotes["ticker"].astype(str).str.upper()
    quotes["listing_date"] = pd.to_datetime(quotes["listing_date"], errors="coerce").dt.normalize()

    trades = pd.read_parquet(
        TRADES_CURRENT,
        columns=["ticker", "date", "severity", "issues", "warns", "action", "rows"],
    ).rename(
        columns={
            "date": "listing_date",
            "severity": "trades_severity",
            "issues": "trades_issues",
            "warns": "trades_warns",
            "action": "trades_action",
            "rows": "trades_rows",
        }
    )
    trades["ticker"] = trades["ticker"].astype(str).str.upper()
    trades["listing_date"] = pd.to_datetime(trades["listing_date"], errors="coerce").dt.normalize()

    df = ipo_event_index.copy()
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df = df.merge(halts, on=["ticker", "listing_date"], how="left")
    df = df.merge(quotes, on=["ticker", "listing_date"], how="left")
    df = df.merge(trades, on=["ticker", "listing_date"], how="left")

    q_problem = df["quotes_severity"].astype(str).isin(["HARD_FAIL", "SOFT_FAIL"])
    t_problem = df["trades_severity"].astype(str).isin(["HARD_FAIL", "SOFT_FAIL"])
    has_halt = df["halt_visual_bucket"].notna()
    df["ipo_link_bucket"] = "ipo_market_clean"
    df.loc[(q_problem | t_problem) & (~has_halt), "ipo_link_bucket"] = "ipo_near_market_anomaly"
    df.loc[has_halt & (q_problem | t_problem), "ipo_link_bucket"] = "ipo_near_halt_market_event"

    summary = (
        df.groupby("ipo_link_bucket", dropna=False)
        .agg(events=("ticker", "count"), tickers=("ticker", "nunique"))
        .reset_index()
        .sort_values("events", ascending=False)
        .reset_index(drop=True)
    )
    return df, summary


def build_corporate_actions_reference_overlap(by_file: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    split_ref_root = REFERENCE_RAW_ROOT / "splits"
    div_ref_root = REFERENCE_RAW_ROOT / "dividends"
    evt_ref_root = REFERENCE_RAW_ROOT / "events"

    for dataset in ["splits", "dividends", "ticker_events"]:
        sub = by_file[(by_file["dataset"] == dataset) & (by_file["is_non_empty"])].copy()
        for _, rec in sub.iterrows():
            ticker = str(rec["ticker"]).upper()
            add_path = Path(str(rec["file_path"]))
            add_df = read_parquet_file(add_path)
            ref_path = {
                "splits": split_ref_root / f"ticker={ticker}" / f"splits_{ticker}.parquet",
                "dividends": div_ref_root / f"ticker={ticker}" / f"dividends_{ticker}.parquet",
                "ticker_events": evt_ref_root / f"ticker={ticker}" / f"events_{ticker}.parquet",
            }[dataset]
            ref_exists = ref_path.exists()
            ref_df = read_parquet_file(ref_path) if ref_exists else pd.DataFrame()
            overlap_rows = 0
            additional_rows = int(len(add_df))
            reference_rows = int(len(ref_df))
            if dataset == "splits" and not ref_df.empty and {"ticker", "execution_date", "split_from", "split_to"}.issubset(ref_df.columns) and {"ticker", "execution_date", "split_from", "split_to"}.issubset(add_df.columns):
                left = add_df.copy()
                right = ref_df.copy()
                left["execution_date"] = pd.to_datetime(left["execution_date"], errors="coerce").dt.normalize()
                right["execution_date"] = pd.to_datetime(right["execution_date"], errors="coerce").dt.normalize()
                merged = left.merge(right[["ticker", "execution_date", "split_from", "split_to"]], on=["ticker", "execution_date", "split_from", "split_to"], how="inner")
                overlap_rows = int(len(merged))
            elif dataset == "dividends" and not ref_df.empty and {"ticker", "ex_dividend_date", "cash_amount"}.issubset(ref_df.columns) and {"ticker", "ex_dividend_date", "cash_amount"}.issubset(add_df.columns):
                left = add_df.copy()
                right = ref_df.copy()
                left["ex_dividend_date"] = pd.to_datetime(left["ex_dividend_date"], errors="coerce").dt.normalize()
                right["ex_dividend_date"] = pd.to_datetime(right["ex_dividend_date"], errors="coerce").dt.normalize()
                merged = left.merge(right[["ticker", "ex_dividend_date", "cash_amount"]], on=["ticker", "ex_dividend_date", "cash_amount"], how="inner")
                overlap_rows = int(len(merged))
            elif dataset == "ticker_events" and not ref_df.empty and {"ticker", "event_date", "event_type"}.issubset(ref_df.columns):
                left = add_df.copy()
                right = ref_df.copy()
                if "date" not in left.columns or "type" not in left.columns:
                    merged = pd.DataFrame()
                else:
                    left["date"] = pd.to_datetime(left["date"], errors="coerce").dt.normalize()
                    right["event_date"] = pd.to_datetime(right["event_date"], errors="coerce").dt.normalize()
                    left = left.rename(columns={"type": "event_type"})
                    merged = left.merge(right[["ticker", "event_date", "event_type"]], left_on=["ticker", "date", "event_type"], right_on=["ticker", "event_date", "event_type"], how="inner")
                overlap_rows = int(len(merged))

            overlap_bucket = "reference_missing"
            schema_ok = {
                "splits": {"ticker", "execution_date", "split_from", "split_to"}.issubset(ref_df.columns),
                "dividends": {"ticker", "ex_dividend_date", "cash_amount"}.issubset(ref_df.columns),
                "ticker_events": {"ticker", "event_date", "event_type"}.issubset(ref_df.columns),
            }[dataset] if ref_exists else False
            if ref_exists and (reference_rows == 0 or not schema_ok):
                overlap_bucket = "reference_present_but_empty"
            if ref_exists and reference_rows > 0 and overlap_rows == 0:
                overlap_bucket = "reference_present_no_exact_overlap"
            if ref_exists and overlap_rows > 0:
                overlap_bucket = "reference_exact_overlap"

            rows.append(
                {
                    "dataset": dataset,
                    "ticker": ticker,
                    "additional_rows": additional_rows,
                    "reference_rows": reference_rows,
                    "overlap_rows": overlap_rows,
                    "reference_file_exists": ref_exists,
                    "overlap_bucket": overlap_bucket,
                }
            )
    df = pd.DataFrame(rows)
    return df.sort_values(["dataset", "ticker"]).reset_index(drop=True) if not df.empty else df


def build_ipos_summary(by_file: pd.DataFrame) -> pd.DataFrame:
    sub = by_file[(by_file["dataset"] == "ipos") & (by_file["is_non_empty"])].copy()
    sample_cols: list[str] = []
    sample_rows = 0
    if not sub.empty:
        sample_path = Path(str(sub.iloc[0]["file_path"]))
        frame = read_parquet_file(sample_path)
        sample_cols = list(frame.columns)
        sample_rows = int(len(frame))
    return pd.DataFrame(
        [
            {
                "dataset": "ipos",
                "dataset_family": "ipos",
                "non_empty_files": int(len(sub)),
                "sample_rows": sample_rows,
                "sample_columns": sample_cols,
            }
        ]
    )


def build_macro_calendar_summary(macro_summary: pd.DataFrame) -> pd.DataFrame:
    m = macro_summary.copy()
    m["dataset_family"] = "economic"
    return m.sort_values("dataset").reset_index(drop=True)


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    universe = load_universe()
    ticker_summary, by_file, macro_summary = read_prior_summary()

    dataset_inventory = build_dataset_inventory(by_file)
    coverage_summary = build_effective_coverage_summary(ticker_summary, macro_summary)
    family_summary = build_family_summary(coverage_summary)
    schema_samples = build_schema_samples(by_file)
    financials_summary = build_financials_summary(by_file)
    news_summary, news_ticker_density, news_multi_ticker_summary = build_news_summary(by_file)
    news_event_index = build_news_event_index(by_file)
    news_market_links, news_link_summary = build_news_causal_links(news_event_index)
    corp_actions_summary = build_corporate_actions_summary(by_file)
    ipos_summary = build_ipos_summary(by_file)
    macro_calendar_summary = build_macro_calendar_summary(macro_summary)
    ipo_event_index = build_ipo_event_index(by_file)
    ipo_market_links, ipo_link_summary = build_ipo_market_links(ipo_event_index)
    corp_ref_overlap = build_corporate_actions_reference_overlap(by_file)
    corp_ref_overlap_summary = (
        corp_ref_overlap.groupby(["dataset", "overlap_bucket"], dropna=False)
        .agg(tickers=("ticker", "nunique"), rows=("ticker", "count"), overlap_rows=("overlap_rows", "sum"))
        .reset_index()
        .sort_values(["dataset", "rows"], ascending=[True, False])
        .reset_index(drop=True)
        if not corp_ref_overlap.empty
        else pd.DataFrame()
    )

    dataset_inventory.to_parquet(OUT_ROOT / "additional_dataset_inventory.parquet", index=False)
    coverage_summary.to_parquet(OUT_ROOT / "additional_effective_coverage_summary.parquet", index=False)
    family_summary.to_parquet(OUT_ROOT / "additional_family_summary.parquet", index=False)
    schema_samples.to_parquet(OUT_ROOT / "additional_schema_samples.parquet", index=False)
    financials_summary.to_parquet(OUT_ROOT / "additional_financials_summary.parquet", index=False)
    news_summary.to_parquet(OUT_ROOT / "additional_news_summary.parquet", index=False)
    news_ticker_density.to_parquet(OUT_ROOT / "additional_news_ticker_density.parquet", index=False)
    news_multi_ticker_summary.to_parquet(OUT_ROOT / "additional_news_multi_ticker_summary.parquet", index=False)
    news_event_index.to_parquet(OUT_ROOT / "additional_news_event_index.parquet", index=False)
    news_market_links.to_parquet(OUT_ROOT / "additional_news_market_link_candidates.parquet", index=False)
    news_link_summary.to_parquet(OUT_ROOT / "additional_news_link_summary.parquet", index=False)
    corp_actions_summary.to_parquet(OUT_ROOT / "additional_corporate_actions_summary.parquet", index=False)
    ipos_summary.to_parquet(OUT_ROOT / "additional_ipos_summary.parquet", index=False)
    macro_calendar_summary.to_parquet(OUT_ROOT / "additional_macro_calendar_summary.parquet", index=False)
    ipo_event_index.to_parquet(OUT_ROOT / "additional_ipo_event_index.parquet", index=False)
    ipo_market_links.to_parquet(OUT_ROOT / "additional_ipo_market_link_candidates.parquet", index=False)
    ipo_link_summary.to_parquet(OUT_ROOT / "additional_ipo_link_summary.parquet", index=False)
    corp_ref_overlap.to_parquet(OUT_ROOT / "additional_corp_actions_reference_overlap.parquet", index=False)
    corp_ref_overlap_summary.to_parquet(OUT_ROOT / "additional_corp_actions_reference_overlap_summary.parquet", index=False)

    manifest = {
        "built_at_utc": utc_now(),
        "additional_root": str(ADDITIONAL_ROOT),
        "universe_parquet": str(UNIVERSE_PARQUET),
        "prior_audit_root": str(PRIOR_AUDIT_ROOT),
        "out_root": str(OUT_ROOT),
        "universe_tickers": len(universe),
        "artifacts": sorted([p.name for p in OUT_ROOT.glob("*.parquet")]),
    }
    write_json(OUT_ROOT / "additional_build_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
