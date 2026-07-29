# runtime_user_invocation_interface_design_v0_1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-28`
Gate: `runtime_user_invocation_interface_v0_1`
Owner layer: `08_RUNTIME_CAPABILITIES`

## Purpose

This document defines the provider-side control plane for asking TSIS for governed Market State or Event State references.

It does not define the backtester, does not open StateReplayFeed, does not deliver table rows, and does not authorize downstream consumption.

## Institutional placement

```text
08_RUNTIME_CAPABILITIES
=
state provider
```

```text
Backtest RunPreflight
=
first expected institutional consumer
```

The provider receives a normalized state request, validates it, resolves effective runtime capability permissions, checks registry metadata where policy allows it, and returns a governed response or a `StateBundleManifest` reference.

## Canonical flow

```text
StateResolutionRequest
-> Runtime User Invocation Interface
-> Runtime Capability Effective View
-> Runtime Invocation Response
-> StateBundleManifest, when a governed bundle reference exists
```

The consumer-side continuation is outside this folder:

```text
BacktestRunSpec
-> RunPreflight
-> BacktestInputManifest
-> StateReplayFeed
-> EventLoop
```

## Request hierarchy

```text
StateResolutionRequest
=
common provider envelope
```

```text
market_state_request
=
specialized Market State payload governed by market_state_request_contract_v0_1.json
```

```text
event_state_request
=
specialized Event State payload governed by event_state_request_contract_v0_1.json
```

The common envelope is not a third scientific request authority. It owns routing, validation mode, reuse policy and consumer intent; the specialized payload owns Market State or Event State semantics.

## Effective capability view

The interface must not infer current permissions directly from old historical manifests alone.

It must derive an effective view from:

```text
promotion/readout/manifest evidence
+
current consumption policy
```

This resolves two issues:

```text
Market State had no symmetric runtime capability manifest in the review package.
Event State had a historical manifest created before the consumption policy enabled governed reuse.
```

The design therefore introduces:

```text
runtime_capability_effective_view_contract_v0_1.json
runtime_capability_registry_snapshot_v0_1.json
```

The snapshot is metadata authority only. It does not authorize row delivery, production or downstream consumption.

## Interface decisions

The interface returns closed decision codes:

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

## Allowed design-time operations

```text
request_validation_allowed = true
request_normalization_allowed = true
request_fingerprint_creation_allowed = true
registry_metadata_lookup_allowed = true
exact_reuse_resolution_allowed_under_policy = true
```

## Closed operations

```text
new_candidate_execution_allowed_without_authorization = false
physical_path_input_allowed = false
physical_row_delivery_allowed = false
official_dataset_delivery_allowed = false
downstream_data_delivery_allowed = false
backtest_consumption_authority = false
```

## Response model

The interface response uses one common envelope:

```text
RuntimeInvocationResponse
```

with optional specialized detail blocks:

```text
market_state_details
event_state_details
```

This prevents the consumer from interpreting Market State and Event State runtime manifests directly as incompatible APIs.

## StateBundleManifest boundary

`StateBundleManifest` is provider-owned. It may be referenced by a future `BacktestInputManifest`, but the backtester must not redefine its schema.

A `StateBundleManifest` may seal:

```text
request_fingerprint
capability references
candidate dataset references
coverage
validation status
restrictions
artifact hashes
field lineage
temporal policy
```

It must not deliver physical rows under this gate.

## Closure status

```text
PROVIDER_BOUNDARY = PASS
PROVIDER_INTERFACE_CONTRACTS = CLOSED
PROVIDER_CONSUMER_COMPATIBILITY = READY_FOR_REVIEW_NOT_VALIDATED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
DOWNSTREAM_STATE_CONSUMPTION = NOT_AUTHORIZED
```

## Next gate

```text
runtime_provider_consumer_contract_compatibility_review_v0_1
```

That gate must compare these provider contracts against the backtest consumer draft contracts field by field. It must not execute a backtest or open StateReplayFeed.