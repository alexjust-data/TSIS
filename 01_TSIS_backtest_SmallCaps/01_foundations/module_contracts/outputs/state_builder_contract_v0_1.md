# State Builder Contract v0.1

## Estado

Tipo: state builder contract.  
Modulo: `01_TSIS_backtest_SmallCaps`.  
Ambito: `CAPA 1 - DATA FOUNDATION`.  
Fecha: 2026-07-04.  

Status:

```text
contract_defined
state_builder_contract_complete_for_declared_scope = true
official_state_builder_implemented = false
fixture_builder_implemented = true
controlled_candidate_builder_implemented = true
market_state_table_materialized = false
event_state_table_materialized = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

Este contrato define como debe ensamblarse una fila futura de  
`market_state_table` o `event_state_table` desde observables elegibles,  
formulas versionadas, timestamps legales y roles de snapshot.  

No materializa la tabla oficial.   
No promociona los candidatos existentes.   
No elige factores ganadores.   
No crea outcomes, rewards, acciones, semantic states, transitions ni evaluadores AlphaEvolve.    

Regla corta:

```text
state builder = ensamblador determinista y auditable
state builder != cientifico que decide que importa
state builder != scanner
state builder != evaluador
state builder != estrategia
```

## 1. Fuentes Normativas

El builder debe consumir estos contratos como inputs normativos:

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/market_state_table_validators.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/event_state_table_validators.md
```

Evidencia operativa existente:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/_state_fixture_builder.py
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_market_state_table.py
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/scripts/materialize_event_state_table.py
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/market_state_builder_fixture_v0_1.json
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/event_state_builder_fixture_v0_1.json
```

Lectura correcta:

```text
los scripts actuales prueban fixture/candidate controlado;
este contrato gobierna el siguiente builder general;
ningun script actual convierte el output oficial en materializado/promovido.
```

## 2. Objetivo Del Builder

El builder debe responder de forma reproducible:

```text
Para este instrumento, en este decision timestamp, bajo este rol,
que observables legales as-of puedo ensamblar,
de que componente vienen,
con que formula si son derivados,
con que cutoff,
con que calidad,
y bajo que restricciones de consumo?
```

La salida esperada es una fila de estado:

```text
market_state row
= identity + calendar + componentes observables + calidad + lineage + gates
```

Y, si hay evento:

```text
event_state row
= market_state row/link
+ event metadata conocida <= cutoff
+ event/window references
+ state_role
+ leakage gates
```

## 3. Flujo Correcto

```text
componentes fuente
-> contrato de elegibilidad de observables
-> contrato de formulas derivadas
-> politica de decision timestamp
-> contrato de roles de snapshot
-> state builder config
-> ensamblaje determinista
-> validators de leakage/calidad/lineage
-> manifest de build
-> market_state/event_state candidate
```

Outcomes y evaluadores quedan despues:

```text
state rows = X bajo cutoff legal
outcomes/labels/rewards = y separado
fitness/evaluator = capa posterior
```

## 4. Modos Permitidos

| Modo | Uso | Estado | Puede escribir oficial? |
| --- | --- | --- | --- |
| `contract_check_only` | comprobar que contratos requeridos existen y son coherentes | permitido | no |
| `deterministic_fixture_only` | fixture pequeno bajo `tests/test_runs` | implementado | no |
| `controlled_candidate` | muestra candidate controlada con manifest, sin promocion | implementado para microstructure/halt; ampliable | no |
| `official_candidate` | candidato multi-componente mas rico contra outputs CAPA 1 | futuro | no, salvo path candidate explicito |
| `official_promoted` | tabla institucional final | bloqueado | solo tras promotion barrier |

Regla:

```text
default official_output_allowed = false
full_universe_claim = false salvo contrato especifico
valid_for_rl_training_direct = false
execution_truth = false
```

## 5. Config Minima Del Builder

Todo builder debe ejecutarse desde una config versionada. No hay defaults
silenciosos que incluyan todas las tablas.

Campos minimos:

| Campo | Obligatorio | Que gobierna |
| --- | --- | --- |
| `dataset_id` | si | `market_state_table_v0_1` o `event_state_table_v0_1` |
| `builder_version` | si | version exacta del builder |
| `materialization_scope` | si | fixture, controlled candidate, official candidate, etc. |
| `mode` | si | modo permitido de la seccion 4 |
| `official_output_allowed` | si | debe ser `false` hasta promotion barrier |
| `output_root` | si para writes | raiz permitida del output |
| `source_components` | si | componentes, roots, manifests, schemas y source states |
| `observable_eligibility_contract` | si | contrato de columnas/observables permitidos |
| `derived_formula_contract` | si | formulas permitidas para derivadas |
| `decision_timestamp_policy` | si | tipos de timestamp y cutoff |
| `snapshot_roles_contract` | si | roles permitidos y reglas por rol |
| `component_join_policy` | si | como se elige row as-of por componente |
| `required_components` | si | componentes que bloquean si faltan |
| `optional_components` | si | componentes que pueden quedar missing/review |
| `allowed_namespaces` | si | namespaces de feature permitidos |
| `selected_observables` | si | lista de observables finales que se van a emitir |
| `selected_formulas` | si si hay derivadas | formula ids/versiones usadas |
| `timestamp_type` | si | tipo de decision timestamp |
| `state_roles` | si para roles/event_state | roles canonicos permitidos |
| `prohibited_prefixes` | si | `outcome__`, `label__`, `reward__`, etc. |
| `consumer_gate_defaults` | si | flags ML/RL/backtest/execution por defecto |
| `manifest_policy` | si | hashes, build ids, source manifests |
| `validator_policy` | si | validators hard/review requeridos |

## 6. Source Component Registry

La config debe declarar cada componente asi:

```text
component_name
source_dataset_id
source_schema_path
source_data_root_or_file
source_manifest_path
source_build_run_id
source_quality_state
source_root_state
as_of_column_or_policy
join_keys
required_or_optional
allowed_for_scope
```

Componentes base actuales:

| Componente | Uso en builder | Regla |
| --- | --- | --- |
| `identity` | identidad ticker/instrument | required para cualquier state row |
| `calendar` | sesiones, segmentos, clocks | required para timestamps intradia |
| `daily` | contexto diario e historico | required u optional segun scope |
| `intraday` | barras 1m y estado vivo agregado | required para estrategias 1m |
| `microstructure` | quotes/trades/tape por ventana | required solo en scopes de segundos/microestructura |
| `halt` | halt/resume/suspension context | required si event family depende de halts |
| `fundamentals` | filing/as-of context | optional o required segun estrategia/scope |
| `news` | published/as-of catalyst context | optional o required segun estrategia/scope |
| `short_context` | short interest/volume con lag | optional, no borrow/SSR |
| `short_constraints` | SSR/borrow/locate | blocked hasta fuente materializada |
| `regime` | contexto regimen/session | optional con cutoff estricto |
| `quality` | gates, coverage, lineage | required |

## 7. Seleccion De Observables

El builder solo puede emitir observables declarados en
`state_observable_eligibility_contract_v0_1.md` o en una version posterior
aprobada.

Reglas:

```text
eligible_now -> puede entrar si pasa cutoff/calidad
eligible_with_cutoff_restriction -> puede entrar solo bajo la restriccion declarada
candidate_requires_formula -> necesita formula en formula contract
candidate_requires_materialization -> no entra hasta que el componente exista
blocked_no_source / blocked_no_materialized_table -> no entra
future_no_namespace -> no entra como namespace actual
support_only / lineage_only / quality_only -> puede gobernar la fila, no es alpha
```

El builder no decide que observable es cientificamente mejor. Solo comprueba si
esta permitido para el scope solicitado.

## 8. Formulas Derivadas

Un observable derivado solo puede emitirse si:

```text
existe en state_derived_observables_formula_contract_v0_1.md
o en una version/candidate posterior declarada en config;
la formula tiene inputs legales;
la ventana queda cerrada <= decision_timestamp_utc;
la formula no usa outcomes, rewards, labels, fills ni datos posteriores;
la formula id/version queda en manifest.
```

Ejemplo de lectura correcta:

```text
rvol_20d no significa "mejor RVOL".
rvol_20d significa "derivada versionada con ventana 20d y formula concreta".
```

Si AlphaEvolve, una estadistica de estrategia o un investigador propone otra
ventana, no se cambia silenciosamente la fila existente. Debe nacer como:

```text
nuevo observable candidate
o nueva formula candidate
o nueva version del formula contract
```

## 9. Decision Timestamp Y Cutoff

El builder debe calcular y conservar:

```text
decision_timestamp_utc
state_cutoff_utc
state_cutoff_reason
timestamp_type
timestamp_policy_version
component_as_of_bundle
max_component_as_of_utc
component_cutoff_violation_count
```

Hard rule:

```text
component_as_of_utc <= decision_timestamp_utc
```

Si una fuente usa fecha y no timestamp, la config debe apuntar a la policy de
availability/lag correspondiente.

Prohibido:

```text
usar daily close final antes del cierre
usar volumen final de sesion antes de estar disponible
usar regime close same-session antes de disponibilidad
usar news/fundamentals por period_end si published/filing/as_of era posterior
```

## 10. Roles De Snapshot

El builder debe consumir `state_snapshot_roles_contract_v0_1.md` y declarar:

```text
state_roles_contract_id
state_role
role_family
allowed_timestamp_type
state_cutoff_rule
allowed_window_policy
outcome_join_policy
required_role_validators
```

Roles canonicos para trabajo nuevo:

```text
DISCOVERY_STATE
EVENT_ANCHOR_STATE
ENTRY_DECISION_STATE
RISK_STATE
EXECUTION_STATE
RL_TRANSITION_STATE
POST_EVENT_ANALYSIS_STATE
```

Compatibilidad legacy:

```text
pre_event
at_event
post_event_review
research_replay
```

Los valores legacy existen en schemas/configs anteriores. El builder nuevo no
debe adivinar su equivalencia. Toda config que consuma valores legacy debe
declarar un `state_role_alias_map` explicito.

Ejemplos permitidos solo si la config lo declara:

| Legacy alias | Posible rol canonico | Caveat |
| --- | --- | --- |
| `post_event_review` | `POST_EVENT_ANALYSIS_STATE` | research only, no X pre-decision |
| `research_replay` | `DISCOVERY_STATE` | no decision operacional por defecto |
| `pre_event` | `EVENT_ANCHOR_STATE` o `ENTRY_DECISION_STATE` | depende del timestamp y del uso |
| `at_event` | `EVENT_ANCHOR_STATE` | solo si el evento era conocido en `t` |

## 11. Ensamblaje De `market_state_table`

Orden minimo:

```text
1. construir decision frame: instrument_id + decision_timestamp_utc + horizon/scope
2. validar identity/calendar requeridos
3. seleccionar cada componente por as-of legal
4. filtrar observables por eligibility contract
5. calcular derivadas declaradas por formula contract
6. aplicar namespaces permitidos
7. calcular component availability/quality states
8. aplicar leakage/timestamp/role validators
9. generar stable market_state_id
10. emitir row + manifest solo si el modo permite write
```

No se copian fuentes enteras. Se emiten observables seleccionados y gobernados.

Required namespaces actuales:

```text
identity__
calendar__
scanner__
daily__
intraday__
microstructure__
halt__
fundamentals__
news__
short_context__
short_constraints__
regime__
quality__
```

## 12. Ensamblaje De `event_state_table`

Orden minimo:

```text
1. cargar event/window frame permitido
2. validar event timestamp, event window y state_role
3. derivar decision_timestamp_utc segun timestamp policy
4. buscar o construir market_state compatible
5. validar market_state_id y cutoff legal
6. agregar event__ metadata conocida <= cutoff
7. conservar outcome_join_key/label_join_key solo como llaves
8. prohibir outcome/label/reward values inline
9. generar stable event_state_id
10. emitir row + manifest solo si el modo permite write
```

`event_state_table` puede llevar un subconjunto controlado de market_state
features, pero debe preservar namespaces originales y agregar `event__` solo
para metadata conocida legalmente.

## 13. IDs Estables

La identidad debe ser reproducible:

```text
market_state_id = hash(dataset_id, instrument_id, decision_timestamp_utc, state_horizon, state_scope, state_schema_version, builder_version)
```

```text
event_state_id = hash(dataset_id, event_window_id, market_state_id, decision_timestamp_utc, state_role, state_schema_version, builder_version)
```

La implementacion puede anadir campos al hash si la config lo declara, pero no
puede depender del orden fisico de lectura ni de timestamps de ejecucion.

## 14. Component Availability Y Quality

Cada componente debe quedar marcado:

```text
included_good
included_review
missing_optional
missing_required
blocked_by_policy
not_requested
not_available
```

Quality states minimos heredan de los schema contracts:

```text
state_good_for_declared_cutoff
state_review_missing_optional_component
state_review_scoped_intraday_component
state_review_microstructure_seed_only
state_review_short_constraints_missing
state_blocked_future_information_detected
state_blocked_required_component_missing
state_blocked_invalid_component_quality
state_bad_duplicate_state_id
state_bad_missing_decision_timestamp
```

Para event_state se usa el prefijo `event_state_` cuando corresponda.

## 15. Consumer Gates

El builder debe emitir gates explicitos. Defaults:

```text
valid_for_event_context_candidate = false salvo scope declarado
valid_for_pattern_discovery = false salvo event_state scope declarado
valid_for_ml_feature_candidate = false salvo role/cutoff/schema/validator pass
valid_for_backtest_context_candidate = false salvo policy declarada
valid_for_rl_state_candidate = false salvo transition path futuro
valid_for_rl_training_direct = false
valid_for_execution_context_candidate = false salvo execution contract futuro
valid_for_execution_simulator_direct = false
execution_truth = false
full_universe_claim = false
requires_asof_filter = true
contains_future_information_without_event_filter = false solo si validators pasan
```

Un builder no puede subir gates por conveniencia. Debe justificarlo en config,
manifest y validators.

## 16. Manifest Obligatorio

Cada build que escriba muestra o candidato debe emitir manifest con:

```text
dataset_id
candidate_dataset_id si aplica
builder_version
builder_contract_version
materialization_scope
mode
official_output_allowed
official_output_materialized
full_universe_claim
created_at_utc
build_run_id
source_components
source_schema_paths
source_manifest_paths
source_manifest_sha256_bundle
source_build_run_id_bundle
source_root_states
observable_eligibility_contract_sha256
derived_formula_contract_sha256
decision_timestamp_policy_sha256
snapshot_roles_contract_sha256
selected_observables
selected_formulas
state_role_alias_map si aplica
timestamp_type
component_as_of_policy_bundle
quality_policy_version
leakage_policy_version
validator_results
row_count
quality_counts
consumer_gate_counts
output_tree_sha256 si escribe parquet/jsonl
requires_rebuild_after_source_parity si aplica
```

## 17. Validators Que Deben Cerrar El Siguiente Paso

Despues de este contrato, los validators deben comprobar como minimo:

| Validator | Debe fallar si |
| --- | --- |
| `builder_bad_missing_contract_input` | falta eligibility/formula/timestamp/roles/composition contract |
| `builder_bad_uneligible_observable` | se emite observable no elegible para scope |
| `builder_bad_formula_not_declared` | derivada sin formula/version |
| `builder_bad_formula_window_leakage` | ventana usa datos posteriores a `t` |
| `builder_bad_component_asof_leakage` | componente as-of posterior a decision timestamp |
| `builder_bad_unknown_state_role` | rol no canonico ni alias declarado |
| `builder_bad_role_timestamp_mismatch` | rol y timestamp incompatibles |
| `builder_bad_role_window_mismatch` | ventana no permitida por rol |
| `builder_bad_prohibited_prefix` | aparece `outcome__`, `label__`, `reward__`, etc. |
| `builder_bad_outcome_inline` | outcome/label/reward value dentro de state row |
| `builder_bad_short_context_as_constraints` | short_context usado como borrow/SSR/locate |
| `builder_bad_full_universe_claim` | full universe sin contrato/cobertura/promocion |
| `builder_bad_official_write` | write oficial sin promotion barrier |
| `builder_bad_manifest_missing_hashes` | falta lineage/hash/version de componentes |
| `builder_bad_non_deterministic_rebuild` | fixture/candidate no recomputa identico |

## 18. Relacion Con Candidatos Existentes

Candidatos existentes:

```text
market_state_table_v0_1_candidate_microstructure_halt_controlled
event_state_table_v0_1_candidate_microstructure_halt_controlled
```

Lectura correcta:

```text
son integration proof controlado;
no son tabla oficial;
no son full universe;
no son ML/RL ready;
heredan lineage provisional D:/quotes;
requieren rebuild tras E:/TSIS/data/quotes_ parity.
```

El builder general debe poder aprender de esa evidencia, pero no puede copiar su
scope como si fuese institucional.

## 19. Relacion Con AlphaEvolve / ML / RL

AlphaEvolve puede proponer:

```text
nuevas formulas derivadas
nuevas representaciones semanticas
nuevos detectores de eventos
nuevas funciones de transicion
nuevas politicas/evaluadores
```

Pero el state builder solo puede consumir lo que este contratado:

```text
observable elegible
formula declarada
timestamp legal
role permitido
validator pass
manifest reproducible
```

ML supervisado:

```text
X = market_state/event_state bajo cutoff legal
y = outcomes/labels separados
```

RL:

```text
state(t), action(t), reward(t), state(t+1)
```

es capa posterior gobernada por `state_transition_contract_v0_1.md`, no por este
contrato.

## 20. Fuera De Alcance

No queda resuelto por este contrato:

```text
1. implementar el builder general multi-componente
2. crear market_state/event_state schema candidate nuevos
3. crear fixtures controlados nuevos para todos los componentes
4. implementar validators ejecutables de leakage/calidad/lineage
5. materializar candidate multi-componente rico
6. promocionar tablas oficiales
7. construir outcomes separados
8. cerrar evaluadores bloqueados
9. crear semantic state representations
10. crear transition datasets/evaluators
11. habilitar AlphaEvolve/RL/ML production use
```

## 21. Acceptance Criteria v0.1

| Criterio | Estado |
| --- | --- |
| objetivo del state builder definido | `done` |
| inputs normativos declarados | `done` |
| modos permitidos/bloqueados definidos | `done` |
| config minima definida | `done` |
| reglas de component registry definidas | `done` |
| consumo de eligibility/formula/timestamp/roles definido | `done` |
| ensamblaje market_state definido | `done` |
| ensamblaje event_state definido | `done` |
| manifest obligatorio definido | `done` |
| validators del siguiente paso definidos | `done` |
| relacion con candidatos existentes aclarada | `done` |
| no materializa oficial ni habilita ML/RL/AlphaEvolve | `done` |

Status final:

```text
state_builder_contract_v0_1 = complete_for_contract_defined_scope
```