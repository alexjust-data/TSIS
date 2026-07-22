Sí, de acuerdo. Entonces cambiaría la prioridad.

  Para minute/ohlcv_1m_raw, el foco principal no debe ser “si vw viene mal”, porque vw es una columna derivable/reconstruible si tenemos
  OHLCV y/o trades suficientes. Importa, pero no puede gobernar toda la lectura de calidad.

  Yo seguiría así:

  1. Separar calidad estructural/core de calidad vw

     El dossier debe decir explícitamente:

     La calidad principal de ohlcv_1m_raw se decide por la validez de la barra:
     timestamp, partición, ticker, open, high, low, close, volume, transactions, cobertura y duplicados.

     vw_* es una familia importante, pero secundaria para consumo que no use vw.

  2. Crear una taxonomía nueva de inspección

     No centrada en vw_*, sino en:
      - schema/readability: puede leerse el parquet, columnas, tipos, encoding, ticker.
      - partition_integrity: ticker/year/month/path coherentes.
      - timestamp_integrity: timestamps parseables, monotónicos, minuto válido, timezone si aplica.
      - ohlc_integrity: precios positivos, low <= open/close <= high, rangos no absurdos.
      - volume_integrity: volumen no negativo, masa razonable, relación con active minutes.
      - duplicate_integrity: duplicados exactos o duplicados ticker-minute.
      - coverage_density: días activos, gaps internos, meses incompletos.
      - cross_dataset_alignment: coherencia contra daily/trades/quotes cuando aplique.
      - vw_quality: solo como capa adicional.

  3. Reclasificar la pregunta institucional

     La pregunta no debe ser:

     ¿Cuántos casos tienen vw fuera de rango?

     Debe ser:

     Si ignoro vw, ¿la barra 1m es fiable como OHLCV raw?

     Y después:

     Si uso vw, ¿qué parte queda condicionada o excluida?

  4. Crear casepacks visuales por calidad core

     Haría primero ejemplos para:
      - casos core_good_without_vw
      - casos schema/readability_issue
      - casos timestamp_or_partition_issue
      - casos ohlc_price_invalid
      - casos coverage_sparse_but_valid
      - casos coverage_gap_problem
      - casos volume_anomaly
      - casos duplicate_or_collision
      - casos vw_bad_but_ohlcv_core_ok
      - casos vw_bad_and_core_bad

  5. Actualizar el README de minute

     Añadiría una sección fuerte:

     Prioridad de calidad en minute

     Con esta jerarquía:

     Nivel 1: legibilidad / schema / partición
     Nivel 2: timestamp / unidad ticker-minute
     Nivel 3: OHLC / volumen / cobertura
     Nivel 4: alineación con daily/trades/quotes
     Nivel 5: vw

     Y dejaría claro que vw no debe ocultar una buena barra OHLCV ni rehabilitar una mala barra.

  6. Revisar los assets actuales

     Antes de crear nada nuevo, buscaría si en los parquet actuales ya hay columnas suficientes para separar:
      - problemas core no-vw
      - problemas solo-vw
      - problemas mixtos

     Si los assets actuales no lo permiten, haría un script inspector nuevo que lea raw_1m_lt1b_filtered_closeout.parquet y genere un
     manifest de familias core.

  7. Solo después produciría los MD

     El orden natural sería:
      - minute_core_quality_model_v0_1.md
      - minute_core_quality_case_manifest_v0_1.csv/parquet
      - minute_core_quality_inspection_readout_v0_1.md
      - casepacks por familia
      - actualización de minute/README.md
      - actualización de inspection_dossiers/README.md
      - entrada en CHANGELOG.md

  Mi recomendación concreta: empezar por el modelo de calidad core de minute, no por imágenes. Primero definimos qué significa “dato 1m
  bueno” sin depender de vw. Luego generamos manifest y muestras visuales.