from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.audit_os_unavailable_shard_certification import shard_for  # noqa: E402


def test_certification_case_selection_covers_each_production_shard() -> None:
    selected = {
        "cik_ticker:0002030829:AIFE": 0,
        "figi_share_class:BBG0025CGH08": 1,
        "cik_ticker:0001601936:CYTO": 2,
        "figi_share_class:BBG001S7VTW8": 3,
    }
    assert {shard_for(instrument_id): shard for instrument_id, shard in selected.items()} == {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
    }


def test_shard_function_is_deterministic() -> None:
    instrument_id = "figi_share_class:BBG001S7VTW8"
    assert shard_for(instrument_id) == shard_for(instrument_id)
