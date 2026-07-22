from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_case_index(cache_dir: str | Path) -> pd.DataFrame:
    cache_dir = Path(cache_dir)
    path = cache_dir / "case_index_cd.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def filter_case_index(
    case_index: pd.DataFrame,
    block: str | None = None,
    group_key: str | None = None,
    ticker: str | None = None,
    top_n: int = 100,
) -> pd.DataFrame:
    if case_index.empty:
        return case_index.copy()

    out = case_index.copy()
    if block is not None:
        out = out.loc[out["block"].astype(str) == str(block)]
    if group_key is not None:
        out = out.loc[out["group_key"].astype(str) == str(group_key)]
    if ticker is not None:
        out = out.loc[out["ticker"].astype(str) == str(ticker)]
    out = out.sort_values("rank_score", ascending=False)
    return out.head(top_n).reset_index(drop=True)


def load_current_case(
    trades_handle,
    file: str | None = None,
    ticker: str | None = None,
    date: str | pd.Timestamp | None = None,
    columns: list[str] | None = None,
    batch_size: int = 50_000,
    normalize: bool = True,
) -> pd.DataFrame:
    cols = columns or [
        "file",
        "ticker",
        "date",
        "severity",
        "issues",
        "warns",
        "metrics_json",
        "batch_id",
    ]

    if file is None and (ticker is None or date is None):
        raise ValueError("Provide `file` or `ticker` + `date`.")

    target_date = pd.to_datetime(date, errors="coerce") if date is not None else None
    chunks: list[pd.DataFrame] = []

    for df in trades_handle.stream(columns=cols, batch_size=batch_size, normalize=normalize):
        mask = pd.Series(True, index=df.index)
        if file is not None:
            mask &= df["file"].astype(str) == str(file)
        if ticker is not None:
            mask &= df["ticker"].astype(str) == str(ticker)
        if target_date is not None:
            mask &= pd.to_datetime(df["date"], errors="coerce") == target_date
        matched = df.loc[mask]
        if not matched.empty:
            chunks.append(matched)

    if not chunks:
        return pd.DataFrame(columns=cols)
    return pd.concat(chunks, ignore_index=True)


def load_source_trade_file(
    file_path: str | Path,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    file_path = Path(file_path)
    if not file_path.exists():
        return pd.DataFrame(columns=columns or [])
    if columns:
        return pd.read_parquet(file_path, columns=columns)
    return pd.read_parquet(file_path)


def load_case_from_index_row(
    trades_handle,
    case_row: pd.Series | dict,
    columns: list[str] | None = None,
    batch_size: int = 50_000,
    normalize: bool = True,
    prefer_source_file: bool = True,
) -> pd.DataFrame:
    file = case_row.get("file")
    ticker = case_row.get("ticker")
    date = case_row.get("date")
    if prefer_source_file and file is not None:
        source_path = Path(str(file))
        if source_path.exists():
            return load_source_trade_file(source_path, columns=columns)
    return load_current_case(
        trades_handle=trades_handle,
        file=file,
        ticker=ticker,
        date=date,
        columns=columns,
        batch_size=batch_size,
        normalize=normalize,
    )
