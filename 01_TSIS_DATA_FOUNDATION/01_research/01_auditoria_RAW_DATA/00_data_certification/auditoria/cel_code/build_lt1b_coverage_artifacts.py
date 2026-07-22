from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyarrow.parquet as pq


LT1B_UNIVERSE_PARQUET = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet"
)
DAILY_INVENTORY_BY_TICKER = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_inventory\daily_inventory_full\daily_inventory_by_ticker.parquet"
)
OHLCV_1M_INVENTORY_BY_TICKER = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\ohlcv_1m_inventory_full_merged\ohlcv_1m_inventory_by_ticker.parquet"
)
QUOTES_INVENTORY_BY_TICKER = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_inventory\quotes_inventory_2005_2026\quotes_inventory_by_ticker.parquet"
)
TRADES_INVENTORY_BY_TICKER = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\trades_inventory_2005_2026\trades_inventory_by_ticker.parquet"
)
QUOTES_CURRENT_PARQUET = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet"
)
TRADES_CURRENT_PARQUET = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\trades_current.parquet"
)
HALTS_MASTER_PARQUET = Path(r"D:\Halts\processed\halts_master_multisource.parquet")
FINANCIAL_INCOME_ROOT = Path(r"D:\financial\income_statements")
FINANCIAL_BALANCE_ROOT = Path(r"D:\financial\balance_sheets")
FINANCIAL_CASH_FLOW_ROOT = Path(r"D:\financial\cash_flow_statements")
FINANCIAL_RATIO_ROOT = Path(r"D:\financial\ratios")
DEFAULT_OUTPUT_ROOT = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\cache_lt1b_coverage"
)


def _utcnow_iso() -> str:
    return pd.Timestamp.now("UTC").isoformat()


def _normalize_ticker(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.upper()


def _month_floor(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce")
    return dt.dt.to_period("M").dt.to_timestamp()


def _log(event: str, **payload: object) -> None:
    row = {"ts": _utcnow_iso(), "event": event}
    row.update(payload)
    print(json.dumps(row, ensure_ascii=False), flush=True)


@dataclass
class DenseScanResult:
    month_presence: pd.DataFrame
    summary: pd.DataFrame


def _ensure_exists(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(str(path))


def _build_pti_month_grid(lt1b: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in lt1b.itertuples(index=False):
        start = pd.Timestamp(row.pti_start)
        end = pd.Timestamp(row.pti_end)
        months = pd.period_range(start=start.to_period("M"), end=end.to_period("M"), freq="M")
        for month in months:
            rows.append(
                {
                    "ticker": row.ticker,
                    "month": month.to_timestamp(),
                    "pti_start": start,
                    "pti_end": end,
                    "classification_1b": row.classification_1b,
                    "classification_reason_1b": row.classification_reason_1b,
                    "in_pti_window": True,
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "month",
                "pti_start",
                "pti_end",
                "classification_1b",
                "classification_reason_1b",
                "in_pti_window",
            ]
        )
    out["month"] = pd.to_datetime(out["month"], errors="coerce")
    return out.sort_values(["ticker", "month"]).reset_index(drop=True)


def _months_between_from_inventory(
    df: pd.DataFrame,
    ticker_col: str = "ticker",
    start_year_col: str = "year_min",
    end_year_col: str = "year_max",
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in df.itertuples(index=False):
        ticker = str(getattr(row, ticker_col, "")).strip().upper()
        if not ticker:
            continue
        year_min = getattr(row, start_year_col, None)
        year_max = getattr(row, end_year_col, None)
        if pd.isna(year_min) or pd.isna(year_max):
            continue
        for year in range(int(year_min), int(year_max) + 1):
            for month in range(1, 13):
                rows.append({"ticker": ticker, "month": pd.Timestamp(year=year, month=month, day=1)})
    return pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)


def _ohlcv_1m_months_from_inventory(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in df.itertuples(index=False):
        ticker = str(getattr(row, "ticker", "")).strip().upper()
        if not ticker:
            continue
        year_min = getattr(row, "year_min", None)
        year_max = getattr(row, "year_max", None)
        month_min = getattr(row, "month_min", None)
        month_max = getattr(row, "month_max", None)
        if pd.isna(year_min) or pd.isna(year_max):
            continue
        start_month = 1 if pd.isna(month_min) else int(month_min)
        end_month = 12 if pd.isna(month_max) else int(month_max)
        if int(year_min) == int(year_max):
            for month in range(start_month, end_month + 1):
                rows.append({"ticker": ticker, "month": pd.Timestamp(year=int(year_min), month=month, day=1)})
            continue
        for year in range(int(year_min), int(year_max) + 1):
            lo = start_month if year == int(year_min) else 1
            hi = end_month if year == int(year_max) else 12
            for month in range(lo, hi + 1):
                rows.append({"ticker": ticker, "month": pd.Timestamp(year=year, month=month, day=1)})
    return pd.DataFrame(rows).drop_duplicates().reset_index(drop=True)


def _summarize_month_presence(month_df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    if month_df.empty:
        return pd.DataFrame(
            columns=["ticker", f"{dataset}_has_any", f"{dataset}_obs_start", f"{dataset}_obs_end", f"{dataset}_months_present"]
        )
    out = (
        month_df.groupby("ticker", as_index=False)
        .agg(
            **{
                f"{dataset}_obs_start": ("month", "min"),
                f"{dataset}_obs_end": ("month", "max"),
                f"{dataset}_months_present": ("month", "nunique"),
            }
        )
        .sort_values("ticker")
        .reset_index(drop=True)
    )
    out[f"{dataset}_has_any"] = True
    return out[["ticker", f"{dataset}_has_any", f"{dataset}_obs_start", f"{dataset}_obs_end", f"{dataset}_months_present"]]


def _clip_month_presence_to_pti(month_df: pd.DataFrame, pti_grid: pd.DataFrame) -> pd.DataFrame:
    if month_df.empty:
        return month_df.copy()
    keys = pti_grid[["ticker", "month"]].drop_duplicates()
    out = month_df.merge(keys, on=["ticker", "month"], how="inner")
    return out.drop_duplicates().sort_values(["ticker", "month"]).reset_index(drop=True)


def _scan_dense_current_months(
    parquet_path: Path,
    dataset_name: str,
    batch_size: int,
    max_batches: int | None,
) -> DenseScanResult:
    _log("scan_dense_current.start", dataset=dataset_name, path=str(parquet_path), batch_size=batch_size, max_batches=max_batches)
    pf = pq.ParquetFile(parquet_path)
    unique_pairs: set[tuple[str, pd.Timestamp]] = set()
    batch_idx = 0
    rows_seen = 0
    for batch in pf.iter_batches(columns=["ticker", "date"], batch_size=batch_size):
        batch_idx += 1
        if max_batches is not None and batch_idx > max_batches:
            break
        df = batch.to_pandas()
        rows_seen += len(df)
        if df.empty:
            continue
        df["ticker"] = _normalize_ticker(df["ticker"])
        df["month"] = _month_floor(df["date"])
        df = df.dropna(subset=["ticker", "month"])
        if df.empty:
            continue
        for row in df[["ticker", "month"]].drop_duplicates().itertuples(index=False):
            unique_pairs.add((str(row.ticker), pd.Timestamp(row.month)))
        _log("scan_dense_current.progress", dataset=dataset_name, batch=batch_idx, rows_seen=rows_seen, unique_pairs=len(unique_pairs))
    month_presence = pd.DataFrame(
        [{"ticker": ticker, "month": month} for ticker, month in sorted(unique_pairs, key=lambda x: (x[0], x[1]))]
    )
    summary = _summarize_month_presence(month_presence, dataset_name)
    _log("scan_dense_current.end", dataset=dataset_name, rows_seen=rows_seen, unique_pairs=len(unique_pairs), tickers=len(summary))
    return DenseScanResult(month_presence=month_presence, summary=summary)


def _scan_halts_overlay(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    _log("scan_halts.start", path=str(path))
    df = pd.read_parquet(path, columns=["ticker", "halt_date"])
    if df.empty:
        empty_month = pd.DataFrame(columns=["ticker", "month", "has_halts_event", "halts_events_count"])
        empty_summary = pd.DataFrame(columns=["ticker", "halts_has_any", "halts_events_total", "halts_first_date", "halts_last_date", "halts_months_present"])
        return empty_month, empty_summary
    df["ticker"] = _normalize_ticker(df["ticker"])
    df["halt_date"] = pd.to_datetime(df["halt_date"], errors="coerce")
    df["month"] = _month_floor(df["halt_date"])
    df = df.dropna(subset=["ticker", "halt_date", "month"]).copy()
    month_overlay = (
        df.groupby(["ticker", "month"], as_index=False)
        .agg(halts_events_count=("halt_date", "size"))
        .sort_values(["ticker", "month"])
        .reset_index(drop=True)
    )
    month_overlay["has_halts_event"] = month_overlay["halts_events_count"] > 0
    summary = (
        df.groupby("ticker", as_index=False)
        .agg(
            halts_events_total=("halt_date", "size"),
            halts_first_date=("halt_date", "min"),
            halts_last_date=("halt_date", "max"),
            halts_months_present=("month", "nunique"),
        )
        .sort_values("ticker")
        .reset_index(drop=True)
    )
    summary["halts_has_any"] = summary["halts_events_total"] > 0
    summary = summary[
        ["ticker", "halts_has_any", "halts_events_total", "halts_first_date", "halts_last_date", "halts_months_present"]
    ]
    _log("scan_halts.end", tickers=len(summary), month_rows=len(month_overlay))
    return month_overlay, summary


def _scan_financial_overlay(
    root: Path,
    dataset_name: str,
    date_columns: list[str],
    has_col: str,
    count_col: str,
    total_col: str,
    max_files: int | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    _log("scan_financial.start", dataset=dataset_name, root=str(root), max_files=max_files)
    files = sorted(root.rglob("*.parquet"))
    if max_files is not None:
        files = files[:max_files]
    month_counter: dict[tuple[str, pd.Timestamp], int] = {}
    first_date: dict[str, pd.Timestamp] = {}
    last_date: dict[str, pd.Timestamp] = {}
    event_count: dict[str, int] = {}
    for idx, file_path in enumerate(files, start=1):
        available_cols = pq.ParquetFile(file_path).schema.names
        use_cols = [col for col in ["ticker", *date_columns] if col in available_cols]
        if "ticker" not in use_cols:
            continue
        df = pd.read_parquet(file_path, columns=use_cols)
        if df.empty:
            continue
        df["ticker"] = _normalize_ticker(df["ticker"])
        date_series = None
        for col in date_columns:
            if col in df.columns:
                cand = pd.to_datetime(df[col], errors="coerce")
                date_series = cand if date_series is None else date_series.fillna(cand)
        if date_series is None:
            continue
        df["event_date"] = date_series
        df["month"] = _month_floor(df["event_date"])
        df = df.dropna(subset=["ticker", "event_date", "month"]).copy()
        for row in df[["ticker", "event_date", "month"]].itertuples(index=False):
            ticker = str(row.ticker)
            event_date = pd.Timestamp(row.event_date)
            month = pd.Timestamp(row.month)
            month_counter[(ticker, month)] = month_counter.get((ticker, month), 0) + 1
            event_count[ticker] = event_count.get(ticker, 0) + 1
            cur_min = first_date.get(ticker)
            cur_max = last_date.get(ticker)
            if cur_min is None or event_date < cur_min:
                first_date[ticker] = event_date
            if cur_max is None or event_date > cur_max:
                last_date[ticker] = event_date
        if idx % 500 == 0:
            _log("scan_financial.progress", dataset=dataset_name, files_done=idx, files_total=len(files), tickers=len(event_count))
    month_df = pd.DataFrame(
        [
            {"ticker": ticker, "month": month, has_col: True, count_col: count}
            for (ticker, month), count in sorted(month_counter.items(), key=lambda x: (x[0][0], x[0][1]))
        ]
    )
    ticker_months: dict[str, set[pd.Timestamp]] = {}
    for ticker, month in month_counter:
        ticker_months.setdefault(ticker, set()).add(month)
    summary_rows = []
    for ticker in sorted(event_count):
        summary_rows.append(
            {
                "ticker": ticker,
                f"{dataset_name}_has_any": True,
                f"{dataset_name}_first_date": first_date[ticker],
                f"{dataset_name}_last_date": last_date[ticker],
                total_col: event_count[ticker],
                f"{dataset_name}_months_present": len(ticker_months.get(ticker, set())),
            }
        )
    summary_df = pd.DataFrame(summary_rows)
    _log("scan_financial.end", dataset=dataset_name, files=len(files), tickers=len(summary_df), month_rows=len(month_df))
    return month_df, summary_df


def _merge_bool_month(base: pd.DataFrame, overlay: pd.DataFrame, bool_col: str) -> pd.DataFrame:
    if overlay.empty:
        base[bool_col] = False
        return base
    out = base.merge(overlay[["ticker", "month", bool_col]], on=["ticker", "month"], how="left")
    out[bool_col] = out[bool_col].astype("boolean").fillna(False).astype(bool)
    return out


def _merge_count_month(base: pd.DataFrame, overlay: pd.DataFrame, count_col: str) -> pd.DataFrame:
    if overlay.empty:
        base[count_col] = 0
        return base
    out = base.merge(overlay[["ticker", "month", count_col]], on=["ticker", "month"], how="left")
    out[count_col] = pd.to_numeric(out[count_col], errors="coerce").fillna(0).astype("int64")
    return out


def _assign_coverage_bucket(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["market_datasets_present_count"] = (
        out[["daily_has_any", "ohlcv_1m_has_any", "quotes_has_any", "trades_has_any"]].fillna(False).sum(axis=1)
    )
    out["coverage_bucket"] = "partial_market_data"
    out.loc[out["market_datasets_present_count"] == 0, "coverage_bucket"] = "no_market_data"
    out.loc[
        out["daily_has_any"] & out["ohlcv_1m_has_any"] & out["quotes_has_any"] & out["trades_has_any"],
        "coverage_bucket",
    ] = "all_market_data"
    out.loc[(out["market_datasets_present_count"] == 3) & (~out["daily_has_any"]), "coverage_bucket"] = "missing_daily"
    out.loc[(out["market_datasets_present_count"] == 3) & (~out["ohlcv_1m_has_any"]), "coverage_bucket"] = "missing_ohlcv_1m"
    out.loc[(out["market_datasets_present_count"] == 3) & (~out["quotes_has_any"]), "coverage_bucket"] = "missing_quotes"
    out.loc[(out["market_datasets_present_count"] == 3) & (~out["trades_has_any"]), "coverage_bucket"] = "missing_trades"
    gap_cols = {
        "daily": "daily_coverage_pct",
        "ohlcv_1m": "ohlcv_1m_coverage_pct",
        "quotes": "quotes_coverage_pct",
        "trades": "trades_coverage_pct",
    }
    top_gap = []
    for row in out.itertuples(index=False):
        best_name = None
        best_value = None
        for name, col in gap_cols.items():
            value = getattr(row, col, None)
            if pd.isna(value):
                value = -1.0
            if best_value is None or float(value) < float(best_value):
                best_name = name
                best_value = value
        top_gap.append(best_name)
    out["top_gap_dataset"] = top_gap
    return out


def _build_overlap_summary(ticker_summary: pd.DataFrame, lt1b_count: int) -> pd.DataFrame:
    combos = {
        "daily&ohlcv_1m": ticker_summary["daily_has_any"] & ticker_summary["ohlcv_1m_has_any"],
        "daily&quotes": ticker_summary["daily_has_any"] & ticker_summary["quotes_has_any"],
        "daily&trades": ticker_summary["daily_has_any"] & ticker_summary["trades_has_any"],
        "quotes&trades": ticker_summary["quotes_has_any"] & ticker_summary["trades_has_any"],
        "daily&ohlcv_1m&quotes&trades": (
            ticker_summary["daily_has_any"]
            & ticker_summary["ohlcv_1m_has_any"]
            & ticker_summary["quotes_has_any"]
            & ticker_summary["trades_has_any"]
        ),
        "all_market_data+income": (
            ticker_summary["daily_has_any"]
            & ticker_summary["ohlcv_1m_has_any"]
            & ticker_summary["quotes_has_any"]
            & ticker_summary["trades_has_any"]
            & ticker_summary["income_has_any"]
        ),
        "all_market_data+financials_any": (
            ticker_summary["daily_has_any"]
            & ticker_summary["ohlcv_1m_has_any"]
            & ticker_summary["quotes_has_any"]
            & ticker_summary["trades_has_any"]
            & (
                ticker_summary["income_has_any"]
                | ticker_summary["balance_has_any"]
                | ticker_summary["cash_flow_has_any"]
                | ticker_summary["ratio_has_any"]
            )
        ),
    }
    rows = []
    for combo_key, mask in combos.items():
        count = int(mask.fillna(False).sum())
        rows.append(
            {
                "combo_key": combo_key,
                "combo_label": combo_key,
                "tickers_count": count,
                "pct_universe": round(100.0 * count / max(lt1b_count, 1), 4),
            }
        )
    return pd.DataFrame(rows).sort_values(["tickers_count", "combo_key"], ascending=[False, True]).reset_index(drop=True)


def _build_case_index(ticker_summary: pd.DataFrame) -> pd.DataFrame:
    out = ticker_summary[
        [
            "ticker",
            "classification_1b",
            "pti_start",
            "pti_end",
            "coverage_bucket",
            "market_datasets_present_count",
            "daily_coverage_pct",
            "ohlcv_1m_coverage_pct",
            "quotes_coverage_pct",
            "trades_coverage_pct",
            "top_gap_dataset",
        ]
    ].copy()
    rank_score = []
    for row in out.itertuples(index=False):
        coverage_sum = sum(
            float(0 if pd.isna(v) else v)
            for v in [row.daily_coverage_pct, row.ohlcv_1m_coverage_pct, row.quotes_coverage_pct, row.trades_coverage_pct]
        )
        pti_start = pd.Timestamp(row.pti_start) if not pd.isna(row.pti_start) else pd.NaT
        pti_end = pd.Timestamp(row.pti_end) if not pd.isna(row.pti_end) else pd.NaT
        if pd.isna(pti_start) or pd.isna(pti_end):
            months_span = 0
        else:
            months_span = len(pd.period_range(pti_start.to_period("M"), pti_end.to_period("M"), freq="M"))
        rank_score.append(round((4 * 100.0 - coverage_sum) + months_span, 4))
    out["top_gap_month"] = pd.NaT
    out["rank_score"] = rank_score
    out["display_label"] = (
        out["ticker"].astype(str)
        + " | "
        + pd.to_datetime(out["pti_start"], errors="coerce").dt.strftime("%Y-%m").fillna("NA")
        + " .. "
        + pd.to_datetime(out["pti_end"], errors="coerce").dt.strftime("%Y-%m").fillna("NA")
        + " | "
        + out["coverage_bucket"].astype(str)
    )
    return out.sort_values(["rank_score", "ticker"], ascending=[False, True]).reset_index(drop=True)


def _write_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def build_artifacts(args: argparse.Namespace) -> None:
    started_at_utc = _utcnow_iso()
    start_perf = time.perf_counter()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    _ensure_exists(
        [
            args.lt1b_universe,
            args.daily_inventory,
            args.ohlcv_1m_inventory,
            args.quotes_inventory,
            args.trades_inventory,
            args.quotes_current,
            args.trades_current,
            args.halts_master,
            args.financial_income_root,
            args.financial_balance_root,
            args.financial_cash_flow_root,
            args.financial_ratio_root,
        ]
    )

    _log("build.start", output_root=str(output_root))

    lt1b = pd.read_parquet(
        args.lt1b_universe,
        columns=["ticker", "first_seen_date", "last_observed_date", "classification_1b", "classification_reason_1b"],
    ).copy()
    lt1b["ticker"] = _normalize_ticker(lt1b["ticker"])
    lt1b["pti_start"] = pd.to_datetime(lt1b["first_seen_date"], errors="coerce")
    lt1b["pti_end"] = pd.to_datetime(lt1b["last_observed_date"], errors="coerce")
    lt1b = lt1b.dropna(subset=["ticker", "pti_start", "pti_end"]).copy()
    lt1b = lt1b.loc[lt1b["pti_end"] >= lt1b["pti_start"]].copy()
    lt1b = lt1b.drop_duplicates(subset=["ticker"]).copy()
    lt1b = lt1b[["ticker", "pti_start", "pti_end", "classification_1b", "classification_reason_1b"]].sort_values("ticker").reset_index(drop=True)
    lt1b["pti_months"] = [
        len(pd.period_range(start=s.to_period("M"), end=e.to_period("M"), freq="M"))
        for s, e in zip(lt1b["pti_start"], lt1b["pti_end"])
    ]
    _log("build.universe_loaded", tickers=len(lt1b))

    pti_grid = _build_pti_month_grid(lt1b)
    _log("build.pti_grid_ready", rows=len(pti_grid))

    daily_inv = pd.read_parquet(args.daily_inventory).copy()
    daily_inv["ticker"] = _normalize_ticker(daily_inv["ticker"])
    daily_month_presence = _months_between_from_inventory(daily_inv)
    daily_month_presence = _clip_month_presence_to_pti(daily_month_presence, pti_grid)
    daily_summary = _summarize_month_presence(daily_month_presence, "daily")

    ohlcv_1m_inv = pd.read_parquet(args.ohlcv_1m_inventory).copy()
    ohlcv_1m_inv["ticker"] = _normalize_ticker(ohlcv_1m_inv["ticker"])
    ohlcv_1m_month_presence = _ohlcv_1m_months_from_inventory(ohlcv_1m_inv)
    ohlcv_1m_month_presence = _clip_month_presence_to_pti(ohlcv_1m_month_presence, pti_grid)
    ohlcv_1m_summary = _summarize_month_presence(ohlcv_1m_month_presence, "ohlcv_1m")

    quotes_scan = _scan_dense_current_months(args.quotes_current, "quotes", args.quotes_batch_size, args.max_dense_batches)
    trades_scan = _scan_dense_current_months(args.trades_current, "trades", args.trades_batch_size, args.max_dense_batches)
    quotes_scan.month_presence = _clip_month_presence_to_pti(quotes_scan.month_presence, pti_grid)
    quotes_scan.summary = _summarize_month_presence(quotes_scan.month_presence, "quotes")
    trades_scan.month_presence = _clip_month_presence_to_pti(trades_scan.month_presence, pti_grid)
    trades_scan.summary = _summarize_month_presence(trades_scan.month_presence, "trades")

    halts_month_overlay, halts_summary = _scan_halts_overlay(args.halts_master)
    halts_month_overlay = _clip_month_presence_to_pti(halts_month_overlay, pti_grid)
    halts_summary = (
        pd.DataFrame(columns=["ticker", "halts_has_any", "halts_events_total", "halts_first_date", "halts_last_date", "halts_months_present"])
        if halts_month_overlay.empty
        else halts_month_overlay.groupby("ticker", as_index=False).agg(
            halts_events_total=("halts_events_count", "sum"),
            halts_first_date=("month", "min"),
            halts_last_date=("month", "max"),
            halts_months_present=("month", "nunique"),
        )
    )
    if not halts_summary.empty:
        halts_summary["halts_has_any"] = halts_summary["halts_events_total"] > 0
        halts_summary = halts_summary[["ticker", "halts_has_any", "halts_events_total", "halts_first_date", "halts_last_date", "halts_months_present"]]
    income_month_overlay, income_summary = _scan_financial_overlay(
        args.financial_income_root, "income", ["filing_date", "period_end"], "has_income", "income_events_count", "income_events_total", args.max_financial_files
    )
    income_month_overlay = _clip_month_presence_to_pti(income_month_overlay, pti_grid)
    income_summary = _summarize_month_presence(income_month_overlay[["ticker", "month"]], "income")
    if not income_summary.empty and "income_months_present" in income_summary.columns:
        income_summary["income_events_total"] = income_month_overlay.groupby("ticker")["income_events_count"].sum().reindex(income_summary["ticker"]).values
    balance_month_overlay, balance_summary = _scan_financial_overlay(
        args.financial_balance_root, "balance", ["filing_date", "period_end"], "has_balance", "balance_events_count", "balance_events_total", args.max_financial_files
    )
    balance_month_overlay = _clip_month_presence_to_pti(balance_month_overlay, pti_grid)
    balance_summary = _summarize_month_presence(balance_month_overlay[["ticker", "month"]], "balance")
    if not balance_summary.empty and "balance_months_present" in balance_summary.columns:
        balance_summary["balance_events_total"] = balance_month_overlay.groupby("ticker")["balance_events_count"].sum().reindex(balance_summary["ticker"]).values
    cash_flow_month_overlay, cash_flow_summary = _scan_financial_overlay(
        args.financial_cash_flow_root, "cash_flow", ["filing_date", "period_end"], "has_cash_flow", "cash_flow_events_count", "cash_flow_events_total", args.max_financial_files
    )
    cash_flow_month_overlay = _clip_month_presence_to_pti(cash_flow_month_overlay, pti_grid)
    cash_flow_summary = _summarize_month_presence(cash_flow_month_overlay[["ticker", "month"]], "cash_flow")
    if not cash_flow_summary.empty and "cash_flow_months_present" in cash_flow_summary.columns:
        cash_flow_summary["cash_flow_events_total"] = cash_flow_month_overlay.groupby("ticker")["cash_flow_events_count"].sum().reindex(cash_flow_summary["ticker"]).values
    ratio_month_overlay, ratio_summary = _scan_financial_overlay(
        args.financial_ratio_root, "ratio", ["date"], "has_ratio", "ratio_points_count", "ratio_points_total", args.max_financial_files
    )
    ratio_month_overlay = _clip_month_presence_to_pti(ratio_month_overlay, pti_grid)
    ratio_summary = _summarize_month_presence(ratio_month_overlay[["ticker", "month"]], "ratio")
    if not ratio_summary.empty and "ratio_months_present" in ratio_summary.columns:
        ratio_summary["ratio_points_total"] = ratio_month_overlay.groupby("ticker")["ratio_points_count"].sum().reindex(ratio_summary["ticker"]).values

    ticker_month_coverage = pti_grid[["ticker", "month", "pti_start", "pti_end", "in_pti_window"]].copy()
    dense_months = {
        "daily": daily_month_presence,
        "ohlcv_1m": ohlcv_1m_month_presence,
        "quotes": quotes_scan.month_presence,
        "trades": trades_scan.month_presence,
    }
    for dataset_name, month_df in dense_months.items():
        bool_col = f"has_{dataset_name}"
        month_df = month_df.copy()
        month_df[bool_col] = True
        ticker_month_coverage = _merge_bool_month(ticker_month_coverage, month_df, bool_col)
    for col in ["has_daily", "has_ohlcv_1m", "has_quotes", "has_trades"]:
        if col not in ticker_month_coverage.columns:
            ticker_month_coverage[col] = False
    ticker_month_coverage["market_datasets_present_count"] = ticker_month_coverage[
        ["has_daily", "has_ohlcv_1m", "has_quotes", "has_trades"]
    ].sum(axis=1)
    ticker_month_coverage = ticker_month_coverage.sort_values(["ticker", "month"]).reset_index(drop=True)

    event_month_overlay = pti_grid[["ticker", "month"]].copy()
    overlay_payloads = [
        (halts_month_overlay, "has_halts_event", "halts_events_count"),
        (income_month_overlay, "has_income", "income_events_count"),
        (balance_month_overlay, "has_balance", "balance_events_count"),
        (cash_flow_month_overlay, "has_cash_flow", "cash_flow_events_count"),
        (ratio_month_overlay, "has_ratio", "ratio_points_count"),
    ]
    for overlay_df, bool_col, count_col in overlay_payloads:
        event_month_overlay = _merge_bool_month(event_month_overlay, overlay_df, bool_col)
        event_month_overlay = _merge_count_month(event_month_overlay, overlay_df, count_col)
    event_month_overlay = event_month_overlay.rename(
        columns={
            "has_income": "has_income_statement",
            "has_balance": "has_balance_sheet",
            "has_cash_flow": "has_cash_flow_statement",
        }
    ).sort_values(["ticker", "month"]).reset_index(drop=True)

    ticker_summary = lt1b.copy()
    for summary_df in [
        daily_summary,
        ohlcv_1m_summary,
        quotes_scan.summary,
        trades_scan.summary,
        halts_summary,
        income_summary,
        balance_summary,
        cash_flow_summary,
        ratio_summary,
    ]:
        if not summary_df.empty:
            ticker_summary = ticker_summary.merge(summary_df, on="ticker", how="left")

    bool_fill_cols = [
        "daily_has_any",
        "ohlcv_1m_has_any",
        "quotes_has_any",
        "trades_has_any",
        "halts_has_any",
        "income_has_any",
        "balance_has_any",
        "cash_flow_has_any",
        "ratio_has_any",
    ]
    for col in bool_fill_cols:
        if col not in ticker_summary.columns:
            ticker_summary[col] = False
        ticker_summary[col] = ticker_summary[col].astype("boolean").fillna(False).astype(bool)

    count_fill_cols = [
        "daily_months_present",
        "ohlcv_1m_months_present",
        "quotes_months_present",
        "trades_months_present",
        "halts_events_total",
        "halts_months_present",
        "income_events_total",
        "income_months_present",
        "balance_events_total",
        "balance_months_present",
        "cash_flow_events_total",
        "cash_flow_months_present",
        "ratio_points_total",
        "ratio_months_present",
    ]
    for col in count_fill_cols:
        if col not in ticker_summary.columns:
            ticker_summary[col] = 0
        ticker_summary[col] = pd.to_numeric(ticker_summary[col], errors="coerce").fillna(0).astype("int64")

    for dataset_name in ["daily", "ohlcv_1m", "quotes", "trades"]:
        ticker_summary[f"{dataset_name}_coverage_pct"] = (
            100.0 * ticker_summary[f"{dataset_name}_months_present"] / ticker_summary["pti_months"].clip(lower=1)
        ).round(4)

    ticker_summary = _assign_coverage_bucket(ticker_summary)
    ticker_summary = ticker_summary.sort_values("ticker").reset_index(drop=True)

    exec_summary = pd.DataFrame(
        [
            {
                "universe_name": "lt1b_active_inactive",
                "as_of_date": pd.Timestamp.today().normalize(),
                "lt1b_tickers_total": int(len(lt1b)),
                "pti_min_date": lt1b["pti_start"].min(),
                "pti_max_date": lt1b["pti_end"].max(),
                "pti_month_rows_total": int(len(pti_grid)),
                "tickers_with_daily": int(ticker_summary["daily_has_any"].sum()),
                "tickers_with_ohlcv_1m": int(ticker_summary["ohlcv_1m_has_any"].sum()),
                "tickers_with_quotes": int(ticker_summary["quotes_has_any"].sum()),
                "tickers_with_trades": int(ticker_summary["trades_has_any"].sum()),
                "tickers_with_any_market_data": int(
                    (
                        ticker_summary["daily_has_any"]
                        | ticker_summary["ohlcv_1m_has_any"]
                        | ticker_summary["quotes_has_any"]
                        | ticker_summary["trades_has_any"]
                    ).sum()
                ),
                "tickers_with_all_market_data": int((ticker_summary["coverage_bucket"] == "all_market_data").sum()),
                "tickers_with_halts": int(ticker_summary["halts_has_any"].sum()),
                "tickers_with_income": int(ticker_summary["income_has_any"].sum()),
                "tickers_with_balance": int(ticker_summary["balance_has_any"].sum()),
                "tickers_with_cash_flow": int(ticker_summary["cash_flow_has_any"].sum()),
                "tickers_with_ratio": int(ticker_summary["ratio_has_any"].sum()),
            }
        ]
    )

    dataset_rows = []
    dataset_specs = [
        ("daily", "dense_market", "daily_has_any", daily_month_presence),
        ("ohlcv_1m", "dense_market", "ohlcv_1m_has_any", ohlcv_1m_month_presence),
        ("quotes", "dense_market", "quotes_has_any", quotes_scan.month_presence),
        ("trades", "dense_market", "trades_has_any", trades_scan.month_presence),
        ("halts", "event", "halts_has_any", halts_month_overlay[["ticker", "month"]] if not halts_month_overlay.empty else pd.DataFrame(columns=["ticker", "month"])),
        ("income", "fundamental", "income_has_any", income_month_overlay[["ticker", "month"]] if not income_month_overlay.empty else pd.DataFrame(columns=["ticker", "month"])),
        ("balance", "fundamental", "balance_has_any", balance_month_overlay[["ticker", "month"]] if not balance_month_overlay.empty else pd.DataFrame(columns=["ticker", "month"])),
        ("cash_flow", "fundamental", "cash_flow_has_any", cash_flow_month_overlay[["ticker", "month"]] if not cash_flow_month_overlay.empty else pd.DataFrame(columns=["ticker", "month"])),
        ("ratio", "fundamental", "ratio_has_any", ratio_month_overlay[["ticker", "month"]] if not ratio_month_overlay.empty else pd.DataFrame(columns=["ticker", "month"])),
    ]
    for dataset, kind, bool_col, month_df in dataset_specs:
        tickers_with_data = int(ticker_summary[bool_col].sum())
        months_with_data = int(len(month_df.drop_duplicates())) if not month_df.empty else 0
        obs_min = month_df["month"].min() if not month_df.empty else pd.NaT
        obs_max = month_df["month"].max() if not month_df.empty else pd.NaT
        dataset_rows.append(
            {
                "dataset": dataset,
                "dataset_kind": kind,
                "tickers_with_data": tickers_with_data,
                "tickers_without_data": int(len(lt1b) - tickers_with_data),
                "months_with_data": months_with_data,
                "obs_min_date": obs_min,
                "obs_max_date": obs_max,
                "coverage_vs_universe_pct": round(100.0 * tickers_with_data / max(len(lt1b), 1), 4),
            }
        )
    dataset_coverage_summary = pd.DataFrame(dataset_rows).sort_values(["dataset_kind", "dataset"]).reset_index(drop=True)

    dataset_overlap_summary = _build_overlap_summary(ticker_summary, len(lt1b))
    case_index_coverage = _build_case_index(ticker_summary)

    _write_df(exec_summary, output_root / "exec_summary.parquet")
    _write_df(dataset_coverage_summary, output_root / "dataset_coverage_summary.parquet")
    _write_df(dataset_overlap_summary, output_root / "dataset_overlap_summary.parquet")
    _write_df(ticker_summary, output_root / "ticker_coverage_summary.parquet")
    _write_df(ticker_month_coverage, output_root / "ticker_month_coverage.parquet")
    _write_df(event_month_overlay, output_root / "event_month_overlay.parquet")
    _write_df(case_index_coverage, output_root / "case_index_coverage.parquet")

    manifest = {
        "build_name": "lt1b_coverage_artifacts",
        "build_version": "0.1.0",
        "built_at_utc": _utcnow_iso(),
        "output_root": str(output_root),
        "universe_source": str(args.lt1b_universe),
        "inputs": {
            "lt1b_universe_parquet": str(args.lt1b_universe),
            "daily_inventory_by_ticker": str(args.daily_inventory),
            "ohlcv_1m_inventory_by_ticker": str(args.ohlcv_1m_inventory),
            "quotes_inventory_by_ticker": str(args.quotes_inventory),
            "trades_inventory_by_ticker": str(args.trades_inventory),
            "quotes_current": str(args.quotes_current),
            "trades_current": str(args.trades_current),
            "halts_master_multisource": str(args.halts_master),
            "financial_income_root": str(args.financial_income_root),
            "financial_balance_root": str(args.financial_balance_root),
            "financial_cash_flow_root": str(args.financial_cash_flow_root),
            "financial_ratios_root": str(args.financial_ratio_root),
        },
        "artifacts": {
            "exec_summary": "exec_summary.parquet",
            "dataset_coverage_summary": "dataset_coverage_summary.parquet",
            "dataset_overlap_summary": "dataset_overlap_summary.parquet",
            "ticker_coverage_summary": "ticker_coverage_summary.parquet",
            "ticker_month_coverage": "ticker_month_coverage.parquet",
            "event_month_overlay": "event_month_overlay.parquet",
            "case_index_coverage": "case_index_coverage.parquet",
        },
        "row_counts": {
            "lt1b_tickers": int(len(lt1b)),
            "ticker_month_rows": int(len(ticker_month_coverage)),
            "ticker_coverage_rows": int(len(ticker_summary)),
            "event_overlay_rows": int(len(event_month_overlay)),
            "case_index_rows": int(len(case_index_coverage)),
        },
        "build_params": {
            "month_grain": True,
            "quotes_batch_size": int(args.quotes_batch_size),
            "trades_batch_size": int(args.trades_batch_size),
            "include_financial_overlays": True,
            "include_halts_overlay": True,
            "max_dense_batches": args.max_dense_batches,
            "max_financial_files": args.max_financial_files,
            "daily_month_logic": "approx_from_inventory_year_range",
            "ohlcv_1m_month_logic": "approx_from_inventory_range",
            "quotes_month_logic": "exact_from_current_chunked",
            "trades_month_logic": "exact_from_current_chunked",
        },
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    finished_at_utc = _utcnow_iso()
    build_log = {
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "duration_sec": round(time.perf_counter() - start_perf, 3),
        "steps": [
            "load_universe",
            "build_pti_month_grid",
            "load_daily",
            "load_ohlcv_1m",
            "scan_quotes_current",
            "scan_trades_current",
            "scan_halts",
            "scan_financials",
            "write_artifacts",
        ],
        "warnings": [
            "daily monthly coverage is approximated from yearly inventory range",
            "ohlcv_1m monthly coverage is approximated from inventory ranges",
        ],
    }
    (output_root / "build_log.json").write_text(json.dumps(build_log, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    _log("build.end", output_root=str(output_root), duration_sec=round(time.perf_counter() - start_perf, 3))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build lt1b coverage artifacts for the general audit notebook.")
    parser.add_argument("--lt1b-universe", type=Path, default=LT1B_UNIVERSE_PARQUET)
    parser.add_argument("--daily-inventory", type=Path, default=DAILY_INVENTORY_BY_TICKER)
    parser.add_argument("--ohlcv-1m-inventory", type=Path, default=OHLCV_1M_INVENTORY_BY_TICKER)
    parser.add_argument("--quotes-inventory", type=Path, default=QUOTES_INVENTORY_BY_TICKER)
    parser.add_argument("--trades-inventory", type=Path, default=TRADES_INVENTORY_BY_TICKER)
    parser.add_argument("--quotes-current", type=Path, default=QUOTES_CURRENT_PARQUET)
    parser.add_argument("--trades-current", type=Path, default=TRADES_CURRENT_PARQUET)
    parser.add_argument("--halts-master", type=Path, default=HALTS_MASTER_PARQUET)
    parser.add_argument("--financial-income-root", type=Path, default=FINANCIAL_INCOME_ROOT)
    parser.add_argument("--financial-balance-root", type=Path, default=FINANCIAL_BALANCE_ROOT)
    parser.add_argument("--financial-cash-flow-root", type=Path, default=FINANCIAL_CASH_FLOW_ROOT)
    parser.add_argument("--financial-ratio-root", type=Path, default=FINANCIAL_RATIO_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--quotes-batch-size", type=int, default=100_000)
    parser.add_argument("--trades-batch-size", type=int, default=100_000)
    parser.add_argument("--max-dense-batches", type=int, default=None)
    parser.add_argument("--max-financial-files", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    build_artifacts(parse_args())


if __name__ == "__main__":
    main()
