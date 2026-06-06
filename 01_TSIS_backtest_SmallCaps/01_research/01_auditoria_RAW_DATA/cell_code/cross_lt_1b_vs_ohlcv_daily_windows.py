from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

DEFAULT_TARGET = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet")
DEFAULT_OHLCV_ROOT = Path(r"D:\ohlcv_daily")
DEFAULT_OUT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\lt_1b_vs_ohlcv_daily_windows")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Cruza universo <1B vs ventanas observadas en D:\\ohlcv_daily")
    ap.add_argument("--target-parquet", default=str(DEFAULT_TARGET))
    ap.add_argument("--ohlcv-root", default=str(DEFAULT_OHLCV_ROOT))
    ap.add_argument("--outdir", default="")
    ap.add_argument("--limit-tickers", type=int, default=0)
    return ap.parse_args()


def load_target(path: Path, limit_tickers: int = 0) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe target parquet: {path}")
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise RuntimeError(f"Falta columna ticker en {path}")
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    for c in ["first_seen_date", "last_observed_date", "last_row_date", "anchor_date_used", "shares_observed_date", "shares_period_end"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce").dt.normalize()
    df = df[df["ticker"] != ""].drop_duplicates(subset=["ticker"], keep="first").sort_values("ticker").reset_index(drop=True)
    if limit_tickers and limit_tickers > 0:
        df = df.head(limit_tickers).copy()
    return df


def scan_one_ticker(ticker: str, root: Path) -> dict[str, object]:
    tdir = root / f"ticker={ticker}"
    if not tdir.exists():
        return {
            "ticker": ticker,
            "has_ohlcv_daily": False,
            "ohlcv_first_day": pd.NaT,
            "ohlcv_last_day": pd.NaT,
            "ohlcv_files_ok": 0,
            "ohlcv_files_bad": 0,
            "ohlcv_rows": 0,
        }

    parquet_files = sorted(tdir.rglob("*.parquet"))
    first_date = None
    last_date = None
    files_ok = 0
    files_bad = 0
    row_count = 0

    for fp in parquet_files:
        try:
            pf = pq.ParquetFile(fp)
            names = pf.schema.names
            if "date" not in names:
                files_bad += 1
                continue
            tbl = pf.read(columns=["date"])
            if tbl.num_rows == 0:
                continue
            s = pd.Series(tbl.column("date").to_pylist(), dtype="object")
            s = pd.to_datetime(s, errors="coerce").dropna().dt.normalize()
            if s.empty:
                files_bad += 1
                continue
            f0 = s.min()
            f1 = s.max()
            first_date = f0 if first_date is None else min(first_date, f0)
            last_date = f1 if last_date is None else max(last_date, f1)
            row_count += int(len(s))
            files_ok += 1
        except Exception:
            files_bad += 1

    return {
        "ticker": ticker,
        "has_ohlcv_daily": bool(first_date is not None and last_date is not None),
        "ohlcv_first_day": first_date,
        "ohlcv_last_day": last_date,
        "ohlcv_files_ok": files_ok,
        "ohlcv_files_bad": files_bad,
        "ohlcv_rows": row_count,
    }


def main() -> int:
    args = parse_args()
    target_path = Path(args.target_parquet)
    ohlcv_root = Path(args.ohlcv_root)
    if args.outdir:
        outdir = Path(args.outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = DEFAULT_OUT_ROOT / f"{stamp}_cross_lt_1b_vs_ohlcv_daily_windows"
    outdir.mkdir(parents=True, exist_ok=True)

    target = load_target(target_path, limit_tickers=args.limit_tickers)
    rows: list[dict[str, object]] = []
    total = len(target)

    for i, tk in enumerate(target["ticker"].tolist(), start=1):
        rows.append(scan_one_ticker(tk, ohlcv_root))
        if i == 1 or i % 250 == 0 or i == total:
            print(f"scan_target_vs_ohlcv_daily: tickers={i}/{total}")

    obs = pd.DataFrame(rows)
    out = target.merge(obs, on="ticker", how="left")
    out["ohlcv_span_days"] = (out["ohlcv_last_day"] - out["ohlcv_first_day"]).dt.days
    out["delta_first_vs_first_seen_days"] = (out["ohlcv_first_day"] - out["first_seen_date"]).dt.days
    out["delta_last_vs_last_observed_days"] = (out["ohlcv_last_day"] - out["last_observed_date"]).dt.days

    status = []
    for _, r in out.iterrows():
        if not bool(r.get("has_ohlcv_daily", False)):
            status.append("NO_OHLCV_DAILY")
            continue
        d0 = r.get("delta_first_vs_first_seen_days")
        d1 = r.get("delta_last_vs_last_observed_days")
        if pd.notna(d0) and pd.notna(d1) and int(d0) == 0 and int(d1) == 0:
            status.append("MATCH_PTI_WINDOW")
        else:
            status.append("WINDOW_DIFFERS")
    out["window_compare_status"] = status

    summary = {
        "target_path": str(target_path),
        "ohlcv_root": str(ohlcv_root),
        "outdir": str(outdir),
        "target_tickers": int(len(target)),
        "with_ohlcv_daily": int(out["has_ohlcv_daily"].fillna(False).sum()),
        "without_ohlcv_daily": int((~out["has_ohlcv_daily"].fillna(False)).sum()),
        "match_pti_window": int((out["window_compare_status"] == "MATCH_PTI_WINDOW").sum()),
        "window_differs": int((out["window_compare_status"] == "WINDOW_DIFFERS").sum()),
        "no_ohlcv_daily": int((out["window_compare_status"] == "NO_OHLCV_DAILY").sum()),
    }

    out.to_parquet(outdir / "lt_1b_vs_ohlcv_daily_windows.parquet", index=False)
    out.to_csv(outdir / "lt_1b_vs_ohlcv_daily_windows.csv", index=False)
    out[out["window_compare_status"] == "WINDOW_DIFFERS"].to_csv(outdir / "window_differs.csv", index=False)
    out[out["window_compare_status"] == "NO_OHLCV_DAILY"].to_csv(outdir / "no_ohlcv_daily.csv", index=False)
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"saved: {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
