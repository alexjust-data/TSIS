from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.ohlcv_1m_quote_guarded import (  # noqa: E402
    QUOTE_GUARDED_VIEW_NAME,
    NY_TZ,
    QuoteGuardConfig,
    build_quote_minute_envelope,
    detect_quote_guarded_repairs,
    to_utc_datetime,
)


DEFAULT_MINUTE_ROOT = Path(r"E:\TSIS\data\ohlcv_1m")
DEFAULT_QUOTES_ROOT = Path(r"D:\quotes")
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded")


@dataclass(frozen=True)
class MinuteFile:
    ticker: str
    year: int
    month: int
    path: Path


@dataclass(frozen=True)
class AuditConfig:
    minute_root: Path
    quotes_root: Path
    run_root: Path
    output_root: Path
    quote_guard: QuoteGuardConfig
    session_start: str
    session_end: str
    max_spread_pct: float | None
    overwrite: bool
    promote_manifest: bool


def _iter_minute_files(root: Path, tickers: set[str] | None = None) -> Iterable[MinuteFile]:
    search_roots: list[Path]
    if tickers is None:
        search_roots = [root]
    else:
        search_roots = []
        for ticker in sorted(tickers):
            for candidate in (root / f"ticker={ticker}", root / ticker):
                if candidate.exists():
                    search_roots.append(candidate)

    for search_root in search_roots:
        for path in search_root.rglob("minute_aggs_*.parquet"):
            yield from _minute_file_from_path(path)


def _minute_file_from_path(path: Path) -> Iterable[MinuteFile]:
    parts = {p.split("=", 1)[0]: p.split("=", 1)[1] for p in path.parts if "=" in p}
    ticker = parts.get("ticker")
    year = parts.get("year")
    month = parts.get("month")
    if not ticker or not year or not month:
        return
    try:
        yield MinuteFile(ticker=ticker.upper(), year=int(year), month=int(month), path=path)
    except ValueError:
        return


def _safe_file_id(item: MinuteFile) -> str:
    return f"{item.ticker}_{item.year:04d}_{item.month:02d}"


def _parse_hhmm(value: str) -> time:
    hh, mm = value.split(":", 1)
    return time(hour=int(hh), minute=int(mm))


def _session_mask(minute_ny: pd.Series, start_hhmm: str, end_hhmm: str) -> pd.Series:
    start = _parse_hhmm(start_hhmm)
    end = _parse_hhmm(end_hhmm)
    local_time = minute_ny.dt.time
    if start <= end:
        return (local_time >= start) & (local_time <= end)
    return (local_time >= start) | (local_time <= end)


def _read_parquet_columns(path: Path, columns: list[str]) -> pd.DataFrame:
    try:
        return pd.read_parquet(path, columns=columns)
    except Exception:
        frame = pd.read_parquet(path)
        keep = [col for col in columns if col in frame.columns]
        return frame[keep].copy()


def _quote_path_candidates(root: Path, ticker: str, session_date: str) -> list[Path]:
    d = pd.Timestamp(session_date)
    y = int(d.year)
    m = int(d.month)
    day = int(d.day)
    return [
        root / ticker / f"year={y}" / f"month={m:02d}" / f"day={day:02d}" / "quotes.parquet",
        root / ticker / f"year={y}" / f"month={m:02d}" / f"day={day}" / "quotes.parquet",
        root / f"ticker={ticker}" / f"year={y}" / f"month={m:02d}" / f"day={day:02d}" / "quotes.parquet",
        root / f"ticker={ticker}" / f"year={y}" / f"month={m:02d}" / f"day={day}" / "quotes.parquet",
    ]


def _find_quote_path(root: Path, ticker: str, session_date: str) -> Path | None:
    for candidate in _quote_path_candidates(root, ticker, session_date):
        if candidate.exists():
            return candidate
    return None


def _quote_timestamp_col(columns: Iterable[str]) -> str | None:
    cols = set(columns)
    for col in ("timestamp", "participant_timestamp", "trf_timestamp"):
        if col in cols:
            return col
    return None


def _load_quote_envelopes(
    cfg: AuditConfig,
    ticker: str,
    session_dates: list[str],
) -> tuple[pd.DataFrame, dict[str, object]]:
    frames: list[pd.DataFrame] = []
    quote_days_found = 0
    quote_days_missing = 0
    quote_rows_raw = 0
    quote_rows_enveloped = 0
    quote_paths: list[str] = []

    for session_date in session_dates:
        quote_path = _find_quote_path(cfg.quotes_root, ticker, session_date)
        if quote_path is None:
            quote_days_missing += 1
            continue
        quote_days_found += 1
        quote_paths.append(str(quote_path))
        try:
            q = pd.read_parquet(quote_path, columns=["timestamp", "bid_price", "ask_price"])
            timestamp_col = "timestamp"
        except Exception:
            q = pd.read_parquet(quote_path)
            timestamp_col = _quote_timestamp_col(q.columns)
            if timestamp_col is None:
                quote_days_missing += 1
                quote_days_found -= 1
                continue
            q = q[[timestamp_col, "bid_price", "ask_price"]].copy()
        quote_rows_raw += int(len(q))
        env = build_quote_minute_envelope(
            q,
            timestamp_col=timestamp_col,
            config=cfg.quote_guard,
            max_spread_pct=cfg.max_spread_pct,
        )
        if env.empty:
            continue
        env = env.loc[env["quote_count"].ge(cfg.quote_guard.min_quote_count)].copy()
        if env.empty:
            continue
        env = env.loc[_session_mask(env["minute_ny"], cfg.session_start, cfg.session_end)].copy()
        if env.empty:
            continue
        env["source_quotes_path"] = str(quote_path)
        frames.append(env)
        quote_rows_enveloped += int(env["quote_count"].sum())

    summary = {
        "quote_days_requested": len(session_dates),
        "quote_days_found": quote_days_found,
        "quote_days_missing": quote_days_missing,
        "quote_rows_raw": quote_rows_raw,
        "quote_rows_enveloped": quote_rows_enveloped,
        "quote_paths": quote_paths,
    }
    if not frames:
        return pd.DataFrame(), summary
    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates(subset=["minute_ny"], keep="last").sort_values("minute_ny").reset_index(drop=True)
    return out, summary


def _load_summary(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def process_minute_file(item: MinuteFile, cfg: AuditConfig) -> dict[str, object]:
    file_id = _safe_file_id(item)
    repair_dir = cfg.run_root / "repair_shards"
    summary_dir = cfg.run_root / "file_summaries"
    repair_path = repair_dir / f"{file_id}_repair_manifest.parquet"
    summary_path = summary_dir / f"{file_id}.json"
    if summary_path.exists() and not cfg.overwrite:
        return _load_summary(summary_path)

    repair_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    if repair_path.exists() and cfg.overwrite:
        repair_path.unlink()

    base_summary: dict[str, object] = {
        "ticker": item.ticker,
        "year": item.year,
        "month": item.month,
        "source_ohlcv_path": str(item.path),
        "repair_shard_path": "",
        "status": "UNKNOWN",
        "raw_rows": 0,
        "session_rows": 0,
        "quote_matched_rows": 0,
        "repair_rows": 0,
        "ohlc_repair_rows": 0,
        "vw_invalid_rows": 0,
        "quote_days_requested": 0,
        "quote_days_found": 0,
        "quote_days_missing": 0,
        "quote_rows_raw": 0,
        "quote_rows_enveloped": 0,
        "error": "",
    }

    try:
        columns = ["ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v", "vw", "n", "t"]
        bars = _read_parquet_columns(item.path, columns)
        base_summary["raw_rows"] = int(len(bars))
        if bars.empty or "ts_utc" not in bars.columns:
            base_summary["status"] = "NO_RAW_ROWS_OR_TIMESTAMP"
            summary_path.write_text(json.dumps(base_summary, indent=2, ensure_ascii=False), encoding="utf-8")
            return base_summary

        bars["ts_utc"] = to_utc_datetime(bars["ts_utc"])
        bars = bars.loc[bars["ts_utc"].notna()].copy()
        if bars.empty:
            base_summary["status"] = "NO_PARSEABLE_TIMESTAMP"
            summary_path.write_text(json.dumps(base_summary, indent=2, ensure_ascii=False), encoding="utf-8")
            return base_summary
        bars["minute_ny"] = bars["ts_utc"].dt.tz_convert(NY_TZ).dt.floor("min")
        bars = bars.loc[_session_mask(bars["minute_ny"], cfg.session_start, cfg.session_end)].copy()
        base_summary["session_rows"] = int(len(bars))
        if bars.empty:
            base_summary["status"] = "NO_SESSION_ROWS"
            summary_path.write_text(json.dumps(base_summary, indent=2, ensure_ascii=False), encoding="utf-8")
            return base_summary

        session_dates = sorted(bars["minute_ny"].dt.date.astype(str).unique().tolist())
        env, quote_summary = _load_quote_envelopes(cfg, item.ticker, session_dates)
        base_summary.update({k: v for k, v in quote_summary.items() if k != "quote_paths"})
        if env.empty:
            base_summary["status"] = "NO_USABLE_QUOTES"
            summary_path.write_text(json.dumps(base_summary, indent=2, ensure_ascii=False), encoding="utf-8")
            return base_summary

        matched_minutes = bars[["minute_ny"]].merge(env[["minute_ny", "quote_count"]], on="minute_ny", how="left")
        base_summary["quote_matched_rows"] = int(matched_minutes["quote_count"].ge(cfg.quote_guard.min_quote_count).sum())
        repairs = detect_quote_guarded_repairs(
            bars.drop(columns=["minute_ny"]),
            env,
            config=cfg.quote_guard,
            ticker=item.ticker,
            source_ohlcv_path=str(item.path),
            source_quotes_path_col="source_quotes_path",
        )
        if repairs.empty:
            base_summary["status"] = "PASS_NO_REPAIRS"
            summary_path.write_text(json.dumps(base_summary, indent=2, ensure_ascii=False), encoding="utf-8")
            return base_summary

        repairs["manifest_created_at_utc"] = datetime.now(timezone.utc).isoformat()
        repairs["run_root"] = str(cfg.run_root)
        repairs.to_parquet(repair_path, index=False)
        base_summary["repair_shard_path"] = str(repair_path)
        base_summary["repair_rows"] = int(len(repairs))
        base_summary["ohlc_repair_rows"] = int(repairs["quote_guarded_repair_applied"].fillna(False).sum())
        base_summary["vw_invalid_rows"] = int((repairs["vw_quote_guarded_status"] == "invalid_not_repaired_from_quotes").sum())
        base_summary["status"] = "REPAIRS_WRITTEN"
        summary_path.write_text(json.dumps(base_summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return base_summary
    except Exception as exc:  # noqa: BLE001
        base_summary["status"] = "ERROR"
        base_summary["error"] = repr(exc)
        summary_path.write_text(json.dumps(base_summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return base_summary


def _write_single_manifest(shards: list[Path], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    writer: pq.ParquetWriter | None = None
    rows = 0
    try:
        for shard in shards:
            table = pq.read_table(shard)
            rows += table.num_rows
            if writer is None:
                writer = pq.ParquetWriter(output_path, table.schema)
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()
    return rows


def _write_manifest_sample(manifest_path: Path, sample_path: Path, limit: int = 1000) -> None:
    if not manifest_path.exists():
        return
    frame = pd.read_parquet(manifest_path)
    frame.head(limit).to_csv(sample_path, index=False)


def build_repairs(
    minute_root: Path,
    quotes_root: Path,
    run_root: Path,
    output_root: Path,
    workers: int,
    min_year: int | None,
    max_year: int | None,
    tickers: set[str] | None,
    max_files: int | None,
    cfg: QuoteGuardConfig,
    session_start: str,
    session_end: str,
    max_spread_pct: float | None,
    overwrite: bool,
    promote_manifest: bool,
) -> dict[str, object]:
    if not minute_root.exists():
        raise FileNotFoundError(f"Missing minute root: {minute_root}")
    if not quotes_root.exists():
        raise FileNotFoundError(f"Missing quotes root: {quotes_root}")
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "repair_shards").mkdir(parents=True, exist_ok=True)
    (run_root / "file_summaries").mkdir(parents=True, exist_ok=True)

    files: list[MinuteFile] = []
    max_file_count = int(max_files) if max_files is not None else None
    if max_file_count is None or max_file_count > 0:
        for item in _iter_minute_files(minute_root, tickers=tickers):
            if tickers is not None and item.ticker not in tickers:
                continue
            if min_year is not None and item.year < min_year:
                continue
            if max_year is not None and item.year > max_year:
                continue
            files.append(item)
            if max_file_count is not None and len(files) >= max_file_count:
                break

    audit_cfg = AuditConfig(
        minute_root=minute_root,
        quotes_root=quotes_root,
        run_root=run_root,
        output_root=output_root,
        quote_guard=cfg,
        session_start=session_start,
        session_end=session_end,
        max_spread_pct=max_spread_pct,
        overwrite=overwrite,
        promote_manifest=promote_manifest,
    )
    run_config = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "view_name": QUOTE_GUARDED_VIEW_NAME,
        "minute_root": str(minute_root),
        "quotes_root": str(quotes_root),
        "run_root": str(run_root),
        "output_root": str(output_root),
        "workers": workers,
        "min_year": min_year,
        "max_year": max_year,
        "tickers": sorted(tickers) if tickers is not None else None,
        "max_files": max_files,
        "session_start": session_start,
        "session_end": session_end,
        "max_spread_pct": max_spread_pct,
        "quote_guard": asdict(cfg),
        "promote_manifest": promote_manifest,
        "overwrite": overwrite,
        "files_planned": len(files),
    }
    (run_root / "run_config.json").write_text(json.dumps(run_config, indent=2, ensure_ascii=False), encoding="utf-8")

    summaries: list[dict[str, object]] = []
    if workers <= 1:
        for item in files:
            summaries.append(process_minute_file(item, audit_cfg))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(process_minute_file, item, audit_cfg): item for item in files}
            for idx, fut in enumerate(as_completed(futures), start=1):
                summary = fut.result()
                summaries.append(summary)
                if idx % 250 == 0:
                    print(f"processed {idx}/{len(files)} files", flush=True)

    file_summary = pd.DataFrame(summaries)
    file_summary_path = run_root / "file_summary.parquet"
    file_summary_csv = run_root / "file_summary.csv"
    file_summary.to_parquet(file_summary_path, index=False)
    file_summary.to_csv(file_summary_csv, index=False)

    shards = sorted(Path(p) for p in file_summary.get("repair_shard_path", pd.Series(dtype=str)).dropna().astype(str) if p)
    run_manifest = run_root / "repair_manifest.parquet"
    manifest_rows = _write_single_manifest(shards, run_manifest) if shards else 0
    _write_manifest_sample(run_manifest, run_root / "repair_manifest_sample.csv")

    promoted_manifest = ""
    if promote_manifest:
        output_root.mkdir(parents=True, exist_ok=True)
        promoted = output_root / "repair_manifest_v0_1.parquet"
        if shards:
            _write_single_manifest(shards, promoted)
            _write_manifest_sample(promoted, output_root / "repair_manifest_v0_1_sample.csv")
        elif promoted.exists() and overwrite:
            promoted.unlink()
        promoted_manifest = str(promoted)

    status_counts = (
        file_summary.groupby("status", dropna=False).size().reset_index(name="n_files").sort_values("status")
        if not file_summary.empty
        else pd.DataFrame(columns=["status", "n_files"])
    )
    status_counts.to_csv(run_root / "status_counts.csv", index=False)

    result = {
        **run_config,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "files_processed": int(len(file_summary)),
        "files_with_repairs": int((file_summary.get("repair_rows", 0) > 0).sum()) if not file_summary.empty else 0,
        "manifest_rows": int(manifest_rows),
        "ohlc_repair_rows": int(file_summary.get("ohlc_repair_rows", pd.Series(dtype=int)).sum()) if not file_summary.empty else 0,
        "vw_invalid_rows": int(file_summary.get("vw_invalid_rows", pd.Series(dtype=int)).sum()) if not file_summary.empty else 0,
        "run_manifest": str(run_manifest),
        "promoted_manifest": promoted_manifest,
        "file_summary": str(file_summary_path),
        "status_counts": str(run_root / "status_counts.csv"),
    }
    (run_root / "repair_summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    if promote_manifest:
        (output_root / "repair_summary_v0_1.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build the manifest-first quote-guarded repair layer for OHLCV 1m."
    )
    ap.add_argument("--minute-root", type=Path, default=DEFAULT_MINUTE_ROOT)
    ap.add_argument("--quotes-root", type=Path, default=DEFAULT_QUOTES_ROOT)
    ap.add_argument("--run-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--min-year", type=int)
    ap.add_argument("--max-year", type=int)
    ap.add_argument("--tickers", help="Comma-separated ticker allowlist for pilots.")
    ap.add_argument("--max-files", type=int)
    ap.add_argument("--bid-quantile", type=float, default=0.01)
    ap.add_argument("--ask-quantile", type=float, default=0.99)
    ap.add_argument("--tolerance-pct", type=float, default=0.003)
    ap.add_argument("--abs-tolerance", type=float, default=0.0001)
    ap.add_argument("--min-quote-count", type=int, default=3)
    ap.add_argument("--session-start", default="04:00")
    ap.add_argument("--session-end", default="20:00")
    ap.add_argument("--max-spread-pct", type=float)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--promote-manifest", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg = QuoteGuardConfig(
        bid_quantile=float(args.bid_quantile),
        ask_quantile=float(args.ask_quantile),
        tolerance_pct=float(args.tolerance_pct),
        abs_tolerance=float(args.abs_tolerance),
        min_quote_count=int(args.min_quote_count),
    )
    tickers = (
        {token.strip().upper() for token in str(args.tickers).split(",") if token.strip()}
        if args.tickers
        else None
    )
    result = build_repairs(
        minute_root=args.minute_root,
        quotes_root=args.quotes_root,
        run_root=args.run_root,
        output_root=args.output_root,
        workers=max(1, int(args.workers)),
        min_year=args.min_year,
        max_year=args.max_year,
        tickers=tickers,
        max_files=args.max_files,
        cfg=cfg,
        session_start=args.session_start,
        session_end=args.session_end,
        max_spread_pct=args.max_spread_pct,
        overwrite=bool(args.overwrite),
        promote_manifest=bool(args.promote_manifest),
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
