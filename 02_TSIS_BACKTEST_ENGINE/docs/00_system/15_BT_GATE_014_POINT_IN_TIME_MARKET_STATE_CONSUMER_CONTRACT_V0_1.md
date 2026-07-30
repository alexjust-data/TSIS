# BT-GATE-014 — Point-in-Time Market State Consumer Contract V0.1

## 0. Control del documento

```text
DOCUMENT_ID =
15_BT_GATE_014_POINT_IN_TIME_MARKET_STATE_CONSUMER_CONTRACT_V0_1

GATE_ID =
BT-GATE-014

GATE_NAME =
POINT_IN_TIME_MARKET_STATE_CONSUMER_V0_1

CONTRACT_VERSION =
V0.1

DOCUMENT_DATE =
2026-07-30

DOCUMENT_STATUS =
CONTRACT_ACCEPTED

BT-GATE-014 =
OPEN_BOUNDED_NON_PHYSICAL_IMPLEMENTATION_AUTHORIZED

BT-GATE-014_CONTRACT =
ACCEPTED

BT-GATE-014_IMPLEMENTATION =
AUTHORIZED_FOR_BOUNDED_NON_PHYSICAL_IMPLEMENTATION_ONLY

BT-GATE-014_PHYSICAL_EXECUTION =
NOT_AUTHORIZED

BT-GATE-015_EVENT_STATE =
NOT_OPEN
```

Este documento define el contrato integral del primer consumidor point-in-time de `Market State` dentro del backtester TSIS.

La aceptación expresa de este contrato autoriza únicamente:

```text
adopción local de la evidencia provider;
implementación del contrato consumidor;
implementación de BoundedMarketStateAvailable;
implementación del payload tipado core-four;
implementación de MarketStateAuditLineage;
implementación de MarketStateStore;
extensión bounded del orden temporal;
tests y runs con fixtures explícitamente sintéticos;
producción de evidencia no física.
```

La aceptación de este contrato no autoriza:

```text
abrir el Parquet de Market State;
leer una sola fila física de Market State;
reutilizar la autorización provider ya consumida;
consumir las 104 filas candidatas;
habilitar StateReplayFeed general;
habilitar Event State;
habilitar callbacks de estrategia;
generar señales, órdenes o fills;
calcular PnL;
ejecutar un backtest de investigación;
declarar un dataset oficial;
uso downstream o producción.
```

La mera existencia o descarga de este documento tampoco equivale a su aceptación. La decisión corresponde al owner del backtester y debe quedar registrada en governance.

---

## 1. Antecedente obligatorio

`BT-GATE-013` está cerrado y aceptado:

```text
BT-GATE-013 =
CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED

BT-GATE-013_IMPLEMENTATION =
IMPLEMENTED_AND_ACCEPTED

IMPLEMENTATION_ACCEPTANCE =
ACCEPTED
```

Paquete final aceptado:

```text
bt_gate_013_physical_replay_acceptance_packet_20260730T081836Z.zip

SHA-256 =
4c89a8279ee7a999fc2774cbac06e15d8779ba347aaf28aa1d9fd7bba2895f9d
```

Resultado científico reproducido:

```text
deterministic_output_hash =
ede33c7037a0bd08670423a4ac05b4836aa1472163027c7a86e883fca0b5c019
```

Por tanto, este gate puede apoyarse en que el backtester ya dispone de:

```text
MarketData físico adaptado;
ReplayBarEvent;
ReplayGapEvent;
reloj simulado;
orden global determinista;
linaje físico;
protección de integridad;
reproducción limpia;
separación entre replay, ejecución y accounting.
```

`BT-GATE-014` no reabre ni modifica la aceptación de `BT-GATE-013`.

---

## 2. Pregunta contractual del gate

`BT-GATE-014` debe responder exclusivamente:

```text
¿Puede el backtester recibir un Market State core-four tipado,
validarlo, ordenarlo point-in-time, almacenarlo de forma inmutable
y exponerlo a un probe consumidor solamente cuando es legalmente
observable, sin confundirlo con MarketData, sin leakage y sin activar
estrategias, órdenes, fills o PnL?
```

El gate no pregunta:

```text
¿Mejora el Market State una estrategia?
¿Existe edge?
¿Qué variables predicen mejor un resultado?
¿Puede operarse ACIU?
¿Puede escalarse a 104 filas o a todo 2005–2026?
¿Está listo Event State?
¿Está listo StateReplayFeed general?
```

---

## 3. Principio de una sola frontera nueva

La única frontera nueva admitida es:

```text
VALIDATED_BOUNDED_MARKET_STATE
        ↓
BoundedMarketStateAvailable
        ↓
MarketStateStore
        ↓
bounded consumer probe
```

Formalmente:

```text
ONE_NEW_BOUNDARY =
POINT_IN_TIME_MARKET_STATE_CONSUMER_AND_STORE

ONE_GATE =
ONE_PRIMARY_UNCERTAINTY
```

No se autoriza introducir simultáneamente:

```text
Event State;
estrategia;
Decision Model;
ML;
RL;
AlphaEvolve;
universo point-in-time;
stocks-in-play;
ejecución basada en estado;
selección de trades;
optimización;
validación de edge;
escalado histórico.
```

---

## 4. Evidencia provider que debe adoptarse

### 4.1 Handoff exterior

```text
PACKAGE =
market_state_pit_bt_gate_014_contract_handoff_v0_1_20260730T091041Z.zip

SHA-256 =
2c578ce9216bb3fd9010ef1f4afe8ba4022ab6b15f665d276a957f50acb35112

ZIP_ENTRIES =
18

DECLARED_ARTIFACTS =
17

PACKAGE_MANIFEST =
1
```

El ZIP exterior deberá conservarse byte por byte como evidencia inmutable.

### 4.2 Evidencia provider anidada

```text
NESTED_PROVIDER_EVIDENCE_PACKAGE =
bounded_state_bundle_read_and_replay_execution_and_review_v0_1_files_20260730T080831Z.zip

SHA-256 =
8f3d914becb3bc6d33f66814b355f636827db8cac67ea483fe9c6840b4fa16c7
```

La adopción local deberá verificar que el ZIP anidado contenido en el handoff exterior tiene exactamente esa identidad.

### 4.3 Artefactos de autoridad

```text
PHYSICAL_SCHEMA_CONTRACT.json SHA-256 =
595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b

market_state_core_four_scale_validation_physical_schema_binding_v0_1.json SHA-256 =
4006e80f099bb8abec147e33670294d7cc2eb565d25a10a08d6bf929c247f083

bounded_read_report.json SHA-256 =
4d994001798cfbf7e7eb860ce4606fb00524f9372428e70112dc658335e2dd00

provider execution final_manifest.json SHA-256 =
143f3e89eb82ec3461867e863814255613bafa72180529866d06351fe7e367ae

StateBundle manifest file SHA-256 =
0845642ba80fac75f0094bccd370db71157da2759cad7807885b2928d2d49ab0

StateBundle canonical SHA-256 =
0e9f7387acdf999a6e41f163ab16c3412c32cb545d1757cde4b5613572406be2
```

### 4.4 Hechos aceptados sin nueva lectura física

El backtester puede adoptar como evidencia provider:

```text
Parquet correcto identificado y abierto por el probe provider;
hash del Parquet verificado;
schema físico exacto de 40 columnas validado;
exactamente 2 filas físicas leídas;
2 materialized_state_candidate_id exactos observados;
state_output_fingerprint recalculado para ambas filas;
materialized_state_candidate_id recalculado para ambas filas;
join 1:1 con el sidecar temporal;
entrega solo cuando clock >= state_available_at_utc;
2 BoundedMarketStateAvailable de envolvente emitidos;
strategy_callbacks = 0;
signals = 0;
orders = 0;
fills = 0;
PnL = false;
production = false;
downstream = false.
```

No se podrá representar esta adopción como una ejecución propia del backtester.

---

## 5. Jerarquía de autoridad y resolución de hashes

La autoridad queda congelada así:

| Rol | Autoridad | SHA-256 / identidad | Uso permitido |
| --- | --- | --- | --- |
| Estructura física | `PHYSICAL_SCHEMA_CONTRACT.json` | `595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b` | Columnas, orden, tipo y nulabilidad |
| Procedencia histórica del perfil | Parquet de promoción Scale C | `b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2` | Provenance histórica solamente |
| Contenido runtime bounded actual | Parquet candidato runtime | `bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68` | Contenido físico de las dos filas para una futura autorización nueva |
| Dataset candidato | `market_state_candidate_dataset_scale_validation_v0_1_516a27d0f8f53762` | fingerprint `516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416` | Identidad del dataset candidato |
| Perfil lógico | `market_state_core_four_intraday_profile_v0_1` | profile fingerprint registrado en StateBundle | Semántica del core-four |

Invariantes:

```text
b1841f... != bc033c...

PROFILE_PROVENANCE_HASH =
NOT_RUNTIME_CONTENT_SELECTOR

RUNTIME_CONTENT_HASH =
bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68

STRUCTURAL_SCHEMA_HASH =
595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b

HASH_ROLE_SUBSTITUTION =
PROHIBITED
```

Ante una contradicción:

```text
binding machine-readable
        ↓
PHYSICAL_SCHEMA_CONTRACT for structure
        ↓
current runtime content authority for bytes
        ↓
profile provenance for history only
```

No se autoriza al consumidor a corregir o reinterpretar artifacts provider.

---

## 6. Scope bounded congelado

```text
STATE_KIND =
market_state

PROFILE_ID =
market_state_core_four_intraday_profile_v0_1

PHYSICAL_PROFILE_ID =
core_four_market_state_profile_v0_1

INSTRUMENT_ID =
cik_ticker:0001651625:ACIU

TICKER =
ACIU

SESSION_DATE =
2021-03-15

AUTHORIZED_ROW_COUNT =
2

MAXIMUM_PHYSICAL_DATA_FILES_FOR_FUTURE_RUN =
1
```

Filas exactas de evidencia:

| Contexto | `materialized_state_candidate_id` | `state_output_fingerprint` | `decision_timestamp_utc` | `state_available_at_utc` |
| --- | --- | --- | --- | --- |
| `scale_c_context_0058` | `f09492ac417d05161f70ee75f81e345a9cc315cef9beb9939d2df6ff3eb58dd3` | `f7c926be8e8bb6e84433061213bc554d54de2e03d0910a799e974ff5aea04617` | `2021-03-15T13:30:00Z` | `2021-03-15T13:30:00Z` |
| `scale_c_context_0115` | `26d923a282355ad242a5d91ad7d6183bed6a94842041ecf966ac70c366308c0e` | `2420034cb851629b48ee3216713b6bc1a337ce0a4356096575a3db1a91edb7bd` | `2021-03-15T20:00:00Z` | `2021-03-15T20:00:00Z` |

Restricciones exactas:

```text
candidate_runtime_only
not_official_dataset
no_downstream
no_production
```

Este scope no incluye:

```text
los otros 102 registros representados;
los 16 contextos no disponibles;
otros instrumentos;
otras sesiones;
otros perfiles;
otros objetos de información;
Event State.
```

---

## 7. Lo que el handoff no contiene

El handoff declara:

```text
physical_data_included = false
backtester_files_included = false
BT_GATE_014_physical_execution_authorized = false
```

Los dos eventos provider incluidos como evidencia contienen envolvente PIT, no los 17 valores científicos.

Por tanto:

```text
PROVIDER_ENVELOPE_EVIDENCE =
REAL_AND_ADOPTABLE

TYPED_CORE_FOUR_PHYSICAL_PAYLOAD_IN_HANDOFF =
ABSENT

PHYSICAL_TYPED_CONSUMER_VALIDATION =
NOT_YET_EXECUTED
```

Queda prohibido rellenar los payloads de las dos identidades físicas con valores inventados y presentarlos como evidencia real.

---

## 8. Fases del gate y autoridad de este contrato

### 8.1 Fase A — adopción y contrato

```text
PHASE_A =
LOCAL_GOVERNANCE_ADOPTION_AND_CONTRACT_ACCEPTANCE
```

Incluye:

```text
verificar hashes;
registrar evidencia;
registrar el cierre de BT-GATE-013;
abrir BT-GATE-014;
aceptar o devolver este contrato.
```

### 8.2 Fase B — implementación no física

Solo después de aceptar este contrato:

```text
PHASE_B =
BOUNDED_NON_PHYSICAL_IMPLEMENTATION

INPUT_DATA_CLASS =
SYNTHETIC_ONLY

PHYSICAL_MARKET_STATE_ROWS_READ =
0

IMPLEMENTATION_MODE =
CONTINUOUS_UNTIL_NON_PHYSICAL_ACCEPTANCE_PACKET,
UNLESS_A_MATERIAL_STOP_CONDITION_APPEARS
```

### 8.3 Fase C — solicitud de autorización física

Después de que Fase B pase:

```text
PHASE_C =
NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_REQUEST
```

La solicitud no constituye por sí misma autorización.

### 8.4 Fase D — ejecución física y aceptación final

Solo si existe una autorización nueva, explícita y válida:

```text
PHASE_D =
BOUNDED_PHYSICAL_CONSUMER_PROBE_AND_EXTERNAL_ACCEPTANCE
```

`BT-GATE-014` no puede cerrarse al terminar únicamente la Fase B.

---

## 9. Componentes lógicos obligatorios

La implementación deberá contener, como mínimo:

```text
BoundedMarketStateAvailable
PriceLocationStructurePayload
PriceMovementPayload
TradingActivityPayload
VolatilityRangeStatePayload
TypedCoreFourMarketStatePayload
MarketStateComponentAvailabilityEvidence
MarketStateAuditLineage
MarketStateStore
BoundedMarketStateConsumerProbe
StateAwareGlobalEventOrderV0_2
```

Los nombres físicos de módulos pueden adaptarse al layout aceptado del repositorio, pero los contratos lógicos y sus responsabilidades no pueden fusionarse de forma ambigua.

No deberá crearse un componente denominado:

```text
StateReplayFeed
```

porque el feed general de estados continúa cerrado.

---

## 10. Contrato de `BoundedMarketStateAvailable`

`BoundedMarketStateAvailable` deberá ser un tipo inmutable y distinto de:

```text
MarketDataBar1m
ReplayBarEvent
ReplayGapEvent
OrderIntent
Order
Fill
Position
```

Estructura conceptual:

```text
BoundedMarketStateAvailable
├── envelope PIT
├── TypedCoreFourMarketStatePayload
└── MarketStateAuditLineage
```

Contrato lógico:

```python
@dataclass(frozen=True)
class BoundedMarketStateAvailable:
    event_type: Literal["BoundedMarketStateAvailable"]
    state_kind: Literal["market_state"]
    profile_id: str
    state_schema_version: str
    physical_profile_id: str
    candidate_dataset_id: str
    candidate_dataset_fingerprint: str
    materialized_state_candidate_id: str
    state_output_fingerprint: str
    instrument_id: str
    ticker: str
    session_date: date
    decision_timestamp_utc: datetime
    state_as_of_utc: datetime
    state_available_at_utc: datetime
    state_availability_policy_id: str
    state_publication_latency_policy_id: str
    state_publication_latency: str
    state_replay_consumption_legality: str
    state_availability_status: str
    restriction_codes: tuple[str, ...]
    payload: TypedCoreFourMarketStatePayload
    audit_lineage: MarketStateAuditLineage
```

La firma anterior es normativa en semántica y tipado, no necesariamente en sintaxis literal.

No debe existir un campo genérico:

```text
payload: dict[str, Any]
```

como única representación operativa del core-four.

---

## 11. Payload científico tipado core-four

### 11.1 Regla general

```text
SCIENTIFIC_VALUE_COUNT =
17

PHYSICAL_TYPE =
double / IEEE-754 float64

NULLABLE =
false

SILENT_ROUNDING =
PROHIBITED

UNIT_RESCALE =
PROHIBITED

PERCENT_RATIO_REINTERPRETATION =
PROHIBITED
```

Todos los valores deberán ser finitos:

```text
NaN = PROHIBITED
+Infinity = PROHIBITED
-Infinity = PROHIBITED
```

### 11.2 `PriceLocationStructurePayload` — 5 valores

| Campo tipado | Columna física exacta | Tipo |
| --- | --- | --- |
| `daily_open_price` | `price_location_structure__daily_open_price` | `float64` |
| `daily_prior_close` | `price_location_structure__daily_prior_close` | `float64` |
| `intraday_bar_close_price` | `price_location_structure__intraday_bar_close_price` | `float64` |
| `intraday_return_vs_prior_close_ratio_as_location` | `price_location_structure__intraday_return_vs_prior_close_ratio_as_location` | `float64` |
| `intraday_return_vs_session_open_ratio_as_location` | `price_location_structure__intraday_return_vs_session_open_ratio_as_location` | `float64` |

### 11.3 `PriceMovementPayload` — 5 valores

| Campo tipado | Columna física exacta | Tipo |
| --- | --- | --- |
| `daily_gap_pct` | `price_movement__daily_gap_pct` | `float64` |
| `daily_prior_close` | `price_movement__daily_prior_close` | `float64` |
| `intraday_bar_close_price` | `price_movement__intraday_bar_close_price` | `float64` |
| `intraday_return_vs_prior_close_ratio` | `price_movement__intraday_return_vs_prior_close_ratio` | `float64` |
| `intraday_return_vs_session_open_ratio` | `price_movement__intraday_return_vs_session_open_ratio` | `float64` |

### 11.4 `TradingActivityPayload` — 4 valores

| Campo tipado | Columna física exacta | Tipo |
| --- | --- | --- |
| `session_volume_to_time_over_prior_20_full_session_volume_mean` | `trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean` | `float64` |
| `daily_volume_20d_avg` | `trading_activity__daily_volume_20d_avg` | `float64` |
| `intraday_bar_volume` | `trading_activity__intraday_bar_volume` | `float64` |
| `intraday_session_volume_to_time` | `trading_activity__intraday_session_volume_to_time` | `float64` |

### 11.5 `VolatilityRangeStatePayload` — 3 valores

| Campo tipado | Columna física exacta | Tipo |
| --- | --- | --- |
| `intraday_high_so_far` | `volatility_range_state__intraday_high_so_far` | `float64` |
| `intraday_low_so_far` | `volatility_range_state__intraday_low_so_far` | `float64` |
| `intraday_range_so_far_ratio` | `volatility_range_state__intraday_range_so_far_ratio` | `float64` |

### 11.6 Contenedor

```python
@dataclass(frozen=True)
class TypedCoreFourMarketStatePayload:
    price_location_structure: PriceLocationStructurePayload
    price_movement: PriceMovementPayload
    trading_activity: TradingActivityPayload
    volatility_range_state: VolatilityRangeStatePayload
```

No se permite:

```text
añadir objetos fuera del core-four;
eliminar uno de los cuatro objetos;
renombrar columnas físicas antes de validar fingerprints;
convertir `daily_gap_pct` por intuición;
deduplicar campos científicamente parecidos;
usar uno de los campos de precio como fill price.
```

La duplicación aparente de precios entre objetos es parte del schema provider y deberá conservarse.

---

## 12. Envolvente física y mapping de las 40 columnas

Las 40 columnas físicas deberán quedar consumidas exactamente una vez por el adapter futuro:

```text
9 columnas -> envelope
17 columnas -> payload científico tipado
14 columnas -> audit lineage
total = 40
```

### 12.1 Columnas físicas asignadas al envelope — 9

| Columna física | Destino |
| --- | --- |
| `materialized_state_candidate_id` | `event.materialized_state_candidate_id` |
| `state_profile_id` | `event.profile_id` |
| `state_schema_version` | `event.state_schema_version` |
| `instrument_id` | `event.instrument_id` |
| `ticker` | `event.ticker` |
| `session_date` | `event.session_date` |
| `decision_timestamp_utc` | `event.decision_timestamp_utc` |
| `restriction_codes_json` | una sola operación de mapping hacia `event.restriction_codes` y su representación raw de auditoría |
| `state_output_fingerprint` | `event.state_output_fingerprint` |

### 12.2 Columnas físicas asignadas al payload — 17

Son exactamente las columnas enumeradas en la sección 11.

### 12.3 Columnas físicas asignadas a audit lineage — 14

| Columna física | Destino |
| --- | --- |
| `materialization_run_id` | `audit_lineage.materialization_run_id` |
| `source_integration_run_id` | `audit_lineage.source_integration_run_id` |
| `source_candidate_record_id` | `audit_lineage.source_candidate_record_id` |
| `source_integration_profile_id` | `audit_lineage.source_integration_profile_id` |
| `decision_case` | `audit_lineage.decision_case` |
| `context_id` | `audit_lineage.context_id` |
| `integration_status` | `audit_lineage.integration_status` |
| `object_completeness_status` | `audit_lineage.object_completeness_status` |
| `quality_status` | `audit_lineage.quality_status` |
| `calendar_version` | `audit_lineage.calendar_version` |
| `source_lineage_json` | raw + parse validado en `audit_lineage` |
| `policy_versions_json` | raw + parse validado en `audit_lineage` |
| `formula_versions_json` | raw + parse validado en `audit_lineage` |
| `context_input_fingerprint` | `audit_lineage.context_input_fingerprint` |

### 12.4 Regla de exhaustividad

La implementación deberá generar una matriz ejecutable:

```text
PHYSICAL_COLUMNS_DECLARED = 40
PHYSICAL_COLUMNS_MAPPED = 40
UNMAPPED_COLUMNS = []
DUPLICATELY_MAPPED_COLUMNS = []
UNDECLARED_COLUMNS = []
```

Fallos:

```text
FAIL_MARKET_STATE_SCHEMA_COLUMN_COUNT
FAIL_MARKET_STATE_SCHEMA_ORDER
FAIL_MARKET_STATE_SCHEMA_NAME
FAIL_MARKET_STATE_SCHEMA_TYPE
FAIL_MARKET_STATE_SCHEMA_NULLABILITY
FAIL_MARKET_STATE_UNMAPPED_PHYSICAL_COLUMN
FAIL_MARKET_STATE_DUPLICATE_COLUMN_MAPPING
```

---

## 13. `MarketStateAuditLineage`

`MarketStateAuditLineage` deberá preservar información suficiente para reconstruir:

```text
qué dataset produjo el estado;
qué schema gobernó la fila;
qué fila candidata fue consumida;
qué sidecar la hizo temporalmente observable;
qué políticas y fórmulas fueron aplicadas;
qué evidencia provider fue adoptada;
qué restricciones permanecen vigentes.
```

Contrato mínimo:

```python
@dataclass(frozen=True)
class MarketStateAuditLineage:
    materialization_run_id: str
    source_integration_run_id: str
    source_candidate_record_id: str
    source_integration_profile_id: str
    decision_case: str
    context_id: str
    integration_status: str
    object_completeness_status: str
    quality_status: str
    calendar_version: str
    context_input_fingerprint: str
    source_lineage_raw_json: str
    source_lineage: Mapping[str, Any]
    policy_versions_raw_json: str
    policy_versions: Mapping[str, Any]
    formula_versions_raw_json: str
    formula_versions: Mapping[str, Any]
    restriction_codes_raw_json: str
    component_availability_evidence: tuple[MarketStateComponentAvailabilityEvidence, ...]
    provider_handoff_sha256: str
    nested_provider_evidence_sha256: str
    structural_schema_sha256: str
    current_runtime_content_sha256: str
    state_bundle_ref_id: str
    state_bundle_canonical_sha256: str
    sidecar_id: str
    sidecar_schema_id: str
    sidecar_sha256: str
    binding_id: str
    binding_sha256: str
```

Los JSON físicos deberán:

```text
ser strings UTF-8 válidos;
parsear sin error;
tener el tipo raíz esperado;
conservarse sin reescritura para fingerprint;
exponerse solo como linaje/política/fórmula, no como features libres.
```

`restriction_codes_json` deberá conservarse como string raw para reproducir el fingerprint y, dentro de la misma operación de mapping, parsearse hacia la tupla operativa validada. Esto no crea dos autoridades: el raw gobierna la reproducción física y la tupla gobierna las comprobaciones del consumidor.

No se permite promover automáticamente cualquier clave encontrada dentro de esos JSON a input operativo.

---

## 14. Sidecar temporal y join 1:1

Los campos siguientes proceden del sidecar, no de las 40 columnas físicas:

```text
physical_profile_id
candidate_dataset_id
candidate_dataset_fingerprint
state_as_of_utc
state_available_at_utc
state_availability_policy_id
state_publication_latency_policy_id
state_publication_latency
state_availability_status
component_availability_evidence
state_replay_consumption_legality
restriction_codes
```

Clave gobernada del join:

```text
materialized_state_candidate_id
```

Regla:

```text
ONE_PHYSICAL_ROW =
EXACTLY_ONE_SIDECAR_RECORD

ONE_SIDECAR_RECORD =
AT_MOST_ONE_AUTHORIZED_PHYSICAL_ROW
```

Validaciones obligatorias entre fila y sidecar:

```text
materialized_state_candidate_id equal;
state_output_fingerprint equal;
state_profile_id == profile_id;
source_candidate_record_id equal;
instrument_id equal;
ticker equal;
session_date equal;
context_id equal;
decision_timestamp_utc equal;
candidate_dataset_id equal to frozen dataset;
candidate_dataset_fingerprint equal to frozen fingerprint.
```

Fallos:

```text
FAIL_MARKET_STATE_SIDECAR_MISSING
FAIL_MARKET_STATE_SIDECAR_DUPLICATE
FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH
FAIL_MARKET_STATE_SIDECAR_FINGERPRINT_MISMATCH
FAIL_MARKET_STATE_SIDECAR_SCOPE_MISMATCH
```

El código de join puede implementarse y probarse en Fase B con fixtures sintéticos. El join con las dos filas físicas queda reservado a Fase D.

---

## 15. Contrato temporal point-in-time

### 15.1 Instantes distintos

```text
decision_timestamp_utc =
instante de mercado representado por la fila de estado

state_as_of_utc =
máximo timestamp de información fuente incorporada

state_available_at_utc =
primer instante histórico en que la fila completa puede entregarse legalmente

event_loop_clock_utc =
instante del reloj simulado durante el dispatch

consumer_observation_timestamp_utc =
instante en que el probe obtiene el estado desde MarketStateStore
```

No deberán colapsarse en un único timestamp.

### 15.2 Derivación upstream adoptada

```text
state_as_of_utc =
max(component_as_of_utc for admitted required components)

state_available_at_utc =
max(
  decision_timestamp_utc,
  component_available_at_utc for admitted required components
)
+ governed_state_publication_latency
```

Para este scope bounded:

```text
state_publication_latency_policy_id =
zero_latency_candidate_replay_publication_policy_v0_1

state_publication_latency =
PT0S
```

`PT0S` solo es legal con esa política exacta.

### 15.3 Invariantes

Para la fila:

```text
state_as_of_utc <= decision_timestamp_utc
decision_timestamp_utc <= state_available_at_utc
state_as_of_utc <= state_available_at_utc
```

Para cada componente:

```text
source_timestamp_utc <= component_as_of_utc
component_as_of_utc <= decision_timestamp_utc
component_as_of_utc <= component_available_at_utc
component_available_at_utc <= state_available_at_utc
```

Para entrega y observación:

```text
event_loop_clock_utc >= state_available_at_utc
consumer_observation_timestamp_utc >= state_available_at_utc
```

### 15.4 Fuentes prohibidas para disponibilidad

```text
parquet_created_at
runtime_invocation_created_at
bundle_created_at
file_modified_at
package timestamp
human review timestamp
wall clock of the test
```

### 15.5 Tiempo canónico

```text
INTERNAL_TIME_STANDARD =
UTC

CANONICAL_SERIALIZATION =
YYYY-MM-DDTHH:MM:SS[.ffffff]Z

NAIVE_DATETIME =
PROHIBITED

HOST_LOCAL_TIME_DEPENDENCE =
PROHIBITED
```

---

## 16. Orden global a igualdad de timestamp

`BT-GATE-014` extiende el orden aceptado sin cambiar la relación previa entre gaps y barras.

```text
GLOBAL_REPLAY_ORDER_V0_1
Gap priority = 0
Bar priority = 1
```

Extensión:

```text
STATE_AWARE_GLOBAL_EVENT_ORDER_V0_2

ReplayGapEvent priority = 0
ReplayBarEvent priority = 1
BoundedMarketStateAvailable priority = 2
```

Clave canónica:

```text
(
  available_at_utc,
  session_date,
  event_priority,
  canonical_ticker,
  source_event_identity
)
```

El resolver deberá usar un accessor explícito por tipo:

```text
ReplayGapEvent.available_at
ReplayBarEvent.available_at
BoundedMarketStateAvailable.state_available_at_utc
```

No se exige introducir un segundo timestamp ambiguo denominado `available_at` dentro del evento de estado. El resolver global transforma cada tipo a la única semántica `available_at_utc` utilizada por la clave.

Identidad del evento de estado:

```text
source_event_identity =
materialized_state_candidate_id
```

Precedencia vinculante:

```text
source bar closed and incorporated
        ↓
Market State becomes eligible
        ↓
Market State validated
        ↓
Market State stored
        ↓
bounded consumer probe may observe it
```

El store y la observación son fases del dispatch del evento de estado, no eventos que puedan reordenarse alfabéticamente.

Reglas:

```text
EVENT_TYPE_ALPHABETICAL_ORDER =
PROHIBITED

FILESYSTEM_ENUMERATION_ORDER =
PROHIBITED

INSERTION_ORDER_AS_TIE_BREAKER =
PROHIBITED

UNRESOLVED_TIE =
FAIL_CLOSED
```

Si no existe una barra del consumidor con el mismo timestamp, el consumidor no deberá inventarla. El phase barrier significa que todas las barras legalmente entregables hasta ese instante se procesan antes del estado. Una dependencia física concreta solo podrá exigirse si está declarada en el linaje.

---

## 17. `MarketStateStore`

### 17.1 Separación

```text
MarketStateStore != MarketData
MarketStateStore != HistoricalReplayFeed
MarketStateStore != StateReplayFeed
MarketStateStore != ExecutionSimulator
MarketStateStore != Portfolio valuation store
```

### 17.2 Mutabilidad

```text
STORE_RECORDS =
IMMUTABLE

IN_PLACE_UPDATE =
PROHIBITED

DELETE_DURING_RUN =
PROHIBITED

OVERWRITE =
PROHIBITED
```

### 17.3 Claves

Clave primaria:

```text
materialized_state_candidate_id
```

Clave lógica secundaria:

```text
(
  profile_id,
  instrument_id,
  decision_timestamp_utc
)
```

No se permiten dos estados distintos bajo la misma clave lógica dentro del scope bounded.

### 17.4 Inserción

Un estado solo puede insertarse cuando:

```text
event validated = true
clock >= state_available_at_utc
legality = decision_safe
availability_status = available_for_decision_replay
core-four complete = true
restrictions propagated = true
```

La inserción debe ser atómica: ningún query puede observar una fila parcialmente validada.

### 17.5 Queries admitidos en este gate

```text
get_exact(materialized_state_candidate_id, observed_at_utc)

latest_visible(
  profile_id,
  instrument_id,
  decision_timestamp_utc,
  observed_at_utc
)
```

Condición de visibilidad:

```text
state_available_at_utc <= observed_at_utc
state_as_of_utc <= decision_timestamp_utc
stored_at_utc <= observed_at_utc
```

`latest_visible` deberá ordenar por:

```text
(
  decision_timestamp_utc,
  state_available_at_utc,
  materialized_state_candidate_id
)
```

y tomar el máximo legal, nunca el registro más cercano en tiempo absoluto.

### 17.6 Fallbacks prohibidos

```text
future state fallback
nearest timestamp fallback
different instrument fallback
ticker-only fallback
different profile fallback
previous session implicit fallback
restriction-dropping fallback
```

---

## 18. Consumer probe

El único consumidor autorizado en este gate es:

```text
BoundedMarketStateConsumerProbe
```

Puede verificar:

```text
presencia del evento;
tipo del payload;
17 valores presentes;
cuatro objetos presentes;
identidad;
fingerprints;
timestamps;
restricciones;
linaje;
visibilidad legal;
orden de store/observation;
determinismo.
```

No puede:

```text
tomar decisiones de trading;
generar features nuevas;
comparar resultados económicos;
crear señales;
crear órdenes;
crear fills;
actualizar posiciones;
actualizar cash;
actualizar equity;
calcular PnL.
```

La observación deberá producir un recibo mínimo, no una decisión:

```text
probe_observation_id
event_sequence
observed_at_utc
materialized_state_candidate_id
state_output_fingerprint
typed_payload_field_count = 17
restriction_codes
store_insert_sequence
visibility_status
```

---

## 19. Separación respecto a MarketData, ejecución y valoración

Aunque el payload contiene campos con nombres de precio:

```text
daily_open_price
daily_prior_close
intraday_bar_close_price
intraday_high_so_far
intraday_low_so_far
```

su función en este gate es representación científica, no ejecución.

Invariantes:

```text
MARKET_STATE_IS_MARKET_DATA =
false

MARKET_STATE_SUPPLIES_EXECUTION_PRICE =
false

MARKET_STATE_TRIGGERS_FILL =
false

MARKET_STATE_UPDATES_VALUATION_PRICE =
false

MARKET_STATE_CREATES_ORDER =
false

MARKET_STATE_CREATES_TRADE =
false

MARKET_STATE_UPDATES_POSITION =
false

MARKET_STATE_UPDATES_CASH =
false

MARKET_STATE_UPDATES_EQUITY =
false
```

Protección estructural obligatoria:

```text
BoundedMarketStateAvailable
must not inherit from MarketDataBar1m

execution simulator input union
must not include BoundedMarketStateAvailable

valuation handler input union
must not include BoundedMarketStateAvailable

order evaluation handler
must not be invoked by BoundedMarketStateAvailable
```

No basta con que el fixture positivo no genere órdenes; deberá existir un test negativo que demuestre que el routing hacia ejecución falla cerrado.

---

## 20. Legalidad, completitud y restricciones

Valores admitidos por el contrato temporal provider:

```text
decision_safe
research_only
blocked_missing_availability_evidence
blocked_temporal_leakage
blocked_required_object_missing
blocked_restriction_propagation_missing
```

Este gate bounded solo admite inserción operativa para:

```text
state_replay_consumption_legality =
decision_safe

state_availability_status =
available_for_decision_replay
```

Los cuatro objetos requeridos deberán aparecer exactamente una vez en `component_availability_evidence`:

```text
price_location_structure
price_movement
trading_activity
volatility_range_state
```

Restricciones bounded exactas y ordenadas:

```text
(
  candidate_runtime_only,
  not_official_dataset,
  no_downstream,
  no_production
)
```

La igualdad de dominios que figuraba en esta sección queda
`SUPERSEDED_BY_MARKET_STATE_RESTRICTION_DOMAIN_BINDING_CLARIFICATION_V0_1`.

Autoridad normativa adoptada:

```text
binding_id =
market_state_restriction_domain_binding_clarification_v0_1

binding_sha256 =
b3ebace6fab7cb0a690be165f0a1706a5906dc7a729488fa1139af00c02e53a9
```

Deberá cumplirse:

```text
physical_provenance_restriction_codes
= physical restriction_codes_json exacto
= lineage y fingerprint físico, nunca policy ejecutable

replay_consumption_restriction_codes
= conjunto bounded exacto de sidecar/bundle/autorización
= policy que gobierna la entrega

component_replay_restriction_codes
= restricciones etiquetadas por componente
⊆ replay_consumption_restriction_codes

union(component_replay_restriction_codes)
⊆ replay_consumption_restriction_codes

physical_provenance_restriction_codes
MUST_NOT_BE_COMPARED_FOR_EQUALITY_WITH
replay_consumption_restriction_codes

UNLABELED_EXECUTABLE_RESTRICTION_UNION = PROHIBITED
```

No se permite:

```text
eliminar una restricción;
renombrarla;
traducirla;
tratar candidate_runtime_only como official;
tratar no_downstream como autorización interna implícita;
tratar decision_safe como autorización de estrategia.
```

---

## 21. Fingerprints y canonicalización

### 21.1 Regla crítica

Los fingerprints físicos deberán recalcularse sobre los nombres y valores físicos antes de construir el payload anidado.

```text
FINGERPRINT_FROM_RENAMED_TYPED_PAYLOAD =
PROHIBITED
```

### 21.2 Canonical JSON

```text
encoding = utf-8
ensure_ascii = true
sort_keys = true
separators = (",", ":")
hash = SHA-256
```

Normalización:

```text
datetime -> UTC ISO-8601 con sufijo Z
date -> YYYY-MM-DD
string -> sin transformación semántica
double -> valor físico sin rounding ni rescale
JSON physical strings -> raw string original
```

### 21.3 `state_output_fingerprint`

Los 35 campos físicos, en autoridad nominal, son:

```text
state_profile_id
state_schema_version
source_integration_profile_id
instrument_id
ticker
session_date
decision_timestamp_utc
decision_case
context_id
integration_status
object_completeness_status
quality_status
price_location_structure__daily_open_price
price_location_structure__daily_prior_close
price_location_structure__intraday_bar_close_price
price_location_structure__intraday_return_vs_prior_close_ratio_as_location
price_location_structure__intraday_return_vs_session_open_ratio_as_location
price_movement__daily_gap_pct
price_movement__daily_prior_close
price_movement__intraday_bar_close_price
price_movement__intraday_return_vs_prior_close_ratio
price_movement__intraday_return_vs_session_open_ratio
trading_activity__session_volume_to_time_over_prior_20_full_session_volume_mean
trading_activity__daily_volume_20d_avg
trading_activity__intraday_bar_volume
trading_activity__intraday_session_volume_to_time
volatility_range_state__intraday_high_so_far
volatility_range_state__intraday_low_so_far
volatility_range_state__intraday_range_so_far_ratio
calendar_version
source_lineage_json
policy_versions_json
formula_versions_json
restriction_codes_json
context_input_fingerprint
```

### 21.4 `materialized_state_candidate_id`

Inputs:

```text
state_profile_id
state_schema_version
instrument_id
decision_timestamp_utc
context_input_fingerprint
recalculated state_output_fingerprint
```

### 21.5 Fase sintética

Los fixtures sintéticos deberán generar fingerprints sintéticos propios mediante el mismo algoritmo.

No deberán:

```text
copiar un state_output_fingerprint físico;
copiar un materialized_state_candidate_id físico;
combinar un fingerprint físico con un payload sintético.
```

---

## 22. Dos clases de fixture estrictamente separadas

### 22.1 Evidencia de envolvente provider

```text
FIXTURE_CLASS =
PROVIDER_EVIDENCE_ENVELOPE_ONLY

REAL_IDENTITIES =
allowed

SCIENTIFIC_PAYLOAD =
absent

PURPOSE =
governance adoption and envelope assertions only
```

Puede contener los dos IDs, fingerprints y timestamps reales ya publicados.

### 22.2 Fixture consumidor sintético

```text
FIXTURE_CLASS =
SYNTHETIC_TYPED_MARKET_STATE

PHYSICAL_DATA =
false

REAL_ROW_IDS =
false

REAL_STATE_FINGERPRINTS =
false

PURPOSE =
typed consumer implementation tests only
```

Debe usar identidades inequívocamente sintéticas, por ejemplo:

```text
instrument_id = synthetic:bt_gate_014:instrument_001
ticker = SYNTH
context_id = synthetic_context_001
materialized_state_candidate_id = hash derived from synthetic payload
```

Cada fixture deberá declarar:

```text
synthetic = true
physical_source_rows = 0
provider_parquet_opened = false
not_provider_evidence = true
not_scientific_observation = true
```

No se permite una tercera clase híbrida.

---

## 23. Integridad y protección frente a mutación

### 23.1 Adopción provider

Los dos ZIP deberán:

```text
hashearse antes de adopción;
copiarse sin modificación;
hashearse después de adopción;
registrar tamaño;
registrar ruta relativa portable;
resolver el hash del ZIP anidado.
```

### 23.2 Inputs sintéticos

Todo fixture o configuración que afecte el run deberá:

```text
tener SHA-256;
tener tamaño;
ser leído con hash-before/hash-after;
fallar si muta durante lectura.
```

### 23.3 Rutas

```text
ABSOLUTE_PATH_IN_SCIENTIFIC_IDENTITY =
PROHIBITED

TEMPORARY_DIRECTORY_IN_SCIENTIFIC_HASH =
PROHIBITED

INSTALLATION_PATH_IN_SCIENTIFIC_HASH =
PROHIBITED
```

---

## 24. Contrato del run sintético

El run positivo de Fase B deberá integrar:

```text
al menos 2 ReplayBarEvent sintéticos;
al menos 2 BoundedMarketStateAvailable sintéticos;
al menos una igualdad de available_at entre barra y estado;
orden de input deliberadamente no canónico;
MarketStateStore vacío al inicio;
consumer probe activo;
strategy callbacks desactivados;
execution desactivada;
accounting desactivado.
```

Resultado mínimo:

```text
market_data_events_processed >= 2
market_state_events_received >= 2
market_state_events_validated = 2
market_state_store_inserts = 2
consumer_probe_observations = 2
early_observations = 0
strategy_callbacks = 0
signals_emitted = 0
orders_emitted = 0
fills_emitted = 0
positions_mutated = 0
cash_mutations = 0
equity_mutations = 0
PnL_calculated = false
physical_data_files_opened = 0
physical_state_rows_read = 0
```

---

## 25. Pruebas positivas obligatorias

```text
POSITIVE_01:
outer handoff hash and nested provider hash resolve exactly

POSITIVE_02:
40 physical columns partition into 9 envelope + 17 payload + 14 lineage

POSITIVE_03:
all four typed payload objects exist with exactly 17 float64 values

POSITIVE_04:
synthetic raw row fingerprint and candidate id recalculate exactly

POSITIVE_05:
synthetic physical-shaped row joins exactly one synthetic sidecar record

POSITIVE_06:
event is not visible when clock < state_available_at_utc

POSITIVE_07:
event becomes eligible when clock == state_available_at_utc

POSITIVE_08:
equal-timestamp ReplayBarEvent is incorporated before Market State

POSITIVE_09:
store insert precedes probe observation

POSITIVE_10:
get_exact returns the correct immutable state

POSITIVE_11:
latest_visible returns only the latest legally visible state

POSITIVE_12:
restrictions and component evidence survive serialization round-trip

POSITIVE_13:
input permutation produces the same canonical event sequence

POSITIVE_14:
two clean roots produce the same scientific hashes

POSITIVE_15:
all prohibited operational counters remain exactly zero
```

---

## 26. Pruebas negativas obligatorias

### 26.1 Autoridad y schema

```text
NEGATIVE_01:
outer handoff byte changed
-> FAIL_PROVIDER_HANDOFF_HASH_MISMATCH

NEGATIVE_02:
nested provider evidence byte changed
-> FAIL_NESTED_PROVIDER_EVIDENCE_HASH_MISMATCH

NEGATIVE_03:
b1841f... supplied as runtime content authority
-> FAIL_MARKET_STATE_HASH_ROLE_SUBSTITUTION

NEGATIVE_04:
physical column missing, extra, reordered, mistyped or nullable drift
-> FAIL_MARKET_STATE_PHYSICAL_SCHEMA_MISMATCH

NEGATIVE_05:
one physical column unmapped or mapped twice
-> FAIL_MARKET_STATE_COLUMN_MAPPING_NOT_BIJECTIVE
```

### 26.2 Payload y JSON

```text
NEGATIVE_06:
one of the 17 values absent or null
-> FAIL_MARKET_STATE_CORE_FOUR_INCOMPLETE

NEGATIVE_07:
NaN or infinity in a scientific value
-> FAIL_MARKET_STATE_NON_FINITE_VALUE

NEGATIVE_08:
source_lineage_json, policy_versions_json, formula_versions_json
or restriction_codes_json invalid
-> FAIL_MARKET_STATE_INVALID_EMBEDDED_JSON

NEGATIVE_09:
payload represented only as untyped dict
-> FAIL_MARKET_STATE_TYPED_PAYLOAD_REQUIRED
```

### 26.3 Join, identidad y fingerprint

```text
NEGATIVE_10:
zero sidecar records for a row
-> FAIL_MARKET_STATE_SIDECAR_MISSING

NEGATIVE_11:
two sidecar records for a row
-> FAIL_MARKET_STATE_SIDECAR_DUPLICATE

NEGATIVE_12:
row and sidecar disagree on identity, scope or timestamp
-> FAIL_MARKET_STATE_SIDECAR_IDENTITY_MISMATCH

NEGATIVE_13:
state_output_fingerprint mismatch
-> FAIL_MARKET_STATE_OUTPUT_FINGERPRINT_MISMATCH

NEGATIVE_14:
materialized_state_candidate_id mismatch
-> FAIL_MARKET_STATE_CANDIDATE_ID_MISMATCH
```

### 26.4 Tiempo y legalidad

```text
NEGATIVE_15:
naive or non-canonical UTC timestamp
-> FAIL_MARKET_STATE_TIMESTAMP_NOT_CANONICAL_UTC

NEGATIVE_16:
state_as_of_utc > decision_timestamp_utc
-> FAIL_MARKET_STATE_TEMPORAL_LEAKAGE

NEGATIVE_17:
component timestamp ordering violated
-> FAIL_MARKET_STATE_COMPONENT_TEMPORAL_ORDER

NEGATIVE_18:
clock < state_available_at_utc
-> event not delivered and store unchanged

NEGATIVE_19:
PT0S with any other latency policy
-> FAIL_MARKET_STATE_ZERO_LATENCY_POLICY

NEGATIVE_20:
legality != decision_safe or availability_status != available_for_decision_replay
-> FAIL_MARKET_STATE_NOT_DECISION_SAFE
```

### 26.5 Completitud y restricciones

```text
NEGATIVE_21:
one required core-four component absent or duplicated
-> FAIL_MARKET_STATE_COMPONENT_SET

NEGATIVE_22:
component is research_only or blocked while row is decision_safe
-> FAIL_MARKET_STATE_COMPONENT_LEGALITY_CONTRADICTION

NEGATIVE_23:
physical, sidecar or component restrictions disagree
-> FAIL_MARKET_STATE_RESTRICTION_PROPAGATION
```

### 26.6 Orden y store

```text
NEGATIVE_24:
Market State ordered before equal-timestamp ReplayBarEvent
-> FAIL_MARKET_STATE_EQUAL_TIMESTAMP_PRIORITY

NEGATIVE_25:
probe observes before atomic store insert
-> FAIL_MARKET_STATE_OBSERVATION_BEFORE_STORE

NEGATIVE_26:
exact duplicate primary id
-> FAIL_DUPLICATE_MARKET_STATE_EVENT

NEGATIVE_27:
different id for same logical secondary key
-> FAIL_CONFLICTING_MARKET_STATE_EVENT

NEGATIVE_28:
future, cross-instrument or cross-profile fallback query
-> no result and store unchanged
```

### 26.7 Fronteras operativas

```text
NEGATIVE_29:
Market State routed to execution or valuation
-> FAIL_MARKET_STATE_OPERATIONAL_ROUTING_PROHIBITED

NEGATIVE_30:
Event State supplied to bounded consumer
-> FAIL_EVENT_STATE_NOT_AUTHORIZED

NEGATIVE_31:
physical provider Parquet open attempted in Fase B
-> FAIL_BT_GATE_014_PHYSICAL_READ_NOT_AUTHORIZED

NEGATIVE_32:
fixture combines real provider id/fingerprint with synthetic payload
-> FAIL_HYBRID_MARKET_STATE_FIXTURE_PROHIBITED

NEGATIVE_33:
absolute root changes between clean runs
-> PASS_WITH_IDENTICAL_SCIENTIFIC_HASHES
```

Cada test deberá comprobar el código o comportamiento exacto; una excepción genérica no es evidencia suficiente.

---

## 27. Determinismo

Se requieren dos ejecuciones desde raíces absolutas diferentes:

```text
CLEAN_SYNTHETIC_RUN_A
CLEAN_SYNTHETIC_RUN_B
```

Deberá cumplirse:

```text
resolved_input_content_hash_A =
resolved_input_content_hash_B

synthetic_fixture_hash_A =
synthetic_fixture_hash_B

typed_event_sequence_hash_A =
typed_event_sequence_hash_B

store_trace_hash_A =
store_trace_hash_B

probe_observation_hash_A =
probe_observation_hash_B

boundary_report_hash_A =
boundary_report_hash_B

scientific_manifest_hash_A =
scientific_manifest_hash_B

deterministic_output_hash_A =
deterministic_output_hash_B
```

Campos excluidos del hash científico mediante lista cerrada:

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

Deberán distinguirse:

```text
ARTIFACT_BYTE_SHA256 =
integridad exacta del archivo

SCIENTIFIC_CONTENT_SHA256 =
hash de contenido JSON canónico
```

Los JSON del run deberán escribirse con LF y UTF-8 para reducir diferencias de plataforma. La autoridad científica seguirá siendo el contenido canónico, no los saltos de línea.

---

## 28. Artefactos obligatorios de Fase B

La implementación no física deberá producir:

```text
provider_handoff_adoption_record.json
market_state_physical_column_mapping.json
bounded_market_state_event_schema.json
typed_core_four_payload_schema.json
market_state_audit_lineage_schema.json
market_state_store_contract.json
synthetic_fixture_manifest.json
synthetic_raw_rows.json
synthetic_sidecar.json
resolved_input_manifest.json
state_aware_event_sequence.json
market_state_validation_report.json
market_state_store_trace.json
bounded_consumer_probe_observations.json
negative_derivative_report.json
boundary_preservation_report.json
determinism_report.json
final_manifest.json
```

El paquete deberá incluir código y tests, pero no:

```text
provider Parquet;
copias de las dos filas físicas;
payloads físicos;
Event State;
orders;
fills;
trades;
cash ledger;
positions;
equity curve;
performance summary;
PnL.
```

---

## 29. `final_manifest` no físico

Campos mínimos:

```text
gate_id
gate_name
contract_version
implementation_phase
provider_handoff_package_name
provider_handoff_sha256
nested_provider_evidence_package_name
nested_provider_evidence_sha256
structural_schema_sha256
profile_provenance_sha256
current_runtime_content_sha256
state_bundle_ref_id
state_bundle_canonical_sha256
profile_id
state_schema_version
physical_column_count
scientific_payload_field_count
synthetic_fixture_class
synthetic_record_count
physical_data_files_opened
physical_state_rows_read
market_state_events_received
market_state_store_inserts
consumer_probe_observations
early_observations
strategy_callbacks
signals_emitted
orders_emitted
fills_emitted
positions_mutated
cash_mutations
equity_mutations
PnL_calculated
positive_case_count
negative_case_count
failed_case_count
output_artifact_hashes
scientific_manifest_hash
deterministic_output_hash
boundary_preservation_status
validation_status
next_required_authorization
```

Estado permitido al completar Fase B:

```text
CONSUMER_CONTRACT =
IMPLEMENTED

SYNTHETIC_CONSUMER_TESTS =
PASS

PHYSICAL_CONSUMER_READ =
NOT_EXECUTED

PHYSICAL_CONSUMER_EVIDENCE =
NOT_YET_PRODUCED

BT-GATE-014 =
IMPLEMENTED_PENDING_NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION
```

No se permite declarar:

```text
BT-GATE-014 = CLOSED_PASS
```

solo con tests sintéticos.

---

## 30. Preservación de governance

La adopción local deberá actualizar de forma coherente:

```text
canonical contract inventory;
decision ledger;
policy register;
traceability matrix;
gate register;
governance validation report;
backtester README;
backtester AGENTS handoff;
backtester CHANGELOG;
CTO backtest-engine living surfaces affected by the gate.
```

Deberá registrar:

```text
BT-GATE-013 closed and accepted;
provider handoff adopted by exact hash;
BT-GATE-014 opened only for bounded non-physical implementation;
physical execution not authorized;
Event State not open;
StateReplayFeed general not authorized.
```

Los documentos históricos no deberán reescribirse para aparentar que `Market State` estaba autorizado durante gates anteriores.

El documento histórico:

```text
STATE_PROVIDER_CONSUMER_HOLD_HANDOFF_V0_1
```

deberá mantenerse como snapshot histórico. Governance podrá marcar su hold como superado únicamente para:

```text
BT-GATE-014 bounded contract
AND
BT-GATE-014 non-physical synthetic implementation
```

No deberá interpretarse como superación general del hold para `StateReplayFeed`, estrategia, `Event State`, producción o downstream.

---

## 31. Condiciones para solicitar la autorización física nueva

La solicitud solo podrá emitirse si:

```text
contract accepted = true
local governance adoption = PASS
implementation review = PASS
synthetic positive cases = PASS
synthetic negative cases = PASS
two-root determinism = PASS
physical reads in Fase B = 0
strategy callbacks = 0
orders = 0
fills = 0
PnL = false
boundary preservation = PASS
```

La solicitud deberá usar una identidad nueva:

```text
consumer_id =
BT_GATE_014_bounded_market_state_consumer_v0_1

purpose =
backtester_pit_consumer_integration_validation_only

state_kind =
market_state

instrument =
cik_ticker:0001651625:ACIU

session =
2021-03-15

rows =
exactly the two frozen materialized_state_candidate_id values

maximum_rows =
2

maximum_physical_files =
1

strategy =
false

signals =
false

orders =
false

fills =
false

PnL =
false

production =
false

downstream =
false
```

La autorización deberá:

```text
ser single-use;
tener máximo de una ejecución;
identificar todos los inputs y hashes;
crear el recibo de consumo antes de la lectura física;
aplicar hash-before/hash-after;
fallar cerrado;
no permitir rutas suministradas por el usuario;
no permitir ampliación de scope.
```

---

## 32. Criterios futuros de Fase D

Una ejecución física autorizada deberá demostrar, dentro del EventLoop real:

```text
1 physical Parquet opened;
exactly 2 physical rows read;
exact 40-column schema;
17 typed scientific values per event;
2 exact physical fingerprints;
2 exact candidate ids;
exact 1:1 sidecar joins;
2 BoundedMarketStateAvailable delivered;
0 early deliveries;
2 atomic store inserts;
2 bounded probe observations;
equal-timestamp priority respected;
restrictions preserved;
no Market State execution routing;
strategy callbacks = 0;
signals = 0;
orders = 0;
fills = 0;
positions mutated = 0;
cash mutations = 0;
equity mutations = 0;
PnL = false;
production = false;
downstream = false;
deterministic rerun policy satisfied within the authorization model.
```

La autorización single-use no debe consumirse dos veces para demostrar determinismo. La política de reproducción física deberá definirse antes de ejecutar, por ejemplo mediante:

```text
una autorización que admita explícitamente dos ejecuciones limpias;

o:

una ejecución single-use más reproducción determinista del consumer
contra un artefacto físico autorizado e inmutable producido por esa ejecución.
```

No se podrá decidir esa política después de consumir la autorización.

---

## 33. Criterios de cierre de `BT-GATE-014`

El cierre requiere:

```text
contract conformance = PASS
provider evidence adoption = PASS
schema authority binding = PASS
typed core-four payload = PASS
audit lineage = PASS
sidecar join = PASS
temporal legality = PASS
equal-timestamp priority = PASS
MarketStateStore = PASS
consumer probe = PASS
fingerprint validation = PASS
restriction propagation = PASS
operational isolation = PASS
negative derivatives = PASS
determinism = PASS
bounded physical consumer probe = PASS
external acceptance review = PASS
boundary preservation = PASS
```

Estado final permitido:

```text
BT-GATE-014 =
CLOSED_PASS_POINT_IN_TIME_MARKET_STATE_CONSUMER_ACCEPTED_WITH_RESTRICTIONS
```

El cierre no autoriza automáticamente:

```text
las 104 filas;
otra sesión;
otro instrumento;
consumo de estrategia;
backtest de Market State;
Event State;
StateReplayFeed general;
producción;
downstream;
dataset oficial;
edge claims.
```

---

## 34. Escalado posterior no autorizado por este contrato

La progresión conceptual futura podrá ser:

```text
2 filas bounded
        ↓
1 sesión completa
        ↓
varias sesiones
        ↓
varios instrumentos
        ↓
dataset candidato completo
        ↓
consumo de estrategia expresamente autorizado
```

Cada transición requiere un gate o autorización independiente. Esta secuencia no constituye autorización anticipada.

`BT-GATE-015` solo podrá abrirse después de:

```text
BT-GATE-014 closed
AND
Event State provider preparation authorized separately
```

---

## 35. Exclusiones expresas

```text
BT-GATE-014_NOT_IN_SCOPE

Event State
general StateReplayFeed
general StateBundle consumption
104-row candidate consumption
official Market State dataset
Market State feature engineering
new Information Objects outside core-four
liquidity
market_microstructure_state
order_flow_pressure
news_catalyst_context
fundamental_context
short_side_context
broad_market_context
halt_context
strategy callbacks
signals
Decision Models
orders
fills
trades
positions
cash
equity
PnL
execution price selection
valuation price selection
portfolio construction
point-in-time universe construction
stocks-in-play selection
borrow or locate evidence
SSR semantics
halt semantics
execution realism
bid/ask simulation
partial fills
queue position
liquidity or capacity modeling
market impact
parameter optimization
train/test orchestration
DSR
PBO
CSCV
machine learning
reinforcement learning
AlphaEvolve
edge claims
full 2005-2026 backtest
provider modification
upstream rebuild
production
downstream
live trading
```

---

## 36. Condiciones de stop y revisión material

La implementación deberá detenerse y volver al owner si:

```text
one of the 40 physical columns cannot be mapped unambiguously;
typed payload requires a semantic reinterpretation;
fingerprint cannot be reproduced from the frozen contract;
provider and consumer timestamp semantics conflict;
equal-timestamp order cannot preserve BT-GATE-013 semantics;
MarketStateStore requires modifying execution or accounting;
the two physical rows cannot join 1:1 with sidecar;
restriction propagation cannot be preserved;
physical data appears necessary during Fase B;
scope must exceed the two frozen rows;
Event State becomes necessary;
provider artifacts must be modified;
the consumed provider authorization appears necessary;
a new source table becomes necessary.
```

Un cambio de estilo, nombre interno de módulo o documentación no constituye defecto material mientras conserve este contrato.

---

## 37. Invariantes finales

```text
BT-GATE-013_ACCEPTED_SEMANTICS =
PRESERVED

ONE_NEW_BOUNDARY =
POINT_IN_TIME_MARKET_STATE_CONSUMER_AND_STORE

PROVIDER_HANDOFF =
IMMUTABLE_AND_HASH_BOUND

SCHEMA_AUTHORITY =
UNAMBIGUOUS

RUNTIME_CONTENT_AUTHORITY =
UNAMBIGUOUS

CORE_FOUR_FIELDS =
17

PHYSICAL_COLUMNS =
40

NO_STATE_LOOKAHEAD =
REQUIRED

NO_EARLY_VISIBILITY =
REQUIRED

MARKET_STATE_STORE_SEPARATE_FROM_MARKET_DATA =
REQUIRED

MARKET_STATE_AS_EXECUTION_PRICE =
PROHIBITED

PHYSICAL_READ_DURING_NON_PHYSICAL_IMPLEMENTATION =
PROHIBITED

REUSE_CONSUMED_PROVIDER_AUTHORIZATION =
PROHIBITED

SYNTHETIC_FIXTURES =
REQUIRED_BEFORE_PHYSICAL_AUTHORIZATION

EVENT_STATE =
NOT_AUTHORIZED

GENERAL_STATE_REPLAY_FEED =
NOT_AUTHORIZED

STRATEGY_CALLBACKS =
0

ORDERS =
0

FILLS =
0

PnL =
false

PRODUCTION =
false

DOWNSTREAM =
false
```

---

## 38. Decisión solicitada al owner

```text
OPTION_A =
RETURN_WITH_REQUIRED_CONTRACT_CORRECTIONS

OPTION_B =
ADOPT_PROVIDER_EVIDENCE,
ACCEPT_CONTRACT,
OPEN_BT_GATE_014,
AND_AUTHORIZE_BOUNDED_NON_PHYSICAL_IMPLEMENTATION
```

`OPTION_B` no incluye:

```text
PHYSICAL_READ_AUTHORIZATION
REUSE_OF_CONSUMED_AUTHORIZATION
EVENT_STATE_AUTHORIZATION
STRATEGY_AUTHORIZATION
ORDER_OR_FILL_AUTHORIZATION
GATE_CLOSURE
```

---

## 39. Estado al emitir V0.1

```text
BT-GATE-013 =
CLOSED_PASS_PHYSICAL_HISTORICAL_REPLAY_ACCEPTED

PROVIDER_HANDOFF =
VERIFIED_AND_READY_FOR_LOCAL_ADOPTION

BT-GATE-014_NAME =
POINT_IN_TIME_MARKET_STATE_CONSUMER_V0_1

BT-GATE-014_OBJECTIVE =
PROVE_CAUSAL_DETERMINISTIC_TYPED_MARKET_STATE_CONSUMPTION

CONTRACT_STATUS =
CONTRACT_ACCEPTED

NON_PHYSICAL_IMPLEMENTATION =
AUTHORIZED

PHYSICAL_CONSUMER_READ =
NOT_AUTHORIZED

PHYSICAL_CONSUMER_EVIDENCE =
NOT_YET_PRODUCED

EVENT_STATE =
NOT_AUTHORIZED

STATE_REPLAY_FEED_GENERAL =
NOT_AUTHORIZED

STRATEGY =
NOT_AUTHORIZED

ORDERS =
NOT_AUTHORIZED

FILLS =
NOT_AUTHORIZED

PnL =
NOT_AUTHORIZED

BT-GATE-015 =
NOT_OPEN
```
