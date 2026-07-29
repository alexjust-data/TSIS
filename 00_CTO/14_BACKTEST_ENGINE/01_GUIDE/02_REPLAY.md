# 02 REPLAY

Estado: TSIS_VALIDATED_CONTRACT_ACOTADO
Fecha: 2026-07-28
Alcance: replay historico minimo para `BACKTEST_VERTICAL_SLICE_V0_1`.

Este documento define solo lo que ya fue necesario para convertir datos aprobados por `RunPreflight` en eventos historicos legalmente observables. No define todavia estrategia, ordenes, fills ni accounting.

## Menu

- [1. Proposito](#1-proposito)
- [2. Regla Ejecutable](#2-regla-ejecutable)
- [3. Decisiones TSIS V0.1](#3-decisiones-tsis-v01)
- [4. Contratos Minimos](#4-contratos-minimos)
- [5. Gates Probados](#5-gates-probados)
- [6. Evidencia](#6-evidencia)
- [7. Fuera De Alcance](#7-fuera-de-alcance)
- [8. Siguiente Paso](#8-siguiente-paso)

## 1. Proposito

`REPLAY` responde una pregunta concreta:

```text
En que orden y en que instante puede observar el motor cada barra historica aprobada?
```

El objetivo no es calcular edge. El objetivo es cerrar la semantica temporal que usaran despues estrategia, ordenes y accounting.

## 2. Regla Ejecutable

`REPLAY` solo puede consumir un `data_preflight_report.json` con:

```text
preflight_status = PREFLIGHT_PASS
physical_inspection_status = PHYSICAL_INSPECTION_PASS
source_partitions_or_files_consumed declarado
snapshot_or_content_hashes declarado
```

Si el archivo fuente cambio respecto al hash del preflight, replay falla cerrado.

## 3. Decisiones TSIS V0.1

### REPLAY-DEC-001: Preflight PASS obligatorio

No existe replay desde un path suelto. El input es el reporte aprobado por `RunPreflight`.

### REPLAY-DEC-002: Orden determinista

Los eventos se ordenan por:

```text
available_at
event_priority: GAP antes de BAR
ticker
```

### REPLAY-DEC-003: Semantica temporal de barra

Para barra 1m:

```text
ts_start = timestamp fisico de inicio de minuto
ts_end = ts_start + 1 minuto
available_at = ts_end
```

La barra no es observable antes de `available_at`.

### REPLAY-DEC-004: Gaps sin imputacion

Un minuto interior ausente produce:

```text
ReplayGapEvent(reason = OBSERVED_MINUTE_GAP)
```

No produce una barra sintetica.

### REPLAY-DEC-005: Campos derivados de proveedor no consumibles

El loader no pide ni propaga `vw` ni indicadores calculados por proveedor. El evento solo transporta OHLCV y lineage minimo.

## 4. Contratos Minimos

Implementacion:

```text
src/tsis_backtest/replay/contracts.py
src/tsis_backtest/replay/historical_feed.py
```

Contratos:

```text
HistoricalReplayFeed
ReplayBarEvent
ReplayGapEvent
ReplayRunSummary
ReplayContractError
```

Columnas requeridas por replay:

```text
ticker
ts_utc
o
h
l
c
v
```

Lineage opcional si existe:

```text
dataset_id
build_run_id
quote_guarded_repair_applied
repair_lookup_state
source_quote_guarded_repair_manifest
source_raw_path
```

## 5. Gates Probados

```text
REPLAY_G1_PREFLIGHT_PASS_REQUIRED
REPLAY_G2_PHYSICAL_INSPECTION_PASS_REQUIRED
REPLAY_G3_SOURCE_HASH_VERIFIED
REPLAY_G4_DETERMINISTIC_ORDER
REPLAY_G5_AVAILABLE_AT_LEGALITY
REPLAY_G6_GAP_EVENT_WITHOUT_IMPUTATION
REPLAY_G7_VENDOR_VW_NOT_PROPAGATED
REPLAY_G8_REAL_FIXTURE_SMOKE
```

## 6. Evidencia

Suite:

```text
$env:PYTHONPATH='src'; python -m unittest discover -s tests
# Ran 43 tests OK
```

Smoke real acotado:

```text
source_preflight = run_preflight_real_fixture_2026_01_05_qg5_v0_2
replay_run = replay_real_fixture_2026_01_05_qg5_v0_1
event_count = 1950
bar_count = 1828
gap_count = 122
first_available_at = 2026-01-05T14:31:00+00:00
last_available_at = 2026-01-05T21:00:00+00:00
```

Outputs:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/replay_real_fixture_2026_01_05_qg5_v0_1/replay_summary.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/replay_real_fixture_2026_01_05_qg5_v0_1/replay_event_sample.json
```

## 7. Fuera De Alcance

```text
strategy decisions
order intents
orders
fills
positions
portfolio accounting
execution realism
full 2005-2026 replay
```

## 8. Siguiente Paso

Siguiente incremento minimo:

```text
Decision/Order/Fill/Position mecanico
  -> una politica programada de apertura/cierre
  -> usar solo eventos de replay aprobados
  -> fill proxy mecanico declarado
  -> posicion y PnL derivado de fills
  -> sin afirmar fill realism ni edge
```
