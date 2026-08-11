from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.run_no_network_os_probe import (  # noqa: E402
    interval_resolution_allowed,
    selected_for_os_probe,
)


def test_ticker_reuse_conflict_blocks_resolution_generically() -> None:
    assert interval_resolution_allowed("TICKER_REUSE_CONFLICT") is False
    assert interval_resolution_allowed("SOURCE_DATE_UNAVAILABLE_OR_NOT_COMPARABLE") is True


def test_os_probe_uses_only_rows_selected_for_periodic_os() -> None:
    frame = pd.DataFrame(
        {
            "accession_number": ["a", "b"],
            "stratified_selection_reasons": [
                ["OS_PERIODIC_LATEST_TWO"],
                ["GOVERNED_LIFECYCLE_EVIDENCE"],
            ],
        }
    )
    selected = selected_for_os_probe(frame)
    assert selected["accession_number"].tolist() == ["a"]
