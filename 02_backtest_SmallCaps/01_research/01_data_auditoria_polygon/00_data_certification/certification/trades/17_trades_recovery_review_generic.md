# Trades | Recovery | `review`

`review` genérico sí parece recuperable en una parte muy grande, pero no como promoción ciega a `good`.

Rutas base:

- [11_trades_review_generic.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\11_trades_review_generic.md)
- [10_review_tof_2010_06_21.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\10_review_tof_2010_06_21.png)
- [raw_metrics_shards](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean_fast_same_schema\raw_metrics_shards)

## Qué cambia aquí

Al contrario de lo que parecía al principio, `review` genérico no es solo un cajón opaco.

Se puede definir un subconjunto muy grande y razonablemente limpio usando una regla simple:

- `daily_vw_to_trade_vw` cerca de `1x`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 0.5`
- `outside_daily_regular_pct <= 1`
- `outside_1m_regular_pct <= 15`

## Resultado

Sobre el estado materializado final de `57f/full_clean_fast_same_schema`:

- `review` total: `2,825,748` files
- subconjunto recuperable estricto: `2,427,056`
- peso sobre `review`: `85.89%`

Perfil del subconjunto recuperable estricto:

- `outside_daily_regular_pct` mediano: `0`
- `outside_1m_regular_pct` mediano: `1.56`
- `trade_vwap_vs_daily_vw_diff_pct_raw` mediano: `0.0267`

Y todavía existe una variante extendida:

- `daily_vw_to_trade_vw` cerca de `1x`
- `trade_vwap_vs_daily_vw_diff_pct_raw <= 1.0`
- `outside_daily_regular_pct <= 2`
- `outside_1m_regular_pct <= 20`

Resultado extendido:

- `2,557,888` files
- `90.52%` del bucket `review`

## Qué significa

Esto sugiere que una gran parte de `review` genérico no está en conflicto severo con `daily`, ni muestra la firma dura de escala o de `bad_data`.

La lectura más razonable es:

- bucket amplio de fricción comparativa leve
- no bucket masivo de deterioro real

## Caso visual

![TOF](img/10_review_tof_2010_06_21.png)

La imagen por sí sola no prueba la partición, pero sí es coherente con la lectura de residuo leve y no con un fallo estructural duro.

## Decisión

Decisión provisional:

- intentar recuperar una parte grande de `review`
- no promoverla a `good`
- sí tratarla como `recoverable_with_flag`

Lectura por uso:

- `backtest_core`
  - no
- `backtest_extended`
  - sí, con la regla estricta
- `ml_primary`
  - no por defecto
- `ml_flagged`
  - sí

## Lo que queda fuera

El resto del bucket `review` que no entra ni en la regla estricta ni en la extendida sigue siendo residuo abierto.

Ese residuo es el que conviene dejar como:

- `review` no rehabilitado
