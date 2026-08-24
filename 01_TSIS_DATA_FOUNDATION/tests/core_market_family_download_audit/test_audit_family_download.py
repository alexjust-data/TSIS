from __future__ import annotations

import importlib.util
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np


SCRIPT = (
    Path(__file__).parents[2]
    / "scripts"
    / "core_market_family_download_audit"
    / "audit_family_download.py"
)
SPEC = importlib.util.spec_from_file_location("family_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


NY = ZoneInfo("America/New_York")


def epoch(local: str, unit: str) -> int:
    instant = datetime.fromisoformat(local).replace(tzinfo=NY)
    seconds = int(instant.timestamp())
    return seconds * (1_000_000_000 if unit == "ns" else 1)


def test_session_boundaries_are_left_inclusive_right_exclusive() -> None:
    index = MODULE.SessionBoundaryIndex(date(2024, 3, 11), date(2024, 3, 11), "s")
    counts = np.zeros((1, 4), dtype=np.int64)
    values = np.array(
        [
            epoch("2024-03-11T03:59:59", "s"),
            epoch("2024-03-11T04:00:00", "s"),
            epoch("2024-03-11T09:29:59", "s"),
            epoch("2024-03-11T09:30:00", "s"),
            epoch("2024-03-11T15:59:59", "s"),
            epoch("2024-03-11T16:00:00", "s"),
            epoch("2024-03-11T19:59:59", "s"),
            epoch("2024-03-11T20:00:00", "s"),
        ],
        dtype=np.int64,
    )
    consumed, outside = index.classify_into(values, counts)
    assert consumed == 8
    assert outside == 0
    assert counts.tolist() == [[2, 2, 2, 2]]


def test_dst_dates_use_america_new_york_not_fixed_offset() -> None:
    index = MODULE.SessionBoundaryIndex(date(2024, 3, 8), date(2024, 3, 11), "s")
    counts = np.zeros((4, 4), dtype=np.int64)
    values = np.array(
        [
            epoch("2024-03-08T04:00:00", "s"),
            epoch("2024-03-11T04:00:00", "s"),
        ],
        dtype=np.int64,
    )
    index.classify_into(values, counts)
    assert counts[0, 0] == 1
    assert counts[3, 0] == 1


def test_nanosecond_clock_classifies_same_sessions() -> None:
    index = MODULE.SessionBoundaryIndex(date(2025, 11, 3), date(2025, 11, 3), "ns")
    counts = np.zeros((1, 4), dtype=np.int64)
    values = np.array(
        [epoch("2025-11-03T09:30:00", "ns"), epoch("2025-11-03T16:00:00", "ns")],
        dtype=np.int64,
    )
    index.classify_into(values, counts)
    assert counts.tolist() == [[0, 1, 1, 0]]

