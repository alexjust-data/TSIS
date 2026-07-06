# Research Question To Operational Component Lifecycle

Fecha: 2026-07-05
Estado: lifecycle_initial

## Flujo

```text
research_question
-> research_experiment
-> evidence_report
-> candidate_knowledge_object
-> validation_protocol
-> validated_knowledge
-> operational_component_candidate
-> production/shadow component
```

## Niveles

| Nivel | Que es | Ejemplo |
| --- | --- | --- |
| Research Question | pregunta cientifica | por que unos pushes continuan y otros fallan? |
| Research Experiment | diseno ejecutable | sweep de thresholds/referencias/ventanas |
| Evidence | resultados reproducibles | MFE/MAE/continuacion/fallo por parametro |
| Knowledge Object | conclusion candidata | zona de comportamiento cambia entre X e Y |
| Validated Knowledge | evidencia robusta | fenomeno estable out-of-sample |
| Operational Component | pieza usable | detector, representation builder, risk rule, policy |

## Regla

No se puede saltar de intuicion a componente operativo.

```text
intuicion -> experimento -> evidencia -> validacion -> componente
```
