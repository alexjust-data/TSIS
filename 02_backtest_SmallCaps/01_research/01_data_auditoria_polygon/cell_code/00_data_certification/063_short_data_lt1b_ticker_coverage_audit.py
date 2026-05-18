from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

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
    "short_ratio",
    "exempt_ratio",
    "short_ratio_ma5",
    "short_ratio_change",
    "short_ratio_zscore",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = (
            Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\short_data_audit")
            / f"{stamp}_short_data_lt1b_ticker_coverage_audit"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def normalize_ticker(series: pd.Series) -> pd.Series:
    return series.astype(str).str.upper().str.strip()


def load_universe(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Universe parquet not found: {path}")
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
    if not root.exists():
        raise FileNotFoundError(f"Dataset root not found: {root}")
    records = []
    for p in sorted(root.glob("*.parquet")):
        records.append(
            {
                "ticker": p.stem.upper(),
                "file_path": str(p),
                "file_name": p.name,
                "file_size_bytes": int(p.stat().st_size),
            }
        )
    return pd.DataFrame(records)


def classify_risk_bucket(
    file_present: bool,
    entity_id_nunique: int,
    rows_before_first_seen: int,
    rows_after_last_observed: int,
) -> str:
    if not file_present:
        return "missing_file"
    outside = (rows_before_first_seen > 0) or (rows_after_last_observed > 0)
    if entity_id_nunique > 1 and outside:
        return "high_risk_possible_reuse_mix"
    if outside:
        return "outside_universe_window"
    if entity_id_nunique > 1:
        return "multi_entity_in_window"
    return "ok_single_entity_in_window"


def audit_dataset(
    dataset_name: str,
    dataset_root: Path,
    date_col: str,
    required_columns: list[str],
    universe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    inventory = file_inventory(dataset_root)
    file_map = {row["ticker"]: row for row in inventory.to_dict(orient="records")}
    extra = inventory.loc[~inventory["ticker"].isin(set(universe["ticker"]))].copy()

    rows = []
    for row in universe.itertuples(index=False):
        ticker = row.ticker
        file_meta = file_map.get(ticker)
        out = {
            "dataset": dataset_name,
            "ticker": ticker,
            "first_seen_date": row.first_seen_date,
            "last_observed_date": row.last_observed_date,
            "status_rebuilt": row.status_rebuilt,
            "classification_1b": row.classification_1b,
            "file_present": file_meta is not None,
            "file_path": file_meta["file_path"] if file_meta else None,
            "file_size_bytes": file_meta["file_size_bytes"] if file_meta else None,
            "rows": 0,
            "date_min": pd.NaT,
            "date_max": pd.NaT,
            "null_date_rows": 0,
            "duplicate_date_rows": 0,
            "rows_before_first_seen": 0,
            "rows_after_last_observed": 0,
            "required_columns_ok": False,
            "missing_required_columns": None,
            "columns_observed_json": None,
            "ticker_values_nunique": 0,
            "ticker_values_match_filename": None,
            "ticker_values_json": None,
        }
        if file_meta is None:
            rows.append(out)
            continue

        file_path = Path(file_meta["file_path"])
        schema = pq.read_schema(file_path)
        cols = list(schema.names)
        missing_required = [c for c in required_columns if c not in cols]
        out["required_columns_ok"] = len(missing_required) == 0
        out["missing_required_columns"] = json.dumps(missing_required)
        out["columns_observed_json"] = json.dumps(cols)

        read_cols = [c for c in [date_col, "ticker"] if c in cols]
        tbl = pq.read_table(file_path, columns=read_cols)
        df = tbl.to_pandas()

        if "ticker" in df.columns:
            ticker_vals = sorted({str(x).strip().upper() for x in df["ticker"].dropna().tolist() if str(x).strip() != ""})
            out["ticker_values_nunique"] = len(ticker_vals)
            out["ticker_values_match_filename"] = ticker_vals == [ticker]
            out["ticker_values_json"] = json.dumps(ticker_vals)
        else:
            out["ticker_values_match_filename"] = None

        if date_col in df.columns:
            ds = pd.to_datetime(df[date_col], errors="coerce")
            out["rows"] = int(len(ds))
            out["null_date_rows"] = int(ds.isna().sum())
            valid_dates = ds.dropna()
            if not valid_dates.empty:
                out["date_min"] = valid_dates.min()
                out["date_max"] = valid_dates.max()
                out["duplicate_date_rows"] = int(valid_dates.duplicated().sum())
                out["rows_before_first_seen"] = int((valid_dates < pd.Timestamp(row.first_seen_date)).sum())
                out["rows_after_last_observed"] = int((valid_dates > pd.Timestamp(row.last_observed_date)).sum())

        rows.append(out)

    audited = pd.DataFrame(rows)
    return audited, extra


def build_joined_summary(
    universe: pd.DataFrame,
    reuse: pd.DataFrame,
    short_interest: pd.DataFrame,
    short_volume: pd.DataFrame,
) -> pd.DataFrame:
    si = short_interest.rename(
        columns={
            "file_present": "short_interest_file_present",
            "rows": "short_interest_rows",
            "date_min": "short_interest_date_min",
            "date_max": "short_interest_date_max",
            "rows_before_first_seen": "short_interest_rows_before_first_seen",
            "rows_after_last_observed": "short_interest_rows_after_last_observed",
            "risk_bucket": "short_interest_risk_bucket",
            "required_columns_ok": "short_interest_required_columns_ok",
            "ticker_values_match_filename": "short_interest_ticker_values_match_filename",
            "duplicate_date_rows": "short_interest_duplicate_date_rows",
        }
    )[
        [
            "ticker",
            "short_interest_file_present",
            "short_interest_rows",
            "short_interest_date_min",
            "short_interest_date_max",
            "short_interest_rows_before_first_seen",
            "short_interest_rows_after_last_observed",
            "short_interest_risk_bucket",
            "short_interest_required_columns_ok",
            "short_interest_ticker_values_match_filename",
            "short_interest_duplicate_date_rows",
        ]
    ]

    sv = short_volume.rename(
        columns={
            "file_present": "short_volume_file_present",
            "rows": "short_volume_rows",
            "date_min": "short_volume_date_min",
            "date_max": "short_volume_date_max",
            "rows_before_first_seen": "short_volume_rows_before_first_seen",
            "rows_after_last_observed": "short_volume_rows_after_last_observed",
            "risk_bucket": "short_volume_risk_bucket",
            "required_columns_ok": "short_volume_required_columns_ok",
            "ticker_values_match_filename": "short_volume_ticker_values_match_filename",
            "duplicate_date_rows": "short_volume_duplicate_date_rows",
        }
    )[
        [
            "ticker",
            "short_volume_file_present",
            "short_volume_rows",
            "short_volume_date_min",
            "short_volume_date_max",
            "short_volume_rows_before_first_seen",
            "short_volume_rows_after_last_observed",
            "short_volume_risk_bucket",
            "short_volume_required_columns_ok",
            "short_volume_ticker_values_match_filename",
            "short_volume_duplicate_date_rows",
        ]
    ]

    joined = universe.merge(reuse, on="ticker", how="left")
    joined = joined.merge(si, on="ticker", how="left")
    joined = joined.merge(sv, on="ticker", how="left")
    joined["entity_id_nunique"] = joined["entity_id_nunique"].fillna(0).astype(int)
    joined["has_any_short_data"] = (
        joined["short_interest_file_present"].fillna(False).astype(bool)
        | joined["short_volume_file_present"].fillna(False).astype(bool)
    )
    joined["high_risk_possible_reuse_mix_any"] = (
        joined["short_interest_risk_bucket"].eq("high_risk_possible_reuse_mix")
        | joined["short_volume_risk_bucket"].eq("high_risk_possible_reuse_mix")
    )
    return joined


def attach_risk(audited: pd.DataFrame, reuse: pd.DataFrame) -> pd.DataFrame:
    out = audited.merge(reuse, on="ticker", how="left")
    out["entity_id_nunique"] = out["entity_id_nunique"].fillna(0).astype(int)
    out["risk_bucket"] = out.apply(
        lambda r: classify_risk_bucket(
            bool(r["file_present"]),
            int(r["entity_id_nunique"]),
            int(r["rows_before_first_seen"]),
            int(r["rows_after_last_observed"]),
        ),
        axis=1,
    )
    return out


def write_table(df: pd.DataFrame, parquet_path: Path, csv_path: Path) -> None:
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)


def main() -> None:
    ap = argparse.ArgumentParser(description="Audit short_data coverage for the complete LT<1B ticker universe")
    ap.add_argument(
        "--universe-parquet",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet",
    )
    ap.add_argument(
        "--panel-parquet",
        default=r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_panel_pti",
    )
    ap.add_argument("--short-root", default=r"C:\TSIS_Data\data\short_data")
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    universe = load_universe(Path(args.universe_parquet))
    reuse = load_entity_reuse_counts(args.panel_parquet, universe["ticker"].tolist())

    short_interest, short_interest_extra = audit_dataset(
        dataset_name="short_interest",
        dataset_root=Path(args.short_root) / "short_interest",
        date_col="settlement_date",
        required_columns=SHORT_INTEREST_REQUIRED,
        universe=universe,
    )
    short_volume, short_volume_extra = audit_dataset(
        dataset_name="short_volume",
        dataset_root=Path(args.short_root) / "short_volume",
        date_col="date",
        required_columns=SHORT_VOLUME_REQUIRED,
        universe=universe,
    )

    short_interest = attach_risk(short_interest, reuse)
    short_volume = attach_risk(short_volume, reuse)
    joined = build_joined_summary(universe, reuse, short_interest, short_volume)

    high_risk = joined.loc[joined["high_risk_possible_reuse_mix_any"]].copy()
    missing_any = joined.loc[
        (~joined["short_interest_file_present"].fillna(False))
        | (~joined["short_volume_file_present"].fillna(False))
    ].copy()

    si_parquet = outdir / "short_interest_lt1b_coverage_by_ticker.parquet"
    si_csv = outdir / "short_interest_lt1b_coverage_by_ticker.csv"
    sv_parquet = outdir / "short_volume_lt1b_coverage_by_ticker.parquet"
    sv_csv = outdir / "short_volume_lt1b_coverage_by_ticker.csv"
    joined_parquet = outdir / "short_data_lt1b_coverage_joined_by_ticker.parquet"
    joined_csv = outdir / "short_data_lt1b_coverage_joined_by_ticker.csv"
    high_risk_parquet = outdir / "short_data_lt1b_high_risk_possible_reuse_mix.parquet"
    high_risk_csv = outdir / "short_data_lt1b_high_risk_possible_reuse_mix.csv"
    missing_any_parquet = outdir / "short_data_lt1b_missing_any_dataset.parquet"
    missing_any_csv = outdir / "short_data_lt1b_missing_any_dataset.csv"
    si_extra_parquet = outdir / "short_interest_extra_files_outside_lt1b_universe.parquet"
    si_extra_csv = outdir / "short_interest_extra_files_outside_lt1b_universe.csv"
    sv_extra_parquet = outdir / "short_volume_extra_files_outside_lt1b_universe.parquet"
    sv_extra_csv = outdir / "short_volume_extra_files_outside_lt1b_universe.csv"
    summary_json = outdir / "short_data_lt1b_ticker_coverage_audit_summary.json"

    write_table(short_interest, si_parquet, si_csv)
    write_table(short_volume, sv_parquet, sv_csv)
    write_table(joined, joined_parquet, joined_csv)
    write_table(high_risk, high_risk_parquet, high_risk_csv)
    write_table(missing_any, missing_any_parquet, missing_any_csv)
    write_table(short_interest_extra, si_extra_parquet, si_extra_csv)
    write_table(short_volume_extra, sv_extra_parquet, sv_extra_csv)

    summary = {
        "audited_at_utc": utc_now(),
        "inputs": {
            "universe_parquet": str(args.universe_parquet),
            "panel_parquet": str(args.panel_parquet),
            "short_root": str(args.short_root),
        },
        "universe_tickers": int(len(universe)),
        "short_interest": {
            "files_present": int(short_interest["file_present"].sum()),
            "files_missing": int((~short_interest["file_present"]).sum()),
            "coverage_pct": round(100 * short_interest["file_present"].mean(), 3),
            "tickers_outside_window_any": int(
                ((short_interest["rows_before_first_seen"] > 0) | (short_interest["rows_after_last_observed"] > 0)).sum()
            ),
            "high_risk_possible_reuse_mix": int((short_interest["risk_bucket"] == "high_risk_possible_reuse_mix").sum()),
            "extra_files_outside_universe": int(len(short_interest_extra)),
            "risk_bucket_counts": short_interest["risk_bucket"].value_counts(dropna=False).to_dict(),
        },
        "short_volume": {
            "files_present": int(short_volume["file_present"].sum()),
            "files_missing": int((~short_volume["file_present"]).sum()),
            "coverage_pct": round(100 * short_volume["file_present"].mean(), 3),
            "tickers_outside_window_any": int(
                ((short_volume["rows_before_first_seen"] > 0) | (short_volume["rows_after_last_observed"] > 0)).sum()
            ),
            "high_risk_possible_reuse_mix": int((short_volume["risk_bucket"] == "high_risk_possible_reuse_mix").sum()),
            "extra_files_outside_universe": int(len(short_volume_extra)),
            "risk_bucket_counts": short_volume["risk_bucket"].value_counts(dropna=False).to_dict(),
        },
        "joined": {
            "tickers_with_any_short_data": int(joined["has_any_short_data"].sum()),
            "tickers_missing_any_dataset": int(len(missing_any)),
            "tickers_high_risk_possible_reuse_mix_any": int(len(high_risk)),
            "entity_reuse_counts": joined["entity_id_nunique"].value_counts(dropna=False).sort_index().to_dict(),
        },
        "expected_file_content": {
            "short_interest": {
                "unit": "one parquet per ticker",
                "required_columns": SHORT_INTEREST_REQUIRED,
                "expected_rows_semantics": "one row per settlement_date for the ticker; ticker column should match the filename",
            },
            "short_volume": {
                "unit": "one parquet per ticker",
                "required_columns": SHORT_VOLUME_REQUIRED,
                "expected_rows_semantics": "one row per trading date for the ticker; ticker column should match the filename",
            },
        },
        "outputs": {
            "short_interest_by_ticker_parquet": str(si_parquet),
            "short_interest_by_ticker_csv": str(si_csv),
            "short_volume_by_ticker_parquet": str(sv_parquet),
            "short_volume_by_ticker_csv": str(sv_csv),
            "joined_by_ticker_parquet": str(joined_parquet),
            "joined_by_ticker_csv": str(joined_csv),
            "high_risk_parquet": str(high_risk_parquet),
            "high_risk_csv": str(high_risk_csv),
            "missing_any_parquet": str(missing_any_parquet),
            "missing_any_csv": str(missing_any_csv),
            "short_interest_extra_parquet": str(si_extra_parquet),
            "short_interest_extra_csv": str(si_extra_csv),
            "short_volume_extra_parquet": str(sv_extra_parquet),
            "short_volume_extra_csv": str(sv_extra_csv),
            "summary_json": str(summary_json),
        },
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
