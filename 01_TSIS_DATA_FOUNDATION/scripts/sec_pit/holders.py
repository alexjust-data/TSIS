from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Iterable
from typing import Any


def _id(*parts: Any) -> str:
    return hashlib.sha256(
        "|".join("" if part is None else str(part) for part in parts).encode("utf-8")
    ).hexdigest()


def _normalized_name(value: Any) -> str | None:
    if not value:
        return None
    normalized = re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()
    return normalized or None


def _controlled_entity_name(row: dict[str, Any]) -> str | None:
    nature = str(row.get("nature_of_ownership") or "").strip()
    if nature and nature.lower() not in {"see footnote", "see footnotes"}:
        return re.sub(r"^By\s+", "", nature, flags=re.I).strip() or None
    for footnote in row.get("footnote_texts") or []:
        match = re.search(
            r"beneficially owned by\s+(.+?)(?=\s+\(the\b|\.\s+The Reporting Person)",
            str(footnote),
            re.I,
        )
        if match:
            return match.group(1).strip()
    return None

def _methodology_relevant(row: dict[str, Any]) -> bool:
    if row["holding_type"] == "DERIVATIVE" or row["reported_shares"] == 0:
        return False
    if row["holder_category"] in {"AGGREGATE_GROUP", "FIVE_PERCENT_HOLDER"}:
        return False
    if row["form"] in {"SC 13G", "SC 13G/A", "SCHEDULE 13G", "SCHEDULE 13G/A"}:
        return False
    return bool(
        row["holder_category"] == "OFFICER_OR_DIRECTOR"
        or row["holder_category"] == "EXPLICIT_AFFILIATE"
        or row["owner_is_director"]
        or row["owner_is_officer"]
    )


def build_holder_position_ledger(
    observations: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_rows = [
        row for row in observations
        if row.get("observation_type") == "HOLDER_POSITION_SNAPSHOT"
    ]
    ledger: dict[str, dict[str, Any]] = {}
    missing_holder_id = 0
    name_only_identity_rows = 0
    indirect_rows = 0
    derivative_rows = 0

    for row in source_rows:
        attributes = row.get("attributes") if isinstance(row.get("attributes"), dict) else {}
        holder_cik = attributes.get("holder_cik")
        holder_name = attributes.get("holder_name")
        normalized_name = _normalized_name(holder_name)
        if holder_cik:
            canonical_holder_id = f"sec_cik:{str(holder_cik).zfill(10)}"
            identity_state = "SEC_CIK_RESOLVED"
            holder_source_identity = canonical_holder_id
        elif normalized_name:
            canonical_holder_id = f"sec_name_candidate:{_id(normalized_name)[:24]}"
            identity_state = "NAME_ONLY_REQUIRES_ENTITY_RESOLUTION"
            holder_source_identity = f"name:{normalized_name}"
            name_only_identity_rows += 1
        else:
            canonical_holder_id = None
            identity_state = "IDENTITY_MISSING"
            holder_source_identity = None
            missing_holder_id += 1

        direct_or_indirect = attributes.get("direct_or_indirect")
        holding_type = attributes.get("holding_type")
        if direct_or_indirect == "I":
            indirect_rows += 1
        if holding_type == "DERIVATIVE":
            derivative_rows += 1

        position_id = _id(
            "holder_position_v0_3",
            holder_source_identity,
            row.get("accession_number"),
            holding_type,
            direct_or_indirect,
            attributes.get("security_title"),
            row.get("value"),
            attributes.get("reported_percent"),
            attributes.get("holder_category"),
        )
        ledger[position_id] = {
            "holder_position_id": position_id,
            "canonical_holder_id": canonical_holder_id,
            "holder_identity_state": identity_state,
            "canonical_holder_group_id": None,
            "economic_position_id": None,
            "overlap_group_id": None,
            "instrument_id": row.get("instrument_id"),
            "security_class_id": row.get("security_class_id"),
            "accession_number": row.get("accession_number"),
            "form": row.get("form"),
            "holder_name": holder_name,
            "holding_type": holding_type,
            "direct_or_indirect": direct_or_indirect,
            "security_title": attributes.get("security_title"),
            "nature_of_ownership": attributes.get("nature_of_ownership"),
            "footnote_texts": attributes.get("footnote_texts") or [],
            "period_of_report": attributes.get("period_of_report"),
            "transaction_date": attributes.get("transaction_date"),
            "transaction_code": attributes.get("transaction_code"),
            "transaction_acquired_disposed_code": attributes.get(
                "transaction_acquired_disposed_code"
            ),
            "transaction_shares": attributes.get("transaction_shares"),
            "holding_sequence": attributes.get("holding_sequence"),
            "supported_issued_common_shares": attributes.get(
                "supported_issued_common_shares"
            ),
            "ownership_component_state": attributes.get("ownership_component_state"),
            "reported_shares": row.get("value"),
            "reported_percent": attributes.get("reported_percent"),
            "holder_category": attributes.get("holder_category"),
            "owner_is_director": bool(attributes.get("owner_is_director")),
            "owner_is_officer": bool(attributes.get("owner_is_officer")),
            "owner_is_ten_percent": bool(attributes.get("owner_is_ten_percent")),
            "owner_officer_title": attributes.get("owner_officer_title"),
            "eligible_from_session": row.get("eligible_from_session"),
            "source_observation_id": row.get("observation_id"),
            "source_sha256": row.get("source_sha256"),
            "source_quality_state": row.get("quality_state"),
            "methodology_relevant": False,
            "deduplication_state": "UNCLASSIFIED",
            "owner_exclusion_eligible": False,
        }

    rows = sorted(
        ledger.values(),
        key=lambda row: (row.get("eligible_from_session") or "", row["holder_position_id"]),
    )
    schedule_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        row["methodology_relevant"] = _methodology_relevant(row)
        if row["holder_category"] == "SCHEDULE_REPORTING_PERSON":
            schedule_groups[(
                row["accession_number"],
                row["security_class_id"],
                row["reported_shares"],
            )].append(row)

    joint_rows = 0
    for key, group in schedule_groups.items():
        if len(group) < 2:
            continue
        economic_position_id = _id("joint_schedule_position_v0_1", *key)
        overlap_group_id = _id("joint_schedule_group_v0_1", *key)
        for row in group:
            row["economic_position_id"] = economic_position_id
            row["overlap_group_id"] = overlap_group_id
            row["deduplication_state"] = "JOINT_REPORTING_POSITION_RESOLVED"
            joint_rows += 1

    non_additive_group_rows = 0
    out_of_methodology_rows = 0
    zero_position_rows = 0
    unresolved_relevant_rows = 0
    for row in rows:
        if row["deduplication_state"] == "JOINT_REPORTING_POSITION_RESOLVED":
            continue
        if row["reported_shares"] == 0:
            row["deduplication_state"] = "ZERO_POSITION_RESOLVED"
            row["economic_position_id"] = _id(
                "zero_position_v0_1", row["canonical_holder_id"], row["accession_number"]
            )
            zero_position_rows += 1
        elif row["holding_type"] == "DERIVATIVE":
            row["deduplication_state"] = "DERIVATIVE_OUT_OF_METHODOLOGY"
            out_of_methodology_rows += 1
        elif row["holder_category"] == "AGGREGATE_GROUP":
            row["deduplication_state"] = "NON_ADDITIVE_AGGREGATE_GROUP"
            non_additive_group_rows += 1
        elif not row["methodology_relevant"]:
            row["deduplication_state"] = "OUT_OF_METHODOLOGY_SCOPE"
            out_of_methodology_rows += 1
        elif row["supported_issued_common_shares"] is None:
            row["deduplication_state"] = "RELEVANT_ISSUED_COMMON_COMPONENT_UNRESOLVED"
            unresolved_relevant_rows += 1
        elif row["direct_or_indirect"] == "I":
            controlled_entity = _controlled_entity_name(row)
            if not controlled_entity:
                row["deduplication_state"] = "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED"
                unresolved_relevant_rows += 1
            else:
                controlled_name = _normalized_name(controlled_entity)
                row["canonical_holder_group_id"] = (
                    f"controlled_entity_name:{_id(controlled_name)[:24]}"
                )
                row["economic_position_id"] = _id(
                    "controlled_entity_position_v0_2",
                    row["instrument_id"],
                    row["security_class_id"],
                    controlled_name,
                    row["eligible_from_session"],
                    row["supported_issued_common_shares"],
                )
                row["deduplication_state"] = "INDIRECT_CONTROLLED_ENTITY_RESOLVED"
        elif row["holder_identity_state"] != "SEC_CIK_RESOLVED":
            row["deduplication_state"] = "SOURCE_DOCUMENT_NAME_ID_RESOLVED"
            row["economic_position_id"] = _id(
                "source_name_position_v0_1",
                row["instrument_id"],
                row["accession_number"],
                _normalized_name(row["holder_name"]),
            )
        else:
            row["deduplication_state"] = "EXACT_POSITION_ID_RESOLVED"
            row["economic_position_id"] = _id(
                "exact_economic_position_v0_1", row["holder_position_id"]
            )

    unresolved_states = {
        "RELEVANT_NAME_IDENTITY_UNRESOLVED",
        "RELEVANT_INDIRECT_RELATIONSHIP_UNRESOLVED",
        "RELEVANT_FOOTNOTE_UNRESOLVED",
        "RELEVANT_ISSUED_COMMON_COMPONENT_UNRESOLVED",
    }
    unresolved_relevant_rows = sum(
        row["deduplication_state"] in unresolved_states for row in rows
    )
    readout = {
        "policy_id": "holder_methodology_scoped_economic_position_resolution_v0_7",
        "source_position_rows": len(source_rows),
        "deduplicated_position_rows": len(rows),
        "exact_duplicate_rows_removed": len(source_rows) - len(rows),
        "unique_holder_count": len({
            row["canonical_holder_id"] for row in rows if row["canonical_holder_id"]
        }),
        "missing_holder_identity_rows": missing_holder_id,
        "name_only_identity_rows": name_only_identity_rows,
        "raw_indirect_rows": indirect_rows,
        "indirect_overlap_unresolved_rows": indirect_rows,
        "footnote_or_overlap_unresolved_rows": sum(
            row["source_quality_state"]
            == "CANDIDATE_REQUIRES_FOOTNOTE_AND_OVERLAP_RESOLUTION"
            for row in rows
        ),
        "derivative_rows": derivative_rows,
        "joint_reporting_rows_resolved": joint_rows,
        "non_additive_group_rows": non_additive_group_rows,
        "zero_position_rows": zero_position_rows,
        "out_of_methodology_rows": out_of_methodology_rows,
        "unresolved_methodology_relevant_rows": unresolved_relevant_rows,
        "row_level_economic_position_resolution_complete": unresolved_relevant_rows == 0,
        "temporal_position_resolution_complete": None,
        "temporal_position_resolution_authority": "DAILY_FLOAT_RESOLVER",
        "economic_position_resolution_complete": False,
        "owner_exclusion_authorized": False,
        "status": "PASS_WITH_RESTRICTIONS" if rows and missing_holder_id == 0 else "FAIL",
    }
    return rows, readout
