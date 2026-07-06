# 00_CTO Local Rules

Fecha de creacion: 2026-06-18
Estado: regla local obligatoria para agentes que trabajen en `00_CTO`.

## 1. Rol de 00_CTO

`00_CTO/` es la capa de direccion tecnica, arquitectura, memoria intelectual y
diseno de automatizaciones de TSIS.

No es la autoridad operativa final del sistema.

Su funcion es:

- ordenar arquitectura;
- destilar notas privadas;
- disenar Harness, evaluadores y protocolos;
- preservar memoria CTO;
- preparar promociones hacia contratos, policies, validators o documentos raiz.

## 2. Autoridad

La autoridad superior sigue viviendo en:

- `PROJECT_OPERATING_SYSTEM.md`
- `PROJECT_RULES.md`
- `VERSIONING_STANDARDS.md`
- `AGENTS.md`
- `RESEARCH_PHILOSOPHY.md`
- `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`

Si este documento contradice un documento raiz, manda el documento raiz.

## 3. Estados de conocimiento

Todo contenido dentro de `00_CTO/` debe entenderse en uno de estos estados:

- `source_note`: nota privada, conversacion, extracto, prompt o idea cruda.
- `draft`: borrador estructurado, no vinculante.
- `candidate_policy`: casi listo para gobernar una capa.
- `promoted`: incorporado a README, contrato, policy, validator, changelog o
  documento canonico.

Solo `promoted` gobierna trabajo operativo.

## 4. Regla sobre 00_private

`00_private/` es fuente de ideas, no autoridad.

Un archivo en `00_private/` no gobierna TSIS aunque sea correcto.

Para que una idea de `00_private/` gobierne, debe destilarse y promoverse a:

- README;
- `LOCAL_RULES.md`;
- contrato;
- policy;
- validator;
- changelog;
- o documento arquitectonico oficial.

## 5. Arquitectura TSIS Lab

La arquitectura de laboratorio de TSIS debe preservar la separacion:

```text
Data Foundation
-> Event Library
-> Event Engine
-> Outcome Research
-> Strategy Research
-> Pattern Discovery
-> Cluster Research
-> Machine Learning
-> Decision Models
-> Evolution Systems
```

Esta cadena es logica. No implica que cada capa deba vivir como carpeta
top-level dentro de `00_CTO`.

## 6. Data Foundation

`Data Foundation` no se duplica dentro de `00_CTO`.

La fuente operativa de Data Foundation vive en:

```text
01_TSIS_backtest_SmallCaps/01_foundations
```

`00_CTO` puede documentar arquitectura, contratos esperados y operating models,
pero no debe crear una segunda source of truth para schemas, registries,
validators o consumption policies.

## 7. Trading Systems

`13_TRADING_SYSTEMS/` es la capa CTO de conocimiento de dominio de mercado.

Debe ser `event-first`.

Regla central:

```text
Evento != estrategia
```

Un evento responde:

```text
Que esta ocurriendo?
```

Una estrategia responde:

```text
Que hago frente a eso?
```

Los eventos deben definirse antes que estrategias, backtests, ML, RL o
AlphaEvolve.

## 8. Event Library

La Event Library es fuente de verdad conceptual para fenomenos observables de
mercado dentro de `00_CTO`.

Debe contener definiciones que:

- describan fenomenos observables;
- puedan detectarse automaticamente;
- no incluyan entradas;
- no incluyan stops;
- no incluyan targets;
- no incluyan position sizing.

Si contiene entrada, stop, target o sizing, no es evento: es estrategia o
execution model.

## 9. Strategy Library

La Strategy Library contiene respuestas operativas ante eventos.

Puede incluir:

- entrada;
- stop;
- salida;
- gestion parcial;
- sizing;
- variantes;
- failure modes;
- execution notes.

No debe redefinir la semantica de eventos ni de datasets upstream.

## 10. Outcome Research

Outcome Research mide consecuencias del mercado tras eventos.

No evalua decisiones.

No contiene entradas, stops ni targets.

Debe responder:

```text
Que paso despues del evento?
```

## 11. Machine Learning y Decision Models

Machine Learning estima probabilidades.

Decision Models optimizan decisiones.

Regla:

```text
ML predice.
Decision Models deciden.
```

No deben mezclarse labels, features, acciones, rewards y estrategias sin
contrato explicito.

## 12. AlphaEvolve y Evolution Systems

AlphaEvolve no es punto de partida.

Solo puede operar cuando existan:

- datos auditados;
- `event_table`;
- `outcome_table`;
- evaluadores bloqueados;
- fitness functions documentadas;
- constraints;
- lineage;
- validacion OOS o equivalente.

AlphaEvolve puede proponer candidatos, pero no puede modificar evaluadores ni
ampliar datos despues de ver resultados.

## 13. SersanSistemas

`99_REFERENCE_LIBRARY/SersanSistemas` es fuente experta, no doctrina directa.

Solo gobierna TSIS despues de pasar por:

```text
20_SERSAN_DISTILLATION_HARNESS
```

y promocion explicita.

## 14. Graphify

Graphify es mapa semantico, no source of truth.

El protocolo local obligatorio es:

```text
GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
```

Ningun agente debe escribir manualmente:

```text
graphify-out/graph.json
GRAPH_REPORT.md
graph.html
```

y presentarlo como Graphify oficial.

## 15. Graphify Update

Cuando cambie `00_CTO`, el grafo debe actualizarse por slices.

No se debe hacer rebuild monolitico por defecto.

Graphify tampoco debe actualizarse por cada commit. Git es memoria continua;
Graphify es mapa semantico por hitos.

La cola operativa de refrescos vive en:

```text
GRAPHIFY_REFRESH_QUEUE.md
```

Flujo:

```text
identificar cambios
-> clasificar severidad Graphify
-> LOW: no tocar Graphify
-> MEDIUM: anotar en GRAPHIFY_REFRESH_QUEUE.md
-> HIGH/CRITICAL: seguir solo en ventana dedicada o necesidad real de mapa
-> mapear slice
-> actualizar/reconstruir leaf con Graphify oficial
-> decidir si root acepta merge aditivo
-> cluster-only si root cambio
-> diagnose multigraph si root cambio
-> actualizar BUILD_MANIFEST / README / CHANGELOG si aplica
```

Si hubo renombres o eliminaciones de rutas ya indexadas, `merge-graphs` no
debe usarse como reemplazo de slice. El root solo queda actualizado si no
retiene nodos antiguos.

## 16. Reference Library

`99_REFERENCE_LIBRARY/` contiene referencia externa.

No debe gobernar arquitectura, trading, evaluadores ni agentes sin destilacion
y promocion.

## 17. Regla funcional para carpetas

Ninguna carpeta top-level de `00_CTO` debe conservarse solo por inercia.

Cada carpeta que quede activa debe poder explicar:

- proposito funcional;
- inputs;
- outputs esperados;
- no-goals;
- estado de madurez;
- relacion con la arquitectura TSIS Lab;
- y por que no pertenece a otra carpeta.

Si una carpeta no puede responder eso, debe pasar por `CLARIFY`, `MOVE`,
`SPLIT`, `ARCHIVE` o eliminacion gobernada.

## 18. Cambios estructurales

Cambios en estructura, nombres canonicos, event taxonomy, arquitectura de capas,
Harness o reglas Graphify son como minimo `HIGH`.

Deben actualizar:

- README;
- CHANGELOG;
- manifests o build manifests cuando aplique;
- y referencias afectadas.

## 19. No duplicados conceptuales

No mantener el mismo documento conceptual en varias carpetas activas.

Si una idea aparece en `00_private` y luego se promueve, el documento promovido
debe ser la referencia activa.

La copia privada puede conservarse como fuente historica, pero no debe
presentarse como autoridad.

## 20. Reglas de escritura

Antes de escribir en `00_CTO`, un agente debe decidir si el cambio es:

- nota fuente;
- borrador;
- contrato;
- policy;
- arquitectura promovida;
- runtime;
- referencia externa.

La ruta debe reflejar ese estado.

## 21. Changelog

Actualizar `00_CTO/CHANGELOG.md` cuando cambie:

- arquitectura conceptual;
- estructura de carpetas;
- event taxonomy;
- reglas locales;
- protocolo Graphify;
- Harness;
- AlphaEvolve policy;
- relacion con `01_foundations`;
- o promocion de una nota privada a arquitectura oficial.

## 22. Regla final

`00_CTO` existe para impedir que TSIS dependa de memoria humana, conversacion o
intuicion no versionada.

Si una idea importa, debe terminar como:

```text
documento versionado
contrato
policy
validator
manifest
changelog
```

No como recuerdo.

