# Experimental Core Four Market State Scale B Candidate Physical Validation Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-23`
Scope: `scale_b_candidate_parquet_independent_validation_only`

This authorization documents the bounded independent physical validation gate
for the Scale B candidate parquet produced by `experimental_scale_b_ms_candidate_materialization_v0_1_20260723T144955Z`.

The validation uses the same materialization scope as its physical contract:

```text
configs/experimental_core_four_market_state_scale_b_candidate_materialization_scope_v0_1.json
```

Authorized execution:

```text
gate = experimental_core_four_market_state_scale_b_candidate_physical_validation
source_materialization_run = experimental_scale_b_ms_candidate_materialization_v0_1_20260723T144955Z
accepted_validation_run = core_four_market_state_candidate_physical_validation_v0_1_20260723T145049Z
```

Authority boundary:

```text
source_market_data_rows_read = 0
parquet_rewrite_allowed = false
official_market_state_allowed = false
production_builder_allowed = false
downstream_consumption_allowed = false
dataset_promotion_allowed = false
full_history_execution_allowed = false
full_universe_execution_allowed = false
```

Expected closure:

```text
input_candidate_records = 64
output_physical_rows = 64
candidate_parquet_files = 1
value_mappings_checked = 1088
hard_validation_failures = 0
```
