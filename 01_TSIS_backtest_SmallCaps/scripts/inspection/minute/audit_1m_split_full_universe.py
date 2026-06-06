from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
import sys

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.price_views import build_future_split_factor_series, canonicalize_split_table


@dataclass(frozen=True)
class AuditConfig:
    minute_root: Path
    splits_root: Path
    output_root: Path
    tolerance: float


def _iter_split_files(root: Path) -> Iterable[Path]:
    yield from sorted(root.rglob("splits_*.parquet"))


def _month_path(root: Path, ticker: str, year: int, month: int) -> Path:
    return root / f"ticker={ticker}" / f"year={year}" / f"month={month:02d}" / f"minute_aggs_{ticker}_{year}_{month:02d}.parquet"


def _neighbor_months(event_date: pd.Timestamp) -> list[tuple[int, int]]:
    current = pd.Timestamp(event_date).normalize().replace(day=1)
    prev = (current - pd.offsets.MonthBegin(1)).normalize()
    nxt = (current + pd.offsets.MonthBegin(1)).normalize()
    months = [(prev.year, prev.month), (current.year, current.month), (nxt.year, nxt.month)]
    seen = set()
    out = []
    for ym in months:
        if ym not in seen:
            seen.add(ym)
            out.append(ym)
    return out


def _load_split_table(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if "_empty" in df.columns and len(df) and bool(df["_empty"].iloc[0]) is True:
        return pd.DataFrame()
    return canonicalize_split_table(df, execution_date_col="execution_date", split_from_col="split_from", split_to_col="split_to")


@lru_cache(maxsize=20000)
def _load_month_dates(path_str: str) -> pd.DataFrame:
    path = Path(path_str)
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path, columns=["date"]).copy()
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.loc[df["date"].notna(), ["date"]].drop_duplicates().sort_values("date").reset_index(drop=True)
    return df


def _load_event_window_dates(minute_root: Path, ticker: str, event_date: pd.Timestamp) -> tuple[pd.DataFrame, list[str]]:
    frames: list[pd.DataFrame] = []
    months_loaded: list[str] = []
    for year, month in _neighbor_months(event_date):
        p = _month_path(minute_root, ticker, year, month)
        if not p.exists():
            continue
        df = _load_month_dates(str(p))
        if df.empty:
            continue
        frames.append(df)
        months_loaded.append(f"{year:04d}-{month:02d}")
    if not frames:
        return pd.DataFrame(), months_loaded
    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates().sort_values(["date"]).reset_index(drop=True)
    return out, months_loaded


def _exclude_one_event(canonical_splits: pd.DataFrame, event_date: pd.Timestamp, split_ratio: float) -> pd.DataFrame:
    mask = (canonical_splits["execution_date"] == event_date) & np.isclose(canonical_splits["split_ratio"], split_ratio, rtol=0, atol=1e-12)
    idx = canonical_splits.index[mask]
    if len(idx) == 0:
        return canonical_splits.copy()
    return canonical_splits.drop(index=idx[0]).reset_index(drop=True)


def audit_event(
    ticker: str,
    event_date: pd.Timestamp,
    split_ratio: float,
    split_from: float,
    split_to: float,
    canonical_splits: pd.DataFrame,
    cfg: AuditConfig,
) -> dict[str, object]:
    frame, months_loaded = _load_event_window_dates(cfg.minute_root, ticker, event_date)
    if frame.empty:
        return {
            "ticker": ticker,
            "event_date": event_date.date().isoformat(),
            "event_year": int(event_date.year),
            "event_month": int(event_date.month),
            "split_from": float(split_from),
            "split_to": float(split_to),
            "split_ratio": float(split_ratio),
            "months_loaded": "",
            "days_total": 0,
            "days_pre": 0,
            "days_post": 0,
            "pre_fail_days": 0,
            "post_fail_days": 0,
            "max_abs_multiplier_error": np.nan,
            "status": "NO_1M_COVERAGE",
        }

    full_factor = build_future_split_factor_series(frame["date"], canonical_splits)
    splits_without_event = _exclude_one_event(canonical_splits, event_date, split_ratio)
    base_factor = build_future_split_factor_series(frame["date"], splits_without_event)
    observed_multiplier = pd.to_numeric(full_factor, errors="coerce") / pd.to_numeric(base_factor, errors="coerce")

    date_series = pd.to_datetime(frame["date"], errors="coerce")
    pre_mask = date_series.lt(event_date)
    post_mask = ~pre_mask
    expected = pd.Series(np.where(pre_mask, split_ratio, 1.0), index=frame.index, dtype="float64")
    abs_err = (observed_multiplier - expected).abs()
    pre_fail = int((pre_mask & abs_err.gt(cfg.tolerance)).sum())
    post_fail = int((post_mask & abs_err.gt(cfg.tolerance)).sum())
    rows_pre = int(pre_mask.sum())
    rows_post = int(post_mask.sum())

    if rows_pre == 0:
        status = "NO_PRE_COVERAGE"
    elif rows_post == 0:
        status = "NO_POST_COVERAGE"
    elif pre_fail > 0 or post_fail > 0:
        status = "FAIL"
    else:
        status = "PASS"

    return {
        "ticker": ticker,
        "event_date": event_date.date().isoformat(),
        "event_year": int(event_date.year),
        "event_month": int(event_date.month),
        "split_from": float(split_from),
        "split_to": float(split_to),
        "split_ratio": float(split_ratio),
        "months_loaded": ",".join(months_loaded),
        "days_total": int(len(frame)),
        "days_pre": rows_pre,
        "days_post": rows_post,
        "pre_fail_days": pre_fail,
        "post_fail_days": post_fail,
        "max_abs_multiplier_error": float(abs_err.max()) if abs_err.notna().any() else np.nan,
        "status": status,
    }


def _summarize(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["status", "n_cases"])
    out = df.groupby("status", dropna=False).size().reset_index(name="n_cases").sort_values("status").reset_index(drop=True)
    total = int(out["n_cases"].sum())
    out["pct_cases"] = out["n_cases"] / total * 100.0 if total else 0.0
    return out


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Audita exhaustivamente todos los casos de split con cobertura real en `1m`.")
    ap.add_argument("--minute-root", default=r"D:\ohlcv_1m")
    ap.add_argument("--splits-root", default=r"C:\TSIS_Data\data\additional\corporate_actions\splits")
    ap.add_argument(
        "--output-root",
        default=r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\inspection_dossiers\1m_split_normalized\evidence_assets\full_universe_split_audit",
    )
    ap.add_argument("--tolerance", type=float, default=1e-12)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg = AuditConfig(
        minute_root=Path(args.minute_root),
        splits_root=Path(args.splits_root),
        output_root=Path(args.output_root),
        tolerance=float(args.tolerance),
    )
    rows: list[dict[str, object]] = []
    split_files_seen = 0
    non_empty_split_files = 0

    for split_file in _iter_split_files(cfg.splits_root):
        split_files_seen += 1
        ticker = split_file.stem.replace("splits_", "", 1).upper()
        ticker_dir = cfg.minute_root / f"ticker={ticker}"
        if not ticker_dir.exists():
            continue
        canonical = _load_split_table(split_file)
        if canonical.empty:
            continue
        non_empty_split_files += 1
        original = pd.read_parquet(split_file).copy()
        if "_empty" in original.columns and len(original) and bool(original["_empty"].iloc[0]) is True:
            continue
        original["execution_date"] = pd.to_datetime(original["execution_date"], errors="coerce")
        original["split_from"] = pd.to_numeric(original["split_from"], errors="coerce")
        original["split_to"] = pd.to_numeric(original["split_to"], errors="coerce")
        original = original.loc[original["execution_date"].notna()].copy()
        original = original.loc[original["split_from"].gt(0) & original["split_to"].gt(0)].copy()
        original["split_ratio"] = original["split_to"] / original["split_from"]
        original = original.sort_values("execution_date").reset_index(drop=True)

        for _, ev in original.iterrows():
            rows.append(
                audit_event(
                    ticker=ticker,
                    event_date=pd.Timestamp(ev["execution_date"]).normalize(),
                    split_ratio=float(ev["split_ratio"]),
                    split_from=float(ev["split_from"]),
                    split_to=float(ev["split_to"]),
                    canonical_splits=canonical,
                    cfg=cfg,
                )
            )

    cases = pd.DataFrame(rows).sort_values(["ticker", "event_date"]).reset_index(drop=True) if rows else pd.DataFrame()
    summary = _summarize(cases)
    meta = pd.DataFrame(
        [
            {
                "split_files_seen": split_files_seen,
                "non_empty_split_files_with_1m_ticker": non_empty_split_files,
                "total_event_cases": int(len(cases)),
                "pass_cases": int((cases["status"] == "PASS").sum()) if not cases.empty else 0,
                "fail_cases": int((cases["status"] == "FAIL").sum()) if not cases.empty else 0,
                "no_pre_cases": int((cases["status"] == "NO_PRE_COVERAGE").sum()) if not cases.empty else 0,
                "no_post_cases": int((cases["status"] == "NO_POST_COVERAGE").sum()) if not cases.empty else 0,
                "no_1m_coverage_cases": int((cases["status"] == "NO_1M_COVERAGE").sum()) if not cases.empty else 0,
            }
        ]
    )

    cfg.output_root.mkdir(parents=True, exist_ok=True)
    cases.to_csv(cfg.output_root / "full_universe_split_event_cases.csv", index=False)
    cases.to_parquet(cfg.output_root / "full_universe_split_event_cases.parquet", index=False)
    summary.to_csv(cfg.output_root / "full_universe_split_event_status_summary.csv", index=False)
    meta.to_csv(cfg.output_root / "full_universe_split_event_audit_meta.csv", index=False)

    print("META")
    print(meta.to_string(index=False))
    print("\nSTATUS SUMMARY")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
