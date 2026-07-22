# Trades | `review_microstructure`

Este bucket sí merece tratamiento propio porque captura un patrón distinto de `reference_scale_mismatch` y de `bad_data`.

Rutas base:

- [layer6_policy_examples.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b\layer6_policy_examples.parquet)
- [03_review_microstructure_qrteb_2019_07_24.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\03_review_microstructure_qrteb_2019_07_24.png)
- [04_review_microstructure_czfs_2022_08_11.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\04_review_microstructure_czfs_2022_08_11.png)

## Qué significa

Aquí el conflicto observado en `trades` no parece dominado por:

- escala extrema
- ruptura física del file

Parece dominado por:

- odd-lots muy pesados
- núcleo `round-lot` pequeño
- comparabilidad imperfecta contra `daily/1m`

## Casos visuales

![QRTEB](img/03_review_microstructure_qrteb_2019_07_24.png)
![CZFS](img/04_review_microstructure_czfs_2022_08_11.png)

Lectura visual defendible:

- el tape no se ve simplemente “corrupto”
- el conflicto no tiene la firma típica de `reference_scale_mismatch`
- el peso de prints no core / odd-lot complica mucho la comparación directa con referencias

## Decisión

Decisión provisional:

- mantener `review_microstructure` como bucket propio
- dejarlo dentro de `review`
- no promoverlo a `good`
- no tratarlo como `bad_data`

Razón:

- la propia auditoría `05` lo interpreta como comparabilidad difícil dominada por microestructura
- visualmente los casos son coherentes con esa lectura
