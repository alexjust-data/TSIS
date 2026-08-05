# Graphify Refresh Queue for 00_data_certification

Fecha de creacion: 2026-06-19
Estado: cola operativa versionada para refrescos Graphify de
`00_data_certification`.

## Rol

Este archivo evita tratar Graphify como si fuera Git.

Git registra cambios continuamente. Graphify se refresca por hitos semanticos,
por severidad o por lote.

Regla:

```text
No actualizar Graphify por cada commit.
Actualizar Graphify cuando el cambio altere el mapa semantico que un agente
necesita consultar.
```

El protocolo autoritativo vive en:

```text
GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
```

La definicion metodologica del primer slice vive en:

```text
module_contracts/graphify/certification_decisions_graph_protocol.md
```

## Severidad de refresco

### LOW

No requiere Graphify.

Ejemplos:

- typo;
- README menor;
- limpieza textual;
- comentario local no promovido.

Accion:

```text
No hacer nada en Graphify.
```

### MEDIUM

Se anota en esta cola, pero no se refresca inmediatamente.

Ejemplos:

- nuevo documento explicativo;
- nuevo README funcional;
- evidencia ligera no promovida;
- ajuste de navegacion documental.

Accion:

```text
Anotar entrada pending.
Refrescar cuando haya lote suficiente o una consulta lo necesite.
```

### HIGH

Requiere rebuild del leaf afectado en una ventana dedicada.

Ejemplos:

- nuevo closeout final;
- nueva policy de certificacion;
- cambio de decision `expected/present/healthy/usable_for`;
- cambio de recovery/exclusion;
- nuevo global metrics manifest;
- nuevo graph slice.

Accion:

```text
Construir o actualizar leaf oficial.
No actualizar root si no es necesario para la tarea inmediata.
```

### CRITICAL

Requiere decision explicita antes de tocar integraciones.

Ejemplos:

- renombrar rutas historicas ya indexadas;
- eliminar o migrar evidencia historica;
- cambiar semantica final de certificacion;
- cambiar el sentido de una exclusion o rehabilitacion;
- promover decisiones hacia `01_foundations`.

Accion:

```text
Construir leaf si aporta valor inmediato.
No hacer merge aditivo si el root conserva nodos antiguos.
Integrar solo mediante rebuild controlado o reemplazo oficial de slice.
```

## Cadencia recomendada

```text
Diario:
  Git normal.
  Documentar cambios relevantes.
  Anotar pending refresh si aplica.

Por hito:
  Rebuild de leaves afectados.

Por ventana dedicada:
  Integracion limpia solo si hace falta.
```

## Entradas activas

### GFQ-20260628-002 - Graphify no-API and version-alignment protocol

Status: full_semantic_leaf_built

Severity: HIGH

Slice:

```text
certification_decisions_graph
graphify_governance_slice
```

Why:

- `00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md` now explicitly
  requires no-API Codex semantic extraction through the Graphify skill
  host-agent/subagent path when no Gemini/Google API is configured.
- Future certification Graphify `BUILD_MANIFEST.md` files must record package
  version, skill/source version, upstream reference, no-API mode and semantic
  coverage.
- CLI `graphify update` alone is not sufficient semantic coverage for
  closeouts, policies, markdown, papers, notebooks converted to documents or
  images.

Changed paths:

```text
00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Required Graphify action:

```text
Include this protocol change in the next official certification governance
leaf. This queue entry does not prove graph refresh completion.
```

Build result:

```text
Covered by cross-project governance leaf:
C:/TSIS_Data/00_CTO/graphify-out/leaf_slices/graphify_governance_20260629/

Graphify package: graphifyy 0.9.1
Semantic mode: Codex host inline extraction, no external API required
Nodes: 37
Edges: 60
Communities: 9
Diagnostic: clean

Important limitation:
This satisfies graphify_governance_slice coverage for the protocol change, but
it does not rebuild certification_decisions_graph or any certification root
graph. Those remain pending by slice.
```

Certification leaf result:

```text
Built topology refresh leaf:
00_data_certification/graphify-out/leaf_slices/certification_decisions_topology_20260629/

Graphify package: graphifyy 0.9.1
Semantic mode: deterministic_certification_decision_topology
Corpus files: 88
Nodes: 122
Edges: 653
Communities: 11
Diagnostic: clean
Root graph: absent / not merged
```

Important limitation:

```text
This topology leaf records modern provenance, corpus and diagnostics for the
controlled certification decisions corpus. It does not replace the full
semantic `certification_decisions_20260619` leaf produced with semantic worker
chunks. A full semantic refresh remains pending if field-level/case-level graph
reasoning is needed.
```

### GFQ-20260628-001 - Graphify build baseline provenance rule

Status: full_semantic_leaf_built

Severity: HIGH

Slice:

```text
certification_graphify_governance
```

Reason:

- The certification Graphify protocol now requires every future
  `BUILD_MANIFEST.md` to record commit, dirty state, exact corpus, queue
  coverage, diagnostics and next-delta commands.
- This keeps future certification leaf rebuilds auditable from the previous
  graph baseline instead of relying on conversation memory.

Changed paths:

```text
00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
```

Recommended action:

```text
Include this governance change in the next certification graph governance or
certification_decisions leaf refresh. Do not rebuild a monolithic
00_data_certification graph.
```

Root action:

```text
No root graph.
```

Build result:

```text
Covered by:
C:/TSIS_Data/00_CTO/graphify-out/leaf_slices/graphify_governance_20260629/BUILD_MANIFEST.md

The manifest records graphify package version, skill path/hash, upstream
reference, no-API mode, semantic extraction mode, commit, dirty state, exact
corpus, diagnostics and next-delta commands.
```

Certification leaf result:

```text
Covered by:
00_data_certification/graphify-out/leaf_slices/certification_decisions_topology_20260629/BUILD_MANIFEST.md

The manifest records graphify package version, skill path/hash, upstream
reference, no-API mode, semantic extraction mode, commit, dirty state, exact
corpus, diagnostics and next-delta commands.
```

Owner:

```text
Modulo 01 / RAW data certification governance
```

### GFQ-20260619-001 - Initial certification decisions Graphify governance

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
certification_decisions_graph
```

Reason:

- Se inicia el primer leaf oficial de Graphify para decisiones de auditoria y
  certificacion.
- El grafo debe vivir dentro de `00_data_certification`, no dentro de
  `01_foundations`.
- Debe mapear closeouts, policies, contratos historicos y global metrics
  livianos sin absorber notebooks ni evidencia pesada.

Changed paths:

```text
00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
00_data_certification/.graphifyignore
00_data_certification/module_contracts/graphify/
```

Recommended action:

```text
Built certification_decisions_graph as the first official certification leaf.
Do not build a monolithic 00_data_certification graph.
Do not include notebooks in this leaf.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / RAW data certification governance
```

Notes:

The first useful Graphify build for `00_data_certification` should map final
certification decisions, not exploratory notebooks or physical evidence.

Notebooks remain important and should later enter a separate leaf:

```text
certification_notebook_evidence_graph
```

Build result:

```text
Output:
00_data_certification/graphify-out/leaf_slices/certification_decisions_20260619/

Stats:
- detected_files: 89
- detected_words: 45813
- nodes: 252
- edges: 322
- communities: 22

Validation:
- graphify diagnose multigraph passed with 0 dangling endpoints, 0 duplicate
  edges, and 0 endpoint-collapsed edge groups.
- graphify explain passed on node `Certification Decisions Graph`.
- root graph intentionally not created:
  00_data_certification/graphify-out/graph.json = absent
```

## Entry template

```text
### GFQ-YYYYMMDD-NNN - <title>

Status: pending | pending_leaf_build | leaf_built | pending_root_integration | closed | cancelled
Severity: LOW | MEDIUM | HIGH | CRITICAL
Slice:
Reason:
Changed paths:
Recommended action:
Root action:
Owner:
Notes:
```

## 2026-07-05 - Certification topology refresh executed

Status: topology_leaf_built_project_root_merged
Severity: HIGH

Covered slices:

```text
certification_decisions_topology_20260705
project_current_20260705 root merge
```

Build outputs:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/graphify-out/leaf_slices/certification_decisions_topology_20260705/
C:/TSIS_Data/graphify-out/graph.json
C:/TSIS_Data/graphify-out/project_current_20260705/
```

Build result:

```text
Certification topology leaf: 122 nodes, 653 edges, 11 communities.
Diagnostic: clean, no missing endpoints, no dangling edges, no self-loops.
Project root merge: 464 nodes, 1507 edges, 49 communities after cluster-only.
```

Limitations:

```text
This is the same deterministic topology coverage model as the 20260629 leaf,
rebuilt as a current 20260705 snapshot and merged into the project root. It does
not replace the older full semantic certification_decisions_20260619 leaf if
case-level or field-level semantic reasoning is required.
```



## 2026-08-05 - Full semantic certification leaf rebuilt

Status: full_semantic_leaf_built
Severity: HIGH

Canonical output:

```text
graphify-out/leaf_slices/certification_decisions/
```

Build result:

```text
Graphify package: graphifyy 0.9.33
Corpus: 88 files / 46,873 words
Extraction: 48 AST nodes + 212 semantic nodes
Graph: 260 nodes / 293 edges / 19 communities
Diagnostics: 0 duplicate, dangling, missing, self-loop or collapsed edges
Semantic mode: four Codex host workers, no external API key
```

This stable leaf supersedes dated leaves for new integrations. Historical
semantic and topology leaves remain preserved as audit evidence. Notebook
evidence and the `01_foundations` authority graph remain separate pending
leaves.

