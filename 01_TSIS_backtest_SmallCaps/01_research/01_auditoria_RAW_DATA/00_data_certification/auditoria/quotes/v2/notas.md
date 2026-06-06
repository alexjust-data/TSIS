# Cómo plantearía la auditoría de quotes

  Yo la plantearía con la misma granularidad que trades, pero con capas propias de quotes.

  No haría un clon del notebook de trades.
  Haría una auditoría por capas así:

  ## Capa 1. Snapshot estructural

  Objetivo:

  - entender el universo auditado sin entrar todavía en microestructura

  Preguntas:

  - cuántos files hay
  - cuántos tickers
  - qué rango temporal cubre
  - cuántos vienen de C y cuántos de D
  - cómo se distribuyen rows por file

  Visualizaciones:

  - tabla snapshot
  - barras root C vs D
  - histograma de rows_per_file
  - percentiles median / p90 / p99

  Esto ya encaja con artefactos tipo:

  - snapshot_cd.parquet
  - root_mix_cd.parquet

  ## Capa 2. Integridad temporal y de partición

  Objetivo:

  - separar problemas físicos o de partición antes de hablar de mercado

  Preguntas:

  - cuántos files tienen timestamp_out_of_partition_day
  - cuánto pesa eso por root, año, mes y ticker
  - si el drift temporal es cosmético o estructural

  Visualizaciones:

  - barras de timestamp_out_of_partition_day
  - serie temporal por año/mes
  - heatmap year x root
  - top tickers afectados

  Esto debe quedar muy visible porque en quotes ya viste que el timestamp drift es real.

  ## Capa 3. Microestructura bid/ask

  Objetivo:

  - entender el corazón del problema de quotes

  Preguntas:

  - cuánto crossed market hay
  - cuándo el crossed market es leve y cuándo es persistente
  - cuántos files tienen crossed_ratio_pct = 100
  - qué relación hay entre:
      - crossed_rows
      - crossed_ratio_pct
      - ask_price = 0
      - ask_integer_with_crossed_anomaly

  Visualizaciones:

  - histograma de crossed_ratio_pct
  - bandas de severidad de crossed
  - scatter rows vs crossed_ratio_pct
  - scatter crossed_rows vs rows
  - top casos extremos
  - distribución de ask_price == 0

  Esta es la capa más importante en quotes.

  ## Capa 4. Concentración

  Objetivo:

  - saber si el problema está extendido o concentrado

  Preguntas:

  - en qué años y meses se concentra el hard fail
  - qué tickers dominan el residuo
  - si hay sesgo por root C o D
  - si 2025-2026 están especialmente cargados, como ya viste

  Visualizaciones:

  - month_rate
  - year_rate
  - top 30 tickers por hard fail
  - top 30 tickers por crossed_ratio
  - comparación C vs D

  Aquí usaría directamente:

  - month_rate_cd.parquet
  - year_rate_cd.parquet
  - ticker_focus_top30_cd.parquet
  - issue_root_view_cd.parquet
  - warn_severity_view_cd.parquet

  ## Capa 5. Taxonomía operativa

  Objetivo:

  - transformar issues sueltas en familias defendibles

  Aquí el resultado tiene que ser parecido a lo que logramos en trades:
  no hablar solo de PASS / SOFT_FAIL / HARD_FAIL, sino de familias.

  Ya tienes una taxonomía bastante buena:

  - clean_pass_or_other
  - mild_crossed_micro_noise
  - persistent_soft_crossed_market
  - moderate_crossed_market
  - timestamp_partition_shift
  - soft_crossed_plus_timestamp_shift
  - hard_crossed_market
  - small_file_hard_crossed

  Esto debe ser una capa explícita del notebook.

  Visualizaciones:

  - barra de taxonomías ordenadas por peso
  - distribución por root
  - distribución por año
  - ejemplos top por taxonomía

  ## Capa 6. Forense puntual

  Objetivo:

  - demostrar con raw que los casos extremos no son fantasmas estadísticos

  Esto ya lo hacías con:

  - focus_examples
  - forensic_candidates
  - carga puntual del quotes.parquet

  Visualizaciones y vistas:

  - preview raw del file
  - primeras/últimas filas
  - columnas clave:
      - bid_price
      - ask_price
      - sip_timestamp o timestamp equivalente
  - tabla resumen del file
  - si se puede, una vista temporal simple del bid/ask

  Aquí no hay que sobrecargar.
  Tiene que ser:

  - select case
  - load raw
  - inspect

  ———

  # Cómo lo estructuraría en notebooks

  Después de trades, yo dejaría quotes en dos notebooks también.

  ## Notebook 1: metodológico

  Algo tipo:

  - 04_quotes_root_cause_methodology.ipynb
  - o reciclar el 03 si prefieres no multiplicar nombres

  Objetivo:

  - explicar las capas
  - validar la taxonomía
  - enseñar ejemplos extremos
  - servir de notebook “de pensamiento”

  ## Notebook 2: closeout full

  Algo tipo:

  - 05_quotes_full_lt1b_closeout.ipynb o 04_quotes_full_cd_closeout.ipynb

  Objetivo:

  - consumir solo artefactos
  - no recalcular nada pesado
  - mostrar el cierre final del universo auditado

  Igual que hicimos con:

  - 05 metodológico en trades
  - 06 closeout full

  ———

  # Qué visualizaciones pondría sí o sí

  Si tuviera que fijar un conjunto mínimo pero fuerte para quotes, sería este:

  1. Snapshot general

  - filas totales
  - tickers
  - roots
  - rango temporal
  - histograma de tamaño de file

  2. Severidad

  - barras PASS / SOFT_FAIL / HARD_FAIL
  - porcentaje sobre total

  3. Root cause duro

  - top issues
  - top warns

  4. Crossed market

  - histograma de crossed_ratio_pct
  - bandas:
      - 0
      - 0-1%
      - 1-5%
      - 5-25%
      - 25-100%
      - 100%

  5. Concentración temporal

  - año
  - mes

  6. Concentración por ticker

  - top 30

  7. Taxonomía

  - barra de familias operativas

  8. Forense

  - 5-10 casos top
  - raw puntual

  ———

  # Qué aprendería de trades para no repetir errores

  Esto es lo más importante.

  ## 1. No mezclar notebook metodológico con closeout final

  En quotes lo separaría antes.

  ## 2. No depender de artefactos gigantes intermedios

  Si snapshot_inputs_cd.parquet y concentration_inputs_cd.parquet no son necesarios, fuera del flujo final.

  ## 3. No dejar la cache en ruta rara si va a ser canónica

  Ahora está en:

  - C:\Users\AlexJ\.codex\memories\backtest_SmallCaps\quotes_cd_notebook_cache

  Eso sirvió por permisos, pero si va a ser el flujo oficial, lo movería a un sitio documentado del proyecto o lo dejaría explícitamente como cache oficial.

  ## 4. Construir desde el principio un case_index rico

  En quotes lo haría con columnas como:

  - taxonomy
  - root
  - severity
  - focus_issue
  - focus_warn
  - crossed_ratio_pct
  - timestamp_out_of_partition_rows
  - rows
  - ticker
  - date

  Eso luego simplifica muchísimo el notebook.

  ## 5. Forense puntual, no preload full

  Eso ya está bien decidido en quotes, y hay que mantenerlo.

  ———

  # Mi propuesta concreta para quotes

  Si empezáramos ahora bien, yo haría esto:

  ## Fase A. Consolidar build offline

  Mantener un único builder pesado:

  - build_quotes_cd_audit_artifacts.py

  Y asegurar que deja:

  - snapshot
  - severidad
  - roots
  - issues
  - warns
  - concentración temporal
  - concentración por ticker
  - taxonomía
  - case index
  - candidatos forenses
  - manifest
  - opcional: build_log.json

  ## Fase B. Helper de vista

  Crear o consolidar un helper tipo:

  - 58_quotes_view_cd.py

  Con funciones:

  - load_manifest
  - load_all_artifacts
  - plot_snapshot
  - plot_severity
  - plot_crossed_band
  - plot_year_rate
  - plot_month_rate
  - plot_taxonomy
  - load_forensic_case

  ## Fase C. Notebook metodológico

  Con secciones:

  - portada
  - contexto
  - capa 3 microestructura
  - capa 4 concentración
  - capa 5 taxonomía
  - capa 6 forense
  - cierre

  ## Fase D. Notebook closeout

  - top ejemplos por taxonomía
  - conclusión final

  python "C:
  \TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py"que hace exactmanente esto ? python "C:
  \TSIS_Data\v1\backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py"


  ------


   En trades, el bucle fino fue:

  - detectar residuos
  - refinar capas
  - separar marginal vs estructural
  - ir clusterizando causas hasta tener una taxonomía defendible

  En quotes, eso también se puede hacer, pero el eje no es el mismo. Aquí el refinado fino gira alrededor de:

  - crossed_ratio_pct
  - crossed_rows
  - timestamp_out_of_partition_day
  - ask_integer_pct
  - ask_eq_round_bid_pct
  - mezcla root C/D
  - anatomía de files pequeños
  - concentración por ticker / año / mes

  O sea:

  - en trades refinábamos el problema de elegibilidad y consistencia económica del tape
  - en quotes refinaremos el problema de microestructura y degradación del libro

  ¿Este builder sirve para ese bucle fino?
  Sí, como base sí.

  Porque ya te deja material para iterar:

  - snapshot
  - severity_counts
  - root_mix
  - hard_issue_counts
  - warn_counts
  - issue_root_view
  - warn_severity_view
  - month_rate
  - year_rate
  - ticker_focus_top30
  - crossed_band
  - micro_sample
  - integer_anomaly
  - timestamp_view
  - focus_examples
  - forensic_candidates
  - taxonomy_summary
  - case_index

  Eso permite exactamente el tipo de trabajo que hicimos en trades:

  - mirar salida
  - entender qué domina
  - proponer un corte más fino
  - volver a materializar
  - volver a leer
  - refinar taxonomía
  - cerrar familias operativas


  ---


python "C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification\auditoria\quotes\v2\cell_code\build_quotes_cd_audit_artifacts_v2.py" --refresh