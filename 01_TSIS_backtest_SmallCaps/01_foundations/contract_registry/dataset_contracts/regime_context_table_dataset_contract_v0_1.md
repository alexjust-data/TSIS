# Regime Context Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: regime_context_table_v0_1
family: data_foundation_outputs
class: reference/context state component table
grain: regime_symbol + trading_date + source_granularity
```

## 2. Purpose

`regime_context_table` turns governed `regime_indicators` minute bars into
session-level regime context rows.

It answers:

```text
What market/regime proxy context was available after this proxy session closed?
```

It does not answer:

- whether a setup should trade;
- whether a regime caused a move;
- what the intraday regime was before a same-session event;
- whether execution was possible;
- whether a row is a direct ML/RL training state.

## 3. Source Lineage

Primary source:

```text
regime_indicators_v0_1
root: E:/TSIS/data/regime_indicators
included: **/minute.parquet
excluded: **/day.parquet
```

Calendar source:

```text
market_calendar_v0_1
root: E:/TSIS/data/data_foundation_outputs/market_calendar
```

Explicitly excluded:

```text
E:/TSIS/data/intraday_regime_features
```

Rationale:

- `day.parquet` files in `regime_indicators_v0_1` have audited invalid 1970
  date semantics and remain blocked.
- `intraday_regime_features` is a pilot ticker-day feature layer, not a global
  regime source for this v0.1 output.
- Minute bars are aggregated to daily/session context so source rows can be
  traced and quality gates can be enforced.

## 4. Current Scope

```text
materialization_scope: regime_indicators_minute_aggregated_daily_context_v0_1
full_universe_claim: false
direct_rl_training_allowed: false
execution_truth: false
requires_asof_filter: true
contains_future_information_without_event_filter: true
same_session_intraday_causal_claim_allowed: false
timestamp_timezone_state: vendor_naive_timestamp_review
as_of_semantics: session_close_aggregate_from_minute_bars
```

The output is a market-regime context component. It is not the final market
state representation and not an intraday causal state builder.

## 5. Current Materialization

```text
build_run_id: regime_context_table_v0_1_20260627T084649Z
path: E:/TSIS/data/data_foundation_outputs/regime_context_table/regime_context_table_v0_1
manifest: E:/TSIS/data/data_foundation_outputs/regime_context_table/_regime_context_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/regime_context_table/_regime_context_table_summary_v0_1.csv
rows: 154692
regime_symbols: 33
parquet_files: 25
output_tree_sha256: 6cb774257e72ec1fa0e0c4fd514141b684f21e262de0a82206362bdbfbcba48c
```

Source inventory:

```text
minute_files: 33
minute_rows_aggregated: 64348953
blocked_day_files: 34
minute_total_bytes: 1213579950
minute_inventory_hash: e26b75c7910caf3e7381ad838c150f57edf531d60897c263e0941523cbb6b395
```

Rows by source proxy family:

```text
etf: 154603
index: 89
```

Quality:

```text
good_minute_aggregated_regime_context: 143840
review_no_market_calendar_session: 9214
review_source_bar_integrity: 107
review_sparse_minute_coverage: 1531
bad_rows: 0
```

## 6. Scientific And Institutional Justification

Decision TSIS:

```text
build regime context from minute.parquet, not from blocked day.parquet
```

Evidence:

- `regime_indicators_v0_1` daily files were previously audited with suspicious
  `1970-01-01` date/datetime semantics.
- The output source inventory reads 33 minute parquet files and explicitly
  blocks 34 daily parquet files.
- The output preserves source path, proxy family, proxy role, coverage state and
  source bar-integrity counts.

Obligation:

```text
consumers must select rows using an external event-time cutoff and must not use
same-session completed aggregates as pre-event information
```

Open limitation:

```text
v0.1 is session-close daily regime context; it is not a live or pre-event
intraday regime model
```

## 7. Allowed Consumers

Allowed with gates:

- `event_engine` as regime context after explicit as-of selection.
- `market_state_builder` as one state component after event-time cutoff.
- `backtest_extended` with `valid_for_event_context_candidate = true`.
- `ml_flagged` with legal as-of selection and feature/label separation.
- `research_only`
- `forensic_only`

Not enabled:

- `backtest_core` direct.
- `execution_simulator`.
- `rl_allowed` as direct training dataset.
- `live_downstream_candidate`.
- same-session intraday causal consumption.

## 8. Change Policy

Version bump required when:

- `day.parquet` files are repaired or allowed;
- `intraday_regime_features` becomes a source;
- timestamp timezone semantics change;
- as-of semantics change from session-close to intraday cutoff;
- proxy role mapping changes;
- quality gates or sparse-coverage thresholds change;
- rows are collapsed, deduplicated or backfilled differently;
- full-universe or ML/RL readiness claims change.
