from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.run_authorized_primary_acquisition_v0_2 import (  # noqa: E402
    classify_acquisition_scope,
)


def test_local_complete_is_not_mislabeled_as_security_class_halt() -> None:
    gates = pd.DataFrame(
        {
            "ticker": ["DOWNLOAD", "LOCAL", "NEGATIVE"],
            "primary_document_acquisition_state": [
                "ELIGIBLE_FOR_GOVERNED_REVIEW",
                "LOCAL_EVIDENCE_COMPLETE",
                "HALT_SECURITY_CLASS",
            ],
        }
    )
    eligible, halts, local = classify_acquisition_scope(gates)
    assert eligible == ["DOWNLOAD"]
    assert halts == ["NEGATIVE"]
    assert local == ["LOCAL"]
