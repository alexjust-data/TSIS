from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_intraday_1m_event_outcomes_candidate as builder  # noqa: E402


def _write_event_state(root: Path) -> Path:
    path = root / "event_state.parquet"
    rows = []
    for role, window_id, decision_ts, close, market_state_id in [
        ("at_event", "window_anchor", "2025-01-06T15:01:00Z", 10.0, "market_anchor"),
        ("post_event_review", "window_post", "2025-01-06T15:04:00Z", 11.0, "market_post"),
    ]:
        rows.append(
            {
                "event_state_id": f"event_state_{role}",
                "event_id": "event_aaa",
                "event_window_id": window_id,
                "market_state_id": market_state_id,
                "instrument_id": "ticker:AAA",
                "ticker": "AAA",
                "event_family": "intraday_first_motion_threshold_cross_candidate",
                "event_timestamp_utc": "2025-01-06T15:00:00Z",
                "decision_timestamp_utc": decision_ts,
                "decision_date": "2025-01-06",
                "state_role": role,
                "state_quality_state": "event_state_review_scoped_intraday_component",
                "event_window_start_utc": "2025-01-06T15:00:00Z" if role == "at_event" else "2025-01-06T15:01:00Z",
                "event_window_end_utc": "2025-01-06T15:01:00Z" if role == "at_event" else "2025-01-06T15:04:00Z",
                "event_source_dataset_id": "intraday_1m_strategy_candidate_events_table_v0_1",
                "event_source_quality_state": "usable_candidate",
                "full_universe_claim": False,
                "execution_truth": False,
                "build_run_id": "event_state_fixture_run",
                "intraday__last_closed_bar_close": close,
                "intraday__price_view": "1m_quote_guarded_raw",
            }
        )
    pd.DataFrame(rows).to_parquet(path, index=False)
    return path


def _write_event_windows(root: Path) -> Path:
    path = root / "event_windows.parquet"
    pd.DataFrame(
        [
            {
                "event_window_id": "window_post",
                "source_event_id": "event_aaa",
                "event_source_dataset_id": "intraday_1m_strategy_candidate_events_table_v0_1",
                "event_family": "intraday_first_motion_threshold_cross_candidate",
                "event_type": "first_motion_threshold_cross",
                "event_code": "intraday_1m_first_session_open_move_pct_ge_50_candidate_v0_1",
                "event_source": "fixture",
                "ticker": "AAA",
                "instrument_id": "ticker:AAA",
                "session_date": "2025-01-06",
                "event_time_utc": "2025-01-06T15:00:00Z",
                "window_role": "post_event_30m",
                "window_start_utc": "2025-01-06T15:01:00Z",
                "window_end_utc": "2025-01-06T15:04:00Z",
                "window_duration_minutes": 3,
                "contains_post_event_information": True,
                "valid_for_outcome_window_candidate": True,
                "full_universe_claim": False,
                "schema_version": "event_windows_table_v0_1_candidate_intraday_1m_strategy_events",
                "quality_policy_version": "event_windows_policy",
                "build_run_id": "event_windows_fixture_run",
            }
        ]
    ).to_parquet(path, index=False)
    return path


def _write_master_intraday(root: Path) -> Path:
    path = root / "master_intraday.parquet"
    rows = [
        ("2025-01-06T15:01:00Z", 10.0, 10.5, 9.5, 10.2, 1000.0, 10.1, 10),
        ("2025-01-06T15:02:00Z", 10.2, 12.0, 10.1, 11.5, 2000.0, 11.2, 20),
        ("2025-01-06T15:03:00Z", 11.5, 11.6, 10.8, 11.0, 1500.0, 11.1, 15),
    ]
    records = []
    for idx, (ts, open_, high, low, close, volume, vwap, count) in enumerate(rows):
        records.append(
            {
                "master_intraday_bar_id": f"bar_{idx}",
                "ticker": "AAA",
                "instrument_id": "ticker:AAA",
                "ts_utc": ts,
                "session_date": "2025-01-06",
                "bar_size": "1m",
                "price_view": "1m_quote_guarded_raw",
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "vwap": vwap,
                "transaction_count": count,
                "quote_guarded_view": "ohlcv_1m_quote_guarded_v0_1",
                "quote_guarded_repair_applied": False,
                "repair_manifest_row_present": False,
                "repair_state": "not_in_repair_manifest",
                "repair_reason": "not_applicable",
                "source_quote_guarded_repair_manifest": "repair_manifest.parquet",
                "source_quote_guarded_run_id": "repair_run",
                "full_universe_claim": False,
                "execution_truth": False,
            }
        )
    pd.DataFrame(records).to_parquet(path, index=False)
    return path


def test_intraday_1m_event_outcomes_candidate_builder(tmp_path: Path) -> None:
    event_state = _write_event_state(tmp_path)
    event_windows = _write_event_windows(tmp_path)
    master_intraday = _write_master_intraday(tmp_path)
    output_root = tmp_path / "out"

    args = builder.parse_args(
        [
            "--event-state",
            str(event_state),
            "--event-windows",
            str(event_windows),
            "--master-intraday",
            str(master_intraday),
            "--output-root",
            str(output_root),
            "--run-id",
            "intraday_outcomes_fixture_run",
            "--created-at-utc",
            "2026-07-05T00:00:00Z",
            "--overwrite",
        ]
    )
    args.event_state_manifest = None
    args.event_windows_manifest = None
    args.master_intraday_manifest = None

    manifest = builder.build(args)
    df = pd.read_parquet(manifest["output_path"])

    assert manifest["dataset_id"] == builder.DATASET_ID
    assert manifest["status"] == "controlled_candidate_not_promoted"
    assert manifest["validations"]["validator_status"] == "passed"
    assert manifest["outcome_rows"] == 1
    assert manifest["good_intraday_1m_outcome_rows"] == 1

    row = df.iloc[0]
    assert row["event_window_id"] == "window_post"
    assert row["reference_event_state_id"] == "event_state_at_event"
    assert row["reference_price"] == 10.0
    assert row["bars_expected"] == 3
    assert row["bars_observed"] == 3
    assert row["outcome_open"] == 10.0
    assert row["outcome_high"] == 12.0
    assert row["outcome_low"] == 9.5
    assert row["outcome_close"] == 11.0
    assert abs(row["reference_to_outcome_close_return_pct"] - 10.0) < 1e-9
    assert abs(row["mfe_pct"] - 20.0) < 1e-9
    assert abs(row["mae_pct"] - (-5.0)) < 1e-9
    assert row["contains_post_event_information"]
    assert row["prohibited_as_pre_event_feature"]
    assert not row["valid_for_ml_label_candidate"]
    assert not row["valid_for_rl_reward_candidate"]
    assert not row["full_universe_claim"]
    assert not row["execution_truth"]
