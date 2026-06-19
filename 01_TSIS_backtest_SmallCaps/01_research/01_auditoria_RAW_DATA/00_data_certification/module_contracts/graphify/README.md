# Graphify Governance for 00_data_certification

Estado: gobernanza local para grafos de certificacion.

## Rol

Este directorio documenta como construir grafos oficiales de Graphify para:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification
```

El objetivo no es reorganizar la evidencia historica. El objetivo es mapearla
con scopes controlados para que agentes y humanos puedan consultar decisiones
de certificacion sin mezclar autoridad final, notebooks exploratorios, imagenes,
parquet, CSV o runtime.

## Documentos

```text
certification_decisions_graph_protocol.md
```

Define el primer leaf oficial:

```text
certification_decisions_graph
```

## Relacion con otros grafos

`foundations_authority_graph` vive en `01_foundations` y mapea autoridad viva:
contratos, schemas, registries, policies y validators.

`certification_decisions_graph` vive aqui y mapea decisiones historicas:
closeouts, policies de certificacion, recovery/exclusion, expected/present/
healthy/usable_for y global metrics livianos.

Un futuro `data_foundation_root_graph` solo debe nacer de leaves oficiales
construidos y diagnosticados.

## Regla para notebooks

Los notebooks son importantes, pero no entran en el primer leaf de decisiones.

La ruta correcta es crear despues un leaf separado:

```text
certification_notebook_evidence_graph
```

Ese leaf debe explicar que los notebooks son evidencia exploratoria o soporte de
closeout, no contratos finales por defecto.
