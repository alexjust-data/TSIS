# Institutional Monorepo Tests

Este directorio contiene los tests de gobierno global de TSIS.

Estos tests deben ejecutarse desde la raiz del repositorio y deben tratar el
monorepo como un sistema unico. No deben depender de notebooks ni de estado
oculto de conversaciones.

## Ambito

Aqui deben vivir pruebas como:

- `test_root_contracts.py`: existencia y consistencia de `AGENTS.md`,
  `PROJECT_OPERATING_SYSTEM.md`, `PROJECT_RULES.md`,
  `VERSIONING_STANDARDS.md`, `ARCHITECTURE_OVERVIEW.md`,
  `RESEARCH_PHILOSOPHY.md` y `CHANGELOG.md`.
- `test_module_boundaries.py`: los modulos no se contaminan entre si; research,
  live y RL mantienen fronteras explicitas.
- `test_graphify_queue_consistency.py`: los cambios semanticos relevantes quedan
  anotados como pending o reconciliados en las colas Graphify adecuadas.
- `test_versioning_policy.py`: los cambios institucionales tienen changelog,
  version logica o nota de migracion cuando aplica.

## Que no pertenece aqui

No pertenece aqui:

- validar filas de `instrument_master`;
- validar sesiones de `market_calendar`;
- inspeccionar imagenes de dossiers de una familia de datos concreta;
- comprobar una estrategia especifica;
- comprobar una politica concreta de ejecucion.

Eso debe vivir dentro del modulo que posee esos artefactos.

## Evidencia exigida

Cada test global debe dejar claro:

- que contrato protege;
- que ruta valida;
- que fallo institucional detectaria;
- si requiere evidencia externa congelada;
- si puede ejecutarse offline o necesita opt-in de red.

Los tests con fuentes externas no deben depender de internet por defecto. Deben
usar evidencia cacheada o saltarse explicitamente salvo que una variable de
entorno habilite la comprobacion en vivo.

