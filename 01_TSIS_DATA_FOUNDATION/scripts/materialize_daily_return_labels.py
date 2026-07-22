from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class LabelsConfig:
    adjusted_root: Path
    output_root: Path
    overwrite: bool
    horizons: tuple[int, ...]


def _iter_ticker_dirs(root: Path, tickers: set[str] | None = None) -> Iterable[Path]:
    for p in sorted(root.glob("ticker=*")):
        if not p.is_dir():
            continue
        ticker = p.name.replace("ticker=", "", 1).upper()
        if tickers and ticker not in tickers:
            continue
        yield p


def _iter_adjusted_files(ticker_dir: Path) -> Iterable[Path]:
    yield from sorted(ticker_dir.rglob("*_adjusted.parquet"))


def _output_path(output_root: Path, adjusted_root: Path, src_path: Path) -> Path:
    rel = src_path.relative_to(adjusted_root)
    stem = src_path.stem.replace("_adjusted", "_labels")
    return output_root / rel.parent / f"{stem}.parquet"


def _build_labels(df: pd.DataFrame, horizons: tuple[int, ...]) -> pd.DataFrame:
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.sort_values("date").reset_index(drop=True)
    close = pd.to_numeric(out["c_adjusted"], errors="coerce")
    for h in horizons:
        out[f"ret_{h}d"] = close.shift(-h) / close - 1.0
    return out


def materialize_ticker(ticker_dir: Path, cfg: LabelsConfig) -> dict[str, int | str]:
    ticker = ticker_dir.name.replace("ticker=", "", 1).upper()
    files_seen = 0
    files_written = 0
    rows_written = 0

    for src_path in _iter_adjusted_files(ticker_dir):
        files_seen += 1
        out_path = _output_path(cfg.output_root, cfg.adjusted_root, src_path)
        if out_path.exists() and not cfg.overwrite:
            continue

        df = pd.read_parquet(src_path).copy()
        if df.empty:
            continue
        if "c_adjusted" not in df.columns:
            raise KeyError(f"Missing `c_adjusted` in {src_path}")

        labels = _build_labels(df, cfg.horizons)
        base_cols = [c for c in ("ticker", "date", "year", "c_adjusted", "materialized_price_view", "source_daily_file") if c in labels.columns]
        label_cols = [f"ret_{h}d" for h in cfg.horizons]
        keep = base_cols + label_cols
        out = labels[keep].copy()
        out["label_source_view"] = "daily_adjusted_v0_1"
        out["label_contract"] = "daily_return_labels_v0_1"

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out.to_parquet(out_path, index=False)
        files_written += 1
        rows_written += int(len(out))

    return {
        "ticker": ticker,
        "files_seen": files_seen,
        "files_written": files_written,
        "rows_written": rows_written,
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa labels diarios de retorno desde `daily_adjusted`.")
    ap.add_argument("--adjusted-root", required=True)
    ap.add_argument("--output-root", required=True)
    ap.add_argument("--tickers", nargs="*", default=None)
    ap.add_argument("--limit-tickers", type=int, default=None)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--horizons", nargs="*", type=int, default=[1, 3, 5])
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    tickers = {t.upper() for t in args.tickers} if args.tickers else None
    cfg = LabelsConfig(
        adjusted_root=Path(args.adjusted_root),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
        horizons=tuple(int(h) for h in args.horizons),
    )

    ticker_dirs = list(_iter_ticker_dirs(cfg.adjusted_root, tickers=tickers))
    if args.limit_tickers is not None:
        ticker_dirs = ticker_dirs[: int(args.limit_tickers)]

    rows: list[dict[str, int | str]] = []
    for ticker_dir in ticker_dirs:
        rows.append(materialize_ticker(ticker_dir, cfg))

    if rows:
        summary = pd.DataFrame(rows)
        cfg.output_root.mkdir(parents=True, exist_ok=True)
        summary.to_csv(cfg.output_root / "_labels_materialization_summary.csv", index=False)
        print(summary.to_string(index=False))
    else:
        print("No ticker directories selected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
