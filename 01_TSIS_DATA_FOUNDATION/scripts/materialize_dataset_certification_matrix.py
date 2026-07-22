from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_ID = "dataset_certification_matrix_v0_1"
SCHEMA_VERSION = "dataset_certification_matrix_v0_1"
QUALITY_POLICY_VERSION = "dataset_certification_matrix_policy_v0_1"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FOUNDATIONS_ROOT = PROJECT_ROOT / "01_foundations"

DEFAULT_FAMILY_STATUS_MATRIX = FOUNDATIONS_ROOT / "data_quality_report" / "family_status_matrix_v0_1.md"
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix")


SCHEMA_PATHS: dict[str, list[str]] = {
    "additional": [
        "01_foundations/canonical_schemas/additional/additional_corporate_actions_schema_contract.md",
        "01_foundations/canonical_schemas/additional/additional_economic_schema_contract.md",
        "01_foundations/canonical_schemas/additional/additional_financials_schema_contract.md",
        "01_foundations/canonical_schemas/additional/additional_ipos_schema_contract.md",
        "01_foundations/canonical_schemas/additional/additional_news_schema_contract.md",
    ],
    "daily": ["01_foundations/canonical_schemas/daily/daily_schema_contract.md"],
    "financial": [
        "01_foundations/canonical_schemas/financial/balance_sheets_schema_contract.md",
        "01_foundations/canonical_schemas/financial/cash_flow_statements_schema_contract.md",
        "01_foundations/canonical_schemas/financial/income_statements_schema_contract.md",
        "01_foundations/canonical_schemas/financial/operational_audit_schema_contract.md",
        "01_foundations/canonical_schemas/financial/operational_run_schema_contract.md",
        "01_foundations/canonical_schemas/financial/ratios_schema_contract.md",
    ],
    "halts": [
        "01_foundations/canonical_schemas/halts/halts_master_multisource_schema_contract.md",
        "01_foundations/canonical_schemas/halts/halts_operational_summary_schema_contract.md",
        "01_foundations/canonical_schemas/halts/halts_raw_sources_schema_contract.md",
        "01_foundations/canonical_schemas/halts/halts_source_specific_outputs_schema_contract.md",
        "01_foundations/canonical_schemas/halts/halts_universe_coverage_schema_contract.md",
    ],
    "intraday_regime_features": [
        "01_foundations/canonical_schemas/features/intraday_regime_features_schema_contract.md",
    ],
    "ohlcv_1m_raw": ["01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_schema_contract.md"],
    "ohlcv_1m_split_normalized": [
        "01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md",
    ],
    "ohlcv_daily_adjusted": ["01_foundations/canonical_schemas/daily/daily_adjusted_schema_contract.md"],
    "quotes": ["01_foundations/canonical_schemas/quotes/quotes_schema_contract.md"],
    "reference": [
        "01_foundations/canonical_schemas/reference/all_tickers_snapshot_schema_contract.md",
        "01_foundations/canonical_schemas/reference/dividends_schema_contract.md",
        "01_foundations/canonical_schemas/reference/events_schema_contract.md",
        "01_foundations/canonical_schemas/reference/exchanges_schema_contract.md",
        "01_foundations/canonical_schemas/reference/operational_run_schema_contract.md",
        "01_foundations/canonical_schemas/reference/overview_schema_contract.md",
        "01_foundations/canonical_schemas/reference/splits_schema_contract.md",
        "01_foundations/canonical_schemas/reference/ticker_types_schema_contract.md",
    ],
    "regime_indicators": [
        "01_foundations/canonical_schemas/regime_indicators/regime_etf_bars_schema_contract.md",
        "01_foundations/canonical_schemas/regime_indicators/regime_index_bars_schema_contract.md",
        "01_foundations/canonical_schemas/regime_indicators/regime_metadata_schema_contract.md",
    ],
    "short_review": [
        "01_foundations/canonical_schemas/short_review/finra_short_interest_schema_contract.md",
        "01_foundations/canonical_schemas/short_review/finra_short_provenance_schema_contract.md",
        "01_foundations/canonical_schemas/short_review/finra_short_volume_schema_contract.md",
    ],
    "trades": ["01_foundations/canonical_schemas/trades/trades_schema_contract.md"],
}

DATASET_CONTRACTS: dict[str, str] = {
    "additional": "01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md",
    "daily": "01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md",
    "financial": "01_foundations/contract_registry/dataset_contracts/financial_dataset_contract_v0_1.md",
    "halts": "01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md",
    "intraday_regime_features": (
        "01_foundations/contract_registry/dataset_contracts/"
        "intraday_regime_features_dataset_contract_v0_1.md"
    ),
    "ohlcv_1m_raw": "01_foundations/contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md",
    "ohlcv_1m_split_normalized": (
        "01_foundations/contract_registry/dataset_contracts/"
        "ohlcv_1m_split_normalized_dataset_contract_v0_1.md"
    ),
    "ohlcv_daily_adjusted": "01_foundations/contract_registry/dataset_contracts/daily_adjusted_dataset_contract_v0_1.md",
    "quotes": "01_foundations/contract_registry/dataset_contracts/quotes_dataset_contract_v0_1.md",
    "reference": "01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md",
    "regime_indicators": "01_foundations/contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md",
    "short_review": "01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md",
    "trades": "01_foundations/contract_registry/dataset_contracts/trades_dataset_contract_v0_1.md",
}

REGISTRY_ENTRIES: dict[str, str] = {
    "additional": "01_foundations/dataset_registry/additional/additional_registry_entry.yaml",
    "daily": "01_foundations/dataset_registry/daily/daily_registry_entry.yaml",
    "financial": "01_foundations/dataset_registry/financial/financial_registry_entry.yaml",
    "halts": "01_foundations/dataset_registry/halts/halts_registry_entry.yaml",
    "intraday_regime_features": (
        "01_foundations/dataset_registry/features/intraday_regime_features_registry_entry.yaml"
    ),
    "ohlcv_1m_raw": "01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml",
    "ohlcv_1m_split_normalized": (
        "01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml"
    ),
    "ohlcv_daily_adjusted": "01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml",
    "quotes": "01_foundations/dataset_registry/quotes/quotes_registry_entry.yaml",
    "reference": "01_foundations/dataset_registry/reference/reference_registry_entry.yaml",
    "regime_indicators": "01_foundations/dataset_registry/regime_indicators/regime_indicators_registry_entry.yaml",
    "short_review": "01_foundations/dataset_registry/short_review/short_review_registry_entry.yaml",
    "trades": "01_foundations/dataset_registry/trades/trades_registry_entry.yaml",
}

POLICIES: dict[str, str] = {
    "additional": "01_foundations/data_consumption_policies/additional_consumption_policy.md",
    "daily": "01_foundations/data_consumption_policies/daily_consumption_policy.md",
    "financial": "01_foundations/data_consumption_policies/financial_consumption_policy.md",
    "halts": "01_foundations/data_consumption_policies/halts_consumption_policy.md",
    "intraday_regime_features": "01_foundations/data_consumption_policies/intraday_regime_features_consumption_policy.md",
    "ohlcv_1m_raw": "01_foundations/data_consumption_policies/ohlcv_1m_raw_consumption_policy.md",
    "ohlcv_1m_split_normalized": "01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md",
    "ohlcv_daily_adjusted": "01_foundations/data_consumption_policies/daily_adjusted_consumption_policy.md",
    "quotes": "01_foundations/data_consumption_policies/quotes_consumption_policy.md",
    "reference": "01_foundations/data_consumption_policies/reference_consumption_policy.md",
    "regime_indicators": "01_foundations/data_consumption_policies/regime_indicators_consumption_policy.md",
    "short_review": "01_foundations/data_consumption_policies/short_review_consumption_policy.md",
    "trades": "01_foundations/data_consumption_policies/trades_consumption_policy.md",
}

VALIDATORS: dict[str, str] = {
    "additional": "01_foundations/validators/additional/additional_validators.md",
    "daily": "01_foundations/validators/daily/daily_validators.md",
    "financial": "01_foundations/validators/financial/financial_validators.md",
    "halts": "01_foundations/validators/halts/halts_validators.md",
    "intraday_regime_features": (
        "01_foundations/validators/intraday_regime_features/intraday_regime_features_validators.md"
    ),
    "ohlcv_1m_raw": "01_foundations/validators/ohlcv_1m/ohlcv_1m_raw_validators.md",
    "ohlcv_1m_split_normalized": "01_foundations/validators/ohlcv_1m/ohlcv_1m_split_normalized_validators.md",
    "ohlcv_daily_adjusted": "01_foundations/validators/daily/daily_adjusted_validators.md",
    "quotes": "01_foundations/validators/quotes/quotes_validators.md",
    "reference": "01_foundations/validators/reference/reference_validators.md",
    "regime_indicators": "01_foundations/validators/regime_indicators/regime_indicators_validators.md",
    "short_review": "01_foundations/validators/short_review/short_review_validators.md",
    "trades": "01_foundations/validators/trades/trades_validators.md",
}

QUALITY_REPORTS: dict[str, str] = {
    "additional": "01_foundations/data_quality_report/families/additional_quality_report_v0_1.md",
    "daily": "01_foundations/data_quality_report/families/daily_quality_report_v0_1.md",
    "financial": "01_foundations/data_quality_report/families/financial_quality_report_v0_1.md",
    "halts": "01_foundations/data_quality_report/families/halts_quality_report_v0_1.md",
    "intraday_regime_features": (
        "01_foundations/data_quality_report/families/intraday_regime_features_quality_report_v0_1.md"
    ),
    "ohlcv_1m_raw": "01_foundations/data_quality_report/families/ohlcv_1m_raw_quality_report_v0_1.md",
    "ohlcv_1m_split_normalized": (
        "01_foundations/data_quality_report/families/ohlcv_1m_split_normalized_quality_report_v0_1.md"
    ),
    "ohlcv_daily_adjusted": "01_foundations/data_quality_report/families/daily_adjusted_quality_report_v0_1.md",
    "quotes": "01_foundations/data_quality_report/families/quotes_quality_report_v0_1.md",
    "reference": "01_foundations/data_quality_report/families/reference_quality_report_v0_1.md",
    "regime_indicators": "01_foundations/data_quality_report/families/regime_indicators_quality_report_v0_1.md",
    "short_review": "01_foundations/data_quality_report/families/short_review_quality_report_v0_1.md",
    "trades": "01_foundations/data_quality_report/families/trades_quality_report_v0_1.md",
}

DOSSIER_ROOTS: dict[str, str] = {
    "additional": "01_foundations/inspection_dossiers/additional",
    "daily": "01_foundations/inspection_dossiers/daily",
    "financial": "01_foundations/inspection_dossiers/financial",
    "halts": "01_foundations/inspection_dossiers/halts",
    "intraday_regime_features": "01_foundations/inspection_dossiers/intraday_regime_features",
    "ohlcv_1m_raw": "01_foundations/inspection_dossiers/minute",
    "ohlcv_1m_split_normalized": "01_foundations/inspection_dossiers/1m_split_normalized",
    "ohlcv_daily_adjusted": "01_foundations/inspection_dossiers/daily_adjusted",
    "quotes": "01_foundations/inspection_dossiers/quotes",
    "reference": "01_foundations/inspection_dossiers/reference",
    "regime_indicators": "01_foundations/inspection_dossiers/regime_indicators",
    "short_review": "01_foundations/inspection_dossiers/short_review",
    "trades": "01_foundations/inspection_dossiers/trades",
}


def _project_path(rel: str) -> Path:
    return PROJECT_ROOT / rel


def _sqlish_path(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _clean_cell(value: str) -> str:
    text = value.strip()
    if text.startswith("`") and text.endswith("`") and len(text) >= 2:
        text = text[1:-1]
    return text.replace("<br>", " ").strip()


def _canonical_family(label: str) -> str:
    cleaned = _clean_cell(label)
    if cleaned == "Halts":
        return "halts"
    return cleaned


def _parse_table(markdown: str, heading: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration as exc:
        raise ValueError(f"Missing heading: {heading}") from exc

    table_lines: list[str] = []
    for line in lines[start + 1 :]:
        if not table_lines and not line.startswith("|"):
            continue
        if table_lines and not line.startswith("|"):
            break
        if line.startswith("|"):
            table_lines.append(line)

    if len(table_lines) < 3:
        raise ValueError(f"Heading {heading} does not contain a markdown table")

    def split_row(line: str) -> list[str]:
        return [_clean_cell(cell) for cell in line.strip().strip("|").split("|")]

    headers = split_row(table_lines[0])
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cells = split_row(line)
        if len(cells) != len(headers):
            raise ValueError(f"Malformed row under {heading}: {line}")
        rows.append(dict(zip(headers, cells)))
    return rows


def _artifact_present(value: str) -> bool:
    return _clean_cell(value).lower().startswith("yes")


def _line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


def _count_files(root: Path, suffixes: tuple[str, ...]) -> int:
    if not root.exists():
        return 0
    return sum(1 for path in root.rglob("*") if path.is_file() and path.suffix.lower() in suffixes)


def _count_casepack_docs(root: Path) -> int:
    if not root.exists():
        return 0
    total = 0
    for path in root.rglob("*.md"):
        lowered = _sqlish_path(path).lower()
        if "case" in lowered or "evidence_pack" in lowered or "good_justification" in lowered:
            total += 1
    return total


def _find_visual_pack(root: Path) -> str:
    if not root.exists():
        return ""
    patterns = ["*visual*inspector*pack*.md", "*inspection_visual_dossier*.md", "*visual_overview*.md"]
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(sorted(root.rglob(pattern)))
    if not matches:
        return ""
    return matches[0].relative_to(PROJECT_ROOT).as_posix()


def _gate_from_verdict(verdict: str, completion_status: str) -> tuple[str, str, bool, bool]:
    if verdict == "blocked_by_data_defect":
        return "blocked_from_backtest_core", "forensic_or_repair_only", True, False
    if "scoped" in verdict or "scoped" in completion_status:
        return "scoped_only", "allowed_with_scope_flags", False, True
    return "declared_scope_allowed", "allowed_with_family_policy", False, False


def _json_array(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=True, separators=(",", ":"))


def materialize_dataset_certification_matrix(
    family_status_matrix: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    if not family_status_matrix.exists():
        raise FileNotFoundError(f"Missing family status matrix: {family_status_matrix}")

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "dataset_certification_matrix_v0_1.parquet"
    summary_path = output_root / "_dataset_certification_matrix_summary_v0_1.csv"
    manifest_path = output_root / "_dataset_certification_matrix_manifest_v0_1.json"
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists. Pass --overwrite to replace: {output_path}")

    markdown = family_status_matrix.read_text(encoding="utf-8")
    summary_rows = _parse_table(markdown, "## Summary Table")
    artifact_rows = {
        _canonical_family(row["Family"]): row for row in _parse_table(markdown, "## Artifact Presence Matrix")
    }
    build_run_id = datetime.now(timezone.utc).strftime("dataset_certification_matrix_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()
    source_matrix_rel = family_status_matrix.relative_to(PROJECT_ROOT).as_posix()
    source_matrix_sha256 = _sha256(family_status_matrix)

    rows: list[dict[str, Any]] = []
    for source_row in summary_rows:
        family_label = _clean_cell(source_row["Family"])
        family = _canonical_family(family_label)
        if family not in DOSSIER_ROOTS:
            raise KeyError(f"Missing route config for family: {family}")

        artifact_row = artifact_rows.get(family)
        if artifact_row is None:
            raise KeyError(f"Missing artifact matrix row for family: {family}")

        schema_paths = SCHEMA_PATHS[family]
        dataset_contract_path = DATASET_CONTRACTS[family]
        registry_entry_path = REGISTRY_ENTRIES[family]
        policy_path = POLICIES[family]
        validator_path = VALIDATORS[family]
        quality_report_path = QUALITY_REPORTS[family]
        dossier_root_path = DOSSIER_ROOTS[family]

        schema_exists = [_project_path(path).exists() for path in schema_paths]
        quality_abs = _project_path(quality_report_path)
        dossier_abs = _project_path(dossier_root_path)
        physical_root = _clean_cell(source_row["Physical root"])
        production_gate, event_gate, blocked_from_core, scoped_only = _gate_from_verdict(
            _clean_cell(source_row["Data quality verdict"]),
            _clean_cell(source_row["Foundations completion status"]),
        )

        certification_id = hashlib.sha256(
            f"{family}|family_level|{SCHEMA_VERSION}|{source_matrix_sha256}".encode("utf-8")
        ).hexdigest()
        rows.append(
            {
                "certification_id": certification_id,
                "dataset_family": family,
                "source_matrix_family_label": family_label,
                "certification_scope": "family_level",
                "physical_root": physical_root,
                "physical_root_exists": Path(physical_root).exists(),
                "role": _clean_cell(source_row["Role"]),
                "data_quality_verdict": _clean_cell(source_row["Data quality verdict"]),
                "foundations_completion_status": _clean_cell(source_row["Foundations completion status"]),
                "visual_inspection_status": _clean_cell(source_row["Visual inspection status"]),
                "production_use_gate": production_gate,
                "event_consumption_gate": event_gate,
                "blocked_from_backtest_core": blocked_from_core,
                "scoped_only": scoped_only,
                "human_inspector_ready": _clean_cell(source_row["Foundations completion status"]).startswith(
                    "human_inspector_ready"
                ),
                "visual_casepack_complete": _clean_cell(source_row["Visual inspection status"]).startswith(
                    "visual_complete"
                ),
                "main_reading": _clean_cell(source_row["Main reading"]),
                "completion_gap_next_action": _clean_cell(source_row["Completion gap / next action"]),
                "source_matrix_path": source_matrix_rel,
                "source_matrix_sha256": source_matrix_sha256,
                "quality_report_path": quality_report_path,
                "quality_report_exists": quality_abs.exists(),
                "quality_report_line_count": _line_count(quality_abs),
                "inspection_dossier_root": dossier_root_path,
                "inspection_dossier_exists": dossier_abs.exists(),
                "inspection_markdown_count": _count_files(dossier_abs, (".md",)),
                "inspection_image_count": _count_files(dossier_abs, (".png", ".jpg", ".jpeg", ".webp", ".svg")),
                "casepack_markdown_count": _count_casepack_docs(dossier_abs),
                "visual_pack_path": _find_visual_pack(dossier_abs),
                "evidence_assets_present": (dossier_abs / "evidence_assets").exists(),
                "schema_contract_paths_json": _json_array(schema_paths),
                "schema_contract_count": len(schema_paths),
                "schema_contract_present": all(schema_exists),
                "missing_schema_contract_count": int(sum(1 for exists in schema_exists if not exists)),
                "dataset_contract_path": dataset_contract_path,
                "dataset_contract_present": _project_path(dataset_contract_path).exists(),
                "registry_entry_path": registry_entry_path,
                "registry_entry_present": _project_path(registry_entry_path).exists(),
                "consumption_policy_path": policy_path,
                "consumption_policy_present": _project_path(policy_path).exists(),
                "validator_path": validator_path,
                "validator_present": _project_path(validator_path).exists(),
                "artifact_matrix_physical": _clean_cell(artifact_row["Physical"]),
                "artifact_matrix_schema": _clean_cell(artifact_row["Schema"]),
                "artifact_matrix_contract": _clean_cell(artifact_row["Contract"]),
                "artifact_matrix_registry": _clean_cell(artifact_row["Registry"]),
                "artifact_matrix_policy": _clean_cell(artifact_row["Policy"]),
                "artifact_matrix_validators": _clean_cell(artifact_row["Validators"]),
                "artifact_matrix_dossier_readout": _clean_cell(artifact_row["Dossier/readout"]),
                "artifact_matrix_evidence_assets": _clean_cell(artifact_row["Evidence assets"]),
                "artifact_matrix_visual_inspector_pack": _clean_cell(artifact_row["Visual inspector pack"]),
                "technical_profile_report_state": _clean_cell(artifact_row["Technical-profile report"]),
                "artifact_matrix_schema_claims_present": _artifact_present(artifact_row["Schema"]),
                "artifact_matrix_contract_claims_present": _artifact_present(artifact_row["Contract"]),
                "artifact_matrix_registry_claims_present": _artifact_present(artifact_row["Registry"]),
                "artifact_matrix_policy_claims_present": _artifact_present(artifact_row["Policy"]),
                "artifact_matrix_validators_claims_present": _artifact_present(artifact_row["Validators"]),
                "artifact_matrix_dossier_claims_present": _artifact_present(artifact_row["Dossier/readout"]),
                "artifact_matrix_evidence_assets_claims_present": _artifact_present(artifact_row["Evidence assets"]),
                "artifact_matrix_visual_claims_present": _artifact_present(artifact_row["Visual inspector pack"]),
                "quality_policy_version": QUALITY_POLICY_VERSION,
                "build_run_id": build_run_id,
                "schema_version": SCHEMA_VERSION,
                "created_at_utc": created_at_utc,
            }
        )

    df = pd.DataFrame(rows).sort_values("dataset_family").reset_index(drop=True)
    duplicate_family_count = int(df["dataset_family"].duplicated().sum())
    missing_physical_root_count = int((~df["physical_root_exists"]).sum())
    missing_quality_report_count = int((~df["quality_report_exists"]).sum())
    missing_dossier_count = int((~df["inspection_dossier_exists"]).sum())
    missing_schema_count = int((~df["schema_contract_present"]).sum())
    missing_contract_count = int((~df["dataset_contract_present"]).sum())
    missing_registry_count = int((~df["registry_entry_present"]).sum())
    missing_policy_count = int((~df["consumption_policy_present"]).sum())
    missing_validator_count = int((~df["validator_present"]).sum())
    visual_without_images_count = int(
        (df["visual_casepack_complete"] & df["inspection_image_count"].eq(0)).sum()
    )
    artifact_claim_mismatch_count = int(
        (
            (df["artifact_matrix_schema_claims_present"] & ~df["schema_contract_present"])
            | (df["artifact_matrix_contract_claims_present"] & ~df["dataset_contract_present"])
            | (df["artifact_matrix_registry_claims_present"] & ~df["registry_entry_present"])
            | (df["artifact_matrix_policy_claims_present"] & ~df["consumption_policy_present"])
            | (df["artifact_matrix_validators_claims_present"] & ~df["validator_present"])
            | (df["artifact_matrix_dossier_claims_present"] & ~df["inspection_dossier_exists"])
            | (df["artifact_matrix_visual_claims_present"] & df["inspection_image_count"].eq(0))
        ).sum()
    )

    hard_fail_count = int(
        duplicate_family_count
        + missing_physical_root_count
        + missing_quality_report_count
        + missing_dossier_count
        + missing_schema_count
        + missing_contract_count
        + missing_registry_count
        + missing_policy_count
        + missing_validator_count
        + visual_without_images_count
        + artifact_claim_mismatch_count
        + (1 if len(df) != 13 else 0)
    )
    if hard_fail_count:
        raise RuntimeError(
            "Hard validation failed: "
            + json.dumps(
                {
                    "row_count": int(len(df)),
                    "duplicate_family_count": duplicate_family_count,
                    "missing_physical_root_count": missing_physical_root_count,
                    "missing_quality_report_count": missing_quality_report_count,
                    "missing_dossier_count": missing_dossier_count,
                    "missing_schema_count": missing_schema_count,
                    "missing_contract_count": missing_contract_count,
                    "missing_registry_count": missing_registry_count,
                    "missing_policy_count": missing_policy_count,
                    "missing_validator_count": missing_validator_count,
                    "visual_without_images_count": visual_without_images_count,
                    "artifact_claim_mismatch_count": artifact_claim_mismatch_count,
                    "hard_fail_count": hard_fail_count,
                },
                indent=2,
            )
        )

    df.to_parquet(output_path, index=False)
    validations: dict[str, Any] = {
        "row_count": int(len(df)),
        "family_count": int(df["dataset_family"].nunique()),
        "duplicate_family_count": duplicate_family_count,
        "missing_physical_root_count": missing_physical_root_count,
        "missing_quality_report_count": missing_quality_report_count,
        "missing_dossier_count": missing_dossier_count,
        "missing_schema_count": missing_schema_count,
        "missing_contract_count": missing_contract_count,
        "missing_registry_count": missing_registry_count,
        "missing_policy_count": missing_policy_count,
        "missing_validator_count": missing_validator_count,
        "visual_without_images_count": visual_without_images_count,
        "artifact_claim_mismatch_count": artifact_claim_mismatch_count,
        "human_inspector_ready_count": int(df["human_inspector_ready"].sum()),
        "visual_casepack_complete_count": int(df["visual_casepack_complete"].sum()),
        "blocked_from_backtest_core_count": int(df["blocked_from_backtest_core"].sum()),
        "scoped_only_count": int(df["scoped_only"].sum()),
        "data_quality_verdict_counts": {
            str(k): int(v) for k, v in df["data_quality_verdict"].value_counts().sort_index().items()
        },
        "foundations_completion_status_counts": {
            str(k): int(v) for k, v in df["foundations_completion_status"].value_counts().sort_index().items()
        },
        "visual_inspection_status_counts": {
            str(k): int(v) for k, v in df["visual_inspection_status"].value_counts().sort_index().items()
        },
        "hard_fail_count": hard_fail_count,
    }

    summary_records = [{"metric": key, "value": value} for key, value in validations.items() if not isinstance(value, dict)]
    for key, counts in validations.items():
        if isinstance(counts, dict):
            for subkey, value in counts.items():
                summary_records.append({"metric": f"{key}.{subkey}", "value": value})
    pd.DataFrame(summary_records).to_csv(summary_path, index=False)

    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": str(output_path),
        "summary_path": str(summary_path),
        "source_family_status_matrix": str(family_status_matrix),
        "source_family_status_matrix_sha256": source_matrix_sha256,
        "validations": validations,
        "contracts": {
            "dataset_contract": "01_foundations/contract_registry/dataset_contracts/dataset_certification_matrix_dataset_contract_v0_1.md",
            "schema_contract": "01_foundations/canonical_schemas/outputs/dataset_certification_matrix_schema_contract.md",
            "consumption_policy": "01_foundations/data_consumption_policies/dataset_certification_matrix_consumption_policy.md",
            "registry_entry": "01_foundations/dataset_registry/outputs/dataset_certification_matrix_registry_entry.yaml",
            "validators": "01_foundations/validators/outputs/dataset_certification_matrix_validators.md",
        },
    }
    manifest["output_sha256"] = _sha256(output_path)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa dataset_certification_matrix_v0_1.")
    ap.add_argument("--family-status-matrix", default=str(DEFAULT_FAMILY_STATUS_MATRIX))
    ap.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    materialize_dataset_certification_matrix(
        family_status_matrix=Path(args.family_status_matrix),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
