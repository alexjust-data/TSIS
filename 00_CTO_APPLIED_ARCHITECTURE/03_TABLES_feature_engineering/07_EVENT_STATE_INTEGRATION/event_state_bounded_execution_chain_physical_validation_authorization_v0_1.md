# Event State Bounded Execution Chain Physical Validation Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-24`

This document authorizes a bounded physical validation of the accepted Event
State bounded execution-chain candidate run only.

Accepted execution run under validation:

```text
event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z
```

Accepted physical validation run:

```text
event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z
```

```text
reconciliation_status = CLOSED_PASS_WITH_RESTRICTIONS
accepted_as_closure_evidence = true
```

The authorized validator may read the run-local candidate outputs, manifests,
reports and referenced source hashes needed to verify the physical evidence.
It may not create new Event Types, create new Event Instances outside the
accepted run evidence, read unbounded Market State, materialize official Event
State parquet, promote a dataset, enable production, or authorize downstream
consumption.

## Scope

```text
validation_scope =
    accepted bounded execution-chain candidate output only

event_type_id =
    event_type:market_data:session_opened

subject_scope =
    exchange_session

expected_requested_contexts = 9
expected_event_state_candidate_records = 8
expected_blocked_contexts = 1
expected_missing_exact_market_state_bindings = 1
expected_event_state_parquet_files_written = 0
```

The candidate source remains non-official evidence:

```text
source_market_state_semantic_profile_id =
    market_state_core_four_intraday_profile_v0_1

source_market_state_physical_profile_id =
    core_four_market_state_profile_v0_1

source_market_state_candidate_parquet_sha256 =
    b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2
```

## Required Checks

The validation must verify:

```text
artifact existence and SHA-256 hashes
candidate JSONL parseability
required schema fields
record id uniqueness
record fingerprint reproducibility
event instance / window / projection / Market State binding reconciliation
exact-one Market State binding policy
blocked context preservation
native Event Instance identity does not use instrument_id
event anchor equals governed session open
event anchor equals decision timestamp for at_open rows
state_role and consumption_legality are present and independent fields
lineage JSON is parseable and complete
source Market State value snapshot JSON is parseable
no fallback rows admitted
no partial Event State records emitted
no Event State parquet files written
official profile promotion = false
official dataset promotion = false
production = false
downstream consumption = false
determinism evidence remains valid
```

## Allowed Outputs

```text
pre_manifest.json
heartbeat.json
schema_validation_report.json
record_fingerprint_validation_report.csv
binding_reconciliation_report.csv
lineage_validation_report.json
authority_boundary_report.json
determinism_validation_report.json
physical_validation_report.json
final_manifest.json
event_state_bounded_execution_chain_physical_validation_readout_v0_1.md
```

All outputs are validation evidence only.

## Closure Criteria

The gate may close as:

```text
CLOSED_PASS_WITH_RESTRICTIONS
```

only if:

```text
hard_validation_failures = 0
schema_failures = 0
hash_failures = 0
record_fingerprint_failures = 0
binding_reconciliation_failures = 0
lineage_failures = 0
authority_failures = 0
determinism_failures = 0
unexpected_parquet_outputs = 0
```

The accepted restriction is:

```text
one context remains blocked by exact Market State binding policy
```

That restriction is expected and does not constitute a hard failure.

## Closed Boundaries

```text
new_event_type_admission = false
event_detection_execution = false
unbounded_event_instance_binding_execution = false
unbounded_event_window_binding_execution = false
unbounded_market_state_consumption = false
event_state_materialization = false
official_event_state_profile_promotion = false
official_event_state_dataset_promotion = false
production = false
downstream_consumption = false
```

## Next Gate If Closed

```text
event_state_candidate_dataset_review_v0_1
```
