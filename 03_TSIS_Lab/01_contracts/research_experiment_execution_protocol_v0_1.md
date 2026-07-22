# Research Experiment Execution Protocol v0.1

Fecha: 2026-07-05
Estado: protocol_defined_initial

## Objetivo

Definir como se ejecuta un `research_experiment` en TSIS.

Este protocolo no busca ganar dinero directamente. Busca producir evidencia reproducible.

## Flujo General

```text
1. definir pregunta cientifica
2. escribir experiment.yaml
3. validar contrato del experimento
4. resolver module bridges y datos disponibles
5. materializar casos historicos
6. construir ventanas
7. unir X legal as-of si aplica
8. medir outcomes separados
9. generar evidencia exploratoria
10. aplicar criterios de promocion
11. registrar knowledge object o rechazo
```

## Fase 1 - Pregunta

Una pregunta valida debe poder responderse con evidencia historica gobernada.

Ejemplo:

```text
Que condiciones hacen que un push intradia en small caps continue o falle?
```

## Fase 2 - Experimento Declarativo

Todo experimento se declara en `experiment.yaml`.

El YAML debe contener:

```text
research_question
hypothesis
universe_definition
probe_definition
parameter_grid
windows
outcome_matrix
baselines
validation_plan
promotion_rules
```

## Fase 3 - Preflight

Antes de ejecutar debe comprobarse:

```text
input paths existen
versiones de state/outcome existen o estan declaradas como pending
cutoffs son legales
no hay outputs inline dentro de X
lineage se puede reconstruir
sample scope esta declarado
```

## Fase 4 - Ejecucion

La ejecucion puede usar datos, builders o backtests de modulos como SmallCaps. Eso no convierte a SmallCaps en adapter: SmallCaps mantiene su propio flujo operativo de investigacion y backtest clasico. `03_TSIS_Lab` conserva la definicion transversal del experimento.

Los outputs pesados deben ir a:

```text
E:/TSIS/data/research_experiments/<experiment_id>/
```

Los artefactos ligeros pueden ir dentro del folder del experimento:

```text
manifests/
reports/
configs/
```

## Fase 5 - Evidencia

La evidencia minima debe incluir:

```text
sample size
coverage
missingness
quality status
leakage status
outcome summary
parameter sensitivity
baseline comparison
known limitations
```

## Fase 6 - Promocion

Un experimento puede terminar en:

```text
rejected
needs_more_data
candidate_knowledge_object
validated_knowledge
operational_component_candidate
```

No se permite saltar directamente de `sampling_probe` a `validated_event_definition`.

## Relacion Con Evaluadores Bloqueados

Los evaluadores bloqueados vienen despues de evidencia suficiente.

Antes de eso se permiten evaluadores exploratorios, marcados como:

```text
evaluator_status = exploratory
production_locked = false
promotion_use = evidence_generation_only
```


