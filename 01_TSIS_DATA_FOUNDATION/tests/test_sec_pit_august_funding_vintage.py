from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.august_funding_vintage import (  # noqa: E402
    extract_august_funding_vintages,
    reconcile_august_funding_vintages,
)


def _extract(payload: bytes, accession: str = "a") -> list[dict]:
    return extract_august_funding_vintages(
        payload,
        accession_number=accession,
        form="10-Q",
        filing_accepted_at="2025-06-04T22:03:14Z",
        eligible_from_session="2025-06-05",
        source_sha256="h",
    )


def test_extracts_separate_vintage_semantics() -> None:
    rows = _extract(
        b"""<p>As of September 13, 2024, 50,000 shares of Common Stock have been released
        from escrow upon payment by the August Purchasers.</p><p>As of March 31, 2025, the August
        SPA has been terminated with respect to certain August Purchasers who exercised warrants.</p>"""
    )
    assert rows[0]["lot_attribution_state"] == "UNATTRIBUTED_ESCROW_LOT"
    assert rows[1]["termination_scope"] == "CERTAIN_PURCHASERS_UNIDENTIFIED"
    assert all(row["tradable_supply_confirmation"] is False for row in rows)


def test_reconciliation_keeps_first_public_vintage() -> None:
    payload = b"<p>As of March 31, 2025, the August SPA has been terminated with respect to certain August Purchasers.</p>"
    rows = _extract(payload, "later") + _extract(payload, "earlier")
    rows[1]["filing_accepted_at"] = "2025-04-01T00:00:00Z"
    reconciled, readout = reconcile_august_funding_vintages(rows)
    assert reconciled[0]["accession_number"] == "earlier"
    assert reconciled[0]["corroboration_count"] == 2
    assert readout["tradable_supply_confirmed_rows"] == 0
