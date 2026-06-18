# TSIS Lab Architecture

Fecha de creacion: 2026-06-18
Estado: arquitectura promovida desde `00_private/arquitectura.md`.

## Proposito

Este documento convierte la arquitectura fuente de `00_private/arquitectura.md`
en una arquitectura CTO promovida y legible por agentes.

`00_private/arquitectura.md` conserva valor historico como source note, pero no
gobierna directamente. La lectura activa para trabajo futuro es este documento,
junto con `LOCAL_RULES.md`, `README.md` y los contratos de modulo.

## Tesis

TSIS no existe solo para preguntar:

```text
Funciona esta estrategia?
```

TSIS existe para responder:

```text
Que eventos existen?
Por que algunos eventos generan grandes movimientos?
Que contexto produce mejores outcomes?
Que decision es mejor dentro de cada contexto?
Como puede evolucionar el propio laboratorio?
```

La arquitectura debe separar fenomeno, consecuencia, decision y evolucion.

## Cadena logica del laboratorio

```text
Data Foundation
-> Event Library
-> Event Engine
-> Outcome Research
-> Strategy Research
-> Pattern Discovery
-> Cluster Research
-> Machine Learning
-> Decision Models
-> Evolution Systems
```

Esta cadena es logica y funcional. No obliga a duplicar carpetas ni contratos en
`00_CTO`.

## 1. Data Foundation

### Objetivo

Construir una representacion fiable, auditada y reproducible del mercado.

Esta capa no busca edge ni estrategias. Su funcion es garantizar que todo el
sistema trabaja sobre datos correctos, trazables y comparables.

### Autoridad operativa

La autoridad operativa vive en:

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

`00_CTO` solo gobierna arquitectura y operating models relacionados.

### Outputs objetivo

```text
master_daily_table
master_intraday_table
data_quality_report
symbol_master
corporate_actions_table
calendar_table
```

Estos outputs no quedan institucionales por estar escritos aqui. Deben cerrarse
en `01_foundations` mediante contracts, schemas, registries, validators,
policies y evidencia.

## 2. Event Library

### Objetivo

Definir fenomenos observables del mercado.

Un evento responde:

```text
Que esta ocurriendo?
```

No responde:

```text
Donde entro?
Donde pongo el stop?
Cuando salgo?
Cuanto size tomo?
```

### Autoridad CTO

La Event Library vive en:

```text
13_TRADING_SYSTEMS/00_EVENT_LIBRARY
```

### Regla

```text
Evento != estrategia
```

Un mismo evento puede ser operado por multiples estrategias.

## 3. Event Engine

### Objetivo

Transformar master tables auditadas en registros estructurados de eventos.

### Inputs

```text
master_daily_table
master_intraday_table
event_definitions
```

### Output

```text
event_table
```

Cada fila de `event_table` representa un fenomeno observado, no un trade.

## 4. Outcome Research

### Objetivo

Medir que ocurrio despues de cada evento.

Outcome Research no evalua decisiones. Evalua consecuencias del mercado.

### Input

```text
event_table
```

### Output

```text
outcome_table
```

Ejemplos de campos:

```text
event_id
max_extension_pct
max_adverse_excursion_pct
close_return_pct
time_to_peak
time_to_failure
outcome_label
runner_score
```

## 5. Strategy Research

### Objetivo

Evaluar respuestas operativas ante eventos.

Strategy Research introduce por primera vez:

```text
entries
stops
exits
position management
risk management
```

### Inputs

```text
event_table
outcome_table
strategy_library
```

### Outputs

```text
strategy_results
strategy_performance
walk_forward_results
```

## 6. Pattern Discovery

### Objetivo

Encontrar relaciones estadisticas que expliquen por que algunos eventos generan
outcomes excepcionales y otros fracasan.

Pattern Discovery produce conocimiento, no estrategias.

### Inputs

```text
event_table
outcome_table
strategy_results
```

### Outputs

```text
discovered_patterns
candidate_hypotheses
```

## 7. Cluster Research

### Objetivo

Agrupar eventos por comportamiento y contexto.

No agrupa tickers.
No agrupa estrategias.
Agrupa fenomenos de mercado.

### Inputs

```text
event_table
outcome_table
discovered_patterns
```

### Outputs

```text
cluster_table
cluster_profiles
behavior_families
```

## 8. Machine Learning

### Objetivo

Modelar:

```text
market state -> future outcome
```

Machine Learning estima probabilidades. No decide trades.

### Inputs

```text
context
event
cluster
outcome_labels
```

### Outputs

```text
success_probability
runner_probability
top_percentile_probability
expected_extension
expected_risk
```

## 9. Decision Models

### Objetivo

Responder:

```text
Que accion maximiza el resultado esperado bajo este contexto?
```

Decision Models convierten estado y probabilidades en politica de accion.

### Inputs

```text
context
event
cluster
ml_probabilities
outcome_history
```

### Outputs

```text
action_policy
entry_policy
exit_policy
sizing_policy
risk_policy
```

## 10. Evolution Systems

### Objetivo

Evolucionar automaticamente detectores, features, clusters, filtros,
estrategias, reglas de decision y evaluadores candidatos dentro de un laboratorio
gobernado.

### Requisito

No hay Evolution Systems institucionales sin:

- data auditada;
- `event_table`;
- `outcome_table`;
- evaluadores bloqueados;
- constraints;
- lineage;
- validacion OOS o equivalente.

AlphaEvolve y OpenEvolve no son el punto de partida. Son motores posteriores que
pueden operar cuando el laboratorio ya es evaluable.

## Mapeo funcional a carpetas

```text
Data Foundation
-> 01_TSIS_backtest_SmallCaps/01_foundations
-> 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS

Event Library
-> 00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY

Event Engine / Outcome Research / Strategy Research / Pattern Discovery /
Cluster Research / Decision Models / Evolution Systems
-> 00_CTO/13_TRADING_SYSTEMS, como arquitectura de conocimiento
-> modulo 01 cuando exista implementacion operativa de backtest/research

Machine Learning
-> 00_CTO/08_MACHINE_LEARNING, como doctrina de modelado
-> modulo 01 o 03 cuando exista implementacion operativa

Autonomous Research / AlphaEvolve
-> 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS, como referencia y diseno general
-> 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE, cuando gobierne Harness/sandbox
```

## Regla final

La arquitectura de TSIS Lab debe hacer imposible confundir:

```text
datos
eventos
outcomes
estrategias
patrones
clusters
probabilidades
decisiones
evolucion
```

Si una carpeta, documento o output mezcla esos niveles sin contrato explicito,
debe corregirse antes de tratarse como arquitectura activa.
