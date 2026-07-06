Yo la enfocaría como la **constitución epistemológica de TSIS**: pocos documentos, muy estables, que expliquen cómo TSIS piensa, investiga y convierte datos en conocimiento.

Propuesta:

```text
C:\TSIS_Data\00_CTO\01_RESEARCH_PHILOSOPHY\

README.md

00_MANIFESTO\
  TSIS_RESEARCH_MANIFESTO.md

01_KNOWLEDGE_MODEL\
  scientific_discovery_engine.md
  research_question_to_operational_component_lifecycle.md
  knowledge_object_taxonomy.md

02_EXPERIMENTAL_METHOD\
  research_experiment_contract_v0_1.md
  evidence_and_validation_principles.md
  exploratory_vs_locked_research.md
  baselines_and_controls_principles.md

03_HUMAN_AND_AI_RESEARCHERS\
  human_researcher_role.md
  alphaevolve_as_researcher.md
  optimizer_mutation_boundaries.md

04_MARKET_SCIENCE_PHILOSOPHY\
  events_are_discovered_not_assumed.md
  state_event_outcome_separation.md
  strategy_is_not_event.md

05_RESEARCH_GOVERNANCE\
  promotion_criteria_principles.md
  reproducibility_lineage_principles.md
  anti_overfitting_and_multiple_testing_principles.md
```

Mi enfoque por documento:

```text
README.md
```

Mapa de la carpeta. Debe decir: “esta carpeta no contiene código ni contratos técnicos; contiene los principios que gobiernan toda investigación TSIS”.

```text
TSIS_RESEARCH_MANIFESTO.md
```

Documento emocional/fundacional. Qué es TSIS: no backtester, no bot, no framework ML; es un Scientific Discovery Engine para small caps.

```text
scientific_discovery_engine.md
```

El más importante. Define la cadena:

```text
Research Question
-> Research Experiment
-> Evidence
-> Knowledge Object
-> Validated Knowledge
-> Operational Component
```

```text
research_question_to_operational_component_lifecycle.md
```

Explica cómo una pregunta como “¿por qué unos pushes continúan y otros se desintegran?” acaba convirtiéndose, si pasa evidencia, en detector/evento/estrategia.

```text
knowledge_object_taxonomy.md
```

Define objetos de conocimiento:

```text
phenomenon
event family
validated event
state representation
transition pattern
reward hypothesis
strategy candidate
execution rule
risk rule
```

```text
research_experiment_contract_v0_1.md
```

Contrato base de todo experimento. Todo experimento debe declarar: pregunta, hipótesis, inputs, variables, controles, outcomes, baselines, métricas, criterios de promoción, lineage.

```text
evidence_and_validation_principles.md
```

Qué cuenta como evidencia: tamaño muestral, robustez temporal, OOS, walk-forward, costes, estabilidad, sensibilidad, leakage-free.

```text
exploratory_vs_locked_research.md
```

Separación crítica:

```text
exploratory = descubrir
locked = validar
production = operar
```

```text
baselines_and_controls_principles.md
```

Cómo evitar autoengaño: comparar contra random, universe baseline, gap-only, volume-only, time-of-day baseline, placebo events.

```text
human_researcher_role.md
```

Tu papel: intuición discrecional, lectura de mercado, generación de hipótesis, inspección visual, criterio cualitativo. No como “verdad”, sino como semilla científica.

```text
alphaevolve_as_researcher.md
```

Idea clave: AlphaEvolve no es magia ni capa final. Es otro investigador que propone experimentos dentro del mismo protocolo.

```text
optimizer_mutation_boundaries.md
```

Qué puede mutar y qué no: probes, ventanas, representaciones, detectores sí bajo contrato; raw data, leakage gates, outcomes, lineage no.

```text
events_are_discovered_not_assumed.md
```

Documento clave para lo que estamos hablando: +50% no es evento; es sampling probe. 30m no es verdad; es sampling window.

```text
state_event_outcome_separation.md
```

Separación sagrada:

```text
X = estado observable legal
event/probe = forma de mirar
y = outcome separado
policy = decisión posterior
```

```text
strategy_is_not_event.md
```

Tu scanner y tus setups discrecionales se traducen a fenómenos investigables, no se copian como verdades.

```text
promotion_criteria_principles.md
```

Cuándo algo sube de nivel:

```text
probe -> event family candidate -> validated event -> operational component
```

```text
reproducibility_lineage_principles.md
```

Todo resultado debe poder reconstruirse: versión de datos, script, config, fechas, universo, filtros, outputs.

```text
anti_overfitting_and_multiple_testing_principles.md
```

Muy importante antes de AlphaEvolve: si pruebas miles de variantes, el ganador puede ser azar. Aquí entra DSR, walk-forward, purged CV, penalización de complejidad.

Mi recomendación: **no crees todos los documentos de golpe con mucho contenido**. Crea primero estos 5:

```text
README.md
TSIS_RESEARCH_MANIFESTO.md
scientific_discovery_engine.md
research_experiment_contract_v0_1.md
events_are_discovered_not_assumed.md
```

Con eso ya tienes la base filosófica real para seguir.
