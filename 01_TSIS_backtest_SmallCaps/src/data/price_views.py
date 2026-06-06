from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


PRICE_COLUMNS_DEFAULT = ("o", "h", "l", "c")


@dataclass(frozen=True)
class PriceViewMetadata:
    view_name: str
    date_col: str
    factor_col: str
    source_price_cols: tuple[str, ...]
    output_price_cols: tuple[str, ...]


def _ensure_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def canonicalize_split_table(
    splits: pd.DataFrame,
    execution_date_col: str = "execution_date",
    split_ratio_col: str = "split_ratio",
    split_from_col: str = "split_from",
    split_to_col: str = "split_to",
) -> pd.DataFrame:
    """
    Return a canonical split table with:

    - `execution_date`
    - `split_ratio`

    The canonical ratio is expressed as a multiplicative future factor
    used to normalize older observations into the later post-split scale.

    Examples:
    - forward split `1 -> 2` => ratio `2.0`
    - reverse split `20 -> 1` => ratio `0.05`
    """
    if splits is None or splits.empty:
        return pd.DataFrame(columns=["execution_date", "split_ratio"])

    out = splits.copy()
    out["execution_date"] = _ensure_datetime(out[execution_date_col])

    if split_ratio_col in out.columns:
        out["split_ratio"] = pd.to_numeric(out[split_ratio_col], errors="coerce")
    else:
        split_from = pd.to_numeric(out[split_from_col], errors="coerce")
        split_to = pd.to_numeric(out[split_to_col], errors="coerce")
        out["split_ratio"] = np.where(split_from > 0, split_to / split_from, np.nan)

    out = out.loc[out["execution_date"].notna()].copy()
    out = out.loc[pd.to_numeric(out["split_ratio"], errors="coerce").gt(0)].copy()
    out = out[["execution_date", "split_ratio"]].sort_values("execution_date").reset_index(drop=True)
    return out


def build_future_split_factor_series(
    dates: pd.Series,
    splits: pd.DataFrame,
    execution_date_col: str = "execution_date",
    split_ratio_col: str = "split_ratio",
) -> pd.Series:
    """
    For each date, compute the multiplicative product of all split ratios
    whose execution date is strictly after the observation date.

    This lets older raw prices be re-expressed in a later split-normalized scale.
    """
    dates = _ensure_datetime(dates)
    canonical = canonicalize_split_table(
        splits,
        execution_date_col=execution_date_col,
        split_ratio_col=split_ratio_col,
    )
    if canonical.empty:
        return pd.Series(np.ones(len(dates)), index=dates.index, dtype=float)

    factors: list[float] = []
    for d in dates:
        future = canonical.loc[canonical["execution_date"].gt(d), "split_ratio"]
        factor = float(future.prod()) if not future.empty else 1.0
        factors.append(factor if np.isfinite(factor) and factor > 0 else 1.0)
    return pd.Series(factors, index=dates.index, dtype=float)


def _build_split_factor_lookup(
    frame: pd.DataFrame,
    date_col: str,
    split_factor_col: str,
) -> dict[pd.Timestamp, float]:
    lookup: dict[pd.Timestamp, float] = {}
    for _, row in frame[[date_col, split_factor_col]].iterrows():
        d = pd.Timestamp(row[date_col])
        factor = float(row[split_factor_col])
        if pd.isna(d) or not np.isfinite(factor) or factor <= 0:
            continue
        lookup[d.normalize()] = factor
    return lookup


def apply_split_normalized_view(
    frame: pd.DataFrame,
    splits: pd.DataFrame,
    date_col: str = "date",
    price_cols: Sequence[str] = PRICE_COLUMNS_DEFAULT,
    factor_col: str = "future_split_factor",
    suffix: str = "_split_normalized",
) -> tuple[pd.DataFrame, PriceViewMetadata]:
    """
    Add a split-normalized price view to a dataframe.

    Output prices are computed as:
    `price * future_split_factor`

    This is correct for reconciling older raw quotes/trades with a later
    post-split scale when the split table expresses ratios as `split_to / split_from`.
    """
    out = frame.copy()
    out[factor_col] = build_future_split_factor_series(out[date_col], splits)
    created_cols: list[str] = []
    for col in price_cols:
        dst = f"{col}{suffix}"
        out[dst] = pd.to_numeric(out[col], errors="coerce") * pd.to_numeric(out[factor_col], errors="coerce")
        created_cols.append(dst)
    return out, PriceViewMetadata(
        view_name="split_normalized",
        date_col=date_col,
        factor_col=factor_col,
        source_price_cols=tuple(price_cols),
        output_price_cols=tuple(created_cols),
    )


def canonicalize_dividend_table(
    dividends: pd.DataFrame,
    ex_date_col: str = "ex_dividend_date",
    cash_col: str = "cash_amount",
) -> pd.DataFrame:
    if dividends is None or dividends.empty:
        return pd.DataFrame(columns=["ex_dividend_date", "cash_amount"])
    out = dividends.copy()
    out["ex_dividend_date"] = _ensure_datetime(out[ex_date_col])
    out["cash_amount"] = pd.to_numeric(out[cash_col], errors="coerce")
    out = out.loc[out["ex_dividend_date"].notna()].copy()
    out = out.loc[out["cash_amount"].gt(0)].copy()
    out = out[["ex_dividend_date", "cash_amount"]].sort_values("ex_dividend_date").reset_index(drop=True)
    return out


def build_future_dividend_adjustment_table(
    daily_frame: pd.DataFrame,
    dividends: pd.DataFrame,
    date_col: str = "date",
    close_col: str = "c",
    ex_date_col: str = "ex_dividend_date",
    cash_col: str = "cash_amount",
    split_factor_col: str | None = None,
) -> pd.DataFrame:
    """
    Build a future dividend factor table over a daily series.

    For each dividend, the factor is based on the previous available raw close:
    `1 - cash_amount / prev_close`

    The final factor for an observation date is the product of all future factors.

    This is suitable for an institutional `adjusted_proxy` and for diagnostics.
    It is intentionally explicit and auditable; it does not claim to reproduce
    every external vendor's adjusted chain exactly.
    """
    out = daily_frame.copy()
    out[date_col] = _ensure_datetime(out[date_col])
    out[close_col] = pd.to_numeric(out[close_col], errors="coerce")
    out = out.sort_values(date_col).reset_index(drop=True)
    split_factor_lookup: dict[pd.Timestamp, float] = {}
    if split_factor_col is not None and split_factor_col in out.columns:
        split_factor_lookup = _build_split_factor_lookup(out, date_col=date_col, split_factor_col=split_factor_col)

    canonical = canonicalize_dividend_table(dividends, ex_date_col=ex_date_col, cash_col=cash_col)
    if out.empty:
        out["future_dividend_sum"] = []
        out["future_dividend_factor"] = []
        return out
    if canonical.empty:
        out["future_dividend_sum"] = 0.0
        out["future_dividend_factor"] = 1.0
        return out

    rows: list[dict[str, float | pd.Timestamp]] = []
    for _, div in canonical.iterrows():
        ex_date = pd.Timestamp(div["ex_dividend_date"])
        cash = float(div["cash_amount"])
        prev = out.loc[out[date_col].lt(ex_date)].sort_values(date_col)
        if prev.empty:
            continue
        prev_close_raw = float(prev.iloc[-1][close_col])
        if not np.isfinite(prev_close_raw) or prev_close_raw <= 0 or cash <= 0:
            continue
        prev_close = prev_close_raw
        if split_factor_lookup:
            split_factor = float(split_factor_lookup.get(ex_date.normalize(), 1.0))
            if np.isfinite(split_factor) and split_factor > 0:
                prev_close = prev_close_raw * split_factor
        if cash >= prev_close:
            continue
        factor = 1.0 - (cash / prev_close)
        if factor <= 0 or not np.isfinite(factor):
            continue
        rows.append(
            {
                "ex_dividend_date": ex_date,
                "cash_amount": cash,
                "prev_close": prev_close,
                "prev_close_raw": prev_close_raw,
                "adj_factor": factor,
            }
        )

    if not rows:
        out["future_dividend_sum"] = 0.0
        out["future_dividend_factor"] = 1.0
        return out

    factors_df = pd.DataFrame(rows).sort_values("ex_dividend_date").reset_index(drop=True)
    future_sums: list[float] = []
    future_factors: list[float] = []
    for d in out[date_col]:
        active = factors_df.loc[factors_df["ex_dividend_date"].gt(pd.Timestamp(d))]
        future_sums.append(float(active["cash_amount"].sum()) if not active.empty else 0.0)
        future_factors.append(float(active["adj_factor"].prod()) if not active.empty else 1.0)

    out["future_dividend_sum"] = future_sums
    out["future_dividend_factor"] = future_factors
    return out


def apply_adjusted_proxy_view(
    daily_frame: pd.DataFrame,
    dividends: pd.DataFrame,
    date_col: str = "date",
    price_cols: Sequence[str] = PRICE_COLUMNS_DEFAULT,
    suffix: str = "_adjusted_proxy",
) -> tuple[pd.DataFrame, PriceViewMetadata]:
    """
    Add an `adjusted_proxy` price view to a daily dataframe using
    multiplicative future dividend factors.
    """
    out = build_future_dividend_adjustment_table(daily_frame, dividends, date_col=date_col)
    created_cols: list[str] = []
    for col in price_cols:
        dst = f"{col}{suffix}"
        out[dst] = pd.to_numeric(out[col], errors="coerce") * pd.to_numeric(out["future_dividend_factor"], errors="coerce")
        created_cols.append(dst)
    return out, PriceViewMetadata(
        view_name="adjusted_proxy",
        date_col=date_col,
        factor_col="future_dividend_factor",
        source_price_cols=tuple(price_cols),
        output_price_cols=tuple(created_cols),
    )


def apply_adjusted_view(
    daily_frame: pd.DataFrame,
    splits: pd.DataFrame,
    dividends: pd.DataFrame,
    date_col: str = "date",
    price_cols: Sequence[str] = PRICE_COLUMNS_DEFAULT,
    split_factor_col: str = "future_split_factor",
    split_suffix: str = "_split_normalized",
    adjusted_factor_col: str = "future_adjustment_factor",
    adjusted_suffix: str = "_adjusted",
) -> tuple[pd.DataFrame, PriceViewMetadata]:
    """
    Add the institutional `adjusted` view to a daily dataframe.

    Sequence:
    1. normalize raw prices to a split-consistent basis
    2. compute future dividend factors in that split-normalized basis
    3. apply the future dividend factor chain to the split-normalized prices
    """
    split_out, _ = apply_split_normalized_view(
        daily_frame,
        splits,
        date_col=date_col,
        price_cols=price_cols,
        factor_col=split_factor_col,
        suffix=split_suffix,
    )
    proxy_close_col = f"c{split_suffix}" if "c" in price_cols else f"{price_cols[-1]}{split_suffix}"
    adj_table = build_future_dividend_adjustment_table(
        split_out,
        dividends,
        date_col=date_col,
        close_col=proxy_close_col,
        split_factor_col=split_factor_col,
    )
    out = adj_table.copy()
    out[adjusted_factor_col] = pd.to_numeric(out["future_dividend_factor"], errors="coerce")
    created_cols: list[str] = []
    for col in price_cols:
        src = f"{col}{split_suffix}"
        dst = f"{col}{adjusted_suffix}"
        out[dst] = pd.to_numeric(out[src], errors="coerce") * pd.to_numeric(out[adjusted_factor_col], errors="coerce")
        created_cols.append(dst)
    return out, PriceViewMetadata(
        view_name="adjusted",
        date_col=date_col,
        factor_col=adjusted_factor_col,
        source_price_cols=tuple(f"{col}{split_suffix}" for col in price_cols),
        output_price_cols=tuple(created_cols),
    )
