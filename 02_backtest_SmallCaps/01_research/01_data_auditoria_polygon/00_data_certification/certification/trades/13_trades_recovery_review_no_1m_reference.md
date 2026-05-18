# Trades | Recovery | `review_no_1m_reference`

Este es el mejor candidato inicial de recuperación dentro de `trades`.

Rutas base:

- [09_trades_review_no_1m_reference.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\09_trades_review_no_1m_reference.md)
- [09_review_no_1m_reference_glbl_2024_09_19.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\09_review_no_1m_reference_glbl_2024_09_19.png)
- [raw_metrics_shards](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean_fast_same_schema\raw_metrics_shards)

## Por qué es recuperable

Sobre el estado materializado final de `57f/full_clean_fast_same_schema`:

- `4,456` files
- `daily_vw_to_trade_vw` cerca de `1x` en `99.98%`
- señal extrema de escala en `0%`
- `trade_vwap_vs_daily_vw_diff_pct_raw >= 20%` en `0%`
- `has_1m_reference = False` en `100%`

La lectura es consistente:

- no es bucket de escala
- no es bucket de raw roto
- no es bucket de conflicto severo contra `daily`
- es bucket de falta de ancla `1m`

## Qué se puede recuperar

No conviene promoverlo entero a `good`.

Sí conviene plantear recuperación como:

- `recoverable_with_flag`
- y, según uso, `recoverable_for_ml`

Primera lectura por uso:

- `backtest_core`
  - no
- `backtest_extended`
  - sí, con flag
- `ml_primary`
  - no por defecto
- `ml_flagged`
  - sí

## Regla provisional de recuperación

Subconjunto recuperable si además cumple:

- `daily_vw_to_trade_vw` muy cerca de `1x`
- `trade_vwap_vs_daily_vw_diff_pct_raw` bajo
- sin señal de `bad_data`
- sin señal de `reference_scale_mismatch`

Semánticamente:

- no queda como `good`
- queda como `review` recuperado
- usable con limitación explícita por falta de referencia `1m`

## Caso visual

![GLBL](img/09_review_no_1m_reference_glbl_2024_09_19.png)

Lectura visual:

- el problema visible no es rotura estructural del tape
- la comparación base de precio sigue siendo razonable
- lo que falta es confirmación intradía fina

## Decisión

Decisión provisional:

- intentar recuperar este bucket antes que los demás
- no promoverlo aún a `good`
- sí tratarlo como candidato fuerte a `review` rehabilitado / `recoverable_with_flag`
