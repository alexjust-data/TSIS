# CTO Governance Contract Tests

Este directorio valida las reglas de gobierno institucional del area CTO.

## Proposito

La arquitectura solo es fiable si sus cambios quedan versionados y trazables.
Estos tests deben detectar cambios semanticos sin changelog, sin cola Graphify o
sin nota de impacto cuando corresponde.

## Pruebas esperadas

Pruebas candidatas:

- `test_cto_changelog_required.py`: cambios en arquitectura o contratos CTO
  tienen entrada de changelog.
- `test_cto_graphify_queue_required.py`: cambios semanticos relevantes quedan en
  la cola Graphify correspondiente.
- `test_versioning_language.py`: los documentos CTO usan lenguaje de estado
  claro: exploratory, provisional, validated o institutional.
- `test_no_hidden_operating_rules.py`: reglas operativas importantes no quedan
  solo en documentos privados o conversaciones.

## Relacion con pruebas raiz

Los tests raiz validan reglas globales de TSIS. Estos tests validan como esas
reglas se aplican especificamente dentro de `00_CTO`.

## Evidencia

Cuando una prueba falle, el mensaje debe indicar:

- documento afectado;
- regla de gobierno incumplida;
- archivo de changelog o cola esperada;
- accion correctiva minima.

