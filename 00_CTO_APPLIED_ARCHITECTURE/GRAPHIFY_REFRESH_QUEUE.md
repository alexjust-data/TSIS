# Graphify Refresh Queue for 00_CTO_APPLIED_ARCHITECTURE

Estado: cola operativa versionada de la rama.

## Regla

Los cambios con impacto semantico deben cerrar con actualizacion y diagnostico
del leaf oficial afectado o con una entrada `pending` en este archivo.

## Pending

### GFQ-20260805-APPLIED-001 - Agent Graphify closeout policy

- **Estado:** `pending`
- **Severidad:** `HIGH`
- **Scope:** gobierno local de agentes
- **Leaf objetivo:** grafo oficial de `00_CTO_APPLIED_ARCHITECTURE`
- **Archivos afectados:** `AGENTS.md`, `GRAPHIFY_REFRESH_QUEUE.md`
- **Motivo:** se anadio la obligacion explicita de actualizar el grafo o
  persistir el aplazamiento. No se ejecuto rebuild durante esta auditoria.
- **Cierre esperado:** rebuild/update oficial, diagnostico limpio y
  `BUILD_MANIFEST.md` actualizado.
