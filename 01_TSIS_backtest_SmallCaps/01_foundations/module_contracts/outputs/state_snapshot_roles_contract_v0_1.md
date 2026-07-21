# State Snapshot Roles Contract v0.1

## Estado

Tipo: state snapshot roles contract.
Modulo: `01_TSIS_backtest_SmallCaps`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Fecha: 2026-07-04.

Status:

```text
contract_defined
snapshot_roles_complete_for_declared_scope = true
state_builder_materialized = false
market_state_table_materialized = false
event_state_table_materialized = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

Este contrato cierra el significado operativo de `state_role` para futuras filas
de `market_state_table` y `event_state_table`.

No materializa datos. No crea un builder. No promociona `market_state_table` ni
`event_state_table`. No define estrategia, accion, outcome, reward ni politica
operativa. Define para que se toma un snapshot, que timestamp puede usar, que
ventanas puede mirar y que joins quedan permitidos por rol.

## Nota De Versionado Y Variabilidad

Este contrato no debe leerse como una lista fija e inmutable de roles. Es la
version `v0.1` de los roles necesarios para avanzar al state builder sin mezclar
investigacion, decision, ejecucion, outcomes, RL o post-analysis.

Durante el desarrollo de TSIS pueden aparecer roles nuevos o variantes si el
proyecto lo exige:

```text
nuevas familias de eventos
nuevas estrategias
nuevas necesidades de ejecucion
nuevos simuladores
nuevos datasets de transicion RL
nuevas representaciones semanticas
nuevas propuestas de AlphaEvolve
nuevos evaluadores bloqueados
```

Pero ningun rol puede entrar de forma silenciosa. Todo rol nuevo o variacion de
rol debe declararse con:

```text
motivo
timestamp types permitidos
ventanas permitidas
joins permitidos
outcomes/rewards permitidos o prohibidos
uso ML/RL/AlphaEvolve permitido
leakage gates requeridos
compatibilidad con builders y schemas existentes
criterio de promocion o rechazo
```

## Fuentes Normativas

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```

## Principio Central

```text
state_role = por que existe este snapshot y que relacion temporal/operativa tiene.
consumption_legality = si esa fila puede consumirse como input, solo como research, cerca de outcome o nunca como input.
```

`state_role` no cambia la verdad observable. Describe el rol del snapshot.
`consumption_legality` separa la legalidad de consumo downstream.

Juntos determinan:

```text
el punto de corte temporal
las ventanas permitidas
los joins permitidos
si puede tocar eventos
si puede tocar outcomes separados
si puede usarse para ML/RL/AlphaEvolve
que validators deben pasar
```

Regla corta:

```text
misma fotografia observable + distinto rol = distinto contrato de uso.
```

## 1. Modelo De Rol

Todo rol debe declarar como minimo:

| Campo | Que significa |
| --- | --- |
| `state_role` | nombre canonico del rol |
| `role_family` | discovery, event, decision, risk, execution, rl, post_analysis |
| `consumption_legality` | decision_safe, research_only, outcome_adjacent, prohibited_as_input |
| `allowed_timestamp_types` | timestamps permitidos desde `state_decision_timestamp_policy_v0_1.md` |
| `state_cutoff_rule` | como se fija `state_cutoff_utc` |
| `allowed_windows` | ventanas que puede mirar |
| `event_anchor_required` | si requiere evento/ancla |
| `outcome_join_key_allowed` | si puede conservar llave para join posterior |
| `outcome_values_inline_allowed` | debe ser false para estados base |
| `label_columns_inline_allowed` | debe ser false para estados base |
| `reward_columns_inline_allowed` | debe ser false para estados base |
| `allowed_for_market_state` | si puede usarse como contexto de market_state candidate |
| `allowed_for_event_state` | si puede usarse como event_state candidate |
| `allowed_for_ml` | si puede formar X para ML despues de joins/labels separados |
| `allowed_for_rl` | si puede alimentar capa RL, no necesariamente como dataset directo |
| `allowed_for_alphaevolve` | si puede alimentar evaluadores/candidatos AlphaEvolve |
| `required_validators` | leakage/calidad/lineage especificos del rol |
| `status` | complete_for_declared_scope, restricted, future, prohibited |

## 2. Roles Canonicos v0.1

| state_role | Objetivo | Timestamp types permitidos | Ventanas permitidas | Uso permitido | Prohibiciones clave | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `DISCOVERY_STATE` | explorar patrones y poblaciones sin decidir operacion | `pre_market_snapshot_t`, `regular_open_snapshot_t`, `bar_close_decision_t`, `event_anchor_t` si el evento ya era conocido | ventanas cerradas `<= t`; event windows solo como frontera | research, pattern discovery, ML candidate si y se separa despues | outcomes/labels/rewards inline; scanner selection como causal truth | `complete_for_declared_scope` |
| `EVENT_ANCHOR_STATE` | congelar estado en el ancla legal de un evento conocido | `event_anchor_t`, `bar_close_decision_t`, `halt_start_known_t`, `halt_resume_known_t`, `live_received_t` | pre-event y anchor windows con `window_end_utc <= t` | event_state candidate, pattern discovery, evaluator input | usar evento antes de conocerlo; response/outcome como feature | `complete_for_declared_scope` |
| `ENTRY_DECISION_STATE` | snapshot justo antes de decidir entrada | `entry_decision_t`, `bar_close_decision_t`, `pre_market_snapshot_t`, `regular_open_snapshot_t` | solo historia observada `<= t`; no post-entry | strategy research, supervised X candidate, AlphaEvolve evaluator input | fill, PnL, best threshold, outcome, accion tomada inline | `complete_for_declared_scope` |
| `RISK_STATE` | reevaluar hold/exit/sizing bajo datos conocidos | `risk_decision_t`, `bar_close_decision_t`, `halt_start_known_t`, `halt_resume_known_t` | historia observada `<= t`; puede incluir estado previo separado si la capa de decision lo declara | risk/evaluator candidate, future policy layer | position/action como market truth; reward/outcome inline | `restricted_requires_decision_layer_contract` |
| `EXECUTION_STATE` | contexto para simulacion o ejecucion, no fill truth | `entry_decision_t`, `risk_decision_t`, `exit_decision_t`, `live_received_t` | microestructura/constraints solo si gobernadas y `<= t` | execution simulator candidate futuro | fill garantizado, slippage real posterior, borrow/locate sin fuente | `restricted_requires_execution_contracts` |
| `RL_TRANSITION_STATE` | punto de una transicion para RL/offline learning | `bar_close_decision_t`, `entry_decision_t`, `risk_decision_t`, `exit_decision_t` | `state(t)` y `state(t+1)` separados; reward separado | future RL transition/evaluator layer | action/reward/outcome inline dentro de market/event state | `future_requires_transition_contract` |
| `POST_EVENT_ANALYSIS_STATE` | estudiar lo ocurrido despues del evento | `post_event_analysis_t`, `outcome_evaluation_t` | post-event, response, next-session windows permitidas como analisis | research, diagnostics, outcome/evaluator joins | usar como X pre-decision sin role/cutoff explicito | `complete_for_declared_scope_research_only` |


## 2.1 Consumption Legality

`state_role` and `consumption_legality` are independent.

```text
state_role
= why the snapshot exists and how it relates to the event/decision timeline.

consumption_legality
= whether the row may be used as predictive/input state.
```

Allowed values:

| consumption_legality | Meaning | Use boundary |
| --- | --- | --- |
| `decision_safe` | observable at the declared decision timestamp and legal under role/window/cutoff gates | may become X only if consumer gates also pass |
| `research_only` | valid for research/audit/diagnostics, not for predictive decision input | not X for pre-decision/event-time prediction |
| `outcome_adjacent` | post-event or response context useful for outcome/evaluator analysis | never X for pre-event/at-event decisions |
| `prohibited_as_input` | invalid as model/policy/strategy/execution input | blocked |

Default mapping for event-relative rows:

| event-relative state_role | default/legal consumption boundary |
| --- | --- |
| `pre_event` | may be `decision_safe` only when all fields satisfy cutoff and consumer gates |
| `at_event` | may be `decision_safe` only when the event and all fields are known at cutoff |
| `post_event` / `post_event_review` | `research_only` or `outcome_adjacent`; prohibited as event-time predictive X |

A row can be a valid Event State research row and still be illegal as prediction input.

## 3. Relacion Con Market State Y Event State

### `market_state_table`

`market_state_table` representa fotografia legal del mercado/instrumento en un
`decision_timestamp_utc`. Puede ser reusable por varios roles, pero si un builder
produce muestras orientadas a una decision debe declarar el rol en row o manifest.

Regla:

```text
market_state_table = observables legales as-of
state_role = contrato de uso de esa fotografia
```

### `event_state_table`

`event_state_table` debe llevar `state_role` de forma obligatoria, porque ancla el
estado a evento, ventana y uso.

Regla:

```text
event_state_table
= market_state bajo cutoff legal
+ event metadata conocida <= cutoff
+ event/window references
+ state_role
+ leakage gates
```

## 4. Matriz De Uso Permitido

| state_role | default consumption_legality | market_state | event_state | ML X candidate | RL candidate | AlphaEvolve evaluator input | Outcomes inline |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `DISCOVERY_STATE` | `research_only` or `decision_safe` if cutoff gates pass | si | si, si evento conocido | candidate only if `decision_safe` | no directo | candidate | no |
| `EVENT_ANCHOR_STATE` | `decision_safe` if event known at cutoff | si | si | candidate only if `decision_safe` | no directo | candidate | no |
| `ENTRY_DECISION_STATE` | `decision_safe` if cutoff gates pass | si | si | candidate only if `decision_safe` | future via transition layer | candidate | no |
| `RISK_STATE` | `decision_safe` or `research_only` depending on decision-layer gates | restricted | restricted | restricted | future via decision layer | candidate/restricted | no |
| `EXECUTION_STATE` | `decision_safe` only for execution context, never fill truth | restricted | restricted | no primary | future simulator only | restricted | no |
| `RL_TRANSITION_STATE` | `research_only` until transition contract | no directo | no directo | no primary | future only | candidate via transition evaluator | no |
| `POST_EVENT_ANALYSIS_STATE` | `research_only` or `outcome_adjacent` | research only | research only | no pre-decision X | no training X | evaluator diagnostics | outcome joins allowed separately |

## 5. Reglas De Ventana Por Rol

| state_role | Ventanas permitidas | Ventanas prohibidas como X pre-decision |
| --- | --- | --- |
| `DISCOVERY_STATE` | historical closed windows, pre-event windows si evento conocido | post-outcome windows sin role post-analysis |
| `EVENT_ANCHOR_STATE` | pre-event, anchor, same-t known context | response window posterior al anchor si decision es en anchor |
| `ENTRY_DECISION_STATE` | session-so-far, closed bars, pre-entry windows | post-entry, fill, PnL, MFE/MAE |
| `RISK_STATE` | history up to risk timestamp | future exit/outcome/reward |
| `EXECUTION_STATE` | quotes/trades/constraints known up to execution decision | realized fill/slippage posterior como feature |
| `RL_TRANSITION_STATE` | state(t), action reference, state(t+1) in separate transition schema | reward inside state row |
| `POST_EVENT_ANALYSIS_STATE` | response/post-event/next-session windows | reuse as pre-decision feature table |

## 6. Label, Outcome, Reward Y Action Boundaries

Ningun rol permite que `market_state_table` o `event_state_table` contengan:

```text
outcome values inline
label columns inline
reward columns inline
realized PnL inline
realized fill inline
strategy action inline como mercado observable
best threshold discovered inline
```

Permitido:

```text
outcome_join_key
label_join_key
transition_join_key
policy_candidate_id
```

Solo si el rol y el builder declaran que son llaves de join, no valores de
resultado.

## 7. Validators Requeridos Por Rol

| Validator | Roles obligatorios | Condicion |
| --- | --- | --- |
| `state_bad_missing_state_role` | `event_state_table`, role-oriented market samples | `state_role` nulo |
| `state_bad_missing_consumption_legality` | `event_state_table`, role-oriented market samples | `consumption_legality` nulo |
| `state_bad_unknown_consumption_legality` | todos | valor no incluido en la taxonomia permitida |
| `state_bad_unknown_state_role` | todos | rol no incluido en este contrato o version permitida |
| `state_bad_role_timestamp_mismatch` | todos | timestamp type incompatible con rol |
| `state_bad_role_window_mismatch` | todos | ventana no permitida por rol |
| `state_bad_post_event_used_as_pre_decision` | discovery, event_anchor, entry, risk, execution | uso de post-event/response/outcome como X pre-decision o `post_event_review` marcado `decision_safe` |
| `state_bad_outcome_inline` | todos | outcome/label/reward inline |
| `state_bad_action_inline_in_state` | todos | accion/politica escrita como mercado observable |
| `state_bad_execution_without_microstructure_contract` | execution | ejecucion sin microestructura/constraints gobernados |
| `state_bad_rl_without_transition_contract` | RL | RL transition sin contrato state/action/reward/next_state separado |
| `state_warn_restricted_role_used_for_ml` | risk/execution/post-analysis | uso ML requiere aprobacion/evaluator separado |

## 8. Relacion Con State Builder

El futuro state builder debe consumir este contrato y declarar:

```text
state_roles_contract_id = state_snapshot_roles_contract_v0_1
state_role
consumption_legality
role_family
allowed_timestamp_type
state_cutoff_rule
allowed_window_policy
outcome_join_policy
required_role_validators
```

El builder debe fallar o marcar la fila como blocked si:

```text
state_role no existe
state_role no permite el timestamp usado
state_role no permite la ventana usada
state_role intenta escribir outcome/label/reward inline
state_role intenta usar post-analysis como X pre-decision
consumption_legality contradice state_role, ventana o consumer gate
```

## 9. Relacion Con Semantic Representations Y Transitions

`semantic_state_representation_contract_v0_1.md` debe construirse despues de que
existan estados candidate y roles. Una representacion semantica debe declarar de
que rol sale su input.

`state_transition_contract_v0_1.md` debe construirse despues de que existan roles
y builder, porque una transicion necesita diferenciar:

```text
state(t) role
state(t+1) role
action(t) separado
reward(t) separado
outcome/evaluator separado
```

## 10. Relacion Con AlphaEvolve / ML / RL

AlphaEvolve puede proponer detectores, formulas, representaciones, transiciones o
politicas, pero debe respetar `state_role`.

Ejemplo:

```text
Puede evaluar una representacion sobre ENTRY_DECISION_STATE.
No puede entrenar con POST_EVENT_ANALYSIS_STATE como si fuera ENTRY_DECISION_STATE.
Puede proponer una transicion RL candidate.
No puede meter reward dentro del event_state base.
```

ML supervisado:

```text
X = state rows bajo role/cutoff legal
y = outcomes/labels separados
```

RL:

```text
state(t), action(t), state(t+1), reward(t)
```

son capa posterior, no `event_state_table` directo.

## 11. Provenance De Este Contrato

Este contrato es una sintesis nueva, basada en reglas ya existentes:

| Regla / idea | Tipo | Fuente local |
| --- | --- | --- |
| lista inicial de roles `DISCOVERY_STATE`, `EVENT_ANCHOR_STATE`, `ENTRY_DECISION_STATE`, `RISK_STATE`, `EXECUTION_STATE`, `RL_TRANSITION_STATE`, `POST_EVENT_ANALYSIS_STATE` | heredado | `state_observable_eligibility_contract_v0_1.md` y v3 |
| `event_state_table` requiere `state_role` | heredado | `market_state_event_state_composition_contract_v0_1.md` |
| roles no cambian verdad observable; cambian punto de corte y uso | heredado + formalizado | `state_observable_eligibility_contract_v0_1.md` |
| timestamp types no son roles completos | heredado | `state_decision_timestamp_policy_v0_1.md` |
| outcomes/labels/rewards inline prohibidos | heredado | `market_state_event_state_composition_contract_v0_1.md` |
| RL necesita transicion/action/reward separado | heredado | `market_state_event_state_composition_contract_v0_1.md` y `state_decision_timestamp_policy_v0_1.md` |
| matriz de uso por rol | formalizacion nueva | derivada de contratos anteriores |
| validators por rol | formalizacion nueva | derivada de leakage gates ya definidos |

Este documento no demuestra valor cientifico de ningun rol. Solo gobierna su uso
legal para que futuros builders, validators, evaluadores y agentes no mezclen
estado, outcome, accion, reward o post-analysis.

## 12. Acceptance Criteria v0.1

| Criterio | Estado |
| --- | --- |
| roles canonicos v0.1 definidos | `done` |
| rol separado de timestamp type | `done` |
| uso permitido por rol declarado | `done` |
| ventanas permitidas/prohibidas por rol declaradas | `done` |
| boundaries de outcome/label/reward/action declaradas | `done` |
| validators minimos por rol definidos | `done` |
| relacion con state builder definida | `done` |
| relacion con semantic representations/transitions definida | `done` |
| no materializa state builder ni tablas oficiales | `done` |

Status final:

```text
state_snapshot_roles_contract_v0_1 = complete_for_contract_defined_scope
```

## 13. Fuera De Alcance

No queda resuelto por este contrato:

```text
1. state builder contract
2. schemas candidate finales de market_state/event_state
3. fixtures controlados
4. validators ejecutables de leakage/calidad/lineage
5. candidate materialization
6. outcomes separados
7. evaluadores bloqueados
8. semantic representations
9. state transition datasets/evaluators
10. AlphaEvolve/RL/ML production use
```