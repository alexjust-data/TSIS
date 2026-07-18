# 001_QUOTES desde DAS LV1 - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS data_family=lv1 / prefix=$Quote` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `run_id` | object |
| 1 | `market_date` | object |
| 2 | `ticker` | object |
| 3 | `symbol` | object |
| 4 | `ask_exchange` | object |
| 5 | `ask_price` | float64 |
| 6 | `ask_size` | int64 |
| 7 | `bid_exchange` | object |
| 8 | `bid_price` | float64 |
| 9 | `bid_size` | int64 |
| 10 | `conditions` | object |
| 11 | `indicators` | object |
| 12 | `participant_timestamp` | object |
| 13 | `sequence_number` | object |
| 14 | `timestamp` | object |
| 15 | `trf_timestamp` | object |
| 16 | `tape` | object |
| 17 | `source_time_et` | object |
| 18 | `observed_at_utc` | object |
| 19 | `last_price` | float64 |
| 20 | `session_volume` | int64 |
| 21 | `session_high` | float64 |
| 22 | `session_low` | float64 |
| 23 | `session_open` | float64 |
| 24 | `prev_close` | float64 |
| 25 | `today_close` | int64 |
| 26 | `vwap` | float64 |
| 27 | `trades_all_day` | int64 |
| 28 | `relative_volume` | int64 |
| 29 | `year` | int64 |
| 30 | `month` | int64 |
| 31 | `day` | int64 |
| 32 | `event_line_index` | int64 |
| 33 | `command` | object |
| 34 | `stage` | object |
| 35 | `raw_line` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ticker` | SOXS | SOXS | EDBL | AAL | AAL |
| `symbol` | SOXS | SOXS | EDBL | AAL | AAL |
| `ask_exchange` |  |  |  |  |  |
| `ask_price` | 4.53 | 4.53 | 0.1194 | 16.58 | 16.58 |
| `ask_size` | 25 | 25 | 395 | 173 | 173 |
| `bid_exchange` |  |  |  |  |  |
| `bid_price` | 4.52 | 4.52 | 0.1194 | 16.57 | 16.57 |
| `bid_size` | 23 | 23 | 1 | 119 | 119 |
| `conditions` |  |  |  |  |  |
| `indicators` |  |  |  |  |  |
| `participant_timestamp` |  |  |  |  |  |
| `sequence_number` |  |  |  |  |  |
| `timestamp` | 2026-07-08T19:37:45Z | 2026-07-08T19:37:45Z | 2026-07-08T19:37:30Z | 2026-07-08T19:37:50Z | 2026-07-08T19:37:50Z |
| `trf_timestamp` |  |  |  |  |  |
| `tape` | A | A | Q | Q | Q |
| `source_time_et` | 15:37:45 | 15:37:45 | 15:37:30 | 15:37:50 | 15:37:50 |
| `observed_at_utc` | 2026-07-08T19:37:46+00:00 | 2026-07-08T19:37:46+00:00 | 2026-07-08T19:37:48+00:00 | 2026-07-08T19:37:51+00:00 | 2026-07-08T19:37:51+00:00 |
| `last_price` | 4.5202 | 4.5201 | 0.1194 | 16.5797 | 16.58 |
| `session_volume` | 797308375 | 797308572 | 459424758 | 159668936 | 159679536 |
| `session_high` | 4.99 | 4.99 | 0.151 | 16.91 | 16.91 |
| `session_low` | 4.46 | 4.46 | 0.1038 | 16.11 | 16.11 |
| `session_open` | 4.98 | 4.98 | 0.1312 | 16.835 | 16.835 |
| `prev_close` | 4.8 | 4.8 | 0.0877 | 17.2 | 17.2 |
| `today_close` | 0 | 0 | 0 | 0 | 0 |
| `vwap` | 4.772 | 4.772 | 0.13877 | 16.452 | 16.452 |
| `trades_all_day` | 472155 | 472156 | 350449 | 189324 | 189327 |
| `relative_volume` | 143 | 143 | 2453 | 123 | 123 |
| `year` | 2026 | 2026 | 2026 | 2026 | 2026 |
| `month` | 7 | 7 | 7 | 7 | 7 |
| `day` | 8 | 8 | 8 | 8 | 8 |
| `event_line_index` | 1 | 2 | 0 | 0 | 2 |
| `command` | SB SOXS Lv1 | SB SOXS Lv1 | SB EDBL Lv1 | SB AAL Lv1 | SB AAL Lv1 |
| `stage` | screener_lv1 | screener_lv1 | screener_lv1 | screener_lv1 | screener_lv1 |
| `raw_line` | $Quote SOXS A:4.53 Asz:25 B:4.52 Bsz:23 V:797308375 L:4.5202 Hi:4.99 Lo:4.46 op:4.98 ycl:4.8 tcl:0 PE:A VWAP:4.772 tr... | $Quote SOXS A:4.53 Asz:25 B:4.52 Bsz:23 V:797308572 L:4.5201 Hi:4.99 Lo:4.46 op:4.98 ycl:4.8 tcl:0 PE:A VWAP:4.772 tr... | $Quote EDBL A:0.1194 Asz:395 B:0.1194 Bsz:1 V:459424758 L:0.1194 Hi:0.151 Lo:0.1038 op:0.1312 ycl:0.0877 tcl:0 PE:Q V... | $Quote AAL A:16.58 Asz:173 B:16.57 Bsz:119 V:159668936 L:16.5797 Hi:16.91 Lo:16.11 op:16.835 ycl:17.2 tcl:0 PE:Q VWAP... | $Quote AAL A:16.58 Asz:173 B:16.57 Bsz:119 V:159679536 L:16.58 Hi:16.91 Lo:16.11 op:16.835 ycl:17.2 tcl:0 PE:Q VWAP:1... |

## Interpretacion

Comparable con `001_QUOTES` en bid/ask/size y timestamps inferidos. No incluye secuencia SIP, participant_timestamp ni TRF.
