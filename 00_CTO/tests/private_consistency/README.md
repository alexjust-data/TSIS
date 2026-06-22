# CTO Private Consistency Tests

Este directorio reserva pruebas de consistencia entre documentos privados de CTO
y contratos publicos del proyecto.

## Proposito

Algunos documentos de `00_CTO/00_private/` pueden contener planes, decisiones o
arquitectura de trabajo. Los tests aqui deben comprobar que las decisiones que
ya se promocionaron al sistema publico aparecen tambien en contratos publicos,
sin filtrar contenido sensible.

## Reglas

- Los tests no deben imprimir contenido privado completo en logs.
- Los tests no deben copiar secretos, credenciales ni notas sensibles a outputs
  publicos.
- Los tests deben validar referencias, hashes, titulos, secciones esperadas o
  nombres de contratos, no reproducir texto privado extenso.
- Si una decision privada gobierna una salida institucional, debe existir una
  version publica suficiente para agentes futuros.

## Pruebas esperadas

Pruebas candidatas:

- `test_private_plan_public_contract_coverage.py`: cada decision promocionada
  desde planes privados tiene contrato publico.
- `test_no_private_only_operational_rule.py`: ninguna regla operativa vigente
  queda solo en `00_private`.
- `test_sensitive_output_guard.py`: los reportes de test no exponen fragmentos
  privados extensos.

