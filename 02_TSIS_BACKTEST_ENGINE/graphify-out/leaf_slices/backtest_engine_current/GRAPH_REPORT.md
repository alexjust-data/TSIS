# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 192 files · ~107,816 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2574 nodes · 6491 edges · 123 communities (112 shown, 11 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 404 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef81564b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Physical Historical Replay Pipeline
- Mechanical Event Accounting
- Deterministic Fill Execution Simulation
- Physical Event State Gate Tests
- Market State Consumer Contracts
- Market State Acceptance Matrix
- Portfolio Slice Execution Runner
- Market State Physical Store
- Market State V0.5 Authorization
- Historical Replay Feed
- Point-in-Time State Consumers
- Backtest Gate Consumption Authority
- Event State Physical Consumers
- Real Data Run Preflight
- Online Backtest Accounting
- Event State Physical Gate Tests
- Frozen Authority Regression Tests
- Input State Feed Policy
- Single-Use Market State Preparation
- Market State Physical Consumer Runtime
- Preflight Report Contract
- Real Data Preflight Inspector
- Run Preflight Failure Tests
- Strategy and Run Contracts
- Atomic Market State Consumer
- Market State V0.2 Execution
- Market State V0.4 Authorization
- Real Data Inspector Tests
- Input State Resolution Policy
- Accounting Execution Policy Schema
- Backtest Contract Serialization
- Fill Cost Accounting
- Market State V0.4 Tests
- Event State Store Acceptance
- Market State Physical Gate Tests
- Market State V0.3 Tests
- Authorized Dataset Requirements
- Event State Physical Authorization
- End-to-End Strategy Runner
- Event State Preconsumption Runner
- Synthetic Market State Runner
- Strategy Artifact Binding Schema
- Event State Store Runtime
- Input Coverage Contract
- Backtest Run Orchestration
- Replay and State Feed Policy
- Market State V0.4 Runner
- Market Data Dataset Binding
- Dataset Authorization Binding
- Consumption Restrictions Schema
- Event State Ordered Physical Runner
- Backtest Authorization Contract
- State Request Authorized Bindings
- State Request Resolution Binding
- Provider Contract Integrity Reference
- Run Evaluation Claim Schema
- Temporal Policy Contract
- Authorized State Dataset Contract
- Official State Artifact Binding
- Market State Consumer Unit Test Suite
- Input Manifest Schema Primitives
- Run Specification Schema Primitives
- Backtest Run Required Contract
- Run Specification Definitions
- State Replay Policy
- State Provider Requests
- Runtime Provider Request Bundle
- Replay Event Ordering Timestamps
- Event State Temporal Legality
- Market State Consumer Tests
- Input State Request Binding
- Input Capability Claim Fields
- Input Manifest Required Fields
- Market Data Binding Requirements
- Decision Policy Contract
- State Profile Request
- Artifact Contract Integrity Reference
- Input Date Range
- Input State Provider Contracts
- Universe Symbol Selection
- Artifact Contract Reference
- State Consumption Authorization
- Run Limitations Contract
- Portfolio Slice Runner Tests
- State Binding Properties
- Input Restrictions and Limitations
- State Binding Requirements
- Input Required Claim Set
- Run State Resolution Reference
- Event State Consumer
- Provider Contract Identity
- State Resolution Requirements
- Backtest Governance Roadmap
- BT-GATE-011 Acceptance Packaging
- Execution Simulation Contracts
- Preflight Manifest Generation
- Input Provider Contract References
- Run Provider Contract References
- Run Temporal Policy
- Market State Restriction Tests
- Consumption Purpose Constraints
- Run Fixture Kind
- V0.3 Preexecution Materialization
- V0.4 Preexecution Materialization
- V0.4 Postexecution Package Validation
- Market State Canonical Serialization
- Event State Consumption Legality
- Coverage Completeness Policy
- V0.4 Preexecution Package Validation
- Market State Acceptance Packaging
- Market State Tamper Checks
- Manifest Generation Timestamp
- Universe Resolution Registry
- Input Manifest Contract Type
- Price View Authorization
- Full Repository Test Runner
- Backtest Engine Package
- Backtest Engine Distribution

## God Nodes (most connected - your core abstractions)
1. `MarketStateContractError` - 138 edges
2. `date_time` - 73 edges
3. `DeterministicFillSimulator` - 71 edges
4. `MarketStateConsumerV0_1` - 71 edges
5. `AcceptanceMatrix` - 68 edges
6. `EventStateContractError` - 61 edges
7. `MarketStateStore` - 56 edges
8. `PhysicalHistoricalReplaySliceRunner` - 55 edges
9. `ReplayBarEvent` - 49 edges
10. `PhysicalReplaySliceRequest` - 48 edges

## Surprising Connections (you probably didn't know these)
- `_z()` --references--> `date_time`  [EXTRACTED]
  02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/event_state/consumer.py → 02_TSIS_BACKTEST_ENGINE/contracts/backtest/backtest_run_spec_contract_v0_1.json
- `main()` --calls--> `BacktestRunRequest`  [INFERRED]
  02_TSIS_BACKTEST_ENGINE/scripts/run_bt_gate_011_end_to_end.py → 02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/backtest/contracts.py
- `main()` --calls--> `SingleStrategyEndToEndBacktestRunner`  [INFERRED]
  02_TSIS_BACKTEST_ENGINE/scripts/run_bt_gate_011_end_to_end.py → 02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/backtest/runner.py
- `main()` --calls--> `PortfolioRunRequest`  [INFERRED]
  02_TSIS_BACKTEST_ENGINE/scripts/run_bt_gate_012_portfolio_slice.py → 02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/portfolio/contracts.py
- `main()` --calls--> `PortfolioSliceRunner`  [INFERRED]
  02_TSIS_BACKTEST_ENGINE/scripts/run_bt_gate_012_portfolio_slice.py → 02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/portfolio/runner.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Backtest Engine Validation Progression** — 02_tsis_backtest_engine_docs_00_system_01_runpreflight_implementation_plan_v0_1_fail_closed_run_context_resolution, 02_tsis_backtest_engine_docs_00_system_03_replay_implementation_plan_v0_1_deterministic_legal_one_minute_replay, 02_tsis_backtest_engine_docs_00_system_04_accounting_implementation_plan_v0_1_gross_to_net_accounting_closure, 02_tsis_backtest_engine_docs_00_system_07_execution_semantics_and_cost_model_contract_v0_1_bar_based_execution_semantics_contract, 02_tsis_backtest_engine_docs_00_system_09_deterministic_fill_simulator_implementation_and_acceptance_v0_1_accepted_deterministic_fill_simulator, 02_tsis_backtest_engine_docs_00_system_10_bt_gate_011_single_strategy_end_to_end_backtest_contract_v0_1_single_strategy_end_to_end_engine_validation, 02_tsis_backtest_engine_docs_00_system_12_bt_gate_012_multi_symbol_multi_session_portfolio_slice_contract_v0_1_multi_symbol_multi_session_portfolio_contract, 02_tsis_backtest_engine_docs_00_system_14_bt_gate_013_physical_historical_replay_slice_contract_v0_1_physical_historical_replay_boundary [EXTRACTED 1.00]
- **Bounded Market State Consumer Lane** — 02_tsis_backtest_engine_docs_00_system_05_runpreflight_state_consumption_implementation_plan_v0_1_state_aware_runpreflight_contract, 02_tsis_backtest_engine_docs_00_system_06_state_replay_feed_implementation_plan_v0_1_deterministic_state_replay_delivery, 02_tsis_backtest_engine_docs_00_system_15_bt_gate_014_point_in_time_market_state_consumer_contract_v0_1_point_in_time_market_state_consumer_contract, 02_tsis_backtest_engine_docs_00_system_16_bt_gate_014_non_physical_consumer_acceptance_packet_v0_1_accepted_non_physical_market_state_consumer, 02_tsis_backtest_engine_docs_00_system_17_bt_gate_014_phase_b_external_re_review_acceptance_v0_1_phase_b_external_re_review_acceptance [INFERRED 0.95]
- **Graphify and Local Governance** — 02_tsis_backtest_engine_agents_current_backtest_engine_gate_authority, 02_tsis_backtest_engine_graphify_official_build_protocol_graphify_controlled_leaf_protocol, 02_tsis_backtest_engine_local_rules_backtest_engine_local_implementation_boundary, 02_tsis_backtest_engine_readme_backtest_engine_vertical_slice_status [EXTRACTED 1.00]
- **Market State Single-Use Authorization Lineage** — 02_tsis_backtest_engine_docs_00_system_18_bt_gate_014_single_use_physical_consumer_authorization_v0_1_superseded_unconsumed_market_state_authorization_v0_1, 02_tsis_backtest_engine_docs_00_system_18_bt_gate_014_single_use_physical_consumer_authorization_v0_2_superseded_unconsumed_market_state_authorization_v0_2, 02_tsis_backtest_engine_docs_00_system_18_bt_gate_014_single_use_physical_consumer_authorization_v0_3_market_state_single_use_authorization_v0_3, 02_tsis_backtest_engine_docs_00_system_18_bt_gate_014_single_use_physical_consumer_authorization_v0_4_market_state_single_use_authorization_v0_4, 02_tsis_backtest_engine_docs_00_system_18_bt_gate_014_single_use_physical_consumer_authorization_v0_5_market_state_restriction_domain_authorization_v0_5, 02_tsis_backtest_engine_docs_00_system_19_bt_gate_014_final_postexecution_acceptance_v0_1_accepted_bounded_market_state_physical_consumer [EXTRACTED 1.00]
- **Event State V0.3 Fail-Closed Recovery** — 02_tsis_backtest_engine_docs_00_system_20_bt_gate_015_point_in_time_event_state_consumer_contract_v0_1_point_in_time_event_state_consumer_contract, 02_tsis_backtest_engine_docs_00_system_21_bt_gate_015_non_physical_implementation_review_packet_v0_2_event_state_non_physical_review_corrections_r2, 02_tsis_backtest_engine_docs_00_system_22_bt_gate_015_non_physical_implementation_review_packet_v0_3_accepted_event_state_non_physical_implementation_r3, 02_tsis_backtest_engine_docs_00_system_23_bt_gate_015_single_use_physical_consumer_authorization_v0_3_event_state_physical_authorization_v0_3, 02_tsis_backtest_engine_docs_00_system_24_bt_gate_015_v0_3_preexecution_review_request_event_state_v0_3_preexecution_review_scope, 02_tsis_backtest_engine_docs_00_system_25_bt_gate_015_v0_3_preexecution_packet_readout_corrected_v0_3_preexecution_packet, 02_tsis_backtest_engine_docs_00_system_26_bt_gate_015_v0_3_consumed_failure_readout_consumed_fail_closed_v0_3_run, 02_tsis_backtest_engine_docs_00_system_27_bt_gate_015_v0_3_postexecution_external_review_confirmed_dataset_fingerprint_domain_binding_error [EXTRACTED 1.00]
- **Event State V0.4 Successful Physical Lane** — 02_tsis_backtest_engine_docs_00_system_27_bt_gate_015_v0_3_postexecution_external_review_confirmed_dataset_fingerprint_domain_binding_error, 02_tsis_backtest_engine_docs_00_system_28_bt_gate_015_single_use_physical_consumer_authorization_v0_4_event_state_physical_authorization_v0_4, 02_tsis_backtest_engine_docs_00_system_29_bt_gate_015_v0_4_preexecution_review_request_event_state_v0_4_preexecution_review_scope, 02_tsis_backtest_engine_docs_00_system_30_bt_gate_015_v0_4_preexecution_packet_readout_corrected_v0_4_preexecution_packet, 02_tsis_backtest_engine_docs_00_system_31_bt_gate_015_v0_4_preexecution_external_review_approved_single_use_v0_4_execution, 02_tsis_backtest_engine_docs_00_system_32_bt_gate_015_v0_4_consumed_success_readout_consumed_successful_v0_4_event_state_run, 02_tsis_backtest_engine_docs_00_system_33_bt_gate_015_v0_4_postexecution_review_request_v0_4_postexecution_review_request [EXTRACTED 1.00]
- **Current Gate Authority Surface** — 02_tsis_backtest_engine_docs_00_system_34_bt_gate_015_v0_4_postexecution_external_review_acceptance_accepted_restricted_event_state_physical_consumer, 02_tsis_backtest_engine_docs_00_system_backtest_engine_roadmap_backtest_engine_capability_roadmap, 02_tsis_backtest_engine_docs_00_system_current_project_handoff_live_backtest_restart_authority, 02_tsis_backtest_engine_docs_00_system_governance_operating_model_capability_level_governance_model [EXTRACTED 1.00]
- **State Consumer Governance Transition** — 02_tsis_backtest_engine_docs_00_system_state_provider_consumer_hold_handoff_v0_1_historical_state_consumer_hold_boundary, 02_tsis_backtest_engine_docs_00_system_34_bt_gate_015_v0_4_postexecution_external_review_acceptance_accepted_restricted_event_state_physical_consumer, 02_tsis_backtest_engine_docs_00_system_current_project_handoff_live_backtest_restart_authority [INFERRED 0.85]

## Communities (123 total, 11 thin omitted)

### Community 0 - "Physical Historical Replay Pipeline"
Cohesion: 0.06
Nodes (34): main(), Path, _resolve(), canonical_hash(), canonical_sha256(), parse_utc(), PhysicalBarReplayAdapterV0_1, PhysicalReplayAdapterError (+26 more)

### Community 1 - "Mechanical Event Accounting"
Cohesion: 0.06
Nodes (45): AccountingRunResult, AccountingRunSummary, AccountState, CashLedgerEntry, CostBreakdown, CostComponent, CostModel, _decimal_str() (+37 more)

### Community 2 - "Deterministic Fill Execution Simulation"
Cohesion: 0.07
Nodes (25): CostComponentV0, CostModelV0, dec(), decimal_str(), EvaluationResult, ExecutionOrder, ExecutionPolicy, ExecutionSimulationError (+17 more)

### Community 3 - "Physical Event State Gate Tests"
Cohesion: 0.06
Nodes (23): main(), Execute the exact BT-GATE-015 V0.4 physical probe once after external PASS., Focused tests for the consumed BT-GATE-015 V0.4 physical result., Focused non-physical tests for the exact BT-GATE-015 V0.4 path., atomic_write_json(), AuthorizationV04, _progress_defaults(), Any (+15 more)

### Community 4 - "Market State Consumer Contracts"
Cohesion: 0.08
Nodes (34): canonical_bytes(), _canonical_restrictions(), _component_replay_restrictions(), _deep_freeze(), is_deeply_immutable(), _json_mapping(), _json_sequence(), MarketStateConsumerV0_1 (+26 more)

### Community 6 - "Portfolio Slice Execution Runner"
Cohesion: 0.12
Nodes (25): BacktestRunError, MetricsSummary, PositionSnapshot, Exception, EventSequenceRecord, PortfolioEventLoopTraceRecord, PortfolioRunManifest, PortfolioRunRequest (+17 more)

### Community 7 - "Market State Physical Store"
Cohesion: 0.10
Nodes (29): main(), resolve(), Executed acceptance matrix for BT-GATE-014 non-physical phase., canonical_hash(), event_physical_identity(), _event_session_date_utc(), state_aware_order_key(), BoundedConsumerProbeObservation (+21 more)

### Community 8 - "Market State V0.5 Authorization"
Cohesion: 0.09
Nodes (21): _load_object(), main(), Path, Only authorized CLI entry point for the BT-GATE-014 V0.5 physical run., _sha256(), _verify_closed_binding(), atomic_write_json(), AuthorizationV05 (+13 more)

### Community 9 - "Historical Replay Feed"
Cohesion: 0.11
Nodes (14): Exception, ReplayContractError, _canonical_sha256(), _event_sequence_sha256(), HistoricalReplayFeed, _lookup_hash(), _parse_utc(), Any (+6 more)

### Community 10 - "Point-in-Time State Consumers"
Cohesion: 0.06
Nodes (44): BT-GATE-014 Physical Authorization V0.1, Superseded Unconsumed Market State Authorization V0.1, BT-GATE-014 Physical Authorization V0.2, Superseded Unconsumed Market State Authorization V0.2, BT-GATE-014 Physical Authorization V0.3, Market State Single-Use Authorization V0.3, BT-GATE-014 Physical Authorization V0.4, Market State Single-Use Authorization V0.4 (+36 more)

### Community 11 - "Backtest Gate Consumption Authority"
Cohesion: 0.14
Nodes (27): Executed acceptance matrix for BT-GATE-015 non-physical implementation., canonical_hash(), EventStateConsumerV0_1, is_issued_receipt(), _payload(), Any, Fail-closed synthetic consumer for BT-GATE-015., _strict_json() (+19 more)

### Community 12 - "Event State Physical Consumers"
Cohesion: 0.06
Nodes (41): Backtest Engine Agent Handoff, Current Backtest Engine Gate Authority, Fail-Closed Run Context Resolution, RunPreflight Implementation Plan, Physical Layout Discovery, Quote-Guarded Physical Fixture Binding, Deterministic Legal One-Minute Replay, Replay Implementation Plan (+33 more)

### Community 13 - "Real Data Run Preflight"
Cohesion: 0.16
Nodes (22): CandidateConsumptionPolicy, CorporateActionPolicy, DataPreflightReport, DatasetDefinition, MissingDataPolicy, PreflightFailure, PriceViewBinding, PriceViewPolicy (+14 more)

### Community 14 - "Online Backtest Accounting"
Cohesion: 0.17
Nodes (34): CashLedgerEntryV0, dec(), EndToEndBacktestResult, EquityCurvePoint, EventLoopTraceRecord, money(), TradeRecord, _accounting_applied_inside_loop() (+26 more)

### Community 15 - "Event State Physical Gate Tests"
Cohesion: 0.11
Nodes (7): Focused non-physical tests for the exact BT-GATE-015 V0.3 path., PhysicalEventStateV03CanonicalTests, PhysicalEventStateV03Tests, PhysicalV03Fixture, Path, sha256(), write_json()

### Community 17 - "Input State Feed Policy"
Cohesion: 0.06
Nodes (34): $ref, $ref, $ref, effective_policies, additionalProperties, properties, required, type (+26 more)

### Community 18 - "Single-Use Market State Preparation"
Cohesion: 0.13
Nodes (17): main(), Any, Path, Atomic single-use authorization state for BT-GATE-014., sha256(), SingleUseAuthorization, _strict(), _write_atomic() (+9 more)

### Community 19 - "Market State Physical Consumer Runtime"
Cohesion: 0.14
Nodes (19): _load_object(), main(), Path, Only authorized CLI entry point for the BT-GATE-014 V0.4 physical run., _sha256(), _verify_closed_binding(), atomic_write_json(), AuthorizationV04 (+11 more)

### Community 20 - "Preflight Report Contract"
Cohesion: 0.07
Nodes (30): $ref, $ref, const, $ref, $ref, format, type, $ref (+22 more)

### Community 21 - "Real Data Preflight Inspector"
Cohesion: 0.15
Nodes (15): format, type, date, _date_from_iso(), _finite_non_negative(), _finite_positive(), _increment(), _minute_range() (+7 more)

### Community 23 - "Strategy and Run Contracts"
Cohesion: 0.13
Nodes (18): main(), Path, _resolve_from_root(), main(), Path, _resolve(), BacktestOrderIntent, decimal_str() (+10 more)

### Community 24 - "Atomic Market State Consumer"
Cohesion: 0.13
Nodes (9): main(), _utc(), atomic(), AuthorizationV02, h(), PhysicalRunnerV02, write(), PhysicalV02Tests (+1 more)

### Community 25 - "Market State V0.2 Execution"
Cohesion: 0.17
Nodes (17): _load_object(), main(), Path, Only authorized CLI entry point for the BT-GATE-014 V0.3 physical run., _sha256(), _verify_closed_binding(), atomic_write_json(), AuthorizationV03 (+9 more)

### Community 27 - "Real Data Inspector Tests"
Cohesion: 0.08
Nodes (26): const, const, state_resolution_policy, bundle_cardinality, capability_view_mode, partial_success_allowed, policy_id, provider_request_cardinality (+18 more)

### Community 28 - "Input State Resolution Policy"
Cohesion: 0.08
Nodes (26): additionalProperties, properties, required, type, $ref, accounting_policy, execution_policy, additionalProperties (+18 more)

### Community 29 - "Accounting Execution Policy Schema"
Cohesion: 0.08
Nodes (25): $ref, $ref, $ref, const, $ref, $ref, $ref, $ref (+17 more)

### Community 30 - "Backtest Contract Serialization"
Cohesion: 0.15
Nodes (3): Any, to_jsonable(), Any

### Community 31 - "Fill Cost Accounting"
Cohesion: 0.16
Nodes (3): EventStateAcceptanceMatrix, Any, Path

### Community 32 - "Market State V0.4 Tests"
Cohesion: 0.21
Nodes (8): sha256_file(), _load_json(), _normalize_arrow_row(), PhysicalRunnerV05, Any, Path, _write_json(), PhysicalV05CanonicalBindingTests

### Community 33 - "Event State Store Acceptance"
Cohesion: 0.16
Nodes (6): PhysicalV03Tests, AuthorizationV03, Path, sha256(), write_json(), PhysicalRunnerV03

### Community 34 - "Market State Physical Gate Tests"
Cohesion: 0.15
Nodes (6): PhysicalV04Tests, AuthorizationV04, Path, sha256(), write_json(), PhysicalRunnerV04

### Community 35 - "Market State V0.3 Tests"
Cohesion: 0.18
Nodes (9): main(), Path, request(), Any, Path, SyntheticEventStateRunner, SyntheticEventStateRunRequest, EventStateRunnerTests (+1 more)

### Community 36 - "Authorized Dataset Requirements"
Cohesion: 0.23
Nodes (13): main(), Execute the exact BT-GATE-015 V0.3 physical probe once after external PASS., atomic_write_json(), AuthorizationV03, _progress_defaults(), Any, BaseException, Path (+5 more)

### Community 37 - "Event State Physical Authorization"
Cohesion: 0.24
Nodes (5): BacktestRunRequest, EndToEndRunSummary, SingleStrategyEndToEndBacktestRunner, Path, SingleStrategyEndToEndBacktestTests

### Community 38 - "End-to-End Strategy Runner"
Cohesion: 0.21
Nodes (15): _session(), EventStateContractError, Exception, PhysicalEventStateConsumerV03, Validate the exact provider row and atomically issue a store receipt., PhysicalRunnerV03, PreconsumptionEvidence, Any (+7 more)

### Community 39 - "Event State Preconsumption Runner"
Cohesion: 0.19
Nodes (8): format_utc_z(), strict_json_document(), Any, Serialize BT-GATE-014 values with the contract's canonical UTC spelling., to_market_state_jsonable(), Any, Path, SyntheticMarketStateRunner

### Community 40 - "Synthetic Market State Runner"
Cohesion: 0.10
Nodes (21): strategy, parameters_artifact_id, parameters_sha256, $ref, $ref, parameters_artifact_id, parameters_sha256, strategy_id (+13 more)

### Community 41 - "Strategy Artifact Binding Schema"
Cohesion: 0.11
Nodes (20): $ref, additionalProperties, minLength, properties, required, type, artifact_ref, artifact_id (+12 more)

### Community 42 - "Event State Store Runtime"
Cohesion: 0.10
Nodes (20): additionalProperties, const, properties, required, type, coverage, coverage_policy_satisfied, represented_contexts (+12 more)

### Community 43 - "Input Coverage Contract"
Cohesion: 0.10
Nodes (20): replay_policy, $ref, const, event_ordering_policy_id, NONE, state_feed, StateReplayFeed, const (+12 more)

### Community 44 - "Backtest Run Orchestration"
Cohesion: 0.29
Nodes (8): sha256_file(), _load_json(), _normalize_arrow_row(), PhysicalRunnerV03, Any, AuthorizationV03, Path, _write_json()

### Community 45 - "Replay and State Feed Policy"
Cohesion: 0.29
Nodes (8): sha256_file(), _load_json(), _normalize_arrow_row(), PhysicalRunnerV04, Any, AuthorizationV04, Path, _write_json()

### Community 46 - "Market State V0.4 Runner"
Cohesion: 0.11
Nodes (19): $ref, type, $ref, $ref, minLength, type, properties, calendar_id (+11 more)

### Community 47 - "Market Data Dataset Binding"
Cohesion: 0.19
Nodes (9): BoundedEventStateAvailable, EventStateStoreTrace, Any, Contracts for the bounded non-physical Event State consumer., to_event_state_jsonable(), Bounded non-physical Event State consumer., Reproducible non-physical acceptance runner for BT-GATE-015., EventStateStore (+1 more)

### Community 48 - "Dataset Authorization Binding"
Cohesion: 0.12
Nodes (18): contains, items, minContains, type, uniqueItems, const, minLength, type (+10 more)

### Community 49 - "Consumption Restrictions Schema"
Cohesion: 0.21
Nodes (13): PreconsumptionEvidence, Any, AuthorizationV04, Path, Bounded physical runner for the BT-GATE-015 V0.4 single-use probe., _read_jsonl(), _sha256(), _strict_json_bytes() (+5 more)

### Community 50 - "Event State Ordered Physical Runner"
Cohesion: 0.12
Nodes (17): const, $ref, const, additionalProperties, properties, required, type, const (+9 more)

### Community 51 - "Backtest Authorization Contract"
Cohesion: 0.12
Nodes (17): items, items, minItems, type, uniqueItems, items, type, uniqueItems (+9 more)

### Community 52 - "State Request Authorized Bindings"
Cohesion: 0.12
Nodes (17): $ref, state_request_binding, event_state, market_state, consumer_request_id, request_fingerprint, runtime_invocation_response, state_kind (+9 more)

### Community 53 - "State Request Resolution Binding"
Cohesion: 0.12
Nodes (17): minLength, type, $ref, const, minLength, type, provider_contract_ref, contract_id (+9 more)

### Community 54 - "Provider Contract Integrity Reference"
Cohesion: 0.12
Nodes (17): type, additionalProperties, properties, required, type, claims, type, type (+9 more)

### Community 55 - "Run Evaluation Claim Schema"
Cohesion: 0.12
Nodes (17): $ref, $ref, $ref, properties, $ref, $ref, $ref, calendar_id (+9 more)

### Community 56 - "Temporal Policy Contract"
Cohesion: 0.12
Nodes (16): additionalProperties, required, type, authorized_state_dataset, profile_id, representation_version, authorized_fields, authorized_information_objects (+8 more)

### Community 57 - "Authorized State Dataset Contract"
Cohesion: 0.12
Nodes (16): properties, const, $ref, const, $ref, downstream_authorized, feature_lineage_manifest, official_dataset (+8 more)

### Community 58 - "Official State Artifact Binding"
Cohesion: 0.26
Nodes (4): cfg(), docs(), MarketStateConsumerTests, request()

### Community 59 - "Market State Consumer Unit Test Suite"
Cohesion: 0.13
Nodes (14): additionalProperties, allOf, $defs, safe_id, sha256, description, $id, pattern (+6 more)

### Community 60 - "Input Manifest Schema Primitives"
Cohesion: 0.13
Nodes (15): const, const, properties, const, all_required_hashes_verified, hash_algorithm, physical_paths_user_supplied, provider_contract_hashes_verified (+7 more)

### Community 61 - "Run Specification Schema Primitives"
Cohesion: 0.13
Nodes (14): additionalProperties, allOf, $defs, safe_id, sha256, description, $id, pattern (+6 more)

### Community 62 - "Backtest Run Required Contract"
Cohesion: 0.13
Nodes (15): required, backtest_id, claims, contract_id, contract_sha256, contract_type, contract_version, run_id (+7 more)

### Community 63 - "Run Specification Definitions"
Cohesion: 0.13
Nodes (15): $ref, $ref, event_state_request, market_state_request, runtime_capability_effective_view, runtime_user_invocation_interface, runtime_user_invocation_response, state_bundle_manifest (+7 more)

### Community 64 - "State Replay Policy"
Cohesion: 0.14
Nodes (14): maxItems, minItems, type, uniqueItems, $ref, $ref, authorized_datasets, backtest_authorization (+6 more)

### Community 65 - "State Provider Requests"
Cohesion: 0.14
Nodes (14): $ref, $ref, event_state_request, market_state_request, provider_contracts, runtime_capability_effective_view, runtime_user_invocation_interface, runtime_user_invocation_response (+6 more)

### Community 66 - "Runtime Provider Request Bundle"
Cohesion: 0.14
Nodes (14): $ref, execution, signal, valuation, additionalProperties, properties, required, type (+6 more)

### Community 67 - "Replay Event Ordering Timestamps"
Cohesion: 0.14
Nodes (14): backtest_id, claims, contract_type, run_id, required, data_preflight_report, effective_policies, generated_at_utc (+6 more)

### Community 68 - "Event State Temporal Legality"
Cohesion: 0.27
Nodes (9): format, type, date_time, BacktestOrderRecord, _bar_id(), _event_id(), _event_ts_end(), _event_ts_start() (+1 more)

### Community 69 - "Market State Consumer Tests"
Cohesion: 0.14
Nodes (14): const, items, maxItems, type, uniqueItems, const, const, decision_clock_basis (+6 more)

### Community 70 - "Input State Request Binding"
Cohesion: 0.14
Nodes (14): const, additionalProperties, properties, required, type, $ref, decision_policy, decision_clock (+6 more)

### Community 71 - "Input Capability Claim Fields"
Cohesion: 0.14
Nodes (14): state_profile_request, consumer_request_id, profile_id, representation_version, state_kind, additionalProperties, allOf, required (+6 more)

### Community 72 - "Input Manifest Required Fields"
Cohesion: 0.15
Nodes (13): type, properties, type, type, broker_cost_realism_claimed, edge_evaluated, fill_realism_claimed, provider_consumer_compatibility_validated (+5 more)

### Community 73 - "Market Data Binding Requirements"
Cohesion: 0.15
Nodes (13): format, type, additionalProperties, properties, required, type, format, type (+5 more)

### Community 74 - "Decision Policy Contract"
Cohesion: 0.15
Nodes (13): market_data_binding, calendar_id, dataset_id, date_range, price_views, session_policy, timezone, additionalProperties (+5 more)

### Community 75 - "State Profile Request"
Cohesion: 0.15
Nodes (13): pattern, selected_symbols, universe_id, universe_manifest, universe_run_id, items, minItems, type (+5 more)

### Community 76 - "Artifact Contract Integrity Reference"
Cohesion: 0.15
Nodes (13): additionalProperties, properties, type, minLength, type, $ref, const, minLength (+5 more)

### Community 77 - "Input Date Range"
Cohesion: 0.15
Nodes (13): const, const, const, bundle_cardinality, capability_view_mode, partial_success_allowed, provider_request_cardinality, provider_response_cardinality (+5 more)

### Community 78 - "Input State Provider Contracts"
Cohesion: 0.15
Nodes (13): additionalProperties, required, type, data_request, calendar_id, corporate_action_policy_id, dataset_id, date_range (+5 more)

### Community 79 - "Universe Symbol Selection"
Cohesion: 0.15
Nodes (13): minLength, pattern, type, default, items, type, uniqueItems, limitations (+5 more)

### Community 81 - "State Consumption Authorization"
Cohesion: 0.17
Nodes (12): $ref, required_fields, required_information_objects, items, default, items, type, uniqueItems (+4 more)

### Community 82 - "Run Limitations Contract"
Cohesion: 0.18
Nodes (11): input_integrity, additionalProperties, required, type, all_required_hashes_verified, hash_algorithm, physical_paths_user_supplied, provider_contract_hashes_verified (+3 more)

### Community 83 - "Portfolio Slice Runner Tests"
Cohesion: 0.18
Nodes (11): state_binding, provider_contracts, resolution_policy, additionalProperties, allOf, required, type, authorized_datasets (+3 more)

### Community 84 - "State Binding Properties"
Cohesion: 0.18
Nodes (11): consumer_request_id, runtime_capability_effective_view, runtime_user_invocation_interface, runtime_user_invocation_response, state_bundle_manifest, state_kind, state_resolution_request, required (+3 more)

### Community 85 - "Input Restrictions and Limitations"
Cohesion: 0.18
Nodes (11): const, consumption_purpose, requests, resolution_policy, allOf, maxItems, minItems, type (+3 more)

### Community 86 - "State Binding Requirements"
Cohesion: 0.18
Nodes (11): $ref, additionalProperties, properties, required, type, $ref, date_end, date_start (+3 more)

### Community 88 - "Run State Resolution Reference"
Cohesion: 0.20
Nodes (10): additionalProperties, required, type, claims, broker_cost_realism_claimed, edge_evaluated, fill_realism_claimed, short_tradability_evaluated (+2 more)

### Community 89 - "Event State Consumer"
Cohesion: 0.20
Nodes (10): $ref, $ref, consumer_request_id, profile_id, representation_version, resolution, minLength, type (+2 more)

### Community 90 - "Provider Contract Identity"
Cohesion: 0.20
Nodes (10): state_resolution_policy, bundle_cardinality, capability_view_mode, partial_success_allowed, provider_request_cardinality, provider_response_cardinality, require_single_bundle_covers_all_requests, additionalProperties (+2 more)

### Community 91 - "State Resolution Requirements"
Cohesion: 0.33
Nodes (10): Accepted Restricted Event State Physical Consumer, BT-GATE-015 V0.4 Postexecution External Acceptance, Backtest Engine Capability Roadmap, Backtest Engine Roadmap, Current Project Handoff, Live Backtest Restart Authority, Capability-Level Governance Model, Governance Operating Model (+2 more)

### Community 92 - "Backtest Governance Roadmap"
Cohesion: 0.56
Nodes (9): add_file(), add_text(), add_tree(), governance_files(), main(), Path, ZipFile, sha256_bytes() (+1 more)

### Community 93 - "BT-GATE-011 Acceptance Packaging"
Cohesion: 0.56
Nodes (9): add_file(), add_text(), add_tree(), governance_files(), main(), Path, ZipFile, sha256_bytes() (+1 more)

### Community 94 - "Execution Simulation Contracts"
Cohesion: 0.56
Nodes (9): add_file(), add_text(), add_tree(), governance_files(), main(), Path, ZipFile, sha256_bytes() (+1 more)

### Community 95 - "Preflight Manifest Generation"
Cohesion: 0.42
Nodes (9): build_data_manifest(), build_universe_manifest(), Any, Path, Manifest writers for RunPreflight outputs., sha256_file(), _validation_manifest(), write_json() (+1 more)

### Community 96 - "Input Provider Contract References"
Cohesion: 0.22
Nodes (9): state_consumption, consumption_purpose, provider_contracts, resolution_policy, additionalProperties, allOf, required, type (+1 more)

### Community 97 - "Run Provider Contract References"
Cohesion: 0.22
Nodes (9): runtime_capability_effective_view, runtime_user_invocation_interface, runtime_user_invocation_response, state_bundle_manifest, state_resolution_request, provider_contracts, additionalProperties, required (+1 more)

### Community 98 - "Run Temporal Policy"
Cohesion: 0.25
Nodes (8): universe_binding, universe_id, additionalProperties, required, type, selected_symbols, universe_manifest, universe_run_id

### Community 99 - "Market State Restriction Tests"
Cohesion: 0.25
Nodes (8): temporal_policy, additionalProperties, required, type, decision_clock_basis, future_window_allowed, outcome_dependency_allowed, require_available_at

### Community 100 - "Consumption Purpose Constraints"
Cohesion: 0.29
Nodes (7): $ref, properties, execution, signal, valuation, $ref, $ref

### Community 101 - "Run Fixture Kind"
Cohesion: 0.29
Nodes (7): execution, signal, valuation, additionalProperties, required, type, price_views

### Community 103 - "V0.4 Preexecution Materialization"
Cohesion: 0.33
Nodes (6): enum, type, fixture_kind, GOVERNED_HISTORICAL_DATASET, NON_EMPIRICAL_TEST_FIXTURE, TSIS_REAL_DATA_FIXTURE

### Community 104 - "V0.4 Postexecution Package Validation"
Cohesion: 0.33
Nodes (6): run_purpose, enum, type, mechanical_validation, research_backtest, strategy_evaluation

### Community 105 - "Market State Canonical Serialization"
Cohesion: 0.53
Nodes (5): main(), Path, Derive the BT-GATE-015 V0.3 config and state from one semantic spec., sha256(), write_json()

### Community 106 - "Event State Consumption Legality"
Cohesion: 0.53
Nodes (5): main(), Path, Derive the BT-GATE-015 V0.4 config and state from one semantic spec., sha256(), write_json()

### Community 107 - "Coverage Completeness Policy"
Cohesion: 0.67
Nodes (5): main(), Path, sha256(), validate_result(), validate_zip()

### Community 108 - "V0.4 Preexecution Package Validation"
Cohesion: 0.40
Nodes (5): enum, type, coverage_policy, ALLOW_DECLARED_UNAVAILABLE_CONTEXTS, REQUIRE_COMPLETE

### Community 109 - "Market State Acceptance Packaging"
Cohesion: 0.40
Nodes (5): event_state, market_state, state_kind, enum, type

### Community 110 - "Market State Tamper Checks"
Cohesion: 0.70
Nodes (4): main(), Path, sha256(), validate_nested_handoff()

### Community 111 - "Manifest Generation Timestamp"
Cohesion: 0.70
Nodes (4): main(), Path, sha256(), validate_nested_handoff()

### Community 112 - "Universe Resolution Registry"
Cohesion: 0.83
Nodes (3): main(), q_suffix(), sha()

### Community 114 - "Price View Authorization"
Cohesion: 0.67
Nodes (3): timezone, minLength, type

## Knowledge Gaps
- **560 isolated node(s):** `$schema`, `$id`, `title`, `description`, `type` (+555 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `date_time` connect `Event State Temporal Legality` to `Physical Historical Replay Pipeline`, `Mechanical Event Accounting`, `Deterministic Fill Execution Simulation`, `Market State Consumer Contracts`, `Portfolio Slice Execution Runner`, `Market State Physical Store`, `Historical Replay Feed`, `Backtest Gate Consumption Authority`, `Real Data Run Preflight`, `Online Backtest Accounting`, `Market State Physical Consumer Runtime`, `Real Data Preflight Inspector`, `Strategy and Run Contracts`, `Atomic Market State Consumer`, `Event State Physical Authorization`, `End-to-End Strategy Runner`, `Event State Preconsumption Runner`, `Market Data Dataset Binding`, `Run Specification Schema Primitives`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `$defs` connect `Run Specification Schema Primitives` to `Input Provider Contract References`, `Event State Temporal Legality`, `Input State Request Binding`, `Input Capability Claim Fields`, `Synthetic Market State Runner`, `Input Coverage Contract`, `Artifact Contract Integrity Reference`, `Input State Provider Contracts`, `Real Data Preflight Inspector`, `Provider Contract Integrity Reference`, `Provider Contract Identity`, `Input State Resolution Policy`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `MarketStateContractError` connect `Market State Consumer Contracts` to `Market State V0.4 Tests`, `Market State Acceptance Matrix`, `Event State Preconsumption Runner`, `Market State Physical Store`, `Market State V0.5 Authorization`, `Backtest Run Orchestration`, `Replay and State Feed Policy`, `Consumption Restrictions Schema`, `Single-Use Market State Preparation`, `Market State Physical Consumer Runtime`, `Atomic Market State Consumer`, `Market State V0.2 Execution`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `MarketStateContractError` (e.g. with `AcceptanceMatrix` and `MarketStateConsumerV0_1`) actually correct?**
  _`MarketStateContractError` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `DeterministicFillSimulator` (e.g. with `SingleStrategyEndToEndBacktestRunner` and `CostBreakdownV0`) actually correct?**
  _`DeterministicFillSimulator` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `MarketStateConsumerV0_1` (e.g. with `AcceptanceMatrix` and `BoundedMarketStateAvailable`) actually correct?**
  _`MarketStateConsumerV0_1` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AcceptanceMatrix` (e.g. with `MarketStateConsumerV0_1` and `MarketStateContractError`) actually correct?**
  _`AcceptanceMatrix` has 5 INFERRED edges - model-reasoned connections that need verification._