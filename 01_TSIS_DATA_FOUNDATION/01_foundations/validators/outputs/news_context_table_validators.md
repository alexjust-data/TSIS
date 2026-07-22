# News Context Table Validators `v0_1`

## 1. Scope

This validator contract governs:

```text
news_context_table_v0_1
```

## 2. Required Inputs

Required governed sources:

- `E:/TSIS/data/additional/news`
- `E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet`
- `E:/TSIS/data/data_foundation_outputs/instrument_master/_instrument_master_manifest_v0_1.json`

Required contracts:

- `01_foundations/canonical_schemas/additional/additional_news_schema_contract.md`
- `01_foundations/data_consumption_policies/additional_consumption_policy.md`
- `01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md`
- `01_foundations/contract_registry/dataset_contracts/news_context_table_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/news_context_table_consumption_policy.md`

## 3. Hard Validation Checks

The build must fail if:

- `news_context_id` is duplicated;
- `article_id + published_utc_raw + ticker` is duplicated;
- a business row has missing `published_utc`;
- a business row has missing `article_id`;
- a business row has missing `article_url`;
- a business row has missing `title`;
- the output has zero rows;
- the manifest `output_tree` does not match the parquet tree.

## 4. Required Quality Checks

The validator must emit:

- source file count;
- business file count;
- empty sentinel file count;
- business row count;
- first and last `published_utc`;
- ticker count;
- instrument count;
- publisher count;
- `news_quality_state` distribution;
- `ticker_attribution_state` distribution;
- `instrument_identity_state` distribution;
- `published_year` distribution;
- consumer-gate row counts.

## 5. Required Consumer Gates

Every row must satisfy:

```text
valid_for_rl_training_direct = false
requires_event_time_filter = true
prohibited_without_asof_filter = true
contains_future_information_without_event_filter = true
causal_proof_by_itself = false
same_day_causal_claim_allowed_without_intraday_ordering = false
timezone_alignment_required_for_intraday_claims = true
full_universe_claim = false
source_empty_sentinel = false
```

Rows may have `valid_for_event_context_candidate = true` only when:

```text
published_utc is not null
article_id is not null
article_url is not null
title is not null
requested_ticker_in_payload_tickers = true
instrument_identity_temporal_match = true
```

## 6. Attribution Checks

Allowed `ticker_attribution_state` values:

- `good_mono_ticker_attributed`
- `review_multi_ticker_attributed`
- `review_missing_article_tickers`
- `review_requested_ticker_not_in_payload`
- `review_unclassified_ticker_attribution`

Multi-ticker article rows must remain review-attribution rows even when they
pass event/context gates.

## 7. Current Expected v0.1 Counts

```text
rows: 287138
tickers: 3869
instruments: 3699
publishers: 11
source_files: 4824
business_files: 3869
empty_sentinel_files: 955
business_rows: 287138
hard_fail_count: 0
duplicate_news_context_id_count: 0
duplicate_source_key_count: 0
missing_published_utc_rows: 0
missing_article_id_rows: 0
missing_article_url_rows: 0
missing_title_rows: 0
valid_for_event_context_candidate_rows: 282607
valid_for_ml_feature_candidate_rows: 282607
valid_for_rl_training_direct_rows: 0
```

Quality:

```text
good_mono_ticker_news_context: 102556
good_review_multi_ticker_news_context: 180051
review_no_temporal_identity: 4531
```

Attribution:

```text
good_mono_ticker_attributed: 104455
review_multi_ticker_attributed: 182683
```

## 8. Test Evidence

The pytest contract is:

```text
tests/data_foundation_outputs/test_news_context_table_contract.py
```

Evidence must be written under:

```text
C:/TSIS_Data/tests/test_runs/<date>/data_foundation_outputs_news_context_table_v0_1/
```
