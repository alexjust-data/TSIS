# Graphify Refresh Queue

Estado: cola operativa versionada para el grafo raiz de `C:\TSIS_Data`.

## Regla

Toda tarea con impacto semantico sobre una rama que contenga `graphify-out/`
debe terminar con el leaf oficial actualizado y diagnosticado o con una entrada
`pending` en la cola mas cercana. Esta cola es el fallback para cambios de
alcance raiz o para ramas sin cola local.

Cada entrada debe incluir fecha, estado, severidad, scope, leaf objetivo,
archivos afectados, motivo del aplazamiento y criterio de cierre.

## Pending

### GFQ-20260805-ROOT-001 - Agent Graphify closeout policy

- **Estado:** `pending`
- **Severidad:** `HIGH`
- **Scope:** gobierno raiz y herencia de agentes
- **Leaf objetivo:** `graphify_governance` y siguiente fusion raiz
- **Archivos afectados:** `C:\TSIS_Data\AGENTS.md`,
  `C:\TSIS_Data\GRAPHIFY_REFRESH_QUEUE.md`
- **Motivo:** se normalizo la obligacion de cerrar cada trabajo con un leaf
  actualizado o una entrada pendiente. No se reconstruyo el grafo raiz.
- **Cierre esperado:** reconstruir y diagnosticar el leaf de gobierno y
  sustituir su cobertura en la siguiente fusion raiz oficial.
