from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.ownership_identity import (  # noqa: E402
    ADMITTED_IDENTITY_STATE,
    REJECTED_ISSUER_STATE,
    REJECTED_SECURITY_STATE,
    UNRESOLVED_IDENTITY_STATE,
    decide_document_identity,
    is_common_equity_title,
)


def _decision(**overrides: object) -> tuple[str, str | None]:
    values = {
        "interval_resolution_allowed": True,
        "target_cik": "0001210618",
        "issuer_cik": "0001210618",
        "form": "3",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1210618/a/x.xml",
        "structured_position_rows": 1,
        "common_equity_rows": 1,
        "name_match": False,
        "name_match_basis": None,
        "cusip_match": False,
        "explicit_non_target_name_match": False,
        "explicit_non_target_cusip": False,
    }
    values.update(overrides)
    return decide_document_identity(**values)


def test_target_cik_and_common_equity_is_governed_continuity() -> None:
    assert _decision() == (
        ADMITTED_IDENTITY_STATE,
        "TARGET_CIK_AND_COMMON_EQUITY_EVIDENCE",
    )


def test_explicit_other_issuer_is_rejected_not_left_unresolved() -> None:
    assert _decision(issuer_cik="0001140310")[0] == REJECTED_ISSUER_STATE


def test_missing_cik_name_linked_to_explicit_other_issuer_is_rejected() -> None:
    assert _decision(
        issuer_cik=None,
        explicit_non_target_name_match=True,
    ) == (REJECTED_ISSUER_STATE, "NAME_LINKED_TO_EXPLICIT_NON_TARGET_CIK")


def test_only_non_target_security_rows_are_rejected() -> None:
    assert _decision(common_equity_rows=0)[0] == REJECTED_SECURITY_STATE


def test_missing_cik_with_explicit_other_class_cusip_is_rejected() -> None:
    assert _decision(
        issuer_cik=None,
        explicit_non_target_cusip=True,
    ) == (REJECTED_SECURITY_STATE, "EXPLICIT_NON_TARGET_CLASS_CUSIP")


def test_missing_cik_proxy_requires_archive_continuity_and_common_equity() -> None:
    assert _decision(issuer_cik=None, form="DEF 14A")[0] == ADMITTED_IDENTITY_STATE
    assert _decision(
        issuer_cik=None,
        form="SC 13D",
        name_match=False,
        cusip_match=False,
    )[0] == UNRESOLVED_IDENTITY_STATE


def test_ticker_reuse_state_never_admits_identity() -> None:
    assert _decision(interval_resolution_allowed=False)[0] == UNRESOLVED_IDENTITY_STATE


def test_common_equity_title_filter_is_conservative() -> None:
    assert is_common_equity_title("Class A Common Stock")
    assert is_common_equity_title("Ordinary Shares")
    assert is_common_equity_title("Common Units")
    assert not is_common_equity_title("Series E1 Preferred Stock")
    assert not is_common_equity_title("Restricted Stock Units")
    assert not is_common_equity_title("12% Convertible Promissory Note")
