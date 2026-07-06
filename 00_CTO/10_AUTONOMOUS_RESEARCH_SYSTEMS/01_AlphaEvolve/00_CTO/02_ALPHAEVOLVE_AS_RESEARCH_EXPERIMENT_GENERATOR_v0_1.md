# AlphaEvolve As Research Experiment Generator Contract v0.1

Fecha: 2026-07-05
Estado: contract_initial_aligned_with_TSIS_LAB_ARCHITECTURE_v3
Owner layer: `00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve`

## Tesis

AlphaEvolve no es el corazon de TSIS.

El corazon de TSIS es:

```text
Scientific Validation Pipeline
```

AlphaEvolve es un generador de candidatos que debe producir objetos compatibles con el laboratorio TSIS:

```text
research_experiment
candidate_code
parameter_grid
representation_builder_candidate
event_detector_candidate
transition_candidate
policy_candidate
```

Ninguno de esos objetos queda aceptado por haber sido propuesto por AlphaEvolve.

## Posicion En La Arquitectura

```text
Scientific Discovery Engine

  Human Researcher      AlphaEvolve / Optimizer / Future Agent
          \             /
           \           /
            candidate research experiments
                     |
                     v
          Scientific Validation Pipeline
                     |
                     v
              Knowledge Objects
                     |
                     v
             Validated Knowledge
                     |
                     v
           Operational Components
```

## Input Permitido

AlphaEvolve solo puede consumir inputs gobernados:

```text
research_question
research_experiment_template
allowed_mutation_scope
canonical_state_version
event_state_version
outcome_version
parameter_sweep_protocol
execution_protocol
validation_pipeline_version
quality/leakage/lineage gates
budget and sandbox policy
```

## Output Permitido

AlphaEvolve puede producir:

```text
candidate_experiment.yaml
candidate_probe_definition
candidate_parameter_grid
candidate_window_definition
candidate_representation_builder
candidate_event_detector
candidate_transition_function
candidate_policy
candidate_code_diff
candidate_evidence_artifacts
candidate_run_manifest
candidate_lineage_manifest
```

Todo output debe quedar trazado a:

```text
parent_candidate_id
experiment_id
code_hash
input_versions
execution_protocol_version
validation_protocol_version
created_at
model_or_generator_id
```

## Superficies De Mutacion Permitidas

AlphaEvolve puede mutar solo superficies declaradas:

| Superficie | Ejemplo | Estado |
| --- | --- | --- |
| `sampling_probe` | `move_pct >= X` | permitido si es research, no evento validado |
| `parameter_grid` | thresholds, referencias, ventanas | permitido bajo protocolo de sweep |
| `representation_builder` | transformar observables legales en representacion candidata | permitido si no redefine estado canonico |
| `event_detector` | detector candidato sobre datos as-of | permitido si respeta cutoff/leakage |
| `transition_function` | paso entre representaciones/estados | permitido como candidato |
| `policy_candidate` | decision rule sobre estado validado | permitido solo despues de X/y/evaluacion |
| `evaluator_candidate` | propuesta de evaluador | no permitido en discovery normal; requiere experimento meta separado |

## Superficies Prohibidas

AlphaEvolve no puede modificar ni decidir:

```text
raw data
canonical state truth
market_state/event_state schema truth
outcome truth
lineage history
quality gates
leakage gates
validator pass/fail logic
sealed holdout membership
promotion status
production readiness
```

Si una propuesta necesita cambiar una de estas piezas, debe abrirse como cambio CTO separado, no como mutacion normal de AlphaEvolve.

## Reglas De Evaluacion

Toda ejecucion AlphaEvolve debe pasar por las mismas fases que un humano:

```text
1. contract validation
2. data availability validation
3. timestamp/cutoff validation
4. leakage validation
5. lineage validation
6. baseline comparison
7. exploratory evidence
8. statistical validation
9. promotion review
10. knowledge object registration
```

No se permite:

```text
optimizar directamente PnL como unica metrica
reutilizar holdout sellado durante search
escoger metricas despues de ver resultados
promocionar el mejor candidato sin correccion de multiple testing
usar selected_by_scanner como feature causal sin contrato
usar outcome futuro dentro del estado
```

## Relacion Con 00_TSIS_Lab

`00_TSIS_Lab` define el formato comun.

AlphaEvolve no crea un laboratorio paralelo.

Debe escribir o consumir experimentos en:

```text
C:/TSIS_Data/00_TSIS_Lab/04_experiments/
```

Y registrar resultados en:

```text
C:/TSIS_Data/00_TSIS_Lab/02_registries/
```

## Primer Uso Esperado

El primer uso no debe ser una estrategia live ni un optimizador de Sharpe.

Primer uso razonable:

```text
EXP_DAS_FRONTSIDE_DISCOVERY_0001
```

Rol de AlphaEvolve en ese caso:

```text
proponer variantes de sampling probes
proponer grids de referencia/threshold/window
proponer representation builders candidatos
proponer detectores candidatos despues de evidencia exploratoria
```

No debe declarar que `+50%`, `30m` o una familia concreta son verdad validada.

## Regla Final

```text
AlphaEvolve propone.
TSIS Lab ejecuta.
Scientific Validation Pipeline decide si hay conocimiento.
```

