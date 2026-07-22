# Short Context Table Validators `v0_1`

## 1. Scope

This validator contract governs:

```text
short_context_table_v0_1
```

## 2. Required Inputs

Required governed sources:

- `E:/TSIS/data/short`
- `E:/TSIS/data/short_review/finra_short`
- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_certification_by_ticker.csv`
- `E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet`

## 3. Hard Validation Checks

The build must fail if:

- `short_context_id` is duplicated;
- any output row is `bad_*`;
- output row count is zero;
- the manifest `output_tree` does not match the parquet tree.

Duplicate source keys are not hard failures. They must be preserved and flagged
because FINRA short volume v0.1 contains known duplicate `ticker + date` keys.

## 4. Required Quality Checks

The validator must emit:

- row count;
- ticker count;
- instrument count;
- first and last `observation_date`;
- source-system counts;
- observation-family counts;
- source/family row counts;
- `short_quality_state` distribution;
- local certification status distribution;
- duplicate-key row count;
- duplicate-key excess row count;
- FINRA short-volume duplicate-key excess rows;
- consumer-gate row counts.

## 5. Required Consumer Gates

Every row must satisfy:

```text
valid_for_rl_training_direct = false
full_universe_claim = false
full_2005_2026_official_free_history_claim = false
execution_truth = false
borrow_data_present = false
ssr_data_present = false
requires_availability_lag_assumption = true
same_day_intraday_causal_claim_allowed = false
prohibited_without_asof_filter = true
contains_future_information_without_event_filter = true
```

Rows may have `valid_for_event_context_candidate = true` only when:

```text
source_duplicate_key_flag = false
instrument_identity_temporal_match = true
```

Local rows also require `local_certification_status` in:

```text
CERTIFIED_OK
CERTIFIED_OK_WITH_LIMITED_WINDOW
```

## 6. Current Expected v0.1 Counts

```text
rows: 7145337
tickers: 4694
instruments: 4462
parquet_files: 32
duplicate_key_rows: 6074
duplicate_key_excess_rows: 5250
finra_short_volume_duplicate_key_excess_rows: 5250
bad_rows: 0
valid_for_event_context_candidate_rows: 5240433
valid_for_ml_feature_candidate_rows: 5080027
valid_for_state_component_candidate_rows: 5240433
valid_for_rl_training_direct_rows: 0
```

Rows by source/family:

```text
finra_official_free:short_interest = 505745
finra_official_free:short_volume = 4689038
local_polygon:short_interest = 520048
local_polygon:short_volume = 1430506
```

Quality:

```text
good_finra_official_free_short_interest_context: 306856
good_finra_official_free_short_volume_context: 4528387
good_local_certified_short_interest_context: 130656
good_local_certified_short_volume_context: 114128
review_finra_pre_2021_short_interest_semantics: 160406
review_local_certification_status: 1705770
review_no_temporal_identity: 193060
review_source_duplicate_key: 6074
```

## 7. Test Evidence

The pytest contract is:

```text
tests/data_foundation_outputs/test_short_context_table_contract.py
```

Evidence must be written under:

```text
C:/TSIS_Data/tests/test_runs/<date>/data_foundation_outputs_short_context_table_v0_1/
```
