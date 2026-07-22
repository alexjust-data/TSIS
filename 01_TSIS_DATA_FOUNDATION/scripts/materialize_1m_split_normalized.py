from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data import apply_split_normalized_view


@dataclass(frozen=True)
class MaterializationConfig:
    minute_root: Path
    splits_root: Path
    output_root: Path
    overwrite: bool


def _find_split_file(root: Path, ticker: str) -> Path | None:
    p = root / f"ticker={ticker}" / f"splits_{ticker}.parquet"
    return p if p.exists() else None


def _load_optional_parquet(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    if "_empty" in df.columns and len(df) and bool(df["_empty"].iloc[0]) is True:
        return pd.DataFrame()
    return df


def _source_path(root: Path, ticker: str, year: int, month: int) -> Path:
    return (
        root
        / f"ticker={ticker}"
        / f"year={year}"
        / f"month={month:02d}"
        / f"minute_aggs_{ticker}_{year}_{month:02d}.parquet"
    )


def _output_path(root: Path, ticker: str, year: int, month: int) -> Path:
    return (
        root
        / f"ticker={ticker}"
        / f"year={year}"
        / f"month={month:02d}"
        / f"minute_aggs_{ticker}_{year}_{month:02d}_split_normalized.parquet"
    )


def materialize_case(row: pd.Series, cfg: MaterializationConfig) -> dict[str, int | str | float]:
    ticker = str(row["ticker"]).upper()
    year = int(row["year"])
    month = int(row["month"])
    role = str(row["role"])
    event_type = str(row["event_type"])
    event_date = "" if pd.isna(row.get("event_date")) else str(row.get("event_date"))

    src_path = _source_path(cfg.minute_root, ticker, year, month)
    out_path = _output_path(cfg.output_root, ticker, year, month)
    splits_path = _find_split_file(cfg.splits_root, ticker)
    splits = _load_optional_parquet(splits_path)

    if out_path.exists() and not cfg.overwrite:
        out = pd.read_parquet(out_path, columns=["future_split_factor"])
        non1 = int((pd.to_numeric(out["future_split_factor"], errors="coerce") != 1.0).sum())
        return {
            "ticker": ticker,
            "year": year,
            "month": month,
            "role": role,
            "event_type": event_type,
            "event_date": event_date,
            "rows_written": int(len(out)),
            "split_non1_rows": non1,
            "output_file": str(out_path),
        }

    df = pd.read_parquet(src_path).copy()
    out, _ = apply_split_normalized_view(
        df,
        splits=splits,
        date_col="date",
        price_cols=("o", "h", "l", "c", "vw"),
    )
    out["materialized_price_view"] = "1m_split_normalized_v0_1"
    out["source_1m_file"] = str(src_path)
    out["source_splits_file"] = str(splits_path or "")
    out["pilot_role"] = role
    out["pilot_event_type"] = event_type
    out["pilot_event_date"] = event_date

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, index=False)

    non1 = int((pd.to_numeric(out["future_split_factor"], errors="coerce") != 1.0).sum())
    return {
        "ticker": ticker,
        "year": year,
        "month": month,
        "role": role,
        "event_type": event_type,
        "event_date": event_date,
        "rows_written": int(len(out)),
        "split_non1_rows": non1,
        "output_file": str(out_path),
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa la primera capa `1m_split_normalized` del modulo 01.")
    ap.add_argument("--minute-root", default=r"D:\ohlcv_1m")
    ap.add_argument("--splits-root", default=r"C:\TSIS_Data\data\additional\corporate_actions\splits")
    ap.add_argument("--output-root", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg = MaterializationConfig(
        minute_root=Path(args.minute_root),
        splits_root=Path(args.splits_root),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )
    manifest = pd.read_csv(args.manifest)

    rows: list[dict[str, int | str | float]] = []
    for _, row in manifest.iterrows():
        rows.append(materialize_case(row, cfg))

    summary = pd.DataFrame(rows)
    cfg.output_root.mkdir(parents=True, exist_ok=True)
    summary.to_csv(cfg.output_root / "_split_normalized_materialization_summary.csv", index=False)
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
