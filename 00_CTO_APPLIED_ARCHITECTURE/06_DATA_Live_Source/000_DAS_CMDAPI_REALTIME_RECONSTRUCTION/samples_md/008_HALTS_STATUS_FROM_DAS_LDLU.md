# 008_HALTS status desde DAS LDLU - Printed Sample

## Proposito

Este documento imprime una muestra reconstruida desde la captura real-time de DAS CMD API para compararla contra la familia local auditada. No certifica la familia completa ni reemplaza los parquets historicos.

## Fuente

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| source | `DAS data_family=ldlu / prefix=$LDLU` |
| raw_events | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |

## Schema Reconstruido

| ordinal | field | type |
| --- | --- | --- |
| 0 | `run_id` | object |
| 1 | `market_date` | object |
| 2 | `ticker` | object |
| 3 | `symbol` | object |
| 4 | `limit_down` | float64 |
| 5 | `limit_up` | float64 |
| 6 | `observed_at_utc` | object |
| 7 | `event_line_index` | int64 |
| 8 | `command` | object |
| 9 | `stage` | object |
| 10 | `raw_line` | object |

## Printed Sample

La muestra esta transpuesta para lectura humana.

| field | sample_1 | sample_2 | sample_3 | sample_4 | sample_5 |
| --- | --- | --- | --- | --- | --- |
| `run_id` | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z | das_cmdapi_live_20260708T193719Z |
| `market_date` | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 | 2026-07-08 |
| `ticker` | SOXS | EDBL | AAL | ONFO | NVDA |
| `symbol` | SOXS | EDBL | AAL | ONFO | NVDA |
| `limit_down` | 3.16 | 0.0 | 14.88 | 0.0 | 183.09 |
| `limit_up` | 5.88 | 0.3 | 18.19 | 0.54 | 223.77 |
| `observed_at_utc` | 2026-07-08T19:37:46+00:00 | 2026-07-08T19:37:48+00:00 | 2026-07-08T19:37:51+00:00 | 2026-07-08T19:37:53+00:00 | 2026-07-08T19:37:56+00:00 |
| `event_line_index` | 0 | 1 | 1 | 0 | 1 |
| `command` | SB SOXS Lv1 | SB EDBL Lv1 | SB AAL Lv1 | SB ONFO Lv1 | SB NVDA Lv1 |
| `stage` | screener_lv1 | screener_lv1 | screener_lv1 | screener_lv1 | screener_lv1 |
| `raw_line` | $LDLU SOXS 3.16 5.88 | $LDLU EDBL 0 0.3 | $LDLU AAL 14.88 18.19 | $LDLU ONFO 0 0.54 | $LDLU NVDA 183.09 223.77 |

## Interpretacion

LDLU permite comparar bandas/estado operativo, no halts oficiales con resume/release.
