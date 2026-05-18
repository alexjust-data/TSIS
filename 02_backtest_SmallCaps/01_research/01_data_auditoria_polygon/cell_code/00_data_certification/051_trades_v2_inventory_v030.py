from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

PATTERN_MARKET = re.compile(
    r"^(?P<ticker>[^\\/]+)[\\/]+year=(?P<year>\d{4})[\\/]+month=(?P<month>\d{2})[\\/]+day=(?P<date>\d{4}-\d{2}-\d{2})[\\/]+market\.parquet$",
    re.IGNORECASE,
)
INVENTORY_COLUMNS = [
    "root",
    "root_path",
    "file",
    "relpath",
    "ticker",
    "date",
    "year",
    "month",
    "day",
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
    m = PATTERN_MARKET.match(rel)
    if not m:
        return None
    ticker = str(m.group("ticker")).upper().strip()
    date = str(m.group("date"))
    return {
        "ticker": ticker,
        "date": date,
        "year": int(m.group("year")),
        "month": int(m.group("month")),
        "day": date,
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


def deterministic_market_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames.sort()
        if "market.parquet" not in filenames:
            continue
        yield Path(dirpath) / "market.parquet"


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
        "date": parsed["date"],
        "year": parsed["year"],
        "month": parsed["month"],
        "day": parsed["day"],
        "task_key": f"{parsed['ticker']}|{parsed['date']}",
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
        df = df.sort_values(["ticker", "date", "file"]).reset_index(drop=True)
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

    for file_path in deterministic_market_files(root):
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
        df = df.sort_values(["ticker", "date", "root", "file"]).reset_index(drop=True)
    return df


def summarize_inventory(df: pd.DataFrame, label: str) -> dict[str, Any]:
    if df.empty:
        return {
            "root": label,
            "rows": 0,
            "task_keys": 0,
            "tickers": 0,
            "date_min": None,
            "date_max": None,
            "total_bytes": 0,
        }
    return {
        "root": label,
        "rows": int(len(df)),
        "task_keys": int(df["task_key"].nunique()),
        "tickers": int(df["ticker"].nunique()),
        "date_min": str(df["date"].min()),
        "date_max": str(df["date"].max()),
        "total_bytes": int(pd.to_numeric(df["size_bytes"], errors="coerce").fillna(0).sum()),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build trades_inventory_files for Agent02 v2")
    ap.add_argument("--c-root", default=r"C:\TSIS_Data\data\trades_ticks_prod_2005_2026")
    ap.add_argument("--d-root", default=r"D:\trades_ticks_prod_2005_2026")
    ap.add_argument("--outdir", default="")
    ap.add_argument("--limit-per-root", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=100000)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    c_root = Path(args.c_root)
    d_root = Path(args.d_root)
    if not c_root.exists():
        raise SystemExit(f"c-root not found: {c_root}")
    if not d_root.exists():
        raise SystemExit(f"d-root not found: {d_root}")

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_inventory\{utc_stamp()}_trades_v2_inventory"
    )
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "inventory_batches").mkdir(parents=True, exist_ok=True)

    checkpoint_path = outdir / "inventory_checkpoint.json"
    manifest_path = outdir / "inventory_run_manifest.json"
    checkpoint = load_json(checkpoint_path, checkpoint_default())
    manifest = load_json(manifest_path, manifest_default())
    manifest["updated_utc"] = utc_now()
    manifest["batch_size"] = int(args.batch_size)
    manifest["roots"] = [
        {"label": "C", "path": str(c_root)},
        {"label": "D", "path": str(d_root)},
    ]
    write_json(manifest_path, manifest)

    limit = int(args.limit_per_root) if int(args.limit_per_root) > 0 else None
    checkpoint, manifest = scan_root_incremental(
        c_root,
        "C",
        outdir,
        checkpoint_path,
        manifest_path,
        checkpoint,
        manifest,
        limit_files=limit,
        batch_size=int(args.batch_size),
        resume=bool(args.resume),
    )
    checkpoint, manifest = scan_root_incremental(
        d_root,
        "D",
        outdir,
        checkpoint_path,
        manifest_path,
        checkpoint,
        manifest,
        limit_files=limit,
        batch_size=int(args.batch_size),
        resume=bool(args.resume),
    )

    all_df = load_batch_frames(outdir)
    c_df = all_df[all_df["root"] == "C"].copy() if not all_df.empty else empty_inventory_df()
    d_df = all_df[all_df["root"] == "D"].copy() if not all_df.empty else empty_inventory_df()

    by_ticker = (
        all_df.groupby("ticker", dropna=False)
        .agg(
            files_total=("file", "count"),
            task_keys=("task_key", "nunique"),
            roots_present=("root", lambda s: "|".join(sorted(set(map(str, s))))),
            date_min=("date", "min"),
            date_max=("date", "max"),
            bytes_total=("size_bytes", lambda s: int(pd.to_numeric(s, errors="coerce").fillna(0).sum())),
        )
        .reset_index()
        if not all_df.empty
        else pd.DataFrame(
            columns=["ticker", "files_total", "task_keys", "roots_present", "date_min", "date_max", "bytes_total"]
        )
    )

    files_parquet = outdir / "trades_inventory_files.parquet"
    files_csv = outdir / "trades_inventory_files.csv"
    by_ticker_parquet = outdir / "trades_inventory_by_ticker.parquet"
    by_ticker_csv = outdir / "trades_inventory_by_ticker.csv"
    summary_json = outdir / "trades_inventory_summary.json"

    all_df.to_parquet(files_parquet, index=False)
    all_df.to_csv(files_csv, index=False)
    by_ticker.to_parquet(by_ticker_parquet, index=False)
    by_ticker.to_csv(by_ticker_csv, index=False)

    summary = {
        "outdir": str(outdir),
        "c_root": str(c_root),
        "d_root": str(d_root),
        "resume": bool(args.resume),
        "batch_size": int(args.batch_size),
        "c_inventory": summarize_inventory(c_df, "C"),
        "d_inventory": summarize_inventory(d_df, "D"),
        "all_rows": int(len(all_df)),
        "all_task_keys": int(all_df["task_key"].nunique()) if not all_df.empty else 0,
        "all_tickers": int(all_df["ticker"].nunique()) if not all_df.empty else 0,
        "outputs": {
            "trades_inventory_files_parquet": str(files_parquet),
            "trades_inventory_files_csv": str(files_csv),
            "trades_inventory_by_ticker_parquet": str(by_ticker_parquet),
            "trades_inventory_by_ticker_csv": str(by_ticker_csv),
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
