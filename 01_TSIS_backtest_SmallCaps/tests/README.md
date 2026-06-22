# SmallCaps Module Tests

Este directorio contiene los tests ejecutables del modulo
`01_TSIS_backtest_SmallCaps`.

El modulo SmallCaps es propietario de la capa `CAPA 1 - DATA FOUNDATION` para
este flujo de backtesting, investigacion de smallcaps, microestructura, eventos,
estrategias y preparacion offline RL.

## Principio de organizacion

Los tests se organizan por responsabilidad, no por capricho de carpeta. Cada
subdirectorio debe proteger una familia de contratos o una capa funcional.

Subdirectorios:

- `data_foundation_outputs/`: tablas institucionales materializadas en
  `E:/TSIS/data/data_foundation_outputs/`.
- `foundations/`: consistencia de schemas, registries, policies, validators,
  inspection dossiers y data quality reports.
- `pipelines/`: materializacion reproducible, idempotencia, manifests y rutas
  de outputs.
- `research/`: promocion segura desde notebooks o exploracion a contratos.
- `event_engine/`: semantica causal, eventos, offerings, halts y alertas.
- `strategy_engine/`: senales, uso correcto de datos y ausencia de lookahead.
- `execution/`: realismo de ejecucion, fills, liquidez, fees, slippage y halts.
- `rl_preparation/`: datasets offline RL, estados, acciones, rewards y splits.

## Regla obligatoria para cada test

Cada test debe declarar o dejar claro:

- contrato que protege;
- dataset o output si aplica;
- fuente de verdad;
- manifest esperado;
- modo offline o third-party;
- riesgo institucional que detecta.

## Tests existentes

El archivo `test_price_views.py` existia antes de esta estructura. Debe
mantenerse hasta que se decida si pertenece a una subcarpeta especifica. No debe
moverse sin revisar imports, CI y referencias.

