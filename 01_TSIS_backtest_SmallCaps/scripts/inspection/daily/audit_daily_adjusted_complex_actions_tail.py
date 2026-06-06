from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
CA_ROOT = Path(r"C:\TSIS_Data\data\additional\corporate_actions")
DAILY_ROOT = Path(r"D:\ohlcv_daily")
OUT_ROOT = (
    PROJECT_ROOT
    / "01_foundations"
    / "inspection_dossiers"
    / "daily"
    / "evidence_assets"
    / "daily_adjusted_complex_actions_tail_audit"
)


def _iter_non_empty_parquet(root: Path):
    for path in root.rglob("*.parquet"):
        pf = pq.ParquetFile(path)
        cols = pf.schema_arrow.names
        if "_empty" in cols:
            empty_df = pf.read(columns=["_empty"]).to_pandas()
            if bool(empty_df["_empty"].iloc[0]):
                continue
        yield path, pf


def _build_candidate_tickers() -> set[str]:
    tickers: set[str] = set()

    for _, pf in _iter_non_empty_parquet(CA_ROOT / "ticker_events"):
        cols = pf.schema_arrow.names
        if {"ticker", "type"}.issubset(cols):
            df = pf.read(columns=["ticker", "type"]).to_pandas()
            if not df.empty and (df["type"].astype(str) == "ticker_change").any():
                tickers.add(str(df["ticker"].iloc[0]))

    for _, pf in _iter_non_empty_parquet(CA_ROOT / "dividends"):
        cols = pf.schema_arrow.names
        if {"ticker", "dividend_type"}.issubset(cols):
            df = pf.read(columns=["ticker", "dividend_type"]).to_pandas()
            if not df.empty and (df["dividend_type"].fillna("NA").astype(str) != "CD").any():
                tickers.add(str(df["ticker"].iloc[0]))

    return tickers


def _build_daily_coverage(candidate_tickers: set[str]) -> pd.DataFrame:
    rows: list[tuple[str, pd.Timestamp, pd.Timestamp]] = []
    for ticker in sorted(candidate_tickers):
        ticker_path = DAILY_ROOT / f"ticker={ticker}"
        if not ticker_path.exists():
            continue
        min_date: pd.Timestamp | None = None
        max_date: pd.Timestamp | None = None
        for file_path in ticker_path.rglob("*.parquet"):
            pf = pq.ParquetFile(file_path)
            cols = pf.schema_arrow.names
            if "date" not in cols:
                continue
            dates = pd.to_datetime(
                pf.read(columns=["date"]).to_pandas()["date"],
                errors="coerce",
            ).dropna()
            if dates.empty:
                continue
            cur_min = dates.min().normalize()
            cur_max = dates.max().normalize()
            min_date = cur_min if min_date is None or cur_min < min_date else min_date
            max_date = cur_max if max_date is None or cur_max > max_date else max_date
        if min_date is not None and max_date is not None:
            rows.append((ticker, min_date, max_date))
    return pd.DataFrame(rows, columns=["ticker", "first_date", "last_date"]).set_index("ticker")


def _collect_ticker_changes(daily_cov: pd.DataFrame) -> pd.DataFrame:
    rows: list[tuple[str, pd.Timestamp, pd.Timestamp, pd.Timestamp, bool, str | None]] = []
    for _, pf in _iter_non_empty_parquet(CA_ROOT / "ticker_events"):
        cols = pf.schema_arrow.names
        required = {"ticker", "type", "date"}
        if not required.issubset(cols):
            continue
        keep = [c for c in ["ticker", "type", "date", "name", "ticker_change.ticker"] if c in cols]
        df = pf.read(columns=keep).to_pandas()
        df = df[df["type"].astype(str) == "ticker_change"].copy()
        if df.empty:
            continue
        ticker = str(df["ticker"].iloc[0])
        if ticker not in daily_cov.index:
            continue
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        first_date = daily_cov.at[ticker, "first_date"]
        last_date = daily_cov.at[ticker, "last_date"]
        for _, row in df.iterrows():
            if pd.isna(row["date"]):
                continue
            event_date = row["date"].normalize()
            within = bool(first_date <= event_date <= last_date)
            rows.append(
                (
                    ticker,
                    event_date,
                    first_date,
                    last_date,
                    within,
                    row.get("ticker_change.ticker"),
                )
            )
    return pd.DataFrame(
        rows,
        columns=["ticker", "event_date", "first_date", "last_date", "within_daily_window", "new_ticker"],
    )


def _collect_non_cd_dividends(daily_cov: pd.DataFrame) -> pd.DataFrame:
    rows: list[tuple[str, str, pd.Timestamp, float, pd.Timestamp, pd.Timestamp, bool]] = []
    for _, pf in _iter_non_empty_parquet(CA_ROOT / "dividends"):
        cols = pf.schema_arrow.names
        required = {"ticker", "dividend_type", "ex_dividend_date", "cash_amount"}
        if not required.issubset(cols):
            continue
        df = pf.read(columns=["ticker", "dividend_type", "ex_dividend_date", "cash_amount"]).to_pandas()
        df = df[df["dividend_type"].fillna("NA").astype(str) != "CD"].copy()
        if df.empty:
            continue
        ticker = str(df["ticker"].iloc[0])
        if ticker not in daily_cov.index:
            continue
        df["ex_dividend_date"] = pd.to_datetime(df["ex_dividend_date"], errors="coerce")
        first_date = daily_cov.at[ticker, "first_date"]
        last_date = daily_cov.at[ticker, "last_date"]
        for _, row in df.iterrows():
            if pd.isna(row["ex_dividend_date"]):
                continue
            event_date = row["ex_dividend_date"].normalize()
            within = bool(first_date <= event_date <= last_date)
            rows.append(
                (
                    ticker,
                    str(row["dividend_type"]),
                    event_date,
                    float(row["cash_amount"]),
                    first_date,
                    last_date,
                    within,
                )
            )
    return pd.DataFrame(
        rows,
        columns=[
            "ticker",
            "dividend_type",
            "event_date",
            "cash_amount",
            "first_date",
            "last_date",
            "within_daily_window",
        ],
    )


def _collect_global_source_counts() -> dict[str, int]:
    event_type_counts: Counter[str] = Counter()
    div_type_counts: Counter[str] = Counter()
    split_rows_total = 0

    for _, pf in _iter_non_empty_parquet(CA_ROOT / "ticker_events"):
        cols = pf.schema_arrow.names
        if {"type"}.issubset(cols):
            df = pf.read(columns=["type"]).to_pandas()
            for key, val in df["type"].astype(str).value_counts(dropna=False).items():
                event_type_counts[str(key)] += int(val)

    for _, pf in _iter_non_empty_parquet(CA_ROOT / "dividends"):
        cols = pf.schema_arrow.names
        if {"dividend_type"}.issubset(cols):
            df = pf.read(columns=["dividend_type"]).to_pandas()
            for key, val in df["dividend_type"].fillna("NA").astype(str).value_counts(dropna=False).items():
                div_type_counts[str(key)] += int(val)

    for _, pf in _iter_non_empty_parquet(CA_ROOT / "splits"):
        cols = pf.schema_arrow.names
        if {"ticker", "execution_date"}.issubset(cols):
            df = pf.read(columns=["ticker", "execution_date"]).to_pandas()
            split_rows_total += len(df)

    return {
        "ticker_event_rows_total": sum(event_type_counts.values()),
        "ticker_event_ticker_change_rows": event_type_counts.get("ticker_change", 0),
        "dividend_rows_total": sum(div_type_counts.values()),
        "dividend_cd_rows": div_type_counts.get("CD", 0),
        "dividend_non_cd_rows": sum(v for k, v in div_type_counts.items() if k != "CD"),
        "split_rows_total": split_rows_total,
    }


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    candidate_tickers = _build_candidate_tickers()
    daily_cov = _build_daily_coverage(candidate_tickers)
    ticker_changes = _collect_ticker_changes(daily_cov)
    non_cd_divs = _collect_non_cd_dividends(daily_cov)
    source_counts = _collect_global_source_counts()

    summary = pd.DataFrame(
        [
            {"metric": "candidate_tickers_complex_tail", "value": len(candidate_tickers)},
            {"metric": "candidate_tickers_with_daily_coverage", "value": len(daily_cov)},
            {"metric": "ticker_change_rows_total", "value": int(len(ticker_changes))},
            {
                "metric": "ticker_change_rows_within_daily_window",
                "value": int(ticker_changes["within_daily_window"].sum()) if not ticker_changes.empty else 0,
            },
            {
                "metric": "ticker_change_rows_outside_daily_window",
                "value": int((~ticker_changes["within_daily_window"]).sum()) if not ticker_changes.empty else 0,
            },
            {
                "metric": "ticker_change_tickers_within_daily_window",
                "value": int(ticker_changes.loc[ticker_changes["within_daily_window"], "ticker"].nunique())
                if not ticker_changes.empty
                else 0,
            },
            {"metric": "non_cd_dividend_rows_total", "value": int(len(non_cd_divs))},
            {
                "metric": "non_cd_dividend_rows_within_daily_window",
                "value": int(non_cd_divs["within_daily_window"].sum()) if not non_cd_divs.empty else 0,
            },
            {
                "metric": "non_cd_dividend_rows_outside_daily_window",
                "value": int((~non_cd_divs["within_daily_window"]).sum()) if not non_cd_divs.empty else 0,
            },
            {
                "metric": "non_cd_dividend_tickers_within_daily_window",
                "value": int(non_cd_divs.loc[non_cd_divs["within_daily_window"], "ticker"].nunique())
                if not non_cd_divs.empty
                else 0,
            },
            *({"metric": k, "value": v} for k, v in source_counts.items()),
        ]
    )

    event_type_rows = [
        {"category": "ticker_event_type", "key": "ticker_change", "rows": int(len(ticker_changes))},
        {
            "category": "ticker_event_within_daily_window",
            "key": "ticker_change",
            "rows": int(ticker_changes["within_daily_window"].sum()) if not ticker_changes.empty else 0,
        },
    ]
    if not non_cd_divs.empty:
        for key, val in non_cd_divs["dividend_type"].value_counts().to_dict().items():
            event_type_rows.append(
                {
                    "category": "non_cd_dividend_type",
                    "key": key,
                    "rows": int(val),
                }
            )
    event_type_summary = pd.DataFrame(event_type_rows)

    summary.to_csv(OUT_ROOT / "daily_adjusted_complex_actions_tail_summary.csv", index=False)
    ticker_changes.to_csv(OUT_ROOT / "daily_adjusted_ticker_change_tail.csv", index=False)
    non_cd_divs.to_csv(OUT_ROOT / "daily_adjusted_non_cd_dividend_tail.csv", index=False)
    event_type_summary.to_csv(OUT_ROOT / "daily_adjusted_complex_actions_type_summary.csv", index=False)

    print(summary.to_string(index=False))
    print("\nWrote:")
    for name in [
        "daily_adjusted_complex_actions_tail_summary.csv",
        "daily_adjusted_ticker_change_tail.csv",
        "daily_adjusted_non_cd_dividend_tail.csv",
        "daily_adjusted_complex_actions_type_summary.csv",
    ]:
        print(OUT_ROOT / name)


if __name__ == "__main__":
    main()
