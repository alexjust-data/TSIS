# Core Market RAW Alignment Audit Handoff v0.1

Fecha: 2026-08-21  
Estado: `DESIGN_HANDOFF_NOT_IMPLEMENTED`  
Owner: `01_TSIS_DATA_FOUNDATION / 01_foundations`  
Severidad semántica: `HIGH`  

## 1. Propósito

Este documento permite que un agente sin contexto previo implemente y ejecute
una auditoría física y de cobertura mínima sobre las cuatro familias RAW de
mercado que TSIS quiere mantener sincronizadas.

La auditoría no valida precios, volúmenes, spreads, trades ni quotes fila por
fila. Debe responder, con evidencia reproducible:

1. si las cuatro familias contienen los mismos 4.824 tickers esperados;
2. si cada ticker tiene la misma primera y última fecha en las cuatro familias;
3. si cada ticker tiene exactamente el mismo conjunto de fechas observadas;
4. si todos los Parquet existen, tienen bytes, se pueden abrir, tienen metadata
   no truncada, al menos una fila y un schema legible.

No se permite declarar `PASS` solo porque el proceso termine.

## 2. Alcance cerrado

Solo se auditan estas raíces:

```text
G:\TSIS\data\ohlcv_daily
G:\TSIS\data\ohlcv_1m
G:\TSIS\data\quotes_
G:\TSIS\data\trades_ticks_prod_2005_2026
```

No forman parte de esta tarea:

```text
G:\TSIS\data\additional
G:\TSIS\data\financial
G:\TSIS\data\Halts
G:\TSIS\data\short
```

Ventana solicitada:

```text
start_date_inclusive = 2005-01-01
end_date_inclusive   = 2026-08-20
```

No existe aquí el concepto de «ventanas certificadas» que reduzca la petición
mediante `first_seen_date` o `last_observed_date`. Se usa la ventana global y se
mide lo que existe físicamente por ticker. No se inventan observaciones antes
del listado ni después del deslistado.

## 3. Autoridad del universo esperado

La lista base de 4.824 miembros debe leerse de:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet
```

Antes de implementar el runner hay que registrar:

- SHA-256 del artefacto;
- número exacto de filas y tickers únicos;
- nombre de la columna de ticker;
- conservación literal de símbolos, incluido `NA`;
- duplicados del identificador lógico, si existen.

Invariante:

```text
EXPECTED_UNIVERSE_MEMBERS = 4824
```

No se puede sustituir esta lista exacta por un rango alfabético, un `min/max`,
el universo hallado en una familia o una lista de activos actuales.

## 4. Auditoría mínima

### 4.1. Por archivo Parquet

Para cada `*.parquet` descubierto:

```text
file_exists              = TRUE
file_size_bytes          > 0
parquet_openable         = TRUE
metadata_readable        = TRUE
metadata_num_rows        > 0
schema_readable          = TRUE
```

`parquet_openable`, metadata y schema deben resolverse abriendo el archivo con
PyArrow y leyendo `ParquetFile.metadata` y `ParquetFile.schema_arrow`. Esto
detecta un footer ausente o truncado sin leer todas las columnas. Puede
comprobarse además la firma `PAR1` inicial y final, sin añadir una segunda
lectura completa.

Inventario mínimo:

```text
family
absolute_path
relative_path
file_size_bytes
metadata_num_rows
row_group_count
schema_fingerprint
parquet_openable
metadata_readable
schema_readable
error_class
error_message
```

El fingerprint registra los schemas existentes. No valida todavía cada campo
frente a Massive ni exige que familias distintas compartan schema.

### 4.2. Por ticker y fecha

Para cada familia se derivan únicamente:

```text
ticker
observed_date
```

Después:

```text
first_observed_date
last_observed_date
observed_date_count
```

La prueba fuerte compara el conjunto exacto `(ticker, observed_date)`. Comparar
solo los extremos no detecta huecos interiores.

Resultados por ticker:

```text
present_in_ohlcv_daily
present_in_ohlcv_1m
present_in_quotes
present_in_trades
first_date_by_family
last_date_by_family
date_count_by_family
ticker_set_equal
window_equal
observed_date_set_equal
```

### 4.3. Granularidad física

No debe suponerse que las cuatro raíces particionan igual.

- Si ticker y fecha están codificados inequívocamente en el path, se obtienen
  del path y el Parquet se valida mediante metadata.
- Si un archivo agrupa varias fechas —por ejemplo ticker-año o ticker-mes— se
  lee solo la columna mínima de fecha/timestamp y se proyecta a
  `observed_date`.
- No se leen OHLC, volumen, VWAP, bid, ask, precio, size, condiciones ni otros
  campos de mercado.

Antes de congelar el parser debe inspeccionarse una muestra de paths y schemas
de cada familia y documentarse la regla usada para ticker y fecha.

## 5. Fuera de alcance

- igualdad económica entre las cuatro familias;
- reconstrucción de barras;
- precios, volumen, VWAP o número de transacciones;
- outliers y duplicados internos de eventos;
- monotonicidad de timestamps;
- condiciones de Massive;
- contenido RTH, premarket o after-hours de `trades`;
- aliases, CIK, FIGI o continuidad económica previa al ticker;
- reparación, reescritura o eliminación de RAW;
- descarga de datos nuevos.

Esta auditoría demuestra alineación física de tickers y fechas, no que el
contenido de mercado sea económicamente correcto o completo.

## 6. Regla de comparación

La autoridad externa es la lista de 4.824 tickers. La sincronización se prueba
comparando los cuatro conjuntos observados.

No se declara `quotes_` como verdad por defecto. Si las familias difieren, se
identifican exactamente los ticker-fechas que faltan o sobran en cada una.

Clases de diferencia:

```text
MISSING_EXPECTED_TICKER
EXTRA_TICKER
FIRST_DATE_MISMATCH
LAST_DATE_MISMATCH
MISSING_TICKER_DATE
EXTRA_TICKER_DATE
ZERO_BYTE_PARQUET
UNREADABLE_PARQUET
EMPTY_PARQUET
UNREADABLE_SCHEMA
```

## 7. Criterio de cierre

Solo se permite `PASS` cuando:

```text
EXPECTED_UNIVERSE_MEMBERS              = 4824
MISSING_EXPECTED_TICKERS_ANY_FAMILY    = 0
EXTRA_TICKERS_UNRESOLVED               = 0
UNREADABLE_PARQUETS                    = 0
ZERO_BYTE_PARQUETS                     = 0
EMPTY_PARQUETS                         = 0
UNREADABLE_SCHEMAS                     = 0
TICKERS_WITH_FIRST_DATE_MISMATCH       = 0
TICKERS_WITH_LAST_DATE_MISMATCH        = 0
MISSING_TICKER_DATES                   = 0
EXTRA_TICKER_DATES                     = 0
```

Si el runner termina pero alguna invariante falla:

```text
RUN_STATUS      = COMPLETED
DATASET_VERDICT = FAIL_WITH_EXACT_DIFFERENCES_REPORTED
```

Una ausencia que después se considere legítima no puede desaparecer
silenciosamente del informe.

## 8. Código y contratos futuros

El código no debe vivir en `01_foundations`:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\
    audit_core_market_raw_alignment.py
    finalize_core_market_raw_alignment.py
    run_core_market_raw_alignment.ps1
    monitor_core_market_raw_alignment.ps1
    README.md

C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\core_market_raw_alignment_audit_v0_1.yaml

C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests\core_market_raw_alignment_audit\
```

Contratos institucionales, cuando la implementación sea estable:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\core_market_raw_alignment_audit\
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\core_market_raw_alignment_audit\
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\core_market_raw_alignment_audit\
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\inspection_dossiers\core_market_raw_alignment_audit\
```

Este handoff no afirma que esos programas o contratos ya existan.

## 9. Artefactos generados

Los resultados runtime y pesados no se guardan en Git.

```text
C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\<run_id>\
```

Convención inicial:

```text
YYYYMMDD_core_market_raw_alignment_audit_v0_1
```

Topología:

```text
<run_id>\
├── 00_control\
│   ├── pre_manifest.json
│   ├── pids.json
│   ├── heartbeat.json
│   ├── heartbeat.jsonl
│   ├── audit.log
│   ├── monitor_command.txt
│   └── run_state.sqlite
├── 01_inventory\
│   ├── ohlcv_daily_inventory.parquet
│   ├── ohlcv_1m_inventory.parquet
│   ├── quotes_inventory.parquet
│   └── trades_inventory.parquet
├── 02_ticker_coverage\
│   ├── ohlcv_daily_ticker_dates.parquet
│   ├── ohlcv_1m_ticker_dates.parquet
│   ├── quotes_ticker_dates.parquet
│   ├── trades_ticker_dates.parquet
│   └── ticker_family_coverage.parquet
├── 03_differences\
│   ├── ticker_set_differences.csv
│   ├── ticker_window_differences.csv
│   ├── ticker_date_differences.parquet
│   ├── zero_byte_parquets.csv
│   ├── unreadable_parquets.csv
│   ├── empty_parquets.csv
│   └── unreadable_schemas.csv
└── 04_closeout\
    ├── audit_summary.json
    ├── audit_summary.csv
    ├── CORE_MARKET_RAW_ALIGNMENT_AUDIT.md
    └── final_manifest.json
```

No se crea un árbol junto a los RAW de `G:` y nunca se modifica un archivo de
las cuatro raíces fuente.

## 10. Paralelismo y hardware

Contrato obligatorio:

```text
C:\TSIS_Data\TSIS_HARDWARE_OPTIMIZATION_PROMPT.md
```

Contexto:

```text
CPU:  Ryzen 7 5800X, 8 cores / 16 threads
RAM:  32 GB
C:    NVMe para estado, checkpoints y outputs
G:    HDD HFS+ compartido, fuente pesada y solo lectura
GPU:  sin utilidad para esta tarea
```

Las cuatro familias pueden lanzarse al mismo tiempo, con este perfil inicial:

```text
one sequential reader per family
four family workers total
bounded queues
no recursive rescans after inventory freeze
no oversubscription
```

Las cuatro lecturas compiten por el mismo disco físico `G:`. El probe debe
comparar el perfil concurrente con uno o dos workers si la cola de disco se
dispara. El paralelismo se ajusta por medición, no por el máximo de hilos.

## 11. Gate previo obligatorio

Antes del full run debe ejecutarse un probe production-equivalent con el mismo:

- runner;
- config y schemas;
- wrapper;
- ledger/checkpoint;
- agregador;
- certifier terminal;
- path lógico del `final_manifest`.

El probe debe incluir una muestra de cada familia, un ticker común, un
deslistado si existe, una partición anual o mensual, un Parquet diario, una
diferencia controlada/fixture de fallo y una interrupción con `resume` sin
duplicar resultados.

El full run no queda autorizado hasta que el probe produzca `PASS` y un humano
apruebe expresamente el comando largo.

## 12. Operación larga

Toda ejecución completa debe obedecer:

```text
C:\TSIS_Data\LONG_RUNNING_OPERATIONS_CONTRACT.md
```

Antes de arrancar deben existir:

```text
pre-manifest
run_id
config hash
source roots
universe hash
PID o process identity
heartbeat vivo
log vivo
monitor separado
checkpoint/resume
final manifest path
```

El agente prepara y verifica el comando, pero el primer lanzamiento largo
corresponde al humano. El monitor debe mostrar familia, archivos descubiertos y
procesados, errores, tickers/ticker-fechas emitidos, velocidad, RAM, cola de
disco, espacio libre y edad del heartbeat.

## 13. Ruta para el próximo agente

```text
1. Leer AGENTS.md y toda la lectura obligatoria de TSIS.
2. Leer este handoff completo.
3. Inspeccionar sin modificar la topología real de las cuatro raíces.
4. Verificar y hashear el universo de 4.824 tickers.
5. Documentar la regla ticker/fecha de cada familia.
6. Implementar código, config, tests, wrapper, monitor y certifier.
7. Ejecutar un probe production-equivalent acotado.
8. Auditar el probe y cerrar su manifest.
9. Presentar al humano los comandos exactos de full run y monitor.
10. No lanzar el full run sin autorización humana expresa.
11. Producir diferencias exactas y aplicar literalmente el gate.
12. Crear el readout institucional y cerrar Graphify según AGENTS.md.
```

## 14. Estado actual

```text
handoff design                 = CREATED
runner implementation          = NOT_STARTED_BY_THIS_HANDOFF
production-equivalent probe    = NOT_RUN
full audit                     = NOT_AUTHORIZED
raw mutation                   = PROHIBITED
new data download              = OUT_OF_SCOPE
```

Este documento fija el recorrido y las rutas. No certifica ninguna familia ni
sustituye futuros manifests, validators o readouts.

## 15. Lectura obligatoria relacionada

```text
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\TSIS_HARDWARE_OPTIMIZATION_PROMPT.md
C:\TSIS_Data\PATH_MIGRATION_2026_07_22.md
C:\TSIS_Data\PATH_NAMING_POLICY.md
C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
C:\TSIS_Data\PROJECT_RULES.md
C:\TSIS_Data\VERSIONING_STANDARDS.md
C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
C:\TSIS_Data\LONG_RUNNING_OPERATIONS_CONTRACT.md
C:\TSIS_Data\00_CTO\TSIS_LAB_ARCHITECTURE_v3.md
C:\TSIS_Data\03_TSIS_Lab\README.md
G:\TSIS\data\README.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\LOCAL_RULES.md
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\LOCAL_RULES.md
```
