# 001_QUOTES profundidad DAS LV2 - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS data_family=lv2 / prefix=$Lv2` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `run_id` | object |
| 1 | `market_date` | object |
| 2 | `ticker` | object |
| 3 | `symbol` | object |
| 4 | `side` | object |
| 5 | `market_maker_or_venue` | object |
| 6 | `price` | float64 |
| 7 | `size` | int64 |
| 8 | `action` | object |
| 9 | `source_time_et` | object |
| 10 | `ts_utc_inferred` | object |
| 11 | `observed_at_utc` | object |
| 12 | `event_line_index` | int64 |
| 13 | `command` | object |
| 14 | `stage` | object |
| 15 | `raw_line` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ticker` | SKYQ | SKYQ | SKYQ | SKYQ | SKYQ |
| `symbol` | SKYQ | SKYQ | SKYQ | SKYQ | SKYQ |
| `side` | A | B | A | B | A |
| `market_maker_or_venue` | ARCA | IEX | NASD | NASD | BATS |
| `price` | 3.7 | 3.68 | 3.7 | 3.68 | 3.71 |
| `size` | 2 | 2 | 80 | 5 | 1 |
| `action` | UPDATED | UPDATED | UPDATED | UPDATED | UPDATED |
| `source_time_et` | 21:41:55 | 21:41:53 | 21:41:50 | 21:42:03 | 21:41:46 |
| `ts_utc_inferred` | 2026-07-09T01:41:55Z | 2026-07-09T01:41:53Z | 2026-07-09T01:41:50Z | 2026-07-09T01:42:03Z | 2026-07-09T01:41:46Z |
| `observed_at_utc` | 2026-07-08T19:42:09+00:00 | 2026-07-08T19:42:09+00:00 | 2026-07-08T19:42:09+00:00 | 2026-07-08T19:42:09+00:00 | 2026-07-08T19:42:09+00:00 |
| `event_line_index` | 0 | 1 | 2 | 3 | 4 |
| `command` | SB SKYQ Lv2 | SB SKYQ Lv2 | SB SKYQ Lv2 | SB SKYQ Lv2 | SB SKYQ Lv2 |
| `stage` | candidate_subscribe | candidate_subscribe | candidate_subscribe | candidate_subscribe | candidate_subscribe |
| `raw_line` | $Lv2 SKYQ A ARCA 3.7 2 UPDATED 21:41:55 | $Lv2 SKYQ B IEX 3.68 2 UPDATED 21:41:53 | $Lv2 SKYQ A NASD 3.7 80 UPDATED 21:41:50 | $Lv2 SKYQ B NASD 3.68 5 UPDATED 21:42:03 | $Lv2 SKYQ A BATS 3.71 1 UPDATED 21:41:46 |

## Interpretacion

Util como contexto de profundidad DAS. No es quote SIP NBBO ni L3/MBO certificado.
