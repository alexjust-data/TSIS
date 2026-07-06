from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_daily_strategy_event_windows_candidate as builder  # noqa: E402


def _write_inputs(root: Path) -> dict[str, Path]:
    source = root / "daily_events.parquet"
    calendar = root / "market_calendar.parquet"
    pd.DataFrame(
        [
            {
                "event_id": "event_daily_aaa_20250106",
                "event_definition_id": "daily_in_play_momentum_candidate_event_v0_1",
                "event_family": "daily_in_play_momentum_candidate",
                "event_type": "in_play_momentum",
                "source_candidate_dataset_id": "daily_scanner_candidates_table_v0_3",
                "ticker": "AAA",
                "instrument_id": "inst_aaa",
                "session_date": "2025-01-06",
                "as_of_utc": "2025-01-06T21:00:00Z",
                "listing_exchange": "XNAS",
                "event_quality_state": "usable_candidate",
                "event_selection_state": "candidate",
                "valid_for_event_windows_candidate": True,
                "contains_outcome_information": False,
                "contains_label_information": False,
                "contains_reward_information": False,
                "instrument_identity_temporal_match": True,
                "is_common_stock": True,
                "is_lt1b_operational": True,
            },
            {
                "event_id": "event_daily_bbb_20250107",
                "event_definition_id": "daily_in_play_momentum_candidate_event_v0_1",
                "event_family": "daily_in_play_momentum_candidate",
                "event_type": "in_play_momentum",
                "source_candidate_dataset_id": "daily_scanner_candidates_table_v0_3",
                "ticker": "BBB",
                "instrument_id": "inst_bbb",
                "session_date": "2025-01-07",
                "as_of_utc": "2025-01-07T21:00:00Z",
                "listing_exchange": "XNAS",
                "event_quality_state": "usable_candidate",
                "event_selection_state": "candidate",
                "valid_for_event_windows_candidate": True,
                "contains_outcome_information": False,
                "contains_label_information": False,
                "contains_reward_information": False,
                "instrument_identity_temporal_match": True,
                "is_common_stock": True,
                "is_lt1b_operational": True,
            },
        ]
    ).to_parquet(source, index=False)
    pd.DataFrame(
        [
            {
                "session_date": "2025-01-03",
                "open_utc": "2025-01-03T14:30:00Z",
                "close_utc": "2025-01-03T21:00:00Z",
                "session_minutes": 390,
                "is_early_close": False,
                "calendar": "XNYS",
                "timezone": "America/New_York",
            },
            {
                "session_date": "2025-01-06",
                "open_utc": "2025-01-06T14:30:00Z",
                "close_utc": "2025-01-06T21:00:00Z",
                "session_minutes": 390,
                "is_early_close": False,
                "calendar": "XNYS",
                "timezone": "America/New_York",
            },
            {
                "session_date": "2025-01-07",
                "open_utc": "2025-01-07T14:30:00Z",
                "close_utc": "2025-01-07T21:00:00Z",
                "session_minutes": 390,
                "is_early_close": False,
                "calendar": "XNYS",
                "timezone": "America/New_York",
            },
            {
                "session_date": "2025-01-08",
                "open_utc": "2025-01-08T14:30:00Z",
                "close_utc": "2025-01-08T21:00:00Z",
                "session_minutes": 390,
                "is_early_close": False,
                "calendar": "XNYS",
                "timezone": "America/New_York",
            },
        ]
    ).to_parquet(calendar, index=False)
    return {"source": source, "calendar": calendar}


def test_daily_strategy_event_windows_candidate_builder(tmp_path: Path) -> None:
    inputs = _write_inputs(tmp_path)
    output_root = tmp_path / "out"
    args = builder.parse_args(
        [
            "--source-events",
            str(inputs["source"]),
            "--market-calendar",
            str(inputs["calendar"]),
            "--output-root",
            str(output_root),
            "--run-id",
            "daily_event_windows_fixture_run",
            "--created-at-utc",
            "2026-07-05T00:00:00Z",
            "--overwrite",
        ]
    )
    manifest = builder.build(args)
    df = pd.read_parquet(manifest["output_path"])

    assert manifest["dataset_id"] == builder.DATASET_ID
    assert manifest["validations"]["validator_status"] == "passed"
    assert manifest["validations"]["validator_hard_fail_count"] == 0
    assert manifest["validations"]["row_count"] == 6
    assert manifest["validations"]["source_event_count"] == 2
    assert manifest["validations"]["window_role_counts"] == {
        "prior_session_regular": 2,
        "event_session_regular": 2,
        "next_session_regular": 2,
    }
    assert set(df["window_role"]) == {
        "prior_session_regular",
        "event_session_regular",
        "next_session_regular",
    }
    assert not df["full_universe_claim"].any()
    assert not df["valid_for_rl_state_component_candidate"].any()
    assert not df[df["valid_for_ml_feature_candidate"]]["contains_post_event_information"].any()
    assert set(df[df["valid_for_ml_feature_candidate"]]["window_role"]) == {"prior_session_regular"}
    assert set(df[df["valid_for_outcome_window_candidate"]]["window_role"]) == {"next_session_regular"}
