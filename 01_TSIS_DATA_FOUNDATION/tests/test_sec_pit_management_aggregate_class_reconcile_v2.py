from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.ownership_class_reconcile import (  # noqa: E402
    reconcile_multiclass_proxy_positions,
)


def proxy(name: str, category: str) -> dict:
    return {
        "observation_id": name,
        "observation_type": "HOLDER_POSITION_SNAPSHOT",
        "accession_number": "proxy",
        "form": "DEF 14A",
        "value": 100.0,
        "eligible_from_session": "2025-07-18",
        "quality_state": "CANDIDATE_REQUIRES_CLASS_ALLOCATION",
        "attributes": {
            "holder_name": name,
            "holder_category": category,
            "supported_issued_common_shares": None,
            "table_class_basis": "MULTI_CLASS_ORDINARY_SHARES",
        },
    }


def test_multiclass_management_aggregate_uses_exact_atomic_class_sum() -> None:
    reconciled, readout = reconcile_multiclass_proxy_positions(
        proxy_observations=[
            proxy("Jane Director", "OFFICER_OR_DIRECTOR"),
            proxy("All directors and officers as a group", "AGGREGATE_GROUP"),
        ],
        class_components=[
            {
                "component_id": "component",
                "holder_name": "Jane Director",
                "security_class_title": "Class B ordinary shares",
                "shares": 100,
                "eligible_from_session": "2025-01-01",
                "source_accession": "source",
            }
        ],
        target_class_label="Class A ordinary shares",
    )
    group = next(
        row
        for row in reconciled
        if row["attributes"]["holder_category"] == "AGGREGATE_GROUP"
    )
    assert group["attributes"]["supported_issued_common_shares"] == 0
    assert readout["unresolved_aggregate_group_rows"] == 0
