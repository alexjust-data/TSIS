# ruff: noqa: E402
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.summarize_100_case_scale_gate import aggregate, blocker_codes, outcome


def test_blocker_codes_deduplicates_and_sorts() -> None:
    values = pd.Series(['["B", "A"]', '["A"]', None])
    assert blocker_codes(values) == ["A", "B"]


def test_outcome_distinguishes_full_partial_and_blocked() -> None:
    assert outcome(5, 5) == "CALCULATED_ALL_SESSIONS"
    assert outcome(2, 5) == "CALCULATED_PARTIAL_SESSIONS"
    assert outcome(0, 5) == "BLOCKED_ALL_SESSIONS"


def test_aggregate_excludes_halt_from_eligible_denominator() -> None:
    frame = pd.DataFrame([
        {"temporal_cohort": "A", "probe_gate": "ELIGIBLE", "session_rows": 5, "os_nonnull_rows": 5, "float_nonnull_rows": 5},
        {"temporal_cohort": "A", "probe_gate": "ELIGIBLE", "session_rows": 5, "os_nonnull_rows": 5, "float_nonnull_rows": 0},
        {"temporal_cohort": "A", "probe_gate": "HALT_SECURITY_CLASS", "session_rows": 0, "os_nonnull_rows": 0, "float_nonnull_rows": 0},
    ])
    row = aggregate(frame, "temporal_cohort")[0]
    assert row["case_count"] == 3
    assert row["eligible_case_count"] == 2
    assert row["halt_case_count"] == 1
    assert row["float_full_case_rate"] == 0.5
