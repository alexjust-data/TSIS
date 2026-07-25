# Source Map - Ernest P. Chan

**book_id:** `quantitative_trading_chan`  
**Libro:** Quantitative Trading, 2nd Edition  
**Funcion:** convertir el libro en mapa fuente -> componente TSIS.

## Menu

- [Mapa Fuente A TSIS](#mapa-fuente-a-tsis)
- [Fuente A Estudiar Por Nodo](#fuente-a-estudiar-por-nodo)
- [Como Usarlo Con Otros Libros](#como-usarlo-con-otros-libros)
- [Orden De Lectura Recomendado](#orden-de-lectura-recomendado)

## Mapa Fuente A TSIS

| Extraer de Chan | Encaja en TSIS | Paginas PDF | Prioridad |
|---|---|---:|---|
| Filtro inicial de ideas por tiempo, capital, datos y capacidad | `StrategyIntakeChecklist` | 28-50 | Alta |
| Advertencia small caps: iliquidez y academic backtests | `SmallCapLiquidityGate`, `CapacityModel` | 28, 34-36, 48-49 | Critica |
| Backtest como replicacion propia | `ReproducibilityGate` | 51-52 | Alta |
| Plataformas y transicion backtest/live | `ReferencePlatforms`, `BacktestLiveEquivalence` | 51-59 | Media |
| Datos ajustados y survivorship-free | `DataQualityGate`, `CorporateActions`, `PointInTimeUniverse` | 59-68 | Critica |
| Sharpe, MDD, MDD duration, MAR | `MetricsEngine`, `DrawdownProfiler` | 68-82 | Alta |
| Look-ahead bias | `TemporalIntegrityGate` | 82-83 | Critica |
| Truncated data position check | `TruncatedDataInvarianceTest` | 83, 93-94 | Critica |
| Data-snooping bias y DSR | `OverfittingGuard`, `ExperimentRegistry` | 83-88 | Critica |
| Sensitivity analysis y simplificacion | `SensitivityAnalysis`, `RefinementGovernance` | 97-98, 103-107 | Alta |
| Transaction costs | `TransactionCostModel`, `CostAccounting` | 43-44, 98-103 | Critica |
| Broker/API/paper account/simulator | `BrokerCapabilityMatrix`, `PaperTradingEnvironment` | 113-115 | Alta |
| Infraestructura fisica/VPS/UPS | `OperationalRunbook` | 116-118 | Media |
| ATS semi/full automated | `AutomatedTradingSystem`, `DASBrokerAdapter` | 120-128 | Alta |
| Order file/order submission workflow | `OrderSubmissionLedger` | 121-126 | Media |
| Minimizacion de costes por order size/ADV | `ParticipationCap`, `AverageVolumeGate` | 130-132 | Critica |
| Paper trading | `ShadowTradingHarness`, `BacktestVsPaperReconciler` | 132-133 | Critica |
| Divergencia backtest/live | `LiveDivergenceMonitor` | 133-137 | Critica |
| Hard-to-borrow y short rules | `ShortAvailabilityModel`, `ShortSaleConstraintModel` | 135 | Critica para shorts |
| Kelly/half-Kelly/leverage | `RiskSizingModel`, `CapitalAllocator` | 138-154 | Alta |
| Model risk/software risk/operational risk | `RiskRegister`, `ModelRiskMonitor` | 156-157 | Alta |
| Mean reversion vs momentum | `StrategyType`, `RegimeMonitor` | 166-170 | Alta |
| Regime change y CPO | `RegimeConditionalParameterPolicy` | 170-181 | Media/Futura |
| Stationarity/cointegration | `PairResearch`, `CointegrationTest` | 182-200 | Media/Futura |
| Factor models/PCA | `FactorExposureModel` | 200-210 | Media/Futura |
| Exit logic por tipo de estrategia | `ExitPolicy` | 210-215 | Alta |
| Seasonal strategies | `SeasonalityResearch` | 215-230 | Baja/Futura |
| HFT requirements | `QuoteEvent`, `SpreadModel`, `LatencyModel`, `HFTReadinessGate` | 230-235 | Alta para intraday avanzado |
| Capacity edge del independiente | `CapacityModel`, `AlphaDecayMonitor` | 238-243 | Critica |

## Fuente A Estudiar Por Nodo

| Nodo TSIS | Chan aporta | Complementar con |
|---|---|---|
| `StrategyIntakeChecklist` | como filtrar ideas por persona, capital, datos, Sharpe, drawdown y capacidad | Pardo para lifecycle formal |
| `DataQualityGate` | split/dividend adjustment, survivorship, point-in-time | TSIS data foundation, CRSP/Polygon docs |
| `TemporalIntegrityGate` | look-ahead y test de truncamiento | Lopez de Prado para leakage avanzado |
| `ExperimentRegistry` | decisiones cualitativas tambien cuentan como tweaks | Pardo y DSR/PBO |
| `TransactionCostModel` | comisiones, spread, market impact, slippage | Harris para microestructura |
| `ExecutionReadiness` | ATS, broker API, semi/full automation | LEAN/Nautilus para arquitectura; DAS docs para implementacion |
| `PaperTradingHarness` | paper como detector de bugs/leakage/operativa | Pardo Ch. 14 para profile comparison |
| `BacktestVsPaperReconciler` | comparar trades teoricos contra ATS/paper | TSIS ledgers |
| `CapacityModel` | baja capacidad como nicho del independiente | Harris, small-cap liquidity stats |
| `RiskSizingModel` | Kelly, half-Kelly, leverage caps por worst loss | Pardo required capital; internal risk policy |
| `RegimeMonitor` | regime shifts por estructura, regulacion, volatilidad | MarketState/EventState TSIS |
| `ExitPolicy` | exits distintos para momentum y mean reversion | Strategy-specific tests |
| `PairResearch` | cointegration y half-life | statsmodels/R/robust tests |
| `FactorExposureModel` | APT, Fama-French, PCA | Grinold/Kahn, data vendors |

## Como Usarlo Con Otros Libros

```text
Si el problema es programar el event loop:
  Successful Algorithmic Trading + Hilpisch

Si el problema es decidir que estrategia merece investigarse:
  Chan Ch. 2 + Pardo Ch. 3

Si el problema es auditar sesgos basicos de backtest:
  Chan Ch. 3 + Pardo Ch. 13 + Lopez de Prado

Si el problema es coste/ejecucion:
  Chan Ch. 3/5 + Harris + broker/DAS docs

Si el problema es pasar de backtest a paper/live:
  Chan Ch. 5 + Pardo Ch. 14 + Hilpisch Ch. 10

Si el problema es sizing/risk:
  Chan Ch. 6 + Pardo Ch. 12

Si el problema es stat arb/pairs/factors:
  Chan Ch. 7 + fuentes estadisticas especificas
```

Chan rellena una capa que faltaba:

```text
motor event-driven correcto
        +
disciplina de evaluacion
        +
operativa real de trader cuantitativo
```

## Orden De Lectura Recomendado

Para un agente nuevo trabajando en `TSIS_BACKTEST_ENGINE`:

```text
1. Leer paginas 28-50 para entender seleccion de ideas y capacidad.
2. Leer paginas 51-107 antes de aceptar cualquier backtest.
3. Leer paginas 120-137 si toca ATS, DAS, paper trading o live.
4. Leer paginas 138-157 si toca sizing, risk o leverage.
5. Leer paginas 166-181 si toca regimenes o MarketState.
6. Leer paginas 210-215 si toca exit logic.
7. Leer paginas 230-235 si toca intraday de alta frecuencia o quotes.
8. Leer paginas 238-243 para entender capacidad y alpha decay.
```

Para el primer vertical slice TSIS, implementar solo lo necesario:

```text
StrategyIntakeChecklist
DataQualityGate
TemporalIntegrityGate
TransactionCostModel basic
MetricsEngine basic
PaperTradingHarness skeleton
BacktestVsPaperReconciler skeleton
CapacityModel v0
```

