# DAS CMDAPI vs 001_DATA_local_audit - Matriz de Comparabilidad

Run reconstruido: `das_cmdapi_live_20260708T193719Z`

Esta matriz indica que se puede reconstruir desde la captura real-time DAS y contra que familia local puede compararse. La comparacion es de forma, cobertura y valores cuando exista la misma fecha/simbolo; no promociona DAS a Data Foundation.

| familia_local | fuente_DAS | comparabilidad | que permite comparar | limite |
| --- | --- | --- | --- | --- |
| 000_TRADES | tms / $T&S | Si, parcial-directa | prints live: ticker, timestamp inferido, price, size, venue/condition DAS | No hay exchange numerico Polygon ni condiciones SIP identicas. |
| 001_QUOTES | lv1 / $Quote + lv2 / $Lv2 | Si, parcial | bid/ask/size/last/volume/VWAP/RVOL y profundidad DAS Lv2 | No hay participant_timestamp, sequence_number, TRF ni NBBO SIP completo. |
| 002_DAILY | daychart / $Bar | Si, parcial | barras diarias DAS para candidatos y rango consultado | No reemplaza daily foundation; usar solo source parity/comparacion. |
| 003_DAILY_ADJUSTED | ninguna directa | No desde DAS solo | DAS no aporta split/dividend adjustment factors | Requiere corporate actions/factores de Data Foundation. |
| 004_1_MINUTE | tms agregado + minchart_1m | Si, parcial-directa | OHLCV 1m reconstruido desde prints y barras MINCHART DAS | Ventana de ~29 minutos y universo PASS, no full universe. |
| 005_1_MINUTE_SPLIT_NORMALIZED | tms/minchart + corporate actions externo | No desde DAS solo | Se podria derivar despues de unir factores split | DAS no trae factores futuros ni vista split-normalized. |
| 006_ADDITIONALS | ninguna directa | No | Solo hay metadata/candidatos | No hay datasets additional tipo IPO/economic/etc. |
| 007_REFERENCE | candidate_registry/toplist/market_cap_ref | Si, parcial | simbolos, filtros, market cap de referencia, estado PASS/FAIL | No es instrument_master completo. |
| 008_HALTS | ldlu + symstatus | Si, parcial | LDLU, SSR y flags de estado | No equivale a halt master con issuer/release/resume official. |
| 009_SHORT | shortinfo | Si, parcial | SHORTINFO posicional DAS por candidato PASS | No equivale a FINRA short_interest settlement table. |
| 010_SHORT_REVIEW | shortinfo | Si, parcial | misma base para revision short | No reconstruye la capa review institucional completa. |

## Regla de Uso

- El raw audit truth sigue siendo `E:\TSIS\data_DAS_live\raw_cmdapi\runs\das_cmdapi_live_20260708T193719Z`.
- Las tablas reconstruidas son derivadas y sirven para inspeccion/comparacion.
- Si la familia historica no contiene `2026-07-08`, la comparacion sera de schema/source parity, no row-level.
- `account_state` no se copia a la auditoria local por sensibilidad operacional.
