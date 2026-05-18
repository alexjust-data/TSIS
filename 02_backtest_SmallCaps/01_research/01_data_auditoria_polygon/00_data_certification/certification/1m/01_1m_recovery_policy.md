# 1m | Recovery Policy

En `1m`, la estrategia correcta también es recuperar lo máximo posible.

## Recuperación ya materializada

La propia auditoría ya parte el universo así:

- `RESCUE_SCHEMA_ONLY`
- `RESCUE_SCHEMA_PLUS_VW`
- `QUARANTINE_PARSE_INVALID`
- `QUARANTINE_PRICE_INVALID`

Eso ya indica que el enfoque no es “tirar todo lo raro”, sino rescatar por capas.

## `price_invalid`

Hay un matiz útil para recuperación:

- `51` casos `price_invalid`
- `47` `QUARANTINE_ZERO_STRUCTURAL`
- `4` `RESCUE_FILTER_ZERO_ROWS`

Base:

- [price_invalid_resolution.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full\root_cause_operational_outputs\price_invalid_resolution.parquet)
- [price_invalid_resolution_summary.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\ohlcv_1m_v2_materialized\ohlcv_1m_current_full\root_cause_operational_outputs\price_invalid_resolution_summary.parquet)

La lectura correcta es:

- incluso dentro de `price_invalid` no todo es pérdida
- una parte pequeña ya quedó rescatada filtrando filas cero

## Lectura fuerte del bloque

`1m` no entra como dataset dominado por cuarentena.

Entra como:

- dataset donde la inmensa mayoría ya pasa por vías de rescate
- con un tail duro muy pequeño de parse/precio inválido
