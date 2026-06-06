from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


DEFAULT_PING_MASTER = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\ping_range_master.parquet")
DEFAULT_OHLCV_ROOT = Path(r"D:\ohlcv_daily")
DEFAULT_OUT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\data_quality\ping_vs_ohlcv_daily")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Compara ping_range_master vs first/last day observados en D:\\ohlcv_daily")
    ap.add_argument("--ping-master", default=str(DEFAULT_PING_MASTER))
    ap.add_argument("--ohlcv-root", default=str(DEFAULT_OHLCV_ROOT))
    ap.add_argument("--outdir", default="")
    ap.add_argument("--limit-tickers", type=int, default=0)
    return ap.parse_args()


def load_ping_master(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe ping master: {path}")
    df = pd.read_parquet(path).copy()
    required = {"ticker", "has_data", "first_day", "last_day"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Ping master incompleto. Faltan columnas: {sorted(missing)}")
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df = df[df["ticker"] != ""]
    df["has_data"] = df["has_data"].fillna(False).astype(bool)
    df["first_day"] = pd.to_datetime(df["first_day"], errors="coerce").dt.normalize()
    df["last_day"] = pd.to_datetime(df["last_day"], errors="coerce").dt.normalize()
    df = (
        df.groupby("ticker", as_index=False)
        .agg(
            has_data=("has_data", "max"),
            ping_first_day=("first_day", "min"),
            ping_last_day=("last_day", "max"),
        )
        .sort_values("ticker")
        .reset_index(drop=True)
    )
    return df


def scan_ohlcv_daily(root: Path, limit_tickers: int = 0) -> pd.DataFrame:
    if not root.exists():
        raise FileNotFoundError(f"No existe ohlcv root: {root}")

    ticker_dirs = sorted([p for p in root.glob("ticker=*") if p.is_dir()])
    if limit_tickers and limit_tickers > 0:
        ticker_dirs = ticker_dirs[:limit_tickers]

    rows: list[dict[str, object]] = []
    total = len(ticker_dirs)

    for i, tdir in enumerate(ticker_dirs, start=1):
        ticker = tdir.name.split("=", 1)[1].strip().upper()
        parquet_files = sorted(tdir.rglob("*.parquet"))
        first_date = None
        last_date = None
        files_ok = 0
        files_bad = 0
        row_count = 0

        for fp in parquet_files:
            try:
                tbl = pq.read_table(fp, columns=["date"])
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

        rows.append(
            {
                "ticker": ticker,
                "ohlcv_first_day": first_date,
                "ohlcv_last_day": last_date,
                "ohlcv_files_ok": files_ok,
                "ohlcv_files_bad": files_bad,
                "ohlcv_rows": row_count,
            }
        )

        if i == 1 or i % 250 == 0 or i == total:
            print(f"scan_ohlcv_daily: tickers={i}/{total}")

    out = pd.DataFrame(rows)
    if len(out):
        out = out.sort_values("ticker").reset_index(drop=True)
    return out


def classify_row(r: pd.Series) -> str:
    in_ping = pd.notna(r.get("ping_first_day")) or pd.notna(r.get("ping_last_day")) or bool(r.get("has_data", False))
    in_ohlcv = pd.notna(r.get("ohlcv_first_day")) or pd.notna(r.get("ohlcv_last_day"))
    if in_ping and in_ohlcv:
        start_match = r.get("delta_first_days") == 0 if pd.notna(r.get("delta_first_days")) else False
        end_match = r.get("delta_last_days") == 0 if pd.notna(r.get("delta_last_days")) else False
        if start_match and end_match:
            return "MATCH"
        return "MISMATCH"
    if in_ping and not in_ohlcv:
        return "PING_ONLY"
    if in_ohlcv and not in_ping:
        return "OHLCV_ONLY"
    return "NO_DATA"


def main() -> int:
    args = parse_args()

    ping_path = Path(args.ping_master)
    ohlcv_root = Path(args.ohlcv_root)
    if args.outdir:
        outdir = Path(args.outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = DEFAULT_OUT_ROOT / f"{stamp}_compare_ping_master_vs_ohlcv_daily"
    outdir.mkdir(parents=True, exist_ok=True)

    ping = load_ping_master(ping_path)
    ohlcv = scan_ohlcv_daily(ohlcv_root, limit_tickers=args.limit_tickers)

    cmp = ping.merge(ohlcv, on="ticker", how="outer")
    cmp["delta_first_days"] = (cmp["ohlcv_first_day"] - cmp["ping_first_day"]).dt.days
    cmp["delta_last_days"] = (cmp["ohlcv_last_day"] - cmp["ping_last_day"]).dt.days
    cmp["comparison_status"] = cmp.apply(classify_row, axis=1)

    summary = {
        "ping_master_path": str(ping_path),
        "ohlcv_root": str(ohlcv_root),
        "outdir": str(outdir),
        "ping_tickers": int(len(ping)),
        "ohlcv_tickers": int(len(ohlcv)),
        "intersection_tickers": int(cmp[cmp["comparison_status"].isin(["MATCH", "MISMATCH"])]["ticker"].nunique()),
        "match": int((cmp["comparison_status"] == "MATCH").sum()),
        "mismatch": int((cmp["comparison_status"] == "MISMATCH").sum()),
        "ping_only": int((cmp["comparison_status"] == "PING_ONLY").sum()),
        "ohlcv_only": int((cmp["comparison_status"] == "OHLCV_ONLY").sum()),
        "first_day_diff_nonzero": int((cmp["delta_first_days"].fillna(0) != 0).sum()),
        "last_day_diff_nonzero": int((cmp["delta_last_days"].fillna(0) != 0).sum()),
    }

    cmp = cmp.sort_values(["comparison_status", "ticker"]).reset_index(drop=True)

    cmp.to_parquet(outdir / "ping_vs_ohlcv_daily_comparison.parquet", index=False)
    cmp.to_csv(outdir / "ping_vs_ohlcv_daily_comparison.csv", index=False)
    cmp[cmp["comparison_status"] == "MISMATCH"].to_csv(outdir / "mismatch.csv", index=False)
    cmp[cmp["comparison_status"] == "PING_ONLY"].to_csv(outdir / "ping_only.csv", index=False)
    cmp[cmp["comparison_status"] == "OHLCV_ONLY"].to_csv(outdir / "ohlcv_only.csv", index=False)
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"saved: {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
