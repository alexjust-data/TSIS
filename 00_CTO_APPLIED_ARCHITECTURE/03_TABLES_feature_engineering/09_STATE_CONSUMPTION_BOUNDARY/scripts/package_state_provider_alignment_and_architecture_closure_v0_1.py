from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\TSIS_Data")
FEATURE = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE / "08_RUNTIME_CAPABILITIES"
BOUNDARY = FEATURE / "09_STATE_CONSUMPTION_BOUNDARY"
SCALE_RUN = (
    RUNTIME
    / "runs"
    / "market_state_on_demand_scale_validation_v0_1_20260727T133641Z"
)
PROFILE = (
    FEATURE
    / "06_MARKET_STATE_INTEGRATION"
    / "official_profiles"
    / "market_state_core_four_intraday_profile_v0_1"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


FILES = [
    # Conceptual and live authority surfaces.
    FEATURE / "00_TABLES_MARKET_STATE_EVENT_STATE.md",
    FEATURE / "00_TABLES_MARKET_STATE_EVENT_STATE_authority_stratification_matrix_v0_1.json",
    FEATURE / "00_TABLES_MARKET_STATE_EVENT_STATE_authority_stratification_readout_v0_1.md",
    FEATURE / "_00_TABLES_EXECUTION_STATE.md",
    FEATURE / "03_INFORMATION_OBJECTS" / "01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md",
    PROFILE / "PROFILE_MANIFEST.json",
    PROFILE / "PHYSICAL_SCHEMA_CONTRACT.json",
    FEATURE
    / "07_EVENT_STATE_INTEGRATION"
    / "event_type_registry_post_initial_admission_snapshot_v0_1.json",
    FEATURE / "99_ruta_de_trabajo.md",
    FEATURE / "AGENT.md",
    ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "CHANGELOG.md",
    RUNTIME / "README.md",
    BOUNDARY / "README.md",
    # Accepted provider v0.1.2 executable authority needed by the alignment.
    RUNTIME / "state_resolution_request_contract_v0_1_2.json",
    RUNTIME / "runtime_user_invocation_response_contract_v0_1_2.json",
    RUNTIME / "state_bundle_manifest_contract_v0_1_2.json",
    RUNTIME / "runtime_provider_contract_schema_hardening_v0_1_2_external_audit_acceptance_readout_v0_1.md",
    RUNTIME / "scripts" / "runtime_provider_contract_schema_hardening_v0_1_2_runner.py",
    RUNTIME / "scripts" / "runtime_provider_contract_schema_hardening_v0_1_2_patch.py",
    RUNTIME / "scripts" / "runtime_provider_contract_schema_hardening_v0_1_2_reaudit_patch.py",
    # Exact scale-validation metadata; parquet is deliberately excluded.
    SCALE_RUN / "final_manifest.json",
    SCALE_RUN / "candidate_output_manifest.json",
    SCALE_RUN / "candidate_registry_entry.json",
    SCALE_RUN / "market_state_validation_report.json",
    SCALE_RUN / "market_state_temporal_legality_report.json",
    SCALE_RUN / "lineage_manifest.json",
    SCALE_RUN / "request_record.json",
    SCALE_RUN / "execution_plan.json",
    # Timestamp contract evidence.
    BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_authorization_v0_1.md",
    BOUNDARY / "configs" / "market_state_core_four_replay_availability_timestamp_contract_scope_v0_1.json",
    BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_v0_1.md",
    BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_v0_1.json",
    BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_matrix_v0_1.json",
    BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_readout_v0_1.md",
    BOUNDARY / "scripts" / "market_state_core_four_replay_availability_timestamp_contract_runner_v0_1.py",
    # Sidecar and v0.1.2 reissue evidence.
    BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1.json",
    BOUNDARY / "market_state_core_four_scale_validation_exact_requested_context_ledger_v0_1.json",
    BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json",
    BOUNDARY / "runtime_v0_1_2_scale_validation_exact_reuse_equivalence_record_v0_1.json",
    BOUNDARY
    / "configs"
    / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_scope_v0_1.json",
    BOUNDARY
    / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_matrix_v0_1.json",
    BOUNDARY
    / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_readout_v0_1.md",
    BOUNDARY / "scripts" / "market_state_core_four_scale_validation_replay_sidecar_and_reissue_runner_v0_1.py",
    BOUNDARY
    / "scripts"
    / "market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_runner_v0_1.py",
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_resolution_request_instance_v0_1.json",
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_runtime_invocation_response_v0_1.json",
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_bundle_manifest_v0_1.json",
    RUNTIME
    / "configs"
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_scope_v0_1.json",
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_matrix_v0_1.json",
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_readout_v0_1.md",
    RUNTIME
    / "scripts"
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_runner.py",
    # Physical evidence alignment v0.2 closure.
    BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_authorization_v0_2.md",
    BOUNDARY / "configs" / "state_bundle_manifest_physical_evidence_alignment_scope_v0_2.json",
    BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_matrix_v0_2.json",
    BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_readout_v0_2.md",
    BOUNDARY / "scripts" / "state_bundle_manifest_physical_evidence_alignment_runner_v0_2.py",
    # Reproducible packager.
    Path(__file__),
]


def main() -> int:
    missing = [rel(path) for path in FILES if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing package inputs: {missing}")

    stamp = datetime.now(timezone.utc).replace(microsecond=0)
    created_at = stamp.isoformat().replace("+00:00", "Z")
    zip_path = FEATURE / (
        "state_provider_alignment_v0_2_and_architecture_stratification_closure_"
        f"{stamp.strftime('%Y%m%dT%H%M%SZ')}.zip"
    )
    unique_files = sorted(set(FILES), key=rel)
    artifacts = [
        {
            "path": rel(path),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for path in unique_files
    ]
    provenance = {
        "package_role": "final_alignment_v0_2_and_documentary_stratification_closure",
        "created_at_utc": created_at,
        "supersedes_review_package": {
            "file_name": (
                "state_provider_replay_and_architecture_evidence_consolidated_"
                "20260730T064355Z.zip"
            ),
            "sha256": "44c4e180c159335e1d38f59e92010b64630fbda2064884d6884b90534fb983bb",
        },
        "closed_paths": {
            "physical_evidence_alignment_v0_2": (
                "CLOSED_PASS_PHYSICAL_EVIDENCE_ALIGNED_READY_FOR_BOUNDED_READ_"
                "AUTHORIZATION_WITH_RESTRICTIONS_NO_PHYSICAL_READ"
            ),
            "conceptual_authority_stratification": (
                "CLOSED_DOCUMENTARY_AUTHORITY_STRATIFICATION_PASS_"
                "NO_EXECUTABLE_SEMANTIC_CHANGE"
            ),
        },
        "explicit_boundaries": {
            "parquet_included": False,
            "physical_state_rows_included": False,
            "backtester_files_included": False,
            "physical_read_authorization_issued": False,
            "StateReplayFeed_authorized": False,
            "backtest_consumption": False,
            "production": False,
            "downstream": False,
        },
    }
    provenance_bytes = (
        json.dumps(provenance, indent=2, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    artifacts.append(
        {
            "path": "PACKAGE_PROVENANCE.json",
            "sha256": hashlib.sha256(provenance_bytes).hexdigest(),
            "size_bytes": len(provenance_bytes),
        }
    )
    manifest = {
        "package_id": (
            "state_provider_alignment_v0_2_and_architecture_stratification_closure"
        ),
        "created_at_utc": created_at,
        "file_count": len(artifacts),
        "artifacts": artifacts,
        "explicitly_excluded": [
            "02_TSIS_BACKTEST_ENGINE",
            "parquet files",
            "physical state rows",
            "StateReplayFeed implementation",
            "backtest runs",
            "production/downstream artifacts",
        ],
    }
    manifest_bytes = (
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n"
    ).encode("utf-8")

    with zipfile.ZipFile(zip_path, "x", zipfile.ZIP_DEFLATED) as archive:
        for path in unique_files:
            archive.write(path, rel(path))
        archive.writestr("PACKAGE_PROVENANCE.json", provenance_bytes)
        archive.writestr("PACKAGE_MANIFEST.json", manifest_bytes)

    print(
        json.dumps(
            {
                "zip_path": str(zip_path),
                "zip_sha256": sha256_file(zip_path),
                "artifact_count": len(artifacts),
                "zip_entries": len(artifacts) + 1,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
