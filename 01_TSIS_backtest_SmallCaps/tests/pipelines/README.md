# Pipeline Tests

Este directorio valida pipelines y scripts de materializacion del modulo
SmallCaps.

## Ambito

Aqui deben vivir tests que comprueben:

- idempotencia de scripts;
- separacion entre raw data y outputs derivados;
- escritura en rutas canonicas;
- generacion de manifests;
- versionado logico de outputs;
- ausencia de sobrescritura silenciosa;
- manejo reproducible de configuraciones.

## Relacion con Data Foundation Outputs

Si el pipeline construye una tabla institucional, este directorio puede testear
el comportamiento del script. El resultado final de la tabla debe validarse en
`data_foundation_outputs/`.

Ejemplo:

- `pipelines/`: el script rechaza escribir sin version o manifest.
- `data_foundation_outputs/`: el parquet final cumple schema, hashes y fuentes.

## Criterio de calidad

Un pipeline no debe aprobar solo porque termina sin excepcion. Debe demostrar:

- que lee las fuentes declaradas;
- que escribe donde el contrato dice;
- que no toca raw data;
- que produce manifest suficiente;
- que falla ante configuraciones ambiguas.

