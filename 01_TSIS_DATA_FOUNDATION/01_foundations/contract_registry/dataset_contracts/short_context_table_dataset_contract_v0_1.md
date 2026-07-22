# Short Context Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: short_context_table_v0_1
family: data_foundation_outputs
class: reference/context state component table
grain: source_system + observation_family + ticker + observation_date + source_duplicate_key_ordinal
```

## 2. Purpose

`short_context_table` turns the governed `short` and `short_review` layers into
a source-scoped context component for short-side pressure, crowding and
squeeze-risk research.

It answers:

```text
What short interest or short sale volume context exists for this ticker/date/source?
```

It does not answer:

- whether a short squeeze will happen;
- whether the data is complete for 2005-2026;
- whether daily FINRA short volume is consolidated market-wide shorting truth;
- whether borrow availability or SSR was active;
- what strategy should trade.

## 3. Source Lineage

Sources:

```text
short_v0_1
root: E:/TSIS/data/short
families: short_interest, short_volume

short_review_finra_v0_1
root: E:/TSIS/data/short_review/finra_short
families: FINRA short_interest, FINRA short_volume
```

Certification overlay:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_certification_by_ticker.csv
```

FINRA aggregate artifacts:

```text
E:/TSIS/data/short_review/finra_short/artifacts/short_interest_all_biweekly_finra.parquet
E:/TSIS/data/short_review/finra_short/artifacts/short_volume_all_daily_finra.parquet
```

## 4. Current Scope

```text
materialization_scope: short_and_short_review_source_scoped_context_v0_1
full_universe_claim: false
direct_rl_training_allowed: false
borrow_data_present: false
ssr_data_present: false
execution_truth: false
requires_availability_lag_assumption: true
```

The table is source-scoped context. It is not a clean universal shorting truth
layer and not a live borrow/SSR feed.

## 5. Current Materialization

```text
build_run_id: short_context_table_v0_1_20260626T215417Z
path: E:/TSIS/data/data_foundation_outputs/short_context_table/short_context_table_v0_1
manifest: E:/TSIS/data/data_foundation_outputs/short_context_table/_short_context_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/short_context_table/_short_context_table_summary_v0_1.csv
rows: 7145337
tickers: 4694
instruments: 4462
parquet_files: 32
output_tree_sha256: 57c0abbdf6a1d4ef4d1ab6bd7ac326e2d57415645d7cd759605334334271652b
```

Rows by source:

```text
finra_official_free: 5194783
local_polygon: 1950554
short_interest: 1025793
short_volume: 6119544
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
bad_rows: 0
```

## 6. Scientific And Institutional Justification

Decision TSIS:

```text
keep local/Polygon and FINRA as separate source planes
```

Reason:

- Local `short` has complete downloaded files for the `<1B>` universe but mixed
  lifecycle/reference certification.
- FINRA `short_review` is official/free baseline and stronger for modern
  short-volume history, but it is not a silent replacement and has source-scope
  limitations.
- FINRA short volume is not consolidated market-wide shorting truth.
- Short interest is slow/biweekly crowding context, not same-day intraday
  evidence.

Obligation:

```text
event/state consumers must preserve source_system, source_scope, quality_state,
duplicate-key flags and availability-lag assumptions
```

Open limitation:

```text
no v0.1 row contains borrow availability or SSR state
```

## 7. Allowed Consumers

Allowed with gates:

- `event_engine` as short-side context after explicit as-of/lag selection.
- `market_state_builder` as a short-pressure component after event-time cutoff.
- `backtest_extended` with `valid_for_backtest_context_candidate = true`.
- `ml_flagged` with `valid_for_ml_feature_candidate = true`.
- `research_only`
- `forensic_only`

Not enabled:

- `backtest_core` direct.
- `ml_primary` direct.
- `execution_simulator`.
- `rl_allowed` as direct training dataset.
- `live_downstream_candidate`.

## 8. Change Policy

Version bump required when:

- source precedence changes;
- FINRA duplicate-key handling changes;
- local/Polygon certification rules change;
- borrow or SSR fields are added;
- availability-lag rules become more precise;
- rows are deduplicated, aggregated or collapsed;
- full-history completeness claims change.
