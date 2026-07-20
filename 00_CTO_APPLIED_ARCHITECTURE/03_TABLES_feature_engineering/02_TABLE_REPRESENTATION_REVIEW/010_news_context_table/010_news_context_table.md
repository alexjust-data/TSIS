# news_context_table_v0_1 - Operational Table Content Sample

## Purpose

This document prints a small human-readable sample from one Data Foundation output that is operational for its declared scope.
It is a navigation and inspection aid, not a new certification artifact and not a promotion decision.

## Operational Status

| item | value |
| --- | --- |
| status | `validated_for_declared_scope` |
| scope | Additional news rows with published_utc as as_of_utc; ticker attribution preserved. |
| operational_use | Catalyst/news context after explicit as-of join. |
| exclusions | Not proof of causality; not live received-latency alert stream; not direct ML/RL table. |

## Source

| item | value |
| --- | --- |
| dataset_id | `news_context_table_v0_1` |
| source_dataset | `E:\TSIS\data\data_foundation_outputs\news_context_table\news_context_table_v0_1` |
| sample_parquet | `E:\TSIS\data\data_foundation_outputs\news_context_table\news_context_table_v0_1\published_year=2016\data_0.parquet` |
| declared_rows_in_status_matrix | 287,138 |
| declared_file_or_partition_count_in_status_matrix | 9 |
| physical_parquet_files_seen | 9 |
| physical_rows_from_parquet_metadata | 287138 |
| physical_row_groups_seen | 9 |
| sample_physical_columns | 71 |

## Sample Selection

First rows from the official dataset root, with Hive partition columns included when present.

## Schema

| ordinal | field | type |
| --- | --- | --- |
| 0 | `news_context_id` | `string` |
| 1 | `ticker` | `string` |
| 2 | `source_path_ticker` | `string` |
| 3 | `instrument_id` | `string` |
| 4 | `source_dataset_id` | `string` |
| 5 | `source_subblock` | `string` |
| 6 | `article_id` | `string` |
| 7 | `article_url` | `string` |
| 8 | `article_url_hash` | `string` |
| 9 | `title` | `string` |
| 10 | `title_hash` | `string` |
| 11 | `author` | `string` |
| 12 | `publisher_name` | `string` |
| 13 | `publisher_homepage_url` | `string` |
| 14 | `publisher_logo_url` | `string` |
| 15 | `publisher_favicon_url` | `string` |
| 16 | `image_url` | `string` |
| 17 | `amp_url` | `string` |
| 18 | `description` | `string` |
| 19 | `published_utc` | `timestamp[us]` |
| 20 | `published_utc_raw` | `string` |
| 21 | `published_date` | `date32[day]` |
| 22 | `as_of_utc` | `timestamp[us]` |
| 23 | `as_of_date` | `date32[day]` |
| 24 | `as_of_semantics` | `string` |
| 25 | `payload_tickers` | `list<element: string>` |
| 26 | `payload_tickers_text` | `string` |
| 27 | `payload_ticker_count` | `int64` |
| 28 | `requested_ticker_in_payload_tickers` | `bool` |
| 29 | `is_mono_ticker_article` | `bool` |
| 30 | `is_multi_ticker_article` | `bool` |
| 31 | `ticker_attribution_state` | `string` |
| 32 | `keywords` | `list<element: string>` |
| 33 | `keywords_text` | `string` |
| 34 | `insights` | `list<element: struct<sentiment: string, sentiment_reasoning: string, ticker: string>>` |
| 35 | `insights_text` | `string` |
| 36 | `instrument_master_ticker_present` | `bool` |
| 37 | `instrument_identity_temporal_match` | `bool` |
| 38 | `instrument_identity_state` | `string` |
| 39 | `is_common_stock` | `bool` |
| 40 | `is_lt1b_operational` | `bool` |
| 41 | `lt1b_classification_1b` | `string` |
| 42 | `news_quality_state` | `string` |
| 43 | `valid_for_event_context_candidate` | `bool` |
| 44 | `valid_for_catalyst_timing_candidate` | `bool` |
| 45 | `valid_for_ml_feature_candidate` | `bool` |
| 46 | `valid_for_state_component_candidate` | `bool` |
| 47 | `valid_for_rl_training_direct` | `bool` |
| 48 | `requires_event_time_filter` | `bool` |
| 49 | `prohibited_without_asof_filter` | `bool` |
| 50 | `contains_future_information_without_event_filter` | `bool` |
| 51 | `causal_proof_by_itself` | `bool` |
| 52 | `same_day_causal_claim_allowed_without_intraday_ordering` | `bool` |
| 53 | `timezone_alignment_required_for_intraday_claims` | `bool` |
| 54 | `source_root` | `string` |
| 55 | `source_file` | `string` |
| 56 | `source_file_relative_path` | `string` |
| 57 | `source_file_row_number` | `int64` |
| 58 | `source_empty_sentinel` | `bool` |
| 59 | `_dataset` | `string` |
| 60 | `_ingested_utc` | `string` |
| 61 | `instrument_master_build_run_id` | `string` |
| 62 | `instrument_master_schema_version` | `string` |
| 63 | `full_universe_claim` | `bool` |
| 64 | `materialization_scope` | `string` |
| 65 | `quality_policy_version` | `string` |
| 66 | `schema_version` | `string` |
| 67 | `build_run_id` | `string` |
| 68 | `created_at_utc` | `string` |
| 69 | `published_year` | `int32` |

## Printed Sample

This is a printed content sample only. It does not certify the whole table.
The printed sample is transposed for readability: fields are rows and sample records are columns.

| field | sample_1 | sample_2 | sample_3 |
| --- | --- | --- | --- |
| `news_context_id` | 5680a44103042e613fe1ae41a3e5872d8a0ef351865ad7d830478f5b0f303e63 | a0155b6247ac282e180523deae3cdafba29a29c7c317be26d86893511704635c | b75e6f89802542157d11b416d20b03d1620d9bf7f8931fc9b7a9dd9f0b2a6178 |
| `ticker` | TWOU | SNCR | BBBY |
| `source_path_ticker` | TWOU | SNCR | BBBY |
| `instrument_id` |  |  |  |
| `source_dataset_id` | additional_v0_1 | additional_v0_1 | additional_v0_1 |
| `source_subblock` | news | news | news |
| `article_id` | A89NcTfkzQjXUxOQ24aX7zLcJTsdJB0rjZnMtkHcEjE | A89NcTfkzQjXUxOQ24aX7zLcJTsdJB0rjZnMtkHcEjE | UH_SBlXP6vmK2huhwHe6w_3VpFrUG9k_sLaaliUKqq0 |
| `article_url` | http://feeds.thestreet.com/~r/tsc/feeds/rss/p/real-money/~3/pw-jkmBpHSs/13621613.html | http://feeds.thestreet.com/~r/tsc/feeds/rss/p/real-money/~3/pw-jkmBpHSs/13621613.html | http://feeds.thestreet.com/~r/tsc/feeds/rss/p/real-money/~3/zGUcjdTVUY8/13617892.html |
| `article_url_hash` | 46dfa3a2958183f8c09b9b41deba8800855419cbce1cf6d7eac613b4250ea610 | 46dfa3a2958183f8c09b9b41deba8800855419cbce1cf6d7eac613b4250ea610 | 0567299f17d0e7c2131db64e323874c1bf47dc82dce33d666261829182ed2bf4 |
| `title` | Brexit Comes at a Particularly Bad Time for Software Companies | Brexit Comes at a Particularly Bad Time for Software Companies | Jim Cramer -- Bed Bath Needs Someone Who Knows What Customers Want |
| `title_hash` | c77c3ea17b05d179de947f0bca8e1d0859883051ce9bd5ca4254255b2454b733 | c77c3ea17b05d179de947f0bca8e1d0859883051ce9bd5ca4254255b2454b733 | cebb7182caa8228924e5c5f7e3d42d5844fa8f89e001135cd2b42c8c852965e2 |
| `author` | twocents@thestreet.com (Chris Nolter) | twocents@thestreet.com (Chris Nolter) | twocents@thestreet.com (Bret Kenwell) |
| `publisher_name` | TheStreet | TheStreet | TheStreet |
| `publisher_homepage_url` | https://www.thestreet.com/ | https://www.thestreet.com/ | https://www.thestreet.com/ |
| `publisher_logo_url` | https://s3.polygon.io/public/assets/news/logos/thestreet.svg | https://s3.polygon.io/public/assets/news/logos/thestreet.svg | https://s3.polygon.io/public/assets/news/logos/thestreet.svg |
| `publisher_favicon_url` | https://s3.polygon.io/public/assets/news/favicons/thestreet.png | https://s3.polygon.io/public/assets/news/favicons/thestreet.png | https://s3.polygon.io/public/assets/news/favicons/thestreet.png |
| `image_url` | https://s.thestreet.com/files/tsc/tst_fb.jpg | https://s.thestreet.com/files/tsc/tst_fb.jpg | https://s.thestreet.com/files/tsc/tst_fb.jpg |
| `amp_url` |  |  |  |
| `description` | For most publicly-traded companies, there was never a good time for the Brexit vote. But for the large software companies?that market to corporate IT departm... | For most publicly-traded companies, there was never a good time for the Brexit vote. But for the large software companies?that market to corporate IT departm... | Bed Bath & Beyond     ?shares are up over 2% Thursday despite the company missing on earnings per share and revenue expectations.  Guidance was unimpressive ... |
| `published_utc` | 2016-06-28T13:41:00 | 2016-06-28T13:41:00 | 2016-06-23T14:31:00 |
| `published_utc_raw` | 2016-06-28T13:41:00Z | 2016-06-28T13:41:00Z | 2016-06-23T14:31:00Z |
| `published_date` | 2016-06-28 | 2016-06-28 | 2016-06-23 |
| `as_of_utc` | 2016-06-28T13:41:00 | 2016-06-28T13:41:00 | 2016-06-23T14:31:00 |
| `as_of_date` | 2016-06-28 | 2016-06-28 | 2016-06-23 |
| `as_of_semantics` | published_utc_vendor_timestamp | published_utc_vendor_timestamp | published_utc_vendor_timestamp |
| `payload_tickers` | ['CYBR', 'OTEX', 'CSOD', 'PANW', 'ADBE', 'ORCL', 'VEEV', 'SNCR', 'PFPT', 'TYL', 'TWOU', 'VRNT', 'SPLK', 'MSFT', 'FTNT', 'CHKP', 'PAYC', 'CRM'] | ['CYBR', 'OTEX', 'CSOD', 'PANW', 'ADBE', 'ORCL', 'VEEV', 'SNCR', 'PFPT', 'TYL', 'TWOU', 'VRNT', 'SPLK', 'MSFT', 'FTNT', 'CHKP', 'PAYC', 'CRM'] | ['BBBY', 'M'] |
| `payload_tickers_text` | [CYBR, OTEX, CSOD, PANW, ADBE, ORCL, VEEV, SNCR, PFPT, TYL, TWOU, VRNT, SPLK, MSFT, FTNT, CHKP, PAYC, CRM] | [CYBR, OTEX, CSOD, PANW, ADBE, ORCL, VEEV, SNCR, PFPT, TYL, TWOU, VRNT, SPLK, MSFT, FTNT, CHKP, PAYC, CRM] | [BBBY, M] |
| `payload_ticker_count` | 18 | 18 | 2 |
| `requested_ticker_in_payload_tickers` | True | True | True |
| `is_mono_ticker_article` | False | False | False |
| `is_multi_ticker_article` | True | True | True |
| `ticker_attribution_state` | review_multi_ticker_attributed | review_multi_ticker_attributed | review_multi_ticker_attributed |
| `keywords` | ['Equities', 'Opinion'] | ['Equities', 'Opinion'] | ['Equities', 'How to Invest', 'JRC Top 5', 'Jim Cramer Stock Picks', 'Opinion', 'Stock Picks'] |
| `keywords_text` | [Equities, Opinion] | [Equities, Opinion] | [Equities, How to Invest, JRC Top 5, Jim Cramer Stock Picks, Opinion, Stock Picks] |
| `insights` |  |  |  |
| `insights_text` |  |  |  |
| `instrument_master_ticker_present` | True | True | True |
| `instrument_identity_temporal_match` | False | False | False |
| `instrument_identity_state` | review_no_temporal_identity | review_no_temporal_identity | review_no_temporal_identity |
| `is_common_stock` |  |  |  |
| `is_lt1b_operational` |  |  |  |
| `lt1b_classification_1b` |  |  |  |
| `news_quality_state` | review_no_temporal_identity | review_no_temporal_identity | review_no_temporal_identity |
| `valid_for_event_context_candidate` | False | False | False |
| `valid_for_catalyst_timing_candidate` | False | False | False |
| `valid_for_ml_feature_candidate` | False | False | False |
| `valid_for_state_component_candidate` | False | False | False |
| `valid_for_rl_training_direct` | False | False | False |
| `requires_event_time_filter` | True | True | True |
| `prohibited_without_asof_filter` | True | True | True |
| `contains_future_information_without_event_filter` | True | True | True |
| `causal_proof_by_itself` | False | False | False |
| `same_day_causal_claim_allowed_without_intraday_ordering` | False | False | False |
| `timezone_alignment_required_for_intraday_claims` | True | True | True |
| `source_root` | E:/TSIS/data/additional/news | E:/TSIS/data/additional/news | E:/TSIS/data/additional/news |
| `source_file` | E:/TSIS/data/additional/news/news/ticker=TWOU/news_TWOU.parquet | E:/TSIS/data/additional/news/news/ticker=SNCR/news_SNCR.parquet | E:/TSIS/data/additional/news/news/ticker=BBBY/news_BBBY.parquet |
| `source_file_relative_path` | news/ticker=TWOU/news_TWOU.parquet | news/ticker=SNCR/news_SNCR.parquet | news/ticker=BBBY/news_BBBY.parquet |
| `source_file_row_number` | 0 | 0 | 0 |
| `source_empty_sentinel` | False | False | False |
| `_dataset` | news | news | news |
| `_ingested_utc` | 2026-04-05T18:37:30.875422+00:00 | 2026-04-05T18:35:49.521935+00:00 | 2026-04-05T18:22:51.019888+00:00 |
| `instrument_master_build_run_id` |  |  |  |
| `instrument_master_schema_version` |  |  |  |
| `full_universe_claim` | False | False | False |
| `materialization_scope` | additional_news_lt1b_published_utc_context_v0_1 | additional_news_lt1b_published_utc_context_v0_1 | additional_news_lt1b_published_utc_context_v0_1 |
| `quality_policy_version` | news_context_table_policy_v0_1 | news_context_table_policy_v0_1 | news_context_table_policy_v0_1 |
| `schema_version` | news_context_table_v0_1 | news_context_table_v0_1 | news_context_table_v0_1 |
| `build_run_id` | news_context_table_v0_1_20260626T123436Z | news_context_table_v0_1_20260626T123436Z | news_context_table_v0_1_20260626T123436Z |
| `created_at_utc` | 2026-06-26T12:34:36.555500+00:00 | 2026-06-26T12:34:36.555500+00:00 | 2026-06-26T12:34:36.555500+00:00 |
| `published_year` | 2016 | 2016 | 2016 |

## Interpretation

Use this file to understand the physical/logical shape and example values of the represented Data Foundation output.
For completeness, pass/fail status, official scope, and exclusions, use the cloned target contract and status matrix in the parent folder.

## Scope Guard

Excluded from this operational sample set:

- `master_intraday_bar_table`: scoped pilot/candidate, not official full-universe 1m.
- `microstructure_features_table`: seed/candidate controlled, not full-universe.
- `market_state_table`: official state table not materialized/promoted; candidates are controlled only.
- `event_state_table`: official state table not materialized/promoted; candidates are controlled only.
- `intraday_scanner_candidates_table`: strategy/candidate surface, not a validated Data Foundation full table.
