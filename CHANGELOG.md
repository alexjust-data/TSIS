## 2026-08-22 - TSIS_GRAPHIFY_REFRESH_20260822

- Rebuilt the governed CTO, Applied Architecture, Data Foundation and Backtest Engine graph leaves.
- Rebuilt the CTO, Data Foundation and TSIS root merges with the official Graphify flow.
- Preserved and namespaced every input hyperedge instead of accepting Graphify merge truncation.
- Added the current `04_TSIS_SCREENERS` and `05_TSIS_STATISTICS_PATTERNS` topology through their governed leaf coverage.
- Removed semantically obsolete source paths from the published graphs.
- Persisted official multigraph diagnostics and an independent terminal audit for all five requested roots.
- Final root: 10,573 nodes, 20,234 edges, 317 hyperedges and 658 communities.

## 2026-08-21 | Repository module map and experiment-root correction

- Added `04_TSIS_SCREENERS` for causal/PIT initial filtering and
  `05_TSIS_STATISTICS_PATTERNS` for descriptive statistical discovery.
- Renumbered live WebSocket and Offline RL modules to
  `06_TSIS_webSocket_SmallCaps` and `07_TSIS_Offline_RL`.
- Removed `06_TSIS_Trading_voice` from the active Repository System Map.
- Established `03_TSIS_Lab/04_experiments` as the canonical location for
  research-experiment definitions, runs and outputs.
- Retired `G:/TSIS/data/research_experiments`; `G:/TSIS/data` remains the
  physical data and governed-materialization plane.
- Corrected the module spelling from `SCRENNERS` to `SCREENERS`.
## 2026-08-17 | Wake-up RTH blind-panel repair gate

- Preserved the completed 2,400-session, 4,447-candidate development scan.
- Invalidated the first 240-case gallery because all rows came from the close
  RTH bucket, and added deterministic temporal balancing plus 25 terminal
  controls.
- The bounded repair probe passed; the full panel-only rebuild remains
  human-launched and D07/A-B/OOS remain closed.

## 2026-08-17 | Project-wide readable path and naming policy

- Added `PATH_NAMING_POLICY.md` as mandatory root governance for human-readable
  names, registered abbreviations and measured final-path preflight.
- Set the TSIS canonical-root operational budget to 235 preferred and 240 hard
  absolute characters, without relying on Windows or Git long-path opt-ins.
- Applied the first governed migration to `00_CTO/04_MARKET_STATES_CREATION`
  with exact path-map and SHA-256 preservation evidence.

## 2026-07-25 | Market State on-demand execution-chain joint review closed

- Recorded `market_state_on_demand_execution_chain_joint_review_v0_1` under `08_RUNTIME_CAPABILITIES`.
- Reviewed Request, Profile Resolver, Universe Resolver, Source Resolver, Partition/Coverage Resolver, Execution Plan, Run Lifecycle, Materializer, Validator and Candidate Dataset Registry contracts as one chain.
- Closed with 0 hard findings and 2 restrictions: bounded execution authorization only, and future execution must use the refined Partition/Coverage disposition model.
- Preserved the boundary: no requests, execution plans, resolver executions, run records, source reads, materializer executions, validator executions, registry writes, datasets, production or downstream consumption.
- Next gate is `market_state_bounded_on_demand_execution_authorization_v0_1`.

## 2026-07-25 | Market State run lifecycle and manifest design closed

- Recorded `market_state_run_lifecycle_and_manifest_design_v0_1` and `market_state_run_lifecycle_and_manifest_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- Defined future run identity, run statuses, allowed transitions, pre-run manifest, heartbeat, final manifest, failure manifest, recovery manifest, idempotency and authorization-consumption semantics.
- Preserved the boundary: no run records, manifests, heartbeats, state transitions, recovery actions, execution authorization consumption, execution plan consumption, materializer execution, validator execution, registry writes, datasets, production or downstream consumption.
- Next gate is `market_state_on_demand_execution_chain_joint_review_v0_1`.

## 2026-07-25 | Market State candidate dataset registry design closed

- Recorded `market_state_candidate_dataset_registry_design_v0_1` and `market_state_candidate_dataset_registry_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- Defined registry identity, dataset fingerprints, validation state, reuse eligibility, promotion review eligibility, downstream boundary, coverage reconciliation, supersession and quarantine references for future candidate Market State outputs.
- Preserved the boundary: no registry entries written, registry runtime reads, dataset registrations, promotions, supersessions, quarantine transitions, official dataset, production or downstream consumption.
- Next gate is `market_state_run_lifecycle_and_manifest_design_v0_1`.

## 2026-07-25 | Market State validator design closed

- Recorded `market_state_validator_design_v0_1` and `market_state_validator_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- Defined validation blocks for candidate Market State materializer outputs: scope, schema, grain, identity, temporal legality, lineage, partition completeness, content, fingerprints and determinism readiness.
- Preserved the boundary: no validator execution, candidate file reads, parquet reads, validation reports, partition status changes, quarantine actions, registry writes, production or downstream consumption.
- Next gate is `market_state_candidate_dataset_registry_design_v0_1`.

## 2026-07-25 | Market State materializer design closed

- Recorded `market_state_materializer_design_v0_1` and `market_state_materializer_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- The design defines how a future materializer consumes one authorized frozen execution plan and emits candidate unvalidated Market State outputs.
- Boundary preserved: 0 materializer executions, 0 builder executions, 0 source rows read, 0 staging directories, 0 candidate files, 0 manifests, 0 validation reports and 0 dataset registry entries written.

## 2026-07-25 | Market State partition and coverage resolver design closed

- Recorded `market_state_partition_and_coverage_resolver_design_v0_1` and `market_state_partition_and_coverage_resolver_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- The design defines mutually exclusive logical partition dispositions and separates source availability evidence from output partition disposition.
- Boundary preserved: 0 partition/coverage resolver executions, 0 partition manifests, 0 coverage manifests, 0 registry runtime reads, 0 source rows read, 0 execution plans created and 0 dataset registry entries written.

## 2026-07-25 | Market State source resolver design closed

- Recorded `market_state_source_resolver_design_v0_1` and `market_state_source_resolver_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- The design defines how future runtime resolution will populate the `resolved_sources` block of a Market State execution plan from profile-required source aliases.
- Boundary preserved: 0 source resolver executions, 0 source registry/contract/schema/policy runtime reads, 0 source parquet files read, 0 source rows read, 0 execution plans created and 0 dataset registry entries written.

## 2026-07-25 | Market State universe resolver design refined

- Refined `market_state_universe_resolver_design_v0_1` to make `resolved_universe_fingerprint`, `coverage_status`, `blocking_findings` and resolved/blocked/excluded context accounting explicit.
- Added zero-execution counters for `instrument_session_contexts_created` and `instrument_master_runtime_reads`.
- Boundary preserved: still 0 universe resolver executions, 0 manifests, 0 source rows, 0 execution plans, 0 datasets and 0 registry writes.

## 2026-07-25 | Market State universe resolver design closed

- Recorded `market_state_universe_resolver_design_v0_1` and `market_state_universe_resolver_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- The design defines how future runtime resolution will populate the `resolved_universe_and_scope` block of a Market State execution plan from point-in-time universe and session intent.
- Boundary preserved: 0 universe resolver executions, 0 universe manifests created, 0 calendar runtime reads, 0 instrument identity runtime reads, 0 execution plans created, 0 source rows read and 0 dataset registry entries written.

## 2026-07-25 | Market State profile resolver design closed

- Recorded `market_state_profile_resolver_design_v0_1` and `market_state_profile_resolver_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- The design defines how future runtime resolution will populate the `resolved_profile` block of a Market State execution plan from exact profile intent.
- Boundary preserved: 0 profile resolver executions, 0 profile registry runtime reads, 0 execution plans created, 0 source rows read, 0 Market State records emitted, 0 parquet files and 0 dataset registry entries written.

## 2026-07-24 | Market State execution plan contract design closed

- Recorded `market_state_execution_plan_contract_design_v0_1` and `market_state_execution_plan_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- The contract defines the immutable resolution artifact that a future materializer must consume after request validation and resolver execution.
- Boundary preserved: 0 execution plans created, 0 resolver executions, 0 source rows read, 0 Market State records emitted, 0 parquet files and 0 dataset registry entries written.

## 2026-07-24 | Market State request contract design closed

- Recorded `market_state_request_contract_design_v0_1` and `market_state_request_contract_v0_1.json` under `08_RUNTIME_CAPABILITIES`.
- The contract defines normalized Market State request intent, fingerprint inputs and blocking rules before resolver or execution-plan work.
- Boundary preserved: 0 request records created, 0 execution plans, 0 source rows read, 0 Market State records emitted, 0 parquet files and 0 dataset registry entries written.

## 2026-07-24 | Market State on-demand capability design closed

- Recorded `market_state_on_demand_capability_design_v0_1` under `08_RUNTIME_CAPABILITIES`.
- The design defines Market State as a future request-resolved runtime capability over `market_state_core_four_intraday_profile_v0_1`.
- Boundary preserved: 0 requests executed, 0 source rows read, 0 Market State records emitted, 0 parquet files and 0 dataset registry entries written.

## 2026-07-24 | Runtime capabilities architecture recorded

- Added `08_RUNTIME_CAPABILITIES` under Applied Architecture as the bridge from representation/profile governance to repeatable request-driven generation.
- Recorded `runtime_capabilities_architecture_v0_1` with Request, Resolver, Execution Plan, Materializer, Validator, Dataset Registry and idempotency roles.
- Boundary preserved: no request resolver, materializer execution, source reads, dataset writes, production or downstream consumption were opened.

## 2026-07-24 | Event State operational registry policy design recorded

- Recorded design-only operational registry / consumption policy for `event_state_core_four_intraday_profile_v0_1`.
- The design allows semantic profile reference for planning and future authorization inputs only; it does not create or authorize an Event State dataset.
- Boundary preserved: no Event State physical consumption, materialization, official parquet, production, downstream use, event detection or source market-data reads were opened.

## 2026-07-24 | Event State profile artifact validation closed

- Validated the official semantic Event State profile registry package for `event_state_core_four_intraday_profile_v0_1`.
- Accepted run `event_state_profile_artifact_validation_v0_1_20260724T204410Z` checked 4 registry artifacts with 0 SHA-256 mismatches, 0 invariant failures and 0 hard validation failures.
- Boundary preserved: no Event State dataset promotion, official parquet, materialization, production, downstream consumption, source market-data reads or unbounded execution were opened.

## 2026-07-24 | Event State semantic profile promoted

- Promoted `event_state_core_four_intraday_profile_v0_1` as an official semantic Event State profile with restrictions under `03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION`.
- Accepted run `event_state_profile_promotion_v0_1_20260724T203016Z` wrote 4 official profile registry artifacts and preserved the accepted bounded `session_opened` evidence lineage.
- Boundary preserved: no Event State dataset promotion, official parquet, materialization, production, downstream consumption, new Event Types or unbounded execution were opened.

## 2026-07-24 | Event State profile promotion review closed

- Reviewed bounded Event State profile evidence under `03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION`.
- Accepted run `event_state_profile_promotion_review_v0_1_20260724T201046Z` approved a separate semantic Event State profile promotion authorization with restrictions; 15 evidence artifacts checked, 0 hash/count mismatches and 0 hard review failures.
- Boundary preserved: no Event State profile promotion was executed, no dataset promotion, official parquet, materialization, production, downstream consumption, new Event Types or unbounded execution were opened.

## 2026-07-24 | DAS CMDAPI PASS-candidate max read-only capture corrected

- Corrected the live DAS evidence capture orientation: for the operator request "use our screener/filter", the canonical ticker source is the TSIS screener candidate file `C:/TSIS_Data/data/screener/runs/das_cmdapi_live_20260724T165627Z/candidates.csv` filtered to `filter_status=PASS`.
- The replay/capture command must use `--candidate-file ... --candidate-file-status PASS --skip-screener --max-readonly`; it intentionally does not use DAS `TOPLIST` as a filter and does not use an external/governed TSIS universe.
- `--scan-tsis-universe` remains an opt-in diagnostic/recovery mechanism for a different question; it is not the operator flow for replaying today's TSIS screener PASS list.
- Run `C:/TSIS_Data/data/raw_cmdapi/runs/das_cmdapi_live_candidate_file_pass_max_readonly_20260724T195551Z/` loaded 17/17 PASS candidates and produced structured locate evidence under `derived/` with 34/34 `%SLRET` price rows (`SAGE` and `TESTSL`) and 0 missing price rows. The raw capture later closed with DAS socket `ConnectionResetError(10054)`, so the run-level `final_summary.json` status is `FAIL`; this is a connection-close status, not a locate extraction failure.
- Broker safety boundary unchanged: order, cancel, replace, complex-order and locate-order commands remain blocked; invalid account/password now aborts by default when account-state or locate inquiry capture is enabled.

## 2026-07-24 | Event State candidate dataset review closed

- Reviewed bounded Event State candidate output `event_state_candidate_dataset_review_v0_1_20260724T194315Z` under `03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION`.
- Decision: approved 8 non-official candidate records as bounded Event State evidence with restrictions and no promotion; 1 exact-binding blocked context remains blocked.
- Boundary preserved: no Event State profile/dataset promotion, official parquet, materialization, production, downstream consumption, new Event Types or unbounded execution were opened.

## 2026-07-24 | Live DAS CMDAPI read-only universe scan and data-root override recorded

- Updated `04_TSIS_webSocket_SmallCaps` so DAS CMDAPI capture preserves prior seed/TOPLIST behavior and adds opt-in TSIS universe scanning from the governed Data Foundation market-cap reference.
- Recorded the current operator-directed DAS CMDAPI data root as `C:/TSIS_Data/data` for this read-only capture path; raw run evidence is under `C:/TSIS_Data/data/raw_cmdapi/runs/<run_id>` and screener evidence under `C:/TSIS_Data/data/screener/runs/<run_id>`.
- Large scanner evaluations above 100 symbols now require explicit `--allow-large-scan`; active full-capture subscriptions and broker safety limits remain separate.
- Broker command boundary unchanged: order/cancel/replace/complex-order/locate-order command prefixes remain blocked, while read-only market, account-state and locate inquiry commands can be requested by `--max-readonly`.
- Future-agent orientation: if a DAS run evaluates only `SOXS` after `TOPLIST: parsed 0 symbols`, check that the launch used `--scan-tsis-universe --allow-large-scan --max-screener-symbols <N>` and that the market-cap reference at `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/market_cap_cutoff_lt_1b_active_inactive.csv` loaded.

## 2026-07-24 | Event State bounded execution-chain physical validation closed

- Added bounded physical validation artifacts under `03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION`.
- Accepted run `event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z` validated the accepted bounded execution output: 8 candidate records checked, 0 schema/hash/fingerprint/binding/lineage/authority/determinism failures and 0 hard validation failures.
- Boundary preserved: the 1 exact-binding blocked context remains blocked; no Event State parquet, official profile/dataset promotion, production, downstream consumption, new Event Types or unbounded execution were opened.

## 2026-07-24 | Event State bounded execution-chain candidate output closed

- Executed accepted bounded run `event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z` under `03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION`.
- Result: 3 Event Instances, 3 Event Window Bindings, 9 instrument-session projections, 8 non-official Event State candidate JSONL records, 1 policy-blocked context, 0 fallback uses and 0 hard validation failures.
- Boundary preserved: no Event State parquet, official dataset/profile promotion, production, downstream consumption, event detection outside `session_opened` or Market State rebuild was opened.

## 2026-07-24 | Applied Architecture Event State bounded authorization issued

- Issued the first bounded Event State execution-chain authorization for the `session_opened`/core-four path.
- The future run is limited to 3 XNYS sessions, 3 instruments and the validated non-official Scale C Market State candidate parquet.
- No Event State rows, parquet, materialization, production or downstream consumption were created or authorized for use.

## 2026-07-24 | Applied Architecture Event State design-chain review closed

- Closed the Event State design-chain joint review for the first `session_opened`/core-four path.
- The chain is approved for a future bounded execution authorization with restrictions.
- No Event State rows, Market State parquet consumption, materialization, production or downstream consumption were authorized.

## 2026-07-24 | Applied Architecture Event State integration design recorded

- Closed the design-only Event State integration gate for the first `session_opened`/core-four path.
- The design preserves Market State as a referenced parent profile and requires exact-one event, window, projection, role and legality bindings.
- No Event State rows, Market State parquet consumption, materialization, production or downstream consumption were authorized.

## 2026-07-24 | Applied Architecture Event State projection design recorded

- Closed the design-only instrument-session projection gate for Event State.
- The projection will bridge exchange-session `session_opened` events/windows to instrument-session Market State context in a future execution gate.
- No projections, Event State rows, materialization, production or downstream consumption were authorized.

## 2026-07-24 | Applied Architecture Market State/Event State compatibility recorded

- Closed the design-only Market State Profile Compatibility gate for `event_state_core_four_intraday_profile_v0_1`.
- The official `market_state_core_four_intraday_profile_v0_1` is semantically compatible as parent profile, but future Event State execution requires instrument-session projection.
- No physical Market State consumption, Event State materialization, production or downstream consumption was authorized.

## 2026-07-24 | Applied Architecture Event Window Binding Design recorded

- Closed the design-only Event Window Binding gate for `event_type:market_data:session_opened`.
- The design separates Event Window Definition from future Event Window Binding and preserves `state_role` versus `consumption_legality`.
- No windows, instances, detectors, parquet, production or downstream consumption were authorized.

## 2026-07-24 | Applied Architecture Event Instance Binding Design recorded

- Recorded the design-only Event Instance Binding contract for `event_type:market_data:session_opened`.
- Native identity is exchange-session scoped; instrument association remains a future projection, not part of the Event Type or Event Instance identity.
- No Event Instances, detectors, Event State materialization, production or downstream consumption were authorized.

## 2026-07-24 | Applied Architecture Event Type admission review recorded

- Closed the initial Event Type admission review under `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION`.
- `session_opened` is accepted with restrictions for exchange-session design only; `halt_resumed` remains investigational pending timestamp/source availability reconciliation.
- No event detection, Event Instances, Event State materialization, production or downstream consumption was authorized.

## 2026-07-24 - Event identity stability future field queued

- Recorded `event_identity_stability` as a future Event Type Registry v0.2 consideration with candidate values `immutable`, `conditionally_stable`, `source_dependent` and `experimental`.
- Preserved v0.1 boundaries: no registry schema field was added to the current snapshot, no candidate was admitted, no detector/instance/window/builder/materialization gate was opened and the snapshot hash remains unchanged.

## 2026-07-24 - Event Type Registry initial candidate population recorded

- Added `07_EVENT_STATE_INTEGRATION/event_type_registry_initial_population_authorization_v0_1.md`, `configs/event_type_registry_initial_population_scope_v0_1.json`, `event_type_registry_initial_population_snapshot_v0_1.json` and `event_type_registry_initial_population_readout_v0_1.md`.
- Recorded two candidate families and two candidate Event Types as `investigational_candidate`: `event_type:regulatory:halt_resumed` and `event_type:market_data:session_opened`; accepted Event Types remain 0.
- Boundary preserved: no event admission, detector execution, instances, windows, Event State builder/materialization, parquet, production, downstream consumption or Execution State design was authorized.

## 2026-07-24 - Variable Attribute Admission record template recorded

- Added `03_VARIABLE_ATTRIBUTE_ADMISSION_RECORD_TEMPLATE_v0_1.md` as the standard review form for proposals such as ATR, RVOL, VWAP, spread fields, Event variables and outcome labels.
- Renumbered the table-status documents so the matrix is now `04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md`, reconciliation authorization is `05_tables_000_018_evidence_reconciliation_authorization_v0_1.md`, and reconciliation readout is `06_tables_000_018_evidence_reconciliation_readout_v0_1.md`.
- Boundary preserved: the template does not admit variables, modify schemas, authorize builders/materializations, promote datasets or open downstream consumption.

## 2026-07-24 - Variable and Attribute Admission Policy recorded

- Added `02_VARIABLE_AND_ATTRIBUTE_ADMISSION_POLICY_v0_1.md` as the bridge policy explaining why raw source attributes, derived features, State variables, Event variables, outcome labels and quality/lineage/governance attributes may be discovered, mapped, admitted, blocked or rejected.
- Consolidated the existing distributed policy from Information Object admission, Operational Mapping, Builder Validation and Market State/Event State profile gates.
- Boundary preserved: no new variables admitted, no schemas changed, no builders/materializations authorized, no datasets promoted and no downstream consumption opened.

## 2026-07-24 - Event Type Registry seed schema designed

- Closed `event_type_registry_seed_design_v0_1` under Applied Architecture as an empty registry schema design.
- Recorded namespaces, status model, identity rules, admission review requirements and future binding guards while keeping `accepted_event_types = 0`.
- Boundary preserved: no event registry population, detection, instance binding, Event State materialization, production or downstream consumption is authorized.

## 2026-07-24 - Tables 000-018 evidence reconciled against Data Foundation

- Executed `tables_000_018_evidence_reconciliation_against_data_foundation_registry_v0_1` and accepted run `tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z`.
- Reconciled 19/19 representation table rows against Data Foundation schemas, dataset contracts, registry entries, consumption policies, validators and status matrix evidence: 13 restricted datasets, 2 validated candidates with restrictions, 3 partial semantic/physical reconciliations and 0 unresolved rows.
- Boundary preserved: `official_datasets_inferred = 0`, no official dataset registry write, no official parquet, no production, no downstream consumption, no Event State materialization and no event detection.

## 2026-07-24 - Tables 000-018 authority axes normalized

- Refined the applied-architecture `000-018` institutional status matrix to separate `physical_authority`, `semantic_authority` and `execution_authority`.
- Clarified the Event State row: Event Type contract shape is ready, while registry schema remains pending seed design and accepted event types remain 0.
- Boundary preserved: no official dataset registry update, official parquet, production, downstream consumption, event detection or Event State materialization is authorized.

## 2026-07-24 - Tables 000-018 institutional status matrix recorded

- Added the applied-architecture institutional status matrix for representation tables `000-018`.
- Clarified that the 2026-07-20 Discovery Pass remains historical discovery evidence, not the current authority matrix.
- Boundary preserved: no official dataset registry update, no official parquet, no production, no downstream consumption, no Event State execution and no dataset promotion is authorized.

## 2026-07-23 - Event policy state normalized

- Normalized the Event State policy boundary: Event Type registry contract shape is ready, but registry schema and population remain closed.
- Restricted the immediate next gate to `event_type_registry_seed_design_v0_1`.
- Added event-domain and epistemic-role separation to avoid conflating market phenomena with scanner, research, system or governance events.

## 2026-07-23 - Event policy recorded

- Recorded the standing Event State event policy under applied architecture before populating any Event Type registry.
- Clarified that event grammar can be designed while the event dictionary remains empty: `accepted_event_types = 0`.
- Boundary preserved: no event admission, event detection, Event State builder, materialization, parquet, production or downstream consumption is authorized.

## 2026-07-23 - Event type/family contract design recorded

- Added the Event State integration design area and an operational contract design for Event Family/Event Type authority before event instance binding.
- Preserved the distinction between conceptual event taxonomy and populated `event_type_id` registry entries.
- Boundary preserved: no event detection, Event State builder, materialization, parquet, production or downstream consumption is authorized.

## 2026-07-23 - Event State profile contract design recorded

- Added the first Event State profile contract design, `event_state_core_four_intraday_profile_v0_1`, under applied architecture.
- Bound it to the official `market_state_core_four_intraday_profile_v0_1` parent profile while leaving event instance binding, event window binding, builders, materialization and consumption closed.
- Preserved boundaries: no Event State execution, parquet, production or downstream consumption is authorized.
## 2026-07-23 - Physical data plane root aligned to G

- Updated active root/module documentation to reference `G:/TSIS/data` as the physical data plane now used for TSIS heavy outputs, materializations and data-provider roots, including `PATH_MIGRATION_2026_07_22.md`, Lab local rules and the mounted `G:/TSIS/data/README.md` physical-plane note.
- Boundary preserved: physical path location does not define dataset semantics; Data Foundation contracts remain the authority for data meaning, quality gates, price views and consumption policy.
- Backtest Engine decision recorded separately in `02_TSIS_BACKTEST_ENGINE/docs/00_system/backtest_engine_boundary_and_data_plane_v0_1.md`.
## 2026-07-23 - Market State profile family architecture recorded

- Recorded `market_state_core_four_intraday_profile_v0_1` as the first member of a governed TSIS Market State profile family, with future profiles required to follow independent lifecycle gates.
- Added an Event State architecture seed under applied architecture that references valid Market State profiles instead of redefining Market State.
- Preserved boundaries: no official dataset registry update, no official parquet, no production, no downstream consumption, no Event State execution and no full-history/full-universe execution.
## 2026-07-23 - Market State core-four official profile promoted

- Registered `market_state_core_four_intraday_profile_v0_1` as an applied-architecture official profile with restrictions and validated the registry package.
- Accepted promotion run `official_market_state_candidate_promotion_v0_1_20260723T193403Z` and artifact validation run `official_market_state_profile_artifact_validation_v0_1_20260723T193711Z`; registry artifacts checked = 4, hash mismatches = 0, invariant failures = 0, hard failures = 0.
- This is not complete TSIS Market State and does not authorize operational dataset registry updates, official parquet, production, downstream consumption or full-history/full-universe execution.

## 2026-07-23 - Market State core-four official-profile review approved

- Review-only gate `official_market_state_candidate_promotion_review_v0_1_20260723T192107Z` approved `market_state_core_four_intraday_profile_v0_1` for a separate official-profile promotion authorization with restrictions.
- Evidence checked: 8 artifacts, 480 resolution records, 104 integrated candidate records, 104 physical candidate rows, parquet SHA-256 `b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2`, 1768 value mappings, 3848 semantic rebuild field comparisons and 0 hard failures.
- No official Market State promotion, official parquet write, production builder, downstream consumption or full-history/full-universe execution was authorized.

## 2026-07-23 - Scale C Market State validation chain closed

- Scale C Market State closed with restrictions through candidate physical validation: 120 contexts, 480 resolution records, 104 candidate physical rows and 0 hard validation failures.
- Candidate parquet SHA-256: `b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2`. Official Market State remains not authorized.

## 2026-07-23 - Scale C Market State surface gate closed

- Market State Scale C advanced from frozen sample to closed run-local execution surface construction: accepted run `experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z`.
- Frozen surface fingerprint `34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554`; next step is a separate builder/resolution authorization.

## 2026-07-23 | phase c | Scale C sample preflight v0.2 closed

- Updated `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/06_MARKET_STATE_INTEGRATION` with the accepted Scale C sample preflight v0.2 run and readout.
- Run `experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z` closed `PASS_WITH_RESTRICTIONS`: 120 frozen contexts, 10 selected instruments, 8 governed historical XNYS sessions, 480 expected resolution records and sample fingerprint `67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d`.
- Boundary preserved: no Scale C execution surface, builders, Market State integration/materialization/parquet, official State, downstream consumption, promotion or full-history/full-universe execution is authorized.

## 2026-07-23 | phase c | Scale C sample preflight authorization issued

- Updated `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/06_MARKET_STATE_INTEGRATION` with a bounded Scale C sample preflight authorization and scope.
- Scale C is authorized only for historical sample preflight across finite governed XNYS sessions; Scale C execution, builders, Market State materialization, official State, downstream consumption, promotion and full-history/full-universe execution remain closed.

## 2026-07-22 | root path migration | TSIS top-level module names realigned

- Added `PATH_MIGRATION_2026_07_22.md` as the canonical transition map for top-level path resolution.
- Current canonical roots: `01_TSIS_DATA_FOUNDATION`, `02_TSIS_BACKTEST_ENGINE`, `03_TSIS_Lab`, `04_TSIS_webSocket_SmallCaps`, `05_TSIS_Offline_RL` and `06_TSIS_Trading_voice`.
- Legacy resolution map: `00_TSIS_Lab -> 03_TSIS_Lab`, `01_TSIS_backtest_SmallCaps -> 01_TSIS_DATA_FOUNDATION`, `02_TSIS_webSocket_SmallCaps -> 04_TSIS_webSocket_SmallCaps`, `03_TSIS_Offline_RL -> 05_TSIS_Offline_RL` and `04_TSIS_Trading_voice -> 06_TSIS_Trading_voice`.
- Boundary preserved: `00_CTO/14_BACKTEST_ENGINE` remains the architecture/theory authority for the backtester; `02_TSIS_BACKTEST_ENGINE` is the future implementation area and must consume Data Foundation contracts rather than owning data certification.
- Audit note: historical changelogs, archives, runtime evidence and Graphify outputs may still contain legacy paths; active code/config/test/governance files should resolve through the migration map until a full refresh/rewrite is explicitly authorized.

## 2026-07-22 | phase b | experimental core-four Market State materialization execution passed with restrictions

- Updated `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering` with the bounded core-four materializer, execution run and readout.
- Run `experimental_core_four_market_state_materialization_v0_1_20260722T081155Z` converted 8 accepted candidate JSONL records into 8 non-official physical candidate rows and 1 candidate parquet with 0 source market-data reads, 0 hard validation failures, 0 roundtrip failures and 0 semantic rebuild differences.
- Boundary preserved: official Market State, production builder, downstream consumption, full-history/full-universe execution and dataset promotion remain unauthorized; next gate is physical candidate validation.

## 2026-07-22 | phase b | materialization authorization scope fingerprint rules clarified

- Updated the core-four materialization authorization scope to remove fingerprint circularity and define semantic rebuild determinism.
- Added canonical policy/restriction JSON derivation rules before materializer implementation.
- Boundary preserved: no materialization execution or parquet output occurred.

## 2026-07-22 | phase b | bounded core-four Market State materialization authorization issued

- Updated `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering` with a scoped authorization for future experimental core-four candidate materialization.
- Result: `experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS`; execution is still not run.
- Boundary preserved: no materializer, parquet output, source data reread, production builder, downstream consumption, full-history/full-universe execution or official Market State promotion occurred.

## 2026-07-22 | phase b | core-four Market State materialization design closed with restrictions

- Updated `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering` with a design-only core-four Market State materialization contract.
- Result: `core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS`; the next possible step is a separate bounded authorization, not execution.
- Boundary preserved: no parquet materialization, production builder, source data reread, downstream consumption, full-history/full-universe execution or official Market State promotion is authorized.

## 2026-07-21 | phase b | experimental core-four Market State integration execution passed with restrictions

- Added the non-production core-four Market State integration execution authorization, scope and probe under `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/06_MARKET_STATE_INTEGRATION/`.
- Executed `experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z` from accepted v0.10 core-four resolution records only: `PASS_WITH_RESTRICTIONS`, 10 contexts seen, 8 candidate JSONL records emitted, 2 required-object-blocked contexts rejected, 0 context/contract/determinism failures, 0 future leaks and 0 blocked values admitted.
- Boundary preserved: source market data rows read = 0, parquet files written = 0, production builder = false, State consumption = false and dataset promotion = false. The next possible gate is design-only `core_four_market_state_materialization_design`.

## 2026-07-21 | phase b | experimental bounded quality and lineage gate passed with restrictions

- Updated `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering` with the bounded quality/lineage gate for the non-production State Builder probe.
- Executed `experimental_state_builder_probe_v0_9_20260721T184537Z`: `PASS_WITH_RESTRICTIONS`, 12,271 rows read within a 20,000-row cap, 0 core-four builder blockers, 2 quote-dependent blockers and 8 promotion-only restrictions.
- Next allowed gate is experimental builder validation execution for the core four Objects only. Production builders, State materialization, Market State Integration, quote-dependent builders and dataset promotion remain closed.

## 2026-07-21 | phase b | experimental bounded grain gate passed with restrictions

- Added `experimental_bounded_grain_validation_authorization_v0_1.md` and `configs/experimental_bounded_grain_scope_v0_1.json` for the non-production State Builder probe.
- Updated `experimental_state_builder_probe.py` to `experimental_state_builder_probe_v0_8` with `bounded_grain_validation`, candidate key checks, duplicate classification, null-key reporting, hidden-dimension findings and raw quote same-timestamp reporting.
- Executed run `experimental_state_builder_probe_v0_8_20260721T171358Z`: `bounded_grain_validation = PASS_WITH_RESTRICTIONS`, `rows_read = 12271`, `maximum_rows_authorized = 20000`, `null_key_rows = 0`, `duplicate_key_groups = 1016`, `identical_duplicate_groups = 1001`, `conflicting_duplicate_groups = 15` and `raw_quotes_same_timestamp_groups = 16`.
- Added `experimental_state_builder_probe_bounded_grain_readout_v0_1.md` and updated probe README, Builder Validation README, feature-engineering README and local AGENT handoff.
- Boundary preserved: no feature builder execution, production builder, State consumption, full data read, physical materialization, dataset promotion or Market State Integration was authorized. Next gate is `bounded_quality_and_lineage_validation` design.

## 2026-07-21 | 03_TABLES_feature_engineering | Experimental bounded identity and temporal gate passed

- Updated the non-production State Builder probe to `experimental_state_builder_probe_v0_7` and added explicit bounded sample authorization/scope artifacts.
- Executed `experimental_state_builder_probe_v0_7_20260721T161612Z`: `bounded_sample_validation = PASS_WITH_RESTRICTIONS`, 6,271 rows read within the 10,000-row cap, 0 identity failures, 0 timestamp parse failures, 0 future-bar leaks and 0 daily availability policy failures.
- Preserved hard boundaries: no grain validation, feature builder execution, production builder, State consumption, full data read, physical materialization, dataset promotion or Market State Integration is authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | Experimental column binding blockers resolved with restrictions

- Added experimental policies `daily_row_availability_policy_v0_1.md` and `intraday_bar_identity_and_cutoff_policy_v0_1.md` for metadata-only resolution of daily availability and intraday bar identity/cutoff context.
- Updated `experimental_column_binding_registry_v0_1.json`: resolved `004_master_daily_table.as_of_utc`, `014_master_intraday_bar_table_candidate.instrument_id` and `014_master_intraday_bar_table_candidate.decision_timestamp_or_bar_end` as governed restrictions, and corrected eight `valid_for_*_candidate` expected type families from `date` to `boolean`.
- Updated the non-production State Builder probe to `experimental_state_builder_probe_v0_6` so `identity_resolution_required` produces `RESOLVED_WITH_RESTRICTIONS` instead of a clean pass.
- Executed `experimental_state_builder_probe_v0_6_20260721T154601Z`: `logical_column_resolution = PASS_WITH_RESTRICTIONS`, 154 fields checked, 125 resolved, 22 resolved with restrictions, 6 non-critical unresolved, 0 critical blockers and 0 failed aliases.
- Preserved hard boundaries: no production builder, State consumption, bounded/full data read, grain validation, temporal value validation, physical materialization, dataset promotion or Market State Integration is authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | Experimental logical-to-physical column binding gate executed

- Added `experimental_column_binding_registry_v0_1.json` for explicit metadata-only resolution from active logical fields to physical columns, partition keys, manifest fields, dataset metadata and restricted cast policies.
- Updated the non-production State Builder probe to `experimental_state_builder_probe_v0_5` with `logical_to_physical_binding_check_only`.
- Executed `experimental_state_builder_probe_v0_5_20260721T144225Z`: 154 logical fields checked, 118 resolved, 27 resolved with restrictions, 9 unresolved; 8 aliases pass with findings and 2 aliases remain blocked (`004_master_daily_table`, `014_master_intraday_bar_table_candidate`).
- Preserved hard boundaries: no production builder, State consumption, bounded/full data read, grain validation, temporal value validation, physical materialization, dataset promotion or Market State Integration is authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | Experimental schema metadata gate failed pending column binding

- Updated the non-production State Builder probe to `experimental_state_builder_probe_v0_4` with `binding_and_schema_check_only` as a metadata-only gate.
- Executed `experimental_state_builder_probe_v0_4_20260721T123345Z`: contract/path/binding gates pass, `schema_resolution = EXECUTED`, `schema_validation = FAILED`, 3 of 10 active aliases pass minimum schema metadata and 7 require logical-to-physical column/partition/manifest/type binding.
- Added `experimental_state_builder_probe_schema_metadata_readout_v0_1.md`; the next required artifact is `configs/experimental_column_binding_registry_v0_1.json`.
- Preserved hard boundaries: no production builder, State consumption, bounded/full data read, grain validation, temporal value validation, physical materialization, dataset promotion or Market State Integration is authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | Experimental physical source binding completed

- Bound the final active experimental physical source batch for `010_news_context_table`, `009_fundamentals_asof_table`, `011_short_context_table`, `012_regime_context_table` and `006_halts_table`.
- Executed `experimental_state_builder_probe_v0_3_20260721T105146Z`: `physical_source_binding = PASS`, `path_validation = PASS`, 10 of 10 active aliases bound and 10 of 10 physical paths found.
- Added `experimental_state_builder_probe_batch3_binding_readout_v0_1.md`; the next recommended gate is `binding_and_schema_check_only`, not data read or State materialization.
- Preserved hard boundaries: no production builder, State consumption, schema metadata discovery, bounded/full data read, physical materialization, dataset promotion or Market State Integration is authorized.
## 2026-07-21 | 03_TABLES_feature_engineering | Experimental physical source binding batch 2 partial pass

- Bound the second experimental physical candidate root batch for `raw_quotes` and `015_microstructure_features_table_candidate`.
- Verified `raw_quotes` against the approved quotes clone lineage: `G:/TSIS/data/quotes_` is used as the local path-probe mirror of official `E:/TSIS/data/quotes_`; `G:/TSIS/data/quotes` is not used for this binding decision.
- Executed `experimental_state_builder_probe_v0_3_20260721T103259Z`: `physical_source_binding = PARTIAL`, `path_validation = PASS`, 5 paths found and 5 unique active aliases remain unbound.
- Preserved hard boundaries: no production builder, State consumption, schema metadata discovery, bounded/full data read, physical materialization, dataset promotion or Market State Integration is authorized.
## 2026-07-21 | 03_TABLES_feature_engineering | Experimental physical source binding batch 1 partial pass

- Bound first experimental physical candidate root batch for `004_master_daily_table`, `013_ohlcv_1m_quote_guarded` and `014_master_intraday_bar_table_candidate`.
- Executed `experimental_state_builder_probe_v0_3_20260721T102009Z`: `physical_source_binding = PARTIAL`, `path_validation = PASS`, 3 paths found and 7 unique active aliases remain unbound.
- Preserved hard boundaries: no production builder, State consumption, schema metadata discovery, bounded/full data read, physical materialization, dataset promotion or Market State Integration is authorized.
## 2026-07-21 | 03_TABLES_feature_engineering | Experimental physical source binding gate opened

- Updated the experimental State Builder probe to `experimental_state_builder_probe_v0_3` with `binding_and_path_check_only` as the active mode.
- Closed `contract_check` as PASS and opened `experimental_physical_source_binding`; 10 unique active source aliases remain pending governed physical candidate roots.
- Kept schema validation, data reads, builder execution and Market State Integration blocked.
- Preserved hard boundaries: no production builder, State consumption, schema metadata discovery, bounded/full data read, physical materialization or dataset promotion is authorized.
## 2026-07-21 | 03_TABLES_feature_engineering | Experimental State Builder source binding registry v0.2

- Added a separated experimental source binding registry for the Phase B non-production State Builder probe.
- Updated the probe status logic so source binding warnings are reflected as `passed_contract_check_pending_source_binding`.
- Executed smoke run `experimental_state_builder_probe_v0_2_20260721T093704Z`: contract gates passed, 10 unique active aliases remain unbound, physical schema/data resolution not executed or authorized.
- Preserved hard boundaries: no production builder, State consumption, bounded/full data read, schema change, physical materialization, dataset promotion or Market State Integration is authorized.
## 2026-07-21 | 03_TABLES_feature_engineering | Experimental State Builder probe scaffolded and smoked

- Added `05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/` with a non-production `contract_check_only` probe, versioned config, run output root and smoke readout.
- Executed smoke run `experimental_state_builder_probe_v0_1_20260721T091253Z`: 12 objects checked, 48 dry-run resolution snapshots, 0 failures, 21 source-binding warnings, 1 expected block and 0 blocked-capability leaks.
- First engineering finding: active source aliases need governed experimental physical bindings before path/schema checks or data-read probes.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration is authorized.
## 2026-07-21 | 03_TABLES_feature_engineering | Builder Validation v1 designs completed

- Completed Builder Validation design coverage for all 12 `TSIS Market Ontology v1` Information Objects.
- Added designs for `Liquidity`, `Market Microstructure State`, `Order Flow Pressure`, `News / Catalyst Context`, `Fundamental Context`, `Short-Side Context`, `Broad Market Context` and `Halt Context`.
- Kept `Order Flow Pressure` blocked pending trade-quote alignment, side classifier and classifier confidence policy.
- Added `experimental_state_builder_boundary_v0_1.md` to define the next step as a non-production experimental builder, not a production builder.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration is authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | Builder Validation first batch added

- Added Builder Validation designs for `Price Movement`, `Price Location / Structure` and `Volatility / Range State`.
- Added a Phase B ratification artifact for the existing `Trading Activity` builder validation pilot and aligned the pilot boundary with the frozen ontology / open Phase B state.
- Updated the Builder Validation inventory and local handoff so the first batch is `design_ready_pending_execution`.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration is authorized by this batch.

## 2026-07-21 | 03_TABLES_feature_engineering | Operational Mapping v1 batch completed

- Completed governed Phase B Operational Mapping coverage for all 12 `TSIS Market Ontology v1` Information Objects.
- Added mappings for `Volatility / Range State`, `Liquidity`, `Market Microstructure State`, `Order Flow Pressure`, `News / Catalyst Context`, `Fundamental Context`, `Short-Side Context`, `Broad Market Context`, `Halt Context`, and a Phase B ratification artifact for `Trading Activity`.
- Updated the Operational Mapping inventory and handoff so the next gate is `Builder Validation`; `Order Flow Pressure` remains State-blocked until trade-quote alignment, side classifier and confidence policy are governed.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization or dataset promotion is authorized by these mappings.
## 2026-07-21 | 03_TABLES_feature_engineering | Price Location Structure Operational Mapping added

- Added `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/price_location_structure_operational_mapping_v0_1.md` as the next governed Phase B Operational Mapping.
- Mapped the core `Price Location / Structure` profile to legal session-open and prior-close anchors while keeping VWAP distance, HOD/LOD proximity, range position, anchored VWAP and pullback/retrace behind later gates.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization or dataset promotion is authorized by this mapping.
## 2026-07-21 | 03_TABLES_feature_engineering | Price Movement Operational Mapping added

- Added `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/price_movement_operational_mapping_v0_1.md` as the first governed Phase B Operational Mapping after the ontology freeze.
- Mapped the core `Price Movement` profile to legal prior-close, session-open and closed-bar return references while keeping speed, acceleration, momentum and reversal/fade behind later gates.
- Preserved hard boundaries: no production builder, State consumption, schema change, physical materialization or dataset promotion is authorized by this mapping.
## 2026-07-21 | 03_TABLES_feature_engineering | TSIS Market Ontology v1 frozen

- Added `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/03_INFORMATION_OBJECTS/TSIS_MARKET_ONTOLOGY_V1_FREEZE.md` as the institutional freeze act for `TSIS Market Ontology v1`.
- Decision: `ontology_status = FROZEN`, `ontology_lock_status = LOCKED`, `phase_a_status = CLOSED`, `phase_b_status = OPEN` for governed engineering.
- Authorized Phase B to start with Operational Mapping while keeping production builders, State consumption, physical variables, schema/materialization and dataset promotion unauthorized until Phase B gates.
- Updated `00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/AGENT.md` so future agents start from the frozen ontology state.
- Aligned the feature-engineering and Phase B boundary READMEs so Operational Mapping is active while Builder Validation and Market State Integration remain gated.
## 2026-07-06 - DAS first push/dip/rebreak semantics v0.2 smoke

## 2026-07-07 - Quotes D-to-E transfer approved

- Approved `E:/TSIS/data/quotes_` as the official E-root quotes dataset for the `D:/quotes` recovery transfer.
- Evidence basis: Phase A structural parity passed for all `5207` tickers; Phase B full SHA256 original shard hash-read exceptions were resolved by targeted retry `quotes_parity_sha256_hash_error_retry_20260707` with `6/6` parity OK and zero mismatches.
- Documents with pre-approval `D:/quotes` lineage now require rebuild against the approved E-root before any official downstream promotion.

- Updated `das_widgets.py` first push logic to follow the human DAS sequence: first green expansion after awakening, first push high before the first red pullback, first dip low inside the first red/non-green pullback sequence, then rebreak of the first push high.
- Updated rebreak validity to require a green candle with high and close above `first_push_high`, plus volume at least equal to the dip-low candle volume.
- Smoke `CYTO 2024-03-25` passed visual manifest validation with 5 labels and generated review image `C:/Users/AlexJ/TSIS_smoke_review/CYTO_2024-03-25_visual_contract_threshold50_v02_semantics.png`.
- Human review is still required before treating v0.2 semantics as accepted.
## 2026-07-06 - Validador visual y manifest label-level para experimento DAS

- Creado `03_TSIS_Lab/06_validators/validate_visual_inspection_manifest.py` para validar evidencia visual label-level en runs de experimento.
- Anotado `06_validators/` en el README del Lab y actualizado `EXP_DAS_FRONTSIDE_DISCOVERY_0001/execution_protocol.md` con el comando de validacion ejecutable.
- Adaptado `00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py` para exportar `visual_inspection_manifest.parquet`, `visual_inspection_manifest.csv`, imagen contractual de inspeccion y sidecar JSON de labels.
- Smoke `XAGE 2025-04-14`: deteccion DAS passed, PNG export passed, `visual_inspection_manifest` generado, 5 labels, 1 visual case, validador visual `PASS`.
## 2026-07-05 - execution_protocol.md para EXP_DAS_FRONTSIDE_DISCOVERY_0001

- Creado `03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/execution_protocol.md`.
- Definida la ejecucion reproducible de `SWEEP_001_frontside_operability_boundary`: inputs, preflight, embudo DAS, metricas, baselines, gates anti-basura, memoria de candidatos, output root y relacion futura con AlphaEvolve.
- Aclarado que el notebook queda como inspeccion humana y que la verdad reproducible debe venir de executor + manifest + evidence report.
## 2026-07-05 - SWEEP_001 reformulado como frontera de operabilidad DAS/frontside

- Renombrado `SWEEP_001_momentum_threshold_sensitivity.yaml` a `SWEEP_001_frontside_operability_boundary.yaml`.
- Aclarado que `+50%` fue una criba humana de operabilidad frontside, no una entrada, evento validado ni threshold optimo.
- Declarado que valores bajo `50%` son grupo de control, `50%` es suelo humano a auditar y valores superiores miden intensidad/sobreextension posible.
## 2026-07-05 - EXP_INTRADAY_MOMENTUM_EXTENSION_0001 archivado

- Movido `03_TSIS_Lab/04_experiments/EXP_INTRADAY_MOMENTUM_EXTENSION_0001/` a `03_TSIS_Lab/04_experiments/_archive/superseded_2026_07_05/EXP_INTRADAY_MOMENTUM_EXTENSION_0001/`.
- Marcado el experimento como `archived_superseded` y `superseded_by: EXP_DAS_FRONTSIDE_DISCOVERY_0001`.
- Actualizadas las referencias activas para que el experimento inicial operativo sea `EXP_DAS_FRONTSIDE_DISCOVERY_0001`.
- `intraday_momentum_extension` queda conservado como concepto/familia futura posible, no como experimento activo.
## 2026-07-05 - EXP_DAS_FRONTSIDE_DISCOVERY_0001 creado en TSIS Lab

- Creado `03_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/` como primer experimento `strategy_seeded_event_discovery` para DAS/frontside.
- Anotados `research_design.md`, `parameter_space.yaml` y `SWEEP_001_frontside_operability_boundary.yaml` con corpus en espanol: origen humano del screener, semillas no validadas, gramatica `scanner seed -> awakening -> first push -> first dip -> rebreak -> DAS sequence -> outcome`, y ruta para descubrir importancia de factores por capas.
- Actualizado el registro de experimentos y el README del Lab. AlphaEvolve queda deshabilitado hasta que existan executor, validators, evidence reports y promotion gates.
## 2026-07-05 - Eliminado ARCHITECTURE_OVERVIEW y alineadas lecturas raiz

- Eliminado `ARCHITECTURE_OVERVIEW.md` porque la autoridad arquitectonica vigente vive en `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`.
- Actualizados `README.md`, `START_HERE.md`, `AGENTS.md`, `PROJECT_RULES.md`, `00_CTO/README.md`, `00_CTO/LOCAL_RULES.md`, `01_TSIS_DATA_FOUNDATION/README.md` y referencias activas relacionadas.
- La lectura raiz queda alineada con TSIS como `Scientific Discovery Engine`, `03_TSIS_Lab` como laboratorio transversal y `research_experiment` como unidad cientifica central.
## 2026-07-05 - Root operating documents aligned with TSIS v3

- Updated `PROJECT_OPERATING_SYSTEM.md` to define TSIS as a Scientific Discovery Engine, add `03_TSIS_Lab`, preserve `01_TSIS_DATA_FOUNDATION` as the operational SmallCaps research/backtest module, and replace the old linear flow with the v3 experiment/evidence/knowledge pipeline.
- Updated `RESEARCH_PHILOSOPHY.md` as the root philosophy synthesis while leaving `00_CTO/01_RESEARCH_PHILOSOPHY/` as the deeper CTO library.
- Updated `VERSIONING_STANDARDS.md` with versioning rules for `research_experiment`, sampling probes, parameter sweeps, evidence reports, knowledge objects, representation candidates, and AlphaEvolve/autonomous generator runs.
## 2026-07-05 - AlphaEvolve aligned with Scientific Discovery Engine

- Updated CTO AlphaEvolve docs so AlphaEvolve is defined as a generator of candidate research experiments under the Scientific Validation Pipeline.
- Added `00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/02_ALPHAEVOLVE_AS_RESEARCH_EXPERIMENT_GENERATOR_v0_1.md`.
- Updated autonomous research system references and `TSIS_LAB_ARCHITECTURE_v3.md` required reads.
## 2026-07-05 - Superseded CTO architecture archive

- Moved `00_CTO/TSIS_LAB_ARCHITECTURE.md`, `00_CTO/TSIS_LAB_ARCHITECTURE_v2.md`, and `00_CTO/00_CTO_REFACTOR_PLAN.md` to `00_CTO/_archive/superseded_architecture_2026_07_05/`.
- Updated active references to use `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md` as the current CTO architecture.
## 2026-07-05 - TSIS Lab Architecture v3

- Created `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md` as the active CTO architecture reading.
- Reframed TSIS as a Scientific Discovery Engine with `research_experiment` as the central unit of work.
- Updated the Market State v3 map so market_state/event_state/outcomes are the observable X/Y base for experiments, not the whole discovery architecture.
## 2026-07-05 - TSIS Scientific Discovery Engine / 03_TSIS_Lab

- Created `03_TSIS_Lab/` as the central operational lab for reproducible TSIS research experiments.
- Added initial lab contracts, registries, templates, and seed experiment `EXP_INTRADAY_MOMENTUM_EXTENSION_0001`.
- Added Research Philosophy documents under `00_CTO/01_RESEARCH_PHILOSOPHY/` to define TSIS as a Scientific Discovery Engine.
- Clarified that AlphaEvolve is a candidate experiment generator, not the authority; scientific validation remains the acceptance layer.
## 2026-07-04 - Mandatory data plane reading for minute work

- Promoted `E:/TSIS/data/README.md` to mandatory base reading for agents.
- Declared `E:/TSIS/data/ohlcv_1m` as the canonical physical root for minute/OHLCV 1m work.
- Reason: prevent future agents from using historical minute roots, treating raw 1m as corrected in place, or bypassing governed repair overlays after the 1m impossible-candle / quote-guarded LT1B incident.
- Queued the semantic change in `00_CTO/GRAPHIFY_REFRESH_QUEUE.md` and `01_TSIS_DATA_FOUNDATION/01_foundations/GRAPHIFY_REFRESH_QUEUE.md` for the next official Graphify refresh.

## 2026-06-29 - Master intraday quote-guarded candidate route

- Documented the `master_intraday_bar_table_v0_2_candidate_quote_guarded`
  route without materializing or promoting a new parquet dataset.
- Preserved `master_intraday_bar_table_v0_1` as a scoped pilot.
- Declared the active bridge lineage:

```text
repair_run_root = C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
minute_root = E:/TSIS/data/ohlcv_1m
quotes_root = D:/quotes
future_official_root = E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded
```

- Blocked final materialization until the official E-root quote-guarded repair
  manifest and final validation report exist.
- Clarified that the candidate table consumes a repair-manifest overlay:
  `raw ohlcv_1m + repair_manifest = quote-guarded view`. It does not require
  or imply a complete corrected OHLCV 1m parquet tree.
- Added a preflight config and pytest contract guard to prevent accidental
  full-universe or v0.1 overwrite claims.

## 2026-06-29 - Controlled market/event state candidate tables

- Added controlled candidate builders for the state-table loop:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_market_state_table.py --materialize-candidate
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_event_state_table.py --materialize-candidate
```

- Materialized candidate outputs under the governed E-root output area:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table/market_state_table_v0_1_candidate_microstructure_halt_controlled/
E:/TSIS/data/data_foundation_outputs/event_state_table/event_state_table_v0_1_candidate_microstructure_halt_controlled/
```

- Results:
  - `market_state_table_v0_1_candidate`: 50 rows, 9 tickers, 50 event windows,
    50 event-context candidate rows, zero ML/RL/full-universe rows.
  - `event_state_table_v0_1_candidate`: 50 rows, 9 tickers, 25 pre-event rows,
    25 post-event-review rows, 50 pattern-discovery rows, zero ML/RL/full-
    universe rows.
- Both candidates inherit provisional `D:/quotes` lineage from the upstream
  microstructure candidate and require rebuild after `E:/TSIS/data/quotes_`
  parity/audit.
- Added executable tests proving candidate materialization, prohibited-prefix
  absence, as-of legality, label/outcome/reward separation and non-promotion:

```text
python -m pytest tests/data_foundation_outputs/test_market_state_table_contract.py tests/data_foundation_outputs/test_event_state_table_contract.py -q
```

## 2026-06-29 - Daily scanner candidates builder and controlled replay

- Added the Module 01 builder for controlled daily scanner replay:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/materialize_daily_scanner_candidates_table.py
```

- Added deterministic builder smoke test:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/tests/data_foundation_outputs/test_daily_scanner_candidates_table_builder.py
```

- Ran the first controlled replay, not an official E-root materialization:

```text
C:/TSIS_Data/tests/test_runs/2026-06-29/daily_scanner_candidates_replay_20250102_20250110_v0_1/
```

- Replay result: 30,646 evaluated rows across 6 sessions, 150 TradeStation-like
  top-25 rows, 3,196 broad-discovery rows, 2,383 broad-discovery rows below
  500k volume, zero duplicate logical keys and ML/RL/live flags all false.
- Documented the scanner replay output-root policy: small samples/tests/demos
  go under `C:/TSIS_Data/tests/test_runs/`, while long-range candidate replays
  go under
  `E:/TSIS/data/data_foundation_outputs/daily_scanner_candidates_table/candidate_replays/`;
  the official promoted root remains reserved.
- Added the research-only notebook explorer:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_research/notebooks/data_foundation_outputs/daily_scanner_candidates_replay_view_v0_1.ipynb
```

## 2026-06-29 - Scanner framework and DAS discovery protection

- Added the Module 01 Data Foundation scanner framework contract:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/scanner_framework_and_definitions_contract_v0_1.md
```

- Added two governed scanner-definition configs for
  `daily_scanner_candidates_table_v0_1`:

```text
configs/data_foundation_outputs/scanner_definitions/trade_station_like_scanner_v0_1.yaml
configs/data_foundation_outputs/scanner_definitions/broad_in_play_discovery_scanner_v0_1.yaml
```

- The scanner layer now distinguishes operational visibility replay from broad
  research discovery, so `volume_today > 500000` and `% change 1D` ranking are
  not treated as the only general scanner for DAS research.
- Future controlled scanner replay must quantify candidates discovered by the
  broad scanner but missed or detected late by the TradeStation-like scanner.

## 2026-06-29 - Daily scanner candidates target stack

- Added the Module 01 Data Foundation target stack for:

```text
daily_scanner_candidates_table_v0_1
```

- The stack defines the governed candidate-generation/in-play discovery layer
  before broad `market_state_table` construction.
- Scanner rows are explicitly candidate-set lineage, not complete market
  states, full-universe truth, labels, rewards, strategy signals, execution
  truth or direct ML/RL rows.
- The new stack includes schema, dataset contract, registry entry, consumption
  policy, validator contract, target contract and Graphify refresh queue entry.
- The `market_state_table` / `event_state_table` contracts now recognize
  scanner candidate lineage through the `scanner__` namespace while keeping it
  separate from full state composition.

## 2026-06-29 - Market-state coverage and lookback policy

- Added the Module 01 Data Foundation policy:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```

- The policy makes explicit that daily in-play/scanner ticker-days are not
  complete market states.
- Future `market_state_table` / `event_state_table` builds must combine
  full-history compact context, daily scanner/event candidates and governed
  event-window microstructure, with explicit lookback policies and lineage.
- Strategies requiring historical memory, such as `Short Into Resistance`, must
  receive as-of lookback features instead of being represented only by the
  current ticker-day.

## 2026-06-29 - State-table provisional D:/quotes lineage accepted

- Accepted `D:/quotes` as provisional candidate-only quote lineage for the next
  controlled `market_state_table` / `event_state_table` loop while
  target official `E:/TSIS/data/quotes_` parity/audit remains incomplete.
- Required any state or microstructure candidate inheriting that source to
  preserve `quotes_root_used`, `quotes_root_state`,
  `target_official_quotes_root`, `legacy_incomplete_e_quotes_root` and
  `requires_rebuild_after_e_quotes_parity`.
- Corrected the target-root semantics: `E:/TSIS/data/quotes_` is the intended
  E-root produced by the active `D:/quotes` clone; `E:/TSIS/data/quotes` is an
  incomplete/legacy E-root for this recovery decision.
- The provisional allowance does not permit institutional promotion, ML/RL
  primary training, backtest-core direct use or execution simulation truth.

## 2026-06-29 - Graphify leaf Git publication policy

- Updated the root Graphify governance policy so `graphify-out/` root payloads
  remain runtime ignored by default while promoted
  `graphify-out/leaf_slices/<leaf_id>/` directories can be versioned in Git.
- Required publishable Graphify leaves to carry `BUILD_MANIFEST.md`, corpus
  manifest or equivalent, `graph.json`, `GRAPH_REPORT.md`, `graph.html` unless
  `--no-viz` is documented, and clean diagnostics or explicit limitations.
- Clarified that deterministic topology/provenance/navigation leaves are
  publishable only when their limited semantic coverage is declared visibly and
  they are not presented as full semantic Graphify extraction.

## 2026-06-29 - Data certification topology Graphify leaf built

- Built the `00_data_certification` topology refresh leaf at:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/graphify-out/leaf_slices/certification_decisions_topology_20260629/
```

- Build result: 88 corpus files, 122 nodes, 653 edges, 11 communities, clean
  `graphify diagnose multigraph` result with 0 missing endpoints, 0 dangling
  endpoints, 0 self-loops and 0 duplicate or collapsed edges.
- The leaf uses `graphifyy 0.9.1` and records modern build provenance, but is a
  deterministic topology refresh; it does not replace the full semantic
  `certification_decisions_20260619` leaf.
- No `00_data_certification` root graph was created or merged.

## 2026-06-29 - Cross-project Graphify governance leaf built

- Upgraded the active Graphify package from `graphifyy 0.8.40` to
  `graphifyy 0.9.1` and reinstalled the Codex Graphify skill before building.
- Built the cross-project Graphify governance leaf at:

```text
C:/TSIS_Data/00_CTO/graphify-out/leaf_slices/graphify_governance_20260629/
```

- The leaf covers root governance, `00_CTO`, `01_foundations`,
  `00_data_certification`, refresh queues, no-API semantic extraction rules,
  build-manifest provenance rules and long-running-operation observability.
- Build result: 37 nodes, 60 edges, 9 communities, clean
  `graphify diagnose multigraph` result with 0 missing endpoints, 0 dangling
  endpoints, 0 self-loops and 0 duplicate or collapsed edges.
- No root graph merge was performed. Larger root refreshes remain pending by
  bounded slice.

## 2026-06-28 - Graphify no-API and version-alignment rule

- Added the root Graphify no-API rule: missing API keys must not block a
  Graphify semantic build in Codex; docs/papers/images must use the Graphify
  skill with host-agent/subagent semantic extraction when no Gemini/Google API
  is configured.
- Clarified that CLI `graphify update` is not enough to prove semantic coverage
  for markdown contracts, papers, images or research documents.
- Required future Graphify build manifests to record installed package version,
  skill/source version, upstream reference, no-API mode and semantic extraction
  coverage before a build can serve as an official baseline.

## 2026-06-28 - Graphify build baseline provenance rule

- Added a root Graphify baseline rule requiring future `BUILD_MANIFEST.md`
  files to record commit, dirty state, exact corpus, queue coverage,
  diagnostics and next-delta commands.
- Required future Graphify rebuilds to preserve enough Git provenance for:

```powershell
git diff --name-status <graph_build_git_commit>...HEAD
git status --short
```

## 2026-06-27 - Long-running operations observability contract

- Added `LONG_RUNNING_OPERATIONS_CONTRACT.md` as a root TSIS contract.
- Root governance now requires pre-manifest, PID manifest, heartbeat, timestamps,
  live logs, compact progress-line monitor command and final manifest/summary
  for long-running operations across all modules.
- The first instrumented Module 01 runners are:
  `scripts/run_1m_split_normalized_materialization.ps1` and
  `scripts/data_ops/clone_quotes_to_staging.ps1`.

`CHANGELOG.md` es:

```text id="cl1"
la memoria histÃƒÆ’Ã‚Â³rica oficial del proyecto
```

Ahora mismo estÃƒÆ’Ã‚Â¡ vacÃƒÆ’Ã‚Â­o (ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œLÃƒÂ¢Ã¢â€šÂ¬Ã‚Â)
y eso es normal al empezar.

---

# Lo MÃƒÆ’Ã‚ÂS importante

NO es:

```text id="cl2"
ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œun log tÃƒÆ’Ã‚Â©cnico giganteÃƒÂ¢Ã¢â€šÂ¬Ã‚Â
```

NO es:

```text id="cl3"
ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œtodos los commits pegadosÃƒÂ¢Ã¢â€šÂ¬Ã‚Â
```

NO es:

```text id="cl4"
ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œhistorial Git duplicadoÃƒÂ¢Ã¢â€šÂ¬Ã‚Â
```

---

# Entonces:

# Ãƒâ€šÃ‚Â¿quÃƒÆ’Ã‚Â© es realmente?

Es:

```text id="cl5"
historia semÃƒÆ’Ã‚Â¡ntica institucional
```

---

# Git ya guarda:

* lÃƒÆ’Ã‚Â­neas cambiadas
* commits
* archivos

---

# CHANGELOG guarda:

```text id="cl6"
quÃƒÆ’Ã‚Â© cambiÃƒÆ’Ã‚Â³ conceptualmente
```

---

# Ejemplo REAL

Git commit:

```text id="cl7"
feat: add universe active status filters
```

Eso estÃƒÆ’Ã‚Â¡ bien para Git.

---

# Pero CHANGELOG debe decir:

```text id="cl8"
v0.3.0
- Universe Builder formalized
- delisted handling introduced
- historical universe reconstruction stabilized
```

---

# Entonces:

# CHANGELOG responde:

```text id="cl9"
cÃƒÆ’Ã‚Â³mo evolucionÃƒÆ’Ã‚Â³ TSIS
```

NO:

```text id="cl10"
quÃƒÆ’Ã‚Â© lÃƒÆ’Ã‚Â­neas cambiaron exactamente
```

---

# QuÃƒÆ’Ã‚Â© pondrÃƒÆ’Ã‚Â­a yo en tu caso

Ahora mismo probablemente:

```md id="cl11"
# TSIS Changelog

Todos los cambios institucionales relevantes del proyecto se registran aquÃƒÆ’Ã‚Â­.

El objetivo NO es duplicar Git commits.

El objetivo es registrar:

- milestones arquitectÃƒÆ’Ã‚Â³nicos;
- cambios semÃƒÆ’Ã‚Â¡nticos importantes;
- promotion states;
- breaking changes;
- releases institucionales;
- evoluciÃƒÆ’Ã‚Â³n conceptual del sistema.
```

---

# Luego:

---

# Primera release

```md id="cl12"
## v0.1.0 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Initial Institutional Foundation

### Added

- monorepo TSIS structure
- governance layer
- AGENTS.md institutional contract
- PROJECT_OPERATING_SYSTEM.md
- VERSIONING_STANDARDS.md
- RESEARCH_PHILOSOPHY.md
- institutional repository architecture

### Notes

This release establishes the foundational governance and research architecture of TSIS.
```

---

# Luego mÃƒÆ’Ã‚Â¡s adelante:

```md id="cl13"
## v0.2.0 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Data Governance Layer

### Added

- RAW data audit layer
- dataset quality policies
- dataset manifests
- schema governance
- historical reconstruction policies

### Changed

- canonical naming authority formalized
```

---

# Luego:

```md id="cl14"
## v0.3.0 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Universe Builder Institutionalization

### Added

- historical universe reconstruction
- active/inactive security tracking
- delisted support
- float filtering policies
- universe manifests

### Fixed

- timestamp normalization inconsistencies

### Breaking Changes

- universe schema updated
```

---

# Lo MÃƒÆ’Ã‚ÂS importante

NO registrar ruido.

---

# NO hacer esto:

```md id="cl15"
- fixed typo
- changed comment
- updated import
- changed variable name
```

Eso NO pertenece aquÃƒÆ’Ã‚Â­.

Eso pertenece a Git.

---

# CHANGELOG debe registrar:

```text id="cl16"
cambios con importancia institucional
```

---

# QuÃƒÆ’Ã‚Â© tipos de cosas sÃƒÆ’Ã‚Â­ van aquÃƒÆ’Ã‚Â­

---

# SÃƒÆ’Ã‚Â­:

* nueva arquitectura
* nuevo pipeline
* nuevo schema
* nueva capa
* breaking changes
* promotion institutional
* nuevas policies
* cambios epistemolÃƒÆ’Ã‚Â³gicos
* nuevo simulador
* nueva ontologÃƒÆ’Ã‚Â­a
* nueva metodologÃƒÆ’Ã‚Â­a

---

# NO:

* pequeÃƒÆ’Ã‚Â±os fixes
* imports
* cleanup trivial
* prints
* typo fixes
* experiments temporales

---

# Lo MÃƒÆ’Ã‚ÂS importante

Tu proyecto tiene:

* governance
* philosophy
* architecture
* reproducibility

Entonces tu changelog debe parecer:

```text id="cl17"
historia evolutiva del sistema
```

---

# NO:

```text id="cl18"
diario tÃƒÆ’Ã‚Â©cnico caÃƒÆ’Ã‚Â³tico
```

---

# CÃƒÆ’Ã‚Â³mo lo usarÃƒÆ’Ã‚Â¡n agentes

MUY importante.

Los agentes leerÃƒÆ’Ã‚Â¡n CHANGELOG para entender:

* quÃƒÆ’Ã‚Â© evolucionÃƒÆ’Ã‚Â³
* quÃƒÆ’Ã‚Â© cambiÃƒÆ’Ã‚Â³ conceptualmente
* quÃƒÆ’Ã‚Â© es estable
* quÃƒÆ’Ã‚Â© se rompiÃƒÆ’Ã‚Â³
* quÃƒÆ’Ã‚Â© fue promocionado
* quÃƒÆ’Ã‚Â© schemas cambiaron
* quÃƒÆ’Ã‚Â© releases existen

---

# Mi recomendaciÃƒÆ’Ã‚Â³n REAL

Tu CHANGELOG deberÃƒÆ’Ã‚Â­a ser:

* corto
* semÃƒÆ’Ã‚Â¡ntico
* institucional
* estable
* limpio
* milestone-oriented

---

# Sinceramente:

# probablemente deberÃƒÆ’Ã‚Â­as pensar en ÃƒÆ’Ã‚Â©l como:

```text id="cl19"
historia constitucional de TSIS
```

NO como log tÃƒÆ’Ã‚Â©cnico.

---

## v0.2.1 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Project-wide scientific justification standard

### Changed

- Promoted the scientific-justification requirement to root governance in
  `PROJECT_RULES.md`.
- Added the matching research-method principle to `RESEARCH_PHILOSOPHY.md`.

### Impact

- Any institutional decision across TSIS must now connect:

```text
Decision TSIS -> Evidencia directa -> Obligacion tecnica -> Limitacion abierta
```

- The requirement applies equally to data, contracts, audits, schemas, events,
  market states, features, ML/RL, simulators, execution, evaluators, fitness
  functions, promotion policies and downstream outputs.
- Components without sufficient direct evidence must remain explicitly marked
  as `engineering convention`, `working hypothesis`, `candidate_policy`,
  `provisional` or `exploratory`.

---

## v0.2.0 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Module 01 official Graphify leaf publication

### Added

- Published the first official Graphify leaf for `01_foundations`:
  `01_TSIS_DATA_FOUNDATION/01_foundations/graphify-out/leaf_slices/foundations_authority_20260619/`.
- Published the first official Graphify leaf for RAW data certification
  decisions:
  `01_TSIS_DATA_FOUNDATION/01_research/01_auditoria_RAW_DATA/00_data_certification/graphify-out/leaf_slices/certification_decisions_20260619/`.
- Versioned Graphify governance files for `01_foundations` and
  `00_data_certification`, including build protocols, refresh queues and
  module-local graphify contracts.

### Changed

- `origin/main` now contains the official Graphify leaf artifacts for both
  initial Module 01 graphs.
- `.gitignore` now explicitly opens the governed
  `00_data_certification` Graphify leaf path while keeping heavy runtime and
  evidence artifacts protected by default.

### Notes

The two published leaves are semantic navigation artifacts for agents and
humans. They do not replace manifests, dataset contracts, validators, physical
profiling or certification evidence.

Root Graphify graphs were intentionally not created for these scopes. The
official state is leaf-first:

```text
01_foundations -> foundations_authority_graph
00_data_certification -> certification_decisions_graph
```

### Impact

- Future agents can query the official leaf graph outputs directly from
  `main`.
- Future data-foundation table design must still combine:

```text
contract + certification + evidence + physical profiling + validator
```

- Notebook evidence remains important but is deferred to a separate future
  Graphify leaf instead of being mixed into the first certification decisions
  graph.
