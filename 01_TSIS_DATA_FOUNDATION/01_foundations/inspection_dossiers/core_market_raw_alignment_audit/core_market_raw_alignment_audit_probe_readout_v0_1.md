# Core Market RAW Alignment Audit Probe Readout v0.1

Fecha: 2026-08-21  
Run autoritativo: `20260821_core_market_raw_alignment_probe_v0_3`  
Estado: `PROBE_PASS_IMPLEMENTATION_DATA_DIFFERENCES_OBSERVED`

## Resultado

El mismo runner, wrapper, ledger, agregador, finalizador, monitor y path de
manifest previstos para producción se ejecutaron sobre `AACT`, `NA` y `MMMW`
en las cuatro familias.

```text
tasks committed              = 12/12
source Parquets inspected    = 2259
unique ticker-date rows      = 6790
physical/schema error files  = 0
partial files after close    = 0
resume adopted/reset         = 12/0
maximum task attempt         = 1
technical_status             = COMPLETED
dataset_verdict              = PROBE_COMPLETED_WITH_DIFFERENCES
```

## Resultado por familia/ticker

| Ticker | daily files/dates | 1m files/dates | quotes files/dates | trades files/dates |
|---|---:|---:|---:|---:|
| AACT | 3 / 563 | 28 / 562 | 574 / 574 | 571 / 571 |
| NA | 5 / 914 | 45 / 930 | 0 / 0 | 0 / 0 |
| MMMW | 6 / 850 | 52 / 851 | 0 / 0 | 975 / 975 |

Los tres tickers presentan diferencias de conjuntos de fechas. `AACT` comparte
el primer y último día observado entre las cuatro familias, pero contiene 12
diferencias interiores. Esto valida la necesidad de comparar conjuntos exactos
y no solo extremos.

## Evidencia de resume

Se repitió el run con `-Resume` bajo el mismo contrato:

```text
adopted = 12
reset = 0
attempt = 1 en las 12 tareas
```

El test focalizado adicional corrompe un artefacto de tarea, reanuda y verifica
que solo esa tarea se invalida y reconstruye. Las tareas válidas mantienen su
primer intento.

## Hashes terminales

```text
final_manifest.json
9D7C878022D5FB964A47EBD0E70A3FFB1150127DE33B6FE0BC0207E76B6E5CE9

audit_summary.json
947FBA30A78158FE715C498AA3FEA9DA5A70AA42FD1D73DE2F55C5AC4B879C39

run_contract_sha256
95C5ED31C740E25A74410516D16F23FE4A658AE5B3FFE692752D6E555FB9639D
```

El final manifest contiene 22 artefactos y no se halló ningún `.partial`.

## Alcance de la conclusión

El probe certifica el comportamiento técnico y la reanudación de esta versión
del auditor. No certifica el universo completo ni la igualdad de las cuatro
familias. El roster previo ya identifica ausencias objetivo en `quotes_` y
`trades`; el full run debe cuantificar todos los Parquet y ticker-fechas antes
de cualquier reparación o descarga.

```text
FULL AUDIT = NOT_AUTHORIZED
RAW MUTATION = NONE
DATA DOWNLOAD = NONE
```
