# Changelog - TSIS Backtest Engine

## 2026-07-28

- Initialized the living guide structure under `01_GUIDE`.
- Added `01_GUIDE/01_DATA.md` as the first infrastructure layer.
- Added minimal root orientation in `README.md`, `LOCAL_RULES` and this changelog.
- Decision: documentation remains incremental and subordinate to `BACKTEST_VERTICAL_SLICE_V0_1`.

### Investigacion dataset quote-guarded 1m

- Aclarado en `01_GUIDE/01_DATA.md` que `ohlcv_1m_quote_guarded_full_universe_v0_1` no esta limpia/promovida para 2005..2026: conserva `complete_with_failures` y `failed_tickers > 0` en 2015..2020.
- Detectada `ohlcv_1m_quote_guarded_full_universe_v0_2_candidate` con validacion tecnica PASS para 2005..2026: `candidate_files_seen=1272004`, `candidate_files_from_delta=43673`, `expected_delta_pairs_observed=3918`, `source_missing=0`, `schema_mismatches=0`, `errors=0`, `warnings=0`.
- Decision: `v0_2_candidate` puede considerarse input controlado candidato si el run declara `validation_manifest`, `price_view`, scope y limitaciones; no es promocion institucional irrestricta porque `promotion_authorization=false`.

### Revision DATA antes de RunPreflight

- Reescrito `01_GUIDE/01_DATA.md` como contrato definido-borrador para implementar `RunPreflight`.
- Corregida la contradiccion entre una sola `price_view` y las tres vistas requeridas: `signal_price_view`, `execution_price_view`, `valuation_price_view`.
- Anadida semantica temporal de barra 1m: intervalo `[ts_start, ts_end)` y `available_at = ts_end`.
- Separados `NON_EMPIRICAL_TEST_FIXTURE` y `TSIS_REAL_DATA_FIXTURE`.
- Anadidas `MissingDataPolicy`, `CorporateActionPolicy` y `CandidateConsumptionPolicy`.
- Cambiado `data_preflight_report.md` a `data_preflight_report.json` obligatorio, con markdown opcional.
- Aclarado que `quote_guarded_1m` es proxy de ejecucion solo para mecanica del motor hasta revisar execution semantics.

### Handoff operativo para agentes

- Creado `AGENT.md` como punto de reentrada para otras sesiones o recuperacion tras interrupcion.
- Anadida regla local: cada paso operativo cerrado debe actualizar `AGENT.md`, `CHANGELOG.md` y el documento de guia afectado.
- Enlazado el protocolo desde `README.md`, `LOCAL_RULES`, `01_GUIDE/README.md` y `01_GUIDE/01_DATA.md`.

### Root limpio de implementacion

- Vaciado y recreado `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE` como `ACTIVE_IMPLEMENTATION_ROOT`.
- Creados `README.md`, `AGENTS.md`, `LOCAL_RULES.md`, `CHANGELOG.md` y `pyproject.toml` en el root de implementacion.
- Creadas carpetas minimas para `src`, `tests`, `configs`, `runs` y `docs`.
- Decision: el siguiente paso ya no es ampliar teoria; es implementar `RunPreflight` con tests sinteticos fail-closed.

### RunPreflight sintetico implementado

- Creado micro-plan `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/01_RUNPREFLIGHT_IMPLEMENTATION_PLAN_V0_1.md`.
- Implementados contratos, registries, writers de manifests y `RunPreflight` bajo `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/src/tsis_backtest/preflight`.
- Implementados tests sinteticos en `tests/unit/test_run_preflight.py`.
- Verificacion: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 17 tests OK.
- Decision: no se consumio dato real; el siguiente gate es seleccionar `TSIS_REAL_DATA_FIXTURE`.


### Endurecimiento RunPreflight antes de fixture real

- Anotado estado exacto: `RUNPREFLIGHT_CONTRACT_RESOLUTION = IMPLEMENTED`, `SYNTHETIC_UNIT_TESTS = PASS`, `REAL_DATA_INSPECTION = NOT_IMPLEMENTED`, `REAL_DATA_PREFLIGHT = NOT_EXECUTED`.
- Anadidos tests contractuales faltantes y aislamiento de outputs por `run_id`.
- Anadida serializacion completa de `MissingDataPolicy` y `CorporateActionPolicy` en manifests.
- Verificacion: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` -> 17 tests OK.
- Siguiente paso: inspector minimo de datos reales + seleccion `TSIS_REAL_DATA_FIXTURE`.

### RunPreflight pre-real guards

- Endurecido `RunPreflight` antes de tocar datos reales.
- Anadida validacion segura de `run_id` con `INVALID_RUN_ID` y containment bajo `output_root`.
- Anadida vinculacion exacta del validation manifest aceptado contra `DatasetDefinition.validation_manifest`.
- Anadidos fallos cerrados: `CANDIDATE_REGISTERED_VALIDATION_MANIFEST_REQUIRED`, `CANDIDATE_VALIDATION_MANIFEST_MISMATCH` y `PHYSICAL_INSPECTION_NOT_IMPLEMENTED`.
- Anadidos estados estructurados del reporte: `context_resolution_status`, `physical_inspection_status`, `preflight_status`.
- Verificacion: `$env:PYTHONPATH='src'; python -m unittest discover -s tests` en `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE` -> 21 tests OK.
- Decision: no se amplio `01_DATA.md`; el siguiente trabajo es inspector minimo de datos reales.

### Physical layout discovery and fixture selection

- Descubierto layout fisico de `ohlcv_1m_quote_guarded_full_universe_v0_2_candidate`: `year=YYYY/ticker=SYMBOL/month=MM/part-000.parquet`.
- Inspeccionados metadatos parquet y filas minimas con `pyarrow`; no se ejecuto procesamiento full-universe.
- Confirmada semantica observada: `ts_utc` es inicio de minuto en UTC y `t` coincide como epoch milliseconds; `available_at` debe derivarse como `ts_utc + 1 minuto`.
- Localizado universo `lt1b_universe_v0_1` y fuente `corporate_actions_table_v0_1` en el mount activo `G:/TSIS/data`.
- Seleccionado fixture `TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1` con `ABAT`, `ABEO`, `ABSI`, `ABTC`, `ACB`.
- Evidencia creada en `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.md` y `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/docs/00_system/02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.json`.
- Config creada en `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE/configs/fixtures/TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1.json`.
- Verificacion: suite de motor -> 21 tests OK; fixture JSON valido.
- Estado: `PHYSICAL_LAYOUT_DISCOVERED = PASS`, `TSIS_REAL_DATA_FIXTURE_SELECTED = SELECTED_NOT_INSPECTED`, `REAL_DATA_INSPECTION = NOT_IMPLEMENTED`, `REAL_DATA_PREFLIGHT = NOT_EXECUTED`.

### RealDataInspector y preflight real acotado

- Implementado `RealDataInspector` en `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE` para el fixture quote-guarded acotado.
- Integrado el inspector en `RunPreflight` para que `TSIS_REAL_DATA_FIXTURE` solo pueda pasar con inspeccion fisica ejecutada.
- Corregida `price_view_policy` estructurada en fixture/discovery: `execution.price_view = quote_guarded_1m` y uso permitido separado como proxy mecanico.
- Fijada regla DATA: `vw`/VWAP de proveedor es campo derivado no consumible; no es requerido ni validado por el inspector.
- Declarado `pyarrow>=21` como dependencia explicita del motor.
- Verificacion: suite en `02_TSIS_BACKTEST_ENGINE` -> 32 tests OK.
- Ejecutado `run_preflight_real_fixture_2026_01_05_qg5_v0_1` con resultado `PREFLIGHT_PASS` y `PHYSICAL_INSPECTION_PASS`.
- Evidencia: 1,828 filas, 5 archivos fuente, 8 hashes, cero acciones corporativas exactas; gaps interiores esperados en `ABEO`, `ABSI`, `ACB` registrados como `OBSERVED_MINUTE_GAP` y permitidos sin imputacion.
- Decision: DATA/RunPreflight queda cerrado para el fixture acotado; el siguiente incremento es REPLAY/event-loop minimo, no backtest 2005-2026.


### Sellado auditabilidad DATA antes de REPLAY

- Anadido `fixture_id` a `RunDataRequest`.
- Anadido fallo cerrado `REAL_FIXTURE_REQUEST_MISMATCH` si request y fixture no coinciden exactamente en fixture id, dataset, universe, fecha, sesion, calendario, timezone, price views o simbolos.
- Anadida verificacion SHA-256 del validation manifest del dataset con fallo `VALIDATION_MANIFEST_HASH_MISMATCH`.
- Anadido el validation manifest a `snapshot_or_content_hashes`; la evidencia activa pasa de 8 a 9 hashes.
- Verificacion: suite en `02_TSIS_BACKTEST_ENGINE` -> 34 tests OK.
- Ejecutado `run_preflight_real_fixture_2026_01_05_qg5_v0_2` con resultado `PREFLIGHT_PASS` y `PHYSICAL_INSPECTION_PASS`.
- Decision: DATA queda sellado para abrir el incremento minimo REPLAY/event-loop.


### Replay minimo event-loop

- Creado `01_GUIDE/02_REPLAY.md` como contrato vivo validado de forma acotada.
- Implementado `HistoricalReplayFeed` en `02_TSIS_BACKTEST_ENGINE`.
- Replay exige `PREFLIGHT_PASS`, `PHYSICAL_INSPECTION_PASS` y verifica hashes de archivos consumidos.
- Definido orden determinista: `available_at`, prioridad `GAP` antes de `BAR`, `ticker`.
- Definidos `ReplayBarEvent` y `ReplayGapEvent`; los gaps se emiten sin imputar barras.
- Preservada regla temporal: `available_at = ts_start + 1 minuto`.
- Confirmado que `vw` no se propaga al evento.
- Verificacion: suite en `02_TSIS_BACKTEST_ENGINE` -> 43 tests OK.
- Smoke real: `replay_real_fixture_2026_01_05_qg5_v0_1` -> 1,950 eventos, 1,828 barras, 122 gaps.
- Decision: siguiente incremento sera recorrido mecanico `Decision/Order/Fill/Position`, no backtest completo.


### Round trip mecanico ABAT

- Endurecido REPLAY: `verify_hashes=False` queda rechazado en `HistoricalReplayFeed`.
- Anadido test explicito de prioridad `GAP` antes de `BAR` cuando comparten `available_at`.
- Anadidos hashes de lineage `replay_preflight_report_sha256` y `replay_event_sequence_sha256`.
- Creado `01_GUIDE/03_MECHANICAL_TRADE_PATH.md`.
- Implementado paquete `mechanics` con decision programada, order intent, order, fill, position, trade ledger y summary.
- Smoke real ABAT: short 100 acciones, entrada 3.87, salida 4.665, PnL bruto -79.5, posicion final 0.
- Verificacion: suite en `02_TSIS_BACKTEST_ENGINE` -> 51 tests OK.
- Decision: siguiente incremento sera CostModel / cash ledger / net PnL minimo, no backtest completo.

### Accounting minimo gross-to-net

- Creado `01_GUIDE/08_ACCOUNTING.md` como contrato vivo validado de forma acotada.
- Implementado paquete `accounting` en `02_TSIS_BACKTEST_ENGINE`.
- Separados costes en componentes: commission, routing_or_ecn_fee, regulatory_fee, locate_fee, borrow_fee y other_fee.
- Cash ledger deriva de fills y costes; equity final deriva de starting equity y PnL neto realizado.
- Smoke real ABAT: gross -79.50, costes 2.00, net -81.50, equity final 9918.50, posicion final 0.
- Verificacion: suite en `02_TSIS_BACKTEST_ENGINE` -> 61 tests OK.
- La serializacion conserva tasas sub-cent del modelo de coste, por ejemplo `commission_per_share = 0.005`.
- Decision: accounting mecanico queda cerrado; no se reclama realismo de costes, realismo de fills, tradability short ni edge.


