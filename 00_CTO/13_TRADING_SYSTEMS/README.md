# 13_TRADING_SYSTEMS

Fecha de actualizacion: 2026-06-18
Estado: capa CTO en refactor gobernado hacia arquitectura event-first.

`13_TRADING_SYSTEMS/` es la capa de conocimiento de dominio de mercado que TSIS
estudia, valida, convierte en eventos, mide con outcomes y solo despues traduce
en estrategias o modelos de decision.

No es una carpeta de backtests.
No es una carpeta de outputs.
No es la autoridad de datos.
No es el lugar donde se duplican contratos de `01_foundations`.

## Autoridad local

Antes de modificar esta carpeta, leer:

- `../LOCAL_RULES.md`
- `../TSIS_LAB_ARCHITECTURE_v3.md`
- `C:/TSIS_Data/03_TSIS_Lab/README.md`
- `00_EVENT_LIBRARY/README.md`

La autoridad de Data Foundation vive fuera de `00_CTO`, en:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations
```

`13_TRADING_SYSTEMS/` consume esa base auditada como dependencia conceptual,
pero no la redefine.

## Regla central

```text
evento != setup != estrategia != decision
```

Un evento describe algo observable en el mercado.
Una hipotesis explica por que podria existir edge.
Una estrategia define una respuesta operacional.
Un modelo de decision decide si actuar, cuando actuar, como dimensionar y bajo
que restricciones.

Por tanto:

- la Event Library no debe contener entradas, stops, targets, sizing ni reglas
  de ejecucion;
- la Strategy Library no debe redefinir datos upstream ni inventar eventos;
- los modelos ML no deben decidir operaciones por si solos;
- AlphaEvolve/OpenEvolve no puede actuar antes de existir eventos, outcomes,
  evaluadores bloqueados y constraints gobernados.

## Cadena funcional TSIS Lab

La lectura vigente para esta carpeta es:

```text
Data Foundation
-> Event Library
-> Event Engine Model
-> Outcome Research
-> Strategy Library
-> Strategy Research
-> Edge Hypotheses
-> Pattern Discovery
-> Cluster Research
-> Execution Models
-> Decision Models
-> Evolution Systems
```

`Data Foundation` no vive aqui. Es el input gobernado que produce, como minimo:

```text
master_daily_table
master_intraday_table
data_quality_report
symbol_master
corporate_actions_table
calendar_table
```

## Estado fisico actual

Esta carpeta ya fue normalizada al arbol event-first de Fase 2:

```text
00_EVENT_LIBRARY/
01_EVENT_ENGINE_MODEL/
02_OUTCOME_RESEARCH/
03_STRATEGY_LIBRARY/
04_STRATEGY_RESEARCH/
05_EDGE_HYPOTHESES/
06_PATTERN_DISCOVERY/
07_CLUSTER_RESEARCH/
08_EXECUTION_MODELS/
09_DECISION_MODELS/
10_EVOLUTION_SYSTEMS/
11_SQUEEZE_RESEARCH/
90_DISCRETIONARY_FRAMEWORKS/
99_EXPERIMENTAL/
```

Cambios ejecutados:

- `00__EVENT_LIBRARY/` fue renombrada a `00_EVENT_LIBRARY/`;
- `01_STRATEGY_LIBRARY/` fue movida a `03_STRATEGY_LIBRARY/`;
- las carpetas vacias antiguas se convirtieron en carpetas canonicas cuando
  habia equivalencia semantica clara;
- `02_SETUP_TAXONOMY/` fue eliminado porque estaba vacia y ya no es una capa
  top-level canonica;
- cada carpeta activa tiene README funcional minimo.

## Arbol canonico activo

El arbol gobernado activo es:

```text
13_TRADING_SYSTEMS/
  README.md
  00_EVENT_LIBRARY/
  01_EVENT_ENGINE_MODEL/
  02_OUTCOME_RESEARCH/
  03_STRATEGY_LIBRARY/
  04_STRATEGY_RESEARCH/
  05_EDGE_HYPOTHESES/
  06_PATTERN_DISCOVERY/
  07_CLUSTER_RESEARCH/
  08_EXECUTION_MODELS/
  09_DECISION_MODELS/
  10_EVOLUTION_SYSTEMS/
  11_SQUEEZE_RESEARCH/
  90_DISCRETIONARY_FRAMEWORKS/
  99_EXPERIMENTAL/
```

Los siguientes cambios deben hacerse en commits pequenos y verificables, no
como reestructuraciones silenciosas.

## Funcion de cada carpeta objetivo

### `00_EVENT_LIBRARY/`

Catalogo de eventos observables de mercado.

Inputs:

- datos auditados de Data Foundation;
- conocimiento de microestructura;
- fenomenos documentados en la referencia;
- `00_private/eventos.md` como nota fuente.

Outputs:

- definiciones de eventos;
- criterios observables;
- familias de eventos;
- prerequisitos de datos;
- exclusions y ambiguedades.

No-goals:

- estrategias;
- reglas de entrada;
- stops;
- targets;
- sizing;
- ejecucion.

### `01_EVENT_ENGINE_MODEL/`

Diseno conceptual del motor que transforma datos auditados en `event_table`.

Inputs:

- `master_daily_table`;
- `master_intraday_table`;
- `symbol_master`;
- `corporate_actions_table`;
- `calendar_table`;
- definiciones de `00_EVENT_LIBRARY/`.

Outputs:

- especificacion de `event_table`;
- reglas de deteccion;
- reglas de versionado de eventos;
- criterios de reproducibilidad.

### `02_OUTCOME_RESEARCH/`

Marco para medir que ocurre despues de un evento.

Inputs:

- `event_table`;
- datos de precios y liquidez auditados;
- calendario;
- constraints de corporate actions y halts.

Outputs:

- `outcome_table`;
- horizontes de outcome;
- metricas de continuation, reversal, failure, volatility, liquidity y risk;
- taxonomia de resultados.

### `03_STRATEGY_LIBRARY/`

Biblioteca de respuestas operacionales propuestas.

Inputs:

- eventos;
- outcomes;
- hipotesis de edge;
- doctrina de ejecucion.

Outputs:

- definiciones de estrategias;
- variantes;
- reglas de accion;
- prerequisitos;
- condiciones de invalidez.

Organizacion interna:

```text
carpetas numeradas por trader/fuente -> enseÃ±anzas, capturas, transcripts y
lecturas fuente

LONG/ SHORT/ FACTORS/ -> estrategias y factores TSIS propios, consolidados o
en investigacion
```

Regla:

```text
una estrategia responde a eventos; no inventa la realidad upstream
```

### `04_STRATEGY_RESEARCH/`

Marco para evaluar estrategias bajo reglas reproducibles.

Inputs:

- `event_table`;
- `outcome_table`;
- Strategy Library;
- constraints de ejecucion;
- costes, slippage y riesgo.

Outputs:

- resultados de estrategia;
- walk-forward results;
- robustness checks;
- failure modes;
- evidencia para promocion o descarte.

### `05_EDGE_HYPOTHESES/`

Hipotesis causales o mecanicas sobre por que podria existir edge.

No contiene estrategias completas.
No contiene resultados de backtest como autoridad final.

### `06_PATTERN_DISCOVERY/`

Patrones encontrados en datos, no ideas humanas sueltas.

Outputs esperados:

- candidate patterns;
- support metrics;
- stability notes;
- limits of evidence.

### `07_CLUSTER_RESEARCH/`

Agrupacion de comportamientos de mercado.

No agrupa tickers por identidad empresarial.
Agrupa estados, trayectorias, eventos y respuestas observadas.

### `08_EXECUTION_MODELS/`

Modelos de ejecucion realista.

Debe cubrir:

- fills;
- liquidity;
- spread;
- slippage;
- halts;
- partial fills;
- latency;
- constraints operativas.

### `09_DECISION_MODELS/`

Modelos que convierten probabilidades, constraints y contexto en decision.

Inputs:

- predicciones ML;
- outcomes;
- risk state;
- execution constraints;
- portfolio context.

Outputs:

- action policy;
- abstention rules;
- sizing policy;
- risk gates.

### `10_EVOLUTION_SYSTEMS/`

Espacio de diseno para AlphaEvolve/OpenEvolve aplicado a TSIS.

Solo puede operar cuando existan:

- datos auditados;
- eventos versionados;
- outcomes versionados;
- evaluadores bloqueados;
- constraints explicitos;
- lineage completo;
- validacion out-of-sample.

### `11_SQUEEZE_RESEARCH/`

Investigacion especializada sobre squeezes, low float runners, liquidity
vacuum, trapped shorts, SSR, halts y expansiones intradia.

Debe estar conectada a Event Library, Outcome Research y Strategy Research.

### `90_DISCRETIONARY_FRAMEWORKS/`

Material discrecional, modelos mentales y doctrina humana que todavia no ha
sido mecanizada.

No debe contaminar eventos ni evaluadores como si fuera contrato objetivo.

### `99_EXPERIMENTAL/`

Ideas no promovidas, prototipos conceptuales y notas de investigacion
contenidas.

Nada en esta carpeta es autoridad hasta promocion documentada.

## Criterio para conservar carpetas

Una carpeta de `13_TRADING_SYSTEMS/` solo debe mantenerse si tiene:

- README funcional;
- proposito claro;
- inputs;
- outputs;
- no-goals;
- estado de madurez;
- relacion con `TSIS_LAB_ARCHITECTURE_v3.md`;
- relacion con Graphify si debe entrar en el grafo.

Las carpetas vacias sin README funcional deben eliminarse, fusionarse o
archivarse durante el refactor.

## Relacion con Graphify

El grafo debe seguir el protocolo oficial:

```text
../GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
```

Despues de cambios estructurales en esta carpeta, no basta con Git commit.

Debe actualizarse el slice de Graphify correspondiente mediante el protocolo
oficial. Si el cambio incluye renombres o eliminaciones, no debe fusionarse a
ciegas con el grafo raiz: primero hay que verificar que el root no conserva
nodos de rutas antiguas del mismo slice.

Estado 2026-06-18:

- el leaf event-first de `13_TRADING_SYSTEMS/` ya fue construido y diagnosticado;
- el leaf local esta en
  `../graphify-out/leaf_slices/trading_systems_event_first_20260618/`;
- el root `../graphify-out/graph.json` conserva rutas antiguas de
  `13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/`;
- por tanto, el root no debe declararse actualizado para trading hasta hacer
  un rebuild controlado o un reemplazo oficial de slice.

`graphify-out/` es runtime reconstruible. No es source of truth.

## Siguientes acciones

1. Convertir eventos de `00_private/eventos.md` en definiciones gobernadas
   dentro de `00_EVENT_LIBRARY/`.
2. Definir el contrato conceptual de `event_table` en
   `01_EVENT_ENGINE_MODEL/`.
3. Definir el contrato conceptual de `outcome_table` en
   `02_OUTCOME_RESEARCH/`.
4. Revisar el material existente en `03_STRATEGY_LIBRARY/` y mover piezas si
   alguna pertenece mejor a Edge Hypotheses, Execution Models o Squeeze
   Research.
5. Integrar el leaf Graphify event-first en el root sin conservar rutas
   antiguas.


