# 05 RUNPREFLIGHT STATE CONSUMPTION IMPLEMENTATION PLAN V0.1

Status: PROPOSED_CONSUMER_CONTRACT_NOT_INTEGRATION_VALIDATED
Date: 2026-07-28
Scope: consumer side of the governed `Market State` / `Event State` interface.

This is not the architectural authority for state consumption.

The authority belongs to:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/04_STATE.md
```

The provider contracts belong to:

```text
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/
03_TABLES_feature_engineering/
08_RUNTIME_CAPABILITIES/
```

This document defines the smallest implementation increment required inside:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

## 1. Objective

Extend the current `RunPreflight` so one `BacktestRunSpec` can:

```text
declare ordinary market-data requirements
declare optional Market State requirements
declare optional Event State requirements
project the data section into RunDataRequest
project each requested state into StateResolutionRequest
invoke the governed State Runtime Interface
validate each RuntimeInvocationResponse
validate the EffectiveCapabilityView used by resolution
validate the aggregated StateBundleManifest
validate separate backtest-consumption authorization
emit one sealed BacktestInputManifest
fail closed before any feed opens
```

The integration boundary is:

```text
BacktestRunSpec
↓
RunPreflight
├── RunDataRequest
└── StateResolutionRequest, if required
        ↓
State Runtime Interface
        ↓
RuntimeInvocationResponse, one per request
        ↓
EffectiveCapabilityView + aggregated StateBundleManifest
        ↓
Backtest-consumption authorization
↓
BacktestInputManifest
```

## 2. Current Baseline

Already implemented and verified:

```text
RunDataRequest
RunPreflight
data_preflight_report.json
data_manifest.json
universe_manifest.json
HistoricalReplayFeed
MechanicalEventLoop
AccountingEngine
61 tests OK
```

This increment must evolve that chain.

It must not replace it with a parallel preflight system.

## 3. Consumer Contracts

Canonical executable contracts:

```text
contracts/backtest/
├── backtest_run_spec_contract_v0_1.json
└── backtest_input_manifest_contract_v0_1.json
```

The relationship with the current code is:

```text
BacktestRunSpec
├── data_request
│   └── projected into RunDataRequest
├── state_consumption, optional
│   └── projected into StateResolutionRequest
├── replay_policy
├── decision_policy
├── execution_policy
└── accounting_policy
```

`RunDataRequest` remains the internal data projection.

It is not the complete run specification.

## 4. Provider Dependencies

This implementation consumes but does not own:

```text
state_resolution_request_contract_v0_1.json
state_bundle_manifest_contract_v0_1.json
runtime_user_invocation_interface_contract_v0_1.json
runtime_user_invocation_response_contract_v0_1.json
runtime_capability_effective_view_contract_v0_1.json
market_state_request_contract_v0_1.json, when Market State is requested
event_state_request_contract_v0_1.json, when Event State is requested
```

Before integration can be marked `PASS`, `RunPreflight` must bind the exact:

```text
contract_id
contract_version
contract_sha256
```

for all five common protocol contracts and every specialized payload contract actually used.

```text
StateResolutionRequest
RuntimeUserInvocationInterface
RuntimeInvocationResponse
StateBundleManifest
RuntimeCapabilityEffectiveView
MarketStateRequest, if used
EventStateRequest, if used
```

Current provider status reviewed on 2026-07-28:

```text
portable strict schema compilation = pending final hardening
adversarial fail-closed validation = pending final hardening
full protocol hash reproducibility = pending final hardening
provider/consumer compatibility = not validated
backtest consumption = not authorized
StateReplayFeed = not authorized
```

Until those conditions pass:

```text
consumer contract drafting = allowed
consumer unit tests with fakes = allowed
provider compatibility claim = prohibited
downstream state consumption = prohibited
```

## 5. Files To Create Or Extend

```text
contracts/backtest/
├── backtest_run_spec_contract_v0_1.json
└── backtest_input_manifest_contract_v0_1.json

src/tsis_backtest/preflight/
├── backtest_run_spec.py
├── state_runtime_client.py
├── state_manifest_validator.py
├── backtest_input_manifest.py
└── run_preflight.py

tests/unit/
├── test_backtest_run_spec.py
├── test_state_preflight.py
└── test_backtest_input_manifest.py
```

Names under `src/` may be adjusted to the existing module style, but the responsibilities must remain separate.

## 6. `BacktestRunSpec` Resolution

Resolution order:

```text
1. Validate BacktestRunSpec against its JSON contract.
2. Validate run_id and output containment.
3. Project data_request into RunDataRequest.
4. Execute existing data preflight.
5. Stop if data preflight is not PASS.
6. If state_consumption is absent, skip State Runtime Interface.
7. If state_consumption exists, verify provider contract identities.
8. Seal the effective resolution_policy.
9. Produce exactly one normalized StateResolutionRequest per requested state_kind.
10. Invoke State Runtime Interface once per StateResolutionRequest.
11. Validate exactly one RuntimeInvocationResponse per request.
12. Validate the EffectiveCapabilityView used by the provider.
13. Validate one aggregated StateBundleManifest covering every request.
14. Prove one-to-one request/fingerprint/response correspondence.
15. Apply separate backtest-specific authorization checks.
16. Seal BacktestInputManifest.
17. Validate the generated manifest against its JSON contract and semantic validator.
18. Write it atomically.
```

No replay feed may open before step 18 completes.

The fixed cardinality is:

```text
Market State requested -> 1 StateResolutionRequest -> 1 RuntimeInvocationResponse
Event State requested  -> 1 StateResolutionRequest -> 1 RuntimeInvocationResponse

all successful requested state kinds
-> 1 aggregated StateBundleManifest
-> 1 BacktestInputManifest

partial success
-> prohibited
```

## 7. Optional State Semantics

The following runs are valid:

```text
market data only
market data + Market State
market data + Event State
market data + Market State + Event State
```

If `state_consumption` is absent:

```text
StateResolutionRequest = not produced
State Runtime Interface = not invoked
StateBundleManifest = not required
StateReplayFeed = NONE
```

If at least one state is requested:

```text
one StateResolutionRequest per state_kind = required
one RuntimeInvocationResponse per request = required
one EffectiveCapabilityView = required
one aggregated StateBundleManifest = required
separate backtest authorization = required
StateReplayFeed = required
```

Every consumer request carries a stable `consumer_request_id`. The generated manifest must preserve:

```text
consumer_request_id
↔
state_kind
↔
StateResolutionRequest artifact + SHA-256
↔
request_fingerprint
↔
RuntimeInvocationResponse artifact + SHA-256
↔
authorized state dataset
```

The semantic validator must reject duplicate IDs, duplicate fingerprints, repeated state kinds, missing correspondences or bundle coverage that differs from the complete requested set.

## 8. No Free Physical Paths

`BacktestRunSpec` may identify:

```text
dataset_id
universe_id
profile_id
representation_version
policy_id
contract_id
```

It may not identify:

```text
C:/...
G:/...
*.parquet
arbitrary file URI
arbitrary directory
```

Physical resolution belongs to governed registries and provider manifests.

The backtester may store local references to its own generated manifests, but it may not use those references to bypass registry resolution or hashes.

## 9. Backtest-Specific State Authorization

A provider response is necessary but not sufficient.

Before inspecting datasets, `RunPreflight` must also require:

```text
portable strict validation of every provider schema used
exact contract ID, version and SHA-256 for the complete protocol
EffectiveCapabilityView artifact available and hash-verified
one valid response per request
one aggregated bundle covering every request and no unrequested request
authorization artifact explicitly authorizing purpose = backtest
```

For every returned state dataset, `RunPreflight` must require:

```text
validation_status = PASS
official_dataset = true
downstream_authorized = true
consumption_purposes contains backtest
coverage_policy_satisfied = true
restrictions compatible with the run
profile_id exactly requested
representation_version exactly requested
state_kind exactly requested
required fields represented
required Information Objects represented
```

Materialization alone is insufficient:

```text
materialized
≠
authorized for backtest
```

Current experimental candidates carrying:

```text
official_dataset = false
production = false
downstream = false
```

must fail.

## 10. Temporal Authorization

For decision consumption, the effective rules must preserve:

```text
state_available_at <= decision_clock
feature_input_max_available_at <= decision_clock
future_window_used = false
outcome_dependency = false
```

For `Event State`, additionally:

```text
consumption_legality = decision_safe

max(
    event_detected_at,
    event_available_at,
    state_available_at
) <= decision_clock
```

`research_only`, `outcome_adjacent` and `prohibited_as_input` rows may exist in research datasets but may not be authorized for `StateReplayFeed` decision delivery.

## 11. `BacktestInputManifest`

This manifest is emitted only on:

```text
BACKTEST_INPUTS_PASS
```

It seals:

```text
BacktestRunSpec ref + SHA-256
data_preflight_report ref + SHA-256
data_manifest ref + SHA-256
universe_manifest ref + SHA-256
StateBundleManifest ref + SHA-256, if requested
all provider contract identities + versions + SHA-256
EffectiveCapabilityView ref + SHA-256
one request/fingerprint/response binding per requested state kind
sealed resolution_policy
separate backtest-authorization artifact + SHA-256
authorized state dataset summaries
state data artifact + SHA-256
state schema artifact + SHA-256
authorized Information Objects and fields
effective policies
input-integrity assertions
explicit claims and limitations
```

It does not duplicate the complete feature lineage.

It references:

```text
feature_lineage_manifest_id
feature_lineage_manifest_sha256
```

through the governed state bundle.

## 12. Failure Codes

Minimum new fail-closed outcomes:

```text
BACKTEST_RUN_SPEC_SCHEMA_INVALID
STATE_PROVIDER_CONTRACT_IDENTITY_MISSING
STATE_PROVIDER_CONTRACT_VERSION_MISMATCH
STATE_PROVIDER_CONTRACT_HASH_MISMATCH
STATE_RESOLUTION_REQUEST_INVALID
STATE_RUNTIME_UNAVAILABLE
STATE_RUNTIME_RESPONSE_INVALID
STATE_RUNTIME_RESPONSE_CARDINALITY_MISMATCH
STATE_EFFECTIVE_CAPABILITY_VIEW_INVALID
STATE_EFFECTIVE_CAPABILITY_VIEW_HASH_MISMATCH
STATE_BUNDLE_MANIFEST_SCHEMA_INVALID
STATE_BUNDLE_CARDINALITY_MISMATCH
STATE_BUNDLE_REQUEST_COVERAGE_MISMATCH
STATE_REQUEST_FINGERPRINT_MISMATCH
STATE_REQUEST_ID_DUPLICATE
STATE_REQUEST_FINGERPRINT_DUPLICATE
STATE_REQUEST_RESPONSE_BINDING_MISMATCH
STATE_KIND_MISMATCH
STATE_PROFILE_MISMATCH
STATE_REPRESENTATION_VERSION_MISMATCH
STATE_REQUIRED_FIELD_MISSING
STATE_REQUIRED_INFORMATION_OBJECT_MISSING
STATE_VALIDATION_NOT_PASS
STATE_OFFICIAL_DATASET_REQUIRED
STATE_DOWNSTREAM_NOT_AUTHORIZED
STATE_BACKTEST_PURPOSE_NOT_AUTHORIZED
STATE_BACKTEST_AUTHORIZATION_ARTIFACT_MISSING
STATE_BACKTEST_AUTHORIZATION_HASH_MISMATCH
STATE_RESTRICTIONS_INCOMPATIBLE
STATE_COVERAGE_POLICY_NOT_SATISFIED
STATE_TEMPORAL_POLICY_INCOMPATIBLE
BACKTEST_INPUT_MANIFEST_SCHEMA_INVALID
BACKTEST_INPUT_MANIFEST_HASH_FAILURE
```

On any failure:

```text
BACKTEST_INPUTS_FAIL
BacktestInputManifest is not emitted
HistoricalReplayFeed does not open
StateReplayFeed does not open
EventLoop does not start
```

## 13. Tests

Minimum synthetic tests:

```text
data-only run remains valid
Market State request produces one provider request
Event State request produces one provider request
both state kinds produce two normalized requests
free physical path is rejected
unknown provider contract identity is rejected
provider contract hash drift is rejected
missing specialized payload contract is rejected
invalid provider response schema is rejected
response count different from request count is rejected
duplicate request ID or fingerprint is rejected
request/fingerprint/response mismatch is rejected
effective capability view hash drift is rejected
aggregated bundle missing one request is rejected
aggregated bundle includes an unrequested request is rejected
partial success across requested state kinds is rejected
materialized but unofficial dataset is rejected
downstream_authorized=false is rejected
backtest absent from consumption purposes is rejected
coverage mismatch is rejected
restriction mismatch is rejected
profile or representation mismatch is rejected
research_only Event State is rejected
valid authorized bundle emits BacktestInputManifest
generated manifest is deterministic for fixed inputs/time
generated manifest validates against JSON Schema
state absence produces no states section
state presence requires StateReplayFeed
state presence requires all provider hash-chain assertions true
state presence requires compatibility and authorization claims true
```

Integration test after provider freeze:

```text
1 symbol
1 session
1 minimum Market State profile
Event State absent
1 official authorized StateBundleManifest
1 BacktestInputManifest
```

## 14. Done Criteria

Consumer-contract drafting is closed when:

```text
both JSON contracts parse
schema meta-validation passes
synthetic examples validate
negative examples fail as intended
implementation plan is reviewed
no provider-owned contract is copied or redefined
```

Consumer implementation is closed when:

```text
BacktestRunSpec projects into existing RunDataRequest
fake State Runtime tests pass
BacktestInputManifest is deterministic
all fail-closed tests pass
AGENTS.md and CHANGELOG.md are updated
```

Integration is closed only when:

```text
provider v0.1 contract identities are frozen
provider contracts compile under portable strict Draft 2020-12 validation
provider adversarial fail-closed matrix passes
all protocol hashes are reproducible
real StateResolutionRequest validates against provider schema
real RuntimeInvocationResponse validates against provider schema
real EffectiveCapabilityView validates and hashes correctly
real StateBundleManifest validates against provider schema
request/response/bundle cardinality and correspondence validate
separate backtest authorization validates
one official downstream-authorized state bundle exists
bounded end-to-end state consumption test passes
```

## 15. Explicit Non-Claims

This increment does not claim:

```text
official State dataset exists
State Runtime production readiness
provider/consumer compatibility before contract freeze
fill realism
broker-cost realism
short tradability
strategy edge
full 2005-2026 backtest readiness
```
