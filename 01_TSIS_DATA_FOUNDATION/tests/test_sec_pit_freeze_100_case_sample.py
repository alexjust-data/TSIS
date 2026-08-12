from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sec_pit.freeze_100_case_sample import span_bucket


def test_span_bucket_boundaries() -> None:
    assert span_bucket(0) == "LT_2Y"
    assert span_bucket(730) == "LT_2Y"
    assert span_bucket(731) == "Y2_TO_5"
    assert span_bucket(3653) == "Y10_TO_15"
    assert span_bucket(5479) == "GE_15Y"
