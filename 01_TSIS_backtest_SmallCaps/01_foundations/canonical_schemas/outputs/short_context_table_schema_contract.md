# Short Context Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
short_context_table_v0_1
```

`short_context_table` is a governed Data Foundation context/state component for
short-side pressure, short interest and short-sale volume context.

It is not quote data, not trade tape, not borrow availability, not SSR state,
not full consolidated market-wide shorting truth and not a direct RL training
dataset.

## 2. Logical Unit

Unit:

```text
one source-scoped short observation
```

Source planes:

- `local_polygon / short_interest`
- `local_polygon / short_volume`
- `finra_official_free / short_interest`
- `finra_official_free / short_volume`

Grain:

```text
source_system + observation_family + ticker + observation_date + source_duplicate_key_ordinal
```

Logical keys:

```text
short_interest: ticker + settlement_date + source_system
short_volume: ticker + trade_date + source_system
```

Duplicate source keys are preserved and flagged. They are not silently
collapsed.

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/short_context_table
```

Dataset:

```text
short_context_table_v0_1/
  source_system=<source_system>/
    observation_family=<short_interest|short_volume>/
      observation_year=<YYYY>/
```

Artifacts:

```text
_short_context_table_manifest_v0_1.json
_short_context_table_summary_v0_1.csv
```

Builder:

```text
scripts/materialize_short_context_table.py
```

## 4. Sources

Governed v0.1 sources:

```text
E:/TSIS/data/short
E:/TSIS/data/short_review/finra_short
```

Source contracts:

```text
01_foundations/contract_registry/dataset_contracts/short_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/short_review_dataset_contract_v0_1.md
```

FINRA is the official/free baseline and provenance layer. Local `short` is the
operational Polygon/local layer. The output keeps both layers separated by
`source_system`; it does not choose one silent winner.

## 5. Required Columns

Identity and lineage:

- `short_context_id`
- `ticker`
- `instrument_id`
- `source_dataset_id`
- `source_family`
- `source_system`
- `source_scope`
- `observation_family`
- `observation_date_type`
- `observation_date`
- `observation_year`
- `source_root`
- `source_file`
- `source_file_relative_path`
- `source_file_row_number`

Date/as-of fields:

- `settlement_date`
- `trade_date`
- `as_of_date`
- `as_of_semantics`

Short interest fields:

- `short_interest`
- `avg_daily_volume`
- `days_to_cover`

Short volume fields:

- `total_volume`
- `short_volume`
- `exempt_volume`
- `non_exempt_volume`
- `short_volume_ratio`
- `nyse_short_volume`
- `nyse_short_volume_exempt`
- `nasdaq_carteret_short_volume`
- `nasdaq_carteret_short_volume_exempt`
- `nasdaq_chicago_short_volume`
- `nasdaq_chicago_short_volume_exempt`
- `adf_short_volume`
- `adf_short_volume_exempt`
- `orf_short_volume`
- `orf_short_volume_exempt`

Certification and identity:

- `local_certification_status`
- `local_certification_reason`
- `local_certified_date_start`
- `local_certified_date_end`
- `local_entity_id_nunique`
- `local_panel_min_date`
- `local_panel_max_date`
- `local_observation_inside_certified_window`
- `instrument_master_ticker_present`
- `instrument_identity_temporal_match`
- `instrument_identity_state`
- `is_common_stock`
- `is_lt1b_operational`
- `lt1b_classification_1b`

`local_certification_*` is a ticker-level overlay from the local short
certification run. It is carried for comparison, but it only controls consumer
gates for `source_system = local_polygon`.

Source duplicate and source-scope flags:

- `source_duplicate_key_flag`
- `source_duplicate_key_count`
- `source_duplicate_key_ordinal`
- `source_duplicate_excess_row`
- `finra_official_free_baseline`
- `local_polygon_operational_source`
- `short_volume_source_scope_not_consolidated_market_wide`
- `finra_pre_modern_short_interest_semantics_flag`
- `finra_pre_official_free_short_volume_window_flag`
- `full_2005_2026_official_free_history_claim`
- `borrow_data_present`
- `ssr_data_present`
- `execution_truth`

Consumer gates:

- `requires_availability_lag_assumption`
- `same_day_intraday_causal_claim_allowed`
- `prohibited_without_asof_filter`
- `contains_future_information_without_event_filter`
- `short_quality_state`
- `valid_for_event_context_candidate`
- `valid_for_ml_feature_candidate`
- `valid_for_backtest_context_candidate`
- `valid_for_state_component_candidate`
- `valid_for_rl_training_direct`

Build lineage:

- `instrument_master_build_run_id`
- `instrument_master_schema_version`
- `full_universe_claim`
- `materialization_scope`
- `quality_policy_version`
- `schema_version`
- `build_run_id`
- `created_at_utc`

## 6. Quality States

Allowed `short_quality_state` values:

- `good_finra_official_free_short_interest_context`
- `good_finra_official_free_short_volume_context`
- `good_local_certified_short_interest_context`
- `good_local_certified_short_volume_context`
- `review_finra_pre_2021_short_interest_semantics`
- `review_local_certification_status`
- `review_local_missing_certification`
- `review_local_outside_certified_window`
- `review_no_temporal_identity`
- `review_source_duplicate_key`
- `review_unclassified_short_context`
- `bad_missing_ticker`
- `bad_missing_observation_date`
- `bad_missing_short_interest`
- `bad_missing_short_volume`
- `bad_missing_total_volume`

Primary context candidates require:

```text
valid_for_event_context_candidate = true
instrument_identity_temporal_match = true
source_duplicate_key_flag = false
```

For local rows, they also require:

```text
local_certification_status in (CERTIFIED_OK, CERTIFIED_OK_WITH_LIMITED_WINDOW)
local_observation_inside_certified_window = true or null window not applicable
```

## 7. Current Materialization

```text
build_run_id: short_context_table_v0_1_20260626T215417Z
rows: 7145337
tickers: 4694
instruments: 4462
parquet_files: 32
output_tree_sha256: 57c0abbdf6a1d4ef4d1ab6bd7ac326e2d57415645d7cd759605334334271652b
```

Source rows:

```text
finra_official_free short_interest: 505745
finra_official_free short_volume: 4689038
local_polygon short_interest: 520048
local_polygon short_volume: 1430506
```

Quality distribution:

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

Duplicate-key evidence:

```text
duplicate_key_rows: 6074
duplicate_key_excess_rows: 5250
finra_short_volume_duplicate_key_excess_rows: 5250
```

## 8. Leakage Rule

Consumers must never use short observations without an external event cutoff
and an explicit availability-lag rule.

Legal consumption requires:

```text
as_of_date <= event/session decision cutoff
requires_availability_lag_assumption = true
```

Same-day intraday causal claims are prohibited in v0.1:

```text
same_day_intraday_causal_claim_allowed = false
```

`valid_for_rl_training_direct` is false for every row.
