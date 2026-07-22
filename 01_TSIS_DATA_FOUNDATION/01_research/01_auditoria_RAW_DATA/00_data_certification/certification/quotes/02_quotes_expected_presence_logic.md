# Quotes Expected Presence Logic

## Estado real

La logica final de `expected` para `quotes` no esta cerrada todavia en el proyecto.
Por tanto, este documento no debe forzar una solucion nueva.

## Lo que si sabemos

Hay tres restricciones obvias que deben respetarse cuando llegue el cierre final:

- universo `<1B>`
- vida PTI del ticker
- alcance temporal real del dataset materializado

## Lo que no debemos hacer

No debemos construir ahora un expected diario sintetico y tratarlo como verdad cerrada.
Eso seria adelantarnos a la certificacion global.

## Uso correcto por ahora

Hasta que el expected set global quede fijado:

- `auditoria\01_auditoria_1B_general.md` manda para cobertura
- `quotes_current.parquet` manda para presencia observada
- cualquier logica de faltantes finos queda pendiente de ensamblado final

## Decision

Este punto queda abierto pero acotado.
No esta resuelto por este documento.
Se resolvera al final de la certificacion global, no de forma aislada dentro de `quotes`.
