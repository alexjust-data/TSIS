#!/usr/bin/env python
"""
EXP_DAS_FRONTSIDE_DISCOVERY_0002 - scanner denominator 2026, v0.2.

Este builder sustituye al camino raw+repair-on-the-fly del v0.1.
Lee directamente la superficie 1m quote-guarded full-universe materializada:

    C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1

No usa candidate_events.parquet, anchors DAS antiguos ni notebooks.
Solo produce el denominador "ticker cazado por scanner":

    market cap <= 100M
    price in [0.50, 20.00]
    accumulated session volume >= 500k
    close vs prior close >= threshold
    session window declared

Los anchors de estrategia (first push, first dip, rebreak/in-play) se calculan
despues desde este denominador.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyarrow.parquet as pq


EXPERIMENT_ID = "EXP_DAS_FRONTSIDE_DISCOVERY_0002"
BUILDER_ID = "build_2026_scanner_from_qg_full_universe_1m_v0_2"
BASE_SCRIPT = Path(__file__).with_name("build_2026_scanner_from_quote_guarded_1m_v0_1.py")


def _load_base_module():
    spec = importlib.util.spec_from_file_location("das_scanner_v0_1_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base scanner module: {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.BUILDER_ID = BUILDER_ID
    module.EXPERIMENT_ID = EXPERIMENT_ID
    return module


base = _load_base_module()
ScannerConfig = base.ScannerConfig


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_parquet_file(path: Path, columns: list[str] | None = None) -> pd.DataFrame:
    return pq.ParquetFile(str(path)).read(columns=columns).to_pandas()


def _parse_tickers(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    return [x.strip().upper() for x in raw.split(",") if x.strip()]


def _list_qg_files(qg_root: Path, year: int, tickers: list[str] | None, limit_files: int | None) -> list[Path]:
    year_root = qg_root / f"year={year}"
    files: list[Path] = []
    if tickers:
        for ticker in tickers:
            files.extend(sorted((year_root / f"ticker={ticker}").glob("month=*/part-000.parquet")))
    else:
        files = sorted(year_root.glob("ticker=*/month=*/part-000.parquet"))
    if limit_files is not None:
        files = files[:limit_files]
    return files


def _prepare_materialized_qg(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ticker"] = out["ticker"].astype(str).str.upper()
    out["ts_utc_dt"] = pd.to_datetime(out["ts_utc"], utc=True, errors="coerce")
    for qg_col, col in [("o_qg", "o"), ("h_qg", "h"), ("l_qg", "l"), ("c_qg", "c")]:
        out[qg_col] = pd.to_numeric(out[col], errors="coerce")
    if "quote_guarded_repair_applied" not in out.columns:
        out["quote_guarded_repair_applied"] = False
    out["quote_guarded_repair_applied"] = out["quote_guarded_repair_applied"].fillna(False).astype(bool)
    if "repair_state" not in out.columns:
        out["repair_state"] = "materialized_qg_no_repair_state"
    if "repair_reason" not in out.columns:
        out["repair_reason"] = pd.NA
    out["quote_guarded_join_state"] = "materialized_qg_full_universe"
    if "source_raw_path" in out.columns:
        out["source_ohlcv_path"] = out["source_raw_path"]
    else:
        out["source_ohlcv_path"] = pd.NA
    if "build_run_id" in out.columns:
        out["run_root"] = out["build_run_id"]
    else:
        out["run_root"] = pd.NA
    return out


def _write_progress(
    out_dir: Path,
    candidates: list[dict],
    config,
    total_files: int,
    files_scanned: int,
    files_read: int,
    current_file: Path | None,
    status: str = "running",
) -> None:
    partial_csv = out_dir / "scanner_2026_qg_full_universe_denominator_partial_v0_2.csv"
    if candidates:
        pd.DataFrame(candidates).to_csv(partial_csv, index=False)
    progress = {
        "updated_utc": _utc_now(),
        "builder_id": BUILDER_ID,
        "experiment_id": EXPERIMENT_ID,
        "status": status,
        "total_files": total_files,
        "files_scanned": files_scanned,
        "files_read": files_read,
        "raw_candidates": len(candidates),
        "current_file": str(current_file) if current_file else None,
        "partial_csv": str(partial_csv) if candidates else None,
        "config": asdict(config),
    }
    (out_dir / "scanner_2026_qg_full_universe_progress_v0_2.json").write_text(
        json.dumps(progress, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_summary(out_dir: Path, candidates: pd.DataFrame, manifest: dict) -> None:
    lines = [
        "# Scanner 2026 QG Full-Universe Summary",
        "",
        f"created_utc: `{manifest['created_utc']}`",
        f"builder_id: `{manifest['builder_id']}`",
        "",
        "## Regla Critica",
        "",
        "Este run lee la superficie 1m quote-guarded full-universe ya materializada.",
        "No usa `candidate_events.parquet`, anchors del DAS antiguo ni raw+repair on-the-fly.",
        "",
        "## Counts",
        "",
        f"- qg_files_seen: {manifest['qg_files_seen']}",
        f"- qg_files_read: {manifest['qg_files_read']}",
        f"- candidates_emitted: {manifest['candidates_emitted']}",
        f"- repair_applied_rows_seen: {manifest['repair_applied_rows_seen']}",
        "",
        "## Market Cap",
        "",
        f"- market_cap_policy: `{manifest['config']['market_cap_policy']}`",
        "- `future_snapshot_review` no es legal como estado as-of; sirve solo para screening research si se declara.",
        "",
    ]
    if not candidates.empty and "market_cap_source_state" in candidates.columns:
        lines.append(f"- market_cap_source_state_counts: `{candidates['market_cap_source_state'].value_counts(dropna=False).to_dict()}`")
    (out_dir / "scanner_2026_qg_full_universe_summary_v0_2.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def build(args: argparse.Namespace) -> None:
    qg_root = Path(args.qg_full_universe_root)
    master_daily_root = Path(args.master_daily_root)
    overview_root = Path(args.reference_overview_root)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    config = ScannerConfig(
        year=args.year,
        threshold_pct=args.threshold_pct,
        min_volume=args.min_volume,
        min_price=args.min_price,
        max_price=args.max_price,
        max_market_cap=args.max_market_cap,
        session_start_et=args.session_start_et,
        session_end_et=args.session_end_et,
        reference_price="prior_close",
        market_cap_policy=args.market_cap_policy,
    )

    tickers = _parse_tickers(args.tickers)
    if args.verbose:
        print(
            "discovering_files "
            f"qg_full_universe_root={qg_root} year={args.year} "
            f"tickers={','.join(tickers) if tickers else 'all'}",
            flush=True,
        )
    qg_files = _list_qg_files(qg_root, args.year, tickers, args.limit_files)
    if args.verbose:
        print(f"files_to_scan={len(qg_files)}", flush=True)
        print(
            "loading_daily_prior_close "
            f"root={master_daily_root} years={args.year - 1},{args.year}",
            flush=True,
        )
    daily = base._load_daily_prior_close(master_daily_root, [args.year - 1, args.year])
    if args.verbose:
        print(f"daily_prior_close_rows={len(daily)}", flush=True)

    overview_cache: dict[str, pd.DataFrame] = {}
    all_candidates: list[dict] = []
    read_count = 0
    repair_applied_rows_total = 0
    skipped_files: list[str] = []
    last_partial_count = 0
    progress_every = max(1, int(args.progress_every))
    partial_flush_every = max(0, int(args.partial_flush_every))

    for idx, qg_file in enumerate(qg_files, start=1):
        if args.verbose:
            print(
                f"processing files_scanned={idx}/{len(qg_files)} "
                f"raw_candidates={len(all_candidates)} current={qg_file}",
                flush=True,
            )
        try:
            raw = _read_parquet_file(qg_file)
            if raw.empty:
                continue
            intraday = _prepare_materialized_qg(raw)
            repair_applied_rows_total += int(intraday["quote_guarded_repair_applied"].fillna(False).sum())
            intraday = base._add_session_fields(intraday, args.session_start_et, args.session_end_et)
            before_candidates = len(all_candidates)
            emitted_rows = base._build_candidates(
                intraday,
                daily,
                overview_cache,
                overview_root,
                config,
                qg_file,
            )
            for row in emitted_rows:
                row["source_input_1m_file"] = str(qg_file)
                row["source_input_1m_dataset"] = "ohlcv_1m_quote_guarded_full_universe_v0_1"
                row["source_input_1m_root"] = str(qg_root)
                row["source_raw_ohlcv_file"] = None
            all_candidates.extend(emitted_rows)
            read_count += 1
            emitted = len(all_candidates) - before_candidates
            if args.verbose:
                print(
                    f"[OK] files_scanned={idx}/{len(qg_files)} "
                    f"read_files={read_count} emitted={emitted} "
                    f"raw_candidates={len(all_candidates)} current={qg_file}",
                    flush=True,
                )
            if args.verbose and (idx == 1 or idx % progress_every == 0 or emitted > 0):
                print(
                    f"progress files_scanned={idx}/{len(qg_files)} "
                    f"raw_candidates={len(all_candidates)} read_files={read_count} current={qg_file}",
                    flush=True,
                )
            should_flush = (
                partial_flush_every > 0
                and (
                    len(all_candidates) - last_partial_count >= partial_flush_every
                    or idx == 1
                    or idx % progress_every == 0
                )
            )
            if should_flush:
                _write_progress(out_dir, all_candidates, config, len(qg_files), idx, read_count, qg_file)
                last_partial_count = len(all_candidates)
        except Exception as exc:
            skipped_files.append(f"{qg_file}: {exc}")
            print(f"[WARN] skipped {qg_file}: {exc}", flush=True)
            _write_progress(out_dir, all_candidates, config, len(qg_files), idx, read_count, qg_file)

    _write_progress(out_dir, all_candidates, config, len(qg_files), len(qg_files), read_count, None, status="complete")
    candidates = pd.DataFrame(all_candidates)
    parquet_path = out_dir / "scanner_2026_qg_full_universe_denominator_v0_2.parquet"
    csv_path = out_dir / "scanner_2026_qg_full_universe_denominator_v0_2.csv"
    if candidates.empty:
        candidates = pd.DataFrame(
            columns=[
                "experiment_id",
                "sweep_id",
                "scanner_config_id",
                "ticker",
                "session_date",
                "scanner_gate_ts_utc",
                "scanner_gate_price",
                "scanner_gate_prior_close_pct",
                "scanner_gate_accumulated_volume",
            ]
        )
    candidates.to_parquet(parquet_path, index=False)
    candidates.to_csv(csv_path, index=False)

    manifest = {
        "created_utc": _utc_now(),
        "builder_id": BUILDER_ID,
        "experiment_id": EXPERIMENT_ID,
        "candidate_events_legacy_used": False,
        "old_das_run_used": False,
        "qg_full_universe_root": str(qg_root),
        "master_daily_root": str(master_daily_root),
        "reference_overview_root": str(overview_root),
        "output_dir": str(out_dir),
        "config": asdict(config),
        "qg_files_seen": len(qg_files),
        "qg_files_read": read_count,
        "repair_applied_rows_seen": repair_applied_rows_total,
        "candidates_emitted": len(candidates),
        "skipped_files": skipped_files,
    }
    (out_dir / "scanner_2026_qg_full_universe_run_manifest_v0_2.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _write_summary(out_dir, candidates, manifest)
    print(json.dumps({k: manifest[k] for k in ["qg_files_seen", "qg_files_read", "candidates_emitted"]}, indent=2))
    print(f"wrote={parquet_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--qg-full-universe-root",
        default=r"C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_1",
    )
    parser.add_argument(
        "--master-daily-root",
        default=r"E:\TSIS\data\data_foundation_outputs\master_daily_table\master_daily_table_v0_1",
    )
    parser.add_argument("--reference-overview-root", default=r"E:\TSIS\data\reference\overview")
    parser.add_argument(
        "--output-dir",
        default=r"C:\TSIS_Data\03_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_qg_full_universe_v0_2",
    )
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--tickers", default=None, help="Comma-separated tickers for smoke runs.")
    parser.add_argument("--limit-files", type=int, default=None)
    parser.add_argument("--threshold-pct", type=float, default=50.0)
    parser.add_argument("--min-volume", type=float, default=500000.0)
    parser.add_argument("--min-price", type=float, default=0.5)
    parser.add_argument("--max-price", type=float, default=20.0)
    parser.add_argument("--max-market-cap", type=float, default=100000000.0)
    parser.add_argument("--session-start-et", default="04:00")
    parser.add_argument("--session-end-et", default="09:30")
    parser.add_argument(
        "--market-cap-policy",
        choices=["asof_only", "snapshot_allowed_flagged", "flag_only"],
        default="snapshot_allowed_flagged",
    )
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--partial-flush-every", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())
