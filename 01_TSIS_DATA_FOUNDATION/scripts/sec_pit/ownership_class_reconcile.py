from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any, Iterable

from sec_pit.extract import stable_id
from sec_pit.ownership_v2 import normalized_name_key


def _class_key(value: Any) -> str | None:
    if not value:
        return None
    text = str(value).lower()
    if "class a" in text and ("ordinary" in text or "common" in text):
        return "CLASS_A_COMMON_OR_ORDINARY"
    if "class b" in text and ("ordinary" in text or "common" in text):
        return "CLASS_B_COMMON_OR_ORDINARY"
    if "common" in text or "ordinary" in text:
        return "UNNUMBERED_COMMON_OR_ORDINARY"
    return None


def _names_compatible(left: Any, right: Any) -> bool:
    left_key = normalized_name_key(left)
    right_key = normalized_name_key(right)
    if not left_key or not right_key:
        return False
    if left_key == right_key:
        return True
    entity_markers = {"llc", "lp", "plc", "bank", "holdings", "management", "capital"}
    left_tokens = set(left_key.split())
    right_tokens = set(right_key.split())
    if left_tokens & entity_markers or right_tokens & entity_markers:
        return False
    return len(left_tokens & right_tokens) >= 2


def reconcile_multiclass_proxy_positions(
    *,
    proxy_observations: Iterable[dict[str, Any]],
    class_components: Iterable[dict[str, Any]],
    target_class_label: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    target_class_key = _class_key(target_class_label)
    if target_class_key is None:
        raise ValueError(f"unsupported target class label: {target_class_label}")

    proxies = [deepcopy(row) for row in proxy_observations]
    components = list(class_components)
    by_holder: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for component in components:
        key = component.get("holder_name_key") or normalized_name_key(
            component.get("holder_name")
        )
        if key and component.get("shares") is not None:
            by_holder[str(key)].append(component)

    resolved: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    aggregate_rows = 0
    aggregate_pending: list[dict[str, Any]] = []
    aggregate_unresolved = 0
    explicit_affiliate_rows = 0
    target_supported_total = 0.0

    for row in proxies:
        attributes = row.get("attributes") or {}
        category = attributes.get("holder_category")
        if category == "AGGREGATE_GROUP":
            aggregate_rows += 1
            reported_components = attributes.get("reported_class_components") or []
            component_total = sum(
                float(item.get("shares") or 0.0) for item in reported_components
            )
            if reported_components and component_total == float(row.get("value") or 0.0):
                target_shares = sum(
                    float(item.get("shares") or 0.0)
                    for item in reported_components
                    if _class_key(item.get("security_class_title")) == target_class_key
                )
                attributes["supported_issued_common_shares"] = target_shares
                attributes["ownership_component_state"] = (
                    "EXACT_REPORTED_CLASS_MANAGEMENT_AGGREGATE_RESOLVED"
                )
                attributes["target_class_key"] = target_class_key
                row["quality_state"] = "ADMITTED_MANAGEMENT_AGGREGATE"
                row["attributes"] = attributes
                target_supported_total += target_shares
                resolved.append(row)
                continue
            supported_single_class = attributes.get("supported_issued_common_shares")
            if (
                target_class_key == "UNNUMBERED_COMMON_OR_ORDINARY"
                and supported_single_class is not None
                and attributes.get("table_class_basis") == "SINGLE_OR_UNSPECIFIED"
            ):
                attributes["supported_issued_common_shares"] = float(supported_single_class)
                attributes["ownership_component_state"] = (
                    "SINGLE_CLASS_MANAGEMENT_AGGREGATE_RESOLVED"
                )
                row["quality_state"] = "ADMITTED_MANAGEMENT_AGGREGATE"
            else:
                attributes["supported_issued_common_shares"] = None
                attributes["ownership_component_state"] = (
                    "MULTI_CLASS_MANAGEMENT_AGGREGATE_PENDING"
                )
                row["quality_state"] = "PENDING_MANAGEMENT_AGGREGATE_CLASS_SUM"
                aggregate_pending.append(row)
            row["attributes"] = attributes
            resolved.append(row)
            continue

        supported_single_class = attributes.get("supported_issued_common_shares")
        if (
            target_class_key == "UNNUMBERED_COMMON_OR_ORDINARY"
            and supported_single_class is not None
            and attributes.get("table_class_basis") == "SINGLE_OR_UNSPECIFIED"
            and _class_key(attributes.get("security_title"))
            == "UNNUMBERED_COMMON_OR_ORDINARY"
        ):
            target_shares = float(supported_single_class)
            attributes["ownership_component_state"] = (
                "SINGLE_CLASS_PROXY_POSITION_RESOLVED"
            )
            attributes["target_class_key"] = target_class_key
            if attributes.get("explicit_affiliate_candidate"):
                attributes["holder_category"] = "EXPLICIT_AFFILIATE"
                attributes["explicit_affiliate_supported"] = True
                explicit_affiliate_rows += 1
            row["quality_state"] = "ADMITTED_SINGLE_CLASS_PROXY_POSITION"
            row["attributes"] = attributes
            row["observation_id"] = stable_id(
                "reconciled_single_class_proxy_position_v0_2",
                row.get("observation_id"),
                target_class_key,
                target_shares,
            )
            target_supported_total += target_shares
            resolved.append(row)
            continue
        holder_name = attributes.get("holder_name")
        holder_key = normalized_name_key(holder_name)
        candidates = by_holder.get(holder_key or "", [])
        if not candidates:
            candidates = [
                component
                for component in components
                if _names_compatible(holder_name, component.get("holder_name"))
            ]
        if row.get("eligible_from_session"):
            candidates = [
                item
                for item in candidates
                if not item.get("eligible_from_session")
                or item["eligible_from_session"] <= row["eligible_from_session"]
            ]
        latest_by_class: dict[str, dict[str, Any]] = {}
        for component in candidates:
            class_key = _class_key(component.get("security_class_title"))
            if class_key is None:
                continue
            current = latest_by_class.get(class_key)
            order = (
                str(component.get("eligible_from_session") or ""),
                str(component.get("source_accession") or ""),
                str(component.get("component_id") or ""),
            )
            if current is None or order > current["_order"]:
                latest_by_class[class_key] = {**component, "_order": order}

        allocated = sum(float(item["shares"]) for item in latest_by_class.values())
        reported = float(row.get("value") or 0.0)
        if not latest_by_class or allocated != reported:
            attributes["supported_issued_common_shares"] = None
            attributes["ownership_component_state"] = (
                "MULTI_CLASS_ALLOCATION_UNRESOLVED"
            )
            attributes["class_component_ids"] = sorted(
                str(item.get("component_id")) for item in latest_by_class.values()
            )
            row["quality_state"] = "BLOCKED_MULTI_CLASS_ALLOCATION"
            row["attributes"] = attributes
            unresolved.append(row)
            resolved.append(row)
            continue

        target_shares = float(
            latest_by_class.get(target_class_key, {}).get("shares", 0.0)
        )
        attributes["supported_issued_common_shares"] = target_shares
        attributes["ownership_component_state"] = "EXACT_MULTI_CLASS_ALLOCATION_RESOLVED"
        attributes["class_component_ids"] = sorted(
            str(item["component_id"]) for item in latest_by_class.values()
        )
        attributes["class_component_total"] = allocated
        attributes["target_class_key"] = target_class_key
        if attributes.get("explicit_affiliate_candidate"):
            attributes["holder_category"] = "EXPLICIT_AFFILIATE"
            attributes["explicit_affiliate_supported"] = True
            explicit_affiliate_rows += 1
        row["quality_state"] = "ADMITTED_EXACT_CLASS_COMPONENT"
        row["attributes"] = attributes
        row["observation_id"] = stable_id(
            "reconciled_multiclass_proxy_position_v0_1",
            row.get("observation_id"),
            target_class_key,
            target_shares,
        )
        target_supported_total += target_shares
        resolved.append(row)

    for aggregate in aggregate_pending:
        atomic = [
            row
            for row in resolved
            if row is not aggregate
            and row.get("accession_number") == aggregate.get("accession_number")
            and (row.get("attributes") or {}).get("holder_category")
            == "OFFICER_OR_DIRECTOR"
        ]
        reported_sum = sum(float(row.get("value") or 0.0) for row in atomic)
        supported_values = [
            (row.get("attributes") or {}).get("supported_issued_common_shares")
            for row in atomic
        ]
        if (
            atomic
            and reported_sum == float(aggregate.get("value") or 0.0)
            and all(value is not None for value in supported_values)
        ):
            aggregate["attributes"]["supported_issued_common_shares"] = sum(
                float(value) for value in supported_values
            )
            aggregate["attributes"]["ownership_component_state"] = (
                "EXACT_MULTI_CLASS_MANAGEMENT_AGGREGATE_RESOLVED"
            )
            aggregate["quality_state"] = "ADMITTED_MANAGEMENT_AGGREGATE"
        else:
            aggregate["attributes"]["ownership_component_state"] = (
                "MULTI_CLASS_MANAGEMENT_AGGREGATE_UNRESOLVED"
            )
            aggregate["quality_state"] = (
                "BLOCKED_MULTI_CLASS_MANAGEMENT_AGGREGATE"
            )
            aggregate_unresolved += 1

    readout = {
        "policy_id": "exact_multiclass_holder_component_reconciliation_v0_2",
        "target_class_key": target_class_key,
        "proxy_position_rows": len(proxies),
        "class_component_rows": len(components),
        "aggregate_management_rows": aggregate_rows,
        "unresolved_aggregate_group_rows": aggregate_unresolved,
        "explicit_affiliate_rows": explicit_affiliate_rows,
        "unresolved_atomic_position_rows": len(unresolved),
        "target_supported_excluded_share_candidates": target_supported_total,
        "row_level_class_allocation_complete": len(unresolved) == 0 and aggregate_unresolved == 0,
        "status": (
            "PASS_WITH_RESTRICTIONS"
            if proxies and not unresolved and aggregate_unresolved == 0
            else "FAIL"
        ),
    }
    return resolved, readout

