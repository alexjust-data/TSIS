# 004_1_MINUTE desde DAS MINCHART - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS data_family=minchart_1m / prefix=$Bar` |
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
| 8 | `month` | int64 |
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
| `source_bar_time` | 2026/07/08-15:41 | 2026/07/08-15:40 | 2026/07/08-15:39 | 2026/07/08-15:38 | 2026/07/08-15:37 |
| `date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ts_utc` | 2026-07-08T19:41:00Z | 2026-07-08T19:40:00Z | 2026-07-08T19:39:00Z | 2026-07-08T19:38:00Z | 2026-07-08T19:37:00Z |
| `year` | 2026 | 2026 | 2026 | 2026 | 2026 |
| `month` | 7 | 7 | 7 | 7 | 7 |
| `o` | 3.69 | 3.695 | 3.7 | 3.7 | 3.6974 |
| `h` | 3.7 | 3.7 | 3.72 | 3.72 | 3.71 |
| `l` | 3.68 | 3.68 | 3.69 | 3.68 | 3.6701 |
| `c` | 3.69 | 3.68 | 3.69 | 3.71 | 3.685 |
| `v` | 13814 | 9848 | 14283 | 22737 | 15955 |
| `vw` |  |  |  |  |  |
| `n` |  |  |  |  |  |
| `t` |  |  |  |  |  |
| `status_or_count` | 1 | 1 | 1 | 1 | 1 |
| `observed_at_utc` | 2026-07-08T19:42:17+00:00 | 2026-07-08T19:42:17+00:00 | 2026-07-08T19:42:17+00:00 | 2026-07-08T19:42:17+00:00 | 2026-07-08T19:42:17+00:00 |
| `event_line_index` | 1 | 2 | 3 | 4 | 5 |
| `command` | SB SKYQ MINCHART 2026/07/08-14:41 2026/07/08-15:41 1 | SB SKYQ MINCHART 2026/07/08-14:41 2026/07/08-15:41 1 | SB SKYQ MINCHART 2026/07/08-14:41 2026/07/08-15:41 1 | SB SKYQ MINCHART 2026/07/08-14:41 2026/07/08-15:41 1 | SB SKYQ MINCHART 2026/07/08-14:41 2026/07/08-15:41 1 |
| `stage` | candidate_chart_query | candidate_chart_query | candidate_chart_query | candidate_chart_query | candidate_chart_query |
| `raw_line` | $Bar SKYQ 2026/07/08-15:41 3.7 3.68 3.69 3.69 13814 1 | $Bar SKYQ 2026/07/08-15:40 3.7 3.68 3.695 3.68 9848 1 | $Bar SKYQ 2026/07/08-15:39 3.72 3.69 3.7 3.69 14283 1 | $Bar SKYQ 2026/07/08-15:38 3.72 3.68 3.7 3.71 22737 1 | $Bar SKYQ 2026/07/08-15:37 3.71 3.6701 3.6974 3.685 15955 1 |

## Interpretacion

Util para reconciliar contra el 1m reconstruido desde TMS y contra historico si existe la misma fecha.
