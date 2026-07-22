from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_master_intraday_quote_guarded_candidate_sample as builder  # noqa: E402


def _write_fixture(root: Path) -> Path:
    raw_file = root / "ticker=AAA" / "year=2025" / "month=01" / "minute_aggs_AAA_2025_01.parquet"
    raw_file.parent.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "ts_utc": "2025-01-02T14:30:00Z",
                "date": "2025-01-02",
                "year": 2025,
                "month": 1,
                "o": 10.0,
                "h": 10.0,
                "l": 10.0,
                "c": 10.0,
                "v": 100.0,
                "vw": 10.0,
                "n": 2,
                "t": 1735828200000,
            },
            {
                "ticker": "AAA",
                "ts_utc": "2025-01-02T14:31:00Z",
                "date": "2025-01-02",
                "year": 2025,
                "month": 1,
                "o": 11.0,
                "h": 11.0,
                "l": 11.0,
                "c": 11.0,
                "v": 200.0,
                "vw": 11.0,
                "n": 3,
                "t": 1735828260000,
            },
        ]
    ).to_parquet(raw_file, index=False)

    sample = root / "repair_manifest_lt1b_v0_1_sample.csv"
    fieldnames = [
        "quote_guarded_view",
        "ticker",
        "ts_utc",
        "minute_utc",
        "minute_ny",
        "session_date",
        "year",
        "month",
        "repair_state",
        "repair_reason",
        "quote_guarded_repair_applied",
        "o_raw",
        "h_raw",
        "l_raw",
        "c_raw",
        "o_qg",
        "h_qg",
        "l_qg",
        "c_qg",
        "vw",
        "v",
        "n",
        "vw_quote_guarded_status",
        "quote_bid_floor",
        "quote_ask_cap",
        "quote_count",
        "source_ohlcv_path",
        "source_quotes_path",
        "run_root",
    ]
    rows = [
        {
            "quote_guarded_view": "ohlcv_1m_quote_guarded_v0_1",
            "ticker": "AAA",
            "ts_utc": "2025-01-02 14:30:00+00:00",
            "minute_utc": "2025-01-02 14:30:00+00:00",
            "minute_ny": "2025-01-02 09:30:00-05:00",
            "session_date": "2025-01-02",
            "year": 2025,
            "month": 1,
            "repair_state": "quote_repairable_ohlc",
            "repair_reason": "high_above_quote_ask_cap",
            "quote_guarded_repair_applied": "True",
            "o_raw": 10.0,
            "h_raw": 10.0,
            "l_raw": 10.0,
            "c_raw": 10.0,
            "o_qg": 10.0,
            "h_qg": 9.95,
            "l_qg": 10.0,
            "c_qg": 10.0,
            "vw": 10.0,
            "v": 100.0,
            "n": 2,
            "vw_quote_guarded_status": "usable",
            "quote_bid_floor": 9.9,
            "quote_ask_cap": 9.95,
            "quote_count": 5,
            "source_ohlcv_path": str(raw_file),
            "source_quotes_path": "D:/quotes/AAA/year=2025/month=01/day=02/quotes.parquet",
            "run_root": "C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/test_run",
        },
        {
            "quote_guarded_view": "ohlcv_1m_quote_guarded_v0_1",
            "ticker": "AAA",
            "ts_utc": "2025-01-02 14:31:00+00:00",
            "minute_utc": "2025-01-02 14:31:00+00:00",
            "minute_ny": "2025-01-02 09:31:00-05:00",
            "session_date": "2025-01-02",
            "year": 2025,
            "month": 1,
            "repair_state": "vw_invalid_only",
            "repair_reason": "vw_invalid_against_quote_or_raw_ohlc",
            "quote_guarded_repair_applied": "False",
            "o_raw": 11.0,
            "h_raw": 11.0,
            "l_raw": 11.0,
            "c_raw": 11.0,
            "o_qg": 11.0,
            "h_qg": 11.0,
            "l_qg": 11.0,
            "c_qg": 11.0,
            "vw": 11.0,
            "v": 200.0,
            "n": 3,
            "vw_quote_guarded_status": "vw_invalid_against_quote_or_raw_ohlc",
            "quote_bid_floor": 10.9,
            "quote_ask_cap": 11.1,
            "quote_count": 4,
            "source_ohlcv_path": str(raw_file),
            "source_quotes_path": "D:/quotes/AAA/year=2025/month=01/day=02/quotes.parquet",
            "run_root": "C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/test_run",
        },
    ]
    with sample.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return sample


def test_master_intraday_quote_guarded_candidate_sample_builder(tmp_path: Path) -> None:
    sample = _write_fixture(tmp_path)
    output_root = tmp_path / "out"
    args = builder.parse_args(
        [
            "--repair-sample",
            str(sample),
            "--output-root",
            str(output_root),
            "--max-applied-rows",
            "1",
            "--max-unapplied-rows",
            "1",
            "--run-id",
            "fixture_run",
            "--created-at-utc",
            "2026-07-05T00:00:00Z",
            "--overwrite",
        ]
    )
    manifest = builder.build(args)
    df = pd.read_parquet(manifest["output_path"])

    assert manifest["dataset_id"] == builder.DATASET_ID
    assert manifest["physical_dataset_id"] == builder.PHYSICAL_DATASET_ID
    assert manifest["status"] == "controlled_sample_materialized_not_official"
    assert manifest["validations"]["validator_status"] == "passed"
    assert manifest["validations"]["raw_ohlc_mismatch_rows"] == 0
    assert manifest["validations"]["quote_guarded_repair_applied_source_rows"] == 1
    assert manifest["validations"]["qg_ohlc_changed_source_rows"] == 1
    assert manifest["validations"]["price_view_counts"] == {"1m_quote_guarded_raw": 2, "1m_raw": 2}
    assert set(df["price_view"]) == {"1m_raw", "1m_quote_guarded_raw"}
    assert not df["full_universe_claim"].any()
    assert not df["valid_for_ml_feature_candidate"].any()
    assert not df["valid_for_rl_state_component_candidate"].any()

    repaired = df[(df["ts_utc"] == "2025-01-02T14:30:00Z") & (df["price_view"] == "1m_quote_guarded_raw")].iloc[0]
    raw = df[(df["ts_utc"] == "2025-01-02T14:30:00Z") & (df["price_view"] == "1m_raw")].iloc[0]
    assert float(raw["high"]) == 10.0
    assert float(repaired["high"]) == 9.95
    assert bool(repaired["quote_guarded_repair_applied"])

    vw_blocked = df[(df["ts_utc"] == "2025-01-02T14:31:00Z") & (df["price_view"] == "1m_quote_guarded_raw")].iloc[0]
    assert vw_blocked["vwap_consumption_state"] == "blocked_by_quote_guarded_status"
    assert pd.isna(vw_blocked["vwap"])
