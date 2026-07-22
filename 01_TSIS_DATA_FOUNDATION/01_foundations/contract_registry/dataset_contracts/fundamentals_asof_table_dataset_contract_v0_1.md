# Fundamentals As-Of Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: fundamentals_asof_table_v0_1
family: data_foundation_outputs
class: reference/context state component table
grain: source_file_relative_path + source_file_row_number + statement_family
```

## 2. Purpose

`fundamentals_asof_table` turns accepted `<1B>` additional financial statements
into a filing-date-aware context component.

It answers:

```text
What financial statement facts were known for this ticker as of this filing_date?
```

It does not answer:

- which row is latest before an event;
- what the market cap or float was at a historical intraday timestamp;
- what label or reward happened after an event;
- what strategy should trade.

## 3. Source Lineage

Authoritative v0.1 source:

```text
source_dataset_id: additional_v0_1
source_subblock: financials_core
root: E:/TSIS/data/additional/financials
```

Included:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`

Excluded:

- `ratios`, because the additional policy marks it `review` and sparse.
- `E:/TSIS/data/financial`, because `financial_v0_1` is blocked while audit
  status remains `FAIL`.

## 4. Current Scope

```text
materialization_scope: additional_financials_core_lt1b_statement_asof_v0_1
full_universe_claim: false
as_of_semantics: filing_date_available_from_date_only
direct_rl_training_allowed: false
```

The output covers the `<1B>` additional financials source universe. It is not a
full public-equity fundamentals warehouse.

## 5. Current Materialization

```text
build_run_id: fundamentals_asof_table_v0_1_20260626T101617Z
path: E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/fundamentals_asof_table_v0_1
manifest: E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/_fundamentals_asof_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table/_fundamentals_asof_table_summary_v0_1.csv
rows: 621756
tickers: 4813
instruments: 4590
parquet_files: 51
output_tree_sha256: 07d3d0200e16e020cee79fc2cf6aa873cde0145cf7efa0f07d0e78c8aefe5d58
```

Source inventory:

```text
source_files: 14472
business_files: 14436
empty_sentinel_files: 36
business_rows: 621756
```

Quality:

```text
good_statement_asof: 500530
review_no_temporal_identity: 121217
review_period_after_filing_date: 9
bad_rows: 0
```

## 6. Scientific And Institutional Justification

Decision TSIS:

```text
use filing_date as availability date and keep period_end as accounting period
```

Evidence:

- SEC EDGAR filing APIs expose submissions/filings as the official publication
  channel; filing time/date is the defensible availability anchor, while fiscal
  period end describes the accounting period.
- Financial ML and event-study practice require point-in-time features and
  strict feature/label separation to avoid lookahead bias.
- TSIS root research policy requires explicit state components with lineage,
  quality gates and leakage boundaries before ML/RL use.

Obligation:

```text
event/session consumers must filter as_of_date <= decision cutoff
```

Open limitation:

```text
v0.1 is date-level filing availability, not second-level EDGAR/newswire latency.
```

## 7. Allowed Consumers

Allowed with gates:

- `event_engine` as contextual lookup after explicit as-of selection.
- `backtest_extended` for contextual filters after as-of selection.
- `ml_flagged` when `valid_for_ml_feature_candidate = true` and the as-of join
  is performed outside this table.
- `research_only`
- `forensic_only`

Not enabled:

- `backtest_core` without an event/session as-of builder.
- `ml_primary` as direct table input.
- `execution_simulator`.
- `rl_allowed` as direct training dataset.
- `live_downstream_candidate`.

## 8. Change Policy

Version bump required when:

- `ratios` are added;
- `E:/TSIS/data/financial` is promoted or merged;
- grain changes from statement row to daily/event snapshot;
- filing timestamp precision changes;
- selected metric columns change materially;
- quality-state definitions change;
- full-universe claims change.

