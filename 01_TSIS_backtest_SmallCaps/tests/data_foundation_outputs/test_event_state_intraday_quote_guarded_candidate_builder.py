from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_event_state_intraday_quote_guarded_candidate as builder  # noqa: E402


def _write_market_state(root: Path) -> Path:
    dataset = root / "market_state"
    dataset.mkdir()
    rows = []
    for ts in ["2025-01-06T14:59:00Z", "2025-01-06T15:01:00Z", "2025-01-06T15:31:00Z"]:
        rows.append(
            {
                "market_state_id": f"market_state_{ts}",
                "source_master_intraday_bar_id": f"bar_{ts}",
                "instrument_id": "ticker:AAA",
                "ticker": "AAA",
                "decision_timestamp_utc": ts,
                "decision_date": "2025-01-06",
                "decision_session_date": "2025-01-06",
                "state_horizon": "closed_1m_bar",
                "state_scope": "intraday_quote_guarded_scoped_candidate",
                "state_schema_version": "market_state_table_v0_1",
                "state_builder_version": "market_state_intraday_quote_guarded_builder_candidate_v0_1",
                "state_quality_state": "state_review_scoped_intraday_component",
                "build_run_id": "market_state_fixture_run",
                "created_at_utc": "2026-07-05T00:00:00Z",
                "source_cutoff_policy_version": "policy",
                "leakage_policy_version": "policy",
                "feature_namespace_version": "features",
                "component_manifest_hash_bundle": "{}",
                "component_build_run_id_bundle": "{}",
                "component_quality_bundle": "{}",
                "component_availability_bundle": "{}",
                "valid_for_event_context_candidate": True,
                "valid_for_ml_feature_candidate": False,
                "valid_for_backtest_context_candidate": False,
                "valid_for_rl_state_candidate": False,
                "valid_for_rl_training_direct": False,
                "valid_for_execution_simulator_direct": False,
                "contains_future_information_without_event_filter": False,
                "requires_asof_filter": True,
                "full_universe_claim": False,
                "execution_truth": False,
                "intraday__last_closed_bar_close": 1.23,
                "intraday__quote_guarded_view": True,
                "quality__candidate_dataset_id": "market_state_table_v0_1_candidate",
            }
        )
    pd.DataFrame(rows).to_parquet(dataset / "data.parquet", index=False)
    return dataset


def _write_event_windows(root: Path) -> Path:
    path = root / "event_windows.parquet"
    pd.DataFrame(
        [
            {
                "event_window_id": "window_pre",
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
                "window_role": "pre_event_30m",
                "window_start_utc": "2025-01-06T14:30:00Z",
                "window_end_utc": "2025-01-06T15:00:00Z",
                "contains_post_event_information": False,
                "leakage_safe_as_pre_event_feature": True,
                "source_event_quality_state": "usable_candidate",
                "event_window_quality_state": "good",
                "event_window_consumption_state": "pre_event_context_window",
                "valid_for_backtest_event_window_candidate": True,
                "full_universe_claim": False,
                "event_anchor_decision_timestamp_utc": "2025-01-06T15:01:00Z",
                "schema_version": "event_windows_table_v0_1_candidate_intraday_1m_strategy_events",
                "quality_policy_version": "policy",
                "build_run_id": "event_windows_fixture_run",
            },
            {
                "event_window_id": "window_anchor",
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
                "window_role": "event_anchor_1m",
                "window_start_utc": "2025-01-06T15:00:00Z",
                "window_end_utc": "2025-01-06T15:01:00Z",
                "contains_post_event_information": False,
                "leakage_safe_as_pre_event_feature": False,
                "source_event_quality_state": "usable_candidate",
                "event_window_quality_state": "good",
                "event_window_consumption_state": "event_anchor_decision_window",
                "valid_for_backtest_event_window_candidate": True,
                "full_universe_claim": False,
                "event_anchor_decision_timestamp_utc": "2025-01-06T15:01:00Z",
                "schema_version": "event_windows_table_v0_1_candidate_intraday_1m_strategy_events",
                "quality_policy_version": "policy",
                "build_run_id": "event_windows_fixture_run",
            },
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
                "window_end_utc": "2025-01-06T15:31:00Z",
                "contains_post_event_information": True,
                "leakage_safe_as_pre_event_feature": False,
                "source_event_quality_state": "usable_candidate",
                "event_window_quality_state": "good",
                "event_window_consumption_state": "outcome_candidate_window",
                "valid_for_backtest_event_window_candidate": True,
                "full_universe_claim": False,
                "event_anchor_decision_timestamp_utc": "2025-01-06T15:01:00Z",
                "schema_version": "event_windows_table_v0_1_candidate_intraday_1m_strategy_events",
                "quality_policy_version": "policy",
                "build_run_id": "event_windows_fixture_run",
            },
        ]
    ).to_parquet(path, index=False)
    return path


def test_event_state_intraday_quote_guarded_candidate_builder(tmp_path: Path) -> None:
    market_root = _write_market_state(tmp_path)
    event_windows = _write_event_windows(tmp_path)
    output_root = tmp_path / "out"
    args = builder.parse_args(
        [
            "--market-state-root",
            str(market_root),
            "--event-windows",
            str(event_windows),
            "--output-root",
            str(output_root),
            "--run-id",
            "event_state_intraday_fixture_run",
            "--created-at-utc",
            "2026-07-05T00:00:00Z",
            "--overwrite",
        ]
    )
    args.market_state_manifest = None
    args.event_windows_manifest = None

    manifest = builder.build(args)
    df = pd.read_parquet(manifest["output_path"])

    assert manifest["dataset_id"] == builder.DATASET_ID
    assert manifest["status"] == "controlled_candidate_not_promoted"
    assert manifest["validations"]["validator_status"] == "passed"
    assert manifest["validations"]["joined_event_state_rows"] == 3
    assert manifest["validations"]["state_role_counts"] == {
        "at_event": 1,
        "post_event_review": 1,
        "pre_event": 1,
    }
    assert df["event_state_id"].is_unique
    assert not df["valid_for_ml_feature_candidate"].any()
    assert not df["valid_for_rl_state_candidate"].any()
    assert not df["full_universe_claim"].any()
    assert not df["execution_truth"].any()
    assert not df["outcome_values_inline_allowed"].any()
    assert not df["label_columns_inline_allowed"].any()
    assert not df["reward_columns_inline_allowed"].any()
    assert not any(column.startswith(builder.PROHIBITED_PREFIXES) for column in df.columns)

    cutoff = pd.to_datetime(df["state_cutoff_utc"], utc=True)
    decision = pd.to_datetime(df["decision_timestamp_utc"], utc=True)
    assert not (cutoff > decision).any()

    role_to_market = dict(zip(df["state_role"], df["market_state_id"]))
    assert role_to_market["pre_event"] == "market_state_2025-01-06T14:59:00Z"
    assert role_to_market["at_event"] == "market_state_2025-01-06T15:01:00Z"
    assert role_to_market["post_event_review"] == "market_state_2025-01-06T15:31:00Z"
    assert df[df["state_role"].eq("post_event_review")][
        "contains_future_information_without_event_filter"
    ].all()
