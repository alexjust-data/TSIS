# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 47 files · ~20,496 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 151 nodes · 212 edges · 14 communities
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Financial PIT Availability
- Additional Subblock Policy
- Additional Dataset Governance
- Auxiliary Block Integration
- Blocked Financial Family
- News Attribution Context
- Additional Causal Overlay
- Additional Structural Audit
- Sparse Context Validation
- Financial Schema Validation
- Secondary Corporate Actions
- Financial Operational Audit
- Inspection Pack Builder
- Financial Payload Evidence

## God Nodes (most connected - your core abstractions)
1. `Additional v0.1` - 9 edges
2. `Additional Causal Overlay` - 8 edges
3. `Additional Subblock Policy` - 8 edges
4. `Additional Accepted Non-Homogeneous Block` - 8 edges
5. `Financial v0.1` - 7 edges
6. `Final Good-Review-Bad Policy` - 7 edges
7. `Filing-Date Point-in-Time Availability` - 6 edges
8. `Attribution-Aware News Context` - 5 edges
9. `Additional Causal Overlay Closeout` - 5 edges
10. `Institutional Auxiliary Block` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Legal As-Of Selection` --semantically_similar_to--> `Filing-Date Point-in-Time Availability`  [INFERRED] [semantically similar]
  01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/fundamentals_asof_table_dataset_contract_v0_1.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/additional/additional_financials_schema_contract.md
- `Corporate Actions Reference Review` --semantically_similar_to--> `Corporate Actions Secondary Confirmation`  [INFERRED] [semantically similar]
  01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/additional/flagged_case_evidence_packs/additional_corporate_actions_reference_review_v0_1.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_causal_overlay_closeout.md
- `News Attribution Review` --conceptually_related_to--> `Additional Causal Overlay`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/additional/flagged_case_evidence_packs/additional_news_attribution_review_cases_v0_1.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_causal_overlay_closeout.md
- `Financial Inspection Dossier` --references--> `Audited-Blocked Financial Family`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/financial/README.md → 01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/financial/financial_inspection_readout_v0_1.md
- `Additional Causal Overlay` --implements--> `Additional Structural Phase Closeout`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_causal_overlay_closeout.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/03_additional_root_cause_audit_phase1_closeout.md

## Hyperedges (group relationships)
- **Additional Context Subfamilies** — 01_tsis_data_foundation_01_foundations_canonical_schemas_additional_additional_corporate_actions_schema_contract_secondary_corporate_actions_layer, 01_tsis_data_foundation_01_foundations_canonical_schemas_additional_additional_economic_schema_contract_macro_regime_overlay, 01_tsis_data_foundation_01_foundations_canonical_schemas_additional_additional_financials_schema_contract_auxiliary_financial_block, 01_tsis_data_foundation_01_foundations_canonical_schemas_additional_additional_ipos_schema_contract_ipo_early_life_context, 01_tsis_data_foundation_01_foundations_canonical_schemas_additional_additional_news_schema_contract_attribution_aware_news [EXTRACTED 1.00]
- **Point-in-Time Context Controls** — 01_tsis_data_foundation_01_foundations_canonical_schemas_additional_additional_financials_schema_contract_filing_date_point_in_time, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_fundamentals_asof_table_dataset_contract_v0_1_legal_asof_selection, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_news_context_table_dataset_contract_v0_1_published_utc_availability, 01_tsis_data_foundation_01_foundations_data_consumption_policies_news_context_table_consumption_policy_news_asof_join_policy [INFERRED 0.95]
- **Additional Governance Chain** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_additional_dataset_contract_v0_1_additional_v0_1, 01_tsis_data_foundation_01_foundations_data_consumption_policies_additional_consumption_policy_additional_subfamily_consumption, 01_tsis_data_foundation_01_foundations_dataset_registry_additional_additional_registry_entry_additional_registry, 01_tsis_data_foundation_01_foundations_inspection_dossiers_additional_additional_inspection_readout_v0_2_additional_institutional_readout [INFERRED 0.95]
- **Additional Evidence-to-Closeout Chain** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_additional_01_contrato_additional_additional_deep_audit_contract, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_additional_03_additional_root_cause_audit_phase1_closeout_additional_structural_phase_closeout, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_additional_04_additional_causal_overlay_closeout_additional_causal_overlay, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_additional_04_additional_closeout_additional_final_closeout, 01_tsis_data_foundation_01_foundations_inspection_dossiers_additional_additional_institutional_closeout_v0_1_institutional_auxiliary_block [INFERRED 0.95]
- **Additional Review Guardrails** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_additional_coverage_case_evidence_packs_additional_sparse_valid_context_cases_v0_1_expectedness_based_coverage, 01_tsis_data_foundation_01_foundations_inspection_dossiers_additional_flagged_case_evidence_packs_additional_corporate_actions_reference_review_v0_1_reference_primary_adjustment_authority, 01_tsis_data_foundation_01_foundations_inspection_dossiers_additional_flagged_case_evidence_packs_additional_news_attribution_review_cases_v0_1_market_context_not_causal_proof, 01_tsis_data_foundation_01_foundations_inspection_dossiers_additional_good_justification_additional_financials_core_good_cases_v0_1_mandatory_filing_pit_guardrail [INFERRED 0.85]
- **Financial Blocking Evidence** — 01_tsis_data_foundation_01_foundations_inspection_dossiers_financial_bad_case_evidence_packs_financial_blocking_schema_cases_v0_1_missing_required_columns, 01_tsis_data_foundation_01_foundations_inspection_dossiers_financial_coverage_case_evidence_packs_financial_coverage_cases_v0_1_complete_endpoint_coverage, 01_tsis_data_foundation_01_foundations_inspection_dossiers_financial_flagged_case_evidence_packs_financial_temporal_cases_v0_1_ticker_lifecycle_anomalies, 01_tsis_data_foundation_01_foundations_inspection_dossiers_financial_good_justification_financial_payload_examples_v0_1_payload_sentinel_identity_evidence, 01_tsis_data_foundation_01_foundations_inspection_dossiers_financial_financial_inspection_readout_v0_1_audited_blocked_financial [INFERRED 0.85]
- **Additional Six-Sublayer Certification** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_financials_core_good, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_financials_ratios_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_news_mixed_good_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_ipos_mixed_good_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_corporate_actions_additional_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_economic_macro_good_ticker_causality_review [EXTRACTED 1.00]
- **Additional Certification Flow** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_00_additional_current_state_six_sublayer_current_state, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_02_additional_closeout_final_good_review_bad_policy, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_02_additional_closeout_additional_accepted_nonhomogeneous [INFERRED 0.95]
- **Remaining Causal Calibration** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_news_mixed_good_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_news_near_halt_strong_subset, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_01_additional_subblock_policy_ipos_mixed_good_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_additional_02_additional_closeout_manual_causal_bucket_calibration [EXTRACTED 1.00]

## Communities (14 total, 0 thin omitted)

### Community 0 - "Financial PIT Availability"
Cohesion: 0.11
Nodes (26): Auxiliary Financial Block, Additional Financials Schema Contract, Filing-Date Point-in-Time Availability, Sparse Ratios Context, Balance Sheet Observation, Balance Sheets Financial Schema Contract, Cash Flow Statement Observation, Cash Flow Statements Financial Schema Contract (+18 more)

### Community 1 - "Additional Subblock Policy"
Cohesion: 0.20
Nodes (19): Additional Internal Hierarchy, Additional Current State, Real Multi-Ticker News Ambiguity, Reference Primary Corporate-Action Authority, Six-Sublayer Current State, Corporate Actions Additional Review, Additional Subblock Policy, Economic Macro Good, Ticker Causality Review (+11 more)

### Community 2 - "Additional Dataset Governance"
Cohesion: 0.16
Nodes (18): Additional Economic Schema Contract, Explicit Macro Availability Lag, Macro Regime Overlay, Additional IPOs Schema Contract, IPO Early-Life Context, IPO-Near-Halt Context, Additional v0.1, Additional Dataset Contract v0.1 (+10 more)

### Community 3 - "Auxiliary Block Integration"
Cohesion: 0.17
Nodes (17): Additional Materialization Evidence, Additional Institutional Closeout v0.1, Institutional Auxiliary Block, Subblock-Specific Consumption, Additional Inspection Dossier, CAPA 1 Context Enrichment, Core Authority Boundary, Additional Inspection Dossier (+9 more)

### Community 4 - "Blocked Financial Family"
Cohesion: 0.23
Nodes (12): Build Financial Inspection Pack v0.1, Dossier-Only Summarization, Financial Inspection Pack Builder, Complete Endpoint Coverage, Coverage Does Not Imply Quality, Financial Coverage Cases v0.1, Audit-Fail Consumption Block, Audited-Blocked Financial Family (+4 more)

### Community 5 - "News Attribution Context"
Cohesion: 0.31
Nodes (10): Attribution-Aware News Context, Additional News Schema Contract, Multi-Ticker News Ambiguity, News-Near-Halt Context, News Context Table Dataset Contract v0.1, News Context Table v0.1, Published-UTC Availability, News Context Table Consumption Policy (+2 more)

### Community 6 - "Additional Causal Overlay"
Cohesion: 0.36
Nodes (9): Corporate Actions Reference Review, Additional Corporate Actions Reference Review v0.1, Reference Primary Adjustment Authority, Additional Causal Overlay, Corporate Actions Secondary Confirmation, Additional Causal Overlay Closeout, IPO Near Halt Market Event, News Near Halt Market Event (+1 more)

### Community 7 - "Additional Structural Audit"
Cohesion: 0.31
Nodes (9): Additional Financials Core Good Cases v0.1, Financials Core Good Cases, Mandatory Filing PIT Guardrail, Additional Deep Audit Contract, Additional Audit Contract, Heterogeneous Analytical Units, Additional Structural Phase Closeout, Additional Root-Cause Audit Phase 1 Closeout (+1 more)

### Community 8 - "Sparse Context Validation"
Cohesion: 0.32
Nodes (8): Additional Sparse Valid Context Cases v0.1, Expectedness-Based Coverage, Sparse Valid Context, Additional News Attribution Review Cases v0.1, Market Context Is Not Causal Proof, News Attribution Review, Additional Validator System, Additional Validators

### Community 9 - "Financial Schema Validation"
Cohesion: 0.32
Nodes (8): Financial Blocking Schema Cases v0.1, Financial Blocking Schema Cases, Missing Required Columns, Financial Temporal Cases v0.1, Financial Temporal Cases, Ticker Lifecycle Anomalies, Financial Validators, Financial Validator System

### Community 10 - "Secondary Corporate Actions"
Cohesion: 0.83
Nodes (4): Additional Corporate Actions Schema Contract, Empty Sentinel Semantics, Reference Reconciliation, Secondary Corporate Actions Layer

### Community 11 - "Financial Operational Audit"
Cohesion: 0.50
Nodes (4): Financial Operational Audit Schema Contract, Financial Operational Audit, Financial Operational Run Schema Contract, Financial Operational Run

### Community 12 - "Inspection Pack Builder"
Cohesion: 0.83
Nodes (4): Additional Inspection Pack Builder, Build Additional Inspection Pack, Historical Audit Immutability, Preserved Evidence Transformation

### Community 13 - "Financial Payload Evidence"
Cohesion: 1.00
Nodes (3): Financial Payload Examples v0.1, Financial Payload Examples, Payload and Sentinel Identity Evidence

## Knowledge Gaps
- **12 isolated node(s):** `Balance Sheets Financial Schema Contract`, `Cash Flow Statements Financial Schema Contract`, `Income Statements Financial Schema Contract`, `Financial Operational Audit Schema Contract`, `Financial Operational Run Schema Contract` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Additional v0.1` connect `Additional Dataset Governance` to `Financial PIT Availability`, `Secondary Corporate Actions`, `News Attribution Context`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `Auxiliary Financial Block` connect `Financial PIT Availability` to `Additional Dataset Governance`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Additional Causal Overlay` (e.g. with `News Attribution Review` and `Additional Structural Phase Closeout`) actually correct?**
  _`Additional Causal Overlay` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Balance Sheets Financial Schema Contract`, `Cash Flow Statements Financial Schema Contract`, `Income Statements Financial Schema Contract` to the rest of the system?**
  _12 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Financial PIT Availability` be split into smaller, more focused modules?**
  _Cohesion score 0.11076923076923077 - nodes in this community are weakly interconnected._