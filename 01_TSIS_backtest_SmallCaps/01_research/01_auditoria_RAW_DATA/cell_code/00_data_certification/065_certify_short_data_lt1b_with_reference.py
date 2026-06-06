from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import polars as pl
import pyarrow.parquet as pq


SHORT_INTEREST_REQUIRED = [
    "settlement_date",
    "ticker",
    "short_interest",
    "avg_daily_volume",
    "days_to_cover",
]

SHORT_VOLUME_REQUIRED = [
    "ticker",
    "date",
    "total_volume",
    "short_volume",
    "exempt_volume",
    "non_exempt_volume",
    "short_volume_ratio",
    "nyse_short_volume",
    "nyse_short_volume_exempt",
    "nasdaq_carteret_short_volume",
    "nasdaq_carteret_short_volume_exempt",
    "nasdaq_chicago_short_volume",
    "nasdaq_chicago_short_volume_exempt",
    "adf_short_volume",
    "adf_short_volume_exempt",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = (
            Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\short_data_certification")
            / f"{stamp}_certify_short_data_lt1b_with_reference"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def normalize_ticker(series: pd.Series) -> pd.Series:
    return series.astype(str).str.upper().str.strip()


def load_universe(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path).copy()
    required = {"ticker", "first_seen_date", "last_observed_date", "status_rebuilt", "classification_1b"}
    missing = required.difference(df.columns)
    if missing:
        raise RuntimeError(f"Universe parquet missing required columns: {sorted(missing)}")
    df["ticker"] = normalize_ticker(df["ticker"])
    df = df[df["ticker"] != ""].copy()
    df = df.drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)
    return df


def load_entity_reuse_counts(panel_path: str, tickers: list[str]) -> pd.DataFrame:
    tickers_df = pl.DataFrame({"ticker": tickers})
    reuse = (
        pl.scan_parquet(panel_path)
        .select(
            [
                pl.col("ticker").cast(pl.Utf8).str.to_uppercase().str.strip_chars().alias("ticker"),
                pl.col("entity_id").cast(pl.Utf8).alias("entity_id"),
                pl.col("snapshot_date"),
            ]
        )
        .join(tickers_df.lazy(), on="ticker", how="inner")
        .group_by("ticker")
        .agg(
            [
                pl.col("entity_id").n_unique().alias("entity_id_nunique"),
                pl.col("snapshot_date").min().alias("panel_min_date"),
                pl.col("snapshot_date").max().alias("panel_max_date"),
            ]
        )
        .collect()
        .to_pandas()
    )
    reuse["ticker"] = normalize_ticker(reuse["ticker"])
    return reuse


def file_inventory(root: Path) -> pd.DataFrame:
    records = []
    if not root.exists():
        return pd.DataFrame(columns=["ticker", "file_path", "file_size_bytes"])
    for p in sorted(root.glob("*.parquet")):
        records.append(
            {
                "ticker": p.stem.upper(),
                "file_path": str(p),
                "file_size_bytes": int(p.stat().st_size),
            }
        )
    return pd.DataFrame(records)


def read_single_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def detect_reference_file(root: Path, ticker: str, prefix: str) -> Path | None:
    d = root / f"ticker={ticker}"
    if not d.exists():
        return None
    matches = sorted(d.glob(f"{prefix}_*.parquet"))
    return matches[0] if matches else None


def build_reference_file_maps(reference_root: Path, dataset: str, prefix: str) -> dict[str, Path]:
    root = reference_root / dataset
    out: dict[str, Path] = {}
    if not root.exists():
        return out
    for d in root.glob("ticker=*"):
        if not d.is_dir():
            continue
        ticker = d.name.split("=", 1)[1].upper()
        matches = sorted(d.glob(f"{prefix}_*.parquet"))
        if matches:
            out[ticker] = matches[0]
    return out


def reference_summary(
    ticker: str,
    overview_map: dict[str, Path],
    events_map: dict[str, Path],
    splits_map: dict[str, Path],
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "overview_file_present": False,
        "overview_file_path": None,
        "overview_rows": 0,
        "overview_columns_json": None,
        "overview_asof_date": None,
        "events_file_present": False,
        "events_file_path": None,
        "events_rows": 0,
        "events_columns_json": None,
        "events_date_min": None,
        "events_date_max": None,
        "events_types_json": None,
        "splits_file_present": False,
        "splits_file_path": None,
        "splits_rows": 0,
        "splits_columns_json": None,
        "splits_execution_date_min": None,
        "splits_execution_date_max": None,
    }

    overview_file = overview_map.get(ticker)
    if overview_file:
        df = read_single_parquet(overview_file)
        out["overview_file_present"] = True
        out["overview_file_path"] = str(overview_file)
        out["overview_rows"] = int(len(df))
        out["overview_columns_json"] = json.dumps(df.columns.tolist())
        if "date" in df.columns and len(df):
            s = pd.to_datetime(df["date"], errors="coerce")
            if s.notna().any():
                out["overview_asof_date"] = s.dropna().max().date().isoformat()

    events_file = events_map.get(ticker)
    if events_file:
        df = read_single_parquet(events_file)
        out["events_file_present"] = True
        out["events_file_path"] = str(events_file)
        out["events_rows"] = int(len(df))
        out["events_columns_json"] = json.dumps(df.columns.tolist())
        if "date" in df.columns and len(df):
            s = pd.to_datetime(df["date"], errors="coerce")
            if s.notna().any():
                out["events_date_min"] = s.dropna().min().date().isoformat()
                out["events_date_max"] = s.dropna().max().date().isoformat()
        event_type_col = None
        for c in ["event_type", "type"]:
            if c in df.columns:
                event_type_col = c
                break
        if event_type_col:
            vals = sorted({str(x) for x in df[event_type_col].dropna().tolist()})
            out["events_types_json"] = json.dumps(vals)

    splits_file = splits_map.get(ticker)
    if splits_file:
        df = read_single_parquet(splits_file)
        out["splits_file_present"] = True
        out["splits_file_path"] = str(splits_file)
        out["splits_rows"] = int(len(df))
        out["splits_columns_json"] = json.dumps(df.columns.tolist())
        date_col = next((c for c in ["execution_date", "ex_date", "date"] if c in df.columns), None)
        if date_col:
            s = pd.to_datetime(df[date_col], errors="coerce")
            if s.notna().any():
                out["splits_execution_date_min"] = s.dropna().min().date().isoformat()
                out["splits_execution_date_max"] = s.dropna().max().date().isoformat()
    return out


def audit_short_dataset(
    dataset_name: str,
    dataset_root: Path,
    date_col: str,
    required_columns: list[str],
    universe: pd.DataFrame,
) -> pd.DataFrame:
    inventory = file_inventory(dataset_root)
    file_map = {row["ticker"]: row for row in inventory.to_dict(orient="records")}
    rows = []
    for row in universe.itertuples(index=False):
        ticker = row.ticker
        file_meta = file_map.get(ticker)
        out = {
            "ticker": ticker,
            f"{dataset_name}_file_present": file_meta is not None,
            f"{dataset_name}_file_path": file_meta["file_path"] if file_meta else None,
            f"{dataset_name}_rows": 0,
            f"{dataset_name}_date_min": pd.NaT,
            f"{dataset_name}_date_max": pd.NaT,
            f"{dataset_name}_rows_before_first_seen": 0,
            f"{dataset_name}_rows_after_last_observed": 0,
            f"{dataset_name}_null_date_rows": 0,
            f"{dataset_name}_duplicate_date_rows": 0,
            f"{dataset_name}_required_columns_ok": False,
            f"{dataset_name}_missing_required_columns_json": None,
            f"{dataset_name}_ticker_values_match_filename": None,
        }
        if not file_meta:
            rows.append(out)
            continue
        file_path = Path(file_meta["file_path"])
        schema = pq.read_schema(file_path)
        cols = list(schema.names)
        missing = [c for c in required_columns if c not in cols]
        out[f"{dataset_name}_required_columns_ok"] = len(missing) == 0
        out[f"{dataset_name}_missing_required_columns_json"] = json.dumps(missing)
        read_cols = [c for c in [date_col, "ticker"] if c in cols]
        df = pq.read_table(file_path, columns=read_cols).to_pandas()
        if "ticker" in df.columns:
            ticker_vals = sorted({str(x).strip().upper() for x in df["ticker"].dropna().tolist() if str(x).strip()})
            out[f"{dataset_name}_ticker_values_match_filename"] = True if len(ticker_vals) == 0 else (ticker_vals == [ticker])
        if date_col in df.columns:
            s = pd.to_datetime(df[date_col], errors="coerce")
            out[f"{dataset_name}_rows"] = int(len(s))
            out[f"{dataset_name}_null_date_rows"] = int(s.isna().sum())
            valid = s.dropna()
            if not valid.empty:
                out[f"{dataset_name}_date_min"] = valid.min()
                out[f"{dataset_name}_date_max"] = valid.max()
                out[f"{dataset_name}_duplicate_date_rows"] = int(valid.duplicated().sum())
                out[f"{dataset_name}_rows_before_first_seen"] = int((valid < pd.Timestamp(row.first_seen_date)).sum())
                out[f"{dataset_name}_rows_after_last_observed"] = int((valid > pd.Timestamp(row.last_observed_date)).sum())
        rows.append(out)
    return pd.DataFrame(rows)


def classify_certification_status(row: pd.Series) -> tuple[str, str]:
    si_present = bool(row.get("short_interest_file_present", False))
    sv_present = bool(row.get("short_volume_file_present", False))
    if (not si_present) and (not sv_present):
        return "MISSING_DATA", "missing_short_interest_and_short_volume"

    schema_fail = (
        (si_present and not bool(row.get("short_interest_required_columns_ok", False)))
        or (sv_present and not bool(row.get("short_volume_required_columns_ok", False)))
    )
    if schema_fail:
        return "QUARANTINE_HIGH_RISK_MIX", "schema_failure_in_short_dataset"

    ticker_fail = (
        (si_present and row.get("short_interest_ticker_values_match_filename") is False)
        or (sv_present and row.get("short_volume_ticker_values_match_filename") is False)
    )
    if ticker_fail:
        return "QUARANTINE_HIGH_RISK_MIX", "ticker_column_mismatch_vs_filename"

    outside_any = (
        int(row.get("short_interest_rows_before_first_seen", 0)) > 0
        or int(row.get("short_interest_rows_after_last_observed", 0)) > 0
        or int(row.get("short_volume_rows_before_first_seen", 0)) > 0
        or int(row.get("short_volume_rows_after_last_observed", 0)) > 0
    )
    entity_n = int(row.get("entity_id_nunique", 0))
    events_present = bool(row.get("events_file_present", False))
    splits_present = bool(row.get("splits_file_present", False))

    if outside_any and entity_n > 1:
        if events_present or splits_present:
            return "REVIEW_TICKER_REUSE", "outside_window_with_multi_entity_and_reference_context"
        return "QUARANTINE_HIGH_RISK_MIX", "outside_window_with_multi_entity_without_reference_context"

    if outside_any:
        return "REVIEW_REFERENCE_CONFLICT", "outside_window_but_single_entity"

    if entity_n > 1:
        return "CERTIFIED_OK_WITH_LIMITED_WINDOW", "multi_entity_ticker_but_short_data_within_current_pti_window"

    if si_present and sv_present:
        return "CERTIFIED_OK", "both_short_datasets_present_and_in_window"

    return "CERTIFIED_OK_WITH_LIMITED_WINDOW", "partial_short_data_present_but_in_window"


def derive_certified_window(row: pd.Series) -> tuple[str | None, str | None]:
    dates_min = []
    dates_max = []
    for col in ["short_interest_date_min", "short_volume_date_min"]:
        val = row.get(col)
        if pd.notna(val):
            dates_min.append(pd.Timestamp(val))
    for col in ["short_interest_date_max", "short_volume_date_max"]:
        val = row.get(col)
        if pd.notna(val):
            dates_max.append(pd.Timestamp(val))

    base_start = pd.Timestamp(row["first_seen_date"])
    base_end = pd.Timestamp(row["last_observed_date"])
    if dates_min:
        base_start = max(base_start, min(dates_min))
    if dates_max:
        base_end = min(base_end, max(dates_max))
    if base_end < base_start:
        return None, None
    return base_start.date().isoformat(), base_end.date().isoformat()


def write_table(df: pd.DataFrame, parquet_path: Path, csv_path: Path) -> None:
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)


def main() -> None:
    ap = argparse.ArgumentParser(description="Certify LT<1B short data using short files plus reference overview/events/splits")
    ap.add_argument(
        "--universe-parquet",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet",
    )
    ap.add_argument(
        "--panel-parquet",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_panel_pti",
    )
    ap.add_argument("--short-root", default=r"C:\TSIS_Data\data\short")
    ap.add_argument("--reference-root", default=r"D:\reference")
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    universe = load_universe(Path(args.universe_parquet))
    reuse = load_entity_reuse_counts(args.panel_parquet, universe["ticker"].tolist())

    short_interest = audit_short_dataset(
        "short_interest",
        Path(args.short_root) / "short_interest",
        "settlement_date",
        SHORT_INTEREST_REQUIRED,
        universe,
    )
    short_volume = audit_short_dataset(
        "short_volume",
        Path(args.short_root) / "short_volume",
        "date",
        SHORT_VOLUME_REQUIRED,
        universe,
    )

    ref_rows = []
    reference_root = Path(args.reference_root)
    overview_map = build_reference_file_maps(reference_root, "overview", "overview")
    events_map = build_reference_file_maps(reference_root, "events", "events")
    splits_map = build_reference_file_maps(reference_root, "splits", "splits")
    for ticker in universe["ticker"].tolist():
        rec = {"ticker": ticker}
        rec.update(reference_summary(ticker, overview_map, events_map, splits_map))
        ref_rows.append(rec)
    refs = pd.DataFrame(ref_rows)

    cert = universe.merge(reuse, on="ticker", how="left")
    cert = cert.merge(short_interest, on="ticker", how="left")
    cert = cert.merge(short_volume, on="ticker", how="left")
    cert = cert.merge(refs, on="ticker", how="left")
    cert["entity_id_nunique"] = cert["entity_id_nunique"].fillna(0).astype(int)

    statuses = cert.apply(classify_certification_status, axis=1, result_type="expand")
    cert["certification_status"] = statuses[0]
    cert["certification_reason"] = statuses[1]

    windows = cert.apply(derive_certified_window, axis=1, result_type="expand")
    cert["certified_date_start"] = windows[0]
    cert["certified_date_end"] = windows[1]

    certified_ok = cert.loc[cert["certification_status"] == "CERTIFIED_OK"].copy()
    certified_limited = cert.loc[cert["certification_status"] == "CERTIFIED_OK_WITH_LIMITED_WINDOW"].copy()
    review_reuse = cert.loc[cert["certification_status"] == "REVIEW_TICKER_REUSE"].copy()
    review_reference = cert.loc[cert["certification_status"] == "REVIEW_REFERENCE_CONFLICT"].copy()
    missing_data = cert.loc[cert["certification_status"] == "MISSING_DATA"].copy()
    quarantine = cert.loc[cert["certification_status"] == "QUARANTINE_HIGH_RISK_MIX"].copy()

    cert_parquet = outdir / "short_data_certification_by_ticker.parquet"
    cert_csv = outdir / "short_data_certification_by_ticker.csv"
    ok_parquet = outdir / "short_data_certified_ok.parquet"
    ok_csv = outdir / "short_data_certified_ok.csv"
    limited_parquet = outdir / "short_data_certified_ok_with_limited_window.parquet"
    limited_csv = outdir / "short_data_certified_ok_with_limited_window.csv"
    reuse_parquet = outdir / "short_data_review_ticker_reuse.parquet"
    reuse_csv = outdir / "short_data_review_ticker_reuse.csv"
    ref_parquet = outdir / "short_data_review_reference_conflict.parquet"
    ref_csv = outdir / "short_data_review_reference_conflict.csv"
    missing_parquet = outdir / "short_data_missing_data.parquet"
    missing_csv = outdir / "short_data_missing_data.csv"
    quarantine_parquet = outdir / "short_data_quarantine_high_risk_mix.parquet"
    quarantine_csv = outdir / "short_data_quarantine_high_risk_mix.csv"
    summary_json = outdir / "short_data_certification_summary.json"

    write_table(cert, cert_parquet, cert_csv)
    write_table(certified_ok, ok_parquet, ok_csv)
    write_table(certified_limited, limited_parquet, limited_csv)
    write_table(review_reuse, reuse_parquet, reuse_csv)
    write_table(review_reference, ref_parquet, ref_csv)
    write_table(missing_data, missing_parquet, missing_csv)
    write_table(quarantine, quarantine_parquet, quarantine_csv)

    summary = {
        "certified_at_utc": utc_now(),
        "inputs": {
            "universe_parquet": str(args.universe_parquet),
            "panel_parquet": str(args.panel_parquet),
            "short_root": str(args.short_root),
            "reference_root": str(args.reference_root),
        },
        "universe_tickers": int(len(cert)),
        "status_counts": cert["certification_status"].value_counts(dropna=False).to_dict(),
        "entity_reuse_counts": cert["entity_id_nunique"].value_counts(dropna=False).sort_index().to_dict(),
        "outputs": {
            "certification_parquet": str(cert_parquet),
            "certification_csv": str(cert_csv),
            "certified_ok_parquet": str(ok_parquet),
            "certified_ok_with_limited_window_parquet": str(limited_parquet),
            "review_ticker_reuse_parquet": str(reuse_parquet),
            "review_reference_conflict_parquet": str(ref_parquet),
            "missing_data_parquet": str(missing_parquet),
            "quarantine_parquet": str(quarantine_parquet),
            "summary_json": str(summary_json),
        },
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
