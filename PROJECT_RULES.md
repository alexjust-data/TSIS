# TSIS Project Rules

## 0. Regla inicial obligatoria de comunicacion `English`

Si un mensaje del humano empieza por `English`, `ENGLISH` o `english`, con o sin dos puntos inmediatamente despues, antes de pensar, explicar, usar herramientas o responder al contenido, el agente debe traducir al ingles exclusivamente el texto del humano posterior a ese marcador.

La primera linea de la respuesta debe ser:

```text
English: <traduccion al ingles del contenido posterior a ENGLISH>
```

Esta linea debe aparecer antes de cualquier pensamiento visible, explicacion, analisis, accion, herramienta, respuesta tecnica o pregunta de aclaracion.

Despues de esa primera linea, el agente puede continuar respondiendo normalmente al contenido del mensaje en el idioma normal de la conversacion.

Importante: `English` / `ENGLISH` / `english` NO significa que la respuesta del agente deba estar en ingles. Solo obliga a traducir primero la frase del humano.

Si el humano escribe literalmente `English answer`, el agente debe responder en ingles. La respuesta en ingles debe ser la traduccion fiel de la respuesta que habria dado en espanol, manteniendo el mismo contenido, alcance y nivel de detalle.

Esta regla es permanente, transversal y obligatoria para cualquier agente futuro que opere dentro de TSIS.

---

## 1. Rol de este documento

`PROJECT_RULES.md` es el reglamento transversal de conducta técnica e institucional de TSIS.

No es un documento filosófico profundo.
No es un manual de Git.
No es un mapa de arquitectura.
No es un contrato específico para agentes.

Su función es definir qué conducta es obligatoria, aceptable e institucionalmente correcta dentro del proyecto.

Si `RESEARCH_PHILOSOPHY.md` define cómo piensa TSIS, y `PROJECT_OPERATING_SYSTEM.md` define cómo funciona TSIS, este documento define cómo debe trabajarse dentro de TSIS.

---

## 2. Principio rector

TSIS no se gobierna por conveniencia local, velocidad momentánea o resultados visualmente atractivos.

TSIS se gobierna por:

- reproducibilidad;
- claridad semántica;
- disciplina estructural;
- robustez;
- trazabilidad;
- y realismo operativo.

Cuando exista conflicto entre rapidez y rigor, manda el rigor.
Cuando exista conflicto entre comodidad local y coherencia institucional, manda la coherencia institucional.

---

## 3. Prioridades institucionales

Las prioridades transversales de TSIS son estas:

- `reproducibilidad > velocidad`
- `robustez > optimización puntual`
- `claridad > complejidad innecesaria`
- `trazabilidad > conveniencia local`
- `ejecución realista > equity curve bonita`
- `semántica explícita > convenciones implícitas`
- `disciplina institucional > atajos personales`

Estas prioridades deben gobernar decisiones humanas y decisiones de agentes.

---

## 4. Reglas fundamentales del proyecto

### 4.1. Ningún resultado importante puede depender de memoria humana

No se acepta como institucionalmente válido ningún resultado que solo pueda explicarse por:

- memoria verbal;
- contexto de conversación;
- prompts pasados;
- conocimiento tácito no documentado;
- parámetros no versionados.

### 4.2. Ningún módulo define su propia source of truth

La verdad operativa del sistema no puede fragmentarse en verdades locales incompatibles.

Todo módulo debe alinearse con:

- contracts institucionales;
- manifests oficiales;
- versionado lógico de datasets;
- semántica canónica del repositorio.

### 4.3. Ningún output importante vale sin contexto

Un output sin:

- origen;
- config;
- dataset version;
- commit;
- manifest o metadata suficiente;

no debe usarse como evidencia institucional.

### 4.4. Ningún resultado bonito equivale por sí mismo a edge real

Una equity curve atractiva no es una prueba.
Un experimento prometedor no es promoción.
Un notebook convincente no es evidencia institucional suficiente.

---

## 5. Reglas de promoción

Nada debe promocionarse dentro de TSIS solo por entusiasmo, intuición o resultados superficiales.

### 5.1. Nada se considera serio si no puede reconstruirse

Ninguna estrategia, dataset, modelo, simulador o pipeline debe considerarse institucionalmente serio si no puede reconstruirse sin ambigüedad.

### 5.2. Nada promoted sin estructura mínima

Nada debe pasar a estado fuerte sin:

- `manifest`;
- `owner` explícito;
- naming estable;
- validación documentada;
- versionado suficiente;
- y trazabilidad de inputs/outputs.

### 5.3. Nada institutional por default

El estado `institutional` debe ser excepcional y ganado.
Nunca debe ser el estado implícito por defecto de algo nuevo.

---

## 6. Reglas de calidad del trabajo

### 6.1. La claridad es una obligación

Toda pieza importante del sistema debe poder explicarse de forma precisa.
Si algo no puede describirse con claridad, probablemente aún no está suficientemente bien definido.

### 6.2. La semántica manda sobre el nombre técnico

No basta con que algo “funcione”.
Debe significar exactamente lo que dice significar.

Los nombres institucionales son contratos semánticos.
Por tanto, está prohibido sostener entidades ambiguas solo porque el código todavía las tolera.

### 6.3. Las decisiones arquitectónicas deben dejar rastro

Toda decisión arquitectónica relevante debe documentarse.
No debe vivir solo en la cabeza de una persona ni en una conversación puntual.

### 6.4. La deuda técnica debe declararse

La deuda técnica no es una vergüenza.
La deuda técnica invisible sí lo es.

Todo compromiso provisional importante debe quedar documentado como tal.

---

## 7. Reglas de investigación

### 7.1. La ausencia de evidencia no es evidencia de edge

Si una hipótesis no ha sido refutada todavía, eso no la convierte en válida.
Si un setup no ha sido suficientemente degradado, eso no lo convierte en robusto.

### 7.2. La simulación realista tiene prioridad sobre el optimismo

Cuando un conflicto entre un resultado atractivo y una simulación más realista obligue a elegir, manda la simulación más realista.

### 7.3. Ninguna hipótesis debe protegerse del escrutinio

Una hipótesis no merece privilegio por:

- sofisticación técnica;
- intuición fuerte;
- tradición del trader;
- pasado reciente;
- complejidad del modelo.

Toda hipótesis relevante debe poder degradarse, falsarse o ponerse en cuarentena.

### 7.4. La robustez importa más que el máximo local

TSIS no persigue el mejor resultado aislado.
Persigue mecanismos suficientemente sólidos como para sobrevivir a validación, fricción y cambio de régimen.

### 7.5. Justificación científica directa obligatoria

Toda decisión técnica con pretensión institucional debe estar justificada con
evidencia directa, no solo con intuición, conveniencia local o conversación.

Esta regla aplica transversalmente a:

- arquitectura;
- contratos entre capas;
- definición de datasets;
- auditorías de calidad de datos;
- schemas canónicos;
- estados de mercado;
- eventos;
- features;
- modelos ML/RL;
- simuladores;
- execution logic;
- evaluadores;
- funciones de fitness;
- políticas de promoción;
- y outputs consumidos downstream.

Cuando una decisión se apoye en ciencia, research cuantitativo o literatura
técnica, la documentación debe incluir referencias concretas y particulares.

No basta escribir:

```text
esto sigue buenas prácticas
```

Debe quedar claro:

```text
qué decisión toma TSIS
qué evidencia externa o interna la justifica
qué obligación técnica impone esa evidencia
qué limitación o supuesto queda abierto
```

Formato recomendado para decisiones relevantes:

```text
Decision TSIS -> Evidencia directa -> Obligacion tecnica -> Limitacion abierta
```

Si no existe evidencia científica directa suficiente, el componente no debe
presentarse como institucionalmente demostrado. Debe marcarse como:

- `engineering convention`;
- `working hypothesis`;
- `candidate_policy`;
- `provisional`;
- o `exploratory`;

según corresponda.

Esta exigencia no es local de una carpeta ni de una fase.
Aplica con la misma dureza a todos los módulos de TSIS:

- `01_TSIS_backtest_SmallCaps`;
- `02_TSIS_webSocket_SmallCaps`;
- `03_TSIS_Offline_RL`;
- `00_CTO`;
- y cualquier capa futura.

Las reglas locales pueden endurecer este estándar, pero no rebajarlo.

---

## 8. Reglas sobre módulos y capas

### 8.1. Los límites entre capas deben respetarse

Las fronteras entre:

- datos;
- features;
- eventos;
- estados;
- estrategias;
- ejecución;
- reporting;
- ML/RL;

no son decorativas.

Son una protección estructural del sistema.

### 8.2. Ninguna capa debe absorber silenciosamente responsabilidades de otra

Si una capa empieza a redefinir el rol de otra, eso debe ser una decisión explícita, no una deriva informal.

### 8.3. Los contratos compartidos deben tratarse como infraestructura

Todo contrato compartido entre módulos o capas debe considerarse infraestructura institucional y no detalle accidental de implementación.

---

## 9. Reglas de documentación

### 9.1. Documentar no es opcional

Cuando una pieza del sistema cambia su semántica operativa, la documentación relevante debe actualizarse.

### 9.2. La documentación institucional no debe duplicarse sin necesidad

Cada documento raíz debe tener función propia.
No se debe convertir un archivo en duplicado parcial de otro.

### 9.3. Si un conocimiento es importante, debe ser persistente

Todo conocimiento estructural relevante debe vivir en el repositorio de forma:

- versionada;
- trazable;
- legible;
- persistente.

### 9.4. Documentos raiz protegidos

Los documentos de gobernanza raiz son artefactos institucionales protegidos.

Esto aplica como minimo a:

- `AGENTS.md`;
- `PROJECT_OPERATING_SYSTEM.md`;
- `PROJECT_RULES.md`;
- `VERSIONING_STANDARDS.md`;
- `ARCHITECTURE_OVERVIEW.md`;
- `RESEARCH_PHILOSOPHY.md`;
- `CHANGELOG.md`.

Un agente no tiene autorizacion para borrar, reemplazar, reescribir
masivamente, normalizar por estetica o reorganizar el contenido de estos
documentos sin autorizacion explicita del humano.

La regla por defecto para estos documentos es:

```text
edicion aditiva y minima
```

Si se necesita una modificacion no aditiva, el agente debe:

- explicar antes que contenido se propone reemplazar;
- justificar por que no basta una adicion;
- esperar autorizacion explicita;
- preservar trazabilidad del cambio en Git;
- y registrar el impacto si altera semantica institucional.

---

## 10. Reglas para humanos

### 10.1. No existe vía rápida humana por encima del sistema

Ninguna persona está autorizada a degradar la disciplina estructural solo porque entiende el contexto actual del proyecto.

### 10.2. El contexto verbal no sustituye el contrato escrito

Lo que “sabemos” de palabra no sustituye:

- manifests;
- changelogs;
- versionado;
- naming canónico;
- policies institucionales.

### 10.3. La autoridad humana implica más responsabilidad, no menos disciplina

Quien toma decisiones finales dentro del proyecto debe aumentar el nivel de trazabilidad, no relajarlo.

### 10.4. Operaciones largas observables

Toda operación larga ejecutada por humanos, agentes o scripts debe obedecer:

- `LONG_RUNNING_OPERATIONS_CONTRACT.md`

Esto aplica a copias masivas, materializaciones, auditorías, normalizaciones,
reparaciones, builds Graphify, entrenamientos, evaluaciones y cualquier comando
que pueda quedar corriendo sin supervisión directa.

Regla mínima:

```text
pre-manifest al inicio + PID + heartbeat + timestamps + log vivo + monitor separado + final manifest
```

Un comando serio que no permita saber dónde está, qué PID tiene, qué etapa
ejecuta, qué logs actualiza y cómo monitorizarlo no cumple el estándar TSIS.

---

## 11. Reglas para agentes

Los agentes deben tratar este documento como norma de conducta transversal.

Si existe conflicto entre:

- producir rápido;
- dejar trazabilidad;
- respetar semántica institucional;
- mantener separación entre capas;

el agente debe elegir la opción que preserve la estructura del sistema.

Los agentes no deben optimizar localmente a costa del orden global del proyecto.

### 11.1. Regla oficial para builds Graphify

Graphify es una herramienta externa con un pipeline propio. Dentro de TSIS, un
grafo Graphify solo puede llamarse oficial si ha sido producido por el flujo
Graphify real:

- skill Graphify invocado desde el asistente (`$graphify ...` en Codex);
- o CLI oficial `graphify extract ...`;
- o subcomandos oficiales de Graphify para `update`, `cluster-only`, `tree`,
  `merge-graphs` o exports documentados.

Un agente no debe fabricar manualmente `graphify-out/graph.json`,
`GRAPH_REPORT.md` ni `graph.html` mediante scripts propios y presentarlos como
Graphify oficial.

Regla:

```text
Compatible con graphify query no significa oficial Graphify.
```

Si el pipeline oficial falla por permisos, falta de backend LLM, falta de
subagentes, API keys, version de CLI o cualquier otra causa, el agente debe:

1. parar;
2. explicar la causa concreta;
3. no escribir en el path canonico `graphify-out/graph.json`;
4. si conserva un experimento, guardarlo fuera del path canonico con nombre
   `non_official_fallback`;
5. documentar la incidencia en el changelog correspondiente.

El path `graphify-out/graph.json` activa el comportamiento "fast path" de la
skill Graphify. Por tanto, dejar ahi un JSON no oficial es un error operativo:
puede hacer que futuros agentes consulten un mapa que no fue construido por
Graphify.

La ausencia de `graph.html` tambien debe tratarse como senal de revision. Puede
ser valida solo si el build oficial se ejecuto con una opcion documentada que
omite visualizacion, por ejemplo `--no-viz`, y esa decision quedo registrada.

### 11.1.1. Politica Git para `graphify-out` y `leaf_slices`

TSIS distingue entre runtime Graphify y grafo publicable.

Regla:

```text
El runtime raiz de graphify-out no es memoria institucional por defecto.
Los leaf_slices promocionados si pueden ser memoria versionada.
```

Por defecto, Git debe ignorar payloads raiz como:

- `graphify-out/graph.json`;
- `graphify-out/GRAPH_REPORT.md`;
- `graphify-out/graph.html`;
- caches, staging, manifests temporales, sidecars de deteccion/extraccion y
  outputs intermedios.

Un directorio `graphify-out/leaf_slices/<leaf_id>/` puede publicarse en Git
solo si cumple todos estos criterios:

- incluye `BUILD_MANIFEST.md` con baseline Git, corpus, modo de extraccion,
  version de Graphify, version/fuente de la skill y limitaciones;
- incluye `graph.json`, `GRAPH_REPORT.md` y `graph.html`, salvo decision
  oficial documentada como `--no-viz`;
- incluye manifest de corpus o equivalente reconstruible;
- tiene diagnostico limpio o limitaciones explicitas mediante
  `graphify diagnose multigraph --graph <leaf>/graph.json`;
- no contiene raw market data, parquet/feather/duckdb, caches, staging,
  notebooks temporales, imagenes pesadas ni evidencia fisica no gobernada;
- la cola `GRAPHIFY_REFRESH_QUEUE.md`, el changelog y el README/protocolo local
  quedan actualizados cuando cambia scope, semantica o estado de cobertura.

Si el leaf fue construido como topologia deterministica, navegacion,
provenance graph o modo sin cobertura semantica completa, el manifest y el
reporte deben decirlo de forma visible. Un leaf de este tipo puede ser util y
versionable, pero no debe presentarse como extraccion semantica completa de un
corpus documental.

La politica de `.gitignore` debe reflejar exactamente esta distincion:

```text
ignorar graphify-out raiz;
permitir graphify-out/leaf_slices/<leaf_id>/ cuando el leaf este promocionado.
```

### 11.2. Baseline obligatorio para builds Graphify

Todo `BUILD_MANIFEST.md` nuevo o actualizado de Graphify debe dejar un baseline
Git reconstruible. El objetivo es que el siguiente agente pueda calcular el
delta desde el ultimo grafo sin depender de memoria humana ni conversacion.

Campos minimos obligatorios:

- `graph_build_git_branch`;
- `graph_build_git_commit`;
- `graph_build_dirty_state`;
- `graph_build_dirty_paths`;
- `graph_build_untracked_paths`;
- `graph_build_timestamp_utc`;
- `graph_build_command`;
- `graph_build_backend_or_agent_mode`;
- `corpus_manifest_path`;
- `corpus_file_count`;
- `corpus_inclusion_rules`;
- `corpus_exclusion_rules`;
- `queue_entries_covered`;
- `queue_entries_left_pending`;
- `diagnostics_command`;
- `diagnostics_result`;
- `next_delta_commands`.

Si el build se hace con working tree sucio, el manifest debe decirlo
explicitamente y conservar la lista de paths modificados/no trackeados que
formaron parte del baseline. Un build con dirty state puede ser valido, pero no
puede presentarse como si correspondiera solo a un commit limpio.

Los comandos minimos para el siguiente delta deben quedar escritos asi:

```powershell
git diff --name-status <graph_build_git_commit>...HEAD
git status --short
```

Si el manifest anterior no tiene `graph_build_git_commit`, el agente debe
reconstruir el baseline con fecha de build, `GRAPHIFY_REFRESH_QUEUE.md`,
`BUILD_MANIFEST.md` y `git status --short`, y debe registrar esa limitacion en
el nuevo manifest.

### 11.3. Modo Graphify sin APIs y alineacion de version

Fuente directa revisada para esta regla: `safishamsi/graphify`, rama `v8`,
version upstream `graphifyy 0.9.1`, consultada el 2026-06-28.

Regla operativa TSIS:

```text
Graphify no debe bloquearse por falta de API keys.
```

Si no existen `GEMINI_API_KEY` ni `GOOGLE_API_KEY`, un agente no debe pedir
`ANTHROPIC_API_KEY`, `OPENAI_API_KEY` ni otra API externa para completar un
build semantico desde Codex. En el modo TSIS actual, sin APIs externas, el
flujo correcto para corpus con documentos, papers o imagenes es:

- skill Graphify activa;
- extraccion AST local para codigo;
- extraccion semantica con el propio agente/subagentes de Codex;
- cache semantica cuando exista;
- build con `root=<scan_root>` para que `source_file`, manifest y futuros
  updates no deriven entre maquinas o clones.

Un corpus solo de codigo puede usar extraccion AST/code-only sin API y sin
subagentes semanticos.

Regla especifica sobre CLI:

```text
graphify update por CLI no equivale automaticamente a update semantico de
docs/papers/images.
```

Para cambios en contratos, markdown, papers, imagenes o research documental,
un agente debe usar el flujo semantico de la skill Graphify o un
`graphify extract` oficial con backend ya configurado. Si no hay backend API y
el entorno no permite subagentes, el agente debe parar y documentar la causa;
no debe escribir un grafo parcial AST-only como si cubriera el corpus
documental.

Antes de declarar un build como baseline oficial, el agente debe registrar:

- `graphify_package_version`;
- `graphify_skill_version_or_source`;
- `graphify_upstream_reference`;
- `graphify_installed_vs_protocol_status`;
- `no_api_mode`;
- `semantic_extraction_mode`;
- `build_from_json_root_or_equivalent`;
- `semantic_update_coverage`.

Si la version instalada de Graphify es anterior a la version upstream que
gobierna el protocolo vigente, el build no debe presentarse como nuevo
baseline oficial hasta que una de estas condiciones quede documentada:

- Graphify instalado fue actualizado/alineado;
- se ejecuto el flujo oficial desde la version upstream revisada;
- o el build queda marcado explicitamente como `provisional` con limitaciones
  de version.

La cola `GRAPHIFY_REFRESH_QUEUE.md` sigue siendo solo plano de control:
declara cambios semanticos pendientes y scope esperado. No prueba que el grafo
haya sido reconstruido ni sustituye detect, extraction, build, manifest,
diagnostics ni report.

---

## 12. Regla final

TSIS no debe convertirse en:

- una colección de scripts;
- un laboratorio de notebooks desconectados;
- una suma de hallazgos difíciles de reconstruir;
- un repositorio dependiente de personas concretas;
- una arquitectura que solo funciona mientras sus creadores recuerdan cómo opera.

TSIS debe evolucionar como:

- sistema cuantitativo modular;
- infraestructura reproducible;
- laboratorio audit-ready;
- stack compatible con agentes;
- y proyecto capaz de crecer durante años sin colapsar estructuralmente.

Toda regla de este documento existe para defender esa dirección.
