from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "build_trading_activity_ta3_stratified_sample.py"
)
SPEC = importlib.util.spec_from_file_location("ta3_sample_builder", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _fixture() -> pd.DataFrame:
    rows = []
    for index in range(160):
        rows.append(
            {
                "selection_hash": f"{index:064x}",
                "ticker_as_of_session": f"T{index:03d}",
                "block_start_population_context_id": f"ctx-{index}",
                "instrument_context_key": f"i-{index}|T{index:03d}",
                "instrument_id": f"i-{index}",
                "block_start_governed_index": 200 + index,
                "price_band": f"P{index % 5 + 1}",
                "market_cap_band": f"M{index % 4 + 1}",
                "foundation_quality_label": f"Q{index % 4 + 1}",
                "local_audit_disposition": f"L{index % 2 + 1}",
                "activity_stratum": f"A{index % 4}",
                "zero_prevalence_stratum": f"Z{index % 3 + 1}",
            }
        )
    return pd.DataFrame(rows)


def test_selection_is_deterministic_and_reaches_capacity() -> None:
    frame = _fixture()
    first, first_audit = MODULE.select_cohort_blocks(
        frame,
        capacity=60,
        price_minimum=8,
        cap_minimum=12,
        metadata_minimum=5,
        max_composite=2,
        max_bare=2,
        minimum_separation=252,
    )
    second, second_audit = MODULE.select_cohort_blocks(
        frame.sample(frac=1.0, random_state=7),
        capacity=60,
        price_minimum=8,
        cap_minimum=12,
        metadata_minimum=5,
        max_composite=2,
        max_bare=2,
        minimum_separation=252,
    )
    assert len(first) == 60
    assert (
        first["block_start_population_context_id"].tolist()
        == second["block_start_population_context_id"].tolist()
    )
    assert first_audit["shortfalls"] == []
    assert second_audit["shortfalls"] == []


def test_reuse_constraints_are_enforced() -> None:
    frame = _fixture().head(20).copy()
    frame.loc[:, "instrument_id"] = "one-id"
    frame.loc[:, "instrument_context_key"] = "one-id|ONE"
    frame.loc[:, "block_start_governed_index"] = range(200, 220)
    selected, _ = MODULE.select_cohort_blocks(
        frame,
        capacity=10,
        price_minimum=1,
        cap_minimum=1,
        metadata_minimum=1,
        max_composite=2,
        max_bare=2,
        minimum_separation=252,
    )
    assert len(selected) == 1


def test_metadata_quota_shortfall_is_explicit() -> None:
    frame = _fixture().head(8).copy()
    selected, audit = MODULE.select_cohort_blocks(
        frame,
        capacity=3,
        price_minimum=2,
        cap_minimum=2,
        metadata_minimum=2,
        max_composite=2,
        max_bare=2,
        minimum_separation=252,
    )
    assert len(selected) == 3
    assert audit["shortfalls"]
