# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 30 files · ~17,538 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 83 nodes · 115 edges · 10 communities
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Reference Dataset Governance
- Reference Deep Audit
- Corporate Actions Semantics
- Instrument Master Identity
- Reference Causal Overlay
- Reference Validator System
- Ticker Continuity Semantics
- Market Calendar Governance
- Reference Certification State
- Split Adjustment Semantics

## God Nodes (most connected - your core abstractions)
1. `reference dataset contract v0 1` - 12 edges
2. `Reference Causal Overlay` - 8 edges
3. `Reference Deep Audit Contract` - 6 edges
4. `Corporate Actions Table` - 5 edges
5. `Instrument Master` - 5 edges
6. `Reference Dataset Family` - 5 edges
7. `Reference Audit Contract` - 5 edges
8. `Reference Causal Overlay Closeout` - 5 edges
9. `Reference Validator System` - 5 edges
10. `Reference Inspection Dossier` - 4 edges

## Surprising Connections (you probably didn't know these)
- `reference dataset contract v0 1` --references--> `exchanges schema contract`  [EXTRACTED]
  01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/reference/exchanges_schema_contract.md
- `reference dataset contract v0 1` --references--> `splits schema contract`  [EXTRACTED]
  01_TSIS_DATA_FOUNDATION/01_foundations/contract_registry/dataset_contracts/reference_dataset_contract_v0_1.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/reference/splits_schema_contract.md
- `Reference Causal Overlay` --implements--> `Reference Causal Phase Readiness`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/04_reference_causal_overlay_closeout.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/03_reference_root_cause_audit_phase1_closeout.md
- `Reference Deep Audit Closeout` --implements--> `Reference Causal Overlay`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/04_reference_closeout.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/04_reference_causal_overlay_closeout.md
- `Split-to-Trades Alignment` --conceptually_related_to--> `Narrow Split-Market Link`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/04_reference_causal_overlay_closeout.md → 01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/00_reference_current_state.md

## Hyperedges (group relationships)
- **Reference Dataset Family** — 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_all_tickers_snapshot_schema_contract_ticker_reference_snapshot, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_overview_schema_contract_ticker_overview_snapshot, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_events_schema_contract_ticker_corporate_event, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_splits_schema_contract_split_event, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_dividends_schema_contract_dividend_event, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_exchanges_schema_contract_exchange_reference, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_ticker_types_schema_contract_ticker_type_dictionary, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_operational_run_schema_contract_reference_operational_run, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_reference_dataset_contract_v0_1_reference_dataset_family [EXTRACTED 1.00]
- **Identity and Corporate Action Resolution** — 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_all_tickers_snapshot_schema_contract_ticker_reference_snapshot, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_instrument_master_dataset_contract_v0_1_instrument_master, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_events_schema_contract_ticker_corporate_event, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_corporate_actions_table_dataset_contract_v0_1_corporate_actions_table, 01_tsis_data_foundation_01_foundations_module_contracts_corporate_actions_adjustment_methodology_corporate_action_adjustment, 01_tsis_data_foundation_01_foundations_canonical_schemas_reference_events_schema_contract_continuity_requires_remap_policy [INFERRED 0.95]
- **Reference Governance Stack** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_reference_dataset_contract_v0_1_reference_dataset_family, 01_tsis_data_foundation_01_foundations_data_consumption_policies_reference_consumption_policy_reference_semantic_infrastructure, 01_tsis_data_foundation_01_foundations_dataset_registry_reference_reference_registry_entry_reference_registry, 01_tsis_data_foundation_01_foundations_inspection_dossiers_reference_readme_reference_inspection_dossier, 01_tsis_data_foundation_01_foundations_inspection_dossiers_reference_reference_inspection_readout_v0_2_human_inspector_ready, 01_tsis_data_foundation_01_foundations_inspection_dossiers_reference_reference_inspection_readout_v0_2_visual_complete [INFERRED 0.95]
- **Reference Audit Lifecycle** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_01_contrato_reference_reference_deep_audit_contract, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_03_reference_root_cause_audit_phase1_closeout_reference_structural_closeout, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_04_reference_causal_overlay_closeout_reference_causal_overlay, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_04_reference_closeout_reference_deep_audit_closeout, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_reference_02_reference_closeout_certified_reference_closeout [INFERRED 0.95]
- **Reference Causal Link Family** — 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_01_contrato_reference_reference_market_link, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_04_reference_causal_overlay_closeout_split_to_trades_alignment, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_04_reference_causal_overlay_closeout_ticker_change_to_halts_alignment, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_04_reference_causal_overlay_closeout_ticker_change_to_quotes_review, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_reference_01_reference_causal_value_market_residual_explanation [INFERRED 0.85]
- **Reference Quality Classification** — 01_tsis_data_foundation_01_foundations_validators_reference_reference_validators_reference_review_states, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_reference_04_reference_closeout_reference_good_review_bad_policy, 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_reference_02_reference_closeout_unconfirmed_split_residue_review [INFERRED 0.85]

## Communities (10 total, 0 thin omitted)

### Community 0 - "Reference Dataset Governance"
Cohesion: 0.17
Nodes (15): operational run schema contract, Reference Operational Run, ticker types schema contract, Ticker Type Dictionary, reference dataset contract v0 1, Reference Dataset Family, reference registry entry, Reference Registry (+7 more)

### Community 1 - "Reference Deep Audit"
Cohesion: 0.33
Nodes (10): Reference Audit Contract, Identity Snapshot, Listing Snapshot, Reference Deep Audit Contract, Reference Event, Reference-Market Link, Reference Root-Cause Audit Phase 1 Closeout, Reference Causal Phase Readiness (+2 more)

### Community 2 - "Corporate Actions Semantics"
Cohesion: 0.25
Nodes (9): Dividend Event, dividends schema contract, Valid No-Payload Shape, Corporate Actions Table, corporate actions table dataset contract v0 1, Corporate Actions as Context, corporate actions table consumption policy, reference consumption policy (+1 more)

### Community 3 - "Instrument Master Identity"
Cohesion: 0.25
Nodes (9): exchanges schema contract, Exchange Reference, overview schema contract, Historically Variable Schema, Ticker Overview Snapshot, instrument master dataset contract v0 1, Instrument Master, instrument master consumption policy (+1 more)

### Community 4 - "Reference Causal Overlay"
Cohesion: 0.39
Nodes (9): Reference Causal Overlay Closeout, Identity-to-Trades Weak Link, Reference Causal Overlay, Split-to-Trades Alignment, Ticker-Change-to-Halts Alignment, Ticker-Change-to-Quotes Review, Reference Causal Value, Market Residual Explanation (+1 more)

### Community 5 - "Reference Validator System"
Cohesion: 0.39
Nodes (8): Reference Validators, Reference Hard-Failure Rules, Reference Review States, Reference Validator System, Subfamily-Specific Validation, Reference Deep Audit Closeout, Reference Deep Audit Closeout, Reference Good-Review-Bad Policy

### Community 6 - "Ticker Continuity Semantics"
Cohesion: 0.47
Nodes (6): all tickers snapshot schema contract, Ticker Is Not Stable Identity, Ticker Reference Snapshot, Continuity Requires Remap Policy, events schema contract, Ticker Corporate Event

### Community 7 - "Market Calendar Governance"
Cohesion: 0.33
Nodes (6): market calendar dataset contract v0 1, Market Calendar, market calendar consumption policy, Session-Aware Consumption, market session scope, Market Session Scope

### Community 8 - "Reference Certification State"
Cohesion: 0.47
Nodes (6): Reference Current State, Narrow Split-Market Link, Reference Identity and Partial Causality, Certified Reference Closeout, Reference Certification Closeout, Unconfirmed Split Residue Review

### Community 9 - "Split Adjustment Semantics"
Cohesion: 0.50
Nodes (5): splits schema contract, Split Event, Corporate Action Adjustment, corporate actions adjustment methodology, Split Normalization

## Knowledge Gaps
- **11 isolated node(s):** `corporate actions table dataset contract v0 1`, `instrument master dataset contract v0 1`, `market calendar dataset contract v0 1`, `corporate actions table consumption policy`, `instrument master consumption policy` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `reference dataset contract v0 1` connect `Reference Dataset Governance` to `Split Adjustment Semantics`, `Corporate Actions Semantics`, `Instrument Master Identity`, `Ticker Continuity Semantics`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `Reference Causal Overlay` connect `Reference Causal Overlay` to `Reference Deep Audit`, `Reference Validator System`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `Reference Dataset Family` connect `Reference Dataset Governance` to `Corporate Actions Semantics`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Reference Causal Overlay` (e.g. with `Reference Causal Phase Readiness` and `Reference Deep Audit Closeout`) actually correct?**
  _`Reference Causal Overlay` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `corporate actions table dataset contract v0 1`, `instrument master dataset contract v0 1`, `market calendar dataset contract v0 1` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._