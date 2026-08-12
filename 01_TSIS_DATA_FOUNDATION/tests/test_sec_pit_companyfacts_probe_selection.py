import gzip
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sec_pit.run_companyfacts_os_reconciliation_probe import (  # noqa: E402
    companyfacts_fetch_state,
    persist_failure,
    read_reusable_companyfacts,
    select_cases,
)

CASES = [
    {"ticker": "ADMP", "probe_gate": "ELIGIBLE"},
    {"ticker": "ASNA", "probe_gate": "ELIGIBLE"},
    {"ticker": "ANTH", "probe_gate": "HALT_SECURITY_CLASS"},
]


def test_companyfacts_probe_can_select_a_bounded_ticker_subset() -> None:
    selected = select_cases(CASES, ["anth", "ADMP"])
    assert [row["ticker"] for row in selected] == ["ADMP", "ANTH"]


def test_companyfacts_probe_rejects_unknown_requested_ticker() -> None:
    with pytest.raises(ValueError, match="absent from case matrix"):
        select_cases(CASES, ["MISSING"])


def test_companyfacts_probe_can_exclude_noneligible_control() -> None:
    selected = select_cases(CASES, None, eligible_only=True)
    assert [row["ticker"] for row in selected] == ["ADMP", "ASNA"]


def test_companyfacts_404_is_explicit_unavailable_not_failure() -> None:
    assert companyfacts_fetch_state(
        http_status=404, payload_available=False
    ) == "COMPANYFACTS_NOT_AVAILABLE"
    assert companyfacts_fetch_state(
        http_status=503, payload_available=False
    ) == "ACQUISITION_FAILED"
    assert companyfacts_fetch_state(
        http_status=200, payload_available=True
    ) == "AVAILABLE"


def test_reusable_companyfacts_is_verified_before_use(tmp_path: Path) -> None:
    payload = json.dumps({"cik": 1, "facts": {}}).encode()
    object_path = tmp_path / "facts.json.gz"
    with gzip.open(object_path, "wb") as handle:
        handle.write(payload)
    url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000001.json"
    row = {
        "status": "FETCHED",
        "url": url,
        "object_path": object_path.as_posix(),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "http_status": 200,
        "content_type": "application/json",
        "logical_path": "companyfacts/0000000001.json",
    }
    result, parsed = read_reusable_companyfacts(row, expected_url=url)
    assert result.status == "FETCHED_REUSED"
    assert result.attempts == 0
    assert parsed["cik"] == 1


def test_persist_failure_closes_final_and_pid_manifests(tmp_path: Path) -> None:
    run_id = "failed-run"
    run_root = tmp_path / "runs" / run_id
    run_root.mkdir(parents=True)
    (run_root / "pre_manifest.json").write_text(
        json.dumps({"run_id": run_id, "created_at_utc": "2026-01-01T00:00:00Z"}),
        encoding="utf-8",
    )
    args = SimpleNamespace(output_root=tmp_path, run_id=run_id)
    persist_failure(args, RuntimeError("expected"))
    final = json.loads((run_root / "final_manifest.json").read_text())
    pid = json.loads((run_root / "pid_manifest.json").read_text())
    assert final["status"] == "FAILED"
    assert pid["expected_alive"] is False
