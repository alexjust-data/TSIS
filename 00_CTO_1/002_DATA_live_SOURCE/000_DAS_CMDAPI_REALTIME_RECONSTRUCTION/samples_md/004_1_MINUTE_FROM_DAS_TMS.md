# 004_1_MINUTE reconstruido desde DAS TMS - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS TMS agregado a OHLCV 1m` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `ticker` | object |
| 1 | `ts_utc` | object |
| 2 | `date` | object |
| 3 | `year` | int64 |
| 4 | `month` | int64 |
| 5 | `o` | float64 |
| 6 | `h` | float64 |
| 7 | `l` | float64 |
| 8 | `c` | float64 |
| 9 | `v` | int64 |
| 10 | `vw` | float64 |
| 11 | `n` | int64 |
| 12 | `t` | object |
| 13 | `run_id` | object |
| 14 | `market_date` | object |
| 15 | `source` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `ticker` | BBLG | BBLG | BBLG | BBLG | BBLG |
| `ts_utc` | 2026-07-08T19:42:00Z | 2026-07-08T19:43:00Z | 2026-07-08T19:45:00Z | 2026-07-08T19:47:00Z | 2026-07-08T19:50:00Z |
| `date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `year` | 2026 | 2026 | 2026 | 2026 | 2026 |
| `month` | 7 | 7 | 7 | 7 | 7 |
| `o` | 1.29 | 1.31 | 1.3099 | 1.305 | 1.31 |
| `h` | 1.32 | 1.3186 | 1.3099 | 1.305 | 1.31 |
| `l` | 1.29 | 1.302 | 1.3099 | 1.305 | 1.3001 |
| `c` | 1.32 | 1.302 | 1.3099 | 1.305 | 1.3001 |
| `v` | 2091 | 692 | 300 | 50 | 250 |
| `vw` | 1.3019320899091344 | 1.3098736994219655 | 1.3099 | 1.305 | 1.3060399999999999 |
| `n` | 22 | 6 | 1 | 1 | 2 |
| `t` |  |  |  |  |  |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `source` | das_tms_reconstructed_1m | das_tms_reconstructed_1m | das_tms_reconstructed_1m | das_tms_reconstructed_1m | das_tms_reconstructed_1m |

## Interpretacion

Es la reconstruccion mas importante para comparar con `004_1_MINUTE`: OHLCV/VW/N por minuto desde prints reales capturados.
