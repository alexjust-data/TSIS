# Core Market Family Download Audit Schema v0.1

Artefactos finales por familia:

- `{family}_session_activity.parquet`: `family`, ticker literal, `session_date_et`, conteos y flags de premarket/RTH/afterhours/outside, estado de clasificación, evidencia física y completitud.
- `{family}_ticker_coverage.parquet`: una fila por ticker con archivos, bytes, filas, primera/última fecha, límites de scope, errores y estado de completitud.
- `audit_summary.json`, `final_manifest.json` y `FAMILY_DOWNLOAD_AUDIT.md`.

`session_date_et` es Arrow `date32`. Los conteos/flags intradía de Daily son `NULL` porque una barra diaria no demuestra en qué sesión ocurrió la actividad. El ticker `NA` siempre es string literal, nunca null.

Estados principales:

```text
physical_evidence_state = ADOPTED_CLOSED_PHYSICAL_AUDIT
download_completeness_state = PRESENT_VALID_FILE
                              | NOT_CERTIFIED_PROVIDER_EMPTY_UNRESOLVED
```

