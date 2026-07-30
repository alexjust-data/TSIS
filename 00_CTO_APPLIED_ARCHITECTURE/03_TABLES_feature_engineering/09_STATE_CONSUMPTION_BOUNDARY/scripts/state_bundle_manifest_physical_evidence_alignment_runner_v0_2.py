from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

ROOT = Path(r"C:\TSIS_Data")
FEATURE = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE / "08_RUNTIME_CAPABILITIES"
BOUNDARY = FEATURE / "09_STATE_CONSUMPTION_BOUNDARY"
MARKET_PROFILE = (
    FEATURE
    / "06_MARKET_STATE_INTEGRATION"
    / "official_profiles"
    / "market_state_core_four_intraday_profile_v0_1"
)
SCALE_RUN = (
    RUNTIME
    / "runs"
    / "market_state_on_demand_scale_validation_v0_1_20260727T133641Z"
)

GATE = "state_bundle_manifest_physical_evidence_alignment_v0_2"
STATUS = (
    "CLOSED_PASS_PHYSICAL_EVIDENCE_ALIGNED_READY_FOR_BOUNDED_READ_"
    "AUTHORIZATION_WITH_RESTRICTIONS_NO_PHYSICAL_READ"
)

PROVIDER_ACCEPTANCE = (
    RUNTIME
    / "runtime_provider_contract_schema_hardening_v0_1_2_external_audit_acceptance_readout_v0_1.md"
)
REQUEST_CONTRACT = RUNTIME / "state_resolution_request_contract_v0_1_2.json"
RESPONSE_CONTRACT = RUNTIME / "runtime_user_invocation_response_contract_v0_1_2.json"
BUNDLE_CONTRACT = RUNTIME / "state_bundle_manifest_contract_v0_1_2.json"
REQUEST = (
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_resolution_request_instance_v0_1.json"
)
RESPONSE = (
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_runtime_invocation_response_v0_1.json"
)
BUNDLE = (
    RUNTIME
    / "runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_bundle_manifest_v0_1.json"
)
FINAL_MANIFEST = SCALE_RUN / "final_manifest.json"
OUTPUT_MANIFEST = SCALE_RUN / "candidate_output_manifest.json"
REGISTRY_ENTRY = SCALE_RUN / "candidate_registry_entry.json"
VALIDATION_REPORT = SCALE_RUN / "market_state_validation_report.json"
TEMPORAL_REPORT = SCALE_RUN / "market_state_temporal_legality_report.json"
LINEAGE_MANIFEST = SCALE_RUN / "lineage_manifest.json"
ORIGINAL_REQUEST = SCALE_RUN / "request_record.json"
ORIGINAL_PLAN = SCALE_RUN / "execution_plan.json"
PHYSICAL_SCHEMA = MARKET_PROFILE / "PHYSICAL_SCHEMA_CONTRACT.json"
PARQUET = SCALE_RUN / "market_state_scale_validation_candidate_v0_1.parquet"
TIMESTAMP_CONTRACT = (
    BOUNDARY / "market_state_core_four_replay_availability_timestamp_contract_v0_1.json"
)
SIDECAR_CONTRACT = (
    BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_contract_v0_1.json"
)
LEDGER = BOUNDARY / "market_state_core_four_scale_validation_exact_requested_context_ledger_v0_1.json"
SIDECAR = (
    BOUNDARY / "market_state_core_four_replay_availability_evidence_sidecar_manifest_v0_1.json"
)
EQUIVALENCE = BOUNDARY / "runtime_v0_1_2_scale_validation_exact_reuse_equivalence_record_v0_1.json"
SOURCE_RUNNER = (
    BOUNDARY
    / "scripts"
    / "market_state_core_four_scale_validation_replay_sidecar_and_reissue_runner_v0_1.py"
)

OUTPUTS = {
    "authorization": BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_authorization_v0_2.md",
    "scope": BOUNDARY / "configs" / "state_bundle_manifest_physical_evidence_alignment_scope_v0_2.json",
    "matrix": BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_matrix_v0_2.json",
    "readout": BOUNDARY / "state_bundle_manifest_physical_evidence_alignment_readout_v0_2.md",
}

REQUIRED_CASE_IDS = [
    "ALIGN_V02_INPUTS_001",
    "ALIGN_V02_PROVIDER_AUTHORITY_001",
    "ALIGN_V02_REQUEST_SCHEMA_001",
    "ALIGN_V02_RESPONSE_SCHEMA_001",
    "ALIGN_V02_BUNDLE_SCHEMA_001",
    "ALIGN_V02_SIDECAR_SCHEMA_001",
    "ALIGN_V02_REQUEST_SEMANTIC_001",
    "ALIGN_V02_RESPONSE_SEMANTIC_001",
    "ALIGN_V02_BUNDLE_SEMANTIC_001",
    "ALIGN_V02_SIDECAR_SEMANTIC_001",
    "ALIGN_V02_DATASET_IDENTITY_001",
    "ALIGN_V02_ARTIFACT_HASH_CHAIN_001",
    "ALIGN_V02_COVERAGE_001",
    "ALIGN_V02_EXACT_REUSE_001",
    "ALIGN_V02_ROW_ADDRESSABILITY_001",
    "ALIGN_V02_TEMPORAL_LEGALITY_001",
    "ALIGN_V02_RESTRICTIONS_001",
    "ALIGN_V02_CROSS_ARTIFACT_VALIDATOR_001",
    "ALIGN_V02_NEG_WRONG_DATASET",
    "ALIGN_V02_NEG_MISSING_SIDECAR_HASH",
    "ALIGN_V02_NEG_WEAKENED_COVERAGE",
    "ALIGN_V02_BOUNDARIES_001",
]

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=True))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def provider_module() -> Any:
    spec = importlib.util.spec_from_file_location("scale_reissue", SOURCE_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {SOURCE_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract_validator(path: Path) -> Draft202012Validator:
    contract = read_json(path)
    schema = contract.get("json_schema", contract)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def schema_errors(validator: Draft202012Validator, document: dict[str, Any]) -> list[str]:
    return sorted(error.message for error in validator.iter_errors(document))


def artifact_hashes(bundle: dict[str, Any]) -> dict[str, str]:
    return {
        item["artifact_id"]: item["sha256"]
        for item in bundle.get("artifact_hashes", [])
        if isinstance(item, dict) and item.get("artifact_id") and item.get("sha256")
    }


def dataset_ref(bundle: dict[str, Any]) -> dict[str, Any]:
    return bundle.get("dataset_refs", {}).get("market_state_dataset_ref") or {}


def coverage_tuple(document: dict[str, Any]) -> tuple[int | None, ...]:
    coverage = document.get("coverage", document)
    return tuple(
        coverage.get(key)
        for key in (
            "requested_contexts",
            "represented_contexts",
            "unavailable_contexts",
            "blocked_contexts",
            "quarantined_contexts",
            "unaccounted_contexts",
        )
    )


def build_scope(now: str) -> dict[str, Any]:
    inputs = [
        PROVIDER_ACCEPTANCE,
        REQUEST_CONTRACT,
        RESPONSE_CONTRACT,
        BUNDLE_CONTRACT,
        REQUEST,
        RESPONSE,
        BUNDLE,
        FINAL_MANIFEST,
        OUTPUT_MANIFEST,
        REGISTRY_ENTRY,
        VALIDATION_REPORT,
        TEMPORAL_REPORT,
        LINEAGE_MANIFEST,
        ORIGINAL_REQUEST,
        ORIGINAL_PLAN,
        PHYSICAL_SCHEMA,
        TIMESTAMP_CONTRACT,
        SIDECAR_CONTRACT,
        LEDGER,
        SIDECAR,
        EQUIVALENCE,
        SOURCE_RUNNER,
    ]
    return {
        "gate": GATE,
        "created_at_utc": now,
        "status": "AUTHORIZED_AND_EXECUTED_READ_ONLY_METADATA_NO_PHYSICAL_READ",
        "owner_layer": "09_STATE_CONSUMPTION_BOUNDARY",
        "purpose": (
            "Prove that the accepted provider v0.1.2 request, response, bundle, exact-context "
            "ledger, replay sidecar and governed physical metadata identify one bounded "
            "Market State scale-validation candidate without opening its parquet."
        ),
        "authorized_inputs": [rel(path) for path in inputs],
        "parquet_path_identified_but_not_opened": rel(PARQUET),
        "authorized_outputs": {
            **{name: rel(path) for name, path in OUTPUTS.items()},
            "runner": rel(Path(__file__)),
        },
        "hard_boundaries": {
            "parquet_opened": False,
            "parquet_hash_recomputed": False,
            "physical_state_rows_read": 0,
            "StateReplayFeed_records_emitted": 0,
            "EventLoop_ticks": 0,
            "strategy_callbacks": 0,
            "orders_emitted": 0,
            "fills_emitted": 0,
            "PnL_calculated": False,
            "runtime_requests_executed": 0,
            "runtime_builds_executed": 0,
            "datasets_written": 0,
            "registry_mutations": 0,
            "backtest_consumption": False,
            "official_dataset": False,
            "production": False,
            "downstream": False,
        },
    }


def build_matrix(now: str) -> dict[str, Any]:
    module = provider_module()
    request = read_json(REQUEST)
    response = read_json(RESPONSE)
    bundle = read_json(BUNDLE)
    final_manifest = read_json(FINAL_MANIFEST)
    output_manifest = read_json(OUTPUT_MANIFEST)
    registry = read_json(REGISTRY_ENTRY)
    validation = read_json(VALIDATION_REPORT)
    temporal = read_json(TEMPORAL_REPORT)
    ledger = read_json(LEDGER)
    sidecar = read_json(SIDECAR)
    equivalence = read_json(EQUIVALENCE)

    request_validator = contract_validator(REQUEST_CONTRACT)
    response_validator = contract_validator(RESPONSE_CONTRACT)
    bundle_validator = contract_validator(BUNDLE_CONTRACT)
    sidecar_validator = contract_validator(SIDECAR_CONTRACT)

    rows: list[dict[str, Any]] = []

    def add(
        case_id: str,
        area: str,
        expected: str,
        observed: Any,
        result: str,
        evidence: list[Path],
    ) -> None:
        rows.append(
            {
                "case_id": case_id,
                "area": area,
                "expected": expected,
                "observed": observed,
                "result": result,
                "evidence_refs": [rel(path) for path in evidence],
            }
        )

    required_inputs = [
        PROVIDER_ACCEPTANCE,
        REQUEST_CONTRACT,
        RESPONSE_CONTRACT,
        BUNDLE_CONTRACT,
        REQUEST,
        RESPONSE,
        BUNDLE,
        FINAL_MANIFEST,
        OUTPUT_MANIFEST,
        REGISTRY_ENTRY,
        VALIDATION_REPORT,
        TEMPORAL_REPORT,
        LINEAGE_MANIFEST,
        ORIGINAL_REQUEST,
        ORIGINAL_PLAN,
        PHYSICAL_SCHEMA,
        TIMESTAMP_CONTRACT,
        SIDECAR_CONTRACT,
        LEDGER,
        SIDECAR,
        EQUIVALENCE,
        SOURCE_RUNNER,
    ]
    missing = [rel(path) for path in required_inputs if not path.exists()]
    add(
        "ALIGN_V02_INPUTS_001",
        "inventory",
        "All governed metadata inputs exist; parquet is identified but not opened.",
        {"missing": missing, "parquet_exists": PARQUET.exists()},
        "PASS" if not missing and PARQUET.exists() else "BLOCK",
        required_inputs,
    )

    provider_accepted = (
        "CLOSED_EXTERNAL_AUDIT_PASS_ACCEPTABLE_AS_PROVIDER_AUTHORITY_WITH_RESTRICTIONS"
        in read_text(PROVIDER_ACCEPTANCE)
    )
    add(
        "ALIGN_V02_PROVIDER_AUTHORITY_001",
        "provider_authority",
        "Provider v0.1.2 is the accepted restricted control-plane authority.",
        provider_accepted,
        "PASS" if provider_accepted else "BLOCK",
        [PROVIDER_ACCEPTANCE],
    )

    for case_id, name, validator, document, path in (
        ("ALIGN_V02_REQUEST_SCHEMA_001", "request", request_validator, request, REQUEST),
        ("ALIGN_V02_RESPONSE_SCHEMA_001", "response", response_validator, response, RESPONSE),
        ("ALIGN_V02_BUNDLE_SCHEMA_001", "bundle", bundle_validator, bundle, BUNDLE),
        ("ALIGN_V02_SIDECAR_SCHEMA_001", "sidecar", sidecar_validator, sidecar, SIDECAR),
    ):
        errors = schema_errors(validator, document)
        add(
            case_id,
            "schema",
            f"{name} validates against its accepted contract.",
            errors,
            "PASS" if not errors else "BLOCK",
            [path],
        )

    semantic_checks = [
        (
            "ALIGN_V02_REQUEST_SEMANTIC_001",
            module.provider_semantic_errors(request, "state_resolution_request"),
            REQUEST,
        ),
        (
            "ALIGN_V02_RESPONSE_SEMANTIC_001",
            module.provider_semantic_errors(response, "runtime_invocation_response"),
            RESPONSE,
        ),
        (
            "ALIGN_V02_BUNDLE_SEMANTIC_001",
            module.provider_semantic_errors(bundle, "state_bundle_manifest"),
            BUNDLE,
        ),
        (
            "ALIGN_V02_SIDECAR_SEMANTIC_001",
            module.sidecar_semantic_errors(sidecar),
            SIDECAR,
        ),
    ]
    for case_id, errors, path in semantic_checks:
        add(
            case_id,
            "semantic",
            "Accepted semantic validator returns no errors.",
            errors,
            "PASS" if not errors else "BLOCK",
            [path, SOURCE_RUNNER],
        )

    output_dataset_id = output_manifest.get("candidate_dataset_id")
    output_fingerprint = output_manifest.get("candidate_dataset_fingerprint")
    bundle_dataset = dataset_ref(bundle)
    identities = {
        "output_manifest": [output_dataset_id, output_fingerprint],
        "bundle": [
            bundle_dataset.get("dataset_id"),
            bundle_dataset.get("candidate_dataset_fingerprint"),
        ],
        "registry": [
            registry.get("dataset_id"),
            registry.get("candidate_dataset_fingerprint"),
        ],
        "sidecar": [
            sidecar.get("candidate_dataset_id"),
            sidecar.get("candidate_dataset_fingerprint"),
        ],
        "equivalence": [
            equivalence.get("candidate_dataset_id"),
            equivalence.get("candidate_dataset_fingerprint"),
        ],
    }
    identity_ok = all(value == identities["output_manifest"] for value in identities.values())
    add(
        "ALIGN_V02_DATASET_IDENTITY_001",
        "dataset_identity",
        "Bundle, registry, sidecar and equivalence record identify the exact physical candidate.",
        identities,
        "PASS" if identity_ok else "BLOCK",
        [OUTPUT_MANIFEST, BUNDLE, REGISTRY_ENTRY, SIDECAR, EQUIVALENCE],
    )

    hashes = artifact_hashes(bundle)
    output_files = {
        item.get("logical_role", item.get("path", "")): item.get("sha256")
        for item in output_manifest.get("files", [])
        if isinstance(item, dict)
    }
    expected_hashes = {
        "candidate_output_manifest": sha256_file(OUTPUT_MANIFEST),
        "candidate_parquet": sidecar.get("candidate_parquet_sha256"),
        "physical_schema_contract": sha256_file(PHYSICAL_SCHEMA),
        "lineage_manifest": sha256_file(LINEAGE_MANIFEST),
        "market_state_validation_report": sha256_file(VALIDATION_REPORT),
        "market_state_temporal_legality_report": sha256_file(TEMPORAL_REPORT),
        "original_request_record": sha256_file(ORIGINAL_REQUEST),
        "original_execution_plan": sha256_file(ORIGINAL_PLAN),
        "exact_requested_context_ledger": sha256_file(LEDGER),
        "replay_availability_sidecar_contract": sha256_file(SIDECAR_CONTRACT),
        "replay_availability_sidecar": sha256_file(SIDECAR),
        "exact_reuse_equivalence_record": sha256_file(EQUIVALENCE),
    }
    hash_mismatches = {
        key: {"bundle": hashes.get(key), "expected": value}
        for key, value in expected_hashes.items()
        if hashes.get(key) != value
    }
    declared_parquet_hashes = {
        item.get("sha256")
        for item in output_manifest.get("files", [])
        if isinstance(item, dict) and str(item.get("path", "")).endswith(".parquet")
    }
    parquet_chain_ok = expected_hashes["candidate_parquet"] in declared_parquet_hashes
    add(
        "ALIGN_V02_ARTIFACT_HASH_CHAIN_001",
        "artifact_hash_chain",
        "Bundle freezes every governed metadata artifact and the previously validated parquet hash.",
        {
            "hash_mismatches": hash_mismatches,
            "parquet_hash_declared_by_output_manifest": parquet_chain_ok,
            "parquet_opened": False,
        },
        "PASS" if not hash_mismatches and parquet_chain_ok else "BLOCK",
        [BUNDLE, OUTPUT_MANIFEST, SIDECAR],
    )

    final_coverage = (
        final_manifest.get("requested_contexts"),
        final_manifest.get("represented_contexts"),
        final_manifest.get("unavailable_contexts"),
        0,
        0,
        0,
    )
    coverage = {
        "bundle": coverage_tuple(bundle),
        "response": coverage_tuple(response),
        "final_manifest": final_coverage,
        "ledger_requested": ledger.get("requested_contexts"),
        "ledger_represented": ledger.get("represented_contexts"),
        "sidecar_rows": len(sidecar.get("records", [])),
    }
    coverage_ok = (
        coverage["bundle"] == final_coverage
        and coverage["response"] == final_coverage
        and coverage["ledger_requested"] == final_coverage[0]
        and coverage["ledger_represented"] == final_coverage[1]
        and coverage["sidecar_rows"] == final_coverage[1]
    )
    add(
        "ALIGN_V02_COVERAGE_001",
        "coverage",
        "Requested, represented and unavailable contexts reconcile without hiding partial coverage.",
        coverage,
        "PASS_WITH_RESTRICTIONS" if coverage_ok else "BLOCK",
        [BUNDLE, RESPONSE, FINAL_MANIFEST, LEDGER, SIDECAR],
    )

    ledger_hash = sha256_file(LEDGER)
    sidecar_hash = sha256_file(SIDECAR)
    equivalence_checks = {
        "ledger_sha": equivalence.get("requested_context_ledger_sha256") == ledger_hash,
        "sidecar_sha": equivalence.get("sidecar_sha256") == sidecar_hash,
        "original_request_sha": equivalence.get("original_request_record_sha256")
        == sha256_file(ORIGINAL_REQUEST),
        "original_plan_sha": equivalence.get("original_execution_plan_sha256")
        == sha256_file(ORIGINAL_PLAN),
        "original_request_fingerprint": equivalence.get("original_request_fingerprint")
        == ledger.get("request_fingerprint"),
        "reissued_request_bound_by_bundle": request.get("request_fingerprint")
        == bundle.get("request_response_bindings", [{}])[0].get("request_fingerprint"),
        "candidate_dataset": equivalence.get("candidate_dataset_id") == output_dataset_id,
        "candidate_fingerprint": equivalence.get("candidate_dataset_fingerprint")
        == output_fingerprint,
    }
    add(
        "ALIGN_V02_EXACT_REUSE_001",
        "exact_reuse",
        "The reissued request is explicitly bound to the original plan, 120-context ledger and 104-row sidecar.",
        equivalence_checks,
        "PASS" if all(equivalence_checks.values()) else "BLOCK",
        [EQUIVALENCE, ORIGINAL_REQUEST, ORIGINAL_PLAN, LEDGER, SIDECAR, REQUEST],
    )

    row_ids = {
        record.get("materialized_state_candidate_id")
        for record in sidecar.get("records", [])
    }
    ledger_rows = {
        item.get("materialized_state_candidate_id")
        for item in ledger.get("contexts", [])
        if item.get("disposition") == "represented"
    }
    row_identity_ok = (
        None not in row_ids
        and len(row_ids) == 104
        and row_ids == ledger_rows
    )
    add(
        "ALIGN_V02_ROW_ADDRESSABILITY_001",
        "row_addressability",
        "Exactly the 104 represented ledger contexts map one-to-one to sidecar row identities.",
        {
            "sidecar_unique_rows": len(row_ids),
            "ledger_represented_rows": len(ledger_rows),
            "symmetric_difference": len(row_ids.symmetric_difference(ledger_rows)),
        },
        "PASS" if row_identity_ok else "BLOCK",
        [LEDGER, SIDECAR],
    )

    timestamp_validator = contract_validator(TIMESTAMP_CONTRACT)
    timestamp_failures: list[dict[str, Any]] = []
    for record in sidecar.get("records", []):
        payload = module.timestamp_payload(record)
        errors = schema_errors(timestamp_validator, payload)
        if errors:
            timestamp_failures.append(
                {
                    "materialized_state_candidate_id": record.get(
                        "materialized_state_candidate_id"
                    ),
                    "errors": errors,
                }
            )
    add(
        "ALIGN_V02_TEMPORAL_LEGALITY_001",
        "temporal_legality",
        "All 104 replay records satisfy the hardened timestamp contract.",
        {"validated_records": len(sidecar.get("records", [])), "failures": timestamp_failures},
        "PASS" if not timestamp_failures and len(sidecar.get("records", [])) == 104 else "BLOCK",
        [TIMESTAMP_CONTRACT, SIDECAR, TEMPORAL_REPORT],
    )

    sidecar_record_restrictions = {
        tuple(sorted(record.get("restriction_codes", [])))
        for record in sidecar.get("records", [])
    }
    restrictions = {
        "bundle": sorted(bundle.get("restrictions", [])),
        "response": sorted(response.get("restrictions", [])),
        "sidecar_record_sets": [list(values) for values in sorted(sidecar_record_restrictions)],
        "dataset_validation_status": bundle_dataset.get("validation_status"),
        "dataset_reuse_eligibility": bundle_dataset.get("reuse_eligibility"),
    }
    effective_restrictions = set(bundle.get("restrictions", []))
    restriction_ok = (
        effective_restrictions == set(response.get("restrictions", []))
        and sidecar_record_restrictions == {tuple(sorted(effective_restrictions))}
        and bundle_dataset.get("validation_status") == "PASS_WITH_RESTRICTIONS"
        and bundle_dataset.get("reuse_eligibility") == "eligible_with_restrictions"
    )
    add(
        "ALIGN_V02_RESTRICTIONS_001",
        "restrictions",
        "Bundle, response, dataset and every sidecar row preserve effective restrictions.",
        restrictions,
        "PASS_WITH_RESTRICTIONS" if restriction_ok else "BLOCK",
        [BUNDLE, RESPONSE, SIDECAR],
    )

    def cross_artifact_errors(candidate_bundle: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        candidate_dataset = dataset_ref(candidate_bundle)
        if (
            candidate_dataset.get("dataset_id") != output_dataset_id
            or candidate_dataset.get("candidate_dataset_fingerprint") != output_fingerprint
        ):
            errors.append("bundle dataset identity does not match candidate output manifest")
        candidate_hashes = artifact_hashes(candidate_bundle)
        for artifact_id, expected_sha in expected_hashes.items():
            if candidate_hashes.get(artifact_id) != expected_sha:
                errors.append(f"artifact hash mismatch: {artifact_id}")
        if coverage_tuple(candidate_bundle) != final_coverage:
            errors.append("bundle coverage does not match final manifest")
        return errors

    base_cross_errors = cross_artifact_errors(bundle)
    add(
        "ALIGN_V02_CROSS_ARTIFACT_VALIDATOR_001",
        "cross_artifact",
        "The alignment-specific validator accepts the unmodified governed bundle.",
        base_cross_errors,
        "PASS" if not base_cross_errors else "BLOCK",
        [BUNDLE, OUTPUT_MANIFEST, FINAL_MANIFEST, SIDECAR],
    )

    negative_cases: list[tuple[str, str, Callable[[], bool]]] = []

    def bundle_mutation(mutator: Callable[[dict[str, Any]], None]) -> bool:
        mutated = copy.deepcopy(bundle)
        mutator(mutated)
        return bool(
            module.provider_semantic_errors(mutated, "state_bundle_manifest")
            or cross_artifact_errors(mutated)
        )

    negative_cases.extend(
        [
            (
                "ALIGN_V02_NEG_WRONG_DATASET",
                "A bundle with a different dataset identity is blocked.",
                lambda: bundle_mutation(
                    lambda value: value["dataset_refs"]["market_state_dataset_ref"].__setitem__(
                        "dataset_id", "wrong_dataset"
                    )
                ),
            ),
            (
                "ALIGN_V02_NEG_MISSING_SIDECAR_HASH",
                "A bundle missing the sidecar artifact hash is blocked.",
                lambda: bundle_mutation(
                    lambda value: value.__setitem__(
                        "artifact_hashes",
                        [
                            item
                            for item in value["artifact_hashes"]
                            if item.get("artifact_id") != "replay_availability_sidecar"
                        ],
                    )
                ),
            ),
            (
                "ALIGN_V02_NEG_WEAKENED_COVERAGE",
                "A bundle that hides unavailable contexts is blocked.",
                lambda: bundle_mutation(
                    lambda value: value["coverage"].__setitem__("unavailable_contexts", 0)
                ),
            ),
        ]
    )
    for case_id, expected, check in negative_cases:
        blocked = check()
        add(
            case_id,
            "adversarial",
            expected,
            {"blocked": blocked},
            "PASS" if blocked else "BLOCK",
            [BUNDLE, BUNDLE_CONTRACT, SOURCE_RUNNER],
        )

    add(
        "ALIGN_V02_BOUNDARIES_001",
        "hard_boundaries",
        "No parquet bytes, rows, replay events, strategy callbacks or backtest actions are performed.",
        {
            "parquet_opened": False,
            "parquet_hash_recomputed": False,
            "physical_state_rows_read": 0,
            "StateReplayFeed_records_emitted": 0,
            "EventLoop_ticks": 0,
            "orders_emitted": 0,
            "fills_emitted": 0,
        },
        "PASS",
        [],
    )

    blocking = [row for row in rows if row["result"] == "BLOCK"]
    restricted = [row for row in rows if row["result"] == "PASS_WITH_RESTRICTIONS"]
    case_ids = [row["case_id"] for row in rows]
    missing_required_case_ids = sorted(set(REQUIRED_CASE_IDS) - set(case_ids))
    unexpected_case_ids = sorted(set(case_ids) - set(REQUIRED_CASE_IDS))
    duplicate_case_ids = sorted(
        {case_id for case_id in case_ids if case_ids.count(case_id) > 1}
    )
    if missing_required_case_ids or unexpected_case_ids or duplicate_case_ids:
        blocking.append({"case_id": "ALIGN_V02_CASE_ID_GUARD", "result": "BLOCK"})
    return {
        "gate": GATE,
        "created_at_utc": now,
        "status": STATUS if not blocking else "CLOSED_BLOCKED_PHYSICAL_EVIDENCE_ALIGNMENT_V0_2",
        "case_count": len(rows),
        "required_case_ids": REQUIRED_CASE_IDS,
        "missing_required_case_ids": missing_required_case_ids,
        "unexpected_case_ids": unexpected_case_ids,
        "duplicate_case_ids": duplicate_case_ids,
        "blocking_findings": len(blocking),
        "restricted_findings": len(restricted),
        "physical_read_authorization_ready": not blocking,
        "authorization_to_read_issued": False,
        "parquet_opened": False,
        "parquet_hash_recomputed": False,
        "physical_state_rows_read": 0,
        "StateReplayFeed_records_emitted": 0,
        "EventLoop_ticks": 0,
        "strategy_callbacks": 0,
        "orders_emitted": 0,
        "fills_emitted": 0,
        "PnL_calculated": False,
        "runtime_requests_executed": 0,
        "runtime_builds_executed": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "backtest_consumption": False,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "next_gate": (
            "bounded_state_bundle_read_and_replay_authorization_v0_1"
            if not blocking
            else "alignment_correction_required"
        ),
        "rows": rows,
    }


def render_authorization(now: str) -> str:
    return f"""# StateBundle Manifest Physical Evidence Alignment Authorization v0.2

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `AUTHORIZED_READ_ONLY_METADATA_NO_PHYSICAL_READ`

## Purpose

Align the accepted provider v0.1.2 request, response and `StateBundleManifest`
with the exact Market State scale-validation candidate, its 120-context ledger,
104-row replay-availability sidecar and governed metadata hash chain.

This gate may read JSON, Markdown and Python validation logic. It identifies the
candidate parquet and consumes its previously governed SHA-256, but it must not
open or hash the parquet, read state rows, emit replay records or execute a
backtest.

## Hard Boundaries

```text
parquet_opened = false
parquet_hash_recomputed = false
physical_state_rows_read = 0
StateReplayFeed_records_emitted = 0
EventLoop_ticks = 0
strategy_callbacks = 0
orders_emitted = 0
fills_emitted = 0
PnL_calculated = false
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
backtest_consumption = false
official_dataset = false
production = false
downstream = false
```
"""


def render_readout(now: str, matrix: dict[str, Any]) -> str:
    return f"""# StateBundle Manifest Physical Evidence Alignment Readout v0.2

Gate: `{GATE}`
Date: `{now[:10]}`
Status: `{matrix['status']}`

## Result

```text
case_count = {matrix['case_count']}
blocking_findings = {matrix['blocking_findings']}
restricted_findings = {matrix['restricted_findings']}
physical_read_authorization_ready = {str(matrix['physical_read_authorization_ready']).lower()}
authorization_to_read_issued = false
```

The accepted provider v0.1.2 control-plane artifacts now align with one exact
Market State scale-validation candidate, its 120 requested contexts, 104
represented row identities, 16 unavailable contexts, replay-availability
sidecar and governed metadata hash chain.

This closure proves metadata alignment only. It does not open the candidate
parquet, deliver rows or authorize `StateReplayFeed` or backtest consumption.

## Preserved Restrictions

```text
candidate dataset only
partial coverage remains visible
official_dataset = false
production = false
downstream = false
backtest_consumption = false
```

## Next Gate

```text
{matrix['next_gate']}
```
"""


def main() -> int:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    scope = build_scope(now)
    matrix = build_matrix(now)
    write_text(OUTPUTS["authorization"], render_authorization(now))
    write_json(OUTPUTS["scope"], scope)
    write_json(OUTPUTS["matrix"], matrix)
    write_text(OUTPUTS["readout"], render_readout(now, matrix))
    print(
        json.dumps(
            {
                "gate": GATE,
                "status": matrix["status"],
                "case_count": matrix["case_count"],
                "blocking_findings": matrix["blocking_findings"],
                "restricted_findings": matrix["restricted_findings"],
                "physical_read_authorization_ready": matrix[
                    "physical_read_authorization_ready"
                ],
                "next_gate": matrix["next_gate"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if matrix["blocking_findings"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
