# BT-GATE-014 — Single-Use Physical Consumer Authorization V0.3

## 0. Control

```text
DOCUMENT_ID =
18_BT_GATE_014_SINGLE_USE_PHYSICAL_CONSUMER_AUTHORIZATION_V0_3

AUTHORIZATION_ID =
BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-3

GATE_ID =
BT-GATE-014

CONSUMER_ID =
BT_GATE_014_BOUNDED_MARKET_STATE_CONSUMER

CONTRACT_CONSUMER_ID =
BT_GATE_014_bounded_market_state_consumer_v0_1

STATUS =
AUTHORIZED_NOT_CONSUMED

ISSUED_AT_UTC =
2026-07-30T18:51:00Z

AUTHORITY =
TSIS_OWNER_EXPLICIT_BT_GATE_014_CORRECTION_INSTRUCTION
```

Esta autorización emite un permiso nuevo y separado dentro del mismo
`BT-GATE-014`. No ejecuta la lectura física, no consume el permiso y no cierra
el gate.

```text
PHYSICAL_CONSUMER_READ = NOT_EXECUTED
PHYSICAL_STATE_ROWS_READ = 0
BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED
```

## 1. Supersesión y baselines inmutables

```text
V0.1 =
SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL

V0.2 =
SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL

V0.3 =
AUTHORIZED_NOT_CONSUMED
```

Baselines:

| Artefacto | SHA-256 | Función |
| --- | --- | --- |
| `bt_gate_014_phase_b_external_re_review_acceptance_packet_20260730T154133Z.zip` | `8e3d6f1d5c9f8dca0da4f30b038e52159f1973819c251ea3daa1325b0f848d96` | Fase B aceptada |
| `bt_gate_014_single_use_physical_preexecution_packet_20260730T171556Z.zip` | `e8d9e4e8d69d664aa10460f23e1b972d490ed576df0bc3f6c2beebb2d72b27db` | V0.1 rechazada |
| `bt_gate_014_single_use_physical_preexecution_packet_v0_2_20260730T181505Z.zip` | `189c911ee5ca83ebf279ddf28be86d320e1f26aebab8967637a08259b6259562` | V0.2 rechazada |

V0.3 corrige exclusivamente:

```text
orden causal BAR -> STATE;
guard de fallo durable antes del consumo;
manejo de errores que incluye consume() y el recibo;
failure_manifest.json disponible ante cualquier interrupción posterior;
identidad científica y determinista explícita;
binding de la dependencia ejecutable completa;
documentación UTF-8 y governance semánticamente coherente.
```

No amplía el scope científico ni operacional.

## 2. Operación autorizada

```text
ALLOWED_OPERATION =
ONE_PHYSICAL_READ_AND_ONE_INTEGRATION_RUN

EXECUTION_LIMIT = 1
MAXIMUM_PHYSICAL_FILES = 1
MAXIMUM_PHYSICAL_ROWS = 2
STATE_KIND = market_state
INSTRUMENT_ID = cik_ticker:0001651625:ACIU
TICKER = ACIU
SESSION_DATE = 2021-03-15
STRATEGY = NONE
STRATEGY_DECISIONS = 0
ORDERS = 0
FILLS = 0
PnL = false
PRODUCTION = false
DOWNSTREAM = false
```

## 3. Dos identidades gobernadas

| `context_id` | `source_candidate_record_id` | `materialized_state_candidate_id` | `state_output_fingerprint` | `decision_timestamp_utc` | `state_available_at_utc` |
| --- | --- | --- | --- | --- | --- |
| `scale_c_context_0058` | `25672915a752b75e823409fc6dad6b55eaeddb900a0e58b7f5eab5f7c2ed941d` | `f09492ac417d05161f70ee75f81e345a9cc315cef9beb9939d2df6ff3eb58dd3` | `f7c926be8e8bb6e84433061213bc554d54de2e03d0910a799e974ff5aea04617` | `2021-03-15T13:30:00Z` | `2021-03-15T13:30:00Z` |
| `scale_c_context_0115` | `27c2b0b4973a880ab31d3df65c9977014f8b6e0a41c8d94e176031ff27672198` | `26d923a282355ad242a5d91ad7d6183bed6a94842041ecf966ac70c366308c0e` | `2420034cb851629b48ee3216713b6bc1a337ce0a4356096575a3db1a91edb7bd` | `2021-03-15T20:00:00Z` | `2021-03-15T20:00:00Z` |

Resultado obligatorio:

```text
AUTHORIZED_ROWS = 2
OBSERVED_ROWS = 2
MISSING_AUTHORIZED_ROWS = 0
UNLISTED_ROWS_DELIVERED = 0
DUPLICATE_ROWS = 0
IDENTITY_FINGERPRINT_MISMATCHES = 0
```

## 4. Dataset, schema y autoridades

```text
CANDIDATE_DATASET_ID =
market_state_candidate_dataset_scale_validation_v0_1_516a27d0f8f53762

CANDIDATE_DATASET_FINGERPRINT =
516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416

PROFILE_ID =
market_state_core_four_intraday_profile_v0_1

PROFILE_FINGERPRINT =
afa44f42164f9be6830740d9d48b09f727a41b8a2f6847e12bf0bd2293de7cd9

PHYSICAL_PROFILE_ID =
core_four_market_state_profile_v0_1

STATE_SCHEMA_VERSION =
core_four_market_state_candidate_physical_schema_v0_1

PHYSICAL_COLUMNS = 40
SCIENTIFIC_VALUES_PER_EVENT = 17
NULLABLE_COLUMNS = 0
```

Hashes de autoridad:

```text
STRUCTURAL_SCHEMA_SHA256 =
595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b

CURRENT_RUNTIME_CONTENT_SHA256 =
bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68

PROFILE_PROVENANCE_SHA256 =
b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2

BINDING_SHA256 =
4006e80f099bb8abec147e33670294d7cc2eb565d25a10a08d6bf929c247f083

STATE_BUNDLE_MANIFEST_FILE_SHA256 =
0845642ba80fac75f0094bccd370db71157da2759cad7807885b2928d2d49ab0

STATE_BUNDLE_CANONICAL_SHA256 =
0e9f7387acdf999a6e41f163ab16c3412c32cb545d1757cde4b5613572406be2
```

La procedencia `b1841f...` no puede sustituir el contenido runtime
`bc033c...`.

## 5. Handoffs adoptados

```text
OUTER_PROVIDER_HANDOFF =
evidence/provider_handoffs/bt_gate_014/
market_state_pit_bt_gate_014_contract_handoff_v0_1_20260730T091041Z.zip

OUTER_PROVIDER_HANDOFF_SHA256 =
2c578ce9216bb3fd9010ef1f4afe8ba4022ab6b15f665d276a957f50acb35112

NESTED_PROVIDER_EVIDENCE =
evidence/provider_handoffs/bt_gate_014/
bounded_state_bundle_read_and_replay_execution_and_review_v0_1_files_
20260730T080831Z.zip

NESTED_PROVIDER_EVIDENCE_SHA256 =
8f3d914becb3bc6d33f66814b355f636827db8cac67ea483fe9c6840b4fa16c7
```

Los dos hashes se verifican antes de consumir V0.3. Estos ZIPs son evidencia
adoptada; su verificación no abre el Parquet runtime.

## 6. Nueve inputs físicos congelados

| Input | SHA-256 |
| --- | --- |
| `candidate_parquet` | `bc033cb2cd518728dc34b545df4b224badb9226130220010a25ae55701577d68` |
| `physical_schema_contract` | `595f2645aa4168e87d0b0d226b1dbc39c3e71deb7fb25b08bb8f5eab563f267b` |
| `binding` | `4006e80f099bb8abec147e33670294d7cc2eb565d25a10a08d6bf929c247f083` |
| `sidecar_manifest` | `8e426b09bb1cafac26e49c7a81de31ef4ea60ca3b56ac3aa766ba13a0772c5ac` |
| `sidecar_contract` | `a29f656a6fe741432c7272d6715637eeb49fd5d34ca550c3ac0f33166bc1b169` |
| `timestamp_contract` | `eae02c685f7bc2cc8b55e6e3bb4a6912dc3b391042c0178b3dc29387fa6b690d` |
| `lineage_manifest` | `85e7331b1b022d4075608bc4b8663de53dcb6234f21215ff232ad84c85cd4c52` |
| `temporal_legality_report` | `0eb607a4286dd3d4819f9aeb8da0eb21a18955a269b87e001f8f672378c44c70` |
| `state_bundle_manifest` | `0845642ba80fac75f0094bccd370db71157da2759cad7807885b2928d2d49ab0` |

Las rutas relativas literales están congeladas en:

```text
configs/runs/
bt_gate_014_single_use_physical_market_state_consumer_v0_3.json

CONFIGURATION_SHA256 =
ee037f501ed17c02c726f1fc776a38712ab4331e82cdd2ca6cd42006b3c05681
```

El runner exige el conjunto exacto de nueve nombres, rechaza rutas absolutas,
`..`, escapes de `TSIS_DATA_ROOT`, sustituciones y campos extra.

## 7. Sidecar, join y payload

```text
JOIN_KEY = materialized_state_candidate_id
JOIN_CARDINALITY = EXACT_1_TO_1
TYPED_CORE_FOUR_VALUES = 17
```

Deben coincidir fila, autorización y sidecar en:

```text
materialized_state_candidate_id
state_output_fingerprint
source_candidate_record_id
instrument_id
ticker
session_date
context_id
decision_timestamp_utc
candidate_dataset_id
candidate_dataset_fingerprint
profile_id
physical_profile_id
```

Los cuatro componentes obligatorios son:

```text
price_location_structure
price_movement
trading_activity
volatility_range_state
```

Restricciones exactas:

```text
candidate_runtime_only
not_official_dataset
no_downstream
no_production
```

## 8. Tiempo y orden causal

```text
state_as_of_utc <= decision_timestamp_utc
decision_timestamp_utc <= state_available_at_utc
component source <= component as_of <= component available
component_available_at_utc <= state_available_at_utc
event_loop_clock_utc >= state_available_at_utc
consumer_observation_timestamp_utc >= state_available_at_utc
```

Prioridad a igualdad de timestamp:

```text
ReplayGapEvent = 0
ReplayBarEvent = 1
BoundedMarketStateAvailable = 2
```

La clave común usa:

```text
available_at_utc
session_date derivada del timestamp UTC para Gap/Bar
event_priority
canonical_ticker
source_event_identity
```

`session_label = REGULAR` no compite con `session_date`. El EventLoop bounded
exige para ambas identidades:

```text
BAR
  -> BoundedMarketStateAvailable
  -> MarketStateStore.insert
  -> bounded consumer observation
```

Barreras sintéticas:

```text
configs/fixtures/
BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_3.json

SHA-256 =
3cf276da2d423f7be83aea4ba547186c050e03946bd573c5027f99ca8ad3f234

PHYSICAL_SOURCE_ROWS = 0
EXECUTION_INPUT = false
PRICE_USE = PROHIBITED
SCIENTIFIC_MARKET_DATA_CLAIM = false
```

## 9. Binding ejecutable completo

| Artefacto | SHA-256 |
| --- | --- |
| `configs/fixtures/BT_GATE_014_PHYSICAL_INTEGRATION_BARRIERS_V0_3.json` | `3cf276da2d423f7be83aea4ba547186c050e03946bd573c5027f99ca8ad3f234` |
| `scripts/run_bt_gate_014_single_use_physical_market_state_consumer_v0_3.py` | `8e18bf96d8206fa19724e8182861f3544c17d5fb6abf17f27f07a7ae4217369d` |
| `src/tsis_backtest/market_state/physical_authorization_v0_3.py` | `2df75e13b0808875a28cb67e9c79a6191bce6e810a1cc8d0484921f7c4c2b414` |
| `src/tsis_backtest/market_state/physical_runner_v0_3.py` | `4584012cbfa064166d1405bd34faca3a3fd00c76761e0e6ab4ad354290f70e55` |
| `src/tsis_backtest/market_state/consumer.py` | `accaa37501c323d21c23d4b9300a947f0438ecbfb769cf6a9cde57e8d7fb7989` |
| `src/tsis_backtest/market_state/contracts.py` | `b3cf8d469e2c730c5341a37d7bbc3063a14decdb59d073a6b8ac3dd94f4b020b` |
| `src/tsis_backtest/market_state/store.py` | `bc9f054657184bd2788c827145f3c5be945384f57d75b5f78c754e36ce3a1d4a` |
| `src/tsis_backtest/replay/contracts.py` | `db8591453abb50e4e07125e7297e698c0690a14575fae66bca7795d97676fc29` |
| `src/tsis_backtest/preflight/contracts.py` | `12da900f292c8ed4169c7674b125d688dd39712a3d475e3e0fe3cc63575cf238` |

El estado machine-readable recalcula estos nueve hashes antes del consumo.

## 10. Comando y run únicos

```text
COMMAND =
python scripts/run_bt_gate_014_single_use_physical_market_state_consumer_v0_3.py
--confirm-authorization-id
BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-3

RUN_ID =
bt_gate_014_single_use_physical_market_state_consumer_v0_3

RUN_DIRECTORY =
runs/bt_gate_014_single_use_physical_market_state_consumer_v0_3
```

El CLI no acepta `--root`, `--config`, `--parquet`, `--sidecar`,
`--output-root` ni rutas suministradas por el usuario. Un directorio de run ya
existente falla cerrado.

## 11. Consumo durable y atómico

Estado:

```text
configs/authorizations/
bt_gate_014_single_use_physical_consumer_authorization_v0_3.json
```

Secuencia:

```text
1. verificar documento, configuración, binding completo y handoffs;
2. adquirir lock exclusivo;
3. releer y exigir AUTHORIZED_NOT_CONSUMED;
4. crear el único RUN_DIRECTORY;
5. escribir y fsync failure_manifest.json como guard fail-closed;
6. escribir y fsync pre_run_manifest.json;
7. reemplazar atómicamente el estado por CONSUMED_BY_RUN_<run_id>;
8. escribir, fsync, releer y verificar authorization_consumption_receipt.json;
9. confirmar physical_access_started = false;
10. solo entonces resolver, hashear y abrir inputs provider.
```

El manejo de errores envuelve también `consume()` y la escritura del recibo.
Si falla cualquier acto después de crear el guard:

```text
failure_manifest.json = PRESENT
authorization_consumed = reconciliado contra el estado canónico
physical_state_rows_read = 0 si la lectura no comenzó
strategy_decisions = 0
orders = 0
fills = 0
PnL_calculated = false
```

En un PASS, el guard permanece como evidencia transaccional con:

```text
status = SUPERSEDED_BY_FINAL_MANIFEST_PASS
superseded_by = final_manifest.json
```

No existe rollback del permiso ni segundo intento.

## 12. Evidencia obligatoria

Éxito:

```text
authorization_consumption_receipt.json
pre_run_manifest.json
resolved_physical_input_manifest.json
physical_schema_validation_report.json
physical_row_identity_report.json
bounded_market_state_events.json
state_aware_event_sequence.json
market_state_store_trace.json
bounded_consumer_probe_observations.json
boundary_preservation_report.json
deterministic_reproduction_source.json
physical_consumer_validation_report.json
final_manifest.json
```

Fallo posterior al guard:

```text
failure_manifest.json
```

`final_manifest.json` debe declarar:

```text
scientific_identity_sha256
deterministic_output_hash
identity_fingerprint_mismatches = 0
provider_modification = false
external_acceptance_review = PENDING
BT_GATE_014_CLOSED_PASS = NOT_AUTHORIZED
```

## 13. Resultado exigido

```text
physical data files opened = 1
physical rows read = 2
Market State events emitted = 2
typed scientific values per event = 17
MarketStateStore inserts = 2
bounded consumer observations = 2
delivery before available_at = 0
identity/fingerprint mismatches = 0
strategy decisions = 0
orders = 0
fills = 0
PnL calculated = false
provider modification = false
```

## 14. Política de reproducción

```text
PHYSICAL_RERUN = NOT_AUTHORIZED

DETERMINISM_POLICY =
ONE_PHYSICAL_RUN_THEN_NON_PHYSICAL_REPRODUCTION_FROM_IMMUTABLE_RUN_EVIDENCE
```

La reproducción posterior usará `deterministic_reproduction_source.json`; no
volverá a abrir el Parquet ni reutilizará V0.3.

## 15. Fallo cerrado

```text
authorization not issued or already consumed
-> no physical access

binding/document/config/handoff mismatch
-> no authorization consumption and no physical access

input hash, schema, cardinality, identity, join or temporal mismatch
-> authorization remains consumed
-> failure_manifest.json remains authoritative

BAR -> STATE violation
-> FAIL_MARKET_STATE_EQUAL_TIMESTAMP_PRIORITY

provider hash-after != hash-before
-> FAIL_SOURCE_MUTATION
```

## 16. Prohibiciones vigentes

```text
otras 102 filas
otros símbolos o sesiones
otro dataset o perfil
Event State
StateReplayFeed general
Market State como MarketData
Market State como execution price
Market State como valuation price
estrategia
signals
orders
fills
trades
positions
cash
equity
PnL
provider modification
upstream rebuild
dataset promotion
production
downstream
full backtest
edge claim
BT-GATE-015
```

## 17. Estado al emitir

```text
BT-GATE-014 =
SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_3_ISSUED_NOT_CONSUMED

NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_1 =
SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL

NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_2 =
SUPERSEDED_UNCONSUMED_AFTER_PREEXECUTION_REVIEW_FAIL

NEW_SINGLE_USE_PHYSICAL_AUTHORIZATION_V0_3 =
AUTHORIZED_NOT_CONSUMED

PHYSICAL_CONSUMER_READ =
NOT_EXECUTED

PHYSICAL_STATE_ROWS_READ =
0

PHYSICAL_RUN_DIRECTORY =
ABSENT

BT-GATE-014_CLOSED_PASS =
NOT_AUTHORIZED
```

El próximo acto permitido es una revisión externa incremental de V0.3. El
comando físico solo podrá ejecutarse después de esa aprobación.
