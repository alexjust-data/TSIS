from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = _load_module(
    "daily_eligible_universe_consumption_gate",
    SCRIPTS / "build_daily_eligible_universe_consumption_gate.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_fixture(tmp_path: Path) -> Path:
    candidate = tmp_path / "candidate.parquet"
    dates = [date(2022, 12, 29), date(2023, 1, 3), date(2025, 3, 17), date(2010, 1, 4)]
    states = [
        "ELIGIBLE_UNDER_DECLARED_PROXY",
        "INELIGIBLE_PRICE",
        "ELIGIBLE_UNDER_DECLARED_PROXY",
        "UNAVAILABLE_SHARES_PROXY",
    ]
    pq.write_table(
        pa.table(
            {
                "population_context_id": [f"ctx-{i}" for i in range(4)],
                "instrument_id": [f"instrument:{i}" for i in range(4)],
                "ticker_as_of_session": [f"T{i}" for i in range(4)],
                "session_date": pa.array(dates, type=pa.date32()),
                "presession_reference_price": [0.5, 25.0, 20.0, 1.0],
                "presession_reference_market_cap_proxy": [99_000_000.0, 90_000_000.0, 99_999_999.0, None],
                "population_membership_state": states,
                "share_selection_policy_id": ["S1_DILUTED_FIRST"] * 4,
                "shares_ttl_policy_id": ["SHARES_TTL_180D"] * 4,
                "exact_point_shares_claim": [False] * 4,
                "full_historical_us_lt100m_population_claim": [False] * 4,
            }
        ),
        candidate,
    )
    candidate_manifest = tmp_path / "candidate_manifest.json"
    candidate_manifest.write_text(
        json.dumps(
            {
                "output_sha256": _sha(candidate),
                "promotion_state": "EXPERIMENTAL_CANDIDATE_NOT_CANONICAL",
                "claims": {
                    "exact_point_shares_outstanding": False,
                    "full_historical_us_lt100m_population": False,
                },
            }
        ),
        encoding="utf-8",
    )
    calendar = tmp_path / "calendar.parquet"
    opens = [datetime(2022, 12, 29, 14, 30, tzinfo=timezone.utc)]
    closes = [datetime(2022, 12, 29, 21, 0, tzinfo=timezone.utc)]
    pq.write_table(
        pa.table(
            {
                "session_date": pa.array([dates[0]], type=pa.date32()),
                "open_utc": pa.array(opens, type=pa.timestamp("us", tz="UTC")),
                "close_utc": pa.array(closes, type=pa.timestamp("us", tz="UTC")),
            }
        ),
        calendar,
    )
    targets = tmp_path / "targets.parquet"
    pq.write_table(
        pa.table(
            {
                "block_id": ["block-1"],
                "target_ordinal": [1],
                "population_context_id": ["ctx-0"],
                "instrument_id": ["instrument:0"],
                "ticker_as_of_session": ["T0"],
                "session_date": pa.array([dates[0]], type=pa.date32()),
                "presession_reference_price": [0.5],
                "presession_reference_market_cap_proxy": [99_000_000.0],
                "population_membership_state": ["ELIGIBLE_UNDER_DECLARED_PROXY"],
                "decision_seconds": [23400.0],
                "session_minutes": [390.0],
                "is_early_close": [False],
            }
        ),
        targets,
    )
    sample_manifest = tmp_path / "sample_manifest.json"
    sample_manifest.write_text("{}\n", encoding="utf-8")
    cardinality = SCRIPTS / "trading_activity_stage8_target_only_contract.py"
    config = {
        "population_candidate": {
            "path": str(candidate),
            "sha256": _sha(candidate),
            "manifest_path": str(candidate_manifest),
            "manifest_sha256": _sha(candidate_manifest),
            "expected_rows": 4,
            "expected_eligible_rows": 2,
            "eligible_state": "ELIGIBLE_UNDER_DECLARED_PROXY",
            "share_selection_policy_id": "S1_DILUTED_FIRST",
            "shares_ttl_policy_id": "SHARES_TTL_180D",
        },
        "selector_policy": {
            "minimum_price_inclusive": 0.5,
            "maximum_price_inclusive": 20.0,
            "maximum_market_cap_proxy_exclusive": 100000000.0,
        },
        "market_calendar": {"path": str(calendar), "sha256": _sha(calendar)},
        "development_targets": {
            "path": str(targets),
            "sha256": _sha(targets),
            "sample_manifest_path": str(sample_manifest),
            "sample_manifest_sha256": _sha(sample_manifest),
            "expected_target_count": 1,
            "expected_decision_points": 23399,
            "expected_early_close_targets": 0,
            "cardinality_contract_path": str(cardinality),
            "cardinality_contract_sha256": _sha(cardinality),
        },
        "splits": {
            "DEVELOPMENT": ["2011-01-03", "2022-12-30"],
            "TEMPORAL_VALIDATION": ["2023-01-03", "2024-12-31"],
            "ENGINEERING_EXPOSED_EMBARGO": ["2025-01-02", "2025-03-14"],
            "FINAL_TEMPORAL_OOS": ["2025-03-17", "2026-03-09"],
        },
        "denominator_identity": {
            "grain": "instrument_id x session_date x decision_timestamp_utc",
            "grid": "integer UTC seconds strictly after session open and strictly before session close",
        },
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


def test_gate_binds_selector_and_compact_denominator(tmp_path: Path) -> None:
    config = _write_fixture(tmp_path)
    output = tmp_path / "run"
    result = gate.build(config, output, "fixture-run", threads=1, memory_limit="1GB")

    assert result["status"] == "PASS"
    assert result["logical_symbol_seconds"] == 23399
    manifest = json.loads((output / "consumption_manifest.json").read_text(encoding="utf-8"))
    assert manifest["selector_owns_membership"]
    assert not manifest["bindings_recalculate_thresholds"]
    assert manifest["development_symbol_second_denominator"]["physical_interval_rows"] == 1
    assert manifest["development_symbol_second_denominator"]["logical_symbol_second_rows"] == 23399
    assert not manifest["restrictions"]["canonical_screener"]


def test_gate_fails_closed_on_hash_drift(tmp_path: Path) -> None:
    config_path = _write_fixture(tmp_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["population_candidate"]["sha256"] = "0" * 64
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValueError, match="SHA-256 drift"):
        gate.build(config_path, tmp_path / "failed-run", "failed-run", 1, "1GB")
    final = json.loads((tmp_path / "failed-run" / "final_manifest.json").read_text(encoding="utf-8"))
    assert final["status"] == "FAILED"


def test_gate_refuses_overwrite(tmp_path: Path) -> None:
    config_path = _write_fixture(tmp_path)
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        gate.build(config_path, output, "existing", 1, "1GB")
