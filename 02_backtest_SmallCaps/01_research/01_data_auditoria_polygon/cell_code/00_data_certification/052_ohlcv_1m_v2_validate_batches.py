from __future__ import annotations

import argparse
import importlib.util
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR_PATH = SCRIPT_DIR / "050_ohlcv_1m_v2_validate_file.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_validator_module():
    spec = importlib.util.spec_from_file_location("ohlcv_1m_v2_validate_file_mod", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load validator module from {VALIDATOR_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VALIDATOR_MOD = load_validator_module()
VALIDATOR_VERSION = getattr(VALIDATOR_MOD, "VALIDATOR_VERSION", "ohlcv_1m_v2_validate_file/unknown")
validate_ohlcv_1m_file = getattr(VALIDATOR_MOD, "validate_ohlcv_1m_file")


def choose_expected_root(root_path: str) -> Path | None:
    s = str(root_path or "").strip()
    return Path(s) if s else None


def worker_validate(task: dict[str, Any]) -> dict[str, Any]:
    return validate_ohlcv_1m_file(
        file_path=Path(task["file"]),
        expected_root=choose_expected_root(task.get("root_path", "")),
        run_id=task["run_id"],
        batch_id=task["batch_id"],
        scan_reason=task["scan_reason"],
        validation_kind=task["validation_kind"],
        min_expected_price=float(task["min_expected_price"]),
        min_active_days_warn=int(task["min_active_days_warn"]),
        max_gap_days_warn=int(task["max_gap_days_warn"]),
    )


def build_outdir(base_outdir: str) -> Path:
    if str(base_outdir).strip():
        outdir = Path(base_outdir)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_validation") / f"{stamp}_ohlcv_1m_v2_validation"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "events_batches").mkdir(parents=True, exist_ok=True)
    return outdir


def load_inventory(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Inventory parquet not found: {path}")
    return pd.read_parquet(path)


def load_ticker_allowlist(args: argparse.Namespace) -> set[str]:
    allowlist: set[str] = set()
    parquet_path = str(getattr(args, "tickers_parquet", "") or "").strip()
    csv_path = str(getattr(args, "tickers_csv", "") or "").strip()

    if parquet_path:
        p = Path(parquet_path)
        if not p.exists():
            raise FileNotFoundError(f"Tickers parquet not found: {p}")
        df = pd.read_parquet(p)
        if "ticker" not in df.columns:
            raise ValueError(f"Tickers parquet missing 'ticker' column: {p}")
        allowlist |= {
            str(x).strip().upper()
            for x in df["ticker"].dropna().tolist()
            if str(x).strip()
        }

    if csv_path:
        p = Path(csv_path)
        if not p.exists():
            raise FileNotFoundError(f"Tickers csv not found: {p}")
        df = pd.read_csv(p)
        if "ticker" not in df.columns:
            raise ValueError(f"Tickers csv missing 'ticker' column: {p}")
        allowlist |= {
            str(x).strip().upper()
            for x in df["ticker"].dropna().tolist()
            if str(x).strip()
        }

    return allowlist


def apply_filters(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    out = df.copy()
    ticker_allowlist = load_ticker_allowlist(args)
    if ticker_allowlist:
        out = out[out["ticker"].astype(str).str.upper().isin(ticker_allowlist)]
    if str(args.root).strip():
        roots = {x.strip().upper() for x in str(args.root).split(",") if x.strip()}
        out = out[out["root"].astype(str).str.upper().isin(roots)]
    if str(args.ticker).strip():
        tickers = {x.strip().upper() for x in str(args.ticker).split(",") if x.strip()}
        out = out[out["ticker"].astype(str).str.upper().isin(tickers)]
    if str(args.year_from).strip():
        out = out[pd.to_numeric(out["year"], errors="coerce") >= int(args.year_from)]
    if str(args.year_to).strip():
        out = out[pd.to_numeric(out["year"], errors="coerce") <= int(args.year_to)]
    if str(args.month_from).strip():
        out = out[pd.to_numeric(out["month"], errors="coerce") >= int(args.month_from)]
    if str(args.month_to).strip():
        out = out[pd.to_numeric(out["month"], errors="coerce") <= int(args.month_to)]
    if int(args.limit) > 0:
        out = out.head(int(args.limit)).copy()
    return out.reset_index(drop=True)


def chunk_dataframe(df: pd.DataFrame, chunk_size: int) -> list[pd.DataFrame]:
    if chunk_size <= 0:
        return [df]
    return [df.iloc[start:start + chunk_size].copy() for start in range(0, len(df), chunk_size)]


def summarize_batch(events_df: pd.DataFrame) -> dict[str, Any]:
    sev = events_df["severity"].value_counts(dropna=False).to_dict() if not events_df.empty else {}
    return {
        "rows": int(len(events_df)),
        "severity_counts": {str(k): int(v) for k, v in sev.items()},
    }


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
        "started_at_utc": None,
        "last_completed_batch_id": None,
        "completed_batch_ids": [],
        "completed_batches_count": 0,
        "validated_rows_total": 0,
        "events_rows_total": 0,
        "status": "initialized",
    }


def manifest_default() -> dict[str, Any]:
    return {
        "version": 1,
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "run_id": None,
        "inventory_parquet": None,
        "validator_version": VALIDATOR_VERSION,
        "filters": {},
        "chunk_size": None,
        "workers": None,
        "batch_files": [],
        "finalized": False,
    }


def existing_batch_ids(events_dir: Path) -> set[str]:
    return {p.stem for p in events_dir.glob("batch_*.parquet")}


def merge_manifest_batch_files(manifest: dict[str, Any], events_dir: Path) -> dict[str, Any]:
    existing = {str(entry.get("batch_id")): entry for entry in manifest.get("batch_files", []) if str(entry.get("batch_id", "")).strip()}
    for path in sorted(events_dir.glob("batch_*.parquet")):
        batch_id = path.stem
        if batch_id not in existing:
            existing[batch_id] = {
                "batch_id": batch_id,
                "path": str(path),
                "rows": None,
                "files_selected": None,
                "events_written": None,
                "severity_counts_json": None,
                "materialized_at_utc": None,
            }
    manifest["batch_files"] = [existing[k] for k in sorted(existing.keys())]
    return manifest


def write_manifest_exports(outdir: Path, manifest: dict[str, Any]) -> None:
    rows = []
    for entry in manifest.get("batch_files", []):
        rows.append(
            {
                "batch_id": entry.get("batch_id"),
                "batch_path": entry.get("path"),
                "files_selected": entry.get("files_selected"),
                "events_written": entry.get("events_written"),
                "severity_counts_json": entry.get("severity_counts_json"),
                "materialized_at_utc": entry.get("materialized_at_utc"),
            }
        )
    manifest_df = pd.DataFrame(rows)
    manifest_df.to_csv(outdir / "batch_manifest_ohlcv_1m_v2.csv", index=False)
    if not manifest_df.empty:
        manifest_df.to_parquet(outdir / "batch_manifest_ohlcv_1m_v2.parquet", index=False)


def load_severity_counts_from_parquet(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    df = pd.read_parquet(path, columns=["severity"])
    if df.empty or "severity" not in df.columns:
        return {}
    return {str(k): int(v) for k, v in df["severity"].value_counts(dropna=False).to_dict().items()}


def recompute_total_counts(manifest: dict[str, Any], events_dir: Path) -> dict[str, int]:
    total: dict[str, int] = {}
    for entry in manifest.get("batch_files", []):
        path = Path(str(entry.get("path", "")).strip())
        if not path.exists():
            path = events_dir / f"{entry.get('batch_id')}.parquet"
        counts = load_severity_counts_from_parquet(path)
        for key, value in counts.items():
            total[key] = total.get(key, 0) + int(value)
    return total


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate ohlcv_1m inventory in parallel and write append-only batch events")
    ap.add_argument("--inventory-parquet", required=True)
    ap.add_argument("--outdir", default="")
    ap.add_argument("--run-id", default="manual_ohlcv_1m_v2")
    ap.add_argument("--scan-reason", default="manual_recheck")
    ap.add_argument("--validation-kind", default="revalidation_only")
    ap.add_argument("--workers", type=int, default=max(1, min(8, (os.cpu_count() or 4))))
    ap.add_argument("--chunk-size", type=int, default=1000)
    ap.add_argument("--root", default="")
    ap.add_argument("--ticker", default="")
    ap.add_argument("--tickers-parquet", default="")
    ap.add_argument("--tickers-csv", default="")
    ap.add_argument("--year-from", default="")
    ap.add_argument("--year-to", default="")
    ap.add_argument("--month-from", default="")
    ap.add_argument("--month-to", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min-expected-price", type=float, default=0.0)
    ap.add_argument("--min-active-days-warn", type=int, default=3)
    ap.add_argument("--max-gap-days-warn", type=int, default=10)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    outdir = build_outdir(args.outdir)
    events_dir = outdir / "events_batches"
    checkpoint_path = outdir / "validation_checkpoint.json"
    manifest_path = outdir / "validation_run_manifest.json"

    checkpoint = load_json(checkpoint_path, checkpoint_default())
    manifest = load_json(manifest_path, manifest_default())
    manifest["run_id"] = args.run_id
    manifest["inventory_parquet"] = str(Path(args.inventory_parquet))
    manifest["validator_version"] = VALIDATOR_VERSION
    manifest["chunk_size"] = int(args.chunk_size)
    manifest["workers"] = int(args.workers)
    manifest["filters"] = {
        "root": args.root,
        "ticker": args.ticker,
        "tickers_parquet": args.tickers_parquet,
        "tickers_csv": args.tickers_csv,
        "year_from": args.year_from,
        "year_to": args.year_to,
        "month_from": args.month_from,
        "month_to": args.month_to,
        "limit": int(args.limit),
    }
    manifest["updated_utc"] = utc_now()
    manifest["finalized"] = False
    manifest = merge_manifest_batch_files(manifest, events_dir)
    write_json(manifest_path, manifest)

    inventory_df = load_inventory(Path(args.inventory_parquet))
    selected_df = apply_filters(inventory_df, args)
    batches = chunk_dataframe(selected_df, int(args.chunk_size))

    if selected_df.empty:
        summary = {
            "run_id": args.run_id,
            "validator_version": VALIDATOR_VERSION,
            "started_at_utc": utc_now(),
            "finished_at_utc": utc_now(),
            "inventory_parquet": str(Path(args.inventory_parquet)),
            "outdir": str(outdir),
            "selected_files": 0,
            "workers": int(args.workers),
            "chunk_size": int(args.chunk_size),
            "batches_written": 0,
            "severity_counts_total": {},
            "filters": manifest["filters"],
            "resume": bool(args.resume),
        }
        checkpoint["updated_utc"] = utc_now()
        checkpoint["status"] = "completed"
        write_json(checkpoint_path, checkpoint)
        manifest["finalized"] = True
        write_json(manifest_path, manifest)
        write_manifest_exports(outdir, manifest)
        (outdir / "validation_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return

    started_at_utc = checkpoint.get("started_at_utc") if args.resume and checkpoint.get("started_at_utc") else utc_now()
    checkpoint["started_at_utc"] = started_at_utc
    checkpoint["status"] = "running"
    checkpoint["updated_utc"] = utc_now()
    write_json(checkpoint_path, checkpoint)

    completed_batches = set(map(str, checkpoint.get("completed_batch_ids", [])))
    completed_batches |= existing_batch_ids(events_dir)
    manifest = merge_manifest_batch_files(manifest, events_dir)
    total_counts = recompute_total_counts(manifest, events_dir)

    executor = ProcessPoolExecutor(max_workers=int(args.workers)) if int(args.workers) > 1 else None
    try:
        for idx, batch_df in enumerate(batches, start=1):
            batch_id = f"batch_{idx:06d}"
            batch_path = events_dir / f"{batch_id}.parquet"

            if args.resume and (batch_id in completed_batches) and batch_path.exists():
                print(f"[resume] skip {batch_id} existing={batch_path}")
                continue

            tasks: list[dict[str, Any]] = []
            for row in batch_df.to_dict(orient="records"):
                row["run_id"] = args.run_id
                row["batch_id"] = batch_id
                row["scan_reason"] = args.scan_reason
                row["validation_kind"] = args.validation_kind
                row["min_expected_price"] = args.min_expected_price
                row["min_active_days_warn"] = args.min_active_days_warn
                row["max_gap_days_warn"] = args.max_gap_days_warn
                tasks.append(row)

            results: list[dict[str, Any]] = []
            if executor is None:
                for task in tasks:
                    results.append(worker_validate(task))
            else:
                futures = [executor.submit(worker_validate, task) for task in tasks]
                for fut in as_completed(futures):
                    results.append(fut.result())

            events_df = pd.DataFrame(results)
            if not events_df.empty:
                events_df = events_df.sort_values(["file"]).reset_index(drop=True)
            events_df.to_parquet(batch_path, index=False)

            batch_summary = summarize_batch(events_df)
            for key, value in batch_summary["severity_counts"].items():
                total_counts[key] = total_counts.get(key, 0) + int(value)

            entry = {
                "batch_id": batch_id,
                "path": str(batch_path),
                "rows": int(len(events_df)),
                "files_selected": int(len(batch_df)),
                "events_written": int(len(events_df)),
                "severity_counts_json": json.dumps(batch_summary["severity_counts"], sort_keys=True),
                "materialized_at_utc": utc_now(),
            }
            existing_entries = {str(e.get("batch_id")): e for e in manifest.get("batch_files", [])}
            existing_entries[batch_id] = entry
            manifest["batch_files"] = [existing_entries[k] for k in sorted(existing_entries.keys())]
            manifest["updated_utc"] = utc_now()
            write_json(manifest_path, manifest)
            write_manifest_exports(outdir, manifest)

            completed_batches.add(batch_id)
            checkpoint["updated_utc"] = utc_now()
            checkpoint["last_completed_batch_id"] = batch_id
            checkpoint["completed_batch_ids"] = sorted(completed_batches)
            checkpoint["completed_batches_count"] = len(completed_batches)
            checkpoint["validated_rows_total"] = int(sum(int(e.get("files_selected") or 0) for e in manifest.get("batch_files", [])))
            checkpoint["events_rows_total"] = int(sum(int(e.get("events_written") or 0) for e in manifest.get("batch_files", [])))
            checkpoint["status"] = "running"
            write_json(checkpoint_path, checkpoint)

            print(f"[{idx}/{len(batches)}] {batch_id} files={len(batch_df)} events={len(events_df)} counts={batch_summary['severity_counts']}")
    finally:
        if executor is not None:
            executor.shutdown(wait=True)

    manifest = merge_manifest_batch_files(manifest, events_dir)
    write_manifest_exports(outdir, manifest)

    finished_at_utc = utc_now()
    manifest["updated_utc"] = finished_at_utc
    manifest["finalized"] = True
    write_json(manifest_path, manifest)

    checkpoint["updated_utc"] = finished_at_utc
    checkpoint["status"] = "completed"
    checkpoint["completed_batch_ids"] = sorted(set(map(str, checkpoint.get("completed_batch_ids", []))) | existing_batch_ids(events_dir))
    checkpoint["completed_batches_count"] = len(checkpoint["completed_batch_ids"])
    checkpoint["validated_rows_total"] = int(sum(int(e.get("files_selected") or 0) for e in manifest.get("batch_files", [])))
    checkpoint["events_rows_total"] = int(sum(int(e.get("events_written") or 0) for e in manifest.get("batch_files", [])))
    write_json(checkpoint_path, checkpoint)

    summary = {
        "run_id": args.run_id,
        "validator_version": VALIDATOR_VERSION,
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "inventory_parquet": str(Path(args.inventory_parquet)),
        "outdir": str(outdir),
        "selected_files": int(len(selected_df)),
        "workers": int(args.workers),
        "chunk_size": int(args.chunk_size),
        "batches_written": int(len(manifest.get("batch_files", []))),
        "severity_counts_total": {str(k): int(v) for k, v in total_counts.items()},
        "filters": manifest["filters"],
        "resume": bool(args.resume),
    }
    (outdir / "validation_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
