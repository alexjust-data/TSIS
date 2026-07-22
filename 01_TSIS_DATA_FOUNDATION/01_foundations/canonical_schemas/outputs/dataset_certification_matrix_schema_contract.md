# Dataset Certification Matrix Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
dataset_certification_matrix_v0_1
```

The table is the machine-readable normalization of:

```text
01_foundations/data_quality_report/family_status_matrix_v0_1.md
```

It does not replace the human matrix. It materializes its family-level status
so downstream builders can join quality gates without scraping markdown by hand.

## 2. Logical Unit

Unit:

```text
dataset family certification state
```

Grain:

```text
dataset_family + certification_scope + quality_policy_version
```

Current scope:

```text
family_level
```

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix
```

Artifacts:

```text
dataset_certification_matrix_v0_1.parquet
_dataset_certification_matrix_summary_v0_1.csv
_dataset_certification_matrix_manifest_v0_1.json
```

Builder:

```text
scripts/materialize_dataset_certification_matrix.py
```

## 4. Source

Authoritative source:

```text
01_foundations/data_quality_report/family_status_matrix_v0_1.md
```

The builder parses:

- `Summary Table`;
- `Artifact Presence Matrix`.

The builder also checks real file presence for schemas, contracts, policies,
registries, validators, quality reports and inspection dossiers.

## 5. Required Columns

Identity:

- `certification_id`
- `dataset_family`
- `source_matrix_family_label`
- `certification_scope`

Status:

- `data_quality_verdict`
- `foundations_completion_status`
- `visual_inspection_status`
- `production_use_gate`
- `event_consumption_gate`
- `blocked_from_backtest_core`
- `scoped_only`
- `human_inspector_ready`
- `visual_casepack_complete`

Physical and evidence:

- `physical_root`
- `physical_root_exists`
- `quality_report_path`
- `quality_report_exists`
- `inspection_dossier_root`
- `inspection_dossier_exists`
- `inspection_markdown_count`
- `inspection_image_count`
- `casepack_markdown_count`
- `visual_pack_path`
- `evidence_assets_present`

Artifact links:

- `schema_contract_paths_json`
- `schema_contract_count`
- `schema_contract_present`
- `missing_schema_contract_count`
- `dataset_contract_path`
- `dataset_contract_present`
- `registry_entry_path`
- `registry_entry_present`
- `consumption_policy_path`
- `consumption_policy_present`
- `validator_path`
- `validator_present`

Source matrix lineage:

- `source_matrix_path`
- `source_matrix_sha256`

Context:

- `role`
- `main_reading`
- `completion_gap_next_action`
- `technical_profile_report_state`

Build lineage:

- `quality_policy_version`
- `build_run_id`
- `schema_version`
- `created_at_utc`

## 6. Controlled Values

`schema_version`:

```text
dataset_certification_matrix_v0_1
```

`quality_policy_version`:

```text
dataset_certification_matrix_policy_v0_1
```

Allowed `production_use_gate` values in v0.1:

- `declared_scope_allowed`
- `scoped_only`
- `blocked_from_backtest_core`

Allowed `event_consumption_gate` values in v0.1:

- `allowed_with_family_policy`
- `allowed_with_scope_flags`
- `forensic_or_repair_only`

## 7. Structural Rules

Hard failures:

- zero rows;
- duplicate `dataset_family`;
- missing physical root;
- missing quality report;
- missing inspection dossier;
- missing schema contract;
- missing dataset contract;
- missing registry entry;
- missing consumption policy;
- missing validator;
- visual-complete row with zero dossier images;
- artifact matrix claims presence while the file evidence is absent;
- row count different from the 13 families in `family_status_matrix_v0_1.md`.

Review:

- source family status matrix hash changes;
- a family changes from scoped to full-ready or vice versa;
- data-quality verdict changes;
- new family is added to `E:/TSIS/data`;
- existing family receives a new consumption state.

## 8. Interpretation

Permitted:

- join family-level quality gates into downstream outputs;
- decide whether a family is allowed, scoped, blocked or forensic-only;
- link an event case to human inspection evidence;
- verify that every family has the required evidence surfaces.

Not permitted:

- use as price, feature, label, market data or signal;
- override a family-specific validator;
- treat `human_inspector_ready` as production usability;
- hide blocked data defects;
- replace visual dossiers or data-quality reports.

