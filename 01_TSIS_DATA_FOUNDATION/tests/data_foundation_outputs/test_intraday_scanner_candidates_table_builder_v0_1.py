from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[2]
BUILDER = MODULE_ROOT / "scripts" / "materialize_intraday_scanner_candidates_table_v0_1.py"
CONFIG_DIR = MODULE_ROOT / "configs" / "data_foundation_outputs" / "scanner_definitions"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _minute_rows(ticker: str, rows: list[tuple[str, float, float, float, float, float]]) -> pd.DataFrame:
    out = []
    for ts_utc, o, h, low, c, volume in rows:
        out.append(
            {
                "ticker": ticker,
                "ts_utc": ts_utc,
                "date": "2025-01-06",
                "year": 2025,
                "month": 1,
                "o": o,
                "h": h,
                "l": low,
                "c": c,
                "v": volume,
                "vw": c,
                "n": 1,
                "t": int(pd.Timestamp(ts_utc).timestamp() * 1000),
            }
        )
    return pd.DataFrame(out)


def _write_minute_file(root: Path, ticker: str, rows: list[tuple[str, float, float, float, float, float]]) -> None:
    target = root / f"ticker={ticker}" / "year=2025" / "month=01"
    target.mkdir(parents=True)
    _minute_rows(ticker, rows).to_parquet(target / f"minute_aggs_{ticker}_2025_01.parquet", index=False)


def _fixture_sources(root: Path) -> dict[str, Path]:
    source_root = root / "sources"
    minute_root = source_root / "ohlcv_1m"
    master_root = source_root / "master_daily_table_v0_1"
    master_root.mkdir(parents=True)
    instrument_path = source_root / "instrument_master_v0_1.parquet"
    calendar_path = source_root / "market_calendar_v0_1.parquet"

    _write_minute_file(
        minute_root,
        "AAA",
        [
            ("2025-01-06T09:00:00Z", 1.00, 1.10, 1.00, 1.08, 100_000),
            ("2025-01-06T09:30:00Z", 1.30, 1.51, 1.28, 1.50, 450_000),
        ],
    )
    _write_minute_file(
        minute_root,
        "BBB",
        [
            ("2025-01-06T09:10:00Z", 2.00, 2.10, 1.98, 2.05, 100_000),
            ("2025-01-06T14:45:00Z", 2.70, 3.05, 2.65, 3.00, 500_000),
        ],
    )
    _write_minute_file(
        minute_root,
        "CCC",
        [
            ("2025-01-06T14:30:00Z", 5.00, 5.10, 4.95, 5.05, 700_000),
        ],
    )
    _write_minute_file(
        minute_root,
        "DDD",
        [
            ("2025-01-06T21:10:00Z", 1.10, 1.60, 1.05, 1.50, 10_000),
        ],
    )
    _write_minute_file(
        minute_root,
        "ETFZ",
        [
            ("2025-01-06T09:30:00Z", 1.00, 1.60, 0.95, 1.55, 700_000),
        ],
    )
    _write_minute_file(
        minute_root,
        "MCAP",
        [
            ("2025-01-06T14:40:00Z", 1.00, 1.60, 0.95, 1.55, 700_000),
        ],
    )

    master_rows = []
    for ticker, instrument_id, prior_close, market_cap_hint in [
        ("AAA", "inst_a", 1.0, 50_000_000),
        ("BBB", "inst_b", 2.0, 50_000_000),
        ("CCC", "inst_c", 5.0, 50_000_000),
        ("DDD", "inst_d", 1.0, 50_000_000),
        ("ETFZ", "inst_e", 1.0, 50_000_000),
        ("MCAP", "inst_f", 1.0, 150_000_000),
    ]:
        master_rows.append(
            {
                "master_daily_id": f"md_{ticker}",
                "instrument_id": instrument_id,
                "ticker": ticker,
                "session_date": pd.Timestamp("2025-01-06"),
                "price_view": "daily_raw",
                "open": prior_close,
                "high": prior_close * 1.6,
                "low": prior_close * 0.95,
                "close": prior_close * 1.2,
                "prior_close": prior_close,
                "volume": 1_000_000,
                "dollar_volume": 1_000_000.0 * prior_close,
                "rvol_20d": 3.0,
                "gap_pct": 0.0,
                "daily_return_pct": 0.20,
                "data_present": True,
                "family_data_quality_verdict": "usable_for_declared_scope",
                "backtest_core_row_candidate": True,
                "build_run_id": "master_fixture",
                "market_cap_hint": market_cap_hint,
            }
        )
    pd.DataFrame(master_rows).to_parquet(master_root / "data.parquet", index=False)

    instrument_rows = []
    for ticker, instrument_id, is_common, market_cap in [
        ("AAA", "inst_a", True, 50_000_000),
        ("BBB", "inst_b", True, 50_000_000),
        ("CCC", "inst_c", True, 50_000_000),
        ("DDD", "inst_d", True, 50_000_000),
        ("ETFZ", "inst_e", False, 50_000_000),
        ("MCAP", "inst_f", True, 150_000_000),
    ]:
        instrument_rows.append(
            {
                "instrument_id": instrument_id,
                "ticker": ticker,
                "name": ticker,
                "is_common_stock": is_common,
                "active_in_reference": True,
                "valid_to": pd.NaT,
                "primary_exchange": "XNAS",
                "exchange_acronym": "NASDAQ",
                "overview_market_cap": float(market_cap),
                "lt1b_market_cap_t": float(market_cap),
                "overview_weighted_shares_outstanding": 10_000_000.0,
                "reference_last_updated_utc": "2025-01-06T00:00:00Z",
                "build_run_id": "instrument_fixture",
            }
        )
    pd.DataFrame(instrument_rows).to_parquet(instrument_path, index=False)

    calendar = pd.DataFrame(
        [
            {
                "session_date": pd.Timestamp("2025-01-06"),
                "expected_session": True,
                "expected_reason": "regular_session",
            }
        ]
    )
    calendar.to_parquet(calendar_path, index=False)

    for manifest_name in (
        "_master_daily_manifest.json",
        "_instrument_manifest.json",
        "_calendar_manifest.json",
    ):
        _write_json(source_root / manifest_name, {"fixture": True})

    return {
        "minute_root": minute_root,
        "master_root": master_root,
        "instrument_path": instrument_path,
        "calendar_path": calendar_path,
        "master_manifest": source_root / "_master_daily_manifest.json",
        "instrument_manifest": source_root / "_instrument_manifest.json",
        "calendar_manifest": source_root / "_calendar_manifest.json",
    }


def test_intraday_scanner_detects_first_cross_segments_and_gates(tmp_path: Path) -> None:
    sources = _fixture_sources(tmp_path)
    output_root = tmp_path / "out"

    cmd = [
        sys.executable,
        str(BUILDER),
        "--start-date",
        "2025-01-06",
        "--end-date",
        "2025-01-06",
        "--run-id",
        "intraday_scanner_fixture_run",
        "--output-root",
        str(output_root),
        "--minute-root",
        str(sources["minute_root"]),
        "--master-daily-root",
        str(sources["master_root"]),
        "--master-daily-manifest",
        str(sources["master_manifest"]),
        "--instrument-master",
        str(sources["instrument_path"]),
        "--instrument-master-manifest",
        str(sources["instrument_manifest"]),
        "--market-calendar",
        str(sources["calendar_path"]),
        "--market-calendar-manifest",
        str(sources["calendar_manifest"]),
        "--scanner-definitions-dir",
        str(CONFIG_DIR),
        "--overwrite",
    ]
    subprocess.run(cmd, check=True)

    dataset_path = (
        output_root
        / "intraday_scanner_candidates_table_v0_1_candidate_replay"
        / "data.parquet"
    )
    df = pd.read_parquet(dataset_path).set_index("ticker")

    assert set(df.index) == {"AAA", "BBB", "CCC", "DDD", "ETFZ", "MCAP"}
    assert bool(df.loc["AAA", "selected_intraday_in_play_candidate"]) is True
    assert df.loc["AAA", "first_cross_50_segment"] == "premarket"
    assert bool(df.loc["BBB", "selected_intraday_in_play_candidate"]) is True
    assert df.loc["BBB", "first_cross_50_segment"] == "regular"
    assert bool(df.loc["CCC", "motion_threshold_passed"]) is False
    assert bool(df.loc["DDD", "motion_threshold_passed"]) is True
    assert bool(df.loc["DDD", "tradability_threshold_passed"]) is False
    assert bool(df.loc["DDD", "selected_intraday_in_play_candidate"]) is False
    assert bool(df.loc["ETFZ", "common_stock_filter_passed"]) is False
    assert bool(df.loc["ETFZ", "selected_intraday_in_play_candidate"]) is False
    assert bool(df.loc["MCAP", "market_cap_filter_passed"]) is False
    assert bool(df.loc["MCAP", "selected_intraday_in_play_candidate"]) is False
    assert df["intraday_scanner_candidate_id"].is_unique

    manifest = json.loads(
        (
            output_root
            / "_intraday_scanner_candidates_table_manifest_v0_1_candidate_replay.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["dataset_id"] == "intraday_scanner_candidates_table_v0_1"
    assert manifest["full_universe_claim"] is False
    assert manifest["stats"]["selected_intraday_in_play_candidate_rows"] == 2
