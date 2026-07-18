# dataset_certification_matrix_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Family-level quality gates. |
| operational_use | Family gate/mask for consumers. |
| exclusions | Family-level only; not ticker/date row validation. |

## Source

| item | value |
| --- | --- |
| dataset_id | `dataset_certification_matrix_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\dataset_certification_matrix_v0_1.parquet` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\dataset_certification_matrix_v0_1.parquet` |
| declared_rows_in_status_matrix | 13 |
| declared_file_or_partition_count_in_status_matrix | 1 |
| physical_parquet_files_seen | 1 |
| physical_rows_from_parquet_metadata | 13 |
| physical_row_groups_seen | 1 |
| sample_physical_columns | 64 |

## Sample Selection

First rows from the official single-file parquet.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `certification_id` | `string` |
| 1 | `dataset_family` | `string` |
| 2 | `source_matrix_family_label` | `string` |
| 3 | `certification_scope` | `string` |
| 4 | `physical_root` | `string` |
| 5 | `physical_root_exists` | `bool` |
| 6 | `role` | `string` |
| 7 | `data_quality_verdict` | `string` |
| 8 | `foundations_completion_status` | `string` |
| 9 | `visual_inspection_status` | `string` |
| 10 | `production_use_gate` | `string` |
| 11 | `event_consumption_gate` | `string` |
| 12 | `blocked_from_backtest_core` | `bool` |
| 13 | `scoped_only` | `bool` |
| 14 | `human_inspector_ready` | `bool` |
| 15 | `visual_casepack_complete` | `bool` |
| 16 | `main_reading` | `string` |
| 17 | `completion_gap_next_action` | `string` |
| 18 | `source_matrix_path` | `string` |
| 19 | `source_matrix_sha256` | `string` |
| 20 | `quality_report_path` | `string` |
| 21 | `quality_report_exists` | `bool` |
| 22 | `quality_report_line_count` | `int64` |
| 23 | `inspection_dossier_root` | `string` |
| 24 | `inspection_dossier_exists` | `bool` |
| 25 | `inspection_markdown_count` | `int64` |
| 26 | `inspection_image_count` | `int64` |
| 27 | `casepack_markdown_count` | `int64` |
| 28 | `visual_pack_path` | `string` |
| 29 | `evidence_assets_present` | `bool` |
| 30 | `schema_contract_paths_json` | `string` |
| 31 | `schema_contract_count` | `int64` |
| 32 | `schema_contract_present` | `bool` |
| 33 | `missing_schema_contract_count` | `int64` |
| 34 | `dataset_contract_path` | `string` |
| 35 | `dataset_contract_present` | `bool` |
| 36 | `registry_entry_path` | `string` |
| 37 | `registry_entry_present` | `bool` |
| 38 | `consumption_policy_path` | `string` |
| 39 | `consumption_policy_present` | `bool` |
| 40 | `validator_path` | `string` |
| 41 | `validator_present` | `bool` |
| 42 | `artifact_matrix_physical` | `string` |
| 43 | `artifact_matrix_schema` | `string` |
| 44 | `artifact_matrix_contract` | `string` |
| 45 | `artifact_matrix_registry` | `string` |
| 46 | `artifact_matrix_policy` | `string` |
| 47 | `artifact_matrix_validators` | `string` |
| 48 | `artifact_matrix_dossier_readout` | `string` |
| 49 | `artifact_matrix_evidence_assets` | `string` |
| 50 | `artifact_matrix_visual_inspector_pack` | `string` |
| 51 | `technical_profile_report_state` | `string` |
| 52 | `artifact_matrix_schema_claims_present` | `bool` |
| 53 | `artifact_matrix_contract_claims_present` | `bool` |
| 54 | `artifact_matrix_registry_claims_present` | `bool` |
| 55 | `artifact_matrix_policy_claims_present` | `bool` |
| 56 | `artifact_matrix_validators_claims_present` | `bool` |
| 57 | `artifact_matrix_dossier_claims_present` | `bool` |
| 58 | `artifact_matrix_evidence_assets_claims_present` | `bool` |
| 59 | `artifact_matrix_visual_claims_present` | `bool` |
| 60 | `quality_policy_version` | `string` |
| 61 | `build_run_id` | `string` |
| 62 | `schema_version` | `string` |
| 63 | `created_at_utc` | `string` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `certification_id` | ccfdb6d7b36e2e960f53221a6ae7469ca3ef3eedcf06239856f8de6172843e95 | 24ab96cd26ec61223d1a37256e230c57879e7752d7c14a350a453622db3247f8 | f0c388bcc1943711b7f0ce4549eba1dc6d55b76b6e3936d55f4133b2077b4e72 | 55d99d2e31a548e73fa7d623f03b98bee20f99f904eeb0780a75dd68352151f3 | 2b4042ae2c67317ee0f63c340564752bf9f6f22d4c84ab0a22c9e7fc86fadad5 |
| `dataset_family` | additional | daily | financial | halts | intraday_regime_features |
| `source_matrix_family_label` | additional | daily | financial | Halts | intraday_regime_features |
| `certification_scope` | family_level | family_level | family_level | family_level | family_level |
| `physical_root` | E:/TSIS/data/additional | E:/TSIS/data/ohlcv_daily | E:/TSIS/data/financial | E:/TSIS/data/Halts | E:/TSIS/data/intraday_regime_features |
| `physical_root_exists` | True | True | True | True | True |
| `role` | RAW vendor context by subfamily | RAW/STAGED daily market bars | RAW/vendor-preserved fundamentals and ratios | RAW reference/event data | Feature layer / consumer pilot |
| `data_quality_verdict` | usable_for_declared_scope | usable_for_declared_scope | blocked_by_data_defect | usable_for_declared_scope | complete_scoped |
| `foundations_completion_status` | human_inspector_ready | human_inspector_ready | human_inspector_ready | human_inspector_ready | human_inspector_ready_scoped |
| `visual_inspection_status` | visual_complete | visual_complete | visual_complete | visual_complete | visual_complete_scoped |
| `production_use_gate` | declared_scope_allowed | declared_scope_allowed | blocked_from_backtest_core | declared_scope_allowed | scoped_only |
| `event_consumption_gate` | allowed_with_family_policy | allowed_with_family_policy | forensic_or_repair_only | allowed_with_family_policy | allowed_with_scope_flags |
| `blocked_from_backtest_core` | False | False | True | False | False |
| `scoped_only` | False | False | False | False | True |
| `human_inspector_ready` | True | True | True | True | True |
| `visual_casepack_complete` | True | True | True | True | True |
| `main_reading` | Has schema, contract, registry, policy, validators, dossier, quality tables, casepacks and a formal visual inspector pack. It is not one uniform dataset. | Institutional raw daily layer with separate quality and coverage axes. Hard invalid tail is small and coverage frontier is explicit. | Operational audit states `status = FAIL`, with 13,337 severe issues and 3,171 temporal issues, now backed by dossier-local evidence assets, casepacks and a v... | Modern dossier exists with root audit, source quality, event taxonomy, universe coverage, multisource reconciliation, casepacks and a 10-image visual inspect... | Semantic pilot proves a real consumer for `ohlcv_1m_split_normalized`; the 8-ticker, 243-row pilot has key/provenance evidence, 10 concrete semantic images a... |
| `completion_gap_next_action` | Maintain subfamily boundaries; no direct feature/alpha promotion without PIT, attribution and authority controls. | Maintain existing dossier, coverage evidence and visual casepacks as benchmark. | Keep blocked for consumption until sentinel severity, temporal/lifecycle issues and identity/PIT policy are repaired or explicitly waived. | Maintain event/context boundary; do not promote to alpha, live, RL or execution simulation without a downstream contract. | Keep pilot boundary explicit; production feature-store promotion requires a future full-universe audit and new visuals. |
| `source_matrix_path` | 01_foundations/data_quality_report/family_status_matrix_v0_1.md | 01_foundations/data_quality_report/family_status_matrix_v0_1.md | 01_foundations/data_quality_report/family_status_matrix_v0_1.md | 01_foundations/data_quality_report/family_status_matrix_v0_1.md | 01_foundations/data_quality_report/family_status_matrix_v0_1.md |
| `source_matrix_sha256` | c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35 | c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35 | c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35 | c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35 | c380c7a5f85c14925410899b264de4e52c62571a1b1ff7b359cec733f16f5d35 |
| `quality_report_path` | 01_foundations/data_quality_report/families/additional_quality_report_v0_1.md | 01_foundations/data_quality_report/families/daily_quality_report_v0_1.md | 01_foundations/data_quality_report/families/financial_quality_report_v0_1.md | 01_foundations/data_quality_report/families/halts_quality_report_v0_1.md | 01_foundations/data_quality_report/families/intraday_regime_features_quality_report_v0_1.md |
| `quality_report_exists` | True | True | True | True | True |
| `quality_report_line_count` | 102 | 195 | 263 | 127 | 240 |
| `inspection_dossier_root` | 01_foundations/inspection_dossiers/additional | 01_foundations/inspection_dossiers/daily | 01_foundations/inspection_dossiers/financial | 01_foundations/inspection_dossiers/halts | 01_foundations/inspection_dossiers/intraday_regime_features |
| `inspection_dossier_exists` | True | True | True | True | True |
| `inspection_markdown_count` | 20 | 9 | 10 | 17 | 10 |
| `inspection_image_count` | 8 | 181 | 6 | 15 | 25 |
| `casepack_markdown_count` | 4 | 4 | 4 | 7 | 4 |
| `visual_pack_path` | 01_foundations/inspection_dossiers/additional/visual_inspector_pack/additional_visual_inspector_pack_v0_1.md |  | 01_foundations/inspection_dossiers/financial/visual_inspector_pack/financial_visual_inspector_pack_v0_1.md | 01_foundations/inspection_dossiers/halts/visual_inspector_pack/halts_visual_inspector_pack_v0_1.md | 01_foundations/inspection_dossiers/intraday_regime_features/visual_inspector_pack/intraday_regime_features_visual_inspector_pack_v0_1.md |
| `evidence_assets_present` | True | True | True | True | True |
| `schema_contract_paths_json` | ["01_foundations/canonical_schemas/additional/additional_corporate_actions_schema_contract.md","01_foundations/canonical_schemas/additional/additional_econom... | ["01_foundations/canonical_schemas/daily/daily_schema_contract.md"] | ["01_foundations/canonical_schemas/financial/balance_sheets_schema_contract.md","01_foundations/canonical_schemas/financial/cash_flow_statements_schema_contr... | ["01_foundations/canonical_schemas/halts/halts_master_multisource_schema_contract.md","01_foundations/canonical_schemas/halts/halts_operational_summary_schem... | ["01_foundations/canonical_schemas/features/intraday_regime_features_schema_contract.md"] |
| `schema_contract_count` | 5 | 1 | 6 | 5 | 1 |
| `schema_contract_present` | True | True | True | True | True |
| `missing_schema_contract_count` | 0 | 0 | 0 | 0 | 0 |
| `dataset_contract_path` | 01_foundations/contract_registry/dataset_contracts/additional_dataset_contract_v0_1.md | 01_foundations/contract_registry/dataset_contracts/daily_dataset_contract_v0_1.md | 01_foundations/contract_registry/dataset_contracts/financial_dataset_contract_v0_1.md | 01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md | 01_foundations/contract_registry/dataset_contracts/intraday_regime_features_dataset_contract_v0_1.md |
| `dataset_contract_present` | True | True | True | True | True |
| `registry_entry_path` | 01_foundations/dataset_registry/additional/additional_registry_entry.yaml | 01_foundations/dataset_registry/daily/daily_registry_entry.yaml | 01_foundations/dataset_registry/financial/financial_registry_entry.yaml | 01_foundations/dataset_registry/halts/halts_registry_entry.yaml | 01_foundations/dataset_registry/features/intraday_regime_features_registry_entry.yaml |
| `registry_entry_present` | True | True | True | True | True |
| `consumption_policy_path` | 01_foundations/data_consumption_policies/additional_consumption_policy.md | 01_foundations/data_consumption_policies/daily_consumption_policy.md | 01_foundations/data_consumption_policies/financial_consumption_policy.md | 01_foundations/data_consumption_policies/halts_consumption_policy.md | 01_foundations/data_consumption_policies/intraday_regime_features_consumption_policy.md |
| `consumption_policy_present` | True | True | True | True | True |
| `validator_path` | 01_foundations/validators/additional/additional_validators.md | 01_foundations/validators/daily/daily_validators.md | 01_foundations/validators/financial/financial_validators.md | 01_foundations/validators/halts/halts_validators.md | 01_foundations/validators/intraday_regime_features/intraday_regime_features_validators.md |
| `validator_present` | True | True | True | True | True |
| `artifact_matrix_physical` | yes | yes | yes | yes | yes |
| `artifact_matrix_schema` | yes | yes | yes | yes | yes |
| `artifact_matrix_contract` | yes | yes | yes | yes | yes |
| `artifact_matrix_registry` | yes | yes | yes | yes | yes |
| `artifact_matrix_policy` | yes | yes | yes | yes | yes |
| `artifact_matrix_validators` | yes | yes | yes | yes | yes |
| `artifact_matrix_dossier_readout` | yes | yes | yes | yes | yes, scoped |
| `artifact_matrix_evidence_assets` | yes | yes | yes | yes | yes |
| `artifact_matrix_visual_inspector_pack` | yes | yes | yes | yes | yes, scoped |
| `technical_profile_report_state` | partial, normalize | yes | yes | yes | yes, scoped |
| `artifact_matrix_schema_claims_present` | True | True | True | True | True |
| `artifact_matrix_contract_claims_present` | True | True | True | True | True |
| `artifact_matrix_registry_claims_present` | True | True | True | True | True |
| `artifact_matrix_policy_claims_present` | True | True | True | True | True |
| `artifact_matrix_validators_claims_present` | True | True | True | True | True |
| `artifact_matrix_dossier_claims_present` | True | True | True | True | True |
| `artifact_matrix_evidence_assets_claims_present` | True | True | True | True | True |
| `artifact_matrix_visual_claims_present` | True | True | True | True | True |
| `quality_policy_version` | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 | dataset_certification_matrix_policy_v0_1 |
| `build_run_id` | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z | dataset_certification_matrix_v0_1_20260622T154116Z |
| `schema_version` | dataset_certification_matrix_v0_1 | dataset_certification_matrix_v0_1 | dataset_certification_matrix_v0_1 | dataset_certification_matrix_v0_1 | dataset_certification_matrix_v0_1 |
| `created_at_utc` | 2026-06-22T15:41:16.124579+00:00 | 2026-06-22T15:41:16.124579+00:00 | 2026-06-22T15:41:16.124579+00:00 | 2026-06-22T15:41:16.124579+00:00 | 2026-06-22T15:41:16.124579+00:00 |

## Interpretation

Use this file to understand the physical/logical shape and example values of the represented Data Foundation output.
For completeness, pass/fail status, official scope, and exclusions, use the cloned target contract and status matrix in the parent folder.

## Scope Guard

Excluded from this operational sample set:

- `master_intraday_bar_table`: scoped pilot/candidate, not official full-universe 1m.
- `microstructure_features_table`: seed/candidate controlled, not full-universe.
- `market_state_table`: official state table not materialized/promoted; candidates are controlled only.
- `event_state_table`: official state table not materialized/promoted; candidates are controlled only.
- `intraday_scanner_candidates_table`: strategy/candidate surface, not a validated Data Foundation full table.
