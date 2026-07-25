# Market State Profile Compatibility Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Design Run: `market_state_profile_compatibility_design_v0_1_20260724T142500Z`

## 1. Scope

This design evaluates compatibility between:

```text
source_market_state_profile_id =
market_state_core_four_intraday_profile_v0_1

event_state_profile_id =
event_state_core_four_intraday_profile_v0_1

event_type_id =
event_type:market_data:session_opened
```

The evaluation is semantic and contractual only. It does not consume a physical
Market State dataset or create Event State rows.

## 2. Compatibility Verdict

```text
semantic_profile_compatibility =
SEMANTICALLY_COMPATIBLE_WITH_RESTRICTIONS

physical_consumption_authority =
NOT_AUTHORIZED

execution_readiness =
NOT_READY_REQUIRES_INSTRUMENT_SESSION_PROJECTION_DESIGN
```

The profiles are compatible at the semantic contract level because Event State
can reference the promoted Market State profile as its parent state
representation.

They are not yet executable together because their native grains differ:

```text
Market State core-four
    = instrument_id + session_date + decision_timestamp_utc + profile/schema lineage

session_opened Event Instance
    = exchange_id + session_date + calendar_version + event_anchor_timestamp_utc
```

Therefore a future instrument-session projection is required before Event State
can bind exchange-session events to instrument-level Market State records.

## 3. Market State Profile Authority

Accepted parent profile:

```text
profile_id = market_state_core_four_intraday_profile_v0_1
status = OFFICIAL_PROFILE_PROMOTED_WITH_RESTRICTIONS
profile_classification = official_profile
promotion_run_id = official_market_state_candidate_promotion_v0_1_20260723T193403Z
```

The profile is not an official physical dataset:

```text
official_market_state_authorized = false
official_dataset_registry_write_authorized = false
official_parquet_written = false
downstream_consumption_authorized = false
complete_tsis_market_state = false
```

The profile covers these required Information Objects:

```text
trading_activity
price_movement
price_location_structure
volatility_range_state
```

It excludes quote-dependent and complete TSIS Market State objects outside
core-four.

## 4. Market State Grain And Join-Relevant Fields

Join-relevant contractual fields include:

```text
state_profile_id
state_schema_version
source_integration_profile_id
instrument_id
ticker
session_date
decision_timestamp_utc
decision_case
context_id
integration_status
object_completeness_status
quality_status
calendar_version
source_lineage_json
policy_versions_json
formula_versions_json
restriction_codes_json
context_input_fingerprint
state_output_fingerprint
```

A future Event State builder must reference Market State records by an
accepted profile identity and a stable Market State record id or fingerprint.
It must not rebuild Market State or read upstream Data Foundation tables
directly unless a separate gate authorizes that builder mode.

## 5. Event Side Authority

Current Event State side:

```text
event_type:market_data:session_opened = accepted_with_restrictions
accepted_subject_scope = exchange_session
event_instance_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
event_window_binding_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
```

Event Instance native identity excludes `instrument_id`. Event Window Binding
also remains exchange-session scoped.

## 6. Required Projection Bridge

Compatibility requires a future projection object:

```text
event_state_instrument_session_projection
```

It must bind:

```text
exchange-session Event Instance
exchange-session Event Window Binding
instrument_id
ticker
instrument_exchange_id
session_date
instrument_lifecycle_status
Market State profile reference
```

The projection must answer whether an instrument belongs to the exchange
session context. It must not change the native Event Instance id or Event
Window Binding id.

## 7. Future Join Semantics

A future Event State record may exist only if all bindings are exactly one:

```text
source_market_state_profile_binding = exactly_one
event_instance_binding = exactly_one
event_window_binding = exactly_one
instrument_session_projection_binding = exactly_one
state_role_classification = exactly_one
consumption_legality_classification = exactly_one
```

Missing or ambiguous bindings must block the row.

Future join constraints:

```text
instrument_id must match projected instrument context
session_date must match governed calendar session
decision_timestamp_utc must be within or legally related to the Event Window
calendar_version must be compatible or explicitly reconciled
Market State profile id must equal market_state_core_four_intraday_profile_v0_1
Market State schema version must match accepted profile schema authority
```

## 8. Temporal And Leakage Policy

For `session_opened`:

```text
event_anchor_timestamp_utc = governed session_open_utc
regular_session_open_timestamp != first_observed_trade_timestamp
```

Compatibility does not make all open-adjacent Market State records
decision-safe.

Future legality must be derived from:

```text
state_role
consumption_legality
decision_timestamp_utc
event_anchor_timestamp_utc
window_start_utc
window_end_utc
first_observable_timestamp_utc
Market State as-of/cutoff evidence
```

Rules preserved:

```text
post_event != decision_safe
post_event_review != decision_safe
outcome_adjacent != feature input
```

## 9. Physical Consumption Boundary

This design does not authorize:

```text
read candidate Market State parquet
read official Market State parquet
copy candidate parquet into official dataset roots
materialize Event State
consume Event State downstream
```

Since no official physical Market State dataset exists yet, future Event State
execution must either consume a separately authorized candidate/evidence
surface or invoke a separately authorized Market State builder mode.

## 10. Data Foundation Boundary

Data Foundation remains physical authority for future datasets and schemas.
Applied Architecture governs semantic compatibility and profile meaning.
Execution authority must be a separate gate.

This design does not change Data Foundation registry state and does not promote
any `016_market_state_table` or `017_event_state_table` physical dataset.

## 11. Closed Boundaries

Still closed:

```text
market_state_physical_consumption
event_instance_binding_execution
event_window_binding_execution
instrument_session_projection_execution
event_state_builder_execution
event_state_integration_execution
event_state_materialization
official_event_state_profile_promotion
official_event_state_dataset_promotion
production
downstream_consumption
```

## 12. Next Work

The next recommended gate is:

```text
event_state_instrument_session_projection_design_authorization_v0_1
```

This is required because the accepted Event Type is exchange-session scoped
while the parent Market State profile is instrument/timestamp scoped.
