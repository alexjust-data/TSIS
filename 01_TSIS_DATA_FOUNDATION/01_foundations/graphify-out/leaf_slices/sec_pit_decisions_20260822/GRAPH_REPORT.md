# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 250 files · ~107,423 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1534 nodes · 3690 edges · 83 communities (81 shown, 2 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 90 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Cohort Metadata Gate Pipeline
- Atomic SEC Storage Layer
- No-Network Share Admission Probe
- Massive SEC Client Runtime
- Holder Position Ledger Pipeline
- Ownership Extraction Test Suite
- Share-Class Recovery Audit
- Presession Market-Cap Pipeline
- Authorized Acquisition Audit
- SEC Observation Extraction Core
- Lifecycle Document Extraction Pipeline
- Ownership Snapshot Parser
- Massive SEC Acquisition Runner
- Content-Addressed SEC Client
- Owner-Exclusion Identity Probe
- Single-Ticker SEC Pilot
- Restriction Evidence Extraction
- Authorized Primary Acquisition Runner
- Stratified Owner-Exclusion Probe
- Acquisition Authorization Validation
- Owner-Exclusion Resolution Batch
- SEC PIT Authority Evidence
- HTML Ownership Extraction
- Descending Acquisition Preflight
- Owner-Exclusion Float Resolver
- Companyfacts O/S Reconciliation Probe
- Instrument-Interval Recovery Audit
- Massive SEC Control Evidence
- Ownership Scale-Gate Decisions
- Daily O/S Resolver Tests
- PGAC No-Network O/S Probe
- Acquisition Telemetry Utilities
- Market Operations Snapshot Pipeline
- Sharded Variable Certification Audit
- Hundred-Case Candidate Pool
- Multiclass Ownership Reconciliation
- Lifecycle Market-Presence Reconciliation
- Submissions Metadata Profiling
- SEC PIT Canonical Schemas
- Ownership Baseline Classification
- Lifecycle Metadata Lane Audit
- Historical CUSIP Materialization
- Acquisition Ledger Merge
- SEC Acquisition Governance Evidence
- Massive Acquisition Telemetry
- Lifecycle Primary Acquisition Runner
- O/S Unavailable Shard Audit
- Daily Balance-Sheet Context
- Hundred-Case Sample Freeze
- Seven-Ticker Replay Pipeline
- Download Authorization Validator
- Class O/S Extraction Tests
- Lockup Release Schedule
- Registration Restriction Conditions
- Target-Interval Filing Review
- Owner-Exclusion Results Audit
- August Funding Vintage Pipeline
- Composite Acquisition Ledger
- Metadata Lifecycle Ledger
- Daily Change Explanation Pipeline
- Pilot O/S Materialization
- O/S Anchor Reconciliation
- Registration-to-O/S Reconciliation
- Acquisition Authorization Tests
- Ownership Identity Tests
- Assignment Schedule Linking
- Ownership Identity Extraction
- Lifecycle Acquisition Audit
- Restriction Event Reconciliation
- Assignment Restriction Extraction
- Overlap Recovery Audit
- August Funding Evidence Extraction
- Predownload Lifecycle Selection
- Split-Adjusted O/S Alignment
- Class O/S V3 Tests
- Lifecycle Market-Presence Tests
- 8-K Disclosure Schemas
- Form 3/4/5 Ownership Extraction
- Massive SEC Model Utilities
- Issuer Name Matching Tests
- Market Operations Snapshot Tests
- EDGAR Index Schema

## God Nodes (most connected - your core abstractions)
1. `EdgarAvailabilityPolicy` - 73 edges
2. `stable_id()` - 53 edges
3. `extract_normalized_ownership_snapshots()` - 49 edges
4. `atomic_write_json()` - 48 edges
5. `execute()` - 42 edges
6. `context()` - 41 edges
7. `SourceObservation` - 38 edges
8. `execute()` - 33 edges
9. `ContentAddressedStore` - 30 edges
10. `execute()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `test_chain_plan_preserves_every_direct_endpoint()` --calls--> `build_chain_plan()`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/tests/test_massive_sec_scope_gate.py → 01_TSIS_DATA_FOUNDATION/scripts/sec_pit/run_massive_sec_acquisition.py
- `InstrumentAdmissionDecision` --uses--> `EdgarAvailabilityPolicy`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/scripts/sec_pit/class_os_extract.py → 01_TSIS_DATA_FOUNDATION/scripts/sec_pit/availability.py
- `InstrumentAdmissionDecision` --uses--> `EdgarAvailabilityPolicy`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/scripts/sec_pit/class_os_extract_v2.py → 01_TSIS_DATA_FOUNDATION/scripts/sec_pit/availability.py
- `RunTelemetry` --uses--> `EdgarAvailabilityPolicy`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/scripts/sec_pit/run_one_ticker_pilot.py → 01_TSIS_DATA_FOUNDATION/scripts/sec_pit/availability.py
- `test_availability_never_uses_post_cutoff_filing_same_session()` --calls--> `EdgarAvailabilityPolicy`  [EXTRACTED]
  01_TSIS_DATA_FOUNDATION/tests/test_sec_pit_pipeline.py → 01_TSIS_DATA_FOUNDATION/scripts/sec_pit/availability.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **schema system** — sec_pit_source_obs_concept, sec_pit_resolved_v02_concept, sec_pit_edgar_index_concept, sec_pit_8k_disclosures_concept, sec_pit_disclosure_taxonomy_concept, sec_pit_form3_concept, sec_pit_form4_concept, sec_pit_runtime_artifacts_concept [EXTRACTED 0.99]
- **dataset governance** — sec_pit_fund_dataset_concept, sec_pit_massive_dataset_concept, sec_pit_predownload_dataset_concept, sec_pit_fund_policy_concept, sec_pit_massive_policy_concept, sec_pit_predownload_policy_concept, sec_pit_massive_registry_concept [EXTRACTED 0.99]
- **authorization workflow** — sec_pit_preparation_concept, sec_pit_full_auth_concept, sec_pit_final_cert_concept, sec_pit_runtime_artifacts_concept [EXTRACTED 0.99]
- **bounded evidence workflow** — sec_pit_predownload_seven_concept, sec_pit_pgac_pilot_concept, sec_pit_pgac_os_concept, sec_pit_pgac_ownership_concept, sec_pit_scale_gate_concept [EXTRACTED 0.99]
- **certification ladder** — sec_pit_os_multi_evidence_concept, sec_pit_ownership_parser_concept, sec_pit_html_whitespace_concept, sec_pit_identity_record_date_concept, sec_pit_split_gate_concept, sec_pit_residual_layout_zero_concept, sec_pit_option_physical_schema_concept, sec_pit_adaptive_baseline_concept, sec_pit_interval_v018_concept, sec_pit_os_overlap_v019_concept, sec_pit_exact_share_class_v021_concept [EXTRACTED 0.99]
- **vendor probe workflow** — sec_pit_massive_recovery_cert_concept, sec_pit_massive_probe_projection_concept, sec_pit_4824_preflight_concept [EXTRACTED 0.99]
- **operational control plane** — sec_pit_operator_runbook_concept, sec_pit_recovery_contract_concept, sec_pit_storage_decision_concept, sec_pit_acquisition_validators_concept, sec_pit_predownload_validators_concept [EXTRACTED 0.99]
- **certification workflow** — sec_pit_seven_owner_probe_concept, sec_pit_share_class_v016_concept, sec_pit_predownload_validators_concept [EXTRACTED 0.99]
- **storage migration boundary** — sec_pit_storage_decision_concept, sec_pit_recovery_contract_concept, sec_pit_operator_runbook_concept [EXTRACTED 1.00]

## Communities (83 total, 2 thin omitted)

### Community 0 - "Cohort Metadata Gate Pipeline"
Cohesion: 0.05
Nodes (76): cik(), distribution(), execute(), git_value(), parse_args(), projected_full_universe_bytes(), Any, Namespace (+68 more)

### Community 1 - "Atomic SEC Storage Layer"
Cohesion: 0.06
Nodes (41): audit(), parser(), ArgumentParser, Namespace, Path, sha256(), audit(), parse_args() (+33 more)

### Community 2 - "No-Network Share Admission Probe"
Cohesion: 0.08
Nodes (47): admit_target_instrument_document_v0_3(), _archive_continuity_allowed(), resolve_common_equity_class_candidate_v0_3(), admit_target_instrument_document(), InstrumentAdmissionDecision, normalized_text_key(), Resolve a generic common-equity gate to the class tied to the ticker., registrant_name_keys() (+39 more)

### Community 3 - "Massive SEC Client Runtime"
Cohesion: 0.09
Nodes (28): AdaptiveRateLimiter, FetchedPage, MassiveResponseContractError, MassiveSecClient, Any, Response, RuntimeError, Session (+20 more)

### Community 4 - "Holder Position Ledger Pipeline"
Cohesion: 0.10
Nodes (38): build_holder_position_ledger(), _controlled_entity_name(), _id(), _methodology_relevant(), _normalized_name(), Any, build_holder_position_ledger_v0_8(), Any (+30 more)

### Community 5 - "Ownership Extraction Test Suite"
Cohesion: 0.14
Nodes (41): extract_normalized_ownership_snapshots(), context(), test_20f_multiclass_accepts_plain_ownership_header(), test_20f_multiclass_supports_interleaved_share_and_percent_columns(), test_20f_share_ownership_table_emits_exact_multiclass_components(), test_annual_report_does_not_infer_zero_from_missing_management_table(), test_annual_report_emits_only_explicit_zero_management_ownership(), test_explicit_unnumbered_common_table_is_not_tainted_by_other_class_text() (+33 more)

### Community 6 - "Share-Class Recovery Audit"
Cohesion: 0.11
Nodes (34): _attributes(), audit_case(), build_audit(), derive_workstreams(), _document_signals(), _json_list(), _load_ledger(), main() (+26 more)

### Community 7 - "Presession Market-Cap Pipeline"
Cohesion: 0.10
Nodes (28): AvailabilityDecision, main(), Path, _sha256(), _write_json(), _as_date(), build_presession_reference_market_cap(), _primary_splits() (+20 more)

### Community 8 - "Authorized Acquisition Audit"
Cohesion: 0.15
Nodes (26): AuditTelemetry, duration_seconds(), git_state(), iter_jsonl(), load_json(), main(), parse_args(), path_is_within() (+18 more)

### Community 9 - "SEC Observation Extraction Core"
Cohesion: 0.18
Nodes (24): admit_target_interval_document(), extract_cover_page_class_os(), InstrumentAdmissionDecision, _candidate_patterns(), class_pattern(), Pattern, extract_cover_page_class_os_v0_3(), Pattern (+16 more)

### Community 10 - "Lifecycle Document Extraction Pipeline"
Cohesion: 0.13
Nodes (30): git_value(), main(), parse_args(), Namespace, Path, Materialize neutral lifecycle observations from acquired SEC primary documents., sha256_file(), utc_now() (+22 more)

### Community 11 - "Ownership Snapshot Parser"
Cohesion: 0.12
Nodes (32): _document_record_date(), _exact_current_shares_from_footnote(), _expanded_row_cells(), _explicit_document_ownership_date(), _explicit_multiclass_table_rows(), _following_table_notes(), _has_position_specific_acquirable_disclosure(), _is_aggregate_management() (+24 more)

### Community 12 - "Massive SEC Acquisition Runner"
Cohesion: 0.18
Nodes (29): stable_json_hash(), TargetGroup, Long-running-operation telemetry for Massive SEC acquisition., utc_now(), write_pid_manifest(), _assert_resume_compatible(), build_chain_plan(), _component_hashes() (+21 more)

### Community 13 - "Content-Addressed SEC Client"
Cohesion: 0.15
Nodes (16): Any, Path, Session, SecClient, AcquisitionResult, Any, ContentAddressedStore, FakeResponse (+8 more)

### Community 14 - "Owner-Exclusion Identity Probe"
Cohesion: 0.17
Nodes (24): blocker_details(), Any, archive_cik(), common_equity_row_count(), decide_document_identity(), is_common_equity_title(), is_identity_admitted(), normalize_cik() (+16 more)

### Community 15 - "Single-Ticker SEC Pilot"
Cohesion: 0.15
Nodes (23): InstrumentScope, Any, resolve_tradability_eligibility(), reconcile_registration_to_selling_lots(), summarize_registration_component_conflicts(), enrich_companyfacts_availability(), execute(), git_value() (+15 more)

### Community 16 - "Restriction Evidence Extraction"
Cohesion: 0.15
Nodes (24): EdgarAvailabilityPolicy, Conservative session eligibility policy for historical EDGAR filings. EDGAR…, extract_cover_page_os(), extract_restriction_clause_candidates(), extract_effect_event(), extract_registration_component_candidate(), extract_registration_scope_clause_candidates(), extract_selling_holder_share_lots() (+16 more)

### Community 17 - "Authorized Primary Acquisition Runner"
Cohesion: 0.15
Nodes (23): classify_acquisition_scope(), complete_submission_fallback_url(), completed_urls(), LowDiskStop, main(), parse_args(), persist_low_disk_stop(), Any (+15 more)

### Community 18 - "Stratified Owner-Exclusion Probe"
Cohesion: 0.19
Nodes (22): execute(), file_sha256(), has_role(), load_cases(), load_reusable_rows(), parse_args(), Any, DataFrame (+14 more)

### Community 19 - "Acquisition Authorization Validation"
Cohesion: 0.16
Nodes (19): AuthorizationDecision, FrozenTarget, Any, Path, Fail-closed configuration, target and human-authorization gates., read_json(), _reject_secret_material(), validate_authorization() (+11 more)

### Community 20 - "Owner-Exclusion Resolution Batch"
Cohesion: 0.14
Nodes (20): execute(), file_sha256(), parse_args(), Any, Namespace, Path, write_json(), SEC point-in-time fundamental evidence pipeline. (+12 more)

### Community 21 - "SEC PIT Authority Evidence"
Cohesion: 0.08
Nodes (24): Full-Universe Descending Preflight, 4,824 Descending Preflight, Adaptive Baseline Reconciliation, Adaptive Baseline Certification, V0.21 SEC PIT Authority, SEC PIT Dossier Handoff, Exact Share-Class Allocation, Exact Share-Class Recovery v0.21 (+16 more)

### Community 22 - "HTML Ownership Extraction"
Cohesion: 0.23
Nodes (20): _clean_name(), extract_html_ownership_snapshots(), _extract_proxy_tables(), _extract_schedule_cover_sheets(), _extract_schedule_xml(), _number(), _proxy_footnotes(), Any (+12 more)

### Community 23 - "Descending Acquisition Preflight"
Cohesion: 0.20
Nodes (19): atomic_json(), build_acquisition_order(), execute(), git_value(), parse_args(), powershell_commands(), Any, DataFrame (+11 more)

### Community 24 - "Owner-Exclusion Float Resolver"
Cohesion: 0.20
Nodes (18): _blocked_rows(), _person_name_key(), _post_baseline_adjustment(), _proxy_baselines(), Any, resolve_owner_exclusion_float(), Any, resolve_owner_exclusion_float_v0_2() (+10 more)

### Community 25 - "Companyfacts O/S Reconciliation Probe"
Cohesion: 0.19
Nodes (19): companyfacts_fetch_state(), execute(), parse_args(), persist_failure(), Any, Namespace, Path, read_reusable_companyfacts() (+11 more)

### Community 26 - "Instrument-Interval Recovery Audit"
Cohesion: 0.26
Nodes (18): _attributes_by_accession(), audit_case(), build_audit(), classify_case(), classify_unresolved_document(), is_common_equity_observation(), main(), normalize_cik() (+10 more)

### Community 27 - "Massive SEC Control Evidence"
Cohesion: 0.11
Nodes (20): Unexecuted Final Certification, Massive Final Certification Readout, Full Run Not Authorized, Massive Full-Run Authorization Readout, Massive Raw Vendor Evidence, Massive Structured Evidence Dataset Contract, Blocked Vendor Evidence Consumption, Massive Evidence Consumption Policy (+12 more)

### Community 28 - "Ownership Scale-Gate Decisions"
Cohesion: 0.10
Nodes (20): Normalized Ownership Headers, Ownership HTML Whitespace Certification, Ownership Aggregate Corrections, Identity Date Aggregate Loop, Causal Record Date Binding, Ownership Identity and Record Date Certification, Multi-Evidence O/S Anchors, O/S Multi-Evidence Shard Certification (+12 more)

### Community 29 - "Daily O/S Resolver Tests"
Cohesion: 0.18
Nodes (16): DailyOsState, owner_exclusion_estimate(), Any, resolve_daily_os(), observation(), test_candidate_cannot_produce_daily_os_state(), test_only_admitted_anchor_can_produce_daily_os_state(), Path (+8 more)

### Community 30 - "PGAC No-Network O/S Probe"
Cohesion: 0.23
Nodes (15): Any, reconcile_class_os_anchors(), extract_ixbrl_class_os(), execute(), parse_args(), Any, Namespace, Path (+7 more)

### Community 31 - "Acquisition Telemetry Utilities"
Cohesion: 0.21
Nodes (9): append_jsonl(), LiveResourceTelemetry, percentile(), process_tree_metrics(), Any, Path, summarize_document_performance(), utc_now() (+1 more)

### Community 32 - "Market Operations Snapshot Pipeline"
Cohesion: 0.26
Nodes (15): _fetch_all(), main(), materialize_snapshot(), _nested_bool(), normalize_conditions(), normalize_exchanges(), _parse_args(), Any (+7 more)

### Community 33 - "Sharded Variable Certification Audit"
Cohesion: 0.23
Nodes (14): audit_daily_frames(), execute(), parse_args(), Any, DataFrame, Namespace, Path, select_cases() (+6 more)

### Community 34 - "Hundred-Case Candidate Pool"
Cohesion: 0.23
Nodes (14): _action_counts(), build_frame(), cohort_for_year(), execute(), parse_args(), DataFrame, Namespace, Path (+6 more)

### Community 35 - "Multiclass Ownership Reconciliation"
Cohesion: 0.25
Nodes (14): _class_key(), _names_compatible(), Any, reconcile_multiclass_proxy_positions(), normalized_name_key(), proxy(), test_multiclass_management_aggregate_uses_exact_atomic_class_sum(), test_single_class_aggregate_does_not_resolve_when_atomic_totals_do_not_close() (+6 more)

### Community 36 - "Lifecycle Market-Presence Reconciliation"
Cohesion: 0.29
Nodes (15): cross_source_boundary_state(), daily_presence(), git_value(), main(), parse_args(), Any, Namespace, Path (+7 more)

### Community 37 - "Submissions Metadata Profiling"
Cohesion: 0.23
Nodes (14): execute(), file_sha256(), git_value(), parse_args(), profile_inventory(), Any, DataFrame, Namespace (+6 more)

### Community 38 - "SEC PIT Canonical Schemas"
Cohesion: 0.13
Nodes (16): Conditional Global 13F Evidence, Form 13F Schema, Insider Initial Ownership Evidence, Form 3 Schema, Insider Transaction Evidence, Form 4 Schema, Experimental SEC Fundamental Evidence, Fundamental Evidence Dataset Contract (+8 more)

### Community 39 - "Ownership Baseline Classification"
Cohesion: 0.23
Nodes (13): classify_baseline_document(), classify_missing_opening_baseline_blocker(), _observation_value(), Any, Classify why no opening baseline was selected without double-counting identity.…, Classify baseline usability from filing content, never from form alone., management_row(), test_annual_report_with_supported_management_table_is_candidate() (+5 more)

### Community 40 - "Lifecycle Metadata Lane Audit"
Cohesion: 0.31
Nodes (13): atomic_json(), candidate_type(), has_item(), main(), parse_args(), Any, DataFrame, Namespace (+5 more)

### Community 41 - "Historical CUSIP Materialization"
Cohesion: 0.26
Nodes (11): extract_cusips(), is_valid_cusip(), Any, resolve_cusip_intervals(), _hash(), main(), Path, _write() (+3 more)

### Community 42 - "Acquisition Ledger Merge"
Cohesion: 0.29
Nodes (12): merge_ledgers(), parse_args(), Any, Namespace, Path, sha256_file(), _write_json(), _write_jsonl() (+4 more)

### Community 43 - "SEC Acquisition Governance Evidence"
Cohesion: 0.16
Nodes (14): Acquisition Integrity Validators, Massive Acquisition Validators, Authorized Probe Operations, Massive Acquisition Operator Runbook, SEC Predownload Admission Validators, Predownload Control Validators, Receipt-Authoritative Handoff, Runtime Recovery and Handoff Contract (+6 more)

### Community 44 - "Massive Acquisition Telemetry"
Cohesion: 0.24
Nodes (5): append_jsonl_durable(), Append one complete record and force it to stable storage., MassiveSecTelemetry, Any, Path

### Community 45 - "Lifecycle Primary Acquisition Runner"
Cohesion: 0.32
Nodes (12): build_plan(), git_value(), load_completed_urls(), main(), parse_args(), DataFrame, Namespace, Path (+4 more)

### Community 46 - "O/S Unavailable Shard Audit"
Cohesion: 0.29
Nodes (10): audit_case(), execute(), parse_args(), Any, Namespace, Path, sha256_file(), shard_for() (+2 more)

### Community 47 - "Daily Balance-Sheet Context"
Cohesion: 0.32
Nodes (9): extract_balance_sheet_facts(), Any, resolve_daily_balance_sheet_context(), _unavailable_fields(), main(), Path, _write(), test_daily_resolver_is_causal_and_uses_same_measurement_vintage() (+1 more)

### Community 48 - "Hundred-Case Sample Freeze"
Cohesion: 0.26
Nodes (10): execute(), parse_args(), Any, DataFrame, Namespace, Path, sha256_file(), solve_sample() (+2 more)

### Community 49 - "Seven-Ticker Replay Pipeline"
Cohesion: 0.32
Nodes (11): atomic_json(), completed(), disk_free_gib(), main(), parser(), Any, ArgumentParser, Path (+3 more)

### Community 50 - "Download Authorization Validator"
Cohesion: 0.33
Nodes (9): AuthorizationDecision, file_sha256(), Path, Hash-bound authorization gate for SEC PIT primary-document acquisition., validate_download_authorization(), Path, test_authorization_cannot_include_a_security_class_halt(), test_authorization_is_bound_to_exact_gate_matrix_hash() (+1 more)

### Community 51 - "Class O/S Extraction Tests"
Cohesion: 0.45
Nodes (10): extract_cover_page_class_os_v0_2(), kwargs(), test_as_of_then_number_of_outstanding_shares_is_supported(), test_class_a_path_remains_exact_and_excludes_class_b(), test_common_stock_text_and_ixbrl_agree(), test_distinct_issued_and_outstanding_values_selects_outstanding(), test_issuable_under_outstanding_plan_is_not_an_os_anchor(), test_issued_and_outstanding_respectively_selects_outstanding() (+2 more)

### Community 52 - "Lockup Release Schedule"
Cohesion: 0.35
Nodes (9): extract_lockup_release_schedule(), _name(), _number(), Any, resolve_lockup_lot_on_session(), resolve_lockup_release_conditions(), test_adv_expiry_does_not_confirm_other_tradability_gates(), test_condition_confirmation_does_not_confirm_tradability() (+1 more)

### Community 53 - "Registration Restriction Conditions"
Cohesion: 0.36
Nodes (9): Any, Resolve registration effectiveness without asserting tradable supply., resolve_registration_component_conditions(), _component(), _effect(), test_effectiveness_does_not_confirm_issuance_or_tradability(), test_empty_component_input_is_blocked_not_passed(), test_missing_effect_remains_explicit() (+1 more)

### Community 54 - "Target-Interval Filing Review"
Cohesion: 0.33
Nodes (9): main(), Path, _review_fields(), run(), _sha256(), test_all_review_decisions_are_present_and_nonempty(), test_non_target_security_classes_are_explicit(), test_scheduled_transfer_requires_confirmation() (+1 more)

### Community 55 - "Owner-Exclusion Results Audit"
Cohesion: 0.38
Nodes (8): audit_matrix(), audit_run(), main(), Any, Path, sha256_file(), Path, test_audit_accepts_calculated_and_explicitly_blocked_rows()

### Community 56 - "August Funding Vintage Pipeline"
Cohesion: 0.36
Nodes (8): extract_august_funding_vintages(), _iso_date(), _number(), Any, reconcile_august_funding_vintages(), _extract(), test_extracts_separate_vintage_semantics(), test_reconciliation_keeps_first_public_vintage()

### Community 57 - "Composite Acquisition Ledger"
Cohesion: 0.42
Nodes (9): execute(), file_sha256(), parse_args(), Any, Namespace, Path, read_jsonl(), verify_row() (+1 more)

### Community 58 - "Metadata Lifecycle Ledger"
Cohesion: 0.31
Nodes (8): execute(), lifecycle_row(), parse_args(), DataFrame, Namespace, Path, sha256_file(), test_metadata_lifecycle_never_promotes_legal_dates()

### Community 59 - "Daily Change Explanation Pipeline"
Cohesion: 0.33
Nodes (7): build_daily_change_explanations(), _cusip_for_session(), Any, main(), Path, _write(), test_explains_split_and_cusip_transition()

### Community 60 - "Pilot O/S Materialization"
Cohesion: 0.36
Nodes (9): instrument_row(), materialize(), normalize_measurement_date(), parser(), ArgumentParser, Namespace, Path, sessions_for() (+1 more)

### Community 61 - "O/S Anchor Reconciliation"
Cohesion: 0.38
Nodes (8): _attributes(), _id(), Any, Admit only exact cross-extraction agreement for a point O/S fact. This v0.1…, reconcile_os_anchors(), candidate(), test_reconciliation_admits_exact_dei_and_primary_agreement(), test_reconciliation_rejects_disagreement_and_period_end_concept()

### Community 62 - "Registration-to-O/S Reconciliation"
Cohesion: 0.38
Nodes (8): Any, Check reported-current components against causal O/S capacity. A passing…, reconcile_registration_components_to_os(), _component(), _os(), test_capacity_consistency_never_confirms_inclusion_or_tradability(), test_component_exceeding_os_is_a_conflict(), test_missing_os_and_non_current_components_remain_explicit()

### Community 63 - "Acquisition Authorization Tests"
Cohesion: 0.67
Nodes (9): _authorized_value(), _decision(), _fixtures(), Path, test_authorization_is_bound_to_executable_bundle_hash(), test_conditional_endpoint_needs_separate_gate_evidence(), test_exact_probe_scope_can_pass(), test_license_and_retention_confirmation_is_mandatory() (+1 more)

### Community 64 - "Ownership Identity Tests"
Cohesion: 0.36
Nodes (9): _decision(), test_common_equity_title_filter_is_conservative(), test_explicit_other_issuer_is_rejected_not_left_unresolved(), test_missing_cik_name_linked_to_explicit_other_issuer_is_rejected(), test_missing_cik_proxy_requires_archive_continuity_and_common_equity(), test_missing_cik_with_explicit_other_class_cusip_is_rejected(), test_only_non_target_security_rows_are_rejected(), test_target_cik_and_common_equity_is_governed_continuity() (+1 more)

### Community 65 - "Assignment Schedule Linking"
Cohesion: 0.44
Nodes (7): extract_assignment_purchaser_schedule(), link_schedule_to_selling_lots(), _name(), _number(), Any, test_link_requires_identity_and_quantity(), test_schedule_preserves_and_resolves_reported_typo()

### Community 66 - "Ownership Identity Extraction"
Cohesion: 0.22
Nodes (9): extract_document_identity(), extract_name_change_events(), Element, _schedule_cover_value(), _xml_text(), test_name_change_extraction_accepts_real_filing_wording_and_curly_quotes(), test_name_change_extraction_is_generic(), test_schedule_html_cover_extracts_values_that_precede_labels() (+1 more)

### Community 67 - "Lifecycle Acquisition Audit"
Cohesion: 0.43
Nodes (6): load_object(), main(), parse_args(), Namespace, Path, Audit lifecycle primary-document acquisition outputs byte by byte.

### Community 68 - "Restriction Event Reconciliation"
Cohesion: 0.48
Nodes (5): Any, reconcile_assignment_restriction_events(), _row(), test_reconciliation_prefers_origin_8k_and_preserves_corroboration(), test_reconciliation_preserves_numeric_conflict()

### Community 69 - "Assignment Restriction Extraction"
Cohesion: 0.53
Nodes (4): extract_assignment_restriction_events(), _iso_date(), _number(), test_assignment_events_preserve_numeric_conflict_without_correction()

### Community 70 - "Overlap Recovery Audit"
Cohesion: 0.47
Nodes (5): execute(), parse_args(), Namespace, Path, shard_for()

### Community 71 - "August Funding Evidence Extraction"
Cohesion: 0.47
Nodes (4): extract_august_funding_evidence(), _number(), Any, test_two_share_contract_resolves_reported_aggregate()

### Community 72 - "Predownload Lifecycle Selection"
Cohesion: 0.47
Nodes (5): execute(), parse_args(), Namespace, Path, sha256_file()

### Community 73 - "Split-Adjusted O/S Alignment"
Cohesion: 0.47
Nodes (4): align_daily_os_to_splits(), Any, test_post_split_anchor_is_not_transformed_again(), test_pre_split_anchor_is_transformed_from_effective_session()

### Community 74 - "Class O/S V3 Tests"
Cohesion: 0.53
Nodes (5): extract(), test_residual_cover_layouts_are_class_and_date_bound(), test_residual_layout_does_not_admit_authorized_shares(), test_table_layout_does_not_capture_par_value(), parametrize

### Community 75 - "Lifecycle Market-Presence Tests"
Cohesion: 0.47
Nodes (4): Path, test_daily_presence_is_bounded_by_identity_window(), test_missing_tape_is_unavailable_not_zero(), test_trade_presence_preserves_naive_timestamp_semantics()

### Community 76 - "8-K Disclosure Schemas"
Cohesion: 0.33
Nodes (6): Structured 8-K Disclosures, 8-K Disclosures Schema, Conditional 8-K Text Evidence, 8-K Text Schema, Versioned Disclosure Taxonomy, Disclosure Taxonomy Schema

### Community 77 - "Form 3/4/5 Ownership Extraction"
Cohesion: 0.50
Nodes (5): extract_form345_owner_snapshot(), _find_text(), _footnote_texts(), Element, test_form4_xml_separates_derivatives()

### Community 79 - "Issuer Name Matching Tests"
Cohesion: 0.40
Nodes (5): issuer_name_present_in_text(), Match an issuer name in filing text without sorted-token adjacency., test_issuer_core_name_match_does_not_admit_a_different_issuer(), test_issuer_name_presence_does_not_depend_on_sorted_token_adjacency(), test_issuer_name_presence_ignores_vendor_security_and_jurisdiction_labels()

### Community 80 - "Market Operations Snapshot Tests"
Cohesion: 0.70
Nodes (4): _load_module(), Path, test_reference_snapshot_flattens_update_rules_without_losing_raw_json(), test_reference_snapshot_materializes_sanitized_versioned_artifacts()

## Knowledge Gaps
- **52 isolated node(s):** `Resolved Daily States Schema v0.1`, `Resolved Daily States Schema v0.2`, `Source Observations Schema v0.1`, `Disclosure Taxonomy Schema`, `EDGAR Index Schema` (+47 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EdgarAvailabilityPolicy` connect `Restriction Evidence Extraction` to `Atomic SEC Storage Layer`, `No-Network Share Admission Probe`, `Assignment Restriction Extraction`, `Ownership Extraction Test Suite`, `Presession Market-Cap Pipeline`, `SEC Observation Extraction Core`, `Class O/S V3 Tests`, `Ownership Snapshot Parser`, `Form 3/4/5 Ownership Extraction`, `Owner-Exclusion Identity Probe`, `Single-Ticker SEC Pilot`, `Class O/S Extraction Tests`, `HTML Ownership Extraction`, `Companyfacts O/S Reconciliation Probe`, `Pilot O/S Materialization`, `Daily O/S Resolver Tests`, `PGAC No-Network O/S Probe`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `atomic_write_json()` connect `Atomic SEC Storage Layer` to `Cohort Metadata Gate Pipeline`, `Lifecycle Acquisition Audit`, `Lifecycle Market-Presence Reconciliation`, `Submissions Metadata Profiling`, `Authorized Acquisition Audit`, `Lifecycle Document Extraction Pipeline`, `Massive SEC Acquisition Runner`, `Massive Acquisition Telemetry`, `Lifecycle Primary Acquisition Runner`, `Single-Ticker SEC Pilot`, `Authorized Primary Acquisition Runner`, `Owner-Exclusion Resolution Batch`, `Companyfacts O/S Reconciliation Probe`, `Pilot O/S Materialization`, `Acquisition Telemetry Utilities`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `extract_normalized_ownership_snapshots()` connect `Ownership Extraction Test Suite` to `Ownership Identity Extraction`, `SEC Observation Extraction Core`, `Ownership Snapshot Parser`, `Form 3/4/5 Ownership Extraction`, `Owner-Exclusion Identity Probe`, `Restriction Evidence Extraction`, `HTML Ownership Extraction`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `EdgarAvailabilityPolicy` (e.g. with `InstrumentAdmissionDecision` and `InstrumentAdmissionDecision`) actually correct?**
  _`EdgarAvailabilityPolicy` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Resolved Daily States Schema v0.1`, `Resolved Daily States Schema v0.2`, `Source Observations Schema v0.1` to the rest of the system?**
  _52 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Cohort Metadata Gate Pipeline` be split into smaller, more focused modules?**
  _Cohesion score 0.05132788559754852 - nodes in this community are weakly interconnected._
- **Should `Atomic SEC Storage Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.0629800307219662 - nodes in this community are weakly interconnected._