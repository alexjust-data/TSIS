# Research Experiment Contract v0.1

Fecha: 2026-07-05
Estado: contract_defined_initial

## Objetivo

Definir la unidad operativa minima del laboratorio TSIS:

```text
research_experiment
```

Un `research_experiment` es un objeto declarativo y reproducible que convierte una pregunta cientifica en evidencia medible.

Debe poder ser propuesto por un humano o por AlphaEvolve sin cambiar la arquitectura.

## Principio Central

```text
humano y AlphaEvolve proponen el mismo tipo de objeto
la validacion cientifica decide que conocimiento sobrevive
```

AlphaEvolve no es la autoridad. El humano tampoco es autoridad final. La autoridad final es el pipeline de validacion cientifica.

## Campos Obligatorios

Todo experimento debe declarar:

```text
experiment_id
experiment_version
status
created_by
generator_type
research_question
objective
hypothesis
target_domain
input_state_versions
input_outcome_versions
source_data_scope
universe_definition
probe_definition
parameter_grid
controlled_variables
experimental_variables
windows
outcome_matrix
metrics
baselines
leakage_gates
quality_gates
lineage_requirements
statistical_validation_plan
promotion_rules
mutation_policy
expected_outputs
```

## Tipos De Generador

```text
human_researcher
alphaevolve
optimizer
research_agent
manual_replay
```

`generator_type` no cambia las reglas de validacion.

## Estados Permitidos

```text
draft
ready_for_preflight
preflight_failed
ready_to_execute
executed
exploratory_report_ready
candidate_knowledge_object
validated_knowledge
rejected
archived
```

## Mutabilidad

Un experimento debe declarar que se puede modificar y que no.

Permitido bajo contrato:

```text
sampling_probe_parameters
sampling_window_parameters
reference_price_functions
parameter_grids
representation_builders
event_family_detectors
policy_candidates
```

Prohibido:

```text
raw_data_rewrite
base_state_truth_rewrite
outcome_rewrite
lineage_rewrite
quality_gate_disable
leakage_gate_disable
sealed_holdout_reuse
production_locked_definition_mutation
```

## Relacion Con State/Event/Outcome

```text
state/event_state = X legal as-of
outcomes = y separado
research_experiment = diseña como mirar X e y
knowledge_object = conclusion promovida por evidencia
```

Un experimento nunca debe copiar outcomes dentro del estado.

## Acceptance Criteria v0.1

Un experimento es valido para ejecucion si:

```text
schema declarativo completo
inputs versionados
cutoffs declarados
lineage declarada
quality gates declarados
leakage gates declarados
outputs esperados declarados
no mezcla X con y
no trata probes humanos como eventos validados
```
