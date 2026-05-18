# Trades | Recovery | `review_1m_reference_alignment`

Este bucket es pequeño, pero sí admite una política explícita de recuperación limitada.

Rutas base:

- [05_trades_review_1m_reference_alignment.md](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\05_trades_review_1m_reference_alignment.md)
- [05_review_1m_reference_alignment_relv_2018_06_07.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\05_review_1m_reference_alignment_relv_2018_06_07.png)
- [06_review_1m_reference_alignment_metc_2021_03_22.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\06_review_1m_reference_alignment_metc_2021_03_22.png)
- [raw_metrics_shards](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean_fast_same_schema\raw_metrics_shards)

## Por qué puede recuperarse parcialmente

Sobre el estado materializado final de `57f/full_clean_fast_same_schema`:

- `3,970` files
- `has_1m_reference = True` en `100%`
- `daily_vw_to_trade_vw` queda muy cerca de `1x` en la masa principal
- el conflicto dominante se concentra contra `1m`

La lectura es:

- no es bucket de escala extrema
- no es bucket de falta de referencia
- es bucket de conflicto específico entre tape y `1m`

## Qué se puede recuperar

No conviene promoverlo a `good`.

Sí conviene tratar una parte como:

- `recoverable_with_flag`
- y, según uso, `ml_flagged`

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

- alineación fuerte frente a `daily`
- sin señal de `bad_data`
- sin firma de `reference_scale_mismatch`
- conflicto con `1m` acotado y documentado

Semánticamente:

- sigue siendo `review`
- pero con posibilidad de rehabilitación de uso limitado

## Casos visuales

![RELV](img/05_review_1m_reference_alignment_relv_2018_06_07.png)
![METC](img/06_review_1m_reference_alignment_metc_2021_03_22.png)

Lectura visual:

- la rareza no está en `daily`
- tampoco en ausencia de referencia
- está en la relación operativa con `1m`

## Decisión

Decisión provisional:

- tratarlo como bucket recuperable con limitación
- no promoverlo a `good`
- mantenerlo por ahora como `review` rehabilitable
