from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.balance_sheet_context import (  # noqa: E402
    extract_balance_sheet_facts,
    resolve_daily_balance_sheet_context,
)


def test_extraction_rejects_pre_instrument_facts() -> None:
    payload = {
        "facts": {
            "us-gaap": {
                "Cash": {
                    "units": {
                        "USD": [
                            {"end": "2023-12-31", "val": 1, "accn": "old"},
                            {"end": "2024-03-31", "val": 2, "accn": "new"},
                        ]
                    }
                }
            }
        }
    }
    rows = extract_balance_sheet_facts(
        payload, {"old": "2024-04-01", "new": "2024-05-15"}, "2024-03-15"
    )
    assert len(rows) == 1
    assert rows[0]["value"] == 2


def test_daily_resolver_is_causal_and_uses_same_measurement_vintage() -> None:
    facts = [
        {
            "concept": "CashAndCashEquivalentsAtCarryingValue",
            "value": 100,
            "measurement_at": "2024-03-31",
            "eligible_from_session": "2024-05-15",
        },
        {
            "concept": "ConvertibleNotesPayable",
            "value": 20,
            "measurement_at": "2024-03-31",
            "eligible_from_session": "2024-05-15",
        },
        {
            "concept": "ShortTermBorrowings",
            "value": 30,
            "measurement_at": "2024-03-31",
            "eligible_from_session": "2024-05-15",
        },
    ]
    daily = [
        {
            "session_date": "2024-05-14",
            "shares_outstanding_estimate_as_known": 10,
            "presession_reference_market_cap_estimate_as_known": 1_000,
        },
        {
            "session_date": "2024-05-15",
            "shares_outstanding_estimate_as_known": 10,
            "presession_reference_market_cap_estimate_as_known": 1_000,
        },
    ]
    rows, readout = resolve_daily_balance_sheet_context(daily, facts)
    assert rows[0]["balance_sheet_state"] == "BALANCE_SHEET_UNAVAILABLE"
    assert rows[1]["enterprise_value_core_estimate_as_known"] == 950
    assert rows[1]["net_cash_per_share_core_estimate_as_known"] == 5
    assert readout["core_ev_calculated_rows"] == 1
