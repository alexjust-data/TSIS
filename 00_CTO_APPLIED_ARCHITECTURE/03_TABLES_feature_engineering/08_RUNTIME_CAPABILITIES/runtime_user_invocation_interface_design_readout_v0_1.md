# runtime_user_invocation_interface_design_readout_v0_1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-28`
Gate: `runtime_user_invocation_interface_v0_1`
Owner layer: `08_RUNTIME_CAPABILITIES`

## Closure

The provider-side runtime user invocation interface is now formally designed as a control-plane protocol, not as a free execution or downstream data-delivery interface.

Closed design and provider contracts:

```text
runtime_user_invocation_interface_design_v0_1.md
runtime_capability_registry_snapshot_v0_1.json
```

Closed provider contracts:

```text
state_resolution_request_contract_v0_1.json
runtime_user_invocation_interface_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
runtime_capability_effective_view_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
```

## Canonical hierarchy

```text
StateResolutionRequest
=
common provider envelope
```

```text
market_state_request / event_state_request
=
specialized provider payloads governed by their existing request contracts
```

```text
BacktestRunSpec / BacktestInputManifest
=
consumer-owned contracts outside 08_RUNTIME_CAPABILITIES
```

## Interface decisions

```text
VALID_REQUEST_REUSE_HIT
VALID_REQUEST_EXECUTION_AUTHORIZATION_REQUIRED
VALID_REQUEST_AUTHORIZED_EXECUTION_REFERENCE
BLOCKED_INVALID_REQUEST
BLOCKED_UNSUPPORTED_PROFILE_OR_EVENT_TYPE
BLOCKED_PRODUCTION_OR_DOWNSTREAM_NOT_AUTHORIZED
BLOCKED_PHYSICAL_PATH_NOT_ALLOWED
BLOCKED_PROVIDER_CONTRACT_MISMATCH
```

## Institutional status

```text
PROVIDER_BOUNDARY = PASS
PROVIDER_INTERFACE_CONTRACTS = CLOSED
PROVIDER_CONSUMER_COMPATIBILITY = READY_FOR_REVIEW_NOT_VALIDATED
DOWNSTREAM_STATE_CONSUMPTION = NOT_AUTHORIZED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
```

The backtest consumer draft contracts should remain in:

```text
PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
```

until a future provider-consumer compatibility review validates them against these provider contracts and examples.

## What this gate authorizes

```text
request validation design
request normalization design
request fingerprint design
capability effective-view design
registry metadata lookup design
reuse-hit response design
execution-authorization-required response design
StateBundleManifest contract design
```

## What remains closed

```text
interface_invocations = 0
market_state_requests_created = 0
event_state_requests_created = 0
runtime_executions = 0
state_bundle_manifests_created = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream = false
backtest_consumption_authority = false
physical_row_delivery = false
```

## Next gate

```text
runtime_provider_consumer_contract_compatibility_review_v0_1
```

This next gate must compare the provider contracts with the backtest consumer draft contracts field-by-field and decide whether the consumer contracts can leave DRAFT status. It must not execute a backtest and must not authorize StateReplayFeed consumption.