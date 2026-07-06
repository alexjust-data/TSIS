# Event Research Design Contract v0.1

## Estado

Tipo: event research design contract.  
Modulo: `01_TSIS_backtest_SmallCaps`.  
Ambito: `CAPA 1 - DATA FOUNDATION` / `MARKET SCIENCE`.  
Fecha: 2026-07-05.  

Status:

```text
contract_defined
research_design_layer_defined = true
sampling_probe_registry_materialized = false
sampling_window_registry_materialized = false
parameter_sweep_materialized = false
event_family_discovery_materialized = false
validated_event_definitions_materialized = false
locked_evaluator_enabled = false
alphaevolve_research_mutation_enabled = configurable_not_default
```

## 0. Filosofia Del Laboratorio

La unidad basica del laboratorio TSIS no debe ser el evento.

La unidad basica del laboratorio debe ser el experimento.

Un `sampling_probe` es un experimento:

```text
muestrame todos los movimientos que superan un determinado umbral
```

Un `parameter_sweep` es un experimento:

```text
que ocurre si el umbral es 20%, 30%, 40%, 50%, 70% o 100%
```

Solo cuando estos experimentos producen evidencia robusta puede nacer una  
familia de eventos. Mas adelante, y solo despues de validacion, puede nacer una  
`validated_event_definition`.

Esta separacion evita convertir decisiones humanas provisionales en supuestos  
fundamentales de la arquitectura. Ejemplos:

```text
+50% de movimiento intradia
ventana pre_event_30m
ventana post_event_30m
```

Estas reglas pueden ser utiles para mirar el mercado, construir fixtures,  
localizar casos extremos o generar imagenes de estudio. Pero no son, por si  
mismas, verdad cientifica, edge, evento validado ni estrategia.  

Lectura correcta:

```text
+50% = sampling probe humano
30m = sampling window controlada
```

Un `sampling_probe` debe entenderse como un instrumento cientifico. Es parecido  
a un microscopio: no crea el fenomeno y no lo define de forma definitiva. Solo    
permite observar una parte del mercado bajo una configuracion concreta.  

El objetivo del laboratorio no es descubrir estrategias primero.  

El objetivo del laboratorio es descubrir fenomenos repetibles del mercado.  

La cadena cientifica deseada es:  

```text
sampling probes
-> fenomenos observados
-> event family candidates
-> validated event definitions
-> strategy candidates
-> operational strategies
```

AlphaEvolve, ML o RL no deben recibir un probe humano como verdad fija. Pueden  
participar despues proponiendo variaciones, representaciones o detectores, pero  
solo dentro de un experimento versionado y con limites explicitos.  

Por eso este contrato no dice:

```text
mutable_by_alphaevolve = true
```

La regla correcta es mas precisa:

```text
research_mutable = true
human_research_mutable = true
optimizer_mutable = configurable
production_locked = false
```

`optimizer_mutable = configurable` significa que cada experimento decide si un  
optimizador, AlphaEvolve u otro sistema puede modificar probes, ventanas,  
parametros, representaciones o detectores. El laboratorio no queda abierto por  
defecto a modificaciones automaticas.  

## 1. Por Que Existe Este Contrato

TSIS ya puede construir, para un caso controlado:

```text
1m quote-guarded
-> market_state
-> event_candidate
-> event_windows
-> event_state
-> outcomes separados
```

Pero eso no significa que TSIS ya conozca el evento correcto.

El `+50%` usado en el caso intradia controlado nacio como una herramienta humana  
para localizar historicamente movimientos grandes y poder estudiar casos. No  
nacio como definicion cientifica del fenomeno.  

Este contrato existe para separar:

```text
instrumentos de muestreo
hipotesis parametrizables
familias de eventos candidatas
definiciones validadas de evento
estrategias operativas
```

Sin esta capa, futuros agentes podrian:

- tratar `threshold_pct = 50.0` como verdad oficial;
- tratar `pre_event_30m` o `post_event_30m` como ventanas demostradas;
- congelar evaluadores antes de saber que evento estan evaluando;
- mezclar filtros de universo con eventos;
- convertir un scanner discrecional humano en senal causal;
- o permitir que AlphaEvolve modifique el laboratorio sin limites claros.

## 2. Fuentes Normativas

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_observable_eligibility_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_canonical_vs_representation_layer_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_contract_v0_1.md
```

## 3. Taxonomia De Investigacion

| Nivel | Que es | Ejemplo | Lectura correcta |
| --- | --- | --- | --- |
| Universo / eligibility | Scope donde se permite buscar | `market_cap < 100M`, `price < 20`, liquidez minima | define donde mirar; no es evento ni edge |
| Scanner / candidate filter | Filtro operativo o discrecional que sugiere atencion | scanner diario usado por trader | generador de candidatos; no es causalidad |
| Sampling probe | Instrumento para observar casos | `move_pct >= 50` | experimento de muestreo; no evento validado |
| Sampling window | Ventana para mirar antes/despues | `pre_event_30m`, `post_event_30m` | ventana inicial de investigacion; no ventana final |
| Parameter sweep | Variacion sistematica de parametros | `20/30/40/50/70/100%` | busca sensibilidad y estructura |
| Fenomeno observado | Patron empirico repetible bajo medicion | push, fallo, continuacion, desintegracion | aun no es definicion validada |
| Event family candidate | Agrupacion de fenomenos parecidos | `intraday_momentum_extension` | candidata a familia de eventos |
| Validated event definition | Evento congelado por evidencia | definicion versionada con criterios pasados | apta para evaluadores bloqueados |
| Strategy candidate | Regla de decision sobre eventos/estado | long pullback, short backside | no vive en estado base |
| Operational strategy | Estrategia promovida | detector + policy + riesgo + ejecucion | produccion/backtest operativo |

## 4. Regla Central

No se debe pasar directamente de un probe humano a una definicion de evento.

Flujo correcto:

```text
sampling_probe
-> parameter_sweep
-> exploratory_statistics
-> event_family_candidate
-> validation_protocol
-> validated_event_definition
-> locked_evaluator
```

Un probe puede ser muy util aunque no sea un buen evento final.

Ejemplo:

```text
threshold_pct = 50.0
```

Puede servir para encontrar casos extremos de momentum intradia, generar pngs,  
crear fixtures, estudiar desintegraciones y medir outcomes. Pero no demuestra  
que `50%` sea el umbral optimo, ni que ese sea el verdadero inicio del fenomeno.  

## 5. Probes Humanos Actualmente Reconocidos

### 5.1 Probe Intradia De Movimiento Fuerte

```text
probe_id = intraday_1m_large_move_pct_human_seed_v0_1
probe_status = sampling_probe_human_seed
threshold_pct = 50.0
reference_price = controlled_builder_defined
research_mutable = true
human_research_mutable = true
optimizer_mutable = configurable
production_locked = false
promoted_event_definition = false
```

Lectura:

```text
sirve para encontrar movimientos grandes
no define el evento oficial
no define edge
no define estrategia
```

### 5.2 Ventanas Controladas Iniciales

```text
window_probe_id = pre_event_30m_controlled_seed_v0_1
window_status = sampling_window_controlled_seed
window_role = pre_event_context
research_mutable = true
optimizer_mutable = configurable
production_locked = false
```

```text
window_probe_id = post_event_30m_controlled_seed_v0_1
window_status = sampling_window_controlled_seed
window_role = outcome_observation
research_mutable = true
optimizer_mutable = configurable
production_locked = false
```

Lectura:

```text
30m es una ventana razonable para empezar
no esta demostrado que sea la ventana correcta
```

## 6. Familias Iniciales De Investigacion

Estas familias no son estrategias ni eventos validados. Son areas donde TSIS
puede disenar experimentos.

| Familia | Que intenta observar | Parametros investigables |
| --- | --- | --- |
| `intraday_momentum_extension` | extension fuerte intradia desde una referencia observable | threshold_pct, reference_price, session_scope, liquidity gate |
| `gap_and_premarket_attention` | gap, atencion premarket y extension antes de la regular | gap_pct, premarket volume, time bucket, catalyst context |
| `vwap_reclaim_or_loss` | recuperacion/perdida de VWAP bajo contexto | cross direction, confirmation window, volume/rvol context |
| `hod_break_or_failure` | ruptura o fallo de high of day | breakout size, hold duration, rejection window |
| `first_pullback_after_push` | retroceso inicial tras extension | pullback depth, time since push, volume decay |
| `backside_or_momentum_failure` | perdida de estructura tras squeeze/push | lower high/lower low rules, VWAP loss, liquidity decay |
| `liquidity_or_volume_shock` | cambio brusco de actividad/liquidez | volume/rvol grids, spread expansion, tape intensity |
| `daily_context_event` | contexto diario tipo former runner, breakout, continuation | lookback, gap, daily range, prior runner evidence |

## 7. Parameter Sweeps

Un `parameter_sweep` no busca demostrar un edge por si solo. Busca medir la
sensibilidad de una familia de fenomenos.

Ejemplo para `intraday_momentum_extension`:

```text
threshold_pct: 20, 30, 40, 50, 70, 100
reference_price: prior_close, session_open, segment_open, premarket_low, vwap
session_scope: premarket, regular, afterhours, full_intraday
pre_event_window: 5m, 15m, 30m, 60m, session_so_far
post_event_window: 1m, 5m, 15m, 30m, 60m, end_of_session
liquidity_gate: none, min_volume, min_dollar_volume, spread_quality
```

Cada sweep debe registrar:

```text
experiment_id
probe_id
event_family_candidate
parameter_grid
source_state_version
source_outcome_version
coverage_rules
leakage_rules
quality_rules
sample_size_rules
created_by
created_at
```

## 8. Outcome Matrix Exploratoria

Antes de bloquear evaluadores, TSIS puede medir outcomes exploratorios.

Ejemplos:

```text
MFE
MAE
return_final
continuation_rate
failure_rate
halt_rate
liquidity_decay
spread_expansion
coverage_ratio
missing_bar_ratio
```

Regla:

```text
outcomes = y separado
state/event_state = X legal as-of
```

Ningun outcome exploratorio puede volver hacia el estado base.

## 9. Criterios De Evidencia Antes De Promocion

La promocion no debe depender de que una definicion parezca interesante.

Debe depender de criterios de evidencia.

Criterios minimos:

```text
sample_size_sufficient
coverage_sufficient
leakage_free
quality_gates_passed
stable_across_time
stable_across_tickers_or_subgroups
robust_to_reasonable_parameter_changes
out_of_sample_or_walk_forward_checked
cost_or_slippage_assumption_declared
complexity_penalty_declared
lineage_reproducible
```

Hasta que estos criterios no esten definidos y superados, el resultado sigue en
fase exploratoria.

## 10. Limites Para AlphaEvolve Y Optimizadores

AlphaEvolve no puede modificar el laboratorio por defecto.

Puede participar solo cuando un experimento declare explicitamente:

```text
optimizer_mutable = true
optimizer_type = alphaevolve | other
mutation_scope = declared
fitness_function = declared
leakage_gates = enforced
complexity_penalty = enforced
output_registry = declared
```

Mutation scopes permitidos, si se declaran:

```text
sampling_probe_parameters
sampling_window_parameters
reference_price_functions
confirmation_rules
representation_builders
event_family_detectors
policy_candidates
```

Mutation scopes prohibidos salvo contrato nuevo:

```text
raw_data_rewrite
base_state_truth_rewrite
outcome_rewrite
lineage_rewrite
quality_gate_disable
leakage_gate_disable
production_locked_definition_mutation
```

## 11. Relacion Con Evaluadores Bloqueados

Un evaluador bloqueado solo tiene sentido cuando ya se sabe que se esta
evaluando.

Por tanto, la ruta correcta es:

```text
controlled outcomes separados
-> event research design
-> sampling probes / windows / parameter sweeps
-> exploratory event statistics
-> event family candidates
-> validated event definitions
-> evaluator_contract_v0_1
-> locked evaluators
```

No se debe bloquear un evaluador global sobre un probe humano no validado.

Puede existir un evaluador exploratorio, pero debe declararse como tal:

```text
evaluator_status = exploratory
production_locked = false
promotion_use = evidence_generation_only
```

## 12. Ruta Actual Corregida

```text
v3 mapa humano DONE
-> state_observable_eligibility_contract_v0_1.md DONE
-> state_derived_observables_formula_contract_v0_1.md DONE
-> state_decision_timestamp_policy_v0_1.md DONE
-> state_snapshot_roles_contract_v0_1.md DONE
-> state_builder_contract_v0_1.md DONE
-> event_candidate_tables_contract_v0_1.md DONE
-> controlled market_state/event_state/outcomes intradia DONE
-> controlled multi-component fixture PENDING
-> event_research_design_contract_v0_1.md DONE
-> sampling_probe_registry_v0_1 PENDING
-> sampling_window_registry_v0_1 PENDING
-> parameter_sweep_plan_v0_1 PENDING
-> exploratory event statistics PENDING
-> event family candidates PENDING
-> validated event definitions PENDING
-> evaluator_contract_v0_1 PENDING
-> locked evaluators PENDING
-> semantic_state_representation_contract_v0_1.md PENDING
-> state_transition_contract_v0_1.md PENDING
-> AlphaEvolve/RL/ML PENDING
```

## 13. Trabajo Pendiente

```text
1. Actualizar el mapa v3 para insertar esta capa antes de evaluadores bloqueados.
2. Marcar el +50% intradia como sampling_probe_human_seed, no event definition validada.
3. Marcar pre_event_30m/post_event_30m como sampling_window_controlled_seed.
4. Crear un registro simple de probes y ventanas si el siguiente experimento lo requiere.
5. Disenar el primer parameter sweep historico sobre 1m quote-guarded.
6. Producir el primer exploratory event statistics report.
7. Solo despues, disenar evaluadores bloqueados para definiciones candidatas promovidas.
```
