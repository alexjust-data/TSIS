from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

PATTERN_1M = re.compile(
    r"^ticker=(?P<ticker>[^\\/]+)[\\/]+year=(?P<year>\d{4})[\\/]+month=(?P<month>\d{2})[\\/]+minute_aggs_(?P<filename_ticker>[^_]+)_(?P<filename_year>\d{4})_(?P<filename_month>\d{2})\.parquet$",
    re.IGNORECASE,
)
INVENTORY_COLUMNS = [
    "root",
    "root_path",
    "file",
    "relpath",
    "ticker",
    "year",
    "month",
    "filename_ticker",
    "filename_year",
    "filename_month",
    "task_key",
    "size_bytes",
    "mtime_utc",
    "inventory_seen_utc",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def parse_relpath(relpath: str) -> dict[str, Any] | None:
    rel = relpath.replace("/", "\\")
    m = PATTERN_1M.match(rel)
    if not m:
        return None
    ticker = str(m.group("ticker")).upper().strip()
    year = int(m.group("year"))
    month = int(m.group("month"))
    filename_ticker = str(m.group("filename_ticker")).upper().strip()
    filename_year = int(m.group("filename_year"))
    filename_month = int(m.group("filename_month"))
    return {
        "ticker": ticker,
        "year": year,
        "month": month,
        "filename_ticker": filename_ticker,
        "filename_year": filename_year,
        "filename_month": filename_month,
    }


def empty_inventory_df() -> pd.DataFrame:
    return pd.DataFrame(columns=INVENTORY_COLUMNS)


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return dict(default)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def checkpoint_default() -> dict[str, Any]:
    return {
        "version": 1,
        "updated_utc": None,
        "completed_roots": [],
        "active_root": None,
        "last_relpath_persisted": None,
        "next_batch_index": 1,
        "persisted_rows_total": 0,
        "batches_written": 0,
    }


def manifest_default() -> dict[str, Any]:
    return {
        "version": 1,
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "batch_size": None,
        "roots": [],
        "batch_files": [],
        "finalized": False,
    }


def scandir_dirs(path: Path):
    try:
        with os.scandir(path) as it:
            entries = [e for e in it if e.is_dir()]
    except FileNotFoundError:
        return []
    entries.sort(key=lambda e: e.name)
    return entries


def scandir_files(path: Path):
    try:
        with os.scandir(path) as it:
            entries = [e for e in it if e.is_file()]
    except FileNotFoundError:
        return []
    entries.sort(key=lambda e: e.name)
    return entries


def iter_ticker_dirs(
    root: Path,
    *,
    ticker_filter: str = "",
    ticker_prefix: str = "",
    ticker_allowlist: set[str] | None = None,
    max_tickers: int | None = None,
):
    matched = 0
    ticker_filter_norm = str(ticker_filter).upper().strip()
    ticker_prefix_norm = str(ticker_prefix).upper().strip()

    for entry in scandir_dirs(root):
        if not entry.name.startswith("ticker="):
            continue
        ticker = entry.name.split("=", 1)[1].upper().strip()
        if ticker_allowlist is not None and ticker not in ticker_allowlist:
            continue
        if ticker_filter_norm and ticker != ticker_filter_norm:
            continue
        if ticker_prefix_norm and not ticker.startswith(ticker_prefix_norm):
            continue
        yield ticker, Path(entry.path)
        matched += 1
        if max_tickers is not None and matched >= max_tickers:
            break


def deterministic_1m_files(
    root: Path,
    *,
    ticker_filter: str = "",
    ticker_prefix: str = "",
    ticker_allowlist: set[str] | None = None,
    max_tickers: int | None = None,
):
    for _, ticker_dir in iter_ticker_dirs(
        root,
        ticker_filter=ticker_filter,
        ticker_prefix=ticker_prefix,
        ticker_allowlist=ticker_allowlist,
        max_tickers=max_tickers,
    ):
        for year_entry in scandir_dirs(ticker_dir):
            if not year_entry.name.startswith("year="):
                continue
            year_dir = Path(year_entry.path)
            for month_entry in scandir_dirs(year_dir):
                if not month_entry.name.startswith("month="):
                    continue
                month_dir = Path(month_entry.path)
                for file_entry in scandir_files(month_dir):
                    name = file_entry.name
                    if not name.lower().endswith(".parquet"):
                        continue
                    if not name.lower().startswith("minute_aggs_"):
                        continue
                    yield Path(file_entry.path)


def build_row(root: Path, label: str, file_path: Path) -> dict[str, Any] | None:
    try:
        rel = str(file_path.relative_to(root))
    except Exception:
        rel = file_path.name

    parsed = parse_relpath(rel)
    if parsed is None:
        return None

    try:
        st = file_path.stat()
        size = int(st.st_size)
        mtime_utc = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        size = None
        mtime_utc = None

    return {
        "root": label,
        "root_path": str(root),
        "file": str(file_path),
        "relpath": rel,
        "ticker": parsed["ticker"],
        "year": parsed["year"],
        "month": parsed["month"],
        "filename_ticker": parsed["filename_ticker"],
        "filename_year": parsed["filename_year"],
        "filename_month": parsed["filename_month"],
        "task_key": f"{parsed['ticker']}|{parsed['year']}|{parsed['month']:02d}",
        "size_bytes": size,
        "mtime_utc": mtime_utc,
        "inventory_seen_utc": utc_now(),
    }


def persist_batch(
    rows: list[dict[str, Any]],
    outdir: Path,
    checkpoint_path: Path,
    manifest_path: Path,
    checkpoint: dict[str, Any],
    manifest: dict[str, Any],
    active_root: str,
    last_relpath: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not rows:
        return checkpoint, manifest

    batch_idx = int(checkpoint.get("next_batch_index", 1))
    batch_name = f"inventory_batch_{batch_idx:06d}.parquet"
    batch_path = outdir / "inventory_batches" / batch_name

    df = pd.DataFrame(rows, columns=INVENTORY_COLUMNS)
    if not df.empty:
        df = df.sort_values(["ticker", "year", "month", "file"]).reset_index(drop=True)
    df.to_parquet(batch_path, index=False)

    checkpoint["updated_utc"] = utc_now()
    checkpoint["active_root"] = active_root
    checkpoint["last_relpath_persisted"] = last_relpath
    checkpoint["next_batch_index"] = batch_idx + 1
    checkpoint["persisted_rows_total"] = int(checkpoint.get("persisted_rows_total", 0)) + int(len(df))
    checkpoint["batches_written"] = int(checkpoint.get("batches_written", 0)) + 1
    write_json(checkpoint_path, checkpoint)

    manifest.setdefault("batch_files", []).append(
        {
            "batch_id": batch_idx,
            "path": str(batch_path),
            "rows": int(len(df)),
            "root": active_root,
            "last_relpath_persisted": last_relpath,
            "written_utc": utc_now(),
        }
    )
    manifest["updated_utc"] = utc_now()
    write_json(manifest_path, manifest)
    return checkpoint, manifest


def scan_root_incremental(
    root: Path,
    label: str,
    outdir: Path,
    checkpoint_path: Path,
    manifest_path: Path,
    checkpoint: dict[str, Any],
    manifest: dict[str, Any],
    progress_every: int = 100000,
    limit_files: int | None = None,
    batch_size: int = 100000,
    resume: bool = False,
    ticker_filter: str = "",
    ticker_prefix: str = "",
    ticker_allowlist: set[str] | None = None,
    max_tickers: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    completed_roots = set(map(str, checkpoint.get("completed_roots", [])))
    if resume and label in completed_roots:
        print(f"scan_{label}: already completed in checkpoint, skipping")
        return checkpoint, manifest

    resume_active_root = str(checkpoint.get("active_root") or "")
    resume_last_relpath = str(checkpoint.get("last_relpath_persisted") or "")
    skip_until_relpath = resume and resume_active_root == label and bool(resume_last_relpath)

    buffered_rows: list[dict[str, Any]] = []
    files_seen = 0
    matched = 0

    for file_path in deterministic_1m_files(
        root,
        ticker_filter=ticker_filter,
        ticker_prefix=ticker_prefix,
        ticker_allowlist=ticker_allowlist,
        max_tickers=max_tickers,
    ):
        files_seen += 1
        try:
            rel = str(file_path.relative_to(root))
        except Exception:
            rel = file_path.name

        if skip_until_relpath:
            if rel <= resume_last_relpath:
                continue
            skip_until_relpath = False

        if limit_files is not None and matched >= limit_files:
            break

        row = build_row(root, label, file_path)
        if row is None:
            continue

        buffered_rows.append(row)
        matched += 1

        if matched % progress_every == 0:
            print(f"scan_{label}: matched={matched}")

        if len(buffered_rows) >= batch_size:
            checkpoint, manifest = persist_batch(
                rows=buffered_rows,
                outdir=outdir,
                checkpoint_path=checkpoint_path,
                manifest_path=manifest_path,
                checkpoint=checkpoint,
                manifest=manifest,
                active_root=label,
                last_relpath=rel,
            )
            buffered_rows = []

    if buffered_rows:
        checkpoint, manifest = persist_batch(
            rows=buffered_rows,
            outdir=outdir,
            checkpoint_path=checkpoint_path,
            manifest_path=manifest_path,
            checkpoint=checkpoint,
            manifest=manifest,
            active_root=label,
            last_relpath=buffered_rows[-1]["relpath"],
        )

    completed_roots = set(map(str, checkpoint.get("completed_roots", [])))
    completed_roots.add(label)
    checkpoint["completed_roots"] = sorted(completed_roots)
    checkpoint["active_root"] = None
    checkpoint["last_relpath_persisted"] = None
    checkpoint["updated_utc"] = utc_now()
    write_json(checkpoint_path, checkpoint)

    print(f"scan_{label}: files_seen={files_seen} matched={matched}")
    return checkpoint, manifest


def load_batch_frames(outdir: Path) -> pd.DataFrame:
    batch_dir = outdir / "inventory_batches"
    files = sorted(batch_dir.glob("inventory_batch_*.parquet"))
    if not files:
        return empty_inventory_df()
    frames = [pd.read_parquet(path) for path in files]
    df = pd.concat(frames, ignore_index=True) if frames else empty_inventory_df()
    if not df.empty:
        df = df.sort_values(["ticker", "year", "month", "root", "file"]).reset_index(drop=True)
    return df


def summarize_inventory(df: pd.DataFrame, label: str) -> dict[str, Any]:
    if df.empty:
        return {
            "root": label,
            "rows": 0,
            "task_keys": 0,
            "tickers": 0,
            "year_min": None,
            "year_max": None,
            "month_min": None,
            "month_max": None,
            "total_bytes": 0,
        }
    year_s = pd.to_numeric(df["year"], errors="coerce")
    month_s = pd.to_numeric(df["month"], errors="coerce")
    return {
        "root": label,
        "rows": int(len(df)),
        "task_keys": int(df["task_key"].nunique()),
        "tickers": int(df["ticker"].nunique()),
        "year_min": int(year_s.min()),
        "year_max": int(year_s.max()),
        "month_min": int(month_s.min()),
        "month_max": int(month_s.max()),
        "total_bytes": int(pd.to_numeric(df["size_bytes"], errors="coerce").fillna(0).sum()),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build ohlcv_1m_inventory_files for Agent02 ohlcv_1m v2")
    ap.add_argument("--d-root", default=r"D:\ohlcv_1m")
    ap.add_argument("--outdir", default="")
    ap.add_argument("--limit-per-root", type=int, default=0)
    ap.add_argument("--ticker", default="")
    ap.add_argument("--ticker-prefix", default="")
    ap.add_argument("--tickers-parquet", default="")
    ap.add_argument("--tickers-csv", default="")
    ap.add_argument("--max-tickers", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=100000)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    d_root = Path(args.d_root)
    if not d_root.exists():
        raise SystemExit("No valid roots found for ohlcv_1m inventory")

    roots: list[tuple[str, Path]] = [("D", d_root)]

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_inventory\{utc_stamp()}_ohlcv_1m_v2_inventory"
    )
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "inventory_batches").mkdir(parents=True, exist_ok=True)

    checkpoint_path = outdir / "inventory_checkpoint.json"
    manifest_path = outdir / "inventory_run_manifest.json"
    checkpoint = load_json(checkpoint_path, checkpoint_default())
    manifest = load_json(manifest_path, manifest_default())
    manifest["updated_utc"] = utc_now()
    manifest["batch_size"] = int(args.batch_size)
    manifest["roots"] = [{"label": label, "path": str(root)} for label, root in roots]
    write_json(manifest_path, manifest)

    limit = int(args.limit_per_root) if int(args.limit_per_root) > 0 else None
    max_tickers = int(args.max_tickers) if int(args.max_tickers) > 0 else None
    ticker_allowlist = None
    if str(args.tickers_parquet).strip():
        p = Path(args.tickers_parquet)
        df = pd.read_parquet(p, columns=["ticker"]).copy()
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
        ticker_allowlist = set(df.loc[df["ticker"] != "", "ticker"].drop_duplicates().tolist())
    elif str(args.tickers_csv).strip():
        p = Path(args.tickers_csv)
        df = pd.read_csv(p, usecols=["ticker"]).copy()
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
        ticker_allowlist = set(df.loc[df["ticker"] != "", "ticker"].drop_duplicates().tolist())

    for label, root in roots:
        checkpoint, manifest = scan_root_incremental(
            root,
            label,
            outdir,
            checkpoint_path,
            manifest_path,
            checkpoint,
            manifest,
            limit_files=limit,
            batch_size=int(args.batch_size),
            resume=bool(args.resume),
            ticker_filter=str(args.ticker),
            ticker_prefix=str(args.ticker_prefix),
            ticker_allowlist=ticker_allowlist,
            max_tickers=max_tickers,
        )

    all_df = load_batch_frames(outdir)
    by_root = {label: all_df[all_df["root"] == label].copy() if not all_df.empty else empty_inventory_df() for label, _ in roots}

    by_ticker = (
        all_df.groupby("ticker", dropna=False)
        .agg(
            files_total=("file", "count"),
            task_keys=("task_key", "nunique"),
            roots_present=("root", lambda s: "|".join(sorted(set(map(str, s))))),
            year_min=("year", "min"),
            year_max=("year", "max"),
            month_min=("month", "min"),
            month_max=("month", "max"),
            bytes_total=("size_bytes", lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).sum())),
        )
        .reset_index()
        if not all_df.empty
        else pd.DataFrame(
            columns=["ticker", "files_total", "task_keys", "roots_present", "year_min", "year_max", "month_min", "month_max", "bytes_total"]
        )
    )

    files_parquet = outdir / "ohlcv_1m_inventory_files.parquet"
    files_csv = outdir / "ohlcv_1m_inventory_files.csv"
    by_ticker_parquet = outdir / "ohlcv_1m_inventory_by_ticker.parquet"
    by_ticker_csv = outdir / "ohlcv_1m_inventory_by_ticker.csv"
    summary_json = outdir / "ohlcv_1m_inventory_summary.json"

    all_df.to_parquet(files_parquet, index=False)
    all_df.to_csv(files_csv, index=False)
    by_ticker.to_parquet(by_ticker_parquet, index=False)
    by_ticker.to_csv(by_ticker_csv, index=False)

    summary = {
        "outdir": str(outdir),
        "resume": bool(args.resume),
        "batch_size": int(args.batch_size),
        "ticker_filter": str(args.ticker),
        "ticker_prefix": str(args.ticker_prefix),
        "tickers_parquet": str(args.tickers_parquet),
        "tickers_csv": str(args.tickers_csv),
        "ticker_allowlist_count": int(len(ticker_allowlist)) if ticker_allowlist is not None else None,
        "max_tickers": int(args.max_tickers),
        "roots": {label: str(root) for label, root in roots},
        "inventories": {label: summarize_inventory(df, label) for label, df in by_root.items()},
        "all_rows": int(len(all_df)),
        "all_task_keys": int(all_df["task_key"].nunique()) if not all_df.empty else 0,
        "all_tickers": int(all_df["ticker"].nunique()) if not all_df.empty else 0,
        "outputs": {
            "ohlcv_1m_inventory_files_parquet": str(files_parquet),
            "ohlcv_1m_inventory_files_csv": str(files_csv),
            "ohlcv_1m_inventory_by_ticker_parquet": str(by_ticker_parquet),
            "ohlcv_1m_inventory_by_ticker_csv": str(by_ticker_csv),
            "summary_json": str(summary_json),
            "checkpoint_json": str(checkpoint_path),
            "manifest_json": str(manifest_path),
            "inventory_batches_dir": str(outdir / "inventory_batches"),
        },
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    manifest["updated_utc"] = utc_now()
    manifest["finalized"] = True
    manifest["final_outputs"] = summary["outputs"]
    write_json(manifest_path, manifest)

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
