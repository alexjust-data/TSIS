# Test Runs

Esta carpeta guarda outputs de ejecuciones de tests.

No es una carpeta de raw data.
No es una carpeta de tablas institucionales.
No debe contener copias completas de datasets pesados.

## Layout obligatorio

Cada ejecucion relevante debe crear una carpeta:

```text
YYYY-MM-DD/<run_id>/
```

Ejemplo:

```text
2026-06-22/data_foundation_outputs_instrument_master_market_calendar_v0_1/
```

Contenido recomendado:

```text
metadata.json
summary.md
pytest_output.txt
junit.xml
coverage.xml
artifacts/
```

## Metadata minima

`metadata.json` debe incluir:

- `run_id`
- `run_date`
- `module`
- `test_scope`
- `contracts_validated`
- `datasets_validated`
- `input_paths`
- `output_paths`
- `evidence_paths`
- `git_commit` si existe
- `agent_or_operator`
- `status`

## Regla de tamano

Los outputs de tests deben ser evidencia, no duplicados de la data. Guardar:

- hashes;
- conteos;
- muestras pequenas;
- reports;
- diffs;
- logs;
- snapshots externos pequenos.

No guardar:

- copias completas de parquet raw;
- carpetas completas de quotes/trades;
- materializaciones institucionales oficiales.

