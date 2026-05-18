from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = (
            Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit")
            / f"{stamp}_daily_v2_span_contiguity"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def load_inventory(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Inventory parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns or "year" not in df.columns:
        raise RuntimeError("Inventory missing required columns: ticker/year")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["ticker", "year"]).copy()
    df["year"] = df["year"].astype(int)
    return df


def audit_ticker_span(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    rows: list[dict] = []

    for ticker, g in df.groupby("ticker", dropna=False):
        years = sorted(set(int(x) for x in g["year"].tolist()))
        start_year = int(min(years))
        end_year = int(max(years))
        expected_years = list(range(start_year, end_year + 1))
        missing_years = [y for y in expected_years if y not in years]

        rows.append(
            {
                "ticker": str(ticker),
                "files_observed": int(len(g)),
                "unique_years_observed": int(len(years)),
                "start_year_observed": start_year,
                "end_year_observed": end_year,
                "expected_years_in_span": int(len(expected_years)),
                "missing_years_in_span_count": int(len(missing_years)),
                "is_contiguous_span": bool(len(missing_years) == 0),
                "observed_years": years,
                "missing_years_in_span": missing_years,
                "task_keys": sorted(set(g["task_key"].astype(str).tolist())) if "task_key" in g.columns else [],
                "roots_present": sorted(set(g["root"].astype(str).tolist())) if "root" in g.columns else [],
            }
        )

    by_ticker = pd.DataFrame(rows).sort_values(
        ["missing_years_in_span_count", "ticker"], ascending=[False, True]
    ).reset_index(drop=True)

    missing_records: list[dict] = []
    for row in by_ticker.to_dict(orient="records"):
        for year in row["missing_years_in_span"]:
            missing_records.append(
                {
                    "ticker": row["ticker"],
                    "missing_year": int(year),
                    "start_year_observed": int(row["start_year_observed"]),
                    "end_year_observed": int(row["end_year_observed"]),
                }
            )
    missing_years_df = pd.DataFrame(missing_records).sort_values(
        ["ticker", "missing_year"], ascending=[True, True]
    ) if missing_records else pd.DataFrame(
        columns=["ticker", "missing_year", "start_year_observed", "end_year_observed"]
    )

    summary = {
        "audited_at_utc": utc_now(),
        "tickers_total": int(by_ticker["ticker"].nunique()),
        "ticker_year_files_total": int(len(df)),
        "contiguous_tickers": int(by_ticker["is_contiguous_span"].sum()),
        "non_contiguous_tickers": int((~by_ticker["is_contiguous_span"]).sum()),
        "pct_contiguous_tickers": round(
            100.0 * float(by_ticker["is_contiguous_span"].mean()) if len(by_ticker) else 0.0, 4
        ),
        "missing_years_total": int(by_ticker["missing_years_in_span_count"].sum()),
        "max_missing_years_for_one_ticker": int(by_ticker["missing_years_in_span_count"].max()) if len(by_ticker) else 0,
        "year_min_global": int(df["year"].min()) if len(df) else None,
        "year_max_global": int(df["year"].max()) if len(df) else None,
    }
    return by_ticker, missing_years_df, summary


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Audit per-ticker year-span contiguity for daily inventory"
    )
    ap.add_argument("--inventory-parquet", required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    inventory_parquet = Path(args.inventory_parquet)
    outdir = build_outdir(args.outdir)

    df = load_inventory(inventory_parquet)
    by_ticker, missing_years_df, summary = audit_ticker_span(df)

    by_ticker_parquet = outdir / "daily_file_span_audit_by_ticker.parquet"
    by_ticker_csv = outdir / "daily_file_span_audit_by_ticker.csv"
    missing_parquet = outdir / "daily_file_span_audit_missing_years.parquet"
    missing_csv = outdir / "daily_file_span_audit_missing_years.csv"
    summary_json = outdir / "daily_file_span_audit_summary.json"

    by_ticker.to_parquet(by_ticker_parquet, index=False)
    by_ticker.to_csv(by_ticker_csv, index=False)
    missing_years_df.to_parquet(missing_parquet, index=False)
    missing_years_df.to_csv(missing_csv, index=False)
    summary_json.write_text(
        json.dumps(
            {
                **summary,
                "inventory_parquet": str(inventory_parquet),
                "outdir": str(outdir),
                "outputs": {
                    "by_ticker_parquet": str(by_ticker_parquet),
                    "by_ticker_csv": str(by_ticker_csv),
                    "missing_years_parquet": str(missing_parquet),
                    "missing_years_csv": str(missing_csv),
                    "summary_json": str(summary_json),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                **summary,
                "inventory_parquet": str(inventory_parquet),
                "outdir": str(outdir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
