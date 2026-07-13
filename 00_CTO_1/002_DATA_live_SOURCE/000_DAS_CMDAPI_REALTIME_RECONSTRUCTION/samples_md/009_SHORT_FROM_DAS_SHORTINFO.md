# 009_SHORT desde DAS SHORTINFO - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS data_family=shortinfo / prefix=$SHORTINFO` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `run_id` | object |
| 1 | `market_date` | object |
| 2 | `ticker` | object |
| 3 | `symbol` | object |
| 4 | `prefix` | object |
| 5 | `positional_fields` | object |
| 6 | `field_1` | object |
| 7 | `field_2` | object |
| 8 | `field_3` | object |
| 9 | `field_4` | object |
| 10 | `field_5` | object |
| 11 | `field_6` | object |
| 12 | `field_7` | object |
| 13 | `observed_at_utc` | object |
| 14 | `event_line_index` | int64 |
| 15 | `command` | object |
| 16 | `stage` | object |
| 17 | `raw_line` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ticker` | SKYQ | NVVE | TVRD | LHAI | ZCMD |
| `symbol` | SKYQ | NVVE | TVRD | LHAI | ZCMD |
| `prefix` | $SHORTINFO | $SHORTINFO | $SHORTINFO | $SHORTINFO | $SHORTINFO |
| `positional_fields` | N\|0\|Y\|0\|0\|N\|Y | N\|0\|Y\|0\|0\|N\|N | N\|0\|Y\|0\|0\|N\|N | N\|0\|Y\|0\|0\|N\|N | N\|0\|Y\|0\|0\|N\|Y |
| `field_1` | N | N | N | N | N |
| `field_2` | 0 | 0 | 0 | 0 | 0 |
| `field_3` | Y | Y | Y | Y | Y |
| `field_4` | 0 | 0 | 0 | 0 | 0 |
| `field_5` | 0 | 0 | 0 | 0 | 0 |
| `field_6` | N | N | N | N | N |
| `field_7` | Y | N | N | N | Y |
| `observed_at_utc` | 2026-07-08T19:42:00+00:00 | 2026-07-08T19:42:23+00:00 | 2026-07-08T19:42:47+00:00 | 2026-07-08T19:43:11+00:00 | 2026-07-08T19:43:38+00:00 |
| `event_line_index` | 1 | 12 | 4 | 1 | 16 |
| `command` | GET SHORTINFO SKYQ | GET SHORTINFO NVVE | GET SHORTINFO TVRD | GET SHORTINFO LHAI | GET SHORTINFO ZCMD |
| `stage` | candidate_static_query | candidate_static_query | candidate_static_query | candidate_static_query | candidate_static_query |
| `raw_line` | $SHORTINFO SKYQ N 0 Y 0 0 N Y | $SHORTINFO NVVE N 0 Y 0 0 N N | $SHORTINFO TVRD N 0 Y 0 0 N N | $SHORTINFO LHAI N 0 Y 0 0 N N | $SHORTINFO ZCMD N 0 Y 0 0 N Y |

## Interpretacion

SHORTINFO aporta senales live/operativas de short, pero no short interest FINRA por settlement_date.
