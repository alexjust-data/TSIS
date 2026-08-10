"""Reconcile lifecycle candidates with bounded observed market presence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.storage import atomic_write_json  # noqa: E402

DEFAULT_EXTRACTION_RUN = Path(
    r"D:\TSIS\fundamental_context\sec_pit_v0_1\replays"
    r"\sec_pit_7t_lifecycle_extract_v0_2"
)
DEFAULT_METADATA_RUN = Path(
    r"D:\TSIS\fundamental_context\sec_pit_v0_1\replays"
    r"\sec_pit_7t_lifecycle_v0_2"
)
DEFAULT_OUTPUT_ROOT = Path(r"D:\TSIS\fundamental_context\sec_pit_v0_1")
DEFAULT_DAILY_ROOT = Path(r"G:\TSIS\data\ohlcv_daily")
DEFAULT_TRADES_ROOT = Path(r"G:\TSIS\data\trades_ticks_prod_2005_2026")
DAY_PATTERN = re.compile(r"day=(\d{4}-\d{2}-\d{2})")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(arguments: list[str]) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *arguments],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def within(value: str, start: str, end: str) -> bool:
    return start <= value <= end


def daily_presence(ticker_root: Path, start: str, end: str) -> dict[str, Any]:
    if not ticker_root.is_dir():
        return {
            "daily_presence_state": "DAILY_SOURCE_UNAVAILABLE",
            "daily_file_count_scanned": 0,
            "daily_observation_count": 0,
            "first_observed_daily_date": None,
            "last_observed_daily_date": None,
        }
    dates: list[str] = []
    files = sorted(ticker_root.rglob("*.parquet"))
    for path in files:
        table = pq.ParquetFile(path).read(columns=["date"])
        for value in table.column("date").to_pylist():
            date_value = str(value)[:10]
            if within(date_value, start, end):
                dates.append(date_value)
    return {
        "daily_presence_state": (
            "OBSERVED_DAILY_BOUNDS_WITHIN_IDENTITY_WINDOW"
            if dates
            else "NO_DAILY_OBSERVATION_WITHIN_IDENTITY_WINDOW"
        ),
        "daily_file_count_scanned": len(files),
        "daily_observation_count": len(dates),
        "first_observed_daily_date": min(dates) if dates else None,
        "last_observed_daily_date": max(dates) if dates else None,
    }


def _trade_file_date(path: Path) -> str | None:
    match = DAY_PATTERN.search(path.as_posix())
    return match.group(1) if match else None


def _timestamp_bound(path: Path, *, first: bool) -> Any:
    values = (
        pq.ParquetFile(path)
        .read(columns=["timestamp"])
        .column("timestamp")
        .to_pylist()
    )
    values = [value for value in values if value is not None]
    if not values:
        return None
    return min(values) if first else max(values)


def trade_presence(ticker_root: Path, start: str, end: str) -> dict[str, Any]:
    if not ticker_root.is_dir():
        return {
            "trade_presence_state": "TAPE_SOURCE_UNAVAILABLE",
            "trade_file_count_in_identity_window": 0,
            "first_observed_trade_timestamp_source_naive": None,
            "last_observed_trade_timestamp_source_naive": None,
            "trade_timestamp_semantics": "UNAVAILABLE",
        }
    candidates = []
    for path in ticker_root.rglob("*.parquet"):
        day = _trade_file_date(path)
        if day and within(day, start, end):
            candidates.append((day, path))
    candidates.sort(key=lambda item: (item[0], item[1].as_posix()))
    first_timestamp = None
    last_timestamp = None
    for _, path in candidates:
        first_timestamp = _timestamp_bound(path, first=True)
        if first_timestamp is not None:
            break
    for _, path in reversed(candidates):
        last_timestamp = _timestamp_bound(path, first=False)
        if last_timestamp is not None:
            break
    observed = first_timestamp is not None and last_timestamp is not None
    return {
        "trade_presence_state": (
            "OBSERVED_TAPE_BOUNDS_WITHIN_IDENTITY_WINDOW"
            if observed
            else "NO_TRADE_OBSERVATION_WITHIN_IDENTITY_WINDOW"
        ),
        "trade_file_count_in_identity_window": len(candidates),
        "first_observed_trade_timestamp_source_naive": first_timestamp,
        "last_observed_trade_timestamp_source_naive": last_timestamp,
        "trade_timestamp_semantics": (
            "SOURCE_NAIVE_REQUIRES_TIMEZONE_REVIEW" if observed else "UNAVAILABLE"
        ),
    }


def cross_source_boundary_state(
    daily: dict[str, Any],
    trades: dict[str, Any],
) -> str:
    first_trade = trades.get("first_observed_trade_timestamp_source_naive")
    last_trade = trades.get("last_observed_trade_timestamp_source_naive")
    if first_trade is None or last_trade is None:
        return "TAPE_UNAVAILABLE_FOR_COMPARISON"
    first_trade_date = str(first_trade)[:10]
    last_trade_date = str(last_trade)[:10]
    if (
        first_trade_date == daily.get("first_observed_daily_date")
        and last_trade_date == daily.get("last_observed_daily_date")
    ):
        return "DAILY_AND_TAPE_BOUNDARY_DATES_AGREE"
    return "CROSS_SOURCE_BOUNDARY_DATE_DIFFERENCE"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extraction-run", type=Path, default=DEFAULT_EXTRACTION_RUN)
    parser.add_argument("--metadata-run", type=Path, default=DEFAULT_METADATA_RUN)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--daily-root", type=Path, default=DEFAULT_DAILY_ROOT)
    parser.add_argument("--trades-root", type=Path, default=DEFAULT_TRADES_ROOT)
    parser.add_argument("--run-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extraction_run = args.extraction_run.resolve()
    metadata_run = args.metadata_run.resolve()
    output_root = args.output_root.resolve()
    daily_root = args.daily_root.resolve()
    trades_root = args.trades_root.resolve()
    run_root = output_root / "replays" / args.run_id
    run_root.mkdir(parents=True, exist_ok=False)

    observations_path = extraction_run / "lifecycle_source_observations.parquet"
    gates_path = metadata_run / "lifecycle_gate_matrix.parquet"
    observations = pd.read_parquet(observations_path)
    gates = pd.read_parquet(gates_path)
    tickers = sorted(observations["ticker"].unique())

    manifest = {
        "run_id": args.run_id,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "script_path": Path(__file__).resolve().as_posix(),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "command_line": sys.argv,
        "cwd": Path.cwd().as_posix(),
        "host": socket.gethostname(),
        "wrapper_pid": os.getpid(),
        "git_branch": git_value(["branch", "--show-current"]),
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["status", "--porcelain"])),
        "extraction_run": extraction_run.as_posix(),
        "metadata_run": metadata_run.as_posix(),
        "source_observations_sha256": sha256_file(observations_path),
        "source_gates_sha256": sha256_file(gates_path),
        "daily_root": daily_root.as_posix(),
        "trades_root": trades_root.as_posix(),
        "ticker_count": len(tickers),
        "output_root": output_root.as_posix(),
        "run_root": run_root.as_posix(),
        "promotion_status": "NOT_AUTHORIZED",
        "success_criteria": (
            "observed bounds emitted without promotion to legal listing or "
            "delisting boundaries"
        ),
    }
    atomic_write_json(run_root / "pre_manifest.json", manifest)
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "run_id": args.run_id,
            "wrapper_pid": os.getpid(),
            "started_at_utc": utc_now(),
            "expected_alive": True,
        },
    )

    rows: list[dict[str, Any]] = []
    for ticker in tickers:
        gate = gates.loc[gates["ticker"].eq(ticker)]
        if len(gate) != 1:
            raise ValueError(f"Expected one identity gate row for {ticker}")
        gate_row = gate.iloc[0]
        start = str(gate_row["first_observed_snapshot"])[:10]
        end = str(gate_row["last_observed_snapshot"])[:10]
        daily = daily_presence(daily_root / f"ticker={ticker}", start, end)
        trades = trade_presence(trades_root / ticker, start, end)
        boundary_state = cross_source_boundary_state(daily, trades)
        rows.append(
            {
                "ticker": ticker,
                "instrument_id": gate_row["instrument_id"],
                "identity_window_start": start,
                "identity_window_end": end,
                "identity_window_source": "GOVERNED_ALL_TICKERS_TARGET_IDENTITY_SNAPSHOTS",
                **daily,
                **trades,
                "cross_source_boundary_state": boundary_state,
                "legal_list_date": None,
                "legal_delist_date": None,
                "listing_resolution_state": (
                    "OBSERVED_MARKET_PRESENCE_ONLY_NOT_LEGAL_LIFECYCLE"
                ),
                "quality_state": (
                    "PASS_WITH_CROSS_SOURCE_BOUNDARY_DIFFERENCE"
                    if boundary_state == "CROSS_SOURCE_BOUNDARY_DATE_DIFFERENCE"
                    else "PASS_WITH_TAPE"
                    if trades["trade_presence_state"].startswith("OBSERVED")
                    else "PASS_DAILY_ONLY_TAPE_UNAVAILABLE"
                ),
                "promotion_status": "NOT_AUTHORIZED",
            }
        )
        atomic_write_json(
            run_root / "heartbeat_latest.json",
            {
                "run_id": args.run_id,
                "observed_at_utc": utc_now(),
                "status": "RUNNING",
                "stage": "RECONCILE_MARKET_PRESENCE",
                "wrapper_pid": os.getpid(),
                "completed": len(rows),
                "total": len(tickers),
                "ticker": ticker,
            },
        )

    frame = pd.DataFrame(rows)
    frame.to_parquet(run_root / "lifecycle_market_presence_bounds.parquet", index=False)
    hard_failures = {
        "row_count_not_six": len(frame) != 6,
        "duplicate_ticker": bool(frame.duplicated(["ticker"]).any()),
        "daily_source_missing": bool(
            frame["daily_presence_state"].ne(
                "OBSERVED_DAILY_BOUNDS_WITHIN_IDENTITY_WINDOW"
            ).any()
        ),
        "legal_list_date_populated": bool(frame["legal_list_date"].notna().any()),
        "legal_delist_date_populated": bool(frame["legal_delist_date"].notna().any()),
    }
    status = "PASS_WITH_RESTRICTIONS" if not any(hard_failures.values()) else "FAIL"
    readout = {
        "run_id": args.run_id,
        "status": status,
        "ticker_rows": len(frame),
        "daily_bounds_observed": int(
            frame["daily_presence_state"]
            .eq("OBSERVED_DAILY_BOUNDS_WITHIN_IDENTITY_WINDOW")
            .sum()
        ),
        "tape_bounds_observed": int(
            frame["trade_presence_state"]
            .eq("OBSERVED_TAPE_BOUNDS_WITHIN_IDENTITY_WINDOW")
            .sum()
        ),
        "tape_source_unavailable": int(
            frame["trade_presence_state"].eq("TAPE_SOURCE_UNAVAILABLE").sum()
        ),
        "cross_source_boundary_differences": int(
            frame["cross_source_boundary_state"]
            .eq("CROSS_SOURCE_BOUNDARY_DATE_DIFFERENCE")
            .sum()
        ),
        "hard_failures": hard_failures,
        "legal_list_dates_nonnull": int(frame["legal_list_date"].notna().sum()),
        "legal_delist_dates_nonnull": int(frame["legal_delist_date"].notna().sum()),
        "lifecycle_promotion": "NOT_AUTHORIZED",
    }
    atomic_write_json(run_root / "lifecycle_market_presence_readout.json", readout)
    final = {
        **manifest,
        **readout,
        "status": "COMPLETE" if status != "FAIL" else "FAILED",
        "completed_at_utc": utc_now(),
    }
    atomic_write_json(run_root / "final_manifest.json", final)
    atomic_write_json(
        run_root / "heartbeat_latest.json",
        {
            "run_id": args.run_id,
            "observed_at_utc": utc_now(),
            "status": final["status"],
            "stage": "MARKET_PRESENCE_COMPLETE",
            "wrapper_pid": os.getpid(),
            "completed": len(frame),
            "total": len(tickers),
        },
    )
    print(json.dumps(readout, indent=2))
    return 0 if status != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())