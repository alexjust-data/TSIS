from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "download_quotes_literal_safe_v0_1.py"


def _load_wrapper():
    spec = importlib.util.spec_from_file_location("download_quotes_literal_safe_v0_1_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_task_reader_preserves_literal_na(tmp_path: Path) -> None:
    wrapper = _load_wrapper()
    legacy = wrapper._load_legacy_module()
    tasks = tmp_path / "tasks.csv"
    tasks.write_text("ticker,date\nNA,2026-03-10\nA,2026-03-10\n", encoding="utf-8")

    frame = wrapper.read_csv_tasks_literal_safe(tasks, legacy)

    assert frame["ticker"].tolist() == ["A", "NA"]
    assert frame["task_key"].tolist() == ["A|2026-03-10", "NA|2026-03-10"]


def test_task_reader_rejects_blank_identity(tmp_path: Path) -> None:
    wrapper = _load_wrapper()
    legacy = wrapper._load_legacy_module()
    tasks = tmp_path / "tasks.csv"
    tasks.write_text("ticker,date\n,2026-03-10\n", encoding="utf-8")

    try:
        wrapper.read_csv_tasks_literal_safe(tasks, legacy)
    except ValueError as exc:
        assert "null/blank ticker or date" in str(exc)
    else:
        raise AssertionError("blank ticker identity was accepted")


def test_single_empty_response_remains_resumable() -> None:
    wrapper = _load_wrapper()
    legacy = wrapper._load_legacy_module()

    wrapper.install_literal_safe_overrides(legacy)

    assert "DOWNLOADED_EMPTY" not in legacy.RESUME_SKIP_STATUSES
    assert legacy.RESUME_SKIP_STATUSES == {"DOWNLOADED_OK", "EMPTY_CONFIRMED"}

def test_corrupt_resume_ledger_fails_closed(tmp_path: Path) -> None:
    wrapper = _load_wrapper()
    legacy = wrapper._load_legacy_module()
    ledger = tmp_path / "download_events_current.csv"
    ledger.write_bytes(b"\xff\xfe\x00")

    try:
        wrapper.load_current_literal_safe(ledger, legacy)
    except RuntimeError as exc:
        assert "Cannot read resume ledger" in str(exc)
    else:
        raise AssertionError("corrupt resume ledger was silently ignored")