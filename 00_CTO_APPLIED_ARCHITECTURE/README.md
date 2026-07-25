# 00_CTO_APPLIED_ARCHITECTURE - Mapa Simple

Status: `readme_v0_43_market_state_bounded_exact_match_reuse_transition_closed`
Date: `2026-07-25`

Current runtime update: `market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1` closed under `03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES` as `CLOSED_APPROVED_REUSE_ELIGIBILITY_TRANSITION_FOR_BOUNDED_EXACT_MATCH_WITH_RESTRICTIONS_NO_PROMOTION`. The bounded candidate dataset `market_state_candidate_dataset_v0_1_433288b634924676` is now eligible only for bounded exact-match reuse via transition record, with 0 baseline registry entry mutations. Official Market State dataset promotion, production, downstream consumption, unbounded reuse and incremental execution remain closed. Next gate: `market_state_on_demand_incremental_overlap_execution_authorization_v0_1`.

Esta carpeta es el mapa de arquitectura aplicada de TSIS.

No es donde viven los datos grandes.
No es donde se ejecutan los builders.
No es la fuente oficial de promocion de datasets.
No sustituye contratos, schemas, registries, validators, manifests ni status matrices.

Sirve para que un humano o agente nuevo entienda como se conectan:

```text
teoria del mercado
representaciones canonicas
gobernanza de materializacion
data RAW observable
capacidades derivables
feature engineering
tablas fuente
Market State
Event State
experimentos
estrategias
```

La regla simple:

```text
Esta carpeta explica y organiza.
La autoridad operativa vive en 01_foundations, builders, validators, manifests y outputs fisicos.
```

---

## Estructura Actual

```text
00_CTO_APPLIED_ARCHITECTURE/
|
|-- 00_EPISTEMOLOGICAL_architecture/
|-- 01_REPRESENTATION_MATERIALIZATION_REVIEW/
|-- 02_MATERIALIZATION_GOVERNANCE_REVIEW/
|-- 03_TABLES_feature_engineering/
|-- 04_DATA_Raw_audit/
|-- 05_DATA_derivable/
|-- 06_DATA_Live_Source/
|-- 07_NEW_STRATEGIES_by_Experiments/
|-- 08_EXPERIMENTS/
|-- 09_STRATEGIES_know/
|-- 99_ZIP/
|-- graphify-out/
|-- AGENTS.md
|-- LOCAL_RULES.md
|-- CHANGELOG.md
`-- README.md
```

---

Current table-level institutional status for `000-018` is maintained in:

```text
C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md
```

That matrix is a reconciliation surface. It does not replace Data Foundation
contracts, dataset registries, validators, manifests or consumption policies,
and it does not promote official datasets by itself.
The matrix separates physical, semantic and execution authority axes so a physical artifact cannot be mistaken for semantic profile authority or execution permission.

Evidence reconciliation against Data Foundation closed with `tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z`. It recorded 19/19 table rows with evidence, kept `official_datasets_inferred = 0`, and left promotion, production, official parquet and downstream consumption closed.

Event Type Registry seed design is closed under `03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION`; the first candidate population and initial admission review are recorded there. `event_type:market_data:session_opened` is `accepted_with_restrictions`, the Event Instance, Event Window, Market State compatibility, instrument-session projection and Event State integration designs are recorded, the execution-chain joint review is closed, and the first bounded execution-chain run `event_state_bounded_execution_chain_execution_v0_1_20260724T185356Z` closed with 8 non-official Event State candidate records, 1 blocked context and 0 hard validation failures. Physical validation run `event_state_bounded_execution_chain_physical_validation_v0_1_20260724T193214Z` checked those 8 records with 0 schema, hash, fingerprint, binding, lineage, authority, determinism or hard validation failures. Candidate dataset review run `event_state_candidate_dataset_review_v0_1_20260724T194315Z` approved the 8-record output as bounded candidate Event State evidence with restrictions and no promotion. Profile promotion review run `event_state_profile_promotion_review_v0_1_20260724T201046Z` approved semantic Event State profile promotion with restrictions; promotion run `event_state_profile_promotion_v0_1_20260724T203016Z` registered `event_state_core_four_intraday_profile_v0_1` as an official semantic Event State profile with restrictions; artifact validation run `event_state_profile_artifact_validation_v0_1_20260724T204410Z` checked 4 registry artifacts with 0 hash mismatches, 0 invariant failures and 0 hard validation failures; operational registry / consumption policy design `event_state_operational_registry_or_consumption_policy_design_v0_1` now allows only semantic profile reference for planning and keeps Event State physical consumption closed. Runtime capabilities architecture is recorded in `03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES` as the bridge from semantic profiles to request/resolver/materializer/validator/registry capability design, with no execution. Market State on-demand capability design is now closed under Runtime Capabilities and has completed its first bounded execution run `market_state_bounded_on_demand_execution_v0_1_20260724T232123Z` with 1 request, 1 execution plan, 8 candidate Market State rows, 1 unavailable context, 1 candidate parquet, 1 candidate registry entry and 0 hard validation failures; candidate dataset review `market_state_bounded_on_demand_candidate_dataset_review_v0_1` approved it as bounded candidate evidence with restrictions and no promotion; deterministic rerun and determinism validation are closed, and idempotency/reuse test run `market_state_bounded_on_demand_idempotency_reuse_test_v0_1_20260725T060318Z` proved bounded exact-match reuse without rebuilding. Reuse eligibility transition review `market_state_bounded_on_demand_reuse_eligibility_transition_review_v0_1_20260725T061233Z` approved bounded exact-match reuse only; incremental overlap execution still requires explicit authorization. `event_type:regulatory:halt_resumed` remains `investigational_candidate` blocked by timestamp/source availability findings. Detection outside `session_opened`, unbounded execution, official Event State dataset promotion, materialization, production and downstream consumption remain closed.

Variable and Attribute Admission Policy is now recorded under `03_TABLES_feature_engineering/02_VARIABLE_AND_ATTRIBUTE_ADMISSION_POLICY_v0_1.md`, with proposal template `03_TABLES_feature_engineering/03_VARIABLE_ATTRIBUTE_ADMISSION_RECORD_TEMPLATE_v0_1.md`. Together they consolidate the bridge between Data Foundation physical attributes, Applied Architecture semantic admission, Operational Mapping and Execution authorization. They do not admit variables, change schemas, promote datasets or authorize consumption.

---

## Flujo Mental Correcto

```text
00_EPISTEMOLOGICAL_architecture
Que significan representacion, feature, evento, estado, outcome y conocimiento?

        ->

01_REPRESENTATION_MATERIALIZATION_REVIEW
Como una representacion canonica podria convertirse en artefacto fisico?

        ->

02_MATERIALIZATION_GOVERNANCE_REVIEW
Como se gobierna esa conversion con contratos, records, reviews y autorizaciones?

        ->

04_DATA_Raw_audit
Que data original observable existe realmente?

        ->

05_DATA_derivable
Que capacidades derivables pueden calcularse legalmente desde esa data?

        ->

03_TABLES_feature_engineering
Que significado tienen esas capacidades, que Objetos de Informacion merecen existir y donde viven fisicamente?

        ->

Market State / Event State
Que informacion admitida se integra legalmente en un decision_timestamp?

        ->

08_EXPERIMENTS / 07_NEW_STRATEGIES_by_Experiments / 09_STRATEGIES_know
Como se investiga, valida y convierte conocimiento en estrategia?
```

---

## Arquitectura Global De Representacion

Este arbol resume como TSIS transforma el mercado real en estados consumibles por investigacion, backtest, ML/RL y estrategias.

| Capa | Pregunta que responde |
| --- | --- |
| Mercado | Que existe realmente antes de que TSIS lo observe? |
| Fenomeno observable | Que comportamiento, condicion o cambio ocurre en el mercado? |
| RAW observable | Que evidencia fuente tenemos para observarlo sin interpretarlo? |
| Capacidad derivable | Que podemos calcular legalmente desde esa evidencia? |
| Objeto de Informacion | Que propiedad cientifica merece conservar TSIS sobre ese fenomeno? |
| Modelo de Representacion | Con que combinacion minima de medidas representamos ese Objeto? |
| Variables / atributos fisicos | Que columnas concretas implementan ese modelo? |
| Tablas fuente | Donde viven fisicamente esas variables y con que grano? |
| State Builder | Como se integran legalmente esas variables en un decision_timestamp? |
| Market State / Event State | Que estado observable queda disponible para decision, investigacion o aprendizaje? |

Cadena corta:

```text
Mercado
-> Fenomeno observable
-> RAW observable
-> Capacidad derivable
-> Objeto de Informacion
-> Modelo de Representacion
-> Variables / atributos fisicos
-> Tablas fuente
-> State Builder
-> Market State / Event State
```

Regla clave:

```text
No toda capacidad derivable debe usarse.
No toda variable merece entrar en State.
No toda tabla es una representacion canonica.
```

Primero se prueba que algo existe y puede calcularse.
Despues se decide si tiene significado suficiente para representar el estado.


Taxonomia minima:

```text
information_object_family
= significado semantico.

source_domain
= fuente observable.

temporal_resolution
= escala temporal.

institutional_role
= rol dentro del sistema.
```

No usar una sola palabra `family` para mezclar esos cuatro ejes.


Market State anti-mega-table rule:

```text
Canonical Market State no significa una fila fisica con toda la informacion existente.

Canonical Market State significa:
- una semantica unica de estado;
- un identificador estable de estado;
- reglas temporales comunes;
- perfiles de representacion fisica compatibles.
```

Ejemplo de perfiles compatibles:

```text
market_state_core
market_state_daily_context
market_state_intraday
market_state_microstructure_extension
market_state_news_extension
```

Todos deben vincularse mediante:

```text
market_state_id
instrument_id
decision_timestamp
representation_profile_version
```
---

## 00_EPISTEMOLOGICAL_architecture

Es la base teorica.

Explica como TSIS entiende:

```text
representaciones
features
eventos
fenomenos
estados
outcomes
causalidad
observabilidad
descubrimiento cientifico
sistemas autonomos de investigacion
```

En palabras simples:

```text
Aqui se define el idioma mental de TSIS.
```

No crea tablas.
Define que significan las cosas antes de construirlas.

---

## 01_REPRESENTATION_MATERIALIZATION_REVIEW

Explica el puente entre una representacion canonica y su posible materializacion fisica.

Responde:

```text
Por que existe una representacion?
Debe materializarse?
Que significa convertirla en tabla, schema, builder, validator o manifest?
```

En palabras simples:

```text
Aqui se estudia como una idea puede llegar a convertirse en artefacto fisico.
```

---

## 02_MATERIALIZATION_GOVERNANCE_REVIEW

Contiene la aplicacion practica del proceso anterior.

Aqui se trabajaron casos reales como:

```text
Market State
Event State
```

Y se generaron artefactos de gobernanza como:

```text
RJR - Representation Justification Record
MDR - Materialization Decision Record
mapping canonico a fisico
autorizacion de candidate build
freeze records
review patterns
```

En palabras simples:

```text
Aqui se decide, con evidencia, si una representacion merece existir y si puede empezar a construirse.
```

Importante:

```text
autorizar candidate build != promocionar tabla oficial
```

---

## 03_TABLES_feature_engineering

Es la capa donde se conecta la representacion del mercado con tablas, variables y Objetos de Informacion.

Responde principalmente:

```text
Que necesitamos saber para describir correctamente
el estado del mercado en un instante t?
```

Y tambien:

```text
Que informacion puede ayudar a describir, explicar o investigar
el comportamiento futuro del mercado, del instrumento o del contexto estudiado?
```

Contiene:

```text
00_TABLES_MARKET_STATE_EVENT_STATE.md
01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
02_TABLE_REPRESENTATION_REVIEW/
03_INFORMATION_OBJECTS/
99_archive/
```

Lectura simple:

```text
02_TABLE_REPRESENTATION_REVIEW/
= audita tablas completas 000-018.

03_INFORMATION_OBJECTS/
= guarda expedientes de Objetos de Informacion.

01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
= decide si un Objeto como Liquidity, Momentum o Trading Activity merece existir.
```

Regla clave:

```text
Tabla != Objeto de Informacion.
```

Una tabla puede contener atributos de varias familias.
Una misma familia puede estar repartida entre varias tablas.

---

## 04_DATA_Raw_audit

Revisa la data original observable.

Ejemplos:

```text
trades
quotes
OHLCV daily
OHLCV 1m
reference
halts
short
additionals
```

Responde:

```text
Que campos existen?
Que granularidad tienen?
Que cobertura poseen?
Que calidad presentan?
Que consumo esta autorizado?
```

En palabras simples:

```text
Aqui se mira la materia prima antes de derivar nada.
```

---

## 05_DATA_derivable

Registra capacidades tecnicas de derivacion.

Responde una sola pregunta:

```text
Con la RAW data o data gobernada disponible actualmente en TSIS,
que capacidades de derivacion y observables pueden calcularse legalmente?
```

Documentos activos:

```text
00_DATA_DERIVABLE_CATALOG_BY_RAW_SOURCE_v0_1.md
01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md
02_DERIVABLE_CAPABILITY_STATUS_MATRIX_v0_1.md
```

Regla central:

```text
Una capacidad de derivacion no implica que deba utilizarse
para representar el estado del mercado.
```

Esta carpeta no decide:

```text
familia semantica
Objeto de Informacion
utilidad cientifica
pertenencia a Market State
pertenencia a Event State
```

Eso se decide despues en `03_TABLES_feature_engineering`.

---

## 06_DATA_Live_Source

Estudia fuentes live o casi live.

Ejemplos:

```text
DAS
Interactive Brokers
TradeStation
L2
L3
scanners
```

En palabras simples:

```text
Aqui se estudia de donde podria venir informacion en tiempo real.
```

Se separa de `04_DATA_Raw_audit` porque data historica y data live tienen riesgos, latencias y contratos distintos.

---

## 07_NEW_STRATEGIES_by_Experiments

Guarda estrategias nuevas nacidas de evidencia experimental.

No es una carpeta para ideas sueltas.

En palabras simples:

```text
Una estrategia nueva debe salir de experimentos y evidencia, no solo de intuicion.
```

---

## 08_EXPERIMENTS

Contiene experimentos reproducibles.

Un experimento responde preguntas concretas:

```text
Este evento tiene comportamiento repetible?
Esta representacion ayuda a encontrar edge?
Este detector funciona bajo condiciones controladas?
Este Objeto de Informacion reduce incertidumbre relevante?
```

En palabras simples:

```text
Aqui se prueban hipotesis de forma trazable.
```

---

## 09_STRATEGIES_know

Conserva conocimiento de estrategias conocidas o estudiadas.

No equivale a estrategia validada.
No sustituye experimentos.
No promociona conocimiento por si misma.

En palabras simples:

```text
Aqui se ordena conocimiento estrategico existente.
```

---

## 99_ZIP

Contiene paquetes comprimidos o snapshots de entrega.

Regla:

```text
si existe una carpeta viva y tambien un zip,
trabaja con la carpeta viva.
```

El zip es copia, paquete o evidencia de intercambio.
No es el lugar natural para editar.

---

## graphify-out

Contiene el grafo semantico generado por Graphify.

Sirve para navegacion conceptual:

```text
que documento se relaciona con que concepto?
donde aparece una idea?
que carpetas conectan con una representacion?
```

No prueba por si solo:

```text
promocion de dataset
validacion fisica
completitud full-universe
schema PASS
```

Para eso mandan manifests, validators, status matrices y evidencia fisica.

---

## Regla De Autoridad

Esta carpeta es una capa secundaria de arquitectura aplicada.

La autoridad operativa final vive principalmente en:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts
C:\TSIS_Data\data\data_foundation_outputs
G:\TSIS\data\data_foundation_outputs
builders
validators
manifests
status matrices
tests
```

Si este README o cualquier documento de arquitectura aplicada contradice un contrato, schema, registry, validator, manifest o status matrix oficial, gana la evidencia operativa.

---

## Orden Recomendado Para Un Agente Nuevo

```text
1. Leer AGENTS.md y LOCAL_RULES.md de esta carpeta.
2. Leer este README.
3. Leer 00_EPISTEMOLOGICAL_architecture si necesita entender conceptos.
4. Leer 01_REPRESENTATION_MATERIALIZATION_REVIEW si trabaja con representaciones canonicas.
5. Leer 02_MATERIALIZATION_GOVERNANCE_REVIEW si trabaja con RJR, MDR, mapping o autorizaciones.
6. Leer 04_DATA_Raw_audit si necesita saber que data original existe.
7. Leer 05_DATA_derivable si necesita saber que se puede calcular legalmente.
8. Leer 03_TABLES_feature_engineering si trabaja con tablas 000-018, Objetos de Informacion, Market State o Event State.
9. Verificar siempre contratos, schemas, registries, validators, manifests y status matrices antes de afirmar estado oficial.
```

---

## Idea Principal

```text
No empezamos por meter columnas en tablas.

Empezamos por significado.
Despues revisamos que data existe.
Despues declaramos que se puede derivar legalmente.
Despues decidimos que informacion merece representar el estado.
Despues ubicamos variables en tablas fuente.
Despues construimos Market State y Event State.
Despues investigamos y validamos.
```

Ese es el papel de `00_CTO_APPLIED_ARCHITECTURE`:

```text
hacer que TSIS avance sin perder significado, trazabilidad ni separacion entre capas.
```


## 2026-07-24 Event State Window Design Note

`03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION/event_window_binding_design_readout_v0_1.md` records design-only Event Window Binding for `event_type:market_data:session_opened` under `exchange_session` scope. It creates no Event Windows, no Event Instances, no Event State materialization and no downstream consumption.


## 2026-07-24 Event State Compatibility Note

`03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION/market_state_profile_compatibility_design_readout_v0_1.md` records semantic compatibility between `event_state_core_four_intraday_profile_v0_1` and `market_state_core_four_intraday_profile_v0_1` with restrictions. It does not authorize Market State physical consumption or Event State execution and requires future instrument-session projection design.


## 2026-07-24 Event State Projection Note

`03_TABLES_feature_engineering/07_EVENT_STATE_INTEGRATION/event_state_instrument_session_projection_design_readout_v0_1.md` records design-only projection from exchange-session Event Instance/Event Window Binding to instrument-session Market State context. It creates no projections and authorizes no Event State execution.
