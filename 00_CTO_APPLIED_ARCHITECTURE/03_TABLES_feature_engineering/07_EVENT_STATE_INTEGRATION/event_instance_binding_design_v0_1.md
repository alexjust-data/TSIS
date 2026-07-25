# Event Instance Binding Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-24`
Scope: `session_opened_exchange_session_event_instance_identity_design`

This document defines how TSIS will identify a native Event Instance for:

```text
event_type_id = event_type:market_data:session_opened
accepted_subject_scope = exchange_session
```

It is design only. It creates no Event Instances and performs no historical
calendar binding.

## 1. Authority

```text
registry_snapshot_id = tsis_event_type_registry_v0_1_post_initial_admission_001
registry_snapshot_sha256 = f3627c8b44062081c8e2f2775bffbd283bd31f2ca1e876aa7469fd6586425c43
event_type_definition_hash = be5a176f5047a606bb4dfb75edf740fcc4dadbfa1acc6f4f25a530798bec7d16
admission_review_id = event_type_initial_admission_review_v0_1_20260724T111500Z
admission_status = accepted_with_restrictions
```

Calendar authority:

```text
source_table = 001_market_calendar
data_foundation_conclusion = PROVEN_RESTRICTED_DATASET
calendar_version = governed_exchange_session_calendar_xnys_v0_1
calendar_binding_run_id = governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z
calendar_source_snapshot_fingerprint = 8b43cda89c1da0dc78e618e46f20697a2832bd13ca7599e60989f01b701ce967
bound_parquet_sha256 = 79a458a3585011ecec7d8153b78f8564834b24c1fb95d3718c6f4d1fea63bc00
timezone_authority = America/New_York
exchange_scope = XNYS
```

## 2. Canonical Grain

Native Event Instance grain:

```text
event_type_id
+ exchange_id
+ session_date
+ calendar_version
+ event_anchor_timestamp_utc
```

For `session_opened`, this means one native Event Instance per governed
exchange-session opening occurrence.

It does not mean one native instance per instrument.

## 3. Event Instance ID

The future executable binding must derive `event_instance_id` deterministically
from canonical key material:

```text
sha256(
    namespace
    + event_type_id
    + event_type_definition_hash
    + event_subject_scope
    + exchange_id
    + session_date
    + event_anchor_timestamp_utc
    + calendar_version
    + calendar_row_fingerprint
)
```

Required namespace:

```text
tsis_event_instance_v0_1
```

Determinism rule:

```text
same governed exchange-session occurrence
under the same registry and calendar authority
    -> same event_instance_id
```

Correction rule:

```text
changed calendar authority,
corrected open timestamp,
or changed calendar_row_fingerprint
    -> version or supersession,
       never silent overwrite
```

## 4. Timestamp Policy

```text
event_anchor_timestamp_utc
    = session_open_utc from governed calendar row

first_observable_timestamp_utc
    = calendar authority may make the scheduled open knowable before occurrence
      but the event occurrence cannot be true before event_anchor_timestamp_utc

detection_timestamp_utc
    = not_applicable_for_calendar_authority_v0_1

binding_created_at_utc
    = required only when a future execution creates a registry or dataset row
```

Forbidden equivalences:

```text
event_anchor_timestamp_utc != first_observed_trade_timestamp
calendar knowledge timestamp != event occurrence timestamp
```

## 5. Source Lineage

Future execution must preserve at least:

```text
calendar_authority_id
calendar_version
calendar_source_snapshot_fingerprint
bound_calendar_parquet_sha256
calendar_row_fingerprint
source_dataset_contract
timezone_authority
exchange_id
session_date
session_open_utc
session_close_utc
session_type
is_early_close
```

## 6. Instrument Projection Boundary

Native `session_opened` identity excludes:

```text
instrument_id
ticker
listing status
first trade timestamp
instrument halt state
tradability
execution capacity
```

Future instrument-level use must be represented as an association/projection:

```text
exchange_session Event Instance
    -> instrument_session_projection
    -> instrument context
```

One exchange-session Event Instance may be associated with many
instrument-session contexts. That association must not change the native
`event_instance_id`.

An instrument halted at the open does not invalidate the exchange-session
event. That fact belongs to future instrument projection, Market State, Event
State or Execution State policy.

## 7. Exceptional Cases

```text
weekends = no governed session row, no instance
holidays = no governed session row, no instance
holiday absence inference = not an Event Instance
early close = does not change open anchor; keep calendar lineage
DST transition = resolved only by governed calendar authority
delayed exchange opening = not admitted unless encoded by governed authority or a future Event Type
exceptional closure = governed calendar correction/supersession policy applies
non-XNYS = not authorized by v0.1
```

## 8. Supersession

Future executable bindings must include:

```text
event_instance_version
supersedes_event_instance_id
superseded_by_event_instance_id
correction_reason
authority_snapshot_hash
supersession_created_at_utc
```

Silent timestamp overwrite is prohibited.

## 9. Non-Executable Example

This is an illustrative contract example only. It is not a registered instance.

```text
event_type_id = event_type:market_data:session_opened
exchange_id = XNYS
session_date = 2026-07-24
calendar_version = governed_exchange_session_calendar_xnys_v0_1
event_anchor_timestamp_utc = <session_open_utc_from_governed_calendar>
event_instance_id = sha256(tsis_event_instance_v0_1|...)
```

## 10. Closed Boundaries

```text
event_instance_binding_execution_authorized = false
event_instances_created = 0
historical_calendar_rows_consumed = 0
physical_parquet_reads_allowed = false
detector_execution_authorized = false
instrument_projection_execution_authorized = false
event_window_binding_execution_authorized = false
market_state_physical_consumption_authorized = false
event_state_builder_execution_authorized = false
event_state_materialization_authorized = false
downstream_consumption_authorized = false
production_authorized = false
```

## 11. Next Gate

The next recommended gate is:

```text
event_window_binding_design_authorization_v0_1
```

Before Event Instance Binding Execution, TSIS should also close:

```text
market_state_profile_compatibility_design_authorization_v0_1
```
