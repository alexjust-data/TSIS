# Runtime State Provider Boundary v0.1

Status: `CLOSED_BOUNDARY_CLARIFIED_NO_EXECUTION`
Date: `2026-07-28`
Owner layer: `08_RUNTIME_CAPABILITIES`
Next gate: `runtime_user_invocation_interface_v0_1`

## Purpose

This document formalizes the provider-side boundary for TSIS state runtimes before designing the common runtime invocation interface.

The goal is to prevent one recurring ambiguity:

```text
Backtest Engine asks for states
```

must not become:

```text
Backtest Engine owns state construction,
state contracts,
state registry lookup,
or physical state delivery policy.
```

The provider boundary is:

```text
08_RUNTIME_CAPABILITIES
=
provider side for Market State and Event State runtime capabilities.
```

The first expected consumer is:

```text
Backtest RunPreflight
```

but the provider contract must remain reusable by future institutional consumers.

## Canonical Boundary

```text
State Runtime Provider
=
validates and resolves governed state requests,
consults capability and registry authority,
and returns governed state references/manifests.
```

```text
Backtest Engine
=
declares what a backtest needs,
fails closed in RunPreflight,
seals BacktestInputManifest,
and delivers legal states through StateReplayFeed.
```

The link between them is not a physical path and not a strategy-level join.

It is:

```text
BacktestRunSpec
-> RunPreflight
-> StateResolutionRequest
-> State Runtime Interface
-> StateBundleManifest / InvocationResponse
-> BacktestInputManifest
-> StateReplayFeed
-> EventLoop
```

## Provider-Owned Objects

The provider owns the contracts that define how state capabilities are requested and answered:

```text
runtime_user_invocation_interface_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
runtime_capability_effective_view_contract_v0_1.json
state_resolution_request_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
market_state_request_contract_v0_1.json
event_state_request_contract_v0_1.json
```

The provider may validate and normalize a state request, compute fingerprints, resolve effective capability permissions, inspect registry metadata, and return a governed manifest/reference.

The provider does not decide strategy behavior, fills, position accounting, or backtest pass/fail policy beyond its own response status and restrictions.

## Consumer-Owned Objects

The backtest consumer owns:

```text
BacktestRunSpec
BacktestInputManifest
RunPreflight pass/fail decision
StateReplayFeed temporal delivery
EventLoop delivery order
execution price policy
orders, fills, positions and ledger
```

These belong under the backtest architecture and implementation roots:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/04_STATE.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/contracts/backtest/
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/src/
```

The backtester must not copy or redefine `StateBundleManifest`. It must reference the provider-owned contract by id, version and hash.

## Meaning of User Invocation

In `runtime_user_invocation_interface_v0_1`, the word `user` means:

```text
institutional consumer module
```

not necessarily a human and not a free-form parquet requester.

For v0.1, the primary concrete consumer is:

```text
Backtest RunPreflight
```

Therefore the interface is a control plane:

```text
validate request
normalize request
compute fingerprint
resolve capability and policy
perform registry metadata lookup
return governed response
```

It is not a data plane:

```text
no raw rows
no free parquet delivery
no unrestricted execution
no production
no downstream/backtest/ML/RL consumption authority
```

## Current Capability Limits

The provider currently exposes only restricted candidate runtime capabilities:

```text
Market State runtime
= promoted with restrictions
= candidate generation / governed reuse only
= no official dataset
= no production
= no downstream
```

```text
Event State runtime
= promoted with restrictions
= session_opened / exchange_session only
= candidate generation / governed reuse only
= no official dataset
= no production
= no downstream
```

`halt_resumed` remains outside Event State runtime invocation v0.1.


## Normalized Request Contract Hierarchy

The provider contract hierarchy is:

```text
StateResolutionRequest
=
common provider envelope
```

```text
market_state_request
=
specialized Market State payload
```

```text
event_state_request
=
specialized Event State payload
```

Therefore:

```text
state_resolution_request_contract_v0_1.json
```

must wrap or reference specialized payloads governed by:

```text
market_state_request_contract_v0_1.json
event_state_request_contract_v0_1.json
```

The three contracts must not become competing authorities for the same request semantics.

## Provider-Consumer Compatibility Status

The boundary is closed, but protocol compatibility is not yet validated.

```text
PROVIDER_BOUNDARY = PASS
CONSUMER_ARCHITECTURE_ALIGNMENT = PASS
PROVIDER_INTERFACE_CONTRACTS = PENDING
PROVIDER_CONSUMER_COMPATIBILITY = NOT_YET_VALIDATED
DOWNSTREAM_STATE_CONSUMPTION = NOT_AUTHORIZED
```

Compatibility can be claimed only after `runtime_user_invocation_interface_v0_1` closes with contract ids, versions and SHA-256 for:

```text
state_resolution_request_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
runtime_user_invocation_interface_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
runtime_capability_effective_view_contract_v0_1.json
```
## Implication for the Next Gate

`runtime_user_invocation_interface_v0_1` must design the provider-side invocation interface.

It must not create backtest contracts and must not implement `StateReplayFeed`.

The correct split is:

```text
08_RUNTIME_CAPABILITIES
-> provider contracts and response envelope
```

```text
02_TSIS_BACKTEST_ENGINE
-> consumer contracts, preflight, replay and event-loop integration
```

## Closed Counters

This boundary clarification authorizes no execution:

```text
interface_invocations = 0
market_state_requests_created = 0
event_state_requests_created = 0
runtime_executions = 0
materializer_executions = 0
validator_executions = 0
source_market_data_rows_read = 0
candidate_dataset_rows_read = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream = false
```
