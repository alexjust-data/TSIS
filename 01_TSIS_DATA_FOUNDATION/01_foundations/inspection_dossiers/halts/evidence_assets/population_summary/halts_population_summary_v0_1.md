# Halts Population Summary v0.1

Resumen ligero promovido desde cache historico. Los parquets pesados siguen en `01_research`.

## Source quality

| source | rows | ticker_nonnull_rows | halt_date_nonnull_rows | halt_start_nonnull_rows | resume_trade_nonnull_rows | release_no_nonnull_rows | item_link_nonnull_rows | issuer_name_nonnull_rows | unique_tickers | unique_event_key_exact | unique_event_key_semantic |
|---|---|---|---|---|---|---|---|---|---|---|---|
| nasdaq | 119630 | 119619 | 119619 | 119619 | 118730 | 0 | 119619 | 116323 | 16572 | 118475 | 118475 |
| nyse | 13178 | 13172 | 13178 | 13178 | 12052 | 0 | 0 | 13178 | 2568 | 12436 | 12436 |
| sec | 1346 | 250 | 1346 | 0 | 0 | 1346 | 1346 | 1346 | 250 | 1346 | 1346 |

## Canonical event taxonomy

| event_taxonomy | events | source_rows | tickers |
|---|---|---|---|
| good_full_intraday_event | 129638 | 131524 | 16232 |
| good_date_level_event | 1272 | 1273 | 1180 |
| review_partial_identity | 1096 | 1096 | 0 |
| regulatory_context_only | 250 | 250 | 250 |
| bad_unusable_event | 1 | 11 | 0 |

## LT1B event taxonomy

| event_taxonomy | events | tickers |
|---|---|---|
| good_full_intraday_event | 53720 | 3900 |
| good_date_level_event | 186 | 152 |
| regulatory_context_only | 3 | 3 |

## Visual buckets

| visual_case_bucket | visual_rows |
|---|---|
| confirmed_halt_microstructure_coherent | 18591 |
| halt_with_trades_signal_only | 3914 |
| halt_with_quotes_signal_only | 1896 |
| halt_present_but_market_clean | 516 |
| market_signal_without_clear_halt_window | 384 |

## Universe coverage

| metric | value | reading |
|---|---|---|
| universe_tickers | 4824 | tickers in lt1b coverage summary |
| tickers_with_halt_data | 3912 | tickers with at least one matched halt event |
| tickers_without_halt_data | 912 | absence means no matched event, not missing coverage |
| halt_events_total_for_universe | 53909 | total events attached to universe tickers |

## Multisource reconciliation

| scope | rows_pre_concat | rows_post_builder_dedup | dedup_delta |
|---|---|---|---|
| nasdaq | 119630 | 118594 | 1036 |
| nyse | 13178 | 13178 | 0 |
| sec | 1346 | 1346 | 0 |
| all_sources_concat | 134154 | 133118 | 1036 |
| persisted_multisource_parquet | 133116 | 133116 | 0 |
