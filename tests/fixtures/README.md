# Test Fixtures

Esta carpeta guarda datos pequenos y deterministas para tests.

Los fixtures deben ser suficientes para probar comportamiento, no para duplicar
datasets reales.

## Usos validos

- mini parquet sintetico con duplicados controlados;
- muestra pequena congelada para probar schema;
- input corrupto deliberado para mutation tests;
- CSV minimo para validar parser;
- calendario reducido para edge cases.

## Reglas

- Cada fixture debe tener nombre explicito.
- Si deriva de data real, debe declarar fuente, fecha y criterio de muestra.
- No guardar informacion sensible.
- No guardar datasets pesados.
- No usar fixtures como source of truth productiva.

