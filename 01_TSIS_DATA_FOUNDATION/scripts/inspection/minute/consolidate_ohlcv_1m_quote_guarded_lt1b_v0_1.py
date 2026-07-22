from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_DATA_FOUNDATION")
DEFAULT_UNIVERSE_PARQUET = (
    PROJECT_ROOT
    / "runs"
    / "backtest"
    / "market_cap_last_observed_cutoff"
    / "20260320_market_cap_last_observed_cutoff"
    / "market_cap_cutoff_lt_1b_active_inactive.parquet"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded")
REPAIR_SUFFIX = "_repair_manifest.parquet"

CANONICAL_MANIFEST_FIELDS = [
    ("quote_guarded_view", pa.string()),
    ("ticker", pa.string()),
    ("ts_utc", pa.timestamp("ns", tz="UTC")),
    ("minute_utc", pa.timestamp("ns", tz="UTC")),
    ("minute_ny", pa.timestamp("ns", tz="America/New_York")),
    ("session_date", pa.string()),
    ("year", pa.int64()),
    ("month", pa.int64()),
    ("repair_state", pa.string()),
    ("repair_reason", pa.string()),
    ("quote_guarded_repair_applied", pa.bool_()),
    ("o_raw", pa.float64()),
    ("h_raw", pa.float64()),
    ("l_raw", pa.float64()),
    ("c_raw", pa.float64()),
    ("o_qg", pa.float64()),
    ("h_qg", pa.float64()),
    ("l_qg", pa.float64()),
    ("c_qg", pa.float64()),
    ("vw", pa.float64()),
    ("v", pa.float64()),
    ("n", pa.int64()),
    ("vw_quote_guarded_status", pa.string()),
    ("quote_bid_floor", pa.float64()),
    ("quote_bid_p50", pa.float64()),
    ("quote_ask_p50", pa.float64()),
    ("quote_ask_cap", pa.float64()),
    ("quote_mid_p50", pa.float64()),
    ("quote_spread_p50", pa.float64()),
    ("quote_spread_pct_p50", pa.float64()),
    ("quote_count", pa.float64()),
    ("quote_guard_config", pa.string()),
    ("source_ohlcv_path", pa.string()),
    ("source_quotes_path", pa.string()),
    ("manifest_created_at_utc", pa.string()),
    ("run_root", pa.string()),
]
CANONICAL_MANIFEST_SCHEMA = pa.schema(CANONICAL_MANIFEST_FIELDS)
CANONICAL_MANIFEST_COLUMNS = [name for name, _type in CANONICAL_MANIFEST_FIELDS]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _as_paths(values: list[str]) -> list[Path]:
    out: list[Path] = []
    for value in values:
        for token in str(value).split(";"):
            token = token.strip().strip('"')
            if token:
                out.append(Path(token))
    return out


def _load_tickers(path: Path, column: str) -> list[str]:
    frame = pd.read_parquet(path, columns=[column])
    tickers = sorted({str(value).strip().upper() for value in frame[column].dropna() if str(value).strip()})
    if not tickers:
        raise ValueError(f"No tickers loaded from {path}")
    return tickers


def _read_status_json(path: Path) -> dict[str, object] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def collect_completion(run_roots: list[Path], universe: set[str]) -> tuple[pd.DataFrame, set[str]]:
    rows: list[dict[str, object]] = []
    best: dict[str, dict[str, object]] = {}
    for root in run_roots:
        status_dir = root / "ticker_status"
        if not status_dir.exists():
            continue
        for path in status_dir.glob("*.json"):
            status = _read_status_json(path)
            if not status:
                continue
            ticker = str(status.get("ticker", "")).strip().upper()
            if ticker not in universe:
                continue
            row = {
                "ticker": ticker,
                "status": str(status.get("status", "")),
                "run_root": str(root),
                "months_done": int(status.get("months_done", 0) or 0),
                "months_planned": int(status.get("months_planned", 0) or 0),
                "repair_rows": int(status.get("repair_rows", 0) or 0),
                "ohlc_repair_rows": int(status.get("ohlc_repair_rows", 0) or 0),
                "vw_invalid_rows": int(status.get("vw_invalid_rows", 0) or 0),
                "last_heartbeat_utc": str(status.get("last_heartbeat_utc", "")),
                "error": str(status.get("error", "")),
            }
            rows.append(row)
            previous = best.get(ticker)
            if previous is None or row["status"] == "DONE" or previous.get("status") != "DONE":
                best[ticker] = row

    completion_rows: list[dict[str, object]] = []
    done: set[str] = set()
    for ticker in sorted(universe):
        row = best.get(ticker)
        if row is None:
            completion_rows.append(
                {
                    "ticker": ticker,
                    "status": "MISSING_STATUS",
                    "run_root": "",
                    "months_done": 0,
                    "months_planned": 0,
                    "repair_rows": 0,
                    "ohlc_repair_rows": 0,
                    "vw_invalid_rows": 0,
                    "last_heartbeat_utc": "",
                    "error": "",
                }
            )
            continue
        completion_rows.append(row)
        if row["status"] == "DONE":
            done.add(ticker)
    return pd.DataFrame(completion_rows), done


def parse_shard_name(path: Path) -> tuple[str, int, int] | None:
    name = path.name
    if not name.endswith(REPAIR_SUFFIX):
        return None
    stem = name[: -len(REPAIR_SUFFIX)]
    parts = stem.rsplit("_", 2)
    if len(parts) != 3:
        return None
    ticker, year_text, month_text = parts
    try:
        return ticker.upper(), int(year_text), int(month_text)
    except ValueError:
        return None


def collect_shards(run_roots: list[Path], universe: set[str], completed: set[str]) -> pd.DataFrame:
    selected: dict[tuple[str, int, int], dict[str, object]] = {}
    skipped_out_scope = 0
    skipped_incomplete = 0
    malformed = 0
    for run_index, root in enumerate(run_roots):
        shard_dir = root / "repair_shards"
        if not shard_dir.exists():
            continue
        for path in shard_dir.glob(f"*{REPAIR_SUFFIX}"):
            parsed = parse_shard_name(path)
            if parsed is None:
                malformed += 1
                continue
            ticker, year, month = parsed
            if ticker not in universe:
                skipped_out_scope += 1
                continue
            if ticker not in completed:
                skipped_incomplete += 1
                continue
            key = (ticker, year, month)
            selected[key] = {
                "ticker": ticker,
                "year": year,
                "month": month,
                "run_index": run_index,
                "run_root": str(root),
                "repair_shard_path": str(path),
            }
    frame = pd.DataFrame(selected.values())
    if not frame.empty:
        frame = frame.sort_values(["ticker", "year", "month", "run_index"]).reset_index(drop=True)
    frame.attrs["skipped_out_scope_shards"] = skipped_out_scope
    frame.attrs["skipped_incomplete_lt1b_shards"] = skipped_incomplete
    frame.attrs["malformed_shard_names"] = malformed
    return frame


def _unique_tickers(table: pa.Table) -> set[str]:
    if "ticker" not in table.column_names:
        return set()
    values = pc.unique(table["ticker"]).to_pylist()
    return {str(value).strip().upper() for value in values if value is not None and str(value).strip()}


def _normalize_manifest_table(table: pa.Table, shard_path: Path) -> pa.Table:
    present = set(table.column_names)
    expected = set(CANONICAL_MANIFEST_COLUMNS)
    missing = sorted(expected - present)
    unexpected = sorted(present - expected)
    if missing:
        raise ValueError(f"Shard is missing manifest columns {missing}: {shard_path}")
    if unexpected:
        raise ValueError(f"Shard has unexpected manifest columns {unexpected}: {shard_path}")
    return table.select(CANONICAL_MANIFEST_COLUMNS).cast(CANONICAL_MANIFEST_SCHEMA, safe=False)


def write_manifest(
    shard_index: pd.DataFrame,
    manifest_path: Path,
    sample_path: Path,
    status_path: Path,
    universe: set[str],
    *,
    overwrite: bool,
    progress_every: int,
    sample_rows: int,
) -> tuple[int, int]:
    if manifest_path.exists() and not overwrite:
        raise FileExistsError(f"Manifest already exists: {manifest_path}")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists():
        manifest_path.unlink()

    writer: pq.ParquetWriter | None = None
    total_rows = 0
    written_shards = 0
    sample_tables: list[pa.Table] = []
    started = time.time()
    try:
        for idx, row in enumerate(shard_index.itertuples(index=False), start=1):
            shard_path = Path(str(row.repair_shard_path))
            table = pq.read_table(shard_path)
            row_tickers = _unique_tickers(table)
            expected = {str(row.ticker).upper()}
            if not row_tickers:
                raise ValueError(f"Shard has no ticker column or no ticker values: {shard_path}")
            if not row_tickers.issubset(universe):
                raise ValueError(f"Out-of-scope ticker inside shard {shard_path}: {sorted(row_tickers - universe)}")
            if row_tickers != expected:
                raise ValueError(f"Ticker mismatch in shard {shard_path}: expected {sorted(expected)}, got {sorted(row_tickers)}")
            table = _normalize_manifest_table(table, shard_path)

            if writer is None:
                writer = pq.ParquetWriter(manifest_path, CANONICAL_MANIFEST_SCHEMA)
            writer.write_table(table)
            total_rows += table.num_rows
            written_shards += 1

            if sample_rows > 0 and sum(t.num_rows for t in sample_tables) < sample_rows:
                remaining = sample_rows - sum(t.num_rows for t in sample_tables)
                sample_tables.append(table.slice(0, min(remaining, table.num_rows)))

            if progress_every > 0 and (idx % progress_every == 0 or idx == len(shard_index)):
                elapsed = max(0.001, time.time() - started)
                atomic_write_json(
                    status_path,
                    {
                        "observed_at_utc": utc_now(),
                        "stage": "writing_manifest",
                        "shards_done": idx,
                        "shards_total": int(len(shard_index)),
                        "rows_written": int(total_rows),
                        "rows_per_sec": int(total_rows / elapsed),
                        "current_shard": str(shard_path),
                        "manifest_path": str(manifest_path),
                    },
                )
    finally:
        if writer is not None:
            writer.close()

    if sample_tables:
        pa.concat_tables(sample_tables, promote_options="default").to_pandas().to_csv(sample_path, index=False)
    return written_shards, total_rows


def consolidate(args: argparse.Namespace) -> dict[str, object]:
    run_roots = _as_paths(args.run_roots)
    if not run_roots:
        raise ValueError("--run-roots is required")
    missing_roots = [str(root) for root in run_roots if not root.exists()]
    if missing_roots:
        raise FileNotFoundError(f"Missing run roots: {missing_roots}")

    tickers = _load_tickers(args.universe_parquet, args.ticker_column)
    universe = set(tickers)
    if args.expected_tickers is not None and len(universe) != int(args.expected_tickers):
        raise ValueError(f"Expected {args.expected_tickers} universe tickers, got {len(universe)}")

    consolidation_run_root = args.consolidation_run_root
    if consolidation_run_root is None:
        run_id = datetime.now(timezone.utc).strftime("quote_guarded_lt1b_consolidation_%Y%m%dT%H%M%SZ")
        consolidation_run_root = PROJECT_ROOT / "runs" / "data_foundation" / "ohlcv_1m_quote_guarded" / run_id
    consolidation_run_root.mkdir(parents=True, exist_ok=True)

    completion, completed_tickers = collect_completion(run_roots, universe)
    completion_path = consolidation_run_root / "lt1b_ticker_completion.csv"
    completion.to_csv(completion_path, index=False)
    missing_completion = sorted(universe - completed_tickers)
    if missing_completion and args.require_complete:
        atomic_write_json(
            consolidation_run_root / "consolidation_summary.json",
            {
                "status": "FAIL_INCOMPLETE_LT1B",
                "created_at_utc": utc_now(),
                "universe_parquet": str(args.universe_parquet),
                "universe_tickers": len(universe),
                "completed_tickers": len(completed_tickers),
                "missing_tickers": len(missing_completion),
                "missing_tickers_sample": missing_completion[:100],
                "completion_csv": str(completion_path),
                "run_roots": [str(root) for root in run_roots],
            },
        )
        raise RuntimeError(f"LT1B incomplete: {len(missing_completion)} tickers missing DONE status")

    shard_index = collect_shards(run_roots, universe, completed_tickers)
    shard_index_path = consolidation_run_root / "lt1b_repair_shard_index.csv"
    shard_index.to_csv(shard_index_path, index=False)

    manifest_rows: int | None = None
    written_shards: int | None = None
    manifest_path = args.manifest_output
    if manifest_path is None:
        manifest_path = consolidation_run_root / "repair_manifest_lt1b_v0_1.parquet"
    sample_path = manifest_path.with_name(manifest_path.stem + "_sample.csv")

    if not args.skip_manifest:
        written_shards, manifest_rows = write_manifest(
            shard_index,
            manifest_path,
            sample_path,
            consolidation_run_root / "consolidation_status.json",
            universe,
            overwrite=bool(args.overwrite),
            progress_every=max(1, int(args.progress_every)),
            sample_rows=max(0, int(args.sample_rows)),
        )

    promoted_manifest = ""
    if args.promote:
        args.output_root.mkdir(parents=True, exist_ok=True)
        promoted = args.output_root / "repair_manifest_lt1b_v0_1.parquet"
        if manifest_path.resolve() != promoted.resolve():
            if promoted.exists() and not args.overwrite:
                raise FileExistsError(f"Promoted manifest already exists: {promoted}")
            shutil.copy2(manifest_path, promoted)
        promoted_manifest = str(promoted)

    summary = {
        "status": "PASS",
        "created_at_utc": utc_now(),
        "universe_dataset": "lt1b_universe_v0_1",
        "universe_parquet": str(args.universe_parquet),
        "universe_tickers": len(universe),
        "completed_tickers": len(completed_tickers),
        "missing_tickers": len(missing_completion),
        "run_roots": [str(root) for root in run_roots],
        "consolidation_run_root": str(consolidation_run_root),
        "completion_csv": str(completion_path),
        "shard_index_csv": str(shard_index_path),
        "selected_repair_shards": int(len(shard_index)),
        "skipped_out_scope_shards": int(shard_index.attrs.get("skipped_out_scope_shards", 0)),
        "skipped_incomplete_lt1b_shards": int(shard_index.attrs.get("skipped_incomplete_lt1b_shards", 0)),
        "malformed_shard_names": int(shard_index.attrs.get("malformed_shard_names", 0)),
        "manifest_path": "" if args.skip_manifest else str(manifest_path),
        "sample_path": "" if args.skip_manifest else str(sample_path),
        "manifest_rows": manifest_rows,
        "written_shards": written_shards,
        "promoted_manifest": promoted_manifest,
    }
    atomic_write_json(consolidation_run_root / "consolidation_summary.json", summary)
    if args.promote:
        atomic_write_json(args.output_root / "repair_manifest_lt1b_v0_1_summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Consolidate quote-guarded repair shards for LT1B only.")
    ap.add_argument("--run-roots", nargs="+", required=True, help="One or more repair run roots; semicolon-separated values are also accepted.")
    ap.add_argument("--universe-parquet", type=Path, default=DEFAULT_UNIVERSE_PARQUET)
    ap.add_argument("--ticker-column", default="ticker")
    ap.add_argument("--expected-tickers", type=int, default=4824)
    ap.add_argument("--consolidation-run-root", type=Path)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    ap.add_argument("--manifest-output", type=Path)
    ap.add_argument("--skip-manifest", action="store_true", help="Only write completion and shard index; do not write the large manifest.")
    ap.add_argument("--require-complete", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--promote", action="store_true")
    ap.add_argument("--progress-every", type=int, default=500)
    ap.add_argument("--sample-rows", type=int, default=1000)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    summary = consolidate(args)
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
