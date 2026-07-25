# Event State Integration Design Authorization v0.1

Status: `authorized_with_restrictions_consumed_by_design_v0_1`
Date: `2026-07-24`
Scope: `session_opened_core_four_event_state_integration_design`

## 1. Authorization

This authorization allows design-only work for the first Event State
integration grammar for:

```text
event_state_profile_id = event_state_core_four_intraday_profile_v0_1
event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
source_market_state_profile_id = market_state_core_four_intraday_profile_v0_1
```

It allows the design to define how future Event State records will atomically
bind:

```text
Market State record reference
Event Instance
Event Window Binding
Instrument Session Projection
State role
Consumption legality
```

## 2. Required Prior Gates

The design must consume only prior design authorities:

```text
event_type_initial_admission_review = CLOSED_WITH_MIXED_DECISIONS_NO_EXECUTION
event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_window_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
market_state_profile_compatibility_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
instrument_session_projection_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
```

No prior design is reopened by this authorization.

## 3. Explicitly Authorized Work

Authorized:

```text
define Event State integration grain
define future Event State record identity
define exact-one binding requirements
define required lineage fields
define state_role and consumption_legality integration rules
define blocked/partial/ambiguous binding policy
define future execution preconditions
define no-execution readout
```

## 4. Explicitly Prohibited Work

Not authorized:

```text
create Event Instances
create Event Window Bindings
create Instrument Session Projections
read Market State parquet
read Data Foundation market-data rows
read instrument_master rows
read calendar rows
emit Event State records
write Event State JSONL
write Event State parquet
modify official Market State profile artifacts
promote an Event State profile
promote an Event State dataset
run detectors
run builders
open downstream consumption
open production
```

## 5. Boundary Counters

Required closure counters:

```text
event_state_records_emitted = 0
event_state_parquet_files_written = 0
market_state_records_consumed = 0
event_instances_created = 0
event_windows_created = 0
instrument_session_projections_created = 0
source_market_data_rows_read = 0
physical_market_state_parquet_reads = 0
downstream_consumers_enabled = 0
```

## 6. Required Design Decision

The design must decide whether future Event State records can exist without all
six bindings being exactly one:

```text
source_market_state_record_binding
event_instance_binding
event_window_binding
instrument_session_projection_binding
state_role_classification
consumption_legality_classification
```

The expected policy is:

```text
missing_or_ambiguous_binding -> blocked
partial_event_state_record -> prohibited
substituted_market_state_record -> prohibited
```

## 7. Completion Criteria

This authorization is consumed only when the following artifacts exist:

```text
configs/event_state_integration_design_scope_v0_1.json
event_state_integration_design_v0_1.md
event_state_integration_design_contract_v0_1.json
event_state_integration_design_readout_v0_1.md
```

## 8. Next Gate

If the design closes, the next recommended gate is:

```text
event_state_execution_chain_joint_review_authorization_v0_1
```

The joint review should inspect the design chain before any execution
authorization is opened.
