# Graphify Refresh Queue for 01_TSIS_DATA_FOUNDATION

Estado: cola fallback para gobierno comun de Data Foundation. Las ramas
`01_foundations` y `00_data_certification` conservan sus colas mas cercanas
para cambios de sus corpus respectivos.

## Regla

Los cambios comunes con impacto semantico deben cerrar con actualizacion y
diagnostico del leaf afectado o con una entrada `pending` aqui. Los cambios
locales deben usar la cola local mas cercana.

## Pending

### GFQ-20260805-FOUNDATION-001 - Agent Graphify closeout policy

- **Estado:** `pending`
- **Severidad:** `HIGH`
- **Scope:** gobierno comun de Data Foundation
- **Leaves objetivo:** `foundations_authority`,
  `certification_decisions` y futura fusion `data_foundation_root`
- **Archivos afectados:** `AGENTS.md`, `GRAPHIFY_REFRESH_QUEUE.md`
- **Motivo:** se normalizo la obligacion de actualizar o registrar pending para
  todas las subramas con Graphify. No se reconstruyeron esos leaves.
- **Cierre esperado:** incorporar esta politica al siguiente leaf de gobierno o
  autoridad aplicable y validar la fusion superior.
