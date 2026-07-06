from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_strategy_candidate_events_table as builder  # noqa: E402


def _write_source(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)
    return path


def test_daily_strategy_candidate_events_builder_writes_validated_candidate(tmp_path: Path) -> None:
    source = _write_source(
        tmp_path / "source" / "daily_scanner.parquet",
        [
            {
                "scanner_candidate_id": "daily_scan_aaa_20250106",
                "scanner_run_id": "daily_scanner_fixture_run_v0_3",
                "scanner_definition_id": "base_eligible_smallcap_denominator_v0_3",
                "build_run_id": "daily_scanner_fixture_run_v0_3",
                "instrument_id": "inst_aaa",
                "ticker": "AAA",
                "session_date": "2025-01-06",
                "primary_exchange": "XNAS",
                "is_common_stock": True,
                "is_lt1b_operational": True,
                "selected_any_profile": True,
                "selected_in_play_momentum_candidate": True,
                "price_view": "daily_raw",
                "as_of_utc": "2025-01-06T21:05:00Z",
                "daily_high_vs_prev_close_pct": 65.0,
                "in_play_motion_pct": 65.0,
                "volume_today": 600000,
                "dollar_volume_today": 990000.0,
                "candidate_reasons": "profile_in_play_momentum_candidate",
            },
            {
                "scanner_candidate_id": "daily_scan_bbb_20250106",
                "scanner_run_id": "daily_scanner_fixture_run_v0_3",
                "scanner_definition_id": "base_eligible_smallcap_denominator_v0_3",
                "build_run_id": "daily_scanner_fixture_run_v0_3",
                "instrument_id": "inst_bbb",
                "ticker": "BBB",
                "session_date": "2025-01-06",
                "is_common_stock": True,
                "is_lt1b_operational": True,
                "selected_any_profile": False,
                "price_view": "daily_raw",
                "as_of_utc": "2025-01-06T21:05:00Z",
            },
        ],
    )
    output_root = tmp_path / "daily_events"

    args = builder.parse_args(
        [
            "--dataset-id",
            builder.DAILY_DATASET_ID,
            "--source-candidates",
            str(source),
            "--output-root",
            str(output_root),
            "--run-id",
            "daily_event_fixture_run",
            "--created-at-utc",
            "2026-07-04T00:00:00Z",
            "--overwrite",
        ]
    )
    manifest = builder.build(args)

    dataset = Path(manifest["dataset_path"])
    df = pd.read_parquet(dataset)
    assert manifest["dataset_id"] == builder.DAILY_DATASET_ID
    assert manifest["validator_summary"]["status"] == "passed"
    assert manifest["validator_summary"]["hard_fail_count"] == 0
    assert len(df) == 1
    row = df.iloc[0].to_dict()
    assert row["event_table_id"] == builder.DAILY_DATASET_ID
    assert row["source_candidate_id"] == "daily_scan_aaa_20250106"
    assert row["event_timestamp_policy"] == "session_close_available"
    assert bool(row["valid_for_event_windows_candidate"]) is True
    assert bool(row["valid_for_event_state_candidate"]) is False
    assert bool(row["valid_for_ml_feature_candidate"]) is False
    assert bool(row["contains_outcome_information"]) is False


def test_intraday_1m_strategy_candidate_events_builder_requires_quote_guarded_and_validates(
    tmp_path: Path,
) -> None:
    source = _write_source(
        tmp_path / "source" / "intraday_scanner_qg.parquet",
        [
            {
                "intraday_scanner_candidate_id": "intraday_scan_aaa_20250106_143000",
                "scanner_run_id": "intraday_scanner_qg_fixture_run",
                "scanner_definition_id": "intraday_in_play_momentum_candidate_denominator_v0_2",
                "build_run_id": "intraday_scanner_qg_fixture_run",
                "instrument_id": "inst_aaa",
                "ticker": "AAA",
                "session_date": "2025-01-06",
                "primary_exchange": "XNAS",
                "is_common_stock": True,
                "is_lt1b_operational": True,
                "selected_intraday_in_play_candidate": True,
                "quote_guarded_event_confirmed": True,
                "quote_guarded_repair_applied_at_event": False,
                "first_cross_50_ts_utc": "2025-01-06T14:30:00Z",
                "first_cross_50_ts_et": "2025-01-06T09:30:00-05:00",
                "first_cross_50_segment": "regular",
                "first_cross_price": 1.55,
                "first_cross_move_vs_prev_close_pct": 55.0,
                "first_cross_move_vs_segment_open_pct": 20.0,
                "volume_to_time_at_first_cross": 750000,
                "dollar_volume_to_time_at_first_cross": 1162500.0,
                "bars_observed_to_first_cross": 1,
                "first_cross_source_ohlcv_1m_file": "fixture/ohlcv_1m_quote_guarded.parquet",
            },
            {
                "intraday_scanner_candidate_id": "intraday_scan_bbb_20250106_143000",
                "scanner_run_id": "intraday_scanner_qg_fixture_run",
                "scanner_definition_id": "intraday_in_play_momentum_candidate_denominator_v0_2",
                "build_run_id": "intraday_scanner_qg_fixture_run",
                "instrument_id": "inst_bbb",
                "ticker": "BBB",
                "session_date": "2025-01-06",
                "is_common_stock": True,
                "is_lt1b_operational": True,
                "selected_intraday_in_play_candidate": False,
                "quote_guarded_event_confirmed": False,
                "first_cross_50_ts_utc": "2025-01-06T15:00:00Z",
            },
        ],
    )
    qg_manifest = tmp_path / "source" / "repair_manifest_lt1b_v0_1.parquet"
    pd.DataFrame([{"repair_manifest_fixture": True}]).to_parquet(qg_manifest, index=False)
    output_root = tmp_path / "intraday_events"

    args = builder.parse_args(
        [
            "--dataset-id",
            builder.INTRADAY_DATASET_ID,
            "--source-candidates",
            str(source),
            "--source-quote-guarded-repair-manifest",
            str(qg_manifest),
            "--source-quote-guarded-run-id",
            "quote_guarded_fixture_run",
            "--output-root",
            str(output_root),
            "--run-id",
            "intraday_event_fixture_run",
            "--created-at-utc",
            "2026-07-04T00:00:00Z",
            "--overwrite",
        ]
    )
    manifest = builder.build(args)

    dataset = Path(manifest["dataset_path"])
    df = pd.read_parquet(dataset)
    assert manifest["dataset_id"] == builder.INTRADAY_DATASET_ID
    assert manifest["validator_summary"]["status"] == "passed"
    assert manifest["validator_summary"]["hard_fail_count"] == 0
    assert len(df) == 1
    row = df.iloc[0].to_dict()
    assert row["event_table_id"] == builder.INTRADAY_DATASET_ID
    assert row["source_candidate_id"] == "intraday_scan_aaa_20250106_143000"
    assert row["source_price_view"] == "ohlcv_1m_quote_guarded"
    assert row["event_timestamp_policy"] == "closed_1m_bar"
    assert row["event_bar_ts_utc"] == "2025-01-06T14:30:00Z"
    assert row["event_bar_end_utc"] == "2025-01-06T14:31:00Z"
    assert row["as_of_utc"] == "2025-01-06T14:31:00Z"
    assert bool(row["quote_guarded_view"]) is True
    assert bool(row["quote_guarded_event_confirmed"]) is True
    assert bool(row["valid_for_ml_feature_candidate"]) is False
    assert bool(row["contains_outcome_information"]) is False


def test_intraday_builder_blocks_selected_rows_without_quote_guarded_confirmation(
    tmp_path: Path,
) -> None:
    source = _write_source(
        tmp_path / "source" / "intraday_raw_only.parquet",
        [
            {
                "intraday_scanner_candidate_id": "intraday_scan_raw_only",
                "instrument_id": "inst_raw",
                "ticker": "RAW",
                "session_date": "2025-01-06",
                "is_common_stock": True,
                "is_lt1b_operational": True,
                "selected_intraday_in_play_candidate": True,
                "quote_guarded_event_confirmed": False,
                "first_cross_50_ts_utc": "2025-01-06T14:30:00Z",
            }
        ],
    )
    qg_manifest = tmp_path / "source" / "repair_manifest_lt1b_v0_1.parquet"
    pd.DataFrame([{"repair_manifest_fixture": True}]).to_parquet(qg_manifest, index=False)

    args = builder.parse_args(
        [
            "--dataset-id",
            builder.INTRADAY_DATASET_ID,
            "--source-candidates",
            str(source),
            "--source-quote-guarded-repair-manifest",
            str(qg_manifest),
            "--output-root",
            str(tmp_path / "out"),
            "--overwrite",
        ]
    )
    with pytest.raises(ValueError, match="quote-guarded confirmation"):
        builder.build(args)
