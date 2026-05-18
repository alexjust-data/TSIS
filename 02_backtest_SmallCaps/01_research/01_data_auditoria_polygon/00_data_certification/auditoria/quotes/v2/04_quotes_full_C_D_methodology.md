# 04_quotes_full_C_D_methodology

## Objetivo

Este documento acompaña al notebook `04_quotes_full_C_D_methodology.ipynb`.

Su función es dejar trazabilidad paso a paso de la auditoría metodológica de `quotes`, separada del cierre ejecutivo. La idea es replicar la disciplina que seguimos en `trades`: cada vuelta de análisis, cada ajuste de criterio y cada hallazgo relevante quedan anotados aquí.

## Base de datos de referencia

- Dataset base actual:
  `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\quotes_current.parquet`
- Universo canónico `<1B>`:
  `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet`
- Verificación de merge:
  `C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_v2_materialized\quotes_current_cd_merged\merge_verification_summary.json`

Estado conocido al arrancar `v2`:

- `merged_current_rows = 9,930,334`
- `verification_passed = true`
- existe también una cola `retry_current.parquet`

## Enfoque de v2

En `quotes/v2` trabajaremos con dos piezas separadas:

- `methodology`: notebook para construir, cuestionar y refinar la lógica de auditoría
- `closeout`: notebook para presentar los resultados ya estabilizados

Esto evita mezclar:

- exploración de métricas
- cambios de criterio
- lectura final defendible

## Pasos de auditoría

### Paso 0. Inventario y contrato del dataset

Objetivo:

- confirmar qué parquet es la base real
- confirmar si el universo auditado actual ya es full C+D
- identificar artefactos existentes reutilizables

Resultado inicial:

- la base real actual es `quotes_current_cd_merged\quotes_current.parquet`
- el merge C+D ya está materializado y verificado
- el universo operativo correcto no es el full total, sino el cutoff `<1B>` canónico
- por tanto, `v2` debe leer el merged `C+D` y filtrarlo por `market_cap_cutoff_lt_1b_active_inactive.parquet`
- no hace falta rehacer el full histórico solo para empezar la auditoría `v2`

### Paso 1. Definir la unidad de auditoría

Pendiente de documentar.

Preguntas a resolver:

- auditamos a nivel row
- auditamos a nivel file
- auditamos a nivel ticker-date
- o usamos una jerarquía combinada

### Paso 2. Capas de validación

Pendiente de documentar.

Capas previstas:

- integridad física y schema
- consistencia temporal
- calidad microestructural del NBBO / bid-ask
- comparación contra referencias derivadas
- severidad real
- política final de aceptación

### Paso 3. Artefactos y cachés

Pendiente de documentar.

Aquí iremos anotando:

- qué builder genera cada artefacto
- qué artefactos son smoke
- qué artefactos son full
- qué partes admiten `resume`

### Paso 4. Visualizaciones del notebook

Pendiente de documentar.

Visualizaciones candidatas:

- cobertura por año y mes
- tasas de hard/soft fail
- mezcla de root causes
- breakdown temporal
- concentración por ticker
- ejemplos forenses

### Paso 5. Cambios de criterio

Pendiente de documentar.

Regla de este documento:

- cada cambio de criterio debe dejar:
  - motivo
  - impacto
  - qué lectura anterior deja de ser válida

## Comandos

Se irán anotando aquí conforme consolidemos el flujo `v2`.

## Estado actual

- `v1` conserva la auditoría previa de quotes
- `v2` arranca como capa nueva y limpia
- falta materializar los notebooks nuevos y conectar los builders/artefactos que vayamos a usar

## Builder v2

Builder principal para regenerar los artefactos del notebook `v2` sin tocar la materializaci?n base:

```sh
python "C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py"
```

Este builder:

- lee `quotes_current_cd_merged\quotes_current.parquet`
- cruza por `ticker` contra `market_cap_cutoff_lt_1b_active_inactive.parquet`
- reutiliza la l?gica de auditor?a ya consolidada
- escribe cache separado en:
  `C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache_v2`
- no relanza inventory, validation ni materialization

### Resume y recomputaci?n parcial

El builder `v2` mantiene progreso por etapa en:

- `C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache_v2\build_progress_cd_lt1b.json`

Esto permite:

- relanzar tras corte de luz sin perder etapas ya completadas
- recomputar solo desde una etapa concreta hacia abajo

Comando de recomputaci?n parcial:

```sh
python "C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py" --from-stage taxonomy
```

Uso previsto:

- `--from-stage taxonomy`
  reeval?a taxonom?a, `case_index` y `manifest` sin rehacer snapshot, root cause, concentration, microstructure, focus examples ni forensic

### Vuelta de refinamiento de taxonom?a

En la vuelta actual se materializaron cuatro refinamientos concretos para evitar mezclar familias distintas:

- dividir `persistent_soft_crossed` en:
  - `persistent_soft_crossed_low`
  - `persistent_soft_crossed_mid`
- dividir `threshold_edge_hard` por tama?o de file en:
  - `small_file_threshold_edge_hard`
  - `medium_file_threshold_edge_hard`
  - `large_file_threshold_edge_hard`
- dividir `extreme_hard_crossed_gt20` en:
  - `extreme_hard_crossed_gt20_integerized`
  - `extreme_hard_crossed_gt20_non_integerized`
- separar el bloque de rollover UTC en:
  - `utc_rollover_large_day_clean`
  - `utc_rollover_large_day_with_soft_crossed`

Lectura resultante tras recomputar desde `taxonomy`:

- `clean_pass_or_other`: `45.79%`
- `soft_crossed_micro_noise`: `20.20%`
- `persistent_soft_crossed_low`: `9.32%`
- `persistent_soft_crossed_mid`: `6.36%`
- `utc_rollover_large_day_clean`: `5.69%`
- `small_file_threshold_edge_hard`: `3.38%`
- `medium_file_threshold_edge_hard`: `3.21%`
- `high_hard_crossed_5_to_20`: `2.84%`
- `utc_rollover_large_day_with_soft_crossed`: `1.25%`
- `large_file_threshold_edge_hard`: `1.04%`
- `extreme_hard_crossed_gt20_non_integerized`: `0.76%`
- `extreme_hard_crossed_gt20_integerized`: `0.08%`
- `extreme_integerized_100pct_crossed`: `0.05%`

Conclusi?n metodol?gica de esta vuelta:

- los extremos ya quedan aislados
- los bordes de umbral dejan de aparecer como un ?nico bloque artificial
- el rollover UTC limpio queda separado de los casos con crossed real
- la siguiente refinaci?n solo deber?a tocar bolsas todav?a heterog?neas; seguir subdividiendo todo de forma ciega ya tender?a a sobreajuste

### Segunda vuelta de refinamiento focal

Se aplic? una segunda vuelta solo sobre cuatro bolsas que segu?an siendo demasiado amplias:

- dividir `high_hard_crossed_5_to_20` en:
  - `high_hard_crossed_5_to_20`
  - `high_hard_crossed_10_to_20`
- dividir `medium_file_threshold_edge_hard` por masa absoluta de crossed:
  - `medium_file_threshold_edge_hard_few_crosses`
  - `medium_file_threshold_edge_hard_many_crosses`
- dividir `large_file_threshold_edge_hard` por masa absoluta de crossed:
  - `large_file_threshold_edge_hard_few_crosses`
  - `large_file_threshold_edge_hard_many_crosses`
- dividir `extreme_hard_crossed_gt20_non_integerized` en:
  - `extreme_hard_crossed_gt20_non_integerized`
  - `extreme_hard_crossed_gt20_non_integerized_with_utc_rollover`
- dividir `persistent_soft_crossed_mid` por escala real del file:
  - `persistent_soft_crossed_mid_thin_scale`
  - `persistent_soft_crossed_mid_large_scale`

Cortes usados:

- `high_hard_crossed_10_to_20`: `crossed_ratio_pct >= 10`
- `medium_file_threshold_edge_hard_few_crosses`: `rows in (100,1000]` y `crossed_rows <= 5`
- `large_file_threshold_edge_hard_few_crosses`: `rows > 1000` y `crossed_rows < 50`
- `persistent_soft_crossed_mid_large_scale`: `rows >= 10_000`
- `extreme_hard_crossed_gt20_non_integerized_with_utc_rollover`: mismo bloque extremo con `timestamp_out_of_partition_day = true`

Lectura resultante tras recomputar de nuevo desde `taxonomy`:

- `persistent_soft_crossed_mid_thin_scale`: `5.86%`
- `persistent_soft_crossed_mid_large_scale`: `0.49%`
- `high_hard_crossed_5_to_20`: `1.77%`
- `high_hard_crossed_10_to_20`: `1.07%`
- `extreme_hard_crossed_gt20_non_integerized`: `0.75%`
- `extreme_hard_crossed_gt20_non_integerized_with_utc_rollover`: `0.013%`

Conclusi?n de esta segunda vuelta:

- `persistent_soft_crossed_mid` ya no mezcla d?as finos con d?as realmente grandes
- el bloque `10-20%` ya queda separado del borde duro de `5-10%`
- el rollover UTC dentro de extremos >`20%` existe, pero es residual
- la bolsa de `large_file_threshold_edge_hard_many_crosses` sigue siendo candidata natural para revisi?n visual en notebook porque concentra mucha masa absoluta aun con pct moderado

### Correcci?n importante del builder

Durante esta vuelta apareci? un bug real en la taxonom?a:

- `build_taxonomy_summary_cached()` no estaba propagando `m.crossed_rows` dentro de `work`

Impacto:

- la separaci?n `few_crosses` vs `many_crosses` pod?a quedar bien escrita en el clasificador pero mal materializada en el resumen final

Acci?n tomada:

- se corrigi? el wiring en `00_load_quotes_run_artifacts.py`
- se recompil? el loader
- se relanz? otra vez:

```sh
python "C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py" --from-stage taxonomy
```

La lectura buena de esta fase es la ?ltima recomputaci?n, no la intermedia.

### Notebook metodol?gico actualizado

Se actualiz? `04_quotes_full_C_D_methodology.ipynb` para que ya no sea solo scaffold y lea directamente los artefactos `v2` sin recalcular nada pesado.

Capas nuevas del notebook:

- estado de la run y manifiesto
- snapshot estructural
- taxonom?a final refinada
- visualizaci?n aislada de familias refinadas
- lectura de `case_index`
- root causes y warnings
- vista temporal de rollover UTC
- bloque final de prioridades para revisi?n manual

Familias que el notebook destaca expl?citamente:

- `persistent_soft_crossed_mid_thin_scale`
- `persistent_soft_crossed_mid_large_scale`
- `high_hard_crossed_5_to_20`
- `high_hard_crossed_10_to_20`
- `medium_file_threshold_edge_hard_few_crosses`
- `medium_file_threshold_edge_hard_many_crosses`
- `large_file_threshold_edge_hard_few_crosses`
- `large_file_threshold_edge_hard_many_crosses`
- `extreme_hard_crossed_gt20_non_integerized`
- `extreme_hard_crossed_gt20_non_integerized_with_utc_rollover`

Lectura operativa que debe salir del notebook:

- qu? parte del residuo sigue siendo `soft crossed` pero a gran escala
- qu? parte del borde duro viene de poca masa absoluta frente a mucha masa absoluta
- qu? parte del extremo >`20%` coincide adem?s con rollover UTC
- cu?les son los cuatro buckets que merecen revisi?n visual final

### Ajuste de notebook

Al ejecutar la capa de snapshot apareci? un ajuste de presentaci?n:

- `root_mix_cd_lt1b.parquet` no viene en formato largo
- sus columnas reales son:
  - `root`
  - `PASS`
  - `SOFT_FAIL`
  - `HARD_FAIL`
  - `total`
  - porcentajes asociados

Acci?n tomada:

- se corrigi? `04_quotes_full_C_D_methodology.ipynb`
- ahora la celda transforma `root_mix` con `melt()` antes de pintar el barplot `root x severity`

Esto no cambia la auditor?a ni los artefactos.
Solo corrige la visualizaci?n del notebook.

### Conclusi?n provisional de methodology

Lectura metodol?gica a este punto:

- `quotes <1B>` no muestra se?ales de corrupci?n masiva del dataset
- el grueso del universo cae en `clean_pass_or_other` o en `soft_crossed_micro_noise`
- el residuo importante ya no aparece como una bolsa ca?tica, sino repartido en familias ya defendibles
- `utc_rollover_large_day_clean` debe leerse como fen?meno temporal propio y no mezclarse con fallo econ?mico duro
- muchos `hard fails` frecuentes quedan pegados al borde de regla y numerosos casos top caen exactamente en `5.0%`
- los `warns` dominantes caen en `persistent_soft_crossed_mid_thin_scale` y muchos ejemplos top caen exactamente en `0.8%`
- los extremos realmente severos existen, pero ya quedan aislados como fracci?n peque?a del universo

Interpretaci?n operativa provisional:

- aceptar como residuo esperable la parte de micro-ruido soft y el rollover UTC limpio
- mantener bajo revisi?n manual los buckets:
  - `persistent_soft_crossed_mid_large_scale`
  - `large_file_threshold_edge_hard_many_crosses`
  - `medium_file_threshold_edge_hard_many_crosses`
  - `high_hard_crossed_10_to_20`
- no seguir refinando taxonom?a por inercia; desde aqu? el valor est? en la lectura econ?mica de esos buckets, no en seguir partiendo etiquetas

Estado resultante:

- `methodology` queda en estado de pre-cierre
- siguiente paso l?gico: consolidar `04_quotes_full_C_D_closeout.ipynb` con esta narrativa ya estabilizada

### Capa nueva: severidad economica del crossed

Para no quedarnos solo en `% crossed`, se anadio una capa nueva de severidad sobre raw quote files:

- `cross_abs = bid_price - ask_price`
- `cross_rel_bps = (bid_price - ask_price) / mid_price * 10000`
- donde `mid_price = (bid_price + ask_price) / 2`

Esto responde a la pregunta correcta:

- no solo cuantas filas tienen `bid > ask`
- sino si ese cruce es pequeno, moderado o economicamente extremo

Artefactos nuevos:

- `crossed_gap_severity_summary_cd_lt1b.parquet`
- `crossed_gap_severity_cases_cd_lt1b.parquet`

Bug encontrado y corregido:

- la primera version devolvia `crossed_rows_raw = 0` en todos los casos
- causa: `pq.read_table()` fallaba en raws particionados y la excepcion dejaba la capa vacia
- correccion: lectura con `pd.read_parquet(..., columns=[bid_price, ask_price])` y fallback a `pq.ParquetFile(...).read(...)`
- despues de la correccion se relanzo solo:

```sh
python "C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py" --from-stage crossed_gap_severity
```

Lectura metodologica importante:

- `cross_rel_bps = 20000` aparece cuando el `ask_price` esta en `0` o practicamente `0`
- eso no es un microcruce alrededor del spread
- eso es un `ask` degenerado que hace que el crossed sea economicamente extremo

Conclusion por familias con esta capa:

- `high_hard_crossed_10_to_20`:
  - mediana `cross_abs` ~ `9.145`
  - mediana `cross_rel_bps` = `20000`
  - lectura: familia claramente extrema, no ruido de borde
- `medium_file_threshold_edge_hard_many_crosses`:
  - mediana `cross_abs` ~ `9.3225`
  - mediana `cross_rel_bps` = `20000`
  - lectura: tambien familia extrema; el problema no es pequeno
- `large_file_threshold_edge_hard_many_crosses`:
  - mediana `cross_abs` ~ `0.03`
  - pero cola severa muy grande y `cross_rel_bps_p90 = 20000`
  - lectura: familia mixta; combina cruces pequenos con contaminacion dura tipo `ask=0`
- `persistent_soft_crossed_mid_large_scale`:
  - mediana `cross_abs` ~ `0.01`
  - mediana `cross_rel_bps` ~ `7.2`
  - composicion mediana:
    - `mild` ~ `10.5%`
    - `moderate` ~ `45.2%`
    - `severe` ~ `3.1%`
  - lectura: esta si parece una familia realmente intermedia y no puramente extrema

Implicacion metodologica:

- la taxonomia ya no debe leerse solo por porcentaje de filas crossed
- debe separarse entre:
  - familias dominadas por `ask=0` o cuasi `0`
  - familias con cruce pequeno pero persistente
  - familias mixtas que combinan ambas cosas

Siguiente refinamiento natural:

- anadir una descomposicion explicita por:
  - `ask_price == 0`
  - `ask_price > 0`
- y medir severidad relativa solo sobre el subconjunto con ambos lados positivos

Eso permitiria distinguir con mucha mas limpieza:

- crossed por `ask` degenerado
- crossed por inversion real de bid/ask en valores positivos

### Refinamiento ejecutado: `ask == 0` vs `ask > 0`

Ese refinamiento ya se implemento sobre la capa `crossed_gap_severity`.

Metricas nuevas por caso:

- `crossed_rows_ask_zero`
- `crossed_rows_ask_positive`
- `crossed_ask_zero_share_pct`
- `crossed_ask_positive_share_pct`
- `cross_rel_bps_median_ask_positive`
- distribucion `near_zero / mild / moderate / severe` solo sobre `ask > 0`

Lectura por familias clave:

- `high_hard_crossed_10_to_20`
  - mediana `ask_zero_share` = `100%`
  - lectura:
    - casi todo el bucket viene de `ask = 0`
    - cuando aparece `ask > 0`, sigue siendo severo (`~127 bps` de mediana)
- `medium_file_threshold_edge_hard_many_crosses`
  - mediana `ask_zero_share` = `100%`
  - lectura:
    - bucket dominado por `ask` degenerado
    - el subconjunto `ask > 0` tambien es severo (`~18.9 bps` de mediana)
- `large_file_threshold_edge_hard_many_crosses`
  - mediana `ask_zero_share` ~ `52.1%`
  - mediana `ask_positive_share` ~ `47.9%`
  - `cross_rel_bps_median_ask_positive` ~ `10.0 bps`
  - lectura:
    - este es el bucket mixto real
    - aqui si conviven dos fenomenos:
      - degeneracion por `ask = 0`
      - inversion positiva de bid/ask en escala moderada
- `persistent_soft_crossed_mid_large_scale`
  - mediana `ask_zero_share` = `0%`
  - mediana `ask_positive_share` = `100%`
  - `cross_rel_bps_median_ask_positive` ~ `6.25 bps`
  - lectura:
    - este bucket ya no puede explicarse por `ask = 0`
    - es un bucket de inversion positiva real, de severidad intermedia

Conclusion metodologica actualizada:

- una parte importante del residuo duro queda explicada por `ask = 0`
- pero no todo
- quedan familias donde el crossed persiste con `ask > 0`, y por tanto no se puede defender solo como degeneracion trivial del lado ask
- las dos familias que mas merecen lectura economica propia ahora son:
  - `large_file_threshold_edge_hard_many_crosses`
  - `persistent_soft_crossed_mid_large_scale`

### Forense raw sobre `ask > 0`

Se revisaron ejemplos raw representativos de esas dos familias:

- `large_file_threshold_edge_hard_many_crosses`
  - `VVUS 2009-09-21`
  - `PD 2006-05-26`
- `persistent_soft_crossed_mid_large_scale`
  - `GLXG 2025-04-08`
  - `YHOO 2009-06-04`

Lectura de `large_file_threshold_edge_hard_many_crosses`:

- `VVUS`:
  - `1047` crossed con `ask > 0`
  - mediana ~ `8.8 bps`, p90 ~ `26.6 bps`
  - muchos pares repetidos tipo `11.73 / 11.72`, `11.64 / 11.63`
  - aparecen bursts pequenos de la misma pareja `bid/ask`
  - lectura:
    - no parece ruido aleatorio puro
    - tampoco parece degeneracion extrema continua
    - se parece a estados crossed repetidos y de severidad moderada
- `PD`:
  - `967` crossed con `ask > 0`
  - mediana ~ `2.29 bps`, p90 ~ `7.0 bps`
  - parejas repetidas con separacion de `0.01` o `0.02`
  - runs muy cortos
  - lectura:
    - este lado del bucket si parece microestructura leve o moderada

Conclusion parcial del bucket:

- `large_file_threshold_edge_hard_many_crosses` no es una sola cosa
- mezcla:
  - casos relativamente leves
  - casos moderados persistentes
  - y una cola con ejemplos realmente severos

Lectura de `persistent_soft_crossed_mid_large_scale`:

- `GLXG`:
  - `1702` crossed con `ask > 0`
  - mediana ~ `55.7 bps`, p90 ~ `191.7 bps`
  - secuencias repetidas sobre niveles tipo `1.58 / 1.43`
  - lectura:
    - esto no es micro-ruido
    - es crossed economicamente severo y repetido
- `YHOO`:
  - `632` crossed con `ask > 0`
  - mediana ~ `6.16 bps`, p90 ~ `6.20 bps`
  - parejas repetidas de `+0.01`
  - lectura:
    - aqui si estamos ante un crossed pequeno pero persistente

Conclusion parcial del bucket:

- `persistent_soft_crossed_mid_large_scale` tambien es mixto
- contiene:
  - una subfamilia de crossed pequeno y repetido
  - otra subfamilia de crossed claramente severo con `ask > 0`

Conclusion forense actual:

- no se puede cerrar el residuo restante con una sola explicacion
- el siguiente refinamiento defendible ya no es por porcentaje crossed ni por `ask = 0`
- es separar dentro de estos dos buckets:
  - crossed positivo leve/moderado
  - crossed positivo severo

### Refinamiento final de crossed positivo

Ese corte ya se materializo en dos artefactos nuevos:

- `positive_cross_review_summary_cd_lt1b.parquet`
- `positive_cross_review_cases_cd_lt1b.parquet`

Regla usada:

- `mild`: mediana `ask > 0` < `5 bps`
- `moderate`: mediana `ask > 0` entre `5` y `25 bps`
- `severe`: mediana `ask > 0` >= `25 bps`

Lectura operativa resultante:

- `large_file_threshold_edge_hard_many_crosses`
  - `mild`: `8` casos
  - `moderate`: `11` casos
  - `severe`: `6` casos
  - lectura:
    - bucket heterogeneo real
    - no debe tratarse como una sola familia economica
- `persistent_soft_crossed_mid_large_scale`
  - `mild`: `16` casos
  - `moderate`: `18` casos
  - `severe`: `5` casos
  - lectura:
    - tampoco es una sola familia
    - el grueso cae en leve o moderado, pero existe una cola severa no trivial
- `medium_file_threshold_edge_hard_many_crosses`
  - `mild`: `5`
  - `moderate`: `3`
  - `severe`: `5`
  - lectura:
    - bucket pequeno pero muy mezclado
- `high_hard_crossed_10_to_20`
  - solo `2` casos con `ask > 0`
  - ambos severos
  - lectura:
    - cuando este bucket sale de `ask = 0`, no sale suave

Conclusiones metodologicas ya estables:

- `ask = 0` explica una parte grande del residuo duro
- el crossed con `ask > 0` no desaparece
- los buckets mas importantes ya no deben leerse como etiquetas unicas
- deben leerse como mezcla de subregimenes:
  - leve
  - moderado
  - severo

Lectura de cierre provisional para quotes:

- dataset global sin senal de corrupcion masiva
- residuo principal ya explicado por:
  - `ask = 0`
  - crossed positivo leve/moderado
  - una cola positiva severa concentrada en pocos casos

### Politica explicita good review bad

La politica metodologica ya estabilizada para `quotes <1B>` queda asi:

- `good`
  - familias dominadas por residual leve, estable o puramente temporal
  - ejemplos:
    - `clean_pass_or_other`
    - `soft_crossed_micro_noise`
    - `persistent_soft_crossed_low`
    - `utc_rollover_large_day_clean`
- `review`
  - familias mixtas donde conviven regimenes `mild` y `moderate`
  - o donde existe cola severa pero no domina la lectura del bucket
  - ejemplos:
    - `large_file_threshold_edge_hard_many_crosses`
    - `persistent_soft_crossed_mid_large_scale`
- `bad`
  - familias donde el residual con `ask > 0` sobrevive como severo
  - o donde la estructura remanente ya no parece defendible como ruido leve
  - ejemplos:
    - `medium_file_threshold_edge_hard_many_crosses`
    - `high_hard_crossed_10_to_20`

Regla verbal reproducible:

- si el residual esta dominado por `ask = 0` o por crossed positivo `mild`, tiende a `good`
- si mezcla `mild` y `moderate`, o si la cola severa existe pero no domina, queda en `review`
- si cuando sobrevive `ask > 0` lo hace como `severe`, queda en `bad`

Lectura final por los cuatro buckets abiertos:

- `high_hard_crossed_10_to_20`:
  `bad`
- `medium_file_threshold_edge_hard_many_crosses`:
  `bad`
- `large_file_threshold_edge_hard_many_crosses`:
  `review`
- `persistent_soft_crossed_mid_large_scale`:
  `review`

Implicacion metodologica:

- la mayor parte del universo sigue cerrando como `good`
- el residuo relevante queda concentrado en muy pocas familias `review/bad`
- desde aqui el valor ya no esta en seguir partiendo taxonomia, sino en usar el inspector visual para defender esos casos frontera

