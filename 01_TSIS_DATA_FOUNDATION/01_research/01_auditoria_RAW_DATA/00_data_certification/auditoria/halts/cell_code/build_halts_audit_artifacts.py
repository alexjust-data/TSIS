from __future__ import annotations

import argparse
import ast
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


@dataclass
class HaltAuditPaths:
    halts_root: Path
    output_root: Path
    universe_path: Path | None

    @property
    def processed_root(self) -> Path:
        return self.halts_root / "processed"

    @property
    def raw_root(self) -> Path:
        return self.halts_root / "raw"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build audit artifacts for halts.")
    parser.add_argument("--halts-root", required=True, help="Root directory of D:\\Halts")
    parser.add_argument("--output-root", required=True, help="Output directory for audit artifacts")
    parser.add_argument("--universe-path", default=None, help="Optional PTI or <1B universe parquet/csv")
    return parser.parse_args()


def build_manifest(paths: HaltAuditPaths) -> dict:
    return {
        "build_name": "halts_audit_artifacts",
        "build_version": "0.1.0",
        "inputs": {
            "halts_root": str(paths.halts_root),
            "processed_root": str(paths.processed_root),
            "raw_root": str(paths.raw_root),
            "universe_path": str(paths.universe_path) if paths.universe_path else None,
        },
        "artifacts": {
            "source_quality_summary": "source_quality_summary.parquet",
            "field_completeness_summary": "field_completeness_summary.parquet",
            "canonical_event_summary": "canonical_event_summary.parquet",
            "duplicate_analysis": "duplicate_analysis.parquet",
            "cross_source_overlap_summary": "cross_source_overlap_summary.parquet",
            "ticker_halt_coverage_summary": "ticker_halt_coverage_summary.parquet",
            "ticker_year_halt_presence": "ticker_year_halt_presence.parquet",
            "event_taxonomy_summary": "event_taxonomy_summary.parquet",
            "halt_event_windows": "halt_event_windows.parquet",
            "halts_lt1b_event_index": "halts_lt1b_event_index.parquet",
            "halts_intraday_overlay_index": "halts_intraday_overlay_index.parquet",
            "halts_quotes_trades_visual_cases": "halts_quotes_trades_visual_cases.parquet",
            "case_index_halts": "case_index_halts.parquet",
            "halts_quotes_link_candidates": "halts_quotes_link_candidates.parquet",
            "halts_trades_link_candidates": "halts_trades_link_candidates.parquet",
            "event_window_alignment_summary": "event_window_alignment_summary.parquet",
        },
    }


def ensure_output_root(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)


def _normalize_text(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.upper()
        .replace({"": pd.NA, "NAN": pd.NA, "<NA>": pd.NA, "NONE": pd.NA})
    )


def _parse_listish(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    if not text or text == "[]":
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (list, tuple, set)):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass
    hits = re.findall(r"'([^']+)'", text) or re.findall(r'"([^"]+)"', text)
    if hits:
        return [str(x).strip() for x in hits if str(x).strip()]
    return [text]


def _parse_metrics_json(value: Any) -> dict[str, Any]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return {}
    if isinstance(value, dict):
        return value
    text = str(value).strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        try:
            parsed = ast.literal_eval(text)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}


def _classify_quotes_taxonomy_simple(work: pd.DataFrame) -> pd.Series:
    crossed = pd.to_numeric(work.get("quotes_crossed_ratio_pct"), errors="coerce").fillna(0.0)
    crossed_rows = pd.to_numeric(work.get("quotes_crossed_rows"), errors="coerce").fillna(0.0)
    ask_integer = pd.to_numeric(work.get("quotes_ask_integer_pct"), errors="coerce").fillna(0.0)
    rows = pd.to_numeric(work.get("quotes_rows"), errors="coerce").fillna(0.0)
    severity = work.get("quotes_severity", pd.Series("", index=work.index)).astype(str)
    ts_shift = work.get("quotes_timestamp_out_of_partition_day", pd.Series(False, index=work.index)).fillna(False).astype(bool)

    conditions = [
        severity.eq("HARD_FAIL") & crossed.ge(90) & ask_integer.ge(90),
        severity.eq("HARD_FAIL") & crossed.ge(20) & ask_integer.ge(80),
        severity.eq("HARD_FAIL") & crossed.ge(20) & ts_shift,
        severity.eq("HARD_FAIL") & crossed.ge(20),
        severity.eq("HARD_FAIL") & crossed.ge(5),
        severity.eq("SOFT_FAIL") & ts_shift & crossed.le(0.1),
        severity.eq("SOFT_FAIL") & crossed.le(0.1),
        severity.eq("SOFT_FAIL") & crossed.gt(0.1),
        severity.eq("PASS"),
    ]
    choices = [
        "extreme_integerized_100pct_crossed",
        "extreme_hard_crossed_gt20_integerized",
        "extreme_hard_crossed_gt20_with_utc_rollover",
        "extreme_hard_crossed_gt20",
        "hard_crossed_gt5",
        "utc_rollover_large_day_clean",
        "soft_crossed_micro_noise",
        "persistent_soft_crossed",
        "clean_pass_or_other",
    ]
    return pd.Series(np.select(conditions, choices, default="clean_pass_or_other"), index=work.index, dtype="string")


def _derive_session_bucket(ts: pd.Series) -> pd.Series:
    hour = ts.dt.hour.fillna(-1).astype(float) + ts.dt.minute.fillna(0).astype(float) / 60.0
    conditions = [
        hour.lt(0),
        hour.lt(9.5),
        hour.le(16.0),
        hour.gt(16.0),
    ]
    choices = [
        "missing",
        "premarket",
        "regular_session",
        "after_hours",
    ]
    return pd.Series(np.select(conditions, choices, default="missing"), index=ts.index, dtype="string")


def _iter_parquet_batches(path: Path, columns: list[str], batch_size: int = 200_000):
    pf = pq.ParquetFile(path)
    for batch in pf.iter_batches(columns=columns, batch_size=batch_size):
        df = batch.to_pandas()
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        yield df


NASDAQ_RAW_PATTERN = re.compile(
    r"Issue Symbol\s+Issue Name\s+Mkt\s+Reason Code\s+Pause Threshold Price\s+Halt Date\s+Halt Time\s+Resumption Date\s+Resumption Quote Time\s+Resumption Trade Time\s+"
    r"(?P<ticker>\S+)\s+"
    r"(?P<issuer_name>.*?)\s*"
    r"(?P<mkt>[A-Z])\s+"
    r"(?P<halt_code>[A-Z0-9]+)\s+"
    r"(?P<pause_threshold>(?:\d+(?:\.\d+)?|\.\d+))?\s*"
    r"(?P<halt_date>\d{2}/\d{2}/\d{4})\s+"
    r"(?P<halt_time>\d{2}:\d{2}:\d{2})\s*"
    r"(?P<resume_date>\d{2}/\d{2}/\d{4})?\s*"
    r"(?P<resume_quote>\d{2}:\d{2}:\d{2})?\s*"
    r"(?P<resume_trade>\d{2}:\d{2}:\d{2})?\s*$"
)


NASDAQ_RAW_PATTERN_ALT = re.compile(
    r"Issue Symbol\s+Issue Name\s+Mkt\s+Reason Code\s+Pause Threshold Price\s+Halt Date\s+Halt Time\s+Resumption Date\s+Resumption Quote Time\s+Resumption Trade Time\s+"
    r"(?P<ticker>\S+)\s+"
    r"(?P<issuer_name>.*?)\s*"
    r"(?P<mkt>[A-Z])\s+"
    r"(?P<halt_code>[A-Z0-9]+)\s+"
    r"(?P<halt_date>\d{2}/\d{2}/\d{4})\s+"
    r"(?P<halt_time>\d{2}:\d{2}:\d{2})\s*"
    r"(?P<pause_threshold>(?:\d+(?:\.\d+)?|\.\d+))?\s*"
    r"(?P<resume_date>\d{2}/\d{2}/\d{4})?\s*"
    r"(?P<resume_quote>\d{2}:\d{2}:\d{2})?\s*"
    r"(?P<resume_trade>\d{2}:\d{2}:\d{2})?\s*$"
)


NASDAQ_MKT_MAP = {
    "Q": "NASDAQ",
    "P": "NYSE ARCA",
    "N": "NYSE",
    "A": "NYSE AMERICAN",
    "C": "OTHER",
}


def _parse_nasdaq_raw_description(text: object) -> dict[str, object]:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return {}
    compact = " ".join(str(text).split())
    match = NASDAQ_RAW_PATTERN.search(compact)
    if not match:
        match = NASDAQ_RAW_PATTERN_ALT.search(compact)
    if not match:
        return {}
    out = match.groupdict()
    halt_date = out.get("halt_date")
    halt_time = out.get("halt_time")
    resume_date = out.get("resume_date")
    resume_quote = out.get("resume_quote")
    resume_trade = out.get("resume_trade")

    parsed: dict[str, object] = {
        "ticker": out.get("ticker"),
        "issuer_name": (out.get("issuer_name") or "").strip() or pd.NA,
        "listing_exchange": NASDAQ_MKT_MAP.get(out.get("mkt") or "", out.get("mkt")),
        "halt_code": out.get("halt_code"),
        "halt_type": out.get("halt_code"),
        "halt_date": pd.to_datetime(halt_date, format="%m/%d/%Y", errors="coerce") if halt_date else pd.NaT,
    }
    parsed["halt_start_et"] = pd.to_datetime(
        f"{halt_date} {halt_time}" if halt_date and halt_time else None,
        format="%m/%d/%Y %H:%M:%S",
        errors="coerce",
    )
    parsed["resume_quote_et"] = pd.to_datetime(
        f"{resume_date} {resume_quote}" if resume_date and resume_quote else None,
        format="%m/%d/%Y %H:%M:%S",
        errors="coerce",
    )
    parsed["resume_trade_et"] = pd.to_datetime(
        f"{resume_date} {resume_trade}" if resume_date and resume_trade else None,
        format="%m/%d/%Y %H:%M:%S",
        errors="coerce",
    )
    return parsed


def _normalize_source_frame(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    out = df.copy()
    if "source" not in out.columns:
        out["source"] = source_name
    out["source"] = out["source"].astype("string").str.strip().str.lower()

    for col in [
        "ticker",
        "issuer_name",
        "listing_exchange",
        "halt_code",
        "halt_type",
        "raw_reason",
        "release_no",
        "item_link",
        "url_source",
        "title",
    ]:
        if col not in out.columns:
            out[col] = pd.NA

    if "is_sec_suspension" not in out.columns:
        out["is_sec_suspension"] = out["source"].eq("sec")

    if "source_priority" not in out.columns:
        out["source_priority"] = 2 if source_name == "nasdaq" else 1

    for col in ["halt_date", "halt_start_et", "resume_quote_et", "resume_trade_et"]:
        if col not in out.columns:
            out[col] = pd.NaT
        out[col] = pd.to_datetime(out[col], errors="coerce")

    out["ticker"] = _normalize_text(out["ticker"])
    out["issuer_name"] = out["issuer_name"].astype("string").str.strip()
    out["listing_exchange"] = _normalize_text(out["listing_exchange"])
    out["halt_code"] = _normalize_text(out["halt_code"])
    out["halt_type"] = out["halt_type"].astype("string").str.strip()
    out["raw_reason"] = out["raw_reason"].astype("string").str.strip()
    out["release_no"] = _normalize_text(out["release_no"])
    out["item_link"] = out["item_link"].astype("string").str.strip()
    out["url_source"] = out["url_source"].astype("string").str.strip()
    out["title"] = out["title"].astype("string").str.strip()

    if source_name == "nasdaq":
        parsed_rows = out["raw_description_text"].map(_parse_nasdaq_raw_description)
        parsed_df = pd.DataFrame(parsed_rows.tolist(), index=out.index)
        if not parsed_df.empty:
            for col in [
                "ticker",
                "issuer_name",
                "listing_exchange",
                "halt_code",
                "halt_type",
                "halt_date",
                "halt_start_et",
                "resume_quote_et",
                "resume_trade_et",
            ]:
                if col in parsed_df.columns:
                    out[col] = out[col].where(out[col].notna(), parsed_df[col])
        out["ticker"] = out["ticker"].fillna(_normalize_text(out["title"]))
        out["ticker"] = _normalize_text(out["ticker"])
        out["issuer_name"] = out["issuer_name"].astype("string").str.strip()
        out["listing_exchange"] = _normalize_text(out["listing_exchange"])
        out["halt_code"] = _normalize_text(out["halt_code"])
        out["halt_type"] = out["halt_type"].astype("string").str.strip()

    out["event_date"] = out["halt_date"].dt.normalize()
    out["halt_start_date"] = out["halt_start_et"].dt.normalize()
    out["resume_trade_date"] = out["resume_trade_et"].dt.normalize()

    return out


def _build_canonical_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    venue_key = (
        out["ticker"].fillna("NA")
        + "|"
        + out["event_date"].astype("string").fillna("NA")
        + "|"
        + out["halt_start_et"].astype("string").fillna("NA")
        + "|"
        + out["halt_code"].fillna("NA")
        + "|"
        + out["halt_type"].astype("string").fillna("NA")
    )

    sec_identity = out["ticker"].fillna(_normalize_text(out["issuer_name"]))
    sec_key = (
        sec_identity.fillna("NA")
        + "|"
        + out["event_date"].astype("string").fillna("NA")
        + "|"
        + out["release_no"].fillna("NA")
    )

    out["event_key_exact"] = out["source"].fillna("NA") + "|" + venue_key
    out["event_key_semantic"] = venue_key
    out.loc[out["source"].eq("sec"), "event_key_exact"] = out.loc[out["source"].eq("sec"), "source"].fillna("NA") + "|" + sec_key[out["source"].eq("sec")]
    out.loc[out["source"].eq("sec"), "event_key_semantic"] = sec_key[out["source"].eq("sec")]

    out["event_id_canonical"] = out["event_key_semantic"]
    return out


def _source_quality_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, sub in df.groupby("source", dropna=False):
        rows.append(
            {
                "source": source,
                "rows": int(len(sub)),
                "ticker_nonnull_rows": int(sub["ticker"].notna().sum()),
                "halt_date_nonnull_rows": int(sub["halt_date"].notna().sum()),
                "halt_start_nonnull_rows": int(sub["halt_start_et"].notna().sum()),
                "resume_trade_nonnull_rows": int(sub["resume_trade_et"].notna().sum()),
                "release_no_nonnull_rows": int(sub["release_no"].notna().sum()),
                "item_link_nonnull_rows": int(sub["item_link"].notna().sum()),
                "issuer_name_nonnull_rows": int(sub["issuer_name"].notna().sum()),
                "unique_tickers": int(sub["ticker"].dropna().nunique()),
                "unique_event_key_exact": int(sub["event_key_exact"].nunique()),
                "unique_event_key_semantic": int(sub["event_key_semantic"].nunique()),
            }
        )
    return pd.DataFrame(rows).sort_values("source").reset_index(drop=True)


def _field_completeness_summary(df: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "ticker",
        "issuer_name",
        "listing_exchange",
        "halt_date",
        "halt_start_et",
        "resume_quote_et",
        "resume_trade_et",
        "halt_code",
        "halt_type",
        "release_no",
        "item_link",
        "url_source",
    ]
    rows = []
    for source, sub in df.groupby("source", dropna=False):
        total = max(len(sub), 1)
        for field in fields:
            nonnull = int(sub[field].notna().sum())
            rows.append(
                {
                    "source": source,
                    "field": field,
                    "nonnull_rows": nonnull,
                    "null_rows": int(len(sub) - nonnull),
                    "nonnull_pct": round(100.0 * nonnull / total, 4),
                }
            )
    return pd.DataFrame(rows)


def _canonical_event_summary(df: pd.DataFrame) -> pd.DataFrame:
    group = df.groupby("event_id_canonical", dropna=False)
    out = group.agg(
        rows=("source", "size"),
        source_count=("source", "nunique"),
        sources=("source", lambda x: ",".join(sorted(pd.Series(x).dropna().astype(str).unique()))),
        ticker=("ticker", "first"),
        issuer_name=("issuer_name", "first"),
        halt_date=("halt_date", "first"),
        halt_start_et=("halt_start_et", "first"),
        resume_trade_et=("resume_trade_et", "first"),
        halt_code=("halt_code", "first"),
        halt_type=("halt_type", "first"),
        release_no=("release_no", "first"),
        is_sec_suspension=("is_sec_suspension", "max"),
    ).reset_index()
    out["has_cross_source_overlap"] = out["source_count"] > 1
    return out.sort_values(["source_count", "rows", "halt_date"], ascending=[False, False, True]).reset_index(drop=True)


def _duplicate_analysis(df: pd.DataFrame) -> pd.DataFrame:
    exact_counts = df.groupby("event_key_exact", dropna=False).size().rename("rows_exact").reset_index()
    semantic_counts = df.groupby("event_key_semantic", dropna=False).size().rename("rows_semantic").reset_index()
    exact_sources = (
        df.groupby("event_key_exact", dropna=False)["source"]
        .agg(lambda x: ",".join(sorted(pd.Series(x).dropna().astype(str).unique())))
        .rename("sources_exact")
        .reset_index()
    )
    semantic_sources = (
        df.groupby("event_key_semantic", dropna=False)["source"]
        .agg(lambda x: ",".join(sorted(pd.Series(x).dropna().astype(str).unique())))
        .rename("sources_semantic")
        .reset_index()
    )
    base = df[
        [
            "source",
            "ticker",
            "issuer_name",
            "halt_date",
            "halt_start_et",
            "halt_code",
            "halt_type",
            "release_no",
            "event_key_exact",
            "event_key_semantic",
        ]
    ].drop_duplicates()
    out = base.merge(exact_counts, on="event_key_exact", how="left")
    out = out.merge(semantic_counts, on="event_key_semantic", how="left")
    out = out.merge(exact_sources, on="event_key_exact", how="left")
    out = out.merge(semantic_sources, on="event_key_semantic", how="left")
    out["is_exact_duplicate"] = out["rows_exact"] > 1
    out["is_semantic_duplicate"] = out["rows_semantic"] > 1
    out["cross_source_semantic_overlap"] = out["sources_semantic"].fillna("").str.contains(",")
    return out.sort_values(["rows_semantic", "rows_exact"], ascending=[False, False]).reset_index(drop=True)


def _event_taxonomy_summary(events: pd.DataFrame) -> pd.DataFrame:
    out = events.copy()
    out["event_taxonomy"] = "good_date_level_event"
    out.loc[out["halt_start_et"].notna() & out["resume_trade_et"].notna(), "event_taxonomy"] = "good_full_intraday_event"
    out.loc[out["is_sec_suspension"].fillna(False), "event_taxonomy"] = "regulatory_context_only"
    out.loc[
        out["source_count"].gt(1)
        & out["halt_start_et"].notna()
        & out["resume_trade_et"].isna(),
        "event_taxonomy",
    ] = "review_missing_resume_time"
    out.loc[
        out["ticker"].isna()
        & out["is_sec_suspension"].fillna(False),
        "event_taxonomy",
    ] = "review_partial_identity"
    out.loc[
        out["halt_date"].isna()
        | (out["ticker"].isna() & out["issuer_name"].isna()),
        "event_taxonomy",
    ] = "bad_unusable_event"

    summary = (
        out.groupby("event_taxonomy", dropna=False)
        .agg(
            events=("event_id_canonical", "nunique"),
            source_rows=("rows", "sum"),
            tickers=("ticker", "nunique"),
        )
        .reset_index()
        .sort_values(["events", "source_rows"], ascending=[False, False])
        .reset_index(drop=True)
    )
    return summary


def _load_universe(universe_path: Path | None) -> pd.DataFrame | None:
    if universe_path is None or not universe_path.exists():
        return None
    if universe_path.suffix.lower() == ".parquet":
        df = pd.read_parquet(universe_path)
    else:
        df = pd.read_csv(universe_path)
    if "ticker" not in df.columns:
        return None
    out = df.copy()
    out["ticker"] = _normalize_text(out["ticker"])
    return out


def _default_lt1b_universe_path() -> Path:
    return Path(
        r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet"
    )


def _ticker_halt_coverage_summary(events: pd.DataFrame, universe_df: pd.DataFrame | None) -> pd.DataFrame:
    by_ticker = (
        events.loc[events["ticker"].notna()]
        .groupby("ticker", dropna=False)
        .agg(
            halt_events_count=("event_id_canonical", "nunique"),
            source_count=("sources", lambda x: max(len(str(v).split(",")) for v in x) if len(x) else 0),
            first_halt_date=("halt_date", "min"),
            last_halt_date=("halt_date", "max"),
            event_taxonomy_top=("event_taxonomy", lambda x: pd.Series(x).mode().iat[0] if not pd.Series(x).mode().empty else pd.NA),
        )
        .reset_index()
    )
    if universe_df is None:
        by_ticker["in_universe"] = True
        return by_ticker.sort_values(["halt_events_count", "ticker"], ascending=[False, True]).reset_index(drop=True)

    merged = universe_df[["ticker"]].drop_duplicates().merge(by_ticker, on="ticker", how="left")
    merged["has_halt_data"] = merged["halt_events_count"].notna()
    merged["halt_events_count"] = merged["halt_events_count"].fillna(0).astype(int)
    merged["in_universe"] = True
    return merged.sort_values(["has_halt_data", "halt_events_count", "ticker"], ascending=[False, False, True]).reset_index(drop=True)


def _ticker_year_halt_presence(events: pd.DataFrame) -> pd.DataFrame:
    out = events.loc[events["ticker"].notna() & events["halt_date"].notna(), ["ticker", "halt_date", "sources"]].copy()
    out["year"] = out["halt_date"].dt.year.astype("Int64")
    return (
        out.groupby(["ticker", "year"], dropna=False)
        .agg(
            halt_events_count=("ticker", "size"),
            first_halt_date=("halt_date", "min"),
            last_halt_date=("halt_date", "max"),
        )
        .reset_index()
        .sort_values(["ticker", "year"])
        .reset_index(drop=True)
    )


def _cross_source_overlap_summary(source_rows: pd.DataFrame) -> pd.DataFrame:
    out = source_rows.loc[source_rows["ticker"].notna() & source_rows["halt_date"].notna(), ["source", "ticker", "halt_date", "halt_start_et", "halt_code", "halt_type"]].copy()
    out["loose_key"] = out["ticker"].astype("string") + "|" + out["halt_date"].dt.strftime("%Y-%m-%d").fillna("<NA>")
    overlap = (
        out.groupby("loose_key", dropna=False)
        .agg(
            ticker=("ticker", "first"),
            halt_date=("halt_date", "first"),
            source_count=("source", "nunique"),
            sources=("source", lambda x: ",".join(sorted(pd.Series(x).astype(str).unique()))),
            rows=("source", "size"),
            halt_start_min=("halt_start_et", "min"),
            halt_start_max=("halt_start_et", "max"),
            halt_code_count=("halt_code", "nunique"),
            halt_type_count=("halt_type", "nunique"),
        )
        .reset_index()
    )
    overlap["has_cross_source_overlap"] = overlap["source_count"] > 1
    return overlap.sort_values(["has_cross_source_overlap", "rows", "ticker"], ascending=[False, False, True]).reset_index(drop=True)


def _multisource_builder_reconciliation(source_rows: pd.DataFrame, multisource_frame: pd.DataFrame | None) -> pd.DataFrame:
    subset = [
        "source",
        "ticker",
        "issuer_name",
        "halt_date",
        "halt_start_et",
        "resume_trade_et",
        "halt_code",
        "halt_type",
        "release_no",
        "item_link",
        "url_source",
    ]

    rows = []
    for source_name in ["nasdaq", "nyse", "sec"]:
        sub = source_rows.loc[source_rows["source"] == source_name].copy()
        pre = int(len(sub))
        post = int(len(sub.drop_duplicates(subset=subset, keep="last")))
        rows.append(
            {
                "scope": source_name,
                "rows_pre_concat": pre,
                "rows_post_builder_dedup": post,
                "dedup_delta": pre - post,
            }
        )

    total_pre = int(len(source_rows))
    total_post = int(len(source_rows.drop_duplicates(subset=subset, keep="last")))
    rows.append(
        {
            "scope": "all_sources_concat",
            "rows_pre_concat": total_pre,
            "rows_post_builder_dedup": total_post,
            "dedup_delta": total_pre - total_post,
        }
    )

    if multisource_frame is not None:
        rows.append(
            {
                "scope": "persisted_multisource_parquet",
                "rows_pre_concat": int(len(multisource_frame)),
                "rows_post_builder_dedup": int(len(multisource_frame)),
                "dedup_delta": 0,
            }
        )

    return pd.DataFrame(rows)


def _nasdaq_final_residual_rows(source_rows: pd.DataFrame) -> pd.DataFrame:
    residual = source_rows.loc[(source_rows["source"] == "nasdaq") & source_rows["halt_date"].isna()].copy()
    cols = [
        "ticker",
        "issuer_name",
        "halt_date",
        "halt_start_et",
        "resume_trade_et",
        "halt_code",
        "halt_type",
        "url_source",
        "raw_description_text",
    ]
    for col in cols:
        if col not in residual.columns:
            residual[col] = pd.NA
    residual["residual_reason"] = "raw_missing_payload"
    return residual[["residual_reason", *cols]].reset_index(drop=True)


def _build_halt_event_windows(canonical_events: pd.DataFrame) -> pd.DataFrame:
    base = canonical_events.copy()
    base = base.loc[base["ticker"].notna() & base["halt_date"].notna()].copy()
    if base.empty:
        return pd.DataFrame()

    base["halt_date"] = pd.to_datetime(base["halt_date"], errors="coerce").dt.normalize()
    base["resume_trade_date"] = pd.to_datetime(base["resume_trade_et"], errors="coerce").dt.normalize()
    base["resume_same_day"] = base["resume_trade_date"].eq(base["halt_date"])
    base["halt_session_bucket"] = _derive_session_bucket(pd.to_datetime(base["halt_start_et"], errors="coerce"))
    base["resume_session_bucket"] = _derive_session_bucket(pd.to_datetime(base["resume_trade_et"], errors="coerce"))

    window_frames: list[pd.DataFrame] = []

    def _append_window(role: str, date_series: pd.Series, session_col: str) -> None:
        sub = base.copy()
        sub["window_role"] = role
        sub["window_date"] = pd.to_datetime(date_series, errors="coerce").dt.normalize()
        sub["window_session_bucket"] = sub[session_col]
        sub = sub.loc[sub["window_date"].notna()].copy()
        window_frames.append(sub)

    _append_window("pre_halt_day", base["halt_date"] - pd.Timedelta(days=1), "halt_session_bucket")
    _append_window("halt_day", base["halt_date"], "halt_session_bucket")
    _append_window("resume_day", base["resume_trade_date"], "resume_session_bucket")
    _append_window("post_resume_day", base["resume_trade_date"] + pd.Timedelta(days=1), "resume_session_bucket")

    windows = pd.concat(window_frames, ignore_index=True, sort=False)
    windows["pair_key"] = windows["ticker"].astype("string") + "|" + windows["window_date"].dt.strftime("%Y-%m-%d")
    windows["window_offset_days"] = (
        (windows["window_date"] - windows["halt_date"]).dt.days.astype("Int64")
    )
    windows["has_intraday_anchor"] = windows["halt_start_et"].notna() | windows["resume_trade_et"].notna()
    keep_cols = [
        "event_id_canonical",
        "ticker",
        "issuer_name",
        "sources",
        "source_count",
        "event_taxonomy",
        "is_sec_suspension",
        "has_cross_source_overlap",
        "halt_date",
        "halt_start_et",
        "resume_trade_et",
        "resume_trade_date",
        "resume_same_day",
        "halt_session_bucket",
        "resume_session_bucket",
        "window_role",
        "window_date",
        "window_session_bucket",
        "window_offset_days",
        "has_intraday_anchor",
        "pair_key",
    ]
    for col in keep_cols:
        if col not in windows.columns:
            windows[col] = pd.NA
    return windows.loc[:, keep_cols].sort_values(["ticker", "window_date", "window_role"]).reset_index(drop=True)


def _build_quotes_link_candidates(event_windows: pd.DataFrame, quotes_current_path: Path, quotes_case_index_path: Path | None = None) -> pd.DataFrame:
    if event_windows.empty or not quotes_current_path.exists():
        return pd.DataFrame()

    pair_keys = set(event_windows["pair_key"].dropna().astype(str).tolist())
    ticker_set = set(event_windows["ticker"].dropna().astype(str).tolist())
    matched_parts: list[pd.DataFrame] = []
    columns = ["file", "ticker", "date", "rows", "severity", "root", "metrics_json"]

    for df in _iter_parquet_batches(quotes_current_path, columns=columns, batch_size=200_000):
        df["ticker"] = df["ticker"].astype("string").str.strip().str.upper()
        df = df.loc[df["ticker"].isin(ticker_set)].copy()
        if df.empty:
            continue
        df["pair_key"] = df["ticker"].astype("string") + "|" + df["date"].dt.strftime("%Y-%m-%d")
        df = df.loc[df["pair_key"].isin(pair_keys)].copy()
        if df.empty:
            continue

        metrics = df["metrics_json"].map(_parse_metrics_json)
        out = pd.DataFrame(
            {
                "pair_key": df["pair_key"],
                "quotes_file": df["file"].astype("string"),
                "quotes_root": df["root"].astype("string"),
                "quotes_rows": pd.to_numeric(df["rows"], errors="coerce"),
                "quotes_severity": df["severity"].astype("string"),
                "quotes_crossed_ratio_pct": pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce"),
                "quotes_crossed_rows": pd.to_numeric(metrics.map(lambda x: x.get("crossed_rows")), errors="coerce"),
                "quotes_ask_integer_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_integer_pct")), errors="coerce"),
                "quotes_ask_eq_round_bid_pct": pd.to_numeric(metrics.map(lambda x: x.get("ask_eq_round_bid_pct")), errors="coerce"),
                "quotes_timestamp_out_of_partition_day": metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False))),
            }
        )
        matched_parts.append(out)

    if not matched_parts:
        return pd.DataFrame()

    quotes_matches = pd.concat(matched_parts, ignore_index=True, sort=False)
    quotes_matches["quotes_taxonomy"] = _classify_quotes_taxonomy_simple(quotes_matches)
    quotes_matches["quotes_problem_flag"] = quotes_matches["quotes_severity"].isin(["HARD_FAIL", "SOFT_FAIL"])
    quotes_matches["quotes_cross_positive_flag"] = pd.to_numeric(quotes_matches["quotes_crossed_rows"], errors="coerce").fillna(0).gt(0)

    out = event_windows.merge(quotes_matches, on="pair_key", how="left")
    out["quotes_linked"] = out["quotes_file"].notna()

    if quotes_case_index_path is not None and quotes_case_index_path.exists():
        case_df = pd.read_parquet(quotes_case_index_path)
        case_df["ticker"] = case_df["ticker"].astype("string").str.strip().str.upper()
        case_df["date"] = pd.to_datetime(case_df["date"], errors="coerce").dt.normalize()
        case_df["pair_key"] = case_df["ticker"].astype("string") + "|" + case_df["date"].dt.strftime("%Y-%m-%d")
        case_agg = (
            case_df.groupby("pair_key", dropna=False)
            .agg(
                quotes_case_index_hits=("pair_key", "size"),
                quotes_case_index_blocks=("block", lambda x: ",".join(sorted(pd.Series(x).dropna().astype(str).unique()))),
                quotes_case_index_taxonomies=("taxonomy", lambda x: ",".join(sorted(pd.Series(x).dropna().astype(str).unique()))),
            )
            .reset_index()
        )
        out = out.merge(case_agg, on="pair_key", how="left")
    return out


def _build_trades_link_candidates(event_windows: pd.DataFrame, trades_current_path: Path, trades_case_index_path: Path | None = None) -> pd.DataFrame:
    if event_windows.empty or not trades_current_path.exists():
        return pd.DataFrame()

    pair_keys = set(event_windows["pair_key"].dropna().astype(str).tolist())
    ticker_set = set(event_windows["ticker"].dropna().astype(str).tolist())
    matched_parts: list[pd.DataFrame] = []
    columns = ["file", "ticker", "date", "rows", "severity", "root", "issues", "warns", "metrics_json"]

    for df in _iter_parquet_batches(trades_current_path, columns=columns, batch_size=200_000):
        df["ticker"] = df["ticker"].astype("string").str.strip().str.upper()
        df = df.loc[df["ticker"].isin(ticker_set)].copy()
        if df.empty:
            continue
        df["pair_key"] = df["ticker"].astype("string") + "|" + df["date"].dt.strftime("%Y-%m-%d")
        df = df.loc[df["pair_key"].isin(pair_keys)].copy()
        if df.empty:
            continue

        metrics = df["metrics_json"].map(_parse_metrics_json)
        issues = df["issues"].map(_parse_listish)
        warns = df["warns"].map(_parse_listish)
        out = pd.DataFrame(
            {
                "pair_key": df["pair_key"],
                "trades_file": df["file"].astype("string"),
                "trades_root": df["root"].astype("string"),
                "trades_rows": pd.to_numeric(df["rows"], errors="coerce"),
                "trades_severity": df["severity"].astype("string"),
                "trades_issue_count": issues.map(len).astype("Int64"),
                "trades_warn_count": warns.map(len).astype("Int64"),
                "trades_issue_tokens": issues.map(lambda xs: ",".join(xs)),
                "trades_warn_tokens": warns.map(lambda xs: ",".join(xs)),
                "trades_duplicate_excess_ratio_pct": pd.to_numeric(metrics.map(lambda x: x.get("duplicate_excess_ratio_pct")), errors="coerce"),
                "trades_max_trades_same_timestamp": pd.to_numeric(metrics.map(lambda x: x.get("max_trades_same_timestamp")), errors="coerce"),
            }
        )
        matched_parts.append(out)

    if not matched_parts:
        return pd.DataFrame()

    trades_matches = pd.concat(matched_parts, ignore_index=True, sort=False)
    trades_matches["trades_problem_flag"] = trades_matches["trades_severity"].isin(["HARD_FAIL", "SOFT_FAIL"])
    trades_matches["trades_focus_issue"] = np.where(
        trades_matches["trades_issue_tokens"].astype("string").str.contains("trade_price_outside_daily_range", na=False),
        "trade_price_outside_daily_range",
        np.where(
            trades_matches["trades_warn_tokens"].astype("string").str.contains("trade_price_outside_1m_range", na=False),
            "trade_price_outside_1m_range",
            "other_or_clean",
        ),
    )

    out = event_windows.merge(trades_matches, on="pair_key", how="left")
    out["trades_linked"] = out["trades_file"].notna()

    if trades_case_index_path is not None and trades_case_index_path.exists():
        case_df = pd.read_parquet(trades_case_index_path)
        case_df["ticker"] = case_df["ticker"].astype("string").str.strip().str.upper()
        case_df["date"] = pd.to_datetime(case_df["date"], errors="coerce").dt.normalize()
        case_df["pair_key"] = case_df["ticker"].astype("string") + "|" + case_df["date"].dt.strftime("%Y-%m-%d")
        case_agg = (
            case_df.groupby("pair_key", dropna=False)
            .agg(
                trades_case_index_hits=("pair_key", "size"),
                trades_case_index_blocks=("block", lambda x: ",".join(sorted(pd.Series(x).dropna().astype(str).unique()))),
                trades_case_index_final_buckets=("final_bucket", lambda x: ",".join(sorted(pd.Series(x).dropna().astype(str).unique()))),
            )
            .reset_index()
        )
        out = out.merge(case_agg, on="pair_key", how="left")
    return out


def _build_event_window_alignment_summary(
    event_windows: pd.DataFrame,
    quotes_links: pd.DataFrame,
    trades_links: pd.DataFrame,
) -> pd.DataFrame:
    if event_windows.empty:
        return pd.DataFrame()

    base = event_windows.copy()

    if quotes_links is not None and not quotes_links.empty:
        q = (
            quotes_links.groupby(["event_id_canonical", "window_role", "window_date"], dropna=False)
            .agg(
                quotes_linked=("quotes_linked", "max"),
                quotes_problem_flag=("quotes_problem_flag", "max"),
                quotes_hard_fail=("quotes_severity", lambda x: pd.Series(x).astype(str).eq("HARD_FAIL").any()),
                quotes_soft_fail=("quotes_severity", lambda x: pd.Series(x).astype(str).eq("SOFT_FAIL").any()),
                quotes_case_index_hits=("quotes_case_index_hits", "max"),
            )
            .reset_index()
        )
        base = base.merge(q, on=["event_id_canonical", "window_role", "window_date"], how="left")

    if trades_links is not None and not trades_links.empty:
        t = (
            trades_links.groupby(["event_id_canonical", "window_role", "window_date"], dropna=False)
            .agg(
                trades_linked=("trades_linked", "max"),
                trades_problem_flag=("trades_problem_flag", "max"),
                trades_hard_fail=("trades_severity", lambda x: pd.Series(x).astype(str).eq("HARD_FAIL").any()),
                trades_soft_fail=("trades_severity", lambda x: pd.Series(x).astype(str).eq("SOFT_FAIL").any()),
                trades_case_index_hits=("trades_case_index_hits", "max"),
            )
            .reset_index()
        )
        base = base.merge(t, on=["event_id_canonical", "window_role", "window_date"], how="left")

    for col in [
        "quotes_linked",
        "quotes_problem_flag",
        "quotes_hard_fail",
        "quotes_soft_fail",
        "trades_linked",
        "trades_problem_flag",
        "trades_hard_fail",
        "trades_soft_fail",
    ]:
        if col in base.columns:
            base[col] = base[col].fillna(False).astype(bool)

    base["alignment_bucket"] = np.select(
        [
            base["quotes_problem_flag"] & base["trades_problem_flag"],
            base["quotes_problem_flag"] & ~base["trades_problem_flag"],
            ~base["quotes_problem_flag"] & base["trades_problem_flag"],
            base["quotes_linked"] & base["trades_linked"],
            base["quotes_linked"] & ~base["trades_linked"],
            ~base["quotes_linked"] & base["trades_linked"],
        ],
        [
            "quotes_and_trades_problem",
            "quotes_problem_only",
            "trades_problem_only",
            "both_linked_clean_or_pass",
            "quotes_only_no_trades_link",
            "trades_only_no_quotes_link",
        ],
        default="no_quotes_no_trades_link",
    )

    summary = (
        base.groupby(
            ["window_role", "window_session_bucket", "alignment_bucket", "event_taxonomy"],
            dropna=False,
        )
        .agg(
            event_windows=("event_id_canonical", "size"),
            events=("event_id_canonical", "nunique"),
            tickers=("ticker", "nunique"),
            quotes_linked=("quotes_linked", "sum"),
            trades_linked=("trades_linked", "sum"),
            quotes_problem=("quotes_problem_flag", "sum"),
            trades_problem=("trades_problem_flag", "sum"),
            quotes_hard_fail=("quotes_hard_fail", "sum"),
            trades_hard_fail=("trades_hard_fail", "sum"),
        )
        .reset_index()
        .sort_values(["window_role", "alignment_bucket", "event_windows"], ascending=[True, True, False])
        .reset_index(drop=True)
    )
    return summary


def _derive_visual_date(row: pd.Series) -> pd.Timestamp | pd.NaT:
    halt_date = pd.to_datetime(row.get("halt_date"), errors="coerce")
    resume_trade_et = pd.to_datetime(row.get("resume_trade_et"), errors="coerce")
    resume_trade_date = pd.to_datetime(row.get("resume_trade_date"), errors="coerce")
    if pd.notna(halt_date):
        return halt_date.normalize()
    if pd.notna(resume_trade_date):
        return resume_trade_date.normalize()
    if pd.notna(resume_trade_et):
        return resume_trade_et.normalize()
    return pd.NaT


def _build_halts_lt1b_event_index(canonical_events: pd.DataFrame, universe_df: pd.DataFrame | None) -> pd.DataFrame:
    events = canonical_events.copy()
    events = events.loc[events["ticker"].notna()].copy()
    events["ticker"] = _normalize_text(events["ticker"])
    if universe_df is None or universe_df.empty:
        events["in_lt1b_universe"] = True
        return events.reset_index(drop=True)

    uni = universe_df.copy()
    uni["ticker"] = _normalize_text(uni["ticker"])
    keep_cols = [c for c in ["ticker", "first_seen_date", "last_observed_date", "classification_1b", "classification_reason_1b"] if c in uni.columns]
    uni = uni.loc[:, keep_cols].drop_duplicates(subset=["ticker"])
    uni["first_seen_date"] = pd.to_datetime(uni.get("first_seen_date"), errors="coerce")
    uni["last_observed_date"] = pd.to_datetime(uni.get("last_observed_date"), errors="coerce")
    out = events.merge(uni, on="ticker", how="left")
    out["in_lt1b_universe"] = out["classification_1b"].notna()
    out = out.loc[out["in_lt1b_universe"]].copy()
    return out.reset_index(drop=True)


def _classify_visual_case_bucket(df: pd.DataFrame) -> pd.Series:
    quotes_linked = df.get("quotes_linked", pd.Series(False, index=df.index)).fillna(False).astype(bool)
    trades_linked = df.get("trades_linked", pd.Series(False, index=df.index)).fillna(False).astype(bool)
    quotes_problem = df.get("quotes_problem_flag", pd.Series(False, index=df.index)).fillna(False).astype(bool)
    trades_problem = df.get("trades_problem_flag", pd.Series(False, index=df.index)).fillna(False).astype(bool)
    has_anchor = df.get("has_intraday_anchor", pd.Series(False, index=df.index)).fillna(False).astype(bool)
    halt_start_et = pd.to_datetime(df.get("halt_start_et"), errors="coerce")
    resume_trade_et = pd.to_datetime(df.get("resume_trade_et"), errors="coerce")
    alignment_review = has_anchor & ((halt_start_et.isna()) | (resume_trade_et.isna() & df.get("event_taxonomy", pd.Series("", index=df.index)).astype(str).eq("good_full_intraday_event")))

    conditions = [
        alignment_review,
        quotes_problem & trades_problem,
        quotes_problem & ~trades_problem,
        ~quotes_problem & trades_problem,
        (quotes_linked | trades_linked) & ~quotes_problem & ~trades_problem,
        (~quotes_linked & ~trades_linked) & has_anchor,
    ]
    choices = [
        "review_timestamp_alignment",
        "confirmed_halt_microstructure_coherent",
        "halt_with_quotes_signal_only",
        "halt_with_trades_signal_only",
        "halt_present_but_market_clean",
        "market_signal_without_clear_halt_window",
    ]
    return pd.Series(np.select(conditions, choices, default="market_signal_without_clear_halt_window"), index=df.index, dtype="string")


def _build_intraday_overlay_index(
    lt1b_event_index: pd.DataFrame,
    quotes_links: pd.DataFrame,
    trades_links: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if lt1b_event_index.empty:
        return pd.DataFrame(), pd.DataFrame()

    base = lt1b_event_index.copy()
    base["visual_date"] = base.apply(_derive_visual_date, axis=1)
    base["visual_date"] = pd.to_datetime(base["visual_date"], errors="coerce").dt.normalize()
    base["resume_trade_date"] = pd.to_datetime(base.get("resume_trade_et"), errors="coerce").dt.normalize()
    q = pd.DataFrame()
    if quotes_links is not None and not quotes_links.empty:
        q = (
            quotes_links.loc[quotes_links["window_role"].isin(["halt_day", "resume_day"])]
            .groupby("event_id_canonical", dropna=False)
            .agg(
                quotes_linked=("quotes_linked", "max"),
                quotes_problem_flag=("quotes_problem_flag", "max"),
                quotes_file_visual=("quotes_file", lambda x: pd.Series(x).dropna().astype(str).iloc[0] if pd.Series(x).dropna().shape[0] else pd.NA),
                quotes_severity=("quotes_severity", lambda x: pd.Series(x).dropna().astype(str).iloc[0] if pd.Series(x).dropna().shape[0] else pd.NA),
                quotes_taxonomy=("quotes_taxonomy", lambda x: pd.Series(x).dropna().astype(str).iloc[0] if pd.Series(x).dropna().shape[0] else pd.NA),
                quotes_case_index_hits=("quotes_case_index_hits", "max"),
                quotes_crossed_ratio_pct=("quotes_crossed_ratio_pct", "max"),
            )
            .reset_index()
        )
        base = base.merge(q, on="event_id_canonical", how="left")

    t = pd.DataFrame()
    if trades_links is not None and not trades_links.empty:
        t = (
            trades_links.loc[trades_links["window_role"].isin(["halt_day", "resume_day"])]
            .groupby("event_id_canonical", dropna=False)
            .agg(
                trades_linked=("trades_linked", "max"),
                trades_problem_flag=("trades_problem_flag", "max"),
                trades_file_visual=("trades_file", lambda x: pd.Series(x).dropna().astype(str).iloc[0] if pd.Series(x).dropna().shape[0] else pd.NA),
                trades_severity=("trades_severity", lambda x: pd.Series(x).dropna().astype(str).iloc[0] if pd.Series(x).dropna().shape[0] else pd.NA),
                trades_focus_issue=("trades_focus_issue", lambda x: pd.Series(x).dropna().astype(str).iloc[0] if pd.Series(x).dropna().shape[0] else pd.NA),
                trades_case_index_hits=("trades_case_index_hits", "max"),
            )
            .reset_index()
        )
        base = base.merge(t, on="event_id_canonical", how="left")

    for col in ["quotes_linked", "quotes_problem_flag", "trades_linked", "trades_problem_flag"]:
        if col not in base.columns:
            base[col] = False
        base[col] = base[col].fillna(False).astype(bool)

    base["has_intraday_quotes"] = base["quotes_file_visual"].notna()
    base["has_intraday_trades"] = base["trades_file_visual"].notna()
    base["visual_case_bucket"] = _classify_visual_case_bucket(base)
    base["quotes_link_strength"] = np.select(
        [base["quotes_problem_flag"], base["quotes_linked"]],
        ["problem", "linked_clean"],
        default="not_linked",
    )
    base["trades_link_strength"] = np.select(
        [base["trades_problem_flag"], base["trades_linked"]],
        ["problem", "linked_clean"],
        default="not_linked",
    )
    base["display_label"] = (
        base["ticker"].astype(str)
        + " | "
        + base["visual_date"].dt.strftime("%Y-%m-%d").fillna("NA")
        + " | "
        + base["visual_case_bucket"].astype(str)
    )
    base["rank_score"] = (
        pd.to_numeric(base.get("quotes_case_index_hits"), errors="coerce").fillna(0) * 10
        + pd.to_numeric(base.get("trades_case_index_hits"), errors="coerce").fillna(0) * 10
        + base["quotes_problem_flag"].astype(int) * 5
        + base["trades_problem_flag"].astype(int) * 5
        + base["has_intraday_quotes"].astype(int)
        + base["has_intraday_trades"].astype(int)
    )
    base["quotes_file_visual"] = base.get("quotes_file_visual", pd.Series(pd.NA, index=base.index)).astype("string")
    base["trades_file_visual"] = base.get("trades_file_visual", pd.Series(pd.NA, index=base.index)).astype("string")
    base["visual_key"] = (
        base["ticker"].astype("string")
        + "|"
        + base["visual_date"].dt.strftime("%Y-%m-%d").fillna("NA")
        + "|"
        + base["quotes_file_visual"].fillna("NA")
        + "|"
        + base["trades_file_visual"].fillna("NA")
    )

    overlay_index = (
        base.groupby("visual_key", dropna=False)
        .agg(
            event_id_canonical=("event_id_canonical", lambda x: pd.Series(x).astype(str).iloc[0]),
            event_ids_in_visual=("event_id_canonical", lambda x: "|".join(pd.Series(x).dropna().astype(str).unique())),
            events_in_visual=("event_id_canonical", "nunique"),
            ticker=("ticker", "first"),
            display_label=("display_label", "first"),
            visual_date=("visual_date", "first"),
            halt_date=("halt_date", "first"),
            halt_start_et=("halt_start_et", "min"),
            resume_trade_et=("resume_trade_et", "max"),
            resume_trade_date=("resume_trade_date", "first"),
            event_taxonomy=("event_taxonomy", lambda x: pd.Series(x).astype(str).iloc[0]),
            visual_case_bucket=("visual_case_bucket", lambda x: pd.Series(x).astype(str).mode().iloc[0] if not pd.Series(x).mode().empty else pd.Series(x).astype(str).iloc[0]),
            quotes_file_visual=("quotes_file_visual", "first"),
            trades_file_visual=("trades_file_visual", "first"),
            has_intraday_quotes=("has_intraday_quotes", "max"),
            has_intraday_trades=("has_intraday_trades", "max"),
            quotes_link_strength=("quotes_link_strength", lambda x: "problem" if pd.Series(x).astype(str).eq("problem").any() else ("linked_clean" if pd.Series(x).astype(str).eq("linked_clean").any() else "not_linked")),
            trades_link_strength=("trades_link_strength", lambda x: "problem" if pd.Series(x).astype(str).eq("problem").any() else ("linked_clean" if pd.Series(x).astype(str).eq("linked_clean").any() else "not_linked")),
            quotes_problem_flag=("quotes_problem_flag", "max"),
            trades_problem_flag=("trades_problem_flag", "max"),
            quotes_case_index_hits=("quotes_case_index_hits", "max"),
            trades_case_index_hits=("trades_case_index_hits", "max"),
            rank_score=("rank_score", "max"),
            halt_markers_count=("halt_start_et", lambda x: pd.to_datetime(x, errors="coerce").notna().sum()),
            resume_markers_count=("resume_trade_et", lambda x: pd.to_datetime(x, errors="coerce").notna().sum()),
            halt_markers_et=("halt_start_et", lambda x: "|".join(pd.to_datetime(x, errors="coerce").dropna().dt.strftime("%Y-%m-%d %H:%M:%S").unique())),
            resume_markers_et=("resume_trade_et", lambda x: "|".join(pd.to_datetime(x, errors="coerce").dropna().dt.strftime("%Y-%m-%d %H:%M:%S").unique())),
        )
        .reset_index()
        .sort_values(["rank_score", "events_in_visual", "ticker"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    keep_cols = [
        "event_id_canonical",
        "event_ids_in_visual",
        "events_in_visual",
        "visual_key",
        "ticker",
        "display_label",
        "visual_date",
        "halt_date",
        "halt_start_et",
        "resume_trade_et",
        "resume_trade_date",
        "event_taxonomy",
        "visual_case_bucket",
        "quotes_file_visual",
        "trades_file_visual",
        "has_intraday_quotes",
        "has_intraday_trades",
        "quotes_link_strength",
        "trades_link_strength",
        "quotes_problem_flag",
        "trades_problem_flag",
        "quotes_case_index_hits",
        "trades_case_index_hits",
        "halt_markers_count",
        "resume_markers_count",
        "halt_markers_et",
        "resume_markers_et",
        "rank_score",
    ]
    visual_cases = overlay_index.loc[:, [c for c in keep_cols if c in overlay_index.columns]].copy()
    return overlay_index, visual_cases


def _write_df(df: pd.DataFrame, path: Path) -> None:
    df.to_parquet(path, index=False)


def build_artifacts(paths: HaltAuditPaths) -> dict:
    processed = paths.processed_root
    source_specs = [
        ("nasdaq", processed / "halts_master_nasdaq_for_run_dates.parquet", True),
        ("nyse", processed / "halts_master_nyse_1y.parquet", True),
        ("sec", processed / "halts_master_sec.parquet", True),
        ("multisource", processed / "halts_master_multisource.parquet", False),
    ]

    source_frames: list[pd.DataFrame] = []
    multisource_frame: pd.DataFrame | None = None
    build_warnings: list[str] = []
    for source_name, path, include_in_base in source_specs:
        if not path.exists():
            build_warnings.append(f"missing_input:{path}")
            continue
        normalized = _normalize_source_frame(pd.read_parquet(path), source_name)
        if include_in_base:
            source_frames.append(normalized)
        else:
            multisource_frame = normalized

    if not source_frames:
        raise RuntimeError("No halts parquet inputs found")

    source_rows = pd.concat(source_frames, ignore_index=True, sort=False)
    source_rows = _build_canonical_keys(source_rows)

    if multisource_frame is not None:
        multisource_frame = _build_canonical_keys(multisource_frame)
        if len(multisource_frame) != len(source_rows):
            build_warnings.append(
                f"multisource_row_mismatch:source_sum={len(source_rows)} multisource_rows={len(multisource_frame)}"
            )

    canonical_events = _canonical_event_summary(source_rows).copy()
    canonical_events = canonical_events.assign(
        event_taxonomy=lambda df: pd.Series([""] * len(df), index=df.index, dtype="string")
    )
    canonical_events["event_taxonomy"] = "good_date_level_event"
    canonical_events.loc[
        canonical_events["halt_start_et"].notna() & canonical_events["resume_trade_et"].notna(),
        "event_taxonomy",
    ] = "good_full_intraday_event"
    canonical_events.loc[canonical_events["is_sec_suspension"].fillna(False), "event_taxonomy"] = "regulatory_context_only"
    canonical_events.loc[
        canonical_events["source_count"].gt(1)
        & canonical_events["halt_start_et"].notna()
        & canonical_events["resume_trade_et"].isna(),
        "event_taxonomy",
    ] = "review_missing_resume_time"
    canonical_events.loc[
        canonical_events["ticker"].isna()
        & canonical_events["is_sec_suspension"].fillna(False),
        "event_taxonomy",
    ] = "review_partial_identity"
    canonical_events.loc[
        canonical_events["halt_date"].isna()
        | (canonical_events["ticker"].isna() & canonical_events["issuer_name"].isna()),
        "event_taxonomy",
    ] = "bad_unusable_event"

    universe_df = _load_universe(paths.universe_path)

    quotes_current_path = Path(
        r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet"
    )
    trades_current_path = Path(
        r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet"
    )
    quotes_case_index_path = Path(
        r"C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache_v2\case_index_top50_cd_lt1b.parquet"
    )
    trades_case_index_path = Path(
        r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\notebook_cd_cache\case_index_cd.parquet"
    )

    halt_event_windows = _build_halt_event_windows(canonical_events)
    halts_quotes_link_candidates = _build_quotes_link_candidates(
        halt_event_windows,
        quotes_current_path=quotes_current_path,
        quotes_case_index_path=quotes_case_index_path,
    )
    halts_trades_link_candidates = _build_trades_link_candidates(
        halt_event_windows,
        trades_current_path=trades_current_path,
        trades_case_index_path=trades_case_index_path,
    )
    event_window_alignment_summary = _build_event_window_alignment_summary(
        halt_event_windows,
        halts_quotes_link_candidates,
        halts_trades_link_candidates,
    )
    halts_lt1b_event_index = _build_halts_lt1b_event_index(canonical_events, universe_df)
    halts_intraday_overlay_index, halts_quotes_trades_visual_cases = _build_intraday_overlay_index(
        halts_lt1b_event_index,
        halts_quotes_link_candidates,
        halts_trades_link_candidates,
    )

    artifacts = {
        "source_quality_summary": _source_quality_summary(source_rows),
        "field_completeness_summary": _field_completeness_summary(source_rows),
        "canonical_event_summary": canonical_events,
        "duplicate_analysis": _duplicate_analysis(source_rows),
        "cross_source_overlap_summary": _cross_source_overlap_summary(source_rows),
        "multisource_builder_reconciliation": _multisource_builder_reconciliation(source_rows, multisource_frame),
        "nasdaq_final_residual_rows": _nasdaq_final_residual_rows(source_rows),
        "ticker_halt_coverage_summary": _ticker_halt_coverage_summary(canonical_events, universe_df),
        "ticker_year_halt_presence": _ticker_year_halt_presence(canonical_events),
        "event_taxonomy_summary": _event_taxonomy_summary(canonical_events),
        "halt_event_windows": halt_event_windows,
        "halts_lt1b_event_index": halts_lt1b_event_index,
        "halts_intraday_overlay_index": halts_intraday_overlay_index,
        "halts_quotes_trades_visual_cases": halts_quotes_trades_visual_cases,
        "halts_quotes_link_candidates": halts_quotes_link_candidates,
        "halts_trades_link_candidates": halts_trades_link_candidates,
        "event_window_alignment_summary": event_window_alignment_summary,
    }

    for name, df in artifacts.items():
        _write_df(df, paths.output_root / f"{name}.parquet")

    return {
        "row_counts": {name: int(len(df)) for name, df in artifacts.items()},
        "input_rows": int(len(source_rows)),
        "warnings": build_warnings,
    }


def main() -> None:
    args = parse_args()
    universe_path = Path(args.universe_path) if args.universe_path else _default_lt1b_universe_path()
    paths = HaltAuditPaths(
        halts_root=Path(args.halts_root),
        output_root=Path(args.output_root),
        universe_path=universe_path,
    )
    ensure_output_root(paths.output_root)

    manifest = build_manifest(paths)
    started = time.time()
    build_info = build_artifacts(paths)
    finished = time.time()

    manifest["row_counts"] = build_info["row_counts"]
    manifest["input_rows"] = build_info["input_rows"]
    manifest["warnings"] = build_info["warnings"]

    manifest_path = paths.output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    build_log_path = paths.output_root / "build_log.json"
    build_log_path.write_text(
        json.dumps(
            {
                "started_at_epoch": started,
                "finished_at_epoch": finished,
                "duration_sec": round(finished - started, 3),
                "warnings": build_info["warnings"],
                "row_counts": build_info["row_counts"],
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("Halts audit scaffold ready")
    print("output_root:", paths.output_root)
    print("manifest:", manifest_path)
    print("build_log:", build_log_path)


if __name__ == "__main__":
    main()
