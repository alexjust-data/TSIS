from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Iterable
from typing import Any


def _id(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def _attributes(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("attributes")
    return value if isinstance(value, dict) else {}


def reconcile_os_anchors(observations: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Admit only exact cross-extraction agreement for a point O/S fact.

    This v0.1 rule is intentionally narrow. Company Facts and the primary
    filing are two extraction paths to the same accession, not independent
    economic sources.
    """

    rows = list(observations)
    cover_keys: dict[tuple[str, str, float], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("extraction_method") != "COVER_PAGE_TEXT_REGEX_V0_1":
            continue
        if not row.get("accession_number") or not row.get("measurement_at") or row.get("value") is None:
            continue
        cover_keys[(row["accession_number"], row["measurement_at"], float(row["value"]))].append(row)

    admitted: list[dict[str, Any]] = []
    dei_candidates = 0
    for row in rows:
        attributes = _attributes(row)
        if row.get("extraction_method") != "SEC_COMPANYFACTS_XBRL":
            continue
        if attributes.get("taxonomy") != "dei" or attributes.get("concept") != "EntityCommonStockSharesOutstanding":
            continue
        dei_candidates += 1
        if not row.get("accession_number") or not row.get("measurement_at") or row.get("value") is None:
            continue
        key = (row["accession_number"], row["measurement_at"], float(row["value"]))
        corroborating = cover_keys.get(key, [])
        if not corroborating:
            continue
        promoted = dict(row)
        promoted["observation_id"] = _id("admitted_os_anchor_v0_1", *key)
        promoted["quality_state"] = "ADMITTED_OS_ANCHOR"
        promoted["extraction_method"] = "RECONCILED_DEI_AND_PRIMARY_COVER_V0_1"
        promoted["source_excerpt"] = corroborating[0].get("source_excerpt")
        promoted["attributes"] = {
            **attributes,
            "admission_policy_id": "os_anchor_exact_cross_extraction_agreement_v0_1",
            "companyfacts_observation_id": row["observation_id"],
            "cover_observation_ids": sorted(item["observation_id"] for item in corroborating),
            "corroboration_scope": "same_accession_two_extraction_paths",
        }
        admitted.append(promoted)

    unique = {row["observation_id"]: row for row in admitted}
    result = list(unique.values())
    readout = {
        "policy_id": "os_anchor_exact_cross_extraction_agreement_v0_1",
        "dei_point_candidates": dei_candidates,
        "admitted_anchor_count": len(result),
        "admission_rate": len(result) / dei_candidates if dei_candidates else 0.0,
        "unadmitted_dei_candidates": dei_candidates - len(result),
        "status": "PASS_WITH_RESTRICTIONS" if result else "FAIL",
    }
    return result, readout

