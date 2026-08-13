from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.audit_instrument_interval_recovery import (  # noqa: E402
    classify_case,
    classify_unresolved_document,
    is_common_equity_observation,
    sec_archive_cik,
)


def test_known_non_target_cik_is_rejected_without_interval_blocker() -> None:
    family = classify_unresolved_document(
        target_cik="0000896493", issuer_cik="0001437491", form="3",
        source_url="https://www.sec.gov/Archives/edgar/data/896493/a/ownership.xml",
        common_equity_rows=1,
    )
    assert family == "NON_TARGET_ISSUER_DOCUMENT_MUST_BE_REJECTED"


def test_target_cik_requires_supported_common_equity() -> None:
    assert classify_unresolved_document(
        target_cik="1210618", issuer_cik="0001210618", form="3",
        source_url="https://www.sec.gov/Archives/edgar/data/1210618/a/x.xml",
        common_equity_rows=2,
    ) == "TARGET_CIK_COMMON_EQUITY_CONTINUITY_CANDIDATE"
    assert classify_unresolved_document(
        target_cik="1210618", issuer_cik="0001210618", form="3",
        source_url="https://www.sec.gov/Archives/edgar/data/1210618/a/x.xml",
        common_equity_rows=0,
    ) == "NON_TARGET_SECURITY_DOCUMENT_MUST_BE_REJECTED"


def test_missing_cik_baseline_uses_sec_archive_lineage_only() -> None:
    assert classify_unresolved_document(
        target_cik="1896212", issuer_cik=None, form="DEF 14A",
        source_url="https://www.sec.gov/Archives/edgar/data/1896212/a/proxy.htm",
        common_equity_rows=9,
    ) == "ISSUER_FILED_BASELINE_METADATA_CONTINUITY_CANDIDATE"
    assert classify_unresolved_document(
        target_cik="1896212", issuer_cik=None, form="SC 13D",
        source_url="https://www.sec.gov/Archives/edgar/data/1896212/a/schedule.htm",
        common_equity_rows=9,
    ) == "TRUE_IDENTITY_EVIDENCE_GAP_OR_UNSUPPORTED_CLASS"


def test_security_title_filter_excludes_non_common_instruments() -> None:
    assert is_common_equity_observation({
        "security_title": "Class A Common Stock",
        "supported_issued_common_shares": 12.0,
    })
    assert not is_common_equity_observation({
        "security_title": "Series E Preferred Stock",
        "supported_issued_common_shares": 12.0,
    })
    assert not is_common_equity_observation({
        "security_title": "Restricted Stock Unit",
        "supported_issued_common_shares": 12.0,
    })


def test_archive_cik_and_mixed_case_classification_are_deterministic() -> None:
    assert sec_archive_cik("https://www.sec.gov/Archives/edgar/data/75208/a/x.htm") == "0000075208"
    assert classify_case({
        "TARGET_CIK_COMMON_EQUITY_CONTINUITY_CANDIDATE",
        "NON_TARGET_ISSUER_DOCUMENT_MUST_BE_REJECTED",
    }) == "MIXED_RECOVERABLE_INTERVAL_FAMILIES"
