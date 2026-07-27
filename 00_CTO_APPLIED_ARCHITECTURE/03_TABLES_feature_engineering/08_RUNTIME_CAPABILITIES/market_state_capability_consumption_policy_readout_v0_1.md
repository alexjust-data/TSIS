# Market State Capability Consumption Policy Readout v0.1

Status: `CLOSED_PASS_CAPABILITY_CONSUMPTION_POLICY_ESTABLISHED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION`
Date: `2026-07-27`

```text
policy_id = market_state_capability_consumption_policy_v0_1_20260727T142133Z
capability_status_required = PROMOTED_WITH_RESTRICTIONS_CANDIDATE_GENERATION_ONLY
consumption_policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
hard_policy_failures = 0
allowed_candidate_generation = separate_authorization_required
allowed_exact_reuse = conditional_candidate_runtime_only
allowed_incremental_reuse = conditional_candidate_runtime_only
official_dataset = false
production = false
downstream = false
source_market_data_rows_read = 0
parquet_content_rows_read = 0
materializer_executions = 0
validator_executions = 0
new_candidate_registry_entries_written = 0
datasets_written = 0
next_allowed_gate = event_state_on_demand_capability_design_authorization_v0_1
```

The promoted Market State on-demand runtime capability now has an explicit
consumption policy. The policy allows metadata inspection and candidate-runtime
reuse under strict fingerprint, lineage, validation and availability conditions.
It does not authorize official dataset consumption, production or downstream
use.
