# Core Market RAW Alignment Audit Handoff v0.2

Fecha: 2026-08-21  
Estado: `IMPLEMENTED_PROBE_VERIFIED_FULL_NOT_AUTHORIZED`  
Owner: `01_TSIS_DATA_FOUNDATION / 01_foundations`  
Severidad semántica: `HIGH`

## 1. Objetivo exacto

Auditar, sin modificar ni leer los valores económicos fila por fila, si estas
cuatro familias RAW contienen los mismos miembros del universo LT1B y el mismo
conjunto exacto de fechas observadas por ticker:

```text
G:\TSIS\data\ohlcv_daily
G:\TSIS\data\ohlcv_1m
G:\TSIS\data\quotes_
G:\TSIS\data\trades_ticks_prod_2005_2026
```

Scope global:

```text
2005-01-01 <= observed_date <= 2026-08-20
```

No se usan `first_seen_date` ni `last_observed_date` como ventanas que reduzcan
la auditoría. Massive o el RAW pueden carecer legítimamente de observaciones
fuera de la vida cotizada de un símbolo, pero toda diferencia física se conserva
y se informa; no se inventan fechas esperadas entre los extremos.

## 2. Autoridad del universo

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet
```

Preflight certificado por el auditor:

```text
rows                         = 4824
unique_tickers               = 4824
null_tickers                 = 0
duplicate_tickers            = 0
literal_NA_count             = 1
SHA256                       = 7B7D056785AAE7E3E097219DC5F24C25E2FE193EB28C139354C4D9F8AFF88468
```

El audit es `target-scoped`: un ticker fuera de esos 4.824 se registra como
contexto no bloqueante. Un ticker objetivo ausente de cualquier familia sí es
bloqueante. `NA` y `NAN` se tratan como símbolos literales distintos.

## 3. Qué comprueba cada Parquet

Solo se realizan comprobaciones físicas mínimas:

```text
file_exists
file_size_bytes > 0
PAR1 header/footer
ParquetFile openable
metadata readable and metadata_num_rows > 0
schema readable
minimum required columns present
```

También se registra el schema completo y su fingerprint para trazabilidad. No
se auditan precios, volumen, spreads, tamaños, condiciones, duplicados de
eventos, monotonicidad ni contenido RTH/extendido.

La fecha se obtiene de forma mínima:

```text
ohlcv_daily   -> proyección exclusiva de la columna date; archivo anual
ohlcv_1m      -> proyección exclusiva de la columna date; archivo mensual
quotes_       -> path year=/month=/day=; archivo diario
trades        -> path year=/month=/day=YYYY-MM-DD; archivo diario
```

## 4. Invariantes de comparación

Para cada ticker objetivo se comparan:

```text
directory present in all four families
at least one non-empty/openable Parquet in all four families
at least one observed date in all four families
first observed date equal
last observed date equal
exact (ticker, observed_date) set equal
```

Un ticker vacío en las cuatro familias no cuenta como igualdad. El cierre full
también exige que cada familia alcance `2026-08-20`; esta regla no bloquea un
probe de tres tickers, pero sí el universo completo.

## 5. Arquitectura ejecutable

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\configs\core_market_raw_alignment_audit_v0_1.yaml
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests\core_market_raw_alignment_audit\
```

El perfil de producción usa un proceso secuencial por familia, cuatro procesos
como máximo, porque las cuatro raíces compiten por el mismo disco físico `G:`.
Cada tarea atómica es `family × ticker`.

El estado autoritativo vive en SQLite:

```text
run_state.sqlite
journal_mode = WAL
synchronous = FULL
```

Cada tarea escribe inventario y fechas en staging privado y publica un manifest
con hashes. `-Resume` adopta una tarea solo si coinciden el contrato del run y
los hashes de todos sus artefactos. Un artefacto corrupto se invalida y se
reconstruye; los demás no se repiten. El finalizador se ejecuta como proceso
separado mientras el padre mantiene heartbeat y se niega a cerrar si falta una
tarea o un manifest válido.

## 6. Outputs

```text
C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\<run_id>\
├── 00_control\
│   ├── pre_manifest.json
│   ├── run_state.sqlite
│   ├── pids.json
│   ├── heartbeat.json
│   ├── heartbeat.jsonl
│   ├── audit.log
│   └── task_results\
├── 01_inventory\
├── 02_ticker_coverage\
├── 03_differences\
└── 04_closeout\
    ├── audit_summary.json
    ├── audit_summary.csv
    ├── CORE_MARKET_RAW_ALIGNMENT_AUDIT.md
    └── final_manifest.json
```

Los RAW de `G:` son estrictamente read-only.

## 7. Probe production-equivalent autoritativo

```text
run_id = 20260821_core_market_raw_alignment_probe_v0_3
tickers = AACT, NA, MMMW
tasks = 12/12 committed
source_parquets = 2259
ticker_date_rows = 6790
Parquet errors = 0
.partial files after close = 0
resume replay = adopted 12, reset 0
maximum task attempt = 1
technical_status = COMPLETED
dataset_verdict = PROBE_COMPLETED_WITH_DIFFERENCES
```

Artefactos de cierre:

```text
C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_probe_v0_3\04_closeout\final_manifest.json
SHA256 = 9D7C878022D5FB964A47EBD0E70A3FFB1150127DE33B6FE0BC0207E76B6E5CE9

C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_probe_v0_3\04_closeout\audit_summary.json
SHA256 = 947FBA30A78158FE715C498AA3FEA9DA5A70AA42FD1D73DE2F55C5AC4B879C39
```

El manifest contiene 22 artefactos hasheados. La prueba automatizada adicional
corrompe deliberadamente un shard y verifica que `resume` reconstruye solo ese
shard, sin duplicar los válidos.

## 8. Qué reveló el preflight/probe

Cobertura de directorios contra los 4.824 tickers objetivo:

| Familia | Tickers objetivo ausentes | Tickers fuera del target |
|---|---:|---:|
| `ohlcv_daily` | 0 | 7.670 |
| `ohlcv_1m` | 0 | 7.344 |
| `quotes_` | 2 (`MMMW`, `NA`) | 385 |
| `trades_ticks_prod_2005_2026` | 454 | 1 (`NAN`) |

Estas cifras proceden del roster físico de carpetas. No sustituyen el full scan
Parquet, pero impiden afirmar de antemano que las cuatro familias tienen los
mismos 4.824 tickers.

En la muestra, los 2.259 Parquet son físicamente válidos, pero los tres tickers
tienen diferencias de fechas. `AACT` comparte extremos entre las cuatro
familias y aun así presenta 12 diferencias interiores, demostrando por qué no
basta comparar solo `min/max`.

## 9. Gate del full run

El full run queda preparado, no ejecutado. Solo puede cerrarse `PASS` si:

```text
expected_universe_members = 4824
all 19296 family × ticker tasks committed
missing expected tickers any family = 0
selected ticker-family pairs without directories/parquets/dates = 0
Parquets with physical/schema errors = 0
tickers with window mismatch = 0
tickers with exact date-set mismatch = 0
all four families reach 2026-08-20
final artifact hash failures = 0
```

Los extras fuera del universo no bloquean. Cualquier ausencia o diferencia del
target permanece en los outputs exactos aunque posteriormente se clasifique
como legítima.

Comando que requiere autorización humana explícita:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\run_core_market_raw_alignment.ps1" -Mode Full -RunId "20260821_core_market_raw_alignment_audit_v0_1" -HumanAuthorizedFull
```

Monitor:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\monitor_core_market_raw_alignment.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_audit_v0_1" -Watch
```

Tras una interrupción se repite el primer comando con `-Resume`. Nunca se
reanuda desde un timestamp ni se modifica un RAW.

## 10. Estado final del handoff

```text
implementation                = COMPLETE
focused_tests                 = PASS 4/4
production-equivalent probe   = COMPLETED
resume replay                 = PASS
source mutation               = NONE
full audit                    = NOT_AUTHORIZED
dataset alignment             = NOT_CERTIFIED
new data download             = OUT_OF_SCOPE
```

Este documento autoriza la lectura del diseño y la ejecución del probe ya
cerrado. No certifica las cuatro familias: esa conclusión solo puede proceder
del manifest terminal del full run.
