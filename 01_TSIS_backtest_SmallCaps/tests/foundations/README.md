# Foundations Tests

Este directorio valida la coherencia interna de `01_foundations`.

## Ambito

Aqui deben vivir tests sobre:

- `canonical_schemas/`
- `contract_registry/`
- `data_consumption_policies/`
- `dataset_registry/`
- `validators/`
- `inspection_dossiers/`
- `data_quality_report/`
- `module_contracts/`
- colas y salidas Graphify de la capa foundations.

## Pruebas esperadas

Pruebas candidatas:

- `test_schema_registry_consistency.py`: cada schema canonico tiene entrada en
  registry cuando aplica.
- `test_dataset_registry_consistency.py`: cada dataset institucional tiene
  owner, source, version, ruta y estado.
- `test_consumption_policy_coverage.py`: cada dataset consumible tiene politica
  de consumo.
- `test_validator_coverage.py`: cada contrato critico tiene validador descrito o
  test ejecutable asociado.
- `test_inspection_dossier_completeness.py`: cada familia auditada tiene readout,
  good cases, review cases, bad cases y evidencia visual cuando el estandar lo
  exige.
- `test_data_quality_report_index.py`: el indice de calidad enlaza las familias,
  tablas y evidencias correctas.

## Separacion de responsabilidades

`01_foundations` define contratos y evidencia. Los tests ejecutables viven aqui
solo cuando validan coherencia de esa capa. Las pruebas fila por fila de tablas
materializadas van en `data_foundation_outputs/`.

