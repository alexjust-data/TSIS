from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


DEFAULT_TASKS = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_lt_1b_tasks\20260324_200919_build_trades_lt_1b_master_from_ohlcv_windows\tasks_trades_lt_1b_master.csv"
)
DEFAULT_INVENTORY = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\polygon_realtime_audit\trades_ticks_prod_2005_2026\inputs\trades_ticks_final_file_paths.txt"
)
DEFAULT_OUT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_lt_1b_missing_only")

TRADES_PATH_RE = re.compile(
    r"^[A-Za-z]:\\trades_ticks_prod_2005_2026\\([^\\]+)\\year=\d{4}\\month=\d{2}\\day=(\d{4}-\d{2}-\d{2})\\market\.parquet$",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Construye missing_only de trades a partir del inventario real de D:")
    ap.add_argument("--tasks-csv", default=str(DEFAULT_TASKS))
    ap.add_argument("--inventory-txt", default=str(DEFAULT_INVENTORY))
    ap.add_argument("--outdir", default="")
    ap.add_argument("--limit-rows", type=int, default=0)
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
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df[df["ticker"] != ""].dropna(subset=["date"]).drop_duplicates(subset=["ticker", "date"], keep="first")
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    if limit_rows and limit_rows > 0:
        df = df.head(limit_rows).copy()
    return df


def load_inventory_keys(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe inventory txt: {path}")

    rows: list[dict[str, str]] = []
    total = 0
    matched = 0

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            total += 1
            m = TRADES_PATH_RE.match(s)
            if not m:
                continue
            matched += 1
            rows.append({"ticker": m.group(1).strip().upper(), "date": m.group(2), "existing_file": s})

    inv = pd.DataFrame(rows)
    if len(inv):
        inv = inv.drop_duplicates(subset=["ticker", "date"], keep="first").sort_values(["ticker", "date"]).reset_index(drop=True)

    print(f"inventory_lines_total={total}")
    print(f"inventory_paths_matched={matched}")
    print(f"inventory_unique_keys={len(inv)}")
    return inv


def main() -> int:
    args = parse_args()
    tasks_path = Path(args.tasks_csv)
    inventory_path = Path(args.inventory_txt)

    if args.outdir:
        outdir = Path(args.outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = DEFAULT_OUT_ROOT / f"{stamp}_build_trades_lt_1b_missing_only_from_inventory"
    outdir.mkdir(parents=True, exist_ok=True)

    tasks = load_tasks(tasks_path, limit_rows=args.limit_rows)
    inv = load_inventory_keys(inventory_path)

    merged = tasks.merge(inv, on=["ticker", "date"], how="left")
    merged["exists_in_D"] = merged["existing_file"].notna()
    merged["action"] = merged["exists_in_D"].map({True: "KEEP_EXISTING_IN_D", False: "MISSING_ONLY_DOWNLOAD"})

    keep_existing = merged.loc[merged["exists_in_D"], ["ticker", "date", "existing_file"]].copy().reset_index(drop=True)
    missing_only = merged.loc[~merged["exists_in_D"], ["ticker", "date"]].copy().reset_index(drop=True)

    audit_csv = outdir / "tasks_trades_lt_1b_inventory_audit.csv"
    keep_csv = outdir / "tasks_trades_lt_1b_keep_existing_in_D.csv"
    missing_csv = outdir / "tasks_trades_lt_1b_missing_only.csv"
    manifest_json = outdir / "tasks_trades_lt_1b_missing_manifest.json"

    merged.to_csv(audit_csv, index=False)
    keep_existing.to_csv(keep_csv, index=False)
    missing_only.to_csv(missing_csv, index=False)

    manifest = {
        "tasks_csv": str(tasks_path),
        "inventory_txt": str(inventory_path),
        "outdir": str(outdir),
        "tasks_total": int(len(tasks)),
        "keep_existing_in_D": int(len(keep_existing)),
        "missing_only": int(len(missing_only)),
        "date_min": str(tasks["date"].min()) if len(tasks) else None,
        "date_max": str(tasks["date"].max()) if len(tasks) else None,
    }
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(manifest, indent=2))
    print(f"saved: {missing_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
