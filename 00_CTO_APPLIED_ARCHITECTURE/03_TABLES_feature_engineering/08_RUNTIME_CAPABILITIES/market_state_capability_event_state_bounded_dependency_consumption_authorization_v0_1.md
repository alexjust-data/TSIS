# Market State Capability Event State Bounded Dependency Consumption Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-27`
Scope: `first_event_state_on_demand_bounded_execution_dependency_only`

## Purpose

This authorization creates a bounded exception to the Market State capability consumption policy for the next gate only:

```text
event_state_on_demand_bounded_execution_v0_1
```

It does not modify `market_state_capability_consumption_policy_v0_1` in place. The policy remains the general rule. This artifact authorizes only the specific Market State dependency needed by the first bounded Event State on-demand execution.

## Authorized Consumer

```text
consumer_gate = event_state_on_demand_bounded_execution_v0_1
consumer_profile_id = event_state_core_four_intraday_profile_v0_1
consumer_event_type_id = event_type:market_data:session_opened
consumer_subject_scope = exchange_session
```

## Authorized Market State Dependency

```text
market_state_runtime_capability_id = market_state_on_demand_runtime_capability_v0_1
market_state_profile_id = market_state_core_four_intraday_profile_v0_1
market_state_profile_version = v0_1
maximum_market_state_dependency_contexts = 9
```

Scope:

```text
exchange_scope = XNYS
session_dates = 2021-01-19, 2021-03-15, 2022-11-25
instrument_ids = figi_share_class:BBG001S5N8T1, figi_share_class:BBG001S8T7K0, figi_share_class:BBG001S6RSK0
```

## Allowed Operations In The Next Gate Only

```text
resolve_market_state_dependency_request_through_runtime_capability = true
lookup_candidate_registry_metadata = true
reuse_exact_validated_candidate_for_matching_dependency_request = true
read_fingerprint_matched_candidate_records_for_event_state_materializer = true
```

## Still Prohibited

```text
direct_market_state_path_consumption = false
read_unmatched_candidate_records = false
open_new_market_state_candidate_execution_without_separate_authorization = false
serve_as_official_market_state_dataset = false
production = false
downstream = false
ML_RL_training = false
full_universe_access = false
```

## Blocking Conditions

```text
scope_exceeds_9_dependency_contexts
consumer_gate_not_event_state_on_demand_bounded_execution_v0_1
event_type_not_session_opened
subject_scope_not_exchange_session
market_state_profile_not_core_four_intraday_v0_1
dependency_request_fingerprint_missing
candidate_dataset_fingerprint_missing_or_mismatch
candidate_artifact_unavailable
direct_market_state_path_requested
official_or_production_or_downstream_consumption_requested
```

## Boundary

This authorization only allows bounded dependency consumption. It does not promote a Market State dataset, does not promote an Event State dataset, does not authorize generalized Event State on-demand execution, and does not authorize downstream consumption.

## Scope File

```text
configs/market_state_capability_event_state_bounded_dependency_consumption_scope_v0_1.json
```
