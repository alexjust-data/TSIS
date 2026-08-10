from __future__ import annotations

from typing import Any

CASH_CONCEPTS = (
    "CashAndCashEquivalentsAtCarryingValue",
    "Cash",
)
DEBT_CONCEPTS = (
    "ConvertibleNotesPayable",
    "ShortTermBorrowings",
)
PREFERRED_CONCEPT = "PreferredStockValueOutstanding"


def extract_balance_sheet_facts(
    payload: dict[str, Any],
    eligible_by_accession: dict[str, str],
    minimum_measurement_date: str,
) -> list[dict[str, Any]]:
    concepts = set(CASH_CONCEPTS + DEBT_CONCEPTS + (PREFERRED_CONCEPT,))
    observations: dict[tuple, dict[str, Any]] = {}
    for taxonomy, facts in payload.get("facts", {}).items():
        for concept, fact in facts.items():
            if concept not in concepts:
                continue
            for unit, records in fact.get("units", {}).items():
                if unit != "USD":
                    continue
                for record in records:
                    accession = record.get("accn")
                    measurement = str(record.get("end") or "")[:10]
                    eligible = eligible_by_accession.get(str(accession))
                    if not eligible or measurement < minimum_measurement_date:
                        continue
                    value = record.get("val")
                    if value is None:
                        continue
                    key = (concept, measurement, accession, float(value))
                    observations[key] = {
                        "taxonomy": taxonomy,
                        "concept": concept,
                        "value": float(value),
                        "unit": unit,
                        "measurement_at": measurement,
                        "accession_number": accession,
                        "form": record.get("form"),
                        "filed": record.get("filed"),
                        "eligible_from_session": eligible,
                    }
    return sorted(
        observations.values(),
        key=lambda row: (
            row["eligible_from_session"],
            row["measurement_at"],
            row["concept"],
        ),
    )


def resolve_daily_balance_sheet_context(
    daily_market_cap_rows: list[dict[str, Any]],
    fact_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for source in daily_market_cap_rows:
        row = dict(source)
        session = str(row["session_date"])[:10]
        eligible = [item for item in fact_rows if item["eligible_from_session"] <= session]
        cash_candidates = [item for item in eligible if item["concept"] in CASH_CONCEPTS]
        if not cash_candidates:
            row.update(_unavailable_fields("BALANCE_SHEET_UNAVAILABLE"))
            output.append(row)
            continue
        measurement = max(item["measurement_at"] for item in cash_candidates)
        vintage = [item for item in eligible if item["measurement_at"] == measurement]
        cash = None
        for concept in CASH_CONCEPTS:
            choices = [item for item in vintage if item["concept"] == concept]
            if choices:
                cash = max(choices, key=lambda item: item["eligible_from_session"])
                break
        debt_items = []
        for concept in DEBT_CONCEPTS:
            choices = [item for item in vintage if item["concept"] == concept]
            if choices:
                debt_items.append(max(choices, key=lambda item: item["eligible_from_session"]))
        if cash is None or len(debt_items) != len(DEBT_CONCEPTS):
            row.update(_unavailable_fields("BALANCE_SHEET_COMPONENTS_INCOMPLETE"))
            output.append(row)
            continue
        cash_value = float(cash["value"])
        debt_value = sum(float(item["value"]) for item in debt_items)
        shares = row.get("shares_outstanding_estimate_as_known")
        market_cap = row.get("presession_reference_market_cap_estimate_as_known")
        net_cash = cash_value - debt_value
        row.update(
            {
                "balance_sheet_measurement_at": measurement,
                "balance_sheet_eligible_from_session": max(
                    [cash["eligible_from_session"]]
                    + [item["eligible_from_session"] for item in debt_items]
                ),
                "cash_and_equivalents_as_known": cash_value,
                "reported_debt_components_as_known": debt_value,
                "reported_debt_concepts": list(DEBT_CONCEPTS),
                "net_cash_core_estimate_as_known": net_cash,
                "net_cash_per_share_core_estimate_as_known": (
                    net_cash / float(shares) if shares is not None and float(shares) > 0 else None
                ),
                "enterprise_value_core_estimate_as_known": (
                    float(market_cap) + debt_value - cash_value
                    if market_cap is not None
                    else None
                ),
                "balance_sheet_state": "CORE_EV_ESTIMATED_AS_KNOWN",
            }
        )
        output.append(row)
    calculated = sum(row["balance_sheet_state"] == "CORE_EV_ESTIMATED_AS_KNOWN" for row in output)
    return output, {
        "status": "PASS_WITH_RESTRICTIONS",
        "daily_rows": len(output),
        "core_ev_calculated_rows": calculated,
        "unavailable_rows": len(output) - calculated,
        "ev_scope": "MARKET_CAP_PLUS_TWO_REPORTED_DEBT_CONCEPTS_MINUS_CASH",
    }


def _unavailable_fields(state: str) -> dict[str, Any]:
    return {
        "balance_sheet_measurement_at": None,
        "balance_sheet_eligible_from_session": None,
        "cash_and_equivalents_as_known": None,
        "reported_debt_components_as_known": None,
        "reported_debt_concepts": [],
        "net_cash_core_estimate_as_known": None,
        "net_cash_per_share_core_estimate_as_known": None,
        "enterprise_value_core_estimate_as_known": None,
        "balance_sheet_state": state,
    }
