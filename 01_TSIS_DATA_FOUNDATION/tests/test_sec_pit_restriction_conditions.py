from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.restriction_conditions import (  # noqa: E402
    resolve_registration_component_conditions,
)


def _component(classification: str, *, file_number: str = "333-1") -> dict:
    return {
        "observation_id": f"component-{classification}",
        "instrument_id": "i",
        "security_class_id": "s",
        "accession_number": "component-accession",
        "value": 100.0,
        "source_sha256": "component-hash",
        "attributes": {
            "file_number": file_number,
            "component_classification": classification,
        },
    }


def _effect(*, file_number: str = "333-1") -> dict:
    return {
        "accession_number": "effect-accession",
        "effective_at": "2024-01-02T16:00:00",
        "eligible_from_session": "2024-01-03",
        "source_sha256": "effect-hash",
        "attributes": {
            "file_number": file_number,
            "restriction_event_type": "RESALE_REGISTRATION_EFFECTIVE",
        },
    }


def test_effectiveness_does_not_confirm_issuance_or_tradability() -> None:
    rows, readout = resolve_registration_component_conditions(
        registration_scope_components=[
            _component("CONTINGENT_OR_FUTURE"),
            _component("REPORTED_HELD"),
        ],
        effect_events=[_effect()],
    )
    future, held = rows
    assert future["restriction_condition_state"] == ("ISSUANCE_OR_EXERCISE_UNCONFIRMED")
    assert future["issued_common_state"] == "NOT_CURRENT_ISSUED_COMMON"
    assert held["restriction_condition_state"] == (
        "RESALE_REGISTRATION_EFFECTIVE_RESTRICTIONS_UNRESOLVED"
    )
    assert held["issued_common_state"] == "REQUIRES_OS_RECONCILIATION"
    assert all(not row["tradable_supply_confirmation"] for row in rows)
    assert all(row["tradability_estimate_contribution"] is None for row in rows)
    assert readout["tradable_supply_confirmed_rows"] == 0
    assert readout["condition_resolution_complete"] is False


def test_non_components_are_not_subject_to_effect_linkage() -> None:
    rows, readout = resolve_registration_component_conditions(
        registration_scope_components=[
            _component("AGGREGATE_REGISTRATION_LIMIT"),
            _component("CONDITIONAL_THRESHOLD_NOT_COMPONENT"),
        ],
        effect_events=[_effect()],
    )
    assert all(row["restriction_condition_state"] == "NOT_APPLICABLE_NON_COMPONENT" for row in rows)
    assert readout["applicable_component_rows"] == 0
    assert readout["effect_link_coverage"] is None


def test_missing_effect_remains_explicit() -> None:
    rows, readout = resolve_registration_component_conditions(
        registration_scope_components=[_component("REPORTED_ISSUED")],
        effect_events=[],
    )
    assert rows[0]["registration_effect_state"] == ("REGISTRATION_EFFECT_NOT_OBSERVED")
    assert readout["registration_effect_not_observed_count"] == 1


def test_empty_component_input_is_blocked_not_passed() -> None:
    rows, readout = resolve_registration_component_conditions(
        registration_scope_components=[],
        effect_events=[_effect()],
    )
    assert rows == []
    assert readout["status"] == "BLOCKED_BY_INPUT_GATES"
    assert "REGISTRATION_SCOPE_COMPONENTS_UNAVAILABLE" in readout["completion_blockers"]
