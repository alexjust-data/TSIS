# Market State Core Four Replay Availability Timestamp Contract v0.1

Gate: `market_state_core_four_replay_availability_timestamp_contract_v0_1`
Status: `CLOSED_CONTRACT_READY_WITH_VALIDATION_HARDENED_RESTRICTIONS_NO_PHYSICAL_READ`
Owner layer: `09_STATE_CONSUMPTION_BOUNDARY`
Date: `2026-07-29`
Scope: `contract_only_no_physical_read`

## Purpose

This contract defines the timestamp evidence required before the bounded `Market State core-four` candidate can be represented as replay-safe state records for a future consumer.

It closes the timestamp blocker from `state_bundle_manifest_physical_evidence_alignment_v0_1`:

```text
ALIGN_REPLAY_TIMESTAMPS_SCHEMA_001
```

It does not authorize physical reads, replay, backtest, production or downstream consumption.

## Target Profile

```text
state_kind = market_state
profile_id = market_state_core_four_intraday_profile_v0_1
logical_profile_id = core_four_market_state_profile_v0_1
required_information_objects = trading_activity, price_movement, price_location_structure, volatility_range_state
Event State requested = false
```

This contract does not add Liquidity, Market Microstructure State, Order Flow Pressure, News/Catalyst, Fundamental, Short-Side, Broad Market or Halt Context. It does not reopen the ontology and does not modify the core-four scientific payload.

## Timestamp Definitions

```text
decision_timestamp_utc
=
market instant represented by the Market State row.
```

```text
state_as_of_utc
=
maximum source-information timestamp incorporated into the complete emitted state row.
```

```text
state_available_at_utc
=
first historical instant at which the complete state row could legally be delivered to a consumer.
```

`state_available_at_utc` is delivery metadata. It is not a scientific feature and not a new Information Object.

It must not be derived from:

```text
parquet_created_at
runtime_invocation_created_at
bundle_created_at
file_modified_at
human review timestamp
```

## Core Formula

For an emitted replay-safe core-four Market State row:

```text
state_as_of_utc
=
max(component_as_of_utc for all admitted required components and objects)
```

```text
state_available_at_utc
=
max(
    decision_timestamp_utc,
    component_available_at_utc for all admitted required components and objects
)
+ governed_state_publication_latency
```

For v0.1 bounded replay validation, `governed_state_publication_latency` may be `PT0S` only if explicitly declared as:

```text
zero_latency_candidate_replay_publication_policy_v0_1
```

Any non-zero policy must be represented as an ISO-8601 duration and carried in the bundle evidence.

## Validation Enforcement

The contract is enforced through both layers:

```text
JSON Schema validation
+
semantic validation
```

The semantic validator must fail closed unless all of these hold:

```text
all four required Information Objects are represented at least once;
source_timestamp_utc <= component_as_of_utc <= decision_timestamp_utc;
component_as_of_utc <= component_available_at_utc <= state_available_at_utc;
state_as_of_utc = max(component_as_of_utc);
state_available_at_utc = max(decision_timestamp_utc, component_available_at_utc) + governed_state_publication_latency;
PT0S uses zero_latency_candidate_replay_publication_policy_v0_1;
decision_safe rows have state_availability_status = available_for_decision_replay;
decision_safe rows have all required components availability_status = available;
row restriction_codes include the union of component restriction_codes;
all *_utc values use canonical Z representation.
```

A consistent `research_only` row may remain evidence, but it is not replay-deliverable.

## Required Evidence Per Row

A future v0.1.2 `StateBundleManifest` or physical record envelope must expose:

```text
decision_timestamp_utc
state_as_of_utc
state_available_at_utc
state_availability_policy_id
state_publication_latency_policy_id
state_publication_latency
state_replay_consumption_legality
state_availability_status
component_availability_evidence
```

Each `component_availability_evidence` entry must expose:

```text
component_id
information_object_id
source_timestamp_utc
component_as_of_utc
component_available_at_utc
cutoff_rule_id
availability_rule_id
availability_status
restriction_codes
```

The four required Information Objects may share component evidence, but the shared evidence must remain explicitly linked to all admitted object ids.

## Legal Ordering Rules

```text
source_timestamp_utc <= component_as_of_utc
component_as_of_utc <= decision_timestamp_utc
component_as_of_utc <= component_available_at_utc
component_available_at_utc <= state_available_at_utc
state_as_of_utc <= state_available_at_utc
decision_timestamp_utc <= state_available_at_utc
```

Future replay delivery rule:

```text
event_loop.clock >= state_available_at_utc
```

A consumer must not use:

```text
event_loop.clock >= decision_timestamp_utc
```

as sufficient delivery eligibility.

## Fail-Closed Conditions

A future physical alignment or read authorization must block if any of these is true:

```text
state_as_of_utc missing
state_available_at_utc missing
state_available_at_utc derived from materialization time
state_available_at_utc < decision_timestamp_utc
state_as_of_utc > decision_timestamp_utc
component_as_of_utc > decision_timestamp_utc
component_available_at_utc missing for required object
publication latency policy missing
state_replay_consumption_legality missing
state_replay_consumption_legality != decision_safe for replay delivery
required object missing or blocked
restriction propagation missing
all required Information Objects not represented
component research_only or blocked while row is decision_safe
state availability status contradicts replay legality
publication latency not included in state_available_at_utc
PT0S used without the zero-latency candidate replay policy
non-canonical UTC timestamp representation
invalid or misordered publication latency duration
```

## Consumption Legality

Allowed row-level legality values:

```text
decision_safe
research_only
blocked_missing_availability_evidence
blocked_temporal_leakage
blocked_required_object_missing
blocked_restriction_propagation_missing
```

Only `decision_safe` can reach future replay delivery. `research_only` may remain in evidence, but it must not be emitted to strategy-facing replay.

## Boundary With Execution

```text
Market State = decision information
MarketDataFeed = market observation stream
Execution Simulator = fills, costs, slippage and capacity
```

No field from this contract can be used as an execution price source. Even if a core-four value numerically equals a bar close, fill pricing remains governed by a separate execution-price policy.

## Boundary With Current Work

This contract prepares the missing timestamp evidence required before repeating physical evidence alignment. It does not itself reissue a v0.1.2 response/bundle. That remains the job of:

```text
runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
```

## Acceptance Criteria

```text
contract_json_parse = PASS
json_schema_compile = PASS
json_schema_fixture_validation = PASS
semantic_matrix = PASS
physical_artifacts_opened = 0
state_rows_read = 0
StateReplayFeed_records_emitted = 0
runtime_requests_executed = 0
runtime_builds_executed = 0
production = false
downstream = false
official_dataset = false
```
