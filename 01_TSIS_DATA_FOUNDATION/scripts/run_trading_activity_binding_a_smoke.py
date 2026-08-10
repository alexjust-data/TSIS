#!/usr/bin/env python3
"""Run Binding A current-state kernel on one governed physical partition."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pyarrow.compute as pc
import pyarrow.parquet as pq

from evaluate_trading_activity_trade_eligibility import (
    evaluate_trade,
    load_condition_matrix,
)
from trading_activity_binding_a_kernel import WINDOW_SECONDS, compute_window_state


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def calendar_session(calendar_path: Path, session_date: date) -> dict[str, Any]:
    columns = [
        "session_date",
        "open_utc",
        "close_utc",
        "calendar",
        "is_early_close",
        "build_run_id",
        "schema_version",
    ]
    table = pq.ParquetFile(calendar_path).read(columns=columns)
    mask = pc.equal(table["session_date"], session_date)
    rows = table.filter(mask).to_pylist()
    rows = [row for row in rows if row["calendar"] == "XNYS"]
    if len(rows) != 1:
        raise ValueError(
            f"Expected one XNYS calendar row for {session_date}, found {len(rows)}"
        )
    return rows[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trades-parquet", required=True, type=Path)
    parser.add_argument("--condition-matrix", required=True, type=Path)
    parser.add_argument("--market-calendar", required=True, type=Path)
    parser.add_argument("--session-date", required=True, type=date.fromisoformat)
    parser.add_argument("--decision-timestamp-utc", required=True)
    parser.add_argument("--latency-ms", required=True, type=int)
    parser.add_argument("--latency-policy-id", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.latency_ms < 0:
        raise ValueError("latency-ms must be non-negative")

    session = calendar_session(args.market_calendar, args.session_date)
    session_open = session["open_utc"].astimezone(timezone.utc)
    session_close = session["close_utc"].astimezone(timezone.utc)
    decision_timestamp = utc_datetime(args.decision_timestamp_utc)
    if not session_open < decision_timestamp < session_close:
        raise ValueError("decision timestamp is outside governed XNYS RTH")

    columns = ["ticker", "date", "timestamp", "price", "size", "exchange", "conditions"]
    rows = pq.ParquetFile(args.trades_parquet).read(columns=columns).to_pylist()
    matrix = load_condition_matrix(args.condition_matrix)
    latency = timedelta(milliseconds=args.latency_ms)
    state_counts: Counter[str] = Counter()
    events: list[dict[str, Any]] = []

    for ordinal, row in enumerate(rows):
        policy_result = evaluate_trade(
            row,
            matrix,
            in_rth=True,
            source_available=True,
            exact_duplicate_research_flag=False,
        )
        state = policy_result["trade_activity_eligibility_state"]
        state_counts[state] += 1
        timestamp = row["timestamp"]
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        if state not in {"ELIGIBLE_WITH_RESTRICTIONS", "UNKNOWN_FAIL_CLOSED"}:
            continue
        events.append(
            {
                "legacy_event_time": timestamp,
                "simulated_available_at": timestamp + latency,
                "price": row["price"],
                "size": row["size"],
                "ordinal": ordinal,
                "eligibility_state": state,
            }
        )

    states = [
        compute_window_state(
            events,
            decision_timestamp=decision_timestamp,
            session_open=session_open,
            window_seconds=window,
            coverage_gate_pass=True,
        )
        for window in WINDOW_SECONDS
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    state_path = args.output_dir / "trading_activity_binding_a_smoke_current_state_v0_1.json"
    manifest_path = args.output_dir / "trading_activity_binding_a_smoke_v0_1.manifest.json"
    payload = {
        "binding_id": "trading_activity_binding_a_minimal_multiscale_rth_v0_2",
        "scope_id": "legacy_rth_reconciled_event_time_research_only",
        "latency_policy_id": args.latency_policy_id,
        "latency_ms": args.latency_ms,
        "session_date": args.session_date,
        "decision_timestamp_utc": decision_timestamp,
        "session_open_utc": session_open,
        "session_close_utc": session_close,
        "market_calendar_build_run_id": session["build_run_id"],
        "market_calendar_schema_version": session["schema_version"],
        "is_early_close": session["is_early_close"],
        "source_row_count": len(rows),
        "policy_state_counts": dict(sorted(state_counts.items())),
        "window_states": states,
        "artifact_status": "EXPERIMENTAL_SMOKE_NOT_CANONICAL",
        "future_window_used": False,
    }
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, default=json_default)
        handle.write("\n")

    manifest = {
        "artifact_id": "trading_activity_binding_a_smoke",
        "artifact_version": "v0_1",
        "artifact_status": "EXPERIMENTAL_SMOKE_NOT_CANONICAL",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_parquet_path": str(args.trades_parquet.resolve()),
        "source_parquet_sha256": sha256_file(args.trades_parquet),
        "condition_matrix_path": str(args.condition_matrix.resolve()),
        "condition_matrix_sha256": sha256_file(args.condition_matrix),
        "market_calendar_path": str(args.market_calendar.resolve()),
        "market_calendar_sha256": sha256_file(args.market_calendar),
        "market_calendar_build_run_id": session["build_run_id"],
        "state_output_path": str(state_path.resolve()),
        "state_output_sha256": sha256_file(state_path),
        "canonical_promotion_authorized": False,
        "detector_consumption_authorized": False,
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
