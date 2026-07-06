# Scientific Validation Pipeline Contract v0.1

Fecha: 2026-07-05
Estado: contract_defined_initial

## Principio

El corazon de TSIS es el `Scientific Validation Pipeline`.

AlphaEvolve, humanos y otros agentes proponen. La validacion decide.

## Flujo

```text
Candidate Experiment
-> Execution
-> Evidence
-> Exploratory Validation
-> Candidate Knowledge Object
-> Locked Validation
-> Validated Knowledge
-> Operational Component
```

## Capas De Validacion

```text
exploratory
validation
sealed_holdout
paper_or_shadow
production_monitoring
```

## Regla Anti-Sobreoptimizacion

Las validaciones usadas durante el loop dejan de ser evidencia final.

Si un generador ve una metrica durante muchas iteraciones, puede sobreoptimizarla. Por tanto:

```text
evolution/train != validation != sealed_holdout
```

## Gates Minimos

```text
leakage_free
quality_gates_passed
coverage_sufficient
sample_size_sufficient
baseline_beaten
parameter_sensitivity_checked
walk_forward_or_oos_checked
selection_bias_accounted
complexity_penalty_declared
lineage_reproducible
```

## Lopez De Prado Como Sistema Inmunologico

En TSIS, la estadistica contra multiple testing no bloquea la investigacion. La protege.

```text
AlphaEvolve amplifica busqueda
Lopez de Prado / statistical validation limita autoengano
```

DSR/PBO/CSCV/purged CV no son magia ni historia nueva. Son estimadores y gates para reducir el riesgo de sobreajuste.
