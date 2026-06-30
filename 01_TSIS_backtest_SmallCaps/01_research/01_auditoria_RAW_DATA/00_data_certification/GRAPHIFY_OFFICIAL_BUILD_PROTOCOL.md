# Graphify Official Build Protocol for 00_data_certification

Fecha: 2026-06-19
Estado: regla operativa local para agentes.

## Proposito

Este documento gobierna los builds oficiales de Graphify para:

```text
01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification
```

`00_data_certification` es memoria cientifica preservada de auditoria,
diagnostico, closeouts y decisiones de certificacion. Su grafo no debe tratarse
como un escaneo documental generico ni como reemplazo de los contratos vivos en
`01_foundations`.

## Regla corta

```text
No escribas manualmente 00_data_certification/graphify-out/graph.json.
Si no lo genero Graphify, no es Graphify oficial.
```

## Relacion con 01_foundations

`01_foundations` define autoridad operativa viva:

```text
contracts, schemas, registries, policies, validators
```

`00_data_certification` preserva evidencia historica y decisiones:

```text
expected/present/healthy/usable_for, recovery, exclusion, closeouts,
certification policies, global metrics, audit contracts
```

El grafo de certificacion debe ayudar a detectar si `01_foundations`
simplifica demasiado una decision historica.

## Que cuenta como build oficial

Un build oficial debe venir de uno de estos flujos:

- `$graphify <path>` desde Codex, con la skill Graphify activa;
- `graphify <path>` desde CLI;
- `graphify <path> --update` cuando exista manifest compatible;
- `graphify <path> --cluster-only` sobre un grafo ya oficial;
- merge o export oficial ofrecido por la version instalada de Graphify.

El build oficial esperado genera, salvo decision documentada:

```text
graphify-out/
  graph.html
  GRAPH_REPORT.md
  graph.json
```

Si se omite `graph.html` por `--no-viz`, debe quedar documentado en la cola o
manifest del build.

## Modo sin APIs y version de Graphify

Fuente directa de esta regla: `https://github.com/safishamsi/graphify`, rama
`v8`, version upstream `graphifyy 0.9.1`, revisada el 2026-06-28.

Estado observado en esta maquina el 2026-06-28:

```text
graphifyy instalado: 0.8.40
upstream revisado:   0.9.1
```

Antes de cualquier nuevo build oficial de `00_data_certification`, el agente
debe comprobar y registrar la version efectiva de Graphify y de la skill usada.
Si la version instalada sigue por detras del protocolo upstream revisado, el
build solo puede declararse baseline oficial si se documenta una de estas
opciones:

- Graphify instalado fue actualizado/alineado;
- se ejecuto el flujo oficial desde la version upstream revisada;
- o el build queda marcado como `provisional` por limitacion de version.

TSIS opera por defecto sin APIs externas para Graphify. La ausencia de
`GEMINI_API_KEY` o `GOOGLE_API_KEY` no autoriza a pedir `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY` ni otro proveedor. Para closeouts, policies, notebooks
destilados, markdown, papers o imagenes, el modo correcto en Codex es:

```text
skill Graphify -> AST local para codigo -> subagentes/host agent para
extraccion semantica -> build oficial -> diagnostics -> manifest.
```

Un corpus solo de codigo puede usar el flujo AST/code-only sin API y sin
subagentes semanticos.

Regla critica:

```text
graphify update por CLI es suficiente solo para cambios code/AST cuando ese
scope lo permita. No prueba cobertura semantica de markdown, closeouts, papers,
notebooks convertidos o imagenes.
```

Para cambios documentales de certificacion, usar el flujo semantico de la skill
Graphify o `graphify extract` con backend ya configurado. Si no hay backend ni
subagentes disponibles, el agente debe parar, documentar la causa y no escribir
un grafo parcial en `graphify-out/`.

## Que no cuenta como build oficial

No cuenta como oficial:

- crear `graph.json` a mano con PowerShell, Python u otro script propio;
- generar nodos/edges curados manualmente;
- copiar un JSON compatible sin conservar procedencia;
- presentar un fallback compatible como si fuera Graphify;
- usar `graphify query`, `graphify explain` o `graphify path` como prueba de
  procedencia;
- hacer un grafo monolitico de todo `00_data_certification` si mezcla
  certification docs, notebooks, imagenes, parquet, CSV, scripts y runtime.

Regla:

```text
Formato compatible no prueba procedencia.
```

## Divergencia TSIS respecto al workflow de Graphify

Graphify upstream puede recomendar compartir `graphify-out/` con el equipo.

En TSIS, `graphify-out/` se trata como runtime reconstruible salvo promocion
explicita. La memoria versionada de como construir el grafo vive en:

```text
00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
00_data_certification/module_contracts/graphify/
```

Esto gobierna versionado y trazabilidad. No autoriza builds manuales.

Politica Git local:

```text
00_data_certification/graphify-out/ raiz sigue siendo runtime reconstruible.
00_data_certification/graphify-out/leaf_slices/<leaf_id>/ puede publicarse en
Git si fue promocionado con BUILD_MANIFEST.md, corpus reconstruible,
graph.json, GRAPH_REPORT.md, graph.html y diagnostico limpio.
```

Un leaf deterministico, topologico, de navegacion o de provenance debe declarar
esa limitacion en `BUILD_MANIFEST.md` y `GRAPH_REPORT.md`. Puede servir como
mapa controlado y versionable, pero no debe sustituir ni borrar un leaf
semantico previo si no cubre la misma semantica.

## Scope correcto

No hacer como primer paso:

```text
graphify 00_data_certification
graphify 01_research/01_auditoria_RAW_DATA
graphify 01_TSIS_backtest_SmallCaps
```

Motivo:

- `00_data_certification` contiene auditoria, notebooks, imagenes, parquet,
  CSV, scripts, caches y material historico preservado;
- un grafo monolitico mezclaria decisiones finales con evidencia fisica,
  exploracion y runtime;
- los notebooks son importantes, pero deben entrar en un leaf de evidencia de
  notebooks, no en el grafo inicial de decisiones de certificacion.

## Familia de grafos

El grafo de certificacion debe entenderse como familia de leaves:

```text
certification_decisions_graph
certification_notebook_evidence_graph
certification_physical_evidence_graph
```

El primer leaf oficial es:

```text
certification_decisions_graph
```

Ese leaf mapea decisiones finales, policies, closeouts y global metrics
livianos. No absorbe notebooks ni evidencia binaria.

## Documentos que gobiernan este flujo

Leer en este orden:

1. `01_TSIS_backtest_SmallCaps/LOCAL_RULES.md`
2. `00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
3. `00_data_certification/GRAPHIFY_REFRESH_QUEUE.md`
4. `00_data_certification/module_contracts/graphify/README.md`
5. `00_data_certification/module_contracts/graphify/certification_decisions_graph_protocol.md`
6. los closeouts, policies, contratos y global metrics del slice.

## Procedimiento de build

1. Revisar esta politica y la cola local.
2. Elegir un solo slice.
3. Confirmar corpus incluido y excluido.
4. Ejecutar Graphify con flujo oficial.
5. Verificar que existen:

```powershell
Test-Path .\graphify-out\leaf_slices\<leaf>\graph.json
Test-Path .\graphify-out\leaf_slices\<leaf>\GRAPH_REPORT.md
Test-Path .\graphify-out\leaf_slices\<leaf>\graph.html
```

6. Validar con:

```powershell
graphify diagnose multigraph --graph .\graphify-out\leaf_slices\<leaf>\graph.json
graphify explain "<nodo canonico>" --graph .\graphify-out\leaf_slices\<leaf>\graph.json
```

7. Actualizar `GRAPHIFY_REFRESH_QUEUE.md` y el manifest del leaf.

## Baseline Git obligatorio del BUILD_MANIFEST

Cada nuevo leaf Graphify de `00_data_certification` debe incluir en su
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

## Regla para notebooks

Los notebooks son evidencia historica importante. Se excluyen por defecto del
`certification_decisions_graph` para evitar que exploracion, celdas fuera de
orden, outputs visuales y paths locales se mezclen con decisiones finales.

Los notebooks deben entrar en un leaf separado:

```text
certification_notebook_evidence_graph
```

Ese leaf debe declarar claramente que mapea exploracion/evidencia, no autoridad
final.
