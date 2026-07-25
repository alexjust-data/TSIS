# Concept Index - Systematic Trading - Robert Carver

## Menu

- [Framework](#framework)
- [Forecasts y reglas](#forecasts-y-reglas)
- [Riesgo y portfolio](#riesgo-y-portfolio)
- [Costes](#costes)
- [Uso TSIS](#uso-tsis)

## Framework

| Concepto | Seccion | Uso TSIS |
|---|---|---|
| Flawed human brain | Ch. 1 | `DecisionGovernance` |
| Systematic trading rules | Ch. 2 | `StrategyRuleSpec` |
| Fitting / overfitting | Ch. 3 | `OverfitGuard` |
| Portfolio allocation | Ch. 4 | `PortfolioWeightPolicy` |
| Modular framework | Ch. 5 | `StrategyFramework` |
| Instruments | Ch. 6 | `InstrumentSelectionPolicy` |

## Forecasts y reglas

| Concepto | Seccion | Uso TSIS |
|---|---|---|
| Forecast | Ch. 7 | `RawForecast` |
| EWMAC | Appendix B | `TrendForecastTemplate` |
| Carry rule | Appendix B | `CarryForecastTemplate` |
| Forecast weights | Ch. 8 | `ForecastCombiner` |
| Forecast scaling | Ch. 8, Appendix D | `ForecastScaler` |
| Forecast cap | Ch. 8 | `ForecastCap` |

## Riesgo y portfolio

| Concepto | Seccion | Uso TSIS |
|---|---|---|
| Volatility targeting | Ch. 9 | `VolatilityTargetPolicy` |
| Position sizing | Ch. 10 | `PositionSizer` |
| From forecast to position | Ch. 10 | `ForecastToTargetPosition` |
| Instrument weights | Ch. 11 | `InstrumentWeightPolicy` |
| Diversification multiplier | Ch. 11, Appendix D | `DiversificationMultiplier` |
| Portfolio of subsystems | Ch. 11 | `PortfolioConstruction` |

## Costes

| Concepto | Seccion | Uso TSIS |
|---|---|---|
| Speed of trading | Ch. 12 | `TradeSpeedPolicy` |
| Cost of trading | Ch. 12 | `ExpectedCostModel` |
| Costs and capital | Ch. 12 | `CapacityAndCostGate` |

## Uso TSIS

| Tarea | Consultar |
|---|---|
| Crear framework comun de sizing | Ch. 8-11 |
| Normalizar senales de distintas estrategias | Ch. 7-8 |
| Disenar risk targeting | Ch. 9-10 |
| Decidir velocidad por costes | Ch. 12 |
| Soportar modo semi-automatico | Ch. 13 |

