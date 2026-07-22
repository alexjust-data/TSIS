# Strategy Engine Tests

Este directorio valida estrategias y logica de senal del modulo SmallCaps.

## Ambito

Aqui deben vivir tests sobre:

- uso correcto de tablas Data Foundation;
- ausencia de lookahead;
- separacion entre features y senales;
- reproducibilidad de backtests;
- reglas de inclusion/exclusion de universo;
- consistencia de parametros;
- interpretacion de eventos.

## Reglas

El strategy engine no debe redefinir silenciosamente:

- calendario de mercado;
- universo smallcap;
- corporate actions;
- precio ajustado o no ajustado;
- halts;
- liquidez;
- disponibilidad temporal de datos.

Debe consumir contratos upstream, no inventarlos.

## Pruebas esperadas

Pruebas candidatas:

- `test_strategy_uses_governed_universe.py`
- `test_strategy_uses_market_calendar.py`
- `test_no_future_bars_in_signal.py`
- `test_signal_feature_boundary.py`
- `test_backtest_reproducibility_manifest.py`

## Criterio de calidad

Un backtest no debe aprobar si no puede explicar:

- que version de tablas uso;
- que calendario uso;
- que universo uso;
- que costos y ejecucion asumio;
- que periodo cubrio;
- que run id produjo.

