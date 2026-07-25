# Event Instance Binding Design Authorization v0.1

Status: `authorized_with_restrictions_consumed_by_design_v0_1`
Date: `2026-07-24`
Scope: `event_instance_binding_design_only_for_session_opened_exchange_session`

This authorization opens one design-only gate for Event Instance Binding.

It is limited to:

```text
event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
registry_snapshot_authority = tsis_event_type_registry_v0_1_post_initial_admission_001
registry_snapshot_sha256 = f3627c8b44062081c8e2f2775bffbd283bd31f2ca1e876aa7469fd6586425c43
```

It does not authorize Event Instance creation, historical binding execution,
detector execution, Event Window binding execution, Market State physical
consumption, Event State builders, materialization, production or downstream
consumption.

## 1. Decision

```text
event_instance_binding_design_authorization_v0_1 = AUTHORIZED_WITH_RESTRICTIONS_CONSUMED
design_id = event_instance_binding_design_v0_1
authorized_event_type = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
event_instance_creation_authorized = false
detector_execution_authorized = false
historical_calendar_rows_consumed = 0
physical_parquet_reads_allowed = false
```

## 2. Governing Inputs

```text
event_state_event_policy_v0_1.md
event_type_registry_seed_design_v0_1.md
event_type_registry_seed_design_contract_v0_1.json
event_type_initial_admission_review_readout_v0_1.md
event_type_initial_admission_review_records_v0_1.json
event_type_registry_post_initial_admission_snapshot_v0_1.json
04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md
06_MARKET_STATE_INTEGRATION/governed_exchange_session_calendar_binding_validation_readout_v0_1.md
configs/event_instance_binding_design_scope_v0_1.json
```

## 3. Authorized Design Questions

The design may define:

```text
canonical Event Instance grain
event_instance_id key material
timestamp policy
calendar lineage requirements
instrument projection boundary
exception and correction policy
supersession policy
```

The design must preserve:

```text
Event Type identity = exchange-session occurrence
Instrument association = future projection or binding
```

Native `session_opened` Event Instance identity must not include:

```text
instrument_id
ticker
first_observed_trade_timestamp
strategy_id
outcome_label
execution_state
```

## 4. Closed Boundaries

```text
event_instance_binding_execution_authorized = false
event_instances_created = 0
historical_calendar_rows_consumed = 0
detector_execution_authorized = false
instrument_projection_execution_authorized = false
event_window_binding_execution_authorized = false
market_state_physical_consumption_authorized = false
event_state_builder_execution_authorized = false
event_state_materialization_authorized = false
downstream_consumption_authorized = false
production_authorized = false
```

## 5. Outputs

```text
configs/event_instance_binding_design_scope_v0_1.json
event_instance_binding_design_v0_1.md
event_instance_binding_design_contract_v0_1.json
event_instance_binding_design_readout_v0_1.md
```

This gate must not create:

```text
event_instance_registry.json
event_instances.parquet
```

## 6. Next Gate

After this design closes, the next recommended gate is:

```text
event_window_binding_design_authorization_v0_1
```

That later gate remains design-only unless separately authorized otherwise.
