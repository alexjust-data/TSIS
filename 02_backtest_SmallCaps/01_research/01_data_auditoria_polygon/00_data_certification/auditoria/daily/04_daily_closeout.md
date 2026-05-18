# 04_daily_closeout

## Objetivo

Este documento acompaña al cierre ejecutivo de `daily` para el universo `<1B>`, filtrado desde el run full `v030`.

## Diagnóstico final

`daily` `<1B>` no presenta evidencia de corrupción masiva del dataset.

La lectura correcta queda separada en tres bloques:

- `schema`: anomalía estructural conocida y transversal
- `vw`: residuo económico que debe abrirse por régimen y no por una sola etiqueta `severe`
- `parse/precio`: núcleo duro pequeño pero real

## Qué se demostró

- gran parte del `severe` actual de `v030` cae por regla de borde:
  - `abs_max >= 1.0`
  - solo `1-2` días afectados
  - ratio muy bajo, típicamente `0.4%` o `0.8%`
- otro bloque de `vw` persistente aparece en años muy ilíquidos:
  - muchas barras planas o casi planas
  - `n` muy bajo
  - `v` muy bajo
  - `vw` ligeramente fuera del rango `high/low`

Esto es mucho más compatible con régimen de construcción del bar y micro-liquidez que con corrupción arbitraria del `daily`.

## Núcleo duro real `<1B>`

Dentro de `<1B>`, el tail duro queda en `102` files sobre `44,423`.

Desglose:

- `19` casos `all_rows_invalid_after_parse`
- `29` casos `negative_or_zero_ohlc_rows`
- `54` casos `negative_or_zero_ohlc_rows` junto con `vw_outside_range_severe`

Lectura forense:

- los `parse_only` no son una falsa alarma del validador
- aparecen files con precios astronómicos y `v = 0`, `vw = NaN`
- también aparecen files con `o = h = l = c = 0` y volumen positivo

Ejemplos observados:

- `ASTI 2006` y `TOPS 2008`: precios del orden `1e13` o `1e14`, `v = 0`, `vw = NaN`
- `TLOG 2024` y `BSPM 2021`: filas con `o = h = l = c = 0`

Por tanto, este bloque sí debe mantenerse en `bad`.

## Buckets refinados

- `schema_only_or_other`
- `vw_edge_absmax_only`
- `vw_low_ratio_limited_days`
- `vw_mid_ratio_illiquid_regime`
- `vw_high_ratio_illiquid_regime`
- `hard_invalid_parse_or_price`

## Política good review bad

- `good`
  - `schema_only_or_other`
  - `vw_edge_absmax_only`
- `review`
  - `vw_warn_minor_or_material`
  - `vw_low_ratio_limited_days`
  - `vw_mid_ratio_illiquid_regime`
  - `vw_high_ratio_illiquid_regime`
- `bad`
  - `hard_invalid_parse_or_price`

## Estado de cierre

`daily` `<1B>` queda cerrado a nivel de auditoría operativa.

La conclusión rigurosa no es “daily no tiene ni un solo error”, sino esta:

- `daily` `<1B>` está ampliamente sano como dataset
- el problema dominante de `vw` queda explicado por borde de regla e iliquidez extrema
- el único residuo verdaderamente duro es un tail pequeño de parse/precio inválido que debe mantenerse fuera del core

## Artefacto operativo de exclusión

Queda materializado un exclusion set canónico para consumo directo por backtesting, spine común o ML:

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_exclusion.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_exclusion.csv`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_ticker_year.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_ticker_year.csv`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\daily_v2_audit\daily_lt1b_hard_invalid_exclusion_v030\daily_lt1b_hard_invalid_exclusion_summary.json`

Resumen:

- `files_excluded = 102`
- `ticker_year_excluded = 102`
- `tickers_excluded = 54`

Uso operativo recomendado:

- excluir estos `ticker-year` del core dataset `daily <1B>`
- mantener el resto de `daily <1B>` bajo la política `good / review / bad` ya fijada
