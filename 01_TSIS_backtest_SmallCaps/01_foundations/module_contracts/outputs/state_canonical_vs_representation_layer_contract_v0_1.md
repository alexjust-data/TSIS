# State Canonical Vs Representation Layer Contract v0.1

## Estado

Tipo: canonical state vs representation layer contract.
Modulo: `01_TSIS_backtest_SmallCaps`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Fecha: 2026-07-04.

Status:

```text
contract_defined
canonical_vs_representation_gate_complete_for_declared_scope = true
canonical_state_schema_changed = false
representation_candidates_materialized = false
semantic_state_representation_contract_materialized = false
state_transition_contract_materialized = false
market_state_table_materialized = false
event_state_table_materialized = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

Este contrato no materializa datos. No crea nuevas columnas oficiales. No cambia
el schema de `market_state_table` ni `event_state_table`. Su funcion es fijar una
frontera conceptual y operativa:

```text
Canonical State = fotografia legal, estable y gobernada del mundo observable en t
Representation Layer = transformaciones candidatas, mutables y evaluables sobre esa fotografia
```

La razon de este contrato es evitar que el estado base se contamine con scores,
interpretaciones, embeddings, thresholds optimizados, labels, outcomes o
features experimentales.

## Fuentes Normativas

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
```

## Problema Que Resuelve

La regla general de TSIS ya dice:

```text
tablas de estado = fotografia legal del mundo observable en t
```

Pero esa frase necesita una segunda frontera. No todo lo que se calcula desde
observables debe entrar en el estado canonico.

Ejemplo:

```text
spread_bps
published_utc
short_interest
halt_state
prior_close
```

son piezas que describen fenomenos observables, economicos, informacionales,
temporales o de calidad.

En cambio:

```text
attention_score
crowding_score
liquidity_stress_v7
setup_quality
breakout_score_v3
best_threshold_found
```

pueden ser representaciones utiles, pero no son verdad base del mercado. Deben
vivir en una capa superior, versionada y evaluable.

## Principio Central

```text
Una columna de Canonical State debe poder justificarse porque representa un
aspecto fisico, economico, informacional, temporal, de calidad o lineage del
mercado, no porque alguna vez fue util para una estrategia.
```

Consecuencia:

```text
Canonical State cambia poco.
Representation Layer puede evolucionar continuamente.
```

## Mapa Mental Correcto

```text
RAW DATA
  -> OBSERVABLES
  -> CANONICAL STATE
  -> REPRESENTATION BUILDERS
  -> REPRESENTATION CANDIDATES
  -> EVENT DETECTORS
  -> POLICIES
  -> EVALUATORS
  -> ALPHAEVOLVE / RL / ML
```

Lectura por capa:

| Capa | Objetivo | Que no debe hacer |
| --- | --- | --- |
| `RAW DATA` | conservar hechos fuente o datos auditados | no elegir estrategia |
| `OBSERVABLES` | declarar que valores pueden conocerse legalmente en `t` | no probar edge |
| `CANONICAL STATE` | ensamblar la fotografia estable y gobernada del mercado | no meter scores experimentales |
| `REPRESENTATION BUILDERS` | transformar estado canonico en representaciones candidatas | no cambiar la verdad observable |
| `REPRESENTATION CANDIDATES` | probar formas alternativas de entender el mercado | no sustituir el estado sin promocion formal |
| `EVENT DETECTORS` | detectar/anclar eventos con definicion versionada | no convertir outcomes en features |
| `POLICIES` | decidir acciones o no-acciones bajo un evaluador | no escribir decisiones dentro del estado base |
| `EVALUATORS` | medir fitness, robustez, costes y leakage | no redefinir datos historicos |
| `ALPHAEVOLVE / RL / ML` | generar, mutar o aprender objetos candidatos | no mutar silenciosamente el estado canonico |

## Definiciones Operativas

### Raw Data

Dato fuente o reconstruccion auditada de una fuente.

Ejemplos:

```text
OHLCV raw
quotes
trades
news
filings
short interest
corporate actions
halts
calendar
```

Raw data no es automaticamente estado. Debe pasar por elegibilidad, cutoff,
calidad, lineage y policy de consumo.

### Observable Elegible

Valor literal o derivado que puede conocerse legalmente en `t` y que no contiene
outcome, reward, label, accion, fill, PnL ni futuro.

Este nivel lo gobierna:

```text
state_observable_eligibility_contract_v0_1.md
```

### Formula Derivada

Transformacion reproducible de inputs observables legales.

Este nivel lo gobierna:

```text
state_derived_observables_formula_contract_v0_1.md
```

Regla importante:

```text
derived no significa automaticamente experimental.
literal no significa automaticamente canonico.
```

Una derivada mecanica estable puede vivir en Canonical State si tiene formula,
cutoff, calidad y lineage. Una columna literal puede quedar fuera si no es legal,
no tiene disponibilidad real, no tiene calidad o representa una decision.

### Canonical State

Snapshot estable y gobernado de observables as-of.

Debe servir como tablero base para investigacion, eventos, evaluadores,
representaciones, ML, RL y AlphaEvolve.

No debe estar optimizado para una estrategia concreta.

### Representation Builder

Codigo, formula, modelo o pipeline que transforma Canonical State en una
representacion candidata.

Ejemplos:

```text
builder de liquidity_stress
builder de attention_score
builder de crowding_proxy
builder de rvol_window_family_candidate
builder de move_shape_embedding
builder de semantic market regime
```

Un representation builder puede ser propuesto por humanos, estadistica de
estrategias, ML, RL o AlphaEvolve.

### Representation Candidate

Resultado de un representation builder.

Puede ser una columna, vector, embedding, score, estado semantico, taxonomia,
grafo u objeto estructurado.

Ejemplos:

```text
attention_score_v0_1
liquidity_stress_candidate_v0_3
crowding_proxy_v0_2
momentum_regime_embedding_v0_1
book_fragility_state_candidate_v0_1
rvol_17d_candidate_v0_1
move_speed_8m_candidate_v0_1
```

No es Canonical State por defecto.

### Semantic State Representation

Representacion candidata que intenta resumir significado de mercado.

Ejemplos:

```text
Attention
Liquidity Stress
Book Fragility
Crowding
Momentum Regime
Volatility Compression
Price Discovery
Inventory Pressure
```

Estas entidades no son observables primarios. Salen de formulas, reglas,
modelos, embeddings o combinaciones. Deben vivir en un contrato posterior:

```text
semantic_state_representation_contract_v0_1.md
```

### Transition Candidate

Objeto que representa paso de un estado o representacion a otro.

Ejemplo:

```text
state(t) -> state(t+1)
representation_A(t) -> representation_A(t+1)
Idle -> Attention -> Liquidity Vacuum -> Squeeze -> Exhaustion
```

Debe vivir en un contrato posterior:

```text
state_transition_contract_v0_1.md
```

## Canonical State No Es Raw-Only

TSIS no dice:

```text
Canonical State = solo datos crudos
```

Dice:

```text
Canonical State = observables legales as-of, literales o derivados, estables y gobernados
```

Por tanto, puede incluir:

```text
columnas literales
columnas mecanicamente derivadas
baselines declarados
calidad
coverage
lineage
```

Siempre que respeten:

```text
formula contratada
cutoff legal
missingness policy
quality gate
lineage
version
```

## Tipos De Derivadas

| Tipo | Puede vivir en Canonical State | Condicion |
| --- | --- | --- |
| Derivada mecanica directa | si | formula simple, estable y gobernada |
| Baseline canonico declarado | si, con cautela | existe por contrato/schema, no porque sea optimo |
| Familia parametrica candidata | no por defecto | vive en Representation Layer |
| Score aprendido o semantico | no por defecto | vive en Representation Layer |
| Threshold ganador descubierto | no | vive en detector/evaluador, nunca como verdad base |
| Outcome, reward, label, fill, PnL | no | vive fuera del estado |

Ejemplo:

```text
daily__dollar_volume
```

puede ser Canonical State si se define como:

```text
close * volume
```

con price view, cutoff y calidad declarados.

Ejemplo:

```text
daily__rvol_20d
```

puede ser baseline canonico si ya esta declarado por el schema y la formula
contract. Eso no significa que 20 sesiones sea cientificamente optimo.

Ejemplo:

```text
daily__rvol_14d_candidate_v0_1
daily__rvol_60d_candidate_v0_1
intraday__move_speed_7m_candidate_v0_1
microstructure__liquidity_texture_v0_1
```

son candidatos de representacion salvo que una version futura los promueva con
justificacion fisica/economica/informacional, formula, cutoff, evidencia y
contrato.

## Regla Para `rvol_20d` Y Ventanas Parecidas

Si `rvol_20d` aparece en el estado canonico, la lectura correcta es:

```text
baseline reproducible declarado por contrato
```

No significa:

```text
mejor ventana
edge probado
criterio cientifico cerrado
feature que AlphaEvolve debe aceptar como optima
```

AlphaEvolve, ML, RL o una estadistica de estrategia pueden proponer:

```text
rvol_7d
rvol_13d
rvol_29d
rvol_to_time_intraday
volume_pace_17m
```

pero esas variantes deben entrar como:

```text
representation_candidate
```

No reemplazan silenciosamente al Canonical State.

## Que Entra En Canonical State

Puede entrar si pasa eligibility, formula/cutoff y quality gates:

```text
identity__*
calendar__*
daily__* estable y gobernado
intraday__* estable y gobernado
microstructure__* estable y gobernado
fundamentals__* as-of
news__* as-of
short_context__* con lag
short_constraints__* si existe fuente legal
halt__* as-of
regime__* si respeta disponibilidad
quality__*
coverage__*
lineage/source manifest cuando el schema lo declare
```

La presencia de `*` no significa carta blanca. Cada columna concreta debe estar
en eligibility/formula/schema/builder contract.

## Que No Entra En Canonical State

No entra como estado canonico:

```text
winner/loser
outcome futuro
reward
label
accion tomada
fill real posterior
PnL posterior
best threshold discovered
selected_by_scanner como senal causal
setup_quality
breakout_score
attention_score
crowding_score
liquidity_stress_score
embedding aprendido
semantic state aprendido
policy action
strategy decision
```

Algunas de estas piezas pueden existir en capas posteriores:

```text
scanner/event detector
event table
representation candidate
semantic state representation
policy candidate
outcome table
evaluation table
```

pero no como verdad base de `market_state_table` o `event_state_table`.

## Aplicacion Por Area

### Daily

Canonical State puede contener observables diarios estables:

```text
prior_close
gap_pct
daily_return_pct
daily_range_pct
dollar_volume
volume_20d_avg
rvol_20d
quality flags
source lineage
```

Lectura correcta:

```text
son observables o baselines declarados, no prueba de que esa ventana sea optima.
```

Alternativas como `rvol_14d`, `rvol_60d`, ranking compuesto o score de setup
viven en Representation Layer salvo promocion formal.

### Intradia 1m

Canonical State puede contener observables 1m estables:

```text
last closed bar OHLCV
session high/low so far
volume so far
bars observed
coverage/missingness
quote-guarded repair state
quality flags
source manifest
```

Derivadas como velocidad, aceleracion, curvature, shape, pace o familias de
ventanas multiples deben tratarse como representation candidates si dependen de
parametros experimentales.

### Microestructura Y Segundos

Canonical State puede contener observables de quotes/trades bajo ventanas
gobernadas:

```text
spread bps
midpoint
locked/crossed state
quote count
trade count
staleness
zero bid/ask ratios
trade volume
size distribution declarada
quality flags
source lineage
```

Representaciones como `book_fragility`, `liquidity_texture`, `inventory_pressure`
o `crowding` no son canonicas por defecto. Deben tener builder, formula/modelo,
cutoff, version y evaluador.

### Contexto As-Of

Canonical State puede contener contexto conocido legalmente en `t`:

```text
fundamentals as-of
news published/as_of timestamps
short interest/short volume con lag
halt/resume state
regime context con disponibilidad declarada
short constraints si existe fuente legal
```

No puede convertir `news`, `short interest` o `regime` en causalidad demostrada.
Eso pertenece a evaluadores, causalidad, representaciones o modelos.

### Eventos

Eventos no son Canonical State.

```text
event candidate table = ancla/deteccion versionada
event_state_table = Canonical State anclado a evento/ventana/rol
```

Un threshold como `first_cross_50` puede vivir en una definicion de evento, pero
no debe aparecer como verdad privilegiada del estado canonico.

### Outcomes Y Evaluadores

Outcomes y evaluadores quedan separados.

```text
X = Canonical State / Event State / Representation Candidate bajo cutoff legal
y = outcomes separados
fitness = evaluadores bloqueados
```

## Regla Para AlphaEvolve

AlphaEvolve puede mutar:

```text
observables derivados candidatos
representation builders
semantic state representations
event detectors
transition functions
policy candidates
evaluation composition
```

AlphaEvolve no puede mutar silenciosamente:

```text
la verdad observable canonica
cutoff/as-of legality
source lineage
quality gates
outcome boundaries
schema oficial promovido
```

Si AlphaEvolve propone una nueva representacion util, debe quedar como:

```text
representation_candidate_id
builder_version
input_canonical_state_version
formula_or_model_version
training_cutoff si aplica
inference_cutoff
lineage
quality gates
evaluator result
promotion status
```

No reemplaza el Canonical State salvo decision formal posterior.

## Promocion Desde Representation Layer Hacia Canonical State

Una representacion candidata puede proponer una nueva columna canonica futura,
pero solo si cumple todas estas condiciones:

| Requisito | Pregunta |
| --- | --- |
| Fenomeno real | representa algo fisico, economico, informacional, temporal, calidad o lineage? |
| Formula estable | tiene formula/modelo fijo y versionado? |
| Cutoff legal | respeta decision timestamp y disponibilidad real? |
| Reproducible | puede reconstruirse desde inputs y manifest? |
| Neutralidad | no codifica label, outcome, reward, accion ni threshold ganador? |
| No parametro oportunista | no existe solo porque optimizo una estrategia puntual? |
| Evidencia | tiene tests, validators y resultados fuera de muestra si aplica? |
| Contrato | aparece en eligibility/formula/schema/builder contract de una version futura? |

Si falla una condicion, permanece como Representation Candidate.

## Interfaces Con Contratos Existentes

| Contrato | Relacion con este contrato |
| --- | --- |
| `state_observable_eligibility_contract_v0_1.md` | dice si una columna puede existir como observable legal |
| `state_derived_observables_formula_contract_v0_1.md` | dice como se calcula una derivada y si cambia de identidad |
| `state_decision_timestamp_policy_v0_1.md` | fija el reloj legal y disponibilidad |
| `state_snapshot_roles_contract_v0_1.md` | fija para que rol se toma el snapshot |
| `state_builder_contract_v0_1.md` | ensambla Canonical State, no representaciones experimentales |
| `event_candidate_tables_contract_v0_1.md` | gobierna detecciones/anclas de evento fuera del estado canonico |
| `event_candidate_table_validators_contract_v0_1.md` | impide que eventos candidatos mezclen outcomes o futuro |
| `semantic_state_representation_contract_v0_1.md` | contrato futuro para representaciones semanticas/latentes |
| `state_transition_contract_v0_1.md` | contrato futuro para transiciones entre estados/representaciones |

## Validators Que Deben Existir Despues

Este contrato requiere validators futuros para detectar:

```text
canonical_column_uses_outcome
canonical_column_uses_strategy_label
canonical_column_uses_action_or_fill
canonical_column_uses_best_threshold
canonical_column_is_learned_score_without_representation_contract
canonical_column_is_parameter_grid_without_promotion
representation_candidate_missing_builder_version
representation_candidate_missing_input_state_version
representation_candidate_missing_cutoff
representation_candidate_missing_evaluator_result
```

No se implementan aqui. Se declaran como requisito para los proximos validators
de estado/representacion.

## Decision Practica Para La Ruta Actual

Este contrato no cambia el siguiente trabajo ejecutable inmediato:

```text
validators ejecutables de event candidate tables
builders/materializacion candidate de daily_strategy_candidate_events_table_v0_1
builders/materializacion candidate de intraday_1m_strategy_candidate_events_table_v0_1
event_windows expansion
controlled market_state/event_state fixture
```

Lo que si cambia es la frontera futura:

```text
controlled market_state/event_state fixture
  -> Canonical State claramente separado de Representation Layer
  -> semantic_state_representation_contract_v0_1.md
  -> semantic representation candidates
  -> state_transition_contract_v0_1.md
  -> transition datasets / transition evaluators
  -> AlphaEvolve/RL/ML
```

## Criterios De Aceptacion

Este contrato queda completo para el scope declarado si:

```text
1. define Canonical State vs Representation Layer sin cambiar schemas oficiales;
2. aclara que estado canonico no es raw-only;
3. aclara que derived no significa automaticamente experimental;
4. aclara que una derivada estable puede ser canonica si tiene formula/cutoff;
5. aclara que parameter grids, scores, embeddings y semantic states son candidates;
6. aclara que AlphaEvolve muta representaciones, detectores, transiciones,
   politicas y evaluadores, no la verdad observable canonica;
7. fija la promocion formal requerida antes de mover algo de representation
   candidate a Canonical State;
8. deja cerrada la frontera para el futuro `semantic_state_representation_contract_v0_1.md`.
```

## Lectura Final

La pregunta correcta no es:

```text
cuantas variables necesita una estrategia?
```

La pregunta correcta para TSIS es:

```text
que tablero canonico necesita el laboratorio para poder descubrir mecanismos
sin contaminar la verdad observable con hipotesis experimentales?
```

Respuesta:

```text
Canonical State = tablero estable.
Representation Layer = espacio de busqueda.
AlphaEvolve = mutador/evaluador de objetos candidatos sobre ese tablero.
```
