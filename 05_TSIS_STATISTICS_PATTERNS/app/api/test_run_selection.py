from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from .server_v2 import _resolve_final_root


LAUNCHER = Path(__file__).parents[1] / "start_atlas_local.ps1"
POWERSHELL = shutil.which("powershell.exe") or "powershell.exe"


def _write_terminal(
    runs_root: Path,
    run_name: str,
    *,
    status: str,
    mode: str,
    certified_at: str,
) -> Path:
    final_root = runs_root / run_name / "final"
    final_root.mkdir(parents=True)
    (final_root / "terminal_certification.json").write_text(
        json.dumps(
            {
                "status": status,
                "mode": mode,
                "certified_at": certified_at,
            }
        ),
        encoding="utf-8",
    )
    return final_root


def _resolve_with_launcher(runs_root: Path) -> Path:
    environment = os.environ.copy()
    environment.pop("ATLAS_FINAL_ROOT", None)
    completed = subprocess.run(
        [
            POWERSHELL,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(LAUNCHER),
            "-RunsRoot",
            str(runs_root),
            "-ResolveOnly",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    return Path(completed.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize("full_status", [None, "fail"], ids=["incomplete", "failed"])
def test_incomplete_or_failed_full_falls_back_to_latest_pass_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    full_status: str | None,
) -> None:
    monkeypatch.delenv("ATLAS_FINAL_ROOT", raising=False)
    probe = _write_terminal(
        tmp_path,
        "20260825_probe_v0_3",
        status="pass",
        mode="probe",
        certified_at="2026-08-25T07:18:55+00:00",
    )
    full = tmp_path / "20260825_full_v0_1" / "final"
    full.mkdir(parents=True)
    if full_status is not None:
        (full / "terminal_certification.json").write_text(
            json.dumps({"status": full_status, "mode": "full"}),
            encoding="utf-8",
        )

    assert _resolve_final_root(tmp_path) == probe
    assert _resolve_with_launcher(tmp_path) == probe


def test_terminal_pass_full_has_priority_over_newer_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ATLAS_FINAL_ROOT", raising=False)
    full = _write_terminal(
        tmp_path,
        "20260825_full_v0_1",
        status="pass",
        mode="full",
        certified_at="2026-08-25T07:00:00+00:00",
    )
    _write_terminal(
        tmp_path,
        "20260825_probe_v0_4",
        status="pass",
        mode="probe",
        certified_at="2026-08-25T08:00:00+00:00",
    )

    assert _resolve_final_root(tmp_path) == full
    assert _resolve_with_launcher(tmp_path) == full


def test_latest_pass_is_selected_deterministically_within_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ATLAS_FINAL_ROOT", raising=False)
    _write_terminal(
        tmp_path,
        "20260825_probe_v0_2",
        status="pass",
        mode="probe",
        certified_at="2026-08-25T06:00:00+00:00",
    )
    latest = _write_terminal(
        tmp_path,
        "20260825_probe_v0_3",
        status="pass",
        mode="probe",
        certified_at="2026-08-25T07:00:00+00:00",
    )

    assert _resolve_final_root(tmp_path) == latest
    assert _resolve_with_launcher(tmp_path) == latest


def test_invalid_explicit_root_is_rejected(tmp_path: Path) -> None:
    incomplete = tmp_path / "20260825_full_v0_1" / "final"
    incomplete.mkdir(parents=True)
    assert _resolve_final_root(tmp_path, explicit_root=incomplete) is None
