from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CONFIG = ROOT / "configs" / "population_target_presession_4824_audit_v0_1.json"
sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


builder = load_module(
    "population_target_presession_4824_candidate_builder",
    SCRIPTS / "materialize_population_target_presession_4824_candidate.py",
)


def _write_sources(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    tickers = ["AAA", "BBB", "CCC", "OTHER", "DDD", "EEE"] + [
        f"T{i:04d}" for i in range(4818)
    ]
    instrument_ids = [
        "instrument:aaa",
        "instrument:bbb",
        "instrument:shared",
        "instrument:shared",
        "instrument:ddd",
        "instrument:eee",
    ] + [f"instrument:t{i:04d}" for i in range(4818)]
    instrument_path = tmp_path / "instrument_master.parquet"
    pq.write_table(
        pa.table(
            {
                "instrument_id": instrument_ids,
                "ticker": tickers,
                "is_common_stock": [True] * 4824,
                "is_lt1b_operational": [True] * 4824,
                "ticker_identity_scope": ["fixture_ticker_grain"] * 4824,
            }
        ),
        instrument_path,
    )

    session_dates = [
        date(2025, 1, 2),
        date(2025, 1, 3),
        date(2025, 1, 4),
        date(2025, 4, 2),
        date(2025, 1, 2),
        date(2025, 1, 2),
        date(2025, 1, 2),
    ]
    master_root = tmp_path / "master"
    master_root.mkdir()
    pq.write_table(
        pa.table(
            {
                "master_daily_id": [f"m{i}" for i in range(7)],
                "instrument_id": [
                    "instrument:aaa",
                    "instrument:aaa",
                    "instrument:aaa",
                    "instrument:bbb",
                    "instrument:shared",
                    "instrument:ddd",
                    "instrument:eee",
                ],
                "ticker": ["AAA", "AAA", "AAA", "BBB", "CCC", "DDD", "EEE"],
                "session_date": pa.array(session_dates, type=pa.date32()),
                "expected_session": [True] * 7,
                "data_present": [True] * 7,
                "missing_expected_data": [False] * 7,
                "prior_close": [0.5, 20.0, 10.0, 10.0, 1.0, None, 1.0],
                "selected_price_hard_invalid": [False] * 7,
                "has_split_action": [False, False, False, False, False, False, True],
                "has_ticker_change_action": [False] * 7,
                "has_any_corporate_action": [False, False, False, False, False, False, True],
                "row_level_price_integrity_state": ["VALID"] * 7,
                "family_data_quality_verdict": ["PASS"] * 7,
                "price_view": ["daily_raw"] * 7,
            }
        ),
        master_root / "fixture.parquet",
    )

    fundamentals_root = tmp_path / "fundamentals"
    fundamentals_root.mkdir()
    pq.write_table(
        pa.table(
            {
                "fundamental_asof_id": ["f1", "f2", "f3", "f4", "f5"],
                "instrument_id": [
                    "instrument:aaa",
                    "instrument:aaa",
                    "instrument:bbb",
                    "instrument:shared",
                    "instrument:eee",
                ],
                "ticker": ["AAA", "AAA", "BBB", "OTHER", "EEE"],
                "as_of_date": pa.array(
                    [
                        date(2024, 12, 31),
                        date(2025, 1, 2),
                        date(2024, 12, 31),
                        date(2024, 12, 31),
                        date(2024, 12, 31),
                    ],
                    type=pa.date32(),
                ),
                "period_end": pa.array(
                    [date(2024, 12, 30), date(2025, 1, 1), date(2024, 12, 30), date(2024, 12, 30), date(2024, 12, 30)],
                    type=pa.date32(),
                ),
                "basic_shares_outstanding": [8_000_000.0, 9_000_000.0, 5_000_000.0, 7_000_000.0, 6_000_000.0],
                "diluted_shares_outstanding": [12_000_000.0, 11_000_000.0, 5_500_000.0, 7_500_000.0, 6_500_000.0],
                "instrument_identity_temporal_match": [True] * 5,
                "fundamental_quality_state": ["good_statement_asof"] * 5,
                "source_file": ["fixture.json"] * 5,
                "source_file_row_number": list(range(5)),
                "build_run_id": ["fund_fixture"] * 5,
                "statement_family": ["income_statements"] * 5,
            }
        ),
        fundamentals_root / "fixture.parquet",
    )

    calendar_path = tmp_path / "market_calendar.parquet"
    calendar_dates = sorted(set(session_dates))
    opens = [
        datetime(d.year, d.month, d.day, 14, 30, tzinfo=timezone.utc)
        for d in calendar_dates
    ]
    pq.write_table(
        pa.table(
            {
                "session_date": pa.array(calendar_dates, type=pa.date32()),
                "open_utc": pa.array(opens, type=pa.timestamp("us", tz="UTC")),
                "build_run_id": ["calendar_fixture"] * len(calendar_dates),
            }
        ),
        calendar_path,
    )
    return master_root, instrument_path, fundamentals_root, calendar_path


def _build(tmp_path: Path, policy: str, ttl: int) -> pa.Table:
    master_root, instrument_path, fundamentals_root, calendar_path = _write_sources(tmp_path)
    output = tmp_path / f"candidate_{policy}_{ttl}.parquet"
    manifest = builder.materialize(
        config_path=CONFIG,
        master_daily_root=master_root,
        instrument_master=instrument_path,
        fundamentals_root=fundamentals_root,
        market_calendar=calendar_path,
        output_parquet=output,
        share_policy=policy,
        ttl_days=ttl,
        temp_directory=tmp_path / "spill",
    )
    assert manifest["summary"]["requested_rows"] == 7
    assert manifest["summary"]["denominator_preserved"]
    return pq.read_table(output)


def _row(table: pa.Table, ticker: str, session_date: date) -> dict:
    rows = table.to_pylist()
    return next(
        item
        for item in rows
        if item["ticker_as_of_session"] == ticker
        and item["session_date"] == session_date
    )


def test_candidate_enforces_cutoff_missingness_boundaries_and_review(tmp_path: Path) -> None:
    table = _build(tmp_path, "S1_DILUTED_FIRST", 90)

    aaa_first = _row(table, "AAA", date(2025, 1, 2))
    assert aaa_first["shares_as_of_date"] == date(2024, 12, 31)
    assert aaa_first["presession_reference_price"] == 0.5
    assert aaa_first["population_membership_state"] == "ELIGIBLE_UNDER_DECLARED_PROXY"
    assert aaa_first["presession_cutoff_utc"].hour == 9

    aaa_last = _row(table, "AAA", date(2025, 1, 4))
    assert aaa_last["shares_as_of_date"] == date(2025, 1, 2)
    assert aaa_last["population_membership_state"] == "INELIGIBLE_MARKET_CAP_PROXY"

    assert _row(table, "BBB", date(2025, 4, 2))["population_membership_state"] == "STALE_SHARES_PROXY"
    assert _row(table, "CCC", date(2025, 1, 2))["population_membership_state"] == "UNAVAILABLE_SHARES_PROXY"
    assert _row(table, "DDD", date(2025, 1, 2))["population_membership_state"] == "UNAVAILABLE_REFERENCE_PRICE"
    assert _row(table, "EEE", date(2025, 1, 2))["population_membership_state"] == "CORPORATE_ACTION_REVIEW"


def test_basic_and_diluted_policies_preserve_real_threshold_disagreement(
    tmp_path: Path,
) -> None:
    diluted = _build(tmp_path / "diluted", "S1_DILUTED_FIRST", 90)
    basic = _build(tmp_path / "basic", "S2_BASIC_FIRST", 90)

    diluted_row = _row(diluted, "AAA", date(2025, 1, 4))
    basic_row = _row(basic, "AAA", date(2025, 1, 4))
    assert diluted_row["presession_reference_market_cap_proxy"] == 110_000_000.0
    assert basic_row["presession_reference_market_cap_proxy"] == 90_000_000.0
    assert diluted_row["population_membership_state"] == "INELIGIBLE_MARKET_CAP_PROXY"
    assert basic_row["population_membership_state"] == "ELIGIBLE_UNDER_DECLARED_PROXY"
