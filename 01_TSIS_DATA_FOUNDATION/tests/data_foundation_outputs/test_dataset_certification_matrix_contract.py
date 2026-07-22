from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from _helpers.data_foundation import (
    MODULE_ROOT,
    assert_relative_contract_paths_exist,
    load_json,
    non_empty_string_mask,
    sha256_file,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix")
OUTPUT_PATH = OUTPUT_ROOT / "dataset_certification_matrix_v0_1.parquet"
MANIFEST_PATH = OUTPUT_ROOT / "_dataset_certification_matrix_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_dataset_certification_matrix_summary_v0_1.csv"

EXPECTED_FAMILIES = {
    "additional",
    "daily",
    "financial",
    "halts",
    "intraday_regime_features",
    "ohlcv_1m_raw",
    "ohlcv_1m_split_normalized",
    "ohlcv_daily_adjusted",
    "quotes",
    "reference",
    "regime_indicators",
    "short_review",
    "trades",
}

REQUIRED_COLUMNS = {
    "certification_id",
    "dataset_family",
    "source_matrix_family_label",
    "certification_scope",
    "physical_root",
    "physical_root_exists",
    "role",
    "data_quality_verdict",
    "foundations_completion_status",
    "visual_inspection_status",
    "production_use_gate",
    "event_consumption_gate",
    "blocked_from_backtest_core",
    "scoped_only",
    "human_inspector_ready",
    "visual_casepack_complete",
    "main_reading",
    "completion_gap_next_action",
    "source_matrix_path",
    "source_matrix_sha256",
    "quality_report_path",
    "quality_report_exists",
    "quality_report_line_count",
    "inspection_dossier_root",
    "inspection_dossier_exists",
    "inspection_markdown_count",
    "inspection_image_count",
    "casepack_markdown_count",
    "visual_pack_path",
    "evidence_assets_present",
    "schema_contract_paths_json",
    "schema_contract_count",
    "schema_contract_present",
    "missing_schema_contract_count",
    "dataset_contract_path",
    "dataset_contract_present",
    "registry_entry_path",
    "registry_entry_present",
    "consumption_policy_path",
    "consumption_policy_present",
    "validator_path",
    "validator_present",
    "quality_policy_version",
    "build_run_id",
    "schema_version",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _frame() -> pd.DataFrame:
    return pd.read_parquet(OUTPUT_PATH)


def _source_summary_rows(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == "## Summary Table")
    table_lines: list[str] = []
    for line in lines[start + 1 :]:
        if not table_lines and not line.startswith("|"):
            continue
        if table_lines and not line.startswith("|"):
            break
        if line.startswith("|"):
            table_lines.append(line)

    def split(line: str) -> list[str]:
        return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]

    headers = split(table_lines[0])
    return [dict(zip(headers, split(line))) for line in table_lines[2:]]


def test_dataset_certification_matrix_manifest_hashes_and_contract_links(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()

    assert manifest["dataset_id"] == "dataset_certification_matrix_v0_1"
    assert manifest["schema_version"] == "dataset_certification_matrix_v0_1"
    assert manifest["quality_policy_version"] == "dataset_certification_matrix_policy_v0_1"
    assert OUTPUT_PATH.exists()
    assert SUMMARY_PATH.exists()
    assert Path(manifest["output_path"]) == OUTPUT_PATH
    assert Path(manifest["summary_path"]) == SUMMARY_PATH
    assert sha256_file(OUTPUT_PATH) == manifest["output_sha256"]
    assert sha256_file(Path(manifest["source_family_status_matrix"])) == manifest[
        "source_family_status_matrix_sha256"
    ]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "dataset_certification_matrix_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "output_path": manifest["output_path"],
            "output_sha256": manifest["output_sha256"],
            "source_family_status_matrix_sha256": manifest["source_family_status_matrix_sha256"],
            "validations": manifest["validations"],
        },
    )


def test_dataset_certification_matrix_schema_status_counts_and_lineage() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 13
    assert df["dataset_family"].nunique() == validations["family_count"] == 13
    assert set(df["dataset_family"]) == EXPECTED_FAMILIES
    assert df["dataset_family"].duplicated().sum() == validations["duplicate_family_count"] == 0
    assert set(df["schema_version"]) == {"dataset_certification_matrix_v0_1"}
    assert set(df["quality_policy_version"]) == {"dataset_certification_matrix_policy_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert set(df["source_matrix_sha256"]) == {manifest["source_family_status_matrix_sha256"]}
    assert non_empty_string_mask(df["certification_id"]).all()
    assert df["certification_id"].duplicated().sum() == 0

    assert validations["data_quality_verdict_counts"] == {
        "blocked_by_data_defect": 2,
        "complete_scoped": 5,
        "usable_for_declared_scope": 6,
    }
    assert validations["foundations_completion_status_counts"] == {
        "human_inspector_ready": 9,
        "human_inspector_ready_scoped": 4,
    }
    assert validations["visual_inspection_status_counts"] == {
        "visual_complete": 10,
        "visual_complete_scoped": 3,
    }
    assert validations["hard_fail_count"] == 0


def test_dataset_certification_matrix_evidence_links_are_real() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert df["physical_root_exists"].all()
    assert df["quality_report_exists"].all()
    assert df["inspection_dossier_exists"].all()
    assert df["schema_contract_present"].all()
    assert df["dataset_contract_present"].all()
    assert df["registry_entry_present"].all()
    assert df["consumption_policy_present"].all()
    assert df["validator_present"].all()
    assert df["missing_schema_contract_count"].sum() == 0
    assert (df["quality_report_line_count"] > 0).all()
    assert (df["inspection_markdown_count"] > 0).all()
    assert (df.loc[df["visual_casepack_complete"], "inspection_image_count"] > 0).all()

    for row in df.itertuples(index=False):
        assert Path(row.physical_root).exists()
        assert (MODULE_ROOT / row.quality_report_path).exists()
        assert (MODULE_ROOT / row.inspection_dossier_root).exists()
        assert (MODULE_ROOT / row.dataset_contract_path).exists()
        assert (MODULE_ROOT / row.registry_entry_path).exists()
        assert (MODULE_ROOT / row.consumption_policy_path).exists()
        assert (MODULE_ROOT / row.validator_path).exists()
        for schema_path in json.loads(row.schema_contract_paths_json):
            assert (MODULE_ROOT / schema_path).exists()

    assert validations["missing_physical_root_count"] == 0
    assert validations["missing_quality_report_count"] == 0
    assert validations["missing_dossier_count"] == 0
    assert validations["missing_schema_count"] == 0
    assert validations["missing_contract_count"] == 0
    assert validations["missing_registry_count"] == 0
    assert validations["missing_policy_count"] == 0
    assert validations["missing_validator_count"] == 0
    assert validations["visual_without_images_count"] == 0
    assert validations["artifact_claim_mismatch_count"] == 0


def test_dataset_certification_matrix_reconciles_to_source_matrix_and_gate_rules(
    tsis_artifacts_dir: Path,
) -> None:
    manifest = _manifest()
    df = _frame()
    source_rows = _source_summary_rows(Path(manifest["source_family_status_matrix"]))
    source_families = {
        "halts" if row["Family"].strip("`") == "Halts" else row["Family"].strip("`")
        for row in source_rows
    }

    assert source_families == EXPECTED_FAMILIES
    assert len(source_rows) == len(df) == 13

    blocked = df["data_quality_verdict"].eq("blocked_by_data_defect")
    scoped = df["data_quality_verdict"].eq("complete_scoped") | df["foundations_completion_status"].str.contains(
        "scoped"
    )
    usable_declared = df["data_quality_verdict"].eq("usable_for_declared_scope") & ~df[
        "foundations_completion_status"
    ].str.contains("scoped")

    assert df.loc[blocked, "production_use_gate"].eq("blocked_from_backtest_core").all()
    assert df.loc[blocked, "event_consumption_gate"].eq("forensic_or_repair_only").all()
    assert df.loc[blocked, "blocked_from_backtest_core"].all()
    assert df.loc[scoped, "production_use_gate"].eq("scoped_only").all()
    assert df.loc[scoped, "scoped_only"].all()
    assert df.loc[usable_declared, "production_use_gate"].eq("declared_scope_allowed").all()
    assert df.loc[usable_declared, "event_consumption_gate"].eq("allowed_with_family_policy").all()

    assert int(blocked.sum()) == manifest["validations"]["blocked_from_backtest_core_count"] == 2
    assert int(scoped.sum()) == manifest["validations"]["scoped_only_count"] == 5
    assert int(df["human_inspector_ready"].sum()) == manifest["validations"]["human_inspector_ready_count"] == 13
    assert int(df["visual_casepack_complete"].sum()) == manifest["validations"]["visual_casepack_complete_count"] == 13

    write_json_artifact(
        tsis_artifacts_dir,
        "dataset_certification_matrix_source_reconciliation.json",
        {
            "source_family_count": len(source_rows),
            "source_families": sorted(source_families),
            "blocked_from_backtest_core": sorted(df.loc[blocked, "dataset_family"].tolist()),
            "scoped_only": sorted(df.loc[scoped, "dataset_family"].tolist()),
            "source_family_status_matrix": manifest["source_family_status_matrix"],
            "source_family_status_matrix_sha256": manifest["source_family_status_matrix_sha256"],
        },
    )
