# Short | Current State

`short` queda aceptado, pero no en terminos simetricos entre providers.

Base:

- [04_short_closeout.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\04_short_closeout.md)
- [cobertura_short_data.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\cobertura_short_data.md)

## Provider baseline

`short_volume`:

- Polygon:
  - `2024-02-06 -> 2026-04-02`
  - `3,381` tickers con filas
- FINRA:
  - `2018-08-01 -> 2026-04-29`
  - `4,623` tickers con filas

`short_interest`:

- providers bastante mas cercanos
- FINRA sigue siendo la referencia preferida

## Conclusion base

- `FINRA short_volume` = baseline oficial
- `FINRA short_interest` = baseline oficial contextual
- `Polygon short` = comparativo secundario

## Matiz importante sobre `only_polygon`

Base:

- [short_only_polygon_tickers.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\cache_v2\short_only_polygon_tickers.parquet)
- [short_outside_life_window.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\cache_v2\short_outside_life_window.parquet)
- [short_possible_reuse_mix.parquet](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\short\cache_v2\short_possible_reuse_mix.parquet)

El conteo bruto de `338 only_polygon` sobrestima el gap real de proveedor.

Desglose directo del parquet:

- `short_interest`: `137` rows `only_polygon`
  - con filas reales Polygon: `7`
  - placeholders vacios: `130`
- `short_volume`: `201` rows `only_polygon`
  - con filas reales Polygon: `19`
  - placeholders vacios: `182`

Ademas:

- `short_outside_life_window`: `25`
- `short_possible_reuse_mix`: `66`

Lectura:

- el problema principal no es que Polygon aporte cientos de tickers utiles que FINRA no tiene
- el problema real es mezcla de placeholders, tickers transitorios y ventanas de vida dudosas
- por eso `FINRA` no solo gana por cobertura, sino por limpieza semantica del baseline
