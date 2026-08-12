from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.availability import EdgarAvailabilityPolicy  # noqa: E402
from sec_pit.class_os_extract_v2 import (  # noqa: E402
    admit_target_instrument_document,
    extract_cover_page_class_os_v0_2,
    resolve_common_equity_class_candidate,
    strip_instrument_class_suffix,
)
from sec_pit.class_os_reconcile_v2 import reconcile_class_os_anchors_v0_3  # noqa: E402
from sec_pit.ixbrl_class_os_extract_v2 import extract_ixbrl_class_os_v0_2  # noqa: E402

COMMON_PAYLOAD = b"""<html><body>
<xbrli:context id="AsOf2025-11-25"><xbrli:period><xbrli:instant>2025-11-25</xbrli:instant></xbrli:period></xbrli:context>
BRAND ENGAGEMENT NETWORK INC.
Common Stock BNAI The Nasdaq Stock Market LLC
As of November 25, 2025,
<ix:nonFraction name="dei:EntityCommonStockSharesOutstanding" contextRef="AsOf2025-11-25" unitRef="Shares">44,880,795</ix:nonFraction>
shares of the Issuer's common stock, $0.0001 par value per share, were outstanding.
</body></html>"""


CLASS_A_PAYLOAD = b"""<html><body>
<xbrli:context id="c2025-08-13"><xbrli:period><xbrli:instant>2025-08-13</xbrli:instant></xbrli:period></xbrli:context>
PANTAGES CAPITAL ACQUISITION CORPORATION
Class A ordinary shares PGAC The Nasdaq Stock Market LLC
As of August 13, 2025, there were
<ix:nonFraction contextRef="c2025-08-13" name="dei:EntityCommonStockSharesOutstanding" unitRef="shares">8,869,250</ix:nonFraction>
of the registrant's Class A ordinary shares, and 2,156,250 of the registrant's
Class B ordinary shares, issued and outstanding.
</body></html>"""


def kwargs(target_class_label: str) -> dict[str, object]:
    return {
        "cik": "0000000001",
        "accession_number": "a",
        "form": "10-Q",
        "accepted_at": "2025-11-25T20:00:00Z",
        "instrument_id": "instrument",
        "security_class_id": "class",
        "target_class_label": target_class_label,
        "source_url": "https://example.test/a",
        "source_sha256": "h",
        "availability_policy": EdgarAvailabilityPolicy(),
    }


def test_generic_admission_uses_registrant_ticker_and_common_class() -> None:
    decision = admit_target_instrument_document(
        COMMON_PAYLOAD,
        temporal_scope_state="TARGET_INTERVAL",
        accession_link_state="SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
        registrant_name="Brand Engagement Network Inc.",
        ticker="BNAI",
        target_class_label="Common Stock",
    )
    assert decision.decision == "ADMITTED_TARGET_INSTRUMENT_CLASS"


def test_generic_common_equity_candidate_resolves_common_stock() -> None:
    label, decision = resolve_common_equity_class_candidate(
        COMMON_PAYLOAD,
        temporal_scope_state="TARGET_INTERVAL",
        accession_link_state="SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
        registrant_name="Brand Engagement Network Inc.",
        ticker="BNAI",
    )
    assert label == "Common Stock"
    assert decision.decision == "ADMITTED_TARGET_INSTRUMENT_CLASS"


def test_instrument_display_name_suffix_is_not_part_of_registrant_identity() -> None:
    label, decision = resolve_common_equity_class_candidate(
        COMMON_PAYLOAD,
        temporal_scope_state="TARGET_INTERVAL",
        accession_link_state="SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
        registrant_name="Brand Engagement Network Inc. Common Stock",
        ticker="BNAI",
    )
    assert label == "Common Stock"
    assert decision.registrant_match
    assert strip_instrument_class_suffix(
        "Pantages Capital Acquisition Corporation Class A Ordinary Shares"
    ) == "Pantages Capital Acquisition Corporation"


def test_generic_common_equity_candidate_prefers_specific_class() -> None:
    label, decision = resolve_common_equity_class_candidate(
        CLASS_A_PAYLOAD,
        temporal_scope_state="TARGET_INTERVAL",
        accession_link_state="SINGLE_INSTRUMENT_CANDIDATE_NOT_PROVEN",
        registrant_name="Pantages Capital Acquisition Corporation",
        ticker="PGAC",
    )
    assert label == "Class A Ordinary Shares"
    assert decision.decision == "ADMITTED_TARGET_INSTRUMENT_CLASS"


def test_common_stock_text_and_ixbrl_agree() -> None:
    text_rows = extract_cover_page_class_os_v0_2(
        COMMON_PAYLOAD, **kwargs("Common Stock")
    )
    ixbrl_rows = extract_ixbrl_class_os_v0_2(
        COMMON_PAYLOAD, **kwargs("Common Stock")
    )
    assert len(text_rows) == len(ixbrl_rows) == 1
    assert text_rows[0].value == ixbrl_rows[0].value == 44_880_795
    assert text_rows[0].measurement_at == ixbrl_rows[0].measurement_at == "2025-11-25"
    admitted, readout = reconcile_class_os_anchors_v0_3(
        [asdict(row) for row in [*text_rows, *ixbrl_rows]]
    )
    assert len(admitted) == 1
    assert readout["status"] == "PASS_WITH_RESTRICTIONS"


def test_class_a_path_remains_exact_and_excludes_class_b() -> None:
    args = kwargs("Class A ordinary shares")
    text_rows = extract_cover_page_class_os_v0_2(CLASS_A_PAYLOAD, **args)
    ixbrl_rows = extract_ixbrl_class_os_v0_2(CLASS_A_PAYLOAD, **args)
    assert [row.value for row in text_rows] == [8_869_250]
    assert [row.value for row in ixbrl_rows] == [8_869_250]


def test_distinct_issued_and_outstanding_values_selects_outstanding() -> None:
    payload = b"""
    <html><body>
    EXAMPLE ISSUER
    Common Stock TEST The Nasdaq Stock Market LLC
    As of August 8, 2025 there were 15,378,586 shares of the Company's
    common stock issued and 15,318,438 shares outstanding.
    </body></html>
    """
    rows = extract_cover_page_class_os_v0_2(
        payload, **kwargs("Common Stock")
    )
    assert [row.value for row in rows] == [15_318_438]
    assert rows[0].attributes["numeric_selection_state"] == (
        "OUTSTANDING_VALUE_AFTER_DISTINCT_ISSUED_VALUE"
    )


def test_issued_and_outstanding_respectively_selects_outstanding() -> None:
    payload = b"""
    <html><body>
    EXAMPLE ISSUER
    Common Stock TEST The Nasdaq Stock Market LLC
    As of August 13, 2025, the registrant had 4,976,556 and 4,976,555
    shares of common stock, $0.001 par value per share, issued and
    outstanding, respectively.
    </body></html>
    """
    rows = extract_cover_page_class_os_v0_2(payload, **kwargs("Common Stock"))
    assert [row.value for row in rows] == [4_976_555]


def test_number_outstanding_as_of_then_value_is_supported() -> None:
    payload = b"""
    <html><body>
    EXAMPLE ISSUER
    Common Stock TEST The Nasdaq Stock Market LLC
    The number of shares outstanding of the issuer's common stock,
    par value $0.0001 per share, as of May 9, 2023, was 173,983,265.
    </body></html>
    """
    rows = extract_cover_page_class_os_v0_2(payload, **kwargs("Common Stock"))
    assert [row.value for row in rows] == [173_983_265]
    assert rows[0].measurement_at == "2023-05-09"


def test_issuable_under_outstanding_plan_is_not_an_os_anchor() -> None:
    payload = b"""
    <html><body>
    EXAMPLE ISSUER
    Common Stock TEST The Nasdaq Stock Market LLC
    As of June 30, 2025, there were 59 shares of common stock issuable
    under outstanding equity awards.
    </body></html>
    """
    rows = extract_cover_page_class_os_v0_2(payload, **kwargs("Common Stock"))
    assert rows == []


def test_registrant_had_value_outstanding_as_of_is_supported() -> None:
    payload = b"""
    <html><body>
    EXAMPLE ISSUER
    Common Stock TEST The Nasdaq Stock Market LLC
    The Registrant had 199,442,465 shares of common stock outstanding
    as of December 5, 2019.
    </body></html>
    """
    rows = extract_cover_page_class_os_v0_2(payload, **kwargs("Common Stock"))
    assert [row.value for row in rows] == [199_442_465]
    assert rows[0].measurement_at == "2019-12-05"


def test_as_of_then_number_of_outstanding_shares_is_supported() -> None:
    payload = b"""
    <html><body>
    EXAMPLE ISSUER
    Common Stock TEST The Nasdaq Stock Market LLC
    As of February 28, 2018, the number of outstanding shares of the
    registrant's common stock, par value $0.001 per share, was 23,397,497.
    </body></html>
    """
    rows = extract_cover_page_class_os_v0_2(payload, **kwargs("Common Stock"))
    assert [row.value for row in rows] == [23_397_497]
    assert rows[0].measurement_at == "2018-02-28"


def test_prehistory_remains_fail_closed() -> None:
    decision = admit_target_instrument_document(
        COMMON_PAYLOAD,
        temporal_scope_state="OPENING_STATE_PREHISTORY_CANDIDATE",
        accession_link_state="REVIEW_MULTIPLE_INSTRUMENT_CANDIDATES",
        registrant_name="Brand Engagement Network Inc.",
        ticker="BNAI",
        target_class_label="Common Stock",
    )
    assert decision.decision == "REJECT_PREHISTORY_NOT_PROVEN"
