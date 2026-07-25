# Source Map - Algorithmic Trading - Ernest P. Chan

Mapa inverso para saber que extraer de la fuente y donde encaja en TSIS.

## Menu

- [Ficha](#ficha)
- [Fuente por seccion](#fuente-por-seccion)
- [Mapa arquitectura TSIS](#mapa-arquitectura-tsis)
- [Preguntas que esta fuente responde](#preguntas-que-esta-fuente-responde)
- [Preguntas que no responde](#preguntas-que-no-responde)
- [Prioridad de lectura](#prioridad-de-lectura)

## Ficha

| Campo | Valor |
|---|---|
| Book ID | `algorithmic_trading_chan` |
| Titulo | `Algorithmic Trading` |
| Autor | `Ernest P. Chan` |
| Paginas extraidas | 225 |
| Tipo de fuente | Libro practico de estrategias cuantitativas y backtesting |
| Estado | Extraido e indexado |
| Uso TSIS | Estrategias, sesgos practicos, puente backtest/live, riesgo |

## Fuente por seccion

| Seccion del libro | Extraer | Encaje TSIS |
|---|---|---|
| Cap. 1 Backtesting and Automated Execution | Pitfalls, hipotesis, plataforma, conexion backtest/live | `ExperimentControl`, `BacktestEngine`, `ReplayEngine`, `RunManifest` |
| Cap. 2 Basics of Mean Reversion | Estacionariedad, ADF, Hurst, VR, half-life, cointegracion | `FeaturePipeline`, `ResearchValidation`, `StrategySpec` |
| Cap. 3 Implementing Mean Reversion | Spreads, ratios, Bollinger, scaling-in, Kalman, errores | `SignalModel`, `StateBuilder`, `DataQualityGate` |
| Cap. 4 Stocks and ETFs | Pares, ETFs, gaps, baskets, short constraints, liquidez | `SmallCapUniverse`, `ExecutionSimulator`, `BorrowModel`, `DataFoundation` |
| Cap. 5 Currencies and Futures | Denominacion, rollovers, calendar spreads, total return | `AccountingLedger`, `InstrumentContract`, `CostModel` |
| Cap. 6 Interday Momentum | Time-series/cross-sectional momentum y filtros | `StrategyLibrary`, `PortfolioConstruction`, `WalkForwardValidation` |
| Cap. 7 Intraday Momentum | Gaps, noticias, PEAD, imbalance | `EventState`, `MarketReplay`, `DecisionLedger` |
| Cap. 8 Risk Management | Kelly, CPPI, stops, risk indicators | `PreTradeRisk`, `PostTradeRisk`, `SizingModel`, `KillSwitch` |

## Mapa arquitectura TSIS

```text
Chan - Algorithmic Trading
    |
    +-- Cap. 1
    |       -> evita sesgos mecanicos
    |       -> exige backtest/live semanticamente conectados
    |       -> define requisitos de manifest y trazabilidad
    |
    +-- Cap. 2-4
    |       -> convierte mean reversion en tests y reglas
    |       -> obliga a filtros de datos y universo historico
    |       -> aporta escenarios small caps: gaps, liquidez, short constraints
    |
    +-- Cap. 6-7
    |       -> convierte momentum en horizontes, eventos y timing
    |       -> refuerza MarketStateSnapshot y EventStateSnapshot
    |
    +-- Cap. 8
            -> sizing, drawdown, stops y risk indicators
            -> separa gestion de riesgo de senal
```

## Preguntas que esta fuente responde

- Como detectar errores comunes de un backtest practico.
- Como convertir una hipotesis de mean reversion o momentum en reglas programables.
- Que tests estadisticos iniciales usar para mean reversion.
- Por que las estrategias de acciones necesitan survivorship-free data, split/dividend handling y short constraints.
- Por que la ejecucion automatizada debe estar prevista desde el diseno del backtest.
- Como pensar en sizing inicial, Kelly, CPPI, stops e indicadores de riesgo.

## Preguntas que no responde

- Como implementar un message bus profesional.
- Como disenar un OMS completo con lifecycle institucional.
- Como implementar fill models realistas para small caps con L2.
- Como disenar almacenamiento Parquet/DuckDB/Polars para TSIS.
- Como aplicar PBO/DSR formalmente a una bateria grande de estrategias.
- Como hacer brokerage adapter especifico para DAS.

## Prioridad de lectura

Para un agente que este construyendo el primer vertical slice de TSIS:

1. Leer Cap. 1 completo.
2. Leer Cap. 7 si la estrategia es intraday/event-driven.
3. Leer Cap. 4 si la estrategia usa small caps, gaps, ETFs o pares de acciones.
4. Leer Cap. 8 antes de implementar sizing o stops.
5. Leer Cap. 2-3 si se implementa mean reversion.
6. Leer Cap. 6 si se implementa momentum interday o ranking.

La fuente debe usarse como manual de criterio estrategico-practico, no como diseno definitivo del motor.
