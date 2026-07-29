# AGENT - TSIS Backtest Engine

Status: LIVE_HANDOFF
Last updated: 2026-07-28
Scope: operational handoff for agents working on `14_BACKTEST_ENGINE`.

Este archivo existe para que otra sesion pueda continuar el trabajo si se corta la ejecucion, cambia el agente o se pierde contexto.

La regla principal es:

```text
construir el backtester primero
mantener la guia como registro vivo de decisiones
actualizar este AGENT.md cada vez que se cierre un paso operativo
```

## 1. Objetivo Actual

Estamos construyendo un backtester propio en Python para small caps dentro de TSIS.

No estamos escribiendo primero un libro completo. La guia se actualiza solo cuando una decision ayuda a implementar, probar o auditar el motor.

El objetivo inmediato es preparar el primer vertical slice:

```text
BACKTEST_VERTICAL_SLICE_V0_1
```

Primer foco cerrado:

```text
01_DATA
  -> RunPreflight
  -> RealDataInspector
  -> datos reales acotados inspeccionados
  -> universo resoluble
  -> price views declaradas
  -> semantica temporal legal
  -> manifests reproducibles
```

Segundo foco cerrado:

```text
02_REPLAY / event-loop minimo
  -> consume solo datos aprobados por RunPreflight
  -> emite eventos/barras en orden determinista
  -> respeta available_at
  -> emite gaps sin imputacion
```

Tercer foco cerrado:

```text
recorrido mecanico Decision/Order/Fill/Position
  -> consume solo eventos de HistoricalReplayFeed
  -> crea order intent, order, fill, position y PnL bruto
  -> mantiene fill proxy declarado como mecanico
```

Cuarto foco cerrado:

```text
CostModel / cash ledger / net PnL minimo
  -> costes configurables
  -> PnL neto
  -> cash ledger derivado de fills y costes
```

Foco siguiente:

```text
elegir el proximo incremento acotado:
  A. varios simbolos del fixture
  B. contrato de execution semantics/cost realism
  C. manifest unico del run completo
```
## 2. Lectura Obligatoria Al Entrar

Leer en este orden:

```text
1. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/README.md
2. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/LOCAL_RULES
3. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/CHANGELOG.md
4. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/00_CTO/00_como_trabajamos.md
5. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/README.md
6. C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/01_GUIDE/01_DATA.md
```

Si se trabaja con datos intradia, leer tambien:

```text
7. G:/TSIS/data/README.md
8. C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
9. C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
10. C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/README.md
11. C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/_validation_runs/qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z/final_manifest_validation.json
```

## 3. Fuentes De Conocimiento

SersanSistemas vive ahora bajo:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/00_CTO/00_SERSANS_SISTEMAS
```

La biblioteca procesada vive bajo:

```text
C:/TSIS_Data/00_CTO/99_REFERENCE_LIBRARY/00_BIBLIOTECA/_processed
```

Uso correcto:

```text
Sersan = fuente practica y experimental
libros = contraste tecnico/cientifico
TSIS = decision normativa propia
```

No convertir una frase de Sersan ni un libro en regla TSIS sin pasar por decision, contrato o test.

## 4. Estado Actual Consolidado

Hecho:

```text
- Workspace `14_BACKTEST_ENGINE` iniciado.
- `README.md`, `LOCAL_RULES` y `CHANGELOG.md` existen.
- `01_GUIDE/README.md` existe como indice de guia viva por capas.
- `01_GUIDE/01_DATA.md` existe como contrato definido-borrador de DATA.
- Se reviso el estado real de `quote_guarded_1m`.
- `v0_1` no debe usarse como full limpio 2005-2026.
- `v0_2_candidate` tiene validacion tecnica PASS para consumo controlado, pero no promocion institucional irrestricta.
- `RunPreflight` esta implementado.
- `RealDataInspector` esta implementado contra el fixture acotado.
- La suite del motor tiene 61 tests OK.
- El layout fisico de `v0_2_candidate` fue descubierto.
- El fixture real `TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1` paso preflight fisico, replay minimo, round trip mecanico ABAT y accounting minimo.
```

Decision DATA actual:

```text
Antes de leer datos, todo backtest debe pasar por RunPreflight.
```

## 5. Siguiente Paso Operativo

`RunPreflight`, `RealDataInspector`, `HistoricalReplayFeed`, `MechanicalEventLoop` y `AccountingEngine` ya pasaron el fixture real acotado.

Siguiente trabajo recomendado:

```text
elegir un siguiente incremento acotado
  -> varios simbolos del fixture, o
  -> primer contrato de execution semantics/cost realism, o
  -> manifest unico preflight -> replay -> mechanics -> accounting
  -> no ejecutar todavia backtest 2005-2026
```
## 6. Protocolo De Trabajo Para Cada Paso

Cada paso operativo debe seguir este flujo:

```text
1. Leer este AGENT.md.
2. Leer `LOCAL_RULES`.
3. Leer el documento de guia de la capa activa.
4. Leer solo las fuentes Sersan/libros necesarias para la decision activa.
5. Tomar una decision TSIS minima.
6. Escribir contrato, gate o test esperado.
7. Implementar o preparar el siguiente artefacto ejecutable.
8. Actualizar este AGENT.md.
9. Actualizar `CHANGELOG.md`.
10. Actualizar el .md de capa afectado.
```

## 7. Como Actualizar Este Archivo

Cuando cierres un paso, modifica estas tres zonas:

```text
- `Last updated`
- `4. Estado Actual Consolidado`
- `8. Registro Vivo De Pasos`
```

Si el paso cambia la prioridad inmediata, modifica tambien:

```text
- `5. Siguiente Paso Operativo`
```

No borres el historial salvo que el usuario lo pida. Anade una entrada nueva.

## 8. Registro Vivo De Pasos

Formato:

```text
YYYY-MM-DD - STATUS - descripcion breve - archivos tocados - siguiente accion
```

Entradas:

```text
2026-07-28 - DONE - Creado handoff operativo para agentes - AGENT.md, README.md, LOCAL_RULES, CHANGELOG.md, 01_GUIDE/README.md, 01_GUIDE/01_DATA.md - siguiente accion: localizar root de implementacion
```

## 9. No Hacer Ahora

```text
- No escribir la guia completa antes del primer vertical slice.
- No revisar exhaustivamente todos los assets Sersan antes de implementar.
- No leer todos los libros de nuevo salvo necesidad concreta.
- No promover `v0_2_candidate` como dataset institucional irrestricto.
- No implementar fills realistas small caps antes de cerrar datos, replay, ordenes y accounting mecanico.
- No mezclar signal, decision, order intent, order, fill, position y trade.
```

## 10. Definicion De Continuidad

Si una sesion se interrumpe, continuar desde aqui:

```text
1. Revisar `8. Registro Vivo De Pasos`.
2. Abrir el archivo indicado como siguiente accion.
3. Confirmar contra `CHANGELOG.md` que no hay un paso posterior.
4. Ejecutar el siguiente paso pequeno.
5. Volver a actualizar este AGENT.md.
```

## 11. Actualizacion 2026-07-28 - Root De Implementacion Resuelto

Estado nuevo:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
= ACTIVE_IMPLEMENTATION_ROOT
```

La carpeta fue vaciada y recreada limpia para empezar de nuevo sin arrastrar el intento anterior.

Siguiente accion real:

```text
implementar RunPreflight contracts y tests sinteticos en:
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

Archivos iniciales creados en el root de implementacion:

```text
README.md
AGENTS.md
LOCAL_RULES.md
CHANGELOG.md
pyproject.toml
src/
tests/
configs/
runs/
docs/
```

Registro vivo adicional:

```text
2026-07-28 - DONE - Vaciado y recreado root limpio de implementacion - C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE - siguiente accion: implementar RunPreflight contracts y tests sinteticos
```


## 12. Actualizacion 2026-07-28 - RunPreflight Sintetico Implementado

```text
DONE: micro-plan creado en 02_TSIS_BACKTEST_ENGINE/docs/00_system
DONE: contracts.py, registries.py, manifests.py y run_preflight.py creados
DONE: tests/unit/test_run_preflight.py creado
DONE: 17 tests sinteticos OK
NEXT: seleccionar TSIS_REAL_DATA_FIXTURE y ejecutar preflight real acotado
```


## 13. Actualizacion 2026-07-28 - RunPreflight Hardening

```text
RUNPREFLIGHT_CONTRACT_RESOLUTION = IMPLEMENTED
SYNTHETIC_UNIT_TESTS = PASS, 21 tests
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

Siguiente accion:

```text
implementar inspector minimo de archivos reales contra el fixture seleccionado
ejecutar preflight real acotado
mantener alcance en una sesion regular y cinco simbolos
```

## 14. Actualizacion 2026-07-28 - RunPreflight Pre-Real Guards

```text
RUNPREFLIGHT_CONTRACT_RESOLUTION = IMPLEMENTED
SYNTHETIC_UNIT_TESTS = PASS, 21 tests
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

Hecho:

```text
- `run_id` inseguro falla con INVALID_RUN_ID antes de escribir outputs.
- El output real del run queda contenido bajo output_root/run_id.
- Un dataset candidato debe tener validation_manifest registrado.
- El manifest aceptado por la politica candidata debe coincidir exactamente con el manifest registrado del dataset.
- `TSIS_REAL_DATA_FIXTURE` no puede devolver PREFLIGHT_PASS hasta que exista inspector fisico.
```

Siguiente accion:

```text
leer layout/schema real del dataset candidato
seleccionar 1 sesion regular + 3-5 simbolos LT1B
implementar inspector minimo de archivos reales
mantener REAL_DATA_PREFLIGHT = NOT_EXECUTED hasta consumir ese fixture
```

Registro vivo adicional:

```text
2026-07-28 - DONE - Endurecido RunPreflight antes de fixture real - 02_TSIS_BACKTEST_ENGINE/src, tests, README.md, AGENTS.md, CHANGELOG.md; 14_BACKTEST_ENGINE/AGENT.md, CHANGELOG.md - siguiente accion: inspector minimo de datos reales
```

## 15. Actualizacion 2026-07-28 - Physical Layout Discovery

```text
PHYSICAL_LAYOUT_DISCOVERED = PASS
TSIS_REAL_DATA_FIXTURE_SELECTED = SELECTED_NOT_INSPECTED
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

Fixture seleccionado:

```text
fixture_id = TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1
session_date = 2026-01-05
symbols = ABAT, ABEO, ABSI, ABTC, ACB
```

Evidencia:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.md
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/configs/fixtures/TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1.json
```

Siguiente accion:

```text
implementar RealDataInspector
con tests sinteticos de fallos fisicos
sin ejecutar todavia backtest ni full-universe scan
```

Registro vivo adicional:

```text
2026-07-28 - DONE - Descubierto layout fisico y seleccionado fixture real - 02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.*, configs/fixtures/TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1.json - siguiente accion: RealDataInspector
```

## 16. Actualizacion 2026-07-28 - RealDataInspector Y Preflight Real

```text
REAL_DATA_INSPECTOR_IMPLEMENTED = PASS
SYNTHETIC_UNIT_TESTS = PASS, 34 tests
REAL_DATA_INSPECTION = PASS
REAL_DATA_PREFLIGHT = PASS
BACKTEST_VERTICAL_SLICE = NOT_STARTED
```

Hecho:

```text
- Implementado RealDataInspector en 02_TSIS_BACKTEST_ENGINE.
- Integrado en RunPreflight para TSIS_REAL_DATA_FIXTURE.
- Corregida price_view_policy estructurada en fixture/discovery.
- Declarado pyarrow como dependencia explicita.
- Vendor vw/VWAP queda fuera del contrato operativo DATA: no se usa, no se calcula y no se valida.
- Ejecutado preflight real acotado sobre 2026-01-05 y 5 simbolos LT1B.
```

Evidencia:

```text
run_id = run_preflight_real_fixture_2026_01_05_qg5_v0_2
preflight_status = PREFLIGHT_PASS
physical_inspection_status = PHYSICAL_INSPECTION_PASS
rows_available = 1828
source_files_consumed = 5
content_hashes = 9
complete_tickers = ABAT, ABTC
gap_tickers = ABEO, ABSI, ACB
warning_codes = OBSERVED_MINUTE_GAP
corporate_action_exact_rows = 0
```

Outputs:

```text
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/run_preflight_real_fixture_2026_01_05_qg5_v0_2/data_manifest.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/run_preflight_real_fixture_2026_01_05_qg5_v0_2/universe_manifest.json
C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/runs/run_preflight_real_fixture_2026_01_05_qg5_v0_2/data_preflight_report.json
```

Registro vivo adicional:

```text
2026-07-28 - DONE - RealDataInspector implementado y preflight real acotado PASS - 02_TSIS_BACKTEST_ENGINE/src, tests, configs/fixtures, docs/00_system, runs/run_preflight_real_fixture_2026_01_05_qg5_v0_2 - siguiente accion: incremento minimo REPLAY/event-loop
```



## 17. Actualizacion 2026-07-28 - Sellado Auditabilidad DATA

```text
REAL_DATA_PREFLIGHT_SEALED_FOR_REPLAY = PASS
SYNTHETIC_UNIT_TESTS = PASS, 34 tests
FIXTURE_REQUEST_BINDING = ENFORCED
VALIDATION_MANIFEST_HASH = VERIFIED
NEXT_INCREMENT = REPLAY_MINIMUM
```

Hecho:

```text
- `RunDataRequest` declara `fixture_id`.
- `RealDataInspector` falla con REAL_FIXTURE_REQUEST_MISMATCH si request y fixture no coinciden exactamente en fixture_id, dataset, universe, fecha, sesion, calendario, timezone, price views o simbolos.
- `RealDataInspector` recalcula SHA-256 del validation manifest del dataset y falla con VALIDATION_MANIFEST_HASH_MISMATCH si cambia.
- El validation manifest entra en `snapshot_or_content_hashes`.
- El preflight real sellado tiene 9 hashes, no 8.
```

Evidencia activa:

```text
run_id = run_preflight_real_fixture_2026_01_05_qg5_v0_2
preflight_status = PREFLIGHT_PASS
physical_inspection_status = PHYSICAL_INSPECTION_PASS
rows_available = 1828
source_files_consumed = 5
content_hashes = 9
warning_codes = OBSERVED_MINUTE_GAP
```

Registro vivo adicional:

```text
2026-07-28 - DONE - Sellado auditabilidad DATA antes de REPLAY - RunDataRequest.fixture_id, REAL_FIXTURE_REQUEST_MISMATCH, VALIDATION_MANIFEST_HASH_MISMATCH, run_preflight_real_fixture_2026_01_05_qg5_v0_2 - siguiente accion: incremento minimo REPLAY/event-loop
```


## 18. Actualizacion 2026-07-28 - Replay Minimo

```text
REPLAY_MINIMUM_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 43 tests
REAL_FIXTURE_REPLAY_SMOKE = PASS
NEXT_INCREMENT = MECHANICAL_DECISION_ORDER_FILL_POSITION
```

Hecho:

```text
- Implementado `HistoricalReplayFeed`.
- Implementados `ReplayBarEvent`, `ReplayGapEvent` y `ReplayRunSummary`.
- Replay exige `PREFLIGHT_PASS` y `PHYSICAL_INSPECTION_PASS`.
- Replay verifica hashes de source files consumidos antes de leer barras.
- Orden determinista: available_at, prioridad de evento, ticker.
- Gaps interiores se emiten como eventos y no se imputan.
- `vw` queda fuera del evento.
```

Evidencia:

```text
replay_run_id = replay_real_fixture_2026_01_05_qg5_v0_1
event_count = 1950
bar_count = 1828
gap_count = 122
first_available_at = 2026-01-05T14:31:00+00:00
last_available_at = 2026-01-05T21:00:00+00:00
```

Registro vivo adicional:

```text
2026-07-28 - DONE - Replay minimo implementado y smoke real PASS - 02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/replay, tests/unit/test_historical_replay_feed.py, 01_GUIDE/02_REPLAY.md - siguiente accion: recorrido mecanico Decision/Order/Fill/Position
```


## 19. Actualizacion 2026-07-28 - Round Trip Mecanico ABAT

```text
MECHANICAL_TRADE_PATH_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 51 tests
REAL_ABAT_MECHANICAL_SMOKE = PASS
NEXT_INCREMENT = ACCOUNTING_MINIMUM
```

Hecho:

```text
- Implementado paquete `mechanics`.
- Decision programada antes del proxy de ejecucion.
- OrderIntent, Order, Fill, Position y TradeLedger creados.
- PnL bruto deriva de fills y coincide con referencia lineal.
- No se afirma fill realism ni edge.
```

Evidencia:

```text
run_id = mechanical_abat_short_open_close_v0_1
ticker = ABAT
quantity = 100
entry_price = 3.87
exit_price = 4.665
gross_pnl = -79.5
final_position_quantity = 0
```

Registro vivo adicional:

```text
2026-07-28 - DONE - Round trip mecanico ABAT PASS - 02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/mechanics, tests/unit/test_mechanical_event_loop.py, 01_GUIDE/03_MECHANICAL_TRADE_PATH.md - siguiente accion: accounting minimo cerrado
```


## 20. Actualizacion 2026-07-28 - Accounting Minimo

```text
ACCOUNTING_MINIMUM_IMPLEMENTED = PASS
ENGINE_TEST_SUITE = PASS, 61 tests
REAL_ABAT_ACCOUNTING_SMOKE = PASS
BACKTEST_VERTICAL_SLICE = ACCOUNTING_VERTICAL_SLICE_CLOSED
```

Hecho:

```text
- Implementado paquete `accounting`.
- Costes separados por componente.
- Cash ledger derivado de fills y costes.
- PnL neto reconciliado contra PnL bruto mecanico.
- Equity final = starting_equity + realized_net_pnl.
- No se afirma broker cost realism, fill realism, short tradability ni edge.
```

Evidencia:

```text
run_id = accounting_abat_short_open_close_v0_1
gross_pnl = -79.50
total_costs = 2.00
realized_net_pnl = -81.50
ending_equity = 9918.50
final_position_quantity = 0
```

Registro vivo adicional:

```text
2026-07-28 - DONE - Accounting minimo gross-to-net PASS - 02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/accounting, tests/unit/test_accounting_engine.py, 01_GUIDE/08_ACCOUNTING.md, runs/accounting_abat_short_open_close_v0_1 - siguiente accion: elegir incremento acotado siguiente
```

