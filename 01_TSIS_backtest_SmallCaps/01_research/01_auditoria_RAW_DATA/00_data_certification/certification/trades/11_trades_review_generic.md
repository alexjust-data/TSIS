# Trades | `review`

Este bucket es grande, pero su lectura ya es defendible.

Rutas base:

- [raw_metrics_shards](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean_fast_same_schema\raw_metrics_shards)
- [10_review_tof_2010_06_21.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\10_review_tof_2010_06_21.png)

## Qué significa

La lectura defendible aquí no es:

- raw roto
- ni `scale mismatch` masivo

La lectura defendible es:

- bucket intermedio de comparabilidad imperfecta
- normalmente cerca de `1x`
- con conflicto intradía más visible contra `1m` que contra `daily`

Sobre el estado materializado final de `57f/full_clean_fast_same_schema`:

- `review`: `2,825,748` files
- `daily_vw_to_trade_vw` cerca de `1x` en `96.90%`
- señal extrema de escala en `0.038%`
- `trade_vwap_vs_daily_vw_diff_pct_raw >= 20%` en `0.035%`

Eso lo separa claramente de:

- `reference_scale_mismatch`
- `bad_data`

## Caso visual

![TOF](img/10_review_tof_2010_06_21.png)

Lectura visual defendible:

- el tape no aparece desplazado en bloque respecto a la referencia
- tampoco muestra el patrón más duro de `bad_data`
- el residuo encaja mejor con fricción de comparabilidad intradía y no con fallo estructural severo

## Decisión

Decisión provisional:

- mantener `review` como `review`
- no promoverlo a `good` por defecto
- no tratarlo como `bad`

Razón:

- su masa principal es demasiado amplia y heterogénea para asumir limpieza plena
- pero no tiene la firma de escala extrema ni de deterioro severo que justificaría degradarlo en bloque
