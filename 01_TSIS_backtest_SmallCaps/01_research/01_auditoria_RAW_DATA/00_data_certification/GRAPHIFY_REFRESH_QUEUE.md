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
