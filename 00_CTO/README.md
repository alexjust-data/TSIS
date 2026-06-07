# 00_CTO

`00_CTO/` es la capa de direccion tecnica, gobierno intelectual y memoria estrategica de TSIS.

No es una carpeta de codigo.
No es una carpeta de datasets.
No es una carpeta de outputs runtime.
No es una carpeta para guardar material pesado.

Su funcion es conservar y organizar la parte del proyecto que define:

- como debe evolucionar TSIS;
- que principios tecnicos gobiernan el trabajo;
- que decisiones arquitectonicas se han tomado o se estan evaluando;
- que reglas deben convertirse en documentos canonicos;
- que research conceptual alimenta la direccion del sistema;
- que roadmap, deuda tecnica y prioridades existen fuera del dia a dia de implementacion.

## Autoridad activa

`00_CTO/` contiene memoria, fuentes, borradores, referencias y direccion tecnica.

La autoridad activa del proyecto vive en los documentos raiz y en los contratos locales:

- `PROJECT_OPERATING_SYSTEM.md`
- `PROJECT_RULES.md`
- `AGENTS.md`
- `VERSIONING_STANDARDS.md`
- `RESEARCH_PHILOSOPHY.md`
- `ARCHITECTURE_OVERVIEW.md`
- `01_TSIS_backtest_SmallCaps/LOCAL_RULES.md`
- `01_TSIS_backtest_SmallCaps/AGENTS.md`

Regla:

```text
00_CTO informa y alimenta la autoridad activa.
Los documentos raiz y locales gobiernan la autoridad activa.
```

Si una idea de `00_CTO/` pasa a ser obligatoria, debe promocionarse a uno de los documentos canonicos correspondientes.

## Que no debe ir en 00_CTO

No debe guardarse aqui:

- data raw;
- parquets;
- bases de datos;
- outputs runtime;
- logs;
- caches;
- notebooks exploratorios pesados;
- imagenes pesadas versionadas;
- estrategias privadas;
- notas personales no institucionales;
- material que deba vivir como contrato operativo en `01_foundations/`.

## Carpetas

### `agent_standards/`

Uso:

- material fuente sobre como deben trabajar agentes IA dentro de TSIS;
- criterios de calidad para prompts, tareas, commits, revisiones y seguridad;
- guias extendidas que pueden alimentar `AGENTS.md`;
- material comparativo entre herramientas de agentes.

Autoridad:

- fuente ampliada;
- no debe ser la unica autoridad activa.

La autoridad activa para agentes vive en:

- `AGENTS.md`;
- `PROJECT_RULES.md`;
- `01_TSIS_backtest_SmallCaps/AGENTS.md`;
- reglas locales aplicables.

Si una regla de `agent_standards/` debe ser obligatoria, debe copiarse o sintetizarse en `AGENTS.md` o en el `AGENTS.md` local correspondiente.

Contenido actual:

- `agent_working_standards_TSIS.md`

Estado:

- bien ubicado conceptualmente;
- debe tratarse como documento fuente largo, no como sustituto del contrato activo de agentes.

### `architecture_decisions/`

Uso:

- decisiones arquitectonicas de alto nivel;
- ADRs;
- evaluaciones de alternativas;
- criterios de diseno que afectan a varios modulos;
- decisiones sobre harness, agentes, estructura, pipelines, enforcement, infraestructura o automatizacion.

Un documento aqui debe responder:

- cual era el problema;
- que opciones existian;
- que decision se tomo;
- por que;
- que consecuencias tiene;
- que modulos afecta;
- que queda pendiente.

Autoridad:

- decision tecnica fuente;
- si afecta al comportamiento obligatorio, debe reflejarse tambien en `PROJECT_OPERATING_SYSTEM.md`, `PROJECT_RULES.md`, `VERSIONING_STANDARDS.md`, `AGENTS.md` o contratos locales.

Contenido actual:

- `HARNESS.md`

Estado:

- la carpeta esta bien nombrada;
- `HARNESS.md` actualmente es solo una referencia de enlaces y deberia convertirse en un ADR real si se mantiene aqui.

### `images_Flash_Research/`

Uso:

- referencias visuales, capturas o assets de apoyo para ideas de producto o interfaz;
- material visual no canonico.

Autoridad:

- ninguna autoridad institucional activa.

Politica de Git:

- queda fuera de Git;
- no debe versionarse salvo que una imagen concreta se convierta en asset institucional ligero y se mueva a una ruta gobernada.

Estado:

- carpeta ignorada por `.gitignore`;
- contiene imagenes y duplicados visuales;
- no debe mezclarse con gobernanza documental.

### `philosophy/`

Uso:

- borradores filosoficos;
- notas largas que alimenten la filosofia de investigacion;
- reflexiones estructurales sobre que es TSIS, que no es y que principios deben gobernarlo.

Autoridad:

- fuente o borrador;
- la autoridad activa vive en `RESEARCH_PHILOSOPHY.md` y `PROJECT_RULES.md`.

Regla:

- no duplicar `RESEARCH_PHILOSOPHY.md`;
- usar esta carpeta para material previo, extensiones o notas que todavia no son canonicas.

Estado actual:

- carpeta vacia.

### `project_governance/`

Uso:

- borradores o fuentes sobre gobierno del proyecto;
- ownership;
- jerarquia documental;
- politica de promocion;
- autoridad humana/agente;
- reglas de revision;
- modelo de decisiones;
- estructura de responsabilidades entre modulos.

Autoridad:

- fuente o borrador;
- la autoridad activa vive en `PROJECT_OPERATING_SYSTEM.md`, `PROJECT_RULES.md`, `AGENTS.md` y `VERSIONING_STANDARDS.md`.

Estado actual:

- carpeta vacia.

### `research_principles/`

Uso:

- principios de investigacion derivados de libros, papers, intuiciones tecnicas y experiencia operacional;
- notas conceptuales que informan features, labels, backtesting, ML, RL, microestructura, causalidad y robustez;
- material intelectual previo a convertirse en filosofia canonica, contrato o roadmap.

Autoridad:

- fuente intelectual;
- no es politica activa por si sola.

La autoridad activa vive en:

- `RESEARCH_PHILOSOPHY.md`;
- `PROJECT_RULES.md`;
- contratos de `01_foundations/` cuando la idea se institucionaliza.

Contenido actual:

- `Advances-in-Financial_Machine_Learning.md`
- `Causal_Factor_Investing.md`
- `High-Frequency-Trading.md`
- `ridk-and-asset-allocation.md`

Estado:

- es la ubicacion correcta para estos documentos;
- estos archivos no deben duplicarse en `roadmap/`.

### `roadmap/`

Uso:

- direccion estrategica del proyecto;
- fases;
- hitos;
- prioridades temporales;
- deuda tecnica;
- roadmap por modulo;
- roadmap por trimestre;
- secuenciacion de trabajo;
- dependencias entre bloques.

Autoridad:

- direccion estrategica;
- no sustituye contratos, policies, schemas o documentos canonicos.

Debe contener documentos como:

- `roadmap_master.md`;
- `roadmap_backtesting.md`;
- `roadmap_live_trading.md`;
- `roadmap_offline_rl.md`;
- `milestones.md`;
- `technical_debt.md`.

No debe contener:

- notas completas de libros;
- research principles duplicados;
- outputs;
- imagenes;
- datasets.

Contenido actual:

- `README.md`

Estado:

- los duplicados de `research_principles/` fueron retirados;
- debe usarse solo para direccion, no para biblioteca conceptual.

### `versioning_standards/`

Uso:

- ejemplos, plantillas, notas auxiliares y borradores relacionados con versionado;
- material previo que alimente `VERSIONING_STANDARDS.md`;
- ejemplos de versionado de datasets, modelos, releases, manifests o cambios breaking.

Autoridad:

- fuente auxiliar;
- la autoridad activa vive en `VERSIONING_STANDARDS.md`.

Estado actual:

- carpeta vacia.

## Regla de promocion desde 00_CTO

Una idea en `00_CTO/` puede estar en cuatro estados:

1. `source_note`: nota o referencia.
2. `draft`: borrador estructurado.
3. `candidate_policy`: candidata a regla institucional.
4. `promoted`: ya fue incorporada a un documento canonico.

Cuando una idea pasa a `promoted`, debe quedar reflejada en el documento canonico correspondiente y, si cambia comportamiento operativo, en `CHANGELOG.md`.

## Regla de duplicados

No debe existir el mismo documento conceptual en dos carpetas distintas de `00_CTO/`.

La ubicacion canonica interna es:

- principios de investigacion: `research_principles/`;
- roadmap: `roadmap/`;
- agentes: `agent_standards/`;
- arquitectura: `architecture_decisions/`;
- versionado: `versioning_standards/`;
- gobierno: `project_governance/`;
- filosofia: `philosophy/`.

Si un documento parece pertenecer a dos carpetas, debe vivir en una sola y ser referenciado desde la otra.

## Regla de Git

Debe versionarse:

- markdown institucional;
- ADRs;
- roadmaps;
- notas fuente ligeras;
- plantillas;
- pequenos ejemplos textuales.

No debe versionarse:

- `images_Flash_Research/`;
- imagenes pesadas;
- videos;
- data;
- outputs runtime;
- estrategias privadas;
- notas personales excluidas por `.gitignore`.

## Regla final

`00_CTO/` debe servir para que el proyecto conserve direccion tecnica y memoria intelectual sin contaminar las carpetas operativas.

Si algo gobierna ejecucion real, consumo de datos, backtesting, ML o comportamiento obligatorio de agentes, debe promocionarse fuera de `00_CTO/` hacia la autoridad activa correspondiente.
