# SmallCaps Lab Bridge

Fecha: 2026-07-05
Estado: bridge_placeholder

## Rol

Este bridge conecta experimentos transversales de `00_TSIS_Lab` con el modulo operativo SmallCaps:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps
```

SmallCaps no queda reducido a proveedor ni a adapter. SmallCaps es el modulo operativo donde viven foundations, investigacion, builders, event discovery, feature engine, backtests clasicos y strategy research. Este bridge solo documenta como un experimento transversal de TSIS Lab puede consumir o invocar piezas SmallCaps sin duplicarlas.

## Regla

`00_TSIS_Lab` no debe duplicar la logica de foundations. Debe llamar o referenciar builders y contratos existentes.




