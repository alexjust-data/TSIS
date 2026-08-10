#!/usr/bin/env python3
"""Reusable engine for the experimental Trading Activity Binding A pilot."""

from __future__ import annotations

import bisect
import hashlib
import json
import math
import os
import random
import time
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.dataset as ds
from evaluate_trading_activity_trade_eligibility import (
    evaluate_trade,
)
from trading_activity_binding_a_kernel import (
    BASELINE_LOOKBACKS,
    BASELINE_MIN_SESSIONS,
    SHORT_LONG_PAIRS,
    WINDOW_SECONDS,
    _distribution_summary,
    compute_multiscale_log_ratio,
    compute_window_state,
)

UTC = UTC
VARIABLE_FAMILIES = (
    "EVENT_COUNT_AND_INTENSITY",
    "SHARE_VOLUME_AND_MARKS",
    "DOLLAR_VOLUME",
    "DURATION_AND_CONCENTRATION",
)
FLOAT_COMPARISON_TOLERANCE = 1e-12
BASELINE_DISTRIBUTION_FIELDS = (
    "total_count",
    "zero_count",
    "positive_count",
    "zero_fraction",
    "unconditional_median",
    "positive_median",
    "positive_mad",
    "positive_p50",
    "positive_p75",
    "positive_p90",
    "positive_p95",
    "positive_p99",
)
BASELINE_LABELS = ("trade_count", "share_volume", "dollar_volume", "arrival_rate")
BASELINE_VALUE_COLUMNS = tuple(
    f"baseline_{label}_{field}"
    for label in BASELINE_LABELS
    for field in BASELINE_DISTRIBUTION_FIELDS
) + (
    "trade_count_percentile_pit",
    "share_volume_percentile_pit",
    "dollar_volume_percentile_pit",
    "arrival_rate_percentile_pit",
    "trade_count_log_ratio_to_pit",
    "share_volume_log_ratio_to_pit",
    "dollar_volume_log_ratio_to_pit",
    "baseline_median_intertrade_duration_us",
    "intertrade_duration_compression",
)
BASELINE_RESULT_COLUMNS = tuple(
    dict.fromkeys(
        (
            "baseline_candidate_id",
            "reference_session_count",
            "reference_observation_count",
            "first_reference_date",
            "last_reference_date",
            "baseline_input_max_available_at",
            "baseline_calculation_state",
            "baseline_zero_dominated",
            "baseline_duration_calculation_state",
        )
        + BASELINE_VALUE_COLUMNS
    )
)


CURRENT_STATE_FLOAT_COLUMNS = (
    "eligible_share_volume",
    "eligible_dollar_volume",
    "trade_arrival_rate",
    "median_intertrade_duration_us",
    "p10_intertrade_duration_us",
    "largest_trade_volume_share",
    "active_subwindow_fraction",
    "max_subwindow_trade_share",
    "max_subwindow_volume_share",
)
CURRENT_STATE_INTEGER_COLUMNS = (
    "window_seconds",
    "subwindow_seconds",
    "observable_seconds",
    "eligible_trade_count",
    "consecutive_active_subwindows",
    "input_event_count",
    "degrading_event_count",
)


def _typed_numeric(frame: pd.DataFrame, columns: Sequence[str], dtype: str) -> None:
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype(dtype)


def _typed_utc(frame: pd.DataFrame, columns: Sequence[str]) -> None:
    for column in columns:
        frame[column] = pd.to_datetime(frame[column], utc=True, errors="coerce")


def _stabilize_current_state(frame: pd.DataFrame) -> pd.DataFrame:
    _typed_numeric(frame, CURRENT_STATE_FLOAT_COLUMNS, "Float64")
    _typed_numeric(frame, CURRENT_STATE_INTEGER_COLUMNS, "Int64")
    _typed_utc(frame, ("decision_timestamp", "feature_input_max_available_at"))
    frame["future_window_used"] = frame["future_window_used"].astype("boolean")
    return frame


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_text(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _replace_with_retry(source: Path, target: Path, attempts: int = 12) -> None:
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.05 * (attempt + 1))


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".t{os.getpid():x}{time.time_ns():x}"
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    _replace_with_retry(temporary, path)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".t{os.getpid():x}{time.time_ns():x}"
    temporary.write_text(text, encoding="utf-8")
    _replace_with_retry(temporary, path)


def atomic_write_parquet(
    frame: pd.DataFrame,
    path: Path,
    *,
    compression: str = "zstd",
    allow_existing_valid: bool = False,
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    hash_path = path.with_suffix(path.suffix + ".sha256")
    if path.exists():
        if not allow_existing_valid or not hash_path.exists():
            raise FileExistsError(f"Refusing to overwrite existing partition: {path}")
        expected = hash_path.read_text(encoding="ascii").strip()
        actual = sha256_file(path)
        if expected != actual:
            raise ValueError(f"Existing partition hash mismatch: {path}")
        return {
            "path": str(path),
            "sha256": actual,
            "rows": len(pd.read_parquet(path, columns=[])),
            "bytes": path.stat().st_size,
            "resumed": True,
        }

    temporary = path.parent / f".t{os.getpid():x}{time.time_ns():x}"
    frame.to_parquet(temporary, index=False, compression=compression)
    partition_hash = sha256_file(temporary)
    partition_bytes = temporary.stat().st_size
    _replace_with_retry(temporary, path)
    atomic_write_text(hash_path, partition_hash + "\n")
    return {
        "path": str(path),
        "sha256": partition_hash,
        "rows": int(len(frame)),
        "bytes": int(partition_bytes),
        "resumed": False,
    }


def normalize_utc(value: Any) -> datetime:
    parsed = pd.Timestamp(value)
    if parsed.tzinfo is None:
        parsed = parsed.tz_localize("UTC")
    else:
        parsed = parsed.tz_convert("UTC")
    return parsed.to_pydatetime()


def resolve_trade_path(raw_root: Path, ticker: str, session_date: date) -> Path:
    return (
        raw_root
        / ticker
        / f"year={session_date.year:04d}"
        / f"month={session_date.month:02d}"
        / f"day={session_date.isoformat()}"
        / "market.parquet"
    )


def select_calendar_block(
    calendar_path: Path,
    *,
    calendar_name: str,
    start: date,
    end: date,
    expected_count: int | None = None,
    session_limit: int | None = None,
) -> pd.DataFrame:
    frame = pd.read_parquet(calendar_path)
    dates = pd.to_datetime(frame["session_date"]).dt.date
    selected = frame.loc[
        (frame["calendar"] == calendar_name) & (dates >= start) & (dates <= end)
    ].copy()
    selected["session_date"] = pd.to_datetime(selected["session_date"]).dt.date
    selected = selected.sort_values("session_date").reset_index(drop=True)
    if session_limit is not None:
        selected = selected.head(session_limit).copy()
    elif expected_count is not None and len(selected) != expected_count:
        raise ValueError(
            f"Calendar scope has {len(selected)} sessions; expected {expected_count}"
        )
    if selected.empty:
        raise ValueError("Calendar scope is empty")
    if selected["session_date"].duplicated().any():
        raise ValueError("Calendar scope contains duplicate session dates")
    return selected


def resolve_identity(
    instrument_master_path: Path,
    *,
    ticker: str,
    instrument_id: str,
    start: date,
    end: date,
) -> dict[str, Any]:
    frame = pd.read_parquet(instrument_master_path)
    candidates = frame.loc[
        (frame["ticker"] == ticker) & (frame["instrument_id"] == instrument_id)
    ].copy()
    if len(candidates) != 1:
        raise ValueError(
            f"Expected one identity row for {ticker}/{instrument_id}; found {len(candidates)}"
        )
    row = candidates.iloc[0].to_dict()
    valid_from = pd.Timestamp(row["valid_from"]).date()
    valid_to_raw = row.get("valid_to")
    valid_to = (
        pd.Timestamp(valid_to_raw).date()
        if valid_to_raw is not None and not pd.isna(valid_to_raw)
        else date.max
    )
    if valid_from > start or valid_to < end:
        raise ValueError("Identity row does not cover the complete pilot interval")
    return row


def load_foundation_evidence(
    shards_root: Path,
    *,
    ticker: str,
    selected_dates: set[date],
) -> pd.DataFrame:
    columns = [
        "file",
        "ticker",
        "date",
        "severity",
        "sample_stratum",
        "n_trades",
        "volume_total",
        "duplicate_exact_ratio_pct_raw",
        "max_trades_same_timestamp_raw",
        "negative_price_rows_raw",
        "negative_size_rows_raw",
        "missing_required_cols_count",
        "dtype_mismatches_count",
        "timestamp_out_of_partition_day",
        "acceptance_label",
    ]
    dataset = ds.dataset(str(shards_root), format="parquet")
    table = dataset.to_table(filter=ds.field("ticker") == ticker, columns=columns)
    frame = table.to_pandas()
    if frame.empty:
        return frame
    frame["session_date"] = pd.to_datetime(frame["date"]).dt.date
    frame = frame.loc[frame["session_date"].isin(selected_dates)].copy()
    if frame["session_date"].duplicated().any():
        duplicates = frame.loc[frame["session_date"].duplicated(), "session_date"].tolist()
        raise ValueError(f"Foundation evidence is not one-to-one: {duplicates[:5]}")
    return frame.drop(columns=["date"])


def filter_acquisition_records(
    records: Iterable[dict[str, Any]],
    *,
    ticker: str,
    selected_dates: set[date],
) -> list[dict[str, Any]]:
    """Bound an already indexed acquisition stream without scanning unrelated tasks."""
    selected: list[dict[str, Any]] = []
    for record in records:
        record_ticker = str(record.get("ticker", "")).upper()
        raw_date = record.get("date") or record.get("session_date")
        if not raw_date:
            continue
        record_date = pd.Timestamp(raw_date).date()
        if record_ticker == ticker.upper() and record_date in selected_dates:
            selected.append(dict(record, session_date=record_date))
    return selected


def build_dense_input_manifest(
    calendar: pd.DataFrame,
    *,
    raw_root: Path,
    ticker: str,
    instrument_id: str,
    foundation: pd.DataFrame,
    acquisition_records: Sequence[dict[str, Any]] = (),
) -> pd.DataFrame:
    foundation_by_date = (
        foundation.set_index("session_date").to_dict("index")
        if not foundation.empty
        else {}
    )
    acquisition_by_date = {
        pd.Timestamp(record["session_date"]).date(): record
        for record in acquisition_records
    }
    rows: list[dict[str, Any]] = []
    for calendar_row in calendar.to_dict("records"):
        session_date = calendar_row["session_date"]
        source_path = resolve_trade_path(raw_root, ticker, session_date)
        evidence = foundation_by_date.get(session_date, {})
        acquisition = acquisition_by_date.get(session_date)
        rows.append(
            {
                "instrument_id": instrument_id,
                "ticker": ticker,
                "session_date": session_date,
                "open_utc": calendar_row["open_utc"],
                "close_utc": calendar_row["close_utc"],
                "open_et": calendar_row["open_et"],
                "close_et": calendar_row["close_et"],
                "session_minutes": calendar_row["session_minutes"],
                "is_early_close": bool(calendar_row["is_early_close"]),
                "source_path": str(source_path),
                "source_exists": source_path.is_file(),
                "source_bytes": source_path.stat().st_size if source_path.is_file() else None,
                "source_sha256": sha256_file(source_path) if source_path.is_file() else None,
                "foundation_quality_label": evidence.get(
                    "acceptance_label", "NO_FOUNDATION_EVIDENCE"
                ),
                "foundation_severity": evidence.get("severity"),
                "foundation_n_trades": evidence.get("n_trades"),
                "foundation_duplicate_exact_ratio_pct_raw": evidence.get(
                    "duplicate_exact_ratio_pct_raw"
                ),
                "foundation_max_trades_same_timestamp_raw": evidence.get(
                    "max_trades_same_timestamp_raw"
                ),
                "foundation_missing_required_cols_count": evidence.get(
                    "missing_required_cols_count"
                ),
                "foundation_dtype_mismatches_count": evidence.get(
                    "dtype_mismatches_count"
                ),
                "foundation_timestamp_out_of_partition_day": evidence.get(
                    "timestamp_out_of_partition_day"
                ),
                "acquisition_evidence_state": (
                    "RESOLVED" if acquisition else "PENDING_BOUNDED_RESOLUTION"
                ),
                "acquisition_run_id": acquisition.get("run_id") if acquisition else None,
            }
        )
    return pd.DataFrame(rows)


def duplicate_key(row: dict[str, Any]) -> tuple[Any, ...]:
    conditions = row.get("conditions")
    if conditions is None or (isinstance(conditions, float) and math.isnan(conditions)):
        normalized_conditions: tuple[int, ...] = ()
    else:
        normalized_conditions = tuple(int(value) for value in conditions)
    return (
        normalize_utc(row["timestamp"]),
        float(row["price"]),
        int(row["size"]),
        row.get("exchange"),
        normalized_conditions,
    )


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
    for ordinal, row in enumerate(raw.to_dict("records")):
        event_time = normalize_utc(row["timestamp"])
        row_for_policy = dict(row)
        row_for_policy["timestamp"] = event_time
        exact_duplicate = duplicate_key(row_for_policy) in seen
        seen.add(duplicate_key(row_for_policy))
        in_rth = session_open < event_time < session_close
        result = evaluate_trade(
            row_for_policy,
            matrix,
            in_rth=in_rth,
            source_available=True,
            exact_duplicate_research_flag=exact_duplicate,
        )
        state = result["trade_activity_eligibility_state"]
        counters["eligible_trade_rows"] += state == "ELIGIBLE_WITH_RESTRICTIONS"
        counters["unknown_fail_closed_rows"] += state == "UNKNOWN_FAIL_CLOSED"
        counters["exact_duplicate_flag_rows"] += exact_duplicate
        events.append(
            {
                "legacy_event_time": event_time,
                "simulated_available_at": event_time + latency,
                "price": float(row["price"]) if pd.notna(row.get("price")) else None,
                "size": int(row["size"]) if pd.notna(row.get("size")) else None,
                "exchange": row.get("exchange"),
                "conditions": row.get("conditions"),
                "ordinal": ordinal,
                "eligibility_state": state,
                "eligibility_reason_codes": result["eligibility_reason_codes"],
                "duplicate_research_flag": result["duplicate_research_flag"],
                "quality_state": result["quality_state"],
            }
        )
    events.sort(key=lambda event: (event["legacy_event_time"], event["ordinal"]))
    return events, {key: int(value) for key, value in counters.items()}


def audit_session_variable_families(
    manifest_row: dict[str, Any], events: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    source_exists = bool(manifest_row["source_exists"])
    foundation_label = manifest_row["foundation_quality_label"]
    base_flags: list[str] = []
    if foundation_label not in {"GOOD", "NO_FOUNDATION_EVIDENCE"}:
        base_flags.append(f"FOUNDATION_LABEL_{foundation_label}")
    if manifest_row.get("foundation_dtype_mismatches_count") not in (None, 0, 0.0):
        base_flags.append("FOUNDATION_DTYPE_WARNING")
    if manifest_row.get("foundation_timestamp_out_of_partition_day") is True:
        base_flags.append("FOUNDATION_TIMESTAMP_PARTITION_WARNING")

    unknown_count = sum(
        event["eligibility_state"] == "UNKNOWN_FAIL_CLOSED" for event in events
    )
    ineligible_count = sum(event["eligibility_state"] == "INELIGIBLE" for event in events)
    eligible_count = sum(
        event["eligibility_state"] == "ELIGIBLE_WITH_RESTRICTIONS" for event in events
    )
    duplicate_count = sum(
        event["duplicate_research_flag"] == "EXACT_DUPLICATE_RESEARCH_FLAG"
        for event in events
    )
    rows: list[dict[str, Any]] = []
    for family in VARIABLE_FAMILIES:
        flags = list(base_flags)
        if unknown_count:
            flags.append("UNKNOWN_CONDITION_WINDOWS_DEGRADE")
        if ineligible_count:
            flags.append("INELIGIBLE_ROWS_EXCLUDED_BY_POLICY")
        if duplicate_count:
            flags.append("EXACT_DUPLICATES_PRESERVED_AND_FLAGGED")
        if not source_exists:
            disposition = "REPLACE_REQUIRED"
            flags.append("SOURCE_FILE_MISSING")
        elif manifest_row.get("foundation_missing_required_cols_count") not in (
            None,
            0,
            0.0,
        ):
            disposition = "DEGRADED"
            flags.append("FOUNDATION_MISSING_REQUIRED_COLUMNS")
        elif flags:
            disposition = "USABLE_WITH_FLAGS"
        else:
            disposition = "USABLE"
        rows.append(
            {
                "instrument_id": manifest_row["instrument_id"],
                "ticker": manifest_row["ticker"],
                "session_date": manifest_row["session_date"],
                "variable_family": family,
                "local_audit_disposition": disposition,
                "reason_codes": sorted(set(flags)),
                "source_trade_rows": len(events),
                "eligible_trade_rows": eligible_count,
                "unknown_fail_closed_rows": unknown_count,
                "ineligible_trade_rows": ineligible_count,
                "exact_duplicate_flag_rows": duplicate_count,
                "foundation_quality_label": foundation_label,
                "automatic_exclusion_applied": False,
            }
        )
    return rows


def coverage_gate_from_audit(audit_rows: Sequence[dict[str, Any]]) -> bool:
    return bool(audit_rows) and all(
        row["local_audit_disposition"] in {"USABLE", "USABLE_WITH_FLAGS"}
        for row in audit_rows
    )


@dataclass(frozen=True)
class EventIndex:
    events: tuple[dict[str, Any], ...]
    times: tuple[datetime, ...]

    @classmethod
    def build(cls, events: Iterable[dict[str, Any]]) -> EventIndex:
        ordered = sorted(events, key=lambda item: (item["legacy_event_time"], item["ordinal"]))
        return cls(tuple(ordered), tuple(item["legacy_event_time"] for item in ordered))

    def window(self, left: datetime, right: datetime) -> tuple[dict[str, Any], ...]:
        start = bisect.bisect_right(self.times, left)
        end = bisect.bisect_right(self.times, right)
        return self.events[start:end]


def iter_decision_timestamps(
    session_open: datetime,
    session_close: datetime,
    *,
    decision_seconds_limit: int | None = None,
) -> Iterator[datetime]:
    current = session_open + timedelta(seconds=1)
    final = session_close - timedelta(seconds=1)
    emitted = 0
    while current <= final:
        if decision_seconds_limit is not None and emitted >= decision_seconds_limit:
            break
        yield current
        current += timedelta(seconds=1)
        emitted += 1


def common_metadata(
    *,
    config: dict[str, Any],
    manifest_row: dict[str, Any],
    quality_state: str,
    coverage_state: str,
    local_window_disposition: str,
) -> dict[str, Any]:
    scope = config["scope"]
    binding = config["binding"]
    sources = config["sources"]
    return {
        "feature_spec_id": binding["feature_spec_id"],
        "feature_version": binding["feature_version"],
        "binding_id": binding["binding_id"],
        "scope_id": scope["scope_id"],
        "pilot_scope_id": scope["pilot_scope_id"],
        "instrument_id": manifest_row["instrument_id"],
        "ticker": manifest_row["ticker"],
        "session_date": manifest_row["session_date"],
        "trade_eligibility_policy_id": binding["trade_eligibility_policy_id"],
        "duplicate_policy_id": binding["duplicate_policy_id"],
        "latency_policy_id": binding["latency_policy_id"],
        "source_dataset_id": binding["source_dataset_id"],
        "source_schema_version": binding["source_schema_version"],
        "market_calendar_build_run_id": sources["calendar_build_run_id"],
        "instrument_master_build_run_id": sources["instrument_master_build_run_id"],
        "foundation_quality_label": manifest_row["foundation_quality_label"],
        "local_window_disposition": local_window_disposition,
        "quality_state": quality_state,
        "coverage_state": coverage_state,
        "coverage_mode": binding["coverage_mode"],
        "lineage_manifest_id": binding["lineage_manifest_id"],
        "future_window_used": False,
    }


def materialize_current_state(
    events: Sequence[dict[str, Any]],
    *,
    config: dict[str, Any],
    manifest_row: dict[str, Any],
    coverage_gate_pass: bool,
    decision_seconds_limit: int | None = None,
) -> pd.DataFrame:
    session_open = normalize_utc(manifest_row["open_utc"])
    session_close = normalize_utc(manifest_row["close_utc"])
    event_index = EventIndex.build(events)
    coverage_state = "OBSERVED_COMPLETE_REQUEST" if coverage_gate_pass else "DEGRADED"
    audit_disposition = "USABLE" if coverage_gate_pass else "DEGRADED"
    rows: list[dict[str, Any]] = []
    windows = tuple(int(value) for value in config["binding"]["windows_seconds"])
    for decision_timestamp in iter_decision_timestamps(
        session_open,
        session_close,
        decision_seconds_limit=decision_seconds_limit,
    ):
        for window_seconds in windows:
            left = decision_timestamp - timedelta(seconds=window_seconds)
            state = compute_window_state(
                event_index.window(left, decision_timestamp),
                decision_timestamp=decision_timestamp,
                session_open=session_open,
                window_seconds=window_seconds,
                coverage_gate_pass=coverage_gate_pass,
            )
            if state["observation_state"] == "DEGRADED":
                local_disposition = "DEGRADED_BY_WINDOW_EVIDENCE"
                quality_state = "DEGRADED"
            else:
                local_disposition = audit_disposition
                quality_state = "OBSERVED"
            rows.append(
                {
                    **common_metadata(
                        config=config,
                        manifest_row=manifest_row,
                        quality_state=quality_state,
                        coverage_state=coverage_state,
                        local_window_disposition=local_disposition,
                    ),
                    **state,
                }
            )
    return _stabilize_current_state(pd.DataFrame(rows))


def materialize_multiscale_contrast(
    current: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> pd.DataFrame:
    if current.empty:
        return pd.DataFrame()
    index = {
        (row.decision_timestamp, int(row.window_seconds)): row._asdict()
        for row in current.itertuples(index=False)
    }
    pairs = [tuple(int(value) for value in pair) for pair in config["binding"]["short_long_pairs_seconds"]]
    rows: list[dict[str, Any]] = []
    timestamps = sorted(current["decision_timestamp"].drop_duplicates())
    base_columns = [
        "feature_spec_id",
        "feature_version",
        "binding_id",
        "scope_id",
        "pilot_scope_id",
        "instrument_id",
        "ticker",
        "session_date",
        "trade_eligibility_policy_id",
        "duplicate_policy_id",
        "latency_policy_id",
        "source_dataset_id",
        "source_schema_version",
        "market_calendar_build_run_id",
        "instrument_master_build_run_id",
        "foundation_quality_label",
        "lineage_manifest_id",
        "future_window_used",
        "coverage_mode",
    ]
    for timestamp in timestamps:
        for short_seconds, long_seconds in pairs:
            short = index[(timestamp, short_seconds)]
            long = index[(timestamp, long_seconds)]
            ratio = compute_multiscale_log_ratio(short, long)
            calculation_state = (
                "CALCULATED" if ratio is not None else "INPUT_NOT_CALCULATED"
            )
            rows.append(
                {
                    **{column: long[column] for column in base_columns},
                    "decision_timestamp": timestamp,
                    "pair_id": f"W{short_seconds}_W{long_seconds}",
                    "short_window_seconds": short_seconds,
                    "long_window_seconds": long_seconds,
                    "activity_rate_multiscale_log_ratio": ratio,
                    "calculation_state": calculation_state,
                    "quality_state": (
                        "OBSERVED" if calculation_state == "CALCULATED" else "DEGRADED"
                    ),
                    "coverage_state": long["coverage_state"],
                    "local_window_disposition": long["local_window_disposition"],
                    "feature_input_max_available_at": max(
                        value
                        for value in (
                            short.get("feature_input_max_available_at"),
                            long.get("feature_input_max_available_at"),
                        )
                        if value is not None and not pd.isna(value)
                    )
                    if any(
                        value is not None and not pd.isna(value)
                        for value in (
                            short.get("feature_input_max_available_at"),
                            long.get("feature_input_max_available_at"),
                        )
                    )
                    else None,
                }
            )
    frame = pd.DataFrame(rows)
    _typed_numeric(
        frame,
        ("short_window_seconds", "long_window_seconds"),
        "Int64",
    )
    _typed_numeric(frame, ("activity_rate_multiscale_log_ratio",), "Float64")
    _typed_utc(frame, ("decision_timestamp", "feature_input_max_available_at"))
    frame["future_window_used"] = frame["future_window_used"].astype("boolean")
    return frame


def _baseline_cache_entry(
    reference: pd.DataFrame,
    *,
    baseline_candidate_id: str,
) -> dict[str, Any]:
    lookback = BASELINE_LOOKBACKS[baseline_candidate_id]
    minimum = BASELINE_MIN_SESSIONS[baseline_candidate_id]
    dates = sorted(pd.to_datetime(reference["session_date"]).dt.date.unique())
    selected_dates = dates[-lookback:]
    selected = reference.loc[
        pd.to_datetime(reference["session_date"]).dt.date.isin(selected_dates)
        & (reference["calculation_state"] == "CALCULATED")
    ].copy()
    base = {
        "baseline_candidate_id": baseline_candidate_id,
        "reference_session_count": len(selected_dates),
        "reference_observation_count": len(selected),
        "first_reference_date": min(selected_dates) if selected_dates else None,
        "last_reference_date": max(selected_dates) if selected_dates else None,
        "baseline_input_max_available_at": selected[
            "feature_input_max_available_at"
        ].dropna().max()
        if not selected.empty
        else None,
        "baseline_duration_calculation_state": "BASELINE_INSUFFICIENT_HISTORY",
        "baseline_median_intertrade_duration_us": None,
    }
    if len(selected_dates) < minimum or len(selected) < minimum:
        return {**base, "baseline_calculation_state": "BASELINE_INSUFFICIENT_HISTORY"}

    fields = {
        "trade_count": "eligible_trade_count",
        "share_volume": "eligible_share_volume",
        "dollar_volume": "eligible_dollar_volume",
        "arrival_rate": "trade_arrival_rate",
    }
    distributions: dict[str, dict[str, Any]] = {}
    sorted_values: dict[str, list[float]] = {}
    for label, field in fields.items():
        values = [float(value) for value in selected[field].dropna().tolist()]
        if len(values) < minimum:
            return {**base, "baseline_calculation_state": "BASELINE_INSUFFICIENT_HISTORY"}
        distributions[label] = _distribution_summary(values)
        sorted_values[label] = sorted(values)
    zero_dominated = distributions["trade_count"]["zero_fraction"] >= 0.80
    duration_values = [
        float(value)
        for value in selected["median_intertrade_duration_us"].dropna().tolist()
    ]
    duration_available = len(duration_values) >= minimum
    return {
        **base,
        "baseline_calculation_state": (
            "BASELINE_ZERO_DOMINATED" if zero_dominated else "BASELINE_AVAILABLE"
        ),
        "baseline_zero_dominated": zero_dominated,
        "baseline_duration_calculation_state": (
            "BASELINE_AVAILABLE"
            if duration_available
            else "BASELINE_INSUFFICIENT_HISTORY"
        ),
        "baseline_median_intertrade_duration_us": (
            float(pd.Series(duration_values).median()) if duration_available else None
        ),
        "distributions": distributions,
        "sorted_values": sorted_values,
    }


def build_baseline_cache(
    prior_current: pd.DataFrame,
    *,
    evaluation_session_date: date,
    baseline_candidates: Sequence[str],
) -> dict[tuple[str, int, str], dict[str, Any]]:
    prior = prior_current.loc[
        pd.to_datetime(prior_current["session_date"]).dt.date < evaluation_session_date
    ].copy()
    timestamps_et = pd.to_datetime(prior["decision_timestamp"], utc=True).dt.tz_convert(
        "America/New_York"
    )
    prior["clock_minute_et"] = timestamps_et.dt.strftime("%H:%M")
    cache: dict[tuple[str, int, str], dict[str, Any]] = {}
    for (clock_minute, window_seconds), group in prior.groupby(
        ["clock_minute_et", "window_seconds"], sort=False
    ):
        for baseline_candidate in baseline_candidates:
            cache[(str(clock_minute), int(window_seconds), baseline_candidate)] = (
                _baseline_cache_entry(
                    group,
                    baseline_candidate_id=baseline_candidate,
                )
            )
    return cache


def _flatten_distribution(
    output: dict[str, Any], label: str, summary: dict[str, Any]
) -> None:
    for field, value in summary.items():
        output[f"baseline_{label}_{field}"] = value


def materialize_baseline_and_surprise(
    current: pd.DataFrame,
    *,
    prior_current: pd.DataFrame,
    config: dict[str, Any],
    evaluation_session_date: date,
) -> pd.DataFrame:
    candidates = list(config["binding"]["baseline_candidates"])
    cache = build_baseline_cache(
        prior_current,
        evaluation_session_date=evaluation_session_date,
        baseline_candidates=candidates,
    )
    fields = {
        "trade_count": "eligible_trade_count",
        "share_volume": "eligible_share_volume",
        "dollar_volume": "eligible_dollar_volume",
        "arrival_rate": "trade_arrival_rate",
    }
    rows: list[dict[str, Any]] = []
    for state in current.to_dict("records"):
        clock_minute = pd.Timestamp(state["decision_timestamp"]).tz_convert(
            "America/New_York"
        ).strftime("%H:%M")
        for candidate in candidates:
            entry = cache.get(
                (clock_minute, int(state["window_seconds"]), candidate),
                {
                    "baseline_candidate_id": candidate,
                    "reference_session_count": 0,
                    "reference_observation_count": 0,
                    "first_reference_date": None,
                    "last_reference_date": None,
                    "baseline_input_max_available_at": None,
                    "baseline_calculation_state": "BASELINE_INSUFFICIENT_HISTORY",
                },
            )
            output = {
                key: state[key]
                for key in (
                    "feature_spec_id",
                    "feature_version",
                    "binding_id",
                    "scope_id",
                    "pilot_scope_id",
                    "instrument_id",
                    "ticker",
                    "session_date",
                    "decision_timestamp",
                    "window_seconds",
                    "subwindow_seconds",
                    "trade_eligibility_policy_id",
                    "duplicate_policy_id",
                    "latency_policy_id",
                    "source_dataset_id",
                    "source_schema_version",
                    "market_calendar_build_run_id",
                    "instrument_master_build_run_id",
                    "foundation_quality_label",
                    "local_window_disposition",
                    "quality_state",
                    "coverage_state",
                    "coverage_mode",
                    "calculation_state",
                    "feature_input_max_available_at",
                    "lineage_manifest_id",
                    "future_window_used",
                )
            }
            output.update(
                {
                    key: value
                    for key, value in entry.items()
                    if key not in {"distributions", "sorted_values"}
                }
            )
            for column in BASELINE_VALUE_COLUMNS:
                output.setdefault(column, None)
            output.setdefault("baseline_zero_dominated", None)
            output.setdefault(
                "baseline_duration_calculation_state",
                "BASELINE_INSUFFICIENT_HISTORY",
            )
            if entry["baseline_calculation_state"] in {
                "BASELINE_AVAILABLE",
                "BASELINE_ZERO_DOMINATED",
            }:
                for label, summary in entry["distributions"].items():
                    _flatten_distribution(output, label, summary)
                    current_value = state.get(fields[label])
                    values = entry["sorted_values"][label]
                    output[f"{label}_percentile_pit"] = (
                        bisect.bisect_right(values, float(current_value)) / len(values)
                        if current_value is not None and not pd.isna(current_value)
                        else None
                    )
                output["trade_count_log_ratio_to_pit"] = math.log(
                    (float(state["eligible_trade_count"]) + 1)
                    / (entry["distributions"]["trade_count"]["unconditional_median"] + 1)
                ) if state.get("eligible_trade_count") is not None else None
                output["share_volume_log_ratio_to_pit"] = math.log(
                    (float(state["eligible_share_volume"]) + 1)
                    / (entry["distributions"]["share_volume"]["unconditional_median"] + 1)
                ) if state.get("eligible_share_volume") is not None else None
                output["dollar_volume_log_ratio_to_pit"] = math.log(
                    (float(state["eligible_dollar_volume"]) + 1)
                    / (entry["distributions"]["dollar_volume"]["unconditional_median"] + 1)
                ) if state.get("eligible_dollar_volume") is not None else None
                current_duration = state.get("median_intertrade_duration_us")
                baseline_duration = entry.get(
                    "baseline_median_intertrade_duration_us"
                )
                if (
                    current_duration is not None
                    and not pd.isna(current_duration)
                    and baseline_duration is not None
                    and not pd.isna(baseline_duration)
                ):
                    output["intertrade_duration_compression"] = math.log(
                        (float(baseline_duration) + 1.0)
                        / (float(current_duration) + 1.0)
                    )
            rows.append(output)
    frame = pd.DataFrame(rows)
    for column in BASELINE_VALUE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Float64")
    frame["baseline_zero_dominated"] = frame["baseline_zero_dominated"].astype(
        "boolean"
    )
    _typed_numeric(
        frame,
        ("window_seconds", "subwindow_seconds", "reference_session_count", "reference_observation_count"),
        "Int64",
    )
    _typed_utc(
        frame,
        (
            "decision_timestamp",
            "feature_input_max_available_at",
            "baseline_input_max_available_at",
        ),
    )
    frame["future_window_used"] = frame["future_window_used"].astype("boolean")
    leading_columns = [
        column for column in frame.columns if column not in BASELINE_RESULT_COLUMNS
    ]
    return frame.reindex(columns=leading_columns + list(BASELINE_RESULT_COLUMNS))


def expected_row_counts(calendar: pd.DataFrame, evaluation_dates: set[date]) -> dict[str, int]:
    decision_seconds = {
        row.session_date: int((normalize_utc(row.close_utc) - normalize_utc(row.open_utc)).total_seconds()) - 1
        for row in calendar.itertuples(index=False)
    }
    total_decisions = sum(decision_seconds.values())
    evaluation_decisions = sum(
        seconds for session_date, seconds in decision_seconds.items() if session_date in evaluation_dates
    )
    return {
        "decision_seconds_total": total_decisions,
        "current_state_rows": total_decisions * len(WINDOW_SECONDS),
        "multiscale_rows": total_decisions * len(SHORT_LONG_PAIRS),
        "baseline_rows": evaluation_decisions * len(WINDOW_SECONDS) * len(BASELINE_LOOKBACKS),
    }


def _values_equal(left: Any, right: Any, tolerance: float) -> bool:
    if left is None or (isinstance(left, float) and math.isnan(left)):
        return right is None or (isinstance(right, float) and math.isnan(right))
    if isinstance(left, float) or isinstance(right, float):
        return math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance)
    return left == right


def validate_event_index_equivalence(
    events: Sequence[dict[str, Any]],
    *,
    session_open: datetime,
    session_close: datetime,
    coverage_gate_pass: bool,
    seed: int,
    random_sample_count: int,
) -> dict[str, Any]:
    index = EventIndex.build(events)
    samples: set[tuple[datetime, int]] = set()
    for window in WINDOW_SECONDS:
        for timestamp in (
            session_open + timedelta(seconds=1),
            session_open + timedelta(seconds=window),
            min(session_open + timedelta(seconds=window + 1), session_close - timedelta(seconds=1)),
            session_close - timedelta(seconds=1),
        ):
            if session_open < timestamp < session_close:
                samples.add((timestamp, window))
    for event in events[:100]:
        for delta in (-1, 0, 1):
            timestamp = event["legacy_event_time"] + timedelta(seconds=delta)
            if session_open < timestamp < session_close:
                samples.add((timestamp, 60))
    rng = random.Random(seed)
    span = int((session_close - session_open).total_seconds()) - 1
    for _ in range(random_sample_count):
        samples.add(
            (
                session_open + timedelta(seconds=rng.randint(1, max(1, span))),
                rng.choice(WINDOW_SECONDS),
            )
        )

    mismatches: list[dict[str, Any]] = []
    fields: set[str] = set()
    for decision_timestamp, window_seconds in sorted(samples):
        left = decision_timestamp - timedelta(seconds=window_seconds)
        oracle = compute_window_state(
            events,
            decision_timestamp=decision_timestamp,
            session_open=session_open,
            window_seconds=window_seconds,
            coverage_gate_pass=coverage_gate_pass,
        )
        optimized = compute_window_state(
            index.window(left, decision_timestamp),
            decision_timestamp=decision_timestamp,
            session_open=session_open,
            window_seconds=window_seconds,
            coverage_gate_pass=coverage_gate_pass,
        )
        fields.update(oracle)
        for field in oracle:
            if not _values_equal(
                oracle[field], optimized.get(field), FLOAT_COMPARISON_TOLERANCE
            ):
                mismatches.append(
                    {
                        "decision_timestamp": decision_timestamp,
                        "window_seconds": window_seconds,
                        "field": field,
                        "oracle": oracle[field],
                        "optimized": optimized.get(field),
                    }
                )
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "sample_count": len(samples),
        "fields_compared": sorted(fields),
        "float_tolerance": FLOAT_COMPARISON_TOLERANCE,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:100],
    }








