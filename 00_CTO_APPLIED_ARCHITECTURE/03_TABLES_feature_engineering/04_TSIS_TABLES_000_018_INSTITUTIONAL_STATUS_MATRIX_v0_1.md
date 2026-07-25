# TSIS Tables 000-018 Institutional Status Matrix v0.1

Status: `recorded_current_authority_reconciliation_v0_39_market_state_bounded_exact_match_reuse_transition_reflected`
Date: `2026-07-25`
Scope: `tables_000_018_current_institutional_status`

## Purpose

This document is the current table-level institutional status matrix for TSIS representation tables `000` through `018`.

It does not replace:

```text
02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
```

The Discovery Pass remains valid as the first historical discovery snapshot:

```text
Discovery Pass = what TSIS initially found.
This matrix   = what authority is currently known, reconciled, unresolved or still closed.
```

This matrix does not promote any dataset, does not authorize production, does not authorize downstream consumption and does not materialize any table.

## Reading Rule

The following states are distinct:

```text
documented table
reviewed table
candidate materialization
validated candidate
official semantic profile
official dataset
production dataset
downstream-consumable dataset
```

A parquet tree, review document, Graphify node, bounded run, manifest or candidate validation is not enough by itself to infer official dataset status.

When required evidence has not been reconciled against Data Foundation contracts, schemas, validators, registry entries and consumption policies, this matrix uses:

```text
UNRESOLVED_PENDING_EVIDENCE_RECONCILIATION
```

## Column Contract

Each table row is expressed as a key-value block with the following columns:

```text
table_id
canonical_name
institutional_role
current_physical_state
contract_status
schema_status
validation_status
registry_status
promotion_status
data_foundation_evidence_reconciliation_status
institutional_conclusion_after_data_foundation_reconciliation
official_dataset_inferred_after_reconciliation
consumption_status
production_status
physical_authority
semantic_authority
execution_authority
accepted_evidence
live_restrictions
next_required_gate
last_reviewed_at
```

## Authority Axis Rule

This matrix separates three authorities:

```text
physical_authority
    = who governs bytes, physical schemas, manifests, dataset registry state and data quality evidence.

semantic_authority
    = who governs meaning, representation role, Information Objects, Market State profiles and Event State policy.

execution_authority
    = which gate may execute, consume, materialize, promote or publish the artifact.
```

These axes must not be collapsed. A table can be physically present, semantically recognized and still have no execution authority.

## Data Foundation Evidence Reconciliation v0.1

Run: `tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z`
Status: `CLOSED_WITH_FINDINGS_NO_PROMOTION`
Persistent readout: `06_tables_000_018_evidence_reconciliation_readout_v0_1.md`

Previous accepted run `tables_000_018_evidence_reconciliation_v0_1_20260724T074513Z` is superseded only by summary-accounting normalization. The evidence conclusions did not change.

This reconciliation found Data Foundation evidence for all `000-018` rows without inferring any official physical dataset promotion.

Current Event State note: `event_type_registry_initial_population_readout_v0_1` recorded a candidate-only registry population; `event_type_initial_admission_review_readout_v0_1` admitted `event_type:market_data:session_opened` with restrictions; `event_instance_binding_design_readout_v0_1` recorded exchange-session instance identity; `event_window_binding_design_readout_v0_1` records design-only Event Window Binding grammar; `market_state_profile_compatibility_design_readout_v0_1` records semantic compatibility with the official Market State profile plus a required instrument-session projection; `event_state_instrument_session_projection_design_readout_v0_1` records the projection grammar; and `event_state_integration_design_readout_v0_1` records atomic exact-one Event State integration design. `event_state_execution_chain_joint_review_readout_v0_1` approved a bounded execution-chain authorization with restrictions and no execution. `event_state_bounded_execution_chain_authorization_readout_v0_1` froze the first bounded execution-chain scope, and accepted run `event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z` closed that scope with 8 non-official Event State candidate records, 1 blocked context and 0 hard validation failures; physical validation run `event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z` checked those 8 records with 0 schema, hash, fingerprint, binding, lineage, authority, determinism or hard validation failures. Candidate dataset review run `event_state_candidate_dataset_review_v0_1_20260724T194315Z` approved the physically validated 8-record output as bounded candidate Event State evidence with restrictions and no promotion. Profile promotion review run `event_state_profile_promotion_review_v0_1_20260724T201046Z` approved the bounded evidence for semantic Event State profile promotion with restrictions. Promotion run `event_state_profile_promotion_v0_1_20260724T203016Z` registered `event_state_core_four_intraday_profile_v0_1` as an official semantic Event State profile with restrictions. Artifact validation run `event_state_profile_artifact_validation_v0_1_20260724T204410Z` checked the 4 official profile registry artifacts with 0 hash mismatches, 0 invariant failures and 0 hard validation failures. Operational registry / consumption policy design `event_state_operational_registry_or_consumption_policy_design_v0_1` records design-only profile-reference use and explicitly keeps official dataset consumption closed. Runtime capabilities architecture `runtime_capabilities_architecture_v0_1` records the cross-cutting request/resolver/materializer/validator/registry layer with no execution. Market State on-demand capability design `market_state_on_demand_capability_design_v0_1`, request contract design `market_state_request_contract_design_v0_1`, execution plan contract design `market_state_execution_plan_contract_design_v0_1`, profile resolver design `market_state_profile_resolver_design_v0_1`, universe resolver design `market_state_universe_resolver_design_v0_1`, source resolver design `market_state_source_resolver_design_v0_1`, partition/coverage resolver design `market_state_partition_and_coverage_resolver_design_v0_1`, materializer design `market_state_materializer_design_v0_1` and validator design `market_state_validator_design_v0_1` and candidate dataset registry design `market_state_candidate_dataset_registry_design_v0_1` and run lifecycle/manifest design `market_state_run_lifecycle_and_manifest_design_v0_1`, on-demand execution-chain joint review `market_state_on_demand_execution_chain_joint_review_v0_1` and bounded on-demand execution authorization `market_state_bounded_on_demand_execution_authorization_v0_1` are recorded under Runtime Capabilities. Accepted run `market_state_bounded_on_demand_execution_v0_1_20260724T232123Z` consumed that authorization and closed as `CLOSED_PASS_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED`: 1 request record, 1 execution plan, 1 profile resolver execution, 1 universe resolver execution, 9 instrument-session contexts, 1 source resolver execution, 1 partition/coverage resolver execution, 1 materializer execution, 1 validator execution, 1 candidate parquet, 8 materialized candidate Market State rows, 1 unavailable context, 0 hard validation failures and 1 candidate dataset registry entry. Candidate dataset review `market_state_bounded_on_demand_candidate_dataset_review_v0_1` then approved that output as bounded candidate Market State on-demand evidence with restrictions, 0 review failures and no promotion. Deterministic rerun `market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z` closed as `CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS`; determinism validation `market_state_bounded_on_demand_determinism_validation_v0_1_20260725T000000Z` approved it as bounded determinism evidence with no reuse eligibility transition, no production and no downstream authority. `market_state_bounded_on_demand_idempotency_reuse_test_authorization_v0_1` was consumed by `market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z`. The bounded reuse lookup test closed as `CLOSED_PASS_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS` with idempotency status `PROVEN_FOR_BOUNDED_EXACT_MATCH_REUSE`: it selected existing dataset `market_state_candidate_dataset_v0_1_433288b634924676`, read 1 candidate registry metadata entry, read 0 candidate parquet files, read 0 source market-data rows, executed 0 materializers, wrote 0 new candidate parquets and wrote 0 new candidate dataset registry entries. Reuse eligibility transition review `market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061233Z` approved `eligible_for_bounded_exact_match_reuse` for the bounded exact-match scope only, using a transition record and 0 baseline registry entry mutations. These changes affect Runtime Capability evidence for `016_market_state_table` and the dependency path of `017_event_state_table`; they do not change the Data Foundation reconciliation run and do not promote any official Market State or Event State dataset.

```text
tables_seen = 19
proven_restricted_datasets = 13
proven_validated_candidates = 2
partial_reconciliations = 3
proven_restricted_controlled_replay_candidates = 1
unresolved = 0
classified_tables = 19
classification_invariant_pass = true
official_datasets_inferred = 0
source_market_data_rows_read = 0
parquet_files_read = 0
dataset_promotions_written = 0
event_type_registry_candidate_entries_written = 4
event_type_registry_accepted_entries_written = 1
event_instance_binding_designs_recorded = 1
event_window_binding_designs_recorded = 1
market_state_profile_compatibility_designs_recorded = 1
instrument_session_projection_designs_recorded = 1
event_state_integration_designs_recorded = 1
event_state_execution_chain_joint_reviews_recorded = 1
event_state_bounded_execution_chain_authorizations_recorded = 1
event_state_bounded_execution_chain_executions_closed = 1
event_state_bounded_execution_chain_physical_validations_closed = 1
event_state_candidate_dataset_reviews_closed = 1
event_state_profile_promotion_reviews_closed = 1
event_state_profile_promotions_closed = 1
event_state_profile_artifact_validations_closed = 1
event_state_operational_registry_or_consumption_policy_designs_recorded = 1
runtime_capabilities_architectures_recorded = 1
market_state_on_demand_capability_designs_recorded = 1
market_state_request_contract_designs_recorded = 1
market_state_execution_plan_contract_designs_recorded = 1
market_state_profile_resolver_designs_recorded = 1
market_state_universe_resolver_designs_recorded = 1
market_state_source_resolver_designs_recorded = 1
market_state_partition_and_coverage_resolver_designs_recorded = 1
market_state_materializer_designs_recorded = 1
market_state_validator_designs_recorded = 1
market_state_candidate_dataset_registry_designs_recorded = 1
market_state_run_lifecycle_and_manifest_designs_recorded = 1
market_state_on_demand_execution_chain_joint_reviews_closed = 1
market_state_bounded_on_demand_execution_authorizations_recorded = 1
market_state_bounded_on_demand_execution_authorized_max_contexts = 9
market_state_bounded_on_demand_execution_runs = 1
market_state_bounded_on_demand_execution_requested_contexts = 9
market_state_bounded_on_demand_execution_materialized_rows = 8
market_state_bounded_on_demand_execution_unavailable_contexts = 1
market_state_bounded_on_demand_execution_hard_validation_failures = 0
market_state_bounded_on_demand_execution_reuse_eligibility = pending_determinism_validation
market_state_bounded_on_demand_candidate_dataset_reviews_closed = 1
market_state_bounded_on_demand_candidate_dataset_review_failures = 0
market_state_bounded_on_demand_candidate_dataset_review_hard_failures = 0
market_state_bounded_on_demand_candidate_dataset_review_reuse_eligibility_after_review = pending_determinism_validation
market_state_bounded_on_demand_deterministic_rerun_authorizations_recorded = 1
market_state_bounded_on_demand_deterministic_rerun_authorization_status = CONSUMED_BY_RERUN
market_state_bounded_on_demand_deterministic_rerun_baseline_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
market_state_bounded_on_demand_deterministic_rerun_contract_content_sha256_excluding_hash_field = b3bc623ca83885f8773d8bd95f48418e1fa15c6038840d35da7cad860595f231
market_state_bounded_on_demand_deterministic_rerun_execution = CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS
market_state_bounded_on_demand_deterministic_rerun_run = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z
market_state_bounded_on_demand_deterministic_rerun_blocked_attempt = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T052825Z
market_state_bounded_on_demand_deterministic_rerun_attempts = 2
market_state_bounded_on_demand_deterministic_rerun_successful_runs = 1
market_state_bounded_on_demand_determinism_comparisons_created = 2
market_state_bounded_on_demand_determinism_successful_comparisons_created = 1
market_state_bounded_on_demand_determinism_status = PROVEN_FOR_BOUNDED_SCOPE
market_state_bounded_on_demand_determinism_blocking_failures = 0
market_state_bounded_on_demand_determinism_runtime_only_differences = 2
market_state_bounded_on_demand_determinism_comparison_fingerprint = ce87938504dbf8fc4e8e962e294aa81f8bc127cdfce69a7aa48157e655329dfb
market_state_bounded_on_demand_reuse_transition_ready = true
market_state_bounded_on_demand_reuse_eligibility_changes = 0
market_state_bounded_on_demand_determinism_validation = CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION
market_state_bounded_on_demand_determinism_validation_id = market_state_bounded_on_demand_determinism_validation_v0_1_20260725T000000Z
market_state_bounded_on_demand_determinism_validation_failures = 0
market_state_bounded_on_demand_determinism_validation_hard_failures = 0
market_state_bounded_on_demand_determinism_validation_reuse_eligibility_after_validation = pending_idempotency_reuse_test
market_state_bounded_on_demand_determinism_validation_reuse_eligibility_changes = 0
market_state_bounded_on_demand_idempotency_reuse_test_authorization = CONSUMED_BY_REUSE_TEST
market_state_bounded_on_demand_idempotency_reuse_test_authorization_baseline_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z
market_state_bounded_on_demand_idempotency_reuse_test_authorization_scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7
market_state_bounded_on_demand_idempotency_reuse_test_contract_content_sha256_excluding_hash_field = c836f3ae2d5821a0d2d7b66ee1c2db1c1866fe83b36a2d1fbb27f31bf678b98d
market_state_bounded_on_demand_idempotency_reuse_test_execution = CLOSED_PASS_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS
market_state_bounded_on_demand_idempotency_reuse_test_run = market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z
market_state_bounded_on_demand_idempotency_status = PROVEN_FOR_BOUNDED_EXACT_MATCH_REUSE
market_state_bounded_on_demand_idempotency_reuse_test_runs = 1
market_state_bounded_on_demand_idempotency_reuse_test_candidate_registry_metadata_reads = 1
market_state_bounded_on_demand_idempotency_reuse_test_materializer_executions = 0
market_state_bounded_on_demand_idempotency_reuse_test_source_market_data_rows_read = 0
market_state_bounded_on_demand_idempotency_reuse_test_source_candidate_records_read = 0
market_state_bounded_on_demand_idempotency_reuse_test_candidate_parquet_files_read = 0
market_state_bounded_on_demand_idempotency_reuse_test_new_candidate_parquet_files = 0
market_state_bounded_on_demand_idempotency_reuse_test_new_candidate_dataset_registry_entries = 0
market_state_bounded_on_demand_idempotency_reuse_test_evidence_entries_written = 1
market_state_bounded_on_demand_idempotency_reuse_test_reuse_eligibility_after_test = pending_reuse_eligibility_transition_review
market_state_bounded_on_demand_idempotency_reuse_test_reuse_eligibility_changes = 0
market_state_bounded_on_demand_idempotency_reuse_test_report_fingerprint = 2fe42810eff703a99aa64ebc67dda9126567c7548b6f99fbe589664490c6f537
market_state_bounded_on_demand_idempotency_reuse_test_evidence_entry_fingerprint = 97f3f0cb5bde4cac4a666f95f16fee2ee71eea821701355d7e8495963aff92b4
market_state_bounded_on_demand_reuse_eligibility_transition_review = CLOSED_APPROVED_REUSE_ELIGIBILITY_TRANSITION_FOR_BOUNDED_EXACT_MATCH_WITH_RESTRICTIONS_NO_PROMOTION
market_state_bounded_on_demand_reuse_eligibility_transition_review_run = market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061233Z
market_state_bounded_on_demand_reuse_eligibility_transition_review_blocked_attempt = market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061154Z
market_state_bounded_on_demand_reuse_eligibility_transition_review_technical_write_failure_attempt = market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061119Z
market_state_bounded_on_demand_reuse_eligibility_after_review = eligible_for_bounded_exact_match_reuse
market_state_bounded_on_demand_reuse_eligibility_transition_scope = bounded_exact_match_only
market_state_bounded_on_demand_reuse_eligibility_transition_registry_entry_mutations = 0
market_state_bounded_on_demand_reuse_eligibility_transition_official_dataset = false
market_state_bounded_on_demand_reuse_eligibility_transition_production = false
market_state_bounded_on_demand_reuse_eligibility_transition_downstream = false
market_state_bounded_on_demand_reuse_eligibility_transition_matrix_fingerprint = e8f1010c078a7ab9e68fa8ef072d7d9fb212f8623341617254e550aa26924f9a
market_state_bounded_on_demand_reuse_eligibility_transition_record_fingerprint = a1ea1e56d7f1b44cd0c91a37e0f6ecc2f4cbbbb16fd6be247f4e4e8959d8d845
market_state_joint_review_hard_findings = 0
market_state_joint_review_restriction_findings = 2
market_state_request_records_created = 1
market_state_execution_plans_created = 1
market_state_profile_resolver_executions = 1
market_state_profile_registry_runtime_reads = 0
market_state_universe_resolver_executions = 1
market_state_universe_manifests_created = 0
market_state_instrument_session_contexts_created = 9
market_state_calendar_runtime_reads = 0
market_state_instrument_master_runtime_reads = 0
market_state_instrument_identity_runtime_reads = 0
market_state_source_resolver_executions = 1
market_state_source_registry_runtime_reads = 0
market_state_source_contract_runtime_reads = 1
market_state_source_schema_runtime_reads = 0
market_state_source_consumption_policy_runtime_reads = 0
market_state_source_parquet_files_read = 0
market_state_resolved_source_sets_created = 1
market_state_partition_coverage_resolver_executions = 1
market_state_partition_manifests_created = 1
market_state_coverage_manifests_created = 1
market_state_existing_dataset_registry_runtime_reads = 0
market_state_source_manifest_runtime_reads = 0
market_state_partition_status_transitions = 0
market_state_execution_plan_instances_created = 1
market_state_materializer_executions = 1
market_state_builder_executions = 1
market_state_staging_directories_created = 0
market_state_candidate_data_files_written = 2
market_state_candidate_parquet_files_written = 1
market_state_output_manifests_created = 1
market_state_lineage_manifests_created = 1
market_state_content_hashes_computed = 8
market_state_validation_reports_created = 5
market_state_validator_executions = 1
market_state_candidate_files_read = 1
market_state_parquet_files_read = 1
market_state_dataset_registry_entries_written = 1
market_state_datasets_registered = 1
market_state_datasets_promoted = 0
market_state_datasets_superseded = 0
market_state_quarantine_transitions = 0
market_state_on_demand_requests_executed = 1
market_state_on_demand_datasets_written = 1
market_state_bounded_on_demand_execution_runs_closed = 1
market_state_run_records_created = 1
market_state_run_manifests_created = 3
market_state_final_manifests_created = 1
market_state_heartbeat_records_written = 1
market_state_execution_authorizations_consumed = 1
market_state_execution_plans_consumed = 1
event_state_candidate_records_emitted_in_bounded_execution = 8
event_state_bounded_execution_blocked_contexts = 1
event_detection_runs_started = 0
event_instances_created_outside_bounded_execution = 0
event_windows_created_outside_bounded_execution = 0
```

| ID | Table | Data Foundation evidence | Institutional conclusion | Confidence |
| --- | --- | --- | --- | --- |
| 000 | `instrument_master` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 001 | `market_calendar` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 002 | `expected_data_calendar` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 003 | `dataset_certification_matrix` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 004 | `master_daily_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 005 | `corporate_actions_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 006 | `halts_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 007 | `event_windows_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 008 | `outcomes_table` | `controlled_candidate_not_promoted,validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET_WITH_CANDIDATE_EXTENSION` | `PROVEN` |
| 009 | `fundamentals_asof_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 010 | `news_context_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 011 | `short_context_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 012 | `regime_context_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 013 | `ohlcv_1m_quote_guarded` | `FOUND_REPAIR_OVERLAY_AND_CANDIDATE_TREE` | `PARTIALLY_RECONCILED_WITH_PROMOTED_REPAIR_OVERLAY_AND_CANDIDATE_TREE` | `PARTIAL` |
| 014 | `master_intraday_bar_table` | `scoped_pilot` | `PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS` | `PROVEN` |
| 015 | `microstructure_features_table` | `controlled_candidate_not_promoted,seed_state_sample` | `PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS` | `PROVEN` |
| 016 | `market_state_table` | `controlled_candidate_not_promoted` | `PARTIALLY_RECONCILED_WITH_SEMANTIC_PHYSICAL_SPLIT` | `PARTIAL` |
| 017 | `event_state_table` | `controlled_candidate_not_promoted; candidate_event_type_population_recorded; initial_admission_review_recorded; event_instance_binding_design_recorded; event_window_binding_design_recorded; market_state_profile_compatibility_design_recorded; instrument_session_projection_design_recorded; event_state_integration_design_recorded; execution_chain_joint_review_recorded; bounded_execution_chain_candidate_output_recorded_physically_validated_reviewed_profile_promoted_profile_artifact_validated_and_operational_registry_policy_design_recorded` | `PARTIALLY_RECONCILED_WITH_DESIGN_CANDIDATE_REGISTRY_ONE_ACCEPTED_EVENT_TYPE_INSTANCE_WINDOW_COMPATIBILITY_PROJECTION_INTEGRATION_JOINT_REVIEW_BOUNDED_EXECUTION_PHYSICAL_VALIDATION_CANDIDATE_DATASET_REVIEW_OFFICIAL_SEMANTIC_PROFILE_PROMOTION_AND_PROFILE_ARTIFACT_VALIDATION_AND_OPERATIONAL_REGISTRY_POLICY_DESIGN` | `PARTIAL` |
| 018 | `intraday_scanner_candidates_table` | `FOUND_CONTROLLED_REPLAY_EVIDENCE` | `PROVEN_RESTRICTED_CONTROLLED_REPLAY_CANDIDATE` | `PROVEN` |

Interpretation:

- `PROVEN_RESTRICTED_DATASET` means Data Foundation evidence exists for the declared scope and restrictions. It does not mean unrestricted production or downstream consumption.
- `PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS` means a candidate/pilot/seed surface exists and remains bounded by explicit scope flags.
- `PROVEN_RESTRICTED_CONTROLLED_REPLAY_CANDIDATE` means replay/candidate evidence exists with restrictions and is not official source authority.
- `PARTIALLY_RECONCILED_WITH_*` means the physical and semantic layers are both documented but must not be collapsed into one official dataset claim.

## Matrix

### 000 - instrument_master

```text
table_id = 000
canonical_name = instrument_master
institutional_role = instrument identity, universe membership and listing lifecycle context
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = identity context is restricted to declared scope; not final lifecycle engine by this matrix
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 001 - market_calendar

```text
table_id = 001
canonical_name = market_calendar
institutional_role = exchange session calendar and temporal observability boundary
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = bounded calendar use only where explicit Market State scopes authorize it
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = trading-session-only XNYS calendar; no fixed UTC fallback and no closed-day row inference unless separately designed
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 002 - expected_data_calendar

```text
table_id = 002
canonical_name = expected_data_calendar
institutional_role = dataset expectedness and observability coverage context
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = expectedness is a denominator/diagnostic, not proof of physical presence or usability
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 003 - dataset_certification_matrix

```text
table_id = 003
canonical_name = dataset_certification_matrix
institutional_role = dataset consumption eligibility, quality state and governance context
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = family-level quality gate; not row-level proof or market signal
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 004 - master_daily_table

```text
table_id = 004
canonical_name = master_daily_table
institutional_role = daily price, range, activity and prior-history context
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = bounded builder scopes only; this matrix grants no execution authority
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = daily context only where flags and prior-history scope allow; no execution/microstructure authority
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 005 - corporate_actions_table

```text
table_id = 005
canonical_name = corporate_actions_table
institutional_role = corporate action context, price adjustment context and identity lifecycle changes
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = corporate actions cannot silently rewrite price semantics downstream
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 006 - halts_table

```text
table_id = 006
canonical_name = halts_table
institutional_role = regulatory or venue interruption context and possible future event source
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = halt source data is not accepted Event Type registry population by itself
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 007 - event_windows_table

```text
table_id = 007
canonical_name = event_windows_table
institutional_role = event-window boundaries and temporal windows for accepted event families
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = halt-derived windows only where declared; not all event families and not Event State execution authority
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 008 - outcomes_table

```text
table_id = 008
canonical_name = outcomes_table
institutional_role = outcomes/labels kept separate from observable state
current_physical_state = Data Foundation output evidence found for declared scope: controlled_candidate_not_promoted,validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = controlled_candidate_not_promoted,validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET_WITH_CANDIDATE_EXTENSION
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = controlled_candidate_not_promoted,validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET_WITH_CANDIDATE_EXTENSION; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = outcomes remain y/labels; never observable X or feature input without leakage-safe contract
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 009 - fundamentals_asof_table

```text
table_id = 009
canonical_name = fundamentals_asof_table
institutional_role = filing-date-aware fundamental context
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = requires explicit as-of join; not ratios/market-cap/float authority by itself
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 010 - news_context_table

```text
table_id = 010
canonical_name = news_context_table
institutional_role = as-of news and catalyst context
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = news context is not proof of causality or live received-latency alert stream
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 011 - short_context_table

```text
table_id = 011
canonical_name = short_context_table
institutional_role = short pressure and short-side context under source-specific lag rules
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = requires explicit source selection, as-of/lag join and source caveats
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 012 - regime_context_table

```text
table_id = 012
canonical_name = regime_context_table
institutional_role = session-level regime context and market background
current_physical_state = Data Foundation output evidence found for declared scope: validated_for_declared_scope
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = validated_for_declared_scope; validator=FOUND; conclusion=PROVEN_RESTRICTED_DATASET
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = validated_for_declared_scope; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_DATASET; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture representation review; Data Foundation governs physical meaning and consumption policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = not same-session intraday causal state or execution truth
next_required_gate = no_reconciliation_gate_pending; separate Data Foundation promotion or consumption gate only if explicitly authorized
last_reviewed_at = 2026-07-24
```

### 013 - ohlcv_1m_quote_guarded

```text
table_id = 013
canonical_name = ohlcv_1m_quote_guarded
institutional_role = intraday bar observability and price-integrity source for governed derived surfaces
current_physical_state = repair overlay promoted for declared LT1B scope plus physical quote-guarded candidate tree; full-universe official claim remains false
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = MISSING_IN_RECONCILED_SCOPE
validation_status = FOUND_REPAIR_OVERLAY_AND_CANDIDATE_TREE; validator=MISSING; conclusion=PARTIALLY_RECONCILED_WITH_PROMOTED_REPAIR_OVERLAY_AND_CANDIDATE_TREE
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = FOUND_REPAIR_MANIFEST_PROMOTION_NOT_DATASET_PROMOTION
data_foundation_evidence_reconciliation_status = FOUND_REPAIR_OVERLAY_AND_CANDIDATE_TREE; schema=MISSING; contract=FOUND; registry=FOUND; policy=FOUND; validator=MISSING
institutional_conclusion_after_data_foundation_reconciliation = PARTIALLY_RECONCILED_WITH_PROMOTED_REPAIR_OVERLAY_AND_CANDIDATE_TREE; confidence=PARTIAL
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture surface-use mapping; Data Foundation quote-guarded price-view policy
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = candidate physical tree is not unrestricted official full-universe dataset; no direct builder/downstream use without explicit scope
next_required_gate = quote_guarded_official_dataset_or_schema_reconciliation_gate_if_required; not opened by this matrix
last_reviewed_at = 2026-07-24
```

### 014 - master_intraday_bar_table

```text
table_id = 014
canonical_name = master_intraday_bar_table
institutional_role = master intraday bar representation / bounded intraday surface source
current_physical_state = Data Foundation scoped pilot exists; Scale A/B/C also created run-local derived surfaces as candidate evidence
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = scoped_pilot; validator=FOUND; conclusion=PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = scoped_pilot; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture intraday surface mapping; Data Foundation output semantics
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = scoped pilot/run-local surfaces only; not full-universe 1m or execution truth
next_required_gate = master_intraday_bar_table_scope_expansion_or_promotion_review_if_required; not opened by this matrix
last_reviewed_at = 2026-07-24
```

### 015 - microstructure_features_table

```text
table_id = 015
canonical_name = microstructure_features_table
institutional_role = microstructure feature representation candidate
current_physical_state = seed sample and controlled candidate materializations exist; not promoted
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = controlled_candidate_not_promoted,seed_state_sample; validator=FOUND; conclusion=PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = controlled_candidate_not_promoted,seed_state_sample; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture future microstructure profile design; Data Foundation candidate feature semantics
execution_authority = not authorized by this matrix; explicit Data Foundation consumption/promotion gate required
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = candidate/seed feature evidence only; not ML/RL-ready or execution-ready
next_required_gate = microstructure_profile_or_candidate_promotion_gate_if_required; not opened by this matrix
last_reviewed_at = 2026-07-24
```

### 016 - market_state_table

```text
table_id = 016
canonical_name = market_state_table
institutional_role = Market State representation target, now governed as a family of profiles rather than a single mega-table
current_physical_state = Data Foundation legacy controlled candidate exists; Applied Architecture official semantic profile exists; one bounded Runtime Capabilities candidate Market State on-demand output exists as non-official candidate evidence; one deterministic force-rebuild rerun reproduced the bounded scientific output; no official physical Market State dataset exists
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = controlled_candidate_not_promoted; runtime_bounded_candidate_validation=PASS_WITH_RESTRICTIONS; validator=FOUND; conclusion=PARTIALLY_RECONCILED_WITH_SEMANTIC_PHYSICAL_SPLIT_AND_BOUNDED_ON_DEMAND_CANDIDATE_EVIDENCE
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = NOT_FOUND_FOR_DATA_FOUNDATION_DATASET; SEMANTIC_PROFILE_PROMOTION_EXISTS_OUTSIDE_DATA_FOUNDATION
data_foundation_evidence_reconciliation_status = controlled_candidate_not_promoted; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PARTIALLY_RECONCILED_WITH_SEMANTIC_PHYSICAL_SPLIT; confidence=PARTIAL
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation for any physical Market State dataset; Applied Architecture only for semantic profile registry
semantic_authority = Applied Architecture official Market State profile registry and profile-family architecture
execution_authority = bounded on-demand candidate execution consumed once for 9 contexts; closed for official dataset materialization/production/downstream consumption
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_execution_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_bounded_on_demand_execution_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_execution_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_execution_authorization_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_execution_v0_1_20260724T232123Z/final_manifest.json; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_execution_v0_1_20260724T232123Z/market_state_bounded_on_demand_execution_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_execution_v0_1_20260724T232123Z/candidate_registry_entry.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_candidate_dataset_review_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_bounded_on_demand_candidate_dataset_review_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_candidate_dataset_review_matrix_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_candidate_dataset_review_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_deterministic_rerun_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_bounded_on_demand_deterministic_rerun_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_deterministic_rerun_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_deterministic_rerun_authorization_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/scripts/market_state_bounded_on_demand_deterministic_rerun_runner_v0_1.py; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T052825Z/final_manifest.json; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z/final_manifest.json; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z/market_state_deterministic_rerun_comparison_v0_1.json; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z/determinism_report.json; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z/deterministic_rerun_evidence_entry.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_determinism_validation_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_bounded_on_demand_determinism_validation_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_determinism_validation_matrix_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_determinism_validation_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_idempotency_reuse_test_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_bounded_on_demand_idempotency_reuse_test_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_idempotency_reuse_test_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_idempotency_reuse_test_authorization_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/scripts/market_state_bounded_on_demand_idempotency_reuse_test_runner_v0_1.py; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z/final_manifest.json; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z/market_state_bounded_on_demand_idempotency_reuse_test_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z/reuse_lookup_report.json; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z/idempotency_reuse_test_report.json; 08_RUNTIME_CAPABILITIES/runs/market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z/idempotency_reuse_evidence_entry.json
live_restrictions = official semantic profile is not official physical dataset; bounded on-demand output, deterministic rerun, determinism validation and idempotency/reuse test are candidate/runtime evidence only; reuse eligibility transition is pending explicit review; official parquet and downstream consumption remain false
next_required_gate = market_state_on_demand_incremental_overlap_execution_authorization_v0_1; official_market_state_dataset_materialization_policy_design remains separate
last_reviewed_at = 2026-07-25
```

### 017 - event_state_table

```text
table_id = 017
canonical_name = event_state_table
institutional_role = Event State representation target dependent on Market State profile, event instance, event window, state_role and consumption_legality
current_physical_state = Data Foundation legacy controlled candidate exists; current Event State architecture, registry seed schema, candidate population, initial admission review, Event Instance Binding Design, Event Window Binding Design, Market State Profile Compatibility Design, Instrument Session Projection Design, Event State Integration Design, execution-chain joint review, bounded candidate execution, bounded candidate physical validation, candidate dataset review, profile promotion review and semantic profile promotion are recorded; one Event Type is accepted_with_restrictions; 8 non-official bounded candidate Event State records exist as physically validated and reviewed candidate evidence; no Event State physical dataset, Event Instance registry or Event Window registry is promoted
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = controlled_candidate_not_promoted; validator=FOUND; conclusion=PARTIALLY_RECONCILED_WITH_DESIGN_CANDIDATE_REGISTRY_ONE_ACCEPTED_EVENT_TYPE_INSTANCE_WINDOW_COMPATIBILITY_PROJECTION_INTEGRATION_JOINT_REVIEW_BOUNDED_EXECUTION_PHYSICAL_VALIDATION_CANDIDATE_DATASET_REVIEW_AND_OFFICIAL_SEMANTIC_PROFILE_PROMOTION
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = SEMANTIC_PROFILE_PROMOTION_EXISTS_OUTSIDE_DATA_FOUNDATION; LEGACY_CANDIDATE_NOT_PROMOTED_AS_DATASET
data_foundation_evidence_reconciliation_status = controlled_candidate_not_promoted; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PARTIALLY_RECONCILED_WITH_DESIGN_CANDIDATE_REGISTRY_ONE_ACCEPTED_EVENT_TYPE_INSTANCE_WINDOW_COMPATIBILITY_PROJECTION_INTEGRATION_JOINT_REVIEW_BOUNDED_EXECUTION_PHYSICAL_VALIDATION_CANDIDATE_DATASET_REVIEW_AND_OFFICIAL_SEMANTIC_PROFILE_PROMOTION; confidence=PARTIAL
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation for any physical Event State dataset; Applied Architecture/Event Governance for current Event State design
semantic_authority = Applied Architecture Event State architecture and Event Type/Event State policy
execution_authority = bounded execution chain consumed for session_opened only; semantic profile promotion consumed; closed for official dataset promotion, unbounded Event Instance Binding execution, unbounded Event Window Binding execution, materialization, production and downstream use
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_type_registry_seed_design_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_type_registry_seed_design_contract_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_type_registry_initial_population_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_type_registry_initial_population_snapshot_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_type_initial_admission_review_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_type_registry_post_initial_admission_snapshot_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_instance_binding_design_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_instance_binding_design_contract_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_window_binding_design_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_window_binding_design_contract_v0_1.json; 07_EVENT_STATE_INTEGRATION/market_state_profile_compatibility_design_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/market_state_profile_compatibility_design_contract_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_instrument_session_projection_design_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_state_instrument_session_projection_design_contract_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_integration_design_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_state_integration_design_contract_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_execution_chain_joint_review_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_state_execution_chain_joint_review_matrix_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_bounded_execution_chain_authorization_v0_1.md; 07_EVENT_STATE_INTEGRATION/configs/event_state_bounded_execution_chain_scope_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_bounded_execution_chain_contract_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_bounded_execution_chain_authorization_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/runs/event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z/final_manifest.json; 07_EVENT_STATE_INTEGRATION/runs/event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z/event_state_bounded_execution_chain_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/runs/event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z/event_state_validation_report.json; 07_EVENT_STATE_INTEGRATION/runs/event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z/event_state_candidate_manifest.json; 07_EVENT_STATE_INTEGRATION/event_state_bounded_execution_chain_physical_validation_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/runs/event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z/final_manifest.json; 07_EVENT_STATE_INTEGRATION/event_state_candidate_dataset_review_authorization_v0_1.md; 07_EVENT_STATE_INTEGRATION/configs/event_state_candidate_dataset_review_scope_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_candidate_dataset_review_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/runs/event_state_candidate_dataset_review_v0_1_20260724T194315Z/final_manifest.json; 07_EVENT_STATE_INTEGRATION/event_state_profile_promotion_review_authorization_v0_1.md; 07_EVENT_STATE_INTEGRATION/configs/event_state_profile_promotion_review_scope_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_profile_promotion_review_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/runs/event_state_profile_promotion_review_v0_1_20260724T201046Z/final_manifest.json; 07_EVENT_STATE_INTEGRATION/event_state_profile_promotion_authorization_v0_1.md; 07_EVENT_STATE_INTEGRATION/configs/event_state_profile_promotion_scope_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_profile_promotion_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/runs/event_state_profile_promotion_v0_1_20260724T203016Z/final_manifest.json; 07_EVENT_STATE_INTEGRATION/official_profiles/event_state_core_four_intraday_profile_v0_1/PROFILE_MANIFEST.json; 07_EVENT_STATE_INTEGRATION/event_state_profile_artifact_validation_authorization_v0_1.md; 07_EVENT_STATE_INTEGRATION/configs/event_state_profile_artifact_validation_scope_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_profile_artifact_validation_readout_v0_1.md; 07_EVENT_STATE_INTEGRATION/runs/event_state_profile_artifact_validation_v0_1_20260724T204410Z/final_manifest.json; 07_EVENT_STATE_INTEGRATION/event_state_operational_registry_or_consumption_policy_design_authorization_v0_1.md; 07_EVENT_STATE_INTEGRATION/configs/event_state_operational_registry_or_consumption_policy_design_scope_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_operational_registry_or_consumption_policy_design_v0_1.md; 07_EVENT_STATE_INTEGRATION/event_state_operational_registry_or_consumption_policy_contract_v0_1.json; 07_EVENT_STATE_INTEGRATION/event_state_operational_registry_or_consumption_policy_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/runtime_capabilities_architecture_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/runtime_capabilities_architecture_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/runtime_capabilities_architecture_v0_1.md; 08_RUNTIME_CAPABILITIES/runtime_capabilities_architecture_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/runtime_capabilities_architecture_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_on_demand_capability_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_on_demand_capability_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_on_demand_capability_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_on_demand_capability_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_on_demand_capability_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_request_contract_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_request_contract_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_request_contract_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_request_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_request_contract_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_execution_plan_contract_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_execution_plan_contract_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_execution_plan_contract_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_execution_plan_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_execution_plan_contract_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_profile_resolver_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_profile_resolver_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_profile_resolver_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_profile_resolver_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_profile_resolver_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_universe_resolver_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_universe_resolver_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_universe_resolver_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_universe_resolver_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_universe_resolver_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_source_resolver_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_source_resolver_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_source_resolver_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_source_resolver_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_source_resolver_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_partition_and_coverage_resolver_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_partition_and_coverage_resolver_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_partition_and_coverage_resolver_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_partition_and_coverage_resolver_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_partition_and_coverage_resolver_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_materializer_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_materializer_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_materializer_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_materializer_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_materializer_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_validator_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_validator_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_validator_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_validator_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_validator_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_candidate_dataset_registry_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_candidate_dataset_registry_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_candidate_dataset_registry_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_candidate_dataset_registry_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_candidate_dataset_registry_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_run_lifecycle_and_manifest_design_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_run_lifecycle_and_manifest_design_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_run_lifecycle_and_manifest_design_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_run_lifecycle_and_manifest_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_run_lifecycle_and_manifest_design_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_on_demand_execution_chain_joint_review_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_on_demand_execution_chain_joint_review_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_on_demand_execution_chain_joint_review_matrix_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_on_demand_execution_chain_joint_review_readout_v0_1.md; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_execution_authorization_v0_1.md; 08_RUNTIME_CAPABILITIES/configs/market_state_bounded_on_demand_execution_scope_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_execution_contract_v0_1.json; 08_RUNTIME_CAPABILITIES/market_state_bounded_on_demand_execution_authorization_readout_v0_1.md
live_restrictions = candidate_event_types = 1; accepted_event_types = 1; session_opened Event Instance and Event Window Binding Designs are exchange_session only; Market State compatibility is semantic only; instrument-session projection, Event State integration, execution-chain joint review, bounded execution-chain candidate output, bounded physical validation, candidate dataset review and profile promotion review are recorded; bounded execution emitted physically validated and reviewed non-official JSONL evidence only; semantic profile promotion is executed with restrictions; Market State bounded on-demand execution run is recorded as a validated partial candidate with 8 materialized rows and 1 unavailable context; halt_resumed remains blocked; no Event State dataset promotion, materialization, official parquet, production or downstream use authorized
next_required_gate = market_state_on_demand_incremental_overlap_execution_authorization_v0_1
last_reviewed_at = 2026-07-25
```

### 018 - intraday_scanner_candidates_table

```text
table_id = 018
canonical_name = intraday_scanner_candidates_table
institutional_role = scanner candidate and attention surface; not Event Type authority
current_physical_state = controlled replay candidate evidence exists; not official E-root materialization and not event authority
contract_status = FOUND_IN_DATA_FOUNDATION_DATASET_CONTRACT
schema_status = FOUND_IN_DATA_FOUNDATION_CANONICAL_SCHEMA
validation_status = FOUND_CONTROLLED_REPLAY_EVIDENCE; validator=FOUND; conclusion=PROVEN_RESTRICTED_CONTROLLED_REPLAY_CANDIDATE
registry_status = FOUND_IN_DATA_FOUNDATION_DATASET_REGISTRY
promotion_status = MISSING
data_foundation_evidence_reconciliation_status = FOUND_CONTROLLED_REPLAY_EVIDENCE; schema=FOUND; contract=FOUND; registry=FOUND; policy=FOUND; validator=FOUND
institutional_conclusion_after_data_foundation_reconciliation = PROVEN_RESTRICTED_CONTROLLED_REPLAY_CANDIDATE; confidence=PROVEN
official_dataset_inferred_after_reconciliation = false
consumption_status = FOUND_DATA_FOUNDATION_CONSUMPTION_POLICY; restrictions preserved; this matrix grants no downstream use
production_status = not_authorized_by_this_matrix
physical_authority = Data Foundation
semantic_authority = Applied Architecture scanner/event boundary policy plus Data Foundation scanner candidate semantics
execution_authority = closed for Event Type authority; scanner lifecycle requires separate gate
accepted_evidence = 06_tables_000_018_evidence_reconciliation_readout_v0_1.md; run tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z; 01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md; 02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md
live_restrictions = scanner candidate != event type; attention surface cannot populate Event State registry automatically
next_required_gate = scanner_candidate_lifecycle_reconciliation_or_v0_2_quote_guarded_design_if_explicitly_authorized
last_reviewed_at = 2026-07-24
```

## Current Cross-Table Boundaries

```text
official_dataset_registry_write_allowed = false
official_parquet_write_allowed = false
candidate_parquet_copy_allowed = false
production_builder_allowed = false
downstream_consumption_allowed = false
full_history_full_universe_claim_allowed = false
market_state_materialization_allowed = false
event_state_materialization_allowed = false
event_type_registry_initial_population_open_authorization_allowed = false
event_type_admission_execution_allowed = false
event_detection_execution_allowed = false
```

## Next Architectural Gate

The next architectural gate after Event State profile promotion is:

```text
market_state_request_contract_design_v0_1
```

The profile promotion gate has been executed separately and registered `event_state_core_four_intraday_profile_v0_1` as an official semantic Event State profile with restrictions. This matrix still does not open official Event State dataset promotion, parquet writes, production or downstream consumption by itself.
