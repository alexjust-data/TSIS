# runtime_user_invocation_interface_design_authorization_v0_1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-28`
Gate: `runtime_user_invocation_interface_v0_1`
Owner layer: `08_RUNTIME_CAPABILITIES`

## Purpose

This authorization opens design only for the TSIS provider-side invocation interface that receives state requests from institutional consumers and returns governed references, decisions and manifests.

It formalizes the provider side of:

```text
StateResolutionRequest
-> Runtime User Invocation Interface
-> Effective Capability View
-> Runtime Invocation Response
-> StateBundleManifest
```

The first expected consumer is Backtest RunPreflight, but this gate does not implement the backtester and does not authorize downstream state consumption.

## Authorized design outputs

```text
state_resolution_request_contract_v0_1.json
runtime_user_invocation_interface_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
runtime_capability_effective_view_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
runtime_user_invocation_interface_design_readout_v0_1.md
```

## Hard boundaries

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

## Required institutional separation

```text
StateResolutionRequest = common provider envelope
market_state_request = specialized Market State payload
event_state_request = specialized Event State payload
BacktestRunSpec = consumer-owned object, outside this folder
BacktestInputManifest = consumer-owned object, outside this folder
```

## Closure condition

The gate may close only if the provider-side contracts define:

```text
valid request -> governed response
invalid request -> fail-closed rejection
Market State payload -> specialized validation boundary
Event State payload -> specialized validation boundary
success response -> StateBundleManifest reference or reuse decision
restricted response -> explicit restrictions
failed response -> no dataset and no downstream authority
contract_id + version + SHA-256 for each provider contract
```