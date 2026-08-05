# Graph Report - C:\tmp\TSIS_graphify_workspaces\backtest_engine_current\corpus  (2026-08-05)

## Corpus Check
- 162 files · ~97,837 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2568 nodes · 6774 edges · 150 communities (138 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 395 edges (avg confidence: 0.57)
- Token cost: 1,132 input · 1,007 output

## Community Hubs (Navigation)
- Accounting engine contracts
- Deterministic fill simulation
- Physical replay adapter
- Market authorization V0.4 tests
- Market authorization V0.5 tests
- Event state consumer
- Historical replay feed
- Portfolio slice orchestration
- Market state acceptance matrix
- State consumption schema
- Backtest policy identifiers
- Market state regression tests
- Physical replay slice runner
- Market state canonicalization
- End-to-end backtest runner
- Gate execution entrypoints
- Single-use market authorization
- Real data inspection
- Backtest run identity schema
- Run preflight validation
- Synthetic event state runner
- Physical event state tests
- Data inspector tests
- Preflight failure tests
- State request resolution schema
- Physical event state consumer
- Market state validation
- Run manifest serialization
- Online accounting pipeline
- Backtest contract modules
- Physical market runner V0.5
- Physical market V0.3 tests
- Event state acceptance matrix
- Execution accounting policy schema
- Physical market consumer V0.2
- Market authorization V0.3
- Physical replay adapter tests
- State resolution policy schema
- Physical market runner V0.3
- Temporal policy constraints
- Replay execution policy schema
- Physical market runner V0.4
- Market state event loops
- State coverage schema
- Repository acceptance test suite
- Single strategy backtest tests
- Strategy decision contracts
- Market data manifest schema
- Strategy specification schema
- State artifact reference schema
- Input manifest identity
- Manifest limitations and restrictions
- Physical replay result assembly
- State request bindings
- Backtest realism claims
- Event authorization V0.3
- State dataset profile schema
- State consumption authorization
- Input integrity verification
- State resolution policy configuration
- Market state consumer tests
- Capability gate governance
- Input manifest required fields
- Decision policy schema
- State profile contract
- Price view schema
- Authorized state dataset schema
- State binding schema
- State validation claims
- Date range schema
- Market data binding schema
- State manifest requirements
- Data request schema
- Run limitations schema
- Portfolio slice tests
- Runtime state request bindings
- Effective policy bindings
- Graphify refresh governance
- Input integrity schema
- State resolution manifest policy
- Backtest run required fields
- Execution cost model governance
- Backtest gate roadmap
- Synthetic market state runner
- Physical market V0.2 tests
- Event state consumer tests
- State consumption overview
- Manifest reusable definitions
- Input capability claims
- Contract artifact metadata
- Data request collection schema
- Market state consumer governance
- Event state gate handoff
- Gate 011 acceptance packaging
- Gate 012 acceptance packaging
- Gate 013 acceptance packaging
- Preflight manifest writers
- End-to-end portfolio contracts
- Schema artifact references
- Artifact hash references
- State replay implementation plans
- State event ordering contracts
- Physical authorization governance
- Input manifest root schema
- Input manifest contract metadata
- State request binding schema
- Universe binding schema
- Run specification root schema
- Event state review packets
- Graphify build governance
- Authorized datasets collection
- SHA256 contract fields
- Provider contract references
- Price view role enumeration
- Price view bindings
- Universe manifest reference
- Artifact contract references
- Run specification reusable definitions
- Physical replay governance
- Market runner V0.4 CLI
- Market runner V0.5 CLI
- Restriction domain tests
- Consumption purpose constraints
- Backtest date range
- Fixture kind enumeration
- Event preexecution materializer
- Backtest vertical slice
- Claims reference schema
- State feed binding
- Market universe binding
- Date boundary references
- Preflight implementation plans
- Accepted event state pipeline
- Event preexecution packager
- Market acceptance matrix tests
- Market acceptance packager
- Preflight registries
- Effective policies reference
- Integrity reference binding
- State binding reference
- Event authorization candidates
- Package configuration
- Price view authorization
- Preflight package interface

## God Nodes (most connected - your core abstractions)
1. `MarketStateContractError` - 138 edges
2. `date_time` - 73 edges
3. `pathlib` - 72 edges
4. `DeterministicFillSimulator` - 71 edges
5. `MarketStateConsumerV0_1` - 71 edges
6. `AcceptanceMatrix` - 68 edges
7. `MarketStateStore` - 56 edges
8. `PhysicalHistoricalReplaySliceRunner` - 55 edges
9. `PhysicalReplaySliceRequest` - 48 edges
10. `PortfolioSliceRunner` - 47 edges

## Surprising Connections (you probably didn't know these)
- `RunPreflight` --semantically_similar_to--> `RunPreflight Before Data Consumption`  [INFERRED] [semantically similar]
  docs/00_system/01_RUNPREFLIGHT_IMPLEMENTATION_PLAN_V0_1.md → LOCAL_RULES.md
- `Engine Validation Is Not Edge Evidence` --semantically_similar_to--> `Single Strategy End-to-End Backtest`  [INFERRED] [semantically similar]
  AGENTS.md → docs/00_system/10_BT_GATE_011_SINGLE_STRATEGY_END_TO_END_BACKTEST_CONTRACT_V0_1.md
- `Engine Validation Is Not Edge Evidence` --semantically_similar_to--> `Multi-Symbol Multi-Session Portfolio Slice`  [INFERRED] [semantically similar]
  AGENTS.md → docs/00_system/12_BT_GATE_012_MULTI_SYMBOL_MULTI_SESSION_PORTFOLIO_SLICE_CONTRACT_V0_1.md
- `Backtest-Specific State Authorization Boundary` --semantically_similar_to--> `BT-GATE-015 Non-Physical Reproduction Boundary`  [INFERRED] [semantically similar]
  docs/00_system/05_RUNPREFLIGHT_STATE_CONSUMPTION_IMPLEMENTATION_PLAN_V0_1.md → REPRODUCE_BT_GATE_015_R2.md
- `BT-GATE-014 Point-in-Time Market State Consumption` --semantically_similar_to--> `BT-GATE-014 Point-in-Time Market State Consumption`  [INFERRED] [semantically similar]
  AGENTS.md → README.md

## Import Cycles
- 1-file cycle: `RUN_BT_GATE_014_INCLUDED_TESTS.py -> RUN_BT_GATE_014_INCLUDED_TESTS.py`
- 1-file cycle: `src/tsis_backtest/backtest/runner.py -> src/tsis_backtest/backtest/runner.py`
- 1-file cycle: `scripts/package_bt_gate_011_acceptance.py -> scripts/package_bt_gate_011_acceptance.py`
- 1-file cycle: `scripts/run_bt_gate_011_end_to_end.py -> scripts/run_bt_gate_011_end_to_end.py`
- 1-file cycle: `src/tsis_backtest/accounting/contracts.py -> src/tsis_backtest/accounting/contracts.py`
- 1-file cycle: `src/tsis_backtest/event_state/contracts.py -> src/tsis_backtest/event_state/contracts.py`
- 1-file cycle: `tests/unit/test_bt_gate_014_single_use_physical.py -> tests/unit/test_bt_gate_014_single_use_physical.py`
- 1-file cycle: `src/tsis_backtest/preflight/registries.py -> src/tsis_backtest/preflight/registries.py`
- 2-file cycle: `src/tsis_backtest/accounting/contracts.py -> src/tsis_backtest/preflight/contracts.py -> src/tsis_backtest/accounting/contracts.py`
- 3-file cycle: `src/tsis_backtest/backtest/runner.py -> src/tsis_backtest/replay/__init__.py -> src/tsis_backtest/replay/historical_feed.py -> src/tsis_backtest/backtest/runner.py`

## Hyperedges (group relationships)
- **Accepted Engine Capability Progression** — docs_00_system_01_runpreflight_implementation_plan_v0_1_runpreflight, docs_00_system_03_replay_implementation_plan_v0_1_historical_replay_feed, docs_00_system_04_accounting_implementation_plan_v0_1_accounting_engine, docs_00_system_09_deterministic_fill_simulator_implementation_and_acceptance_v0_1_deterministic_fill_simulator, docs_00_system_10_bt_gate_011_single_strategy_end_to_end_backtest_contract_v0_1_single_strategy_backtest, docs_00_system_12_bt_gate_012_multi_symbol_multi_session_portfolio_slice_contract_v0_1_portfolio_slice, docs_00_system_14_bt_gate_013_physical_historical_replay_slice_contract_v0_1_physical_bar_replay_adapter [INFERRED 0.95]
- **Governed State Consumption Chain** — docs_00_system_01_runpreflight_implementation_plan_v0_1_runpreflight, docs_00_system_05_runpreflight_state_consumption_implementation_plan_v0_1_backtest_input_manifest, docs_00_system_05_runpreflight_state_consumption_implementation_plan_v0_1_state_authorization_boundary, docs_00_system_06_state_replay_feed_implementation_plan_v0_1_state_replay_feed, docs_00_system_06_state_replay_feed_implementation_plan_v0_1_state_execution_separation [EXTRACTED 1.00]
- **Graphify Controlled Leaf Governance** — graphify_official_build_protocol_semantic_navigation_layer, graphify_official_build_protocol_backtest_engine_current_leaf, graphify_official_build_protocol_controlled_corpus_boundary, graphify_refresh_queue_semantic_change_refresh_obligation [EXTRACTED 1.00]
- **BT-GATE-014 Bounded Market State Acceptance Lifecycle** — docs_00_system_15_bt_gate_014_point_in_time_market_state_consumer_contract_v0_1_document, docs_00_system_16_bt_gate_014_non_physical_consumer_acceptance_packet_v0_1_document, docs_00_system_17_bt_gate_014_phase_b_external_re_review_acceptance_v0_1_document, docs_00_system_18_bt_gate_014_single_use_physical_consumer_authorization_v0_3_document, docs_00_system_18_bt_gate_014_single_use_physical_consumer_authorization_v0_5_document, docs_00_system_19_bt_gate_014_final_postexecution_acceptance_v0_1_document [INFERRED 0.95]
- **BT-GATE-015 Bounded Event State Pre-Execution Lifecycle** — docs_00_system_20_bt_gate_015_point_in_time_event_state_consumer_contract_v0_1_document, docs_00_system_22_bt_gate_015_non_physical_implementation_review_packet_v0_3_document, docs_00_system_23_bt_gate_015_single_use_physical_consumer_authorization_v0_3_document, docs_00_system_24_bt_gate_015_v0_3_preexecution_review_request_document, docs_00_system_25_bt_gate_015_v0_3_preexecution_packet_readout_document, docs_00_system_current_project_handoff_current_project_handoff [INFERRED 0.95]
- **BAR to Market State to Event State Causal Chain** — docs_00_system_15_bt_gate_014_point_in_time_market_state_consumer_contract_v0_1_boundedmarketstateavailable, docs_00_system_20_bt_gate_015_point_in_time_event_state_consumer_contract_v0_1_boundedeventstateavailable, docs_00_system_20_bt_gate_015_point_in_time_event_state_consumer_contract_v0_1_state_aware_global_order, docs_00_system_20_bt_gate_015_point_in_time_event_state_consumer_contract_v0_1_eventstatestore [EXTRACTED 1.00]
- **Backtest Vertical Slice Pipeline** — agents_runpreflight, agents_real_data_inspector, agents_historical_replay_feed, agents_mechanical_trade_path, agents_accounting_engine, agents_deterministic_fill_simulator [EXTRACTED 1.00]
- **Capability Gate Progression** — agents_single_strategy_end_to_end_backtest, agents_multi_symbol_multi_session_portfolio_slice, agents_physical_historical_replay_slice [EXTRACTED 1.00]
- **Current Authoritative Gate State** — agents_bt_gate_014, agents_bt_gate_015, agents_current_project_handoff [EXTRACTED 1.00]
- **Backtest Engine Macrogate Progression** — docs_00_system_backtest_engine_roadmap_bt_gate_011, docs_00_system_backtest_engine_roadmap_bt_gate_012, docs_00_system_backtest_engine_roadmap_bt_gate_013 [EXTRACTED 1.00]
- **BT-GATE-015 Synthetic Event State Path** — docs_00_system_current_project_handoff_replay_bar_event, docs_00_system_current_project_handoff_bounded_market_state_available, docs_00_system_current_project_handoff_bounded_event_state_available, docs_00_system_current_project_handoff_event_state_store [EXTRACTED 1.00]
- **BT-GATE-015 Failure Review Scope** — docs_00_system_current_project_handoff_bt_gate_015, docs_00_system_current_project_handoff_v0_3_execution, docs_00_system_current_project_handoff_fail_event_state_identity_mismatch, docs_00_system_current_project_handoff_postexecution_failure_review [EXTRACTED 1.00]
- **Active Graphify Refresh Entries** — graphify_refresh_queue_gfq_20260805_bt_001, graphify_refresh_queue_gfq_20260805_bt_002, graphify_refresh_queue_gfq_20260805_bt_003 [EXTRACTED 1.00]

## Communities (150 total, 12 thin omitted)

### Community 0 - "Accounting engine contracts"
Cohesion: 0.06
Nodes (45): AccountingRunResult, AccountingRunSummary, AccountState, CashLedgerEntry, CostBreakdown, CostComponent, CostModel, _decimal_str() (+37 more)

### Community 1 - "Deterministic fill simulation"
Cohesion: 0.07
Nodes (25): CostComponentV0, CostModelV0, dec(), decimal_str(), EvaluationResult, ExecutionOrder, ExecutionPolicy, ExecutionSimulationError (+17 more)

### Community 2 - "Physical replay adapter"
Cohesion: 0.12
Nodes (20): format, format, type, type, date, date_time, _z(), canonical_sha256() (+12 more)

### Community 3 - "Market authorization V0.4 tests"
Cohesion: 0.08
Nodes (15): atomic_write_json(), AuthorizationV04, _error_code(), _failure_guard(), _fsync_directory(), Any, BaseException, Path (+7 more)

### Community 4 - "Market authorization V0.5 tests"
Cohesion: 0.08
Nodes (15): atomic_write_json(), AuthorizationV05, _error_code(), _failure_guard(), _fsync_directory(), Any, BaseException, Path (+7 more)

### Community 5 - "Event state consumer"
Cohesion: 0.14
Nodes (29): Executed acceptance matrix for BT-GATE-015 non-physical implementation., canonical_hash(), EventStateConsumerV0_1, is_issued_receipt(), _payload(), Any, Fail-closed synthetic consumer for BT-GATE-015., _session() (+21 more)

### Community 6 - "Historical replay feed"
Cohesion: 0.11
Nodes (13): Exception, ReplayContractError, _canonical_sha256(), _event_sequence_sha256(), HistoricalReplayFeed, _lookup_hash(), _parse_utc(), Any (+5 more)

### Community 7 - "Portfolio slice orchestration"
Cohesion: 0.14
Nodes (19): main(), BacktestRunError, Exception, OrderSimulationResult, EventSequenceRecord, PortfolioEventLoopTraceRecord, PortfolioRunRequest, PortfolioRunResult (+11 more)

### Community 9 - "State consumption schema"
Cohesion: 0.05
Nodes (42): resolution_policy, $ref, const, state_consumption, $ref, consumption_purpose, provider_contracts, resolution_policy (+34 more)

### Community 10 - "Backtest policy identifiers"
Cohesion: 0.07
Nodes (41): $ref, $ref, $ref, properties, $ref, $ref, $ref, accounting_policy_id (+33 more)

### Community 11 - "Market state regression tests"
Cohesion: 0.10
Nodes (4): SyntheticMarketStateRunner, ExternalReviewRegressionTests, load(), request()

### Community 12 - "Physical replay slice runner"
Cohesion: 0.16
Nodes (7): main(), Path, _resolve(), PhysicalReplaySliceRequest, _CopiedRequest, PhysicalHistoricalReplaySliceRunner, Path

### Community 13 - "Market state canonicalization"
Cohesion: 0.11
Nodes (29): math, canonical_bytes(), canonical_hash(), _canonical_restrictions(), _deep_freeze(), event_physical_identity(), is_deeply_immutable(), _json_mapping() (+21 more)

### Community 14 - "End-to-end backtest runner"
Cohesion: 0.14
Nodes (26): BacktestRunRequest, EndToEndBacktestResult, EndToEndRunSummary, EventLoopTraceRecord, _accounting_applied_inside_loop(), _bar_id(), _event_id(), _event_ts_end() (+18 more)

### Community 15 - "Gate execution entrypoints"
Cohesion: 0.14
Nodes (15): argparse, json, os, pathlib, Execute the exact BT-GATE-015 V0.3 physical probe once after external PASS., Path, _resolve_from_root(), Path (+7 more)

### Community 16 - "Single-use market authorization"
Cohesion: 0.13
Nodes (18): main(), Any, Path, Atomic single-use authorization state for BT-GATE-014., sha256(), SingleUseAuthorization, _strict(), _write_atomic() (+10 more)

### Community 17 - "Real data inspection"
Cohesion: 0.16
Nodes (18): MissingDataPolicy, ResolvedDataContext, CorporateActionScreen, _date_from_iso(), _finite_non_negative(), _finite_positive(), _increment(), _minute_range() (+10 more)

### Community 18 - "Backtest run identity schema"
Cohesion: 0.06
Nodes (33): $ref, $ref, const, $ref, $ref, $ref, properties, accounting_policy (+25 more)

### Community 19 - "Run preflight validation"
Cohesion: 0.18
Nodes (16): re, CandidateConsumptionPolicy, DataPreflightReport, DatasetDefinition, PreflightFailure, PriceViewBinding, PriceViewPolicy, RunDataRequest (+8 more)

### Community 20 - "Synthetic event state runner"
Cohesion: 0.13
Nodes (12): main(), Path, request(), Any, to_event_state_jsonable(), Any, Path, SyntheticEventStateRunner (+4 more)

### Community 21 - "Physical event state tests"
Cohesion: 0.15
Nodes (5): PhysicalEventStateV03Tests, PhysicalV03Fixture, Path, sha256(), write_json()

### Community 22 - "Data inspector tests"
Cohesion: 0.22
Nodes (3): CorporateActionPolicy, Path, RealDataInspectorTests

### Community 24 - "State request resolution schema"
Cohesion: 0.07
Nodes (28): $ref, enum, type, event_state, market_state, $ref, consumer_request_id, coverage_policy (+20 more)

### Community 25 - "Physical event state consumer"
Cohesion: 0.13
Nodes (18): main(), PhysicalEventStateConsumerV03, Validate the exact provider row and atomically issue a store receipt., PhysicalRunnerV03, PreconsumptionEvidence, Any, AuthorizationV03, Path (+10 more)

### Community 26 - "Market state validation"
Cohesion: 0.16
Nodes (11): _component_replay_restrictions(), MarketStateConsumerV0_1, _physical_provenance_restrictions(), Any, Validate physical restrictions without reinterpreting them as replay policy., Atomically validate governed inputs and issue a receipt for that result., Perform the closed bijection and atomic validation used by the runner., _require_nonempty_string() (+3 more)

### Community 27 - "Run manifest serialization"
Cohesion: 0.13
Nodes (6): decimal_str(), Any, to_jsonable(), UnifiedRunManifest, PortfolioRunManifest, Any

### Community 28 - "Online accounting pipeline"
Cohesion: 0.24
Nodes (21): CashLedgerEntryV0, dec(), EquityCurvePoint, money(), PositionSnapshot, Decimal, TradeRecord, _apply_fill_online() (+13 more)

### Community 29 - "Backtest contract modules"
Cohesion: 0.19
Nodes (12): copy, dataclasses, hashlib, Durable single-use authorization state machine for BT-GATE-014 V0.3., Durable single-use authorization state machine for BT-GATE-014 V0.4., Durable single-use authorization state machine for BT-GATE-014 V0.5., Synthetic-only BT-GATE-014 runner and evidence writer., Contracts for the TSIS run preflight gate. (+4 more)

### Community 30 - "Physical market runner V0.5"
Cohesion: 0.22
Nodes (11): sha256_file(), BoundedPhysicalMarketStateEventLoopV05, FrozenPhysicalRunSpec, _load_json(), _normalize_arrow_row(), PhysicalRunnerV05, Any, Path (+3 more)

### Community 31 - "Physical market V0.3 tests"
Cohesion: 0.15
Nodes (6): PhysicalRunnerV03, PhysicalV03Tests, AuthorizationV03, Path, sha256(), write_json()

### Community 32 - "Event state acceptance matrix"
Cohesion: 0.16
Nodes (3): EventStateAcceptanceMatrix, Any, Path

### Community 33 - "Execution accounting policy schema"
Cohesion: 0.08
Nodes (24): additionalProperties, properties, required, type, $ref, accounting_policy, replay_policy, required (+16 more)

### Community 34 - "Physical market consumer V0.2"
Cohesion: 0.14
Nodes (13): main(), _event_session_date_utc(), format_utc_z(), state_aware_order_key(), _utc(), Any, Serialize BT-GATE-014 values with the contract's canonical UTC spelling., to_market_state_jsonable() (+5 more)

### Community 35 - "Market authorization V0.3"
Cohesion: 0.19
Nodes (15): _load_object(), main(), Path, _sha256(), _verify_closed_binding(), atomic_write_json(), AuthorizationV03, _error_code() (+7 more)

### Community 36 - "Physical replay adapter tests"
Cohesion: 0.21
Nodes (9): _append_row(), _authorize_current_tree(), _config(), _copy_fixture_root(), PhysicalReplayAdapterTests, Path, _remove_timestamp(), _request() (+1 more)

### Community 37 - "State resolution policy schema"
Cohesion: 0.09
Nodes (23): const, const, state_resolution_policy, bundle_cardinality, capability_view_mode, partial_success_allowed, provider_request_cardinality, provider_response_cardinality (+15 more)

### Community 38 - "Physical market runner V0.3"
Cohesion: 0.25
Nodes (10): sha256_file(), FrozenPhysicalRunSpec, _load_json(), _normalize_arrow_row(), PhysicalRunnerV03, Any, AuthorizationV03, Path (+2 more)

### Community 39 - "Temporal policy constraints"
Cohesion: 0.09
Nodes (22): const, items, maxItems, type, uniqueItems, const, const, decision_clock_basis (+14 more)

### Community 40 - "Replay execution policy schema"
Cohesion: 0.09
Nodes (22): execution_policy, $ref, additionalProperties, properties, type, const, $ref, const (+14 more)

### Community 41 - "Physical market runner V0.4"
Cohesion: 0.27
Nodes (9): sha256_file(), FrozenPhysicalRunSpec, _load_json(), _normalize_arrow_row(), PhysicalRunnerV04, Any, Path, Frozen two-row physical Market State integration runner for BT-GATE-014. (+1 more)

### Community 42 - "Market state event loops"
Cohesion: 0.16
Nodes (8): BoundedConsumerProbeObservation, MarketStateStoreTrace, ValidatedBoundedMarketStateAvailable, BoundedPhysicalMarketStateEventLoopV03, Dispatch only synthetic barriers and the two authorized state events., BoundedPhysicalMarketStateEventLoopV04, Dispatch only synthetic barriers and the two authorized state events., MarketStateStore

### Community 43 - "State coverage schema"
Cohesion: 0.10
Nodes (20): additionalProperties, const, properties, required, type, coverage, coverage_policy_satisfied, represented_contexts (+12 more)

### Community 44 - "Repository acceptance test suite"
Cohesion: 0.23
Nodes (10): datetime, decimal, pyarrow, parquet, Focused non-physical tests for the exact BT-GATE-015 V0.3 path., shutil, Executed acceptance matrix for BT-GATE-014 non-physical phase., BT-GATE-013 physical historical replay slice runner. (+2 more)

### Community 45 - "Single strategy backtest tests"
Cohesion: 0.25
Nodes (5): main(), BacktestOrderRecord, SingleStrategyEndToEndBacktestRunner, Path, SingleStrategyEndToEndBacktestTests

### Community 46 - "Strategy decision contracts"
Cohesion: 0.21
Nodes (11): BacktestOrderIntent, MetricsSummary, Contracts for BT-GATE-011 single-strategy end-to-end backtests., StrategyDecision, StrategySpec, End-to-end backtest orchestration for TSIS., default_open_short_close_strategy(), OpenShortCloseCoverStrategy (+3 more)

### Community 47 - "Market data manifest schema"
Cohesion: 0.11
Nodes (19): $ref, type, $ref, $ref, minLength, type, properties, calendar_id (+11 more)

### Community 48 - "Strategy specification schema"
Cohesion: 0.11
Nodes (19): strategy, parameters_artifact_id, parameters_sha256, $ref, parameters_artifact_id, strategy_id, strategy_version, additionalProperties (+11 more)

### Community 49 - "State artifact reference schema"
Cohesion: 0.15
Nodes (18): $ref, $ref, $ref, authorization_artifact, event_state_request, market_state_request, runtime_capability_effective_view, runtime_user_invocation_interface (+10 more)

### Community 50 - "Input manifest identity"
Cohesion: 0.11
Nodes (18): $ref, const, $ref, format, type, $ref, const, properties (+10 more)

### Community 51 - "Manifest limitations and restrictions"
Cohesion: 0.12
Nodes (18): items, minLength, pattern, type, default, items, type, uniqueItems (+10 more)

### Community 52 - "Physical replay result assembly"
Cohesion: 0.29
Nodes (4): canonical_hash(), PhysicalReplayBundle, Any, Decimal

### Community 53 - "State request bindings"
Cohesion: 0.12
Nodes (17): items, minItems, type, uniqueItems, items, type, uniqueItems, $ref (+9 more)

### Community 54 - "Backtest realism claims"
Cohesion: 0.12
Nodes (17): type, additionalProperties, properties, required, type, claims, type, type (+9 more)

### Community 55 - "Event authorization V0.3"
Cohesion: 0.29
Nodes (10): atomic_write_json(), AuthorizationV03, _progress_defaults(), Any, BaseException, Path, sha256_file(), strict_load_json() (+2 more)

### Community 56 - "State dataset profile schema"
Cohesion: 0.12
Nodes (16): properties, const, $ref, const, $ref, downstream_authorized, feature_lineage_manifest, official_dataset (+8 more)

### Community 57 - "State consumption authorization"
Cohesion: 0.13
Nodes (15): const, const, additionalProperties, properties, required, type, const, backtest_authorization (+7 more)

### Community 58 - "Input integrity verification"
Cohesion: 0.13
Nodes (15): const, const, properties, const, all_required_hashes_verified, hash_algorithm, physical_paths_user_supplied, provider_contract_hashes_verified (+7 more)

### Community 59 - "State resolution policy configuration"
Cohesion: 0.13
Nodes (15): const, const, const, $ref, bundle_cardinality, capability_view_mode, partial_success_allowed, policy_id (+7 more)

### Community 60 - "Market state consumer tests"
Cohesion: 0.26
Nodes (4): cfg(), docs(), MarketStateConsumerTests, request()

### Community 61 - "Capability gate governance"
Cohesion: 0.19
Nodes (14): Backtest Engine Governance, BT-GATE-015 Current Authoritative State, Capability Gate Governance, Capability Gate Policy, Deterministic Fill Simulator V0.1, Engine Validation Evidence Policy, Execution Semantics and Cost Model Contract V0.1, Governance Traceability Chain (+6 more)

### Community 62 - "Input manifest required fields"
Cohesion: 0.14
Nodes (14): backtest_id, claims, contract_type, run_id, required, data_preflight_report, effective_policies, generated_at_utc (+6 more)

### Community 63 - "Decision policy schema"
Cohesion: 0.14
Nodes (14): const, additionalProperties, properties, required, type, $ref, decision_policy, decision_clock (+6 more)

### Community 64 - "State profile contract"
Cohesion: 0.14
Nodes (14): state_profile_request, consumer_request_id, profile_id, representation_version, state_kind, additionalProperties, allOf, required (+6 more)

### Community 65 - "Price view schema"
Cohesion: 0.14
Nodes (14): $ref, execution, signal, valuation, additionalProperties, properties, required, type (+6 more)

### Community 66 - "Authorized state dataset schema"
Cohesion: 0.15
Nodes (13): required, profile_id, representation_version, authorized_fields, authorized_information_objects, consumption_purposes, coverage, downstream_authorized (+5 more)

### Community 67 - "State binding schema"
Cohesion: 0.15
Nodes (13): $ref, state_binding, $ref, backtest_authorization, effective_capability_view, provider_contracts, additionalProperties, type (+5 more)

### Community 68 - "State validation claims"
Cohesion: 0.15
Nodes (13): type, properties, type, type, broker_cost_realism_claimed, edge_evaluated, fill_realism_claimed, provider_consumer_compatibility_validated (+5 more)

### Community 69 - "Date range schema"
Cohesion: 0.15
Nodes (13): format, type, additionalProperties, properties, required, type, format, type (+5 more)

### Community 70 - "Market data binding schema"
Cohesion: 0.15
Nodes (13): market_data_binding, calendar_id, dataset_id, date_range, price_views, session_policy, timezone, additionalProperties (+5 more)

### Community 71 - "State manifest requirements"
Cohesion: 0.15
Nodes (13): provider_contracts, resolution_policy, runtime_capability_effective_view, runtime_user_invocation_interface, runtime_user_invocation_response, state_bundle_manifest, state_resolution_request, required (+5 more)

### Community 72 - "Data request schema"
Cohesion: 0.15
Nodes (13): additionalProperties, required, type, data_request, calendar_id, corporate_action_policy_id, dataset_id, date_range (+5 more)

### Community 73 - "Run limitations schema"
Cohesion: 0.15
Nodes (13): minLength, pattern, type, default, items, type, uniqueItems, limitations (+5 more)

### Community 75 - "Runtime state request bindings"
Cohesion: 0.17
Nodes (12): $ref, event_state, market_state, consumer_request_id, request_fingerprint, runtime_invocation_response, state_kind, $ref (+4 more)

### Community 76 - "Effective policy bindings"
Cohesion: 0.17
Nodes (12): effective_policies, additionalProperties, required, type, corporate_action_policy_id, event_ordering_policy_id, missing_data_policy_id, state_feed (+4 more)

### Community 77 - "Graphify refresh governance"
Cohesion: 0.18
Nodes (12): 99_archive, Backtest Archive History, Backtest Engine Current, Backtest Gate Evidence History, Controlled Inclusion Contract, GFQ-20260805-BT-001 Initial Current-Engine Leaf, GFQ-20260805-BT-002 Gate Evidence History Leaf, GFQ-20260805-BT-003 Archive History Leaf (+4 more)

### Community 78 - "Input integrity schema"
Cohesion: 0.18
Nodes (11): input_integrity, additionalProperties, required, type, all_required_hashes_verified, hash_algorithm, physical_paths_user_supplied, provider_contract_hashes_verified (+3 more)

### Community 79 - "State resolution manifest policy"
Cohesion: 0.18
Nodes (11): state_resolution_policy, bundle_cardinality, capability_view_mode, partial_success_allowed, policy_id, provider_request_cardinality, provider_response_cardinality, require_single_bundle_covers_all_requests (+3 more)

### Community 80 - "Backtest run required fields"
Cohesion: 0.18
Nodes (11): backtest_id, claims, contract_type, run_id, required, accounting_policy, data_request, decision_policy (+3 more)

### Community 81 - "Execution cost model governance"
Cohesion: 0.20
Nodes (11): AccountingEngine, Accounting Implementation Plan V0.1, Deterministic Cost Model V0.1, Execution Semantics and Cost Model Contract V0.1, Execution Semantics V0.1, No Same-Bar Lookahead, Bounded Fill Simulator Authorization, Deterministic Fill Simulator V0.1 Authorization (+3 more)

### Community 82 - "Backtest gate roadmap"
Cohesion: 0.22
Nodes (11): Backtest Engine Roadmap, BT-GATE-011 Single-Strategy End-to-End Backtest, BT-GATE-011 Execution Path, BT-GATE-012 Multi-Symbol Multi-Session Portfolio Slice, BT-GATE-013 Physical Historical Replay Slice V0.1, BT-GATE-014 Point-in-Time Market State Consumption, Engine Validation Run, Gate Grouping Rule (+3 more)

### Community 83 - "Synthetic market state runner"
Cohesion: 0.42
Nodes (4): strict_json_document(), Any, Path, SyntheticMarketStateRunRequest

### Community 86 - "State consumption overview"
Cohesion: 0.29
Nodes (10): BT-GATE-014 Point-in-Time Market State Consumption, BT-GATE-015 Event State Consumption, Current Project Handoff, Point-in-Time Data Rules, State Consumption Authorization Boundary, BT-GATE-014 Point-in-Time Market State Consumption, BT-GATE-014 Accepted Market State Consumption, BT-GATE-015 Event State Consumption (+2 more)

### Community 87 - "Manifest reusable definitions"
Cohesion: 0.20
Nodes (10): additionalProperties, type, $defs, authorized_state_dataset, safe_id, sha256, pattern, type (+2 more)

### Community 88 - "Input capability claims"
Cohesion: 0.20
Nodes (10): additionalProperties, required, type, claims, broker_cost_realism_claimed, edge_evaluated, fill_realism_claimed, short_tradability_evaluated (+2 more)

### Community 89 - "Contract artifact metadata"
Cohesion: 0.20
Nodes (10): properties, minLength, type, $ref, const, minLength, type, contract_id (+2 more)

### Community 90 - "Data request collection schema"
Cohesion: 0.20
Nodes (10): $ref, data_request, requests, allOf, items, maxItems, minItems, type (+2 more)

### Community 91 - "Market state consumer governance"
Cohesion: 0.22
Nodes (10): BT-GATE-014 Point-in-Time Market State Consumer Contract V0.1, MarketStateStore, One New Boundary Principle, Atomic Market State Validation and Sealing, BT-GATE-014 Non-Physical Consumer Acceptance Packet V0.1, BT-GATE-014 Phase B External Re-review Acceptance V0.1, Governance Operating Model, One Gate, One Scientifically Usable Capability (+2 more)

### Community 92 - "Event state gate handoff"
Cohesion: 0.24
Nodes (10): BT-GATE-015 Point-in-Time Event State Consumption, Closed Consumption Boundaries, FAIL_EVENT_STATE_IDENTITY_MISMATCH, BT-GATE-015 Event State Consumer Gate, Closed Backtest Engine Boundaries, FAIL_EVENT_STATE_IDENTITY_MISMATCH, Frozen Future Physical Slice, Post-Execution Failure Review (+2 more)

### Community 93 - "Gate 011 acceptance packaging"
Cohesion: 0.56
Nodes (9): add_file(), add_text(), add_tree(), governance_files(), main(), Path, ZipFile, sha256_bytes() (+1 more)

### Community 94 - "Gate 012 acceptance packaging"
Cohesion: 0.56
Nodes (9): add_file(), add_text(), add_tree(), governance_files(), main(), Path, ZipFile, sha256_bytes() (+1 more)

### Community 95 - "Gate 013 acceptance packaging"
Cohesion: 0.56
Nodes (9): add_file(), add_text(), add_tree(), governance_files(), main(), Path, ZipFile, sha256_bytes() (+1 more)

### Community 97 - "Preflight manifest writers"
Cohesion: 0.42
Nodes (9): build_data_manifest(), build_universe_manifest(), Any, Path, Manifest writers for RunPreflight outputs., sha256_file(), _validation_manifest(), write_json() (+1 more)

### Community 98 - "End-to-end portfolio contracts"
Cohesion: 0.25
Nodes (9): Engine Validation Is Not Edge Evidence, BT-GATE-011 Single Strategy End-to-End Contract, Single Strategy End-to-End Backtest, BT-GATE-011 Acceptance Packet, BT-GATE-012 Portfolio Slice Contract, Global Replay Order V0.1, Multi-Symbol Multi-Session Portfolio Slice, BT-GATE-012 Portfolio Slice Acceptance Packet (+1 more)

### Community 99 - "Schema artifact references"
Cohesion: 0.22
Nodes (9): $ref, properties, artifact_id, schema_id, schema_version, minLength, type, minLength (+1 more)

### Community 100 - "Artifact hash references"
Cohesion: 0.22
Nodes (9): additionalProperties, minLength, required, type, artifact_ref, artifact_ref, artifact_id, artifact_ref (+1 more)

### Community 101 - "State replay implementation plans"
Cohesion: 0.22
Nodes (9): BacktestInputManifest, RunPreflight State Consumption Plan V0.1, Backtest-Specific State Authorization Boundary, StateReplayFeed Implementation Plan V0.1, State and Execution Separation, StateReplayFeed, BT-GATE-015 Non-Physical Reproduction Boundary, BT-GATE-015 R2 Reproduction Procedure (+1 more)

### Community 102 - "State event ordering contracts"
Cohesion: 0.28
Nodes (9): BoundedMarketStateAvailable, Point-in-Time State Availability, StateAwareGlobalEventOrderV0.2, Typed Core-Four Market State Payload, BoundedEventStateAvailable, Event State Point-in-Time Availability, EventStateStore, Physical Row-to-Sidecar Bijection (+1 more)

### Community 103 - "Physical authorization governance"
Cohesion: 0.28
Nodes (9): BT-GATE-014 Single-Use Physical Consumer Authorization V0.1, BT-GATE-014 Single-Use Physical Consumer Authorization V0.2, BT-GATE-014 Single-Use Physical Consumer Authorization V0.3, Durable Single-Use Authorization Consumption, BT-GATE-014 Single-Use Physical Consumer Authorization V0.4, BT-GATE-014 Single-Use Physical Consumer Authorization V0.5, Restriction Domain Separation, BT-GATE-014 Final Postexecution Acceptance V0.1 (+1 more)

### Community 104 - "Input manifest root schema"
Cohesion: 0.25
Nodes (7): additionalProperties, allOf, description, $id, $schema, title, type

### Community 105 - "Input manifest contract metadata"
Cohesion: 0.25
Nodes (8): minLength, type, const, minLength, type, contract_id, contract_version, properties

### Community 106 - "State request binding schema"
Cohesion: 0.25
Nodes (8): state_request_binding, consumer_request_id, state_kind, additionalProperties, required, type, request_fingerprint, runtime_invocation_response

### Community 107 - "Universe binding schema"
Cohesion: 0.25
Nodes (8): universe_binding, universe_id, additionalProperties, required, type, selected_symbols, universe_manifest, universe_run_id

### Community 108 - "Run specification root schema"
Cohesion: 0.25
Nodes (7): additionalProperties, allOf, description, $id, $schema, title, type

### Community 109 - "Event state review packets"
Cohesion: 0.46
Nodes (8): BT-GATE-015 Point-in-Time Event State Consumer Contract V0.1, BT-GATE-015 Non-Physical Implementation Review Packet V0.2, BT-GATE-015 Non-Physical Implementation Review Packet V0.3, BT-GATE-015 Single-Use Physical Event State Consumer Authorization V0.3, BT-GATE-015 V0.3 Pre-Execution External Review Request, BT-GATE-015 V0.3 Corrected R2 Pre-Execution Packet Readout, TSIS Backtest Engine Current Project Handoff, Fail-Closed Governance Reconciliation

### Community 110 - "Graphify build governance"
Cohesion: 0.29
Nodes (8): Backtest Engine Current Leaf, Controlled Corpus Authority Boundary, Graphify Official Build Protocol, Graphify Semantic Navigation Layer, Graphify Refresh Queue, Semantic Change Refresh Obligation, RunPreflight Before Data Consumption, TSIS Backtest Engine Local Rules

### Community 111 - "Authorized datasets collection"
Cohesion: 0.29
Nodes (7): items, maxItems, minItems, type, uniqueItems, authorized_datasets, dataset

### Community 112 - "SHA256 contract fields"
Cohesion: 0.29
Nodes (7): $ref, contract_sha256, sha256, $ref, $ref, parameters_sha256, sha256

### Community 113 - "Provider contract references"
Cohesion: 0.29
Nodes (7): provider_contract_ref, contract_id, contract_sha256, contract_version, additionalProperties, required, type

### Community 114 - "Price view role enumeration"
Cohesion: 0.29
Nodes (7): $ref, properties, execution, signal, valuation, $ref, $ref

### Community 115 - "Price view bindings"
Cohesion: 0.29
Nodes (7): execution, signal, valuation, additionalProperties, required, type, price_views

### Community 116 - "Universe manifest reference"
Cohesion: 0.29
Nodes (7): universe_id, universe_manifest, universe_run_id, properties, $ref, $ref, $ref

### Community 117 - "Artifact contract references"
Cohesion: 0.29
Nodes (7): additionalProperties, required, type, artifact_contract_ref, contract_id, contract_sha256, contract_version

### Community 118 - "Run specification reusable definitions"
Cohesion: 0.29
Nodes (7): $defs, safe_id, sha256, pattern, type, pattern, type

### Community 119 - "Physical replay governance"
Cohesion: 0.33
Nodes (7): Replay Implementation Plan V0.1, Gap Events Without Imputation, HistoricalReplayFeed, BT-GATE-013 Physical Historical Replay Contract, PhysicalBarReplayAdapter V0.1, Physical Row-to-Event Lineage, Scientific Hash Boundary

### Community 120 - "Market runner V0.4 CLI"
Cohesion: 0.52
Nodes (6): _load_object(), main(), Path, Only authorized CLI entry point for the BT-GATE-014 V0.4 physical run., _sha256(), _verify_closed_binding()

### Community 121 - "Market runner V0.5 CLI"
Cohesion: 0.52
Nodes (6): _load_object(), main(), Path, Only authorized CLI entry point for the BT-GATE-014 V0.5 physical run., _sha256(), _verify_closed_binding()

### Community 123 - "Consumption purpose constraints"
Cohesion: 0.33
Nodes (6): contains, minContains, type, uniqueItems, const, consumption_purposes

### Community 124 - "Backtest date range"
Cohesion: 0.33
Nodes (6): additionalProperties, required, type, date_end, date_start, date_range

### Community 125 - "Fixture kind enumeration"
Cohesion: 0.33
Nodes (6): enum, type, fixture_kind, GOVERNED_HISTORICAL_DATASET, NON_EMPIRICAL_TEST_FIXTURE, TSIS_REAL_DATA_FIXTURE

### Community 126 - "Event preexecution materializer"
Cohesion: 0.53
Nodes (5): main(), Path, Derive the BT-GATE-015 V0.3 config and state from one semantic spec., sha256(), write_json()

### Community 127 - "Backtest vertical slice"
Cohesion: 0.50
Nodes (5): Accounting Engine, HistoricalReplayFeed, Mechanical Decision Order Fill Position Path, RealDataInspector, RunPreflight

### Community 128 - "Claims reference schema"
Cohesion: 0.40
Nodes (5): $ref, claims, $ref, claims, claims

### Community 129 - "State feed binding"
Cohesion: 0.40
Nodes (5): NONE, StateReplayFeed, state_feed, enum, type

### Community 130 - "Market universe binding"
Cohesion: 0.40
Nodes (5): $ref, market_data, universe, $ref, binding

### Community 131 - "Date boundary references"
Cohesion: 0.40
Nodes (5): $ref, properties, $ref, date_end, date_start

### Community 132 - "Preflight implementation plans"
Cohesion: 0.40
Nodes (5): RunPreflight Implementation Plan V0.1, Fail-Closed Data Preflight, RunPreflight, Physical Layout Discovery V0.1, QG5 Real Data Fixture

### Community 133 - "Accepted event state pipeline"
Cohesion: 0.40
Nodes (5): BoundedEventStateAvailable, BoundedMarketStateAvailable, BT-GATE-015 Accepted Non-Physical Evidence, EventStateStore, ReplayBarEvent

### Community 134 - "Event preexecution packager"
Cohesion: 0.70
Nodes (4): main(), Path, sha256(), validate_nested_handoff()

### Community 136 - "Market acceptance packager"
Cohesion: 0.83
Nodes (3): main(), q_suffix(), sha()

### Community 139 - "Effective policies reference"
Cohesion: 0.67
Nodes (3): $ref, effective_policies, policies

### Community 140 - "Integrity reference binding"
Cohesion: 0.67
Nodes (3): $ref, input_integrity, integrity

### Community 141 - "State binding reference"
Cohesion: 0.67
Nodes (3): states, $ref, binding

## Knowledge Gaps
- **564 isolated node(s):** `$schema`, `$id`, `title`, `description`, `type` (+559 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `$defs` connect `Run specification reusable definitions` to `State profile contract`, `Execution accounting policy schema`, `Physical replay adapter`, `State resolution policy schema`, `Data request schema`, `Replay execution policy schema`, `State consumption schema`, `Run specification root schema`, `Strategy specification schema`, `Artifact contract references`, `Backtest realism claims`, `Decision policy schema`?**
  _High betweenness centrality (0.424) - this node is a cross-community bridge._
- **Why does `date_time` connect `Physical replay adapter` to `Accounting engine contracts`, `Deterministic fill simulation`, `Physical market consumer V0.2`, `Event state consumer`, `Historical replay feed`, `Portfolio slice orchestration`, `Market state event loops`, `Single strategy backtest tests`, `Strategy decision contracts`, `End-to-end backtest runner`, `Market state canonicalization`, `Real data inspection`, `Gate execution entrypoints`, `Synthetic event state runner`, `Run specification reusable definitions`, `Market state validation`, `Online accounting pipeline`, `Backtest contract modules`?**
  _High betweenness centrality (0.395) - this node is a cross-community bridge._
- **Why does `id` connect `Backtest policy identifiers` to `Execution accounting policy schema`, `Price view schema`, `Schema artifact references`, `Replay execution policy schema`, `Runtime state request bindings`, `Market data manifest schema`, `Strategy specification schema`, `Input manifest identity`, `Price view role enumeration`, `Universe manifest reference`, `State request bindings`, `Backtest run identity schema`, `State dataset profile schema`, `State request resolution schema`, `State resolution policy configuration`, `Decision policy schema`?**
  _High betweenness centrality (0.284) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `MarketStateContractError` (e.g. with `AcceptanceMatrix` and `MarketStateConsumerV0_1`) actually correct?**
  _`MarketStateContractError` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `DeterministicFillSimulator` (e.g. with `SingleStrategyEndToEndBacktestRunner` and `CostBreakdownV0`) actually correct?**
  _`DeterministicFillSimulator` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `MarketStateConsumerV0_1` (e.g. with `AcceptanceMatrix` and `BoundedMarketStateAvailable`) actually correct?**
  _`MarketStateConsumerV0_1` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `$id`, `title` to the rest of the system?**
  _564 weakly-connected nodes found - possible documentation gaps or missing edges._