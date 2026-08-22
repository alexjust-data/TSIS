from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_trading_activity_stage8_target_only_recovery as runner  # noqa: E402
import trading_activity_stage8_target_only_contract as contract  # noqa: E402


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _target_row(ordinal: int, session: date, early: bool = False) -> dict:
    seconds = 12600 if early else 23400
    return {
        "block_id": "ta3b:block000",
        "target_ordinal": ordinal,
        "instrument_id": "instrument:TEST",
        "ticker_as_of_session": "TEST",
        "session_date": session,
        "decision_seconds": float(seconds),
        "session_minutes": float(seconds / 60),
        "is_early_close": early,
        "expected_current_state_rows": 1.0,
        "expected_multiscale_contrast_rows": 1.0,
        "expected_pit_baseline_rows": 1.0,
    }


def _family_table(family: str, target: dict, rows: int) -> pa.Table:
    session = target["session_date"]
    timestamp = datetime.combine(session, datetime.min.time(), tzinfo=UTC)
    values: dict[str, pa.Array] = {
        "instrument_id": pa.array([target["instrument_id"]] * rows),
        "ticker": pa.array([target["ticker_as_of_session"]] * rows),
        "session_date": pa.array([session] * rows, type=pa.date32()),
        "decision_timestamp": pa.array(
            [timestamp + timedelta(seconds=index) for index in range(rows)],
            type=pa.timestamp("us", tz="UTC"),
        ),
        "binding_id": pa.array(["binding_a_v0_2"] * rows),
        "feature_spec_id": pa.array(["spec"] * rows),
        "feature_version": pa.array(["v0_2"] * rows),
        "scope_id": pa.array(["scope"] * rows),
        "source_dataset_id": pa.array(["source"] * rows),
        "coverage_state": pa.array(["OBSERVED"] * rows),
        "calculation_state": pa.array(["AVAILABLE"] * rows),
        "future_window_used": pa.array([False] * rows),
        "feature_input_max_available_at": pa.array(
            [timestamp] * rows, type=pa.timestamp("us", tz="UTC")
        ),
        "lineage_manifest_id": pa.array(["lineage"] * rows),
    }
    if family == "current_state":
        values["window_seconds"] = pa.array([5] * rows, type=pa.int64())
    elif family == "multiscale_contrast":
        values["short_window_seconds"] = pa.array([5] * rows, type=pa.int64())
        values["long_window_seconds"] = pa.array([60] * rows, type=pa.int64())
        values["pair_id"] = pa.array(["5_60"] * rows)
    else:
        values["window_seconds"] = pa.array([5] * rows, type=pa.int64())
        values["baseline_candidate_id"] = pa.array(["B20"] * rows)
        values["first_reference_date"] = pa.array(
            [session - timedelta(days=30)] * rows, type=pa.date32()
        )
        values["last_reference_date"] = pa.array(
            [session - timedelta(days=1)] * rows, type=pa.date32()
        )
        values["baseline_input_max_available_at"] = pa.array(
            [timestamp - timedelta(days=1)] * rows,
            type=pa.timestamp("us", tz="UTC"),
        )
    return pa.table(values)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def _fixture_plan(tmp_path: Path) -> tuple[Path, Path]:
    source_root = tmp_path / "source"
    source_output = source_root / "outputs"
    source_runtime = source_root / "runtime"
    engine = "engine-fingerprint"
    completed_by_shard: dict[int, list[dict]] = {index: [] for index in range(4)}
    for index in range(240):
        shard = index // 60
        block_id = f"ta3b:block{index:03d}"
        block_run_id = f"block_{index:03d}"
        output_root = source_output / f"run_id={block_run_id}"
        block_final = source_runtime / f"ta3c1_s{shard}" / "blocks" / block_run_id / "final_manifest.json"
        _write_json(
            block_final,
            {
                "status": "COMPLETE",
                "output_run_root": str(output_root),
                "stage8_engine": {
                    "engine_name": "cpp",
                    "engine_fingerprint_sha256": engine,
                },
            },
        )
        completed_by_shard[shard].append(
            {"block_id": block_id, "block_run_id": block_run_id, "return_code": 0}
        )
    for shard in range(4):
        _write_json(
            source_runtime / f"ta3c1_s{shard}" / "final_manifest.json",
            {
                "final_status": "COMPLETE",
                "completed_blocks": completed_by_shard[shard],
                "failed_blocks": [],
            },
        )

    start = date(2010, 1, 1)
    targets = [
        _target_row(index + 1, start + timedelta(days=index), early=index == 999)
        for index in range(2400)
    ]
    target_path = tmp_path / "targets.parquet"
    pq.write_table(pa.Table.from_pylist(targets), target_path)
    sample_manifest = tmp_path / "sample_manifest.json"
    _write_json(sample_manifest, {"status": "FROZEN", "targets": 2400})

    selected = [targets[0], targets[999]]
    target_output = source_output / "run_id=block_000"
    validation = target_output / "validation"
    metadata = target_output / "metadata"
    _write_json(metadata / "lineage_manifest.json", {"future_window_used": False})
    for name in (
        "grain_uniqueness_validation.json",
        "temporal_legality_validation.json",
        "baseline_reference_validation.json",
    ):
        _write_json(validation / name, {"status": "PASS", "failures": []})
    hash_rows = []
    for target in selected:
        expected = contract.expected_physical_counts(target)
        for family in contract.PHYSICAL_FAMILY_KEYS:
            path = (
                target_output
                / family
                / "ticker=TEST"
                / f"session_date={target['session_date'].isoformat()}"
                / "part-00000.parquet"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            pq.write_table(_family_table(family, target, expected[family]), path)
            digest = _sha(path)
            path.with_name(path.name + ".sha256").write_text(digest, encoding="utf-8")
            hash_rows.append(
                {
                    "path": str(path),
                    "sha256": digest,
                    "rows": expected[family],
                    "bytes": path.stat().st_size,
                    "resumed": False,
                    "run_id": "source-run",
                }
            )
    hash_index = validation / "output_hashes.parquet"
    pq.write_table(pa.Table.from_pylist(hash_rows), hash_index)
    hash_index.with_name(hash_index.name + ".sha256").write_text(
        _sha(hash_index), encoding="utf-8"
    )

    run_root = tmp_path / "probe"
    controls = [
        {
            "control_id": f"RM-MAT-CTRL-00{index}",
            "source_incident_id": f"RM-MAT-INC-00{index}",
            "applicability": "applicable",
            "status": "PENDING_RUNTIME_PROBE",
        }
        for index in (1, 2, 3, 4, 5)
    ]
    full_contract = contract.aggregate_contract(targets)
    selected_contract = contract.aggregate_contract(selected)
    plan = {
        "plan_schema_version": runner.EXPECTED_PLAN_SCHEMA,
        "artifact_status": "PREREGISTERED_PROBE_AUTHORIZED",
        "mode": "PROBE",
        "run_id": "fixture_target_only_probe",
        "probe_run_roots": {str(index): str(run_root / f"shard_{index}") for index in range(4)},
        "run_root": str(run_root),
        "source_run_root": str(source_root),
        "source_runtime_root": str(source_runtime),
        "source_output_root": str(source_output),
        "source_blocks_recomputed": 0,
        "target_table": str(target_path),
        "target_table_sha256": _sha(target_path),
        "sample_manifest": str(sample_manifest),
        "sample_manifest_sha256": _sha(sample_manifest),
        "expected_stage8_engine_fingerprint": engine,
        "source_shards": [
            {"shard_index": index, "run_id": f"ta3c1_s{index}", "expected_block_count": 60}
            for index in range(4)
        ],
        "full_scope_contract": full_contract,
        "probe_target_keys_by_shard": {
            "0": [
                {
                    "block_id": row["block_id"],
                    "instrument_id": row["instrument_id"],
                    "ticker_as_of_session": row["ticker_as_of_session"],
                    "session_date": row["session_date"].isoformat(),
                }
                for row in selected
            ],
            "1": [],
            "2": [],
            "3": [],
        },
        "probe_scope_contracts": {
            "0": selected_contract,
            "1": selected_contract,
            "2": selected_contract,
            "3": selected_contract,
        },
        "runner_sha256": _sha(runner.SCRIPT_PATH),
        "contract_sha256": _sha(Path(contract.__file__)),
        "monitor_sha256": _sha(runner.MONITOR_PATH),
        "inherited_incident_controls": controls,
        "resume_policy": "SAME_IDENTITY_ONLY",
        "canonical_promotion_authorized": False,
        "success_criteria": ["fixture terminal path pass"],
    }
    plan_path = tmp_path / "plan.json"
    _write_json(plan_path, plan)
    return plan_path, run_root / "shard_0"


def test_cardinality_contract_excludes_metadata_from_physical_domain() -> None:
    row = _target_row(1, date(2024, 7, 3), early=True)
    expected = contract.expected_physical_counts(row)
    assert contract.decision_points(row) == 12599
    assert expected == {
        "current_state": 62995,
        "multiscale_contrast": 25198,
        "pit_baseline_and_surprise": 188985,
    }
    contract.assert_physical_counts(expected, expected)
    with pytest.raises(AssertionError, match="three families"):
        contract.assert_physical_counts(
            {**expected, "decision_points_total": 12599}, expected
        )


def test_exact_sparse_membership_is_not_a_date_interval() -> None:
    rows = [
        _target_row(1, date(2024, 1, 2)),
        _target_row(2, date(2024, 8, 30)),
    ]
    result = contract.aggregate_contract(rows)
    assert result["metadata_scalars"]["target_count"] == 2
    assert result["metadata_scalars"]["partition_count"] == 6
    assert result["physical_family_row_counts"]["current_state"] == 233990


def test_duplicate_exact_target_fails_closed() -> None:
    row = _target_row(1, date(2024, 1, 2))
    with pytest.raises(ValueError, match="Duplicate exact target key"):
        contract.aggregate_contract([row, {**row, "target_ordinal": 2}])


def test_terminal_rehearsal_passes_without_recomputing_blocks(tmp_path: Path) -> None:
    plan_path, run_root = _fixture_plan(tmp_path)
    assert runner.execute(plan_path, probe_shard=0, resume=False) == 0
    final = json.loads(
        (run_root / "runtime" / "final_manifest.json").read_text(encoding="utf-8")
    )
    assert final["status"] == "PASS"
    assert final["calculation_status"] == "NOT_EXECUTED_REUSED_FROZEN_OUTPUTS"
    assert final["source_blocks_recomputed"] == 0
    assert final["exact_target_contract"]["metadata_scalars"]["target_count"] == 2
    assert final["hash_validation"] == {"selected": 6, "passed": 6, "failed": 0}
    assert all(
        item["runtime_status"] == "PASS"
        for item in final["inherited_incident_controls"]
    )
    assert {
        item["control_id"] for item in final["inherited_incident_controls"]
    } == {f"RM-MAT-CTRL-00{index}" for index in (1, 2, 3, 4, 5)}


def test_terminal_rehearsal_fails_closed_on_partition_corruption(tmp_path: Path) -> None:
    plan_path, run_root = _fixture_plan(tmp_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    target = Path(plan["source_output_root"]) / "run_id=block_000" / "current_state" / "ticker=TEST" / "session_date=2010-01-01" / "part-00000.parquet"
    with target.open("ab") as handle:
        handle.write(b"corruption")
    assert runner.execute(plan_path, probe_shard=0, resume=False) == 1
    final = json.loads(
        (run_root / "runtime" / "final_manifest.json").read_text(encoding="utf-8")
    )
    assert final["status"] == "FAILED"
    assert final["certification_status"] == "FAILED"
    assert final["source_blocks_recomputed"] == 0
    assert "File size mismatch" in final["failure_reason"]
