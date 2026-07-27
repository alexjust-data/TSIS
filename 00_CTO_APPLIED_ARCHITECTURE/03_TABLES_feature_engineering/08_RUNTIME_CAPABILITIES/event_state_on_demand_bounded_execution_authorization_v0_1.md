# Event State On-Demand Bounded Execution Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-27`

```text
gate = event_state_on_demand_bounded_execution_authorization_v0_1
parent_gate = event_state_on_demand_execution_chain_joint_review_v0_1
authorization_scope = bounded_event_state_on_demand_execution_only
authorized_next_gate = event_state_on_demand_bounded_execution_v0_1
event_state_requests_created = 0
dependency_resolver_executions = 0
execution_plans_created = 0
run_records_created = 0
event_instances_created = 0
event_window_bindings_created = 0
instrument_projections_created = 0
market_state_dependency_requests_executed = 0
market_state_candidate_files_read = 0
event_state_materializer_executions = 0
event_state_validator_executions = 0
registry_entries_written = 0
event_state_records_emitted = 0
datasets_written = 0
official_dataset = false
production = false
downstream = false
```

This authorization consumes the Event State on-demand execution-chain joint review and authorizes opening one bounded execution gate.

It does not execute that gate.

## Authorized Bounded Scope

The future bounded execution may create exactly one candidate Event State on-demand run for:

```text
request_type = event_state
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
event_state_profile_version_policy = exact
event_type_id = event_type:market_data:session_opened
event_subject_scope = exchange_session
event_type_registry_snapshot_policy = exact
output_mode = candidate
exchange_scope = XNYS
session_dates = 2021-01-19, 2021-03-15, 2022-11-25
instrument_projection_scope = explicit_instrument_ids
instrument_ids =
    figi_share_class:BBG001S5N8T1  # AAME
    figi_share_class:BBG001S8T7K0  # ABEO
    figi_share_class:BBG001S6RSK0  # ABUS
maximum_event_types = 1
maximum_exchanges = 1
maximum_sessions = 3
maximum_native_event_instances = 3
maximum_instruments = 3
maximum_instrument_session_projections = 9
maximum_market_state_dependency_contexts = 9
maximum_event_state_logical_contexts = 9
maximum_event_state_candidate_records = 9
```

Native Event Instance identity remains exchange-session scoped:

```text
event_instance_native_grain = event_type_id + exchange_id + session_date + calendar_version + event_anchor_timestamp_utc
instrument_id_in_native_event_instance_identity = false
```

Instrument association is a projection, not native event identity.

## Market State Dependency Boundary

The future bounded execution must resolve Market State through:

```text
market_state_runtime_capability_id = market_state_on_demand_runtime_capability_v0_1
market_state_consumption_policy = market_state_capability_consumption_policy_v0_1
market_state_dependency_mode = runtime_capability_subrequest_or_exact_validated_candidate_reference
market_state_profile_id = market_state_core_four_intraday_profile_v0_1
market_state_profile_version_policy = exact
market_state_dependency_reuse_policy = reuse_if_exact_validated_dependency_match_or_block
```

It must not name or consume direct Market State parquet paths as authority.

Any physical Market State candidate access in the future execution must be explicitly justified by the Market State runtime capability policy, bounded to this scope, fingerprint-matched, lineage-checked and recorded as dependency evidence. If that authority cannot be proven, the future execution must close blocked before Event State materialization.

## Authorized Future Actions

The next gate may, only inside the bounded scope above:

```text
create one normalized Event State request record
execute Event State dependency resolution
create one frozen Event State Execution Plan
consume one explicit execution authorization
create one run record and governed manifests
create or resolve bounded Event Instances for session_opened
create or resolve bounded Event Window Bindings
create or resolve bounded Instrument Session Projections
resolve one bounded Market State dependency through runtime capability authority
execute the Event State materializer if all dependencies are exact-one resolved
write candidate Event State output files
execute the Event State validator
write validation reports
write one candidate Event State dataset registry entry
emit a bounded execution readout
```

## Required Restrictions

The future execution must:

```text
use output_mode = candidate
use exact profile and registry snapshot policies
use no fallback Event Type, no halt_resumed and no detector execution
preserve exchange_session as native event subject scope
preserve instrument association as projection only
use no direct Market State physical path authority
block before materialization if Market State dependency authority is unavailable
record every requested logical context as represented, blocked, unavailable, quarantined or not_built
preserve state_role and consumption_legality as separate fields
```

## Explicit Prohibitions

This authorization does not allow:

```text
unbounded Event State execution
full-history execution
full-universe execution
new Event Types
halt_resumed
event detection
instrument-level native session_opened identity
new Market State profiles
new Event State profiles
official Event State dataset promotion
official parquet writes
production
downstream consumption
backtesting
ML/RL consumption
strategy evaluation
```

## Closure

This document records authorization only. The authorization is consumed by being recorded for the next bounded execution gate and cannot be reused for a different scope.

The next allowed gate is:

```text
event_state_on_demand_bounded_execution_v0_1
```