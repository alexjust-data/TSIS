from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_trading_activity_binding_a_multisession_pilot.py"
UTC = UTC


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_raw(root: Path, ticker: str, value: date, opening: datetime) -> None:
    path = (
        root
        / ticker
        / f"year={value.year:04d}"
        / f"month={value.month:02d}"
        / f"day={value.isoformat()}"
        / "market.parquet"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = opening.replace(tzinfo=None) + timedelta(seconds=2)
    pd.DataFrame(
        {
            "ticker": [ticker, ticker],
            "date": [value.isoformat(), value.isoformat()],
            "timestamp": [timestamp, timestamp],
            "price": [2.0, 2.0],
            "size": [100, 100],
            "exchange": [11, 11],
            "conditions": [[], []],
            "year": [value.year, value.year],
            "month": [value.month, value.month],
            "day": [value.isoformat(), value.isoformat()],
        }
    ).to_parquet(path, index=False)


def _write_acquisition(root: Path, ticker: str, dates: list[date]) -> None:
    run = root / "fixture_shard_01"
    run.mkdir(parents=True)
    expected_columns = ["task_key", "ticker", "date", "session", "expected_file"]
    event_columns = expected_columns[:-1] + [
        "status",
        "rows",
        "file",
        "elapsed_sec",
        "processed_at_utc",
        "error",
    ]
    with (run / "expected_manifest_trades_ticks.csv").open(
        "w", encoding="utf-8", newline=""
    ) as expected_handle, (run / "download_events_trades_ticks_current.csv").open(
        "w", encoding="utf-8", newline=""
    ) as event_handle:
        expected_writer = csv.writer(expected_handle)
        event_writer = csv.writer(event_handle)
        expected_writer.writerow(expected_columns)
        event_writer.writerow(event_columns)
        for value in dates:
            key = f"{ticker}|{value.isoformat()}|market"
            expected_writer.writerow([key, ticker, value.isoformat(), "market", "fixture"])
            event_writer.writerow(
                [
                    key,
                    ticker,
                    value.isoformat(),
                    "market",
                    "DOWNLOADED_OK",
                    2,
                    "fixture",
                    0.1,
                    "2025-01-01T00:00:00Z",
                    "",
                ]
            )


def _fixture(tmp_path: Path) -> Path:
    ticker = "TST"
    instrument_id = "fixture:TST"
    dates = [date(2025, 1, 2), date(2025, 1, 3)]
    openings = [
        datetime(2025, 1, 2, 14, 30, tzinfo=UTC),
        datetime(2025, 1, 3, 14, 30, tzinfo=UTC),
    ]
    closes = [openings[0] + timedelta(seconds=11), openings[1] + timedelta(seconds=7)]

    calendar_path = tmp_path / "calendar.parquet"
    pd.DataFrame(
        {
            "session_date": dates,
            "open_utc": openings,
            "close_utc": closes,
            "open_et": openings,
            "close_et": closes,
            "session_minutes": [11 / 60, 7 / 60],
            "is_early_close": [False, True],
            "year": [2025, 2025],
            "month": [1, 1],
            "dow": ["Thursday", "Friday"],
            "calendar": ["XNYS", "XNYS"],
            "timezone": ["America/New_York", "America/New_York"],
            "source_calendar_artifact": ["fixture", "fixture"],
            "build_run_id": ["fixture_calendar", "fixture_calendar"],
            "schema_version": ["v0_1", "v0_1"],
            "created_at_utc": ["2025-01-01T00:00:00Z"] * 2,
        }
    ).to_parquet(calendar_path, index=False)

    identity_path = tmp_path / "instrument_master.parquet"
    pd.DataFrame(
        {
            "instrument_id": [instrument_id],
            "ticker": [ticker],
            "valid_from": [datetime(2020, 1, 1)],
            "valid_to": [pd.NaT],
        }
    ).to_parquet(identity_path, index=False)

    condition_path = tmp_path / "conditions.csv"
    condition_path.write_text(
        "condition_id,condition_name,condition_type,legacy,provider_consolidated_updates_volume,provider_consolidated_updates_high_low,provider_consolidated_updates_open_close,policy_review_state,semantic_class,activity_event_effect,share_volume_effect,dollar_volume_effect,causal_arrival_effect,price_path_effect,reason_code,policy_confidence,historical_temporality_state,policy_id\n",
        encoding="utf-8",
    )

    foundation_root = tmp_path / "foundation"
    foundation_root.mkdir()
    pd.DataFrame(
        {
            "file": ["fixture1", "fixture2"],
            "ticker": [ticker, ticker],
            "date": pd.to_datetime(dates),
            "severity": ["REVIEW_NOT_REHABILITATED", "GOOD"],
            "sample_stratum": ["fixture", "fixture"],
            "n_trades": [2, 2],
            "volume_total": [200.0, 200.0],
            "duplicate_exact_ratio_pct_raw": [50.0, 50.0],
            "max_trades_same_timestamp_raw": [2, 2],
            "negative_price_rows_raw": [0, 0],
            "negative_size_rows_raw": [0, 0],
            "missing_required_cols_count": [0, 0],
            "dtype_mismatches_count": [0, 0],
            "timestamp_out_of_partition_day": [False, False],
            "acceptance_label": ["BAD", "GOOD"],
        }
    ).to_parquet(foundation_root / "raw_metrics_00001.parquet", index=False)

    raw_root = tmp_path / "raw"
    for value, opening in zip(dates, openings, strict=False):
        _write_raw(raw_root, ticker, value, opening)

    acquisition_root = tmp_path / "acquisition"
    _write_acquisition(acquisition_root, ticker, dates)

    config = {
        "config_id": "fixture_multisession_v0_1",
        "scope": {
            "scope_id": "fixture_rth",
            "pilot_scope_id": "fixture_two_sessions",
            "ticker": ticker,
            "instrument_id": instrument_id,
            "calendar": "XNYS",
            "session_start": dates[0].isoformat(),
            "session_end": dates[-1].isoformat(),
            "expected_session_count": 2,
            "warmup_end": dates[0].isoformat(),
            "evaluation_start": dates[-1].isoformat(),
            "evaluation_end": dates[-1].isoformat(),
            "expected_evaluation_session_count": 1,
            "decision_frequency_seconds": 1,
            "decision_grid_boundary": "OPEN_EXCLUSIVE_CLOSE_EXCLUSIVE",
        },
        "binding": {
            "binding_id": "fixture_binding_a",
            "feature_spec_id": "fixture_feature_spec",
            "feature_version": "v0_2",
            "windows_seconds": [5, 15, 30, 60, 300],
            "short_long_pairs_seconds": [[5, 60], [15, 300]],
            "baseline_candidates": ["B20", "B60", "B120"],
            "trade_eligibility_policy_id": "fixture_policy",
            "duplicate_policy_id": "PRESERVE_EXACT_DUPLICATES_PRIMARY_V0_1",
            "coverage_mode": "INFERRED_FROM_SUCCESSFUL_FULL_RTH_REQUEST",
            "latency_policy_id": "FIXTURE_1000MS",
            "simulated_latency_ms": 1000,
            "source_dataset_id": "fixture_raw",
            "source_schema_version": "fixture_v0_1",
            "lineage_manifest_id": "fixture_lineage",
        },
        "sources": {
            "raw_trade_root": str(raw_root),
            "calendar_path": str(calendar_path),
            "calendar_expected_sha256": _sha256(calendar_path),
            "calendar_build_run_id": "fixture_calendar",
            "instrument_master_path": str(identity_path),
            "instrument_master_expected_sha256": _sha256(identity_path),
            "instrument_master_build_run_id": "fixture_identity",
            "condition_policy_matrix_path": str(condition_path),
            "condition_policy_matrix_expected_sha256": _sha256(condition_path),
            "foundation_57f_shards_root": str(foundation_root),
            "acquisition_manifest_root": str(acquisition_root),
        },
        "outputs": {
            "heavy_output_root": str(tmp_path / "outputs"),
            "runtime_root": str(tmp_path / "runtime"),
            "pointer_root": str(tmp_path / "pointers"),
            "parquet_compression": "zstd",
            "overwrite_policy": "NEVER",
            "resume_policy": "RESUME_HASH_VALIDATED_COMPLETE_PARTITIONS",
        },
        "operation": {
            "heartbeat_interval_seconds": 1,
            "heartbeat_stale_after_seconds": 3,
            "maximum_projected_output_gib": 1,
            "minimum_free_space_gib": 1,
            "minimum_free_space_multiplier": 1,
            "partition_batch_seconds": 10,
            "kernel_equivalence_seed": 7,
            "kernel_equivalence_random_samples_per_session": 5,
        },
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config_path


def _run(config: Path, run_id: str, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--config",
            str(config),
            "--run-id",
            run_id,
            "--skip-disk-gate",
            *extra,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_two_session_smoke_controlled_stop_resume_and_complete(tmp_path: Path):
    config = _fixture(tmp_path)
    run_id = "fixture_binding_a_run"
    interrupted = _run(config, run_id, "--stop-after-stage", "STAGE_5")
    assert interrupted.returncode == 2, interrupted.stderr
    runtime = tmp_path / "runtime" / run_id
    assert json.loads((runtime / "final_manifest.json").read_text())["status"] == "INTERRUPTED_COOPERATIVE"

    completed = _run(config, run_id, "--resume")
    assert completed.returncode == 0, completed.stderr + completed.stdout
    final = json.loads((runtime / "final_manifest.json").read_text())
    assert final["status"] == "COMPLETE"

    output = tmp_path / "outputs" / f"run_id={run_id}"
    summary = json.loads((output / "metadata" / "run_summary.json").read_text())
    assert summary["run_completion"] == "PASS"
    assert summary["row_counts"] == {
        "current_state_rows": 80,
        "multiscale_rows": 32,
        "baseline_rows": 90,
    }
    dense = pd.read_parquet(output / "scope" / "dense_input_manifest.parquet")
    assert len(dense) == 2
    assert set(dense["foundation_quality_label"]) == {"BAD", "GOOD"}
    audits = pd.read_parquet(output / "scope" / "selected_session_local_audit.parquet")
    assert len(audits) == 2 * 4
    assert audits["automatic_exclusion_applied"].eq(False).all()
    assert (output / "current_state" / "ticker=TST" / "session_date=2025-01-02" / "part-00000.parquet").is_file()
    assert (output / "multiscale_contrast" / "ticker=TST" / "session_date=2025-01-03" / "part-00000.parquet").is_file()
    assert (output / "pit_baseline_and_surprise" / "ticker=TST" / "session_date=2025-01-03" / "part-00000.parquet").is_file()
    pointer = tmp_path / "pointers" / run_id / "run_pointer_manifest.json"
    assert json.loads(pointer.read_text())["status"] == "COMPLETE"


def _partition_hashes(root: Path, family: str) -> dict[str, str]:
    return {
        str(path.relative_to(root)): _sha256(path)
        for path in sorted((root / family).rglob("part-*.parquet"))
    }


def test_cpp_stage8_engine_matches_python_and_persists_fingerprint(
    tmp_path: Path,
) -> None:
    config = _fixture(tmp_path)
    python_run_id = "fixture_binding_a_python"
    cpp_run_id = "fixture_binding_a_cpp"
    python_result = _run(config, python_run_id, "--stage8-engine", "python")
    assert python_result.returncode == 0, python_result.stderr + python_result.stdout
    cpp_result = _run(config, cpp_run_id, "--stage8-engine", "cpp")
    assert cpp_result.returncode == 0, cpp_result.stderr + cpp_result.stdout

    python_output = tmp_path / "outputs" / f"run_id={python_run_id}"
    cpp_output = tmp_path / "outputs" / f"run_id={cpp_run_id}"
    for family in ("current_state", "multiscale_contrast", "pit_baseline_and_surprise"):
        assert _partition_hashes(python_output, family) == _partition_hashes(
            cpp_output, family
        )

    runtime = tmp_path / "runtime" / cpp_run_id
    pointer = tmp_path / "pointers" / cpp_run_id / "run_pointer_manifest.json"
    manifests = [
        json.loads((runtime / "pre_manifest.json").read_text()),
        json.loads((runtime / "final_manifest.json").read_text()),
        json.loads((cpp_output / "metadata" / "lineage_manifest.json").read_text()),
        json.loads((cpp_output / "metadata" / "run_summary.json").read_text()),
        json.loads(pointer.read_text()),
    ]
    fingerprints = {
        manifest["stage8_engine"]["engine_fingerprint_sha256"]
        for manifest in manifests
    }
    assert len(fingerprints) == 1
    for manifest in manifests:
        engine = manifest["stage8_engine"]
        assert engine["engine_name"] == "cpp"
        assert engine["semantic_oracle_engine_id"].endswith("python_reference_v0_2")
        assert "native_binary" in {
            component["role"] for component in engine["components"]
        }


def test_resume_rejects_stage8_engine_fingerprint_change(tmp_path: Path) -> None:
    config = _fixture(tmp_path)
    run_id = "fixture_binding_a_engine_change"
    interrupted = _run(
        config,
        run_id,
        "--stage8-engine",
        "python",
        "--stop-after-stage",
        "STAGE_5",
    )
    assert interrupted.returncode == 2, interrupted.stderr
    rejected = _run(config, run_id, "--resume", "--stage8-engine", "cpp")
    assert rejected.returncode != 0
    assert "engine fingerprint differs" in rejected.stderr

