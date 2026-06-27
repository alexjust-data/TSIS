# Fundamentals As-Of Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
fundamentals_asof_table_v0_1
```

`fundamentals_asof_table` is a governed Data Foundation state component for
fundamental statement context known as of a filing date.

It is not a raw financial dataset, not a ratios table, not a market-cap
universe source, not a label table and not a direct RL training dataset.

## 2. Logical Unit

Unit:

```text
one statement observation known as of filing_date
```

Grain:

```text
source_file_relative_path + source_file_row_number + statement_family
```

Logical key:

```text
ticker + statement_family + period_end + filing_date + fiscal_year + fiscal_quarter + timeframe
```

Availability rule:

```text
as_of_date = filing_date
period_end is accounting period, not availability date
```

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table
```

Dataset:

```text
fundamentals_asof_table_v0_1/
  statement_family=<family>/
    as_of_year=<YYYY>/
```

Artifacts:

```text
_fundamentals_asof_table_manifest_v0_1.json
_fundamentals_asof_table_summary_v0_1.csv
```

Builder:

```text
scripts/materialize_fundamentals_asof_table.py
```

## 4. Sources

Governed source v0.1:

```text
E:/TSIS/data/additional/financials
```

Included subfamilies:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`

Explicitly excluded from v0.1 core:

- `additional/financials/ratios`: `review` sparse vendor-derived snapshot.
- `E:/TSIS/data/financial`: governed but blocked while `financial_v0_1`
  audit state is `FAIL`.

## 5. Required Columns

Identity and statement lineage:

- `fundamental_asof_id`
- `ticker`
- `instrument_id`
- `statement_family`
- `source_dataset_id`
- `source_subblock`
- `period_end`
- `filing_date`
- `as_of_date`
- `as_of_year`
- `fiscal_year`
- `fiscal_quarter`
- `timeframe`
- `cik`
- `source_tickers`

Instrument context:

- `instrument_master_ticker_present`
- `instrument_identity_temporal_match`
- `instrument_identity_state`
- `is_common_stock`
- `is_lt1b_operational`
- `lt1b_classification_1b`

Quality and consumer gates:

- `fundamental_quality_state`
- `valid_for_event_context_candidate`
- `valid_for_ml_feature_candidate`
- `valid_for_backtest_context_candidate`
- `valid_for_state_component_candidate`
- `valid_for_rl_training_direct`
- `as_of_semantics`
- `period_end_is_availability_date`
- `requires_event_time_filter`
- `prohibited_without_asof_filter`
- `contains_future_information_without_event_filter`
- `ratios_excluded_from_core_v0_1`
- `standalone_financial_root_excluded_from_core_v0_1`

Source lineage:

- `source_root`
- `source_file`
- `source_file_relative_path`
- `source_file_row_number`
- `source_path_ticker`
- `source_empty_sentinel`
- `_dataset`
- `_ingested_utc`
- `instrument_master_build_run_id`
- `instrument_master_schema_version`
- `full_universe_claim`
- `materialization_scope`
- `quality_policy_version`
- `schema_version`
- `build_run_id`
- `created_at_utc`

Selected statement metrics:

- income: `revenue`, `cost_of_revenue`, `gross_profit`,
  `operating_income`, `consolidated_net_income_loss`, EPS, shares and
  `ebitda` fields.
- balance sheet: cash, receivables, inventory, assets, liabilities, equity,
  debt and preferred/common stock fields.
- cash flow: operating/investing/financing cash flow, capex, dividends,
  change in cash and currency effect fields.

Metric columns are nullable. Missing numeric accounting values are missing
values, not zero.

## 6. Quality States

Allowed `fundamental_quality_state` values:

- `good_statement_asof`
- `review_no_temporal_identity`
- `review_period_after_filing_date`
- `bad_missing_filing_date`
- `bad_missing_period_end`

Primary consumer gates require:

```text
fundamental_quality_state = good_statement_asof
```

## 7. Current Materialization

```text
build_run_id: fundamentals_asof_table_v0_1_20260626T101617Z
rows: 621756
parquet_files: 51
output_tree_sha256: 07d3d0200e16e020cee79fc2cf6aa873cde0145cf7efa0f07d0e78c8aefe5d58
```

Quality distribution:

```text
good_statement_asof: 500530
review_no_temporal_identity: 121217
review_period_after_filing_date: 9
```

Statement rows:

```text
income_statements: 242886
balance_sheets: 136661
cash_flow_statements: 242209
```

## 8. Leakage Rule

Consumers must never join by `period_end`.

Legal consumption requires:

```text
as_of_date <= event_time/session cutoff
```

and the chosen row must be selected by an explicit as-of rule, normally latest
eligible filing before the event/session.

