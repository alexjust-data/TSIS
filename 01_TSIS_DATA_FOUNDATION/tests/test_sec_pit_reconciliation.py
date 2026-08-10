from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.reconcile import reconcile_os_anchors  # noqa: E402


def candidate(method: str, value: float, concept: str | None = None) -> dict:
    return {
        "observation_id": f"{method}-{value}",
        "observation_type": "SHARES_OUTSTANDING_ANCHOR_CANDIDATE",
        "accession_number": "a",
        "measurement_at": "2025-01-02",
        "value": value,
        "extraction_method": method,
        "quality_state": "CANDIDATE_REQUIRES_RECONCILIATION",
        "attributes": {"taxonomy": "dei", "concept": concept} if concept else {},
    }


def test_reconciliation_admits_exact_dei_and_primary_agreement() -> None:
    rows, readout = reconcile_os_anchors([
        candidate("SEC_COMPANYFACTS_XBRL", 10_000_000, "EntityCommonStockSharesOutstanding"),
        candidate("COVER_PAGE_TEXT_REGEX_V0_1", 10_000_000),
    ])
    assert len(rows) == 1
    assert rows[0]["quality_state"] == "ADMITTED_OS_ANCHOR"
    assert readout["status"] == "PASS_WITH_RESTRICTIONS"


def test_reconciliation_rejects_disagreement_and_period_end_concept() -> None:
    rows, readout = reconcile_os_anchors([
        candidate("SEC_COMPANYFACTS_XBRL", 10_000_000, "EntityCommonStockSharesOutstanding"),
        candidate("COVER_PAGE_TEXT_REGEX_V0_1", 750_000_000),
        candidate("SEC_COMPANYFACTS_XBRL", 9_000_000, "CommonStockSharesOutstanding"),
    ])
    assert rows == []
    assert readout["status"] == "FAIL"

