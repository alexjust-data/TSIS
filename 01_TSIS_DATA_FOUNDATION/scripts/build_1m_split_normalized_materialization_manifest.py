from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


DEFAULT_MINUTE_ROOT = Path(r"E:\TSIS\data\ohlcv_1m")
DEFAULT_SPLITS_ROOT = Path(r"E:\TSIS\data\additional\corporate_actions\splits")


@dataclass(frozen=True)
class MinuteFile:
    ticker: str
    year: int
    month: int
    path: Path


def _split_file(root: Path, ticker: str) -> Path:
    return root / f"ticker={ticker}" / f"splits_{ticker}.parquet"


def _source_path(root: Path, ticker: str, year: int, month: int) -> Path:
    return (
        root
        / f"ticker={ticker}"
        / f"year={year}"
        / f"month={month:02d}"
        / f"minute_aggs_{ticker}_{year}_{month:02d}.parquet"
    )


def _parse_partition_int(path: Path, prefix: str) -> int | None:
    if not path.name.startswith(prefix):
        return None
    try:
        return int(path.name.split("=", 1)[1])
    except ValueError:
        return None


def _ticker_from_partition(path: Path) -> str | None:
    if not path.name.startswith("ticker="):
        return None
    ticker = path.name.split("=", 1)[1].strip().upper()
    return ticker or None


def _iter_split_tickers(root: Path) -> Iterable[str]:
    for ticker_dir in sorted(root.iterdir(), key=lambda p: p.name):
        if not ticker_dir.is_dir():
            continue
        ticker = _ticker_from_partition(ticker_dir)
        if ticker and _split_file(root, ticker).exists():
            yield ticker


def _iter_existing_months_for_ticker(
    minute_root: Path,
    ticker: str,
    min_year: int | None,
    max_year: int | None,
) -> Iterable[MinuteFile]:
    ticker_dir = minute_root / f"ticker={ticker}"
    if not ticker_dir.exists():
        return

    for year_dir in sorted(ticker_dir.iterdir(), key=lambda p: p.name):
        if not year_dir.is_dir():
            continue
        year = _parse_partition_int(year_dir, "year=")
        if year is None:
            continue
        if min_year is not None and year < min_year:
            continue
        if max_year is not None and year > max_year:
            continue

        for month_dir in sorted(year_dir.iterdir(), key=lambda p: p.name):
            if not month_dir.is_dir():
                continue
            month = _parse_partition_int(month_dir, "month=")
            if month is None:
                continue
            source = _source_path(minute_root, ticker, year, month)
            if source.exists():
                yield MinuteFile(ticker=ticker, year=year, month=month, path=source)


def _iter_all_existing_minute_files(
    minute_root: Path,
    min_year: int | None,
    max_year: int | None,
) -> Iterable[MinuteFile]:
    for ticker_dir in sorted(minute_root.iterdir(), key=lambda p: p.name):
        if not ticker_dir.is_dir():
            continue
        ticker = _ticker_from_partition(ticker_dir)
        if not ticker:
            continue
        yield from _iter_existing_months_for_ticker(
            minute_root=minute_root,
            ticker=ticker,
            min_year=min_year,
            max_year=max_year,
        )


def _event_type(split_from: float, split_to: float) -> str:
    if split_from > split_to:
        return "reverse_split"
    if split_to > split_from:
        return "forward_split"
    return "split"


def _load_split_events(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(
            columns=["execution_date", "split_from", "split_to", "split_ratio", "event_type"]
        )
    frame = pd.read_parquet(path)
    if "_empty" in frame.columns and len(frame) and bool(frame["_empty"].iloc[0]) is True:
        return pd.DataFrame(
            columns=["execution_date", "split_from", "split_to", "split_ratio", "event_type"]
        )
    required = {"execution_date", "split_from", "split_to"}
    if not required <= set(frame.columns):
        return pd.DataFrame(
            columns=["execution_date", "split_from", "split_to", "split_ratio", "event_type"]
        )
    out = frame[["execution_date", "split_from", "split_to"]].copy()
    out["execution_date"] = pd.to_datetime(out["execution_date"], errors="coerce")
    out["split_from"] = pd.to_numeric(out["split_from"], errors="coerce")
    out["split_to"] = pd.to_numeric(out["split_to"], errors="coerce")
    out = out.loc[
        out["execution_date"].notna() & out["split_from"].gt(0) & out["split_to"].gt(0)
    ].copy()
    if out.empty:
        return pd.DataFrame(
            columns=["execution_date", "split_from", "split_to", "split_ratio", "event_type"]
        )
    out["execution_date"] = out["execution_date"].dt.normalize()
    out["split_ratio"] = out["split_to"] / out["split_from"]
    out["event_type"] = [
        _event_type(float(split_from), float(split_to))
        for split_from, split_to in zip(out["split_from"], out["split_to"], strict=True)
    ]
    return out.sort_values("execution_date").reset_index(drop=True)


def _future_event_for_month(events: pd.DataFrame, year: int, month: int) -> pd.Series | None:
    month_start = pd.Timestamp(year=year, month=month, day=1)
    future = events.loc[events["execution_date"].gt(month_start)]
    if future.empty:
        return None
    return future.iloc[0]


def build_manifest(
    minute_root: Path,
    splits_root: Path,
    output: Path,
    mode: str,
    min_year: int | None,
    max_year: int | None,
    limit: int | None,
    chunk_size: int | None,
    chunks_dir: Path | None,
) -> dict[str, object]:
    if not minute_root.exists():
        raise FileNotFoundError(f"Missing minute root: {minute_root}")
    if not splits_root.exists():
        raise FileNotFoundError(f"Missing splits root: {splits_root}")

    split_cache: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, object]] = []
    files_seen = 0
    files_in_year_window = 0
    files_without_split_effect = 0
    split_tickers_seen = 0
    split_tickers_without_minute_dir = 0

    if mode == "all-existing":
        minute_files = _iter_all_existing_minute_files(
            minute_root=minute_root,
            min_year=min_year,
            max_year=max_year,
        )
        scan_strategy = "partition_direct_all_existing"
        for minute_file in minute_files:
            files_seen += 1
            files_in_year_window += 1
            rows.append(
                {
                    "ticker": minute_file.ticker,
                    "year": minute_file.year,
                    "month": minute_file.month,
                    "event_type": "physical_full_universe",
                    "event_date": "",
                    "role": "all_existing_raw_1m_month",
                    "split_from": 1,
                    "split_to": 1,
                    "rationale": "physical full-universe split-normalized materialization candidate",
                }
            )

            if limit is not None and len(rows) >= limit:
                break
    else:
        scan_strategy = "split_tickers_then_partition_direct"
        for ticker in _iter_split_tickers(splits_root):
            split_tickers_seen += 1
            if not (minute_root / f"ticker={ticker}").exists():
                split_tickers_without_minute_dir += 1
                continue

            if ticker not in split_cache:
                split_cache[ticker] = _load_split_events(_split_file(splits_root, ticker))
            events = split_cache[ticker]
            if events.empty:
                continue

            for minute_file in _iter_existing_months_for_ticker(
                minute_root=minute_root,
                ticker=ticker,
                min_year=min_year,
                max_year=max_year,
            ):
                files_seen += 1
                files_in_year_window += 1
                event = _future_event_for_month(events, minute_file.year, minute_file.month)
                if event is None:
                    files_without_split_effect += 1
                    continue
                rows.append(
                    {
                        "ticker": minute_file.ticker,
                        "year": minute_file.year,
                        "month": minute_file.month,
                        "event_type": str(event["event_type"]),
                        "event_date": pd.Timestamp(event["execution_date"]).date().isoformat(),
                        "role": "split_affected_ticker_month",
                        "split_from": float(event["split_from"]),
                        "split_to": float(event["split_to"]),
                        "rationale": "ticker-month has at least one future split and needs split-normalized 1m materialization",
                    }
                )

                if limit is not None and len(rows) >= limit:
                    break

            if limit is not None and len(rows) >= limit:
                break

    manifest = pd.DataFrame(
        rows,
        columns=[
            "ticker",
            "year",
            "month",
            "event_type",
            "event_date",
            "role",
            "split_from",
            "split_to",
            "rationale",
        ],
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(output, index=False)

    chunk_paths: list[str] = []
    if chunk_size and chunk_size > 0 and chunks_dir is not None:
        chunks_dir.mkdir(parents=True, exist_ok=True)
        for idx, start in enumerate(range(0, len(manifest), chunk_size), start=1):
            chunk = manifest.iloc[start : start + chunk_size]
            chunk_path = chunks_dir / f"{output.stem}_chunk_{idx:04d}.csv"
            chunk.to_csv(chunk_path, index=False)
            chunk_paths.append(str(chunk_path))

    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "minute_root": str(minute_root),
        "splits_root": str(splits_root),
        "output": str(output),
        "rows": int(len(manifest)),
        "tickers": int(manifest["ticker"].nunique()) if not manifest.empty else 0,
        "scan_strategy": scan_strategy,
        "files_seen": files_seen,
        "files_in_year_window": files_in_year_window,
        "files_without_split_effect": files_without_split_effect,
        "split_tickers_seen": split_tickers_seen,
        "split_tickers_without_minute_dir": split_tickers_without_minute_dir,
        "min_year": min_year,
        "max_year": max_year,
        "limit": limit,
        "chunk_size": chunk_size,
        "chunks_dir": str(chunks_dir) if chunks_dir else "",
        "chunk_count": len(chunk_paths),
        "chunk_paths": chunk_paths,
    }
    output.with_suffix(".summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a manifest for 1m split-normalized materialization."
    )
    parser.add_argument("--minute-root", type=Path, default=DEFAULT_MINUTE_ROOT)
    parser.add_argument("--splits-root", type=Path, default=DEFAULT_SPLITS_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=["split-affected", "all-existing"],
        default="split-affected",
        help=(
            "split-affected materializes only ticker-months that need non-1 future split factors; "
            "all-existing emits every raw 1m ticker-month for a physical full copy."
        ),
    )
    parser.add_argument("--min-year", type=int)
    parser.add_argument("--max-year", type=int)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--chunk-size", type=int)
    parser.add_argument("--chunks-dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_manifest(
        minute_root=args.minute_root,
        splits_root=args.splits_root,
        output=args.output,
        mode=args.mode,
        min_year=args.min_year,
        max_year=args.max_year,
        limit=args.limit,
        chunk_size=args.chunk_size,
        chunks_dir=args.chunks_dir,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
