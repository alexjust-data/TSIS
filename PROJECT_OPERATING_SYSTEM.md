# TSIS Project Operating System

## 1. Rol de este documento

`PROJECT_OPERATING_SYSTEM.md` define cómo funciona TSIS como sistema global.

No es el manifiesto epistemológico del proyecto.
No es la constitución de versionado.
No es el contrato operativo específico para agentes.
No es el reglamento transversal de conducta.

Su función es describir:

- qué es TSIS como sistema;
- qué módulos lo componen;
- cómo se separan sus capas;
- cómo fluye el trabajo entre research, live y RL;
- y qué documentos gobiernan cada tipo de decisión.

Si `RESEARCH_PHILOSOPHY.md` define cómo piensa TSIS, `VERSIONING_STANDARDS.md` define cómo preserva memoria y trazabilidad, `AGENTS.md` define cómo deben actuar los agentes, y `PROJECT_RULES.md` define qué conducta es institucionalmente aceptable, este documento define cómo opera el sistema completo.

---

## 2. Qué es TSIS

TSIS es un sistema cuantitativo institucional, agent-first y multi-módulo, diseñado para construir, validar y operar conocimiento reproducible sobre microcaps y small caps.

Desde 2026-07-05, la lectura operativa vigente es más precisa:

```text
TSIS = Scientific Discovery Engine
```

Esto significa que TSIS no se organiza alrededor de AlphaEvolve, de un backtester o de una tabla concreta. Se organiza alrededor de un pipeline científico capaz de convertir datos gobernados en experimentos reproducibles, evidencia, conocimiento validado y componentes operativos.

La unidad científica central es:

```text
research_experiment
```

Y la cadena operativa superior es:

```text
Data Foundation
-> Canonical State / Event State / Outcomes
-> Research Experiment
-> Evidence
-> Scientific Validation Pipeline
-> Knowledge Object
-> Validated Knowledge
-> Operational Component
-> Backtest / Live / ML / RL / AlphaEvolve, segun corresponda
```

TSIS no debe entenderse como:

- un conjunto de scripts aislados;
- una colección de notebooks desconectados;
- un repositorio de señales sin arquitectura;
- un backtester suelto;
- ni un laboratorio oportunista de experimentos difíciles de reconstruir.

TSIS debe entenderse como un stack completo con horizontes coordinados:

- `scientific discovery and validation`;
- `research experiments and classic backtesting`;
- `live event-driven operation`;
- `offline learning and policy improvement`;
- `autonomous candidate generation` bajo contratos, nunca como autoridad final.

---

## 3. Modulos del sistema

TSIS esta organizado como un ecosistema con autoridad raiz, arquitectura aplicada, Data Foundation, backtest engine, laboratorio transversal, modulos operativos y data roots pesados.

Componentes principales:

- `00_CTO`
- `00_CTO_APPLIED_ARCHITECTURE`
- `01_TSIS_DATA_FOUNDATION`
- `02_TSIS_BACKTEST_ENGINE`
- `03_TSIS_Lab`
- `04_TSIS_webSocket_SmallCaps`
- `05_TSIS_Offline_RL`
- `06_TSIS_Trading_voice`
- `G:/TSIS/data`

`00_CTO` gobierna filosofia, arquitectura, mapas y reglas.

`00_CTO_APPLIED_ARCHITECTURE` conserva arquitectura aplicada, handoffs y gates de ingenieria gobernada.

`03_TSIS_Lab` organiza contratos operativos, registros, plantillas y experimentos cientificos reproducibles.

`G:/TSIS/data` conserva outputs pesados, materializaciones y runs voluminosos fuera de Git.

Para resolver referencias antiguas a carpetas raiz, leer `PATH_MIGRATION_2026_07_22.md`.

### 3.0. 00_CTO, arquitectura aplicada y Lab

`00_CTO` es la capa de autoridad. No ejecuta backtests ni materializaciones pesadas. Define la arquitectura, la filosofia, los mapas y las reglas de gobierno.

`00_CTO_APPLIED_ARCHITECTURE` traduce arquitectura en gates, handoffs y disenos aplicados, sin sustituir la autoridad CTO ni los contratos de los modulos.

`03_TSIS_Lab` es el laboratorio operativo transversal. No sustituye a los modulos. Define como un humano, AlphaEvolve u otro generador proponen y ejecutan `research_experiments` bajo la misma estructura.

La regla es:

```text
00_CTO = autoridad y arquitectura
00_CTO_APPLIED_ARCHITECTURE = arquitectura aplicada y gates
03_TSIS_Lab = contrato comun de experimentos
modulos = implementacion y ejecucion concreta
G:/TSIS/data = outputs pesados/materializaciones
```

### 3.1. 01_TSIS_DATA_FOUNDATION

Es el modulo operativo SmallCaps para Data Foundation: auditoria, certificacion, inmutabilidad, contratos, schemas, policies, validators, dossiers, builders de outputs gobernados y memoria cientifica preservada.

Su mision es:

- construir datasets y universos historicos defendibles;
- auditar y certificar calidad de market data;
- formalizar contratos de datos, price views, corporate actions, estados candidatos, eventos, outcomes y ventanas;
- mantener registries, validators, dossiers y lineage;
- preservar evidencia historica sin reescribirla por estetica;
- servir outputs gobernados a backtest, live, ML/RL y Lab sin que esas capas redefinan semantica upstream.

No es el motor profesional de backtest. El futuro motor vive en `02_TSIS_BACKTEST_ENGINE` y debe consumir esta Data Foundation por contrato.

### 3.2. 02_TSIS_BACKTEST_ENGINE

Es la futura capa de implementacion del backtester profesional TSIS.

Su mision sera:

- adaptar simulation inputs historicos/replay/live;
- ejecutar clock/event loop determinista;
- consumir Market State/Event State observables;
- coordinar decision policy, portfolio, risk, OMS, execution, accounting y ledgers;
- producir run manifests, reports y validacion reproducible.

La arquitectura/theory authority permanece en `00_CTO/14_BACKTEST_ENGINE` hasta promocion explicita.

### 3.3. 04_TSIS_webSocket_SmallCaps

Es la capa de operacion live y procesamiento en tiempo real.

Su mision es:

- ingerir datos live;
- construir features y eventos en tiempo real;
- enrutar senales o decisiones;
- coordinar ejecucion y monitoreo;
- registrar evidencia operativa del sistema en vivo.

### 3.4. 05_TSIS_Offline_RL

Es la capa de aprendizaje secuencial sobre datos ya auditados y estados ya definidos.

Su mision es:

- construir datasets de aprendizaje offline;
- entrenar behavioral cloning y offline RL;
- evaluar politicas en entornos controlados;
- comparar candidatos de despliegue;
- retroalimentar research y ejecucion sin romper los contratos del sistema.

### 3.5. 06_TSIS_Trading_voice

Es la capa Trading Decision Intelligence para voz, transcripcion, diario de decisiones, metricas de proceso y analisis del trader.

### 3.6. System Boundaries

No todos los componentes del ecosistema forman parte del core institucional de TSIS.

Vendors, brokers, APIs externas, servicios auxiliares, herramientas de observabilidad y componentes de soporte deben tratarse como dependencias externas.

Pueden ser criticas para operar el sistema, pero no deben confundirse con:

- source of truth institucional;
- semantica canonica del repositorio;
- contratos internos compartidos;
- ni memoria persistente del sistema.

---

## 4. Modelo de capas

TSIS separa el sistema en capas con responsabilidades distintas.

Capas conceptuales:

- `raw data`
- `reference and universe`
- `canonical observables`
- `canonical state / event state`
- `outcomes`
- `research experiments`
- `evidence`
- `knowledge objects`
- `validated knowledge`
- `event families / representations / transitions`
- `strategies or policies`
- `execution`
- `risk`
- `reporting and monitoring`
- `ML / RL / AlphaEvolve`

La distinción clave de la arquitectura v3 es:

```text
market_state/event_state = X legal observable as-of
outcomes = y separado
research_experiment = forma cientifica de mirar X e y
evidence = resultado reproducible
knowledge_object = conclusion candidata
validated_knowledge = conocimiento promovido
operational_component = detector, representacion, policy, estrategia o regla usable
```

### 4.1. Regla estructural

Estas capas no son una preferencia estética.
Son una protección contra contaminación semántica, deuda técnica y colapso arquitectónico.

### 4.2. Implicación operativa

Cada capa debe:

- tener responsabilidad reconocible;
- consumir inputs definidos;
- producir outputs trazables;
- respetar contratos compartidos;
- y evitar absorber silenciosamente el rol de otra capa.

### 4.3. Contract Stability

Los contratos compartidos entre módulos y capas deben evolucionar lentamente y con trazabilidad explícita.

La estabilidad contractual tiene prioridad sobre la conveniencia local de implementación.

Cuando un contrato compartido necesite cambiar:

- el cambio debe hacerse explícito;
- el impacto downstream debe identificarse;
- y la compatibilidad debe evaluarse antes de tratar el cambio como institucionalmente aceptable.

---

## 5. Flujo operativo global

TSIS opera como una cadena institucional de transformación de información.

Flujo global vigente:

```text
data
-> normalization / certification
-> reference / universe
-> canonical observables
-> canonical state / event state
-> outcomes separados
-> research_experiment
-> execution
-> evidence
-> scientific validation
-> knowledge_object
-> validated_knowledge
-> operational_component
-> backtest / live / ML / RL / AlphaEvolve, segun corresponda
```

El flujo antiguo `features -> events -> strategies -> evaluation` sigue existiendo como lectura local de algunas implementaciones, pero no es la arquitectura superior vigente.

### 5.1. Research path

En research, el flujo termina en:

- validación;
- análisis de robustez;
- evidencia reproducible;
- decisión explícita de promoción, revisión o descarte.

Desde la v3, research no empieza necesariamente con un evento ya definido. Puede empezar con:

```text
sampling_probe
parameter_sweep
research_question
candidate_event_family
representation_candidate
transition_hypothesis
```

Eso debe convertirse en `research_experiment` antes de producir evidencia institucional.

### 5.2. Live path

En live, el flujo termina en:

- señal o decisión operacional;
- ejecución o veto por riesgo;
- logging institucional;
- monitoreo del comportamiento real.

### 5.3. RL path

En RL, el flujo parte de estados y decisiones ya formalizados.
No debe inventar de forma autónoma una semántica paralela del mercado ni una source of truth distinta.

### 5.4. Operational Directionality

`research` puede promover estructuras validadas hacia `live` y hacia `offline RL`.

`live` y `offline RL` pueden generar evidencia, telemetría o feedback útil para research, pero no deben redefinir silenciosamente la semántica institucional upstream.

AlphaEvolve y otros sistemas autónomos siguen la misma regla. Pueden proponer candidatos o experimentos, pero no pueden redefinir verdad observable, outcomes, validadores, holdouts o promoción institucional.

La dirección institucional correcta es:

- `research` formaliza y valida;
- `live` opera y evidencia;
- `RL` aprende sobre estructuras ya gobernadas;
- y el feedback hacia upstream debe volver como revisión explícita, no como deriva semántica informal.

---

## 6. Ciclo de vida institucional

Todo trabajo serio en TSIS debe recorrer un ciclo de vida reconocible.

### 6.1. Fases

1. `research question or hypothesis`
2. `research_experiment design`
3. `dataset/state/outcome/config definition`
4. `execution`
5. `evidence report`
6. `scientific validation`
7. `knowledge_object candidate`
8. `validated_knowledge, falsification, quarantine, deprecation or archive`
9. `operational_component promotion when applicable`

### 6.2. Regla

Nada importante debe saltarse directamente desde intuición a institucional.
Toda promoción debe pasar por estructura, validación y trazabilidad suficientes para su nivel de impacto.

### 6.3. Promotion Flow Ownership

Toda promoción entre estados institucionales requiere:

- validación explícita;
- evidencia de reproducibilidad;
- ownership claro;
- y compatibilidad semántica con sistemas downstream.

Ningún componente debe avanzar en madurez institucional solo porque ya existe, porque funciona localmente o porque todavía no ha fallado.

---

## 7. Artefactos institucionales

TSIS distingue entre distintos tipos de artefactos.

### 7.1. Artefactos institucionales

Son aquellos de los que otros componentes pueden depender oficialmente.
Ejemplos:

- datasets promovidos;
- manifests oficiales;
- configs canónicas;
- simuladores oficiales;
- modelos promovidos;
- reports de validación;
- documentación raíz.

### 7.2. Artefactos exploratorios

Son válidos para investigación y diseño, pero no deben tratarse como contratos oficiales sin promoción explícita.

Ejemplos nuevos de la arquitectura v3:

- `research_experiment` en diseño;
- `sampling_probe` humano o generado;
- `parameter_sweep` exploratorio;
- `representation_candidate`;
- `event_detector_candidate`;
- `alphaevolve_candidate_run`;
- `evidence_report` aún no promovido.

### 7.3. Artefactos runtime

Son temporales, operativos o efímeros.
Pueden ser útiles, pero no son source of truth institucional.

---

## 8. Jerarquía documental

TSIS se gobierna mediante documentos raíz con roles distintos.

### 8.1. Documentos canónicos

- `PROJECT_OPERATING_SYSTEM.md`: cómo funciona TSIS globalmente.
- `PROJECT_RULES.md`: qué reglas transversales gobiernan el trabajo.
- `VERSIONING_STANDARDS.md`: cómo preserva memoria, trazabilidad y semántica histórica.
- `RESEARCH_PHILOSOPHY.md`: cómo piensa TSIS sobre mercado, datos, edge, causalidad y aprendizaje.
- `AGENTS.md`: cómo deben actuar agentes y colaboradores dentro del repositorio.
- `LONG_RUNNING_OPERATIONS_CONTRACT.md`: cómo deben instrumentarse operaciones largas, copias, materializaciones, auditorías, entrenamientos y builds para que nunca sean cajas negras.
- `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`: arquitectura CTO vigente; define TSIS como Scientific Discovery Engine.
- `03_TSIS_Lab/README.md`: laboratorio operativo transversal para `research_experiments`.
- `03_TSIS_Lab/01_contracts/`: contratos comunes de experimentos, ejecución, sweeps, validación y promoción de conocimiento.

### 8.2. Regla de precedencia

Las reglas locales pueden endurecer comportamiento, pero no contradecir documentos institucionales de nivel superior salvo excepción explícita y documentada.

### 8.3. Regla de no duplicación

Ningún documento raíz debe absorber innecesariamente el rol de otro.
Si una materia ya tiene documento canónico, este archivo debe referenciarla, no replicarla en detalle.

## 8.4. Institutional Memory

El repositorio es la memoria persistente de TSIS.

Ningún conocimiento operativo crítico debe depender exclusivamente de:

- conversaciones;
- prompts;
- supuestos no documentados;
- o memoria individual.

Toda pieza importante de conocimiento debe terminar representada en artefactos persistentes, versionados y recuperables.

---

## 9. Qué decisiones se resuelven aquí y cuáles no

### 9.1. Sí se resuelven aquí

Este documento sí debe responder:

- qué es TSIS como sistema;
- qué módulos existen;
- cómo se relacionan;
- qué capas estructuran el stack;
- cómo fluye el trabajo global;
- y qué documento gobierna cada dimensión institucional.

### 9.2. No se resuelven aquí

Este documento no debe contener en detalle:

- filosofía profunda de mercado, causalidad o edge;
- políticas completas de Git, branching, releases o manifests;
- reglas operativas finas para agentes;
- plantillas detalladas de PR o changelog;
- ni contratos locales específicos de una capa concreta.

Eso pertenece a otros documentos raíz o a `LOCAL_RULES.md` cuando aplique.

---

## 10. Criterio final del sistema

TSIS debe evolucionar como un sistema capaz de:

- pensar con rigor;
- operar con trazabilidad;
- aprender sin contaminar su memoria histórica;
- y crecer durante años sin degradarse en un conjunto de scripts, prompts y outputs ambiguos.

Ese es el estándar operativo global del proyecto.













