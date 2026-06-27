# News Context Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: news_context_table_v0_1
family: data_foundation_outputs
class: reference/context state component table
grain: source_file_relative_path + source_file_row_number
```

## 2. Purpose

`news_context_table` turns accepted `<1B>` Polygon news rows from
`additional/news` into a timestamp-aware event/context component.

It answers:

```text
What news article was published for this requested ticker, and when was it published?
```

It does not answer:

- whether the article caused the move;
- whether the article was received by TSIS live before the event;
- whether a same-day move was already disordered before publication;
- what strategy should trade;
- what label or reward happened after the news.

## 3. Source Lineage

Authoritative v0.1 source:

```text
source_dataset_id: additional_v0_1
source_subblock: news
root: E:/TSIS/data/additional/news
```

Accepted physical form:

```text
news/ticker=<TICKER>/news_<TICKER>.parquet
```

Source schema:

```text
01_foundations/canonical_schemas/additional/additional_news_schema_contract.md
```

## 4. Current Scope

```text
materialization_scope: additional_news_lt1b_published_utc_context_v0_1
full_universe_claim: false
as_of_semantics: published_utc_vendor_timestamp
direct_rl_training_allowed: false
```

The table covers the non-empty `<1B>` additional news source files. It is not a
complete market-wide news archive and is not a low-latency real-time alert
stream.

## 5. Current Materialization

```text
build_run_id: news_context_table_v0_1_20260626T123436Z
path: E:/TSIS/data/data_foundation_outputs/news_context_table/news_context_table_v0_1
manifest: E:/TSIS/data/data_foundation_outputs/news_context_table/_news_context_table_manifest_v0_1.json
summary: E:/TSIS/data/data_foundation_outputs/news_context_table/_news_context_table_summary_v0_1.csv
rows: 287138
tickers: 3869
instruments: 3699
publishers: 11
parquet_files: 9
output_tree_sha256: bff4a26caaab27e1d7974e8947ecea8b26cea09e585fe304206812db8aafdbff
```

Source inventory:

```text
source_files: 4824
business_files: 3869
empty_sentinel_files: 955
metadata_rows: 288093
business_rows: 287138
```

Quality:

```text
good_mono_ticker_news_context: 102556
good_review_multi_ticker_news_context: 180051
review_no_temporal_identity: 4531
bad_rows: 0
hard_fail_count: 0
```

Attribution:

```text
good_mono_ticker_attributed: 104455
review_multi_ticker_attributed: 182683
```

## 6. Scientific And Institutional Justification

Decision TSIS:

```text
use published_utc as the historical availability anchor and keep ticker attribution explicit
```

Reason:

- Event-study and market-state research require strict temporal ordering:
  context known after the decision cutoff cannot become a pre-event feature.
- News is a plausible catalyst overlay, but the article payload may reference
  several symbols; multi-ticker rows are therefore attribution-review rows, not
  deterministic ticker-causal truth.
- A market-state builder needs both technical state and catalyst context. This
  table supplies the catalyst context component, not the final state.

Obligation:

```text
event/state consumers must filter published_utc <= decision cutoff
```

Open limitation:

```text
v0.1 uses historical vendor published_utc, not TSIS live received_utc latency.
```

## 7. Allowed Consumers

Allowed with gates:

- `event_engine` as catalyst/context lookup after explicit as-of selection.
- `market_state_builder` as a news/catalyst component after event-time cutoff.
- `backtest_extended` for contextual filters after as-of selection.
- `ml_flagged` when `valid_for_ml_feature_candidate = true` and the as-of join
  is performed outside this table.
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

- source root or provider changes;
- live `received_utc` latency is added;
- catalyst taxonomy is added or changed;
- article-level deduplication changes the grain;
- multi-ticker attribution rules change;
- `valid_for_ml_feature_candidate` or `valid_for_state_component_candidate`
  gate semantics change;
- full-universe claims change.
