from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded as builder  # noqa: E402


def _bar(ticker: str, session: str, ts: str, view: str, open_: float, high: float, close: float) -> dict[str, object]:
    return {
        "master_intraday_bar_id": f"bar_{ticker}_{ts}_{view}",
        "dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded",
        "physical_dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped",
        "ticker": ticker,
        "instrument_id": None,
        "ts_utc": ts,
        "session_date": session,
        "year": int(session[:4]),
        "month": int(session[5:7]),
        "bar_size": "1m",
        "price_view": view,
        "open": open_,
        "high": high,
        "low": min(open_, close),
        "close": close,
        "volume": 1000.0,
        "vwap": close,
        "transaction_count": 10,
        "source_raw_open": open_,
        "source_raw_high": high,
        "source_raw_low": min(open_, close),
        "source_raw_close": close,
        "source_raw_vwap": close,
        "source_raw_volume": 1000.0,
        "source_raw_transaction_count": 10,
        "quote_guarded_view": "ohlcv_1m_quote_guarded_v0_1" if view == "1m_quote_guarded_raw" else "raw_ohlcv_1m",
        "quote_guarded_repair_applied": False,
        "repair_manifest_row_present": True,
        "repair_state": "usable",
        "repair_reason": "not_applicable",
        "vw_quote_guarded_status": "usable_observed_raw_vwap",
        "quote_bid_floor": None,
        "quote_ask_cap": None,
        "quote_count": 5,
        "source_quote_guarded_repair_manifest": "repair_manifest.parquet",
        "source_repair_shard_path": "repair_shard.parquet",
        "source_quote_guarded_run_id": "quote_guarded_fixture_run",
        "source_quotes_root": "D:/quotes",
        "source_quotes_root_state": "provisional_d_legacy_recovery_root_pending_e_parity",
        "source_ohlcv_path": f"E:/TSIS/data/ohlcv_1m/ticker={ticker}/fixture.parquet",
        "source_quotes_path": f"D:/quotes/{ticker}/fixture.parquet",
        "raw_ohlc_matches_manifest": True,
        "qg_ohlc_changed": False,
        "manifest_qg_ohlc_differs_from_raw": False,
        "manifest_qg_diff_not_applied": False,
        "vwap_consumption_state": "usable_observed_raw_vwap",
        "event_research_bar_candidate": True,
        "backtest_core_bar_candidate": False,
        "valid_for_ml_feature_candidate": False,
        "valid_for_rl_state_component_candidate": False,
        "full_universe_claim": False,
        "execution_truth": False,
        "schema_version": "master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped_v0_1",
        "quality_policy_version": "master_intraday_quote_guarded_candidate_scoped_policy_v0_1",
    }


def _write_fixture(root: Path) -> tuple[Path, Path, Path]:
    rows = [
        _bar("AAA", "2025-01-02", "2025-01-02T14:30:00Z", "1m_raw", 10.0, 10.2, 10.1),
        _bar("AAA", "2025-01-02", "2025-01-02T14:30:00Z", "1m_quote_guarded_raw", 10.0, 10.2, 10.1),
        _bar("AAA", "2025-01-02", "2025-01-02T14:31:00Z", "1m_raw", 10.1, 15.2, 15.0),
        _bar("AAA", "2025-01-02", "2025-01-02T14:31:00Z", "1m_quote_guarded_raw", 10.1, 15.2, 15.0),
        _bar("BBB", "2025-01-02", "2025-01-02T14:30:00Z", "1m_raw", 20.0, 20.1, 20.0),
        _bar("BBB", "2025-01-02", "2025-01-02T14:30:00Z", "1m_quote_guarded_raw", 20.0, 20.1, 20.0),
        _bar("BBB", "2025-01-02", "2025-01-02T14:31:00Z", "1m_raw", 20.0, 21.0, 20.8),
        _bar("BBB", "2025-01-02", "2025-01-02T14:31:00Z", "1m_quote_guarded_raw", 20.0, 21.0, 20.8),
    ]
    parquet = root / "master_intraday.parquet"
    pd.DataFrame(rows).to_parquet(parquet, index=False)
    manifest = root / "master_intraday_manifest.json"
    manifest.write_text(json.dumps({"dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded"}), encoding="utf-8")
    repair = root / "repair_manifest.parquet"
    pd.DataFrame([{"repair_manifest_fixture": True}]).to_parquet(repair, index=False)
    return parquet, manifest, repair


def test_intraday_event_adapter_builds_valid_quote_guarded_events(tmp_path: Path) -> None:
    master, manifest_path, repair = _write_fixture(tmp_path)
    args = builder.parse_args(
        [
            "--master-intraday-parquet",
            str(master),
            "--master-intraday-manifest",
            str(manifest_path),
            "--source-quote-guarded-repair-manifest",
            str(repair),
            "--output-root",
            str(tmp_path / "out"),
            "--run-id",
            "intraday_event_adapter_fixture_run",
            "--created-at-utc",
            "2026-07-05T00:00:00Z",
            "--overwrite",
        ]
    )
    manifest = builder.build(args)
    events = pd.read_parquet(manifest["event_table_dataset"])
    source = pd.read_parquet(manifest["source_candidates_path"])

    assert manifest["status"] == "controlled_candidate_not_promoted"
    assert manifest["source_stats"]["source_session_count"] == 2
    assert manifest["source_stats"]["selected_source_row_count"] == 1
    assert manifest["event_table_stats"]["row_count"] == 1
    assert manifest["validator_summary"]["status"] == "passed"
    assert manifest["validator_summary"]["hard_fail_count"] == 0
    assert len(source) == 2
    assert len(events) == 1

    row = events.iloc[0].to_dict()
    assert row["ticker"] == "AAA"
    assert row["event_timestamp_utc"] == "2025-01-02T14:31:00Z"
    assert row["event_bar_end_utc"] == "2025-01-02T14:32:00Z"
    assert row["as_of_utc"] == "2025-01-02T14:32:00Z"
    assert bool(row["quote_guarded_view"])
    assert bool(row["quote_guarded_event_confirmed"])
    assert not bool(row["valid_for_ml_feature_candidate"])
    assert not bool(row["valid_for_rl_state_candidate"])
    assert not bool(row["contains_outcome_information"])
