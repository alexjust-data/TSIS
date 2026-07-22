# Knowledge Object Promotion Contract v0.1

Fecha: 2026-07-05
Estado: contract_defined_initial

## Objetivo

Definir como una observacion experimental se convierte, o no, en conocimiento TSIS.

## Taxonomia

```text
observation
exploratory_result
candidate_phenomenon
event_family_candidate
representation_candidate
transition_candidate
policy_candidate
validated_knowledge
operational_component_candidate
operational_component
```

## Regla

Ningun resultado pasa a conocimiento validado solo porque tenga buen score.

Debe pasar por:

```text
reproducibility
coverage
quality
leakage gates
baseline comparison
robustness checks
promotion review
```

## Prohibido

```text
promover sampling_probe como evento validado
promover best backtest como edge
promover AlphaEvolve candidate sin validacion externa
promover labels/rewards sin contrato
promover outcome como feature
```

## Ejemplo

```text
+50% intradia
= sampling_probe_human_seed
!= validated event

Si un sweep muestra estructura robusta, puede nacer:

intraday_momentum_extension
= event_family_candidate
```
