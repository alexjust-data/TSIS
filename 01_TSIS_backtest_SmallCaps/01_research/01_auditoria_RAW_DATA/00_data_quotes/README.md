Para quotes, el orden debería seguir exactamente el ciclo real del sistema y separar:

  - preparación de inputs
  - contrato de descarga
  - estado real
  - validación
  - coverage
  - recovery

  Harías bien en dejar dentro de C:\TSIS_Data\02_backtest_SmallCaps\notebooks\00_data_certification_v2 esta estructura:

  00_data_certification_v2/
    README.md
    00_run_context_and_sources.ipynb
    01_universe_lineage_quotes.ipynb
    02_task_builder_contract_quotes.ipynb
    03_agent01_download_contract.ipynb
    04_agent01_run_audit.ipynb
    05_agent02_validation_audit.ipynb
    06_agent03_coverage_audit.ipynb
    07_recovery_builder_audit.ipynb
    08_final_run_reconstruction.ipynb
    cell_code/
      quotes/
        00_paths_and_helpers.py
        01_universe_lineage_quotes.py
        02_task_builder_contract_quotes.py
        03_agent01_download_contract.py
        04_agent01_run_audit.py
        05_agent02_validation_audit.py
        06_agent03_coverage_audit.py
        07_recovery_builder_audit.py
        08_final_run_reconstruction.py

  ## Orden y propósito

  ### 00_run_context_and_sources.ipynb

  Primero.

  Debe fijar el contexto inmutable del run actual:

  - run_id
  - run_dir
  - quotes_root
  - paths oficiales de universo, lifecycle, tasks, events, validation, coverage
  - timestamps y existencia de artefactos
  - hashes si los calculas

  Objetivo:

  - que todo notebook posterior herede el mismo contexto
  - evitar auditorías contra paths distintos

  ### 01_universe_lineage_quotes.ipynb

  Segundo.

  Debe responder:

  - cuál es el universo base
  - qué derivados lleva hasta el universo refinado de quotes
  - qué artefactos exactos intervienen
  - dónde entra tickers_2005_2026_upper_excluding_ohlcv_1m_missing_vs_daily_ge_2B_or_null.parquet

  Objetivo:

  - dejar cerrada la genealogía del universo antes de hablar de tasks

  ### 02_task_builder_contract_quotes.ipynb

  Tercero.

  Debe reconstruir y auditar cómo se generó:

  - tickers_quotes_prod.csv
  - tasks_quotes_prod.csv
  - tasks_quotes_prod_meta.json

  Y además definir cómo debería construirse en v2:

  - calendario oficial XNYS
  - rango explícito del run
  - sin bdate_range
  - sin notebooks manuales productivos

  Objetivo:

  - formalizar el contrato del Task Builder

  ### 03_agent01_download_contract.ipynb

  Cuarto.

  Aquí defines el contrato esperado de Agent01:

  - qué consume
  - qué escribe
  - qué no puede decidir
  - cómo debe comportarse resume
  - estados válidos
  - integridad física mínima

  Objetivo:

  - convertir Agent01 en una pieza acotada y auditable

  ### 04_agent01_run_audit.ipynb

  Quinto.

  Audita el run real de Agent01:

  - download_events_history.csv
  - download_events_current.csv
  - download_live_status.json
  - download_state.json
  - parquets en D:\quotes

  Objetivo:

  - comparar contrato esperado vs ejecución real
  - detectar incoherencias físicas y de estado

  ### 05_agent02_validation_audit.ipynb

  Sexto.

  Audita:

  - descubrimiento de disco
  - validación por archivo
  - severidades PASS/SOFT_FAIL/HARD_FAIL
  - retry semántico

  Artefactos:

  - quotes_agent_strict_events_current.csv
  - live_status_quotes_strict.json
  - retry_queue_quotes_strict_current.csv
  - quotes_reconciliation_status.json

  Objetivo:

  - separar claramente “descargado” de “usable”

  ### 06_agent03_coverage_audit.ipynb

  Séptimo.

  Solo cobertura y reporting:

  - coverage_by_ticker
  - quality_summary_by_ticker
  - causes_by_ticker
  - run_summary.json

  Objetivo:

  - confirmar que Agent03 es diagnóstico/gate, no productor de inputs

  ### 07_recovery_builder_audit.ipynb

  Octavo.

  Aquí reconstruyes el recovery real:

  - tasks_quotes_prod.csv
  - download_events_current.repaired_from_history.csv
  - disk_quotes_inventory.csv
  - reconciliaciones
  - tasks_quotes_prod_missing_only_final.csv
  - tasks_quotes_prod_missing_only_final_v2.csv

  Objetivo:

  - formalizar cómo debería existir un Recovery Builder
  - dejar claro qué pasó realmente en este run

  ### 08_final_run_reconstruction.ipynb

  Noveno y último.

  Debe cerrar el caso completo:

  - línea temporal del run
  - universo usado
  - tasks usados
  - estado final Agent01/02/03
  - recovery
  - comando final ejecutado
  - hallazgos y rediseño propuesto

  Objetivo:

  - tener un notebook único de cierre auditable

  ## Cómo lo haría en la práctica

  No metería lógica larga dentro de las celdas. Haría notebooks finos y toda la lógica en:

  - cell_code/quotes/*.py

  Así cada notebook:

  - fija contexto
  - llama un bloque de código
  - muestra tablas y conclusiones

  ## README inicial

  En README.md pondría solo el orden canónico:

  1. 00_run_context_and_sources.ipynb
  2. 01_universe_lineage_quotes.ipynb
  3. 02_task_builder_contract_quotes.ipynb
  4. 03_agent01_download_contract.ipynb
  5. 04_agent01_run_audit.ipynb
  6. 05_agent02_validation_audit.ipynb
  7. 06_agent03_coverage_audit.ipynb
  8. 07_recovery_builder_audit.ipynb
  9. 08_final_run_reconstruction.ipynb

  ## Recomendación concreta

  Si vas a empezar ya, empezaría por crear solo estos 3 primero:

  - 00_run_context_and_sources.ipynb
  - 01_universe_lineage_quotes.ipynb
  - 02_task_builder_contract_quotes.ipynb

  Porque sin esos tres no tienes fijado:

  - qué run auditas
  - de dónde sale el universo
  - de dónde salen las tasks
