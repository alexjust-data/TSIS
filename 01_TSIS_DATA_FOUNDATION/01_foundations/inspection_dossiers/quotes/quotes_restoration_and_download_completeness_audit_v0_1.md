# Quotes restoration and download completeness audit v0.1

Estado: `AUDIT_PASS_DATASET_REMEDIATION_REQUIRED`  
Fecha de cierre: `2026-08-24`

## Objetivo

Determinar si la restauración `G:/TSIS/data/quotes`, unida al RAW retenido
`G:/TSIS/data/quotes_`, contiene la cobertura Quotes requerida para los 4.824
tickers entre `2005-01-01` y `2026-08-20`.

Esta auditoría es de cobertura y descarga. No recertifica la calidad económica
de cada quote ni modifica ningún RAW.

## Veredicto

La restauración es físicamente sana, pero incompleta. La unión de las dos raíces
no cubre el intervalo completo solicitado.

```text
AUDITORÍA TÉCNICA                         PASS
INTEGRIDAD DE LOS ARCHIVOS RESTAURADOS   PASS
RESTAURACIÓN COMPLETA DEL INVENTARIO C   FAIL
DESCARGA 4.824 × INTERVALO COMPLETO      NOT_CERTIFIED
REMEDIACIÓN                              REQUIRED
```

## Restauración física

Comparación contra el inventario C pre-merge cerrado:

```text
archivos conocidos no vacíos esperados   1.767.826
archivos restaurados coincidentes         1.412.747
archivos todavía ausentes                   355.079
archivos extra                                     0
errores físicos/schema                            0
diferencias de tamaño                             0
```

Los 1.412.747 archivos restaurados contienen `9.169.821.927` filas y
`111.186.222.301` bytes. No existe ninguna diferencia de row count contra su
metadata histórica.

Evidencia:

- `C:/TSIS_Data/runs/data_ops/quotes_restoration_audit/20260824_quotes_restoration_audit_v0_1/03_closeout/final_manifest.json`
- `C:/TSIS_Data/runs/data_ops/quotes_restoration_audit/20260824_quotes_restoration_audit_v0_1/03_closeout/known_nonempty_missing.parquet`

## Explicación exacta de Daily presente / Quotes ausente

La diferencia histórica de `1.793.296` ticker-fecha queda completamente
explicada:

```text
disponibles en la restauración C            1.361.704
C conocido no vacío todavía ausente           338.235
respuesta API vacía pendiente de recheck        92.443
ticker literal NA nunca ejecutado                  914
residuo inexplicado                                  0
```

La raíz restaurada no contiene todo lo que falta: después de unirla con
`quotes_`, todavía quedan `355.076` archivos C conocidos no vacíos sin
cobertura. Solo tres de los `355.079` ausentes físicos ya estaban cubiertos por
`quotes_`.

Evidencia:

- `C:/TSIS_Data/runs/data_ops/quotes_restoration_reconciliation/20260824_quotes_restoration_reconciliation_v0_1/03_closeout/final_manifest.json`
- `C:/TSIS_Data/runs/data_ops/quotes_restoration_reconciliation/20260824_quotes_restoration_reconciliation_v0_1/02_reconciliation/daily_without_current_quotes_decomposition.parquet`

## Por qué la descarga histórica no cubría el intervalo completo

El master histórico no era el producto cartesiano 4.824 × sesiones. Se creó a
partir de ventanas OHLC observadas. Además:

- el ticker literal `NA` se perdió por el tratamiento NA por defecto de
  `pandas.read_csv`;
- una respuesta `DOWNLOADED_EMPTY` se trataba como terminal sin una
  confirmación independiente;
- el master incluía días laborables no XNYS y omitía millones de sesiones fuera
  de las ventanas OHLC de cada ticker;
- la descarga terminaba en marzo de 2026, no el 20 de agosto de 2026.

En el comparador XNYS usado por esta auditoría:

```text
tickers                                  4.824
sesiones XNYS                            5.442
producto completo                   26.252.208
ticker-fecha nunca consultados      15.267.746
```

XNYS es aquí un comparador operativo homogéneo. No sustituye un lifecycle
master de identidad/listing y no demuestra que todo ticker deba producir filas
en toda sesión.

## Plan completo de remediación

El conjunto exacto y sin solapamientos para completar o revalidar la cobertura
es:

```text
nunca consultados en el intervalo completo  15.267.746
C conocido no vacío físicamente ausente         355.076
respuesta vacía con Daily presente               92.443
TOTAL                                         15.715.265
```

Propiedades certificadas del plan:

```text
claves duplicadas/solapadas        0
fechas fuera de XNYS               0
tickers afectados              4.824
intervalos contiguos          209.701
suma de sesiones de intervalos 15.715.265
```

Artefactos ejecutables:

- detalle exacto ticker-fecha:
  `C:/TSIS_Data/runs/data_ops/quotes_complete_interval_remediation_plan/20260824_quotes_complete_interval_remediation_plan_v0_1/03_closeout/quotes_complete_interval_exact_daily_requests.parquet`
- intervalos contiguos:
  `C:/TSIS_Data/runs/data_ops/quotes_complete_interval_remediation_plan/20260824_quotes_complete_interval_remediation_plan_v0_1/03_closeout/quotes_complete_interval_contiguous_intervals.csv`
- manifest:
  `C:/TSIS_Data/runs/data_ops/quotes_complete_interval_remediation_plan/20260824_quotes_complete_interval_remediation_plan_v0_1/03_closeout/final_manifest.json`

## Ejecución recomendada

1. Mantener `quotes` y `quotes_` inmutables.
2. Descargar a una nueva versión mediante REST por ticker e intervalo contiguo.
3. Preservar todos los campos y todas las filas devueltas por Massive.
4. Preservar el ticker literal `NA` con `keep_default_na=false`.
5. No considerar una única respuesta vacía como ausencia certificada.
6. Escribir primero en staging transaccional; compactar después por
   ticker-fecha con procedencia e idempotencia de ingestión.
7. Reejecutar auditoría física, unión de cobertura y reconciliación final.

Gates de cierre:

```text
4.824/4.824 tickers terminales
0 requests sin estado terminal
0 archivos conocidos no vacíos ausentes
0 respuestas vacías Daily-presente sin recheck
0 truncamientos de paginación
0 fallos físicos/schema
0 duplicados de ingestión en canónico
```

El wrapper literal-safe preparado vive en:

- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/download_quotes_literal_safe_v0_1.py`

La descarga productiva no se ha lanzado. Antes debe autorizarse explícitamente
el endpoint/credencial vigentes de Massive y ejecutarse un pilot
production-equivalent con el mismo runner, schema, manifests y certifier.

## Scripts utilizados

- `scripts/quotes_restoration_audit/audit_quotes_restoration.py`
- `scripts/quotes_restoration_audit/finalize_quotes_restoration_reconciliation.py`
- `scripts/quotes_restoration_audit/audit_quotes_empty_response_evidence.py`
- `scripts/quotes_restoration_audit/audit_quotes_full_interval_scope.py`
- `scripts/quotes_restoration_audit/build_quotes_complete_interval_remediation_plan.py`
- `scripts/quotes_restoration_audit/monitor_quotes_restoration_audit.py`
- `scripts/quotes_restoration_audit/run_quotes_restoration_audit.ps1`
- `scripts/quotes_restoration_audit/stop_quotes_restoration_audit.ps1`

## Limitaciones

- Una respuesta vacía puede ser legítima; solo queda marcada para reconsulta.
- El calendario global XNYS no resuelve por sí solo altas, bajas, aliases ni
  ticker reuse.
- Esta auditoría prueba presencia, ausencia e integridad física; no declara que
  cada quote individual sea económicamente correcto.
