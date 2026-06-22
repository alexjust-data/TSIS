# CTO Architecture Contract Tests

Este directorio valida la coherencia de la arquitectura TSIS.

## Proposito

Los tests aqui deben proteger que los documentos CTO no describan una realidad
distinta de la implementada en los modulos.

## Pruebas esperadas

Pruebas candidatas:

- `test_layer_references.py`: cada capa declarada en la arquitectura tiene una
  ruta operativa o contrato aguas abajo.
- `test_data_foundation_outputs_reference.py`: `TSIS_LAB_ARCHITECTURE.md`
  referencia el contrato de outputs de Data Foundation.
- `test_pipeline_stage_map.py`: las etapas de data, research, eventos,
  estrategia, ejecucion y RL conservan fronteras explicitas.
- `test_no_architecture_orphans.py`: no hay contratos operativos importantes sin
  referencia desde el mapa CTO cuando ya son institucionales.

## Criterio de calidad

Estos tests no deben aceptar nombres parecidos como equivalentes. Deben validar
rutas canonicas exactas o aliases documentados.

Cuando un documento CTO declara una tabla o salida objetivo, el test debe exigir
que exista:

- contrato de salida;
- propietario;
- nivel de promocion;
- ruta de materializacion o razon explicita para no existir todavia;
- politica de validacion.

