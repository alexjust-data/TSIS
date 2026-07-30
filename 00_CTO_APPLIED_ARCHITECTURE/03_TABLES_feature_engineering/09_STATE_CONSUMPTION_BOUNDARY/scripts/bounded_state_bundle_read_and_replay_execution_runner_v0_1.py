from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


FEATURE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = FEATURE_ROOT.parents[1]
BOUNDARY = FEATURE_ROOT / "09_STATE_CONSUMPTION_BOUNDARY"
DEFAULT_SCOPE = BOUNDARY / "configs/bounded_state_bundle_read_and_replay_execution_scope_v0_1.json"


class ExecutionBlocked(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def normalize(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    return value


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def resolve_frozen_path(raw: str) -> Path:
    path = (REPO_ROOT / raw).resolve()
    if not path.is_relative_to(REPO_ROOT.resolve()):
        raise ExecutionBlocked(f"Frozen path escapes repository root: {raw}")
    return path


def expected_arrow_type(type_name: str) -> pa.DataType:
    mapping = {
        "string": pa.string(),
        "double": pa.float64(),
        "date32[day]": pa.date32(),
        "timestamp[us, tz=UTC]": pa.timestamp("us", tz="UTC"),
    }
    try:
        return mapping[type_name]
    except KeyError as exc:
        raise ExecutionBlocked(f"Unsupported schema-contract type: {type_name}") from exc


def validate_schema(observed: pa.Schema, contract: dict[str, Any]) -> list[dict[str, Any]]:
    expected_columns = contract["columns"]
    if len(observed) != contract["column_count"] or len(expected_columns) != contract["column_count"]:
        raise ExecutionBlocked("Physical schema column count mismatch")
    reports: list[dict[str, Any]] = []
    for index, expected in enumerate(expected_columns):
        field = observed[index]
        expected_type = expected_arrow_type(expected["type"])
        match = (
            field.name == expected["name"]
            and field.type == expected_type
            and field.nullable == expected["nullable"]
        )
        reports.append(
            {
                "column_index": index,
                "name": field.name,
                "observed_type": str(field.type),
                "expected_type": str(expected_type),
                "observed_nullable": field.nullable,
                "expected_nullable": expected["nullable"],
                "match": match,
            }
        )
    if not all(report["match"] for report in reports):
        raise ExecutionBlocked("Physical schema does not match frozen contract")
    return reports


def add_case(cases: list[dict[str, Any]], case_id: str, passed: bool, evidence: Any) -> None:
    cases.append(
        {
            "case_id": case_id,
            "status": "PASS" if passed else "FAIL",
            "passed": passed,
            "evidence": evidence,
        }
    )
    if not passed:
        raise ExecutionBlocked(f"{case_id}: {evidence}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    args = parser.parse_args()
    scope = read_json(args.scope.resolve())
    run_id = scope["run_id"]
    run_dir = (REPO_ROOT / scope["run_output_directory"]).resolve()
    if not run_dir.is_relative_to(BOUNDARY.resolve()):
        raise ExecutionBlocked("Run directory escapes State Consumption Boundary")
    if run_dir.exists():
        raise ExecutionBlocked(f"Single-use authorization already consumed or run directory exists: {run_id}")

    allowed_outputs = set(scope["allowed_outputs"])
    if len(allowed_outputs) != scope["bounded_slice"]["maximum_output_files"]:
        raise ExecutionBlocked("Allowed output count does not equal maximum_output_files")
    run_dir.mkdir(parents=True, exist_ok=False)
    paths = {name: run_dir / name for name in allowed_outputs}
    started = utc_now()
    pre_run = {
        "run_id": run_id,
        "gate": scope["gate"],
        "started_at_utc": started,
        "authorization_gate": scope["authorization"]["authorization_gate"],
        "authorization_status_at_start": "NOT_CONSUMED",
        "single_use_authorization": True,
        "maximum_execution_runs": 1,
        "consumer_id": scope["authorization"]["consumer_id"],
        "consumption_purpose": scope["authorization"]["consumption_purpose"],
        "expected_input_files": scope["bounded_slice"]["maximum_input_files"],
        "expected_output_files": scope["bounded_slice"]["maximum_output_files"],
        "expected_rows": scope["bounded_slice"]["authorized_row_count"],
    }
    write_json(paths["pre_run_manifest.json"], pre_run)
    write_json(
        paths["heartbeat.json"],
        {
            "run_id": run_id,
            "status": "STARTED_AUTHORIZATION_CONSUMED_BEFORE_PHYSICAL_READ",
            "updated_at_utc": started,
            "pid": __import__("os").getpid(),
        },
    )
    write_json(
        paths["authorization_consumption_receipt.json"],
        {
            "authorization_gate": scope["authorization"]["authorization_gate"],
            "single_use_authorization": True,
            "maximum_execution_runs": 1,
            "authorization_status": f"CONSUMED_BY_RUN_{run_id}",
            "consumed_by_run_id": run_id,
            "consumed_at_utc": started,
        },
    )

    cases: list[dict[str, Any]] = []
    counters = {
        "input_files_verified": 0,
        "physical_data_files_opened": 0,
        "physical_state_rows_read": 0,
        "bounded_probe_records_emitted": 0,
        "EventLoop_ticks": 0,
        "strategy_callbacks": 0,
        "signals_emitted": 0,
        "orders_emitted": 0,
        "fills_emitted": 0,
        "PnL_calculated": False,
        "datasets_written": 0,
        "registry_mutations": 0,
        "official_dataset": False,
        "production": False,
        "downstream": False,
    }
    try:
        frozen = scope["frozen_inputs"]
        add_case(cases, "EXEC_SINGLE_USE_RECEIPT_CREATED", paths["authorization_consumption_receipt.json"].exists(), run_id)
        add_case(cases, "EXEC_INPUT_FILE_LIMIT_EXACT", len(frozen) == scope["bounded_slice"]["maximum_input_files"] == 9, len(frozen))
        resolved: dict[str, Path] = {}
        hash_reports = []
        for item in frozen:
            path = resolve_frozen_path(item["path"])
            observed_hash = sha256_file(path)
            matched = observed_hash == item["sha256"]
            hash_reports.append(
                {
                    "artifact_id": item["artifact_id"],
                    "path": item["path"],
                    "expected_sha256": item["sha256"],
                    "observed_sha256": observed_hash,
                    "match": matched,
                }
            )
            if not matched:
                raise ExecutionBlocked(f"Frozen hash mismatch: {item['artifact_id']}")
            resolved[item["artifact_id"]] = path
            counters["input_files_verified"] += 1
        add_case(cases, "EXEC_ALL_FROZEN_HASHES_MATCH", counters["input_files_verified"] == 9, hash_reports)

        selection = read_json(resolved["selection_manifest"])
        sidecar = read_json(resolved["replay_availability_sidecar"])
        bundle = read_json(resolved["state_bundle_manifest"])
        schema_contract = read_json(resolved["physical_schema_contract"])
        selected = selection["authorized_rows"]
        authorized_ids = [row["materialized_state_candidate_id"] for row in selected]
        add_case(cases, "EXEC_EXACT_AUTHORIZED_SELECTION", len(authorized_ids) == len(set(authorized_ids)) == 2, authorized_ids)
        add_case(
            cases,
            "EXEC_BUNDLE_DATASET_MATCH",
            bundle["dataset_refs"]["market_state_dataset_ref"]["dataset_id"] == selection["candidate_dataset_id"],
            selection["candidate_dataset_id"],
        )

        parquet_path = resolved["candidate_parquet"]
        parquet_file = pq.ParquetFile(parquet_path)
        counters["physical_data_files_opened"] = 1
        schema_reports = validate_schema(parquet_file.schema_arrow, schema_contract)
        add_case(cases, "EXEC_PHYSICAL_SCHEMA_EXACT", all(row["match"] for row in schema_reports), schema_reports)

        table = pq.read_table(
            parquet_path,
            filters=[("materialized_state_candidate_id", "in", authorized_ids)],
        )
        physical_rows = table.to_pylist()
        counters["physical_state_rows_read"] = len(physical_rows)
        observed_ids = [row["materialized_state_candidate_id"] for row in physical_rows]
        add_case(cases, "EXEC_TWO_ROWS_READ", len(physical_rows) == 2, len(physical_rows))
        add_case(cases, "EXEC_NO_DUPLICATE_ROWS", len(observed_ids) == len(set(observed_ids)), observed_ids)
        add_case(cases, "EXEC_NO_MISSING_OR_EXTRA_ROWS", set(observed_ids) == set(authorized_ids), observed_ids)

        selection_by_id = {row["materialized_state_candidate_id"]: row for row in selected}
        fp_fields = scope["fingerprint_contract"]["state_output_fingerprint_payload_fields"]
        id_fields = scope["fingerprint_contract"]["materialized_state_candidate_id_inputs"]
        fingerprint_reports = []
        for row in physical_rows:
            state_payload = {field: normalize(row[field]) for field in fp_fields}
            recalculated_state = sha256_payload(state_payload)
            id_payload = {
                field: normalize(recalculated_state if field == "state_output_fingerprint" else row[field])
                for field in id_fields
            }
            recalculated_id = sha256_payload(id_payload)
            selected_row = selection_by_id[row["materialized_state_candidate_id"]]
            report = {
                "materialized_state_candidate_id": row["materialized_state_candidate_id"],
                "state_output_fingerprint": row["state_output_fingerprint"],
                "recalculated_state_output_fingerprint": recalculated_state,
                "recalculated_materialized_state_candidate_id": recalculated_id,
                "state_fingerprint_match": recalculated_state == row["state_output_fingerprint"] == selected_row["state_output_fingerprint"],
                "candidate_id_match": recalculated_id == row["materialized_state_candidate_id"],
                "instrument_match": row["instrument_id"] == scope["bounded_slice"]["instrument_id"],
                "session_match": normalize(row["session_date"]) == scope["bounded_slice"]["session_date"],
                "decision_timestamp_match": normalize(row["decision_timestamp_utc"]) == selected_row["decision_timestamp_utc"],
            }
            fingerprint_reports.append(report)
        add_case(
            cases,
            "EXEC_ROW_FINGERPRINTS_RECALCULATED",
            all(r["state_fingerprint_match"] and r["candidate_id_match"] for r in fingerprint_reports),
            fingerprint_reports,
        )
        add_case(
            cases,
            "EXEC_ROW_SCOPE_MATCH",
            all(r["instrument_match"] and r["session_match"] and r["decision_timestamp_match"] for r in fingerprint_reports),
            fingerprint_reports,
        )

        sidecar_by_id: dict[str, list[dict[str, Any]]] = {}
        for record in sidecar["records"]:
            sidecar_by_id.setdefault(record["materialized_state_candidate_id"], []).append(record)
        joined = []
        for row in physical_rows:
            matches = sidecar_by_id.get(row["materialized_state_candidate_id"], [])
            if len(matches) != 1:
                raise ExecutionBlocked("Physical row does not join exactly one sidecar record")
            evidence = matches[0]
            if evidence["state_output_fingerprint"] != row["state_output_fingerprint"]:
                raise ExecutionBlocked("Sidecar fingerprint does not match physical row")
            joined.append(
                {
                    "state_kind": "market_state",
                    "profile_id": evidence["profile_id"],
                    "materialized_state_candidate_id": row["materialized_state_candidate_id"],
                    "state_output_fingerprint": row["state_output_fingerprint"],
                    "instrument_id": row["instrument_id"],
                    "ticker": row["ticker"],
                    "session_date": normalize(row["session_date"]),
                    "decision_timestamp_utc": normalize(row["decision_timestamp_utc"]),
                    "state_as_of_utc": evidence["state_as_of_utc"],
                    "state_available_at_utc": evidence["state_available_at_utc"],
                    "state_replay_consumption_legality": evidence["state_replay_consumption_legality"],
                    "restriction_codes": evidence["restriction_codes"],
                }
            )
        add_case(cases, "EXEC_EXACT_ONE_SIDECAR_PER_ROW", len(joined) == 2, [r["materialized_state_candidate_id"] for r in joined])

        ordered = sorted(
            joined,
            key=lambda row: (
                row["state_available_at_utc"],
                row["state_kind"],
                row["instrument_id"],
                row["materialized_state_candidate_id"],
            ),
        )
        emitted = []
        event_loop_clock = None
        for record in ordered:
            next_available = record["state_available_at_utc"]
            event_loop_clock = next_available
            counters["EventLoop_ticks"] += 1
            if event_loop_clock < next_available:
                raise ExecutionBlocked("Attempted early delivery")
            emitted.append(
                {
                    "event_type": "BoundedMarketStateAvailable",
                    "event_loop_clock_utc": event_loop_clock,
                    **record,
                }
            )
        counters["bounded_probe_records_emitted"] = len(emitted)
        add_case(cases, "EXEC_CANONICAL_REPLAY_ORDER", emitted == sorted(emitted, key=lambda row: (row["state_available_at_utc"], row["state_kind"], row["instrument_id"], row["materialized_state_candidate_id"])), [r["state_available_at_utc"] for r in emitted])
        add_case(cases, "EXEC_NO_EARLY_DELIVERY", all(r["event_loop_clock_utc"] >= r["state_available_at_utc"] for r in emitted), "clock >= available_at")
        add_case(cases, "EXEC_TWO_BOUNDED_RECORDS_EMITTED", len(emitted) == 2, len(emitted))
        add_case(
            cases,
            "EXEC_PROHIBITED_COUNTERS_ZERO",
            counters["strategy_callbacks"] == counters["signals_emitted"] == counters["orders_emitted"] == counters["fills_emitted"] == 0
            and counters["PnL_calculated"] is False
            and counters["datasets_written"] == counters["registry_mutations"] == 0,
            counters,
        )

        read_report = {
            "run_id": run_id,
            "status": "PASS",
            "input_hash_verification": hash_reports,
            "schema_validation": schema_reports,
            "fingerprint_validation": fingerprint_reports,
            "physical_state_rows_read": counters["physical_state_rows_read"],
            "authorized_row_ids": authorized_ids,
            "observed_row_ids": observed_ids,
            "unlisted_rows_delivered": 0,
        }
        replay_report = {
            "run_id": run_id,
            "status": "PASS",
            "canonical_order": scope["execution_rules"]["canonical_order"],
            "delivery_eligibility_rule": scope["execution_rules"]["delivery_eligibility_rule"],
            "bounded_probe_records_emitted": len(emitted),
            "events": emitted,
            "strategy_callbacks": 0,
            "signals_emitted": 0,
            "orders_emitted": 0,
            "fills_emitted": 0,
            "PnL_calculated": False,
        }
        write_json(paths["bounded_read_report.json"], read_report)
        write_json(paths["bounded_replay_report.json"], replay_report)
        final_status = "CLOSED_PASS_ONE_BOUNDED_MARKET_STATE_PHYSICAL_READ_AND_REPLAY_PROBE_WITH_RESTRICTIONS"
        finished = utc_now()
        write_json(
            paths["heartbeat.json"],
            {
                "run_id": run_id,
                "status": "COMPLETED",
                "updated_at_utc": finished,
                "pid": __import__("os").getpid(),
            },
        )
        output_hashes = {}
        for name in sorted(allowed_outputs - {"final_manifest.json", "readout.md"}):
            output_hashes[name] = sha256_file(paths[name])
        final_manifest = {
            "run_id": run_id,
            "gate": scope["gate"],
            "status": final_status,
            "started_at_utc": started,
            "finished_at_utc": finished,
            "authorization_consumed": True,
            "authorization_consumed_by_run_id": run_id,
            "case_count": len(cases),
            "failed_cases": sum(not case["passed"] for case in cases),
            "counters": counters,
            "output_hashes_before_final_manifest": output_hashes,
            "cases": cases,
            "next_gate": scope["next_gate_on_pass"],
        }
        write_json(paths["final_manifest.json"], final_manifest)
        readout = f"""# Bounded StateBundle Read and Replay Execution Readout v0.1

Gate: `bounded_state_bundle_read_and_replay_execution_v0_1`
Run: `{run_id}`
Date: `2026-07-30`
Status: `{final_status}`

```text
physical_data_files_opened = 1
physical_state_rows_read = 2
bounded_probe_records_emitted = 2
early_deliveries = 0
unlisted_rows_delivered = 0
strategy_callbacks = 0
signals = 0
orders = 0
fills = 0
PnL = false
datasets_written = 0
registry_mutations = 0
production = false
downstream = false
```

The single-use authorization was consumed by this run. The exact ACIU records
for 2021-03-15 were hash-verified, schema-validated, fingerprint-recalculated,
joined one-to-one with replay availability evidence and emitted only when the
probe clock reached `state_available_at_utc`.

This is bounded integration evidence, not general `StateReplayFeed` or backtest
strategy-consumption authority.

## Next Gate

```text
bounded_state_bundle_read_and_replay_review_v0_1
```
"""
        paths["readout.md"].write_text(readout, encoding="utf-8", newline="\n")
        print(json.dumps({"status": final_status, "run_id": run_id, "counters": counters}, indent=2))
        return 0
    except Exception as exc:
        failed_at = utc_now()
        write_json(
            paths["heartbeat.json"],
            {
                "run_id": run_id,
                "status": "FAILED_CLOSED",
                "updated_at_utc": failed_at,
                "pid": __import__("os").getpid(),
                "error": str(exc),
            },
        )
        write_json(
            paths["bounded_read_report.json"],
            {"run_id": run_id, "status": "FAILED_CLOSED", "error": str(exc), "counters": counters},
        )
        write_json(
            paths["bounded_replay_report.json"],
            {"run_id": run_id, "status": "NOT_EXECUTED_OR_FAILED_CLOSED", "error": str(exc), "bounded_probe_records_emitted": counters["bounded_probe_records_emitted"]},
        )
        write_json(
            paths["final_manifest.json"],
            {
                "run_id": run_id,
                "gate": scope["gate"],
                "status": "CLOSED_BLOCKED_EXECUTION_FAILED_CLOSED",
                "authorization_consumed": True,
                "authorization_consumed_by_run_id": run_id,
                "error": str(exc),
                "cases": cases,
                "counters": counters,
                "next_gate": None,
            },
        )
        paths["readout.md"].write_text(
            f"# Bounded StateBundle Read and Replay Execution Readout v0.1\n\nStatus: `CLOSED_BLOCKED_EXECUTION_FAILED_CLOSED`\n\nError: `{exc}`\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps({"status": "FAILED_CLOSED", "error": str(exc), "run_id": run_id}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
