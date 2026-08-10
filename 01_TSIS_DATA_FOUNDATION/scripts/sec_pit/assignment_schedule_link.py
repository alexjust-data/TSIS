from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd

from sec_pit.extract import stable_id

NAME_ALIASES = {
    "joe bevash": "joseph bevash",
    "due figlie": "due figlie llc",
    "lucas venture partners": "lucas venture partners llc",
}


def _name(value: Any) -> str:
    normalized = " ".join(str(value).replace(",", " ").lower().split())
    return NAME_ALIASES.get(normalized, normalized)


def _number(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def extract_assignment_purchaser_schedule(
    payload: bytes,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    schedule = None
    for table in pd.read_html(BytesIO(payload)):
        rendered = (
            " ".join(map(str, table.columns))
            + " "
            + " ".join(table.astype(str).fillna("").to_numpy().ravel())
        )
        if "Purchaser Party" in rendered and "Shares Received" in rendered:
            schedule = table
            break
    if schedule is None:
        return [], {"status": "NOT_OBSERVABLE", "reason": "PURCHASER_SCHEDULE_NOT_FOUND"}

    holder_column = next(
        column
        for column in schedule.columns
        if "purchaser party" in str(column).lower()
        or schedule[column].astype(str).str.contains("Purchaser Party", case=False).any()
    )
    candidate_share_columns = [
        column
        for column in schedule.columns
        if column != holder_column and schedule[column].map(_number).notna().sum() > 0
    ]
    shares_column = max(
        candidate_share_columns,
        key=lambda column: schedule[column].map(_number).notna().sum(),
    )

    rows: list[dict[str, Any]] = []
    reported_total = None
    for _, row in schedule.iterrows():
        holder = row[holder_column]
        shares = _number(row[shares_column])
        if str(holder).strip().lower() == "total":
            reported_total = shares
        elif shares is not None and str(holder).lower() != "nan":
            rows.append(
                {
                    "holder_name_reported": str(holder).strip(),
                    "holder_name_key": _name(holder),
                    "shares_reported": shares,
                }
            )

    raw_sum = sum(row["shares_reported"] for row in rows)
    conflict_rows = []
    if reported_total is not None and raw_sum != reported_total:
        delta = raw_sum - reported_total
        for row in rows:
            if row["shares_reported"] > reported_total:
                row["shares_resolved"] = row["shares_reported"] - delta
                row["quality_state"] = "SOURCE_NUMERIC_CONFLICT_RESOLVED_BY_REPORTED_TOTAL"
                conflict_rows.append(row["holder_name_key"])
            else:
                row["shares_resolved"] = row["shares_reported"]
                row["quality_state"] = "REPORTED"
    else:
        for row in rows:
            row["shares_resolved"] = row["shares_reported"]
            row["quality_state"] = "REPORTED"

    resolved_sum = sum(row["shares_resolved"] for row in rows)
    return rows, {
        "status": "PASS_WITH_RESTRICTIONS" if conflict_rows else "PASS",
        "purchaser_rows": len(rows),
        "raw_sum": raw_sum,
        "reported_total": reported_total,
        "resolved_sum": resolved_sum,
        "source_numeric_conflict_holders": conflict_rows,
    }


def link_schedule_to_selling_lots(
    schedule_rows: list[dict[str, Any]], selling_lots: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lots = {
        _name((row.get("attributes") or {}).get("holder_name")): row
        for row in selling_lots
        if (row.get("attributes") or {}).get("file_number") == "333-282130"
    }
    links = []
    for schedule in schedule_rows:
        lot = lots.get(schedule["holder_name_key"])
        lot_shares = (
            (lot.get("attributes") or {}).get("maximum_common_shares_offered") if lot else None
        )
        exact = lot is not None and float(lot_shares) == float(schedule["shares_resolved"])
        links.append(
            {
                **schedule,
                "link_id": stable_id(
                    "assignment_schedule_selling_lot_link_v0_1", schedule["holder_name_key"]
                ),
                "selling_lot_observation_id": lot.get("observation_id") if lot else None,
                "selling_lot_shares": lot_shares,
                "link_state": "IDENTITY_AND_QUANTITY_LINKED" if exact else "UNRESOLVED",
                "tradable_supply_confirmation": False,
            }
        )
    linked = sum(row["link_state"] == "IDENTITY_AND_QUANTITY_LINKED" for row in links)
    return links, {
        "status": "PASS_WITH_RESTRICTIONS" if linked == len(links) else "BLOCKED_BY_INPUT_GATES",
        "schedule_rows": len(links),
        "identity_and_quantity_linked_rows": linked,
        "tradable_supply_confirmed_rows": 0,
    }
