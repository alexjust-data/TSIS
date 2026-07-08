#!/usr/bin/env python
"""
EXP_DAS_FRONTSIDE_DISCOVERY_0002 - scanner denominator 2026.

Este script NO consume candidate_events.parquet ni anchors del DAS antiguo.
Construye el denominador del scanner desde:

1. E:/TSIS/data/ohlcv_1m
2. E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet
3. E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1
4. E:/TSIS/data/reference/overview

El objetivo es producir "tickers cazados por el scanner" con lineage claro.
Los anchors de estrategia (first push, dip, rebreak) se calculan despues, no aqui.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyarrow.parquet as pq

try:
    import duckdb
except ImportError as exc:  # pragma: no cover
    raise SystemExit("duckdb is required for quote-guarded manifest filtering") from exc


EXPERIMENT_ID = "EXP_DAS_FRONTSIDE_DISCOVERY_0002"
BUILDER_ID = "build_2026_scanner_from_quote_guarded_1m_v0_1"


@dataclass(frozen=True)
class ScannerConfig:
    year: int
    threshold_pct: float
    min_volume: float
    min_price: float
    max_price: float
    max_market_cap: float
    session_start_et: str
    session_end_et: str
    reference_price: str
    market_cap_policy: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_parquet_file(path: Path, columns: list[str] | None = None) -> pd.DataFrame:
    return pq.ParquetFile(str(path)).read(columns=columns).to_pandas()


def _sql_literal(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace("'", "''")


def _parse_tickers(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    return [x.strip().upper() for x in raw.split(",") if x.strip()]


def _time_to_minutes(value: str) -> int:
    hh, mm = value.split(":")
    return int(hh) * 60 + int(mm)


def _list_raw_files(raw_root: Path, year: int, tickers: list[str] | None, limit_files: int | None) -> list[Path]:
    files: list[Path] = []
    if tickers:
        for ticker in tickers:
            year_root = raw_root / f"ticker={ticker}" / f"year={year}"
            files.extend(sorted(year_root.glob("month=*/*.parquet")))
    else:
        files = sorted(raw_root.glob(f"ticker=*/year={year}/month=*/*.parquet"))
    if limit_files is not None:
        files = files[:limit_files]
    return files


def _load_daily_prior_close(master_daily_root: Path, years: Iterable[int]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for year in years:
        path = master_daily_root / f"year={year}" / "price_view=daily_raw" / "data_0.parquet"
        if not path.exists():
            continue
        cols = ["ticker", "session_date", "prior_close", "close"]
        part = _read_parquet_file(path, columns=cols)
        part["ticker"] = part["ticker"].astype(str).str.upper()
        part["session_date"] = pd.to_datetime(part["session_date"]).dt.date.astype(str)
        frames.append(part)
    if not frames:
        return pd.DataFrame(columns=["ticker", "session_date", "prior_close", "close"])
    daily = pd.concat(frames, ignore_index=True)
    daily = daily.sort_values(["ticker", "session_date"])
    missing_prior = daily["prior_close"].isna()
    daily.loc[missing_prior, "prior_close"] = daily.groupby("ticker")["close"].shift(1)[missing_prior]
    return daily


def _load_overview_history(overview_root: Path, ticker: str) -> pd.DataFrame:
    ticker_root = overview_root / f"ticker={ticker.upper()}"
    files = sorted(ticker_root.glob("*.parquet"))
    if not files:
        return pd.DataFrame(columns=["ticker", "market_cap", "request_date", "_ingested_utc"])
    frames: list[pd.DataFrame] = []
    for path in files:
        try:
            cols = ["ticker", "market_cap", "request_date", "_ingested_utc"]
            df = _read_parquet_file(path, columns=cols)
        except Exception:
            df = _read_parquet_file(path)
            keep = [c for c in ["ticker", "market_cap", "request_date", "_ingested_utc"] if c in df.columns]
            df = df[keep]
        if "request_date" not in df.columns:
            df["request_date"] = path.stem.rsplit("_", 1)[-1]
        frames.append(df)
    hist = pd.concat(frames, ignore_index=True)
    hist["ticker"] = hist["ticker"].astype(str).str.upper()
    hist["request_date"] = pd.to_datetime(hist["request_date"], errors="coerce").dt.date.astype(str)
    hist["market_cap"] = pd.to_numeric(hist["market_cap"], errors="coerce")
    return hist.sort_values("request_date")


def _market_cap_for_date(hist: pd.DataFrame, session_date: str) -> tuple[float | None, str | None, str]:
    if hist.empty:
        return None, None, "missing_overview"
    asof = hist[hist["request_date"] <= session_date].dropna(subset=["market_cap"])
    if not asof.empty:
        row = asof.iloc[-1]
        return float(row["market_cap"]), str(row["request_date"]), "asof"
    with_cap = hist.dropna(subset=["market_cap"])
    if with_cap.empty:
        return None, None, "missing_market_cap"
    row = with_cap.iloc[-1]
    return float(row["market_cap"]), str(row["request_date"]), "future_snapshot_review"


def _load_repairs_for_file(
    con: duckdb.DuckDBPyConnection,
    manifest: Path,
    shard_roots: list[Path],
    ticker: str,
    year: int,
    month: int,
) -> pd.DataFrame:
    shard_name = f"{ticker.upper()}_{int(year)}_{int(month):02d}_repair_manifest.parquet"
    for root in shard_roots:
        shard = root / shard_name
        if shard.exists():
            df = _read_parquet_file(shard)
            df["repair_source_file"] = str(shard)
            return df
    manifest_sql = _sql_literal(manifest)
    ticker_sql = ticker.replace("'", "''")
    query = f"""
        SELECT
            ticker,
            ts_utc,
            o_qg,
            h_qg,
            l_qg,
            c_qg,
            repair_state,
            repair_reason,
            quote_guarded_repair_applied,
            source_ohlcv_path,
            run_root
        FROM read_parquet('{manifest_sql}')
        WHERE ticker = '{ticker_sql}'
          AND year = {int(year)}
          AND month = {int(month)}
    """
    try:
        df = con.execute(query).df()
        df["repair_source_file"] = str(manifest)
        return df
    except Exception as exc:
        print(f"[WARN] repair query failed for {ticker} {year}-{month:02d}: {exc}")
        return pd.DataFrame()


def _prepare_intraday(raw: pd.DataFrame, repairs: pd.DataFrame) -> pd.DataFrame:
    raw = raw.copy()
    raw["ticker"] = raw["ticker"].astype(str).str.upper()
    raw["ts_utc_dt"] = pd.to_datetime(raw["ts_utc"], utc=True, errors="coerce")

    if repairs.empty:
        for col in ["o_qg", "h_qg", "l_qg", "c_qg"]:
            raw[col] = raw[col[0]]
        raw["repair_state"] = "no_manifest_rows"
        raw["repair_reason"] = pd.NA
        raw["quote_guarded_repair_applied"] = False
        raw["quote_guarded_join_state"] = "no_manifest_rows"
        raw["source_ohlcv_path"] = pd.NA
        raw["run_root"] = pd.NA
        return raw

    repairs = repairs.copy()
    repairs["ticker"] = repairs["ticker"].astype(str).str.upper()
    repairs["ts_utc_dt"] = pd.to_datetime(repairs["ts_utc"], utc=True, errors="coerce")
    repairs = repairs.drop_duplicates(["ticker", "ts_utc_dt"], keep="last")

    merged = raw.merge(
        repairs.drop(columns=["ts_utc"], errors="ignore"),
        on=["ticker", "ts_utc_dt"],
        how="left",
        suffixes=("", "_repair"),
    )
    for qg, raw_col in [("o_qg", "o"), ("h_qg", "h"), ("l_qg", "l"), ("c_qg", "c")]:
        merged[qg] = pd.to_numeric(merged[qg], errors="coerce").fillna(pd.to_numeric(merged[raw_col], errors="coerce"))
    merged["repair_state"] = merged["repair_state"].fillna("manifest_no_row_for_bar")
    merged["quote_guarded_repair_applied"] = merged["quote_guarded_repair_applied"].where(merged["quote_guarded_repair_applied"].notna(), False).astype(bool)
    merged["quote_guarded_join_state"] = "joined_or_raw_fallback"
    return merged


def _add_session_fields(df: pd.DataFrame, session_start: str, session_end: str) -> pd.DataFrame:
    out = df.copy()
    et = out["ts_utc_dt"].dt.tz_convert("America/New_York")
    out["ts_et"] = et
    out["session_date"] = et.dt.date.astype(str)
    out["minute_et"] = et.dt.hour * 60 + et.dt.minute
    start = _time_to_minutes(session_start)
    end = _time_to_minutes(session_end)
    out = out[(out["minute_et"] >= start) & (out["minute_et"] < end)].copy()
    out = out.sort_values(["ticker", "session_date", "ts_utc_dt"])
    out["session_bar_index"] = out.groupby(["ticker", "session_date"]).cumcount() + 1
    out["scanner_accumulated_volume"] = out.groupby(["ticker", "session_date"])["v"].cumsum()
    return out


def _market_gate(cap: float | None, cap_state: str, max_market_cap: float) -> str:
    if cap is None or pd.isna(cap):
        return "missing"
    prefix = "pass" if cap <= max_market_cap else "fail"
    if cap_state != "asof":
        return f"{prefix}_{cap_state}"
    return prefix


def _build_candidates(
    intraday: pd.DataFrame,
    daily: pd.DataFrame,
    overview_cache: dict[str, pd.DataFrame],
    overview_root: Path,
    config: ScannerConfig,
    raw_file: Path,
) -> list[dict]:
    if intraday.empty:
        return []

    daily_key = daily.set_index(["ticker", "session_date"])["prior_close"]
    candidates: list[dict] = []

    for (ticker, session_date), group in intraday.groupby(["ticker", "session_date"], sort=False):
        prior_close = daily_key.get((ticker, session_date), pd.NA)
        prior_close = pd.to_numeric(pd.Series([prior_close]), errors="coerce").iloc[0]
        if pd.isna(prior_close) or prior_close <= 0:
            continue

        if ticker not in overview_cache:
            overview_cache[ticker] = _load_overview_history(overview_root, ticker)
        market_cap, market_cap_asof, market_cap_state = _market_cap_for_date(overview_cache[ticker], session_date)
        market_cap_gate_state = _market_gate(market_cap, market_cap_state, config.max_market_cap)

        group = group.copy()
        group["scanner_gate_prior_close_pct"] = (pd.to_numeric(group["c_qg"], errors="coerce") / prior_close - 1.0) * 100.0
        group["price_gate_pass"] = (
            (pd.to_numeric(group["c_qg"], errors="coerce") >= config.min_price)
            & (pd.to_numeric(group["c_qg"], errors="coerce") <= config.max_price)
        )
        group["volume_gate_pass"] = group["scanner_accumulated_volume"] >= config.min_volume
        group["threshold_gate_pass"] = True
        group["momentum_threshold_filter_used"] = False
        group["market_cap_gate_pass"] = bool(market_cap is not None and not pd.isna(market_cap) and market_cap <= config.max_market_cap)

        if config.market_cap_policy == "asof_only":
            group["market_cap_inclusion_pass"] = group["market_cap_gate_pass"] & (market_cap_state == "asof")
        elif config.market_cap_policy == "snapshot_allowed_flagged":
            group["market_cap_inclusion_pass"] = group["market_cap_gate_pass"]
        elif config.market_cap_policy == "flag_only":
            group["market_cap_inclusion_pass"] = True
        else:
            raise ValueError(f"Unsupported market_cap_policy: {config.market_cap_policy}")

        gate = group[
            group["price_gate_pass"]
            & group["volume_gate_pass"]
            & group["market_cap_inclusion_pass"]
        ]
        if gate.empty:
            continue

        row = gate.iloc[0]
        candidates.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "sweep_id": f"denominator_no_momentum_threshold_vol_{config.min_volume:g}_{config.market_cap_policy}",
                "scanner_config_id": f"{BUILDER_ID}__{config.year}__denominator_price_volume_mcap_no_momentum_threshold",
                "builder_id": BUILDER_ID,
                "ticker": ticker,
                "session_date": session_date,
                "scanner_gate_ts_utc": row["ts_utc_dt"].isoformat(),
                "scanner_gate_ts_et": row["ts_et"].isoformat(),
                "scanner_gate_price": float(row["c_qg"]),
                "scanner_gate_prior_close_pct": float(row["scanner_gate_prior_close_pct"]),
                "scanner_gate_accumulated_volume": float(row["scanner_accumulated_volume"]),
                "scanner_gate_bar_index": int(row["session_bar_index"]),
                "prior_close": float(prior_close),
                "reference_price": config.reference_price,
                "threshold_pct": None,
                "momentum_threshold_filter_used": False,
                "denominator_filter_rule": "price_volume_market_cap_only_no_momentum_threshold_v0_2",
                "min_volume": float(config.min_volume),
                "min_price": float(config.min_price),
                "max_price": float(config.max_price),
                "max_market_cap": float(config.max_market_cap),
                "market_cap": None if market_cap is None or pd.isna(market_cap) else float(market_cap),
                "market_cap_asof": market_cap_asof,
                "market_cap_source_state": market_cap_state,
                "market_cap_gate_state": market_cap_gate_state,
                "price_gate_state": "pass",
                "volume_gate_state": "pass",
                "threshold_gate_state": "not_used_denominator_no_momentum_filter",
                "quote_guarded_join_state": str(row.get("quote_guarded_join_state", "")),
                "quote_guarded_repair_applied_at_gate": bool(row.get("quote_guarded_repair_applied", False)),
                "repair_state_at_gate": str(row.get("repair_state", "")),
                "repair_reason_at_gate": None if pd.isna(row.get("repair_reason", pd.NA)) else str(row.get("repair_reason")),
                "source_raw_ohlcv_file": str(raw_file),
                "source_ohlcv_path_from_manifest": None
                if pd.isna(row.get("source_ohlcv_path", pd.NA))
                else str(row.get("source_ohlcv_path")),
                "source_quote_guarded_run_root": None if pd.isna(row.get("run_root", pd.NA)) else str(row.get("run_root")),
                "created_utc": _utc_now(),
                "candidate_events_legacy_used": False,
                "old_das_run_used": False,
            }
        )
    return candidates


def _write_summary(out_dir: Path, candidates: pd.DataFrame, manifest: dict) -> None:
    lines = [
        "# Scanner 2026 Quote-Guarded Summary",
        "",
        f"created_utc: `{manifest['created_utc']}`",
        f"builder_id: `{manifest['builder_id']}`",
        "",
        "## Regla Critica",
        "",
        "Este run no usa `candidate_events.parquet` ni anchors del DAS antiguo.",
        "",
        "## Counts",
        "",
        f"- raw_files_seen: {manifest['raw_files_seen']}",
        f"- raw_files_read: {manifest['raw_files_read']}",
        f"- candidates_emitted: {len(candidates)}",
        "",
        "## Market Cap",
        "",
        f"- market_cap_policy: `{manifest['config']['market_cap_policy']}`",
        "- `future_snapshot_review` no es legal como estado as-of; sirve solo para screening research si se declara.",
        "",
    ]
    if not candidates.empty:
        by_state = candidates["market_cap_source_state"].value_counts(dropna=False).to_dict()
        lines.append(f"- market_cap_source_state_counts: `{by_state}`")
    (out_dir / "scanner_2026_quote_guarded_summary_v0_1.md").write_text("\n".join(lines), encoding="utf-8")


def _write_progress_snapshot(
    out_dir: Path,
    candidates: list[dict],
    config: ScannerConfig,
    total_files: int,
    files_scanned: int,
    files_read: int,
    current_file: Path | None,
) -> None:
    partial_csv = out_dir / "scanner_2026_quote_guarded_denominator_partial_v0_1.csv"
    if candidates:
        pd.DataFrame(candidates).to_csv(partial_csv, index=False)
    progress = {
        "updated_utc": _utc_now(),
        "builder_id": BUILDER_ID,
        "experiment_id": EXPERIMENT_ID,
        "status": "running",
        "total_files": total_files,
        "files_scanned": files_scanned,
        "files_read": files_read,
        "raw_candidates": len(candidates),
        "current_file": str(current_file) if current_file else None,
        "partial_csv": str(partial_csv) if candidates else None,
        "config": asdict(config),
    }
    (out_dir / "scanner_2026_quote_guarded_progress_v0_1.json").write_text(
        json.dumps(progress, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def build(args: argparse.Namespace) -> None:
    raw_root = Path(args.raw_root)
    repair_manifest = Path(args.repair_manifest)
    shard_roots = [Path(x) for x in str(args.repair_shard_roots).split(";") if x]
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
            f"raw_root={raw_root} year={args.year} "
            f"tickers={','.join(tickers) if tickers else 'all'}",
            flush=True,
        )
    raw_files = _list_raw_files(raw_root, args.year, tickers, args.limit_files)
    if args.verbose:
        print(f"files_to_scan={len(raw_files)}", flush=True)
        print(
            "loading_daily_prior_close "
            f"root={master_daily_root} years={args.year - 1},{args.year}",
            flush=True,
        )
    daily = _load_daily_prior_close(master_daily_root, [args.year - 1, args.year])
    if args.verbose:
        print(f"daily_prior_close_rows={len(daily)}", flush=True)
    overview_cache: dict[str, pd.DataFrame] = {}
    con = duckdb.connect(database=":memory:")

    all_candidates: list[dict] = []
    read_count = 0
    repair_rows_total = 0
    repair_applied_rows_total = 0
    skipped_files: list[str] = []
    last_partial_count = 0
    progress_every = max(1, int(args.progress_every))
    partial_flush_every = max(0, int(args.partial_flush_every))

    for idx, raw_file in enumerate(raw_files, start=1):
        if args.verbose:
            print(
                f"processing files_scanned={idx}/{len(raw_files)} "
                f"raw_candidates={len(all_candidates)} current={raw_file}",
                flush=True,
            )
        try:
            raw = _read_parquet_file(raw_file)
            if raw.empty:
                if args.verbose and (idx == 1 or idx % progress_every == 0):
                    print(
                        f"progress files_scanned={idx}/{len(raw_files)} "
                        f"raw_candidates={len(all_candidates)} read_files={read_count} current={raw_file}",
                        flush=True,
                    )
                continue
            ticker = str(raw["ticker"].dropna().iloc[0]).upper()
            year = int(raw["year"].dropna().iloc[0])
            month = int(raw["month"].dropna().iloc[0])
            repairs = _load_repairs_for_file(con, repair_manifest, shard_roots, ticker, year, month)
            repair_rows_total += len(repairs)
            intraday = _prepare_intraday(raw, repairs)
            repair_applied_rows_total += int(intraday["quote_guarded_repair_applied"].fillna(False).sum())
            intraday = _add_session_fields(intraday, args.session_start_et, args.session_end_et)
            before_candidates = len(all_candidates)
            all_candidates.extend(
                _build_candidates(intraday, daily, overview_cache, overview_root, config, raw_file)
            )
            read_count += 1
            emitted = len(all_candidates) - before_candidates
            if args.verbose:
                print(
                    f"[OK] files_scanned={idx}/{len(raw_files)} "
                    f"read_files={read_count} emitted={emitted} "
                    f"raw_candidates={len(all_candidates)} current={raw_file}",
                    flush=True,
                )
            if args.verbose and (idx == 1 or idx % progress_every == 0 or emitted > 0):
                print(
                    f"progress files_scanned={idx}/{len(raw_files)} "
                    f"raw_candidates={len(all_candidates)} read_files={read_count} current={raw_file}",
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
                _write_progress_snapshot(
                    out_dir, all_candidates, config, len(raw_files), idx, read_count, raw_file
                )
                last_partial_count = len(all_candidates)
        except Exception as exc:
            skipped_files.append(f"{raw_file}: {exc}")
            print(f"[WARN] skipped {raw_file}: {exc}", flush=True)
            _write_progress_snapshot(out_dir, all_candidates, config, len(raw_files), idx, read_count, raw_file)

    _write_progress_snapshot(out_dir, all_candidates, config, len(raw_files), len(raw_files), read_count, None)
    candidates = pd.DataFrame(all_candidates)
    parquet_path = out_dir / "scanner_2026_quote_guarded_denominator_v0_1.parquet"
    csv_path = out_dir / "scanner_2026_quote_guarded_denominator_v0_1.csv"
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
        "raw_root": str(raw_root),
        "repair_manifest": str(repair_manifest),
        "repair_shard_roots": [str(x) for x in shard_roots],
        "master_daily_root": str(master_daily_root),
        "reference_overview_root": str(overview_root),
        "output_dir": str(out_dir),
        "config": asdict(config),
        "raw_files_seen": len(raw_files),
        "raw_files_read": read_count,
        "repair_rows_loaded": repair_rows_total,
        "repair_applied_rows_seen": repair_applied_rows_total,
        "candidates_emitted": len(candidates),
        "skipped_files": skipped_files,
    }
    (out_dir / "scanner_2026_quote_guarded_run_manifest_v0_1.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    _write_summary(out_dir, candidates, manifest)
    print(json.dumps({k: manifest[k] for k in ["raw_files_seen", "raw_files_read", "candidates_emitted"]}, indent=2))
    print(f"wrote={parquet_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", default=r"E:\TSIS\data\ohlcv_1m")
    parser.add_argument(
        "--repair-manifest",
        default=r"E:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet",
    )
    parser.add_argument(
        "--repair-shard-roots",
        default=(
            r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_20260627_091838\repair_shards"
            r";C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_lt1b_missing180_20260703_092956\repair_shards"
            r";C:\TSIS_Data\01_TSIS_backtest_SmallCaps\runs\data_foundation\ohlcv_1m_quote_guarded\quote_guarded_v0_2_lt1b_licn_repair_20260703\repair_shards"
        ),
        help="Semicolon-separated repair shard roots. The consolidated manifest is only a fallback.",
    )
    parser.add_argument(
        "--master-daily-root",
        default=r"E:\TSIS\data\data_foundation_outputs\master_daily_table\master_daily_table_v0_1",
    )
    parser.add_argument("--reference-overview-root", default=r"E:\TSIS\data\reference\overview")
    parser.add_argument(
        "--output-dir",
        default=r"C:\TSIS_Data\00_TSIS_Lab\04_experiments\EXP_DAS_FRONTSIDE_DISCOVERY_0002\evidence\scanner_2026_quote_guarded_v0_1",
    )
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--tickers", default=None, help="Comma-separated tickers for smoke runs.")
    parser.add_argument("--limit-files", type=int, default=None)
    parser.add_argument("--threshold-pct", type=float, default=50.0)
    parser.add_argument("--min-volume", type=float, default=500000.0)
    parser.add_argument("--min-price", type=float, default=0.5)
    parser.add_argument("--max-price", type=float, default=20.0)
    parser.add_argument("--max-market-cap", type=float, default=100000000.0)
    parser.add_argument("--session-start-et", default="03:30")
    parser.add_argument("--session-end-et", default="09:30")
    parser.add_argument(
        "--market-cap-policy",
        choices=["asof_only", "snapshot_allowed_flagged", "flag_only"],
        default="snapshot_allowed_flagged",
        help=(
            "asof_only is legal for state. snapshot_allowed_flagged is research-only when PIT market cap is unavailable."
        ),
    )
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--partial-flush-every", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())




