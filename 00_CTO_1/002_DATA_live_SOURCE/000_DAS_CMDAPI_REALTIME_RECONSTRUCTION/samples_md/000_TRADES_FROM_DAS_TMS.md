# 000_TRADES desde DAS TMS - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS data_family=tms / prefix=$T&S` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `run_id` | object |
| 1 | `market_date` | object |
| 2 | `ticker` | object |
| 3 | `symbol` | object |
| 4 | `date` | object |
| 5 | `timestamp` | object |
| 6 | `ts_utc_inferred` | object |
| 7 | `source_time_et` | object |
| 8 | `observed_at_utc` | object |
| 9 | `price` | float64 |
| 10 | `size` | int64 |
| 11 | `exchange` | object |
| 12 | `conditions` | object |
| 13 | `sale_marker` | object |
| 14 | `venue` | object |
| 15 | `flag_1` | object |
| 16 | `flag_2` | object |
| 17 | `year` | int64 |
| 18 | `month` | int64 |
| 19 | `day` | object |
| 20 | `event_line_index` | int64 |
| 21 | `command` | object |
| 22 | `stage` | object |
| 23 | `raw_line` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ticker` | SKYQ | SKYQ | SKYQ | SKYQ | SKYQ |
| `symbol` | SKYQ | SKYQ | SKYQ | SKYQ | SKYQ |
| `date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `timestamp` | 2026-07-08T19:41:31Z | 2026-07-08T19:41:36Z | 2026-07-08T19:41:37Z | 2026-07-08T19:41:37Z | 2026-07-08T19:41:46Z |
| `ts_utc_inferred` | 2026-07-08T19:41:31Z | 2026-07-08T19:41:36Z | 2026-07-08T19:41:37Z | 2026-07-08T19:41:37Z | 2026-07-08T19:41:46Z |
| `source_time_et` | 15:41:31 | 15:41:36 | 15:41:37 | 15:41:37 | 15:41:46 |
| `observed_at_utc` | 2026-07-08T19:42:05+00:00 | 2026-07-08T19:42:05+00:00 | 2026-07-08T19:42:05+00:00 | 2026-07-08T19:42:05+00:00 | 2026-07-08T19:42:05+00:00 |
| `price` | 3.6806 | 3.6897 | 3.6841 | 3.6805 | 3.685 |
| `size` | 20 | 5 | 100 | 17 | 40 |
| `exchange` | FADF | FADF | FADF | FADF | FADF |
| `conditions` | I\|I\|64 | I\|I\|64 | @\|I\|112 | I\|I\|64 | I\|I\|64 |
| `sale_marker` | I | I | @ | I | I |
| `venue` | FADF | FADF | FADF | FADF | FADF |
| `flag_1` | I | I | I | I | I |
| `flag_2` | 64 | 64 | 112 | 64 | 64 |
| `year` | 2026 | 2026 | 2026 | 2026 | 2026 |
| `month` | 7 | 7 | 7 | 7 | 7 |
| `day` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `event_line_index` | 0 | 1 | 2 | 3 | 4 |
| `command` | SB SKYQ tms | SB SKYQ tms | SB SKYQ tms | SB SKYQ tms | SB SKYQ tms |
| `stage` | candidate_subscribe | candidate_subscribe | candidate_subscribe | candidate_subscribe | candidate_subscribe |
| `raw_line` | $T&S SKYQ 3.6806 20 I 15:41:31 FADF I 64 | $T&S SKYQ 3.6897 5 I 15:41:36 FADF I 64 | $T&S SKYQ 3.6841 100 @ 15:41:37 FADF I 112 | $T&S SKYQ 3.6805 17 I 15:41:37 FADF I 64 | $T&S SKYQ 3.685 40 I 15:41:46 FADF I 64 |

## Interpretacion

Comparable con `000_TRADES` en precio, tamano, timestamp inferido y venue/condition DAS. No es equivalencia perfecta con condiciones/exchange Polygon.
