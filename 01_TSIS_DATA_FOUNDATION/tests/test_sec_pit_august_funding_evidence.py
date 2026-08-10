from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.august_funding_evidence import extract_august_funding_evidence  # noqa: E402


def test_two_share_contract_resolves_reported_aggregate() -> None:
    payload = b"""<p>For every $5.00 paid to the Company, the Company will release one share
    of Common Stock under the August SPA and one share of Common Stock under the Assignment Agreement.
    As of November 13, 2024, a total of 220,000 shares of Common Stock have been issued to the August
    Purchasers for gross proceeds of $550,000. Certain investors have failed to make their required
    fundings, giving effect to all cure periods, in an aggregate amount of $1.25 million.</p>"""
    rows, readout = extract_august_funding_evidence(payload)
    aggregate = rows[0]
    assert aggregate["spa_shares_supported"] == 110_000
    assert aggregate["sponsor_shares_supported"] == 110_000
    assert rows[1]["failed_funding_amount_reported"] == 1_250_000
    assert readout["tradable_supply_confirmed_rows"] == 0
