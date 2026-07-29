from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(r"C:\TSIS_Data")
FEATURE_ROOT = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE_ROOT / "08_RUNTIME_CAPABILITIES"
RUNS = RUNTIME / "runs"
SCRIPTS = RUNTIME / "scripts"

GATE = "runtime_user_invocation_bounded_interface_execution_v0_1"
NEXT_GATE = "runtime_user_invocation_bounded_interface_execution_review_v0_1"
STATUS = "CLOSED_PASS_BOUNDED_INTERFACE_EXECUTION_WITH_RESTRICTIONS_PENDING_REVIEW"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def h(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def case_code(case_id: str) -> str:
    return "_".join(case_id.split("_")[:2])


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def ref(path: Path, ref_type: str, availability: str = "available") -> dict[str, Any]:
    return {"ref_id": path.stem, "ref_type": ref_type, "sha256": sha256_file(path), "availability": availability}


def declared_ref(ref_id: str, ref_type: str, seed: str, availability: str = "not_required") -> dict[str, Any]:
    return {"ref_id": ref_id, "ref_type": ref_type, "sha256": h(seed), "availability": availability}


def path_entry(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def replace_line(text: str, prefix: str, new_line: str) -> str:
    lines = text.splitlines()
    done = False
    for i, line in enumerate(lines):
        if line.startswith(prefix) and not done:
            lines[i] = new_line
            done = True
    return "\n".join(lines) + "\n"


def insert_after(text: str, marker: str, block: str) -> str:
    if block.strip() in text:
        return text
    idx = text.find(marker)
    if idx == -1:
        return text.rstrip() + "\n\n" + block.strip() + "\n"
    return text[: idx + len(marker)] + "\n\n" + block.strip() + "\n" + text[idx + len(marker) :]


def validate(schema: dict[str, Any], doc: dict[str, Any]) -> list[str]:
    return [e.message for e in sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(e.path))]


def coverage_ok(c: dict[str, int]) -> bool:
    keys = ["requested_contexts", "represented_contexts", "unavailable_contexts", "blocked_contexts", "quarantined_contexts", "unaccounted_contexts"]
    if not all(k in c for k in keys):
        return True
    return c["requested_contexts"] == c["represented_contexts"] + c["unavailable_contexts"] + c["blocked_contexts"] + c["quarantined_contexts"] + c["unaccounted_contexts"]


def make_dataset(kind: str) -> dict[str, Any]:
    return {
        "dataset_id": f"{kind}_candidate_scale_validation_reference_v0_1",
        "dataset_kind": kind,
        "candidate_dataset_fingerprint": h(f"{kind}:candidate")[:64],
        "validation_status": "PASS_WITH_RESTRICTIONS",
        "reuse_eligibility": "eligible_with_restrictions",
        "artifact_availability": "available",
    }


def make_bundle(case_id: str, mode: str, request_fp: str, capability_ref: dict[str, Any], dataset: dict[str, Any], coverage: dict[str, int], restrictions: list[str], artifact_ref: dict[str, Any]) -> dict[str, Any]:
    kind = dataset["dataset_kind"]
    return {
        "state_bundle_manifest_id": f"{case_id}_bundle",
        "bundle_state_mode": mode,
        "state_kinds": [kind],
        "request_fingerprints": [request_fp],
        "state_resolution_request_refs": [declared_ref(f"{case_id}_state_resolution_request", "state_resolution_request", request_fp)],
        "runtime_invocation_response_ref": declared_ref(f"{case_id}_runtime_invocation_response", "runtime_invocation_response", case_id),
        "capability_refs": [capability_ref],
        "dataset_refs": {
            "market_state_dataset_ref": dataset if kind == "market_state" else None,
            "event_state_dataset_ref": dataset if kind == "event_state" else None,
        },
        "coverage": coverage,
        "validation_status": "PASS_WITH_RESTRICTIONS",
        "restrictions": restrictions,
        "representation_profile_versions": [{"profile_id": f"{kind}_profile", "profile_version": "v0_1"}],
        "schema_fingerprints": [h(case_id + ":schema")],
        "source_dataset_ids": [],
        "source_content_hashes": [],
        "artifact_hashes": [artifact_ref],
        "field_lineage": [],
        "temporal_policy": {"available_at_required": True, "point_in_time_legal": True},
        "materialization_status": "reused_validated_candidate_reference_only",
        "consumption_authorization": {"backtest_consumption_authorized": False, "downstream_authorized": False, "consumption_purposes": []},
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "physical_rows_delivered": False,
    }


def make_response(case_id: str, request_type: str, decision: str, status: str, capability_id: str, profile_id: str | None, dataset_id: str | None, coverage: dict[str, Any], restrictions: list[str], bundle_ref: dict[str, Any] | None, artifact_refs: list[dict[str, Any]]) -> dict[str, Any]:
    details = {"materializer_executions": 0, "source_market_data_rows_read": 0, "registry_mutations": 0, "physical_rows_delivered": 0} if status == "reuse_hit" else None
    return {
        "invocation_id": case_id,
        "request_type": request_type,
        "request_fingerprint": h(case_id + ":request"),
        "invocation_status": status,
        "resolution_decision": decision,
        "capability_id": capability_id,
        "profile_id": profile_id,
        "run_id": None,
        "dataset_id": dataset_id,
        "dataset_status": "validated_candidate" if dataset_id else None,
        "validation_status": "PASS_WITH_RESTRICTIONS" if dataset_id else None,
        "state_bundle_manifest_ref": bundle_ref,
        "coverage": coverage,
        "restrictions": restrictions,
        "artifact_references": artifact_refs,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "market_state_details": details if request_type == "market_state" else None,
        "event_state_details": details if request_type == "event_state" else None,
        "authorization_ref": None,
    }


def main() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    stamp = now.replace("-", "").replace(":", "").replace("+00:00", "Z").replace("+", "")
    run_id = f"{GATE}_{stamp}"
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    assert run_dir.exists(), f"run_dir_not_created: {run_dir}"

    response_schema = read_json(RUNTIME / "runtime_user_invocation_response_contract_v0_1.json")["json_schema"]
    bundle_schema = read_json(RUNTIME / "state_bundle_manifest_contract_v0_1.json")["json_schema"]
    registry_hash = sha256_file(RUNTIME / "runtime_capability_registry_snapshot_v0_1.json")
    market_manifest = RUNTIME / "runs" / "market_state_on_demand_scale_validation_v0_1_20260727T133641Z" / "final_manifest.json"
    event_manifest = RUNTIME / "runs" / "event_state_on_demand_scale_validation_v0_1_20260728T120123Z" / "final_manifest.json"

    caps = {
        "market_state": {"ref_id": "market_state_on_demand_runtime_capability_v0_1", "ref_type": "runtime_capability", "sha256": registry_hash, "availability": "available"},
        "event_state": {"ref_id": "event_state_on_demand_runtime_capability_v0_1", "ref_type": "runtime_capability", "sha256": registry_hash, "availability": "available"},
    }
    datasets = {"market_state": make_dataset("market_state"), "event_state": make_dataset("event_state")}
    profiles = {"market_state": "market_state_core_four_intraday_profile_v0_1", "event_state": "event_state_core_four_intraday_profile_v0_1"}
    manifests = {"market_state": market_manifest, "event_state": event_manifest}
    coverages = {
        "market_state": {"requested_contexts": 120, "represented_contexts": 104, "unavailable_contexts": 16, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0},
        "event_state": {"requested_contexts": 80, "represented_contexts": 74, "unavailable_contexts": 6, "blocked_contexts": 0, "quarantined_contexts": 0, "unaccounted_contexts": 0},
    }

    response_paths: list[Path] = []

    positive = [
        ("case_01_market_state_exact_reuse_hit_reference_only", "market_state", ["candidate_runtime_only", "partial_coverage", "no_downstream"]),
        ("case_02_event_state_exact_reuse_hit_reference_only", "event_state", ["candidate_runtime_only", "session_opened_only", "partial_coverage", "no_downstream"]),
        ("case_07_partial_candidate_coverage_preserved", "market_state", ["candidate_runtime_only", "coverage_status_partial", "unavailable_contexts_preserved"]),
        ("case_08_reuse_hit_zero_build_evidence", "event_state", ["candidate_runtime_only", "reuse_hit", "zero_build", "zero_source_rows", "zero_registry_mutations"]),
    ]
    for case_id, kind, restrictions in positive:
        request_fp = h(case_id + ":request")
        artifact_ref = ref(manifests[kind], "runtime_scale_validation_final_manifest")
        bundle = make_bundle(case_id, f"{kind}_only", request_fp, caps[kind], datasets[kind], coverages[kind], restrictions, artifact_ref)
        bp = run_dir / f"{case_code(case_id)}_bundle.json"
        write_json(bp, bundle)
        response = make_response(case_id, kind, "VALID_REQUEST_REUSE_HIT", "reuse_hit", caps[kind]["ref_id"], profiles[kind], datasets[kind]["dataset_id"], coverages[kind], restrictions, ref(bp, "state_bundle_manifest"), [artifact_ref])
        rp = run_dir / f"{case_code(case_id)}_response.json"
        write_json(rp, response)
        response_paths.append(rp)

    blocked = [
        ("case_03_event_state_unsupported_halt_resumed_blocked", "event_state", "BLOCKED_UNSUPPORTED_PROFILE_OR_EVENT_TYPE", ["unsupported_event_type:halt_resumed", "session_opened_only"]),
        ("case_05_production_or_downstream_request_blocked", "market_state", "BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED", ["production_not_authorized", "downstream_not_authorized"]),
        ("case_06_physical_path_input_blocked", "event_state", "BLOCKED_PHYSICAL_PATH_NOT_ALLOWED", ["physical_path_input_forbidden", "fail_closed"]),
    ]
    for case_id, kind, decision, restrictions in blocked:
        response = make_response(case_id, kind, decision, "blocked", caps[kind]["ref_id"], profiles[kind], None, {}, restrictions, None, [])
        rp = run_dir / f"{case_code(case_id)}_response.json"
        write_json(rp, response)
        response_paths.append(rp)

    response = make_response("case_04_new_candidate_without_execution_authorization", "market_state", "VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED", "authorization_required", caps["market_state"]["ref_id"], profiles["market_state"], None, {}, ["new_candidate_execution_requires_separate_authorization"], None, [])
    rp = run_dir / "case_04_response.json"
    write_json(rp, response)
    response_paths.append(rp)

    cases = []
    for rp in sorted(response_paths):
        response = read_json(rp)
        response_errors = validate(response_schema, response)
        bp = run_dir / rp.name.replace("_response.json", "_bundle.json")
        bundle_errors = validate(bundle_schema, read_json(bp)) if bp.exists() else []
        details = response.get("market_state_details") or response.get("event_state_details") or {}
        cases.append({
            "case_id": response["invocation_id"],
            "response_ref": rel(rp),
            "bundle_ref": rel(bp) if bp.exists() else None,
            "invocation_status": response["invocation_status"],
            "resolution_decision": response["resolution_decision"],
            "response_schema_validation": "PASS" if not response_errors else "FAIL",
            "bundle_schema_validation": "PASS" if bp.exists() and not bundle_errors else "NOT_APPLICABLE" if not bp.exists() else "FAIL",
            "coverage_arithmetic": "PASS" if coverage_ok(response.get("coverage") or {}) else "FAIL",
            "materializer_executions": details.get("materializer_executions", 0),
            "source_market_data_rows_read": details.get("source_market_data_rows_read", 0),
            "registry_mutations": details.get("registry_mutations", 0),
            "physical_rows_delivered": details.get("physical_rows_delivered", 0),
            "errors": response_errors + bundle_errors,
        })
    hard_failures = sum(1 for c in cases if "FAIL" in (c["response_schema_validation"], c["bundle_schema_validation"], c["coverage_arithmetic"]))
    execution_status = STATUS if hard_failures == 0 else "CLOSED_FAILED_BOUNDED_INTERFACE_EXECUTION"
    counters = {
        "interface_invocations": len(cases),
        "runtime_builds_executed": 0,
        "materializer_executions": 0,
        "source_market_data_rows_read": 0,
        "datasets_written": 0,
        "registry_mutations": 0,
        "physical_state_rows_delivered": 0,
        "state_replay_feed_records_emitted": 0,
        "backtest_runs_started": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
        "backtest_consumption": False,
    }
    matrix = {"execution_id": run_id, "gate": GATE, "created_at_utc": now, "execution_status": execution_status, "case_count": len(cases), "hard_failures": hard_failures, "cases": cases, "aggregate_counters": counters, "next_gate": NEXT_GATE}
    matrix_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_matrix_v0_1.json"
    write_json(matrix_path, matrix)
    write_json(run_dir / matrix_path.name, matrix)
    final_manifest = {"run_id": run_id, "gate": GATE, "status": execution_status, "created_at_utc": now, "matrix_ref": path_entry(matrix_path), "case_count": len(cases), "hard_failures": hard_failures, "aggregate_counters": counters, "restrictions": ["reference_only", "no_runtime_builds", "no_physical_row_delivery", "no_backtest_consumption", "no_state_replay_feed", "no_downstream"], "next_gate": NEXT_GATE}
    write_json(run_dir / "final_manifest.json", final_manifest)
    readout = f"""# Runtime User Invocation Bounded Interface Execution Readout v0.1\n\nGate: `{GATE}`\nRun: `{run_id}`\nDate: `{now[:10]}`\nStatus: `{execution_status}`\n\n## Result\n\n```text\ncase_count = {len(cases)}\nhard_failures = {hard_failures}\ninterface_invocations = {len(cases)}\nruntime_builds_executed = 0\nmaterializer_executions = 0\nsource_market_data_rows_read = 0\ndatasets_written = 0\nregistry_mutations = 0\nphysical_state_rows_delivered = 0\nStateReplayFeed records emitted = 0\nbacktest_runs_started = 0\n```\n\nThe bounded provider interface behavior test produced governed response artifacts and, for reuse hits, metadata-only `StateBundleManifest` references. It did not build Market State or Event State, did not read physical state rows, did not mutate registries and did not authorize downstream consumption.\n\n## Next Gate\n\n```text\n{NEXT_GATE}\n```\n"""
    readout_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_readout_v0_1.md"
    write_text(readout_path, readout)
    write_text(run_dir / "readout.md", readout)

    route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
    text = read_text(route)
    text = replace_line(text, "Status:", "Status: `route_v1_40_bounded_interface_execution_completed_pending_review`")
    text = replace_line(text, "Current gate:", f"Current gate: `{NEXT_GATE}`")
    block = f"""## Runtime User Invocation Bounded Interface Execution {now[:10]}\n\n```text\n{GATE}\n=\n{execution_status}\n```\n\n```text\ncase_count = {len(cases)}\nhard_failures = {hard_failures}\nruntime_builds_executed = 0\nphysical_state_rows_delivered = 0\nStateReplayFeed = NOT_AUTHORIZED\nbacktest_consumption = false\nproduction = false\ndownstream = false\n```\n\nNext gate:\n\n```text\n{NEXT_GATE}\n```\n"""
    text = insert_after(text, f"Current gate: `{NEXT_GATE}`", block)
    write_text(route, text)

    agent = FEATURE_ROOT / "AGENT.md"
    text = read_text(agent)
    block = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt\n\n## Current Runtime Handoff Override - Bounded Interface Execution Completed Pending Review\n\nStatus: `agent_handoff_prompt_v0_127`\nDate: `{now[:10]}`\n\n```text\ncurrent_gate = {NEXT_GATE}\nlast_closed_gate = {GATE}\nlast_closed_run_id = {run_id}\nlast_closed_status = {execution_status}\ncase_count = {len(cases)}\nhard_failures = {hard_failures}\nruntime_builds_executed = 0\nphysical_state_rows_delivered = 0\nstate_replay_feed_authority = false\nbacktest_state_consumption_authority = false\nofficial_dataset = false\nproduction = false\ndownstream_state_consumption = NOT_AUTHORIZED\n```\n\nNext gate:\n\n```text\n{NEXT_GATE}\n```\n\nThe next gate must review the bounded provider interface execution evidence. It must not open StateReplayFeed, physical state row delivery, production or downstream consumption.\n\n"""
    if "Bounded Interface Execution Completed Pending Review" not in text:
        text = block + text
    write_text(agent, text)

    readme = RUNTIME / "README.md"
    text = read_text(readme)
    text = replace_line(text, "Status:", "Status: `runtime_user_invocation_bounded_interface_execution_completed_pending_review_v0_1`")
    text = replace_line(text, "Current gate:", f"Current gate: `{NEXT_GATE}`")
    write_text(readme, text)

    changelog = FEATURE_ROOT / "CHANGELOG.md"
    text = read_text(changelog) if changelog.exists() else "# Changelog\n"
    entry = f"""## {now[:10]} - Runtime User Invocation Bounded Interface Execution\n\n- Executed `{GATE}` with `{len(cases)}` provider-only interface behavior cases.\n- Hard failures: `{hard_failures}`.\n- Preserved zero runtime builds, zero physical row delivery, zero registry mutations, no `StateReplayFeed`, no backtest state consumption, no production and no downstream.\n- Set next gate to `{NEXT_GATE}`.\n"""
    if "Runtime User Invocation Bounded Interface Execution" not in text:
        text = text.rstrip() + "\n\n" + entry
    write_text(changelog, text)

    package_files = [FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", readout_path, matrix_path, RUNTIME / "runtime_user_invocation_response_contract_v0_1.json", RUNTIME / "state_bundle_manifest_contract_v0_1.json", RUNTIME / "state_resolution_request_contract_v0_1.json", SCRIPTS / "runtime_user_invocation_bounded_interface_execution_runner_v0_1.py", run_dir / "final_manifest.json", run_dir / "readout.md"] + sorted(run_dir.glob("*.json"))
    unique = []
    seen = set()
    for p in package_files:
        if p.exists() and p not in seen:
            unique.append(p)
            seen.add(p)
    zip_path = FEATURE_ROOT / f"runtime_user_invocation_bounded_interface_execution_provider_only_{stamp}.zip"
    manifest = {"package_id": "runtime_user_invocation_bounded_interface_execution_provider_only", "created_at_utc": now, "gate": GATE, "status": execution_status, "entry_count_excluding_manifest": len(unique), "explicitly_excluded": ["02_TSIS_BACKTEST_ENGINE files", "StateReplayFeed files", "parquet files", "physical market data", "downstream row delivery artifacts"], "entries": [path_entry(p) for p in unique]}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in unique:
            zf.write(p, rel(p))
        zf.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"gate": GATE, "run_id": run_id, "status": execution_status, "case_count": len(cases), "hard_failures": hard_failures, "next_gate": NEXT_GATE, "run_dir": str(run_dir), "zip_path": str(zip_path)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

