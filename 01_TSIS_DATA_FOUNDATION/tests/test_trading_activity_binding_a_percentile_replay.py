from __future__ import annotations

import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "trading_activity_binding_a_percentile_replay_oracle.py"
SPEC = importlib.util.spec_from_file_location("percentile_replay_oracle", MODULE_PATH)
assert SPEC and SPEC.loader
oracle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = oracle
SPEC.loader.exec_module(oracle)


def test_empirical_percentile_is_right_inclusive_without_midrank() -> None:
    reference = np.asarray([0.0, 1.0, 1.0, 4.0])
    actual = oracle.empirical_percentile(reference, np.asarray([1.0, 2.0, np.nan]))
    assert actual[0] == 0.75
    assert actual[1] == 0.75
    assert np.isnan(actual[2])


def test_reference_dates_are_causal_group_local_and_tail_bounded() -> None:
    dates = np.asarray([1, 2, 3, 30, 31, 32, 33], dtype=np.int32)
    assert oracle.select_reference_dates(dates, 32, "B20").tolist() == [1, 2, 3, 30, 31]
    long = np.arange(1, 151, dtype=np.int32)
    selected = oracle.select_reference_dates(long, 140, "B120")
    assert selected[0] == 20
    assert selected[-1] == 139
    assert 140 not in selected and 150 not in selected


def test_oracle_does_not_import_production_baseline_engines() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    prohibited = (
        "trading_activity_binding_a_multisession_engine",
        "trading_activity_binding_a_baseline_vectorized",
        "trading_activity_binding_a_baseline_cpp",
        "tsis_baseline_native_cpp",
    )
    assert all(name not in source for name in prohibited)


def test_complete_session_replay_matches_manual_right_inclusive_fixture(tmp_path: Path) -> None:
    epoch = date(1970, 1, 1)
    target_date = date(2024, 2, 1)
    target_day = (target_date - epoch).days
    history_dates = np.repeat(np.arange(target_day - 20, target_day, dtype=np.int32), 2)
    history_values = np.tile(np.arange(1.0, 21.0), 2).reshape(2, 20).T.reshape(-1)
    order = np.argsort(history_dates, kind="stable")
    history_values = history_values[order]
    group_code = 570005
    history = oracle.HistoryMatrix(
        group_code=np.full(40, group_code, dtype=np.int32),
        session_day=history_dates,
        calculated=np.ones(40, dtype=bool),
        values={label: history_values.copy() for label in oracle.VALUE_COLUMNS},
        group_bounds={group_code: (0, 40)},
        row_count=40,
        source_partition_count=20,
    )
    timestamps = pd.to_datetime(["2024-02-01T14:30:01Z", "2024-02-01T14:30:02Z"])
    current_values = [10.0, 20.0]
    current = pd.DataFrame({
        "session_date": [target_date, target_date],
        "decision_timestamp": timestamps,
        "window_seconds": [5, 5],
        "calculation_state": ["CALCULATED", "CALCULATED"],
        "eligible_trade_count": current_values,
        "eligible_share_volume": current_values,
        "eligible_dollar_volume": current_values,
        "trade_arrival_rate": current_values,
    })
    current_path = tmp_path / "current.parquet"
    current.to_parquet(current_path, index=False)

    rows = []
    first_date = target_date - timedelta(days=20)
    last_date = target_date - timedelta(days=1)
    for row_index, timestamp in enumerate(timestamps):
        for candidate in oracle.CANDIDATES:
            available = candidate == "B20"
            row = {
                "decision_timestamp": timestamp,
                "window_seconds": 5,
                "baseline_candidate_id": candidate,
                "reference_session_count": 20,
                "reference_observation_count": 40,
                "first_reference_date": first_date,
                "last_reference_date": last_date,
                "baseline_calculation_state": "BASELINE_AVAILABLE" if available else "BASELINE_INSUFFICIENT_HISTORY",
                "baseline_zero_dominated": False if available else None,
            }
            for label in oracle.VALUE_COLUMNS:
                row[oracle.TOTAL_COUNT_COLUMNS[label]] = 40.0 if available else None
                row[oracle.PERCENTILE_COLUMNS[label]] = (0.5 if row_index == 0 else 1.0) if available else None
            rows.append(row)
    baseline_path = tmp_path / "baseline.parquet"
    pd.DataFrame(rows).to_parquet(baseline_path, index=False)
    result = oracle.audit_target_session(
        history, current_path=current_path, baseline_path=baseline_path
    )
    assert result["status"] == "PASS"
    assert result["mismatch_count"] == 0
    assert result["percentile_cells_checked"] == 24
