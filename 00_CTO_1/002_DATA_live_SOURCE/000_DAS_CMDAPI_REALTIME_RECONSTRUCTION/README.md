# DAS CMDAPI Realtime Reconstruction vs 001_DATA_local_audit

## Proposito

Esta carpeta reconstruye todo lo razonable desde la captura real-time de DAS CMD API para poder compararlo contra las familias de `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit`.

No es una promocion de DAS a Data Foundation. Es una capa derivada de inspeccion, reconciliacion y source parity.

## Fuente Primaria

| item | value |
| --- | --- |
| run_id | `das_cmdapi_live_20260708T193719Z` |
| raw_run | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z` |
| screener_run | `E:\TSIS\data_DAS_live\screener\runs\das_cmdapi_live_20260708T193719Z` |
| events_jsonl | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\events.jsonl` |
| candidate_registry | `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z\candidate_registry.jsonl` |

## Conteo Por Familia DAS

| data_family | event_rows |
| --- | --- |
| tms | 65590 |
| lv2 | 36327 |
| lv1 | 35174 |
| minchart_1m | 979 |
| session | 185 |
| ldlu | 179 |
| symstatus | 140 |
| daychart | 104 |
| shortinfo | 18 |
| toplist | 13 |
| account_state | 2 |

## Simbolos Con Mas Eventos

| symbol | event_rows |
| --- | --- |
| TVRD | 34887 |
| SKYQ | 23936 |
| NVVE | 20081 |
| SRXH | 18278 |
| SDOT | 12156 |
| VTAK | 9489 |
| LHAI | 3725 |
| LUCY | 3170 |
| CLRO | 2690 |
| VANI | 2226 |
| ZCMD | 1693 |
| JEM | 1442 |
| VEEE | 1208 |
| BTAI | 1031 |
| BJDX | 816 |
| INLF | 658 |
| VMAR | 520 |
| BBLG | 173 |
| INTC | 8 |
| ONFO | 6 |

## Tablas Normalizadas Escritas

| dataset | rows | path |
| --- | --- | --- |
| daychart | 104 | `E:\TSIS\data_DAS_live\normalized\daychart\market_date=2026-07-08` |
| ldlu | 179 | `E:\TSIS\data_DAS_live\normalized\ldlu\market_date=2026-07-08` |
| lv1 | 35081 | `E:\TSIS\data_DAS_live\normalized\lv1\market_date=2026-07-08` |
| lv2 | 36319 | `E:\TSIS\data_DAS_live\normalized\lv2\market_date=2026-07-08` |
| minchart_1m | 979 | `E:\TSIS\data_DAS_live\normalized\minchart_1m\market_date=2026-07-08` |
| ohlcv_1m_from_tms | 391 | `E:\TSIS\data_DAS_live\normalized\ohlcv_1m_from_tms\market_date=2026-07-08` |
| shortinfo | 18 | `E:\TSIS\data_DAS_live\normalized\shortinfo\market_date=2026-07-08` |
| symstatus | 140 | `E:\TSIS\data_DAS_live\normalized\symstatus\market_date=2026-07-08` |
| tms | 65590 | `E:\TSIS\data_DAS_live\normalized\tms\market_date=2026-07-08` |
| toplist | 240 | `E:\TSIS\data_DAS_live\normalized\toplist\market_date=2026-07-08\data.parquet` |

## Indices Escritos

| dataset | rows | path |
| --- | --- | --- |
| candidate_daily_index | 136 | `E:\TSIS\data_DAS_live\indexes\candidate_daily_index\market_date=2026-07-08\candidates.parquet` |
| run_index | 1 | `E:\TSIS\data_DAS_live\indexes\run_index.parquet` |

## Tablas Local-like Para Comparacion

| dataset | rows | path |
| --- | --- | --- |
| 000_TRADES_from_das_tms | 65590 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\000_TRADES_from_das_tms.parquet` |
| 001_QUOTES_depth_from_das_lv2 | 36319 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\001_QUOTES_depth_from_das_lv2.parquet` |
| 001_QUOTES_from_das_lv1 | 35081 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\001_QUOTES_from_das_lv1.parquet` |
| 002_DAILY_from_das_daychart | 104 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\002_DAILY_from_das_daychart.parquet` |
| 004_1_MINUTE_from_das_minchart | 979 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\004_1_MINUTE_from_das_minchart.parquet` |
| 004_1_MINUTE_from_das_tms | 391 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\004_1_MINUTE_from_das_tms.parquet` |
| 007_REFERENCE_from_das_candidate_registry | 136 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\007_REFERENCE_from_das_candidate_registry.parquet` |
| 008_HALTS_STATUS_from_das_ldlu | 179 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\008_HALTS_STATUS_from_das_ldlu.parquet` |
| 008_HALTS_STATUS_from_das_symstatus | 140 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\008_HALTS_STATUS_from_das_symstatus.parquet` |
| 009_SHORT_from_das_shortinfo | 18 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\009_SHORT_from_das_shortinfo.parquet` |
| 010_SHORT_REVIEW_from_das_shortinfo | 18 | `C:\TSIS_Data\00_CTO_1\001_DATA_local_audit\011_DAS_CMDAPI_REALTIME_RECONSTRUCTION\reconstructed_local_like\010_SHORT_REVIEW_from_das_shortinfo.parquet` |

## Lectura Correcta

- `000_TRADES`, `001_QUOTES` y `004_1_MINUTE` son las comparaciones principales.
- `002_DAILY` se puede comparar con `DAYCHART`, pero como fuente DAS externa.
- `008_HALTS` y `009_SHORT` son comparables solo como estado live/operativo parcial.
- `003_DAILY_ADJUSTED`, `005_1_MINUTE_SPLIT_NORMALIZED` y `006_ADDITIONALS` no se reconstruyen desde DAS sin fuentes externas.
- `account_state` queda excluido de esta carpeta por sensibilidad.

## Documentos De Muestra

Ver `samples_md/` para muestras transpuestas por familia comparable.
