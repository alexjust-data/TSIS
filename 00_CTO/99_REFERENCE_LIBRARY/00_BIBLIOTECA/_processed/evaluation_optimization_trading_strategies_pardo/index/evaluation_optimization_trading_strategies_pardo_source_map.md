# Source Map - Robert Pardo

**book_id:** `evaluation_optimization_trading_strategies_pardo`  
**Libro:** The Evaluation and Optimization of Trading Strategies  
**Funcion:** convertir el libro en mapa fuente -> componente TSIS.

## Menu

- [Mapa Fuente A TSIS](#mapa-fuente-a-tsis)
- [Fuente A Estudiar Por Nodo](#fuente-a-estudiar-por-nodo)
- [Como Usarlo Con Otros Libros](#como-usarlo-con-otros-libros)
- [Orden De Lectura Recomendado](#orden-de-lectura-recomendado)

## Mapa Fuente A TSIS

| Extraer de Pardo | Encaja en TSIS | Paginas PDF | Prioridad |
|---|---|---:|---|
| Proceso idea -> trading -> monitorizacion | `StrategyLifecycle`, `ResearchGovernance` | 85-100 | Critica |
| Plataforma con scripting, diagnosticos, optimizacion y WFA | `BacktestPlatform`, `ExperimentRunner` | 101-117 | Alta |
| Entrada, salida, risk management y sizing | `StrategySpec`, `RiskModel`, `SizingModel` | 118-142 | Alta |
| Reportes de simulacion historica | `TradeList`, `EquityCurve`, `IntervalPerformance` | 143-203 | Critica |
| Problemas de slippage, order fills y same-bar ambiguity | `ExecutionSimulator`, `FillModel` | 143-170 | Alta |
| Tamano de muestra, market types y degrees of freedom | `SampleSizeGate`, `RegimeCoverage`, `ComplexityBudget` | 178-203, 383-386 | Critica |
| Especificacion exacta de reglas | `StrategySpecification`, `ParameterSchema` | 204-216 | Critica |
| Test preliminar y verificacion manual | `GoldenCaseTests`, `TradeReconciliation` | 217-242 | Critica |
| Metodos de busqueda | `ParameterSearch` | 243-270 | Media |
| Objective functions robustas | `ObjectiveFunctionLibrary` | 271-281 | Alta |
| Framework de optimizacion | `OptimizationRun`, `SearchSpace` | 282-300 | Alta |
| Analisis del optimization profile | `OptimizationProfile`, `RobustnessAnalyzer` | 300-312 | Critica |
| Walk-forward analysis | `WalkForwardRunner`, `WindowPolicy` | 314-345 | Critica |
| Walk-forward efficiency | `WalkForwardEfficiencyMetric` | 316-317, 343-344 | Alta |
| Riesgo, capital y max drawdown | `RiskReport`, `CapitalModel`, `DrawdownProfiler` | 346-358 | Alta |
| Consistencia y distribucion de PnL | `StabilityReport`, `PnLDistributionReport` | 362-367 | Alta |
| Causas de sobreajuste | `OverfittingGuard` | 369-393 | Critica |
| Evaluation profile vs trade profile | `LivePerformanceMonitor`, `ShadowTradingMonitor` | 403-408 | Critica |
| Strategy stop-loss | `StrategyStopLossPolicy` | 399-403 | Alta |

## Fuente A Estudiar Por Nodo

| Nodo TSIS | Pardo aporta | Complementar con |
|---|---|---|
| `StrategyLifecycle` | fases de desarrollo y refinamiento | Lopez de Prado para research protocol moderno |
| `StrategySpecification` | necesidad de reglas exactas antes de test | QuantStart/Hilpisch para convertirlo en clases Python |
| `BacktestEngine` | criterios de simulacion correcta y reportes | QuantStart para event loop; Nautilus/LEAN para arquitectura |
| `ExecutionSimulator` | riesgos de fills historicos, limit/stops/slippage | Harris para microestructura y ordenes |
| `ExperimentRunner` | batch testing, diagnosticos, optimizacion | Hilpisch para Python/automatizacion |
| `ParameterSearch` | search space, grid/step/hill/genetic | Optuna/sklearn solo como herramientas, no como criterio cientifico |
| `ObjectiveFunction` | PROM, CECPP, thresholds, robustez | Lopez de Prado para DSR/PBO y multiple testing |
| `OptimizationProfile` | porcentaje rentable, dispersion, forma suave | tests propios de vecindad y sensibilidad |
| `WalkForwardRunner` | ventanas rolling y WFE | Lopez de Prado para purging/embargo cuando aplique |
| `EvaluationProfile` | expected behavior historico | TSIS ledgers y metrics |
| `TradeProfile` | comparacion live/shadow contra expected behavior | DAS/live logs y monitoring |
| `StrategyStopLoss` | limite de perdida de estrategia completa | Risk policy interna TSIS |

## Como Usarlo Con Otros Libros

```text
Si el problema es programar el loop:
  Successful Algorithmic Trading + Hilpisch + Nautilus/LEAN

Si el problema es decidir si una estrategia puede pasar de fase:
  Pardo

Si el problema es fills, spread, liquidez y ordenes:
  Harris

Si el problema es sobreajuste estadistico avanzado:
  Lopez de Prado + PBO + DSR

Si el problema es small caps point-in-time:
  completar con fuentes de datos, corporate actions, delistings, halts, borrow
```

Pardo debe vivir como capa de proceso encima del motor:

```text
BacktestEngine produce datos correctos
Pardo define como evaluar esos datos
Lopez de Prado endurece la inferencia estadistica
Harris endurece la plausibilidad economica de ejecucion
```

## Orden De Lectura Recomendado

Para un agente nuevo trabajando en `TSIS_BACKTEST_ENGINE`:

```text
1. Leer paginas 85-100 para entender lifecycle.
2. Leer paginas 204-242 antes de tocar una estrategia concreta.
3. Leer paginas 143-203 antes de validar outputs de backtest.
4. Leer paginas 282-313 si va a optimizar parametros.
5. Leer paginas 314-345 si va a implementar WFA.
6. Leer paginas 369-393 si va a revisar overfitting.
7. Leer paginas 394-413 si va a trabajar en shadow/live monitoring.
```

Para el primer vertical slice TSIS, no intentar implementar todo Pardo. Implementar primero:

```text
StrategySpec
PreliminaryTestReport
OptimizationRun manifest
simple OptimizationProfile
basic WalkForwardRunner
EvaluationProfile
```

