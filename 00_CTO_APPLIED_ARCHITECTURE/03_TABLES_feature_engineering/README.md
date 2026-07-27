# 03_TABLES_feature_engineering

> Current runtime note (2026-07-27): `event_state_on_demand_bounded_candidate_dataset_review_v0_1` is closed; next gate is `event_state_on_demand_bounded_deterministic_rerun_authorization_v0_1`. The candidate was approved only as bounded Event State on-demand evidence with restrictions: 9 requested = 8 represented + 1 unavailable, 0 hard review failures, no registry mutation, no official dataset, no production and no downstream.

Status: `readme_v3_57_event_state_on_demand_bounded_candidate_dataset_review_closed`
Date: `2026-07-27`

Current runtime update: `event_state_on_demand_bounded_candidate_dataset_review_v0_1` closed under `08_RUNTIME_CAPABILITIES` as `CLOSED_APPROVED_AS_EVENT_STATE_ON_DEMAND_BOUNDED_CANDIDATE_EVIDENCE_WITH_RESTRICTIONS_NO_PROMOTION`. It reviewed the first bounded Event State on-demand candidate from `event_state_on_demand_bounded_execution_v0_1_20260727T200322Z`: 9 requested contexts = 8 represented + 1 unavailable, 8 Event State candidate records, 0 unaccounted contexts, 0 hard review failures, 0 registry mutations and 0 additional Market State reads. The output remains candidate evidence only. Next gate: `event_state_on_demand_bounded_deterministic_rerun_authorization_v0_1`.

Esta seccion conecta tablas existentes, Objetos de Informacion, feature engineering, Market State, Event State, builders, validators y consumo downstream.

No es una autoridad operativa independiente.

La autoridad final vive en:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations
G:\TSIS\data\data_foundation_outputs
builders
validators
manifests
tests
status matrices
```

---

Current table-level institutional status for `000-018` is now maintained in:

```text
04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md
```

`02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md` remains the accepted historical discovery pass. It is not the current authority matrix and must not be used to infer official dataset, production or downstream-consumption status.

Data Foundation evidence reconciliation is now closed by `tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z` with `CLOSED_WITH_FINDINGS_NO_PROMOTION`: 19 tables reconciled, 13 restricted datasets proven for declared scope, 2 validated candidates proven with restrictions, 3 partial semantic/physical reconciliations, 1 restricted controlled replay candidate, 0 unresolved rows, 0 official datasets inferred, 0 parquet files read and 0 source market-data rows read. The persistent readout is `06_tables_000_018_evidence_reconciliation_readout_v0_1.md`.

---

## Pregunta Central

Todo trabajo en esta seccion debe responder:

```text
Que necesitamos saber
para describir correctamente
el estado del mercado
en un instante t?
```

Y tambien:

```text
Que informacion puede ayudar
a describir, explicar o investigar
el comportamiento futuro del mercado,
del instrumento o del contexto estudiado?
```

El objetivo no es acumular columnas.
El objetivo es admitir solo variables que representen informacion necesaria.

The variable and attribute admission policy is now consolidated in:

```text
02_VARIABLE_AND_ATTRIBUTE_ADMISSION_POLICY_v0_1.md
```

That document does not admit new variables, change schemas or authorize execution. It records the standing bridge:

```text
Data Foundation physical attribute authority
    + Applied Architecture semantic admission
    + Operational Mapping
    + Execution authorization
```

---

## TSIS Market Ontology v1 Freeze

```text
phase = TSIS Market Ontology Phase
status = CLOSED
ontology = TSIS Market Ontology v1
ontology_status = FROZEN
ontology_lock_status = LOCKED
phase_b_status = OPEN
phase_b_scope = governed_engineering
production_builder_development_authorized = false
state_consumption_authorized = false
```

El vertical de `Trading Activity` demostro el lifecycle completo, pero queda
clasificado como piloto de proceso. Operational Mapping y Builder Validation
design estan completos para los 12 Objetos de v1. Los gates experimentales de
contract, source binding, path, schema metadata, logical-to-physical binding,
bounded identity/temporal validation, bounded grain validation y bounded
quality/lineage validation, core-four builder execution, resolution record
acceptance, core-four integration design, core-four integration execution,
core-four materialization design, core-four materialization authorization y
core-four materialization execution quedan cerrados o emitidos con restricciones.

El run vigente de integracion experimental es:

```text
experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z
```

Emitio 8 Market State candidate records no canonicos y rechazo 2 contextos
pre-bar bajo object atomicity.


Scale B calendar-aware Market State integration had closed with restrictions by `experimental_core_four_market_state_scale_b_market_state_integration_execution_v0_1_20260723T144323Z`: 288 accepted resolution records were consumed, 64 non-canonical Market State candidate JSONL records emitted, 8 expected blocked contexts rejected, 0 source market-data rows read, 0 parquet files written and 0 hard validation failures. That downstream Scale B materialization and physical validation chain has now also closed with restrictions; official Market State, production, downstream consumption, dataset/table promotion and full-history/full-universe execution remain closed.

Scale B is now closed with restrictions through candidate physical validation by `core_four_market_state_candidate_physical_validation_v0_1_20260723T145049Z`. The accepted chain produced 64 non-official physical candidate rows from 64 integrated JSONL candidates, checked 1088 source-to-physical value mappings, wrote 1 candidate parquet, read 0 source market-data rows during integration/materialization/validation and recorded 0 hard validation failures. Scale C has closed with restrictions through independent candidate physical validation by `core_four_market_state_scale_c_candidate_physical_validation_v0_1_20260723T184900Z`: 120 contexts, 480 resolution records, 104 candidate physical rows, parquet SHA-256 `b1841f4897a759de8ec9a317bece888a9ff817da3df2cd0eb477b4ed950775a2`, 1768 value mappings checked and 0 hard validation failures. Official Market State, production, downstream consumption, dataset/table promotion and full-history/full-universe execution remain closed. Promotion review run `official_market_state_candidate_promotion_review_v0_1_20260723T192107Z` approved `market_state_core_four_intraday_profile_v0_1`; promotion run `official_market_state_candidate_promotion_v0_1_20260723T193403Z` registered the applied-architecture official profile package and validation run `official_market_state_profile_artifact_validation_v0_1_20260723T193711Z` closed with 4 registry artifacts checked, 0 hash mismatches, 0 invariant failures and 0 hard failures. The Market State profile-family architecture is now recorded in `06_MARKET_STATE_INTEGRATION/tsis_market_state_profiles_family_architecture_v0_1.md`, with an Event State dependency seed in `06_MARKET_STATE_INTEGRATION/event_state_architecture_from_market_state_profiles_v0_1.md`. Event State profile contract design is now recorded as `event_state_core_four_intraday_profile_v0_1` in `06_MARKET_STATE_INTEGRATION/event_state_profile_contract_design_v0_1.md`, with machine-readable contract `06_MARKET_STATE_INTEGRATION/event_state_profile_contract_design_contract_v0_1.json`. Event policy is now recorded in `07_EVENT_STATE_INTEGRATION/event_state_event_policy_v0_1.md`. Event type/family contract design is now recorded in `07_EVENT_STATE_INTEGRATION/event_type_or_event_family_contract_design_v0_1.md`, with machine-readable contract `07_EVENT_STATE_INTEGRATION/event_type_or_event_family_contract_design_contract_v0_1.json`. Event Type Registry seed design is recorded in `07_EVENT_STATE_INTEGRATION/event_type_registry_seed_design_v0_1.md`, with machine-readable contract `07_EVENT_STATE_INTEGRATION/event_type_registry_seed_design_contract_v0_1.json`. The first candidate-only registry population is recorded in `07_EVENT_STATE_INTEGRATION/event_type_registry_initial_population_readout_v0_1.md`; the initial admission review is recorded in `07_EVENT_STATE_INTEGRATION/event_type_initial_admission_review_readout_v0_1.md` and successor snapshot `07_EVENT_STATE_INTEGRATION/event_type_registry_post_initial_admission_snapshot_v0_1.json`. `event_type:market_data:session_opened` is now `accepted_with_restrictions`; Event Instance Binding, Event Window Binding, Market State Profile Compatibility, Instrument Session Projection and Event State Integration designs are recorded, the Event State execution-chain joint review is closed, the first bounded execution-chain execution is closed by `event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z` with 8 non-official Event State candidate JSONL records, 1 blocked context, 0 fallback uses and 0 hard validation failures, physical validation run `event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z` closed with 8 candidate records checked and 0 schema, hash, fingerprint, binding, lineage, authority, determinism or hard validation failures, and candidate dataset review run `event_state_candidate_dataset_review_v0_1_20260724T194315Z` approved the 8-record output as bounded candidate Event State evidence with restrictions and no promotion. Profile promotion review run `event_state_profile_promotion_review_v0_1_20260724T201046Z` approved semantic Event State profile promotion with restrictions; promotion run `event_state_profile_promotion_v0_1_20260724T203016Z` registered `event_state_core_four_intraday_profile_v0_1` as an official semantic Event State profile with restrictions; artifact validation run `event_state_profile_artifact_validation_v0_1_20260724T204410Z` checked 4 registry artifacts with 0 hash mismatches, 0 invariant failures and 0 hard validation failures; operational registry / consumption policy design `event_state_operational_registry_or_consumption_policy_design_v0_1` records profile-reference use only and keeps physical Event State consumption closed. Runtime capabilities architecture is recorded in `08_RUNTIME_CAPABILITIES` to define Request, Resolver, Execution Plan, Materializer, Validator, Registry and Idempotency before Market State on-demand design. Market State on-demand capability design and the full request/resolver/materializer/validator/registry chain are now closed through the first bounded execution run `market_state_bounded_on_demand_execution_v0_1_20260724T232123Z`: 1 request, 1 execution plan, 9 requested contexts, 8 candidate Market State rows, 1 unavailable context, 1 candidate parquet, 1 candidate registry entry and 0 hard validation failures. The run remains candidate evidence only; candidate dataset review `market_state_bounded_on_demand_candidate_dataset_review_v0_1` approved that evidence with restrictions and no promotion. Deterministic rerun `market_state_bounded_on_demand_deterministic_rerun_v0_1_20260725T053434Z` closed as `CLOSED_PASS_DETERMINISTIC_RERUN_MATCH_WITH_RESTRICTIONS`; determinism validation `market_state_bounded_on_demand_determinism_validation_v0_1_20260725T000000Z` approved it as bounded determinism evidence with no reuse eligibility transition. `market_state_bounded_on_demand_idempotency_reuse_test_authorization_v0_1` is now recorded to authorize the next bounded cache/idempotency test. Production/downstream remain closed. `event_type:regulatory:halt_resumed` remains `investigational_candidate` blocked by source timestamp and point-in-time availability findings. Official Market State, operational dataset registry, official parquet, Event State materialization, production, downstream consumption and full-history/full-universe execution remain closed.


El run vigente de materializacion experimental es:

```text
experimental_core_four_market_state_materialization_v0_1_20260722T081155Z
```

Convirtio los 8 candidate JSONL records en 8 filas fisicas candidatas y un
unico parquet candidato no oficial. Resultado: `PASS_WITH_RESTRICTIONS`, 40
columnas fisicas, 17 columnas de valores, 0 source market-data rows read, 0
fallos duros, 0 roundtrip failures y 0 semantic rebuild differences sobre 37
campos comparados.

El diseno vigente de materializacion es:

```text
core_four_market_state_materialization_design_v0_1
core_four_market_state_materialization_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
```

La autorizacion experimental de materializacion core-four ya fue ejecutada con
restricciones sobre 8 filas candidatas. El parquet generado sigue siendo
experimental, candidato y no oficial. Market State parquet oficial, produccion,
consumo downstream, full-history/full-universe y promocion siguen cerrados.

Scale A ya cerro hasta validacion fisica independiente contra la muestra congelada:

```text
builder_resolution_run = experimental_core_four_market_state_scale_a_builder_resolution_execution_v0_1_20260722T202557Z
integration_run = experimental_core_four_market_state_scale_a_market_state_integration_execution_v0_1_20260722T204126Z
candidate_materialization_run = experimental_scale_a_ms_candidate_materialization_v0_1_20260722T204356Z
physical_validation_run = experimental_core_four_market_state_scale_a_candidate_physical_validation_v0_1_20260722T204600Z
```

Resultado vigente: `CLOSED_PASS_WITH_RESTRICTIONS`, 60 contextos congelados, 240 Information Object resolution records, 52 Market State candidate records integrados, 52 filas fisicas candidatas, 1 parquet candidato no oficial, 40 columnas fisicas, 17 columnas de valores, 884 value mappings reconciliados, 52 fingerprints de estado y 52 materialized IDs recalculados, 0 source market-data rows read durante integracion/materializacion/validacion fisica y 0 hard validation failures.

El diseno `governed_exchange_session_calendar_design_v0_1` queda cerrado como `CLOSED_DESIGN_READY_WITH_RESTRICTIONS`. La autorizacion `governed_exchange_session_calendar_binding_authorization_v0_1` fue ejecutada por `governed_exchange_session_calendar_binding_validation_v0_1_20260723T064928Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 5.328 sesiones XNYS, 45 early closes, SHA-256 fuente verificado, 18 columnas gobernadas, 0 fallos temporales/fingerprint/determinismo y 0 hard validation failures.

La autorizacion `experimental_core_four_market_state_scale_b_authorization_v0_1` fue ejecutada por `experimental_core_four_market_state_scale_b_sample_preflight_v0_1_20260723T094626Z` y cerro `CLOSED_PASS_WITH_RESTRICTIONS`: 72 contextos congelados, 8 instrumentos, 6 sesiones gobernadas, 288 resolution records esperados, 8 contextos bloqueados esperados, 64 contextos integrables esperados y sample fingerprint `5866b534b1bd3448375b91b14125721942bc5ec3ed5df9c9df8ebd68d83d5972`. La superficie `experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1` cerro `CLOSED_PASS_WITH_RESTRICTIONS` por `experimental_core_four_market_state_scale_b_execution_surface_construction_v0_1_20260723T111450Z` con fingerprint `dd05b10143b92d20af4b7eb5be470ab1ab8667820b57f1cc4a43bce5b2f218aa`. El builder/resolution Scale B cerro `CLOSED_PASS_WITH_RESTRICTIONS` por `experimental_core_four_market_state_scale_b_builder_resolution_execution_v0_1_20260723T142329Z`; la integration, candidate materialization y physical validation tambien cerraron con restricciones por `experimental_core_four_market_state_scale_b_market_state_integration_execution_v0_1_20260723T144323Z`, `experimental_scale_b_ms_candidate_materialization_v0_1_20260723T144955Z` y `core_four_market_state_candidate_physical_validation_v0_1_20260723T145049Z`. Scale C queda cerrado con restricciones por `core_four_market_state_scale_c_candidate_physical_validation_v0_1_20260723T184900Z`; la siguiente frontera requiere autorizacion separada de review/promocion de candidato oficial o plan de escala posterior.

Regla:

```text
No production Market State Builder before governed Operational Mapping,
Builder Validation, Market State Integration and Operational Promotion gates.
```

---
## Estructura Activa

```text
03_TABLES_feature_engineering/
|
|-- 00_TABLES_MARKET_STATE_EVENT_STATE.md
|-- 01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
|-- 02_VARIABLE_AND_ATTRIBUTE_ADMISSION_POLICY_v0_1.md
|-- 03_VARIABLE_ATTRIBUTE_ADMISSION_RECORD_TEMPLATE_v0_1.md
|-- 04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md
|-- 05_tables_000_018_evidence_reconciliation_authorization_v0_1.md
|-- 06_tables_000_018_evidence_reconciliation_readout_v0_1.md
|-- 02_TABLE_REPRESENTATION_REVIEW/
|-- 03_INFORMATION_OBJECTS/
|-- 04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/
|-- 05_STATE_BUILDER_VALIDATION/
|-- 06_MARKET_STATE_INTEGRATION/
|-- 07_EVENT_STATE_INTEGRATION/
|-- 99_archive/
|-- CHANGELOG.md
`-- README.md
```

---

## Responsabilidad De Cada Parte

| Path | Funcion |
| --- | --- |
| `00_TABLES_MARKET_STATE_EVENT_STATE.md` | Explica por que existen Market State y Event State, y como consumen Objetos de Informacion. |
| `01_INFORMATION_OBJECT_ADMISSION_PROCESS.md` | Gobierna la admision de Objetos de Informacion como `Liquidity`, `Momentum` o `Trading Activity`. No audita tablas completas. |
| `02_VARIABLE_AND_ATTRIBUTE_ADMISSION_POLICY_v0_1.md` | Consolida la politica distribuida que decide por que un raw source attribute, derived feature, state variable, event variable, outcome label o quality/lineage attribute puede quedar descubierto, candidato, mapeado, admitido, bloqueado o rechazado. No admite variables ni cambia schemas por si mismo. |
| `03_VARIABLE_ATTRIBUTE_ADMISSION_RECORD_TEMPLATE_v0_1.md` | Plantilla de ficha para proponer ATR, RVOL, VWAP, spreads, labels u otros atributos: fija quien propone, por que ahora, que Objeto/constructo sirve, que evidencia existe y que autoridad puede decidir. No admite variables por si misma. |
| `04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md` | Matriz viva de autoridad institucional de tablas `000-018`: separa discovery historico, candidato fisico, perfil oficial, dataset oficial, consumo, produccion, siguiente gate y los ejes `physical_authority`, `semantic_authority` y `execution_authority`. No promueve datasets ni autoriza consumo por si misma. |
| `02_TABLE_REPRESENTATION_REVIEW/` | Audita tablas completas `000-018`: responsabilidad, grano, frontera, atributos, faltantes y solapamientos. Sus discovery passes y reviews son evidencia historica/de revision; la autoridad transversal vigente vive en `04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md`. |
| `03_INFORMATION_OBJECTS/` | Guarda expedientes trazables de Objetos evaluados: candidatos, revisados, aceptados, aceptados con restricciones o rechazados. |
| `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/` | Phase B complete_for_v1. Puente gobernado: Objeto admitido -> modelos aprobados -> capacidades -> variables candidatas -> tablas fuente -> perfiles de State. |
| `05_STATE_BUILDER_VALIDATION/` | Builder Validation design completo para v1. El builder experimental core-four y la aceptacion de resolution records cerraron con restricciones. No autoriza builders de produccion, materializacion ni consumo State por si mismo. |
| `06_MARKET_STATE_INTEGRATION/` | Integracion core-four experimental, materializacion candidata, Scale A cerrada, calendario gobernado validado, Scale B cerrada hasta validacion fisica independiente de 64 filas, Scale C cerrado hasta validacion fisica independiente y perfil oficial aplicado `market_state_core_four_intraday_profile_v0_1` promovido con restricciones. Mantiene evidencia fisica no oficial, 240 resolution records Scale A, 288 resolution records Scale B, 480 resolution records Scale C, 5.328 sesiones XNYS gobernadas, superficie 014 run-local Scale B de 8112 filas, superficie 014 run-local Scale C de 13969 filas y parquet candidato Scale C de 104 filas. Dataset Market State oficial, produccion, consumo operativo y full-history/full-universe siguen cerrados. |
| `07_EVENT_STATE_INTEGRATION/` | Diseno gobernado de Event State posterior al perfil oficial Market State: politica de eventos, registro seed, primera admision mixta, disenos de instancia/ventana/proyeccion/integracion, bounded execution-chain candidate output, validacion fisica, candidate dataset review, profile promotion review, semantic profile promotion, artifact validation y operational registry/consumption policy design cerrados. Mantiene `candidate_event_types = 1`, `accepted_event_types = 1`; no autoriza nuevos eventos, ejecucion no acotada, dataset promotion, materializacion oficial, parquet oficial, produccion ni downstream. |
| `08_RUNTIME_CAPABILITIES/` | Arquitectura puente de capacidades runtime: Request, Resolver, Execution Plan, Materializer, Validator, Dataset Registry e idempotencia. Registra arquitectura runtime y el primer diseno de capacidad Market State on-demand; no implementa resolver, no ejecuta materializadores, no lee fuentes, no escribe datasets, no abre produccion ni downstream. |
| `99_archive/` | Documentos historicos, superseded o no activos. No son autoridad operativa. |

---

## Tres Procesos Distintos

### Revision De Tablas

Gobernada por:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md
```

Pregunta principal:

```text
Que responsabilidad tiene esta tabla
dentro de la representacion de TSIS?
```

La revision de tabla determina:

```text
responsabilidad
grano
clave primaria
inputs
outputs
fronteras
informacion minima
atributos reales
columnas no justificadas
faltantes
solapamientos
legalidad temporal
estado fisico / contractual / validado / promovido
candidatos a Objetos de Informacion
```

### Admision De Objetos De Informacion

Gobernada por:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
```

Pregunta principal:

```text
Esta informacion merece formar parte
de la representacion del estado?
```

Ejemplos:

```text
Liquidity
Momentum
Trading Activity
News Context
Market Regime
```

La revision de tabla puede descubrir candidatos.
La admision de Objetos decide si esos candidatos existen institucionalmente.

### Admision De Variables Y Atributos

Gobernada por:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_VARIABLE_AND_ATTRIBUTE_ADMISSION_POLICY_v0_1.md
```

Pregunta principal:

```text
Por que esta variable, atributo o feature entra en una representacion TSIS,
y por que otra no?
```

La politica separa:

```text
raw_source_attribute
derived_feature
state_variable
event_variable
outcome_label
quality_lineage_governance_attribute
```

Regla:

```text
Research puede proponer evidencia.
Applied Architecture puede admitir significado.
Data Foundation gobierna fuentes fisicas.
Execution gates autorizan uso.
Builders ejecutan; no escogen variables.
```

---

## Definicion De Objeto De Informacion

```text
Objeto de Informacion
=
unidad semantica de informacion que TSIS decide preservar
sobre uno o varios fenomenos observables,
independiente de su Modelo de Representacion
y de su implementacion fisica.
```

Ejemplo:

```text
Liquidity
= Objeto de Informacion

coste de negociacion + profundidad + disponibilidad
= Modelo de Representacion

spread_bps + depth + quote_count
= implementacion fisica / variables
```

Regla:

```text
El Objeto no es aun la representacion.
Es lo que debe ser representado.
```

---
## Taxonomias Separadas

No usar una unica columna llamada `family` para clasificar todo.
TSIS separa cuatro ejes:

| Eje | Pregunta | Ejemplos |
| --- | --- | --- |
| `information_object_family` | Que significado semantico tiene el Objeto? | `Price Dynamics`, `Trading Activity`, `Liquidity`, `Market Microstructure`, `Instrument Context`, `External Context`, `Market Context` |
| `source_domain` | De que fuente observable procede la evidencia? | `OHLCV`, `Trades`, `Quotes`, `News`, `Fundamentals`, `SEC`, `Short`, `Halts`, `Reference` |
| `temporal_resolution` | En que escala o ventana aplica? | `daily`, `intraday_bar`, `second`, `event_window`, `as_of` |
| `institutional_role` | Que papel cumple dentro de TSIS? | `observable`, `quality`, `lineage`, `governance`, `outcome` |

Regla:

```text
Information Object Family es solo semantica.
Feature Family, source family, dataset family, event family,
quality family u outcome family no deben mezclarse en el mismo campo.
```


## Object Discovery vs Object Admission

Hay dos direcciones validas, pero no tienen la misma autoridad.

### Object Discovery Process

Puede empezar desde abajo o desde cualquier evidencia disponible:

```text
tablas existentes
-> variables reales
-> capacidades derivables
-> posibles significados
-> Objeto de Informacion candidato
```

Sirve para descubrir candidatos.
No admite Objetos.
No autoriza variables para Market State.
No convierte una tabla existente en significado cientifico oficial.

### Object Admission Process

Siempre debe seguir la direccion cientifica:

```text
fenomeno o necesidad cientifica
-> Objeto de Informacion
-> Modelo de Representacion
-> implementacion fisica candidata
-> legalidad temporal
-> decision de admision
```

Sirve para decidir si el Objeto merece existir institucionalmente.
Solo despues de esta decision puede cerrarse un mapping operativo hacia variables, tablas fuente y State.

Regla:

```text
Las tablas pueden descubrir candidatos.
La admision define el significado.
```

---

## Orden De Trabajo

```text
Phase A cerrada:
    pasos 1-7 completados para los 12 Information Objects principales,
    seguidos de revision transversal y ontology freeze.

Phase B abierta:
    pasos 8-9 ya cubren Operational Mapping y Builder Validation design
    para los 12 Objetos de v1; el builder experimental ya paso contract,
    source binding, path, schema metadata, logical-to-physical binding,
    bounded identity/temporal validation, bounded grain validation y bounded
    quality/lineage validation, core-four builder execution, acceptance review,
    integration design y integration execution con restricciones. El siguiente
    gate posible es `core_four_market_state_materialization_design`, todavia
    sin materializacion parquet ni consumo operativo.
```
```text
1. Revisar tablas existentes como tablas.
2. Identificar que informacion aportan.
3. Extraer candidatos a Objetos de Informacion.
4. Consolidar candidatos repetidos entre tablas.
5. Definir dominio, landscape y candidate object.
6. Revisar adversarialmente el candidato en object_admission_review.
7. Emitir Formal Admission en ACCEPTED / ACCEPTED_WITH_RESTRICTIONS / REJECTED.
8. Mapear Objeto -> modelos -> capacidades -> variables -> tablas -> perfiles de State.
9. Validar que el builder puede resolver el Objeto legalmente.
10. Disenar integracion en Market State.
11. Promover contratos, schemas o builders solo desde la autoridad operativa correspondiente.
12. Construir Event State reutilizando Market State cuando proceda.
```

Cadena logica:

```text
Tablas existentes
-> variables reales
-> Objetos de Informacion candidatos
-> Object Admission Review
-> Formal Admission
-> Operational Mapping
-> Builder Validation
-> Market State Integration
-> promocion operativa si procede
-> Event State
```

Market State no debe nacer de meter todas las columnas disponibles.
Debe nacer de Objetos de Informacion admitidos y legalmente observables en `decision_timestamp`.

## Event State: Rol Temporal Y Legalidad De Consumo

`Event State` usa dos clasificaciones independientes:

```text
state_role
= pre_event | at_event | post_event/post_event_review

consumption_legality
= decision_safe | research_only | outcome_adjacent | prohibited_as_input
```

`post_event` puede existir para investigacion, pero no puede alimentar X predictivo para una decision anterior o tomada en el evento.


## Market State No Es Mega-Tabla

`Market State` debe construirse desde Objetos de Informacion admitidos, pero eso no implica una unica tabla fisica con todos los atributos posibles.

Regla:

```text
canonicalidad
= misma semantica de estado
+ mismo identificador logico
+ reglas temporales comunes
+ perfiles fisicos compatibles

materializacion
= que perfil se construye,
con que cobertura,
resolucion y extension.
```

Perfiles fisicos permitidos conceptualmente:

```text
market_state_core
market_state_daily_context
market_state_intraday
market_state_microstructure_extension
market_state_news_extension
```

Llaves comunes obligatorias entre perfiles:

```text
market_state_id
instrument_id
decision_timestamp
representation_profile_version
```

Regla anti-ruido:

```text
Ningun consumidor justifica por si solo agrandar el Market State canonico.
Si un consumidor necesita informacion pesada o especializada, debe declararse
un perfil/extensibilidad gobernada, no inflar el core universal.
```


---

## Revision De Tablas 000-018

Las carpetas `000-018` viven bajo:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\02_TABLE_REPRESENTATION_REVIEW
```

No son Objetos de Informacion.
Son expedientes tecnicos y auditorias de tablas/salidas.

Su finalidad es determinar:

```text
responsabilidad de la tabla
grano
fronteras
informacion minima
atributos fisicos
candidatos a Objetos de Informacion
redundancias
faltantes
estado institucional
```

| Carpeta | Tabla / salida | Lectura correcta |
| --- | --- | --- |
| `000_instrument_master` | `instrument_master_v0_1` | Identidad/universo de instrumentos. |
| `001_market_calendar` | `market_calendar_v0_1` | Infraestructura temporal canonica. No representa liquidez, momentum o presion compradora. |
| `002_expected_data_calendar` | `expected_data_calendar_v0_1` | Denominador esperado de cobertura. |
| `003_dataset_certification_matrix` | `dataset_certification_matrix_v0_1` | Gobernanza/calidad. No representa un fenomeno de mercado. |
| `004_master_daily_table` | `master_daily_table_v0_1` | Contexto diario del instrumento para su scope declarado. |
| `005_corporate_actions_table` | `corporate_actions_table_v0_1` | Splits, dividendos y cambios de ticker. |
| `006_halts_table` | `halts_table_v0_1` | Halts/suspensions para su scope declarado. |
| `007_event_windows_table` | `event_windows_table_v0_1` | Ventanas de eventos gobernadas. |
| `008_outcomes_table` | `outcomes_table_v0_1` | Outcomes/labels posteriores. No debe alimentar X observable. |
| `009_fundamentals_asof_table` | `fundamentals_asof_table_v0_1` | Contexto fundamental point-in-time/as-of. |
| `010_news_context_table` | `news_context_table_v0_1` | Contexto de noticias con restricciones temporales. |
| `011_short_context_table` | `short_context_table_v0_1` | Short interest/short volume por fuente y lag. |
| `012_regime_context_table` | `regime_context_table_v0_1` | Contexto de regimen observable/as-of. |
| `013_ohlcv_1m_quote_guarded` | `ohlcv_1m_quote_guarded` | Overlay/view quote-guarded sobre raw 1m; no muta raw. |
| `014` | `master_intraday_bar_table` | Representacion intradia basada en barras. |
| `015` | `microstructure_features_table` | Representacion microestructural basada principalmente en trades, quotes y ventanas/timestamps gobernados. |
| `016` | `market_state_table` | Integracion legal en decision_timestamp. No asumir promovido. |
| `017` | `event_state_table` | Market State contextualizado respecto a evento. No asumir promovido. |
| `018` | `intraday_scanner_candidates_table` | Superficie de candidatos/scanners intradia cuando aplique legalmente. |

---

## Objetos De Informacion

Los expedientes viven en:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS
```

Estructura:

```text
03_INFORMATION_OBJECTS/
|-- CANDIDATES/
|-- ACCEPTED/
|-- ACCEPTED_WITH_RESTRICTIONS/
`-- REJECTED/
```

Regla:

```text
todo Objeto de Informacion formalmente evaluado
=
un expediente propio y trazable
```

Un Objeto rechazado tambien debe conservar ficha.

---

## Relacion Correcta 013-018

No debe leerse como una cadena lineal simple.

`014` y `015` son principalmente superficies hermanas.

```text
raw OHLCV 1m
+ 013 quote-guarded overlay
+ corporate actions
+ quality
        |
        v
014 master_intraday_bar_table
```

En paralelo:

```text
raw trades
+ raw quotes
+ eligibility policies
+ quality gates
+ decision timestamps / event windows
        |
        v
015 microstructure_features_table
```

Despues:

```text
000-015 contextos y observables
+ 018 scanner candidates cuando corresponda y sea temporalmente legal
        |
        v
016 market_state_table
```

Y:

```text
016 market_state_table
+ source events
+ 007 event_windows_table
        |
        v
017 event_state_table
```

`008 outcomes_table` permanece separado:

```text
008 outcomes_table
= resultados posteriores / labels / evaluacion
= no input observable directo de Market State
```

---

## Archive

Los documentos en:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\99_archive
```

son historicos, superseded o no activos.

No son autoridad activa.
Solo pueden reutilizarse mediante nueva revision y decision explicita de promocion.

---

## Regla De Consumo

Antes de consumir cualquier salida para research, backtest, ML/RL, Event State o Market State:

```text
leer contrato
leer schema
leer registry
leer consumption policy
leer validators
leer manifest/resumen fisico
confirmar status y scope
```

Nada en esta carpeta, por si solo, promueve una tabla.

---

## Raices Fisicas Relevantes

Raiz fisica verificada en esta instalacion:

```text
G:\TSIS\data\data_foundation_outputs
```

Algunos contratos historicos pueden referenciar:

```text
E:\TSIS\data
```

Antes de afirmar cobertura fisica, verificar la raiz efectiva de esta instalacion.
