# Execution Tests

Este directorio valida realismo de ejecucion.

## Ambito

Aqui deben vivir tests sobre:

- fills;
- slippage;
- fees;
- liquidity constraints;
- halts;
- spreads;
- partial fills;
- order types;
- limites de volumen;
- compatibilidad con live trading.

## Reglas

Execution no debe contaminar features ni eventos. Su responsabilidad es modelar
si una orden podia ejecutarse, a que precio probable, con que coste y bajo que
restricciones.

## Pruebas esperadas

Pruebas candidatas:

- `test_no_fill_during_halt.py`
- `test_fill_respects_market_calendar.py`
- `test_fill_respects_intraday_liquidity.py`
- `test_cost_model_manifest.py`
- `test_spread_and_slippage_bounds.py`

## Criterio institucional

Una simulacion de ejecucion debe ser reconstruible:

- tabla intradia usada;
- halts usados;
- calendario usado;
- parametros de coste;
- version del simulador;
- run id y manifest.

