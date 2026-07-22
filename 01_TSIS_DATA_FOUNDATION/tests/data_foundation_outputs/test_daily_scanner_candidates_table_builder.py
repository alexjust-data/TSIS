from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_daily_scanner_candidates_table as builder  # noqa: E402


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(builder.json.dumps(payload, indent=2), encoding="utf-8")


def _fixture_sources(root: Path) -> dict[str, Path]:
    source_root = root / "sources"
    master_root = source_root / "master_daily_table_v0_1"
    master_root.mkdir(parents=True)
    instrument_path = source_root / "instrument_master_v0_1.parquet"
    calendar_path = source_root / "market_calendar_v0_1.parquet"

    session = pd.Timestamp("2025-01-06")
    close_utc = pd.Timestamp("2025-01-06T21:00:00Z")
    master_rows = [
        {
            "master_daily_id": "a",
            "instrument_id": "inst_a",
            "ticker": "AAA",
            "session_date": session,
            "price_view": "daily_raw",
            "open": 1.1,
            "close": 1.65,
            "prior_close": 1.0,
            "volume": 600_000,
            "dollar_volume": 990_000.0,
            "rvol_20d": 4.0,
            "daily_return_pct": 0.65,
            "gap_pct": 0.10,
            "daily_range_pct": 0.80,
            "data_present": True,
            "family_data_quality_verdict": "usable_for_declared_scope",
            "backtest_core_row_candidate": True,
            "build_run_id": "master_fixture",
        },
        {
            "master_daily_id": "b",
            "instrument_id": "inst_b",
            "ticker": "BBB",
            "session_date": session,
            "price_view": "daily_raw",
            "open": 2.0,
            "close": 2.30,
            "prior_close": 2.0,
            "volume": 100_000,
            "dollar_volume": 230_000.0,
            "rvol_20d": 6.0,
            "daily_return_pct": 0.15,
            "gap_pct": 0.03,
            "daily_range_pct": 0.20,
            "data_present": True,
            "family_data_quality_verdict": "usable_for_declared_scope",
            "backtest_core_row_candidate": True,
            "build_run_id": "master_fixture",
        },
        {
            "master_daily_id": "b_alias",
            "instrument_id": "inst_b",
            "ticker": "BBBZ",
            "session_date": session,
            "price_view": "daily_raw",
            "open": 2.0,
            "close": 2.30,
            "prior_close": 2.0,
            "volume": 100_000,
            "dollar_volume": 230_000.0,
            "rvol_20d": 6.0,
            "daily_return_pct": 0.15,
            "gap_pct": 0.03,
            "daily_range_pct": 0.20,
            "data_present": True,
            "family_data_quality_verdict": "usable_for_declared_scope",
            "backtest_core_row_candidate": True,
            "build_run_id": "master_fixture",
        },
        {
            "master_daily_id": "c",
            "instrument_id": "inst_c",
            "ticker": "CCC",
            "session_date": session,
            "price_view": "daily_raw",
            "open": 5.0,
            "close": 5.05,
            "prior_close": 5.0,
            "volume": 700_000,
            "dollar_volume": 3_535_000.0,
            "rvol_20d": 1.1,
            "daily_return_pct": 0.01,
            "gap_pct": 0.0,
            "daily_range_pct": 0.05,
            "data_present": True,
            "family_data_quality_verdict": "usable_for_declared_scope",
            "backtest_core_row_candidate": True,
            "build_run_id": "master_fixture",
        },
        {
            "master_daily_id": "d",
            "instrument_id": "inst_d",
            "ticker": "DDD",
            "session_date": session,
            "price_view": "daily_raw",
            "open": 10.0,
            "close": 12.0,
            "prior_close": 10.0,
            "volume": 250_000,
            "dollar_volume": 3_000_000.0,
            "rvol_20d": 3.0,
            "daily_return_pct": 0.20,
            "gap_pct": 0.05,
            "daily_range_pct": 0.25,
            "data_present": True,
            "family_data_quality_verdict": "usable_for_declared_scope",
            "backtest_core_row_candidate": True,
            "build_run_id": "master_fixture",
        },
        {
            "master_daily_id": "e",
            "instrument_id": "inst_e",
            "ticker": "ETFZ",
            "session_date": session,
            "price_view": "daily_raw",
            "open": 10.0,
            "close": 11.0,
            "prior_close": 10.0,
            "volume": 900_000,
            "dollar_volume": 9_900_000.0,
            "rvol_20d": 3.0,
            "daily_return_pct": 0.10,
            "gap_pct": 0.05,
            "daily_range_pct": 0.12,
            "data_present": True,
            "family_data_quality_verdict": "usable_for_declared_scope",
            "backtest_core_row_candidate": True,
            "build_run_id": "master_fixture",
        },
    ]
    pd.DataFrame(master_rows).to_parquet(master_root / "data.parquet", index=False)

    instrument_rows = [
        {
            "instrument_id": "inst_a",
            "ticker": "AAA",
            "is_common_stock": True,
            "is_lt1b_operational": True,
            "lt1b_market_cap_t": 50_000_000.0,
            "overview_market_cap": 60_000_000.0,
            "lt1b_anchor_date_used": "2025-01-06",
            "lt1b_shares_observed_date": "2025-01-06",
            "overview_request_date": "2025-01-06",
            "primary_exchange": "XNAS",
            "exchange_acronym": "NASDAQ",
            "active_in_reference": True,
            "reference_last_updated_utc": "2025-01-06T00:00:00Z",
            "build_run_id": "instrument_fixture",
        },
        {
            "instrument_id": "inst_b",
            "ticker": "BBB",
            "is_common_stock": True,
            "is_lt1b_operational": True,
            "lt1b_market_cap_t": 50_000_000.0,
            "overview_market_cap": 50_000_000.0,
            "lt1b_anchor_date_used": "2025-01-06",
            "lt1b_shares_observed_date": "2025-01-06",
            "overview_request_date": "2025-01-06",
            "primary_exchange": "XNAS",
            "exchange_acronym": "NASDAQ",
            "active_in_reference": True,
            "reference_last_updated_utc": "2025-01-06T00:00:00Z",
            "build_run_id": "instrument_fixture",
        },
        {
            "instrument_id": "inst_c",
            "ticker": "CCC",
            "is_common_stock": True,
            "is_lt1b_operational": True,
            "lt1b_market_cap_t": 50_000_000.0,
            "overview_market_cap": 50_000_000.0,
            "lt1b_anchor_date_used": "2025-01-06",
            "lt1b_shares_observed_date": "2025-01-06",
            "overview_request_date": "2025-01-06",
            "primary_exchange": "XNAS",
            "exchange_acronym": "NASDAQ",
            "active_in_reference": True,
            "reference_last_updated_utc": "2025-01-06T00:00:00Z",
            "build_run_id": "instrument_fixture",
        },
        {
            "instrument_id": "inst_d",
            "ticker": "DDD",
            "is_common_stock": True,
            "is_lt1b_operational": True,
            "lt1b_market_cap_t": 150_000_000.0,
            "overview_market_cap": 150_000_000.0,
            "lt1b_anchor_date_used": "2025-01-06",
            "lt1b_shares_observed_date": "2025-01-06",
            "overview_request_date": "2025-01-06",
            "primary_exchange": "XNAS",
            "exchange_acronym": "NASDAQ",
            "active_in_reference": True,
            "reference_last_updated_utc": "2025-01-06T00:00:00Z",
            "build_run_id": "instrument_fixture",
        },
        {
            "instrument_id": "inst_e",
            "ticker": "ETFZ",
            "is_common_stock": False,
            "is_lt1b_operational": True,
            "lt1b_market_cap_t": 50_000_000.0,
            "overview_market_cap": 50_000_000.0,
            "lt1b_anchor_date_used": "2025-01-06",
            "lt1b_shares_observed_date": "2025-01-06",
            "overview_request_date": "2025-01-06",
            "primary_exchange": "XNAS",
            "exchange_acronym": "NASDAQ",
            "active_in_reference": True,
            "reference_last_updated_utc": "2025-01-06T00:00:00Z",
            "build_run_id": "instrument_fixture",
        },
    ]
    pd.DataFrame(instrument_rows).to_parquet(instrument_path, index=False)
    pd.DataFrame(
        [
            {
                "session_date": session,
                "close_utc": close_utc,
                "build_run_id": "calendar_fixture",
                "calendar": "XNYS",
                "timezone": "America/New_York",
            }
        ]
    ).to_parquet(calendar_path, index=False)

    master_manifest = source_root / "_master_daily_table_manifest_v0_1.json"
    instrument_manifest = source_root / "_instrument_master_manifest_v0_1.json"
    calendar_manifest = source_root / "_market_calendar_manifest_v0_1.json"
    _write_json(master_manifest, {"build_run_id": "master_fixture"})
    _write_json(instrument_manifest, {"build_run_id": "instrument_fixture"})
    _write_json(calendar_manifest, {"build_run_id": "calendar_fixture"})

    return {
        "master_root": master_root,
        "master_manifest": master_manifest,
        "instrument": instrument_path,
        "instrument_manifest": instrument_manifest,
        "calendar": calendar_path,
        "calendar_manifest": calendar_manifest,
    }


def test_daily_scanner_builder_separates_operational_and_broad_discovery(tmp_path: Path) -> None:
    sources = _fixture_sources(tmp_path)
    output_root = tmp_path / "daily_scanner_replay"
    args = builder.parse_args(
        [
            "--start-date",
            "2025-01-06",
            "--end-date",
            "2025-01-06",
            "--run-id",
            "daily_scanner_fixture_run",
            "--master-daily-root",
            str(sources["master_root"]),
            "--master-daily-manifest",
            str(sources["master_manifest"]),
            "--instrument-master",
            str(sources["instrument"]),
            "--instrument-master-manifest",
            str(sources["instrument_manifest"]),
            "--market-calendar",
            str(sources["calendar"]),
            "--market-calendar-manifest",
            str(sources["calendar_manifest"]),
            "--output-root",
            str(output_root),
        ]
    )

    manifest = builder.build(args)
    validations = manifest["validations"]

    assert validations["row_count"] == 10
    assert validations["source_rows_before_dedup"] == 6
    assert validations["source_duplicate_alias_groups"] == 1
    assert validations["source_duplicate_alias_excess_rows"] == 1
    assert validations["duplicate_key_groups"] == 0
    assert validations["selected_trade_station_like_top25_rows"] == 2
    assert validations["selected_broad_discovery_rows"] >= 3
    assert validations["broad_selected_below_500k_volume_rows"] >= 1
    assert validations["full_universe_claim_true_rows"] == 0
    assert validations["ml_feature_candidate_rows"] == 0
    assert validations["rl_state_candidate_rows"] == 0
    assert validations["live_downstream_candidate_rows"] == 0

    parquet = Path(manifest["output_path"]) / "data.parquet"
    con = duckdb.connect()
    below_500k = con.sql(
        f"""
        select ticker, selected_broad_discovery, selected_trade_station_like_top25, candidate_reasons
        from read_parquet('{parquet.as_posix()}')
        where ticker = 'BBB'
          and scanner_definition_id = 'broad_in_play_discovery_scanner_v0_1'
        """
    ).fetchdf().iloc[0].to_dict()

    assert below_500k["selected_broad_discovery"] is True
    assert below_500k["selected_trade_station_like_top25"] is False
    assert "reason_volume_acceleration" in below_500k["candidate_reasons"]
