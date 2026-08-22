# Core Market Session Coverage Audit Schema Contract v0.1

Artefactos canónicos del run:

- `ohlcv_1m_session_dates_et.parquet`: `ticker`, `session_date_et`.
- `ticker_family_session_presence.parquet`: una fila por `ticker × session_date_et`; los flags de una familia no comprometida son `NULL`.
- `family_gap_ledger.parquet`: ausencia observada, familias presentes, clasificación, confianza, evidencia de shard y necesidad de reconciliación Massive.
- `ticker_family_windows.parquet`: estado fuente, conteo, primera/última fecha,
  ausencias y límites `UNVERIFIED_BEFORE_FIRST_OBSERVED` /
  `UNVERIFIED_AFTER_LAST_OBSERVED` por `ticker × family`.
- `gap_summary_by_family.csv`, `gap_summary_by_class.csv`, `audit_summary.json`, `final_manifest.json` y `CORE_MARKET_SESSION_COVERAGE_AUDIT.md`.

Las fechas usan Arrow `date32`. Los ticker son strings literales; `NA` nunca es null. Los flags de presencia son nullable para representar `SOURCE_PENDING` sin fabricar una ausencia.

Los intervalos boundary son calendario civil, no una lista de sesiones
esperadas. No se denominan data faltante porque el calendario gobernado
disponible termina en 2026-03-09 y no resuelve por sí solo listing/delisting.
