from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable
from typing import Any


def _person_name_key(value: Any) -> str | None:
    if not value:
        return None
    ignored = {"dr", "mr", "mrs", "ms", "jr", "sr", "ii", "iii", "iv"}
    tokens = re.findall(r"[a-z0-9]+", str(value).lower())
    tokens = [token for token in tokens if token not in ignored and len(token) > 1]
    return " ".join(sorted(tokens)) or None


def _blocked_rows(
    os_rows: list[dict[str, Any]],
    *,
    methodology_id: str,
    blockers: list[str],
) -> list[dict[str, Any]]:
    return [
        {
            "instrument_id": row["instrument_id"],
            "session_date": row["session_date"],
            "shares_outstanding_estimate_as_known": row.get(
                "shares_outstanding_estimate_as_known"
            ),
            "float_owner_exclusion_estimate_as_known": None,
            "float_percent_estimate_as_known": None,
            "unique_supported_excluded_shares": None,
            "methodology_id": methodology_id,
            "ownership_baseline_accession": None,
            "ownership_baseline_eligible_from_session": None,
            "ownership_update_observation_count": 0,
            "ownership_update_latest_transaction_date": None,
            "ownership_conflict_state": None,
            "estimation_state": "BLOCKED_BY_INPUT_GATES",
            "blocker_codes": blockers,
        }
        for row in os_rows
    ]


def _proxy_baselines(
    holders: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in holders:
        if row.get("form") != "DEF 14A" or not row.get("methodology_relevant"):
            continue
        eligible = row.get("eligible_from_session")
        accession = row.get("accession_number")
        if eligible and accession:
            groups[(eligible, accession)].append(row)

    baselines: list[dict[str, Any]] = []
    for (eligible, accession), rows in groups.items():
        if not rows or any(
            row.get("supported_issued_common_shares") is None for row in rows
        ):
            continue
        economic_positions: dict[str, float] = {}
        for row in rows:
            position_id = row.get("economic_position_id") or row.get(
                "holder_position_id"
            )
            value = float(row["supported_issued_common_shares"])
            if position_id in economic_positions and economic_positions[position_id] != value:
                economic_positions = {}
                break
            economic_positions[position_id] = value
        if not economic_positions:
            continue
        conflict_states = sorted({
            str(row["ownership_component_state"])
            for row in rows
            if row.get("ownership_component_state")
            and "CONFLICT" in str(row["ownership_component_state"])
        })
        baselines.append({
            "eligible_from_session": eligible,
            "accession_number": accession,
            "excluded_shares": sum(economic_positions.values()),
            "position_count": len(economic_positions),
            "holder_name_keys": {
                key for key in (_person_name_key(row.get("holder_name")) for row in rows)
                if key
            },
            "conflict_states": conflict_states,
        })
    return sorted(
        baselines,
        key=lambda row: (row["eligible_from_session"], row["accession_number"]),
    )


def _post_baseline_adjustment(
    *,
    holders: list[dict[str, Any]],
    baseline: dict[str, Any],
    session: str,
) -> tuple[float | None, int, str | None, list[str]]:
    events = [
        row for row in holders
        if row.get("methodology_relevant")
        and baseline["eligible_from_session"] < (row.get("eligible_from_session") or "") <= session
        and row.get("form") != "DEF 14A"
    ]
    if not events:
        return 0.0, 0, None, []

    blockers: list[str] = []
    accounts: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in events:
        if row.get("form") not in {"3", "3/A", "4", "4/A", "5", "5/A"}:
            blockers.append("UNSUPPORTED_POST_BASELINE_OWNERSHIP_FORM")
            continue
        if row.get("supported_issued_common_shares") is None:
            blockers.append("POST_BASELINE_ISSUED_COMMON_COMPONENT_UNRESOLVED")
            continue
        holder_key = _person_name_key(row.get("holder_name"))
        if holder_key in baseline["holder_name_keys"]:
            blockers.append("EXISTING_BASELINE_HOLDER_ACCOUNT_SET_INCOMPLETE")
            continue
        if not row.get("canonical_holder_id") or not row.get("transaction_date"):
            blockers.append("POST_BASELINE_EVENT_IDENTITY_OR_DATE_UNRESOLVED")
            continue
        account = (
            str(row["canonical_holder_id"]),
            str(row.get("canonical_holder_group_id") or row.get("direct_or_indirect") or ""),
            str(row.get("security_class_id") or ""),
        )
        order = (
            str(row.get("transaction_date") or ""),
            str(row.get("eligible_from_session") or ""),
            str(row.get("accession_number") or ""),
            int(row.get("holding_sequence") or 0),
        )
        current = accounts.get(account)
        if current is None or order > current["order"]:
            accounts[account] = {"order": order, "row": row}

    if blockers:
        return None, 0, None, sorted(set(blockers))
    selected = [item["row"] for item in accounts.values()]
    adjustment = sum(float(row["supported_issued_common_shares"]) for row in selected)
    latest_transaction = max(
        (str(row["transaction_date"]) for row in selected),
        default=None,
    )
    return adjustment, len(selected), latest_transaction, []


def resolve_owner_exclusion_float(
    *,
    daily_os_rows: Iterable[dict[str, Any]],
    holder_ledger: Iterable[dict[str, Any]],
    ownership_coverage: dict[str, Any],
    holder_deduplication: dict[str, Any],
    methodology_authorized: bool = False,
    methodology_id: str = "officer_director_explicit_affiliate_v0_1",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    os_rows = list(daily_os_rows)
    holders = list(holder_ledger)
    blockers: list[str] = []
    if not ownership_coverage.get("structured_extraction_complete"):
        blockers.append("OWNERSHIP_STRUCTURED_EXTRACTION_INCOMPLETE")
    if not holder_deduplication.get("row_level_economic_position_resolution_complete"):
        blockers.append("ECONOMIC_POSITION_OVERLAP_UNRESOLVED")
    if not methodology_authorized:
        blockers.append("OWNER_EXCLUSION_NOT_AUTHORIZED")

    if blockers:
        rows = _blocked_rows(os_rows, methodology_id=methodology_id, blockers=blockers)
        return rows, {
            "methodology_id": methodology_id,
            "status": "BLOCKED_BY_INPUT_GATES",
            "blocker_codes": blockers,
            "daily_rows": len(rows),
            "non_null_float_rows": 0,
            "holder_rows_considered": len(holders),
            "baseline_count": 0,
        }

    baselines = _proxy_baselines(holders)
    rows: list[dict[str, Any]] = []
    for os_row in os_rows:
        session = os_row["session_date"]
        available = [row for row in baselines if row["eligible_from_session"] <= session]
        baseline = available[-1] if available else None
        state = "CALCULATED"
        row_blockers: list[str] = []
        estimate: float | None = None
        excluded: float | None = None
        conflict_state: str | None = None
        update_count = 0
        update_latest_transaction: str | None = None

        if baseline is None:
            state = "OWNERSHIP_BASELINE_UNAVAILABLE"
            row_blockers.append("OWNERSHIP_BASELINE_UNAVAILABLE")
        else:
            adjustment, update_count, update_latest_transaction, update_blockers = (
                _post_baseline_adjustment(
                    holders=holders,
                    baseline=baseline,
                    session=session,
                )
            )
            if update_blockers:
                state = "POST_BASELINE_OWNERSHIP_EVENT_UNRESOLVED"
                row_blockers.extend(update_blockers)
            elif os_row.get("shares_outstanding_estimate_as_known") is None:
                state = "SHARES_OUTSTANDING_UNAVAILABLE"
                row_blockers.append("SHARES_OUTSTANDING_UNAVAILABLE")
            else:
                excluded = float(baseline["excluded_shares"]) + float(adjustment or 0.0)
                shares = float(os_row["shares_outstanding_estimate_as_known"])
                if excluded > shares:
                    excluded = None
                    state = "EXCLUDED_SHARES_EXCEED_OS"
                    row_blockers.append("EXCLUDED_SHARES_EXCEED_OS")
                else:
                    estimate = shares - excluded
                    if baseline["conflict_states"]:
                        conflict_state = "SOURCE_CONFLICT_PRECEDENCE_APPLIED"
                        state = "CALCULATED_WITH_SOURCE_CONFLICT"
                    if update_count:
                        state += "_AND_TEMPORAL_UPDATE"

        shares = os_row.get("shares_outstanding_estimate_as_known")
        rows.append({
            "instrument_id": os_row["instrument_id"],
            "session_date": session,
            "shares_outstanding_estimate_as_known": shares,
            "float_owner_exclusion_estimate_as_known": estimate,
            "float_percent_estimate_as_known": (
                estimate / float(shares) if estimate is not None and shares else None
            ),
            "unique_supported_excluded_shares": excluded,
            "methodology_id": methodology_id,
            "ownership_baseline_accession": (
                baseline["accession_number"] if baseline else None
            ),
            "ownership_baseline_eligible_from_session": (
                baseline["eligible_from_session"] if baseline else None
            ),
            "ownership_update_observation_count": update_count,
            "ownership_update_latest_transaction_date": update_latest_transaction,
            "ownership_conflict_state": conflict_state,
            "estimation_state": state,
            "blocker_codes": row_blockers,
        })

    non_null = sum(
        row["float_owner_exclusion_estimate_as_known"] is not None for row in rows
    )
    return rows, {
        "methodology_id": methodology_id,
        "status": "PASS_WITH_RESTRICTIONS" if non_null else "BLOCKED_BY_INPUT_GATES",
        "blocker_codes": [],
        "daily_rows": len(rows),
        "non_null_float_rows": non_null,
        "holder_rows_considered": len(holders),
        "baseline_count": len(baselines),
        "post_baseline_temporal_update_resolution_complete": all(
            row["estimation_state"] != "POST_BASELINE_OWNERSHIP_EVENT_UNRESOLVED"
            for row in rows
        ),
        "historical_ownership_coverage_complete": all(
            row["estimation_state"] != "OWNERSHIP_BASELINE_UNAVAILABLE"
            for row in rows
        ),
        "estimation_state_counts": {
            state: sum(row["estimation_state"] == state for row in rows)
            for state in sorted({row["estimation_state"] for row in rows})
        },
    }