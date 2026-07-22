from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1"
RUN_ID_PREFIX = "experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_scale_a_execution_scope_v0_1.json"
)
REQUIRED_OBJECT_IDS = [
    "trading_activity",
    "price_movement",
    "price_location_structure",
    "volatility_range_state",
]
ALLOWED_NAMESPACES = [
    "trading_activity__",
    "price_movement__",
    "price_location_structure__",
    "volatility_range_state__",
]
SEMANTIC_JOIN_KEY = ["instrument_id", "ticker", "session_date", "decision_timestamp_utc", "decision_case"]


class ScaleAIntegrationError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json(json_safe(value)).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe(v) for v in value]
    return value


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ScaleAIntegrationError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(json_safe(row), ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize_cell(value: Any) -> str:
    if value is None:
        return ""
    safe = json_safe(value)
    if isinstance(safe, (dict, list)):
        return json.dumps(safe, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(safe)


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialize_cell(row.get(field)) for field in fieldnames})


def resolve_path(raw: str, base: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_info(repo_root: Path) -> dict[str, Any]:
    return {
        "commit": git_value(["git", "rev-parse", "HEAD"], repo_root),
        "branch": git_value(["git", "branch", "--show-current"], repo_root),
        "dirty": bool(git_value(["git", "status", "--porcelain"], repo_root)),
    }


def load_integration_module(script_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("tsis_core_four_market_state_integration_probe", script_path)
    if spec is None or spec.loader is None:
        raise ScaleAIntegrationError(f"Cannot load integration module from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_authority(scope: dict[str, Any]) -> None:
    authority = scope.get("authority", {})
    for key in ["scale_a_execution_authorized", "integration_execution_allowed_for_scale_a"]:
        if authority.get(key) is not True:
            raise ScaleAIntegrationError(f"Authority violation: {key} must be true")
    for key in [
        "sample_reselection_allowed",
        "sample_manifest_mutation_allowed",
        "013_upstream_read_allowed",
        "raw_quotes_read_allowed",
        "quote_dependent_object_integration_allowed",
        "official_market_state_allowed",
        "official_state_table_write_allowed",
        "production_builder_allowed",
        "state_consumption_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
        "scale_b_calendar_aware_execution_allowed",
        "scale_c_historical_bounded_execution_allowed",
    ]:
        if authority.get(key) is not False:
            raise ScaleAIntegrationError(f"Authority violation: {key} must be false")


def find_latest_builder_run(integration_root: Path) -> Path:
    candidates = sorted(
        p for p in (integration_root / "runs").iterdir()
        if p.is_dir()
        and p.name.startswith("experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_")
        and (p / "final_manifest.json").exists()
    )
    if not candidates:
        raise ScaleAIntegrationError("No accepted Scale A builder/resolution run found")
    accepted = []
    for run_dir in candidates:
        manifest = read_json(run_dir / "final_manifest.json")
        if manifest.get("status") == "CLOSED_PASS_WITH_RESTRICTIONS":
            accepted.append(run_dir)
    if not accepted:
        raise ScaleAIntegrationError("No CLOSED_PASS_WITH_RESTRICTIONS builder/resolution run found")
    return accepted[-1]


def load_contract_status(path: Path) -> dict[str, str]:
    return {row["request_id"]: row.get("output_contract_status", "") for row in read_csv_rows(path)}


def load_determinism_status(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in read_csv_rows(path):
        result[row["request_id"]] = {
            "determinism_status": row.get("determinism_status", ""),
            "repeat_run_fingerprint_match": row.get("repeat_run_fingerprint_match", "").lower() == "true",
        }
    return result


def load_cutoff_status(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in read_csv_rows(path):
        req = row["request_id"]
        current = result.setdefault(req, {"future_leak": False, "rows": 0})
        current["future_leak"] = bool(current["future_leak"] or row.get("future_leak", "").lower() == "true")
        current["rows"] = int(current["rows"]) + 1
    return result


def load_selected_source_report(path: Path) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in read_csv_rows(path):
        counts[row["request_id"]] += 1
    return dict(counts)


def build_context_report(records: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["context_id"])].append(record)
    report: dict[str, dict[str, str]] = {}
    for context_id in sorted(grouped):
        context_records = sorted(grouped[context_id], key=lambda row: str(row.get("object_id")))
        representative = context_records[0]
        payload = {
            "context_id": context_id,
            "instrument_id": representative.get("instrument_id"),
            "ticker": representative.get("ticker"),
            "session_date": representative.get("session_date"),
            "decision_timestamp_utc": representative.get("decision_timestamp_utc"),
            "decision_case": representative.get("decision_case"),
            "object_record_ids": {row["object_id"]: row.get("record_id") for row in context_records},
            "resolution_fingerprints": {row["object_id"]: row.get("resolution_fingerprint") for row in context_records},
        }
        report[context_id] = {
            "context_id": context_id,
            "context_input_fingerprint": sha256_payload(payload),
            "context_acceptance_status": "PASS",
        }
    return report


def summarize(scope: dict[str, Any], run_id: str, builder_run_id: str, records: list[dict[str, Any]], candidates: list[dict[str, Any]], rejected: list[dict[str, Any]], context_rows: list[dict[str, Any]], value_rows: list[dict[str, Any]], cutoff_status: dict[str, dict[str, Any]]) -> dict[str, Any]:
    limits = scope["limits"]
    failed_context_consistency = sum(1 for row in context_rows if row["integration_status"] == "FAILED_CONTEXT_CONSISTENCY")
    failed_contract_or_determinism = sum(1 for row in context_rows if row["integration_status"] == "FAILED_CONTRACT_OR_DETERMINISM")
    rejected_required_object_blocked = sum(1 for row in context_rows if row["integration_status"] == "REJECTED_REQUIRED_OBJECT_BLOCKED")
    future_bar_leaks = sum(1 for row in cutoff_status.values() if row.get("future_leak"))
    blocked_values_admitted = 0
    for candidate in candidates:
        for object_id, status in candidate.get("object_statuses", {}).items():
            if str(status).startswith("BLOCKED"):
                blocked_values_admitted += sum(1 for key in candidate.get("values", {}) if key.startswith(f"{object_id}__"))
    hard_failures = sum([
        failed_context_consistency,
        failed_contract_or_determinism,
        future_bar_leaks,
        blocked_values_admitted,
        int(len(records) != int(limits["expected_resolution_records"])),
        int(len(candidates) != int(limits["expected_integrable_contexts"])),
        int(rejected_required_object_blocked != int(limits["expected_blocked_contexts"])),
        int(len(candidates) > int(limits["maximum_integrated_candidate_records"])),
    ])
    gate_status = "CLOSED_PASS_WITH_RESTRICTIONS" if hard_failures == 0 else "FAILED"
    return {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_id": scope.get("scope_id"),
        "builder_run_id": builder_run_id,
        "integration_execution_status": gate_status,
        "market_state_profile_id": scope["source_integration_profile_id"],
        "input_resolution_records": len(records),
        "contexts_seen": len(context_rows),
        "candidate_records_emitted": len(candidates),
        "expected_candidate_records": int(limits["expected_integrable_contexts"]),
        "rejected_contexts": len(rejected),
        "rejected_required_object_blocked_contexts": rejected_required_object_blocked,
        "expected_rejected_required_object_blocked_contexts": int(limits["expected_blocked_contexts"]),
        "failed_context_consistency": failed_context_consistency,
        "failed_contract_or_determinism": failed_contract_or_determinism,
        "future_bar_leaks": future_bar_leaks,
        "blocked_values_admitted": blocked_values_admitted,
        "admitted_value_rows": len(value_rows),
        "source_market_data_rows_read": 0,
        "candidate_records_are_canonical_market_state": False,
        "candidate_records_are_downstream_consumable": False,
        "state_materialization_allowed": False,
        "candidate_parquet_files_written": 0,
        "official_market_state_allowed": False,
        "production_builder_allowed": False,
        "downstream_consumption_allowed": False,
        "dataset_promotion_allowed": False,
        "full_history_execution_allowed": False,
        "full_universe_execution_allowed": False,
        "hard_validation_failures": hard_failures,
        "next_allowed_gate": "experimental_core_four_market_state_scale_a_candidate_materialization_execution",
    }


def write_readout(path: Path, summary: dict[str, Any], run_dir: Path) -> None:
    lines = [
        "# Experimental Core Four Market State Scale A Market State Integration Execution Readout v0.1",
        "",
        f"run_id: `{summary['run_id']}`",
        f"status: `{summary['integration_execution_status']}`",
        "",
        "## Scope",
        "",
        "This gate consumed the accepted Scale A builder/resolution records and emitted integrated Market State candidate records only.",
        "It did not read market data, did not execute builders, did not materialize parquet and did not authorize downstream consumption.",
        "",
        "## Counts",
        "",
        f"input_resolution_records = {summary['input_resolution_records']}",
        f"contexts_seen = {summary['contexts_seen']}",
        f"candidate_records_emitted = {summary['candidate_records_emitted']}",
        f"rejected_contexts = {summary['rejected_contexts']}",
        f"rejected_required_object_blocked_contexts = {summary['rejected_required_object_blocked_contexts']}",
        f"admitted_value_rows = {summary['admitted_value_rows']}",
        "",
        "## Validation",
        "",
        f"failed_context_consistency = {summary['failed_context_consistency']}",
        f"failed_contract_or_determinism = {summary['failed_contract_or_determinism']}",
        f"future_bar_leaks = {summary['future_bar_leaks']}",
        f"blocked_values_admitted = {summary['blocked_values_admitted']}",
        f"hard_validation_failures = {summary['hard_validation_failures']}",
        "",
        "## Next Gate",
        "",
        "Allowed next: `experimental_core_four_market_state_scale_a_candidate_materialization_execution`.",
        "Still closed: official Market State, production builder, downstream consumption, promotion, full-history, full-universe, Scale B, Scale C.",
        "",
        "## Run Directory",
        "",
        f"`{run_dir}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def artifact_report(paths: dict[str, Path]) -> dict[str, dict[str, Any]]:
    return {name: {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size} for name, path in paths.items() if path.exists()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Integrate Scale A core-four resolution records into bounded Market State candidates.")
    parser.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    parser.add_argument("--builder-run-dir", type=Path, default=None)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    scope_path = args.scope.resolve()
    integration_root = scope_path.parents[1]
    feature_root = integration_root.parent
    repo_root = feature_root.parents[1]
    scope = read_json(scope_path)
    validate_authority(scope)

    builder_run_dir = args.builder_run_dir.resolve() if args.builder_run_dir else find_latest_builder_run(integration_root)
    builder_manifest = read_json(builder_run_dir / "final_manifest.json")
    builder_summary = builder_manifest.get("summary", {})
    if builder_summary.get("builder_resolution_execution_status") != "CLOSED_PASS_WITH_RESTRICTIONS":
        raise ScaleAIntegrationError("Builder/resolution run is not closed PASS_WITH_RESTRICTIONS")
    if builder_summary.get("resolution_records") != int(scope["limits"]["expected_resolution_records"]):
        raise ScaleAIntegrationError("Builder/resolution record count does not match Scale A scope")

    run_id = args.run_id or f"{RUN_ID_PREFIX}_{safe_timestamp()}"
    run_dir = integration_root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    integration_script = integration_root / "scripts" / "core_four_market_state_integration_probe.py"
    integration = load_integration_module(integration_script)
    contract_path = integration_root / "core_four_market_state_integration_design_contract_v0_1.json"
    contract = read_json(contract_path)

    records_path = builder_run_dir / "core_four_resolution_records.jsonl"
    contract_report_path = builder_run_dir / "builder_output_contract_report.csv"
    cutoff_report_path = builder_run_dir / "cutoff_enforcement_report.csv"
    determinism_report_path = builder_run_dir / "determinism_report.csv"
    selected_source_report_path = builder_run_dir / "selected_source_rows_report.csv"

    records = read_jsonl(records_path)
    if len(records) != int(scope["limits"]["expected_resolution_records"]):
        raise ScaleAIntegrationError("Input resolution record count mismatch")

    integration_scope = {
        "profile_id": scope["source_integration_profile_id"],
        "required_object_ids": REQUIRED_OBJECT_IDS,
        "semantic_join_key": SEMANTIC_JOIN_KEY,
        "allowed_value_namespaces": ALLOWED_NAMESPACES,
        "object_atomicity": {"pass_statuses_admitted": ["PASS", "PASS_WITH_RESTRICTIONS"]},
    }
    context_report = build_context_report(records)
    output_contract_status = load_contract_status(contract_report_path)
    determinism_status = load_determinism_status(determinism_report_path)
    cutoff_status = load_cutoff_status(cutoff_report_path)
    selected_source_counts = load_selected_source_report(selected_source_report_path)

    candidates, rejected, context_rows, value_rows = integration.integrate_contexts(
        records=records,
        context_report=context_report,
        output_contract_status=output_contract_status,
        determinism_status=determinism_status,
        cutoff_status=cutoff_status,
        selected_source_counts=selected_source_counts,
        scope=integration_scope,
        contract=contract,
    )

    summary = summarize(scope, run_id, builder_run_dir.name, records, candidates, rejected, context_rows, value_rows, cutoff_status)

    candidate_path = run_dir / "market_state_candidate_records.jsonl"
    rejected_path = run_dir / "rejected_context_report.csv"
    context_path = run_dir / "integration_context_report.csv"
    values_path = run_dir / "integration_value_manifest.csv"
    readout_path = run_dir / "readout.md"
    summary_path = run_dir / "integration_summary.json"
    final_manifest_path = run_dir / "final_manifest.json"

    write_jsonl(candidate_path, candidates)
    write_csv_rows(rejected_path, [
        "context_id", "integration_status", "rejected_reason", "object_statuses",
        "object_record_ids", "context_input_fingerprint",
    ], rejected)
    write_csv_rows(context_path, [
        "context_id", "integration_status", "candidate_emitted", "rejected", "rejected_reason",
        "instrument_id", "ticker", "session_date", "decision_timestamp_utc", "decision_case",
        "object_statuses", "object_record_ids", "context_input_fingerprint", "admitted_value_count",
        "selected_source_report_rows",
    ], context_rows)
    write_csv_rows(values_path, [
        "market_state_candidate_id", "context_id", "object_id", "source_record_id",
        "value_namespace", "value_field", "value_admitted",
    ], value_rows)
    write_json(summary_path, summary)
    write_readout(readout_path, summary, run_dir)

    root_readout = integration_root / "experimental_core_four_market_state_scale_a_market_state_integration_execution_readout_v0_1.md"
    write_readout(root_readout, summary, run_dir)

    if list(run_dir.rglob("*.parquet")):
        raise ScaleAIntegrationError("Parquet output is forbidden in Scale A integration execution")

    output_paths = {
        "market_state_candidate_records": candidate_path,
        "integration_context_report": context_path,
        "rejected_context_report": rejected_path,
        "integration_value_manifest": values_path,
        "core_four_market_state_scale_a_integration_execution_summary": summary_path,
        "readout": readout_path,
    }
    final_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_path": str(scope_path),
        "status": summary["integration_execution_status"],
        "created_at_utc": utc_now(),
        "summary": summary,
        "input_artifacts": artifact_report({
            "builder_final_manifest": builder_run_dir / "final_manifest.json",
            "resolution_records": records_path,
            "builder_output_contract_report": contract_report_path,
            "cutoff_enforcement_report": cutoff_report_path,
            "determinism_report": determinism_report_path,
            "selected_source_rows_report": selected_source_report_path,
            "design_contract": contract_path,
            "scope": scope_path,
        }),
        "artifacts": artifact_report(output_paths),
        "versioned_readout": str(root_readout),
        "authority": {
            "source_market_data_rows_read": 0,
            "builders_executed": False,
            "state_materialization_allowed": False,
            "candidate_parquet_files_written": 0,
            "official_market_state_allowed": False,
            "production_builder_allowed": False,
            "downstream_consumption_allowed": False,
            "dataset_promotion_allowed": False,
            "full_history_execution_allowed": False,
            "full_universe_execution_allowed": False,
        },
        "environment": {"python": sys.version, "platform": platform.platform()},
        "git": git_info(repo_root),
        "next_allowed_gate": summary["next_allowed_gate"],
    }
    write_json(final_manifest_path, final_manifest)

    required_outputs = scope["required_outputs_by_stage"]["scale_a_market_state_integration_execution"]
    missing = [name for name in required_outputs if not (run_dir / name).exists()]
    if missing:
        raise ScaleAIntegrationError(f"Missing required outputs: {missing}")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["hard_validation_failures"] == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScaleAIntegrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
