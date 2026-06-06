# TSIS Versioning Standards

## 1. Naturaleza del documento

`VERSIONING_STANDARDS.md` es una constitución operativa de versionado.

No es un tutorial de Git.
No es una guía informal.
No es una recopilación de buenas prácticas opcionales.

Este documento define cómo evita TSIS degradarse estructuralmente a medida que crece como sistema:

- monorepo;
- multi-módulo;
- multi-stage;
- research + live + RL;
- agent-first;
- reproducible;
- dataset-heavy;
- architecture-driven.

Gobierna los tres módulos:

- `01_TSIS_backtest_SmallCaps`
- `02_TSIS_webSocket_SmallCaps`
- `03_TSIS_Offline_RL`

Su objetivo es impedir:

- pérdida de trazabilidad;
- resultados no reconstruibles;
- datasets ambiguos;
- experimentos imposibles de auditar;
- agentes y humanos introduciendo cambios silenciosos;
- colapso estructural del repositorio a medio plazo.

---

## 2. Principio rector

En TSIS, versionar no significa “guardar cambios”.
Versionar significa preservar la identidad técnica, científica y operativa del sistema.

Todo resultado importante debe poder responder:

- qué código lo produjo;
- qué commit exacto estaba activo;
- qué dataset o datasets lo alimentaron;
- qué versión lógica de esos datasets se usó;
- qué configuración efectiva gobernó el run;
- qué simulador, política de calidad y período aplicaron;
- qué outputs se generaron;
- y bajo qué release o estado institucional debe interpretarse.

Git es memoria estructural.
Los manifests son memoria operativa.
Los changelogs son memoria histórica.
Los releases son memoria institucional.
Los experimentos versionados son memoria científica.

---

## 3. Source of Truth

La fuente oficial de verdad en TSIS queda definida así:

### 3.1. Código y documentación

La fuente oficial es `Git`.

Todo lo que represente lógica, gobernanza, contratos o conocimiento estructural debe vivir en el repositorio y estar versionado.

### 3.2. Datasets, modelos y artefactos grandes

La fuente oficial no es Git directo.
La verdad oficial debe expresarse mediante:

- manifests;
- versionado lógico de datasets;
- rutas canónicas;
- metadata de generación;
- hashes, run ids o sistemas de tracking equivalentes.

### 3.3. Configuración experimental

La fuente oficial son `configs` versionadas y asociadas a run ids, no parámetros recordados “de cabeza”, ni notebooks editados manualmente, ni argumentos irrepetibles lanzados una sola vez.

### 3.4. Estado operativo de cada capa

La fuente oficial es su `manifest.yaml`.

### 3.5. Evolución histórica y semántica

La fuente oficial es `CHANGELOG.md` cuando el cambio tiene relevancia estructural, metodológica o institucional.

### 3.6. Conversaciones y prompts

Las conversaciones no son source of truth.
Pueden ayudar a construir conocimiento, pero no sustituyen documentación, manifests ni versionado formal.

---

## 4. Forbidden Practices

Las siguientes prácticas están prohibidas en TSIS.

### 4.1. Git y ramas

Está prohibido:

- trabajar directamente sobre `main`;
- usar `main` como sandbox;
- hacer commits rápidos en `main`;
- mergear cambios sin semántica clara;
- mezclar múltiples intenciones estructurales en una sola rama caótica.

### 4.2. Datasets y outputs

Está prohibido:

- sobrescribir outputs importantes sin versionar;
- modificar datasets silenciosamente;
- cambiar reglas de construcción de un dataset sin emitir nueva versión lógica;
- usar el mismo nombre para datasets semánticamente distintos;
- borrar evidencia relevante de experimentos fallidos para “limpiar” el árbol.

### 4.3. Notebooks

Está prohibido:

- usar notebooks como única fuente de lógica productiva;
- dejar lógica crítica solo en celdas sin migrarla a `src/`, `pipelines/`, `validators/` o `scripts/` cuando pase a ser estable;
- tratar un notebook como contrato operativo institucional.

### 4.4. Commits y trazabilidad

Está prohibido:

- hacer commits gigantes sin unidad lógica;
- usar mensajes genéricos tipo `update`, `misc`, `fix stuff`, `changes`;
- cambiar configs críticas sin trazabilidad;
- tocar manifests o changelogs solo parcialmente cuando el cambio sí altera la semántica operativa.

### 4.5. Archivos pesados

Está prohibido:

- guardar parquets enormes en Git;
- commitear modelos pesados en Git salvo decisión excepcional explícita;
- mezclar outputs voluminosos y memoria estructural en el mismo flujo de versionado.

---

## 5. Estados de promoción institucional

Todo componente relevante de TSIS debe tener un estado de madurez explícito.

Estados oficiales:

- `exploratory`
- `provisional`
- `validated`
- `institutional`
- `deprecated`
- `archived`

### 5.1. Significado

- `exploratory`: investigación inicial, hipótesis aún abiertas, semántica no congelada.
- `provisional`: ya existe estructura reproducible mínima, pero aún no está lista para depender de ella downstream.
- `validated`: pasó validaciones suficientes para su nivel de ambición y tiene semántica estable local.
- `institutional`: forma parte del stack oficial de TSIS y puede ser usada como referencia interna.
- `deprecated`: sigue existiendo, pero no debe usarse para nuevo desarrollo salvo necesidad explícita.
- `archived`: se conserva solo por memoria histórica, auditabilidad o falsificación.

### 5.2. Aplicación obligatoria

Estos estados deben aparecer, cuando aplique, en:

- manifests de capas;
- manifests de datasets;
- manifests o metadata de modelos;
- reports de promoción;
- documentación de componentes clave.

---

## 6. Ownership Governance

Todo componente institucional debe tener ownership explícito.

### 6.1. Todo componente relevante debe tener

- `owner` principal;
- módulo responsable;
- política de promoción;
- política de deprecación;
- y, cuando aplique, política de archivado.

### 6.2. Ámbito

Esto aplica como mínimo a:

- datasets institucionales;
- schemas canónicos;
- simuladores;
- universos;
- pipelines oficiales;
- políticas de calidad;
- modelos promovidos.

### 6.3. Regla

Un componente sin owner explícito no debe promocionarse a `institutional`.

---

## 7. Severidad operativa del cambio

No todos los cambios tienen el mismo peso estructural.

TSIS clasifica la severidad de los cambios en:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

### 7.1. LOW

Cambios como:

- docs menores;
- comentarios;
- limpieza visual o textual;
- mejoras no semánticas de readability.

### 7.2. MEDIUM

Cambios como:

- validadores compatibles;
- configs compatibles;
- nuevas features sin romper contratos;
- mejoras de performance sin alterar semántica.

### 7.3. HIGH

Cambios como:

- schemas canónicos;
- ontología de eventos;
- semántica del simulador;
- lógica de ejecución;
- semántica de outputs consumidos downstream.

### 7.4. CRITICAL

Cambios como:

- source of truth;
- definición del universo;
- semántica oficial de datasets;
- cambios en reward RL institucional;
- redefinición de contratos entre módulos;
- políticas de calidad centrales.

### 7.5. Regla de enforcement

Cuanto mayor sea la severidad, mayor debe ser la disciplina de:

- version bump;
- manifest update;
- migration note;
- changelog explícito;
- revisión downstream.

---

## 8. Unidad lógica de cambio

### 8.1. Definición

Una unidad lógica de cambio es el bloque mínimo de modificación que puede explicarse, auditarse y revertirse sin ambigüedad.

Debe tener una sola intención dominante.

### 8.2. Ejemplos válidos

Son unidades lógicas válidas:

- creación de una nueva capa;
- corrección puntual de un bug;
- formalización de un nuevo contrato entre módulos;
- introducción de una feature específica;
- incorporación de una política de calidad;
- refactor de una pieza concreta sin mezclarlo con features nuevas;
- nuevo baseline de estrategia;
- nuevo validador;
- nuevo dataset lógico derivado.

### 8.3. Ejemplos inválidos

No es una unidad lógica válida mezclar en un solo cambio:

- refactor + feature + docs + outputs;
- nueva estrategia + cambio de arquitectura + fix de datos;
- experimento exploratorio + promoción institucional;
- cambio de schema + ajuste visual + update de changelog sin explicar semántica.

El principio es simple:
si no puede describirse en una frase precisa, el cambio está demasiado mezclado.

---

## 9. Qué se versiona y qué no

### 9.1. Debe versionarse en Git

Debe vivir en Git todo lo que represente memoria estructural o reproducible:

- código fuente;
- scripts;
- configuraciones;
- documentación;
- manifests;
- changelogs;
- contratos entre capas;
- tests;
- definiciones de estrategias;
- definiciones de eventos;
- validadores;
- plantillas;
- reglas locales;
- documentación arquitectónica y metodológica.

### 9.2. No debe versionarse en Git

No debe vivir en Git, salvo excepción muy justificada:

- datasets históricos grandes;
- parquets pesados;
- modelos pesados;
- stores intermedios voluminosos;
- caches masivas;
- logs grandes;
- exports reconstruibles;
- artefactos de runtime efímeros.

Eso debe vivir fuera de Git y quedar referenciado por:

- nombre canónico;
- versión lógica;
- manifest;
- run id;
- hash o tracking externo equivalente.

---

## 10. Runtime vs Institutional Artifacts

Los artefactos de runtime no son artefactos institucionales.

### 10.1. Runtime artifacts

Los artefactos runtime:

- no son source of truth;
- no son evidencia institucional final;
- pueden eliminarse;
- no deben confundirse con outputs promocionados.

Ejemplos típicos:

- caches temporales;
- estados efímeros de procesos;
- logs transitorios;
- outputs intermedios no promocionados;
- archivos de runtime local.

### 10.2. Institutional artifacts

Los artefactos institucionales:

- tienen identidad lógica;
- tienen manifest o metadata suficiente;
- tienen owner;
- tienen semántica explícita;
- y pueden ser referenciados como verdad operativa o evidencia.

---

## 11. Git Policy

### 11.1. Rama `main`

`main` representa el estado estable, legible y reproducible del sistema.

`main` no es área de desarrollo rápido.
`main` no es una rama personal.
`main` no es memoria de trabajo provisional.

### 11.2. Branching model oficial

Solo se permiten ramas con intención explícita:

- `feature/*`
- `fix/*`
- `research/*`
- `experiment/*`
- `refactor/*`
- `docs/*`
- `release/*`

Ejemplos correctos:

- `feature/03-universe-builder-v01`
- `feature/05-event-engine-contracts`
- `fix/quotes-timestamp-ordering`
- `research/gapgo-baseline`
- `experiment/meta-labeling-v03`
- `refactor/split-execution-validator`
- `docs/rewrite-versioning-standards`
- `release/v0.7.0`

### 11.3. Commits

Formato obligatorio de commits:

- `feat:`
- `fix:`
- `docs:`
- `refactor:`
- `test:`
- `perf:`
- `research:`
- `chore:`

Ejemplos correctos:

- `feat: add logical dataset manifest for quotes current merged`
- `fix: repair universe builder date window comparison`
- `research: add gap and go triple barrier baseline`
- `docs: formalize source of truth policy`

Mensajes prohibidos:

- `update`
- `misc`
- `wip`
- `changes`
- `fix stuff`

### 11.4. Pull Requests

Todo cambio destinado a memoria institucional debe pasar por PR, aunque el repositorio tenga un único operador humano en determinados momentos.

El PR actúa como auditoría mínima de:

- intención;
- impacto;
- trazabilidad;
- validación;
- semántica del cambio.

### 11.5. Merge policy

No se mergea algo solo porque “funciona localmente”.
Se mergea cuando el cambio es:

- legible;
- trazable;
- reconstruible;
- coherente con manifests, configs y documentación.

### 11.6. Tags y releases

Los tags oficiales marcan estados institucionales del sistema.
No deben crearse tags triviales o ruidosos.

Se permite taggear:

- milestones arquitectónicos;
- releases reproducibles;
- puntos de promoción institucional;
- estados estables de módulos mayores.

---

## 12. Semantic Versioning

### 12.1. Regla oficial

TSIS usa `Semantic Versioning`:

`MAJOR.MINOR.PATCH`

### 12.2. Significado

- `MAJOR`: cambio incompatible o redefinición estructural importante.
- `MINOR`: nueva capacidad compatible.
- `PATCH`: fix o mejora acotada sin cambio conceptual grande.

### 12.3. Fase pre-1.0

Mientras el sistema siga en construcción, la mayoría de releases estarán en `0.x.y`.

Eso significa:

- arquitectura todavía evolutiva;
- contratos aún no totalmente congelados;
- estabilidad creciente, pero no definitiva.

### 12.4. Cuándo subir cada número

Subir `PATCH` cuando cambian:

- bugs;
- validadores;
- manifests sin cambio de semántica profunda;
- detalles operativos compatibles.

Subir `MINOR` cuando aparece:

- una nueva capacidad;
- una nueva capa;
- un nuevo pipeline estable;
- una metodología institucionalizada.

Subir `MAJOR` cuando cambia:

- el contrato entre módulos;
- el schema canónico incompatible;
- la ontología de una capa;
- la semántica de un dataset lógico de forma incompatible;
- la política operativa central del proyecto.

---

## 13. Canonical Naming Authority

Los nombres institucionales son contratos semánticos.

Está prohibido:

- naming ambiguo;
- abreviaciones inconsistentes;
- aliases silenciosos;
- reutilizar nombres para entidades incompatibles;
- introducir variantes semánticas sin bump de versión o sin nueva identidad.

### 13.1. Regla

Si dos entidades no significan lo mismo, no deben compartir nombre.
Si una entidad cambia de semántica, no debe seguir llamándose exactamente igual sin nueva versión o renombrado explícito.

---

## 14. Dataset Versioning Policy

### 14.1. Regla central

El principal riesgo de trazabilidad en TSIS no será el código.
Será no poder responder:

“¿qué dataset produjo este resultado?”

Por eso el versionado de datasets es obligatorio y formal.

### 14.2. Principio

Los datasets se versionan lógicamente, no solo físicamente.

Un dataset lógico debe tener:

- nombre canónico;
- versión;
- scope;
- fuente o fuentes;
- política de calidad;
- política de construcción;
- commit o pipeline que lo generó;
- fecha de generación;
- evidencia asociada.

### 14.3. Convención de nombres

Formato recomendado:

`{dataset_name}_v{major}.{minor}.{patch}`

o, cuando el scope sea parte crítica de la identidad:

`{dataset_name}_{scope}_v{major}.{minor}.{patch}`

Ejemplos:

- `master_daily_table_v0.4.2.parquet`
- `event_dataset_gapgo_v0.3.1.parquet`
- `quotes_cleaned_v0.2.0.parquet`
- `market_cap_cutoff_lt_1b_active_inactive_v1.0.0.parquet`
- `ohlcv_1m_current_full_fullscope_v0.3.0.parquet`

### 14.4. Manifest mínimo de dataset

Todo dataset lógico importante debe tener metadata equivalente a:

```yaml
dataset: master_daily_table
version: 0.4.2
scope: lt1b
source:
  - polygon_ohlcv_1m
  - polygon_daily
  - reference_layer_v0.2.1
quality_policy:
  - daily_quality_policy_v03
generated_by:
  pipeline: feature_engine_v0.4.2
  commit: 8f34ab2
generated_at: 2026-05-18
```

### 14.5. Qué obliga a bump de versión de dataset

Debe emitirse nueva versión lógica de dataset si cambia cualquiera de estos elementos:

- universo fuente;
- reglas de inclusión o exclusión;
- merges entre roots o sources;
- schema final materializado;
- política de calidad;
- semántica del output;
- transformación estructural del contenido.

Está prohibido sobrescribir un dataset semánticamente nuevo bajo el mismo nombre antiguo.

---

## 15. Cross-Module Compatibility

TSIS es multi-módulo.
Por tanto, los contratos compartidos entre módulos deben gobernarse explícitamente.

Todo contrato compartido entre módulos debe:

- tener schema explícito;
- tener versionado;
- documentar breaking changes;
- documentar compatibilidad mínima requerida.

Esto es especialmente crítico entre:

- `01_TSIS_backtest_SmallCaps`
- `02_TSIS_webSocket_SmallCaps`
- `03_TSIS_Offline_RL`

La compatibilidad cross-module no puede depender de suposiciones implícitas.

---

## 16. Schema Governance

Todo schema canónico debe tener gobierno explícito.

### 16.1. Obligaciones mínimas

Todo schema canónico debe:

- tener `owner`;
- tener versión;
- tener changelog cuando cambie de forma relevante;
- documentar columnas y semántica;
- documentar breaking changes;
- documentar impacto downstream cuando aplique.

### 16.2. Áreas críticas

Esto es especialmente importante en:

- `event_engine`
- datasets para RL
- execution logs
- master tables
- outputs institucionales de backtesting

### 16.3. Regla

Cambiar un schema canónico sin gobierno explícito es una violación estructural.

---

## 17. Research Versioning Policy

### 17.1. Regla central

El research cambia constantemente.
Precisamente por eso debe versionarse con dureza.

### 17.2. Todo experimento relevante debe tener

- `experiment_id`
- `run_id`
- config efectiva
- dataset version exacta
- commit hash
- período analizado
- outputs
- estado final

### 17.3. Convención recomendada

Formato sugerido:

`{date}_{module}_{purpose}_{version}`

Ejemplos:

- `20260518_gapgo_triple_barrier_baseline_v01`
- `20260518_quotes_soft_crossed_review_v02`
- `20260518_short_flow_context_study_v01`

### 17.4. Experimental containment

Los experimentos exploratorios NO deben contaminar:

- contratos oficiales;
- schemas canónicos;
- datasets institucionales;
- releases estables;
- pipelines de producción.

La exploración debe estar aislada por naming, rutas, manifests y estado de promoción.

### 17.5. Research inválido institucionalmente

Un experimento no debe considerarse institucionalmente válido si no puede responder:

- qué dataset usó;
- qué config exacta usó;
- qué commit lo produjo;
- qué outputs se derivaron;
- y cómo se clasifica su resultado: exploratorio, falsado, promocionable o descartado.

---

## 18. Model Versioning Policy

### 18.1. Regla central

Todo modelo entrenado relevante debe tener identidad persistente.

Esto es especialmente crítico para `03_TSIS_Offline_RL`, pero aplica también a clasificadores, meta-labelers y modelos auxiliares del módulo de backtesting.

### 18.2. Convención de nombres

Ejemplos recomendados:

- `model_gapgo_meta_v0.3.0`
- `policy_rl_v0.1.2`
- `behavioral_clone_v0.2.1`

### 18.3. Un modelo no existe institucionalmente si no está ligado a

- dataset exacto;
- versión de dataset exacta;
- config de entrenamiento exacta;
- commit exacto;
- training window exacta;
- validación exacta;
- política de promoción exacta.

### 18.4. Cambios que exigen nueva versión de modelo

- nuevo dataset;
- nueva ventana de entrenamiento;
- nueva arquitectura;
- nueva loss o reward;
- cambio de labeling;
- cambio relevante de hyperparameters;
- cambio de política de evaluación.

---

## 19. Principio histórico inmutable

Los artefactos históricos institucionales no deben reescribirse silenciosamente.

Esto incluye:

- datasets versionados;
- manifests históricos;
- metadata de experimentos;
- reports released;
- releases institucionales;
- resultados promocionados como evidencia oficial.

Si un artefacto histórico requiere corrección, la corrección debe generar:

- nueva versión;
- nota de migración si procede;
- corrective changelog;
- y explicitación del impacto.

La historia institucional se corrige por capas, no se borra silenciosamente.

---

## 20. Breaking Changes Policy

### 20.1. Definición

Un breaking change es cualquier cambio incompatible que altere el contrato descendente de una capa, dataset, schema, config o pipeline.

### 20.2. Ejemplos de breaking change

- cambio de schema en outputs canónicos;
- cambio incompatible en naming de columnas;
- cambio de semántica de un dataset lógico;
- redefinición del universo;
- cambio incompatible en manifest contract;
- cambio de política de calidad que altere el significado downstream.

### 20.3. Obligaciones ante un breaking change

Todo breaking change debe:

- incrementar versión adecuadamente;
- actualizar manifests;
- actualizar changelogs;
- documentar impacto downstream;
- dejar notas de migración cuando haga falta;
- evitar introducir incompatibilidad silenciosa.

Un breaking change oculto es una violación grave de este estándar.

---

## 21. Deprecation Policy

Un componente `deprecated`:

- no debe usarse para nuevo desarrollo;
- debe mantener metadata histórica suficiente;
- debe documentar reemplazo recomendado si existe;
- no debe eliminarse silenciosamente.

Deprecar no significa borrar.
Significa declarar que la entidad sigue existiendo, pero ha dejado de ser la opción correcta para nueva dependencia.

---

## 22. Archival Policy

Los componentes `archived`:

- se conservan por auditabilidad;
- quedan congelados;
- no reciben desarrollo nuevo;
- mantienen reproducibilidad histórica mínima razonable.

Archivar es una decisión institucional, no una limpieza accidental del árbol.

---

## 23. Failed Experiments Policy

### 23.1. Regla central

Los experimentos fallidos no se borran como si no hubieran existido.

### 23.2. Valor institucional del fallo

Los experimentos fallidos son valiosos para:

- falsificación;
- auditabilidad científica;
- evitar repetir errores;
- entender límites de hipótesis;
- conservar contexto histórico del proyecto.

### 23.3. Qué no significa conservar fallos

No significa ensuciar `main` con basura sin clasificar.
Significa:

- registrar el experimento;
- marcar su estado;
- conservar su metadata;
- archivar outputs o referencias relevantes;
- evitar que el conocimiento desaparezca.

---

## 24. Notebook Policy

### 24.1. Regla central

Los notebooks son exploratorios.
No son la autoridad productiva final del sistema.

### 24.2. Qué sí pueden hacer

- exploración;
- diseño metodológico;
- inspección visual;
- drilldown forense;
- prototipado inicial.

### 24.3. Qué no deben hacer como estado final

No deben ser la única sede de:

- lógica productiva;
- contratos operativos;
- validadores oficiales;
- política de ejecución;
- definición canónica de datasets;
- lógica institucional crítica.

### 24.4. Regla de migración

Cuando una lógica explorada en notebook se vuelve estable, debe migrarse a:

- `src/`
- `pipelines/`
- `validators/`
- `scripts/`
- `configs/`

según corresponda.

---

## 25. Institutional Reproducibility

TSIS distingue entre:

- algo reproducible en sentido débil;
- y algo institucionalmente reproducible.

Un resultado solo se considera institucionalmente reproducible si:

- puede reconstruirse sin memoria humana;
- no depende de prompts desaparecidos;
- no depende de notebooks efímeros;
- no depende de paths locales ambiguos;
- no depende de parámetros no versionados;
- no depende de convenciones solo conocidas por un operador;
- y deja suficiente evidencia para ser repetido por otra persona o agente.

---

## 26. Auditability Principle

Todo cambio relevante debe dejar evidencia suficiente para:

- reconstruir intención;
- reconstruir inputs;
- reconstruir outputs;
- reconstruir impacto downstream.

Si el cambio no deja rastro suficiente para auditoría técnica posterior, el cambio no cumple estándar institucional.

---

## 27. Promotion Barrier

Nada se considera institucional hasta que supere una barrera mínima de promoción.

Un componente no debe promocionarse a `institutional` hasta que:

- tenga manifest;
- tenga changelog cuando corresponda;
- tenga reproducibilidad mínima suficiente;
- tenga config versionada;
- tenga validación documentada;
- tenga owner claro;
- tenga naming estable y semántica explícita.

La promoción institucional no se obtiene por entusiasmo ni por un buen resultado aislado.
Se obtiene por disciplina estructural.

---

## 28. Institutional Promotion Review

La promoción a `institutional` implica una revisión mínima equivalente a un comité de promoción, aunque el proyecto tenga un único operador humano.

Esa revisión debe cubrir:

- reproducibilidad;
- naming;
- manifests;
- impacto downstream;
- coherencia epistemológica mínima;
- y compatibilidad con contratos vigentes.

El concepto importante no es el número de revisores.
Es la disciplina mental de no promocionar algo sin pasar una barrera explícita.

---

## 29. Enforcement Philosophy

Las políticas de TSIS no deben quedarse solo en texto.
Deben evolucionar hacia enforcement automático siempre que sea viable.

La dirección correcta incluye:

- CI checks;
- validators;
- schema verification;
- naming validators;
- manifest consistency checks;
- release gates.

La filosofía es simple:

cuanto más importante sea una regla, menos debe depender solo de memoria o buena voluntad.

---

## 30. Release Policy

### 30.1. Qué representa una release estable

Una release estable representa:

- un estado reproducible;
- una arquitectura validada para ese nivel de madurez;
- outputs documentados;
- configs sincronizadas;
- manifests coherentes;
- y trazabilidad suficiente para reconstrucción.

### 30.2. Qué no debe llamarse release

No debe llamarse release a:

- un experimento local prometedor;
- un branch a medio terminar;
- un notebook interesante;
- una corrida con resultados bonitos pero no auditados.

### 30.3. Hitos arquitectónicos

TSIS puede usar releases como hitos arquitectónicos, por ejemplo:

- `v0.3.0`: universe builder stable
- `v0.5.0`: event engine formalized
- `v0.7.0`: execution simulator realistic
- `v0.9.0`: first walk-forward institutional stack
- `v1.0.0`: first reproducible institutional TSIS core

---

## 31. Technical Debt Policy

### 31.1. Regla central

TSIS asume que el research genera deuda técnica de forma natural.
La deuda técnica no debe negarse ni esconderse.
Debe declararse.

### 31.2. Política

Toda deuda técnica relevante debe documentarse en:

`00_CTO/technical_debt/`

### 31.3. Qué debe registrarse como deuda

- hacks temporales;
- validadores incompletos;
- migraciones pendientes de notebooks a código estable;
- contratos todavía frágiles;
- dependencias provisionales;
- schemas pendientes de consolidación;
- capas con semántica aún no congelada.

La deuda documentada es aceptable.
La deuda invisible no lo es.

---

## 32. Agent Requirements

Los agentes deben cumplir explícitamente este estándar.

Los agentes MUST:

- crear ramas antes de modificar estructura relevante;
- mantener commits semánticos y pequeños;
- actualizar changelogs cuando el cambio lo requiera;
- actualizar manifests cuando cambie el estado operativo;
- preservar semantic versioning;
- evitar cambios estructurales silenciosos;
- no sobrescribir outputs importantes sin version bump o nueva identidad lógica;
- documentar breaking changes;
- no tratar conversaciones como memoria persistente del sistema.

Los agentes MUST NOT:

- asumir reglas no escritas;
- esconder decisiones importantes en prompts;
- improvisar naming de datasets incompatibles con el estándar;
- borrar evidencia relevante de experimentos fallidos;
- promover lógica de notebook a institucional sin migración adecuada.

---

## 33. Human Requirements

Los humanos operan bajo la misma disciplina estructural que los agentes.

No existe una vía rápida humana que justifique:

- trabajar en `main` directamente;
- saltarse manifests;
- saltarse versionado lógico de datasets;
- cambiar semánticas sin changelog;
- sostener resultados importantes solo con memoria verbal.

La autoridad final humana existe, pero no debe ejercerse contra la trazabilidad del sistema.

---

## 34. Regla final

`VERSIONING_STANDARDS.md` existe para garantizar que TSIS pueda crecer durante años sin perder identidad, trazabilidad ni reproducibilidad.

Nunca debe quedar conocimiento estructural importante:

- solo en conversaciones;
- solo en prompts;
- solo en notebooks temporales;
- solo en memoria humana;
- solo en outputs sin contexto.

Todo conocimiento importante del sistema debe vivir:

- dentro del repositorio;
- versionado;
- documentado;
- trazable;
- legible por agentes;
- y reconstruible por humanos.

Ese es el estándar de versionado de TSIS.
