# Global Metrics Tables | Traceable

Este duplicado mantiene la capa cuantitativa, pero añade trazabilidad técnica:

- artefacto fuente exacto
- script o builder que lo produce
- notebook o imagen donde se ve visualmente
- nota corta de lectura

## daily_quality

Fuente:
- [daily_quality.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\daily_quality.parquet)
- [daily_lt1b_hard_invalid_exclusion_summary.json](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_exclusion_summary.json)
- [daily_lt1b_hard_invalid_exclusion.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_exclusion.parquet)

Visual / notebook:
- [04_daily_closeout.ipynb](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\daily\04_daily_closeout.ipynb)
- [04_daily_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\daily\04_daily_closeout.md)

Lectura:
- `bad` en `daily` es cola dura de exclusión, no un frente masivo.

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| daily | ticker_year | good_or_review | 44321 | 99.770389 |
| daily | ticker_year | bad | 102 | 0.229611 |

## daily_coverage

Fuente:
- [daily_coverage.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\daily_coverage.parquet)
- [problematic57_cross_1m_quotes_trades_summary.json](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\problematic57_cross_1m_quotes_trades_full\problematic57_cross_1m_quotes_trades_summary.json)
- [problematic57_cross_1m_quotes_trades.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\problematic57_cross_1m_quotes_trades_full\problematic57_cross_1m_quotes_trades.parquet)

Visual / notebook:
- [001.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\daily\img\001.png)
- [007.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\daily\img\007.png)

Lectura:
- esta tabla mide cobertura de ticker, no corrupción OHLCV.

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| daily | ticker | complete_daily_present | 4171 | 86.463516 |
| daily | ticker | likely_valid_gap_only | 374 | 7.752902 |
| daily | ticker | ambiguous_review | 222 | 4.60199 |
| daily | ticker | unexpected_problematic | 57 | 1.181592 |

## 1m_operational

Fuente:
- [1m_operational.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\1m_operational.parquet)
- [operational_decision_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full\root_cause_operational_outputs\operational_decision_summary.parquet)
- [rescue_schema_only.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full\root_cause_operational_outputs\rescue_schema_only.parquet)
- [rescue_schema_plus_vw.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full\root_cause_operational_outputs\rescue_schema_plus_vw.parquet)
- [hard_quarantine.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full\root_cause_operational_outputs\hard_quarantine.parquet)

Visual / notebook:
- [04_ohlcv_1m_closeout.ipynb](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\ohlcv_1m\04_ohlcv_1m_closeout.ipynb)
- [04_ohlcv_1m_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\ohlcv_1m\04_ohlcv_1m_closeout.md)

Lectura:
- la tabla es full-scope operativo; no debe venderse como corte `<1B>` recalculado.

| status | count | block | scope | pct |
| --- | --- | --- | --- | --- |
| RESCUE_SCHEMA_PLUS_VW | 1063976 | 1m | event | 83.645649 |
| RESCUE_SCHEMA_ONLY | 204928 | 1m | event | 16.110641 |
| QUARANTINE_PARSE_INVALID | 3049 | 1m | event | 0.239701 |
| QUARANTINE_PRICE_INVALID | 51 | 1m | event | 0.004009 |

## quotes_core_mix

Fuente:
- [quotes_core_mix.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\quotes_core_mix.parquet)
- [quotes_taxonomy.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\quotes_taxonomy.parquet)
- [quotes_open_buckets.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\quotes_open_buckets.parquet)

Visual / notebook:
- [04_quotes_full_C_D_closeout.ipynb](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\quotes\v2\04_quotes_full_C_D_closeout.ipynb)
- [12_quotes_open_buckets_synthesis.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\12_quotes_open_buckets_synthesis.md)
- [01_major_quality_mix.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\01_major_quality_mix.png)

Lectura:
- `good_core_explicit` es el núcleo limpio explicitado; `other_taxonomies_closed_elsewhere` recoge familias ya cerradas pero no resumidas aquí como `open`.

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| quotes | ticker_date_file | good_core_explicit | 7716014 | 81.005708 |
| quotes | ticker_date_file | review_open_explicit | 97364 | 1.022165 |
| quotes | ticker_date_file | bad_open_explicit | 187512 | 1.968574 |
| quotes | ticker_date_file | other_taxonomies_closed_elsewhere | 1524382 | 16.003553 |

## quotes_open_buckets

Fuente:
- [quotes_open_buckets.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\quotes_open_buckets.parquet)

Visual / notebook:
- [08_persistent_soft_crossed_mid_large_scale.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\08_persistent_soft_crossed_mid_large_scale.md)
- [09_large_file_threshold_edge_hard_many_crosses.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\09_large_file_threshold_edge_hard_many_crosses.md)
- [10_medium_file_threshold_edge_hard_many_crosses.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\10_medium_file_threshold_edge_hard_many_crosses.md)
- [11_high_hard_crossed_10_to_20.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes\11_high_hard_crossed_10_to_20.md)

Lectura:
- aquí sí están los buckets abiertos que requirieron decisión manual `review / bad`.

| taxonomy | files | tickers | dates | hard_fail_files | soft_fail_files | crossed_ratio_median_pct | crossed_ratio_p90_pct | pct | block | scope | final_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high_hard_crossed_10_to_20 | 101549 | 2572 | 5300 | 101549 | 0 | 13.043478260869565 | 17.647058823529413 | 1.0661007895627548 | quotes | ticker_date_file | bad |
| medium_file_threshold_edge_hard_many_crosses | 85963 | 3871 | 5320 | 85963 | 0 | 2.0202020202020203 | 4.156711520480403 | 0.9024729162589793 | quotes | ticker_date_file | bad |
| large_file_threshold_edge_hard_many_crosses | 50288 | 2828 | 4819 | 50288 | 0 | 1.5225045640344486 | 3.638551856395101 | 0.5279429290838099 | quotes | ticker_date_file | review |
| persistent_soft_crossed_mid_large_scale | 47076 | 2615 | 4544 | 0 | 47076 | 0.4353414773425088 | 0.6821229527032022 | 0.4942221072532102 | quotes | ticker_date_file | review |

## trades_final_recovery

Fuente:
- [trades_final_recovery.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\trades_final_recovery.parquet)
- [trades_raw_labels.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\trades_raw_labels.parquet)
- [file_acceptance_cache_lt1b_full_clean](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean)

Visual / notebook:
- [20_trades_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\20_trades_closeout.md)
- [00_current_policy_distribution_from_raw_shards.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\00_current_policy_distribution_from_raw_shards.png)
- [11_d_full_final_bucket_distribution.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\11_d_full_final_bucket_distribution.png)

Lectura:
- esta tabla está hoy calculada sobre el subset materializado `5.6M`, no sobre `9,429,112`; debe rehacerse cuando cierre `57e`.

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| trades | file | good | 80 | 0.001429 |
| trades | file | recoverable_with_flag | 3737456 | 66.740286 |
| trades | file | review_not_rehabilitated | 1853108 | 33.091214 |
| trades | file | bad | 9356 | 0.167071 |

## halts_lt1b_event_taxonomy

Fuente:
- [halts_lt1b_event_taxonomy.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\halts_lt1b_event_taxonomy.parquet)
- [halts_lt1b_event_index.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\cache_v2\halts_lt1b_event_index.parquet)
- [event_taxonomy_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\halts\cache_v2\event_taxonomy_summary.parquet)

Visual / notebook:
- [03_halts_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\halts\03_halts_closeout.md)
- [02_context_blocks.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\02_context_blocks.png)

Lectura:
- el bloque `halts` entra casi limpio; la cola residual es marginal.

| block | scope | status | count | pct |
| --- | --- | --- | --- | --- |
| halts | lt1b_event | good_full_intraday_event | 53720 | 99.649409 |
| halts | lt1b_event | good_date_level_event | 186 | 0.345026 |
| halts | lt1b_event | regulatory_context_only | 3 | 0.005565 |

## reference_identity

Fuente:
- [reference_identity.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\reference_identity.parquet)
- [reference_identity_quality_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\reference\cache_v2\reference_identity_quality_summary.parquet)

Visual / notebook:
- [02_reference_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\reference\02_reference_closeout.md)
- [02_context_blocks.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\02_context_blocks.png)

Lectura:
- mide calidad de identidad, no toda la potencia causal del bloque.

| status | count | distinct_tickers | lt1b_rows | with_market_cap | active_true | row_pct | block | scope | pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| good_identity_snapshot | 12093 | 12093 | 4812 | 7853 | 12093 | 96.99 | reference | identity_row | 96.9923 |
| bad_unresolved_identity | 200 | 200 | 2 | 0 | 0 | 1.6 | reference | identity_row | 1.604107 |
| review_transient_symbol | 175 | 175 | 10 | 29 | 175 | 1.4 | reference | identity_row | 1.403593 |

## short_provider_baseline

Fuente:
- [short_provider_baseline.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\short_provider_baseline.parquet)
- [short_provider_comparison_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\cache_v2\short_provider_comparison_summary.parquet)
- [short_only_polygon_tickers.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\cache_v2\short_only_polygon_tickers.parquet)

Visual / notebook:
- [02_short_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\short\02_short_closeout.md)
- [02_context_blocks.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\02_context_blocks.png)

Lectura:
- esta sección demuestra que `FINRA` es baseline y que el gap `only_polygon` estaba sobreleído.

| block | dataset | polygon_present_rows | finra_present_rows | raw_only_polygon_rows | meaningful_only_polygon_rows | zero_row_only_polygon_rows |
| --- | --- | --- | --- | --- | --- | --- |
| short | short_interest | 4824 | 4687 | 137 | 7 | 130 |
| short | short_volume | 4824 | 4623 | 201 | 19 | 182 |

## additional_coverage

Fuente:
- [additional_coverage.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\additional_coverage.parquet)
- [additional_effective_coverage_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_effective_coverage_summary.parquet)

Visual / notebook:
- [02_additional_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\additional\02_additional_closeout.md)

Lectura:
- cobertura por subcapa, no decisión final única del bloque.

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

Fuente:
- [additional_news.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\additional_news.parquet)
- [additional_news_link_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_news_link_summary.parquet)
- [additional_news_market_link_candidates.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_news_market_link_candidates.parquet)

Visual / notebook:
- [02_additional_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\additional\02_additional_closeout.md)
- [02_context_blocks.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\02_context_blocks.png)

Lectura:
- `review_multi_ticker_ambiguous_news` es un bucket ambiguo real, no un artefacto de agregación.

| status | count | tickers | mean_tickers_per_news | block | scope | pct |
| --- | --- | --- | --- | --- | --- | --- |
| review_multi_ticker_ambiguous_news | 169154 | 3627 | 16.26471144637431 | additional | news_event | 58.91035 |
| news_near_market_anomaly | 98400 | 3103 | 1.0 | additional | news_event | 34.269236 |
| news_context_only | 18296 | 2798 | 28.048589855706165 | additional | news_event | 6.371849 |
| news_near_halt_market_event | 1268 | 707 | 1.0 | additional | news_event | 0.4416 |
| news_near_short_flow_only | 20 | 15 | 6.2 | additional | news_event | 0.006965 |

## additional_ipos

Fuente:
- [additional_ipos.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\additional_ipos.parquet)
- [additional_ipo_link_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\additional\cache_v2\additional_ipo_link_summary.parquet)

Visual / notebook:
- [02_additional_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\additional\02_additional_closeout.md)

Lectura:
- `ipos` aporta contexto, pero no debe tratarse como bloque maestro comparable a `daily` o `halts`.

| status | count | tickers | block | scope | pct |
| --- | --- | --- | --- | --- | --- |
| ipo_near_market_anomaly | 676 | 668 | additional | ipo_event | 52.771272 |
| ipo_market_clean | 449 | 443 | additional | ipo_event | 35.050742 |
| ipo_near_halt_market_event | 156 | 156 | additional | ipo_event | 12.177986 |

## Figures

- [01_major_quality_mix.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\01_major_quality_mix.png)
- [02_context_blocks.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\global_metrics\img\02_context_blocks.png)
