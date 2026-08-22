from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.run_authorized_primary_acquisition_v0_2 import (  # noqa: E402
    classify_acquisition_scope,
    persist_low_disk_stop,
    require_canonical_sec_root,
)


def test_local_complete_is_not_mislabeled_as_security_class_halt() -> None:
    gates = pd.DataFrame(
        {
            "ticker": ["DOWNLOAD", "COHORT", "LOCAL", "NEGATIVE"],
            "primary_document_acquisition_state": [
                "ELIGIBLE_FOR_GOVERNED_REVIEW",
                "ELIGIBLE_FOR_REVIEW_NOT_AUTHORIZED",
                "LOCAL_EVIDENCE_COMPLETE",
                "HALT_SECURITY_CLASS",
            ],
        }
    )
    eligible, halts, local = classify_acquisition_scope(gates)
    assert eligible == ["COHORT", "DOWNLOAD"]
    assert halts == ["NEGATIVE"]
    assert local == ["LOCAL"]


def test_low_disk_stop_persists_resume_safe_terminal_state(tmp_path: Path) -> None:
    final = persist_low_disk_stop(
        tmp_path,
        {"run_id": "test", "status": "RUNNING"},
        free_gib=199.5,
        minimum_gib=200.0,
    )
    assert final["status"] == "STOPPED_LOW_DISK"
    assert final["exit_code"] == 2
    assert "--resume" in final["resume_instructions"]
    assert (tmp_path / "final_manifest.json").is_file()
    assert (tmp_path / "heartbeat_latest.json").is_file()
    assert (tmp_path / "pid_manifest.json").is_file()


def test_primary_runner_rejects_legacy_or_other_output_root(tmp_path: Path) -> None:
    canonical = tmp_path / "active"
    canonical.mkdir()
    assert require_canonical_sec_root(canonical, canonical) == canonical.resolve()
    legacy = tmp_path / "legacy"
    legacy.mkdir()
    try:
        require_canonical_sec_root(legacy, canonical)
    except ValueError as exc:
        assert "governed active SEC PIT root" in str(exc)
    else:
        raise AssertionError("noncanonical primary output root was accepted")
