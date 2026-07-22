# State Decision Timestamp Policy v0.1

## Estado

Tipo: state decision timestamp policy contract.
Modulo: `01_TSIS_DATA_FOUNDATION`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Fecha: 2026-07-04.

Status:

```text
contract_defined
decision_timestamp_policy_complete_for_declared_scope = true
state_snapshot_roles_contract_defined = true
state_builder_materialized = false
market_state_table_materialized = false
event_state_table_materialized = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

Este contrato cierra el significado operativo de `t` para las futuras tablas de
estado:

```text
state(t, instrument, event_context, data_availability_cutoff)
```

No materializa datos. No crea un builder. No promociona `market_state_table` ni
`event_state_table`. No define todavia todos los roles de snapshot. Fija que
reloj manda, que timestamps deben existir y que datos pueden ser conocidos para
una fila de estado.

## Nota De Versionado Y Variabilidad

Este contrato no debe leerse como una ley fija e inmutable del proyecto. Debe leerse como la version `v0.1` de la politica temporal que hoy permite construir estado sin leakage.

Durante el desarrollo de TSIS estas reglas pueden cambiar, ampliarse o dividirse si aparece una necesidad tecnica o cientifica real:

```text
nuevas fuentes con mejor timestamp/latencia
nuevos feeds live con received_utc gobernado
nuevas ventanas de decision o ejecucion
nuevos roles de snapshot
nuevas necesidades de RL/offline transitions
nuevas representaciones semanticas
nuevas propuestas de AlphaEvolve
nuevos evaluadores que demuestren que otra politica temporal es mejor
```

Pero ninguna variacion puede entrar de forma silenciosa. Toda variacion debe quedar como contrato nuevo o version nueva, con:

```text
motivo
fuente
regla de disponibilidad
cutoff
impacto sobre leakage
impacto sobre builders/validators
compatibilidad con estados ya materializados
criterio de promocion o rechazo
```

Regla practica:

```text
AlphaEvolve, ML, RL o estadisticas de estrategia pueden proponer cambios en formulas, ventanas, representaciones o transiciones, pero no pueden cambiar la verdad temporal base sin contrato/version y validacion explicita.
```

## Fuentes Normativas

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md
```

## Principio Central

```text
decision_timestamp_utc = instante desde el que TSIS pregunta:
que podia saber legalmente el sistema en ese momento?
```

Todo observable de estado debe demostrar:

```text
availability_time <= decision_timestamp_utc
```

No basta con que el dato tenga una fecha de evento anterior. Debe existir una
regla que demuestre cuando TSIS podia conocerlo.

Ejemplo:

```text
period_end_date de un filing no es disponibilidad.
published_utc de una noticia puede ser disponibilidad si la fuente lo gobierna.
received_utc manda sobre live alerts.
bar_end_utc manda sobre una vela cerrada.
build_created_at_utc nunca es disponibilidad de mercado; es solo lineage.
```

## 1. Vocabulario Temporal

| Campo | Que significa | Regla |
| --- | --- | --- |
| `decision_timestamp_utc` | instante legal del snapshot o decision | campo obligatorio en toda fila de estado |
| `state_cutoff_utc` | maximo timestamp de datos permitido para construir el estado | por defecto igual a `decision_timestamp_utc`; puede ser mas conservador |
| `component_as_of_utc` | disponibilidad efectiva seleccionada para un componente | siempre `<= state_cutoff_utc` |
| `source_observation_utc` | timestamp del evento observado por la fuente: bar, quote, trade, filing, news | no prueba disponibilidad por si solo |
| `source_availability_utc` | momento en que el dato pudo conocerse | debe existir para fuentes as-of/live/contexto |
| `received_utc` | momento de recepcion por feed/vendor/sistema | manda para live alerts, newswire, broker/vendor feeds y futuras alertas corporativas |
| `event_timestamp_utc` | momento del evento de mercado o evento externo | solo puede anclar estado si el evento era conocido `<= decision_timestamp_utc` |
| `bar_start_utc` | inicio de una vela | no permite usar OHLCV final |
| `bar_end_utc` | cierre de una vela | permite usar OHLCV de esa vela solo si `bar_end_utc <= decision_timestamp_utc` |
| `window_start_utc` | inicio de una ventana de observacion | define alcance, no disponibilidad |
| `window_end_utc` | fin de una ventana de observacion | para pre-decision debe ser `<= decision_timestamp_utc` |
| `created_at_utc` | momento de construccion del dataset | lineage; nunca alpha ni disponibilidad de mercado |
| `build_run_id` | identificador de materializacion | lineage; no desbloquea datos futuros |

Regla corta:

```text
observation time dice cuando paso algo.
availability time dice cuando TSIS podia saberlo.
decision timestamp dice desde donde se permite mirar.
```

## 2. Campos Obligatorios Para State Builder

Todo builder futuro de `market_state_table` o `event_state_table` debe producir o
conservar estos campos en fila, manifest o bundle de lineage:

| Campo | Nivel | Obligatorio | Motivo |
| --- | --- | --- | --- |
| `decision_timestamp_utc` | row | si | ancla legal del snapshot |
| `decision_date` | row | si | particion/calendario derivado desde timestamp UTC y session policy |
| `state_cutoff_utc` | row | si | maximo dato permitido para la fila |
| `state_cutoff_reason` | row | si | explica si el cutoff viene de decision, event anchor, bar close, live received time, etc. |
| `timestamp_policy_version` | row/manifest | si | versiona esta politica |
| `component_availability_bundle` | row/manifest | si | disponibilidad usada por componente |
| `component_as_of_bundle` | row/manifest | si | as-of efectivo por componente |
| `component_cutoff_violation_count` | row/manifest | si | contador de violaciones temporales |
| `max_component_as_of_utc` | row/manifest | si | prueba rapida de `<= state_cutoff_utc` |
| `build_created_at_utc` | manifest | si | lineage, no disponibilidad |
| `state_role` | row para event_state; recomendado para market_state samples | definido en `state_snapshot_roles_contract_v0_1.md` | une esta policy con roles canonicos de snapshot |

## 3. Tipos De Timestamp De Decision

Estos nombres no son roles por si solos. Son tipos de anclaje temporal. El contrato `state_snapshot_roles_contract_v0_1.md` ya define como se usan en discovery, entrada, riesgo, ejecucion, RL o post-analisis.

| Timestamp type | Definicion | Uso esperado | Cutoff base | Permitido para pre-decision |
| --- | --- | --- | --- | --- |
| `pre_market_snapshot_t` | instante elegido antes del open regular | contexto premarket, watchlist, discovery | `state_cutoff_utc = pre_market_snapshot_t` | si |
| `regular_open_snapshot_t` | instante en o despues de apertura regular observable | estado al inicio regular | `state_cutoff_utc = timestamp` | si |
| `bar_close_decision_t` | cierre de una vela gobernada | decisiones basadas en vela cerrada | `bar_end_utc <= t` | si |
| `event_anchor_t` | momento en que un evento queda conocido | anclar `event_state_table` | `event_known_utc <= t` | si, si el evento era conocido |
| `entry_decision_t` | instante antes de decidir entrada | decisiones de estrategia | `state_cutoff_utc = entry_decision_t` | si |
| `risk_decision_t` | instante de reevaluacion de riesgo | sizing, hold, exit candidate | `state_cutoff_utc = risk_decision_t` | si |
| `exit_decision_t` | instante antes de decidir salida | salida/hold | `state_cutoff_utc = exit_decision_t` | si |
| `halt_start_known_t` | instante en que el halt queda conocido | estado durante halt | `halt availability <= t` | si |
| `halt_resume_known_t` | instante en que resume queda conocido | estado post-resume | `resume availability <= t` | si |
| `live_received_t` | instante de recepcion de alerta live | newswire, broker/vendor, corporate alerts futuros | `received_utc <= t` | si |
| `post_event_analysis_t` | instante posterior usado para estudio | analisis de trayectoria | puede mirar despues del evento segun rol | no para features pre-decision |
| `outcome_evaluation_t` | instante/horizonte usado para medir outcome | label/reward separado | vive en outcomes/evaluadores | no es estado base |

Regla:

```text
Un timestamp posterior puede existir en research, pero si mira despues del punto
de decision debe marcarse como post_event_analysis/outcome/evaluator, nunca como
feature pre-decision.
```

## 4. Politica Por Componente

| Componente / familia | Timestamp que manda | Regla de disponibilidad | Caveat |
| --- | --- | --- | --- |
| Daily prior sessions | session close availability | sesiones cerradas y disponibles antes de `t` | prior sessions son seguros si la availability policy pasa |
| Daily current session open | first observable open/bar availability | permitido solo despues de observable | no usar high/low/close/volume final antes del cierre |
| Daily same-session final OHLCV | close/session final availability | solo despues de cierre y disponibilidad | prohibido en pre-close state |
| Daily lookbacks | ventanas de sesiones cerradas | cada sesion de lookback debe estar cerrada antes de `t` | `volume_20d_avg`/`rvol_20d` no pueden usar volumen final futuro |
| Intradia 1m | `bar_end_utc` / closed bar timestamp | solo barras cerradas `<= t` | vela incompleta prohibida salvo policy futura explicita |
| Intradia session-so-far | max closed bar timestamp incluido | acumulados solo con barras observadas `<= t` | no usar volumen/high/low final de sesion si aun no termino |
| Quote-guarded overlay | source event time + repair lineage | valores reparados pueden usarse como vista historica candidate si el manifest gobierna alcance | repair flags son quality/lineage, no alpha causal live |
| Microestructura quotes/trades | `window_end_utc` y source timestamps | ventanas pre-decision deben terminar `<= t` | ventanas que cruzan despues de `t` solo post-analysis/outcome/evaluator |
| News | `published_utc` o `received_utc` si live | noticia solo si conocida `<= t` | headline/catalyst no demuestra causalidad |
| Fundamentals | filing/accepted/as_of availability | `period_end` no es disponibilidad | si no hay accepted time, usar policy conservadora documentada |
| Short context | source `as_of` + lag model | disponibilidad debe incorporar lag/source scope | no implica borrow, locate ni SSR |
| Regime context | `as_of_utc` o barra/periodo observado | same-session aggregates solo si disponibles `<= t` | no usar cierre/regimen final intradia antes de disponibilidad |
| Halts | event timestamp + known/availability policy | halt/resume permitido si conocido `<= t` | si fuente historica no prueba latencia, marcar caveat |
| Short constraints | broker/vendor/regulatory availability | bloqueado hasta fuente as-of/live | no materializado hoy |
| Float context | point-in-time effective/as_of | bloqueado hasta tabla/fuente gobernada | no namespace confirmado hoy |
| Live corporate alerts | `received_utc` y latency semantics | bloqueado hasta feed live/backfill gobernado | `event_date` no basta |
| Outcomes | outcome horizon timestamp | separado de estado | nunca feature de `market_state`/`event_state` |
| Semantic representations | model/formula output timestamp | futura capa derivada desde estado legal | no verdad observable primaria |

## 5. Reglas De Corte Por Tipo De Ventana

| Window type | Regla |
| --- | --- |
| `point_in_time` | usar solo registros con disponibilidad `<= decision_timestamp_utc` |
| `closed_bar_window` | todos los `bar_end_utc` dentro de la ventana deben ser `<= decision_timestamp_utc` |
| `session_so_far` | acumulados calculados solo con datos observados hasta `t` |
| `pre_event_window` | `window_end_utc <= event_anchor_t <= decision_timestamp_utc` |
| `event_response_window` | si termina despues de `decision_timestamp_utc`, no puede ser feature pre-decision |
| `post_event_window` | permitido solo para post-analysis/outcome/evaluator |
| `next_session_window` | outcomes/labels, nunca estado pre-decision |
| `live_alert_window` | cada alerta necesita `received_utc <= t` |

## 6. Prohibiciones Explícitas

No se permite construir estado base con:

```text
daily close final antes del cierre
session high/low final antes de que la sesion termine
volumen final de sesion antes de que la sesion termine
vela 1m incompleta como si estuviera cerrada
quote/trade posterior a decision_timestamp_utc
noticia con published_utc o received_utc posterior a decision_timestamp_utc
filing usando period_end como disponibilidad
short interest sin lag/as_of gobernado
halt/resume si no era conocido por el timestamp declarado
outcome, reward, PnL, fill posterior o label inline
best threshold descubierto despues
semantic score sin formula/modelo/version/cutoff
build_created_at_utc como prueba de disponibilidad de mercado
```

## 7. Leakage Gates Que Deben Existir

Los validators futuros deben implementar como minimo:

| Gate | Condicion |
| --- | --- |
| `state_bad_missing_decision_timestamp` | `decision_timestamp_utc` nulo o invalido |
| `state_bad_non_utc_timestamp` | timestamp sin UTC o ambiguo |
| `state_bad_component_after_cutoff` | algun `component_as_of_utc > state_cutoff_utc` |
| `state_bad_observation_after_cutoff` | fuente observada despues de `state_cutoff_utc` en feature pre-decision |
| `state_bad_window_crosses_decision` | ventana de feature pre-decision termina despues de `decision_timestamp_utc` |
| `state_bad_same_session_final_leakage` | uso de close/high/low/volume final antes de disponibilidad |
| `state_bad_live_received_after_decision` | alerta/live feed recibido despues de `decision_timestamp_utc` |
| `state_bad_outcome_inline` | outcome/label/reward dentro de estado base |
| `state_bad_build_time_as_availability` | build timestamp usado como disponibilidad de mercado |
| `state_warn_conservative_availability_assumption` | fuente sin timestamp exacto, usando policy conservadora documentada |

## 8. Relacion Con Roles De Snapshot

Este contrato responde:

```text
cual es el reloj legal?
```

El siguiente contrato debe responder:

```text
para que se usa ese snapshot?
```

Por eso `state_snapshot_roles_contract_v0_1.md` debe tomar esta policy como
entrada y definir, por rol:

```text
state_role
allowed timestamp types
allowed windows
allowed joins to event/outcome
allowed use for research/ml/rl/alphaevolve
required leakage gates
```

Ejemplo:

```text
ENTRY_DECISION_STATE puede usar entry_decision_t y ventanas cerradas <= t.
POST_EVENT_ANALYSIS_STATE puede mirar ventanas posteriores, pero no puede ser X
pre-decision para ML/RL sin separacion explicita.
RL_TRANSITION_STATE necesitara state(t), action(t), state(t+1) y reward separados.
```

## 9. Relacion Con AlphaEvolve / ML / RL

AlphaEvolve, ML y RL pueden consumir estados solo si el timestamp contract permite
probar que cada feature era conocida en `t`.

No pueden usar:

```text
representaciones semanticas calculadas con datos posteriores
thresholds elegidos mirando outcomes y escritos retroactivamente como feature
transition labels como si fueran observables en t
reward/outcome dentro de event_state
```

AlphaEvolve puede proponer nuevas formulas, representaciones o transiciones,
pero cada candidato debe declarar:

```text
input timestamps
availability rule
cutoff rule
window rule
model/formula version
validator expectations
```

## 10. Manifest Requerido

Toda materializacion candidate futura debe declarar en manifest:

```text
timestamp_policy_id = state_decision_timestamp_policy_v0_1
timestamp_policy_version = 0.1
default_timezone = UTC
decision_timestamp_source
state_cutoff_rule
component_availability_bundle_schema
component_as_of_bundle_schema
leakage_guard_version
same_session_final_data_policy
live_received_time_policy
post_event_window_policy
known_conservative_availability_assumptions
```

## 11. Acceptance Criteria v0.1

| Criterio | Estado |
| --- | --- |
| `decision_timestamp_utc` definido como reloj legal principal | `done` |
| diferencia entre observation, availability, received, cutoff y build time definida | `done` |
| tipos de timestamp para premarket, bar close, event anchor, entry/risk/exit, halt/live y post-analysis definidos | `done` |
| reglas de disponibilidad por componente declaradas | `done` |
| ventanas pre/post decision separadas | `done` |
| prohibiciones de leakage temporal declaradas | `done` |
| gates minimos para validators definidos | `done` |
| relacion con snapshot roles definida sin cerrar roles todavia | `done` |
| no materializa state builder ni tablas oficiales | `done` |

Status final:

```text
state_decision_timestamp_policy_v0_1 = complete_for_contract_defined_scope
```

## 12. Fuera De Alcance

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
```
## 13. Provenance De Este Contrato

Este documento fue creado como contrato nuevo, pero no fue inventado desde cero.
La lectura correcta es:

```text
state_decision_timestamp_policy_v0_1.md
= sintesis contractual nueva
= basada en reglas ya existentes en TSIS
= con normalizaciones nuevas para hacerlas operativas
```

No venia ya escrito como documento unico. Lo que existia estaba repartido en
varios documentos del area Market State y Data Foundation.

### Bases Directas Usadas

| Regla / idea | Tipo | Fuente local |
| --- | --- | --- |
| `state(t, instrument, event_context, data_availability_cutoff)` | heredado | `market_state_tables_status_and_operating_map_2026_07_01_v3.md` |
| `component_as_of_utc <= decision_timestamp_utc` | heredado | `market_state_event_state_composition_contract_v0_1.md` |
| `decision_timestamp_utc`, `state_cutoff_utc`, `state_cutoff_reason`, `state_role` en skeletons | heredado | `market_state_event_state_composition_contract_v0_1.md` |
| ningun observable puede usar datos con `component_as_of_utc > decision_timestamp_utc` | heredado | `state_observable_eligibility_contract_v0_1.md` |
| barras 1m cerradas `<= decision_timestamp_utc` | heredado | `state_observable_eligibility_contract_v0_1.md` y `state_derived_observables_formula_contract_v0_1.md` |
| ventanas de microestructura pre-decision con `window_end_utc <= decision_timestamp_utc` | heredado | `state_observable_eligibility_contract_v0_1.md` y `state_derived_observables_formula_contract_v0_1.md` |
| news con `published_utc <= t` | heredado | `market_state_tables_status_and_operating_map_2026_07_01_v3.md`, `state_observable_eligibility_contract_v0_1.md`, `state_derived_observables_formula_contract_v0_1.md` |
| live alerts requieren `received_utc` y latencia gobernada | heredado + formalizado | `market_state_tables_status_and_operating_map_2026_07_01_v3.md` y `state_observable_eligibility_contract_v0_1.md` |
| outcomes nunca son feature source | heredado | `market_state_event_state_composition_contract_v0_1.md` |

### Normalizaciones Nuevas Introducidas Aqui

Lo que se formaliza por primera vez en este contrato es la taxonomia completa:

```text
observation time
availability time
received time
state_cutoff_utc
build time
```

Esa taxonomia no estaba cerrada como contrato independiente. Se deduce de las
reglas as-of ya escritas para impedir que el builder mezcle:

```text
cuando ocurrio algo
cuando TSIS pudo saberlo
cuando se recibio
hasta donde puede mirar el estado
cuando se construyo el dataset
```

Tambien se formalizan tipos de timestamp como:

```text
bar_close_decision_t
entry_decision_t
risk_decision_t
halt_start_known_t
live_received_t
post_event_analysis_t
```

Algunos ya estaban mencionados en el mapa v3 o en eligibility. Otros son
extensiones contractuales para cubrir los casos que ya aparecen en la
arquitectura: premarket, vela cerrada, evento conocido, decision de entrada,
risk/exit, halt/resume, live alerts, post-analysis y outcomes.

### Lectura Correcta

Este contrato no es evidencia empirica nueva ni una tabla real existente. Es un
contrato de gobierno temporal creado a partir de reglas dispersas en TSIS.

Su funcion es convertir esas reglas en una politica operativa que futuros
builders y validators puedan aplicar de forma reproducible.

Si una regla temporal cambia en el futuro, no debe editarse silenciosamente como
si siempre hubiera sido asi. Debe nacer una version nueva o una variante
candidate, por ejemplo:

```text
state_decision_timestamp_policy_v0_2.md
state_decision_timestamp_policy_live_alerts_candidate_v0_1.md
state_decision_timestamp_policy_rl_transitions_candidate_v0_1.md
```

Esa variante debe explicar por que cambia, que fuente la justifica, que leakage
nuevo introduce o elimina, y que evaluador o necesidad del proyecto la motiva.
## 14. Respuesta Copiada Para Trazabilidad

Pregunta original:

```text
Todo esto de donde lo has sacado? lo has creado tu o te has basado en algo?
```

Respuesta:

```text
Si: lo he creado yo como contrato nuevo, pero no lo he inventado desde cero.

Lo correcto es decirlo asi:

state_decision_timestamp_policy_v0_1.md
= sintesis contractual nueva
= basada en reglas ya existentes en TSIS
= con algunas normalizaciones mias para hacerlas operativas

No venia ya escrito como documento unico. Lo que existia estaba repartido.

Bases directas que use:

- Regla central de estado:
  market_state_tables_status_and_operating_map_2026_07_01_v3.md
  state(t, instrument, event_context, data_availability_cutoff)

- Regla obligatoria as-of:
  market_state_event_state_composition_contract_v0_1.md
  component_as_of_utc <= decision_timestamp_utc

- Skeletons que ya exigian decision_timestamp_utc, state_cutoff_utc, state_cutoff_reason, state_role:
  market_state_event_state_composition_contract_v0_1.md

- Reglas ya escritas en eligibility:
  state_observable_eligibility_contract_v0_1.md
  Ningun observable puede usar datos con component_as_of_utc > decision_timestamp_utc

- Reglas de 1m, ventanas, microestructura, news y received time:
  state_observable_eligibility_contract_v0_1.md

- Reglas de formulas ya cerradas:
  state_derived_observables_formula_contract_v0_1.md

Lo que si anadi yo como formalizacion nueva:

observation time
availability time
received time
state_cutoff_utc
build time

Eso no estaba como taxonomia cerrada en un contrato. Lo deduje de tus propias reglas as-of para que el builder no mezcle:

cuando ocurrio algo
cuando TSIS pudo saberlo
cuando se recibio
hasta donde puede mirar el estado
cuando se construyo el dataset

Tambien formalice tipos como:

bar_close_decision_t
entry_decision_t
risk_decision_t
halt_start_known_t
live_received_t
post_event_analysis_t

Algunos ya estaban mencionados en el v3/eligibility; otros son extensiones contractuales mias para cubrir los casos que ya aparecen en la arquitectura.

Asi que tu duda es legitima: no es evidencia empirica nueva ni una tabla real existente. Es un contrato de gobierno temporal creado por mi, basado en reglas ya dispersas en TSIS.
```
