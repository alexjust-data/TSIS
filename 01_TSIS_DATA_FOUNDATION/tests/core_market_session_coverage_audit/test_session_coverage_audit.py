from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "core_market_session_coverage_audit"
    / "audit_core_market_session_coverage.py"
)
SPEC = importlib.util.spec_from_file_location("session_coverage", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_utc_hour_normalization_handles_standard_and_daylight_time() -> None:
    assert MODULE.normalize_utc_hour_to_session_date("2026-01-31T00") == date(2026, 1, 30)
    assert MODULE.normalize_utc_hour_to_session_date("2026-07-01T00") == date(2026, 6, 30)
    assert MODULE.normalize_utc_hour_to_session_date("2026-07-01T08") == date(2026, 7, 1)


def test_vectorized_timestamp_chunk_returns_both_clocks() -> None:
    chunk = pa.array(
        [
            "2026-01-30T23:59:00Z",
            "2026-01-31T00:23:00Z",
            "2026-02-02T14:30:00Z",
        ]
    )
    raw, sessions, invalid = MODULE.normalize_ts_chunk(chunk)
    assert invalid == 0
    assert raw == {date(2026, 1, 30), date(2026, 1, 31), date(2026, 2, 2)}
    assert sessions == {date(2026, 1, 30), date(2026, 2, 2)}


def test_month_end_session_accepts_same_or_next_utc_month_shard() -> None:
    assert MODULE.expected_minute_shards(date(2026, 1, 31)) == [(2026, 1), (2026, 2)]
    assert MODULE.expected_minute_shards(date(2026, 1, 30)) == [(2026, 1)]


def test_minute_missing_shard_is_a_confirmed_local_absence() -> None:
    sets = {family: set() for family in MODULE.FAMILIES}
    sets["ohlcv_daily"] = {date(2026, 2, 2)}
    result = MODULE.classify_gap(
        missing_family="ohlcv_1m",
        session_date=date(2026, 2, 2),
        date_sets=sets,
        minute_shards={(2026, 1)},
    )
    assert result["gap_class"] == "MISSING_MONTH_SHARD"
    assert result["diagnostic_confidence"] == "CONFIRMED_LOCAL_ABSENCE"
    assert result["source_shard_exists"] is False


def test_missing_quote_inside_window_remains_product_dependent() -> None:
    sets = {family: set() for family in MODULE.FAMILIES}
    sets["quotes_"] = {date(2026, 2, 2), date(2026, 2, 4)}
    sets["ohlcv_daily"] = {date(2026, 2, 3)}
    result = MODULE.classify_gap(
        missing_family="quotes_",
        session_date=date(2026, 2, 3),
        date_sets=sets,
        minute_shards=set(),
    )
    assert result["gap_class"] == "PRODUCT_SEMANTIC_DIFFERENCE"
    assert result["diagnostic_confidence"] == "PRODUCT_DEPENDENT"


def test_boundary_fields_expose_common_tail_without_calling_it_missing() -> None:
    result = MODULE.boundary_fields(
        {date(2005, 1, 3), date(2026, 3, 6)},
        "COMMITTED",
        date(2005, 1, 1),
        date(2026, 8, 20),
    )
    assert result["leading_boundary_state"] == "UNVERIFIED_BEFORE_FIRST_OBSERVED"
    assert result["leading_unverified_start"] == date(2005, 1, 1)
    assert result["leading_unverified_end"] == date(2005, 1, 2)
    assert result["trailing_boundary_state"] == "UNVERIFIED_AFTER_LAST_OBSERVED"
    assert result["trailing_unverified_start"] == date(2026, 3, 7)
    assert result["trailing_unverified_end"] == date(2026, 8, 20)


def test_boundary_fields_do_not_evaluate_pending_source() -> None:
    result = MODULE.boundary_fields(
        set(), "SOURCE_PENDING", date(2005, 1, 1), date(2026, 8, 20)
    )
    assert result["trailing_boundary_state"] == "SOURCE_PENDING_NOT_EVALUATED"
    assert result["trailing_unverified_start"] is None


def test_literal_na_is_not_interpreted_as_null() -> None:
    table = MODULE.table_from_rows(
        [{"ticker": "NA", "session_date_et": date(2026, 3, 9)}],
        MODULE.SESSION_DATE_SCHEMA,
    )
    assert table.column("ticker").to_pylist() == ["NA"]


def test_output_schema_order_is_stable() -> None:
    assert MODULE.PRESENCE_SCHEMA.names == [
        "ticker",
        "session_date_et",
        "ohlcv_daily_present",
        "ohlcv_1m_present",
        "quotes_present",
        "trades_present",
        "available_family_count",
        "present_family_count",
        "source_pending_families_json",
    ]


def test_controlled_stop_artifact_names_are_distinct() -> None:
    assert "stop.requested" != "stop.acknowledged"


def test_detached_wrapper_control_directory_does_not_force_resume(tmp_path: Path) -> None:
    (tmp_path / "00_control").mkdir()
    (tmp_path / "00_control" / "wrapper_stdout.log").touch()
    assert MODULE.run_root_requires_resume(tmp_path, resume=False) is False
    (tmp_path / "00_control" / "pre_manifest.json").write_text("{}", encoding="utf-8")
    assert MODULE.run_root_requires_resume(tmp_path, resume=False) is True
    assert MODULE.run_root_requires_resume(tmp_path, resume=True) is False


def test_individual_parquet_under_hive_named_directory_does_not_merge_partition_schema(
    tmp_path: Path,
) -> None:
    path = (
        tmp_path
        / "02_ticker_coverage"
        / "ohlcv_daily"
        / "ticker=RAD"
        / "ticker_dates.parquet"
    )
    path.parent.mkdir(parents=True)
    pq.write_table(
        pa.table(
            {
                "family": ["ohlcv_daily"],
                "ticker": ["RAD"],
                "observed_date": [date(2026, 3, 6)],
            }
        ),
        path,
    )
    assert MODULE.load_source_dates(tmp_path, "ohlcv_daily", "RAD") == {date(2026, 3, 6)}
