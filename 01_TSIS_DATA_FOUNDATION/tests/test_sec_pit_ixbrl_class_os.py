from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.class_os_extract import extract_cover_page_class_os  # noqa: E402
from sec_pit.class_os_reconcile import reconcile_class_os_anchors  # noqa: E402
from sec_pit.ixbrl_class_os_extract import extract_ixbrl_class_os  # noqa: E402


PAYLOAD = b"""<html><body>As of August 13, 2025, there were
<ix:nonFraction contextRef="c4" decimals="INF"
name="dei:EntityCommonStockSharesOutstanding" unitRef="shares">8,869,250</ix:nonFraction>
of the registrant&#8217;s Class A ordinary shares, par value $0.0001 per share, and
<ix:nonFraction contextRef="c5" decimals="INF"
name="dei:EntityCommonStockSharesOutstanding" unitRef="shares">2,156,250</ix:nonFraction>
of the registrant&#8217;s Class B ordinary shares, issued and outstanding.</body></html>"""


def kwargs() -> dict[str, object]:
    return {
        "cik": "0002030829",
        "accession_number": "a",
        "form": "10-Q",
        "accepted_at": "2025-08-13T22:20:04.000Z",
        "instrument_id": "cik_ticker:0002030829:PGAC",
        "security_class_id": None,
        "target_class_label": "Class A ordinary shares",
        "source_url": "x",
        "source_sha256": "h",
        "availability_policy": EdgarAvailabilityPolicy(),
    }


def test_ixbrl_class_extraction_selects_class_a_context() -> None:
    rows = extract_ixbrl_class_os(PAYLOAD, **kwargs())
    assert len(rows) == 1
    assert rows[0].value == 8_869_250
    assert rows[0].measurement_at == "2025-08-13"
    assert rows[0].eligible_from_session == "2025-08-14"


def test_dual_extraction_agreement_admits_class_anchor() -> None:
    text_rows = extract_cover_page_class_os(PAYLOAD, **kwargs())
    ixbrl_rows = extract_ixbrl_class_os(PAYLOAD, **kwargs())
    admitted, readout = reconcile_class_os_anchors(
        [asdict(row) for row in [*text_rows, *ixbrl_rows]]
    )
    assert len(admitted) == 1
    assert admitted[0]["value"] == 8_869_250
    assert admitted[0]["quality_state"] == "ADMITTED_OS_ANCHOR"
    assert readout["status"] == "PASS_WITH_RESTRICTIONS"
