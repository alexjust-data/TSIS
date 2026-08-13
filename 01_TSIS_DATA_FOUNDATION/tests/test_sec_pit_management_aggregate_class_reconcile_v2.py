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


def test_single_class_aggregate_uses_atomic_current_sum_only_when_totals_close() -> None:
    director_one = proxy("Director One", "OFFICER_OR_DIRECTOR")
    director_one["value"] = 40.0
    director_one["attributes"].update({
        "supported_issued_common_shares": 40.0,
        "security_title": "Common Stock",
        "table_class_basis": "SINGLE_OR_UNSPECIFIED",
        "reported_beneficial_total_shares": 60.0,
    })
    director_two = proxy("Director Two", "OFFICER_OR_DIRECTOR")
    director_two["value"] = 30.0
    director_two["attributes"].update({
        "supported_issued_common_shares": 30.0,
        "security_title": "Common Stock",
        "table_class_basis": "SINGLE_OR_UNSPECIFIED",
        "reported_beneficial_total_shares": 40.0,
    })
    aggregate = proxy("All directors and officers as a group", "AGGREGATE_GROUP")
    aggregate["value"] = 100.0
    aggregate["attributes"].update({
        "security_title": "Common Stock",
        "table_class_basis": "SINGLE_OR_UNSPECIFIED",
        "reported_beneficial_total_shares": 100.0,
    })
    reconciled, readout = reconcile_multiclass_proxy_positions(
        proxy_observations=[director_one, director_two, aggregate],
        class_components=[],
        target_class_label="Common Stock",
    )
    group = next(
        row
        for row in reconciled
        if row["attributes"]["holder_category"] == "AGGREGATE_GROUP"
    )
    assert group["attributes"]["supported_issued_common_shares"] == 70.0
    assert group["attributes"]["ownership_component_state"] == (
        "EXACT_MULTI_CLASS_MANAGEMENT_AGGREGATE_RESOLVED"
    )
    assert readout["unresolved_aggregate_group_rows"] == 0


def test_single_class_aggregate_does_not_resolve_when_atomic_totals_do_not_close() -> None:
    director = proxy("Director One", "OFFICER_OR_DIRECTOR")
    director["value"] = 40.0
    director["attributes"].update({
        "supported_issued_common_shares": 40.0,
        "security_title": "Common Stock",
        "table_class_basis": "SINGLE_OR_UNSPECIFIED",
        "reported_beneficial_total_shares": 60.0,
    })
    aggregate = proxy("All directors and officers as a group", "AGGREGATE_GROUP")
    aggregate["value"] = 100.0
    aggregate["attributes"].update({
        "security_title": "Common Stock",
        "table_class_basis": "SINGLE_OR_UNSPECIFIED",
        "reported_beneficial_total_shares": 100.0,
    })
    reconciled, readout = reconcile_multiclass_proxy_positions(
        proxy_observations=[director, aggregate],
        class_components=[],
        target_class_label="Common Stock",
    )
    group = next(
        row
        for row in reconciled
        if row["attributes"]["holder_category"] == "AGGREGATE_GROUP"
    )
    assert group["attributes"]["supported_issued_common_shares"] is None
    assert readout["unresolved_aggregate_group_rows"] == 1
