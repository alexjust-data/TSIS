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

TSIS no debe entenderse como:

- un conjunto de scripts aislados;
- una colección de notebooks desconectados;
- un repositorio de señales sin arquitectura;
- un backtester suelto;
- ni un laboratorio oportunista de experimentos difíciles de reconstruir.

TSIS debe entenderse como un stack completo con tres horizontes coordinados:

- `research and backtesting`;
- `live event-driven operation`;
- `offline learning and policy improvement`.

---

## 3. Módulos del sistema

TSIS está organizado como un monorepo compuesto por tres módulos principales:

- `01_TSIS_backtest_SmallCaps`
- `02_TSIS_webSocket_SmallCaps`
- `03_TSIS_Offline_RL`

### 3.1. 01_TSIS_backtest_SmallCaps

Es la capa de investigación, simulación y validación histórica.

Su misión es:

- construir datasets y universos defendibles;
- formalizar eventos y estados de mercado;
- simular ejecución con realismo suficiente;
- evaluar hipótesis, setups y estrategias;
- producir evidencia reproducible para promoción o descarte.

### 3.2. 02_TSIS_webSocket_SmallCaps

Es la capa de operación live y procesamiento en tiempo real.

Su misión es:

- ingerir datos live;
- construir features y eventos en tiempo real;
- enrutar señales o decisiones;
- coordinar ejecución y monitoreo;
- registrar evidencia operativa del sistema en vivo.

### 3.3. 03_TSIS_Offline_RL

Es la capa de aprendizaje secuencial sobre datos ya auditados y estados ya definidos.

Su misión es:

- construir datasets de aprendizaje offline;
- entrenar behavioral cloning y offline RL;
- evaluar políticas en entornos controlados;
- comparar candidatos de despliegue;
- retroalimentar research y ejecución sin romper los contratos del sistema.

### 3.4. System Boundaries

No todos los componentes del ecosistema forman parte del core institucional de TSIS.

Vendors, brokers, APIs externas, servicios auxiliares, herramientas de observabilidad y componentes de soporte deben tratarse como dependencias externas.

Pueden ser críticas para operar el sistema, pero no deben confundirse con:

- source of truth institucional;
- semántica canónica del repositorio;
- contratos internos compartidos;
- ni memoria persistente del sistema.

---

## 4. Modelo de capas

TSIS separa el sistema en capas con responsabilidades distintas.

Capas conceptuales:

- `raw data`
- `reference and universe`
- `features`
- `events`
- `states`
- `strategies or policies`
- `execution`
- `risk`
- `reporting and monitoring`
- `ML and RL`

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

Flujo global:

`data -> normalization -> reference/universe -> features -> event logic -> state logic -> strategy or policy -> execution or simulation -> evaluation -> promotion or quarantine`

### 5.1. Research path

En research, el flujo termina en:

- validación;
- análisis de robustez;
- evidencia reproducible;
- decisión explícita de promoción, revisión o descarte.

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

La dirección institucional correcta es:

- `research` formaliza y valida;
- `live` opera y evidencia;
- `RL` aprende sobre estructuras ya gobernadas;
- y el feedback hacia upstream debe volver como revisión explícita, no como deriva semántica informal.

---

## 6. Ciclo de vida institucional

Todo trabajo serio en TSIS debe recorrer un ciclo de vida reconocible.

### 6.1. Fases

1. `idea or hypothesis`
2. `formalization`
3. `dataset and config definition`
4. `research or implementation`
5. `validation`
6. `reproducibility check`
7. `promotion, quarantine, deprecation or archive`

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
- `ARCHITECTURE_OVERVIEW.md`: cómo fluye TSIS técnicamente.

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
