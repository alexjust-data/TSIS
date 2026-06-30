# Graphify Official Build Protocol for 00_CTO

Fecha: 2026-06-18
Estado: regla operativa local para agentes.

## Proposito

Este documento existe para evitar que otro agente confunda un grafo compatible
con Graphify con un grafo producido oficialmente por Graphify.

`00_CTO` puede usar Graphify como mapa semantico de navegacion, pero el grafo
solo se considera valido si fue generado por el pipeline oficial de Graphify.

## Regla corta

```text
No escribas manualmente 00_CTO/graphify-out/graph.json.
Si no lo genero Graphify, no es Graphify oficial.
```

## Que cuenta como build oficial

Un build oficial de Graphify debe venir de uno de estos flujos:

- `$graphify .` desde Codex, con la skill Graphify activa;
- `graphify extract <scope>` usando el CLI oficial;
- `graphify update`, `graphify cluster-only`, `graphify merge-graphs` o exports
  oficiales sobre un grafo ya generado por Graphify.

El build oficial esperado genera, salvo decision documentada:

```text
graphify-out/
├── graph.html
├── GRAPH_REPORT.md
└── graph.json
```

Si se omite HTML por `--no-viz` u otra opcion oficial, esa decision debe quedar
registrada en el changelog o manifest del build.

## Modo sin APIs y version de Graphify

Fuente directa de esta regla: `https://github.com/safishamsi/graphify`, rama
`v8`, version upstream `graphifyy 0.9.1`, revisada el 2026-06-28.

Estado observado en esta maquina el 2026-06-28:

```text
graphifyy instalado: 0.8.40
upstream revisado:   0.9.1
```

Por tanto, antes de cualquier nuevo build oficial de `00_CTO`, el agente debe
comprobar y registrar la version efectiva de Graphify y de la skill usada. Si
la version instalada sigue por detras del protocolo upstream revisado, el build
solo puede declararse baseline oficial si se documenta una de estas opciones:

- Graphify instalado fue actualizado/alineado;
- se ejecuto el flujo oficial desde la version upstream revisada;
- o el build queda marcado como `provisional` por limitacion de version.

TSIS opera por defecto sin APIs externas para Graphify. La ausencia de
`GEMINI_API_KEY` o `GOOGLE_API_KEY` no autoriza a pedir `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY` ni otro proveedor. Para documentos, papers o imagenes, el modo
correcto en Codex es:

```text
skill Graphify -> AST local para codigo -> subagentes/host agent para
extraccion semantica -> build oficial -> diagnostics -> manifest.
```

Un corpus solo de codigo puede usar el flujo AST/code-only sin API y sin
subagentes semanticos.

Regla critica:

```text
graphify update por CLI es suficiente solo para cambios code/AST cuando ese
scope lo permita. No prueba cobertura semantica de markdown, contracts, papers
o imagenes.
```

Para cambios documentales de `00_CTO`, usar el flujo semantico de la skill
Graphify o `graphify extract` con backend ya configurado. Si no hay backend ni
subagentes disponibles, el agente debe parar, documentar la causa y no escribir
un grafo parcial en `graphify-out/`.

## Divergencia TSIS respecto al workflow de equipo de Graphify

Graphify upstream recomienda normalmente compartir `graphify-out/` con el
equipo para que todos empiecen con el mismo mapa.

TSIS puede decidir algo distinto por gobierno institucional: tratar
`graphify-out/` como runtime reconstruible salvo promocion explicita.

Esa divergencia es aceptable solo en la politica de versionado/commit del
artefacto. No autoriza a cambiar el modo de generacion.

Regla:

```text
TSIS puede gobernar si se versiona graphify-out/.
TSIS no puede llamar Graphify oficial a algo que Graphify no genero.
```

Politica Git local:

```text
00_CTO/graphify-out/ raiz sigue siendo runtime reconstruible.
00_CTO/graphify-out/leaf_slices/<leaf_id>/ puede publicarse en Git si fue
promocionado con BUILD_MANIFEST.md, corpus reconstruible, graph.json,
GRAPH_REPORT.md, graph.html y diagnostico limpio.
```

Un leaf topologico, de navegacion o de provenance debe declarar esa limitacion
en `BUILD_MANIFEST.md` y `GRAPH_REPORT.md`. No puede presentarse como
extraccion semantica completa si no hubo cobertura semantica completa.

## Que no cuenta como build oficial

No cuenta como oficial:

- crear `graph.json` a mano con PowerShell, Python u otro script propio;
- generar nodos y edges curados manualmente;
- construir un JSON que solo sea legible por `graphify query`;
- usar `graphify explain` o `graphify path` como prueba suficiente de origen;
- presentar un fallback compatible como si fuera salida de Graphify.

Regla:

```text
Formato compatible no prueba procedencia.
```

## Por que ocurrio el fallo de 2026-06-18

Durante el intento inicial de construir el grafo de `00_CTO`, el agente mezclo
dos objetivos distintos:

1. cumplir la politica TSIS de separar scope operativo, subgrafos y runtime;
2. entregar rapidamente `graph.json` y `GRAPH_REPORT.md`.

Al fallar el camino oficial por una combinacion de:

- ausencia de un backend LLM/API key utilizable para `graphify extract`;
- confusion entre flujo de skill Graphify y flujo CLI headless;
- problemas de escritura desde Python en `graphify-out`;
- presion por no perder la extraccion semantica;

el agente genero un fallback manual compatible con el formato de Graphify.

Ese fallback fue un error porque uso los nombres canonicos:

```text
00_CTO/graphify-out/graph.json
00_CTO/graphify-out/GRAPH_REPORT.md
```

Eso podia activar el fast path de Graphify y hacer creer a futuros agentes que
existia un grafo oficial.

## Correccion aplicada

El fallback no oficial fue retirado del path canonico y movido a cuarentena:

```text
C:\tmp\graphify_00_cto\non_official_fallback_2026-06-18
```

Tambien se retiro el mirror temporal que habia quedado en:

```text
C:\tmp\graphify_00_cto\phase1_outputs
```

Mientras no exista un build oficial, este path no debe existir:

```text
00_CTO/graphify-out/graph.json
```

## Procedimiento correcto para el proximo intento

Desde Codex:

```powershell
cd C:\TSIS_Data\00_CTO
$graphify .
```

Si se ejecuta headless:

```powershell
graphify extract C:\TSIS_Data\00_CTO\<scope> --out C:\tmp\graphify_00_cto\<build_id>
```

El agente debe parar si:

- Graphify pide backend LLM y no existe backend disponible;
- la skill no puede lanzar subagentes;
- mas de la mitad de chunks fallan;
- no se genera `GRAPH_REPORT.md`;
- no se genera `graph.json`;
- no se genera `graph.html` y no hubo `--no-viz` documentado;
- el output procede de un script manual.

## Criterios minimos de aceptacion

Antes de declarar exito, el agente debe comprobar:

```powershell
Test-Path .\graphify-out\graph.json
Test-Path .\graphify-out\GRAPH_REPORT.md
Test-Path .\graphify-out\graph.html
graphify diagnose multigraph --graph .\graphify-out\graph.json
graphify explain "<nodo canonico>" --graph .\graphify-out\graph.json
```

Si el output es un leaf, la comprobacion equivalente debe apuntar a:

```powershell
Test-Path .\graphify-out\leaf_slices\<leaf_id>\graph.json
Test-Path .\graphify-out\leaf_slices\<leaf_id>\GRAPH_REPORT.md
Test-Path .\graphify-out\leaf_slices\<leaf_id>\graph.html
graphify diagnose multigraph --graph .\graphify-out\leaf_slices\<leaf_id>\graph.json
```

Si `graph.html` falta por decision oficial, debe indicarse el flag usado.

## Protocolo de actualizacion incremental

El grafo raiz de `00_CTO` es un grafo fusionado. No debe actualizarse como un
escaneo monolitico de todo `00_CTO` cuando el cambio pertenece a un slice
concreto.

Regla:

```text
Primero se actualiza el subgrafo leaf afectado.
Despues se fusiona oficialmente contra el grafo raiz.
```

### Cadencia de refresco

Graphify no debe seguir el ritmo de Git commit a commit.

Git es memoria continua. Graphify es mapa semantico. El mapa se refresca por
hitos, por severidad o por lote, no por cada modificacion menor.

La cola versionada de refrescos vive en:

```text
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
```

Regla operativa:

```text
LOW      -> no actualizar Graphify
MEDIUM   -> anotar en GRAPHIFY_REFRESH_QUEUE.md
HIGH     -> reconstruir leaf en ventana dedicada
CRITICAL -> reconstruir leaf y decidir root explicitamente
```

Severidad minima:

- `LOW`: typo, README menor, limpieza textual, nota privada no promovida.
- `MEDIUM`: nuevo README funcional, nueva nota de research, documento
  conceptual no promovido.
- `HIGH`: nueva Event Library, nueva Strategy Library, nuevo PDF importante,
  policy local o arquitectura promovida.
- `CRITICAL`: renombres, eliminaciones o migraciones de rutas ya indexadas,
  event taxonomy, contratos canonicos, schemas o semantica de datasets.

Un agente no debe gastar tokens en rebuild Graphify inmediato si el cambio solo
requiere quedar en cola. La decision correcta es documentar el pending refresh y
seguir trabajando en Git.

Flujo obligatorio para nuevos archivos o modificaciones:

1. Revisar `git status --short` y localizar archivos nuevos, modificados o
   eliminados.
2. Clasificar severidad Graphify: `LOW`, `MEDIUM`, `HIGH` o `CRITICAL`.
3. Si es `LOW`, no tocar Graphify.
4. Si es `MEDIUM`, anotar o actualizar entrada en
   `GRAPHIFY_REFRESH_QUEUE.md` y parar ahi.
5. Si es `HIGH` o `CRITICAL`, mapear cada path al slice Graphify
   correspondiente.
6. Ejecutar el flujo oficial Graphify sobre ese slice solo si la tarea actual
   requiere el mapa actualizado o si se esta en una ventana dedicada de refresh:
   - `graphify update` si el slice ya tiene manifest compatible;
   - o rebuild del leaf con la skill Graphify si contiene docs, papers,
     imagenes o material semantico que requiere extraccion LLM/subagentes.
7. Decidir si el root puede aceptar un merge aditivo:
   - si solo hay nuevos documentos o modificaciones en paths ya vigentes,
     fusionar el leaf actualizado con `graphify merge-graphs`;
   - si hubo renombres, eliminaciones o migracion de paths, no usar un merge
     aditivo hasta confirmar que el root no conserva nodos antiguos del slice.
8. Recalcular comunidades con `graphify cluster-only` cuando el root haya sido
   actualizado.
9. Validar con `graphify diagnose multigraph`.
10. Actualizar `graphify-out/BUILD_MANIFEST.md` y, si el cambio altera scope o
   semantica, actualizar `README.md` y `CHANGELOG.md`.

## Baseline Git obligatorio del BUILD_MANIFEST

Cada nuevo leaf o root Graphify de `00_CTO` debe incluir en su
`BUILD_MANIFEST.md` un baseline Git reconstruible.

El manifest debe registrar:

- `graph_build_git_branch`;
- `graph_build_git_commit`;
- `graph_build_dirty_state`;
- `graph_build_dirty_paths`;
- `graph_build_untracked_paths`;
- `graph_build_timestamp_utc`;
- `graph_build_command`;
- `graph_build_backend_or_agent_mode`;
- `graphify_package_version`;
- `graphify_skill_version_or_source`;
- `graphify_upstream_reference`;
- `graphify_installed_vs_protocol_status`;
- `no_api_mode`;
- `semantic_extraction_mode`;
- `build_from_json_root_or_equivalent`;
- `semantic_update_coverage`;
- `corpus_manifest_path`;
- `corpus_file_count`;
- `corpus_inclusion_rules`;
- `corpus_exclusion_rules`;
- `queue_entries_covered`;
- `queue_entries_left_pending`;
- `diagnostics_command`;
- `diagnostics_result`;
- `next_delta_commands`.

Regla:

```text
Un grafo sin commit base y corpus exacto no permite saber que cambio desde el
ultimo build. No debe promocionarse como baseline completo para futuros diffs.
```

Comandos que deben quedar escritos para el siguiente agente:

```powershell
git diff --name-status <graph_build_git_commit>...HEAD
git status --short
```

Si el build se hace con working tree sucio, el manifest debe decirlo y listar
los paths modificados o no trackeados incluidos en el baseline. Si el build
anterior no tiene commit base, el nuevo manifest debe reconstruir la comparacion
con fecha de build, `GRAPHIFY_REFRESH_QUEUE.md`, manifest anterior y
`git status --short`, y debe registrar esa limitacion.

Regla para renombres:

```text
graphify merge-graphs no es reemplazo de slice.
Si el root conserva rutas antiguas, un merge aditivo crea ruido.
```

En ese caso, el agente debe dejar el leaf oficial construido y diagnosticado,
pero no declarar el root actualizado. La integracion correcta requiere rebuild
controlado desde leaves vigentes, o una funcion oficial de reemplazo de slice
si Graphify la ofrece en una version futura.

Si el humano ya hizo commit y el working tree esta limpio, el agente no debe
asumir que no hay nada que actualizar. Debe usar el manifest incremental de
Graphify y el historial Git reciente para comparar contra el ultimo build
documentado.

Prompt operativo reutilizable:

```text
Actualiza el grafo Graphify oficial de 00_CTO tras los cambios recientes.

Reglas:
- Lee 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md antes de actuar.
- No hagas un rebuild monolitico de 00_CTO por defecto.
- Identifica los paths cambiados desde el ultimo build Graphify documentado.
- Clasifica la severidad Graphify: LOW, MEDIUM, HIGH o CRITICAL.
- Si es LOW, no actualices Graphify.
- Si es MEDIUM, anota o actualiza 00_CTO/GRAPHIFY_REFRESH_QUEUE.md y termina.
- Si es HIGH o CRITICAL, mapea cada path a su slice Graphify.
- Si el slice ya tiene manifest compatible, usa el flujo oficial --update.
- Si el slice no tiene manifest compatible, reconstruye el leaf con Graphify
  oficial y despues fusiona.
- Si no hay renombres ni eliminaciones en el slice, fusiona con
  graphify merge-graphs.
- Si hay renombres o eliminaciones, verifica primero que el root no conserva
  nodos de rutas antiguas; si los conserva, no hagas merge aditivo.
- Reclustering con graphify cluster-only solo despues de actualizar el root.
- Diagnostica con graphify diagnose multigraph.
- Actualiza 00_CTO/GRAPHIFY_REFRESH_QUEUE.md con el estado final.
- Actualiza graphify-out/BUILD_MANIFEST.md.
- Actualiza README.md y CHANGELOG.md solo si cambia scope, cobertura o
  semantica.
- No escribas graphify-out/graph.json con scripts manuales.
```

Nota sobre hooks:

```text
No asumir hook automatico.
```

Graphify upstream ofrece `graphify hook install` para reconstruccion automatica
post-commit. TSIS no debe depender de ese mecanismo para `00_CTO` mientras el
grafo raiz sea un grafo fusionado por slices y contenga documentos, PDFs o
referencias que requieren decision de scope. El hook puede ser util para
proyectos simples o cambios AST/code-only; en `00_CTO`, las actualizaciones
semanticamente relevantes deben seguir el protocolo de slices.

Mapping operativo actual:

```text
13_TRADING_SYSTEMS/
-> core_cto_graph / trading_systems_slice
-> Event Library, Event Engine Model, Outcome Research, Strategy Library,
   Strategy Research, Edge Hypotheses, Pattern Discovery, Cluster Research,
   Execution Models, Decision Models, Evolution Systems, Squeeze Research,
   Discretionary Frameworks and Experimental material
-> docs/papers de trading systems; requiere extraccion semantica oficial

12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/
12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/
-> data_quality_harness_graph

12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/
-> sersan_distillation_graph

99_REFERENCE_LIBRARY/SersanSistemas/
-> reference_sersan_graph
-> puede fusionarse al grafo raiz solo con decision explicita de scope
```

No se debe usar `.graphifyignore` para ocultar material semanticamente
importante. `.graphifyignore` sirve para excluir runtime, caches, datasets,
artefactos pesados y outputs reconstruibles. La separacion entre `core`,
`distillation` y `reference` se gobierna por slices y manifests, no por esconder
fuentes relevantes.

Para una carpeta nueva como:

```text
C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS
```

el agente debe tratarla como ampliacion del `core_cto_graph` mediante un
`trading_systems_slice`. El grafo raiz no debe declararse actualizado hasta que
ese slice haya sido extraido por Graphify, integrado sin nodos antiguos del
mismo slice, reclusterizado y diagnosticado.

Estado especial 2026-06-18 para `13_TRADING_SYSTEMS/`:

- El leaf event-first ya fue construido y diagnosticado oficialmente.
- El root actual conserva nodos historicos de
  `13_TRADING_SYSTEMS/01_STRATEGY_LIBRARY/`.
- No debe hacerse un merge aditivo de ese leaf al root actual porque dejaria
  rutas viejas y nuevas en el mismo grafo.

## Prohibicion final

Un agente no debe "salvar" una extraccion fallida escribiendo un grafo manual
en `graphify-out/`.

La accion correcta ante un fallo es diagnosticar, documentar y parar.
