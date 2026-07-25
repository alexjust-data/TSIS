# Event State Instrument Session Projection Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Design Run: `event_state_instrument_session_projection_design_v0_1_20260724T144500Z`

## 1. Scope

This design defines the projection bridge required before Event State can bind
the exchange-session `session_opened` Event Type to instrument-level Market
State records.

It is design-only. It does not enumerate instruments, read `instrument_master`,
read calendars, create projections, create Event Instances, bind windows,
consume Market State or materialize Event State.

## 2. Why The Projection Exists

The accepted Event Type is scoped as:

```text
event_type:market_data:session_opened
accepted_subject_scope = exchange_session
```

The parent Market State profile is scoped by:

```text
instrument_id
session_date
decision_timestamp_utc
```

Therefore TSIS needs an explicit projection layer:

```text
exchange_session Event Instance
    +
exchange_session Event Window Binding
    +
instrument-session association
    ->
instrument-level Event State context
```

This avoids silently turning one exchange opening into thousands of native Event
Instances.

## 3. Projection Identity

Future projection identity must be deterministic and separate from event
identity.

Conceptual identity:

```text
event_state_instrument_session_projection_id =
sha256(
    event_instance_id
    + event_window_binding_id
    + instrument_id
    + session_date
    + instrument_exchange_id
    + market_state_profile_id
    + projection_policy_version
)
```

The projection id may change if instrument identity, exchange mapping,
calendar authority or projection policy changes. The native Event Instance id
and Event Window Binding id must not change because of projection.

## 4. Future Projection Fields

Future projection records must preserve at least:

```text
event_state_instrument_session_projection_id
projection_policy_id
projection_policy_version
event_type_id
event_instance_id
event_window_binding_id
exchange_id
session_date
event_anchor_timestamp_utc
window_start_utc
window_end_utc
instrument_id
ticker
instrument_exchange_id
instrument_master_version
instrument_identity_fingerprint
instrument_lifecycle_status
listing_status_as_of_session
instrument_session_eligibility_state
market_state_profile_id
market_state_schema_version
calendar_version
calendar_row_fingerprint
projection_quality_state
projection_created_at_utc
supersedes_projection_id
superseded_by_projection_id
correction_reason
```

This is not a physical schema authorization. It is a minimum contract for a
future execution gate.

## 5. Eligibility Policy

An instrument-session projection may be valid only when future execution can
prove:

```text
instrument_id resolves exactly once
ticker resolves to the instrument_id for the session date when ticker is used
instrument exchange is compatible with the exchange-session Event Instance
instrument lifecycle permits association on session_date
calendar session exists and matches the Event Instance
Market State profile reference is compatible
```

Missing or ambiguous identity, exchange or lifecycle evidence must block the
projection.

## 6. Exchange Policy

For v0.1 design, the safest policy is:

```text
primary_or_governed_listing_exchange_match_required
```

If an instrument has multiple venues, stale exchange metadata or ambiguous
primary exchange assignment for the session date, the projection must be
blocked or marked non-executable until a venue policy is authorized.

## 7. Halt And Tradability Boundary

An instrument-specific halt at the regular open does not invalidate the
exchange-session `session_opened` Event Instance.

It may affect:

```text
instrument_session_eligibility_state
Market State interpretation
Event State quality_state
future Execution State / tradability
```

It must not change:

```text
event_type_id
event_instance_id
event_window_binding_id
```

Locates, borrow availability, broker routing, fills, slippage, commissions and
API latency belong to Execution State or execution policy, not this projection
identity.

## 8. Market State Join Boundary

Projection does not consume Market State. It only defines the future bridge.

Future Event State integration must still prove:

```text
market_state_profile_id = market_state_core_four_intraday_profile_v0_1
instrument_id matches projection
session_date matches projection and governed calendar
decision_timestamp_utc is legally related to the event window
state_output_fingerprint or accepted reference resolves exactly once
```

No direct exchange-session to Market State join is allowed without projection.

## 9. Closed Boundaries

Still closed:

```text
instrument_session_projection_execution
event_instance_binding_execution
event_window_binding_execution
market_state_physical_consumption
event_state_builder_execution
event_state_integration_execution
event_state_materialization
official_event_state_profile_promotion
official_event_state_dataset_promotion
production
downstream_consumption
```

## 10. Next Work

The next recommended gate is:

```text
event_state_integration_design_authorization_v0_1
```

That gate can design how Market State, Event Instance, Event Window and
instrument-session projection records combine atomically. It must still not
execute unless a later execution authorization is issued.
