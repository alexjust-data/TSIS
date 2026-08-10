from __future__ import annotations

from typing import Any

NON_COMPONENT_CLASSES = {
    "AGGREGATE_REGISTRATION_LIMIT",
    "CONDITIONAL_THRESHOLD_NOT_COMPONENT",
}
CURRENT_SHARE_CANDIDATE_CLASSES = {
    "REPORTED_COMMON_STOCK_OFFER_COMPONENT",
    "REPORTED_HELD",
    "REPORTED_ISSUED",
    "REPORTED_TRANSFERRED",
}


def resolve_registration_component_conditions(
    *,
    registration_scope_components: list[dict[str, Any]],
    effect_events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Resolve registration effectiveness without asserting tradable supply."""
    effects_by_file_number: dict[str, list[dict[str, Any]]] = {}
    for event in effect_events:
        attributes = event.get("attributes") or {}
        file_number = attributes.get("file_number")
        if (
            isinstance(file_number, str)
            and attributes.get("restriction_event_type") == "RESALE_REGISTRATION_EFFECTIVE"
        ):
            effects_by_file_number.setdefault(file_number, []).append(event)

    rows: list[dict[str, Any]] = []
    for component in registration_scope_components:
        attributes = component.get("attributes") or {}
        file_number = attributes.get("file_number")
        classification = attributes.get("component_classification")
        linked_effects = effects_by_file_number.get(file_number, [])
        linked_effects = sorted(
            linked_effects,
            key=lambda row: (
                row.get("effective_at") or "",
                row.get("accession_number") or "",
            ),
        )
        effect = linked_effects[0] if linked_effects else None

        if classification in NON_COMPONENT_CLASSES:
            condition_state = "NOT_APPLICABLE_NON_COMPONENT"
            issued_common_state = "NOT_A_CURRENT_SHARE_COMPONENT"
            registration_effect_state = "NOT_APPLICABLE"
        elif classification == "CONTINGENT_OR_FUTURE":
            condition_state = "ISSUANCE_OR_EXERCISE_UNCONFIRMED"
            issued_common_state = "NOT_CURRENT_ISSUED_COMMON"
            registration_effect_state = (
                "EFFECTIVE_REGISTRATION_OBSERVED" if effect else "REGISTRATION_EFFECT_NOT_OBSERVED"
            )
        elif classification in CURRENT_SHARE_CANDIDATE_CLASSES:
            condition_state = (
                "RESALE_REGISTRATION_EFFECTIVE_RESTRICTIONS_UNRESOLVED"
                if effect
                else "REGISTRATION_EFFECT_NOT_OBSERVED"
            )
            issued_common_state = "REQUIRES_OS_RECONCILIATION"
            registration_effect_state = (
                "EFFECTIVE_REGISTRATION_OBSERVED" if effect else "REGISTRATION_EFFECT_NOT_OBSERVED"
            )
        else:
            condition_state = "COMPONENT_CLASSIFICATION_UNRESOLVED"
            issued_common_state = "UNRESOLVED"
            registration_effect_state = "UNRESOLVED"

        rows.append(
            {
                "component_observation_id": component.get("observation_id"),
                "instrument_id": component.get("instrument_id"),
                "security_class_id": component.get("security_class_id"),
                "file_number": file_number,
                "component_accession_number": component.get("accession_number"),
                "component_eligible_from_session": component.get("eligible_from_session"),
                "component_classification": classification,
                "component_shares": component.get("value"),
                "issued_common_state": issued_common_state,
                "registration_effect_state": registration_effect_state,
                "restriction_condition_state": condition_state,
                "effect_accession_number": effect.get("accession_number") if effect else None,
                "effect_effective_at": effect.get("effective_at") if effect else None,
                "effect_eligible_from_session": (
                    effect.get("eligible_from_session") if effect else None
                ),
                "tradable_supply_confirmation": False,
                "tradability_estimate_contribution": None,
                "source_component_sha256": component.get("source_sha256"),
                "source_effect_sha256": effect.get("source_sha256") if effect else None,
            }
        )

    state_counts = {
        state: sum(row["restriction_condition_state"] == state for row in rows)
        for state in sorted({row["restriction_condition_state"] for row in rows})
    }
    applicable = [
        row for row in rows if row["restriction_condition_state"] != "NOT_APPLICABLE_NON_COMPONENT"
    ]
    linked = [
        row
        for row in applicable
        if row["registration_effect_state"] == "EFFECTIVE_REGISTRATION_OBSERVED"
    ]
    completion_blockers = [
        *([] if rows else ["REGISTRATION_SCOPE_COMPONENTS_UNAVAILABLE"]),
        "ISSUANCE_AND_OS_RECONCILIATION_INCOMPLETE",
        "LOCKUP_LEGEND_AND_RESALE_CONDITIONS_UNRESOLVED",
        "TRADABILITY_METHODOLOGY_NOT_AUTHORIZED",
    ]
    readout = {
        "status": "PASS_WITH_RESTRICTIONS" if rows else "BLOCKED_BY_INPUT_GATES",
        "component_rows": len(rows),
        "applicable_component_rows": len(applicable),
        "effect_linked_component_rows": len(linked),
        "effect_link_coverage": len(linked) / len(applicable) if applicable else None,
        "condition_state_counts": state_counts,
        "unresolved_component_classification_count": state_counts.get(
            "COMPONENT_CLASSIFICATION_UNRESOLVED", 0
        ),
        "registration_effect_not_observed_count": state_counts.get(
            "REGISTRATION_EFFECT_NOT_OBSERVED", 0
        ),
        "tradable_supply_confirmed_rows": sum(
            bool(row["tradable_supply_confirmation"]) for row in rows
        ),
        "condition_resolution_complete": False,
        "completion_blockers": completion_blockers,
    }
    return rows, readout
