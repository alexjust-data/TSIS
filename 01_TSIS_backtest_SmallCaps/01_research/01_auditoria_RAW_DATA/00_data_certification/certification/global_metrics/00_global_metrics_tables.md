# Global Metrics Tables

## daily_quality

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| daily | ticker_year | good_or_review | 44321 | 99.770389 |
| daily | ticker_year | bad | 102 | 0.229611 |

## daily_coverage

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| daily | ticker | complete_daily_present | 4171 | 86.463516 |
| daily | ticker | likely_valid_gap_only | 374 | 7.752902 |
| daily | ticker | ambiguous_review | 222 | 4.60199 |
| daily | ticker | unexpected_problematic | 57 | 1.181592 |

## 1m_operational

| status | count | block | scope | pct |
| --- | --- | --- | --- | --- |
| RESCUE_SCHEMA_PLUS_VW | 1063976 | 1m | event | 83.645649 |
| RESCUE_SCHEMA_ONLY | 204928 | 1m | event | 16.110641 |
| QUARANTINE_PARSE_INVALID | 3049 | 1m | event | 0.239701 |
| QUARANTINE_PRICE_INVALID | 51 | 1m | event | 0.004009 |

## quotes_core_mix

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| quotes | ticker_date_file | good_core_explicit | 7716014 | 81.005708 |
| quotes | ticker_date_file | review_open_explicit | 97364 | 1.022165 |
| quotes | ticker_date_file | bad_open_explicit | 187512 | 1.968574 |
| quotes | ticker_date_file | other_taxonomies_closed_elsewhere | 1524382 | 16.003553 |

## quotes_open_buckets

| taxonomy | files | tickers | dates | hard_fail_files | soft_fail_files | crossed_ratio_median_pct | crossed_ratio_p90_pct | pct | block | scope | final_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high_hard_crossed_10_to_20 | 101549 | 2572 | 5300 | 101549 | 0 | 13.043478260869565 | 17.647058823529413 | 1.0661007895627548 | quotes | ticker_date_file | bad |
| medium_file_threshold_edge_hard_many_crosses | 85963 | 3871 | 5320 | 85963 | 0 | 2.0202020202020203 | 4.156711520480403 | 0.9024729162589793 | quotes | ticker_date_file | bad |
| large_file_threshold_edge_hard_many_crosses | 50288 | 2828 | 4819 | 50288 | 0 | 1.5225045640344486 | 3.638551856395101 | 0.5279429290838099 | quotes | ticker_date_file | review |
| persistent_soft_crossed_mid_large_scale | 47076 | 2615 | 4544 | 0 | 47076 | 0.4353414773425088 | 0.6821229527032022 | 0.4942221072532102 | quotes | ticker_date_file | review |

## trades_final_recovery

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| trades | file | good | 80 | 0.001429 |
| trades | file | recoverable_with_flag | 3737456 | 66.740286 |
| trades | file | review_not_rehabilitated | 1853108 | 33.091214 |
| trades | file | bad | 9356 | 0.167071 |

## halts_lt1b_event_taxonomy

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| halts | lt1b_event | good_full_intraday_event | 53720 | 99.649409 |
| halts | lt1b_event | good_date_level_event | 186 | 0.345026 |
| halts | lt1b_event | regulatory_context_only | 3 | 0.005565 |

## reference_identity

| status | count | distinct_tickers | lt1b_rows | with_market_cap | active_true | row_pct | block | scope | pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| good_identity_snapshot | 12093 | 12093 | 4812 | 7853 | 12093 | 96.99 | reference | identity_row | 96.9923 |
| bad_unresolved_identity | 200 | 200 | 2 | 0 | 0 | 1.6 | reference | identity_row | 1.604107 |
| review_transient_symbol | 175 | 175 | 10 | 29 | 175 | 1.4 | reference | identity_row | 1.403593 |

## short_provider_baseline

| block | dataset | polygon_present_rows | finra_present_rows | raw_only_polygon_rows | meaningful_only_polygon_rows | zero_row_only_polygon_rows |
| --- | --- | --- | --- | --- | --- | --- |
| short | short_interest | 4824 | 4687 | 137 | 7 | 130 |
| short | short_volume | 4824 | 4623 | 201 | 19 | 182 |

## additional_coverage

| dataset | dataset_family | effective_non_empty_pct | files_non_empty | files_present | rows_total | block |
| --- | --- | --- | --- | --- | --- | --- |
| balance_sheets | financials_core | 99.772 | 4813.0 | 4824.0 | 136672 | additional |
| cash_flow_statements | financials_core | 99.71 | 4810.0 | 4824.0 | 242223 | additional |
| dividends | corporate_actions_additional | 26.078 | 1258.0 | 4824.0 | 49684 | additional |
| income_statements | financials_core | 99.772 | 4813.0 | 4824.0 | 242897 | additional |
| ipos | ipos | 26.016 | 1255.0 | 4824.0 | 4850 | additional |
| news | news | 80.203 | 3869.0 | 4824.0 | 288093 | additional |
| ratios | financials_ratios | 46.269 | 2232.0 | 4824.0 | 4824 | additional |
| splits | corporate_actions_additional | 38.889 | 1876.0 | 4824.0 | 6283 | additional |
| ticker_events | corporate_actions_additional | 56.032 | 2703.0 | 4824.0 | 5158 | additional |
| inflation | economic | 100.0 |  |  | 950 | additional |
| inflation_expectations | economic | 100.0 |  |  | 531 | additional |
| treasury_yields | economic | 100.0 |  |  | 16047 | additional |

## additional_news

| status | count | tickers | mean_tickers_per_news | block | scope | pct |
| --- | --- | --- | --- | --- | --- | --- |
| review_multi_ticker_ambiguous_news | 169154 | 3627 | 16.26471144637431 | additional | news_event | 58.91035 |
| news_near_market_anomaly | 98400 | 3103 | 1.0 | additional | news_event | 34.269236 |
| news_context_only | 18296 | 2798 | 28.048589855706165 | additional | news_event | 6.371849 |
| news_near_halt_market_event | 1268 | 707 | 1.0 | additional | news_event | 0.4416 |
| news_near_short_flow_only | 20 | 15 | 6.2 | additional | news_event | 0.006965 |

## additional_ipos

| status | count | tickers | block | scope | pct |
| --- | --- | --- | --- | --- | --- |
| ipo_near_market_anomaly | 676 | 668 | additional | ipo_event | 52.771272 |
| ipo_market_clean | 449 | 443 | additional | ipo_event | 35.050742 |
| ipo_near_halt_market_event | 156 | 156 | additional | ipo_event | 12.177986 |

## Figures

- [01_major_quality_mix.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\01_major_quality_mix.png)
- [02_context_blocks.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\02_context_blocks.png)