# StateBundle Physical Consumption Authorization Design v0.1

Gate: `state_bundle_physical_consumption_authorization_design_v0_1`
Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_PHYSICAL_READ`

## Purpose

This design defines the shared boundary that allows a future consumer to physically open an exact governed `StateBundleManifest` under bounded authorization.

It exists because the State Provider control-plane can now return governed references, but physical row delivery remains closed until a separate authorization proves scope, hashes, temporal legality and restriction propagation.

## Ownership

```text
State Provider
=
produce, validate and reference bundles
```

```text
State Consumption Boundary
=
authorize exact bounded physical opening
```

```text
Consumer / data-plane
=
read, type, order and replay records under its own contracts
```

This gate does not move `StateBundleReader`, `StateReplayFeed` or `EventLoop` into provider ownership.

## Required Authorization Fields

A future physical consumption authorization must freeze:

```text
consumer_id
consumer_type
consumption_purpose
authorized_state_kind
authorized_profile_id
authorized_bundle_id
authorized_bundle_manifest_fingerprint
authorized_dataset_id
authorized_dataset_fingerprint
RuntimeInvocationResponse reference
StateBundleManifest reference
allowed_artifact_fingerprints
allowed_file_count
allowed_row_count
allowed_byte_count
authorized_instruments
authorized_sessions
coverage_policy
temporal_legality_policy
restriction_propagation_policy
failure_policy
```

## First Vertical Slice

The first physical-consumption proof should use:

```text
state_kind = market_state
profile_id = market_state_core_four_intraday_profile_v0_1
event_state_requested = false
scope = 1 instrument x 1 session
consumer_id = bounded_backtest_state_integration_probe_v0_1
consumption_purpose = bounded_provider_consumer_integration_validation
```

It must keep:

```text
strategy_execution = false
orders = 0
fills = 0
PnL = false
production = false
downstream = false
official_dataset = false
```

## Temporal Legality

Physical consumption is not decision-safe unless each delivered record has a demonstrable:

```text
decision_timestamp
state_as_of_utc
state_available_at_utc
```

Definitions:

```text
decision_timestamp = market instant represented by the state
state_as_of_utc = maximum source-information timestamp used by the state
state_available_at_utc = first historical instant at which the complete state could legally be known by the consumer
```

The replay eligibility rule is:

```text
event_loop.clock >= state_available_at_utc
```

Not merely:

```text
event_loop.clock >= decision_timestamp
```

`state_available_at_utc` is not the retrospective parquet creation timestamp.

## Must Block

A physical consumption authorization must fail closed before row delivery when:

```text
bundle_id does not match authorization
manifest fingerprint mismatch
artifact hash mismatch
schema fingerprint mismatch
profile mismatch
state_kind mismatch
coverage ledger absent
unavailable contexts omitted
restriction propagation missing
row count exceeds authorization
file count exceeds authorization
user supplied physical path appears
state_available_at_utc not demonstrable
downstream or production requested
strategy execution requested
orders/fills requested
```

## Non-Goals

This design does not authorize:

```text
StateBundleReader execution
StateReplayFeed execution
Backtest Engine execution
MarketDataFeed substitution
Execution Simulator behavior
strategy callbacks
orders
fills
PnL
new State builds
new Event Types
Liquidity or other profile extensions
production
downstream
```

## Invariant

```text
StateBundle physical consumption authorization
permits bounded opening of exact governed evidence.

It does not make the StateBundle official,
downstream-consumable or usable as an execution-price source.
```
