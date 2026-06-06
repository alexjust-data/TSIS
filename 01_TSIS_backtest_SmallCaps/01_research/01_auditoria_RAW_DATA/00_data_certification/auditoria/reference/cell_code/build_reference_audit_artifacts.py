from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


PROJECT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps")
REFERENCE_ROOT = Path(r"D:\reference")
AUDIT_ROOT = PROJECT_ROOT / "notebooks" / "00_data_certification" / "auditoria" / "reference"
CACHE_ROOT = AUDIT_ROOT / "cache_v2"
LT1B_UNIVERSE_PATH = PROJECT_ROOT / "runs" / "backtest" / "market_cap_last_observed_cutoff" / "20260320_market_cap_last_observed_cutoff" / "market_cap_cutoff_lt_1b_active_inactive.parquet"
MARKET_UNIVERSE_PATH = PROJECT_ROOT / "data" / "reference" / "universe_pti" / "tickers_2005_2026_upper.parquet"

RUN_DIR = REFERENCE_ROOT / "_run"
AUDIT_CSV = RUN_DIR / "download_reference_universe_polygon.audit.csv"
ERRORS_CSV = RUN_DIR / "download_reference_universe_polygon.errors.csv"
PROGRESS_JSON = RUN_DIR / "download_reference_universe_polygon.progress.json"

OVERVIEW_DIR = REFERENCE_ROOT / "overview"
ALL_TICKERS_DIR = REFERENCE_ROOT / "all_tickers"
EVENTS_DIR = REFERENCE_ROOT / "events"
SPLITS_DIR = REFERENCE_ROOT / "splits"
DIVIDENDS_DIR = REFERENCE_ROOT / "dividends"
TICKER_TYPES_PATH = REFERENCE_ROOT / "ticker_types" / "ticker_types.parquet"
EXCHANGES_PATH = REFERENCE_ROOT / "exchanges" / "exchanges.parquet"
RAW_DAILY_ROOT = Path(r"D:\ohlcv_daily")
RAW_1M_ROOT = Path(r"D:\ohlcv_1m")
TRADES_FILE_ACCEPTANCE_EXAMPLES_PATH = PROJECT_ROOT / "runs" / "backtest" / "trades_v2_materialized" / "trades_current_cd_merged" / "root_cause_exports" / "file_acceptance_cache_lt1b" / "layer6_policy_examples.parquet"
TRADES_FINAL_BUCKET_PATH = PROJECT_ROOT / "runs" / "backtest" / "trades_v2_materialized" / "trades_current_cd_merged" / "root_cause_exports" / "trades_cd_root_cause_final_bucket.parquet"
QUOTES_CURRENT_CD_PATH = PROJECT_ROOT / "runs" / "backtest" / "quotes_v2_materialized" / "quotes_current_cd_merged" / "quotes_current.parquet"
HALTS_LT1B_EVENT_INDEX_PATH = PROJECT_ROOT / "notebooks" / "00_data_certification" / "auditoria" / "halts" / "cache_v2" / "halts_lt1b_event_index.parquet"

ENDPOINTS = [
    "overview",
    "all_tickers",
    "events",
    "splits",
    "dividends",
    "ticker_types",
    "exchanges",
]

TRANSIENT_PATTERN = re.compile(r"(?:\.|/|=)")
SUFFIX_VARIANT_PATTERN = re.compile(r"(?:W|WS|U|R)$")


@dataclass(frozen=True)
class BuildConfig:
    reference_root: Path
    cache_root: Path
    lt1b_universe_path: Path
    market_universe_path: Path
    sample_files_per_dataset: int


def utc_now_iso() -> str:
    return pd.Timestamp.utcnow().isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def safe_read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def normalize_ticker(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.upper()


def list_parquet_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(path.rglob("*.parquet"))


def dataset_file_inventory(cfg: BuildConfig) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    mapping = {
        "overview": OVERVIEW_DIR,
        "all_tickers": ALL_TICKERS_DIR,
        "events": EVENTS_DIR,
        "splits": SPLITS_DIR,
        "dividends": DIVIDENDS_DIR,
        "ticker_types": TICKER_TYPES_PATH.parent,
        "exchanges": EXCHANGES_PATH.parent,
    }
    for dataset, base_path in mapping.items():
        parquet_files = list_parquet_files(base_path)
        rows.append(
            {
                "dataset": dataset,
                "base_path": str(base_path),
                "exists": bool(base_path.exists()),
                "parquet_file_count": len(parquet_files),
                "dir_count": sum(1 for p in base_path.iterdir() if p.is_dir()) if base_path.exists() else 0,
                "file_count_all": sum(1 for p in base_path.rglob("*") if p.is_file()) if base_path.exists() else 0,
                "sample_file": str(parquet_files[0]) if parquet_files else pd.NA,
            }
        )
    return pd.DataFrame(rows).sort_values("dataset").reset_index(drop=True)


def build_download_summaries() -> tuple[pd.DataFrame, pd.DataFrame]:
    audit = safe_read_csv(AUDIT_CSV)
    errors = safe_read_csv(ERRORS_CSV)

    if audit.empty:
        return pd.DataFrame(), pd.DataFrame()

    for col in ["dataset", "ticker", "status", "msg", "out_file"]:
        if col in audit.columns:
            audit[col] = audit[col].astype("string")
    if "http_status" in audit.columns:
        audit["http_status"] = pd.to_numeric(audit["http_status"], errors="coerce")
    if "rows_saved" in audit.columns:
        audit["rows_saved"] = pd.to_numeric(audit["rows_saved"], errors="coerce")
    if "request_date" in audit.columns:
        audit["request_date"] = pd.to_datetime(audit["request_date"], errors="coerce")

    summary = (
        audit.groupby("dataset", dropna=False)
        .agg(
            audit_rows=("dataset", "size"),
            ok_rows=("status", lambda s: int((s == "ok").sum())),
            error_rows=("status", lambda s: int((s == "error").sum())),
            resume_skip_rows=("status", lambda s: int(pd.Series(s).astype("string").str.startswith("resume-skip", na=False).sum())),
            distinct_tickers=("ticker", lambda s: int(pd.Series(s).dropna().astype("string").nunique())),
            http_404_rows=("http_status", lambda s: int((pd.to_numeric(s, errors="coerce") == 404).sum())),
            nonzero_rows_saved=("rows_saved", lambda s: int((pd.to_numeric(s, errors="coerce").fillna(0) > 0).sum())),
        )
        .reset_index()
        .sort_values("dataset")
        .reset_index(drop=True)
    )
    summary["ok_pct"] = (100.0 * summary["ok_rows"] / summary["audit_rows"]).round(2)
    summary["error_pct"] = (100.0 * summary["error_rows"] / summary["audit_rows"]).round(2)
    summary["http_404_pct"] = (100.0 * summary["http_404_rows"] / summary["audit_rows"]).round(2)

    if errors.empty:
        error_summary = pd.DataFrame(columns=["dataset", "http_status", "error_count"])
    else:
        for col in ["dataset", "ticker", "msg"]:
            if col in errors.columns:
                errors[col] = errors[col].astype("string")
        if "http_status" in errors.columns:
            errors["http_status"] = pd.to_numeric(errors["http_status"], errors="coerce")
        error_summary = (
            errors.groupby(["dataset", "http_status"], dropna=False)
            .size()
            .reset_index(name="error_count")
            .sort_values(["dataset", "error_count"], ascending=[True, False])
            .reset_index(drop=True)
        )
    return summary, error_summary


def build_overview_404_case_index(universe_lt1b: pd.DataFrame, market_universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    audit = safe_read_csv(AUDIT_CSV)
    if audit.empty:
        return pd.DataFrame(), pd.DataFrame()
    audit["dataset"] = audit["dataset"].astype("string")
    audit["ticker"] = normalize_ticker(audit["ticker"])
    audit["http_status"] = pd.to_numeric(audit["http_status"], errors="coerce")
    audit["request_date"] = pd.to_datetime(audit["request_date"], errors="coerce")
    ov404 = audit[(audit["dataset"] == "overview") & (audit["http_status"] == 404)].copy()
    if ov404.empty:
        return pd.DataFrame(), pd.DataFrame()
    ov404["ends_w"] = ov404["ticker"].astype("string").str.endswith("W", na=False)
    ov404["ends_ws"] = ov404["ticker"].astype("string").str.endswith("WS", na=False)
    ov404["ends_u"] = ov404["ticker"].astype("string").str.endswith("U", na=False)
    ov404["ends_r"] = ov404["ticker"].astype("string").str.endswith("R", na=False)
    ov404["contains_dot"] = ov404["ticker"].astype("string").str.contains(r"\.", na=False)
    ov404["contains_slash"] = ov404["ticker"].astype("string").str.contains("/", na=False)
    ov404["contains_eq"] = ov404["ticker"].astype("string").str.contains("=", na=False)
    ov404["in_lt1b_universe"] = ov404["ticker"].isin(set(universe_lt1b["ticker"])) if not universe_lt1b.empty else False
    ov404["in_market_universe"] = ov404["ticker"].isin(set(market_universe["ticker"])) if not market_universe.empty else False
    ov404["overview_404_bucket"] = "review_overview_404_other"
    ov404.loc[ov404["ends_w"], "overview_404_bucket"] = "review_overview_404_w_suffix"
    ov404.loc[ov404["contains_dot"], "overview_404_bucket"] = "review_overview_404_punctuation"

    detail_cols = [c for c in ["ticker", "request_date", "msg", "out_file", "ends_w", "ends_ws", "ends_u", "ends_r", "contains_dot", "contains_slash", "contains_eq", "in_lt1b_universe", "in_market_universe", "overview_404_bucket"] if c in ov404.columns]
    detail = ov404[detail_cols].sort_values(["overview_404_bucket", "ticker", "request_date"]).reset_index(drop=True)
    summary = (
        detail.groupby("overview_404_bucket", dropna=False)
        .agg(
            rows=("ticker", "size"),
            distinct_tickers=("ticker", "nunique"),
            lt1b_rows=("in_lt1b_universe", lambda s: int(pd.Series(s).fillna(False).sum())),
            market_rows=("in_market_universe", lambda s: int(pd.Series(s).fillna(False).sum())),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
        .reset_index(drop=True)
    )
    return detail, summary


def schema_summary_for_dataset(dataset: str, paths: Iterable[Path], sample_limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in list(paths)[:sample_limit]:
        try:
            table = pq.read_table(path)
            rows.append(
                {
                    "dataset": dataset,
                    "path": str(path),
                    "num_rows": int(table.num_rows),
                    "num_cols": len(table.schema.names),
                    "columns": json.dumps(table.schema.names, ensure_ascii=False),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "dataset": dataset,
                    "path": str(path),
                    "num_rows": pd.NA,
                    "num_cols": pd.NA,
                    "columns": json.dumps([], ensure_ascii=False),
                    "schema_error": f"{type(exc).__name__}: {exc}",
                }
            )
    return rows


def build_schema_summary(cfg: BuildConfig) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    rows.extend(schema_summary_for_dataset("overview", list_parquet_files(OVERVIEW_DIR), cfg.sample_files_per_dataset))
    rows.extend(schema_summary_for_dataset("all_tickers", list_parquet_files(ALL_TICKERS_DIR), cfg.sample_files_per_dataset))
    rows.extend(schema_summary_for_dataset("events", list_parquet_files(EVENTS_DIR), cfg.sample_files_per_dataset))
    rows.extend(schema_summary_for_dataset("splits", list_parquet_files(SPLITS_DIR), cfg.sample_files_per_dataset))
    rows.extend(schema_summary_for_dataset("dividends", list_parquet_files(DIVIDENDS_DIR), cfg.sample_files_per_dataset))
    rows.extend(schema_summary_for_dataset("ticker_types", [TICKER_TYPES_PATH], cfg.sample_files_per_dataset))
    rows.extend(schema_summary_for_dataset("exchanges", [EXCHANGES_PATH], cfg.sample_files_per_dataset))
    return pd.DataFrame(rows)


def read_lt1b_universe(path: Path) -> pd.DataFrame:
    d = safe_read_parquet(path)
    if d.empty:
        return pd.DataFrame(columns=["ticker"])
    d = d.copy()
    d["ticker"] = normalize_ticker(d["ticker"])
    cols = [c for c in ["ticker", "entity_id", "primary_exchange", "status", "name"] if c in d.columns]
    return d[cols].drop_duplicates(subset=["ticker"]).reset_index(drop=True)


def read_market_universe(path: Path) -> pd.DataFrame:
    d = safe_read_parquet(path)
    if d.empty:
        return pd.DataFrame(columns=["ticker"])
    d = d.copy()
    d["ticker"] = normalize_ticker(d["ticker"])
    for c in ["snapshot_date", "first_seen_date", "last_seen_date"]:
        if c in d.columns:
            d[c] = pd.to_datetime(d[c], errors="coerce")
    return d


def build_identity_snapshot(universe_lt1b: pd.DataFrame) -> pd.DataFrame:
    files = list_parquet_files(OVERVIEW_DIR)
    frames: list[pd.DataFrame] = []
    for path in files:
        df = safe_read_parquet(path)
        if df.empty:
            continue
        df = df.copy()
        if "ticker" not in df.columns:
            continue
        df["ticker"] = normalize_ticker(df["ticker"])
        if "request_date" in df.columns:
            df["request_date"] = pd.to_datetime(df["request_date"], errors="coerce")
        if "active" in df.columns:
            df["active"] = df["active"].astype("boolean")
        if "list_date" in df.columns:
            df["list_date"] = pd.to_datetime(df["list_date"], errors="coerce")
        if "market_cap" in df.columns:
            df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
        frames.append(df)
    if not frames:
        return pd.DataFrame()

    out = pd.concat(frames, ignore_index=True, sort=False)
    out["in_lt1b_universe"] = out["ticker"].isin(set(universe_lt1b["ticker"])) if not universe_lt1b.empty else False
    out["missing_identity_core"] = out[["name", "type", "primary_exchange"]].isna().all(axis=1)
    out["transient_symbol_flag"] = out["ticker"].astype("string").str.contains(TRANSIENT_PATTERN, regex=True, na=False)
    out["suffix_variant_flag"] = out["ticker"].astype("string").str.contains(SUFFIX_VARIANT_PATTERN, regex=True, na=False)
    out["instrument_family"] = pd.NA
    if "type" in out.columns:
        out.loc[out["type"].astype("string").eq("CS"), "instrument_family"] = "common_stock"
        out.loc[out["type"].astype("string").eq("PFD"), "instrument_family"] = "preferred"
        out.loc[out["type"].astype("string").eq("UNIT"), "instrument_family"] = "unit"
        out.loc[out["type"].astype("string").eq("WARRANT"), "instrument_family"] = "warrant"
        out.loc[out["type"].astype("string").eq("RIGHT"), "instrument_family"] = "right"
    out["identity_bucket"] = "good_identity_snapshot"
    out.loc[out["missing_identity_core"], "identity_bucket"] = "bad_unresolved_identity"
    out.loc[~out["missing_identity_core"] & out["transient_symbol_flag"], "identity_bucket"] = "review_transient_symbol"
    out.loc[
        ~out["missing_identity_core"]
        & out["instrument_family"].isin(["preferred", "unit", "warrant", "right"]).fillna(False),
        "identity_bucket",
    ] = "review_instrument_type_ambiguity"
    return out


def build_identity_quality_summary(identity: pd.DataFrame) -> pd.DataFrame:
    if identity.empty:
        return pd.DataFrame()
    out = (
        identity.groupby("identity_bucket", dropna=False)
        .agg(
            rows=("ticker", "size"),
            distinct_tickers=("ticker", "nunique"),
            lt1b_rows=("in_lt1b_universe", lambda s: int(pd.Series(s).fillna(False).sum())),
            with_market_cap=("market_cap", lambda s: int(pd.to_numeric(s, errors="coerce").notna().sum())),
            active_true=("active", lambda s: int(pd.Series(s).fillna(False).sum())),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
        .reset_index(drop=True)
    )
    out["row_pct"] = (100.0 * out["rows"] / max(1, int(out["rows"].sum()))).round(2)
    return out


def build_identity_case_index(identity: pd.DataFrame) -> pd.DataFrame:
    if identity.empty:
        return pd.DataFrame()
    cols = [
        c
        for c in [
            "ticker",
            "request_date",
            "name",
            "type",
            "primary_exchange",
            "active",
            "market_cap",
            "ticker_root",
            "list_date",
            "identity_bucket",
            "transient_symbol_flag",
            "suffix_variant_flag",
            "in_lt1b_universe",
        ]
        if c in identity.columns
    ]
    out = identity[cols].copy()
    out = out.sort_values(["identity_bucket", "ticker", "request_date"], na_position="last").reset_index(drop=True)
    return out


def build_listing_snapshots(universe_lt1b: pd.DataFrame) -> pd.DataFrame:
    files = list_parquet_files(ALL_TICKERS_DIR)
    frames: list[pd.DataFrame] = []
    for path in files:
        df = safe_read_parquet(path)
        if df.empty or "ticker" not in df.columns:
            continue
        df = df.copy()
        df["ticker"] = normalize_ticker(df["ticker"])
        if "snapshot_date" in df.columns:
            df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], errors="coerce")
        if "last_updated_utc" in df.columns:
            df["last_updated_utc"] = pd.to_datetime(df["last_updated_utc"], errors="coerce")
        if "active" in df.columns:
            df["active"] = df["active"].astype("boolean")
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True, sort=False)
    out["in_lt1b_universe"] = out["ticker"].isin(set(universe_lt1b["ticker"])) if not universe_lt1b.empty else False
    return out


def build_listing_snapshot_summary(listing: pd.DataFrame) -> pd.DataFrame:
    if listing.empty:
        return pd.DataFrame()
    out = (
        listing.groupby("ticker", dropna=False)
        .agg(
            snapshot_rows=("ticker", "size"),
            first_snapshot=("snapshot_date", "min"),
            last_snapshot=("snapshot_date", "max"),
            exchange_nunique=("primary_exchange", lambda s: int(pd.Series(s).dropna().astype("string").nunique())),
            type_nunique=("type", lambda s: int(pd.Series(s).dropna().astype("string").nunique())),
            active_true_rows=("active", lambda s: int(pd.Series(s).fillna(False).sum())),
            in_lt1b_universe=("in_lt1b_universe", "max"),
        )
        .reset_index()
    )
    out["presence_bucket"] = "good_snapshot_presence"
    out.loc[out["exchange_nunique"] > 1, "presence_bucket"] = "review_exchange_or_listing_conflict"
    out.loc[out["type_nunique"] > 1, "presence_bucket"] = "review_instrument_type_ambiguity"
    out.loc[out["snapshot_rows"] <= 2, "presence_bucket"] = "review_sparse_presence"
    return out.sort_values(["presence_bucket", "snapshot_rows", "ticker"], ascending=[True, False, True]).reset_index(drop=True)


def build_ticker_presence_timeline(listing: pd.DataFrame) -> pd.DataFrame:
    if listing.empty:
        return pd.DataFrame()
    cols = [c for c in ["ticker", "snapshot_date", "active", "type", "primary_exchange", "in_lt1b_universe"] if c in listing.columns]
    return listing[cols].sort_values(["ticker", "snapshot_date"]).reset_index(drop=True)


def build_snapshot_presence_gaps(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return pd.DataFrame()
    out = summary.copy()
    out["span_days"] = (out["last_snapshot"] - out["first_snapshot"]).dt.days
    out["sparse_density"] = (out["snapshot_rows"] / out["span_days"].clip(lower=1)).round(6)
    return out.sort_values(["presence_bucket", "snapshot_rows", "ticker"], ascending=[True, True, True]).reset_index(drop=True)


def build_remap_candidates(identity: pd.DataFrame, listing_summary: pd.DataFrame) -> pd.DataFrame:
    if identity.empty:
        return pd.DataFrame()
    out = identity[identity["identity_bucket"].astype("string").str.startswith("review_", na=False)].copy()
    if out.empty:
        return out
    out["ticker_base"] = out["ticker"].astype("string").str.replace(r"[\./=].*$", "", regex=True).str.replace(r"(WS|W|U|R)$", "", regex=True)
    if not listing_summary.empty:
        listing_lookup = listing_summary[["ticker", "snapshot_rows", "presence_bucket"]].rename(
            columns={"ticker": "ticker_base", "snapshot_rows": "base_snapshot_rows", "presence_bucket": "base_presence_bucket"}
        )
        out = out.merge(listing_lookup, on="ticker_base", how="left")
    out["remap_candidate_flag"] = out["ticker_base"].notna() & out["ticker_base"].ne(out["ticker"])
    cols = [c for c in ["ticker", "ticker_base", "request_date", "identity_bucket", "type", "primary_exchange", "base_snapshot_rows", "base_presence_bucket", "remap_candidate_flag"] if c in out.columns]
    return out[cols].sort_values(["remap_candidate_flag", "ticker"], ascending=[False, True]).reset_index(drop=True)


def build_transient_symbol_review(identity: pd.DataFrame) -> pd.DataFrame:
    if identity.empty:
        return pd.DataFrame()
    out = identity[identity["transient_symbol_flag"].fillna(False)].copy()
    cols = [c for c in ["ticker", "request_date", "type", "primary_exchange", "name", "identity_bucket", "in_lt1b_universe"] if c in out.columns]
    return out[cols].sort_values(["ticker", "request_date"]).reset_index(drop=True)


def build_instrument_type_summary(identity: pd.DataFrame, listing: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not identity.empty and "type" in identity.columns:
        frames.append(
            identity.groupby("type", dropna=False)
            .agg(identity_rows=("ticker", "size"), identity_tickers=("ticker", "nunique"))
            .reset_index()
        )
    if not listing.empty and "type" in listing.columns:
        listing_part = (
            listing.groupby("type", dropna=False)
            .agg(listing_rows=("ticker", "size"), listing_tickers=("ticker", "nunique"))
            .reset_index()
        )
        if frames:
            out = frames[0].merge(listing_part, on="type", how="outer")
        else:
            out = listing_part
        return out.sort_values("type", na_position="last").reset_index(drop=True)
    return frames[0] if frames else pd.DataFrame()


def build_exchange_summary(identity: pd.DataFrame, listing: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not identity.empty and "primary_exchange" in identity.columns:
        frames.append(
            identity.groupby("primary_exchange", dropna=False)
            .agg(identity_rows=("ticker", "size"), identity_tickers=("ticker", "nunique"))
            .reset_index()
        )
    if not listing.empty and "primary_exchange" in listing.columns:
        listing_part = (
            listing.groupby("primary_exchange", dropna=False)
            .agg(listing_rows=("ticker", "size"), listing_tickers=("ticker", "nunique"))
            .reset_index()
        )
        if frames:
            out = frames[0].merge(listing_part, on="primary_exchange", how="outer")
        else:
            out = listing_part
        return out.sort_values("primary_exchange", na_position="last").reset_index(drop=True)
    return frames[0] if frames else pd.DataFrame()


def _explode_event_records(value: Any) -> list[dict[str, Any]]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, np.ndarray):
        return [x for x in value.tolist() if isinstance(x, dict)]
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def build_events_exploded(universe_lt1b: pd.DataFrame) -> pd.DataFrame:
    files = list_parquet_files(EVENTS_DIR)
    rows: list[dict[str, Any]] = []
    for path in files:
        df = safe_read_parquet(path)
        if df.empty or "ticker" not in df.columns:
            continue
        for _, row in df.iterrows():
            ticker = str(row.get("ticker", "")).strip().upper()
            events = _explode_event_records(row.get("events"))
            if not events:
                rows.append(
                    {
                        "ticker": ticker,
                        "event_type": pd.NA,
                        "event_date": pd.NaT,
                        "event_status": "empty_events_payload",
                        "in_lt1b_universe": ticker in set(universe_lt1b["ticker"]) if not universe_lt1b.empty else False,
                    }
                )
                continue
            for idx, event in enumerate(events, start=1):
                event_date = event.get("date") or event.get("execution_date") or event.get("event_date") or event.get("published_utc")
                event_type = event.get("type") or event.get("event_type") or event.get("name")
                ticker_change_to = pd.NA
                if isinstance(event.get("ticker_change"), dict):
                    ticker_change_to = event["ticker_change"].get("ticker", pd.NA)
                rows.append(
                    {
                        "ticker": ticker,
                        "event_idx": idx,
                        "event_type": str(event_type) if event_type is not None else pd.NA,
                        "event_date": pd.to_datetime(event_date, errors="coerce"),
                        "event_status": "ok_event",
                        "ticker_change_to": ticker_change_to,
                        "event_payload": json.dumps(event, ensure_ascii=False, default=str),
                        "in_lt1b_universe": ticker in set(universe_lt1b["ticker"]) if not universe_lt1b.empty else False,
                    }
                )
    return pd.DataFrame(rows)


def build_event_type_summary(events_exploded: pd.DataFrame) -> pd.DataFrame:
    if events_exploded.empty:
        return pd.DataFrame()
    out = (
        events_exploded.groupby(["event_status", "event_type"], dropna=False)
        .agg(rows=("ticker", "size"), distinct_tickers=("ticker", "nunique"))
        .reset_index()
        .sort_values(["event_status", "rows"], ascending=[True, False])
        .reset_index(drop=True)
    )
    return out


def build_splits_summary(universe_lt1b: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    files = list_parquet_files(SPLITS_DIR)
    frames: list[pd.DataFrame] = []
    for path in files:
        df = safe_read_parquet(path)
        if df.empty or "ticker" not in df.columns:
            continue
        df = df.copy()
        df["ticker"] = normalize_ticker(df["ticker"])
        if "execution_date" in df.columns:
            df["execution_date"] = pd.to_datetime(df["execution_date"], errors="coerce")
        if "split_from" in df.columns:
            df["split_from"] = pd.to_numeric(df["split_from"], errors="coerce")
        if "split_to" in df.columns:
            df["split_to"] = pd.to_numeric(df["split_to"], errors="coerce")
        frames.append(df)
    if not frames:
        return pd.DataFrame(), pd.DataFrame()
    splits = pd.concat(frames, ignore_index=True, sort=False)
    splits["in_lt1b_universe"] = splits["ticker"].isin(set(universe_lt1b["ticker"])) if not universe_lt1b.empty else False
    splits["split_ratio"] = splits["split_to"] / splits["split_from"]
    splits["split_bucket"] = "good_split_event"
    placeholder_mask = splits["execution_date"].isna() & splits["id"].isna() & splits["split_from"].isna() & splits["split_to"].isna()
    splits.loc[placeholder_mask, "split_bucket"] = "review_no_split_payload"
    splits.loc[splits["execution_date"].isna() & ~placeholder_mask, "split_bucket"] = "bad_reference_event"
    splits.loc[(splits["split_from"].isna() | splits["split_to"].isna()) & ~placeholder_mask, "split_bucket"] = "review_split_scale_uncertain"
    splits.loc[(splits["split_from"] <= 0) | (splits["split_to"] <= 0), "split_bucket"] = "bad_reference_event"

    summary = (
        splits.groupby("split_bucket", dropna=False)
        .agg(rows=("ticker", "size"), distinct_tickers=("ticker", "nunique"), lt1b_rows=("in_lt1b_universe", lambda s: int(pd.Series(s).fillna(False).sum())))
        .reset_index()
        .sort_values("rows", ascending=False)
        .reset_index(drop=True)
    )
    return splits, summary


def build_dividends_summary(universe_lt1b: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    files = list_parquet_files(DIVIDENDS_DIR)
    frames: list[pd.DataFrame] = []
    for path in files:
        df = safe_read_parquet(path)
        if df.empty or "ticker" not in df.columns:
            continue
        df = df.copy()
        df["ticker"] = normalize_ticker(df["ticker"])
        frames.append(df)
    if not frames:
        return pd.DataFrame(), pd.DataFrame()
    dividends = pd.concat(frames, ignore_index=True, sort=False)
    dividends["in_lt1b_universe"] = dividends["ticker"].isin(set(universe_lt1b["ticker"])) if not universe_lt1b.empty else False
    metadata_only_cols = {"ticker", "_dataset", "_ingested_utc"}
    payload_cols = [c for c in dividends.columns if c not in metadata_only_cols and c != "in_lt1b_universe"]
    dividends["has_payload_cols"] = len(payload_cols) > 0
    dividends["non_null_payload_fields"] = 0
    if payload_cols:
        dividends["non_null_payload_fields"] = dividends[payload_cols].notna().sum(axis=1)
    dividends["dividend_bucket"] = "review_no_dividend_payload"
    dividends.loc[dividends["non_null_payload_fields"] > 0, "dividend_bucket"] = "good_dividend_event"

    summary = (
        dividends.groupby("dividend_bucket", dropna=False)
        .agg(
            rows=("ticker", "size"),
            distinct_tickers=("ticker", "nunique"),
            lt1b_rows=("in_lt1b_universe", lambda s: int(pd.Series(s).fillna(False).sum())),
            payload_rows=("non_null_payload_fields", lambda s: int((pd.to_numeric(s, errors="coerce") > 0).sum())),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
        .reset_index(drop=True)
    )
    return dividends, summary


def load_trades_policy_examples() -> pd.DataFrame:
    d = safe_read_parquet(TRADES_FILE_ACCEPTANCE_EXAMPLES_PATH)
    if d.empty:
        return d
    d = d.copy()
    d["ticker"] = normalize_ticker(d["ticker"])
    d["date"] = pd.to_datetime(d["date"], errors="coerce")
    return d


def load_halts_lt1b_event_index() -> pd.DataFrame:
    d = safe_read_parquet(HALTS_LT1B_EVENT_INDEX_PATH)
    if d.empty:
        return d
    d = d.copy()
    d["ticker"] = normalize_ticker(d["ticker"])
    d["halt_date"] = pd.to_datetime(d["halt_date"], errors="coerce")
    if "halt_start_et" in d.columns:
        d["halt_start_et"] = pd.to_datetime(d["halt_start_et"], errors="coerce")
    if "resume_trade_et" in d.columns:
        d["resume_trade_et"] = pd.to_datetime(d["resume_trade_et"], errors="coerce")
    return d


def load_trades_final_bucket() -> pd.DataFrame:
    d = safe_read_parquet(TRADES_FINAL_BUCKET_PATH)
    if d.empty:
        return d
    d = d.copy()
    d["ticker"] = normalize_ticker(d["ticker"])
    d["date"] = pd.to_datetime(d["date"], errors="coerce")
    return d


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
        return {}


def _parse_token_list(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, np.ndarray):
        return _parse_token_list(value.tolist())
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    text = str(value).strip()
    if not text or text == "[]" or text.lower() == "nan":
        return []
    try:
        parsed = json.loads(text.replace("'", '"'))
        if isinstance(parsed, list):
            return [str(x) for x in parsed if str(x).strip()]
    except Exception:
        pass
    return [chunk.strip(" '\"") for chunk in text.strip("[]").split(",") if chunk.strip(" '\"")]


def build_reference_overview_market_identity_links(
    identity_case_index: pd.DataFrame,
    overview_404_case_index: pd.DataFrame,
    remap_candidates: pd.DataFrame,
    trades_examples: pd.DataFrame,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not trades_examples.empty:
        trades_cols = [c for c in ["ticker", "date", "severity", "sample_stratum", "acceptance_label", "scale_bucket_vw", "scale_bucket_high", "scale_bucket_low"] if c in trades_examples.columns]
        trades_min = trades_examples[trades_cols].copy()
    else:
        trades_min = pd.DataFrame(columns=["ticker", "date"])

    if not overview_404_case_index.empty:
        x = overview_404_case_index.copy()
        x["identity_link_type"] = "overview_404"
        frames.append(x.merge(trades_min, on="ticker", how="left"))
    if not remap_candidates.empty:
        y = remap_candidates.copy()
        y["identity_link_type"] = "remap_candidate"
        frames.append(y.merge(trades_min, on="ticker", how="left"))
    if not identity_case_index.empty:
        z = identity_case_index[identity_case_index["identity_bucket"].astype("string").ne("good_identity_snapshot")].copy()
        z["identity_link_type"] = "identity_review_case"
        frames.append(z.merge(trades_min, on="ticker", how="left"))

    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True, sort=False)
    out["has_trades_example_link"] = out["date"].notna()
    if "acceptance_label" in out.columns:
        scale_link = out["acceptance_label"].astype("string").eq("reference_scale_mismatch").fillna(False)
        out["identity_market_bucket"] = np.where(
            scale_link,
            "identity_review_linked_to_scale_mismatch",
            np.where(out["has_trades_example_link"], "identity_review_linked_to_other_trades_case", "identity_review_without_trades_link"),
        )
    else:
        out["identity_market_bucket"] = np.where(out["has_trades_example_link"], "identity_review_linked_to_trades_case", "identity_review_without_trades_link")
    return out


def build_reference_split_market_link_candidates(splits: pd.DataFrame, trades_final_bucket: pd.DataFrame, universe_lt1b: pd.DataFrame) -> pd.DataFrame:
    if splits.empty or trades_final_bucket.empty:
        return pd.DataFrame()
    split_real = splits[splits["split_bucket"] == "good_split_event"].copy()
    if split_real.empty:
        return pd.DataFrame()
    lt1b_tickers = set(universe_lt1b["ticker"]) if not universe_lt1b.empty else set()
    trades = trades_final_bucket.copy()
    if lt1b_tickers:
        trades = trades[trades["ticker"].isin(lt1b_tickers)].copy()
    trades = trades[
        trades["has_scale_warn"].fillna(False)
        | trades["final_bucket"].astype("string").eq("scale_suspect")
    ].copy()
    if trades.empty:
        return pd.DataFrame()
    merge = split_real.merge(trades, on="ticker", how="inner", suffixes=("_split", "_trade"))
    if merge.empty:
        return merge
    merge["trade_date"] = pd.to_datetime(merge["date"], errors="coerce")
    merge["days_from_split"] = (merge["trade_date"] - merge["execution_date"]).dt.days
    merge["abs_days_from_split"] = merge["days_from_split"].abs()
    merge = merge[merge["abs_days_from_split"] <= 7].copy()
    if merge.empty:
        return merge
    merge["split_timing_bucket"] = np.where(
        merge["abs_days_from_split"] == 0,
        "same_day",
        np.where(merge["abs_days_from_split"] <= 3, "near_3d", "near_7d"),
    )
    merge["reference_market_bucket"] = "reference_split_near_market_case"
    merge.loc[
        merge["final_bucket"].astype("string").eq("scale_suspect")
        & merge["abs_days_from_split"].le(3),
        "reference_market_bucket",
    ] = "split_explains_trade_scale_mismatch"
    merge.loc[
        merge["final_bucket"].astype("string").eq("scale_suspect")
        & merge["abs_days_from_split"].gt(3),
        "reference_market_bucket",
    ] = "split_near_scale_mismatch_review"
    merge.loc[
        merge["final_bucket"].astype("string").ne("scale_suspect")
        & merge["abs_days_from_split"].le(3),
        "reference_market_bucket",
    ] = "split_near_non_scale_market_case"
    return merge.sort_values(["reference_market_bucket", "ticker", "execution_date", "trade_date"]).reset_index(drop=True)


def build_reference_event_halt_link_candidates(events_exploded: pd.DataFrame, halts_event_index: pd.DataFrame) -> pd.DataFrame:
    if events_exploded.empty or halts_event_index.empty:
        return pd.DataFrame()
    events_ok = events_exploded[events_exploded["event_status"] == "ok_event"].copy()
    if events_ok.empty:
        return pd.DataFrame()
    merge = events_ok.merge(
        halts_event_index[
            [
                "event_id_canonical",
                "ticker",
                "halt_date",
                "halt_start_et",
                "resume_trade_et",
                "event_taxonomy",
                "in_lt1b_universe",
            ]
        ].rename(columns={"in_lt1b_universe": "halt_in_lt1b_universe"}),
        on="ticker",
        how="inner",
    )
    if merge.empty:
        return merge
    merge["days_event_to_halt"] = (merge["halt_date"] - merge["event_date"]).dt.days
    merge["abs_days_event_to_halt"] = merge["days_event_to_halt"].abs()
    merge = merge[merge["abs_days_event_to_halt"] <= 30].copy()
    if merge.empty:
        return merge
    merge["event_halt_timing_bucket"] = np.where(
        merge["abs_days_event_to_halt"] == 0,
        "same_day",
        np.where(merge["abs_days_event_to_halt"] <= 3, "near_3d", "near_30d"),
    )
    merge["reference_halt_bucket"] = np.where(
        merge["event_type"].astype("string").eq("ticker_change") & merge["abs_days_event_to_halt"].le(3),
        "ticker_change_near_halt",
        "reference_event_near_halt_review",
    )
    merge = (
        merge.sort_values(["ticker", "event_idx", "event_date", "abs_days_event_to_halt", "halt_date"], ascending=[True, True, True, True, True])
        .drop_duplicates(subset=["ticker", "event_idx", "event_date", "event_type"], keep="first")
        .reset_index(drop=True)
    )
    return merge.sort_values(["reference_halt_bucket", "ticker", "event_date", "halt_date"]).reset_index(drop=True)


def build_reference_event_quotes_link_candidates(events_exploded: pd.DataFrame) -> pd.DataFrame:
    if events_exploded.empty or not QUOTES_CURRENT_CD_PATH.exists():
        return pd.DataFrame()
    events_ok = events_exploded[events_exploded["event_status"] == "ok_event"].copy()
    if events_ok.empty:
        return pd.DataFrame()
    event_tickers = set(events_ok["ticker"].dropna().astype(str).tolist())
    quote_rows: list[pd.DataFrame] = []
    pf = pq.ParquetFile(QUOTES_CURRENT_CD_PATH)
    cols = ["ticker", "date", "severity", "warns", "issues", "metrics_json"]
    for batch in pf.iter_batches(columns=cols, batch_size=200_000):
        df = batch.to_pandas()
        df["ticker"] = normalize_ticker(df["ticker"])
        df = df[df["ticker"].isin(event_tickers)].copy()
        if df.empty:
            continue
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        metrics = df["metrics_json"].map(_parse_metrics_json)
        df["m.crossed_ratio_pct"] = pd.to_numeric(metrics.map(lambda x: x.get("crossed_ratio_pct")), errors="coerce")
        df["m.crossed_rows"] = pd.to_numeric(metrics.map(lambda x: x.get("crossed_rows")), errors="coerce")
        df["m.timestamp_out_of_partition_day"] = metrics.map(lambda x: bool(x.get("timestamp_out_of_partition_day", False)))
        df["warns_list"] = df["warns"].map(_parse_token_list)
        df["issues_list"] = df["issues"].map(_parse_token_list)
        df["quotes_anomaly_flag"] = (
            df["severity"].astype("string").ne("PASS")
            | df["m.crossed_ratio_pct"].fillna(0).gt(0)
            | df["m.timestamp_out_of_partition_day"].fillna(False)
        )
        keep_cols = ["ticker", "date", "severity", "m.crossed_ratio_pct", "m.crossed_rows", "m.timestamp_out_of_partition_day", "warns_list", "issues_list", "quotes_anomaly_flag"]
        quote_rows.append(df[keep_cols])
    if not quote_rows:
        return pd.DataFrame()
    quotes_df = pd.concat(quote_rows, ignore_index=True, sort=False)
    merge = events_ok.merge(quotes_df, on="ticker", how="inner")
    if merge.empty:
        return merge
    merge["days_event_to_quote"] = (merge["date"] - merge["event_date"]).dt.days
    merge["abs_days_event_to_quote"] = merge["days_event_to_quote"].abs()
    merge = merge[merge["abs_days_event_to_quote"] <= 30].copy()
    if merge.empty:
        return merge
    merge["event_quotes_timing_bucket"] = np.where(
        merge["abs_days_event_to_quote"] == 0,
        "same_day",
        np.where(merge["abs_days_event_to_quote"] <= 3, "near_3d", "near_30d"),
    )
    merge["reference_quotes_bucket"] = np.where(
        merge["quotes_anomaly_flag"].fillna(False) & merge["abs_days_event_to_quote"].le(3),
        "ticker_change_near_quotes_anomaly",
        np.where(
            merge["quotes_anomaly_flag"].fillna(False),
            "reference_event_near_quotes_review",
            "reference_event_near_quotes_clean",
        ),
    )
    merge = (
        merge.sort_values(
            ["ticker", "event_idx", "event_date", "quotes_anomaly_flag", "abs_days_event_to_quote", "m.crossed_ratio_pct"],
            ascending=[True, True, True, False, True, False],
        )
        .drop_duplicates(subset=["ticker", "event_idx", "event_date", "event_type"], keep="first")
        .reset_index(drop=True)
    )
    return merge.sort_values(["reference_quotes_bucket", "ticker", "event_date", "date"]).reset_index(drop=True)


def build_reference_causal_alignment_summary(
    identity_links: pd.DataFrame,
    split_links: pd.DataFrame,
    event_halt_links: pd.DataFrame,
    split_daily_links: pd.DataFrame | None = None,
    split_1m_links: pd.DataFrame | None = None,
    event_quotes_links: pd.DataFrame | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not identity_links.empty:
        for bucket, count in identity_links["identity_market_bucket"].value_counts(dropna=False).items():
            rows.append({"causal_domain": "identity_vs_trades", "bucket": bucket, "rows": int(count)})
    if not split_links.empty:
        for bucket, count in split_links["reference_market_bucket"].value_counts(dropna=False).items():
            rows.append({"causal_domain": "splits_vs_trades", "bucket": bucket, "rows": int(count)})
    if not event_halt_links.empty:
        for bucket, count in event_halt_links["reference_halt_bucket"].value_counts(dropna=False).items():
            rows.append({"causal_domain": "events_vs_halts", "bucket": bucket, "rows": int(count)})
    if split_daily_links is not None and not split_daily_links.empty:
        for bucket, count in split_daily_links["daily_split_alignment_bucket"].value_counts(dropna=False).items():
            rows.append({"causal_domain": "splits_vs_daily", "bucket": bucket, "rows": int(count)})
    if split_1m_links is not None and not split_1m_links.empty:
        for bucket, count in split_1m_links["m1_split_alignment_bucket"].value_counts(dropna=False).items():
            rows.append({"causal_domain": "splits_vs_1m", "bucket": bucket, "rows": int(count)})
    if event_quotes_links is not None and not event_quotes_links.empty:
        for bucket, count in event_quotes_links["reference_quotes_bucket"].value_counts(dropna=False).items():
            rows.append({"causal_domain": "events_vs_quotes", "bucket": bucket, "rows": int(count)})
    return pd.DataFrame(rows).sort_values(["causal_domain", "rows"], ascending=[True, False]).reset_index(drop=True) if rows else pd.DataFrame(columns=["causal_domain", "bucket", "rows"])


def _read_daily_window(ticker: str, split_date: pd.Timestamp) -> dict[str, Any]:
    year_path = RAW_DAILY_ROOT / f"ticker={ticker}" / f"year={split_date.year}" / f"day_aggs_{ticker}_{split_date.year}.parquet"
    if not year_path.exists():
        return {"daily_window_status": "missing_daily_file"}
    df = pd.read_parquet(year_path)
    if df.empty:
        return {"daily_window_status": "empty_daily_file"}
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)
    same = df[df["date"] == split_date].copy()
    if same.empty:
        return {"daily_window_status": "split_date_not_in_daily"}
    idx = same.index[0]
    prev_row = df.iloc[idx - 1] if idx > 0 else None
    cur_row = df.iloc[idx]
    next_row = df.iloc[idx + 1] if idx + 1 < len(df) else None
    prev_close = pd.to_numeric(prev_row["c"], errors="coerce") if prev_row is not None else np.nan
    split_open = pd.to_numeric(cur_row["o"], errors="coerce")
    split_close = pd.to_numeric(cur_row["c"], errors="coerce")
    split_vw = pd.to_numeric(cur_row["vw"], errors="coerce")
    next_close = pd.to_numeric(next_row["c"], errors="coerce") if next_row is not None else np.nan
    return {
        "daily_window_status": "ok",
        "daily_prev_date": prev_row["date"] if prev_row is not None else pd.NaT,
        "daily_prev_close": prev_close,
        "daily_split_date": cur_row["date"],
        "daily_split_open": split_open,
        "daily_split_close": split_close,
        "daily_split_vw": split_vw,
        "daily_next_date": next_row["date"] if next_row is not None else pd.NaT,
        "daily_next_close": next_close,
    }


def _read_1m_window(ticker: str, split_date: pd.Timestamp) -> dict[str, Any]:
    prev_day = split_date - pd.Timedelta(days=7)
    months = sorted({(split_date.year, split_date.month), (prev_day.year, prev_day.month)})
    frames: list[pd.DataFrame] = []
    for year, month in months:
        path = RAW_1M_ROOT / f"ticker={ticker}" / f"year={year}" / f"month={month:02d}" / f"minute_aggs_{ticker}_{year}_{month:02d}.parquet"
        if path.exists():
            x = pd.read_parquet(path)
            if not x.empty:
                frames.append(x)
    if not frames:
        return {"m1_window_status": "missing_1m_files"}
    df = pd.concat(frames, ignore_index=True, sort=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], errors="coerce", utc=True)
    df = df.sort_values("ts_utc").reset_index(drop=True)
    pre = df[df["date"] < split_date].copy()
    cur = df[df["date"] == split_date].copy()
    if cur.empty:
        return {"m1_window_status": "split_date_not_in_1m"}
    prev_last = pre.iloc[-1] if not pre.empty else None
    cur_first = cur.iloc[0]
    cur_last = cur.iloc[-1]
    return {
        "m1_window_status": "ok",
        "m1_prev_ts_utc": prev_last["ts_utc"] if prev_last is not None else pd.NaT,
        "m1_prev_close": pd.to_numeric(prev_last["c"], errors="coerce") if prev_last is not None else np.nan,
        "m1_first_ts_utc": cur_first["ts_utc"],
        "m1_first_open": pd.to_numeric(cur_first["o"], errors="coerce"),
        "m1_first_close": pd.to_numeric(cur_first["c"], errors="coerce"),
        "m1_last_ts_utc": cur_last["ts_utc"],
        "m1_last_close": pd.to_numeric(cur_last["c"], errors="coerce"),
    }


def _best_scale_alignment(observed_values: list[float], prev_value: float, split_ratio: float) -> tuple[float, float]:
    if pd.isna(prev_value) or prev_value == 0 or pd.isna(split_ratio) or split_ratio == 0:
        return np.nan, np.nan
    ratios = []
    for value in observed_values:
        if pd.notna(value):
            ratios.append(value / prev_value)
    if not ratios:
        return np.nan, np.nan
    arr = np.array(ratios, dtype=float)
    diffs = np.abs(arr - split_ratio)
    idx = int(diffs.argmin())
    return float(arr[idx]), float(diffs[idx])


def build_reference_split_daily_link_candidates(split_links: pd.DataFrame) -> pd.DataFrame:
    if split_links.empty:
        return pd.DataFrame()
    base = split_links[["ticker", "execution_date", "split_from", "split_to", "split_ratio", "reference_market_bucket"]].drop_duplicates().copy()
    rows: list[dict[str, Any]] = []
    for _, row in base.iterrows():
        ticker = str(row["ticker"])
        split_date = pd.to_datetime(row["execution_date"], errors="coerce")
        payload = row.to_dict()
        payload.update(_read_daily_window(ticker, split_date))
        best_ratio, best_diff = _best_scale_alignment(
            [payload.get("daily_split_open"), payload.get("daily_split_close"), payload.get("daily_split_vw"), payload.get("daily_next_close")],
            payload.get("daily_prev_close"),
            row.get("split_ratio"),
        )
        payload["daily_best_ratio_vs_prev_close"] = best_ratio
        payload["daily_best_ratio_diff_vs_split_ratio"] = best_diff
        payload["daily_split_alignment_bucket"] = "review_no_daily_alignment"
        if payload.get("daily_window_status") == "ok":
            if pd.notna(best_diff) and best_diff <= 0.02:
                payload["daily_split_alignment_bucket"] = "daily_split_ratio_coherent"
            elif pd.notna(best_diff) and best_diff <= 0.08:
                payload["daily_split_alignment_bucket"] = "daily_split_ratio_review"
        rows.append(payload)
    return pd.DataFrame(rows).sort_values(["daily_split_alignment_bucket", "ticker", "execution_date"]).reset_index(drop=True)


def build_reference_split_1m_link_candidates(split_links: pd.DataFrame) -> pd.DataFrame:
    if split_links.empty:
        return pd.DataFrame()
    base = split_links[["ticker", "execution_date", "split_from", "split_to", "split_ratio", "reference_market_bucket"]].drop_duplicates().copy()
    rows: list[dict[str, Any]] = []
    for _, row in base.iterrows():
        ticker = str(row["ticker"])
        split_date = pd.to_datetime(row["execution_date"], errors="coerce")
        payload = row.to_dict()
        payload.update(_read_1m_window(ticker, split_date))
        best_ratio, best_diff = _best_scale_alignment(
            [payload.get("m1_first_open"), payload.get("m1_first_close"), payload.get("m1_last_close")],
            payload.get("m1_prev_close"),
            row.get("split_ratio"),
        )
        payload["m1_best_ratio_vs_prev_close"] = best_ratio
        payload["m1_best_ratio_diff_vs_split_ratio"] = best_diff
        payload["m1_split_alignment_bucket"] = "review_no_1m_alignment"
        if payload.get("m1_window_status") == "ok":
            if pd.notna(best_diff) and best_diff <= 0.02:
                payload["m1_split_alignment_bucket"] = "m1_split_ratio_coherent"
            elif pd.notna(best_diff) and best_diff <= 0.08:
                payload["m1_split_alignment_bucket"] = "m1_split_ratio_review"
        rows.append(payload)
    return pd.DataFrame(rows).sort_values(["m1_split_alignment_bucket", "ticker", "execution_date"]).reset_index(drop=True)


def build_manifest(cfg: BuildConfig, artifact_rows: list[dict[str, Any]], started_at: float) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "reference_root": str(cfg.reference_root),
        "cache_root": str(cfg.cache_root),
        "lt1b_universe_path": str(cfg.lt1b_universe_path),
        "market_universe_path": str(cfg.market_universe_path),
        "built_at_utc": utc_now_iso(),
        "duration_sec": round(time.time() - started_at, 3),
        "artifacts": artifact_rows,
    }
    if PROGRESS_JSON.exists():
        try:
            manifest["progress_snapshot"] = json.loads(PROGRESS_JSON.read_text(encoding="utf-8"))
        except Exception:
            manifest["progress_snapshot"] = {"error": "progress_json_unreadable"}
    return manifest


def save_artifact(df: pd.DataFrame, path: Path, artifacts: list[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    df.to_parquet(path, index=False)
    artifacts.append({"path": str(path), "rows": int(len(df)), "columns": list(df.columns)})


def build_reference_audit_artifacts(cfg: BuildConfig) -> dict[str, Any]:
    started_at = time.time()
    ensure_dir(cfg.cache_root)

    artifacts: list[dict[str, Any]] = []

    endpoint_inventory = dataset_file_inventory(cfg)
    save_artifact(endpoint_inventory, cfg.cache_root / "reference_endpoint_inventory.parquet", artifacts)

    download_summary, error_summary = build_download_summaries()
    save_artifact(download_summary, cfg.cache_root / "reference_download_audit_summary.parquet", artifacts)
    save_artifact(error_summary, cfg.cache_root / "reference_download_error_summary.parquet", artifacts)

    schema_summary = build_schema_summary(cfg)
    save_artifact(schema_summary, cfg.cache_root / "reference_schema_summary.parquet", artifacts)

    lt1b_universe = read_lt1b_universe(cfg.lt1b_universe_path)
    market_universe = read_market_universe(cfg.market_universe_path)
    if not market_universe.empty:
        market_case = market_universe[["ticker"]].drop_duplicates().assign(in_market_universe=True)
    else:
        market_case = pd.DataFrame(columns=["ticker", "in_market_universe"])

    overview_404_case_index, overview_404_summary = build_overview_404_case_index(lt1b_universe, market_universe)
    save_artifact(overview_404_case_index, cfg.cache_root / "reference_overview_404_case_index.parquet", artifacts)
    save_artifact(overview_404_summary, cfg.cache_root / "reference_overview_404_summary.parquet", artifacts)

    identity = build_identity_snapshot(lt1b_universe)
    if not identity.empty and not market_case.empty:
        identity = identity.merge(market_case, on="ticker", how="left")
        identity["in_market_universe"] = identity["in_market_universe"].fillna(False)
    save_artifact(identity, cfg.cache_root / "reference_identity_snapshot.parquet", artifacts)

    identity_quality = build_identity_quality_summary(identity)
    save_artifact(identity_quality, cfg.cache_root / "reference_identity_quality_summary.parquet", artifacts)

    identity_case_index = build_identity_case_index(identity)
    save_artifact(identity_case_index, cfg.cache_root / "reference_identity_case_index.parquet", artifacts)

    listing = build_listing_snapshots(lt1b_universe)
    save_artifact(listing, cfg.cache_root / "reference_listing_snapshots.parquet", artifacts)

    listing_summary = build_listing_snapshot_summary(listing)
    save_artifact(listing_summary, cfg.cache_root / "reference_listing_snapshot_summary.parquet", artifacts)

    ticker_presence = build_ticker_presence_timeline(listing)
    save_artifact(ticker_presence, cfg.cache_root / "reference_ticker_presence_timeline.parquet", artifacts)

    presence_gaps = build_snapshot_presence_gaps(listing_summary)
    save_artifact(presence_gaps, cfg.cache_root / "reference_snapshot_presence_gaps.parquet", artifacts)

    remap_candidates = build_remap_candidates(identity, listing_summary)
    save_artifact(remap_candidates, cfg.cache_root / "reference_remap_candidates.parquet", artifacts)

    transient_review = build_transient_symbol_review(identity)
    save_artifact(transient_review, cfg.cache_root / "reference_transient_symbol_review.parquet", artifacts)

    instrument_type_summary = build_instrument_type_summary(identity, listing)
    save_artifact(instrument_type_summary, cfg.cache_root / "reference_instrument_type_summary.parquet", artifacts)

    exchange_summary = build_exchange_summary(identity, listing)
    save_artifact(exchange_summary, cfg.cache_root / "reference_exchange_summary.parquet", artifacts)

    events_exploded = build_events_exploded(lt1b_universe)
    save_artifact(events_exploded, cfg.cache_root / "reference_events_exploded.parquet", artifacts)

    event_type_summary = build_event_type_summary(events_exploded)
    save_artifact(event_type_summary, cfg.cache_root / "reference_event_type_summary.parquet", artifacts)

    splits, splits_summary = build_splits_summary(lt1b_universe)
    save_artifact(splits, cfg.cache_root / "reference_split_case_index.parquet", artifacts)
    save_artifact(splits_summary, cfg.cache_root / "reference_splits_summary.parquet", artifacts)

    dividends, dividends_summary = build_dividends_summary(lt1b_universe)
    save_artifact(dividends, cfg.cache_root / "reference_dividend_case_index.parquet", artifacts)
    save_artifact(dividends_summary, cfg.cache_root / "reference_dividends_summary.parquet", artifacts)

    trades_examples = load_trades_policy_examples()
    trades_final_bucket = load_trades_final_bucket()
    halts_event_index = load_halts_lt1b_event_index()

    overview_market_identity_links = build_reference_overview_market_identity_links(
        identity_case_index,
        overview_404_case_index,
        remap_candidates,
        trades_examples,
    )
    save_artifact(overview_market_identity_links, cfg.cache_root / "reference_overview_market_identity_links.parquet", artifacts)

    split_market_link_candidates = build_reference_split_market_link_candidates(splits, trades_final_bucket, lt1b_universe)
    save_artifact(split_market_link_candidates, cfg.cache_root / "reference_split_market_link_candidates.parquet", artifacts)

    split_daily_link_candidates = build_reference_split_daily_link_candidates(split_market_link_candidates)
    save_artifact(split_daily_link_candidates, cfg.cache_root / "reference_split_daily_link_candidates.parquet", artifacts)

    split_1m_link_candidates = build_reference_split_1m_link_candidates(split_market_link_candidates)
    save_artifact(split_1m_link_candidates, cfg.cache_root / "reference_split_1m_link_candidates.parquet", artifacts)

    event_halt_link_candidates = build_reference_event_halt_link_candidates(events_exploded, halts_event_index)
    save_artifact(event_halt_link_candidates, cfg.cache_root / "reference_event_halt_link_candidates.parquet", artifacts)

    event_quotes_link_candidates = build_reference_event_quotes_link_candidates(events_exploded)
    save_artifact(event_quotes_link_candidates, cfg.cache_root / "reference_event_quotes_link_candidates.parquet", artifacts)

    causal_alignment_summary = build_reference_causal_alignment_summary(
        overview_market_identity_links,
        split_market_link_candidates,
        event_halt_link_candidates,
        split_daily_link_candidates,
        split_1m_link_candidates,
        event_quotes_link_candidates,
    )
    save_artifact(causal_alignment_summary, cfg.cache_root / "reference_causal_alignment_summary.parquet", artifacts)

    manifest = build_manifest(cfg, artifacts, started_at)
    write_json(cfg.cache_root / "manifest.json", manifest)
    return manifest


def parse_args() -> BuildConfig:
    parser = argparse.ArgumentParser(description="Build reference audit artifacts")
    parser.add_argument("--reference-root", type=Path, default=REFERENCE_ROOT)
    parser.add_argument("--cache-root", type=Path, default=CACHE_ROOT)
    parser.add_argument("--lt1b-universe-path", type=Path, default=LT1B_UNIVERSE_PATH)
    parser.add_argument("--market-universe-path", type=Path, default=MARKET_UNIVERSE_PATH)
    parser.add_argument("--sample-files-per-dataset", type=int, default=3)
    args = parser.parse_args()
    return BuildConfig(
        reference_root=args.reference_root,
        cache_root=args.cache_root,
        lt1b_universe_path=args.lt1b_universe_path,
        market_universe_path=args.market_universe_path,
        sample_files_per_dataset=args.sample_files_per_dataset,
    )


def main() -> None:
    cfg = parse_args()
    manifest = build_reference_audit_artifacts(cfg)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
