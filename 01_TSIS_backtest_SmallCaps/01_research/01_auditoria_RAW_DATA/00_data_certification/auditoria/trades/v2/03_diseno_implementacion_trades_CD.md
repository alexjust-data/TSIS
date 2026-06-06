# Estado Real De Implementación `trades` C+D

## Objetivo de este documento

Este `.md` ya no debe leerse como diseño teórico, sino como documento de handoff para el siguiente agente.

Su función es dejar claro:

- en qué punto estamos realmente
- qué se ha implementado ya
- qué problemas se han resuelto
- qué artefactos existen
- qué notebook es el que hay que usar
- qué falta todavía

## Contexto del problema

La auditoría `C + D` de `trades` no era viable en el diseño original del notebook porque cargaba demasiado en memoria dentro de Jupyter.

Problema original:

- carga full de `trades_current.parquet`
- expansión masiva de `metrics_json`
- materialización de `issues_list` y `warns_list`
- repetición de lecturas full por bloque

Dataset afectado:

- parquet: `trades_current_cd_merged/trades_current.parquet`
- tamaño aproximado: `~5.24 GB`
- filas: `9,632,124`
- row groups: `10`

Conclusión operativa:

- el notebook no debía seguir procesando el full parquet
- había que separar `build` y `view`

## Decisión arquitectónica tomada

Se ha adoptado el patrón:

1. `build`
   Script offline que recorre el parquet en batches pequeños y genera caches.

2. `view`
   Notebook que lee caches pequeños y visualiza resultados.

3. `drilldown`
   Carga puntual de casos concretos para widgets y forense visual.

Regla actual:

- Jupyter no debe procesar el full parquet de `trades C + D`
- Jupyter debe consumir caches precomputados
- solo se deben abrir datos crudos al inspeccionar un caso concreto

## Archivos clave implantados

### Loader común

- [00_load_trades_run_artifacts.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/00_load_trades_run_artifacts.py)

Estado:

- implementado `TradesAuditHandle`
- soporta `stream(...)`
- soporta `load_projection(...)`
- añade helpers para extracción controlada de métricas

### Builder offline

- [build_trades_cd_audit_artifacts.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/build_trades_cd_audit_artifacts.py)

Estado:

- implementado
- recorre el parquet full en batches
- genera caches pequeños para el notebook
- emite progreso por etapa en stdout
- escribe `manifest.json`

### Lanzador

- [run_build_trades_cd_audit_artifacts.ps1](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/run_build_trades_cd_audit_artifacts.ps1)

Estado:

- implementado
- deja trazas en terminal y en log
- registra hora de inicio/fin
- muestra progreso por etapa

### Loader puntual de casos

- [trade_case_loader.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/trade_case_loader.py)

Estado:

- implementado
- filtra `case_index`
- puede cargar un caso desde `file`
- si el `file` apunta al `market.parquet` real, lo abre directamente sin reescanear `trades_current.parquet`

### Notebook visor

- [04_trades_full_C_D_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/04_trades_full_C_D_audit.ipynb)

Estado:

- ya migrado a modo visor de caches
- ya no recalcula bloques pesados del full parquet
- ya fue ejecutado y guardado con outputs
- `kernelspec` corregido a `backtest`

## Caches disponibles

Ubicación:

- `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\notebook_cd_cache`

Artefactos confirmados:

- `manifest.json`
- `severity_counts_cd.parquet`
- `snapshot_cd.parquet`
- `batch_mix_cd.parquet`
- `batch_rate_roll50_cd.parquet`
- `hard_issue_counts_cd.parquet`
- `warn_counts_cd.parquet`
- `issue_evidence_cd.parquet`
- `time_concentration_month_cd.parquet`
- `time_concentration_month_rate_cd.parquet`
- `time_concentration_year_cd.parquet`
- `time_concentration_year_rate_cd.parquet`
- `ticker_focus_cd.parquet`
- `diag_sample_cd.parquet`
- `diag_scale_cd.parquet`
- `diag_dup_cd.parquet`
- `diag_dup_outlier_view_cd.parquet`
- `issue_examples_cd.parquet`
- `warn_examples_cd.parquet`
- `exec_summary_cd.parquet`
- `exec_readout_cd.md`
- `daily_break_cd.parquet`
- `break_summary_cd.parquet`
- `top_breaks_cd.parquet`
- `band_df_cd.parquet`
- `abs_bucket_counts_cd.parquet`
- `pct_bucket_counts_cd.parquet`
- `cross_abs_cd.parquet`
- `cross_pct_cd.parquet`
- `cross_abs_pct_cd.parquet`
- `cross_pct_pct_cd.parquet`
- `tax_df_cd.parquet`
- `taxonomy_summary_cd.parquet`
- `taxonomy_side_cd.parquet`
- `taxonomy_side_view_cd.parquet`
- `final_df_cd.parquet`
- `final_summary_cd.parquet`
- `case_index_cd.parquet`

## Comando real de build

Lanzadera recomendada:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\run_build_trades_cd_audit_artifacts.ps1 -BatchSize 10000
```

Qué deja:

- progreso por etapa
- filas procesadas
- filas restantes
- porcentaje
- ETA aproximada
- log persistente en el cache dir

## Build full ejecutada

Se ha ejecutado la build full completa.

Resultado:

- estado: `ok`
- `exit_code=0`
- tiempo total aproximado: `2599.785s` (`43.3 min`)
- etapa `break_cache`: `690.58s`
- filas procesadas: `9,632,124`

Logs existentes:

- `build_trades_cd_audit_artifacts_20260412_125933.log`
- `build_trades_cd_audit_artifacts_20260412_130055.log`

## Estado del notebook

Notebook operativo:

- [04_trades_full_C_D_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/04_trades_full_C_D_audit.ipynb)

Estado:

- ejecutado correctamente con kernel `backtest`
- outputs guardados dentro del `.ipynb`
- tiempo de ejecución aproximado: `57s`

Problemas corregidos durante esta fase:

- el notebook apuntaba a `python3` en vez de `backtest`
- el widget final fallaba porque `tax_df_cd.parquet` no traía `issues_list`
- se corrigió el cache base y se endureció el widget para tolerar columnas ausentes

## Lectura técnica de resultados

Resultado principal de la auditoría:

- el problema parece real, masivo y estructural
- no parece simple ruido de validación

Señales principales observadas:

- `PASS`: `553,887` (`5.750%`)
- `SOFT_FAIL`: `5,392,744` (`55.987%`)
- `HARD_FAIL`: `3,685,493` (`38.263%`)

Issue dominante:

- `trade_price_outside_daily_range`: `2,983,713`

Warns dominantes:

- `trade_price_outside_1m_range`: `5,094,621`
- `duplicate_exact_trade_rows_present`: `4,224,703`
- `off_session_trades_present`: `3,191,518`

Taxonomía:

- `confirmed_by_1m_and_not_scale`: `1,875,771`
- `confirmed_by_1m_and_dup_heavy`: `1,052,522`
- `not_confirmed_by_1m`: `55,420`

Lectura operativa:

- el core del problema está confirmado por `1m`
- `scale mismatch` no explica el grueso del residuo
- los duplicados son una contaminación muy importante, pero no la explicación única
- `below_only` domina claramente

Conclusión:

- existe una subpoblación dominante de breaks reales contra referencia
- además hay una subpoblación muy sucia por duplicados y actividad fuera de sesión

## Qué se ha logrado exactamente

### Resuelto

- se eliminó la dependencia del notebook respecto a cargas full del parquet
- ya existe builder offline reutilizable
- ya existe caché por bloques
- el notebook C+D ya consume esos caches
- el widget final vuelve a funcionar
- el full run se puede reconstruir sin reventar Jupyter

### No resuelto todavía

- no existe todavía una lanzadera incremental por bloque
  - ahora mismo el builder recompone todo el pipeline
- no se ha hecho la réplica equivalente en `quotes`
- no se han limpiado aún los warnings menores de notebook:
  - `MissingIDFieldWarning`
  - warning de `zmq`/event loop en Windows
- no se ha refinado todavía la experiencia del widget para navegar directamente por `case_index_cd.parquet`
  - el widget actual funciona sobre `tax_df`
  - no está todavía reescrito para apoyarse directamente en `case_index`

## Qué debería hacer el siguiente agente

### Prioridad 1

Reutilizar esta arquitectura para `quotes`.

Objetivo:

- mismo patrón `build/view/drilldown`
- evitar que `quotes` vuelva a cargar el full parquet en Jupyter

### Prioridad 2

Mejorar el widget de `trades` para apoyarlo más explícitamente en `case_index_cd.parquet`.

Objetivo:

- selección por `block`
- selección por `group_key`
- ranking por `rank_score`
- carga puntual por caso

### Prioridad 3

Si compensa, añadir modo incremental al builder:

- regenerar solo `break/taxonomy/final_bucket`
- sin tener que recalcular snapshot/root-cause/diag si no han cambiado

### Prioridad 4

Limpiar warnings menores del notebook:

- normalizar ids de celdas
- revisar warnings de `zmq`/Windows solo si molestan en la operativa

## Riesgos o matices a recordar

- el notebook correcto para `C + D` es `04_trades_full_C_D_audit.ipynb`
- si alguien abre el notebook y no ve outputs, revisar primero:
  - que use kernel `backtest`
  - que existan los caches en `notebook_cd_cache`
- si el widget vuelve a fallar, revisar antes el schema de `tax_df_cd.parquet`
- el builder ya deja trazabilidad suficiente para diagnóstico en log

## Resumen corto para el siguiente agente

Estado actual:

- `trades C + D` ya está migrado a arquitectura low-memory
- la build full ya se ejecutó correctamente
- el notebook visor ya funciona con caches y widget
- la lectura analítica principal es que el problema parece real, masivo y confirmado por `1m`

Lo siguiente más lógico:

1. portar este patrón a `quotes`
2. refinar el widget para usar `case_index_cd`
3. añadir regeneración parcial por bloques si hace falta
