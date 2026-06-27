from __future__ import annotations

import argparse
import json
import os
import sys
import time as time_module
from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, wait
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
class TickerJob:
    ticker: str
    ticker_dir: Path


@dataclass(frozen=True)
class MonthFile:
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
    min_year: int | None
    max_year: int | None
    max_months_per_ticker: int | None
    overwrite: bool
    promote_manifest: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    last_exc: Exception | None = None
    for attempt in range(20):
        try:
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(path)
            return
        except PermissionError as exc:
            last_exc = exc
            time_module.sleep(0.05 * (attempt + 1))
    if last_exc is not None:
        raise last_exc


def write_status_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    for attempt in range(20):
        try:
            path.write_text(text, encoding="utf-8")
            return
        except PermissionError:
            time_module.sleep(0.05 * (attempt + 1))


def append_jsonl(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    for attempt in range(20):
        try:
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line)
            return
        except PermissionError:
            time_module.sleep(0.05 * (attempt + 1))


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


def iter_ticker_jobs(minute_root: Path, tickers: set[str] | None, max_tickers: int | None) -> Iterable[TickerJob]:
    emitted = 0
    if tickers is not None:
        for ticker in sorted(tickers):
            for candidate in (minute_root / f"ticker={ticker}", minute_root / ticker):
                if candidate.exists() and candidate.is_dir():
                    yield TickerJob(ticker=ticker, ticker_dir=candidate)
                    emitted += 1
                    break
            if max_tickers is not None and emitted >= max_tickers:
                return
        return

    for child in minute_root.iterdir():
        if not child.is_dir():
            continue
        name = child.name
        ticker = name.split("=", 1)[1] if name.startswith("ticker=") else name
        if ticker.startswith("_"):
            continue
        if not ticker:
            continue
        yield TickerJob(ticker=ticker.upper(), ticker_dir=child)
        emitted += 1
        if max_tickers is not None and emitted >= max_tickers:
            return


def iter_month_files(job: TickerJob, cfg: AuditConfig) -> Iterable[MonthFile]:
    emitted = 0
    for year_dir in job.ticker_dir.iterdir():
        if not year_dir.is_dir() or not year_dir.name.startswith("year="):
            continue
        try:
            year = int(year_dir.name.split("=", 1)[1])
        except ValueError:
            continue
        if cfg.min_year is not None and year < cfg.min_year:
            continue
        if cfg.max_year is not None and year > cfg.max_year:
            continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir() or not month_dir.name.startswith("month="):
                continue
            try:
                month = int(month_dir.name.split("=", 1)[1])
            except ValueError:
                continue
            expected = month_dir / f"minute_aggs_{job.ticker}_{year}_{month:02d}.parquet"
            paths = [expected] if expected.exists() else sorted(month_dir.glob("minute_aggs_*.parquet"))
            for path in paths:
                if not path.exists():
                    continue
                yield MonthFile(ticker=job.ticker, year=year, month=month, path=path)
                emitted += 1
                if cfg.max_months_per_ticker is not None and emitted >= cfg.max_months_per_ticker:
                    return


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

    for session_date in session_dates:
        quote_path = _find_quote_path(cfg.quotes_root, ticker, session_date)
        if quote_path is None:
            quote_days_missing += 1
            continue
        quote_days_found += 1
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
    }
    if not frames:
        return pd.DataFrame(), summary
    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates(subset=["minute_ny"], keep="last").sort_values("minute_ny").reset_index(drop=True)
    return out, summary


def process_month_file(month_file: MonthFile, cfg: AuditConfig) -> dict[str, object]:
    file_id = f"{month_file.ticker}_{month_file.year:04d}_{month_file.month:02d}"
    summary_path = cfg.run_root / "month_summaries" / f"{file_id}.json"
    repair_path = cfg.run_root / "repair_shards" / f"{file_id}_repair_manifest.parquet"
    if summary_path.exists() and not cfg.overwrite:
        try:
            return json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    if repair_path.exists() and cfg.overwrite:
        repair_path.unlink()

    summary: dict[str, object] = {
        "ticker": month_file.ticker,
        "year": month_file.year,
        "month": month_file.month,
        "source_ohlcv_path": str(month_file.path),
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
        "started_at_utc": utc_now(),
        "finished_at_utc": "",
        "error": "",
    }

    try:
        columns = ["ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v", "vw", "n", "t"]
        bars = _read_parquet_columns(month_file.path, columns)
        summary["raw_rows"] = int(len(bars))
        if bars.empty or "ts_utc" not in bars.columns:
            summary["status"] = "NO_RAW_ROWS_OR_TIMESTAMP"
            return _finish_month_summary(summary_path, summary)

        bars["ts_utc"] = to_utc_datetime(bars["ts_utc"])
        bars = bars.loc[bars["ts_utc"].notna()].copy()
        if bars.empty:
            summary["status"] = "NO_PARSEABLE_TIMESTAMP"
            return _finish_month_summary(summary_path, summary)

        bars["minute_ny"] = bars["ts_utc"].dt.tz_convert(NY_TZ).dt.floor("min")
        bars = bars.loc[_session_mask(bars["minute_ny"], cfg.session_start, cfg.session_end)].copy()
        summary["session_rows"] = int(len(bars))
        if bars.empty:
            summary["status"] = "NO_SESSION_ROWS"
            return _finish_month_summary(summary_path, summary)

        session_dates = sorted(bars["minute_ny"].dt.date.astype(str).unique().tolist())
        env, quote_summary = _load_quote_envelopes(cfg, month_file.ticker, session_dates)
        summary.update(quote_summary)
        if env.empty:
            summary["status"] = "NO_USABLE_QUOTES"
            return _finish_month_summary(summary_path, summary)

        matched_minutes = bars[["minute_ny"]].merge(env[["minute_ny", "quote_count"]], on="minute_ny", how="left")
        summary["quote_matched_rows"] = int(matched_minutes["quote_count"].ge(cfg.quote_guard.min_quote_count).sum())
        repairs = detect_quote_guarded_repairs(
            bars.drop(columns=["minute_ny"]),
            env,
            config=cfg.quote_guard,
            ticker=month_file.ticker,
            source_ohlcv_path=str(month_file.path),
            source_quotes_path_col="source_quotes_path",
        )
        if repairs.empty:
            summary["status"] = "PASS_NO_REPAIRS"
            return _finish_month_summary(summary_path, summary)

        repairs["manifest_created_at_utc"] = utc_now()
        repairs["run_root"] = str(cfg.run_root)
        repair_path.parent.mkdir(parents=True, exist_ok=True)
        repairs.to_parquet(repair_path, index=False)
        summary["repair_shard_path"] = str(repair_path)
        summary["repair_rows"] = int(len(repairs))
        summary["ohlc_repair_rows"] = int(repairs["quote_guarded_repair_applied"].fillna(False).sum())
        summary["vw_invalid_rows"] = int((repairs["vw_quote_guarded_status"] == "invalid_not_repaired_from_quotes").sum())
        summary["status"] = "REPAIRS_WRITTEN"
        return _finish_month_summary(summary_path, summary)
    except Exception as exc:  # noqa: BLE001
        summary["status"] = "ERROR"
        summary["error"] = repr(exc)
        return _finish_month_summary(summary_path, summary)


def _finish_month_summary(path: Path, summary: dict[str, object]) -> dict[str, object]:
    summary["finished_at_utc"] = utc_now()
    atomic_write_json(path, summary)
    return summary


def _ticker_status_path(cfg: AuditConfig, ticker: str) -> Path:
    return cfg.run_root / "ticker_status" / f"{ticker}.json"


def _ticker_events_path(cfg: AuditConfig, ticker: str) -> Path:
    return cfg.run_root / "ticker_events" / f"{ticker}.jsonl"


def update_ticker_status(cfg: AuditConfig, ticker: str, payload: dict[str, object]) -> None:
    base = {
        "ticker": ticker,
        "status": "UNKNOWN",
        "pid": os.getpid(),
        "last_heartbeat_utc": utc_now(),
    }
    base.update(payload)
    try:
        write_status_json(_ticker_status_path(cfg, ticker), base)
        append_jsonl(_ticker_events_path(cfg, ticker), base)
    except PermissionError:
        # Telemetry must never fail a ticker repair. A later heartbeat or the
        # durable month/ticker summary will carry the state forward.
        return


def process_ticker(job: TickerJob, cfg: AuditConfig) -> dict[str, object]:
    ticker = job.ticker
    ticker_summary_path = cfg.run_root / "ticker_summaries" / f"{ticker}.json"
    started_at = utc_now()
    months = list(iter_month_files(job, cfg))
    totals: dict[str, object] = {
        "ticker": ticker,
        "ticker_dir": str(job.ticker_dir),
        "status": "RUNNING",
        "months_planned": len(months),
        "months_done": 0,
        "months_with_repairs": 0,
        "repair_rows": 0,
        "ohlc_repair_rows": 0,
        "vw_invalid_rows": 0,
        "started_at_utc": started_at,
        "finished_at_utc": "",
        "error": "",
    }
    update_ticker_status(cfg, ticker, totals)

    try:
        for idx, month_file in enumerate(months, start=1):
            update_ticker_status(
                cfg,
                ticker,
                {
                    **totals,
                    "status": "RUNNING",
                    "months_done": idx - 1,
                    "current_year": month_file.year,
                    "current_month": month_file.month,
                    "current_path": str(month_file.path),
                },
            )
            month_summary = process_month_file(month_file, cfg)
            totals["months_done"] = int(totals["months_done"]) + 1
            if int(month_summary.get("repair_rows", 0)) > 0:
                totals["months_with_repairs"] = int(totals["months_with_repairs"]) + 1
            totals["repair_rows"] = int(totals["repair_rows"]) + int(month_summary.get("repair_rows", 0))
            totals["ohlc_repair_rows"] = int(totals["ohlc_repair_rows"]) + int(month_summary.get("ohlc_repair_rows", 0))
            totals["vw_invalid_rows"] = int(totals["vw_invalid_rows"]) + int(month_summary.get("vw_invalid_rows", 0))

        totals["status"] = "DONE"
        totals["finished_at_utc"] = utc_now()
        atomic_write_json(ticker_summary_path, totals)
        update_ticker_status(cfg, ticker, totals)
        return totals
    except Exception as exc:  # noqa: BLE001
        totals["status"] = "ERROR"
        totals["error"] = repr(exc)
        totals["finished_at_utc"] = utc_now()
        atomic_write_json(ticker_summary_path, totals)
        update_ticker_status(cfg, ticker, totals)
        return totals


def summarize_progress(run_root: Path) -> dict[str, object]:
    status_dir = run_root / "ticker_status"
    statuses: list[dict[str, object]] = []
    for path in status_dir.glob("*.json") if status_dir.exists() else []:
        try:
            statuses.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    status_counts: dict[str, int] = {}
    for row in statuses:
        status = str(row.get("status", "UNKNOWN"))
        status_counts[status] = status_counts.get(status, 0) + 1
    month_done = sum(int(row.get("months_done", 0) or 0) for row in statuses)
    month_planned = sum(int(row.get("months_planned", 0) or 0) for row in statuses)
    return {
        "observed_at_utc": utc_now(),
        "ticker_status_files": len(statuses),
        "status_counts": status_counts,
        "months_done": month_done,
        "months_planned_in_started_tickers": month_planned,
        "repair_rows": sum(int(row.get("repair_rows", 0) or 0) for row in statuses),
        "ohlc_repair_rows": sum(int(row.get("ohlc_repair_rows", 0) or 0) for row in statuses),
        "vw_invalid_rows": sum(int(row.get("vw_invalid_rows", 0) or 0) for row in statuses),
    }


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


def build_repairs_by_ticker(
    minute_root: Path,
    quotes_root: Path,
    run_root: Path,
    output_root: Path,
    workers: int,
    min_year: int | None,
    max_year: int | None,
    tickers: set[str] | None,
    max_tickers: int | None,
    max_months_per_ticker: int | None,
    cfg: QuoteGuardConfig,
    session_start: str,
    session_end: str,
    max_spread_pct: float | None,
    overwrite: bool,
    promote_manifest: bool,
    progress_interval_sec: int,
) -> dict[str, object]:
    if not minute_root.exists():
        raise FileNotFoundError(f"Missing minute root: {minute_root}")
    if not quotes_root.exists():
        raise FileNotFoundError(f"Missing quotes root: {quotes_root}")
    run_root.mkdir(parents=True, exist_ok=True)
    for name in ("ticker_status", "ticker_events", "ticker_summaries", "month_summaries", "repair_shards"):
        (run_root / name).mkdir(parents=True, exist_ok=True)

    audit_cfg = AuditConfig(
        minute_root=minute_root,
        quotes_root=quotes_root,
        run_root=run_root,
        output_root=output_root,
        quote_guard=cfg,
        session_start=session_start,
        session_end=session_end,
        max_spread_pct=max_spread_pct,
        min_year=min_year,
        max_year=max_year,
        max_months_per_ticker=max_months_per_ticker,
        overwrite=overwrite,
        promote_manifest=promote_manifest,
    )
    jobs = list(iter_ticker_jobs(minute_root, tickers=tickers, max_tickers=max_tickers))
    run_config = {
        "created_at_utc": utc_now(),
        "view_name": QUOTE_GUARDED_VIEW_NAME,
        "script_version": "v0_2_ticker_worker",
        "minute_root": str(minute_root),
        "quotes_root": str(quotes_root),
        "run_root": str(run_root),
        "output_root": str(output_root),
        "workers": workers,
        "min_year": min_year,
        "max_year": max_year,
        "tickers": sorted(tickers) if tickers is not None else None,
        "max_tickers": max_tickers,
        "max_months_per_ticker": max_months_per_ticker,
        "session_start": session_start,
        "session_end": session_end,
        "max_spread_pct": max_spread_pct,
        "quote_guard": asdict(cfg),
        "promote_manifest": promote_manifest,
        "overwrite": overwrite,
        "tickers_planned": len(jobs),
    }
    atomic_write_json(run_root / "run_config.json", run_config)
    print(f"planned tickers: {len(jobs)}", flush=True)

    results: list[dict[str, object]] = []
    completed = 0
    last_progress = datetime.now(timezone.utc)
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        future_to_job: dict[Future[dict[str, object]], TickerJob] = {
            pool.submit(process_ticker, job, audit_cfg): job for job in jobs
        }
        pending: set[Future[dict[str, object]]] = set(future_to_job)
        while pending:
            done, pending = wait(pending, timeout=max(1, progress_interval_sec), return_when=FIRST_COMPLETED)
            for fut in done:
                job = future_to_job[fut]
                completed += 1
                try:
                    result = fut.result()
                except Exception as exc:  # noqa: BLE001
                    result = {
                        "ticker": job.ticker,
                        "ticker_dir": str(job.ticker_dir),
                        "status": "ERROR",
                        "error": repr(exc),
                        "finished_at_utc": utc_now(),
                    }
                results.append(result)
                print(
                    f"ticker_done {completed}/{len(jobs)} {job.ticker} "
                    f"status={result.get('status')} months={result.get('months_done', 0)}/{result.get('months_planned', 0)} "
                    f"repairs={result.get('repair_rows', 0)}",
                    flush=True,
                )
            now = datetime.now(timezone.utc)
            if (now - last_progress).total_seconds() >= progress_interval_sec:
                progress = summarize_progress(run_root)
                atomic_write_json(run_root / "progress_snapshot.json", progress)
                print(
                    f"progress tickers_done={completed}/{len(jobs)} "
                    f"status={progress['status_counts']} "
                    f"months={progress['months_done']}/{progress['months_planned_in_started_tickers']} "
                    f"repairs={progress['repair_rows']} ohlc={progress['ohlc_repair_rows']} vw_invalid={progress['vw_invalid_rows']}",
                    flush=True,
                )
                last_progress = now

    ticker_summary = pd.DataFrame(results)
    ticker_summary_path = run_root / "ticker_summary.parquet"
    ticker_summary.to_parquet(ticker_summary_path, index=False)
    ticker_summary.to_csv(run_root / "ticker_summary.csv", index=False)

    shards = sorted((run_root / "repair_shards").glob("*_repair_manifest.parquet"))
    run_manifest = run_root / "repair_manifest.parquet"
    manifest_rows = _write_single_manifest(shards, run_manifest) if shards else 0
    _write_manifest_sample(run_manifest, run_root / "repair_manifest_sample.csv")

    promoted_manifest = ""
    if promote_manifest:
        output_root.mkdir(parents=True, exist_ok=True)
        promoted = output_root / "repair_manifest_v0_2.parquet"
        if shards:
            _write_single_manifest(shards, promoted)
            _write_manifest_sample(promoted, output_root / "repair_manifest_v0_2_sample.csv")
        elif promoted.exists() and overwrite:
            promoted.unlink()
        promoted_manifest = str(promoted)

    final_progress = summarize_progress(run_root)
    result = {
        **run_config,
        "finished_at_utc": utc_now(),
        "tickers_processed": int(len(ticker_summary)),
        "tickers_with_repairs": int((ticker_summary.get("repair_rows", 0) > 0).sum()) if not ticker_summary.empty else 0,
        "manifest_rows": int(manifest_rows),
        "ohlc_repair_rows": int(ticker_summary.get("ohlc_repair_rows", pd.Series(dtype=int)).sum()) if not ticker_summary.empty else 0,
        "vw_invalid_rows": int(ticker_summary.get("vw_invalid_rows", pd.Series(dtype=int)).sum()) if not ticker_summary.empty else 0,
        "run_manifest": str(run_manifest),
        "promoted_manifest": promoted_manifest,
        "ticker_summary": str(ticker_summary_path),
        "progress": final_progress,
    }
    atomic_write_json(run_root / "repair_summary.json", result)
    if promote_manifest:
        atomic_write_json(output_root / "repair_summary_v0_2.json", result)
    return result


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build quote-guarded OHLCV 1m repairs by assigning whole tickers to workers."
    )
    ap.add_argument("--minute-root", type=Path, default=DEFAULT_MINUTE_ROOT)
    ap.add_argument("--quotes-root", type=Path, default=DEFAULT_QUOTES_ROOT)
    ap.add_argument("--run-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--min-year", type=int)
    ap.add_argument("--max-year", type=int)
    ap.add_argument("--tickers", help="Comma-separated ticker allowlist for pilots.")
    ap.add_argument("--max-tickers", type=int)
    ap.add_argument("--max-months-per-ticker", type=int)
    ap.add_argument("--bid-quantile", type=float, default=0.01)
    ap.add_argument("--ask-quantile", type=float, default=0.99)
    ap.add_argument("--tolerance-pct", type=float, default=0.003)
    ap.add_argument("--abs-tolerance", type=float, default=0.0001)
    ap.add_argument("--min-quote-count", type=int, default=3)
    ap.add_argument("--session-start", default="04:00")
    ap.add_argument("--session-end", default="20:00")
    ap.add_argument("--max-spread-pct", type=float)
    ap.add_argument("--progress-interval-sec", type=int, default=30)
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
    result = build_repairs_by_ticker(
        minute_root=args.minute_root,
        quotes_root=args.quotes_root,
        run_root=args.run_root,
        output_root=args.output_root,
        workers=max(1, int(args.workers)),
        min_year=args.min_year,
        max_year=args.max_year,
        tickers=tickers,
        max_tickers=args.max_tickers,
        max_months_per_ticker=args.max_months_per_ticker,
        cfg=cfg,
        session_start=args.session_start,
        session_end=args.session_end,
        max_spread_pct=args.max_spread_pct,
        overwrite=bool(args.overwrite),
        promote_manifest=bool(args.promote_manifest),
        progress_interval_sec=max(5, int(args.progress_interval_sec)),
    )
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
