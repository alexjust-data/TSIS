from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_intraday_1m_strategy_event_windows_candidate as builder  # noqa: E402


def _write_events(path: Path) -> Path:
    source = path / "intraday_events.parquet"
    pd.DataFrame(
        [
            {
                "event_id": "event_intraday_aaa_20250106_150000",
                "event_definition_id": "intraday_1m_first_session_open_move_pct_ge_50_candidate_v0_1",
                "event_family": "intraday_first_motion_threshold_cross_candidate",
                "event_type": "first_motion_threshold_cross",
                "source_candidate_dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded",
                "ticker": "AAA",
                "instrument_id": "ticker:AAA",
                "session_date": "2025-01-06",
                "event_timestamp_utc": "2025-01-06T15:00:00Z",
                "event_bar_end_utc": "2025-01-06T15:01:00Z",
                "as_of_utc": "2025-01-06T15:01:00Z",
                "event_session_phase": "regular",
                "listing_exchange": "XNAS",
                "market_timezone": "America/New_York",
                "event_quality_state": "usable_candidate",
                "event_selection_state": "candidate",
                "valid_for_event_windows_candidate": True,
                "contains_outcome_information": False,
                "contains_label_information": False,
                "contains_reward_information": False,
                "full_universe_claim": False,
                "instrument_identity_temporal_match": True,
                "is_common_stock": True,
                "is_lt1b_operational": True,
            },
            {
                "event_id": "event_intraday_bbb_20250106_210000",
                "event_definition_id": "intraday_1m_first_session_open_move_pct_ge_50_candidate_v0_1",
                "event_family": "intraday_first_motion_threshold_cross_candidate",
                "event_type": "first_motion_threshold_cross",
                "source_candidate_dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded",
                "ticker": "BBB",
                "instrument_id": "ticker:BBB",
                "session_date": "2025-01-06",
                "event_timestamp_utc": "2025-01-06T21:00:00Z",
                "event_bar_end_utc": "2025-01-06T21:01:00Z",
                "as_of_utc": "2025-01-06T21:01:00Z",
                "event_session_phase": "afterhours",
                "listing_exchange": "XNAS",
                "market_timezone": "America/New_York",
                "event_quality_state": "usable_candidate",
                "event_selection_state": "candidate",
                "valid_for_event_windows_candidate": True,
                "contains_outcome_information": False,
                "contains_label_information": False,
                "contains_reward_information": False,
                "full_universe_claim": False,
                "instrument_identity_temporal_match": True,
                "is_common_stock": True,
                "is_lt1b_operational": True,
            },
        ]
    ).to_parquet(source, index=False)
    return source


def test_intraday_1m_strategy_event_windows_candidate_builder(tmp_path: Path) -> None:
    source = _write_events(tmp_path)
    output_root = tmp_path / "out"
    args = builder.parse_args(
        [
            "--source-events",
            str(source),
            "--output-root",
            str(output_root),
            "--run-id",
            "intraday_event_windows_fixture_run",
            "--created-at-utc",
            "2026-07-05T00:00:00Z",
            "--overwrite",
        ]
    )
    args.market_calendar = None
    args.market_calendar_manifest = None

    manifest = builder.build(args)
    df = pd.read_parquet(manifest["output_path"])

    assert manifest["dataset_id"] == builder.DATASET_ID
    assert manifest["validations"]["validator_status"] == "passed"
    assert manifest["validations"]["validator_hard_fail_count"] == 0
    assert manifest["validations"]["row_count"] == 6
    assert manifest["validations"]["source_event_count"] == 2
    assert manifest["validations"]["window_role_counts"] == {
        "event_anchor_1m": 2,
        "post_event_30m": 2,
        "pre_event_30m": 2,
    }

    assert set(df["window_role"]) == {"pre_event_30m", "event_anchor_1m", "post_event_30m"}
    assert not df["full_universe_claim"].any()
    assert not df["valid_for_rl_state_component_candidate"].any()
    assert set(df[df["valid_for_ml_feature_candidate"]]["window_role"]) == {"pre_event_30m"}
    assert set(df[df["valid_for_outcome_window_candidate"]]["window_role"]) == {"post_event_30m"}
    assert not df[df["valid_for_ml_feature_candidate"]]["contains_post_event_information"].any()

    pre = df[df["window_role"].eq("pre_event_30m")]
    pre_end = pd.to_datetime(pre["window_end_utc"], utc=True)
    event_time = pd.to_datetime(pre["event_time_utc"], utc=True)
    assert (pre_end <= event_time).all()
