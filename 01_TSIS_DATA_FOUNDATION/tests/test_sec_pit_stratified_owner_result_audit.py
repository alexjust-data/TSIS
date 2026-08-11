from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.audit_stratified_owner_exclusion_results import audit_run  # noqa: E402


def test_audit_accepts_calculated_and_explicitly_blocked_rows(tmp_path: Path) -> None:
    run = tmp_path / "run"
    run.mkdir()
    daily = pd.DataFrame(
        [
            {
                "instrument_id": "instrument",
                "session_date": "2026-03-02",
                "schema_version": "v1",
                "shares_outstanding_estimate_as_known": 100.0,
                "float_owner_exclusion_estimate_as_known": 80.0,
                "float_percent_estimate_as_known": 80.0,
                "unique_supported_excluded_shares": 20.0,
                "ownership_baseline_eligible_from_session": "2026-02-01",
                "estimation_state": "CALCULATED",
                "blocker_codes_json": "[]",
            },
            *[
                {
                    "instrument_id": "instrument",
                    "session_date": f"2026-03-0{day}",
                    "schema_version": "v1",
                    "shares_outstanding_estimate_as_known": None,
                    "float_owner_exclusion_estimate_as_known": None,
                    "float_percent_estimate_as_known": None,
                    "unique_supported_excluded_shares": None,
                    "ownership_baseline_eligible_from_session": None,
                    "estimation_state": "BLOCKED_BY_INPUT_GATES",
                    "blocker_codes_json": '["BLOCKED"]',
                }
                for day in range(3, 7)
            ],
        ]
    )
    daily.to_parquet(run / "daily_float_state.parquet", index=False)
    audit = {key: "PASS" for key in (
        "S5_OS_MANUAL_GATE", "S6_NEUTRAL_OWNERSHIP_EXTRACTION",
        "S7_HOLDER_AND_CLASS_RECONCILIATION", "S8_OWNER_EXCLUSION_FLOAT",
        "S9_FLOAT_CHANGE_AUDIT",
    )}
    (run / "variable_audit.json").write_text(json.dumps(audit), encoding="utf-8")
    daily_hash = __import__("hashlib").sha256((run / "daily_float_state.parquet").read_bytes()).hexdigest()
    manifest = {
        "ticker": "TEST", "run_id": "run", "network_requests": 0,
        "component_hashes": {"code.py": "hash"},
        "output_files": {"daily_float_state.parquet": {"sha256": daily_hash}},
    }
    (run / "final_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert audit_run(run)["status"] == "PASS"
