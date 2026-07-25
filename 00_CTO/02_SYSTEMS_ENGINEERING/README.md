# Systems Engineering

Fecha de actualizacion: 2026-07-07
Estado: CTO systems engineering workspace activo.

## Objetivo

`02_SYSTEMS_ENGINEERING/` disena TSIS como sistema mantenible.

No es la capa de IA, no es la capa de trading y no es una carpeta de runtime.
Su funcion es documentar arquitectura tecnica transversal: modulos,
interfaces, data flow, contratos tecnicos, boundaries de seguridad y decisiones
de diseno que conectan varias partes del proyecto.

## Preguntas

Esta carpeta debe responder:

- como se comunican los modulos;
- donde vive cada clase de dato;
- como se desacoplan fuentes externas, adapters y consumidores;
- que contratos gobiernan cada boundary;
- que queda como referencia externa, que queda como implementacion y que queda
  como data plane;
- que decisiones tecnicas deben leer futuros agentes antes de modificar un
  sistema compartido.

## Contenido esperado

- arquitectura de interfaces;
- module boundaries;
- data flow;
- event-driven design;
- source adapters;
- broker/API safety boundaries;
- technical decisions.

## Estructura activa

```text
02_SYSTEMS_ENGINEERING/
  README.md
  01_INTERFACES_AND_ADAPTERS/
    README.md
    live_source_adapter_topology_v0_1.md
    broker_api_safety_boundary_v0_1.md
    das_api/
      dastrades_cmdapi_system_map_v0_1.md  # local ignored detailed API map
```

## 01_INTERFACES_AND_ADAPTERS

Esta seccion explica como TSIS organiza fuentes externas, vendor APIs,
broker APIs, adapters, contratos de captura, data roots fisicos y consumidores
posteriores.

Regla central:

```text
source reference != source adapter != live payload != governed state/features
```

La seccion no implementa adapters. La implementacion vive en el modulo que
opera la fuente. Para live ingestion SmallCaps, la autoridad operativa vive en:

```text
C:/TSIS_Data/04_TSIS_webSocket_SmallCaps
```

## No-goals

Esta carpeta no debe contener:

- credenciales;
- payloads live;
- transcripts sensibles;
- manuales completos de proveedor si ya viven en Reference Library;
- codigo de adapters;
- configs operativas;
- runtime outputs;
- secretos de broker;
- contratos operativos que pertenecen al modulo live.

## Resultado esperado

Arquitectura mantenible durante anos, con boundaries claros para que agentes,
modulos y futuros adapters no mezclen referencia externa, implementacion,
datos capturados, estado gobernado ni ejecucion.
