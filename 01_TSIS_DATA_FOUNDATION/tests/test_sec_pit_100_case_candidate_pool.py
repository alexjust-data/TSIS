from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.build_100_case_candidate_pool import select_pool


def test_candidate_pool_preserves_anchors_and_exact_temporal_quotas() -> None:
    rows = []
    cohorts = ["2005_2008", "2009_2012"]
    for cohort_index, cohort in enumerate(cohorts):
        for index in range(10):
            rows.append({
                "ticker": f"T{cohort_index}{index}",
                "temporal_cohort": cohort,
                "stable_rank": index,
                "tag_anchor": index == 0,
                "tag_longitudinal_2005_to_2025": cohort_index == 0,
                "tag_multiple_ticker_changes": index % 2 == 0,
                "tag_heavy_reverse_split_history": index % 3 == 0,
                "tag_spac_name_candidate": index % 4 == 0,
                "tag_inactive_or_delisted_candidate": index % 2 == 1,
                "tag_recent_listing_candidate": False,
            })
    frame = pd.DataFrame(rows)
    selected = select_pool(
        frame,
        cohort_quotas={"2005_2008": 4, "2009_2012": 3},
        tag_targets={
            "ANCHOR_7_CASE": 2,
            "LONGITUDINAL_2005_TO_2025": 2,
            "MULTIPLE_TICKER_CHANGES": 2,
            "HEAVY_REVERSE_SPLIT_HISTORY": 2,
            "SPAC_NAME_CANDIDATE": 2,
            "INACTIVE_OR_DELISTED_CANDIDATE": 2,
            "RECENT_LISTING_CANDIDATE": 0,
        },
        anchors={"T00", "T10"},
    )
    assert len(selected) == 7
    assert set(selected.loc[selected["tag_anchor"], "ticker"]) == {"T00", "T10"}
    assert selected["temporal_cohort"].value_counts().to_dict() == {
        "2005_2008": 4,
        "2009_2012": 3,
    }


def test_candidate_pool_selection_is_deterministic() -> None:
    frame = pd.DataFrame([
        {
            "ticker": f"T{index}",
            "temporal_cohort": "2005_2008",
            "stable_rank": 10 - index,
            "tag_anchor": False,
            "tag_longitudinal_2005_to_2025": False,
            "tag_multiple_ticker_changes": False,
            "tag_heavy_reverse_split_history": False,
            "tag_spac_name_candidate": False,
            "tag_inactive_or_delisted_candidate": False,
            "tag_recent_listing_candidate": False,
        }
        for index in range(10)
    ])
    kwargs = {
        "cohort_quotas": {"2005_2008": 3},
        "tag_targets": {tag: 0 for tag in (
            "ANCHOR_7_CASE", "LONGITUDINAL_2005_TO_2025",
            "MULTIPLE_TICKER_CHANGES", "HEAVY_REVERSE_SPLIT_HISTORY",
            "SPAC_NAME_CANDIDATE", "INACTIVE_OR_DELISTED_CANDIDATE",
            "RECENT_LISTING_CANDIDATE",
        )},
        "anchors": set(),
    }
    first = select_pool(frame, **kwargs)
    second = select_pool(frame.sample(frac=1, random_state=3), **kwargs)
    assert first["ticker"].tolist() == second["ticker"].tolist()
