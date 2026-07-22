from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _helpers.data_foundation import write_json_artifact


MODULE_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = MODULE_ROOT / "scripts/validate_event_candidate_tables.py"
FIXTURES = MODULE_ROOT / "tests/fixtures/data_foundation_outputs/event_candidate_tables_v0_1"

DAILY_DATASET_ID = "daily_strategy_candidate_events_table_v0_1"
INTRADAY_DATASET_ID = "intraday_1m_strategy_candidate_events_table_v0_1"


def _run_validator(dataset_id: str, fixture_name: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    summary = tmp_path / f"{fixture_name}.summary.json"
    results = tmp_path / f"{fixture_name}.results.json"
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--dataset-id",
            dataset_id,
            "--input",
            str(FIXTURES / fixture_name),
            "--summary-output",
            str(summary),
            "--results-output",
            str(results),
        ],
        cwd=MODULE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _payload(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.stdout.strip(), result.stderr
    return json.loads(result.stdout)


def _validator_ids(payload: dict) -> set[str]:
    return {failure["validator_id"] for failure in payload["failures"]}


def test_event_candidate_validator_contract_check(tsis_artifacts_dir: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--contract-check-only"],
        cwd=MODULE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["validator_contract_id"] == "event_candidate_table_validators_contract_v0_1"
    assert payload["validator_version"] == "event_candidate_table_validators_executable_v0_1"
    assert payload["status"] == "executable_validator_defined_for_fixture_scope"
    assert payload["real_tables_materialized"] is False
    assert payload["fixture_scope"] is True
    assert payload["writes_official_output"] is False
    assert payload["missing_contracts"] == []
    write_json_artifact(tsis_artifacts_dir, "event_candidate_validator_contract_check.json", payload)


def test_daily_event_candidate_good_fixture_passes(tsis_artifacts_dir: Path) -> None:
    result = _run_validator(DAILY_DATASET_ID, "daily_good_v0_1.json", tsis_artifacts_dir)
    payload = _payload(result)
    assert result.returncode == 0, result.stderr + result.stdout
    assert payload["status"] == "passed"
    assert payload["hard_fail_count"] == 0
    assert payload["materialization_allowed"] is True
    assert payload["ml_ready_dataset_enabled"] is False
    assert payload["rl_training_dataset_enabled"] is False
    assert payload["alphaevolve_evaluator_enabled"] is False


def test_daily_event_candidate_blocks_outcome_inline(tsis_artifacts_dir: Path) -> None:
    result = _run_validator(DAILY_DATASET_ID, "daily_bad_outcome_inline_v0_1.json", tsis_artifacts_dir)
    payload = _payload(result)
    assert result.returncode != 0
    assert payload["hard_fail_count"] > 0
    ids = _validator_ids(payload)
    assert "event_bad_outcome_inline" in ids
    assert "event_bad_prohibited_prefix" in ids


def test_daily_event_candidate_blocks_intraday_claim_without_source(tsis_artifacts_dir: Path) -> None:
    result = _run_validator(
        DAILY_DATASET_ID,
        "daily_bad_intraday_claim_without_source_v0_1.json",
        tsis_artifacts_dir,
    )
    payload = _payload(result)
    assert result.returncode != 0
    ids = _validator_ids(payload)
    assert "daily_event_bad_intraday_claim_without_source" in ids
    assert "daily_event_bad_eod_proxy_as_intraday_truth" in ids


def test_intraday_event_candidate_good_quote_guarded_fixture_passes(tsis_artifacts_dir: Path) -> None:
    result = _run_validator(INTRADAY_DATASET_ID, "intraday_good_quote_guarded_v0_1.json", tsis_artifacts_dir)
    payload = _payload(result)
    assert result.returncode == 0, result.stderr + result.stdout
    assert payload["status"] == "passed"
    assert payload["hard_fail_count"] == 0
    assert payload["review_fail_count"] == 0
    assert payload["materialization_allowed"] is True


def test_intraday_event_candidate_blocks_raw_only_promoted(tsis_artifacts_dir: Path) -> None:
    result = _run_validator(INTRADAY_DATASET_ID, "intraday_bad_raw_only_promoted_v0_1.json", tsis_artifacts_dir)
    payload = _payload(result)
    assert result.returncode != 0
    ids = _validator_ids(payload)
    assert "intraday_event_bad_qg_view_false_for_canonical" in ids
    assert "intraday_event_bad_quote_guarded_not_confirmed" in ids
    assert "intraday_event_bad_raw_only_promoted" in ids
    assert "intraday_event_bad_raw_spike_selected" in ids


def test_intraday_event_candidate_blocks_future_cutoff_and_open_bar(tsis_artifacts_dir: Path) -> None:
    result = _run_validator(INTRADAY_DATASET_ID, "intraday_bad_future_cutoff_v0_1.json", tsis_artifacts_dir)
    payload = _payload(result)
    assert result.returncode != 0
    ids = _validator_ids(payload)
    assert "event_bad_source_cutoff_future" in ids
    assert "intraday_event_bad_bar_not_closed" in ids
