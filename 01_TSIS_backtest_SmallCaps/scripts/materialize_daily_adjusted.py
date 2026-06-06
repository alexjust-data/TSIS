from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data import apply_adjusted_proxy_view, apply_adjusted_view


@dataclass(frozen=True)
class MaterializationConfig:
    daily_root: Path
    splits_root: Path
    dividends_root: Path
    output_root: Path
    overwrite: bool


def _iter_ticker_dirs(root: Path, tickers: set[str] | None = None) -> Iterable[Path]:
    for p in sorted(root.glob("ticker=*")):
        if not p.is_dir():
            continue
        ticker = p.name.replace("ticker=", "", 1).upper()
        if tickers and ticker not in tickers:
            continue
        yield p


def _find_action_file(root: Path, kind: str, ticker: str) -> Path | None:
    p = root / f"ticker={ticker}" / f"{kind}_{ticker}.parquet"
    return p if p.exists() else None


def _load_optional_parquet(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    if "_empty" in df.columns and len(df) and bool(df["_empty"].iloc[0]) is True:
        return pd.DataFrame()
    return df


def _iter_daily_files(ticker_dir: Path) -> Iterable[Path]:
    yield from sorted(ticker_dir.rglob("*.parquet"))


def _output_path(output_root: Path, daily_root: Path, src_path: Path) -> Path:
    rel = src_path.relative_to(daily_root)
    stem = src_path.stem
    return output_root / rel.parent / f"{stem}_adjusted.parquet"


def materialize_ticker(
    ticker_dir: Path,
    cfg: MaterializationConfig,
) -> dict[str, int | str]:
    ticker = ticker_dir.name.replace("ticker=", "", 1).upper()
    splits = _load_optional_parquet(_find_action_file(cfg.splits_root, "splits", ticker))
    dividends = _load_optional_parquet(_find_action_file(cfg.dividends_root, "dividends", ticker))

    files_seen = 0
    files_written = 0
    rows_written = 0

    for src_path in _iter_daily_files(ticker_dir):
        files_seen += 1
        out_path = _output_path(cfg.output_root, cfg.daily_root, src_path)
        if out_path.exists() and not cfg.overwrite:
            continue

        df = pd.read_parquet(src_path).copy()
        if df.empty:
            continue

        adjusted_df, _ = apply_adjusted_view(
            df,
            splits=splits,
            dividends=dividends,
            date_col="date",
            price_cols=("o", "h", "l", "c"),
        )
        adjusted_df, _ = apply_adjusted_proxy_view(
            adjusted_df,
            dividends=dividends,
            date_col="date",
            price_cols=("o", "h", "l", "c"),
        )

        adjusted_df["materialized_price_view"] = "daily_adjusted_v0_1"
        adjusted_df["source_daily_file"] = str(src_path)
        adjusted_df["source_splits_file"] = str(_find_action_file(cfg.splits_root, "splits", ticker) or "")
        adjusted_df["source_dividends_file"] = str(_find_action_file(cfg.dividends_root, "dividends", ticker) or "")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        adjusted_df.to_parquet(out_path, index=False)
        files_written += 1
        rows_written += int(len(adjusted_df))

    return {
        "ticker": ticker,
        "files_seen": files_seen,
        "files_written": files_written,
        "rows_written": rows_written,
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa la primera capa `daily_adjusted` del modulo 01.")
    ap.add_argument("--daily-root", default=r"D:\ohlcv_daily")
    ap.add_argument("--splits-root", default=r"C:\TSIS_Data\data\additional\corporate_actions\splits")
    ap.add_argument("--dividends-root", default=r"C:\TSIS_Data\data\additional\corporate_actions\dividends")
    ap.add_argument("--output-root", required=True)
    ap.add_argument("--tickers", nargs="*", default=None, help="Lista opcional de tickers a materializar.")
    ap.add_argument("--limit-tickers", type=int, default=None)
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    tickers = {t.upper() for t in args.tickers} if args.tickers else None
    cfg = MaterializationConfig(
        daily_root=Path(args.daily_root),
        splits_root=Path(args.splits_root),
        dividends_root=Path(args.dividends_root),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )

    ticker_dirs = list(_iter_ticker_dirs(cfg.daily_root, tickers=tickers))
    if args.limit_tickers is not None:
        ticker_dirs = ticker_dirs[: int(args.limit_tickers)]

    cfg.output_root.mkdir(parents=True, exist_ok=True)
    summary_path = cfg.output_root / "_materialization_summary.csv"
    existing_summary = pd.read_csv(summary_path) if summary_path.exists() else pd.DataFrame()
    completed_tickers: set[str] = set()
    if not cfg.overwrite and not existing_summary.empty and "ticker" in existing_summary.columns:
        completed_tickers = set(existing_summary["ticker"].astype(str).str.upper())
        ticker_dirs = [
            p
            for p in ticker_dirs
            if p.name.replace("ticker=", "", 1).upper() not in completed_tickers
        ]
    rows: list[dict[str, int | str]] = (
        existing_summary.to_dict(orient="records") if not existing_summary.empty else []
    )
    for ticker_dir in ticker_dirs:
        row = materialize_ticker(ticker_dir, cfg)
        rows.append(row)
        pd.DataFrame(rows).to_csv(summary_path, index=False)
        print(
            f"[daily_adjusted] ticker={row['ticker']} "
            f"files_seen={row['files_seen']} "
            f"files_written={row['files_written']} "
            f"rows_written={row['rows_written']}"
        )

    if rows:
        summary = pd.DataFrame(rows)
        summary.to_csv(summary_path, index=False)
        print(summary.to_string(index=False))
    else:
        print("No ticker directories selected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
