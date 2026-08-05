# 01 DATA

Estado: TSIS_VALIDATED_CONTRACT_ACOTADO
Fecha: 2026-07-28
Alcance: primera capa de infraestructura para `BACKTEST_VERTICAL_SLICE_V0_1`.

Este documento define el contrato minimo de datos que debe existir antes de que el backtester lea una sola barra. No intenta resolver toda la Data Foundation. Su objetivo es cerrar lo necesario para implementar `RunPreflight` y el primer smoke test.

## Menu

- [1. Proposito](#1-proposito)
- [2. Regla Ejecutable](#2-regla-ejecutable)
- [3. Fuentes Consultadas](#3-fuentes-consultadas)
- [4. Lectura De Las Fuentes](#4-lectura-de-las-fuentes)
- [5. Decisiones TSIS V0.1](#5-decisiones-tsis-v01)
- [6. Contratos Minimos](#6-contratos-minimos)
- [7. Salidas Obligatorias](#7-salidas-obligatorias)
- [8. Gates De Aceptacion](#8-gates-de-aceptacion)
- [9. Tests Iniciales](#9-tests-iniciales)
- [10. Fuera De Alcance Por Ahora](#10-fuera-de-alcance-por-ahora)
- [11. Siguiente Paso](#11-siguiente-paso)
- [12. Preguntas Abiertas](#12-preguntas-abiertas)

## 1. Proposito

La capa de datos responde una pregunta:

```text
Que informacion puede observar legalmente este backtest en cada timestamp?
```

Para TSIS small caps esto no es un simple paso de carga. Controla:

```text
survivorship
delistings
corporate actions
sesiones
minutos ausentes
price views
quote-guarded repairs
precio de senal
precio de valoracion
precio proxy de ejecucion
```

Si esta capa es ambigua, el resto del motor puede estar mecanicamente correcto y aun asi producir un backtest falso.

## 2. Regla Ejecutable

El backtester no acepta un path de precios suelto.

Debe recibir una politica declarada de consumo:

```text
PriceViewPolicy
UniversePolicy
SessionPolicy
MissingDataPolicy
CorporateActionPolicy
CandidateConsumptionPolicy
```

`RunPreflight` es el primer componente obligatorio. Resuelve esas politicas antes de que el motor lea datos y falla cerrado si algo no esta permitido.

## 3. Fuentes Consultadas

### Contratos Locales TSIS

- `G:/TSIS/data/README.md`
- `G:/TSIS/data/ohlcv_1m_quote_guarded_full_universe_materialization_plan_2026_07_06.md`
- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/raw_data_authority_and_derivation_map.md`
- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md`
- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_research/LT1B_UNIVERSE_SOURCE_OF_TRUTH_CERTIFICATION.md`
- `C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/00_CTO/99_NOTAS_BRUTO_gpt/00_BACKTEST_ENGINE_ARCHITECTURE_V0_1.md`

### Sersan

- `00_CTO/00_SERSANS_SISTEMAS/README.md`
- `00_CTO/00_SERSANS_SISTEMAS/00_SERSANS_SISTEMAS_COURSE/07_INTEGRATION/FINAL/SERSAN_SYSTEM_MANUAL.md`
- `00_CTO/00_SERSANS_SISTEMAS/00_SERSANS_SISTEMAS_COURSE/07_INTEGRATION/FINAL/KNOWLEDGE_RECORDS/KR-001.md`
- `00_CTO/00_SERSANS_SISTEMAS/00_SERSANS_SISTEMAS_YOUTUBE/Small Caps el backtest NO te prepara para esto  1 mes en real/ideas_extraidas/microcap_smallcap_backtest_deep_research_v0_1.md`

### Libros Procesados

- `successful_algorithmic_trading`: capitulos 3, 7, 8 y 14.
- `python_for_algorithmic_trading_hilpisch`: capitulos 3, 4, 6 y 7.
- `algorithmic_trading_chan`: capitulos 1, 3 y 4.
- `machine_trading_chan`: capitulos 1 y 6.
- `trading_and_exchanges_harris`: precio observado, precio ejecutable, liquidez y spread.
- `evaluation_optimization_trading_strategies_pardo`: especificacion del experimento y preliminary testing.

## 4. Lectura De Las Fuentes

### 4.1 Root Fisico No Es Autoridad Semantica

TSIS separa:

```text
root fisico = donde viven los bytes
contrato del dataset = que significa el dato
```

El raw/staged 1m canonico vive en:

```text
G:/TSIS/data/ohlcv_1m
```

Pero el backtester v0.1 no debe consumir raw 1m directamente salvo auditoria o test especifico. Para el primer vertical slice la vista candidata preferente es:

```text
price_view = quote_guarded_1m
physical_root = C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
raw_lineage = G:/TSIS/data/ohlcv_1m
validation_manifest = C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/_validation_runs/qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z/final_manifest_validation.json
```

### 4.2 Todo Consumo De Precios Declara `price_view`

Esto aplica tanto a raw/staged como a vistas derivadas.

Ejemplos:

```text
raw_1m
split_normalized_1m
quote_guarded_1m
otra vista contratada
```

La regla no existe para hacer documentacion. Existe para que `RunPreflight` impida mezclas peligrosas:

```text
senal con adjusted y fill con precio sintetico
raw con velas malas sin reparar
candidate dataset sin manifest de validacion
PnL sin saber de que vista procede
```

### 4.3 Estado Real De `v0_1` Y `v0_2_candidate`

Hay dos salidas fisicas distintas:

```text
ohlcv_1m_quote_guarded_full_universe_v0_1
  path = C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1
  years_present = 2005..2026
  global_clean_close_2005_2026 = false
  status = candidate_not_official
  full_universe_claim = false
  problema conocido = 2015..2020 complete_with_failures / failed_tickers > 0

ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
  path = C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
  validation_status = PASS
  status = validated_candidate_for_controlled_downstream_consumption
  promotion_state = validated_candidate_not_unrestricted_institutional
  full_universe_claim = validated_physical_candidate_2005_2026
```

La `v0_2_candidate` resuelve tecnicamente los failures conocidos de `v0_1` mediante un merge hardlink `v0_1 + delta 2015..2020`.

Validacion observada:

```text
years = 2005..2026
candidate_files_seen = 1272004
candidate_files_from_original = 1228331
candidate_files_from_delta = 43673
expected_delta_pairs_observed = 3918
source_missing = 0
schema_checked = 600
schema_mismatches = 0
errors = 0
warnings = 0
status = PASS
```

Pero no es promocion institucional irrestricta:

```text
promotion_authorization = false
promotion_note = Validation PASS makes the candidate eligible for promotion review only; it does not promote the dataset.
```

Lectura operativa:

```text
v0_1 = no usar como full limpio 2005..2026.
v0_2_candidate = input controlado candidato si el run declara manifest, scope y limitaciones.
```

### 4.4 Validacion Fisica No Demuestra Realismo De Fills

La validacion tecnica de `v0_2_candidate` demuestra presencia, fuente, delta, schema y ausencia de errores observados por ese validador.

No demuestra por si sola:

```text
que cada precio sea ejecutable
que el OHLC represente liquidez disponible
que el fill model sea economicamente realista
que una estrategia tenga edge
```

Para v0.1, `quote_guarded_1m` queda asi:

```text
signal: allowed_controlled
valuation: allowed_controlled
execution: proxy_allowed_for_engine_mechanics_only
```

Significa:

```text
se puede usar para validar clock, replay, orders, fills mecanicos, accounting y ledgers.
no permite afirmar fill realism ni edge economico sin una revision posterior de execution semantics.
```

### 4.5 Sersan Y Los Libros

Sersan KR-001 fija una regla central: una serie historica no es neutral. Depende de proveedor, sesion, zona horaria, ajustes, continuidad y disponibilidad temporal.

Los libros refuerzan estas reglas:

```text
Successful Algorithmic Trading -> securities master, data handler, sesgos, data quality.
Hilpisch -> research vectorizado rapido, pero autoridad event-based/online para path dependency.
Chan -> survivorship, lookahead, corporate actions y precios ejecutables.
Machine Trading -> BBO/NBBO, consolidated price vs executable price, intradia y latency.
Harris -> last, bid, ask, midpoint y fill price no son el mismo objeto economico.
Pardo -> todo experimento debe declarar dataset, universo, parametros, costes, fills y supuestos.
```

## 5. Decisiones TSIS V0.1

### DATA-DEC-001: `RunPreflight` Es Obligatorio

Todo backtest empieza con `RunPreflight`.

El motor falla cerrado si no puede resolver:

```text
dataset_id
dataset contract
schema
PriceViewPolicy
UniversePolicy
date range
SessionPolicy
timezone
MissingDataPolicy
CorporateActionPolicy
CandidateConsumptionPolicy
known limitations
```

### DATA-DEC-002: Tres Vistas De Precio

El run debe declarar:

```text
signal_price_view
execution_price_view
valuation_price_view
```

Aunque las tres apunten inicialmente a `quote_guarded_1m`, la equivalencia debe quedar declarada.

### DATA-DEC-003: Semantica Temporal De Barra 1m

V0.1 adopta esta regla:

```text
intervalo = [ts_start, ts_end)
available_at = ts_end
```

La estrategia solo puede usar OHLCV de una barra cuando:

```text
decision_timestamp >= available_at
```

El timestamp fisico del proveedor debe normalizarse durante ingestion/adaptacion a:

```text
ts_start
ts_end
available_at
```

Si una fuente solo trae un campo temporal ambiguo, el adapter debe resolver su significado o fallar cerrado.

### DATA-DEC-004: Fixtures Separados

Hay dos tipos de prueba:

```text
NON_EMPIRICAL_TEST_FIXTURE
  fixture sintetico para tests unitarios de motor.
  no necesita pertenecer a LT1B.
  debe estar marcado como no empirico y no publicable como backtest.

TSIS_REAL_DATA_FIXTURE
  muestra real pequena basada en LT1B y v0_2_candidate.
  sirve para probar integracion con rutas, schemas, sesiones y manifests reales.
```

Los backtests empiricos deben usar un universo versionado. Los fixtures sinteticos pueden usar simbolos inventados si el manifest los marca explicitamente.

### DATA-DEC-005: Universo LT1B Para Backtests Empiricos

V0.1 usa `lt1b_universe_v0_1` o un subuniverso derivado con manifest propio.

Regla minima:

```text
ticker normalizado + interseccion con ventana [first_seen_date, last_observed_date]
```

El manifest debe aclarar que `lt1b_universe_v0_1` es un corte operativo gobernado por Data Foundation y no una membership diaria perfecta por market cap.

### DATA-DEC-006: Missing Data Sin Imputacion

V0.1 adopta:

```text
missing_data_policy = EMIT_GAP_WITHOUT_IMPUTATION
```

Reglas:

```text
no fabricar barras
no forward-fill de OHLCV para crear liquidez
registrar gap
fallar ticker-day si falta una barra requerida por la estrategia smoke
```

Las estrategias posteriores podran decidir si saltan el ticker-day, pero el motor no debe ocultar el hueco.

### DATA-DEC-007: Corporate Actions Minimo V0.1

Para el primer smoke test:

```text
corporate_action_policy = EXCLUDE_EFFECTIVE_CA_TICKER_DAYS
```

Si no existe una comprobacion disponible para el ticker-day, el run debe declararlo como limitacion. El primer vertical slice no debe cruzar sesiones alrededor de splits/reverse splits conocidos.

### DATA-DEC-008: Candidato Autorizado Por Manifest, No Por Booleano

No basta con:

```text
allow_candidate_dataset = true
```

Debe existir:

```text
candidate_consumption_policy
authorization_basis
accepted_validation_manifest
accepted_limitations
```

Para v0.1, la autorizacion candidata inicial es:

```text
candidate_dataset = ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
authorization_basis = validation_pass_for_controlled_downstream_consumption
accepted_validation_manifest = C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/_validation_runs/qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z/final_manifest_validation.json
```

## 6. Contratos Minimos

### `RunDataRequest`

```text
run_id
run_purpose
dataset_id
signal_price_view
execution_price_view
valuation_price_view
universe_id
date_start
date_end
session_policy
timezone
calendar_id
missing_data_policy
corporate_action_policy
symbols_optional
candidate_consumption_policy
```

### `PriceViewPolicy`

```text
signal:
  price_view
  physical_root
  validation_manifest
  allowed_use

execution:
  price_view
  physical_root
  validation_manifest
  allowed_use
  execution_semantics_state

valuation:
  price_view
  physical_root
  validation_manifest
  allowed_use

raw_lineage
known_limitations
```

V0.1 default:

```text
signal.price_view = quote_guarded_1m
signal.allowed_use = allowed_controlled

execution.price_view = quote_guarded_1m
execution.allowed_use = proxy_allowed_for_engine_mechanics_only
execution.execution_semantics_state = pending_execution_semantics_review

valuation.price_view = quote_guarded_1m
valuation.allowed_use = allowed_controlled
```

### `CandidateConsumptionPolicy`

```text
candidate_dataset_id
candidate_physical_root
authorization_basis
accepted_validation_manifest
promotion_authorization
permitted_run_purposes
accepted_limitations
```

### `ResolvedDataContext`

```text
dataset_id
dataset_version
resolved_physical_root
schema_version
price_view_policy
universe_dataset_id
universe_run_id
universe_filter_policy
calendar_id
session_policy
timezone
data_quality_state
candidate_consumption_policy
known_limitations
source_contract_paths
```

### `UniverseMembership`

```text
ticker
first_seen_date
last_observed_date
classification_1b
effective_from
effective_to
known_at
selection_rule_id
selection_rule_version
membership_source_snapshot
membership_source_hash
```

Si alguno de estos campos no existe fisicamente en LT1B, `RunPreflight` debe poblarlo como `not_available` y registrarlo como limitacion. No debe inventarlo.

### `MarketDataBar1m`

Payload minimo v0.1:

```text
ticker
ts_start
ts_end
available_at
session_label
open
high
low
close
volume
price_view
quality_flags
source_partition_id
source_file
```

Regla:

```text
available_at = ts_end
```

### `MissingDataPolicy`

```text
policy_id
on_missing_bar
on_required_open_missing
on_required_close_missing
imputation_allowed
gap_event_emitted
```

V0.1:

```text
on_missing_bar = EMIT_GAP_WITHOUT_IMPUTATION
on_required_open_missing = FAIL_TICKER_DAY
on_required_close_missing = FAIL_TICKER_DAY
imputation_allowed = false
gap_event_emitted = true
```

### `CorporateActionPolicy`

```text
policy_id
source_dataset_id
source_snapshot
on_effective_action_inside_ticker_day
on_unknown_action_state
```

V0.1:

```text
on_effective_action_inside_ticker_day = EXCLUDE_TICKER_DAY
on_unknown_action_state = DECLARE_LIMITATION
```

### `DataPreflightReport`

JSON obligatorio:

```text
resolved
reason_if_failed
dataset_id
resolved_physical_root
price_view_policy
universe_policy
date_range
session_policy
timezone
calendar_id
candidate_consumption_policy
rows_available
symbols_available
date_min
date_max
missing_data_summary
corporate_action_screen
known_limitations
```

Markdown opcional:

```text
human_summary
```

## 7. Salidas Obligatorias

Todo run debe escribir:

```text
data_manifest.json
universe_manifest.json
data_preflight_report.json
```

Puede escribir:

```text
data_preflight_report.md
selected_universe.parquet
market_data_sample_profile.parquet
```

`data_manifest.json` debe identificar como minimo:

```text
manifest_schema_version
dataset_id
dataset_version
resolved_physical_root
price_view_policy
date_range
session_policy
timezone
calendar_id
source_partitions_or_files_consumed
snapshot_or_content_hashes
validation_manifest
candidate_authorization
known_limitations
```

`universe_manifest.json` debe identificar como minimo:

```text
universe_id
universe_run_id
selection_rule
effective_window
selected_symbols
source_snapshot
source_hash
exclusions_and_reasons
limitations
```

## 8. Gates De Aceptacion

### `DATA_G1_DATASET_RESOLVED`

`dataset_id`, root fisico, schema, price view policy y limitaciones se resuelven antes de leer filas.

### `DATA_G2_PRICE_VIEW_POLICY_RESOLVED`

El run declara `signal_price_view`, `execution_price_view` y `valuation_price_view`. Si coinciden, la equivalencia queda registrada.

### `DATA_G3_UNIVERSE_RESOLVED`

Backtests empiricos usan `lt1b_universe_v0_1` o un subuniverso derivado con manifest. Tests sinteticos usan `NON_EMPIRICAL_TEST_FIXTURE`.

### `DATA_G4_TEMPORAL_LEGALITY`

La estrategia no puede leer:

```text
membresia futura del universo
estado futuro de corporate actions
barras futuras
high/low/close antes de `available_at`
labels u outcomes futuros
```

### `DATA_G5_CANDIDATE_AUTHORIZATION`

Si se consume un candidato, el run declara:

```text
candidate_dataset_id
authorization_basis
accepted_validation_manifest
promotion_authorization
accepted_limitations
```

### `DATA_G6_MISSING_DATA_POLICY`

Todo hueco se registra. No hay imputacion silenciosa.

### `DATA_G7_CORPORATE_ACTION_POLICY`

El run declara como trata ticker-days con corporate actions efectivas o estado desconocido.

### `DATA_G8_SAMPLE_SMOKE_READ`

Una muestra pequena se carga, ordena y emite deterministicamente sin leer todo el universo.

### `DATA_G9_MANIFESTS_WRITTEN`

El run escribe `data_manifest.json`, `universe_manifest.json` y `data_preflight_report.json`.

## 9. Tests Iniciales

Primer paquete de tests para `RunPreflight`:

```text
dataset inexistente -> fail closed
price view no autorizada -> fail closed
universe no resuelto -> fail closed
candidate dataset sin validation_manifest -> fail closed
barra no visible antes de available_at
mismo input -> mismo orden y mismos manifests
hueco de datos -> comportamiento segun MissingDataPolicy
fixture sintetico separado de fixture empirico
```

## 10. Fuera De Alcance Por Ahora

No requerido para la primera capa:

```text
reconstruccion completa de CRSP delisting returns
promocion institucional irrestricta de v0_2_candidate
historial completo de borrow/locates
reconstruccion L2/order book completa
historial OTC de tiers y disclosure
todos los casos extremos de corporate actions
batch completo 2005-2026
fill realism economico definitivo
```

Estas piezas no se rechazan. Se aplazan hasta que el vertical slice las necesite.

## 11. Siguiente Paso

Implementar el primer incremento de `RunPreflight` en `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE`:

```text
input: RunDataRequest
outputs:
  ResolvedDataContext
  data_manifest.json
  universe_manifest.json
  data_preflight_report.json

tests:
  NON_EMPIRICAL_TEST_FIXTURE
  TSIS_REAL_DATA_FIXTURE
```

Antes de ejecutar ese plan, leer el handoff operativo:

```text
C:/TSIS_Data/00_CTO/14_BACKTEST_ENGINE/AGENTS.md
```

Cada avance de `RunPreflight` debe actualizar `AGENTS.md`, `CHANGELOG.md`, los registros de governance aplicables y este documento si cambia el contrato DATA.
`DATA` y `REPLAY` pueden coevolucionar cuando sea necesario para cerrar la semantica temporal del primer smoke test. No se desarrollara otra capa mas alla de lo necesario para ese objetivo.

## 12. Preguntas Abiertas

```text
Q1. RESUELTA 2026-07-28: el root fisico del codigo sera `C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE`.
Q2. Que ticker-days formaran el primer TSIS_REAL_DATA_FIXTURE?
Q3. V0.1 sera regular-only o incluira premarket?
Q4. Que fuente concreta usaremos para detectar corporate actions efectivas en el fixture?
Q5. Que formato exacto tendran los hashes de source_partitions_or_files_consumed?
Q6. Cuando revisaremos execution semantics de quote_guarded_1m para pasar de proxy mecanico a execution view realista?
```



## 13. Actualizacion 2026-07-28 - Root De Codigo

Q1 queda resuelta:

```text
root fisico del codigo = C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
```

La siguiente accion de DATA ya no es ampliar el contrato. Es implementar el primer incremento de `RunPreflight` en ese root:

```text
src/tsis_backtest/preflight/contracts.py
src/tsis_backtest/preflight/registries.py
src/tsis_backtest/preflight/manifests.py
src/tsis_backtest/preflight/run_preflight.py
tests/unit/test_run_preflight.py
tests/fixtures/non_empirical/
```

Orden:

```text
1. tests sinteticos fail-closed
2. fixture real pequeno
3. preflight real
4. actualizar estado de contrato si hay evidencia reproducible
```


## 14. Actualizacion 2026-07-28 - RunPreflight Sintetico

Evidencia de implementacion inicial:

```text
root = C:/TSIS_Data/02_TSIS_BACKTEST_ENGINE
micro_plan = docs/00_system/01_RUNPREFLIGHT_IMPLEMENTATION_PLAN_V0_1.md
implementation = src/tsis_backtest/preflight/
tests = tests/unit/test_run_preflight.py
verification = 17 tests OK
```

Estado de contrato:

```text
01_DATA sigue en TSIS_CONTRACT_DEFINED_DRAFT.
No asciende todavia a TSIS_VALIDATED_CONTRACT porque falta fixture real TSIS y preflight real acotado.
```

Siguiente paso DATA:

```text
seleccionar TSIS_REAL_DATA_FIXTURE
crear configs de dataset/universe/run
hacer preflight real pequeno
registrar manifests y limitaciones
```


## 15. Actualizacion 2026-07-28 - Endurecimiento RunPreflight

Estado exacto tras endurecimiento:

```text
RUNPREFLIGHT_CONTRACT_RESOLUTION = IMPLEMENTED
SYNTHETIC_UNIT_TESTS = PASS, 17 tests
REAL_DATA_INSPECTION = NOT_IMPLEMENTED
REAL_DATA_PREFLIGHT = NOT_EXECUTED
```

Correcciones aplicadas:

```text
DATASET_ROOT_NOT_FOUND cubierto por test
INVALID_DATE_RANGE cubierto por test
CANDIDATE_RUN_PURPOSE_NOT_PERMITTED cubierto por test
SYMBOL_NOT_IN_UNIVERSE cubierto por test
MissingDataPolicy serializada completa en data_manifest.json
CorporateActionPolicy serializada completa en data_manifest.json
outputs por output_root/run_id
RUN_OUTPUT_NOT_EMPTY evita mezclar outputs viejos y nuevos
```

Aclaracion importante:

```text
La politica de missing data existe como contrato.
La deteccion real de gaps, open ausente y close ausente todavia no esta implementada.
La inspeccion de particiones reales, filas, hashes y corporate actions pertenece al siguiente incremento.
```


## 16. Actualizacion 2026-07-28 - DATA Validado Acotado

Evidencia:

```text
RunPreflight implementado
RealDataInspector implementado
preflight real sellado = run_preflight_real_fixture_2026_01_05_qg5_v0_2
preflight_status = PREFLIGHT_PASS
physical_inspection_status = PHYSICAL_INSPECTION_PASS
content_hashes = 9
```

Alcance de la validacion:

```text
validado para fixture real acotado de 2026-01-05 y cinco simbolos LT1B
no implica promocion institucional irrestricta de v0_2_candidate
no implica fill realism ni edge economico
```
