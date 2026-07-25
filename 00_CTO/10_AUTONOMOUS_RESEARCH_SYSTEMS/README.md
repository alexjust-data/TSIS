# Autonomous Research Systems

Fecha: 2026-07-05
Estado: lectura_alineada_con_TSIS_LAB_ARCHITECTURE_v3

## Rol

`10_AUTONOMOUS_RESEARCH_SYSTEMS/` estudia sistemas capaces de proponer investigacion automatizada:

```text
AlphaEvolve
FunSearch
OpenEvolve
research agents
automated hypothesis generation
evolutionary search
```

Esta carpeta no es el centro de TSIS.

El centro operativo de investigacion es:

```text
C:/TSIS_Data/03_TSIS_Lab
```

El centro de aceptacion cientifica es:

```text
Scientific Validation Pipeline
```

## Regla De Arquitectura

Un sistema autonomo puede proponer candidatos, pero no puede aceptar conocimiento por autoridad propia.

```text
human_researcher
alphaevolve_or_optimizer
future_research_agent

-> candidate research experiment
-> same execution protocol
-> same scientific validation pipeline
-> evidence
-> knowledge object
-> validated knowledge only if promoted
```

## No-Goals

Esta carpeta no debe convertirse en:

```text
fuente de verdad de datos
lugar de materializaciones pesadas
atajo para saltar validacion
carpeta de estrategias promocionadas
autoridad sobre market_state/outcomes/evaluators
```

## Lecturas Obligatorias

```text
C:/TSIS_Data/00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
C:/TSIS_Data/03_TSIS_Lab/README.md
C:/TSIS_Data/03_TSIS_Lab/01_contracts/research_experiment_contract_v0_1.md
C:/TSIS_Data/03_TSIS_Lab/01_contracts/scientific_validation_pipeline_contract_v0_1.md
C:/TSIS_Data/00_CTO/01_RESEARCH_PHILOSOPHY/03_HUMAN_AND_AI_RESEARCHERS/human_and_alphaevolve_common_protocol.md
```

## Estado De AlphaEvolve

La lectura operativa de AlphaEvolve vive en:

```text
01_AlphaEvolve/README.md
01_AlphaEvolve/00_CTO/02_ALPHAEVOLVE_AS_RESEARCH_EXPERIMENT_GENERATOR_v0_1.md
```
