from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

DEFAULT_TASKS = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_tasks\20260322_221029_build_quotes_lt_1b_master_from_ohlcv_windows\tasks_quotes_lt_1b_master.csv")
DEFAULT_QUOTES_ROOT = Path(r"D:\quotes")
DEFAULT_OUT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_missing_only")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Construye missing_only de quotes restando task master vs D:\\quotes")
    ap.add_argument("--tasks-csv", default=str(DEFAULT_TASKS))
    ap.add_argument("--quotes-root", default=str(DEFAULT_QUOTES_ROOT))
    ap.add_argument("--outdir", default="")
    ap.add_argument("--limit-rows", type=int, default=0)
    ap.add_argument("--block-size", type=int, default=250000)
    ap.add_argument("--resume", action="store_true")
    return ap.parse_args()


def load_tasks(path: Path, limit_rows: int = 0) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe tasks csv: {path}")
    df = pd.read_csv(path).copy()
    required = {"ticker", "date"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Faltan columnas en tasks csv: {sorted(missing)}")
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df = df[df["ticker"] != ""].dropna(subset=["date"]).drop_duplicates(subset=["ticker", "date"], keep="first")
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    if limit_rows and limit_rows > 0:
        df = df.head(limit_rows).copy()
    return df.reset_index(drop=True)


def expected_quote_path(quotes_root: Path, ticker: str, dt_val: pd.Timestamp) -> Path:
    yyyy = dt_val.strftime("%Y")
    mm = dt_val.strftime("%m")
    dd = dt_val.strftime("%d")
    return quotes_root / ticker / f"year={yyyy}" / f"month={mm}" / f"day={dd}" / "quotes.parquet"


def load_partial_csv(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=columns)
    df = pd.read_csv(path)
    for c in columns:
        if c not in df.columns:
            df[c] = pd.NA
    return df[columns].copy()


def main() -> int:
    args = parse_args()
    tasks_path = Path(args.tasks_csv)
    quotes_root = Path(args.quotes_root)
    if args.outdir:
        outdir = Path(args.outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = DEFAULT_OUT_ROOT / f"{stamp}_build_quotes_lt_1b_missing_only_from_disk"
    outdir.mkdir(parents=True, exist_ok=True)

    audit_csv = outdir / "tasks_quotes_lt_1b_disk_audit.csv"
    missing_csv = outdir / "tasks_quotes_lt_1b_missing_only.csv"
    keep_csv = outdir / "tasks_quotes_lt_1b_keep_existing.csv"
    manifest_json = outdir / "tasks_quotes_lt_1b_missing_manifest.json"
    progress_json = outdir / "tasks_quotes_lt_1b_missing_progress.json"
    partial_audit_csv = outdir / "tasks_quotes_lt_1b_disk_audit.partial.csv"
    partial_missing_csv = outdir / "tasks_quotes_lt_1b_missing_only.partial.csv"
    partial_keep_csv = outdir / "tasks_quotes_lt_1b_keep_existing.partial.csv"

    tasks = load_tasks(tasks_path, limit_rows=args.limit_rows)
    total = len(tasks)

    processed = 0
    if args.resume and progress_json.exists():
        try:
            progress = json.loads(progress_json.read_text(encoding="utf-8"))
            processed = int(progress.get("processed", 0))
        except Exception:
            processed = 0
    processed = max(0, min(processed, total))

    if processed > 0 and args.resume:
        print(f"resume: true | already_processed={processed}/{total}")
    else:
        print(f"resume: {bool(args.resume)} | already_processed=0/{total}")

    t0 = time.time()
    for block_start in range(processed, total, args.block_size):
        block_end = min(block_start + args.block_size, total)
        block = tasks.iloc[block_start:block_end].copy()

        rows = []
        for r in block.itertuples(index=False):
            ticker = str(r.ticker)
            dt_val = pd.Timestamp(r.date)
            exp = expected_quote_path(quotes_root, ticker, dt_val)
            exists = exp.exists()
            rows.append({
                "ticker": ticker,
                "date": dt_val.date().isoformat(),
                "expected_file": str(exp),
                "exists_in_disk": bool(exists),
                "action": "KEEP_EXISTING" if exists else "MISSING_ONLY_DOWNLOAD",
            })

        audit_block = pd.DataFrame(rows)
        missing_block = audit_block[audit_block["action"] == "MISSING_ONLY_DOWNLOAD"][ ["ticker", "date"] ].copy()
        keep_block = audit_block[audit_block["action"] == "KEEP_EXISTING"][ ["ticker", "date"] ].copy()

        write_header = not partial_audit_csv.exists() or block_start == 0 and processed == 0
        audit_block.to_csv(partial_audit_csv, mode="a", header=write_header, index=False)
        missing_block.to_csv(partial_missing_csv, mode="a", header=(not partial_missing_csv.exists() or block_start == 0 and processed == 0), index=False)
        keep_block.to_csv(partial_keep_csv, mode="a", header=(not partial_keep_csv.exists() or block_start == 0 and processed == 0), index=False)

        done = block_end
        elapsed = time.time() - t0
        block_rows = len(audit_block)
        rate = (done - processed) / elapsed if elapsed > 0 else 0.0
        remaining = total - done
        eta_sec = int(remaining / rate) if rate > 0 else None

        progress = {
            "status": "running",
            "processed": int(done),
            "total": int(total),
            "progress_pct": round(100.0 * done / total, 2) if total else 100.0,
            "block_start": int(block_start + 1),
            "block_end": int(block_end),
            "block_size": int(block_rows),
            "elapsed_sec_this_run": round(elapsed, 2),
            "rate_rows_per_sec_this_run": round(rate, 2),
            "eta_sec": eta_sec,
            "updated_at_utc": utc_now(),
            "partial_audit_csv": str(partial_audit_csv),
            "partial_missing_csv": str(partial_missing_csv),
            "partial_keep_csv": str(partial_keep_csv),
        }
        progress_json.write_text(json.dumps(progress, indent=2), encoding="utf-8")

        eta_txt = f"{eta_sec/60:.1f}m" if eta_sec is not None else "n/a"
        print(
            f"[block] rows={block_start+1}-{block_end}/{total} | "
            f"done={done}/{total} ({progress['progress_pct']:.2f}%) | "
            f"elapsed={elapsed/60:.1f}m | eta={eta_txt} | "
            f"keep={len(keep_block)} | missing={len(missing_block)}"
        )

    audit = load_partial_csv(partial_audit_csv, ["ticker", "date", "expected_file", "exists_in_disk", "action"])
    missing_only = load_partial_csv(partial_missing_csv, ["ticker", "date"])
    keep_existing = load_partial_csv(partial_keep_csv, ["ticker", "date"])

    audit.to_csv(audit_csv, index=False)
    missing_only.to_csv(missing_csv, index=False)
    keep_existing.to_csv(keep_csv, index=False)

    manifest = {
        "tasks_csv": str(tasks_path),
        "quotes_root": str(quotes_root),
        "outdir": str(outdir),
        "tasks_total": int(len(tasks)),
        "keep_existing": int(len(keep_existing)),
        "missing_only": int(len(missing_only)),
        "date_min": str(tasks["date"].min().date()) if len(tasks) else None,
        "date_max": str(tasks["date"].max().date()) if len(tasks) else None,
        "block_size": int(args.block_size),
        "resume": bool(args.resume),
    }
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    progress = {
        "status": "completed",
        "processed": int(total),
        "total": int(total),
        "progress_pct": 100.0,
        "updated_at_utc": utc_now(),
        "audit_csv": str(audit_csv),
        "missing_csv": str(missing_csv),
        "keep_csv": str(keep_csv),
        "manifest_json": str(manifest_json),
    }
    progress_json.write_text(json.dumps(progress, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(manifest, indent=2))
    print(f"saved: {missing_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
