# CRM Missing Operational Artifacts v0.1

Status: `architectural_review_v0_1`

Reviewed object: `C:\TSIS_Data\00_CTO_1\01_CANONICAL_REPRESENTATION_MATERIALIZATION`

Reviewed as: `candidate_architecture`

Review date: `2026-07-14`

## Purpose

This review identifies which verifiable artifacts would be required for the CRM framework to change TSIS in practice.

The rule used here is strict: do not create a new document if an existing contract, registry, status matrix, manifest or validator can be extended without losing clarity.

## Operational Artifact Matrix

| Artifact | Purpose | Required fields | Existing equivalent | Create / extend / do not create | Authoritative location | Affected contracts or registries |
|---|---|---|---|---|---|---|
| `representation_justification_record` | Prove why a representation or enabling artifact deserves to exist before table creation. | `record_id`; `artifact_id`; `artifact_role` (`canonical_market_representation`, `enabling_institutional_artifact`, `feature_surface`, `outcome_surface`, `quality_gate`, `overlay_manifest`); `justification_type`; `problem_solved`; `authority_source_paths`; `non_goals`; `downstream_consumers`; `status`; `owner`; `review_date`. | Partial equivalents in `data_foundation_outputs_target_contract_v0_1.md` (`que debe existir y por que`), dataset contracts, registry entries, `VERSIONING_STANDARDS.md` promotion rules. | `extend + create_template`: extend dataset contracts/registry entries; create a lightweight proposal template only for new artifacts not yet in registry. | Future official: `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\...` and `dataset_registry\outputs\...`; candidate template can live under CRM until adopted. | Dataset contracts, dataset registry, target contract, table creation process. |
| `materialization_decision_record` | Record whether semantic existence should become a physical artifact, and under what scope/status. | `record_id`; `canonical_representation_ref`; `physical_artifact_id`; `materialization_mode`; `materialization_scope`; `coverage_denominator`; `full_universe_claim`; `candidate_status`; `source_roots`; `expected_output_root`; `required_validators`; `promotion_blockers`; `decision`; `decision_date`; `reviewer`. | Strong partial equivalent in Market Representation Chapter 16; materialization plans for `014` and `015`; `market_state_coverage_and_lookback_policy_v0_1.md`; manifests and status matrix. | `extend + create_template`: extend dataset contracts/manifests/status matrix; template only for proposals. | Future official fields should appear in dataset contract + manifest + status matrix. CRM can own the review template, not final status. | `data_foundation_outputs_status_matrix_v0_1.md`, dataset contracts, output manifests, materialization plans, `TABLES_CREATION_process_v0_1.md`. |
| `canonical_to_physical_mapping` | Link semantic authority to the exact physical artifact and prevent "table name = meaning" ambiguity. | `mapping_id`; `canonical_authority_path`; `canonical_entity_name`; `physical_artifact_id`; `physical_representation_type`; `schema_contract_path`; `dataset_contract_path`; `registry_entry_path`; `consumption_policy_path`; `validator_path`; `builder_path`; `manifest_path`; `promotion_status`; `consumer_permissions`; `known_gaps`. | Partial equivalents in `05_TABLES\paths.md`, dataset registry entries, target contract lists and status matrix. No single crosswalk currently covers semantic authority -> physical artifact -> current status. | `create + extend`: create as required crosswalk in proposal/review; later extend dataset registry fields so it is queryable. | Candidate: CRM `_00_CTO` or future `_templates`; official: `01_foundations\dataset_registry\outputs` and/or `contract_registry`. | Dataset registry entries for all governed outputs; status matrix; table creation process. |
| `certification_record` | Prove the artifact has evidence, validators and current readiness status. | `artifact_id`; `schema_validation_status`; `validator_status`; `test_evidence_path`; `manifest_path`; `summary_path`; `row_count`; `file_count`; `quality_state`; `hard_fail_count`; `review_findings`; `consumer_gate_status`; `certification_status`; `certification_date`. | Strong equivalent in `data_foundation_outputs_status_matrix_v0_1.md`, validators, manifests, test-run folders and inspection dossiers. | `extend`: do not create a second certification authority. Add missing CRM fields to status matrix/registry if needed. | `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md` plus validators/manifests. | Status matrix, validators, manifests, inspection dossiers, dataset registry. |
| `promotion_record` | Record official adoption and allowed consumption. | `artifact_id`; `from_status`; `to_status`; `promotion_scope`; `semantic_authority`; `schema_version`; `dataset_version`; `manifest_hash`; `validator_summary`; `downstream_compatibility`; `breaking_change_flag`; `changelog_entry`; `approver`; `promotion_date`; `rollback/deprecation note`. | Strong partial equivalent in `VERSIONING_STANDARDS.md`, `CHANGELOG.md`, status matrix, registry entries and table-specific promotion gates. | `extend + create_template`: do not create parallel promotion authority; create a promotion-review template for high-severity artifacts if needed. | Official status in registry/status matrix/changelog; review template can be governed by `VERSIONING_STANDARDS.md`. | `VERSIONING_STANDARDS.md`, `CHANGELOG.md`, dataset registry, status matrix, promotion sections in materialization plans. |
| `representation_lifecycle_record` | Track semantic lifecycle separately from physical artifact lifecycle. | `canonical_representation_id`; `canonical_lifecycle_status`; `physical_artifact_id`; `physical_lifecycle_status`; `dataset_version`; `schema_version`; `replacement_of`; `replaced_by`; `deprecation_reason`; `migration_note`; `archive_path`; `effective_dates`. | Partial equivalents in `VERSIONING_STANDARDS.md`, dataset registry entries and manifests. The canonical-vs-physical split is not consistently explicit. | `extend`: add lifecycle fields to registry/status matrix; standalone docs only for deprecation/migration notes. | Dataset registry and versioning/changelog system. | Dataset registry entries, status matrix, changelog, versioning standards. |
| `architectural_traceability_record` | Make every adopted representation navigable from epistemology to physical manifest and back to consumer permissions. | `traceability_id`; `epistemological_authority_paths`; `representation_chapter_ref`; `target_contract_path`; `schema_contract_path`; `dataset_contract_path`; `registry_entry_path`; `policy_path`; `validator_path`; `builder_path`; `config_path`; `manifest_path`; `test_evidence_path`; `status_matrix_ref`; `consumer_gates`; `graphify_nodes`; `known_gaps`; `last_review_date`. | Partial equivalents in raw-to-consumption lineage contracts, dataset registry authority-chain concepts, status matrix and Graphify. No general architecture-to-physical record exists. | `create + extend`: create required traceability record for new high-severity representations; extend registries/manifests to hold links. | CRM can define the template; official evidence lives in `01_foundations` registries/contracts/manifests and status matrix. | State raw-to-consumption lineage contracts, dataset registry, status matrix, manifests, table creation process. |

## Artifact-Specific Findings

### 1. representation_justification_record

Current state: `documented_target` exists informally in target contracts, but not as a reusable gate.

Evidence:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md`, section `target_contract = que debe existir y por que`.
- `C:\TSIS_Data\VERSIONING_STANDARDS.md`, section `Promotion barrier`.
- `C:\TSIS_Data\00_CTO_1\01_CANONICAL_REPRESENTATION_MATERIALIZATION\Chapter_03_Representation_Justification.md`.

Recommendation:

- Create a short template only for proposals.
- Once an artifact is accepted, persist the fields in dataset contract and registry entry.

### 2. materialization_decision_record

Current state: `documented_target` exists strongly in theory and table-specific plans, but not as a general pre-build gate.

Evidence:

- `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\17_Chapter_16_Materialization_Policy_TSIS.md`, sections `16.2`, `16.3`, `16.12`, `16.13`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md`, sections `Non-Negotiable Boundary`, `What "Full Universe" Means Here`, `Promotion Gate`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\microstructure_features_table_multi_window_materialization_plan_v0_1.md`, sections `Candidate Dataset`, `Test Requirements`, `Current Status`.

Recommendation:

- Make this the main operational artifact of CRM.
- It should not redefine materialization modes; it should cite them.

### 3. canonical_to_physical_mapping

Current state: partial lists exist, but no canonical crosswalk currently answers the full question "which semantic representation does this physical artifact implement, under what status?"

Evidence:

- `C:\TSIS_Data\00_CTO_1\05_TABLES\paths.md`, section `Schemas, dataset contracts, policies, registries y validators`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\*.yaml`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`, output status rows.

Recommendation:

- Create this as a required CRM crosswalk.
- Later add fields such as `canonical_representation_ref`, `artifact_role`, `physical_representation_type`, `materialization_mode`, `promotion_status` to registry entries.

### 4. certification_record

Current state: strong equivalent exists.

Evidence:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`, output status table and evidence sections.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\*.md`.
- `C:\TSIS_Data\tests\test_runs\...` evidence paths cited by status matrix.

Recommendation:

- Do not create a second certification document as authority.
- Extend status matrix only if CRM-specific fields are missing.

### 5. promotion_record

Current state: promotion rules exist, but a representation-scoped promotion record could make high-severity promotions clearer.

Evidence:

- `C:\TSIS_Data\VERSIONING_STANDARDS.md`, sections `Institutional Promotion Review`, `Required Versioning Practices`.
- `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\19_Chapter_18_Representation_Governance_TSIS.md`, sections `Promotion Path`, `Governance Review`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`, statuses `controlled_candidate_not_promoted`, `validated_for_declared_scope`, `not_materialized`.

Recommendation:

- Use a promotion-review template for high-severity artifacts.
- Persist official promotion status in registry/status matrix/changelog, not in CRM.

### 6. representation_lifecycle_record

Current state: lifecycle exists for datasets and institutional artifacts, but the canonical-vs-physical split is not yet systematic.

Evidence:

- `C:\TSIS_Data\VERSIONING_STANDARDS.md`, sections `Institutional maturity status model`, `Dataset and Output Versioning`, `Deprecation / Archive`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\*.yaml`.

Recommendation:

- Extend registry/status fields.
- Avoid standalone lifecycle files except for deprecation, migration or archive decisions.

### 7. architectural_traceability_record

Current state: specific lineage contracts exist for state work; a general CRM traceability record does not.

Evidence:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md`.
- Graphify navigation surfaced related nodes: `Raw To Consumption Lineage`, `Market State Builder`, `Outcomes Separated From State`.

Recommendation:

- Create this only for high-severity or new representation/materialization proposals.
- It should be a pointer record; evidence remains in source documents, contracts, tests and manifests.

## Minimal Adoption Package

If CRM is adopted, the minimal verifiable package should be:

1. Add a `representation_justification` section to new dataset contracts or proposal templates.
2. Add a `materialization_decision` section to new dataset contracts/manifests/status rows.
3. Add registry fields: `artifact_role`, `canonical_representation_ref`, `physical_representation_type`, `materialization_mode`, `promotion_status`, `lifecycle_status`.
4. Add a `canonical_to_physical_mapping` crosswalk for every high-severity representation/table.
5. Add an `architectural_traceability` checklist for high-severity changes.
6. Extend `TABLES_CREATION_process_v0_1.md` with a pre-build gate: no physical build until justification, materialization decision and contract-set crosswalk exist.

## What Not To Create

Do not create independent authoritative copies of:

1. certification status;
2. promotion status;
3. schema definitions;
4. validator definitions;
5. table creation process;
6. materialization modes;
7. constitutional principles.

Those authorities already exist. CRM should only require that they are cited and connected.

