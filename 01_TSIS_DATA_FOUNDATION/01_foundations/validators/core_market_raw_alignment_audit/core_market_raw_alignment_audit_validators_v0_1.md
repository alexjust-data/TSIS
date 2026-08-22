# Core Market RAW Alignment Audit Validators v0.1

Fecha: 2026-08-21  
Estado: `PROVISIONAL_EXECUTABLE_VALIDATORS`

## Validadores por archivo

```text
CMRA-PQ-001  path exists and file_size_bytes > 0
CMRA-PQ-002  header and footer equal PAR1
CMRA-PQ-003  PyArrow ParquetFile opens
CMRA-PQ-004  metadata is readable and metadata_num_rows > 0
CMRA-PQ-005  Arrow schema is readable
CMRA-PQ-006  configured minimum columns are present
CMRA-PQ-007  observed dates can be extracted by the family rule
```

No se valida el valor económico de ninguna columna.

## Validadores de universo y cobertura

```text
CMRA-UV-001  universe rows = unique tickers = 4824
CMRA-UV-002  no null or duplicate target ticker
CMRA-UV-003  literal ticker NA is preserved
CMRA-CV-001  every target ticker has a directory in every family
CMRA-CV-002  every target ticker has Parquet and observed dates in every family
CMRA-CV-003  first and last observed dates are equal across families
CMRA-CV-004  exact ticker-date sets are equal across families
CMRA-CV-005  full runs reach the inclusive scope end in every family
```

Los símbolos fuera del target se registran, pero no bloquean. No pueden cubrir
la ausencia de un ticker objetivo; `NAN` nunca sustituye a `NA`.

## Validadores operativos

```text
CMRA-OP-001  pre-manifest exists before source scan
CMRA-OP-002  task count = selected tickers × 4 families
CMRA-OP-003  every committed task has hash-valid private artifacts
CMRA-OP-004  finalizer refuses incomplete or invalid task sets
CMRA-OP-005  no .partial file remains after terminal close
CMRA-OP-006  final manifest hashes every governed closeout artifact
CMRA-OP-007  resume preserves valid attempts and rebuilds invalid artifacts only
CMRA-OP-008  full mode requires explicit HumanAuthorizedFull
```

## Veredictos

```text
technical_status = COMPLETED
```

solo significa que el runner y el finalizador cerraron. En probe, las
diferencias se expresan como `PROBE_COMPLETED_WITH_DIFFERENCES`. En full, todo
CMRA-PQ/UV/CV/OP aplicable debe pasar para certificar alineación. Cualquier
diferencia produce un veredicto fail-closed con sus rows exactas persistidas.
