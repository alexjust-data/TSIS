from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import materialize_master_intraday_quote_guarded_candidate_scoped as builder  # noqa: E402


def _write_fixture(root: Path) -> tuple[Path, Path]:
    raw_root = root / "ohlcv_1m"
    raw_file = raw_root / "ticker=AAA" / "year=2025" / "month=01" / "minute_aggs_AAA_2025_01.parquet"
    raw_file.parent.mkdir(parents=True)
    pd.DataFrame(
        [
            {"ticker": "AAA", "ts_utc": "2025-01-02T14:30:00Z", "date": "2025-01-02", "year": 2025, "month": 1, "o": 10.0, "h": 10.2, "l": 9.9, "c": 10.1, "v": 100.0, "vw": 10.05, "n": 2, "t": 1},
            {"ticker": "AAA", "ts_utc": "2025-01-02T14:31:00Z", "date": "2025-01-02", "year": 2025, "month": 1, "o": 11.0, "h": 11.2, "l": 10.9, "c": 11.1, "v": 200.0, "vw": 11.05, "n": 3, "t": 2},
            {"ticker": "AAA", "ts_utc": "2025-01-02T14:32:00Z", "date": "2025-01-02", "year": 2025, "month": 1, "o": 12.0, "h": 12.2, "l": 11.9, "c": 12.1, "v": 300.0, "vw": 12.05, "n": 4, "t": 3},
        ]
    ).to_parquet(raw_file, index=False)

    shard = root / "AAA_2025_01_repair_manifest.parquet"
    pd.DataFrame(
        [
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
                "quote_guarded_repair_applied": True,
                "o_raw": 10.0,
                "h_raw": 10.2,
                "l_raw": 9.9,
                "c_raw": 10.1,
                "o_qg": 10.0,
                "h_qg": 10.0,
                "l_qg": 9.9,
                "c_qg": 10.0,
                "vw": 10.05,
                "v": 100.0,
                "n": 2,
                "vw_quote_guarded_status": "usable",
                "quote_bid_floor": 9.9,
                "quote_bid_p50": 9.95,
                "quote_ask_p50": 10.0,
                "quote_ask_cap": 10.0,
                "quote_mid_p50": 9.975,
                "quote_spread_p50": 0.05,
                "quote_spread_pct_p50": 0.5,
                "quote_count": 5,
                "quote_guard_config": "fixture",
                "source_ohlcv_path": str(raw_file),
                "source_quotes_path": "D:/quotes/AAA/year=2025/month=01/day=02/quotes.parquet",
                "manifest_created_at_utc": "2026-07-05T00:00:00Z",
                "run_root": "C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/test_run",
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
                "quote_guarded_repair_applied": False,
                "o_raw": 11.0,
                "h_raw": 11.2,
                "l_raw": 10.9,
                "c_raw": 11.1,
                "o_qg": 11.0,
                "h_qg": 11.2,
                "l_qg": 10.9,
                "c_qg": 11.1,
                "vw": 11.05,
                "v": 200.0,
                "n": 3,
                "vw_quote_guarded_status": "vw_invalid_against_quote_or_raw_ohlc",
                "quote_bid_floor": 10.9,
                "quote_bid_p50": 11.0,
                "quote_ask_p50": 11.1,
                "quote_ask_cap": 11.2,
                "quote_mid_p50": 11.05,
                "quote_spread_p50": 0.1,
                "quote_spread_pct_p50": 0.9,
                "quote_count": 4,
                "quote_guard_config": "fixture",
                "source_ohlcv_path": str(raw_file),
                "source_quotes_path": "D:/quotes/AAA/year=2025/month=01/day=02/quotes.parquet",
                "manifest_created_at_utc": "2026-07-05T00:00:00Z",
                "run_root": "C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/test_run",
            },
        ]
    ).to_parquet(shard, index=False)

    shard_index = root / "lt1b_repair_shard_index.csv"
    with shard_index.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["ticker", "year", "month", "run_index", "run_root", "repair_shard_path"])
        writer.writeheader()
        writer.writerow({"ticker": "AAA", "year": 2025, "month": 1, "run_index": 0, "run_root": "fixture", "repair_shard_path": str(shard)})
    return raw_root, shard_index


def test_master_intraday_quote_guarded_candidate_scoped_builder(tmp_path: Path) -> None:
    raw_root, shard_index = _write_fixture(tmp_path)
    output_root = tmp_path / "out"
    args = builder.parse_args(
        [
            "--ticker-month",
            "AAA:2025-01",
            "--raw-root",
            str(raw_root),
            "--shard-index",
            str(shard_index),
            "--output-root",
            str(output_root),
            "--run-id",
            "fixture_scoped_run",
            "--created-at-utc",
            "2026-07-05T00:00:00Z",
            "--overwrite",
        ]
    )
    manifest = builder.build(args)
    df = pd.read_parquet(manifest["output_path"])

    assert manifest["dataset_id"] == builder.DATASET_ID
    assert manifest["physical_dataset_id"] == builder.PHYSICAL_DATASET_ID
    assert manifest["status"] == "scoped_candidate_materialized_not_official"
    assert manifest["validations"]["validator_status"] == "passed"
    assert manifest["validations"]["raw_rows"] == 3
    assert manifest["validations"]["repair_manifest_rows_in_scope"] == 2
    assert manifest["validations"]["quote_guarded_repair_applied_rows"] == 1
    assert manifest["validations"]["qg_ohlc_changed_rows"] == 1
    assert manifest["validations"]["output_rows"] == 6
    assert manifest["validations"]["price_view_counts"] == {"1m_quote_guarded_raw": 3, "1m_raw": 3}
    assert not df["full_universe_claim"].any()
    assert not df["valid_for_ml_feature_candidate"].any()
    assert not df["valid_for_rl_state_component_candidate"].any()

    repaired = df[(df["ts_utc"] == "2025-01-02T14:30:00Z") & (df["price_view"] == "1m_quote_guarded_raw")].iloc[0]
    unchanged = df[(df["ts_utc"] == "2025-01-02T14:32:00Z") & (df["price_view"] == "1m_quote_guarded_raw")].iloc[0]
    vw_blocked = df[(df["ts_utc"] == "2025-01-02T14:31:00Z") & (df["price_view"] == "1m_quote_guarded_raw")].iloc[0]

    assert float(repaired["high"]) == 10.0
    assert bool(repaired["quote_guarded_repair_applied"])
    assert unchanged["repair_state"] == "not_in_repair_manifest"
    assert float(unchanged["high"]) == 12.2
    assert vw_blocked["vwap_consumption_state"] == "blocked_by_quote_guarded_status"
    assert pd.isna(vw_blocked["vwap"])
