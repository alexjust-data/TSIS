# News Context Table Schema Contract `v0_1`

## 1. Role

This document defines the canonical schema for:

```text
news_context_table_v0_1
```

`news_context_table` is a governed Data Foundation context/state component for
historical news known from `published_utc`.

It is not a real-time alert feed, not proof of causality by itself, not a label
table and not a direct RL training dataset.

## 2. Logical Unit

Unit:

```text
one news article row downloaded for one requested ticker
```

Grain:

```text
source_file_relative_path + source_file_row_number
```

Logical key:

```text
ticker + published_utc + article_id
```

Availability rule:

```text
as_of_utc = published_utc
as_of_date = date(published_utc)
```

`ticker` is the requested/download ticker. `payload_tickers` is the article
symbol list and may contain multiple tickers. Consumers must preserve this
distinction.

## 3. Physical Layout

Root:

```text
E:/TSIS/data/data_foundation_outputs/news_context_table
```

Dataset:

```text
news_context_table_v0_1/
  published_year=<YYYY>/
```

Artifacts:

```text
_news_context_table_manifest_v0_1.json
_news_context_table_summary_v0_1.csv
```

Builder:

```text
scripts/materialize_news_context_table.py
```

## 4. Sources

Governed source v0.1:

```text
E:/TSIS/data/additional/news
```

Source contract:

```text
01_foundations/canonical_schemas/additional/additional_news_schema_contract.md
```

Business rows only are materialized. Empty sentinel rows remain recorded in the
manifest source inventory but are excluded from the output table.

## 5. Required Columns

Identity and article lineage:

- `news_context_id`
- `ticker`
- `source_path_ticker`
- `instrument_id`
- `source_dataset_id`
- `source_subblock`
- `article_id`
- `article_url`
- `article_url_hash`
- `title`
- `title_hash`
- `author`

Publisher and media:

- `publisher_name`
- `publisher_homepage_url`
- `publisher_logo_url`
- `publisher_favicon_url`
- `image_url`
- `amp_url`
- `description`

Availability:

- `published_utc`
- `published_utc_raw`
- `published_date`
- `published_year`
- `as_of_utc`
- `as_of_date`
- `as_of_semantics`

Ticker attribution:

- `payload_tickers`
- `payload_tickers_text`
- `payload_ticker_count`
- `requested_ticker_in_payload_tickers`
- `is_mono_ticker_article`
- `is_multi_ticker_article`
- `ticker_attribution_state`

Text/context payload:

- `keywords`
- `keywords_text`
- `insights`
- `insights_text`

Instrument context:

- `instrument_master_ticker_present`
- `instrument_identity_temporal_match`
- `instrument_identity_state`
- `is_common_stock`
- `is_lt1b_operational`
- `lt1b_classification_1b`

Quality and consumer gates:

- `news_quality_state`
- `valid_for_event_context_candidate`
- `valid_for_catalyst_timing_candidate`
- `valid_for_ml_feature_candidate`
- `valid_for_state_component_candidate`
- `valid_for_rl_training_direct`
- `requires_event_time_filter`
- `prohibited_without_asof_filter`
- `contains_future_information_without_event_filter`
- `causal_proof_by_itself`
- `same_day_causal_claim_allowed_without_intraday_ordering`
- `timezone_alignment_required_for_intraday_claims`

Source lineage:

- `source_root`
- `source_file`
- `source_file_relative_path`
- `source_file_row_number`
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

## 6. Quality States

Allowed `news_quality_state` values:

- `good_mono_ticker_news_context`
- `good_review_multi_ticker_news_context`
- `review_no_temporal_identity`
- `review_missing_article_tickers`
- `review_requested_ticker_not_in_payload`
- `review_unclassified_news_context`
- `bad_missing_published_utc`
- `bad_missing_article_id`
- `bad_missing_article_url`
- `bad_missing_title`

Allowed `ticker_attribution_state` values:

- `good_mono_ticker_attributed`
- `review_multi_ticker_attributed`
- `review_missing_article_tickers`
- `review_requested_ticker_not_in_payload`
- `review_unclassified_ticker_attribution`

Primary context candidates require:

```text
valid_for_event_context_candidate = true
requested_ticker_in_payload_tickers = true
instrument_identity_temporal_match = true
published_utc is not null
```

Multi-ticker rows can pass context gates, but they remain review-attribution
rows. Downstream event/state builders must decide how to weight or filter them.

## 7. Current Materialization

```text
build_run_id: news_context_table_v0_1_20260626T123436Z
rows: 287138
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

Quality distribution:

```text
good_mono_ticker_news_context: 102556
good_review_multi_ticker_news_context: 180051
review_no_temporal_identity: 4531
```

Attribution distribution:

```text
good_mono_ticker_attributed: 104455
review_multi_ticker_attributed: 182683
```

## 8. Leakage Rule

Consumers must never join by session date alone.

Legal consumption requires:

```text
published_utc <= event/decision cutoff
```

For intraday claims, consumers must align `published_utc` to market timezone and
prove that market disorder did not predate the publication before making a
causal claim.

`valid_for_rl_training_direct` is false for every v0.1 row.
