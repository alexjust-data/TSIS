from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from trading_activity_binding_a_multisession_engine import (  # noqa: E402
    EventIndex,
    atomic_write_parquet,
    audit_session_variable_families,
    build_dense_input_manifest,
    coverage_gate_from_audit,
    expected_row_counts,
    filter_acquisition_records,
    validate_event_index_equivalence,
)
from trading_activity_binding_a_multisession_runtime import (  # noqa: E402
    load_acquisition_evidence_bounded,
    load_and_evaluate_events,
)

UTC = UTC
OPEN = datetime(2025, 1, 2, 14, 30, tzinfo=UTC)


def _event(
    seconds: float,
    *,
    available_seconds: float | None = None,
    state: str = "ELIGIBLE_WITH_RESTRICTIONS",
    ordinal: int = 0,
):
    return {
        "legacy_event_time": OPEN + timedelta(seconds=seconds),
        "simulated_available_at": OPEN
        + timedelta(seconds=available_seconds if available_seconds is not None else seconds),
        "price": 2.0,
        "size": 100,
        "ordinal": ordinal,
        "eligibility_state": state,
    }


def _calendar_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "session_date": date(2025, 1, 2),
                "open_utc": OPEN,
                "close_utc": OPEN + timedelta(seconds=11),
                "open_et": OPEN,
                "close_et": OPEN + timedelta(seconds=11),
                "session_minutes": 11 / 60,
                "is_early_close": False,
            },
            {
                "session_date": date(2025, 1, 3),
                "open_utc": OPEN + timedelta(days=1),
                "close_utc": OPEN + timedelta(days=1, seconds=7),
                "open_et": OPEN + timedelta(days=1),
                "close_et": OPEN + timedelta(days=1, seconds=7),
                "session_minutes": 7 / 60,
                "is_early_close": True,
            },
        ]
    )


def test_event_index_window_and_oracle_equivalence():
    events = [
        _event(1, ordinal=1),
        _event(3, available_seconds=5, ordinal=2),
        _event(3, available_seconds=8, ordinal=3),
        _event(7, state="UNKNOWN_FAIL_CLOSED", ordinal=4),
    ]
    index = EventIndex.build(events)
    assert [event["ordinal"] for event in index.window(OPEN, OPEN + timedelta(seconds=3))] == [1, 2, 3]
    result = validate_event_index_equivalence(
        events,
        session_open=OPEN,
        session_close=OPEN + timedelta(seconds=20),
        coverage_gate_pass=True,
        seed=7,
        random_sample_count=20,
    )
    assert result["status"] == "PASS"
    assert result["mismatch_count"] == 0


def test_future_available_unknown_event_does_not_degrade_early():
    from trading_activity_binding_a_kernel import compute_window_state

    result = compute_window_state(
        [_event(2, available_seconds=10, state="UNKNOWN_FAIL_CLOSED")],
        decision_timestamp=OPEN + timedelta(seconds=5),
        session_open=OPEN,
        window_seconds=5,
        coverage_gate_pass=True,
    )
    assert result["observation_state"] == "OBSERVED_ZERO"
    assert result["calculation_state"] == "CALCULATED"


def test_expected_row_counts_include_normal_and_early_close():
    result = expected_row_counts(_calendar_frame(), {date(2025, 1, 3)})
    assert result == {
        "decision_seconds_total": 16,
        "current_state_rows": 80,
        "multiscale_rows": 32,
        "baseline_rows": 90,
    }


def test_foundation_label_is_metadata_and_never_automatic_exclusion(tmp_path: Path):
    calendar = _calendar_frame().head(1)
    raw_root = tmp_path / "raw"
    source = (
        raw_root
        / "TST"
        / "year=2025"
        / "month=01"
        / "day=2025-01-02"
        / "market.parquet"
    )
    source.parent.mkdir(parents=True)
    pd.DataFrame({"x": [1]}).to_parquet(source)
    foundation = pd.DataFrame(
        [
            {
                "session_date": date(2025, 1, 2),
                "acceptance_label": "BAD",
                "severity": "REVIEW_NOT_REHABILITATED",
                "n_trades": 1,
                "duplicate_exact_ratio_pct_raw": 0.0,
                "max_trades_same_timestamp_raw": 1,
                "missing_required_cols_count": 0,
                "dtype_mismatches_count": 0,
                "timestamp_out_of_partition_day": False,
            }
        ]
    )
    dense = build_dense_input_manifest(
        calendar,
        raw_root=raw_root,
        ticker="TST",
        instrument_id="fixture:TST",
        foundation=foundation,
    )
    events = [
        {
            **_event(1),
            "duplicate_research_flag": "NO_EXACT_DUPLICATE_FLAG",
        }
    ]
    rows = audit_session_variable_families(dense.iloc[0].to_dict(), events)
    assert len(rows) == 4
    assert all(row["automatic_exclusion_applied"] is False for row in rows)
    assert all(row["local_audit_disposition"] == "USABLE_WITH_FLAGS" for row in rows)
    assert coverage_gate_from_audit(rows) is True


def test_filter_acquisition_records_is_ticker_date_bounded():
    records = [
        {"ticker": "TST", "date": "2025-01-02", "status": "DOWNLOADED_OK"},
        {"ticker": "TST", "date": "2025-01-04", "status": "DOWNLOADED_OK"},
        {"ticker": "ZZZ", "date": "2025-01-02", "status": "DOWNLOADED_OK"},
    ]
    selected = filter_acquisition_records(
        records, ticker="TST", selected_dates={date(2025, 1, 2)}
    )
    assert len(selected) == 1
    assert selected[0]["session_date"] == date(2025, 1, 2)


def test_bounded_acquisition_reader_stops_at_end_of_ticker_group(tmp_path: Path):
    run = tmp_path / "run_01"
    run.mkdir()
    columns = ["task_key", "ticker", "date", "session", "expected_file"]
    expected = [
        ["AAA|2025-01-02|market", "AAA", "2025-01-02", "market", "a"],
        ["TST|2025-01-02|market", "TST", "2025-01-02", "market", "t"],
        ["ZZZ|2025-01-02|market", "ZZZ", "2025-01-02", "market", "z"],
    ]
    with (run / "expected_manifest_trades_ticks.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(expected)
    event_columns = columns[:-1] + [
        "status",
        "rows",
        "file",
        "elapsed_sec",
        "processed_at_utc",
        "error",
    ]
    with (run / "download_events_trades_ticks_current.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(event_columns)
        writer.writerow(
            [
                "TST|2025-01-02|market",
                "TST",
                "2025-01-02",
                "market",
                "DOWNLOADED_OK",
                2,
                "t",
                0.1,
                "2025-01-02T00:00:00Z",
                "",
            ]
        )
    resolved = load_acquisition_evidence_bounded(
        tmp_path, ticker="TST", selected_dates={date(2025, 1, 2)}
    )
    assert len(resolved) == 1
    assert resolved[0]["status"] == "DOWNLOADED_OK"


def test_exact_duplicate_is_preserved_and_flagged(tmp_path: Path):
    source = tmp_path / "market.parquet"
    timestamp = datetime(2025, 1, 2, 14, 30, 2)
    frame = pd.DataFrame(
        {
            "ticker": ["TST", "TST"],
            "date": ["2025-01-02", "2025-01-02"],
            "timestamp": [timestamp, timestamp],
            "price": [2.0, 2.0],
            "size": [100, 100],
            "exchange": [11, 11],
            "conditions": [[], []],
        }
    )
    frame.to_parquet(source)
    events, counters = load_and_evaluate_events(
        source,
        matrix={},
        session_open=OPEN,
        session_close=OPEN + timedelta(seconds=20),
        simulated_latency_ms=1000,
    )
    assert len(events) == 2
    assert counters["exact_duplicate_flag_rows"] == 1
    assert events[1]["duplicate_research_flag"] == "EXACT_DUPLICATE_RESEARCH_FLAG"


def test_atomic_partition_write_and_hash_validated_resume(tmp_path: Path):
    path = tmp_path / "part.parquet"
    frame = pd.DataFrame({"a": [1, 2]})
    first = atomic_write_parquet(frame, path)
    resumed = atomic_write_parquet(frame, path, allow_existing_valid=True)
    assert first["resumed"] is False
    assert resumed["resumed"] is True
    assert first["sha256"] == resumed["sha256"]
    path.write_bytes(path.read_bytes() + b"corruption")
    try:
        atomic_write_parquet(frame, path, allow_existing_valid=True)
    except ValueError as exc:
        assert "hash mismatch" in str(exc)
    else:
        raise AssertionError("Corrupt resumable partition was accepted")


def test_monitor_derives_stale_no_process(tmp_path: Path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "pid_manifest.json").write_text(
        json.dumps({"pid": 99999999}), encoding="utf-8"
    )
    (runtime / "heartbeat_latest.json").write_text(
        json.dumps(
            {
                "timestamp_utc": "2000-01-01T00:00:00Z",
                "status": "RUNNING",
                "stage": "STAGE_5",
                "counters": {},
            }
        ),
        encoding="utf-8",
    )
    monitor = SCRIPTS / "monitor_trading_activity_binding_a_multisession_pilot.ps1"
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-File",
            str(monitor),
            "-RuntimeRoot",
            str(runtime),
            "-Compact",
            "-Once",
            "-StaleAfterSeconds",
            "1",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 3
    assert "status=STALE_NO_PROCESS" in result.stdout

def _baseline_state_row(session_date: date, duration_us: float | None) -> dict:
    timestamp = pd.Timestamp(datetime.combine(session_date, datetime.min.time(), tzinfo=UTC)) + pd.Timedelta(hours=14, minutes=30)
    return {
        "feature_spec_id": "trading_activity_binding_a_exact_specification",
        "feature_version": "v0_2",
        "binding_id": "trading_activity_binding_a_candidate_v0_2",
        "scope_id": "fixture_rth",
        "pilot_scope_id": "fixture",
        "instrument_id": "fixture:TST",
        "ticker": "TST",
        "session_date": session_date,
        "decision_timestamp": timestamp,
        "window_seconds": 5,
        "subwindow_seconds": 1,
        "trade_eligibility_policy_id": "fixture_policy",
        "duplicate_policy_id": "PRESERVE_EXACT_DUPLICATES_PRIMARY_V0_1",
        "latency_policy_id": "FIXTURE_1000MS",
        "source_dataset_id": "fixture_raw",
        "source_schema_version": "fixture_v0_1",
        "market_calendar_build_run_id": "fixture_calendar",
        "instrument_master_build_run_id": "fixture_identity",
        "foundation_quality_label": "GOOD",
        "local_window_disposition": "USABLE",
        "quality_state": "OBSERVED",
        "coverage_state": "OBSERVED_COMPLETE_REQUEST",
        "coverage_mode": "INFERRED_FROM_SUCCESSFUL_FULL_RTH_REQUEST",
        "calculation_state": "CALCULATED",
        "feature_input_max_available_at": timestamp,
        "lineage_manifest_id": "fixture_lineage_v0_2",
        "future_window_used": False,
        "eligible_trade_count": 10,
        "eligible_share_volume": 1000,
        "eligible_dollar_volume": 2000.0,
        "trade_arrival_rate": 2.0,
        "median_intertrade_duration_us": duration_us,
    }


def test_duration_compression_and_insufficient_history_keep_identical_schema():
    from trading_activity_binding_a_multisession_engine import materialize_baseline_and_surprise

    evaluation_date = date(2025, 2, 3)
    current = pd.DataFrame([_baseline_state_row(evaluation_date, 500.0)])
    prior = pd.DataFrame(
        [
            _baseline_state_row(date(2025, 1, day), 1000.0)
            for day in range(1, 16)
        ]
    )
    config = {"binding": {"baseline_candidates": ["B20"]}}

    available = materialize_baseline_and_surprise(
        current,
        prior_current=prior,
        config=config,
        evaluation_session_date=evaluation_date,
    )
    insufficient = materialize_baseline_and_surprise(
        current,
        prior_current=prior.head(14),
        config=config,
        evaluation_session_date=evaluation_date,
    )

    assert list(available.columns) == list(insufficient.columns)
    assert available.loc[0, "baseline_duration_calculation_state"] == "BASELINE_AVAILABLE"
    assert available.loc[0, "baseline_median_intertrade_duration_us"] == 1000.0
    assert available.loc[0, "intertrade_duration_compression"] == pytest.approx(
        math.log(1001.0 / 501.0)
    )
    assert insufficient.loc[0, "baseline_calculation_state"] == "BASELINE_INSUFFICIENT_HISTORY"
    assert pd.isna(insufficient.loc[0, "intertrade_duration_compression"])
    assert str(insufficient["intertrade_duration_compression"].dtype) == "Float64"


