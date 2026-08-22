# Quotes Worker Acceleration Runbook v0.1

Fecha: 2026-08-21  
Run: `20260821_core_market_raw_alignment_audit_v0_1`  
Estado: `ACTIVE_TWO_QUOTES_WORKERS_AUTO_SCALE_TO_THREE`  
Owner: `01_TSIS_DATA_FOUNDATION / 01_foundations`

## Objetivo

Acelerar exclusivamente la familia `quotes_` del full scan ya autorizado sin
reiniciar el padre y sin parar los workers existentes de `ohlcv_1m` o Trades.
Los cuatro roots RAW de `G:` permanecen estrictamente read-only.

Topología autorizada:

```text
mientras ohlcv_1m siga pendiente:
    ohlcv_1m = 1 worker original
    Trades   = 1 worker original
    Quotes   = 2 workers acelerados

cuando ohlcv_1m committed = 4824:
    ohlcv_1m = 0 workers
    Trades   = 1 worker original
    Quotes   = 3 workers acelerados
```

No se detiene Trades. No se detiene `ohlcv_1m`. El tercer worker de Quotes se
crea solo después de que el ledger registre las 4.824 tareas 1m como
`committed`.

## Motivo técnico

El worker original recorre una familia secuencialmente y su transición a
`running` no constituye una reclamación exclusiva utilizable por copias
concurrentes. Lanzar dos runners originales sobre Quotes podría procesar el
mismo ticker y publicar sobre los mismos artefactos.

El acelerador usa una transacción SQLite `BEGIN IMMEDIATE` para seleccionar y
actualizar una única fila `quotes_` que todavía esté `pending`. El commit exige
que coincidan:

```text
family = quotes_
ticker
status = running
worker_pid
attempt
```

Cada worker conserva el auditor original, el schema, el alcance, los paths de
tarea, las escrituras atómicas y el `run_contract_sha256` del full run.

## Intervención ejecutada

Antes del reemplazo se verificó desde el ledger y la tabla de procesos:

```text
parent PID          = 263664
ohlcv_1m PID        = 266916  [PROTECTED]
Trades PID          = 13032   [PROTECTED]
Quotes original PID = 266568  [ONLY REPLACEMENT TARGET]
```

El PID `266568` fue el único proceso detenido. La tarea Quotes que poseía en el
instante real del corte, `AFMD`, volvió transaccionalmente a `pending`. No se
modificó ninguna tarea de 1m ni Trades.

El acelerador quedó lanzado así:

```text
coordinator PID = 274300
Quotes worker   = 270864
Quotes worker   = 276172
```

Los PIDs son evidencia del lanzamiento inicial; el coordinador puede sustituir
un helper finalizado y creará otro PID cuando active el tercer worker.

## Pruebas previas

Suite focalizada:

```text
python -m pytest \
  tests/core_market_raw_alignment_audit/test_core_market_raw_alignment.py \
  tests/core_market_raw_alignment_audit/test_quotes_accelerator.py -q

resultado = 6/6 PASS
```

La prueba concurrente usó ocho reclamadores y 120 tickers temporales:

```text
claims total                = 120
unique tickers claimed      = 120
duplicate ticker-attempt    = 0
```

Otra prueba recuperó solo una tarea Quotes por PID y demostró que las filas
`ohlcv_1m` y Trades conservaron `status=running` y sus PIDs originales.

Primer control del ledger vivo:

```text
ORIGINAL_WORKER_TASK_RECOVERED = 1
TASK_CLAIMED                   = 9
TASK_COMMITTED                 = 7
duplicate ticker-attempt       = 0
```

## Artefactos de control

```text
C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\
  20260821_core_market_raw_alignment_audit_v0_1\00_control\quotes_accelerator\
    pre_manifest.json
    pids.json
    heartbeat.json
    heartbeat.jsonl
    accelerator.log
    worker_<pid>.log
    stdout.log
    stderr.log
    final_manifest.json  # solo al terminar o fallar
```

La tabla append-only `quote_accelerator_events` vive dentro del
`run_state.sqlite` autoritativo y registra claims, commits, reintentos y la
recuperación del worker reemplazado.

## Monitores

Run completo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\monitor_core_market_raw_alignment.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_audit_v0_1" -Watch
```

Acelerador Quotes:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\core_market_raw_alignment_audit\monitor_quotes_accelerator.ps1" -RunRoot "C:\TSIS_Data\runs\data_ops\core_market_raw_alignment_audit\20260821_core_market_raw_alignment_audit_v0_1" -Watch
```

El monitor principal obtiene las tareas activas del ledger y por ello muestra
los dos PIDs Quotes aunque el `pids.json` original del padre todavía enumere el
worker reemplazado.

## Reanudación

Si solo cae el acelerador, no se debe reiniciar todo el full run ni detener 1m
o Trades. Primero se identifican las tareas `quotes_` en `running` cuyos PIDs
ya no existen, se devuelven de forma exacta a `pending` y se vuelve a lanzar un
coordinador bajo manifest nuevo. Los commits válidos se conservan.

Si cae también el padre, aplica el `-Resume` del auditor completo. Los manifests
válidos se adoptan por hash. Nunca se modifica ni se reescribe un RAW de `G:`.

## Gate terminal

La aceleración no certifica los datos por sí sola. El full run solo puede
cerrar cuando el ledger original alcance 19.296/19.296 tareas comprometidas y
el finalizador produzca el manifest y las diferencias exactas de las cuatro
familias.
