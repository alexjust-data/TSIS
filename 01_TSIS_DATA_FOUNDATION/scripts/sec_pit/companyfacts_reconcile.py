from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from sec_pit.extract import stable_id


def reconcile_companyfacts_to_primary_os(
    companyfacts_rows: Iterable[dict[str, Any]],
    primary_rows: Iterable[dict[str, Any]],
    *,
    target_class_label: str,
    security_class_gate: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    primary = list(primary_rows)
    by_accession: dict[str, list[dict[str, Any]]] = {}
    for row in primary:
        by_accession.setdefault(str(row.get("accession_number") or ""), []).append(row)
    multiclass_target = "class " in target_class_label.lower()
    output: list[dict[str, Any]] = []
    for fact in companyfacts_rows:
        attributes = fact.get("attributes") or {}
        qualified = (
            fact.get("extraction_method") == "SEC_COMPANYFACTS_XBRL"
            and attributes.get("taxonomy") == "dei"
            and attributes.get("concept") == "EntityCommonStockSharesOutstanding"
        )
        candidates = by_accession.get(str(fact.get("accession_number") or ""), [])
        exact = [
            row
            for row in candidates
            if row.get("measurement_at") == fact.get("measurement_at")
            and row.get("value") is not None
            and fact.get("value") is not None
            and float(row["value"]) == float(fact["value"])
        ]
        same_point_conflict = [
            row
            for row in candidates
            if row.get("measurement_at") == fact.get("measurement_at")
            and row.get("value") is not None
            and fact.get("value") is not None
            and float(row["value"]) != float(fact["value"])
        ]
        if security_class_gate != "PASS":
            state = "HALT_SECURITY_CLASS"
        elif not qualified:
            state = "UNQUALIFIED_COMPANYFACTS_CONCEPT"
        elif exact:
            state = "EXACT_SAME_ACCESSION_MEASUREMENT_VALUE"
        elif same_point_conflict:
            state = "SAME_ACCESSION_MEASUREMENT_VALUE_CONFLICT"
        elif candidates:
            state = "SAME_ACCESSION_POINT_NOT_COMPARABLE"
        else:
            state = "NO_PRIMARY_ACCESSION_MATCH"
        class_validation_authorized = bool(
            state == "EXACT_SAME_ACCESSION_MEASUREMENT_VALUE"
            and not multiclass_target
            and security_class_gate == "PASS"
        )
        output.append(
            {
                "observation_id": fact.get("observation_id"),
                "accession_number": fact.get("accession_number"),
                "form": fact.get("form"),
                "measurement_at": fact.get("measurement_at"),
                "eligible_from_session": fact.get("eligible_from_session"),
                "companyfacts_value": fact.get("value"),
                "taxonomy": attributes.get("taxonomy"),
                "concept": attributes.get("concept"),
                "companyfacts_filed_date": attributes.get(
                    "companyfacts_filed_date"
                ),
                "reconciliation_state": state,
                "matching_primary_observation_ids": sorted(
                    str(row.get("observation_id")) for row in exact
                ),
                "class_validation_authorized": class_validation_authorized,
                "class_scope_state": (
                    "MULTICLASS_TARGET_REQUIRES_PRIMARY_CLASS_EVIDENCE"
                    if multiclass_target
                    else "SINGLE_OR_UNNUMBERED_COMMON_TARGET"
                ),
            }
        )
    readout = {
        "policy_id": "sec_companyfacts_primary_os_reconciliation_v0_1",
        "companyfacts_rows": len(output),
        "exact_same_accession_measurement_value": sum(
            row["reconciliation_state"]
            == "EXACT_SAME_ACCESSION_MEASUREMENT_VALUE"
            for row in output
        ),
        "value_conflicts": sum(
            row["reconciliation_state"]
            == "SAME_ACCESSION_MEASUREMENT_VALUE_CONFLICT"
            for row in output
        ),
        "class_validation_authorized_rows": sum(
            row["class_validation_authorized"] for row in output
        ),
        "companyfacts_role": "O/S_RECONCILIATION_ONLY_NOT_FLOAT_SOURCE",
        "status": "PASS_WITH_RESTRICTIONS",
    }
    return output, readout


def promote_companyfacts_validated_primary_anchors(
    primary_rows: Iterable[dict[str, Any]],
    reconciliation_rows: Iterable[dict[str, Any]],
    *,
    reconciliation_artifact_sha256: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Promote exact single-class primary observations validated by Company Facts."""
    primary_by_id = {
        str(row.get("observation_id")): row for row in primary_rows
    }
    promoted_by_key: dict[tuple[str, str, float, str], dict[str, Any]] = {}
    conflicts = 0
    for reconciliation in reconciliation_rows:
        state = str(reconciliation.get("reconciliation_state") or "")
        if state == "SAME_ACCESSION_MEASUREMENT_VALUE_CONFLICT":
            conflicts += 1
        if not bool(reconciliation.get("class_validation_authorized")):
            continue
        if state != "EXACT_SAME_ACCESSION_MEASUREMENT_VALUE":
            continue
        matching = reconciliation.get("matching_primary_observation_ids")
        if matching is None:
            encoded = reconciliation.get("matching_primary_observation_ids_json")
            matching = json.loads(encoded) if encoded else []
        candidates = [
            primary_by_id[str(observation_id)]
            for observation_id in matching
            if str(observation_id) in primary_by_id
        ]
        if not candidates:
            continue
        chosen = sorted(candidates, key=lambda row: str(row["observation_id"]))[0]
        if (
            not chosen.get("eligible_from_session")
            or chosen.get("causality_state") != "AVAILABILITY_SESSION_RESOLVED"
            or chosen.get("value") is None
            or not chosen.get("measurement_at")
        ):
            continue
        attributes = chosen.get("attributes") or {}
        key = (
            str(chosen.get("accession_number") or ""),
            str(chosen["measurement_at"]),
            float(chosen["value"]),
            str(attributes.get("security_class_label") or ""),
        )
        promoted = dict(chosen)
        promoted["observation_id"] = stable_id(
            "admitted_primary_companyfacts_os_v0_4", *key
        )
        promoted["quality_state"] = "ADMITTED_OS_ANCHOR"
        promoted["extraction_method"] = (
            "RECONCILED_PRIMARY_AND_SEC_COMPANYFACTS_V0_4"
        )
        promoted["attributes"] = {
            **attributes,
            "admission_policy_id": (
                "class_os_primary_companyfacts_exact_agreement_v0_4"
            ),
            "primary_observation_id": chosen["observation_id"],
            "companyfacts_observation_id": reconciliation.get("observation_id"),
            "companyfacts_reconciliation_state": state,
            "companyfacts_reconciliation_artifact_sha256": (
                reconciliation_artifact_sha256
            ),
            "corroboration_scope": (
                "same_accession_measurement_value_primary_and_official_sec_companyfacts"
            ),
        }
        promoted_by_key[key] = promoted
    promoted = list(promoted_by_key.values())
    return promoted, {
        "policy_id": "class_os_primary_companyfacts_exact_agreement_v0_4",
        "promoted_anchor_count": len(promoted),
        "value_conflict_count": conflicts,
        "status": "PASS_WITH_RESTRICTIONS" if promoted else "NO_PROMOTION",
        "restriction": (
            "single_or_unnumbered_common_class_only; multiclass remains fail_closed"
        ),
    }
