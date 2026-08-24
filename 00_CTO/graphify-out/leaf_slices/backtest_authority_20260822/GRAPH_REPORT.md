# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 43 files · ~36,994 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 210 nodes · 293 edges · 17 communities (16 shown, 1 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Governance Schema Properties
- Backtest Authority Governance
- Governance Registry Schema
- Historical Handoff Records
- Deterministic Replay Guide
- Gate 014 Authorization
- Governance Update Protocol
- Governance Schema Contract
- Wake-Up Scientific Architecture
- Accounting Engine Mechanics
- Backtest Agent Authority
- Gate 014 Version History
- Gate 015 Acceptance
- Gate 014 Historical Versions
- Governance Validator
- Local Governance Rules
- Preliminary Evaluation Artifact

## God Nodes (most connected - your core abstractions)
1. `TSIS Backtest Engine Authority Root` - 20 edges
2. `Wake-Up and Frontside Termination Scientific Architecture v0.2` - 8 edges
3. `required` - 7 edges
4. `RunPreflight` - 7 edges
5. `BT-GATE-015 v0.4 Final Acceptance` - 7 edges
6. `Backtest Engine Agent Authority Contract` - 6 edges
7. `Data Guide` - 6 edges
8. `BT-GATE-015 Closed Pass with Restrictions` - 6 edges
9. `Deterministic Historical Replay` - 6 edges
10. `Accounting Engine` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Bounded Market State Acceptance` --semantically_similar_to--> `BT-GATE-014 Closed Pass with Restrictions`  [INFERRED] [semantically similar]
  00_CTO/14_BACKTEST_ENGINE/08_GATES_AND_REVIEWS/BT_GATE_014_FINAL_POSTEXECUTION_ACCEPTANCE_V0_1.md → 00_CTO/14_BACKTEST_ENGINE/AGENTS.md
- `BT-GATE-015 v0.4 Final Acceptance` --semantically_similar_to--> `BT-GATE-015 Closed Pass with Restrictions`  [INFERRED] [semantically similar]
  00_CTO/14_BACKTEST_ENGINE/08_GATES_AND_REVIEWS/BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW_ACCEPTANCE_V0_1.md → 00_CTO/14_BACKTEST_ENGINE/AGENTS.md
- `Single-Use Authorization v0.4` --semantically_similar_to--> `Single-Use Authorization v0.5`  [INFERRED] [semantically similar]
  00_CTO/14_BACKTEST_ENGINE/08_GATES_AND_REVIEWS/BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_4.md → 00_CTO/14_BACKTEST_ENGINE/08_GATES_AND_REVIEWS/BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_5.md
- `BT-GATE-015 v0.4 Final Acceptance` --semantically_similar_to--> `BT-GATE-015 Closed with Restrictions`  [INFERRED] [semantically similar]
  00_CTO/14_BACKTEST_ENGINE/08_GATES_AND_REVIEWS/BT_GATE_015_V0_4_POSTEXECUTION_EXTERNAL_REVIEW_ACCEPTANCE_V0_1.md → 00_CTO/14_BACKTEST_ENGINE/10_VALIDATION/GOVERNANCE_VALIDATION_REPORT.md
- `ASCII Architecture View` --semantically_similar_to--> `Scientific Backtest Architecture`  [INFERRED] [semantically similar]
  00_CTO/14_BACKTEST_ENGINE/TSIS_ARQUITECTURA_BACKTEST_CIENTIFICO_ASCII.md → 00_CTO/14_BACKTEST_ENGINE/TSIS_ARQUITECTURA_BACKTEST_CIENTIFICO.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Backtest Vertical Slice** — 00_cto_14_backtest_engine_01_guide_01_data_runpreflight, 00_cto_14_backtest_engine_01_guide_02_replay_deterministic_historical_replay, 00_cto_14_backtest_engine_01_guide_03_mechanical_trade_path_decision_order_fill_position, 00_cto_14_backtest_engine_01_guide_03_mechanical_trade_path_fill_derived_position_pnl, 00_cto_14_backtest_engine_01_guide_08_accounting_accounting_engine, 00_cto_14_backtest_engine_01_guide_01_system_status_and_inspector_guide_proven_vertical_slice [INFERRED 0.95]
- **Backtest Authority Evidence Gate Chain** — 00_cto_14_backtest_engine_readme_authority_root, 00_cto_14_backtest_engine_02_architecture_01_authority_and_evidence_boundary_authority_verification_physical_evidence_boundary, 00_cto_14_backtest_engine_03_contracts_contract_inventory_contract_lifecycle_inventory, 00_cto_14_backtest_engine_changelog_gate_evidence_chain, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_phase_b_external_re_review_acceptance_v0_1_non_physical_phase_b_acceptance, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_final_postexecution_acceptance_v0_1_bounded_market_state_acceptance, 00_cto_14_backtest_engine_agents_bt_gate_014_closed_pass [INFERRED 0.95]
- **Market State Provider-Consumer Boundary** — 00_cto_14_backtest_engine_tsis_arquitectura_backtester_state_provider_000_018_ascii_state_provider_boundary, 00_cto_14_backtest_engine_tsis_arquitectura_backtester_state_provider_000_018_ascii_provider_consumer_compatibility, 00_cto_14_backtest_engine_02_architecture_02_applied_architecture_context_boundary_external_context_not_authorization, 00_cto_14_backtest_engine_02_architecture_02_applied_architecture_context_boundary_explicit_compatibility_gate, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_phase_b_external_re_review_acceptance_v0_1_non_physical_phase_b_acceptance, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_final_postexecution_acceptance_v0_1_bounded_market_state_acceptance [INFERRED 0.95]
- **BT-GATE-014 Single-Use Authorization Evolution** — 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_single_use_physical_consumer_authorization_v0_3_single_use_v0_3, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_single_use_physical_consumer_authorization_v0_4_v0_3_consumed_failed_final, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_single_use_physical_consumer_authorization_v0_4_single_use_v0_4, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_single_use_physical_consumer_authorization_v0_5_separate_restriction_domains, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_single_use_physical_consumer_authorization_v0_5_single_use_v0_5, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_014_single_use_physical_consumer_authorization_v0_5_two_aciu_rows [INFERRED 0.95]
- **BT-GATE-015 Acceptance Chain** — 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_015_non_physical_external_review_acceptance_v0_1_bt_gate_015_non_physical_acceptance, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_015_non_physical_external_review_acceptance_v0_1_zero_physical_event_state_reads, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_015_v0_4_postexecution_external_review_acceptance_v0_1_bt_gate_015_v0_4_final_acceptance, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_015_v0_4_postexecution_external_review_acceptance_v0_1_single_use_consumption_receipt, 00_cto_14_backtest_engine_08_gates_and_reviews_bt_gate_015_v0_4_postexecution_external_review_acceptance_v0_1_bounded_event_state_slice, 00_cto_14_backtest_engine_10_validation_governance_validation_report_bt_gate_015_closed_with_restrictions [INFERRED 0.95]
- **Historical Vertical Slice Evidence** — 00_cto_14_backtest_engine_11_historical_snapshots_2026_07_28_pre_governance_root_agent_historical_historical_runpreflight, 00_cto_14_backtest_engine_11_historical_snapshots_2026_07_28_pre_governance_root_agent_historical_historical_replay_minimum, 00_cto_14_backtest_engine_11_historical_snapshots_2026_07_28_pre_governance_root_agent_historical_historical_mechanical_round_trip, 00_cto_14_backtest_engine_11_historical_snapshots_2026_07_28_pre_governance_root_agent_historical_historical_accounting_minimum, 00_cto_14_backtest_engine_11_historical_snapshots_2026_07_28_pre_governance_root_changelog_history_source_vertical_slice_history, 00_cto_14_backtest_engine_11_historical_snapshots_2026_07_28_pre_governance_root_changelog_history_source_validation_manifest_hash_binding [INFERRED 0.95]

## Communities (17 total, 1 thin omitted)

### Community 0 - "Governance Schema Properties"
Cohesion: 0.07
Nodes (32): type, items, type, minLength, type, items, type, additionalProperties (+24 more)

### Community 1 - "Backtest Authority Governance"
Cohesion: 0.11
Nodes (28): Professional Trading Systems Guide, Layered Implementation Guide, Maturity States, Authority / Verification / Physical Evidence Boundary, Authority and Evidence Boundary, Parallel Provider Lane, Applied Architecture Context Boundary, Explicit Compatibility Gate (+20 more)

### Community 2 - "Governance Registry Schema"
Cohesion: 0.09
Nodes (23): format, type, items, type, type, anyOf, minProperties, minLength (+15 more)

### Community 3 - "Historical Handoff Records"
Cohesion: 0.16
Nodes (21): Historical Agent Handoff, Historical Accounting Minimum, Historical Live Handoff, Historical Mechanical Round Trip, Historical Replay Minimum, Historical RunPreflight, No Full-History Backtest, Controlled Quote-Guarded Candidate (+13 more)

### Community 4 - "Deterministic Replay Guide"
Cohesion: 0.26
Nodes (13): Controlled Candidate Consumption, Data Guide, Missing Data Without Imputation, RunPreflight, Three Price Views, Versioned Universe, System Status and Inspector Guide, Mechanical and Arithmetic Closure Only (+5 more)

### Community 5 - "Gate 014 Authorization"
Cohesion: 0.27
Nodes (11): ACIU Core-Four Two-Row Scope, Bounded Market State Acceptance, BT-GATE-014 Final Postexecution Acceptance, Atomic Validation and Sealing, BT-GATE-014 Phase B External Re-review Acceptance, Non-Physical Phase B Acceptance, Authorization Is Not Self-Executing, BT-GATE-014 Single-Use Physical Consumer Authorization v0.5 (+3 more)

### Community 6 - "Governance Update Protocol"
Cohesion: 0.33
Nodes (10): Atomic Living Status Update, Backtest Engine Governance Update Protocol, Governance/Evidence Separation, Governance Update Protocol, Increment Classification, BT-GATE-015 Closed with Restrictions, BT-GATE-016 Not Open, Governance Validation Report (+2 more)

### Community 7 - "Governance Schema Contract"
Cohesion: 0.20
Nodes (9): additionalProperties, anyOf, $id, required, $schema, title, type, as_of (+1 more)

### Community 8 - "Wake-Up Scientific Architecture"
Cohesion: 0.42
Nodes (9): Detector Research Run, Wake-Up and Frontside Termination Scientific Architecture v0.2, Event State, Frontside Termination Event, Light/Heavy State Architecture, Market State, Policy Backtest Run, Separate Scientific Programs (+1 more)

### Community 9 - "Accounting Engine Mechanics"
Cohesion: 0.39
Nodes (9): Decision / Order / Fill / Position, Mechanical Trade Path Guide, Fill-Derived Position and PnL, Mechanical Fill Proxy, Accounting Engine, Cash Is Not Short Equity, Component Cost Breakdown, Accounting Guide (+1 more)

### Community 10 - "Backtest Agent Authority"
Cohesion: 0.36
Nodes (9): Contract Lifecycle Inventory, Contract Inventory, Typed Event State Payload, Authority Fail-Closed Rule, BT-GATE-014 Closed Pass with Restrictions, BT-GATE-015 Closed Pass with Restrictions, BT-GATE-016 Not Open, Current Authoritative Backtest State (+1 more)

### Community 11 - "Gate 014 Version History"
Cohesion: 0.36
Nodes (9): BT-GATE-014 Single-Use Physical Consumer Authorization v0.3, Frozen Nine-Input Provider Binding, Single-Use Authorization v0.3, Strategy NONE, BT-GATE-014 Single-Use Physical Consumer Authorization v0.4, Durable Physical Progress Telemetry, External Pre-Execution Review, Single-Use Authorization v0.4 (+1 more)

### Community 12 - "Gate 015 Acceptance"
Cohesion: 0.36
Nodes (9): BT-GATE-015 Non-Physical Acceptance, BT-GATE-015 Non-Physical External Review Acceptance, Physical Authorization Preparation Only, Zero Physical Event State Reads, Bounded Event State Slice, BT-GATE-015 v0.4 Final Acceptance, BT-GATE-015 v0.4 Postexecution External Review Acceptance, No Broader Event State Authority (+1 more)

### Community 13 - "Gate 014 Historical Versions"
Cohesion: 0.50
Nodes (5): BT-GATE-014 Single-Use Physical Consumer Authorization v0.1, Historical Authorization v0.1, BT-GATE-014 Single-Use Physical Consumer Authorization v0.2, Historical Authorization v0.2, Superseded by v0.3

### Community 14 - "Governance Validator"
Cohesion: 0.70
Nodes (4): load(), main(), sha(), Path

### Community 15 - "Local Governance Rules"
Cohesion: 0.60
Nodes (5): Canonical JSON Registers, Contractual Data Meaning, Local Governance Rules, Missing Evidence Is Not Pass, Raw Data Immutable

## Knowledge Gaps
- **41 isolated node(s):** `$id`, `$schema`, `additionalProperties`, `anyOf`, `format` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TSIS Backtest Engine Authority Root` connect `Backtest Authority Governance` to `Deterministic Replay Guide`, `Gate 014 Authorization`, `Accounting Engine Mechanics`, `Backtest Agent Authority`, `Local Governance Rules`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `Backtest Engine Agent Authority Contract` connect `Backtest Agent Authority` to `Backtest Authority Governance`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `BT-GATE-015 v0.4 Final Acceptance` connect `Gate 015 Acceptance` to `Backtest Agent Authority`, `Governance Update Protocol`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **What connects `$id`, `$schema`, `additionalProperties` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Governance Schema Properties` be split into smaller, more focused modules?**
  _Cohesion score 0.06653225806451613 - nodes in this community are weakly interconnected._
- **Should `Backtest Authority Governance` be split into smaller, more focused modules?**
  _Cohesion score 0.10846560846560846 - nodes in this community are weakly interconnected._
- **Should `Governance Registry Schema` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._