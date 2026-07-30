## Recovery Entry

The canonical cold-start entry for this boundary is:

```text
../STATE_PROVIDER_CONSUMER_RECOVERY.md
```

It defines the current authority, accepted packages, reading order, next owner
and prohibitions. Historical closure sections below do not override it.

## Market State Restriction Domain Binding Closed

```text
market_state_restriction_domain_binding_clarification_v0_1
=
CLOSED_PASS_RESTRICTION_DOMAINS_DISAMBIGUATED_FOR_BT_GATE_014_NO_PHYSICAL_READ_NO_CONSUMER_AUTHORIZATION

physical provenance domain = 26 codes observed per V0.4 row
bounded replay-consumption domain = 4 required codes
component replay domain = 4 required core-four components
case_count = 19
failed_cases = 0
V0.4 = consumed, not reusable
V0.5 = not authorized
```

Physical `restriction_codes_json` is fingerprinted provenance lineage.
Sidecar and component restrictions govern bounded replay consumption. They are
distinct labeled domains and must not be compared for equality or silently
merged into one executable policy.

The next owner is BT-GATE-014. It must adopt the binding in its consumer
contract and implementation before proposing a new single-use authorization.

## BT-GATE-014 Contract Handoff Ready

```text
schema/runtime binding = CLOSED_PASS
structural schema authority = PHYSICAL_SCHEMA_CONTRACT.json
profile provenance hash = b1841f4897...
current bounded runtime content hash = bc033cb2cd...
BT-GATE-014 provider evidence handoff = COMPLETE
backtester current-gate authority = 02_TSIS_BACKTEST_ENGINE/AGENTS.md
active provider gate = none
```

Use `market_state_pit_bt_gate_014_handoff_v0_1.md` and
`market_state_core_four_scale_validation_physical_schema_binding_v0_1.json`.
The provider evidence delivered temporal envelopes, not a typed 17-value
backtester payload.

## Bounded Market State Physical Read and Replay Review Closed

```text
execution = CLOSED_PASS_ONE_BOUNDED_MARKET_STATE_PHYSICAL_READ_AND_REPLAY_PROBE_WITH_RESTRICTIONS
review = CLOSED_PASS_BOUNDED_MARKET_STATE_PHYSICAL_READ_AND_REPLAY_REVIEW_WITH_RESTRICTIONS_READY_FOR_BT_GATE_014_HANDOFF
authorization_single_use_consumed = true
input_files_verified = 9
physical_data_files_opened = 1
physical_state_rows_read = 2
bounded_probe_records_emitted = 2
early_delivered_records = 0
unlisted_rows_delivered = 0
strategy_callbacks = 0
orders = 0
fills = 0
PnL = false
next_handoff = BT-GATE-014_POINT_IN_TIME_MARKET_STATE_CONSUMPTION_EVIDENCE_READY
general_StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

The provider/shared-boundary work required for the first PIT Market State
consumer handoff is complete. The next decision belongs to the backtester gate
owner; Event State and general replay remain closed.

## Bounded StateBundle Read and Replay Authorization v0.2 Closed

```text
bounded_state_bundle_read_and_replay_authorization_v0_2
=
CLOSED_AUTHORIZED_ONE_BOUNDED_MARKET_STATE_READ_AND_REPLAY_PROBE_WITH_RESTRICTIONS_NO_EXECUTION

authorization_to_read_issued = true
bounded_execution_authorized = true
current_boundary_gate = bounded_state_bundle_read_and_replay_execution_v0_1_pending
authorized_instrument = ACIU
authorized_session = 2021-03-15
authorized_row_count = 2
maximum_rows = 2
parquet_opened = false
physical_state_rows_read = 0
general_StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

The active authorization is `v0.2`; blocked authorization `v0.1` remains
historical evidence. The next gate may open only the exact frozen candidate
parquet and deliver only the two frozen row identities to a bounded integration
probe.

## StateBundle Physical Evidence Alignment v0.2 Closed

```text
state_bundle_manifest_physical_evidence_alignment_v0_2
=
CLOSED_PASS_PHYSICAL_EVIDENCE_ALIGNED_READY_FOR_BOUNDED_READ_AUTHORIZATION_WITH_RESTRICTIONS_NO_PHYSICAL_READ

case_count = 22
blocking_findings = 0
restricted_findings = 2
physical_read_authorization_ready = true
authorization_to_read_issued = false
current_boundary_gate = bounded_state_bundle_read_and_replay_authorization_v0_1_pending
parquet_opened = false
physical_state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
```

The aligned evidence identifies one exact restricted Market State scale-validation candidate and preserves partial coverage. This gate does not grant physical-read authority.

## Scale Validation Replay Availability Sidecar Active

```text
market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1 = CLOSED_PASS_SCALE_VALIDATION_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_CREATED_AND_VALIDATED_WITH_RESTRICTIONS_NO_PHYSICAL_READ
sidecar_candidate_dataset_id = market_state_candidate_dataset_scale_validation_v0_1_516a27d0f8f53762
sidecar_records = 104
parquet_opened = false
state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
```

## Runtime Interface Regression Closed With Replay Availability Evidence

```text
upstream_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
upstream_status = CLOSED_PASS_V0_1_2_BOUNDED_INTERFACE_EXECUTION_REGRESSION_WITH_RESTRICTIONS_NO_CONSUMPTION
current_boundary_gate = state_bundle_manifest_physical_evidence_alignment_v0_1_pending
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED
```

The row-addressable replay availability sidecar is now available. Physical evidence alignment is the next gate and still must not open StateReplayFeed or backtest consumption.

## Market State Core Four Replay Availability Evidence Sidecar Execution v0.1

```text
market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1 = CLOSED_PASS_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_CREATED_AND_VALIDATED_WITH_RESTRICTIONS_NO_PHYSICAL_READ
current_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_pending
sidecar_records_written = 8
parquet_opened = false
state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
```

The sidecar binds each validated core-four physical candidate row to replay availability timestamps and restrictions. It is not downstream authorization.

## Market State Core Four Replay Availability Evidence Sidecar Authorization v0.1

```text
market_state_core_four_replay_availability_evidence_sidecar_authorization_v0_1 = CLOSED_AUTHORIZED_REPLAY_AVAILABILITY_EVIDENCE_SIDECAR_EXECUTION_AND_VALIDATION_WITH_RESTRICTIONS_NO_PHYSICAL_READ
current_gate = market_state_core_four_replay_availability_evidence_sidecar_execution_and_validation_v0_1_pending
sidecar_records_written = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
```

The next execution-and-validation gate must produce the row-addressable replay availability sidecar or block fail-closed.

## Runtime Interface Regression Blocked On Replay Availability Evidence

```text
upstream_gate = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
upstream_status = CLOSED_BLOCKED_REQUIRES_ROW_ADDRESSABLE_REPLAY_AVAILABILITY_EVIDENCE_NO_PHYSICAL_READ
current_boundary_gate = market_state_core_four_replay_availability_evidence_sidecar_authorization_v0_1_pending
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED
```

Before repeating physical evidence alignment, TSIS must create or authorize a sidecar/envelope that binds each physical Market State core-four row identity to `state_as_of_utc`, `state_available_at_utc`, component availability evidence and restrictions.

## Historical Snapshot - Market State Core Four Replay Availability Timestamp Contract Validation Hardened

```text
market_state_core_four_replay_availability_timestamp_contract_v0_1
=
CLOSED_CONTRACT_READY_WITH_VALIDATION_HARDENED_RESTRICTIONS_NO_PHYSICAL_READ

case_count = 30
failed_cases = 0
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED

Current gate at timestamp contract closure = runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_pending
```

The contract now closes the semantic-enforcement gap found by external review. It remains a contract-only gate and does not authorize physical StateBundle reads.

## Market State Core Four Replay Availability Timestamp Contract v0.1

```text
market_state_core_four_replay_availability_timestamp_contract_v0_1 = CLOSED_CONTRACT_READY_WITH_VALIDATION_HARDENED_RESTRICTIONS_NO_PHYSICAL_READ
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED
```

Required next gate at timestamp contract closure:

```text
runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
```

After that gate reissues v0.1.2 response/bundle evidence, repeat physical evidence alignment before any bounded read-and-replay authorization.

## StateBundle Manifest Physical Evidence Alignment v0.1

```text
state_bundle_manifest_physical_evidence_alignment_v0_1 = CLOSED_BLOCKED_REQUIRES_V0_1_2_BUNDLE_REISSUE_AND_REPLAY_TIMESTAMP_EVIDENCE_NO_PHYSICAL_READ
physical_read_authorization_ready = false
StateReplayFeed = NOT_AUTHORIZED
```

Required next gates:

```text
market_state_core_four_replay_availability_timestamp_contract_v0_1
runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
```

# 09_STATE_CONSUMPTION_BOUNDARY

Status: `runtime_interface_regression_blocked_on_replay_availability_evidence`
Date: `2026-07-29`
Current gate: `market_state_core_four_replay_availability_evidence_sidecar_authorization_v0_1_pending`
Last closed gate: `runtime_user_invocation_bounded_interface_execution_regression_v0_1_2`

This folder records the shared boundary between the TSIS State Provider control-plane and future state consumers.

It is not the State Provider runtime itself and it is not the Backtest Engine implementation. It defines when a governed `StateBundleManifest` reference may be physically opened by an explicitly authorized consumer.

## Boundary

```text
Provider
=
validates, resolves, builds/reuses and references StateBundles
```

```text
Consumption Boundary
=
authorizes bounded physical opening of an exact StateBundle
```

```text
Consumer
=
reads, types, orders and replays records under its own implementation contracts
```

## Current Status

```text
state_bundle_physical_consumption_authorization_design_v0_1
=
CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_PHYSICAL_READ
```

Still closed:

```text
state_bundle_rows_read = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_strategy_execution = false
orders = 0
fills = 0
PnL = false
production = false
downstream = false
official_dataset = false
```

## Next Boundary At Prior Closure

```text
state_bundle_manifest_physical_evidence_alignment_v0_1
```

That gate has since closed blocked. The current required next gates are:

```text
market_state_core_four_replay_availability_timestamp_contract_v0_1
runtime_user_invocation_bounded_interface_execution_regression_v0_1_2
```

They must not read rows, implement the Backtest Engine or execute a strategy.

## StateBundle Reader and Replay Contract Design v0.1

```text
state_bundle_reader_and_replay_contract_design_v0_1
=
CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION
```

The reader and replay contracts are designed but not executed. `StateReplayFeed` remains unauthorized for runtime execution until a later bounded read-and-replay authorization.

## Provider Consumer Data-Plane Joint Review v0.1

```text
provider_consumer_data_plane_joint_review_v0_1
=
CLOSED_APPROVED_FOR_BOUNDED_STATE_BUNDLE_READ_AND_REPLAY_AUTHORIZATION_WITH_RESTRICTIONS_NO_EXECUTION
```

The next gate at joint-review closure was permitted to authorize one bounded read-and-replay probe. It still did not execute the probe.


## Bounded StateBundle Read and Replay Authorization v0.1

```text
bounded_state_bundle_read_and_replay_authorization_v0_1
=
CLOSED_BLOCKED_BEFORE_PHYSICAL_READ
```

No physical read authorization was issued. The attempted provider `StateBundleManifest` reference remains control-plane evidence only because dataset identity, response hash linkage, physical artifact hashes and replay-safe availability evidence are not yet sufficiently aligned for bounded row delivery.

Next corrective gate at bounded authorization closure:

```text
state_bundle_manifest_physical_evidence_alignment_v0_1
```
