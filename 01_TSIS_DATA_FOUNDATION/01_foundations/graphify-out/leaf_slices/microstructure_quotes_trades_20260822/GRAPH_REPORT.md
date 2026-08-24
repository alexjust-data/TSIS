# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 120 files · ~292,730 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 357 nodes · 480 edges · 28 communities (27 shown, 1 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef81564b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Trade Casepack Evidence
- Trade Label Taxonomy
- Microstructure Schema Contracts
- Population Inspection Dossiers
- Quote Quality Certification
- Trade Recovery Synthesis
- Intraday Regime Features
- Trade Recovery Policy
- RAW Alignment Handoffs
- Quotes Validator Governance
- Quote Casepack Audit
- Trades Audit Implementation
- Trades Certification Closeout
- Controlled Microstructure Windows
- Alignment Recovery Tooling
- Trades Validator System
- Quotes Artifact Mapping
- RAW Alignment Audit
- Quotes Consumption Policy
- Trades Consumption Policy
- Quotes Audit Architecture
- Quotes Good Cases
- Stratified Trade Sampling
- Regime Materialization Coverage
- Regime Boundary Cases
- Regime Good Cases
- Regime Validator System
- Trades CTO Audit

## God Nodes (most connected - your core abstractions)
1. `Trades Recovery Synthesis` - 10 edges
2. `Trades Certification Closeout` - 10 edges
3. `Trade Family Casepack Index` - 8 edges
4. `Distinct Trade Label Families` - 8 edges
5. `Final Trades Recovery Policy` - 8 edges
6. `Good, Review, and Bad Quote Quality` - 7 edges
7. `Quotes Open-Bucket Disposition` - 7 edges
8. `Good, Review, and Bad Certification Mapping` - 7 edges
9. `Microstructure Recovery` - 7 edges
10. `Intraday Regime Features v0.1` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Certified Quote Usage Policy` --semantically_similar_to--> `Provisional Trade Certification`  [INFERRED] [semantically similar]
  01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/04_quotes_usage_policy.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/04_trades_provisional_cert_policy.md
- `Microstructure Review` --semantically_similar_to--> `Persistent Soft-Crossed Review`  [INFERRED] [semantically similar]
  01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/06_trades_review_microstructure.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/08_persistent_soft_crossed_mid_large_scale.md
- `Bad-Data Trade Family` --semantically_similar_to--> `Medium-File Hard-Cross Bad`  [INFERRED] [semantically similar]
  01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/08_trades_bad_data.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/10_medium_file_threshold_edge_hard_many_crosses.md
- `Intraday Regime Registry` --references--> `Intraday Regime Features v0.1`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/dataset_registry/features/intraday_regime_features_registry_entry.yaml → 01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/intraday_regime_features_dataset_contract_v0_1.md
- `Split-Protected Regime State` --conceptually_related_to--> `Scoped State Sample`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/intraday_regime_features_dataset_contract_v0_1.md → 01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/microstructure_features_table_dataset_contract_v0_1.md

## Hyperedges (group relationships)
- **Microstructure Raw Authorities** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_quotes_dataset_contract_v0_1_quotes_core_v0_1, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_quotes_dataset_contract_v0_1_primary_book_authority, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_trades_dataset_contract_v0_1_trades_core_v0_1, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_trades_dataset_contract_v0_1_primary_tape_authority [INFERRED 0.95]
- **Intraday Feature Pilot Chain** — 01_tsis_data_foundation_01_foundations_canonical_schemas_features_intraday_regime_features_schema_contract_intraday_regime_feature_schema, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_intraday_regime_features_dataset_contract_v0_1_intraday_regime_features_v0_1, 01_tsis_data_foundation_01_foundations_inspection_dossiers_intraday_regime_features_intraday_regime_features_semantic_pilot_readout_v0_1_intraday_regime_semantic_pilot, 01_tsis_data_foundation_01_foundations_inspection_dossiers_intraday_regime_features_readme_intraday_regime_dossier, 01_tsis_data_foundation_01_foundations_inspection_dossiers_intraday_regime_features_bad_case_evidence_packs_intraday_regime_features_production_boundary_v0_1_intraday_regime_production_boundary [INFERRED 0.95]
- **Microstructure Quality Governance** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_quotes_label_taxonomy_and_cut_policy_quotes_cut_taxonomy, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_trades_label_taxonomy_and_cut_policy_trades_cut_taxonomy, 01_tsis_data_foundation_01_foundations_data_consumption_policies_quotes_consumption_policy_quotes_consumption, 01_tsis_data_foundation_01_foundations_data_consumption_policies_trades_consumption_policy_trades_consumption, 01_tsis_data_foundation_01_foundations_inspection_dossiers_core_market_raw_alignment_audit_core_market_raw_alignment_audit_probe_readout_v0_1_raw_alignment_probe [INFERRED 0.85]
- **Intraday Feature Case Evidence** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_intraday_regime_features_coverage_case_evidence_packs_intraday_regime_features_materialization_coverage_v0_1_regime_feature_pilot_coverage, 01_tsis_data_foundation_01_foundations_inspection_dossiers_intraday_regime_features_flagged_case_evidence_packs_intraday_regime_features_lookback_and_boundary_cases_v0_1_lookback_boundary_cases, 01_tsis_data_foundation_01_foundations_inspection_dossiers_intraday_regime_features_good_justification_intraday_regime_features_semantic_pilot_good_cases_v0_1_regime_feature_good_cases, 01_tsis_data_foundation_01_foundations_inspection_dossiers_intraday_regime_features_good_justification_intraday_regime_features_semantic_pilot_good_cases_v0_1_split_neutralization_controls [INFERRED 0.95]
- **Quotes Inspection Evidence Chain** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_quotes_build_quotes_inspection_pack_quotes_inspection_builder, 01_tsis_data_foundation_01_foundations_inspection_dossiers_quotes_quotes_inspection_readout_v0_1_quotes_inspection_readout, 01_tsis_data_foundation_01_foundations_inspection_dossiers_quotes_quotes_open_casepacks_audit_v0_1_quotes_open_casepack_audit, 01_tsis_data_foundation_01_foundations_inspection_dossiers_quotes_good_justification_quotes_good_cases_v0_1_quotes_good_cases, 01_tsis_data_foundation_01_foundations_inspection_dossiers_quotes_flagged_case_evidence_packs_quotes_review_cases_v0_1_quotes_review_cases, 01_tsis_data_foundation_01_foundations_inspection_dossiers_quotes_bad_case_evidence_packs_quotes_bad_cases_v0_1_quotes_bad_cases, 01_tsis_data_foundation_01_foundations_inspection_dossiers_quotes_readme_quotes_inspection_dossier [INFERRED 0.95]
- **Trades Population Inspection Chain** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_build_trades_inspection_pack_trades_inspection_builder, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_trades_global_universe_readout_v0_1_trades_global_universe, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_trades_inspection_readout_v0_1_trades_inspection_readout, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_readme_trades_inspection_dossier, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_trades_inspection_readout_v0_1_strict_review_rehabilitation [INFERRED 0.95]
- **Trade Acceptance Family System** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_family_case_evidence_packs_bad_data_bad_data_cases_v0_1_bad_data_family, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_family_case_evidence_packs_good_good_cases_v0_1_good_trade_family, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_family_case_evidence_packs_reference_scale_mismatch_reference_scale_mismatch_cases_v0_1_reference_scale_mismatch_family, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_family_case_evidence_packs_review_review_cases_v0_1_generic_review_family, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_family_case_evidence_packs_review_1m_reference_alignment_review_1m_reference_alignment_cases_v0_1_review_1m_alignment_family, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_family_case_evidence_packs_review_microstructure_review_microstructure_cases_v0_1_review_microstructure_family, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_family_case_evidence_packs_review_no_1m_reference_review_no_1m_reference_cases_v0_1_review_no_1m_family [EXTRACTED 1.00]
- **Trade Evidence Sampling Chain** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_trades_sampling_strategy_v0_1_stratified_trade_sampling, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_file_acceptance_evidence_packs_trades_file_acceptance_readout_v0_1_trade_file_acceptance, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_population_evidence_packs_trades_population_readout_v0_1_trades_population_evidence, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_flagged_case_evidence_packs_trades_review_cases_v0_1_trades_review_casepack, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_good_justification_trades_good_cases_v0_1_trades_good_justification, 01_tsis_data_foundation_01_foundations_inspection_dossiers_trades_bad_case_evidence_packs_trades_bad_cases_v0_1_trades_bad_boundary [INFERRED 0.95]
- **RAW Alignment Handoff Lifecycle** — 01_tsis_data_foundation_01_foundations_module_contracts_core_market_raw_alignment_audit_core_market_raw_alignment_audit_handoff_v0_1_raw_alignment_design_handoff, 01_tsis_data_foundation_01_foundations_module_contracts_core_market_raw_alignment_audit_core_market_raw_alignment_audit_handoff_v0_2_raw_alignment_probe_handoff, 01_tsis_data_foundation_01_foundations_module_contracts_core_market_raw_alignment_audit_core_market_raw_alignment_audit_handoff_v0_3_raw_alignment_recovery_handoff, 01_tsis_data_foundation_01_foundations_module_contracts_core_market_raw_alignment_audit_changelog_raw_alignment_changelog, 01_tsis_data_foundation_01_foundations_module_contracts_core_market_raw_alignment_audit_core_market_raw_alignment_audit_handoff_v0_3_session_date_correction [INFERRED 0.95]
- **Quotes Audit Certification Lifecycle** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_quotes_v1_00_auditoria_quotes_quotes_audit_proposal, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_quotes_v1_01_contrato_agent02_agent03_03312026_quotes_agent_contract, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_quotes_v1_02_diseno_arquitectura_quotes_cd_quotes_cd_architecture, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_quotes_v2_04_quotes_full_c_d_methodology_quotes_cd_methodology, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_quotes_v2_04_quotes_full_c_d_closeout_quotes_cd_closeout, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_00_quotes_certification_guide_quotes_certification_guide, 01_tsis_data_foundation_01_foundations_validators_quotes_quotes_validators_quotes_validator_system [INFERRED 0.95]
- **Trades Audit Acceptance Lifecycle** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_trades_v1_00_auditoria_trades_trades_audit_proposal, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_trades_v1_01_contrato_agent02_agent03_trades_04012026_trades_agent_contract, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_trades_v1_02_diseno_implementacion_trades_v2_trades_v2_implementation, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_trades_v2_03_diseno_implementacion_trades_cd_trades_cd_implementation, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_trades_v2_04_trades_full_c_d_notebook_trades_cd_population_notebook, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_trades_v2_05_trades_file_acceptance_notebook_trades_file_acceptance_notebook, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_trades_full_lt1b_57f_final_readout_trades_57f_final_readout [INFERRED 0.95]
- **RAW Alignment Operational Controls** — 01_tsis_data_foundation_01_foundations_module_contracts_core_market_raw_alignment_audit_quotes_worker_acceleration_runbook_v0_1_quotes_worker_acceleration, 01_tsis_data_foundation_01_foundations_module_contracts_core_market_raw_alignment_audit_quotes_worker_acceleration_runbook_v0_1_transactional_worker_claiming, 01_tsis_data_foundation_01_foundations_validators_core_market_raw_alignment_audit_core_market_raw_alignment_audit_validators_v0_1_raw_alignment_validator_system, 01_tsis_data_foundation_01_foundations_validators_core_market_raw_alignment_audit_core_market_raw_alignment_audit_validators_v0_1_operational_manifest_gates [INFERRED 0.95]
- **Quotes Certification Assembly** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_02_quotes_expected_presence_logic_expected_presence_logic, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_03_quotes_quality_policy_good_review_bad_quality, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_05_quotes_artifact_mapping_existing_artifact_mapping, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_06_quotes_cert_table_spec_ticker_date_certification_table, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_07_quotes_local_certification_build_plan_local_certification_build, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_04_quotes_usage_policy_certified_quote_usage_policy [INFERRED 0.95]
- **Quotes Open-Bucket Disposition** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_08_persistent_soft_crossed_mid_large_scale_persistent_soft_crossed_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_09_large_file_threshold_edge_hard_many_crosses_large_file_threshold_edge_mixed_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_10_medium_file_threshold_edge_hard_many_crosses_medium_file_hard_cross_bad, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_11_high_hard_crossed_10_to_20_high_hard_cross_bad, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_quotes_12_quotes_open_buckets_synthesis_open_bucket_disposition [EXTRACTED 1.00]
- **Trades Acceptance Taxonomy** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_01_trades_label_assessment_distinct_trade_label_families, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_03_trades_old_vs_new_bucket_bridge_amplitude_acceptance_bridge, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_04_trades_provisional_cert_policy_provisional_trade_certification, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_05_trades_review_1m_reference_alignment_review_1m_reference_alignment, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_06_trades_review_microstructure_review_microstructure, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_07_trades_reference_scale_mismatch_reference_scale_mismatch, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_08_trades_bad_data_bad_data_family, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_09_trades_review_no_1m_reference_review_no_1m_reference [INFERRED 0.95]
- **Trades Bucket Certification Map** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_12_trades_good_good_bucket, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_11_trades_review_generic_generic_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_10_trades_bucket_synthesis_closed_specific_buckets, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_10_trades_bucket_synthesis_good_review_bad_operational_map [INFERRED 0.95]
- **Trades Recovery Families** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_13_trades_recovery_review_no_1m_reference_no_1m_recovery, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_17_trades_recovery_review_generic_generic_review_recovery, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_15_trades_recovery_review_microstructure_microstructure_recovery, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_16_trades_recovery_review_1m_reference_alignment_alignment_recovery, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_14_trades_recovery_reference_scale_mismatch_scale_mismatch_recovery, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_18_trades_recovery_synthesis_recovery_synthesis [EXTRACTED 1.00]
- **Trades Final Certification Closeout** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_19_trades_final_recovery_policy_final_recovery_policy, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_19_trades_final_recovery_policy_four_final_certification_states, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_17_trades_recovery_review_generic_strict_recovery_rule, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_19_trades_final_recovery_policy_backtest_and_ml_usage_tiers, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_20_trades_closeout_canonical_57f_closeout_cache, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_trades_20_trades_closeout_bounded_rehabilitation_verdict [INFERRED 0.95]

## Communities (28 total, 1 thin omitted)

### Community 0 - "Trade Casepack Evidence"
Cohesion: 0.07
Nodes (34): Trades Bad Cases v0.1, Intrinsic Tape Damage, Trades Bad Boundary, Bad Data Family, Trades Bad Data Cases v0.1, Small Hard Tail, Trades Family Casepacks Index v0.1, Trade Family Casepack Index (+26 more)

### Community 1 - "Trade Label Taxonomy"
Cohesion: 0.12
Nodes (26): Authoritative Trades Certification State, Trades Current State, Final 57f Trades Run, Distinct Trade Label Families, Trades Label Assessment, Trades Base-Certification Decision, Fine File-Acceptance Base, Old Residual Mass Is Not Final Policy (+18 more)

### Community 2 - "Microstructure Schema Contracts"
Cohesion: 0.11
Nodes (24): Quotes Schema Contract, Observed Bid-Ask Book, Quotes Raw Schema, Trades Schema Contract, Raw Trade Row, Trade File Acceptance Schema, Trades Raw Schema, Microstructure Features Table Dataset Contract v0.1 (+16 more)

### Community 3 - "Population Inspection Dossiers"
Cohesion: 0.12
Nodes (24): Build Quotes Inspection Pack, Population and Forensic Evidence, Quotes Inspection Builder, Quotes Coverage Casepack Index, Quotes Coverage Case Index, Quotes Inspection Readout v0.1, Local Book Quality, Quotes Inspection Readout (+16 more)

### Community 4 - "Quote Quality Certification"
Cohesion: 0.12
Nodes (24): Quotes Certification Contract, Expected, Present, Healthy, and Usable, Quote Certification State, Quotes Expected-Presence Logic, Expected-Presence Logic, Synthetic Expected Truth Is Forbidden, Quotes Quality Policy, Good, Review, and Bad Quote Quality (+16 more)

### Community 5 - "Trade Recovery Synthesis"
Cohesion: 0.15
Nodes (24): Recovery: No 1m Reference, Extended Backtest and Flagged-ML Use, Missing Intraday Anchor, No-1m-Reference Recovery, Recoverable With Flag, Recovery: Reference-Scale Mismatch, Explained Review, Explanation Is Not Rehabilitation (+16 more)

### Community 6 - "Intraday Regime Features"
Cohesion: 0.12
Nodes (22): Intraday Regime Features Schema Contract v0.1, Intraday Regime Feature Schema, Local and Cross-Session Features, Intraday Regime Features Dataset Contract v0.1, Intraday Regime Features v0.1, Split-Protected Regime State, Intraday Regime Features Consumption Policy, Intraday Regime Consumption (+14 more)

### Community 7 - "Trade Recovery Policy"
Cohesion: 0.17
Nodes (22): Trades Bucket Synthesis, Closed Specific Trade Buckets, Trades Bucket Synthesis, Generic Review Remains Open, Good, Review, and Bad Operational Map, Generic Trades Review, Generic Review Bucket, Heterogeneous Mass Requires Review (+14 more)

### Community 8 - "RAW Alignment Handoffs"
Cohesion: 0.15
Nodes (18): Trading Activity RTH Coverage Sidecar Pilot v0.1, Legacy Source Gate, RTH Coverage Sidecar, RAW Alignment Audit Changelog, RAW Alignment Changelog, RAW Alignment Audit Handoff v0.1, Physical, Not Economic, Alignment, RAW Alignment Design Handoff (+10 more)

### Community 9 - "Quotes Validator Governance"
Cohesion: 0.19
Nodes (14): Quotes Validators, External Context Explanation, Local Book Verdict, Quotes Validator System, Quotes Full C+D Closeout, Quotes C+D Closeout, Crossed Economic Severity, Quotes Full C+D Methodology (+6 more)

### Community 10 - "Quote Casepack Audit"
Cohesion: 0.19
Nodes (13): Destructive Crossed Book, Quotes Bad Cases v0.1, Quotes Bad Cases, Quotes Bad Casepack Index, Quotes Bad Case Index, Context Is Not Rehabilitation, Quotes Review Cases v0.1, Quotes Review Cases (+5 more)

### Community 11 - "Trades Audit Implementation"
Cohesion: 0.20
Nodes (12): Trades Audit Proposal v1, Trades Audit Proposal, Append-Only Audit State, Trades Agent02-Agent03 Contract, Trades Agent Audit Contract, Trades v2 Implementation Design, Trades v2 Implementation, Trades C+D Implementation State (+4 more)

### Community 12 - "Trades Certification Closeout"
Cohesion: 0.30
Nodes (12): Good Trades, Good Trade Bucket, Semantic Quality Without Empirical Dominance, Small Good-Bucket Caveat, Trades, Daily, and 1m Alignment, Bounded Rehabilitation Verdict, Canonical 57f Closeout Cache, Do Not Conflate 57e Statistics With 57f (+4 more)

### Community 13 - "Controlled Microstructure Windows"
Cohesion: 0.24
Nodes (11): Controlled Microstructure Windows, Controlled Microstructure Visual Readout v0.2, Fifty-Window Candidate, Microstructure Candidate Visual Readout v0.1, Microstructure Smoke Windows, Six-Row Smoke Candidate, Microstructure Features Dossier, Microstructure Visual Dossier (+3 more)

### Community 14 - "Alignment Recovery Tooling"
Cohesion: 0.29
Nodes (10): Quotes Worker Acceleration Runbook v0.1, Quotes Worker Acceleration, Transactional Worker Claiming, Quotes Recovery Clone Runbook v0.1, Non-Destructive Clone, Post-Copy Parity Gate, Quotes Recovery Clone, RAW Alignment Audit Validators v0.1 (+2 more)

### Community 15 - "Trades Validator System"
Cohesion: 0.29
Nodes (10): Trades Validators, Layered Trade Validation, Trades Validator System, Trades LT1B 57f Final Readout, Full LT1B Acceptance Labels, Trades 57f Final Readout, Condition-Code Anatomy, Trades File Acceptance Notebook (+2 more)

### Community 16 - "Quotes Artifact Mapping"
Cohesion: 0.33
Nodes (9): Assemble Certification Without Re-Audit, Quotes Artifact Mapping, Existing Quotes Artifact Mapping, Quotes Certification Table Specification, Presence, Quality, Context, and Final Use, Ticker-Date Quotes Certification Table, Quotes Local Certification Build Plan, Local Quotes Certification Build (+1 more)

### Community 17 - "RAW Alignment Audit"
Cohesion: 0.47
Nodes (6): Core Market RAW Alignment Audit Schema Contract v0.1, RAW Alignment Audit Schema, Read-Only Physical Audit, Core Market RAW Alignment Probe Readout v0.1, Full Audit Not Authorized, RAW Alignment Probe

### Community 18 - "Quotes Consumption Policy"
Cohesion: 0.47
Nodes (6): Quotes Label Taxonomy and Cut Policy, Local Quality vs External Causality, Quotes Cut Taxonomy, Quotes Consumption Policy, Quotes Consumption, Quotes Good-Review-Bad

### Community 19 - "Trades Consumption Policy"
Cohesion: 0.47
Nodes (6): Trades Label Taxonomy and Cut Policy, Trade Acceptance Families, Trades Cut Taxonomy, Trades Consumption Policy, Trade Recovery States, Trades Consumption

### Community 20 - "Quotes Audit Architecture"
Cohesion: 0.33
Nodes (6): Quotes Audit Proposal v1, Quotes Audit Proposal, Quotes Agent02-Agent03 Contract, Quotes Agent Audit Contract, Quotes C+D Architecture Design, Quotes C+D Architecture

### Community 21 - "Quotes Good Cases"
Cohesion: 0.50
Nodes (5): Defensible Observed Book, Quotes Good Cases v0.1, Quotes Good Cases, Quotes Good Casepack Index, Quotes Good Case Index

### Community 22 - "Stratified Trade Sampling"
Cohesion: 0.50
Nodes (5): Trades File Acceptance Readout v0.1, Trade File Acceptance, Anti-Cherry-Picking, Trades Sampling Strategy v0.1, Stratified Trade Sampling

### Community 23 - "Regime Materialization Coverage"
Cohesion: 1.00
Nodes (3): Intraday Regime Materialization Coverage v0.1, Eight-Ticker Scope, Regime Feature Pilot Coverage

### Community 24 - "Regime Boundary Cases"
Cohesion: 1.00
Nodes (3): Intraday Regime Lookback and Boundary Cases v0.1, Expected Lookback Nulls, Lookback and Boundary Cases

### Community 25 - "Regime Good Cases"
Cohesion: 1.00
Nodes (3): Intraday Regime Good Scoped Cases v0.1, Regime Feature Good Cases, Split-Neutralization Controls

### Community 26 - "Regime Validator System"
Cohesion: 1.00
Nodes (3): Intraday Regime Features Validators, Intraday Regime Validator System, Scoped Pilot Acceptance

## Knowledge Gaps
- **39 isolated node(s):** `Intraday Regime Features Registry Entry`, `Quotes Registry Entry`, `Trades Registry Entry`, `Intraday Regime Features Dossier`, `Microstructure Features Dossier` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Trades Recovery Synthesis` connect `Trade Recovery Synthesis` to `Trades Certification Closeout`, `Trade Recovery Policy`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `Trades Certification Closeout` connect `Trades Certification Closeout` to `Trade Recovery Synthesis`, `Trade Recovery Policy`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Trade Family Casepack Index` (e.g. with `Bad Data Family` and `Good Trade Family`) actually correct?**
  _`Trade Family Casepack Index` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Distinct Trade Label Families` (e.g. with `Authoritative Trades Certification State` and `1m Reference-Alignment Review`) actually correct?**
  _`Distinct Trade Label Families` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Intraday Regime Features Registry Entry`, `Quotes Registry Entry`, `Trades Registry Entry` to the rest of the system?**
  _39 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Trade Casepack Evidence` be split into smaller, more focused modules?**
  _Cohesion score 0.07308377896613191 - nodes in this community are weakly interconnected._
- **Should `Trade Label Taxonomy` be split into smaller, more focused modules?**
  _Cohesion score 0.11692307692307692 - nodes in this community are weakly interconnected._