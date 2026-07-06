# Research Experiment Principles

Fecha: 2026-07-05
Estado: principles_initial

## Principio

Todo experimento TSIS debe ser declarativo, reproducible y validable.

Debe declarar:

```text
research_question
hypothesis
universe
inputs
probe_or_candidate_generator
parameter_grid
windows
outcomes
metrics
baselines
quality_gates
leakage_gates
lineage
promotion_rules
```

## Exploratorio Vs Validacion

```text
exploratory = descubrir estructura
validation = comprobar robustez
locked = evaluar sin cambiar reglas
production = operar o usar en shadow/live
```

## Regla Anti-Autoengano

No se promociona el mejor resultado exploratorio como conocimiento.

Primero debe pasar:

```text
baseline comparison
sample coverage
parameter sensitivity
out-of-sample/walk-forward si aplica
selection-bias accounting
complexity penalty
lineage reproducible
```
