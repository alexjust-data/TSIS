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
            / f"{stamp}_cross_lt1b_missing_vs_universe_audit"
        )
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def load_lt1b_missing(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"LT1B missing parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError(f"Missing ticker column in {path}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    return df[df["ticker"] != ""].drop_duplicates(subset=["ticker"], keep="first").reset_index(drop=True)


def load_missing_audit(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing-years audit parquet not found: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "missing_year", "classification"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"Missing required columns in {path}: {required}")
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["missing_year"] = pd.to_numeric(df["missing_year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["ticker", "missing_year"]).copy()
    df["missing_year"] = df["missing_year"].astype(int)
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description="Cross LT1B missing-complete-daily tickers vs universe-calendar missing-years audit")
    ap.add_argument("--lt1b-missing-parquet", required=True)
    ap.add_argument("--missing-audit-parquet", required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    lt1b_missing = load_lt1b_missing(Path(args.lt1b_missing_parquet))
    missing_audit = load_missing_audit(Path(args.missing_audit_parquet))

    merged = lt1b_missing.merge(missing_audit, on="ticker", how="left")

    by_ticker = (
        merged.groupby("ticker", dropna=False)
        .agg(
            missing_year_rows=("missing_year", "size"),
            unexpected_rows=("classification", lambda s: int(s.isin(["unexpected_missing", "unexpected_missing_ambiguous_ticker", "unexpected_missing_calendar_unavailable"]).sum())),
            unexpected_clean_rows=("classification", lambda s: int((s == "unexpected_missing").sum())),
            unexpected_ambiguous_rows=("classification", lambda s: int((s == "unexpected_missing_ambiguous_ticker").sum())),
            likely_valid_rows=("classification", lambda s: int((s == "likely_valid_gap_outside_reference_window").sum())),
            classifications=("classification", lambda s: sorted(set(str(x) for x in s.dropna().tolist()))),
        )
        .reset_index()
    )

    def status(row: pd.Series) -> str:
        if int(row["unexpected_clean_rows"]) > 0:
            return "REALLY_PROBLEMATIC_UNEXPECTED"
        if int(row["unexpected_ambiguous_rows"]) > 0:
            return "AMBIGUOUS_REVIEW"
        if int(row["likely_valid_rows"]) > 0 and int(row["unexpected_rows"]) == 0:
            return "LIKELY_VALID_GAP_ONLY"
        return "UNCLASSIFIED"

    by_ticker["lt1b_daily_gap_status"] = by_ticker.apply(status, axis=1)

    really_problematic = by_ticker[by_ticker["lt1b_daily_gap_status"] == "REALLY_PROBLEMATIC_UNEXPECTED"].copy()
    ambiguous = by_ticker[by_ticker["lt1b_daily_gap_status"] == "AMBIGUOUS_REVIEW"].copy()
    likely_valid = by_ticker[by_ticker["lt1b_daily_gap_status"] == "LIKELY_VALID_GAP_ONLY"].copy()

    summary = {
        "audited_at_utc": utc_now(),
        "lt1b_missing_tickers_input": int(lt1b_missing["ticker"].nunique()),
        "really_problematic_tickers": int(really_problematic["ticker"].nunique()),
        "ambiguous_review_tickers": int(ambiguous["ticker"].nunique()),
        "likely_valid_gap_only_tickers": int(likely_valid["ticker"].nunique()),
        "status_counts": by_ticker["lt1b_daily_gap_status"].value_counts(dropna=False).to_dict(),
        "inputs": {
            "lt1b_missing_parquet": str(args.lt1b_missing_parquet),
            "missing_audit_parquet": str(args.missing_audit_parquet),
        },
        "outdir": str(outdir),
    }

    all_parquet = outdir / "lt1b_missing_vs_universe_audit.parquet"
    all_csv = outdir / "lt1b_missing_vs_universe_audit.csv"
    problematic_parquet = outdir / "lt1b_really_problematic_unexpected.parquet"
    problematic_csv = outdir / "lt1b_really_problematic_unexpected.csv"
    ambiguous_parquet = outdir / "lt1b_ambiguous_review.parquet"
    ambiguous_csv = outdir / "lt1b_ambiguous_review.csv"
    likely_valid_parquet = outdir / "lt1b_likely_valid_gap_only.parquet"
    likely_valid_csv = outdir / "lt1b_likely_valid_gap_only.csv"
    summary_json = outdir / "lt1b_missing_vs_universe_audit_summary.json"

    by_ticker.to_parquet(all_parquet, index=False)
    by_ticker.to_csv(all_csv, index=False)
    really_problematic.to_parquet(problematic_parquet, index=False)
    really_problematic.to_csv(problematic_csv, index=False)
    ambiguous.to_parquet(ambiguous_parquet, index=False)
    ambiguous.to_csv(ambiguous_csv, index=False)
    likely_valid.to_parquet(likely_valid_parquet, index=False)
    likely_valid.to_csv(likely_valid_csv, index=False)
    summary_json.write_text(
        json.dumps(
            {
                **summary,
                "outputs": {
                    "all_parquet": str(all_parquet),
                    "all_csv": str(all_csv),
                    "problematic_parquet": str(problematic_parquet),
                    "problematic_csv": str(problematic_csv),
                    "ambiguous_parquet": str(ambiguous_parquet),
                    "ambiguous_csv": str(ambiguous_csv),
                    "likely_valid_parquet": str(likely_valid_parquet),
                    "likely_valid_csv": str(likely_valid_csv),
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
                "outputs": {
                    "problematic_parquet": str(problematic_parquet),
                    "ambiguous_parquet": str(ambiguous_parquet),
                    "likely_valid_parquet": str(likely_valid_parquet),
                    "summary_json": str(summary_json),
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
