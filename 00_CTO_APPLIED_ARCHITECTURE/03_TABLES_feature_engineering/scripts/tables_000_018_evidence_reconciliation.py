from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_FOUND = "FOUND"
STATUS_MISSING = "MISSING"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@dataclass
class EvidenceFile:
    category: str
    path: Path
    normalized_path: str


def index_evidence_files(scope: dict[str, Any]) -> list[EvidenceFile]:
    roots = scope["data_foundation"]["evidence_roots"]
    indexed: list[EvidenceFile] = []
    for category, raw_root in roots.items():
        root = Path(raw_root)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.as_posix()
            indexed.append(EvidenceFile(category=category, path=path, normalized_path=normalize(rel)))
    return indexed


def parse_status_matrix(path: Path) -> dict[str, dict[str, str]]:
    text = read_text(path)
    rows: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 8:
            continue
        output = cells[0].strip("`")
        rows[output] = {
            "output": output,
            "rows": cells[1],
            "parquet_files": cells[2],
            "scope": cells[3],
            "test_evidence": cells[4],
            "current_status": cells[5].strip("`"),
            "primary_allowed_use_today": cells[6],
            "main_blocker": cells[7],
        }
    return rows


def find_matches(index: list[EvidenceFile], table: dict[str, Any], category: str) -> list[str]:
    wanted = [normalize(x) for x in table.get("search_tokens", [])]
    wanted += [normalize(x) for x in table.get("data_foundation_dataset_ids", [])]
    wanted = sorted(set(x for x in wanted if x))
    matches: list[str] = []
    for item in index:
        if item.category != category:
            continue
        if any(token in item.normalized_path for token in wanted):
            matches.append(item.path.as_posix())
    return sorted(set(matches))


def matched_status_matrix_rows(status_rows: dict[str, dict[str, str]], table: dict[str, Any]) -> list[dict[str, str]]:
    tokens = [normalize(x) for x in table.get("data_foundation_dataset_ids", [])]
    tokens = sorted(set(x for x in tokens if x))
    out: list[dict[str, str]] = []
    for output, row in status_rows.items():
        norm_output = normalize(output)
        if any(token == norm_output or token in norm_output or norm_output in token for token in tokens):
            out.append(row)
    return out


def status_from_matches(matches: list[str]) -> str:
    return STATUS_FOUND if matches else STATUS_MISSING


def output_statuses(rows: list[dict[str, str]]) -> list[str]:
    return sorted(set(row["current_status"] for row in rows if row.get("current_status")))


def physical_status(table_id: str, rows: list[dict[str, str]], status_text: str) -> str:
    if rows:
        if any(row.get("current_status") != "not_materialized" for row in rows):
            return STATUS_FOUND
    if table_id == "013" and "ohlcv_1m_quote_guarded_full_universe_v0_1" in status_text:
        return "FOUND_REPAIR_OVERLAY_AND_CANDIDATE_TREE"
    if table_id == "018" and "intraday_scanner_candidates_table_v0_1 is the forward detector" in status_text:
        return "FOUND_CONTROLLED_REPLAY_EVIDENCE"
    return STATUS_MISSING


def promotion_status(table_id: str, status_text: str) -> str:
    if table_id == "013" and "promoted_manifest_state = PASS" in status_text:
        return "FOUND_REPAIR_MANIFEST_PROMOTION_NOT_DATASET_PROMOTION"
    if table_id == "016":
        return "NOT_FOUND_FOR_DATA_FOUNDATION_DATASET; SEMANTIC_PROFILE_PROMOTION_EXISTS_OUTSIDE_DATA_FOUNDATION"
    if table_id == "017":
        return "NOT_FOUND_FOR_CURRENT_EVENT_STATE_PROFILE; LEGACY_CANDIDATE_NOT_PROMOTED"
    return STATUS_MISSING


def institutional_conclusion(table: dict[str, Any], statuses: list[str], row: dict[str, str]) -> str:
    table_id = table["table_id"]
    if table_id == "013":
        return "PARTIALLY_RECONCILED_WITH_PROMOTED_REPAIR_OVERLAY_AND_CANDIDATE_TREE"
    if table_id == "016":
        return "PARTIALLY_RECONCILED_WITH_SEMANTIC_PHYSICAL_SPLIT"
    if table_id == "017":
        return "PARTIALLY_RECONCILED_WITH_DESIGN_ONLY_CURRENT_PROFILE"
    if table_id == "018":
        return "PROVEN_RESTRICTED_CONTROLLED_REPLAY_CANDIDATE"
    if "validated_for_declared_scope" in statuses and any(
        status in statuses
        for status in ("controlled_candidate_not_promoted", "controlled_replay_candidate")
    ):
        return "PROVEN_RESTRICTED_DATASET_WITH_CANDIDATE_EXTENSION"
    if any(status in statuses for status in ("scoped_pilot", "seed_state_sample", "controlled_candidate_not_promoted", "controlled_replay_candidate")):
        return "PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS"
    if "validated_for_declared_scope" in statuses:
        return "PROVEN_RESTRICTED_DATASET"
    found_count = sum(1 for key in (
        "schema_contract_status",
        "dataset_contract_status",
        "registry_entry_status",
        "consumption_policy_status",
        "validator_evidence_status",
    ) if row[key] == STATUS_FOUND)
    if found_count >= 3:
        return "PARTIALLY_RECONCILED"
    return "UNRESOLVED"


def confidence(conclusion: str, row: dict[str, str]) -> str:
    if conclusion.startswith("PROVEN_"):
        return "PROVEN"
    if conclusion.startswith("PARTIALLY_RECONCILED"):
        return "PARTIAL"
    if row["physical_artifact_status"] == STATUS_MISSING:
        return "UNRESOLVED"
    return "SUPPORTED"


def summarize_evidence(matches: dict[str, list[str]], status_rows: list[dict[str, str]]) -> str:
    parts = []
    if status_rows:
        parts.append("status_matrix:" + ",".join(row["output"] for row in status_rows))
    for category, paths in matches.items():
        if paths:
            parts.append(f"{category}:{len(paths)}")
    return "; ".join(parts) if parts else "none"


def make_reconciliation(scope: dict[str, Any], run_dir: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    status_matrix_path = Path(scope["data_foundation"]["status_matrix"])
    status_text = read_text(status_matrix_path)
    status_rows = parse_status_matrix(status_matrix_path)
    index = index_evidence_files(scope)
    records: list[dict[str, str]] = []

    for table in scope["tables"]:
        matches = {
            "canonical_schema": find_matches(index, table, "canonical_schema"),
            "dataset_contract": find_matches(index, table, "dataset_contract"),
            "registry_entry": find_matches(index, table, "registry_entry"),
            "consumption_policy": find_matches(index, table, "consumption_policy"),
            "validator": find_matches(index, table, "validator"),
            "module_contract_outputs": find_matches(index, table, "module_contract_outputs"),
        }
        rows = matched_status_matrix_rows(status_rows, table)
        statuses = output_statuses(rows)
        record: dict[str, str] = {
            "table_id": table["table_id"],
            "canonical_name": table["canonical_name"],
            "priority_group": table["priority_group"],
            "data_foundation_outputs": ",".join(row["output"] for row in rows) or "",
            "data_foundation_statuses": ",".join(statuses) or "",
            "physical_artifact_status": physical_status(table["table_id"], rows, status_text),
            "schema_contract_status": status_from_matches(matches["canonical_schema"]),
            "dataset_contract_status": status_from_matches(matches["dataset_contract"]),
            "registry_entry_status": status_from_matches(matches["registry_entry"]),
            "consumption_policy_status": status_from_matches(matches["consumption_policy"]),
            "validator_evidence_status": status_from_matches(matches["validator"]),
            "module_contract_status": status_from_matches(matches["module_contract_outputs"]),
            "promotion_record_status": promotion_status(table["table_id"], status_text),
            "official_dataset_inferred": "false",
            "evidence_summary": summarize_evidence(matches, rows),
        }
        record["institutional_conclusion"] = institutional_conclusion(table, statuses, record)
        record["confidence"] = confidence(record["institutional_conclusion"], record)
        records.append(record)

    proven_restricted = sum(
        1 for r in records
        if r["institutional_conclusion"].startswith("PROVEN_RESTRICTED_DATASET")
    )
    proven_candidates = sum(
        1 for r in records
        if r["institutional_conclusion"].startswith("PROVEN_VALIDATED_CANDIDATE")
    )
    partial = sum(
        1 for r in records
        if r["institutional_conclusion"].startswith("PARTIALLY_RECONCILED")
    )
    controlled_replay = sum(
        1 for r in records
        if r["institutional_conclusion"] == "PROVEN_RESTRICTED_CONTROLLED_REPLAY_CANDIDATE"
    )
    unresolved = sum(1 for r in records if r["institutional_conclusion"] == "UNRESOLVED")
    classified_tables = proven_restricted + proven_candidates + partial + controlled_replay + unresolved

    summary = {
        "tables_seen": len(records),
        "proven_restricted_datasets": proven_restricted,
        "proven_validated_candidates": proven_candidates,
        "partial_reconciliations": partial,
        "proven_restricted_controlled_replay_candidates": controlled_replay,
        "unresolved": unresolved,
        "classified_tables": classified_tables,
        "classification_invariant_pass": classified_tables == len(records),
        "official_datasets_inferred": sum(1 for r in records if r["official_dataset_inferred"] == "true"),
        "parquet_files_read": 0,
        "source_market_data_rows_read": 0,
        "dataset_promotions_written": 0,
        "event_type_registry_entries_written": 0,
        "event_detection_runs_started": 0,
        "run_dir": run_dir.as_posix(),
    }
    return records, summary


def write_matrix_csv(path: Path, records: list[dict[str, str]]) -> None:
    fieldnames = [
        "table_id",
        "canonical_name",
        "priority_group",
        "data_foundation_outputs",
        "data_foundation_statuses",
        "physical_artifact_status",
        "schema_contract_status",
        "dataset_contract_status",
        "registry_entry_status",
        "consumption_policy_status",
        "validator_evidence_status",
        "module_contract_status",
        "promotion_record_status",
        "official_dataset_inferred",
        "institutional_conclusion",
        "confidence",
        "evidence_summary",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def render_readout(run_id: str, summary: dict[str, Any], records: list[dict[str, str]]) -> str:
    lines = [
        "# Tables 000-018 Evidence Reconciliation Readout v0.1",
        "",
        "Status: `CLOSED_WITH_FINDINGS_NO_PROMOTION`",
        f"Run: `{run_id}`",
        "Date: `2026-07-24`",
        "",
        "## Boundary",
        "",
        "```text",
        "dataset promotion = false",
        "official dataset registry write = false",
        "official parquet write = false",
        "production builder execution = false",
        "downstream consumption = false",
        "Market State materialization = false",
        "Event State materialization = false",
        "event type registry population = false",
        "event detection execution = false",
        "source_market_data_rows_read = 0",
        "parquet_files_read = 0",
        "```",
        "",
        "## Summary",
        "",
        "```text",
    ]
    for key in (
        "tables_seen",
        "proven_restricted_datasets",
        "proven_validated_candidates",
        "partial_reconciliations",
        "proven_restricted_controlled_replay_candidates",
        "unresolved",
        "classified_tables",
        "classification_invariant_pass",
        "official_datasets_inferred",
        "source_market_data_rows_read",
        "parquet_files_read",
        "dataset_promotions_written",
        "event_type_registry_entries_written",
        "event_detection_runs_started",
    ):
        lines.append(f"{key} = {summary[key]}")
    lines += [
        "```",
        "",
        "## Table Conclusions",
        "",
        "| ID | Table | Data Foundation status | Conclusion | Confidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        df_status = record["data_foundation_statuses"] or record["physical_artifact_status"]
        lines.append(
            f"| {record['table_id']} | `{record['canonical_name']}` | `{df_status}` | "
            f"`{record['institutional_conclusion']}` | `{record['confidence']}` |"
        )
    lines += [
        "",
        "## Critical Interpretations",
        "",
        "- `016_market_state_table` is reconciled as a semantic/physical split: Data Foundation has a legacy controlled candidate, while Applied Architecture has promoted `market_state_core_four_intraday_profile_v0_1` as an official semantic profile. This does not create an official physical Market State dataset.",
        "- `017_event_state_table` remains design-only for the current Event State architecture. Legacy controlled candidate evidence does not populate the current Event Type registry and does not authorize Event State execution.",
        "- `013_ohlcv_1m_quote_guarded` is reconciled as a promoted repair overlay plus candidate physical tree, not as an unrestricted official full-universe intraday dataset.",
        "- `018_intraday_scanner_candidates_table` is reconciled as controlled replay/candidate detector evidence. It is not Event Type authority.",
        "",
        "## Next Gate",
        "",
        "```text",
        "event_type_registry_seed_design_v0_1",
        "```",
        "",
        "No execution, promotion, production or downstream consumption opens from this readout.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", required=True)
    args = parser.parse_args()

    scope_path = Path(args.scope)
    scope = json.loads(read_text(scope_path))
    started = utc_now()
    run_id = f"tables_000_018_evidence_reconciliation_v0_1_{started.strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = Path(scope["runs_root"]) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    pre_manifest = {
        "run_id": run_id,
        "started_at_utc": started.isoformat().replace("+00:00", "Z"),
        "scope_path": scope_path.as_posix(),
        "scope_sha256": sha256_file(scope_path),
        "authorized_gate": scope["authorized_gate"],
        "tables_expected": len(scope["tables"]),
        "parquet_reads_allowed": False,
        "source_market_data_reads_allowed": False,
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": "running", "updated_at_utc": pre_manifest["started_at_utc"]})

    records, summary = make_reconciliation(scope, run_dir)
    write_matrix_csv(run_dir / "reconciliation_matrix.csv", records)
    write_json(run_dir / "reconciliation_matrix.json", records)

    readout = render_readout(run_id, summary, records)
    (run_dir / "tables_000_018_evidence_reconciliation_readout.md").write_text(readout, encoding="utf-8")
    Path(scope["readout_output_path"]).write_text(readout, encoding="utf-8")

    completed = utc_now().isoformat().replace("+00:00", "Z")
    final_manifest = {
        "run_id": run_id,
        "status": "CLOSED_WITH_FINDINGS_NO_PROMOTION",
        "completed_at_utc": completed,
        "summary": summary,
        "outputs": {
            "reconciliation_matrix_csv": (run_dir / "reconciliation_matrix.csv").as_posix(),
            "reconciliation_matrix_json": (run_dir / "reconciliation_matrix.json").as_posix(),
            "run_readout": (run_dir / "tables_000_018_evidence_reconciliation_readout.md").as_posix(),
            "persistent_readout": scope["readout_output_path"],
        },
        "boundary": {
            "official_dataset_registry_write": False,
            "official_parquet_write": False,
            "production_builder_execution": False,
            "downstream_consumption": False,
            "source_market_data_rows_read": 0,
            "parquet_files_read": 0,
        },
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": "complete", "updated_at_utc": completed})
    print(json.dumps({"run_id": run_id, "status": final_manifest["status"], "summary": summary}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
