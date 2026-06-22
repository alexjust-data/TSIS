from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest


TESTS_DIR = Path(__file__).resolve().parent
MODULE_ROOT = TESTS_DIR.parent
REPO_ROOT = MODULE_ROOT.parent
ROOT_TESTS_DIR = REPO_ROOT / "tests"

if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _json_default(value: Any) -> str:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    commit = result.stdout.strip()
    return commit or None


def _test_run_paths() -> tuple[str, str, Path]:
    now = _utc_now()
    run_date = os.environ.get("TSIS_TEST_RUN_DATE") or now.date().isoformat()
    run_id = os.environ.get("TSIS_TEST_RUN_ID") or f"pytest_{now.strftime('%Y%m%dT%H%M%SZ')}"
    run_dir_env = os.environ.get("TSIS_TEST_RUN_DIR")
    run_dir = Path(run_dir_env) if run_dir_env else ROOT_TESTS_DIR / "test_runs" / run_date / run_id
    return run_date, run_id, run_dir


def pytest_configure(config: pytest.Config) -> None:
    run_date, run_id, run_dir = _test_run_paths()
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    config._tsis_run_date = run_date  # type: ignore[attr-defined]
    config._tsis_run_id = run_id  # type: ignore[attr-defined]
    config._tsis_run_dir = run_dir  # type: ignore[attr-defined]
    config._tsis_artifacts_dir = artifacts_dir  # type: ignore[attr-defined]
    config._tsis_reports = []  # type: ignore[attr-defined]

    metadata = {
        "run_id": run_id,
        "run_date": run_date,
        "created_at_utc": _utc_now().isoformat(),
        "module": "01_TSIS_backtest_SmallCaps",
        "test_scope": os.environ.get("TSIS_TEST_SCOPE", "unspecified"),
        "repo_root": str(REPO_ROOT),
        "module_root": str(MODULE_ROOT),
        "root_tests_dir": str(ROOT_TESTS_DIR),
        "run_dir": str(run_dir),
        "artifacts_dir": str(artifacts_dir),
        "pytest_args": list(config.invocation_params.args),
        "python": sys.version,
        "platform": platform.platform(),
        "git_commit": _git_commit(),
        "status": "running",
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, default=_json_default),
        encoding="utf-8",
    )


def pytest_report_header(config: pytest.Config) -> list[str]:
    return [
        f"TSIS test run id: {config._tsis_run_id}",  # type: ignore[attr-defined]
        f"TSIS test evidence: {config._tsis_run_dir}",  # type: ignore[attr-defined]
    ]


@pytest.fixture(scope="session")
def tsis_test_run_dir(pytestconfig: pytest.Config) -> Path:
    return pytestconfig._tsis_run_dir  # type: ignore[attr-defined]


@pytest.fixture(scope="session")
def tsis_artifacts_dir(pytestconfig: pytest.Config) -> Path:
    return pytestconfig._tsis_artifacts_dir  # type: ignore[attr-defined]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" or report.outcome == "failed":
        item.config._tsis_reports.append(  # type: ignore[attr-defined]
            {
                "nodeid": report.nodeid,
                "phase": report.when,
                "outcome": report.outcome,
                "duration_seconds": report.duration,
                "longrepr": str(report.longrepr) if report.failed else "",
            }
        )


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    config = session.config
    run_dir: Path = config._tsis_run_dir  # type: ignore[attr-defined]
    reports: list[dict[str, Any]] = config._tsis_reports  # type: ignore[attr-defined]

    counts = {"passed": 0, "failed": 0, "skipped": 0, "xfailed": 0, "xpassed": 0}
    for report in reports:
        outcome = report["outcome"]
        if outcome in counts:
            counts[outcome] += 1

    failed = [r for r in reports if r["outcome"] == "failed"]
    status = "passed" if exitstatus == 0 else "failed"

    summary_lines = [
        f"# TSIS Test Run Summary `{config._tsis_run_id}`",  # type: ignore[attr-defined]
        "",
        f"- Status: `{status}`",
        f"- Exit status: `{exitstatus}`",
        f"- Run date: `{config._tsis_run_date}`",  # type: ignore[attr-defined]
        f"- Evidence path: `{run_dir}`",
        f"- Passed: `{counts['passed']}`",
        f"- Failed: `{counts['failed']}`",
        f"- Skipped: `{counts['skipped']}`",
        "",
        "## Scope",
        "",
        f"`{os.environ.get('TSIS_TEST_SCOPE', 'unspecified')}`",
        "",
        "## Failed Tests",
        "",
    ]
    if failed:
        for item in failed:
            summary_lines.extend(
                [
                    f"### `{item['nodeid']}`",
                    "",
                    "```text",
                    item["longrepr"][:8000],
                    "```",
                    "",
                ]
            )
    else:
        summary_lines.append("No failed tests.")

    (run_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    metadata_path = run_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata.update(
        {
            "finished_at_utc": _utc_now().isoformat(),
            "status": status,
            "exitstatus": exitstatus,
            "counts": counts,
            "failed_tests": [r["nodeid"] for r in failed],
        }
    )
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, default=_json_default),
        encoding="utf-8",
    )
