# Core Market Session Coverage Audit Validators v0.1

- `CMSCA-CV-001`: universo Full exactamente 4.824, sin duplicados y con ticker literal `NA`.
- `CMSCA-CV-002`: todo artefacto fuente consumido procede de una tarea `committed`; cualquier otra tarea se representa como `SOURCE_PENDING` o `SOURCE_UNAVAILABLE`.
- `CMSCA-CV-003`: las fechas UTC reconstruidas desde `ohlcv_1m.ts_utc` coinciden exactamente con el inventario UTC de la auditoría física fuente.
- `CMSCA-CV-004`: `session_date_et` se deriva con `America/New_York`, incluido DST y rollover UTC.
- `CMSCA-CV-005`: cada tarea escribe artefactos privados atómicos y un manifest final con tamaño y SHA-256.
- `CMSCA-CV-006`: ninguna ausencia de una familia pendiente entra en `family_gap_ledger`.
- `CMSCA-CV-007`: el ledger distingue hecho (`missing_family`, fecha, familias presentes) de diagnóstico (`gap_class`, confianza, vendor reconciliation).
- `CMSCA-CV-008`: el cierre Full exige 4.824 tareas comprometidas, cero fallidas y schemas exactos.
- `CMSCA-CV-009`: el cierre declara por familia si alcanza
  `2026-08-20`; una cola común posterior al máximo observado se registra como
  `UNVERIFIED_COMMON_TAIL`, nunca se omite del resultado.
