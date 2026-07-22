# Daily | Quality Policy

La política de calidad de `daily` ya sale muy bien definida desde `04_daily_closeout.md`.

## Buckets operativos

- `schema_only_or_other`
- `vw_edge_absmax_only`
- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `hard_invalid_parse_or_price`

## Lectura correcta

La mayor parte del residuo `vw` no se comporta como corrupción arbitraria.

Se comporta como:

- borde de regla
- años muy ilíquidos
- barras planas o casi planas
- `vw` ligeramente fuera de `high/low`

El único núcleo duro real es:

- `hard_invalid_parse_or_price`

Desglose del exclusion set:

- `19` `all_rows_invalid_after_parse`
- `29` `negative_or_zero_ohlc_rows`
- `54` `negative_or_zero_ohlc_rows + vw_outside_range_severe`

## Política final

- `good`
  - `schema_only_or_other`
  - `vw_edge_absmax_only`
- `review`
  - `vw_low_ratio_limited_days`
  - `vw_mid_ratio_illiquid_regime`
  - `vw_high_ratio_illiquid_regime`
- `bad`
  - `hard_invalid_parse_or_price`

## Recuperación

En `daily`, la recuperación máxima defendible es:

- recuperar casi todo el residuo `vw`
- excluir solo el tail duro de `102`

Ese es precisamente el resultado que ya materializa:

- [daily_lt1b_hard_invalid_exclusion.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_exclusion.parquet)
