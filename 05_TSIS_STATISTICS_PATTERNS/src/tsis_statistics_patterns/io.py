from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import pyarrow.parquet as pq


ADJUSTED_REQUIRED_COLUMNS = [
    "ticker",
    "date",
    "year",
    "o",
    "h",
    "l",
    "c",
    "v",
    "vw",
    "n",
    "t",
    "future_split_factor",
    "o_split_normalized",
    "h_split_normalized",
    "l_split_normalized",
    "c_split_normalized",
    "materialized_price_view",
    "source_daily_file",
]


CANONICAL_RAW_ROOT = Path(r"G:\TSIS\data\ohlcv_daily")


def canonical_source_daily_file(
    value: object, raw_root: str | Path = CANONICAL_RAW_ROOT
) -> str:
    normalized = str(value).replace("\\", "/")
    marker = "ticker="
    position = normalized.lower().find(marker)
    if position < 0:
        raise ValueError(f"Unresolvable source_daily_file lineage: {value}")
    return (Path(raw_root) / Path(normalized[position:])).as_posix()


def load_universe_tickers(activity_path: str | Path) -> list[str]:
    table = pq.read_table(activity_path, columns=["ticker"])
    return sorted(set(str(x) for x in table.column("ticker").to_pylist()))


def stable_ticker_shard(ticker: str, shard_count: int) -> int:
    digest = hashlib.sha256(ticker.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big") % shard_count


def tickers_for_shard(tickers: list[str], shard_index: int, shard_count: int) -> list[str]:
    if shard_count <= 0 or not 0 <= shard_index < shard_count:
        raise ValueError("Invalid shard index/count")
    return [t for t in tickers if stable_ticker_shard(t, shard_count) == shard_index]


def ticker_files(adjusted_root: str | Path, ticker: str) -> list[Path]:
    root = Path(adjusted_root) / f"ticker={ticker}"
    return sorted(root.glob("year=*/*.parquet"))


def load_adjusted_ticker(
    adjusted_root: str | Path, ticker: str, raw_root: str | Path = CANONICAL_RAW_ROOT
) -> pd.DataFrame:
    files = ticker_files(adjusted_root, ticker)
    if not files:
        raise FileNotFoundError(f"No adjusted daily files for ticker={ticker}")
    frames = [
        pq.ParquetFile(path).read(columns=ADJUSTED_REQUIRED_COLUMNS).to_pandas()
        for path in files
    ]
    frame = pd.concat(frames, ignore_index=True)
    observed = set(frame["ticker"].dropna().astype(str).unique())
    if observed != {ticker}:
        raise ValueError(f"Ticker identity mismatch for {ticker}: {sorted(observed)}")
    frame["source_daily_file"] = frame["source_daily_file"].map(lambda value: canonical_source_daily_file(value, raw_root))
    return frame


def safe_ticker_filename(ticker: str) -> str:
    return quote(ticker, safe="")


def write_table_part(frame: pd.DataFrame, table_root: str | Path, ticker: str) -> Path | None:
    if frame.empty:
        return None
    root = Path(table_root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"ticker={safe_ticker_filename(ticker)}.parquet"
    frame.to_parquet(path, index=False, compression="zstd")
    return path
