# Event State Capability Consumption Policy Readout v0.1

Status: `CLOSED_PASS_EVENT_STATE_CAPABILITY_CONSUMPTION_POLICY_ESTABLISHED_WITH_RESTRICTIONS_NO_DATASET_PROMOTION`
Date: `2026-07-28`

```text
policy_id = event_state_capability_consumption_policy_v0_1_20260728T135626Z
capability_id = event_state_on_demand_runtime_capability_v0_1
policy_status = ESTABLISHED_WITH_RESTRICTIONS_CANDIDATE_RUNTIME_ONLY
allowed_event_type_ids = ['event_type:market_data:session_opened']
accepted_subject_scope = exchange_session
hard_policy_failures = 0
official_event_state_dataset = false
production = false
downstream = false
source_market_data_rows_read = 0
new_materializer_executions = 0
new_registry_entries_written = 0
next_allowed_gate = runtime_user_invocation_interface_v0_1
```

The Event State on-demand runtime capability is now consumable only as a
restricted candidate-runtime capability. This policy does not authorize official
datasets, production, downstream consumption, additional Event Types or
unbounded generation.
