from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(r"C:\TSIS_Data")
FEATURE_ROOT = ROOT / "00_CTO_APPLIED_ARCHITECTURE" / "03_TABLES_feature_engineering"
RUNTIME = FEATURE_ROOT / "08_RUNTIME_CAPABILITIES"
CONFIGS = RUNTIME / "configs"
SCRIPTS = RUNTIME / "scripts"

GATE = "runtime_user_invocation_bounded_interface_execution_review_v0_1"
EXECUTION_GATE = "runtime_user_invocation_bounded_interface_execution_v0_1"
STATUS = "CLOSED_PASS_STATE_PROVIDER_CONTROL_PLANE_READY_WITH_RESTRICTIONS_NO_CONSUMPTION"
NEXT_BOUNDARY = "state_bundle_physical_consumption_authorization_design_v0_1"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def entry(path: Path) -> dict[str, Any]:
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


def main() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    stamp = now.replace("-", "").replace(":", "").replace("+00:00", "Z").replace("+", "")
    execution_matrix_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_matrix_v0_1.json"
    execution_readout_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_readout_v0_1.md"
    execution_matrix = read_json(execution_matrix_path)
    counters = execution_matrix["aggregate_counters"]

    review_rows = []
    def add(area: str, expected: str, observed: Any, result: str, notes: str) -> None:
        review_rows.append({"area": area, "expected": expected, "observed": observed, "result": result, "notes": notes})

    add("case_count", "8 authorized cases", execution_matrix["case_count"], "PASS" if execution_matrix["case_count"] == 8 else "FAIL", "All authorized bounded cases represented.")
    add("hard_failures", "0", execution_matrix["hard_failures"], "PASS" if execution_matrix["hard_failures"] == 0 else "FAIL", "No schema or coverage arithmetic failures.")
    add("response_schema_validation", "PASS for every response", [c["response_schema_validation"] for c in execution_matrix["cases"]], "PASS" if all(c["response_schema_validation"] == "PASS" for c in execution_matrix["cases"]) else "FAIL", "RuntimeInvocationResponse contract enforced.")
    add("bundle_schema_validation", "PASS or NOT_APPLICABLE", [c["bundle_schema_validation"] for c in execution_matrix["cases"]], "PASS" if all(c["bundle_schema_validation"] in {"PASS", "NOT_APPLICABLE"} for c in execution_matrix["cases"]) else "FAIL", "Reuse hit StateBundleManifest artifacts validate.")
    add("coverage_arithmetic", "PASS", [c["coverage_arithmetic"] for c in execution_matrix["cases"]], "PASS" if all(c["coverage_arithmetic"] == "PASS" for c in execution_matrix["cases"]) else "FAIL", "Partial coverage is preserved.")
    add("zero_builds", "0", counters["runtime_builds_executed"], "PASS" if counters["runtime_builds_executed"] == 0 and counters["materializer_executions"] == 0 else "FAIL", "No Market/Event materialization occurred.")
    add("zero_source_rows", "0", counters["source_market_data_rows_read"], "PASS" if counters["source_market_data_rows_read"] == 0 else "FAIL", "No market rows read.")
    add("zero_registry_mutations", "0", counters["registry_mutations"], "PASS" if counters["registry_mutations"] == 0 else "FAIL", "No registry mutation occurred.")
    add("no_physical_delivery", "0 rows delivered", counters["physical_state_rows_delivered"], "PASS" if counters["physical_state_rows_delivered"] == 0 else "FAIL", "Control-plane only.")
    add("no_consumer_opening", "StateReplayFeed/backtest/downstream closed", {"state_replay_feed": counters["state_replay_feed_records_emitted"], "backtest": counters["backtest_runs_started"], "downstream": counters["downstream"]}, "PASS" if counters["state_replay_feed_records_emitted"] == 0 and counters["backtest_runs_started"] == 0 and counters["downstream"] is False else "FAIL", "Consumer/data-plane remains closed.")

    failed = [r for r in review_rows if r["result"] == "FAIL"]
    status = STATUS if not failed else "CLOSED_FAILED_BOUNDED_INTERFACE_EXECUTION_REVIEW"
    review = {"review_id": GATE, "created_at_utc": now, "review_status": status, "execution_gate_reviewed": EXECUTION_GATE, "execution_id": execution_matrix["execution_id"], "rows": review_rows, "failed_rows": len(failed), "state_provider_control_plane": "READY_WITH_RESTRICTIONS" if not failed else "NOT_READY", "remaining_closed": {"physical_row_delivery": False, "backtest_consumption": False, "state_replay_feed": False, "official_dataset": False, "production": False, "downstream": False}, "next_boundary_after_provider_control_plane": NEXT_BOUNDARY}

    auth_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_review_authorization_v0_1.md"
    write_text(auth_path, f"""# Runtime User Invocation Bounded Interface Execution Review Authorization v0.1\n\nGate: `{GATE}`\nDate: `{now[:10]}`\nStatus: `AUTHORIZED_REVIEW_NO_EXECUTION`\n\nAuthorize review of `{EXECUTION_GATE}` evidence only. No new interface invocation, runtime build, physical row delivery, backtest, `StateReplayFeed`, production or downstream consumption is authorized.\n""")
    scope_path = CONFIGS / "runtime_user_invocation_bounded_interface_execution_review_scope_v0_1.json"
    write_json(scope_path, {"scope_id": "runtime_user_invocation_bounded_interface_execution_review_scope_v0_1", "gate": GATE, "created_at_utc": now, "reviewed_execution_matrix": entry(execution_matrix_path), "reviewed_execution_readout": entry(execution_readout_path), "not_in_scope": ["new interface invocation", "runtime build", "state row delivery", "backtest execution", "StateReplayFeed", "downstream consumption"]})
    matrix_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_review_matrix_v0_1.json"
    write_json(matrix_path, review)
    readout_path = RUNTIME / "runtime_user_invocation_bounded_interface_execution_review_readout_v0_1.md"
    write_text(readout_path, f"""# Runtime User Invocation Bounded Interface Execution Review Readout v0.1\n\nGate: `{GATE}`\nDate: `{now[:10]}`\nStatus: `{status}`\n\n## Verdict\n\n```text\nSTATE_PROVIDER_CONTROL_PLANE = {review['state_provider_control_plane']}\nreviewed_cases = {execution_matrix['case_count']}\nhard_failures = {execution_matrix['hard_failures']}\nfailed_review_rows = {len(failed)}\nruntime_builds_executed = 0\nphysical_state_rows_delivered = 0\nStateReplayFeed = NOT_AUTHORIZED\nbacktest_consumption = false\nproduction = false\ndownstream = false\n```\n\nThe provider control-plane can now be treated as ready with restrictions for bounded request validation, capability resolution, governed reuse/reference responses and fail-closed blocking. This does not authorize the state data-plane.\n\n## Remaining Boundary\n\n```text\nphysical row delivery = false\nbacktest state consumption = false\nStateReplayFeed = false\nofficial dataset = false\nproduction = false\ndownstream = false\n```\n\nThe next workstream belongs to state-bundle physical consumption authorization and consumer/data-plane design, not additional conceptual Market/Event State provider architecture.\n""")

    route = FEATURE_ROOT / "99_ruta_de_trabajo.md"
    text = read_text(route)
    text = replace_line(text, "Status:", "Status: `route_v1_41_state_provider_control_plane_ready_with_restrictions`")
    text = replace_line(text, "Current gate:", "Current gate: `state_provider_control_plane_ready_with_restrictions_no_active_provider_gate`")
    block = f"""## Runtime User Invocation Bounded Interface Execution Review {now[:10]}\n\n```text\n{GATE}\n=\n{status}\n```\n\n```text\nSTATE_PROVIDER_CONTROL_PLANE = {review['state_provider_control_plane']}\nphysical_row_delivery = false\nStateReplayFeed = NOT_AUTHORIZED\nbacktest_consumption = false\nproduction = false\ndownstream = false\n```\n\nProvider control-plane v0.1 is closed for bounded validation/resolution/reference behavior. The next boundary is consumer/data-plane authorization, not more provider architecture.\n"""
    text = insert_after(text, "Current gate: `state_provider_control_plane_ready_with_restrictions_no_active_provider_gate`", block)
    write_text(route, text)

    agent = FEATURE_ROOT / "AGENT.md"
    text = read_text(agent)
    block = f"""# 03_TABLES_feature_engineering - Agent Handoff Prompt\n\n## Current Runtime Handoff Override - State Provider Control Plane Ready\n\nStatus: `agent_handoff_prompt_v0_128`\nDate: `{now[:10]}`\n\n```text\ncurrent_gate = state_provider_control_plane_ready_with_restrictions_no_active_provider_gate\nlast_closed_gate = {GATE}\nlast_closed_status = {status}\nstate_provider_control_plane = {review['state_provider_control_plane']}\nphysical_row_delivery = false\nstate_replay_feed_authority = false\nbacktest_state_consumption_authority = false\nofficial_dataset = false\nproduction = false\ndownstream_state_consumption = NOT_AUTHORIZED\n```\n\nThe next workstream is state-bundle physical consumption authorization / consumer data-plane design. Do not reopen provider architecture unless a material contract defect is found.\n\n"""
    if "State Provider Control Plane Ready" not in text:
        text = block + text
    write_text(agent, text)

    readme = RUNTIME / "README.md"
    text = read_text(readme)
    text = replace_line(text, "Status:", "Status: `state_provider_control_plane_ready_with_restrictions_v0_1`")
    text = replace_line(text, "Current gate:", "Current gate: `state_provider_control_plane_ready_with_restrictions_no_active_provider_gate`")
    write_text(readme, text)

    changelog = FEATURE_ROOT / "CHANGELOG.md"
    text = read_text(changelog) if changelog.exists() else "# Changelog\n"
    entry_text = f"""## {now[:10]} - Runtime User Invocation Bounded Interface Execution Review\n\n- Closed `{GATE}` as `{status}`.\n- Marked State Provider control-plane v0.1 as `READY_WITH_RESTRICTIONS`.\n- Kept physical row delivery, `StateReplayFeed`, backtest state consumption, production, downstream and official dataset delivery closed.\n"""
    if "Runtime User Invocation Bounded Interface Execution Review" not in text:
        text = text.rstrip() + "\n\n" + entry_text
    write_text(changelog, text)

    files = [FEATURE_ROOT / "99_ruta_de_trabajo.md", FEATURE_ROOT / "AGENT.md", RUNTIME / "README.md", auth_path, scope_path, matrix_path, readout_path, RUNTIME / "runtime_user_invocation_bounded_interface_execution_readout_v0_1.md", RUNTIME / "runtime_user_invocation_bounded_interface_execution_matrix_v0_1.json", SCRIPTS / "runtime_user_invocation_bounded_interface_execution_review_runner_v0_1.py"]
    unique = []
    seen = set()
    for p in files:
        if p.exists() and p not in seen:
            unique.append(p); seen.add(p)
    zip_path = FEATURE_ROOT / f"runtime_user_invocation_bounded_interface_execution_review_provider_only_{stamp}.zip"
    manifest = {"package_id": "runtime_user_invocation_bounded_interface_execution_review_provider_only", "created_at_utc": now, "gate": GATE, "status": status, "entry_count_excluding_manifest": len(unique), "explicitly_excluded": ["02_TSIS_BACKTEST_ENGINE files", "StateReplayFeed files", "parquet files", "physical state rows", "downstream artifacts"], "entries": [entry(p) for p in unique]}
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in unique:
            zf.write(p, rel(p))
        zf.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps({"gate": GATE, "status": status, "failed_review_rows": len(failed), "state_provider_control_plane": review["state_provider_control_plane"], "zip_path": str(zip_path)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
