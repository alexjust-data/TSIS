# Scientific Discovery Engine

Fecha: 2026-07-05
Estado: architecture_principle_initial

## Definicion

`Scientific Discovery Engine` es la arquitectura mental superior de TSIS.

Su unidad de trabajo no es la estrategia, el evento ni el modelo.

Su unidad de trabajo es:

```text
research_experiment
```

## Cadena Canonica

```text
Research Question
-> Research Experiment
-> Execution
-> Evidence
-> Knowledge Object
-> Validated Knowledge
-> Operational Component
```

## Ejemplo

Pregunta:

```text
Por que algunos pushes intradia small caps continuan y otros se desintegran?
```

Experimento:

```text
barrer thresholds, referencias, ventanas, liquidez y contexto
```

Evidencia:

```text
MFE, MAE, return final, continuacion, fallo, coverage, sensibilidad, baseline
```

Knowledge object candidato:

```text
intraday_momentum_extension_family_candidate
```

Componente operativo futuro, si supera validacion:

```text
event detector
state representation
strategy candidate
risk rule
policy
```

## Relacion Con Tablas De Estado

Las tablas de estado no descubren conocimiento por si solas.

Proveen:

```text
X legal observable as-of
```

Los outcomes proveen:

```text
Y separado
```

El experimento define como mirar ambos sin contaminar uno con otro.

## Relacion Con AlphaEvolve

AlphaEvolve no es el corazon de esta arquitectura.

AlphaEvolve puede proponer experimentos, representaciones, detectores o politicas.

Pero todos pasan por la misma cadena:

```text
Candidate Experiment
-> Scientific Validation Pipeline
-> Knowledge Object
```
