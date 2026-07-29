# Event State On-Demand Incremental Lineage Chain Validation Readout v0.1

Status: `CLOSED_PASS_EVENT_STATE_INCREMENTAL_LINEAGE_CHAIN_VALIDATED_WITH_RESTRICTIONS_NO_PROMOTION`
Date: `2026-07-28`

```text
validation_id = event_state_on_demand_incremental_lineage_chain_validation_v0_1_20260728T000000Z
validation_run_id = event_state_on_demand_incremental_lineage_chain_validation_v0_1_20260728T112448Z
source_review = event_state_on_demand_second_generation_incremental_extension_candidate_dataset_review_v0_1_20260728T110845Z
validation_decision = lineage_chain_validated_with_restrictions
requested_contexts = 15
represented_contexts = 14
baseline_origin_rows = 8
delta1_origin_rows = 3
delta2_origin_rows = 3
unavailable_contexts = 1
unaccounted_contexts = 0
duplicate_canonical_contexts = 0
missing_parent_refs = 0
row_identity_mismatches = 0
hard_validation_failures = 0
official_dataset = false
production = false
downstream = false
next_allowed_gate = event_state_on_demand_scale_validation_v0_1
```

The lineage chain is accepted only as bounded Event State runtime evidence. The
validation proves that generation 2 is a governed composition of immutable
baseline, delta1 and delta2 evidence, with the inherited unavailable context
preserved and no promotion or downstream authority opened.
