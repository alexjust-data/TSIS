# Trades | `reference_scale_mismatch`

Este es el bucket más claro de `trades` dentro de la política nueva.

Rutas base:

- [layer6_policy_examples.parquet](C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b\layer6_policy_examples.parquet)
- [01_reference_scale_mismatch_sga_2009_01_05.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\01_reference_scale_mismatch_sga_2009_01_05.png)
- [02_reference_scale_mismatch_lpcn_2014_07_07.png](C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades\img\02_reference_scale_mismatch_lpcn_2014_07_07.png)

## Qué significa

Aquí la lectura defendible no es:

- `trades` roto por mala calidad intrínseca

La lectura defendible es:

- `trades` raw y referencias `daily/1m` aparecen en escalas distintas
- por eso el conflicto frente a `daily` y `1m` se dispara
- pero la causa dominante parece de comparabilidad, no de corrupción física del tape

## Casos visuales

![SGA](img/01_reference_scale_mismatch_sga_2009_01_05.png)
![LPCN](img/02_reference_scale_mismatch_lpcn_2014_07_07.png)

Lectura visual defendible:

- los prints de `trades` quedan claramente desplazados de la escala de referencia
- el patrón es fuerte y no parece un puñado de outliers marginales
- la distancia es demasiado grande para tratarlo como simple microestructura o ruido

## Decisión

Decisión provisional:

- mantener `reference_scale_mismatch` como bucket propio
- clasificarlo dentro de `review`
- no tratarlo como `bad_data`
- no esconderlo dentro de `review` genérico

Razón:

- es un tipo de residuo distinto
- importante para backtest y ML
- y la propia auditoría `05` ya lo señala como explicación dominante del residuo extremo conservador
