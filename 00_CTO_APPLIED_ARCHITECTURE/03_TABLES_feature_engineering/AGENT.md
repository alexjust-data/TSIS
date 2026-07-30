# Active-State Rule

```text
canonical cold-start entry = STATE_PROVIDER_CONSUMER_RECOVERY.md
current handoff = the first handoff block below only
all later handoff blocks = historical closure snapshots
```

Read `LOCAL_RULES.md` and `STATE_PROVIDER_CONSUMER_RECOVERY.md` before using
this file. Repeated historical headings do not create concurrent current gates.

# Current Runtime Handoff Override - Restriction Domains Clarified

Status: `agent_handoff_prompt_v0_155`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-30`

```text
last_closed_gate = market_state_restriction_domain_binding_clarification_v0_1
last_closed_status = CLOSED_PASS_RESTRICTION_DOMAINS_DISAMBIGUATED_FOR_BT_GATE_014_NO_PHYSICAL_READ_NO_CONSUMER_AUTHORIZATION
physical_provenance_restriction_codes = physical fingerprinted lineage domain
replay_consumption_restriction_codes = bounded delivery policy domain
component_replay_restriction_codes = component replay-legality domain
BT_GATE_014_V0_4 = CONSUMED_FAILED_FINAL
BT_GATE_014_V0_4_reuse = PROHIBITED
BT_GATE_014_V0_5 = NOT_AUTHORIZED
next_owner = BT-GATE-014
active_provider_gate = none
parquet_opened_by_gate = false
physical_rows_read_by_gate = 0
backtester_files_modified = 0
Event_State = NOT_OPEN
general_StateReplayFeed = NOT_AUTHORIZED
```

The backtester must adopt the labeled restriction domains in its contract,
event, lineage, store and regression suite. Do not issue or execute V0.5 from
this handoff. A new single-use authorization requires independent
pre-execution review.

# Current Runtime Handoff Override - BT-GATE-014 Contract Handoff Ready

Status: `agent_handoff_prompt_v0_154`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-30`

```text
last_closed_gate = market_state_core_four_scale_validation_physical_schema_binding_clarification_v0_1
last_closed_status = CLOSED_PASS_SCHEMA_PROVENANCE_AND_RUNTIME_CONTENT_AUTHORITY_DISAMBIGUATED_FOR_BT_GATE_014_NO_PHYSICAL_READ
next_owner = BT-GATE-014
BT_GATE_014_provider_evidence_handoff = COMPLETE
backtester_current_gate_authority = 02_TSIS_BACKTEST_ENGINE/AGENTS.md
provider_authorization_reuse = PROHIBITED
active_provider_gate = none
general_StateReplayFeed = NOT_AUTHORIZED
Event_State = NOT_OPEN
official_dataset = false
production = false
downstream = false
```

The provider handoff is complete. Read `02_TSIS_BACKTEST_ENGINE/AGENTS.md` for
the mutable consumer gate state. Do not modify the backtester from this handoff.

# Current Runtime Handoff Override - Bounded Market State Read/Replay Review Closed

Status: `agent_handoff_prompt_v0_153`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-30`

```text
last_executed_gate = bounded_state_bundle_read_and_replay_execution_v0_1
last_execution_status = CLOSED_PASS_ONE_BOUNDED_MARKET_STATE_PHYSICAL_READ_AND_REPLAY_PROBE_WITH_RESTRICTIONS
last_closed_gate = bounded_state_bundle_read_and_replay_review_v0_1
last_closed_status = CLOSED_PASS_BOUNDED_MARKET_STATE_PHYSICAL_READ_AND_REPLAY_REVIEW_WITH_RESTRICTIONS_READY_FOR_BT_GATE_014_HANDOFF
authorization_single_use_consumed = true
physical_state_rows_read = 2
bounded_probe_records_emitted = 2
next_handoff = BT-GATE-014_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_EVIDENCE_READY
general_StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
event_state = NOT_AUTHORIZED
official_dataset = false
production = false
downstream = false
```

Do not modify `02_TSIS_BACKTEST_ENGINE` from this handoff. Provide the execution
and review evidence to the BT-GATE-014 owner. The consumed authorization cannot
be reused and no additional physical provider read is authorized.

# Current Runtime Handoff Override - Bounded Read and Replay Authorization v0.2 Closed

Status: `agent_handoff_prompt_v0_152`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-30`

```text
last_closed_gate = bounded_state_bundle_read_and_replay_authorization_v0_2
last_closed_status = CLOSED_AUTHORIZED_ONE_BOUNDED_MARKET_STATE_READ_AND_REPLAY_PROBE_WITH_RESTRICTIONS_NO_EXECUTION
authorization_to_read_issued = true
bounded_execution_authorized = true
current_gate = bounded_state_bundle_read_and_replay_execution_v0_1_pending
authorized_slice = ACIU / 2021-03-15 / 2 exact row identities
parquet_opened = false
physical_state_rows_read = 0
bounded_probe_records_emitted = 0
general_StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
official_dataset = false
production = false
downstream = false
```

Do not modify `02_TSIS_BACKTEST_ENGINE` from this handoff. The next permitted
work is one bounded execution against the exact frozen paths, hashes and row
identities. No scope expansion, strategy, signals, orders, fills or PnL is
authorized.

# Current Runtime Handoff Override - Physical Evidence Alignment v0.2 Closed

Status: `agent_handoff_prompt_v0_151`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-30`

```text
last_closed_gate = state_bundle_manifest_physical_evidence_alignment_v0_2
last_closed_status = CLOSED_PASS_PHYSICAL_EVIDENCE_ALIGNED_READY_FOR_BOUNDED_READ_AUTHORIZATION_WITH_RESTRICTIONS_NO_PHYSICAL_READ
physical_read_authorization_ready = true
authorization_to_read_issued = false
current_gate = bounded_state_bundle_read_and_replay_authorization_v0_1_pending
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
physical_state_rows_read = 0
parquet_opened = false
official_dataset = false
production = false
downstream = false
```

Do not modify `02_TSIS_BACKTEST_ENGINE` from this handoff. The next permitted shared-boundary work is the bounded read-and-replay authorization. Alignment readiness does not itself authorize opening parquet, delivering rows or emitting StateReplayFeed records.

# Current Runtime Handoff Override - Scale Validation Sidecar and Reissue Ready

Status: `agent_handoff_prompt_v0_150`
Layer: `03_TABLES_feature_engineering`
Boundary layers: `08_RUNTIME_CAPABILITIES`, `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-29`

```text
last_closed_sidecar_gate = market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1
last_closed_sidecar_status = CLOSED_PASS_SCALE_VALIDATION_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_CREATED_AND_VALIDATED_WITH_RESTRICTIONS_NO_PHYSICAL_READ
last_closed_runtime_regression = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
last_closed_runtime_regression_status = CLOSED_PASS_V0_1_2_CONTROL_PLANE_REISSUE_WITH_CANONICAL_BUNDLE_AND_EXACT_REUSE_EVIDENCE_NO_CONSUMPTION
current_gate = state_bundle_manifest_physical_evidence_alignment_v0_2_pending
scale_validation_sidecar_records = 104
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

Do not touch `02_TSIS_BACKTEST_ENGINE`. The next work is physical evidence alignment against the new v0.1.2 response/bundle and the scale-validation replay sidecar.

# Current Runtime Handoff Override - Bounded Interface Regression v0.1.2 Closed

Status: `agent_handoff_prompt_v0_149`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `08_RUNTIME_CAPABILITIES`
Date: `2026-07-29`

```text
last_closed_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
last_closed_status = CLOSED_PASS_V0_1_2_BOUNDED_INTERFACE_EXECUTION_REGRESSION_WITH_RESTRICTIONS_NO_CONSUMPTION
current_gate = state_bundle_manifest_physical_evidence_alignment_v0_1_pending
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
runtime_requests_executed = 0
runtime_builds_executed = 0
state_rows_read = 0
```

Do not touch `02_TSIS_BACKTEST_ENGINE`. The next gate is physical evidence alignment; do not open physical reads unless that gate passes.

# Historical Runtime Handoff Override - Replay Availability Sidecar Created

Status: `agent_handoff_prompt_v0_148`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-29`

```text
last_closed_gate = market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1
last_closed_status = CLOSED_PASS_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_CREATED_AND_VALIDATED_WITH_RESTRICTIONS_NO_PHYSICAL_READ
current_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_pending
sidecar_records_written = 8
parquet_opened = false
state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

Do not touch `02_TSIS_BACKTEST_ENGINE`. The next gate is the runtime bounded interface regression v0.1.2, now with sidecar evidence available.

# Historical Runtime Handoff Override - Replay Availability Sidecar Authorization Closed

Status: `agent_handoff_prompt_v0_147`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-29`

```text
last_closed_gate = market_state_core_four_replay_availability_evidence_sidecar_authorization_v0_1
last_closed_status = CLOSED_AUTHORIZED_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_EXECUTION_AND_VALIDATION_WITH_RESTRICTIONS_NO_PHYSICAL_READ
current_gate = market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1_pending
sidecar_records_written = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

Do not touch `02_TSIS_BACKTEST_ENGINE`. The next gate must create and validate the sidecar/envelope before any physical evidence alignment retry.

# Historical Runtime Handoff Override - Bounded Interface Regression v0.1.2 Blocked

Status: `agent_handoff_prompt_v0_146`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `08_RUNTIME_CAPABILITIES`
Date: `2026-07-29`

```text
last_closed_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
last_closed_status = CLOSED_BLOCKED_REQUIRES_ROW_ADDRESSABLE_REPLAY_AVAILABILITY_EVIDENCE_NO_PHYSICAL_READ
current_gate = market_state_core_four_replay_availability_evidence_sidecar_authorization_v0_1_pending
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
runtime_requests_executed = 0
runtime_builds_executed = 0
state_rows_read = 0
```

Do not touch `02_TSIS_BACKTEST_ENGINE`. The next provider/shared-boundary work is to authorize a row-addressable replay availability sidecar or envelope for the already validated Market State core-four physical candidate. Do not infer `state_available_at_utc` from `decision_timestamp_utc` or parquet creation time.

# Historical Runtime Handoff Override - Replay Availability Timestamp Contract Validation Hardened

Status: `agent_handoff_prompt_v0_145`
Layer: `03_TABLES_feature_engineering`
Boundary layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-29`

```text
last_closed_gate = market_state_core_four_replay_availability_timestamp_contract_v0_1
last_closed_status = CLOSED_CONTRACT_READY_WITH_VALIDATION_HARDENED_RESTRICTIONS_NO_PHYSICAL_READ
current_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_pending
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

The timestamp contract validator is hardened after external review: every fixture is schema-validated and semantically validated; core-four object coverage, component/row legality, latency inclusion, timestamp ordering and restriction propagation are fail-closed. Do not open physical reads or StateReplayFeed from this gate.

## Historical Runtime Handoff Override - Replay Availability Timestamp Contract Closed

Status: `agent_handoff_prompt_v0_144`
Date: `2026-07-29`

```text
current_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_pending
boundary_layer = 08_RUNTIME_CAPABILITIES
last_closed_gate = market_state_core_four_replay_availability_timestamp_contract_v0_1
last_closed_status = CLOSED_CONTRACT_READY_WITH_VALIDATION_HARDENED_RESTRICTIONS_NO_PHYSICAL_READ
previous_blocker_addressed = ALIGN_REPLAY_TIMESTAMPS_SCHEMA_001
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
state_rows_read = 0
physical_artifacts_opened = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Do not open physical reads. The next work is a provider/runtime control-plane regression that must reissue a v0.1.2 response and StateBundleManifest with the timestamp evidence required by the replay availability contract. Do not modify `02_TSIS_BACKTEST_ENGINE` from this handoff.

## Historical Runtime Handoff Override - StateBundle Physical Evidence Alignment Blocked

Status: `agent_handoff_prompt_v0_143`
Date: `2026-07-29`

```text
current_gate = market_state_core_four_replay_availability_timestamp_contract_v0_1_pending
also_required_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
boundary_layer = 09_STATE_CONSUMPTION_BOUNDARY
last_closed_gate = state_bundle_manifest_physical_evidence_alignment_v0_1
last_closed_status = CLOSED_BLOCKED_REQUIRES_V0_1_2_BUNDLE_REISSUE_AND_REPLAY_TIMESTAMP_EVIDENCE_NO_PHYSICAL_READ
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
state_rows_read = 0
physical_artifacts_opened = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Do not open physical reads. The next work must prove replay-safe timestamps and reissue the control-plane response/bundle under provider v0.1.2 before bounded read authorization can reopen.

## Historical Runtime Handoff Override - Provider-Consumer Compatibility Regression v0.1.2 Closed

Status: `agent_handoff_prompt_v0_142`
Date: `2026-07-29`

```text
current_gate = state_bundle_manifest_physical_evidence_alignment_v0_1
boundary_layer = 09_STATE_CONSUMPTION_BOUNDARY
last_closed_gate = runtime_provider_consumer_contract_compatibility_regression_v0_1_2
last_closed_status = CLOSED_PASS_PROVIDER_CONSUMER_CONTROL_PLANE_COMPATIBLE_WITH_RESTRICTIONS_NO_CONSUMPTION
active_provider_authority = runtime_provider_contract_schema_hardening_v0_1_2
provider_control_plane = REFROZEN_AT_V0_1_2_WITH_RESTRICTIONS
provider_consumer_control_plane_compatibility = PASS_WITH_RESTRICTIONS
consumer_contract_status = DRAFT_NOT_INTEGRATION_VALIDATED
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
physical_rows_delivered = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Do not modify `02_TSIS_BACKTEST_ENGINE` from this provider handoff. The next permitted shared-boundary work is state_bundle_manifest_physical_evidence_alignment_v0_1; it still must not open StateReplayFeed or backtest rows.

# 03_TABLES_feature_engineering - Agent Handoff Prompt

## Historical Runtime Handoff Override - Provider Hardening v0.1.2 External Audit Accepted

Status: `agent_handoff_prompt_v0_141`
Date: `2026-07-29`

```text
current_gate = runtime_provider_consumer_contract_compatibility_regression_v0_1_2
boundary_layer = 08_RUNTIME_CAPABILITIES
last_closed_gate = runtime_provider_contract_schema_hardening_v0_1_2
last_closed_status = CLOSED_EXTERNAL_AUDIT_PASS_ACCEPTABLE_AS_PROVIDER_AUTHORITY_WITH_RESTRICTIONS
active_provider_authority = runtime_provider_contract_schema_hardening_v0_1_2
ACTIVE_PROVIDER_AUTHORITY = runtime_provider_contract_schema_hardening_v0_1_2
provider_control_plane = REFROZEN_AT_V0_1_2_WITH_RESTRICTIONS
provider_v0_1_2_external_audit = PASS
provider_v0_1_2_external_audit_genealogy = RECORDED_THROUGH_105019Z
provider_consumer_compatibility = READY_FOR_REGRESSION_NOT_OPENED
case_count = 133
failed_cases = 0
missing_required_case_ids = 0
unexpected_case_ids = 0
provider_only_zip = C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T141808Z.zip
provider_only_zip_sha256 = 191f40e40f2cfe374ce2f493fb9dd3e2509e33f64b9ed8f3969c9c8b0badf759
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
physical_rows_delivered = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Do not open StateBundle physical reads, StateReplayFeed, backtest state integration, production or downstream. The only next authorized work is the small provider-consumer contract compatibility regression against v0.1.2.

## Historical Runtime Handoff Override - Provider Contract Schema Hardening v0.1.2 Quarantined

Status: `agent_handoff_prompt_v0_131_quarantined`
Date: `2026-07-28`

```text
quarantined_gate = runtime_provider_contract_schema_hardening_v0_1_2
quarantine_status = QUARANTINED_NO_ACTIVE_AUTHORITY
reason = boundary_violation_by_backtester_scoped_agent
active_provider_authority = state_provider_control_plane_ready_with_restrictions_reference_only
provider_consumer_compatibility = NOT_OPENED_AFTER_V0_1_2
consumer_contract_status = DRAFT
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
quarantine_ref = 99_archive/v0_1_2_boundary_quarantine_20260728/QUARANTINE_MANIFEST.json
```

Historical note: do not treat this quarantined block as the current handoff. The current handoff is the provider hardening reauthorization block above.

## Historical Agent Handoff Prompt

## Historical Runtime Handoff Override - Data-Plane Joint Review Closed - HISTORICAL_SNAPSHOT

Status: `agent_handoff_prompt_v0_133`
Date: `2026-07-28`

```text
last_closed_gate = provider_consumer_data_plane_joint_review_v0_1
last_closed_status = CLOSED_APPROVED_FOR_BOUNDED_STATE_BUNDLE_READ_AND_REPLAY_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION
current_gate = bounded_state_bundle_read_and_replay_authorization_v0_1_pending
boundary_layer = 09_STATE_CONSUMPTION_BOUNDARY
provider_control_plane = READY_WITH_RESTRICTIONS
physical_consumption_authorization_contract = design_ready
state_bundle_reader_contract = design_ready
state_replay_feed_contract = design_ready
blocking_findings = 0
state_bundle_rows_read = 0
state_replay_feed_records_emitted = 0
event_loop_ticks = 0
strategy_callbacks = 0
orders = 0
fills = 0
pnl = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Continue with `bounded_state_bundle_read_and_replay_authorization_v0_1` only if authorizing one bounded probe. Do not execute it in the authorization gate. Do not add Liquidity, Event Types, strategy execution, orders, fills, PnL, production or downstream.
## Historical Agent Handoff Prompt

## Historical Runtime Handoff Override - Reader and Replay Contracts Designed - HISTORICAL_SNAPSHOT

Status: `agent_handoff_prompt_v0_132`
Date: `2026-07-28`

```text
last_closed_gate = state_bundle_reader_and_replay_contract_design_v0_1
last_closed_status = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
current_gate = provider_consumer_data_plane_joint_review_v0_1_pending
boundary_layer = 09_STATE_CONSUMPTION_BOUNDARY
state_provider_control_plane = READY_WITH_RESTRICTIONS
state_bundle_physical_consumption_authorization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_PHYSICAL_READ
state_bundle_reader_contract = design_ready_no_execution
state_replay_feed_contract = design_ready_no_execution
clock_authority = EventLoop
state_delivery_rule = event_loop_clock_gte_state_available_at_utc
state_bundle_rows_read = 0
state_replay_feed_records_emitted = 0
event_loop_ticks = 0
strategy_callbacks = 0
orders = 0
fills = 0
pnl = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Continue with `provider_consumer_data_plane_joint_review_v0_1` as a review-only gate. Do not execute physical reads, start EventLoop/StateReplayFeed, start backtests, emit orders/fills, calculate PnL, add Liquidity, add Event Types, promote datasets, production or downstream from this gate.
## Historical Agent Handoff Prompt

## Historical Runtime Handoff Override - StateBundle Physical Consumption Boundary Opened - HISTORICAL_SNAPSHOT

Status: `agent_handoff_prompt_v0_131`
Date: `2026-07-28`

```text
last_closed_gate = state_bundle_physical_consumption_authorization_design_v0_1
last_closed_status = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_PHYSICAL_READ
current_gate = state_bundle_reader_contract_design_v0_1_pending_consumer_data_plane
state_provider_control_plane = READY_WITH_RESTRICTIONS
provider_owned_next_gate = none_active
boundary_layer = 09_STATE_CONSUMPTION_BOUNDARY
first_vertical_slice_state_kind = market_state
first_vertical_slice_profile = market_state_core_four_intraday_profile_v0_1
event_state_requested_in_first_slice = false
state_bundle_rows_read = 0
physical_artifacts_opened = 0
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
strategy_execution = false
orders = 0
fills = 0
pnl = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Continue with the StateBundle reader contract as a bounded consumer/data-plane design. Do not implement `StateReplayFeed`, start backtests, emit orders/fills, calculate PnL, add Liquidity, add Event Types, promote datasets, production or downstream from this gate.
## Historical Agent Handoff Prompt

## Historical Runtime Handoff Override - State Provider Control-Plane v0.1 Frozen

Status: `agent_handoff_prompt_v0_130`
Date: `2026-07-28`

```text
current_gate = state_provider_control_plane_ready_with_restrictions_no_active_provider_gate
last_closed_gate = runtime_user_invocation_bounded_interface_execution_review_v0_1
last_closed_status = CLOSED_PASS_STATE_PROVIDER_CONTROL_PLANE_READY_WITH_RESTRICTIONS_NO_CONSUMPTION
last_prerequisite_gate = runtime_provider_contract_schema_hardening_v0_1_1
last_prerequisite_status = CLOSED_PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_1_WITH_RESTRICTIONS_NO_EXECUTION
state_provider_control_plane = READY_WITH_RESTRICTIONS
provider_owned_next_gate = none_active
next_boundary = state_bundle_physical_consumption_authorization_design_v0_1
next_boundary_owner = consumer_data_plane_or_shared_boundary
runtime_builds_executed = 0
source_market_data_rows_read = 0
registry_mutations = 0
physical_row_delivery = false
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Do not reopen provider architecture unless a material contract defect is found. Do not implement `StateReplayFeed`, physical StateBundle reads, backtest state consumption, production or downstream from this layer.

## Historical Agent Handoff Prompt

## Historical Runtime Handoff Override - Bounded Interface Execution Completed Pending Review

Status: `agent_handoff_prompt_v0_127`
Date: `2026-07-28`

```text
current_gate = runtime_user_invocation_bounded_interface_execution_review_v0_1
last_closed_gate = runtime_user_invocation_bounded_interface_execution_v0_1
last_closed_run_id = runtime_user_invocation_bounded_interface_execution_v0_1_20260728T1731090000
last_closed_status = CLOSED_PASS_BOUNDED_INTERFACE_EXECUTION_WITH_RESTRICTIONS_PENDING_REVIEW
case_count = 8
hard_failures = 0
runtime_builds_executed = 0
physical_state_rows_delivered = 0
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
backtest_state_consumption_authority = false
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Next gate:

```text
runtime_user_invocation_bounded_interface_execution_review_v0_1
```

The next gate must review the bounded provider interface execution evidence. It must not open StateReplayFeed, physical state row delivery, production or downstream consumption.

## Historical Agent Handoff Prompt

## Historical Runtime Handoff Override - Bounded Interface Execution Authorized

Status: `agent_handoff_prompt_v0_126`
Date: `2026-07-28`

```text
current_gate = runtime_user_invocation_bounded_interface_execution_v0_1
last_closed_gate = runtime_user_invocation_bounded_interface_execution_authorization_v0_1
last_closed_run_id = none_authorization_gate
last_closed_status = CLOSED_AUTHORIZED_BOUNDED_INTERFACE_EXECUTION_WITH_RESTRICTIONS_NO_EXECUTION
provider_control_plane = READY_FOR_BOUNDED_BEHAVIOR_TEST
provider_consumer_compatibility = PASS_WITH_RESTRICTIONS
consumer_contract_status = PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
authorized_test_cases = 8
runtime_builds_authorized = false
physical_row_delivery = false
backtest_state_consumption_authority = false
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
official_dataset = false
production = false
downstream_state_consumption = NOT_AUTHORIZED
```

Next gate:

```text
runtime_user_invocation_bounded_interface_execution_v0_1
```

The next gate may execute bounded provider interface behavior tests only. It
must not build datasets, start a backtest, open StateReplayFeed, deliver state
rows, promote official datasets or authorize downstream consumption.

## Historical Agent Handoff Prompt

## Historical Runtime Handoff Override - Provider Consumer Compatibility Closed

Status: `agent_handoff_prompt_v0_125`
Date: `2026-07-28`

```text
current_gate = runtime_user_invocation_bounded_interface_execution_authorization_v0_1
last_closed_gate = runtime_provider_consumer_contract_compatibility_review_v0_1
last_closed_run_id = none_review_gate
last_closed_status = CLOSED_APPROVED_FOR_BOUNDED_INTERFACE_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION
provider_boundary = CLOSED_BOUNDARY_CLARIFIED_NO_EXECUTION
provider_interface_documentation = CLOSED
provider_schema_strict_validation = PASS
fail_closed_semantics = PASS_WITH_CODE_VALIDATION_REQUIRED
provider_consumer_compatibility = PASS_WITH_RESTRICTIONS
consumer_contract_status = PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
backtest_state_consumption_authority = false
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
downstream_state_consumption = NOT_AUTHORIZED
official_dataset = false
production = false
physical_row_delivery = false
compatibility_matrix = runtime_provider_consumer_contract_compatibility_review_matrix_v0_1.json
```

Next gate:

```text
runtime_user_invocation_bounded_interface_execution_authorization_v0_1
```

The next gate may authorize bounded runtime interface behavior tests. It must
not open StateReplayFeed, backtest state consumption, production, downstream
consumption or physical row delivery.

## Historical Runtime Handoff Override - Provider Schema Hardened

Status: `agent_handoff_prompt_v0_124`
Date: `2026-07-28`

```text
current_gate = runtime_provider_consumer_contract_compatibility_review_v0_1
last_closed_gate = runtime_provider_contract_schema_hardening_v0_1
last_closed_run_id = none_design_gate
last_closed_status = CLOSED_SCHEMA_HARDENED_WITH_RESTRICTIONS_NO_EXECUTION
provider_boundary = CLOSED_BOUNDARY_CLARIFIED_NO_EXECUTION
provider_interface_documentation = CLOSED
provider_schema_strict_validation = HARDENED_PENDING_COMPATIBILITY_REVIEW
fail_closed_semantics = HARDENED_PENDING_COMPATIBILITY_REVIEW
provider_consumer_compatibility = READY_FOR_REVIEW_NOT_VALIDATED
backtest_state_consumption_authority = false
state_replay_feed_authority = false
StateReplayFeed = NOT_AUTHORIZED
downstream_state_consumption = NOT_AUTHORIZED
official_dataset = false
production = false
physical_row_delivery = false
hardened_provider_contracts = state_resolution_request_contract_v0_1.json, runtime_user_invocation_response_contract_v0_1.json, state_bundle_manifest_contract_v0_1.json
required_specialized_payload_contracts = market_state_request_contract_v0_1.json, event_state_request_contract_v0_1.json
validation_matrix = runtime_provider_contract_schema_hardening_validation_matrix_v0_1.json
```

Next gate:

```text
runtime_provider_consumer_contract_compatibility_review_v0_1
```

The next gate must rerun compatibility against the hardened provider schemas and the backtest consumer draft contracts. It must not execute requests, run a backtest, promote official datasets, open StateReplayFeed consumption, open production or authorize downstream consumption.


## Historical Runtime Handoff Override - Provider Interface Closed Before Schema Hardening

Status: `agent_handoff_prompt_v0_123`
Date: `2026-07-28`

```text
current_gate = runtime_provider_consumer_contract_compatibility_review_v0_1
last_closed_gate = runtime_user_invocation_interface_v0_1
last_closed_run_id = none_design_gate
last_closed_status = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
provider_boundary = CLOSED_BOUNDARY_CLARIFIED_NO_EXECUTION
provider_interface_contracts = CLOSED
provider_consumer_compatibility = READY_FOR_REVIEW_NOT_VALIDATED
state_resolution_request_role = common_provider_envelope
market_state_request_role = specialized_payload
event_state_request_role = specialized_payload
backtest_state_consumption_authority = false
downstream_state_consumption = NOT_AUTHORIZED
official_dataset = false
production = false
physical_row_delivery = false
provider_contracts_closed = state_resolution_request_contract_v0_1.json, runtime_user_invocation_interface_contract_v0_1.json, runtime_user_invocation_response_contract_v0_1.json, runtime_capability_effective_view_contract_v0_1.json, state_bundle_manifest_contract_v0_1.json
```

Next gate:

```text
runtime_provider_consumer_contract_compatibility_review_v0_1
```

The next gate must compare provider-side runtime contracts with the backtest consumer draft contracts. It must not execute requests, run a backtest, promote official datasets, open StateReplayFeed consumption, open production or authorize downstream consumption.



Status: `agent_handoff_prompt_v0_116`

Date: `2026-07-28`


## Historical Runtime Handoff Override - Superseded

This block is historical context and is superseded by the Provider Interface Closed override above.

Status: `agent_handoff_prompt_v0_122`
Date: `2026-07-28`

```text
current_gate = runtime_user_invocation_interface_v0_1
last_closed_gate = event_state_capability_consumption_policy_v0_1
last_closed_run_id = event_state_capability_consumption_policy_v0_1_20260728T135626Z
last_closed_status = CLOSED_PASS_EVENT_STATE_CAPABILITY_CONSUMPTION_POLICY_ESTABLISHED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION
capability_id = event_state_on_demand_runtime_capability_v0_1
policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
allowed_event_type_ids = [event_type:market_data:session_opened]
accepted_subject_scope = exchange_session
hard_policy_failures = 0
source_market_data_rows_read = 0
new_event_state_materializer_executions = 0
new_market_state_materializer_executions = 0
new_candidate_dataset_registry_entries_written = 0
registry_entry_mutations = 0
official_event_state_dataset = false
production = false
downstream = false
provider_boundary = CLOSED_BOUNDARY_CLARIFIED_NO_EXECUTION
provider_boundary_authority = runtime_state_provider_boundary_v0_1.md
provider_boundary_normalization = CLOSED_PASS_BOUNDARY_STATUS_AND_REQUEST_HIERARCHY_NORMALIZED_NO_EXECUTION
provider_boundary_normalization_authority = runtime_state_provider_boundary_normalization_readout_v0_1.md
state_resolution_request_role = common_provider_envelope
market_state_request_role = specialized_payload
event_state_request_role = specialized_payload
provider_interface_contracts = PENDING
provider_consumer_compatibility = NOT_YET_VALIDATED
```

Next gate:

```text
runtime_user_invocation_interface_v0_1
```

The next gate must design the provider-side invocation layer for governed Market State and Event State requests. In v0.1, user means institutional consumer module; the first expected consumer is Backtest RunPreflight. The gate must not execute requests, promote official datasets, open production or authorize downstream consumption.
Este documento es el prompt local de continuidad para agentes que trabajen en:



```text

C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering

```



No sustituye:



```text

C:\TSIS_Data\AGENTS.md

C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\AGENTS.md

C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\LOCAL_RULES.md

```



Si hay conflicto, manda la autoridad superior.



Nota de lectura: el bloque `Estado Vigente 2026-07-28` es la autoridad operativa actual de este handoff. Las secciones inferiores conservan contexto historico y no deben reabrir estados cerrados salvo contradiccion estructural demostrada.





## 0. Estado Vigente 2026-07-28



```text

core_four_market_state_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS

core_four_market_state_bounded_scaling_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_sample_preflight = SUPERSEDED_BLOCKED_SAMPLE_CARDINALITY

core_four_scale_a_eligible_representation_surface_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

experimental_core_four_scale_a_eligible_representation_surface_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_scale_a_eligible_representation_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS

eligible_instrument_pool = ACCEPTED

experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_sample_preflight_rerun = CLOSED_PASS_WITH_RESTRICTIONS

scale_a_sample_manifest = FROZEN

experimental_core_four_market_state_scale_a_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_a_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS

governed_exchange_session_calendar_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

governed_exchange_session_calendar_binding_authorization = AUTHORIZED_WITH_RESTRICTIONS

governed_exchange_session_calendar_binding_validation = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_sample_preflight = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_execution_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_builder_resolution_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_market_state_integration_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_candidate_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_candidate_physical_validation_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_b_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_b_execution = SCALE_B_CLOSED_PASS_WITH_RESTRICTIONS_OFFICIAL_NOT_AUTHORIZED

experimental_core_four_market_state_scale_c_authorization_v0_1 = SUPERSEDED_BY_V0_2_AFTER_POOL_BLOCK

experimental_core_four_market_state_scale_c_authorization_v0_2 = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_sample_preflight_v0_1 = SUPERSEDED_BLOCKED_INSTRUMENT_HISTORY_COVERAGE

experimental_core_four_market_state_scale_c_sample_preflight_v0_2 = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_sample_preflight = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_execution_surface_construction_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_execution_surface_construction = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_builder_resolution_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_market_state_integration_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_candidate_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_candidate_physical_validation_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_execution = SCALE_C_CLOSED_PASS_WITH_RESTRICTIONS_OFFICIAL_NOT_AUTHORIZED

official_market_state_candidate_promotion_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

official_market_state_candidate_promotion_review = APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS

official_market_state_candidate_promotion_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

official_market_state_candidate_promotion = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS

official_market_state_profile_artifact_validation_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

official_market_state_profile_artifact_validation = CLOSED_PASS_WITH_RESTRICTIONS

market_state_core_four_intraday_profile_v0_1 = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS

tsis_market_state_profiles_family_architecture = RECORDED_NO_EXECUTION

event_state_architecture_from_market_state_profiles = RECORDED_NO_EXECUTION

event_state_profile_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

event_policy = RECORDED_NO_EXECUTION

event_type_or_event_family_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

event_type_registry_status = POST_INITIAL_ADMISSION_REVIEW_RECORDED_WITH_RESTRICTIONS

event_type_registry_schema = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

event_type_registry_seed_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

candidate_event_families = 1

candidate_event_types = 1

accepted_event_families = 1

accepted_event_types = 1

event_type_initial_admission_review = CLOSED_WITH_MIXED_DECISIONS_NO_EXECUTION

event_type:market_data:session_opened = ACCEPTED_WITH_RESTRICTIONS_EXCHANGE_SESSION_DESIGN_ONLY

event_type:regulatory:halt_resumed = INVESTIGATIONAL_CANDIDATE_BLOCKED_PENDING_TIMESTAMP_POLICY

event_instance_binding_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_window_binding_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

market_state_profile_compatibility_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_window_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_profile_compatibility_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_instance_binding_execution = NOT_AUTHORIZED

event_window_binding_execution = NOT_AUTHORIZED

instrument_session_projection_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

instrument_session_projection_execution = NOT_AUTHORIZED

event_state_integration_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_integration_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_execution_chain_joint_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_execution_chain_joint_review = CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION

event_state_bounded_execution_chain_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_bounded_execution_chain_execution = CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT

event_state_bounded_execution_chain_physical_validation_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_bounded_execution_chain_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS

event_state_candidate_dataset_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_candidate_dataset_review = CLOSED_APPROVED_WITH_RESTRICTIONS_NO_PROMOTION

event_state_profile_promotion_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_profile_promotion_review = APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS

event_state_profile_promotion_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_profile_promotion = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS

event_state_profile_artifact_validation_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_profile_artifact_validation = CLOSED_PASS_WITH_RESTRICTIONS

event_state_operational_registry_or_consumption_policy_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_operational_registry_or_consumption_policy_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

runtime_capabilities_architecture = RECORDED_ARCHITECTURE_NO_EXECUTION

runtime_capabilities_layer = 08_RUNTIME_CAPABILITIES

market_state_on_demand_capability_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_request_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_execution_plan_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_profile_resolver_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_universe_resolver_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_source_resolver_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_partition_and_coverage_resolver_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_materializer_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_validator_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_candidate_dataset_registry_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_run_lifecycle_and_manifest_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_on_demand_execution_chain_joint_review = CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION

market_state_bounded_on_demand_execution_authorization = CONSUMED_BY_RUN

market_state_bounded_on_demand_execution = CLOSED_PASS_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED

market_state_bounded_on_demand_execution_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z

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

market_state_source_contract_runtime_reads = 0

market_state_source_schema_runtime_reads = 0

market_state_source_consumption_policy_runtime_reads = 0

market_state_source_parquet_files_read = 0

market_state_resolved_source_sets_created = 0

market_state_partition_coverage_resolver_executions = 1

market_state_partition_manifests_created = 0

market_state_coverage_manifests_created = 0

market_state_existing_dataset_registry_runtime_reads = 0

market_state_source_manifest_runtime_reads = 0

market_state_partition_status_transitions = 0

market_state_execution_plan_instances_created = 1

market_state_materializer_executions = 1

market_state_builder_executions = 1

market_state_staging_directories_created = 0

market_state_candidate_data_files_written = 2

market_state_candidate_parquet_files_written = 1

market_state_output_manifests_created = 0

market_state_lineage_manifests_created = 0

market_state_content_hashes_computed = 0

market_state_validation_reports_created = 5

market_state_validator_executions = 1

market_state_candidate_files_read = 0

market_state_parquet_files_read = 0

market_state_partition_status_changes = 0

market_state_quarantine_actions = 0

market_state_dataset_registry_entries_written = 1

market_state_registry_runtime_reads = 0

market_state_datasets_registered = 1

market_state_datasets_promoted = 0

market_state_datasets_superseded = 0

market_state_quarantine_transitions = 0

market_state_official_dataset = false

market_state_run_records_created = 1

market_state_run_manifests_created = 0

market_state_final_manifests_created = 1

market_state_heartbeat_records_written = 0

market_state_run_state_transitions = 0

market_state_recovery_actions = 0

market_state_execution_authorizations_consumed = 1

market_state_execution_plans_consumed = 1

market_state_joint_reviews_closed = 1

market_state_on_demand_incremental_overlap_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION

market_state_on_demand_incremental_overlap_authorized_baseline_dataset = market_state_candidate_dataset_v0_1_433288b634924676

market_state_on_demand_incremental_overlap_authorized_delta_session = 2023-03-20

market_state_on_demand_incremental_overlap_authorized_requested_contexts = 12

market_state_on_demand_incremental_overlap_expected_reusable_validated_contexts = 8

market_state_on_demand_incremental_overlap_expected_known_unavailable_contexts = 1

market_state_on_demand_incremental_overlap_expected_delta_to_build_contexts = 3

market_state_on_demand_incremental_overlap_execution = CLOSED_PASS_INCREMENTAL_OVERLAP_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED

market_state_on_demand_incremental_overlap_execution_run = market_state_on_demand_incremental_overlap_execution_v0_1_20260725T064143Z

market_state_on_demand_incremental_overlap_requested_contexts = 12

market_state_on_demand_incremental_overlap_reusable_validated_contexts = 8

market_state_on_demand_incremental_overlap_delta_materialized_candidate_rows = 3

market_state_on_demand_incremental_overlap_combined_candidate_contexts_represented = 11

market_state_on_demand_incremental_overlap_unavailable_contexts = 1

market_state_on_demand_incremental_overlap_hard_validation_failures = 0

market_state_on_demand_incremental_overlap_materializer_delta_only_pass = true

market_state_on_demand_incremental_overlap_baseline_registry_entry_mutations = 0

market_state_on_demand_incremental_overlap_candidate_dataset_fingerprint = f2cfd5cf55d0c1be1722693cc0216ffd425bbb869e19c17745976c030f2c7a2a

market_state_on_demand_incremental_overlap_scientific_dataset_fingerprint = 7103e4fdbae205e4bccbeb0c436508f62b016107b4b2756c549073dae971bb5f

market_state_on_demand_incremental_overlap_reuse_eligibility = pending_incremental_determinism_validation

market_state_on_demand_incremental_overlap_official_dataset = false

market_state_on_demand_incremental_overlap_production = false

market_state_on_demand_incremental_overlap_downstream = false

market_state_on_demand_incremental_overlap_candidate_dataset_review = CLOSED_PASS_INCREMENTAL_OVERLAP_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION

market_state_on_demand_incremental_overlap_candidate_dataset_review_id = market_state_on_demand_incremental_overlap_candidate_dataset_review_v0_1_20260725T000000Z

market_state_on_demand_incremental_overlap_candidate_dataset_review_requested_contexts = 12

market_state_on_demand_incremental_overlap_candidate_dataset_review_represented_contexts = 11

market_state_on_demand_incremental_overlap_candidate_dataset_review_baseline_reused_rows = 8

market_state_on_demand_incremental_overlap_candidate_dataset_review_delta_materialized_rows = 3

market_state_on_demand_incremental_overlap_candidate_dataset_review_unavailable_contexts = 1

market_state_on_demand_incremental_overlap_candidate_dataset_review_unaccounted_contexts = 0

market_state_on_demand_incremental_overlap_candidate_dataset_review_hard_failures = 0

market_state_on_demand_incremental_overlap_candidate_dataset_review_candidate_dataset_validated = true

market_state_on_demand_incremental_overlap_candidate_dataset_review_next_gate = market_state_on_demand_incremental_overlap_idempotency_reuse_test_authorization_v0_1

market_state_on_demand_incremental_overlap_idempotency_reuse_test_authorization = AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION

market_state_on_demand_incremental_overlap_idempotency_reuse_test_authorized_next_gate = market_state_on_demand_incremental_overlap_idempotency_reuse_test_v0_1

market_state_on_demand_incremental_overlap_idempotency_reuse_test_contract_content_sha256_excluding_hash_field = 00108c6c9ad5114c731357c29f5239199ecea91c07c3bbde95d9521c2c7a3cf5

market_state_on_demand_incremental_overlap_idempotency_reuse_policy = reuse_if_exact_validated_overlap_match

market_state_on_demand_incremental_overlap_idempotency_reuse_expected_materializer_executions = 0

market_state_on_demand_incremental_overlap_idempotency_reuse_expected_delta_materializer_executions = 0

market_state_on_demand_incremental_overlap_idempotency_reuse_expected_new_candidate_registry_entries = 0

market_state_on_demand_incremental_overlap_idempotency_reuse_test_run = market_state_on_demand_incremental_overlap_idempotency_reuse_test_v0_1_20260727T094006Z

market_state_on_demand_incremental_overlap_idempotency_reuse_test_status = CLOSED_PASS_INCREMENTAL_OVERLAP_IDEMPOTENCY_REUSE_HIT_WITH_RESTRICTIONS

market_state_on_demand_incremental_overlap_idempotency_status = PROVEN_FOR_INCREMENTAL_OVERLAP_REUSE

market_state_on_demand_incremental_overlap_idempotency_requested_contexts = 12

market_state_on_demand_incremental_overlap_idempotency_represented_contexts = 11

market_state_on_demand_incremental_overlap_idempotency_unavailable_contexts = 1

market_state_on_demand_incremental_overlap_idempotency_materializer_executions = 0

market_state_on_demand_incremental_overlap_idempotency_delta_materializer_executions = 0

market_state_on_demand_incremental_overlap_idempotency_source_market_data_rows_read = 0

market_state_on_demand_incremental_overlap_idempotency_source_candidate_records_read = 0

market_state_on_demand_incremental_overlap_idempotency_candidate_parquet_files_read = 0

market_state_on_demand_incremental_overlap_idempotency_new_candidate_parquet_files = 0

market_state_on_demand_incremental_overlap_idempotency_new_candidate_dataset_registry_entries = 0

market_state_on_demand_incremental_overlap_idempotency_baseline_registry_entry_mutations = 0

market_state_on_demand_incremental_overlap_idempotency_combined_candidate_registry_entry_mutations = 0

market_state_on_demand_second_generation_incremental_extension_authorization = AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION

market_state_on_demand_second_generation_incremental_extension_authorized_next_gate = market_state_on_demand_second_generation_incremental_extension_v0_1

market_state_on_demand_second_generation_incremental_extension_run = market_state_on_demand_second_generation_incremental_extension_v0_1_20260727T103901Z

market_state_on_demand_second_generation_incremental_extension_status = CLOSED_PASS_SECOND_GENERATION_INCREMENTAL_EXTENSION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED

market_state_on_demand_second_generation_incremental_extension_invalid_attempt = market_state_on_demand_second_generation_incremental_extension_v0_1_20260727T103756Z

market_state_on_demand_second_generation_incremental_extension_invalid_attempt_status = CLOSED_FAILED_RUNTIME_ARTIFACT_PATH_TOO_LONG

market_state_on_demand_second_generation_incremental_extension_reusable_validated = 11

market_state_on_demand_second_generation_incremental_extension_second_delta_materialized_rows = 3

market_state_on_demand_second_generation_incremental_extension_combined_candidate_contexts_represented = 14

market_state_on_demand_second_generation_incremental_extension_unavailable_contexts = 1

market_state_on_demand_second_generation_incremental_extension_hard_validation_failures = 0

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_fingerprint = 5e8da235219628220bac462f342cab469fbd2a48d047eef0772cb5a2cffe893f

market_state_on_demand_second_generation_incremental_extension_next_gate = market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review = CLOSED_PASS_SECOND_GENERATION_INCREMENTAL_CANDIDATE_DATASET_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_id = market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1_20260727T000000Z

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_requested_contexts = 15

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_represented_contexts = 14

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_base_combined_reused_contexts = 11

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_second_delta_materialized_rows = 3

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_unavailable_contexts = 1

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_unaccounted_contexts = 0

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_hard_failures = 0

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_candidate_dataset_validated = true

market_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_next_gate = market_state_on_demand_incremental_lineage_chain_validation_v0_1

market_state_on_demand_incremental_lineage_chain_validation = CLOSED_PASS_INCREMENTAL_LINEAGE_CHAIN_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION

market_state_on_demand_incremental_lineage_chain_validation_id = market_state_on_demand_incremental_lineage_chain_validation_v0_1_20260727T000000Z

market_state_on_demand_incremental_lineage_chain_validation_requested_contexts = 15

market_state_on_demand_incremental_lineage_chain_validation_represented_contexts = 14

market_state_on_demand_incremental_lineage_chain_validation_baseline_origin_rows = 8

market_state_on_demand_incremental_lineage_chain_validation_delta1_origin_rows = 3

market_state_on_demand_incremental_lineage_chain_validation_delta2_origin_rows = 3

market_state_on_demand_incremental_lineage_chain_validation_unavailable_contexts = 1

market_state_on_demand_incremental_lineage_chain_validation_unaccounted_contexts = 0

market_state_on_demand_incremental_lineage_chain_validation_hard_failures = 0

market_state_on_demand_incremental_lineage_chain_validation_next_gate = market_state_on_demand_scale_validation_v0_1

market_state_on_demand_scale_validation = CLOSED_PASS_SCALE_VALIDATION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED

market_state_on_demand_scale_validation_run = market_state_on_demand_scale_validation_v0_1_20260727T133641Z

market_state_on_demand_scale_validation_invalid_attempt = market_state_on_demand_scale_validation_v0_1_20260727T133242Z

market_state_on_demand_scale_validation_invalid_attempt_status = CLOSED_FAILED_PRE_MATERIALIZATION_SCHEMA_CONTRACT_FIELD_MISMATCH

market_state_on_demand_scale_validation_requested_contexts = 120

market_state_on_demand_scale_validation_represented_contexts = 104

market_state_on_demand_scale_validation_reusable_validated_contexts = 14

market_state_on_demand_scale_validation_delta_materialized_contexts = 90

market_state_on_demand_scale_validation_unavailable_contexts = 16

market_state_on_demand_scale_validation_unaccounted_contexts = 0

market_state_on_demand_scale_validation_source_candidate_records_read = 104

market_state_on_demand_scale_validation_source_market_data_rows_read = 0

market_state_on_demand_scale_validation_candidate_parquet_files_written = 1

market_state_on_demand_scale_validation_candidate_registry_entries_written = 1

market_state_on_demand_scale_validation_hard_validation_failures = 0

market_state_on_demand_scale_validation_candidate_dataset_fingerprint = 516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416

market_state_on_demand_scale_validation_scientific_dataset_fingerprint = 0cc901750cabe9fef67a2ee3ebcd6a30c4a807a7b35cda8d29dbd8baa9ddad6e

market_state_on_demand_scale_validation_official_dataset = false

market_state_on_demand_scale_validation_production = false

market_state_on_demand_scale_validation_downstream = false

market_state_on_demand_scale_validation_next_gate = market_state_on_demand_capability_promotion_review_v0_1

market_state_on_demand_capability_promotion_review = CLOSED_PASS_CAPABILITY_PROMOTED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION

market_state_on_demand_capability_promotion_review_run = market_state_on_demand_capability_promotion_review_v0_1_20260727T140338Z

market_state_on_demand_capability_promotion_decision = promote_with_restrictions_candidate_generation_only

market_state_on_demand_capability_status_after_review = PROMOTED_WITH_RESTRICTIONS_CANDIDATE_GENERATION_ONLY

market_state_on_demand_capability_promotion_reviewed_evidence_items = 9

market_state_on_demand_capability_promotion_hard_review_failures = 0

market_state_on_demand_capability_promotion_source_market_data_rows_read = 0

market_state_on_demand_capability_promotion_parquet_content_rows_read = 0

market_state_on_demand_capability_promotion_materializer_executions = 0

market_state_on_demand_capability_promotion_validator_executions = 0

market_state_on_demand_capability_promotion_new_candidate_registry_entries_written = 0

market_state_on_demand_capability_promotion_datasets_written = 0

market_state_on_demand_capability_promotion_official_dataset = false

market_state_on_demand_capability_promotion_production = false

market_state_on_demand_capability_promotion_downstream = false

market_state_on_demand_capability_promotion_next_gate = market_state_capability_consumption_policy_v0_1

market_state_capability_consumption_policy = CLOSED_PASS_CAPABILITY_CONSUMPTION_POLICY_ESTABLISHED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION

market_state_capability_consumption_policy_run = market_state_capability_consumption_policy_v0_1_20260727T142133Z

market_state_capability_consumption_policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY

market_state_capability_consumption_policy_hard_failures = 0

market_state_capability_consumption_policy_source_market_data_rows_read = 0

market_state_capability_consumption_policy_parquet_content_rows_read = 0

market_state_capability_consumption_policy_materializer_executions = 0

market_state_capability_consumption_policy_validator_executions = 0

market_state_capability_consumption_policy_new_candidate_registry_entries_written = 0

market_state_capability_consumption_policy_registry_entry_mutations = 0

market_state_capability_consumption_policy_datasets_written = 0

market_state_capability_consumption_policy_official_dataset = false

market_state_capability_consumption_policy_production = false

market_state_capability_consumption_policy_downstream = false

market_state_capability_consumption_policy_event_state_on_demand_execution = false

market_state_capability_consumption_policy_next_gate = event_state_on_demand_capability_design_authorization_v0_1

event_state_on_demand_capability_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_on_demand_capability_design_authorization_target = event_state_on_demand_capability_design_v0_1

event_state_on_demand_capability_design_authorization_profile = event_state_core_four_intraday_profile_v0_1

event_state_on_demand_capability_design_authorization_event_type_scope = event_type:market_data:session_opened

event_state_on_demand_capability_design_authorization_subject_scope = exchange_session

event_state_on_demand_capability_design_authorization_execution = false

event_state_on_demand_capability_design_authorization_materialization = false

event_state_on_demand_capability_design_authorization_downstream = false

event_state_on_demand_capability_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_on_demand_capability_design_capability_id = event_state_on_demand_capability_v0_1

event_state_on_demand_capability_design_market_state_dependency_resolver = RECORDED_DESIGN_PRINCIPLE

event_state_on_demand_capability_design_market_state_design_id = market_state_on_demand_capability_v0_1

event_state_on_demand_capability_design_market_state_runtime_id = market_state_on_demand_runtime_capability_v0_1

event_state_on_demand_capability_design_identity_relation = promoted_runtime_identity_of

event_state_on_demand_capability_design_market_state_access = metadata_only_design_time_requires_future_execution_authorization

event_state_on_demand_capability_design_direct_candidate_path_consumption = false

event_state_on_demand_capability_design_event_state_requests_created = 0

event_state_on_demand_capability_design_market_state_dependency_requests_created = 0

event_state_on_demand_capability_design_event_instances_created = 0

event_state_on_demand_capability_design_event_window_bindings_created = 0

event_state_on_demand_capability_design_records_emitted = 0

event_state_on_demand_capability_design_datasets_written = 0

event_state_on_demand_capability_design_registry_entries_written = 0

event_state_on_demand_capability_design_next_gate = event_state_request_contract_design_v0_1

event_state_request_contract_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_request_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_request_contract = event_state_request_contract_v0_1

event_state_request_contract_request_type = event_state

event_state_request_contract_event_type_scope = event_type:market_data:session_opened

event_state_request_contract_subject_scope = exchange_session

event_state_request_contract_market_state_dependency_mode = emit_or_resolve_market_state_subrequest_through_runtime_capability

event_state_request_contract_direct_market_state_path_consumption = false

event_state_request_contract_requests_created = 0

event_state_request_contract_event_instances_created = 0

event_state_request_contract_records_emitted = 0

event_state_request_contract_datasets_written = 0

event_state_request_contract_registry_entries_written = 0

event_state_request_contract_next_gate = event_state_dependency_resolution_design_v0_1

event_state_dependency_resolution_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_dependency_resolution_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_dependency_resolution_contract = event_state_dependency_resolution_contract_v0_1

event_state_dependency_resolution_output_block = resolved_event_state_dependencies_v0_1

event_state_dependency_resolution_event_type_scope = event_type:market_data:session_opened

event_state_dependency_resolution_subject_scope = exchange_session

event_state_dependency_resolution_market_state_dependency_mode = emit_or_resolve_market_state_subrequest_through_runtime_capability

event_state_dependency_resolution_direct_market_state_path_consumption = false

event_state_dependency_resolution_records_created = 0

event_state_dependency_resolution_execution_plans_created = 0

event_state_dependency_resolution_event_instances_created = 0

event_state_dependency_resolution_records_emitted = 0

event_state_dependency_resolution_datasets_written = 0

event_state_dependency_resolution_registry_entries_written = 0

event_state_dependency_resolution_next_gate = event_state_execution_plan_contract_design_v0_1

event_state_execution_plan_contract_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_execution_plan_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_execution_plan_contract = event_state_execution_plan_contract_v0_1

event_state_execution_plan_contract_input_block = resolved_event_state_dependencies_v0_1

event_state_execution_plan_contract_output = frozen_event_state_execution_plan_contract

event_state_execution_plan_event_type_scope = event_type:market_data:session_opened

event_state_execution_plan_subject_scope = exchange_session

event_state_execution_plan_direct_market_state_path_consumption = false

event_state_execution_plan_records_created = 0

event_state_execution_plan_event_instances_created = 0

event_state_execution_plan_records_emitted = 0

event_state_execution_plan_datasets_written = 0

event_state_execution_plan_registry_entries_written = 0

event_state_execution_plan_next_gate = event_state_materializer_design_v0_1

event_state_materializer_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_materializer_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_materializer_contract = event_state_materializer_contract_v0_1

event_state_materializer_required_input = authorized_frozen_event_state_execution_plan

event_state_materializer_event_type_scope = event_type:market_data:session_opened

event_state_materializer_subject_scope = exchange_session

event_state_materializer_direct_market_state_path_consumption = false

event_state_materializer_executions = 0

event_state_materializer_event_instances_created = 0

event_state_materializer_records_emitted = 0

event_state_materializer_candidate_files_written = 0

event_state_materializer_registry_entries_written = 0

event_state_materializer_next_gate = event_state_validator_design_v0_1

event_state_validator_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_validator_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_validator_contract = event_state_validator_contract_v0_1

event_state_validator_required_input = candidate_unvalidated_event_state_output_under_future_authorization

event_state_validator_event_type_scope = event_type:market_data:session_opened

event_state_validator_subject_scope = exchange_session

event_state_validator_direct_market_state_path_consumption = false

event_state_validator_executions = 0

event_state_validator_candidate_files_read = 0

event_state_validator_validation_reports_created = 0

event_state_validator_registry_entries_written = 0

event_state_validator_records_emitted = 0

event_state_validator_datasets_written = 0

event_state_validator_next_gate = event_state_candidate_dataset_registry_design_v0_1

event_state_candidate_dataset_registry_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_candidate_dataset_registry_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_state_candidate_dataset_registry_contract = event_state_candidate_dataset_registry_contract_v0_1

event_state_candidate_dataset_registry_required_input = validator_result_for_candidate_event_state_output_under_future_authorization

event_state_candidate_dataset_registry_event_type_scope = event_type:market_data:session_opened

event_state_candidate_dataset_registry_subject_scope = exchange_session

event_state_candidate_dataset_registry_direct_market_state_path_consumption = false

event_state_candidate_dataset_registry_entries_written = 0

event_state_candidate_dataset_registry_runtime_reads = 0

event_state_candidate_dataset_registry_datasets_registered = 0

event_state_candidate_dataset_registry_candidate_files_read = 0

event_state_candidate_dataset_registry_market_state_candidate_files_read = 0

event_state_candidate_dataset_registry_records_emitted = 0

event_state_candidate_dataset_registry_datasets_written = 0

event_state_candidate_dataset_registry_next_gate = event_state_on_demand_execution_chain_joint_review_v0_1

event_state_on_demand_execution_chain_joint_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_on_demand_execution_chain_joint_review = CLOSED_APPROVED_FOR_BOUNDED_EXECUTION_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION

event_state_on_demand_execution_chain_joint_review_matrix = event_state_on_demand_execution_chain_joint_review_matrix_v0_1

event_state_on_demand_execution_chain_joint_review_hard_findings = 0

event_state_on_demand_execution_chain_joint_review_restriction_findings = 3

event_state_on_demand_execution_chain_joint_review_reviewed_contracts = 9

event_state_on_demand_execution_chain_joint_review_event_type_scope = event_type:market_data:session_opened

event_state_on_demand_execution_chain_joint_review_subject_scope = exchange_session

event_state_on_demand_execution_chain_joint_review_market_state_dependency_mode = runtime_capability_subrequest_only

event_state_on_demand_execution_chain_joint_review_direct_market_state_path_consumption = false

event_state_on_demand_execution_chain_joint_review_requests_created = 0

event_state_on_demand_execution_chain_joint_review_execution_plans_created = 0

event_state_on_demand_execution_chain_joint_review_event_instances_created = 0

event_state_on_demand_execution_chain_joint_review_market_state_candidate_files_read = 0

event_state_on_demand_execution_chain_joint_review_materializer_executions = 0

event_state_on_demand_execution_chain_joint_review_validator_executions = 0

event_state_on_demand_execution_chain_joint_review_registry_entries_written = 0

event_state_on_demand_execution_chain_joint_review_records_emitted = 0

event_state_on_demand_execution_chain_joint_review_datasets_written = 0

event_state_on_demand_execution_chain_joint_review_next_gate = event_state_on_demand_bounded_execution_authorization_v0_1

event_state_on_demand_bounded_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_on_demand_bounded_execution_authorization_readout = AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION

event_state_on_demand_bounded_execution_authorized_next_gate = event_state_on_demand_bounded_execution_v0_1

event_state_on_demand_bounded_execution_event_type_scope = event_type:market_data:session_opened

event_state_on_demand_bounded_execution_subject_scope = exchange_session

event_state_on_demand_bounded_execution_exchange_scope = XNYS

event_state_on_demand_bounded_execution_sessions = 2021-01-19,2021-03-15,2022-11-25

event_state_on_demand_bounded_execution_instrument_projection_scope = AAME,ABEO,ABUS stable FIGI share-class identifiers

event_state_on_demand_bounded_execution_max_event_state_contexts = 9

event_state_on_demand_bounded_execution_market_state_dependency_mode = runtime_capability_subrequest_or_exact_validated_candidate_reference

event_state_on_demand_bounded_execution_direct_market_state_path_consumption = false

event_state_on_demand_bounded_execution_requests_created = 0

event_state_on_demand_bounded_execution_execution_plans_created = 0

event_state_on_demand_bounded_execution_records_emitted = 0

event_state_on_demand_bounded_execution_datasets_written = 0

event_state_on_demand_bounded_execution_preflight_correction = CLOSED_PASS_PREFLIGHT_BLOCKERS_RESOLVED_NO_EXECUTION

event_state_on_demand_bounded_execution_authority_bundle = event_state_on_demand_bounded_execution_authority_bundle_v0_1.json

event_state_on_demand_bounded_execution_authority_bundle_sha256 = 71e25390273f46110aab92376ab87341a6a43a1589f6510a518c1402235aca4c

event_state_on_demand_bounded_execution_market_state_dependency_consumption_authorization = market_state_capability_event_state_bounded_dependency_consumption_authorization_v0_1

event_state_on_demand_bounded_execution_effective_market_state_dependency_mode = emit_or_resolve_market_state_subrequest_through_runtime_capability

event_state_on_demand_bounded_execution_effective_market_state_dependency_reuse_policy = reuse_if_exact_validated_dependency_match_or_block

event_state_on_demand_bounded_execution_effective_event_window_definition_id = session_opened_at_anchor_context_v0_1

event_state_on_demand_bounded_execution_effective_output_format = jsonl

event_state_on_demand_bounded_execution_maximum_output_files = 1

event_state_on_demand_bounded_execution_maximum_output_records = 9

event_state_on_demand_bounded_execution_maximum_output_bytes = 1048576

event_state_on_demand_bounded_execution_preflight_requests_created = 0

event_state_on_demand_bounded_execution_preflight_market_state_reads = 0

event_state_on_demand_bounded_execution_preflight_records_emitted = 0

event_state_on_demand_bounded_execution_preflight_datasets_written = 0

event_state_on_demand_bounded_execution_run = event_state_on_demand_bounded_execution_v0_1_20260727T200322Z

event_state_on_demand_bounded_execution_status = CLOSED_PASS_EVENT_STATE_ON_DEMAND_BOUNDED_EXECUTION_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED

event_state_on_demand_bounded_execution_failed_attempt = event_state_on_demand_bounded_execution_v0_1_20260727T200207Z

event_state_on_demand_bounded_execution_failed_attempt_status = FAILED_TECHNICAL_RUNNER_BUG_BEFORE_FINAL_MANIFEST

event_state_on_demand_bounded_execution_request_fingerprint = f82e424b60a69e2e9edec00e3dcf456c2042d18b334366dab76622286fac6ade

event_state_on_demand_bounded_execution_dependency_resolution_fingerprint = c89dc7ece24ba916dadd1046b8784b66febe6c91175781a6a609f3ae2f379ec8

event_state_on_demand_bounded_execution_plan_fingerprint = 2dc97d398c7c7dd56789628be951b96a19c7f2389febe1c5922d753a7f7f4276

event_state_on_demand_bounded_execution_source_market_state_candidate_dataset_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b

event_state_on_demand_bounded_execution_candidate_dataset_fingerprint = d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33

event_state_on_demand_bounded_execution_logical_dataset_fingerprint = 1b981958488e69f8f553c9197861bbffeed2d5388437c1113f9e21422b9cf970

event_state_on_demand_bounded_execution_validation_result_fingerprint = 2f4797da1a74c06a7061fe1e597299d0d1e9f5d55c82ec147ff66b5891550361

event_state_on_demand_bounded_execution_registry_entry_fingerprint = 5a78f487ee549ff38e13547bf0324add50556e9aed054a536017b6a4f111fa4b

event_state_on_demand_bounded_execution_requested_contexts = 9

event_state_on_demand_bounded_execution_represented_contexts = 8

event_state_on_demand_bounded_execution_unavailable_contexts = 1

event_state_on_demand_bounded_execution_event_instances_created = 3

event_state_on_demand_bounded_execution_event_window_bindings_created = 3

event_state_on_demand_bounded_execution_instrument_session_projections_created = 9

event_state_on_demand_bounded_execution_market_state_candidate_files_read = 1

event_state_on_demand_bounded_execution_market_state_candidate_records_read = 8

event_state_on_demand_bounded_execution_source_market_data_rows_read = 0

event_state_on_demand_bounded_execution_fallback_uses = 0

event_state_on_demand_bounded_execution_hard_validation_failures = 0

event_state_on_demand_bounded_execution_candidate_registry_entries_written = 1

event_state_on_demand_bounded_execution_official_dataset = false

event_state_on_demand_bounded_execution_production = false

event_state_on_demand_bounded_execution_downstream = false

event_state_on_demand_bounded_execution_next_gate = event_state_on_demand_bounded_candidate_dataset_review_v0_1

event_state_on_demand_bounded_candidate_dataset_review = CLOSED_APPROVED_AS_EVENT_STATE_ON_DEMAND_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION

event_state_on_demand_bounded_candidate_dataset_review_run = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T202013Z

event_state_on_demand_bounded_candidate_dataset_review_failed_attempt_1 = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T201823Z

event_state_on_demand_bounded_candidate_dataset_review_failed_attempt_1_status = FAILED_TECHNICAL_REVIEWER_MANIFEST_SHAPE_BUG_BEFORE_REVIEW_CLOSURE

event_state_on_demand_bounded_candidate_dataset_review_failed_attempt_2 = event_state_on_demand_bounded_candidate_dataset_review_v0_1_20260727T201924Z

event_state_on_demand_bounded_candidate_dataset_review_failed_attempt_2_status = FAILED_TECHNICAL_REVIEWER_FAILURE_MANIFEST_FIELD_BUG_BEFORE_REVIEW_CLOSURE

event_state_on_demand_bounded_candidate_dataset_review_candidate_fingerprint = d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33

event_state_on_demand_bounded_candidate_dataset_review_logical_fingerprint = 1b981958488e69f8f553c9197861bbffeed2d5388437c1113f9e21422b9cf970

event_state_on_demand_bounded_candidate_dataset_review_requested_contexts = 9

event_state_on_demand_bounded_candidate_dataset_review_represented_contexts = 8

event_state_on_demand_bounded_candidate_dataset_review_unavailable_contexts = 1

event_state_on_demand_bounded_candidate_dataset_review_unaccounted_contexts = 0

event_state_on_demand_bounded_candidate_dataset_review_hard_failures = 0

event_state_on_demand_bounded_candidate_dataset_review_registry_entry_mutations = 0

event_state_on_demand_bounded_candidate_dataset_review_materializer_executions = 0

event_state_on_demand_bounded_candidate_dataset_review_market_state_reads = 0

event_state_on_demand_bounded_candidate_dataset_review_official_dataset = false

event_state_on_demand_bounded_candidate_dataset_review_production = false

event_state_on_demand_bounded_candidate_dataset_review_downstream = false

event_state_on_demand_bounded_candidate_dataset_review_next_gate = event_state_on_demand_bounded_deterministic_rerun_authorization_v0_1

event_state_on_demand_bounded_deterministic_rerun_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_state_on_demand_bounded_deterministic_rerun = CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS

event_state_on_demand_bounded_deterministic_rerun_run_id = event_state_on_demand_bounded_deterministic_rerun_v0_1_20260728T070338Z

event_state_on_demand_bounded_deterministic_rerun_determinism_status = PROVEN_FOR_BOUNDED_SCOPE

event_state_on_demand_bounded_deterministic_rerun_requested_contexts = 9

event_state_on_demand_bounded_deterministic_rerun_represented_contexts = 8

event_state_on_demand_bounded_deterministic_rerun_unavailable_contexts = 1

event_state_on_demand_bounded_deterministic_rerun_records_emitted = 8

event_state_on_demand_bounded_deterministic_rerun_blocking_failures = 0

event_state_on_demand_bounded_deterministic_rerun_runtime_only_differences = 4

event_state_on_demand_bounded_deterministic_rerun_comparison_fingerprint = 9580cc5f747ef6c6fd3ec2b3c92460a7ce0eba6e9164248e636ab241dcf55c55

event_state_on_demand_bounded_deterministic_rerun_materializer_executed = true

event_state_on_demand_bounded_deterministic_rerun_market_state_rematerialized = false

event_state_on_demand_bounded_deterministic_rerun_candidate_dataset_registry_entries_written = 0

event_state_on_demand_bounded_deterministic_rerun_reuse_eligibility_changes = 0

event_state_on_demand_bounded_deterministic_rerun_authorization_authorized_next_gate = event_state_on_demand_bounded_deterministic_rerun_v0_1

event_state_on_demand_bounded_deterministic_rerun_next_gate = event_state_on_demand_bounded_determinism_validation_v0_1

event_state_on_demand_bounded_deterministic_rerun_authorization_contract_hash = d5a5ee2515716b546189a8b8ac606857de1244fdbd5c3ee678ddaeacd6024af1

event_state_on_demand_bounded_deterministic_rerun_event_state_reuse_policy = force_rebuild_for_determinism_test

event_state_on_demand_bounded_deterministic_rerun_market_state_dependency_rematerialization_required = false

event_state_on_demand_bounded_deterministic_rerun_expected_market_state_candidate_fingerprint = 433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b

event_state_on_demand_bounded_deterministic_rerun_authorization_official_dataset = false

event_state_on_demand_bounded_deterministic_rerun_authorization_production = false

event_state_on_demand_bounded_deterministic_rerun_authorization_downstream = false

event_state_on_demand_bounded_determinism_validation = CLOSED_APPROVED_DETERMINISM_FOR_BOUNDED_SCOPE_WITH_RESTRICTIONS_NO_REUSE_TRANSITION

event_state_on_demand_bounded_determinism_validation_id = event_state_on_demand_bounded_determinism_validation_v0_1_20260728T000000Z

event_state_on_demand_bounded_determinism_validation_baseline_run = event_state_on_demand_bounded_execution_v0_1_20260727T200322Z

event_state_on_demand_bounded_determinism_validation_rerun_run = event_state_on_demand_bounded_deterministic_rerun_v0_1_20260728T070338Z

event_state_on_demand_bounded_determinism_validation_status = PROVEN_FOR_BOUNDED_SCOPE

event_state_on_demand_bounded_determinism_validation_comparison_fingerprint = 9580cc5f747ef6c6fd3ec2b3c92460a7ce0eba6e9164248e636ab241dcf55c55

event_state_on_demand_bounded_determinism_validation_normalized_logical_dataset_fingerprint = e2c47083b8dd560e67bcda32b0063cf9f468754e34f76b82e9f839046d375699

event_state_on_demand_bounded_determinism_validation_requested_contexts = 9

event_state_on_demand_bounded_determinism_validation_represented_contexts = 8

event_state_on_demand_bounded_determinism_validation_unavailable_contexts = 1

event_state_on_demand_bounded_determinism_validation_blocking_failures = 0

event_state_on_demand_bounded_determinism_validation_hard_failures = 0

event_state_on_demand_bounded_determinism_validation_runtime_only_differences = 4

event_state_on_demand_bounded_determinism_validation_reuse_transition_ready = true

event_state_on_demand_bounded_determinism_validation_reuse_eligibility_after_validation = pending_idempotency_reuse_test

event_state_on_demand_bounded_determinism_validation_reuse_eligibility_changes = 0

event_state_on_demand_bounded_determinism_validation_official_dataset = false

event_state_on_demand_bounded_determinism_validation_production = false

event_state_on_demand_bounded_determinism_validation_downstream = false

event_state_on_demand_bounded_determinism_validation_next_gate = event_state_on_demand_bounded_idempotency_reuse_test_authorization_v0_1

event_state_on_demand_bounded_idempotency_reuse_test_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED_BY_REUSE_TEST

event_state_on_demand_bounded_idempotency_reuse_test_authorization_parent_gate = event_state_on_demand_bounded_determinism_validation_v0_1

event_state_on_demand_bounded_idempotency_reuse_test_authorization_authorized_next_gate = event_state_on_demand_bounded_idempotency_reuse_test_v0_1

event_state_on_demand_bounded_idempotency_reuse_test_authorization_baseline_dataset_id = event_state_candidate_dataset_v0_1_d5662103e1c45f90

event_state_on_demand_bounded_idempotency_reuse_test_authorization_baseline_request_fingerprint = f82e424b60a69e2e9edec00e3dcf456c2042d18b334366dab76622286fac6ade

event_state_on_demand_bounded_idempotency_reuse_test_authorization_baseline_candidate_dataset_fingerprint = d5662103e1c45f90847b51e69b0e698243bde231758fa3c864e24c4a6839be33

event_state_on_demand_bounded_idempotency_reuse_test_authorization_normalized_logical_dataset_fingerprint = e2c47083b8dd560e67bcda32b0063cf9f468754e34f76b82e9f839046d375699

event_state_on_demand_bounded_idempotency_reuse_test_authorization_contract_hash = 50ede549474d286c3e1e0f71ff270e3e2baadebd57f328cc9919a9c8b73ab4f6

event_state_on_demand_bounded_idempotency_reuse_test_authorization_reuse_policy = reuse_if_exact_validated_event_state_match

event_state_on_demand_bounded_idempotency_reuse_test_authorization_maximum_runs = 1

event_state_on_demand_bounded_idempotency_reuse_test_authorization_event_state_materializer_executions_expected = 0

event_state_on_demand_bounded_idempotency_reuse_test_authorization_market_state_materializer_executions_expected = 0

event_state_on_demand_bounded_idempotency_reuse_test_authorization_candidate_records_read_expected = 0

event_state_on_demand_bounded_idempotency_reuse_test_authorization_new_candidate_dataset_registry_entries_expected = 0

event_state_on_demand_bounded_idempotency_reuse_test_authorization_reuse_eligibility_changes = 0

event_state_on_demand_bounded_idempotency_reuse_test_authorization_official_dataset = false

event_state_on_demand_bounded_idempotency_reuse_test_authorization_production = false

event_state_on_demand_bounded_idempotency_reuse_test_authorization_downstream = false

event_state_on_demand_bounded_idempotency_reuse_test_authorization_next_gate = event_state_on_demand_bounded_idempotency_reuse_test_v0_1

market_state_on_demand_second_generation_incremental_extension_delta2_session = 2024-03-11

market_state_on_demand_second_generation_incremental_extension_requested_contexts = 15

market_state_on_demand_second_generation_incremental_extension_expected_reusable_validated = 11

market_state_on_demand_second_generation_incremental_extension_expected_unavailable = 1

market_state_on_demand_second_generation_incremental_extension_expected_to_build_delta2 = 3

market_state_joint_review_hard_findings = 0

market_state_joint_review_restriction_findings = 2

market_state_bounded_on_demand_execution_authorizations_recorded = 1

market_state_bounded_on_demand_execution_authorized_max_contexts = 9

market_state_bounded_on_demand_execution_runs = 1

market_state_bounded_on_demand_execution_requested_contexts = 9

market_state_bounded_on_demand_execution_materialized_rows = 8

market_state_bounded_on_demand_execution_unavailable_contexts = 1

market_state_bounded_on_demand_execution_hard_validation_failures = 0

market_state_bounded_on_demand_execution_reuse_eligibility = pending_determinism_validation

market_state_bounded_on_demand_candidate_dataset_review = CLOSED_APPROVED_AS_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION

market_state_bounded_on_demand_candidate_dataset_review_id = market_state_bounded_on_demand_candidate_dataset_review_v0_1_20260725T000000Z

market_state_bounded_on_demand_candidate_dataset_review_failures = 0

market_state_bounded_on_demand_candidate_dataset_review_hard_failures = 0

market_state_bounded_on_demand_deterministic_rerun_authorization = CONSUMED_BY_RERUN

market_state_bounded_on_demand_deterministic_rerun_authorization_baseline_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z

market_state_bounded_on_demand_deterministic_rerun_contract_content_sha256_excluding_hash_field = b3bc623ca83885f8773d8bd95f48418e1fa15c6038840d35da7cad860595f231

market_state_bounded_on_demand_deterministic_rerun_execution = CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS

market_state_bounded_on_demand_deterministic_rerun_run = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z

market_state_bounded_on_demand_deterministic_rerun_blocked_attempt = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T052825Z

market_state_bounded_on_demand_deterministic_rerun_attempts = 2

market_state_bounded_on_demand_deterministic_rerun_successful_runs = 1

market_state_bounded_on_demand_deterministic_rerun_blocked_comparison_normalization_attempts = 1

market_state_bounded_on_demand_determinism_comparisons_created = 2

market_state_bounded_on_demand_determinism_successful_comparisons_created = 1

market_state_bounded_on_demand_determinism_status = PROVEN_FOR_BOUNDED_SCOPE

market_state_bounded_on_demand_determinism_blocking_failures = 0

market_state_bounded_on_demand_determinism_runtime_only_differences = 2

market_state_bounded_on_demand_determinism_comparison_fingerprint = ce87938504dbf8fc4e8e962e294aa81f8bc127cdfce69a7aa48157e655329dfb

market_state_bounded_on_demand_determinism_scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7

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

market_state_requests_executed = 1

market_state_reuse_lookup_requests_executed = 1

market_state_datasets_written = 1

event_state_candidate_records_emitted = 8

event_state_bounded_execution_blocked_contexts = 1

event_state_integration_execution = CLOSED_BOUNDED_CHAIN_WITH_RESTRICTIONS

next_allowed_event_state_gate = none_pending; Event State physical execution/materialization requires future explicit authorization after Market State on-demand capability

future_event_registry_v0_2_consideration = event_identity_stability_informative_only

event_state_core_four_intraday_profile_v0_1 = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS

event_state_builder_execution = NOT_AUTHORIZED

tables_000_018_institutional_status_matrix = RECORDED_CURRENT_AUTHORITY_RECONCILIATION_DATA_FOUNDATION_EVIDENCE_RECONCILED

discovery_pass_000_018 = HISTORICAL_DISCOVERY_VALID_NOT_CURRENT_AUTHORITY

tables_000_018_authority_axes = physical_authority + semantic_authority + execution_authority

official_dataset_registry_for_000_018 = NOT_INFERRED_AFTER_DATA_FOUNDATION_RECONCILIATION

tables_000_018_evidence_reconciliation = CLOSED_WITH_FINDINGS_NO_PROMOTION

variable_and_attribute_admission_policy = RECORDED_NO_EXECUTION

variable_attribute_admission_record_template = RECORDED_TEMPLATE_NO_EXECUTION

next_allowed_variable_admission_gate = none_pending; variable-specific admission, schema or consumption gates require explicit authorization

next_allowed_table_status_gate = none_pending; table-specific Data Foundation promotion or consumption gates require explicit authorization

event_state_operational_registry_or_consumption_policy_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

runtime_capabilities_architecture = RECORDED_ARCHITECTURE_NO_EXECUTION

market_state_on_demand_capability_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

consumption_policy_or_operational_registry_design = CLOSED_FOR_EVENT_STATE_PROFILE_REFERENCE_ONLY

```



Tables 000-018 evidence reconciliation run:



```text

run_id = tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z

status = CLOSED_WITH_FINDINGS_NO_PROMOTION

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

next_architectural_gate = event_state_on_demand_bounded_idempotency_reuse_test_v0_1

```





Event State bounded execution-chain accepted run:



```text

event_state_bounded_execution_run = event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z

status = CLOSED_PASS_WITH_RESTRICTIONS_CANDIDATE_OUTPUT

event_instances_created = 3

event_window_bindings_created = 3

instrument_session_projections_created = 9

market_state_exact_bindings_found = 8

event_state_candidate_records_emitted = 8

blocked_contexts = 1

missing_exact_market_state_bindings = 1

fallback_uses = 0

hard_validation_failures = 0

accepted_output = 07_EVENT_STATE_INTEGRATION/runs/event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z/event_state_candidate_records.jsonl

superseded_attempts = event_state_bounded_execution_chain_execution_v0_1_20260724T184946Z, event_state_bounded_execution_chain_execution_v0_1_20260724T185240Z

physical_validation_run = event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z

physical_validation_status = CLOSED_PASS_WITH_RESTRICTIONS

physical_validation_hard_failures = 0

candidate_dataset_review_run = event_state_candidate_dataset_review_v0_1_20260724T194315Z

candidate_dataset_review_status = CLOSED_APPROVED_WITH_RESTRICTIONS_NO_PROMOTION

candidate_dataset_review_hard_failures = 0

profile_promotion_review_run = event_state_profile_promotion_review_v0_1_20260724T201046Z

profile_promotion_review_decision = APPROVED_FOR_EVENT_STATE_PROFILE_PROMOTION_WITH_RESTRICTIONS

profile_promotion_review_hard_failures = 0

superseded_profile_promotion_review_attempt = event_state_profile_promotion_review_v0_1_20260724T200936Z

profile_promotion_run = event_state_profile_promotion_v0_1_20260724T203016Z

profile_promotion_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS

profile_promotion_registry_artifacts_written = 4

profile_promotion_official_dataset = false

profile_promotion_official_parquet_files_written = 0

profile_promotion_downstream_consumption = false

profile_artifact_validation_run = event_state_profile_artifact_validation_v0_1_20260724T204410Z

profile_artifact_validation_status = CLOSED_PASS_WITH_RESTRICTIONS

profile_artifact_validation_registry_artifacts_checked = 4

profile_artifact_validation_hash_mismatches = 0

profile_artifact_validation_invariant_failures = 0

profile_artifact_validation_hard_failures = 0

operational_registry_or_consumption_policy_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

operational_registry_or_consumption_policy_design_profile_reference_allowed = true

operational_registry_or_consumption_policy_design_physical_consumption_allowed = false

runtime_capabilities_architecture = RECORDED_ARCHITECTURE_NO_EXECUTION

runtime_capabilities_request_resolver_implemented = false

runtime_capabilities_materializers_executed = 0

market_state_on_demand_capability_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_on_demand_requests_executed = 1

market_state_on_demand_source_rows_read = 0

market_state_bounded_on_demand_execution_authorization = CONSUMED_BY_RUN

market_state_bounded_on_demand_execution = CLOSED_PASS_WITH_RESTRICTIONS_PARTIAL_CANDIDATE_REGISTERED

market_state_bounded_on_demand_execution_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z

market_state_bounded_on_demand_execution_authorized_scope = XNYS_3_sessions_3_instruments_9_contexts

market_state_bounded_on_demand_execution_runs = 1

market_state_bounded_on_demand_execution_requested_contexts = 9

market_state_bounded_on_demand_execution_materialized_rows = 8

market_state_bounded_on_demand_execution_unavailable_contexts = 1

market_state_bounded_on_demand_execution_hard_validation_failures = 0

market_state_bounded_on_demand_execution_reuse_eligibility = pending_determinism_validation

market_state_bounded_on_demand_candidate_dataset_review = CLOSED_APPROVED_AS_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION

market_state_bounded_on_demand_candidate_dataset_review_id = market_state_bounded_on_demand_candidate_dataset_review_v0_1_20260725T000000Z

market_state_bounded_on_demand_candidate_dataset_review_failures = 0

market_state_bounded_on_demand_candidate_dataset_review_hard_failures = 0

market_state_bounded_on_demand_deterministic_rerun_authorization = CONSUMED_BY_RERUN

market_state_bounded_on_demand_deterministic_rerun_authorization_baseline_run = market_state_bounded_on_demand_execution_v0_1_20260724T232123Z

market_state_bounded_on_demand_deterministic_rerun_contract_content_sha256_excluding_hash_field = b3bc623ca83885f8773d8bd95f48418e1fa15c6038840d35da7cad860595f231

market_state_bounded_on_demand_deterministic_rerun_execution = CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS

market_state_bounded_on_demand_deterministic_rerun_run = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z

market_state_bounded_on_demand_deterministic_rerun_blocked_attempt = market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T052825Z

market_state_bounded_on_demand_deterministic_rerun_attempts = 2

market_state_bounded_on_demand_deterministic_rerun_successful_runs = 1

market_state_bounded_on_demand_deterministic_rerun_blocked_comparison_normalization_attempts = 1

market_state_bounded_on_demand_determinism_comparisons_created = 2

market_state_bounded_on_demand_determinism_successful_comparisons_created = 1

market_state_bounded_on_demand_determinism_status = PROVEN_FOR_BOUNDED_SCOPE

market_state_bounded_on_demand_determinism_blocking_failures = 0

market_state_bounded_on_demand_determinism_runtime_only_differences = 2

market_state_bounded_on_demand_determinism_comparison_fingerprint = ce87938504dbf8fc4e8e962e294aa81f8bc127cdfce69a7aa48157e655329dfb

market_state_bounded_on_demand_determinism_scientific_dataset_fingerprint = a9182b19e434ea77ca2bf5b3395b84a4592560bbf28e5cb0d80ee5561c5fe1b7

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

next_gate = event_state_on_demand_bounded_incremental_overlap_execution_v0_1

```



## Variable And Attribute Admission Policy



```text

02_VARIABLE_AND_ATTRIBUTE_ADMISSION_POLICY_v0_1.md

03_VARIABLE_ATTRIBUTE_ADMISSION_RECORD_TEMPLATE_v0_1.md

```



The template records who can propose variables like ATR/RVOL/VWAP and when a proposal is legitimate.



This policy package consolidates the already distributed policy for why a raw source

attribute, derived feature, state variable, event variable, outcome label or

quality/lineage/governance attribute may be discovered, mapped, admitted,

blocked or rejected.



Boundary:



```text

new_variables_admitted = 0

physical_schema_changes_authorized = false

builder_execution_authorized = false

materialization_authorized = false

dataset_promotion_authorized = false

downstream_consumption_authorized = false

```



Authority rule:



```text

Research/ML/AlphaEvolve may propose evidence.

Applied Architecture governs semantic admission.

Data Foundation governs physical source authority.

Execution gates authorize use.

Builders execute; they do not choose variables.

```



Run vigente de cierre Scale C sample preflight:



```text

experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z

scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d

requested_contexts = 120

selected_instruments = 10

selected_sessions = 8

expected_resolution_records_if_later_executed = 480

hard_preflight_failures = 0

```



Run vigente de cierre Scale C execution surface construction:



```text

experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z

scale_c_execution_surface_fingerprint = 34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554

surface_rows_written = 13969

source_013_rows_read = 360409

candidate_surface_parquet_files_written = 1

calendar_binding_failures = 0

session_boundary_mismatches = 0

early_close_boundary_failures = 0

fixed_utc_probe_calendar_as_current_authority = 0

builder_records_emitted = 0

market_state_records_emitted = 0

hard_validation_failures = 0

```



Intentos Scale C no vigentes:



```text

experimental_core_four_market_state_scale_c_sample_preflight_v0_1_20260723T152658Z = SUPERSEDED_BLOCKED_INSTRUMENT_HISTORY_COVERAGE

experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T163051Z = SUPERSEDED_SOURCE_ROW_CAP_ATTEMPT

experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T163701Z = SUPERSEDED_FAILED_FILTER_ATTEMPT

```



Siguiente gate permitido:



```text

official_market_state_candidate_promotion_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

official_market_state_candidate_promotion_review = APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS

official_market_state_candidate_promotion_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

official_market_state_candidate_promotion = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS

official_market_state_profile_artifact_validation = CLOSED_PASS_WITH_RESTRICTIONS

event_state_operational_registry_or_consumption_policy_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

consumption_policy_or_operational_registry_design = CLOSED_FOR_EVENT_STATE_PROFILE_REFERENCE_ONLY

event_state_architecture_design = RECORDED_AS_SEED_NO_EXECUTION

event_state_profile_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

event_type_registry_seed_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

event_type_registry_initial_population_authorization = CONSUMED_WITH_RESTRICTIONS

event_type_initial_admission_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_type_initial_admission_review = CLOSED_WITH_MIXED_DECISIONS_NO_EXECUTION

event_window_binding_design_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION_SESSION_OPENED_EXCHANGE_SESSION_ONLY

event_window_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

market_state_profile_compatibility_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION

event_instance_binding_execution = NOT_AUTHORIZED

event_window_binding_execution = NOT_AUTHORIZED

```



## Tables 000-018 Institutional Status Matrix



```text

04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md

```



This is the current applied-architecture table-level status matrix for `000-018`.

It records known authority, unresolved evidence and closed boundaries without

promoting any dataset.



The historical first discovery pass remains:



```text

02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md

```



Reading rule:



```text

Discovery Pass = historical discovery evidence.

Institutional Status Matrix = current reconciliation surface.

```



The matrix explicitly preserves:



```text

official_dataset_registry_write_allowed = false

official_parquet_write_allowed = false

production_builder_allowed = false

downstream_consumption_allowed = false

event_type_registry_initial_population_open_authorization_allowed = false

event_type_admission_execution_allowed = false

event_detection_execution_allowed = false

event_state_materialization_allowed = false

```



Next table-status work requires a separate reconciliation gate against Data

Foundation contracts, schemas, registries, manifests, validators and consumption

policies.



## Experimental Core Four Market State Scale C Chain Closure



```text

experimental_core_four_market_state_scale_c_builder_resolution_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_builder_resolution_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_market_state_integration_execution_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_candidate_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_candidate_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_candidate_physical_validation_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

experimental_core_four_market_state_scale_c_candidate_physical_validation = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_scale_c_execution = SCALE_C_CLOSED_PASS_WITH_RESTRICTIONS_OFFICIAL_NOT_AUTHORIZED

```



Accepted Scale C runs:



```text

sample_preflight_run = experimental_core_four_market_state_scale_c_sample_preflight_v0_2_20260723T164132Z

execution_surface_run = experimental_core_four_market_state_scale_c_execution_surface_construction_v0_1_20260723T165402Z

builder_resolution_run = experimental_core_four_market_state_scale_c_builder_resolution_execution_v0_1_20260723T184203Z

market_state_integration_run = experimental_core_four_market_state_scale_c_market_state_integration_execution_v0_1_20260723T184533Z

candidate_materialization_run = experimental_scale_c_ms_candidate_materialization_v0_1_20260723T184752Z

candidate_physical_validation_run = core_four_market_state_scale_c_candidate_physical_validation_v0_1_20260723T184900Z

```



Closure evidence:



```text

sample_contexts = 120

resolution_records = 480

integrable_contexts = 104

blocked_contexts = 16

candidate_jsonl_records = 104

candidate_physical_rows = 104

candidate_parquet_files = 1

candidate_parquet_sha256 = b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2

scale_c_sample_fingerprint = 67d46f6b5f2567b3af82d000bb2a6cb6e05f0546f0be11b1c263586c3bc9515d

scale_c_execution_surface_fingerprint = 34db7887874a57658bbbec52cc9b3915f86afdc61b7997e6b930056c0a9cf554

source_013_rows_read_during_builder_integration_materialization_validation = 0

source_market_data_rows_read_during_integration_materialization_validation = 0

value_mappings_checked = 1768

semantic_rebuild_field_comparisons = 3848

hard_validation_failures = 0

```



Scale C closes the bounded multi-period, governed-calendar, non-production Market State demonstration. It does not open official Market State, production builders, downstream consumption, dataset promotion, full-history execution or full-universe execution.



## Official Market State Candidate Promotion Review



```text

official_market_state_candidate_promotion_review_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

official_market_state_candidate_promotion_review = APPROVED_FOR_OFFICIAL_PROFILE_PROMOTION_WITH_RESTRICTIONS

reviewed_profile_id = market_state_core_four_intraday_profile_v0_1

accepted_review_run = official_market_state_candidate_promotion_review_v0_1_20260723T192107Z

evidence_artifacts_checked = 8

resolution_records = 480

integrated_candidate_records = 104

physical_candidate_rows = 104

value_mappings_checked = 1768

semantic_rebuild_field_comparisons = 3848

hash_mismatches = 0

count_mismatches = 0

hard_validation_failures = 0

official_profile_promotion_executed = false

official_market_state_authorized = false

official_parquet_files_written = 0

source_market_data_rows_read = 0

next_allowed_gate = official_market_state_candidate_promotion_authorization_v0_1

```



This review approved a bounded profile-promotion authorization that was later consumed by the validated promotion run recorded below. It is not complete TSIS Market State and did not authorize official parquet, production, downstream consumption, full-history execution or full-universe execution.



## Official Core-Four Profile Promotion And Artifact Validation



```text

official_market_state_candidate_promotion_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

official_market_state_candidate_promotion = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS

official_market_state_profile_artifact_validation_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED

official_market_state_profile_artifact_validation = CLOSED_PASS_WITH_RESTRICTIONS

promoted_profile_id = market_state_core_four_intraday_profile_v0_1

promotion_run = official_market_state_candidate_promotion_v0_1_20260723T193403Z

profile_artifact_validation_run = official_market_state_profile_artifact_validation_v0_1_20260723T193711Z

registry_artifacts_written = 4

registry_artifacts_checked = 4

registry_sha256_mismatches = 0

registry_invariant_failures = 0

hard_validation_failures = 0

official_market_state_authorized = false

official_dataset_registry_write_authorized = false

official_parquet_files_written = 0

candidate_parquet_copied = false

source_market_data_rows_read = 0

next_allowed_gate = consumption_policy_or_operational_registry_design_only_after_explicit_authorization

```



The profile registry package lives at `06_MARKET_STATE_INTEGRATION/official_profiles/market_state_core_four_intraday_profile_v0_1`. It is the applied-architecture official profile contract only; production, downstream consumption, operational dataset registry updates, complete TSIS Market State and full-history/full-universe execution remain closed.







## Market State Profiles Family And Event State Seed



```text

tsis_market_state_profiles_family_architecture = RECORDED_NO_EXECUTION

event_state_architecture_from_market_state_profiles = RECORDED_NO_EXECUTION

current_official_profile = market_state_core_four_intraday_profile_v0_1

official_dataset_registry_updated = false

official_market_state_authorized = false

event_state_builder_execution = NOT_AUTHORIZED

downstream_consumption_authorized = false

```



New continuity artifacts:



```text

06_MARKET_STATE_INTEGRATION/tsis_market_state_profiles_family_architecture_v0_1.md

06_MARKET_STATE_INTEGRATION/event_state_architecture_from_market_state_profiles_v0_1.md

```



The first document establishes Market State as a governed family of profiles.

The second records that future Event State design should reference a valid

Market State profile, currently `market_state_core_four_intraday_profile_v0_1`,

without rebuilding Market State or consuming physical artifacts without a

separate policy/registry gate.



## Event State Profile Contract Design



```text

event_state_profile_contract_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

event_state_profile_id = event_state_core_four_intraday_profile_v0_1

source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1

source_market_state_profile_status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS

event_state_builder_execution = NOT_AUTHORIZED

event_state_materialization = NOT_AUTHORIZED

downstream_consumption = NOT_AUTHORIZED

```



Artifacts:



```text

06_MARKET_STATE_INTEGRATION/event_state_profile_contract_design_v0_1.md

06_MARKET_STATE_INTEGRATION/event_state_profile_contract_design_contract_v0_1.json

07_EVENT_STATE_INTEGRATION/event_state_event_policy_v0_1.md



07_EVENT_STATE_INTEGRATION/event_type_or_event_family_contract_design_v0_1.md

07_EVENT_STATE_INTEGRATION/event_type_or_event_family_contract_design_contract_v0_1.json

07_EVENT_STATE_INTEGRATION/event_type_registry_seed_design_v0_1.md

07_EVENT_STATE_INTEGRATION/event_type_registry_seed_design_contract_v0_1.json

07_EVENT_STATE_INTEGRATION/event_type_registry_initial_population_authorization_v0_1.md

07_EVENT_STATE_INTEGRATION/configs/event_type_registry_initial_population_scope_v0_1.json

07_EVENT_STATE_INTEGRATION/event_type_registry_initial_population_snapshot_v0_1.json

07_EVENT_STATE_INTEGRATION/event_type_registry_initial_population_readout_v0_1.md

```



This design fixes the first Event State profile contract and requires later

bindings for event instance, event window, Market State compatibility, join

semantics, object atomicity and lineage. It does not authorize event detection,

Event State builder execution, integration, materialization, parquet, production

or downstream consumption.



Run vigente de cierre Scale B surface:



```text

experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z

```



Referencia historica Scale A inicial no vigente:



```text

experimental_core_four_market_state_scale_a_sample_preflight_v0_1_20260722T123859Z

```



El preflight comprobo 5 sesiones compatibles con el guard fijo UTC, pero no congelo la muestra de 60 contextos porque la superficie 014 autorizada contiene solo 3 tickers intradia y solo 1 instrumento elegible bajo el guard de calendario. No ejecutar builders, integracion, materializacion ni validacion fisica Scale A hasta ajustar la fuente autorizada o el scope y rerun del preflight.



Se ejecuto `experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194905Z` y el rerun del preflight Scale A cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 60 contextos congelados, 8 instrumentos, 5 sesiones, 240 resolution records esperados, 52 contextos integrables esperados, 8 bloqueados esperados, 0 fallos de calendario/identidad/cobertura/estratificacion y sample fingerprint `65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1`. El intento `experimental_core_four_market_state_scale_a_sample_preflight_rerun_v0_1_20260722T194131Z` no es evidencia de cierre porque expuso un bug de estratificacion de duplicados. El siguiente gate permitido es `experimental_core_four_market_state_scale_a_execution_authorization_v0_1`; no ejecutar builders, integrar ni materializar Market State hasta que exista esa autorizacion y nombre el fingerprint exacto.



Se emitio `experimental_core_four_market_state_scale_a_execution_authorization_v0_1` y `configs/experimental_core_four_market_state_scale_a_execution_scope_v0_1.json`. Scale A execution queda `AUTHORIZED_WITH_RESTRICTIONS` contra el sample fingerprint `65a05b1c0637a7473380e9a04705a6c5879a921a0196dbad0a1815a19e8edea1`.



Se ejecuto `experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202557Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 60 contextos, 240 Information Object resolution records, 208 PASS/PASS_WITH_RESTRICTIONS, 32 BLOCKED_INPUT_UNAVAILABLE, 52 contextos integrables, 8 bloqueados esperados, 0 leaks futuros, 0 fallos de formula/contrato/determinismo y 5761 source rows read bajo el limite. Los intentos `20260722T202216Z`, `20260722T202243Z` y `20260722T202407Z` no son evidencia de cierre; quedaron superseded por issues de wrapper/reporte de frontera de lectura.



Se ejecuto `experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 240 resolution records consumidos, 60 contextos vistos, 52 Market State candidate records emitidos, 8 contextos bloqueados esperados rechazados, 884 value rows admitidas, 0 source market-data rows read, 0 blocked values admitted y 0 hard validation failures. Los intentos `20260722T203507Z`, `20260722T203635Z` y `20260722T204045Z` no son evidencia de cierre para la cadena Scale A; quedaron superseded por el run que emite `integration_summary.json` compatible con materializacion.



Se ejecuto `experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 52 input candidate records, 52 filas fisicas candidatas, 1 parquet candidato no oficial, 40 columnas fisicas, 17 columnas de valores, 0 source market-data rows read, 0 rejected contexts materialized, 0 hard validation failures, 0 roundtrip failures y 0 semantic rebuild differences. El siguiente subgate ejecutable es `experimental_core_four_market_state_scale_a_candidate_physical_validation`; debe validar independientemente el parquet real. No re-seleccionar muestra, leer `013`, integrar objetos quote-dependent, promover datasets, usar produccion ni autorizar downstream.



Se ejecuto `experimental_core_four_market_state_scale_a_candidate_physical_validation_v0_1_20260722T204600Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 52 input candidate records, 52 physical rows, 884 source-to-physical value mappings checked, 52 RVOL rename checks, 52 state_output_fingerprint matches, 52 materialized_state_candidate_id matches, 1924 semantic rebuild field comparisons, 0 authority failures y 0 hard validation failures. Scale A queda cerrado con restricciones hasta validacion fisica independiente.



Se cerro `governed_exchange_session_calendar_design_v0_1` como `CLOSED_DESIGN_READY_WITH_RESTRICTIONS`: define el objeto `governed_exchange_session_calendar`, la frontera de binding, el candidato fuente `001_market_calendar / market_calendar_v0_1`, los campos logicos requeridos, la politica de dias cerrados y los criterios de aceptacion calendar-aware para Scale B.



Se emitio `governed_exchange_session_calendar_binding_authorization_v0_1` con `configs/governed_exchange_session_calendar_binding_scope_v0_1.json` como `AUTHORIZED_WITH_RESTRICTIONS`. Autoriza solo una futura validacion acotada contra `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\data\reference\market_calendar_official_XNYS_20050101_20260309.parquet` y su meta, con hash esperado `5e423e444e1228a671a05159eda0a707f9bb2446f5b17860740f3001edbbd954`. La ruta procesada documentada `E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet` no esta disponible y debe reportarse como ausencia en la validacion. No autoriza Scale B execution, builders, integracion, materializacion, produccion, consumo downstream, full-history/full-universe ni promocion.



Se ejecuto `governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 5328 source rows, 5328 bound calendar rows, 45 early-close sessions, SHA-256 fuente verificado, fingerprint snapshot `8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967`, 0 duplicados de session_date, 0 fallos de equivalencia UTC/local, 0 mismatches de duracion, 0 mismatches de early close, 0 fallos de row fingerprint, 0 diferencias roundtrip, 0 fallos de determinismo y 0 hard validation failures. El run `governed_exchange_session_calendar_binding_validation_v0_1_20260723T061003Z` queda superseded por aclaracion del limite de bytes de output, no por defecto del calendario. El siguiente gate permitido era `experimental_core_four_market_state_scale_b_authorization_v0_1`; ya fue emitido.



Se emitio `experimental_core_four_market_state_scale_b_authorization_v0_1` con `configs/experimental_core_four_market_state_scale_b_scope_v0_1.json` como `AUTHORIZED_WITH_RESTRICTIONS`. Autoriza solo `experimental_core_four_market_state_scale_b_sample_preflight_v0_1`: 6 sesiones gobernadas XNYS, 8 instrumentos, 72 contextos objetivo, 288 resolution records si posteriormente se ejecuta, 8 contextos bloqueados esperados y 64 contextos integrables esperados. No autoriza Scale B execution, builders, resolution records, Market State integration, Market State materialization, Market State parquet, construccion run-local de 014, uso directo de 013 como builder input, produccion, consumo downstream, full-history/full-universe ni promocion.



Se ejecuto `experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 72 contextos congelados, 8 instrumentos seleccionados desde 13 del pool elegible, 6 sesiones gobernadas XNYS, 288 resolution records esperados si posteriormente se ejecuta, 8 contextos bloqueados esperados, 64 contextos integrables esperados, 0 mismatches de frontera de calendario, 0 uso del fixed UTC probe calendar como autoridad actual, 0 fallos de cobertura/identidad/estratificacion, 0 duplicados de contexto y sample fingerprint `5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972`. El intento `experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T073906Z` queda superseded porque se inicio antes de estar disponible `G:\`; no congelo muestra ni es evidencia de cierre. El siguiente gate permitido fue `experimental_core_four_market_state_scale_b_execution_authorization_v0_1`; esa autorizacion ya fue emitida en el bloque siguiente y el preflight no debe repetirse.



Se emitio `experimental_core_four_market_state_scale_b_execution_authorization_v0_1` con `configs/experimental_core_four_market_state_scale_b_execution_scope_v0_1.json` como `AUTHORIZED_WITH_RESTRICTIONS`. Autoriza una cadena no productiva contra el sample fingerprint `5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972`: construccion run-local de superficie 014 Scale B, builder/resolution, integration, candidate materialization e independent physical validation. El primer subgate ejecutable es `experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1`. `013` queda permitido solo para construir esa superficie 014 run-local; sigue prohibido como input directo de builders, Market State, materializacion o downstream. Produccion, Market State oficial, consumo downstream, promocion, full-history/full-universe y Scale C siguen cerrados.



Se ejecuto `experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 8112 filas en `014_scale_b_execution_surface_candidate_v0_1.parquet`, 32 ficheros 013 acotados leidos, 149237 filas 013 leidas bajo el limite 250000, sample fingerprint `5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972`, surface fingerprint `dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa`, 0 fallos de calendario/frontera early-close/cutoff/cobertura/autoridad/determinismo, 0 builder records, 0 Information Object formulas, 0 Market State records y 0 Market State parquet. Los intentos `20260723T105511Z`, `20260723T110307Z` y `20260723T110716Z` quedan superseded por issues de ruta larga/output contract, no por defecto de datos. El siguiente gate permitido fue `experimental_core_four_market_state_scale_b_builder_resolution_execution_authorization_v0_1`; esa autorizacion ya fue emitida en el bloque siguiente.



Se emitio `experimental_core_four_market_state_scale_b_builder_resolution_execution_authorization_v0_1` con `configs/experimental_core_four_market_state_scale_b_builder_resolution_execution_scope_v0_1.json` como `AUTHORIZED_WITH_RESTRICTIONS`. Esa autorizacion fue consumida por `experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1_20260723T142329Z`, que cerro `CLOSED_PASS_WITH_RESTRICTIONS` contra 72 contextos congelados, 4 objetos core-four por contexto, 288 resolution records, sample fingerprint `5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972` y surface fingerprint `dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa`. El run leyo la superficie 014 run-local aceptada y `004_master_daily_table`; `013` siguio prohibido como input directo, la reconstruccion de superficie siguio prohibida, fixed UTC fallback fue 0 y Market State integration/materialization/parquet/produccion/downstream/promocion seguian cerrados en ese gate.



Se emitio `experimental_core_four_market_state_scale_b_market_state_integration_execution_authorization_v0_1` con `configs/experimental_core_four_market_state_scale_b_market_state_integration_execution_scope_v0_1.json` como `AUTHORIZED_WITH_RESTRICTIONS`. Esa autorizacion fue consumida por `experimental_core_four_market_state_scale_b_market_state_integration_execution_v0_1_20260723T144323Z`, que cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 288 resolution records consumidos, 72 contextos vistos, 64 Market State candidate JSONL records emitidos, 8 contextos bloqueados esperados rechazados, 1088 value rows admitidas, 0 blocked values admitted, 0 source market-data rows read, 0 parquet files written, 0 fixed UTC fallback uses y 0 hard validation failures. El intento `experimental_core_four_market_state_scale_b_market_state_integration_execution_v0_1_20260723T144247Z` queda superseded por limite de ruta larga de Windows en nombres de output antes de escribir summary/final_manifest, no por defecto de datos o contrato. El siguiente gate correcto es `experimental_core_four_market_state_scale_b_candidate_materialization_authorization_v0_1`; materializacion, Market State oficial, produccion, downstream, promocion y full-history/full-universe seguian cerrados en ese gate.



Se ejecuto `experimental_core_four_market_state_scale_b_candidate_materialization_execution` con run `experimental_scale_b_ms_candidate_materialization_v0_1_20260723T144955Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 64 input candidate records, 64 filas fisicas candidatas, 1 parquet candidato no oficial, 40 columnas fisicas, 17 columnas de valores, 0 source market-data rows read, 0 rejected contexts materialized, 0 hard validation failures, 0 roundtrip failures y 0 semantic rebuild differences. Luego se ejecuto validacion fisica independiente `core_four_market_state_candidate_physical_validation_v0_1_20260723T145049Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 64 input candidate records, 64 physical rows, 1088 source-to-physical value mappings checked, 64 RVOL rename checks, 64 state_output_fingerprint matches, 64 materialized_state_candidate_id matches, 2368 semantic rebuild field comparisons, 0 authority failures y 0 hard validation failures. Scale B queda cerrado como demostracion calendar-aware acotada y no productiva. Se emitio `experimental_core_four_market_state_scale_c_authorization_v0_1` con `configs/experimental_core_four_market_state_scale_c_scope_v0_1.json` como `AUTHORIZED_WITH_RESTRICTIONS`. Autoriza solo `experimental_core_four_market_state_scale_c_sample_preflight_v0_1`: una muestra historica acotada 2021-2025, 8 sesiones gobernadas XNYS, objetivo de 120 contextos, 480 resolution records si posteriormente se ejecuta, 16 contextos bloqueados esperados y 104 contextos integrables objetivo. No autoriza Scale C execution, construccion run-local de 014, builders, integration, materializacion, parquet, produccion, downstream, promocion ni full-history/full-universe. Market State oficial, produccion, downstream, promocion y full-history/full-universe siguen cerrados.



## 1. Prompt De Arranque Para El Agente



```text

Estas continuando despues del freeze de TSIS Market Ontology v1 dentro de:



C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering



Tu objetivo no es crear mas metodologia.

Tu objetivo no es admitir nuevos Information Objects en v1.

Tu objetivo no es reabrir la ciencia congelada salvo contradiccion real.

Tu objetivo no es desarrollar builders de produccion.

Tu objetivo no es autorizar consumo operativo de State.



Tu objetivo actual es continuar Phase B como ingenieria gobernada,

trabajando en el builder experimental no productivo.



Los gates de builder experimental core-four, acceptance review, integration

design, integration execution, materialization design, materialization

authorization y materialization execution ya quedaron cerrados o emitidos con

restricciones.



El siguiente gate posible ya no es Scale B operativo: Scale B quedo cerrado con restricciones por `core_four_market_state_candidate_physical_validation_v0_1_20260723T145049Z`. Scale C ya cerro con restricciones hasta validacion fisica independiente; el proximo trabajo no es ejecucion automatica, sino autorizacion explicita de review/promocion de candidato oficial o plan de escala posterior.



Resumen vigente: Scale B consumio 72 contextos calendar-aware, construyo superficie 014 run-local, emitio 288 resolution records, integro 64 Market State candidate JSONL records, materializo 64 filas candidatas y valido fisicamente el parquet candidato con 0 hard validation failures. Scale C queda cerrado con muestra historica acotada, superficie 014 run-local, builder/resolution, integration, materializacion candidata y validacion fisica independiente. Market State oficial, produccion, consumo downstream, promocion y full-history/full-universe execution siguen cerrados.



Trabaja como agente de ingenieria ontologica:



1. lee los contratos indicados abajo;

2. trata `TSIS Market Ontology v1` como dependencia frozen/locked;

3. usa las Formal Admissions y el Freeze Act como autoridad;

4. usa los Operational Mappings admitidos como autoridad de ingenieria;

5. conserva production builders, State consumption, schema changes,

   official physical materialization y dataset promotion como false hasta gates

   explicitos de Phase B;

6. actualiza changelogs cuando el cambio sea semantico,

   estructural o de gobernanza;

7. no toques metodologia ni reabras Phase A salvo contradiccion

   estructural demostrada.

```



## 2. Lectura Obligatoria Antes De Tocar Nada



Leer en este orden:



```text

1. C:\TSIS_Data\AGENTS.md

2. C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md

3. C:\TSIS_Data\PROJECT_RULES.md

4. C:\TSIS_Data\VERSIONING_STANDARDS.md

5. C:\TSIS_Data\RESEARCH_PHILOSOPHY.md

6. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\AGENTS.md

7. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\LOCAL_RULES.md

8. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\README.md

9. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\CHANGELOG.md

10. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md

11. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\CHANGELOG.md

12. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_TABLES_MARKET_STATE_EVENT_STATE.md

13. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md

14. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\README.md

15. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\04_TSIS_MARKET_ONTOLOGY_PHASE_v0_1.md

16. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_REVIEW.md

17. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md

18. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\README.md

19. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\README.md

20. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\README.md

21. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_bounded_sample_validation_authorization_v0_1.md

22. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\configs\experimental_bounded_sample_scope_v0_1.json

23. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_state_builder_probe_bounded_identity_temporal_readout_v0_1.md

24. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_bounded_grain_validation_authorization_v0_1.md

25. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\configs\experimental_bounded_grain_scope_v0_1.json

26. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_state_builder_probe_bounded_grain_readout_v0_1.md

27. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_bounded_quality_lineage_validation_authorization_v0_1.md

28. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\configs\experimental_bounded_quality_lineage_scope_v0_1.json

29. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\policies\004_price_view_selection_policy_v0_1.md

30. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\policies\014_duplicate_intraday_bar_policy_v0_1.md

31. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\policies\raw_quote_ordering_policy_v0_1.md

32. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\policies\raw_quote_quality_policy_v0_1.md

33. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_state_builder_probe_bounded_quality_lineage_readout_v0_1.md

34. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\runs\experimental_state_builder_probe_v0_9_20260721T184537Z\final_manifest.json

35. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\runs\experimental_state_builder_probe_v0_10_20260721T193918Z\final_manifest.json

36. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_state_builder_probe_core_four_builder_validation_readout_v0_1.md

37. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_core_four_resolution_record_acceptance_review_v0_1.md

38. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_core_four_resolution_record_acceptance_summary_v0_1.json

39. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION\experimental_state_builder_probe\experimental_core_four_resolution_record_acceptance_context_report_v0_1.csv

40. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\README.md

41. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\core_four_market_state_integration_design_v0_1.md

42. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\core_four_market_state_integration_design_contract_v0_1.json

43. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\experimental_core_four_market_state_integration_execution_authorization_v0_1.md

44. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\configs\core_four_market_state_integration_execution_scope_v0_1.json

45. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\experimental_core_four_market_state_integration_execution_readout_v0_1.md

46. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z\final_manifest.json

47. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\core_four_market_state_materialization_design_v0_1.md

48. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\core_four_market_state_materialization_design_contract_v0_1.json

49. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\experimental_core_four_market_state_materialization_authorization_v0_1.md

50. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\configs\experimental_core_four_market_state_materialization_scope_v0_1.json

51. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\scripts\core_four_market_state_materialization_probe.py

52. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\experimental_core_four_market_state_materialization_execution_readout_v0_1.md

53. C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\06_MARKET_STATE_INTEGRATION\runs\experimental_core_four_market_state_materialization_v0_1_20260722T081155Z\final_manifest.json

```



Nota:



```text

C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\LOCAL_RULES.md

```



no existe a fecha `2026-07-21`. No lo inventes. Usa las reglas superiores y

este handoff local.



## 3. Lectura Obligatoria Para Operational Mapping De Un Objeto



Para cada Information Object admitido, leer en este orden:



```text

1. DOMAIN_DEFINITIONS\<object>_domain_definition_v0_1.md

2. DOMAIN_DEFINITIONS\<object>_representation_landscape_v0_1.md

3. CANDIDATES\<object>_candidate_object_definition_v0_1.md

4. CANDIDATES\object_admission_review\<object>_v0_1.md

5. ACCEPTED_WITH_RESTRICTIONS\<object>_formal_admission_v0_1.md

6. TSIS_MARKET_ONTOLOGY_V1_REVIEW.md

7. TSIS_MARKET_ONTOLOGY_V1_FREEZE.md

8. 04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\README.md

9. 04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\trading_activity_operational_mapping_v0_1.md

```



El punto 9 es piloto de proceso y estilo, no autoridad operativa automatica.

El Freeze Act manda sobre cualquier texto pre-freeze que conserve un estado

de fase anterior.

## 4. Punto Exacto Del Proyecto



```text

ontology = TSIS Market Ontology v1

ontology_status = FROZEN

ontology_lock_status = LOCKED

phase_a_status = CLOSED

phase_b_status = OPEN

phase_b_scope = governed_engineering

production_builder_development_authorized = false

state_consumption_authorized = false

official_physical_materialization_authorized = false

bounded_experimental_candidate_materialization = CLOSED_PASS_WITH_RESTRICTIONS

```



El vertical de `Trading Activity` ya demostro el lifecycle completo:



```text

Formal Admission

    -> Operational Mapping

        -> Builder Validation

            -> Market State Integration

```



pero queda clasificado como:



```text

pilot_vertical_artifact

proof_of_process

not_operational_authority

```



El trabajo activo ahora es Phase B:



```text

Operational Mapping

    -> Builder Validation

        -> Market State Integration

            -> Event State Integration

                -> Operational Promotion

```



La unidad activa de trabajo ya no es Operational Mapping. Ese bloque esta

completo para v1.



La unidad activa vigente es:



```text

core_four_market_state_candidate_physical_validation

```



Debe revisar la evidencia generada por `experimental_core_four_market_state_materialization_v0_1_20260722T081155Z`: 8 candidate rows, un parquet

candidato no oficial, schema cerrado, JSON canonico, 0 source market-data

reread, 0 fallos duros, roundtrip limpio y determinismo semantico sobre 37

campos. No autoriza produccion, consumo downstream, promocion ni

full-history/full-universe execution.



Estado previo cerrado:



```text

bounded_identity_and_temporal_validation = CLOSED_PASS_WITH_RESTRICTIONS

bounded_grain_validation = CLOSED_PASS_WITH_RESTRICTIONS

```



## 5. Estado Real De Admissions



Object Admission Reviews completos:



```text

broad_market_context_v0_1.md

fundamental_context_v0_1.md

halt_context_v0_1.md

liquidity_v0_1.md

market_microstructure_state_v0_1.md

news_catalyst_context_v0_1.md

order_flow_pressure_v0_1.md

price_location_structure_v0_1.md

price_movement_v0_1.md

short_side_context_v0_1.md

trading_activity_v0_1.md

volatility_range_state_v0_1.md

```



Formal Admissions ya creadas:



```text

Trading Activity = accepted_with_restrictions

Price Movement = accepted_with_restrictions

Price Location / Structure = accepted_with_restrictions

Volatility / Range State = accepted_with_restrictions

Liquidity = accepted_with_restrictions

Market Microstructure State = accepted_with_restrictions

Order Flow Pressure = accepted_with_restrictions

News / Catalyst Context = accepted_with_restrictions

Fundamental Context = accepted_with_restrictions

Short-Side Context = accepted_with_restrictions

Broad Market Context = accepted_with_restrictions

Halt Context = accepted_with_restrictions

```



Formal Admissions pendientes:



```text

none

```



`Event Window Context` queda fuera de la cola ordinaria:



```text

classification = infrastructure_context

formal_object_admission = not_applicable

state_variables_authorized = false

```



## 6. Estado De Freeze Y Siguiente Trabajo



La cola de Formal Admission ya esta completa.



La Cross-Object Ontology Review ya esta creada:



```text

C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_REVIEW.md

review_result = passes_with_restrictions

freeze_recommendation = proceed_to_freeze_artifact

```



La TSIS Market Ontology v1 ya esta congelada:



```text

C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md

ontology_status = FROZEN

ontology_lock_status = LOCKED

phase_a_status = CLOSED

phase_b_status = OPEN

```



El siguiente paso es Phase B:



```text

1. Operational Mapping

2. Builder Validation

3. Market State Integration

4. Event State Integration

5. Operational Promotion

```



Ningun nuevo Information Object entra en v1 salvo evidencia extraordinaria,

contradiccion estructural demostrada o decision explicita de gobierno para

abrir v1.1/v2.

## 6.1 Estado De Operational Mapping



Operational Mappings de `TSIS Market Ontology v1`:



```text

status = complete_for_v1

objects_with_governed_mapping = 12

production_builder_authorized = false

state_consumption_authorized = false

```



Inventario:



```text

Trading Activity:

    artifact = trading_activity_operational_mapping_v0_1.md

    ratification = trading_activity_operational_mapping_phase_b_ratification_v0_1.md

    status = mapping_ready_pending_builder_validation



Price Movement:

    artifact = price_movement_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Price Location / Structure:

    artifact = price_location_structure_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Volatility / Range State:

    artifact = volatility_range_state_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Liquidity:

    artifact = liquidity_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Market Microstructure State:

    artifact = market_microstructure_state_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Order Flow Pressure:

    artifact = order_flow_pressure_operational_mapping_v0_1.md

    status = mapping_documented_but_state_blocked

    unblock_requires = trade_quote_alignment + side_classifier + confidence_policy



News / Catalyst Context:

    artifact = news_catalyst_context_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Fundamental Context:

    artifact = fundamental_context_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Short-Side Context:

    artifact = short_side_context_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Broad Market Context:

    artifact = broad_market_context_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation



Halt Context:

    artifact = halt_context_operational_mapping_v0_1.md

    status = mapping_ready_pending_builder_validation

```



Builder Validation designs quedan completos para los 12 Objetos de v1.



Siguiente gate recomendado:



```text

core_four_market_state_candidate_physical_validation

```



No empezar promocion, escalado historico, consumo State ni Market State oficial

hasta que se revise formalmente la evidencia fisica candidata.



## 6.2 Estado De Builder Validation



Builder Validation design coverage de `TSIS Market Ontology v1`:



```text

status = complete_for_v1_design

objects_with_builder_validation_design = 12

objects_design_ready_pending_execution = 11

objects_blocked_pending_prerequisites = 1

production_builder_authorized = false

state_consumption_authorized = false

physical_materialization_authorized = false

```



Inventario:



```text

Trading Activity:

    artifact = 05_STATE_BUILDER_VALIDATION/trading_activity_builder_validation_v0_1.md

    ratification = 05_STATE_BUILDER_VALIDATION/trading_activity_builder_validation_phase_b_ratification_v0_1.md

    status = design_ready_pending_execution



Price Movement:

    artifact = 05_STATE_BUILDER_VALIDATION/price_movement_builder_validation_v0_1.md

    status = design_ready_pending_execution



Price Location / Structure:

    artifact = 05_STATE_BUILDER_VALIDATION/price_location_structure_builder_validation_v0_1.md

    status = design_ready_pending_execution



Volatility / Range State:

    artifact = 05_STATE_BUILDER_VALIDATION/volatility_range_state_builder_validation_v0_1.md

    status = design_ready_pending_execution



Liquidity:

    artifact = 05_STATE_BUILDER_VALIDATION/liquidity_builder_validation_v0_1.md

    status = design_ready_pending_execution



Market Microstructure State:

    artifact = 05_STATE_BUILDER_VALIDATION/market_microstructure_state_builder_validation_v0_1.md

    status = design_ready_pending_execution



Order Flow Pressure:

    artifact = 05_STATE_BUILDER_VALIDATION/order_flow_pressure_builder_validation_v0_1.md

    status = blocked_pending_state_capability_prerequisites

    unblock_requires = trade_quote_alignment_policy + side_classifier_policy + classifier_confidence_policy



News / Catalyst Context:

    artifact = 05_STATE_BUILDER_VALIDATION/news_catalyst_context_builder_validation_v0_1.md

    status = design_ready_pending_execution



Fundamental Context:

    artifact = 05_STATE_BUILDER_VALIDATION/fundamental_context_builder_validation_v0_1.md

    status = design_ready_pending_execution



Short-Side Context:

    artifact = 05_STATE_BUILDER_VALIDATION/short_side_context_builder_validation_v0_1.md

    status = design_ready_pending_execution



Broad Market Context:

    artifact = 05_STATE_BUILDER_VALIDATION/broad_market_context_builder_validation_v0_1.md

    status = design_ready_pending_execution



Halt Context:

    artifact = 05_STATE_BUILDER_VALIDATION/halt_context_builder_validation_v0_1.md

    status = design_ready_pending_execution

```



## 6.3 Siguiente Paso: Experimental Builder Validation Execution Core Four



El builder experimental ya existe y ha cerrado estos gates:



```text

contract_check

source_binding

path_validation

schema_metadata

logical_to_physical_column_binding

bounded_identity_and_temporal_validation

bounded_grain_validation

bounded_quality_and_lineage_validation

```



El siguiente builder no es de produccion. El siguiente gate es:



```text

experimental_builder_validation_execution_core_four

```



Objetos autorizados para el siguiente diseno/ejecucion experimental:



```text

Trading Activity

Price Movement

Price Location / Structure

Volatility / Range State

```



No abrir todavia:



```text

Liquidity builder execution

Market Microstructure builder execution

Order Flow Pressure builder execution

Market State Integration

State materialization

production builder development

unbounded row reads

full data reads

```



Si el builder experimental ejecuta una operacion larga, debe cumplir:



```text

C:\TSIS_Data\LONG_RUNNING_OPERATIONS_CONTRACT.md

```

## 6.4 Resultado Del Builder Experimental



Smokes y runs ejecutados:



```text

v0_1 = initial embedded-registry contract probe

v0_2 = separated source binding registry probe using superseded binding_and_schema_check_only mode name

v0_3 = binding_and_path_check_only pre-binding baseline

batch1_binding_v0_1 = first governed physical candidate root batch

batch2_binding_v0_1 = second governed physical candidate root batch; raw_quotes and 015 path-probed

batch3_binding_v0_1 = final governed physical candidate root batch; active binding layer complete

v0_4_schema_metadata_v0_1 = schema metadata gate executed; 3 pass, 7 fail pending column binding

v0_5_column_binding_v0_1 = logical-to-physical binding executed; 8 pass with findings, 2 blocked

v0_6_column_binding_v0_2 = blockers resolved; logical-to-physical binding passes with restrictions

v0_7_bounded_identity_temporal_v0_1 = bounded identity and temporal validation passes with restrictions

v0_8_bounded_grain_v0_1 = bounded grain validation passes with restrictions

v0_9_bounded_quality_lineage_v0_1 = bounded quality and lineage validation passes with restrictions

```



Reference run vigente:



```text

run_id = experimental_state_builder_probe_v0_9_20260721T184537Z

mode = bounded_quality_and_lineage_validation

overall_status = passed_bounded_quality_lineage_validation_with_restrictions

contract_resolution = PASS

ontology_to_mapping_resolution = PASS

blocked_capability_masking = PASS

order_flow_expected_block = PASS

binding_contract_structure = PASS

physical_candidate_roots = BOUND

physical_source_binding = PASS

path_validation = PASS

schema_resolution = REEXECUTED_WITH_COLUMN_BINDINGS

schema_validation = PASS_WITH_RESTRICTIONS

logical_column_resolution = PASS_WITH_RESTRICTIONS

data_resolution = BOUNDED_QUALITY_LINEAGE_AUTHORIZED_BY_SCOPE

data_validation = BOUNDED_QUALITY_LINEAGE_EXECUTED_WITH_LIMITS

grain_validation = CLOSED_PASS_WITH_RESTRICTIONS

temporal_value_validation = RECHECKED_FOR_QUALITY_LINEAGE_DERIVATION

quality_semantics_validation = PASS_WITH_RESTRICTIONS

lineage_validation = PASS_WITH_RESTRICTIONS

builder_validation_execution = NOT_EXECUTED

market_state_integration = NOT_OPEN



sources_sampled = 5

files_sampled = 8

rows_read = 12271

maximum_rows_authorized = 20000

rows_limit_respected = true

quality_lineage_fields_checked = 10

quality_lineage_derivations_checked = 8

builder_execution_blockers = 2

core_four_builder_execution_blockers = 0

quote_dependent_builder_execution_blockers = 2

promotion_only_restrictions = 8

core_four_builder_execution_readiness = OPEN_FOR_EXPERIMENTAL_BUILDER_VALIDATION_DESIGN

quote_dependent_builder_execution_readiness = BLOCKED_PENDING_QUOTE_ORDERING_OR_ASOF

```



Artefactos:



```text

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_state_builder_probe_v0_1.json

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_source_binding_registry_v0_1.json

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_column_binding_registry_v0_1.json

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_bounded_sample_scope_v0_1.json

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_bounded_grain_scope_v0_1.json

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_bounded_sample_validation_authorization_v0_1.md

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_bounded_grain_validation_authorization_v0_1.md

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_state_builder_probe_bounded_identity_temporal_readout_v0_1.md

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_state_builder_probe_bounded_grain_readout_v0_1.md

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/configs/experimental_bounded_quality_lineage_scope_v0_1.json

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_bounded_quality_lineage_validation_authorization_v0_1.md

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/experimental_state_builder_probe_bounded_quality_lineage_readout_v0_1.md

05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/runs/experimental_state_builder_probe_v0_9_20260721T184537Z/

```



Estado de gates:



```text

contract_check = CLOSED_PASS

experimental_physical_source_binding = CLOSED_PASS

path_validation = PASS

experimental_physical_schema_validation = REEXECUTED_WITH_COLUMN_BINDINGS

logical_to_physical_column_binding = PASS_WITH_RESTRICTIONS

bounded_identity_and_temporal_validation = CLOSED_PASS_WITH_RESTRICTIONS

bounded_grain_validation = CLOSED_PASS_WITH_RESTRICTIONS

bounded_quality_and_lineage_validation = CLOSED_PASS_WITH_RESTRICTIONS

experimental_builder_validation_execution_core_four = CLOSED_PASS_WITH_RESTRICTIONS

core_four_resolution_record_acceptance_review = CLOSED_PASS_WITH_RESTRICTIONS

experimental_core_four_market_state_integration_execution = CLOSED_PASS_WITH_RESTRICTIONS

core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS

official_state_materialization = NOT_AUTHORIZED

```



Hallazgo principal:



```text

El circuito documental de los 12 Objetos resuelve sin fallos ni leaks.

La transicion source_alias logico -> superficie fisica gobernada esta completa.

La capa logical_field -> physical evidence ya no tiene blockers criticos.

El primer bounded row-read gate no encontro fallos de identidad, parse temporal,

cutoff ni politica diaria en muestra acotada. El bounded grain gate no encontro

claves nulas ni duplicados criticos, pero si restricciones reales: 014 contiene

duplicados identicos y raw_quotes necesita una clave de orden adicional.

El resultado correcto es PASS_WITH_RESTRICTIONS, no PASS limpio.

```



Restricciones vivas:



```text

canonical identity normalization pending = true

raw quote timestamp unit policy promotion pending = true

daily availability calendar-aware policy pending = true

014 duplicate identical row handling policy pending = true

raw_quotes additional ordering key pending = true

quality semantics validation = partial/not executed

feature formulas = not executed

```



Decision especial de quotes sigue vigente:



```text

raw_quotes -> G:/TSIS/data/quotes_



G:/TSIS/data/quotes_ se usa como mirror local path-probe del root oficial:

E:/TSIS/data/quotes_



G:/TSIS/data/quotes no se usa para este binding.

```



Siguiente paso recomendado:



```text

core_four_market_state_candidate_physical_validation

```



Revisar solo la evidencia fisica candidata ya generada. No leer source market

data, no abrir quote-dependent builders y no autorizar consumo State.



## 6.5 Estado De Core-Four Integration Execution



El primer gate experimental de integracion core-four ya cerro con restricciones:



```text

run_id = experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z

mode = experimental_core_four_market_state_integration_execution

overall_status = passed_core_four_market_state_integration_execution_with_restrictions

experimental_core_four_market_state_integration_execution = PASS_WITH_RESTRICTIONS

contexts_seen = 10

input_resolution_records = 40

candidate_records_emitted = 8

rejected_contexts = 2

rejected_required_object_blocked_contexts = 2

failed_context_consistency = 0

failed_contract_or_determinism = 0

future_bar_leaks = 0

blocked_values_admitted = 0

admitted_value_rows = 136

source_market_data_rows_read = 0

parquet_files_written = 0

```



Artefactos:



```text

06_MARKET_STATE_INTEGRATION/experimental_core_four_market_state_integration_execution_authorization_v0_1.md

06_MARKET_STATE_INTEGRATION/configs/core_four_market_state_integration_execution_scope_v0_1.json

06_MARKET_STATE_INTEGRATION/scripts/core_four_market_state_integration_probe.py

06_MARKET_STATE_INTEGRATION/experimental_core_four_market_state_integration_execution_readout_v0_1.md

06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z/

```



Interpretacion:



```text

8 candidate JSONL records = diagnostic integration evidence

2 rejected contexts = expected pre-bar object_atomicity rejects

candidate records != canonical Market State rows

Market State parquet materialization = NOT_AUTHORIZED

production builder = NOT_AUTHORIZED

downstream consumption = NOT_AUTHORIZED

```



Estado posterior:



```text

core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS

```



## 6.6 Estado De Core-Four Materialization Design



El diseno de materializacion candidata core-four ya cerro con restricciones:



```text

logical_profile_id = core_four_market_state_profile_v0_1

physical_schema_id = core_four_market_state_candidate_physical_schema_v0_1

source_integration_run_id = experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z

input_candidate_records_expected = 8

candidate_records_accepted_for_materialization_design = true

core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS

experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS

experimental_candidate_parquet_output_allowed = true

official_parquet_write_authorized = false

production_builder_authorized = false

downstream_consumption_authorized = false

official_market_state_authorized = false

```



Artefactos:



```text

06_MARKET_STATE_INTEGRATION/core_four_market_state_materialization_design_v0_1.md

06_MARKET_STATE_INTEGRATION/core_four_market_state_materialization_design_contract_v0_1.json

```



Interpretacion:



```text

8 candidate records = accepted design inputs only

candidate parquet execution = CLOSED_PASS_WITH_RESTRICTIONS

official Market State = NOT_OPEN

downstream consumption = NOT_AUTHORIZED

```



## 6.7 Estado De Core-Four Materialization Authorization



La autorizacion acotada de materializacion candidata core-four ya fue emitida:



```text

authorization = experimental_core_four_market_state_materialization_authorization_v0_1.md

scope = configs/experimental_core_four_market_state_materialization_scope_v0_1.json

experimental_core_four_market_state_materialization_authorization = AUTHORIZED_WITH_RESTRICTIONS

experimental_core_four_market_state_materialization_execution = CLOSED_PASS_WITH_RESTRICTIONS

input_candidate_records = 8

max_output_candidate_rows = 8

schema_inference_from_sample = false

physical_value_columns_closed = true

json_field_serialization = canonical_utf8_json_string

state_output_fingerprint_payload = exact_non_circular

semantic_rebuild_determinism = required

byte_identical_parquet_rebuild = not_required

source_market_data_reread_allowed = false

official_market_state_allowed = false

downstream_consumption_allowed = false

```



Siguiente gate posible:



```text

core_four_market_state_candidate_physical_validation

```



La ejecucion ya creo el materializer experimental, escribio un parquet candidato

no oficial dentro de `06_MARKET_STATE_INTEGRATION/runs/`, uso el payload exacto

y no circular de `state_output_fingerprint`, valido determinismo semantico entre

rebuilds, emitio reports de schema/grain/lineage/restrictions/fingerprints/

roundtrip y cerro con readout. No hay autorizacion para consumo downstream ni

promocion.





## 6.8 Estado De Core-Four Materialization Execution



La ejecucion experimental acotada de materializacion core-four ya cerro con

restricciones:



```text

run_id = experimental_core_four_market_state_materialization_v0_1_20260722T081155Z

mode = experimental_core_four_market_state_materialization_execution

overall_status = passed_core_four_market_state_materialization_with_restrictions

experimental_core_four_market_state_materialization_execution = PASS_WITH_RESTRICTIONS

input_candidate_records = 8

output_candidate_rows = 8

candidate_parquet_files_written = 1

candidate_parquet_bytes = 34097

source_market_data_rows_read = 0

physical_column_count = 40

physical_value_column_count = 17

schema_match = true

hard_validation_failures = 0

roundtrip_failures = 0

semantic_rebuild_differences = 0

semantic_rebuild_compare_field_count = 37

```



Artefactos:



```text

06_MARKET_STATE_INTEGRATION/scripts/core_four_market_state_materialization_probe.py

06_MARKET_STATE_INTEGRATION/experimental_core_four_market_state_materialization_execution_readout_v0_1.md

06_MARKET_STATE_INTEGRATION/runs/experimental_core_four_market_state_materialization_v0_1_20260722T081155Z/

```



Interpretacion:



```text

8 physical candidate rows = bounded experimental evidence

core_four_market_state_candidate_v0_1.parquet != official Market State table

candidate rows are not downstream consumable

production builder remains false

dataset promotion remains false

```



Siguiente gate posible:



```text

core_four_market_state_candidate_physical_validation

```



## 7. Estructura Esperada De Cada Operational Mapping



Ubicacion:



```text

C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING\<object>_operational_mapping_v0_1.md

```



El documento debe ser puente de ingenieria, no nueva ciencia.

Debe implementar la Formal Admission y el Freeze Act sin redefinir la identidad

del Objeto.



Debe contener como minimo:



```text

1. Governance Input

2. Approved Semantic Capability

3. Approved Representation Models

4. Capability To Physical Mapping

5. Source Tables And Temporal Legality

6. Operational Restrictions

7. Required Builder Validation

8. Authorized And Non-Authorized Consumers

9. Review Triggers

10. Evidence TSIS

```



El bloque de decision debe conservar:



```text

operational_mapping_phase_b_authorized = true

production_builder_authorized = false

state_consumption_authorized = false

physical_variables_authorized = false

schema_change_authorized = false_until_phase_b_artifacts

physical_materialization_authorized = false

dataset_promotion_authorized = false

builder_validation_required = true

market_state_integration_required = true

```



## 8. Verificaciones Obligatorias



Despues de crear cada Operational Mapping:



```text

1. Buscar autorizaciones accidentales. Los siguientes flags no deben aparecer

   con valor verdadero en el artefacto revisado:



   production_builder_authorized

   state_consumption_authorized

   physical_variables_authorized

   schema_change_authorized

   physical_materialization_authorized

   dataset_promotion_authorized

   operational_promotion_authorized



2. Confirmar que el mapping no redefine la scientific identity del Objeto.



3. Confirmar que cada variable fisica candidata tiene fuente, temporal rule,

   State profile previsto y restriction si falta una policy.



4. Ejecutar git diff --check sobre los archivos tocados.



5. Revisar git status --short solo para los archivos tocados.



6. Confirmar que no se modificaron builders, schemas, materializaciones,

   datasets productivos ni Market State Integration salvo instruccion explicita.

```

## 9. Artefactos De Cierre De Phase A



Phase A queda cerrada por estos artefactos:



```text

Formal Admissions:

    C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\ACCEPTED_WITH_RESTRICTIONS\



Cross-Object Ontology Review:

    C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_REVIEW.md



Freeze Act:

    C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md

```



No recrear estos documentos salvo contradiccion estructural real.



## 10. Autoridad De Phase B



El freeze autoriza iniciar Phase B como ingenieria gobernada:



```text

Operational Mapping

    -> Builder Validation

        -> Market State Integration

            -> Event State Integration

                -> Operational Promotion

```



Reglas de autoridad:



```text

operational_mapping_phase_b_authorized = true

production_builder_authorized = false

state_consumption_authorized = false

physical_materialization_authorized = false

schema_change_authorized = false_until_phase_b_artifacts

```



Usar el vertical de `Trading Activity` como piloto de proceso, no como

autoridad operativa automatica.



## 11. Lock De Ontologia v1



Ningun nuevo Information Object entra en `TSIS Market Ontology v1` salvo:



```text

extraordinary_evidence_of_missing_primary_informational_uncertainty

proven_structural_contradiction

phase_b_identity_loss_discovery

explicit_v1_1_or_v2_governance_decision

```



Los conceptos nuevos ordinarios van a backlog `vNext candidate`.

## 12. Regla Final



No dejar decisiones estructurales solo en conversacion.



Si una decision cambia semantica, estructura o gobierno, debe quedar en:



```text

formal admission

cross-object review

freeze artifact

changelog

```



No crear nuevas capas de proceso salvo contradiccion estructural real.
