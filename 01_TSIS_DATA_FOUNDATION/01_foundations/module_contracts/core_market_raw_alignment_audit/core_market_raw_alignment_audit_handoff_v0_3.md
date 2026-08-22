# Core Market RAW Alignment Audit Handoff v0.3

Fecha: 2026-08-22
Estado: `FULL_SCAN_ACTIVE_SESSION_DATE_CORRECTION_REQUIRED`
Owner: `01_TSIS_DATA_FOUNDATION / 01_foundations`
Severidad semantica: `HIGH`

Este documento sustituye el estado operativo de `v0.2`. `v0.2` permanece como
evidencia historica del diseño y del probe que autorizaron el full scan.

## 1. Punto de entrada despues de una interrupcion

La autoridad institucional para entender y continuar este trabajo es este
documento:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\
core_market_raw_alignment_audit\core_market_raw_alignment_audit_handoff_v0_3.md
```

El run activo contiene una copia runtime de recuperacion:

```text
C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\
20260821_core_market_raw_alignment_audit_v0_1\00_control\
RECOVERY_HANDOFF_20260822.md
```

La copia runtime sirve para localizar esta autoridad. No sustituye este
contrato ni convierte los artefactos runtime en source of truth institucional.

## 2. Objetivo vigente

Determinar para los 4.824 tickers objetivo, entre `2005-01-01` y
`2026-08-20`, la presencia fisica y la cobertura temporal de:

```text
G:\TSIS\data\ohlcv_daily
G:\TSIS\data\ohlcv_1m
G:\TSIS\data\quotes_
G:\TSIS\data\trades_ticks_prod_2005_2026
```

Los cuatro roots de `G:` son estrictamente read-only. La auditoria no autoriza
reparaciones ni descargas.

El resultado final debe separar:

```text
presencia por familia, ticker y fecha de sesion ET
rollover UTC -> America/New_York
shard mensual ausente
fecha ausente dentro de un shard existente
cola temporal incompleta
diferencia legitima de producto
ausencia que requiere reconciliacion contra Massive
```

## 3. Estado exacto persistido del full scan

Run:

```text
run_id = 20260821_core_market_raw_alignment_audit_v0_1
run_root = C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\
           20260821_core_market_raw_alignment_audit_v0_1
ledger = <run_root>\00_control\run_state.sqlite
```

Snapshot del heartbeat a `2026-08-22T06:38:35.964167Z`:

```text
status                    = running
stage                     = family_ticker_audit
total tasks               = 19.296
committed                 = 14.610
running                   = 7
pending                   = 4.679
committed error files     = 0
output free space         = 402,719 GB

ohlcv_daily committed     = 4.824 / 4.824
ohlcv_1m committed        = 4.824 / 4.824
quotes committed          = 3.942 / 4.824
quotes running            = 6
trades committed          = 1.020 / 4.824
trades running            = 1
```

Los conteos de Quotes pueden haber avanzado despues de este snapshot. El estado
autoritativo actual siempre se obtiene de `run_state.sqlite` y de
`00_control/heartbeat.json`, no de estas cifras congeladas.

Topologia activa en el snapshot:

```text
Daily       = terminado
1m          = terminado
Quotes      = 6 workers transaccionales
Trades      = 1 worker original
```

El parent, el acelerador inicial de Quotes y el sidecar de scale-out mantienen
heartbeats separados. Sus PIDs son efimeros y no deben reutilizarse despues de
un reinicio.

## 4. Que esta certificado y que no

Resultados cerrados por familia:

```text
ohlcv_daily
    target tasks committed = 4.824 / 4.824
    Parquets                = 44.423
    ticker-date rows        = 9.290.966
    physical/schema errors  = 0

ohlcv_1m
    target tasks committed = 4.824 / 4.824
    Parquets                = 466.945
    ticker-date rows raw    = 9.354.195
    physical/schema errors  = 0
```

Esto permite afirmar:

```text
target ticker presence     = PASS para Daily y 1m
minimum physical integrity = PASS para Daily y 1m
minimum required schema    = PASS para Daily y 1m
session-date alignment     = NOT_CERTIFIED
provider completeness      = NOT_CERTIFIED
```

Quotes y Trades siguen activos. El full run no tiene todavia
`04_closeout/final_manifest.json` terminal.

## 5. Correccion semantica obligatoria UTC frente a ET

El auditor `v0.1` configura:

```text
ohlcv_daily.date_strategy = column(date)
ohlcv_1m.date_strategy    = column(date)
```

Pero esas columnas no representan el mismo reloj:

```text
ohlcv_daily.date = fecha de sesion de mercado
ohlcv_1m.date    = fecha calendario UTC coherente con ts_utc
```

El after-hours del viernes puede cruzar medianoche UTC:

```text
viernes 19:04 America/New_York
= sabado 00:04 UTC
```

Casos comprobados directamente en los RAW:

```text
RAD   raw date 2005-02-12 -> viernes 2005-02-11 ET
YHOO  raw date 2006-11-04 -> viernes 2006-11-03 ET
AAME  raw date 2021-02-06 -> viernes 2021-02-05 ET
FCEL  raw date 2026-01-31 -> viernes 2026-01-30 ET
ALTS  raw date 2026-03-07 -> viernes 2026-03-06 ET
```

Consecuencia:

```text
4.640 tickers con raw date-set distinto
79.727 ticker-date solo en 1m raw
16.498 ticker-date solo en Daily
```

son cifras validas de desigualdad entre columnas crudas, pero no cuantifican
huecos reales de sesiones. No deben usarse para decidir reparaciones.

Cuando el full `v0.1` finalice:

```text
physical/schema outputs = reutilizables
raw date comparison     = provisional para 1m vs Daily
session alignment       = requiere recomputacion v0.2
```

## 6. Huecos reales ya confirmados

La correccion UTC/ET no explica todos los descuadres.

### 6.1 FCEL: shards mensuales 1m ausentes

No existen los shards 1m de febrero y marzo de 2026. Daily contiene 24
sesiones entre `2026-02-02` y `2026-03-06`. La sesion `2026-02-02`, por ejemplo,
tiene en Daily:

```text
volume       = 2.763.084
transactions = 24.058
```

Clasificacion provisional:

```text
MISSING_MONTH_SHARD_CONFIRMED
```

### 6.2 DJCO: fecha ausente dentro de un shard existente

El shard 1m de marzo de 2005 existe, pero no contiene `2005-03-09`. Daily si
contiene una barra para esa fecha:

```text
OHLC         = 44,99
volume       = 400
transactions = 1
```

Clasificacion provisional:

```text
MISSING_INTRAMONTH_SESSION_OR_PROVIDER_AGGREGATION_DIFFERENCE
```

Debe reconciliarse contra Massive antes de declarar perdida fisica: una
diferencia entre agregados del proveedor no se convertira silenciosamente en
un error de descarga.

### 6.3 Colas heterogeneas

Daily termina globalmente en `2026-03-06`, coherente con el documento original
que declaraba 2026 parcial e incremental. Algunos tickers 1m llegan hasta
`2026-03-27`, mientras FCEL termina en enero de 2026. No existe un unico cutoff
homogeneo para 1m.

Clasificacion provisional:

```text
HETEROGENEOUS_INCREMENTAL_TAIL_CONFIRMED
```

## 7. Recuperacion exacta despues de apagado o interrupcion

### 7.1 Preflight

No borrar `.partial`, no editar SQLite y no relanzar coordinadores a ciegas.
Primero leer:

```text
<run_root>\00_control\heartbeat.json
<run_root>\00_control\pids.json
<run_root>\00_control\audit.log
<run_root>\00_control\quotes_accelerator\heartbeat.json
<run_root>\00_control\quotes_scaleout_6_workers\heartbeat.json
```

Comprobar despues los procesos vivos. Los PIDs guardados antes del apagado son
solo evidencia historica.

### 7.2 Si todo el run cayo

Reanudar el auditor principal:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\run_core_market_raw_alignment.ps1" -Mode Full -RunId "20260821_core_market_raw_alignment_audit_v0_1" -HumanAuthorizedFull -Resume
```

La reanudacion adopta solo tareas committed cuyos manifests, hashes y contrato
coincidan. Las tareas `running` abandonadas se recuperan; no se vuelve a leer
una tarea comprometida valida.

Monitor principal:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\monitor_core_market_raw_alignment.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_audit_v0_1" -Watch
```

### 7.3 Restaurar seis workers de Quotes solo si siguen pendientes

Despues de que el parent reanudado tenga heartbeat fresco, obtener de
`heartbeat.json` el PID del unico worker original con `family=quotes_`. Nunca
usar el PID antiguo documentado.

Sustituir solo ese worker por el pool transaccional:

```powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\accelerate_quotes_workers.py" --run-root "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_audit_v0_1" --replace-worker-pid <PID_QUOTES_ACTUAL> --initial-workers 2 --scale-workers 3 --heartbeat-seconds 10 --max-attempts 3 --human-authorized
```

Cuando ese coordinador este vivo, ampliar de tres a seis:

```powershell
python "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\scale_out_quotes_workers.py" --run-root "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_audit_v0_1" --target-total-workers 6 --heartbeat-seconds 10 --max-attempts 3 --human-authorized
```

No lanzar esos sidecars si Quotes ya esta `4.824/4.824`. No ejecutar dos
coordinadores iguales simultaneamente. Trades permanece con un worker.

## 8. Estrategia posterior al full scan actual

No lanzar otro barrido completo sobre `G:` mientras Quotes y Trades sigan
leyendo el disco. Mientras tanto solo se prepara codigo y documentacion en
`C:`.

Secuencia obligatoria:

```text
1. terminar Quotes y Trades del run v0.1
2. conservar su final manifest y todos los shards committed
3. implementar la correccion versionada v0.2
4. derivar ohlcv_1m.session_date_et desde ts_utc
   usando America/New_York, nunca un offset UTC fijo
5. reutilizar Daily/Quotes/Trades ticker-date del run cerrado
6. ejecutar probe production-equivalent con casos UTC y huecos reales
7. auditar valores y clasificaciones del probe
8. obtener gate humano PASS
9. ejecutar la recomputacion completa de 1m
10. producir el ledger final de huecos por familia/ticker/fecha
```

El probe minimo debe incluir:

```text
RAD, YHOO, AAME, FCEL, ALTS, DJCO
```

Y debe demostrar:

```text
UTC rollover reclasificado correctamente
FCEL detectado como missing monthly shard
DJCO conservado como vendor-check candidate
schema y hashes estables
resume sin duplicados
ninguna escritura en G:
```

## 9. Outputs exigidos de la correccion v0.2

Nuevo run root, separado del `v0.1`:

```text
C:\TSIS_Data\runs\data_ops\core_market_session_coverage_audit\<run_id>\
```

Artefactos terminales minimos:

```text
ohlcv_1m_session_dates_et.parquet
ticker_family_session_presence.parquet
family_gap_ledger.parquet
ticker_family_windows.parquet
gap_summary_by_family.csv
gap_summary_by_class.csv
audit_summary.json
final_manifest.json
CORE_MARKET_SESSION_COVERAGE_AUDIT.md
```

Cada fila del gap ledger debe identificar:

```text
ticker
session_date_et
missing_family
present_families
gap_class
source_shard_expected
source_shard_exists
requires_vendor_reconciliation
evidence_reference
```

Clases minimas:

```text
UTC_DATE_ROLLOVER_ONLY
MISSING_MONTH_SHARD
MISSING_INTRAMONTH_SESSION
DOWNLOAD_TAIL_MISSING
POSSIBLE_TICKER_REUSE_OR_IDENTITY_INTERVAL
PRODUCT_SEMANTIC_DIFFERENCE
VENDOR_RECONCILIATION_REQUIRED
```

## 10. Condicion de cierre

No declarar que conocemos exactamente los huecos hasta que existan:

```text
4.824 / 4.824 tickers procesados
session_date_et corregida para todo 1m
Quotes y Trades terminales o explicitamente excluidos del veredicto
0 tareas failed/running/unresolved
0 schema drift sin resolver
gap ledger completo y hasheado
resumen exacto por familia, ticker, fecha y clase
final manifest terminal
```

El objetivo no es forzar igualdad artificial entre productos. El objetivo es
separar con evidencia:

```text
ausencia local observada
perdida real de descarga
ausencia legitima del producto
caso que Massive debe confirmar
```

## 11. Documentos y artefactos que debe leer el siguiente agente

Solo son necesarios:

```text
1. este handoff v0.3
2. scripts/core_market_raw_alignment_audit/README.md
3. quotes_worker_acceleration_runbook_v0_1.md
4. <run_root>/00_control/pre_manifest.json
5. <run_root>/00_control/heartbeat.json
6. <run_root>/00_control/run_state.sqlite
7. <run_root>/04_closeout/final_manifest.json, cuando exista
```

No comenzar leyendo toda la biblioteca de certificacion. Estos artefactos
contienen el estado, la recuperacion y el siguiente trabajo autorizado.
