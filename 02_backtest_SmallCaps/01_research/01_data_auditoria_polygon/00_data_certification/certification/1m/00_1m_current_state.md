# 1m | Current State

`ohlcv_1m` llega con cierre operativo ya hecho en auditoría.

Base:

- [04_ohlcv_1m_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\ohlcv_1m\04_ohlcv_1m_closeout.md)
- [materialization_summary.json](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full\materialization_summary.json)
- [operational_decision_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full\root_cause_operational_outputs\operational_decision_summary.parquet)

## Punto importante de alcance

El `closeout` que encontré trabaja sobre:

- `ohlcv_1m_current_full`

No encontré artefacto paralelo ya materializado con filtro explícito `<1B>`.

Por tanto:

- la política operativa sí es reutilizable
- las proporciones brutas deben leerse como `full-scope`, no todavía como `<1B>`

## Estado materializado

- `events_rows`: `1,272,004`
- `current_rows`: `1,272,004`

Decisiones operativas brutas:

- `RESCUE_SCHEMA_PLUS_VW`: `1,063,976` (`83.65%`)
- `RESCUE_SCHEMA_ONLY`: `204,928` (`16.11%`)
- `QUARANTINE_PARSE_INVALID`: `3,049` (`0.2397%`)
- `QUARANTINE_PRICE_INVALID`: `51` (`0.0040%`)

La lectura de primer nivel ya es buena:

- el núcleo duro de cuarentena es muy pequeño
- el grueso del dataset entra por rescate, no por exclusión
