from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from sec_pit.extract import stable_id


METHODS = frozenset({
    "COVER_PAGE_CLASS_OS_TEXT_V0_2",
    "INLINE_XBRL_CLASS_CONTEXT_V0_2",
})


def reconcile_class_os_anchors_v0_3(
    observations: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    groups: dict[tuple[str, str, float, str], list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        if row.get("extraction_method") not in METHODS:
            continue
        if (
            not row.get("accession_number")
            or not row.get("measurement_at")
            or row.get("value") is None
            or not row.get("eligible_from_session")
            or row.get("causality_state") != "AVAILABILITY_SESSION_RESOLVED"
        ):
            continue
        attributes = row.get("attributes") or {}
        key = (
            str(row["accession_number"]),
            str(row["measurement_at"]),
            float(row["value"]),
            str(attributes.get("security_class_label") or ""),
        )
        groups[key].append(row)

    admitted: list[dict[str, Any]] = []
    for key, rows in groups.items():
        observed_methods = {str(row["extraction_method"]) for row in rows}
        if observed_methods != METHODS:
            continue
        source_hashes = {str(row.get("source_sha256") or "") for row in rows}
        if len(source_hashes) != 1 or "" in source_hashes:
            continue
        chosen = sorted(rows, key=lambda row: row["observation_id"])[0]
        promoted = dict(chosen)
        promoted["observation_id"] = stable_id("admitted_class_os_v0_3", *key)
        promoted["quality_state"] = "ADMITTED_OS_ANCHOR"
        promoted["extraction_method"] = "RECONCILED_CLASS_TEXT_AND_INLINE_XBRL_V0_3"
        promoted["attributes"] = {
            **(chosen.get("attributes") or {}),
            "admission_policy_id": "class_os_exact_dual_extraction_agreement_v0_3",
            "corroborating_observation_ids": sorted(
                row["observation_id"] for row in rows
            ),
            "corroborating_methods": sorted(observed_methods),
            "corroboration_scope": "same_primary_source_two_deterministic_extraction_paths",
        }
        admitted.append(promoted)

    readout = {
        "policy_id": "class_os_exact_dual_extraction_agreement_v0_3",
        "candidate_group_count": len(groups),
        "admitted_anchor_count": len(admitted),
        "unadmitted_group_count": len(groups) - len(admitted),
        "status": "PASS_WITH_RESTRICTIONS" if admitted else "FAIL",
        "restriction": "same_source_cross_extraction_not_independent_economic_source",
    }
    return admitted, readout
