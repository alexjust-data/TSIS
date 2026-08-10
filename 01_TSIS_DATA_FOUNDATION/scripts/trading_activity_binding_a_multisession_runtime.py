#!/usr/bin/env python3
"""Physical-source adapters for the Trading Activity multisession engine."""

from __future__ import annotations

import csv
import math
from collections.abc import Sequence
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
from evaluate_trading_activity_trade_eligibility import evaluate_trade
from trading_activity_binding_a_multisession_engine import duplicate_key, normalize_utc


def _read_ticker_group_csv(path: Path, ticker: str) -> list[dict[str, Any]]:
    """Read one contiguous ticker group from a ticker-sorted acquisition CSV."""
    rows: list[dict[str, Any]] = []
    found = False
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            row_ticker = str(row.get("ticker", "")).upper()
            if row_ticker == ticker.upper():
                found = True
                rows.append(row)
            elif found:
                break
            elif row_ticker and row_ticker > ticker.upper():
                break
    return rows


def load_acquisition_evidence_bounded(
    acquisition_root: Path,
    *,
    ticker: str,
    selected_dates: set[date],
) -> list[dict[str, Any]]:
    """Resolve selected ticker-dates without traversing every acquisition task."""
    resolved: dict[date, dict[str, Any]] = {}
    for run_dir in sorted(path for path in acquisition_root.iterdir() if path.is_dir()):
        expected_path = run_dir / "expected_manifest_trades_ticks.csv"
        if not expected_path.is_file():
            continue
        expected = _read_ticker_group_csv(expected_path, ticker)
        relevant_dates = {
            pd.Timestamp(row["date"]).date()
            for row in expected
            if row.get("date")
        } & selected_dates
        if not relevant_dates:
            continue
        events: list[dict[str, Any]] = []
        for name in (
            "download_events_trades_ticks_history.csv",
            "download_events_trades_ticks_current.csv",
        ):
            path = run_dir / name
            if path.is_file():
                events.extend(_read_ticker_group_csv(path, ticker))
        for row in events:
            row_date = pd.Timestamp(row["date"]).date()
            if row_date in relevant_dates:
                resolved[row_date] = {
                    **row,
                    "session_date": row_date,
                    "run_id": run_dir.name,
                    "evidence_source": str(run_dir),
                }
    return [resolved[key] for key in sorted(resolved)]


def _normalize_conditions(value: Any) -> list[int]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    values = value.tolist() if hasattr(value, "tolist") else list(value)
    return [int(item) for item in values]


def load_and_evaluate_events(
    source_path: Path,
    *,
    matrix: dict[int, dict[str, str]],
    session_open: datetime,
    session_close: datetime,
    simulated_latency_ms: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    if not source_path.is_file():
        return [], {
            "source_trade_rows": 0,
            "eligible_trade_rows": 0,
            "unknown_fail_closed_rows": 0,
            "exact_duplicate_flag_rows": 0,
        }
    raw = pd.read_parquet(source_path)
    events: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    counters = {
        "source_trade_rows": int(len(raw)),
        "eligible_trade_rows": 0,
        "unknown_fail_closed_rows": 0,
        "exact_duplicate_flag_rows": 0,
    }
    latency = timedelta(milliseconds=simulated_latency_ms)
    for ordinal, raw_row in enumerate(raw.to_dict("records")):
        row = dict(raw_row)
        event_time = normalize_utc(row["timestamp"])
        row["timestamp"] = event_time
        row["exchange"] = (
            int(row["exchange"]) if pd.notna(row.get("exchange")) else None
        )
        row["conditions"] = _normalize_conditions(row.get("conditions"))
        if pd.notna(row.get("size")):
            row["size"] = int(row["size"])
        key = duplicate_key(row)
        exact_duplicate = key in seen
        seen.add(key)
        result = evaluate_trade(
            row,
            matrix,
            in_rth=session_open < event_time < session_close,
            source_available=True,
            exact_duplicate_research_flag=exact_duplicate,
        )
        state = result["trade_activity_eligibility_state"]
        counters["eligible_trade_rows"] += int(
            state == "ELIGIBLE_WITH_RESTRICTIONS"
        )
        counters["unknown_fail_closed_rows"] += int(state == "UNKNOWN_FAIL_CLOSED")
        counters["exact_duplicate_flag_rows"] += int(exact_duplicate)
        events.append(
            {
                "legacy_event_time": event_time,
                "simulated_available_at": event_time + latency,
                "price": float(row["price"]) if pd.notna(row.get("price")) else None,
                "size": int(row["size"]) if pd.notna(row.get("size")) else None,
                "exchange": row.get("exchange"),
                "conditions": row["conditions"],
                "ordinal": ordinal,
                "eligibility_state": state,
                "eligibility_reason_codes": result["eligibility_reason_codes"],
                "duplicate_research_flag": result["duplicate_research_flag"],
                "quality_state": result["quality_state"],
            }
        )
    events.sort(key=lambda event: (event["legacy_event_time"], event["ordinal"]))
    return events, counters


def choose_evaluation_dates(
    selected_dates: Sequence[date],
    *,
    evaluation_start: date,
    evaluation_end: date,
    smoke_mode: bool,
) -> set[date]:
    governed = {
        value for value in selected_dates if evaluation_start <= value <= evaluation_end
    }
    if governed or not smoke_mode:
        return governed
    return {max(selected_dates)} if selected_dates else set()
