# Source Map - Trading Systems, 2nd Edition - Jaekle/Tomasini

Mapa inverso para agentes: que extraer de este libro y donde encaja en TSIS.

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `trading_systems_urban_jaekle` |
| Titulo | `Trading Systems: A New Approach to System Development and Portfolio Optimisation` |
| Autores | Urban Jaekle, Emilio Tomasini |
| Edicion | Second Edition |
| Paginas PDF | 363 |
| Palabras extraidas aprox. | 81622 |
| Tipo de fuente | Manual practico de desarrollo, robustez, sizing y portfolio |
| Estado | Extraido e indexado |

## Fuente por bloque

| Bloque | Extraer | Encaje TSIS |
|---|---|---|
| Caps. 1-2 | Definicion de sistema, datos, timeframe, complejidad, metricas | `StrategySpec`, `DataQualityGate`, `MetricsEngine` |
| Cap. 3 | Caso LUXOR, costes, estabilidad, exits, MAE/MFE | `StrategyDevelopmentWorkflow`, `ExitDiagnostics` |
| Cap. 4 | Timescale analysis y Monte Carlo | `TimeframeStressTest`, `MonteCarloEngine` |
| Cap. 5 | Biases, OOS deterioration, overfitting, robust system | `OverfittingGuard`, `OOSDecayReport` |
| Cap. 6 | Anchored/rolling WFA | `WalkForwardRunner`, `WindowPolicy` |
| Cap. 7 | Position sizing | `SizingModel`, `CapitalModel` |
| Cap. 8 | Dynamic portfolio construction | `PortfolioConstruction`, `StrategyActivationPolicy` |
| Cap. 9 | Stock portfolio, survivorship, ranking, daily execution | `PointInTimeUniverse`, `SignalRankingPolicy`, `ExecutionRunbook` |

## Mapa arquitectura TSIS

```text
Jaekle/Tomasini
    |
    +-- Development process
    |       -> IdeaSpec
    |       -> StrategyRules
    |       -> CostedBacktest
    |
    +-- Diagnostics
    |       -> ParameterStabilityMap
    |       -> MAE_MFE_Report
    |       -> TradeDistributionReport
    |
    +-- Validation
    |       -> TimescaleStressTest
    |       -> MonteCarloTradeSequence
    |       -> WalkForwardRunner
    |
    +-- Portfolio
    |       -> EquityCorrelationAnalyzer
    |       -> DynamicPortfolioComposition
    |       -> SignalRankingPolicy
    |
    +-- Data realism
            -> ContinuousContractPolicy
            -> SurvivorshipBiasGuard
            -> DataVendorAudit
```

## Preguntas que esta fuente responde

- Como convertir una idea en un sistema completo paso a paso.
- Como ver el efecto de costes sobre la viabilidad inicial.
- Como usar MAE/MFE para elegir stops, trailing y profit targets.
- Como distinguir picos de optimizacion de zonas estables.
- Como aplicar WFA anchored y rolling.
- Como usar Monte Carlo para estimar drawdown probable.
- Como pensar en universe, ranking y survivorship en portfolios de acciones.
- Como separar backtesting profesional de ejecucion diaria.

## Preguntas que no responde

- Como implementar un motor event-driven profesional en Python.
- Como modelar partial fills, broker callbacks, order state machine o DAS.
- Como persistir snapshots TSIS.
- Como implementar controles PBO/DSR formalmente.
- Como simular microestructura small caps con quotes/trades L2.

## Prioridad de lectura TSIS

1. Cap. 3 completo: vertical slice de desarrollo de sistema.
2. Cap. 6: WFA anchored/rolling.
3. Cap. 9: acciones, survivorship, ranking y daily execution.
4. Cap. 4: timescale y Monte Carlo.
5. Cap. 7-8: sizing y portfolio.
6. Cap. 2: datos, complejidad y metricas.
