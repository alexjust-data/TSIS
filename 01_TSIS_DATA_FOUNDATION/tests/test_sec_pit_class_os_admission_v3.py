from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.class_os_admission_v3 import (  # noqa: E402
    resolve_common_equity_class_candidate_v0_3,
)


PAYLOAD = b"""
<html>AIFEEX NEXUS ACQUISITION CORPORATION
Title of each class Trading Symbol Name of exchange
Class A ordinary shares, par value $0.0001 per share AIFE Nasdaq
Class B ordinary shares are not publicly traded.
</html>
"""


def decide(*, source_url: str, link_state: str = "REVIEW_MULTIPLE_INSTRUMENT_CANDIDATES"):
    return resolve_common_equity_class_candidate_v0_3(
        PAYLOAD,
        temporal_scope_state="TARGET_INTERVAL",
        accession_link_state=link_state,
        registrant_name="stale vendor display name",
        ticker="AIFE",
        target_cik="0002030829",
        source_url=source_url,
    )


def test_exact_archive_cik_and_exchange_row_recover_multiple_candidate_link() -> None:
    label, decision = decide(
        source_url=(
            "https://www.sec.gov/Archives/edgar/data/2030829/"
            "000101376225002878/filing.htm"
        )
    )
    assert label == "Class A Ordinary Shares"
    assert decision.decision == "ADMITTED_TARGET_INSTRUMENT_CLASS"
    assert decision.registrant_match is False
    assert decision.ticker_class_match is True


def test_archive_cik_mismatch_remains_unresolved() -> None:
    label, decision = decide(
        source_url=(
            "https://www.sec.gov/Archives/edgar/data/9999999/"
            "000101376225002878/filing.htm"
        )
    )
    assert label is None
    assert decision.decision == "UNRESOLVED_REQUIRES_REVIEW"


def test_no_exchange_ticker_row_remains_unresolved() -> None:
    label, decision = resolve_common_equity_class_candidate_v0_3(
        b"<html>Class A ordinary shares with no trading symbol.</html>",
        temporal_scope_state="TARGET_INTERVAL",
        accession_link_state="REVIEW_MULTIPLE_INSTRUMENT_CANDIDATES",
        registrant_name="stale name",
        ticker="AIFE",
        target_cik="0002030829",
        source_url=(
            "https://www.sec.gov/Archives/edgar/data/2030829/"
            "000101376225002878/filing.htm"
        ),
    )
    assert label is None
    assert decision.decision == "UNRESOLVED_REQUIRES_REVIEW"
