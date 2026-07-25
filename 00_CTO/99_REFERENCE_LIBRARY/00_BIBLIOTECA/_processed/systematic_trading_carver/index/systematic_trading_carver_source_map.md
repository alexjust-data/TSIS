# Source Map - Systematic Trading - Robert Carver

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `systematic_trading_carver` |
| Tipo | libro practico de diseno sistematico y portfolio/risk |
| Estado | extraido e indexado |
| Uso principal | forecasts, sizing, volatility target, portfolio construction |

## Fuente por bloque

| Bloque | Extraer | Encaje TSIS |
|---|---|---|
| Theory | reglas simples, sesgos, estilos | `StrategyGovernance` |
| Toolbox | fitting y portfolio allocation | `OverfitGuard`, `WeightPolicy` |
| Framework | forecasts, vol target, sizing, costs | `PortfolioConstructionEngine` |
| Practice | operadores y rutinas | `OperationalRunbook` |
| Appendices | EWMAC, carry, forecast rescaling | `StrategyTemplateLibrary` |

## Preguntas que responde

- Como convertir una senal en posicion dimensionada por riesgo.
- Como combinar forecasts.
- Como evitar que el sizing dependa de intuicion.
- Como ajustar velocidad de trading a costes.
- Como crear un framework modular para distintos estilos.

## Preguntas que no responde

- Como implementar event loop.
- Como simular limit order book.
- Como hacer TCA institucional detallado.
- Como validar PBO/DSR.

## Prioridad de lectura

1. Ch. 5-12 para arquitectura de forecast/risk/portfolio.
2. Ch. 3-4 para fitting y weights.
3. Appendices B-D para reglas y formulas.

