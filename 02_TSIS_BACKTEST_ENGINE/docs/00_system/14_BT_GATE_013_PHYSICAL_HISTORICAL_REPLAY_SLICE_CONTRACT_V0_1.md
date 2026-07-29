# BT-GATE-013 — Physical Historical Replay Slice Contract V0.1

## 0. Control del documento

```text
DOCUMENT_ID =
14_BT_GATE_013_PHYSICAL_HISTORICAL_REPLAY_SLICE_CONTRACT_V0_1

GATE_ID =
BT-GATE-013

GATE_NAME =
PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1

CONTRACT_VERSION =
V0.1

STATUS =
CONTRACT_DRAFT_PENDING_OWNER_REVIEW

BT-GATE-013 =
NOT_OPEN

BT-GATE-013_IMPLEMENTATION =
NOT_AUTHORIZED

CODE_IMPLEMENTATION =
NOT_AUTHORIZED
```

Este documento define el contrato propuesto para `BT-GATE-013`. No autoriza código, modificación del provider, reconstrucción upstream, consumo de `Market State` o `Event State`, ni ejecución del backtest completo 2005–2026.

---

## 1. Antecedentes y punto de partida aceptado

`BT-GATE-012` se encuentra cerrado:

```text
BT-GATE-012 =
CLOSED_PASS_IMPLEMENTATION_ACCEPTED

IMPLEMENTATION_ACCEPTANCE =
ACCEPTED

FINAL_OWNER_REVIEW =
PASS
```

`BT-GATE-012` ya demostró, sobre fixtures controlados:

```text
multi-symbol replay
multi-session replay
single global replay order
portfolio cash continuity
positions and equity accounting
session enforcement
orders, fills and trades
deterministic execution
artifact and manifest production
```

La incertidumbre principal siguiente no es construir todavía un runner completo de investigación small caps. Es demostrar que el motor aceptado puede cruzar de forma causal, trazable y determinista la frontera:

```text
physical historical rows
        ↓
canonical physical-bar adaptation
        ↓
ReplayBarEvent / ReplayGapEvent
        ↓
BT-GATE-012 accepted portfolio replay engine
```

---

## 2. Pregunta contractual del gate

`BT-GATE-013` debe responder exclusivamente:

```text
¿Puede el motor aceptado en BT-GATE-012 ejecutar un slice histórico
físico pequeño procedente de 013_ohlcv_1m_quote_guarded,
respetando disponibilidad temporal, sesiones, orden global,
linaje físico, integridad de inputs, contabilidad y determinismo,
sin modificar la semántica aceptada del motor?
```

El gate no pregunta:

```text
¿Existe edge?
¿Es realista económicamente un short?
¿Había borrow o locate?
¿Puede escalarse a todo 2005–2026?
¿Está listo el runner científico completo?
```

---

## 3. Principio de una sola frontera nueva

`BT-GATE-013` autorizará, si el contrato es aprobado, una sola capacidad nueva:

```text
NEW_AUTHORIZED_BOUNDARY =
PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_EVENTS
```

No se autoriza introducir simultáneamente:

```text
point-in-time universe construction
stocks-in-play eligibility
Market State consumption
Event State consumption
borrow or locate evidence
SSR semantics
halt semantics
liquidity or capacity modeling
research batch families
parameter search
statistical edge validation
```

Regla de diagnóstico:

```text
ONE_GATE =
ONE_PRIMARY_UNCERTAINTY
```

Si el gate falla, la causa debe poder localizarse en la frontera física, temporal, de adaptación, de replay, de contabilidad o de reproducibilidad definida aquí.

---

## 4. Objetivo positivo

El gate deberá demostrar:

1. Resolución explícita de un slice físico pequeño de `013_ohlcv_1m_quote_guarded`.
2. Validación de integridad y esquema antes del replay.
3. Adaptación determinista de filas físicas a eventos canónicos.
4. Entrega de cada barra solamente cuando su información completa sea legalmente observable.
5. Detección explícita de minutos contractualmente esperados pero ausentes.
6. Ejecución multi-symbol y multi-session mediante el runner aceptado en `BT-GATE-012`.
7. Linaje verificable desde cada `ReplayBarEvent` hasta una fila física exacta.
8. Reconciliación de órdenes, fills, trades, cash, posiciones, costes y equity.
9. Reproducción equivalente desde extracciones limpias.
10. Conservación de todas las fronteras no autorizadas.

---

## 5. Fuente física autorizada

```text
AUTHORIZED_SOURCE_TABLE_ID =
013_ohlcv_1m_quote_guarded

AUTHORIZED_DATA_PRODUCT =
RAW_1_MINUTE_EXECUTION_BARS_ONLY

AUTHORIZED_ACCESS =
READ_ONLY

UPSTREAM_REBUILD =
PROHIBITED

PROVIDER_CODE_MODIFICATION =
PROHIBITED
```

El uso de `013_ohlcv_1m_quote_guarded` no autoriza automáticamente otras tablas, derivados, features o productos del provider.

Antes de ejecutar el gate, la evidencia de implementación deberá congelar:

```text
source_table_id
source_contract_version
source_schema_version
source_dataset_version
source_root_identity
source_relative_paths
source_file_sha256
source_file_size_bytes
source_file_row_count
```

No se permiten rutas absolutas como identidad científica portable.

```text
ABSOLUTE_PATH_IN_SCIENTIFIC_IDENTITY =
PROHIBITED
```

---

## 6. Binding físico y esquema

El adapter deberá declarar, mediante configuración versionada y hasheada, el binding exacto entre el esquema físico y los campos canónicos requeridos:

```text
source symbol field
source bar timestamp field
source open field
source high field
source low field
source close field
source volume field
source transaction-count field, if contractually present
source provenance or row locator fields
source repair/quality fields required by table 013
```

El contrato no permite adivinar nombres de columnas ni semánticas a partir de convenciones.

```text
UNDECLARED_SCHEMA_INFERENCE =
PROHIBITED

IMPLICIT_COLUMN_FALLBACK =
PROHIBITED

SILENT_TYPE_COERCION =
PROHIBITED
```

La implementación deberá fallar antes del replay si:

- falta un campo obligatorio;
- el tipo físico no es compatible con el binding congelado;
- existen valores nulos en campos contractualmente no nulos;
- `high < max(open, close)`;
- `low > min(open, close)`;
- `high < low`;
- el volumen es negativo;
- el símbolo no puede normalizarse sin ambigüedad;
- el timestamp no puede interpretarse de manera inequívoca;
- una regla de calidad obligatoria de la tabla `013` no se cumple.

No se autoriza reparar datos dentro del adapter:

```text
ADAPTER_DATA_REPAIR =
PROHIBITED
```

---

## 7. Componente autorizado

El componente propuesto es:

```text
PhysicalBarReplayAdapterV0_1
```

Responsabilidad única:

```text
validated physical 013 row
        ↓
canonical ReplayBarEvent
```

y, cuando corresponda:

```text
missing contractually expected minute
        ↓
ReplayGapEvent
```

El adapter:

- no calcula features;
- no calcula `Market State`;
- no calcula `Event State`;
- no consulta `StateBundle`;
- no decide el universo;
- no selecciona oportunidades;
- no genera señales;
- no modifica órdenes;
- no ejecuta fills;
- no repara datos;
- no infiere halts;
- no cambia accounting.

```text
StateReplayFeed =
NOT_AUTHORIZED
```

El nombre `StateReplayFeed` queda reservado para una futura frontera de consumo de estados.

---

## 8. Perfil físico mínimo de aceptación

El slice deberá ser pequeño, congelado y suficiente para probar estructura, no rentabilidad:

```text
PHYSICAL_REPLAY_ACCEPTANCE_PROFILE_V0_1

distinct_sessions >= 2
distinct_symbols_per_session >= 3
symbol_sessions >= 6

same_timestamp_cross_symbol_bars =
REQUIRED

at_least_one_detectable_missing_expected_minute =
REQUIRED

contractual_session_open_coverage =
REQUIRED

contractual_session_close_coverage =
REQUIRED

physical_source_rows =
REQUIRED

portable_relative_paths =
REQUIRED

all_input_files_hashed =
REQUIRED
```

La selección deberá congelarse antes de inspeccionar PnL agregado.

```text
SLICE_SELECTION_POLICY =
OPERATIONAL_COVERAGE_ONLY

PROFITABILITY_BASED_SELECTION =
PROHIBITED

OUTCOME_BASED_SELECTION =
PROHIBITED
```

La evidencia deberá explicar por qué cada sesión y símbolo fue incluido en términos de cobertura operacional:

```text
session boundary
cross-symbol timestamp tie
physical gap
multi-session cash continuity
source partition coverage
```

---

## 9. Contrato temporal

### 9.1 Instantes distintos

Cada barra física adaptada deberá distinguir, como mínimo:

```text
market_timestamp_utc
bar_start_timestamp_utc
bar_end_timestamp_utc
source_as_of_utc
available_at_utc
replay_delivery_timestamp_utc
```

Definiciones:

- `market_timestamp_utc`: timestamp de mercado representado por la fila según el contrato de `013`.
- `bar_start_timestamp_utc`: inicio inclusivo del intervalo representado.
- `bar_end_timestamp_utc`: final exclusivo del intervalo representado.
- `source_as_of_utc`: máximo instante fuente utilizado para producir la fila física.
- `available_at_utc`: primer instante en que todos los campos entregados por la barra pueden ser consumidos legalmente.
- `replay_delivery_timestamp_utc`: instante del reloj del replay en el que el evento se entrega realmente.

No se permite colapsar estas semánticas en un único campo ambiguo:

```text
SINGLE_AMBIGUOUS_TIMESTAMP =
PROHIBITED
```

### 9.2 Disponibilidad de una barra OHLCV

Para una barra que representa:

```text
[bar_start_timestamp_utc, bar_end_timestamp_utc)
```

sus valores completos:

```text
high
low
close
volume
transaction_count, if present
```

no pueden entregarse al comienzo del intervalo.

Regla base:

```text
BAR_AVAILABLE_AT_UTC =
max(
  bar_end_timestamp_utc,
  source_as_of_utc,
  contractually_declared_source_availability
)
```

Si `013` documenta una disponibilidad más tardía, prevalece la más tardía. Nunca se permite adelantar la disponibilidad por conveniencia del replay.

### 9.3 Condición legal de entrega

```text
EVENT_DELIVERY_CONDITION =
event_loop.clock >= available_at_utc
```

Invariantes:

```text
bar_end_timestamp_utc > bar_start_timestamp_utc

source_as_of_utc <= available_at_utc

market_timestamp_utc <= available_at_utc

replay_delivery_timestamp_utc >= available_at_utc

consumer_observation_timestamp_utc >= available_at_utc
```

Una violación debe detener el run:

```text
FAIL_TEMPORAL_AVAILABILITY_VIOLATION
```

### 9.4 Zona horaria y DST

```text
INTERNAL_TIME_STANDARD =
UTC

SESSION_CALENDAR_TIMEZONE =
America/New_York

NAIVE_TIMESTAMPS =
PROHIBITED

HOST_LOCAL_TIME_DEPENDENCE =
PROHIBITED
```

La conversión deberá usar un snapshot de calendario congelado y versionado. Los cambios DST no pueden resolverse mediante offsets fijos.

---

## 10. Calendario y sesiones

```text
SESSION_POLICY =
REGULAR_ONLY_XNYS_V0_1

CALENDAR_AUTHORITY =
FROZEN_HASHED_SNAPSHOT

OVERNIGHT_POSITIONS =
PROHIBITED
```

El snapshot deberá declarar, para cada sesión seleccionada:

```text
session_date
market_open_utc
market_close_utc
early_close_flag
calendar_source_identity
calendar_snapshot_sha256
```

No se autoriza inferir el calendario a partir de la presencia o ausencia de barras.

```text
SOURCE_ROWS_AS_CALENDAR_AUTHORITY =
PROHIBITED
```

Una sesión seleccionada truncada o sin el cierre contractual requerido debe fallar, salvo que la ausencia sea precisamente el derivado negativo bajo prueba:

```text
FAIL_TRUNCATED_PHYSICAL_SESSION
FAIL_MISSING_CONTRACTUAL_CLOSE
```

---

## 11. Duplicados, orden y normalización

La clave física canónica mínima será:

```text
(session_date, canonical_symbol, bar_start_timestamp_utc)
```

Política:

```text
EXACT_DUPLICATE_PHYSICAL_ROW =
FAIL_DUPLICATE_PHYSICAL_BAR

CONFLICTING_DUPLICATE_PHYSICAL_ROW =
FAIL_CONFLICTING_PHYSICAL_BAR
```

No se permite deduplicación silenciosa.

Los archivos físicos pueden no venir ordenados. El adapter deberá aplicar un orden canónico determinista antes de producir eventos, sin alterar valores:

```text
PHYSICAL_CANONICAL_ORDER =
(
  available_at_utc,
  market_timestamp_utc,
  canonical_symbol,
  source_file_sha256,
  source_row_locator
)
```

La entrega al motor deberá conservar:

```text
GLOBAL_REPLAY_ORDER =
GLOBAL_REPLAY_ORDER_V0_1
```

Si el orden físico original es relevante para detectar corrupción, deberá registrarse como evidencia, pero no podrá introducir no determinismo.

---

## 12. Linaje fila a evento

Cada `ReplayBarEvent` deberá ser trazable a una única fila física exacta.

Identidad mínima:

```text
source_table_id
source_dataset_version
source_relative_path
source_file_sha256
source_row_locator
source_symbol
source_timestamp_raw
canonical_symbol
bar_start_timestamp_utc
```

El `source_row_locator` debe ser estable para los mismos bytes y no depender del orden de ejecución, número de threads, rutas absolutas o motor de lectura.

```text
EVERY_REPLAY_BAR_EVENT =
TRACEABLE_TO_EXACTLY_ONE_PHYSICAL_SOURCE_ROW

ONE_PHYSICAL_SOURCE_ROW =
AT_MOST_ONE_REPLAY_BAR_EVENT
```

Los `ReplayGapEvent` no tienen una fila física causante. Su linaje deberá referenciar:

```text
calendar_snapshot
symbol_session
expected_minute
left_physical_neighbor, if present
right_physical_neighbor, if present
gap_detection_rule_version
```

---

## 13. Política de gaps

Un minuto contractualmente esperado pero ausente no puede rellenarse silenciosamente.

```text
MISSING_EXPECTED_MINUTE =
ReplayGapEvent

SYNTHETIC_FORWARD_FILL =
PROHIBITED

SYNTHETIC_ZERO_VOLUME_BAR =
PROHIBITED

INTERPOLATED_BAR =
PROHIBITED
```

Semántica de `ReplayGapEvent`:

```text
supplies_execution_price = false
triggers_fill = false
updates_valuation_price = false
creates_trade = false
infers_halt = false
```

El gate deberá distinguir:

```text
session closed
expected minute missing from selected physical source
source truncation
unauthorized symbol/session
```

No deberá afirmar, sin evidencia adicional:

```text
no trading activity
market halt
provider outage
regulatory interruption
```

Por tanto:

```text
GAP_CAUSE_V0_1 =
UNKNOWN_SOURCE_GAP

HALT_INFERENCE =
NOT_AUTHORIZED
```

---

## 14. Estrategia y órdenes de aceptación

El gate deberá reutilizar una lógica determinista ya aceptada o una política mecánica congelada antes de observar resultados.

```text
STRATEGY_PURPOSE =
INFRASTRUCTURE_ACCEPTANCE_ONLY

STRATEGY_LOGIC =
FROZEN_BEFORE_RESULT_INSPECTION

PARAMETER_SEARCH =
PROHIBITED

OPTIMIZATION =
PROHIBITED

OUTCOME_DRIVEN_ADJUSTMENT =
PROHIBITED

EDGE_INTERPRETATION =
PROHIBITED
```

Si la estrategia de `BT-GATE-012` no puede aplicarse sin cambio semántico a barras físicas, el gate deberá detenerse y solicitar revisión del contrato. No se autoriza adaptar oportunistamente la estrategia para conseguir fills o PnL.

---

## 15. Semántica de ejecución heredada

Salvo las nuevas reglas de adaptación física y disponibilidad, las semánticas aceptadas permanecen congeladas:

```text
EXECUTION_SEMANTICS =
UNCHANGED_FROM_BT_GATE_012

GLOBAL_REPLAY_ORDER =
GLOBAL_REPLAY_ORDER_V0_1

ACTIVE_ORDER_EVALUATION_ORDER =
ACTIVE_ORDER_EVALUATION_ORDER_V0_1

PORTFOLIO_VALUATION_PRICE_FIELD =
close

COST_MODEL =
UNCHANGED_FROM_BT_GATE_012

ACCOUNTING_MODEL =
UNCHANGED_FROM_BT_GATE_012
```

Invariantes:

```text
position_zero_before_session_transition = required
cash_continuity_across_sessions = required
orders_reconciled = required
fills_reconciled = required
trades_reconciled = required
costs_reconciled = required
cash_reconciled = required
positions_reconciled = required
equity_reconciled = required
final_positions_zero = required
```

Condiciones de fallo:

```text
FAIL_MISSING_CONTRACTUAL_CLOSE
FAIL_TRUNCATED_PHYSICAL_SESSION
FAIL_UNEXECUTED_REQUIRED_EXIT
FAIL_UNEXPLAINED_OPEN_ORDER_AT_SESSION_END
FAIL_UNEXPLAINED_POSITION_AT_SESSION_END
FAIL_ACCOUNTING_RECONCILIATION
```

`BT-GATE-013` no autoriza cambiar fills, costes o accounting para acomodar los resultados físicos.

---

## 16. Integridad física y protección frente a mutación

Los inputs deberán resolverse y hashearse antes de leer las filas que alimentan el replay.

Regla:

```text
HASH_BEFORE_READ =
REQUIRED

HASH_AFTER_READ =
REQUIRED

HASH_BEFORE_READ =
HASH_AFTER_READ
```

Si los bytes cambian entre resolución y consumo:

```text
FAIL_SOURCE_MUTATION
```

Si el hash real no coincide con el declarado:

```text
FAIL_SOURCE_HASH_MISMATCH
```

El manifest deberá registrar todos los archivos físicamente leídos, incluidos metadatos auxiliares que afecten selección, esquema, calendario o adaptación.

```text
UNDECLARED_PHYSICAL_READ =
PROHIBITED
```

---

## 17. Artefactos obligatorios del run

El run aceptable deberá producir, como mínimo:

```text
resolved_input_manifest
source_file_inventory
source_schema_binding
selected_symbol_sessions
selected_physical_rows
row_to_event_lineage
replay_bar_events
replay_gap_events
orders
fills
trades
cash_ledger
positions
equity_curve
performance_summary
validation_report
negative_derivative_report
final_manifest
```

Los artefactos deberán usar formatos deterministas y esquemas versionados.

El `final_manifest` deberá declarar:

```text
gate_id
gate_contract_version
source_table_id
source_contract_version
source_schema_version
source_dataset_version
source_relative_paths
source_file_sha256
source_file_size_bytes
source_file_row_count
selected_row_count
selected_symbols
selected_sessions
selected_symbol_sessions
minimum_source_timestamp
maximum_source_timestamp
minimum_available_at_utc
maximum_available_at_utc
calendar_snapshot_sha256
adapter_version
engine_version
strategy_version
cost_model_version
accounting_model_version
run_configuration_sha256
artifact_schema_versions
output_artifact_hashes
deterministic_output_hash
validation_status
boundary_preservation_status
```

---

## 18. Hash científico y campos volátiles

El hash científico deberá cubrir todos los inputs, configuraciones y outputs con relevancia causal.

No deberán formar parte del hash científico:

```text
package_creation_timestamp
wall_clock_duration
host_name
user_name
process_id
temporary_directory
absolute_path
installation_path
log_rendering_timestamp
```

La exclusión deberá ser explícita, cerrada y versionada:

```text
VOLATILE_FIELD_EXCLUSION_POLICY =
FROZEN_CLOSED_LIST
```

No se permite excluir un campo después de observar que rompe determinismo.

---

## 19. Determinismo exigido

Se requieren al menos dos reproducciones desde extracciones limpias e independientes:

```text
CLEAN_EXTRACTION_RUN_1
CLEAN_EXTRACTION_RUN_2
```

Deberá cumplirse:

```text
resolved_input_hash_1 = resolved_input_hash_2
selected_rows_hash_1 = selected_rows_hash_2
replay_event_sequence_hash_1 = replay_event_sequence_hash_2
order_sequence_hash_1 = order_sequence_hash_2
fill_sequence_hash_1 = fill_sequence_hash_2
trade_sequence_hash_1 = trade_sequence_hash_2
ledger_hash_1 = ledger_hash_2
equity_curve_hash_1 = equity_curve_hash_2
scientific_manifest_hash_1 = scientific_manifest_hash_2
deterministic_output_hash_1 = deterministic_output_hash_2
```

La reproducción deberá ser independiente de:

```text
absolute extraction directory
host local timezone
filesystem enumeration order
thread scheduling
temporary filenames
```

---

## 20. Pruebas negativas obligatorias

El gate no podrá cerrarse únicamente con el happy path.

### 20.1 Integridad

```text
NEGATIVE_01:
source file byte changed
-> FAIL_SOURCE_HASH_MISMATCH

NEGATIVE_02:
source changed between resolution and completed read
-> FAIL_SOURCE_MUTATION
```

### 20.2 Filas y esquema

```text
NEGATIVE_03:
required physical field missing
-> FAIL_SOURCE_SCHEMA_MISMATCH

NEGATIVE_04:
exact physical row duplicated
-> FAIL_DUPLICATE_PHYSICAL_BAR

NEGATIVE_05:
duplicate symbol/timestamp with conflicting values
-> FAIL_CONFLICTING_PHYSICAL_BAR

NEGATIVE_06:
invalid OHLC or negative volume
-> FAIL_INVALID_PHYSICAL_BAR
```

### 20.3 Tiempo

```text
NEGATIVE_07:
bar delivered before available_at_utc
-> FAIL_TEMPORAL_AVAILABILITY_VIOLATION

NEGATIVE_08:
naive or ambiguous timestamp
-> FAIL_AMBIGUOUS_SOURCE_TIMESTAMP

NEGATIVE_09:
fixed-offset DST handling
-> FAIL_CALENDAR_TIMEZONE_CONTRACT
```

### 20.4 Sesión y scope

```text
NEGATIVE_10:
missing contractual session close
-> FAIL_MISSING_CONTRACTUAL_CLOSE

NEGATIVE_11:
truncated selected session
-> FAIL_TRUNCATED_PHYSICAL_SESSION

NEGATIVE_12:
symbol or session outside frozen selection enters replay
-> FAIL_SCOPE_LEAKAGE
```

### 20.5 Portabilidad y orden

```text
NEGATIVE_13:
same bytes moved to a different absolute extraction path
-> PASS_WITH_IDENTICAL_SCIENTIFIC_HASH

NEGATIVE_14:
physical rows enumerated in a different input order
-> PASS_WITH_IDENTICAL_CANONICAL_EVENT_SEQUENCE
```

### 20.6 Gaps

```text
NEGATIVE_15:
expected minute removed from an otherwise complete symbol-session
-> ReplayGapEvent

ReplayGapEvent supplies price = false
ReplayGapEvent triggers fill = false
ReplayGapEvent updates valuation = false
```

Cada derivado negativo deberá demostrar el error o comportamiento contractual exacto, no solo una excepción genérica.

---

## 21. Validación y criterios de aceptación

```text
BT-GATE-013_ACCEPTANCE_V0_1

contract_conformance = PASS
physical_input_integrity = PASS
source_schema_validation = PASS
source_quality_contract_validation = PASS
slice_selection_freeze = PASS
profitability_independent_selection = PASS
row_level_lineage = PASS
temporal_availability_validation = PASS
calendar_and_session_validation = PASS
gap_semantics = PASS
global_replay_order = PASS
multi_symbol_multi_session_execution = PASS
accounting_reconciliation = PASS
session_enforcement = PASS
negative_derivatives = PASS
clean_reproduction = PASS
deterministic_output = PASS
boundary_preservation = PASS
```

Todos los criterios son obligatorios. No se permite compensar un fallo con el éxito de otros.

Estado final permitido si todos pasan:

```text
BT-GATE-013 =
CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED
```

Estados no autorizados como consecuencia del cierre:

```text
BACKTEST_ENGINE_READY
RESEARCH_RUNNER_READY
FULL_HISTORY_READY
PRODUCTION_READY
ECONOMIC_REALISM_VALIDATED
EDGE_PROVEN
```

---

## 22. Exclusiones expresas

```text
BT-GATE-013_NOT_IN_SCOPE

Market State consumption
Event State consumption
StateBundle physical reads
StateReplayFeed
feature engineering
014 master intraday feature consumption
015 microstructure feature consumption
point-in-time universe construction
stocks-in-play eligibility
news
fundamentals
short-interest data
borrow availability
locates
locate costs
hard-to-borrow modeling
SSR semantics
halt semantics or halt inference
corporate-action modeling beyond already-frozen source integrity
bid/ask execution
partial fills
queue position
liquidity constraints
participation limits
market impact
capital contention claims
batch strategy families
parameter optimization
train/test research orchestration
multiple-testing correction
DSR
PBO
CSCV
machine learning
reinforcement learning
AlphaEvolve
edge claims
full 2005-2026 backtest
provider modification
upstream data rebuild
live trading
```

Regla preservada para gates posteriores:

```text
mechanically executable order
≠
actually shortable action
≠
economically valid trade
≠
demonstrated edge
```

`BT-GATE-013` solo prueba la primera frontera física y mecánica bajo las semánticas heredadas; no demuestra las tres restantes.

---

## 23. Condiciones de stop y revisión material

La implementación futura deberá detenerse y volver a revisión del owner si aparece cualquiera de estas condiciones:

```text
source timestamp semantics cannot be proven
source availability semantics cannot be proven
table 013 schema requires an undeclared interpretation
BT-GATE-012 execution semantics must change
BT-GATE-012 accounting semantics must change
calendar authority must change
data repair becomes necessary
another physical source table becomes necessary
Market State or Event State becomes necessary
provider modification becomes necessary
scope must expand beyond the frozen acceptance slice
```

Estas condiciones constituyen cambio material. No pueden resolverse como detalle interno de implementación.

---

## 24. Evidencia necesaria antes de autorizar implementación

La aprobación del contrato no deberá basarse solo en una declaración documental. El paquete de autorización deberá incluir:

1. Este contrato.
2. Snapshot o inventario verificable de las superficies relevantes del motor aceptado.
3. Contrato físico vigente de `013_ohlcv_1m_quote_guarded`.
4. Esquema físico real y binding canónico propuesto.
5. Semántica documentada del timestamp fuente.
6. Evidencia de disponibilidad de la barra o política conservadora propuesta.
7. Inventario del slice candidato sin resultados económicos.
8. Snapshot de calendario candidato.
9. Declaración reproducible de ausencia de implementación anticipada de `BT-GATE-013`.
10. Escaneo reproducible de preservación de fronteras no autorizadas.

Si la semántica temporal física no puede demostrarse, la implementación no debe autorizarse.

---

## 25. Flujo de autorización propuesto

Estado actual:

```text
BT-GATE-013 =
NOT_OPEN

CONTRACT =
CONTRACT_DRAFT_PENDING_OWNER_REVIEW

IMPLEMENTATION =
NOT_AUTHORIZED
```

Tras revisión y aprobación expresa del contrato:

```text
BT-GATE-013 =
AUTHORIZED_FOR_CONTINUOUS_IMPLEMENTATION

BT-GATE-013_IMPLEMENTATION =
AUTHORIZED

EXECUTION_MODE =
CONTINUOUS_UNTIL_FINAL_ACCEPTANCE_PACKET

NO_INTERMEDIATE_MICROGATES =
AUTHORIZED

NEXT_OWNER_REVIEW =
FINAL_GATE_ACCEPTANCE_ONLY,
UNLESS MATERIAL SCOPE OR SEMANTIC CHANGE
```

La aprobación deberá ser explícita. La existencia de este documento no equivale a autorización.

---

## 26. Paquete final de aceptación

La implementación futura deberá entregar un paquete autocontenido que permita, desde una extracción limpia:

```text
install
validate package integrity
run included tests
run positive physical replay
run all required negative derivatives
reproduce the deterministic hashes
inspect all manifests and lineage artifacts
verify unauthorized-boundary absence
```

El paquete deberá incluir:

```text
exact reproduction commands
package manifest
per-file SHA-256 and size
source subset or an authorized immutable resolution mechanism
all required configuration
calendar snapshot
tests
positive run evidence
negative derivative evidence
governance snapshot
```

No se aceptará evidencia que dependa de archivos externos no declarados o de rutas exclusivas del host de construcción.

---

## 27. Relación con la futura arquitectura small caps

Este gate no sustituye el futuro `SMALL_CAPS_RIGOROUS_RESEARCH_RUNNER`. Lo precede.

Secuencia conceptual no congelada:

```text
BT-GATE-013
Physical Historical Replay Slice
        ↓
future gate
Point-in-Time Market State Consumption
        ↓
future gate
Event State Consumption
        ↓
future gate
Historical Coverage and Batch Scaling
        ↓
future gate
Small-Caps Tradability and Execution Realism
        ↓
future gate
Rigorous Research Runner
        ↓
future gate
Statistical Research Validation
        ↓
future gate
Frozen Strategy Research Backtest
```

Los números y nombres posteriores no quedan autorizados ni congelados por este documento.

---

## 28. Invariantes finales

```text
BT-GATE-012_ACCEPTED_SEMANTICS =
PRESERVED

ONE_NEW_BOUNDARY =
PHYSICAL_013_ROWS_TO_ACCEPTED_REPLAY_EVENTS

NO_BAR_LOOKAHEAD =
REQUIRED

ROW_LEVEL_LINEAGE =
REQUIRED

PHYSICAL_INPUT_HASHING =
REQUIRED

GAP_FORWARD_FILL =
PROHIBITED

DETERMINISTIC_CLEAN_REPRODUCTION =
REQUIRED

MARKET_STATE =
NOT_AUTHORIZED

EVENT_STATE =
NOT_AUTHORIZED

STATE_REPLAY_FEED =
NOT_AUTHORIZED

PROVIDER_MODIFICATION =
NOT_AUTHORIZED

FULL_2005_2026_BACKTEST =
NOT_AUTHORIZED

EDGE_CLAIMS =
NOT_AUTHORIZED
```

---

## 29. Decisión solicitada al owner

Este draft solicita únicamente una decisión contractual:

```text
OPTION_A =
RETURN_WITH_REQUIRED_CONTRACT_CORRECTIONS

OPTION_B =
ACCEPT_CONTRACT_AND_REQUEST_AUTHORIZATION_EVIDENCE_PACKET
```

No solicita todavía:

```text
IMPLEMENTATION_AUTHORIZATION
CODE_CHANGES
PHYSICAL_RUN_EXECUTION
GATE_CLOSURE
```

---

## 30. Estado al emitir V0.1

```text
BT-GATE-013_NAME =
PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1

BT-GATE-013_OBJECTIVE =
PROVE_CAUSAL_DETERMINISTIC_REPLAY_FROM_PHYSICAL_013_DATA

CONTRACT_STATUS =
CONTRACT_DRAFT_PENDING_OWNER_REVIEW

BT-GATE-013 =
NOT_OPEN

CODE_IMPLEMENTATION =
NOT_AUTHORIZED

PHYSICAL_RUN =
NOT_AUTHORIZED

MARKET_STATE =
NOT_AUTHORIZED

EVENT_STATE =
NOT_AUTHORIZED

STATE_REPLAY_FEED =
NOT_AUTHORIZED

FULL_2005_2026_BACKTEST =
NOT_AUTHORIZED
```
