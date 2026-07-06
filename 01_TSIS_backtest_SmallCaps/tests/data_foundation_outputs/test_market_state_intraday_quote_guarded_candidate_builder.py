from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_market_state_intraday_quote_guarded_candidate as builder  # noqa: E402


def _base_row(price_view: str, bar_id: str, ts_utc: str) -> dict[str, object]:
    return {
        "master_intraday_bar_id": bar_id,
        "dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded",
        "physical_dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped",
        "ticker": "AAA",
        "instrument_id": None,
        "ts_utc": ts_utc,
        "session_date": "2025-01-02",
        "bar_size": "1m",
        "price_view": price_view,
        "open": 10.0,
        "high": 10.2,
        "low": 9.9,
        "close": 10.1,
        "volume": 100.0,
        "vwap": 10.05,
        "transaction_count": 2,
        "quote_guarded_view": "ohlcv_1m_quote_guarded_v0_1",
        "quote_guarded_repair_applied": False,
        "repair_manifest_row_present": True,
        "repair_state": "quote_repairable_ohlc",
        "repair_reason": "high_above_quote_ask_cap",
        "vw_quote_guarded_status": "usable",
        "quote_count": 5,
        "source_quote_guarded_repair_manifest": (
            "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/"
            "repair_manifest_lt1b_v0_1.parquet"
        ),
        "source_repair_shard_path": "C:/runs/shard.parquet",
        "source_quote_guarded_run_id": "fixture_run",
        "source_quotes_root_state": "provisional_d_legacy_recovery_root_pending_e_parity",
        "source_ohlcv_path": (
            "E:/TSIS/data/ohlcv_1m/ticker=AAA/year=2025/month=01/"
            "minute_aggs_AAA_2025_01.parquet"
        ),
        "source_quotes_path": "D:/quotes/AAA/year=2025/month=01/day=02/quotes.parquet",
        "raw_ohlc_matches_manifest": True,
        "qg_ohlc_changed": False,
        "manifest_qg_ohlc_differs_from_raw": False,
        "manifest_qg_diff_not_applied": False,
        "vwap_consumption_state": "usable_observed_raw_vwap",
        "full_universe_claim": False,
        "execution_truth": False,
        "valid_for_ml_feature_candidate": False,
        "valid_for_rl_state_component_candidate": False,
        "schema_version": "master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped_v0_1",
        "quality_policy_version": "master_intraday_quote_guarded_candidate_scoped_policy_v0_1",
    }


def _write_intraday_fixture(root: Path) -> tuple[Path, Path]:
    parquet_path = root / "intraday" / "data.parquet"
    parquet_path.parent.mkdir(parents=True)
    raw_row = _base_row("1m_raw", "bar_raw_1", "2025-01-02T14:30:00Z")
    qg_repaired = _base_row("1m_quote_guarded_raw", "bar_qg_1", "2025-01-02T14:30:00Z")
    qg_repaired.update(
        {
            "high": 10.0,
            "close": 10.0,
            "quote_guarded_repair_applied": True,
            "qg_ohlc_changed": True,
            "manifest_qg_ohlc_differs_from_raw": True,
        }
    )
    qg_vwap_blocked = _base_row("1m_quote_guarded_raw", "bar_qg_2", "2025-01-02T14:31:00Z")
    qg_vwap_blocked.update(
        {
            "instrument_id": "ins_AAA",
            "open": 11.0,
            "high": 11.2,
            "low": 10.9,
            "close": 11.1,
            "volume": 200.0,
            "vwap": None,
            "transaction_count": 3,
            "quote_guarded_repair_applied": False,
            "repair_state": "vw_invalid_only",
            "repair_reason": "vw_invalid_against_quote_or_raw_ohlc",
            "vw_quote_guarded_status": "vw_invalid_against_quote_or_raw_ohlc",
            "quote_count": 4,
            "vwap_consumption_state": "blocked_by_quote_guarded_status",
        }
    )
    pd.DataFrame([raw_row, qg_repaired, qg_vwap_blocked]).to_parquet(parquet_path, index=False)
    manifest_path = root / "intraday_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded",
                "physical_dataset_id": "master_intraday_bar_table_v0_2_candidate_quote_guarded_scoped",
                "status": "scoped_candidate_materialized_not_official",
                "build_run_id": "fixture_intraday_run",
                "materialization_scope": "quote_guarded_lt1b_scoped_ticker_month_candidate",
                "full_universe_claim": False,
                "validations": {"validator_status": "passed"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return parquet_path, manifest_path


def test_market_state_intraday_quote_guarded_candidate_builder(tmp_path: Path) -> None:
    intraday_path, intraday_manifest = _write_intraday_fixture(tmp_path)
    args = builder.parse_args(
        [
            "--intraday-parquet",
            str(intraday_path),
            "--intraday-manifest",
            str(intraday_manifest),
            "--output-root",
            str(tmp_path / "out"),
            "--run-id",
            "fixture_market_state_run",
            "--created-at-utc",
            "2026-07-05T00:00:00Z",
            "--overwrite",
        ]
    )
    manifest = builder.build(args)
    df = pd.read_parquet(manifest["output_path"])

    assert manifest["dataset_id"] == builder.DATASET_ID
    assert manifest["physical_dataset_id"] == builder.PHYSICAL_DATASET_ID
    assert manifest["status"] == "controlled_candidate_not_promoted"
    assert manifest["official_dataset_created"] is False
    assert manifest["validations"]["validator_status"] == "passed"
    assert manifest["validations"]["source_quote_guarded_intraday_rows"] == 2
    assert manifest["validations"]["state_rows"] == 2
    assert manifest["validations"]["quote_guarded_repair_applied_rows"] == 1
    assert manifest["validations"]["qg_ohlc_changed_rows"] == 1
    assert manifest["validations"]["full_universe_claim_rows"] == 0
    assert manifest["validations"]["ml_candidate_rows"] == 0
    assert manifest["validations"]["rl_candidate_rows"] == 0

    assert set(df["intraday__price_view"]) == {"1m_quote_guarded_raw"}
    assert not df["full_universe_claim"].any()
    assert not df["valid_for_ml_feature_candidate"].any()
    assert not df["valid_for_rl_state_candidate"].any()
    assert not df["execution_truth"].any()
    assert df["market_state_id"].is_unique
    assert (df["intraday_component_state"] == "included_good").all()
    assert (df["state_quality_state"] == "state_review_scoped_intraday_component").all()

    first = df[df["intraday__source_master_intraday_bar_id"] == "bar_qg_1"].iloc[0]
    assert first["decision_timestamp_utc"] == "2025-01-02T14:31:00Z"
    assert first["intraday_as_of_utc"] == "2025-01-02T14:31:00Z"
    assert first["intraday__bar_start_utc"] == "2025-01-02T14:30:00Z"
    assert first["intraday__bar_end_utc"] == "2025-01-02T14:31:00Z"
    assert float(first["intraday__last_closed_bar_high"]) == 10.0
    assert bool(first["intraday__quote_guarded_repair_applied"])
    assert first["identity__instrument_id_source"] == "ticker_fallback_from_intraday_candidate"

    second = df[df["intraday__source_master_intraday_bar_id"] == "bar_qg_2"].iloc[0]
    assert second["instrument_id"] == "ins_AAA"
    assert second["identity__instrument_id_source"] == "source_intraday_instrument_id"
    assert pd.isna(second["intraday__last_closed_bar_vwap"])
    assert second["intraday__vwap_consumption_state"] == "blocked_by_quote_guarded_status"

    for column in df.columns:
        assert not column.startswith(("outcome__", "label__", "reward__", "future__", "signal__", "strategy__"))
