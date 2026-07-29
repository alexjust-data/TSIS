# runtime_provider_contract_schema_hardening_readout_v0_1

Status: `CLOSED_SCHEMA_HARDENED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-28`
Gate: `runtime_provider_contract_schema_hardening_v0_1`
Owner layer: `08_RUNTIME_CAPABILITIES`

## Reason

A provider-consumer compatibility preflight found that the provider documentation was coherent, but the provider JSON Schemas did not yet enforce the fail-closed semantics described by the documents.

## Hardened contracts

```text
state_resolution_request_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
```

Specialized request contracts are now required package authorities:

```text
market_state_request_contract_v0_1.json
event_state_request_contract_v0_1.json
```

## Corrections made

```text
StateResolutionRequest links request_type to the matching payload.
payload is type object with additionalProperties=false.
Market and Event payload shapes reject unexpected physical path fields.
RuntimeInvocationResponse ties invocation_status to resolution_decision and allowed refs.
blocked responses cannot return dataset ids or artifact references.
reuse_hit responses require a StateBundleManifest reference.
StateBundleManifest requires capability refs, request refs, dataset refs, artifact hashes and explicit cardinality.
StateBundleManifest supports an aggregate bundle for market_and_event requests.
Coverage arithmetic is declared as mandatory code validation where JSON Schema is insufficient.
Contract hash canonicalization policy is declared in hardened contracts.
```

## Validation evidence

```text
validation_matrix = runtime_provider_contract_schema_hardening_validation_matrix_v0_1.json
case_count = 10
failed_cases = 0
schema_validator = jsonschema.Draft202012Validator
```

## Institutional result

```text
PACKAGE_INTEGRITY = PASS
PROVIDER_BOUNDARY = PASS
PROVIDER_INTERFACE_DOCUMENTATION = CLOSED
PROVIDER_SCHEMA_STRICT_VALIDATION = HARDENED_PENDING_COMPATIBILITY_REVIEW
FAIL_CLOSED_SEMANTICS = HARDENED_PENDING_COMPATIBILITY_REVIEW
PROVIDER_CONSUMER_COMPATIBILITY = READY_FOR_REVIEW_NOT_VALIDATED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
```

## What remains closed

```text
runtime_executions = 0
market_state_requests_created = 0
event_state_requests_created = 0
state_bundle_manifests_created = 0
datasets_written = 0
registry_mutations = 0
backtest_runs_created = 0
StateReplayFeed_opened = false
official_dataset = false
production = false
downstream = false
```

## Next gate

```text
runtime_provider_consumer_contract_compatibility_review_v0_1
```

This next review may now rerun against hardened provider schemas. It must still keep the backtest consumer contracts in DRAFT unless field-by-field compatibility passes and separate backtest consumption authority is established.
