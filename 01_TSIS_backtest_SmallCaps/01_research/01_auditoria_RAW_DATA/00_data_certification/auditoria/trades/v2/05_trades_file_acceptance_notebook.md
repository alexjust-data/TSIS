# `05_trades_file_acceptance_audit.ipynb` | Estado y lectura actual

Este documento deja constancia de la lectura técnica actual del notebook:

- [05_trades_file_acceptance_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/05_trades_file_acceptance_audit.ipynb)

No es un diseño teórico. Es un handoff operativo para que el siguiente agente entienda:

- qué está haciendo el notebook realmente
- por qué trabaja sobre `380` casos y no sobre el full raw `<1B>`
- qué se ha refactorizado ya
- qué lectura técnica se sostiene ahora mismo
- qué debe considerarse explicación plausible del residuo

## Qué significa la muestra estratificada

La auditoría file-level de `05` no relee los `9,429,112` files raw `<1B>` completos en cada iteración. El builder hace dos cosas distintas:

1. `layer1`
   Recorre todo el universo `<1B>` dentro de `trades_current.parquet`.

2. `sample_recompute`
   Baja a raw solo sobre una muestra estratificada de files.

La muestra estratificada significa:

- no se eligen `380` casos al azar puro
- se reservan cupos por tipo de caso (`sample_stratum`)
- cada estrato toma `20` files por `reservoir sampling`
- el objetivo es no perder casos raros o severos en la auditoría profunda

En el builder actual:

- `sample_per_stratum = 20`
- estratos observados en la última build `<1B>`: `19`
- muestra final: `380` files

Conclusión:

- `380` no es “el universo”
- tampoco es una muestra ingenua
- es una muestra diseñada para exploración profunda, calibración y refactorización metodológica

## Builder y artefactos vigentes

Builder `<1B>`:

- [57b_build_trades_file_acceptance_artifacts_lt1b.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/57b_build_trades_file_acceptance_artifacts_lt1b.py)

Viewer:

- [58b_trades_file_acceptance_view_lt1b.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/58b_trades_file_acceptance_view_lt1b.py)
- [58_trades_file_acceptance_view.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/58_trades_file_acceptance_view.py)

Cache canónico actual:

- [file_acceptance_cache_lt1b](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_materialized/trades_current_cd_merged/root_cause_exports/file_acceptance_cache_lt1b)

Artefactos relevantes añadidos en esta fase:

- `condition_code_summary.parquet`
- `condition_combo_summary.parquet`
- `layer2_session_profile.parquet`
- `layer2_session_mismatch.parquet`

## Correcciones ya aplicadas

### Integridad

Se corrigió la lógica de capa 1:

- inválido solo si `price < 0`
- inválido solo si `size < 0`
- `price = 0` y `size = 0` no se consideran fallo físico por sí mismos

### Visualización de `conditions`

Se corrigió la normalización de `conditions` para que:

- `condition_code_summary` cuente códigos individuales correctamente
- `condition_combo_summary` muestre combinaciones legibles como `[]`, `[14]`, `[14, 41]`

## Hallazgo principal de la capa 2

La refactorización de la segunda capa deja un resultado importante:

- la señal heredada de `off_session_trade_pct` no se confirma en el recompute raw

Última lectura:

- `sample_index` heredado marca `117/380` files con `off_session_trade_pct > 0`
- `raw_file_metrics` nuevo marca `0/380`

La discrepancia queda materializada en:

- [layer2_session_mismatch.parquet](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_materialized/trades_current_cd_merged/root_cause_exports/file_acceptance_cache_lt1b/layer2_session_mismatch.parquet)

Esto cambia la interpretación:

- el problema no debe atribuirse de entrada a `trades off-session`
- antes de juzgar la data, había que revisar los métricos heredados

Lectura técnica actual:

- la señal heredada de off-session es poco fiable
- la lectura raw nueva es más coherente con los timestamps reales observados

## Hallazgo principal sobre odd-lots

Una vez separadas sesión y tamaño, el outside se concentra mucho más en trades pequeños que en el flujo round-lot.

Medianas actuales de la muestra:

- `median_odd_lot_trade_pct = 53.94%`
- `median_round_lot_trade_pct = 46.06%`
- `median_outside_daily_odd_lot_pct = 5.34%`
- `median_outside_daily_round_lot_pct = 0.00%`
- `median_outside_1m_odd_lot_pct = 33.33%`
- `median_outside_1m_round_lot_pct = 0.00%`

Lectura:

- gran parte del conflicto con referencias no está en el corazón round-lot del tape
- eso encaja mejor con microestructura y comparabilidad que con mala calidad global de trades

## Hallazgo principal sobre `conditions`

Ya no solo sabemos qué `conditions` existen; ahora también sabemos cuánto outside concentran.

Códigos dominantes en la muestra:

- `14`
- `37`
- `41`

Combos dominantes:

- `[]`
- `[37]`
- `[14]`
- `[14, 41]`
- `[14, 37, 41]`

Ejemplos de lectura:

- `[14]` tiene `outside_1m_pct_within_combo` bastante menor que `[37]`
- `[37]` y `[14, 41]` concentran una fracción alta del outside `1m`

Conclusión:

- no todas las `sale conditions` se comportan igual
- la política final no debería tratar todas las combinaciones como equivalentes

## Resultado del filtro conservador `regular + round_lot`

Se construyó una lectura más conservadora del tape:

- sesión `regular`
- `size >= 100`

Resultado sobre la muestra:

- mediana `core_outside_daily_pct = 0.00%`
- mediana `core_outside_1m_pct = 0.00%`

Esto es clave:

- el caso mediano deja de romper cuando se usa el núcleo más conservador del tape
- eso debilita la tesis de “data mala generalizada”

## Residuo extremo del core

Quedó un subconjunto de `42` files con `core_outside_1m_pct >= 25`.

El trabajo posterior mostró que la mayoría de ese residuo no parece error aleatorio del tape, sino desalineación de escala contra `daily/1m`.

### Bucketización de factores de escala

Sobre esos `42` casos extremos:

- `36/42` caen en buckets de escala plausibles
- porcentaje explicable por bucket limpio: `85.7%`

Buckets observados:

- `~0.9091x`
- `~4x`
- `~5x`
- `~6x`
- `~10x`
- `~15x`
- `~20x`
- `~100x`
- `~150x`
- `~300x`
- `~1000x`
- `~5000x`

Eso apunta a:

- split / reverse split
- corporate action
- referencia en escala distinta al tape raw

### Casos muy claros

Ejemplos:

- `TISI`, `ANGI`, `NEON`, `WMC` -> `~10x`
- `ASPS`, `KFS`, `HEAR`, `ALTI` -> `~4x`
- `DYNT`, `IDI` -> `~5x`
- `CLRO`, `ENSV`, `GMM` -> `~15x`
- `COMS`, `REED` -> `~300x`
- `FALC` -> `~100x`

### Casos inicialmente “no limpios”

También los casos que inicialmente quedaron en `>1x_other` resultaron ser escalas extremas al inspeccionarlos minuto a minuto:

- `WHLR` -> `~30,236,281x`
- `XELA` -> `~12,000x`
- `RVSN` -> `~240x`
- `CDR` -> `~6.6x`
- `KPRX` -> `~9x`
- `XXII` -> `~11,177,034x`

La referencia `1m` y `daily` aparece directamente en otra escala frente al trade raw.

Conclusión:

- tampoco esos casos apuntan a trade tape corrupto
- apuntan a `reference_scale_mismatch`

## Conclusión actual

La lectura defendible a día de hoy no es:

- “Polygon trades está mal”

La lectura defendible es:

1. una parte del diagnóstico heredado estaba contaminada por métricos poco fiables
2. una parte relevante del outside se concentra en odd-lots
3. el residuo extremo conservador está dominado por `reference_scale_mismatch`

En otras palabras:

- el problema dominante observado en `05` no parece ser mala calidad intrínseca de `trades`
- parece ser comparabilidad imperfecta contra `daily` y `1m`

## Implicación para la política final

La política `good / review / bad` no debe seguir tratando como `bad_data` casos que en realidad son:

- `reference_scale_mismatch`
- odd-lot dominant conflict
- discrepancia heredada de sesión no confirmada en raw
- conflicto de alineación contra referencia `1m`

La política final debería separar al menos:

- `good`
- `review_microstructure`
- `reference_scale_mismatch`
- `review_no_1m_reference`
- `review_1m_reference_alignment`
- `review`

## Estado de la política actual

La política muestral ya fue refactorizada para introducir etiquetas explícitas de comparabilidad:

- `reference_scale_mismatch`
- `review_microstructure`
- `review_no_1m_reference`
- `review_1m_reference_alignment`

Reparto actual de la muestra `380`:

- `review = 140`
- `reference_scale_mismatch = 106`
- `review_microstructure = 111`
- `review_no_1m_reference = 21`
- `review_1m_reference_alignment = 2`

Lectura:

- `106` casos ya quedan separados como `reference_scale_mismatch`
- `111` casos quedan separados como `review_microstructure`, dominados por odd-lots y comparabilidad difícil
- `21` casos quedan separados como `review_no_1m_reference`, donde el conflicto frente a `daily` existe pero falta confirmación `1m`
- `2` casos quedan separados como `review_1m_reference_alignment`, donde `daily` y `VWAP` están alineados pero la comparación con `1m` rompe de forma amplia en el núcleo
- ya no queda bloque `bad_data` en la muestra estratificada actual
- el resultado favorece la hipótesis de que el problema dominante es de comparabilidad con referencias y microestructura, no de mala calidad intrínseca del tape

## Siguiente paso recomendado

El siguiente paso ya no es seguir buscando “errores” en `trades`.

Es:

1. consolidar esta política como cierre metodológico de la muestra
2. decidir si `review_1m_reference_alignment` debe mantenerse como bucket propio o absorberse en `review`
3. documentar que el residuo duro muestral ha quedado drenado a buckets explicables
4. solo después decidir si merece la pena promover la lógica a full `<1B>` raw file-level

## Paso operativo para full `<1B>`

Si se decide promover la logica a full `<1B>` sin depender del notebook, el cierre operativo real ya no debe anclarse en `57e`, sino en el runner posterior `57f`, que conserva el mismo universo e indice de `57e` pero deja cerrado el recompute full:

- runner parcial anterior:
  - [57e_build_trades_file_acceptance_artifacts_lt1b_full_clean.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/57e_build_trades_file_acceptance_artifacts_lt1b_full_clean.py)
- runner final correcto:
  - [57f_build_trades_file_acceptance_artifacts_lt1b_full_clean_fast_same_schema.py](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/57f_build_trades_file_acceptance_artifacts_lt1b_full_clean_fast_same_schema.py)

Launcher PowerShell historico:

- [57e_run_build_trades_file_acceptance_artifacts_lt1b_full_clean.ps1](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/57e_run_build_trades_file_acceptance_artifacts_lt1b_full_clean.ps1)

Comando historico de prueba sobre `57e`:

```powershell
python "C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/57e_build_trades_file_acceptance_artifacts_lt1b_full_clean.py" --workers 4 --limit-shards 8
```

Comando full posteriormente cerrado con `57f`:

```powershell
python "C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/cell_code/57f_build_trades_file_acceptance_artifacts_lt1b_full_clean_fast_same_schema.py" --workers 4
```

Que hace este runner final:

1. fase indice
   Recorre `trades_current.parquet`, filtra por el universo `<1B>` y escribe `full_index_shards/`.

2. fase recompute
   Relee cada file raw `<1B>` desde esos `index shards`, calcula metricas file-level con la politica refactorizada y escribe `raw_metrics_shards/`.

3. fase finalize
   Agrega los shards y escribe los resumenes full.

Estado real confirmado:

- `57e/full_clean`
  - dejo `95` `full_index_shards`
  - total indice: `9,429,112`
  - dejo `56` `raw_metrics_shards`
  - total recompute materializado: `5,600,000`
- `57f/full_clean_fast_same_schema`
  - reutiliza el mismo universo e indice de `57e`
  - los `full_index_shards` son equivalentes shard a shard
  - deja `95` `raw_metrics_shards`
  - total recompute materializado: `9,429,112`

Regla operativa importante:

- `57e` ya no debe interpretarse como cierre pendiente de esta corrida
- `57f` es el cache final que supersede a `57e`
- no hace falta mezclar ambos caches para leer el total
- `57f` ya contiene el universo completo y absorbe los shards compatibles de `57e`

Progreso esperado en terminal:

- bloques JSON con `stage = "full_clean_index"`
- bloques JSON con `stage = "full_clean_recompute"`

Artefactos de salida que deben usarse como referencia final:

- [file_acceptance_cache_lt1b_full_clean_fast_same_schema](C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/trades_v2_materialized/trades_current_cd_merged/root_cause_exports/file_acceptance_cache_lt1b_full_clean_fast_same_schema)

Dentro de ese directorio:

- `full_index_shards/`
- `raw_metrics_shards/`
- `layer1_integrity_summary.parquet`
- `layer1_integrity_examples.parquet`
- `sample_index.parquet`
- `layer6_policy_summary_full.parquet`
- `layer2_coverage_summary_full.parquet`
- `progress.json`
- `manifest.json`

Objetivo de este paso:

- materializar artefactos full `<1B>` en terminal
- evitar rehacer computo pesado en notebook
- poder inspeccionar avance y estado del run directamente desde consola
- dejar un cierre full realmente completo en disco

## Notebook de cierre full

La separacion final queda asi:

- [05_trades_file_acceptance_audit.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/05_trades_file_acceptance_audit.ipynb)
  Notebook metodologico de muestra (`380` files estratificados).

- [06_trades_file_acceptance_full_lt1b_closeout.ipynb](C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/00_data_certification/auditoria/trades/v2/06_trades_file_acceptance_full_lt1b_closeout.ipynb)
  Notebook de cierre full `<1B>` para ejecutar sobre el cache final ya cerrado por `57f`, dejando `57e` como run parcial previo sobre el mismo indice.

Regla practica:

- `05` se usa para explicar y defender la metodologia.
- `06` se usa para leer el resultado final del universo full `<1B>`.

## Patron recomendado para futuras auditorias full

La ejecucion historica con `57e` no llego a cerrar el recompute full. El cierre real quedo resuelto con `57f`, que mantiene el mismo esquema y el mismo indice pero completa los shards faltantes.  
Pero para futuras auditorias full, si se quiere escalar mas sin mezclar estados ni correr varios runners sobre el mismo cache, el patron recomendado sigue siendo **particionar por rangos de shards y fusionar al final**.

Arquitectura recomendada:

1. construir una sola vez `full_index_shards/`
2. dividir esos shards en rangos disjuntos
3. lanzar un run independiente por rango
4. escribir los resultados de cada rango en su propio `cache_dir`
5. hacer un merge/reduce final de todos los `raw_metrics_shards`
6. materializar un unico `layer6_policy_summary_full.parquet`, `layer2_coverage_summary_full.parquet` y `manifest.json`

Ejemplo conceptual:

- run A: shards `1-24`
- run B: shards `25-48`
- run C: shards `49-72`
- run D: shards `73-95`

Ventajas de este patron:

- evita que varios procesos compitan por el mismo `cache_dir`
- evita colisiones entre `progress.json`, `manifest.json` y `raw_metrics_shards`
- permite distribuir trabajo entre varias sesiones o maquinas
- hace el resume mas claro
- deja un merge final explicito y auditable

Lo que no se recomienda:

- lanzar varios runners identicos contra el mismo cache esperando que "se repartan solos"

Porque eso:

- puede duplicar trabajo
- puede degradar el disco por I/O
- puede generar estado ambiguo en los shards y en el progreso

Conclusion operativa:

- para esta corrida actual la referencia final ya no es `57e`, sino `57f/full_clean_fast_same_schema`
- `57e` debe conservarse como evidencia de run parcial anterior sobre el mismo universo
- para futuras auditorias full conviene pasar a un esquema `split by shard range + merge final`
