# StateBundle Reader and Replay Contract Design v0.1

Gate: `state_bundle_reader_and_replay_contract_design_v0_1`
Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`

## Purpose

This design defines the consumer-side data-plane contracts needed after a bounded StateBundle physical consumption authorization exists.

It combines two responsibilities while keeping them separate internally:

```text
StateBundleReader
=
opens exact authorized evidence, verifies it and returns typed state records
```

```text
StateReplayFeed
=
orders typed records by legal availability and exposes StateAvailable events to a clock owner
```

## Ownership

```text
EventLoop = simulated clock authority
StateReplayFeed = next eligible state event provider
StateBundleReader = bounded evidence reader
MarketDataFeed = market observations, not state representations
Execution Simulator = orders/fills/costs, not state representation
```

## StateBundleReader Requirements

The reader must verify before row delivery:

```text
physical consumption authorization status
bundle_id exact match
manifest fingerprint exact match
artifact hash exact match
schema fingerprint exact match
profile_id exact match
state_kind exact match
coverage ledger present
restriction propagation present
row/file/byte limits
no user supplied physical path
```

It must block before row delivery if any verification fails.

It must not:

```text
resolve another bundle
modify files
repair records
calculate features
reinterpret columns
change restrictions
emit replay events
emit strategy signals
```

## Typed State Record Minimum

Every typed record delivered by the reader to replay must expose:

```text
state_record_id
state_kind
profile_id
dataset_id
bundle_id
instrument_id or subject_id
session_date
decision_timestamp
state_as_of_utc
state_available_at_utc
content_fingerprint
lineage_ref
restriction_codes
consumption_legality
payload
```

For Event State records, additional event fields must remain visible:

```text
event_type_id
event_instance_id
event_timestamp
event_detected_at
event_available_at
```

## StateReplayFeed Requirements

The feed must not own the clock. It exposes the next eligible record to the EventLoop.

Eligibility rule:

```text
event_loop.clock >= state_available_at_utc
```

Canonical ordering:

```text
state_available_at_utc
state_kind_priority
instrument_id_or_subject_id
session_date
state_record_id
```

The feed must emit no record early and must not emit duplicates.

## StateReplayFeed Event

A future `StateAvailable` event must include:

```text
state_event_id
state_kind
state_record_id
profile_id
instrument_id or subject_id
decision_timestamp
state_as_of_utc
state_available_at_utc
bundle_id
dataset_id
consumption_legality
restriction_codes
payload_reference_or_typed_payload
```

## Non-Execution Rule

The first vertical slice must emit no strategy callbacks, orders, fills or PnL.

```text
StateReplayFeed != MarketDataFeed
Market State != execution price source
Event State != retrospective event permission
```

## Next Gate

```text
provider_consumer_data_plane_joint_review_v0_1
```
