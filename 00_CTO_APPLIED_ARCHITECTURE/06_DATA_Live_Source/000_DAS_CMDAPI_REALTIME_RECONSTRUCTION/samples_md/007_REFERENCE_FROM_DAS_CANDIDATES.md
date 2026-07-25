# 007_REFERENCE parcial desde DAS candidate_registry - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS candidate_registry/toplist + market_cap reference` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `run_id` | object |
| 1 | `market_date` | object |
| 2 | `ticker` | object |
| 3 | `symbol` | object |
| 4 | `event_type` | object |
| 5 | `filter_status` | object |
| 6 | `session` | object |
| 7 | `observed_at_utc` | object |
| 8 | `price_usd` | float64 |
| 9 | `volume_shares` | int64 |
| 10 | `market_cap_usd` | float64 |
| 11 | `market_cap_asof_date` | object |
| 12 | `market_cap_source` | object |
| 13 | `failure_reasons` | object |
| 14 | `toplist_seen` | bool |
| 15 | `capture_status` | object |
| 16 | `lv1_bid` | float64 |
| 17 | `lv1_ask` | float64 |
| 18 | `lv1_last` | float64 |
| 19 | `lv1_volume` | int64 |
| 20 | `quote_raw_line` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ticker` | SOXS | EDBL | AAL | ONFO | NVDA |
| `symbol` | SOXS | EDBL | AAL | ONFO | NVDA |
| `event_type` | screener_evaluated | screener_evaluated | screener_evaluated | screener_evaluated | screener_evaluated |
| `filter_status` | FAIL | FAIL | FAIL | FAIL | FAIL |
| `session` | regular_market | regular_market | regular_market | regular_market | regular_market |
| `observed_at_utc` | 2026-07-08T19:37:47+00:00 | 2026-07-08T19:37:50+00:00 | 2026-07-08T19:37:52+00:00 | 2026-07-08T19:37:54+00:00 | 2026-07-08T19:37:57+00:00 |
| `price_usd` | 4.5201 | 0.1194 | 16.575 | 0.237 | 205.065 |
| `volume_shares` | 797308572 | 459424758 | 159689036 | 135220085 | 109458223 |
| `market_cap_usd` |  | 32362.496000000003 |  | 2661329.3200000003 |  |
| `market_cap_asof_date` |  | 2026-03-06 |  | 2026-03-06 |  |
| `market_cap_source` | unavailable_in_market_cap_reference | C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observ... | unavailable_in_market_cap_reference | C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observ... | unavailable_in_market_cap_reference |
| `failure_reasons` | market_cap_unavailable | price_outside_range | market_cap_unavailable | price_outside_range | market_cap_unavailable\|price_outside_range |
| `toplist_seen` | True | True | True | True | True |
| `capture_status` |  |  |  |  |  |
| `lv1_bid` | 4.52 | 0.1194 | 16.57 | 0.2374 | 205.06 |
| `lv1_ask` | 4.53 | 0.1194 | 16.58 | 0.2393 | 205.07 |
| `lv1_last` | 4.5201 | 0.1194 | 16.575 | 0.237 | 205.065 |
| `lv1_volume` | 797308572 | 459424758 | 159689036 | 135220085 | 109458223 |
| `quote_raw_line` | $Quote SOXS A:4.53 Asz:25 B:4.52 Bsz:23 V:797308572 L:4.5201 Hi:4.99 Lo:4.46 op:4.98 ycl:4.8 tcl:0 PE:A VWAP:4.772 tr... | $Quote EDBL A:0.1194 Asz:395 B:0.1194 Bsz:1 V:459424758 L:0.1194 Hi:0.151 Lo:0.1038 op:0.1312 ycl:0.0877 tcl:0 PE:Q V... | $Quote AAL A:16.58 Asz:173 B:16.57 Bsz:119 V:159689036 L:16.575 Hi:16.91 Lo:16.11 op:16.835 ycl:17.2 tcl:0 PE:Q VWAP:... | $Quote ONFO A:0.2393 Asz:1 B:0.2374 Bsz:19 V:135220085 L:0.237 Hi:0.5869 Lo:0.2222 op:0.5369 ycl:0.394 tcl:0 PE:Q VWA... | $Quote NVDA A:205.07 Asz:29 B:205.06 Bsz:2 V:109458223 L:205.065 Hi:205.16 Lo:195.1 op:195.18 ycl:196.93 tcl:0 PE:Q V... |

## Interpretacion

Sirve para comparar universo candidato, PASS/FAIL y market cap usado. No es instrument_master completo.
