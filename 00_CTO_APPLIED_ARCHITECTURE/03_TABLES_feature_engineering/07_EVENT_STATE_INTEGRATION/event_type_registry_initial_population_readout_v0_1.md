# Event Type Registry Initial Population Readout v0.1

Status: `closed_pass_with_restrictions_candidate_population_only_v0_1`
Date: `2026-07-24`
Scope: `initial_candidate_event_family_and_type_population_only`

This readout closes the first bounded Event Type Registry population action.

It created candidate registry entries only. It did not admit any Event Type.

## 1. Accepted Inputs

```text
authorization = event_type_registry_initial_population_authorization_v0_1.md
scope = configs/event_type_registry_initial_population_scope_v0_1.json
seed_design = event_type_registry_seed_design_v0_1.md
seed_design_contract = event_type_registry_seed_design_contract_v0_1.json
policy = event_state_event_policy_v0_1.md
```

## 2. Output Snapshot

```text
registry_snapshot_id = tsis_event_type_registry_v0_1_candidate_population_001
registry_snapshot_file = event_type_registry_initial_population_snapshot_v0_1.json
registry_snapshot_sha256 = 10613b9b4139b9184ccf5a2f515d23ba0563a973cb50262647ee7ae8ea457537
```

## 3. Counts

```text
candidate_event_families_created = 2
candidate_event_types_created = 2
candidate_event_variants_created = 0
candidate_event_compositions_created = 0
accepted_event_families = 0
accepted_event_types = 0
admission_reviews_executed = 0
detectors_executed = 0
event_instances_created = 0
event_windows_bound = 0
event_state_records_created = 0
parquet_files_written = 0
downstream_consumers_enabled = 0
```

## 4. Candidate Families

```text
event_family:regulatory:trading_halt
    status = investigational_candidate

event_family:market_data:session_lifecycle
    status = investigational_candidate
```

These are candidate family entries, not accepted families.

## 5. Candidate Event Types

```text
event_type:regulatory:halt_resumed
    status = investigational_candidate
    source_authority_seed = 006_halts_table

event_type:market_data:session_opened
    status = investigational_candidate
    source_authority_seed = 001_market_calendar
    calendar_authority_seed = governed_exchange_session_calendar_xnys_v0_1
```

These are not eligible for Event Instance binding until a separate admission
review moves an entry to:

```text
accepted_with_restrictions
accepted
```

## 6. Session Open Boundary

For `event_type:market_data:session_opened`:

```text
regular_session_open_timestamp != first_observed_trade_timestamp
```

The event is the governed regular-session open from calendar authority. It is
not the first trade printed by the instrument.

## 7. Halt Resume Boundary

For `event_type:regulatory:halt_resumed`:

```text
halt_resume_timestamp != first_post_halt_trade_timestamp
```

The event is the governed halt-resumption transition. It is not proof of
tradability, fills, liquidity, spread or post-resume execution quality.

## 8. Execution State Boundary

The population records a standing boundary:

```text
Event Type = what occurred.
Market State = how the market was represented.
Execution State = what operational execution capacity existed.
Outcome = what happened after.
```

The initial candidates do not encode:

```text
locates
slippage
broker acceptance
routing
API latency
partial fills
commission or fees
tradability
```

Those require future Execution State or execution-policy design.

## 8.1 Admission Review Marker

The candidate entries use:

```text
admission_review_record_id = pending_admission_review_not_authorized
```

This is a blocking marker, not an admission review. It means no candidate can
support Event Instance binding until a separate admission review creates a real
review record and changes the entry status.

## 8.2 Future Identity Stability Field

A future registry schema revision should consider `event_identity_stability`
with values such as:

```text
immutable
conditionally_stable
source_dependent
experimental
```

This was not added to the v0.1 snapshot and does not change the snapshot hash.
The field should be evaluated before the registry contains many Event Types, not
retroactively inferred from candidate names.

## 9. Closed Boundaries

The following remain closed:

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

## 10. Closure

```text
event_type_registry_initial_population = CLOSED_PASS_WITH_RESTRICTIONS
registry_population_state = candidate_population_recorded
accepted_event_types = 0
next_allowed_gate = event_type_initial_admission_review_authorization_v0_1
```

The next gate is not opened by this readout.
