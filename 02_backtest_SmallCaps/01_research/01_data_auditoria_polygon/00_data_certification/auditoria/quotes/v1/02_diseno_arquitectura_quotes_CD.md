# Arquitectura y estado actual `quotes` C+D

## Propósito de este documento

Este fichero ya no es solo un diseño teórico.

Debe servir como handoff operativo para el siguiente agente:

- qué arquitectura se decidió
- qué está ya implantado
- qué resultados han salido
- qué problemas siguen abiertos
- qué falta para cerrar la auditoría

## Contexto

Dataset principal auditado:

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet`

Parquets auxiliares:

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_full_sharded_merged\quotes_current.parquet`
- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_c_full_sharded_merged\quotes_current.parquet`

Magnitud del parquet `C+D`:

- filas: `9,930,334`
- tamaño parquet: `2,310,171,358 bytes`
- rango temporal: `2005-01-03` a `2026-03-20`

## Veredicto sobre el patrón de `trades`

El diseño de `trades` C+D era correcto como patrón arquitectónico:

- separar `build / view / drilldown`
- sacar el cálculo pesado fuera de Jupyter
- usar `case_index`
- mantener forense puntual sobre raw

Pero no era correcto copiarlo literalmente a `quotes`.

Motivo:

- `quotes` no gira alrededor de `daily breaks` o validación contra `1m`
- `quotes` gira alrededor de microestructura:
  - `crossed_ratio_pct`
  - `crossed_rows`
  - `timestamp_out_of_partition_day`
  - enterización de `ask`
  - redondeo `ask` vs `bid`
  - mezcla `C/D`
  - anatomía de files pequeños

Conclusión:

- sí, el patrón base de `trades` sirve
- no, la semántica de `trades` no debe copiarse a `quotes`

## Arquitectura decidida

La arquitectura correcta para `quotes` C+D es:

1. `build`
   Script pesado fuera de Jupyter que recorre el parquet full en streaming y genera artefactos pequeños.

2. `view`
   Notebook Jupyter que consume solo caches pequeños, tablas agregadas, muestras e índices.

3. `drilldown`
   Carga puntual del `quotes.parquet` raw para un caso concreto.

Regla operativa:

- Jupyter no debe procesar el parquet full
- Jupyter debe visualizar artefactos precomputados
- el raw solo se toca al abrir un caso puntual o al regenerar artefactos

## Objetivo técnico

Evitar que el notebook:

- cargue `C+D`, `C` y `D` completos en pandas
- expanda `metrics_json` masivamente
- materialice `issues_list` y `warns_list` sobre millones de filas
- repita lecturas full por bloque

## Implementación realizada

### Scripts y notebook modificados

- loader principal:
  - [00_load_quotes_run_artifacts.py](C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/auditoria/quotes/v1/cell_code/00_load_quotes_run_artifacts.py)

- builder offline:
  - [build_quotes_cd_audit_artifacts.py](C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/auditoria/quotes/v1/cell_code/build_quotes_cd_audit_artifacts.py)

- notebook refactorizado:
  - [03_quotes_full_C_D_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/auditoria/quotes/v1/03_quotes_full_C_D_audit.ipynb)

- ajuste de resumen ejecutivo:
  - [17_cd_exec_summary.py](C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/auditoria/quotes/v1/cell_code/17_cd_exec_summary.py)

### Componentes implantados

Se implantó `QuotesAuditHandle` para:

- `row_count()`
- `iter_batches(columns, batch_size=...)`
- `cache_path(...)`

Se dejaron builders/caches para:

- `snapshot`
- `severity_counts`
- `root_mix`
- `hard_issue_counts`
- `warn_counts`
- `issue_root_view`
- `warn_severity_view`
- `month_rate`
- `year_rate`
- `ticker_focus_top30`
- `crossed_band`
- `micro_sample`
- `integer_anomaly`
- `timestamp_view`
- `focus_examples`
- `forensic_candidates`
- `taxonomy_summary`
- `case_index`
- `manifest`

## Ruta real de cache

El cache real usado en la implementación quedó en:

- `C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache`

Se usó esa ruta para evitar problemas de permisos al escribir dentro de `C:\TSIS_Data\...`.

## Comando de build completo

Comando ejecutado:

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v1\cell_code\build_quotes_cd_audit_artifacts.py
```

Resultado observado:

- duración: `2547.69s`
- `row_count`: `9,930,334`
- `snapshot_rows_total`: `9,930,334`
- `top_hard_issue`: `crossed_ratio_gt_threshold`
- `top_warn`: `crossed_rows_present_but_under_threshold`
- `top_taxonomy`: `clean_pass_or_other`
- `artifacts_written`: `22`

## Manifest y artefactos

Manifest real:

- `C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache\manifest_cd.json`

Campos importantes observados:

- `builder_version`: `quotes_cd_v1`
- `source_parquet`: `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet`
- `row_count`: `9930334`

Artefactos presentes:

- `case_index_top50_cd.parquet`
- `concentration_inputs_cd.parquet`
- `crossed_band_cd.parquet`
- `focus_examples_*.parquet`
- `forensic_candidates_*.parquet`
- `hard_issue_counts_cd.parquet`
- `integer_anomaly_cd.parquet`
- `issue_root_view_cd.parquet`
- `manifest_cd.json`
- `micro_sample_cd.parquet`
- `month_rate_cd.parquet`
- `root_mix_cd.parquet`
- `severity_counts_cd.parquet`
- `snapshot_cd.parquet`
- `snapshot_inputs_cd.parquet`
- `taxonomy_summary_cd.parquet`
- `ticker_focus_top30_cd.parquet`
- `timestamp_view_cd.parquet`
- `warn_counts_cd.parquet`
- `warn_severity_view_cd.parquet`
- `year_rate_cd.parquet`

## Observación importante sobre artefactos intermedios

Han quedado dos artefactos grandes e intermedios:

- `snapshot_inputs_cd.parquet`
- `concentration_inputs_cd.parquet`

No bloquean el flujo, pero no encajan con el ideal final de “solo artefactos pequeños”.

Deuda técnica abierta:

- limpiar esos artefactos del pipeline final si ya no son necesarios

## Corrección importante realizada durante la auditoría

### Problema detectado

Los tokens de `issues` y `warns` estaban mal parseados.

Aparecían valores concatenados como:

- `crossed_ratio_gt_hard_capcrossed_ratio_gt_threshold`
- `crossed_rows_present_but_under_thresholdtimestamp_out_of_partition_day`

La causa era el formato real del parquet, que no venía como lista Python normal con comas, sino como representación tipo numpy:

- `['a' 'b']`
- `['a'\n 'b']`

Además, `ast.literal_eval("['a' 'b']")` concatena strings adyacentes y produce `'ab'`.

### Solución aplicada

Se corrigió `_parse_token_list(...)` en [00_load_quotes_run_artifacts.py](C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/auditoria/quotes/v1/cell_code/00_load_quotes_run_artifacts.py):

- primero extrae tokens por regex entre comillas
- solo después intenta `ast.literal_eval(...)`

### Regeneración parcial ejecutada

Se regeneraron artefactos afectados con progreso por terminal:

- `root_cause`
- `microstructure`
- `focus_examples`
- `taxonomy`
- `case_index`

Duración observada:

- `1517.7s`

## Estado actual del notebook

Notebook:

- [03_quotes_full_C_D_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/auditoria/quotes/v1/03_quotes_full_C_D_audit.ipynb)

Situación:

- ya no hace preload full de `C+D`, `C` y `D`
- consume artefactos desde cache
- el bloque forense carga raw puntual desde `file`
- se corrigió la celda final para no hacer `float()` sobre una `Series`

## Qué salidas se validaron

### Snapshot

- `rows_total`: `9,930,334`
- `ticker_n`: `5,207`
- `root_c_rows`: `1,767,658`
- `root_d_rows`: `8,162,676`
- `rows_median`: `1,716`
- `rows_p90`: `14,976`
- `rows_p99`: `66,718.04`
- `crossed_ratio_median_pct`: `0.003695`
- `crossed_ratio_p99_pct`: `16.666667`
- `timestamp_out_of_partition_rows`: `743,148`

### Severidad

- `PASS`: `4,554,569` (`45.87%`)
- `SOFT_FAIL`: `4,285,486` (`43.16%`)
- `HARD_FAIL`: `1,090,279` (`10.98%`)

### Root cause corregido

`hard_issue_counts` tras corregir parser:

- `crossed_ratio_gt_threshold`: `1,090,279`
- `crossed_ratio_gt_hard_cap`: `348,895`
- `ask_integer_with_crossed_anomaly`: `6,967`

`warn_counts` tras corregir parser:

- `crossed_rows_present_but_under_threshold`: `3,927,750`
- `timestamp_out_of_partition_day`: `743,148`

### Concentración

Se validó:

- `month_rate_cd.parquet`
- `year_rate_cd.parquet`
- `ticker_focus_top30_cd.parquet`

Lectura rápida:

- el hard fail cae claramente en 2025-2026 frente a años anteriores
- hay tickers muy concentrados en hard fail

### Microestructura

Se validó:

- `integer_anomaly_cd.parquet`
- `timestamp_view_cd.parquet`
- `micro_sample_cd.parquet`
- `crossed_band_cd.parquet`

Hallazgos:

- existen files con `crossed_ratio_pct = 100`
- existen casos con `ask_price = 0`
- el bloque de timestamp drift es real y no cosmético

### Taxonomía corregida

Top taxonomías tras corrección:

- `clean_pass_or_other`: `45.83%`
- `mild_crossed_micro_noise`: `20.67%`
- `persistent_soft_crossed_market`: `15.37%`
- `moderate_crossed_market`: `4.13%`
- `timestamp_partition_shift`: `3.60%`
- `soft_crossed_plus_timestamp_shift`: `3.51%`
- `hard_crossed_market`: `3.44%`
- `small_file_hard_crossed`: `3.33%`

Observación:

- la separación entre `timestamp_partition_shift` y `soft_crossed_plus_timestamp_shift` quedó correcta tras la corrección del parser

### Forense puntual

Se validó carga raw real.

Caso ejemplo:

- `TOP_FORENSIC_FILE`: `D:\quotes\CAK\year=2009\month=02\day=26\quotes.parquet`

Resultado:

- `raw_shape`: `(45, 16)`
- columnas raw presentes
- se observó `ask_price = 0.0` frente a `bid_price = 7.65`
- caso consistente con `crossed_ratio_pct = 100`

## Conclusión sobre la calidad de la data

No puede decirse que la data esté saneada.

Sí puede decirse que está ya auditada, estructurada y segmentada.

Lectura operativa:

- el universo no está roto globalmente
- pero sigue habiendo un residuo material de `HARD_FAIL`, `SOFT_FAIL`, drift temporal y anomalías microestructurales reproducibles

Frase recomendada para documentación:

> El dataset `quotes C+D` no puede considerarse saneado a fecha actual. Sí puede considerarse auditado y segmentado en familias operativas, con una fracción material de residuo todavía presente en forma de `HARD_FAIL`, `SOFT_FAIL`, drift temporal y anomalías microestructurales reproducibles.

## Qué se ha logrado

- evitar el crash de memoria virtual en la primera celda del notebook
- mover el cálculo pesado fuera de Jupyter
- generar artefactos reutilizables
- construir snapshot, root cause, concentración, microestructura, ejemplos, taxonomía y forense
- dejar el notebook funcional como visor de artefactos
- validar casos raw reales
- corregir el parser de `issues/warns`

## Qué falta

### Pendiente funcional

- reejecutar en notebook las celdas afectadas tras la corrección del parser:
  - root cause
  - microestructura
  - focus examples
  - forense
  - taxonomía
  - resumen ejecutivo

### Pendiente de producto

- enriquecer `case_index` para navegación más rica por `taxonomy`, `root`, `focus_issue`, `focus_warn`
- decidir si hace falta un widget forense más sofisticado o si el actual es suficiente

### Pendiente técnico

- limpiar artefactos intermedios grandes si dejan de ser necesarios
- decidir si la ruta de cache final debe quedarse en `C:\Users\AlexJ\.codex\memories\...` o moverse a otra ruta de trabajo documentada
- valorar si conviene añadir `build_log.json` con tiempos por bloque

## Qué debe hacer el siguiente agente

1. Abrir [03_quotes_full_C_D_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/notebooks/00_data_certification/auditoria/quotes/v1/03_quotes_full_C_D_audit.ipynb).
2. Reejecutar celdas afectadas tras la corrección del parser.
3. Confirmar que en el notebook ya no aparecen tokens concatenados en root cause.
4. Confirmar que la taxonomía mostrada en notebook coincide con la regenerada fuera de Jupyter.
5. Decidir si se hace una segunda fase de limpieza de artefactos intermedios y enriquecimiento de `case_index`.

## Veredicto final de estado

Estado actual:

- arquitectura correcta: `sí`
- notebook usable sin cargar full parquet: `sí`
- artefactos completos construidos: `sí`
- parser de `issues/warns` corregido: `sí`
- notebook completamente refrescado después de la corrección del parser: `pendiente`
- data saneada: `no`
- data auditada y segmentada: `sí`
