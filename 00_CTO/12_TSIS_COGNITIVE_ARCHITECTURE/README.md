# TSIS Cognitive Architecture

Estado: draft v0.1
Fecha: 2026-06-12
Ambito: 00_CTO / diseno transversal de automatizaciones, agentes y evolucion de investigacion.

## Proposito

Este documento define el primer plano de trabajo para convertir TSIS en una fabrica de investigacion cuantitativa reproducible, agentica y evaluable.

No sustituye a `PROJECT_RULES.md`, `AGENTS.md`, contratos de `01_foundations` ni changelogs. Este documento sirve para ordenar el pensamiento CTO y promover despues reglas canonicas cuando esten validadas.

## Estructura vigente

`12_TSIS_COGNITIVE_ARCHITECTURE/` queda organizado por dominio Harness:

```text
00_SHARED_HARNESS_KERNEL/
10_DATA_QUALITY_HARNESS/
20_SERSAN_DISTILLATION_HARNESS/
```

Regla:

```text
lo comun vive en SHARED;
lo especifico vive dentro de su Harness;
ningun Harness debe usar toolchain, runbooks o artifacts de otro Harness sin declararlo.
```

## Documentos de referencia activos

Leer en este orden:

1. `00_SHARED_HARNESS_KERNEL/agentic_harness_architecture_reference.md`
   - Define que es un Harness agentic, sus fundamentos, arquitectura, matematicas, fuentes y aplicacion TSIS.
2. `00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md`
   - Fija que generadores, validadores, prompts y configs Harness vivan en el proyecto, con hashes y `run_manifest.json`.
3. `00_SHARED_HARNESS_KERNEL/shared_run_manifest_contract.md`
   - Fija el minimo comun de `run_manifest.json` para todos los Harness.
4. `00_SHARED_HARNESS_KERNEL/shared_validation_principles.md`
   - Fija principios comunes de validacion, parada y revision humana.
5. `10_DATA_QUALITY_HARNESS/README.md`
   - Entrada operativa del Data Quality Harness y estado de datasets pendientes.
6. `10_DATA_QUALITY_HARNESS/data_audit_harness_agentic_operating_map.md`
   - Aplica Harness a la auditoria de data y al futuro control live.
7. `10_DATA_QUALITY_HARNESS/data_audit_completion_artifact_contract.md`
   - Fija artefactos obligatorios para cerrar datasets pendientes con calidad comparable a `daily`, `quotes`, `trades` y `1m`.
8. `10_DATA_QUALITY_HARNESS/runbooks/2026-06-12_overnight_data_audit_completion_harness_runbook.md`
   - Runbook single-agent para cerrar auditoria pendiente con el estandar inspector maduro.
9. `10_DATA_QUALITY_HARNESS/runbooks/2026-06-12_data_audit_agent_prompt_pack.md`
   - Prompt unico `SINGLE_AGENT_DATA_AUDIT_COMPLETION` para el siguiente run autonomo.
10. `10_DATA_QUALITY_HARNESS/future_live_data_quality_contract.md`
   - Reserva el contrato futuro para live data quality; aun no es operativo.
11. `20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_protocol.md`
   - Aplica Harness a la destilacion del curso SersanSistemas.
12. `20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md`
   - Fija los schemas de outputs por lesson pack.
13. `20_SERSAN_DISTILLATION_HARNESS/sersan_pilot_harness_runbook.md`
   - Define como ejecutar pilotos Sersan, iterar, validar, parar e incrustar imagenes relevantes.

## Artefactos activos

`20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/` contiene los
primeros artefactos generados bajo contrato para Sersan Distillation Harness.

Inventario vigente:

- `20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/_corpus_inventory/sersan_corpus_manifest.csv`
- `20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/_corpus_inventory/sersan_corpus_manifest.md`
- `20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/_corpus_inventory/sersan_corpus_manifest_summary.json`
- `20_SERSAN_DISTILLATION_HARNESS/sersan_distillation_artifacts/<lesson_id>/lesson_pack_manifest.json`

Estado actual:

- `17` lesson packs inventariados;
- `2108` referencias de imagen;
- `0` imagenes locales sin resolver;
- `1` lesson pack `inventory_only` por falta de numero de practica.

## Tesis central

TSIS no debe empezar por "un bot que inventa estrategias". TSIS debe empezar por un sistema que sabe:

1. que datos puede usar;
2. que contratos gobiernan esos datos;
3. que agente puede tocar cada cosa;
4. que evaluador decide si algo funciona;
5. que evidencia queda guardada;
6. que cambios pasan a investigacion, backtest, paper/live o descarte.

La formula operativa es:

```text
TSIS = memoria + contratos + agentes + evaluadores + ejecucion reproducible + evolucion controlada
```

## Dos motores, no uno

### Harness

Harness es el sistema operativo de trabajo agentico.

Su funcion no es descubrir alpha. Su funcion es coordinar trabajo largo, dividir tareas, aplicar reglas, lanzar herramientas, leer resultados, pedir aprobaciones, registrar evidencia y detener procesos inseguros.

En TSIS, Harness debe gobernar:

1. auditoria de datos historica y diaria;
2. mantenimiento de contratos;
3. extraccion del conocimiento de SersanSistemas;
4. investigacion de estrategias;
5. ejecucion de backtests;
6. generacion de dossiers;
7. vigilancia de calidad en tiempo real;
8. promocion o rechazo de artefactos.

### AlphaEvolve

AlphaEvolve es el motor de busqueda evolutiva.

Su funcion no es decidir si una estrategia es buena. Su funcion es proponer candidatos: codigo, reglas, filtros, parametros, features, heuristicas de ejecucion o mejoras de rendimiento.

En TSIS, AlphaEvolve solo puede operar dentro de un sandbox donde:

1. el candidato es modificable;
2. el evaluador no es modificable;
3. los datos fuente no son modificables;
4. el fitness esta versionado;
5. todo run deja manifiesto, codigo, parametros, semillas, resultados y evidencia.

Regla base: el LLM puede tocar el candidato, pero no el juez.

## Capas de arquitectura

### 1. Fuente y memoria

Incluye documentacion canonica, contratos, changelogs, ADRs, run manifests, experimentos, fallos, decisiones y lecciones.

Objetivo: que ningun conocimiento importante viva solo en prompts o conversaciones.

### 2. Contratos y semantica

Define que significa cada dataset, precio, etiqueta, feature, universe, ventana temporal y estado de calidad.

Objetivo: evitar que ML, backtest o agentes mezclen datos con semantica incompatible.

### 3. Harness agentico

Define roles, permisos, workflows, checkpoints, herramientas, observabilidad y criterios de parada.

Objetivo: que los agentes trabajen como equipo tecnico, no como chatbots.

### 4. Evaluadores

Define pruebas automaticas, metricas, stress tests, validaciones estadisticas, inspecciones visuales y reglas de promocion.

Objetivo: medir robustez real antes de optimizar.

### 5. Ejecucion reproducible

Define pipelines, entornos, seeds, caches permitidas, manifests, versionado de datos/modelos/estrategias y compute distribuido.

Objetivo: poder reconstruir cualquier resultado.

### 6. Evolucion controlada

Define donde AlphaEvolve puede buscar y bajo que limites.

Objetivo: acelerar descubrimiento sin convertir la investigacion en p-hacking automatizado.

## Principios extraidos de SersanSistemas

Estos principios vienen de una lectura selectiva del corpus revisado, especialmente robustez de Apolo, BRaC, walk-forward, money management y portfolio.

### Robustez

1. Un set no vale por ser el mejor punto; vale si vive dentro de una zona robusta.
2. Los vecinos importan: si un paso de parametro destruye el resultado, el set es fragil.
3. Hay que distinguir sensibilidad, tolerancia y robustez.
4. Los mapas 2D/pivots son preferibles a superficies 3D si estas ocultan escala o densidad.
5. El objetivo es encontrar regiones estables, no islas espectaculares.

### Validacion

1. IS/OOS, BRaC y walk-forward son pruebas de estres complementarias, no religiones.
2. Walk-forward sirve sobre todo para estresar adaptacion temporal, no para elegir magicamente parametros.
3. Anchored WF puede tener mas sentido cuando se necesita acumular muestra.
4. Rolling WF puede ser demasiado inestable si hay pocos trades o regimenes largos.
5. La significacion estadistica manda: pocos trades no validan una estrategia aunque la curva sea bonita.

### Optimizacion

1. No se optimizan todos los inputs por defecto.
2. Se separan constantes, money management, parametros heredados robustos y variables realmente bajo estudio.
3. La busqueda grande sirve para mapear regiones; la seleccion final debe reducir espacio y evitar sobreoptimizacion.
4. El fitness debe compararse entre metricas: retorno, drawdown, estabilidad, expectancy, PPC, robustness, etc.
5. Penalizar artefactos irreales de ejecucion es obligatorio.

### Money management

1. La ventaja debe venir del sistema, no de martingalas.
2. Fixed fractional y volatility position sizing son bases razonables.
3. El riesgo usado como denominador manda el tamano de posicion; por tanto debe estar auditado.
4. Volatilidad normalizada es preferible a ATR en puntos para historicos largos.
5. Debe existir suelo de volatilidad para evitar sobrecargar contratos en calma previa a expansion.
6. Deben existir minimos/maximos de posicion y limites de exposicion.

### Portfolio

1. Mejor pocos sistemas robustos que muchos sistemas mediocres.
2. Diversificacion no es meter cosas distintas; es combinar robustez, baja correlacion y comportamiento complementario.
3. Money management controla exposicion; portfolio controla diversificacion. Ambos estan conectados.
4. Equal weighted por volatilidad es una base pragmatica mejor que una optimizacion fragil de pesos.
5. Los optimizadores de portfolio deben tener minimos y maximos; no pueden concentrar todo en un unico ganador historico.
6. Rebalancear por calendario y tolerancias suele ser mas robusto que reaccionar continuamente.
7. Reducir exposicion por drawdown puede tener sentido, pero exige regla explicita de reentrada.

## Evaluador minimo de estrategia TSIS

Ningun candidato de estrategia debe promocionar sin pasar un evaluador que cubra:

1. dataset usado, version, calidad, contratos y price view;
2. universe admissible y ventana temporal PTI;
3. split/corporate action semantics;
4. halts, liquidez, spreads, costes, comisiones, slippage y fill realism;
5. sample size, numero de trades y distribucion temporal;
6. IS/OOS o alternativa documentada;
7. regime split;
8. vecinos de parametros y mapas de robustez;
9. sensibilidad a costes y latencia;
10. drawdown, worst trade, losing streak y recuperacion;
11. estabilidad de expectancy y avg trade;
12. turnover y capacidad;
13. complejidad del sistema;
14. aportacion marginal a portfolio;
15. dossier explicativo con limites de lo que no demuestra.

## Primeros casos de uso Harness

### H1. Data Quality Harness

Objetivo: convertir la auditoria historica de `01_foundations` en una operacion repetible y luego diaria.

Fases:

1. leer contratos existentes;
2. ejecutar checks por dataset;
3. comparar contra thresholds;
4. generar manifiesto y dossier;
5. abrir incidencias;
6. bloquear consumidores si la calidad cae bajo minimo.

Por que primero: ya existe trabajo avanzado, tiene evidencia y es menos ambiguo que inventar estrategias.

### H2. Sersan Distillation Harness

Objetivo: convertir el curso en doctrina mecanica TSIS.

Salida esperada:

1. glosario operacional;
2. reglas de robustez;
3. checklist de backtest;
4. patrones de validacion;
5. anti-patrones;
6. ejemplos visuales indexados;
7. criterios convertibles en evaluadores.

Por que: antes de evolucionar estrategias hay que saber que significa "bueno" segun el criterio experto del proyecto.

### H3. Strategy Research Harness

Objetivo: coordinar investigacion desde hipotesis hasta dossier.

Flujo:

```text
hipotesis -> contrato de experimento -> backtest -> evaluador -> dossier -> decision
```

Por que: evita que cada estrategia sea un experimento artesanal irreproducible.

### H4. Contract Steward Harness

Objetivo: mantener consistencia entre contratos, changelogs, price semantics, datasets y consumidores.

Por que: TSIS tiene muchas capas; sin agente steward, la documentacion canonica divergira.

### H5. Live Data Quality Harness

Objetivo: reutilizar los estandares historicos como control diario de data entrante.

Flujo futuro:

```text
stream -> microchecks -> alertas -> quarantine -> dossier diario -> decision humana/automatica
```

Por que: si una data feed falla en real time, ML/backtest/live quedan contaminados.

## Primeros casos de uso AlphaEvolve

### A1. Optimizacion de rendimiento del backtester

Primer caso recomendado.

Razon: es menos peligroso que evolucionar alpha; el evaluador puede ser exactitud + velocidad + equivalencia de resultados.

### A2. Busqueda de filtros sobre estrategia conocida

Razon: parte de una logica humana y reduce espacio de busqueda.

Restriccion: AlphaEvolve no puede tocar el evaluador ni ampliar datos despues de ver OOS.

### A3. Features para meta-labeling

Razon: puede proponer transformaciones, interacciones y filtros.

Restriccion: toda feature debe respetar timestamp, disponibilidad historica y leakage checks.

### A4. Execution y sizing heuristics

Razon: en smallcaps/microcaps el edge puede morir por ejecucion.

Restriccion: incluir halts, spreads, liquidez, partial fills y capacidad.

### A5. Portfolio constrained search

Razon: una estrategia mediocre aislada puede aportar diversificacion, y una estrategia top puede empeorar cartera.

Restriccion: optimizacion con minimos/maximos, volatilidad target y penalizacion de concentracion.

## Orden de implantacion

### Paso 0. Cerrar vocabulario

Crear documentos minimos:

1. `TSIS_AGENT_OPERATING_MODEL.md`;
2. `TSIS_AGENT_ROLES.md`;
3. `TSIS_EVALUATOR_CONTRACT_TRADING.md`;
4. `SERSAN_DISTILLATION_PROTOCOL.md`;
5. `ALPHAEVOLVE_TSIS_SANDBOX_POLICY.md`;
6. `DATA_QUALITY_HARNESS_OPERATING_MODEL.md`.

### Paso 1. Harness sobre data quality

Automatizar lo que ya existe en `01_foundations`, sin cambiar semantica ni mover evidencia.

Done cuando un agente pueda ejecutar, resumir y reportar calidad de un dataset con manifiesto reproducible.

### Paso 2. Harness sobre Sersan

Extraer doctrina mecanica desde el corpus revisado, con referencias a practica, seccion e imagen.

Done cuando cada regla de robustez tenga origen, interpretacion y traduccion a check/evaluador.

### Paso 3. Evaluador de estrategia v0

Codificar el primer contrato de evaluacion: no para maximizar alpha, sino para rechazar basura.

Done cuando una estrategia pueda fallar por datos, muestra, costes, fragilidad, leakage, ejecucion o portfolio.

### Paso 4. AlphaEvolve sandbox

Arrancar con optimizacion tecnica o estrategia muy acotada.

Done cuando existan archivo candidato, evaluator lock, run manifest, archive, ranking y dossier.

### Paso 5. Promocion a live/paper

Conectar research con controles diarios de data, ejecucion y supervision.

Done cuando todo candidato tenga estado: rejected, research, paper, live_candidate, live, retired.

## Reglas de seguridad

1. Ningun agente modifica raw/certified data.
2. Ningun agente cambia contratos canonicos sin ADR o revision humana.
3. Ningun AlphaEvolve cambia evaluadores durante un run.
4. Ningun backtest promociona sin costes, slippage y semantica de precio documentada.
5. Ninguna feature ML se acepta sin timestamp y leakage check.
6. Ninguna estrategia live cambia por decision autonoma sin regla previa y aprobacion.
7. Ningun resultado se considera valido sin manifest y evidencia.

## Mapa de carpetas 00_CTO

`00_private`: notas privadas, intuiciones y borradores no canonicos.

`03_AGENT_ENGINEERING`: patrones generales de agentes, roles, permisos, herramientas y AGENTS standards.

`05_EVALUATION_SYSTEMS`: criterios de evaluacion, evals de agentes y evaluadores de trading.

`06_MLOPS_AND_REPRODUCIBILITY`: custodia cientifica, versionado, manifests y reproducibilidad.

`10_AUTONOMOUS_RESEARCH_SYSTEMS`: teoria y referencias de AlphaEvolve, FunSearch, OpenEvolve y discovery systems.

`11_MARKET_SCIENCE`: representacion del estado de mercado y principios de microestructura/causalidad/riesgo.

`12_TSIS_COGNITIVE_ARCHITECTURE`: aplicacion concreta a TSIS. Aqui vive el plano transversal.

`99_REFERENCE_LIBRARY`: fuentes externas y corpus original. No debe ser canon hasta destilarse.

## Referencias externas iniciales y lectura para TSIS

1. Anthropic, "Building effective agents": https://www.anthropic.com/engineering/building-effective-agents

Lectura TSIS: empezar con workflows simples, herramientas claras, checkpoints, evaluacion y guardrails antes de subir autonomia. Esto justifica que Data Quality Harness y Sersan Distillation Harness sean workflows primero y agentes autonomos despues.

2. OpenAI, "Introducing Codex": https://openai.com/index/introducing-codex/

Lectura TSIS: los agentes rinden mejor con `AGENTS.md`, entorno configurado, documentacion fiable y tests. Esto justifica que TSIS trate contratos, manifests, READMEs y tests como parte del sistema agentico, no como documentacion secundaria.

3. Google DeepMind, "AlphaEvolve": https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/

Lectura TSIS: AlphaEvolve funciona porque combina generacion de codigo con evaluadores automaticos que verifican, ejecutan y puntuan candidatos. DeepMind reporta usos en data centers, chip design, AI training, kernels y problemas matematicos. Para TSIS, la analogia correcta no es "inventar estrategias libremente", sino "evolucionar candidatos bajo evaluadores bloqueados".

4. "Agentic Harness Engineering" (arXiv 2026): https://arxiv.org/abs/2604.25850

Lectura TSIS: el harness tambien puede evolucionar, pero solo si hay observabilidad de componentes, experiencia y decisiones. Para TSIS esto implica registrar que agente cambio que, por que predijo mejora, que resultado obtuvo y si el cambio fue revertible.

## Decision v0

La prioridad inmediata de TSIS es Harness antes que AlphaEvolve.

Razon: AlphaEvolve sin evaluadores, contratos y memoria solo automatiza sobreoptimizacion. Harness crea el sistema que permite que AlphaEvolve sea util, medible y seguro.

