# 002_DAILY desde DAS DAYCHART - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS data_family=daychart / prefix=$Bar` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `run_id` | object |
| 1 | `market_date` | object |
| 2 | `ticker` | object |
| 3 | `symbol` | object |
| 4 | `source_bar_time` | object |
| 5 | `date` | object |
| 6 | `ts_utc` | object |
| 7 | `year` | int64 |
| 8 | `month` | object |
| 9 | `o` | float64 |
| 10 | `h` | float64 |
| 11 | `l` | float64 |
| 12 | `c` | float64 |
| 13 | `v` | int64 |
| 14 | `vw` | object |
| 15 | `n` | object |
| 16 | `t` | object |
| 17 | `status_or_count` | int64 |
| 18 | `observed_at_utc` | object |
| 19 | `event_line_index` | int64 |
| 20 | `command` | object |
| 21 | `stage` | object |
| 22 | `raw_line` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ticker` | SKYQ | SKYQ | SKYQ | SKYQ | SKYQ |
| `symbol` | SKYQ | SKYQ | SKYQ | SKYQ | SKYQ |
| `source_bar_time` | 2026/06/29 | 2026/06/30 | 2026/07/01 | 2026/07/02 | 2026/07/06 |
| `date` | 2026 | 2026 | 2026 | 2026 | 2026 |
| `ts_utc` |  |  |  |  |  |
| `year` | 2026 | 2026 | 2026 | 2026 | 2026 |
| `month` |  |  |  |  |  |
| `o` | 3.05 | 3.91 | 3.295 | 2.82 | 2.3 |
| `h` | 4.1386 | 4.18 | 3.295 | 2.91 | 2.52 |
| `l` | 2.88 | 3.41 | 2.6001 | 2.2 | 2.08 |
| `c` | 3.48 | 3.67 | 2.97 | 2.64 | 2.12 |
| `v` | 20002322 | 12775434 | 5270853 | 3207189 | 2479115 |
| `vw` |  |  |  |  |  |
| `n` |  |  |  |  |  |
| `t` |  |  |  |  |  |
| `status_or_count` | 1 | 1 | 1 | 1 | 1 |
| `observed_at_utc` | 2026-07-08T19:42:12+00:00 | 2026-07-08T19:42:12+00:00 | 2026-07-08T19:42:12+00:00 | 2026-07-08T19:42:12+00:00 | 2026-07-08T19:42:12+00:00 |
| `event_line_index` | 3 | 4 | 5 | 6 | 7 |
| `command` | SB SKYQ DAYCHART 2026/06/28 2026/07/08 | SB SKYQ DAYCHART 2026/06/28 2026/07/08 | SB SKYQ DAYCHART 2026/06/28 2026/07/08 | SB SKYQ DAYCHART 2026/06/28 2026/07/08 | SB SKYQ DAYCHART 2026/06/28 2026/07/08 |
| `stage` | candidate_chart_query | candidate_chart_query | candidate_chart_query | candidate_chart_query | candidate_chart_query |
| `raw_line` | $Bar SKYQ 2026/06/29 4.1386 2.88 3.05 3.48 20002322 1 | $Bar SKYQ 2026/06/30 4.18 3.41 3.91 3.67 12775434 1 | $Bar SKYQ 2026/07/01 3.295 2.6001 3.295 2.97 5270853 1 | $Bar SKYQ 2026/07/02 2.91 2.2 2.82 2.64 3207189 1 | $Bar SKYQ 2026/07/06 2.52 2.08 2.3 2.12 2479115 1 |

## Interpretacion

Comparable con `002_DAILY` como fuente externa DAS para barras diarias de candidatos. No sustituye daily foundation.
