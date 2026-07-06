# AlphaEvolve En Finanzas - Vision TSIS v3

Fecha de revision: 2026-07-05
Estado: vision_operativa_alineada_con_TSIS_LAB_ARCHITECTURE_v3

## Tesis

AlphaEvolve no debe ser tratado como el centro de TSIS.

TSIS es un Scientific Discovery Engine.

El centro de aceptacion cientifica es:

```text
Scientific Validation Pipeline
```

AlphaEvolve es una fuente posible de candidatos, igual que un humano puede ser una fuente de candidatos.

```text
Human Researcher      AlphaEvolve
      |                    |
      v                    v
candidate research experiments
              |
              v
Scientific Validation Pipeline
```

## Por Que Esto Importa En Finanzas

En finanzas, generar muchas variantes aumenta el riesgo de overfitting, data snooping y falsos edges.

Por eso AlphaEvolve no puede optimizar directamente:

```text
max Sharpe
best equity curve
best threshold after seeing results
```

Ese uso convertiria AlphaEvolve en una fabrica industrial de sobreajuste.

## Uso Correcto En TSIS

AlphaEvolve debe proponer objetos investigables:

```text
sampling probes
parameter grids
window definitions
representation builders
event detector candidates
transition hypotheses
policy candidates
```

Cada objeto se convierte en un `research_experiment` o en una pieza versionada de un experimento.

Luego pasa por:

```text
execution protocol
lineage gates
leakage gates
quality gates
baseline comparison
statistical validation
promotion rules
```

## Que Puede Mutar

AlphaEvolve puede mutar:

```text
como mirar el mercado
que probe probar
que grid explorar
que representacion construir desde observables legales
que detector candidato ejecutar
que transicion candidata modelar
que politica candidata comparar
```

## Que No Puede Mutar En Un Run Normal

AlphaEvolve no puede mutar:

```text
raw data
market_state/event_state truth
outcome truth
validators
quality gates
leakage gates
lineage
sealed holdout
promotion status
```

Si se quiere evolucionar un evaluador, eso debe ser un experimento meta separado y nunca debe correr contra el mismo holdout usado para aceptar estrategias o detectores.

## Relacion Con Lopez De Prado

Lopez de Prado no es un obstaculo para AlphaEvolve.

En TSIS, la disciplina de multiple testing, DSR, PBO, purged/embargoed validation, holdout sellado y control de leakage es el sistema inmunologico que evita convertir busqueda evolutiva en sobreajuste.

La frase operativa es:

```text
AlphaEvolve amplifica el evaluador.
Si el evaluador mide ruido, amplifica ruido.
Si el pipeline mide evidencia robusta, puede amplificar discovery.
```

## Resultado Deseado

AlphaEvolve no debe buscar directamente una estrategia ganadora.

Debe ayudar a TSIS a descubrir y refinar:

```text
observables derivados candidatos
representaciones de estado
event families
detectores
transiciones
politicas
```

Solo lo que sobreviva al Scientific Validation Pipeline puede convertirse en conocimiento validado u operational component.
