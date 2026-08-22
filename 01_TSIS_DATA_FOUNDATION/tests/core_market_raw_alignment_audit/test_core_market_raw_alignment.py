from __future__ import annotations

import importlib.util
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import yaml


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "core_market_raw_alignment_audit"
    / "audit_core_market_raw_alignment.py"
)
SPEC = importlib.util.spec_from_file_location("core_market_raw_alignment_audit", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def _write_daily(root: Path, ticker: str, values: list[str]) -> None:
    path = root / f"ticker={ticker}" / "year=2023" / f"day_aggs_{ticker}_2023.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    count = len(values)
    pq.write_table(
        pa.table(
            {
                "ticker": [ticker] * count,
                "date": values,
                "o": [1.0] * count,
                "h": [1.1] * count,
                "l": [0.9] * count,
                "c": [1.0] * count,
                "v": [100.0] * count,
            }
        ),
        path,
    )


def _write_1m(root: Path, ticker: str, values: list[str]) -> None:
    path = root / f"ticker={ticker}" / "year=2023" / "month=01" / f"minute_aggs_{ticker}_2023_01.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    count = len(values)
    pq.write_table(
        pa.table(
            {
                "ticker": [ticker] * count,
                "ts_utc": [f"{value}T14:30:00+00:00" for value in values],
                "date": values,
                "year": [2023] * count,
                "month": [1] * count,
                "o": [1.0] * count,
                "h": [1.1] * count,
                "l": [0.9] * count,
                "c": [1.0] * count,
                "v": [100.0] * count,
            }
        ),
        path,
    )


def _write_quote(root: Path, ticker: str, value: str) -> None:
    parsed = date.fromisoformat(value)
    path = (
        root
        / ticker
        / f"year={parsed.year}"
        / f"month={parsed.month:02d}"
        / f"day={parsed.day:02d}"
        / "quotes.parquet"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.table(
            {
                "ask_price": [1.01],
                "bid_price": [1.0],
                "timestamp": [1_700_000_000_000_000_000],
                "year": pa.array([parsed.year], type=pa.int32()),
                "month": pa.array([parsed.month], type=pa.int32()),
                "day": pa.array([parsed.day], type=pa.int32()),
            }
        ),
        path,
    )


def _write_trade(root: Path, ticker: str, value: str) -> None:
    parsed = date.fromisoformat(value)
    path = (
        root
        / ticker
        / f"year={parsed.year}"
        / f"month={parsed.month:02d}"
        / f"day={value}"
        / "market.parquet"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.table(
            {
                "ticker": [ticker],
                "date": [value],
                "timestamp": pa.array([datetime(parsed.year, parsed.month, parsed.day, 15)], type=pa.timestamp("us")),
                "price": [1.0],
                "size": [100],
                "exchange": [4],
                "conditions": pa.array([[0]], type=pa.list_(pa.int64())),
                "year": [parsed.year],
                "month": [parsed.month],
                "day": [value],
            }
        ),
        path,
    )


def _config(tmp_path: Path, expected: int = 2) -> Path:
    roots = {
        "ohlcv_daily": tmp_path / "daily",
        "ohlcv_1m": tmp_path / "minute",
        "quotes_": tmp_path / "quotes",
        "trades_ticks_prod_2005_2026": tmp_path / "trades",
    }
    for root in roots.values():
        root.mkdir(parents=True, exist_ok=True)
    universe = tmp_path / "universe.parquet"
    pq.write_table(pa.table({"ticker": ["AACT", "NA"]}), universe)
    payload = {
        "contract_version": "test",
        "audit_name": "core_market_raw_alignment_audit",
        "scope": {
            "start_date_inclusive": "2005-01-01",
            "end_date_inclusive": "2026-08-20",
            "expected_universe_members": expected,
            "target_scoped": True,
            "extras_outside_target_are_blocking": False,
        },
        "universe": {"path": str(universe), "ticker_column": "ticker"},
        "runtime": {
            "output_root": str(tmp_path / "runs"),
            "heartbeat_seconds": 1,
            "family_workers": 4,
            "one_sequential_reader_per_family": True,
        },
        "families": {
            "ohlcv_daily": {
                "root": str(roots["ohlcv_daily"]),
                "ticker_directory_template": "ticker={ticker}",
                "date_strategy": "column",
                "date_column": "date",
                "required_columns": ["ticker", "date", "o", "h", "l", "c", "v"],
            },
            "ohlcv_1m": {
                "root": str(roots["ohlcv_1m"]),
                "ticker_directory_template": "ticker={ticker}",
                "date_strategy": "column",
                "date_column": "date",
                "required_columns": ["ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v"],
            },
            "quotes_": {
                "root": str(roots["quotes_"]),
                "ticker_directory_template": "{ticker}",
                "date_strategy": "path_ymd_parts",
                "required_columns": ["ask_price", "bid_price", "timestamp", "year", "month", "day"],
            },
            "trades_ticks_prod_2005_2026": {
                "root": str(roots["trades_ticks_prod_2005_2026"]),
                "ticker_directory_template": "{ticker}",
                "date_strategy": "path_day_iso",
                "required_columns": [
                    "ticker",
                    "date",
                    "timestamp",
                    "price",
                    "size",
                    "exchange",
                    "conditions",
                    "year",
                    "month",
                    "day",
                ],
            },
        },
        "probe": {"tickers": ["AACT", "NA"]},
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return config_path


def test_inspect_daily_reads_only_date_column_and_metadata(tmp_path: Path) -> None:
    root = tmp_path / "daily"
    _write_daily(root, "AACT", ["2023-01-03", "2023-01-04"])
    path = next(root.rglob("*.parquet"))
    spec = {
        "date_strategy": "column",
        "date_column": "date",
        "required_columns": ["ticker", "date", "o", "h", "l", "c", "v"],
    }
    row, dates = AUDIT.inspect_parquet_file(
        path=path,
        family="ohlcv_daily",
        ticker="AACT",
        family_root=root,
        spec=spec,
        scope_start=date(2005, 1, 1),
        scope_end=date(2026, 8, 20),
    )
    assert row["parquet_openable"] is True
    assert row["metadata_num_rows"] == 2
    assert row["required_schema_complete"] is True
    assert row["error_class"] is None
    assert dates == {date(2023, 1, 3), date(2023, 1, 4)}


def test_zero_byte_and_missing_schema_are_explicit(tmp_path: Path) -> None:
    root = tmp_path / "quotes"
    zero = root / "AACT" / "year=2023" / "month=01" / "day=03" / "quotes.parquet"
    zero.parent.mkdir(parents=True, exist_ok=True)
    zero.write_bytes(b"")
    spec = {
        "date_strategy": "path_ymd_parts",
        "required_columns": ["ask_price", "bid_price", "timestamp", "year", "month", "day"],
    }
    row, dates = AUDIT.inspect_parquet_file(
        path=zero,
        family="quotes_",
        ticker="AACT",
        family_root=root,
        spec=spec,
        scope_start=date(2005, 1, 1),
        scope_end=date(2026, 8, 20),
    )
    assert "ZERO_BYTE_PARQUET" in row["error_class"]
    assert "UNREADABLE_PARQUET" in row["error_class"]
    assert dates == set()

    bad_schema = root / "AACT" / "year=2023" / "month=01" / "day=04" / "quotes.parquet"
    bad_schema.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table({"timestamp": [1]}), bad_schema)
    row, dates = AUDIT.inspect_parquet_file(
        path=bad_schema,
        family="quotes_",
        ticker="AACT",
        family_root=root,
        spec=spec,
        scope_start=date(2005, 1, 1),
        scope_end=date(2026, 8, 20),
    )
    assert "SCHEMA_MISSING_REQUIRED_COLUMNS" in row["error_class"]
    assert dates == {date(2023, 1, 4)}


def test_roster_extras_are_reported_separately_from_missing_targets(tmp_path: Path) -> None:
    root = tmp_path / "daily"
    (root / "ticker=AACT").mkdir(parents=True)
    (root / "ticker=EXTRA").mkdir(parents=True)
    roster = AUDIT.roster_for_family(
        {"root": str(root), "ticker_directory_template": "ticker={ticker}"},
        {"AACT", "NA"},
    )
    assert roster["missing"] == ["NA"]
    assert roster["extra"] == ["EXTRA"]
    assert roster["expected_target_present_count"] == 1


def test_end_to_end_probe_and_hash_valid_resume(tmp_path: Path) -> None:
    config_path = _config(tmp_path)
    config, _ = AUDIT.load_config(config_path)
    roots = {family: Path(spec["root"]) for family, spec in config["families"].items()}

    _write_daily(roots["ohlcv_daily"], "AACT", ["2023-01-03", "2023-01-04"])
    _write_1m(roots["ohlcv_1m"], "AACT", ["2023-01-03", "2023-01-04"])
    _write_quote(roots["quotes_"], "AACT", "2023-01-03")
    _write_quote(roots["quotes_"], "AACT", "2023-01-04")
    _write_trade(roots["trades_ticks_prod_2005_2026"], "AACT", "2023-01-03")

    _write_daily(roots["ohlcv_daily"], "NA", ["2023-01-03"])
    _write_1m(roots["ohlcv_1m"], "NA", ["2023-01-03"])
    (roots["ohlcv_daily"] / "ticker=EXTRA").mkdir(parents=True)

    code, summary = AUDIT.execute_run(
        config_path=config_path,
        run_id="probe_test",
        mode="probe",
        explicit_tickers="AACT,NA",
        resume=False,
        use_processes=False,
    )
    assert code == 0
    assert summary is not None
    assert summary["technical_status"] == "COMPLETED"
    assert summary["dataset_verdict"] == "PROBE_COMPLETED_WITH_DIFFERENCES"
    assert summary["extra_tickers_outside_target_by_family"]["ohlcv_daily"] == 1
    assert summary["missing_expected_tickers_by_family"]["quotes_"] == 1
    assert summary["blocking_counts"]["tickers_with_date_set_mismatch"] == 2

    run_root = Path(config["runtime"]["output_root"]) / "probe_test"
    coverage = pq.read_table(run_root / "02_ticker_coverage" / "ticker_family_coverage.parquet")
    assert coverage.num_rows == 2
    assert set(coverage.column("ticker").to_pylist()) == {"AACT", "NA"}

    pre_manifest = yaml.safe_load((run_root / "00_control" / "pre_manifest.json").read_text(encoding="utf-8"))
    task_manifest = AUDIT.task_paths(run_root, "ohlcv_daily", "AACT")["manifest"]
    task_payload = yaml.safe_load(task_manifest.read_text(encoding="utf-8"))
    damaged_artifact = Path(task_payload["artifacts"][0]["path"])
    with damaged_artifact.open("ab") as handle:
        handle.write(b"controlled-test-corruption")
    assert AUDIT.task_manifest_valid(task_manifest, pre_manifest["run_contract_sha256"]) is False

    code, resumed_summary = AUDIT.execute_run(
        config_path=config_path,
        run_id="probe_test",
        mode="probe",
        explicit_tickers="AACT,NA",
        resume=True,
        use_processes=False,
    )
    assert code == 0
    assert resumed_summary == summary | {"completed_at_utc": resumed_summary["completed_at_utc"]}

    assert AUDIT.task_manifest_valid(task_manifest, pre_manifest["run_contract_sha256"]) is True
    connection = sqlite3.connect(run_root / "00_control" / "run_state.sqlite")
    try:
        attempts = {
            (family, ticker): attempt
            for family, ticker, attempt in connection.execute("SELECT family,ticker,attempt FROM tasks")
        }
    finally:
        connection.close()
    assert attempts[("ohlcv_daily", "AACT")] == 2
    assert all(
        attempt == 1
        for key, attempt in attempts.items()
        if key != ("ohlcv_daily", "AACT")
    )
