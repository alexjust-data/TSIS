# Concept Index - The Evaluation and Optimization of Trading Strategies

**book_id:** `evaluation_optimization_trading_strategies_pardo`  
**Uso:** indice concepto -> paginas -> aplicacion TSIS.  
**Regla:** abrir primero este indice, despues el resumen, y solo despues el PDF original por pagina.

## Menu

- [Indice Conceptual](#indice-conceptual)
- [Conceptos Mas Importantes Para TSIS](#conceptos-mas-importantes-para-tsis)
- [Preguntas Rapidas Para Agentes](#preguntas-rapidas-para-agentes)

## Indice Conceptual

| Concepto | Paginas PDF | Que aporta | Encaje TSIS |
|---|---:|---|---|
| Abuse of hindsight | 372-375 | Riesgo de disenar reglas mirando eventos pasados concretos | `ResearchGovernance`, `HypothesisLog` |
| Annualized risk-adjusted return | 357-358 | Evalua retorno contra capital/riesgo asumido | `Metrics`, `RiskReport` |
| Backtest diagnostics | 101-117, 143-203 | Trade list, equity curve, interval performance, debugging | `DiagnosticsReport`, `Ledger` |
| Big fish in small pond | 391 | Beneficio concentrado en pocas operaciones dentro de muestra pequena | `OverfittingGuard`, `TradeContributionAnalysis` |
| CECPP | 274-276 | Relaciona equity curve con oportunidad teorica del mercado | future `OpportunityCaptureMetric` |
| Consistency | 362-367 | Distribucion estable de PnL, trades, runs y drawdowns | `StabilityReport` |
| Degree of freedom | 383-386 | Control de complejidad frente a tamano de muestra | `ModelComplexityBudget` |
| Evaluation profile | 403-408 | Perfil esperado de performance historica/WFA | `EvaluationProfile` |
| Fill realism | 143-170 | Ambiguedades de simulacion, limit orders, stops, slippage | `ExecutionSimulator`, `FillModel` |
| Formulation | 85-100, 204-216 | Pasar idea a reglas precisas | `StrategySpecification` |
| Grid search | 246-250 | Busqueda exhaustiva de combinaciones | `ParameterGrid` |
| Historical simulation | 143-203 | Simular reglas en datos historicos con costes y restricciones | `BacktestEngine` |
| Market types | 194-199, 319-324 | Bull, bear, congestion, volatilidad, liquidez | `RegimeLabel`, `MarketState` |
| Maximum drawdown | 348-353 | Riesgo principal para capitalizacion y stop de estrategia | `DrawdownProfiler`, `Risk` |
| Maximum run-up | 353-354 | Periodos optimos y riesgo psicologico de windfall | `RunupProfiler` |
| Model efficiency | 359-360 | Porcentaje de oportunidad de mercado capturado | future `OpportunityCaptureMetric` |
| Multimarket/multiperiod test | 217-242, 312-313 | Robustez preliminar en mercados y periodos diversos | `PreliminaryTestReport` |
| Objective function | 243-281 | Criterio de seleccion de parametros | `ObjectiveFunction` |
| Optimization | 282-313 | Seleccion de parametros robustos | `OptimizationRun` |
| Optimization profile | 301-312 | Distribucion completa de candidatos y forma de superficie | `OptimizationProfile` |
| Overfitting | 369-393 | Parametros buenos in-sample y malos OOS/live | `OverfittingGuard` |
| Overparameterization | 388-389 | Demasiados parametros optimizables | `ParameterBudget` |
| Overscanning | 389-391 | Rangos/pasos demasiado finos o amplios | `SearchSpaceReview` |
| Pessimistic return on margin | 276-280 | Objective function conservadora que penaliza muestras pequenas | `ObjectiveFunctionLibrary` |
| Preliminary testing | 217-242 | Verificar reglas, calculos, trades y plausibilidad antes de optimizar | `GoldenCaseTests` |
| Profit distribution | 362-367 | Detecta beneficios concentrados o deterioro reciente | `PnLDistributionReport` |
| Required capital | 354-357 | Capital necesario para margen y drawdown con margen de seguridad | `CapitalModel` |
| Risk stop | 130-136, 399-403 | Stop de trade y stop de estrategia | `RiskPolicy`, `StrategyStopLoss` |
| Robust optimization | 300-312 | Parametros con vecinos rentables y superficie suave | `RobustnessAnalyzer` |
| Search method | 243-270 | Grid, step, hill climbing, genetic search | `ParameterSearch` |
| Strategy development process | 85-100 | Flujo idea -> trading -> monitorizacion | `StrategyLifecycle` |
| Strategy stop-loss | 399-403 | Limite para suspender trading de una estrategia completa | `StrategyStopLossPolicy` |
| Trade profile | 403-408 | Perfil real-time comparable con evaluation profile | `LivePerformanceProfile` |
| Trade sample size | 386-388 | Tamano minimo de muestra y error estadistico | `SampleSizeGate` |
| Walk-forward analysis | 314-345 | Validacion rolling out-of-sample | `WalkForwardRunner` |
| Walk-forward efficiency | 316-317, 343-344 | Ratio entre performance OOS e in-sample | `WalkForwardEfficiencyMetric` |

## Conceptos Mas Importantes Para TSIS

1. `StrategySpecification`: ninguna estrategia pasa a codigo sin reglas exactas.
2. `PreliminaryTestReport`: antes de optimizar hay que demostrar que el codigo opera segun diseno.
3. `OptimizationProfile`: no seleccionar el maximo aislado; analizar vecindad, porcentaje rentable y dispersion.
4. `WalkForwardAnalysis`: validar sobre datos fuera de muestra concatenados, no sobre el mismo tramo usado para elegir parametros.
5. `EvaluationProfile`: convertir el backtest/WFA en expectativa medible.
6. `TradeProfile`: comparar shadow/live contra la expectativa historica.
7. `StrategyStopLoss`: definir de antemano cuando pausar o retirar una estrategia.

## Preguntas Rapidas Para Agentes

| Pregunta | Buscar |
|---|---|
| Como organizo el proceso completo de research? | paginas 85-100 |
| Que reportes minimos debe producir el backtester? | paginas 101-117 y 143-203 |
| Como convierto una idea en reglas testeables? | paginas 204-216 |
| Como verifico que el codigo no esta mal antes de optimizar? | paginas 217-242 |
| Como selecciono parametros sin perseguir max net profit? | paginas 243-313 |
| Como implemento walk-forward? | paginas 314-345 |
| Como decido si la performance justifica trading? | paginas 346-368 |
| Como detecto sobreajuste operativo? | paginas 369-393 |
| Como comparo live contra backtest? | paginas 394-413 |

