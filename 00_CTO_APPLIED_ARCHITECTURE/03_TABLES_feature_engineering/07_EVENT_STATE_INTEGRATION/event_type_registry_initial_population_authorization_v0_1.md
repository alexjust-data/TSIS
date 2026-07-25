# Event Type Registry Initial Population Authorization v0.1

Status: `authorized_with_restrictions_consumed_by_initial_population_v0_1`
Date: `2026-07-24`
Scope: `initial_candidate_event_family_and_type_population_only`

This authorization opens one bounded registry population action.

It authorizes candidate entries only. It does not admit any Event Type,
execute detectors, create Event Instances, bind Event Windows, consume Market
State physically, execute Event State builders, materialize parquet, promote a
dataset, enable production or open downstream consumption.

## 1. Decision

```text
event_type_registry_initial_population_authorization = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
registry_snapshot_authorized = true
allowed_initial_status = investigational_candidate
candidate_event_families_authorized = 2
candidate_event_types_authorized = 2
accepted_event_families_authorized = 0
accepted_event_types_authorized = 0
contract_draft_status_authorized = false
event_detection_execution_authorized = false
event_instance_creation_authorized = false
event_window_binding_authorized = false
event_state_builder_execution_authorized = false
event_state_materialization_authorized = false
downstream_consumption_authorized = false
```

## 2. Governing Inputs

```text
event_state_event_policy_v0_1.md
event_type_or_event_family_contract_design_v0_1.md
event_type_or_event_family_contract_design_contract_v0_1.json
event_type_registry_seed_design_v0_1.md
event_type_registry_seed_design_contract_v0_1.json
configs/event_type_registry_initial_population_scope_v0_1.json
```

## 3. Authorized Registry Snapshot

```text
registry_snapshot_id = tsis_event_type_registry_v0_1_candidate_population_001
registry_snapshot_file = event_type_registry_initial_population_snapshot_v0_1.json
readout = event_type_registry_initial_population_readout_v0_1.md
```

The snapshot may create only these candidate families:

```text
event_family:regulatory:trading_halt
event_family:market_data:session_lifecycle
```

The snapshot may create only these candidate types:

```text
event_type:regulatory:halt_resumed
event_type:market_data:session_opened
```

All four entries must use:

```text
status = investigational_candidate
```

## 4. Namespace Extension

The seed design already recognized:

```text
event_domain = regulatory
```

This authorization permits `regulatory` as a candidate family/type namespace
for the initial halt lifecycle candidate. This is a namespace correction and
population permission only. It does not create an accepted regulatory family.

```text
accepted_event_families = 0
accepted_event_types = 0
```

## 5. Candidate Semantics

### event_type:regulatory:halt_resumed

Phenomenon:

```text
A previously halted instrument or security has resumed trading under governed
halt source or venue/regulatory authority.
```

Initial source authority:

```text
006_halts_table
```

The official halt/resume timestamp and the first post-halt trade must remain
distinct unless a later admission review proves equality.

### event_type:market_data:session_opened

Phenomenon:

```text
The regular trading session for the instrument/exchange/session_date has begun
according to the governed market calendar authority.
```

Initial source authority:

```text
001_market_calendar
governed_exchange_session_calendar_xnys_v0_1
```

Critical boundary:

```text
regular_session_open_timestamp != first_observed_trade_timestamp
```

The event is the governed regular-session open, not the first print for the
instrument.

## 6. Execution State Boundary

Event Type identity must not encode execution capacity.

The initial candidates do not describe:

```text
locates
slippage
broker availability
order routing
API latency
partial fills
commissions
order acceptance
tradability
```

Those belong to a future Execution State or execution-policy layer, not to the
identity of an Event Type.

## 7. Closed Boundaries

This authorization keeps closed:

```text
event_type_admission_execution
event_detection_execution
event_instance_binding_execution
event_window_binding_execution
market_state_physical_consumption
event_state_builder_execution
event_state_integration_execution
event_state_materialization
event_state_physical_validation
official_event_state_profile_promotion
official_event_state_dataset_promotion
production
downstream_consumption
```

## 8. Next Gate

After the accepted population readout, the next possible gate is:

```text
event_type_initial_admission_review_authorization_v0_1
```

That later gate may review candidate entries. It is not opened here.
