# Graphify Refresh Queue for 01_foundations

Fecha de creacion: 2026-06-19
Estado: cola operativa versionada para refrescos Graphify de `01_foundations`.

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

La definicion metodologica de slices vive en:

```text
module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md
```

## Severidad de refresco

### LOW

No requiere Graphify.

Ejemplos:

- typo;
- README menor;
- limpieza textual;
- nota privada o no promovida;
- cambio que no altera contratos, schemas, registries, policies ni validators.

Accion:

```text
No hacer nada en Graphify.
```

### MEDIUM

Se anota en esta cola, pero no se refresca inmediatamente.

Ejemplos:

- nuevo documento explicativo;
- nuevo README funcional;
- ampliacion documental sin cambio contractual;
- evidencia ligera no promovida;
- ajuste de navegacion que afecta como un agente encuentra documentos.

Accion:

```text
Anotar entrada pending.
Refrescar cuando haya lote suficiente o una consulta lo necesite.
```

### HIGH

Requiere rebuild del leaf afectado en una ventana dedicada.

Ejemplos:

- nuevo dataset contract;
- nuevo schema canonico;
- nueva data consumption policy;
- validator que cambia aceptacion;
- closeout que cambia interpretacion;
- nuevo protocolo transversal de tablas;
- nuevo graph slice.

Accion:

```text
Construir o actualizar leaf oficial.
No actualizar root si no es necesario para la tarea inmediata.
```

### CRITICAL

Requiere decision explicita antes de tocar el root.

Ejemplos:

- renombrar carpetas ya indexadas;
- eliminar o migrar rutas indexadas;
- cambiar semantica de dataset;
- cambiar price semantics;
- cambiar certification/recovery state;
- promocionar master table;
- cambiar consumo downstream.

Accion:

```text
Construir leaf si aporta valor inmediato.
No hacer merge aditivo si el root conserva nodos antiguos.
Integrar root solo mediante rebuild controlado o reemplazo oficial de slice.
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
  Integracion limpia del root si hace falta.
```

## Entradas activas

### GFQ-20260619-001 - Initial Data Foundation Graphify governance

Status: `leaf_built`

Severity: `HIGH`

Slice:

```text
foundations_authority_graph
```

Reason:

- Se creo la gobernanza inicial para Graphify de CAPA 1.
- Existen nuevos documentos que deben entrar en el mapa semantico cuando se
  construya el primer leaf oficial:
  - `GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md`
  - `GRAPHIFY_REFRESH_QUEUE.md`
  - `module_contracts/graphify/README.md`
  - `module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md`

Changed paths:

```text
01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_foundations/.graphifyignore
01_foundations/README.md
01_foundations/module_contracts/graphify/
01_foundations/module_contracts/README.md
```

Recommended action:

```text
Built foundations_authority_graph as the first official leaf.
Do not build a monolithic 01_foundations graph yet.
```

Root action:

```text
No root graph yet.
```

Owner:

```text
Modulo 01 / Data Foundation governance
```

Notes:

The first useful Graphify build for CAPA 1 should map authority, not evidence.
Evidence-heavy dossiers and parquet/CSV profiling come later and must stay
separate.

`foundations_authority_graph` is not a physical folder. It is the first official
leaf graph name. The full `01_foundations` map is expected to emerge from
separate leaves and, if useful, a later `data_foundation_root_graph`.

Build result:

```text
Output:
01_foundations/graphify-out/leaf_slices/foundations_authority_20260619/

Stats:
- detected_files: 246
- detected_words: 411452
- nodes: 696
- edges: 854
- communities: 75

Validation:
- graphify diagnose multigraph passed with 0 dangling endpoints, 0 duplicate
  edges, and 0 endpoint-collapsed edge groups.
- root graph intentionally not created:
  01_foundations/graphify-out/graph.json = absent
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
