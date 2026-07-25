# Interfaces And Adapters

Fecha de creacion: 2026-07-07
Estado: systems_engineering_map
Owner layer: `00_CTO/02_SYSTEMS_ENGINEERING`

## Proposito

Esta carpeta documenta como TSIS conecta sistemas externos con modulos internos
sin mezclar responsabilidades.

Una fuente externa puede ser un vendor market-data API, un broker API, un feed
websocket, una flat-file delivery, una libreria local de referencia o un future
adapter propio. La arquitectura debe separar siempre:

```text
external source/reference
-> adapter contract
-> implementation/runtime
-> physical data root
-> parity/certification audit
-> governed state/features
-> downstream consumers
```

## Documentos

### `live_source_adapter_topology_v0_1.md`

Mapa general para fuentes live. Define la topologia comun desde vendor/broker
API hasta data root, source parity audit y consumo por estado/features.

### `broker_api_safety_boundary_v0_1.md`

Boundary de seguridad para APIs de broker. Fija read-only por defecto,
separacion entre captura y ejecucion, reglas de secretos y prohibicion de
ordenes sin contrato explicito.

### `das_api/dastrades_cmdapi_system_map_v0_1.md`

Mapa local/ignorado especifico de DasTrades/Sage CMD API dentro de TSIS. Explica donde vive la
referencia cruda, donde vive el contrato live, donde vive la app local, donde se
escriben los datos y como se conecta con source parity/live state.

## Reglas

- Esta carpeta no contiene implementacion.
- Esta carpeta no contiene credenciales ni payloads.
- Esta carpeta no convierte una fuente externa en autoridad canonica.
- Todo adapter live debe tener contrato antes de alimentar state/features.
- Todo dato live capturado debe escribirse en un data root fisico declarado.
- Todo campo model-facing debe pasar por source parity/cutoff semantics antes de
  consumo ML/RL/live.

## Relacion Con Otros Paths

```text
00_CTO/99_REFERENCE_LIBRARY/
  referencia externa cruda, no autoridad directa

04_TSIS_webSocket_SmallCaps/01_data_ingestion_live/
  contratos y source inventories de live ingestion

04_TSIS_webSocket_SmallCaps/src/
  implementaciones de adapters live cuando existan

E:/TSIS/
  data plane fisico para datasets y capturas declaradas
```
