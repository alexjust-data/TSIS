from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import psutil
import pytest


SCRIPT_DIR = (
    Path(__file__).resolve().parents[2] / "scripts" / "core_market_raw_alignment_audit"
)
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location(
    "trades_accelerator_test_runtime", SCRIPT_DIR / "accelerate_trades_workers.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def initialize_ledger(path: Path) -> None:
    MODULE.AUDIT.initialize_ledger(
        path,
        run_id="probe",
        run_contract_sha256="ABC",
        families=[MODULE.FAMILY],
        tickers=["AAA", "BBB", "CCC"],
    )
    MODULE.configure_base()
    MODULE.initialize_event_ledger(path)


def test_claims_are_disjoint_and_commits_require_exact_ownership(tmp_path: Path) -> None:
    ledger = tmp_path / "run_state.sqlite"
    initialize_ledger(ledger)
    first = MODULE.BASE.claim_next_quote_task(ledger, 101)
    second = MODULE.BASE.claim_next_quote_task(ledger, 202)
    assert first and second
    assert first[0] != second[0]
    result = {
        "source_ticker_dir_exists": True,
        "file_count": 1,
        "source_bytes": 10,
        "date_count": 1,
        "error_file_count": 0,
        "task_manifest_path": "probe.json",
    }
    with pytest.raises(RuntimeError, match="Lost task ownership"):
        MODULE.BASE.mark_quote_committed(ledger, first[0], 999, first[1], result)
    MODULE.BASE.mark_quote_committed(ledger, first[0], 101, first[1], result)
    recovered = MODULE.recover_added_tasks(ledger, [202], "probe_recovery")
    assert recovered == [second[0]]
    snapshot = MODULE.ledger_snapshot(ledger)
    assert snapshot["trades_counts"] == {"committed": 1, "pending": 2, "total": 3}
    assert snapshot["active_trades"] == []


def test_suspend_gate_does_not_leave_dummy_process_stopped(tmp_path: Path) -> None:
    ledger = tmp_path / "run_state.sqlite"
    initialize_ledger(ledger)
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        MODULE.suspend_without_sql_lock(ledger, process.pid)
        controlled = psutil.Process(process.pid)
        assert controlled.status() == psutil.STATUS_STOPPED
        controlled.resume()
        assert controlled.status() != psutil.STATUS_STOPPED
    finally:
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=10)
