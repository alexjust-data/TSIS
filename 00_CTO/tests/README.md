# 00_CTO Tests

Este directorio contiene los tests propios del area CTO.

`00_CTO` gobierna arquitectura, criterios institucionales, mapas de capas y
decisiones transversales. Sus tests no deben validar datasets concretos fila por
fila. Deben comprobar que la arquitectura declarada, las decisiones privadas y
los contratos publicos del sistema siguen siendo coherentes.

## Subdirectorios

- `architecture_contracts/`: coherencia de documentos de arquitectura y salidas
  objetivo.
- `governance_contracts/`: changelog, versionado, Graphify y reglas de gobierno.
- `private_consistency/`: consistencia entre documentacion privada y contratos
  publicos sin filtrar contenido sensible.

## Relacion con SmallCaps

Cuando `00_CTO` declara una capa, por ejemplo `CAPA 1 - DATA FOUNDATION`, los
tests de CTO deben comprobar que existe una referencia institucional al contrato
operativo correspondiente.

Ejemplo:

- documento de arquitectura: `00_CTO/TSIS_LAB_ARCHITECTURE_v3.md`
- contrato operativo de salida: `01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- tests ejecutables de tablas: `01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/`

La regla es: CTO define el mapa; el modulo implementa y valida.

## Criterio de exito

Una prueba CTO debe responder:

- que capa del sistema protege;
- que documento de arquitectura es fuente de verdad;
- que contrato operativo debe existir aguas abajo;
- que actualizacion de changelog o Graphify se espera;
- que riesgo de desalineacion detecta.


