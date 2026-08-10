from __future__ import annotations

import importlib.util
import sys
from datetime import date, datetime
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


auditor = load_module(
    "population_target_presession_4824_gates_auditor",
    SCRIPTS / "audit_population_target_presession_4824_gates.py",
)


def _write_fixture_sources(tmp_path: Path) -> tuple[Path, Path, Path]:
    instrument_path = tmp_path / "instrument_master.parquet"
    parent_tickers = ["AAA", "BBB"] + [f"T{i:04d}" for i in range(4822)]
    parent_instruments = ["instrument:aaa", "instrument:bbb"] + [
        f"instrument:t{i:04d}" for i in range(4822)
    ]
    pq.write_table(
        pa.table(
            {
                "instrument_id": parent_instruments,
                "ticker": parent_tickers,
                "is_common_stock": [True] * 4824,
                "is_lt1b_operational": [True] * 4824,
            }
        ),
        instrument_path,
    )

    master_root = tmp_path / "master_daily"
    master_root.mkdir()
    session_dates = [
        date(2025, 1, 2),
        date(2025, 1, 3),
        date(2025, 1, 4),
        date(2025, 1, 2),
    ]
    pq.write_table(
        pa.table(
            {
                "master_daily_id": ["m1", "m2", "m3", "m4"],
                "instrument_id": [
                    "instrument:aaa",
                    "instrument:aaa",
                    "instrument:aaa",
                    "instrument:bbb",
                ],
                "ticker": ["AAA", "AAA", "AAA", "BBB"],
                "session_date": pa.array(session_dates, type=pa.date32()),
                "expected_session": [True] * 4,
                "data_present": [True] * 4,
                "missing_expected_data": [False] * 4,
                "prior_close": [0.5, 20.0, 10.0, 10.0],
                "selected_price_hard_invalid": [False] * 4,
                "has_split_action": [False] * 4,
                "has_ticker_change_action": [False] * 4,
                "has_any_corporate_action": [False] * 4,
                "row_level_price_integrity_state": ["VALID"] * 4,
                "price_view": ["daily_raw"] * 4,
            }
        ),
        master_root / "fixture.parquet",
    )

    fundamentals_root = tmp_path / "fundamentals"
    fundamentals_root.mkdir()
    pq.write_table(
        pa.table(
            {
                "fundamental_asof_id": ["f1", "f2", "f3"],
                "instrument_id": [
                    "instrument:aaa",
                    "instrument:aaa",
                    "instrument:bbb",
                ],
                "ticker": ["AAA", "AAA", "BBB"],
                "as_of_date": pa.array(
                    [date(2024, 12, 31), date(2025, 1, 2), date(2024, 12, 31)],
                    type=pa.date32(),
                ),
                "period_end": pa.array(
                    [date(2024, 12, 30), date(2025, 1, 1), date(2024, 12, 30)],
                    type=pa.date32(),
                ),
                "basic_shares_outstanding": [8_000_000.0, 9_000_000.0, 5_000_000.0],
                "diluted_shares_outstanding": [12_000_000.0, 11_000_000.0, 5_500_000.0],
                "instrument_identity_temporal_match": [True] * 3,
                "valid_for_event_context_candidate": [True] * 3,
                "fundamental_quality_state": ["good_statement_asof"] * 3,
                "as_of_semantics": ["filing_date_available_from_date_only"] * 3,
                "statement_family": ["income_statements"] * 3,
            }
        ),
        fundamentals_root / "fixture.parquet",
    )
    return master_root, instrument_path, fundamentals_root


def test_g0_config_freezes_required_semantics() -> None:
    config = auditor._read_json(CONFIG)
    result = auditor.validate_g0_config(config)

    assert result["g0_contract_gate"] == "PASS"
    assert all(result["checks"].values())


def test_g1_g3_audit_preserves_strict_cutoff_and_measure_disagreement(
    tmp_path: Path,
) -> None:
    master_root, instrument_path, fundamentals_root = _write_fixture_sources(tmp_path)

    result = auditor.audit(
        config_path=CONFIG,
        master_daily_root=master_root,
        instrument_master=instrument_path,
        fundamentals_root=fundamentals_root,
        temp_directory=tmp_path / "duckdb_spill",
    )

    assert result["g0"]["g0_contract_gate"] == "PASS"
    assert result["g1"]["gate"] == "PASS_WITH_RESTRICTIONS"
    assert result["g1"]["parent_metrics"]["ticker_count"] == 4824
    assert result["g2"]["gate"] == "PASS_WITH_RESTRICTIONS"
    assert result["g2"]["same_date_share_rows_conservatively_excluded"] == 1
    assert result["g3"]["gate"] == "PASS_WITH_RESTRICTIONS"
    assert result["g3"]["overall_metrics"]["same_date_selected_rows"] == 0
    assert result["g3"]["checks"]["strict_prior_date_selection"]
    ttl_90 = result["g3"]["ttl_metrics"][0]
    assert ttl_90["ttl_days"] == 90
    assert ttl_90["classification_disagreement_rows"] >= 1
    assert result["next_authorization"] == "CONTROLLED_FIXTURE_IMPLEMENTATION_AUTHORIZED"


def test_g1_fails_duplicate_composite_identity_session_grain(tmp_path: Path) -> None:
    master_root, instrument_path, fundamentals_root = _write_fixture_sources(tmp_path)
    table = pq.read_table(master_root / "fixture.parquet")
    extra = pa.table(
        {
            name: pa.array([table[name][0].as_py()], type=table[name].type)
            for name in table.schema.names
        }
    )
    extra = extra.set_column(
        extra.schema.get_field_index("master_daily_id"),
        "master_daily_id",
        pa.array(["duplicate-id"]),
    )
    pq.write_table(extra, master_root / "duplicate.parquet")

    result = auditor.audit(
        config_path=CONFIG,
        master_daily_root=master_root,
        instrument_master=instrument_path,
        fundamentals_root=fundamentals_root,
        temp_directory=tmp_path / "duckdb_spill_duplicate",
    )

    assert result["g1"]["duplicate_instrument_session_groups"] == 1
    assert not result["g1"]["checks"]["composite_identity_session_grain_unique"]
    assert result["g1"]["gate"] == "FAIL"
