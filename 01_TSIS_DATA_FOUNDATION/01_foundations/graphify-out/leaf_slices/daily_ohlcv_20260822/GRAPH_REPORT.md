# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 84 files · ~116,026 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 251 nodes · 325 edges · 23 communities
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Minute Implementation Governance
- Daily Adjusted Returns
- Quote-Guarded Minute Repair
- Daily Recovery Certification
- Master Bar Tables
- Split-Normalized Audit
- Minute Schema Views
- Master Daily Consumption
- Intraday View Consumption
- Raw Minute Inspection
- Daily Quality Taxonomy
- Daily Validator System
- Daily Evidence Dossiers
- Price View Governance
- Raw Minute Consumption
- Daily Inspection Readout
- Schema Audit Proposals
- Daily Audit Implementation
- Daily Coverage Cases
- Split-Normalized Validators
- Restricted Daily Universe
- Daily Good Cases
- Daily Audit Maintenance

## God Nodes (most connected - your core abstractions)
1. `Quote-Guarded Single Reading` - 6 edges
2. `Quote-Guarded Governance` - 6 edges
3. `Daily Recovery and Coverage` - 6 edges
4. `Daily Adjusted v0.1` - 5 edges
5. `Daily Return Labels v0.1` - 5 edges
6. `Expected Data Calendar` - 5 edges
7. `Master Daily Consumption` - 5 edges
8. `Master Intraday Consumption` - 5 edges
9. `Quote-Guarded Consumption` - 5 edges
10. `Split-Normalized Final Readout` - 5 edges

## Surprising Connections (you probably didn't know these)
- `VWAP Illiquidity Residue` --semantically_similar_to--> `VWAP Severity Taxonomy`  [INFERRED] [semantically similar]
  01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/02_1m_quality_policy.md
- `Raw Observed Price Scale` --semantically_similar_to--> `Cross-Session Scale Comparability`  [INFERRED] [semantically similar]
  01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md
- `Daily Registry` --conceptually_related_to--> `Master Daily Consumption`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/daily/daily_registry_entry.yaml → 01_TSIS_DATA_FOUNDATION/01_foundations/data_consumption_policies/master_daily_table_consumption_policy.md
- `Daily Return Labels Registry` --conceptually_related_to--> `Master Daily Consumption`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/daily/daily_return_labels_registry_entry.yaml → 01_TSIS_DATA_FOUNDATION/01_foundations/data_consumption_policies/master_daily_table_consumption_policy.md
- `Quote-Guarded Registry` --references--> `Quote-Guarded Consumption`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_quote_guarded_registry_entry.yaml → 01_TSIS_DATA_FOUNDATION/01_foundations/data_consumption_policies/ohlcv_1m_quote_guarded_consumption_policy.md

## Hyperedges (group relationships)
- **Daily Price View Family** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_daily_dataset_contract_v0_1_daily_core_v0_1, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_daily_adjusted_dataset_contract_v0_1_daily_adjusted_v0_1, 01_tsis_data_foundation_01_foundations_data_consumption_policies_daily_adjusted_consumption_policy_raw_adjusted_separation, 01_tsis_data_foundation_01_foundations_canonical_schemas_daily_daily_adjusted_schema_contract_economic_daily_continuity [INFERRED 0.95]
- **Minute Price View Family** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_ohlcv_1m_raw_dataset_contract_v0_1_ohlcv_1m_raw_v0_1, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_ohlcv_1m_quote_guarded_dataset_contract_v0_1_quote_guarded_minute_view, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_ohlcv_1m_split_normalized_dataset_contract_v0_1_ohlcv_1m_split_normalized_v0_1, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_ohlcv_1m_raw_dataset_contract_v0_1_raw_observed_price_scale, 01_tsis_data_foundation_01_foundations_canonical_schemas_ohlcv_1m_ohlcv_1m_split_normalized_schema_contract_cross_session_scale_comparability [INFERRED 0.95]
- **Daily State Input Boundaries** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_daily_scanner_candidates_table_dataset_contract_v0_1_daily_scanner_candidates_table, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_expected_data_calendar_dataset_contract_v0_1_expected_data_calendar, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_master_daily_table_dataset_contract_v0_1_master_daily_table, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_master_intraday_bar_table_dataset_contract_v0_1_master_intraday_bar_table, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_daily_return_labels_dataset_contract_v0_1_daily_return_labels_v0_1 [INFERRED 0.85]
- **Intraday Price View Governance** — 01_tsis_data_foundation_01_foundations_data_consumption_policies_ohlcv_1m_raw_consumption_policy_raw_minute_consumption, 01_tsis_data_foundation_01_foundations_data_consumption_policies_ohlcv_1m_quote_guarded_consumption_policy_quote_guarded_consumption, 01_tsis_data_foundation_01_foundations_data_consumption_policies_ohlcv_1m_split_normalized_consumption_policy_split_normalized_consumption, 01_tsis_data_foundation_01_foundations_data_consumption_policies_master_intraday_bar_table_consumption_policy_master_intraday_consumption [INFERRED 0.95]
- **Split-Normalized Evidence Chain** — 01_tsis_data_foundation_01_foundations_dataset_registry_ohlcv_1m_ohlcv_1m_split_normalized_pilot_manifest_v0_1_split_normalized_pilot_manifest, 01_tsis_data_foundation_01_foundations_inspection_dossiers_1m_split_normalized_ohlcv_1m_split_normalized_pilot_readout_v0_1_split_semantic_pilot, 01_tsis_data_foundation_01_foundations_inspection_dossiers_1m_split_normalized_ohlcv_1m_split_normalized_full_universe_audit_readout_v0_1_split_full_universe_audit, 01_tsis_data_foundation_01_foundations_inspection_dossiers_1m_split_normalized_event_case_evidence_packs_ohlcv_1m_split_normalized_visual_inspector_pack_v0_1_split_visual_inspection, 01_tsis_data_foundation_01_foundations_inspection_dossiers_1m_split_normalized_ohlcv_1m_split_normalized_final_readout_v0_1_split_normalized_final_readout, 01_tsis_data_foundation_01_foundations_dataset_registry_ohlcv_1m_ohlcv_1m_split_normalized_registry_entry_split_normalized_registry [INFERRED 0.95]
- **Daily Inspection Evidence Chain** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_build_daily_inspection_pack_daily_inspection_pack_builder, 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_daily_adjusted_full_universe_audit_v0_1_daily_adjusted_full_universe_audit, 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_daily_adjusted_complex_corporate_actions_tail_audit_v0_1_complex_corporate_actions_tail, 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_daily_inspection_readout_v0_1_daily_inspection_readout, 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_daily_inspection_readout_v0_1_daily_final_quality_states [INFERRED 0.95]
- **Daily Case Evidence Classes** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_bad_case_evidence_packs_daily_hard_invalid_cases_v0_1_hard_invalid_daily_cases, 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_flagged_case_evidence_packs_daily_non_good_quality_cases_v0_1_daily_non_good_cases, 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_good_justification_daily_good_cases_v0_1_daily_good_cases, 01_tsis_data_foundation_01_foundations_inspection_dossiers_daily_coverage_case_evidence_packs_daily_coverage_cases_v0_1_daily_coverage_cases, 01_tsis_data_foundation_01_foundations_validators_daily_daily_validators_daily_validator_system [INFERRED 0.95]
- **Quote-Guarded Operating System** — 01_tsis_data_foundation_01_foundations_module_contracts_ohlcv_1m_quote_guarded_ohlcv_1m_quote_guarded_single_reading_v0_1_quote_guarded_single_reading, 01_tsis_data_foundation_01_foundations_module_contracts_ohlcv_1m_quote_guarded_ohlcv_1m_quote_guarded_repair_runbook_v0_1_quote_guarded_repair_runbook, 01_tsis_data_foundation_01_foundations_module_contracts_ohlcv_1m_quote_guarded_ohlcv_1m_quote_guarded_live_supervision_validation_protocol_v0_1_quote_guarded_live_supervision, 01_tsis_data_foundation_01_foundations_module_contracts_ohlcv_1m_quote_guarded_ohlcv_1m_quote_guarded_lt1b_scope_recovery_protocol_v0_1_quote_guarded_scope_recovery, 01_tsis_data_foundation_01_foundations_module_contracts_ohlcv_1m_quote_guarded_readme_quote_guarded_governance, 01_tsis_data_foundation_01_foundations_module_contracts_ohlcv_1m_quote_guarded_readme_promoted_repair_manifest [INFERRED 0.95]
- **Price View Authority Stack** — 01_tsis_data_foundation_01_foundations_module_contracts_market_session_scope_market_session_scope, 01_tsis_data_foundation_01_foundations_module_contracts_pipeline_price_view_policy_pipeline_price_view_policy, 01_tsis_data_foundation_01_foundations_module_contracts_price_semantics_and_adjustment_policy_price_semantics_policy, 01_tsis_data_foundation_01_foundations_module_contracts_price_views_registry_price_views_registry, 01_tsis_data_foundation_01_foundations_module_contracts_ohlcv_1m_quote_guarded_ohlcv_1m_quote_guarded_single_reading_v0_1_immutable_raw_overlay [INFERRED 0.85]
- **Daily Audit Certification Lifecycle** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_daily_00_auditoria_daily_daily_audit_proposal, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_daily_01_contrato_agent02_agent03_daily_04032026_daily_agent_audit_contract, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_daily_02_diseno_implementacion_daily_v2_daily_v2_implementation, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_daily_04_daily_closeout_daily_audit_closeout, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_00_daily_current_state_daily_current_state, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_02_daily_quality_policy_daily_quality_policy, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_01_daily_recovery_and_coverage_daily_recovery_coverage, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_03_daily_closeout_daily_certification_closeout [INFERRED 0.95]
- **Minute Audit Certification Lifecycle** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_ohlcv_1m_00_auditoria_ohlcv_1m_minute_audit_proposal, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_ohlcv_1m_01_contrato_agent02_agent03_ohlcv_1m_04032026_minute_agent_audit_contract, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_ohlcv_1m_02_diseno_implementacion_ohlcv_1m_v2_minute_v2_implementation, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_ohlcv_1m_04_ohlcv_1m_closeout_minute_audit_closeout, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_1m_00_1m_current_state_minute_current_state, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_1m_01_1m_recovery_policy_minute_recovery_policy, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_1m_02_1m_quality_policy_minute_quality_policy, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_1m_03_1m_closeout_minute_certification_closeout [INFERRED 0.95]
- **Daily Final Policy Axes** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_00_daily_current_state_daily_bar_quality_axis, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_00_daily_current_state_daily_coverage_axis, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_02_daily_quality_policy_recoverable_vwap_residue, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_01_daily_recovery_and_coverage_likely_valid_gap_only, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_01_daily_recovery_and_coverage_ambiguous_coverage_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_01_daily_recovery_and_coverage_problematic_unexpected_coverage, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_daily_03_daily_closeout_five_state_daily_policy [INFERRED 0.95]

## Communities (23 total, 0 thin omitted)

### Community 0 - "Minute Implementation Governance"
Cohesion: 0.13
Nodes (21): OHLCV 1m Agent02-Agent03 Audit Contract, Minute Agent Audit Contract, Ticker-Month Audit Unit, OHLCV 1m v2 Implementation Design, Incremental Minute Audit Artifacts, Minute v2 Implementation, OHLCV 1m Audit Closeout, Minute Audit Closeout (+13 more)

### Community 1 - "Daily Adjusted Returns"
Cohesion: 0.15
Nodes (19): Adjustment Provenance, Daily Adjusted Schema, Daily Adjusted Schema Contract, Economic Daily Continuity, Daily Return Label Schema, Daily Return Labels Schema Contract, Forward Return Outcomes, Daily Adjusted v0.1 (+11 more)

### Community 2 - "Quote-Guarded Minute Repair"
Cohesion: 0.16
Nodes (19): Market Session Scope, Extended-Hours Boundary, Market Session Scope, Quote-Guarded Live Supervision Validation Protocol v0.1, Long-Run Validation, Quote-Guarded Live Supervision, Quote-Guarded LT1B Scope Recovery Protocol v0.1, LT1B Manifest Reconciliation (+11 more)

### Community 3 - "Daily Recovery Certification"
Cohesion: 0.18
Nodes (19): Daily Audit Closeout, Daily Hard-Invalid Tail, Daily Audit Closeout, VWAP Illiquidity Residue, Daily Bar Quality Axis, Daily Coverage Axis, Daily Current State, Daily Current State (+11 more)

### Community 4 - "Master Bar Tables"
Cohesion: 0.15
Nodes (18): Candidate Is Not State, Daily Scanner Candidates Table, Daily Scanner Candidates Table Dataset Contract v0.1, Expected Data Calendar Dataset Contract v0.1, Expected Data Calendar, Expectedness Is Not Presence, Daily State Component, Master Daily Table Dataset Contract v0.1 (+10 more)

### Community 5 - "Split-Normalized Audit"
Cohesion: 0.15
Nodes (17): Balanced Split Event Controls, OHLCV 1m Split-Normalized Pilot Manifest v0.1, Split-Normalized Pilot Manifest, OHLCV 1m Split-Normalized Visual Inspector Pack v0.1, Split Visual Inspection, Do-Not-Touch Marker, Split-Normalized Do-Not-Touch Marker, OHLCV 1m Split-Normalized Final Readout v0.1 (+9 more)

### Community 6 - "Minute Schema Views"
Cohesion: 0.18
Nodes (15): OHLCV 1m Schema Contract, Minute Physical Aliases, Raw Minute-Bar Schema, Cross-Session Scale Comparability, OHLCV 1m Split-Normalized Schema Contract, Split-Normalized Minute Schema, OHLCV 1m Quote-Guarded Dataset Contract v0.1, Quote-Evidence Repair (+7 more)

### Community 7 - "Master Daily Consumption"
Cohesion: 0.16
Nodes (15): Master Daily Table Consumption Policy, Explicit Daily Price View, Master Daily Consumption, Daily Adjusted Registry, Daily Adjusted Registry Entry, Daily Registry, Daily Registry Entry, Daily Return Labels Registry (+7 more)

### Community 8 - "Intraday View Consumption"
Cohesion: 0.19
Nodes (15): Master Intraday Bar Table Consumption Policy, Master Intraday Consumption, Scoped Intraday Surface, Candidate, Not Institutional Default, OHLCV 1m Quote-Guarded Consumption Policy, Quote-Guarded Consumption, Repair Provenance Gate, OHLCV 1m Split-Normalized Consumption Policy (+7 more)

### Community 9 - "Raw Minute Inspection"
Cohesion: 0.21
Nodes (13): Minute Core Quality Visual Cases v0.1, Minute Core Quality Visual Cases, Raw 1m LT1B Closeout Recalculation v0.1, Raw Minute LT1B Recalculation, Raw Minute Quality Distribution, Raw 1m Schema-Only LT1B Inspection Readout v0.1, Schema-Only Minute Inspection, Schema Rescue Boundary (+5 more)

### Community 10 - "Daily Quality Taxonomy"
Cohesion: 0.21
Nodes (12): Daily Hard-Invalid Rules, Daily Schema Contract, Raw Daily Bar Schema, Daily Core v0.1, Daily Dataset Contract v0.1, Institutional Daily Bar, Bar Quality and Coverage Axes, Daily Quality Cut Taxonomy (+4 more)

### Community 11 - "Daily Validator System"
Cohesion: 0.31
Nodes (9): Daily Hard Invalid Cases v0.1, Hard-Invalid Daily Cases, Zero-OHLC Invalidation, Daily Non-Good Cases, Daily Non-Good Quality Cases v0.1, Recoverable with Flag, Daily Validator System, Daily Validators (+1 more)

### Community 12 - "Daily Evidence Dossiers"
Cohesion: 0.32
Nodes (8): Daily Adjusted Dossier, Daily Adjusted Inspection Dossier, Daily Inspection Dossier, Daily Inspection Dossier, Institutional Daily Evidence, Adjusted Hard-Failure Gates, Daily Adjusted Validator System, Daily Adjusted Validators v0.1

### Community 13 - "Price View Governance"
Cohesion: 0.32
Nodes (8): Declared Price View, Pipeline Price View Policy, Pipeline Price View Policy, Price Semantics and Adjustment Policy, Price Semantics and Adjustment Policy, Raw, Split, and Adjusted Separation, Price Views Registry, Price Views Registry

### Community 14 - "Raw Minute Consumption"
Cohesion: 0.43
Nodes (7): OHLCV 1m Raw Consumption Policy, Raw Minute Consumption, Raw Minute Quality Filters, VWAP Quality Debt, OHLCV 1m Raw Registry Entry, Institutional Raw Closeout, Raw Minute Registry

### Community 15 - "Daily Inspection Readout"
Cohesion: 0.43
Nodes (7): Daily Inspection Pack Builder, Daily Quality-Coverage Separation, Build Daily Inspection Pack, Daily Final Quality States, Daily Inspection Readout, Daily Inspection Readout v0.1, Visual-Certification Boundary

### Community 16 - "Schema Audit Proposals"
Cohesion: 0.47
Nodes (6): Daily Audit Proposal, Daily Audit Proposal v2, File and Dataset Schema Distinction, OHLCV 1m Audit Proposal v2, Minute Audit Proposal, Minute File-Dataset Schema Distinction

### Community 17 - "Daily Audit Implementation"
Cohesion: 0.47
Nodes (6): Daily Agent Audit Contract, Daily Agent02-Agent03 Audit Contract, Ticker-Year Audit Unit, Daily v2 Implementation, Daily v2 Implementation Design, Incremental Daily Audit Artifacts

### Community 18 - "Daily Coverage Cases"
Cohesion: 0.83
Nodes (4): Aligned Cross-Dataset Gaps, Daily Coverage Cases, Daily Coverage Cases v0.1, Moderate Coverage Misalignment

### Community 19 - "Split-Normalized Validators"
Cohesion: 0.83
Nodes (4): OHLCV 1m Split-Normalized Validators v0.1, Inherited Raw Limitations, Split-Event Invariants, Split-Normalized Validator System

### Community 20 - "Restricted Daily Universe"
Cohesion: 1.00
Nodes (3): Daily Eligible Universe Restricted Research Policy v0.1, Hash-Bound A/B Population, Restricted Daily Universe Proxy

### Community 21 - "Daily Good Cases"
Cohesion: 1.00
Nodes (3): Daily Good Cases, Defensible Daily Bars, Daily Good Cases v0.1

### Community 22 - "Daily Audit Maintenance"
Cohesion: 1.00
Nodes (3): Daily Audit Maintenance, Daily Audit Local Maintenance, Historical Semantics Preserved

## Ambiguous Edges - Review These
- `Do-Not-Touch Marker` → `Split-Normalized Inspection Dossier`  [AMBIGUOUS]
  01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/1m_split_normalized/NOTOCAR.md · relation: rationale_for

## Knowledge Gaps
- **13 isolated node(s):** `Institutional Daily Bar`, `Daily Adjusted Registry Entry`, `Daily Registry Entry`, `Daily Return Labels Registry Entry`, `OHLCV 1m Quote-Guarded Registry Entry` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Do-Not-Touch Marker` and `Split-Normalized Inspection Dossier`?**
  _Edge tagged AMBIGUOUS (relation: rationale_for) - confidence is low._
- **Why does `Daily Hard-Invalid Tail` connect `Daily Recovery Certification` to `Minute Implementation Governance`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `Daily Audit Closeout` connect `Daily Recovery Certification` to `Daily Audit Implementation`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **What connects `Institutional Daily Bar`, `Daily Adjusted Registry Entry`, `Daily Registry Entry` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Minute Implementation Governance` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `Daily Adjusted Returns` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._