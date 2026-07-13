# 008_HALTS status desde DAS SymStatus - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS data_family=symstatus / prefix=$SymStatus` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `run_id` | object |
| 1 | `market_date` | object |
| 2 | `ticker` | object |
| 3 | `symbol` | object |
| 4 | `status_prefix` | object |
| 5 | `ssr` | object |
| 6 | `flags_json` | object |
| 7 | `loose_fields` | object |
| 8 | `observed_at_utc` | object |
| 9 | `event_line_index` | int64 |
| 10 | `command` | object |
| 11 | `stage` | object |
| 12 | `raw_line` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ticker` | EDBL | ONFO | RIVN | INTC | BIYA |
| `symbol` | EDBL | ONFO | RIVN | INTC | BIYA |
| `status_prefix` | $SymStatus | $SymStatus | $SymStatus | $SymStatus | $SymStatus |
| `ssr` | Y | Y | Y | Y | Y |
| `flags_json` | {"SSR": "Y"} | {"SSR": "Y"} | {"SSR": "Y"} | {"SSR": "Y"} | {"SSR": "Y"} |
| `loose_fields` |  |  |  |  |  |
| `observed_at_utc` | 2026-07-08T19:37:48+00:00 | 2026-07-08T19:37:53+00:00 | 2026-07-08T19:38:00+00:00 | 2026-07-08T19:38:03+00:00 | 2026-07-08T19:38:08+00:00 |
| `event_line_index` | 2 | 1 | 2 | 2 | 2 |
| `command` | SB EDBL Lv1 | SB ONFO Lv1 | SB RIVN Lv1 | SB INTC Lv1 | SB BIYA Lv1 |
| `stage` | screener_lv1 | screener_lv1 | screener_lv1 | screener_lv1 | screener_lv1 |
| `raw_line` | $SymStatus EDBL SSR:Y | $SymStatus ONFO SSR:Y | $SymStatus RIVN SSR:Y | $SymStatus INTC SSR:Y | $SymStatus BIYA SSR:Y |

## Interpretacion

SymStatus/SSR sirve para revision de estado, no para certificar halt master.
