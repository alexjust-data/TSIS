# Market State Run Lifecycle And Manifest Design v0.1

Status: `CLOSED_DESIGN_READY_WITH_RESTRICTIONS_NO_EXECUTION`
Date: `2026-07-25`
Parent Gate: `market_state_candidate_dataset_registry_design_v0_1`

This document defines the future Market State on-demand run lifecycle and
manifest model.

It is design-only. It does not create run records, write manifests, write
heartbeats, transition run states, consume execution authorizations, consume
execution plans, execute materializers, execute validators, write registry
entries, read source data, write datasets, promote datasets, authorize
production or authorize downstream consumption.

## 1. Lifecycle Principle

```text
Market State Run Lifecycle
    = the future governance layer that records how one on-demand run starts,
      transitions, heartbeats, closes, fails, recovers and emits immutable
      manifests.
```

A run is not a dataset.

```text
run
    = execution attempt and evidence trail

candidate dataset
    = registered output artifact after materialization and validation
```

The lifecycle must not collapse these identities.

## 2. Runtime Position

```text
Request
    ↓
Execution Plan
    ↓
Run Lifecycle
    ↓
Materializer
    ↓
Validator
    ↓
Candidate Dataset Registry
```

The lifecycle coordinates future execution evidence. It does not replace the
contracts of the materializer, validator or registry.

## 3. Run Identity

A future run must have a stable, unique identity:

```text
run_id
run_kind
run_contract_version
request_id
request_fingerprint
execution_plan_id
execution_plan_fingerprint
authorization_id
created_at_utc
```

The `run_id` must not be derived only from an output path or machine name.

The run must also record:

```text
runner_identity
runtime_environment_id
code_version_or_commit
working_root
configured_output_root
```

## 4. Run State Model

Closed status set:

```text
planned
authorized
initialized
running
materializing
validating
registering_candidate
closed_pass
closed_pass_with_restrictions
blocked
failed
quarantined
cancelled
superseded
abandoned
```

No implementation may introduce ad hoc statuses without a contract update.

## 5. Allowed Transitions

For v0.1 design:

```text
planned -> authorized
authorized -> initialized
initialized -> running
running -> materializing
materializing -> validating
validating -> registering_candidate
registering_candidate -> closed_pass
registering_candidate -> closed_pass_with_restrictions
```

Failure or interruption transitions:

```text
planned -> blocked
authorized -> blocked
initialized -> failed
running -> failed
materializing -> failed
validating -> failed
registering_candidate -> failed
any_non_terminal -> cancelled
any_non_terminal -> abandoned
any_non_terminal -> quarantined
```

Supersession:

```text
closed_pass -> superseded
closed_pass_with_restrictions -> superseded
failed -> superseded
quarantined -> superseded
```

The lifecycle must record transition authority and reason.

## 6. Required Manifest Types

Future lifecycle execution must support:

```text
pre_run_manifest.json
run_manifest.json
heartbeat.jsonl
materializer_manifest_ref
validator_manifest_ref
candidate_registry_entry_ref
failure_manifest.json
recovery_manifest.json
final_manifest.json
run_readout.md
```

This design gate creates none of these artifacts.

## 7. Pre-Run Manifest

The future `pre_run_manifest.json` must record:

```text
run_id
request_fingerprint
execution_plan_fingerprint
authorization_id
authorized_scope
quantitative_limits
expected_materializer_contract
expected_validator_contract
expected_registry_contract
output_roots
heartbeat_policy
restart_policy
```

It must exist before future source reads or output writes.

## 8. Heartbeat Policy

A future run must emit heartbeat records while active.

Each heartbeat must include:

```text
run_id
heartbeat_timestamp_utc
current_run_status
current_step
last_completed_partition
records_emitted_so_far
blocked_contexts_so_far
quarantined_contexts_so_far
current_output_root
process_id_or_worker_id
```

Heartbeat records are runtime evidence. They are not validation results and not
dataset registry entries.

## 9. Final Manifest

The future `final_manifest.json` must record:

```text
run_id
final_run_status
request_fingerprint
execution_plan_fingerprint
materializer_run_manifest_ref
candidate_output_manifest_ref
lineage_manifest_ref
validation_result_fingerprint
candidate_dataset_registry_entry_ref
registry_entry_fingerprint
started_at_utc
ended_at_utc
duration_seconds
requested_partition_count
materialized_partition_count
blocked_partition_count
quarantined_partition_count
not_built_partition_count
final_findings
next_allowed_gate
```

The final manifest must be immutable after closure.

## 10. Failure Manifest

If a future run fails, it must emit:

```text
failure_manifest.json
```

with:

```text
run_id
failed_status
failure_timestamp_utc
failure_stage
failure_reason_code
failure_message
last_successful_checkpoint
artifacts_written_before_failure
safe_to_resume
safe_to_delete_staging
required_remediation_gate
```

Failure must not be represented only by logs.

## 11. Recovery Manifest

If a future interrupted run is resumed, recovery must be explicit:

```text
recovery_manifest.json
```

with:

```text
original_run_id
recovery_run_id
recovery_authorization_id
last_certified_checkpoint
partitions_reused
partitions_rebuilt
staging_cleanup_actions
reason_for_recovery
```

This design does not authorize recovery execution.

## 12. Idempotency And Restartability

The lifecycle must preserve:

```text
same request_fingerprint
+ same execution_plan_fingerprint
+ same authorized contracts
    =
same run intent
```

But a new `run_id` may exist for a rerun or recovery attempt.

The lifecycle must distinguish:

```text
same intent
```

from:

```text
same execution attempt
```

## 13. Authorization Consumption

A future execution authorization must be consumed exactly once by a run unless
the authorization explicitly permits retry semantics.

The lifecycle must record:

```text
authorization_id
authorization_status_before_run
authorization_consumed_at_utc
authorization_consumption_result
```

This design gate consumes no execution authorization.

## 14. Blocking Rules

A future run must block before execution when:

```text
run_id_missing
request_fingerprint_missing
execution_plan_fingerprint_missing
execution_plan_not_authorized
authorization_missing
authorization_already_consumed_without_retry_policy
pre_run_manifest_missing
quantitative_limits_missing
output_root_authority_missing
heartbeat_policy_missing
restart_policy_missing
materializer_contract_missing
validator_contract_missing
candidate_dataset_registry_contract_missing
invalid_run_state_transition
final_manifest_missing_for_closed_status
failure_manifest_missing_for_failed_status
recovery_manifest_missing_for_recovered_attempt
```

## 15. Closed Boundaries

This design gate records:

```text
run_records_created = 0
run_manifests_created = 0
final_manifests_created = 0
heartbeat_records_written = 0
run_state_transitions = 0
recovery_actions = 0
execution_authorizations_consumed = 0
execution_plans_consumed = 0
materializer_executions = 0
validator_executions = 0
registry_entries_written = 0
datasets_written = 0
official_dataset = false
production = false
downstream = false
```

## 16. Next Gate

```text
next_allowed_gate =
market_state_on_demand_execution_chain_joint_review_v0_1
```

That gate may review the coherence of the full design chain before bounded
execution authorization. It must not be treated as already open by this
document.
