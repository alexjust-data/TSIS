from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.assignment_schedule_link import (  # noqa: E402
    extract_assignment_purchaser_schedule,
    link_schedule_to_selling_lots,
)


def test_schedule_preserves_and_resolves_reported_typo() -> None:
    payload = b"""<table><tr><th></th><th></th><th></th><th></th><th></th><th></th><th>Purchaser Party</th><th></th><th>Shares Received</th><th></th></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td><td>Joe Bevash</td><td></td><td></td><td>120000</td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td><td>BEN Capital Fund I LLC</td><td></td><td></td><td>2000000</td></tr>
    <tr><td></td><td></td><td></td><td></td><td></td><td></td><td>Total</td><td></td><td></td><td>320000</td></tr></table>"""
    rows, readout = extract_assignment_purchaser_schedule(payload)
    assert readout["raw_sum"] == 2_120_000
    assert readout["resolved_sum"] == 320_000
    assert rows[1]["shares_reported"] == 2_000_000
    assert rows[1]["shares_resolved"] == 200_000


def test_link_requires_identity_and_quantity() -> None:
    schedule = [{"holder_name_key": "joseph bevash", "shares_resolved": 120_000}]
    lots = [
        {
            "observation_id": "x",
            "attributes": {
                "file_number": "333-282130",
                "holder_name": "Joseph Bevash",
                "maximum_common_shares_offered": 120_000,
            },
        }
    ]
    links, readout = link_schedule_to_selling_lots(schedule, lots)
    assert links[0]["link_state"] == "IDENTITY_AND_QUANTITY_LINKED"
    assert links[0]["tradable_supply_confirmation"] is False
    assert readout["tradable_supply_confirmed_rows"] == 0
