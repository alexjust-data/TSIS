from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


IMAGE_CSV_HEADER = [
    "contract_version",
    "lesson_id",
    "image_id",
    "source_ref",
    "resolved_path",
    "resolution_status",
    "referenced_from_section_ids",
    "visual_type",
    "contains_numbers",
    "contains_code",
    "contains_chart",
    "contains_platform_config",
    "extracted_values_ref",
    "technical_reading_ref",
    "doctrine_relevance",
    "requires_human_review",
    "notes",
]

TRANSLATION_CSV_HEADER = [
    "contract_version",
    "lesson_id",
    "translation_id",
    "rule_id",
    "target",
    "tsis_artifact_candidate",
    "action_type",
    "priority",
    "blocking_power",
    "consumer_scope",
    "implementation_hint",
    "requires_human_review",
    "source_anchor_refs",
    "notes",
]

QUALITY_HEADINGS = [
    "# Quality Report: ",
    "## 1. Summary",
    "## 2. Input Coverage",
    "## 3. Asset Resolution",
    "## 4. Sectionization Quality",
    "## 5. Image Reading Quality",
    "## 6. Mechanical Rule Quality",
    "## 7. TSIS Translation Quality",
    "## 8. Open Questions",
    "## 9. Blocking Issues",
    "## 10. Acceptance Decision",
]

ALLOWED_STATUS = {
    "not_started",
    "inventory_only",
    "assets_resolved",
    "sectionized",
    "images_read",
    "rules_extracted",
    "translated",
    "reviewed",
    "blocked",
}

ALLOWED_IMAGE_STATUS = {
    "resolved_direct",
    "resolved_lesson_fallback",
    "external_reference",
    "missing",
    "duplicate_reference",
    "not_required_duplicate",
    "needs_human_review",
}

ALLOWED_VISUAL_TYPES = {
    "optimization_map",
    "excel_parameter_grid",
    "fitness_summary",
    "performance_report",
    "equity_curve",
    "drawdown_curve",
    "portfolio_report",
    "platform_settings",
    "code_screenshot",
    "trade_example",
    "execution_anomaly",
    "concept_diagram",
    "ui_navigation",
    "unknown",
}

ALLOWED_DOMAINS = {
    "data_semantics",
    "price_view",
    "bar_construction",
    "setup_logic",
    "entry_logic",
    "exit_logic",
    "stop_loss",
    "take_profit",
    "filters",
    "optimization",
    "overfitting",
    "robustness",
    "BRaC",
    "walk_forward",
    "IS_OOS",
    "sample_size",
    "trade_distribution",
    "execution_realism",
    "commissions_slippage",
    "halts",
    "money_management",
    "position_sizing",
    "portfolio",
    "correlation",
    "regime",
    "market_microstructure",
    "small_caps_transfer",
    "AlphaEvolve_constraints",
    "other",
}

ALLOWED_RULE_TYPES = {"hard_rule", "soft_rule", "warning", "heuristic", "open_question"}
ALLOWED_PROMOTION = {
    "source_observation",
    "interpreted_claim",
    "mechanical_rule_candidate",
    "tsis_translation_candidate",
    "reviewed_doctrine_candidate",
    "promoted",
    "rejected",
}
ALLOWED_CONFIDENCE = {"low", "medium", "high", "requires_human_review"}
ALLOWED_TARGETS = {
    "strategy_evaluator",
    "backtest_checklist",
    "data_quality_gate",
    "feature_leakage_check",
    "execution_realism_check",
    "portfolio_evaluator",
    "money_management_policy",
    "AlphaEvolve_constraint",
    "human_review_checklist",
    "research_protocol",
    "do_not_promote_rule",
    "documentation_only",
    "open_question",
}
ALLOWED_ACTIONS = {"require", "warn", "block", "score", "document", "review"}
ALLOWED_PRIORITY = {"low", "medium", "high", "critical"}
ALLOWED_BLOCKING = {"none", "soft_gate", "hard_gate", "human_review_gate"}
ALLOWED_RUN_STATUS = {"pass", "pass_with_warnings", "needs_human_review", "fail", "blocked"}

PROJECT_ROOT = None
SCRIPT_PATH = Path(__file__).resolve()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def find_project_root() -> Path:
    current = SCRIPT_PATH
    for parent in [current, *current.parents]:
        if (parent / "PROJECT_RULES.md").exists() and (parent / "AGENTS.md").exists():
            return parent
    raise RuntimeError("Unable to locate TSIS project root")


def project_root() -> Path:
    global PROJECT_ROOT
    if PROJECT_ROOT is None:
        PROJECT_ROOT = find_project_root()
    return PROJECT_ROOT


def rel_project(path: Path) -> str:
    return path.resolve().relative_to(project_root().resolve()).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, payload: Any) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def harness_paths() -> dict[str, Path]:
    root = project_root()
    harness = root / "00_CTO" / "12_TSIS_COGNITIVE_ARCHITECTURE" / "20_SERSAN_DISTILLATION_HARNESS"
    return {
        "root": root,
        "harness": harness,
        "artifact_root": harness / "sersan_distillation_artifacts",
        "inventory_csv": harness / "sersan_distillation_artifacts" / "_corpus_inventory" / "sersan_corpus_manifest.csv",
    }


def load_inventory() -> list[dict[str, str]]:
    with harness_paths()["inventory_csv"].open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def prohibited_path(value: str) -> bool:
    normalized = value.lower().replace("/", "\\")
    return (
        normalized.startswith("c:\\users\\")
        or normalized.startswith("c:\\tmp\\")
        or "\\downloads\\" in normalized
        or "\\appdata\\local\\temp\\" in normalized
    )


def project_path(value: str) -> Path:
    return (project_root() / value.replace("/", "\\")).resolve()


def validate_manifest(lesson_dir: Path, lesson_id: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    path = lesson_dir / "lesson_pack_manifest.json"
    if not path.exists():
        errors.append(f"{lesson_id}: missing lesson_pack_manifest.json")
        return {}
    try:
        manifest = json.loads(read_text(path))
    except Exception as exc:
        errors.append(f"{lesson_id}: manifest JSON parse failed: {exc}")
        return {}
    required = [
        "contract_version",
        "generated_at_utc",
        "generated_by",
        "lesson_id",
        "practice_number",
        "title",
        "status",
        "source_md",
        "workshop_dir",
        "image_dir",
        "asset_resolution",
        "source_hashes",
        "counts",
        "known_issues",
    ]
    for field in required:
        if field not in manifest:
            errors.append(f"{lesson_id}: manifest missing field {field}")
    if manifest.get("contract_version") != "sersan_lesson_pack_contract_v0_1":
        errors.append(f"{lesson_id}: invalid manifest contract_version")
    if manifest.get("lesson_id") != lesson_id:
        errors.append(f"{lesson_id}: manifest lesson_id mismatch")
    if manifest.get("status") not in ALLOWED_STATUS:
        errors.append(f"{lesson_id}: invalid manifest status {manifest.get('status')}")
    if manifest.get("status") == "blocked":
        warnings.append(f"{lesson_id}: lesson is locally blocked")
    return manifest


def validate_sections(lesson_dir: Path, lesson_id: str, errors: list[str]) -> list[dict[str, Any]]:
    path = lesson_dir / "lesson_sections.jsonl"
    if not path.exists():
        errors.append(f"{lesson_id}: missing lesson_sections.jsonl")
        return []
    sections: list[dict[str, Any]] = []
    seen: set[str] = set()
    previous_end = 0
    for line_no, line in enumerate(read_text(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except Exception as exc:
            errors.append(f"{lesson_id}: section JSONL line {line_no} parse failed: {exc}")
            continue
        sid = record.get("section_id")
        if not sid:
            errors.append(f"{lesson_id}: section line {line_no} missing section_id")
        elif sid in seen:
            errors.append(f"{lesson_id}: duplicate section_id {sid}")
        else:
            seen.add(sid)
        if record.get("lesson_id") != lesson_id:
            errors.append(f"{lesson_id}: section {sid} lesson_id mismatch")
        if record.get("contract_version") != "sersan_lesson_sections_v0_1":
            errors.append(f"{lesson_id}: section {sid} invalid contract_version")
        if record.get("line_start", 0) < 1 or record.get("line_end", 0) < record.get("line_start", 0):
            errors.append(f"{lesson_id}: section {sid} invalid line range")
        if record.get("line_start", 0) < previous_end:
            errors.append(f"{lesson_id}: section {sid} overlaps previous section")
        previous_end = max(previous_end, int(record.get("line_end", 0)))
        sections.append(record)
    return sections


def validate_images(lesson_dir: Path, lesson_id: str, section_ids: set[str], errors: list[str], warnings: list[str]) -> list[dict[str, str]]:
    path = lesson_dir / "image_evidence_index.csv"
    if not path.exists():
        errors.append(f"{lesson_id}: missing image_evidence_index.csv")
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != IMAGE_CSV_HEADER:
            errors.append(f"{lesson_id}: image CSV header mismatch")
            return []
        rows = list(reader)
    seen: set[str] = set()
    for row in rows:
        image_id = row["image_id"]
        if image_id in seen:
            errors.append(f"{lesson_id}: duplicate image_id {image_id}")
        seen.add(image_id)
        if row["lesson_id"] != lesson_id:
            errors.append(f"{lesson_id}: image {image_id} lesson_id mismatch")
        if row["resolution_status"] not in ALLOWED_IMAGE_STATUS:
            errors.append(f"{lesson_id}: image {image_id} invalid resolution_status")
        if row["visual_type"] not in ALLOWED_VISUAL_TYPES:
            errors.append(f"{lesson_id}: image {image_id} invalid visual_type")
        if row["resolution_status"] in {"resolved_direct", "resolved_lesson_fallback"}:
            if not row["resolved_path"]:
                errors.append(f"{lesson_id}: image {image_id} has empty resolved_path")
            elif not project_path(row["resolved_path"]).exists():
                errors.append(f"{lesson_id}: image {image_id} resolved_path does not exist: {row['resolved_path']}")
        for section_id in filter(None, row["referenced_from_section_ids"].split("|")):
            if section_id not in section_ids:
                errors.append(f"{lesson_id}: image {image_id} references missing section {section_id}")
        note_ref = row["technical_reading_ref"]
        if note_ref and not (lesson_dir / note_ref).exists():
            errors.append(f"{lesson_id}: image {image_id} note missing: {note_ref}")
        if row["doctrine_relevance"] in {"medium", "high", "critical"} and not note_ref:
            errors.append(f"{lesson_id}: image {image_id} medium+ relevance without note")
        if row["resolution_status"] == "missing":
            warnings.append(f"{lesson_id}: image {image_id} missing")
    return rows


def validate_rules(lesson_dir: Path, lesson_id: str, section_ids: set[str], image_ids: set[str], errors: list[str]) -> list[dict[str, Any]]:
    path = lesson_dir / "mechanical_rules.yaml"
    if not path.exists():
        errors.append(f"{lesson_id}: missing mechanical_rules.yaml")
        return []
    try:
        payload = yaml.safe_load(read_text(path)) or {}
    except Exception as exc:
        errors.append(f"{lesson_id}: mechanical_rules.yaml parse failed: {exc}")
        return []
    if payload.get("contract_version") != "sersan_mechanical_rules_v0_1":
        errors.append(f"{lesson_id}: mechanical rules invalid contract_version")
    if payload.get("lesson_id") != lesson_id:
        errors.append(f"{lesson_id}: mechanical rules lesson_id mismatch")
    rules = payload.get("rules", [])
    if not isinstance(rules, list):
        errors.append(f"{lesson_id}: rules is not a list")
        return []
    seen: set[str] = set()
    required = [
        "rule_id",
        "promotion_state",
        "confidence",
        "rule_type",
        "domains",
        "statement",
        "trigger",
        "action",
        "failure_mode_if_ignored",
        "required_evidence",
        "source_anchors",
        "caveats",
        "related_rules",
    ]
    for rule in rules:
        rid = rule.get("rule_id")
        if not rid:
            errors.append(f"{lesson_id}: rule missing rule_id")
            continue
        if rid in seen:
            errors.append(f"{lesson_id}: duplicate rule_id {rid}")
        seen.add(rid)
        for field in required:
            if field not in rule:
                errors.append(f"{lesson_id}: rule {rid} missing {field}")
        if rule.get("promotion_state") not in ALLOWED_PROMOTION:
            errors.append(f"{lesson_id}: rule {rid} invalid promotion_state")
        if rule.get("promotion_state") == "promoted":
            errors.append(f"{lesson_id}: rule {rid} illegally promoted")
        if rule.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"{lesson_id}: rule {rid} invalid confidence")
        if rule.get("rule_type") not in ALLOWED_RULE_TYPES:
            errors.append(f"{lesson_id}: rule {rid} invalid rule_type")
        domains = rule.get("domains", [])
        if not isinstance(domains, list) or not domains:
            errors.append(f"{lesson_id}: rule {rid} must have domains")
        for domain in domains:
            if domain not in ALLOWED_DOMAINS:
                errors.append(f"{lesson_id}: rule {rid} invalid domain {domain}")
        if not rule.get("trigger"):
            errors.append(f"{lesson_id}: rule {rid} empty trigger")
        if not rule.get("failure_mode_if_ignored"):
            errors.append(f"{lesson_id}: rule {rid} empty failure mode")
        anchors = rule.get("source_anchors", [])
        if not anchors:
            errors.append(f"{lesson_id}: rule {rid} missing source anchors")
        for anchor in anchors:
            if anchor.get("lesson_id") != lesson_id:
                errors.append(f"{lesson_id}: rule {rid} anchor lesson mismatch")
            if anchor.get("section_id") not in section_ids:
                errors.append(f"{lesson_id}: rule {rid} anchor missing section {anchor.get('section_id')}")
            for image_id in anchor.get("image_ids", []):
                if image_id not in image_ids:
                    errors.append(f"{lesson_id}: rule {rid} anchor missing image {image_id}")
    return rules


def validate_translations(lesson_dir: Path, lesson_id: str, rule_ids: set[str], errors: list[str]) -> list[dict[str, str]]:
    path = lesson_dir / "tsis_translation_map.csv"
    if not path.exists():
        errors.append(f"{lesson_id}: missing tsis_translation_map.csv")
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != TRANSLATION_CSV_HEADER:
            errors.append(f"{lesson_id}: translation CSV header mismatch")
            return []
        rows = list(reader)
    seen: set[str] = set()
    high_risk_domains = {"overfitting", "leakage", "data quality", "execution realism", "money management"}
    for row in rows:
        tid = row["translation_id"]
        if tid in seen:
            errors.append(f"{lesson_id}: duplicate translation_id {tid}")
        seen.add(tid)
        if row["lesson_id"] != lesson_id:
            errors.append(f"{lesson_id}: translation {tid} lesson_id mismatch")
        if row["rule_id"] not in rule_ids:
            errors.append(f"{lesson_id}: translation {tid} references missing rule {row['rule_id']}")
        if row["target"] not in ALLOWED_TARGETS:
            errors.append(f"{lesson_id}: translation {tid} invalid target {row['target']}")
        if row["action_type"] not in ALLOWED_ACTIONS:
            errors.append(f"{lesson_id}: translation {tid} invalid action_type {row['action_type']}")
        if row["priority"] not in ALLOWED_PRIORITY:
            errors.append(f"{lesson_id}: translation {tid} invalid priority {row['priority']}")
        if row["blocking_power"] not in ALLOWED_BLOCKING:
            errors.append(f"{lesson_id}: translation {tid} invalid blocking_power {row['blocking_power']}")
        if row["priority"] == "critical" and row["requires_human_review"] != "true":
            errors.append(f"{lesson_id}: critical translation {tid} must require human review")
        scope = row["consumer_scope"]
        risk_text = " ".join([row["target"], row["tsis_artifact_candidate"], row["implementation_hint"], row["notes"]]).lower()
        if "AlphaEvolve" in scope and row["blocking_power"] == "none" and any(term in risk_text for term in high_risk_domains):
            errors.append(f"{lesson_id}: AlphaEvolve high-risk translation {tid} has no gate")
        if len(row["implementation_hint"].strip()) < 20:
            errors.append(f"{lesson_id}: translation {tid} implementation_hint too short")
    return rows


def validate_quality_report(lesson_dir: Path, lesson_id: str, errors: list[str]) -> str:
    path = lesson_dir / "quality_report.md"
    if not path.exists():
        errors.append(f"{lesson_id}: missing quality_report.md")
        return ""
    text = read_text(path)
    for heading in QUALITY_HEADINGS:
        if heading not in text:
            errors.append(f"{lesson_id}: quality_report missing heading {heading}")
    match = re.search(r"Acceptance decision:\s*`([^`]+)`", text)
    decision = match.group(1) if match else ""
    if decision not in {"pass", "pass_with_warnings", "needs_human_review", "fail"}:
        errors.append(f"{lesson_id}: invalid or missing quality acceptance decision")
    return decision


def validate_run_manifest(lesson_dir: Path, lesson_id: str, errors: list[str]) -> dict[str, Any]:
    path = lesson_dir / "run_manifest.json"
    if not path.exists():
        errors.append(f"{lesson_id}: missing run_manifest.json")
        return {}
    try:
        manifest = json.loads(read_text(path))
    except Exception as exc:
        errors.append(f"{lesson_id}: run_manifest JSON parse failed: {exc}")
        return {}
    required = [
        "run_id",
        "mode",
        "status",
        "contract_version",
        "toolchain_traceability_contract",
        "execution_command",
        "toolchain_artifacts",
        "input_artifacts",
        "output_artifacts",
        "non_project_artifacts_used",
        "known_limitations",
        "acceptance_decision",
    ]
    for field in required:
        if field not in manifest:
            errors.append(f"{lesson_id}: run_manifest missing {field}")
    if manifest.get("status") not in ALLOWED_RUN_STATUS:
        errors.append(f"{lesson_id}: invalid run_manifest status {manifest.get('status')}")
    for tool in manifest.get("toolchain_artifacts", []):
        rel = tool.get("project_relative_path", "")
        if not rel or prohibited_path(rel):
            errors.append(f"{lesson_id}: invalid toolchain path {rel}")
            continue
        path_obj = project_path(rel)
        if not path_obj.exists():
            errors.append(f"{lesson_id}: toolchain artifact missing {rel}")
            continue
        if tool.get("sha256") != sha256_file(path_obj):
            errors.append(f"{lesson_id}: toolchain hash mismatch {rel}")
        if not tool.get("project_resident"):
            errors.append(f"{lesson_id}: toolchain artifact not marked project_resident {rel}")
    for output in manifest.get("output_artifacts", []):
        rel = output.get("path", "")
        if not rel:
            errors.append(f"{lesson_id}: empty output artifact path")
            continue
        path_obj = project_path(rel)
        if not path_obj.exists():
            errors.append(f"{lesson_id}: output artifact missing {rel}")
            continue
        if output.get("sha256") != sha256_file(path_obj):
            errors.append(f"{lesson_id}: output hash mismatch {rel}")
    if manifest.get("non_project_artifacts_used"):
        errors.append(f"{lesson_id}: non_project_artifacts_used must be empty")
    return manifest


def validate_lesson(row: dict[str, str]) -> dict[str, Any]:
    paths = harness_paths()
    lesson_id = row["lesson_id"]
    lesson_dir = paths["artifact_root"] / lesson_id
    errors: list[str] = []
    warnings: list[str] = []
    if not lesson_dir.exists():
        return {"lesson_id": lesson_id, "status": "fail", "errors": [f"{lesson_id}: missing lesson directory"], "warnings": []}
    manifest = validate_manifest(lesson_dir, lesson_id, errors, warnings)
    sections = validate_sections(lesson_dir, lesson_id, errors)
    section_ids = {section.get("section_id", "") for section in sections}
    images = validate_images(lesson_dir, lesson_id, section_ids, errors, warnings)
    image_ids = {row["image_id"] for row in images}
    rules = validate_rules(lesson_dir, lesson_id, section_ids, image_ids, errors)
    rule_ids = {rule.get("rule_id", "") for rule in rules}
    translations = validate_translations(lesson_dir, lesson_id, rule_ids, errors)
    decision = validate_quality_report(lesson_dir, lesson_id, errors)
    run_manifest = validate_run_manifest(lesson_dir, lesson_id, errors)
    if manifest:
        counts = manifest.get("counts", {})
        if counts.get("sections") != len(sections):
            errors.append(f"{lesson_id}: manifest section count mismatch")
        if counts.get("images") != len(images):
            errors.append(f"{lesson_id}: manifest image count mismatch")
        if counts.get("rules") != len(rules):
            errors.append(f"{lesson_id}: manifest rule count mismatch")
        if counts.get("translations") != len(translations):
            errors.append(f"{lesson_id}: manifest translation count mismatch")
    if decision == "pass" and warnings:
        errors.append(f"{lesson_id}: quality report cannot be pass with validator warnings")
    status = "fail" if errors else (run_manifest.get("status") or decision or "pass")
    return {
        "lesson_id": lesson_id,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "sections": len(sections),
        "images": len(images),
        "rules": len(rules),
        "translations": len(translations),
    }


def write_validation_report(results: list[dict[str, Any]]) -> None:
    paths = harness_paths()
    artifact_root = paths["artifact_root"]
    total_errors = sum(len(result["errors"]) for result in results)
    total_warnings = sum(len(result["warnings"]) for result in results)
    payload = {
        "generated_at_utc": utc_now(),
        "status": "fail" if total_errors else ("pass_with_warnings" if total_warnings else "pass"),
        "lesson_packs_validated": len(results),
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "results": results,
    }
    write_json(artifact_root / "_corpus_validation_summary.json", payload)
    lines = [
        "# Sersan Corpus Validation Report",
        "",
        f"Generated at UTC: `{payload['generated_at_utc']}`",
        f"Status: `{payload['status']}`",
        f"Lesson packs validated: `{payload['lesson_packs_validated']}`",
        f"Total errors: `{total_errors}`",
        f"Total warnings: `{total_warnings}`",
        "",
        "## Lesson Results",
        "",
        "| lesson_id | status | errors | warnings | sections | images | rules | translations |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        lines.append(
            f"| `{result['lesson_id']}` | `{result['status']}` | {len(result['errors'])} | {len(result['warnings'])} | {result.get('sections', 0)} | {result.get('images', 0)} | {result.get('rules', 0)} | {result.get('translations', 0)} |"
        )
    if total_errors:
        lines.extend(["", "## Errors", ""])
        for result in results:
            for error in result["errors"]:
                lines.append(f"- {error}")
    if total_warnings:
        lines.extend(["", "## Warnings", ""])
        for result in results:
            for warning in result["warnings"]:
                lines.append(f"- {warning}")
    write_text(artifact_root / "_corpus_validation_report.md", "\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Sersan corpus distillation artifacts.")
    parser.add_argument("--write-report", action="store_true", help="Write corpus validation report artifacts.")
    args = parser.parse_args()
    rows = load_inventory()
    results = [validate_lesson(row) for row in rows]
    if args.write_report:
        write_validation_report(results)
    total_errors = sum(len(result["errors"]) for result in results)
    total_warnings = sum(len(result["warnings"]) for result in results)
    print(
        json.dumps(
            {
                "status": "fail" if total_errors else ("pass_with_warnings" if total_warnings else "pass"),
                "lesson_packs_validated": len(results),
                "total_errors": total_errors,
                "total_warnings": total_warnings,
            },
            indent=2,
        )
    )
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
